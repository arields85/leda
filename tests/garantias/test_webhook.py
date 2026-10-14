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


def test_por_el_webhook_el_administrador_pide_el_enlace_de_una_tarea(conn, webhook,
                                                                     monkeypatch):
    """Revisión de la porción 5 (`entrada.py:162`, sin prueba): el pedido `/enlace` por el
    webhook del bot de administración se contesta por el bot de administración, con el enlace
    atado a quien lo pidió, como en el escuchador."""
    from tests.garantias.test_pagina_de_la_tarea import _tarea

    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url="https://leda.example"))
    morgan = webhook["mundo"]["north-lab"]["people"]["Morgan Hale"]
    with admin(conn) as cur:
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                    (morgan["app_user_id"],))
        tarea = _tarea(cur, webhook["mundo"]["north-lab"], titulo="Calibrar la balanza")
    conn.commit()

    r = _post(webhook["cliente"], "admin",
              mensaje_de_telegram(42, "/enlace north-lab balanza", morgan["telegram"]),
              entrada.secreto_del_bot("admin"))

    assert r.status_code == 200
    [enviado] = webhook["salida"].enviados
    assert enviado.chat_id == morgan["telegram"]
    assert enviado.texto.rsplit("\n", 1)[-1].startswith("https://leda.example/tarea/")
    with admin(conn) as cur:
        cur.execute("select admin_app_user_id, task_id from acceso_tarea")
        [acceso] = cur.fetchall()
    conn.commit()
    assert (str(acceso["admin_app_user_id"]), str(acceso["task_id"])) == (
        morgan["app_user_id"], tarea["id"])


def test_registrar_webhooks_le_da_a_cada_bot_su_direccion_y_su_secreto(webhook, monkeypatch):
    telegram = TelegramFalso()
    monkeypatch.setattr(entrada.config.__class__, "espacios_con_token",
                        lambda self: dict(TOKENS))

    resultado = entrada.registrar_webhooks(telegram.cliente())

    assert resultado == {slug: True for slug in TOKENS}
    pedidos = {p["url"].rsplit("/", 1)[-1]: p for metodo, p in telegram.llamadas
               if metodo == "setWebhook"}
    assert pedidos["north-lab"]["secret_token"] == entrada.secreto_del_bot("north-lab")
    # El botón del menú de cada bot, con la dirección del momento (ADR 0024), sin chat_id.
    menus = [p for metodo, p in telegram.llamadas if metodo == "setChatMenuButton"]
    assert len(menus) == len(TOKENS) and all("chat_id" not in p for p in menus)
    botones = {p["menu_button"]["web_app"]["url"]: p["menu_button"]["text"] for p in menus}
    assert botones["https://leda.example/app/abrir/e/north-lab/"] == "Tareas"
    assert botones["https://leda.example/app/abrir/admin/"] == "Administración"
    assert pedidos["admin"]["allowed_updates"] == ["message", "callback_query"]
    assert pedidos["west-studio"]["allowed_updates"] == ["message", "callback_query"]
    assert len({p["secret_token"] for p in pedidos.values()}) == len(TOKENS)


def test_una_falla_del_boton_del_menu_nunca_corta_el_registro_de_los_webhooks(webhook, conn,
                                                                            monkeypatch):
    """R3-menu-failure-aborts-webhook-registration y R2-webhook-path-only-prints: si Telegram no
    acepta el botón del menú, o no se le puede pedir, los webhooks de todos los bots se registran
    igual, y cada falla deja su incidente con su causa (no sólo una línea en la consola)."""
    import httpx

    telegram = TelegramFalso()
    monkeypatch.setattr(entrada.config.__class__, "espacios_con_token",
                        lambda self: dict(TOKENS))

    def atender(pedido: httpx.Request) -> httpx.Response:
        if pedido.url.path.endswith("/setChatMenuButton"):
            if TOKENS["north-lab"] in pedido.url.path:
                raise httpx.ConnectError("sin red")
            if TOKENS["west-studio"] in pedido.url.path:
                return httpx.Response(200, json={"ok": False, "description": "Bad Request"})
        return telegram(pedido)

    resultado = entrada.registrar_webhooks(httpx.Client(transport=httpx.MockTransport(atender)))

    assert resultado == {slug: True for slug in TOKENS}
    assert sorted(p["url"].rsplit("/", 1)[-1] for metodo, p in telegram.llamadas
                  if metodo == "setWebhook") == sorted(TOKENS)
    mundo = webhook["mundo"]
    with admin(conn) as cur:
        cur.execute("""select workspace_id, resumen_sanitizado from incident
                        where etapa = 'menu_del_bot'""")
        incidentes = {str(f["workspace_id"]): f["resumen_sanitizado"] for f in cur.fetchall()}
    conn.commit()
    assert set(incidentes) == {mundo["north-lab"]["id"], mundo["west-studio"]["id"]}
    assert "no se pudo hacer el pedido a Telegram" in incidentes[mundo["north-lab"]["id"]]
    assert "Telegram no lo aceptó" in incidentes[mundo["west-studio"]["id"]]
    assert all(token not in texto for token in TOKENS.values() for texto in incidentes.values())


def test_registrar_webhooks_se_niega_sin_direccion_o_sin_secreto(monkeypatch):
    for falta in ({"base_url": ""}, {"webhook_secret": ""}):
        monkeypatch.setattr(entrada, "config", dataclasses.replace(
            config_mod.config, **{"base_url": "https://leda.example",
                                  "webhook_secret": SECRETO, **falta}))
        with pytest.raises(LookupError):
            entrada.registrar_webhooks(TelegramFalso().cliente())


def test_el_toque_de_entrar_en_la_compu_por_el_webhook_del_bot_de_administracion(webhook, conn):
    """R3-admin-callback-wiring-unproved: por el webhook, el toque de "Entrar en la compu" del
    bot de administración recibe su acuse (`answerCallbackQuery`) y aprueba el pedido."""
    import hashlib
    import secrets

    morgan = webhook["mundo"]["north-lab"]["people"]["Morgan Hale"]
    with admin(conn) as cur:
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                    (morgan["app_user_id"],))
    conn.commit()
    codigo, secreto = "compu_" + secrets.token_urlsafe(24), secrets.token_urlsafe(32)
    from leda.db import sin_espacio

    with sin_espacio(conn) as cur:
        cur.execute("""select pedir_entrada_por_qr('administracion', null, %s, %s, 'Chrome') as r""",
                    (hashlib.sha256(codigo.encode()).hexdigest(),
                     hashlib.sha256(secreto.encode()).hexdigest()))
        pedido = cur.fetchone()["r"]["pedido_id"]
    conn.commit()
    r = _post(webhook["cliente"], "admin",
              toque_de_telegram(4001, f"compu:{pedido}", morgan["telegram"], "cb-web"),
              entrada.secreto_del_bot("admin"))
    assert r.status_code == 200, r.text
    acuses = [p for metodo, p in webhook["telegram"].llamadas if metodo == "answerCallbackQuery"]
    assert acuses == [{"callback_query_id": "cb-web"}]
    with admin(conn) as cur:
        cur.execute("select estado from pedido_de_entrada where id = %s", (pedido,))
        assert cur.fetchone()["estado"] == "aprobado"
