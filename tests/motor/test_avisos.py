"""Los avisos guardados: cómo salen (`leda.motor.avisos`; E2-5).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Avisos guardados", "Horario" y "Fallas de la
IA"); ADR 0018, decisiones 8 (caso 2), 9b, 9e y 9f; conversaciones 02 y 11. Al llegar su hora,
dentro del horario, el código vuelve a leer la tarea; si todavía corresponde, la IA lo redacta
desde los hechos de ese momento y va al outbox; si no, se omite con su motivo. La IA es
guionada y el reloj, fijo en cada paso: el lunes 5 de octubre de 2026 en Buenos Aires (UTC-3).
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from leda.db import admin
from leda.motor.ia import IAGuionada, Jugada

from tests.motor.ayudantes import (AHORA, T1, cuantas, dice, enviar, jugada_prevision,
                                   nueva_tarea, octubre, todos, uno)


def _avisos(conn) -> list[dict]:
    return todos(conn, "select * from scheduled_notice order by creado_en, dedupe_key")


# --- El aviso de una nueva previsión (conversación 02, paso 3) -------------------------------

def test_el_aviso_al_referente_sale_redactado_desde_los_hechos_a_su_hora(conn, mundo, escribe):
    ismael = mundo["personas"]["Ismael"]
    dice(conn, escribe, jugada_prevision("T1", "2026-10-14", "el proveedor se demoró"))
    ia = IAGuionada(redacciones=["Marcos prevé terminar el miércoles 14."])

    resumen = enviar(conn, mundo, ia, AHORA)

    assert resumen == {"enviado": 1}
    [pedido] = ia.pedidos_de_redaccion
    assert pedido["persona"] == "Ismael" and pedido["mensaje"] is None
    assert pedido["pregunta"] is None       # el aviso no espera respuesta por chat
    assert pedido["hechos"] == [{
        "aviso": "nueva_prevision", "necesita_respuesta": False,
        "tarea": "Revisar el tablero", "responsable": "Marcos", "prevision": "2026-10-14",
        "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-09",
        "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": []}]
    [aviso] = _avisos(conn)
    assert aviso["estado"] == "enviado" and aviso["intentos"] == 1
    assert aviso["resuelto_en"] == AHORA and aviso["turno_id"] is not None
    salida = uno(conn, "select * from message_outbox where id = %s", aviso["outbox_id"])
    assert salida["cuerpo"] == "Marcos prevé terminar el miércoles 14."
    assert salida["chat_id"] == ismael["telegram"] and salida["es_respuesta"] is False
    assert salida["es_coordinacion"] is True     # lo causa el acto de otra persona (§10)
    turno = uno(conn, """select * from conversation_turn
                           where membership_id = %s""", ismael["membership_id"])
    assert turno["sentido"] == "salida" and turno["outbox_id"] == salida["id"]
    assert uno(conn, "select ultimo_aviso_id from conversation_state where membership_id = %s",
               ismael["membership_id"])["ultimo_aviso_id"] == aviso["id"]

    assert enviar(conn, mundo, IAGuionada(), AHORA) == {}       # nada sale dos veces


# --- Horario (9e; conversación 11, paso 3) -----------------------------------------------------

def test_fuera_del_horario_no_sale_nada_que_leda_inicie(conn, mundo, escribe):
    """La respuesta sale enseguida; el aviso a Ismael espera a la hora de salida del día hábil
    siguiente (10:00, `tiempo.HORA_DE_SALIDA`) y, antes, ni se redacta."""
    dice(conn, escribe, jugada_prevision("T1", "2026-10-14"), at=octubre(5, 17, 20))
    [aviso] = _avisos(conn)
    assert aviso["programado_para"] == octubre(6, 10)
    ia = IAGuionada(redacciones=["Aviso."])

    assert enviar(conn, mundo, ia, octubre(5, 18)) == {"fuera_de_horario": 1}
    assert enviar(conn, mundo, ia, octubre(6, 8, 30)) == {"fuera_de_horario": 1}
    assert enviar(conn, mundo, ia, octubre(6, 9, 30)) == {}     # en horario, antes de su hora
    assert ia.pedidos_de_redaccion == []
    assert cuantas(conn, "message_outbox", "not es_respuesta") == 0

    assert enviar(conn, mundo, ia, octubre(6, 10)) == {"enviado": 1}


def test_un_fin_de_semana_tampoco_sale(conn, mundo, escribe):
    dice(conn, escribe, jugada_prevision("T1", "2026-10-14"))
    sabado = octubre(10, 11)

    assert enviar(conn, mundo, IAGuionada(), sabado) == {"fuera_de_horario": 1}
    assert uno(conn, "select estado from scheduled_notice")["estado"] == "guardado"


# --- Lo que dejó de corresponder se omite con su motivo (9b; conversación 11, paso 5) ---------

def test_una_prevision_que_vuelve_a_la_fecha_comprometida_no_avisa_nada(conn, mundo, escribe):
    dice(conn, escribe, jugada_prevision("T1", "2026-10-14", "espero el switch"),
         at=octubre(5, 17, 20))
    dice(conn, escribe, jugada_prevision("T1", "2026-10-09"), at=octubre(6, 8, 30))
    ia = IAGuionada()

    resumen = enviar(conn, mundo, ia, octubre(6, 9))

    assert resumen == {} and ia.pedidos_de_redaccion == []
    [aviso] = _avisos(conn)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido",
                                                          "hay_una_prevision_mas_nueva")
    assert cuantas(conn, "message_outbox", "not es_respuesta") == 0
    assert cuantas(conn, "task_forecast") == 2         # la historia guarda las dos


def test_un_aviso_cuya_tarea_se_cerro_antes_de_salir_se_omite(conn, mundo, escribe):
    dice(conn, escribe, jugada_prevision("T1", "2026-10-14"), at=octubre(5, 17, 20))
    with admin(conn) as cur:
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind, motivo)
                       values (%s, 'asignada', 'cancelada', 'sistema', 'prueba')""",
                    (mundo["tarea"],))
    conn.commit()

    assert enviar(conn, mundo, IAGuionada(), octubre(6, 10)) == {"omitido": 1}
    aviso = _avisos(conn)[0]
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "tarea_cerrada")
    assert aviso["resuelto_en"] == octubre(6, 10)


# --- La corrección de una previsión (9f) -------------------------------------------------

def test_la_correccion_al_referente_sale_por_el_mismo_camino(conn, mundo, escribe):
    nueva_tarea(conn, mundo, "Probar las comunicaciones")
    dice(conn, escribe, jugada_prevision("T1", "2026-10-14"))
    enviar(conn, mundo, IAGuionada(redacciones=["Previsión."]), AHORA)
    dice(conn, escribe, Jugada("corregir", {"corrige": "anotar_prevision", "tarea": "T1"}))
    ia = IAGuionada(redacciones=["Corrección."])

    assert enviar(conn, mundo, ia, AHORA + timedelta(minutes=1)) == {"enviado": 1}
    [pedido] = ia.pedidos_de_redaccion
    assert pedido["persona"] == "Ismael"
    assert pedido["hechos"][0]["prevision_que_no_vale"] == "2026-10-14"
    assert pedido["hechos"][0]["fecha_comprometida"] == "2026-10-09"


def test_corregir_y_volver_a_una_prevision_anterior_rearma_su_aviso(conn, mundo, escribe):
    """Pendiente de la E2-4: el aviso de la previsión del 14 se retiró cuando Marcos dijo el
    20; si el 20 era de otra tarea, Ismael tiene que enterarse del 14, que nunca le llegó."""
    nueva_tarea(conn, mundo, "Probar las comunicaciones")
    dice(conn, escribe, jugada_prevision("T1", "2026-10-14", "el proveedor"), at=octubre(5, 17, 20))
    dice(conn, escribe, jugada_prevision("T1", "2026-10-20"), at=octubre(5, 17, 30))

    r = dice(conn, escribe, Jugada("corregir", {"corrige": "anotar_prevision", "tarea": "T1",
                                                  "tarea_correcta": "T2"}),
             at=octubre(5, 17, 40))

    [hecho] = r.hechos
    assert hecho["vuelve_a"] == {"prevision": "2026-10-14"}
    assert hecho["aviso_de_la_prevision_corregida"] == {"a": "Ismael",
                                                        "llega": "no_le_va_a_llegar"}
    assert hecho["aviso_de_la_prevision_anterior"]["llega"].startswith("2026-10-06T10:00")
    ia = IAGuionada(redacciones=["Aviso del 14.", "Aviso de T2."])
    assert enviar(conn, mundo, ia, octubre(6, 10)) == {"enviado": 2}
    de_t1 = [p["hechos"][0] for p in ia.pedidos_de_redaccion
             if p["hechos"][0]["tarea"] == T1["titulo"]]
    assert de_t1 == [{"aviso": "nueva_prevision", "necesita_respuesta": False,
                      "tarea": "Revisar el tablero", "responsable": "Marcos",
                      "prevision": "2026-10-14", "motivo": "el proveedor",
                      "fecha_comprometida": "2026-10-09",
                      "atraso_si_se_cumple_la_prevision_dias_habiles": 3,
                      "dependientes": []}]


def test_si_el_aviso_de_la_anterior_ya_habia_salido_no_se_repite(conn, mundo, escribe):
    nueva_tarea(conn, mundo, "Probar las comunicaciones")
    dice(conn, escribe, jugada_prevision("T1", "2026-10-14"))
    enviar(conn, mundo, IAGuionada(redacciones=["Aviso del 14."]), AHORA)
    dice(conn, escribe, jugada_prevision("T1", "2026-10-16"), at=octubre(5, 17, 30))

    r = dice(conn, escribe, Jugada("corregir", {"corrige": "anotar_prevision", "tarea": "T1"}),
             at=octubre(5, 17, 40))

    assert "aviso_de_la_prevision_anterior" not in r.hechos[0]
    assert cuantas(conn, "scheduled_notice", "estado = 'guardado'") == 0


# --- Si la IA no redacta (decisión 8, caso 2) ----------------------------------------------------

def test_si_la_ia_no_redacta_se_reintenta_a_los_1_2_4_y_8_minutos(conn, mundo, escribe):
    marcos = mundo["personas"]["Marcos"]
    dice(conn, escribe, jugada_prevision("T1", "2026-10-14"))
    caida = IAGuionada(redacciones=[RuntimeError("caída") for _ in range(5)])
    momento = AHORA
    for espera in (1, 2, 4, 8):
        assert enviar(conn, mundo, caida, momento) == {"reintento": 1}
        aviso = _avisos(conn)[0]
        assert aviso["proximo_intento_en"] == momento + timedelta(minutes=espera)
        # Antes del próximo intento no se vuelve a pedir.
        assert enviar(conn, mundo, caida, momento + timedelta(seconds=30)) == {}
        momento += timedelta(minutes=espera)
    assert len(caida.pedidos_de_redaccion) == 4

    assert enviar(conn, mundo, caida, momento) == {"fallido": 1}

    aviso, falla = _avisos(conn)
    assert (aviso["estado"], aviso["intentos"]) == ("fallido", 5)
    assert aviso["resuelto_en"] == momento and aviso["outbox_id"] is None
    assert aviso["hechos"]["prevision"] == "2026-10-14"        # queda con sus hechos
    incidente = uno(conn, "select * from incident")
    assert incidente["etapa"] == "motor_aviso_guardado"
    assert "Marcos" in incidente["resumen_sanitizado"]
    # A quien lo causó le llega el aviso de la falla, que también redacta la IA.
    assert falla["tipo"] == "falla_de_aviso"
    assert str(falla["destinatario_membership_id"]) == marcos["membership_id"]
    assert falla["hechos"]["aviso_que_no_salio"]["a"] == "Ismael"
    assert falla["hechos"]["aviso_que_no_salio"]["llega"] == "no_le_llego"
    assert falla["hechos"]["aviso_que_no_salio"]["lo_pendiente"] == aviso["hechos"]
    assert cuantas(conn, "message_outbox", "not es_respuesta") == 0   # ningún texto fijo

    ia = IAGuionada(redacciones=["No le pude avisar a Ismael."])
    assert enviar(conn, mundo, ia, momento) == {"enviado": 1}
    assert uno(conn, "select chat_id from message_outbox where not es_respuesta")[
        "chat_id"] == marcos["telegram"]


def test_si_tampoco_sale_el_aviso_de_la_falla_queda_el_incidente(conn, mundo, escribe):
    dice(conn, escribe, jugada_prevision("T1", "2026-10-14"))
    caida = IAGuionada(redacciones=[RuntimeError("caída") for _ in range(10)])
    momento = AHORA
    for _ in range(10):
        enviar(conn, mundo, caida, momento)
        momento += timedelta(minutes=10)

    estados = [(a["tipo"], a["estado"]) for a in _avisos(conn)]
    assert estados == [("nueva_prevision", "fallido"), ("falla_de_aviso", "fallido")]
    assert cuantas(conn, "incident") == 2


# --- Ausencias (mecánica §9) -----------------------------------------------------------------

def test_a_alguien_ausente_no_le_llega_nada_hasta_que_vuelve(conn, mundo, escribe):
    with admin(conn) as cur:
        cur.execute("""insert into absence (workspace_id, membership_id, desde, hasta)
                       values (%s, %s, '2026-10-05', '2026-10-06')""",
                    (mundo["id"], mundo["personas"]["Ismael"]["membership_id"]))
    conn.commit()
    dice(conn, escribe, jugada_prevision("T1", "2026-10-14"))
    ia = IAGuionada(redacciones=["Aviso."])

    assert enviar(conn, mundo, ia, AHORA) == {"en_espera": 1}
    assert enviar(conn, mundo, ia, octubre(6, 10)) == {"en_espera": 1}
    assert ia.pedidos_de_redaccion == []
    assert enviar(conn, mundo, ia, octubre(7, 9)) == {"enviado": 1}


@pytest.mark.parametrize("columna, motivo", [("telegram_user_id", "destinatario_sin_telegram")])
def test_un_destinatario_que_no_se_puede_alcanzar_se_dice(conn, mundo, escribe, columna, motivo):
    dice(conn, escribe, jugada_prevision("T1", "2026-10-14"))
    with admin(conn) as cur:
        cur.execute(f"update app_user set {columna} = null where id = %s",
                    (mundo["personas"]["Ismael"]["app_user_id"],))
    conn.commit()

    assert enviar(conn, mundo, IAGuionada(), AHORA) == {"omitido": 1}
    assert _avisos(conn)[0]["motivo_omision"] == motivo
