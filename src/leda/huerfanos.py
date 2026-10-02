"""Un mensaje cuyo turno murió no queda sin respuesta (T9-H19e, ADR 0013 regla 2).

El recibo de la fase 1 (`inbound_message`, confirmado antes del turno largo)
significa "recibido", no "respondido". T9-H19d recupera un turno muerto cuando
Telegram reentrega el mensaje pasada `VENTANA_TURNO_EN_CURSO`; si esa reentrega no
llega (Telegram dejó de reintentar, o el proceso murió y nadie reintenta), el
recibo quedaría sin respuesta para siempre. `barrer` es la red que lo cierra: cada
pasada de fondo (`ciclo.ejecutar_pasada`, la de `servir` y la de `escuchar`,
también la primera tras un arranque) busca los recibos viejos sin respuesta visible,
encola UN aviso neutro por cada uno (`NOTICIA_NEUTRA_INCIDENTE`, atado al recibo) y
deja el incidente. No vuelve a correr el turno con contenido viejo: la persona
reenvía si lo necesita.

Qué es un huérfano. Un recibo de esta pasada que:
- es más viejo que `VENTANA` (su turno ya no puede estar corriendo: un aviso falso
  a un turno vivo es peor que la demora) y más nuevo que `COTA` (lo que Telegram
  todavía podría reentregar; más atrás es historia, no un pendiente). Las dos
  edades se miden con el reloj de la base (`now()` en la misma consulta), igual que
  en `gateway._estado_de_entrega`: dos relojes desalineados no pueden avisar un
  turno vivo ni dejar pasar uno muerto (T9-H19g);
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
no bloqueante por espacio, tomado en la transacción de cada recibo, evita que dos
procesos avisen el mismo a la vez.

Cada recibo se atiende aparte (T9-H19g, T9-H19h):
- en su propia transacción, que corre ANTES de la del ciclo de fondo: se confirma y
  suelta sus candados enseguida, así una reentrega no espera al resto de la pasada
  (el candado de transacción sólo se suelta con el commit; soltarlo antes con uno de
  sesión reabriría la carrera). Si el aviso de uno falla (aun tras escribir algo) se
  revierte SÓLO ese recibo, se reporta con un incidente en otra transacción propia
  (`ETAPA_MENSAJE_HUERFANO_FALLO`, una vez por proceso y recibo, no en cada pasada; la
  marca vale sólo cuando el incidente ya se confirmó) y el barrido sigue con los demás. Los que ya fallaron van al final del lote, así no
  ocupan el lugar de los sanos, y se reintentan en cada pasada por si la causa
  desapareció;
- bajo el MISMO candado por mensaje que toma `gateway._estado_de_entrega`
  (`gateway.clave_de_candado_del_mensaje`), sin esperar: si la reentrega lo tiene, se
  deja para la pasada siguiente; y el recibo se vuelve a comprobar huérfano ya con el
  candado, porque entre elegirlo y tomarlo la reentrega pudo recuperarlo. Así el
  aviso neutro y la respuesta real nunca salen los dos.
"""

from __future__ import annotations

import time
from datetime import datetime

from .db import atar_al_entrante, espacio
from .gateway import COTA_REENTREGA as COTA
from .gateway import VENTANA_TURNO_EN_CURSO as VENTANA
from .gateway import clave_de_candado_del_mensaje
from .incidentes import (ETAPA_MENSAJE_HUERFANO, ETAPA_MENSAJE_HUERFANO_FALLO,
                         NOTICIA_NEUTRA_INCIDENTE, REFERENCIA_INBOUND_MESSAGE,
                         registrar_incidente)
from .respuesta_unica import sql_respondido
from .salida import enqueue_outbox

# Cuántos recibos se avisan por pasada: lo que queda sale en la siguiente.
LOTE_HUERFANOS = 50

# Los recibos cuyo aviso ya falló y ya se reportó (recibo -> instante monotónico): un
# incidente por recibo y proceso, no uno por pasada. `incident` no se puede leer con
# el rol del espacio, así que la deduplicación vive en memoria, como la del ciclo
# (`ciclo.SupresorDeRepetidos`); tras un reinicio se vuelve a reportar una vez.
_FALLIDOS: dict[str, float] = {}

_CANDIDATOS = f"""
    select i.id, i.chat_id, i.telegram_message_id, i.app_user_id, m.membership_id
      from inbound_message i
      left join integrante m
             on m.workspace_id = i.workspace_id
            and m.app_user_id = i.app_user_id and m.activo
     where i.workspace_id = %(ws)s
       and i.at <= now() - %(ventana)s and i.at > now() - %(cota)s
       and i.app_user_id is not null
       and (i.boton_callback is not null or i.texto is not null
            or i.telegram_message_id is not null)
       and not {sql_respondido("i")}
       and not exists (
            select 1 from inbound_message j
             where j.workspace_id = i.workspace_id and j.chat_id = i.chat_id
               and j.telegram_message_id = i.telegram_message_id
               and j.at > i.at)
       {{filtro}}
     order by {{orden}}
     limit %(lote)s
"""
_HUERFANOS = _CANDIDATOS.format(
    filtro="", orden="(i.id = any(%(fallidos)s::uuid[])), i.at")
_HUERFANO_POR_ID = _CANDIDATOS.format(filtro="and i.id = %(id)s", orden="i.at")


def _parametros(workspace_id: str, **mas) -> dict:
    return {"ws": workspace_id, "ventana": VENTANA, "cota": COTA, "lote": 1, **mas}


def barrer(conn, workspace_id: str, ahora: datetime,
           lote: int = LOTE_HUERFANOS) -> int:
    """Avisa a las personas de los recibos huérfanos de este espacio y devuelve a
    cuántas avisó. Corre ANTES de la transacción del ciclo de fondo, con su propia
    transacción acotada al espacio (`db.espacio`, RLS) por cada recibo: el aviso de
    uno se confirma y suelta su candado por mensaje enseguida, así una reentrega no
    espera a que termine el resto del ciclo (T9-H19h). `ahora` es el reloj de la
    aplicación: sólo fecha lo que se encola; qué recibo es huérfano lo decide el
    reloj de la base.

    El candado por espacio ya no cubre toda la pasada: se toma (sin esperar) dentro de
    la transacción de cada recibo. Dos procesos que barren a la vez se alternan por
    recibo, y el recheque bajo candado (`_avisar`) evita que avisen el mismo dos
    veces."""
    with espacio(conn, workspace_id) as cur:
        _olvidar_fallidos_viejos()
        cur.execute(_HUERFANOS, _parametros(workspace_id, lote=lote,
                                            fallidos=list(_FALLIDOS)))
        candidatos = cur.fetchall()
    conn.commit()
    avisados = 0
    for candidato in candidatos:
        entrante_id = str(candidato["id"])
        try:
            with espacio(conn, workspace_id) as cur:
                cur.execute(
                    "select pg_try_advisory_xact_lock(hashtextextended(%s, 0)) as ok",
                    (f"huerfanos:{workspace_id}",))
                if not cur.fetchone()["ok"]:
                    break              # otro proceso está barriendo este espacio
                avisado = _avisar(cur, workspace_id, entrante_id, ahora)
            conn.commit()
        except Exception as e:  # noqa: BLE001 -- se reporta y se sigue con el resto
            _revertir(conn)
            if conn.closed:
                raise
            _reportar_fallo(conn, workspace_id, candidato, e)
            continue
        _FALLIDOS.pop(entrante_id, None)
        avisados += avisado
    return avisados


def _revertir(conn) -> None:
    try:
        conn.rollback()
    except Exception:  # noqa: BLE001 -- la conexión rota se detecta con `conn.closed`
        pass


def _avisar(cur, workspace_id: str, entrante_id: str, ahora: datetime) -> bool:
    """Avisa un recibo (dentro de la transacción de quien llama, que la confirma
    o la revierte entera). `False` si lo deja:
    la reentrega tiene el candado de su mensaje o, ya con el candado, dejó de ser
    huérfano."""
    cur.execute("select chat_id, telegram_message_id from inbound_message "
                "where id = %s", (entrante_id,))
    fila = cur.fetchone()
    if fila is None:
        return False
    if fila["telegram_message_id"] is not None:
        cur.execute(
            "select pg_try_advisory_xact_lock(hashtextextended(%s, 0)) as ok",
            (clave_de_candado_del_mensaje(
                workspace_id, fila["chat_id"], fila["telegram_message_id"]),))
        if not cur.fetchone()["ok"]:
            return False               # la reentrega lo está atendiendo
    cur.execute(_HUERFANO_POR_ID, _parametros(workspace_id, id=entrante_id))
    h = cur.fetchone()
    if h is None:
        return False                   # ya lo respondió o lo recuperó la reentrega
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
    cur.execute("select set_config('leda.entrante_id', '', true)")
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
    return True


def _reportar_fallo(conn, workspace_id: str, candidato: dict,
                    error: Exception) -> None:
    """El aviso de un recibo falló y su transacción ya se revirtió: incidente (una vez
    por recibo y proceso) en su propia transacción y el barrido sigue. La marca de
    "ya reportado" se pone sólo DESPUÉS del commit del incidente: si éste se pierde,
    el recibo se reporta de nuevo. Si ni el incidente se puede escribir, se avisa por
    consola -- nunca en silencio -- y se reintenta la próxima pasada."""
    entrante_id = str(candidato["id"])
    if entrante_id in _FALLIDOS:
        return
    try:
        with espacio(conn, workspace_id) as cur:
            registrar_incidente(
                cur, workspace_id,
                "No se pudo avisar de un mensaje recibido sin respuesta (falló al "
                "escribir su aviso); se reintenta en cada pasada de fondo y el "
                "resto de los mensajes sigue.",
                severidad="alta", etapa=ETAPA_MENSAJE_HUERFANO_FALLO,
                referencia_tipo=REFERENCIA_INBOUND_MESSAGE, referencia_id=entrante_id,
                referencia_cruda=f"{type(error).__name__}: {error}"[:2000],
                chat_id=candidato["chat_id"],
                app_user_id=str(candidato["app_user_id"]))
        conn.commit()
    except Exception as e:  # noqa: BLE001 -- no se marca: se reintenta la próxima vez
        _revertir(conn)
        print(f"  ! no se pudo registrar el incidente del recibo huérfano "
              f"{entrante_id} ({type(e).__name__}); el aviso falló por "
              f"{type(error).__name__}")
        return
    _FALLIDOS[entrante_id] = time.monotonic()


def _olvidar_fallidos_viejos() -> None:
    """Acota la memoria de `_FALLIDOS`: una marca de más de `COTA` se olvida. Se pone
    al reportar, y el recibo tenía entonces a lo sumo `COTA` de edad; pasada otra
    `COTA` ya es más viejo que ella y no es candidato: la marca no sirve más."""
    limite = time.monotonic() - COTA.total_seconds()
    for entrante_id in [k for k, t in _FALLIDOS.items() if t < limite]:
        del _FALLIDOS[entrante_id]
