"""Escribirle a quien destraba (`leda.motor.persecucion`; C-5, porción 1; decisión 4 del usuario,
2026-10-08, primera mitad; ADR 0017, decisión 3a; conversación 32).

Cuando la persona trabada nombra a un integrante que destraba su tarea, Leda le escribe a esa
persona como Leda: un aviso guardado que sale terminado el margen para corregir y, al salir,
abre una pregunta para ella, con su propia espera (la repite la escalera de las preguntas, sin
escalar). Sin un chat con Leda, no le escribe y lo dice. Lo que contesta queda como un hecho del
bloqueo (`dicho_de_quien_destraba`) y la persona trabada se entera, como información; un "ya
está" no cierra el bloqueo. "No le escribas" retira el mensaje que todavía no salió; del que ya
salió, Leda dice que ya le llegó.
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from leda.db import admin
from leda.motor.escalera import correr_escalera
from leda.motor.fichas import FICHAS
from leda.motor.ia import Jugada
from leda.motor.ia_real import DATOS
from leda.motor import hechos as hechos_mod
from leda.motor.tiempo import RelojFijo

from tests.motor.ayudantes import (AHORA, IAQueRedacta, administrador, avisos_guardados,
                                   cuantas, enviar, nueva_tarea, octubre, todos, uno)
from tests.motor.test_aprobacion import Turnos

ARIEL, MARIANO = "Ariel De Simone", "Mariano Naim"
CAUSA = "me falta la ip del servidor"
PREGUNTA_A_QUIEN_DESTRABA = "pregunta_a_quien_destraba"
LO_QUE_DIJO = "lo_que_dijo_quien_destraba"


def _integrante(conn, mundo, corto: str, nombre: str, telegram: int | None) -> None:
    """Otra persona del espacio, cuyo trabajo aprueba Ismael; sin Telegram, no tiene un chat con
    Leda."""
    with admin(conn) as cur:
        cur.execute("select rol_id from membership where id = %s",
                    (mundo["personas"]["Marcos"]["membership_id"],))
        rol = cur.fetchone()["rol_id"]
        cur.execute("insert into app_user (telegram_user_id, nombre) values (%s, %s) "
                    "returning id", (telegram, nombre))
        usuario = str(cur.fetchone()["id"])
        cur.execute("""insert into membership (workspace_id, app_user_id, area_id, rol_id,
                                               aprobador_membership_id)
                       values (%s, %s, %s, %s, %s) returning id""",
                    (mundo["id"], usuario, mundo["area"], rol,
                     mundo["personas"]["Ismael"]["membership_id"]))
        mundo["personas"][corto] = {"app_user_id": usuario, "telegram": telegram,
                                    "membership_id": str(cur.fetchone()["id"])}
        cur.execute("""insert into greeting_state (membership_id, workspace_id, ultima_fecha_local)
                       values (%s, %s, date '9999-12-31')""",
                    (mundo["personas"][corto]["membership_id"], mundo["id"]))
    conn.commit()


@pytest.fixture
def equipo(conn, mundo) -> Turnos:
    """Ariel, con un chat con Leda, y Mariano, sin él; los turnos de cualquiera."""
    _integrante(conn, mundo, "Ariel", ARIEL, 81_020)
    _integrante(conn, mundo, "Mariano", MARIANO, None)
    return Turnos(conn, mundo)


def _trabada(t: Turnos, quien: str = "ariel"):
    """Marcos se traba con su tarea y dice quién la destraba: el resultado del segundo turno."""
    t.dice("Marcos", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": CAUSA}))
    return t.dice("Marcos", Jugada("anotar_quien_destraba", {"quien": quien}))


def _membresia(mundo, corto: str) -> str:
    return mundo["personas"][corto]["membership_id"]


def _salir(conn, mundo, at) -> IAQueRedacta:
    ia = IAQueRedacta()
    from leda.motor.avisos import enviar_avisos
    enviar_avisos(conn, mundo["id"], ia, RelojFijo(at))
    conn.commit()
    return ia


# --- Le escribe a quien destraba ------------------------------------------------------------

def test_nombrar_a_quien_destraba_guarda_una_pregunta_para_esa_persona(conn, mundo, equipo):
    r = _trabada(equipo)

    [aviso] = avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Ariel")
    assert str(aviso["task_id"]) == mundo["tarea"]
    # Le llega terminado el margen para corregir: es por algo que dijo Marcos.
    assert aviso["programado_para"] == AHORA + timedelta(minutes=2 + 10)
    hechos = aviso["hechos"]
    assert hechos["tarea"] == "Revisar el tablero"
    assert hechos["responsable"] == "Marcos"
    assert hechos["causa"] == CAUSA
    assert hechos["necesita_respuesta"] is True
    assert hechos["pregunta"] == "cuando_se_destraba"
    # Una por cada vez que se dice quién destraba.
    destraba = uno(conn, "select id from blocker_unblocker")
    assert aviso["dedupe_key"] == f"motor:{PREGUNTA_A_QUIEN_DESTRABA}:{mundo['tarea']}:" \
                                  f"u{destraba['id']}"
    [hecho] = r.hechos
    assert hecho["se_le_pregunta_a"]["a"] == ARIEL
    assert hecho["se_le_pregunta_a"]["llega"].startswith("2026-10-05T10:12")
    assert "salidas" not in hecho


def test_a_quien_no_tiene_un_chat_con_leda_no_le_escribe_y_lo_dice(conn, mundo, equipo):
    r = _trabada(equipo, quien="mariano")

    assert avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA) == []
    [hecho] = r.hechos
    assert "se_le_pregunta_a" not in hecho
    assert hecho["no_se_le_puede_escribir_a"] == {"a": MARIANO,
                                                  "motivo": "destinatario_sin_telegram"}


# --- Quien destraba no tiene Leda conectada (decisión 37 del usuario, 2026-10-09; C-5b) ------

SIN_LEDA_CONECTADA = "motor_sin_leda_conectada"


def test_sin_leda_conectada_se_le_avisa_al_administrador_para_que_lo_conecte(conn, mundo,
                                                                            equipo):
    administrador(conn)

    r = _trabada(equipo, quien="mariano")

    # El aviso sale de verdad, por el canal del administrador (un incidente y su aviso).
    [incidente] = todos(conn, "select etapa, resumen_sanitizado from incident")
    assert incidente["etapa"] == SIN_LEDA_CONECTADA
    assert MARIANO in incidente["resumen_sanitizado"]
    [cuerpo] = [f["cuerpo"] for f in todos(conn, "select cuerpo from admin_notice")]
    assert cuerpo.splitlines()[0] == "Una persona del equipo no tiene Leda conectada"
    [hecho] = r.hechos
    assert hecho["no_se_le_puede_escribir_a"] == {"a": MARIANO,
                                                  "motivo": "destinatario_sin_telegram"}
    aviso = hecho["se_le_aviso_al_administrador"]
    assert aviso["para_que_conecte"] == MARIANO
    assert aviso["llega"].startswith("2026-10-05T10:02")


def test_sin_un_administrador_alcanzable_no_promete_el_aviso(conn, mundo, equipo):
    r = _trabada(equipo, quien="mariano")

    # El incidente queda igual; a la persona no se le dice que el administrador se enteró.
    assert cuantas(conn, "incident", "etapa = %s", SIN_LEDA_CONECTADA) == 1
    [hecho] = r.hechos
    assert hecho["se_le_aviso_al_administrador"] == {"para_que_conecte": MARIANO,
                                                     "llega": "no_le_va_a_llegar"}


def test_sin_leda_conectada_le_ofrece_salidas(conn, mundo, equipo):
    """Otra persona que pueda destrabarlo, o que se lo pida ella y le cuente: un tema abierto,
    como toda propuesta."""
    administrador(conn)

    r = _trabada(equipo, quien="mariano")

    [hecho] = r.hechos
    assert hecho["salidas"] == ["anotar_quien_destraba", "pedirselo_y_contar"]
    assert r.pregunta["tipo"] == "propuesta"
    for codigo in ("se_le_aviso_al_administrador", "para_que_conecte", "pedirselo_y_contar"):
        assert hechos_mod.significado(codigo), codigo


def test_nombrar_a_otra_persona_contesta_las_salidas_y_le_escribe(conn, mundo, equipo):
    administrador(conn)
    _trabada(equipo, quien="mariano")

    r = equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"tarea": "T1", "quien": "ariel"}))

    assert cuantas(conn, "conversation_question",
                   "tipo = 'propuesta' and cerrada_en is null") == 0
    [aviso] = avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Ariel")
    [hecho] = r.hechos
    assert "salidas" not in hecho


def test_destrabar_cierra_las_salidas(conn, mundo, equipo):
    """"Se lo pido yo y te cuento": cuando cuenta que se destrabó, no queda nada abierto."""
    administrador(conn)
    _trabada(equipo, quien="mariano")

    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}))

    assert cuantas(conn, "conversation_question",
                   "tipo = 'propuesta' and cerrada_en is null") == 0


def test_a_alguien_de_afuera_del_equipo_no_le_escribe(conn, mundo, equipo):
    r = _trabada(equipo, quien="el proveedor de cables")
    # No es nadie del equipo: Leda pregunta quién es, y Marcos contesta que no es del equipo
    # (decisión 65 del usuario, 2026-10-11).
    assert r.pregunta["tipo"] == "quien_es_esa_persona"
    r = equipo.dice("Marcos", Jugada("decir_quien_es", {"de_afuera": True}),
                    texto="no es del equipo")

    assert avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA) == []
    [hecho] = r.hechos
    assert hecho["quien_destraba"] == {"externo": "el proveedor de cables"}
    assert "se_le_pregunta_a" not in hecho


def test_si_cambia_quien_destraba_el_mensaje_al_anterior_no_sale(conn, mundo, equipo):
    _trabada(equipo)
    equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"tarea": "T1", "quien": "ismael"}))

    viejo, nuevo = avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)
    assert (viejo["estado"], viejo["motivo_omision"]) == ("omitido", "cambio_quien_destraba")
    assert str(nuevo["destinatario_membership_id"]) == _membresia(mundo, "Ismael")
    assert nuevo["estado"] == "guardado"


def test_nombrar_otra_vez_a_la_misma_persona_no_le_escribe_dos_veces(conn, mundo, equipo):
    _trabada(equipo)
    r = equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"tarea": "T1", "quien": "ariel"}))

    [aviso] = avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)
    assert aviso["estado"] == "guardado"
    [hecho] = r.hechos
    assert hecho["se_le_pregunta_a"]["llega"].startswith("2026-10-05T10:12")


# --- Al salir -------------------------------------------------------------------------------

def test_al_salir_le_abre_la_pregunta_con_su_espera(conn, mundo, equipo):
    _trabada(equipo)

    ia = _salir(conn, mundo, AHORA + timedelta(minutes=12))

    [pedido] = ia.pedidos_de_redaccion
    assert pedido["persona"] == ARIEL
    assert pedido["pregunta"]["tipo"] == "cuando_se_destraba"
    [hechos] = pedido["hechos"]
    assert (hechos["aviso"], hechos["responsable"], hechos["causa"]) == (
        PREGUNTA_A_QUIEN_DESTRABA, "Marcos", CAUSA)
    ariel = _membresia(mundo, "Ariel")
    pregunta = uno(conn, """select q.tipo, q.task_id::text tarea from conversation_state s
                              join conversation_question q on q.id = s.pregunta_abierta_id
                             where s.membership_id = %s""", ariel)
    assert pregunta == {"tipo": "cuando_se_destraba", "tarea": mundo["tarea"]}
    espera = uno(conn, """select tipo, task_id::text tarea, satisfecho_en from pending_reply
                           where membership_id = %s""", ariel)
    assert espera == {"tipo": "cuando_se_destraba", "tarea": mundo["tarea"],
                      "satisfecho_en": None}
    assert cuantas(conn, "message_outbox", "destinatario_membership_id = %s and not es_respuesta",
                   ariel) == 1


def test_no_sale_si_la_tarea_ya_se_destrabo(conn, mundo, equipo):
    _trabada(equipo)
    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}))

    _salir(conn, mundo, AHORA + timedelta(minutes=13))

    [aviso] = avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "ya_se_destrabo")


def _los_dias(conn, mundo, dias) -> IAQueRedacta:
    ia = IAQueRedacta()
    from leda.motor.avisos import enviar_avisos
    for dia in dias:
        correr_escalera(conn, mundo["id"], RelojFijo(octubre(dia, 10)))
        conn.commit()
        enviar_avisos(conn, mundo["id"], ia, RelojFijo(octubre(dia, 10)))
        conn.commit()
    return ia


def _repreguntas(conn) -> list[dict]:
    return todos(conn, """select destinatario_membership_id::text a, hechos, creado_en
                            from scheduled_notice where tipo = 'repregunta'
                           order by creado_en""")


def test_a_quien_destraba_y_no_contesta_nunca_lo_abandona(conn, espacio_con_escalera, equipo):
    """Decisión 38 del usuario (2026-10-09): los días 1 a 3, una vez por día (la pregunta del
    lunes 5 y las del martes 6 y el miércoles 7); desde el 4, cada 2 días hábiles mientras siga
    el bloqueo (el viernes 9; el lunes 12 es feriado, así que el miércoles 14 y el viernes 16).
    Nunca escala: lo que pasa con un bloqueo que no se mueve es el bloqueo viejo."""
    mundo = espacio_con_escalera
    _trabada(equipo)
    _salir(conn, mundo, AHORA + timedelta(minutes=12))
    ariel = _membresia(mundo, "Ariel")

    _los_dias(conn, mundo, (6, 7, 8, 9, 13, 14, 15, 16))

    repreguntas = _repreguntas(conn)
    assert [r["a"] for r in repreguntas] == [ariel] * 5
    assert [(r["creado_en"] - timedelta(hours=3)).day for r in repreguntas] == [6, 7, 9, 14, 16]
    assert [r["hechos"]["numero"] for r in repreguntas] == [2, 3, 4, 5, 6]
    assert all("avisa_que_va_a_escalar" not in r["hechos"] for r in repreguntas)
    assert all("si_no_hay_respuesta" not in r["hechos"] for r in repreguntas)
    assert cuantas(conn, "scheduled_notice", "tipo = 'escalamiento_de_una_pregunta'") == 0
    # Lo que se repite dice quién está trabado y por qué.
    assert repreguntas[0]["hechos"]["sobre"]["responsable"] == "Marcos"
    assert repreguntas[0]["hechos"]["sobre"]["causa"] == CAUSA


def test_deja_de_repetirla_cuando_se_destraba(conn, espacio_con_escalera, equipo):
    mundo = espacio_con_escalera
    _trabada(equipo)
    _salir(conn, mundo, AHORA + timedelta(minutes=12))
    _los_dias(conn, mundo, (6, 7, 8, 9))
    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}), at=octubre(9, 11))

    _los_dias(conn, mundo, (13, 14, 15, 16))

    assert len(_repreguntas(conn)) == 3


# --- Quien destraba contesta ----------------------------------------------------------------

def _le_pregunto(conn, mundo, equipo) -> None:
    _trabada(equipo)
    _salir(conn, mundo, AHORA + timedelta(minutes=12))
    equipo.minuto = 30


def test_quien_destraba_ve_la_tarea_trabada_en_su_lista(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)

    equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                {"tarea": "T1", "para_cuando": "2026-10-06"}))

    [tarea] = equipo.situacion["tareas"]
    assert tarea["alias"] == "T1"
    assert tarea["titulo"] == "Revisar el tablero"
    assert tarea["espera_que_la_destrabe"] is True
    assert (tarea["responsable"], tarea["causa"]) == ("Marcos", CAUSA)
    assert equipo.situacion["estado"]["pregunta_abierta"] == {"tipo": "cuando_se_destraba",
                                                              "tarea": "T1"}


def test_lo_que_dice_queda_anotado_y_le_llega_a_quien_esta_trabado(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)

    r = equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                    {"para_cuando": "2026-10-06",
                                     "lo_que_dice": "manana a la manana se la paso"}),
                    texto="uh me olvide, manana a la manana se la paso")

    dicho = uno(conn, """select d.para_cuando::text para_cuando, d.ya_esta, d.lo_que_dice,
                                d.dicho_por_membership_id::text quien
                           from dicho_de_quien_destraba d""")
    assert dicho == {"para_cuando": "2026-10-06", "ya_esta": False,
                     "lo_que_dice": "manana a la manana se la paso",
                     "quien": _membresia(mundo, "Ariel")}
    assert cuantas(conn, "audit_log", "accion = 'anotar_lo_que_dice_quien_destraba'") == 1
    ariel = _membresia(mundo, "Ariel")
    # Su pregunta y su espera se cierran.
    assert cuantas(conn, "conversation_question",
                   "membership_id = %s and cerrada_en is null", ariel) == 0
    assert cuantas(conn, "pending_reply",
                   "membership_id = %s and satisfecho_en is null", ariel) == 0
    # El bloqueo sigue abierto: lo cierra Marcos.
    assert cuantas(conn, "blocker", "resuelto_en is null") == 1
    [aviso] = avisos_guardados(conn, LO_QUE_DIJO)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Marcos")
    assert aviso["programado_para"] == AHORA + timedelta(minutes=31 + 10)
    assert aviso["hechos"]["quien_destraba"] == ARIEL
    assert aviso["hechos"]["dice_quien_destraba"] == {
        "para_cuando": "2026-10-06", "lo_que_dice": "manana a la manana se la paso"}
    assert aviso["hechos"]["necesita_respuesta"] is False
    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["tarea"] == {"alias": "T1", "titulo": "Revisar el tablero"}
    assert hecho["aviso_a_quien_esta_trabado"]["a"] == "Marcos"
    assert r.pregunta is None


def test_ya_esta_no_cierra_el_bloqueo(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)

    equipo.dice("Ariel", Jugada("decir_cuando_destraba", {"tarea": "T1", "ya_esta": True}))

    assert cuantas(conn, "blocker", "resuelto_en is null") == 1
    assert uno(conn, "select estado::text e from task where id = %s",
               mundo["tarea"])["e"] == "bloqueada"
    [aviso] = avisos_guardados(conn, LO_QUE_DIJO)
    assert aviso["hechos"]["dice_quien_destraba"] == {"ya_esta": True}


def test_sin_decir_nada_no_anota_nada(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)

    r = equipo.dice("Ariel", Jugada("decir_cuando_destraba", {"tarea": "T1"}))

    [hecho] = r.hechos
    assert hecho["resultado"] == "falta_dato"
    assert cuantas(conn, "dicho_de_quien_destraba") == 0


def test_quien_no_destraba_esa_tarea_no_puede_decirlo(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)

    r = equipo.dice("Ismael", Jugada("decir_cuando_destraba", {"para_cuando": "2026-10-06"}))

    [hecho] = r.hechos
    assert hecho["resultado"] in ("no_se_puede", "falta_dato")
    assert cuantas(conn, "dicho_de_quien_destraba") == 0
    assert avisos_guardados(conn, LO_QUE_DIJO) == []


def test_lo_que_le_llega_a_quien_esta_trabado_no_sale_si_ya_se_destrabo(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_cuando_destraba", {"tarea": "T1", "ya_esta": True}))
    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}))

    # Pasada la media hora en que Marcos estuvo conversando (no interrumpir).
    _salir(conn, mundo, AHORA + timedelta(minutes=90))

    [aviso] = avisos_guardados(conn, LO_QUE_DIJO)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "ya_se_destrabo")


def test_destrabar_cierra_la_pregunta_de_quien_destraba(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)

    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}))

    ariel = _membresia(mundo, "Ariel")
    assert cuantas(conn, "conversation_question",
                   "membership_id = %s and cerrada_en is null", ariel) == 0
    assert cuantas(conn, "pending_reply",
                   "membership_id = %s and satisfecho_en is null", ariel) == 0


# --- "Ya lo hablé con él" (C-5, porción 2; decisión 4, segunda mitad; conversación 33) ---------

def _su_pregunta(conn, mundo, corto: str = "Ariel") -> dict | None:
    return uno(conn, """select q.tipo, q.task_id::text tarea, q.jugada, q.cerrada_en
                          from conversation_state s
                          join conversation_question q on q.id = s.pregunta_abierta_id
                         where s.membership_id = %s""", _membresia(mundo, corto))


def test_ya_lo_hablaron_sin_fecha_pregunta_que_arreglaron(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)

    r = equipo.dice("Ariel", Jugada("decir_cuando_destraba", {"ya_lo_hablaron": True}),
                    texto="si ya lo hable con marcos")

    [hecho] = r.hechos
    assert hecho["resultado"] == "falta_dato"
    assert hecho["falta"] == ["lo_que_arreglaron", "para_cuando"]
    assert hecho["ya_lo_hablaron"] is True
    assert hecho["pregunta"] == "cuando_se_destraba"
    assert hecho["tarea"] == {"alias": "T1", "titulo": "Revisar el tablero"}
    # Nada queda anotado todavía y Marcos no se entera de nada.
    assert cuantas(conn, "dicho_de_quien_destraba") == 0
    assert avisos_guardados(conn, LO_QUE_DIJO) == []
    # La pregunta sigue abierta, con su espera, y ahora recuerda que ya lo hablaron.
    pregunta = _su_pregunta(conn, mundo)
    assert (pregunta["tipo"], pregunta["tarea"], pregunta["cerrada_en"]) == (
        "cuando_se_destraba", mundo["tarea"], None)
    assert pregunta["jugada"]["datos"]["ya_lo_hablaron"] is True
    assert cuantas(conn, "pending_reply", "membership_id = %s and satisfecho_en is null",
                   _membresia(mundo, "Ariel")) == 1


def test_lo_que_arreglaron_queda_anotado_y_le_llega_a_quien_esta_trabado(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_cuando_destraba", {"ya_lo_hablaron": True}))

    r = equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                    {"para_cuando": "2026-10-08",
                                     "lo_que_dice": "quedamos q se la paso el jueves"}))

    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["dice_quien_destraba"] == {"para_cuando": "2026-10-08",
                                            "lo_que_dice": "quedamos q se la paso el jueves",
                                            "ya_lo_hablaron": True}
    dicho = uno(conn, "select para_cuando::text p, lo_que_dice from dicho_de_quien_destraba")
    assert dicho == {"p": "2026-10-08", "lo_que_dice": "quedamos q se la paso el jueves"}
    [aviso] = avisos_guardados(conn, LO_QUE_DIJO)
    assert aviso["hechos"]["dice_quien_destraba"]["ya_lo_hablaron"] is True
    assert _su_pregunta(conn, mundo) is None
    assert cuantas(conn, "pending_reply", "membership_id = %s and satisfecho_en is null",
                   _membresia(mundo, "Ariel")) == 0
    assert cuantas(conn, "audit_log", "accion = 'anotar_lo_que_dice_quien_destraba'") == 1


def test_dicho_todo_junto_se_anota_sin_preguntar(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)

    r = equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                    {"tarea": "T1", "ya_lo_hablaron": True,
                                     "para_cuando": "2026-10-09"}))

    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["dice_quien_destraba"] == {"para_cuando": "2026-10-09", "ya_lo_hablaron": True}
    assert "pregunta" not in hecho
    assert cuantas(conn, "dicho_de_quien_destraba") == 1


def test_lo_que_arreglaron_se_pregunta_una_sola_vez(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_cuando_destraba", {"ya_lo_hablaron": True}))

    r = equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                    {"lo_que_dice": "quedamos que lo ve el con corelabs"}))

    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["dice_quien_destraba"] == {"lo_que_dice": "quedamos que lo ve el con corelabs",
                                            "ya_lo_hablaron": True}
    assert _su_pregunta(conn, mundo) is None


def test_lo_que_dice_junto_con_ya_lo_hablaron_no_se_pierde(conn, mundo, equipo):
    """Lo que dice quien destraba al contar que ya lo hablaron, sin una fecha, queda en su
    pregunta y se anota con la respuesta: nada de lo que dijo se pierde (revisión del
    2026-10-09)."""
    _le_pregunto(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                {"ya_lo_hablaron": True,
                                 "lo_que_dice": "ya lo hable con marcos, depende de sistemas"}))
    assert _su_pregunta(conn, mundo)["jugada"]["datos"]["lo_que_dice"] == \
        "ya lo hable con marcos, depende de sistemas"

    r = equipo.dice("Ariel", Jugada("decir_cuando_destraba", {"para_cuando": "2026-10-08"}))

    [hecho] = r.hechos
    assert hecho["dice_quien_destraba"]["lo_que_dice"] == \
        "ya lo hable con marcos, depende de sistemas"
    dicho = uno(conn, "select lo_que_dice from dicho_de_quien_destraba")
    assert dicho["lo_que_dice"] == "ya lo hable con marcos, depende de sistemas"


def test_lo_que_dice_antes_y_despues_de_la_pregunta_queda_todo(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                {"ya_lo_hablaron": True, "lo_que_dice": "depende de sistemas"}))

    equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                {"para_cuando": "2026-10-08",
                                 "lo_que_dice": "quedamos q se la paso el jueves"}))

    dicho = uno(conn, "select lo_que_dice from dicho_de_quien_destraba")
    assert "depende de sistemas" in dicho["lo_que_dice"]
    assert "quedamos q se la paso el jueves" in dicho["lo_que_dice"]


def test_lo_que_se_repite_recuerda_que_ya_lo_hablaron(conn, espacio_con_escalera, equipo):
    mundo = espacio_con_escalera
    _le_pregunto(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_cuando_destraba", {"ya_lo_hablaron": True}))

    correr_escalera(conn, mundo["id"], RelojFijo(octubre(6, 10)))
    conn.commit()

    [repregunta] = todos(conn, "select hechos from scheduled_notice where tipo = 'repregunta'")
    assert repregunta["hechos"]["sobre"]["ya_lo_hablaron"] is True


def test_si_contesta_antes_de_que_le_llegue_la_pregunta_no_sale(conn, mundo, equipo):
    """Quien destraba ya ve la tarea en su lista: si contesta antes de que le llegue el mensaje
    de Leda (el margen para corregir), ese mensaje no sale."""
    _trabada(equipo)

    equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                {"tarea": "T1", "para_cuando": "2026-10-06"}))
    # Pasada la media hora en que Ariel estuvo conversando (no interrumpir).
    _salir(conn, mundo, AHORA + timedelta(minutes=40))

    [aviso] = avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "ya_respondio")


def test_ya_lo_hablaron_antes_de_que_le_llegue_la_pregunta_se_la_hace_ahora(conn, mundo, equipo):
    _trabada(equipo)

    r = equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                    {"tarea": "T1", "ya_lo_hablaron": True}))
    _salir(conn, mundo, AHORA + timedelta(minutes=40))

    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["pregunta"]) == ("falta_dato", "cuando_se_destraba")
    pregunta = _su_pregunta(conn, mundo)
    assert pregunta["tipo"] == "cuando_se_destraba"
    destraba = uno(conn, "select id::text id from blocker_unblocker")
    assert pregunta["jugada"]["destraba_id"] == destraba["id"]
    # El mensaje que todavía no salió ya no hace falta: la pregunta se le hizo en su chat.
    [aviso] = avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "ya_respondio")


# --- "No le escribas" -------------------------------------------------------------------------

def test_no_le_escribas_retira_el_mensaje_que_todavia_no_salio(conn, mundo, equipo):
    _trabada(equipo)

    r = equipo.dice("Marcos", Jugada("no_escribirle", {"quien": "ariel"}))

    [aviso] = avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "pidio_que_no_le_escriba")
    assert cuantas(conn, "audit_log", "accion = 'no_escribirle'") == 1
    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["se_le_pregunta_a"] == {"a": ARIEL, "llega": "no_le_va_a_llegar",
                                         "motivo": "pidio_que_no_le_escriba"}
    # Quién destraba sigue anotado.
    assert cuantas(conn, "blocker_unblocker") == 1
    _salir(conn, mundo, AHORA + timedelta(minutes=20))
    assert cuantas(conn, "message_outbox", "destinatario_membership_id = %s",
                   _membresia(mundo, "Ariel")) == 0


def test_no_le_escribas_despues_de_que_dio_un_dia_se_lo_cierra(conn, mundo, equipo):
    """Ariel ya había dado un día: "no le escribas" hace que Leda no le pregunte más y se lo
    diga (derivado de la regla 39 en la C-5d; antes no le llegaba nada)."""
    _le_pregunto(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                {"tarea": "T1", "para_cuando": "2026-10-06"}))

    r = equipo.dice("Marcos", Jugada("no_escribirle", {"tarea": "T1"}))

    [aviso] = avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)
    assert aviso["estado"] == "enviado"
    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["se_le_pregunta_a"] == {"a": ARIEL, "llega": "ya_le_llego",
                                         "el": "2026-10-05"}
    [avisado] = hecho["ya_no_hace_falta_que_destraben"]
    assert avisado["aviso_a_quien_destrababa"]["a"] == ARIEL
    [cerrado] = avisos_guardados(conn, YA_NO_HACE_FALTA)
    assert str(cerrado["destinatario_membership_id"]) == _membresia(mundo, "Ariel")
    assert cerrado["hechos"]["como_se_cerro"] == "dijo_que_ya_lo_hablaron"
    assert cerrado["hechos"]["habia_dicho"] == {"para_cuando": "2026-10-06"}


def test_no_le_escribas_despues_de_que_dijo_que_ya_esta_dice_que_ya_le_llego(conn, mundo,
                                                                            equipo):
    """Ariel ya dijo que ya está: Leda no le pregunta nada ni le va a preguntar, así que no hay
    nada que retirar ni que cerrarle."""
    _le_pregunto(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_cuando_destraba", {"tarea": "T1", "ya_esta": True}))

    r = equipo.dice("Marcos", Jugada("no_escribirle", {"tarea": "T1"}))

    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["motivo"]) == ("no_se_puede", "ya_se_le_escribio")
    assert hecho["se_le_pregunta_a"] == {"a": ARIEL, "llega": "ya_le_llego",
                                         "el": "2026-10-05"}
    assert avisos_guardados(conn, YA_NO_HACE_FALTA) == []


def test_no_le_escribas_encuentra_el_mensaje_aunque_esa_persona_ya_no_este_activa(conn, mundo,
                                                                                   equipo):
    """La vista `integrante` incluye a las personas inactivas del espacio: el mensaje a quien
    dejó de estar activo después de guardado se encuentra y se retira igual (revisión del
    2026-10-09, que no era un defecto: queda como regresión)."""
    _trabada(equipo)
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (_membresia(mundo, "Ariel"),))
    conn.commit()

    r = equipo.dice("Marcos", Jugada("no_escribirle", {"tarea": "T1"}))

    [aviso] = avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "pidio_que_no_le_escriba")
    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["se_le_pregunta_a"]["a"] == ARIEL


def test_no_le_escribas_sin_ningun_mensaje_lo_dice(conn, mundo, equipo):
    _trabada(equipo, quien="mariano")

    r = equipo.dice("Marcos", Jugada("no_escribirle", {"tarea": "T1"}))

    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["motivo"]) == ("no_se_puede", "no_le_iba_a_escribir")


def test_no_le_escribas_en_el_mismo_mensaje_lo_cuenta_como_quedo(conn, mundo, equipo):
    equipo.dice("Marcos", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": CAUSA}))

    r = equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"quien": "ariel"}),
                    Jugada("no_escribirle", {"tarea": "T1"}))

    destraba, no_escribir = r.hechos
    assert destraba["se_le_pregunta_a"]["llega"] == "no_le_va_a_llegar"
    assert no_escribir["resultado"] == "anotado"


# --- El contrato con la IA ------------------------------------------------------------------

def test_las_jugadas_nuevas_tienen_sus_datos_y_sus_significados():
    for nombre in ("decir_cuando_destraba", "no_escribirle"):
        ficha = FICHAS[nombre]
        assert ficha.es
        for dato in ficha.necesita + ficha.opcional:
            assert dato in DATOS, (nombre, dato)
        assert nombre in hechos_mod.PARA_LA_REDACCION
    for codigo in ("cuando_se_destraba", PREGUNTA_A_QUIEN_DESTRABA, LO_QUE_DIJO,
                   "se_le_pregunta_a", "no_se_le_puede_escribir_a", "espera_que_la_destrabe",
                   "dice_quien_destraba", "aviso_a_quien_esta_trabado", "para_cuando",
                   "ya_esta", "lo_que_dice", "pidio_que_no_le_escriba", "ya_se_le_escribio",
                   "no_le_iba_a_escribir", "ya_se_destrabo", "cambio_quien_destraba",
                   "no_le_toca_destrabarla",
                   # La porción 2: "ya lo hablé con él".
                   "ya_lo_hablaron", "lo_que_arreglaron"):
        assert hechos_mod.significado(codigo), codigo
    assert "ya_lo_hablaron" in FICHAS["decir_cuando_destraba"].opcional


# --- C-5c: cerrar el tema para todos, lo acordado y "se lo pido yo" ----------------------------
#
# Decisiones 39, 47 y 48 del usuario (2026-10-09; `odd/tasks/fase-c.md`) y la salida "se lo pido
# yo y te cuento" de la decisión 37; conversaciones 33 y 43.

YA_NO_HACE_FALTA = "ya_no_hace_falta_que_destrabe"
LO_QUE_DIJO_QUIEN_ESTA_TRABADO = "lo_que_dijo_quien_esta_trabado"
PREGUNTA_A_QUIEN_ESTA_TRABADO = "pregunta_a_quien_esta_trabado"
COMO_LE_FUE = "como_le_fue_con_quien_destraba"


def _ariel_dice(equipo, at=None, **datos):
    return equipo.dice("Ariel", Jugada("decir_cuando_destraba", {"tarea": "T1", **datos}), at=at)


def _marcos_cuenta(equipo, at=None, **datos):
    return equipo.dice("Marcos", Jugada("contar_lo_que_arreglaron", datos), at=at)


def _abiertas(conn, mundo, corto: str, tipo: str | None = None) -> int:
    return cuantas(conn, "conversation_question",
                   "membership_id = %s and cerrada_en is null "
                   "and (%s::text is null or tipo = %s)",
                   _membresia(mundo, corto), tipo, tipo)


def _esperas(conn, mundo, corto: str) -> int:
    return cuantas(conn, "pending_reply", "membership_id = %s and satisfecho_en is null",
                   _membresia(mundo, corto))


# Decisión 39: si el bloqueo se resuelve por otro lado, a quien le preguntaba se le avisa.

def test_si_se_destraba_por_otro_lado_a_quien_le_preguntaba_se_le_avisa(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)
    _ariel_dice(equipo, para_cuando="2026-10-08")

    r = equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}))

    [aviso] = avisos_guardados(conn, YA_NO_HACE_FALTA)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Ariel")
    # Con el margen para corregir: lo causa lo que dijo Marcos.
    assert aviso["programado_para"] == AHORA + timedelta(minutes=32 + 10)
    hechos = aviso["hechos"]
    assert hechos["como_se_cerro"] == "ya_se_destrabo"
    assert hechos["habia_dicho"] == {"para_cuando": "2026-10-08"}
    assert hechos["necesita_respuesta"] is False
    assert (hechos["tarea"], hechos["responsable"], hechos["causa"]) == (
        "Revisar el tablero", "Marcos", CAUSA)
    [hecho] = r.hechos
    [avisado] = hecho["ya_no_hace_falta_que_destraben"]
    assert avisado["aviso_a_quien_destrababa"]["a"] == ARIEL
    assert avisado["aviso_a_quien_destrababa"]["llega"].startswith("2026-10-05T1")


def test_a_quien_todavia_no_le_llego_la_pregunta_no_hay_nada_que_cerrarle(conn, mundo, equipo):
    _trabada(equipo)

    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}))

    assert avisos_guardados(conn, YA_NO_HACE_FALTA) == []


def test_a_quien_dijo_que_ya_esta_se_le_avisa_cuando_por_fin_se_destraba(conn, mundo, equipo):
    """Derivado de la regla 39 en la C-5d: el bloqueo lo da por destrabado quien está trabado
    (decisión 41), así que quien dijo "ya está" se entera de cuándo se cerró de verdad."""
    _le_pregunto(conn, mundo, equipo)
    _ariel_dice(equipo, ya_esta=True)

    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}))

    [aviso] = avisos_guardados(conn, YA_NO_HACE_FALTA)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Ariel")
    assert aviso["hechos"]["como_se_cerro"] == "ya_se_destrabo"
    assert aviso["hechos"]["habia_dicho"] == {"ya_esta": True}


def test_a_quien_no_contesto_tambien_se_le_avisa(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)

    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}))

    [aviso] = avisos_guardados(conn, YA_NO_HACE_FALTA)
    assert "habia_dicho" not in aviso["hechos"]
    assert _abiertas(conn, mundo, "Ariel") == 0


def test_si_lo_destraba_otra_persona_a_quien_le_preguntaba_se_le_avisa(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)

    r = equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"tarea": "T1", "quien": "ismael"}))

    [aviso] = avisos_guardados(conn, YA_NO_HACE_FALTA)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Ariel")
    assert aviso["hechos"]["como_se_cerro"] == "cambio_quien_destraba"
    assert _abiertas(conn, mundo, "Ariel") == 0
    assert "ya_no_hace_falta_que_destraben" in r.hechos[0]


def test_si_dice_que_no_sabe_quien_a_quien_le_preguntaba_tambien_se_le_avisa(conn, mundo,
                                                                             equipo):
    _le_pregunto(conn, mundo, equipo)

    equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"tarea": "T1", "no_sabe": True}))

    [aviso] = avisos_guardados(conn, YA_NO_HACE_FALTA)
    # Lo que pasó, no que la destraba otra persona: nadie nombró a nadie (ronda real del
    # 2026-10-10, conversación 34).
    assert aviso["hechos"]["como_se_cerro"] == "no_sabe_quien_destraba"
    assert _abiertas(conn, mundo, "Ariel") == 0


def test_si_dice_que_no_hay_nadie_mas_a_quien_le_preguntaba_se_le_avisa_eso(conn, mundo,
                                                                            equipo):
    _le_pregunto(conn, mundo, equipo)

    equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"tarea": "T1", "nadie_mas": True}))

    [aviso] = avisos_guardados(conn, YA_NO_HACE_FALTA)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Ariel")
    assert aviso["hechos"]["como_se_cerro"] == "nadie_mas_puede_destrabar"
    assert _abiertas(conn, mundo, "Ariel") == 0


def test_si_dice_que_no_sabe_y_despues_vuelve_a_nombrarlo_el_aviso_no_sale(conn, mundo, equipo):
    """Como con otra persona: si antes de que salga lo vuelve a nombrar, ya no es cierto."""
    _le_pregunto(conn, mundo, equipo)
    equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"tarea": "T1", "no_sabe": True}))
    equipo.minuto = 33
    equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"tarea": "T1", "quien": "ariel"}))

    _salir(conn, mundo, AHORA + timedelta(minutes=60))

    [aviso] = avisos_guardados(conn, YA_NO_HACE_FALTA)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido",
                                                          "volvio_a_ser_quien_destraba")


def test_nombrar_otra_vez_a_quien_le_preguntaba_no_le_cierra_nada(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)

    equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"tarea": "T1", "quien": "ariel"}))

    assert avisos_guardados(conn, YA_NO_HACE_FALTA) == []


def test_si_lo_vuelve_a_nombrar_dentro_del_margen_el_aviso_no_sale(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)
    equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"tarea": "T1", "quien": "ismael"}))
    equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"tarea": "T1", "quien": "ariel"}))

    _salir(conn, mundo, AHORA + timedelta(minutes=90))

    [aviso] = avisos_guardados(conn, YA_NO_HACE_FALTA)
    assert aviso["estado"] == "omitido"


def test_que_ya_no_hace_falta_sale_como_informacion(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)
    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}))

    ia = _salir(conn, mundo, AHORA + timedelta(minutes=90))

    [pedido] = [p for p in ia.pedidos_de_redaccion if p["persona"] == ARIEL]
    assert pedido["pregunta"] is None
    assert pedido["hechos"][0]["aviso"] == YA_NO_HACE_FALTA
    assert hechos_mod.sin_significado(pedido) == set()


def _cerrado_por_otro_lado(conn, mundo, equipo) -> None:
    """Ariel dijo para cuándo, Marcos lo resolvió por otro lado y a Ariel ya le llegó."""
    _le_pregunto(conn, mundo, equipo)
    _ariel_dice(equipo, para_cuando="2026-10-08")
    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}))
    _salir(conn, mundo, AHORA + timedelta(minutes=90))


def test_lo_que_contesta_despues_le_llega_a_quien_decide(conn, mundo, equipo):
    """Decisión 39: "ya lo pedí, no lo puedo cancelar" afecta a Marcos, que decide: le llega, y
    si quiere decirle algo, Leda se lo pasa."""
    _cerrado_por_otro_lado(conn, mundo, equipo)

    r = equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                    {"lo_que_dice": "ya lo pedi, no lo puedo cancelar"}),
                    at=AHORA + timedelta(minutes=100))

    [vista] = equipo.situacion["tareas"]
    assert vista["ya_no_hace_falta_que_la_destrabe"] is True
    assert "espera_que_la_destrabe" not in vista
    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["aviso_a_quien_esta_trabado"]["a"] == "Marcos"
    aviso = avisos_guardados(conn, LO_QUE_DIJO)[-1]
    assert aviso["estado"] == "guardado"
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Marcos")
    assert aviso["hechos"]["dice_quien_destraba"] == {
        "lo_que_dice": "ya lo pedi, no lo puedo cancelar"}
    assert aviso["hechos"]["ya_se_habia_destrabado"] is True
    assert aviso["hechos"]["se_lo_pasa_si_contesta"] is True
    assert cuantas(conn, "dicho_de_quien_destraba") == 2


def test_la_respuesta_de_quien_decide_le_llega_y_cierra_el_tema(conn, mundo, equipo):
    _cerrado_por_otro_lado(conn, mundo, equipo)
    _ariel_dice(equipo, at=AHORA + timedelta(minutes=100),
                lo_que_dice="ya lo pedi, no lo puedo cancelar")
    _salir(conn, mundo, AHORA + timedelta(minutes=140))

    r = _marcos_cuenta(equipo, at=AHORA + timedelta(minutes=150),
                       lo_que_dice="que llegue nomas, queda de repuesto")

    [aviso] = avisos_guardados(conn, LO_QUE_DIJO_QUIEN_ESTA_TRABADO)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Ariel")
    assert aviso["hechos"]["cierra_el_tema"] is True
    assert "se_lo_pasa_si_contesta" not in aviso["hechos"]
    assert aviso["hechos"]["quien_esta_trabado"] == "Marcos"
    assert aviso["hechos"]["dice_quien_esta_trabado"] == {
        "lo_que_dice": "que llegue nomas, queda de repuesto"}
    dicho = uno(conn, """select lo_que_dice from dicho_de_quien_destraba
                          where dicho_por_membership_id = %s""", _membresia(mundo, "Marcos"))
    assert dicho["lo_que_dice"] == "que llegue nomas, queda de repuesto"
    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["cierra_el_tema"]) == ("anotado", True)
    assert hecho["aviso_a_quien_destraba"]["a"] == ARIEL
    # Cerrado para los dos: con la respuesta de Marcos, la tarea deja de estar en la lista de Ariel.
    _salir(conn, mundo, AHORA + timedelta(minutes=200))
    equipo.dice("Ariel", at=AHORA + timedelta(minutes=210))
    assert equipo.situacion["tareas"] == []


# Decisión 62: la oferta de pasarle algo deja una pregunta liviana, si no hay otra abierta.

def _la_oferta(conn, mundo, corto: str) -> dict | None:
    """La oferta opcional que Leda le dejó a esa persona (`preguntas.OPCIONAL`), la última."""
    return uno(conn, """select * from conversation_question
                         where membership_id = %s and tipo = 'propuesta'
                           and (jugada ->> 'opcional')::boolean
                         order by abierta_en desc limit 1""", _membresia(mundo, corto))


def _a_marcos_le_llega_lo_que_dijo(conn, mundo, equipo, *antes) -> IAQueRedacta:
    """Ariel contesta después de que el tema se cerró y a Marcos le llega, con la oferta de
    pasarle algo (`se_lo_pasa_si_contesta`). `antes`: lo que hace Marcos antes de que le llegue."""
    _cerrado_por_otro_lado(conn, mundo, equipo)
    _ariel_dice(equipo, at=AHORA + timedelta(minutes=100),
                lo_que_dice="ya lo pedi, no lo puedo cancelar")
    for jugada in antes:
        equipo.dice("Marcos", jugada, at=AHORA + timedelta(minutes=102))
    return _salir(conn, mundo, AHORA + timedelta(minutes=140))


def test_la_oferta_de_pasarle_algo_deja_una_pregunta_opcional(conn, mundo, equipo):
    """La conversación 43, paso 9: lo que Marcos contesta se lee como respuesta a la oferta. El
    aviso sale como información (la oferta la dicen sus hechos) y deja anotada la pregunta."""
    ia = _a_marcos_le_llega_lo_que_dijo(conn, mundo, equipo)

    [pedido] = [p for p in ia.pedidos_de_redaccion if p["persona"] == "Marcos"]
    assert pedido["pregunta"] is None
    assert pedido["hechos"][0]["se_lo_pasa_si_contesta"] is True
    oferta = _la_oferta(conn, mundo, "Marcos")
    assert oferta is not None and oferta["cerrada_en"] is None
    assert str(oferta["task_id"]) == mundo["tarea"]
    assert oferta["jugada"]["propone"] == ["contar_lo_que_arreglaron"]
    assert _su_pregunta(conn, mundo, "Marcos")["tipo"] == "propuesta"
    # No espera respuesta: no abre ninguna espera.
    assert _esperas(conn, mundo, "Marcos") == 0

    r = _marcos_cuenta(equipo, at=AHORA + timedelta(minutes=150),
                       lo_que_dice="que llegue nomas, queda de repuesto")

    assert equipo.situacion["estado"]["pregunta_abierta"] == {
        "tipo": "propuesta", "tarea": "T1", "propone": ["contar_lo_que_arreglaron"],
        "opcional": True}
    assert hechos_mod.sin_significado(equipo.situacion["estado"]) == set()
    assert r.hechos[0]["cierra_el_tema"] is True
    cerrada = uno(conn, "select cierre from conversation_question where id = %s", oferta["id"])
    assert cerrada["cierre"] == "respondida"


def test_la_oferta_sin_respuesta_vence_sola(conn, mundo, equipo):
    """Sin respuesta es un no: Leda no insiste y la oferta se cierra sola, como las de una
    respuesta."""
    _a_marcos_le_llega_lo_que_dijo(conn, mundo, equipo)
    oferta = _la_oferta(conn, mundo, "Marcos")

    correr_escalera(conn, mundo["id"], RelojFijo(octubre(6, 10)))
    conn.commit()

    cerrada = uno(conn, "select cierre, cierre_detalle from conversation_question where id = %s",
                  oferta["id"])
    assert cerrada["cierre"] == "sin_efecto"
    assert cerrada["cierre_detalle"]["oferta_sin_respuesta"] is True
    assert avisos_guardados(conn, "repeticion_del_dia") == []


def test_con_otra_pregunta_abierta_la_oferta_no_deja_ninguna(conn, mundo, equipo):
    """Una pregunta que hace falta contestar nunca queda tapada por una opcional: Marcos tiene
    abierta la de quién destraba T2, así que el aviso no deja ninguna oferta, y lo que conteste
    se lee como hoy (sin límite de tiempo, `_contesta_lo_que_se_le_paso`)."""
    nueva_tarea(conn, mundo, COMUNICACIONES)
    _a_marcos_le_llega_lo_que_dijo(
        conn, mundo, equipo, Jugada("anotar_bloqueo", {"tarea": "T2", "causa": "la licencia"}))

    [_] = [a for a in avisos_guardados(conn, LO_QUE_DIJO) if a["estado"] == "enviado"
           and a["hechos"].get("se_lo_pasa_si_contesta")]
    assert _la_oferta(conn, mundo, "Marcos") is None
    assert _su_pregunta(conn, mundo, "Marcos")["tipo"] == "quien_destraba"

    r = _marcos_cuenta(equipo, at=AHORA + timedelta(minutes=150), tarea="T1",
                       lo_que_dice="que llegue nomas, queda de repuesto")

    assert r.hechos[0]["cierra_el_tema"] is True


def test_la_oferta_a_quien_destraba_tambien_deja_su_pregunta(conn, mundo, equipo):
    """Lo mismo del otro lado: lo que Marcos cuenta de lo acordado le llega a Ariel para que lo
    confirme, y lo que Ariel conteste se lee como respuesta a esa oferta."""
    _le_pregunto(conn, mundo, equipo)
    _ariel_dice(equipo, ya_lo_hablaron=True)
    _salir(conn, mundo, AHORA + timedelta(minutes=90))
    _marcos_cuenta(equipo, at=AHORA + timedelta(minutes=100), para_cuando="2026-10-08")
    _salir(conn, mundo, AHORA + timedelta(minutes=150))

    oferta = _la_oferta(conn, mundo, "Ariel")
    assert oferta is not None and oferta["cerrada_en"] is None
    assert str(oferta["task_id"]) == mundo["tarea"]
    assert oferta["jugada"]["propone"] == ["decir_cuando_destraba"]

    r = _ariel_dice(equipo, at=AHORA + timedelta(minutes=160), para_cuando="2026-10-09")

    assert equipo.situacion["estado"]["pregunta_abierta"]["propone"] == ["decir_cuando_destraba"]
    assert r.hechos[0]["resultado"] == "anotado"
    assert uno(conn, "select cierre from conversation_question where id = %s",
               oferta["id"])["cierre"] == "respondida"


def test_una_fecha_que_es_solo_informacion_no_deja_ninguna_oferta(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)
    _ariel_dice(equipo, para_cuando="2026-10-08")

    _salir(conn, mundo, AHORA + timedelta(minutes=90))

    assert avisos_guardados(conn, LO_QUE_DIJO)[0]["estado"] == "enviado"
    assert _la_oferta(conn, mundo, "Marcos") is None


# "No le escribas" después de que la pregunta salió (derivado de la 39 en la decisión 47).

def test_no_le_escribas_con_la_pregunta_abierta_deja_de_preguntarle_y_se_lo_dice(conn, mundo,
                                                                                equipo):
    _le_pregunto(conn, mundo, equipo)

    r = equipo.dice("Marcos", Jugada("no_escribirle", {"tarea": "T1"}))

    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["se_le_pregunta_a"] == {"a": ARIEL, "llega": "ya_le_llego", "el": "2026-10-05"}
    [avisado] = hecho["ya_no_hace_falta_que_destraben"]
    assert avisado["aviso_a_quien_destrababa"]["a"] == ARIEL
    assert _abiertas(conn, mundo, "Ariel") == 0
    assert _esperas(conn, mundo, "Ariel") == 0
    [aviso] = avisos_guardados(conn, YA_NO_HACE_FALTA)
    assert aviso["hechos"]["como_se_cerro"] == "dijo_que_ya_lo_hablaron"
    # Quién destraba sigue anotado y el bloqueo, abierto.
    assert cuantas(conn, "blocker_unblocker") == 1
    assert cuantas(conn, "blocker", "resuelto_en is null") == 1


# Corregir "no le escribas" anotado en la otra tarea (9f y 9n; ronda real del 2026-10-10,
# conversación 32: Marcos pidió no escribirle a Ariel por una tarea y quedó anotado en la otra, que
# también destraba Ariel; la corrección decía que no cambiaba nada).

COMUNICACIONES = "Probar las comunicaciones"
EQUIVOCADA = "se_anoto_en_la_tarea_equivocada"


def _trabada_tambien(conn, mundo, equipo) -> str:
    """Marcos se traba también con T2, que destraba Ariel: la id de T2."""
    t2 = nueva_tarea(conn, mundo, COMUNICACIONES)
    equipo.dice("Marcos", Jugada("anotar_bloqueo", {"tarea": "T2", "causa": "falta la licencia"}))
    equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"tarea": "T2", "quien": "ariel"}))
    return t2


def _pregunta_a_ariel(conn, task_id: str) -> dict:
    return uno(conn, "select * from scheduled_notice where tipo = %s and task_id = %s",
               PREGUNTA_A_QUIEN_DESTRABA, task_id)


def _corregir_a_t2(equipo, *mas: Jugada):
    return equipo.dice("Marcos", Jugada("corregir", {"corrige": "no_escribirle", "tarea": "T1",
                                                     "tarea_correcta": "T2"}), *mas)


def test_corregir_no_le_escribas_devuelve_el_mensaje_y_lo_retira_de_la_tarea_correcta(
        conn, mundo, equipo):
    """Ningún mensaje salió todavía: el de T1, retirado por error, vuelve a salir (terminado el
    margen de la corrección, que es algo que dijo Marcos); el de T2 queda retirado."""
    _trabada(equipo)
    t2 = _trabada_tambien(conn, mundo, equipo)
    equipo.dice("Marcos", Jugada("no_escribirle", {"tarea": "T1", "quien": "ariel"}))
    assert _pregunta_a_ariel(conn, mundo["tarea"])["estado"] == "omitido"

    r = _corregir_a_t2(equipo)

    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["tarea"]["titulo"]) == ("corregido", "Revisar el tablero")
    assert hecho["se_le_pregunta_a"] == {"a": ARIEL, "llega": "2026-10-05T10:16:00-03:00"}
    aplicado = hecho["aplicado"]
    assert (aplicado["resultado"], aplicado["tarea"]["titulo"]) == ("anotado", COMUNICACIONES)
    assert aplicado["se_le_pregunta_a"] == {"a": ARIEL, "llega": "no_le_va_a_llegar",
                                            "motivo": "pidio_que_no_le_escriba"}
    de_t1, de_t2 = _pregunta_a_ariel(conn, mundo["tarea"]), _pregunta_a_ariel(conn, t2)
    assert (de_t1["estado"], de_t1["motivo_omision"]) == ("guardado", None)
    assert de_t1["programado_para"] == AHORA + timedelta(minutes=6 + 10)
    assert (de_t2["estado"], de_t2["motivo_omision"]) == ("omitido", "pidio_que_no_le_escriba")
    # Nada se borra: la corrección queda auditada, junto a los dos "no le escribas".
    assert cuantas(conn, "audit_log", "accion = 'corregir_no_escribirle'") == 1
    assert cuantas(conn, "audit_log", "accion = 'no_escribirle'") == 2

    _salir(conn, mundo, AHORA + timedelta(minutes=20))

    assert cuantas(conn, "message_outbox", "destinatario_membership_id = %s",
                   _membresia(mundo, "Ariel")) == 1
    assert _su_pregunta(conn, mundo)["tarea"] == mundo["tarea"]


def test_corregir_no_le_escribas_vuelve_a_preguntarle_como_antes(conn, mundo, equipo):
    """La pregunta de T1 ya le había llegado y Leda le dejaba de preguntar: el aviso de que ya no
    hace falta, que todavía no salió, se retira, y su pregunta y su espera vuelven como estaban."""
    _le_pregunto(conn, mundo, equipo)
    _trabada_tambien(conn, mundo, equipo)
    equipo.dice("Marcos", Jugada("no_escribirle", {"tarea": "T1", "quien": "ariel"}))
    assert _abiertas(conn, mundo, "Ariel") == 0

    r = _corregir_a_t2(equipo)

    [hecho] = r.hechos
    assert hecho["resultado"] == "corregido"
    assert hecho["se_le_pregunta_a"] == {"a": ARIEL, "llega": "ya_le_llego", "el": "2026-10-05"}
    [avisado] = hecho["ya_no_hace_falta_que_destraben"]
    assert avisado["aviso_a_quien_destrababa"] == {"a": ARIEL, "llega": "no_le_va_a_llegar",
                                                   "motivo": EQUIVOCADA}
    [cerrado] = avisos_guardados(conn, YA_NO_HACE_FALTA)
    assert (cerrado["estado"], cerrado["motivo_omision"]) == ("omitido", EQUIVOCADA)
    assert _abiertas(conn, mundo, "Ariel", "cuando_se_destraba") == 1
    assert _esperas(conn, mundo, "Ariel") == 1
    assert _su_pregunta(conn, mundo)["tarea"] == mundo["tarea"]
    assert hecho["aplicado"]["se_le_pregunta_a"]["llega"] == "no_le_va_a_llegar"

    _salir(conn, mundo, AHORA + timedelta(minutes=60))

    assert avisos_guardados(conn, YA_NO_HACE_FALTA)[0]["estado"] == "omitido"


def test_corregir_y_pedir_lo_mismo_por_la_otra_en_el_mismo_mensaje(conn, mundo, equipo):
    """La ronda real: Ariel ya había dado un día por T1; "no le escribas" por T2 quedó en T1, y
    Marcos corrige y pide lo mismo por T1 en un mensaje. El aviso equivocado se retira y el de
    T1 se vuelve a guardar: la corrección no le quita su lugar."""
    _le_pregunto(conn, mundo, equipo)
    _ariel_dice(equipo, para_cuando="2026-10-06")
    t2 = _trabada_tambien(conn, mundo, equipo)
    equipo.dice("Marcos", Jugada("no_escribirle", {"tarea": "T1", "quien": "ariel"}))

    r = _corregir_a_t2(equipo, Jugada("no_escribirle", {"tarea": "T1", "quien": "ariel"}))

    corregido, otra_vez = r.hechos
    assert corregido["resultado"] == "corregido"
    assert corregido["aplicado"]["se_le_pregunta_a"]["llega"] == "no_le_va_a_llegar"
    assert _pregunta_a_ariel(conn, t2)["motivo_omision"] == "pidio_que_no_le_escriba"
    assert otra_vez["resultado"] == "anotado"
    [avisado] = otra_vez["ya_no_hace_falta_que_destraben"]
    assert avisado["aviso_a_quien_destrababa"]["a"] == ARIEL
    equivocado, vale = avisos_guardados(conn, YA_NO_HACE_FALTA)
    assert (equivocado["estado"], equivocado["motivo_omision"]) == ("omitido", EQUIVOCADA)
    assert vale["estado"] == "guardado"
    assert vale["hechos"]["habia_dicho"] == {"para_cuando": "2026-10-06"}


def _ya_le_llego_que_no_hace_falta(conn) -> None:
    with admin(conn) as cur:
        cur.execute("update scheduled_notice set estado = 'enviado', resuelto_en = %s "
                    "where tipo = %s", (AHORA + timedelta(minutes=34), YA_NO_HACE_FALTA))
    conn.commit()


def _la_que_se_lo_corrige(conn, mundo) -> list[dict]:
    """Lo que Leda le guarda a Ariel por T1 después de la corrección."""
    return [a for a in avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)
            if str(a["task_id"]) == mundo["tarea"] and ":n" in a["dedupe_key"]]


SIGUE = "aviso_de_que_sigue_haciendo_falta"
ERA_POR_OTRA = "lo_de_antes_era_por_otra_tarea"


def test_corregir_no_le_escribas_que_ya_le_llego_se_lo_corrige_y_le_vuelve_a_preguntar(
        conn, mundo, equipo):
    """Decisión 61: el aviso de que ya no hace falta ya le llegó a Ariel. No se hace como que no
    pasó (los hechos lo dicen): Leda le escribe que eso era por la otra tarea, que de ésta sigue
    haciendo falta, y le vuelve a hacer la misma pregunta, con su espera. La corrección pasa
    igual a la tarea correcta."""
    _le_pregunto(conn, mundo, equipo)
    t2 = _trabada_tambien(conn, mundo, equipo)
    pregunta = uno(conn, """select id from conversation_question
                             where tipo = 'cuando_se_destraba' and task_id = %s""",
                   mundo["tarea"])
    equipo.dice("Marcos", Jugada("no_escribirle", {"tarea": "T1", "quien": "ariel"}))
    _ya_le_llego_que_no_hace_falta(conn)

    r = _corregir_a_t2(equipo)

    [hecho] = r.hechos
    assert hecho["resultado"] == "corregido"
    [avisado] = hecho["ya_no_hace_falta_que_destraben"]
    assert avisado["aviso_a_quien_destrababa"] == {"a": ARIEL, "llega": "ya_le_llego",
                                                   "el": "2026-10-05"}
    [nuevo] = _la_que_se_lo_corrige(conn, mundo)
    assert nuevo["estado"] == "guardado"
    assert str(nuevo["destinatario_membership_id"]) == _membresia(mundo, "Ariel")
    # Le llega terminado el margen de la corrección, que es algo que dijo Marcos.
    assert nuevo["programado_para"] == AHORA + timedelta(minutes=34 + 10)
    assert hecho[SIGUE] == {"a": ARIEL, "llega": "2026-10-05T10:44:00-03:00"}
    assert hecho["se_le_pregunta_a"] == {"a": ARIEL, "llega": "2026-10-05T10:44:00-03:00"}
    assert nuevo["hechos"][ERA_POR_OTRA] == COMUNICACIONES
    assert nuevo["hechos"]["necesita_respuesta"] is True
    assert nuevo["hechos"]["pregunta"] == "cuando_se_destraba"
    assert (nuevo["hechos"]["tarea"], nuevo["hechos"]["responsable"]) == ("Revisar el tablero",
                                                                         "Marcos")
    assert hechos_mod.sin_significado(nuevo["hechos"]) == set()
    assert hechos_mod.sin_significado({k: v for k, v in hecho.items() if k != "efectos"}) == set()
    # Hasta que le llegue, Leda no le pregunta nada.
    assert _abiertas(conn, mundo, "Ariel", "cuando_se_destraba") == 0
    assert hecho["aplicado"]["resultado"] == "anotado"
    assert _pregunta_a_ariel(conn, t2)["motivo_omision"] == "pidio_que_no_le_escriba"
    assert cuantas(conn, "audit_log", "accion = 'corregir_no_escribirle'") == 1

    ia = _salir(conn, mundo, AHORA + timedelta(minutes=60))

    [nuevo] = _la_que_se_lo_corrige(conn, mundo)
    assert nuevo["estado"] == "enviado"
    [pedido] = [p for p in ia.pedidos_de_redaccion if p["persona"] == ARIEL]
    assert pedido["pregunta"]["tipo"] == "cuando_se_destraba"
    # La misma pregunta de antes, abierta otra vez, con su espera desde ahora.
    assert uno(conn, "select cerrada_en from conversation_question where id = %s",
               pregunta["id"])["cerrada_en"] is None
    assert _abiertas(conn, mundo, "Ariel", "cuando_se_destraba") == 1
    assert _su_pregunta(conn, mundo)["tarea"] == mundo["tarea"]
    assert _esperas(conn, mundo, "Ariel") == 1

    # El tema vuelve a estar abierto para Ariel: si se destraba, se entera (decisión 39).
    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}), at=AHORA + timedelta(minutes=70))
    ultimo = avisos_guardados(conn, YA_NO_HACE_FALTA)[-1]
    assert ultimo["estado"] == "guardado"
    assert ultimo["hechos"]["como_se_cerro"] == "ya_se_destrabo"


def test_corregir_que_ya_le_llego_con_un_dia_dado_se_lo_corrige_y_ese_dia_le_pregunta(
        conn, mundo, equipo):
    """La ronda real (la 32): Ariel ya había dado un día por T1, así que Leda no le preguntaba:
    le iba a preguntar ese día. Se le corrige sin preguntarle nada, con lo que había dicho, y la
    pregunta de ese día sale como antes."""
    _le_pregunto(conn, mundo, equipo)
    _ariel_dice(equipo, para_cuando="2026-10-08")
    _trabada_tambien(conn, mundo, equipo)
    equipo.dice("Marcos", Jugada("no_escribirle", {"tarea": "T1", "quien": "ariel"}))
    _ya_le_llego_que_no_hace_falta(conn)

    r = _corregir_a_t2(equipo)

    [hecho] = r.hechos
    assert hecho[SIGUE]["a"] == ARIEL
    assert "se_le_pregunta_a" not in hecho
    [nuevo] = _la_que_se_lo_corrige(conn, mundo)
    assert nuevo["hechos"]["necesita_respuesta"] is False
    assert "pregunta" not in nuevo["hechos"]
    assert nuevo["hechos"]["habia_dicho"] == {"para_cuando": "2026-10-08"}
    assert nuevo["hechos"][ERA_POR_OTRA] == COMUNICACIONES

    # Ariel habló hace poco (minuto 31): pasados los 30 minutos sin escribir (decisión 13).
    _salir(conn, mundo, AHORA + timedelta(minutes=70))

    assert _la_que_se_lo_corrige(conn, mundo)[0]["estado"] == "enviado"
    assert _abiertas(conn, mundo, "Ariel", "cuando_se_destraba") == 0
    _salir(conn, mundo, octubre(8, 10))
    [el_dia] = avisos_guardados(conn, "el_dia_que_dijo_quien_destraba")
    assert el_dia["estado"] == "enviado"
    assert _su_pregunta(conn, mundo)["tipo"] == "cuando_se_destraba"


def test_corregir_que_ya_le_llego_si_contesto_despues_no_se_le_vuelve_a_escribir(conn, mundo,
                                                                                equipo):
    """Ariel ya contestó algo después de que le llegó que no hacía falta: lo que dijo sigue su
    camino (le llega a Marcos) y Leda no le escribe otra vez; los hechos dicen que ya le llegó."""
    _le_pregunto(conn, mundo, equipo)
    _trabada_tambien(conn, mundo, equipo)
    equipo.dice("Marcos", Jugada("no_escribirle", {"tarea": "T1", "quien": "ariel"}))
    _ya_le_llego_que_no_hace_falta(conn)
    _ariel_dice(equipo, lo_que_dice="dale, igual ya lo pedi")

    r = _corregir_a_t2(equipo)

    [hecho] = r.hechos
    assert hecho["resultado"] == "corregido"
    assert SIGUE not in hecho and "se_le_pregunta_a" not in hecho
    [avisado] = hecho["ya_no_hace_falta_que_destraben"]
    assert avisado["aviso_a_quien_destrababa"]["llega"] == "ya_le_llego"
    assert _la_que_se_lo_corrige(conn, mundo) == []


def test_corregir_no_le_escribas_que_fallo_vuelve_a_preguntarle_como_antes(conn, mundo, equipo):
    """El aviso de que ya no hace falta falló (nunca le llegó a Ariel): es como si no hubiera
    salido. Su pregunta y su espera vuelven como estaban y Leda no le escribe nada; el aviso
    queda como estaba, fallido (nada se borra), y deja de contar como el cierre del tema."""
    _le_pregunto(conn, mundo, equipo)
    _trabada_tambien(conn, mundo, equipo)
    equipo.dice("Marcos", Jugada("no_escribirle", {"tarea": "T1", "quien": "ariel"}))
    with admin(conn) as cur:
        cur.execute("update scheduled_notice set estado = 'fallido', intentos = 5, "
                    "resuelto_en = %s where tipo = %s",
                    (AHORA + timedelta(minutes=34), YA_NO_HACE_FALTA))
    conn.commit()

    r = _corregir_a_t2(equipo)

    [hecho] = r.hechos
    assert hecho["resultado"] == "corregido"
    [avisado] = hecho["ya_no_hace_falta_que_destraben"]
    assert avisado["aviso_a_quien_destrababa"] == {"a": ARIEL, "llega": "no_le_llego"}
    assert hecho["se_le_pregunta_a"] == {"a": ARIEL, "llega": "ya_le_llego", "el": "2026-10-05"}
    assert SIGUE not in hecho
    assert _la_que_se_lo_corrige(conn, mundo) == []
    assert _abiertas(conn, mundo, "Ariel", "cuando_se_destraba") == 1
    assert _esperas(conn, mundo, "Ariel") == 1
    assert _su_pregunta(conn, mundo)["tarea"] == mundo["tarea"]
    [fallido] = avisos_guardados(conn, YA_NO_HACE_FALTA)
    assert fallido["estado"] == "fallido"

    # El tema vuelve a estar abierto para Ariel: si se destraba, se entera (decisión 39).
    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}))
    ultimo = avisos_guardados(conn, YA_NO_HACE_FALTA)[-1]
    assert ultimo["id"] != fallido["id"]
    assert (ultimo["estado"], ultimo["hechos"]["como_se_cerro"]) == ("guardado",
                                                                     "ya_se_destrabo")


def test_la_repeticion_que_no_salio_porque_se_cerro_no_corta_la_que_se_reabre(
        conn, espacio_con_escalera, equipo):
    """La repetición del martes 6 esperaba salir cuando "no le escribas" le cerró la pregunta a
    Ariel: no sale (ya no esperaba nada). La corrección se la reabre, y desde ahí la escalera la
    sigue repitiendo como a cualquier pregunta sin contestar (decisión 38): nunca se la abandona."""
    mundo = espacio_con_escalera
    _le_pregunto(conn, mundo, equipo)
    _trabada_tambien(conn, mundo, equipo)
    correr_escalera(conn, mundo["id"], RelojFijo(octubre(6, 10)))
    conn.commit()
    equipo.dice("Marcos", Jugada("no_escribirle", {"tarea": "T1", "quien": "ariel"}),
                at=octubre(6, 10, 5))
    _salir(conn, mundo, octubre(6, 10, 6))
    [no_salio] = [a for a in avisos_guardados(conn, "repregunta")
                  if str(a["task_id"]) == mundo["tarea"]]
    assert (no_salio["estado"], no_salio["motivo_omision"]) == ("omitido", "ya_respondio")
    equipo.minuto = int((octubre(6, 10, 6) - AHORA).total_seconds() // 60)
    _corregir_a_t2(equipo)              # a las 10:07 del martes 6
    assert _abiertas(conn, mundo, "Ariel", "cuando_se_destraba") >= 1

    _los_dias(conn, mundo, (7, 8, 9))

    de_t1 = [a for a in avisos_guardados(conn, "repregunta")
             if str(a["task_id"]) == mundo["tarea"]]
    assert len(de_t1) >= 2
    otra = de_t1[1]
    assert otra["estado"] == "enviado"
    assert str(otra["destinatario_membership_id"]) == _membresia(mundo, "Ariel")
    # La que no salió no se cuenta como un pedido que no le llegó: Leda la retiró.
    assert "pedidos_anteriores_que_no_le_llegaron" not in otra["hechos"]


def test_lo_de_antes_era_por_otra_tarea_tiene_su_significado():
    for codigo in (SIGUE, ERA_POR_OTRA):
        assert hechos_mod.significado(codigo), codigo


# Decisiones 47 y 48: lo acordado se confirma con el otro; "ya lo hablé" sin decir qué, a los dos.

def test_ya_lo_hablaron_sin_decir_que_tambien_le_pregunta_a_quien_esta_trabado(conn, mundo,
                                                                              equipo):
    _le_pregunto(conn, mundo, equipo)

    r = _ariel_dice(equipo, ya_lo_hablaron=True)

    [aviso] = avisos_guardados(conn, PREGUNTA_A_QUIEN_ESTA_TRABADO)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Marcos")
    assert aviso["programado_para"] == AHORA + timedelta(minutes=31 + 10)
    assert aviso["hechos"]["necesita_respuesta"] is True
    assert aviso["hechos"]["pregunta"] == "que_arreglaron"
    assert aviso["hechos"]["quien_destraba"] == ARIEL
    assert aviso["hechos"]["ya_lo_hablaron"] is True
    [hecho] = r.hechos
    assert hecho["le_pregunta_tambien_a"]["a"] == "Marcos"
    ia = _salir(conn, mundo, AHORA + timedelta(minutes=90))
    [pedido] = [p for p in ia.pedidos_de_redaccion if p["persona"] == "Marcos"]
    assert pedido["pregunta"]["tipo"] == "que_arreglaron"
    assert _su_pregunta(conn, mundo, "Marcos")["tipo"] == "que_arreglaron"
    assert cuantas(conn, "pending_reply", "membership_id = %s and tipo = 'que_arreglaron' "
                   "and satisfecho_en is null", _membresia(mundo, "Marcos")) == 1


def test_si_contesta_primero_quien_destraba_al_otro_no_se_le_pregunta_y_se_le_confirma(
        conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)
    _ariel_dice(equipo, ya_lo_hablaron=True)

    _ariel_dice(equipo, para_cuando="2026-10-08")

    [pregunta] = avisos_guardados(conn, PREGUNTA_A_QUIEN_ESTA_TRABADO)
    assert (pregunta["estado"], pregunta["motivo_omision"]) == ("omitido",
                                                               "ya_lo_conto_quien_destraba")
    [aviso] = avisos_guardados(conn, LO_QUE_DIJO)
    assert aviso["hechos"]["se_lo_pasa_si_contesta"] is True


def test_si_contesta_quien_destraba_despues_de_que_al_otro_le_llego_se_le_cierra(conn, mundo,
                                                                                 equipo):
    _le_pregunto(conn, mundo, equipo)
    _ariel_dice(equipo, ya_lo_hablaron=True)
    _salir(conn, mundo, AHORA + timedelta(minutes=90))

    _ariel_dice(equipo, at=AHORA + timedelta(minutes=100), para_cuando="2026-10-08")

    assert _abiertas(conn, mundo, "Marcos", "que_arreglaron") == 0
    assert _esperas(conn, mundo, "Marcos") == 0


def test_si_contesta_primero_quien_esta_trabado_vale_lo_suyo(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)
    _ariel_dice(equipo, ya_lo_hablaron=True)
    _salir(conn, mundo, AHORA + timedelta(minutes=90))

    r = _marcos_cuenta(equipo, at=AHORA + timedelta(minutes=100), para_cuando="2026-10-08")

    dicho = uno(conn, """select para_cuando::text p, dicho_por_membership_id::text quien
                           from dicho_de_quien_destraba""")
    assert dicho == {"p": "2026-10-08", "quien": _membresia(mundo, "Marcos")}
    assert cuantas(conn, "audit_log", "accion = 'anotar_lo_que_arreglaron'") == 1
    # Vale lo que contestó el primero: a los dos se les cierra la pregunta y la espera.
    assert _abiertas(conn, mundo, "Marcos") == 0
    assert _abiertas(conn, mundo, "Ariel") == 0
    assert _esperas(conn, mundo, "Marcos") == 0 and _esperas(conn, mundo, "Ariel") == 0
    [aviso] = avisos_guardados(conn, LO_QUE_DIJO_QUIEN_ESTA_TRABADO)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Ariel")
    assert aviso["hechos"]["se_lo_pasa_si_contesta"] is True
    assert "cierra_el_tema" not in aviso["hechos"]
    assert aviso["hechos"]["dice_quien_esta_trabado"] == {"para_cuando": "2026-10-08"}
    assert aviso["programado_para"] == AHORA + timedelta(minutes=100 + 10)
    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["aviso_a_quien_destraba"]["a"] == ARIEL
    assert "cierra_el_tema" not in hecho


def test_lo_acordado_le_llega_a_quien_esta_trabado_para_confirmarlo(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)

    _ariel_dice(equipo, ya_lo_hablaron=True, para_cuando="2026-10-08")

    [aviso] = avisos_guardados(conn, LO_QUE_DIJO)
    assert aviso["hechos"]["se_lo_pasa_si_contesta"] is True
    assert avisos_guardados(conn, PREGUNTA_A_QUIEN_ESTA_TRABADO) == []


def test_una_fecha_que_no_es_algo_acordado_es_solo_informacion(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)

    _ariel_dice(equipo, para_cuando="2026-10-08")

    [aviso] = avisos_guardados(conn, LO_QUE_DIJO)
    assert "se_lo_pasa_si_contesta" not in aviso["hechos"]
    assert "cierra_el_tema" not in aviso["hechos"]


def test_la_correccion_de_quien_esta_trabado_le_llega_y_cierra_el_tema(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)
    _ariel_dice(equipo, ya_lo_hablaron=True, para_cuando="2026-10-08")
    _salir(conn, mundo, AHORA + timedelta(minutes=90))

    r = _marcos_cuenta(equipo, at=AHORA + timedelta(minutes=100), para_cuando="2026-10-07",
                       lo_que_dice="no, quedamos el miercoles")

    [aviso] = avisos_guardados(conn, LO_QUE_DIJO_QUIEN_ESTA_TRABADO)
    assert aviso["hechos"]["cierra_el_tema"] is True
    assert "se_lo_pasa_si_contesta" not in aviso["hechos"]
    assert r.hechos[0]["cierra_el_tema"] is True


def test_la_correccion_de_quien_destraba_cierra_el_tema(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)
    _ariel_dice(equipo, ya_lo_hablaron=True)
    _salir(conn, mundo, AHORA + timedelta(minutes=90))
    _marcos_cuenta(equipo, at=AHORA + timedelta(minutes=100), para_cuando="2026-10-08")
    _salir(conn, mundo, AHORA + timedelta(minutes=150))

    r = _ariel_dice(equipo, at=AHORA + timedelta(minutes=160), para_cuando="2026-10-09")

    aviso = avisos_guardados(conn, LO_QUE_DIJO)[-1]
    assert aviso["hechos"]["cierra_el_tema"] is True
    assert "se_lo_pasa_si_contesta" not in aviso["hechos"]
    assert r.hechos[0]["resultado"] == "anotado"


def test_contar_lo_que_arreglaron_sin_quien_destraba_no_se_puede(conn, mundo, equipo):
    equipo.dice("Marcos", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": CAUSA}))

    r = _marcos_cuenta(equipo, tarea="T1", para_cuando="2026-10-08")

    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["motivo"]) == ("no_se_puede", "sin_quien_destraba")
    assert cuantas(conn, "dicho_de_quien_destraba") == 0


def test_contar_lo_que_arreglaron_sin_decir_nada_pregunta_que(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)

    r = _marcos_cuenta(equipo, tarea="T1")

    [hecho] = r.hechos
    assert hecho["resultado"] == "falta_dato"
    assert cuantas(conn, "dicho_de_quien_destraba") == 0


# "Se lo pido yo y te cuento" (la salida de la decisión 37).

def test_se_lo_pido_yo_no_le_escribe_a_nadie_y_pregunta_como_le_fue_al_dia_siguiente(
        conn, mundo, equipo):
    administrador(conn)
    _trabada(equipo, quien="mariano")

    r = equipo.dice("Marcos", Jugada("pedirselo_y_contar", {"tarea": "T1"}))

    # Las salidas se cierran: era una de ellas.
    assert cuantas(conn, "conversation_question",
                   "tipo = 'propuesta' and cerrada_en is null") == 0
    assert cuantas(conn, "audit_log", "accion = 'pedirselo_y_contar'") == 1
    assert avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA) == []
    [aviso] = avisos_guardados(conn, COMO_LE_FUE)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Marcos")
    # El día hábil siguiente, a la hora en que Leda escribe.
    assert aviso["programado_para"] == AHORA + timedelta(days=1)
    assert aviso["hechos"]["necesita_respuesta"] is True
    assert aviso["hechos"]["pregunta"] == "que_arreglaron"
    assert aviso["hechos"]["se_lo_pide_a"] == MARIANO
    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["se_lo_pide_a"] == MARIANO
    assert hecho["le_pregunta_como_le_fue"]["llega"].startswith("2026-10-06T10:00")
    assert r.pregunta is None


def test_se_lo_pido_yo_retira_el_mensaje_que_todavia_no_salio(conn, mundo, equipo):
    _trabada(equipo)

    equipo.dice("Marcos", Jugada("pedirselo_y_contar", {"tarea": "T1"}))

    [aviso] = avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido",
                                                         "se_lo_pide_quien_esta_trabado")
    assert avisos_guardados(conn, YA_NO_HACE_FALTA) == []


def test_se_lo_pido_yo_despues_de_que_le_llego_le_cierra_el_tema(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)

    equipo.dice("Marcos", Jugada("pedirselo_y_contar", {"tarea": "T1"}))

    [aviso] = avisos_guardados(conn, YA_NO_HACE_FALTA)
    assert aviso["hechos"]["como_se_cerro"] == "se_lo_pide_quien_esta_trabado"
    assert _abiertas(conn, mundo, "Ariel") == 0
    assert _esperas(conn, mundo, "Ariel") == 0


# Decisión 64: "se lo pido yo" no anula el día que ya dio quien destraba.

EL_DIA = "el_dia_que_dijo_quien_destraba"


def _ariel_dio_el_jueves_y_marcos_se_lo_pide(conn, mundo, equipo) -> None:
    _le_pregunto(conn, mundo, equipo)
    _ariel_dice(equipo, para_cuando="2026-10-08")
    equipo.dice("Marcos", Jugada("pedirselo_y_contar", {"tarea": "T1"}),
                at=AHORA + timedelta(minutes=60))


def _lo_que_se_le_redacta_a_ariel(ia: IAQueRedacta) -> dict:
    [pedido] = [p for p in ia.pedidos_de_redaccion if p["persona"] == ARIEL]
    [hechos] = pedido["hechos"]
    return hechos


def test_se_lo_pido_yo_despues_del_dia_que_dio_no_le_cierra_el_tema(conn, mundo, equipo):
    """Ariel ya dio un día: es un compromiso suyo, registrado. Que Marcos diga que se lo pide él
    no se lo cierra ni le retira la pregunta de ese día; a Marcos le pregunta cómo le fue."""
    _ariel_dio_el_jueves_y_marcos_se_lo_pide(conn, mundo, equipo)

    assert avisos_guardados(conn, YA_NO_HACE_FALTA) == []
    [el_dia] = avisos_guardados(conn, EL_DIA)
    assert el_dia["estado"] == "guardado"
    [como] = avisos_guardados(conn, COMO_LE_FUE)
    assert str(como["destinatario_membership_id"]) == _membresia(mundo, "Marcos")


def test_el_dia_que_dio_le_pregunta_igual_y_le_cuenta_que_marcos_se_lo_iba_a_pedir(conn, mundo,
                                                                                   equipo):
    """Decisión 64, con el ajuste del usuario: el jueves Leda le pregunta a Ariel si pudo, y le
    cuenta que Marcos dijo que se lo pedía él directamente, para que entienda por qué le
    pregunta. Nada sobre si Marcos le confirmó a Leda que habló con él."""
    _ariel_dio_el_jueves_y_marcos_se_lo_pide(conn, mundo, equipo)
    _salir(conn, mundo, octubre(6, 10))
    [como] = avisos_guardados(conn, COMO_LE_FUE)
    assert como["estado"] == "enviado"

    ia = _salir(conn, mundo, octubre(8, 10))

    [el_dia] = avisos_guardados(conn, EL_DIA)
    assert el_dia["estado"] == "enviado"
    hechos = _lo_que_se_le_redacta_a_ariel(ia)
    assert hechos["aviso"] == EL_DIA
    assert hechos["dijo_que_se_lo_pedia"] == "Marcos"
    assert hechos["habia_dicho"]["para_cuando"] == "2026-10-08"
    assert _su_pregunta(conn, mundo)["tipo"] == "cuando_se_destraba"
    assert hechos_mod.significado("dijo_que_se_lo_pedia")


def test_el_dia_que_dio_sin_se_lo_pido_yo_no_lo_menciona(conn, mundo, equipo):
    _le_pregunto(conn, mundo, equipo)
    _ariel_dice(equipo, para_cuando="2026-10-08")

    ia = _salir(conn, mundo, octubre(8, 10))

    assert "dijo_que_se_lo_pedia" not in _lo_que_se_le_redacta_a_ariel(ia)


def test_se_lo_pido_yo_antes_del_dia_que_dio_despues_no_lo_menciona(conn, mundo, equipo):
    """Si Marcos dijo que se lo pedía y después Ariel dio un día, eso que dijo Marcos ya no
    explica nada: Ariel habló con Leda después."""
    _le_pregunto(conn, mundo, equipo)
    equipo.dice("Marcos", Jugada("pedirselo_y_contar", {"tarea": "T1"}))
    _ariel_dice(equipo, para_cuando="2026-10-08")

    ia = _salir(conn, mundo, octubre(8, 10))

    assert "dijo_que_se_lo_pedia" not in _lo_que_se_le_redacta_a_ariel(ia)


def test_se_lo_pido_yo_sin_un_dia_dado_deja_de_escribirle(conn, espacio_con_escalera, equipo):
    """Decisión 37, sin cambios: Ariel no se comprometió a nada; con "se lo pido yo" Leda deja de
    preguntarle y no le repite nada. A Marcos sí le pregunta cómo le fue."""
    mundo = espacio_con_escalera
    _le_pregunto(conn, mundo, equipo)

    equipo.dice("Marcos", Jugada("pedirselo_y_contar", {"tarea": "T1"}))
    _los_dias(conn, mundo, (6, 7, 8))

    assert avisos_guardados(conn, EL_DIA) == []
    [cerrado] = avisos_guardados(conn, YA_NO_HACE_FALTA)
    assert str(cerrado["destinatario_membership_id"]) == _membresia(mundo, "Ariel")
    assert [r["a"] for r in _repreguntas(conn)] == [_membresia(mundo, "Marcos")] * 2
    [como] = avisos_guardados(conn, COMO_LE_FUE)
    assert como["estado"] == "enviado"


def test_la_pregunta_de_como_le_fue_nunca_se_abandona(conn, espacio_con_escalera, equipo):
    """Al salir abre la pregunta de lo que arregló, con su espera; si no contesta, la escalera de
    las preguntas se la repite sin escalar (decisión 38)."""
    mundo = espacio_con_escalera
    _trabada(equipo, quien="mariano")
    equipo.dice("Marcos", Jugada("pedirselo_y_contar", {"tarea": "T1"}))

    _los_dias(conn, mundo, (6,))

    assert _su_pregunta(conn, mundo, "Marcos")["tipo"] == "que_arreglaron"
    assert cuantas(conn, "pending_reply", "membership_id = %s and tipo = 'que_arreglaron' "
                   "and satisfecho_en is null", _membresia(mundo, "Marcos")) == 1
    _los_dias(conn, mundo, (7, 8))
    repreguntas = _repreguntas(conn)
    assert [r["a"] for r in repreguntas] == [_membresia(mundo, "Marcos")] * 2
    assert cuantas(conn, "scheduled_notice", "tipo = 'escalamiento_de_una_pregunta'") == 0


def test_lo_que_cuenta_de_como_le_fue_queda_anotado(conn, mundo, equipo):
    _trabada(equipo, quien="mariano")
    equipo.dice("Marcos", Jugada("pedirselo_y_contar", {"tarea": "T1"}))
    _salir(conn, mundo, AHORA + timedelta(days=1))

    r = _marcos_cuenta(equipo, at=AHORA + timedelta(days=1, minutes=40),
                       para_cuando="2026-10-09")

    dicho = uno(conn, """select d.para_cuando::text p, d.dicho_por_membership_id::text quien,
                                u.destraba_membership_id::text destraba
                           from dicho_de_quien_destraba d
                           join blocker_unblocker u on u.id = d.blocker_unblocker_id""")
    assert dicho == {"p": "2026-10-09", "quien": _membresia(mundo, "Marcos"),
                     "destraba": _membresia(mundo, "Mariano")}
    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["no_se_le_puede_escribir_a"] == {"a": MARIANO,
                                                  "motivo": "destinatario_sin_telegram"}
    assert "aviso_a_quien_destraba" not in hecho
    assert _abiertas(conn, mundo, "Marcos") == 0
    assert _esperas(conn, mundo, "Marcos") == 0


def test_si_se_destraba_antes_la_pregunta_de_como_le_fue_no_sale(conn, mundo, equipo):
    _trabada(equipo, quien="mariano")
    equipo.dice("Marcos", Jugada("pedirselo_y_contar", {"tarea": "T1"}))
    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}))

    _salir(conn, mundo, AHORA + timedelta(days=1))

    [aviso] = avisos_guardados(conn, COMO_LE_FUE)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "ya_se_destrabo")


def test_las_jugadas_y_los_codigos_de_la_c5c_tienen_sus_significados():
    from leda.motor import preguntas as preguntas_mod
    for nombre in ("contar_lo_que_arreglaron", "pedirselo_y_contar"):
        ficha = FICHAS[nombre]
        assert ficha.es and not ficha.se_ofrece
        for dato in ficha.necesita + ficha.opcional:
            assert dato in DATOS, (nombre, dato)
        assert nombre in hechos_mod.PARA_LA_REDACCION
    assert preguntas_mod.TIPOS["que_arreglaron"].escala is False
    assert preguntas_mod.TIPOS["que_arreglaron"].espera == "que_arreglaron"
    for codigo in ("que_arreglaron", PREGUNTA_A_QUIEN_ESTA_TRABADO, COMO_LE_FUE,
                   LO_QUE_DIJO_QUIEN_ESTA_TRABADO, YA_NO_HACE_FALTA, "se_lo_pasa_si_contesta",
                   "cierra_el_tema", "como_se_cerro", "habia_dicho", "dijo_que_ya_lo_hablaron",
                   "se_lo_pide_quien_esta_trabado", "ya_no_hace_falta_que_destraben",
                   "aviso_a_quien_destrababa", "quien_esta_trabado", "dice_quien_esta_trabado",
                   "aviso_a_quien_destraba", "le_pregunta_tambien_a", "ya_se_habia_destrabado",
                   "ya_no_hace_falta_que_la_destrabe", "se_lo_pide_a", "le_pregunta_como_le_fue",
                   "ya_lo_conto_quien_destraba", "ya_lo_conto_quien_esta_trabado",
                   "sin_quien_destraba", "volvio_a_ser_quien_destraba",
                   "no_sabe_quien_destraba", "nadie_mas_puede_destrabar",
                   "dijo_que_se_lo_pedia"):
        assert hechos_mod.significado(codigo), codigo
