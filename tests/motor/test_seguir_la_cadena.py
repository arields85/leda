"""Leda sigue la cadena hasta quien puede destrabarla (C-5e; decisión 42 del usuario, 2026-10-09;
`leda.motor.encadenados` y `leda.motor.persecucion`; conversación 44).

Si quien Marcos nombra como quien destraba (Ariel) ya está trabado con lo que le falta a Marcos (la
tarea de Marcos depende de una de Ariel, que tiene un bloqueo abierto), Leda no le pide a Ariel lo
que no puede dar: se lo cuenta enseguida a Marcos, con quién destraba a Ariel y lo que ya dijo, y
Marcos se entera de cada avance (decisión 6). Cuando Ariel puede seguir, ahora sí puede dar lo que
falta: Leda le pregunta para cuándo. Y a quien destraba y da un día, el día de esa fecha Leda le
vuelve a preguntar si ya está, con la regla de la decisión 38 si no contesta: una sola regla, para
cualquiera que destraba.
"""

from __future__ import annotations

from datetime import timedelta

from leda.motor import hechos as hechos_mod
from leda.motor.avisos import TIPOS
from leda.motor.escalera import correr_escalera
from leda.motor.ia import Jugada
from leda.motor.tiempo import RelojFijo

from tests.motor.ayudantes import AHORA, avisos_guardados, cuantas, octubre, todos, uno
from tests.motor.test_bloqueos_encadenados import (  # noqa: F401 -- fixtures
    ARIEL, CAUSA, JUAN, LUCAS, SERVIDOR, SWITCH, TABLERO, _tarea_de, equipo, servidor)
from tests.motor.test_cadena_del_bloqueo import _membresia, _salir, _su_pregunta

PREGUNTA = "pregunta_a_quien_destraba"
EL_DIA = "el_dia_que_dijo_quien_destraba"
COMPRAS = "Comprar el switch"
PROVEEDOR = "falta que el proveedor confirme"


def _ariel_trabado(t, *, lucas_dice: dict | None = None) -> None:
    """Ariel está trabado con el servidor (la tarea previa de la de Marcos) y lo destraba Lucas;
    con `lucas_dice`, lo que contestó Lucas."""
    t.dice("Ariel", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": SWITCH}))
    t.dice("Ariel", Jugada("anotar_quien_destraba", {"quien": "lucas"}))
    if lucas_dice is not None:
        t.dice("Lucas", Jugada("decir_cuando_destraba", {"tarea": "T1", **lucas_dice}))


def _marcos_nombra_a_ariel(t):
    t.dice("Marcos", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": CAUSA}))
    return t.dice("Marcos", Jugada("anotar_quien_destraba", {"quien": "ariel"}))


def _preguntas_a(conn, mundo, corto: str, tipo: str = PREGUNTA) -> list[dict]:
    return [a for a in avisos_guardados(conn, tipo)
            if str(a["destinatario_membership_id"]) == _membresia(mundo, corto)]


# --- La lista cerrada y el vocabulario --------------------------------------------------------

def test_el_aviso_y_los_hechos_nuevos_estan_declarados_con_su_significado():
    tipo = TIPOS[EL_DIA]
    assert tipo.tipo_de_mensaje == "seguimiento" and tipo.abre is not None
    assert not tipo.es_coordinacion
    for codigo in (EL_DIA, "ya_esta_trabado", "se_entera_de_cada_avance",
                   "dice_quien_lo_destraba", "lo_esperan", "le_pregunta_para_cuando",
                   "le_vuelve_a_preguntar"):
        assert hechos_mod.significado(codigo), codigo


# --- No le pide lo que no puede dar -----------------------------------------------------------

def test_a_quien_ya_esta_trabado_con_lo_que_falta_no_se_le_pregunta(conn, mundo, servidor,
                                                                    equipo):
    _ariel_trabado(equipo)

    r = _marcos_nombra_a_ariel(equipo)

    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert "se_le_pregunta_a" not in hecho
    assert hecho["ya_esta_trabado"] == {
        "a": ARIEL, "se_entera_de_cada_avance": True,
        "esperando_a": [{"de": ARIEL, "tarea": SERVIDOR, "causa": SWITCH, "lo_destraba": LUCAS}]}
    # Queda anotado que lo destraba Ariel (así Marcos espera lo de Ariel, decisión 6), pero a
    # Ariel no se le guarda ninguna pregunta por lo de Marcos.
    assert uno(conn, """select u.destraba_membership_id::text d from blocker_unblocker u
                          join blocker b on b.id = u.blocker_id
                         where b.task_id = %s""", mundo["tarea"])["d"] == _membresia(mundo,
                                                                                     "Ariel")
    assert _preguntas_a(conn, mundo, "Ariel") == []
    _salir(conn, mundo, AHORA + timedelta(hours=2))
    assert _su_pregunta(conn, mundo, "Ariel") is None


def test_cuenta_lo_que_ya_dijo_quien_lo_destraba(conn, mundo, servidor, equipo):
    _ariel_trabado(equipo, lucas_dice={"para_cuando": "2026-10-08"})

    r = _marcos_nombra_a_ariel(equipo)

    [paso] = r.hechos[0]["ya_esta_trabado"]["esperando_a"]
    assert paso["lo_destraba"] == LUCAS
    assert paso["dice_quien_lo_destraba"] == {"para_cuando": "2026-10-08"}


def test_quien_espera_se_entera_de_cada_avance(conn, mundo, servidor, equipo):
    _ariel_trabado(equipo)
    _marcos_nombra_a_ariel(equipo)

    equipo.dice("Lucas", Jugada("decir_cuando_destraba",
                                {"tarea": "T1", "para_cuando": "2026-10-08"}))

    [novedad] = [a for a in avisos_guardados(conn, "novedad_de_lo_que_espera")
                 if str(a["destinatario_membership_id"]) == _membresia(mundo, "Marcos")]
    assert novedad["hechos"]["novedad"]["dice_quien_destraba"] == {"para_cuando": "2026-10-08"}


def test_sigue_la_cadena_mas_arriba(conn, mundo, servidor, equipo):
    """Lucas, que destraba a Ariel, también está trabado con lo que le falta a Ariel (la tarea de
    Ariel depende de una de Lucas): la cadena sigue hasta quien puede destrabarla, Juan."""
    _tarea_de(conn, mundo, "Lucas", COMPRAS, depende=servidor)
    equipo.dice("Lucas", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": PROVEEDOR}))
    equipo.dice("Lucas", Jugada("anotar_quien_destraba", {"quien": "juan"}))
    _ariel_trabado(equipo)

    r = _marcos_nombra_a_ariel(equipo)

    assert r.hechos[0]["ya_esta_trabado"]["esperando_a"] == [
        {"de": ARIEL, "tarea": SERVIDOR, "causa": SWITCH, "lo_destraba": LUCAS},
        {"de": LUCAS, "tarea": COMPRAS, "causa": PROVEEDOR, "lo_destraba": JUAN}]
    assert _preguntas_a(conn, mundo, "Ariel") == []


def test_trabado_con_otra_cosa_se_le_pregunta_igual(conn, mundo, equipo):
    """Sin la dependencia cargada, lo que traba a Ariel no es lo que le falta a Marcos: nunca por
    adivinar."""
    _tarea_de(conn, mundo, "Ariel", SERVIDOR)
    _ariel_trabado(equipo)

    r = _marcos_nombra_a_ariel(equipo)

    assert "ya_esta_trabado" not in r.hechos[0]
    assert r.hechos[0]["se_le_pregunta_a"]["a"] == ARIEL
    assert len(_preguntas_a(conn, mundo, "Ariel")) == 1


def test_trabado_con_lo_que_falta_dicho_por_quien_no_lo_toma_tampoco(conn, mundo, servidor,
                                                                     equipo):
    """En la cadena de "no me corresponde" (decisión 51) vale lo mismo: si a quien nombran ya está
    trabado con lo que falta, no se le pregunta, y la persona trabada se entera, sin que la cadena
    se corte."""
    _ariel_trabado(equipo)
    equipo.dice("Marcos", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": CAUSA}))
    equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"quien": "juan"}))
    _salir(conn, mundo, AHORA + timedelta(minutes=30))
    equipo.minuto = 40

    r = equipo.dice("Juan", Jugada("decir_que_no_le_toca", {"quien": "ariel"}))

    assert "ya_esta_trabado" in r.hechos[0]
    assert _preguntas_a(conn, mundo, "Ariel") == []
    assert avisos_guardados(conn, "cadena_del_bloqueo") == []
    [a_marcos] = [a for a in avisos_guardados(conn, "lo_que_dijo_quien_destraba")
                  if str(a["destinatario_membership_id"]) == _membresia(mundo, "Marcos")]
    assert a_marcos["hechos"]["ya_esta_trabado"]["a"] == ARIEL


# --- Cuando puede seguir, ahora sí ------------------------------------------------------------

def test_cuando_puede_seguir_se_le_pregunta_para_cuando(conn, mundo, servidor, equipo):
    _ariel_trabado(equipo)
    _marcos_nombra_a_ariel(equipo)

    r = equipo.dice("Ariel", Jugada("destrabar", {"tarea": "T1"}))

    [pregunta] = _preguntas_a(conn, mundo, "Ariel")
    assert str(pregunta["task_id"]) == mundo["tarea"]
    assert pregunta["hechos"]["responsable"] == "Marcos"
    assert pregunta["hechos"]["causa"] == CAUSA
    [item] = r.hechos[0]["lo_esperan"]
    assert item["le_pregunta_para_cuando"]["responsable"] == "Marcos"
    assert item["le_pregunta_para_cuando"]["tarea"] == TABLERO
    # Le llega pasada la media hora en que estuvo conversando (no interrumpir).
    ia = _salir(conn, mundo, AHORA + timedelta(hours=2))
    assert [h for p in ia.pedidos_de_redaccion if p["persona"] == ARIEL
            for h in p["hechos"] if h.get("aviso") == PREGUNTA]
    assert _su_pregunta(conn, mundo, "Ariel")["tipo"] == "cuando_se_destraba"
    assert _su_pregunta(conn, mundo, "Ariel")["tarea"] == mundo["tarea"]


def test_si_ya_le_habian_preguntado_antes_de_trabarse_se_le_vuelve_a_preguntar(conn, mundo,
                                                                               servidor, equipo):
    """Marcos lo nombró cuando todavía no estaba trabado; Ariel se trabó con eso (su pregunta se
    cerró) y ahora puede seguir: la pregunta vuelve a salir, otra, no la vieja."""
    _marcos_nombra_a_ariel(equipo)
    _salir(conn, mundo, AHORA + timedelta(minutes=12))
    equipo.minuto = 30
    _ariel_trabado(equipo)

    equipo.dice("Ariel", Jugada("destrabar", {"tarea": "T1"}))

    preguntas = _preguntas_a(conn, mundo, "Ariel")
    assert [p["estado"] for p in preguntas] == ["enviado", "guardado"]
    _salir(conn, mundo, AHORA + timedelta(hours=3))
    assert _su_pregunta(conn, mundo, "Ariel")["tipo"] == "cuando_se_destraba"


def test_si_lo_dice_antes_de_que_le_llegue_la_pregunta_no_sale(conn, mundo, servidor, equipo):
    _ariel_trabado(equipo)
    _marcos_nombra_a_ariel(equipo)
    equipo.dice("Ariel", Jugada("destrabar", {"tarea": "T1"}))

    equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                {"tarea": "T2", "para_cuando": "2026-10-06"}))
    _salir(conn, mundo, AHORA + timedelta(hours=3))

    [pregunta] = _preguntas_a(conn, mundo, "Ariel")
    assert (pregunta["estado"], pregunta["motivo_omision"]) == ("omitido", "ya_respondio")


def test_si_sigue_trabado_con_otra_tarea_previa_no_se_le_pregunta(conn, mundo, servidor, equipo):
    """Ariel destraba una tarea suya, pero otra que también le falta a Marcos sigue trabada."""
    otra = _tarea_de(conn, mundo, "Ariel", "Configurar la red", depende=mundo["tarea"])
    _ariel_trabado(equipo)
    equipo.dice("Ariel", Jugada("anotar_bloqueo", {"tarea": "T2", "causa": "falta un cable"}))
    _marcos_nombra_a_ariel(equipo)

    equipo.dice("Ariel", Jugada("destrabar", {"tarea": "T1"}))

    assert otra
    assert _preguntas_a(conn, mundo, "Ariel") == []


# --- El día que dijo, otra vez ----------------------------------------------------------------

def test_el_dia_que_dijo_se_le_vuelve_a_preguntar(conn, mundo, servidor, equipo):
    _ariel_trabado(equipo)

    r = equipo.dice("Lucas", Jugada("decir_cuando_destraba",
                                    {"tarea": "T1", "para_cuando": "2026-10-07",
                                     "lo_que_dice": "llega el miercoles"}))

    [aviso] = _preguntas_a(conn, mundo, "Lucas", EL_DIA)
    assert aviso["programado_para"] == octubre(7, 10)
    assert str(aviso["task_id"]) == servidor
    assert aviso["hechos"]["necesita_respuesta"] is True
    assert aviso["hechos"]["pregunta"] == "cuando_se_destraba"
    assert aviso["hechos"]["responsable"] == ARIEL and aviso["hechos"]["causa"] == SWITCH
    assert aviso["hechos"]["habia_dicho"] == {"para_cuando": "2026-10-07",
                                              "lo_que_dice": "llega el miercoles"}
    assert r.hechos[0]["le_vuelve_a_preguntar"]["llega"] == octubre(7, 10).isoformat()

    # El día anterior, nada; ese día, la pregunta, con su espera.
    _salir(conn, mundo, octubre(6, 11))
    assert _preguntas_a(conn, mundo, "Lucas", EL_DIA)[0]["estado"] == "guardado"
    _salir(conn, mundo, octubre(7, 10))
    assert _preguntas_a(conn, mundo, "Lucas", EL_DIA)[0]["estado"] == "enviado"
    pregunta = _su_pregunta(conn, mundo, "Lucas")
    assert (pregunta["tipo"], pregunta["tarea"]) == ("cuando_se_destraba", servidor)
    assert cuantas(conn, "pending_reply", "membership_id = %s and tipo = 'cuando_se_destraba' "
                   "and satisfecho_en is null", _membresia(mundo, "Lucas")) == 1


def test_lo_que_contesta_ese_dia_queda_anotado_y_se_cierra_la_pregunta(conn, mundo, servidor,
                                                                      equipo):
    _ariel_trabado(equipo, lucas_dice={"para_cuando": "2026-10-07"})
    _salir(conn, mundo, octubre(7, 10))

    equipo.dice("Lucas", Jugada("decir_cuando_destraba", {"ya_esta": True}),
                at=octubre(7, 11))

    assert _su_pregunta(conn, mundo, "Lucas") is None
    assert uno(conn, "select count(*) n from dicho_de_quien_destraba where ya_esta")["n"] == 1
    # Ya está: no hay otro día que preguntar.
    assert len(_preguntas_a(conn, mundo, "Lucas", EL_DIA)) == 1


def test_si_no_contesta_rige_la_regla_de_quien_no_contesta(conn, espacio_con_escalera, servidor,
                                                           equipo):
    """Decisión 38: la pregunta del día se repite el día hábil siguiente, sin escalar."""
    mundo = espacio_con_escalera
    _ariel_trabado(equipo, lucas_dice={"para_cuando": "2026-10-07"})
    _salir(conn, mundo, octubre(7, 10))

    correr_escalera(conn, mundo["id"], RelojFijo(octubre(8, 10)))
    conn.commit()

    [repregunta] = todos(conn, """select destinatario_membership_id::text a, hechos
                                    from scheduled_notice where tipo = 'repregunta'""")
    assert repregunta["a"] == _membresia(mundo, "Lucas")
    assert repregunta["hechos"]["pregunta"] == "cuando_se_destraba"
    assert not repregunta["hechos"].get("avisa_que_va_a_escalar")


def test_si_dijo_algo_mas_nuevo_no_sale(conn, mundo, servidor, equipo):
    _ariel_trabado(equipo, lucas_dice={"para_cuando": "2026-10-07"})
    equipo.dice("Lucas", Jugada("decir_cuando_destraba",
                                {"tarea": "T1", "lo_que_dice": "el proveedor no contesta"}))

    _salir(conn, mundo, octubre(7, 10))

    [aviso] = _preguntas_a(conn, mundo, "Lucas", EL_DIA)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "dijo_algo_mas_nuevo")


def test_un_dia_nuevo_reemplaza_al_anterior(conn, mundo, servidor, equipo):
    _ariel_trabado(equipo, lucas_dice={"para_cuando": "2026-10-07"})
    equipo.dice("Lucas", Jugada("decir_cuando_destraba",
                                {"tarea": "T1", "para_cuando": "2026-10-09"}))

    _salir(conn, mundo, octubre(9, 10))

    primero, segundo = _preguntas_a(conn, mundo, "Lucas", EL_DIA)
    assert (primero["estado"], primero["motivo_omision"]) == ("omitido", "dijo_algo_mas_nuevo")
    assert segundo["programado_para"] == octubre(9, 10) and segundo["estado"] == "enviado"


def test_si_se_destrabo_no_sale(conn, mundo, servidor, equipo):
    _ariel_trabado(equipo, lucas_dice={"para_cuando": "2026-10-07"})
    equipo.dice("Ariel", Jugada("destrabar", {"tarea": "T1"}))

    _salir(conn, mundo, octubre(7, 10))

    [aviso] = _preguntas_a(conn, mundo, "Lucas", EL_DIA)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "ya_se_destrabo")


def test_si_lo_destraba_otra_persona_no_sale(conn, mundo, servidor, equipo):
    _ariel_trabado(equipo, lucas_dice={"para_cuando": "2026-10-07"})
    equipo.dice("Ariel", Jugada("anotar_quien_destraba", {"tarea": "T1", "quien": "juan"}))

    _salir(conn, mundo, octubre(7, 10))

    [aviso] = _preguntas_a(conn, mundo, "Lucas", EL_DIA)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "cambio_quien_destraba")


def test_si_dice_hoy_y_ya_paso_la_hora_es_el_dia_habil_siguiente(conn, mundo, servidor, equipo):
    _ariel_trabado(equipo)

    equipo.dice("Lucas", Jugada("decir_cuando_destraba",
                                {"tarea": "T1", "para_cuando": "2026-10-05"}))

    [aviso] = _preguntas_a(conn, mundo, "Lucas", EL_DIA)
    assert aviso["programado_para"] == octubre(6, 10)


def test_ya_esta_no_deja_nada_para_otro_dia(conn, mundo, servidor, equipo):
    _ariel_trabado(equipo)

    r = equipo.dice("Lucas", Jugada("decir_cuando_destraba", {"tarea": "T1", "ya_esta": True}))

    assert _preguntas_a(conn, mundo, "Lucas", EL_DIA) == []
    assert "le_vuelve_a_preguntar" not in r.hechos[0]
