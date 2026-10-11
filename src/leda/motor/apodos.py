"""Los apodos: Leda reconoce a una persona del equipo cuando la nombran por un apodo y, si no la
reconoce, pregunta quién es (ADR 0020; conversación 47).

En un equipo real la gente se nombra como se habla ("el Tano", "Pato"). Un apodo es del espacio
(decisión 6): lo que enseñó una persona lo entiende Leda con todo el equipo de ese espacio, y
nunca en otro (la tabla `apodo`, con RLS forzado, migración 0055). Una persona puede tener varios
(decisión 2) y un apodo puede ser de dos personas (decisión 3).

**Se reconoce en un solo lugar** (`fichas.integrantes_que_coinciden`, que usan todas las jugadas
que nombran a alguien): los integrantes cuyo nombre tiene, como palabras enteras, todas las
palabras de lo dicho, y los que tienen un apodo vigente con todas esas palabras. Se compara con
las mismas palabras que los nombres (`fichas.palabras`: sin mayúsculas ni acentos), así "el tano"
y "Tano" son el mismo apodo "el tano", y nada de lo dicho actúa como comodín.

**Si no reconoce a nadie, pregunta quién es** (decisión 1; `quien_es`): nada se anota de lo que
nombraba a esa persona; lo pedido queda guardado en la pregunta (`QUIEN_ES`), una pregunta más de
la conversación, con su lugar entre las pendientes (un tema a la vez). Si la jugada contestaba otra
pregunta (quién lo destraba), la de quién es va antes: precisa esa respuesta. La persona contesta
con un nombre (`decir_quien_es`, la jugada de la respuesta) y Leda confirma con nombre y apellido
(`CONFIRMAR_QUIEN_ES`, con el botón Confirmar o escrito, con la guarda de la decisión 2 del ADR
0018: lo último que vio, en un mensaje anterior). Con la confirmación de esa persona, nunca de la
IA (constitución §5), aprende el apodo (`aprender`) y hace lo que se le había pedido como si lo
hubieran nombrado por su nombre (`_seguir`): la misma jugada, por el manejador de la lista
cerrada, con lo que dijo la persona y la persona ya reconocida. Si el nombre que da no es de
nadie, lo dice y sigue preguntando: nunca inventa una identidad (§4). Si dice que no es del
equipo, la jugada sigue con alguien de afuera, sin aprender nada; eso lo contesta la persona a la
pregunta, en un mensaje posterior, y nunca lo decide la IA leyendo el mismo mensaje que la nombró
(decisión 65 del usuario, 2026-10-11: Leda pregunta siempre).

**Un apodo de dos personas se aclara con nombre y apellido** (decisión 3; `CUAL_DE_ESAS_PERSONAS`):
un botón por persona (elegir entre opciones es un uso válido de los botones), y escribirlo vale
igual; Leda nunca elige. Elegir con nombre y apellido es la confirmación: si era la respuesta a
quién es, el apodo se aprende para la elegida; si era un apodo ya aprendido de dos, ninguno cambia.

**Qué jugadas preguntan** (el alcance, decidido con el ADR): las que nombran a una persona para
hacer algo con ella y hoy, sin reconocerla, terminaban sin salida (`persona_desconocida`): a quién
se le pasa una tarea (`pase.pedir`) y de quién es el trabajo que se aprueba, se devuelve o se mira
(`aprobacion._la_tarea`); y quién destraba un bloqueo y a quién le toca (`fichas._anotar_quien_
destraba`, `persecucion.decir_que_no_le_toca`), que sin reconocerla la anotaban como alguien de
afuera: ahora es de afuera sólo si la persona lo dice. Las que nombran a alguien que la
conversación ya tiene (a quién no escribirle, a quién se lo pide la persona trabada) lo reconocen
también por su apodo, pero un nombre desconocido sigue como antes: preguntar quién es no cambia lo
que hacen.

**El apodo sirve para entender, nunca para hablar** (decisión 5): lo que se reconoce es el
integrante, con su nombre; los hechos que llegan a la IA lo nombran por su nombre, y lo que dijo la
persona va como eso, lo que dijo (`como_lo_nombro`). **Y no concede nada** (decisión 7): ninguna
regla de autoridad lo lee: quién puede pedir qué lo sigue decidiendo cada jugada con la persona ya
reconocida.

**Cada apodo aprendido queda auditado** (decisión 8; `aprender`): en `apodo`, con quién lo enseñó,
cuándo y por qué canal, y en `audit_log`.

**Decir de quién es un apodo, sin que Leda lo pregunte** (decisión 67 del usuario, 2026-10-11;
`_de_quien_es_el_apodo`): "no, el flaco es Marcos". Si el apodo ya es de otra persona, Leda no
cambia nada sin preguntar si a las dos les dicen así (`A_QUIENES`, con dos botones): "A los dos"
le enseña el apodo también a la nueva (desde entonces da la duda, como dos nombres iguales);
"Sólo a" la nueva deja de usar el de las otras, con quién y cuándo (`dejar_de_usar`, auditado), y
se lo enseña a ella. Escribirlo vale igual que el botón. Si el apodo no es de nadie, es como
contestar quién es: Leda confirma con nombre y apellido antes de aprenderlo. Si ya es sólo de
esa persona, no cambia nada.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import psycopg

from ..autoridad import Solicitante
from . import preguntas
from .auditoria import auditar
from .ia import Jugada

CHAT = "chat"
PLATAFORMA = "plataforma"

# En los hechos: lo que dijo la persona para nombrar a alguien que Leda no reconoce, tal cual
# (nunca el nombre de nadie); a quién reconoce Leda, para confirmarlo; y a quién aprendió a
# reconocer por eso. Sus significados, en `hechos.py`.
COMO_LO_NOMBRO = "como_lo_nombro"
PARA_CONFIRMAR = "quien_es_para_confirmar"
APRENDIO = "aprendio_como_le_dicen_a"
# Lo que falta: quién es.
QUIEN_ES = "quien_es"
# En lo que se recuerda de un nombre para el resto del turno (`Contexto.nombrados`): la persona
# dijo que no es del equipo.
DE_AFUERA = "de_afuera"
# Sin pregunta de quién es que contestar.
SIN_PREGUNTA = "sin_pregunta_abierta"
# El dato de una opción de "cuál de esas personas": el integrante elegido.
INTEGRANTE_ID = "integrante_id"
BOTON_CONFIRMAR = "Confirmar"
# Decir de quién es un apodo sin que Leda lo pregunte (decisión 67): el apodo, como lo dice; a
# quiénes se lo dicen ya; lo que falta saber (si a todas o sólo a la nueva, la pregunta
# `preguntas.A_QUIENES`, que también es el dato de sus opciones), y cómo quedó.
APODO = "apodo"
YA_LE_DICEN_ASI_A = "ya_le_dicen_asi_a"
A_QUIENES = preguntas.A_QUIENES
SIGUE_RECONOCIENDO_ASI_A = "sigue_reconociendo_asi_a"
DEJO_DE_RECONOCER_ASI_A = "dejo_de_reconocer_asi_a"
YA_LO_RECONOCIA_ASI = "ya_lo_reconocia_asi"
A_TODOS, SOLO_A_ESA = "a_todos", "solo_a_esa"

_DE_QUIEN_ES = (preguntas.QUIEN_ES, preguntas.CONFIRMAR_QUIEN_ES, preguntas.CUAL_DE_ESAS_PERSONAS,
                preguntas.A_QUIENES)


def normalizar(dicho: str) -> str:
    """Las palabras de lo dicho como el código compara los nombres, separadas por un espacio:
    "El Tano" es "el tano"."""
    from .fichas import palabras        # fichas importa este módulo
    return " ".join(palabras(dicho))


def vigentes(cur: psycopg.Cursor) -> list[dict[str, Any]]:
    """Los apodos vigentes de los integrantes activos del espacio (la vista `integrante` lo acota
    al espacio de la transacción, también con la conexión de administración)."""
    cur.execute("""select a.membership_id, a.apodo
                     from apodo a
                     join integrante i on i.membership_id = a.membership_id
                    where a.borrado_en is null and i.activo""")
    return cur.fetchall()


def aprender(cur: psycopg.Cursor, quien: Solicitante, membership_id: str, dicho: str,
             ahora: datetime, *, inbound_message_id: str | None = None) -> bool:
    """El apodo aprendido por chat para ese integrante, con quien lo enseñó, y su fila de
    auditoría (ADR 0020, decisiones 1 y 8). Si ya lo tenía vigente, no cambia nada. Devuelve si
    lo aprendió ahora."""
    apodo = normalizar(dicho)
    if not apodo:
        return False
    cur.execute("""select 1 from apodo
                    where membership_id = %s and apodo = %s and borrado_en is null""",
                (membership_id, apodo))
    if cur.fetchone() is not None:
        return False
    cur.execute(
        """insert into apodo (workspace_id, membership_id, apodo, ensenado_por_app_user_id,
                              canal, at)
           values (%s, %s, %s, %s, %s, %s) returning id""",
        (quien.workspace_id, membership_id, apodo, quien.app_user_id, CHAT, ahora))
    apodo_id = cur.fetchone()["id"]
    auditar(cur, accion="aprender_apodo", workspace_id=quien.workspace_id,
            sujeto_tipo="apodo", sujeto_id=apodo_id, quien=quien,
            detalle={"membership_id": membership_id, "apodo": apodo, "canal": CHAT,
                     "ensenado_por_membership_id": quien.membership_id,
                     "at": ahora.isoformat(), "inbound_message_id": inbound_message_id})
    return True


def dejar_de_usar(cur: psycopg.Cursor, quien: Solicitante, membership_ids: list[str], dicho: str,
                  ahora: datetime, *, inbound_message_id: str | None = None) -> list[str]:
    """El apodo vigente de esos integrantes deja de usarse, con quién y cuándo (nada se borra:
    la fila queda, con `borrado_en`), y su fila de auditoría (decisión 67). Los integrantes a los
    que se les dejó de usar."""
    apodo = normalizar(dicho)
    cur.execute("""update apodo set borrado_en = %s, borrado_por_app_user_id = %s
                    where membership_id = any(%s::uuid[]) and apodo = %s and borrado_en is null
                returning id, membership_id""",
                (ahora, quien.app_user_id, membership_ids, apodo))
    filas = cur.fetchall()
    for f in filas:
        auditar(cur, accion="dejar_de_usar_apodo", workspace_id=quien.workspace_id,
                sujeto_tipo="apodo", sujeto_id=f["id"], quien=quien,
                detalle={"membership_id": str(f["membership_id"]), "apodo": apodo,
                         "canal": CHAT, "dejado_por_membership_id": quien.membership_id,
                         "at": ahora.isoformat(), "inbound_message_id": inbound_message_id})
    return [str(f["membership_id"]) for f in filas]


# --- Reconocer, o preguntar quién es ------------------------------------------------------------

def quien_es(ctx, dicho: str, *, jugada: str, datos: dict[str, Any], task_id: str | None
             ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """A quién nombra lo dicho, para una jugada que pregunta (ver el módulo): `(integrante,
    None)` si es una sola persona del equipo; `(None, None)` si la persona ya dijo que no es del
    equipo; `(None, hecho)` si Leda pregunta quién es, o cuál de varias personas, con la pregunta
    abierta y lo pedido guardado en ella para seguir después (`hecho`, para la jugada)."""
    from .fichas import integrantes_que_coinciden       # fichas importa este módulo
    nombrado = ctx.nombrados.get(normalizar(dicho))
    if nombrado == DE_AFUERA:
        return None, None
    if nombrado is not None:
        return _integrante(ctx.cur, nombrado), None
    coinciden = integrantes_que_coinciden(ctx.cur, dicho)
    if len(coinciden) == 1:
        return coinciden[0], None
    pedido = {"nombre": jugada, COMO_LO_NOMBRO: dicho,
              "datos": {k: v for k, v in datos.items() if k not in ("tarea", "de_la_pregunta")}}
    if not coinciden:
        return None, _preguntar_quien_es(ctx, pedido, task_id)
    return None, _preguntar_cual(ctx, pedido, task_id, coinciden, aprende=False)


def _integrante(cur, membership_id: str) -> dict[str, Any] | None:
    cur.execute("""select membership_id, nombre from integrante
                    where membership_id = %s and activo""", (membership_id,))
    return cur.fetchone()


def _abrir(ctx, tipo: str, pedido: dict[str, Any], task_id: str | None, *,
           jugada: dict[str, Any], opciones=()) -> tuple[bool, str]:
    """Abre la pregunta de quién es (o de cuál de esas personas), con lo pedido guardado. Si la
    jugada contestaba la pregunta que está abierta (quién lo destraba), ésta va antes: precisa esa
    respuesta, que queda para después (un tema a la vez igual). Devuelve si se hace ahora y su id."""
    from .fichas import FICHAS      # fichas importa este módulo
    vigente = preguntas.actual(ctx.cur, ctx.quien.membership_id)
    ahora, pregunta_id = preguntas.abrir_con_id(ctx, tipo, task_id, jugada=jugada,
                                                opciones=opciones)
    ficha = FICHAS.get(pedido.get("nombre"))
    if (not ahora and vigente is not None and ficha is not None
            and vigente["tipo"] in ficha.contesta
            and str(vigente["task_id"]) == str(task_id)):
        preguntas.adelantar(ctx, pregunta_id)
        ahora = True
    return ahora, pregunta_id


def _preguntar_quien_es(ctx, pedido: dict[str, Any], task_id: str | None) -> dict[str, Any]:
    """La pregunta de quién es, con lo pedido guardado (`_abrir`)."""
    from .fichas import nombrar_pregunta      # fichas importa este módulo
    ahora, pregunta_id = _abrir(ctx, preguntas.QUIEN_ES, pedido, task_id, jugada=pedido)
    hecho = {"resultado": "falta_dato", "falta": [QUIEN_ES],
             COMO_LO_NOMBRO: pedido[COMO_LO_NOMBRO]}
    nombrar_pregunta(hecho, "pregunta" if ahora else "pregunta_para_despues",
                     preguntas.QUIEN_ES, pregunta_id)
    return hecho


def _preguntar_cual(ctx, pedido: dict[str, Any], task_id: str | None,
                    coinciden: list[dict[str, Any]], *, aprende: bool) -> dict[str, Any]:
    """Cuál de esas personas, con un botón por persona, por su nombre y apellido (`_abrir`);
    `aprende`: si lo elegido enseña el apodo (la respuesta a quién es) o sólo dice a quién se
    refería (un apodo ya aprendido de dos)."""
    from .fichas import nombrar_pregunta      # fichas importa este módulo
    preguntas.cerrar_las_de_una_jugada_de_tipo(
        ctx, preguntas.CUAL_DE_ESAS_PERSONAS, pedido.get("nombre"), task_id, "sin_efecto",
        {"reemplazada": True, **({"tarea": task_id} if task_id else {})})
    jugada = {**pedido, "candidatos": [str(c["membership_id"]) for c in coinciden],
              "aprende": aprende}
    ahora, pregunta_id = _abrir(
        ctx, preguntas.CUAL_DE_ESAS_PERSONAS, pedido, task_id, jugada=jugada,
        opciones=[(c["nombre"], {"jugada": "decir_quien_es",
                                 "datos": {INTEGRANTE_ID: str(c["membership_id"])}})
                  for c in coinciden])
    hecho = {"resultado": "falta_dato", "falta": [QUIEN_ES],
             COMO_LO_NOMBRO: pedido[COMO_LO_NOMBRO], "coinciden": [c["nombre"] for c in coinciden]}
    nombrar_pregunta(hecho, "pregunta" if ahora else "pregunta_para_despues",
                     preguntas.CUAL_DE_ESAS_PERSONAS, pregunta_id)
    return hecho


# --- La respuesta: quién es ---------------------------------------------------------------------

def decir(ctx, datos: dict[str, Any], tarea: dict[str, Any] | None) -> dict[str, Any]:
    """La jugada `decir_quien_es`: la respuesta a la pregunta de quién es (o de cuál de esas
    personas, o un nombre distinto del que Leda mostró para confirmar). Ver el módulo."""
    from .fichas import integrantes_que_coinciden, vacio       # fichas importa este módulo
    cur = ctx.cur
    q = _la_pregunta(ctx, datos)
    tocada = bool(datos.get("de_la_pregunta"))
    apodo = None if vacio(datos.get(APODO)) else str(datos[APODO]).strip()
    if apodo is not None and not tocada and not _la_contesta(q, apodo):
        return _de_quien_es_el_apodo(ctx, apodo, datos.get(QUIEN_ES))
    if q is None:
        return {"resultado": "no_se_puede", "motivo": SIN_PREGUNTA}
    pedido = dict(q["jugada"] or {})
    if q["tipo"] == preguntas.A_QUIENES:
        return _a_quienes(ctx, q, pedido, datos, tocada=tocada)
    if tocada and datos.get(INTEGRANTE_ID):
        # El botón de una persona: es una de las que Leda ofreció.
        integrante = (_integrante(cur, str(datos[INTEGRANTE_ID]))
                      if str(datos[INTEGRANTE_ID]) in (pedido.get("candidatos") or []) else None)
        if integrante is None:
            return {"resultado": "no_se_puede", "motivo": "persona_desconocida"}
        return _elegida(ctx, q, pedido, integrante, tocada=True)
    if datos.get(DE_AFUERA) is True:
        if str(q["id"]) in ctx.preguntas_del_turno:
            # Que no es del equipo lo contesta la persona, a la pregunta que vio en un mensaje
            # anterior: leído del mismo mensaje que la nombró, lo decidiría la IA (decisión 65
            # del usuario, 2026-10-11). La pregunta sigue.
            return {"resultado": "falta_dato", "falta": [QUIEN_ES],
                    COMO_LO_NOMBRO: pedido.get(COMO_LO_NOMBRO)}
        _cerrar(ctx, q, "respondida", {"jugada": "decir_quien_es", DE_AFUERA: True})
        return _seguir(ctx, q, pedido, DE_AFUERA)
    if vacio(datos.get(QUIEN_ES)):
        return {"resultado": "falta_dato", "falta": [QUIEN_ES],
                COMO_LO_NOMBRO: pedido.get(COMO_LO_NOMBRO)}
    dicho = str(datos[QUIEN_ES]).strip()
    coinciden = integrantes_que_coinciden(cur, dicho)
    if q["tipo"] == preguntas.CUAL_DE_ESAS_PERSONAS:
        coinciden = [c for c in coinciden
                     if str(c["membership_id"]) in (pedido.get("candidatos") or [])]
    if not coinciden:
        # Nunca una identidad inventada: lo dice, y la pregunta sigue (constitución §4).
        return {"resultado": "no_se_puede", "motivo": "persona_desconocida",
                "nombre_que_no_esta": dicho, COMO_LO_NOMBRO: pedido.get(COMO_LO_NOMBRO)}
    if q["tipo"] == preguntas.CUAL_DE_ESAS_PERSONAS:
        if len(coinciden) == 1:
            return _elegida(ctx, q, pedido, coinciden[0], tocada=False)
        # Todavía más de una de las que Leda ofreció: la pregunta sigue, y Leda no elige.
        return {"resultado": "falta_dato", "falta": [QUIEN_ES],
                COMO_LO_NOMBRO: pedido.get(COMO_LO_NOMBRO),
                "coinciden": [c["nombre"] for c in coinciden]}
    _cerrar(ctx, q, "respondida" if q["tipo"] == preguntas.QUIEN_ES else "sin_efecto",
            {"jugada": "decir_quien_es"})
    pedido = {k: v for k, v in pedido.items()
              if k not in ("candidatos", "aprende", INTEGRANTE_ID, "integrante")}
    if len(coinciden) > 1:
        return _preguntar_cual(ctx, pedido, _task(q), coinciden, aprende=True)
    return _mostrar_para_confirmar(ctx, pedido, _task(q), coinciden[0])


def _la_contesta(q: dict[str, Any] | None, apodo: str) -> bool:
    """Si decir de quién es ese apodo contesta la pregunta de quién es (o de a quiénes) que Leda
    hizo por él: entonces no es una corrección."""
    if q is None:
        return False
    return normalizar(str((q["jugada"] or {}).get(COMO_LO_NOMBRO) or "")) == normalizar(apodo)


def _la_pregunta(ctx, datos: dict[str, Any]) -> dict[str, Any] | None:
    """La pregunta que contesta: la del botón tocado; si no, la abierta si es de quién es; si
    no, la más nueva de quién es que quedó para después."""
    cur = ctx.cur
    if datos.get("de_la_pregunta"):
        cur.execute("select * from conversation_question where id = %s",
                    (datos["de_la_pregunta"],))
        q = cur.fetchone()
        return q if q is not None and q["tipo"] in _DE_QUIEN_ES else None
    abierta = preguntas.actual(cur, ctx.quien.membership_id)
    if abierta is not None and abierta["tipo"] in _DE_QUIEN_ES:
        return abierta
    cur.execute("""select * from conversation_question
                    where membership_id = %s and cerrada_en is null and tipo = any(%s)
                    order by abierta_en desc limit 1""",
                (ctx.quien.membership_id, list(_DE_QUIEN_ES)))
    return cur.fetchone()


def _task(q: dict[str, Any]) -> str | None:
    return str(q["task_id"]) if q["task_id"] is not None else None


def _cerrar(ctx, q: dict[str, Any], cierre: str, detalle: dict[str, Any]) -> None:
    if q["cerrada_en"] is None:
        preguntas.cerrar(ctx, str(q["id"]), cierre,
                         {**detalle, **({"tarea": _task(q)} if q["task_id"] else {})})


def _mostrar_para_confirmar(ctx, pedido: dict[str, Any], task_id: str | None,
                            integrante: dict[str, Any]) -> dict[str, Any]:
    """A quién reconoce Leda, con nombre y apellido, para que la persona lo confirme; nada se
    aprende todavía."""
    from .fichas import nombrar_pregunta      # fichas importa este módulo
    jugada = {**pedido, INTEGRANTE_ID: str(integrante["membership_id"]),
              "integrante": integrante["nombre"]}
    preguntas.cerrar_las_de_una_jugada_de_tipo(
        ctx, preguntas.CONFIRMAR_QUIEN_ES, pedido.get("nombre"), task_id, "sin_efecto",
        {"reemplazada": True, **({"tarea": task_id} if task_id else {})})
    ahora, pregunta_id = preguntas.abrir_con_id(
        ctx, preguntas.CONFIRMAR_QUIEN_ES, task_id, jugada=jugada,
        opciones=[(BOTON_CONFIRMAR, {"jugada": "confirmar"})])
    hecho = {"resultado": PARA_CONFIRMAR, COMO_LO_NOMBRO: pedido[COMO_LO_NOMBRO],
             "integrante": integrante["nombre"]}
    nombrar_pregunta(hecho, "pregunta" if ahora else "pregunta_para_despues",
                     preguntas.CONFIRMAR_QUIEN_ES, pregunta_id)
    return hecho


def _elegida(ctx, q: dict[str, Any], pedido: dict[str, Any], integrante: dict[str, Any], *,
             tocada: bool) -> dict[str, Any]:
    """Una de las personas que Leda ofreció, elegida con nombre y apellido: si era la respuesta
    a quién es, el apodo se aprende para ella; si era un apodo ya aprendido de dos, no cambia
    ninguno. Después, lo pedido."""
    _cerrar(ctx, q, "respondida", {"jugada": "decir_quien_es"})
    aprendio = None
    if pedido.get("aprende"):
        aprender(ctx.cur, ctx.quien, str(integrante["membership_id"]), pedido[COMO_LO_NOMBRO],
                 ctx.ahora, inbound_message_id=ctx.entrante_id)
        aprendio = integrante["nombre"]
    return _seguir(ctx, q, pedido, str(integrante["membership_id"]), aprendio=aprendio,
                   tocada=tocada)


# --- Confirmarlo --------------------------------------------------------------------------------

def la_que_se_confirma(ctx, datos: dict[str, Any], tarea: dict[str, Any] | None
                       ) -> dict[str, Any] | None:
    """La confirmación de quién es, si es eso lo que la persona confirma: la del botón tocado o,
    escrita, la que está abierta (de la tarea que nombra, si nombra una). Si no, `None`."""
    cur = ctx.cur
    if datos.get("de_la_pregunta"):
        cur.execute("select * from conversation_question where id = %s",
                    (datos["de_la_pregunta"],))
        q = cur.fetchone()
        return q if q is not None and q["tipo"] == preguntas.CONFIRMAR_QUIEN_ES else None
    abierta = preguntas.actual(cur, ctx.quien.membership_id)
    if (abierta is not None and abierta["tipo"] == preguntas.CONFIRMAR_QUIEN_ES
            and (tarea is None or str(abierta["task_id"]) == tarea["id"])):
        return abierta
    return None


def confirmar(ctx, datos: dict[str, Any], q: dict[str, Any]) -> dict[str, Any]:
    """Quién es, confirmado por la persona, tocado o escrito. Escrito vale la guarda de la
    decisión 2: lo último que vio, en un mensaje anterior. Con la confirmación, Leda aprende el
    apodo y hace lo pedido."""
    from .entrega import NO_ES_LO_ULTIMO_QUE_VIO, NO_VALE_LA_CONFIRMACION
    cur = ctx.cur
    tocada = bool(datos.get("de_la_pregunta"))
    pedido = dict(q["jugada"] or {})
    if not tocada:
        vigente = preguntas.actual(cur, ctx.quien.membership_id)
        if (q["cerrada_en"] is not None or vigente is None
                or str(vigente["id"]) != str(q["id"])
                or str(q["id"]) in ctx.preguntas_del_turno):
            return {"resultado": NO_VALE_LA_CONFIRMACION, "motivo": NO_ES_LO_ULTIMO_QUE_VIO,
                    COMO_LO_NOMBRO: pedido.get(COMO_LO_NOMBRO),
                    "integrante": pedido.get("integrante")}
    integrante = _integrante(cur, str(pedido.get(INTEGRANTE_ID)))
    if integrante is None:
        # Dejó de ser del equipo entre que se mostró y se confirmó: no se aprende nada.
        _cerrar(ctx, q, "sin_efecto", {"jugada": "confirmar"})
        return {"resultado": "no_se_puede", "motivo": "persona_desconocida",
                "nombre_que_no_esta": pedido.get("integrante")}
    _cerrar(ctx, q, "respondida", {"jugada": "confirmar"})
    aprender(cur, ctx.quien, str(integrante["membership_id"]), pedido[COMO_LO_NOMBRO],
             ctx.ahora, inbound_message_id=ctx.entrante_id)
    return _seguir(ctx, q, pedido, str(integrante["membership_id"]),
                   aprendio=integrante["nombre"], tocada=tocada)


# --- Decir de quién es un apodo, sin que Leda lo pregunte (decisión 67) -------------------------

def _de_quien_es_el_apodo(ctx, apodo: str, dicho: Any) -> dict[str, Any]:
    """"El flaco es Marcos": si ya es de otra persona, Leda pregunta a quiénes les dicen así, con
    dos botones, y no cambia nada todavía; si no es de nadie, confirma con nombre y apellido antes
    de aprenderlo; si ya es sólo de esa persona, no cambia nada (ver el módulo)."""
    from .fichas import integrantes_que_coinciden, nombrar_pregunta, vacio
    cur = ctx.cur
    if vacio(dicho):
        return {"resultado": "falta_dato", "falta": [QUIEN_ES], COMO_LO_NOMBRO: apodo}
    dicho = str(dicho).strip()
    coinciden = integrantes_que_coinciden(cur, dicho)
    if not coinciden:
        return {"resultado": "no_se_puede", "motivo": "persona_desconocida",
                "nombre_que_no_esta": dicho, COMO_LO_NOMBRO: apodo}
    if len(coinciden) > 1:
        return {"resultado": "falta_dato", "falta": [QUIEN_ES], COMO_LO_NOMBRO: apodo,
                "coinciden": [c["nombre"] for c in coinciden]}
    nueva = coinciden[0]
    nueva_id = str(nueva["membership_id"])
    duenos = {str(a["membership_id"]) for a in vigentes(cur) if a["apodo"] == normalizar(apodo)}
    if not duenos:
        # Un apodo que no es de nadie: como contestar quién es (ADR 0020, decisión 1).
        return _mostrar_para_confirmar(ctx, {COMO_LO_NOMBRO: apodo}, None, nueva)
    otras = sorted((_integrante(cur, d) for d in duenos - {nueva_id}),
                   key=lambda i: i["nombre"])
    if not otras:
        return {"resultado": YA_LO_RECONOCIA_ASI, COMO_LO_NOMBRO: apodo,
                "integrante": nueva["nombre"]}
    jugada = {"nombre": "decir_quien_es", COMO_LO_NOMBRO: apodo, INTEGRANTE_ID: nueva_id,
              "integrante": nueva["nombre"], "otras": [str(o["membership_id"]) for o in otras]}
    preguntas.cerrar_las_de_una_jugada_de_tipo(ctx, A_QUIENES, "decir_quien_es", None,
                                               "sin_efecto", {"reemplazada": True})
    ahora, pregunta_id = preguntas.abrir_con_id(
        ctx, A_QUIENES, None, jugada=jugada,
        opciones=[("A los dos" if len(otras) == 1 else "A todos",
                   {"jugada": "decir_quien_es", "datos": {A_QUIENES: A_TODOS}}),
                  (f"Sólo a {nueva['nombre']}",
                   {"jugada": "decir_quien_es", "datos": {A_QUIENES: SOLO_A_ESA}})])
    hecho = {"resultado": "falta_dato", "falta": [A_QUIENES], COMO_LO_NOMBRO: apodo,
             "integrante": nueva["nombre"], YA_LE_DICEN_ASI_A: [o["nombre"] for o in otras]}
    nombrar_pregunta(hecho, "pregunta" if ahora else "pregunta_para_despues", A_QUIENES,
                     pregunta_id)
    return hecho


def _a_quienes(ctx, q: dict[str, Any], pedido: dict[str, Any], datos: dict[str, Any], *,
               tocada: bool) -> dict[str, Any]:
    """La respuesta a si a todas les dicen así o sólo a la nueva: tocada, la opción; escrita,
    nombrar sólo a la nueva es "sólo a ella" (elegir la opción por escrito la corre como el
    botón). Lo demás no la contesta: la pregunta sigue."""
    from .fichas import integrantes_que_coinciden, vacio
    nueva = _integrante(ctx.cur, str(pedido.get(INTEGRANTE_ID)))
    if nueva is None:
        _cerrar(ctx, q, "sin_efecto", {"jugada": "decir_quien_es"})
        return {"resultado": "no_se_puede", "motivo": "persona_desconocida",
                "nombre_que_no_esta": pedido.get("integrante")}
    eleccion = datos.get(A_QUIENES) if tocada else None
    if not tocada and not vacio(datos.get(QUIEN_ES)):
        coinciden = integrantes_que_coinciden(ctx.cur, str(datos[QUIEN_ES]))
        if [str(c["membership_id"]) for c in coinciden] == [str(nueva["membership_id"])]:
            eleccion = SOLO_A_ESA
    if eleccion not in (A_TODOS, SOLO_A_ESA):
        return {"resultado": "falta_dato", "falta": [A_QUIENES],
                COMO_LO_NOMBRO: pedido.get(COMO_LO_NOMBRO), "integrante": nueva["nombre"]}
    _cerrar(ctx, q, "respondida", {"jugada": "decir_quien_es", A_QUIENES: eleccion})
    apodo = pedido[COMO_LO_NOMBRO]
    otras = [str(o) for o in pedido.get("otras") or []]
    hecho: dict[str, Any] = {"resultado": "anotado", COMO_LO_NOMBRO: apodo}
    if eleccion == SOLO_A_ESA:
        dejadas = dejar_de_usar(ctx.cur, ctx.quien, otras, apodo, ctx.ahora,
                                inbound_message_id=ctx.entrante_id)
        hecho[DEJO_DE_RECONOCER_ASI_A] = _nombres(ctx.cur, dejadas)
    else:
        hecho[SIGUE_RECONOCIENDO_ASI_A] = _nombres(ctx.cur, otras)
    aprender(ctx.cur, ctx.quien, str(nueva["membership_id"]), apodo, ctx.ahora,
             inbound_message_id=ctx.entrante_id)
    hecho[APRENDIO] = nueva["nombre"]
    return hecho


def _nombres(cur, membership_ids: list[str]) -> list[str]:
    return sorted(i["nombre"] for i in (_integrante(cur, m) for m in membership_ids) if i)


# --- Seguir con lo pedido -----------------------------------------------------------------------

def _seguir(ctx, q: dict[str, Any], pedido: dict[str, Any], nombrado: str, *,
            aprendio: str | None = None, tocada: bool = False) -> dict[str, Any]:
    """Lo que la persona había pedido, como si hubiera nombrado a la persona por su nombre (o, si
    no es del equipo, como alguien de afuera): la misma jugada, con lo que dijo, por el manejador
    de la lista cerrada del turno y con las comprobaciones de su ficha."""
    from .fichas import JUGADAS               # fichas importa este módulo
    from .situaciones import LO_ELEGIDO_QUEDA
    ctx.nombrados[normalizar(pedido[COMO_LO_NOMBRO])] = nombrado
    if not pedido.get("nombre"):
        # Sólo decía de quién es un apodo (decisión 67): no había nada más pedido.
        return {"resultado": "anotado", COMO_LO_NOMBRO: pedido[COMO_LO_NOMBRO],
                **({APRENDIO: aprendio} if aprendio is not None else {})}
    datos = dict(pedido.get("datos") or {})
    if q["task_id"] is not None:
        alias = preguntas.tarea_dicha(ctx, q["task_id"]).get("alias")
        if alias is not None:
            datos["tarea"] = alias
    jugadas = ctx.jugadas if ctx.jugadas is not None else JUGADAS
    manejador = jugadas.get(pedido["nombre"])
    if manejador is None:
        return {"resultado": "no_se_puede", "motivo": "fuera_de_la_lista"}
    hecho = dict(manejador(ctx, Jugada(pedido["nombre"], datos)))
    if aprendio is not None:
        hecho[APRENDIO] = aprendio
        if tocada and hecho.get("resultado") == "no_se_puede":
            # Lo confirmado ya quedó aprendido: que lo pedido no se pueda no lo deshace.
            hecho[LO_ELEGIDO_QUEDA] = True
    return hecho
