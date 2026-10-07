"""El webhook del motor (`POST /telegram/{slug}` de `leda.entrada`; E3-7).

La ruta de producción: Telegram entrega cada update del bot de un espacio con el secreto de ese
bot en la cabecera `X-Telegram-Bot-Api-Secret-Token`. Lo que se hace con el update es lo mismo
que en el escuchador (`leda.motor.recibir`). Son garantías de la frontera:

- sin el secreto correcto no pasa nada: ni un mensaje guardado, ni un turno, ni una respuesta;
- el secreto es de cada bot (`entrada.secreto_del_bot`): el de un espacio no abre el webhook
  de otro, y sin secreto configurado el webhook no atiende a nadie;
- quien escribe al bot de un espacio que no es el suyo no es atendido, y nada de su espacio se
  toca (el aislamiento lo da `identificar_en_espacio` y la RLS de `db.espacio`);
- un mensaje válido corre un turno, deja una respuesta en el outbox y el registro de turnos.

Con `TestClient`, la IA guionada y Telegram de mentira: nada sale a la red.
"""

from __future__ import annotations

import dataclasses

import pytest
from fastapi.testclient import TestClient

from leda import config as config_mod
from leda import entrada
from leda.db import admin
from leda.despachador import TransporteDePrueba
from leda.motor.ia import IAGuionada, Jugada

from tests.motor.ayudantes import TelegramFalso, mensaje_de_telegram, toque_de_telegram

SECRETO = "secreto-de-prueba"
TOKENS = {"north-lab": "7001:token-norte", "west-studio": "7002:token-oeste",
          "admin": "7009:token-admin"}


@pytest.fixture
def webhook(conn, intake_world, monkeypatch):
    """El webhook sobre la base efímera, con el secreto configurado, los tokens de prueba, la
    IA guionada y Telegram de mentira."""
    ia = IAGuionada()
    telegram = TelegramFalso()
    salida = TransporteDePrueba()
    monkeypatch.setattr(entrada, "config",
                        dataclasses.replace(config_mod.config, webhook_secret=SECRETO,
                                            base_url="https://leda.example"))
    monkeypatch.setattr(entrada, "_conn", lambda: conn)
    monkeypatch.setattr(entrada, "_token_de", lambda slug: _token(slug))
    monkeypatch.setattr(entrada, "_ia_de", lambda conn, ws: ia)
    monkeypatch.setattr(entrada, "_cliente_http", telegram.cliente)
    monkeypatch.setattr(entrada, "_INTENTOS", {})
    # Lo que sale por el bot de cada espacio, de mentira.
    monkeypatch.setattr(entrada, "_transporte_de", lambda token: salida, raising=False)
    return {"cliente": TestClient(entrada.app), "ia": ia, "telegram": telegram,
            "salida": salida, "mundo": intake_world}


def _token(slug: str) -> str:
    if slug not in TOKENS:
        raise LookupError(f"Falta el token de {slug}")
    return TOKENS[slug]


def _post(cliente, slug: str, update: dict, secreto: str | None):
    cabeceras = {} if secreto is None else {"X-Telegram-Bot-Api-Secret-Token": secreto}
    return cliente.post(f"/telegram/{slug}", json=update, headers=cabeceras)


def _cuantas(conn, tabla: str, donde: str = "true", *args) -> int:
    with admin(conn) as cur:
        cur.execute(f"select count(*) n from {tabla} where {donde}", args)
        return cur.fetchone()["n"]


def _sin_efectos(conn) -> None:
    for tabla in ("inbound_message", "conversation_turn", "message_outbox", "incident"):
        assert _cuantas(conn, tabla) == 0, tabla


def _de(webhook, espacio: str, persona: str = "Sam North") -> int:
    return webhook["mundo"][espacio]["people"][persona]["telegram"]


# --- El secreto --------------------------------------------------------------------------------

@pytest.mark.parametrize("secreto", [None, "", "otro-secreto"])
def test_sin_el_secreto_del_bot_se_rechaza_sin_efectos(conn, webhook, secreto):
    webhook["ia"].jugadas = [[]]
    webhook["ia"].redacciones = ["Hola."]
    update = mensaje_de_telegram(10, "arranqué", _de(webhook, "north-lab"))

    r = _post(webhook["cliente"], "north-lab", update, secreto)

    assert r.status_code == 403
    _sin_efectos(conn)
    assert webhook["ia"].pedidos_de_jugadas == []


def test_el_secreto_de_un_bot_no_abre_el_webhook_de_otro(conn, webhook):
    update = mensaje_de_telegram(11, "arranqué", _de(webhook, "north-lab"))

    r = _post(webhook["cliente"], "north-lab", update, entrada.secreto_del_bot("west-studio"))

    assert r.status_code == 403
    _sin_efectos(conn)


def test_sin_secreto_configurado_el_webhook_no_atiende_a_nadie(conn, webhook, monkeypatch):
    monkeypatch.setattr(entrada, "config",
                        dataclasses.replace(config_mod.config, webhook_secret=""))
    update = mensaje_de_telegram(12, "arranqué", _de(webhook, "north-lab"))

    r = _post(webhook["cliente"], "north-lab", update, "")

    assert r.status_code == 403
    _sin_efectos(conn)


def test_un_espacio_sin_bot_configurado_no_se_atiende(conn, webhook, monkeypatch):
    monkeypatch.setattr(entrada, "_token_de", lambda slug: _token("ninguno"))
    update = mensaje_de_telegram(13, "arranqué", _de(webhook, "north-lab"))

    r = _post(webhook["cliente"], "north-lab", update, entrada.secreto_del_bot("north-lab"))

    assert r.status_code == 404
    _sin_efectos(conn)


# --- El aislamiento ----------------------------------------------------------------------------

def test_quien_escribe_al_bot_de_otro_espacio_no_es_atendido(conn, webhook):
    """Sam North 2 es de West Studio y le escribe al bot de North Lab: no se guarda nada, no
    corre ningún turno, no sale nada, ni en North Lab ni en West Studio."""
    webhook["ia"].jugadas = [[]]
    webhook["ia"].redacciones = ["Hola."]
    update = mensaje_de_telegram(20, "arranqué", _de(webhook, "west-studio"))

    r = _post(webhook["cliente"], "north-lab", update, entrada.secreto_del_bot("north-lab"))

    assert r.status_code == 200
    _sin_efectos(conn)
    assert webhook["ia"].pedidos_de_jugadas == []


def test_un_toque_de_alguien_de_otro_espacio_solo_recibe_la_senal(conn, webhook):
    update = toque_de_telegram(21, "m:token-cualquiera", _de(webhook, "west-studio"))

    r = _post(webhook["cliente"], "north-lab", update, entrada.secreto_del_bot("north-lab"))

    assert r.status_code == 200
    assert webhook["telegram"].metodos() == ["answerCallbackQuery"]
    _sin_efectos(conn)


# --- Un mensaje válido -------------------------------------------------------------------------

def test_un_mensaje_valido_corre_un_turno_y_deja_una_respuesta(conn, webhook):
    webhook["ia"].jugadas = [[]]
    webhook["ia"].redacciones = ["Hola, Sam."]
    norte = webhook["mundo"]["north-lab"]
    update = mensaje_de_telegram(30, "hola", _de(webhook, "north-lab"))

    primero = _post(webhook["cliente"], "north-lab", update, entrada.secreto_del_bot("north-lab"))
    repetido = _post(webhook["cliente"], "north-lab", update,
                     entrada.secreto_del_bot("north-lab"))      # Telegram lo reentrega

    assert primero.status_code == repetido.status_code == 200
    with admin(conn) as cur:
        cur.execute("select * from inbound_message")
        [entrante] = cur.fetchall()
        cur.execute("select sentido from conversation_turn order by numero")
        turnos = [f["sentido"] for f in cur.fetchall()]
        cur.execute("select workspace_id, chat_id, cuerpo, es_respuesta, entrante_id "
                    "from message_outbox")
        [respuesta] = cur.fetchall()
    assert str(entrante["workspace_id"]) == norte["id"]
    assert entrante["telegram_bot_id"] == 7001 and entrante["telegram_message_id"] == 30
    assert turnos == ["entrada", "salida"]
    assert len(webhook["ia"].pedidos_de_jugadas) == 1
    assert str(respuesta["workspace_id"]) == norte["id"]
    assert respuesta["chat_id"] == _de(webhook, "north-lab") and respuesta["cuerpo"] == "Hola, Sam."
    assert respuesta["es_respuesta"] and respuesta["entrante_id"] == entrante["id"]
    assert _cuantas(conn, "incident") == 0


def test_la_respuesta_sale_al_atender_el_update_sin_esperar_al_despacho_de_fondo(conn,
                                                                               webhook):
    """Pedido del usuario (2026-10-07): la respuesta sale apenas termina su turno, también por
    el webhook. Cuando Telegram recibe el 200, el mensaje ya se entregó: no espera la vuelta
    siguiente del despacho de fondo (`leda.motor.fondo`). Sale por el outbox, como siempre."""
    webhook["ia"].jugadas = [[]]
    webhook["ia"].redacciones = ["Hola, Sam."]
    update = mensaje_de_telegram(33, "hola", _de(webhook, "north-lab"))

    r = _post(webhook["cliente"], "north-lab", update, entrada.secreto_del_bot("north-lab"))

    assert r.status_code == 200
    assert [(e.chat_id, e.texto) for e in webhook["salida"].enviados] == [
        (_de(webhook, "north-lab"), "Hola, Sam.")]
    with admin(conn) as cur:
        cur.execute("select estado::text e from message_outbox")
        assert [f["e"] for f in cur.fetchall()] == ["enviado"]


def test_sin_ia_configurada_la_persona_recibe_el_texto_fijo_y_queda_un_incidente(
        conn, webhook, monkeypatch):
    from leda.motor.recibir import IANoConfigurada
    from leda.motor.turno import TEXTO_SI_LA_IA_FALLA

    monkeypatch.setattr(entrada, "_ia_de",
                        lambda conn, ws: IANoConfigurada("No hay modelo configurado."))
    update = mensaje_de_telegram(31, "hola", _de(webhook, "north-lab"))

    r = _post(webhook["cliente"], "north-lab", update, entrada.secreto_del_bot("north-lab"))

    assert r.status_code == 200
    with admin(conn) as cur:
        cur.execute("select cuerpo from message_outbox")
        assert [f["cuerpo"] for f in cur.fetchall()] == [TEXTO_SI_LA_IA_FALLA]
    assert _cuantas(conn, "incident", "etapa = 'turno_conversacion'") == 1


def test_una_falla_al_recibir_pide_la_reentrega_y_a_los_intentos_lo_deja(conn, webhook,
                                                                         monkeypatch):
    """Como en el escuchador: si la base se cae al guardar, Telegram lo reentrega (un error
    5xx); a los `INTENTOS_POR_UPDATE`, un incidente y el texto fijo, nunca en silencio."""
    import psycopg

    from leda.motor.recibir import INTENTOS_POR_UPDATE, Recepcion
    from leda.motor.turno import TEXTO_SI_LA_IA_FALLA

    def falla(self, *args, **kwargs):
        raise psycopg.OperationalError("la base no contesta")

    monkeypatch.setattr(Recepcion, "_guardar", falla)
    update = mensaje_de_telegram(32, "hola", _de(webhook, "north-lab"))
    secreto = entrada.secreto_del_bot("north-lab")

    codigos = [_post(webhook["cliente"], "north-lab", update, secreto).status_code
               for _ in range(INTENTOS_POR_UPDATE)]

    assert codigos == [503] * (INTENTOS_POR_UPDATE - 1) + [200]
    assert _cuantas(conn, "incident", "etapa = 'turno_conversacion'") == 1
    with admin(conn) as cur:
        cur.execute("select cuerpo from message_outbox")
        assert [f["cuerpo"] for f in cur.fetchall()] == [TEXTO_SI_LA_IA_FALLA]


# --- El bot de administración y el registro de los webhooks ------------------------------------

def test_el_bot_de_administracion_registra_el_chat_de_un_administrador(conn, webhook):
    morgan = webhook["mundo"]["north-lab"]["people"]["Morgan Hale"]
    with admin(conn) as cur:
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                    (morgan["app_user_id"],))
    conn.commit()
    update = mensaje_de_telegram(40, "hola", morgan["telegram"])

    afuera = _post(webhook["cliente"], "admin", mensaje_de_telegram(41, "hola", 99999),
                   entrada.secreto_del_bot("admin"))
    r = _post(webhook["cliente"], "admin", update, entrada.secreto_del_bot("admin"))

    assert afuera.status_code == r.status_code == 200
    with admin(conn) as cur:
        cur.execute("select actor_app_user_id, detalle from audit_log "
                    "where accion = 'mensaje_admin'")
        [registro] = cur.fetchall()
    assert str(registro["actor_app_user_id"]) == morgan["app_user_id"]
    assert registro["detalle"] == {"chat_id": morgan["telegram"]}


def test_registrar_webhooks_le_da_a_cada_bot_su_direccion_y_su_secreto(webhook, monkeypatch):
    telegram = TelegramFalso()
    monkeypatch.setattr(entrada.config.__class__, "espacios_con_token",
                        lambda self: dict(TOKENS))

    resultado = entrada.registrar_webhooks(telegram.cliente())

    assert resultado == {slug: True for slug in TOKENS}
    pedidos = {p["url"].rsplit("/", 1)[-1]: p for metodo, p in telegram.llamadas}
    assert pedidos["north-lab"]["secret_token"] == entrada.secreto_del_bot("north-lab")
    assert pedidos["admin"]["allowed_updates"] == ["message"]
    assert pedidos["west-studio"]["allowed_updates"] == ["message", "callback_query"]
    assert len({p["secret_token"] for p in pedidos.values()}) == len(TOKENS)


def test_registrar_webhooks_se_niega_sin_direccion_o_sin_secreto(monkeypatch):
    for falta in ({"base_url": ""}, {"webhook_secret": ""}):
        monkeypatch.setattr(entrada, "config", dataclasses.replace(
            config_mod.config, **{"base_url": "https://leda.example",
                                  "webhook_secret": SECRETO, **falta}))
        with pytest.raises(LookupError):
            entrada.registrar_webhooks(TelegramFalso().cliente())
