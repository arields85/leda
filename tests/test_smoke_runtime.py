from __future__ import annotations

import io
import threading
import time
from contextlib import redirect_stdout


class _Updates:
    def get(self, url, params=None):
        return self

    def raise_for_status(self):
        return None

    def json(self):
        return {"result": [{
            "update_id": 41,
            "message": {
                "message_id": 7,
                "text": "mensaje de prueba",
                "chat": {"id": 123},
                "from": {"id": 456, "first_name": "Nora"},
            },
        }]}


def test_listener_procesa_con_stdout_ascii_redirigido(monkeypatch):
    from prisma import local

    procesados = []
    monkeypatch.setattr(
        local, "procesar_update",
        lambda *args, **kwargs: procesados.append(args[2]))
    escucha = local.Escucha(
        object(), "equipo-prueba", "ws-prueba", "token-prueba",
        cliente=_Updates(), authority_conn=object())
    bytes_salida = io.BytesIO()
    salida_ascii = io.TextIOWrapper(bytes_salida, encoding="ascii", errors="strict")

    with redirect_stdout(salida_ascii):
        assert escucha.recibir(espera=0) == 1
    salida_ascii.flush()

    assert procesados[0]["update_id"] == 41
    assert b"Nora" in bytes_salida.getvalue()


def test_listener_preserva_update_unicode_aunque_la_consola_no_lo_represente(
        monkeypatch):
    from prisma import local

    update = _Updates().json()["result"][0]
    update["message"]["text"] = "señal Δ y válvula"
    procesados = []
    monkeypatch.setattr(
        local, "procesar_update",
        lambda *args, **kwargs: procesados.append(args[2]))
    escucha = local.Escucha(
        object(), "equipo-prueba", "ws-prueba", "token-prueba",
        cliente=_UpdatesUnicode(update), authority_conn=object())
    salida = io.TextIOWrapper(io.BytesIO(), encoding="ascii", errors="strict")

    with redirect_stdout(salida):
        escucha.recibir(espera=0)

    assert procesados == [update]
    assert procesados[0]["message"]["text"] == "señal Δ y válvula"


class _ChatActionHttp:
    def __init__(self, falla: bool = False) -> None:
        self.falla = falla
        self.llamadas: list[tuple[str, dict]] = []

    def post(self, url, json):
        self.llamadas.append((url, json))
        if self.falla:
            raise ConnectionError("fallo simulado")
        return object()


class _UpdatesUnicode(_Updates):
    def __init__(self, update):
        self.update = update

    def json(self):
        return {"result": [self.update]}


class _ChatActionBloqueado:
    def __init__(self):
        self.empezo = threading.Event()
        self.soltar = threading.Event()
        self.cerrado = threading.Event()

    def post(self, url, json):
        self.empezo.set()
        self.soltar.wait(5)

    def close(self):
        self.cerrado.set()


def test_typing_se_refresca_sin_enviar_mensaje_y_se_detiene():
    from prisma.despachador import mantener_chat_activo

    http = _ChatActionHttp()
    with mantener_chat_activo(
            "token-prueba", 123, cliente=http, intervalo=0.01):
        time.sleep(0.035)

    assert len(http.llamadas) >= 2
    assert all(url.endswith("/sendChatAction") for url, _ in http.llamadas)
    assert all(body == {"chat_id": 123, "action": "typing"}
               for _, body in http.llamadas)
    cantidad = len(http.llamadas)
    time.sleep(0.025)
    assert len(http.llamadas) == cantidad


def test_typing_limpia_el_hilo_si_telegram_falla():
    from prisma.despachador import mantener_chat_activo

    http = _ChatActionHttp(falla=True)
    nombre = "prisma-typing-prueba"
    try:
        with mantener_chat_activo(
                "token-prueba", 123, cliente=http, intervalo=0.01,
                nombre_hilo=nombre):
            time.sleep(0.02)
            raise RuntimeError("falla del procesamiento")
    except RuntimeError:
        pass

    assert http.llamadas
    assert not any(h.name == nombre for h in threading.enumerate())


def test_typing_cleanup_no_espera_indefinidamente_un_cliente_bloqueado():
    from prisma.despachador import mantener_chat_activo

    http = _ChatActionBloqueado()
    inicio = time.monotonic()
    with mantener_chat_activo(
            "token-prueba", 123, cliente=http, intervalo=0.01,
            espera_cierre=0.03):
        assert http.empezo.wait(0.2)
    duracion = time.monotonic() - inicio
    http.soltar.set()

    assert duracion < 0.2


def test_typing_owned_client_cierra_al_terminar_el_heartbeat(monkeypatch):
    from prisma import despachador

    http = _ChatActionBloqueado()
    monkeypatch.setattr("httpx.Client", lambda **kwargs: http)
    with despachador.mantener_chat_activo(
            "token-prueba", 123, intervalo=0.01, espera_cierre=0.02):
        assert http.empezo.wait(0.2)
    http.soltar.set()

    assert http.cerrado.wait(0.2)
    assert not any(h.name == "prisma-typing" for h in threading.enumerate())


def test_typing_client_creation_failure_degrades_to_noop(monkeypatch):
    from prisma import despachador

    monkeypatch.setattr(
        "httpx.Client",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("setup failed")),
    )
    processed = []

    with despachador.mantener_chat_activo("token-prueba", 123):
        processed.append(True)

    assert processed == [True]


def test_typing_thread_start_failure_degrades_and_closes_owned_client(monkeypatch):
    from prisma import despachador

    http = _ChatActionBloqueado()
    original_start = threading.Thread.start

    def start(thread):
        if thread.name == "prisma-typing":
            raise RuntimeError("thread failed")
        return original_start(thread)

    monkeypatch.setattr("httpx.Client", lambda **kwargs: http)
    monkeypatch.setattr(threading.Thread, "start", start)
    processed = []

    with despachador.mantener_chat_activo(
            "token-prueba", 123, espera_cierre=0.02):
        processed.append(True)

    assert processed == [True]
    assert http.cerrado.wait(0.2)
