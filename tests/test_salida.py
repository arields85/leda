from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from prisma import escalera, gateway, onboarding, reloj
from prisma.agente import responder
from prisma.autoridad import Canal, identificar
from prisma.calendario import Calendario
from prisma.db import admin, espacio
from prisma.despachador import Boton, TransporteTelegram
from prisma.llm import ProveedorGuionado, Respuesta
from prisma.salida import (BUTTON_TEXT_LIMIT, TELEGRAM_TEXT_LIMIT,
                             NO_EFFECT_STATUS, PayloadValidationError,
                             enqueue_outbox, normalize_visible_text,
                             prepare_payload, telegram_utf16_units,
                             with_no_effect_status)


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 8, 14, 15, 0, tzinfo=timezone.utc)


def test_payload_contract_normalizes_controls_and_counts_utf16_units():
    assert normalize_visible_text(" Cafe\u0301\r\n👩\u200d🔧\u202e ") == "Café\n👩\u200d🔧"
    assert telegram_utf16_units("a👩") == 3


def test_ordinary_payload_split_is_deterministic_and_dedupe_safe():
    text = "section\n" + ("👩\u200d🔧 result " * 900)
    first = prepare_payload(text, dedupe_key="report:1", allow_split=True)
    second = prepare_payload(text, dedupe_key="report:1", allow_split=True)
    assert first == second
    assert len(first) > 1
    assert len({part.dedupe_key for part in first}) == len(first)
    assert all(telegram_utf16_units(part.text) <= TELEGRAM_TEXT_LIMIT
               for part in first)
    assert all(part.text.startswith(f"({index}/{len(first)})\n")
               for index, part in enumerate(first, 1))


def test_button_payload_never_splits_and_uses_safe_text_budget():
    with pytest.raises(PayloadValidationError, match="botones"):
        prepare_payload("x" * (BUTTON_TEXT_LIMIT + 1), dedupe_key="choice:1",
                        has_buttons=True, allow_split=True)


def test_telegram_transport_revalidates_before_http():
    class NoHttp:
        called = False

        def post(self, *args, **kwargs):
            self.called = True
            raise AssertionError("HTTP must not be reached")

    http = NoHttp()
    transport = TransporteTelegram("unused", cliente=http)
    with pytest.raises(PayloadValidationError):
        transport.enviar(1, "x" * (BUTTON_TEXT_LIMIT + 1),
                         [Boton("Confirm", "p:token")])
    assert not http.called


def test_all_python_outbox_producers_use_the_central_contract():
    offenders = []
    for path in (ROOT / "src" / "prisma").glob("*.py"):
        if path.name == "salida.py":
            continue
        if "insert into message_outbox" in path.read_text("utf-8").lower():
            offenders.append(path.name)
    assert offenders == []


def test_visible_payload_preserves_legitimate_domain_words_exactly():
    raw = "intake preview pending request_id=abc draft_id:xyz"

    assert prepare_payload(raw, dedupe_key="roundtrip")[0].text == raw


@pytest.mark.parametrize("raw", [
    "No se registró ningún cambio.",
    "No pude aplicar el cambio solicitado.",
    "Nothing was changed.",
    "No changes were applied.",
])
def test_no_effect_status_does_not_duplicate_provider_paraphrases(raw):
    rendered = with_no_effect_status(raw)

    assert rendered.count(NO_EFFECT_STATUS) == 1


def test_no_effect_marker_is_server_owned_and_appended_at_most_once():
    supplied = f"No pude completar la operación.\n\n{NO_EFFECT_STATUS}"

    rendered = with_no_effect_status(supplied)

    assert rendered.count(NO_EFFECT_STATUS) == 1
    assert with_no_effect_status("Estado general.", required=False) == "Estado general."


def test_runtime_and_tests_do_not_restore_the_unconditional_no_effect_footer():
    forbidden = "Sin cambios " + "registrados"
    paths = list((ROOT / "src").rglob("*.py"))
    paths += list((ROOT / "tests").rglob("*.py"))
    paths += [ROOT / "db" / "esquema.sql",
              ROOT / "db" / "migrations" / "0002_general_task_intake.sql"]
    assert [str(path.relative_to(ROOT)) for path in paths
            if forbidden in path.read_text("utf-8")] == []


def test_sql_terminal_producers_are_guarded_by_the_same_database_contract():
    schema = (ROOT / "db" / "esquema.sql").read_text("utf-8")
    migration = (ROOT / "db" / "migrations" /
                 "0002_general_task_intake.sql").read_text("utf-8")
    for sql in (schema, migration):
        assert "message_outbox_telegram_payload" in sql
        assert "telegram_utf16_units" in sql


def test_split_outbox_parts_get_strictly_increasing_schedule(corework, conn):
    """Defecto pre-existente, encontrado en la revisión del orquestador del
    2026-09-26 sobre T3a (observación no bloqueante en
    `tests/test_lista_botones.py:511-512`): antes de esta corrección,
    `enqueue_outbox` mandaba todas las partes de un mensaje partido con el
    mismo `programado_para` -- el único valor que ordena
    `despachador.despachar` (`despachador.py:299`) --, y `message_outbox.id`
    es un `uuid` al azar que no desempata, así que el orden de entrega entre
    partes quedaba librado al azar del orden físico con el que Postgres
    devolviera las filas. Cada parte tiene que quedar estrictamente después
    de la anterior, en el mismo orden en que `_split` las generó -- acá se
    verifica ese orden con `dedupe_key` (que sí codifica el índice de cada
    parte de forma estable), no con `programado_para`, para no validar la
    corrección usando la misma columna que se está corrigiendo."""
    ws = corework.workspace_id
    texto = "sección larga de la respuesta para forzar el partido. " * 900
    with espacio(conn, ws) as cur:
        enqueue_outbox(
            cur, workspace_id=ws, chat_id=1, text=texto,
            dedupe_key="split-order-test", scheduled_for=NOW,
            allow_split=True,
        )
        cur.execute(
            """select cuerpo, programado_para from message_outbox
                where dedupe_key like 'split-order-test:part:%'
                order by dedupe_key""")
        filas = cur.fetchall()

    assert len(filas) > 1
    for indice, fila in enumerate(filas, start=1):
        assert fila["cuerpo"].startswith(f"({indice}/{len(filas)})\n")

    marcas = [f["programado_para"] for f in filas]
    assert marcas == sorted(marcas)
    assert len(set(marcas)) == len(marcas)  # sin empates


def test_agent_arbitrary_long_model_output_is_split_before_enqueue(corework, conn):
    ws = corework.workspace_id
    long_answer = "👩\u200d🔧 status " * 900
    with espacio(conn, ws) as cur:
        cur.execute("select telegram_user_id from integrante where nombre = %s",
                    ("Marcos Tarquini",))
        who = identificar(cur, cur.fetchone()["telegram_user_id"],
                          Canal.ESPACIO, ws)
        result = responder(
            cur, who, "status", ProveedorGuionado([Respuesta(texto=long_answer)]),
            Calendario.desde_base(cur, ws), chat_id=9002, ahora=NOW,
        )
        cur.execute("select cuerpo, dedupe_key from message_outbox order by dedupe_key")
        rows = cur.fetchall()
        assert result.texto == long_answer.strip()
        assert len(rows) > 1
        assert len({row["dedupe_key"] for row in rows}) == len(rows)
        assert all(telegram_utf16_units(row["cuerpo"]) <= TELEGRAM_TEXT_LIMIT
                   for row in rows)


def test_gateway_and_onboarding_split_long_informational_copy(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    long_copy = "Welcome 👋 " * 900
    with admin(conn) as cur:
        cur.execute(
            """select u.telegram_user_id
                 from membership m join app_user u on u.id = m.app_user_id
                where m.workspace_id = %s and u.telegram_user_id is not null
                order by u.nombre limit 1""", (ws,))
        telegram_id = cur.fetchone()["telegram_user_id"]
    monkeypatch.setattr(onboarding, "bienvenida", lambda *args: long_copy)
    gateway._activacion(conn, ws, "/start", telegram_id, telegram_id)
    with admin(conn) as cur:
        cur.execute("select cuerpo from message_outbox order by dedupe_key")
        rows = cur.fetchall()
        assert len(rows) > 1
        assert all(telegram_utf16_units(row["cuerpo"]) <= TELEGRAM_TEXT_LIMIT
                   for row in rows)


def test_onboarding_scheduler_and_escalation_split_only_buttonless_messages(
        corework, conn):
    ws = corework.workspace_id
    long_copy = "Operational update 👩\u200d🔧 " * 700
    with admin(conn) as cur:
        cur.execute("update persona_config set presentacion = %s where workspace_id = %s",
                    (long_copy, ws))
        cur.execute("update workspace set grupo_chat_id = -1001 where id = %s", (ws,))
    with espacio(conn, ws) as cur:
        cur.execute("select membership_id from integrante where nombre = %s",
                    ("Marcos Tarquini",))
        membership_id = str(cur.fetchone()["membership_id"])
        assert onboarding.encolar_presentacion(cur, ws, NOW)
        cal = Calendario.desde_base(cur, ws)
        action = escalera.Accion(
            task_id="00000000-0000-0000-0000-000000000001", paso="aviso",
            tipo="informativo", destinatario_membership_id=membership_id, chat_id=9002,
            cuerpo=long_copy, dedupe_key="long-escalation",
        )
        escalera.encolar(cur, ws, [action], cal, NOW)
        reloj._encolar(cur, ws, 9002, membership_id,
                       long_copy, "long-cadence", cal, NOW)
        cur.execute("select cuerpo from message_outbox")
        rows = cur.fetchall()
        assert len(rows) >= 6
        assert all(telegram_utf16_units(row["cuerpo"]) <= TELEGRAM_TEXT_LIMIT
                   for row in rows)


def test_invalid_button_metadata_is_rejected_before_enqueue():
    with pytest.raises(PayloadValidationError, match="etiqueta"):
        prepare_payload("Choose", dedupe_key="bad-label", has_buttons=True,
                        buttons=[SimpleNamespace(etiqueta="x" * 81,
                                                 callback_data="p:ok")])
    with pytest.raises(PayloadValidationError, match="callback"):
        prepare_payload("Choose", dedupe_key="bad-callback", has_buttons=True,
                        buttons=[SimpleNamespace(etiqueta="ok",
                                                 callback_data="p:" + "x" * 80)])
