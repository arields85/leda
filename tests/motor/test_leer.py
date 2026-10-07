"""El lector del registro de turnos (`leda.motor.leer`).

Para leer una prueba real sin capturas: los turnos en orden (sentido, texto, jugadas, hechos,
toques como la opción tocada, errores y latencias), las preguntas abiertas y para después, las
esperas y los avisos guardados con su estado. Sólo lee. La conversación de la prueba se arma con
el turno de verdad, la IA guionada y el reloj fijo.

Portadas de `prueba_chica/test_leer.py` (E2-6), borrada el 2026-10-07.
"""

from __future__ import annotations

from zoneinfo import ZoneInfo

import pytest

from leda.motor.escalera import correr_escalera
from leda.motor.ia import IAGuionada, Jugada
from leda.motor.leer import desde_texto, leer
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import procesar_turno

from tests.motor.ayudantes import AHORA, IAQueRedacta, cuantas, enviar, octubre, toca

TABLAS = ("conversation_turn", "conversation_question", "pending_reply", "scheduled_notice",
          "message_outbox")


@pytest.fixture
def charla(conn, mundo, escribe, espacio_con_escalera, duda) -> dict:
    """Marcos arrancó sin decir cuál (duda con botones), tocó una opción, dio una previsión, y
    un mensaje suyo quedó sin respuesta de la IA; el día de la previsión (9i), la escalera le
    pidió el estado."""
    toca(conn, mundo, duda["O2"])
    quien, entrante = escribe("Marcos", "llego el 14, el proveedor")
    procesar_turno(conn, quien, entrante,
                   IAGuionada(jugadas=[[Jugada("anotar_prevision",
                                               {"tarea": "T1", "fecha": "2026-10-14",
                                                "motivo": "el proveedor"})]],
                              redacciones=["Anotado el 14."]), RelojFijo(AHORA))
    conn.commit()
    quien, entrante = escribe("Marcos", "y esto?")
    procesar_turno(conn, quien, entrante,
                   IAGuionada(jugadas=[ConnectionError("sin red"), TimeoutError("tarde")]),
                   RelojFijo(AHORA))
    conn.commit()
    correr_escalera(conn, mundo["id"], RelojFijo(octubre(14, 10)))
    conn.commit()
    enviar(conn, mundo, IAQueRedacta(), octubre(14, 10))
    return mundo


def test_el_lector_muestra_turnos_preguntas_esperas_y_avisos(conn, charla):
    antes = {t: cuantas(conn, t) for t in TABLAS}

    texto = leer(conn, charla["id"], completo=True)

    secciones = ["Turnos", "Preguntas abiertas y para después", "Esperas de respuesta",
                 "Avisos guardados"]
    assert [linea for linea in texto.splitlines() if linea in secciones] == secciones
    turnos = texto.split("Preguntas abiertas")[0]
    assert '← "hoy arranque"' in turnos
    assert "jugadas: anotar_inicio {}" in turnos
    assert "tocó «Probar las comunicaciones»" in turnos
    assert '← "llego el 14, el proveedor"' in turnos
    assert "jugadas: anotar_prevision {" in turnos and '"fecha": "2026-10-14"' in turnos
    assert '"atraso_si_se_cumple_la_prevision_dias_habiles": 2' in turnos                     # los hechos
    assert "error: ia_no_respondio: TimeoutError" in turnos
    assert "Leda → Marcos" in turnos and '"Aviso 2."' in turnos     # el pedido del 14
    assert " ms" in turnos
    # Los turnos van en orden: la entrada antes de su respuesta.
    assert turnos.index("hoy arranque") < turnos.index("tocó") < turnos.index("llego el 14")
    preguntas = texto.split("Preguntas abiertas y para después")[1].split("Esperas")[0]
    assert "Marcos · estado_de_la_tarea · Revisar el tablero" in preguntas
    esperas = texto.split("Esperas de respuesta")[1].split("Avisos guardados")[0]
    assert "Marcos · Revisar el tablero" in esperas and "recordatorios 1" in esperas
    avisos = texto.split("Avisos guardados")[1]
    assert "nueva_prevision → Ismael · Revisar el tablero · enviado" in avisos
    assert "pedido_de_estado → Marcos · Revisar el tablero · enviado" in avisos
    # Sólo lee.
    assert {t: cuantas(conn, t) for t in TABLAS} == antes


def test_el_lector_filtra_por_persona_y_desde_una_hora(conn, charla):
    de_ismael = leer(conn, charla["id"], persona="ismael")
    assert "hoy arranque" not in de_ismael and "nueva_prevision → Ismael" in de_ismael
    assert "pedido_de_estado → Marcos" not in de_ismael

    desde_el_viernes = leer(conn, charla["id"], desde=octubre(9, 9))
    turnos = desde_el_viernes.split("Preguntas abiertas")[0]
    assert "hoy arranque" not in turnos and '"Aviso 2."' in turnos

    with pytest.raises(ValueError, match="nadie"):
        leer(conn, charla["id"], persona="nahuel")


def test_el_lector_corta_los_textos_largos_sin_completo(conn, mundo, escribe):
    quien, entrante = escribe("Marcos", "x" * 400)
    procesar_turno(conn, quien, entrante,
                   IAGuionada(jugadas=[[]], redacciones=["Listo."]), RelojFijo(AHORA))
    conn.commit()

    assert '"' + "x" * 300 + '…"' in leer(conn, mundo["id"])
    assert '"' + "x" * 400 + '"' in leer(conn, mundo["id"], completo=True)


def test_desde_acepta_una_hora_de_hoy_o_una_fecha_con_hora():
    zona = ZoneInfo("America/Argentina/Buenos_Aires")

    assert desde_texto("09:00", octubre(9, 15), zona) == octubre(9, 9)
    assert desde_texto("2026-10-05 10:00", octubre(9, 15), zona) == AHORA
    with pytest.raises(ValueError):
        desde_texto("ayer", octubre(9, 15), zona)


def test_el_comando_lee_con_una_conexion_recien_abierta(conn, mundo, uri, monkeypatch, capsys):
    """`conectar` fija la ruta de búsqueda sin confirmarla; el comando no puede perderla al
    cerrar su primera transacción (E2-9: con la base recreada, el lector no encontraba
    `workspace`)."""
    import leda.db

    from leda.motor.leer import main

    conn.commit()
    original = leda.db.conectar
    monkeypatch.setattr(leda.db, "conectar", lambda url=None: original(uri))

    assert main(["prueba"]) == 0
    assert "Turnos" in capsys.readouterr().out
    assert main(["no-existe"]) == 1
    assert "No hay un espacio 'no-existe'." in capsys.readouterr().out
