"""Una fecha que atrasa lleva su explicación (decisión del usuario, 2026-10-07; ADR 0018, 9n).

"Pasar una fecha sin motivo no es una buena idea, tiene que haber una explicación." Antes, una
fecha nueva sin porqué se anotaba sin porqué y el aviso a quien aprueba el trabajo salía con la
fecha sola (conversación 08). Ahora, como regla general de la ficha de la previsión y no para un
mensaje:

1. Si la fecha nueva queda después del vencimiento y la persona no dio el porqué, Leda anota la
   fecha y pregunta qué la atrasa (`preguntas.MOTIVO_DEL_ATRASO`, una pregunta que espera
   respuesta, con su escalera). Si la fecha no atrasa la tarea, no pregunta nada. Si corre otra
   vez una fecha que ya atrasaba la tarea y cuyo porqué dio hace menos de una hora, ése sigue
   siendo el porqué del atraso: no se le vuelve a preguntar (constitución §8; conversación 05,
   paso 4). Si pasó más, se le pregunta otra vez (usuario, 2026-10-07: "para Leda es difícil
   saber que se refiere a ese motivo; hay que poner un límite de tiempo más corto"). Los minutos
   son del espacio (`motivo_vale_minutos`, 60 por omisión) y se cuentan desde que lo dijo. Y
   la conversación tiene que haber seguido en esa tarea: un mensaje de la persona en el medio
   sobre otra tarea u otro tema corta el hilo, y Leda vuelve a preguntar (usuario, 2026-10-07).
2. El aviso al referente espera esa respuesta y sale con el porqué, en palabras de la persona,
   después del margen para corregir y dentro del horario.
3. Si no contesta, el aviso no espera para siempre: sale al terminar el día de trabajo
   (`tiempo.al_terminar_el_dia`) y dice que todavía no dio el porqué, nunca uno inventado. La
   pregunta sigue abierta para la persona y la escalera la repite.
4. Una corrección que pasa la fecha a otra tarea mueve sólo la fecha: el porqué se dijo de la
   otra. Si la fecha atrasa la tarea correcta, se pregunta su porqué.
5. Con otra pregunta abierta, una a la vez, con el mecanismo de siempre (`preguntas.abrir`).

El reloj es el de las pruebas del motor: el lunes 5 de octubre de 2026, 10:00 en Buenos Aires,
con el horario de 09:00 a 17:00; la tarea "Revisar el tablero" (T1) de Marcos vence el viernes 9.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from leda.calendario import Calendario
from leda.db import espacio
from leda.motor import hechos as vocabulario
from leda.motor import preguntas
from leda.motor.ia import IAGuionada, Jugada
from leda.motor import margen, tiempo
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import procesar_turno

from tests.motor.ayudantes import (AHORA, abierta, avisos_guardados, dice, enviar,
                                   jugada_bloqueo, jugada_prevision, nueva_tarea, octubre, todos,
                                   uno)

MOTIVO = "motivo_del_atraso"          # preguntas.MOTIVO_DEL_ATRASO


def _turno(conn, escribe, *jugadas: Jugada, at: datetime = AHORA) -> tuple[list[dict], dict]:
    """Un mensaje de Marcos: los hechos del turno y el pedido de redacción."""
    quien, entrante = escribe("Marcos", "-", at=at)
    ia = IAGuionada(jugadas=[list(jugadas)], redacciones=["Listo."])
    resultado = procesar_turno(conn, quien, entrante, ia, RelojFijo(at))
    conn.commit()
    assert resultado.error is None
    return resultado.hechos, ia.pedidos_de_redaccion[-1]


def _preguntas_sin_cerrar(conn, tipo: str = MOTIVO) -> list[dict]:
    return todos(conn, """select * from conversation_question
                           where tipo = %s and cerrada_en is null order by abierta_en""", tipo)


def _esperas(conn, tipo: str = MOTIVO) -> list[dict]:
    return todos(conn, "select * from pending_reply where tipo = %s order by preguntado_en",
                 tipo)


# --- El final del día de trabajo -------------------------------------------------------------

@pytest.mark.parametrize("ahora, termina", [
    (octubre(5, 10), octubre(5, 16, 30)),       # media hora antes del cierre (17:00)
    (octubre(5, 8), octubre(5, 16, 30)),        # antes del horario: el de ese día
    (octubre(5, 16, 45), octubre(5, 16, 30)),   # ya pasó: quien llama toma la hora más tarde
    (octubre(5, 20), octubre(6, 16, 30)),       # de noche: el del día hábil siguiente
    (octubre(10, 11), octubre(12, 16, 30)),     # sábado: el del lunes
], ids=["jornada", "temprano", "pasada", "noche", "sabado"])
def test_el_dia_de_trabajo_termina_media_hora_antes_del_cierre(conn, mundo, ahora, termina):
    with espacio(conn, mundo["id"]) as cur:
        cal = Calendario.desde_base(cur, mundo["id"])
    conn.commit()
    assert tiempo.al_terminar_el_dia(cal, ahora) == termina


@pytest.mark.parametrize("ahora, sale", [
    (octubre(5, 10), octubre(5, 16, 30)),       # espera el porqué hasta el final del día
    (octubre(5, 16, 45), octubre(5, 16, 55)),   # dicho al final del día: sólo el margen
    (octubre(5, 16, 55), octubre(6, 16, 30)),   # el margen pasa el cierre: el día siguiente
    (octubre(5, 20), octubre(6, 16, 30)),       # de noche: el final del día hábil siguiente
], ids=["jornada", "al-final", "margen-pasa-el-cierre", "noche"])
def test_el_aviso_sin_porque_sale_al_terminar_el_dia_y_nunca_antes_del_margen(conn, mundo, ahora,
                                                                             sale):
    with espacio(conn, mundo["id"]) as cur:
        cal = Calendario.desde_base(cur, mundo["id"])
        assert margen.sale_esperando_el_motivo(cur, cal, mundo["id"], ahora) == sale
    conn.commit()


# --- 1. Una fecha que atrasa, sin porqué -------------------------------------------------------

def test_una_fecha_que_atrasa_sin_porque_pregunta_que_la_atrasa_y_el_aviso_espera(
        conn, mundo, escribe):
    [hecho], pedido = _turno(conn, escribe, jugada_prevision("T1", "2026-10-13"))

    # La fecha queda anotada igual: el porqué no es una condición para anotarla.
    [prevision] = todos(conn, "select * from task_forecast")
    assert prevision["fecha_prevista"].isoformat() == "2026-10-13"
    assert prevision["motivo"] is None
    assert hecho["resultado"] == "anotado" and hecho["motivo"] is None
    # Leda pregunta qué la atrasa: es la pregunta de esta respuesta, que espera respuesta.
    assert hecho["pregunta"] == MOTIVO
    assert pedido["pregunta"]["tipo"] == MOTIVO
    assert abierta(conn) == (MOTIVO, mundo["tarea"])
    [espera] = _esperas(conn)
    assert str(espera["task_id"]) == mundo["tarea"] and espera["satisfecho_en"] is None
    assert not preguntas.TIPOS[preguntas.MOTIVO_DEL_ATRASO].se_puede_dejar
    # El aviso a Ismael espera el porqué hasta el final del día de trabajo, y el hecho lo dice.
    assert hecho["aviso_al_referente"] == {"a": "Ismael", "llega": "2026-10-05T16:30:00-03:00",
                                           "espera_el_motivo": True}
    [aviso] = avisos_guardados(conn, "nueva_prevision")
    assert aviso["programado_para"] == octubre(5, 16, 30)
    assert aviso["hechos"]["sin_motivo_todavia"] is True
    assert aviso["hechos"]["motivo"] is None
    # Todo lo que recibe la redacción tiene su significado (`hechos.py`).
    assert vocabulario.sin_significado(pedido) == set()
    assert vocabulario.sin_significado(aviso["hechos"]) == set()


def test_una_fecha_que_no_atrasa_no_pregunta_el_porque(conn, mundo, escribe):
    """Antes del vencimiento (un adelanto) no hay atraso que explicar: el aviso sale con el
    margen, como siempre."""
    [hecho], pedido = _turno(conn, escribe, jugada_prevision("T1", "2026-10-08"))

    assert hecho["resultado"] == "anotado"
    assert "pregunta" not in hecho and pedido["pregunta"] is None
    assert _preguntas_sin_cerrar(conn) == [] and _esperas(conn) == []
    assert hecho["aviso_al_referente"] == {"a": "Ismael", "llega": "2026-10-05T10:10:00-03:00"}
    [aviso] = avisos_guardados(conn, "nueva_prevision")
    assert "sin_motivo_todavia" not in aviso["hechos"]


def test_una_fecha_que_atrasa_con_su_porque_no_pregunta_nada(conn, mundo, escribe):
    [hecho], pedido = _turno(conn, escribe,
                             jugada_prevision("T1", "2026-10-13", "faltan los cables"))

    assert "pregunta" not in hecho and pedido["pregunta"] is None
    assert _preguntas_sin_cerrar(conn) == []
    assert hecho["aviso_al_referente"] == {"a": "Ismael", "llega": "2026-10-05T10:10:00-03:00"}


def test_correr_otra_vez_un_atraso_ya_explicado_conserva_su_porque(conn, mundo, escribe):
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-13", "faltan los cables"))
    [hecho], pedido = _turno(conn, escribe, jugada_prevision("T1", "2026-10-14"),
                             at=octubre(5, 10, 30))

    assert hecho["motivo"] == "faltan los cables"
    assert "pregunta" not in hecho and pedido["pregunta"] is None
    assert _preguntas_sin_cerrar(conn) == []
    segunda = uno(conn, "select motivo from task_forecast where fecha_prevista = '2026-10-14'")
    assert segunda["motivo"] == "faltan los cables"
    _, con_porque = avisos_guardados(conn, "nueva_prevision")
    assert con_porque["hechos"]["motivo"] == "faltan los cables"
    assert con_porque["programado_para"] == octubre(5, 10, 40)
    # La auditoría separa lo que dijo ahora de lo que había dicho antes.
    auditado = uno(conn, """select detalle from audit_log where accion = 'anotar_prevision'
                             order by at desc, id desc limit 1""")
    assert auditado["detalle"]["motivo_dicho_antes"] is True


def _vale_minutos(conn, mundo, valor: str) -> None:
    from leda.db import admin
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, 'motivo_vale_minutos', %s)""", (mundo["id"], valor))
    conn.commit()


def test_un_porque_de_hace_mas_de_una_hora_no_explica_la_fecha_nueva(conn, mundo, escribe):
    """Pasó más de una hora: puede no referirse a ese porqué, así que Leda lo pregunta otra vez."""
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-13", "faltan los cables"))
    [hecho], _ = _turno(conn, escribe, jugada_prevision("T1", "2026-10-14"), at=octubre(5, 11, 1))

    assert hecho["motivo"] is None and hecho["pregunta"] == MOTIVO
    assert hecho["aviso_al_referente"]["espera_el_motivo"] is True


def test_la_hora_se_cuenta_desde_que_lo_dijo_no_desde_la_ultima_fecha(conn, mundo, escribe):
    """El porqué que se conservó no vuelve a empezar la cuenta: a las 11:10 lo dijo hace 70
    minutos, aunque la última fecha fue a las 10:30."""
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-13", "faltan los cables"))
    [conservado], _ = _turno(conn, escribe, jugada_prevision("T1", "2026-10-14"),
                             at=octubre(5, 10, 30))
    [otra_vez], _ = _turno(conn, escribe, jugada_prevision("T1", "2026-10-15"),
                           at=octubre(5, 11, 10))

    assert conservado["motivo"] == "faltan los cables"
    assert otra_vez["motivo"] is None and otra_vez["pregunta"] == MOTIVO


def test_el_espacio_cambia_cuantos_minutos_vale_un_porque(conn, mundo, escribe):
    _vale_minutos(conn, mundo, "120")
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-13", "faltan los cables"))

    [a_la_hora_y_media], _ = _turno(conn, escribe, jugada_prevision("T1", "2026-10-14"),
                                    at=octubre(5, 11, 30))
    assert a_la_hora_y_media["motivo"] == "faltan los cables"
    [pasadas_dos_horas], _ = _turno(conn, escribe, jugada_prevision("T1", "2026-10-15"),
                                    at=octubre(5, 12, 1))
    assert pasadas_dos_horas["motivo"] is None and pasadas_dos_horas["pregunta"] == MOTIVO


@pytest.mark.parametrize("valor", ['"uno"', "-1", "true", "null", "1.5"])
def test_un_valor_que_no_vale_usa_la_hora_del_producto(conn, mundo, escribe, valor):
    _vale_minutos(conn, mundo, valor)
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-13", "faltan los cables"))
    [dentro], _ = _turno(conn, escribe, jugada_prevision("T1", "2026-10-14"), at=octubre(5, 10, 30))
    [fuera], _ = _turno(conn, escribe, jugada_prevision("T1", "2026-10-15"), at=octubre(5, 11, 1))

    assert dentro["motivo"] == "faltan los cables"
    assert fuera["motivo"] is None and fuera["pregunta"] == MOTIVO


def test_un_mensaje_sobre_otra_tarea_en_el_medio_corta_el_hilo(conn, mundo, escribe):
    """10:00 el porqué de T1; 10:20 habla de T2; 10:40 otra fecha de T1: ya no se sobreentiende
    que es el mismo porqué, aunque no pasó una hora."""
    nueva_tarea(conn, mundo, "Probar las comunicaciones")
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-13", "faltan los cables"))
    _turno(conn, escribe, Jugada("anotar_inicio", {"tarea": "T2"}), at=octubre(5, 10, 20))
    [hecho], _ = _turno(conn, escribe, jugada_prevision("T1", "2026-10-14"),
                        at=octubre(5, 10, 40))

    assert hecho["motivo"] is None and hecho["pregunta"] == MOTIVO


def test_un_mensaje_sin_tarea_en_el_medio_corta_el_hilo(conn, mundo, escribe):
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-13", "faltan los cables"))
    _turno(conn, escribe, Jugada("consultar_pendientes", {}), at=octubre(5, 10, 20))
    [hecho], _ = _turno(conn, escribe, jugada_prevision("T1", "2026-10-14"),
                        at=octubre(5, 10, 40))

    assert hecho["motivo"] is None and hecho["pregunta"] == MOTIVO


def test_un_mensaje_sin_jugadas_en_el_medio_corta_el_hilo(conn, mundo, escribe):
    """Una pregunta sobre otra cosa (sin jugadas) es otro tema."""
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-13", "faltan los cables"))
    _turno(conn, escribe, at=octubre(5, 10, 20))
    [hecho], _ = _turno(conn, escribe, jugada_prevision("T1", "2026-10-14"),
                        at=octubre(5, 10, 40))

    assert hecho["motivo"] is None and hecho["pregunta"] == MOTIVO


def test_un_mensaje_sobre_la_misma_tarea_en_el_medio_no_corta_el_hilo(conn, mundo, escribe):
    nueva_tarea(conn, mundo, "Probar las comunicaciones")
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-13", "faltan los cables"))
    _turno(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(5, 10, 20))
    [hecho], _ = _turno(conn, escribe, jugada_prevision("T1", "2026-10-14"),
                        at=octubre(5, 10, 40))

    assert hecho["motivo"] == "faltan los cables" and "pregunta" not in hecho


def test_lo_que_leda_manda_en_el_medio_no_corta_el_hilo(conn, mundo, escribe):
    """Sólo cuentan los mensajes de la persona: el aviso de Leda a Ismael no es un tema de ella."""
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-13", "faltan los cables"))
    enviar(conn, mundo, IAGuionada(redacciones=["Aviso."]), octubre(5, 10, 10))
    [hecho], _ = _turno(conn, escribe, jugada_prevision("T1", "2026-10-14"),
                        at=octubre(5, 10, 40))

    assert hecho["motivo"] == "faltan los cables"


def test_el_porque_de_una_fecha_que_no_atrasaba_no_explica_un_atraso(conn, mundo, escribe):
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-08", "termino antes"))
    [hecho], _ = _turno(conn, escribe, jugada_prevision("T1", "2026-10-13"), at=octubre(5, 11))

    assert hecho["motivo"] is None and hecho["pregunta"] == MOTIVO


# --- 2. El porqué llega: el aviso sale con él ---------------------------------------------------

def test_el_porque_cierra_la_pregunta_y_el_aviso_sale_con_el_despues_del_margen(
        conn, mundo, escribe):
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-13"))
    [hecho], pedido = _turno(conn, escribe,
                             jugada_prevision("T1", "2026-10-13", "faltan los cables"),
                             at=octubre(5, 11))

    assert hecho["resultado"] == "anotado" and hecho["motivo"] == "faltan los cables"
    assert "pregunta" not in hecho and pedido["pregunta"] is None
    assert _preguntas_sin_cerrar(conn) == []
    [espera] = _esperas(conn)
    assert espera["satisfecho_en"] is not None
    # La historia guarda las dos: la fecha sola y la misma fecha con su porqué.
    primera, segunda = todos(conn, "select * from task_forecast order by at")
    assert segunda["reemplaza_id"] == primera["id"]
    assert segunda["fecha_prevista"] == primera["fecha_prevista"]
    assert segunda["motivo"] == "faltan los cables"
    # El aviso que esperaba el porqué no sale: lo reemplaza el que lo lleva, con el margen.
    sin_porque, con_porque = avisos_guardados(conn, "nueva_prevision")
    assert (sin_porque["estado"], sin_porque["motivo_omision"]) == ("omitido", "llego_el_motivo")
    assert con_porque["estado"] == "guardado"
    assert con_porque["programado_para"] == octubre(5, 11, 10)
    assert con_porque["hechos"]["motivo"] == "faltan los cables"
    assert "sin_motivo_todavia" not in con_porque["hechos"]
    assert hecho["aviso_al_referente"] == {"a": "Ismael", "llega": "2026-10-05T11:10:00-03:00"}
    # Lo que se le había anunciado y ya no va a pasar se dice con su motivo, que lo explica.
    assert pedido["ya_no_va_a_pasar"] == [{"anuncio": "aviso_al_referente",
                                          "tarea": "Revisar el tablero", "a": "Ismael",
                                          "llega": "no_le_va_a_llegar",
                                          "motivo": "llego_el_motivo"}]
    assert vocabulario.sin_significado(pedido) == set()


def test_una_fecha_nueva_sin_porque_sigue_esperando_el_porque(conn, mundo, escribe):
    """La misma pregunta, no otra: la fecha cambió y el porqué sigue faltando."""
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-13"))
    [hecho], _ = _turno(conn, escribe, jugada_prevision("T1", "2026-10-14"), at=octubre(5, 11))

    assert hecho["pregunta"] == MOTIVO
    [pregunta] = _preguntas_sin_cerrar(conn)
    assert pregunta["jugada"]["datos"] == {"fecha": "2026-10-14"}
    primero, segundo = avisos_guardados(conn, "nueva_prevision")
    assert (primero["estado"], primero["motivo_omision"]) == ("omitido",
                                                              "hay_una_prevision_mas_nueva")
    assert segundo["programado_para"] == octubre(5, 16, 30)


def test_una_fecha_que_ya_no_atrasa_deja_sin_efecto_la_pregunta_del_porque(conn, mundo,
                                                                          escribe):
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-13"))
    [hecho], _ = _turno(conn, escribe, jugada_prevision("T1", "2026-10-09"), at=octubre(5, 11))

    assert "pregunta" not in hecho
    assert _preguntas_sin_cerrar(conn) == []
    assert uno(conn, "select cierre from conversation_question where tipo = %s",
               MOTIVO)["cierre"] == "sin_efecto"


# --- 3. Sin respuesta: el aviso sale al final del día y la pregunta sigue -------------------------

def test_sin_porque_el_aviso_sale_al_terminar_el_dia_y_la_pregunta_sigue(conn, mundo, escribe,
                                                                        dias):
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-13"))

    # Todavía espera el porqué; a Marcos, la repetición del día de la pregunta, a las 4 horas
    # (decisión 29 del usuario).
    [repeticion] = dias.ciclo(octubre(5, 16))
    assert repeticion["persona"] == "Marcos"
    assert (repeticion["hechos"][0]["aviso"], repeticion["pregunta"]["tipo"]) == (
        "repeticion_del_dia", MOTIVO)

    [a_ismael] = dias.ciclo(octubre(5, 16, 30))
    assert a_ismael["persona"] == "Ismael"
    [hechos] = a_ismael["hechos"]
    assert hechos["aviso"] == "nueva_prevision"
    # El hecho dice que todavía no lo dio: nunca un porqué que nadie dijo.
    assert hechos["sin_motivo_todavia"] is True and hechos["motivo"] is None
    assert vocabulario.sin_significado(a_ismael) == set()
    # La pregunta sigue abierta para Marcos, esperando.
    assert abierta(conn) == (MOTIVO, mundo["tarea"])
    [espera] = _esperas(conn)
    assert espera["satisfecho_en"] is None

    # Y la escalera de la pregunta la repite el día hábil siguiente, con lo que se anotó.
    [otra_vez] = dias.ciclo(octubre(6, 10))
    assert otra_vez["persona"] == "Marcos"
    [hechos] = otra_vez["hechos"]
    assert (hechos["aviso"], hechos["pregunta"]) == ("repregunta", MOTIVO)
    assert hechos["sobre"] == {"jugada": "anotar_prevision", "fecha": "2026-10-13"}


def test_el_porque_despues_del_aviso_sin_porque_le_llega_a_quien_aprueba(conn, mundo, escribe,
                                                                         dias):
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-13"))
    dias.ciclo(octubre(5, 16, 30))                             # salió sin el porqué

    [hecho], _ = _turno(conn, escribe, jugada_prevision("T1", "2026-10-13", "faltan los cables"),
                        at=octubre(6, 9, 30))

    assert hecho["aviso_al_referente"]["a"] == "Ismael"
    [con_porque] = [a for a in avisos_guardados(conn, "nueva_prevision")
                    if a["estado"] == "guardado"]
    assert con_porque["hechos"]["motivo"] == "faltan los cables"
    [a_ismael] = dias.ciclo(octubre(6, 10))
    assert a_ismael["persona"] == "Ismael"
    assert a_ismael["hechos"][0]["motivo"] == "faltan los cables"
    assert _preguntas_sin_cerrar(conn) == []


# --- 4. Una corrección mueve sólo la fecha ----------------------------------------------------

def test_una_correccion_pasa_solo_la_fecha_y_pregunta_el_porque_si_atrasa_la_otra(
        conn, mundo, escribe):
    # Vence el martes 13, después de T1 (los alias siguen el vencimiento): el 14 la atrasa.
    t2 = nueva_tarea(conn, mundo, "Probar las comunicaciones",
                     fecha=datetime(2026, 10, 13, 20, 0, tzinfo=timezone.utc))
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-14", "faltan los cables"))

    [hecho], pedido = _turno(conn, escribe, Jugada("corregir", {
        "corrige": "anotar_prevision", "tarea": "T1", "tarea_correcta": "T2"}),
        at=octubre(5, 10, 5))

    aplicado = hecho["aplicado"]
    assert aplicado["resultado"] == "anotado" and aplicado["prevision"] == "2026-10-14"
    # El porqué se dijo de la otra tarea: no viaja.
    assert aplicado["motivo"] is None
    en_t2 = uno(conn, "select * from task_forecast where task_id = %s", t2)
    assert en_t2["motivo"] is None
    # La fecha atrasa la tarea correcta: Leda pregunta su porqué, y el aviso lo espera.
    assert aplicado["pregunta"] == MOTIVO
    assert abierta(conn) == (MOTIVO, t2)
    assert aplicado["aviso_al_referente"]["llega"] == "2026-10-05T16:30:00-03:00"
    assert pedido["pregunta"]["tipo"] == MOTIVO


def test_una_correccion_a_una_tarea_que_no_atrasa_no_pregunta(conn, mundo, escribe):
    t2 = nueva_tarea(conn, mundo, "Probar las comunicaciones")       # vence el viernes 16
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-13", "faltan los cables"))

    [hecho], _ = _turno(conn, escribe, Jugada("corregir", {
        "corrige": "anotar_prevision", "tarea": "T1", "tarea_correcta": "T2"}),
        at=octubre(5, 10, 5))

    assert hecho["aplicado"]["motivo"] is None
    assert "pregunta" not in hecho["aplicado"]
    assert _preguntas_sin_cerrar(conn) == []
    assert uno(conn, "select motivo from task_forecast where task_id = %s", t2)["motivo"] is None


def test_corregir_una_fecha_sin_porque_deja_sin_efecto_su_pregunta(conn, mundo, escribe):
    nueva_tarea(conn, mundo, "Probar las comunicaciones")            # vence el viernes 16
    _turno(conn, escribe, jugada_prevision("T1", "2026-10-13"))

    _turno(conn, escribe, Jugada("corregir", {
        "corrige": "anotar_prevision", "tarea": "T1", "tarea_correcta": "T2"}),
        at=octubre(5, 10, 5))

    assert _preguntas_sin_cerrar(conn) == []
    assert abierta(conn) is None
    assert uno(conn, "select cierre from conversation_question where tipo = %s and task_id = %s",
               MOTIVO, mundo["tarea"])["cierre"] == "sin_efecto"


# --- 5. Con otra pregunta abierta: una a la vez -------------------------------------------------

def test_en_el_mismo_mensaje_la_pregunta_del_porque_espera_su_turno(conn, mundo, escribe):
    nueva_tarea(conn, mundo, "Probar las comunicaciones")
    hechos, pedido = _turno(conn, escribe, jugada_bloqueo("T2", "no llego el switch"),
                            jugada_prevision("T1", "2026-10-13"))

    assert hechos[0]["pregunta"] == "quien_destraba"
    assert hechos[1]["pregunta_para_despues"] == MOTIVO and "pregunta" not in hechos[1]
    assert pedido["pregunta"]["tipo"] == "quien_destraba"
    [para_despues] = _preguntas_sin_cerrar(conn)
    assert para_despues["para_despues_en"] is not None


def test_una_pregunta_de_antes_queda_para_despues_y_vuelve(conn, mundo, escribe):
    """9d: Leda sigue a la persona; la de antes queda para después y vuelve cuando se contesta
    la nueva, en un mensaje aparte (decisión 50 del usuario, 2026-10-09)."""
    t2 = nueva_tarea(conn, mundo, "Probar las comunicaciones")
    dice(conn, escribe, jugada_bloqueo("T2", "no llego el switch"))
    assert abierta(conn) == ("quien_destraba", t2)

    [hecho], _ = _turno(conn, escribe, jugada_prevision("T1", "2026-10-13"), at=octubre(5, 10, 5))
    assert hecho["pregunta"] == MOTIVO
    assert abierta(conn) == (MOTIVO, mundo["tarea"])

    _, pedido = _turno(conn, escribe, jugada_prevision("T1", "2026-10-13", "faltan los cables"),
                       at=octubre(5, 10, 10))
    assert pedido["pregunta"] is None
    assert abierta(conn) == ("quien_destraba", t2)
    [vuelve] = todos(conn, "select * from scheduled_notice where tipo = 'vuelve_la_pregunta'")
    assert vuelve["hechos"]["pregunta"] == "quien_destraba" and vuelve["estado"] == "guardado"
