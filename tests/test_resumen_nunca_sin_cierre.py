"""El resumen para revisar nunca sale sin el cierre que nombra el botón (F-C5).

El resumen de las 08:18:47 salió sin su cierre ("Con Confirmar se crea la tarea
con estos datos."): la persona tenía el botón y no el texto que dice qué hace. El
cierre es una parte propia del texto, del código, y se cumple por estructura: sea
cual sea el camino de la redacción (el modelo acepta, rechaza dos veces, da error,
tarda, o un defecto devuelve un texto sin cierre), el resumen termina en su cierre.
"""

from __future__ import annotations

import json

import pytest

from leda import incidentes, redaccion
from leda import ingreso_tareas as I
from leda.db import admin
from leda.llm import ProveedorGuionado
from leda.redaccion import TextoRedactado

from tests.test_alta_eleccion_confirmacion import _alta_en_confirmacion
from tests.test_alta_guiada_mensaje_entero import _a

DATOS = dict(title="Revisar el variador", objective="Reducir demoras",
             area="Servicio", responsible="Sam North", due_date="04/10/2028",
             acceptance_criterion="Acta firmada", evidence=["registro de prueba"])


class _Modelo(ProveedorGuionado):
    def __init__(self, *borradores):
        super().__init__(guion=[], borradores=list(borradores))


APERTURA = json.dumps({"texto": "Listo, revisalo:", "pregunta": None, "afirma": []},
                      ensure_ascii=False)
RECHAZADA = json.dumps({"texto": "Ya creé la tarea.", "pregunta": None,
                        "afirma": ["tarea_creada"]}, ensure_ascii=False)


@pytest.mark.parametrize("borradores", [
    [APERTURA],                                   # el modelo acepta
    [RECHAZADA, RECHAZADA],                       # rechaza dos veces
    [RuntimeError("cayó")],                       # da error
    [TimeoutError("colgado")],                    # tarda
    ["{}"],                                       # sin el formato pedido (y no sirve)
])
@pytest.mark.parametrize("cierre", [I.CIERRE_CONFIRMAR, I.cierre_enviar("Morgan Hale")])
def test_el_resumen_termina_en_su_cierre_pase_lo_que_pase_con_el_modelo(
        borradores, cierre, intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    _a(conn, ws, monkeypatch, _Modelo(*borradores))

    with admin(conn) as cur:
        resumen = I.render_resumen(**DATOS, cierre=cierre, variante="A", cur=cur,
                                   workspace_id=ws)

    assert resumen.cierre == cierre
    assert resumen.texto.endswith("\n\n" + cierre)
    assert "Título: Revisar el variador" in resumen.texto


def test_un_texto_sin_cierre_se_corrige_y_queda_registrado(
        intake_world, conn, monkeypatch):
    """Defensa en profundidad: si un defecto devuelve el resumen sin su cierre, el
    cierre se vuelve a poner (nadie recibe un botón sin su texto) y queda un
    incidente, nunca en silencio."""
    ws = intake_world["north-lab"]["id"]
    monkeypatch.setattr(
        I, "redactar_turno",
        lambda *a, **k: TextoRedactado("Resumen para revisar\nTítulo: x\n"))

    with admin(conn) as cur:
        resumen = I.render_resumen(**DATOS, variante="A", cur=cur, workspace_id=ws)
        cur.execute("select severidad from incident where etapa = %s",
                    (incidentes.ETAPA_RESUMEN_SIN_CIERRE,))
        incidentes_ = cur.fetchall()

    assert resumen.texto == "Resumen para revisar\nTítulo: x\n\n" + I.CIERRE_CONFIRMAR
    assert resumen.cierre == I.CIERRE_CONFIRMAR
    assert len(incidentes_) == 1


@pytest.mark.parametrize("borradores", [[RuntimeError("cayó")], [RECHAZADA, RECHAZADA]])
def test_el_resumen_de_un_alta_con_el_modelo_caido_sale_con_su_cierre_y_botones(
        borradores, intake_world, conn, monkeypatch):
    """El caso de las 08:18:47 de punta a punta: el alta llega al resumen con el
    modelo fallando; lo que sale, con sus botones, termina en el cierre."""
    ws = intake_world["north-lab"]["id"]
    _a(conn, ws, monkeypatch, _Modelo(*borradores * 20))

    rid, pid = _alta_en_confirmacion(conn, intake_world)

    with admin(conn) as cur:
        cur.execute("select resumen from pending_action where id = %s", (pid,))
        texto = cur.fetchone()["resumen"]
        cur.execute("select cuerpo from message_outbox where pending_action_id = %s",
                    (pid,))
        enviado = cur.fetchone()["cuerpo"]
    assert texto.endswith("\n\n" + I.CIERRE_CONFIRMAR)
    assert enviado.endswith("\n\n" + I.CIERRE_CONFIRMAR)
