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

from tests.motor.ayudantes import (AHORA, IAQueRedacta, avisos_guardados, cuantas, enviar,
                                   octubre, todos, uno)
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


def test_la_pregunta_se_repite_el_dia_habil_siguiente_sin_escalar(conn, espacio_con_escalera,
                                                                    equipo):
    mundo = espacio_con_escalera
    _trabada(equipo)
    _salir(conn, mundo, AHORA + timedelta(minutes=12))
    ariel = _membresia(mundo, "Ariel")
    ia = IAQueRedacta()

    redactados = []
    # Martes 6, miércoles 7, jueves 8 y viernes 9 a las 10:00.
    for dia in (6, 7, 8, 9):
        correr_escalera(conn, mundo["id"], RelojFijo(octubre(dia, 10)))
        conn.commit()
        from leda.motor.avisos import enviar_avisos
        enviar_avisos(conn, mundo["id"], ia, RelojFijo(octubre(dia, 10)))
        conn.commit()
        redactados.append(list(ia.pedidos_de_redaccion))
        ia.pedidos_de_redaccion.clear()

    repreguntas = todos(conn, """select destinatario_membership_id::text a, hechos
                                   from scheduled_notice where tipo = 'repregunta'
                                  order by creado_en""")
    assert [r["a"] for r in repreguntas] == [ariel, ariel]
    assert all("avisa_que_va_a_escalar" not in r["hechos"] for r in repreguntas)
    assert all("si_no_hay_respuesta" not in r["hechos"] for r in repreguntas)
    assert cuantas(conn, "scheduled_notice", "tipo = 'escalamiento_de_una_pregunta'") == 0
    # Lo que se repite dice quién está trabado y por qué.
    assert repreguntas[0]["hechos"]["sobre"]["responsable"] == "Marcos"
    assert repreguntas[0]["hechos"]["sobre"]["causa"] == CAUSA


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
    _le_pregunto(conn, mundo, equipo)

    r = equipo.dice("Marcos", Jugada("no_escribirle", {"tarea": "T1"}))

    [aviso] = avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)
    assert aviso["estado"] == "enviado"
    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["motivo"]) == ("no_se_puede", "ya_se_le_escribio")
    assert hecho["se_le_pregunta_a"] == {"a": ARIEL, "llega": "ya_le_llego",
                                         "el": "2026-10-05"}


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
                   "no_le_toca_destrabarla"):
        assert hechos_mod.significado(codigo), codigo
