from __future__ import annotations

import dataclasses
import threading
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
import psycopg
from fastapi.testclient import TestClient

from leda import gateway
from leda import herramientas as H
from leda import ingreso_tareas as I
from leda import pendientes as P
from leda.agente import responder
from leda.autoridad import Canal, Denegado, identificar
from leda.calendario import Calendario
from leda.db import admin, autoridad, conectar, espacio
from leda.despachador import TransporteDePrueba, despachar
from leda.llm import (IntentAction, IntentRoute, ProveedorAnthropic,
                        RespectoPendiente, Respuesta, RoutingError)
from leda.salida import (BUTTON_LABEL_LIMIT, ICONO_TAREA, con_icono,
                           etiqueta_sin_icono, etiquetas_coinciden,
                           telegram_utf16_units)


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2028, 2, 28, 15, 0, tzinfo=timezone.utc)


def _actor(cur, world, workspace_slug="north-lab", person="Taylor Quinn"):
    item = world[workspace_slug]
    tg = item["people"][person]["telegram"]
    return identificar(cur, tg, Canal.ESPACIO, item["id"])


def _start(cur, world, *, workspace_slug="north-lab", chat_id=71001,
           raw="Please create the task", buttons_first=False, **changes):
    item = world[workspace_slug]
    actor = _actor(cur, world, workspace_slug)
    cur.execute(
        """insert into inbound_message
             (workspace_id, telegram_message_id, chat_id, app_user_id, texto)
           values (%s, 501, %s, %s, %s) returning id""",
        (item["id"], chat_id, actor.app_user_id, raw),
    )
    inbound_id = str(cur.fetchone()["id"])
    proposals = {
        "title": "Inspect relief valve",
        "objective": "service delay",
        "responsible": "Sam",
        "area": "Field",
        "due_date": "29/2",
        "acceptance_criterion": "Signed test record attached",
    }
    proposals.update(changes)
    outcome = I.start(
        cur, actor, chat_id=chat_id, source_inbound_id=inbound_id,
        source_raw_text=raw, proposals=proposals, now=NOW,
        buttons_first=buttons_first,
    )
    return actor, outcome


def _active_choices(cur, request_id):
    cur.execute(
        """select c.etiqueta, c.token
             from task_intake_choice c
             join task_intake_choice_set s on s.id = c.choice_set_id
            where s.request_id = %s and s.estado = 'active' and c.activa
            order by c.orden""",
        (request_id,),
    )
    return {row["etiqueta"]: row["token"] for row in cur.fetchall()}


def _choose(cur, actor, request_id, label, chat_id=71001):
    # Ignora el ícono de categoría (íconos, decisión del usuario,
    # 2026-09-28): ver `salida.etiquetas_coinciden`.
    opciones = _active_choices(cur, request_id)
    etiqueta = next(e for e in opciones if etiquetas_coinciden(e, label))
    token = opciones[etiqueta]
    return I.resolve_choice(cur, actor, token=token, chat_id=chat_id, now=NOW)


def _callback_client(conn, monkeypatch, *, raise_server_exceptions=True):
    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    monkeypatch.setattr(gateway, "acusar_toque", lambda *args, **kwargs: None)
    monkeypatch.setattr(gateway, "config", SimpleNamespace(
        webhook_secret="test-secret", token_bot=lambda slug: "unused-token"))
    return TestClient(gateway.app, raise_server_exceptions=raise_server_exceptions)


def _objective_callback_setup(conn, world):
    ws = world["north-lab"]
    user = ws["people"]["Taylor Quinn"]["telegram"]
    with espacio(conn, ws["id"]) as cur:
        actor, outcome = _start(
            cur, world, chat_id=user, objective="service delay")
        _choose(cur, actor, outcome.request_id, "Sí", chat_id=user)
        label = next(label for label in _active_choices(cur, outcome.request_id)
                     if "Reduce service delay" in label)
        cur.execute(
            """select c.id choice_id, c.choice_set_id, c.token, s.request_version
                 from task_intake_choice c
                 join task_intake_choice_set s on s.id = c.choice_set_id
                where s.request_id = %s and c.etiqueta = %s""",
            (outcome.request_id, label),
        )
        choice = cur.fetchone()
        cur.execute(
            """update message_outbox set estado = 'enviado'
                where intake_choice_set_id = %s""",
            (choice["choice_set_id"],),
        )
        cur.execute(
            "select count(*) n from task_intake_choice where choice_set_id = %s",
            (choice["choice_set_id"],),
        )
        choice["choice_count"] = cur.fetchone()["n"]
        cur.execute(
            "select count(*) n from message_outbox where workspace_id = %s",
            (ws["id"],),
        )
        choice["outbox_count"] = cur.fetchone()["n"]
    conn.commit()
    return ws, user, outcome.request_id, choice


def _post_intake_callback(client, token, user, *, chat=None, callback_id="intake-cb"):
    return client.post(
        "/telegram/north-lab",
        json={"callback_query": {
            "id": callback_id, "from": {"id": user},
            "data": I.callback_data(token),
            "message": {"message_id": 7, "chat": {"id": chat or user}},
        }},
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"},
    )


def test_objective_callback_commits_once_dispatches_next_prompt_and_replays_inert(
        intake_world, conn, monkeypatch):
    ws, user, request_id, choice = _objective_callback_setup(conn, intake_world)
    client = _callback_client(conn, monkeypatch)

    first = _post_intake_callback(client, choice["token"], user)
    replay = _post_intake_callback(
        client, choice["token"], user, callback_id="intake-cb-replay")

    assert first.status_code == 200
    assert replay.status_code == 200
    with admin(conn) as cur:
        cur.execute(
            """select r.version, f.estado, f.valor, f.proposed_by,
                      f.source_choice_id
                 from task_intake_request r
                 join task_intake_field f on f.request_id = r.id
                where r.id = %s and f.campo = 'objective'""",
            (request_id,),
        )
        selected = cur.fetchone()
        assert selected["version"] == choice["request_version"] + 1
        assert selected["estado"] == "confirmed"
        assert selected["valor"]["id"] == ws["objectives"][0]
        assert selected["proposed_by"] == "server"
        assert selected["source_choice_id"] == choice["choice_id"]
        cur.execute(
            """select count(*) total,
                      count(*) filter (where not activa) inactive,
                      count(*) filter (where elegida) chosen
                 from task_intake_choice where choice_set_id = %s""",
            (choice["choice_set_id"],),
        )
        consumed = cur.fetchone()
        assert consumed["total"] == consumed["inactive"]
        assert consumed["chosen"] == 1
        cur.execute(
            """select id, campo, request_version
                 from task_intake_choice_set
                where request_id = %s and estado = 'active'""",
            (request_id,),
        )
        responsible_set = cur.fetchone()
        assert responsible_set["campo"] == "responsible"
        assert responsible_set["request_version"] == selected["version"]
        cur.execute(
            """select id, estado from message_outbox
                where intake_choice_set_id = %s""",
            (responsible_set["id"],),
        )
        queued = cur.fetchall()
        assert len(queued) == 1
        assert queued[0]["estado"] == "listo"

    transport = TransporteDePrueba()
    with espacio(conn, ws["id"]) as cur:
        summary = despachar(
            cur, ws["id"], transport, Calendario.desde_base(cur, ws["id"]),
            datetime.now(timezone.utc) + timedelta(minutes=1),
        )
    conn.commit()

    assert summary == {
        "enviados": 1, "pospuestos": 0, "fallidos": 0, "descartados": 0,
        "retenidos": 0}
    assert len(transport.enviados) == 1
    assert {button.etiqueta for button in transport.enviados[0].botones} == {
        con_icono("Para mí", ICONO_TAREA), con_icono("Sam North 1", ICONO_TAREA),
        con_icono("Sam Noble 1", ICONO_TAREA), I.OTHER}


@pytest.mark.parametrize("invalid", ("actor", "chat", "request", "version"))
def test_objective_callback_rejects_wrong_actor_chat_request_or_version(
        invalid, intake_world, conn, monkeypatch):
    ws, user, request_id, choice = _objective_callback_setup(conn, intake_world)
    callback_user = user
    callback_chat = user
    expected_version = choice["request_version"]
    expected_request_state = "active"
    if invalid == "actor":
        callback_user = ws["people"]["Sam North"]["telegram"]
    elif invalid == "chat":
        callback_chat += 99
    elif invalid == "request":
        with admin(conn) as cur:
            cur.execute(
                "update task_intake_request set estado = 'cancelled' where id = %s",
                (request_id,),
            )
        expected_request_state = "cancelled"
    else:
        with admin(conn) as cur:
            cur.execute(
                "update task_intake_request set version = version + 1 where id = %s",
                (request_id,),
            )
        expected_version += 1
    conn.commit()
    client = _callback_client(conn, monkeypatch)

    response = _post_intake_callback(
        client, choice["token"], callback_user, chat=callback_chat)

    assert response.status_code == 200
    with admin(conn) as cur:
        cur.execute(
            "select estado, version from task_intake_request where id = %s",
            (request_id,),
        )
        request = cur.fetchone()
        assert request == {
            "estado": expected_request_state, "version": expected_version}
        cur.execute(
            """select estado, source_choice_id from task_intake_field
                where request_id = %s and campo = 'objective'""",
            (request_id,),
        )
        assert cur.fetchone() == {"estado": "proposed", "source_choice_id": None}
        cur.execute(
            "select estado from task_intake_choice_set where id = %s",
            (choice["choice_set_id"],),
        )
        assert cur.fetchone()["estado"] == "active"
        cur.execute(
            "select count(*) n from message_outbox where workspace_id = %s",
            (ws["id"],),
        )
        # Un toque que no se atiende (otra persona, otro chat, ya usado o
        # reemplazado) recibe su única respuesta: que ya no está vigente (T9-R4).
        assert cur.fetchone()["n"] == choice["outbox_count"] + 1
        cur.execute(
            "select cuerpo from message_outbox where workspace_id = %s "
            "and es_respuesta and entrante_id is not null",
            (ws["id"],),
        )
        assert [f["cuerpo"] for f in cur.fetchall()] == [
            gateway.AVISO_PEDIDO_NO_VIGENTE]


def test_objective_callback_failure_rolls_back_before_outer_commit(
        intake_world, conn, monkeypatch):
    """Revisión del orquestador sobre `0814fa3` (T2b, punto 2): antes,
    `gateway.procesar_update` revertía la transacción y volvía a levantar la
    excepción -- 500, sin incidente ni aviso a la persona. Decisión del
    usuario, 2026-09-25: un error nunca pasa en silencio. La reversión de la
    mutación de intake (lo que este test prueba de fondo) sigue exactamente
    igual; lo que cambia es que ahora la respuesta es 200 (la persona no se
    queda sin nada) y queda un incidente más un aviso neutro encolado."""
    ws, user, request_id, choice = _objective_callback_setup(conn, intake_world)
    resolve_choice = I.resolve_choice

    def fail_after_resolution(*args, **kwargs):
        resolve_choice(*args, **kwargs)
        raise RuntimeError("failure after intake mutation")

    monkeypatch.setattr(I, "resolve_choice", fail_after_resolution)
    client = _callback_client(conn, monkeypatch, raise_server_exceptions=False)

    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where workspace_id = %s", (ws["id"],))
        incidentes_antes = cur.fetchone()["n"]

    response = _post_intake_callback(client, choice["token"], user)

    assert response.status_code == 200
    assert conn.info.transaction_status == psycopg.pq.TransactionStatus.IDLE
    with admin(conn) as cur:
        cur.execute(
            "select estado, version from task_intake_request where id = %s",
            (request_id,),
        )
        assert cur.fetchone() == {
            "estado": "active", "version": choice["request_version"]}
        cur.execute(
            """select estado, source_choice_id from task_intake_field
                where request_id = %s and campo = 'objective'""",
            (request_id,),
        )
        assert cur.fetchone() == {"estado": "proposed", "source_choice_id": None}
        cur.execute(
            "select estado from task_intake_choice_set where id = %s",
            (choice["choice_set_id"],),
        )
        assert cur.fetchone()["estado"] == "active"
        cur.execute(
            "select count(*) n from task_intake_choice where choice_set_id = %s and activa",
            (choice["choice_set_id"],),
        )
        assert cur.fetchone()["n"] == choice["choice_count"]
        # Sigue sin haber ningún cambio de negocio aplicado -- lo único
        # nuevo en la cola es el aviso neutro del incidente, no un efecto de
        # la elección que falló.
        cur.execute(
            "select count(*) n from message_outbox where workspace_id = %s",
            (ws["id"],),
        )
        assert cur.fetchone()["n"] == choice["outbox_count"] + 1
        cur.execute(
            """select count(*) n from message_outbox
                where workspace_id = %s and cuerpo = %s""",
            (ws["id"], gateway.NOTICIA_NEUTRA_INCIDENTE),
        )
        assert cur.fetchone()["n"] == 1
        cur.execute(
            "select count(*) n from incident where workspace_id = %s", (ws["id"],))
        assert cur.fetchone()["n"] == incidentes_antes + 1


def _complete(cur, world, request_id, actor, *, criterion_label="Confirm"):
    _choose(cur, actor, request_id, "Sí")
    cur.execute(
        """select campo from task_intake_choice_set
            where request_id = %s and estado = 'active'""",
        (request_id,),
    )
    active_field = cur.fetchone()
    if active_field and active_field["campo"] == "description":
        _choose(cur, actor, request_id, "Sí")
    objective_label = next(label for label in _active_choices(cur, request_id)
                            if "Reduce service delay" in label)
    _choose(cur, actor, request_id, objective_label)
    responsible_label = next(label for label in _active_choices(cur, request_id)
                             if "Sam North" in label)
    _choose(cur, actor, request_id, responsible_label)
    area_label = next(label for label in _active_choices(cur, request_id)
                      if "Field Services" in label)
    _choose(cur, actor, request_id, area_label)
    _choose(cur, actor, request_id, "Sí")
    return _choose(cur, actor, request_id,
                   "Sí" if criterion_label == "Confirm" else criterion_label)


@pytest.mark.parametrize(("raw", "expected"), (
    ("  Cafe\u0301\x00 valve  ", "Café valve"),
    ("line\r\nbreak\tkept", "line\nbreak\tkept"),
    ("technician 👩\u200d🔧\u202e", "technician 👩\u200d🔧"),
))
def test_text_normalization_is_nfc_and_rejects_controls(raw, expected):
    assert I.normalize_text(raw) == expected


@pytest.mark.parametrize(("raw", "expected"), (
    ("29/2", date(2028, 2, 29)),
    ("1 marzo", date(2028, 3, 1)),
    ("2028-03-02", date(2028, 3, 2)),
    ("mañana", date(2028, 2, 29)),
))
def test_dates_are_deterministic_in_workspace_timezone(raw, expected):
    assert I.resolve_date(raw, NOW, "America/Argentina/Buenos_Aires") == expected


@pytest.mark.parametrize("raw", ("2027-03-01", "31/02", "algún viernes"))
def test_past_invalid_or_ambiguous_dates_require_clarification(raw):
    with pytest.raises(I.AmbiguousDate):
        I.resolve_date(raw, NOW, "America/Argentina/Buenos_Aires")


def test_model_values_are_proposed_with_exact_inbound_lineage(intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, outcome = _start(cur, intake_world, raw="Create it for Sam, 29/2")
        cur.execute(
            """select campo, estado, source_inbound_id, source_raw_text
                 from task_intake_field where request_id = %s order by campo""",
            (outcome.request_id,),
        )
        fields = cur.fetchall()
        assert {f["estado"] for f in fields} <= {"missing", "proposed", "confirmed"}
        proposed = [f for f in fields if f["estado"] == "proposed"]
        assert proposed and all(f["source_inbound_id"] for f in proposed)
        assert all(f["source_raw_text"] == "Create it for Sam, 29/2"
                   for f in proposed)
        assert not any(f["estado"] == "confirmed" and f["campo"] in
                       {"title", "objective", "responsible", "due_date",
                        "acceptance_criterion"} for f in fields)
        assert set(_active_choices(cur, outcome.request_id)) == {
            "Sí", "No", I.OTHER}
        assert actor.nombre and actor.nombre not in outcome.text


def test_one_active_request_offers_explicit_conflict_choices(intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, first = _start(cur, intake_world)
        _, second = _start(cur, intake_world, raw="Start a different task",
                           title="Calibrate pressure sensor")
        cur.execute(
            """select count(*) n from task_intake_request
                where membership_id = %s and chat_id = 71001 and estado = 'active'""",
            (actor.membership_id,),
        )
        assert cur.fetchone()["n"] == 1
        assert second.request_id == first.request_id
        assert set(_active_choices(cur, first.request_id)) == {
            "Continuar borrador", I.CANCELAR_BORRADOR, "Empezar otro",
        }


def test_concurrent_starts_converge_without_unique_violation(
        intake_world, conn, uri):
    ws = intake_world["north-lab"]["id"]
    conn.commit()
    barrier = threading.Barrier(2)
    outcomes = []
    failures = []

    def begin(index):
        other = conectar(uri)
        try:
            with espacio(other, ws) as cur:
                actor = _actor(cur, intake_world)
                cur.execute(
                    """insert into inbound_message
                         (workspace_id, telegram_message_id, chat_id, app_user_id, texto)
                       values (%s, %s, 71001, %s, %s) returning id""",
                    (ws, 900 + index, actor.app_user_id, f"concurrent {index}"),
                )
                inbound_id = str(cur.fetchone()["id"])
                barrier.wait()
                outcomes.append(I.start(
                    cur, actor, chat_id=71001, source_inbound_id=inbound_id,
                    source_raw_text=f"concurrent {index}",
                    proposals={"title": f"Task {index}"}, now=NOW,
                ))
            other.commit()
        except Exception as exc:  # captured to prove no raw database error escapes
            failures.append(exc)
            other.rollback()
        finally:
            other.close()

    threads = [threading.Thread(target=begin, args=(index,)) for index in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert failures == []
    assert len(outcomes) == 2
    assert len({outcome.request_id for outcome in outcomes}) == 1
    with espacio(conn, ws) as cur:
        cur.execute(
            """select count(*) n from task_intake_request
                where workspace_id = %s and membership_id = %s
                  and chat_id = 71001 and estado = 'active'""",
            (ws, intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]),
        )
        assert cur.fetchone()["n"] == 1
        assert set(_active_choices(cur, outcomes[0].request_id)) == {
            "Continuar borrador", I.CANCELAR_BORRADOR, "Empezar otro",
        }


def test_other_atomically_invalidates_siblings_and_opens_exact_slot(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, outcome = _start(cur, intake_world)
        choices = _active_choices(cur, outcome.request_id)
        other = choices[I.OTHER]
        stale_confirm = choices["Sí"]
        I.resolve_choice(cur, actor, token=other, chat_id=71001, now=NOW)
        replay = I.resolve_choice(cur, actor, token=stale_confirm,
                                  chat_id=71001, now=NOW)
        assert replay.inert and not replay.changed
        cur.execute(
            """select campo, request_version from task_intake_free_text_slot
                where request_id = %s and estado = 'active'""",
            (outcome.request_id,),
        )
        slot = cur.fetchone()
        assert slot["campo"] == "title"
        cur.execute(
            """select count(*) n from task_intake_choice c
                 join task_intake_choice_set s on s.id = c.choice_set_id
                where s.request_id = %s and c.activa""",
            (outcome.request_id,),
        )
        assert cur.fetchone()["n"] == 0


def test_exact_pending_free_text_bypasses_model_and_confirms_source(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, outcome = _start(cur, intake_world)
        _choose(cur, actor, outcome.request_id, "Otra opción")
        cur.execute(
            """insert into inbound_message
                 (workspace_id, telegram_message_id, chat_id, app_user_id, texto)
               values (%s, 502, 71001, %s, %s) returning id""",
            (ws, actor.app_user_id, "Inspect café safety loop"),
        )
        inbound_id = str(cur.fetchone()["id"])
        consumed = I.consume_pending_text(
            cur, actor, chat_id=71001, source_inbound_id=inbound_id,
            source_raw_text="Inspect cafe\u0301 safety loop", now=NOW,
        )
        assert consumed and consumed.changed
        cur.execute(
            """select estado, valor, source_inbound_id, source_raw_text
                 from task_intake_field
                where request_id = %s and campo = 'title'""",
            (outcome.request_id,),
        )
        field = cur.fetchone()
        assert field["estado"] == "confirmed"
        assert field["valor"] == "Inspect café safety loop"
        assert str(field["source_inbound_id"]) == inbound_id
        assert field["source_raw_text"] == "Inspect cafe\u0301 safety loop"


def test_ambiguous_known_entities_are_server_candidates_with_other(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, outcome = _start(cur, intake_world)
        _choose(cur, actor, outcome.request_id, "Sí")
        objective_choices = _active_choices(cur, outcome.request_id)
        assert any("Reduce service delay" in x for x in objective_choices)
        assert I.OTHER in objective_choices
        objective = next(x for x in objective_choices if "Reduce service delay" in x)
        _choose(cur, actor, outcome.request_id, objective)
        people = _active_choices(cur, outcome.request_id)
        assert any("Sam North" in x for x in people)
        assert any("Sam Noble" in x for x in people)
        assert con_icono("Para mí", ICONO_TAREA) in people and I.OTHER in people


def test_intake_candidate_label_near_the_limit_still_fits_with_its_icon(
        intake_world, conn):
    """R3-003 (revisión 2026-09-28+2): `_open_entity_page` iconizaba la
    etiqueta de una candidata (objetivo, responsable, área) sin descontarle
    el costo del ícono al presupuesto -- a diferencia de los otros cinco
    lugares que arman botones de tarea. Un objetivo con un título largo,
    cerca del límite real de Telegram, tiene que seguir entrando en un botón
    válido en vez de romper `prepare_buttons`."""
    ws = intake_world["north-lab"]["id"]
    # 79 caracteres: pasa el chequeo de configuración de
    # `ingreso_tareas.CONFIG_LABEL_LIMIT` (80, sobre el título CRUDO, sin
    # ícono) pero el ícono + espacio (3 unidades) lo empuja a 82 -- por
    # encima de `BUTTON_LABEL_LIMIT` (80) si no se le descuenta el costo del
    # ícono al presupuesto ANTES de truncar (el bug real de R3-003: no
    # alcanza con un título disparatadamente largo, que ya lo frena esa otra
    # validación -- tiene que ser uno que la pasa de vuelta por el margen
    # exacto que le come el ícono).
    base = "Reduce el atraso de entregas en la planta industrial de la empresa "
    titulo_largo = (base * 2)[:79]
    assert telegram_utf16_units(titulo_largo) == 79
    assert telegram_utf16_units(f"{ICONO_TAREA} {titulo_largo}") > BUTTON_LABEL_LIMIT
    with admin(conn) as cur:
        cur.execute(
            """insert into objective (workspace_id, tipo, titulo, estado)
               values (%s, 'operativo', %s, 'activo')""",
            (ws, titulo_largo))
    with espacio(conn, ws) as cur:
        actor, outcome = _start(cur, intake_world, objective=None)
        _choose(cur, actor, outcome.request_id, "Sí")
        choices = _active_choices(cur, outcome.request_id)

    # `intake_world["north-lab"]` ya trae tres objetivos de fixture -- busca
    # específicamente la candidata del título largo, no cualquiera.
    candidata = next(
        c for c in choices
        if c != I.OTHER and titulo_largo.startswith(etiqueta_sin_icono(c).rstrip("…")))
    assert candidata.startswith(f"{ICONO_TAREA} ")
    assert telegram_utf16_units(candidata) <= BUTTON_LABEL_LIMIT


def test_objective_exact_free_text_match_is_not_limited_to_first_page(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    target = "ZZZ exact objective beyond first page"
    with admin(conn) as cur:
        for index in range(15):
            cur.execute(
                """insert into objective (workspace_id, tipo, titulo, estado)
                   values (%s, 'operativo', %s, 'activo')""",
                (ws, f"Paged objective {index:02d}"),
            )
        cur.execute(
            """insert into objective (workspace_id, tipo, titulo, estado)
               values (%s, 'operativo', %s, 'activo')""",
            (ws, target),
        )
    with espacio(conn, ws) as cur:
        actor, outcome = _start(cur, intake_world, objective=None)
        _choose(cur, actor, outcome.request_id, "Sí")
        assert I.VER_MAS in _active_choices(cur, outcome.request_id)
        _choose(cur, actor, outcome.request_id, "Otra opción")
        cur.execute(
            """insert into inbound_message
                 (workspace_id, telegram_message_id, chat_id, app_user_id, texto)
               values (%s, 950, 71001, %s, %s) returning id""",
            (ws, actor.app_user_id, target),
        )
        consumed = I.consume_pending_text(
            cur, actor, chat_id=71001,
            source_inbound_id=str(cur.fetchone()["id"]),
            source_raw_text=target, now=NOW,
        )
        assert consumed and consumed.changed
        cur.execute(
            """select estado, valor from task_intake_field
                where request_id = %s and campo = 'objective'""",
            (outcome.request_id,),
        )
        objective = cur.fetchone()
        assert objective["estado"] == "confirmed"
        assert objective["valor"]["title"] == target


def test_candidate_pages_are_bounded_and_reach_every_objective(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    inserted = {f"Scalable objective {index:02d}" for index in range(20)}
    with admin(conn) as cur:
        for title in sorted(inserted):
            cur.execute(
                """insert into objective (workspace_id, tipo, titulo, estado)
                   values (%s, 'operativo', %s, 'activo')""",
                (ws, title),
            )
    with espacio(conn, ws) as cur:
        actor, outcome = _start(cur, intake_world, objective=None)
        _choose(cur, actor, outcome.request_id, "Sí")
        shown = set()
        while True:
            choices = _active_choices(cur, outcome.request_id)
            assert len(choices) <= I.CANDIDATE_PAGE_SIZE + 2
            assert I.OTHER in choices
            shown.update(etiqueta_sin_icono(label) for label in choices
                         if label not in {I.VER_MAS, I.OTHER})
            if I.VER_MAS not in choices:
                break
            _choose(cur, actor, outcome.request_id, "Ver más")
        assert inserted <= shown


def test_no_match_model_proposal_still_pages_known_objectives_before_free_text(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    inserted = {f"Known objective {index:02d}" for index in range(12)}
    with admin(conn) as cur:
        for title in sorted(inserted):
            cur.execute(
                """insert into objective (workspace_id, tipo, titulo, estado)
                   values (%s, 'operativo', %s, 'activo')""",
                (ws, title),
            )
    with espacio(conn, ws) as cur:
        _, outcome = _start(
            cur, intake_world, objective="objective that does not exist",
            buttons_first=True,
        )
        shown = set()
        while True:
            choices = _active_choices(cur, outcome.request_id)
            assert len(choices) <= I.CANDIDATE_PAGE_SIZE + 2
            assert I.OTHER in choices
            assert I.CANCELAR_BORRADOR not in choices
            shown.update(etiqueta_sin_icono(label) for label in choices
                         if label not in {I.VER_MAS, I.OTHER})
            if I.VER_MAS not in choices:
                break
            _choose(cur, _actor(cur, intake_world), outcome.request_id, "Ver más")
        assert inserted <= shown
        cur.execute(
            """select count(*) n from task_intake_free_text_slot
                where request_id = %s and estado = 'active'""",
            (outcome.request_id,),
        )
        assert cur.fetchone()["n"] == 0


def test_empty_entity_set_offers_simple_cancel_instead_of_free_text(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with admin(conn) as cur:
        cur.execute("delete from objective where workspace_id = %s", (ws,))
    with espacio(conn, ws) as cur:
        _, outcome = _start(
            cur, intake_world, objective="missing", buttons_first=True)
        assert outcome.text == I.NO_CANDIDATES
        assert set(_active_choices(cur, outcome.request_id)) == {
            I.CANCELAR_BORRADOR}
        assert not any(term in outcome.text.casefold()
                       for term in ("intake", "request_id", "draft_id"))
        cur.execute(
            """select count(*) n from task_intake_free_text_slot
                where request_id = %s and estado = 'active'""",
            (outcome.request_id,),
        )
        assert cur.fetchone()["n"] == 0


def test_preview_is_server_rendered_complete_and_transport_bounded(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, outcome = _start(cur, intake_world)
        completed = _complete(cur, intake_world, outcome.request_id, actor)
        assert completed.pending_action_id
        cur.execute(
            """select cuerpo from message_outbox
                where pending_action_id = %s""",
            (completed.pending_action_id,),
        )
        preview = cur.fetchone()["cuerpo"]
        assert I.telegram_text_length(preview) <= I.SAFE_TELEGRAM_TEXT
        for committed in ("Inspect relief valve", "Reduce service delay",
                          "Sin descripción", "Sam North", "Field Services", "29/02/2028",
                          "Signed test record attached", "test record"):
            assert committed in preview
        cur.execute(
            """select estado, valor, proposed_by from task_intake_field
                where request_id = %s and campo = 'evidence'""",
            (outcome.request_id,),
        )
        evidence = cur.fetchone()
        assert evidence["estado"] == "confirmed"
        assert evidence["valor"] == {"items": ["test record"], "version": 1}
        assert evidence["proposed_by"] == "server"


def test_preview_accepts_exact_utf16_safe_bound_without_truncation():
    base = I.render_preview(
        title="T", objective="O", area="A", responsible="R",
        due_date="2028-02-29", acceptance_criterion="", evidence=["E"],
    )
    room = I.SAFE_TELEGRAM_TEXT - I.telegram_text_length(base)
    preview = I.render_preview(
        title="T", objective="O", area="A", responsible="R",
        due_date="2028-02-29", acceptance_criterion="x" * room,
        evidence=["E"],
    )
    assert I.telegram_text_length(preview) == I.SAFE_TELEGRAM_TEXT
    assert preview.count("x") == room


@pytest.mark.parametrize("field", tuple(I.USER_FIELD_LIMITS))
def test_arbitrary_long_model_values_never_reach_a_visible_prompt(
        intake_world, conn, field):
    ws = intake_world["north-lab"]["id"]
    huge = "👩\u200d🔧" * (I.USER_FIELD_LIMITS[field] + 1)
    with espacio(conn, ws) as cur:
        _, outcome = _start(cur, intake_world, **{field: huge})
        cur.execute(
            """select estado from task_intake_field
                where request_id = %s and campo = %s""",
            (outcome.request_id, field),
        )
        assert cur.fetchone()["estado"] == "missing"
        cur.execute(
            "select cuerpo from message_outbox where cuerpo like '%%👩%%'",
        )
        assert cur.fetchall() == []
        cur.execute(
            "select cuerpo from message_outbox where dedupe_key like %s",
            (f"intake:{outcome.request_id}:%",),
        )
        assert all(I.telegram_text_length(row["cuerpo"]) <= I.SAFE_TELEGRAM_TEXT
                   for row in cur.fetchall())


@pytest.mark.parametrize("field", tuple(I.USER_FIELD_LIMITS))
def test_arbitrary_long_user_value_reopens_only_the_exact_controlled_field(
        intake_world, conn, field):
    ws = intake_world["north-lab"]["id"]
    huge = "👩\u200d🔧" * (I.USER_FIELD_LIMITS[field] + 1)
    with espacio(conn, ws) as cur:
        actor, outcome = _start(cur, intake_world)
        cur.execute(
            """update task_intake_choice_set set estado = 'invalidated'
                where request_id = %s and estado = 'active'""",
            (outcome.request_id,),
        )
        cur.execute(
            """insert into inbound_message
                 (workspace_id, telegram_message_id, chat_id, app_user_id, texto)
                values (%s, %s, 71001, %s, %s) returning id""",
            (ws, 1000 + list(I.USER_FIELD_LIMITS).index(field),
             actor.app_user_id, huge),
        )
        inbound_id = str(cur.fetchone()["id"])
        cur.execute(
            """insert into task_intake_free_text_slot
                 (workspace_id, request_id, campo, request_version)
               values (%s, %s, %s, 1)""",
            (ws, outcome.request_id, field),
        )
        rejected = I.consume_pending_text(
            cur, actor, chat_id=71001,
            source_inbound_id=inbound_id, source_raw_text=huge, now=NOW,
        )
        assert rejected and rejected.inert
        visible_field = {
            "title": "título", "description": "descripción",
            "objective": "objetivo", "responsible": "responsable",
            "area": "área", "due_date": "fecha objetivo",
            "acceptance_criterion": "criterio de aceptación",
        }[field]
        assert visible_field in rejected.text.lower()
        assert str(I.USER_FIELD_LIMITS[field]) in rejected.text
        cur.execute(
            """select campo from task_intake_free_text_slot
                where request_id = %s and estado = 'active'""",
            (outcome.request_id,),
        )
        assert cur.fetchone()["campo"] == field


@pytest.mark.parametrize("cause", ("objective", "responsible", "area", "evidence"))
def test_oversized_server_configuration_fails_closed_without_user_field_loop(
        intake_world, conn, cause):
    ws = intake_world["north-lab"]["id"]
    huge = "configured " * 100
    with admin(conn) as cur:
        if cause == "objective":
            cur.execute("update objective set titulo = titulo || %s where id = %s",
                        (huge, intake_world["north-lab"]["objectives"][0]))
        elif cause == "responsible":
            cur.execute("update app_user set nombre = nombre || %s where id = %s",
                        (huge, intake_world["north-lab"]["people"]["Sam North"]["app_user_id"]))
        elif cause == "area":
            cur.execute("update area set nombre = nombre || %s where id = %s",
                        (huge, intake_world["north-lab"]["areas"]["field"]))
        else:
            cur.execute(
                """update task_evidence_policy set evidencia_requerida = %s
                    where workspace_id = %s and area_id = %s""",
                ([huge], ws, intake_world["north-lab"]["areas"]["field"]),
            )
    with espacio(conn, ws) as cur:
        actor, outcome = _start(cur, intake_world)
        last = outcome
        for _ in range(8):
            choices = _active_choices(cur, outcome.request_id)
            if set(choices) == {I.CANCELAR_BORRADOR}:
                break
            preferred = next((label for label in choices if label == I.CONFIRM), None)
            preferred = preferred or next(
                (label for label in choices if "Reduce service delay" in label), None)
            preferred = preferred or next(
                (label for label in choices if "Sam North" in label), None)
            preferred = preferred or next(
                (label for label in choices if "Field Services" in label), None)
            assert preferred
            last = _choose(cur, actor, outcome.request_id, preferred)
        assert last.text == I.CONFIG_ERROR
        assert set(_active_choices(cur, outcome.request_id)) == {I.CANCELAR_BORRADOR}
        cur.execute(
            """select count(*) n from task_intake_free_text_slot
                where request_id = %s and estado = 'active'""",
            (outcome.request_id,),
        )
        assert cur.fetchone()["n"] == 0
    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 1
        cur.execute(
            """select count(*) n from audit_log
                where accion = 'configuracion_intake_invalida'"""
        )
        assert cur.fetchone()["n"] == 1


def test_normalized_emoji_content_roundtrips_preview_draft_and_task(
        intake_world, conn, authority_conn):
    ws = intake_world["north-lab"]["id"]
    title = "Inspect intake preview pending request_id draft_id cafe\u0301 👩\u200d🔧"
    description = "Family marker 👨\u200d👩\u200d👧\u200d👦"
    criterion = ("Keep intake preview pending request_id draft_id joiner "
                 "👩\u200d🔧 and remove\u202e control")
    with espacio(conn, ws) as cur:
        actor, outcome = _start(
            cur, intake_world, title=title, description=description,
            acceptance_criterion=criterion,
        )
        completed = _complete(cur, intake_world, outcome.request_id, actor)
        expected_title = (
            "Inspect intake preview pending request_id draft_id café 👩\u200d🔧")
        expected_criterion = (
            "Keep intake preview pending request_id draft_id joiner "
            "👩\u200d🔧 and remove control")
        assert expected_title in completed.text
        assert description in completed.text
        assert expected_criterion in completed.text
        confirm = P.opcion_por_etiqueta(cur, completed.pending_action_id,
                                        "Confirmar").token
        cur.execute(
            """select telegram_user_id, chat_id from integrante i
                 join pending_action p on p.membership_id = i.membership_id
                where p.id = %s""",
            (completed.pending_action_id,),
        )
        terminal_actor = cur.fetchone()
    conn.commit()
    with autoridad(authority_conn) as cur:
        result = P.resolver_borrador(
            cur, ws, confirm, terminal_actor["telegram_user_id"],
            terminal_actor["chat_id"],
        )
    with admin(conn) as cur:
        cur.execute("select titulo, descripcion, criterio_aceptacion from task where id = %s",
                    (result.task_id,))
        task = cur.fetchone()
        assert task == {
            "titulo": expected_title,
            "descripcion": description,
            "criterio_aceptacion": expected_criterion,
        }


def test_choice_race_has_one_winner_and_persisted_inert_loser(
        intake_world, conn, uri):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, outcome = _start(cur, intake_world)
        tokens = _active_choices(cur, outcome.request_id)
    conn.commit()
    barrier = threading.Barrier(2)
    results = []

    def click(token):
        other = conectar(uri)
        try:
            other.commit()
            with espacio(other, ws) as cur:
                local_actor = _actor(cur, intake_world)
                barrier.wait()
                results.append(I.resolve_choice(
                    cur, local_actor, token=token, chat_id=71001, now=NOW))
            other.commit()
        finally:
            other.close()

    threads = [threading.Thread(target=click, args=(tokens[label],))
               for label in ("Sí", I.OTHER)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert sum(result.changed for result in results) == 1
    assert sum(result.inert for result in results) == 1


def test_terminal_cancel_and_confirm_are_exactly_once_with_replay(
        intake_world, conn, authority_conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, outcome = _start(cur, intake_world)
        completed = _complete(cur, intake_world, outcome.request_id, actor)
        confirm = P.opcion_por_etiqueta(cur, completed.pending_action_id,
                                        "Confirmar").token
        cur.execute(
            """select telegram_user_id from integrante
                where membership_id = (select membership_id from pending_action
                                        where id = %s)""",
            (completed.pending_action_id,),
        )
        approver_tg = cur.fetchone()["telegram_user_id"]
    conn.commit()
    with autoridad(authority_conn) as cur:
        first = P.resolver_borrador(cur, ws, confirm, approver_tg, approver_tg)
    with autoridad(authority_conn) as cur:
        replay = P.resolver_borrador(cur, ws, confirm, approver_tg, approver_tg)
    assert first and first.task_id
    assert replay and replay.task_id == first.task_id and replay.replay
    with admin(conn) as cur:
        cur.execute("select estado from task_intake_request where id = %s",
                    (outcome.request_id,))
        assert cur.fetchone()["estado"] == "converted"
        cur.execute("select estado from task_draft where id = (select task_draft_id "
                    "from task_intake_request where id = %s)", (outcome.request_id,))
        assert cur.fetchone()["estado"] == "converted"
        cur.execute("select count(*) n from audit_log where accion = "
                    "'confirmar_borrador_tarea' and sujeto_id = %s", (first.task_id,))
        assert cur.fetchone()["n"] == 1


def test_terminal_cancel_is_audited_and_replayed_exactly_once(
        intake_world, conn, authority_conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, outcome = _start(cur, intake_world)
        completed = _complete(cur, intake_world, outcome.request_id, actor)
        cancel = P.opcion_por_etiqueta(cur, completed.pending_action_id,
                                       "Cancelar").token
        cur.execute(
            """select telegram_user_id from integrante
                where membership_id = (select membership_id from pending_action
                                        where id = %s)""",
            (completed.pending_action_id,),
        )
        approver_tg = cur.fetchone()["telegram_user_id"]
    conn.commit()
    with autoridad(authority_conn) as cur:
        first = P.resolver_borrador(cur, ws, cancel, approver_tg, approver_tg)
    with autoridad(authority_conn) as cur:
        replay = P.resolver_borrador(cur, ws, cancel, approver_tg, approver_tg)
    assert first and first.cancelada and not first.replay
    assert replay and replay.cancelada and replay.replay
    with admin(conn) as cur:
        cur.execute(
            "select estado, task_draft_id from task_intake_request where id = %s",
            (outcome.request_id,),
        )
        request = cur.fetchone()
        assert request["estado"] == "cancelled"
        cur.execute("select estado from task_draft where id = %s",
                    (request["task_draft_id"],))
        assert cur.fetchone()["estado"] == "cancelled"
        cur.execute(
            """select count(*) n from audit_log
                where accion = 'cancelar_ingreso_tarea'
                  and sujeto_id = %s""",
            (request["task_draft_id"],),
        )
        assert cur.fetchone()["n"] == 1
        cur.execute(
            """select count(*) n from message_outbox
                where dedupe_key = %s""",
            (f"{ws}:intake-terminal:{completed.pending_action_id}:cancelled",),
        )
        assert cur.fetchone()["n"] == 1


def test_terminal_callback_requires_originating_chat(
        intake_world, conn, authority_conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, outcome = _start(cur, intake_world)
        completed = _complete(cur, intake_world, outcome.request_id, actor)
        confirm = P.opcion_por_etiqueta(cur, completed.pending_action_id,
                                        "Confirmar").token
        cur.execute(
            """select telegram_user_id from integrante
                where membership_id = (select membership_id from pending_action
                                        where id = %s)""",
            (completed.pending_action_id,),
        )
        approver_tg = cur.fetchone()["telegram_user_id"]
    conn.commit()
    with autoridad(authority_conn) as cur:
        with pytest.raises(Denegado):
            P.resolver_borrador(cur, ws, confirm, approver_tg, approver_tg + 99)
    with autoridad(authority_conn) as cur:
        accepted = P.resolver_borrador(cur, ws, confirm, approver_tg, approver_tg)
    assert accepted and accepted.task_id


def test_no_mutating_tool_output_is_truth_marked_and_has_no_buttons(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor = _actor(cur, intake_world)
        cal = Calendario.desde_base(cur, ws)
        result = responder(
            cur, actor, "No, do not create anything",
            SimpleNamespace(responder=lambda *args: Respuesta(
                texto="Task preview: everything is ready. Confirm?")),
            cal, chat_id=71001, ahora=NOW,
        )
        assert "no se modificó nada" not in result.texto
        cur.execute("select pending_action_id, intake_choice_set_id from message_outbox")
        filas = cur.fetchall()
        assert all(f["intake_choice_set_id"] is None for f in filas)
        # Desde T4b (`leda-orienta`, ADR 0007) un texto que pregunta sin
        # botones propios recibe el cierre genérico del servidor. Lo que este
        # caso protege sigue intacto: el "Confirm?" del modelo, sin ninguna
        # herramienta de por medio, nunca termina en una confirmación -- los
        # únicos botones posibles son los del cierre genérico.
        ids = [f["pending_action_id"] for f in filas if f["pending_action_id"]]
        assert len(ids) <= 1
        if ids:
            cur.execute("select herramienta from pending_action where id = %s",
                        (ids[0],))
            assert cur.fetchone()["herramienta"] == P.SENTINEL_OPCIONES_MODELO
            cur.execute("""select etiqueta from pending_action_option
                            where pending_action_id = %s order by orden""",
                        (ids[0],))
            etiquetas = [f["etiqueta"] for f in cur.fetchall()]
            # Sin `entrante_id` (este turno no viene de un `inbound_message`
            # persistido) el cierre genérico no ofrece "Es una tarea nueva"
            # -- ese botón tiene garantizado fallar sin un mensaje de origen
            # (hallazgo del orquestador, unidad sobre `gateway.py`
            # `_mostrar_tareas_propias`/`agente._encolar_opciones_genericas`).
            assert etiquetas == ["Es sobre una tarea existente",
                                 P.ETIQUETA_SALIR_OPCIONES]


def test_legacy_create_task_is_hidden_and_fails_closed(intake_world, conn):
    assert "crear_tarea" not in {tool["name"] for tool in H.esquemas()}
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor = _actor(cur, intake_world)
        with pytest.raises(Denegado):
            H.ejecutar(cur, actor, "crear_tarea", {"titulo": "hidden"})


class _AnthropicProtocolMock:
    def __init__(self):
        self.calls = []
        self.messages = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if len(self.calls) == 1:
            block = SimpleNamespace(
                type="tool_use", id="route-1", name="route_intent",
                input={
                    "action": "start_task_intake",
                    "task": {
                        "title": "Inspect backup pump",
                        "objective": "delivery quality",
                        "responsible": "Sam",
                        "area": "Field",
                        "due_date": "2 marzo 2028",
                        "acceptance_criterion": "Checklist accepted",
                    },
                },
            )
            return SimpleNamespace(content=[block])
        return SimpleNamespace(content=[SimpleNamespace(
            type="text", text="Fake model preview: confirm everything")])


def test_real_testclient_gateway_with_mocked_anthropic_protocol(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]
    protocol = _AnthropicProtocolMock()
    provider = ProveedorAnthropic("mock-model", "unused", cliente=protocol)
    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    monkeypatch.setattr(gateway, "mantener_chat_activo",
                        lambda *args, **kwargs: __import__("contextlib").nullcontext())
    monkeypatch.setattr(gateway, "config", SimpleNamespace(
        webhook_secret="test-secret", llm_api_key="unused",
        token_bot=lambda slug: "unused-token"))
    monkeypatch.setattr("leda.llm.desde_base", lambda *args: provider)
    client = TestClient(gateway.app)
    user = ws["people"]["Taylor Quinn"]["telegram"]
    response = client.post(
        "/telegram/north-lab",
        json={"message": {"message_id": 811, "text": "Set up the pump check",
                          "chat": {"id": user, "type": "private"},
                          "from": {"id": user}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"},
    )
    assert response.status_code == 200
    assert protocol.calls[0]["tool_choice"] == {
        "type": "tool", "name": "route_intent"}
    assert [tool["name"] for tool in protocol.calls[0]["tools"]] == [
        "route_intent"]
    assert len(protocol.calls) == 1
    with admin(conn) as cur:
        cur.execute("select count(*) n from task_intake_request where workspace_id = %s",
                    (ws["id"],))
        assert cur.fetchone()["n"] == 1
        cur.execute("select cuerpo, pending_action_id, intake_choice_set_id "
                    "from message_outbox order by programado_para")
        messages = cur.fetchall()
        assert messages and all("Fake model preview" not in m["cuerpo"]
                                for m in messages)
        assert any(m["intake_choice_set_id"] for m in messages)
        cur.execute("select texto from inbound_message where telegram_message_id = 811")
        assert cur.fetchone()["texto"] == "Set up the pump check"


class _RoutingProvider:
    def __init__(self, routes, answer="Natural answer"):
        self.routes = list(routes)
        self.answer = answer
        self.route_calls = []
        self.pending_calls = []
        self.main_calls = 0

    def route_intent(self, text, pendiente=None):
        self.route_calls.append(text)
        self.pending_calls.append(pendiente)
        result = self.routes.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    def responder(self, *args):
        self.main_calls += 1
        return Respuesta(texto=self.answer)


def _post_message(conn, monkeypatch, world, provider, raw, *, slug="north-lab",
                  message_id=1400):
    ws = world[slug]
    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    monkeypatch.setattr(gateway, "mantener_chat_activo",
                        lambda *args, **kwargs: __import__("contextlib").nullcontext())
    monkeypatch.setattr(gateway, "config", SimpleNamespace(
        webhook_secret="test-secret", llm_api_key="unused",
        token_bot=lambda selected_slug: "unused-token"))
    monkeypatch.setattr("leda.llm.desde_base", lambda *args: provider)
    user = ws["people"]["Taylor Quinn"]["telegram"]
    response = TestClient(gateway.app).post(
        f"/telegram/{slug}",
        json={"message": {"message_id": message_id, "text": raw,
                          "chat": {"id": user, "type": "private"},
                          "from": {"id": user}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"},
    )
    assert response.status_code == 200
    return ws, user


@pytest.mark.parametrize("raw", [
    "Necesito dejar armada una tarea para revisar la bomba",
    "armame lo de revisar la bomba como tarea, porfa",
    "podems crear para mañana la revisón de la bomba?",
    "Para Sam, la bomba: dejalo como trabajo a completar",
    "Please make the backup pump check a task for the team",
])
def test_varied_task_creation_routes_open_server_choices_first(
        raw, intake_world, conn, monkeypatch):
    provider = _RoutingProvider([IntentRoute(
        IntentAction.START_TASK_INTAKE,
        {"title": "Inspect backup pump", "objective": "service delay",
         "responsible": "Sam", "due_date": "2 marzo 2028",
         "acceptance_criterion": "Checklist accepted"},
    )])
    ws, _ = _post_message(conn, monkeypatch, intake_world, provider, raw)

    assert provider.route_calls == [raw]
    assert provider.main_calls == 0
    with admin(conn) as cur:
        cur.execute(
            "select id, task_draft_id from task_intake_request where workspace_id = %s",
            (ws["id"],),
        )
        request = cur.fetchone()
        assert request and request["task_draft_id"]
        cur.execute("select estado from task_draft where id = %s",
                    (request["task_draft_id"],))
        assert cur.fetchone()["estado"] == "open"
        choices = _active_choices(cur, str(request["id"]))
        assert I.OTHER in choices
        assert any("Reduce service delay" in label for label in choices)
        cur.execute(
            """select * from message_outbox
                where intake_choice_set_id is not null order by programado_para"""
        )
        message = cur.fetchone()
        assert message
        from leda.despachador import _botones
        buttons = _botones(cur, message)
        assert buttons and all(button.callback_data.startswith("i:")
                               for button in buttons)


@pytest.mark.parametrize("raw", [
    "¿Qué tareas tengo abiertas?",
    "cómo viene la tarea de la bomba",
    "actualizá el estado de la tarea que terminé",
    "Do I have any overdue work?",
])
def test_queries_status_and_updates_do_not_start_task_capture(
        raw, intake_world, conn, monkeypatch):
    provider = _RoutingProvider([
        IntentRoute(IntentAction.NORMAL_CONVERSATION)], answer="Te respondo eso.")
    ws, _ = _post_message(conn, monkeypatch, intake_world, provider, raw)

    assert provider.route_calls == [raw]
    assert provider.main_calls == 1
    with admin(conn) as cur:
        cur.execute("select count(*) n from task_intake_request where workspace_id = %s",
                    (ws["id"],))
        assert cur.fetchone()["n"] == 0
        cur.execute("select cuerpo from message_outbox")
        assert cur.fetchone()["cuerpo"] == "Te respondo eso."


def test_router_retries_once_then_starts_without_main_agent(
        intake_world, conn, monkeypatch):
    provider = _RoutingProvider([
        RoutingError("raw model text"),
        IntentRoute(IntentAction.START_TASK_INTAKE,
                    {"objective": "delivery quality"}),
    ])
    ws, _ = _post_message(
        conn, monkeypatch, intake_world, provider,
        "Quiero convertir el chequeo en una tarea")

    assert len(provider.route_calls) == 2
    assert provider.main_calls == 0
    with admin(conn) as cur:
        cur.execute("select count(*) n from task_intake_request where workspace_id = %s",
                    (ws["id"],))
        assert cur.fetchone()["n"] == 1


def test_router_fails_closed_after_one_retry_without_raw_text(
        intake_world, conn, monkeypatch):
    provider = _RoutingProvider([
        RoutingError("start_task_intake raw output"),
        RoutingError("request_id=secret raw output"),
    ])
    ws, _ = _post_message(
        conn, monkeypatch, intake_world, provider,
        "Quiero convertir el chequeo en una tarea")

    assert len(provider.route_calls) == 2
    assert provider.main_calls == 0
    with admin(conn) as cur:
        cur.execute("select count(*) n from task_intake_request where workspace_id = %s",
                    (ws["id"],))
        assert cur.fetchone()["n"] == 0
        cur.execute("select cuerpo from message_outbox")
        body = cur.fetchone()["cuerpo"]
        assert "no pude" in body.casefold() and "Estado: sin cambios." in body
        assert "start_task_intake" not in body and "request_id" not in body


def test_active_choice_state_is_read_as_a_pending_question_not_by_the_main_model(
        intake_world, conn, monkeypatch):
    # ADR 0013 rule 1 (T9-R1c-2): an open choice is a pending question, so the
    # message goes through one typed routing call that receives it (never a
    # blind reminder), and a chat remark re-sends the same choice with its
    # buttons without waking the main model.
    provider = _RoutingProvider([
        IntentRoute(IntentAction.START_TASK_INTAKE, {"objective": "service delay"}),
        IntentRoute(IntentAction.NORMAL_CONVERSATION,
                    respecto_pendiente=RespectoPendiente.CHARLA)])
    ws, _ = _post_message(
        conn, monkeypatch, intake_world, provider,
        "Armemos una tarea para la revisión", message_id=1500)
    _post_message(
        conn, monkeypatch, intake_world, provider,
        "¿cuál de estas opciones conviene?", message_id=1501)

    assert len(provider.route_calls) == 2
    assert provider.pending_calls[0] is None
    assert "elección" in provider.pending_calls[1]
    assert provider.main_calls == 0
    with admin(conn) as cur:
        cur.execute("select count(*) n from task_intake_request where workspace_id = %s",
                    (ws["id"],))
        assert cur.fetchone()["n"] == 1
        cur.execute("select count(*) n from message_outbox where intake_choice_set_id is not null")
        assert cur.fetchone()["n"] == 2


def test_active_free_text_state_is_read_as_a_pending_question_not_by_the_main_model(
        intake_world, conn, monkeypatch):
    # ADR 0013 rule 1 (T9-R1c-1): the free-text field is a pending question,
    # so the message goes through one typed routing call that receives it
    # (never a blind consume), and the answer is still not handled by the
    # main model.
    provider = _RoutingProvider([
        IntentRoute(IntentAction.START_TASK_INTAKE, {"objective": "service delay"}),
        IntentRoute(IntentAction.NORMAL_CONVERSATION,
                    respecto_pendiente=RespectoPendiente.RESPONDE)])
    ws, user = _post_message(
        conn, monkeypatch, intake_world, provider,
        "Armemos una tarea para la revisión", message_id=1550)
    with espacio(conn, ws["id"]) as cur:
        actor = _actor(cur, intake_world)
        cur.execute(
            "select id from task_intake_request where workspace_id = %s",
            (ws["id"],),
        )
        request_id = str(cur.fetchone()["id"])
        _choose(cur, actor, request_id, "Otra opción", chat_id=user)

    _post_message(
        conn, monkeypatch, intake_world, provider,
        "Reduce service delay 1", message_id=1551)

    assert len(provider.route_calls) == 2
    assert provider.pending_calls[0] is None
    assert "Escribí parte del nombre del objetivo" in provider.pending_calls[1]
    assert provider.main_calls == 0
    with admin(conn) as cur:
        cur.execute(
            """select estado, source_raw_text from task_intake_field
                where request_id = %s and campo = 'objective'""",
            (request_id,),
        )
        field = cur.fetchone()
        assert field["estado"] == "confirmed"
        assert field["source_raw_text"] == "Reduce service delay 1"


def test_routing_stays_scoped_across_workspaces(
        intake_world, conn, monkeypatch):
    provider = _RoutingProvider([
        IntentRoute(IntentAction.START_TASK_INTAKE, {"objective": "service delay"}),
        IntentRoute(IntentAction.START_TASK_INTAKE, {"objective": "delivery quality"}),
    ])
    for index, slug in enumerate(("north-lab", "west-studio"), start=1):
        _post_message(conn, monkeypatch, intake_world, provider,
                      "Create the task in this workspace", slug=slug,
                      message_id=1600 + index)
    with admin(conn) as cur:
        cur.execute("select workspace_id, count(*) n from task_intake_request group by workspace_id")
        assert {str(row["workspace_id"]): row["n"] for row in cur.fetchall()} == {
            intake_world["north-lab"]["id"]: 1,
            intake_world["west-studio"]["id"]: 1,
        }


def test_two_workspaces_do_not_share_requests_or_candidates(intake_world, conn):
    request_ids = []
    for slug, chat in (("north-lab", 71001), ("west-studio", 71101)):
        ws = intake_world[slug]["id"]
        with espacio(conn, ws) as cur:
            _, outcome = _start(cur, intake_world, workspace_slug=slug,
                                chat_id=chat)
            request_ids.append(outcome.request_id)
            choices = _active_choices(cur, outcome.request_id)
            assert all(slug == "north-lab" or "North Lab" not in label
                       for label in choices)
    assert request_ids[0] != request_ids[1]


def test_workspace_correlation_constraints_and_rls_reject_cross_tenant_children(
        intake_world, conn):
    north = intake_world["north-lab"]
    west = intake_world["west-studio"]
    requests = {}
    for slug, chat in (("north-lab", 71001), ("west-studio", 71101)):
        with espacio(conn, intake_world[slug]["id"]) as cur:
            _, outcome = _start(cur, intake_world, workspace_slug=slug, chat_id=chat)
            requests[slug] = outcome.request_id
    conn.commit()

    with admin(conn) as cur:
        cur.execute(
            """insert into task_draft (workspace_id, creado_por_membership_id)
               values (%s, %s) returning id""",
            (north["id"], north["people"]["Taylor Quinn"]["membership_id"]),
        )
        draft_id = cur.fetchone()["id"]
        cur.execute(
            """insert into inbound_message
                 (workspace_id, telegram_message_id, chat_id, app_user_id, texto)
                   values (%s, 1200, 71999, %s, 'cross source') returning id""",
            (west["id"], west["people"]["Taylor Quinn"]["app_user_id"]),
        )
        foreign_inbound = cur.fetchone()["id"]
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            cur.execute(
                """insert into task_intake_request
                     (workspace_id, membership_id, chat_id, task_draft_id,
                      source_inbound_id, source_raw_text)
                   values (%s, %s, 71999, %s, %s, 'cross source')""",
                (north["id"], north["people"]["Taylor Quinn"]["membership_id"],
                 draft_id, foreign_inbound),
            )
        cur.execute(
            """update task_intake_choice_set set estado = 'invalidated'
                where request_id = %s and estado = 'active'""",
            (requests["west-studio"],),
        )

    with espacio(conn, north["id"]) as cur:
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            cur.execute(
                """insert into task_intake_choice_set
                     (workspace_id, request_id, request_version, tipo)
                   values (%s, %s, 1, 'cross-workspace')""",
                (north["id"], requests["west-studio"]),
            )
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute(
                """insert into task_intake_choice_set
                     (workspace_id, request_id, request_version, tipo)
                   values (%s, %s, 1, 'cross-rls')""",
                (west["id"], requests["west-studio"]),
            )


def test_migration_clean_schema_parity_and_guarded_rollback():
    schema = (ROOT / "db" / "esquema.sql").read_text("utf-8")
    migration = (ROOT / "db" / "migrations" /
                 "0002_general_task_intake.sql").read_text("utf-8")
    rollback = (ROOT / "db" / "rollbacks" /
                "0002_general_task_intake.sql").read_text("utf-8")
    for table in ("task_intake_request", "task_intake_field",
                  "task_intake_choice_set", "task_intake_choice",
                  "task_intake_free_text_slot"):
        assert f"create table {table}" in schema
        assert f"create table {table}" in migration
        assert f"drop table if exists {table}" in rollback
    assert migration.startswith("\\encoding UTF8\n\\set ON_ERROR_STOP on\n")
    assert "0002 requires an unmodified UTF-8 input stream" in migration
    assert "0001_task_commitment.sql" in migration
    assert "legacy crear_tarea" in migration.lower()
    for constraint in (
        "message_outbox_telegram_payload",
        "pending_action_option_telegram_label",
        "task_intake_choice_telegram_label",
        "task_draft_title_payload",
        "task_draft_description_payload",
        "task_draft_acceptance_payload",
    ):
        assert constraint in schema
        assert constraint in migration
    for constraint in (
        "message_outbox_telegram_payload",
        "pending_action_option_telegram_label",
        "task_draft_title_payload",
        "task_draft_description_payload",
        "task_draft_acceptance_payload",
    ):
        assert constraint in rollback
    assert migration.index("0002 preflight failed") < migration.index(
        "create function telegram_utf16_units")
    assert migration.index("0002 preflight failed") < migration.index(
        "alter table task_draft\n  add column estado")
    assert "converted_task_id is not null" in rollback
    assert rollback.index("pg_advisory_xact_lock") < rollback.index("if exists")
    assert rollback.index("lock table task_intake_request") < rollback.index("if exists")
    assert "confirmar_borrador_tarea(uuid, text, bigint, bigint)" in migration
