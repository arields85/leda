"""El escuchador de la prueba chica (E2-3b).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Entrada propia") y sección 5 ("Ejecución
única"). Telegram es un transporte HTTP falso que contesta lo preparado; la IA, guionada; lo que
sale, `despachador.TransporteDePrueba`. Nada llega a Telegram ni a un proveedor de IA.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import httpx
import pytest

from prueba_chica.conftest import AHORA
from prueba_chica.escuchar import BotTelegram, Escucha
from prueba_chica.ia import IAGuionada, Jugada
from prueba_chica.tiempo import RelojFijo
from prueba_chica.turno import ETAPA_FUERA_DE_LA_LISTA, TEXTO_SI_LA_IA_FALLA

from leda.db import admin
from leda.despachador import TransporteDePrueba

ID_DEL_BOT = 7000
MARCOS = 81001


@dataclass
class TelegramFalso:
    """La API de un bot, de mentira: `getUpdates` entrega los lotes preparados, de a uno."""

    lotes: list[list[dict]] = field(default_factory=list)
    webhook: str = ""
    llamadas: list[tuple[str, dict]] = field(default_factory=list)

    def __call__(self, pedido: httpx.Request) -> httpx.Response:
        metodo = pedido.url.path.rsplit("/", 1)[-1]
        parametros = json.loads(pedido.content) if pedido.content else {}
        self.llamadas.append((metodo, parametros))
        if metodo == "getUpdates":      # sólo este pedido consume un lote
            resultado = self.lotes.pop(0) if self.lotes else []
        else:
            resultado = {
                "getMe": {"id": ID_DEL_BOT, "username": "leda_motor_bot"},
                "deleteWebhook": True,
                "getWebhookInfo": {"url": self.webhook},
                "answerCallbackQuery": True,
            }[metodo]
        return httpx.Response(200, json={"ok": True, "result": resultado})

    def metodos(self) -> list[str]:
        return [m for m, _ in self.llamadas]


def _mensaje(update_id: int, texto: str, de: int = MARCOS, message_id: int | None = None,
             tipo: str = "private") -> dict:
    return {"update_id": update_id, "message": {
        "message_id": message_id or update_id, "text": texto,
        "from": {"id": de, "first_name": "X"}, "chat": {"id": de, "type": tipo}}}


@dataclass
class Montaje:
    escucha: Escucha
    telegram: TelegramFalso
    telegram_admin: TelegramFalso
    salida: TransporteDePrueba
    salida_admin: TransporteDePrueba


def _montar(conn, mundo, ia, *, webhook_admin: str = "",
            imprimir=lambda *_: None) -> Montaje:
    telegram, telegram_admin = TelegramFalso(), TelegramFalso(webhook=webhook_admin)
    salida, salida_admin = TransporteDePrueba(), TransporteDePrueba()
    escucha = Escucha(
        conn, mundo["id"], ia, RelojFijo(AHORA),
        bot=BotTelegram("token-falso", httpx.Client(transport=httpx.MockTransport(telegram))),
        transporte=salida,
        bot_admin=BotTelegram("token-admin-falso",
                              httpx.Client(transport=httpx.MockTransport(telegram_admin))),
        transporte_admin=salida_admin, imprimir=imprimir)
    escucha.preparar()
    return Montaje(escucha, telegram, telegram_admin, salida, salida_admin)


def _uno(conn, sql: str, *params):
    with admin(conn) as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def _cuantas(conn, tabla: str, where: str = "true") -> int:
    return _uno(conn, f"select count(*) n from {tabla} where {where}")["n"]


# --- Preparar ---------------------------------------------------------------------------------

def test_preparar_saca_el_webhook_del_bot_del_equipo_y_aprende_su_id(conn, mundo):
    m = _montar(conn, mundo, IAGuionada())

    assert m.telegram.metodos() == ["getMe", "deleteWebhook"]
    assert m.escucha.bot_id == ID_DEL_BOT
    # Al bot de administración sólo se le pregunta: nunca se le saca un webhook.
    assert m.telegram_admin.metodos() == ["getWebhookInfo"]


def test_un_bot_de_administracion_con_webhook_no_se_sondea(conn, mundo):
    m = _montar(conn, mundo, IAGuionada(), webhook_admin="https://otro.invalid/hook")

    m.escucha.una_vuelta(espera=0)

    assert "getUpdates" not in m.telegram_admin.metodos()


# --- Un mensaje -------------------------------------------------------------------------------

def test_un_mensaje_se_guarda_una_vez_corre_su_turno_y_sale_la_respuesta(conn, mundo):
    ia = IAGuionada(jugadas=[[Jugada("anotar_inicio", {"tarea": "T1"})]],
                    redacciones=["Anoté que arrancaste Revisar el tablero."])
    m = _montar(conn, mundo, ia)
    actualizacion = _mensaje(500, "arranqué")
    m.telegram.lotes = [[actualizacion], [actualizacion]]    # Telegram lo entrega dos veces

    m.escucha.una_vuelta(espera=0)
    m.escucha.una_vuelta(espera=0)

    entrante = _uno(conn, "select * from inbound_message")
    assert entrante["telegram_bot_id"] == ID_DEL_BOT and entrante["telegram_message_id"] == 500
    assert entrante["texto"] == "arranqué" and entrante["chat_id"] == MARCOS
    assert str(entrante["app_user_id"]) == mundo["personas"]["Marcos"]["app_user_id"]
    assert _cuantas(conn, "inbound_message") == 1
    assert _cuantas(conn, "conversation_turn", "sentido = 'entrada'") == 1
    assert len(ia.pedidos_de_jugadas) == 1
    assert _uno(conn, "select estado::text e from task where id = %s",
                mundo["tarea"])["e"] == "en_curso"
    assert [(e.chat_id, e.texto) for e in m.salida.enviados] == [
        (MARCOS, "Anoté que arrancaste Revisar el tablero.")]
    # La segunda vez pidió desde el update siguiente.
    pedidos = [p for metodo, p in m.telegram.llamadas if metodo == "getUpdates"]
    assert pedidos[0]["offset"] == 0 and pedidos[1]["offset"] == 501


def test_un_mensaje_guardado_sin_turno_se_atiende_cuando_vuelve_a_llegar(conn, mundo):
    """Si el proceso se cortó después de guardar el mensaje y antes de su turno, Telegram lo
    vuelve a entregar: no se guarda de nuevo, pero se atiende."""
    with admin(conn) as cur:
        cur.execute("""insert into inbound_message (workspace_id, telegram_bot_id,
                                                    telegram_message_id, chat_id,
                                                    app_user_id, texto, at)
                       values (%s, %s, 600, %s, %s, 'arranqué', %s)""",
                    (mundo["id"], ID_DEL_BOT, MARCOS,
                     mundo["personas"]["Marcos"]["app_user_id"], AHORA))
    conn.commit()
    m = _montar(conn, mundo, IAGuionada(jugadas=[[]], redacciones=["Bien."]))
    m.telegram.lotes = [[_mensaje(600, "arranqué")]]

    m.escucha.una_vuelta(espera=0)

    assert _cuantas(conn, "inbound_message") == 1
    assert _cuantas(conn, "conversation_turn", "sentido = 'entrada'") == 1
    assert [e.texto for e in m.salida.enviados] == ["Bien."]


@pytest.mark.parametrize("actualizacion", [
    _mensaje(700, "hola", de=99999),                     # no es del equipo
    _mensaje(701, "hola", tipo="group"),                 # un grupo, no un privado
    {"update_id": 702, "edited_message": {"message_id": 9, "text": "x",
                                          "from": {"id": MARCOS}, "chat": {"id": MARCOS,
                                                                           "type": "private"}}},
    {"update_id": 703, "message": {"message_id": 10, "from": {"id": MARCOS},
                                   "chat": {"id": MARCOS, "type": "private"},
                                   "sticker": {}}},     # sin texto
])
def test_lo_que_no_es_un_mensaje_escrito_de_alguien_del_equipo_no_se_atiende(conn, mundo,
                                                                            actualizacion):
    ia = IAGuionada()
    m = _montar(conn, mundo, ia)
    m.telegram.lotes = [[actualizacion]]

    m.escucha.una_vuelta(espera=0)

    assert _cuantas(conn, "inbound_message") == 0 and ia.pedidos_de_jugadas == []
    assert m.salida.enviados == []


def test_si_el_turno_se_cae_queda_un_incidente_y_la_persona_recibe_el_texto_fijo(
        conn, mundo, monkeypatch):
    import prueba_chica.escuchar as escuchar

    def se_cae(*_, **__):
        raise RuntimeError("defecto")

    monkeypatch.setattr(escuchar, "procesar_turno", se_cae)
    m = _montar(conn, mundo, IAGuionada())
    m.telegram.lotes = [[_mensaje(800, "arranqué")]]

    m.escucha.una_vuelta(espera=0)

    incidente = _uno(conn, "select * from incident")
    entrante = _uno(conn, "select id from inbound_message")["id"]
    assert incidente["etapa"] == "turno_conversacion"
    assert incidente["referencia_id"] == entrante
    assert [e.texto for e in m.salida.enviados] == [TEXTO_SI_LA_IA_FALLA]


# --- Una falla al recibir no pierde el mensaje ni corta la escucha (revisión de la E2-3b) -----

def _falla_con(monkeypatch, metodo: str, message_ids: set[int], veces: int | None = None):
    """Hace fallar `Escucha.<metodo>` para esos mensajes, `veces` veces (o siempre), como una
    base que se cae en el medio."""
    import psycopg

    original = getattr(Escucha, metodo)
    fallas = {"n": 0}

    def falla(self, mensaje, *args, **kwargs):
        mid = mensaje["message_id"] if isinstance(mensaje, dict) else args[-1]
        if mid in message_ids and (veces is None or fallas["n"] < veces):
            fallas["n"] += 1
            raise psycopg.OperationalError("la base no contesta")
        return original(self, mensaje, *args, **kwargs)

    monkeypatch.setattr(Escucha, metodo, falla)
    return fallas


def test_una_falla_al_guardar_no_corta_la_escucha_y_el_mensaje_vuelve(conn, mundo, monkeypatch):
    """La falla deshace lo suyo, la escucha sigue y el mensaje no se pierde: el offset no pasa
    de él, así que Telegram lo vuelve a entregar y se atiende."""
    _falla_con(monkeypatch, "_guardar", {1100}, veces=1)
    ia = IAGuionada(jugadas=[[Jugada("anotar_inicio", {"tarea": "T1"})]],
                    redacciones=["Anotado."])
    m = _montar(conn, mundo, ia)
    m.telegram.lotes = [[_mensaje(1100, "arranqué")], [_mensaje(1100, "arranqué")]]

    m.escucha.una_vuelta(espera=0)          # no levanta: la escucha sigue
    m.escucha.una_vuelta(espera=0)

    pedidos = [p for metodo, p in m.telegram.llamadas if metodo == "getUpdates"]
    assert [p["offset"] for p in pedidos[:2]] == [0, 0]      # no pasó del que falló
    assert _cuantas(conn, "inbound_message") == 1
    assert _cuantas(conn, "conversation_turn", "sentido = 'entrada'") == 1
    assert [e.texto for e in m.salida.enviados] == ["Anotado."]
    assert m.escucha.offset == 1101


def test_un_mensaje_que_falla_siempre_queda_como_incidente_y_la_escucha_sigue(conn, mundo,
                                                                             monkeypatch):
    """Tras los intentos, nunca en silencio: un incidente, el texto fijo a la persona y el
    mensaje siguiente se atiende."""
    _falla_con(monkeypatch, "_guardar", {1200})
    ia = IAGuionada(jugadas=[[]], redacciones=["Bien."])
    m = _montar(conn, mundo, ia)
    atascado = _mensaje(1200, "arranqué")
    m.telegram.lotes = [[atascado, _mensaje(1201, "hola")] for _ in range(3)]

    for _ in range(3):
        m.escucha.una_vuelta(espera=0)

    incidente = _uno(conn, "select * from incident")
    assert incidente["etapa"] == "turno_conversacion" and incidente["severidad"] == "alta"
    assert incidente["chat_id"] == MARCOS
    assert _cuantas(conn, "incident") == 1
    # El atascado no se guardó; el siguiente sí, con su turno, en la tercera vuelta.
    assert _cuantas(conn, "inbound_message") == 1
    assert sorted(e.texto for e in m.salida.enviados) == sorted([TEXTO_SI_LA_IA_FALLA, "Bien."])
    assert m.escucha.offset == 1202


def test_una_falla_al_activar_no_corta_la_escucha(conn, mundo, monkeypatch):
    _falla_con(monkeypatch, "_activar", {1300})
    m = _montar(conn, mundo, IAGuionada())
    m.telegram.lotes = [[_mensaje(1300, "/start")] for _ in range(3)]

    for _ in range(3):
        m.escucha.una_vuelta(espera=0)

    assert _cuantas(conn, "incident") == 1
    assert m.escucha.offset == 1301


# --- Activación -------------------------------------------------------------------------------

def test_un_enlace_de_activacion_vincula_a_la_persona_y_le_da_la_bienvenida(conn, mundo):
    with admin(conn) as cur:
        cur.execute("""select area_id, rol_id from membership where id = %s""",
                    (mundo["personas"]["Marcos"]["membership_id"],))
        base = cur.fetchone()
        cur.execute("""insert into app_user (nombre) values ('Nora Sosa') returning id""")
        usuario = cur.fetchone()["id"]
        cur.execute("""insert into membership (workspace_id, app_user_id, area_id, rol_id)
                       values (%s, %s, %s, %s) returning id""",
                    (mundo["id"], usuario, base["area_id"], base["rol_id"]))
        membresia = cur.fetchone()["id"]
        cur.execute("""insert into activation_token (workspace_id, membership_id, token,
                                                     expira_en)
                       values (%s, %s, 'enlace-de-prueba', %s)""",
                    (mundo["id"], membresia, AHORA.replace(year=2027)))
        cur.execute("insert into greeting_state (membership_id, workspace_id, "
                    "ultima_fecha_local) values (%s, %s, '9999-12-31')",
                    (membresia, mundo["id"]))
    conn.commit()
    m = _montar(conn, mundo, IAGuionada())
    m.telegram.lotes = [[_mensaje(900, "/start enlace-de-prueba", de=83000)]]

    m.escucha.una_vuelta(espera=0)

    assert _uno(conn, "select telegram_user_id t from app_user where id = %s",
                usuario)["t"] == 83000
    [bienvenida] = m.salida.enviados
    assert bienvenida.chat_id == 83000 and bienvenida.texto.startswith("Listo, Nora.")


def test_start_de_alguien_ya_vinculado_le_da_la_bienvenida(conn, mundo):
    m = _montar(conn, mundo, IAGuionada())
    m.telegram.lotes = [[_mensaje(901, "/start")]]

    m.escucha.una_vuelta(espera=0)

    [bienvenida] = m.salida.enviados
    assert bienvenida.chat_id == MARCOS and bienvenida.texto.startswith("Listo, Marcos.")
    assert _cuantas(conn, "inbound_message") == 0


# --- El bot de administración -----------------------------------------------------------------

def test_el_administrador_se_registra_escribiendo_al_bot_y_le_llegan_los_avisos(conn, mundo):
    ismael = mundo["personas"]["Ismael"]
    with admin(conn) as cur:
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                    (ismael["app_user_id"],))
    conn.commit()
    ia = IAGuionada(jugadas=[[Jugada("recordar_algo_personal", {})]],
                    redacciones=["Eso no lo puedo hacer por acá."])
    m = _montar(conn, mundo, ia)
    m.telegram_admin.lotes = [[_mensaje(1, "hola", de=ismael["telegram"])]]

    m.escucha.una_vuelta(espera=0)
    registro = _uno(conn, "select * from audit_log where accion = 'mensaje_admin'")
    assert registro["detalle"] == {"chat_id": ismael["telegram"]}
    assert str(registro["actor_app_user_id"]) == ismael["app_user_id"]

    m.telegram.lotes = [[_mensaje(1000, "me recordás el turno del médico?")]]
    m.escucha.una_vuelta(espera=0)

    assert _uno(conn, "select etapa from incident")["etapa"] == ETAPA_FUERA_DE_LA_LISTA
    [aviso] = m.salida_admin.enviados
    assert aviso.chat_id == ismael["telegram"]
    assert aviso.texto.startswith("Leda recibió de Marcos un pedido que todavía no sabe hacer")


def test_alguien_que_no_es_administrador_no_se_registra(conn, mundo):
    m = _montar(conn, mundo, IAGuionada())
    m.telegram_admin.lotes = [[_mensaje(2, "hola")]]

    m.escucha.una_vuelta(espera=0)

    assert _cuantas(conn, "audit_log", "accion = 'mensaje_admin'") == 0


# --- Botones y toques (E2-4) ----------------------------------------------------------------
#
# Situaciones generales 5, 6 y 7: una duda sale con las tareas como botones, por el outbox (el
# `callback_data` es el token de la opción, nada más); un toque recibe su señal, corre el mismo
# turno que la elección escrita y no hace nada dos veces (ADR 0013, regla 4).

def _toque(update_id: int, data: str, de: int = MARCOS, callback_id: str | None = None) -> dict:
    return {"update_id": update_id, "callback_query": {
        "id": callback_id or f"cb{update_id}", "from": {"id": de, "first_name": "X"},
        "data": data,
        "message": {"message_id": 1, "chat": {"id": de, "type": "private"}}}}


def _con_dos_tareas(conn, mundo) -> str:
    from prueba_chica.test_situaciones import _tarea
    return _tarea(conn, mundo, "Probar las comunicaciones")


def test_una_duda_sale_con_las_tareas_como_botones(conn, mundo):
    _con_dos_tareas(conn, mundo)
    ia = IAGuionada(jugadas=[[Jugada("anotar_inicio", {})]], redacciones=["¿Cuál arrancaste?"])
    m = _montar(conn, mundo, ia)
    m.telegram.lotes = [[_mensaje(1400, "hoy arranque")]]

    m.escucha.una_vuelta(espera=0)

    [salida] = m.salida.enviados
    tokens = {o["orden"]: o["token"] for o in _todos(
        conn, "select orden, token from conversation_option")}
    assert [(b.etiqueta, b.callback_data) for b in salida.botones] == [
        ("Revisar el tablero", f"m:{tokens[1]}"),
        ("Probar las comunicaciones", f"m:{tokens[2]}")]
    pedidos = [p for metodo, p in m.telegram.llamadas if metodo == "getUpdates"]
    assert "callback_query" in pedidos[0]["allowed_updates"]


def test_un_toque_recibe_su_senal_corre_su_turno_y_no_se_repite(conn, mundo):
    t2 = _con_dos_tareas(conn, mundo)
    ia = IAGuionada(jugadas=[[Jugada("anotar_inicio", {})]],
                    redacciones=["¿Cuál arrancaste?", "Anotado."])
    m = _montar(conn, mundo, ia)
    m.telegram.lotes = [[_mensaje(1500, "hoy arranque")]]
    m.escucha.una_vuelta(espera=0)
    token = _uno(conn, "select token from conversation_option where orden = 2")["token"]

    m.telegram.lotes = [[_toque(1501, f"m:{token}")], [_toque(1502, f"m:{token}")]]
    m.escucha.una_vuelta(espera=0)
    m.escucha.una_vuelta(espera=0)          # el mismo botón, tocado otra vez

    senales = [p for metodo, p in m.telegram.llamadas if metodo == "answerCallbackQuery"]
    assert [s["callback_query_id"] for s in senales] == ["cb1501", "cb1502"]
    assert _uno(conn, "select estado::text e from task where id = %s", t2)["e"] == "en_curso"
    assert _cuantas(conn, "conversation_turn", "option_id is not null") == 1
    assert [e.texto for e in m.salida.enviados] == ["¿Cuál arrancaste?", "Anotado."]
    assert m.salida.enviados[1].botones == []       # la pregunta ya se cerró


def test_un_toque_que_falla_siempre_queda_como_incidente_y_la_persona_lo_sabe(conn, mundo,
                                                                             monkeypatch):
    """Revisión de la E2-4: un toque que no se puede recibir tras los intentos no se deja en
    silencio, igual que un mensaje: un incidente y el texto fijo a quien tocó."""
    import psycopg

    def falla(self, toque):
        raise psycopg.OperationalError("la base no contesta")

    monkeypatch.setattr(Escucha, "_toque", falla)
    m = _montar(conn, mundo, IAGuionada())
    m.telegram.lotes = [[_toque(1800, "m:token")] for _ in range(3)]

    for _ in range(3):
        m.escucha.una_vuelta(espera=0)

    incidente = _uno(conn, "select * from incident")
    assert incidente["etapa"] == "turno_conversacion" and incidente["severidad"] == "alta"
    assert incidente["chat_id"] == MARCOS and incidente["app_user_id"] is not None
    assert [e.texto for e in m.salida.enviados] == [TEXTO_SI_LA_IA_FALLA]
    assert m.escucha.offset == 1801


def test_un_toque_de_alguien_de_afuera_solo_recibe_la_senal(conn, mundo):
    _con_dos_tareas(conn, mundo)
    ia = IAGuionada(jugadas=[[Jugada("anotar_inicio", {})]], redacciones=["¿Cuál?"])
    m = _montar(conn, mundo, ia)
    m.telegram.lotes = [[_mensaje(1600, "hoy arranque")]]
    m.escucha.una_vuelta(espera=0)
    token = _uno(conn, "select token from conversation_option where orden = 1")["token"]

    m.telegram.lotes = [[_toque(1601, f"m:{token}", de=99999),
                         _toque(1602, "otra-cosa")]]
    m.escucha.una_vuelta(espera=0)

    assert m.telegram.metodos().count("answerCallbackQuery") == 2
    assert _cuantas(conn, "conversation_turn", "option_id is not null") == 0
    assert len(m.salida.enviados) == 1 and _cuantas(conn, "incident") == 0


def test_lo_que_leda_manda_por_su_cuenta_nunca_lleva_botones(conn, mundo):
    """Sin botones en los avisos (9b), aunque haya una duda abierta."""
    from leda.db import espacio
    from leda.salida import enqueue_outbox

    _con_dos_tareas(conn, mundo)
    ia = IAGuionada(jugadas=[[Jugada("anotar_inicio", {})]], redacciones=["¿Cuál?"])
    m = _montar(conn, mundo, ia)
    m.telegram.lotes = [[_mensaje(1700, "hoy arranque")]]
    m.escucha.una_vuelta(espera=0)
    with espacio(conn, mundo["id"]) as cur:
        enqueue_outbox(cur, workspace_id=mundo["id"], chat_id=MARCOS, text="Un aviso.",
                       dedupe_key="aviso-de-prueba", message_type="informativo",
                       recipient_membership_id=mundo["personas"]["Marcos"]["membership_id"],
                       scheduled_for=AHORA)
    conn.commit()

    m.escucha.una_vuelta(espera=0)

    assert [(e.texto, e.botones) for e in m.salida.enviados][1] == ("Un aviso.", [])


def _todos(conn, sql: str, *params) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(sql, params)
        return cur.fetchall()
