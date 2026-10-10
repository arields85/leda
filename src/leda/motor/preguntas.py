"""Las preguntas de Leda y sus opciones.

Diseño probado en la Etapa 2 (E2-4; `odd/tasks/prueba-chica-del-motor.md`, sección 4, "Las
ocho situaciones, una vez"); ADR 0018,
decisiones 3, 4 y 9d. Una pregunta es lo que Leda espera de la persona para completar algo
que ella empezó: la causa de un bloqueo, quién lo destraba, de qué tarea habla. Se guarda en
`conversation_question` con la jugada que espera (`jugada`) y, si es una duda, sus opciones en
`conversation_option`, cada una con un token único: lo único que vuelve con un toque.

Un tema a la vez, para todas las fichas igual:

- **La pregunta abierta** es la de `conversation_state.pregunta_abierta_id`; las demás sin
  cerrar están **para después** (`para_despues_en`).
- **Abrir una:** si no hay otra abierta, queda abierta. Si la abierta salió en este mismo
  mensaje, la nueva queda para después: de a una, en el orden en que la persona las dijo
  (situación general 2). Si la abierta es de antes, Leda sigue a la persona: pregunta lo nuevo y
  la de antes queda para después (9d). Una pregunta igual a una sin cerrar (mismo tipo, tarea y
  jugada) no se repite: es la misma.
- **Contestar:** una jugada que se anota contesta las preguntas que su ficha declara
  (`Ficha.contesta`) sobre esa tarea y la duda que esperaba esa misma jugada si la tarea es una
  de sus opciones.
- **Al terminar el turno**, si no quedó ninguna abierta, vuelve la más vieja de las que
  quedaron para después (salvo la que la persona dejó para después en este mismo mensaje), y la
  redacción recibe la única pregunta que se hace (`al_terminar_el_turno`).

Nada se borra: una pregunta se cierra con su momento, cómo (`respondida`, `cancelada` o
`sin_efecto`) y con qué (`cierre_detalle`), que es lo que se dice si después llega un toque
viejo (situación general 7).

**Cada tipo de pregunta se declara una vez** (`TIPOS`, como las fichas de las jugadas): si
espera respuesta y cuál es su espera. Una pregunta que **espera respuesta** no se puede dejar
sin efecto y, cuando Leda la hace, abre su espera (`pending_reply`, ADR 0017, decisión 6) si no
hay una abierta; una que queda para después la abre cuando vuelve. Sin respuesta, la escalera la
repite y sigue hasta escalar (`escalera.py`; ADR 0018, 9b y 9c; decisión del usuario,
2026-10-05). La del estado de la tarea y la de su fecha esperan
con el pedido de estado, que repite la escalera de la tarea; las demás, con su propia espera,
que repite la escalera de las preguntas. Una que no espera respuesta se puede dejar ("dejá, no
importa") y Leda no insiste.

**Lo que Leda propone es un tema abierto** (`PROPUESTA`; ADR 0013, la pregunta pendiente es el
contexto): cuando una jugada le propone algo a la persona (las salidas de un bloqueo, una
previsión en lugar de una reasignación), queda como pregunta, con lo propuesto. Se contesta
haciendo una de las cosas propuestas, se puede cancelar o dejar para después, y vale un tema a
la vez como para cualquier otra.

**Una oferta opcional** (`OPCIONAL` en su jugada; `es_opcional`): lo que Leda ofrece "si lo
necesitás" (pedir el detalle de una tarea, decisión 33) es un tema abierto liviano (constitución
§8: "liviana en todo lo demás"). Se contesta como cualquier propuesta, pero si la persona no la
contesta es un no: no se repite a las 4 horas (decisión 29 es para lo que Leda necesita saber),
no frena los otros temas, y no vuelve después de un cambio de tema ni cuando otro tema la deja
para después (decisión 50): se cierra (`sin_efecto`, `NO_LA_TOMO`). Una regla de las preguntas,
para cualquier oferta así, no de una jugada (derivado por el coordinador, 2026-10-09).
"""

from __future__ import annotations

import json
import re
import secrets
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from ..calendario import Calendario

CUAL_TAREA = "cual_tarea"      # la duda: de qué tarea habla (situación general 5)
# El estado de una tarea, que Leda pide por su cuenta desde el vencimiento (escalera, 9b): no se
# puede dejar sin efecto, y la contestan las jugadas que informan un hecho de la tarea.
ESTADO_DE_LA_TAREA = "estado_de_la_tarea"
# Para cuándo prevé terminar la tarea: Leda la pregunta directo a la segunda respuesta sin un
# hecho cierto (`informar_avance`, decisión del usuario, 2026-10-05). Es parte del pedido de
# estado: no se deja sin efecto, la contestan las jugadas que informan un hecho cierto, y el
# pedido del estado del día hábil siguiente la reemplaza (`avisos._abrir_la_pregunta`).
FECHA_DE_LA_TAREA = "fecha_de_la_tarea"
CAUSA_DEL_BLOQUEO = "causa_del_bloqueo"
# Quién puede destrabar un bloqueo (9c): espera respuesta como un pedido de estado.
QUIEN_DESTRABA = "quien_destraba"
# Lo que Leda le propone a la persona: lo propuesto va en la jugada de la pregunta (`propone`).
PROPUESTA = "propuesta"
# Una oferta opcional ("si lo necesitás"), en la jugada de su pregunta: sin respuesta es un no
# (ver el módulo). Cómo se cierra cuando la persona no la tomó.
OPCIONAL = "opcional"
NO_LA_TOMO = "oferta_sin_respuesta"
# Qué atrasa la tarea hasta la fecha que dio la persona, cuando queda después del vencimiento y
# no dio el porqué (usuario, 2026-10-07: "pasar una fecha sin motivo no es una buena idea, tiene
# que haber una explicación"; ADR 0018, 9n). Espera respuesta con su propia espera, como la de
# quién destraba: no se deja sin efecto y la escalera de las preguntas la repite. La abre y la
# cierra la ficha de la previsión (`fichas._anotar_prevision`), y la contesta otra previsión con
# su porqué; el aviso al referente la espera hasta el final del día (`margen.py`).
MOTIVO_DEL_ATRASO = "motivo_del_atraso"
# La entrega en curso de una tarea (ADR 0019, decisiones 4 y 5; `entrega.py`): la vista previa
# completa, que espera la confirmación (con el botón "Confirmar"), o la que espera lo que falta.
# Su jugada guarda las piezas, la huella y lo que se le mostró a la persona (`muestra`). Se
# pueden dejar: "dejá, no la entrego todavía" no anota nada.
CONFIRMAR_ENTREGA = "confirmar_la_entrega"
LO_QUE_FALTA_DE_LA_ENTREGA = "lo_que_falta_de_la_entrega"
# La decisión que ofrece el aviso de una entrega a quien la aprueba (porción 3b de la C-3;
# `aprobacion.py`): "Aprobar" y "Pedir cambios" como atajos. No es un tema abierto: quien aprueba
# no le debe una respuesta a la conversación (sus recordatorios son de la 3c), así que no se
# ordena con las demás (`ofrecer`). Vale mientras el aviso sea el vigente; un aviso más nuevo de
# la misma tarea la reemplaza, y la decisión, tocada o escrita, la contesta.
DECISION_DE_LA_ENTREGA = "decision_de_la_entrega"
# Qué le falta a una entrega a la que quien aprueba le pide cambios sin decirlo ("Pedir cambios"
# tocado): un tema abierto, que contesta el pedido de cambios con su comentario.
QUE_CAMBIOS_PIDE = "que_cambios_pide"
# Un mensaje que hace a la vez dos jugadas opuestas sobre la misma tarea (aprobar y pedir
# cambios) admite dos lecturas: ninguna se hace y Leda pregunta cuál, con las dos como opciones
# (constitución §8; ADR 0018, decisión 2). Una sola vez: la misma pregunta no se repite.
CUAL_DE_LAS_DOS = "cual_de_las_dos"
# Un botón que muestra la entrega de una tarea que espera la decisión de la persona (decisión 17
# del usuario, 2026-10-08): lo ofrece una lista de entregas, un recordatorio o lo que queda por
# revisar después de decidir una. No es un tema abierto, sólo muestra: uno nuevo no reemplaza a
# otro (`ofrecer`, `reemplaza=False`), y tocarlo corre `ver_entrega`, como escribirlo.
VER_LA_ENTREGA = "ver_la_entrega"
# Para cuándo destraba una tarea de otra persona quien la puede destrabar (C-5, porción 1;
# decisión 4 del usuario, 2026-10-08): la abre el aviso que le escribe Leda
# (`avisos.PREGUNTA_A_QUIEN_DESTRABA`) para esa persona, sobre la tarea de la persona trabada.
# Espera respuesta con su propia espera, que la escalera de las preguntas repite; no escala a
# nadie (el bloqueo que no se mueve es la decisión 7, de otra porción). La contesta lo que dice
# quien destraba (`decir_cuando_destraba`) y se cierra cuando la tarea se destraba o cambia
# quién la destraba (`persecucion.py`).
CUANDO_SE_DESTRABA = "cuando_se_destraba"
# Qué arregló la persona trabada con quien destraba su tarea (C-5c; decisiones 48 y 37 del
# usuario, 2026-10-09): la abre el aviso que se la hace (`avisos.PREGUNTA_A_QUIEN_ESTA_TRABADO`,
# cuando quien destraba dice que ya lo hablaron sin decir qué; `avisos.COMO_LE_FUE`, al día hábil
# siguiente de "se lo pido yo y te cuento"). Espera respuesta con su propia espera, que la escalera
# de las preguntas repite sin escalar (decisión 38: nunca se la abandona). La contesta lo que
# cuenta la persona trabada (`contar_lo_que_arreglaron`) o que ya puede seguir (`destrabar`); se
# cierra si contesta primero quien destraba (`persecucion.py`).
QUE_ARREGLARON = "que_arreglaron"
# Cómo vienen las tareas de la lista que Leda manda con el ritmo fijo del espacio (C-6, decisión 8 del
# usuario, 2026-10-08; `cadencias.py`): una sola pregunta por todas, sin tarea propia. Su jugada guarda
# las tareas de la lista (`tareas`) y las que la persona ya contó (`contestadas`, con el momento del
# turno); cada jugada sobre una de ellas la contesta en la lista (`marcar_en_la_lista`), y cuando
# están todas se cierra. Si contestó sólo una parte, la respuesta pregunta una vez por las otras
# (`pregunto_por_las_otras`) y, con otra respuesta parcial, se cierra (`al_terminar_el_turno`). Se
# puede dejar: las tareas que vencen tienen la espera de su escalera.
COMO_VIENEN_SUS_TAREAS = "como_vienen_sus_tareas"
# Pasarle una tarea a otra persona (C-7; `pase.py`): la vista previa del pase, que espera la
# confirmación de quien lo pide (con el botón "Confirmar" o escrita, con la guarda; se puede
# dejar), y lo que ofrece la pregunta a quien decide y a quien recibe, con dos botones cada una:
# como la decisión de una entrega, no es un tema abierto (`ofrecer`); se contesta tocando o
# escribiendo (`contestar_el_pase`).
CONFIRMAR_EL_PASE = "confirmar_el_pase"
DECIDIR_EL_PASE = "decidir_el_pase"
TOMAR_LA_TAREA = "tomar_la_tarea"
# El detalle de una tarea (decisión 33 del usuario; `detalle.py`): lo que ofrece la pregunta al
# encargado del sector de la tarea, si le comparte el detalle a quien lo pidió, con dos botones:
# como la del pase, no es un tema abierto (`ofrecer`); se contesta tocando o escribiendo
# (`contestar_el_pedido_del_detalle`).
COMPARTIR_EL_DETALLE = "compartir_el_detalle"


@dataclass(frozen=True)
class TipoDePregunta:
    """Un tipo de pregunta de Leda. `espera`: el tipo de la espera (`pending_reply.tipo`) con
    que espera respuesta; `None` si se puede dejar sin efecto. `sin_elegir_queda`: si se hace
    una sola vez, el tipo de la decisión que queda con sus opciones cuando la persona contesta
    otra cosa sin elegir: la pregunta se cierra, no se repite, y sus opciones salen como botones
    de la respuesta (`ofrecer_en_la_respuesta`), sin ser un tema abierto. `escala`: si la
    escalera de una pregunta que espera respuesta termina avisándole a quien corresponde
    (`escalera.py`); si no, la repite y no le avisa a nadie."""

    nombre: str
    espera: str | None = None
    sin_elegir_queda: str | None = None
    escala: bool = True

    @property
    def se_puede_dejar(self) -> bool:
        return self.espera is None


TIPOS: Mapping[str, TipoDePregunta] = MappingProxyType({t.nombre: t for t in (
    TipoDePregunta(CUAL_TAREA),
    TipoDePregunta(CAUSA_DEL_BLOQUEO),
    TipoDePregunta(PROPUESTA),
    TipoDePregunta(ESTADO_DE_LA_TAREA, espera=ESTADO_DE_LA_TAREA),
    # Parte del pedido de estado: espera con él y la repite la escalera de la tarea.
    TipoDePregunta(FECHA_DE_LA_TAREA, espera=ESTADO_DE_LA_TAREA),
    TipoDePregunta(QUIEN_DESTRABA, espera=QUIEN_DESTRABA),
    TipoDePregunta(MOTIVO_DEL_ATRASO, espera=MOTIVO_DEL_ATRASO),
    TipoDePregunta(CONFIRMAR_ENTREGA),
    TipoDePregunta(LO_QUE_FALTA_DE_LA_ENTREGA),
    TipoDePregunta(DECISION_DE_LA_ENTREGA),
    TipoDePregunta(QUE_CAMBIOS_PIDE),
    TipoDePregunta(CUAL_DE_LAS_DOS, sin_elegir_queda=DECISION_DE_LA_ENTREGA),
    TipoDePregunta(VER_LA_ENTREGA),
    TipoDePregunta(CUANDO_SE_DESTRABA, espera=CUANDO_SE_DESTRABA, escala=False),
    TipoDePregunta(QUE_ARREGLARON, espera=QUE_ARREGLARON, escala=False),
    TipoDePregunta(COMO_VIENEN_SUS_TAREAS),
    TipoDePregunta(CONFIRMAR_EL_PASE),
    TipoDePregunta(DECIDIR_EL_PASE),
    TipoDePregunta(TOMAR_LA_TAREA),
    TipoDePregunta(COMPARTIR_EL_DETALLE),
)})

PREFIJO_TOQUE = "m:"           # el `callback_data` de un botón es el prefijo y el token
_LARGO_ETIQUETA = 80           # `salida.BUTTON_LABEL_LIMIT`


def callback(token: str) -> str:
    return f"{PREFIJO_TOQUE}{token}"


def token_de(data: str) -> str | None:
    """El token de un `callback_data` del motor; `None` si no es uno."""
    if not data.startswith(PREFIJO_TOQUE):
        return None
    return data[len(PREFIJO_TOQUE):] or None


def alias_de_opcion(orden: int) -> str:
    return f"O{orden}"


def orden_de_alias(alias: Any) -> int | None:
    m = re.fullmatch(r"[Oo](\d+)", str(alias).strip())
    return int(m.group(1)) if m else None


# --- Leer -----------------------------------------------------------------------------------

def actual(cur, membership_id: str) -> dict[str, Any] | None:
    """La pregunta abierta de la persona, si hay y no se cerró."""
    cur.execute("""select q.* from conversation_state s
                     join conversation_question q on q.id = s.pregunta_abierta_id
                    where s.membership_id = %s and q.cerrada_en is null""", (membership_id,))
    return cur.fetchone()


def para_despues(cur, membership_id: str) -> list[dict[str, Any]]:
    cur.execute("""select * from conversation_question
                    where membership_id = %s and cerrada_en is null
                      and para_despues_en is not null
                    order by abierta_en""", (membership_id,))
    return cur.fetchall()


def opciones(cur, pregunta_id: str) -> list[dict[str, Any]]:
    cur.execute("""select * from conversation_option where question_id = %s order by orden""",
                (pregunta_id,))
    return cur.fetchall()


def opcion_por_token(cur, token: str) -> dict[str, Any] | None:
    """La opción de un toque y su pregunta, bajo la RLS del espacio: un token de otro espacio
    no se encuentra."""
    cur.execute("""select o.id, o.orden, o.etiqueta, o.valor, o.question_id,
                          q.membership_id, q.cerrada_en
                     from conversation_option o
                     join conversation_question q on q.id = o.question_id
                    where o.token = %s""", (token,))
    return cur.fetchone()


def estado_para_la_ia(cur, membership_id: str, tareas) -> dict[str, Any] | None:
    """Lo que la IA recibe del estado de la conversación: la pregunta abierta (con sus
    opciones por alias) y las que quedaron para después. `None` si no hay ninguna."""
    abierta = actual(cur, membership_id)
    despues = para_despues(cur, membership_id)
    if abierta is None and not despues:
        return None
    return {"pregunta_abierta": _para_la_ia(cur, abierta, tareas) if abierta else None,
            "para_despues": [{"tipo": q["tipo"], "tarea": _alias(tareas, q["task_id"])}
                             for q in despues]}


def _para_la_ia(cur, q, tareas) -> dict[str, Any]:
    dicha = {"tipo": q["tipo"], "tarea": _alias(tareas, q["task_id"]), **_lo_propuesto(q),
             **_lo_mostrado(q)}
    if q["tipo"] == COMO_VIENEN_SUS_TAREAS:
        dicha["de_la_lista"] = [_alias(tareas, t) for t in faltan_de_la_lista(q)]
    ops = opciones(cur, q["id"])
    if ops:
        dicha["opciones"] = [{"opcion": alias_de_opcion(o["orden"]), "etiqueta": o["etiqueta"],
                              **({"tarea": _alias(tareas, (o["valor"] or {}).get("tarea"))}
                                 if not _corre_otra_jugada(o) else {})}
                             for o in ops]
    return dicha


def _corre_otra_jugada(opcion) -> bool:
    """Una opción que corre una jugada propia (el "Confirmar" de una entrega) no elige una
    tarea: su tarea es la de la pregunta."""
    return bool((opcion["valor"] or {}).get("jugada"))


def es_opcional(q) -> bool:
    """Si la pregunta es una oferta opcional: sin respuesta, es un no (ver el módulo)."""
    return bool(q is not None and (q.get("jugada") or {}).get(OPCIONAL))


def caducar(cur, q, ahora) -> None:
    """Una oferta opcional que la persona no tomó se cierra (ver el módulo): deja de ser su tema
    abierto y nada la vuelve a traer."""
    cur.execute("""update conversation_question
                      set cerrada_en = %s, cierre = 'sin_efecto', cierre_detalle = %s
                    where id = %s and cerrada_en is null""",
                (ahora, _json({NO_LA_TOMO: True, **({"tarea": str(q["task_id"])}
                                                     if q.get("task_id") else {})}),
                 str(q["id"])))
    cur.execute("""update conversation_state set pregunta_abierta_id = null, actualizado_en = %s
                    where membership_id = %s and pregunta_abierta_id = %s""",
                (ahora, str(q["membership_id"]), str(q["id"])))


def _lo_propuesto(q) -> dict[str, Any]:
    jugada = q["jugada"] or {}
    propone = jugada.get("propone")
    if not propone:
        return {}
    return {"propone": list(propone), **({OPCIONAL: True} if jugada.get(OPCIONAL) else {})}


def _lo_mostrado(q) -> dict[str, Any]:
    """Lo que la pregunta le mostró a la persona, si lo guardó (`muestra`: las piezas de una
    entrega, con sus alias): para elegir sobre eso y para volver a decirlo. De una entrega a la
    que le falta algo, también qué le falta y el ejemplo que Leda le propuso para lo que falta
    del criterio (C-3d, D3): para aceptarlo y para volver a decirlo."""
    jugada = q["jugada"] or {}
    dicho: dict[str, Any] = {}
    if jugada.get("muestra"):
        dicho["lo_mostrado"] = list(jugada["muestra"])
    for clave in ("le_falta", "le_falta_del_criterio", "ejemplo"):
        if jugada.get(clave):
            dicho[clave] = jugada[clave]
    return dicho


def lo_que_lleva(q) -> dict[str, Any]:
    """Lo que la pregunta propone o mostró, para volver a hacerla en un aviso (decisión 21)."""
    return {**_lo_propuesto(q), **_lo_mostrado(q)}


def lo_anotado(pregunta) -> dict[str, Any]:
    """Lo que se había anotado cuando Leda hizo la pregunta (la jugada y sus datos, sin la
    tarea ni ids): lo que recuerda un aviso que la vuelve a hacer."""
    jugada = pregunta["jugada"] or {}
    if not jugada.get("nombre"):
        return {}
    datos = {k: v for k, v in (jugada.get("datos") or {}).items() if k != "tarea"}
    return {"jugada": jugada["nombre"], **datos}


def _alias(tareas, task_id) -> str | None:
    if task_id is None:
        return None
    return next((t["alias"] for t in tareas if t["id"] == str(task_id)), None)


def _todas(ctx) -> tuple:
    """Las tareas que la persona nombra por su alias: las suyas, las entregas que esperan su
    decisión (`fichas.Contexto.para_aprobar`), las de otras personas que espera que destrabe
    (`fichas.Contexto.para_destrabar`), las de otras personas cuyo pase espera algo de ella
    (`fichas.Contexto.pases`, C-7) y las que alguien pidió ver y espera que decida si las comparte
    (`fichas.Contexto.para_compartir`, decisión 33)."""
    return (tuple(ctx.tareas) + tuple(getattr(ctx, "para_aprobar", ()) or ())
            + tuple(getattr(ctx, "para_destrabar", ()) or ())
            + tuple(getattr(ctx, "pases", ()) or ())
            + tuple(getattr(ctx, "para_compartir", ()) or ()))


# --- Abrir, cerrar y retomar ------------------------------------------------------------------

def abrir(ctx, tipo: str, task_id: str | None, *, jugada: dict[str, Any],
          opciones_de_tareas: Sequence[dict[str, Any]] = ()) -> bool:
    """Abre una pregunta (o reconoce la misma sin cerrar) y la ordena con las demás (ver el
    módulo); si su tipo espera respuesta, abre también su espera. `opciones_de_tareas`: las
    tareas de una duda, que se ofrecen como opciones. Devuelve si es la que se pregunta ahora
    (`False`: quedó para después)."""
    return abrir_con_id(ctx, tipo, task_id, jugada=jugada,
                        opciones_de_tareas=opciones_de_tareas)[0]


def abrir_con_id(ctx, tipo: str, task_id: str | None, *, jugada: dict[str, Any],
                 opciones_de_tareas: Sequence[dict[str, Any]] = (),
                 opciones: Sequence[tuple[str, dict[str, Any]]] = ()) -> tuple[bool, str]:
    """`abrir`, y además el id de la pregunta: el hecho que la nombra lo lleva para leerla al
    terminar el turno (`fichas.EFECTOS`). `opciones`: otras opciones que las tareas, cada una
    con su etiqueta y su valor (la tarea, y la jugada que corre si se la elige, con sus datos;
    `situaciones.elegir_opcion`)."""
    cur, persona = ctx.cur, ctx.quien.membership_id
    de_tipo = TIPOS[tipo]           # la lista es cerrada: un tipo sin declarar es un error
    se_puede_dejar = de_tipo.se_puede_dejar
    cur.execute("""select id from conversation_question
                    where membership_id = %s and cerrada_en is null and tipo = %s
                      and task_id is not distinct from %s
                      and jugada ->> 'nombre' is not distinct from %s
                    order by abierta_en limit 1""",
                (persona, tipo, task_id, jugada.get("nombre")))
    misma = cur.fetchone()
    if misma is not None:
        pregunta = str(misma["id"])
        cur.execute("update conversation_question set jugada = %s where id = %s",
                    (_json(jugada), pregunta))
    else:
        cur.execute(
            """insert into conversation_question (workspace_id, membership_id, tipo, task_id,
                                                  jugada, se_puede_dejar, abierta_en)
               values (%s, %s, %s, %s, %s, %s, %s) returning id""",
            (ctx.quien.workspace_id, persona, tipo, task_id, _json(jugada), se_puede_dejar,
             ctx.ahora))
        pregunta = str(cur.fetchone()["id"])
        todas = ([(t["titulo"], {"tarea": t["id"]}) for t in opciones_de_tareas]
                 + list(opciones))
        for orden, (etiqueta, valor) in enumerate(todas, 1):
            cur.execute(
                """insert into conversation_option (workspace_id, question_id, token,
                                                    etiqueta, valor, orden)
                   values (%s, %s, %s, %s, %s, %s)""",
                (ctx.quien.workspace_id, pregunta, secrets.token_urlsafe(9),
                 _etiqueta(etiqueta), _json(valor), orden))

    vigente = actual(cur, persona)
    if vigente is None or str(vigente["id"]) == pregunta:
        _que_sea_la_abierta(ctx, pregunta)
        ahora_si = True
    elif str(vigente["id"]) in ctx.preguntas_del_turno:
        _dejar_para_despues(ctx, pregunta)
        ahora_si = False
    else:
        _dejar_para_despues(ctx, str(vigente["id"]))
        _que_sea_la_abierta(ctx, pregunta)
        ahora_si = True
    if ahora_si:
        _esperar_respuesta(ctx, tipo, task_id)
    if pregunta not in ctx.preguntas_del_turno:
        ctx.preguntas_del_turno.append(pregunta)
    return ahora_si, pregunta


def ofrecer(ctx, tipo: str, task_id: str, *, jugada: dict[str, Any],
            opciones: Sequence[tuple[str, dict[str, Any]]], reemplaza: bool = True) -> str:
    """Una decisión que ofrece un aviso, con sus opciones como botones (`DECISION_DE_LA_ENTREGA`):
    queda sin cerrar, para que sus botones valgan, pero no es un tema abierto ni queda para
    después (no se ordena con las demás ni vuelve sola). La que ofrecía otro aviso de la misma
    tarea queda reemplazada (situación general 7), salvo con `reemplaza=False` (lo que sólo
    muestra algo, como ver una entrega: un botón viejo sigue valiendo). Devuelve su id."""
    if reemplaza:
        ctx.cur.execute("""select id from conversation_question
                            where membership_id = %s and tipo = %s and task_id = %s
                              and cerrada_en is null""",
                        (ctx.quien.membership_id, tipo, task_id))
        for vieja in ctx.cur.fetchall():
            cerrar(ctx, str(vieja["id"]), "sin_efecto", {"reemplazada": True, "tarea": task_id})
    ctx.cur.execute(
        """insert into conversation_question (workspace_id, membership_id, tipo, task_id,
                                              jugada, se_puede_dejar, abierta_en)
           values (%s, %s, %s, %s, %s, %s, %s) returning id""",
        (ctx.quien.workspace_id, ctx.quien.membership_id, tipo, task_id, _json(jugada),
         TIPOS[tipo].se_puede_dejar, ctx.ahora))
    pregunta = str(ctx.cur.fetchone()["id"])
    for orden, (etiqueta, valor) in enumerate(opciones, 1):
        ctx.cur.execute(
            """insert into conversation_option (workspace_id, question_id, token, etiqueta,
                                                valor, orden)
               values (%s, %s, %s, %s, %s, %s)""",
            (ctx.quien.workspace_id, pregunta, secrets.token_urlsafe(9), _etiqueta(etiqueta),
             _json(valor), orden))
    return pregunta


def ofrecer_en_la_respuesta(ctx, tipo: str, task_id: str, *, jugada: dict[str, Any],
                            opciones: Sequence[tuple[str, dict[str, Any]]],
                            reemplaza: bool = True) -> str:
    """Una decisión ofrecida en la respuesta de este turno (`ofrecer`): sus botones salen con esa
    respuesta (`botones.ConOpciones`), que el turno ata a la decisión al encolarla
    (`de_la_respuesta`). No es un tema abierto. Devuelve su id."""
    pregunta = ofrecer(ctx, tipo, task_id, jugada=jugada, opciones=opciones, reemplaza=reemplaza)
    ctx.ofrecidas.append(pregunta)
    return pregunta


def atar_a_la_respuesta(cur, ofrecidas: Sequence[str], outbox_id: str) -> None:
    """Las decisiones ofrecidas en un turno, atadas a la fila de su respuesta, con el orden en
    que se ofrecieron (el de sus botones)."""
    for orden, pregunta in enumerate(ofrecidas, 1):
        cur.execute("""update conversation_question
                          set jugada = coalesce(jugada, '{}'::jsonb)
                                       || jsonb_build_object('de_la_respuesta', %s::text,
                                                             'orden_en_la_respuesta', %s::int)
                        where id = %s""", (outbox_id, orden, pregunta))


def _esperar_respuesta(ctx, tipo: str, task_id) -> None:
    """Cuando Leda hace una pregunta que espera respuesta, su espera: desde ese momento cuenta el
    silencio. Una que queda para después no la abre: nadie puede no contestar lo que todavía no
    se le preguntó (revisión de la corrida en seco con las 16 conversaciones)."""
    de_tipo = TIPOS[tipo]
    if de_tipo.espera is not None and task_id is not None:
        _abrir_la_espera(ctx, de_tipo.espera, str(task_id))


def _abrir_la_espera(ctx, tipo: str, task_id: str) -> None:
    """La espera de la respuesta, si no hay una abierta de ese tipo para esa tarea: una
    pregunta que espera respuesta nunca queda sin su espera (la repite la escalera)."""
    cur, persona = ctx.cur, ctx.quien.membership_id
    cur.execute("""select 1 from pending_reply
                    where membership_id = %s and task_id = %s and tipo = %s
                      and satisfecho_en is null and escalado_en is null""",
                (persona, task_id, tipo))
    if cur.fetchone() is not None:
        return
    cal = Calendario.desde_base(cur, ctx.quien.workspace_id)
    cur.execute(
        """insert into pending_reply (workspace_id, membership_id, task_id, tipo,
                                      preguntado_en, vence_en)
           values (%s, %s, %s, %s, %s, %s)""",
        (ctx.quien.workspace_id, persona, task_id, tipo, ctx.ahora,
         cal.dentro_de_jornada(cal.sumar_habiles(ctx.ahora, 1))))


def retomar(ctx, pregunta_id: str) -> None:
    """Leda vuelve a hacer una pregunta que sigue sin contestar (la repite la escalera): es la
    abierta, y la que estaba abierta, si era otra, queda para después (un tema a la vez). Si la
    abierta salió en este mismo mensaje (un envío que junta varios avisos), ésa va primero y
    ésta queda para después, como al abrir."""
    vigente = actual(ctx.cur, ctx.quien.membership_id)
    otra = vigente is not None and str(vigente["id"]) != pregunta_id
    if otra and str(vigente["id"]) in ctx.preguntas_del_turno:
        _dejar_para_despues(ctx, pregunta_id)
    else:
        if otra:
            _dejar_para_despues(ctx, str(vigente["id"]))
        _que_sea_la_abierta(ctx, pregunta_id)
    if pregunta_id not in ctx.preguntas_del_turno:
        ctx.preguntas_del_turno.append(pregunta_id)


def cerrar(ctx, pregunta_id: str, cierre: str, detalle: dict[str, Any]) -> None:
    ctx.cur.execute(
        """update conversation_question
              set cerrada_en = %s, cierre = %s, cierre_detalle = %s
            where id = %s and cerrada_en is null""",
        (ctx.ahora, cierre, _json(detalle), pregunta_id))
    ctx.cur.execute(
        """update conversation_state set pregunta_abierta_id = null, actualizado_en = %s
            where membership_id = %s and pregunta_abierta_id = %s""",
        (ctx.ahora, ctx.quien.membership_id, pregunta_id))


def cerrar_de_tipo(ctx, tipo: str, task_id: str, cierre: str, detalle: dict[str, Any]) -> None:
    ctx.cur.execute("""select id from conversation_question
                        where membership_id = %s and tipo = %s and task_id = %s
                          and cerrada_en is null""",
                    (ctx.quien.membership_id, tipo, task_id))
    for fila in ctx.cur.fetchall():
        cerrar(ctx, str(fila["id"]), cierre, detalle)


def cerrar_las_de_la_tarea(ctx, task_id: str, cierre: str, detalle: dict[str, Any]) -> None:
    """Las preguntas sin cerrar sobre esa tarea, de cualquier persona: lo que esperaba algo de
    ella ya no espera nada (D8: después de decidir una entrega, el botón para verla seguía
    abierto para siempre). La que una persona tenía abierta deja de serlo."""
    ctx.cur.execute(
        """update conversation_question
              set cerrada_en = %s, cierre = %s, cierre_detalle = %s
            where task_id = %s and cerrada_en is null
        returning id, membership_id""", (ctx.ahora, cierre, _json(detalle), task_id))
    for fila in ctx.cur.fetchall():
        ctx.cur.execute(
            """update conversation_state set pregunta_abierta_id = null, actualizado_en = %s
                where membership_id = %s and pregunta_abierta_id = %s""",
            (ctx.ahora, fila["membership_id"], fila["id"]))


def cerrar_las_de_otras_personas(ctx, tipo: str, task_id: str, cierre: str,
                                 detalle: dict[str, Any], *, salvo: str | None = None) -> int:
    """Las preguntas sin cerrar de ese tipo sobre esa tarea, de cualquier persona salvo `salvo`,
    con su espera: lo que se le preguntaba ya no espera nada (la tarea se destrabó, o la destraba
    otra persona). La que una persona tenía abierta deja de serlo. Cuántas cerró."""
    ctx.cur.execute(
        """update conversation_question
              set cerrada_en = %s, cierre = %s, cierre_detalle = %s
            where task_id = %s and tipo = %s and cerrada_en is null
              and membership_id is distinct from %s::uuid
        returning id, membership_id""",
        (ctx.ahora, cierre, _json(detalle), task_id, tipo, salvo))
    cerradas = ctx.cur.fetchall()
    for fila in cerradas:
        ctx.cur.execute(
            """update conversation_state set pregunta_abierta_id = null, actualizado_en = %s
                where membership_id = %s and pregunta_abierta_id = %s""",
            (ctx.ahora, fila["membership_id"], fila["id"]))
    espera = TIPOS[tipo].espera
    if espera is not None:
        ctx.cur.execute(
            """update pending_reply set satisfecho_en = %s
                where task_id = %s and tipo = %s and satisfecho_en is null
                  and membership_id is distinct from %s::uuid""",
            (ctx.ahora, task_id, espera, salvo))
    return len(cerradas)


def cerrar_las_de_una_jugada(ctx, nombre: str, task_id: str, cierre: str,
                             detalle: dict[str, Any]) -> None:
    """Las preguntas sin cerrar que esperaban algo de esa jugada sobre esa tarea."""
    ctx.cur.execute("""select id from conversation_question
                        where membership_id = %s and task_id = %s and cerrada_en is null
                          and jugada ->> 'nombre' = %s""",
                    (ctx.quien.membership_id, task_id, nombre))
    for fila in ctx.cur.fetchall():
        cerrar(ctx, str(fila["id"]), cierre, detalle)


def contestar(ctx, nombre: str, tipos: Sequence[str], task_id: str) -> None:
    """Una jugada que se anotó sobre una tarea contesta las preguntas de los tipos que su
    ficha declara sobre esa tarea, la duda que esperaba esa jugada, si la tarea era una de
    sus opciones, y lo que Leda propuso, si era hacer eso sobre esa tarea (o sin tarea)."""
    ctx.cur.execute(
        """select q.id from conversation_question q
            where q.membership_id = %s and q.cerrada_en is null
              and ((q.tipo = any(%s) and q.task_id = %s)
                   or (q.tipo = %s and q.jugada ->> 'nombre' = %s
                       and exists (select 1 from conversation_option o
                                    where o.question_id = q.id
                                      and o.valor ->> 'tarea' = %s))
                   or (q.tipo = %s and q.jugada -> 'propone' ? %s
                       and (q.task_id is null or q.task_id = %s)))""",
        (ctx.quien.membership_id, list(tipos), task_id, CUAL_TAREA, nombre, task_id,
         PROPUESTA, nombre, task_id))
    for fila in ctx.cur.fetchall():
        cerrar(ctx, str(fila["id"]), "respondida", {"jugada": nombre, "tarea": task_id})


def marcar_en_la_lista(ctx, task_id: str) -> None:
    """Una jugada sobre una tarea de la lista de la cadencia la contesta en la lista (C-6): queda
    contada con el momento del turno, y la lista se cierra cuando están todas."""
    cur = ctx.cur
    cur.execute("""select * from conversation_question
                    where membership_id = %s and tipo = %s and cerrada_en is null
                      and jugada -> 'tareas' ? %s""",
                (ctx.quien.membership_id, COMO_VIENEN_SUS_TAREAS, str(task_id)))
    for q in cur.fetchall():
        jugada = dict(q["jugada"] or {})
        if str(task_id) in _contestadas(jugada):
            continue
        jugada["contestadas"] = [*(jugada.get("contestadas") or []),
                                 {"tarea": str(task_id), "en": ctx.ahora.isoformat()}]
        cur.execute("update conversation_question set jugada = %s where id = %s",
                    (_json(jugada), q["id"]))
        if not faltan_de_la_lista({**q, "jugada": jugada}):
            cerrar(ctx, str(q["id"]), "respondida", {"tareas": list(jugada.get("tareas") or [])})


def en_la_lista(cur, membership_id: str, task_id) -> bool:
    """Si la tarea está en una lista de la cadencia que la persona tiene sin cerrar: Leda le pidió
    su estado ahí."""
    cur.execute("""select 1 from conversation_question
                    where membership_id = %s and tipo = %s and cerrada_en is null
                      and jugada -> 'tareas' ? %s limit 1""",
                (membership_id, COMO_VIENEN_SUS_TAREAS, str(task_id)))
    return cur.fetchone() is not None


def faltan_de_la_lista(q) -> list[str]:
    """Las tareas de la lista que la persona todavía no contó."""
    jugada = q["jugada"] or {}
    ya = _contestadas(jugada)
    return [t for t in jugada.get("tareas") or [] if t not in ya]


def _contestadas(jugada: dict[str, Any]) -> set[str]:
    return {c["tarea"] for c in jugada.get("contestadas") or []}


def _la_lista_al_terminar(ctx) -> None:
    """Si la persona contestó en este turno otra parte de la lista después de que Leda preguntó
    una vez por las otras, la lista se cierra: no se pregunta otra vez (decisión 8)."""
    cur = ctx.cur
    cur.execute("""select * from conversation_question
                    where membership_id = %s and tipo = %s and cerrada_en is null
                      and (jugada ->> 'pregunto_por_las_otras')::boolean""",
                (ctx.quien.membership_id, COMO_VIENEN_SUS_TAREAS))
    for q in cur.fetchall():
        de_este_turno = [c for c in (q["jugada"] or {}).get("contestadas") or []
                         if c.get("en") == ctx.ahora.isoformat()]
        if de_este_turno:
            cerrar(ctx, str(q["id"]), "respondida",
                   {"tareas": list((q["jugada"] or {}).get("tareas") or []),
                    "sin_contestar": faltan_de_la_lista(q)})


def dejar_para_despues(ctx, pregunta_id: str) -> None:
    """La persona deja la pregunta para más tarde: no vuelve en este mismo mensaje."""
    _dejar_para_despues(ctx, pregunta_id)
    ctx.dejadas.append(pregunta_id)


def al_terminar_el_turno(ctx) -> dict[str, Any] | None:
    """Si no quedó una pregunta abierta, vuelve la más vieja de las que quedaron para
    después. Devuelve la única que se hace en la respuesta, descrita para la redacción, con
    `desde_antes` si no salió de este mensaje (volver a ella es retomarla, 9d)."""
    cur, persona = ctx.cur, ctx.quien.membership_id
    _la_lista_al_terminar(ctx)
    abierta = actual(cur, persona)
    if abierta is None:
        cur.execute("""select * from conversation_question
                        where membership_id = %s and cerrada_en is null
                          and para_despues_en is not null and not (id = any(%s::uuid[]))
                        order by abierta_en limit 1""", (persona, list(ctx.dejadas)))
        abierta = cur.fetchone()
        if abierta is None:
            return None
        _que_sea_la_abierta(ctx, str(abierta["id"]))
        _esperar_respuesta(ctx, abierta["tipo"], abierta["task_id"])
    if abierta["tipo"] == COMO_VIENEN_SUS_TAREAS and (abierta["jugada"] or {}).get("contestadas"):
        # La pregunta por las otras de la lista, una sola vez (decisión 8).
        cur.execute("""update conversation_question
                          set jugada = jugada || '{"pregunto_por_las_otras": true}'::jsonb
                        where id = %s""", (abierta["id"],))
    return {**describir(ctx, abierta),
            "desde_antes": str(abierta["id"]) not in ctx.preguntas_del_turno}


def describir(ctx, q) -> dict[str, Any]:
    """Una pregunta para la redacción: su tipo, su tarea y sus opciones (las tareas, por su
    título; van como botones)."""
    dicha: dict[str, Any] = {"tipo": q["tipo"]}
    if q["task_id"] is not None:
        dicha["tarea"] = tarea_dicha(ctx, q["task_id"])
    dicha.update(_lo_propuesto(q))
    dicha.update(_lo_mostrado(q))
    if q["tipo"] == COMO_VIENEN_SUS_TAREAS:
        dicha["de_la_lista"] = [tarea_dicha(ctx, t) for t in faltan_de_la_lista(q)]
    ops = opciones(ctx.cur, q["id"])
    if ops:
        dicha["opciones"] = [{"opcion": alias_de_opcion(o["orden"]), "etiqueta": o["etiqueta"],
                              **_tarea_de_opcion(ctx, o)} for o in ops]
    return dicha


def con_que_se_cerro(ctx, pregunta_id: str) -> dict[str, Any]:
    """Cómo y con qué se cerró una pregunta: lo que Leda dice ante un toque viejo."""
    ctx.cur.execute("select cerrada_en, cierre, cierre_detalle from conversation_question "
                    "where id = %s", (pregunta_id,))
    q = ctx.cur.fetchone()
    detalle = q["cierre_detalle"] or {}
    dicho: dict[str, Any] = {"cierre": q["cierre"],
                             "cuando": q["cerrada_en"].astimezone(
                                 ctx.calendario.zona).date().isoformat()}
    if detalle.get("tarea"):
        dicho["tarea"] = tarea_dicha(ctx, detalle["tarea"])
    if detalle.get("reemplazada"):
        # Una vista previa que dejó de valer porque cambió lo que mostraba: la reemplazó otra.
        dicho["reemplazada"] = True
    if detalle.get("ya_decidio"):
        # Se cerró porque quien aprueba ya decidió sobre la entrega de su tarea (D8).
        dicho["ya_decidio"] = True
    return dicho


def tarea_dicha(ctx, task_id) -> dict[str, str]:
    """Una tarea para los hechos: su alias si está entre las de la persona, y su título."""
    tarea = next((t for t in _todas(ctx) if t["id"] == str(task_id)), None)
    if tarea is not None:
        return {"alias": tarea["alias"], "titulo": tarea["titulo"]}
    ctx.cur.execute("select titulo from task where id = %s", (str(task_id),))
    fila = ctx.cur.fetchone()
    return {"titulo": fila["titulo"]} if fila else {}


def _tarea_de_opcion(ctx, opcion) -> dict[str, Any]:
    task_id = (opcion["valor"] or {}).get("tarea")
    if not task_id or _corre_otra_jugada(opcion):
        return {}
    return {"tarea": tarea_dicha(ctx, task_id)}


def _que_sea_la_abierta(ctx, pregunta_id: str) -> None:
    ctx.cur.execute("update conversation_question set para_despues_en = null where id = %s",
                    (pregunta_id,))
    ctx.cur.execute(
        """insert into conversation_state (membership_id, workspace_id, pregunta_abierta_id,
                                           actualizado_en)
           values (%s, %s, %s, %s)
           on conflict (membership_id) do update
              set pregunta_abierta_id = excluded.pregunta_abierta_id,
                  actualizado_en = excluded.actualizado_en""",
        (ctx.quien.membership_id, ctx.quien.workspace_id, pregunta_id, ctx.ahora))


def _dejar_para_despues(ctx, pregunta_id: str) -> None:
    """La pregunta queda para después. Una oferta opcional que ya se hizo (no en este mismo
    mensaje) no queda para después: si otro tema la deja de lado, es un no (ver el módulo)."""
    if pregunta_id not in ctx.preguntas_del_turno:
        ctx.cur.execute("select * from conversation_question where id = %s", (pregunta_id,))
        q = ctx.cur.fetchone()
        if es_opcional(q):
            caducar(ctx.cur, q, ctx.ahora)
            return
    ctx.cur.execute("""update conversation_question set para_despues_en = %s
                        where id = %s and cerrada_en is null""", (ctx.ahora, pregunta_id))
    ctx.cur.execute(
        """update conversation_state set pregunta_abierta_id = null, actualizado_en = %s
            where membership_id = %s and pregunta_abierta_id = %s""",
        (ctx.ahora, ctx.quien.membership_id, pregunta_id))


def _etiqueta(titulo: str) -> str:
    return titulo if len(titulo) <= _LARGO_ETIQUETA else titulo[:_LARGO_ETIQUETA - 1] + "…"


def _json(valor: Any) -> str:
    return json.dumps(valor, ensure_ascii=False, default=str)


# Para el cierre de una pregunta que escribe otro módulo (`pase.py`).
json_de = _json
