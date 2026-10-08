"""Lo que el motor escribe por su cuenta queda auditado con la versión de las reglas.

Constitución §12: toda acción de Leda con efecto queda en `audit_log` con quién la originó,
cuándo, sobre qué y con qué versión de las reglas del núcleo y del pack del espacio. Lo que
pasa por la cocina (`herramientas.ejecutar`) ya deja su fila allá (`tests/garantias`); estas
pruebas cubren lo que el motor escribe directo y la regla de qué se audita y qué no
(`leda.motor.auditoria`).
"""

from __future__ import annotations

from datetime import timedelta

import psycopg

from leda import versiones
from leda.db import admin
from leda.motor import fichas
from leda.motor.ia import IAGuionada, Jugada

from tests.motor.ayudantes import (AHORA, cuantas, dice, enviar, jugada_bloqueo,
                                   jugada_prevision, todos, uno)


def _auditadas(conn, accion: str) -> list[dict]:
    return todos(conn, "select * from audit_log where accion = %s order by at", accion)


def _con_la_version_de_las_reglas(fila: dict) -> None:
    # El pack del mundo de prueba (`conftest.mundo`) y el núcleo de este repositorio.
    assert fila["pack_hash"] == "hash-prueba"
    assert fila["nucleo_hash"] == versiones.nucleo_hash()


def _de_marcos(fila: dict, mundo) -> None:
    assert fila["actor_kind"] == "persona"
    assert str(fila["actor_app_user_id"]) == mundo["personas"]["Marcos"]["app_user_id"]
    assert str(fila["workspace_id"]) == mundo["id"]


# --- Lo que se audita: crear un hecho del trabajo ------------------------------------------------

def test_una_prevision_queda_auditada_con_la_version_de_las_reglas(conn, mundo, escribe):
    dice(conn, escribe, jugada_prevision("T1", "2026-10-14", "el proveedor se demoró"))

    [fila] = _auditadas(conn, "anotar_prevision")
    prevision = uno(conn, "select id from task_forecast")
    _de_marcos(fila, mundo)
    _con_la_version_de_las_reglas(fila)
    assert (fila["sujeto_tipo"], str(fila["sujeto_id"])) == ("task", mundo["tarea"])
    assert fila["detalle"] == {
        "prevision_id": str(prevision["id"]), "fecha_prevista": "2026-10-14",
        "fecha_comprometida": "2026-10-09", "atraso_dias_habiles": 3,
        "motivo": "el proveedor se demoró", "reemplaza_id": None, "at": AHORA.isoformat(),
        "inbound_message_id": str(uno(conn, "select id from inbound_message")["id"])}


def test_la_correccion_de_una_prevision_queda_auditada(conn, mundo, escribe):
    dice(conn, escribe, jugada_prevision("T1", "2026-10-14"))
    dice(conn, escribe, Jugada("corregir", {"corrige": "anotar_prevision", "tarea": "T1"}))

    [fila] = _auditadas(conn, "corregir_prevision")
    equivocada, correccion = todos(conn, "select id, es_correccion from task_forecast "
                                         "order by es_correccion")
    _de_marcos(fila, mundo)
    _con_la_version_de_las_reglas(fila)
    assert (fila["sujeto_tipo"], str(fila["sujeto_id"])) == ("task", mundo["tarea"])
    assert fila["detalle"]["prevision_id"] == str(correccion["id"])
    assert fila["detalle"]["corrige_prevision_id"] == str(equivocada["id"])
    assert fila["detalle"]["fecha_prevista"] == "2026-10-09"   # vuelve a la comprometida


def test_quien_destraba_un_bloqueo_queda_auditado(conn, mundo, escribe):
    dice(conn, escribe, jugada_bloqueo("T1", "falta el repuesto"))
    dice(conn, escribe, Jugada("anotar_quien_destraba", {"quien": "Ismael"}))

    [fila] = _auditadas(conn, "anotar_quien_destraba")
    bloqueo = uno(conn, "select id from blocker")
    anotado = uno(conn, "select id from blocker_unblocker")
    _de_marcos(fila, mundo)
    _con_la_version_de_las_reglas(fila)
    assert (fila["sujeto_tipo"], fila["sujeto_id"]) == ("blocker", bloqueo["id"])
    assert fila["detalle"]["blocker_unblocker_id"] == str(anotado["id"])
    assert fila["detalle"]["destraba_membership_id"] == mundo["personas"]["Ismael"][
        "membership_id"]
    assert fila["detalle"]["task_id"] == mundo["tarea"]


def test_un_avance_queda_auditado_con_la_version_de_las_reglas(conn, mundo, escribe):
    with admin(conn) as cur:
        cur.execute("""insert into pending_reply (workspace_id, membership_id, task_id, tipo,
                                                  preguntado_en, vence_en)
                       values (%s, %s, %s, 'estado_de_la_tarea', %s, %s)""",
                    (mundo["id"], mundo["personas"]["Marcos"]["membership_id"],
                     mundo["tarea"], AHORA, AHORA))
    conn.commit()

    dice(conn, escribe, Jugada("informar_avance", {"tarea": "T1", "palabras": "voy bien"}))

    [fila] = _auditadas(conn, "informar_avance")
    _de_marcos(fila, mundo)
    _con_la_version_de_las_reglas(fila)
    assert fila["detalle"]["dijo"] == "voy bien"


# --- Lo que se audita: lo que Leda manda por su cuenta -------------------------------------------

# El aviso a Ismael sale terminado el margen para corregir (`margen.py`): 10 minutos después.
SALE = AHORA + timedelta(minutes=10)


def test_cada_aviso_que_sale_queda_auditado_como_un_envio_de_leda(conn, mundo, escribe):
    dice(conn, escribe, jugada_prevision("T1", "2026-10-14"))

    assert enviar(conn, mundo, IAGuionada(redacciones=["Marcos prevé el 14."]), SALE) == {
        "enviado": 1}

    [fila] = _auditadas(conn, "enviar_aviso")
    aviso = uno(conn, "select id, outbox_id from scheduled_notice")
    assert fila["actor_kind"] == "leda" and fila["actor_app_user_id"] is None
    _con_la_version_de_las_reglas(fila)
    assert (fila["sujeto_tipo"], str(fila["sujeto_id"])) == ("task", mundo["tarea"])
    assert fila["detalle"] == {
        "aviso_id": str(aviso["id"]), "tipo": "nueva_prevision",
        "destinatario_membership_id": mundo["personas"]["Ismael"]["membership_id"],
        "outbox_id": str(aviso["outbox_id"]), "at": SALE.isoformat()}


def test_un_aviso_que_no_salio_no_se_audita_como_enviado(conn, mundo, escribe):
    """La IA no lo redactó: queda para reintentar, y nada se envió."""
    dice(conn, escribe, jugada_prevision("T1", "2026-10-14"))

    caida = IAGuionada(redacciones=[RuntimeError("sin servicio")])
    assert enviar(conn, mundo, caida, SALE) == {"reintento": 1}

    assert _auditadas(conn, "enviar_aviso") == []


# --- En la misma transacción que el efecto ---------------------------------------------------

def test_lo_que_se_deshace_se_deshace_con_su_auditoria(conn, mundo, escribe, monkeypatch):
    """Una jugada que falla después de escribir se deshace entera (su punto de guardado): la
    previsión y su fila de auditoría."""
    def regla_del_trabajo(*_, **__):
        raise psycopg.errors.RaiseException("una regla del trabajo")

    monkeypatch.setattr(fichas, "_proponer", regla_del_trabajo)
    resultado = dice(conn, escribe, jugada_prevision("T1", "2026-10-14"))

    assert resultado.hechos[0]["motivo"] == "regla_del_trabajo"
    assert cuantas(conn, "task_forecast") == 0
    assert _auditadas(conn, "anotar_prevision") == []


# --- Lo que no se audita --------------------------------------------------------------------

def test_la_conversacion_misma_no_se_audita(conn, mundo, escribe):
    """Una pregunta, su espera y la respuesta de Leda son la conversación, que queda en su
    registro de turnos (constitución §9): no son una acción con efecto."""
    dice(conn, escribe, jugada_bloqueo("T1"))           # sin causa: Leda pregunta la causa
    dice(conn, escribe)                                 # sin jugadas: sólo la respuesta

    assert cuantas(conn, "conversation_question") == 1
    assert cuantas(conn, "audit_log") == 0


def test_lo_que_hace_la_cocina_se_audita_una_sola_vez(conn, mundo, escribe):
    """Un inicio pasa por `herramientas.ejecutar`, que deja su fila: el motor no agrega otra."""
    dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}))

    assert [f["accion"] for f in todos(conn, "select accion from audit_log")] == [
        "herramienta:actualizar_estado"]
