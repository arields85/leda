"""La escalera del motor (E2-5).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Escalera"); mecánica §9 (anclada al
vencimiento V, en días hábiles del espacio, comprimida para una tarea corta, privada hasta el
escalamiento; un bloqueo la detiene; una ausencia la pausa y la vuelta lleva un reencuadre);
ADR 0018, decisión 9b (un solo aviso previo N días hábiles antes, sin pedir respuesta; desde V
cada recordatorio pide el estado y abre una espera; sin respuesta, V+1, V+2 avisando que va a
escalar y V+3 por la ruta `falta_persistente_de_respuesta`); ADR 0017, decisión 6
(`pending_reply`); conversaciones 01, 02 y 04.

El reloj se mueve por días: la tarea "Revisar el tablero" de Marcos vence el viernes 9 de
octubre de 2026; el sábado 10 y el domingo 11 no son hábiles y el lunes 12 es feriado. Cada
"ciclo" corre la escalera y manda los avisos guardados, como lo hará el ciclo de la E2-6. La IA
es guionada: redacta siempre y guarda lo que recibió.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import pytest

from prueba_chica.avisos import enviar_avisos
from prueba_chica.escalera import ETAPA_ESCALERA, correr_escalera
from prueba_chica.ia import Jugada
from prueba_chica.test_avisos import _dice, _hora
from prueba_chica.test_situaciones import _cuantas, _tarea, _todos, _uno
from prueba_chica.tiempo import RelojFijo

from leda.db import admin


@dataclass
class IAQueRedacta:
    nombre: str = "guionada"
    pedidos_de_redaccion: list[dict[str, Any]] = field(default_factory=list)

    def redactar(self, pedido: dict[str, Any]) -> str:
        self.pedidos_de_redaccion.append(pedido)
        return f"Aviso {len(self.pedidos_de_redaccion)}."

    def elegir_jugadas(self, situacion):     # la escalera nunca elige jugadas
        raise AssertionError("La escalera no le pide jugadas a la IA.")


@pytest.fixture
def espacio_con_escalera(conn, mundo) -> dict:
    """CoreWork en chico: aviso previo a 3 días hábiles, el feriado del lunes 12 y la falta de
    respuesta escalada a quien lidera (Ismael)."""
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, 'aviso_previo_dias_habiles', '3')""", (mundo["id"],))
        cur.execute("insert into holiday (workspace_id, fecha) values (%s, '2026-10-12')",
                    (mundo["id"],))
        cur.execute("""insert into escalation_route (workspace_id, disparador, destino_rol_id)
                       select %s, 'falta_persistente_de_respuesta', id from rol
                        where workspace_id = %s and slug = 'lider'""",
                    (mundo["id"], mundo["id"]))
    conn.commit()
    return mundo


class Dias:
    """Los ciclos de la escalera, día por día, con la IA que redacta."""

    def __init__(self, conn, mundo) -> None:
        self.conn, self.mundo = conn, mundo
        self.ia = IAQueRedacta()

    def ciclo(self, at: datetime) -> list[dict[str, Any]]:
        """Corre la escalera y manda lo guardado; devuelve lo que se redactó en este ciclo."""
        antes = len(self.ia.pedidos_de_redaccion)
        correr_escalera(self.conn, self.mundo["id"], RelojFijo(at))
        self.conn.commit()
        enviar_avisos(self.conn, self.mundo["id"], self.ia, RelojFijo(at))
        self.conn.commit()
        return self.ia.pedidos_de_redaccion[antes:]


@pytest.fixture
def dias(conn, espacio_con_escalera) -> Dias:
    return Dias(conn, espacio_con_escalera)


def _avisos(conn, tipo: str | None = None) -> list[dict]:
    return _todos(conn, """select * from scheduled_notice
                            where %s::text is null or tipo = %s
                            order by creado_en, dedupe_key""", tipo, tipo)


def _espera(conn) -> dict | None:
    return _uno(conn, "select * from pending_reply where tipo = 'estado_de_la_tarea'")


def _para(conn, mundo, nombre: str) -> list[str]:
    """Lo que salió por cuenta de Leda para esa persona, en orden."""
    return [f["cuerpo"] for f in _todos(
        conn, """select cuerpo from message_outbox
                  where not es_respuesta and chat_id = %s order by programado_para, cuerpo""",
        mundo["personas"][nombre]["telegram"])]


# --- El aviso previo (9b; conversaciones 01 y 04) -----------------------------------------------

def test_el_aviso_previo_sale_una_sola_vez_n_dias_habiles_antes(conn, mundo, dias):
    assert dias.ciclo(_hora(5, 10)) == []          # faltan 4 días hábiles

    [pedido] = dias.ciclo(_hora(6, 10))            # faltan 3

    assert pedido["persona"] == "Marcos" and pedido["pregunta"] is None
    assert pedido["hechos"] == [{"aviso": "vencimiento_proximo", "necesita_respuesta": False,
                                 "tarea": "Revisar el tablero", "vence": "2026-10-09",
                                 "dias_habiles_hasta_el_vencimiento": 3}]
    [aviso] = _avisos(conn)
    assert aviso["tipo"] == "aviso_previo" and aviso["estado"] == "enviado"
    assert _uno(conn, "select tipo from message_outbox")["tipo"] == "informativo"
    assert _espera(conn) is None                   # no pide respuesta
    assert _cuantas(conn, "conversation_question") == 0
    for dia in (7, 8):                             # uno solo (conversación 01, paso 3)
        assert dias.ciclo(_hora(dia, 10)) == []
    assert _cuantas(conn, "scheduled_notice") == 1


def test_una_tarea_corta_comprime_el_aviso_previo(conn, mundo, dias):
    """Una tarea con menos días hábiles por delante que el aviso previo lo recibe enseguida
    (mecánica §9: la escalera se comprime, nunca saltea un paso)."""
    [pedido] = dias.ciclo(_hora(8, 10))           # vence mañana

    assert pedido["hechos"][0]["dias_habiles_hasta_el_vencimiento"] == 1
    assert dias.ciclo(_hora(8, 15)) == []


def test_correr_la_escalera_dos_veces_no_hace_nada_nuevo(conn, mundo, dias):
    for _ in range(2):
        correr_escalera(conn, mundo["id"], RelojFijo(_hora(6, 10)))
        conn.commit()
    assert _cuantas(conn, "scheduled_notice") == 1
    dias.ciclo(_hora(6, 10))
    dias.ciclo(_hora(9, 10))
    dias.ciclo(_hora(9, 10))
    assert _cuantas(conn, "scheduled_notice") == 2
    assert _cuantas(conn, "message_outbox") == 2
    assert _cuantas(conn, "pending_reply") == 1


# --- Sin respuesta: de V al escalamiento (conversación 04) ------------------------------------

def test_sin_respuesta_la_escalera_avanza_un_dia_habil_por_paso_y_escala(conn, mundo, dias):
    ismael, marcos = mundo["personas"]["Ismael"], mundo["personas"]["Marcos"]
    dias.ciclo(_hora(6, 10))                       # el aviso previo

    [v] = dias.ciclo(_hora(9, 10))

    assert v["hechos"] == [{"aviso": "pedido_de_estado", "numero": 1,
                            "necesita_respuesta": True, "tarea": "Revisar el tablero",
                            "vence": "2026-10-09", "atraso_dias_habiles": 0,
                            "estado": "asignada"}]
    assert v["pregunta"] == {"tipo": "estado_de_la_tarea",
                             "tarea": {"titulo": "Revisar el tablero"}, "desde_antes": False}
    espera = _espera(conn)
    assert str(espera["membership_id"]) == marcos["membership_id"]
    assert str(espera["task_id"]) == mundo["tarea"]
    assert espera["satisfecho_en"] is None and espera["recordatorios"] == 1
    pregunta = _uno(conn, """select q.tipo, q.se_puede_dejar from conversation_state s
                              join conversation_question q on q.id = s.pregunta_abierta_id
                             where s.membership_id = %s""", marcos["membership_id"])
    assert pregunta == {"tipo": "estado_de_la_tarea", "se_puede_dejar": False}

    # Nada más el viernes, el fin de semana ni el feriado del lunes.
    for momento in (_hora(9, 15), _hora(10, 10), _hora(11, 10), _hora(12, 10)):
        assert dias.ciclo(momento) == []

    [v1] = dias.ciclo(_hora(13, 10))
    assert v1["hechos"][0]["numero"] == 2 and v1["hechos"][0]["atraso_dias_habiles"] == 1
    assert "si_no_hay_respuesta" not in v1["hechos"][0]
    [v2] = dias.ciclo(_hora(14, 10))
    assert v2["hechos"][0]["numero"] == 3
    assert v2["hechos"][0]["si_no_hay_respuesta"] == {"se_avisa_a": ["Ismael"],
                                                      "estado": "todavia_no"}
    assert _espera(conn)["recordatorios"] == 3

    [v3] = dias.ciclo(_hora(15, 10))

    assert v3["persona"] == "Ismael" and v3["pregunta"] is None
    assert v3["hechos"] == [{"aviso": "falta_de_respuesta", "necesita_respuesta": False,
                             "pedidos_de_estado_sin_respuesta": 3,
                             "pedido_desde": "2026-10-09", "tarea": "Revisar el tablero",
                             "vence": "2026-10-09", "atraso_dias_habiles": 3,
                             "estado": "asignada", "responsable": "Marcos"}]
    escalamiento = _uno(conn, "select * from message_outbox where chat_id = %s",
                        ismael["telegram"])
    assert escalamiento["tipo"] == "prioritario" and escalamiento["es_respuesta"] is False
    assert _espera(conn)["escalado_en"] == _hora(15, 10)
    assert dias.ciclo(_hora(16, 10)) == [] and dias.ciclo(_hora(19, 10)) == []
    assert len(_para(conn, mundo, "Marcos")) == 4 and len(_para(conn, mundo, "Ismael")) == 1


def test_los_recordatorios_dicen_la_prevision_y_lo_que_depende(conn, mundo, dias, escribe):
    """Conversación 02, paso 4: el recordatorio sigue contra la fecha comprometida y dice que
    Marcos ya dio una previsión y que Ismael está al tanto; lo que depende, como impacto."""
    otra = _tarea(conn, mundo, "Probar las comunicaciones")
    with admin(conn) as cur:
        cur.execute("""insert into dependency (workspace_id, origen_task_id, destino_task_id)
                       values (%s, %s, %s)""", (mundo["id"], mundo["tarea"], otra))
    conn.commit()
    _dice(conn, escribe, Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-14",
                                                     "motivo": "el proveedor"}),
          at=_hora(6, 15))
    dias.ciclo(_hora(6, 15, 30))           # el aviso a Ismael (y el aviso previo)

    [v] = [p for p in dias.ciclo(_hora(9, 10)) if p["persona"] == "Marcos"]

    hechos = v["hechos"][0]
    assert hechos["prevision_vigente"] == {
        "fecha": "2026-10-14", "motivo": "el proveedor", "atraso_dias_habiles": 2,
        "aviso_al_referente": {"a": "Ismael", "estado": "enviado"}}
    assert hechos["dependientes"] == [{"tarea": "Probar las comunicaciones",
                                       "no_puede_arrancar_hasta_que_termine": True}]


# --- Una respuesta detiene la escalera (9b) -----------------------------------------------------

@pytest.mark.parametrize("jugada", [
    Jugada("anotar_inicio", {"tarea": "T1"}),
    # Una previsión lleva la escalera a su fecha (9i, `test_ancla.py`): una posterior a los días
    # que mira esta prueba.
    Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-20"}),
    Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "falta el repuesto"}),
], ids=lambda j: j.nombre)
def test_una_respuesta_cierra_la_espera_y_la_pregunta_y_detiene_la_escalera(conn, mundo, dias,
                                                                            escribe, jugada):
    dias.ciclo(_hora(9, 10))

    _dice(conn, escribe, jugada, at=_hora(9, 11))

    assert _espera(conn)["satisfecho_en"] == _hora(9, 11)
    pregunta = _uno(conn, """select cierre from conversation_question
                              where tipo = 'estado_de_la_tarea'""")
    assert pregunta["cierre"] == "respondida"
    for dia in (13, 14, 15, 16):
        dias.ciclo(_hora(dia, 10))
    assert _cuantas(conn, "scheduled_notice", "tipo in ('pedido_de_estado', 'escalamiento')") \
        == 1
    assert _para(conn, mundo, "Ismael") in ([], ["Aviso 2."])    # sólo el de la previsión


def test_un_pedido_guardado_que_ya_se_contesto_no_sale(conn, mundo, dias, escribe):
    """Guardado antes del horario; la persona escribe antes de que salga: se omite con su
    motivo, nunca en silencio, y la escalera queda detenida."""
    correr_escalera(conn, mundo["id"], RelojFijo(_hora(9, 7)))
    conn.commit()
    [pedido] = _avisos(conn, "pedido_de_estado")
    assert pedido["programado_para"] == _hora(9, 9)
    _dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=_hora(9, 8, 30))

    assert dias.ciclo(_hora(9, 9)) == []

    [pedido] = _avisos(conn, "pedido_de_estado")
    assert (pedido["estado"], pedido["motivo_omision"]) == ("omitido", "ya_respondio")
    assert dias.ciclo(_hora(13, 10)) == []


# --- Un bloqueo abierto detiene la escalera (mecánica §9) ------------------------------------

def test_un_bloqueo_abierto_detiene_la_escalera(conn, mundo, dias, escribe):
    _dice(conn, escribe, Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "falta el PLC"}),
          at=_hora(5, 11))

    for dia in (6, 9, 13, 14, 15):
        assert dias.ciclo(_hora(dia, 10)) == []
    assert _cuantas(conn, "scheduled_notice") == 0 and _espera(conn) is None


def test_un_aviso_guardado_de_una_tarea_que_se_bloqueo_se_omite(conn, mundo, dias, escribe):
    correr_escalera(conn, mundo["id"], RelojFijo(_hora(9, 7)))
    conn.commit()
    _dice(conn, escribe, Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "falta el PLC"}),
          at=_hora(9, 8))
    # El bloqueo contestó la espera; aun sin eso, la tarea bloqueada no lleva el pedido.
    with admin(conn) as cur:
        cur.execute("update pending_reply set satisfecho_en = null")
    conn.commit()

    assert dias.ciclo(_hora(9, 9)) == []
    [pedido] = _avisos(conn, "pedido_de_estado")
    assert pedido["motivo_omision"] == "bloqueo_abierto"


# --- Horario (9e) ---------------------------------------------------------------------------------

def test_lo_que_la_escalera_guarda_fuera_del_horario_sale_al_empezar_la_jornada(conn, mundo, dias):
    assert dias.ciclo(_hora(9, 7)) == []
    assert _cuantas(conn, "message_outbox") == 0

    [v] = dias.ciclo(_hora(9, 9))
    assert v["hechos"][0]["aviso"] == "pedido_de_estado"


# --- Ausencias (mecánica §9) ------------------------------------------------------------------

def _ausente(conn, mundo, desde: str, hasta: str | None) -> None:
    with admin(conn) as cur:
        cur.execute("""insert into absence (workspace_id, membership_id, desde, hasta)
                       values (%s, %s, %s, %s)""",
                    (mundo["id"], mundo["personas"]["Marcos"]["membership_id"], desde, hasta))
    conn.commit()


def test_una_ausencia_pausa_la_escalera_y_la_vuelta_lleva_un_reencuadre(conn, mundo, dias):
    dias.ciclo(_hora(6, 10))                       # el aviso previo
    [v] = dias.ciclo(_hora(9, 10))                 # el primer pedido
    _ausente(conn, mundo, "2026-10-13", "2026-10-14")

    assert dias.ciclo(_hora(13, 10)) == [] and dias.ciclo(_hora(14, 10)) == []

    [vuelta] = dias.ciclo(_hora(15, 10))
    hechos = vuelta["hechos"][0]
    assert hechos["aviso"] == "vuelta_de_ausencia"
    assert hechos["ausencia"] == {"desde": "2026-10-13", "hasta": "2026-10-14"}
    assert hechos["necesita_respuesta"] is True and hechos["atraso_dias_habiles"] == 3
    assert vuelta["pregunta"]["tipo"] == "estado_de_la_tarea"
    assert _avisos(conn, "reencuadre")[0]["estado"] == "enviado"
    assert dias.ciclo(_hora(15, 15)) == []

    # Retoma desde donde quedó: el segundo pedido, no el escalamiento que le tocaba.
    [siguiente] = dias.ciclo(_hora(16, 10))
    assert siguiente["hechos"][0]["aviso"] == "pedido_de_estado"
    assert siguiente["hechos"][0]["numero"] == 2


def test_lo_guardado_para_alguien_que_se_ausenta_lo_reemplaza_el_reencuadre(conn, mundo, dias):
    correr_escalera(conn, mundo["id"], RelojFijo(_hora(9, 7)))     # el pedido, guardado
    conn.commit()
    _ausente(conn, mundo, "2026-10-09", "2026-10-13")

    assert dias.ciclo(_hora(9, 10)) == []
    [vuelta] = dias.ciclo(_hora(14, 10))

    assert vuelta["hechos"][0]["aviso"] == "vuelta_de_ausencia"
    [pedido] = _avisos(conn, "pedido_de_estado")
    assert (pedido["estado"], pedido["motivo_omision"]) == ("omitido",
                                                            "reemplazado_por_el_reencuadre")
    [primero] = dias.ciclo(_hora(15, 10))
    assert primero["hechos"][0]["numero"] == 1


def test_una_ausencia_antes_del_vencimiento_cambia_el_aviso_previo_por_el_reencuadre(conn, mundo,
                                                                                    dias):
    _ausente(conn, mundo, "2026-10-05", "2026-10-06")

    assert dias.ciclo(_hora(6, 10)) == []
    [vuelta] = dias.ciclo(_hora(7, 10))

    hechos = vuelta["hechos"][0]
    assert hechos["aviso"] == "vuelta_de_ausencia" and hechos["necesita_respuesta"] is False
    assert hechos["dias_habiles_hasta_el_vencimiento"] == 2 and vuelta["pregunta"] is None
    assert dias.ciclo(_hora(8, 10)) == []
    assert _avisos(conn, "aviso_previo") == []


def test_un_escalamiento_guardado_espera_si_el_responsable_se_ausenta(conn, mundo, dias):
    """Mecánica §9, ausencias: la escalera no avanza mientras la persona está ausente, tampoco
    su escalamiento, aunque vaya a otra persona. Uno ya guardado espera; a la vuelta lo
    reemplaza el reencuadre."""
    for dia in (9, 13, 14):                         # los tres pedidos, sin respuesta
        dias.ciclo(_hora(dia, 10))
    correr_escalera(conn, mundo["id"], RelojFijo(_hora(15, 9, 5)))   # el escalamiento, guardado
    conn.commit()
    [guardado] = _avisos(conn, "escalamiento")
    assert guardado["estado"] == "guardado"
    _ausente(conn, mundo, "2026-10-15", "2026-10-15")

    assert dias.ciclo(_hora(15, 10)) == []
    assert _para(conn, mundo, "Ismael") == []

    [vuelta] = dias.ciclo(_hora(16, 10))

    assert vuelta["persona"] == "Marcos"
    assert vuelta["hechos"][0]["aviso"] == "vuelta_de_ausencia"
    [escalamiento] = _avisos(conn, "escalamiento")
    assert (escalamiento["estado"], escalamiento["motivo_omision"]) == (
        "omitido", "reemplazado_por_el_reencuadre")
    assert _para(conn, mundo, "Ismael") == []


# --- Lo que falta configurar no queda en silencio -------------------------------------------

def test_sin_el_aviso_previo_configurado_usa_el_minimo_y_lo_registra(conn, mundo, dias):
    """El plan lo dejó `PENDIENTE`: sin `aviso_previo_dias_habiles`, el mínimo del núcleo (un
    día hábil, mecánica §9) y un incidente por cada aviso previo que salió con él."""
    with admin(conn) as cur:
        cur.execute("delete from workspace_setting where clave = 'aviso_previo_dias_habiles'")
    conn.commit()

    assert dias.ciclo(_hora(7, 10)) == []          # faltan 2 días hábiles
    [pedido] = dias.ciclo(_hora(8, 10))
    assert pedido["hechos"][0]["dias_habiles_hasta_el_vencimiento"] == 1
    dias.ciclo(_hora(8, 11))

    incidente = _uno(conn, "select * from incident")
    assert incidente["etapa"] == ETAPA_ESCALERA and incidente["severidad"] == "baja"
    assert "aviso_previo_dias_habiles" in incidente["resumen_sanitizado"]
    assert _cuantas(conn, "incident") == 1


# --- Un escalamiento termina la escalera de ese vencimiento (revisión de la E2-5) -------------

def _cambiar_el_vencimiento(conn, mundo, vence: datetime) -> None:
    """La fecha comprometida es inmutable en la base; la cambiará la plataforma (ADR 0017,
    decisión 4). La prueba la cambia como lo haría ella, con la guarda apagada un momento."""
    with conn.transaction(), conn.cursor() as cur:
        cur.execute("alter table task disable trigger trg_bloquear_estado_directo")
        cur.execute("update task set fecha_objetivo = %s where id = %s", (vence, mundo["tarea"]))
        cur.execute("alter table task enable trigger trg_bloquear_estado_directo")
    conn.commit()


def test_un_vencimiento_nuevo_empieza_su_propia_escalera_despues_de_escalar(conn, mundo, dias):
    """Mecánica §9: la escalera se ancla a su vencimiento y termina al escalar. Si la persona
    nunca contestó, la espera queda abierta y escalada; con un vencimiento nuevo la escalera
    empieza de cero, con su aviso previo, y no la frena el escalamiento del anterior."""
    for dia in (6, 9, 13, 14, 15):
        dias.ciclo(_hora(dia, 10))
    assert _espera(conn)["escalado_en"] == _hora(15, 10)
    assert dias.ciclo(_hora(16, 10)) == []                 # la del 9 terminó

    _cambiar_el_vencimiento(conn, mundo, datetime(2026, 10, 23, 20, 0, tzinfo=timezone.utc))

    [previo] = dias.ciclo(_hora(20, 10))                   # faltan 3 días hábiles
    assert previo["hechos"][0]["aviso"] == "vencimiento_proximo"
    assert previo["hechos"][0]["vence"] == "2026-10-23"
    [v] = dias.ciclo(_hora(23, 10))
    assert v["hechos"][0]["aviso"] == "pedido_de_estado" and v["hechos"][0]["numero"] == 1
    # La espera de esta escalera es nueva: la del vencimiento anterior quedó escalada.
    esperas = _todos(conn, """select escalado_en, recordatorios from pending_reply
                               where satisfecho_en is null order by preguntado_en""")
    assert esperas == [{"escalado_en": _hora(15, 10), "recordatorios": 3},
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
    correr_escalera(conn, mundo["id"], RelojFijo(_hora(9, 10)))
    conn.commit()
    for minuto in (0, 1, 3, 7, 15):
        enviar_avisos(conn, mundo["id"], dias.ia, RelojFijo(_hora(9, 10, minuto)))
        conn.commit()
    [pedido] = _avisos(conn, "pedido_de_estado")
    assert pedido["estado"] == "fallido"
    assert _uno(conn, "select etapa from incident")["etapa"] == "motor_aviso_guardado"

    [v1] = dias.ciclo(_hora(13, 10))

    assert v1["hechos"][0]["numero"] == 2
    assert v1["hechos"][0]["pedidos_anteriores_que_no_le_llegaron"] == 1
    assert v1["pregunta"]["tipo"] == "estado_de_la_tarea"
    dias.ciclo(_hora(14, 10))
    [v3] = dias.ciclo(_hora(15, 10))
    assert v3["persona"] == "Ismael"
    assert v3["hechos"][0]["pedidos_de_estado_sin_respuesta"] == 2
    assert v3["hechos"][0]["pedidos_de_estado_que_no_le_llegaron"] == 1
    assert v3["hechos"][0]["pedido_desde"] == "2026-10-13"


def test_un_pedido_omitido_porque_la_persona_contesto_si_detiene_la_escalera(conn, mundo, dias,
                                                                           escribe):
    """El primer pedido se omite porque Marcos contestó antes de que saliera: la escalera no
    vuelve a guardarlo ni abre otra espera."""
    correr_escalera(conn, mundo["id"], RelojFijo(_hora(9, 7)))
    conn.commit()
    _dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=_hora(9, 8))
    dias.ciclo(_hora(9, 9))

    for dia in (13, 14, 15):
        assert dias.ciclo(_hora(dia, 10)) == []
    assert _cuantas(conn, "pending_reply", "satisfecho_en is null") == 0


def test_sin_ruta_de_escalamiento_se_registra_y_no_se_repite(conn, mundo, dias):
    with admin(conn) as cur:
        cur.execute("delete from escalation_route")
    conn.commit()
    for dia in (9, 13, 14):
        dias.ciclo(_hora(dia, 10))
    assert "si_no_hay_respuesta" not in _avisos(conn, "pedido_de_estado")[-1]["hechos"]

    assert dias.ciclo(_hora(15, 10)) == []
    dias.ciclo(_hora(16, 10))

    assert _avisos(conn, "escalamiento") == []
    incidente = _uno(conn, "select * from incident")
    assert incidente["etapa"] == ETAPA_ESCALERA and incidente["severidad"] == "media"
    assert _cuantas(conn, "incident") == 1 and _espera(conn)["escalado_en"] == _hora(15, 10)


def test_la_escalera_de_un_vencimiento_nuevo_tambien_escala(conn, mundo, dias):
    """Revisión de la E2-6: la escalera nueva llega hasta su propio escalamiento, con su clave,
    aunque la del vencimiento anterior ya haya escalado a la misma persona."""
    for dia in (6, 9, 13, 14, 15):
        dias.ciclo(_hora(dia, 10))
    _cambiar_el_vencimiento(conn, mundo, datetime(2026, 10, 23, 20, 0, tzinfo=timezone.utc))
    for dia in (20, 23, 26, 27):
        dias.ciclo(_hora(dia, 10))

    [escalamiento] = dias.ciclo(_hora(28, 10))

    assert escalamiento["persona"] == "Ismael"
    assert escalamiento["hechos"][0]["vence"] == "2026-10-23"
    assert escalamiento["hechos"][0]["pedido_desde"] == "2026-10-23"
    claves = [a["dedupe_key"].split(":")[3] for a in _avisos(conn, "escalamiento")]
    assert claves == ["2026-10-09", "2026-10-23"]
    assert len(_para(conn, mundo, "Ismael")) == 2
    assert dias.ciclo(_hora(29, 10)) == []


def test_un_escalamiento_que_reemplazo_un_reencuadre_no_cuenta_como_escalado(conn, mundo, dias):
    """Revisión de `informar_avance`: el escalamiento quedó guardado y la persona estuvo ausente
    ese día (el ciclo no llegó a mandarlo). A la vuelta, el reencuadre lo reemplaza: no salió,
    así que la escalera no terminó, y si no hay respuesta, escala el día hábil siguiente."""
    for dia in (9, 13, 14):
        dias.ciclo(_hora(dia, 10))
    correr_escalera(conn, mundo["id"], RelojFijo(_hora(15, 7)))    # el escalamiento, guardado
    conn.commit()
    _ausente(conn, mundo, "2026-10-15", "2026-10-15")

    [vuelta] = dias.ciclo(_hora(16, 10))

    assert vuelta["persona"] == "Marcos"
    assert vuelta["hechos"][0]["aviso"] == "vuelta_de_ausencia"
    [reemplazado] = _avisos(conn, "escalamiento")
    assert (reemplazado["estado"], reemplazado["motivo_omision"]) == (
        "omitido", "reemplazado_por_el_reencuadre")

    [escalamiento] = dias.ciclo(_hora(19, 10))

    assert escalamiento["persona"] == "Ismael"
    assert escalamiento["hechos"][0]["aviso"] == "falta_de_respuesta"
    assert dias.ciclo(_hora(20, 10)) == []


def test_el_aviso_previo_no_se_repite_cuando_el_ancla_vuelve_al_vencimiento(conn, mundo, dias,
                                                                           escribe):
    """El aviso previo es de la fecha comprometida, no de un anclaje (revisión de la E2-7): si
    una previsión lleva el ancla a otra fecha y otra la devuelve al vencimiento, la escalera
    nueva del vencimiento no manda otro aviso previo."""
    from prueba_chica.test_ancla import _prevision

    [previo] = dias.ciclo(_hora(6, 10))
    assert previo["hechos"][0]["aviso"] == "vencimiento_proximo"
    _prevision(conn, escribe, "2026-10-15", at=_hora(6, 11))
    _prevision(conn, escribe, "2026-10-09", at=_hora(6, 12))

    for momento in (_hora(6, 13), _hora(7, 10), _hora(8, 10)):
        assert [p for p in dias.ciclo(momento) if p["persona"] == "Marcos"] == []
    assert len(_avisos(conn, "aviso_previo")) == 1
