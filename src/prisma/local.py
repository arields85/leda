"""Modo local: escuchar por long polling en lugar de webhook.

Telegram entrega mensajes de dos maneras. El webhook necesita que tu máquina
sea alcanzable desde internet con HTTPS; el polling no necesita nada — el
proceso pregunta cada tanto si hay algo nuevo.

Para probar en tu computadora, polling. Al pasar a la VPS se cambia por
webhook y no se toca nada más: los dos caminos llaman a la misma función.

Este comando hace el circuito completo en un solo proceso: escucha, procesa,
dispara las cadencias vencidas, corre la escalera y despacha la cola (mismo
ciclo que usa `servir`, en `ciclo.py`). Es más simple de seguir que cuatro
servicios, y para dos o tres personas alcanza de sobra.
"""

from __future__ import annotations

import signal
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import NamedTuple
from urllib.parse import urlsplit

import httpx

from . import ciclo
from .calendario import Calendario
from .config import config, recargar_dotenv
from .db import admin, conectar_autoridad, espacio
from .despachador import Transporte, TransporteTelegram
from .gateway import (ETAPA_TOQUE_BOTON, ETAPA_TURNO_TEXTO, procesar_update,
                      reportar_incidente_no_manejado)
from .incidentes import registrar_incidente
from .reloj import ejecutar_cadencia

_seguir = True

# Cada cuánto `_obtener_transporte_admin` puede releer `.env` mientras el
# token todavía no aparece -- el listener corre cada unos segundos y sin
# este tope le pegaría al disco en cada pasada.
_RELECTURA_DOTENV_CADA = timedelta(minutes=1)

# Cada cuánto `_obtener_transporte_admin` puede volver a consultar
# `getWebhookInfo` sobre el bot de administración mientras esa consulta
# sigue sin resolverse a favor (falla, o el bot sigue detrás de un webhook)
# -- mismo motivo que `_RELECTURA_DOTENV_CADA`: sin este tope, cada vuelta
# del listener le pegaría a la API de Telegram para nada.
_RECONSULTA_WEBHOOK_ADMIN_CADA = timedelta(minutes=1)

# Etapa de la red de contención (T11) para un update del canal de
# administración que se escapó de `gateway.procesar_update` sin que nada
# específico lo atajara -- mismo criterio que `gateway.ETAPA_TURNO_TEXTO` /
# `ETAPA_TOQUE_BOTON`, pero acá no hay espacio: ver
# `_reportar_incidente_admin_no_manejado`.
ETAPA_MENSAJE_ADMIN = "mensaje_admin"


class _AdminBot(NamedTuple):
    """Token y transporte del bot de administración, cacheados juntos: un
    transporte sin su token no es representable (R2-003, revisión
    2026-09-28)."""
    token: str
    transporte: Transporte


def _imprimir(texto: str = "") -> None:
    """No deja caer el listener si la consola no representa Unicode."""
    salida = sys.stdout
    try:
        salida.write(texto + "\n")
    except UnicodeEncodeError:
        encoding = getattr(salida, "encoding", None) or "ascii"
        seguro = texto.encode(encoding, errors="backslashreplace").decode(encoding)
        salida.write(seguro + "\n")
    salida.flush()


def _error_sin_url(e: Exception) -> str:
    """Describe un error de red sin su mensaje: el de httpx incluye la URL,
    y la URL de la API de Telegram lleva el token del bot (`/bot<token>/`)."""
    respuesta = getattr(e, "response", None)
    if respuesta is not None:
        return f"{type(e).__name__} HTTP {respuesta.status_code}"
    return type(e).__name__


def _parar(*_):
    global _seguir
    _seguir = False
    _imprimir("\nCortando…")


def _reportar_incidente_admin_no_manejado(conn, *, chat_id: int | None,
                                          error: Exception) -> None:
    """Misma red de contención que `gateway.reportar_incidente_no_manejado`
    (decisión del usuario, 2026-09-25: un error nunca pasa en silencio), pero
    para el canal de administración -- esa función no sirve acá porque hace
    `if workspace_id is None: return` (usa `identificar_en_espacio` y
    `espacio()`, que necesitan un espacio activo) y un update del bot de
    administración no es de ningún espacio en particular.

    El incidente queda registrado global (`workspace_id=None`), mismo camino
    que ya cubre `incidentes.registrar_incidente` para el validador de
    invariantes -- y bajo rol `prisma_admin`, como el resto de lo que toca el
    canal de administración. Nunca deja escapar una excepción propia: si ni
    siquiera esto funciona, el aviso se pierde pero el ciclo que sigue
    escuchando no se cuelga."""
    resumen = (f"Excepción no manejada en '{ETAPA_MENSAJE_ADMIN}' "
              f"({type(error).__name__}).")
    try:
        with admin(conn) as cur:
            registrar_incidente(
                cur, None, resumen, severidad="alta",
                referencia_cruda=str(error)[:2000], etapa=ETAPA_MENSAJE_ADMIN,
                chat_id=chat_id)
        conn.commit()
    except Exception:  # noqa: BLE001
        try:
            conn.rollback()
        except Exception:  # noqa: BLE001
            pass


class Escucha:
    def __init__(self, conn, slug: str, workspace_id: str, token: str,
                 cliente: httpx.Client | None = None,
                 authority_conn=None, *, con_cadencias: bool = True) -> None:
        self.conn = conn
        self.slug = slug
        self.ws = workspace_id
        self.token = token
        self.http = cliente or httpx.Client(timeout=40)
        self.offset = 0
        self.offset_admin = 0
        self.transporte = TransporteTelegram(token, cliente=httpx.Client(timeout=15))
        self.authority_conn = authority_conn
        self.con_cadencias = con_cadencias
        # Piso de búsqueda de `ciclo.cadencias_vencidas`: nunca repone un
        # disparo anterior a que este proceso arrancara.
        self.arranque = datetime.now(timezone.utc)
        # Deduplica el reporte de una falla persistente (ciclo.reportar_fallo):
        # una vez mientras sigue igual, de nuevo si se recupera y vuelve a fallar.
        self._fallas = ciclo.SupresorDeRepetidos()
        self._admin_bot: _AdminBot | None = None
        self._ultimo_reintento_dotenv: datetime | None = None
        self._avisado_falta_token_admin = False
        self._ultimo_chequeo_webhook_admin: datetime | None = None
        self._avisado_webhook_admin_activo = False

    # -- ciclo -------------------------------------------------------------

    def una_vuelta(self, espera: int = 25) -> int:
        recibidos = self.recibir(espera)
        recibidos += self.recibir_admin()
        self.tareas_de_fondo()
        return recibidos

    def recibir(self, espera: int = 25) -> int:
        try:
            r = self.http.get(
                f"https://api.telegram.org/bot{self.token}/getUpdates",
                # callback_query va sí o sí: Telegram no entrega lo que no se
                # le pide, y sin esto los botones se dibujan pero el toque no
                # llega nunca. No da error: sencillamente no pasa nada.
                params={"offset": self.offset, "timeout": espera,
                        "allowed_updates": '["message","callback_query"]'})
            r.raise_for_status()
            updates = r.json().get("result", [])
        except Exception as e:  # noqa: BLE001
            _imprimir(f"  (sin conexión con Telegram: {_error_sin_url(e)})")
            time.sleep(5)
            return 0

        for u in updates:
            self.offset = u["update_id"] + 1
            origen = u.get("message") or u.get("callback_query") or {}
            quien = origen.get("from", {}).get("first_name", "?")
            if "callback_query" in u:
                _imprimir(f"  ← {quien}: [tocó un botón]")
            else:
                _imprimir(f"  ← {quien}: {origen.get('text', '')[:70]}")
            try:
                procesar_update(self.conn, self.slug, u,
                                authority_conn=self.authority_conn)
            except Exception as e:  # noqa: BLE001
                # Un mensaje que rompe no puede frenar la escucha. Decisión
                # del usuario, 2026-09-25: un error nunca pasa en silencio
                # -- `procesar_update` ya atrapa casi todo por su cuenta
                # (incidente + aviso neutro), así que llegar hasta acá es lo
                # que queda para una falla estructural previa a eso (p. ej.
                # un update malformado). `self.ws` es el único espacio que
                # escucha este proceso, así que se sabe igual sin haberlo
                # resuelto adentro de `procesar_update`.
                self.conn.rollback()
                mensaje_o_toque = origen if "callback_query" not in u else (
                    u["callback_query"].get("message") or {})
                chat_id = mensaje_o_toque.get("chat", {}).get("id")
                tg_user = origen.get("from", {}).get("id")
                etapa = ETAPA_TOQUE_BOTON if "callback_query" in u else ETAPA_TURNO_TEXTO
                reportar_incidente_no_manejado(
                    self.conn, workspace_id=self.ws, chat_id=chat_id,
                    tg_user=tg_user, error=e, etapa=etapa)
                _imprimir(f"  ! no se pudo procesar: {type(e).__name__}")
        return len(updates)

    def recibir_admin(self) -> int:
        """Sondea el bot de administración, aparte del bot del espacio que
        atiende `recibir` (T11: sin esto, nadie podía volverse "alcanzable"
        -- `db/esquema.sql`, `avisar_incidente_admin` -- en desarrollo local,
        porque nada leía sus updates fuera del webhook de `servir`).

        `timeout=0`: no bloqueante a propósito, para no sumarle latencia al
        long poll del bot del espacio (`recibir`, que ya espera hasta
        `espera` segundos por vuelta) -- esto sondea "hay algo ahora", no
        espera a que aparezca. Offset propio (`self.offset_admin`): son dos
        bots distintos, cada uno con su propia numeración de updates."""
        if self._obtener_transporte_admin() is None:
            return 0
        # `self._admin_bot` quedó cacheado por `_obtener_transporte_admin`
        # -- token y transporte juntos (`_AdminBot`, R2-003, revisión
        # 2026-09-28), así que si el transporte está resuelto el token
        # también lo está, por construcción.
        token_admin = self._admin_bot.token

        try:
            r = self.http.get(
                f"https://api.telegram.org/bot{token_admin}/getUpdates",
                params={"offset": self.offset_admin, "timeout": 0,
                        "allowed_updates": '["message"]'})
            r.raise_for_status()
            updates = r.json().get("result", [])
        except Exception as e:  # noqa: BLE001
            _imprimir("  (sin conexión con el bot de administración: "
                      f"{_error_sin_url(e)})")
            return 0

        for u in updates:
            self.offset_admin = u["update_id"] + 1
            mensaje = u.get("message") or {}
            quien = mensaje.get("from", {}).get("first_name", "?")
            _imprimir(f"  ← [admin] {quien}: {mensaje.get('text', '')[:70]}")
            try:
                procesar_update(self.conn, "admin", u,
                                authority_conn=self.authority_conn)
            except Exception as e:  # noqa: BLE001
                # Mismo criterio que en `recibir`: un update que rompe no
                # puede frenar la escucha, y nunca en silencio -- pero acá no
                # hay espacio (`_reportar_incidente_admin_no_manejado`,
                # no `gateway.reportar_incidente_no_manejado`).
                self.conn.rollback()
                chat_id = mensaje.get("chat", {}).get("id")
                _reportar_incidente_admin_no_manejado(
                    self.conn, chat_id=chat_id, error=e)
                _imprimir(f"  ! no se pudo procesar [admin]: {type(e).__name__}")
        return len(updates)

    def _obtener_transporte_admin(self, ahora: datetime | None = None) -> Transporte | None:
        """El bot de administración es opcional en desarrollo local: si
        `PRISMA_BOT_TOKEN_ADMIN` no está configurado, los avisos de
        incidente quedan encolados en `admin_notice` igual (los arma
        `incidentes.registrar_incidente`) y se entregan solos en cuanto se
        configure el token, sin perder nada mientras tanto.

        Nunca cachea la AUSENCIA del token -- sólo el transporte, una vez
        que lo encuentra y confirma que puede sondearlo (ver más abajo):
        `config._cargar_dotenv` sólo lee `.env` una vez, al importar el
        módulo, así que cachear la ausencia dejaría a este proceso sin ver
        un token agregado después hasta reiniciarlo. Por eso, mientras
        falta, cada pasada relee `.env` (`config.recargar_dotenv`, sin
        pisar lo que ya esté en el entorno) -- acotado a
        `_RELECTURA_DOTENV_CADA` para no pegarle al disco en cada vuelta del
        listener, que corre cada unos segundos.

        Antes de sondear, sólo CONSULTA `getWebhookInfo` (R1-001, revisión
        2026-09-28): borrar el webhook a ciegas le robaría los updates a un
        bot servido por webhook en otro lado, como el de producción. Si hay
        uno puesto, no lo toca ni sondea, avisa una vez y vuelve a consultar
        cada `_RECONSULTA_WEBHOOK_ADMIN_CADA`; una consulta fallida se avisa
        y se reintenta igual, nunca se da por buena.

        `ahora` es inyectable (mismo patrón que `tareas_de_fondo` /
        `correr_cadencia`) para que las pruebas del throttle de
        `_RECONSULTA_WEBHOOK_ADMIN_CADA` controlen el tiempo sin depender
        del reloj real ni pisar `_ultimo_chequeo_webhook_admin` a mano."""
        if self._admin_bot is not None:
            return self._admin_bot.transporte

        ahora = ahora or datetime.now(timezone.utc)
        if (self._ultimo_reintento_dotenv is None
                or ahora - self._ultimo_reintento_dotenv >= _RELECTURA_DOTENV_CADA):
            self._ultimo_reintento_dotenv = ahora
            recargar_dotenv()

        try:
            token = config.token_bot("admin")
        except LookupError:
            if not self._avisado_falta_token_admin:
                self._avisado_falta_token_admin = True
                _imprimir("  (sin PRISMA_BOT_TOKEN_ADMIN: los avisos de "
                          "administración quedan encolados hasta que se "
                          "configure)")
            return None

        if (self._ultimo_chequeo_webhook_admin is not None
                and ahora - self._ultimo_chequeo_webhook_admin
                    < _RECONSULTA_WEBHOOK_ADMIN_CADA):
            return None
        self._ultimo_chequeo_webhook_admin = ahora

        try:
            # 5s, no 15s: corre en el único hilo del listener -- una demora
            # larga acá le resta esa misma demora a `recibir` (R4-001,
            # revisión 2026-09-28).
            r = httpx.get(f"https://api.telegram.org/bot{token}/getWebhookInfo",
                         timeout=5)
            r.raise_for_status()
            cuerpo = r.json()
            if not cuerpo.get("ok"):
                raise RuntimeError("getWebhookInfo respondió ok=false")
            webhook_url = (cuerpo.get("result") or {}).get("url") or ""
        except Exception as e:  # noqa: BLE001
            _imprimir("  (no se pudo confirmar si el bot de administración "
                      "tiene un webhook puesto -- se reintenta en una "
                      f"vuelta posterior: {_error_sin_url(e)})")
            return None

        if webhook_url:
            if not self._avisado_webhook_admin_activo:
                self._avisado_webhook_admin_activo = True
                host = urlsplit(webhook_url).netloc or "otro servidor"
                _imprimir(
                    "  ! el bot de administración ya tiene un webhook puesto "
                    f"en '{host}' -- no se sondea acá para no robarle los "
                    "updates (probablemente `servir` en producción). Si es "
                    "un resto de una prueba local anterior sobre ESTE "
                    "bot, sacalo a mano (`deleteWebhook`, ver "
                    "PRUEBA-LOCAL.md) -- se detecta solo, dentro de un "
                    "minuto aproximadamente, sin reiniciar nada.")
            return None

        self._admin_bot = _AdminBot(
            token=token,
            transporte=TransporteTelegram(token, cliente=httpx.Client(timeout=15)))
        return self._admin_bot.transporte

    def _revertir(self) -> None:
        ciclo._revertir_best_effort(self.conn)

    def tareas_de_fondo(self, ahora: datetime | None = None) -> dict[str, int]:
        ahora = ahora or datetime.now(timezone.utc)
        try:
            with espacio(self.conn, self.ws) as cur:
                resumen = ciclo.ejecutar_ciclo_espacio(
                    cur, self.ws, self.transporte, ahora, self.arranque,
                    con_cadencias=self.con_cadencias)
            self.conn.commit()
            self._fallas.recuperada((self.ws, "tick"))
        except Exception as e:  # noqa: BLE001 -- una pasada rota no corta la escucha
            self._revertir()
            ciclo.reportar_fallo(
                self.conn, self._fallas, self.ws, "tick",
                f"Falló la pasada de fondo de '{self.slug}' "
                f"({type(e).__name__}).", e)
            _imprimir(f"  ! la pasada de fondo falló: {_error_sin_url(e)}")
            resumen = ciclo._resumen_vacio()

        # Una cadencia rota (cron inválido, o uno válido que falló al
        # ejecutarse) no frena a las demás: se aisló en
        # `ciclo.cadencias_vencidas`/`ciclo.ejecutar_ciclo_espacio`, y se
        # reporta acá con la misma implementación compartida que usa
        # `Ciclo.tick` (R2-002, revisión 2026-09-28+1).
        ciclo.reportar_cadencias_rotas(
            self.conn, self._fallas, self.ws, self.slug, resumen,
            imprimir=_imprimir)

        for _ in range(resumen["enviados"]):
            _imprimir("  → enviado")

        # El aviso a la administración (T28, Constitución §10) no está
        # acotado a este espacio -- puede venir de cualquiera, o de ninguno
        # -- así que se despacha aparte, bajo rol `prisma_admin`, y corre
        # igual aunque la pasada de este espacio haya fallado arriba. Desde
        # la unificación de G1d con esta unidad (decisión del usuario,
        # 2026-09-28), `ciclo.despachar_admin` también reconcilia y entrega
        # los avisos "🛠️ Administración" (`aviso_administrativo`) -- un solo
        # despacho hacia la administración, nunca dos.
        transporte_admin = self._obtener_transporte_admin()
        if transporte_admin is not None:
            try:
                resumen_admin = ciclo.despachar_admin(self.conn, transporte_admin, ahora)
            except Exception as e:  # noqa: BLE001
                self._revertir()
                ciclo.reportar_fallo(
                    self.conn, self._fallas, None, "admin",
                    f"Falló el aviso a la administración "
                    f"({type(e).__name__}).", e)
                _imprimir(f"  ! el aviso a la administración falló: "
                          f"{_error_sin_url(e)}")
                return resumen
            self._fallas.recuperada((None, "admin"))
            resumen["avisos_admin_enviados"] = resumen_admin["enviados"]
            resumen["avisos_admin_agotados"] = resumen_admin["agotados"]
            resumen["avisos_admin_incidentes_sin_registrar"] = (
                resumen_admin["incidentes_sin_registrar"])
            for _ in range(resumen_admin["enviados"]):
                _imprimir("  → aviso admin enviado")
            for _ in range(resumen_admin["agotados"]):
                # Nunca en silencio: agotó MAX_INTENTOS y quedó un incidente
                # (despachador.despachar_avisos_admin) -- visible acá también.
                _imprimir("  ! aviso admin agotado tras reintentos -- ver "
                          f"`python -m prisma incidentes {self.slug}`")
            for _ in range(resumen_admin["incidentes_sin_registrar"]):
                # Nunca en silencio (regla del proyecto): además de agotar
                # reintentos, el propio incidente no se pudo registrar
                # (punto de retorno de `despachar_avisos_admin`, R3-002) --
                # el aviso queda 'fallido' con su intento al día igual, y
                # `ultimo_error` en `admin_notice` lleva la marca para
                # inspeccionar en PostgreSQL.
                _imprimir("  ! aviso admin agotado sin poder registrar su "
                          "incidente -- ver `ultimo_error` en `admin_notice`")
        return resumen

    def correr_cadencia(self, nombre: str, ahora: datetime | None = None) -> int:
        """Dispara una cadencia a mano, para no esperar al lunes 09:15."""
        with espacio(self.conn, self.ws) as cur:
            cal = Calendario.desde_base(cur, self.ws)
            n = ejecutar_cadencia(cur, self.ws, nombre, cal, ahora)
        self.conn.commit()
        return n


def escuchar(conn, slug: str, workspace_id: str, *,
            con_cadencias: bool = True) -> None:
    global _seguir
    _seguir = True
    signal.signal(signal.SIGINT, _parar)

    token = config.token_bot(slug)
    if not config.authority_db_url:
        raise RuntimeError("Falta PRISMA_AUTHORITY_DB_URL.")
    authority_conn = conectar_autoridad(config.authority_db_url)
    e = Escucha(conn, slug, workspace_id, token,
                authority_conn=authority_conn, con_cadencias=con_cadencias)

    r = httpx.get(f"https://api.telegram.org/bot{token}/getMe", timeout=15).json()
    if not r.get("ok"):
        raise SystemExit("El token del bot no es válido.")
    usuario = r["result"]["username"]

    # Un webhook activo bloquea getUpdates: si quedó de una prueba anterior,
    # se saca.
    httpx.post(f"https://api.telegram.org/bot{token}/deleteWebhook", timeout=15)

    _imprimir(f"Escuchando como @{usuario} — espacio '{slug}'.")
    _imprimir("Ctrl+C para cortar.\n")

    while _seguir:
        e.una_vuelta()
