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

**Sale por la cola, y el enlace se emite al mandarla** (migración 0054; la corrección chica de
la Fase C). La respuesta queda en `admin_notice` como respuesta (`es_respuesta`, sin incidente),
sin el enlace: la cola guarda el texto, y el token en claro no puede quedar en la base (ADR 0019,
7a). Si lleva el enlace, una marca dice de qué tarea y para quién (`admin_notice_enlace`), y el
despachador lo emite recién al mandarla (`despachador.despachar_avisos_admin`), como el enlace de
una persona del equipo (`message_outbox_enlace`): revalida el rol, la base guarda sólo el hash y,
si el envío falla, no queda ningún acceso y queda un incidente; se reintenta como todo aviso a la
administración. Se manda enseguida, por el mismo bot; un pedido que Telegram entrega dos veces
tiene una sola respuesta (la clave es el mensaje).
"""

from __future__ import annotations

from typing import Any, Callable

from ..autoridad import Canal, Denegado, identificar
from ..db import admin, espacio
from ..despachador import (Transporte, despachar_avisos_admin, encolar_respuesta_admin,
                           texto_error_seguro)
from ..incidentes import registrar_incidente
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
                  imprimir: Callable[[str], None] = print,
                  senal: Callable[[str], Any] | None = None) -> bool:
    """Un update del bot de administración: registra el chat de un administrador de plataforma
    y, en un chat privado, le contesta el pedido `/enlace`, `/start` (el botón
    "Administración", que abre la Mini App de la administración; ADR 0024, decisión 3) o
    `/start compu_<código>` (el QR de la computadora, con "Entrar en la compu"; decisión 8). Un
    toque de "Entrar en la compu" aprueba el pedido. `True` si era de un administrador."""
    if u.get("callback_query"):
        return _toque(conn, u["callback_query"], transporte, imprimir, senal)
    if not registrar_admin(conn, u, imprimir):
        return False
    mensaje = u.get("message") or {}
    partes = (mensaje.get("text") or "").split()
    chat = mensaje.get("chat") or {}
    comando = partes[0].split("@", 1)[0].lower() if partes else ""
    if chat.get("type") != "private" or transporte is None:
        return True
    if comando == "/start":
        return _start(conn, mensaje, chat, transporte, imprimir)
    if comando != COMANDO:
        return True
    quien = None
    try:
        # Se identifica otra vez, dentro de la guarda: si en el medio perdió el rol, no se le
        # contesta; si identificarlo falla, queda el incidente (revisión de la porción 5).
        with admin(conn) as cur:
            quien = identificar(cur, mensaje["from"]["id"], Canal.ADMINISTRACION, None)
        conn.commit()
        texto, de_la_tarea = _pedir_enlace(conn, partes[1:])
        aviso = _encolar(conn, quien.app_user_id, chat["id"], mensaje.get("message_id"), texto,
                         de_la_tarea)
        if aviso is not None:
            # Enseguida, por el mismo bot: el despachador emite el enlace al mandarla.
            with admin(conn) as cur:
                despachar_avisos_admin(cur, transporte, solo=[aviso])
            conn.commit()
        imprimir("  ← [admin] pedido de enlace atendido")
    except Denegado:
        conn.rollback()
        return True
    except Exception as e:  # noqa: BLE001 -- nunca en silencio: incidente y consola
        conn.rollback()
        imprimir(f"  ! [admin] no se pudo contestar el pedido de enlace: {texto_error_seguro(e)}")
        with admin(conn) as cur:
            registrar_incidente(
                cur, None, "No se pudo contestarle a un administrador de plataforma su pedido "
                "del enlace de una tarea por el bot de administración; no quedó ningún enlace.",
                severidad="baja", etapa=ETAPA, referencia_cruda=texto_error_seguro(e),
                app_user_id=quien.app_user_id if quien is not None else None,
                avisar_admin=False,
                sin_avisar_porque="falló el mismo canal de administración.")
        conn.commit()
    return True


TEXTO_DE_LA_ADMINISTRACION = "La administración de Leda: tocá «Administración» para abrirla."
SIN_ADMINISTRACION = ("La administración no está disponible por acá: falta la dirección "
                      "pública (LEDA_BASE_URL).")


def _start(conn, mensaje: dict[str, Any], chat: dict[str, Any], transporte: Transporte,
           imprimir: Callable[[str], None]) -> bool:
    """`/start`: el botón "Administración"; `/start compu_<código>`: el pedido de entrada de una
    computadora, con "Entrar en la compu". Nunca en silencio si falla."""
    from ..config import config
    from . import bot_entrar

    quien = None
    try:
        with admin(conn) as cur:
            quien = identificar(cur, mensaje["from"]["id"], Canal.ADMINISTRACION, None)
        conn.commit()
        codigo = bot_entrar.codigo_de(mensaje.get("text") or "")
        if codigo is not None:
            aviso = bot_entrar.mostrar_en_la_administracion(
                conn, quien.app_user_id, codigo, chat["id"], mensaje.get("message_id"))
        else:
            with admin(conn) as cur:
                aviso = encolar_respuesta_admin(
                    cur, quien.app_user_id, chat["id"],
                    TEXTO_DE_LA_ADMINISTRACION if config.base_url else SIN_ADMINISTRACION,
                    clave=f"respuesta-admin:{chat['id']}:{mensaje.get('message_id')}",
                    boton="administracion" if config.base_url else None)
            conn.commit()
        _despachar(conn, transporte, aviso)
        imprimir("  ← [admin] /start atendido")
    except Denegado:
        conn.rollback()
    except Exception as e:  # noqa: BLE001 -- nunca en silencio: incidente y consola
        _falla(conn, quien, e, imprimir, "su pedido de entrar a la administración")
    return True


def _toque(conn, toque: dict[str, Any], transporte: Transporte | None,
           imprimir: Callable[[str], None], senal: Callable[[str], Any] | None) -> bool:
    """Un toque en el bot de administración: sólo "Entrar en la compu", de un administrador de
    plataforma, en un chat privado."""
    from . import bot_entrar

    if senal is not None:
        try:
            senal(toque["id"])
        except Exception as e:  # noqa: BLE001 -- un acuse: si falla, el toque se atiende igual
            imprimir(f"  (no se pudo dar la señal del toque: {texto_error_seguro(e)})")
    chat = (toque.get("message") or {}).get("chat") or {}
    tg_user = (toque.get("from") or {}).get("id")
    pedido = bot_entrar.pedido_del_toque(str(toque.get("data") or ""))
    if pedido is None or tg_user is None or chat.get("type") != "private" or transporte is None:
        return False
    quien = None
    try:
        with admin(conn) as cur:
            quien = identificar(cur, tg_user, Canal.ADMINISTRACION, None)
        conn.commit()
        aviso = bot_entrar.aprobar_en_la_administracion(conn, quien.app_user_id, pedido,
                                                        tg_user, chat["id"], str(toque["id"]))
        _despachar(conn, transporte, aviso)
        imprimir("  ← [admin] tocó «Entrar en la compu»")
    except Denegado:
        conn.rollback()
        return False
    except Exception as e:  # noqa: BLE001 -- nunca en silencio: incidente y consola
        _falla(conn, quien, e, imprimir, "su pedido de entrar en la compu")
    return True


def _despachar(conn, transporte: Transporte, aviso: str | None) -> None:
    if aviso is not None:
        with admin(conn) as cur:
            despachar_avisos_admin(cur, transporte, solo=[aviso])
        conn.commit()


def _falla(conn, quien, e: Exception, imprimir: Callable[[str], None], que: str) -> None:
    conn.rollback()
    imprimir(f"  ! [admin] no se pudo contestar {que}: {texto_error_seguro(e)}")
    with admin(conn) as cur:
        registrar_incidente(
            cur, None, f"No se pudo contestarle a un administrador de plataforma {que} por el "
            "bot de administración.",
            severidad="baja", etapa=ETAPA, referencia_cruda=texto_error_seguro(e),
            app_user_id=quien.app_user_id if quien is not None else None,
            avisar_admin=False, sin_avisar_porque="falló el mismo canal de administración.")
    conn.commit()


def _pedir_enlace(conn, palabras: list[str]) -> tuple[str, dict[str, str] | None]:
    """El pedido: el texto de la respuesta y, si es el enlace de una tarea, de qué espacio y qué
    tarea (el enlace no va en el texto: lo agrega el despachador al mandarla)."""
    if len(palabras) < 2 or not que_nombra(" ".join(palabras[1:])):
        return USO, None
    slug, dicho = palabras[0], " ".join(palabras[1:])
    with admin(conn) as cur:
        cur.execute("select id::text id, nombre from workspace where slug = %s", (slug,))
        ws = cur.fetchone()
    conn.commit()
    if ws is None:
        return f"No hay ningún espacio «{slug}».", None
    with espacio(conn, ws["id"]) as cur:
        coinciden = tareas_que_nombra(cur, ws["id"], dicho)
    conn.commit()
    if not coinciden:
        return f"En {ws['nombre']} no hay ninguna tarea que se llame así.", None
    if len(coinciden) > 1:
        return _cual(ws, slug, coinciden), None
    [tarea] = coinciden
    from ..config import config         # se lee al pedir: la dirección puede cambiar
    if not config.base_url:
        return SIN_PAGINA, None
    return (f"La página de «{tarea['titulo']}» ({ws['nombre']}), sólo para vos. Cada vez que la "
            f"abras queda registrado.", {"espacio": ws["id"], "tarea": str(tarea["id"])})


def _encolar(conn, usuario: str, chat_id: int, message_id: int | None, texto: str,
             de_la_tarea: dict[str, str] | None) -> str | None:
    """La respuesta en la cola del bot de administración, sin el enlace
    (`despachador.encolar_respuesta_admin`). Una por mensaje del pedido: si Telegram lo entrega
    otra vez, ya tiene su respuesta (`None`)."""
    with admin(conn) as cur:
        aviso = encolar_respuesta_admin(
            cur, usuario, chat_id, texto, clave=f"respuesta-admin:{chat_id}:{message_id}",
            enlace_de=((de_la_tarea["espacio"], de_la_tarea["tarea"]) if de_la_tarea else None))
    conn.commit()
    return aviso


def _cual(ws: dict, slug: str, coinciden: list[dict]) -> str:
    """Las que coinciden, por su título y de quién son, y la pregunta de cuál."""
    renglones = [f"• {t['titulo']}" + (f" (de {t['responsable']})" if t["responsable"] else "")
                 for t in coinciden[:HASTA]]
    if len(coinciden) > HASTA:
        renglones.append(f"• y {len(coinciden) - HASTA} más")
    return (f"En {ws['nombre']} coinciden {len(coinciden)}:\n" + "\n".join(renglones)
            + f"\n¿Cuál? Volvé a escribir /enlace {slug} con más palabras del título.")

