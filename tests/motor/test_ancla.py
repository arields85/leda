"""El ancla de la escalera (`leda.motor.ancla`; ADR 0018, decisión 9i).

Las dos pruebas de una cadena rota vienen de `prueba_chica/test_ancla.py`; las demás fijan,
sin la escalera (que llega con la capa 3), lo que el ancla decide sola: la fecha y la clave
del anclaje, la racha de una misma fecha, los pasos de un anclaje y cuándo una escalera escaló.
La tarea "Revisar el tablero" de Marcos vence el viernes 9 de octubre de 2026.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from leda.db import admin, espacio
from leda.motor import ancla
from leda.motor.ancla import Anclaje, anclaje

from tests.motor.ayudantes import AHORA

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
