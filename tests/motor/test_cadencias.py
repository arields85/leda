"""Los pedidos de estado con ritmo fijo (`leda.motor.cadencias`; C-6; decisión 8 del usuario,
2026-10-08, opción A; ADR 0017, decisión 3b, punto 5; mecánica §9, §10 y §12; conversación 37).

Con el ritmo del pack del espacio (`cadence_job`, a cada integrante en privado), Leda le pide a cada
persona el estado de sus tareas en un solo mensaje, con la lista; el recordatorio del día de esas
tareas va adentro y no sale aparte. Lo que contesta cuenta para la escalera de cada tarea; si contesta
sólo una, Leda la anota y pregunta una vez por las otras. Una vez por día de la cadencia: si su día pasó
sin que saliera, no sale tarde y queda registrado; un feriado tampoco.

Las decisiones 31, 32, 44 y 46 del usuario (2026-10-09; conversación 40): la lista trae todas las
tareas abiertas con su situación y pregunta sólo por las que se pueden mover (32); lo contestado no se
vuelve a preguntar mientras no cambie nada (31); después de "viene bien", lo próximo es el aviso previo
de siempre (44); la primera lista de la semana es completa y las otras traen sólo lo que cambió o no se
contestó, y si no hay nada no salen (46).
"""

from __future__ import annotations

from datetime import time

from leda.db import admin
from leda.motor import hechos as hechos_mod
from leda.motor import preguntas
from leda.motor.avisos import TIPOS
from leda.motor.cadencias import leer_ritmo
from leda.motor.escalera import ETAPA_ESCALERA
from leda.motor.ia import Jugada

from tests.motor.ayudantes import (abierta, avisos_guardados, cuantas, dice, estado_de,
                                   nueva_tarea, octubre, poner_estado, todos, uno)

LISTA = "como_vienen_sus_tareas"
LUNES = "15 9 * * 1"
MIERCOLES = "30 11 * * 3"
T1, T2, T3 = "Revisar el tablero", "Probar las comunicaciones", "Medir los sensores"


def _cadencia(conn, mundo, cron: str = LUNES, nombre: str = "objetivos_semanales",
              audiencia: str = "privado_cada_integrante") -> None:
    with admin(conn) as cur:
        cur.execute("""insert into cadence_job (workspace_id, nombre, cron, audiencia,
                                                plantilla_clave)
                       values (%s, %s, %s, %s, %s)""", (mundo["id"], nombre, cron, audiencia,
                                                        nombre))
    conn.commit()


def _listas(conn) -> list[dict]:
    return avisos_guardados(conn, LISTA)


def _para(dias, nombre: str = "Marcos") -> list[dict]:
    return [p for p in dias.ia.pedidos_de_redaccion if p["persona"] == nombre]


def _salieron_para(conn, mundo, nombre: str = "Marcos") -> list[dict]:
    return todos(conn, """select * from message_outbox where not es_respuesta and chat_id = %s
                           order by programado_para""", mundo["personas"][nombre]["telegram"])


def _titulos(lista) -> list[str]:
    return [t["tarea"] if isinstance(t["tarea"], str) else t["tarea"]["titulo"] for t in lista]


def _pregunta_la_lista(conn, mundo, dias, *tareas: str, at=None) -> None:
    """La lista del lunes 5 con las tareas de Marcos: la del mundo y las que se agregan."""
    _cadencia(conn, mundo)
    for titulo, vence in tareas:
        nueva_tarea(conn, mundo, titulo, fecha=vence)
    dias.ciclo(at or octubre(5, 10))


# --- Lo declarado -------------------------------------------------------------------------------

def test_el_aviso_y_la_pregunta_estan_declarados_con_su_significado():
    tipo = TIPOS[LISTA]
    assert tipo.tipo_de_mensaje == "seguimiento" and not tipo.es_coordinacion and tipo.lista
    assert preguntas.TIPOS[LISTA].se_puede_dejar
    for codigo in (LISTA, "sus_tareas", "vence_hoy", "de_la_lista", "ya_paso_su_momento",
                   "no_es_dia_habil", "sin_tareas_abiertas", "sin_respuesta_desde",
                   "solo_lo_que_cambio_o_falta", "sin_novedades_para_la_lista",
                   "antes_le_recuerda_que_vence"):
        assert hechos_mod.significado(codigo), codigo
    # Lo que la escalera tenía para ese día sobre una tarea de la lista va adentro.
    assert {n for n, t in TIPOS.items() if t.entra_en_la_lista} == {
        "aviso_previo", "vencimiento_con_prevision", "pedido_de_estado", "reencuadre",
        "repregunta_de_estado"}


def test_el_ritmo_de_una_cadencia_se_lee_de_su_cron():
    assert leer_ritmo("15 9 * * 1") == (time(9, 15), frozenset({0}))
    assert leer_ritmo("15 6 * * 1-6") == (time(6, 15), frozenset({0, 1, 2, 3, 4, 5}))
    assert leer_ritmo("0 11 * * 3,5") == (time(11, 0), frozenset({2, 4}))
    assert leer_ritmo("30 9 * * *") == (time(9, 30), frozenset(range(7)))
    assert leer_ritmo("0 7 * * 0") == (time(7, 0), frozenset({6}))     # domingo
    assert leer_ritmo("0 7 * * 7") == (time(7, 0), frozenset({6}))
    for roto in ("cada lunes", "15 25 * * 1", "15 9 1 * 1", "15 9 * * 8", ""):
        assert leer_ritmo(roto) is None, roto


# --- Un mensaje por persona, con la lista -------------------------------------------------------

def test_el_dia_de_la_cadencia_cada_persona_recibe_un_mensaje_con_la_lista(conn, mundo, dias):
    _pregunta_la_lista(conn, mundo, dias, (T2, octubre(16, 17)))

    [aviso] = _listas(conn)
    assert aviso["estado"] == "enviado"
    assert str(aviso["destinatario_membership_id"]) == mundo["personas"]["Marcos"]["membership_id"]
    [pedido] = _para(dias)
    [hechos] = pedido["hechos"]
    assert hechos["aviso"] == LISTA and hechos["necesita_respuesta"] is True
    assert _titulos(hechos["sus_tareas"]) == [T1, T2]
    assert [t["vence"] for t in hechos["sus_tareas"]] == ["2026-10-09", "2026-10-16"]
    # Una sola pregunta, por la lista entera.
    assert pedido["pregunta"]["tipo"] == LISTA
    assert _titulos([{"tarea": t} for t in pedido["pregunta"]["de_la_lista"]]) == [T1, T2]
    assert abierta(conn) == (LISTA, None)
    assert len(_salieron_para(conn, mundo)) == 1
    # A Ismael, que no tiene tareas, nada.
    assert _para(dias, "Ismael") == []


def test_el_recordatorio_del_dia_va_dentro_de_la_lista_y_no_sale_aparte(conn, mundo, dias):
    """El viernes 9 vence la tarea del mundo: su primer pedido de estado de la escalera va en la
    lista del viernes, como un renglón más ("vence hoy"), en el mismo mensaje."""
    _cadencia(conn, mundo, "0 9 * * 5")
    nueva_tarea(conn, mundo, T2, fecha=octubre(16, 17))

    dias.ciclo(octubre(9, 10))

    [salio] = _salieron_para(conn, mundo)
    [lista] = _listas(conn)
    [pedido_de_estado] = avisos_guardados(conn, "pedido_de_estado")
    assert lista["estado"] == pedido_de_estado["estado"] == "enviado"
    assert str(lista["outbox_id"]) == str(pedido_de_estado["outbox_id"]) == str(salio["id"])
    [pedido] = _para(dias)
    [hechos] = pedido["hechos"]
    del_dia, otra = hechos["sus_tareas"]
    assert _titulos([del_dia, otra]) == [T1, T2]
    assert del_dia["vence_hoy"] is True and del_dia["numero"] == 1
    assert "vence_hoy" not in otra
    # El recordatorio cuenta en su espera, sin abrir otra pregunta: la de la lista es la única.
    assert uno(conn, """select recordatorios from pending_reply
                         where tipo = 'estado_de_la_tarea'""")["recordatorios"] == 1
    assert abierta(conn) == (LISTA, None)
    assert cuantas(conn, "conversation_question", "cerrada_en is null") == 1


def test_una_cadencia_mas_tarde_retiene_el_recordatorio_del_dia_hasta_su_hora(conn, mundo, dias):
    _cadencia(conn, mundo, "30 11 * * 5")

    dias.ciclo(octubre(9, 10))
    assert _salieron_para(conn, mundo) == []
    [pedido_de_estado] = avisos_guardados(conn, "pedido_de_estado")
    assert pedido_de_estado["estado"] == "guardado"

    dias.ciclo(octubre(9, 11, 30))
    [salio] = _salieron_para(conn, mundo)
    [lista] = _listas(conn)
    [pedido_de_estado] = avisos_guardados(conn, "pedido_de_estado")
    assert str(lista["outbox_id"]) == str(pedido_de_estado["outbox_id"]) == str(salio["id"])


def test_una_vez_por_dia_de_la_cadencia(conn, mundo, dias):
    _pregunta_la_lista(conn, mundo, dias)
    dias.ciclo(octubre(5, 10, 5))
    dias.ciclo(octubre(6, 10))
    dias.ciclo(octubre(7, 10))

    assert len(_listas(conn)) == 1
    assert len([p for p in _para(dias) if p["hechos"][0]["aviso"] == LISTA]) == 1


def test_la_lista_trae_todas_las_abiertas_con_su_situacion_y_pregunta_por_las_que_se_mueven(
        conn, mundo, dias):
    """Decisión 32 del usuario (2026-10-09): también la trabada ("sigue trabada esperando el
    repuesto") y la entregada ("esperando revisión"), para que la persona vea todo junto y avise si
    algo cambió. La pregunta es sólo por las que se pueden mover; una cerrada no va."""
    _cadencia(conn, mundo)
    trabada = nueva_tarea(conn, mundo, T2, fecha=octubre(16, 17))
    entregada = nueva_tarea(conn, mundo, T3, fecha=octubre(16, 17))
    cerrada = nueva_tarea(conn, mundo, "Pintar la baranda", fecha=octubre(16, 17))
    poner_estado(conn, entregada, "en_revision")
    poner_estado(conn, cerrada, "cancelada")
    with admin(conn) as cur:
        cur.execute("""insert into blocker (workspace_id, task_id, causa)
                       values (%s, %s, 'falta el repuesto')""", (mundo["id"], trabada))
    conn.commit()

    dias.ciclo(octubre(5, 10))

    [pedido] = _para(dias)
    [hechos] = pedido["hechos"]
    t1, de_la_entregada, de_la_trabada = hechos["sus_tareas"]
    assert _titulos([t1, de_la_entregada, de_la_trabada]) == [T1, T3, T2]
    assert de_la_trabada["estado"] == "bloqueada"
    assert de_la_trabada["causas"] == ["falta el repuesto"]
    assert de_la_entregada["estado"] == "en_revision"
    assert hechos["necesita_respuesta"] is True
    assert [t["titulo"] for t in pedido["pregunta"]["de_la_lista"]] == [T1]
    lista = uno(conn, "select jugada from conversation_question where tipo = %s", LISTA)
    assert lista["jugada"]["tareas"] == [mundo["tarea"]]


def test_con_solo_tareas_trabadas_o_entregadas_la_lista_sale_sin_pregunta(conn, mundo, dias):
    """La persona ve igual todo lo suyo (decisión 32), pero no hay nada que preguntarle: la lista
    no pide respuesta ni queda como una pregunta abierta."""
    _cadencia(conn, mundo)
    poner_estado(conn, mundo["tarea"], "en_revision")

    dias.ciclo(octubre(5, 10))

    [pedido] = _para(dias)
    [hechos] = pedido["hechos"]
    assert _titulos(hechos["sus_tareas"]) == [T1]
    assert hechos["necesita_respuesta"] is False
    assert pedido["pregunta"] is None
    assert abierta(conn) is None


def test_sin_tareas_abiertas_no_sale_nada(conn, mundo, dias):
    _cadencia(conn, mundo)
    poner_estado(conn, mundo["tarea"], "cancelada")

    dias.ciclo(octubre(5, 10))

    assert _listas(conn) == []
    assert _para(dias) == []


# --- Cuando no sale -------------------------------------------------------------------------

def test_un_feriado_no_sale_y_queda_registrado(conn, mundo, dias):
    _cadencia(conn, mundo)

    dias.ciclo(octubre(12, 10))         # lunes 12, feriado del espacio

    [aviso] = _listas(conn)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "no_es_dia_habil")
    assert _salieron_para(conn, mundo) == []


def test_si_el_dia_de_la_cadencia_pasa_sin_que_salga_no_sale_tarde(conn, mundo, dias):
    """Mecánica §12: un mensaje de cadencia cuya ventana ya pasó no se envía tarde; se descarta y
    se registra la omisión. El ciclo corrió el viernes 2 y volvió recién el martes 6."""
    _cadencia(conn, mundo)
    dias.ciclo(octubre(2, 10))

    dias.ciclo(octubre(6, 10))

    [aviso] = _listas(conn)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "ya_paso_su_momento")
    assert [p for p in _para(dias) if p["hechos"][0]["aviso"] == LISTA] == []


def test_antes_de_la_primera_vuelta_no_se_repone_una_cadencia_vieja(conn, mundo, dias):
    _cadencia(conn, mundo)

    dias.ciclo(octubre(6, 10))          # la primera vuelta, un día después de la cadencia

    assert _listas(conn) == []


def test_una_persona_ausente_no_la_recibe_y_a_la_vuelta_ya_paso_su_momento(conn, mundo, dias):
    _cadencia(conn, mundo)
    with admin(conn) as cur:
        cur.execute("""insert into absence (workspace_id, membership_id, desde, hasta)
                       values (%s, %s, '2026-10-05', '2026-10-05')""",
                    (mundo["id"], mundo["personas"]["Marcos"]["membership_id"]))
    conn.commit()

    dias.ciclo(octubre(5, 10))
    [aviso] = _listas(conn)
    assert aviso["estado"] == "guardado"

    dias.ciclo(octubre(6, 10))
    [aviso] = _listas(conn)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "ya_paso_su_momento")


def test_un_ritmo_que_no_se_entiende_deja_un_incidente_por_dia_y_las_demas_siguen(
        conn, mundo, dias):
    _cadencia(conn, mundo, "cada lunes", nombre="rota")
    _cadencia(conn, mundo)

    dias.ciclo(octubre(5, 10))
    dias.ciclo(octubre(5, 10, 5))

    assert len(_listas(conn)) == 1
    [incidente] = todos(conn, "select * from incident where etapa = %s", ETAPA_ESCALERA)
    assert "rota" in incidente["resumen_sanitizado"]
    dias.ciclo(octubre(6, 10))
    assert cuantas(conn, "incident", "etapa = %s", ETAPA_ESCALERA) == 2


def test_una_cadencia_al_grupo_no_es_un_pedido_a_cada_persona(conn, mundo, dias):
    _cadencia(conn, mundo, nombre="resumen_grupal", audiencia="grupo")

    dias.ciclo(octubre(5, 10))

    assert _listas(conn) == []


# --- Lo que contesta la persona -----------------------------------------------------------------

def test_lo_que_contesta_de_cada_tarea_cuenta_y_la_lista_se_cierra(conn, mundo, escribe, dias):
    _pregunta_la_lista(conn, mundo, dias, (T2, octubre(30, 17)))

    r = dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}),
             Jugada("informar_avance", {"tarea": "T2", "palabras": "viene bien"}),
             at=octubre(5, 10, 30))

    assert r.pregunta is None
    assert estado_de(conn, mundo["tarea"]) == "en_curso"
    assert cuantas(conn, "audit_log", "accion = 'informar_avance'") == 1
    lista = uno(conn, "select * from conversation_question where tipo = %s", LISTA)
    assert lista["cierre"] == "respondida"
    assert abierta(conn) is None


def test_si_contesta_una_sola_pregunta_una_vez_por_las_otras(conn, mundo, escribe, dias):
    _pregunta_la_lista(conn, mundo, dias, (T2, octubre(16, 17)), (T3, octubre(16, 17)))

    r = dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(5, 10, 30))

    assert r.pregunta["tipo"] == LISTA
    assert [t["titulo"] for t in r.pregunta["de_la_lista"]] == [T3, T2]   # por su vencimiento
    assert abierta(conn) == (LISTA, None)

    r = dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T2"}), at=octubre(5, 11))

    assert r.pregunta is None
    lista = uno(conn, "select * from conversation_question where tipo = %s", LISTA)
    assert lista["cierre"] == "respondida"
    assert abierta(conn) is None


def test_hablar_de_otra_cosa_no_cuenta_como_contestar_la_lista(conn, mundo, escribe, dias):
    """Sin contestar ninguna, la lista es una pregunta abierta como cualquier otra: vuelve en la
    respuesta (9d) y no gasta la única vez que Leda pregunta por las otras."""
    _pregunta_la_lista(conn, mundo, dias, (T2, octubre(16, 17)))

    r = dice(conn, escribe, Jugada("consultar_pendientes", {}), at=octubre(5, 10, 30))

    assert r.pregunta["tipo"] == LISTA and r.pregunta["desde_antes"] is True
    r = dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(5, 11))
    assert r.pregunta["tipo"] == LISTA
    assert [t["titulo"] for t in r.pregunta["de_la_lista"]] == [T2]


def test_un_avance_de_una_tarea_que_no_vence_vuelve_en_la_proxima_lista(conn, mundo, escribe,
                                                                         dias):
    """Sin pedido de la escalera, "viene bien" se anota igual: Leda pidió el estado en la lista.
    T2 (vence el 30) vuelve en la próxima lista completa (el lunes 12 es feriado: el 19), antes
    que su vencimiento. T1 (vence el viernes 9): lo contestado cubre el día en que vence, porque
    no hay otra lista en el medio (decisión 31), así que Leda le pregunta el día hábil siguiente
    (el martes 13), si sigue sin entregar; antes, el martes 6, le llega el aviso previo de siempre
    (decisión 44). Nunca al día hábil siguiente de la respuesta."""
    _pregunta_la_lista(conn, mundo, dias, (T2, octubre(30, 17)))

    r = dice(conn, escribe, Jugada("informar_avance", {"tarea": "T2", "palabras": "viene bien"}),
             Jugada("informar_avance", {"tarea": "T1", "palabras": "bien tambien"}),
             at=octubre(5, 10, 30))

    de_t2, de_t1 = r.hechos[:2]
    assert de_t2["resultado"] == de_t1["resultado"] == "anotado"
    assert de_t2["vuelve_a_pedir_el_estado"]["llega"].startswith("2026-10-19T10:00")
    assert "antes_le_recuerda_que_vence" not in de_t2       # su aviso previo es el 27
    assert de_t1["vuelve_a_pedir_el_estado"]["llega"].startswith("2026-10-13T10:00")
    assert de_t1["antes_le_recuerda_que_vence"]["llega"].startswith("2026-10-06T10:00")
    assert avisos_guardados(conn, "repregunta_de_estado") == []
    assert cuantas(conn, "pending_reply") == 0


# --- Lo contestado no se vuelve a preguntar (decisión 31) --------------------------------------

def test_lo_contestado_en_la_lista_no_se_vuelve_a_preguntar_el_dia_que_vence(conn, mundo,
                                                                             escribe, dias):
    """Decisión 31 del usuario (2026-10-09): Marcos contó en la lista del lunes cómo viene T1, que
    vence el viernes 9. El martes le llega el aviso previo de siempre (no pide nada, decisión 44);
    el viernes, ningún "hoy vence"; el martes 13 (el lunes es feriado), ya atrasada y sin
    entregar, cambió: Leda le pide el estado."""
    _pregunta_la_lista(conn, mundo, dias)
    dice(conn, escribe, Jugada("informar_avance", {"tarea": "T1", "palabras": "viene bien"}),
         at=octubre(5, 10, 30))

    [previo] = [p for p in dias.ciclo(octubre(6, 10)) if p["persona"].startswith("Marcos")]
    assert previo["hechos"][0]["aviso"] == "vencimiento_proximo"
    assert dias.ciclo(octubre(9, 10)) == []
    assert avisos_guardados(conn, "pedido_de_estado") == []

    [pedido] = dias.ciclo(octubre(13, 10))
    assert pedido["hechos"][0]["aviso"] == "pedido_de_estado"
    assert pedido["hechos"][0]["numero"] == 1


def test_si_no_contesto_esa_tarea_el_dia_que_vence_se_le_pregunta(conn, mundo, escribe, dias):
    """La tarea vuelve si no contestó: contestar otra de la lista no cubre ésta."""
    _pregunta_la_lista(conn, mundo, dias, (T2, octubre(30, 17)))
    dice(conn, escribe, Jugada("informar_avance", {"tarea": "T2", "palabras": "viene bien"}),
         at=octubre(5, 10, 30))

    dias.ciclo(octubre(9, 10))

    [pedido] = avisos_guardados(conn, "pedido_de_estado")
    assert pedido["estado"] == "enviado"


def test_si_cambio_algo_despues_de_contestar_el_dia_que_vence_se_le_pregunta(conn, mundo,
                                                                            escribe, dias):
    """La tarea vuelve si cambió algo desde que la persona contó cómo venía: acá, su estado
    cambió por otro camino (como lo haría la plataforma)."""
    _pregunta_la_lista(conn, mundo, dias)
    dice(conn, escribe, Jugada("informar_avance", {"tarea": "T1", "palabras": "viene bien"}),
         at=octubre(5, 10, 30))
    poner_estado(conn, mundo["tarea"], "en_curso")

    dias.ciclo(octubre(9, 10))

    [pedido] = avisos_guardados(conn, "pedido_de_estado")
    assert pedido["estado"] == "enviado"


def test_con_otra_lista_en_el_medio_el_dia_que_vence_se_le_pregunta(conn, mundo, escribe, dias):
    """Lo contestado cubre hasta la lista siguiente: con la del miércoles en el medio (que no la
    trae, porque no cambió), el viernes 9 el pedido del vencimiento sale."""
    _cadencia(conn, mundo, MIERCOLES, nombre="estado_medio_semana")
    _pregunta_la_lista(conn, mundo, dias, (T2, octubre(30, 17)))
    dice(conn, escribe, Jugada("informar_avance", {"tarea": "T1", "palabras": "viene bien"}),
         at=octubre(5, 10, 30))
    dias.ciclo(octubre(7, 11, 30))

    dias.ciclo(octubre(9, 10))

    [pedido] = avisos_guardados(conn, "pedido_de_estado")
    assert pedido["estado"] == "enviado"


# --- Las otras listas de la semana, sólo lo que falta (decisión 46) -----------------------------

def _dos_listas(conn, mundo, dias) -> None:
    """Las listas del lunes y del miércoles (11:30), con T1 (vence el 9), T2 y T3 (el 30)."""
    _cadencia(conn, mundo, MIERCOLES, nombre="estado_medio_semana")
    _pregunta_la_lista(conn, mundo, dias, (T2, octubre(30, 17)), (T3, octubre(30, 17)))


def _las_listas_para(dias) -> list[dict]:
    return [p for p in _para(dias) if p["hechos"][0]["aviso"] == LISTA]


def test_la_lista_del_miercoles_trae_solo_lo_que_no_se_contesto(conn, mundo, escribe, dias):
    """Decisión 46 del usuario (2026-10-09): Marcos contestó T1 y T2 el lunes y no T3. El
    miércoles la lista trae sólo T3, con desde cuándo no la contestó ("del PLC no me contaste el
    lunes")."""
    _dos_listas(conn, mundo, dias)
    dice(conn, escribe, Jugada("informar_avance", {"tarea": "T1", "palabras": "viene bien"}),
         Jugada("anotar_inicio", {"tarea": "T2"}), at=octubre(5, 10, 30))

    dias.ciclo(octubre(7, 11, 30))

    lunes, miercoles = _las_listas_para(dias)
    assert "solo_lo_que_cambio_o_falta" not in lunes["hechos"][0]
    [hechos] = miercoles["hechos"]
    assert hechos["solo_lo_que_cambio_o_falta"] is True
    [t3] = hechos["sus_tareas"]
    assert _titulos([t3]) == [T3] and t3["sin_respuesta_desde"] == "2026-10-05"
    assert [t["titulo"] for t in miercoles["pregunta"]["de_la_lista"]] == [T3]


def test_la_lista_del_miercoles_trae_lo_que_cambio(conn, mundo, escribe, dias):
    """Una tarea contestada que después cambió (acá, la entregaron por otro camino) vuelve en la
    lista siguiente, con su situación de ahora; como no se puede mover, no se pregunta por ella."""
    _dos_listas(conn, mundo, dias)
    dice(conn, escribe, Jugada("informar_avance", {"tarea": "T1", "palabras": "viene bien"}),
         Jugada("anotar_inicio", {"tarea": "T2"}), Jugada("anotar_inicio", {"tarea": "T3"}),
         at=octubre(5, 10, 30))
    t2 = uno(conn, "select id from task where titulo = %s", T2)["id"]
    poner_estado(conn, str(t2), "en_revision")

    dias.ciclo(octubre(7, 11, 30))

    miercoles = _las_listas_para(dias)[-1]
    [hechos] = miercoles["hechos"]
    [de_t2] = hechos["sus_tareas"]
    assert _titulos([de_t2]) == [T2] and de_t2["estado"] == "en_revision"
    assert hechos["necesita_respuesta"] is False and miercoles["pregunta"] is None


def test_si_no_hay_nada_nuevo_la_lista_del_miercoles_no_sale(conn, mundo, escribe, dias):
    _dos_listas(conn, mundo, dias)
    dice(conn, escribe, Jugada("informar_avance", {"tarea": "T1", "palabras": "viene bien"}),
         Jugada("anotar_inicio", {"tarea": "T2"}), Jugada("anotar_inicio", {"tarea": "T3"}),
         at=octubre(5, 10, 30))

    dias.ciclo(octubre(7, 11, 30))

    _, miercoles = _listas(conn)
    assert (miercoles["estado"], miercoles["motivo_omision"]) == (
        "omitido", "sin_novedades_para_la_lista")
    assert len(_salieron_para(conn, mundo)) == 1           # sólo la del lunes


def test_lo_que_cuenta_fuera_de_la_lista_tambien_cuenta_como_contestado(conn, mundo, escribe,
                                                                         dias):
    """Marcos no contestó T3 en la lista, pero el martes contó que la arrancó: el miércoles no se
    le vuelve a preguntar."""
    _dos_listas(conn, mundo, dias)
    dice(conn, escribe, Jugada("informar_avance", {"tarea": "T1", "palabras": "viene bien"}),
         Jugada("anotar_inicio", {"tarea": "T2"}), at=octubre(5, 10, 30))
    dice(conn, escribe, Jugada("dejar_para_despues", {}), at=octubre(5, 10, 40))
    dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T3"}), at=octubre(6, 15))

    dias.ciclo(octubre(7, 11, 30))

    _, miercoles = _listas(conn)
    assert (miercoles["estado"], miercoles["motivo_omision"]) == (
        "omitido", "sin_novedades_para_la_lista")


def test_la_primera_lista_de_la_semana_es_completa_aunque_no_sea_el_lunes(conn, mundo, escribe,
                                                                          dias):
    """El lunes 12 es feriado: la del miércoles 14 es la primera de esa semana y trae todo."""
    _dos_listas(conn, mundo, dias)
    dice(conn, escribe, Jugada("informar_avance", {"tarea": "T1", "palabras": "viene bien"}),
         Jugada("anotar_inicio", {"tarea": "T2"}), Jugada("anotar_inicio", {"tarea": "T3"}),
         at=octubre(5, 10, 30))
    dias.ciclo(octubre(7, 11, 30))
    dias.ciclo(octubre(12, 10))

    dias.ciclo(octubre(14, 11, 30))

    [hechos] = _las_listas_para(dias)[-1]["hechos"]
    assert "solo_lo_que_cambio_o_falta" not in hechos
    assert _titulos(hechos["sus_tareas"]) == [T1, T3, T2]       # por su vencimiento y título


def test_lo_que_contesta_del_dia_que_vence_cuenta_para_su_escalera(conn, mundo, escribe, dias):
    """El pedido del viernes 9 fue en la lista: la respuesta lo contesta y la escalera de esa
    tarea se detiene."""
    _cadencia(conn, mundo, "0 9 * * 5")
    dias.ciclo(octubre(9, 10))

    dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(9, 10, 30))
    dias.ciclo(octubre(13, 10))
    dias.ciclo(octubre(14, 10))

    assert uno(conn, "select satisfecho_en from pending_reply")["satisfecho_en"] is not None
    assert len(avisos_guardados(conn, "pedido_de_estado")) == 1
