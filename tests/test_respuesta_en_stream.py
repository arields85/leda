"""La respuesta en stream del alta conducida (ADR 0011 y ADR 0014; experimento del
2026-10-01).

En un chat privado y con el ajuste `stream` del espacio, la persona ve el `texto` del
turno aparecer en el borrador nativo de Telegram mientras el modelo lo escribe. El
mensaje real sigue siendo el verificado, por la cola: el borrador es efímero y sin
botones. Sin red: transportes falsos.
"""

from __future__ import annotations

import json
import threading
import time
from types import SimpleNamespace

import httpx
import openai
import pytest
from fastapi.testclient import TestClient
from psycopg.types.json import Jsonb

from leda import alta_conducida as AC
from leda import despachador as desp
from leda import gateway, incidentes, llm
from leda.alta_turno import NOMBRE_HERRAMIENTA
from leda.db import admin, espacio
from leda.llm import (LectorDeTexto, ProveedorCompatible, ProveedorGemini,
                        ProveedorGuionado, SalidaDeConduccionInvalida,
                        texto_parcial)

from tests.test_alta_conducida import chat, conversada, salida  # noqa: F401
from tests.test_alta_eleccion_confirmacion import _nuevas, _salidas

TOKEN = "123:token-falso"
SEMILLA = desp.SEMILLA_INDICADOR


# ------------------------------------------------- el texto parcial del JSON

TEXTOS = [
    "Dale. ¿Para cuándo?",
    'Anotado: "Calibrar" \\ otra línea\ny una tab\t, ñ, 😀 y á.',
]
DOCUMENTOS = [
    {"intencion": "continuar", "texto": TEXTOS[0], "pregunta": ["due_date"]},
    {"texto": TEXTOS[1], "intencion": "continuar"},
    # `texto` no es la primera clave, y hay otro `texto` anidado antes.
    {"intencion": "continuar", "valores": {"title": {"texto": "ANIDADO"}},
     "pregunta": ["objective"], "texto": TEXTOS[1], "botones": None},
]


def _casos():
    for doc in DOCUMENTOS:
        for ascii_ in (True, False):
            yield json.dumps(doc, ensure_ascii=ascii_), doc["texto"]


def _avisos(cortes: list[int], crudo: str) -> list[str]:
    avisos: list[str] = []
    lector = LectorDeTexto(avisos.append)
    ant = 0
    for corte in [*cortes, len(crudo)]:
        lector.alimentar(crudo[ant:corte])
        ant = corte
    return avisos


def _comprobar(avisos: list[str], esperado: str) -> None:
    assert avisos, "nunca avisó el texto"
    assert avisos[-1] == esperado
    for visto, siguiente in zip(avisos, avisos[1:]):
        assert siguiente.startswith(visto) and siguiente != visto
    for visto in avisos:
        assert esperado.startswith(visto)           # sólo el texto, nunca JSON
        assert "ANIDADO" not in visto and '"intencion"' not in visto


@pytest.mark.parametrize("crudo,esperado", list(_casos()))
def test_el_texto_parcial_crece_con_cualquier_corte_en_dos_fragmentos(crudo, esperado):
    for corte in range(len(crudo) + 1):
        _comprobar(_avisos([corte], crudo), esperado)


@pytest.mark.parametrize("crudo,esperado", list(_casos()))
def test_el_texto_parcial_con_fragmentos_de_un_caracter_y_de_tres(crudo, esperado):
    _comprobar(_avisos(list(range(1, len(crudo))), crudo), esperado)
    _comprobar(_avisos(list(range(3, len(crudo), 3)), crudo), esperado)


@pytest.mark.parametrize("crudo,esperado", list(_casos()))
def test_antes_de_que_empiece_texto_no_se_muestra_nada(crudo, esperado):
    inicio = crudo.rindex('"texto": "') + len('"texto": "')
    assert texto_parcial(crudo[:inicio]) == ""      # abrió la comilla: aún vacío
    for largo in range(inicio):
        assert not texto_parcial(crudo[:largo])


def test_un_escape_cortado_no_muestra_basura():
    assert texto_parcial('{"texto": "a\\') == "a"
    assert texto_parcial('{"texto": "a\\u00') == "a"
    assert texto_parcial('{"texto": "a\\u00e1') == "aá"
    assert texto_parcial('{"texto": "\\ud83d') == ""             # primera mitad sola
    assert texto_parcial('{"texto": "\\ud83d\\ude0') == ""
    assert texto_parcial('{"texto": "\\ud83d\\ude00') == "😀"


def test_texto_nulo_o_no_cadena_no_muestra_nada():
    assert texto_parcial('{"texto": null, "x": "y"}') is None
    assert texto_parcial('{"texto": 5}') is None
    assert texto_parcial('{"valores": {"texto": "no"}, "x": 1}') is None
    assert texto_parcial("") is None


# ----------------------------------------------- la llamada en stream (NaN)

SALIDAS = [{"intencion": "continuar", "texto": TEXTOS[1], "pregunta": ["due_date"]},
           {"valores": {"title": {"texto": "Anidado"}}, "intencion": "continuar",
            "texto": TEXTOS[0]}]
HISTORIAL = [{"role": "user", "content": "quiero una tarea"}]


def _completion(argumentos: str) -> dict:
    return {"id": "c1", "object": "chat.completion", "created": 0, "model": "m",
            "choices": [{"index": 0, "finish_reason": "stop", "message": {
                "role": "assistant", "content": None, "tool_calls": [{
                    "id": "t1", "type": "function", "function": {
                        "name": NOMBRE_HERRAMIENTA, "arguments": argumentos}}]}}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}}


def _trozo(delta: dict, fin=None) -> str:
    cuerpo = {"id": "c1", "object": "chat.completion.chunk", "created": 0,
              "model": "m", "choices": [{"index": 0, "delta": delta,
                                         "finish_reason": fin}]}
    return f"data: {json.dumps(cuerpo)}\n\n"


def _sse(argumentos: str | None, tamano: int = 5, contenido: str | None = None):
    partes = [_trozo({"role": "assistant"})]
    if argumentos is not None:
        partes.append(_trozo({"tool_calls": [{
            "index": 0, "id": "t1", "type": "function",
            "function": {"name": NOMBRE_HERRAMIENTA, "arguments": ""}}]}))
        for i in range(0, len(argumentos), tamano):
            partes.append(_trozo({"tool_calls": [{
                "index": 0, "function": {"arguments": argumentos[i:i + tamano]}}]}))
    if contenido:
        partes.append(_trozo({"content": contenido}))
    partes.append(_trozo({}, "stop"))
    partes.append("data: [DONE]\n\n")
    return httpx.Response(200, content="".join(partes).encode(),
                          headers={"content-type": "text/event-stream"})


_OPENAI = openai.OpenAI


def _compatible(monkeypatch, respond):
    http = httpx.Client(transport=httpx.MockTransport(respond))
    monkeypatch.setattr(openai, "OpenAI", lambda **kw: _OPENAI(http_client=http, **kw))
    monkeypatch.setattr("time.sleep", lambda s: None)
    return ProveedorCompatible("m", "sk-test", "http://localhost/v1")


@pytest.mark.parametrize("ascii_", [True, False])
@pytest.mark.parametrize("tamano", [1, 4, 7, 500])
@pytest.mark.parametrize("esperada", SALIDAS)
def test_en_stream_devuelve_los_mismos_argumentos_que_sin_stream(
        monkeypatch, esperada, tamano, ascii_):
    argumentos = json.dumps(esperada, ensure_ascii=ascii_)

    def sin_stream(request):
        assert "stream" not in json.loads(request.content)
        return httpx.Response(200, json=_completion(argumentos))

    def con_stream(request):
        assert json.loads(request.content)["stream"] is True
        return _sse(argumentos, tamano)

    base = _compatible(monkeypatch, sin_stream).conducir_alta("s", HISTORIAL, "h")
    avisos: list[str] = []
    en_vivo = _compatible(monkeypatch, con_stream).conducir_alta(
        "s", HISTORIAL, "h", al_avanzar=avisos.append)

    assert en_vivo == base == esperada
    _comprobar(avisos, esperada["texto"])                # prefijos crecientes, sin JSON


def test_en_stream_conserva_el_timeout_http_y_con_plazo_corta_sin_reintentos(
        monkeypatch):
    tiempos = []

    def respond(request: httpx.Request) -> httpx.Response:
        tiempos.append(request.extensions["timeout"]["read"])
        raise httpx.ReadTimeout("colgado", request=request)

    proveedor = _compatible(monkeypatch, respond)
    with pytest.raises(openai.APITimeoutError):
        proveedor.conducir_alta("s", [], "h", al_avanzar=lambda t: None)
    assert len(tiempos) == 3 and set(tiempos) == {20}       # el del cliente

    tiempos.clear()
    with pytest.raises(openai.APITimeoutError):
        proveedor.conducir_alta("s", [], "h", plazo=2.5, al_avanzar=lambda t: None)
    assert tiempos == [2.5]


def test_en_stream_sin_llamada_devuelve_el_contenido_y_no_avisa_nada(monkeypatch):
    avisos: list[str] = []
    contenido = json.dumps(SALIDAS[0])
    r = _compatible(monkeypatch, lambda req: _sse(None, contenido=contenido))
    assert r.conducir_alta("s", [], "h", al_avanzar=avisos.append) == contenido
    assert avisos == []


@pytest.mark.parametrize("sse", [lambda: _sse("{no es json"), lambda: _sse(None)])
def test_en_stream_sin_salida_usable_es_el_mismo_error(monkeypatch, sse):
    p = _compatible(monkeypatch, lambda req: sse())
    with pytest.raises(SalidaDeConduccionInvalida):
        p.conducir_alta("s", [], "h", al_avanzar=lambda t: None)


def test_un_aviso_que_falla_no_rompe_la_llamada(monkeypatch):
    def falla(texto):
        raise RuntimeError("boom")

    p = _compatible(monkeypatch,
                    lambda req: _sse(json.dumps(SALIDAS[1]), 6))
    assert p.conducir_alta("s", [], "h", al_avanzar=falla) == SALIDAS[1]


def test_gemini_acepta_al_avanzar_y_responde_igual_sin_avisar():
    http = httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json={"candidates": [{"content": {
            "parts": [{"functionCall": {"name": NOMBRE_HERRAMIENTA,
                                        "args": SALIDAS[0]}}]}}]})))
    avisos: list[str] = []
    assert ProveedorGemini("m", "k", cliente=http).conducir_alta(
        "s", [], "h", al_avanzar=avisos.append) == SALIDAS[0]
    assert avisos == []


def test_el_guionado_entrega_los_avances_solo_si_se_pidieron():
    p = ProveedorGuionado(guion=[], conducciones=[SALIDAS[0], SALIDAS[0]],
                          avances=[["a", "ab"], ["x"]])
    vistos: list[str] = []
    p.conducir_alta("s", [], "h", al_avanzar=vistos.append)
    p.conducir_alta("s", [], "h")
    assert vistos == ["a", "ab"] and p.pidieron_avance == [True, False]


# ------------------------------------------------ el indicador y su borrador

class Telegram:
    """Un cliente HTTP falso de Telegram: anota cada pedido y puede fallar."""

    def __init__(self, falla=None):
        self.pedidos: list[tuple[str, dict]] = []
        self._falla = falla
        self._candado = threading.Lock()

    def post(self, url, json=None):
        metodo = url.rsplit("/", 1)[-1]
        with self._candado:
            self.pedidos.append((metodo, dict(json or {})))
        if self._falla and self._falla(metodo, json or {}):
            raise httpx.ConnectError(f"sin red para {url}")
        return httpx.Response(200, request=httpx.Request("POST", url),
                              json={"ok": True, "result": {"message_id": 9}})

    def borradores(self) -> list[dict]:
        return [p for m, p in self.pedidos if m == "sendMessageDraft"]

    def textos(self) -> list[str]:
        return [p["text"] for p in self.borradores() if p["text"] != SEMILLA]

    def metodos(self) -> list[str]:
        return [m for m, _ in self.pedidos]


def _esperar(condicion, plazo=2.0):
    fin = time.monotonic() + plazo
    while time.monotonic() < fin:
        if condicion():
            return
        time.sleep(0.005)
    raise AssertionError("no pasó a tiempo")


def _activo(tg, **kw):
    kw.setdefault("chat_type", "private")
    kw.setdefault("umbral", 0)
    kw.setdefault("intervalo", 0.05)
    kw.setdefault("intervalo_borrador", 0)
    kw.setdefault("espera_cierre", 1.0)
    return desp.mantener_chat_activo(TOKEN, 7, cliente=tg, **kw)


def test_las_actualizaciones_usan_el_draft_id_de_la_semilla_y_se_retiran_igual():
    tg = Telegram()
    with _activo(tg) as ind:
        _esperar(lambda: SEMILLA in [p["text"] for p in tg.borradores()])
        ind.actualizar_borrador("Ho")
        ind.actualizar_borrador("Hola")
        assert desp.indicador_actual() is ind
    assert desp.indicador_actual() is None

    assert {p["draft_id"] for p in tg.borradores()} == {ind.draft_id}
    assert tg.textos() == ["Ho", "Hola"]
    assert all(set(p) == {"chat_id", "draft_id", "text"} for p in tg.borradores())
    # El retiro de siempre, y el typing después del retiro (0d86349).
    metodos = tg.metodos()
    retiro = metodos.index("sendMessage")
    assert metodos[retiro:retiro + 3] == ["sendMessage", "deleteMessage",
                                          "sendChatAction"]
    assert "sendMessageDraft" not in metodos[retiro:]


def test_con_texto_antes_del_umbral_la_semilla_no_lo_tapa_y_igual_se_retira():
    tg = Telegram()
    with _activo(tg, umbral=0.3) as ind:
        ind.actualizar_borrador("Ya hay texto")
        time.sleep(0.5)                          # pasa el umbral del indicador
    assert tg.textos() == ["Ya hay texto"]
    assert SEMILLA not in [p["text"] for p in tg.borradores()]
    assert "deleteMessage" in tg.metodos()       # el borrador se retiró


def test_el_texto_se_acota_a_una_actualizacion_por_intervalo():
    """Lo intermedio que quedó viejo antes de poder salir no se manda; lo último
    sí, cuando pasa el intervalo; el mismo texto o uno vacío no se repiten."""
    tg = Telegram()
    with _activo(tg, umbral=10, intervalo_borrador=0.2) as ind:
        ind.actualizar_borrador("a")             # la primera sale enseguida
        _esperar(lambda: tg.textos() == ["a"])
        ind.actualizar_borrador("ab")            # muy pronto: queda pendiente...
        ind.actualizar_borrador("abc")           # ...y la reemplaza la más nueva
        _esperar(lambda: tg.textos()[-1:] == ["abc"])
        ind.actualizar_borrador("abc")           # el mismo texto: no sale
        ind.actualizar_borrador("")              # vacío: no sale
        time.sleep(0.3)
    assert tg.textos() == ["a", "abc"]


def test_en_un_grupo_no_hay_borrador_aunque_se_actualice():
    tg = Telegram()
    with _activo(tg, chat_type="group") as ind:
        assert ind.admite_borrador is False
        ind.actualizar_borrador("hola")
        time.sleep(0.1)
    assert tg.borradores() == []


def test_despues_de_cerrar_no_se_manda_mas_texto():
    tg = Telegram()
    with _activo(tg, umbral=10) as ind:
        ind.actualizar_borrador("a")
    antes = len(tg.pedidos)
    ind.actualizar_borrador("tarde")
    assert len(tg.pedidos) == antes


def test_una_falla_del_borrador_no_rompe_se_reporta_una_vez_y_no_se_insiste(capsys):
    tg = Telegram(falla=lambda m, j: m == "sendMessageDraft")
    with _activo(tg, umbral=10) as ind:
        ind.actualizar_borrador("a")
        ind.actualizar_borrador("ab")
        ind.actualizar_borrador("abc")
    assert [p["text"] for p in tg.borradores()] == ["a"]       # un solo intento
    assert capsys.readouterr().out.count("indicador de actividad (stream)") == 1
    assert "deleteMessage" in tg.metodos()                     # el retiro igual corre


# --------------------------------------------------------- el ajuste `stream`

def _poner_stream(conn, world, valor):
    with admin(conn) as cur:
        cur.execute("delete from workspace_setting where clave = 'stream'")
        if valor is not None:
            cur.execute(
                "insert into workspace_setting (workspace_id, clave, valor) "
                "values (%s, 'stream', %s)",
                (world["north-lab"]["id"], Jsonb(valor)))
    conn.commit()


@pytest.mark.parametrize("valor,activo", [
    (None, False), (True, True), ({"activo": True}, True),
    (False, False), ({"activo": False}, False)])
def test_el_ajuste_stream_se_lee_del_espacio(valor, activo, intake_world, conn):
    _poner_stream(conn, intake_world, valor)
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        assert AC.stream_activo(cur, ws) is activo
    with admin(conn) as cur:
        cur.execute("select 1 from incident where etapa = %s",
                    (incidentes.ETAPA_INTERRUPTOR_STREAM,))
        assert cur.fetchall() == []                  # un valor válido no es anomalía


@pytest.mark.parametrize("valor", ["si", 1, {"activo": "yes"}, {"otro": True}])
def test_un_valor_invalido_es_apagado_y_un_incidente_una_sola_vez(
        valor, intake_world, conn):
    _poner_stream(conn, intake_world, valor)
    ws = intake_world["north-lab"]["id"]
    AC._anomalias_stream.clear()
    with espacio(conn, ws) as cur:
        assert AC.stream_activo(cur, ws) is False
        assert AC.stream_activo(cur, ws) is False
    with admin(conn) as cur:
        cur.execute("select etapa from incident where etapa = %s",
                    (incidentes.ETAPA_INTERRUPTOR_STREAM,))
        assert len(cur.fetchall()) == 1


# ------------------------------------------------------ de punta a punta

_mensajes = iter(range(7000, 8000))


def _escribir_en_vivo(c, texto: str, tg: Telegram, tipo="private"):
    """Un mensaje por el webhook, con el indicador de actividad REAL (y Telegram
    falso) alrededor del turno, como en producción."""
    ws = c.world["north-lab"]
    mp = c.monkeypatch
    mp.setattr(gateway, "_conn", lambda: c.conn)
    mp.setattr(gateway, "mantener_chat_activo",
               lambda token, chat_id, **k: _activo(tg, **k))
    mp.setattr(gateway, "config", SimpleNamespace(
        webhook_secret="test-secret", llm_api_key="unused",
        token_bot=lambda slug: "unused-token"))
    mp.setattr("leda.llm.desde_base", lambda *a: c.modelo)
    usuario = ws["people"]["Taylor Quinn"]["telegram"]
    respuesta = TestClient(gateway.app).post(
        "/telegram/north-lab",
        json={"message": {"message_id": next(_mensajes), "text": texto,
                          "chat": {"id": usuario, "type": tipo},
                          "from": {"id": usuario}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"})
    assert respuesta.status_code == 200


def _turno(c, tg, texto="necesito crear una tarea"):
    antes = _salidas(c.conn, c.usuario)
    _escribir_en_vivo(c, texto, tg)
    return [f["cuerpo"] for f in _nuevas(c.conn, c.usuario, antes)]


def test_de_punta_a_punta_el_borrador_crece_con_el_mismo_draft_id_y_el_mensaje_es_el_verificado(
        chat, conn, conversada):
    _poner_stream(conn, conversada, True)
    c = chat(salida("Dale. ¿Qué hay que hacer?", pregunta=["title"]))
    c.modelo.avances = [["Dale.", "Dale. ¿Qué", "Dale. ¿Qué hay que hacer?"]]
    tg = Telegram()

    cuerpos = _turno(c, tg)

    assert cuerpos == ["Dale. ¿Qué hay que hacer?"]           # el verificado, por la cola
    assert c.modelo.pidieron_avance == [True]
    assert tg.textos() == ["Dale.", "Dale. ¿Qué", "Dale. ¿Qué hay que hacer?"]
    assert len({p["draft_id"] for p in tg.borradores()}) == 1  # el mismo del indicador
    # Nunca un mensaje con el texto de la respuesta por Telegram directo: el único
    # `sendMessage` es el retiro del borrador (semilla).
    assert [p["text"] for m, p in tg.pedidos if m == "sendMessage"] == [SEMILLA]


def test_sin_el_ajuste_no_hay_stream_ni_se_pide_el_avance(chat):
    c = chat(salida("¿Qué hay que hacer?", pregunta=["title"]))
    c.modelo.avances = [["¿Qué"]]
    tg = Telegram()

    assert _turno(c, tg) == ["¿Qué hay que hacer?"]
    assert c.modelo.pidieron_avance == [False]
    assert tg.textos() == []


def test_con_un_ajuste_invalido_no_hay_stream_y_queda_un_incidente(
        chat, conn, conversada):
    _poner_stream(conn, conversada, "si")
    AC._anomalias_stream.clear()
    c = chat(salida("¿Qué hay que hacer?", pregunta=["title"]))
    tg = Telegram()

    assert _turno(c, tg) == ["¿Qué hay que hacer?"]
    assert c.modelo.pidieron_avance == [False] and tg.textos() == []
    assert len(c.incidentes(incidentes.ETAPA_INTERRUPTOR_STREAM)) == 1


def test_un_primer_intento_rechazado_y_un_reintento_aceptado_reinicia_el_borrador(
        chat, conn, conversada):
    _poner_stream(conn, conversada, {"activo": True})
    # Falta el título y el primer intento no pregunta nada: el código lo rechaza.
    c = chat(salida("Dale, anotado."),
             salida("¿Qué hay que hacer?", pregunta=["title"]))
    c.modelo.avances = [["Dale, anotado."], ["¿Qué hay", "¿Qué hay que hacer?"]]
    tg = Telegram()

    cuerpos = _turno(c, tg)

    assert len(c.modelo.conducidos) == 2
    assert c.modelo.pidieron_avance == [True, True]
    assert tg.textos() == ["Dale, anotado.", "¿Qué hay", "¿Qué hay que hacer?"]
    assert cuerpos == ["¿Qué hay que hacer?"]                  # el del reintento


def test_una_falla_del_borrador_no_rompe_el_turno_ni_la_respuesta(
        chat, conn, conversada, capsys):
    _poner_stream(conn, conversada, True)
    c = chat(salida("¿Qué hay que hacer?", pregunta=["title"]))
    c.modelo.avances = [["¿Qué", "¿Qué hay", "¿Qué hay que hacer?"]]
    tg = Telegram(falla=lambda m, j: m == "sendMessageDraft" and j["text"] != SEMILLA)

    assert _turno(c, tg) == ["¿Qué hay que hacer?"]
    assert len(tg.textos()) == 1                                # un intento y basta
    assert capsys.readouterr().out.count("indicador de actividad (stream)") == 1


def test_un_telegram_lento_no_frena_la_lectura_del_modelo():
    """Revisión RDD `review-16296c4f68eaa688` (R3/R4): actualizar el borrador no
    puede esperar a Telegram en el hilo que lee lo que escribe el modelo; si hay un
    envío en vuelo, la actualización siguiente se saltea (la próxima la alcanza) y
    el cierre igual espera al envío antes de retirar."""
    class Lento(Telegram):
        def post(self, url, json=None):
            if url.endswith("/sendMessageDraft") and (json or {}).get("text") != SEMILLA:
                time.sleep(0.4)
            return super().post(url, json)

    tg = Lento()
    with _activo(tg) as ind:
        _esperar(lambda: ind.activado.is_set())
        inicio = time.monotonic()
        ind.actualizar_borrador("Hola")
        ind.actualizar_borrador("Hola, ¿qué")
        demora = time.monotonic() - inicio
    assert demora < 0.2
    assert tg.textos() == ["Hola"]                 # el segundo se salteó: había uno en vuelo
    metodos = tg.metodos()
    ultimo_borrador = max(i for i, m in enumerate(metodos) if m == "sendMessageDraft")
    assert "deleteMessage" in metodos[ultimo_borrador:]   # el retiro, después del envío


def test_el_ultimo_texto_siempre_llega_al_borrador_aunque_haya_llegado_rapido():
    """Prueba real del 2026-10-01 (Ariel): se veían sólo las primeras letras
    ("List…") y después el mensaje final. Lo que llega mientras hay un envío en
    vuelo, o antes del intervalo, no se descarta: queda pendiente y sale apenas se
    puede, así el borrador termina mostrando lo último que escribió el modelo."""
    tg = Telegram()
    with _activo(tg, intervalo_borrador=0.15) as ind:
        _esperar(lambda: ind.activado.is_set())
        for parcial in ("Li", "Listo", "Listo, anoté", "Listo, anoté la tarea"):
            ind.actualizar_borrador(parcial)
        _esperar(lambda: tg.textos() and tg.textos()[-1] == "Listo, anoté la tarea")
    # El primero que sale depende de cuándo arranca el trabajador; lo que se
    # garantiza es que todo lo enviado es algo que escribió el modelo, en orden,
    # y que lo último siempre llega.
    enviados = tg.textos()
    escritos = ["Li", "Listo", "Listo, anoté", "Listo, anoté la tarea"]
    assert all(t in escritos for t in enviados)
    assert enviados == sorted(enviados, key=escritos.index)
    assert enviados[-1] == "Listo, anoté la tarea"
    assert len(tg.textos()) <= 3                      # sigue acotado por el intervalo


def test_el_borrador_se_actualiza_seguido_para_que_se_vea_mientras_escribe():
    """Pedido del usuario (2026-10-01): "que apenas tenga algo para mostrar lo
    muestre", y bajarlo más para ver mejor cómo escribe. El primer texto sale
    enseguida y después, a lo sumo cada 0,15 s."""
    assert desp.INTERVALO_DE_BORRADOR <= 0.15



class _TelegramConRitmo(Telegram):
    """Responde 429 (más despacio) al primer texto del borrador, como Telegram
    cuando se le manda muy seguido; después acepta."""

    def __init__(self, codigo=429):
        super().__init__()
        self._codigo = codigo
        self.rechazados = 0

    def post(self, url, json=None):
        if (url.endswith("/sendMessageDraft") and (json or {}).get("text") != SEMILLA
                and self.rechazados == 0):
            self.rechazados += 1
            with self._candado:
                self.pedidos.append(("rechazado", dict(json or {})))
            return httpx.Response(
                self._codigo, request=httpx.Request("POST", url),
                json={"ok": False, "error_code": self._codigo,
                      "description": "Too Many Requests: retry after 0",
                      "parameters": {"retry_after": 0}})
        return super().post(url, json)


def test_si_telegram_pide_ir_mas_despacio_se_espera_y_se_sigue_con_lo_ultimo():
    """Un 429 no corta el stream del turno: se espera lo que pide Telegram
    (acotado) y se manda el texto más nuevo."""
    tg = _TelegramConRitmo()
    with _activo(tg) as ind:
        _esperar(lambda: ind.activado.is_set())
        ind.actualizar_borrador("Hola")
        _esperar(lambda: tg.rechazados == 1)
        ind.actualizar_borrador("Hola, ¿qué")
        _esperar(lambda: tg.textos()[-1:] == ["Hola, ¿qué"])
    assert tg.textos()[-1] == "Hola, ¿qué"


def test_otro_error_de_telegram_corta_el_stream_del_turno_y_se_reporta(capsys):
    tg = _TelegramConRitmo(codigo=400)
    with _activo(tg) as ind:
        _esperar(lambda: ind.activado.is_set())
        ind.actualizar_borrador("Hola")
        _esperar(lambda: tg.rechazados == 1)
        time.sleep(0.05)
        ind.actualizar_borrador("Hola, ¿qué")
        time.sleep(0.2)
    assert tg.textos() == []
    assert "stream" in capsys.readouterr().out
