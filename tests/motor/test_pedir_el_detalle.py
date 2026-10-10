"""El resumen para cualquiera, el detalle a pedido (decisión 33 del usuario, 2026-10-09;
`leda.motor.enlace` y `leda.motor.detalle`; conversación 45).

Dos niveles: el resumen de una tarea (qué tarea, de quién, para cuándo, cómo quedó) lo ve
cualquiera del equipo; el detalle (fotos, archivos, correcciones pedidas) sólo quienes tienen que
ver con la tarea (ADR 0019, 7b, igual). Leda nunca contesta "no la podés ver" ni deja a la persona
sin un próximo paso: le da el resumen y le ofrece pedir el detalle por ella. Si la persona dice que
sí (`pedir_el_detalle`), Leda le pregunta al encargado del sector de la tarea si se la comparte,
con dos botones (`contestar_el_pedido_del_detalle`); si dice que sí, la cocina la comparte
(auditado, revocable) y a la persona le llega el enlace; si no, se lo cuenta (decisión 39).

El mundo es el de las conversaciones (`tests.conversaciones.carga`): Nahuel (OT), Lucas y Martín
(Infraestructura IT; Martín es su encargado), Marcos (encargado de OT).
"""

from __future__ import annotations

import dataclasses
from datetime import timedelta

import pytest

from leda import config as config_mod
from leda.autoridad import identificar_en_espacio
from leda.db import admin, espacio
from leda.herramientas import ejecutar
from leda.motor import hechos as hechos_mod
from leda.motor import preguntas
from leda.motor.avisos import LLEVA_EL_ENLACE, enviar_avisos
from leda.motor.fichas import FICHAS
from leda.motor.ia import Jugada
from leda.motor.tiempo import RelojFijo

from tests.conversaciones.carga import cargar
from tests.motor.ayudantes import (AHORA, IAQueRedacta, administrador, avisos_guardados,
                                   cuantas, octubre, todos, uno)
from tests.motor.test_aprobacion import Turnos

DIRECCION = "https://leda.invalid/"
SWITCH = "Configurar el switch de la planta"
SERVIDOR = "Instalar el servidor de la planta"
LUCAS, MARTIN, NAHUEL, MARCOS = "Lucas Natuche", "Martín Forte", "Nahuel Gimenez", "Marcos Tarquini"
PEDIDO, COMO_TERMINO = "pedido_del_detalle", "como_termino_el_pedido_del_detalle"


@pytest.fixture
def direccion(monkeypatch):
    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url=DIRECCION))


@pytest.fixture
def equipo(conn, direccion) -> Turnos:
    """CoreWork en chico: dos tareas de Lucas (Infraestructura IT) y una de Marcos (OT)."""
    mundo = cargar(conn, {"tareas": {
        "SW": {"titulo": SWITCH, "responsable": "Lucas", "vence": "2026-10-16",
               "estado": "en_curso", "desde": "2026-10-01",
               "criterio": "El switch da red a las doce máquinas de la línea"},
        "SRV": {"titulo": SERVIDOR, "responsable": "Lucas", "vence": "2026-10-23"},
        "PLC": {"titulo": "Programar el PLC", "responsable": "Marcos", "vence": "2026-10-16"},
    }})
    t = Turnos(conn, {"id": mundo.workspace_id, "personas": mundo.personas})
    t.carga = mundo
    return t


def _pide_el_enlace(t: Turnos, nombre: str, como: str):
    return t.dice(nombre, Jugada("pedir_enlace", {"como_la_nombra": como}),
                  texto=f"pasame el link de {como}")


def _enlaces(conn, nombre: str | None = None, t: Turnos | None = None) -> list[str]:
    """Las tareas de las marcas de enlace de lo que salió (respuestas y avisos)."""
    filas = todos(conn, """select e.task_id::text tarea, e.membership_id::text persona
                             from message_outbox_enlace e""")
    if nombre is None:
        return [f["tarea"] for f in filas]
    persona = t.mundo["personas"][nombre]["membership_id"]
    return [f["tarea"] for f in filas if f["persona"] == persona]


def _salir(conn, t: Turnos, at) -> IAQueRedacta:
    ia = IAQueRedacta()
    enviar_avisos(conn, t.carga.workspace_id, ia, RelojFijo(at))
    conn.commit()
    return ia


def _boton(conn, t: Turnos, nombre: str, etiqueta: str) -> str:
    return uno(conn, """select o.token from conversation_option o
                          join conversation_question q on q.id = o.question_id
                         where q.membership_id = %s and o.etiqueta = %s
                         order by q.abierta_en desc limit 1""",
               t.mundo["personas"][nombre]["membership_id"], etiqueta)["token"]


def _pedido_hecho(conn, t: Turnos, tarea: str = "SW") -> None:
    """Nahuel pide el enlace del switch, que no ve, y acepta que Leda le pida el detalle."""
    _pide_el_enlace(t, "Nahuel", "switch" if tarea == "SW" else "servidor")
    t.dice("Nahuel", Jugada("pedir_el_detalle", {}), texto="si dale")


def _alias_de(t: Turnos, nombre: str, titulo: str) -> str:
    t.dice(nombre)
    return next(x["alias"] for x in t.situacion["tareas"] if x["titulo"] == titulo)


# --- Las fichas ------------------------------------------------------------------------------

def test_pedir_el_detalle_y_contestarlo_son_fichas_de_la_lista_cerrada():
    pedir, contestar = FICHAS["pedir_el_detalle"], FICHAS["contestar_el_pedido_del_detalle"]
    assert not pedir.del_responsable and not contestar.del_responsable
    assert set(pedir.opcional) == {"tarea", "como_la_nombra"} and pedir.necesita == ()
    assert set(contestar.opcional) == {"tarea", "acepta", "por_que"}
    assert not contestar.se_ofrece
    assert contestar.contesta == (preguntas.COMPARTIR_EL_DETALLE,)
    for nombre in ("pedir_el_detalle", "contestar_el_pedido_del_detalle"):
        assert nombre in hechos_mod.PARA_LA_REDACCION
    for codigo in ("solo_el_resumen", "el_detalle_lo_ve", "se_lo_puede_pedir_a",
                   "detalle_pedido", "ya_se_lo_pidio_a", "compartir_el_detalle",
                   "pedido_del_detalle", "como_termino_el_pedido_del_detalle",
                   "pide_ver_el_detalle", "la_compartio", "aviso_a_quien_lo_pidio",
                   "espera_que_decida_si_la_comparte", "no_hay_un_pedido_del_detalle",
                   "sin_encargado_del_sector", "ya_la_ve"):
        assert hechos_mod.significado(codigo), codigo


# --- El resumen, que ve cualquiera ------------------------------------------------------------

def test_quien_no_la_ve_recibe_el_resumen_y_la_oferta_y_ningun_enlace(conn, equipo):
    r = _pide_el_enlace(equipo, "Nahuel", "switch")

    [hecho] = r.hechos
    assert hecho == {"jugada": "pedir_enlace", "resultado": "solo_el_resumen",
                     "tarea": {"titulo": SWITCH}, "responsable": LUCAS, "estado": "en_curso",
                     "vence": "2026-10-16", "el_detalle_lo_ve": "Infraestructura IT",
                     "se_lo_puede_pedir_a": MARTIN, "pregunta": preguntas.PROPUESTA}
    assert _enlaces(conn) == []
    # Lo que Leda ofrece es un tema abierto: una propuesta sobre esa tarea.
    assert r.pregunta["tipo"] == preguntas.PROPUESTA
    [propuesta] = todos(conn, """select task_id::text tarea, jugada from conversation_question
                                  where tipo = 'propuesta' and cerrada_en is null""")
    assert propuesta["tarea"] == equipo.carga.tareas["SW"]
    assert propuesta["jugada"]["propone"] == ["pedir_el_detalle"]
    # Nada se pide ni se comparte todavía, y la IA no ve el detalle: ni el criterio.
    assert cuantas(conn, "pedido_de_detalle") == cuantas(conn, "tarea_compartida") == 0
    assert avisos_guardados(conn) == []
    assert "doce máquinas" not in repr(equipo.redaccion)


def test_el_resumen_nunca_dice_que_no_la_puede_ver(conn, equipo):
    r = _pide_el_enlace(equipo, "Nahuel", "switch")
    assert "no_puede_ver_esa_tarea" not in repr(r.hechos)
    assert not hechos_mod.significado("no_puede_ver_esa_tarea")


def test_varias_que_coinciden_y_no_ve_las_nombra_y_pregunta_cual(conn, equipo):
    r = _pide_el_enlace(equipo, "Nahuel", "planta")
    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["falta"]) == ("falta_dato", ["tarea"])
    assert hecho["coinciden"] == [{"titulo": SWITCH, "responsable": LUCAS},
                                  {"titulo": SERVIDOR, "responsable": LUCAS}]
    assert _enlaces(conn) == []


def test_sin_encargado_que_le_pueda_escribir_no_se_le_ofrece(conn, equipo):
    """Antes de prometer un envío, Leda comprueba que el destinatario esté conectado
    (constitución §7): sin Martín conectado, el resumen sin la oferta, y dice por qué. Y el
    administrador se entera, de verdad, para que lo conecte (decisión 37, su mecanismo)."""
    administrador(conn)
    with admin(conn) as cur:
        cur.execute("update app_user set telegram_user_id = null where id = %s",
                    (equipo.mundo["personas"]["Martin"]["app_user_id"],))
    conn.commit()
    [hecho] = _pide_el_enlace(equipo, "Nahuel", "switch").hechos
    assert hecho["resultado"] == "solo_el_resumen"
    assert "se_lo_puede_pedir_a" not in hecho and "pregunta" not in hecho
    assert hecho["no_se_le_puede_escribir_a"] == {"a": MARTIN,
                                                  "motivo": "destinatario_sin_telegram"}
    assert hecho["se_le_aviso_al_administrador"]["para_que_conecte"] == MARTIN
    assert hecho["se_le_aviso_al_administrador"]["llega"] != "no_le_va_a_llegar"
    [incidente] = todos(conn, "select etapa, resumen_sanitizado from incident")
    assert incidente["etapa"] == "motor_sin_leda_conectada"
    assert MARTIN in incidente["resumen_sanitizado"]
    assert cuantas(conn, "pedido_de_detalle") == 0


def test_sin_encargado_del_sector_el_resumen_lo_dice(conn, equipo):
    with admin(conn) as cur:
        cur.execute("update area set referente_membership_id = null where id = %s",
                    (equipo.carga.areas["it"],))
    conn.commit()
    [hecho] = _pide_el_enlace(equipo, "Nahuel", "switch").hechos
    assert hecho["resultado"] == "solo_el_resumen"
    assert hecho["sin_encargado_del_sector"] is True and "pregunta" not in hecho


# --- Pedir el detalle -----------------------------------------------------------------------

def test_aceptar_la_oferta_le_pregunta_al_encargado_terminado_el_margen(conn, equipo):
    _pide_el_enlace(equipo, "Nahuel", "switch")
    r = equipo.dice("Nahuel", Jugada("pedir_el_detalle", {}), texto="si dale")

    [hecho] = r.hechos
    assert hecho["resultado"] == "detalle_pedido"
    assert hecho["tarea"] == {"titulo": SWITCH}
    assert hecho["le_pregunta_a"]["a"] == MARTIN
    [pedido] = todos(conn, "select * from pedido_de_detalle")
    assert pedido["estado"] == "esperando_decision"
    assert str(pedido["decide_membership_id"]) == equipo.mundo["personas"]["Martin"][
        "membership_id"]
    assert str(pedido["pedido_por_membership_id"]) == equipo.mundo["personas"]["Nahuel"][
        "membership_id"]
    [aviso] = avisos_guardados(conn, PEDIDO)
    assert aviso["programado_para"] > AHORA
    assert aviso["hechos"]["pide_ver_el_detalle"] == NAHUEL
    assert aviso["hechos"]["la_tiene"] == LUCAS
    assert aviso["hechos"]["necesita_respuesta"] is True
    # Lo propuesto quedó contestado, y el pedido, en la auditoría.
    assert cuantas(conn, "conversation_question",
                   "tipo = 'propuesta' and cerrada_en is null") == 0
    assert cuantas(conn, "audit_log", "accion = 'herramienta:pedir_detalle_de_tarea'") == 1
    # Nada compartido todavía.
    assert cuantas(conn, "tarea_compartida") == 0


def test_tambien_se_pide_nombrandola(conn, equipo):
    r = equipo.dice("Nahuel", Jugada("pedir_el_detalle", {"como_la_nombra": "switch"}))
    assert r.hechos[0]["resultado"] == "detalle_pedido"


def test_sin_oferta_ni_nombre_falta_cual(conn, equipo):
    r = equipo.dice("Nahuel", Jugada("pedir_el_detalle", {}))
    assert (r.hechos[0]["resultado"], r.hechos[0]["falta"]) == ("falta_dato", ["tarea"])
    assert cuantas(conn, "pedido_de_detalle") == 0


def test_pedirlo_dos_veces_no_pide_otro(conn, equipo):
    _pedido_hecho(conn, equipo)
    r = equipo.dice("Nahuel", Jugada("pedir_el_detalle", {"como_la_nombra": "switch"}))
    assert (r.hechos[0]["resultado"], r.hechos[0]["motivo"]) == ("no_se_puede", "ya_lo_pidio")
    assert r.hechos[0]["ya_se_lo_pidio_a"] == MARTIN
    assert cuantas(conn, "pedido_de_detalle") == 1
    # Y el resumen no lo vuelve a ofrecer: ya se lo pidió.
    [hecho] = _pide_el_enlace(equipo, "Nahuel", "switch").hechos
    assert hecho["ya_se_lo_pidio_a"] == MARTIN and "pregunta" not in hecho


def test_si_ya_la_ve_le_pasa_el_enlace_sin_pedir_nada(conn, equipo):
    r = equipo.dice("Martin", Jugada("pedir_el_detalle", {"como_la_nombra": "switch"}))
    assert r.hechos[0]["resultado"] == "leido" and r.hechos[0][LLEVA_EL_ENLACE] is True
    assert cuantas(conn, "pedido_de_detalle") == 0


# --- El encargado decide ----------------------------------------------------------------------

def test_la_tarea_esta_en_la_lista_del_encargado_como_un_pedido_que_espera_su_decision(conn,
                                                                                    equipo):
    _pedido_hecho(conn, equipo)
    equipo.dice("Martin")
    vista = next(x for x in equipo.situacion["tareas"] if x["titulo"] == SWITCH)
    assert vista["espera_que_decida_si_la_comparte"] is True
    assert vista["pide_ver_el_detalle"] == [NAHUEL]
    assert "id" not in vista


def test_la_pregunta_al_encargado_sale_con_dos_botones(conn, equipo):
    _pedido_hecho(conn, equipo)
    _salir(conn, equipo, AHORA + timedelta(minutes=30))
    [aviso] = avisos_guardados(conn, PEDIDO)
    assert aviso["estado"] == "enviado"
    etiquetas = [f["etiqueta"] for f in todos(
        conn, """select o.etiqueta from conversation_option o
                   join conversation_question q on q.id = o.question_id
                  where q.tipo = %s order by o.orden""", preguntas.COMPARTIR_EL_DETALLE)]
    assert etiquetas == ["Compartirla", "No compartirla"]


def test_compartirla_con_el_boton_la_comparte_y_a_quien_la_pidio_le_llega_el_enlace(conn,
                                                                                 equipo):
    _pedido_hecho(conn, equipo)
    _salir(conn, equipo, AHORA + timedelta(minutes=30))

    r = equipo.toca("Martin", _boton(conn, equipo, "Martin", "Compartirla"),
                    at=AHORA + timedelta(minutes=40))

    [hecho] = r.hechos
    assert hecho["jugada"] == "contestar_el_pedido_del_detalle"
    assert (hecho["resultado"], hecho["la_compartio"]) == ("anotado", True)
    assert hecho["aviso_a_quien_lo_pidio"]["a"] == NAHUEL
    [compartida] = todos(conn, "select * from tarea_compartida")
    personas = equipo.mundo["personas"]
    assert str(compartida["membership_id"]) == personas["Nahuel"]["membership_id"]
    assert str(compartida["compartida_por_membership_id"]) == personas["Martin"]["membership_id"]
    assert str(compartida["task_id"]) == equipo.carga.tareas["SW"]
    assert compartida["revocada_en"] is None
    [pedido] = todos(conn, "select estado from pedido_de_detalle")
    assert pedido["estado"] == "compartida"
    # Auditado: quién la compartió, con quién y cuándo.
    [fila] = todos(conn, """select actor_app_user_id::text actor, detalle from audit_log
                             where accion = 'compartir_tarea'""")
    assert fila["actor"] == personas["Martin"]["app_user_id"]
    assert fila["detalle"]["con"] == personas["Nahuel"]["membership_id"]
    # A Nahuel le llega cómo terminó, con el enlace al final.
    [aviso] = avisos_guardados(conn, COMO_TERMINO)
    assert aviso["hechos"]["la_compartio"] is True
    _salir(conn, equipo, AHORA + timedelta(hours=2))
    assert _enlaces(conn, "Nahuel", equipo) == [equipo.carga.tareas["SW"]]
    # Desde entonces, pedir el enlace se lo pasa como a cualquiera que la ve.
    [hecho] = _pide_el_enlace(equipo, "Nahuel", "switch").hechos
    assert hecho["resultado"] == "leido" and hecho[LLEVA_EL_ENLACE] is True


def test_si_no_la_comparte_nada_cambia_y_se_lo_cuenta(conn, equipo):
    _pedido_hecho(conn, equipo)
    _salir(conn, equipo, AHORA + timedelta(minutes=30))
    alias = _alias_de(equipo, "Martin", SWITCH)

    r = equipo.dice("Martin", Jugada("contestar_el_pedido_del_detalle",
                                     {"tarea": alias, "acepta": False,
                                      "por_que": "tiene las claves del rack"}),
                    texto="no, tiene las claves del rack", at=AHORA + timedelta(minutes=40))

    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["la_compartio"]) == ("anotado", False)
    assert cuantas(conn, "tarea_compartida") == 0
    [pedido] = todos(conn, "select estado, motivo from pedido_de_detalle")
    assert (pedido["estado"], pedido["motivo"]) == ("no_compartida", "tiene las claves del rack")
    [aviso] = avisos_guardados(conn, COMO_TERMINO)
    assert aviso["hechos"]["la_compartio"] is False
    assert aviso["hechos"]["por_que"] == "tiene las claves del rack"
    _salir(conn, equipo, AHORA + timedelta(hours=2))
    assert _enlaces(conn) == []
    # La pregunta a Martín, con sus botones, ya no espera nada.
    assert cuantas(conn, "conversation_question",
                   "tipo = %s and cerrada_en is null", preguntas.COMPARTIR_EL_DETALLE) == 0


def test_un_boton_de_un_pedido_ya_decidido_no_hace_nada(conn, equipo):
    _pedido_hecho(conn, equipo)
    _salir(conn, equipo, AHORA + timedelta(minutes=30))
    token = _boton(conn, equipo, "Martin", "Compartirla")
    alias = _alias_de(equipo, "Martin", SWITCH)
    equipo.dice("Martin", Jugada("contestar_el_pedido_del_detalle",
                                 {"tarea": alias, "acepta": False}))
    equipo.toca("Martin", token)
    assert cuantas(conn, "tarea_compartida") == 0


def test_quien_no_decide_no_contesta_un_pedido(conn, equipo):
    _pedido_hecho(conn, equipo)
    r = equipo.dice("Marcos", Jugada("contestar_el_pedido_del_detalle", {"acepta": True}))
    assert (r.hechos[0]["resultado"], r.hechos[0]["motivo"]) == (
        "no_se_puede", "no_hay_un_pedido_del_detalle")
    assert cuantas(conn, "tarea_compartida") == 0


# --- Revocable --------------------------------------------------------------------------------

def test_dejar_de_compartirla_vuelve_al_resumen(conn, equipo):
    _pedido_hecho(conn, equipo)
    _salir(conn, equipo, AHORA + timedelta(minutes=30))
    equipo.toca("Martin", _boton(conn, equipo, "Martin", "Compartirla"),
                at=AHORA + timedelta(minutes=40))
    personas = equipo.mundo["personas"]
    with espacio(conn, equipo.carga.workspace_id) as cur:
        quien = identificar_en_espacio(cur, personas["Martin"]["telegram"],
                                       equipo.carga.workspace_id)
        r = ejecutar(cur, quien, "dejar_de_compartir_tarea",
                     {"tarea_id": equipo.carga.tareas["SW"],
                      "membership_id": personas["Nahuel"]["membership_id"]},
                     ya_confirmada=True)
    conn.commit()
    assert r.get("revocada") is True
    assert cuantas(conn, "audit_log", "accion = 'dejar_de_compartir_tarea'") == 1
    [hecho] = _pide_el_enlace(equipo, "Nahuel", "switch").hechos
    assert hecho["resultado"] == "solo_el_resumen"


def test_dejar_de_compartirla_no_es_de_cualquiera(conn, equipo):
    _pedido_hecho(conn, equipo)
    _salir(conn, equipo, AHORA + timedelta(minutes=30))
    equipo.toca("Martin", _boton(conn, equipo, "Martin", "Compartirla"),
                at=AHORA + timedelta(minutes=40))
    personas = equipo.mundo["personas"]
    with espacio(conn, equipo.carga.workspace_id) as cur:
        quien = identificar_en_espacio(cur, personas["Nahuel"]["telegram"],
                                       equipo.carga.workspace_id)
        from leda.autoridad import Denegado
        with pytest.raises(Denegado):
            ejecutar(cur, quien, "dejar_de_compartir_tarea",
                     {"tarea_id": equipo.carga.tareas["SW"],
                      "membership_id": personas["Nahuel"]["membership_id"]},
                     ya_confirmada=True)
    conn.rollback()
    assert cuantas(conn, "tarea_compartida", "revocada_en is null") == 1


# --- Lo que dejaron la revisión y la impugnación del detalle a pedido (2026-10-09) ----------------

def _personas(t: Turnos, nombre: str) -> dict:
    return t.mundo["personas"][nombre]


def _otro_encargado_de_it(conn, t: Turnos, nombre: str = "Ariel") -> None:
    with admin(conn) as cur:
        cur.execute("update area set referente_membership_id = %s where id = %s",
                    (_personas(t, nombre)["membership_id"], t.carga.areas["it"]))
    conn.commit()


def test_si_cambia_el_encargado_antes_de_preguntarle_la_pregunta_va_al_de_ahora(conn, equipo):
    """El pedido sigue al encargado de ahora (como la revisión sigue a quien aprueba, decisiones
    16 y 43): si el sector cambió de encargado antes de que saliera la pregunta, le llega al
    nuevo, y es él quien lo ve en su lista."""
    _pedido_hecho(conn, equipo)
    _otro_encargado_de_it(conn, equipo)

    _salir(conn, equipo, AHORA + timedelta(minutes=30))

    [aviso] = avisos_guardados(conn, PEDIDO)
    assert aviso["estado"] == "enviado"
    assert str(aviso["destinatario_membership_id"]) == _personas(equipo, "Ariel")["membership_id"]
    equipo.dice("Ariel", at=AHORA + timedelta(hours=1))
    assert any(x.get("espera_que_decida_si_la_comparte") for x in equipo.situacion["tareas"])
    equipo.dice("Martin", at=AHORA + timedelta(hours=1))
    assert not any(x.get("espera_que_decida_si_la_comparte")
                   for x in equipo.situacion["tareas"])


@pytest.mark.parametrize("acepta", [True, False])
def test_un_encargado_anterior_no_decide_ni_que_si_ni_que_no(conn, equipo, acepta):
    """A Martín le llegó la pregunta y después dejó de ser el encargado: su botón (o lo que
    escriba) no decide nada, ni que sí ni que no; el pedido sigue esperando al de ahora, que lo
    decide (revisión del detalle a pedido: la base comprobaba al encargado de ahora y la cocina al
    de entonces, y el pedido quedaba trabado)."""
    _pedido_hecho(conn, equipo)
    _salir(conn, equipo, AHORA + timedelta(minutes=30))
    token = _boton(conn, equipo, "Martin", "Compartirla" if acepta else "No compartirla")
    _otro_encargado_de_it(conn, equipo)

    r = equipo.toca("Martin", token, at=AHORA + timedelta(minutes=40))

    # Su botón viejo se lo dice como todo botón de una tarea que ya no le corresponde.
    assert (r.hechos[0]["resultado"], r.hechos[0]["motivo"]) == ("no_se_puede",
                                                                 "ya_no_le_corresponde")
    [pedido] = todos(conn, "select estado from pedido_de_detalle")
    assert pedido["estado"] == "esperando_decision"
    assert cuantas(conn, "tarea_compartida") == 0
    alias = _alias_de(equipo, "Ariel", SWITCH)
    r = equipo.dice("Ariel", Jugada("contestar_el_pedido_del_detalle",
                                    {"tarea": alias, "acepta": acepta}),
                    at=AHORA + timedelta(minutes=50))
    assert (r.hechos[0]["resultado"], r.hechos[0]["la_compartio"]) == ("anotado", acepta)
    [pedido] = todos(conn, "select estado, decidido_por_membership_id::text por "
                           "from pedido_de_detalle")
    assert pedido["estado"] == ("compartida" if acepta else "no_compartida")
    assert pedido["por"] == _personas(equipo, "Ariel")["membership_id"]
    # Quien lo pidió se entera de quién lo decidió de verdad.
    [aviso] = avisos_guardados(conn, COMO_TERMINO)
    assert aviso["hechos"]["lo_decidio"] == "Ariel De Simone"


def test_si_ya_la_veia_la_auditoria_dice_lo_que_paso(conn, equipo):
    """Nahuel la empezó a ver por otro lado mientras esperaba (pasó a aprobar el trabajo de
    Lucas): decir que sí no comparte nada, y la auditoría lo dice así, nunca una tarea compartida
    sin fila (revisión del detalle a pedido, `herramientas.py:3131-3152`)."""
    _pedido_hecho(conn, equipo)
    _salir(conn, equipo, AHORA + timedelta(minutes=30))
    with admin(conn) as cur:
        cur.execute("update membership set aprobador_membership_id = %s where id = %s",
                    (_personas(equipo, "Nahuel")["membership_id"],
                     _personas(equipo, "Lucas")["membership_id"]))
    conn.commit()

    equipo.toca("Martin", _boton(conn, equipo, "Martin", "Compartirla"),
                at=AHORA + timedelta(minutes=40))

    assert cuantas(conn, "tarea_compartida") == 0
    assert cuantas(conn, "audit_log", "accion = 'compartir_tarea'") == 0
    [fila] = todos(conn, """select detalle from audit_log
                             where accion = 'decidir_detalle_de_tarea'""")
    assert fila["detalle"]["ya_la_veia"] is True and fila["detalle"]["comparte"] is True
    assert "compartida_id" not in fila["detalle"]


def test_un_no_tambien_queda_en_la_auditoria(conn, equipo):
    _pedido_hecho(conn, equipo)
    _salir(conn, equipo, AHORA + timedelta(minutes=30))

    equipo.toca("Martin", _boton(conn, equipo, "Martin", "No compartirla"),
                at=AHORA + timedelta(minutes=40))

    [fila] = todos(conn, "select actor_app_user_id::text actor, detalle from audit_log "
                         "where accion = 'no_compartir_tarea'")
    assert fila["actor"] == _personas(equipo, "Martin")["app_user_id"]
    assert fila["detalle"]["con"] == _personas(equipo, "Nahuel")["membership_id"]


class _SeCruzaOtroPedido:
    """Un cursor que, apenas la cocina mira si ya hay un pedido abierto y no lo ve, deja que
    llegue el de otro mensaje de la misma persona (la carrera de dos mensajes que se cruzan)."""

    def __init__(self, cur, otro) -> None:
        self._cur, self._otro, self.cruzo = cur, otro, False

    def execute(self, sql, params=None, **kw):
        r = self._cur.execute(sql, params, **kw)
        if (not self.cruzo and "from pedido_de_detalle" in sql
                and "esperando_decision" in sql and sql.lstrip().startswith("select")):
            self.cruzo = True
            self._otro()
        return r

    def __getattr__(self, nombre):
        return getattr(self._cur, nombre)


def test_dos_pedidos_que_se_cruzan_son_uno(conn, equipo):
    """La carrera al pedirlo (revisión del detalle a pedido, `herramientas.py:3088-3099`): el
    segundo encuentra el primero y dice que ya lo pidió, sin caerse."""
    from psycopg.rows import dict_row
    nahuel = _personas(equipo, "Nahuel")
    with espacio(conn, equipo.carga.workspace_id) as cur:
        quien = identificar_en_espacio(cur, nahuel["telegram"], equipo.carga.workspace_id)

        def otro():
            with conn.cursor(row_factory=dict_row) as aparte:
                aparte.execute(
                    """insert into pedido_de_detalle (workspace_id, task_id,
                                                      pedido_por_membership_id,
                                                      decide_membership_id, estado, pedido_en)
                       values (%s, %s, %s, %s, 'esperando_decision', %s)""",
                    (equipo.carga.workspace_id, equipo.carga.tareas["SW"],
                     nahuel["membership_id"], _personas(equipo, "Martin")["membership_id"],
                     AHORA))

        r = ejecutar(_SeCruzaOtroPedido(cur, otro), quien, "pedir_detalle_de_tarea",
                     {"tarea_id": equipo.carga.tareas["SW"], "at": AHORA.isoformat()},
                     ya_confirmada=True)
    conn.commit()
    assert r["error"] == "ya_lo_pidio"
    assert cuantas(conn, "pedido_de_detalle") == 1


# --- Una oferta "si lo necesitás" no se repite ni vuelve (decisión 33; constitución §8) ---------

def test_la_oferta_no_se_repite_a_las_cuatro_horas_y_sin_respuesta_es_un_no(conn, equipo):
    """La oferta es opcional ("si lo necesitás, le pregunto"): Leda no la repite a las 4 horas
    como una pregunta que espera respuesta (decisión 29); si la persona no contesta, es un no, y
    la oferta se cierra."""
    from leda.motor.escalera import correr_escalera
    _pide_el_enlace(equipo, "Marcos", "switch")

    for horas in (4, 5, 9):
        correr_escalera(conn, equipo.carga.workspace_id,
                        RelojFijo(AHORA + timedelta(hours=horas, minutes=5)))
        conn.commit()

    assert avisos_guardados(conn, "repeticion_del_dia") == []
    assert cuantas(conn, "conversation_question",
                   "tipo = 'propuesta' and cerrada_en is null") == 0
    assert cuantas(conn, "pedido_de_detalle") == 0


def test_la_oferta_no_vuelve_despues_de_un_cambio_de_tema(conn, equipo):
    """Marcos pide el enlace del switch, que no ve, y en vez de contestar la oferta habla de su
    PLC: la respuesta es lo nuevo y la oferta no vuelve aparte (decisión 50 es para lo que Leda
    necesita saber); se cierra como un no."""
    _pide_el_enlace(equipo, "Marcos", "switch")
    plc = _alias_de(equipo, "Marcos", "Programar el PLC")

    equipo.dice("Marcos", Jugada("anotar_inicio", {"tarea": plc}), texto="arranque el plc",
                at=AHORA + timedelta(minutes=20))

    assert avisos_guardados(conn, "vuelve_la_pregunta") == []
    assert cuantas(conn, "conversation_question",
                   "tipo = 'propuesta' and cerrada_en is null") == 0


def test_la_oferta_no_frena_lo_que_espera_a_la_persona(conn, equipo):
    """Una oferta sin contestar no es una pregunta que Leda necesita: no frena los otros temas
    (decisión 21 es para lo que Leda pregunta)."""
    from leda.motor import pregunta_sin_contestar
    _pide_el_enlace(equipo, "Marcos", "switch")
    abierta = uno(conn, """select q.* from conversation_state s
                             join conversation_question q on q.id = s.pregunta_abierta_id
                            where s.membership_id = %s""",
                  _personas(equipo, "Marcos")["membership_id"])
    with espacio(conn, equipo.carga.workspace_id) as cur:
        from leda.calendario import Calendario
        cal = Calendario.desde_base(cur, equipo.carga.workspace_id)
        assert pregunta_sin_contestar.termino_su_turno(
            cur, cal, equipo.carga.workspace_id, abierta, AHORA + timedelta(minutes=10))
    conn.commit()


# --- El encargado que no contesta (decisión 26, la misma regla que los pases) ---------------------

def _dia(dia: int, hora: int = 10):
    return octubre(dia, hora)


def _ciclo(conn, equipo, at) -> IAQueRedacta:
    from leda.motor.escalera import correr_escalera
    correr_escalera(conn, equipo.carga.workspace_id, RelojFijo(at))
    conn.commit()
    return _salir(conn, equipo, at)


RECORDATORIO = "recordatorio_del_pedido_del_detalle"


def test_si_el_encargado_no_contesta_se_le_repite_una_vez_y_termina(conn, equipo):
    """Lunes 5: Nahuel lo pide y a Martín le llega. Martes 6, el día hábil siguiente: la pregunta
    otra vez, una sola. Miércoles 7, a la hora en que Leda escribe, sigue sin contestar: el pedido
    termina sin respuesta y Nahuel se entera de que Martín no contestó; a Martín, que ya no hace
    falta (decisión 39). Nunca un tema abierto para siempre."""
    _pedido_hecho(conn, equipo)
    _salir(conn, equipo, AHORA + timedelta(minutes=30))

    _ciclo(conn, equipo, _dia(6))
    [otra_vez] = avisos_guardados(conn, RECORDATORIO)
    assert otra_vez["estado"] == "enviado"
    assert str(otra_vez["destinatario_membership_id"]) == _personas(equipo, "Martin")[
        "membership_id"]
    assert otra_vez["hechos"]["pide_ver_el_detalle"] == NAHUEL
    assert otra_vez["hechos"]["si_sigue_sin_contestar"]["fecha"] == "2026-10-07"
    _ciclo(conn, equipo, _dia(6, 15))
    assert len(avisos_guardados(conn, RECORDATORIO)) == 1      # una sola vez
    [pedido] = todos(conn, "select estado from pedido_de_detalle")
    assert pedido["estado"] == "esperando_decision"

    _ciclo(conn, equipo, _dia(7))

    [pedido] = todos(conn, "select estado from pedido_de_detalle")
    assert pedido["estado"] == "sin_respuesta"
    assert cuantas(conn, "audit_log", "accion = 'pedido_de_detalle_sin_respuesta'") == 1
    terminos = avisos_guardados(conn, COMO_TERMINO)
    a_nahuel = next(a for a in terminos if str(a["destinatario_membership_id"])
                    == _personas(equipo, "Nahuel")["membership_id"])
    assert a_nahuel["hechos"]["sin_respuesta"] is True
    assert a_nahuel["hechos"]["no_contesto"] == MARTIN
    a_martin = next(a for a in terminos if str(a["destinatario_membership_id"])
                    == _personas(equipo, "Martin")["membership_id"])
    assert a_martin["hechos"]["ya_no_espera_su_respuesta"] is True
    assert cuantas(conn, "tarea_compartida") == 0
    # Los botones de la pregunta ya no deciden nada.
    assert cuantas(conn, "conversation_question",
                   "tipo = %s and cerrada_en is null", preguntas.COMPARTIR_EL_DETALLE) == 0
    # Y puede volver a pedirlo.
    r = equipo.dice("Nahuel", Jugada("pedir_el_detalle", {"como_la_nombra": "switch"}),
                    at=_dia(7, 11))
    assert r.hechos[0]["resultado"] == "detalle_pedido"


def test_si_contesta_despues_de_la_repeticion_no_termina(conn, equipo):
    _pedido_hecho(conn, equipo)
    _salir(conn, equipo, AHORA + timedelta(minutes=30))
    _ciclo(conn, equipo, _dia(6))
    equipo.toca("Martin", _boton(conn, equipo, "Martin", "No compartirla"), at=_dia(6, 11))

    _ciclo(conn, equipo, _dia(7))

    [pedido] = todos(conn, "select estado from pedido_de_detalle")
    assert pedido["estado"] == "no_compartida"
    assert cuantas(conn, "audit_log", "accion = 'pedido_de_detalle_sin_respuesta'") == 0


def test_la_repeticion_va_al_encargado_de_ahora(conn, equipo):
    """Si el encargado cambió después de la primera pregunta, la repetición le llega al nuevo
    (decisión 16: al nuevo, lo que espera su decisión)."""
    _pedido_hecho(conn, equipo)
    _salir(conn, equipo, AHORA + timedelta(minutes=30))
    _otro_encargado_de_it(conn, equipo)

    _ciclo(conn, equipo, _dia(6))

    [otra_vez] = avisos_guardados(conn, RECORDATORIO)
    assert str(otra_vez["destinatario_membership_id"]) == _personas(equipo, "Ariel")[
        "membership_id"]


def test_el_recordatorio_del_pedido_esta_declarado():
    from leda.motor.avisos import TIPOS
    tipo = TIPOS[RECORDATORIO]
    assert tipo.tipo_de_mensaje == "seguimiento" and tipo.va_a is not None
    for codigo in (RECORDATORIO, "sin_respuesta", "no_contesto",
                   "ya_no_espera_su_respuesta", "si_sigue_sin_contestar"):
        assert hechos_mod.significado(codigo), codigo
