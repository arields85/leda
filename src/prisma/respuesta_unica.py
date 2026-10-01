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
conserva, y si el turno no dejó ninguna, la nota acompaña al aviso neutro. Una nota
de otro evento no sale en esa respuesta: deja un incidente (`nota_sin_respuesta`).
"""

from __future__ import annotations

import re
from contextvars import ContextVar
from datetime import datetime, timedelta

from .db import entrante_atado
from .incidentes import REFERENCIA_INBOUND_MESSAGE, registrar_incidente
from .salida import (PayloadValidationError, enqueue_outbox, margen_saludo,
                     prepare_payload)

ETAPA_SIN_RESPUESTA = "sin_respuesta"
ETAPA_RESPUESTA_DUPLICADA = "respuesta_duplicada"
ETAPA_NOTA_SIN_RESPUESTA = "nota_sin_respuesta"

_PARTE_DE_TEXTO_PARTIDO = re.compile(r":part:\d+-of-\d+$")

# Las notas del turno en curso (`dejar_nota`), cada una con el evento entrante al
# que quedó atado el turno que la dejó. Un turno corre entero en un mismo hilo y
# contexto. `controlar` sólo dice las de SU evento y descarta el resto (T9-R4b):
# la nota de un turno que se revirtió, o de una entrada cuyo camino no llamó a
# `limpiar_nota`, no puede salir en la respuesta de otra.
_NOTAS: ContextVar[tuple[tuple[str | None, str, bool], ...]] = ContextVar(
    "notas_de_la_respuesta", default=())


def dejar_nota(cur, texto: str, *, unida: bool = False) -> None:
    """Anota algo que la respuesta de este turno tiene que decir además de lo suyo
    (T9-R4): sale como una parte más de la MISMA respuesta, delante de las demás.
    Con `unida` va en el MISMO mensaje, delante del texto de la respuesta (el alta
    conducida: la persona lee un solo mensaje); si juntos no entran en un mensaje,
    sale como parte aparte del mismo grupo. Queda atada al evento entrante del turno
    (`db.atar_al_entrante`)."""
    _NOTAS.set(_NOTAS.get() + ((entrante_atado(cur), texto, unida),))


def limpiar_nota() -> None:
    """Empieza un turno sin notas (un turno que se revirtió no deja las suyas)."""
    _NOTAS.set(())


def grupo_de(fila: dict) -> str:
    """El nombre de la respuesta a la que pertenece una salida."""
    return fila["respuesta_grupo"] or _PARTE_DE_TEXTO_PARTIDO.sub(
        "", fila["dedupe_key"])


def sql_respondido(recibo: str) -> str:
    """Fragmento SQL: el recibo `recibo` (alias de una fila de `inbound_message`) ya
    tiene respuesta. Es el criterio único de "este turno no murió" (T9-H19f) que
    comparten `gateway._estado_de_entrega` y `huerfanos.barrer`.

    Cuenta una fila de respuesta en CUALQUIER estado. Lo que el código descarta a
    propósito antes de enviar (un juego de opciones reemplazado, una vista previa que
    ya no es vigente al despachar, el duplicado que `controlar` suprime) o lo que
    falló al entregarse (con su propio incidente) es la respuesta de un turno que
    vivió; un turno que murió no deja NINGUNA fila de respuesta (murió antes de
    encolar o su transacción se revirtió). No confundir con `respuestas_del_mensaje`,
    que cuenta las visibles para garantizar una sola."""
    return (f"exists (select 1 from message_outbox o where o.entrante_id = {recibo}.id"
            f" and o.chat_id = {recibo}.chat_id and o.es_respuesta)")


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


def _incidentes_de_notas_ajenas(cur, quien, workspace_id: str, chat_id: int,
                                eventos: list[str | None]) -> None:
    """Una nota que no es de este evento no sale en su respuesta, pero tampoco se
    pierde en silencio (T9-R4c): un incidente por evento, sin el texto de la nota
    (`incident` no lleva contenido de conversaciones), con el evento que la dejó
    como referencia cuando lo tiene."""
    for evento in dict.fromkeys(eventos):
        cantidad = eventos.count(evento)
        registrar_incidente(
            cur, workspace_id,
            f"{cantidad} {'nota' if cantidad == 1 else 'notas'} de un turno "
            "que no llegó a su respuesta se descartó"
            f"{'' if evento else ' (sin evento entrante)'}: no salió en la "
            "respuesta de otro evento.",
            severidad="alta", etapa=ETAPA_NOTA_SIN_RESPUESTA,
            referencia_tipo=REFERENCIA_INBOUND_MESSAGE if evento else None,
            referencia_id=evento, chat_id=chat_id, app_user_id=quien.app_user_id)


def _unir_al_mensaje(cur, primera: dict, unidas: list[str]) -> list[str]:
    """Antepone las notas `unidas` al texto del primer mensaje de la respuesta que se
    conserva, para que la persona lea uno solo. Devuelve las que no se pudieron unir
    (el mensaje ya salió o con ellas no entra en un mensaje): salen como parte
    aparte del mismo grupo."""
    cur.execute(
        "select id, cuerpo, destinatario_membership_id from message_outbox "
        "where id = %s and estado = 'listo' for update", (primera["id"],))
    fila = cur.fetchone()
    if fila is None:
        return unidas
    texto = "\n\n".join([*unidas, fila["cuerpo"]])
    try:
        prepare_payload(texto, dedupe_key=primera["dedupe_key"],
                        has_buttons=_ofrece_botones([primera]),
                        margen=margen_saludo(
                            personal=fila["destinatario_membership_id"] is not None))
    except PayloadValidationError:
        return unidas
    cur.execute("update message_outbox set cuerpo = %s where id = %s",
                (texto, fila["id"]))
    return []


def controlar(cur, quien, *, workspace_id: str, chat_id: int, entrante_id: str,
              ahora: datetime, aviso_neutro: str,
              nota_de_la_respuesta: str | None = None) -> int:
    """Garantiza una respuesta visible para el mensaje `entrante_id`. Devuelve
    cuántas respuestas visibles quedaron (siempre una).

    `nota_de_la_respuesta` es algo que la respuesta tiene que decir además de lo
    suyo (hoy, que el adjunto todavía no se guarda, H15): sale como una parte
    más de la MISMA respuesta, delante de las demás."""
    propias = [(texto, unida) for evento, texto, unida in _NOTAS.get()
               if evento == str(entrante_id)]
    notas = ([nota_de_la_respuesta] if nota_de_la_respuesta else []) + [
        texto for texto, unida in propias if not unida]
    unidas = [texto for texto, unida in propias if unida]
    ajenas = [evento for evento, _, _ in _NOTAS.get() if evento != str(entrante_id)]
    limpiar_nota()
    _incidentes_de_notas_ajenas(cur, quien, workspace_id, chat_id, ajenas)
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
    if unidas:
        sobrantes = _unir_al_mensaje(cur, respuesta[0], unidas)
        notas = sobrantes + notas
    if notas:
        enqueue_outbox(
            cur, workspace_id=workspace_id, chat_id=chat_id,
            text="\n\n".join(notas),
            recipient_membership_id=quien.membership_id,
            scheduled_for=respuesta[0]["programado_para"] - timedelta(milliseconds=1),
            dedupe_key=f"{workspace_id}:nota-de-respuesta:{entrante_id}",
            is_response=True, grupo_respuesta=grupo_de(respuesta[0]))
    return 1
