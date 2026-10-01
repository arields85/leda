"""El alta guiada sobre el flujo de un mensaje (ADR 0014, F3a): título primero,
valores normalizados por el modelo y validados por el código (M1), y nunca un
valor inventado.

Cubre R4c-H4 (el orden), R4c-H6 (las fechas dichas de cualquier forma) y la
parte de R4c-H5 que es del alta (pedir otra tarea a mitad del alta no reinicia
ni entra en bucle). Los valores del modelo se guionan como `IntentRoute.valor`:
ninguna prueba toca la red ni interpreta texto libre con el código.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest
from psycopg.types.json import Jsonb

from prisma import gateway
from prisma import ingreso_tareas as I
from prisma.db import admin, espacio
from prisma.llm import IntentAction, IntentRoute, RespectoPendiente

from tests.test_task_intake import (NOW, _RoutingProvider, _actor,  # noqa: F401
                                    _active_choices, _choose, _post_message)

CHAT = 71001
TITULO = "Revisar el variador de la comprimidora"


def _entrante(cur, ws, actor, texto="Necesito crear una tarea", n=800,
              chat=CHAT) -> str:
    cur.execute(
        """insert into inbound_message
             (workspace_id, telegram_message_id, chat_id, app_user_id, texto)
           values (%s, %s, %s, %s, %s) returning id""",
        (ws, n, chat, actor.app_user_id, texto))
    return str(cur.fetchone()["id"])


def _empezar(cur, world, chat=CHAT, **propuestas):
    ws = world["north-lab"]["id"]
    actor = _actor(cur, world)
    inbound = _entrante(cur, ws, actor, n=900 + chat, chat=chat)
    outcome = I.start(cur, actor, chat_id=chat, source_inbound_id=inbound,
                      source_raw_text="Necesito crear una tarea",
                      proposals=propuestas, now=NOW)
    return actor, outcome


def _elegir(cur, actor, rid, parte, chat=CHAT):
    """Toca el botón cuya etiqueta contiene `parte`."""
    etiqueta = next(e for e in _active_choices(cur, rid) if parte in e)
    return _choose(cur, actor, rid, etiqueta, chat_id=chat)


def _campo(cur, rid, campo) -> dict:
    cur.execute("""select estado, valor, proposed_by from task_intake_field
                    where request_id = %s and campo = %s""", (rid, campo))
    return cur.fetchone()


def _slot(cur, rid) -> str | None:
    cur.execute("""select campo from task_intake_free_text_slot
                    where request_id = %s and estado = 'active'""", (rid,))
    fila = cur.fetchone()
    return fila["campo"] if fila else None


def _conjunto_activo(cur, rid) -> str | None:
    cur.execute("""select campo from task_intake_choice_set
                    where request_id = %s and estado = 'active'""", (rid,))
    fila = cur.fetchone()
    return fila["campo"] if fila else None


def _incidentes(conn, etapa) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where etapa = %s", (etapa,))
        return cur.fetchone()["n"]


def _cuerpos(cur, rid) -> list[str]:
    cur.execute("""select cuerpo from message_outbox
                    where dedupe_key like %s order by programado_para, id""",
                (f"intake:{rid}:%",))
    return [f["cuerpo"] for f in cur.fetchall()]


# ---------------------------------------------------------------- el orden

def test_sin_la_tarea_en_el_mensaje_pregunta_primero_que_hay_que_hacer(
        intake_world, conn):
    """R4c-H4: empezaba por "Elegí el objetivo" sin saber qué tarea era."""
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        _, outcome = _empezar(cur, intake_world)
        assert outcome.text == "¿Qué hay que hacer?"
        assert _slot(cur, outcome.request_id) == "title"
        assert _conjunto_activo(cur, outcome.request_id) is None


@pytest.mark.parametrize("titulo", [TITULO, "Cablear el tablero norte", "x"])
def test_si_el_mensaje_ya_trae_la_tarea_se_toma_el_titulo_y_sigue_el_objetivo(
        titulo, intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        _, outcome = _empezar(cur, intake_world, title=titulo)
        titulo_guardado = _campo(cur, outcome.request_id, "title")
        assert titulo_guardado["estado"] == "confirmed"
        assert titulo_guardado["valor"] == titulo
        assert _conjunto_activo(cur, outcome.request_id) == "objective"
        assert _slot(cur, outcome.request_id) is None


def test_el_titulo_escrito_por_la_persona_lo_normaliza_el_modelo(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, outcome = _empezar(cur, intake_world)
        rid = outcome.request_id
        inbound = _entrante(cur, ws, actor, "ah, revisar el variador", n=801)
        resultado = I.consume_pending_text(
            cur, actor, chat_id=CHAT, source_inbound_id=inbound,
            source_raw_text="ah, revisar el variador", now=NOW,
            valor={"texto": "Revisar el variador"})
        assert resultado is not None and resultado.changed
        titulo = _campo(cur, rid, "title")
        assert titulo["estado"] == "confirmed"
        assert titulo["valor"] == "Revisar el variador"      # lo que normalizó
        assert _conjunto_activo(cur, rid) == "objective"


# ------------------------------------------------------------- las fechas

def _en_la_fecha(cur, world):
    """El alta con todo confirmado menos la fecha objetivo, que espera."""
    ws = world["north-lab"]["id"]
    actor, outcome = _empezar(cur, world, title=TITULO)
    rid = outcome.request_id
    _elegir(cur, actor, rid, "Reduce service delay")
    _elegir(cur, actor, rid, "Sam North")
    if _conjunto_activo(cur, rid) == "area":     # hasta que se complete sola (F3b)
        _elegir(cur, actor, rid, "Field Services")
    assert _slot(cur, rid) == "due_date", _conjunto_activo(cur, rid)
    return actor, rid, ws


def _decir_fecha(cur, world, actor, rid, ws, valor, texto="el 4 de octubre", n=810):
    inbound = _entrante(cur, ws, actor, texto, n=n)
    return I.consume_pending_text(
        cur, actor, chat_id=CHAT, source_inbound_id=inbound,
        source_raw_text=texto, now=NOW, valor=valor)


@pytest.mark.parametrize(("texto", "iso"), [
    ("4de octubre", "2028-10-04"),       # R4c-H6: sin espacio
    ("04 / 10", "2028-10-04"),           # R4c-H6: espacios junto a la barra
    ("el viernes 3 de marzo", "2028-03-03"),
    ("mañana", "2028-02-29"),
])
def test_una_fecha_dicha_de_cualquier_forma_la_resuelve_el_modelo_y_el_codigo_la_valida(
        texto, iso, intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, rid, ws = _en_la_fecha(cur, intake_world)
        resultado = _decir_fecha(cur, intake_world, actor, rid, ws,
                                 {"fecha_iso": iso}, texto)
        assert resultado is not None
        fecha = _campo(cur, rid, "due_date")
        assert fecha["estado"] == "confirmed" and fecha["valor"] == iso
        assert _slot(cur, rid) == "acceptance_criterion"     # sigue el alta


@pytest.mark.parametrize(("valor", "en_el_texto"), [
    ({"fecha_iso": "2028-02-01"}, ("ya pasó", "desde hoy")),     # pasada
    ({"fecha_iso": "2028-02-30"}, ("no existe", "desde hoy")),   # no existe
    ({"fecha_iso": "4 de octubre"}, ("no existe", "desde hoy")),  # mal formado
])
def test_una_fecha_que_no_sirve_dice_la_razon_y_la_pregunta_sigue_abierta(
        valor, en_el_texto, intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, rid, ws = _en_la_fecha(cur, intake_world)
        resultado = _decir_fecha(cur, intake_world, actor, rid, ws, valor)
        assert resultado is not None and resultado.inert
        for parte in en_el_texto:
            assert parte in resultado.text
        assert _campo(cur, rid, "due_date")["estado"] == "missing"
        assert _slot(cur, rid) == "due_date"                 # la misma pregunta
        assert _cuerpos(cur, rid).count(resultado.text) == 1  # una sola vez
    # Es conversación normal, no una falla: sin incidente.
    assert _incidentes(conn, I.ETAPA_VALOR_SIN_INTERPRETAR) == 0


@pytest.mark.parametrize("valor", [None, {}, {"opcion_id": "1"},
                                   {"falta": "cual"}])   # la falta de otro tipo
def test_sin_valor_la_pregunta_queda_abierta_con_incidente_y_aviso_neutro(
        valor, intake_world, conn):
    """El modelo no pudo interpretar: nunca se inventa el valor."""
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, rid, ws = _en_la_fecha(cur, intake_world)
        resultado = _decir_fecha(cur, intake_world, actor, rid, ws, valor)
        assert resultado is not None and resultado.inert
        assert I.NOTICIA_NEUTRA_INCIDENTE in resultado.text
        assert "¿Para cuándo" in resultado.text              # y la misma pregunta
        assert _campo(cur, rid, "due_date")["estado"] == "missing"
        assert _slot(cur, rid) == "due_date"
    assert _incidentes(conn, I.ETAPA_VALOR_SIN_INTERPRETAR) == 1
    # F-B4: el incidente apunta al mensaje que lo disparó (como los de otras
    # etapas), así el aviso a la administración no dice "sin referencia".
    with admin(conn) as cur:
        cur.execute("""select referencia_tipo, referencia_id, chat_id, app_user_id
                         from incident where etapa = %s""",
                    (I.ETAPA_VALOR_SIN_INTERPRETAR,))
        incidente = cur.fetchone()
    assert incidente["referencia_tipo"] == "inbound_message"
    assert incidente["referencia_id"] is not None
    assert incidente["chat_id"] == CHAT and incidente["app_user_id"] is not None


@pytest.mark.parametrize("texto", [
    "la semana que viene", "a fin de mes", "en octubre", "pronto", "después del feriado",
])
def test_una_fecha_incompleta_repregunta_el_dia_sin_incidente(
        texto, intake_world, conn):
    """F-B1: un período ("la semana que viene") es una respuesta parcial, no una
    falla: la misma pregunta sigue abierta y se pide el día, sin incidente ni
    aviso técnico."""
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, rid, ws = _en_la_fecha(cur, intake_world)
        resultado = _decir_fecha(cur, intake_world, actor, rid, ws,
                                 {"falta": "dia"}, texto)
        assert resultado is not None and resultado.inert
        assert "día exacto" in resultado.text
        assert I.NOTICIA_NEUTRA_INCIDENTE not in resultado.text
        assert _campo(cur, rid, "due_date")["estado"] == "missing"
        assert _slot(cur, rid) == "due_date"                 # la misma pregunta
        assert _cuerpos(cur, rid).count(resultado.text) == 1
    assert _incidentes(conn, I.ETAPA_VALOR_SIN_INTERPRETAR) == 0


@pytest.mark.parametrize("texto", ["algo que sirva", "lo que corresponda"])
def test_un_texto_demasiado_general_pide_detalle_sin_incidente(
        texto, intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, rid, ws = _en_la_fecha(cur, intake_world)
        _decir_fecha(cur, intake_world, actor, rid, ws,
                     {"fecha_iso": "2028-03-05"})
        assert _slot(cur, rid) == "acceptance_criterion"
        inbound = _entrante(cur, ws, actor, texto, n=820)
        resultado = I.consume_pending_text(
            cur, actor, chat_id=CHAT, source_inbound_id=inbound,
            source_raw_text=texto, now=NOW, valor={"falta": "detalle"})
        assert resultado is not None and resultado.inert
        assert "detalle" in resultado.text
        assert _slot(cur, rid) == "acceptance_criterion"
    assert _incidentes(conn, I.ETAPA_VALOR_SIN_INTERPRETAR) == 0


@pytest.mark.parametrize(("chat", "propuesta", "parte"), [
    (72001, "2028-01-05", "ya pasó"),       # pasada
    (72002, "29/2", "no existe"),           # sin formato ISO
    (72003, "el viernes", "no existe"),     # relativa: sin hoy no se resuelve
])
def test_la_fecha_que_propuso_el_modelo_se_valida_y_si_no_sirve_se_dice(
        chat, propuesta, parte, intake_world, conn):
    """Antes se descartaba sin avisar si el código no la entendía."""
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        _, outcome = _empezar(cur, intake_world, chat=chat, title=TITULO,
                              due_date=propuesta)
        assert _campo(cur, outcome.request_id, "due_date")["estado"] == "missing"
        assert "fecha objetivo" in outcome.text
        assert parte in outcome.text
        assert _conjunto_activo(cur, outcome.request_id) == "objective"


def test_la_fecha_que_propuso_el_modelo_y_sirve_queda_propuesta(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        _, outcome = _empezar(cur, intake_world, title=TITULO,
                              due_date="2028-03-05")
        fecha = _campo(cur, outcome.request_id, "due_date")
        assert fecha["estado"] == "proposed" and fecha["valor"] == "2028-03-05"


def test_ya_no_hay_un_interprete_de_fechas_por_expresiones_regulares():
    """ADR 0014: un camino está migrado cuando se retiran sus mecanismos viejos."""
    assert not hasattr(I, "_parse_absolute_date")
    assert not hasattr(I, "resolve_date")
    assert not hasattr(I, "AmbiguousDate")


# ------------------------------------------- respuestas escritas (gateway)

_ids_de_mensaje = iter(range(3000, 4000))


def _usuario(world) -> int:
    return world["north-lab"]["people"]["Taylor Quinn"]["telegram"]


def _alta_en_el_objetivo(conn, world, **propuestas) -> tuple[int, str]:
    user = _usuario(world)
    with espacio(conn, world["north-lab"]["id"]) as cur:
        _, outcome = _empezar(cur, world, chat=user, title=TITULO, **propuestas)
        assert _conjunto_activo(cur, outcome.request_id) == "objective"
    conn.commit()
    return user, outcome.request_id


def _escribir(conn, monkeypatch, world, provider, texto):
    return _post_message(conn, monkeypatch, world, provider, texto,
                         message_id=next(_ids_de_mensaje))


def _ruta(valor=None, comando=RespectoPendiente.RESPONDE) -> IntentRoute:
    return IntentRoute(IntentAction.NORMAL_CONVERSATION,
                       respecto_pendiente=comando, valor=valor or {})


def _salidas(conn, chat) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("""select id, cuerpo, intake_choice_set_id, pending_action_id
                         from message_outbox where chat_id = %s
                        order by programado_para, id""", (chat,))
        return cur.fetchall()


def _nuevas(conn, chat, antes: list[dict]) -> list[dict]:
    """Lo que salió después de `antes`: el armado del alta usa un reloj fijo
    (`NOW`), así que no se compara por posición."""
    vistos = {f["id"] for f in antes}
    return [f for f in _salidas(conn, chat) if f["id"] not in vistos]


def _estado(conn, rid, campo) -> dict:
    with admin(conn) as cur:
        return _campo(cur, rid, campo)


# Los objetivos se ofrecen por título: 1 Expand, 2 Raise, 3 Reduce (+ Otra opción).
@pytest.mark.parametrize(("opcion", "indice"), [("1", 2), ("2", 1), ("3", 0)])
def test_una_eleccion_escrita_se_resuelve_por_el_id_que_dice_el_modelo(
        opcion, indice, intake_world, conn, monkeypatch):
    """R4c-H4: la respuesta natural ya no recibe "No encontré esa opción"."""
    user, rid = _alta_en_el_objetivo(conn, intake_world)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta({"opcion_id": opcion})])

    _escribir(conn, monkeypatch, intake_world, provider,
              "la de la entrega, dale")              # no es una etiqueta exacta

    objetivo = _estado(conn, rid, "objective")
    assert objetivo["estado"] == "confirmed"
    assert objetivo["valor"]["id"] == intake_world["north-lab"]["objectives"][indice]
    assert provider.main_calls == 0
    # El modelo recibió las opciones con sus ids, no sólo el texto.
    esperado = provider.esperados[0]
    assert [o.id for o in esperado.opciones][:3] == ["1", "2", "3"]
    assert len(_nuevas(conn, user, antes)) == 1            # una respuesta


def test_una_opcion_que_no_se_ofrecio_dice_cuales_hay_y_deja_la_eleccion_abierta(
        intake_world, conn, monkeypatch):
    user, rid = _alta_en_el_objetivo(conn, intake_world)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta({"opcion_id": "9"})])

    _escribir(conn, monkeypatch, intake_world, provider, "la novena")

    assert _estado(conn, rid, "objective")["estado"] != "confirmed"
    with admin(conn) as cur:
        assert _conjunto_activo(cur, rid) == "objective"
    (ultimo,) = _nuevas(conn, user, antes)
    assert "no está entre las que te ofrecí" in ultimo["cuerpo"]
    assert "Reduce service delay 1" in ultimo["cuerpo"]
    assert ultimo["intake_choice_set_id"]                  # con sus botones


def test_una_eleccion_sin_valor_queda_abierta_con_incidente_y_aviso_neutro(
        intake_world, conn, monkeypatch):
    user, rid = _alta_en_el_objetivo(conn, intake_world)
    previas = _salidas(conn, user)
    provider = _RoutingProvider([_ruta({})])

    _escribir(conn, monkeypatch, intake_world, provider, "mmm")

    assert _incidentes(conn, I.ETAPA_VALOR_SIN_INTERPRETAR) == 1
    with admin(conn) as cur:
        assert _conjunto_activo(cur, rid) == "objective"
    (ultimo,) = _nuevas(conn, user, previas)
    assert I.NOTICIA_NEUTRA_INCIDENTE in ultimo["cuerpo"]
    assert ultimo["intake_choice_set_id"]


def test_una_eleccion_que_podria_ser_mas_de_una_opcion_se_repregunta_sin_incidente(
        intake_world, conn, monkeypatch):
    """F-B1: una respuesta ambigua entre dos opciones no es una falla."""
    user, rid = _alta_en_el_objetivo(conn, intake_world)
    previas = _salidas(conn, user)
    provider = _RoutingProvider([_ruta({"falta": "cual"})])

    _escribir(conn, monkeypatch, intake_world, provider, "la de reducir o la de subir")

    assert _incidentes(conn, I.ETAPA_VALOR_SIN_INTERPRETAR) == 0
    assert _estado(conn, rid, "objective")["estado"] != "confirmed"
    with admin(conn) as cur:
        assert _conjunto_activo(cur, rid) == "objective"
    (ultimo,) = _nuevas(conn, user, previas)
    assert "más de una de las opciones" in ultimo["cuerpo"]
    assert I.NOTICIA_NEUTRA_INCIDENTE not in ultimo["cuerpo"]
    assert ultimo["intake_choice_set_id"]                  # con sus botones


def test_un_valor_escrito_que_no_es_una_opcion_se_busca_entre_los_de_la_base(
        intake_world, conn, monkeypatch):
    """Sigue la búsqueda actual en la base (etapa 3, Jev: todavía no migrada)."""
    user, rid = _alta_en_el_objetivo(conn, intake_world)
    provider = _RoutingProvider([_ruta({"opcion_id": "ninguna",
                                        "texto": "delivery"})])

    _escribir(conn, monkeypatch, intake_world, provider, "el de delivery")

    objetivo = _estado(conn, rid, "objective")
    assert objetivo["estado"] == "confirmed"
    assert objetivo["valor"]["id"] == intake_world["north-lab"]["objectives"][1]
    assert objetivo["proposed_by"] == "user"


# --------------------------------------------- R4c-H5: sin bucle a mitad del alta

@pytest.mark.parametrize("donde", ["titulo", "objetivo"])
def test_pedir_otra_tarea_a_mitad_del_alta_no_reinicia_ni_entra_en_bucle(
        donde, intake_world, conn, monkeypatch):
    user = _usuario(intake_world)
    if donde == "titulo":
        with espacio(conn, intake_world["north-lab"]["id"]) as cur:
            _, outcome = _empezar(cur, intake_world, chat=user)
            rid = outcome.request_id
        conn.commit()
    else:
        user, rid = _alta_en_el_objetivo(conn, intake_world)
    for _ in range(3):                   # pedirla una y otra vez
        antes = _salidas(conn, user)
        provider = _RoutingProvider([_ruta(comando=RespectoPendiente.OTRO_TEMA)])

        _escribir(conn, monkeypatch, intake_world, provider,
                  "quiero crear una tarea nueva")

        nuevas = _nuevas(conn, user, antes)
        assert len(nuevas) == 1                        # una sola respuesta
        assert nuevas[0]["pending_action_id"]          # la pregunta de la rama
        assert provider.main_calls == 0
        with admin(conn) as cur:
            cur.execute("""select count(*) n from task_intake_request
                            where chat_id = %s and estado = 'active'""", (user,))
            assert cur.fetchone()["n"] == 1            # no se abrió otra alta
            assert (_slot(cur, rid) == "title") if donde == "titulo" else (
                _conjunto_activo(cur, rid) == "objective")   # sigue la misma
