"""No interrumpir una conversación (`leda.motor.no_interrumpir`; decisión 13 del usuario,
2026-10-08; conversación 26, con sus variantes).

Hallazgo de la prueba por Telegram real del 2026-10-08: el aviso de que una tarea vencía en 3 días
salió justo después de una respuesta de Leda, en medio de la conversación, repitiendo lo que se
estaba hablando. La regla, para todos los avisos que Leda manda por su cuenta:

1. mientras la persona conversa (escribió o tocó algo hace menos de 30 minutos, o los del espacio),
   no le llega ningún aviso: espera, y cada mensaje vuelve a contar;
2. con una pregunta de Leda sin contestar, ningún aviso sale junto con ella: la pregunta misma,
   cuando la escalera la repite, sale sola;
3. el de otra tarea que no pide respuesta sale aparte; el que pide respuesta espera a que se
   cierre la pregunta;
4. nunca fuera del horario: si la espera cruza el cierre, sale el día hábil siguiente a la hora
   en que Leda escribe por su cuenta;
5. al salir se relee y lo ya hablado no se repite;
6. vale también para los avisos de coordinación, y sólo para la persona que conversa.

El reloj es el de `test_escalera.py`: "Revisar el tablero" (T1) vence el viernes 9 de octubre de
2026, con el aviso previo tres días hábiles antes (el martes 6, a las 10:00).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from leda.db import admin, espacio
from leda.motor import preguntas
from leda.motor.avisos import TIPOS
from leda.motor.escalera import correr_escalera
from leda.motor.ia import IAGuionada, Jugada
from leda.motor.no_interrumpir import (CLAVE, ESPERA_POR_OMISION, YA_SE_HABLO,
                                       espera_sin_interrumpir)
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import procesar_toque, procesar_turno

from tests.motor.ayudantes import (IAQueRedacta, avisos_guardados, contexto, dice, enviar,
                                   jugada_prevision, nueva_tarea, octubre, solicitante, todos)

VIERNES_9 = datetime(2026, 10, 9, 20, 0, tzinfo=timezone.utc)


@pytest.fixture
def dos(conn, mundo, espacio_con_escalera) -> dict[str, str]:
    """Las dos tareas de Marcos: T1 vence el viernes 9 y T2 el viernes 16."""
    return {"T1": mundo["tarea"], "T2": nueva_tarea(conn, mundo, "Probar las comunicaciones")}


@pytest.fixture
def dos_del_viernes_9(conn, mundo, espacio_con_escalera) -> dict[str, str]:
    """Las dos tareas de Marcos vencen el viernes 9: el aviso previo de las dos, el martes 6."""
    return {"T1": mundo["tarea"],
            "T2": nueva_tarea(conn, mundo, "Probar las comunicaciones", fecha=VIERNES_9)}


def _escalera(conn, mundo, at: datetime) -> None:
    correr_escalera(conn, mundo["id"], RelojFijo(at))
    conn.commit()


def _hola(conn, escribe, at: datetime, nombre: str = "Marcos") -> None:
    """Un mensaje sin jugadas: la persona escribe y no habla de ninguna tarea."""
    quien, entrante = escribe(nombre, "hola", at=at)
    r = procesar_turno(conn, quien, entrante, IAGuionada(jugadas=[[]], redacciones=["Hola."]),
                       RelojFijo(at))
    conn.commit()
    assert r.error is None


def _estados(conn, tipo: str) -> list[tuple[str, str | None]]:
    return [(a["estado"], a["motivo_omision"]) for a in avisos_guardados(conn, tipo)]


def _configurar(conn, mundo, valor: str) -> None:
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, %s, %s)""", (mundo["id"], CLAVE, valor))
    conn.commit()


def _abrir(conn, mundo, tipo: str, task_id: str, at: datetime) -> str:
    """Una pregunta de Leda a Marcos sobre esa tarea, abierta (como la deja un turno)."""
    with espacio(conn, mundo["id"]) as cur:
        ctx = contexto(cur, mundo, ahora=at)
        _, pregunta = preguntas.abrir_con_id(ctx, tipo, task_id, jugada={"nombre": "prueba"})
    conn.commit()
    return pregunta


def _cerrar(conn, mundo, pregunta: str, at: datetime) -> None:
    with espacio(conn, mundo["id"]) as cur:
        preguntas.cerrar(contexto(cur, mundo, ahora=at), pregunta, "respondida", {})
    conn.commit()


# --- Cuánto espera -----------------------------------------------------------------------------

def _espera(conn, mundo) -> timedelta:
    with espacio(conn, mundo["id"]) as cur:
        espera = espera_sin_interrumpir(cur, mundo["id"])
    conn.commit()
    return espera


def test_sin_configurar_espera_treinta_minutos(conn, mundo):
    assert ESPERA_POR_OMISION == timedelta(minutes=30)
    assert _espera(conn, mundo) == timedelta(minutes=30)


@pytest.mark.parametrize("valor, minutos", [("5", 5), ("0", 0), ("45", 45)])
def test_el_espacio_cambia_cuanto_espera(conn, mundo, valor, minutos):
    _configurar(conn, mundo, valor)
    assert _espera(conn, mundo) == timedelta(minutes=minutos)


@pytest.mark.parametrize("valor", ['"treinta"', "-5", "true", "null"])
def test_un_valor_que_no_vale_usa_el_del_producto(conn, mundo, valor):
    _configurar(conn, mundo, valor)
    assert _espera(conn, mundo) == ESPERA_POR_OMISION


# --- 1. Mientras la persona conversa, el aviso espera ---------------------------------------

def test_mientras_la_persona_conversa_el_aviso_espera(conn, mundo, escribe, dos_del_viernes_9):
    _escalera(conn, mundo, octubre(6, 9))           # guarda los dos avisos previos, para las 10
    _hola(conn, escribe, octubre(6, 9, 56))
    ia = IAQueRedacta()
    assert enviar(conn, mundo, ia, octubre(6, 10)) == {"en_espera": 2}
    assert enviar(conn, mundo, ia, octubre(6, 10, 25)) == {"en_espera": 2}
    assert ia.pedidos_de_redaccion == []
    assert enviar(conn, mundo, ia, octubre(6, 10, 26)) == {"enviado": 2}
    [pedido] = ia.pedidos_de_redaccion              # juntos, en un envío (mecánica §10)
    assert len(pedido["hechos"]) == 2


def test_cada_mensaje_vuelve_a_contar_la_espera(conn, mundo, escribe, dos_del_viernes_9):
    _escalera(conn, mundo, octubre(6, 9))
    _hola(conn, escribe, octubre(6, 9, 56))
    _hola(conn, escribe, octubre(6, 10, 20))
    ia = IAQueRedacta()
    assert enviar(conn, mundo, ia, octubre(6, 10, 30)) == {"en_espera": 2}
    assert enviar(conn, mundo, ia, octubre(6, 10, 50)) == {"enviado": 2}


def test_un_toque_tambien_es_conversar(conn, mundo, duda, espacio_con_escalera):
    """Marcos toca una opción de la duda del lunes (la de "Probar las comunicaciones", que no
    tiene aviso previo esta semana): el aviso previo de "Revisar el tablero" espera."""
    _escalera(conn, mundo, octubre(6, 9))
    r = procesar_toque(conn, solicitante(conn, mundo), duda["O2"],
                       mundo["personas"]["Marcos"]["telegram"],
                       IAGuionada(redacciones=["Listo."]), RelojFijo(octubre(6, 9, 58)))
    conn.commit()
    assert r is not None and r.error is None
    assert enviar(conn, mundo, IAQueRedacta(), octubre(6, 10, 10)) == {"en_espera": 1}
    assert enviar(conn, mundo, IAQueRedacta(), octubre(6, 10, 28)) == {"enviado": 1}


def test_el_espacio_que_no_espera_manda_a_su_hora(conn, mundo, escribe, dos_del_viernes_9):
    _configurar(conn, mundo, "0")
    _escalera(conn, mundo, octubre(6, 9))
    _hola(conn, escribe, octubre(6, 9, 59))
    assert enviar(conn, mundo, IAQueRedacta(), octubre(6, 10)) == {"enviado": 2}


def test_el_aviso_a_otra_persona_no_espera_por_la_que_conversa(conn, mundo, escribe, dos):
    """Ismael no está conversando aunque Marcos sí (regla, punto 6)."""
    dice(conn, escribe, jugada_prevision("T2", "2026-10-15", "el proveedor"),
         at=octubre(6, 9, 56))
    ia = IAQueRedacta()
    assert enviar(conn, mundo, ia, octubre(6, 10, 6)) == {"enviado": 1}
    [pedido] = ia.pedidos_de_redaccion
    assert pedido["persona"] == "Ismael"


def test_tambien_espera_un_aviso_de_coordinacion(conn, mundo, escribe, dos):
    """El aviso de una previsión a Ismael espera si Ismael está conversando."""
    _hola(conn, escribe, octubre(6, 10), nombre="Ismael")
    dice(conn, escribe, jugada_prevision("T2", "2026-10-15", "el proveedor"),
         at=octubre(6, 10, 1))
    ia = IAQueRedacta()
    assert enviar(conn, mundo, ia, octubre(6, 10, 11)) == {"en_espera": 1}
    assert enviar(conn, mundo, ia, octubre(6, 10, 30)) == {"enviado": 1}


# --- 4. Nunca fuera del horario --------------------------------------------------------------

def test_si_la_espera_cruza_el_cierre_sale_el_dia_habil_siguiente(conn, mundo, escribe,
                                                                  dos_del_viernes_9):
    """Variante 3: Marcos conversa hasta las 16:50; el aviso no sale a las 17:20, fuera del
    horario, sino el miércoles a la hora en que Leda escribe por su cuenta, releído ese día."""
    _escalera(conn, mundo, octubre(6, 9))
    _hola(conn, escribe, octubre(6, 16, 50))
    ia = IAQueRedacta()
    assert enviar(conn, mundo, ia, octubre(6, 16, 59)) == {"en_espera": 2}
    assert enviar(conn, mundo, ia, octubre(6, 17, 20)) == {"fuera_de_horario": 1}
    assert enviar(conn, mundo, ia, octubre(7, 9, 5)) == {"en_espera": 2}
    assert enviar(conn, mundo, ia, octubre(7, 10)) == {"enviado": 2}
    [pedido] = ia.pedidos_de_redaccion
    assert {h["dias_habiles_hasta_el_vencimiento"] for h in pedido["hechos"]} == {2}


# --- 2 y 3. Con una pregunta sin contestar ------------------------------------------------------

def test_con_una_pregunta_abierta_el_de_otra_tarea_sale_aparte_sin_pregunta(
        conn, mundo, escribe, dos_del_viernes_9):
    """Variante 1: la pregunta de una tarea sigue abierta; el aviso de la otra, que no pide
    respuesta, sale en su propio mensaje, sin repetirla ni abrir otra."""
    _escalera(conn, mundo, octubre(6, 9))
    pregunta = _abrir(conn, mundo, preguntas.PROPUESTA, dos_del_viernes_9["T2"], octubre(5, 15))
    ia = IAQueRedacta()
    assert enviar(conn, mundo, ia, octubre(6, 10)) == {"enviado": 1, "en_espera": 1}
    [pedido] = ia.pedidos_de_redaccion
    assert [h["tarea"] for h in pedido["hechos"]] == ["Revisar el tablero"]
    assert pedido["pregunta"] is None
    assert str(preguntas_abierta(conn)) == pregunta
    # La de la misma tarea que la pregunta espera a que se cierre (lo único que le llega de ese
    # tema es la pregunta), y entonces sale, releída.
    _cerrar(conn, mundo, pregunta, octubre(6, 11))
    assert enviar(conn, mundo, ia, octubre(6, 11, 1)) == {"enviado": 1}
    assert [h["tarea"] for h in ia.pedidos_de_redaccion[-1]["hechos"]] == [
        "Probar las comunicaciones"]


def preguntas_abierta(conn) -> str | None:
    fila = todos(conn, """select q.id from conversation_state s
                            join conversation_question q on q.id = s.pregunta_abierta_id
                           where q.cerrada_en is null""")
    return str(fila[0]["id"]) if fila else None


def test_un_aviso_que_pide_respuesta_espera_a_que_se_cierre_la_pregunta(conn, mundo, escribe,
                                                                         dos):
    """Variante 2: con la pregunta del motivo de T2 abierta, el pedido de estado de T1 no sale;
    sale cuando Marcos contesta y pasan los 30 minutos, con los datos de ese momento."""
    dice(conn, escribe, jugada_prevision("T2", "2026-10-20"), at=octubre(9, 9, 40))
    assert preguntas_abierta(conn) is not None
    _escalera(conn, mundo, octubre(9, 10))          # el pedido de estado de T1, el día que vence
    ia = IAQueRedacta()
    resumen = enviar(conn, mundo, ia, octubre(9, 10, 15))
    assert resumen.get("en_espera") == 1 and not resumen.get("enviado")
    assert _estados(conn, "pedido_de_estado") == [("guardado", None)]
    dice(conn, escribe, jugada_prevision("T2", "2026-10-20", "falta el switch"),
         at=octubre(9, 10, 20))
    assert preguntas_abierta(conn) is None
    assert enviar(conn, mundo, ia, octubre(9, 10, 45)).get("en_espera") == 1
    assert enviar(conn, mundo, ia, octubre(9, 10, 50)).get("enviado") == 1
    pedido = next(p for p in ia.pedidos_de_redaccion if p["persona"] == "Marcos")
    assert pedido["pregunta"]["tipo"] == preguntas.ESTADO_DE_LA_TAREA
    assert [h["tarea"] for h in pedido["hechos"]] == ["Revisar el tablero"]


def test_la_pregunta_abierta_cuando_la_repite_la_escalera_sale_sola(conn, mundo, escribe, dos):
    """Variante 1, paso 3: la repregunta del motivo sale en su propio mensaje; el aviso previo
    de la otra tarea, del mismo momento, sale aparte."""
    dice(conn, escribe, jugada_prevision("T2", "2026-10-20"), at=octubre(5, 11))
    abierta = preguntas_abierta(conn)
    enviar(conn, mundo, IAQueRedacta(), octubre(5, 16, 30))     # el aviso a Ismael, sin motivo
    _escalera(conn, mundo, octubre(6, 10))          # la repregunta del motivo y el aviso previo
    assert {a["tipo"] for a in avisos_guardados(conn) if a["estado"] == "guardado"} == {
        "repregunta", "aviso_previo"}
    ia = IAQueRedacta()
    assert enviar(conn, mundo, ia, octubre(6, 10)) == {"enviado": 2}
    assert len(ia.pedidos_de_redaccion) == 2
    repregunta = next(p for p in ia.pedidos_de_redaccion if p["pregunta"] is not None)
    otro = next(p for p in ia.pedidos_de_redaccion if p["pregunta"] is None)
    assert [h["tarea"] for h in repregunta["hechos"]] == ["Probar las comunicaciones"]
    assert repregunta["pregunta"]["tipo"] == preguntas.MOTIVO_DEL_ATRASO
    assert [h["tarea"] for h in otro["hechos"]] == ["Revisar el tablero"]
    assert preguntas_abierta(conn) == abierta
    salidas = todos(conn, "select id from message_outbox where not es_respuesta and chat_id = %s",
                    mundo["personas"]["Marcos"]["telegram"])
    assert len(salidas) >= 2


# --- 5. Lo ya hablado no se repite ----------------------------------------------------------

def test_lo_ya_hablado_de_una_tarea_no_se_repite(conn, mundo, escribe, dos_del_viernes_9):
    _escalera(conn, mundo, octubre(6, 9))
    r = dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T2"}), at=octubre(6, 9, 50))
    hablada = r.hechos[0]["tarea"]["titulo"]
    [otra] = {"Revisar el tablero", "Probar las comunicaciones"} - {hablada}
    ia = IAQueRedacta()
    assert enviar(conn, mundo, ia, octubre(6, 10, 20)) == {"enviado": 1, "omitido": 1}
    [pedido] = ia.pedidos_de_redaccion
    assert [h["tarea"] for h in pedido["hechos"]] == [otra]
    [omitido] = [a for a in avisos_guardados(conn, "aviso_previo") if a["estado"] == "omitido"]
    assert omitido["motivo_omision"] == YA_SE_HABLO
    assert omitido["hechos"]["tarea"] == hablada


def test_lo_hablado_antes_de_que_se_guardara_no_cuenta(conn, mundo, escribe, dos_del_viernes_9):
    dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T2"}), at=octubre(6, 8, 20))
    _escalera(conn, mundo, octubre(6, 9))
    assert enviar(conn, mundo, IAQueRedacta(), octubre(6, 10)) == {"enviado": 2}


def test_lo_ya_hablado_omite_solo_lo_que_no_trae_nada_nuevo():
    """Lo omiten sólo los recordatorios de la propia tarea que no piden nada: los que traen el
    acto de otra persona o piden algo esperan y salen releídos (`PENDIENTE` del usuario)."""
    omiten = {n for n, t in TIPOS.items() if t.se_omite_si_ya_se_hablo}
    assert omiten == {"aviso_previo", "vencimiento_con_prevision"}


def test_el_motivo_de_la_omision_tiene_su_significado():
    from leda.motor.hechos import significado

    assert significado(YA_SE_HABLO) is not None


# --- Lo que se le cuenta a otra persona: cuándo se entera de verdad ---------------------------

def test_cuando_se_entera_otra_persona_cuenta_la_espera_de_su_conversacion(conn, mundo, escribe,
                                                                           dos):
    """Los hechos dicen cuándo se entera de verdad quien recibe el aviso (constitución §4; como
    con el margen para corregir, `margen.py`): si está conversando, cuando termine su espera."""
    _hola(conn, escribe, octubre(6, 10), nombre="Ismael")
    r = dice(conn, escribe, jugada_prevision("T2", "2026-10-15", "el proveedor"),
             at=octubre(6, 10, 1))
    llega = r.hechos[0]["aviso_al_referente"]["llega"]
    assert datetime.fromisoformat(llega) == octubre(6, 10, 30)


def test_sin_conversacion_los_hechos_dicen_la_hora_del_aviso(conn, mundo, escribe, dos):
    r = dice(conn, escribe, jugada_prevision("T2", "2026-10-15", "el proveedor"),
             at=octubre(6, 10, 1))
    llega = r.hechos[0]["aviso_al_referente"]["llega"]
    assert datetime.fromisoformat(llega) == octubre(6, 10, 11)
