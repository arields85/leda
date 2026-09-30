"""Un mensaje cuyo turno murió no queda sin respuesta (T9-H19e, ADR 0013 regla 2).

El recibo de la fase 1 (`inbound_message`, confirmado antes del turno largo)
significa "recibido", no "respondido". T9-H19d recupera un turno muerto cuando
Telegram reentrega el mensaje pasada `VENTANA_TURNO_EN_CURSO`; si esa reentrega no
llega (Telegram dejó de reintentar, o el proceso murió y nadie reintenta), el
recibo quedaría sin respuesta para siempre. `barrer` es la red que lo cierra: cada
pasada de fondo (`ciclo.ejecutar_ciclo_espacio`, la de `servir` y la de `escuchar`,
también la primera tras un arranque) busca los recibos viejos sin respuesta visible,
encola UN aviso neutro por cada uno (`NOTICIA_NEUTRA_INCIDENTE`, atado al recibo) y
deja el incidente. No vuelve a correr el turno con contenido viejo: la persona
reenvía si lo necesita.

Qué es un huérfano. Un recibo de esta pasada que:
- es más viejo que `VENTANA` (su turno ya no puede estar corriendo: un aviso falso
  a un turno vivo es peor que la demora) y más nuevo que `COTA` (lo que Telegram
  todavía podría reentregar; más atrás es historia, no un pendiente);
- por diseño debía tener respuesta: es un mensaje escrito o un toque que se atendió.
  Un toque absorbido por repetido (`gateway._registrar_toque(..., None)`) no trae
  texto, ni id de Telegram, ni botón, y por diseño no responde: se excluye. Un
  desconocido nunca deja recibo (`procesar_update` lo descarta antes de la fase 1);
- no tiene ninguna fila de respuesta, en cualquier estado
  (`respuesta_unica.sql_respondido`): un turno muerto no deja ninguna, y lo que el
  código descartó a propósito o falló al entregarse no es un turno muerto;
- no tiene un recibo más nuevo del mismo mensaje: si la reentrega lo recuperó, el
  recibo muerto queda atrás y sólo cuenta el último (con respuesta o sin ella).

Quien ya no es integrante activo del espacio no recibe ningún mensaje: queda el
incidente y una marca (una fila de respuesta `descartado`, sin destinatario, con la
clave del aviso) atada al recibo. Es la marca más simple que cierra el barrido sin
tabla ni columna nuevas: para el criterio único el recibo queda "respondido".

Idempotente por estructura: el aviso (o la marca) lleva una clave de deduplicación
por recibo y, una vez encolado, el recibo ya tiene su respuesta. Un candado de asesor
no bloqueante por espacio evita que dos procesos barran a la vez.
"""

from __future__ import annotations

from datetime import datetime

from .db import atar_al_entrante
from .gateway import COTA_REENTREGA as COTA
from .gateway import VENTANA_TURNO_EN_CURSO as VENTANA
from .incidentes import (ETAPA_MENSAJE_HUERFANO, NOTICIA_NEUTRA_INCIDENTE,
                         REFERENCIA_INBOUND_MESSAGE, registrar_incidente)
from .respuesta_unica import sql_respondido
from .salida import enqueue_outbox

# Cuántos recibos se avisan por pasada: lo que queda sale en la siguiente.
LOTE_HUERFANOS = 50

_HUERFANOS = f"""
    select i.id, i.chat_id, i.app_user_id, m.membership_id
      from inbound_message i
      left join integrante m
             on m.app_user_id = i.app_user_id and m.activo
     where i.workspace_id = %(ws)s
       and i.at <= %(hasta)s and i.at > %(desde)s
       and i.app_user_id is not null
       and (i.boton_callback is not null or i.texto is not null
            or i.telegram_message_id is not null)
       and not {sql_respondido("i")}
       and not exists (
            select 1 from inbound_message j
             where j.workspace_id = i.workspace_id and j.chat_id = i.chat_id
               and j.telegram_message_id = i.telegram_message_id
               and j.at > i.at)
     order by i.at
     limit %(lote)s
"""


def barrer(cur, workspace_id: str, ahora: datetime,
           lote: int = LOTE_HUERFANOS) -> int:
    """Avisa a las personas de los recibos huérfanos de este espacio (`cur` ya
    acotado a él por `db.espacio`) y devuelve a cuántas avisó."""
    cur.execute("select pg_try_advisory_xact_lock(hashtextextended(%s, 0)) as ok",
                (f"huerfanos:{workspace_id}",))
    if not cur.fetchone()["ok"]:
        return 0                       # otro proceso está barriendo este espacio
    cur.execute(_HUERFANOS, {"ws": workspace_id, "hasta": ahora - VENTANA,
                             "desde": ahora - COTA, "lote": lote})
    huerfanos = cur.fetchall()
    for h in huerfanos:
        entrante_id = str(h["id"])
        # El aviso es la respuesta a ese recibo (T9-R2); la atadura es sólo suya, no
        # de lo que se encole después en esta misma transacción.
        atar_al_entrante(cur, entrante_id)
        activo = h["membership_id"] is not None
        enqueue_outbox(
            cur, workspace_id=workspace_id, chat_id=h["chat_id"],
            text=NOTICIA_NEUTRA_INCIDENTE,
            recipient_membership_id=str(h["membership_id"]) if activo else None,
            scheduled_for=ahora, dedupe_key=f"{workspace_id}:huerfano:{entrante_id}",
            is_response=True, state="listo" if activo else "descartado")
        cur.execute("select set_config('prisma.entrante_id', '', true)")
        registrar_incidente(
            cur, workspace_id,
            "Un mensaje recibido no llegó a responderse (su turno murió y Telegram "
            "no lo reentregó)"
            + (": salió el aviso neutro." if activo else
               ", pero la persona ya no es integrante activa del espacio: no salió "
               "ningún mensaje."),
            severidad="alta", etapa=ETAPA_MENSAJE_HUERFANO,
            referencia_tipo=REFERENCIA_INBOUND_MESSAGE, referencia_id=entrante_id,
            chat_id=h["chat_id"], app_user_id=str(h["app_user_id"]),
            notificado_en=ahora if activo else None)
    return len(huerfanos)
