"""El comando que dispara el aviso previo (E2-3b).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Avisos guardados"); ADR 0018, decisiones 8 y
9b: el aviso se guarda como hechos, la IA lo redacta justo antes de enviarlo y no pide
respuesta. Para el primer contacto real se dispara a mano; el ciclo y la escalera son de la
E2-5 y la E2-6. La IA es guionada y el reloj, fijo.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from prueba_chica.avisar import avisar_vencimiento, resolver
from prueba_chica.conftest import AHORA
from prueba_chica.ia import IAGuionada
from prueba_chica.tiempo import RelojFijo
from prueba_chica.turno import procesar_turno

from leda.autoridad import identificar_en_espacio
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.despachador import TransporteDePrueba, despachar

TEXTO = "El viernes 9 vence Revisar el tablero. No hace falta que me contestes."
HECHOS = {"aviso": "vencimiento_proximo", "tarea": "Revisar el tablero",
          "vence": "2026-10-09", "dias_habiles_hasta_el_vencimiento": 4,
          "necesita_respuesta": False}


def _uno(conn, sql: str, *params):
    with admin(conn) as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def _cuantas(conn, tabla: str) -> int:
    return _uno(conn, f"select count(*) n from {tabla}")["n"]


def _avisar(conn, mundo, ia, **opciones):
    resultado = avisar_vencimiento(conn, mundo["id"], mundo["personas"]["Marcos"][
        "membership_id"], mundo["tarea"], ia, RelojFijo(AHORA), **opciones)
    conn.commit()
    return resultado


def test_el_aviso_previo_se_guarda_como_hechos_se_redacta_y_se_encola(conn, mundo):
    marcos = mundo["personas"]["Marcos"]
    ia = IAGuionada(redacciones=[TEXTO])

    resultado = _avisar(conn, mundo, ia)

    assert resultado.estado == "encolado" and resultado.texto == TEXTO
    # La IA redacta desde los hechos: la tarea, cuándo vence y que no pide respuesta (9b).
    [pedido] = ia.pedidos_de_redaccion
    assert pedido["hechos"] == [HECHOS] and pedido["persona"] == "Marcos"
    assert pedido["mensaje"] is None and pedido["hoy"] == "2026-10-05"
    aviso = _uno(conn, "select * from scheduled_notice")
    assert aviso["tipo"] == "aviso_previo" and aviso["hechos"] == HECHOS
    assert str(aviso["task_id"]) == mundo["tarea"]
    assert str(aviso["destinatario_membership_id"]) == marcos["membership_id"]
    assert aviso["estado"] == "enviado" and aviso["intentos"] == 1
    assert aviso["creado_en"] == AHORA and aviso["resuelto_en"] == AHORA
    salida = _uno(conn, "select * from message_outbox")
    assert salida["id"] == aviso["outbox_id"] and salida["cuerpo"] == TEXTO
    assert salida["chat_id"] == marcos["telegram"] and salida["es_respuesta"] is False
    assert str(salida["destinatario_membership_id"]) == marcos["membership_id"]
    turno = _uno(conn, "select * from conversation_turn")
    assert turno["sentido"] == "salida" and turno["outbox_id"] == salida["id"]
    assert turno["ia"] == "guionada" and turno["at"] == AHORA
    assert _uno(conn, "select ultimo_aviso_id from conversation_state")[
        "ultimo_aviso_id"] == aviso["id"]

    # La respuesta que no nombra la tarea la encuentra en el último aviso (conversación 01).
    with espacio(conn, mundo["id"]) as cur:
        cur.execute("""insert into inbound_message (workspace_id, chat_id, app_user_id, texto,
                                                    at)
                       values (%s, %s, %s, 'arranqué', %s) returning id""",
                    (mundo["id"], marcos["telegram"], marcos["app_user_id"], AHORA))
        entrante = str(cur.fetchone()["id"])
        quien = identificar_en_espacio(cur, marcos["telegram"], mundo["id"])
    conn.commit()
    turno_ia = IAGuionada(jugadas=[[]], redacciones=["Bien."])
    procesar_turno(conn, quien, entrante, turno_ia, RelojFijo(AHORA))
    situacion = turno_ia.pedidos_de_jugadas[0]
    assert situacion["ultimo_aviso"] == {"tipo": "aviso_previo", "tarea": "T1"}
    assert situacion["ultimos_turnos"][-1]["texto"] == TEXTO


def test_correrlo_de_nuevo_no_manda_otro_aviso_salvo_que_se_pida(conn, mundo):
    _avisar(conn, mundo, IAGuionada(redacciones=[TEXTO]))
    otra = IAGuionada(redacciones=["Otra vez."])

    resultado = _avisar(conn, mundo, otra)

    assert resultado.estado == "ya_enviado" and otra.pedidos_de_redaccion == []
    assert _cuantas(conn, "message_outbox") == 1

    de_nuevo = _avisar(conn, mundo, otra, de_nuevo=True)
    assert de_nuevo.estado == "encolado" and _cuantas(conn, "message_outbox") == 2


def test_si_la_ia_no_redacta_el_aviso_queda_guardado_sin_enviar(conn, mundo):
    resultado = _avisar(conn, mundo, IAGuionada(
        redacciones=[RuntimeError("caída"), RuntimeError("caída")]))

    assert resultado.estado == "sin_redactar" and resultado.texto is None
    aviso = _uno(conn, "select estado, intentos, outbox_id from scheduled_notice")
    assert aviso == {"estado": "guardado", "intentos": 1, "outbox_id": None}
    assert _cuantas(conn, "message_outbox") == 0 and _cuantas(conn, "conversation_turn") == 0

    # Nunca sale un texto armado a mano (decisión 8): al volver a correrlo, se redacta.
    otra = _avisar(conn, mundo, IAGuionada(redacciones=[TEXTO]))
    assert otra.estado == "encolado" and _cuantas(conn, "scheduled_notice") == 1
    assert _uno(conn, "select intentos from scheduled_notice")["intentos"] == 2


def test_cada_estado_del_aviso_se_informa_como_es(conn, mundo):
    """Revisión de la E2-5: un aviso que ya existía fallido u omitido no se informa como
    enviado, y el quinto fallo de la IA no se informa como un intento más."""
    caida = IAGuionada(redacciones=[RuntimeError("caída") for _ in range(5)])
    for _ in range(4):
        assert _avisar(conn, mundo, caida).estado == "sin_redactar"

    quinto = _avisar(conn, mundo, caida)
    assert quinto.estado == "fallido"
    assert _avisar(conn, mundo, IAGuionada(redacciones=[TEXTO])).estado == "fallido"

    # Otro aviso (con --de-nuevo) que se omite al salir porque la tarea se bloqueó.
    with admin(conn) as cur:
        cur.execute("""insert into blocker (workspace_id, task_id, causa)
                       values (%s, %s, 'falta el repuesto')""", (mundo["id"], mundo["tarea"]))
    conn.commit()
    omitido = _avisar(conn, mundo, IAGuionada(redacciones=[TEXTO]), de_nuevo=True)
    assert (omitido.estado, omitido.motivo) == ("omitido", "bloqueo_abierto")
    otra_vez = _avisar(conn, mundo, IAGuionada(redacciones=[TEXTO]), de_nuevo=True)
    assert (otra_vez.estado, otra_vez.motivo) == ("omitido", "bloqueo_abierto")


def test_a_alguien_ausente_el_aviso_le_espera(conn, mundo):
    with admin(conn) as cur:
        cur.execute("""insert into absence (workspace_id, membership_id, desde, hasta)
                       values (%s, %s, '2026-10-05', '2026-10-06')""",
                    (mundo["id"], mundo["personas"]["Marcos"]["membership_id"]))
    conn.commit()

    resultado = _avisar(conn, mundo, IAGuionada(redacciones=[TEXTO]))

    assert resultado.estado == "en_espera"
    assert _uno(conn, "select estado, intentos from scheduled_notice") == {
        "estado": "guardado", "intentos": 0}


@pytest.mark.parametrize("estado", ["terminada", "cancelada"])
def test_una_tarea_cerrada_no_se_avisa(conn, mundo, estado):
    with admin(conn) as cur:
        cur.execute("""insert into task (workspace_id, objective_id, titulo, area_id,
                                         responsable_membership_id, estado, fecha_objetivo)
                       select workspace_id, objective_id, 'Cerrada', area_id,
                              responsable_membership_id, %s, fecha_objetivo
                         from task where id = %s
                       returning id""", (estado, mundo["tarea"]))
        cerrada = str(cur.fetchone()["id"])
    conn.commit()
    with pytest.raises(ValueError, match="abierta"):
        avisar_vencimiento(conn, mundo["id"], mundo["personas"]["Marcos"]["membership_id"],
                           cerrada, IAGuionada(redacciones=[TEXTO]), RelojFijo(AHORA))
    conn.rollback()
    assert _cuantas(conn, "scheduled_notice") == 0


def test_la_tarea_tiene_que_ser_de_la_persona(conn, mundo):
    with pytest.raises(ValueError, match="no es de"):
        avisar_vencimiento(conn, mundo["id"], mundo["personas"]["Ismael"]["membership_id"],
                           mundo["tarea"], IAGuionada(redacciones=[TEXTO]), RelojFijo(AHORA))


def test_el_comando_encuentra_persona_y_tarea_por_palabras(conn, mundo):
    with espacio(conn, mundo["id"]) as cur:
        assert resolver(cur, "marcos", "tablero") == (
            mundo["personas"]["Marcos"]["membership_id"], "Marcos", mundo["tarea"])
        with pytest.raises(ValueError, match="Ismael"):
            resolver(cur, "ismael", "tablero")          # no tiene esa tarea
        with pytest.raises(ValueError, match="nadie"):
            resolver(cur, "nahuel", "tablero")


def test_fuera_del_horario_el_aviso_espera_al_proximo_dia_habil(conn, mundo):
    _avisar(conn, mundo, IAGuionada(redacciones=[TEXTO]))
    sabado = datetime(2026, 10, 10, 15, 0, tzinfo=timezone.utc)
    transporte = TransporteDePrueba()

    with espacio(conn, mundo["id"]) as cur:
        resumen = despachar(cur, mundo["id"], transporte,
                            Calendario.desde_base(cur, mundo["id"]), ahora=sabado)
    conn.commit()

    assert resumen["pospuestos"] == 1 and transporte.enviados == []
