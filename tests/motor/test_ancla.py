"""El ancla de la escalera (`leda.motor.ancla`; ADR 0018, decisión 9i).

Las dos pruebas de una cadena rota y las de la escalera con una previsión vienen de
`prueba_chica/test_ancla.py`; las demás fijan, sin la escalera, lo que el ancla decide sola: la
fecha y la clave del anclaje, la racha de una misma fecha, los pasos de un anclaje y cuándo una
escalera escaló. La tarea "Revisar el tablero" de Marcos vence el viernes 9 de octubre de 2026;
con la escalera (`dias`), el aviso previo es a 3 días hábiles y el lunes 12 es feriado.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from leda.db import admin, espacio
from leda.motor import ancla
from leda.motor.ancla import Anclaje, anclaje
from leda.motor.escalera import correr_escalera
from leda.motor.tiempo import RelojFijo

from tests.motor.ayudantes import (AHORA, avisos_guardados, cuantas, dice_una_prevision,
                                   espera_del_estado, lo_que_salio_para, octubre)

V = date(2026, 10, 9)


# --- Una cadena rota (de `prueba_chica/test_ancla.py`) ------------------------------------------

class _Fila(dict):
    """Una fila que cuenta cuántas veces se la recorre: un ciclo en la cadena no termina."""

    lecturas = 0

    def __getitem__(self, clave):
        type(self).lecturas += 1
        if type(self).lecturas > 1000:
            raise AssertionError("la cadena de previsiones no termina")
        return super().__getitem__(clave)


class _CursorDeUnaCadena:
    """Dos previsiones que se reemplazan una a la otra con la misma fecha: una cadena rota."""

    def __init__(self) -> None:
        self.a = _Fila(id="a", fecha_prevista=date(2026, 10, 15), reemplaza_id="b")
        self.b = _Fila(id="b", fecha_prevista=date(2026, 10, 15), reemplaza_id="a")

    def execute(self, sql, params=None):
        pass

    def fetchone(self):
        return self.a

    def fetchall(self):
        return [self.a, self.b]


def test_una_cadena_de_previsiones_con_un_ciclo_no_cuelga_el_ancla():
    _Fila.lecturas = 0
    de = anclaje(_CursorDeUnaCadena(), "tarea", V)

    assert de.fecha == date(2026, 10, 15)
    assert de.clave.startswith("2026-10-15+")


def test_un_ciclo_que_no_pasa_la_fecha_comprometida_deja_la_escalera_de_siempre():
    """Un ciclo es el final de la cadena: si sus previsiones no pasan la fecha comprometida,
    ninguna movió el ancla y la clave es la del vencimiento, no una escalera nueva."""
    cursor = _CursorDeUnaCadena()
    cursor.a["fecha_prevista"] = cursor.b["fecha_prevista"] = date(2026, 10, 5)
    _Fila.lecturas = 0
    de = anclaje(cursor, "tarea", V)

    assert (de.fecha, de.clave, de.legado) == (V, "2026-10-09", None)


# --- Con la base ------------------------------------------------------------------------------

def _prevision(conn, mundo, fecha: date, *, reemplaza: str | None = None,
               at: datetime = AHORA) -> str:
    with admin(conn) as cur:
        cur.execute(
            """insert into task_forecast (workspace_id, task_id, fecha_prevista,
                                          fecha_comprometida, atraso_dias_habiles,
                                          reemplaza_id, dicho_por_membership_id, at)
               values (%s, %s, %s, %s, 0, %s, %s, %s) returning id""",
            (mundo["id"], mundo["tarea"], fecha,
             datetime(2026, 10, 9, 20, 0, tzinfo=timezone.utc), reemplaza,
             mundo["personas"]["Marcos"]["membership_id"], at))
        return str(cur.fetchone()["id"])


def _anclaje(conn, mundo) -> Anclaje:
    with espacio(conn, mundo["id"]) as cur:
        return anclaje(cur, mundo["tarea"], V)


def test_sin_prevision_el_ancla_es_la_fecha_comprometida(conn, mundo):
    assert _anclaje(conn, mundo) == Anclaje(V, "2026-10-09")


def test_una_prevision_posterior_mueve_el_ancla_con_su_propia_clave(conn, mundo):
    p = _prevision(conn, mundo, date(2026, 10, 15))

    assert _anclaje(conn, mundo) == Anclaje(date(2026, 10, 15), f"2026-10-15+{p}",
                                            legado="2026-10-15")
    with espacio(conn, mundo["id"]) as cur:
        assert ancla.ancla(cur, mundo["tarea"], V) == date(2026, 10, 15)
        assert str(ancla.prevision_vigente(cur, mundo["tarea"])["id"]) == p


def test_una_prevision_anterior_no_mueve_el_ancla(conn, mundo):
    _prevision(conn, mundo, date(2026, 10, 7))

    assert _anclaje(conn, mundo) == Anclaje(V, "2026-10-09")


def test_repetir_la_misma_fecha_sigue_la_racha_y_otra_fecha_es_un_anclaje_nuevo(conn, mundo):
    p1 = _prevision(conn, mundo, date(2026, 10, 15))
    p2 = _prevision(conn, mundo, date(2026, 10, 15), reemplaza=p1,
                    at=AHORA + timedelta(hours=1))
    assert _anclaje(conn, mundo).clave == f"2026-10-15+{p1}"

    p3 = _prevision(conn, mundo, date(2026, 10, 20), reemplaza=p2,
                    at=AHORA + timedelta(hours=2))
    assert _anclaje(conn, mundo).clave == f"2026-10-20+{p3}"


def test_volver_a_la_fecha_comprometida_despues_de_moverla_es_un_anclaje_nuevo(conn, mundo):
    p1 = _prevision(conn, mundo, date(2026, 10, 15))
    p2 = _prevision(conn, mundo, V, reemplaza=p1, at=AHORA + timedelta(hours=1))

    assert _anclaje(conn, mundo) == Anclaje(V, f"2026-10-09+{p2}")


def test_los_pasos_de_un_anclaje_salen_de_su_clave(conn, mundo):
    p = _prevision(conn, mundo, date(2026, 10, 15))
    tarea, marcos = mundo["tarea"], mundo["personas"]["Marcos"]["membership_id"]
    claves = {"del_vencimiento": f"motor:pedido_de_estado:{tarea}:2026-10-09",
              "de_la_prevision": f"motor:pedido_de_estado:{tarea}:2026-10-15+{p}",
              "de_antes": f"motor:reencuadre:{tarea}:2026-10-15:1"}
    with admin(conn) as cur:
        for n, clave in enumerate(claves.values()):
            cur.execute(
                """insert into scheduled_notice (workspace_id, tipo, task_id,
                                                 destinatario_membership_id, hechos,
                                                 programado_para, dedupe_key, creado_en)
                   values (%s, %s, %s, %s, '{}', %s, %s, %s)""",
                (mundo["id"], clave.split(":")[1], tarea, marcos, AHORA, clave,
                 AHORA + timedelta(minutes=n)))
    de = _anclaje(conn, mundo)
    with espacio(conn, mundo["id"]) as cur:
        del_anclaje = [a["dedupe_key"] for a in ancla.pasos(cur, tarea, de)]
        de_la_fecha = [a["dedupe_key"] for a in ancla.pasos(cur, tarea, date(2026, 10, 15))]

    # El paso guardado con la clave de antes (la fecha sola) sigue siendo de esta escalera.
    assert del_anclaje == [claves["de_la_prevision"], claves["de_antes"]]
    assert de_la_fecha == [claves["de_la_prevision"], claves["de_antes"]]
    assert ancla.fecha_de_la_clave({"dedupe_key": claves["de_la_prevision"]}) \
        == date(2026, 10, 15)
    assert ancla.clave_del_anclaje({"dedupe_key": claves["del_vencimiento"]}) == "2026-10-09"


def test_una_escalera_escalo_solo_con_un_escalamiento_dado_o_su_espera_escalada():
    pedido = {"tipo": "pedido_de_estado", "estado": "enviado", "motivo_omision": None,
              "creado_en": AHORA}
    escalamiento = {"tipo": "escalamiento", "estado": "enviado", "motivo_omision": None,
                    "creado_en": AHORA}
    reemplazado = {**escalamiento, "estado": "omitido",
                   "motivo_omision": ancla.REEMPLAZADO_POR_UN_AVANCE}
    guardado = {**escalamiento, "estado": "guardado"}
    espera = {"escalado_en": AHORA, "preguntado_en": AHORA + timedelta(hours=1)}

    assert ancla.escalo([pedido, escalamiento], None)
    assert not ancla.escalo([pedido, reemplazado], None)
    assert not ancla.escalo([pedido, guardado], None)
    assert ancla.escalo([pedido], espera)
    # La espera escalada de un ancla anterior no frena a la nueva.
    assert not ancla.escalo([pedido], {**espera, "preguntado_en": AHORA - timedelta(days=3)})
    assert not ancla.escalo([], espera)


def test_al_mediodia_es_un_momento_del_dia_en_la_zona():
    zona = ZoneInfo("America/Argentina/Buenos_Aires")
    assert ancla.al_mediodia(V, zona) == datetime(2026, 10, 9, 12, 0, tzinfo=zona)


def test_el_candado_de_una_tarea_se_toma_sin_esperar(conn, mundo):
    with espacio(conn, mundo["id"]) as cur:
        assert ancla.candado(cur, mundo["tarea"], esperar=False) is True
        assert ancla.candado(cur, mundo["tarea"]) is True


# --- Con la escalera (de `prueba_chica/test_ancla.py`) --------------------------------------------

def _de_marcos(pedidos: list[dict]) -> list[dict]:
    return [p for p in pedidos if p["persona"] == "Marcos"]


def test_con_una_prevision_el_vencimiento_lleva_un_recordatorio_y_la_escalera_va_a_la_prevision(
        conn, mundo, dias, escribe):
    dice_una_prevision(conn, escribe, "2026-10-15", at=octubre(5, 11))
    [al_referente] = dias.ciclo(octubre(5, 11, 30))
    assert al_referente["persona"] == "Ismael"

    # Hasta el vencimiento, nada: el aviso previo era de V, y Marcos ya dio su fecha.
    for dia in (6, 7, 8):
        assert dias.ciclo(octubre(dia, 10)) == []

    [recordatorio] = dias.ciclo(octubre(9, 10))

    assert recordatorio["persona"] == "Marcos" and recordatorio["pregunta"] is None
    hechos = recordatorio["hechos"][0]
    assert hechos["aviso"] == "vencimiento_con_prevision"
    assert hechos["necesita_respuesta"] is False
    assert hechos["vence"] == "2026-10-09" and hechos["atraso_dias_habiles"] == 0
    assert hechos["prevision_vigente"] == {
        "fecha": "2026-10-15", "motivo": "el proveedor",
        "atraso_si_se_cumple_la_prevision_dias_habiles": 3,
        "aviso_al_referente": {"a": "Ismael", "llega": "ya_le_llego"}}
    assert hechos["pide_el_estado_el"] == {"fecha": "2026-10-15"}
    assert espera_del_estado(conn) is None
    assert cuantas(conn, "conversation_question", "cerrada_en is null") == 0
    # Uno solo, y nada cada día hasta la previsión (el lunes 12 es feriado).
    for momento in (octubre(9, 15), octubre(13, 10), octubre(14, 10)):
        assert dias.ciclo(momento) == []

    [v] = dias.ciclo(octubre(15, 10))

    hechos = v["hechos"][0]
    assert (hechos["aviso"], hechos["numero"]) == ("pedido_de_estado", 1)
    assert hechos["seguimiento_por"] == "prevision" and hechos["necesita_respuesta"] is True
    assert hechos["vence"] == "2026-10-09" and hechos["atraso_dias_habiles"] == 3
    assert v["pregunta"]["tipo"] == "estado_de_la_tarea"
    assert espera_del_estado(conn)["satisfecho_en"] is None

    # Sin respuesta, la escalera sigue desde la previsión.
    assert dias.ciclo(octubre(16, 10))[0]["hechos"][0]["numero"] == 2
    [tercero] = dias.ciclo(octubre(19, 10))
    assert tercero["hechos"][0]["si_no_hay_respuesta"]["se_avisa_a"] == ["Ismael"]

    [escalamiento] = dias.ciclo(octubre(20, 10))

    assert escalamiento["persona"] == "Ismael"
    hechos = escalamiento["hechos"][0]
    assert hechos["aviso"] == "falta_de_respuesta" and hechos["seguimiento_por"] == "prevision"
    assert hechos["pedido_desde"] == "2026-10-15" and hechos["atraso_dias_habiles"] == 6
    assert hechos["prevision_vigente"]["fecha"] == "2026-10-15"
    assert dias.ciclo(octubre(21, 10)) == []
    # La fecha comprometida no cambió.
    assert all(a["hechos"]["vence"] == "2026-10-09" for a in avisos_guardados(conn)
               if a["tipo"] != "nueva_prevision")


def test_una_prevision_mas_nueva_mueve_el_ancla(conn, mundo, dias, escribe):
    dice_una_prevision(conn, escribe, "2026-10-15", at=octubre(5, 11))
    for dia in (5, 9, 13):
        dias.ciclo(octubre(dia, 11))
    correr_escalera(conn, mundo["id"], RelojFijo(octubre(15, 7)))   # el pedido del 15, guardado
    conn.commit()

    dice_una_prevision(conn, escribe, "2026-10-20", at=octubre(15, 8))

    assert _de_marcos(dias.ciclo(octubre(15, 10))) == []
    [guardado] = avisos_guardados(conn, "pedido_de_estado")
    assert (guardado["estado"], guardado["motivo_omision"]) == ("omitido", "ya_respondio")
    assert _de_marcos(dias.ciclo(octubre(16, 10))) == []
    assert _de_marcos(dias.ciclo(octubre(19, 10))) == []
    [v] = _de_marcos(dias.ciclo(octubre(20, 10)))
    assert (v["hechos"][0]["aviso"], v["hechos"][0]["numero"]) == ("pedido_de_estado", 1)
    assert v["hechos"][0]["prevision_vigente"]["fecha"] == "2026-10-20"
    # Un solo recordatorio del vencimiento, aunque la previsión haya cambiado.
    assert len(avisos_guardados(conn, "vencimiento_con_prevision")) == 1


def test_una_prevision_que_vuelve_a_la_fecha_comprometida_devuelve_el_ancla(conn, mundo, dias,
                                                                           escribe):
    dice_una_prevision(conn, escribe, "2026-10-15", at=octubre(5, 11))
    assert _de_marcos(dias.ciclo(octubre(6, 10))) == []   # sin aviso previo: el ancla es F

    dice_una_prevision(conn, escribe, "2026-10-09", at=octubre(7, 9, 30))

    [previo] = _de_marcos(dias.ciclo(octubre(7, 10)))     # vuelve el de V, comprimido
    assert previo["hechos"][0]["aviso"] == "vencimiento_proximo"
    [v] = dias.ciclo(octubre(9, 10))
    assert (v["hechos"][0]["aviso"], v["hechos"][0]["numero"]) == ("pedido_de_estado", 1)
    assert "seguimiento_por" not in v["hechos"][0]
    assert avisos_guardados(conn, "vencimiento_con_prevision") == []


def test_un_recordatorio_guardado_no_sale_si_la_prevision_vuelve_a_la_fecha_comprometida(
        conn, mundo, dias, escribe):
    dice_una_prevision(conn, escribe, "2026-10-15", at=octubre(5, 11))
    correr_escalera(conn, mundo["id"], RelojFijo(octubre(9, 7)))
    conn.commit()
    dice_una_prevision(conn, escribe, "2026-10-09", at=octubre(9, 8))

    [v] = _de_marcos(dias.ciclo(octubre(9, 10)))

    [recordatorio] = avisos_guardados(conn, "vencimiento_con_prevision")
    assert (recordatorio["estado"], recordatorio["motivo_omision"]) == (
        "omitido", "volvio_a_la_fecha_comprometida")
    assert v["hechos"][0]["aviso"] == "pedido_de_estado"


def test_una_prevision_despues_del_vencimiento_lleva_la_escalera_a_la_prevision(conn, mundo, dias,
                                                                              escribe):
    """El pedido de V ya salió: no hay recordatorio del vencimiento. La previsión contesta la
    espera, y la escalera nueva empieza el día de la previsión."""
    [v] = dias.ciclo(octubre(9, 10))
    assert v["hechos"][0]["numero"] == 1

    dice_una_prevision(conn, escribe, "2026-10-16", at=octubre(9, 11))

    for dia in (13, 14, 15):
        assert _de_marcos(dias.ciclo(octubre(dia, 10))) == []
    [f] = _de_marcos(dias.ciclo(octubre(16, 10)))
    assert (f["hechos"][0]["numero"], f["hechos"][0]["seguimiento_por"]) == (1, "prevision")
    assert avisos_guardados(conn, "vencimiento_con_prevision") == []
    assert lo_que_salio_para(conn, mundo, "Ismael") == ["Aviso 2."]  # sólo el de la previsión


@pytest.mark.parametrize("fecha", ["2026-10-08", "2026-10-09"])
def test_una_prevision_que_no_pasa_la_fecha_comprometida_deja_el_ancla_en_el_vencimiento(
        conn, mundo, dias, escribe, fecha):
    dice_una_prevision(conn, escribe, fecha, at=octubre(5, 11))

    [previo] = _de_marcos(dias.ciclo(octubre(6, 10)))
    assert previo["hechos"][0]["aviso"] == "vencimiento_proximo"
    [v] = _de_marcos(dias.ciclo(octubre(9, 10)))
    assert v["hechos"][0]["aviso"] == "pedido_de_estado"


# --- Cada anclaje es una escalera nueva (revisión del ancla, 2026-10-05) ----------------------
#
# El ancla iba en la clave sólo por su fecha: volver a una fecha ya usada reusaba los pasos de
# aquella escalera (contestada o escalada) y el seguimiento quedaba muerto. Ahora cada anclaje
# (la previsión con que empieza una racha de la misma fecha) es una escalera nueva; repetir la
# misma fecha no lo es.


def test_volver_a_la_fecha_comprometida_despues_de_empezar_su_escalera_es_una_escalera_nueva(
        conn, mundo, dias, escribe):
    [v] = dias.ciclo(octubre(9, 10))                         # el pedido de V, sin respuesta
    assert v["hechos"][0]["numero"] == 1
    # Contesta: el ancla va al 16.
    dice_una_prevision(conn, escribe, "2026-10-16", at=octubre(9, 11))
    assert _de_marcos(dias.ciclo(octubre(13, 9, 30))) == []

    dice_una_prevision(conn, escribe, "2026-10-09", at=octubre(13, 9, 40))  # vuelve a V, ya vencida

    [otra_vez] = _de_marcos(dias.ciclo(octubre(13, 10)))
    hechos = otra_vez["hechos"][0]
    assert (hechos["aviso"], hechos["numero"]) == ("pedido_de_estado", 1)
    assert "seguimiento_por" not in hechos
    assert cuantas(conn, "pending_reply", "satisfecho_en is null") == 1    # su propia espera
    # Sin respuesta, sigue hasta escalar, como cualquier escalera.
    assert dias.ciclo(octubre(14, 10))[0]["hechos"][0]["numero"] == 2


def test_volver_a_una_prevision_ya_usada_es_una_escalera_nueva(conn, mundo, dias, escribe):
    dice_una_prevision(conn, escribe, "2026-10-15", at=octubre(5, 11))
    for dia in (5, 9, 13):
        dias.ciclo(octubre(dia, 11))
    [f] = _de_marcos(dias.ciclo(octubre(15, 10)))            # el pedido del día de la previsión
    assert f["hechos"][0]["numero"] == 1
    dice_una_prevision(conn, escribe, "2026-10-20", at=octubre(15, 11))  # contesta y mueve el ancla

    # Vuelve al 15, ya pasado.
    dice_una_prevision(conn, escribe, "2026-10-15", at=octubre(16, 9, 30))

    [otra_vez] = _de_marcos(dias.ciclo(octubre(16, 10)))
    hechos = otra_vez["hechos"][0]
    assert (hechos["aviso"], hechos["numero"]) == ("pedido_de_estado", 1)
    assert hechos["prevision_vigente"]["fecha"] == "2026-10-15"


def test_repetir_la_misma_fecha_no_empieza_otra_escalera(conn, mundo, dias, escribe):
    dice_una_prevision(conn, escribe, "2026-10-15", at=octubre(5, 11))
    for dia in (5, 9, 13):
        dias.ciclo(octubre(dia, 11))
    dias.ciclo(octubre(15, 10))                              # el pedido del 15

    dice_una_prevision(conn, escribe, "2026-10-15", at=octubre(15, 11))  # "sigo para hoy": contesta

    for momento in (octubre(15, 12), octubre(16, 10), octubre(19, 10)):
        assert _de_marcos(dias.ciclo(momento)) == []


# --- Revisión de la E2-7 ---------------------------------------------------------------------


def test_un_paso_guardado_con_la_clave_de_antes_sigue_siendo_de_su_ancla(conn, mundo, dias,
                                                                         escribe):
    """Antes de la revisión del ancla, la clave de un paso anclado en una previsión era la
    fecha sola. Un paso así, guardado en una base de antes, sigue siendo de la escalera de esa
    previsión: sale, y la escalera sigue contándolo."""
    dice_una_prevision(conn, escribe, "2026-10-15", at=octubre(5, 11))
    for dia in (5, 9, 13):
        dias.ciclo(octubre(dia, 11))
    correr_escalera(conn, mundo["id"], RelojFijo(octubre(15, 7)))   # el pedido del 15, guardado
    conn.commit()
    with admin(conn) as cur:
        cur.execute("""update scheduled_notice
                          set dedupe_key = regexp_replace(dedupe_key, '[+][^:]+', '')
                        where tipo = 'pedido_de_estado'""")
    conn.commit()

    [f] = _de_marcos(dias.ciclo(octubre(15, 10)))

    assert f["hechos"][0]["numero"] == 1
    [pedido] = avisos_guardados(conn, "pedido_de_estado")
    assert pedido["estado"] == "enviado"
    assert _de_marcos(dias.ciclo(octubre(16, 10)))[0]["hechos"][0]["numero"] == 2
