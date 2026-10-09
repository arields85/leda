"""La escalera del motor (`leda.motor.escalera`; diseño probado en la Etapa 2, E2-5).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Escalera"); mecánica §9 (anclada al
vencimiento V, en días hábiles del espacio, comprimida para una tarea corta, privada hasta el
escalamiento; un bloqueo la detiene; una ausencia la pausa y la vuelta lleva un reencuadre);
ADR 0018, decisión 9b (un solo aviso previo N días hábiles antes, sin pedir respuesta; desde V
cada recordatorio pide el estado y abre una espera; sin respuesta, V+1, V+2 avisando que va a
escalar y V+3 por la ruta `falta_persistente_de_respuesta`); ADR 0017, decisión 6
(`pending_reply`); conversaciones 01, 02 y 04.

El reloj se mueve por días: la tarea "Revisar el tablero" de Marcos vence el viernes 9 de
octubre de 2026; el sábado 10 y el domingo 11 no son hábiles y el lunes 12 es feriado. Cada
"ciclo" corre la escalera y manda los avisos guardados, como el ciclo (`ayudantes.Dias`). La IA
es guionada: redacta siempre y guarda lo que recibió.

Portadas de `prueba_chica/test_escalera.py`.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from leda.db import admin
from leda.motor.avisos import ETAPA_AVISO_GUARDADO, enviar_avisos
from leda.motor.escalera import ETAPA_ESCALERA, correr_escalera
from leda.motor.ia import Jugada
from leda.motor.tiempo import RelojFijo

from tests.motor.ayudantes import (IAQueRedacta, avisos_guardados, cambiar_el_vencimiento, cuantas,
                                   dice, dice_una_prevision, espera_del_estado, lo_que_salio_para,
                                   nueva_tarea, octubre, todos, uno)


# --- El aviso previo (9b; conversaciones 01 y 04) -----------------------------------------------

def test_el_aviso_previo_sale_una_sola_vez_n_dias_habiles_antes(conn, mundo, dias):
    assert dias.ciclo(octubre(5, 10)) == []        # faltan 4 días hábiles

    [pedido] = dias.ciclo(octubre(6, 10))          # faltan 3

    assert pedido["persona"] == "Marcos" and pedido["pregunta"] is None
    assert pedido["hechos"] == [{"aviso": "vencimiento_proximo", "necesita_respuesta": False,
                                 "tarea": "Revisar el tablero", "vence": "2026-10-09",
                                 "dias_habiles_hasta_el_vencimiento": 3}]
    [aviso] = avisos_guardados(conn)
    assert aviso["tipo"] == "aviso_previo" and aviso["estado"] == "enviado"
    assert uno(conn, "select tipo from message_outbox")["tipo"] == "informativo"
    assert espera_del_estado(conn) is None         # no pide respuesta
    assert cuantas(conn, "conversation_question") == 0
    for dia in (7, 8):                             # uno solo (conversación 01, paso 3)
        assert dias.ciclo(octubre(dia, 10)) == []
    assert cuantas(conn, "scheduled_notice") == 1


def test_lo_que_leda_manda_por_su_cuenta_no_espera_el_margen_para_corregir(conn, mundo, dias):
    """El margen para corregir (`margen.py`) es para lo que una persona dijo y le llega a otra:
    la escalera no sale de lo que nadie dijo, así que sale a su hora aunque el espacio tenga un
    margen largo (decisión del usuario, 2026-10-07)."""
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, 'margen_para_corregir_minutos', '30')""", (mundo["id"],))
    conn.commit()

    [previo] = dias.ciclo(octubre(6, 10))
    [pedido] = dias.ciclo(octubre(9, 10))

    assert previo["hechos"][0]["aviso"] == "vencimiento_proximo"
    assert pedido["hechos"][0]["aviso"] == "pedido_de_estado"
    assert [(a["tipo"], a["programado_para"]) for a in avisos_guardados(conn)] == [
        ("aviso_previo", octubre(6, 10)), ("pedido_de_estado", octubre(9, 10))]


def test_una_tarea_corta_comprime_el_aviso_previo(conn, mundo, dias):
    """Una tarea con menos días hábiles por delante que el aviso previo lo recibe enseguida
    (mecánica §9: la escalera se comprime, nunca saltea un paso)."""
    [pedido] = dias.ciclo(octubre(8, 10))         # vence mañana

    assert pedido["hechos"][0]["dias_habiles_hasta_el_vencimiento"] == 1
    assert dias.ciclo(octubre(8, 15)) == []


def test_correr_la_escalera_dos_veces_no_hace_nada_nuevo(conn, mundo, dias):
    for _ in range(2):
        correr_escalera(conn, mundo["id"], RelojFijo(octubre(6, 10)))
        conn.commit()
    assert cuantas(conn, "scheduled_notice") == 1
    dias.ciclo(octubre(6, 10))
    dias.ciclo(octubre(9, 10))
    dias.ciclo(octubre(9, 10))
    assert cuantas(conn, "scheduled_notice") == 2
    assert cuantas(conn, "message_outbox") == 2
    assert cuantas(conn, "pending_reply") == 1


# --- Sin respuesta: de V al escalamiento (conversación 04) ------------------------------------

def test_sin_respuesta_la_escalera_avanza_un_dia_habil_por_paso_y_escala(conn, mundo, dias):
    ismael, marcos = mundo["personas"]["Ismael"], mundo["personas"]["Marcos"]
    dias.ciclo(octubre(6, 10))                     # el aviso previo

    [v] = dias.ciclo(octubre(9, 10))

    assert v["hechos"] == [{"aviso": "pedido_de_estado", "numero": 1,
                            "necesita_respuesta": True, "tarea": "Revisar el tablero",
                            "vence": "2026-10-09", "atraso_dias_habiles": 0,
                            "estado": "asignada",
                            "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina",
                                                   "si_esta_trabada"]}]
    assert v["pregunta"] == {"tipo": "estado_de_la_tarea",
                             "tarea": {"titulo": "Revisar el tablero"}, "desde_antes": False}
    espera = espera_del_estado(conn)
    assert str(espera["membership_id"]) == marcos["membership_id"]
    assert str(espera["task_id"]) == mundo["tarea"]
    assert espera["satisfecho_en"] is None and espera["recordatorios"] == 1
    pregunta = uno(conn, """select q.tipo, q.se_puede_dejar from conversation_state s
                              join conversation_question q on q.id = s.pregunta_abierta_id
                             where s.membership_id = %s""", marcos["membership_id"])
    assert pregunta == {"tipo": "estado_de_la_tarea", "se_puede_dejar": False}

    # Sin respuesta, la repetición del día a las 4 horas, haya o no otro tema esperando
    # (decisiones 21 y 29 del usuario; `pregunta_sin_contestar.py`): no es un paso de la escalera.
    [repeticion] = dias.ciclo(octubre(9, 15))
    assert repeticion["hechos"][0]["aviso"] == "repeticion_del_dia"
    assert repeticion["pregunta"]["tipo"] == "estado_de_la_tarea"
    # Nada más el viernes, el fin de semana ni el feriado del lunes.
    for momento in (octubre(9, 16), octubre(10, 10), octubre(11, 10), octubre(12, 10)):
        assert dias.ciclo(momento) == []

    [v1] = dias.ciclo(octubre(13, 10))
    assert v1["hechos"][0]["numero"] == 2 and v1["hechos"][0]["atraso_dias_habiles"] == 1
    assert "si_no_hay_respuesta" not in v1["hechos"][0]
    [v2] = dias.ciclo(octubre(14, 10))
    assert v2["hechos"][0]["numero"] == 3
    assert v2["hechos"][0]["si_no_hay_respuesta"] == {"se_avisa_a": ["Ismael"]}
    # Tres pedidos y la repetición del viernes: también es un recordatorio de esa espera.
    assert espera_del_estado(conn)["recordatorios"] == 4

    [v3] = dias.ciclo(octubre(15, 10))

    assert v3["persona"] == "Ismael" and v3["pregunta"] is None
    assert v3["hechos"] == [{"aviso": "falta_de_respuesta", "necesita_respuesta": False,
                             "pedidos_de_estado_sin_respuesta": 3,
                             "pedido_desde": "2026-10-09", "tarea": "Revisar el tablero",
                             "vence": "2026-10-09", "atraso_dias_habiles": 3,
                             "estado": "asignada", "responsable": "Marcos"}]
    escalamiento = uno(conn, "select * from message_outbox where chat_id = %s",
                       ismael["telegram"])
    assert escalamiento["tipo"] == "prioritario" and escalamiento["es_respuesta"] is False
    assert espera_del_estado(conn)["escalado_en"] == octubre(15, 10)
    assert dias.ciclo(octubre(16, 10)) == [] and dias.ciclo(octubre(19, 10)) == []
    # El aviso previo, los tres pedidos y la repetición del viernes (decisión 29).
    assert len(lo_que_salio_para(conn, mundo, "Marcos")) == 5
    assert len(lo_que_salio_para(conn, mundo, "Ismael")) == 1


def test_los_recordatorios_dicen_la_prevision_y_lo_que_depende(conn, mundo, dias, escribe):
    """Conversación 02, paso 4: el recordatorio sigue contra la fecha comprometida y dice que
    Marcos ya dio una previsión y que Ismael está al tanto; lo que depende, como impacto."""
    otra = nueva_tarea(conn, mundo, "Probar las comunicaciones")
    with admin(conn) as cur:
        cur.execute("""insert into dependency (workspace_id, origen_task_id, destino_task_id)
                       values (%s, %s, %s)""", (mundo["id"], mundo["tarea"], otra))
    conn.commit()
    dice(conn, escribe, Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-14",
                                                    "motivo": "el proveedor"}),
         at=octubre(6, 15))
    dias.ciclo(octubre(6, 15, 30))         # el aviso a Ismael (y el aviso previo)

    [v] = [p for p in dias.ciclo(octubre(9, 10)) if p["persona"] == "Marcos"]

    hechos = v["hechos"][0]
    assert hechos["prevision_vigente"] == {
        "fecha": "2026-10-14", "motivo": "el proveedor",
        "atraso_si_se_cumple_la_prevision_dias_habiles": 2,
        "aviso_al_referente": {"a": "Ismael", "llega": "ya_le_llego"}}
    assert hechos["dependientes"] == [{"tarea": "Probar las comunicaciones",
                                       "no_puede_arrancar_hasta_que_termine": True}]


# --- Una respuesta detiene la escalera (9b) -----------------------------------------------------

@pytest.mark.parametrize("jugada", [
    Jugada("anotar_inicio", {"tarea": "T1"}),
    # Una previsión lleva la escalera a su fecha (9i, `test_ancla.py`): una posterior a los días
    # que mira esta prueba.
    Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-20", "motivo": "el proveedor"}),
    Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "falta el repuesto"}),
], ids=lambda j: j.nombre)
def test_una_respuesta_cierra_la_espera_y_la_pregunta_y_detiene_la_escalera(conn, mundo, dias,
                                                                            escribe, jugada):
    dias.ciclo(octubre(9, 10))

    dice(conn, escribe, jugada, at=octubre(9, 11))

    assert espera_del_estado(conn)["satisfecho_en"] == octubre(9, 11)
    pregunta = uno(conn, """select cierre from conversation_question
                              where tipo = 'estado_de_la_tarea'""")
    assert pregunta["cierre"] == "respondida"
    for dia in (13, 14, 15, 16):
        dias.ciclo(octubre(dia, 10))
    assert cuantas(conn, "scheduled_notice", "tipo in ('pedido_de_estado', 'escalamiento')") \
        == 1
    # A Ismael, sólo el aviso de la previsión o, con el bloqueo, el escalamiento de la pregunta
    # de quién lo destraba, que Marcos nunca contestó (9c, paso 4; 2026-10-05).
    al_referente = [a["tipo"] for a in avisos_guardados(conn) if a["estado"] == "enviado"
                    and str(a["destinatario_membership_id"])
                    == mundo["personas"]["Ismael"]["membership_id"]]
    assert al_referente == {"anotar_inicio": [], "anotar_prevision": ["nueva_prevision"],
                            "anotar_bloqueo": ["escalamiento_de_una_pregunta"]}[jugada.nombre]


def test_un_pedido_guardado_que_ya_se_contesto_no_sale(conn, mundo, dias, escribe):
    """Guardado antes de su hora; la persona escribe antes de que salga: se omite con su
    motivo, nunca en silencio, y la escalera queda detenida."""
    correr_escalera(conn, mundo["id"], RelojFijo(octubre(9, 7)))
    conn.commit()
    [pedido] = avisos_guardados(conn, "pedido_de_estado")
    assert pedido["programado_para"] == octubre(9, 10)
    dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(9, 8, 30))

    assert dias.ciclo(octubre(9, 10)) == []

    [pedido] = avisos_guardados(conn, "pedido_de_estado")
    assert (pedido["estado"], pedido["motivo_omision"]) == ("omitido", "ya_respondio")
    assert dias.ciclo(octubre(13, 10)) == []


# --- Un bloqueo abierto detiene la escalera (mecánica §9) ------------------------------------

def test_un_bloqueo_abierto_detiene_la_escalera(conn, mundo, dias, escribe):
    dice(conn, escribe, Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "falta el PLC"}),
         at=octubre(5, 11))

    # Ningún paso de la escalera de la tarea. Lo que sigue es la escalera de la pregunta de
    # quién lo destraba, que espera respuesta (`test_preguntas_que_esperan.py`), y, a los cinco
    # días hábiles, el bloqueo viejo (C-5, porción 5; `test_bloqueo_viejo.py`), que no es de la
    # escalera de la tarea.
    otros = ("repregunta", "falta_de_respuesta", "bloqueo_que_sigue_abierto")
    for dia in (6, 9, 13, 14, 15):
        assert [p for p in dias.ciclo(octubre(dia, 10))
                if any(h["aviso"] not in otros for h in p["hechos"])] == []
    assert cuantas(conn, "scheduled_notice",
                   "tipo not in ('repregunta', 'escalamiento_de_una_pregunta', "
                   "'bloqueo_que_sigue_abierto')") == 0
    assert cuantas(conn, "scheduled_notice", "tipo = 'bloqueo_que_sigue_abierto'") == 1
    assert espera_del_estado(conn) is None


def test_un_aviso_guardado_de_una_tarea_que_se_bloqueo_se_omite(conn, mundo, dias, escribe):
    correr_escalera(conn, mundo["id"], RelojFijo(octubre(9, 7)))
    conn.commit()
    dice(conn, escribe, Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "falta el PLC"}),
         at=octubre(9, 8))
    # El bloqueo contestó la espera; aun sin eso, la tarea bloqueada no lleva el pedido.
    with admin(conn) as cur:
        cur.execute("update pending_reply set satisfecho_en = null")
    conn.commit()

    assert dias.ciclo(octubre(9, 10)) == []
    [pedido] = avisos_guardados(conn, "pedido_de_estado")
    assert pedido["motivo_omision"] == "bloqueo_abierto"


def test_destrabar_un_bloqueo_que_detuvo_la_escalera_la_retoma(conn, mundo, dias, escribe):
    """Decisión del usuario, 2026-10-05 (ADR 0018, 9l; conversación 17): si el bloqueo había
    detenido la escalera (un paso guardado que no salió porque la tarea se bloqueó), al
    destrabarse el seguimiento vuelve. El día del vencimiento, destrabarse empieza una cuenta
    nueva, como un avance (9h): lo que detuvo la cuenta anterior no detiene la nueva."""
    correr_escalera(conn, mundo["id"], RelojFijo(octubre(9, 7)))
    conn.commit()
    dice(conn, escribe, Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "falta el PLC"}),
         at=octubre(9, 8))
    assert dias.ciclo(octubre(9, 10)) == []
    [omitido] = avisos_guardados(conn, "pedido_de_estado")
    assert omitido["motivo_omision"] == "bloqueo_abierto"

    dice(conn, escribe, Jugada("destrabar", {"tarea": "T1"}), at=octubre(9, 10, 30))

    [otra_vez] = dias.ciclo(octubre(13, 10))       # el lunes 12 es feriado
    assert otra_vez["hechos"][0]["aviso"] == "repregunta_de_estado"
    [sigue] = dias.ciclo(octubre(14, 10))          # sin respuesta, la escalera sigue
    assert sigue["hechos"][0]["aviso"] == "pedido_de_estado"


# --- Horario (9e) ---------------------------------------------------------------------------------

def test_lo_que_la_escalera_guarda_fuera_del_horario_sale_a_la_hora_de_salida(conn, mundo, dias):
    """Ni fuera del horario ni al empezar la jornada: a la hora de salida (10:00,
    `tiempo.HORA_DE_SALIDA`), la misma que dicen los hechos y el reloj adelantado."""
    assert dias.ciclo(octubre(9, 7)) == []
    assert dias.ciclo(octubre(9, 9)) == []
    assert cuantas(conn, "message_outbox") == 0

    [v] = dias.ciclo(octubre(9, 10))
    assert v["hechos"][0]["aviso"] == "pedido_de_estado"


# --- Ausencias (mecánica §9) ------------------------------------------------------------------

def _ausente(conn, mundo, desde: str, hasta: str | None) -> None:
    with admin(conn) as cur:
        cur.execute("""insert into absence (workspace_id, membership_id, desde, hasta)
                       values (%s, %s, %s, %s)""",
                    (mundo["id"], mundo["personas"]["Marcos"]["membership_id"], desde, hasta))
    conn.commit()


def test_una_ausencia_pausa_la_escalera_y_la_vuelta_lleva_un_reencuadre(conn, mundo, dias):
    dias.ciclo(octubre(6, 10))                     # el aviso previo
    [v] = dias.ciclo(octubre(9, 10))               # el primer pedido
    _ausente(conn, mundo, "2026-10-13", "2026-10-14")

    assert dias.ciclo(octubre(13, 10)) == [] and dias.ciclo(octubre(14, 10)) == []

    [vuelta] = dias.ciclo(octubre(15, 10))
    hechos = vuelta["hechos"][0]
    assert hechos["aviso"] == "vuelta_de_ausencia"
    assert hechos["ausencia"] == {"desde": "2026-10-13", "hasta": "2026-10-14"}
    assert hechos["necesita_respuesta"] is True and hechos["atraso_dias_habiles"] == 3
    assert vuelta["pregunta"]["tipo"] == "estado_de_la_tarea"
    assert avisos_guardados(conn, "reencuadre")[0]["estado"] == "enviado"
    # La repetición del día de su pregunta, a las 4 horas (decisión 29 del usuario).
    [repeticion] = dias.ciclo(octubre(15, 15))
    assert repeticion["hechos"][0]["aviso"] == "repeticion_del_dia"
    assert dias.ciclo(octubre(15, 16)) == []

    # Retoma desde donde quedó: el segundo pedido, no el escalamiento que le tocaba.
    [siguiente] = dias.ciclo(octubre(16, 10))
    assert siguiente["hechos"][0]["aviso"] == "pedido_de_estado"
    assert siguiente["hechos"][0]["numero"] == 2


def test_lo_guardado_para_alguien_que_se_ausenta_lo_reemplaza_el_reencuadre(conn, mundo, dias):
    correr_escalera(conn, mundo["id"], RelojFijo(octubre(9, 7)))   # el pedido, guardado
    conn.commit()
    _ausente(conn, mundo, "2026-10-09", "2026-10-13")

    assert dias.ciclo(octubre(9, 10)) == []
    [vuelta] = dias.ciclo(octubre(14, 10))

    assert vuelta["hechos"][0]["aviso"] == "vuelta_de_ausencia"
    [pedido] = avisos_guardados(conn, "pedido_de_estado")
    assert (pedido["estado"], pedido["motivo_omision"]) == ("omitido",
                                                            "reemplazado_por_el_reencuadre")
    [primero] = dias.ciclo(octubre(15, 10))
    assert primero["hechos"][0]["numero"] == 1


def test_una_ausencia_antes_del_vencimiento_cambia_el_aviso_previo_por_el_reencuadre(conn, mundo,
                                                                                    dias):
    _ausente(conn, mundo, "2026-10-05", "2026-10-06")

    assert dias.ciclo(octubre(6, 10)) == []
    [vuelta] = dias.ciclo(octubre(7, 10))

    hechos = vuelta["hechos"][0]
    assert hechos["aviso"] == "vuelta_de_ausencia" and hechos["necesita_respuesta"] is False
    assert hechos["dias_habiles_hasta_el_vencimiento"] == 2 and vuelta["pregunta"] is None
    assert dias.ciclo(octubre(8, 10)) == []
    assert avisos_guardados(conn, "aviso_previo") == []


def test_un_escalamiento_guardado_espera_si_el_responsable_se_ausenta(conn, mundo, dias):
    """Mecánica §9, ausencias: la escalera no avanza mientras la persona está ausente, tampoco
    su escalamiento, aunque vaya a otra persona. Uno ya guardado espera; a la vuelta lo
    reemplaza el reencuadre."""
    for dia in (9, 13, 14):                         # los tres pedidos, sin respuesta
        dias.ciclo(octubre(dia, 10))
    correr_escalera(conn, mundo["id"], RelojFijo(octubre(15, 9, 5)))  # el escalamiento, guardado
    conn.commit()
    [guardado] = avisos_guardados(conn, "escalamiento")
    assert guardado["estado"] == "guardado"
    _ausente(conn, mundo, "2026-10-15", "2026-10-15")

    assert dias.ciclo(octubre(15, 10)) == []
    assert lo_que_salio_para(conn, mundo, "Ismael") == []

    [vuelta] = dias.ciclo(octubre(16, 10))

    assert vuelta["persona"] == "Marcos"
    assert vuelta["hechos"][0]["aviso"] == "vuelta_de_ausencia"
    [escalamiento] = avisos_guardados(conn, "escalamiento")
    assert (escalamiento["estado"], escalamiento["motivo_omision"]) == (
        "omitido", "reemplazado_por_el_reencuadre")
    assert lo_que_salio_para(conn, mundo, "Ismael") == []


# --- Lo que falta configurar no queda en silencio -------------------------------------------

def test_sin_el_aviso_previo_configurado_usa_el_minimo_y_lo_registra(conn, mundo, dias):
    """El plan lo dejó `PENDIENTE`: sin `aviso_previo_dias_habiles`, el mínimo del núcleo (un
    día hábil, mecánica §9) y un incidente por cada aviso previo que salió con él."""
    with admin(conn) as cur:
        cur.execute("delete from workspace_setting where clave = 'aviso_previo_dias_habiles'")
    conn.commit()

    assert dias.ciclo(octubre(7, 10)) == []        # faltan 2 días hábiles
    [pedido] = dias.ciclo(octubre(8, 10))
    assert pedido["hechos"][0]["dias_habiles_hasta_el_vencimiento"] == 1
    dias.ciclo(octubre(8, 11))

    incidente = uno(conn, "select * from incident")
    assert incidente["etapa"] == ETAPA_ESCALERA and incidente["severidad"] == "baja"
    assert "aviso_previo_dias_habiles" in incidente["resumen_sanitizado"]
    assert cuantas(conn, "incident") == 1


# --- Un escalamiento termina la escalera de ese vencimiento (revisión de la E2-5) -------------


def test_un_vencimiento_nuevo_empieza_su_propia_escalera_despues_de_escalar(conn, mundo, dias):
    """Mecánica §9: la escalera se ancla a su vencimiento y termina al escalar. Si la persona
    nunca contestó, la espera queda abierta y escalada; con un vencimiento nuevo la escalera
    empieza de cero y no la frena el escalamiento del anterior.

    El aviso previo del vencimiento nuevo se guarda, pero espera: la pregunta del estado de la
    tarea sigue sin contestar y, de ese tema, sólo le llega la pregunta cuando Leda la repite
    (no interrumpir, decisión 13, punto 2; `PENDIENTE` del usuario en `odd/tasks/fase-c.md`,
    D5). El pedido del vencimiento nuevo es esa misma pregunta, repetida: sale solo."""
    for dia in (6, 9, 13, 14, 15):
        dias.ciclo(octubre(dia, 10))
    assert espera_del_estado(conn)["escalado_en"] == octubre(15, 10)
    assert dias.ciclo(octubre(16, 10)) == []               # la del 9 terminó

    cambiar_el_vencimiento(conn, mundo, datetime(2026, 10, 23, 20, 0, tzinfo=timezone.utc))

    assert dias.ciclo(octubre(20, 10)) == []               # faltan 3 días hábiles
    [previo] = [a for a in avisos_guardados(conn, "aviso_previo")
                if a["hechos"]["vence"] == "2026-10-23"]
    assert previo["estado"] == "guardado"
    [v] = dias.ciclo(octubre(23, 10))
    assert v["hechos"][0]["aviso"] == "pedido_de_estado" and v["hechos"][0]["numero"] == 1
    # La espera de esta escalera es nueva: la del vencimiento anterior quedó escalada.
    esperas = todos(conn, """select escalado_en, recordatorios from pending_reply
                               where satisfecho_en is null order by preguntado_en""")
    assert esperas == [{"escalado_en": octubre(15, 10), "recordatorios": 3},
                       {"escalado_en": None, "recordatorios": 1}]


# --- Un paso que no salió no apaga el seguimiento (revisión de la E2-5) -----------------------

class IAQueFallaPrimero(IAQueRedacta):
    """Falla las primeras `fallas` redacciones; después redacta."""

    def __init__(self, fallas: int) -> None:
        super().__init__()
        self.fallas = fallas

    def redactar(self, pedido: dict[str, Any]) -> str:
        if self.fallas:
            self.fallas -= 1
            raise RuntimeError("caída")
        return super().redactar(pedido)


def test_un_pedido_que_la_ia_no_redacto_no_detiene_la_escalera(conn, mundo, dias):
    """El primer pedido queda `fallido` tras los cinco intentos (con su incidente); la
    escalera sigue con el paso siguiente al día hábil siguiente, y los hechos dicen que el
    anterior no le llegó."""
    dias.ia = IAQueFallaPrimero(fallas=5)
    correr_escalera(conn, mundo["id"], RelojFijo(octubre(9, 10)))
    conn.commit()
    for minuto in (0, 1, 3, 7, 15):
        enviar_avisos(conn, mundo["id"], dias.ia, RelojFijo(octubre(9, 10, minuto)))
        conn.commit()
    [pedido] = avisos_guardados(conn, "pedido_de_estado")
    assert pedido["estado"] == "fallido"
    assert cuantas(conn, "incident", "etapa = %s", ETAPA_AVISO_GUARDADO) == 1

    [v1] = dias.ciclo(octubre(13, 10))

    assert v1["hechos"][0]["numero"] == 2
    assert v1["hechos"][0]["pedidos_anteriores_que_no_le_llegaron"] == 1
    assert v1["pregunta"]["tipo"] == "estado_de_la_tarea"
    dias.ciclo(octubre(14, 10))
    [v3] = dias.ciclo(octubre(15, 10))
    assert v3["persona"] == "Ismael"
    assert v3["hechos"][0]["pedidos_de_estado_sin_respuesta"] == 2
    assert v3["hechos"][0]["pedidos_de_estado_que_no_le_llegaron"] == 1
    assert v3["hechos"][0]["pedido_desde"] == "2026-10-13"


def test_un_pedido_omitido_porque_la_persona_contesto_si_detiene_la_escalera(conn, mundo, dias,
                                                                           escribe):
    """El primer pedido se omite porque Marcos contestó antes de que saliera: la escalera no
    vuelve a guardarlo ni abre otra espera."""
    correr_escalera(conn, mundo["id"], RelojFijo(octubre(9, 7)))
    conn.commit()
    dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(9, 8))
    dias.ciclo(octubre(9, 9))

    for dia in (13, 14, 15):
        assert dias.ciclo(octubre(dia, 10)) == []
    assert cuantas(conn, "pending_reply", "satisfecho_en is null") == 0


def test_sin_ruta_de_escalamiento_se_registra_y_no_se_repite(conn, mundo, dias):
    with admin(conn) as cur:
        cur.execute("delete from escalation_route")
    conn.commit()
    for dia in (9, 13, 14):
        dias.ciclo(octubre(dia, 10))
    assert "si_no_hay_respuesta" not in avisos_guardados(conn, "pedido_de_estado")[-1]["hechos"]

    assert dias.ciclo(octubre(15, 10)) == []
    dias.ciclo(octubre(16, 10))

    assert avisos_guardados(conn, "escalamiento") == []
    incidente = uno(conn, "select * from incident")
    assert incidente["etapa"] == ETAPA_ESCALERA and incidente["severidad"] == "media"
    assert cuantas(conn, "incident") == 1
    assert espera_del_estado(conn)["escalado_en"] == octubre(15, 10)


def test_la_escalera_de_un_vencimiento_nuevo_tambien_escala(conn, mundo, dias):
    """Revisión de la E2-6: la escalera nueva llega hasta su propio escalamiento, con su clave,
    aunque la del vencimiento anterior ya haya escalado a la misma persona."""
    for dia in (6, 9, 13, 14, 15):
        dias.ciclo(octubre(dia, 10))
    cambiar_el_vencimiento(conn, mundo, datetime(2026, 10, 23, 20, 0, tzinfo=timezone.utc))
    for dia in (20, 23, 26, 27):
        dias.ciclo(octubre(dia, 10))

    [escalamiento] = dias.ciclo(octubre(28, 10))

    assert escalamiento["persona"] == "Ismael"
    assert escalamiento["hechos"][0]["vence"] == "2026-10-23"
    assert escalamiento["hechos"][0]["pedido_desde"] == "2026-10-23"
    claves = [a["dedupe_key"].split(":")[3] for a in avisos_guardados(conn, "escalamiento")]
    assert claves == ["2026-10-09", "2026-10-23"]
    assert len(lo_que_salio_para(conn, mundo, "Ismael")) == 2
    assert dias.ciclo(octubre(29, 10)) == []


def test_un_escalamiento_que_reemplazo_un_reencuadre_no_cuenta_como_escalado(conn, mundo, dias):
    """Revisión de `informar_avance`: el escalamiento quedó guardado y la persona estuvo ausente
    ese día (el ciclo no llegó a mandarlo). A la vuelta, el reencuadre lo reemplaza: no salió,
    así que la escalera no terminó, y si no hay respuesta, escala el día hábil siguiente."""
    for dia in (9, 13, 14):
        dias.ciclo(octubre(dia, 10))
    correr_escalera(conn, mundo["id"], RelojFijo(octubre(15, 7)))  # el escalamiento, guardado
    conn.commit()
    _ausente(conn, mundo, "2026-10-15", "2026-10-15")

    [vuelta] = dias.ciclo(octubre(16, 10))

    assert vuelta["persona"] == "Marcos"
    assert vuelta["hechos"][0]["aviso"] == "vuelta_de_ausencia"
    [reemplazado] = avisos_guardados(conn, "escalamiento")
    assert (reemplazado["estado"], reemplazado["motivo_omision"]) == (
        "omitido", "reemplazado_por_el_reencuadre")

    [escalamiento] = dias.ciclo(octubre(19, 10))

    assert escalamiento["persona"] == "Ismael"
    assert escalamiento["hechos"][0]["aviso"] == "falta_de_respuesta"
    assert dias.ciclo(octubre(20, 10)) == []


def test_el_aviso_previo_no_se_repite_cuando_el_ancla_vuelve_al_vencimiento(conn, mundo, dias,
                                                                           escribe):
    """El aviso previo es de la fecha comprometida, no de un anclaje (revisión de la E2-7): si
    una previsión lleva el ancla a otra fecha y otra la devuelve al vencimiento, la escalera
    nueva del vencimiento no manda otro aviso previo."""

    [previo] = dias.ciclo(octubre(6, 10))
    assert previo["hechos"][0]["aviso"] == "vencimiento_proximo"
    dice_una_prevision(conn, escribe, "2026-10-15", at=octubre(6, 11))
    dice_una_prevision(conn, escribe, "2026-10-09", at=octubre(6, 12))

    for momento in (octubre(6, 13), octubre(7, 10), octubre(8, 10)):
        assert [p for p in dias.ciclo(momento) if p["persona"] == "Marcos"] == []
    assert len(avisos_guardados(conn, "aviso_previo")) == 1
