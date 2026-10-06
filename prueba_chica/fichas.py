"""La lista cerrada de jugadas y sus fichas (E2-3).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Jugadas"); ADR 0018, decisiones 1, 4 y 9.

Cada jugada se declara con una ficha: qué datos necesita, qué comprueba el código, qué efecto
hace y qué pasa después. La comprobación común (los datos que faltan, la tarea por su alias y
los estados en que la jugada vale) la hace `correr` igual para todas; el manejador de cada
ficha hace sólo lo suyo. Ninguna jugada confirma (9a): el efecto va directo, con
`herramientas.ejecutar(..., ya_confirmada=True)`, que verifica la autoridad igual.

El resultado de una jugada son hechos (un dict), nunca un texto: la IA redacta desde ellos. Una
jugada que existe pero no se puede hacer ahora devuelve por qué (`no_se_puede`), sin aviso al
administrador (decisión 1). Las tareas viajan por su alias; un id de la base nunca llega a la
IA. Cada jugada corre en su propio punto de guardado: si falla, lo suyo se deshace.

Las jugadas de las situaciones generales (`elegir`, `corregir`, `cancelar`,
`dejar_para_despues`) están en `situaciones.py`, y las preguntas, en `preguntas.py` (E2-4); acá
se declaran con las demás. Cada ficha declara lo suyo para ellas: qué preguntas contesta
(`contesta`) y cómo se deshace lo que anota (`deshacer`, para una corrección, 9f). La duda
también es común: si a una jugada le falta la tarea, se pregunta con las tareas en que vale
como opciones (situación general 5). Y lo que una jugada le propone a la persona (`propone`)
queda como tema abierto, una pregunta como cualquier otra (`preguntas.PROPUESTA`; decisión del
usuario, 2026-10-05).

**Con la tarea vencida, una respuesta sin fecha lleva la pregunta de para cuándo** (decisión del
usuario, 2026-10-05; ADR 0018, 9j; conversación 16), también común: si la tarea pasó su fecha de
seguimiento (la comprometida o, si es posterior, la previsión: el ancla, 9i), lo que la jugada
anotó queda anotado y, si no es algo cierto sobre cuándo (`Ficha.algo_cierto`: una fecha o un
bloqueo lo son; un inicio o un avance, no), la espera del estado sigue abierta, Leda vuelve a
pedirlo el día hábil siguiente con la cuenta de nuevo (como después de un avance, 9h) y, en esa
misma respuesta, pregunta para qué día la va a tener. Los hechos dicen que venció y el atraso.
"""

from __future__ import annotations

import json
import unicodedata
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from functools import cached_property
from types import MappingProxyType
from typing import Any

import psycopg

from leda.autoridad import Denegado, Solicitante
from leda.calendario import Calendario
from leda.db import registrar_auditoria
from leda.herramientas import (EstadoCambio, NecesitaConfirmacion, NecesitaElegir,
                               NecesitaOpciones, ejecutar)

from . import cambios_de_estado, preguntas, situaciones
from .ancla import (REEMPLAZADO_POR_UN_AVANCE, REPREGUNTA_DE_ESTADO, anclaje, candado, escalo,
                    pasos)
from .ia import Jugada
from .tiempo import sale as sale_a_la_hora, sale_el


@dataclass(frozen=True)
class Contexto:
    """Lo que un manejador de jugada necesita: la transacción del espacio, quién escribió,
    el momento del motor y lo leído al empezar el turno. `avisos_guardados` junta los
    avisos que guardan las jugadas del turno, para atarlos al turno al registrarlo."""

    cur: psycopg.Cursor
    quien: Solicitante
    entrante_id: str | None         # None: el turno es un toque
    chat_id: int
    texto: str
    ahora: datetime
    estado: dict[str, Any] | None
    tareas: tuple[dict[str, Any], ...]
    ultimos_turnos: tuple[dict[str, Any], ...]
    avisos_guardados: list[str] = field(default_factory=list)
    ultimo_aviso: dict[str, Any] | None = None     # el último que Leda le mandó, y su tarea
    preguntas_del_turno: list[str] = field(default_factory=list)   # abiertas en este turno
    dejadas: list[str] = field(default_factory=list)   # dejadas para después en este turno
    toque: str | None = None        # si el turno es un toque, la etiqueta de la opción tocada
    # La lista cerrada de este turno (nombre → manejador): una opción elegida corre la jugada que
    # esperaba por ella, como una jugada escrita. `None`: la de siempre (`JUGADAS`).
    jugadas: Mapping[str, Callable[..., dict[str, Any]]] | None = None

    def tarea(self, alias: str) -> dict[str, Any] | None:
        return next((t for t in self.tareas if t["alias"] == alias), None)

    @cached_property
    def calendario(self) -> Calendario:
        return Calendario.desde_base(self.cur, self.quien.workspace_id)


Manejador = Callable[[Contexto, Jugada], dict[str, Any]]


# Una tarea abierta: comprometida y sin cerrar (mecánica §3).
ESTADOS_ABIERTOS = frozenset({"asignada", "en_curso", "bloqueada", "en_revision"})


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
    # En qué estados de la tarea vale, si es del responsable: por omisión, abierta.
    estados: frozenset[str] = ESTADOS_ABIERTOS
    # False: no está entre lo que Leda dice que puede hacer: se reconoce pero no se hace por
    # chat (9g), o es de una situación general.
    se_ofrece: bool = True
    contesta: tuple[str, ...] = ()  # las preguntas sobre su tarea que contesta al anotarse
    # Cómo se deshace lo que anotó, agregando hechos (9f): `None` si no hay nada que deshacer;
    # si no, los hechos de la corrección y los datos para anotarlo en la tarea correcta.
    deshacer: Callable[[Contexto, dict[str, Any]], dict[str, Any] | None] | None = None
    # Lo que Leda le propone a la persona en sus hechos (las jugadas o salidas que puede elegir):
    # queda como tema abierto (`preguntas.PROPUESTA`). `None`: no propone nada.
    propone: Callable[[dict[str, Any]], list[str] | None] | None = None
    # Si lo que anota es algo cierto sobre la tarea (una fecha, un bloqueo): con la tarea
    # vencida, lo que no lo es lleva la pregunta de para cuándo (9j).
    algo_cierto: bool = False
    # Si su manejador ya sigue el pedido de estado (un avance, 9h): la regla de la tarea vencida
    # no guarda otro pedido.
    sigue_el_pedido: bool = False
    # Qué es la jugada para la IA que elige: lo que la persona dice para que sea ésta y en qué se
    # distingue de las parecidas, desde el núcleo (mecánica §3 y §8). Va en el esquema de la
    # herramienta, junto a sus datos (revisión del contrato, 2026-10-05). Describe la jugada,
    # nunca un caso ni una frase.
    es: str = ""


# Lo que Leda propone cuando no hay otra persona que destrabe el bloqueo (la persona no sabe
# quién, o le toca a la persona misma; 9c, corregida el 2026-10-05): que alguien la ayude, o más tiempo,
# que es la jugada de la nueva previsión.
SALIDAS_DE_UN_BLOQUEO = ("que_alguien_ayude", "anotar_prevision")

# El estado de un efecto que pasa después (un aviso a otra persona), que su hecho dice siempre,
# explícito: la redacción nunca puede contarlo como hecho (constitución §4). Primer contacto
# real, 2026-10-05: un aviso con sólo `a` y `sale` se contó como enviado.
GUARDADO_SIN_ENVIAR = "guardado_sin_enviar"     # guardado; sale a la hora de `sale`
EN_COLA_SIN_ENVIAR = "en_cola_sin_enviar"       # en la cola de su canal; sale enseguida

# Un avance sin un hecho cierto (`informar_avance`, decisión del usuario, 2026-10-05): la espera
# sigue abierta y Leda vuelve a pedir el estado el día hábil siguiente con un aviso de la
# escalera (`REPREGUNTA_DE_ESTADO`, `escalera.py`), que espera algo cierto. Los pasos de la
# escalera que todavía no salieron quedan reemplazados por él (`REEMPLAZADO_POR_UN_AVANCE`): ya
# no es silencio. Lo que espera saber depende del estado de la tarea (`avisos.espera_saber`):
# esto es lo de una tarea en curso.
ESPERA_ALGO_CIERTO = ("si_la_termino", "para_cuando_la_termina", "si_esta_trabada")

# El atraso que tendrá la tarea si se cumple una previsión: distinto del atraso de hoy
# (`atraso_dias_habiles`), con su propia clave (revisión del contrato, 2026-10-05; ronda 1: el
# del aviso al referente se contó como el atraso de hoy). Su significado, en `hechos.py`.
ATRASO_SI_SE_CUMPLE = "atraso_si_se_cumple_la_prevision_dias_habiles"


# Lo que un hecho nombra y pasa después (un aviso guardado, una espera, una pregunta) puede
# cambiar por otra jugada del mismo mensaje: una fecha contesta la espera de un avance y su
# pedido del día siguiente ya no sale. Por eso el hecho lleva, en esta clave interna, el id de
# cada efecto que nombra, y al terminar todas las jugadas el turno vuelve a leerlos de la base y
# pone su estado final (`efectos.al_final_del_turno`; ADR 0018, 9k). La clave se saca antes de
# redactar: ni la IA ni el registro de turnos ven un id.
EFECTOS = "_efectos"
AVISO, ESPERA, PREGUNTA = "aviso", "espera", "pregunta"     # de qué tabla es el efecto


def nombrar_efecto(hecho: dict[str, Any], clave: str, de: str, efecto_id: Any) -> None:
    """Anota en el hecho que `clave` nombra el efecto `efecto_id` (un aviso, una espera o una
    pregunta), para leerlo al terminar el turno."""
    hecho.setdefault(EFECTOS, []).append({"clave": clave, "de": de, "id": str(efecto_id)})


def _juntar(hecho: dict[str, Any], mas: dict[str, Any]) -> None:
    """`hecho.update(mas)`, sin perder los efectos que ya nombraba el hecho."""
    for clave, valor in mas.items():
        if clave == EFECTOS:
            hecho.setdefault(EFECTOS, []).extend(valor)
        else:
            hecho[clave] = valor


def _es_un_aviso_al_referente(tipo: str) -> dict[str, Any]:
    """Los hechos de un aviso al referente dicen qué aviso son y que no piden respuesta: es
    información para él (9i)."""
    return {"aviso": tipo, "necesita_respuesta": False}
_PASOS_QUE_REEMPLAZA = ("pedido_de_estado", REPREGUNTA_DE_ESTADO, "escalamiento")


# --- Comprobación común --------------------------------------------------------------------

def correr(ficha: Ficha, ctx: Contexto, jugada: Jugada) -> dict[str, Any]:
    """La comprobación común y el manejador de la ficha; si la jugada se anotó, contesta las
    preguntas que esperaban eso (`preguntas.contestar`)."""
    datos = dict(jugada.datos or {})
    faltan = [k for k in ficha.necesita if _vacio(datos.get(k))]
    if "tarea" in faltan:
        return _duda(ficha, ctx, datos)
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
                if tarea["estado"] not in ficha.estados:
                    # Desde cuándo, si el motor lo sabe (`cambios_de_estado.py`).
                    return _hecho(ficha, "no_se_puede", motivo="estado",
                                  tarea=_tarea(tarea), estado=tarea["estado"],
                                  estado_desde=cambios_de_estado.desde(
                                      ctx.cur, tarea["id"], ctx.quien.membership_id,
                                      tarea["estado"], ctx.calendario.zona))
            hecho = {"jugada": ficha.nombre, **ficha.manejar(ctx, datos, tarea)}
            de_la_tarea = tarea or ctx.tarea((hecho.get("tarea") or {}).get("alias", ""))
            if hecho.get("resultado") == "anotado" and hecho["jugada"] == ficha.nombre:
                if de_la_tarea is not None:
                    preguntas.contestar(ctx, ficha.nombre, ficha.contesta, de_la_tarea["id"])
            if hecho["jugada"] == ficha.nombre:
                # Primero la pregunta de la tarea vencida (9j) y después lo propuesto: si ya se
                # pregunta algo en esta respuesta, lo propuesto queda para después (un tema a
                # la vez; nunca dos preguntas juntas).
                _si_esta_vencida(ficha, ctx, hecho, de_la_tarea)
                _proponer(ficha, ctx, hecho, de_la_tarea)
            return hecho
    except Exception as e:      # el punto de guardado ya deshizo lo de esta jugada
        rechazo = _rechazo_del_dominio(e)
        if rechazo is None:
            raise
        resultado, mas = rechazo
        return _hecho(ficha, resultado, tarea=_tarea(tarea) if tarea else None, **mas)


def _proponer(ficha: Ficha, ctx: Contexto, hecho: dict[str, Any],
              tarea: dict[str, Any] | None) -> None:
    """Lo que la jugada le propone a la persona queda como tema abierto: una pregunta con lo
    propuesto, ordenada con las demás (un tema a la vez). Los hechos la nombran como a
    cualquier pregunta (`pregunta` o `pregunta_para_despues`)."""
    propuesto = ficha.propone(hecho) if ficha.propone is not None else None
    if not propuesto:
        return
    ahora, pregunta_id = preguntas.abrir_con_id(
        ctx, preguntas.PROPUESTA, tarea["id"] if tarea else None,
        jugada={"nombre": ficha.nombre, "propone": list(propuesto)})
    _nombrar_pregunta(hecho, _clave_de_pregunta(ahora), preguntas.PROPUESTA, pregunta_id)


def _si_esta_vencida(ficha: Ficha, ctx: Contexto, hecho: dict[str, Any],
                     tarea: dict[str, Any] | None) -> None:
    """La regla de la tarea vencida (9j, ver el módulo), igual para toda jugada que anota algo
    sobre una tarea del responsable sin que sea algo cierto sobre cuándo."""
    if (hecho.get("resultado") != "anotado" or tarea is None or ficha.algo_cierto
            or not ficha.del_responsable):
        return
    vencida = _vencida(ctx, tarea)
    if vencida is None:
        return
    hecho["vencida"] = vencida
    if not ficha.sigue_el_pedido:
        candado(ctx.cur, tarea["id"])
        _juntar(hecho, _seguir_pidiendo(ctx, tarea, _espera_del_estado(ctx, tarea),
                                        {"jugada": ficha.nombre,
                                         "dijo": (ctx.texto or ctx.toque or "").strip()}))
    fecha = preguntas.FECHA_DE_LA_TAREA
    if fecha not in (hecho.get("pregunta"), hecho.get("pregunta_para_despues")):
        _abrir_pregunta(ctx, hecho, fecha, tarea["id"], jugada={"nombre": ficha.nombre})


def _vencida(ctx: Contexto, tarea: dict[str, Any]) -> dict[str, Any] | None:
    """Si la tarea pasó su fecha de seguimiento (el ancla, 9i): la fecha comprometida, el atraso
    contra ella (lo calcula el código) y, si el ancla era una previsión, cuál. `None` si no."""
    cal = ctx.calendario
    ctx.cur.execute("select fecha_objetivo from task where id = %s", (tarea["id"],))
    fila = ctx.cur.fetchone()
    if fila is None or fila["fecha_objetivo"] is None:
        return None
    vence = fila["fecha_objetivo"].astimezone(cal.zona).date()
    de = anclaje(ctx.cur, tarea["id"], vence)
    if ctx.ahora.astimezone(cal.zona).date() <= de.fecha:
        return None
    return {"fecha_comprometida": vence.isoformat(),
            "atraso_dias_habiles": cal.habiles_entre(fila["fecha_objetivo"], ctx.ahora),
            **({"prevision_vencida": de.fecha.isoformat()} if de.fecha > vence else {})}


def _espera_del_estado(ctx: Contexto, tarea: dict[str, Any]) -> dict[str, Any]:
    """La espera del estado de la tarea: la abierta o, si la jugada la contestó (un inicio),
    una nueva: la respuesta no fue algo cierto sobre cuándo, así que se sigue esperando."""
    cur, persona = ctx.cur, ctx.quien.membership_id
    cur.execute("""select * from pending_reply
                    where membership_id = %s and task_id = %s and tipo = %s
                      and satisfecho_en is null
                    order by preguntado_en desc limit 1""",
                (persona, tarea["id"], preguntas.ESTADO_DE_LA_TAREA))
    espera = cur.fetchone()
    if espera is not None:
        return espera
    cal = ctx.calendario
    cur.execute(
        """insert into pending_reply (workspace_id, membership_id, task_id, tipo,
                                      preguntado_en, vence_en)
           values (%s, %s, %s, %s, %s, %s) returning *""",
        (ctx.quien.workspace_id, persona, tarea["id"], preguntas.ESTADO_DE_LA_TAREA, ctx.ahora,
         cal.dentro_de_jornada(cal.sumar_habiles(ctx.ahora, 1))))
    return cur.fetchone()


def _duda(ficha: Ficha, ctx: Contexto, datos: dict[str, Any]) -> dict[str, Any]:
    """Situación general 5: la jugada no dice de qué tarea habla. Leda no adivina: pregunta
    con las tareas de la persona en que la jugada vale como opciones, y la jugada espera la
    elección. Sin ninguna en que valga, lo dice."""
    candidatas = [t for t in ctx.tareas if t["estado"] in ficha.estados]
    if not candidatas:
        return _hecho(ficha, "no_se_puede", motivo="ninguna_tarea_posible")
    ahora, pregunta_id = preguntas.abrir_con_id(
        ctx, preguntas.CUAL_TAREA, None, jugada={"nombre": ficha.nombre, "datos": datos},
        opciones_de_tareas=candidatas)
    hecho = _hecho(ficha, "falta_dato", falta=["tarea"])
    _nombrar_pregunta(hecho, _clave_de_pregunta(ahora), preguntas.CUAL_TAREA, pregunta_id)
    return hecho


def _nombrar_pregunta(hecho: dict[str, Any], clave: str, tipo: str,
                     pregunta_id: str | None = None) -> None:
    """Pone en los hechos la pregunta que abrió la jugada, siempre como un nombre (`pregunta` o
    `pregunta_para_despues`). Si la clave ya nombra otra (dos que quedaron para después), la
    nueva va a `otras_preguntas_para_despues`, una lista: nunca se pierde una y cada clave
    tiene siempre la misma forma. Con su id, el turno la vuelve a leer al terminar (`EFECTOS`)
    y la nombra como quedó."""
    if pregunta_id is not None:
        nombrar_efecto(hecho, clave, PREGUNTA, pregunta_id)
    nombrar_tipo_de_pregunta(hecho, clave, tipo)


def nombrar_tipo_de_pregunta(hecho: dict[str, Any], clave: str, tipo: str) -> None:
    antes = hecho.get(clave)
    if antes is None or antes == tipo:
        hecho[clave] = tipo
    elif tipo not in hecho.setdefault(OTRAS_PARA_DESPUES, []):
        hecho[OTRAS_PARA_DESPUES].append(tipo)


OTRAS_PARA_DESPUES = "otras_preguntas_para_despues"


def _clave_de_pregunta(ahora: bool) -> str:
    """En el hecho de una jugada, la pregunta que abrió: la que se hace ahora (`pregunta`) o
    una que quedó para después (`pregunta_para_despues`), que no se hace en esta respuesta."""
    return "pregunta" if ahora else "pregunta_para_despues"


def _rechazo_del_dominio(e: Exception) -> tuple[str, dict[str, Any]] | None:
    """Lo que `herramientas.ejecutar` levanta como respuesta del dominio, en hechos; `None`
    si es una falla de verdad. Nunca su texto: puede traer detalles técnicos (§10)."""
    if isinstance(e, Denegado):
        return "no_se_puede", {"motivo": "no_autorizado"}
    if isinstance(e, NecesitaElegir):
        return "falta_dato", {"falta": [e.campo],
                              "coinciden": [nombre for nombre, _ in e.opciones]}
    if isinstance(e, (NecesitaConfirmacion, EstadoCambio, NecesitaOpciones)):
        # Con `ya_confirmada` no deberían llegar: piden un paso que esta jugada no tiene.
        return "no_se_puede", {"motivo": "pide_otro_paso"}
    if isinstance(e, psycopg.errors.RaiseException):
        # Una regla del trabajo que la base hace cumplir (un disparador), no una falla.
        return "no_se_puede", {"motivo": "regla_del_trabajo"}
    return None


def _no_hecho(r: dict[str, Any], tarea: dict[str, Any]) -> dict[str, Any]:
    """Un rechazo de negocio que la operación devuelve como dict, en hechos."""
    if r.get("falta"):
        return {"resultado": "no_se_puede", "motivo": "falta", "falta": r["falta"],
                "tarea": _tarea(tarea)}
    motivo = ("tarea_cerrada" if "cerrada" in str(r.get("error", ""))
              else "tarea_desconocida")
    return {"resultado": "no_se_puede", "motivo": motivo, "tarea": _tarea(tarea)}


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


def _abrir_pregunta(ctx: Contexto, hecho: dict[str, Any], tipo: str, task_id: str, *,
                    jugada: dict[str, Any]) -> None:
    """Una pregunta de Leda, ordenada con las demás (`preguntas.abrir`: nunca dos juntas, 9d);
    si su tipo espera respuesta, con su espera. El hecho la nombra con su clave
    (`_clave_de_pregunta`) y su id (`_nombrar_pregunta`)."""
    ahora, pregunta_id = preguntas.abrir_con_id(ctx, tipo, task_id, jugada=jugada)
    _nombrar_pregunta(hecho, _clave_de_pregunta(ahora), tipo, pregunta_id)


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
        return _no_hecho(r, tarea)
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
             ATRASO_SI_SE_CUMPLE: atraso, "dependientes": dependientes,
             "aviso_al_referente": None}

    quien_aprueba = referente(cur, str(fila["responsable_membership_id"]))
    if prevista == comprometida.astimezone(cal.zona).date():
        return {**hecho, "sin_aviso": "misma_fecha_comprometida"}
    if quien_aprueba is None:
        return {**hecho, "sin_aviso": "sin_referente"}
    sale = sale_a_la_hora(cal, ctx.ahora)
    hechos_del_aviso = {k: hecho[k] for k in ("prevision", "motivo", "fecha_comprometida",
                                              ATRASO_SI_SE_CUMPLE, "dependientes")}
    cur.execute(
        """insert into scheduled_notice (workspace_id, tipo, task_id,
                                         destinatario_membership_id, hechos, programado_para,
                                         dedupe_key, creado_en)
           values (%s, 'nueva_prevision', %s, %s, %s, %s, %s, %s) returning id""",
        (ctx.quien.workspace_id, tarea["id"], quien_aprueba["membership_id"],
         json.dumps({**_es_un_aviso_al_referente("nueva_prevision"), "tarea": tarea["titulo"],
                     "responsable": ctx.quien.nombre, **hechos_del_aviso}, ensure_ascii=False),
         sale, f"motor:nueva_prevision:{prevision_id}", ctx.ahora))
    aviso_id = str(cur.fetchone()["id"])
    ctx.avisos_guardados.append(aviso_id)
    hecho["aviso_al_referente"] = {"a": quien_aprueba["nombre"], "estado": GUARDADO_SIN_ENVIAR,
                                   "sale": sale.isoformat()}
    nombrar_efecto(hecho, "aviso_al_referente", AVISO, aviso_id)
    return hecho


def _anotar_bloqueo(ctx: Contexto, datos: dict, tarea: dict) -> dict:
    jugada = {"nombre": "anotar_bloqueo", "datos": datos}
    if _vacio(datos.get("causa")):
        # Sin causa no hay bloqueo (mecánica §3): se pregunta y no se anota nada (9c, 1).
        sin_causa = {"resultado": "falta_dato", "falta": ["causa"], "tarea": _tarea(tarea)}
        _abrir_pregunta(ctx, sin_causa, preguntas.CAUSA_DEL_BLOQUEO, tarea["id"], jugada=jugada)
        return sin_causa
    causa = str(datos["causa"]).strip()
    r = ejecutar(ctx.cur, ctx.quien, "registrar_bloqueo",
                 {"tarea_id": tarea["id"], "causa": causa}, ya_confirmada=True)
    if "bloqueo_id" not in r:
        return _no_hecho(r, tarea)
    _cerrar_esperas(ctx, tarea["id"])
    # La causa contesta su pregunta antes de que se abra la siguiente.
    preguntas.contestar(ctx, "anotar_bloqueo", (preguntas.CAUSA_DEL_BLOQUEO,), tarea["id"])
    # Todo bloqueo con causa: quién lo puede destrabar, una pregunta que espera respuesta (su
    # ficha de pregunta lo dice: abre su espera y la escalera la repite). Lo decide la respuesta
    # de la persona, no un juicio de la IA sobre la causa (9c, corregida el 2026-10-05).
    anotado = {"resultado": "anotado", "tarea": _tarea(tarea), "causa": causa}
    _abrir_pregunta(ctx, anotado, preguntas.QUIEN_DESTRABA, tarea["id"],
                    jugada={**jugada, "bloqueo_id": r["bloqueo_id"]})
    return anotado


def _anotar_quien_destraba(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    cur = ctx.cur
    no_sabe = datos.get("no_sabe") is True
    nadie_mas = datos.get("nadie_mas") is True      # le toca a la persona misma
    quien_texto = None if _vacio(datos.get("quien")) else str(datos["quien"]).strip()
    if no_sabe + nadie_mas + (quien_texto is not None) != 1:
        # Una sola respuesta, de las tres que puede ser (revisión de la E2-3b).
        return {"resultado": "falta_dato", "falta": ["quien_destraba"],
                "puede_ser": ["alguien", "no_sabe", "nadie_mas"]}

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
        coinciden = integrantes_que_coinciden(cur, quien_texto)
        if len(coinciden) > 1:
            return {"resultado": "falta_dato", "falta": ["integrante"],
                    "coinciden": [c["nombre"] for c in coinciden]}
        integrante = coinciden[0] if coinciden else None
        # Nombrarse a sí misma es decir que le toca a la persona que escribe.
        nadie_mas = (integrante is not None
                     and str(integrante["membership_id"]) == ctx.quien.membership_id)
    if nadie_mas:
        integrante = {"membership_id": ctx.quien.membership_id, "nombre": ctx.quien.nombre}
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
    preguntas.cerrar_de_tipo(ctx, "quien_destraba", task_id, "respondida",
                             {"blocker_unblocker_id": anotado})
    _cerrar_esperas(ctx, task_id)
    hecho = {"resultado": "anotado", **({"tarea": _tarea(alias)} if alias else {}),
             "quien_destraba": ({"no_sabe": True} if no_sabe
                                else {"nadie_mas": True} if nadie_mas
                                else {"integrante": integrante["nombre"]} if integrante
                                else {"externo": quien_texto})}
    # Con otra persona que lo destraba, seguirla es la persecución (ADR 0017, decisión 3a),
    # de la prueba siguiente; sin otra persona, las salidas (9c, corregida el 2026-10-05).
    sin_otra_persona = no_sabe or nadie_mas
    return {**hecho, "salidas": list(SALIDAS_DE_UN_BLOQUEO)} if sin_otra_persona else hecho


def _destrabar(ctx: Contexto, datos: dict, tarea: dict) -> dict:
    """La persona dice que la causa del bloqueo ya no está (decisión del usuario, 2026-10-05; ADR
    0018, 9l). Se cierra directo, como se anotó (9a), con la operación del dominio
    (`resolver_bloqueo`): la tarea vuelve al estado que tenía antes de bloquearse (mecánica §3).
    Lo que esperaba algo del bloqueo se cierra con él: la pregunta de quién lo destraba (la
    contesta, por su ficha), lo propuesto para salir de él y sus esperas. Con más de un bloqueo
    abierto no se elige cuál: se dice, con sus causas.

    La tarea vuelve al seguimiento (la escalera sólo sigue las que no tienen un bloqueo
    abierto). Antes de su fecha, la escalera sigue sola. Si su seguimiento ya había empezado (hoy
    es su fecha, o la pasó), la respuesta no es algo cierto sobre cuándo la termina: la espera
    del estado queda abierta y Leda vuelve a pedirlo el día hábil siguiente con la cuenta de
    nuevo, como después de un avance (9h); vencida, además, la pregunta de para cuándo (9j,
    `_si_esta_vencida`)."""
    cur = ctx.cur
    cur.execute("""select id, causa from blocker where task_id = %s and resuelto_en is null
                    order by abierto_en, causa""", (tarea["id"],))
    abiertos = cur.fetchall()
    if not abiertos:
        return {"resultado": "no_se_puede", "motivo": "sin_bloqueo_abierto",
                "tarea": _tarea(tarea)}
    if len(abiertos) > 1:
        return {"resultado": "no_se_puede", "motivo": "varios_bloqueos_abiertos",
                "tarea": _tarea(tarea), "causas": [b["causa"] for b in abiertos]}
    [bloqueo] = abiertos
    dijo = (ctx.texto or ctx.toque or "").strip() or "la causa del bloqueo ya no está"
    r = ejecutar(cur, ctx.quien, "resolver_bloqueo",
                 {"bloqueo_id": str(bloqueo["id"]), "resolucion": dijo}, ya_confirmada=True)
    if not r.get("resuelto"):
        return _no_hecho(r, tarea)
    _cerrar_esperas(ctx, tarea["id"])
    preguntas.cerrar_las_de_una_jugada(ctx, "anotar_quien_destraba", tarea["id"], "sin_efecto",
                                       {"jugada": "destrabar", "tarea": tarea["id"]})
    cur.execute("select estado::text estado from task where id = %s", (tarea["id"],))
    hecho: dict[str, Any] = {"resultado": "anotado", "tarea": _tarea(tarea),
                             "bloqueo_resuelto": {"causa": bloqueo["causa"]},
                             "estado": cur.fetchone()["estado"]}
    fila = _exigir_responsable(cur, ctx.quien, tarea["id"])
    if fila["fecha_objetivo"] is not None:
        cal = ctx.calendario
        de = anclaje(cur, tarea["id"], fila["fecha_objetivo"].astimezone(cal.zona).date())
        if ctx.ahora.astimezone(cal.zona).date() >= de.fecha:
            candado(cur, tarea["id"])
            _juntar(hecho, _seguir_pidiendo(ctx, tarea, _espera_del_estado(ctx, tarea),
                                            {"jugada": "destrabar", "dijo": dijo}))
    return hecho


def palabras(texto: str) -> list[str]:
    """Las palabras de un nombre, sin mayúsculas ni acentos."""
    sin_acentos = unicodedata.normalize("NFKD", texto.casefold())
    sin_acentos = "".join(c for c in sin_acentos if not unicodedata.combining(c))
    return "".join(c if c.isalnum() else " " for c in sin_acentos).split()


def integrantes_que_coinciden(cur, dicho: str) -> list[dict[str, Any]]:
    """Los integrantes del espacio cuyo nombre tiene, como palabras enteras, todas las
    palabras de lo dicho: "ismael" es Ismael Soschinski; "Mar" no es Marcos. Se compara
    acá y no con un patrón de la base, así nada de lo dicho actúa como comodín."""
    buscadas = palabras(dicho)
    if not buscadas:
        return []
    cur.execute("select membership_id, nombre from integrante where activo order by nombre")
    return [f for f in cur.fetchall() if set(buscadas) <= set(palabras(f["nombre"]))]


def _informar_avance(ctx: Contexto, datos: dict, tarea: dict) -> dict:
    """La respuesta a un pedido de estado que cuenta un avance sin un hecho cierto (no dice que
    la terminó, ni para cuándo, ni que está trabada). Se anota con las palabras de la persona,
    atribuido y auditado, sin cambiar estado ni fecha; la espera sigue abierta, porque la
    respuesta no es cierta, y Leda vuelve a pedir el estado el día hábil siguiente, dentro de la
    escalera de su ancla (la previsión, si es posterior al vencimiento; 9i). No es silencio: la
    escalera cuenta sólo los pedidos sin respuesta (`escalera.py`). A la segunda respuesta así
    para la misma espera, Leda pregunta directo para cuándo (decisión del usuario, 2026-10-05);
    con la tarea vencida, ya a la primera (9j, `_si_esta_vencida`).

    Si no hay un pedido siguiente, los hechos lo dicen (nunca en silencio): la tarea no tiene
    vencimiento, o la escalera de su ancla ya terminó al escalar (y a quién se le avisó)."""
    cur, persona = ctx.cur, ctx.quien.membership_id
    dijo = str(datos["palabras"]).strip() if not _vacio(datos.get("palabras")) \
        else ctx.texto.strip()
    if not dijo:
        return {"resultado": "falta_dato", "falta": ["palabras"], "tarea": _tarea(tarea)}
    # La escalera no toca la tarea mientras se reemplazan sus pasos (`ancla.candado`).
    candado(cur, tarea["id"])
    cur.execute("""select * from pending_reply
                    where membership_id = %s and task_id = %s and tipo = %s
                      and satisfecho_en is null
                    order by preguntado_en desc limit 1""",
                (persona, tarea["id"], preguntas.ESTADO_DE_LA_TAREA))
    espera = cur.fetchone()
    if espera is None:
        return {"resultado": "no_se_puede", "motivo": "nadie_pidio_el_estado",
                "tarea": _tarea(tarea)}

    registrar_auditoria(cur, accion="informar_avance", workspace_id=ctx.quien.workspace_id,
                        actor_app_user_id=ctx.quien.app_user_id, actor_kind="persona",
                        sujeto_tipo="task", sujeto_id=tarea["id"],
                        detalle={"dijo": dijo, "dicho_por_membership_id": persona,
                                 "at": ctx.ahora.isoformat(),
                                 "inbound_message_id": ctx.entrante_id})
    hecho: dict[str, Any] = {"resultado": "anotado", "tarea": _tarea(tarea),
                             "avance": {"dijo": dijo}, "el_pedido_de_estado": "sigue_abierto"}
    nombrar_efecto(hecho, "el_pedido_de_estado", ESPERA, espera["id"])
    _juntar(hecho, _seguir_pidiendo(ctx, tarea, espera, {"dijo": dijo}))
    if hecho.get("veces_sin_algo_cierto", 0) > 1:
        _abrir_pregunta(ctx, hecho, preguntas.FECHA_DE_LA_TAREA, tarea["id"],
                        jugada={"nombre": "informar_avance", "datos": datos})
    return hecho


def _seguir_pidiendo(ctx: Contexto, tarea: dict[str, Any], espera: dict[str, Any],
                     contesto: dict[str, Any]) -> dict[str, Any]:
    """Una respuesta que no es algo cierto deja la espera abierta y Leda vuelve a pedir el
    estado el día hábil siguiente, dentro de la escalera de su ancla (la previsión, si es
    posterior al vencimiento; 9i): ese pedido es el primero de una cuenta nueva y reemplaza los
    pasos guardados que no salieron (9h). Los hechos que agrega: cuándo vuelve a pedirlo y
    cuántas respuestas así lleva la espera, o por qué no vuelve a pedirlo (nunca en silencio:
    sin vencimiento, o con la escalera de su ancla ya escalada). `contesto`: lo que contestó,
    que el pedido siguiente recuerda (`avance_anterior`). Quien llama tiene la tarea tomada
    (`ancla.candado`)."""
    cur, cal, persona = ctx.cur, ctx.calendario, ctx.quien.membership_id
    fila = _exigir_responsable(cur, ctx.quien, tarea["id"])
    if fila["fecha_objetivo"] is None:      # sin vencimiento no hay escalera que vuelva a pedir
        return {"no_vuelve_a_pedir_el_estado": {"motivo": "sin_fecha_comprometida"}}
    vence = fila["fecha_objetivo"].astimezone(cal.zona).date()
    de = anclaje(cur, tarea["id"], vence)      # la escalera de la previsión, si es posterior
    escalon = pasos(cur, tarea["id"], de)
    if escalo(escalon, espera):
        return {"no_vuelve_a_pedir_el_estado": {
            "motivo": "ya_se_escalo", "escalado_a": _escalado_a(cur, escalon)}}

    # Los pasos de la escalera de esta ancla que todavía no salieron ya no corresponden: la
    # persona contestó. Los reemplaza el pedido del día hábil siguiente.
    cur.execute("""update scheduled_notice
                      set estado = 'omitido', motivo_omision = %s, resuelto_en = %s,
                          proximo_intento_en = null
                    where id = any(%s) and estado = 'guardado'""",
                (REEMPLAZADO_POR_UN_AVANCE, ctx.ahora,
                 [p["id"] for p in escalon if p["tipo"] in _PASOS_QUE_REEMPLAZA]))
    # La cuenta es de la espera, que la clave del pedido nombra: la misma espera y la misma
    # cuenta dan la misma clave, así que nada se guarda dos veces.
    de_la_espera = f"e{espera['id']}"
    veces = 1 + sum(p["tipo"] == REPREGUNTA_DE_ESTADO
                    and p["dedupe_key"].split(":")[5:6] == [de_la_espera] for p in escalon)
    hoy = ctx.ahora.astimezone(cal.zona).date()
    sale = sale_el(cal, cal.proximo_habil(hoy + timedelta(days=1)))
    # Lo manda Leda por su cuenta, como los demás pasos de la escalera: sin turno que lo cause.
    clave = f"motor:{REPREGUNTA_DE_ESTADO}:{tarea['id']}:{de.clave}:0:{de_la_espera}:a{veces}"
    cur.execute(
        """insert into scheduled_notice (workspace_id, tipo, task_id,
                                         destinatario_membership_id, hechos, programado_para,
                                         dedupe_key, creado_en)
           values (%s, %s, %s, %s, %s, %s, %s, %s)
           on conflict (workspace_id, dedupe_key) do nothing""",
        (ctx.quien.workspace_id, REPREGUNTA_DE_ESTADO, tarea["id"], persona,
         json.dumps({"aviso": REPREGUNTA_DE_ESTADO, "necesita_respuesta": True,
                     "avance_anterior": {**contesto, "el": hoy.isoformat()},
                     "tarea": tarea["titulo"], "vence": vence.isoformat(),
                     **({"seguimiento_por": "prevision"} if de.fecha > vence else {})},
                    ensure_ascii=False),
         sale, clave, ctx.ahora))
    cur.execute("select id from scheduled_notice where workspace_id = %s and dedupe_key = %s",
                (ctx.quien.workspace_id, clave))
    pidiendo = {"vuelve_a_pedir_el_estado": {"estado": GUARDADO_SIN_ENVIAR,
                                             "sale": sale.isoformat()},
                "veces_sin_algo_cierto": veces}
    nombrar_efecto(pidiendo, "vuelve_a_pedir_el_estado", AVISO, cur.fetchone()["id"])
    return pidiendo


def _escalado_a(cur, escalon: list[dict[str, Any]]) -> list[dict[str, str]]:
    """A quiénes llegó el escalamiento de la escalera, con el estado de su aviso."""
    ids = [str(p["id"]) for p in escalon
           if p["tipo"] == "escalamiento" and p["estado"] in ("enviado", "fallido")]
    if not ids:
        return []
    cur.execute("""select i.nombre, a.estado from scheduled_notice a
                     join integrante i on i.membership_id = a.destinatario_membership_id
                    where a.id = any(%s::uuid[]) order by i.nombre""", (ids,))
    return [{"a": f["nombre"], "estado": "enviado" if f["estado"] == "enviado" else "no_salio"}
            for f in cur.fetchall()]


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


# Lo que no se hace por chat y no tiene otra forma definida de hacerse en esta etapa: el hecho lo
# dice, para que la redacción no invente un canal (ronda 3, conversación 12, paso 6: "presentala
# por fuera de este chat"). Qué hace la persona con una tarea terminada mientras la entrega no
# se recibe por chat no está decidido (ADR 0018, 9g): `PENDIENTE` del usuario.
NINGUNA_DEFINIDA = "ninguna_definida"


def _entregar(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    return {"resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat",
            **({"tarea": _tarea(tarea)} if tarea else {}),
            "otra_forma_de_hacerlo": NINGUNA_DEFINIDA}


def _pedir_reasignacion(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    decide = referente(ctx.cur, ctx.quien.membership_id)
    return {"resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat",
            "quien_decide": decide["nombre"] if decide else None,
            "alternativa": "anotar_prevision",
            **({"tarea": _tarea(tarea)} if tarea else {})}


# --- Cómo se deshace lo anotado (9f) -------------------------------------------------------
#
# Una corrección agrega hechos, nunca borra (constitución §12): la tarea vuelve a como estaba
# por la misma operación del dominio con que cambia siempre, y la historia guarda los dos.

MOTIVO_DE_LA_CORRECCION = "corrección: se había anotado en la tarea equivocada"


def _deshacer_inicio(ctx: Contexto, tarea: dict) -> dict | None:
    """Un inicio sólo se anota desde `asignada` (su ficha), así que vuelve a `asignada`."""
    fila = _exigir_responsable(ctx.cur, ctx.quien, tarea["id"])
    if str(fila["estado"]) != "en_curso":
        return None
    r = ejecutar(ctx.cur, ctx.quien, "actualizar_estado",
                 {"tarea_id": tarea["id"], "estado": "asignada",
                  "motivo": MOTIVO_DE_LA_CORRECCION}, ya_confirmada=True)
    if r.get("estado") != "asignada":
        return None
    return {"hechos": {"vuelve_a": {"estado": "asignada"}}, "datos": {}}


def _deshacer_prevision(ctx: Contexto, tarea: dict) -> dict | None:
    """Una previsión de corrección que reemplaza a la equivocada con la de antes (o con la
    fecha comprometida, si no había). Su aviso al referente: si no salió, se retira; si salió,
    se guarda una corrección breve para él (9f). Si no salió y la de antes tenía un aviso que
    se había retirado por ella, ése se vuelve a guardar (`_rearmar_aviso_de_la_anterior`)."""
    cur, cal = ctx.cur, ctx.calendario
    cur.execute("""select * from task_forecast f
                    where f.task_id = %s
                      and not exists (select 1 from task_forecast g where g.reemplaza_id = f.id)
                    order by f.at desc limit 1""", (tarea["id"],))
    equivocada = cur.fetchone()
    if (equivocada is None or equivocada["es_correccion"]
            or str(equivocada["dicho_por_membership_id"]) != ctx.quien.membership_id):
        return None
    anterior = None
    if equivocada["reemplaza_id"] is not None:
        cur.execute("select * from task_forecast where id = %s", (equivocada["reemplaza_id"],))
        anterior = cur.fetchone()
    comprometida = equivocada["fecha_comprometida"].astimezone(cal.zona).date()
    vuelve = anterior["fecha_prevista"] if anterior else comprometida
    cur.execute(
        """insert into task_forecast (task_id, fecha_prevista, motivo, fecha_comprometida,
                                      atraso_dias_habiles, reemplaza_id, es_correccion,
                                      dicho_por_membership_id, at)
           values (%s, %s, %s, %s, %s, %s, true, %s, %s) returning id""",
        (tarea["id"], vuelve, anterior["motivo"] if anterior else None,
         equivocada["fecha_comprometida"],
         anterior["atraso_dias_habiles"] if anterior else 0, equivocada["id"],
         ctx.quien.membership_id, ctx.ahora))
    correccion_id = str(cur.fetchone()["id"])
    hechos: dict[str, Any] = {
        "vuelve_a": ({"prevision": vuelve.isoformat()} if anterior
                     else {"fecha_comprometida": comprometida.isoformat()}),
        "prevision_corregida": equivocada["fecha_prevista"].isoformat()}

    cur.execute("""select id, estado from scheduled_notice
                    where workspace_id = %s and dedupe_key = %s""",
                (ctx.quien.workspace_id, f"motor:nueva_prevision:{equivocada['id']}"))
    aviso = cur.fetchone()
    quien_aprueba = referente(cur, ctx.quien.membership_id)
    if aviso is not None and aviso["estado"] == "guardado":
        cur.execute("""update scheduled_notice
                          set estado = 'omitido', motivo_omision = 'prevision_corregida',
                              resuelto_en = %s
                        where id = %s""", (ctx.ahora, aviso["id"]))
        hechos["aviso_de_la_prevision_corregida"] = {"estado": "retirado_sin_enviar"}
    elif aviso is not None and aviso["estado"] == "enviado" and quien_aprueba is not None:
        sale = sale_a_la_hora(cal, ctx.ahora)
        cur.execute(
            """insert into scheduled_notice (workspace_id, tipo, task_id,
                                             destinatario_membership_id, hechos,
                                             programado_para, dedupe_key, creado_en)
               values (%s, 'correccion_de_prevision', %s, %s, %s, %s, %s, %s) returning id""",
            (ctx.quien.workspace_id, tarea["id"], quien_aprueba["membership_id"],
             json.dumps({**_es_un_aviso_al_referente("correccion_de_prevision"),
                         "tarea": tarea["titulo"], "responsable": ctx.quien.nombre,
                         "prevision_que_no_vale": equivocada["fecha_prevista"].isoformat(),
                         "motivo": "se_anoto_en_la_tarea_equivocada",
                         **hechos["vuelve_a"]}, ensure_ascii=False),
             sale, f"motor:correccion_de_prevision:{correccion_id}", ctx.ahora))
        correccion_aviso = str(cur.fetchone()["id"])
        ctx.avisos_guardados.append(correccion_aviso)
        hechos["correccion_al_referente"] = {"a": quien_aprueba["nombre"],
                                             "estado": GUARDADO_SIN_ENVIAR,
                                             "sale": sale.isoformat()}
        nombrar_efecto(hechos, "correccion_al_referente", AVISO, correccion_aviso)
    if (anterior is not None and quien_aprueba is not None
            and (aviso is None or aviso["estado"] != "enviado")):
        rearmado = _rearmar_aviso_de_la_anterior(ctx, tarea, anterior, correccion_id,
                                                 quien_aprueba)
        if rearmado is not None:
            rearmado_id, hechos["aviso_de_la_prevision_anterior"] = rearmado
            nombrar_efecto(hechos, "aviso_de_la_prevision_anterior", AVISO, rearmado_id)
    return {"hechos": hechos,
            "datos": {"fecha": equivocada["fecha_prevista"].isoformat(),
                      **({"motivo": equivocada["motivo"]} if equivocada["motivo"] else {})}}


def _rearmar_aviso_de_la_anterior(ctx: Contexto, tarea: dict, anterior: dict,
                                  correccion_id: str,
                                  quien_aprueba: dict) -> tuple[str, dict] | None:
    """La corrección vuelve a una previsión anterior cuyo aviso al referente se había retirado
    sin salir (la reemplazó la equivocada): el referente nunca supo de ella, así que su aviso
    se vuelve a guardar, con los hechos de esa previsión, atado a la corrección, que es la
    previsión vigente. Si el aviso de la anterior ya había salido, el referente ya la sabe
    (pendiente de la E2-4)."""
    cur, cal = ctx.cur, ctx.calendario
    cur.execute("""select estado from scheduled_notice
                    where workspace_id = %s and dedupe_key = %s""",
                (ctx.quien.workspace_id, f"motor:nueva_prevision:{anterior['id']}"))
    suyo = cur.fetchone()
    comprometida = anterior["fecha_comprometida"].astimezone(cal.zona).date()
    if suyo is None or suyo["estado"] != "omitido" or anterior["fecha_prevista"] == comprometida:
        return None
    cur.execute("""select t.titulo from dependency d join task t on t.id = d.destino_task_id
                    where d.origen_task_id = %s and t.estado not in ('terminada', 'cancelada')
                    order by t.titulo""", (tarea["id"],))
    sale = sale_a_la_hora(cal, ctx.ahora)
    cur.execute(
        """insert into scheduled_notice (workspace_id, tipo, task_id,
                                         destinatario_membership_id, hechos, programado_para,
                                         dedupe_key, creado_en)
           values (%s, 'nueva_prevision', %s, %s, %s, %s, %s, %s) returning id""",
        (ctx.quien.workspace_id, tarea["id"], quien_aprueba["membership_id"],
         json.dumps({**_es_un_aviso_al_referente("nueva_prevision"), "tarea": tarea["titulo"],
                     "responsable": ctx.quien.nombre,
                     "prevision": anterior["fecha_prevista"].isoformat(),
                     "motivo": anterior["motivo"],
                     "fecha_comprometida": comprometida.isoformat(),
                     ATRASO_SI_SE_CUMPLE: anterior["atraso_dias_habiles"],
                     "dependientes": [r["titulo"] for r in cur.fetchall()]},
                    ensure_ascii=False),
         sale, f"motor:nueva_prevision:{correccion_id}", ctx.ahora))
    aviso_id = str(cur.fetchone()["id"])
    ctx.avisos_guardados.append(aviso_id)
    return aviso_id, {"a": quien_aprueba["nombre"], "estado": GUARDADO_SIN_ENVIAR,
                      "sale": sale.isoformat()}


def _deshacer_bloqueo(ctx: Contexto, tarea: dict) -> dict | None:
    """El bloqueo se resuelve como corrección (`resolver_bloqueo`): la tarea vuelve al estado
    que tenía antes de bloquearse."""
    cur = ctx.cur
    cur.execute("""select id, causa from blocker
                    where task_id = %s and resuelto_en is null and abierto_por = %s
                    order by abierto_en desc limit 1""", (tarea["id"], ctx.quien.membership_id))
    bloqueo = cur.fetchone()
    if bloqueo is None:
        return None
    r = ejecutar(cur, ctx.quien, "resolver_bloqueo",
                 {"bloqueo_id": str(bloqueo["id"]), "resolucion": MOTIVO_DE_LA_CORRECCION},
                 ya_confirmada=True)
    if not r.get("resuelto"):
        return None
    cur.execute("select estado::text estado from task where id = %s", (tarea["id"],))
    return {"hechos": {"vuelve_a": {"estado": cur.fetchone()["estado"]}},
            "datos": {"causa": bloqueo["causa"]}}


FICHAS: Mapping[str, Ficha] = MappingProxyType({f.nombre: f for f in (
    Ficha("anotar_inicio", "anotar que arrancó una tarea",
          necesita=("tarea",), opcional=(),
          comprueba="que sea el responsable y que la tarea esté asignada",
          hace="la pasa a en curso (actualizar_estado)",
          despues="cierra la espera de esa tarea",
          manejar=_anotar_inicio, del_responsable=True,
          estados=frozenset({"asignada"}),
          contesta=(preguntas.ESTADO_DE_LA_TAREA, preguntas.FECHA_DE_LA_TAREA),
          deshacer=_deshacer_inicio,
          es="La persona dice que empezó a trabajar en una tarea. Es sólo el comienzo: no "
             "trae la fecha para la que la termina ni dice que no puede avanzar. Seguir con "
             "una tarea que estaba trabada no es empezarla: es salir del bloqueo."),
    Ficha("anotar_prevision", "anotar para cuándo prevé terminar una tarea, y por qué",
          necesita=("tarea", "fecha"), opcional=("motivo",),
          comprueba="que sea el responsable, que la tarea esté abierta y tenga fecha "
                    "comprometida",
          hace="anota la previsión con el atraso en días hábiles del espacio; la fecha "
               "comprometida no cambia",
          despues="guarda el aviso al referente, salvo que vuelva a la fecha comprometida; "
                  "cierra la espera de esa tarea",
          manejar=_anotar_prevision, del_responsable=True,
          contesta=(preguntas.ESTADO_DE_LA_TAREA, preguntas.FECHA_DE_LA_TAREA),
          deshacer=_deshacer_prevision, algo_cierto=True,
          es="La persona da la fecha para la que espera terminar una tarea, con su porqué o "
             "sin él. Es un atraso (o un adelanto) previsto, no un bloqueo: quien da una fecha "
             "dice cuándo va a terminar, aunque el porqué sea algo que espera, y no dice que "
             "no puede avanzar. Una fecha nueva que reemplaza otra que dio antes es otra "
             "previsión, no una corrección."),
    Ficha("anotar_bloqueo", "anotar que una tarea está trabada y por qué",
          necesita=("tarea",), opcional=("causa",),
          comprueba="que sea el responsable y que la tarea esté abierta",
          hace="sin causa, nada; con causa, registra el bloqueo (registrar_bloqueo)",
          despues="sin causa, pregunta la causa; con causa, pregunta quién lo puede "
                  "destrabar. Ningún aviso al referente (9c)",
          manejar=_anotar_bloqueo, del_responsable=True,
          contesta=("causa_del_bloqueo", preguntas.ESTADO_DE_LA_TAREA,
                    preguntas.FECHA_DE_LA_TAREA),
          deshacer=_deshacer_bloqueo, algo_cierto=True,
          es="La persona dice que no puede avanzar con una tarea: está trabada o parada. Su "
             "causa es lo que le falta o lo que frena el trabajo, si la dice. Explicar por qué "
             "se corre una fecha no es un bloqueo: es el porqué de una previsión."),
    Ficha("anotar_quien_destraba", "anotar quién puede destrabar un bloqueo",
          necesita=(), opcional=("tarea", "quien", "no_sabe", "nadie_mas"),
          comprueba="que haya un bloqueo abierto en una tarea suya",
          hace="anota quién destraba: un integrante, alguien de afuera, que no se sabe o "
               "que le toca a la persona misma",
          despues="cierra la pregunta y la espera; si no se sabe o le toca a la persona "
                  "que escribe, propone salidas, que quedan como tema abierto",
          manejar=_anotar_quien_destraba,
          contesta=(preguntas.QUIEN_DESTRABA, preguntas.ESTADO_DE_LA_TAREA),
          propone=lambda hecho: hecho.get("salidas"),
          es="La persona dice quién puede destrabar un bloqueo (alguien del equipo o de "
             "afuera), que no sabe quién, o que nadie más: le toca a la persona que escribe. "
             "El bloqueo es uno abierto antes o el que anota una jugada anterior del mismo "
             "mensaje. Quién lo destraba es un hecho distinto de la causa, aunque los dos "
             "vengan en la misma frase: cada uno va en su jugada."),
    Ficha("destrabar", "anotar que una tarea trabada ya puede seguir",
          necesita=("tarea",), opcional=(),
          comprueba="que sea el responsable y que la tarea esté bloqueada, con un solo bloqueo "
                    "abierto",
          hace="cierra el bloqueo (resolver_bloqueo): la tarea vuelve al estado que tenía "
               "antes de bloquearse",
          despues="cierra la pregunta de quién lo destraba, lo propuesto para salir del bloqueo "
                  "y sus esperas; la escalera vuelve a seguir la tarea y, si su seguimiento ya "
                  "había empezado, Leda vuelve a pedir el estado el día hábil siguiente",
          manejar=_destrabar, del_responsable=True, estados=frozenset({"bloqueada"}),
          contesta=(preguntas.QUIEN_DESTRABA,), sigue_el_pedido=True,
          es="La persona dice que la causa de un bloqueo ya no está: llegó lo que le faltaba "
             "o se resolvió lo que frenaba el trabajo, y la tarea puede seguir. El bloqueo es "
             "uno abierto antes o el que anota una jugada anterior del mismo mensaje. Es salir "
             "de un bloqueo: no es empezar la tarea, ni dar la fecha para la que la termina, "
             "ni contar cómo viene; si además dice uno de esos hechos, ése es otra jugada."),
    Ficha("informar_avance", "anotar cómo viene una tarea cuando la persona cuenta un avance "
                             "sin un hecho cierto",
          necesita=("tarea",), opcional=("palabras",),
          comprueba="que sea el responsable, que la tarea esté abierta y que Leda le haya "
                    "pedido el estado (una espera abierta)",
          hace="anota el avance con las palabras de la persona, atribuido y auditado; no "
               "cambia el estado ni la fecha",
          despues="la espera sigue abierta y Leda vuelve a pedir el estado el día hábil "
                  "siguiente, sin contarlo como silencio; a la segunda respuesta sin nada "
                  "cierto, pregunta para cuándo. Sin un pedido siguiente (sin vencimiento, o "
                  "ya escaló), lo dice",
          manejar=_informar_avance, del_responsable=True,
          contesta=(preguntas.ESTADO_DE_LA_TAREA,), sigue_el_pedido=True,
          es="La persona cuenta cómo viene una tarea sin un hecho cierto: no dice que la "
             "terminó, ni para cuándo, ni que arrancó, ni que no puede avanzar. Si dice uno de "
             "esos hechos, es la jugada de ese hecho, no ésta."),
    Ficha("consultar_pendientes", "contar qué tareas tiene pendientes",
          necesita=(), opcional=(),
          comprueba="nada", hace="lee sus tareas abiertas (consultar_tareas)",
          despues="nada", manejar=_consultar_pendientes,
          es="La persona pregunta qué tareas tiene pendientes, o cómo están sus tareas. Leda "
             "las lee de la base."),
    Ficha("entregar", "recibir la entrega de una tarea",
          necesita=(), opcional=("tarea",),
          comprueba="nada", hace="nada: todavía no se recibe por chat (9g)",
          despues="sin aviso al administrador", manejar=_entregar, se_ofrece=False,
          es="La persona dice que terminó una tarea. Terminarla no es contar que le falta "
             "poco: eso es un avance."),
    Ficha("pedir_reasignacion", "pasarle una tarea a otra persona",
          necesita=(), opcional=("tarea", "a"),
          comprueba="nada", hace="nada: cambiar el responsable no es por chat (9g)",
          despues="dice quién lo decide y ofrece una nueva previsión, que queda como tema "
                  "abierto; sin aviso al administrador",
          manejar=_pedir_reasignacion, se_ofrece=False,
          propone=lambda hecho: [hecho["alternativa"]] if hecho.get("alternativa") else None,
          es="La persona pide que una tarea suya pase a otra persona."),
    # Las situaciones generales (`situaciones.py`): valen igual para todas las fichas.
    Ficha("elegir", "elegir una de las opciones de la pregunta abierta",
          necesita=("opcion",), opcional=(),
          comprueba="que la opción sea de una pregunta suya; si la pregunta ya se cerró, no "
                    "hace nada y dice con qué se cerró",
          hace="cierra la pregunta con esa opción y hace la jugada que esperaba, con la "
               "opción como dato y las comprobaciones de su ficha",
          despues="vuelve la pregunta que quedó para después, si hay",
          manejar=situaciones.elegir, se_ofrece=False,
          es="La persona elige una de las opciones de la pregunta abierta de Leda (o una de "
             "las jugadas que Leda le propuso), tocando o escribiendo. Sin una pregunta abierta "
             "con opciones, no es esta jugada."),
    Ficha("corregir", "corregir algo ya anotado que era de otra tarea o que no pasó",
          necesita=("corrige", "tarea"), opcional=("tarea_correcta",),
          comprueba="que sea el responsable y que eso haya quedado anotado en esa tarea en "
                    "sus últimos turnos",
          hace="agrega un hecho de corrección: la tarea vuelve a como estaba y, si la dice, "
               "el hecho va a la tarea correcta; nada se borra (9f)",
          despues="un aviso que no salió se retira; uno que ya salió lleva una corrección "
                  "al referente",
          manejar=situaciones.corregir, del_responsable=True, se_ofrece=False,
          es="La persona dice que algo que ya quedó anotado estaba mal: era de otra tarea o no "
             "pasó. Dar un hecho nuevo que reemplaza al de antes no es corregir: es la jugada "
             "de ese hecho."),
    Ficha("cancelar", "dejar sin efecto la pregunta abierta",
          necesita=(), opcional=(),
          comprueba="que haya una pregunta abierta y que se pueda dejar (la de quién destraba "
                    "espera respuesta, 9c)",
          hace="la cierra sin anotar nada",
          despues="no se vuelve a preguntar; vuelve la que quedó para después, si hay",
          manejar=situaciones.cancelar, se_ofrece=False,
          es="La persona deja sin efecto la pregunta abierta de Leda: no la va a contestar. "
             "Dejar sin efecto algo que la persona dijo antes no es cancelar: es corregirlo o "
             "dar el hecho nuevo."),
    Ficha("dejar_para_despues", "dejar la pregunta abierta para más tarde",
          necesita=(), opcional=(),
          comprueba="que haya una pregunta abierta",
          hace="la deja para después, sin cerrarla",
          despues="vuelve en un mensaje siguiente, cuando no haya otra abierta",
          manejar=situaciones.dejar_para_despues, se_ofrece=False,
          es="La persona deja la pregunta abierta de Leda para más tarde, sin contestarla ni "
             "dejarla sin efecto."),
)})


def _manejador(ficha: Ficha) -> Manejador:
    return lambda ctx, jugada: correr(ficha, ctx, jugada)


# La lista cerrada: nombre de la jugada → su manejador.
JUGADAS: Mapping[str, Manejador] = MappingProxyType(
    {nombre: _manejador(ficha) for nombre, ficha in FICHAS.items()})


def lo_que_puede_hacer(jugadas: Mapping[str, Manejador]) -> list[str]:
    """Lo que Leda puede hacer por chat, para el hecho de algo fuera de la lista."""
    return [FICHAS[n].para_que for n in sorted(jugadas) if n in FICHAS and FICHAS[n].se_ofrece]


# Para las situaciones generales (`situaciones.py`).
vacio = _vacio
tarea_hecho = _tarea
