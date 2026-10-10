"""El bot de administración: el enlace de una tarea para un administrador de plataforma (ADR 0019,
7b; porción 5 de la C-3; `odd/tasks/fase-c.md`).

**El sombrero lo define el canal** (constitución §2). Un administrador de plataforma ve cualquier
tarea de un espacio con un enlace que pide por el bot de administración, nunca por el del
espacio: ahí se lo trata sólo por su rol en ese espacio (`enlace.pedir_enlace` y
`puede_ver_tarea` no saben nada de la plataforma).

**Un pedido cerrado, no una conversación.** El bot de administración no tiene IA ni motor:
registra el chat de quien le escribe (`recibir.registrar_admin`, para los avisos de incidentes) y
atiende un solo pedido, determinista:

    /enlace <espacio> <palabras del título o el nombre de quien la tiene>

El espacio es su identificador (`corework`); la tarea se busca con la misma regla que la jugada
`pedir_enlace` (`enlace.tareas_que_nombra`: cada palabra, entera, en el título o en el nombre de
quien la tiene), en la transacción de ese espacio, así que la base acota la búsqueda a él. Si
coinciden varias, las nombra y pregunta cuál; si ninguna, lo dice. Cualquier otro mensaje no
tiene respuesta. Sólo en un chat privado: un enlace nunca sale a un grupo.

**El enlace** queda atado al usuario de plataforma y a esa tarea de ese espacio
(`pagina_de_tarea.emitir_para_administrador`: sólo el hash en la base, auditado); vale mientras
tenga el rol y cada vez que lo abre queda en `audit_log` (la base, `leer_pagina_de_tarea`).

**Sale directo, no por una cola.** La respuesta del bot de administración no pasa por
`admin_notice` (la cola de los avisos de incidentes), porque esa cola guarda el texto y el token
en claro no puede quedar en la base (ADR 0019, 7a). Es la respuesta inmediata a un pedido del
administrador, como el acuse de un toque: se emite el acceso, se manda, y sólo si salió se
confirma; si no sale, no queda ningún acceso y la falla queda como incidente.
"""

from __future__ import annotations

from typing import Any, Callable

from ..autoridad import Canal, Denegado, identificar
from ..db import admin, espacio
from ..despachador import Transporte, texto_error_seguro
from ..incidentes import registrar_incidente
from ..pagina_de_tarea import emitir_para_administrador, enlace
from .enlace import que_nombra, tareas_que_nombra
from .recibir import registrar_admin

COMANDO = "/enlace"
ETAPA = "bot_de_administracion"
# Cuántas tareas se nombran, como mucho, cuando coinciden varias.
HASTA = 10

USO = ("Para pedir el enlace de una tarea: /enlace <espacio> <palabras del título o el nombre "
       "de quien la tiene>. Por ejemplo: /enlace corework tablero de marcos")
SIN_PAGINA = ("La página de las tareas no está disponible: falta la dirección pública "
              "(LEDA_BASE_URL).")


def atender_admin(conn, u: dict[str, Any], transporte: Transporte | None,
                  imprimir: Callable[[str], None] = print) -> bool:
    """Un update del bot de administración: registra el chat de un administrador de plataforma
    y, si es el pedido `/enlace` en un chat privado, le contesta. `True` si era de un
    administrador."""
    if not registrar_admin(conn, u, imprimir):
        return False
    mensaje = u.get("message") or {}
    partes = (mensaje.get("text") or "").split()
    chat = mensaje.get("chat") or {}
    if (not partes or partes[0].split("@", 1)[0].lower() != COMANDO
            or chat.get("type") != "private" or transporte is None):
        return True
    with admin(conn) as cur:
        quien = identificar(cur, mensaje["from"]["id"], Canal.ADMINISTRACION, None)
    conn.commit()
    try:
        _pedir_enlace(conn, quien.app_user_id, chat["id"], partes[1:], transporte)
        imprimir("  ← [admin] pedido de enlace atendido")
    except Denegado:
        return True
    except Exception as e:  # noqa: BLE001 -- nunca en silencio: incidente y consola
        conn.rollback()
        imprimir(f"  ! [admin] no se pudo contestar el pedido de enlace: {texto_error_seguro(e)}")
        with admin(conn) as cur:
            registrar_incidente(
                cur, None, "No se pudo contestarle a un administrador de plataforma su pedido "
                "del enlace de una tarea por el bot de administración; no quedó ningún enlace.",
                severidad="baja", etapa=ETAPA, referencia_cruda=texto_error_seguro(e),
                app_user_id=quien.app_user_id, avisar_admin=False,
                sin_avisar_porque="falló el mismo canal de administración.")
        conn.commit()
    return True


def _pedir_enlace(conn, usuario: str, chat_id: int, palabras: list[str],
                  transporte: Transporte) -> None:
    """El pedido: el espacio, la tarea y el enlace, o lo que falta. Si el mensaje no sale, la
    transacción que emitió el acceso se deshace y la excepción sube."""
    if len(palabras) < 2 or not que_nombra(" ".join(palabras[1:])):
        _mandar(transporte, chat_id, USO)
        return
    slug, dicho = palabras[0], " ".join(palabras[1:])
    with admin(conn) as cur:
        cur.execute("select id::text id, nombre from workspace where slug = %s", (slug,))
        ws = cur.fetchone()
    conn.commit()
    if ws is None:
        _mandar(transporte, chat_id, f"No hay ningún espacio «{slug}».")
        return
    with espacio(conn, ws["id"]) as cur:
        coinciden = tareas_que_nombra(cur, ws["id"], dicho)
    conn.commit()
    if not coinciden:
        _mandar(transporte, chat_id, f"En {ws['nombre']} no hay ninguna tarea que se llame así.")
        return
    if len(coinciden) > 1:
        _mandar(transporte, chat_id, _cual(ws, slug, coinciden))
        return
    [tarea] = coinciden
    from ..config import config         # se lee al pedir: la dirección puede cambiar
    if not config.base_url:
        _mandar(transporte, chat_id, SIN_PAGINA)
        return
    with admin(conn) as cur:
        token = emitir_para_administrador(cur, usuario, ws["id"], tarea["id"])
        if token is None:                  # dejó de ser administrador en el medio
            raise Denegado("No sos administrador de plataforma.")
        _mandar(transporte, chat_id,
                f"La página de «{tarea['titulo']}» ({ws['nombre']}), sólo para vos. Cada vez "
                f"que la abras queda registrado.\n"
                f"{enlace(config.base_url, token)}",
                sin_vista_previa=True)
    conn.commit()


def _cual(ws: dict, slug: str, coinciden: list[dict]) -> str:
    """Las que coinciden, por su título y de quién son, y la pregunta de cuál."""
    renglones = [f"• {t['titulo']}" + (f" (de {t['responsable']})" if t["responsable"] else "")
                 for t in coinciden[:HASTA]]
    if len(coinciden) > HASTA:
        renglones.append(f"• y {len(coinciden) - HASTA} más")
    return (f"En {ws['nombre']} coinciden {len(coinciden)}:\n" + "\n".join(renglones)
            + f"\n¿Cuál? Volvé a escribir /enlace {slug} con más palabras del título.")


def _mandar(transporte: Transporte, chat_id: int, texto: str, **mas: Any) -> None:
    transporte.enviar(chat_id, texto, None, **mas)
