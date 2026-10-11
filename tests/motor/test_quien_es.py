"""Un nombre que Leda no reconoce: pregunta quién es (`leda.motor.apodos`; ADR 0020, decisiones
1, 3 y 5; conversación 47).

Cuando alguien nombra a una persona que no coincide con nadie del equipo ni con un apodo
aprendido, Leda no anota nada: pregunta quién es, la persona contesta con un nombre y Leda confirma
con nombre y apellido (con el botón Confirmar o escrito, con la guarda de la decisión 2 del ADR
0018). Con la confirmación aprende el apodo, auditado, y hace lo que se le había pedido como si lo
hubieran nombrado por su nombre. Un apodo de dos personas se pregunta con un botón por persona, y
Leda nunca elige. El apodo sirve para entender, nunca para hablar.

El mundo es el de las conversaciones (`tests.conversaciones.carga`).
"""

from __future__ import annotations

import pytest

from leda.motor import hechos
from leda.motor.ia import Jugada

from tests.conversaciones.carga import cargar
from tests.motor.ayudantes import todos, uno
from tests.motor.test_aprobacion import Turnos

MARIANO, MARTIN, MARCOS = "Mariano Naim", "Martín Forte", "Marcos Tarquini"
QUIEN_ES, CONFIRMAR, CUAL = ("quien_es_esa_persona", "confirmar_quien_es_esa_persona",
                             "cual_de_esas_personas")


@pytest.fixture
def turnos(conn) -> Turnos:
    """CoreWork en chico con una tarea de Marcos y una de Nahuel, cuyo trabajo aprueba Marcos;
    "el flaco" cargado por la plataforma para Martín y para Marcos."""
    mundo = cargar(conn, {
        "inicio": "2026-10-20 09:00",
        "apodos": [{"apodo": "el flaco", "de": "Martin"}, {"apodo": "el flaco", "de": "Marcos"}],
        "tareas": {
            "COM": {"titulo": "Revisar comunicaciones", "responsable": "Marcos",
                    "vence": "2026-11-06", "estado": "en_curso", "desde": "2026-10-19"},
            "SEN": {"titulo": "Calibrar los sensores", "responsable": "Nahuel",
                    "vence": "2026-11-06", "estado": "en_curso", "desde": "2026-10-19",
                    "criterio": "Los sensores quedan calibrados y probados"},
        }})
    t = Turnos(conn, {"id": mundo.workspace_id, "personas": mundo.personas})
    t.carga = mundo
    return t


def _pregunta(conn, t: Turnos, corto: str) -> dict | None:
    """La pregunta abierta de esa persona."""
    return uno(conn, """select q.* from conversation_state s
                          join conversation_question q on q.id = s.pregunta_abierta_id
                         where s.membership_id = %s and q.cerrada_en is null""",
               t.mundo["personas"][corto]["membership_id"])


def _boton(conn, t: Turnos, corto: str, etiqueta: str) -> str:
    return uno(conn, """select o.token from conversation_option o
                          join conversation_question q on q.id = o.question_id
                         where q.membership_id = %s and o.etiqueta = %s
                         order by q.abierta_en desc limit 1""",
               t.mundo["personas"][corto]["membership_id"], etiqueta)["token"]


def _apodos(conn) -> list[tuple[str, str, str]]:
    return [(f["nombre"], f["apodo"], f["canal"]) for f in todos(
        conn, """select u.nombre, a.apodo, a.canal from apodo a
                   join membership m on m.id = a.membership_id
                   join app_user u on u.id = m.app_user_id
                  order by a.apodo, u.nombre""")]


def _el_tano(conn) -> list[tuple[str, str, str]]:
    return [a for a in _apodos(conn) if a[1] == "el tano"]


def _pases(conn) -> list[dict]:
    return todos(conn, "select * from pase_de_tarea")


def _alias(t: Turnos, corto: str, titulo: str) -> str:
    t.dice(corto)
    return next(x["alias"] for x in t.situacion["tareas"] if x["titulo"] == titulo)


def _pedir(t: Turnos, a: str):
    alias = _alias(t, "Marcos", "Revisar comunicaciones")
    return t.dice("Marcos", Jugada("pedir_reasignacion", {"tarea": alias, "a": a}),
                  texto=f"pasale la de comunicaciones a {a}")


def _que_es_mariano(conn, t: Turnos):
    _pedir(t, "el tano")
    return t.dice("Marcos", Jugada("decir_quien_es", {"quien_es": "mariano"}), texto="mariano")


# --- Preguntar quién es ------------------------------------------------------------------------

def test_a_quien_no_reconoce_le_pregunta_quien_es_sin_hacer_nada(conn, turnos):
    r = _pedir(turnos, "el tano")

    [hecho] = r.hechos
    assert hecho["jugada"] == "pedir_reasignacion"
    assert (hecho["resultado"], hecho["falta"]) == ("falta_dato", ["quien_es"])
    assert hecho["como_lo_nombro"] == "el tano" and hecho["pregunta"] == QUIEN_ES
    assert r.pregunta["tipo"] == QUIEN_ES and r.pregunta["como_lo_nombro"] == "el tano"
    assert _pregunta(conn, turnos, "Marcos")["tipo"] == QUIEN_ES
    assert _pases(conn) == [] and _el_tano(conn) == []
    assert hechos.sin_significado(turnos.redaccion) == set()


def test_la_respuesta_se_confirma_con_nombre_y_apellido_antes_de_aprender(conn, turnos):
    r = _que_es_mariano(conn, turnos)

    [hecho] = r.hechos
    assert hecho["jugada"] == "decir_quien_es"
    assert hecho["resultado"] == "quien_es_para_confirmar"
    assert hecho["como_lo_nombro"] == "el tano" and hecho["integrante"] == MARIANO
    assert r.pregunta["tipo"] == CONFIRMAR
    assert [o["etiqueta"] for o in r.pregunta["opciones"]] == ["Confirmar"]
    assert _el_tano(conn) == [] and _pases(conn) == []
    assert hechos.sin_significado(turnos.redaccion) == set()


def test_con_el_boton_aprende_el_apodo_y_hace_lo_que_se_pidio(conn, turnos):
    _que_es_mariano(conn, turnos)

    r = turnos.toca("Marcos", _boton(conn, turnos, "Marcos", "Confirmar"))

    [hecho] = r.hechos
    # Lo que se había pedido, como si lo hubiera nombrado por su nombre: la vista previa del pase.
    assert (hecho["jugada"], hecho["resultado"]) == ("pedir_reasignacion",
                                                     "pase_para_confirmar")
    assert hecho["pase"]["pasaria_a"] == MARIANO
    assert hecho["aprendio_como_le_dicen_a"] == MARIANO
    assert _el_tano(conn) == [(MARIANO, "el tano", "chat")]
    [auditoria] = todos(conn, """select * from audit_log where accion = 'aprender_apodo'
                                   and detalle ->> 'canal' = 'chat'""")
    assert (str(auditoria["actor_app_user_id"])
            == turnos.mundo["personas"]["Marcos"]["app_user_id"])
    assert r.pregunta["tipo"] == "confirmar_el_pase"
    assert hechos.sin_significado(turnos.redaccion) == set()


def test_un_si_escrito_vale_igual_que_el_boton(conn, turnos):
    _que_es_mariano(conn, turnos)

    r = turnos.dice("Marcos", Jugada("confirmar", {}), texto="si")

    [hecho] = r.hechos
    assert (hecho["jugada"], hecho["resultado"]) == ("pedir_reasignacion",
                                                     "pase_para_confirmar")
    assert hecho["pase"]["pasaria_a"] == MARIANO
    assert _el_tano(conn) == [(MARIANO, "el tano", "chat")]


def test_una_confirmacion_en_el_mismo_mensaje_no_vale(conn, turnos):
    """La guarda de la decisión 2: lo que confirma es lo último que vio, en un mensaje anterior."""
    _pedir(turnos, "el tano")

    r = turnos.dice("Marcos", Jugada("decir_quien_es", {"quien_es": "mariano"}),
                    Jugada("confirmar", {}), texto="mariano, si")

    assert r.hechos[1]["resultado"] == "no_vale_la_confirmacion"
    assert _el_tano(conn) == []
    assert _pregunta(conn, turnos, "Marcos")["tipo"] == CONFIRMAR


def test_un_nombre_que_no_es_de_nadie_se_dice_y_sigue_preguntando(conn, turnos):
    _pedir(turnos, "el tano")

    r = turnos.dice("Marcos", Jugada("decir_quien_es", {"quien_es": "roberto"}),
                    texto="roberto")

    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["motivo"]) == ("no_se_puede", "persona_desconocida")
    assert hecho["nombre_que_no_esta"] == "roberto"
    assert _pregunta(conn, turnos, "Marcos")["tipo"] == QUIEN_ES
    assert r.pregunta["tipo"] == QUIEN_ES
    assert _el_tano(conn) == []
    assert hechos.sin_significado(turnos.redaccion) == set()


def test_otro_nombre_en_lugar_de_confirmar_muestra_ese(conn, turnos):
    _que_es_mariano(conn, turnos)

    r = turnos.dice("Marcos", Jugada("decir_quien_es", {"quien_es": "lucas"}),
                    texto="no, perdon, lucas")

    [hecho] = r.hechos
    assert hecho["resultado"] == "quien_es_para_confirmar"
    assert hecho["integrante"] == "Lucas Natuche"
    assert _pregunta(conn, turnos, "Marcos")["tipo"] == CONFIRMAR
    assert _el_tano(conn) == []


def test_si_no_es_del_equipo_no_se_aprende_nada_y_se_dice(conn, turnos):
    _pedir(turnos, "el tano")

    r = turnos.dice("Marcos", Jugada("decir_quien_es", {"de_afuera": True}),
                    texto="no es del equipo, es un proveedor")

    [hecho] = r.hechos
    assert hecho["jugada"] == "pedir_reasignacion"
    assert (hecho["resultado"], hecho["motivo"]) == ("no_se_puede", "persona_desconocida")
    assert _pregunta(conn, turnos, "Marcos") is None
    assert _el_tano(conn) == [] and _pases(conn) == []


def test_dejarla_sin_efecto_no_anota_nada(conn, turnos):
    _pedir(turnos, "el tano")

    r = turnos.dice("Marcos", Jugada("cancelar", {}), texto="deja")

    assert r.hechos[0]["resultado"] == "cancelado"
    assert _pregunta(conn, turnos, "Marcos") is None
    assert _el_tano(conn) == [] and _pases(conn) == []


def test_un_apodo_aprendido_se_reconoce_sin_volver_a_preguntar(conn, turnos):
    _que_es_mariano(conn, turnos)
    turnos.toca("Marcos", _boton(conn, turnos, "Marcos", "Confirmar"))
    turnos.dice("Marcos", Jugada("cancelar", {}), texto="deja, no se la paso")

    r = _pedir(turnos, "Tano")

    assert r.hechos[0]["resultado"] == "pase_para_confirmar"
    assert r.hechos[0]["pase"]["pasaria_a"] == MARIANO


# --- Un apodo de dos personas: un botón por persona, y Leda nunca elige (decisión 3) -----------

def test_un_apodo_de_dos_personas_se_pregunta_con_un_boton_por_persona(conn, turnos):
    r = _pedir(turnos, "el flaco")

    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["falta"]) == ("falta_dato", ["quien_es"])
    assert hecho["coinciden"] == [MARCOS, MARTIN] and hecho["pregunta"] == CUAL
    assert r.pregunta["tipo"] == CUAL
    assert [o["etiqueta"] for o in r.pregunta["opciones"]] == [MARCOS, MARTIN]
    assert _pases(conn) == []
    assert hechos.sin_significado(turnos.redaccion) == set()

    r = turnos.toca("Marcos", _boton(conn, turnos, "Marcos", MARTIN))

    [hecho] = r.hechos
    assert (hecho["jugada"], hecho["resultado"]) == ("pedir_reasignacion",
                                                     "pase_para_confirmar")
    assert hecho["pase"]["pasaria_a"] == MARTIN
    assert "aprendio_como_le_dicen_a" not in hecho
    assert len(_apodos(conn)) == 2          # ningún apodo cambia


def test_elegir_escrito_entre_las_dos_vale_igual(conn, turnos):
    _pedir(turnos, "el flaco")

    r = turnos.dice("Marcos", Jugada("decir_quien_es", {"quien_es": "martin"}), texto="martin")

    assert r.hechos[0]["pase"]["pasaria_a"] == MARTIN
    assert len(_apodos(conn)) == 2


def test_una_respuesta_que_es_de_dos_personas_se_elige_y_se_aprende(conn, turnos):
    """"¿Quién es el tano?" "el flaco": son dos; elige con nombre y apellido, y eso confirma."""
    _pedir(turnos, "el tano")

    r = turnos.dice("Marcos", Jugada("decir_quien_es", {"quien_es": "el flaco"}),
                    texto="el flaco")
    assert r.pregunta["tipo"] == CUAL and _el_tano(conn) == []
    r = turnos.toca("Marcos", _boton(conn, turnos, "Marcos", MARTIN))

    assert r.hechos[0]["pase"]["pasaria_a"] == MARTIN
    assert _el_tano(conn) == [(MARTIN, "el tano", "chat")]


# --- La aprobación también pregunta ------------------------------------------------------------

def test_decidir_lo_de_alguien_por_un_apodo_que_no_conoce_pregunta_quien_es(conn, turnos):
    t = turnos
    alias = _alias(t, "Nahuel", "Calibrar los sensores")
    t.dice("Nahuel", Jugada("entregar", {"tarea": alias, "lo_descrito_cubre": ["C1"]}),
           texto="listo, calibrados y probados")
    t.dice("Nahuel", Jugada("confirmar", {}), texto="dale")

    r = t.dice("Marcos", Jugada("aprobar", {"de": "el negro"}), texto="aprobale lo del negro")
    assert (r.hechos[0]["resultado"], r.pregunta["tipo"]) == ("falta_dato", QUIEN_ES)
    t.dice("Marcos", Jugada("decir_quien_es", {"quien_es": "nahuel"}), texto="nahuel")
    r = t.toca("Marcos", _boton(conn, t, "Marcos", "Confirmar"))

    [hecho] = r.hechos
    assert (hecho["jugada"], hecho["resultado"]) == ("aprobar", "anotado")
    assert ("Nahuel Gimenez", "el negro", "chat") in _apodos(conn)


# --- El apodo sirve para entender, nunca para hablar (decisión 5) ------------------------------

def _con_clave(valor, clave=None):
    if isinstance(valor, dict):
        for k, v in valor.items():
            yield from _con_clave(v, k)
    elif isinstance(valor, list):
        for v in valor:
            yield from _con_clave(v, clave)
    else:
        yield clave, valor


def test_lo_que_lee_la_ia_nombra_a_la_persona_por_su_nombre(conn, turnos):
    """El apodo llega sólo como lo que dijo la persona (`como_lo_nombro`), nunca como el nombre
    de nadie."""
    _que_es_mariano(conn, turnos)
    for pedido in (turnos.redaccion,):
        claves = {k for k, v in _con_clave(pedido["hechos"])
                  if isinstance(v, str) and "tano" in v.lower()}
        assert claves <= {"como_lo_nombro"}, claves
    turnos.toca("Marcos", _boton(conn, turnos, "Marcos", "Confirmar"))
    claves = {k for k, v in _con_clave(turnos.redaccion["hechos"])
              if isinstance(v, str) and "tano" in v.lower()}
    assert claves == set(), claves


# --- Quién destraba también pregunta (decisión 65 del usuario, 2026-10-11) ---------------------
#
# Un nombre que no es nadie del equipo ("el proveedor", "pedro de compras") no se anota como
# alguien de afuera: Leda pregunta quién es, y sólo si la persona contesta que no es del equipo
# queda así. La IA nunca lo decide sola, tampoco leyendo el mismo mensaje que nombró a la persona.

def _trabada(t: Turnos) -> str:
    alias = _alias(t, "Marcos", "Revisar comunicaciones")
    t.dice("Marcos", Jugada("anotar_bloqueo", {"tarea": alias, "causa": "me falta el cable"}),
           texto="la de comunicaciones esta trabada, me falta el cable")
    return alias


def _destraban(conn) -> list[tuple[str | None, str | None]]:
    return [(f["nombre"], f["destraba_externo"]) for f in todos(
        conn, """select u.nombre, b.destraba_externo from blocker_unblocker b
                   left join membership m on m.id = b.destraba_membership_id
                   left join app_user u on u.id = m.app_user_id
                  order by b.at, b.id""")]


def _lo_destraba(t: Turnos, alias: str, quien: str):
    return t.dice("Marcos", Jugada("anotar_quien_destraba", {"tarea": alias, "quien": quien}),
                  texto=f"me lo consigue {quien}")


def test_quien_destraba_con_un_nombre_que_no_conoce_pregunta_quien_es(conn, turnos):
    alias = _trabada(turnos)

    r = _lo_destraba(turnos, alias, "el proveedor")

    [hecho] = r.hechos
    assert hecho["jugada"] == "anotar_quien_destraba"
    assert (hecho["resultado"], hecho["falta"]) == ("falta_dato", ["quien_es"])
    assert hecho["como_lo_nombro"] == "el proveedor" and hecho["pregunta"] == QUIEN_ES
    assert _pregunta(conn, turnos, "Marcos")["tipo"] == QUIEN_ES
    assert _destraban(conn) == []
    assert hechos.sin_significado(turnos.redaccion) == set()


def test_si_contesta_que_no_es_del_equipo_queda_como_alguien_de_afuera(conn, turnos):
    alias = _trabada(turnos)
    _lo_destraba(turnos, alias, "el proveedor")

    r = turnos.dice("Marcos", Jugada("decir_quien_es", {"de_afuera": True}),
                    texto="no es del equipo, es el proveedor del cable")

    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["quien_destraba"] == {"externo": "el proveedor"}
    assert _destraban(conn) == [(None, "el proveedor")]
    assert _pregunta(conn, turnos, "Marcos") is None
    assert len(_apodos(conn)) == 2          # no aprende nada
    assert hechos.sin_significado(turnos.redaccion) == set()


def test_la_ia_no_decide_sola_que_es_de_afuera_en_el_mismo_mensaje(conn, turnos):
    """Que no es del equipo lo contesta la persona a la pregunta de Leda, en un mensaje
    posterior: leído del mismo mensaje que la nombró, es la IA la que lo decide, y no vale."""
    alias = _trabada(turnos)

    r = turnos.dice("Marcos",
                    Jugada("anotar_quien_destraba", {"tarea": alias, "quien": "el proveedor"}),
                    Jugada("decir_quien_es", {"de_afuera": True}),
                    texto="me lo consigue el proveedor")

    assert r.hechos[1]["resultado"] == "falta_dato" and r.hechos[1]["falta"] == ["quien_es"]
    assert _destraban(conn) == []
    assert _pregunta(conn, turnos, "Marcos")["tipo"] == QUIEN_ES


def test_si_es_alguien_del_equipo_confirma_aprende_y_lo_anota(conn, turnos):
    alias = _trabada(turnos)
    _lo_destraba(turnos, alias, "el tano")
    r = turnos.dice("Marcos", Jugada("decir_quien_es", {"quien_es": "mariano"}), texto="mariano")
    assert r.pregunta["tipo"] == CONFIRMAR and _destraban(conn) == []

    r = turnos.toca("Marcos", _boton(conn, turnos, "Marcos", "Confirmar"))

    [hecho] = r.hechos
    assert (hecho["jugada"], hecho["resultado"]) == ("anotar_quien_destraba", "anotado")
    assert hecho["quien_destraba"] == {"integrante": MARIANO}
    assert hecho["aprendio_como_le_dicen_a"] == MARIANO
    assert _destraban(conn) == [(MARIANO, None)]
    assert _el_tano(conn) == [(MARIANO, "el tano", "chat")]


def test_un_apodo_de_dos_personas_para_quien_destraba_se_elige(conn, turnos):
    alias = _trabada(turnos)

    r = _lo_destraba(turnos, alias, "el flaco")
    assert r.pregunta["tipo"] == CUAL
    r = turnos.toca("Marcos", _boton(conn, turnos, "Marcos", MARTIN))

    assert r.hechos[0]["quien_destraba"] == {"integrante": MARTIN}
    assert _destraban(conn) == [(MARTIN, None)]


# --- Corregir un apodo que ya tiene dueño: Leda pregunta (decisión 67 del usuario, 2026-10-11) --
#
# Si "el tano" es Mariano y alguien dice "no, el tano es Nahuel", Leda no cambia nada sin
# preguntar: si a los dos les dicen así ("A los dos": desde entonces "el tano" da la duda con un
# botón por persona) o sólo a Nahuel ("Sólo a Nahuel Gimenez": el de Mariano se deja de usar, con
# quién y cuándo, y se le enseña a Nahuel). Escribirlo vale igual que el botón.

NAHUEL = "Nahuel Gimenez"
A_QUIENES = "a_quienes_les_dicen_asi"


def _el_tano_es_mariano(conn, t: Turnos) -> None:
    _que_es_mariano(conn, t)
    t.toca("Marcos", _boton(conn, t, "Marcos", "Confirmar"))
    t.dice("Marcos", Jugada("cancelar", {}), texto="deja, no se la paso")


def _el_tano_es_nahuel(t: Turnos):
    return t.dice("Marcos", Jugada("decir_quien_es", {"apodo": "el tano", "quien_es": "nahuel"}),
                  texto="no, el tano es nahuel")


def _vigentes_del_tano(conn) -> list[str]:
    return [f["nombre"] for f in todos(
        conn, """select u.nombre from apodo a
                   join membership m on m.id = a.membership_id
                   join app_user u on u.id = m.app_user_id
                  where a.apodo = 'el tano' and a.borrado_en is null order by u.nombre""")]


def test_corregir_un_apodo_que_ya_tiene_dueno_pregunta_a_quienes_sin_cambiar_nada(conn, turnos):
    _el_tano_es_mariano(conn, turnos)

    r = _el_tano_es_nahuel(turnos)

    [hecho] = r.hechos
    assert hecho["jugada"] == "decir_quien_es"
    assert (hecho["resultado"], hecho["falta"]) == ("falta_dato", [A_QUIENES])
    assert hecho["como_lo_nombro"] == "el tano" and hecho["integrante"] == NAHUEL
    assert hecho["ya_le_dicen_asi_a"] == [MARIANO]
    assert hecho["pregunta"] == A_QUIENES
    assert r.pregunta["tipo"] == A_QUIENES
    assert [o["etiqueta"] for o in r.pregunta["opciones"]] == ["A los dos", f"Sólo a {NAHUEL}"]
    assert _vigentes_del_tano(conn) == [MARIANO]
    assert hechos.sin_significado(turnos.redaccion) == set()


def test_a_los_dos_les_ensena_el_apodo_y_desde_entonces_pregunta_cual(conn, turnos):
    _el_tano_es_mariano(conn, turnos)
    _el_tano_es_nahuel(turnos)

    r = turnos.toca("Marcos", _boton(conn, turnos, "Marcos", "A los dos"))

    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["aprendio_como_le_dicen_a"] == NAHUEL
    assert hecho["sigue_reconociendo_asi_a"] == [MARIANO]
    assert _vigentes_del_tano(conn) == [MARIANO, NAHUEL]
    assert _pregunta(conn, turnos, "Marcos") is None
    assert hechos.sin_significado(turnos.redaccion) == set()

    r = _pedir(turnos, "el tano")
    assert r.pregunta["tipo"] == CUAL
    assert [o["etiqueta"] for o in r.pregunta["opciones"]] == [MARIANO, NAHUEL]


def test_solo_a_el_deja_de_usar_el_de_antes_con_quien_y_cuando_y_se_lo_ensena(conn, turnos):
    _el_tano_es_mariano(conn, turnos)
    _el_tano_es_nahuel(turnos)

    r = turnos.toca("Marcos", _boton(conn, turnos, "Marcos", f"Sólo a {NAHUEL}"))

    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["aprendio_como_le_dicen_a"] == NAHUEL
    assert hecho["dejo_de_reconocer_asi_a"] == [MARIANO]
    assert _vigentes_del_tano(conn) == [NAHUEL]
    marcos = turnos.mundo["personas"]["Marcos"]["app_user_id"]
    [retirado] = todos(conn, """select a.id, a.borrado_en, a.borrado_por_app_user_id
                                  from apodo a where a.apodo = 'el tano'
                                   and a.borrado_en is not null""")
    assert str(retirado["borrado_por_app_user_id"]) == marcos
    [auditoria] = todos(conn, """select * from audit_log where accion = 'dejar_de_usar_apodo'""")
    assert str(auditoria["sujeto_id"]) == str(retirado["id"])
    assert str(auditoria["actor_app_user_id"]) == marcos
    assert hechos.sin_significado(turnos.redaccion) == set()

    r = _pedir(turnos, "el tano")
    assert r.hechos[0]["pase"]["pasaria_a"] == NAHUEL


def test_elegirlo_por_escrito_vale_igual_que_el_boton(conn, turnos):
    _el_tano_es_mariano(conn, turnos)
    _el_tano_es_nahuel(turnos)

    r = turnos.dice("Marcos", Jugada("elegir", {"opcion": "O2"}), texto="solo a nahuel")

    assert r.hechos[0]["dejo_de_reconocer_asi_a"] == [MARIANO]
    assert _vigentes_del_tano(conn) == [NAHUEL]


def test_nombrar_solo_a_la_nueva_persona_es_solo_a_ella(conn, turnos):
    _el_tano_es_mariano(conn, turnos)
    _el_tano_es_nahuel(turnos)

    r = turnos.dice("Marcos", Jugada("decir_quien_es", {"quien_es": "nahuel"}),
                    texto="solo nahuel")

    assert r.hechos[0]["dejo_de_reconocer_asi_a"] == [MARIANO]
    assert _vigentes_del_tano(conn) == [NAHUEL]


def test_dejar_la_pregunta_sin_efecto_no_cambia_nada(conn, turnos):
    _el_tano_es_mariano(conn, turnos)
    _el_tano_es_nahuel(turnos)

    turnos.dice("Marcos", Jugada("cancelar", {}), texto="deja, olvidate")

    assert _vigentes_del_tano(conn) == [MARIANO]
    assert _pregunta(conn, turnos, "Marcos") is None


def test_decir_que_el_apodo_es_de_quien_ya_lo_tiene_no_cambia_nada(conn, turnos):
    _el_tano_es_mariano(conn, turnos)

    r = turnos.dice("Marcos", Jugada("decir_quien_es", {"apodo": "el tano",
                                                        "quien_es": "mariano"}),
                    texto="el tano es mariano")

    [hecho] = r.hechos
    assert hecho["resultado"] == "ya_lo_reconocia_asi" and hecho["integrante"] == MARIANO
    assert r.pregunta is None
    assert _vigentes_del_tano(conn) == [MARIANO]
    assert hechos.sin_significado(turnos.redaccion) == set()


def test_un_apodo_que_no_es_de_nadie_se_confirma_antes_de_aprenderlo(conn, turnos):
    r = turnos.dice("Marcos", Jugada("decir_quien_es", {"apodo": "el tano",
                                                        "quien_es": "mariano"}),
                    texto="al tano le decimos a mariano")

    [hecho] = r.hechos
    assert hecho["resultado"] == "quien_es_para_confirmar" and hecho["integrante"] == MARIANO
    assert r.pregunta["tipo"] == CONFIRMAR
    assert _vigentes_del_tano(conn) == []

    r = turnos.toca("Marcos", _boton(conn, turnos, "Marcos", "Confirmar"))

    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["aprendio_como_le_dicen_a"]) == ("anotado", MARIANO)
    assert _vigentes_del_tano(conn) == [MARIANO]
    assert hechos.sin_significado(turnos.redaccion) == set()


def test_con_la_pregunta_de_quien_es_abierta_el_apodo_la_contesta(conn, turnos):
    """Si Leda preguntaba quién es "el tano", decir "el tano es mariano" es la respuesta, no una
    corrección."""
    _pedir(turnos, "el tano")

    r = turnos.dice("Marcos", Jugada("decir_quien_es", {"apodo": "el tano",
                                                        "quien_es": "mariano"}),
                    texto="el tano es mariano")

    assert r.hechos[0]["resultado"] == "quien_es_para_confirmar"
    assert r.pregunta["tipo"] == CONFIRMAR
