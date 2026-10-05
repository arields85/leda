"""La lista cerrada de jugadas y sus fichas (E2-3).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Jugadas"); ADR 0018, decisiones 1, 4 y 9.

Cada jugada se declara con una ficha: qué datos necesita, qué comprueba el código, qué efecto
hace y qué pasa después. La comprobación común (los datos que faltan, la tarea por su alias y
los estados en que la jugada vale) la hace `_correr` igual para todas; el manejador de cada
ficha hace sólo lo suyo. Ninguna jugada confirma (9a): el efecto va directo, con
`herramientas.ejecutar(..., ya_confirmada=True)`, que verifica la autoridad igual.

El resultado de una jugada son hechos (un dict), nunca un texto: la IA redacta desde ellos. Una
jugada que existe pero no se puede hacer ahora devuelve por qué (`no_se_puede`), sin aviso al
administrador (decisión 1). Las tareas viajan por su alias; un id de la base nunca llega a la
IA. Cada jugada corre en su propio punto de guardado: si falla, lo suyo se deshace.

Las jugadas de las situaciones generales (`elegir`, `corregir`, `cancelar`,
`dejar_para_despues`) son de la E2-4.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import date, datetime, time
from functools import cached_property
from types import MappingProxyType
from typing import Any

import psycopg

from leda.autoridad import Denegado, Solicitante
from leda.calendario import Calendario
from leda.herramientas import ejecutar

from .ia import Jugada


@dataclass(frozen=True)
class Contexto:
    """Lo que un manejador de jugada necesita: la transacción del espacio, quién escribió,
    el momento del motor y lo leído al empezar el turno. `avisos_guardados` junta los
    avisos que guardan las jugadas del turno, para atarlos al turno al registrarlo."""

    cur: psycopg.Cursor
    quien: Solicitante
    entrante_id: str
    chat_id: int
    texto: str
    ahora: datetime
    estado: dict[str, Any] | None
    tareas: tuple[dict[str, Any], ...]
    ultimos_turnos: tuple[dict[str, Any], ...]
    avisos_guardados: list[str] = field(default_factory=list)

    def tarea(self, alias: str) -> dict[str, Any] | None:
        return next((t for t in self.tareas if t["alias"] == alias), None)

    @cached_property
    def calendario(self) -> Calendario:
        return Calendario.desde_base(self.cur, self.quien.workspace_id)


Manejador = Callable[[Contexto, Jugada], dict[str, Any]]


@dataclass(frozen=True)
class Ficha:
    """Una jugada de la lista cerrada (ADR 0018, decisión 4)."""

    nombre: str
    para_que: str                   # qué hace, para decirle a la persona qué puede pedir
    necesita: tuple[str, ...]       # datos sin los que no se hace
    opcional: tuple[str, ...]
    comprueba: str
    hace: str
    despues: str
    manejar: Callable[[Contexto, dict[str, Any], dict[str, Any] | None], dict[str, Any]]
    del_responsable: bool = False   # la tarea tiene que ser de quien escribe
    estados: frozenset[str] | None = None   # en qué estados de la tarea vale; None: abierta
    se_ofrece: bool = True          # False: se reconoce, pero no se hace por chat (9g)


# Lo que Leda propone cuando la persona no puede destrabar sola (9c, paso 3): que alguien la
# ayude, o más tiempo, que es la jugada de la nueva previsión.
SALIDAS_DE_UN_BLOQUEO = ("que_alguien_ayude", "anotar_prevision")


# --- Comprobación común --------------------------------------------------------------------

def _correr(ficha: Ficha, ctx: Contexto, jugada: Jugada) -> dict[str, Any]:
    datos = dict(jugada.datos or {})
    faltan = [k for k in ficha.necesita if _vacio(datos.get(k))]
    if faltan:
        return _hecho(ficha, "falta_dato", falta=faltan)
    tarea = None
    if not _vacio(datos.get("tarea")) and "tarea" in ficha.necesita + ficha.opcional:
        tarea = ctx.tarea(str(datos["tarea"]))
        if tarea is None:
            return _hecho(ficha, "no_se_puede", motivo="tarea_desconocida")
    try:
        with ctx.cur.connection.transaction():
            if tarea is not None and ficha.del_responsable:
                # Leída de nuevo, bajo la RLS del espacio: el estado vigente, no el del
                # principio del turno (otra jugada del mismo mensaje pudo cambiarlo).
                fila = _exigir_responsable(ctx.cur, ctx.quien, tarea["id"])
                tarea = {**tarea, "estado": str(fila["estado"])}
                if ficha.estados is not None and tarea["estado"] not in ficha.estados:
                    return _hecho(ficha, "no_se_puede", motivo="estado",
                                  tarea=_tarea(tarea), estado=tarea["estado"])
            return {"jugada": ficha.nombre, **ficha.manejar(ctx, datos, tarea)}
    except Denegado:
        return _hecho(ficha, "no_se_puede", motivo="no_autorizado",
                      tarea=_tarea(tarea) if tarea else None)


def _vacio(valor: Any) -> bool:
    return valor is None or (isinstance(valor, str) and not valor.strip())


def _hecho(ficha: Ficha, resultado: str, **mas: Any) -> dict[str, Any]:
    return {"jugada": ficha.nombre, "resultado": resultado,
            **{k: v for k, v in mas.items() if v is not None}}


def _tarea(tarea: dict[str, Any]) -> dict[str, str]:
    return {"alias": tarea["alias"], "titulo": tarea["titulo"]}


# --- Lo que comparten las fichas -----------------------------------------------------------

def _cerrar_esperas(ctx: Contexto, task_id: str) -> None:
    """Un hecho informado sobre una tarea contesta la espera de esa tarea (9b)."""
    ctx.cur.execute(
        """update pending_reply set satisfecho_en = %s
            where membership_id = %s and task_id = %s and satisfecho_en is null""",
        (ctx.ahora, ctx.quien.membership_id, task_id))


def _abrir_pregunta(ctx: Contexto, tipo: str, task_id: str, *, se_puede_dejar: bool,
                    jugada: dict[str, Any]) -> None:
    """Una pregunta de Leda. Si ya hay una abierta, la nueva queda para después: nunca dos
    preguntas juntas, en el orden en que salieron (9d). Cómo se retoma, la E2-4."""
    cur = ctx.cur
    cur.execute("""select q.id from conversation_state s
                     join conversation_question q on q.id = s.pregunta_abierta_id
                    where s.membership_id = %s and q.cerrada_en is null""",
                (ctx.quien.membership_id,))
    hay_otra = cur.fetchone() is not None
    cur.execute(
        """insert into conversation_question (workspace_id, membership_id, tipo, task_id,
                                              jugada, se_puede_dejar, abierta_en,
                                              para_despues_en)
           values (%s, %s, %s, %s, %s, %s, %s, %s) returning id""",
        (ctx.quien.workspace_id, ctx.quien.membership_id, tipo, task_id,
         json.dumps(jugada, ensure_ascii=False), se_puede_dejar, ctx.ahora,
         ctx.ahora if hay_otra else None))
    pregunta = str(cur.fetchone()["id"])
    if not hay_otra:
        cur.execute(
            """insert into conversation_state (membership_id, workspace_id,
                                               pregunta_abierta_id, actualizado_en)
               values (%s, %s, %s, %s)
               on conflict (membership_id) do update
                  set pregunta_abierta_id = excluded.pregunta_abierta_id,
                      actualizado_en = excluded.actualizado_en""",
            (ctx.quien.membership_id, ctx.quien.workspace_id, pregunta, ctx.ahora))


def _cerrar_preguntas(ctx: Contexto, tipo: str, task_id: str, detalle: dict) -> None:
    cur = ctx.cur
    cur.execute(
        """update conversation_question
              set cerrada_en = %s, cierre = 'respondida', cierre_detalle = %s
            where membership_id = %s and tipo = %s and task_id = %s and cerrada_en is null
        returning id""",
        (ctx.ahora, json.dumps(detalle), ctx.quien.membership_id, tipo, task_id))
    cerradas = [r["id"] for r in cur.fetchall()]
    if cerradas:
        cur.execute(
            """update conversation_state set pregunta_abierta_id = null, actualizado_en = %s
                where membership_id = %s and pregunta_abierta_id = any(%s)""",
            (ctx.ahora, ctx.quien.membership_id, cerradas))


def referente(cur, responsable_membership_id: str) -> dict[str, str] | None:
    """Quien aprueba el trabajo del responsable de una tarea, según la política del espacio
    (`autoridad.puede_aprobar_tarea`: `membership.aprobador_membership_id`). Es a quien le
    llega el aviso de una nueva previsión y quien decide una reasignación (9b, 9g)."""
    cur.execute("""select i.membership_id, i.nombre
                     from membership m
                     join integrante i on i.membership_id = m.aprobador_membership_id
                    where m.id = %s""", (responsable_membership_id,))
    fila = cur.fetchone()
    return {"membership_id": str(fila["membership_id"]), "nombre": fila["nombre"]} \
        if fila else None


def _exigir_responsable(cur, quien: Solicitante, task_id: str) -> dict[str, Any]:
    """La tarea, leída bajo la RLS del espacio, si la persona es su responsable (constitución
    §3: la persona responsable informa los hechos de su tarea)."""
    cur.execute("""select id, titulo, estado, fecha_objetivo, responsable_membership_id
                     from task where id = %s""", (task_id,))
    fila = cur.fetchone()
    if fila is None or str(fila["responsable_membership_id"]) != quien.membership_id:
        raise Denegado("La tarea no es de quien la nombra.")
    return fila


# --- Las fichas ----------------------------------------------------------------------------

def _anotar_inicio(ctx: Contexto, datos: dict, tarea: dict) -> dict:
    r = ejecutar(ctx.cur, ctx.quien, "actualizar_estado",
                 {"tarea_id": tarea["id"], "estado": "en_curso"}, ya_confirmada=True)
    if r.get("estado") != "en_curso":
        return {"resultado": "no_se_puede", "tarea": _tarea(tarea),
                **({"motivo": "falta", "falta": r["falta"]} if r.get("falta")
                   else {"motivo": "tarea_desconocida"})}
    _cerrar_esperas(ctx, tarea["id"])
    return {"resultado": "anotado", "tarea": _tarea(tarea), "estado": "en_curso"}


def _anotar_prevision(ctx: Contexto, datos: dict, tarea: dict) -> dict:
    cur, cal = ctx.cur, ctx.calendario
    try:
        prevista = date.fromisoformat(str(datos["fecha"]).strip())
    except ValueError:
        return {"resultado": "falta_dato", "falta": ["fecha"], "tarea": _tarea(tarea)}
    fila = _exigir_responsable(cur, ctx.quien, tarea["id"])
    if fila["fecha_objetivo"] is None:
        return {"resultado": "no_se_puede", "motivo": "sin_fecha_comprometida",
                "tarea": _tarea(tarea)}
    comprometida = fila["fecha_objetivo"]
    atraso = cal.habiles_entre(comprometida, datetime.combine(prevista, time(12), cal.zona))
    motivo = None if _vacio(datos.get("motivo")) else str(datos["motivo"]).strip()

    # La previsión vigente es la última de la cadena: la que ninguna otra reemplaza.
    cur.execute("""select f.id from task_forecast f
                    where f.task_id = %s
                      and not exists (select 1 from task_forecast g where g.reemplaza_id = f.id)
                    order by f.at desc limit 1""", (tarea["id"],))
    anterior = cur.fetchone()
    cur.execute(
        """insert into task_forecast (task_id, fecha_prevista, motivo, fecha_comprometida,
                                      atraso_dias_habiles, reemplaza_id,
                                      dicho_por_membership_id, at)
           values (%s, %s, %s, %s, %s, %s, %s, %s) returning id""",
        (tarea["id"], prevista, motivo, comprometida, atraso,
         anterior["id"] if anterior else None, ctx.quien.membership_id, ctx.ahora))
    prevision_id = str(cur.fetchone()["id"])
    _cerrar_esperas(ctx, tarea["id"])

    # Un aviso de previsión que todavía no salió queda atrás: lo reemplaza el de ésta, o
    # ninguno si volvió a la fecha comprometida (9b). Nunca en silencio: con su motivo.
    cur.execute(
        """update scheduled_notice
              set estado = 'omitido', motivo_omision = 'hay_una_prevision_mas_nueva',
                  resuelto_en = %s
            where task_id = %s and tipo = 'nueva_prevision' and estado = 'guardado'""",
        (ctx.ahora, tarea["id"]))

    cur.execute("""select t.titulo from dependency d join task t on t.id = d.destino_task_id
                    where d.origen_task_id = %s and t.estado not in ('terminada', 'cancelada')
                    order by t.titulo""", (tarea["id"],))
    dependientes = [r["titulo"] for r in cur.fetchall()]
    hecho = {"resultado": "anotado", "tarea": _tarea(tarea), "prevision": prevista.isoformat(),
             "motivo": motivo,
             "fecha_comprometida": comprometida.astimezone(cal.zona).date().isoformat(),
             "atraso_dias_habiles": atraso, "dependientes": dependientes,
             "aviso_al_referente": None}

    quien_aprueba = referente(cur, str(fila["responsable_membership_id"]))
    if prevista == comprometida.astimezone(cal.zona).date():
        return {**hecho, "sin_aviso": "misma_fecha_comprometida"}
    if quien_aprueba is None:
        return {**hecho, "sin_aviso": "sin_referente"}
    sale = cal.dentro_de_jornada(ctx.ahora)
    hechos_del_aviso = {k: hecho[k] for k in ("prevision", "motivo", "fecha_comprometida",
                                              "atraso_dias_habiles", "dependientes")}
    cur.execute(
        """insert into scheduled_notice (workspace_id, tipo, task_id,
                                         destinatario_membership_id, hechos, programado_para,
                                         dedupe_key, creado_en)
           values (%s, 'nueva_prevision', %s, %s, %s, %s, %s, %s) returning id""",
        (ctx.quien.workspace_id, tarea["id"], quien_aprueba["membership_id"],
         json.dumps({"tarea": tarea["titulo"], "responsable": ctx.quien.nombre,
                     **hechos_del_aviso}, ensure_ascii=False),
         sale, f"motor:nueva_prevision:{prevision_id}", ctx.ahora))
    ctx.avisos_guardados.append(str(cur.fetchone()["id"]))
    return {**hecho, "aviso_al_referente": {"a": quien_aprueba["nombre"],
                                            "sale": sale.isoformat()}}


def _anotar_bloqueo(ctx: Contexto, datos: dict, tarea: dict) -> dict:
    jugada = {"nombre": "anotar_bloqueo", "datos": datos}
    if _vacio(datos.get("causa")):
        # Sin causa no hay bloqueo (mecánica §3): se pregunta y no se anota nada (9c, 1).
        _abrir_pregunta(ctx, "causa_del_bloqueo", tarea["id"], se_puede_dejar=True,
                        jugada=jugada)
        return {"resultado": "falta_dato", "falta": ["causa"], "tarea": _tarea(tarea),
                "pregunta": "causa_del_bloqueo"}
    causa = str(datos["causa"]).strip()
    r = ejecutar(ctx.cur, ctx.quien, "registrar_bloqueo",
                 {"tarea_id": tarea["id"], "causa": causa}, ya_confirmada=True)
    if "bloqueo_id" not in r:
        return {"resultado": "no_se_puede", "motivo": "tarea_cerrada", "tarea": _tarea(tarea)}
    _cerrar_esperas(ctx, tarea["id"])
    hecho = {"resultado": "anotado", "tarea": _tarea(tarea), "causa": causa}
    # Si la causa depende de otra persona (lo dice la IA; sin decirlo, se pregunta), quién
    # se encarga de destrabarlo: una pregunta que espera como un pedido de estado (9c, 2).
    if datos.get("depende_de_otro", True) is not False:
        _abrir_pregunta(ctx, "quien_destraba", tarea["id"], se_puede_dejar=False,
                        jugada={**jugada, "bloqueo_id": r["bloqueo_id"]})
        return {**hecho, "pregunta": "quien_destraba"}
    return {**hecho, "salidas": list(SALIDAS_DE_UN_BLOQUEO)}


def _anotar_quien_destraba(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    cur = ctx.cur
    no_sabe = datos.get("no_sabe") is True
    quien_texto = None if _vacio(datos.get("quien")) else str(datos["quien"]).strip()
    if no_sabe == (quien_texto is not None):
        return {"resultado": "falta_dato", "falta": ["quien_o_no_sabe"]}

    # El bloqueo: el de la tarea nombrada o, si no la nombra, el de la pregunta abierta.
    if tarea is not None:
        task_id = tarea["id"]
    else:
        cur.execute("""select task_id from conversation_question
                        where membership_id = %s and tipo = 'quien_destraba'
                          and cerrada_en is null
                        order by para_despues_en nulls first, abierta_en limit 1""",
                    (ctx.quien.membership_id,))
        pregunta = cur.fetchone()
        task_id = str(pregunta["task_id"]) if pregunta else None
    bloqueo = None
    if task_id is not None:
        _exigir_responsable(cur, ctx.quien, task_id)
        cur.execute("""select id from blocker where task_id = %s and resuelto_en is null
                        order by abierto_en desc limit 1""", (task_id,))
        bloqueo = cur.fetchone()
    if bloqueo is None:
        return {"resultado": "no_se_puede", "motivo": "sin_bloqueo_abierto",
                **({"tarea": _tarea(tarea)} if tarea else {})}
    alias = next((t for t in ctx.tareas if t["id"] == task_id), None)

    integrante = None
    if quien_texto is not None:
        cur.execute("""select membership_id, nombre from integrante
                        where activo and nombre ilike %s order by nombre""",
                    (f"%{quien_texto}%",))
        coinciden = cur.fetchall()
        if len(coinciden) > 1:
            return {"resultado": "falta_dato", "falta": ["integrante"],
                    "coinciden": [c["nombre"] for c in coinciden]}
        integrante = coinciden[0] if coinciden else None
    cur.execute(
        """insert into blocker_unblocker (workspace_id, blocker_id, destraba_membership_id,
                                          destraba_externo, no_sabe,
                                          dicho_por_membership_id, at)
           values (%s, %s, %s, %s, %s, %s, %s) returning id""",
        (ctx.quien.workspace_id, bloqueo["id"],
         integrante["membership_id"] if integrante else None,
         quien_texto if quien_texto is not None and integrante is None else None,
         no_sabe, ctx.quien.membership_id, ctx.ahora))
    anotado = str(cur.fetchone()["id"])
    _cerrar_preguntas(ctx, "quien_destraba", task_id, {"blocker_unblocker_id": anotado})
    _cerrar_esperas(ctx, task_id)
    hecho = {"resultado": "anotado", **({"tarea": _tarea(alias)} if alias else {}),
             "quien_destraba": ({"no_sabe": True} if no_sabe
                                else {"integrante": integrante["nombre"]} if integrante
                                else {"externo": quien_texto})}
    return {**hecho, "salidas": list(SALIDAS_DE_UN_BLOQUEO)} if no_sabe else hecho


def _consultar_pendientes(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    filas = ejecutar(ctx.cur, ctx.quien, "consultar_tareas", {})
    alias = {t["id"]: t["alias"] for t in ctx.tareas}
    zona = ctx.calendario.zona
    tareas = [
        {"alias": alias.get(str(f["id"])), "titulo": f["titulo"], "estado": str(f["estado"]),
         "vence": f["fecha_objetivo"].astimezone(zona).date().isoformat()
         if f["fecha_objetivo"] else None,
         **({"cambios_pedidos": f["cambios_pedidos"]} if f.get("cambios_pedidos") else {})}
        for f in filas if str(f["estado"]) not in ("terminada", "cancelada")]
    return {"resultado": "leido", "tareas": tareas}


def _entregar(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    return {"resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat",
            **({"tarea": _tarea(tarea)} if tarea else {})}


def _pedir_reasignacion(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    decide = referente(ctx.cur, ctx.quien.membership_id)
    return {"resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat",
            "quien_decide": decide["nombre"] if decide else None,
            "alternativa": "anotar_prevision",
            **({"tarea": _tarea(tarea)} if tarea else {})}


FICHAS: Mapping[str, Ficha] = MappingProxyType({f.nombre: f for f in (
    Ficha("anotar_inicio", "anotar que arrancó una tarea",
          necesita=("tarea",), opcional=(),
          comprueba="que sea el responsable y que la tarea esté asignada",
          hace="la pasa a en curso (actualizar_estado)",
          despues="cierra la espera de esa tarea",
          manejar=_anotar_inicio, del_responsable=True,
          estados=frozenset({"asignada"})),
    Ficha("anotar_prevision", "anotar para cuándo prevé terminar una tarea, y por qué",
          necesita=("tarea", "fecha"), opcional=("motivo",),
          comprueba="que sea el responsable, que la tarea esté abierta y tenga fecha "
                    "comprometida",
          hace="anota la previsión con el atraso en días hábiles del espacio; la fecha "
               "comprometida no cambia",
          despues="guarda el aviso al referente, salvo que vuelva a la fecha comprometida; "
                  "cierra la espera de esa tarea",
          manejar=_anotar_prevision, del_responsable=True),
    Ficha("anotar_bloqueo", "anotar que una tarea está trabada y por qué",
          necesita=("tarea",), opcional=("causa", "depende_de_otro"),
          comprueba="que sea el responsable y que la tarea esté abierta",
          hace="sin causa, nada; con causa, registra el bloqueo (registrar_bloqueo)",
          despues="sin causa, pregunta la causa; si depende de otro, pregunta quién lo "
                  "destraba; si no, propone salidas. Ningún aviso al referente (9c)",
          manejar=_anotar_bloqueo, del_responsable=True),
    Ficha("anotar_quien_destraba", "anotar quién se encarga de destrabar un bloqueo",
          necesita=(), opcional=("tarea", "quien", "no_sabe"),
          comprueba="que haya un bloqueo abierto en una tarea suya",
          hace="anota quién destraba: un integrante, alguien de afuera o que no se sabe",
          despues="cierra la pregunta y la espera; si no se sabe, propone salidas",
          manejar=_anotar_quien_destraba),
    Ficha("consultar_pendientes", "contar qué tareas tiene pendientes",
          necesita=(), opcional=(),
          comprueba="nada", hace="lee sus tareas abiertas (consultar_tareas)",
          despues="nada", manejar=_consultar_pendientes),
    Ficha("entregar", "recibir la entrega de una tarea",
          necesita=(), opcional=("tarea",),
          comprueba="nada", hace="nada: todavía no se recibe por chat (9g)",
          despues="sin aviso al administrador", manejar=_entregar, se_ofrece=False),
    Ficha("pedir_reasignacion", "pasarle una tarea a otra persona",
          necesita=(), opcional=("tarea", "a"),
          comprueba="nada", hace="nada: cambiar el responsable no es por chat (9g)",
          despues="dice quién lo decide y ofrece una nueva previsión; sin aviso al "
                  "administrador",
          manejar=_pedir_reasignacion, se_ofrece=False),
)})


def _manejador(ficha: Ficha) -> Manejador:
    return lambda ctx, jugada: _correr(ficha, ctx, jugada)


# La lista cerrada: nombre de la jugada → su manejador.
JUGADAS: Mapping[str, Manejador] = MappingProxyType(
    {nombre: _manejador(ficha) for nombre, ficha in FICHAS.items()})


def lo_que_puede_hacer(jugadas: Mapping[str, Manejador]) -> list[str]:
    """Lo que Leda puede hacer por chat, para el hecho de algo fuera de la lista."""
    return [FICHAS[n].para_que for n in sorted(jugadas) if n in FICHAS and FICHAS[n].se_ofrece]
