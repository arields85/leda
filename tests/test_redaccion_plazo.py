"""El plazo de la redacción de A y el tamaño de su pedido (ADR 0014, latencia).

Con A cada texto y cada toque espera una llamada al modelo: el plazo es propio,
corto y sin reintentos, y si se pasa sale la plantilla de B de inmediato y queda
registrado. El pedido lleva sólo los hechos y una guía de voz corta, no el
contexto conversacional. Sin red y sin esperar: el reloj y el modelo se simulan.
"""

from __future__ import annotations

import inspect
import json
import threading
import time

import httpx
import pytest

from prisma import incidentes, llm, redaccion
from prisma.db import admin, espacio
from prisma.llm import ProveedorGuionado
from prisma.resultado_turno import (Cambio, Falta, OpcionDisponible, Rechazo,
                                    ResultadoTurno, ValorAceptado)
from prisma.valores import TipoValor

EN_CURSO = ResultadoTurno(
    cambios=(Cambio("la tarea «Revisar PLC»", "quedó en curso"),))
PREGUNTA = ResultadoTurno(
    falta=Falta("la fecha objetivo", TipoValor.FECHA, pregunta="¿Para cuándo?",
                campo="due_date"))


class _Reloj:
    """Un reloj que sólo avanza cuando alguien duerme: la prueba no espera."""

    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def dormir(self, segundos):
        self.t += segundos


class _ModeloLento(ProveedorGuionado):
    """Tarda `tarda` segundos (simulados) y respeta el plazo que le piden: si lo
    pasa, vence en el plazo (`PlazoAgotado`, lo que hace `llamar_con_plazo` con el
    reloj real), sin esperar el resto."""

    def __init__(self, reloj: _Reloj, tarda: float, texto: str = ""):
        super().__init__(guion=[])
        self.reloj, self.tarda, self.texto = reloj, tarda, texto
        self.llamadas = 0

    def redactar(self, sistema, hechos, *, plazo=None):
        self.llamadas += 1
        self.plazos.append(plazo)
        if plazo is not None and self.tarda > plazo:
            self.reloj.dormir(plazo)
            raise llm.PlazoAgotado(plazo)
        self.reloj.dormir(self.tarda)
        return self.texto


def _intentos(conn, ws):
    with admin(conn) as cur:
        cur.execute("select detalle from audit_log where workspace_id = %s "
                    "and accion = %s order by at", (ws, redaccion.ACCION_REDACCION_A))
        return [f["detalle"] for f in cur.fetchall()]


def _incidentes(conn, ws):
    with admin(conn) as cur:
        cur.execute("select severidad, referencia_cruda, notificado_admin_en "
                    "from incident where workspace_id = %s and etapa = %s",
                    (ws, incidentes.ETAPA_REDACCION_RECHAZADA))
        return cur.fetchall()


def _redactar(conn, ws, resultado, proveedor, **kw):
    with espacio(conn, ws) as cur:
        return redaccion.redactar_turno(cur, ws, resultado, "A",
                                        proveedor=proveedor, **kw)


# ------------------------------------------------------------------ el plazo

def test_el_plazo_por_omision_es_corto_y_se_le_pasa_al_modelo(corework, conn):
    assert redaccion.PLAZO_REDACCION_S == 4.0
    ws = corework.workspace_id
    bueno = json.dumps({"texto": "Listo, la tarea «Revisar PLC» quedó en curso.",
                        "pregunta": None, "afirma": ["c1"]}, ensure_ascii=False)
    p = ProveedorGuionado(guion=[], borradores=[bueno])

    _redactar(conn, ws, EN_CURSO, p)

    assert p.plazos == [redaccion.PLAZO_REDACCION_S]


def test_el_plazo_se_puede_configurar_por_llamada(corework, conn):
    ws = corework.workspace_id
    p = ProveedorGuionado(guion=[], borradores=["{}"])
    _redactar(conn, ws, EN_CURSO, p, plazo=1.25)
    assert p.plazos == [1.25]


def test_un_modelo_lento_cae_a_b_dentro_del_plazo_sin_reintentar(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    reloj = _Reloj()
    monkeypatch.setattr(redaccion, "_reloj", reloj)
    modelo = _ModeloLento(reloj, tarda=40.0)          # un modelo colgado

    texto = _redactar(conn, ws, EN_CURSO, modelo)

    assert texto == redaccion.redactar_partes(EN_CURSO, "B")      # B, de inmediato
    assert modelo.llamadas == 1                                   # sin reintentos
    assert reloj.t == redaccion.PLAZO_REDACCION_S                 # y a tiempo
    (intento,) = _intentos(conn, ws)
    assert intento["resultado"] == "timeout"
    assert intento["duracion_ms"] == 4000
    assert "4" in intento["motivo"]
    (incidente,) = _incidentes(conn, ws)
    assert incidente["severidad"] == "baja" and incidente["notificado_admin_en"] is None


def test_un_modelo_que_contesta_a_tiempo_no_se_corta(corework, conn, monkeypatch):
    ws = corework.workspace_id
    reloj = _Reloj()
    monkeypatch.setattr(redaccion, "_reloj", reloj)
    bueno = json.dumps({"texto": "Listo, la tarea «Revisar PLC» quedó en curso.",
                        "pregunta": None, "afirma": ["c1"]}, ensure_ascii=False)
    modelo = _ModeloLento(reloj, tarda=3.9, texto=bueno)

    texto = _redactar(conn, ws, EN_CURSO, modelo)

    assert texto.texto == "Listo, la tarea «Revisar PLC» quedó en curso."
    assert _intentos(conn, ws)[0]["resultado"] == "aceptada"


def test_la_estadistica_cuenta_los_timeouts_aparte(corework, conn, monkeypatch):
    ws = corework.workspace_id
    reloj = _Reloj()
    monkeypatch.setattr(redaccion, "_reloj", reloj)
    _redactar(conn, ws, EN_CURSO, _ModeloLento(reloj, tarda=40.0))
    _redactar(conn, ws, EN_CURSO, ProveedorGuionado(
        guion=[], borradores=[RuntimeError("cayó")]))

    with admin(conn) as cur:
        e = redaccion.estadistica_variante_a(cur, ws)
    assert (e["llamadas"], e["timeouts"], e["errores"]) == (2, 1, 1)


def test_la_charla_de_b_tambien_tiene_plazo(corework, conn):
    ws = corework.workspace_id
    p = ProveedorGuionado(guion=[], borradores=["¡Hola!"])
    with espacio(conn, ws) as cur:
        redaccion.redactar_charla(cur, ws, "hola", "¿Qué hay que hacer?", proveedor=p)
    assert p.plazos == [redaccion.PLAZO_REDACCION_S]


# ---------------------------------------------- el plazo acota el tiempo TOTAL

class _ModeloColgado(ProveedorGuionado):
    """Ignora el plazo, como un cliente cuyo timeout es por fase (conexión,
    escritura, lectura): espera hasta que la prueba lo suelta y recién entonces
    contesta. El plazo del proyecto es el que tiene que cortar."""

    def __init__(self, respuesta: str = ""):
        super().__init__(guion=[])
        self.suelta = threading.Event()
        self.respuesta = respuesta

    def redactar(self, sistema, hechos, *, plazo=None):
        self.plazos.append(plazo)
        self.suelta.wait(10)
        return self.respuesta


def test_el_plazo_acota_el_tiempo_total_aunque_el_modelo_lo_ignore(corework, conn):
    ws = corework.workspace_id
    bueno = json.dumps({"texto": "Listo, la tarea «Revisar PLC» quedó en curso.",
                        "pregunta": None, "afirma": ["c1"]}, ensure_ascii=False)
    modelo = _ModeloColgado(bueno)
    try:
        inicio = time.perf_counter()
        texto = _redactar(conn, ws, EN_CURSO, modelo, plazo=0.1)
        espera = time.perf_counter() - inicio
    finally:
        modelo.suelta.set()                  # la respuesta tardía llega después

    assert espera < 2.0                      # no esperó a un modelo que no contesta
    assert texto == redaccion.redactar_partes(EN_CURSO, "B")
    time.sleep(0.2)                          # y la respuesta tardía se descarta
    (intento,) = _intentos(conn, ws)
    assert intento["resultado"] == "timeout"
    assert "0.1 s sin respuesta" in intento["motivo"]
    assert len(_incidentes(conn, ws)) == 1


def test_la_charla_tambien_se_corta_en_el_plazo_total(corework, conn, monkeypatch):
    ws = corework.workspace_id
    monkeypatch.setattr(redaccion, "PLAZO_REDACCION_S", 0.1)
    modelo = _ModeloColgado("¡Hola!")
    try:
        inicio = time.perf_counter()
        with espacio(conn, ws) as cur:
            breve = redaccion.redactar_charla(cur, ws, "hola", "¿Qué hay que hacer?",
                                              proveedor=modelo)
        espera = time.perf_counter() - inicio
    finally:
        modelo.suelta.set()
    assert breve == "" and espera < 2.0


def test_un_modelo_rapido_no_paga_nada_por_el_plazo(corework, conn):
    ws = corework.workspace_id
    bueno = json.dumps({"texto": "Listo, la tarea «Revisar PLC» quedó en curso.",
                        "pregunta": None, "afirma": ["c1"]}, ensure_ascii=False)
    modelo = _ModeloColgado(bueno)
    modelo.suelta.set()
    texto = _redactar(conn, ws, EN_CURSO, modelo, plazo=5.0)
    assert texto.texto == "Listo, la tarea «Revisar PLC» quedó en curso."


# ----------------------------------------- los timeouts se clasifican por tipo

class _TimeoutDeUnCliente(Exception):
    """Como `openai.APITimeoutError`: el cliente envuelve el timeout de httpx."""


def _envuelto(causa: BaseException) -> BaseException:
    try:
        raise _TimeoutDeUnCliente("Request timed out.") from causa
    except _TimeoutDeUnCliente as exc:
        return exc


class _NombraTimeoutPeroNoLoEs(Exception):
    pass


@pytest.mark.parametrize("excepcion", [
    TimeoutError("se agotó"),
    httpx.ReadTimeout("lectura"),
    httpx.ConnectTimeout("conexión"),
    httpx.PoolTimeout("pool"),
    _envuelto(httpx.ReadTimeout("lectura")),
])
def test_un_timeout_se_reconoce_por_su_tipo_y_no_dice_mas_de_lo_que_sabe(
        corework, conn, excepcion):
    ws = corework.workspace_id
    p = ProveedorGuionado(guion=[], borradores=[excepcion])
    _redactar(conn, ws, EN_CURSO, p)
    (intento,) = _intentos(conn, ws)
    assert intento["resultado"] == "timeout"
    assert "sin respuesta" not in intento["motivo"]       # eso es sólo del plazo propio


def test_un_error_con_timeout_en_el_nombre_no_es_un_timeout(corework, conn):
    ws = corework.workspace_id
    p = ProveedorGuionado(guion=[], borradores=[_NombraTimeoutPeroNoLoEs("x")])
    _redactar(conn, ws, EN_CURSO, p)
    assert _intentos(conn, ws)[0]["resultado"] == "error"


# ----------------------- R14: el motivo de una falla no guarda lo que trae el mensaje

SECRETO = "SECRETO-9f3a7c1d"
MENSAJES_CON_CREDENCIAL = [
    f"URL inválida https://api.ejemplo.com/v1/models?key={SECRETO}&x=1",
    f"falló la llamada a api.ejemplo.com con api_key={SECRETO}",
    f"Authorization: Bearer {SECRETO}",
    f"GET /v1/chat?token={SECRETO} devolvió 401",
    f"no se pudo leer http://usuario:{SECRETO}@host/ruta",
]


class _ErrorHttpDeUnCliente(httpx.HTTPError):
    pass


class _ErrorDeJson(ValueError):
    pass


def _motivo(conn, ws, excepcion):
    p = ProveedorGuionado(guion=[], borradores=[excepcion])
    _redactar(conn, ws, EN_CURSO, p)
    (intento,) = _intentos(conn, ws)
    return intento["motivo"]


@pytest.mark.parametrize("mensaje", MENSAJES_CON_CREDENCIAL)
@pytest.mark.parametrize("tipo", [
    ValueError, LookupError, KeyError, _ErrorDeJson, _ErrorHttpDeUnCliente,
    httpx.InvalidURL, httpx.UnsupportedProtocol, RuntimeError])
def test_el_secreto_de_una_excepcion_no_llega_a_la_auditoria_ni_al_incidente(
        corework, conn, tipo, mensaje):
    ws = corework.workspace_id
    motivo = _motivo(conn, ws, tipo(mensaje))

    assert SECRETO not in motivo and "?" not in motivo and "api_key" not in motivo
    assert motivo.startswith(tipo.__name__)
    for incidente in _incidentes(conn, ws):
        assert SECRETO not in incidente["referencia_cruda"]
    with admin(conn) as cur:
        cur.execute("select detalle::text t from audit_log where workspace_id = %s",
                    (ws,))
        assert all(SECRETO not in f["t"] for f in cur.fetchall())


def test_una_configuracion_que_falta_sigue_diciendo_que_falta(corework, conn):
    """Un `ValueError`/`LookupError` propio, sin nada parecido a una dirección,
    conserva su razón corta: es lo que permite arreglar la configuración."""
    ws = corework.workspace_id
    motivo = _motivo(conn, ws, LookupError("no hay un modelo configurado"))
    assert motivo == "LookupError: no hay un modelo configurado"


def test_la_razon_corta_tiene_tope(corework, conn):
    ws = corework.workspace_id
    assert len(_motivo(conn, ws, ValueError("x" * 5000))) <= 160


def test_un_error_http_o_de_json_guarda_sólo_su_tipo(corework, conn):
    ws = corework.workspace_id
    assert _motivo(conn, ws, _ErrorDeJson("Expecting value: line 1")) == "_ErrorDeJson"
    with admin(conn) as cur:
        cur.execute("delete from audit_log where workspace_id = %s and accion = %s",
                    (ws, redaccion.ACCION_REDACCION_A))
    assert _motivo(conn, ws, httpx.HTTPStatusError(
        "401 en https://x/?key=SECRETO", request=httpx.Request("GET", "https://x/"),
        response=httpx.Response(401))) == "HTTPStatusError"


# ------------------------------------------- todo proveedor acepta el `plazo`

def _proveedores():
    return [c for _, c in inspect.getmembers(llm, inspect.isclass)
            if "redactar" in vars(c)]


def test_hay_proveedores_que_comprobar():
    nombres = {c.__name__ for c in _proveedores()}
    assert {"Proveedor", "ProveedorGuionado"} <= nombres
    assert len(nombres) >= 5            # los de cada proveedor real, también


@pytest.mark.parametrize("clase", _proveedores(), ids=lambda c: c.__name__)
def test_todo_proveedor_acepta_el_plazo_como_argumento_con_nombre(clase):
    """El contrato de `redactar` es parte del tipo: un proveedor sin `plazo=`
    perdería el plazo sin avisar."""
    parametro = inspect.signature(clase.redactar).parameters.get("plazo")
    assert parametro is not None, f"{clase.__name__}.redactar no acepta `plazo`"
    assert parametro.kind is inspect.Parameter.KEYWORD_ONLY
    assert parametro.default is None


# ------------------------------------------------------------ el tamaño del pedido

def _pedido(resultado) -> int:
    return len(redaccion.SISTEMA_REDACCION) + len(redaccion.serializar_hechos(resultado))


def test_el_pedido_lleva_sólo_la_guia_de_voz_y_los_hechos():
    """Una guía de voz de pocas líneas y los hechos del turno: nada del contexto
    conversacional (el núcleo, el historial, la lista de tareas)."""
    assert len(redaccion.SISTEMA_REDACCION) <= 1100
    assert len(redaccion.SISTEMA_REDACCION.splitlines()) <= 8
    for lejano in ("nucleo", "historial", "herramienta", "constitución"):
        assert lejano not in redaccion.SISTEMA_REDACCION.lower()

    tipica = ResultadoTurno(
        entendido=(ValorAceptado("el título", "Revisar el variador"),),
        rechazo=Rechazo("Esa fecha ya pasó.", "Decime una fecha desde hoy en adelante."),
        falta=Falta("la fecha objetivo", TipoValor.FECHA,
                    pregunta="¿Para cuándo la necesitás? Decime la fecha.",
                    campo="due_date"),
        opciones=(OpcionDisponible("Confirmar", "confirmar"),))
    # Un turno típico: el pedido entero cabe en ~400 tokens (3,5 caracteres por token).
    assert _pedido(tipica) <= 1400


def test_los_hechos_son_sólo_los_del_resultado():
    datos = json.loads(redaccion.serializar_hechos(ResultadoTurno(
        falta=Falta("la fecha objetivo", TipoValor.FECHA, campo="due_date"))))
    assert set(datos) == {"falta"}


@pytest.mark.parametrize("variante", ["B"])
def test_b_no_paga_ningun_plazo(corework, conn, variante):
    ws = corework.workspace_id
    p = ProveedorGuionado(guion=[], borradores=["x"])
    with espacio(conn, ws) as cur:
        redaccion.redactar_turno(cur, ws, EN_CURSO, variante, proveedor=p)
    assert p.plazos == [] and _intentos(conn, ws) == []
