"""Cada mensaje recibe exactamente una respuesta visible (T9-R2, ADR 0013 regla 2).

Al terminar de procesar un mensaje entrante, `controlar` mira lo que se encoló
como respuesta a ESE mensaje (`message_outbox.entrante_id`, migración 0021; el
gateway la deja puesta con `db.atar_al_entrante` y el valor por omisión de la
columna hace el resto) y garantiza la regla por estructura, no por el cuidado
de cada camino:

- Sin ninguna respuesta: sale el aviso neutro y queda un incidente. Un camino
  que ya encoló su propia disculpa o aviso cuenta como la respuesta.
- Con más de una respuesta independiente: queda una sola y el incidente dice
  qué se suprimió. Nunca se descarta sin registrarlo.

Qué es "una respuesta". Puede tener varias partes y un juego de botones. Las
filas que comparten `respuesta_grupo` son partes de una respuesta; sin grupo,
las partes de un texto partido (`salida.prepare_payload`, sufijo
`:part:NNN-of-MMM`) comparten el prefijo de su clave y cada llamada a
`enqueue_outbox` es su propia respuesta. Lo que un camino encola en varias
llamadas a propósito (el texto y aparte el mensaje con los botones) tiene que
pasar `grupo_respuesta`: si no, el control lo cuenta como dos respuestas y lo
dice en el incidente, que es la forma de encontrar el camino que falta marcar.

Cuál se conserva (determinista, documentado): la que ofrece botones a resolver
(`pending_action_id` o `intake_choice_set_id`, porque su acción quedaría sin
que nadie la pueda tocar); si ninguna o varias, la primera en salir (menor
`programado_para`, después la clave de deduplicación). Las demás pasan a
`descartado`. El saludo del día no es una respuesta aparte (se antepone al
despachar) ni el indicador de actividad (ADR 0011, no es una salida).

Los toques entran igual (T9-R4): cada toque deja una fila de `inbound_message`
(`gateway._registrar_toque`) que es su "mensaje entrante", y `gateway._toque` la
deja puesta con `atar_al_entrante` y llama a `controlar` al terminar. Un toque
absorbido por repetido (ADR 0013 regla 4) no procesa nada ni se controla: no es
una respuesta que falte.

Una parte de la respuesta que un camino sólo conoce a mitad de camino (el aviso de
lo que se dejó de lado, delante de lo que contesta el camino normal) se anota con
`dejar_nota`: `controlar` la agrega como una parte más de la MISMA respuesta que
conserva, y si el turno no dejó ninguna, la nota acompaña al aviso neutro.
"""

from __future__ import annotations

import re
from contextvars import ContextVar
from datetime import datetime, timedelta

from .incidentes import REFERENCIA_INBOUND_MESSAGE, registrar_incidente
from .salida import enqueue_outbox

ETAPA_SIN_RESPUESTA = "sin_respuesta"
ETAPA_RESPUESTA_DUPLICADA = "respuesta_duplicada"

_PARTE_DE_TEXTO_PARTIDO = re.compile(r":part:\d+-of-\d+$")

# Las notas del turno en curso (`dejar_nota`). Un turno corre entero en un mismo
# hilo y contexto; cada entrada (mensaje o toque) empieza con `limpiar_nota`.
_NOTAS: ContextVar[tuple[str, ...]] = ContextVar("notas_de_la_respuesta",
                                                 default=())


def dejar_nota(texto: str) -> None:
    """Anota algo que la respuesta de este turno tiene que decir además de lo suyo
    (T9-R4): sale como una parte más de la MISMA respuesta, delante de las demás."""
    _NOTAS.set(_NOTAS.get() + (texto,))


def limpiar_nota() -> None:
    """Empieza un turno sin notas (un turno que se revirtió no deja las suyas)."""
    _NOTAS.set(())


def grupo_de(fila: dict) -> str:
    """El nombre de la respuesta a la que pertenece una salida."""
    return fila["respuesta_grupo"] or _PARTE_DE_TEXTO_PARTIDO.sub(
        "", fila["dedupe_key"])


def respuestas_del_mensaje(cur, entrante_id: str, chat_id: int) -> list[list[dict]]:
    """Las respuestas visibles encoladas para el mensaje: una lista de filas por
    respuesta, en el orden en que salen. No cuenta lo descartado."""
    cur.execute(
        """select id, dedupe_key, respuesta_grupo, programado_para,
                  pending_action_id, intake_choice_set_id
             from message_outbox
            where entrante_id = %s and chat_id = %s and es_respuesta
              and estado <> 'descartado'
            order by programado_para, dedupe_key""",
        (entrante_id, chat_id))
    grupos: dict[str, list[dict]] = {}
    for fila in cur.fetchall():
        grupos.setdefault(grupo_de(fila), []).append(fila)
    return list(grupos.values())


def _ofrece_botones(grupo: list[dict]) -> bool:
    return any(f["pending_action_id"] is not None
               or f["intake_choice_set_id"] is not None for f in grupo)


def _describir(grupo: list[dict]) -> str:
    partes = len(grupo)
    return (f"salida {str(grupo[0]['id'])[:8]} ({partes} "
            f"{'parte' if partes == 1 else 'partes'}, "
            f"{'con' if _ofrece_botones(grupo) else 'sin'} botones)")


def controlar(cur, quien, *, workspace_id: str, chat_id: int, entrante_id: str,
              ahora: datetime, aviso_neutro: str,
              nota_de_la_respuesta: str | None = None) -> int:
    """Garantiza una respuesta visible para el mensaje `entrante_id`. Devuelve
    cuántas respuestas visibles quedaron (siempre una).

    `nota_de_la_respuesta` es algo que la respuesta tiene que decir además de lo
    suyo (hoy, que el adjunto todavía no se guarda, H15): sale como una parte
    más de la MISMA respuesta, delante de las demás."""
    notas = ([nota_de_la_respuesta] if nota_de_la_respuesta else []) + list(
        _NOTAS.get())
    limpiar_nota()
    respuestas = respuestas_del_mensaje(cur, entrante_id, chat_id)

    if not respuestas:
        enqueue_outbox(
            cur, workspace_id=workspace_id, chat_id=chat_id, text=aviso_neutro,
            recipient_membership_id=quien.membership_id, scheduled_for=ahora,
            dedupe_key=f"{workspace_id}:sin-respuesta:{entrante_id}",
            is_response=True)
        registrar_incidente(
            cur, workspace_id,
            "Un mensaje quedó sin ninguna respuesta: salió el aviso neutro.",
            severidad="alta", etapa=ETAPA_SIN_RESPUESTA,
            referencia_tipo=REFERENCIA_INBOUND_MESSAGE, referencia_id=entrante_id,
            chat_id=chat_id, app_user_id=quien.app_user_id, notificado_en=ahora)
        respuestas = respuestas_del_mensaje(cur, entrante_id, chat_id)
    elif len(respuestas) > 1:
        conservada = min(
            respuestas,
            key=lambda g: (not _ofrece_botones(g), g[0]["programado_para"],
                           g[0]["dedupe_key"]))
        suprimidas = [g for g in respuestas if g is not conservada]
        cur.execute(
            "update message_outbox set estado = 'descartado' where id = any(%s)",
            ([f["id"] for g in suprimidas for f in g],))
        criterio = ("la que ofrece botones" if _ofrece_botones(conservada)
                    and not all(_ofrece_botones(g) for g in respuestas)
                    else "la primera en salir")
        registrar_incidente(
            cur, workspace_id,
            f"Un mismo mensaje recibió {len(respuestas)} respuestas "
            f"independientes: se conservó {criterio} "
            f"({_describir(conservada)}) y se suprimieron "
            f"{len(suprimidas)}: {'; '.join(_describir(g) for g in suprimidas)}.",
            severidad="alta", etapa=ETAPA_RESPUESTA_DUPLICADA,
            referencia_tipo=REFERENCIA_INBOUND_MESSAGE, referencia_id=entrante_id,
            chat_id=chat_id, app_user_id=quien.app_user_id)
        respuestas = [conservada]

    (respuesta,) = respuestas
    if notas:
        enqueue_outbox(
            cur, workspace_id=workspace_id, chat_id=chat_id,
            text="\n\n".join(notas),
            recipient_membership_id=quien.membership_id,
            scheduled_for=respuesta[0]["programado_para"] - timedelta(milliseconds=1),
            dedupe_key=f"{workspace_id}:nota-de-respuesta:{entrante_id}",
            is_response=True, grupo_respuesta=grupo_de(respuesta[0]))
    return 1
