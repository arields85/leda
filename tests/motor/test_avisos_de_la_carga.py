"""Los avisos de la carga desde la web y de lo pedido a otra área (porción J4b; `leda.motor.carga`;
decisiones del usuario del 2026-10-14 D1b, D4, D6, D7, D8, D9 y D14).

El equipo es el de las garantías de la carga (`tests/garantias/test_carga_del_equipo.py`): North
Lab, con Morgan Hale en Dirección (Ismael), Taylor Quinn referente de Field (Martín), Sam Noble
referente de Quality (Marcos), Sam North de Field y Alex Rivera de Quality (Nahuel).

- **A quien la hace** (D6): un mensaje con todas las tareas que le cargaron seguidas, unos 10 minutos
  después de la última, dentro del horario; de coordinación (fuera del tope diario).
- **A quien la revisa** (D7), sólo si no la cargó él ni la hace.
- **Dirección no se entera** de lo que un referente se carga o le carga a su gente (D4, D8).
- **Un pedido a otra área** dice quién lo pide y que quien lo recibe decide quién lo hace (D14); un
  pedido a Dirección, quién lo pide (D1b).
- **Sin Leda conectada** (D9): la administración recibe el aviso para conectarla, y sus tareas le
  llegan juntas cuando se conecta.
- **Lo pedido** (D14, pasos 4 a 6): cuando termina, a quien lo pidió (y a quien lo esperaba); cuando
  se reabre, al referente que lo recibe, con el motivo; cuando vuelve a terminar, otra vez.
"""

from __future__ import annotations

from datetime import timedelta

from leda.db import admin
from leda.motor import carga
from leda.motor.avisos import enviar_avisos
from leda.motor.tiempo import RelojFijo

from tests.garantias.test_carga_de_tareas import AHORA, sesion  # noqa: F401 -- `sesion`
from tests.garantias.test_carga_del_equipo import (  # noqa: F401 -- `equipo` es la fixture
    _aprobar, _como, _entregar, _id, _norte, _pedida_y_terminada, _reabrir,
    _sesion_del_equipo, equipo)
from tests.motor.ayudantes import IAQueRedacta, todos, uno

NUEVAS = "tareas_nuevas"
PARA_REVISAR = "tareas_nuevas_para_revisar"
TERMINO = "lo_pedido_termino"
SE_REABRIO = "lo_pedido_se_reabrio"


# --- Ayudas ---------------------------------------------------------------------------------

def _cargar(conn, mundo, quien: str, at=AHORA, **cambios) -> str:
    """Carga por la puerta del equipo y guarda sus avisos, como `web_app._cargar`."""
    from leda.db import espacio

    r = _como(conn, mundo, quien, ahora=at, **cambios)
    assert r["ok"], r
    with espacio(conn, _norte(mundo)["id"]) as cur:
        carga.avisar_la_carga(cur, _norte(mundo)["id"], str(r["task_id"]), at,
                              cargada_por_app_user=mundo["north-lab"]["people"][quien]
                              ["app_user_id"], por_la_administracion=False)
    conn.commit()
    return str(r["task_id"])


def _avisos(conn, tipo: str | None = None) -> list[dict]:
    return [a for a in todos(conn, "select * from scheduled_notice order by creado_en, dedupe_key")
            if tipo is None or a["tipo"] == tipo]


def _para(conn, mundo, tipo: str, nombre: str) -> list[dict]:
    return [a for a in _avisos(conn, tipo)
            if str(a["destinatario_membership_id"]) == _id(mundo, nombre)]


def _enviar(conn, mundo, at) -> IAQueRedacta:
    ia = IAQueRedacta()
    enviar_avisos(conn, _norte(mundo)["id"], ia, RelojFijo(at))
    conn.commit()
    return ia


def _hechos(ia: IAQueRedacta, persona: str) -> list[dict]:
    return [h for p in ia.pedidos_de_redaccion if p["persona"].startswith(persona)
            for h in p["hechos"]]


def _terminar(conn, task_id: str) -> None:
    with admin(conn) as cur:
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind)
                       values (%s, 'en_revision', 'terminada', 'persona')""", (task_id,))
    conn.commit()


def _los_pedidos(conn, mundo, at=AHORA) -> dict:
    r = carga.avisar_lo_de_los_pedidos(conn, _norte(mundo)["id"], RelojFijo(at))
    conn.commit()
    return r


# --- A quien la hace (D6) ---------------------------------------------------------------------

def test_las_tareas_cargadas_seguidas_van_en_un_mensaje_despues_de_la_ultima(conn, equipo):
    primera = _cargar(conn, equipo, "Taylor Quinn")
    _cargar(conn, equipo, "Taylor Quinn", at=AHORA + timedelta(minutes=5),
            titulo="Probar el módem")
    [aviso] = _avisos(conn)
    assert aviso["tipo"] == NUEVAS
    assert str(aviso["destinatario_membership_id"]) == _id(equipo, "Sam North")
    assert aviso["programado_para"] == AHORA + timedelta(minutes=15)
    assert aviso["dedupe_key"] == f"motor:{NUEVAS}:{primera}:{_id(equipo, 'Sam North')}"
    # Antes del margen de la última, nada.
    assert _enviar(conn, equipo, AHORA + timedelta(minutes=12)).pedidos_de_redaccion == []
    ia = _enviar(conn, equipo, AHORA + timedelta(minutes=16))
    [hecho] = _hechos(ia, "Sam North")
    assert hecho["aviso"] == NUEVAS and hecho["necesita_respuesta"] is False
    tareas = hecho["tareas_que_le_cargaron"]
    assert [t["tarea"] for t in tareas] == ["Colgar el módem en la pared", "Probar el módem"]
    assert tareas[0] == {"tarea": "Colgar el módem en la pared", "vence": "2026-10-16",
                         "objetivo": "Reduce service delay 1", "la_cargo": "Taylor Quinn 1",
                         "la_revisa": "Taylor Quinn 1"}
    # Sin la dirección pública, ningún enlace se promete.
    assert "lleva_el_boton" not in hecho
    salida = uno(conn, "select * from message_outbox where not es_respuesta")
    assert salida["es_coordinacion"] is True and salida["tipo"] == "informativo"


def test_con_la_direccion_publica_lleva_el_boton_que_abre_la_tarea(conn, equipo, monkeypatch):
    """ADR 0024, decisión 2: el aviso de una tarea lleva "Ver la tarea", que abre esa tarea (no la
    página principal); el de varias, "Ver mis tareas"."""
    import dataclasses

    from leda import config as config_mod

    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url="https://leda.example"))
    tarea = _cargar(conn, equipo, "Taylor Quinn")
    [hecho] = _hechos(_enviar(conn, equipo, AHORA + timedelta(minutes=11)), "Sam North")
    assert hecho["lleva_el_boton"] == "Ver la tarea"
    salida = uno(conn, "select id from message_outbox where not es_respuesta")
    marca = uno(conn, "select * from message_outbox_entrada_web where outbox_id = %s",
                salida["id"])
    assert str(marca["membership_id"]) == _id(equipo, "Sam North")
    assert (marca["es_ofrecimiento"], marca["destino"], str(marca["task_id"])) == (
        False, "tarea", tarea)

    _cargar(conn, equipo, "Taylor Quinn", at=AHORA + timedelta(hours=1), titulo="Probar el módem")
    _cargar(conn, equipo, "Taylor Quinn", at=AHORA + timedelta(hours=1, minutes=1),
            titulo="Medir la señal")
    [hecho] = _hechos(_enviar(conn, equipo, AHORA + timedelta(hours=2)), "Sam North")
    assert len(hecho["tareas_que_le_cargaron"]) == 2
    assert hecho["lleva_el_boton"] == "Ver mis tareas"


def test_fuera_del_horario_sale_al_empezar_el_siguiente(conn, equipo):
    tarde = AHORA.replace(hour=20, minute=55)     # 17:55 en Buenos Aires: sale 18:05, fuera
    _cargar(conn, equipo, "Taylor Quinn", at=tarde)
    assert _enviar(conn, equipo, tarde + timedelta(minutes=11)).pedidos_de_redaccion == []
    manana = AHORA.replace(day=15, hour=11, minute=1)    # 08:01 del jueves
    assert len(_hechos(_enviar(conn, equipo, manana), "Sam North")) == 1


def test_una_tarea_que_ya_no_sigue_abierta_no_va(conn, equipo):
    _cargar(conn, equipo, "Taylor Quinn")
    otra = _cargar(conn, equipo, "Taylor Quinn", titulo="Probar el módem")
    with admin(conn) as cur:
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind, motivo)
                       values (%s, 'asignada', 'cancelada', 'persona', 'ya no hace falta')""",
                    (otra,))
    conn.commit()
    [hecho] = _hechos(_enviar(conn, equipo, AHORA + timedelta(minutes=11)), "Sam North")
    assert [t["tarea"] for t in hecho["tareas_que_le_cargaron"]] == [
        "Colgar el módem en la pared"]


# --- A quien la revisa (D7) y Dirección (D4, D8) ------------------------------------------------

def test_a_quien_la_revisa_si_no_la_cargo_el(conn, equipo):
    _cargar(conn, equipo, "Morgan Hale", revisa=_id(equipo, "Sam Noble"))
    assert len(_para(conn, equipo, NUEVAS, "Sam North")) == 1
    assert len(_para(conn, equipo, PARA_REVISAR, "Sam Noble")) == 1
    assert _para(conn, equipo, NUEVAS, "Morgan Hale") == []
    ia = _enviar(conn, equipo, AHORA + timedelta(minutes=11))
    [a_north] = _hechos(ia, "Sam North")
    assert a_north["tareas_que_le_cargaron"][0]["la_cargo"] == "Morgan Hale 1"
    assert a_north["tareas_que_le_cargaron"][0]["la_revisa"] == "Sam Noble 1"
    [a_noble] = _hechos(ia, "Sam Noble")
    assert a_noble["aviso"] == PARA_REVISAR
    [tarea] = a_noble["tareas_que_va_a_revisar"]
    assert tarea["la_hace"] == "Sam North 1" and tarea["la_cargo"] == "Morgan Hale 1"
    assert "la_revisa" not in tarea


def test_direccion_no_se_entera_de_lo_que_un_referente_carga_para_si_o_para_su_gente(conn,
                                                                                     equipo):
    _cargar(conn, equipo, "Taylor Quinn", responsable=_id(equipo, "Taylor Quinn"))
    _cargar(conn, equipo, "Taylor Quinn", titulo="Probar el módem")
    assert [(a["tipo"], str(a["destinatario_membership_id"])) for a in _avisos(conn)] == [
        (NUEVAS, _id(equipo, "Sam North"))]


def test_la_administracion_carga_y_quien_la_decidio_se_dice(conn, equipo):
    from leda.db import espacio

    r = _como(conn, equipo, "Morgan Hale")      # la tarea; los avisos, como por la otra puerta
    with espacio(conn, _norte(equipo)["id"]) as cur:
        guardados = carga.avisar_la_carga(cur, _norte(equipo)["id"], str(r["task_id"]), AHORA,
                                          cargada_por_app_user=None, por_la_administracion=True,
                                          decidio=_id(equipo, "Morgan Hale"))
    conn.commit()
    # La revisa Taylor (el referente de Sam North): no la cargó, así que se entera.
    assert guardados == [NUEVAS, PARA_REVISAR]
    [hecho] = _hechos(_enviar(conn, equipo, AHORA + timedelta(minutes=11)), "Sam North")
    tarea = hecho["tareas_que_le_cargaron"][0]
    assert tarea["la_cargo"] == "la_administracion" and tarea["la_decidio"] == "Morgan Hale 1"


# --- Los pedidos (D14, D1b) ---------------------------------------------------------------------

def test_un_pedido_a_otra_area_dice_quien_lo_pide_y_que_el_decide_quien_lo_hace(conn, equipo):
    _cargar(conn, equipo, "Taylor Quinn", responsable=_id(equipo, "Sam Noble"))
    # La revisa Sam Noble, que la recibe: no hay aviso aparte para revisarla.
    assert [a["tipo"] for a in _avisos(conn)] == [NUEVAS]
    [hecho] = _hechos(_enviar(conn, equipo, AHORA + timedelta(minutes=11)), "Sam Noble")
    [tarea] = hecho["tareas_que_le_cargaron"]
    assert tarea["la_pide"] == "Taylor Quinn 1"
    assert tarea["para_el_area"] == "Field Services"
    assert tarea["decide_quien_la_hace"] is True
    assert "la_revisa" not in tarea


def test_un_pedido_a_direccion_dice_quien_lo_pide(conn, equipo):
    _cargar(conn, equipo, "Taylor Quinn", responsable=_id(equipo, "Morgan Hale"))
    [hecho] = _hechos(_enviar(conn, equipo, AHORA + timedelta(minutes=11)), "Morgan Hale")
    [tarea] = hecho["tareas_que_le_cargaron"]
    assert tarea["la_pide"] == "Taylor Quinn 1" and tarea["es_un_pedido_a_direccion"] is True
    assert tarea["la_revisa"] == "Taylor Quinn 1"
    assert "decide_quien_la_hace" not in tarea


# --- Sin Leda conectada (D9) --------------------------------------------------------------------

def test_sin_leda_conectada_la_administracion_se_entera_y_sus_tareas_esperan(conn, equipo):
    north = equipo["north-lab"]["people"]["Sam North"]
    with admin(conn) as cur:
        cur.execute("update app_user set telegram_user_id = null where id = %s",
                    (north["app_user_id"],))
    conn.commit()
    _cargar(conn, equipo, "Taylor Quinn")
    _cargar(conn, equipo, "Taylor Quinn", titulo="Probar el módem")
    incidentes = todos(conn, "select * from incident where etapa = 'motor_sin_leda_conectada'")
    assert len(incidentes) == 1, "uno por persona y por día"
    assert "Sam North 1" in incidentes[0]["resumen_sanitizado"]
    assert _enviar(conn, equipo, AHORA + timedelta(minutes=30)).pedidos_de_redaccion == []
    [aviso] = _avisos(conn, NUEVAS)
    assert aviso["estado"] == "guardado"
    # Se conecta: le llegan sus tareas juntas.
    with admin(conn) as cur:
        cur.execute("update app_user set telegram_user_id = %s where id = %s",
                    (north["telegram"], north["app_user_id"]))
    conn.commit()
    [hecho] = _hechos(_enviar(conn, equipo, AHORA + timedelta(hours=2)), "Sam North")
    assert len(hecho["tareas_que_le_cargaron"]) == 2


# --- Lo pedido que termina y se reabre (D14, pasos 4 a 6) ------------------------------------------

def test_lo_pedido_que_termina_le_llega_a_quien_lo_pidio_una_vez_por_cierre(conn, equipo):
    tarea = _pedida_y_terminada(conn, equipo)
    assert _los_pedidos(conn, equipo) == {TERMINO: 1}
    assert _los_pedidos(conn, equipo) == {}
    [hecho] = _hechos(_enviar(conn, equipo, AHORA + timedelta(minutes=1)), "Taylor Quinn")
    assert hecho == {"aviso": TERMINO, "necesita_respuesta": False,
                     "tarea": "Colgar el módem en la pared", "la_hizo": "Alex Rivera 1",
                     "la_aprobo": "Sam Noble 1", "la_pediste": True}

    # Taylor pide cambios: vuelve a Sam Noble con el motivo.
    r = _reabrir(conn, _sesion_del_equipo(conn, equipo, "Taylor Quinn"), tarea,
                 "El módem quedó torcido")
    assert r["ok"], r
    assert _los_pedidos(conn, equipo) == {SE_REABRIO: 1}
    [hecho] = _hechos(_enviar(conn, equipo, AHORA + timedelta(minutes=2)), "Sam Noble")
    assert hecho == {"aviso": SE_REABRIO, "necesita_respuesta": False,
                     "tarea": "Colgar el módem en la pared", "la_reabrio": "Taylor Quinn 1",
                     "motivo_de_la_reapertura": "El módem quedó torcido",
                     "decide_quien_la_retoma": True, "la_tenia": "Alex Rivera 1"}

    # Sam Noble la vuelve a aprobar: a Taylor le llega otra vez.
    _entregar(conn, equipo, tarea)
    _aprobar(conn, equipo, tarea, "Sam Noble")
    _terminar(conn, tarea)
    assert _los_pedidos(conn, equipo, AHORA + timedelta(minutes=3)) == {TERMINO: 1}
    assert len(_para(conn, equipo, TERMINO, "Taylor Quinn")) == 2


def test_quien_esperaba_lo_pedido_se_entera_de_que_puede_seguir(conn, equipo):
    """D1b: Taylor le pide a Dirección aprobar la compra; la tarea de Sam North la espera. Lo da por
    cumplido Taylor, así que a Taylor no le llega nada; a Sam North, que puede seguir."""
    pedido = _cargar(conn, equipo, "Taylor Quinn", responsable=_id(equipo, "Morgan Hale"),
                     titulo="Aprobar la compra del servidor")
    _cargar(conn, equipo, "Taylor Quinn", titulo="Instalar el servidor", espera=pedido)
    _entregar(conn, equipo, pedido)
    _aprobar(conn, equipo, pedido, "Taylor Quinn")
    _terminar(conn, pedido)
    assert _los_pedidos(conn, equipo) == {TERMINO: 1}
    assert _para(conn, equipo, TERMINO, "Taylor Quinn") == []
    ia = _enviar(conn, equipo, AHORA + timedelta(minutes=11))
    [hecho] = [h for h in _hechos(ia, "Sam North") if h["aviso"] == TERMINO]
    assert hecho["la_pidio"] == "Taylor Quinn 1"
    assert hecho["tareas_que_la_esperaban"] == [{"tarea": "Instalar el servidor",
                                                 "ya_puede_seguir": True}]
    assert _hechos(ia, "Taylor Quinn") == []
    assert _los_pedidos(conn, equipo) == {}


def test_lo_que_aprobo_quien_lo_pidio_sin_nadie_que_lo_espere_no_se_cuenta(conn, equipo):
    """Nadie a quien contarle: el aviso queda omitido con su motivo, nunca en silencio, y el cierre
    no se vuelve a mirar."""
    pedido = _cargar(conn, equipo, "Taylor Quinn", responsable=_id(equipo, "Morgan Hale"))
    _entregar(conn, equipo, pedido)
    _aprobar(conn, equipo, pedido, "Taylor Quinn")
    _terminar(conn, pedido)
    assert _los_pedidos(conn, equipo) == {}
    [aviso] = _para(conn, equipo, TERMINO, "Taylor Quinn")
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "la_aprobo_quien_la_pidio")
    assert _los_pedidos(conn, equipo) == {}
    assert len(_avisos(conn, TERMINO)) == 1


def test_un_cierre_que_no_salio_antes_de_reabrirse_no_se_cuenta_dos_veces(conn, equipo):
    """Revisión de la J4b (R3-termino-duplicado): el aviso del primer cierre todavía no salió
    (fuera de horario o en la cola) cuando la tarea se reabre y se vuelve a cerrar. Al salir, sólo
    cuenta el último cierre: quien lo pidió se entera una vez, no dos."""
    tarea = _pedida_y_terminada(conn, equipo)
    assert _los_pedidos(conn, equipo) == {TERMINO: 1}
    r = _reabrir(conn, _sesion_del_equipo(conn, equipo, "Taylor Quinn"), tarea,
                 "El módem quedó torcido")
    assert r["ok"], r
    _entregar(conn, equipo, tarea)
    _aprobar(conn, equipo, tarea, "Sam Noble")
    _terminar(conn, tarea)
    assert _los_pedidos(conn, equipo, AHORA + timedelta(minutes=1)) == {TERMINO: 1,
                                                                        SE_REABRIO: 1}
    ia = _enviar(conn, equipo, AHORA + timedelta(minutes=2))
    assert len([h for h in _hechos(ia, "Taylor Quinn") if h["aviso"] == TERMINO]) == 1
    viejo, nuevo = _para(conn, equipo, TERMINO, "Taylor Quinn")
    assert (viejo["estado"], viejo["motivo_omision"]) == ("omitido", "se_reabrio_antes")
    assert nuevo["estado"] == "enviado"
