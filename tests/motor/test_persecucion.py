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
                                   cuantas, enviar, octubre, todos, uno)
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


def test_no_le_escribas_despues_de_que_salio_dice_que_ya_le_llego(conn, mundo, equipo):
    """Ariel ya contestó: Leda no le está preguntando nada, así que no hay nada que retirar ni
    que cerrarle (con la pregunta todavía abierta, ver la C-5c, abajo)."""
    _le_pregunto(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                {"tarea": "T1", "para_cuando": "2026-10-06"}))

    r = equipo.dice("Marcos", Jugada("no_escribirle", {"tarea": "T1"}))

    [aviso] = avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)
    assert aviso["estado"] == "enviado"
    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["motivo"]) == ("no_se_puede", "ya_se_le_escribio")
    assert hecho["se_le_pregunta_a"] == {"a": ARIEL, "llega": "ya_le_llego",
                                         "el": "2026-10-05"}


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


def test_a_quien_dijo_que_ya_esta_no_se_le_cierra_nada(conn, mundo, equipo):
    """Lo cerró él: ya sabe cómo terminó."""
    _le_pregunto(conn, mundo, equipo)
    _ariel_dice(equipo, ya_esta=True)

    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}))

    assert avisos_guardados(conn, YA_NO_HACE_FALTA) == []


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
    assert aviso["hechos"]["como_se_cerro"] == "cambio_quien_destraba"


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
                   "sin_quien_destraba", "volvio_a_ser_quien_destraba"):
        assert hechos_mod.significado(codigo), codigo
