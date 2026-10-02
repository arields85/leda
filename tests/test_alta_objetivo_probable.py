"""F-B10: el objetivo más probable primero (⭐). Jev ordena los candidatos que
salen de la base según el título de la tarea; con una decisión clara el primero
lleva ⭐ y de todos modos se pregunta (la persona elige). Si Jev duda, no
responde o falta la credencial, salen en el orden de siempre y queda registrado:
nunca en silencio."""

from __future__ import annotations

from leda import ingreso_tareas as I
from leda import jev
from leda.db import admin, espacio
from leda.jev import ClienteJevGuionado

from tests.test_alta_guiada_flujo import TITULO, _campo, _conjunto_activo, _empezar
from tests.test_task_intake import NOW, _active_choices

ETAPA = "objetivo_sin_ordenar"
# Los tres objetivos del mundo de prueba, por título: Expand (O1), Raise (O2),
# Reduce (O3), el orden alfabético de siempre.
CLARO_EL_TERCERO = {"objetivo": {"probabilities": {"O1": 0.02, "O2": 0.05, "O3": 0.93}}}


def _con_jev(monkeypatch, cliente):
    monkeypatch.setattr(jev, "desde_base", lambda api_key: cliente)


def _incidentes(conn):
    with admin(conn) as cur:
        cur.execute("select severidad, notificado_admin_en from incident "
                    "where etapa = %s", (ETAPA,))
        return cur.fetchall()


def _alta(conn, world):
    with espacio(conn, world["north-lab"]["id"]) as cur:
        _, outcome = _empezar(cur, world, title=TITULO)
        rid = outcome.request_id
        return (rid, _conjunto_activo(cur, rid), list(_active_choices(cur, rid)),
                outcome.text)


def _sin_icono(etiquetas):
    return [I.etiqueta_sin_icono(e) for e in etiquetas]


def test_con_una_decision_clara_el_mas_probable_va_primero_con_estrella(
        intake_world, conn, monkeypatch):
    cliente = ClienteJevGuionado([CLARO_EL_TERCERO])
    _con_jev(monkeypatch, cliente)
    _, activo, etiquetas, texto = _alta(conn, intake_world)
    assert activo == "objective"                      # igual se pregunta
    assert etiquetas[0].startswith("⭐ ")
    assert _sin_icono(etiquetas)[:3] == ["Reduce service delay 1",
                                         "Expand regional coverage 1",
                                         "Raise delivery quality 1"]
    assert sum(e.startswith("⭐") for e in etiquetas) == 1
    assert "⭐" in texto
    state, preguntas = cliente.pedidos[0]
    assert state["tarea"] == TITULO
    assert set(preguntas["objetivo"]["criteria"].values()) == {
        "Expand regional coverage 1", "Raise delivery quality 1",
        "Reduce service delay 1"}
    assert _incidentes(conn) == []


def test_la_estrella_no_elige_por_la_persona(intake_world, conn, monkeypatch):
    _con_jev(monkeypatch, ClienteJevGuionado([CLARO_EL_TERCERO]))
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        _, outcome = _empezar(cur, intake_world, title=TITULO)
        assert _campo(cur, outcome.request_id, "objective")["estado"] != "confirmed"


def test_tocar_el_destacado_lo_elige_como_cualquier_otro(
        intake_world, conn, monkeypatch):
    _con_jev(monkeypatch, ClienteJevGuionado([CLARO_EL_TERCERO]))
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        actor, outcome = _empezar(cur, intake_world, title=TITULO)
        opciones = _active_choices(cur, outcome.request_id)
        I.resolve_choice(cur, actor, token=opciones[next(iter(opciones))],
                         chat_id=71001, now=NOW)
        assert _campo(cur, outcome.request_id, "objective")["valor"]["title"] == \
            "Reduce service delay 1"


def test_con_duda_sale_el_orden_de_siempre_sin_estrella(
        intake_world, conn, monkeypatch):
    _con_jev(monkeypatch, ClienteJevGuionado([{"objetivo": {"probabilities": {
        "O1": 0.4, "O2": 0.4, "O3": 0.2}}}]))
    _, activo, etiquetas, texto = _alta(conn, intake_world)
    assert activo == "objective"
    assert not any("⭐" in e for e in etiquetas) and "⭐" not in texto
    assert _sin_icono(etiquetas)[:3] == ["Expand regional coverage 1",
                                         "Raise delivery quality 1",
                                         "Reduce service delay 1"]
    assert _incidentes(conn) == []


def test_si_jev_falla_sale_el_orden_de_siempre_y_queda_registrado(
        intake_world, conn, monkeypatch):
    _con_jev(monkeypatch, ClienteJevGuionado([]))      # guion agotado: JevError
    _, activo, etiquetas, _ = _alta(conn, intake_world)
    assert activo == "objective"
    assert not any("⭐" in e for e in etiquetas)
    (incidente,) = _incidentes(conn)
    assert incidente["severidad"] == "baja"
    assert incidente["notificado_admin_en"] is None


def test_sin_credencial_de_jev_se_registra_una_vez_por_espacio_y_proceso(
        intake_world, conn, monkeypatch):
    monkeypatch.setattr(jev, "desde_base", lambda api_key: None)
    monkeypatch.setattr(I, "_SIN_ORDENAR_AVISADO", set())
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        for chat in (71001, 71002):
            _, outcome = _empezar(cur, intake_world, chat=chat, title=TITULO)
            assert _conjunto_activo(cur, outcome.request_id) == "objective"
            assert not any("⭐" in e for e in _active_choices(cur, outcome.request_id))
    assert len(_incidentes(conn)) == 1


def test_con_un_solo_objetivo_no_se_llama_a_jev(intake_world, conn, monkeypatch):
    cliente = ClienteJevGuionado([])
    _con_jev(monkeypatch, cliente)
    ws = intake_world["north-lab"]
    with admin(conn) as cur:
        cur.execute("update objective set area_id = %s where workspace_id = %s "
                    "and titulo = 'Reduce service delay 1'",
                    (ws["areas"]["field"], ws["id"]))
    conn.commit()
    with espacio(conn, ws["id"]) as cur:
        _, outcome = _empezar(cur, intake_world, title=TITULO)
        assert _campo(cur, outcome.request_id, "objective")["estado"] == "confirmed"
    assert cliente.pedidos == [] and _incidentes(conn) == []


def test_jev_solo_ve_los_objetivos_del_area(intake_world, conn, monkeypatch):
    cliente = ClienteJevGuionado([{"objetivo": {"probabilities": {
        "O1": 0.9, "O2": 0.05}}}])
    _con_jev(monkeypatch, cliente)
    ws = intake_world["north-lab"]
    with admin(conn) as cur:
        for titulo, area in (("Reduce service delay 1", "field"),
                             ("Expand regional coverage 1", "field"),
                             ("Raise delivery quality 1", "quality")):
            cur.execute("update objective set area_id = %s where workspace_id = %s "
                        "and titulo = %s", (ws["areas"][area], ws["id"], titulo))
    conn.commit()
    _alta(conn, intake_world)
    assert set(cliente.pedidos[0][1]["objetivo"]["criteria"].values()) == {
        "Expand regional coverage 1", "Reduce service delay 1"}


def test_buscar_por_nombre_no_dice_opciones_que_coinciden_y_hace_una_pregunta(
        intake_world, conn, monkeypatch):
    _con_jev(monkeypatch, ClienteJevGuionado([]))
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        actor, outcome = _empezar(cur, intake_world, title=TITULO)
        resultado = I._open_entity_page(
            cur, I._request(cur, outcome.request_id), actor, "objective",
            "service", 0, NOW)
        assert "Opciones que coinciden" not in resultado.text
        assert "«service»" in resultado.text and "¿A qué objetivo" in resultado.text


def test_con_la_variante_a_la_pregunta_con_estrella_pasa_la_verificacion(
        intake_world, conn, monkeypatch):
    from tests.test_alta_guiada_flujo import _cuerpos
    from tests.test_alta_guiada_mensaje_entero import _a, _Eco, _intentos

    _con_jev(monkeypatch, ClienteJevGuionado([CLARO_EL_TERCERO]))
    ws = intake_world["north-lab"]["id"]
    _a(conn, ws, monkeypatch, _Eco())
    with espacio(conn, ws) as cur:
        _, outcome = _empezar(cur, intake_world, title=TITULO)
        cuerpos = _cuerpos(cur, outcome.request_id)
    assert any("⭐" in c for c in cuerpos), cuerpos
    assert [i["resultado"] for i in _intentos(conn, ws)] == ["aceptada"]
