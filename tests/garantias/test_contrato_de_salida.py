"""El contrato de salida: todo mensaje visible pasa por `salida` (normalizado, medido en
unidades UTF-16, partido de forma determinista y con claves de deduplicación propias), la
base exige el mismo contrato, y el despachador entrega cada fila una sola vez.

Movidas desde `tests/test_salida.py` y `tests/test_ciclo.py` (E3-1).
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from leda import onboarding
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.despachador import Boton, TransporteDePrueba, TransporteTelegram
from leda.salida import (BUTTON_TEXT_LIMIT, NO_EFFECT_STATUS, TELEGRAM_TEXT_LIMIT,
                         PayloadValidationError, enqueue_outbox,
                         normalize_visible_text, prepare_payload,
                         telegram_utf16_units, with_no_effect_status)


ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 14, 15, 0, tzinfo=timezone.utc)
BA = ZoneInfo("America/Argentina/Buenos_Aires")


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
    for path in (ROOT / "src" / "leda").glob("*.py"):
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
        # Lo que Leda manda por su cuenta, sin botones (antes, la escalera y la cadencia
        # viejas, retiradas en la E3-7; hoy, los avisos guardados del motor): se parte.
        for tipo, clave in (("informativo", "long-escalation"), ("seguimiento", "long-cadence")):
            enqueue_outbox(cur, workspace_id=ws, chat_id=9002, text=long_copy,
                           recipient_membership_id=membership_id, message_type=tipo,
                           scheduled_for=NOW, dedupe_key=clave, allow_split=True)
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


# ---------------------------------------------------------------------------
# El despachador como transporte (requisito 7): `servir` y `escuchar` corriendo
# a la vez no duplican envíos.
# ---------------------------------------------------------------------------

def test_despachar_con_fila_tomada_por_otra_conexion_no_la_duplica(
        corework, conn, uri):
    """`for update skip locked` es lo que permite correr `servir` y
    `escuchar` sobre el mismo espacio sin que ambos entreguen el mismo
    mensaje: mientras otra conexión sostiene el lock (transacción sin
    `commit` todavía), esta lo saltea en vez de bloquearse o reprocesarlo."""
    from leda.db import conectar
    from leda.despachador import despachar

    ws = corework.workspace_id
    ahora = datetime(2026, 7, 27, 9, 16, tzinfo=BA)
    with espacio(conn, ws) as cur:
        cur.execute("""select membership_id, telegram_user_id from integrante
                        where nombre = 'Marcos Tarquini'""")
        marcos = cur.fetchone()
        enqueue_outbox(cur, workspace_id=ws, chat_id=marcos["telegram_user_id"],
                       text="Tus tareas abiertas: Programar PLC.", message_type="seguimiento",
                       recipient_membership_id=str(marcos["membership_id"]),
                       scheduled_for=ahora, dedupe_key="test:una-fila")
    conn.commit()

    otra = conectar(uri)
    try:
        with otra.transaction():
            with otra.cursor() as cur_otra:
                cur_otra.execute("set local role leda_app")
                cur_otra.execute(
                    "select set_config('leda.workspace_id', %s, true)", (ws,))
                cur_otra.execute(
                    """select id from message_outbox
                        where workspace_id = %s and estado = 'listo'
                        for update skip locked""", (ws,))
                assert len(cur_otra.fetchall()) == 1  # sostiene el lock, sin commit

            transporte = TransporteDePrueba()
            with espacio(conn, ws) as cur:
                cal = Calendario.desde_base(cur, ws)
                r = despachar(cur, ws, transporte, cal, ahora)
            conn.commit()
            assert r["enviados"] == 0        # la fila estaba tomada: la salteó
            assert transporte.enviados == []
        # el `with otra.transaction()` ya confirmó al salir: lock liberado
    finally:
        otra.close()

    transporte2 = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        r2 = despachar(cur, ws, transporte2, cal, ahora)
    conn.commit()
    assert r2["enviados"] == 1               # liberado el lock, ahora sí la entrega
