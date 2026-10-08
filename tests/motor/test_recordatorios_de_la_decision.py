"""Quien aprueba no contesta: los recordatorios de una decisión que espera (porción 3c de la C-3).

Decidido por el usuario (`odd/tasks/fase-c.md`, pregunta 3, con su precisión del 2026-10-07;
conversación 24): un recordatorio a quien aprueba al día hábil siguiente del aviso de la entrega
y otro al segundo, que avisa que al día siguiente se entera quien está arriba (sólo si hay
alguien). Al tercero, quien está arriba (Nahuel → Marcos → Ismael) recibe un aviso sólo
informativo de que la aprobación está trabada: no le pide nada ni lo convierte en aprobador.
Quien aprueba sigue con un recordatorio cordial por día hábil hasta decidir y, cuando decide, a
quien está arriba le llega que se destrabó. Sin nadie arriba, un recordatorio por día hábil. Al
responsable nunca le llega nada de esto: no depende de él. Todo en días hábiles y dentro del
horario del espacio (ADR 0018, 9e), y releído al salir (decisión 8, 9b).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import pytest

from leda.autoridad import identificar_en_espacio
from leda.db import admin, espacio
from leda.motor import preguntas
from leda.motor.ia import IAGuionada, Jugada
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import procesar_turno

from tests.motor.ayudantes import (AHORA, VIERNES_16, Dias, avisos_guardados,
                                   cambiar_el_vencimiento, estado_de, octubre, poner_estado, todos,
                                   uno)

RECORDATORIO = "recordatorio_de_la_decision"
TRABADA = "aprobacion_trabada"
DESTRABADA = "aprobacion_destrabada"
DE_NAHUEL = "Actualizar los planos de la paila"
DE_MARCOS = "Programar el PLC"


# --- Ayudas ---------------------------------------------------------------------------------

def _nahuel(conn, mundo) -> None:
    """Otra persona del espacio, cuyo trabajo aprueba Marcos (a Marcos lo aprueba Ismael, y a
    Ismael nadie)."""
    with admin(conn) as cur:
        cur.execute("select rol_id from membership where id = %s",
                    (mundo["personas"]["Marcos"]["membership_id"],))
        rol = cur.fetchone()["rol_id"]
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (81009, 'Nahuel Gimenez') returning id""")
        usuario = str(cur.fetchone()["id"])
        cur.execute("""insert into membership (workspace_id, app_user_id, area_id, rol_id,
                                               aprobador_membership_id)
                       values (%s, %s, %s, %s, %s) returning id""",
                    (mundo["id"], usuario, mundo["area"], rol,
                     mundo["personas"]["Marcos"]["membership_id"]))
        mundo["personas"]["Nahuel"] = {"app_user_id": usuario, "telegram": 81009,
                                       "membership_id": str(cur.fetchone()["id"])}
        cur.execute("""insert into greeting_state (membership_id, workspace_id, ultima_fecha_local)
                       values (%s, %s, date '9999-12-31')""",
                    (mundo["personas"]["Nahuel"]["membership_id"], mundo["id"]))
    conn.commit()


def _tarea(conn, mundo, titulo: str, quien: str,
           criterio: str | None = "Lo pedido, hecho y probado") -> str:
    """Una tarea en curso de `quien`, sin evidencia que pida su área."""
    with admin(conn) as cur:
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, estado, fecha_objetivo,
                                 criterio_aceptacion)
               values (%s, %s, %s, %s, %s, 'asignada', %s, %s) returning id""",
            (mundo["id"], mundo["objetivo"], titulo, mundo["area"],
             mundo["personas"][quien]["membership_id"], VIERNES_16, criterio))
        tarea = str(cur.fetchone()["id"])
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind, motivo, at)
                       values (%s, 'asignada', 'en_curso', 'persona', 'prueba', %s)""",
                    (tarea, AHORA - timedelta(days=3)))
    conn.commit()
    return tarea


def _dice(conn, mundo, nombre: str, *jugadas: Jugada, at: datetime, texto: str = "-"):
    persona = mundo["personas"][nombre]
    with espacio(conn, mundo["id"]) as cur:
        quien = identificar_en_espacio(cur, persona["telegram"], mundo["id"])
        cur.execute(
            """insert into inbound_message (workspace_id, telegram_message_id, chat_id,
                                            app_user_id, texto, at)
               values (%s, %s, %s, %s, %s, %s) returning id""",
            (mundo["id"], uuid.uuid4().int % 1_000_000, persona["telegram"],
             persona["app_user_id"], texto, at))
        entrante = str(cur.fetchone()["id"])
    conn.commit()
    ia = IAGuionada(jugadas=[list(jugadas)], redacciones=["Listo."])
    r = procesar_turno(conn, quien, entrante, ia, RelojFijo(at))
    conn.commit()
    assert r.error is None, r.error
    return r, ia


def _entrega(conn, mundo, nombre: str, minuto: int = 0) -> None:
    """La persona entrega su única tarea, con lo que describe su criterio de aceptación (C-3d,
    D3), y la confirma, el lunes 5 a la mañana."""
    _dice(conn, mundo, nombre, Jugada("entregar", {"tarea": "T1", "lo_descrito_cubre": ["C1"]}),
          at=octubre(5, 11, minuto), texto="termine, quedo hecho y probado")
    _dice(conn, mundo, nombre, Jugada("confirmar", {}), at=octubre(5, 11, minuto + 1),
          texto="dale")


@pytest.fixture
def dias(conn, mundo) -> Dias:
    """Nahuel y Marcos entregan una tarea cada uno el lunes 5 y los avisos de las entregas salen
    (a Marcos, el de Nahuel; a Ismael, el de Marcos). La tarea del mundo sale de la escalera."""
    _nahuel(conn, mundo)
    cambiar_el_vencimiento(conn, mundo, None)
    mundo["de_nahuel"] = _tarea(conn, mundo, DE_NAHUEL, "Nahuel")
    _entrega(conn, mundo, "Nahuel")
    poner_estado(conn, mundo["tarea"], "cancelada")     # así la de Marcos es su T1
    mundo["de_marcos"] = _tarea(conn, mundo, DE_MARCOS, "Marcos")
    _entrega(conn, mundo, "Marcos", minuto=30)
    d = Dias(conn, mundo)
    salieron = d.ciclo(octubre(5, 12))
    assert sorted(a["aviso"] for p in salieron for a in p["hechos"]) == \
        ["entrega_para_aprobar"] * 2
    return d


def _de(pedidos: list[dict], aviso: str) -> list[dict]:
    return [h for p in pedidos for h in p["hechos"] if h.get("aviso") == aviso]


def _para(pedidos: list[dict], persona: str) -> list[dict]:
    return [p for p in pedidos if p["persona"] == persona]


def _de_tipos(conn, *tipos: str) -> list[dict]:
    return [a for a in avisos_guardados(conn) if a["tipo"] in tipos]


# --- Los recordatorios a quien aprueba --------------------------------------------------------

def test_ningun_recordatorio_el_mismo_dia_de_la_entrega(conn, mundo, dias):
    for hora in (13, 15, 16):
        assert _de(dias.ciclo(octubre(5, hora)), RECORDATORIO) == []
    assert _de_tipos(conn, RECORDATORIO, TRABADA) == []


def test_el_primer_dia_habil_un_recordatorio_a_cada_uno_que_no_abre_otra_pregunta(conn, mundo,
                                                                                 dias):
    pedidos = dias.ciclo(octubre(6, 10))
    [a_marcos] = _para(pedidos, "Marcos")
    [h] = a_marcos["hechos"]
    assert h["aviso"] == RECORDATORIO and h["tarea"] == DE_NAHUEL
    assert h["responsable"] == "Nahuel Gimenez" and h["entregada_el"] == "2026-10-05"
    assert h["necesita_respuesta"] is True and h["veces_que_se_lo_recuerda"] == 1
    assert "si_sigue_sin_decidir" not in h
    # Recuerda la decisión que ofreció el aviso de la entrega: la misma pregunta, sin botones.
    assert a_marcos["pregunta"]["tipo"] == preguntas.DECISION_DE_LA_ENTREGA
    assert a_marcos["pregunta"]["desde_antes"] is True and "opciones" not in a_marcos["pregunta"]
    [a_ismael] = _para(pedidos, "Ismael")
    assert [h["tarea"] for h in a_ismael["hechos"]] == [DE_MARCOS]
    # Ninguna pregunta nueva ni ninguna espera para quien aprueba: la decisión no es un tema
    # abierto y la sigue ofreciendo el aviso de la entrega.
    assert uno(conn, "select 1 from conversation_state where pregunta_abierta_id is not null") \
        is None
    assert todos(conn, "select * from pending_reply") == []
    [decision] = todos(conn, """select * from conversation_question
                                 where task_id = %s and cerrada_en is null""",
                       mundo["de_nahuel"])
    assert decision["tipo"] == preguntas.DECISION_DE_LA_ENTREGA
    # Ningún botón en el recordatorio: los de la decisión van con el aviso de la entrega.
    assert len(todos(conn, """select o.id from scheduled_notice a
                                join conversation_question q
                                  on q.jugada ->> 'del_aviso' = a.id::text
                                join conversation_option o on o.question_id = q.id
                               where a.tipo = %s""", RECORDATORIO)) == 0


def test_el_segundo_avisa_que_manana_se_entera_quien_esta_arriba_solo_si_hay_alguien(
        conn, mundo, dias):
    dias.ciclo(octubre(6, 10))
    pedidos = dias.ciclo(octubre(7, 10))
    [de_nahuel] = _de(_para(pedidos, "Marcos"), RECORDATORIO)
    assert de_nahuel["veces_que_se_lo_recuerda"] == 2
    assert de_nahuel["si_sigue_sin_decidir"] == {"se_avisa_a": ["Ismael"],
                                                 "fecha": "2026-10-08"}
    [de_marcos] = _de(_para(pedidos, "Ismael"), RECORDATORIO)
    assert de_marcos["veces_que_se_lo_recuerda"] == 2
    assert "si_sigue_sin_decidir" not in de_marcos      # a Ismael no lo aprueba nadie


def test_al_tercero_quien_esta_arriba_se_entera_una_sola_vez_y_sin_que_se_le_pida_nada(
        conn, mundo, dias):
    for dia in (6, 7):
        dias.ciclo(octubre(dia, 10))
    pedidos = dias.ciclo(octubre(8, 10))
    [a_ismael] = _para(pedidos, "Ismael")       # un envío: lo de los dos, cada uno con lo suyo
    trabada = next(h for h in a_ismael["hechos"] if h["aviso"] == TRABADA)
    assert trabada["tarea"] == DE_NAHUEL and trabada["responsable"] == "Nahuel Gimenez"
    assert trabada["quien_aprueba"] == "Marcos" and trabada["entregada_el"] == "2026-10-05"
    assert trabada["necesita_respuesta"] is False
    assert trabada["leda_se_lo_sigue_recordando"] is True
    assert trabada["se_le_avisa_cuando_decida"] is True
    recordatorio = next(h for h in a_ismael["hechos"] if h["aviso"] == RECORDATORIO)
    assert recordatorio["tarea"] == DE_MARCOS and recordatorio["veces_que_se_lo_recuerda"] == 3
    # La única pregunta del envío es la del recordatorio de la tarea que sí decide Ismael.
    assert a_ismael["pregunta"]["tarea"]["titulo"] == DE_MARCOS
    [a_marcos] = _de(_para(pedidos, "Marcos"), RECORDATORIO)
    assert a_marcos["veces_que_se_lo_recuerda"] == 3 and "si_sigue_sin_decidir" not in a_marcos

    viernes = dias.ciclo(octubre(9, 10))
    assert [h["tarea"] for h in _de(_para(viernes, "Ismael"), RECORDATORIO)] == [DE_MARCOS]
    assert _de(viernes, TRABADA) == []
    assert [h["veces_que_se_lo_recuerda"] for h in _de(_para(viernes, "Marcos"),
                                                       RECORDATORIO)] == [4]
    assert len(_de_tipos(conn, TRABADA)) == 1


def test_quien_esta_arriba_no_es_aprobador_de_esa_entrega(conn, mundo, dias):
    for dia in (6, 7, 8):
        dias.ciclo(octubre(dia, 10))
    # Ismael no tiene ninguna decisión abierta sobre la tarea de Nahuel, ni la ve para decidir.
    assert todos(conn, """select * from conversation_question
                           where task_id = %s and membership_id = %s""",
                 mundo["de_nahuel"], mundo["personas"]["Ismael"]["membership_id"]) == []
    r, ia = _dice(conn, mundo, "Ismael", Jugada("aprobar", {"de": "nahuel"}),
                  at=octubre(8, 11), texto="lo de nahuel aprobalo")
    assert not any(t.get("titulo") == DE_NAHUEL for t in ia.pedidos_de_jugadas[-1]["tareas"])
    [hecho] = [h for h in r.hechos if h.get("jugada") == "aprobar"]
    assert hecho["resultado"] == "no_se_puede" and hecho["motivo"] == "no_es_quien_aprueba"
    assert hecho["quien_aprueba"] == "Marcos"
    assert estado_de(conn, mundo["de_nahuel"]) == "en_revision"
    assert todos(conn, "select * from approval where sujeto_id = %s", mundo["de_nahuel"]) == []


def test_un_recordatorio_por_dia_habil_y_nada_fuera_del_horario(conn, mundo, dias):
    for dia in (6, 7, 8, 9):
        dias.ciclo(octubre(dia, 10))
    for momento in (octubre(10, 10), octubre(11, 10), octubre(12, 8)):   # sáb, dom, lun 08:00
        assert _de(dias.ciclo(momento), RECORDATORIO) == []
    # El del lunes ya está guardado para la hora de salida, y sale recién entonces.
    assert [a["estado"] for a in _de_tipos(conn, RECORDATORIO)
            if a["programado_para"] == octubre(12, 10)] == ["guardado", "guardado"]
    pedidos = dias.ciclo(octubre(12, 10))
    assert sorted(h["veces_que_se_lo_recuerda"] for h in _de(pedidos, RECORDATORIO)) == [5, 5]
    # Correr el ciclo otra vez el mismo día no guarda otro.
    assert _de(dias.ciclo(octubre(12, 15)), RECORDATORIO) == []


def test_sin_nadie_arriba_un_recordatorio_cordial_por_dia_habil_y_nada_mas(conn, mundo, dias):
    for dia in (6, 7, 8, 9, 12, 13):
        dias.ciclo(octubre(dia, 10))
    de_marcos = [a for a in _de_tipos(conn, RECORDATORIO, TRABADA)
                 if str(a["task_id"]) == mundo["de_marcos"]]
    assert [a["tipo"] for a in de_marcos] == [RECORDATORIO] * 6
    assert {str(a["destinatario_membership_id"]) for a in de_marcos} == \
        {mundo["personas"]["Ismael"]["membership_id"]}
    assert not any("si_sigue_sin_decidir" in a["hechos"] for a in de_marcos)


def test_al_responsable_nunca_le_llega_nada_de_esto(conn, mundo, dias):
    for dia in (6, 7, 8, 9, 12):
        dias.ciclo(octubre(dia, 10))
    responsables = {mundo["personas"]["Nahuel"]["membership_id"],
                    mundo["personas"]["Marcos"]["membership_id"]}
    for a in _de_tipos(conn, RECORDATORIO, TRABADA):
        responsable = uno(conn, "select responsable_membership_id r from task where id = %s",
                          a["task_id"])["r"]
        assert str(a["destinatario_membership_id"]) != str(responsable)
    assert responsables       # Marcos recibe por la de Nahuel, nunca por la suya
    assert todos(conn, """select * from message_outbox
                           where chat_id = %s and not es_respuesta""",
                 mundo["personas"]["Nahuel"]["telegram"]) == []


# --- Cuando decide ----------------------------------------------------------------------------

def test_cuando_decide_se_cortan_los_recordatorios_y_quien_esta_arriba_se_entera(conn, mundo,
                                                                                dias):
    for dia in (6, 7, 8):
        dias.ciclo(octubre(dia, 10))
    r, _ = _dice(conn, mundo, "Marcos", Jugada("aprobar", {"tarea": "T2"}), at=octubre(8, 11),
                 texto="lo de nahuel aprobado")
    [hecho] = [h for h in r.hechos if h.get("jugada") == "aprobar"]
    assert hecho["resultado"] == "anotado" and hecho["quedo_terminada"] is True
    assert hecho["aviso_de_que_se_destrabo"]["a"] == "Ismael"
    assert estado_de(conn, mundo["de_nahuel"]) == "terminada"
    [destrabada] = _de_tipos(conn, DESTRABADA)
    assert str(destrabada["destinatario_membership_id"]) == \
        mundo["personas"]["Ismael"]["membership_id"]

    pedidos = dias.ciclo(octubre(8, 11, 1))
    [h] = _de(_para(pedidos, "Ismael"), DESTRABADA)
    assert h["tarea"] == DE_NAHUEL and h["quien_aprueba"] == "Marcos"
    assert h["responsable"] == "Nahuel Gimenez" and h["quedo_terminada"] is True
    assert h["necesita_respuesta"] is False
    for dia in (9, 12):
        assert [x["tarea"] for x in _de(dias.ciclo(octubre(dia, 10)), RECORDATORIO)] == \
            [DE_MARCOS]
    assert len(_de_tipos(conn, DESTRABADA)) == 1


def test_sin_aviso_arriba_una_decision_no_avisa_a_nadie_mas(conn, mundo, dias):
    dias.ciclo(octubre(6, 10))
    r, _ = _dice(conn, mundo, "Ismael", Jugada("aprobar", {"tarea": "T1"}), at=octubre(6, 11),
                 texto="el plc aprobado")
    [hecho] = [h for h in r.hechos if h.get("jugada") == "aprobar"]
    assert "aviso_de_que_se_destrabo" not in hecho
    assert _de_tipos(conn, DESTRABADA) == []


def test_un_pedido_de_cambios_tambien_lo_destraba(conn, mundo, dias):
    for dia in (6, 7, 8):
        dias.ciclo(octubre(dia, 10))
    _dice(conn, mundo, "Marcos",
          Jugada("pedir_cambios", {"tarea": "T2", "comentario": "falta el plano unifilar"}),
          at=octubre(8, 11), texto="le falta el unifilar")
    assert estado_de(conn, mundo["de_nahuel"]) == "en_curso"
    [h] = _de(_para(dias.ciclo(octubre(8, 11, 1)), "Ismael"), DESTRABADA)
    assert h["pidio_cambios"] == "Marcos" and "quedo_terminada" not in h
    assert _de(dias.ciclo(octubre(9, 10)), RECORDATORIO) != []      # sólo el de la de Marcos
    assert all(x["tarea"] == DE_MARCOS for x in _de(dias.ciclo(octubre(12, 10)), RECORDATORIO))


def test_un_recordatorio_guardado_que_ya_no_corresponde_se_omite_con_su_motivo(conn, mundo,
                                                                              dias):
    dias.ciclo(octubre(6, 9))      # guardado para las 10:00
    _dice(conn, mundo, "Ismael", Jugada("aprobar", {"tarea": "T1"}), at=octubre(6, 9, 30),
          texto="el plc aprobado")
    dias.ciclo(octubre(6, 10))
    [omitido] = [a for a in _de_tipos(conn, RECORDATORIO)
                 if str(a["task_id"]) == mundo["de_marcos"]]
    assert omitido["estado"] == "omitido" and omitido["motivo_omision"] == "tarea_cerrada"


def test_una_aprobacion_que_no_cierra_igual_corta_los_recordatorios(conn, mundo):
    """Aprobada, pero sin el criterio de aceptación: sigue en revisión, pero ya decidió."""
    _nahuel(conn, mundo)
    cambiar_el_vencimiento(conn, mundo, None)
    tarea = _tarea(conn, mundo, DE_NAHUEL, "Nahuel", criterio=None)
    _entrega(conn, mundo, "Nahuel")
    d = Dias(conn, mundo)
    d.ciclo(octubre(5, 12))
    d.ciclo(octubre(6, 9))          # el recordatorio, guardado para las 10:00
    r, _ = _dice(conn, mundo, "Marcos", Jugada("aprobar", {"tarea": "T2"}), at=octubre(6, 9, 30))
    assert estado_de(conn, tarea) == "en_revision"
    d.ciclo(octubre(6, 10))
    [omitido] = _de_tipos(conn, RECORDATORIO)
    assert omitido["estado"] == "omitido" and omitido["motivo_omision"] == "ya_decidio"
    for dia in (7, 8, 9):
        assert _de(d.ciclo(octubre(dia, 10)), RECORDATORIO) == []
    assert _de_tipos(conn, TRABADA) == []
