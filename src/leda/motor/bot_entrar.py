""""Entrar en la compu" por Telegram (ADR 0024, decisión 8; migración 0073).

La computadora muestra un QR con el enlace `t.me/<bot>?start=compu_<código>`. Al escanearlo,
Telegram abre el chat del bot de esa puerta y manda `/start compu_<código>`:

- **El bot del equipo** (`Recepcion.procesar`) busca el pedido pendiente de ese código, de su
  espacio, y le muestra a quien escribió en qué espacio y desde dónde se pidió, con el botón
  "Entrar en la compu" (para que nadie apruebe un QR ajeno sin darse cuenta). A quien no es del
  equipo no se le contesta, como a cualquier desconocido.
- **El bot de administración** (`administracion.atender_admin`) hace lo mismo para la puerta de
  administración, sólo a un administrador de plataforma.

Al tocar el botón (el callback `compu:<pedido>`), la base liga el pedido a quien tocó y lo marca
aprobado (`aprobar_pedido_de_entrada`, auditado); la computadora, que pregunta cada pocos
segundos, recibe su sesión. Los textos son del código, como la bienvenida: es un control de
seguridad, no una conversación, y no pasa por la IA. Salen por la cola de cada bot.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from ..db import admin, espacio
from ..despachador import PREFIJO_ENTRAR_EN_LA_COMPU, encolar_respuesta_admin
from ..entrar_con_telegram import (CODIGO, PUERTA_DE_ADMINISTRACION, PUERTA_DEL_EQUIPO,
                                   es_un_uuid, aprobar_pedido, ver_pedido)
from ..salida import enqueue_outbox

TEXTO_DEL_PEDIDO = ("Pediste entrar a Leda{donde} en una computadora: {desde}, a las {hora}. "
                    "Si fuiste vos, tocá «Entrar en la compu» y la computadora entra sola. Si no "
                    "fuiste vos, no toques nada.")
TEXTO_YA_NO_SIRVE = ("Ese código ya no sirve: venció o ya se usó. En la computadora, recargá la "
                     "página para ver uno nuevo.")
TEXTO_LISTO = "Listo: la computadora entra sola en unos segundos."
TEXTOS_DEL_RECHAZO = {
    "vencido": "Ese pedido venció. En la computadora, recargá la página para ver un QR nuevo.",
    "ya_aprobado": "Ya lo habías aprobado: la computadora entra sola.",
}
# La administración no es de un espacio: la hora del pedido se dice en la zona de la plataforma
# (inventario de lo configurable, `docs/product/plataforma-pendientes.md`).
ZONA_DE_LA_ADMINISTRACION = "America/Argentina/Buenos_Aires"
TEXTO_NO_SE_PUDO = ("No se pudo aprobar ese pedido. En la computadora, recargá la página para "
                    "ver un QR nuevo.")


def codigo_de(texto: str) -> str | None:
    """El código de un `/start compu_<código>`, o `None` si no es eso."""
    partes = (texto or "").split()
    if len(partes) != 2 or partes[0].split("@", 1)[0] != "/start":
        return None
    return partes[1] if CODIGO.match(partes[1]) else None


def pedido_del_toque(data: str) -> str | None:
    """El pedido de un toque de "Entrar en la compu", o `None`."""
    if not (data or "").startswith(PREFIJO_ENTRAR_EN_LA_COMPU):
        return None
    pedido = data[len(PREFIJO_ENTRAR_EN_LA_COMPU):]
    return pedido if es_un_uuid(pedido) else None


def _hora(cuando: datetime, zona: str) -> str:
    return cuando.astimezone(ZoneInfo(zona)).strftime("%H:%M")


def _texto_del_pedido(pedido: dict[str, Any], zona: str, *, con_espacio: bool) -> str:
    donde = f" de {pedido['espacio']}" if con_espacio and pedido.get("espacio") else ""
    return TEXTO_DEL_PEDIDO.format(donde=donde, desde=pedido["desde"],
                                   hora=_hora(pedido["pedido_en"], zona))


# --- El bot del equipo --------------------------------------------------------------------------

def _del_equipo(cur, telegram_user_id: int) -> str | None:
    cur.execute("""select membership_id from integrante
                    where telegram_user_id = %s and activo""", (telegram_user_id,))
    fila = cur.fetchone()
    return str(fila["membership_id"]) if fila else None


def _el_espacio(cur, workspace_id: str) -> dict[str, Any]:
    cur.execute("select slug, zona_horaria from workspace where id = %s", (workspace_id,))
    return cur.fetchone()


def mostrar_en_el_equipo(conn, workspace_id: str, codigo: str, telegram_user_id: int,
                         chat_id: int, message_id: int, ahora: datetime,
                         bot_id: int | None) -> bool:
    """`/start compu_<código>` en el bot del espacio. `True` si contestó."""
    with espacio(conn, workspace_id) as cur:
        persona = _del_equipo(cur, telegram_user_id)
        if persona is None:
            return False                       # un desconocido: no se le contesta
        ws = _el_espacio(cur, workspace_id)
        pedido = ver_pedido(cur, codigo, PUERTA_DEL_EQUIPO, ws["slug"])
        clave = f"motor:compu:{bot_id}:{chat_id}:{message_id}"
        if pedido is None:
            enqueue_outbox(cur, workspace_id=workspace_id, chat_id=chat_id,
                           text=TEXTO_YA_NO_SIRVE, dedupe_key=clave,
                           recipient_membership_id=persona, message_type="informativo",
                           is_response=True, scheduled_for=ahora)
        else:
            enqueue_outbox(cur, workspace_id=workspace_id, chat_id=chat_id,
                           text=_texto_del_pedido(pedido, ws["zona_horaria"], con_espacio=True),
                           dedupe_key=clave, recipient_membership_id=persona,
                           message_type="informativo", is_response=True, scheduled_for=ahora,
                           enlace_de_entrada_web=persona, destino_web="entrar_en_la_compu",
                           pedido_de_entrada=str(pedido["pedido_id"]))
    conn.commit()
    return True


def aprobar_en_el_equipo(conn, workspace_id: str, pedido_id: str, telegram_user_id: int,
                         chat_id: int, toque_id: str, ahora: datetime) -> bool:
    """El toque de "Entrar en la compu" en el bot del espacio. `True` si contestó."""
    with espacio(conn, workspace_id) as cur:
        persona = _del_equipo(cur, telegram_user_id)
        if persona is None:
            return False
        ws = _el_espacio(cur, workspace_id)
        resultado = aprobar_pedido(cur, pedido_id, PUERTA_DEL_EQUIPO, ws["slug"],
                                   telegram_user_id)
        enqueue_outbox(cur, workspace_id=workspace_id, chat_id=chat_id,
                       text=_texto_del_resultado(resultado),
                       dedupe_key=f"motor:compu:toque:{toque_id}",
                       recipient_membership_id=persona, message_type="informativo",
                       is_response=True, scheduled_for=ahora)
    conn.commit()
    return True


def _texto_del_resultado(resultado: dict[str, Any]) -> str:
    if resultado.get("ok"):
        return TEXTO_LISTO
    return TEXTOS_DEL_RECHAZO.get(resultado.get("motivo"), TEXTO_NO_SE_PUDO)


# --- El bot de administración -------------------------------------------------------------------

def mostrar_en_la_administracion(conn, quien_app_user_id: str, codigo: str, chat_id: int,
                                 message_id: int | None) -> str | None:
    """`/start compu_<código>` en el bot de administración, de un administrador de plataforma
    (ya identificado). Devuelve la respuesta encolada."""
    with admin(conn) as cur:
        pedido = ver_pedido(cur, codigo, PUERTA_DE_ADMINISTRACION, None)
        clave = f"respuesta-admin:{chat_id}:{message_id}"
        if pedido is None:
            aviso = encolar_respuesta_admin(cur, quien_app_user_id, chat_id, TEXTO_YA_NO_SIRVE,
                                            clave=clave)
        else:
            texto = _texto_del_pedido(pedido, ZONA_DE_LA_ADMINISTRACION,
                                      con_espacio=False).replace(
                "entrar a Leda", "entrar a la administración de Leda")
            aviso = encolar_respuesta_admin(cur, quien_app_user_id, chat_id, texto, clave=clave,
                                            boton="entrar_en_la_compu",
                                            pedido_de_entrada=str(pedido["pedido_id"]))
    conn.commit()
    return aviso


def aprobar_en_la_administracion(conn, quien_app_user_id: str, pedido_id: str,
                                 telegram_user_id: int, chat_id: int,
                                 toque_id: str) -> str | None:
    with admin(conn) as cur:
        resultado = aprobar_pedido(cur, pedido_id, PUERTA_DE_ADMINISTRACION, None,
                                   telegram_user_id)
        aviso = encolar_respuesta_admin(cur, quien_app_user_id, chat_id,
                                        _texto_del_resultado(resultado),
                                        clave=f"respuesta-admin:toque:{toque_id}")
    conn.commit()
    return aviso
