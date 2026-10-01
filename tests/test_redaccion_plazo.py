"""El plazo de la redacción de A y el tamaño de su pedido (ADR 0014, latencia).

Con A cada texto y cada toque espera una llamada al modelo: el plazo es propio,
corto y sin reintentos, y si se pasa sale la plantilla de B de inmediato y queda
registrado. El pedido lleva sólo los hechos y una guía de voz corta, no el
contexto conversacional. Sin red y sin esperar: el reloj y el modelo se simulan.
"""

from __future__ import annotations

import json

import pytest

from prisma import incidentes, redaccion
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
    pasa, lanza el timeout en el plazo, sin esperar el resto."""

    def __init__(self, reloj: _Reloj, tarda: float, texto: str = ""):
        super().__init__(guion=[])
        self.reloj, self.tarda, self.texto = reloj, tarda, texto
        self.llamadas = 0

    def redactar(self, sistema, hechos, *, plazo=None):
        self.llamadas += 1
        self.plazos.append(plazo)
        if plazo is not None and self.tarda > plazo:
            self.reloj.dormir(plazo)
            raise TimeoutError("el modelo no contestó a tiempo")
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
    assert redaccion.PLAZO_REDACCION_S == 3.0
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
    assert intento["duracion_ms"] == 3000
    assert "3" in intento["motivo"]
    (incidente,) = _incidentes(conn, ws)
    assert incidente["severidad"] == "baja" and incidente["notificado_admin_en"] is None


def test_un_modelo_que_contesta_a_tiempo_no_se_corta(corework, conn, monkeypatch):
    ws = corework.workspace_id
    reloj = _Reloj()
    monkeypatch.setattr(redaccion, "_reloj", reloj)
    bueno = json.dumps({"texto": "Listo, la tarea «Revisar PLC» quedó en curso.",
                        "pregunta": None, "afirma": ["c1"]}, ensure_ascii=False)
    modelo = _ModeloLento(reloj, tarda=2.9, texto=bueno)

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
