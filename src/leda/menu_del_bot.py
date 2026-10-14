"""El botón fijo del menú de cada bot (ADR 0024, decisión 2; prueba de la Mini App en el celular,
2026-10-14).

Al lado de donde se escribe, Telegram muestra el botón del menú del bot. Con `setChatMenuButton`
sin `chat_id` se fija el de todos los chats del bot: un botón `web_app` que abre la Mini App. El
del bot de un espacio dice "Tareas" y abre la puerta del equipo de ese espacio
(`/app/e/<espacio>/`); el del bot de administración dice "Administración" y abre esa puerta. Los
dos pasan por el lanzador (`/app/abrir/...`), que en Telegram de la computadora abre la web en el
navegador.

Mientras la web vive en un túnel, su dirección cambia: por eso se vuelve a fijar en cada arranque
del escuchador (`motor.escucha.Escucha.preparar`) y en cada registro de los webhooks
(`entrada.registrar_webhooks`), con la dirección del momento (`LEDA_BASE_URL`). Sin ella no se
fija ninguno, y nunca en silencio: queda un incidente. Nunca se registra el token del bot.
"""

from __future__ import annotations

from typing import Any, Callable

from . import config as configuracion

TEXTO_DEL_EQUIPO = "Tareas"
TEXTO_DE_LA_ADMINISTRACION = "Administración"
# El bot de administración, por su nombre en la configuración (`LEDA_BOT_TOKEN_ADMIN`).
SLUG_DE_LA_ADMINISTRACION = "admin"
ETAPA_MENU_DEL_BOT = "menu_del_bot"


def boton_del_menu(slug: str, base_url: str | None = None) -> dict[str, Any] | None:
    """El botón del menú del bot de `slug` (el de un espacio, o `admin`), o `None` sin la
    dirección pública."""
    from .despachador import (direccion_de_la_mini_app,
                              direccion_de_la_mini_app_de_administracion)

    # Se lee al llamar: la dirección del momento.
    base = configuracion.config.base_url if base_url is None else base_url
    if not base:
        return None
    if slug == SLUG_DE_LA_ADMINISTRACION:
        return {"type": "web_app", "text": TEXTO_DE_LA_ADMINISTRACION,
                "web_app": {"url": direccion_de_la_mini_app_de_administracion(base)}}
    return {"type": "web_app", "text": TEXTO_DEL_EQUIPO,
            "web_app": {"url": direccion_de_la_mini_app(base, slug, "inicio")}}


def fijar_el_menu(llamar: Callable[..., Any], slug: str) -> bool:
    """Fija el botón del menú de ese bot para todos sus chats (sin `chat_id`). `False` si no hay
    dirección pública; una falla de Telegram se levanta, sin el token (`pedido_telegram`)."""
    boton = boton_del_menu(slug)
    if boton is None:
        return False
    llamar("setChatMenuButton", menu_button=boton)
    return True


def registrar_que_no_se_fijo(conn, workspace_id: str | None, slug: str, motivo: str,
                             ahora_iso_dia: str) -> None:
    """El incidente de un menú que no se pudo fijar (uno por bot, motivo y día), nunca en
    silencio. Con la conexión administrativa: el del bot de administración no es de un espacio."""
    from .db import admin
    from .incidentes import registrar_incidente

    with admin(conn) as cur:
        registrar_incidente(
            cur, workspace_id,
            f"No se fijó el botón del menú del bot ({'administración' if slug == SLUG_DE_LA_ADMINISTRACION else 'equipo'}): "
            f"{motivo}. El chat sigue andando; el botón vuelve cuando se arranque con la dirección.",
            severidad="baja", etapa=ETAPA_MENU_DEL_BOT, avisar_admin=False,
            sin_avisar_porque="no impide conversar; se ve en la consola",
            clave=f"{ETAPA_MENU_DEL_BOT}:{slug}:{motivo}:{ahora_iso_dia}")
    conn.commit()


def causa_de_la_falla(falla: Exception) -> str:
    """Por qué no se fijó, en palabras y sin el token (revisión R2-except-mislabels-cause): que
    Telegram lo rechace, que no se le pueda hacer el pedido y que falle antes de llegar a Telegram
    no son lo mismo."""
    from .despachador import ErrorTelegram

    if isinstance(falla, ErrorTelegram):
        return "no se pudo hacer el pedido a Telegram"
    if isinstance(falla, RuntimeError) and "ok=false" in str(falla):
        return "Telegram no lo aceptó"
    return f"falló antes de pedírselo a Telegram ({type(falla).__name__})"


def registrar_sin_fallar(conn, workspace_id: str | None, slug: str, motivo: str,
                         ahora_iso_dia: str, imprimir: Callable[[str], Any] = print) -> bool:
    """`registrar_que_no_se_fijo`, sin que su propia falla corte a quien llama (el arranque del
    escuchador o el registro de los webhooks; revisión R3-incident-path-misclassified-and-
    unguarded): si la base no lo acepta, se dice en la consola, sólo con el tipo de la falla."""
    try:
        registrar_que_no_se_fijo(conn, workspace_id, slug, motivo, ahora_iso_dia)
        return True
    except Exception as falla:  # noqa: BLE001 -- el chat sigue sin el botón y sin el incidente
        try:
            conn.rollback()
        except Exception:  # noqa: BLE001 -- una conexión rota se reabre en el próximo uso
            pass
        imprimir(f"  ! tampoco se pudo registrar el incidente del botón del menú "
                 f"({type(falla).__name__}).")
        return False
