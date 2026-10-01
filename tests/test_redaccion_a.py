"""La variante A de la redacción (ADR 0014, etapa 6): el modelo redacta el
mensaje entero sobre los hechos del turno (salida estructurada
`{texto, pregunta, afirma}`), el código verifica y, si el texto no sirve o el
modelo falla, sale la plantilla de B, que lo reemplaza, y queda registrado
con la duración de la llamada.

El modelo se guiona con `ProveedorGuionado.borradores`: ninguna prueba toca la
red.
"""

from __future__ import annotations

import json

import pytest

from prisma import incidentes, redaccion
from prisma.db import admin, espacio
from prisma.llm import ProveedorGuionado
from prisma.resultado_turno import (
    Cambio, Estado, Falta, OpcionDisponible, ResultadoTurno, Resumen,
    ValorAceptado,
)
from prisma.valores import TipoValor

EN_CURSO = ResultadoTurno(
    cambios=(Cambio("la tarea «Revisar PLC»", "quedó en curso"),),
    estado=(Estado("«Revisar PLC»", "en curso"),))


def _json(texto, pregunta=None, afirma=()):
    """Lo que devuelve el modelo: el JSON pedido."""
    return json.dumps({"texto": texto, "pregunta": pregunta, "afirma": list(afirma)},
                      ensure_ascii=False)


BUENO = _json("Listo, la tarea «Revisar PLC» quedó en curso.", afirma=["c1"])


def _proveedor(*borradores) -> ProveedorGuionado:
    return ProveedorGuionado(guion=[], borradores=list(borradores))


def _intentos(conn, ws) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(
            "select detalle from audit_log where workspace_id = %s and accion = %s "
            "order by at", (ws, redaccion.ACCION_REDACCION_A))
        return [f["detalle"] for f in cur.fetchall()]


def _incidentes(conn, ws) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(
            "select severidad, resumen_sanitizado, referencia_cruda, etapa, "
            "notificado_admin_en from incident "
            "where workspace_id = %s and etapa = %s order by at",
            (ws, incidentes.ETAPA_REDACCION_RECHAZADA))
        return cur.fetchall()


def _redactar(conn, ws, resultado, proveedor, variante="A"):
    with espacio(conn, ws) as cur:
        return redaccion.redactar_turno(cur, ws, resultado, variante,
                                        proveedor=proveedor)


# ------------------------------------------------------------ el texto del modelo

def test_a_usa_el_texto_del_modelo_si_el_verificador_lo_acepta(corework, conn):
    ws = corework.workspace_id
    proveedor = _proveedor(BUENO)

    texto = _redactar(conn, ws, EN_CURSO, proveedor)

    assert texto.texto == "Listo, la tarea «Revisar PLC» quedó en curso."
    (sistema, hechos) = proveedor.redactados[0]
    assert "Prisma" in sistema and "JSON" in sistema
    datos = json.loads(hechos)
    assert datos["cambios"] == [{"id": "c1", "sujeto": "la tarea «Revisar PLC»",
                                 "que": "quedó en curso"}]
    assert _incidentes(conn, ws) == []


def test_los_hechos_para_el_modelo_llevan_las_etiquetas_pero_no_el_cierre():
    r = ResultadoTurno(
        resumen=Resumen("Resumen para revisar", (("Título", "Revisar PLC"),),
                        "Con Confirmar se crea la tarea con estos datos."),
        falta=Falta("la fecha objetivo", TipoValor.FECHA, pregunta="¿Para cuándo?",
                    campo="due_date"),
        valores_aceptados=(ValorAceptado("la fecha objetivo", "04/10/2026"),),
        entendido=(ValorAceptado("el título", "Revisar PLC"),),
        opciones=(OpcionDisponible("Confirmar", "confirmar"),))
    datos = json.loads(redaccion.serializar_hechos(r))
    assert "Con Confirmar se crea" not in json.dumps(datos, ensure_ascii=False)
    # Las opciones son contexto (para qué sirve la pregunta): sólo la etiqueta.
    assert datos["opciones"] == ["Confirmar"]
    assert datos["resumen"] == {"titulo": "Resumen para revisar",
                                "datos": [{"dato": "Título", "valor": "Revisar PLC"}]}
    assert datos["falta"] == {"campo": "due_date", "dato": "la fecha objetivo",
                              "tipo": "fecha", "pregunta": "¿Para cuándo?"}
    assert datos["entendido"] == [{"dato": "el título", "valor": "Revisar PLC"}]


def test_con_un_resumen_el_modelo_escribe_la_apertura_y_los_datos_y_el_cierre_son_del_codigo(
        corework, conn):
    cierre = "Con Confirmar se crea la tarea con estos datos."
    r = ResultadoTurno(resumen=Resumen(
        "Resumen para revisar", (("Título", "Revisar PLC"),), cierre))
    bloque = "Resumen para revisar\nTítulo: Revisar PLC"
    apertura = "Listo, ya está el borrador. Revisalo:"

    texto = _redactar(conn, corework.workspace_id, r,
                      _proveedor(_json(apertura)))

    assert texto.cuerpo == apertura + "\n\n" + bloque and texto.cierre == cierre
    assert texto.texto == apertura + "\n\n" + bloque + "\n\n" + cierre


def test_una_plantilla_propia_de_b_es_el_respaldo_cuando_hay(corework, conn):
    """Un texto que B ya tenía antes del resultado (no la plantilla genérica)
    sale tal cual si A no sirve."""
    from prisma.redaccion import TextoRedactado

    propia = TextoRedactado("Le mandé el borrador a Morgan.")
    resultado = ResultadoTurno(cambios=(Cambio("el borrador", "quedó enviado",
                                               id="enviado"),))
    texto = _redactar_con_base(conn, corework.workspace_id, resultado,
                               _proveedor(_json("Listo.", afirma=[])), propia)
    assert texto == propia


def _redactar_con_base(conn, ws, resultado, proveedor, base):
    with espacio(conn, ws) as cur:
        return redaccion.redactar_turno(cur, ws, resultado, "A", proveedor=proveedor,
                                        base=base)


# ------------------------------------------------------------ el respaldo de B

@pytest.mark.parametrize("borrador", [
    # un número inventado
    _json("Listo, la tarea «Revisar PLC» quedó en curso en 2 minutos.",
          afirma=["c1"]),
    _json("Listo, quedó en curso.", afirma=["c1"]),               # falta el nombre
    _json("Listo, «Revisar PLC» quedó en curso.", afirma=["c1", "c2"]),  # otro efecto
    _json("Listo, «Revisar PLC» quedó en curso.", afirma=[]),     # omite el efecto
    "Listo, la tarea «Revisar PLC» quedó en curso.",              # no es el JSON pedido
])
def test_un_texto_rechazado_se_reemplaza_por_la_plantilla_de_b_y_queda_registrado(
        borrador, corework, conn):
    ws = corework.workspace_id

    texto = _redactar(conn, ws, EN_CURSO, _proveedor(borrador))

    assert texto == redaccion.redactar_partes(EN_CURSO, "B")
    (intento,) = _intentos(conn, ws)
    assert intento["resultado"] == "rechazada" and intento["motivo"]
    assert isinstance(intento["duracion_ms"], (int, float))
    (incidente,) = _incidentes(conn, ws)
    assert incidente["severidad"] == "baja"
    assert intento["motivo"] in incidente["referencia_cruda"]
    # No avisa a la administración por cada rechazo: es dato del experimento.
    assert incidente["notificado_admin_en"] is None


@pytest.mark.parametrize("error", [TimeoutError("colgado"), RuntimeError("cayó")])
def test_si_el_modelo_falla_o_se_cuelga_sale_b_y_queda_registrado(error, corework, conn):
    ws = corework.workspace_id

    texto = _redactar(conn, ws, EN_CURSO, _proveedor(error))

    assert texto == redaccion.redactar_partes(EN_CURSO, "B")
    (intento,) = _intentos(conn, ws)
    assert intento["resultado"] == "error"
    assert type(error).__name__ in intento["motivo"]
    (incidente,) = _incidentes(conn, ws)
    assert type(error).__name__ in incidente["referencia_cruda"]


def test_un_defecto_del_verificador_cae_en_b_y_queda_registrado(
        corework, conn, monkeypatch):
    def roto(*args, **kwargs):
        raise RuntimeError("defecto del verificador")

    monkeypatch.setattr(redaccion, "verificar", roto)
    ws = corework.workspace_id

    texto = _redactar(conn, ws, EN_CURSO, _proveedor(BUENO))

    assert texto == redaccion.redactar_partes(EN_CURSO, "B")
    (intento,) = _intentos(conn, ws)
    assert intento["resultado"] == "error" and "RuntimeError" in intento["motivo"]
    assert len(_incidentes(conn, ws)) == 1


def test_el_texto_de_la_excepcion_de_un_proveedor_no_se_guarda(corework, conn):
    ws = corework.workspace_id
    secreto = "https://user:clave-secreta@modelo.example/v1"

    _redactar(conn, ws, EN_CURSO, _proveedor(RuntimeError(secreto)))

    (intento,) = _intentos(conn, ws)
    assert "RuntimeError" in intento["motivo"] and "clave-secreta" not in intento["motivo"]
    (incidente,) = _incidentes(conn, ws)
    assert "clave-secreta" not in incidente["referencia_cruda"]


def test_un_texto_vacio_del_modelo_tambien_cae_en_b(corework, conn):
    texto = _redactar(conn, corework.workspace_id, EN_CURSO, _proveedor(""))
    assert texto == redaccion.redactar_partes(EN_CURSO, "B")
    assert _intentos(conn, corework.workspace_id)[0]["resultado"] == "rechazada"


def test_sin_modelo_configurado_sale_b_y_queda_registrado(corework, conn, monkeypatch):
    def sin_modelo(cur, workspace_id):
        raise LookupError("No hay modelo configurado.")

    monkeypatch.setattr(redaccion, "proveedor_de_redaccion", sin_modelo)
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        texto = redaccion.redactar_turno(cur, ws, EN_CURSO, "A")
    assert texto == redaccion.redactar_partes(EN_CURSO, "B")
    assert _intentos(conn, ws)[0]["resultado"] == "error"
    assert len(_incidentes(conn, ws)) == 1


# ------------------------------------------------------------ B no cambia

def test_b_no_llama_al_modelo_ni_registra_nada(corework, conn):
    ws = corework.workspace_id
    proveedor = _proveedor(BUENO)

    texto = _redactar(conn, ws, EN_CURSO, proveedor, variante="B")

    assert texto == redaccion.redactar_partes(EN_CURSO, "B")
    assert proveedor.redactados == []
    assert _intentos(conn, ws) == [] and _incidentes(conn, ws) == []


def test_b_ignora_lo_entendido_y_las_opciones():
    con_contexto = ResultadoTurno(
        falta=Falta("la fecha objetivo", TipoValor.FECHA, pregunta="¿Para cuándo?",
                    campo="due_date"),
        entendido=(ValorAceptado("el título", "Revisar PLC"),),
        opciones=(OpcionDisponible("Confirmar", "confirmar"),))
    sin_contexto = ResultadoTurno(
        falta=Falta("la fecha objetivo", TipoValor.FECHA, pregunta="¿Para cuándo?"))
    assert (redaccion.redactar(con_contexto, "B")
            == redaccion.redactar(sin_contexto, "B") == "¿Para cuándo?")


# ------------------------------------------------------------ latencia

def test_cada_intento_registra_la_duracion_y_se_resume_con_la_mediana(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    reloj = iter([0.0, 1.0,       # 1000 ms, aceptada
                  10.0, 13.0,     # 3000 ms, aceptada
                  20.0, 25.0,     # 5000 ms, rechazada
                  30.0, 40.0])    # 10000 ms, error

    monkeypatch.setattr(redaccion, "_reloj", lambda: next(reloj))
    _redactar(conn, ws, EN_CURSO, _proveedor(BUENO))
    _redactar(conn, ws, EN_CURSO, _proveedor(BUENO))
    _redactar(conn, ws, EN_CURSO, _proveedor(_json("Hola.")))
    _redactar(conn, ws, EN_CURSO, _proveedor(TimeoutError("x")))

    assert [i["duracion_ms"] for i in _intentos(conn, ws)] == [1000, 3000, 5000, 10000]
    with admin(conn) as cur:
        e = redaccion.estadistica_variante_a(cur, ws)
    assert e["llamadas"] == 4
    assert (e["aceptadas"], e["rechazadas"], e["errores"]) == (2, 1, 1)
    assert e["mediana_ms"] == 4000          # entre 3000 y 5000
    assert e["mediana_aceptadas_ms"] == 2000
    assert e["maximo_ms"] == 10000


def test_la_estadistica_sin_intentos_no_inventa_una_mediana(corework, conn):
    with admin(conn) as cur:
        e = redaccion.estadistica_variante_a(cur, corework.workspace_id)
    assert e["llamadas"] == 0 and e["mediana_ms"] is None
