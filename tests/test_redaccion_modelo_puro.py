"""La variante A como modelo puro (pedido del usuario, 2026-10-01): sin plazo
propio, sin plantilla de respaldo.

El plazo de 4 s y el respaldo de plantilla protegían la latencia, y a cambio
hacían que la respuesta fuera "mitad planilla, mitad modelo". Mientras dure el
experimento:

- el modelo no tiene un plazo propio (queda el timeout HTTP normal del
  proveedor, para que nada se cuelgue para siempre);
- si el verificador rechaza el texto, se le pide UNA vez más al modelo, con el
  motivo del rechazo (máximo dos intentos), en vez de caer a una plantilla;
- si falla dos veces, o el modelo da error: un incidente y un aviso neutro y
  corto, nunca en silencio y sin texto de plantilla.

`redaccion.MODELO_PURO = False` restaura el plazo y el respaldo (las pruebas del
plazo y de las plantillas corren con esa restauración).
"""

from __future__ import annotations

import json
import time

import pytest

from leda import incidentes, redaccion
from leda import ingreso_tareas as I
from leda.db import admin, espacio
from leda.incidentes import NOTICIA_NEUTRA_INCIDENTE
from leda.llm import ProveedorGuionado
from leda.resultado_turno import (Cambio, Falta, OpcionDisponible, Resumen,
                                    ResultadoTurno, ValorAceptado)
from leda.valores import TipoValor

from tests.test_alta_guiada_flujo import _cuerpos, _empezar
from tests.test_alta_guiada_mensaje_entero import _a
from tests.test_task_intake import NOW

PREGUNTA = ResultadoTurno(falta=Falta(
    "el título", TipoValor.TEXTO, pregunta="¿Qué hay que hacer?", campo="title"))
BUENO = json.dumps({"texto": "Dale. ¿Qué hay que hacer?", "pregunta": "title",
                    "afirma": []}, ensure_ascii=False)
# No pide el dato que falta: el verificador lo rechaza (`falta_pregunta`).
MALO = json.dumps({"texto": "Anoté tu pedido, ¿qué más?", "pregunta": None,
                   "afirma": []}, ensure_ascii=False)


def _incidentes_de(conn, etapa) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select severidad, referencia_cruda from incident "
                    "where etapa = %s", (etapa,))
        return cur.fetchall()


def _intentos(conn, ws) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select detalle from audit_log where workspace_id = %s "
                    "and accion = %s order by at",
                    (ws, redaccion.ACCION_REDACCION_A))
        return [f["detalle"] for f in cur.fetchall()]


def _turno(conn, ws, modelo, resultado=PREGUNTA, **kwargs):
    with admin(conn) as cur:
        return redaccion.redactar_turno(cur, ws, resultado, "A",
                                        proveedor=modelo, **kwargs)


def test_el_modo_puro_es_el_de_siempre_y_se_puede_restaurar():
    assert redaccion.MODELO_PURO is True
    assert redaccion.INTENTOS_MODELO_PURO == 2
    assert redaccion.PLAZO_REDACCION_S == 4.0       # el plazo restaurable sigue ahí


# --- sin plazo propio --------------------------------------------------------

class _Lento(ProveedorGuionado):
    def __init__(self, tarda: float, texto: str):
        super().__init__(guion=[])
        self.tarda, self.texto = tarda, texto

    def redactar(self, sistema, hechos, **kwargs):
        self.plazos.append(kwargs.get("plazo"))
        time.sleep(self.tarda)
        return self.texto


def test_un_modelo_lento_no_se_corta_y_no_recibe_plazo(intake_world, conn,
                                                       monkeypatch):
    ws = intake_world["north-lab"]["id"]
    monkeypatch.setattr(redaccion, "PLAZO_REDACCION_S", 0.05)
    modelo = _Lento(0.3, BUENO)                       # seis veces el plazo viejo

    texto = _turno(conn, ws, modelo)

    assert texto.texto == "Dale. ¿Qué hay que hacer?"
    assert modelo.plazos == [None]                    # el timeout es el del cliente
    assert [i["resultado"] for i in _intentos(conn, ws)] == ["aceptada"]
    assert _incidentes_de(conn, incidentes.ETAPA_REDACCION_FALLIDA) == []


# --- un rechazo se corrige una vez ---------------------------------------------

class _Corrige(ProveedorGuionado):
    """Un modelo que ve la corrección y la atiende en el segundo intento."""

    def __init__(self, *borradores):
        super().__init__(guion=[], borradores=list(borradores))

    @property
    def hechos(self) -> list[dict]:
        return [json.loads(h) for _, h in self.redactados]


def test_si_el_verificador_rechaza_se_vuelve_a_pedir_con_el_motivo(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    modelo = _Corrige(MALO, BUENO)

    texto = _turno(conn, ws, modelo)

    assert texto.texto == "Dale. ¿Qué hay que hacer?"      # el del modelo, no una plantilla
    assert len(modelo.redactados) == 2
    primero, segundo = modelo.hechos
    assert "correccion" not in primero
    assert segundo["correccion"]["motivo"].startswith("falta_pregunta")
    assert "Anoté tu pedido" in segundo["correccion"]["texto_anterior"]
    assert segundo["falta"] == primero["falta"]              # los mismos hechos
    # Las dos filas comparten `at` (una transacción, `now()`): la lectura de la
    # auditoría no tiene orden; el orden de los intentos ya lo prueba `modelo.hechos`.
    assert sorted(i["resultado"] for i in _intentos(conn, ws)) == ["aceptada", "rechazada"]
    assert _incidentes_de(conn, incidentes.ETAPA_REDACCION_FALLIDA) == []
    assert _incidentes_de(conn, incidentes.ETAPA_REDACCION_RECHAZADA) == []


def test_la_guia_explica_la_correccion():
    assert "`correccion`" in redaccion.SISTEMA_REDACCION
    assert len(redaccion.SISTEMA_REDACCION.splitlines()) <= 8


# --- si falla dos veces, o da error: incidente y aviso neutro -----------------

def test_dos_rechazos_seguidos_dejan_un_incidente_y_el_aviso_neutro(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    modelo = _Corrige(MALO, MALO)

    texto = _turno(conn, ws, modelo)

    assert texto.texto == NOTICIA_NEUTRA_INCIDENTE            # corto, neutro
    assert texto.fallida is True
    assert "¿Qué hay que hacer?" not in texto.texto           # sin plantilla
    assert len(modelo.redactados) == 2                        # y no más de dos
    assert [i["resultado"] for i in _intentos(conn, ws)] == ["rechazada", "rechazada"]
    (incidente,) = _incidentes_de(conn, incidentes.ETAPA_REDACCION_FALLIDA)
    assert incidente["severidad"] == "media"
    assert incidente["referencia_cruda"].count("falta_pregunta") == 2


@pytest.mark.parametrize("error,resultado", [
    (RuntimeError("cayó"), "error"), (TimeoutError("colgado"), "timeout")])
def test_un_error_del_modelo_no_se_reintenta_y_deja_el_aviso_neutro(
        error, resultado, intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    modelo = _Corrige(error, BUENO)

    texto = _turno(conn, ws, modelo)

    assert texto.texto == NOTICIA_NEUTRA_INCIDENTE and texto.fallida is True
    assert len(modelo.redactados) == 1                        # el proveedor ya reintentó
    assert [i["resultado"] for i in _intentos(conn, ws)] == [resultado]
    assert len(_incidentes_de(conn, incidentes.ETAPA_REDACCION_FALLIDA)) == 1


def test_una_salida_que_no_es_el_formato_pedido_tambien_se_corrige_una_vez(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    modelo = _Corrige("no sé qué decir", BUENO)

    texto = _turno(conn, ws, modelo)

    assert texto.texto == "Dale. ¿Qué hay que hacer?"
    assert modelo.hechos[1]["correccion"]["motivo"].startswith("formato")


# --- lo que la persona tiene que ver para decidir nunca falta ------------------

RESUMEN = ResultadoTurno(resumen=Resumen(
    "Resumen para revisar", (("Título", "Revisar el variador"),
                             ("Objetivo", "Reducir demoras")),
    "Con Confirmar se crea la tarea con estos datos."))


def test_un_resumen_sin_texto_del_modelo_sale_con_sus_datos_y_su_cierre(
        intake_world, conn):
    """F-C5: el cierre nombra el botón real y es del código, también cuando el
    modelo falla: nadie confirma sin ver el resumen."""
    ws = intake_world["north-lab"]["id"]

    texto = _turno(conn, ws, _Corrige(RuntimeError("cayó")), RESUMEN)

    assert texto.texto.startswith(NOTICIA_NEUTRA_INCIDENTE)
    assert "Título: Revisar el variador" in texto.texto
    assert texto.texto.endswith("Con Confirmar se crea la tarea con estos datos.")
    assert texto.cierre == "Con Confirmar se crea la tarea con estos datos."


def test_un_valor_que_se_pide_confirmar_sale_a_la_vista_aunque_el_modelo_falle(
        intake_world, conn, monkeypatch):
    """Los botones Sí / No confirman un valor: si el modelo falla, el valor igual
    sale a la vista (nadie lo confirma a ciegas)."""
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        _, outcome = _empezar(cur, intake_world, title="Revisar el variador")
    _a(conn, ws, monkeypatch, _Corrige(RuntimeError("cayó")))

    with espacio(conn, ws) as cur:
        texto = I._decir_pregunta(
            cur, I._request(cur, outcome.request_id), "due_date",
            TipoValor.OPCION, "¿Confirmás esta fecha? 04/10/2028", NOW,
            opciones=["Sí", "No"], propuesto="04/10/2028")

    assert texto == f"{NOTICIA_NEUTRA_INCIDENTE}\n\n04/10/2028"


# --- restaurar el plazo y el respaldo -----------------------------------------

def test_con_el_modo_restaurado_el_modelo_que_falla_cae_a_la_plantilla(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    monkeypatch.setattr(redaccion, "MODELO_PURO", False)
    modelo = _Corrige(RuntimeError("cayó"))

    texto = _turno(conn, ws, modelo)

    assert texto.texto == "¿Qué hay que hacer?"              # la plantilla de B
    assert modelo.plazos == [redaccion.PLAZO_REDACCION_S]


def test_con_b_no_se_llama_al_modelo(intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    modelo = _Corrige(BUENO)
    with admin(conn) as cur:
        texto = redaccion.redactar_turno(cur, ws, PREGUNTA, "B", proveedor=modelo)
    assert texto.texto == "¿Qué hay que hacer?" and modelo.redactados == []


# --- el alta guiada -------------------------------------------------------------

def test_en_el_alta_un_modelo_caido_deja_un_solo_mensaje_neutro_y_la_pregunta_abierta(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    _a(conn, ws, monkeypatch, _Corrige(RuntimeError("cayó")))

    with espacio(conn, ws) as cur:
        _, outcome = _empezar(cur, intake_world)
        cuerpos = _cuerpos(cur, outcome.request_id)
        cur.execute("""select campo from task_intake_free_text_slot
                        where request_id = %s and estado = 'active'""",
                    (outcome.request_id,))
        abierta = cur.fetchone()

    assert cuerpos == [NOTICIA_NEUTRA_INCIDENTE]              # una, neutra y sin plantilla
    assert abierta["campo"] == "title"                        # puede volver a escribir
    assert len(_incidentes_de(conn, incidentes.ETAPA_REDACCION_FALLIDA)) == 1
