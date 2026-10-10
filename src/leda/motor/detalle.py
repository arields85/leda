"""El resumen para cualquiera, el detalle a pedido (decisión 33 del usuario, 2026-10-09).

`odd/tasks/fase-c.md`, decisión 33; ADR 0019, decisión 7b (quién ve el detalle, igual); ADR 0018,
decisión 1 (la IA elige la jugada; la cocina decide si vale); constitución §7 (antes de prometer un
envío, Leda comprueba que el destinatario esté conectado) y §12 (auditoría); conversación 45. La
regla la hace cumplir la cocina (`herramientas`: `pedir_detalle_de_tarea`,
`decidir_detalle_de_tarea` y `dejar_de_compartir_tarea`) y la base (`pedido_de_detalle`,
`tarea_compartida`, `puede_ver_tarea`; migración 0050); acá está la conversación.

**Dos niveles.** El resumen de una tarea (qué tarea, de quién, para cuándo, cómo quedó) lo ve
cualquiera del equipo; el detalle (la página: fotos, archivos, correcciones pedidas), sólo quienes
tienen que ver con ella. Leda nunca contesta "no la podés ver" ni deja a la persona sin un próximo
paso: cuando pide el enlace de una tarea que no ve (`enlace.pedir_enlace`), le da el resumen y,
con él, lo que puede hacer (`ofrecer`): pedirle el detalle al encargado del sector de la tarea (el
referente de su área), que Leda le ofrece como una propuesta, un tema abierto como cualquier otro.
Sin encargado, o si Leda no le puede escribir, no se ofrece, y los hechos dicen por qué.

**Pedirlo** (`pedir`, la jugada `pedir_el_detalle`): con lo que Leda ofreció, o nombrando la
tarea. La cocina anota el pedido y Leda le pregunta al encargado, como Leda, terminado el margen
para corregir (`PEDIDO_DEL_DETALLE`), con dos botones (`TipoDeAviso.opciones`). Si ya la ve, el
enlace; si ya lo pidió, lo dice.

**El encargado decide** (`contestar`, la jugada `contestar_el_pedido_del_detalle`): la tarea está
en su lista como un pedido que espera su decisión (`para_contestar`). Si la comparte, queda
compartida con quien la pidió, auditado y revocable, y la base la cuenta para ver la página; si
no, nada cambia. Quien la pidió se entera de cómo terminó (decisión 39: nunca un tema abierto sin
que todos sepan cómo se cerró; `COMO_TERMINO_EL_PEDIDO_DEL_DETALLE`), con el enlace si se la
compartió, que la base vuelve a comprobar al mandar.

**Lo que dejaron la revisión y la impugnación** (2026-10-09; derivado por el coordinador de las
decisiones del usuario, sin preguntar):

- **La oferta es opcional** ("si lo necesitás, le pregunto": `preguntas.OPCIONAL`): no se repite a
  las 4 horas ni vuelve después de un cambio de tema; si la persona no la contesta, es un no
  (constitución §8, "liviana en todo lo demás"). Una regla de las preguntas, no de esta jugada.
- **El pedido sigue al encargado de ahora** (como la revisión sigue a quien aprueba, decisiones 16
  y 43): la pregunta va a quien es el encargado al salir (`al_encargado_de_ahora`), lo ve en su
  lista y lo decide él; un encargado anterior no decide nada, ni que sí ni que no (lo comprueban
  la cocina y la base, migración 0051), y su botón viejo se lo dice como cualquier botón de
  una tarea que ya no le corresponde.
- **Si el encargado no contesta** (`seguir_los_pedidos`; la regla de la decisión 26, la misma que
  los pases, `una_vez_y_termina`): la pregunta otra vez, una sola, el día hábil siguiente; si
  sigue sin contestar, el pedido termina sin respuesta (la cocina, `terminar_pedido_de_detalle`)
  y se enteran quien lo pidió (que puede volver a pedirlo) y el encargado, que ya no hace falta
  que conteste (decisión 39).
- **Un encargado sin Leda conectada** (el mecanismo de la decisión 37): no se ofrece ni se pide,
  los hechos dicen la verdad (a quién no se le puede escribir) y el administrador recibe el
  aviso, de verdad, para que lo conecte (`persecucion.avisar_para_que_lo_conecte`).
"""

from __future__ import annotations

import uuid
from typing import Any

from ..autoridad import encargado_de_la_tarea
from ..herramientas import ejecutar

from datetime import timedelta

from ..herramientas import terminar_pedido_de_detalle

from . import preguntas
from .ancla import candado
from .avisos import (COMO_TERMINO_EL_PEDIDO_DEL_DETALLE, PEDIDO_DEL_DETALLE,
                     RECORDATORIO_DEL_PEDIDO_DEL_DETALLE, ausente, guardar, integrante)
from .fichas import AVISO, LLEGA, Contexto, juntar, nombrar_efecto, nombrar_pregunta, vacio
from .margen import sale_con_margen
from .persecucion import (SE_LE_AVISO_AL_ADMINISTRADOR, SIN_TELEGRAM, alcanzable,
                          avisar_para_que_lo_conecte)
from .tiempo import sale
from .una_vez_y_termina import toca_repetir, vencio

PEDIR_EL_DETALLE = "pedir_el_detalle"
CONTESTAR = "contestar_el_pedido_del_detalle"
# Los resultados y los motivos (sus significados, en `hechos.py`).
DETALLE_PEDIDO = "detalle_pedido"
YA_LO_PIDIO = "ya_lo_pidio"
SIN_ENCARGADO = "sin_encargado_del_sector"
NO_HAY_UN_PEDIDO = "no_hay_un_pedido_del_detalle"
EL_PEDIDO_YA_NO_ESPERA = "el_pedido_ya_no_espera"
# Los botones de la pregunta al encargado: cada uno corre `contestar_el_pedido_del_detalle` con lo
# que dice (`acepta`) y el pedido que contesta.
BOTONES = (("Compartirla", True), ("No compartirla", False))
_ESPERA = "esperando_decision"


# --- Lo que Leda ofrece con el resumen ----------------------------------------------------------

def ofrecer(ctx: Contexto, task_id: str, hecho: dict[str, Any]) -> None:
    """Lo que se suma al resumen de una tarea que la persona no ve: qué sector ve el detalle y, si
    se puede, a quién se lo puede pedir, como una propuesta (un tema abierto). Si ya se lo pidió,
    a quién; sin encargado, o si Leda no le puede escribir, por qué no se ofrece."""
    cur, yo = ctx.cur, ctx.quien.membership_id
    cur.execute("""select a.nombre from task t join area a on a.id = t.area_id
                    where t.id = %s""", (task_id,))
    hecho["el_detalle_lo_ve"] = cur.fetchone()["nombre"]
    encargado = encargado_de_la_tarea(cur, task_id)
    if encargado is None:
        hecho[SIN_ENCARGADO] = True
        return
    if _pedido_abierto(cur, task_id, yo) is not None:
        hecho["ya_se_lo_pidio_a"] = integrante(cur, encargado)["nombre"]
        return
    quien, motivo = alcanzable(cur, encargado)
    if motivo is not None:
        hecho.update(_sin_leda_conectada(ctx, quien, motivo, task_id))
        return
    hecho["se_lo_puede_pedir_a"] = quien["nombre"]
    # Una oferta opcional: no se repite ni vuelve, y sin respuesta es un no (`preguntas.OPCIONAL`).
    ahora, pregunta_id = preguntas.abrir_con_id(
        ctx, preguntas.PROPUESTA, task_id,
        jugada={"nombre": "pedir_enlace", "propone": [PEDIR_EL_DETALLE],
                preguntas.OPCIONAL: True})
    nombrar_pregunta(hecho, "pregunta" if ahora else "pregunta_para_despues",
                     preguntas.PROPUESTA, pregunta_id)


def _sin_leda_conectada(ctx: Contexto, quien: dict | None, motivo: str,
                        task_id: str) -> dict[str, Any]:
    """El encargado no tiene Leda conectada: la verdad (a quién no se le puede escribir y por
    qué) y, si le falta el chat, el aviso al administrador para que lo conecte, de verdad, por su
    canal (el mecanismo de la decisión 37). Nunca se promete un mensaje que no sale (§7)."""
    nombre = quien["nombre"] if quien else None
    hecho: dict[str, Any] = {"no_se_le_puede_escribir_a": {"a": nombre, "motivo": motivo}}
    if motivo == SIN_TELEGRAM and nombre:
        titulo = preguntas.tarea_dicha(ctx, task_id).get("titulo", "")
        hecho[SE_LE_AVISO_AL_ADMINISTRADOR] = avisar_para_que_lo_conecte(
            ctx, nombre, f"para que decida si le comparte el detalle de la tarea «{titulo}»")
    return hecho


def _pedido_abierto(cur, task_id: str, persona: str) -> dict | None:
    cur.execute("""select * from pedido_de_detalle
                    where task_id = %s and pedido_por_membership_id = %s and estado = %s""",
                (task_id, persona, _ESPERA))
    return cur.fetchone()


def _la_propuesta(cur, persona: str) -> dict | None:
    """Lo que Leda le ofreció a la persona y sigue abierto: pedir el detalle de una tarea, la más
    nueva."""
    cur.execute("""select * from conversation_question
                    where membership_id = %s and tipo = %s and cerrada_en is null
                      and task_id is not null and jugada -> 'propone' ? %s
                    order by abierta_en desc limit 1""",
                (persona, preguntas.PROPUESTA, PEDIR_EL_DETALLE))
    return cur.fetchone()


def _cerrar_la_propuesta(ctx: Contexto, task_id: str) -> None:
    """Lo que Leda le ofreció sobre esa tarea quedó contestado."""
    ctx.cur.execute("""select id from conversation_question
                        where membership_id = %s and tipo = %s and task_id = %s
                          and cerrada_en is null and jugada -> 'propone' ? %s""",
                    (ctx.quien.membership_id, preguntas.PROPUESTA, task_id, PEDIR_EL_DETALLE))
    for fila in ctx.cur.fetchall():
        preguntas.cerrar(ctx, str(fila["id"]), "respondida",
                         {"jugada": PEDIR_EL_DETALLE, "tarea": task_id})


# --- Pedirlo ----------------------------------------------------------------------------------

def pedir(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    """La persona acepta que Leda le pida el detalle al encargado del sector de la tarea: la de
    su lista, la que nombra (`como_la_nombra`) o la de lo que Leda le ofreció."""
    from . import enlace                # enlace importa este módulo al ofrecer
    cur, yo = ctx.cur, ctx.quien.membership_id
    if tarea is not None:
        task_id = tarea["id"]
    elif not vacio(datos.get("como_la_nombra")):
        una = enlace.la_que_nombra(ctx, str(datos["como_la_nombra"]))
        if "resultado" in una:
            return una
        task_id = una["id"]
    else:
        propuesta = _la_propuesta(cur, yo)
        if propuesta is None:
            return {"resultado": "falta_dato", "falta": ["tarea"]}
        task_id = str(propuesta["task_id"])
    if enlace.puede_verla(cur, yo, task_id):
        # Ya la ve (la tiene, la revisa, se la compartieron): el enlace, como a cualquiera.
        _cerrar_la_propuesta(ctx, task_id)
        return enlace.pedir_enlace(ctx, {}, {"id": task_id})
    hecho: dict[str, Any] = {"tarea": preguntas.tarea_dicha(ctx, task_id)}
    encargado = encargado_de_la_tarea(cur, task_id)
    if encargado is None:
        return {**hecho, "resultado": "no_se_puede", "motivo": SIN_ENCARGADO}
    quien, motivo = alcanzable(cur, encargado)
    if motivo is not None:
        # Nunca se promete un mensaje que no sale (constitución §7).
        return {**hecho, "resultado": "no_se_puede", "motivo": motivo,
                **_sin_leda_conectada(ctx, quien, motivo, task_id)}
    r = ejecutar(cur, ctx.quien, "pedir_detalle_de_tarea",
                 {"tarea_id": task_id, "at": ctx.ahora.isoformat()}, ya_confirmada=True)
    if r.get("error") == YA_LO_PIDIO:
        return {**hecho, "resultado": "no_se_puede", "motivo": YA_LO_PIDIO,
                "ya_se_lo_pidio_a": quien["nombre"]}
    if "error" in r:
        return {**hecho, "resultado": "no_se_puede", "motivo": r["error"]}
    _cerrar_la_propuesta(ctx, task_id)
    pedido = _el_pedido(cur, r["pedido_id"])
    aviso_id, sale = _guardar(ctx, pedido, PEDIDO_DEL_DETALLE, encargado,
                              hechos_de_la_pregunta(pedido, ctx.calendario.zona), "")
    hecho.update({"resultado": DETALLE_PEDIDO,
                  "le_pregunta_a": {"a": quien["nombre"], LLEGA: sale.isoformat()}})
    nombrar_efecto(hecho, "le_pregunta_a", AVISO, aviso_id)
    return hecho


def _el_pedido(cur, pedido_id: str) -> dict:
    """Un pedido con los nombres de quién lo pidió, quién tiene la tarea y quién lo decidió (o,
    mientras espera, a quién se le preguntó al pedirlo)."""
    cur.execute(
        """select p.*, t.titulo, t.fecha_objetivo, pide.nombre pidio, tiene.nombre la_tiene,
                  decide.nombre decide
             from pedido_de_detalle p
             join task t on t.id = p.task_id
             join integrante pide on pide.membership_id = p.pedido_por_membership_id
             join integrante tiene on tiene.membership_id = t.responsable_membership_id
             join integrante decide
               on decide.membership_id = coalesce(p.decidido_por_membership_id,
                                                  p.decide_membership_id)
            where p.id = %s""", (str(pedido_id),))
    pedido = dict(cur.fetchone())
    for clave in ("id", "task_id", "pedido_por_membership_id", "decide_membership_id"):
        pedido[clave] = str(pedido[clave])
    return pedido


def hechos_de_la_pregunta(pedido: dict, zona) -> dict[str, Any]:
    """Lo que lleva la pregunta al encargado: quién pide ver el detalle, de quién es la tarea y
    cuándo vence."""
    hechos: dict[str, Any] = {"necesita_respuesta": True,
                              "pregunta": preguntas.COMPARTIR_EL_DETALLE,
                              "pide_ver_el_detalle": pedido["pidio"],
                              "la_tiene": pedido["la_tiene"]}
    if pedido["fecha_objetivo"] is not None:
        hechos["vence"] = pedido["fecha_objetivo"].astimezone(zona).date().isoformat()
    return hechos


def _guardar(ctx: Contexto, pedido: dict, tipo: str, destinatario: str, hechos: dict,
             clave: str) -> tuple[str, Any]:
    """Un aviso del pedido, terminado el margen para corregir: lo causa lo que dijo otra
    persona."""
    sale = sale_con_margen(ctx.cur, ctx.calendario, ctx.quien.workspace_id, ctx.ahora)
    aviso_id, _ = guardar(
        ctx.cur, ctx.quien.workspace_id, tipo, task_id=pedido["task_id"],
        destinatario=destinatario, hechos={"aviso": tipo, "tarea": pedido["titulo"], **hechos},
        programado_para=sale, clave=f"motor:{tipo}:{pedido['task_id']}:d{pedido['id']}{clave}",
        ahora=ctx.ahora)
    ctx.avisos_guardados.append(aviso_id)
    return aviso_id, sale


# --- Lo que ve el encargado ---------------------------------------------------------------------

def para_contestar(cur, membership_id: str, desde: int) -> tuple[dict[str, Any], ...]:
    """Las tareas cuyo detalle alguien pidió ver y esperan que quien escribe, el encargado de su
    sector ahora (el pedido sigue al encargado de ahora), decida si se lo comparte
    (`espera_que_decida_si_la_comparte`), con su alias (siguiendo los anteriores, desde `desde`),
    quién la tiene y quiénes lo pidieron. No son tareas suyas."""
    cur.execute(
        """select t.id, t.titulo, t.estado::text estado, t.fecha_objetivo,
                  tiene.nombre la_tiene,
                  array_agg(pide.nombre order by p.pedido_en, p.id) piden
             from pedido_de_detalle p
             join task t on t.id = p.task_id
             join area a on a.id = t.area_id
             join integrante tiene on tiene.membership_id = t.responsable_membership_id
             join integrante pide on pide.membership_id = p.pedido_por_membership_id
            where p.estado = %s and a.referente_membership_id = %s
            group by t.id, t.titulo, t.estado, t.fecha_objetivo, tiene.nombre
            order by t.fecha_objetivo nulls last, t.titulo""", (_ESPERA, membership_id))
    return tuple(
        {"alias": f"T{i}", "id": str(f["id"]), "titulo": f["titulo"], "estado": f["estado"],
         "fecha_objetivo": f["fecha_objetivo"].isoformat() if f["fecha_objetivo"] else None,
         "la_tiene": f["la_tiene"], "espera_que_decida_si_la_comparte": True,
         "pide_ver_el_detalle": list(f["piden"])}
        for i, f in enumerate(cur.fetchall(), desde + 1))


# --- Contestarlo: el encargado ------------------------------------------------------------------

def contestar(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    """El encargado dice si comparte el detalle: el del botón que tocó (su pedido) o, escrito, el
    de la tarea que nombra o el único que espera su decisión. La cocina lo anota y, si la
    comparte, queda compartida; quien la pidió se entera."""
    cur, yo = ctx.cur, ctx.quien.membership_id
    if tarea is None:
        if len(ctx.para_compartir) > 1:
            return {"resultado": "falta_dato", "falta": ["tarea"]}
        tarea = ctx.para_compartir[0] if ctx.para_compartir else None
    if tarea is None or not any(t["id"] == tarea["id"] for t in ctx.para_compartir):
        # Un encargado anterior no la tiene en su lista: no decide nada (su botón viejo lo dice
        # por la regla de todo botón de una tarea que ya no le corresponde, `situaciones`).
        return {"resultado": "no_se_puede", "motivo": NO_HAY_UN_PEDIDO,
                **({"tarea": preguntas.tarea_dicha(ctx, tarea["id"])} if tarea else {})}
    acepta = datos.get("acepta")
    dicha = preguntas.tarea_dicha(ctx, tarea["id"])
    if not isinstance(acepta, bool):
        return {"resultado": "falta_dato", "falta": ["acepta"], "tarea": dicha}
    # El pedido del botón tocado, si lo trae (un identificador que no es tal no nombra ninguno).
    del_boton = datos.get("pedido")
    if del_boton is not None:
        try:
            del_boton = str(uuid.UUID(str(del_boton)))
        except ValueError:
            return {"resultado": "no_se_puede", "motivo": NO_HAY_UN_PEDIDO, "tarea": dicha}
    cur.execute("""select id from pedido_de_detalle
                    where task_id = %s and estado = %s
                      and (%s::uuid is null or id = %s::uuid)
                    order by pedido_en, id""",
                (tarea["id"], _ESPERA, del_boton, del_boton))
    abiertos = [str(f["id"]) for f in cur.fetchall()]
    if not abiertos:
        # El botón de un pedido que ya se decidió: no hace nada y lo dice.
        return {"resultado": "no_se_puede", "motivo": NO_HAY_UN_PEDIDO, "tarea": dicha}
    por_que = None if vacio(datos.get("por_que")) else str(datos["por_que"]).strip()
    hecho: dict[str, Any] = {"resultado": "anotado", "tarea": dicha, "la_compartio": acepta}
    avisados: list[str] = []
    for pedido_id in abiertos:
        r = ejecutar(cur, ctx.quien, "decidir_detalle_de_tarea",
                     {"pedido_id": pedido_id, "comparte": acepta, "at": ctx.ahora.isoformat(),
                      **({"motivo": por_que} if por_que else {})}, ya_confirmada=True)
        if "error" in r:
            continue
        pedido = _el_pedido(cur, pedido_id)
        _cerrar_las_preguntas(cur, pedido, ctx.ahora)
        termino = {"necesita_respuesta": False, "la_compartio": acepta,
                   "lo_decidio": pedido["decide"], **({"por_que": por_que} if por_que else {})}
        aviso_id, sale = _guardar(ctx, pedido, COMO_TERMINO_EL_PEDIDO_DEL_DETALLE,
                                  pedido["pedido_por_membership_id"], termino, ":termino")
        if not avisados:
            nombrar_efecto(hecho, "aviso_a_quien_lo_pidio", AVISO, aviso_id)
            hecho["aviso_a_quien_lo_pidio"] = {"a": pedido["pidio"], LLEGA: sale.isoformat()}
        avisados.append(pedido["pidio"])
    if len(avisados) > 1:
        # Varias personas pidieron la misma tarea: la respuesta escrita vale para todas.
        juntar(hecho, {"aviso_a_quienes_lo_pidieron": {
            "a": avisados, LLEGA: hecho["aviso_a_quien_lo_pidio"][LLEGA]}})
    return hecho


def _cerrar_las_preguntas(cur, pedido: dict, ahora) -> None:
    """La pregunta del pedido, con sus botones, deja de esperar: ya se decidió (un botón viejo,
    igual, no hace nada y lo dice: `contestar`)."""
    cur.execute("""update conversation_question
                      set cerrada_en = %s, cierre = 'sin_efecto', cierre_detalle = %s
                    where task_id = %s and tipo = %s and cerrada_en is null
                      and jugada ->> 'pedido' = %s""",
                (ahora, preguntas.json_de({"tarea": pedido["task_id"],
                                           "el_pedido_ya_no_espera": True}),
                 pedido["task_id"], preguntas.COMPARTIR_EL_DETALLE, pedido["id"]))


# --- Lo que un aviso del pedido necesita al salir -------------------------------------------------

def al_encargado_de_ahora(m, aviso) -> str | None:
    """La pregunta del pedido (y su repetición) va a quien es el encargado del sector de la
    tarea al salir: el pedido sigue al encargado de ahora (decisiones 16 y 43)."""
    return encargado_de_la_tarea(m.cur, aviso["task_id"]) if aviso["task_id"] else None


def vigencia(m, aviso) -> tuple[str | None, dict[str, Any]]:
    """La pregunta al encargado (y su repetición) sale mientras el pedido espere su decisión y
    vaya al encargado de ahora; cómo terminó, siempre."""
    from .avisos import de_la_clave       # avisos importa este módulo al salir
    if aviso["tipo"] == COMO_TERMINO_EL_PEDIDO_DEL_DETALLE:
        return None, dict(aviso["hechos"])
    m.cur.execute("select estado from pedido_de_detalle where id = %s", (de_la_clave(aviso),))
    pedido = m.cur.fetchone()
    if pedido is None:
        return "tarea_inexistente", {}
    if pedido["estado"] != _ESPERA:
        return EL_PEDIDO_YA_NO_ESPERA, {}
    if str(aviso["destinatario_membership_id"]) != al_encargado_de_ahora(m, aviso):
        return "sin_encargado_del_sector", {}
    return None, dict(aviso["hechos"])


# --- Si el encargado no contesta (la regla de la decisión 26) --------------------------------------

def seguir_los_pedidos(m) -> list[str]:
    """Lo que toca de cada pedido del detalle que espera una decisión que no llega (la regla de
    la decisión 26, la misma que los pases: `una_vez_y_termina`): la pregunta otra vez, una sola,
    el día hábil siguiente de haber salido, al encargado de ahora; y, al día hábil siguiente de la
    repetición, a la hora en que Leda escribe, el fin sin respuesta (la cocina,
    `terminar_pedido_de_detalle`), del que se enteran quien lo pidió y el encargado. Corre en la
    escalera (`escalera.correr_escalera`). Los tipos de lo que guardó."""
    cur = m.cur
    cur.execute("select id from pedido_de_detalle where estado = %s order by pedido_en, id",
                (_ESPERA,))
    guardados: list[str] = []
    for fila in cur.fetchall():
        pedido = _el_pedido(cur, str(fila["id"]))
        if not candado(cur, pedido["task_id"], esperar=False):
            continue                    # un turno la tiene tomada: la vuelta siguiente
        encargado = encargado_de_la_tarea(cur, pedido["task_id"])
        pregunta = _el_aviso(cur, PEDIDO_DEL_DETALLE, pedido)
        otra_vez = _el_aviso(cur, RECORDATORIO_DEL_PEDIDO_DEL_DETALLE, pedido)
        pausado = encargado is None or ausente(cur, encargado, m.hoy)
        if vencio(m, otra_vez, pausado=pausado) and terminar_pedido_de_detalle(
                cur, pedido["id"], m.ahora) is not None:
            _sin_respuesta(m, pedido, otra_vez)
            guardados.append(COMO_TERMINO_EL_PEDIDO_DEL_DETALLE)
            continue
        if toca_repetir(m, pregunta, otra_vez, pausado=pausado):
            _repetir(m, pedido, encargado, pregunta)
            guardados.append(RECORDATORIO_DEL_PEDIDO_DEL_DETALLE)
    return guardados


def _el_aviso(cur, tipo: str, pedido: dict) -> dict | None:
    """Un aviso del pedido por su clave (la de `_guardar`)."""
    cur.execute("select * from scheduled_notice where dedupe_key = %s",
                (f"motor:{tipo}:{pedido['task_id']}:d{pedido['id']}",))
    return cur.fetchone()


def _repetir(m, pedido: dict, encargado: str, pregunta: dict) -> None:
    """La pregunta otra vez, con lo mismo que la primera, cuándo se le preguntó y qué pasa si
    sigue sin contestar: el día hábil siguiente, el pedido termina sin compartir nada."""
    hechos = {"aviso": RECORDATORIO_DEL_PEDIDO_DEL_DETALLE, "tarea": pedido["titulo"],
              **hechos_de_la_pregunta(pedido, m.cal.zona),
              "se_lo_pregunto_el": m.fecha(pregunta["resuelto_en"]).isoformat(),
              "si_sigue_sin_contestar": {
                  "no_se_comparte": True,
                  "fecha": m.cal.proximo_habil(m.hoy + timedelta(days=1)).isoformat()}}
    guardar(m.cur, m.workspace_id, RECORDATORIO_DEL_PEDIDO_DEL_DETALLE, task_id=pedido["task_id"],
            destinatario=encargado, hechos=hechos, programado_para=sale(m.cal, m.ahora),
            clave=f"motor:{RECORDATORIO_DEL_PEDIDO_DEL_DETALLE}:{pedido['task_id']}"
                  f":d{pedido['id']}", ahora=m.ahora)


def _sin_respuesta(m, pedido: dict, otra_vez: dict) -> None:
    """El fin que da el sistema: a quien lo pidió, que no hubo respuesta (quién no contestó) y que
    puede volver a pedirlo; a quien se le preguntó la última vez, que ya no hace falta que
    conteste (decisión 39). Las preguntas del pedido, con sus botones, dejan de esperar.
    Información, a la hora en que Leda escribe."""
    _cerrar_las_preguntas(m.cur, pedido, m.ahora)
    preguntado = str(otra_vez["destinatario_membership_id"])
    persona = integrante(m.cur, preguntado)
    base = {"aviso": COMO_TERMINO_EL_PEDIDO_DEL_DETALLE, "tarea": pedido["titulo"],
            "necesita_respuesta": False, "sin_respuesta": True, "la_compartio": False}
    for destinatario, clave, propio in (
            (pedido["pedido_por_membership_id"], ":termino",
             {"no_contesto": persona["nombre"] if persona else None,
              "puede_volver_a_pedirlo": True}),
            (preguntado, ":a_quien_se_le_preguntaba",
             {"ya_no_espera_su_respuesta": True, "pidio": pedido["pidio"]})):
        guardar(m.cur, m.workspace_id, COMO_TERMINO_EL_PEDIDO_DEL_DETALLE,
                task_id=pedido["task_id"], destinatario=destinatario,
                hechos={**base, **propio}, programado_para=sale(m.cal, m.ahora),
                clave=f"motor:{COMO_TERMINO_EL_PEDIDO_DEL_DETALLE}:{pedido['task_id']}"
                      f":d{pedido['id']}{clave}", ahora=m.ahora)


def opciones(m, aviso) -> tuple[str, dict[str, Any], list[tuple[str, dict[str, Any]]]]:
    """La decisión que ofrece la pregunta al encargado al salir, con sus dos botones."""
    from .avisos import de_la_clave
    task_id, pedido_id = str(aviso["task_id"]), de_la_clave(aviso)
    return preguntas.COMPARTIR_EL_DETALLE, {"nombre": CONTESTAR, "del_aviso": str(aviso["id"]),
                                            "pedido": pedido_id}, [
        (etiqueta, {"tarea": task_id, "jugada": CONTESTAR,
                    "datos": {"acepta": acepta, "pedido": pedido_id}})
        for etiqueta, acepta in BOTONES]
