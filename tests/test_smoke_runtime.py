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
    # `umbral=0` (ADR 0011): esta prueba es sobre el refresco y la limpieza
    # del hilo, no sobre el umbral -- ése tiene sus propias pruebas más
    # abajo.
    with mantener_chat_activo(
            "token-prueba", 123, cliente=http, intervalo=0.01, umbral=0):
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
                nombre_hilo=nombre, umbral=0):
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
            espera_cierre=0.03, umbral=0):
        assert http.empezo.wait(0.2)
    duracion = time.monotonic() - inicio
    http.soltar.set()

    assert duracion < 0.2


def test_typing_owned_client_cierra_al_terminar_el_heartbeat(monkeypatch):
    from prisma import despachador

    http = _ChatActionBloqueado()
    monkeypatch.setattr("httpx.Client", lambda **kwargs: http)
    with despachador.mantener_chat_activo(
            "token-prueba", 123, intervalo=0.01, espera_cierre=0.02, umbral=0):
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


# ---------------------------------------------------------------------------
# Indicador diferido: "escribiendo…" + borrador nativo (ADR 0011, decisión 2)
# ---------------------------------------------------------------------------

class _ClienteIndicador:
    """Doble de `httpx.Client` para typing + borrador + su retiro. Devuelve
    ids de mensaje incrementales para `sendMessage`, como Telegram."""

    def __init__(self, falla_en: frozenset[str] = frozenset()) -> None:
        self.llamadas: list[tuple[str, dict]] = []
        self.falla_en = falla_en
        self._siguiente_id = 900

    def post(self, url, json=None):
        self.llamadas.append((url, json))
        if any(url.endswith(sufijo) for sufijo in self.falla_en):
            raise ConnectionError("fallo simulado")
        return _RespuestaIndicador(url, self)

    def urls(self, sufijo: str) -> list[dict]:
        return [cuerpo for url, cuerpo in self.llamadas if url.endswith(sufijo)]


class _RespuestaIndicador:
    def __init__(self, url: str, cliente: _ClienteIndicador) -> None:
        self._url = url
        self._cliente = cliente

    def raise_for_status(self):
        return None

    def json(self):
        if self._url.endswith("/sendMessage"):
            self._cliente._siguiente_id += 1
            return {"ok": True, "result": {"message_id": self._cliente._siguiente_id}}
        return {"ok": True, "result": True}


def test_indicador_no_aparece_si_la_respuesta_esta_lista_antes_del_umbral():
    from prisma.despachador import mantener_chat_activo

    http = _ClienteIndicador()
    with mantener_chat_activo(
            "token-prueba", 123, cliente=http, chat_type="private",
            umbral=1.0, intervalo=0.01):
        time.sleep(0.02)   # muy por debajo del umbral

    assert http.llamadas == []


def test_indicador_aparece_recien_despues_del_umbral(monkeypatch):
    from prisma.despachador import SEMILLA_INDICADOR, mantener_chat_activo

    http = _ClienteIndicador()
    with mantener_chat_activo(
            "token-prueba", 123, cliente=http, chat_type="private",
            umbral=0.02, intervalo=0.01):
        time.sleep(0.08)

    borradores = http.urls("/sendMessageDraft")
    assert len(borradores) == 1
    assert borradores[0]["text"] == SEMILLA_INDICADOR
    assert http.urls("/sendChatAction")


def test_borrador_se_retira_con_mensaje_transitorio_silencioso_y_borrado():
    from prisma.despachador import SEMILLA_INDICADOR, mantener_chat_activo

    http = _ClienteIndicador()
    with mantener_chat_activo(
            "token-prueba", 123, cliente=http, chat_type="private",
            umbral=0.01, intervalo=0.01):
        time.sleep(0.05)

    envios = http.urls("/sendMessage")
    assert len(envios) == 1
    assert envios[0]["text"] == SEMILLA_INDICADOR
    assert envios[0]["disable_notification"] is True
    borrados = http.urls("/deleteMessage")
    assert len(borrados) == 1
    assert borrados[0]["message_id"] == 901   # primer id que devuelve el doble


def test_grupo_nunca_intenta_el_borrador_sólo_escribiendo():
    from prisma.despachador import mantener_chat_activo

    http = _ClienteIndicador()
    with mantener_chat_activo(
            "token-prueba", 123, cliente=http, chat_type="group",
            umbral=0.01, intervalo=0.01):
        time.sleep(0.05)

    assert http.urls("/sendMessageDraft") == []
    assert http.urls("/sendMessage") == []
    assert http.urls("/deleteMessage") == []
    assert http.urls("/sendChatAction")


def test_fallo_al_mandar_o_retirar_el_borrador_no_rompe_el_turno():
    from prisma.despachador import mantener_chat_activo

    http = _ClienteIndicador(falla_en=frozenset(
        {"/sendMessageDraft", "/sendMessage", "/deleteMessage"}))
    procesado = []
    with mantener_chat_activo(
            "token-prueba", 123, cliente=http, chat_type="private",
            umbral=0.01, intervalo=0.01):
        time.sleep(0.03)
        procesado.append(True)

    assert procesado == [True]   # nunca se rompió ni se propagó la falla


def test_draft_id_es_distinto_en_cada_activacion():
    from prisma.despachador import mantener_chat_activo

    ids = []
    for _ in range(2):
        http = _ClienteIndicador()
        with mantener_chat_activo(
                "token-prueba", 123, cliente=http, chat_type="private",
                umbral=0.01, intervalo=0.01):
            time.sleep(0.03)
        ids.append(http.urls("/sendMessageDraft")[0]["draft_id"])

    assert ids[0] != ids[1]


def test_retiro_ya_ocurrio_cuando_el_llamador_manda_la_respuesta_real():
    """El retiro pasa adentro del `finally` del `with`: para cuando el
    llamador sigue con lo próximo (acá, un envío marcado aparte), el
    borrador ya no está (ADR 0011, decisión 3 -- "antes de los botones")."""
    from prisma.despachador import mantener_chat_activo

    http = _ClienteIndicador()
    with mantener_chat_activo(
            "token-prueba", 123, cliente=http, chat_type="private",
            umbral=0.01, intervalo=0.01):
        time.sleep(0.03)
    posicion_retiro = next(
        i for i, (url, _) in enumerate(http.llamadas) if url.endswith("/deleteMessage"))
    http.post("https://api.telegram.org/bottoken-prueba/sendMessage",
              json={"chat_id": 123, "text": "respuesta real con botones"})
    posicion_respuesta = len(http.llamadas) - 1

    assert posicion_retiro < posicion_respuesta


# ---------------------------------------------------------------------------
# Fallas del indicador: nunca en silencio, nunca en aluvión (revisión del
# padre sobre task #9)
# ---------------------------------------------------------------------------

def test_fallo_de_typing_se_imprime_una_vez_por_turno_y_no_rompe_el_turno(capsys):
    from prisma.despachador import mantener_chat_activo

    http = _ChatActionHttp(falla=True)
    procesado = []
    # `intervalo=0.01` sobre 0.05s de sueño deja varios reintentos fallidos
    # dentro del MISMO turno -- sólo el primero debe imprimir.
    with mantener_chat_activo(
            "token-prueba", 123, cliente=http, intervalo=0.01, umbral=0):
        time.sleep(0.05)
        procesado.append(True)

    assert procesado == [True]   # el turno no se vio afectado
    salida = capsys.readouterr().out
    lineas_typing = [l for l in salida.splitlines() if "(typing)" in l]
    assert len(lineas_typing) == 1
    assert "token-prueba" not in salida
    assert "https://" not in salida


def test_fallo_al_retirar_se_imprime_por_turno_y_registra_un_solo_incidente(
        conn, corework, capsys):
    from prisma.db import admin, espacio
    from prisma.despachador import mantener_chat_activo

    ws = corework.workspace_id
    # Sólo falla el mensaje transitorio de retiro (`/sendMessage`); el
    # borrador y el typing salen bien -- así la única falla es "retiro".
    http = _ClienteIndicador(falla_en=frozenset({"/sendMessage"}))

    for _ in range(2):   # dos turnos, la misma falla persistente
        with espacio(conn, ws) as cur:
            with mantener_chat_activo(
                    "token-prueba", 123, cliente=http, chat_type="private",
                    umbral=0.01, intervalo=0.01, cur=cur, workspace_id=ws):
                time.sleep(0.03)
        conn.commit()

    salida = capsys.readouterr().out
    lineas_retiro = [l for l in salida.splitlines() if "(retiro)" in l]
    assert len(lineas_retiro) == 2   # una por turno -- no se reprime entre turnos
    assert "token-prueba" not in salida
    assert "https://" not in salida

    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from incident where etapa = 'indicador_actividad'")
        # Deduplicado por proceso (mismo criterio que `saludo.reportar_falla`):
        # dos turnos con la misma falla, un solo incidente.
        assert cur.fetchone()["n"] == 1
