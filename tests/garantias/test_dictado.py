"""El dictado al cargar, con Gemini en el servidor (porción J2b de
`odd/tasks/plataforma-jerarquias.md`): las garantías en la entrada HTTP, con un Gemini de mentira
(un transporte de `httpx` falso; nunca el real).

- **La puerta:** sólo una sesión de administración vigente, con la protección contra otros sitios
  de la carga, y validada antes de leer el audio (J2-30); sólo audio de los tipos admitidos (415,
  con un incidente) y de hasta 10 MB (413); un espacio que no existe, 404; y unos pocos dictados a
  la vez por proceso (503, con un incidente). Nada de eso llega a Gemini.
- **Lo que recibe Gemini:** el audio tal cual, en línea, con su tipo; las instrucciones con los
  nombres de ese espacio (integrantes, áreas y objetivos abiertos) y nada de otro; la clave en su
  cabecera, nunca en la dirección. Sin pensar, temperatura 0 y un tope de salida.
- **Nunca en silencio:** sin clave o si Gemini no responde, un aviso humano y un incidente
  (`dictado_al_cargar`), saneado: ni el audio, ni el texto, ni la clave. Si no se entendió nada,
  "No te entendí", sin incidente (es una respuesta, no una falla), y la auditoría lo dice.
- **La auditoría** (`dictar_al_cargar`): quién dictó, en qué espacio, el tipo, el tramo de
  tamaño y si respondió; nunca el audio ni el texto. El audio no se guarda en ningún lado.
- **El candado de la web no espera a Gemini:** la llamada se hace fuera de él.
- **El plazo total es real** (J2-30): cada operación de la red espera, a lo sumo, lo que queda
  del plazo; las pruebas lo miden con un reloj de mentira, nunca con el reloj de verdad.
"""

from __future__ import annotations

import base64
import json
import threading

import httpcore
import httpx
import pytest

from leda import dictado as _dictado

from tests.garantias.test_carga_de_tareas import (  # noqa: F401
    _contar, _fila, _navegador_de_administracion, _navegador_del_equipo, _norte, _revocar,
    administradora, sesion, web)

# El cliente de verdad, antes de que la prueba ponga el de mentira (`gemini`).
_CLIENTE_DE_VERDAD = _dictado._cliente

CLAVE = "clave-de-mentira-0123456789"
AUDIO = b"OggS\x00audio de mentira\xff\x00\x01"
TEXTO_SIN_DICTADO = "No pude pasar el audio a texto ahora. Probá de nuevo en un rato o escribilo acá."
TEXTO_NO_SE_ENTENDIO = "No te entendí; probá de nuevo o escribilo acá."
DICHO = "Hay que colgar el estante del módem para el viernes, que lo haga Sam North."


def _camino(espacio_id: str) -> str:
    return f"/app/admin/api/espacios/{espacio_id}/dictado"


class GeminiDeMentira:
    """Lo que contesta Gemini, en orden; cada pedido queda guardado para mirarlo."""

    def __init__(self) -> None:
        self.respuestas: list = []
        self.pedidos: list[httpx.Request] = []
        self.al_llamar = None

    def __call__(self, pedido: httpx.Request) -> httpx.Response:
        self.pedidos.append(pedido)
        if self.al_llamar is not None:
            self.al_llamar()
        if not self.respuestas:
            # Nadie lo esperaba: la prueba lo mira en `pedidos`.
            return httpx.Response(500, json={"error": {"status": "INTERNAL"}})
        respuesta = self.respuestas.pop(0)
        if isinstance(respuesta, Exception):
            raise respuesta
        return respuesta

    def cuerpo(self, i: int = 0) -> dict:
        return json.loads(self.pedidos[i].content)


def _con_texto(texto: str) -> httpx.Response:
    return httpx.Response(200, json={"candidates": [
        {"content": {"role": "model", "parts": [{"text": texto}]}, "finishReason": "STOP"}]})


@pytest.fixture(autouse=True)
def gemini(monkeypatch):
    """Nunca el Gemini real: el cliente del dictado usa un transporte falso, y la clave es una de
    mentira (aunque el `.env` tenga la real)."""
    from leda import dictado

    falso = GeminiDeMentira()
    monkeypatch.setenv("LEDA_GEMINI_API_KEY", CLAVE)
    monkeypatch.setattr(dictado, "_cliente", lambda limite: httpx.Client(
        transport=httpx.MockTransport(falso), timeout=dictado.PLAZO_DEL_PROVEEDOR_S))
    return falso


class RelojDeMentira:
    """El reloj del plazo total (`dictado._reloj`): no avanza solo, avanza cuando la prueba dice."""

    def __init__(self) -> None:
        self.ahora = 1000.0

    def __call__(self) -> float:
        return self.ahora

    def avanzar(self, segundos: float) -> None:
        self.ahora += segundos


@pytest.fixture
def reloj(monkeypatch) -> RelojDeMentira:
    from leda import dictado

    falso = RelojDeMentira()
    monkeypatch.setattr(dictado, "_reloj", falso)
    return falso


def _dictar(navegador, espacio_id: str, audio: bytes = AUDIO,
            tipo: str = "audio/webm;codecs=opus", **cabeceras):
    return navegador.post(_camino(espacio_id), content=audio,
                          headers={"content-type": tipo, **cabeceras})


# --- El dictado, de punta a punta ---------------------------------------------------------------

def test_el_audio_vuelve_como_texto(web, conn, intake_world, administradora, gemini):
    navegador = _navegador_de_administracion(web, conn, administradora)
    gemini.respuestas.append(_con_texto(f"  {DICHO}\n"))
    r = _dictar(navegador, _norte(intake_world)["id"])
    assert r.status_code == 200, r.text
    assert r.json() == {"texto": DICHO}
    assert r.headers["cache-control"] == "no-store"
    # Nada se cargó: dictar no es cargar.
    assert _contar(conn, "task") == 0


def test_gemini_recibe_el_audio_tal_cual_con_su_tipo_y_la_clave_en_su_cabecera(
        web, conn, intake_world, administradora, gemini):
    from leda import dictado
    from leda.llm import GEMINI_BASE

    navegador = _navegador_de_administracion(web, conn, administradora)
    gemini.respuestas.append(_con_texto(DICHO))
    assert _dictar(navegador, _norte(intake_world)["id"]).status_code == 200
    (pedido,) = gemini.pedidos
    assert str(pedido.url) == f"{GEMINI_BASE}/models/{dictado.MODELO}:generateContent"
    assert dictado.MODELO == "gemini-3.8-flash"
    assert pedido.headers["x-goog-api-key"] == CLAVE
    assert CLAVE not in str(pedido.url)
    cuerpo = gemini.cuerpo()
    partes = cuerpo["contents"][0]["parts"]
    (audio,) = [p["inline_data"] for p in partes if "inline_data" in p]
    # El tipo sin sus parámetros (`codecs`), y el audio sin convertir.
    assert audio["mime_type"] == "audio/webm"
    assert base64.b64decode(audio["data"]) == AUDIO
    configuracion = cuerpo["generationConfig"]
    assert configuracion["temperature"] == 0
    assert configuracion["thinkingConfig"] == {"thinkingBudget": 0}
    assert 0 < configuracion["maxOutputTokens"] <= 2048


def test_las_instrucciones_favorecen_los_nombres_de_ese_espacio_y_de_ningun_otro(
        web, conn, intake_world, administradora, gemini):
    navegador = _navegador_de_administracion(web, conn, administradora)
    gemini.respuestas.append(_con_texto(DICHO))
    assert _dictar(navegador, _norte(intake_world)["id"]).status_code == 200
    instrucciones = " ".join(p["text"] for p in gemini.cuerpo()["contents"][0]["parts"]
                             if "text" in p)
    assert "transcrib" in instrucciones.lower()
    for persona in _norte(intake_world)["people"].values():
        assert persona["name"] in instrucciones
    assert "Field Services" in instrucciones
    assert "Reduce service delay 1" in instrucciones
    oeste = intake_world["west-studio"]
    for persona in oeste["people"].values():
        assert persona["name"] not in instrucciones
    assert "Reduce service delay 2" not in instrucciones


@pytest.mark.parametrize("tipo", ["audio/mp4", "audio/ogg;codecs=opus", "audio/mpeg",
                                  "audio/aac", "audio/wav", "AUDIO/WEBM"])
def test_los_tipos_de_audio_de_los_celulares_se_admiten(web, conn, intake_world, administradora,
                                                       gemini, tipo):
    navegador = _navegador_de_administracion(web, conn, administradora)
    gemini.respuestas.append(_con_texto(DICHO))
    assert _dictar(navegador, _norte(intake_world)["id"], tipo=tipo).status_code == 200
    (audio,) = [p["inline_data"] for p in gemini.cuerpo()["contents"][0]["parts"]
                if "inline_data" in p]
    assert audio["mime_type"] == tipo.split(";")[0].lower()


# --- La puerta --------------------------------------------------------------------------------

def test_sin_sesion_de_administracion_no_hay_dictado(web, conn, intake_world, administradora,
                                                    gemini):
    norte = _norte(intake_world)
    assert _dictar(web(), norte["id"]).status_code == 401
    equipo = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    assert _dictar(equipo, norte["id"]).status_code == 401
    navegador = _navegador_de_administracion(web, conn, administradora)
    for origen in ("https://otro.example", "null"):
        assert _dictar(navegador, norte["id"], origin=origen).status_code == 403
    assert _dictar(navegador, "00000000-0000-0000-0000-000000000000").status_code == 404
    assert _dictar(navegador, "no-es-un-id").status_code == 404
    assert gemini.pedidos == []
    assert _contar(conn, "audit_log", "accion = 'dictar_al_cargar'") == 0


def test_la_sesion_se_valida_antes_de_leer_el_audio(web, conn, intake_world, administradora,
                                                     gemini, monkeypatch):
    """J2-30: sin una sesión vigente (sin galleta, o con una que ya no vale) el pedido se rechaza
    sin leer el audio, que puede pesar hasta 10 MB."""
    from leda import web_app

    leidos = []
    leer = web_app._el_cuerpo_con_tope

    async def contando(request, tope):
        leidos.append(tope)
        return await leer(request, tope)

    monkeypatch.setattr(web_app, "_el_cuerpo_con_tope", contando)
    norte = _norte(intake_world)
    assert _dictar(web(), norte["id"]).status_code == 401
    navegador = _navegador_de_administracion(web, conn, administradora)
    _revocar(conn, administradora)
    assert _dictar(navegador, norte["id"]).status_code == 401
    assert leidos == []
    assert gemini.pedidos == []


@pytest.mark.parametrize("tipo, dice", [
    ("application/json", "application/json"), ("text/plain", "text/plain"),
    ("video/mp4", "video/mp4"), ("multipart/form-data; boundary=x", "multipart/form-data"),
    ("", "vacío"), ("audio/<script>", "ilegible")])
def test_lo_que_no_es_audio_no_se_manda(web, conn, intake_world, administradora, gemini, tipo,
                                        dice):
    """No llega a Gemini y, con una sesión vigente, deja un incidente con el tipo saneado (J2-30:
    un celular que mandaba el audio sin su tipo fallaba sin que la administración se enterara)."""
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _dictar(navegador, _norte(intake_world)["id"], tipo=tipo)
    assert r.status_code == 415
    assert gemini.pedidos == []
    incidente = _incidente(conn)
    assert incidente is not None
    assert str(incidente["workspace_id"]) == _norte(intake_world)["id"]
    assert incidente["referencia_cruda"] == f"content-type: {dice}"


def test_sin_sesion_un_tipo_que_no_es_audio_no_deja_incidente(web, conn, intake_world, gemini):
    assert _dictar(web(), _norte(intake_world)["id"], tipo="text/plain").status_code == 401
    assert _contar(conn, "incident", "etapa = 'dictado_al_cargar'") == 0


def test_hay_un_tope_de_dictados_a_la_vez(web, conn, intake_world, administradora, gemini,
                                          monkeypatch):
    """J2-30: unos pocos dictados a la vez por proceso; lleno, no se espera ni se lee el audio:
    el aviso de siempre y un incidente. Al terminar uno, su lugar se libera."""
    from leda import web_app

    assert 1 <= web_app.DICTADOS_A_LA_VEZ <= 8
    tope = threading.BoundedSemaphore(1)
    monkeypatch.setattr(web_app, "_DICTADOS", tope)
    navegador = _navegador_de_administracion(web, conn, administradora)
    norte = _norte(intake_world)
    assert tope.acquire(blocking=False)
    try:
        r = _dictar(navegador, norte["id"])
    finally:
        tope.release()
    assert r.status_code == 503
    assert r.json() == {"error": "sin_dictado", "texto": TEXTO_SIN_DICTADO}
    assert gemini.pedidos == []
    incidente = _incidente(conn)
    assert incidente is not None
    assert incidente["referencia_cruda"] == f"dictados_a_la_vez: {web_app.DICTADOS_A_LA_VEZ}"
    gemini.respuestas.append(_con_texto(DICHO))
    assert _dictar(navegador, norte["id"]).status_code == 200
    # Terminado, el lugar quedó libre otra vez.
    assert tope.acquire(blocking=False)
    tope.release()


def test_un_audio_de_mas_de_10_mb_no_se_manda(web, conn, intake_world, administradora, gemini):
    from leda import dictado

    assert dictado.TAMANO_MAXIMO == 10 * 1024 * 1024
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _dictar(navegador, _norte(intake_world)["id"], audio=b"x" * (dictado.TAMANO_MAXIMO + 1))
    assert r.status_code == 413
    assert gemini.pedidos == []


def test_sin_audio_no_se_manda(web, conn, intake_world, administradora, gemini):
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _dictar(navegador, _norte(intake_world)["id"], audio=b"")
    assert r.status_code == 422
    assert r.json()["texto"] == TEXTO_NO_SE_ENTENDIO
    assert gemini.pedidos == []


def test_una_sesion_cortada_mientras_responde_gemini_no_recibe_el_texto(
        web, conn, intake_world, administradora, gemini):
    navegador = _navegador_de_administracion(web, conn, administradora)
    gemini.respuestas.append(_con_texto(DICHO))
    gemini.al_llamar = lambda: _revocar(conn, administradora)
    r = _dictar(navegador, _norte(intake_world)["id"])
    assert r.status_code == 401
    assert DICHO not in r.text


def test_la_web_no_espera_a_gemini_con_su_candado(web, conn, intake_world, administradora,
                                                 gemini):
    from leda import web_app

    navegador = _navegador_de_administracion(web, conn, administradora)
    candado = []
    gemini.al_llamar = lambda: candado.append(web_app._WEB.locked())
    gemini.respuestas.append(_con_texto(DICHO))
    assert _dictar(navegador, _norte(intake_world)["id"]).status_code == 200
    assert candado == [False]


# --- Las fallas: un aviso humano y un incidente, saneado ----------------------------------------

def _incidente(conn) -> dict:
    return _fila(conn, "select * from incident where etapa = 'dictado_al_cargar'")


def _sin_nada_sensible(*textos: str | None) -> None:
    plano = " ".join(t or "" for t in textos)
    for sensible in (CLAVE, DICHO, AUDIO.decode("latin-1"),
                     base64.b64encode(AUDIO).decode("ascii"), "generativelanguage"):
        assert sensible not in plano


def test_sin_clave_un_aviso_y_un_incidente(web, conn, intake_world, administradora, gemini,
                                          monkeypatch):
    monkeypatch.delenv("LEDA_GEMINI_API_KEY", raising=False)
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _dictar(navegador, _norte(intake_world)["id"])
    assert r.status_code == 503
    assert r.json() == {"error": "sin_dictado", "texto": TEXTO_SIN_DICTADO}
    assert gemini.pedidos == []
    incidente = _incidente(conn)
    assert incidente is not None
    assert str(incidente["workspace_id"]) == _norte(intake_world)["id"]
    assert "SinClave" in incidente["referencia_cruda"]
    auditoria = _fila(conn, "select detalle from audit_log where accion = 'dictar_al_cargar'")
    assert auditoria["detalle"]["respondio"] is False
    assert auditoria["detalle"]["resultado"] == "sin_clave"


@pytest.mark.parametrize("respuesta, causa", [
    (httpx.Response(429, json={"error": {"code": 429, "status": "RESOURCE_EXHAUSTED",
                                         "message": f"cupo; clave {CLAVE}; dijo {DICHO}"}}),
     "status_429 RESOURCE_EXHAUSTED"),
    (httpx.Response(400, text=f"<html>{DICHO}</html>"), "status_400"),
    (httpx.ReadTimeout(f"tardó: https://generativelanguage.googleapis.com/?key={CLAVE}"),
     "ReadTimeout"),
    (httpx.ConnectError("sin red"), "ConnectError"),
    (httpx.Response(200, text="no es json"), "respuesta_ilegible"),
    (httpx.Response(200, json={"promptFeedback": {"blockReason": "OTHER"}}), "sin_candidatos"),
])
def test_si_gemini_no_responde_un_aviso_y_un_incidente_saneado(
        web, conn, intake_world, administradora, gemini, respuesta, causa):
    navegador = _navegador_de_administracion(web, conn, administradora)
    gemini.respuestas.append(respuesta)
    r = _dictar(navegador, _norte(intake_world)["id"])
    assert r.status_code == 502
    assert r.json() == {"error": "sin_dictado", "texto": TEXTO_SIN_DICTADO}
    _sin_nada_sensible(r.text)
    incidente = _incidente(conn)
    assert incidente is not None
    assert causa in incidente["referencia_cruda"]
    _sin_nada_sensible(incidente["referencia_cruda"], incidente["resumen_sanitizado"])
    auditoria = _fila(conn, "select detalle from audit_log where accion = 'dictar_al_cargar'")
    assert auditoria["detalle"]["resultado"] == "sin_respuesta"


def test_si_no_se_entendio_nada_lo_dice_sin_incidente(web, conn, intake_world, administradora,
                                                     gemini):
    navegador = _navegador_de_administracion(web, conn, administradora)
    gemini.respuestas.append(_con_texto("  \n "))
    r = _dictar(navegador, _norte(intake_world)["id"])
    assert r.status_code == 422
    assert r.json() == {"error": "no_se_entendio", "texto": TEXTO_NO_SE_ENTENDIO}
    assert _contar(conn, "incident", "etapa = 'dictado_al_cargar'") == 0
    auditoria = _fila(conn, "select detalle from audit_log where accion = 'dictar_al_cargar'")
    assert auditoria["detalle"]["respondio"] is True
    assert auditoria["detalle"]["resultado"] == "vacio"


# --- La deuda de la J2b (revisión `review-0f465303e17d9ce6`) ----------------------------------

def test_gemini_tiene_un_plazo_total_que_vence_antes_que_la_web(web, conn, intake_world,
                                                                administradora, gemini, reloj):
    """El plazo de `httpx` es por operación: una respuesta que llega de a gotas lo estira sin
    fin. El dictado tiene un plazo total, debajo de los 45 s de la web; vencido, es que Gemini no
    respondió (un aviso y un incidente), aunque la respuesta llegue después. Con un reloj de
    mentira (J2-30): la respuesta llega cuando el plazo ya pasó."""
    from leda import dictado

    assert dictado.PLAZO_DEL_PROVEEDOR_S <= dictado.PLAZO_TOTAL_S < 45
    gemini.al_llamar = lambda: reloj.avanzar(dictado.PLAZO_TOTAL_S + 1)
    gemini.respuestas.append(_con_texto(DICHO))
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _dictar(navegador, _norte(intake_world)["id"])
    assert DICHO not in r.text
    assert r.status_code == 502
    assert r.json() == {"error": "sin_dictado", "texto": TEXTO_SIN_DICTADO}
    assert "plazo_total" in _incidente(conn)["referencia_cruda"]
    auditoria = _fila(conn, "select detalle from audit_log where accion = 'dictar_al_cargar'")
    assert auditoria["detalle"]["resultado"] == "sin_respuesta"


def test_una_respuesta_dentro_del_plazo_llega(web, conn, intake_world, administradora, gemini,
                                             reloj):
    from leda import dictado

    gemini.al_llamar = lambda: reloj.avanzar(dictado.PLAZO_TOTAL_S - 1)
    gemini.respuestas.append(_con_texto(DICHO))
    navegador = _navegador_de_administracion(web, conn, administradora)
    assert _dictar(navegador, _norte(intake_world)["id"]).json() == {"texto": DICHO}


class FlujoDeMentira:
    """Una conexión de mentira: anota el plazo que recibe cada operación."""

    def __init__(self, plazos: list) -> None:
        self.plazos = plazos

    def read(self, max_bytes, timeout=None):
        self.plazos.append(("read", timeout))
        return b""

    def write(self, buffer, timeout=None):
        self.plazos.append(("write", timeout))

    def close(self):
        self.plazos.append(("close", None))

    def start_tls(self, ssl_context, server_hostname=None, timeout=None):
        self.plazos.append(("start_tls", timeout))
        return FlujoDeMentira(self.plazos)

    def get_extra_info(self, info):
        return None


class RedDeMentira:
    """La red de mentira debajo del plazo total: nunca sale a internet."""

    def __init__(self) -> None:
        self.plazos: list = []

    def connect_tcp(self, host, port, timeout=None, local_address=None, socket_options=None):
        self.plazos.append(("connect_tcp", timeout))
        return FlujoDeMentira(self.plazos)

    def connect_unix_socket(self, path, timeout=None, socket_options=None):
        self.plazos.append(("connect_unix_socket", timeout))
        return FlujoDeMentira(self.plazos)

    def sleep(self, seconds):
        self.plazos.append(("sleep", seconds))


def test_cada_operacion_de_la_red_espera_a_lo_sumo_lo_que_queda_del_plazo(reloj):
    """J2-30: el hilo del pedido no sobrevive al plazo total. Cada operación (conectar, el TLS,
    mandar, cada lectura) espera lo suyo o lo que queda del plazo, lo que sea menos; vencido,
    ninguna espera: falla en el momento, sin tocar la red."""
    from leda import dictado

    red = RedDeMentira()
    con_plazo = dictado._RedConPlazo(reloj.ahora + 10, red)
    flujo = con_plazo.connect_tcp("gemini", 443, timeout=5)
    reloj.avanzar(4)
    flujo = flujo.start_tls(None, server_hostname="gemini", timeout=30)
    reloj.avanzar(4)
    flujo.write(b"pedido", timeout=30)
    assert flujo.read(1024, timeout=30) == b""
    assert flujo.read(1024, timeout=None) == b""
    assert flujo.read(1024, timeout=1) == b""
    assert red.plazos == [("connect_tcp", 5), ("start_tls", 6), ("write", 2), ("read", 2),
                          ("read", 2), ("read", 1)]
    reloj.avanzar(2)
    for operacion, falla in ((lambda: flujo.read(1024, timeout=30), httpcore.ReadTimeout),
                             (lambda: flujo.write(b"x", timeout=30), httpcore.WriteTimeout),
                             (lambda: flujo.start_tls(None, timeout=30), httpcore.ConnectTimeout),
                             (lambda: con_plazo.connect_tcp("gemini", 443, timeout=5),
                              httpcore.ConnectTimeout)):
        with pytest.raises(falla):
            operacion()
    assert len(red.plazos) == 6
    flujo.close()
    assert red.plazos[-1] == ("close", None)


def test_el_cliente_del_dictado_usa_la_red_con_el_plazo(monkeypatch, reloj):
    """El cliente de verdad (`dictado._cliente`) manda todo por la red con el plazo: con una red de
    mentira debajo, conectar recibe lo que queda del plazo total (acá 2 s, menos que los 5 de la
    conexión). Nunca sale a internet."""
    from leda import dictado

    red = RedDeMentira()

    def no_conecta(host, port, timeout=None, local_address=None, socket_options=None):
        red.plazos.append(("connect_tcp", timeout))
        raise httpcore.ConnectError("sin red")

    red.connect_tcp = no_conecta
    # Sin un proxy del entorno, que `httpx` usaría en lugar del transporte.
    for variable in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "https_proxy", "http_proxy",
                     "all_proxy"):
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.setattr(dictado, "_cliente", _CLIENTE_DE_VERDAD)
    monkeypatch.setattr(dictado, "_red_de_verdad", lambda: red)
    monkeypatch.setattr(dictado, "GEMINI_BASE", "https://gemini.invalid")
    monkeypatch.setattr(dictado, "PLAZO_TOTAL_S", 2.0)
    with pytest.raises(dictado.ProveedorNoResponde) as falla:
        dictado.transcribir(AUDIO, "audio/webm", [])
    assert falla.value.motivo == "ConnectError"
    assert red.plazos == [("connect_tcp", 2.0)]


TEXTO_CORTADO = ("Pasé a texto sólo una parte: el dictado se cortó. Dictá lo que falta o "
                 "escribilo acá.")


def test_una_transcripcion_cortada_por_el_tope_lo_avisa(web, conn, intake_world, administradora,
                                                       gemini):
    """Si Gemini se detuvo por el tope de salida, el texto llega con un aviso de que se cortó
    (nunca en silencio, como si fuera todo); la auditoría lo dice y queda un incidente, por si el
    tope quedó corto."""
    navegador = _navegador_de_administracion(web, conn, administradora)
    gemini.respuestas.append(httpx.Response(200, json={"candidates": [
        {"content": {"role": "model", "parts": [{"text": DICHO}]},
         "finishReason": "MAX_TOKENS"}]}))
    r = _dictar(navegador, _norte(intake_world)["id"])
    assert r.status_code == 200, r.text
    assert r.json() == {"texto": DICHO, "aviso": TEXTO_CORTADO}
    auditoria = _fila(conn, "select detalle from audit_log where accion = 'dictar_al_cargar'")
    assert auditoria["detalle"]["resultado"] == "cortado"
    assert auditoria["detalle"]["respondio"] is True
    assert auditoria["detalle"]["caracteres"] == len(DICHO)
    incidente = _incidente(conn)
    assert incidente is not None and "MAX_TOKENS" in incidente["referencia_cruda"]
    _sin_nada_sensible(incidente["referencia_cruda"], incidente["resumen_sanitizado"])


# --- La auditoría -----------------------------------------------------------------------------

def test_la_auditoria_guarda_el_pedido_sin_el_audio_ni_el_texto(web, conn, intake_world,
                                                               administradora, gemini):
    norte = _norte(intake_world)
    navegador = _navegador_de_administracion(web, conn, administradora)
    gemini.respuestas.append(_con_texto(DICHO))
    assert _dictar(navegador, norte["id"], tipo="audio/mp4").status_code == 200
    fila = _fila(conn, """select workspace_id, actor_app_user_id, actor_kind, sujeto_tipo,
                                 sujeto_id, detalle, pack_hash, nucleo_hash
                            from audit_log where accion = 'dictar_al_cargar'""")
    assert str(fila["workspace_id"]) == norte["id"]
    assert str(fila["actor_app_user_id"]) == administradora
    assert (fila["actor_kind"], fila["sujeto_tipo"]) == ("persona", "workspace")
    assert fila["pack_hash"] and fila["nucleo_hash"]
    detalle = fila["detalle"]
    assert detalle["origen"] == "web" and detalle["sesion_de_administracion_id"]
    assert detalle["proveedor"] == "gemini" and detalle["modelo"] == "gemini-3.8-flash"
    assert detalle["tipo"] == "audio/mp4"
    assert detalle["tamano"] == "hasta_256_kb"
    assert detalle["respondio"] is True and detalle["resultado"] == "texto"
    assert detalle["caracteres"] == len(DICHO)
    _sin_nada_sensible(json.dumps(detalle, ensure_ascii=False))


def test_el_tramo_de_tamano():
    from leda import dictado

    assert dictado.tramo_de_tamano(1) == "hasta_256_kb"
    assert dictado.tramo_de_tamano(256 * 1024) == "hasta_256_kb"
    assert dictado.tramo_de_tamano(256 * 1024 + 1) == "hasta_1_mb"
    assert dictado.tramo_de_tamano(3 * 1024 * 1024) == "hasta_4_mb"
    assert dictado.tramo_de_tamano(dictado.TAMANO_MAXIMO) == "hasta_10_mb"


# --- J3-4: el dictado por la puerta del equipo, para Dirección ------------------------------------
#
# El mismo dictado, por `/app/api/dictado`, sólo para Dirección (como la ayuda del objetivo; la J4
# lo abre a los referentes): la sesión del equipo validada antes de leer el audio, los nombres de
# las opciones del objetivo de su espacio para Gemini, y la auditoría con su sesión.

EQUIPO = "/app/api/dictado"


def _dictar_por_el_equipo(navegador, audio: bytes = AUDIO, tipo: str = "audio/mp4", **cabeceras):
    return navegador.post(EQUIPO, content=audio, headers={"content-type": tipo, **cabeceras})


def test_direccion_dicta_por_la_puerta_del_equipo(web, conn, intake_world, gemini):
    from leda.db import admin

    norte = _norte(intake_world)
    with admin(conn) as cur:
        cur.execute("update area set referente_membership_id = %s where id = %s",
                    (norte["people"]["Taylor Quinn"]["membership_id"], norte["areas"]["field"]))
    conn.commit()
    direccion = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    gemini.respuestas.append(_con_texto(DICHO))
    r = _dictar_por_el_equipo(direccion)
    assert r.status_code == 200, r.text
    assert r.json() == {"texto": DICHO}
    instrucciones = json.dumps(gemini.cuerpo(), ensure_ascii=False)
    assert "Taylor Quinn 1" in instrucciones
    for persona in intake_world["west-studio"]["people"].values():
        assert persona["name"] not in instrucciones
    detalle = _fila(conn, "select detalle from audit_log where accion = 'dictar_al_cargar'")[
        "detalle"]
    assert detalle["puerta"] == "equipo" and detalle["sesion_web_id"]
    assert "sesion_de_administracion_id" not in detalle
    _sin_nada_sensible(json.dumps(detalle, ensure_ascii=False))


def test_la_puerta_del_equipo_dicta_solo_para_direccion(web, conn, intake_world, administradora,
                                                        gemini, monkeypatch):
    from leda import web_app

    leidos = []
    leer = web_app._el_cuerpo_con_tope

    async def contando(request, tope):
        leidos.append(tope)
        return await leer(request, tope)

    monkeypatch.setattr(web_app, "_el_cuerpo_con_tope", contando)
    for nombre in ("Sam North", "Taylor Quinn"):
        r = _dictar_por_el_equipo(_navegador_del_equipo(web, conn, intake_world, nombre))
        assert r.status_code == 403, (nombre, r.text)
    assert _dictar_por_el_equipo(web()).status_code == 401
    administracion = _navegador_de_administracion(web, conn, administradora)
    assert _dictar_por_el_equipo(administracion).status_code == 401
    direccion = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    assert _dictar_por_el_equipo(direccion, origin="https://otro.example").status_code == 403
    # Nada de eso leyó el audio ni llegó a Gemini.
    assert leidos == []
    assert gemini.pedidos == []
    assert _contar(conn, "audit_log", "accion = 'dictar_al_cargar'") == 0


def test_por_la_puerta_del_equipo_una_sesion_cortada_mientras_responde_gemini(
        web, conn, intake_world, gemini):
    from leda import web_app
    from leda.db import espacio

    norte = _norte(intake_world)

    def cortar():
        with espacio(conn, norte["id"]) as cur:
            web_app.cortar_sesiones(cur, norte["people"]["Morgan Hale"]["membership_id"])
        conn.commit()

    direccion = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    gemini.respuestas.append(_con_texto(DICHO))
    gemini.al_llamar = cortar
    r = _dictar_por_el_equipo(direccion)
    assert r.status_code == 401
    assert DICHO not in r.text
    assert _contar(conn, "audit_log", "accion = 'dictar_al_cargar'") == 0


def test_por_la_puerta_del_equipo_sin_clave_un_aviso_y_un_incidente(web, conn, intake_world,
                                                                    gemini, monkeypatch):
    monkeypatch.delenv("LEDA_GEMINI_API_KEY", raising=False)
    direccion = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    r = _dictar_por_el_equipo(direccion)
    assert r.status_code == 503
    assert r.json() == {"error": "sin_dictado", "texto": TEXTO_SIN_DICTADO}
    incidente = _incidente(conn)
    assert incidente is not None
    assert str(incidente["workspace_id"]) == _norte(intake_world)["id"]
    assert gemini.pedidos == []


def test_las_instrucciones_dicen_que_se_dicta_una_tarea_o_un_objetivo(web, conn, intake_world,
                                                                      gemini):
    """J3-4b: las instrucciones a Gemini dicen qué se está dictando, según el formulario
    (`?de=objetivo`); sin decirlo, una tarea, como siempre. Los nombres del espacio van igual, y
    la auditoría dice qué se dictó."""
    from leda import dictado
    from leda.db import admin

    direccion = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    gemini.respuestas += [_con_texto(DICHO), _con_texto(DICHO), _con_texto(DICHO)]
    assert direccion.post(f"{EQUIPO}?de=objetivo", content=AUDIO,
                          headers={"content-type": "audio/mp4"}).status_code == 200
    assert _dictar_por_el_equipo(direccion).status_code == 200
    assert direccion.post(f"{EQUIPO}?de=otra-cosa", content=AUDIO,
                          headers={"content-type": "audio/mp4"}).status_code == 200

    def instrucciones(i: int) -> str:
        return " ".join(p["text"] for p in gemini.cuerpo(i)["contents"][0]["parts"] if "text" in p)

    # Lo que se dicta se busca por su descripción entera (`LO_QUE_SE_DICTA`), no por la posición de
    # una oración: la que nombra los datos del espacio también dice "un objetivo" ("una persona,
    # un área o un objetivo de esta lista"), y el orden de las oraciones puede cambiar.
    objetivo, tarea = dictado.LO_QUE_SE_DICTA["objetivo"], dictado.LO_QUE_SE_DICTA["tarea"]
    assert objetivo in instrucciones(0) and tarea not in instrucciones(0)
    assert tarea in instrucciones(1) and objetivo not in instrucciones(1)
    assert instrucciones(2) == instrucciones(1)
    assert dictado.instrucciones([], de="objetivo") != dictado.instrucciones([])
    with admin(conn) as cur:
        cur.execute("""select detalle ->> 'de' as de from audit_log
                        where accion = 'dictar_al_cargar' order by at, id""")
        assert [f["de"] for f in cur.fetchall()] == ["objetivo", "tarea", "tarea"]
