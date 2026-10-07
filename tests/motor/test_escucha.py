"""El escuchador del motor (`leda.motor.escucha`; diseño probado en la Etapa 2, E2-3b).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Entrada propia") y sección 5 ("Ejecución
única"). Telegram es un transporte HTTP falso que contesta lo preparado; la IA, guionada; lo que
sale, `despachador.TransporteDePrueba`. Nada llega a Telegram ni a un proveedor de IA.

Portadas de `prueba_chica/test_escuchar.py` (E3-7). Lo que se hace con cada update vive en
`leda.motor.recibir`, que comparte con el webhook: la falla de un turno se simula ahí.
"""

from __future__ import annotations

import re
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from types import SimpleNamespace

import psycopg
import pytest

from leda.db import admin, espacio
from leda.despachador import TransporteDePrueba
from leda.motor import recibir
from leda.motor.escucha import BotTelegram, Escucha
from leda.motor.ia import IAGuionada, Jugada
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import ETAPA_FUERA_DE_LA_LISTA, TEXTO_SI_LA_IA_FALLA
from leda.salida import enqueue_outbox

from tests.motor.ayudantes import (AHORA, ID_DEL_BOT, TelegramFalso, cuantas,
                                   mensaje_de_telegram, nueva_tarea, todos, toque_de_telegram,
                                   uno)

MARCOS = 81001


def _mensaje(update_id: int, texto: str, de: int = MARCOS, message_id: int | None = None,
             tipo: str = "private") -> dict:
    return mensaje_de_telegram(update_id, texto, de, message_id, tipo)


def _toque(update_id: int, data: str, de: int = MARCOS) -> dict:
    return toque_de_telegram(update_id, data, de)


@dataclass
class Montaje:
    escucha: Escucha
    telegram: TelegramFalso
    telegram_admin: TelegramFalso
    salida: TransporteDePrueba
    salida_admin: TransporteDePrueba


def _montar(conn, mundo, ia, *, webhook_admin: str = "",
            imprimir=lambda *_: None, indicador=None) -> Montaje:
    telegram, telegram_admin = TelegramFalso(), TelegramFalso(webhook=webhook_admin)
    salida, salida_admin = TransporteDePrueba(), TransporteDePrueba()
    escucha = Escucha(
        conn, mundo["id"], ia, RelojFijo(AHORA),
        bot=BotTelegram("token-falso", telegram.cliente()),
        transporte=salida,
        bot_admin=BotTelegram("token-admin-falso", telegram_admin.cliente()),
        transporte_admin=salida_admin, imprimir=imprimir, indicador=indicador)
    escucha.preparar()
    return Montaje(escucha, telegram, telegram_admin, salida, salida_admin)


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

    entrante = uno(conn, "select * from inbound_message")
    assert entrante["telegram_bot_id"] == ID_DEL_BOT and entrante["telegram_message_id"] == 500
    assert entrante["texto"] == "arranqué" and entrante["chat_id"] == MARCOS
    assert str(entrante["app_user_id"]) == mundo["personas"]["Marcos"]["app_user_id"]
    assert cuantas(conn, "inbound_message") == 1
    assert cuantas(conn, "conversation_turn", "sentido = 'entrada'") == 1
    assert len(ia.pedidos_de_jugadas) == 1
    assert uno(conn, "select estado::text e from task where id = %s",
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

    assert cuantas(conn, "inbound_message") == 1
    assert cuantas(conn, "conversation_turn", "sentido = 'entrada'") == 1
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

    assert cuantas(conn, "inbound_message") == 0 and ia.pedidos_de_jugadas == []
    assert m.salida.enviados == []


def test_si_el_turno_se_cae_queda_un_incidente_y_la_persona_recibe_el_texto_fijo(
        conn, mundo, monkeypatch):
    import leda.motor.recibir as recibir

    def se_cae(*_, **__):
        raise RuntimeError("defecto")

    monkeypatch.setattr(recibir, "procesar_turno", se_cae)
    m = _montar(conn, mundo, IAGuionada())
    m.telegram.lotes = [[_mensaje(800, "arranqué")]]

    m.escucha.una_vuelta(espera=0)

    incidente = uno(conn, "select * from incident")
    entrante = uno(conn, "select id from inbound_message")["id"]
    assert incidente["etapa"] == "turno_conversacion"
    assert incidente["referencia_id"] == entrante
    assert [e.texto for e in m.salida.enviados] == [TEXTO_SI_LA_IA_FALLA]


# --- Una falla al recibir no pierde el mensaje ni corta la escucha (revisión de la E2-3b) -----

def _falla_con(monkeypatch, metodo: str, message_ids: set[int], veces: int | None = None):
    """Hace fallar `Escucha.<metodo>` para esos mensajes, `veces` veces (o siempre), como una
    base que se cae en el medio."""
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
    assert cuantas(conn, "inbound_message") == 1
    assert cuantas(conn, "conversation_turn", "sentido = 'entrada'") == 1
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

    incidente = uno(conn, "select * from incident")
    assert incidente["etapa"] == "turno_conversacion" and incidente["severidad"] == "alta"
    assert incidente["chat_id"] == MARCOS
    assert cuantas(conn, "incident") == 1
    # El atascado no se guardó; el siguiente sí, con su turno, en la tercera vuelta.
    assert cuantas(conn, "inbound_message") == 1
    assert sorted(e.texto for e in m.salida.enviados) == sorted([TEXTO_SI_LA_IA_FALLA, "Bien."])
    assert m.escucha.offset == 1202


def test_una_falla_al_activar_no_corta_la_escucha(conn, mundo, monkeypatch):
    _falla_con(monkeypatch, "_activar", {1300})
    m = _montar(conn, mundo, IAGuionada())
    m.telegram.lotes = [[_mensaje(1300, "/start")] for _ in range(3)]

    for _ in range(3):
        m.escucha.una_vuelta(espera=0)

    assert cuantas(conn, "incident") == 1
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

    assert uno(conn, "select telegram_user_id t from app_user where id = %s",
               usuario)["t"] == 83000
    [bienvenida] = m.salida.enviados
    assert bienvenida.chat_id == 83000 and bienvenida.texto.startswith("Listo, Nora.")


def test_start_de_alguien_ya_vinculado_le_da_la_bienvenida(conn, mundo):
    m = _montar(conn, mundo, IAGuionada())
    m.telegram.lotes = [[_mensaje(901, "/start")]]

    m.escucha.una_vuelta(espera=0)

    [bienvenida] = m.salida.enviados
    assert bienvenida.chat_id == MARCOS and bienvenida.texto.startswith("Listo, Marcos.")
    assert cuantas(conn, "inbound_message") == 0


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
    registro = uno(conn, "select * from audit_log where accion = 'mensaje_admin'")
    assert registro["detalle"] == {"chat_id": ismael["telegram"]}
    assert str(registro["actor_app_user_id"]) == ismael["app_user_id"]

    m.telegram.lotes = [[_mensaje(1000, "me recordás el turno del médico?")]]
    m.escucha.una_vuelta(espera=0)

    assert uno(conn, "select etapa from incident")["etapa"] == ETAPA_FUERA_DE_LA_LISTA
    [aviso] = m.salida_admin.enviados
    assert aviso.chat_id == ismael["telegram"]
    assert aviso.texto.startswith("Leda recibió de Marcos un pedido que todavía no sabe hacer")


def test_alguien_que_no_es_administrador_no_se_registra(conn, mundo):
    m = _montar(conn, mundo, IAGuionada())
    m.telegram_admin.lotes = [[_mensaje(2, "hola")]]

    m.escucha.una_vuelta(espera=0)

    assert cuantas(conn, "audit_log", "accion = 'mensaje_admin'") == 0


# --- Botones y toques (E2-4) ----------------------------------------------------------------
#
# Situaciones generales 5, 6 y 7: una duda sale con las tareas como botones, por el outbox (el
# `callback_data` es el token de la opción, nada más); un toque recibe su señal, corre el mismo
# turno que la elección escrita y no hace nada dos veces (ADR 0013, regla 4).

def test_una_duda_sale_con_las_tareas_como_botones(conn, mundo):
    nueva_tarea(conn, mundo, "Probar las comunicaciones")
    ia = IAGuionada(jugadas=[[Jugada("anotar_inicio", {})]], redacciones=["¿Cuál arrancaste?"])
    m = _montar(conn, mundo, ia)
    m.telegram.lotes = [[_mensaje(1400, "hoy arranque")]]

    m.escucha.una_vuelta(espera=0)

    [salida] = m.salida.enviados
    tokens = {o["orden"]: o["token"] for o in todos(
        conn, "select orden, token from conversation_option")}
    assert [(b.etiqueta, b.callback_data) for b in salida.botones] == [
        ("Revisar el tablero", f"m:{tokens[1]}"),
        ("Probar las comunicaciones", f"m:{tokens[2]}")]
    pedidos = [p for metodo, p in m.telegram.llamadas if metodo == "getUpdates"]
    assert "callback_query" in pedidos[0]["allowed_updates"]


def test_un_toque_recibe_su_senal_corre_su_turno_y_no_se_repite(conn, mundo):
    t2 = nueva_tarea(conn, mundo, "Probar las comunicaciones")
    ia = IAGuionada(jugadas=[[Jugada("anotar_inicio", {})]],
                    redacciones=["¿Cuál arrancaste?", "Anotado."])
    m = _montar(conn, mundo, ia)
    m.telegram.lotes = [[_mensaje(1500, "hoy arranque")]]
    m.escucha.una_vuelta(espera=0)
    token = uno(conn, "select token from conversation_option where orden = 2")["token"]

    m.telegram.lotes = [[_toque(1501, f"m:{token}")], [_toque(1502, f"m:{token}")]]
    m.escucha.una_vuelta(espera=0)
    m.escucha.una_vuelta(espera=0)          # el mismo botón, tocado otra vez

    senales = [p for metodo, p in m.telegram.llamadas if metodo == "answerCallbackQuery"]
    assert [s["callback_query_id"] for s in senales] == ["cb1501", "cb1502"]
    assert uno(conn, "select estado::text e from task where id = %s", t2)["e"] == "en_curso"
    assert cuantas(conn, "conversation_turn", "option_id is not null") == 1
    assert [e.texto for e in m.salida.enviados] == ["¿Cuál arrancaste?", "Anotado."]
    assert m.salida.enviados[1].botones == []       # la pregunta ya se cerró


def test_un_toque_que_falla_siempre_queda_como_incidente_y_la_persona_lo_sabe(conn, mundo,
                                                                             monkeypatch):
    """Revisión de la E2-4: un toque que no se puede recibir tras los intentos no se deja en
    silencio, igual que un mensaje: un incidente y el texto fijo a quien tocó."""

    def falla(self, toque):
        raise psycopg.OperationalError("la base no contesta")

    monkeypatch.setattr(Escucha, "_toque", falla)
    m = _montar(conn, mundo, IAGuionada())
    m.telegram.lotes = [[_toque(1800, "m:token")] for _ in range(3)]

    for _ in range(3):
        m.escucha.una_vuelta(espera=0)

    incidente = uno(conn, "select * from incident")
    assert incidente["etapa"] == "turno_conversacion" and incidente["severidad"] == "alta"
    assert incidente["chat_id"] == MARCOS and incidente["app_user_id"] is not None
    assert [e.texto for e in m.salida.enviados] == [TEXTO_SI_LA_IA_FALLA]
    assert m.escucha.offset == 1801


def test_un_toque_de_alguien_de_afuera_solo_recibe_la_senal(conn, mundo):
    nueva_tarea(conn, mundo, "Probar las comunicaciones")
    ia = IAGuionada(jugadas=[[Jugada("anotar_inicio", {})]], redacciones=["¿Cuál?"])
    m = _montar(conn, mundo, ia)
    m.telegram.lotes = [[_mensaje(1600, "hoy arranque")]]
    m.escucha.una_vuelta(espera=0)
    token = uno(conn, "select token from conversation_option where orden = 1")["token"]

    m.telegram.lotes = [[_toque(1601, f"m:{token}", de=99999),
                         _toque(1602, "otra-cosa")]]
    m.escucha.una_vuelta(espera=0)

    assert m.telegram.metodos().count("answerCallbackQuery") == 2
    assert cuantas(conn, "conversation_turn", "option_id is not null") == 0
    assert len(m.salida.enviados) == 1 and cuantas(conn, "incident") == 0


def test_lo_que_leda_manda_por_su_cuenta_nunca_lleva_botones(conn, mundo):
    """Sin botones en los avisos (9b), aunque haya una duda abierta."""
    nueva_tarea(conn, mundo, "Probar las comunicaciones")
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


# --- El indicador de actividad (pedido del usuario, 2026-10-07; ADR 0011, decisión 2) ---------

@dataclass
class IndicadorFalso:
    """El indicador de un turno, de mentira: guarda en qué chat se abrió, el texto que la
    redacción le fue pasando y cuántos mensajes habían salido cuando se apagó. `falla` hace que
    falle al abrirse o al cerrarse."""

    salida: TransporteDePrueba
    falla: str | None = None
    abiertos: list[int] = field(default_factory=list)
    textos: list[str] = field(default_factory=list)
    cerrados: list[tuple[int, int]] = field(default_factory=list)
    siguen: list[int] = field(default_factory=list)     # chats a los que les sigue un mensaje

    def __call__(self, chat_id: int):
        return self._abrir(chat_id)

    @contextmanager
    def _abrir(self, chat_id: int):
        if self.falla == "al_abrir":
            raise ConnectionError("el indicador no arranca")
        self.abiertos.append(chat_id)
        try:
            yield SimpleNamespace(admite_borrador=True, actualizar_borrador=self.textos.append,
                                  sigue_la_respuesta=lambda: self.siguen.append(chat_id))
        finally:
            self.cerrados.append((chat_id, len(self.salida.enviados)))
            if self.falla == "al_cerrar":
                raise ConnectionError("el indicador no se apaga")


def _con_indicador(conn, mundo, ia, **opciones) -> tuple[Montaje, IndicadorFalso]:
    salida_previa = TransporteDePrueba()
    indicador = IndicadorFalso(salida_previa, **opciones)
    m = _montar(conn, mundo, ia, indicador=indicador)
    indicador.salida = m.salida
    return m, indicador


def test_mientras_corre_el_turno_se_ve_el_indicador_y_se_apaga_antes_de_la_respuesta(conn,
                                                                                    mundo):
    ia = IAGuionada(jugadas=[[Jugada("anotar_inicio", {"tarea": "T1"})]],
                    redacciones=["Anoté que arrancaste Revisar el tablero."])
    m, indicador = _con_indicador(conn, mundo, ia)
    m.telegram.lotes = [[_mensaje(2000, "arranqué")]]

    m.escucha.una_vuelta(espera=0)

    assert indicador.abiertos == [MARCOS]
    # Se apagó con el turno, antes de que saliera la respuesta, avisado de que sigue un mensaje:
    # el mensaje reemplaza al borrador, sin retiro (pedido del usuario, 2026-10-07).
    assert indicador.cerrados == [(MARCOS, 0)]
    assert indicador.siguen == [MARCOS]
    # La redacción se vio en vivo; lo que sale es el texto del outbox.
    assert indicador.textos == ["Anoté que arrancaste Revisar el tablero."]
    assert [e.texto for e in m.salida.enviados] == ["Anoté que arrancaste Revisar el tablero."]


def test_la_respuesta_sale_apenas_termina_su_turno_sin_esperar_al_resto_del_lote(conn, mundo):
    """Despacho inmediato (ADR 0011, decisión 1): la respuesta no espera al siguiente mensaje
    del lote ni al resto de la vuelta."""
    ia = IAGuionada(jugadas=[[], []], redacciones=["Primera.", "Segunda."])
    m, indicador = _con_indicador(conn, mundo, ia)
    m.telegram.lotes = [[_mensaje(2100, "hola"), _mensaje(2101, "¿seguís?")]]

    m.escucha.una_vuelta(espera=0)

    # Cuando se apagó el indicador del segundo turno, la primera respuesta ya había salido.
    assert indicador.cerrados == [(MARCOS, 0), (MARCOS, 1)]
    assert [e.texto for e in m.salida.enviados] == ["Primera.", "Segunda."]


def test_si_la_ia_no_responde_el_indicador_se_apaga_y_sale_el_texto_fijo(conn, mundo):
    ia = IAGuionada(jugadas=[[]], redacciones=[TimeoutError("uno"), TimeoutError("dos")])
    m, indicador = _con_indicador(conn, mundo, ia)
    m.telegram.lotes = [[_mensaje(2200, "hola")]]

    m.escucha.una_vuelta(espera=0)

    assert indicador.cerrados == [(MARCOS, 0)]
    assert indicador.siguen == [MARCOS]
    assert [e.texto for e in m.salida.enviados] == [TEXTO_SI_LA_IA_FALLA]


def test_si_el_turno_se_cae_el_indicador_se_apaga_y_sale_el_texto_fijo(conn, mundo,
                                                                       monkeypatch):
    def se_cae(*_, **__):
        raise RuntimeError("se cayó el turno")

    monkeypatch.setattr(recibir, "procesar_turno", se_cae)
    m, indicador = _con_indicador(conn, mundo, IAGuionada())
    m.telegram.lotes = [[_mensaje(2300, "hola")]]

    m.escucha.una_vuelta(espera=0)

    assert indicador.cerrados == [(MARCOS, 0)]
    assert [e.texto for e in m.salida.enviados] == [TEXTO_SI_LA_IA_FALLA]


@pytest.mark.parametrize("falla", ["al_abrir", "al_cerrar"])
def test_un_indicador_que_falla_no_cambia_el_turno(conn, mundo, falla):
    ia = IAGuionada(jugadas=[[]], redacciones=["Hola, Marcos."])
    m, indicador = _con_indicador(conn, mundo, ia, falla=falla)
    m.telegram.lotes = [[_mensaje(2400, "hola")]]

    m.escucha.una_vuelta(espera=0)

    assert [e.texto for e in m.salida.enviados] == ["Hola, Marcos."]
    assert cuantas(conn, "incident") == 0
    assert m.escucha.offset == 2401


def test_un_toque_tambien_muestra_el_indicador(conn, mundo):
    nueva_tarea(conn, mundo, "Probar las comunicaciones")
    ia = IAGuionada(jugadas=[[Jugada("anotar_inicio", {})]],
                    redacciones=["¿Cuál arrancaste?", "Anotado."])
    m, indicador = _con_indicador(conn, mundo, ia)
    m.telegram.lotes = [[_mensaje(2500, "hoy arranque")]]
    m.escucha.una_vuelta(espera=0)
    token = uno(conn, "select token from conversation_option where orden = 2")["token"]

    m.telegram.lotes = [[_toque(2501, f"m:{token}")]]
    m.escucha.una_vuelta(espera=0)

    assert indicador.abiertos == [MARCOS, MARCOS]
    assert indicador.cerrados == [(MARCOS, 0), (MARCOS, 1)]
    assert indicador.textos == ["¿Cuál arrancaste?", "Anotado."]


def test_lo_que_leda_manda_por_su_cuenta_no_muestra_el_indicador(conn, mundo):
    """Ni los avisos ni la escalera: el indicador es sólo para responder a alguien."""
    m, indicador = _con_indicador(conn, mundo, IAGuionada())
    with espacio(conn, mundo["id"]) as cur:
        enqueue_outbox(cur, workspace_id=mundo["id"], chat_id=MARCOS, text="Un aviso.",
                       dedupe_key="aviso-sin-indicador", message_type="informativo",
                       recipient_membership_id=mundo["personas"]["Marcos"]["membership_id"],
                       scheduled_for=AHORA)
    conn.commit()

    m.escucha.una_vuelta(espera=0)

    assert [e.texto for e in m.salida.enviados] == ["Un aviso."]
    assert indicador.abiertos == []


def test_a_quien_no_es_del_equipo_no_se_le_muestra_el_indicador(conn, mundo):
    m, indicador = _con_indicador(conn, mundo, IAGuionada())
    m.telegram.lotes = [[_mensaje(2600, "hola", de=99999)]]

    m.escucha.una_vuelta(espera=0)

    assert indicador.abiertos == [] and m.salida.enviados == []


# --- El indicador no demora la respuesta (pedido del usuario, 2026-10-07) ----------------------
#
# "La función del escribiendo y el '…' es mostrar que Leda está activa, no generar demora en la
# respuesta." Con el indicador de verdad (`despachador.mantener_chat_activo`) y la salida de
# verdad (`despachador.TransporteTelegram`) sobre el mismo Telegram de mentira, que guarda cada
# llamada en orden: después de la redacción, lo próximo que llega a ese chat es el mensaje.

class IAQueEsperaSuBorrador(IAGuionada):
    """La IA guionada que, al terminar de redactar, espera (acotado) a que el borrador con su
    texto esté en vuelo, y anota cuándo terminó: así la prueba sabe que el cierre del turno
    encuentra un borrador todavía en vuelo."""

    def __init__(self, telegram, **guion) -> None:
        super().__init__(**guion)
        self.telegram = telegram
        self.termino: float | None = None

    def redactar(self, pedido, al_avanzar=None):
        texto = super().redactar(pedido, al_avanzar)
        if al_avanzar is not None and self.telegram.borrador_lento:
            self.telegram.borrador_en_vuelo.wait(1.0)
        self.termino = time.monotonic()
        return texto


def _con_indicador_de_verdad(conn, mundo, ia_de, *, borrador_lento: float = 0.0):
    """El escuchador con el indicador y la salida de verdad sobre un Telegram de mentira. El
    umbral es largo: sólo se ve el borrador con el texto que la IA redacta."""
    from leda.despachador import TransporteTelegram, mantener_chat_activo

    from tests.motor.test_indicador import TelegramDeMentira

    telegram = TelegramDeMentira(borrador_lento=borrador_lento)
    ia = ia_de(telegram)
    lineas: list[str] = []
    bot = TelegramFalso()
    escucha = Escucha(
        conn, mundo["id"], ia, RelojFijo(AHORA),
        bot=BotTelegram("token-falso", bot.cliente()),
        transporte=TransporteTelegram("token-falso", cliente=telegram),
        imprimir=lineas.append,
        indicador=lambda chat_id: mantener_chat_activo(
            "token-falso", chat_id, cliente=telegram, chat_type="private", umbral=10.0,
            intervalo=10.0, intervalo_borrador=0.0))
    escucha.preparar()
    return escucha, bot, telegram, ia, lineas


def _hilos_del_indicador() -> set:
    import threading
    return {h for h in threading.enumerate()
            if h.name in ("leda-typing", "leda-borrador") and h.is_alive()}


def _sin_hilos_nuevos(antes: set, timeout: float = 1.0) -> bool:
    limite = time.monotonic() + timeout
    while time.monotonic() < limite:
        if not (_hilos_del_indicador() - antes):
            return True
        time.sleep(0.01)
    return False


def test_despues_de_la_redaccion_lo_proximo_que_sale_es_la_respuesta(conn, mundo):
    escucha, bot, telegram, _, lineas = _con_indicador_de_verdad(
        conn, mundo, lambda _: IAGuionada(jugadas=[[Jugada("anotar_inicio", {"tarea": "T1"})]],
                                          redacciones=["Anoté que arrancaste."]))
    bot.lotes = [[_mensaje(2700, "arranqué")]]
    antes = _hilos_del_indicador()

    escucha.una_vuelta(espera=0)
    time.sleep(0.2)                 # un borrador tardío tendría tiempo de salir

    # A lo sumo el borrador con el texto (si llegó a salir antes del cierre) y la respuesta:
    # ni retiro (semilla silenciosa y su borrado), ni otro "escribiendo…", ni borradores después.
    metodos = telegram.metodos()
    assert metodos in (["sendMessage"], ["sendMessageDraft", "sendMessage"])
    [final] = [p for metodo, p in telegram.llamadas if metodo == "sendMessage"]
    assert final["chat_id"] == MARCOS and final["text"] == "Anoté que arrancaste."
    assert final["disable_notification"] is False
    # La línea de la consola: cuánto tardó la respuesta desde que el texto estuvo listo.
    [hora] = [linea for linea in lineas if "⏱" in linea]
    assert re.fullmatch(r"  ⏱ respuesta: texto listo → enviado en \d+ ms", hora)
    assert _sin_hilos_nuevos(antes)


def test_un_borrador_lento_no_demora_la_respuesta(conn, mundo):
    """Un borrador en vuelo que tarda 2 s en volver: la respuesta sale igual enseguida."""
    escucha, bot, telegram, ia, lineas = _con_indicador_de_verdad(
        conn, mundo, lambda telegram: IAQueEsperaSuBorrador(
            telegram, jugadas=[[]], redacciones=["Hola, Marcos."]), borrador_lento=2.0)
    bot.lotes = [[_mensaje(2800, "hola")]]
    try:
        escucha.una_vuelta(espera=0)
        enviado = telegram.horas[telegram.metodos().index("sendMessage")]

        assert ia.termino is not None and enviado - ia.termino < 1.0
        assert telegram.metodos() == ["sendMessageDraft", "sendMessage"]
    finally:
        telegram.soltar.set()


def test_el_texto_fijo_de_un_turno_caido_tambien_sale_sin_retiro(conn, mundo, monkeypatch):
    def se_cae(conn, quien, entrante, ia, reloj, *, al_avanzar=None):
        al_avanzar("Anoté que")
        time.sleep(0.1)
        raise RuntimeError("se cayó el turno")

    monkeypatch.setattr(recibir, "procesar_turno", se_cae)
    escucha, bot, telegram, _, _ = _con_indicador_de_verdad(conn, mundo,
                                                            lambda _: IAGuionada())
    bot.lotes = [[_mensaje(2900, "hola")]]
    antes = _hilos_del_indicador()

    escucha.una_vuelta(espera=0)

    assert telegram.metodos() == ["sendMessageDraft", "sendMessage"]
    assert telegram.llamadas[-1][1]["text"] == TEXTO_SI_LA_IA_FALLA
    assert _sin_hilos_nuevos(antes)


def test_un_mensaje_ya_respondido_retira_el_borrador_y_no_deja_hilos(conn, mundo):
    """Sin mensaje que siga (el mensaje ya tenía respuesta), el borrador se retira: es el único
    caso con retiro."""
    escucha, bot, telegram, _, _ = _con_indicador_de_verdad(
        conn, mundo, lambda _: IAGuionada(jugadas=[[]], redacciones=["Hola."]))
    bot.lotes = [[_mensaje(3000, "hola")]]
    escucha.una_vuelta(espera=0)
    escucha.indicador = lambda chat_id: _indicador_que_muestra_algo(telegram, chat_id)
    bot.lotes = [[_mensaje(3000, "hola")]]            # Telegram lo reentrega
    antes = _hilos_del_indicador()

    escucha.una_vuelta(espera=0)

    from leda.despachador import SEMILLA_INDICADOR

    assert telegram.metodos()[-3:] == ["sendMessage", "deleteMessage", "sendChatAction"]
    enviados = [p["text"] for metodo, p in telegram.llamadas if metodo == "sendMessage"]
    assert enviados == ["Hola.", SEMILLA_INDICADOR]
    assert _sin_hilos_nuevos(antes)


@contextmanager
def _indicador_que_muestra_algo(telegram, chat_id):
    """El indicador de verdad, que ya mostró los tres puntos y el "escribiendo…" cuando el
    turno empieza: así el turno que no deja mensaje tiene algo que retirar."""
    from leda.despachador import mantener_chat_activo
    with mantener_chat_activo("token-falso", chat_id, cliente=telegram, chat_type="private",
                              umbral=0.0, intervalo=10.0) as abierto:
        assert telegram.esperar(lambda: telegram.metodos()[-2:] == ["sendMessageDraft",
                                                                   "sendChatAction"])
        yield abierto
