"""Los botones de una duda, al despachar (`leda.motor.botones`; ADR 0018, decisiones 4 y 9d).

En la prueba chica los probaba el escuchador (`prueba_chica/test_escuchar.py`, "Botones y
toques"), que llega al motor con la E3-7. Acá, por el ciclo del motor, que despacha con el
transporte que agrega las opciones (`Ciclo._despachar`): la respuesta que pregunta una duda
sale con sus opciones, cada una con su token; lo que Leda manda por su cuenta nunca lleva
botones (9b), y una respuesta posterior a cerrarse la pregunta, tampoco.
"""

from __future__ import annotations

from leda.db import espacio
from leda.despachador import TransporteDePrueba
from leda.motor.ciclo import Ciclo
from leda.motor.ia import IAGuionada
from leda.motor.preguntas import callback
from leda.motor.tiempo import RelojFijo
from leda.salida import enqueue_outbox

from tests.motor.ayudantes import AHORA, toca


def _despachar(conn, mundo) -> TransporteDePrueba:
    salida = TransporteDePrueba()
    Ciclo(conn, mundo["id"], IAGuionada(), RelojFijo(AHORA), salida, seguimiento=False,
          imprimir=lambda *_: None).vuelta()
    return salida


def test_la_respuesta_que_pregunta_una_duda_sale_con_sus_opciones(conn, mundo, duda):
    [respuesta] = _despachar(conn, mundo).enviados

    assert respuesta.texto == "Listo."
    assert [(b.etiqueta, b.callback_data) for b in respuesta.botones] == [
        ("Revisar el tablero", callback(duda["O1"])),
        ("Probar las comunicaciones", callback(duda["O2"]))]


def test_lo_que_leda_manda_por_su_cuenta_nunca_lleva_botones(conn, mundo, duda):
    marcos = mundo["personas"]["Marcos"]
    _despachar(conn, mundo)
    with espacio(conn, mundo["id"]) as cur:
        enqueue_outbox(cur, workspace_id=mundo["id"], chat_id=marcos["telegram"],
                       text="Un aviso.", dedupe_key="aviso-de-prueba",
                       message_type="informativo",
                       recipient_membership_id=marcos["membership_id"], scheduled_for=AHORA)
    conn.commit()

    [aviso] = _despachar(conn, mundo).enviados

    assert (aviso.texto, aviso.botones) == ("Un aviso.", [])


def test_una_respuesta_despues_de_cerrarse_la_pregunta_sale_sin_botones(conn, mundo, duda):
    _despachar(conn, mundo)
    toca(conn, mundo, duda["O2"], IAGuionada(redacciones=["Anotado."]))

    [respuesta] = _despachar(conn, mundo).enviados

    assert (respuesta.texto, respuesta.botones) == ("Anotado.", [])
