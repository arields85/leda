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
from tests.motor.ayudantes import AHORA, IAQueRedacta, avisos_guardados, cuantas, todos, uno
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
    (constitución §7): sin Martín conectado, el resumen sin la oferta, y dice por qué."""
    with admin(conn) as cur:
        cur.execute("update app_user set telegram_user_id = null where id = %s",
                    (equipo.mundo["personas"]["Martin"]["app_user_id"],))
    conn.commit()
    [hecho] = _pide_el_enlace(equipo, "Nahuel", "switch").hechos
    assert hecho["resultado"] == "solo_el_resumen"
    assert "se_lo_puede_pedir_a" not in hecho and "pregunta" not in hecho
    assert hecho["no_se_le_puede_escribir_a"] == {"a": MARTIN,
                                                  "motivo": "destinatario_sin_telegram"}


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
