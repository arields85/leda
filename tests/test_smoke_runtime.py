from __future__ import annotations

import threading
import time


class _ChatActionHttp:
    def __init__(self, falla: bool = False) -> None:
        self.falla = falla
        self.llamadas: list[tuple[str, dict]] = []

    def post(self, url, json):
        self.llamadas.append((url, json))
        if self.falla:
            raise ConnectionError("fallo simulado")
        return object()


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
    from leda.despachador import mantener_chat_activo

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
    from leda.despachador import mantener_chat_activo

    http = _ChatActionHttp(falla=True)
    nombre = "leda-typing-prueba"
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
    from leda.despachador import mantener_chat_activo

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
    from leda import despachador

    http = _ChatActionBloqueado()
    monkeypatch.setattr("httpx.Client", lambda **kwargs: http)
    with despachador.mantener_chat_activo(
            "token-prueba", 123, intervalo=0.01, espera_cierre=0.02, umbral=0):
        assert http.empezo.wait(0.2)
    http.soltar.set()

    assert http.cerrado.wait(0.2)
    assert not any(h.name == "leda-typing" for h in threading.enumerate())


def test_typing_client_creation_failure_degrades_to_noop(monkeypatch):
    from leda import despachador

    monkeypatch.setattr(
        "httpx.Client",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("setup failed")),
    )
    processed = []

    with despachador.mantener_chat_activo("token-prueba", 123):
        processed.append(True)

    assert processed == [True]


def test_typing_thread_start_failure_degrades_and_closes_owned_client(monkeypatch):
    from leda import despachador

    http = _ChatActionBloqueado()
    original_start = threading.Thread.start

    def start(thread):
        if thread.name == "leda-typing":
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
    ids de mensaje incrementales para `sendMessage`, como Telegram.

    Cada endpoint tiene su propio `threading.Event` (`esperar`) -- se marca
    SIEMPRE, incluso si esa llamada después falla, para esperar de forma
    determinista a que se intentó en vez de un `sleep` fijo adivinado
    (R3-004/R3-005, revisión del padre sobre el commit e2a094e)."""

    _ENDPOINTS = ("/sendMessageDraft", "/sendMessage", "/deleteMessage",
                 "/sendChatAction")

    def __init__(self, falla_en: frozenset[str] = frozenset()) -> None:
        self.llamadas: list[tuple[str, dict]] = []
        self.falla_en = falla_en
        self._siguiente_id = 900
        self._lock = threading.Lock()
        self._eventos = {endpoint: threading.Event() for endpoint in self._ENDPOINTS}

    def post(self, url, json=None):
        with self._lock:
            self.llamadas.append((url, json))
        for endpoint, evento in self._eventos.items():
            if url.endswith(endpoint):
                evento.set()
        if any(url.endswith(sufijo) for sufijo in self.falla_en):
            raise ConnectionError("fallo simulado")
        return _RespuestaIndicador(url, self)

    def urls(self, sufijo: str) -> list[dict]:
        return [cuerpo for url, cuerpo in self.llamadas if url.endswith(sufijo)]

    def esperar(self, endpoint: str, timeout: float = 1.0) -> bool:
        """Bloquea hasta que se INTENTÓ (llegó o falló) una llamada a
        `endpoint`, acotado a `timeout` -- nunca un `sleep` a ciegas."""
        return self._eventos[endpoint].wait(timeout)


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
    from leda.despachador import mantener_chat_activo

    http = _ClienteIndicador()
    with mantener_chat_activo(
            "token-prueba", 123, cliente=http, chat_type="private",
            umbral=1.0, intervalo=0.01):
        time.sleep(0.02)   # muy por debajo del umbral

    assert http.llamadas == []


def test_indicador_aparece_recien_despues_del_umbral():
    from leda.despachador import SEMILLA_INDICADOR, mantener_chat_activo

    http = _ClienteIndicador()
    with mantener_chat_activo(
            "token-prueba", 123, cliente=http, chat_type="private",
            umbral=0.02, intervalo=0.01):
        assert http.esperar("/sendMessageDraft")

    borradores = http.urls("/sendMessageDraft")
    assert len(borradores) == 1
    assert borradores[0]["text"] == SEMILLA_INDICADOR
    assert http.urls("/sendChatAction")


def test_borrador_se_retira_con_mensaje_transitorio_silencioso_y_borrado():
    from leda.despachador import SEMILLA_INDICADOR, mantener_chat_activo

    http = _ClienteIndicador()
    with mantener_chat_activo(
            "token-prueba", 123, cliente=http, chat_type="private",
            umbral=0.01, intervalo=0.01):
        assert http.esperar("/sendMessageDraft")
    # El retiro corre en el `finally` del `with`, ANTES de que este bloque
    # termine de salir -- para cuando llegamos acá ya se resolvió (o falló).

    envios = http.urls("/sendMessage")
    assert len(envios) == 1
    assert envios[0]["text"] == SEMILLA_INDICADOR
    assert envios[0]["disable_notification"] is True
    borrados = http.urls("/deleteMessage")
    assert len(borrados) == 1
    assert borrados[0]["message_id"] == 901   # primer id que devuelve el doble


def test_grupo_nunca_intenta_el_borrador_sólo_escribiendo():
    from leda.despachador import mantener_chat_activo

    http = _ClienteIndicador()
    with mantener_chat_activo(
            "token-prueba", 123, cliente=http, chat_type="group",
            umbral=0.01, intervalo=0.01):
        assert http.esperar("/sendChatAction")

    assert http.urls("/sendMessageDraft") == []
    assert http.urls("/sendMessage") == []
    assert http.urls("/deleteMessage") == []
    assert http.urls("/sendChatAction")


def test_fallo_al_mandar_y_retirar_el_borrador_se_intenta_una_vez_cada_uno_y_no_rompe_el_turno(
        capsys):
    """R3-004/R3-005: además de no romper el turno, las dos fallas (mandar
    Y retirar) tienen que haberse INTENTADO de verdad -- no sólo "no
    reventó" -- y cada una imprime exactamente una vez (mismo criterio que
    `_reportar_falla_indicador`: a lo sumo una vez por tipo y por turno)."""
    from leda.despachador import mantener_chat_activo

    http = _ClienteIndicador(falla_en=frozenset(
        {"/sendMessageDraft", "/sendMessage", "/deleteMessage"}))
    procesado = []
    with mantener_chat_activo(
            "token-prueba", 123, cliente=http, chat_type="private",
            umbral=0.01, intervalo=0.01):
        assert http.esperar("/sendMessageDraft")
        procesado.append(True)

    assert procesado == [True]   # nunca se rompió ni se propagó la falla
    # Las dos se intentaron de verdad, una vez cada una -- mandar el
    # borrador (falló) y retirarlo (también falló, en su propio `sendMessage`
    # transitorio; nunca llega a `deleteMessage`).
    assert len(http.urls("/sendMessageDraft")) == 1
    assert len(http.urls("/sendMessage")) == 1

    salida = capsys.readouterr().out
    lineas = salida.splitlines()
    assert len([l for l in lineas if "(borrador)" in l]) == 1
    assert len([l for l in lineas if "(retiro)" in l]) == 1


def test_draft_id_es_distinto_en_cada_activacion():
    from leda.despachador import mantener_chat_activo

    ids = []
    for _ in range(2):
        http = _ClienteIndicador()
        with mantener_chat_activo(
                "token-prueba", 123, cliente=http, chat_type="private",
                umbral=0.01, intervalo=0.01):
            assert http.esperar("/sendMessageDraft")
        borradores = http.urls("/sendMessageDraft")
        assert len(borradores) == 1   # nunca indexar sin probar que llegó
        ids.append(borradores[0]["draft_id"])

    assert ids[0] != ids[1]


def test_retiro_ya_ocurrio_cuando_el_llamador_manda_la_respuesta_real():
    """El retiro pasa adentro del `finally` del `with`: para cuando el
    llamador sigue con lo próximo (acá, un envío marcado aparte), el
    borrador ya no está (ADR 0011, decisión 3 -- "antes de los botones")."""
    from leda.despachador import mantener_chat_activo

    http = _ClienteIndicador()
    with mantener_chat_activo(
            "token-prueba", 123, cliente=http, chat_type="private",
            umbral=0.01, intervalo=0.01):
        assert http.esperar("/sendMessageDraft")
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
    from leda.despachador import mantener_chat_activo

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
    from leda.db import admin, espacio
    from leda.despachador import mantener_chat_activo

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


# ---------------------------------------------------------------------------
# R3-001 (revisión del padre sobre commit e2a094e): el retiro no puede
# llegar antes que el propio borrador.
# ---------------------------------------------------------------------------

class _RespuestaRetiroLento:
    def __init__(self, url: str, cliente: "_ClienteBorradorLento") -> None:
        self._url = url
        self._cliente = cliente

    def raise_for_status(self):
        return None

    def json(self):
        if self._url.endswith("/sendMessage"):
            self._cliente._siguiente_id += 1
            return {"ok": True, "result": {"message_id": self._cliente._siguiente_id}}
        return {"ok": True, "result": True}


class _ClienteBorradorLento:
    """`sendMessageDraft` queda bloqueado hasta que el propio caso de
    prueba lo suelta -- simula que la llamada sigue en vuelo justo cuando
    el turno termina, el escenario exacto de R3-001. Cada llamada registra
    si el borrador YA se había resuelto en ese momento -- la prueba de la
    invariante no mira el orden en que se registraron los pedidos (el de
    retiro nunca se bloquea, así que igual quedaría antes en la lista),
    sino si, cuando el de retiro se hizo, el del borrador ya había vuelto."""

    def __init__(self) -> None:
        self.llamadas: list[tuple[str, dict, bool]] = []
        self.borrador_en_curso = threading.Event()
        self.borrador_resuelto = threading.Event()
        self.soltar_borrador = threading.Event()
        self._siguiente_id = 900

    def post(self, url, json=None):
        ya_resuelto = self.borrador_resuelto.is_set()
        self.llamadas.append((url, json, ya_resuelto))
        if url.endswith("/sendMessageDraft"):
            self.borrador_en_curso.set()
            self.soltar_borrador.wait(5)
            self.borrador_resuelto.set()
        return _RespuestaRetiroLento(url, self)


def test_el_retiro_nunca_llega_antes_de_que_el_borrador_termine():
    """El hilo marca `activado` ANTES de llamar a `sendMessageDraft`
    (`despachador.py`, `ciclo`): un `join` que agotó `espera_cierre` no
    garantiza que esa llamada ya haya vuelto. Si el turno termina justo
    cuando el borrador recién empezaba a mandarse, y esa llamada es lenta,
    retirar de inmediato puede llegar a Telegram ANTES que el propio
    borrador -- el borrador queda visible."""
    from leda.despachador import mantener_chat_activo

    http = _ClienteBorradorLento()
    with mantener_chat_activo(
            "token-prueba", 123, cliente=http, chat_type="private",
            umbral=0.01, intervalo=0.05, espera_cierre=0.05):
        assert http.borrador_en_curso.wait(0.5)
        # Se suelta un poco después, desde otro hilo, para que la llamada
        # del borrador siga en vuelo cuando este bloque `with` empiece a
        # salir (el `finally` de `mantener_chat_activo` ya corre).
        threading.Timer(0.15, http.soltar_borrador.set).start()

    _, _, borrador_ya_resuelto_al_retirar = next(
        (u, j, r) for u, j, r in http.llamadas
        if u.endswith("/sendMessage") and not u.endswith("Draft"))
    assert borrador_ya_resuelto_al_retirar, (
        "el retiro llegó a Telegram antes de que el borrador terminara "
        "de intentarse (R3-001)")


# ---------------------------------------------------------------------------
# R3-002 (revisión del padre sobre commit e2a094e): una falla al REGISTRAR
# el incidente del retiro no puede abortar la transacción del turno.
# ---------------------------------------------------------------------------

def test_fallo_al_registrar_el_incidente_de_retiro_no_aborta_el_turno(
        conn, corework, monkeypatch, capsys):
    from leda import despachador
    from leda.db import admin, espacio
    from leda.despachador import mantener_chat_activo

    ws = corework.workspace_id
    http = _ClienteIndicador(falla_en=frozenset({"/sendMessage"}))

    def _registrar_que_rompe(cur, *a, **k):
        # Un error SQL real (no sólo una excepción de Python): deja la
        # transacción en curso abortada en PostgreSQL si nadie la aísla en
        # su propio SAVEPOINT.
        cur.execute("select 1/0")

    monkeypatch.setattr(despachador, "registrar_incidente", _registrar_que_rompe)

    with espacio(conn, ws) as cur:
        with mantener_chat_activo(
                "token-prueba", 123, cliente=http, chat_type="private",
                umbral=0.01, intervalo=0.01, cur=cur, workspace_id=ws):
            time.sleep(0.03)
        # Si `_reportar_falla_retiro` hubiera dejado la transacción
        # abortada (R3-002), esta consulta -- en la MISMA transacción --
        # ya fallaría con "current transaction is aborted".
        cur.execute("select 1 as uno")
        assert cur.fetchone()["uno"] == 1
    conn.commit()   # tampoco debe fallar

    salida = capsys.readouterr().out
    assert "no se pudo registrar el incidente" in salida
    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from incident where etapa = 'indicador_actividad'")
        assert cur.fetchone()["n"] == 0   # el registro rompió: no quedó fila
