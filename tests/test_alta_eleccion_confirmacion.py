"""Una pregunta pendiente es contexto, no una trampa (T9-R1c-2, ADR 0013 regla
1): las elecciones con botones del alta guiada y la confirmación del borrador.

Hasta ahora `ingreso_tareas.handle_active_text` tragaba el mensaje de quien
tenía una elección abierta (repetía la pregunta como recordatorio) o un
borrador esperando confirmación ("El borrador de la tarea está esperando
confirmación."), sin interpretarlo. Ahora el mensaje pasa por el ruteo tipado y
el manejo genérico (`gateway._atender_pregunta_pendiente`), como el campo de
texto libre (T9-R1c-1):

- elección abierta: `responde` toma la opción sólo si el texto es exactamente
  una de las opciones activas (como el toque); si no, vuelve a mostrar la
  pregunta con sus botones. El modelo nunca elige la opción.
- borrador esperando confirmación: la conversión sigue siendo explícita, con el
  botón Confirmar; ningún mensaje la confirma. `corrige` abre el selector de
  Modificar (`test_alta_modificar.py`); `cancela` lo cancela.

Los ruteos y el modelo se guionan; ninguna prueba toca la red ni el modelo real.
"""

from __future__ import annotations

import pytest

from prisma import gateway
from prisma import ingreso_tareas as I
from prisma import pendientes as P
from prisma.db import admin, espacio
from prisma.llm import IntentAction, IntentRoute, RespectoPendiente

from tests.test_task_intake import (NOW, _RoutingProvider, _actor,  # noqa: F401
                                    _active_choices, _callback_client,
                                    _choose, _post_message, _start)

TITULO = "Inspect relief valve"
_ids = iter(range(2000, 3000))


def _ruta(comando: RespectoPendiente | None) -> IntentRoute:
    return IntentRoute(IntentAction.NORMAL_CONVERSATION, respecto_pendiente=comando)


def _escribir(conn, monkeypatch, world, provider, texto):
    return _post_message(conn, monkeypatch, world, provider, texto,
                         message_id=next(_ids))


def _usuario(world) -> int:
    return world["north-lab"]["people"]["Taylor Quinn"]["telegram"]


def _alta_con_eleccion(conn, world) -> str:
    """El alta con el título confirmado y el objetivo esperando una elección con
    botones (la propuesta "service delay" deja una sola candidata)."""
    user = _usuario(world)
    with espacio(conn, world["north-lab"]["id"]) as cur:
        actor, outcome = _start(cur, world, chat_id=user, objective="service delay")
        _choose(cur, actor, outcome.request_id, "Sí", chat_id=user)
        pregunta = I.open_intake_question(cur, actor, user)
        assert pregunta["tipo"] == "choice"
    conn.commit()
    return outcome.request_id


def _alta_en_confirmacion(conn, world, responsable="Sam North") -> tuple[str, str]:
    """El alta completa: el borrador espera la confirmación. Devuelve el id de
    la solicitud y el de la `pending_action` de la vista previa. Quien escribe
    (Taylor Quinn) aprueba lo de Sam North; lo suyo ("Para mí") lo aprueba
    Morgan Hale."""
    user = _usuario(world)
    with espacio(conn, world["north-lab"]["id"]) as cur:
        actor, outcome = _start(cur, world, chat_id=user)
        rid = outcome.request_id
        _choose(cur, actor, rid, "Sí", chat_id=user)
        cur.execute("""select campo from task_intake_choice_set
                        where request_id = %s and estado = 'active'""", (rid,))
        if cur.fetchone()["campo"] == "description":
            _choose(cur, actor, rid, "Sí", chat_id=user)
        for parte in ("Reduce service delay", responsable, "Field Services"):
            etiqueta = next(e for e in _active_choices(cur, rid) if parte in e)
            _choose(cur, actor, rid, etiqueta, chat_id=user)
        _choose(cur, actor, rid, "Sí", chat_id=user)
        final = _choose(cur, actor, rid, "Sí", chat_id=user)
        # Quien escribe tiene la pregunta abierta: la confirmación si es quien
        # confirma, o su revisión antes de enviar a aprobación (T9-R1c-4).
        pregunta = I.open_intake_question(cur, actor, user)
        assert pregunta["tipo"] == "confirmation"
    conn.commit()
    return rid, final.pending_action_id


def _alta_enviada(conn, world, responsable="Para mí") -> tuple[str, str]:
    """El alta que confirma otra persona, ya enviada a aprobación por quien la
    pidió (T9-R1c-4): devuelve el id de la solicitud y el de la `pending_action`
    de la vista previa de quien confirma, con Confirmar y Rechazar."""
    rid, revision = _alta_en_confirmacion(conn, world, responsable=responsable)
    user = _usuario(world)
    ws = world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        token = P.opcion_por_etiqueta(cur, revision, "Enviar a aprobación").token
        assert I.send_to_approval(cur, _actor(cur, world), token=token, chat_id=user,
                                  now=NOW) is not None
        cur.execute(
            """select p.id from pending_action p
                 join task_intake_request r on r.task_draft_id = p.draft_id
                where r.id = %s and p.estado = 'esperando'""", (rid,))
        (fila,) = cur.fetchall()
    conn.commit()
    return rid, str(fila["id"])


def _salidas(conn, chat_id) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(
            """select id, cuerpo, pending_action_id, intake_choice_set_id
                 from message_outbox where chat_id = %s
                order by programado_para, id""", (chat_id,))
        return cur.fetchall()


def _nuevas(conn, chat_id, antes: list[dict]) -> list[dict]:
    """Lo que salió después de `antes`, en orden de envío. El armado del alta
    usa un reloj fijo (`NOW`), así que no se compara por posición con lo
    anterior."""
    vistos = {fila["id"] for fila in antes}
    return [f for f in _salidas(conn, chat_id) if f["id"] not in vistos]


def _pregunta(salidas: list[dict], conjunto: str) -> str:
    """El texto con que se hizo la pregunta de la elección `conjunto`."""
    return next(f["cuerpo"] for f in salidas
                if str(f["intake_choice_set_id"]) == conjunto)


def _solicitud(conn, rid) -> str:
    with admin(conn) as cur:
        cur.execute("select estado from task_intake_request where id = %s", (rid,))
        return cur.fetchone()["estado"]


def _campo(conn, rid, campo) -> dict:
    with admin(conn) as cur:
        cur.execute("""select estado, valor, source_choice_id, proposed_by
                         from task_intake_field where request_id = %s and campo = %s""",
                    (rid, campo))
        return cur.fetchone()


def _conjunto_activo(conn, rid) -> str | None:
    with admin(conn) as cur:
        cur.execute("""select id from task_intake_choice_set
                        where request_id = %s and estado = 'active'""", (rid,))
        fila = cur.fetchone()
    return str(fila["id"]) if fila else None


def _tocar_boton(client, conn, token, user):
    return client.post(
        "/telegram/north-lab",
        json={"callback_query": {
            "id": f"cb-{next(_ids)}", "from": {"id": user},
            "data": P.CALLBACK_PREFIJO + token,
            "message": {"message_id": 7, "chat": {"id": user}}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"})


def _token_de(conn, etiqueta_parte: str) -> str:
    with admin(conn) as cur:
        cur.execute(
            """select o.token from pending_action_option o
                 join pending_action p on p.id = o.pending_action_id
                where o.etiqueta like %s order by p.creado_en desc limit 1""",
            (f"%{etiqueta_parte}%",))
        return cur.fetchone()["token"]


# ---------------------------------------------------------------- elección

@pytest.mark.parametrize("texto", [
    "Reduce service delay 1", "reduce service delay 1", "  REDUCE   service delay 1 "])
def test_elegir_escribiendo_la_opcion_resuelve_como_el_toque(
        texto, intake_world, conn, monkeypatch):
    rid = _alta_con_eleccion(conn, intake_world)
    conjunto = _conjunto_activo(conn, rid)
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(RespectoPendiente.RESPONDE)])

    _escribir(conn, monkeypatch, intake_world, provider, texto)

    campo = _campo(conn, rid, "objective")
    assert campo["estado"] == "confirmed"
    assert campo["valor"]["id"] == intake_world["north-lab"]["objectives"][0]
    assert campo["proposed_by"] == "server" and campo["source_choice_id"]
    assert provider.main_calls == 0
    # El ruteo recibe la elección abierta y sus opciones como contexto.
    assert "Reduce service delay 1" in provider.pending_calls[0]
    siguiente = _conjunto_activo(conn, rid)
    assert siguiente != conjunto                       # sigue la próxima pregunta
    # Una sola respuesta visible, y es la próxima pregunta del alta.
    salidas = _nuevas(conn, user, antes)
    assert len(salidas) == 1
    assert str(salidas[0]["intake_choice_set_id"]) == siguiente
    assert salidas[0]["cuerpo"] == _pregunta(salidas, siguiente)


def test_una_opcion_que_parece_un_titulo_no_tira_abajo_el_ruteo(
        intake_world, conn, monkeypatch):
    """Banco b-0022: la opción escrita parece el título de una tarea y el
    modelo la rutea como conversación con propuestas de tarea. Con la elección
    abierta la decisión es `respecto_pendiente`: la opción se toma y no hay
    RoutingError ni incidente."""
    from prisma.llm import Llamada, ProveedorGuionado, RouteEnvelope

    rid = _alta_con_eleccion(conn, intake_world)
    sobre = RouteEnvelope(calls=(Llamada("c", "route_intent", {
        "action": "normal_conversation", "respecto_pendiente": "responde",
        "task": {"title": "Reduce service delay 1"}}),))
    provider = ProveedorGuionado([], rutas=[sobre])

    _escribir(conn, monkeypatch, intake_world, provider,
              "Reduce service delay 1")

    assert _campo(conn, rid, "objective")["estado"] == "confirmed"
    with admin(conn) as cur:
        cur.execute("select count(*) n from incident")
        assert cur.fetchone()["n"] == 0


def test_un_texto_que_no_es_una_opcion_repite_la_pregunta_con_sus_botones(
        intake_world, conn, monkeypatch):
    rid = _alta_con_eleccion(conn, intake_world)
    user = _usuario(intake_world)
    conjunto = _conjunto_activo(conn, rid)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(RespectoPendiente.RESPONDE)])

    _escribir(conn, monkeypatch, intake_world, provider, "el de la bomba, creo")

    assert _campo(conn, rid, "objective")["estado"] != "confirmed"
    assert _conjunto_activo(conn, rid) == conjunto            # sigue abierta
    salidas = _nuevas(conn, user, antes)
    assert len(salidas) == 1
    assert salidas[-1]["cuerpo"] == _pregunta(antes, conjunto)       # la misma pregunta
    assert str(salidas[-1]["intake_choice_set_id"]) == conjunto  # con sus botones


def _fila_de_evento(conn, world) -> str:
    """Una fila de `inbound_message` (un mensaje o un toque) para atar lo que se
    encole con `db.atar_al_entrante`."""
    with admin(conn) as cur:
        cur.execute(
            """insert into inbound_message (workspace_id, chat_id) values
                 (%s, %s) returning id""",
            (world["north-lab"]["id"], _usuario(world)))
        fila = str(cur.fetchone()["id"])
    conn.commit()
    return fila


def test_reenviar_la_eleccion_sale_del_evento_que_lo_dispara_y_es_idempotente(
        intake_world, conn):
    """T9-R4 (review e11061770c5f40ae): sin `ref` explícito la referencia del
    reenvío sale del evento que lo dispara (el mensaje o el toque al que está
    atado el turno), no de un conteo: un callback que se entrega dos veces
    reenvía UNA vez, y otro evento reenvía de nuevo."""
    from prisma.db import atar_al_entrante

    rid = _alta_con_eleccion(conn, intake_world)
    conjunto = _conjunto_activo(conn, rid)
    user = _usuario(intake_world)
    uno = _fila_de_evento(conn, intake_world)
    otro = _fila_de_evento(conn, intake_world)
    antes = _salidas(conn, user)

    for evento in (uno, uno, otro):
        with espacio(conn, intake_world["north-lab"]["id"]) as cur:
            atar_al_entrante(cur, evento)
            assert I.resend_choice_prompt(cur, _actor(cur, intake_world),
                                          conjunto, NOW, None)
        conn.commit()

    assert len(_nuevas(conn, user, antes)) == 2


def test_reenviar_la_eleccion_sin_mensaje_de_origen_usa_referencias_deterministas(
        intake_world, conn):
    rid = _alta_con_eleccion(conn, intake_world)
    conjunto = _conjunto_activo(conn, rid)
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        actor = _actor(cur, intake_world)
        assert I.resend_choice_prompt(cur, actor, conjunto, NOW, None)
        assert I.resend_choice_prompt(cur, actor, conjunto, NOW, None)
    conn.commit()

    # Cada reenvío es un mensaje propio: la referencia no es la misma ni sale
    # del reloj, así que el segundo no se pierde por la deduplicación.
    assert len(_nuevas(conn, user, antes)) == 2
    with admin(conn) as cur:
        cur.execute("""select dedupe_key from message_outbox
                        where intake_choice_set_id = %s and dedupe_key like %s
                        order by dedupe_key""", (conjunto, "%:reask:%"))
        claves = [f["dedupe_key"] for f in cur.fetchall()]
    assert claves == [f"intake:{rid}:reask:n1", f"intake:{rid}:reask:n2"]


def test_repreguntar_una_eleccion_ya_cerrada_dice_que_ya_no_esta_vigente(
        intake_world, conn):
    rid = _alta_con_eleccion(conn, intake_world)
    user = _usuario(intake_world)
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor = _actor(cur, intake_world)
        abierta = gateway._ver_pregunta_abierta(cur, actor, user, NOW, alta=True)
        assert abierta.herramienta == gateway._SENTINEL_ALTA_ELECCION
        etiqueta = next(iter(_active_choices(cur, rid)))
        _choose(cur, actor, rid, etiqueta, chat_id=user)  # otro camino la cerró
    conn.commit()
    antes = _salidas(conn, user)

    with espacio(conn, ws) as cur:
        gateway._repreguntar(cur, actor, ws, user, abierta,
                             gateway._pregunta_de(abierta), NOW, None)
    conn.commit()

    salidas = _nuevas(conn, user, antes)
    assert [f["cuerpo"] for f in salidas] == [gateway.AVISO_DATO_YA_NO_PENDIENTE]


def test_una_pregunta_de_texto_libre_sin_nombre_de_campo_falla_fuerte(
        intake_world, conn):
    abierta = P.ModificacionAbierta(
        pregunta_id="x", herramienta=gateway._SENTINEL_ALTA_TEXTO_LIBRE,
        args={"campo": "campo_inexistente", "titulo": None}, resumen="¿Cuál?")

    with pytest.raises(KeyError, match="campo_inexistente"):
        gateway._pregunta_de(abierta)


def test_una_opcion_repetida_no_se_elige_sola(intake_world, conn):
    # Dos opciones con el mismo nombre: escribirlo no alcanza para elegir una.
    rid = _alta_con_eleccion(conn, intake_world)
    user = _usuario(intake_world)
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        actor = _actor(cur, intake_world)
        cur.execute(
            """insert into task_intake_choice
                 (workspace_id, choice_set_id, token, etiqueta, accion, valor, orden)
               select workspace_id, choice_set_id, 'duplicada-000001', etiqueta,
                      accion, valor, 99
                 from task_intake_choice
                where choice_set_id = %s and accion = 'select' limit 1""",
            (_conjunto_activo(conn, rid),))
        conjunto = _conjunto_activo(conn, rid)
        resuelta = I.resolve_typed_choice(
            cur, actor, choice_set_id=conjunto, text="Reduce service delay 1",
            chat_id=user, now=NOW)
    assert resuelta is None
    assert _campo(conn, rid, "objective")["estado"] != "confirmed"


@pytest.mark.parametrize("texto", ["service", "Reduce service delay", "delay service 1"])
def test_no_hay_coincidencia_parcial_ni_aproximada(
        texto, intake_world, conn):
    rid = _alta_con_eleccion(conn, intake_world)
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        actor = _actor(cur, intake_world)
        resuelta = I.resolve_typed_choice(
            cur, actor, choice_set_id=_conjunto_activo(conn, rid), text=texto,
            chat_id=_usuario(intake_world), now=NOW)
    assert resuelta is None
    assert _campo(conn, rid, "objective")["estado"] != "confirmed"


def test_cancela_con_una_eleccion_abierta_cancela_el_borrador_y_lo_dice(
        intake_world, conn, monkeypatch):
    rid = _alta_con_eleccion(conn, intake_world)
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(RespectoPendiente.CANCELA)])

    _escribir(conn, monkeypatch, intake_world, provider, "dejá, no la quiero crear")

    assert _solicitud(conn, rid) == "cancelled"
    assert _conjunto_activo(conn, rid) is None
    salidas = _nuevas(conn, user, antes)
    assert len(salidas) == 1
    assert salidas[-1]["cuerpo"] == gateway.AVISO_ALTA_DEJADA.format(
        titulo=f" «{TITULO}»")


def test_otro_tema_con_una_eleccion_abierta_pregunta_por_la_rama_sin_atender_el_mensaje(
        intake_world, conn, monkeypatch):
    rid = _alta_con_eleccion(conn, intake_world)
    user = _usuario(intake_world)
    conjunto = _conjunto_activo(conn, rid)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(RespectoPendiente.OTRO_TEMA)])

    _escribir(conn, monkeypatch, intake_world, provider, "¿qué es un bloqueo?")

    assert provider.main_calls == 0
    assert _conjunto_activo(conn, rid) == conjunto            # la elección sigue
    salidas = _nuevas(conn, user, antes)
    assert [f["cuerpo"] for f in salidas] == [gateway.PREGUNTA_RAMA_ABIERTA.format(
        nombre="la elección sobre el objetivo de la tarea nueva")]
    assert salidas[0]["pending_action_id"]                    # con sus botones


def test_seguir_con_una_eleccion_abierta_la_vuelve_a_mostrar_con_sus_botones(
        intake_world, conn, monkeypatch):
    rid = _alta_con_eleccion(conn, intake_world)
    user = _usuario(intake_world)
    conjunto = _conjunto_activo(conn, rid)
    provider = _RoutingProvider([_ruta(RespectoPendiente.OTRO_TEMA)])
    _escribir(conn, monkeypatch, intake_world, provider, "¿qué es un bloqueo?")
    antes = _salidas(conn, user)
    client = _callback_client(conn, monkeypatch)

    assert _tocar_boton(client, conn, _token_de(conn, "Seguir"),
                        user).status_code == 200

    assert _conjunto_activo(conn, rid) == conjunto
    salidas = _nuevas(conn, user, antes)
    assert len(salidas) == 1
    assert str(salidas[0]["intake_choice_set_id"]) == conjunto  # con sus botones
    assert salidas[0]["cuerpo"] == _pregunta(antes, conjunto)


@pytest.mark.parametrize("comando", [
    RespectoPendiente.CHARLA, RespectoPendiente.NO_PUEDO])
def test_charla_y_no_puedo_con_una_eleccion_abierta_repiten_la_pregunta_con_botones(
        comando, intake_world, conn, monkeypatch):
    rid = _alta_con_eleccion(conn, intake_world)
    user = _usuario(intake_world)
    conjunto = _conjunto_activo(conn, rid)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(comando)])

    _escribir(conn, monkeypatch, intake_world, provider, "hola, che")

    assert _conjunto_activo(conn, rid) == conjunto
    salidas = _nuevas(conn, user, antes)
    assert len(salidas) == 1
    assert str(salidas[-1]["intake_choice_set_id"]) == conjunto
    assert salidas[-1]["cuerpo"].endswith(_pregunta(antes, conjunto))
    if comando is RespectoPendiente.NO_PUEDO:
        assert salidas[-1]["cuerpo"].startswith(gateway.AVISO_NO_PUEDO_DATO_PENDIENTE)
    else:
        assert salidas[-1]["cuerpo"] == _pregunta(antes, conjunto)


@pytest.mark.parametrize("comando", [
    RespectoPendiente.DUDOSO, RespectoPendiente.CORRIGE])
def test_dudoso_y_corrige_con_una_eleccion_abierta_preguntan_con_botones(
        comando, intake_world, conn, monkeypatch):
    rid = _alta_con_eleccion(conn, intake_world)
    user = _usuario(intake_world)
    conjunto = _conjunto_activo(conn, rid)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(comando)])

    _escribir(conn, monkeypatch, intake_world, provider, "Reduce service delay 1")

    assert _conjunto_activo(conn, rid) == conjunto            # no se consumió
    assert _campo(conn, rid, "objective")["estado"] != "confirmed"
    salidas = _nuevas(conn, user, antes)
    assert len(salidas) == 1
    assert salidas[-1]["cuerpo"].startswith("¿Esto es")
    assert salidas[-1]["pending_action_id"]


def test_dejar_con_una_eleccion_abierta_cancela_el_borrador_y_atiende_el_mensaje(
        intake_world, conn, monkeypatch):
    rid = _alta_con_eleccion(conn, intake_world)
    user = _usuario(intake_world)
    provider = _RoutingProvider(
        [_ruta(RespectoPendiente.OTRO_TEMA),
         IntentRoute(IntentAction.NORMAL_CONVERSATION)],
        answer="Un bloqueo frena una tarea.")
    _escribir(conn, monkeypatch, intake_world, provider, "¿qué es un bloqueo?")
    client = _callback_client(conn, monkeypatch)
    antes = _salidas(conn, user)

    assert _tocar_boton(client, conn, _token_de(conn, "Dejarlo"),
                        user).status_code == 200

    assert _solicitud(conn, rid) == "cancelled"
    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [
        gateway.AVISO_ALTA_DEJADA.format(titulo=f" «{TITULO}»"),
        "Un bloqueo frena una tarea."]


def test_si_es_eso_del_dudoso_con_un_texto_que_no_es_la_opcion_repite_la_pregunta(
        intake_world, conn, monkeypatch):
    rid = _alta_con_eleccion(conn, intake_world)
    user = _usuario(intake_world)
    conjunto = _conjunto_activo(conn, rid)
    provider = _RoutingProvider([_ruta(RespectoPendiente.DUDOSO)])
    _escribir(conn, monkeypatch, intake_world, provider, "el de la bomba")
    client = _callback_client(conn, monkeypatch)
    antes = _salidas(conn, user)

    assert _tocar_boton(client, conn, _token_de(conn, "Sí, es eso"),
                        user).status_code == 200

    assert _campo(conn, rid, "objective")["estado"] != "confirmed"
    nuevas = _nuevas(conn, user, antes)
    assert len(nuevas) == 1 and str(nuevas[0]["intake_choice_set_id"]) == conjunto


def test_si_es_eso_del_dudoso_toma_la_opcion_escrita(
        intake_world, conn, monkeypatch):
    rid = _alta_con_eleccion(conn, intake_world)
    user = _usuario(intake_world)
    provider = _RoutingProvider([_ruta(RespectoPendiente.DUDOSO)])
    _escribir(conn, monkeypatch, intake_world, provider, "Reduce service delay 1")
    client = _callback_client(conn, monkeypatch)
    token = _token_de(conn, "Sí, es eso")

    assert _tocar_boton(client, conn, token, user).status_code == 200

    assert _campo(conn, rid, "objective")["estado"] == "confirmed"


def test_con_el_ruteo_caido_la_eleccion_queda_abierta_y_hay_una_respuesta(
        intake_world, conn, monkeypatch):
    rid = _alta_con_eleccion(conn, intake_world)
    user = _usuario(intake_world)
    conjunto = _conjunto_activo(conn, rid)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([RuntimeError("caído"), RuntimeError("caído")])

    _escribir(conn, monkeypatch, intake_world, provider, "Reduce service delay 1")

    assert _conjunto_activo(conn, rid) == conjunto
    assert _campo(conn, rid, "objective")["estado"] != "confirmed"
    assert len(_nuevas(conn, user, antes)) == 1


def test_el_toque_de_una_opcion_sigue_funcionando_igual(
        intake_world, conn, monkeypatch):
    rid = _alta_con_eleccion(conn, intake_world)
    user = _usuario(intake_world)
    with admin(conn) as cur:
        cur.execute(
            """select c.token from task_intake_choice c
                 join task_intake_choice_set s on s.id = c.choice_set_id
                where s.request_id = %s and s.estado = 'active'
                  and c.etiqueta like %s""", (rid, "%Reduce service delay 1%"))
        token = cur.fetchone()["token"]
    client = _callback_client(conn, monkeypatch)

    response = client.post(
        "/telegram/north-lab",
        json={"callback_query": {
            "id": "cb-regresion", "from": {"id": user}, "data": I.callback_data(token),
            "message": {"message_id": 7, "chat": {"id": user}}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"})

    assert response.status_code == 200
    assert _campo(conn, rid, "objective")["estado"] == "confirmed"


# ------------------------------------------------------------ confirmación

def _sin_conversion(conn, rid, pid):
    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid,))
        assert cur.fetchone()["estado"] == "esperando"
        cur.execute("select count(*) n from task where titulo = %s", (TITULO,))
        assert cur.fetchone()["n"] == 0
    assert _solicitud(conn, rid) == "active"


@pytest.mark.parametrize("texto", ["sí, dale", "confirmalo", "ok"])
def test_responde_no_convierte_el_borrador_y_dice_como_se_confirma(
        texto, intake_world, conn, monkeypatch):
    rid, pid = _alta_en_confirmacion(conn, intake_world)
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(RespectoPendiente.RESPONDE)])

    _escribir(conn, monkeypatch, intake_world, provider, texto)

    _sin_conversion(conn, rid, pid)
    assert provider.main_calls == 0
    assert "Confirmar" in provider.pending_calls[0]
    salidas = _nuevas(conn, user, antes)
    assert len(salidas) == 1
    assert salidas[-1]["cuerpo"] == I.DRAFT_AWAITING_CONFIRMATION


# Regla 3 (ADR 0013, estado real): si quien escribe no es quien confirma, la
# respuesta dice quién confirma en vez de dar a entender que puede hacerlo.
def test_quien_escribe_es_el_aprobador_la_respuesta_no_nombra_a_nadie(
        intake_world, conn, monkeypatch):
    _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(RespectoPendiente.RESPONDE)])

    _escribir(conn, monkeypatch, intake_world, provider, "sí, dale")

    salidas = _nuevas(conn, user, antes)
    assert [f["cuerpo"] for f in salidas] == [I.DRAFT_AWAITING_CONFIRMATION]
    assert "Morgan Hale" not in salidas[0]["cuerpo"]


# Una rama está abierta para quien tiene que responderla (ADR 0013 regla 1,
# enmienda del 2026-09-29): el borrador que ya se envió a la confirmación de otra
# persona (T9-R1c-4; antes de enviarlo, el resumen es rama de quien lo pidió) no es
# una rama abierta de quien lo pidió. Sus mensajes siguen el camino normal: sin
# ruteo contra la pregunta, sin pregunta de la rama.
@pytest.mark.parametrize("texto", ["¿qué es un bloqueo?", "sí, dale", "hola"])
def test_quien_escribe_no_es_el_aprobador_su_mensaje_sigue_el_camino_normal(
        texto, intake_world, conn, monkeypatch):
    rid, pid = _alta_enviada(conn, intake_world)
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([IntentRoute(IntentAction.NORMAL_CONVERSATION)],
                                answer="Un bloqueo frena una tarea.")

    _escribir(conn, monkeypatch, intake_world, provider, texto)

    _sin_conversion(conn, rid, pid)                # el borrador sigue esperando
    assert provider.pending_calls == [None]        # ruteado sin pregunta pendiente
    assert provider.main_calls == 1                # lo atendió el agente
    salidas = _nuevas(conn, user, antes)
    assert [f["cuerpo"] for f in salidas] == ["Un bloqueo frena una tarea."]
    assert salidas[0]["pending_action_id"] is None  # sin botones de rama
    # La vista previa con los botones sigue siendo del aprobador, no de quien escribe.
    with admin(conn) as cur:
        cur.execute(
            """select o.chat_id from message_outbox o
                where o.pending_action_id = %s""", (pid,))
        assert cur.fetchone()["chat_id"] == (
            intake_world["north-lab"]["people"]["Morgan Hale"]["telegram"])


def test_quien_escribe_es_el_aprobador_su_otro_tema_abre_la_pregunta_de_la_rama(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(RespectoPendiente.OTRO_TEMA)])

    _escribir(conn, monkeypatch, intake_world, provider, "¿qué es un bloqueo?")

    _sin_conversion(conn, rid, pid)
    assert provider.main_calls == 0
    salidas = _nuevas(conn, user, antes)
    assert [f["cuerpo"] for f in salidas] == [gateway.PREGUNTA_RAMA_ABIERTA.format(
        nombre="la confirmación del borrador de la tarea nueva")]
    assert salidas[0]["pending_action_id"]                    # con sus botones


def test_cancela_con_el_borrador_esperando_lo_cancela_y_lo_dice(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_confirmacion(conn, intake_world)
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(RespectoPendiente.CANCELA)])

    _escribir(conn, monkeypatch, intake_world, provider, "no, cancelalo")

    assert _solicitud(conn, rid) == "cancelled"
    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid,))
        assert cur.fetchone()["estado"] == "cancelada"
        cur.execute("select d.estado from task_draft d join task_intake_request r "
                    "on r.task_draft_id = d.id where r.id = %s", (rid,))
        assert cur.fetchone()["estado"] == "cancelled"
    salidas = _nuevas(conn, user, antes)
    assert len(salidas) == 1
    assert salidas[-1]["cuerpo"] == gateway.AVISO_ALTA_DEJADA.format(
        titulo=f" «{TITULO}»")


def test_seguir_con_el_borrador_esperando_repite_el_estado_sin_convertir(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_confirmacion(conn, intake_world)
    user = _usuario(intake_world)
    provider = _RoutingProvider([_ruta(RespectoPendiente.OTRO_TEMA)])
    _escribir(conn, monkeypatch, intake_world, provider, "¿qué es un bloqueo?")
    client = _callback_client(conn, monkeypatch)
    antes = _salidas(conn, user)

    assert _tocar_boton(client, conn, _token_de(conn, "Seguir"),
                        user).status_code == 200

    _sin_conversion(conn, rid, pid)
    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [
        I.DRAFT_AWAITING_CONFIRMATION]
    assert provider.main_calls == 0


def test_dejar_con_el_borrador_esperando_lo_cancela_y_atiende_el_mensaje(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_confirmacion(conn, intake_world)
    user = _usuario(intake_world)
    provider = _RoutingProvider(
        [_ruta(RespectoPendiente.OTRO_TEMA),
         IntentRoute(IntentAction.NORMAL_CONVERSATION)],
        answer="Un bloqueo frena una tarea.")
    _escribir(conn, monkeypatch, intake_world, provider, "¿qué es un bloqueo?")
    client = _callback_client(conn, monkeypatch)
    antes = _salidas(conn, user)

    assert _tocar_boton(client, conn, _token_de(conn, "Dejarlo"),
                        user).status_code == 200

    assert _solicitud(conn, rid) == "cancelled"
    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [
        gateway.AVISO_ALTA_DEJADA.format(titulo=f" «{TITULO}»"),
        "Un bloqueo frena una tarea."]
    assert provider.pending_calls[-1] is None


@pytest.mark.parametrize("comando", [
    RespectoPendiente.CHARLA, RespectoPendiente.NO_PUEDO, RespectoPendiente.DUDOSO])
def test_charla_no_puedo_y_dudoso_con_el_borrador_esperando_dejan_una_respuesta(
        comando, intake_world, conn, monkeypatch):
    rid, pid = _alta_en_confirmacion(conn, intake_world)
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(comando)])

    _escribir(conn, monkeypatch, intake_world, provider, "hola")

    _sin_conversion(conn, rid, pid)
    assert len(_nuevas(conn, user, antes)) == 1


def test_si_es_eso_del_dudoso_con_el_borrador_esperando_tampoco_lo_convierte(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_confirmacion(conn, intake_world)
    user = _usuario(intake_world)
    provider = _RoutingProvider([_ruta(RespectoPendiente.DUDOSO)])
    _escribir(conn, monkeypatch, intake_world, provider, "sí")
    client = _callback_client(conn, monkeypatch)
    antes = _salidas(conn, user)

    assert _tocar_boton(client, conn, _token_de(conn, "Sí, es eso"),
                        user).status_code == 200

    _sin_conversion(conn, rid, pid)
    salidas = _nuevas(conn, user, antes)
    assert len(salidas) == 1
    assert salidas[-1]["cuerpo"] == I.DRAFT_AWAITING_CONFIRMATION


def test_con_el_ruteo_caido_el_borrador_queda_esperando_y_hay_una_respuesta(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_confirmacion(conn, intake_world)
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([RuntimeError("caído"), RuntimeError("caído")])

    _escribir(conn, monkeypatch, intake_world, provider, "sí, dale")

    _sin_conversion(conn, rid, pid)
    assert len(_nuevas(conn, user, antes)) == 1


def test_un_mensaje_no_impide_confirmar_con_el_boton(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid = _alta_en_confirmacion(conn, intake_world)
    ws = intake_world["north-lab"]["id"]
    provider = _RoutingProvider([_ruta(RespectoPendiente.RESPONDE)])
    _escribir(conn, monkeypatch, intake_world, provider, "sí, dale")
    with espacio(conn, ws) as cur:
        confirmar = P.opcion_por_etiqueta(cur, pid, "Confirmar").token
        cur.execute(
            """select telegram_user_id from integrante
                where membership_id = (select membership_id from pending_action
                                        where id = %s)""", (pid,))
        aprobador = cur.fetchone()["telegram_user_id"]
    conn.commit()

    from prisma.db import autoridad
    with autoridad(authority_conn) as cur:
        resuelta = P.resolver_borrador(cur, ws, confirmar, aprobador, aprobador)

    assert resuelta and resuelta.task_id
    assert _solicitud(conn, rid) == "converted"


def test_una_referencia_explicita_le_gana_al_evento_atado(intake_world, conn):
    # T9-R4b (R2-002): dos reenvíos con referencias explícitas distintas dentro de
    # un mismo turno atado salen los dos; la referencia del evento es sólo el
    # valor por omisión.
    from prisma.db import atar_al_entrante

    rid = _alta_con_eleccion(conn, intake_world)
    conjunto = _conjunto_activo(conn, rid)
    user = _usuario(intake_world)
    evento = _fila_de_evento(conn, intake_world)
    antes = _salidas(conn, user)

    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        atar_al_entrante(cur, evento)
        actor = _actor(cur, intake_world)
        assert I.resend_choice_prompt(cur, actor, conjunto, NOW, "uno")
        assert I.resend_choice_prompt(cur, actor, conjunto, NOW, "dos")
    conn.commit()

    assert len(_nuevas(conn, user, antes)) == 2
