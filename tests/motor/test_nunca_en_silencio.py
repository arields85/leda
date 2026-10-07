"""Un mensaje cuyo turno murió no queda sin respuesta (E3-7; T9-H19e, ADR 0013 regla 2).

`leda.huerfanos` es la garantía de no fallar en silencio: un mensaje recibido
(`inbound_message`) que pasada la ventana del turno en curso no tiene ninguna respuesta recibe
el aviso neutro y deja un incidente. Corre en cada vuelta del ciclo del motor (`motor.ciclo`),
antes del despacho, así el aviso sale en la misma vuelta. Del lado de la entrada del motor
(`motor.recibir`):

- el mensaje se guarda con la hora de la base, que es con la que el barrido mide la ventana
  (el reloj de Leda puede estar adelantado días);
- el texto fijo de un turno que se cayó es la respuesta de ese mensaje: el barrido no manda
  otro aviso;
- el turno toma el mismo candado por mensaje que el barrido (`entrada.clave_de_candado_del_mensaje`)
  y no corre si el mensaje ya tiene respuesta: el aviso neutro y una respuesta tardía nunca
  salen los dos.

Reloj fijo, IA guionada, Telegram de mentira.
"""

from __future__ import annotations

from leda.db import admin
from leda.despachador import TransporteDePrueba
from leda.incidentes import ETAPA_MENSAJE_HUERFANO, NOTICIA_NEUTRA_INCIDENTE
from leda.motor.ciclo import Ciclo
from leda.motor.escucha import BotTelegram, Escucha
from leda.motor.ia import IAGuionada, Jugada
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import TEXTO_SI_LA_IA_FALLA

from tests.motor.ayudantes import (AHORA, ID_DEL_BOT, IAQueRedacta, Charla, TelegramFalso,
                                   cuantas, mensaje_de_telegram, todos, uno)

MARCOS = 81001


def _recibido(conn, mundo, minutos: int, message_id: int = 900) -> str:
    """Un mensaje de Marcos recibido hace `minutos`, por la hora de la base, sin turno."""
    with admin(conn) as cur:
        cur.execute("""insert into inbound_message (workspace_id, telegram_bot_id,
                                                    telegram_message_id, chat_id,
                                                    app_user_id, texto, at)
                       values (%s, %s, %s, %s, %s, 'arranqué',
                               now() - make_interval(mins => %s))
                       returning id""",
                    (mundo["id"], ID_DEL_BOT, message_id, MARCOS,
                     mundo["personas"]["Marcos"]["app_user_id"], minutos))
        entrante = str(cur.fetchone()["id"])
    conn.commit()
    return entrante


def _hace(conn, entrante: str, minutos: int) -> None:
    with admin(conn) as cur:
        cur.execute("update inbound_message set at = now() - make_interval(mins => %s) "
                    "where id = %s", (minutos, entrante))
    conn.commit()


def _ciclo(conn, mundo) -> tuple[Ciclo, TransporteDePrueba]:
    salida = TransporteDePrueba()
    return Ciclo(conn, mundo["id"], IAQueRedacta(), RelojFijo(AHORA), salida,
                 seguimiento=False, imprimir=lambda *_: None), salida


def _escucha(conn, mundo, ia) -> tuple[Escucha, TelegramFalso, TransporteDePrueba]:
    telegram, salida = TelegramFalso(), TransporteDePrueba()
    escucha = Escucha(conn, mundo["id"], ia, RelojFijo(AHORA),
                      bot=BotTelegram("token-falso", telegram.cliente()), transporte=salida,
                      imprimir=lambda *_: None)
    escucha.preparar()
    return escucha, telegram, salida


# --- El barrido, en el ciclo del motor -------------------------------------------------------

def test_un_mensaje_sin_respuesta_pasada_la_ventana_recibe_el_aviso_neutro(conn, mundo):
    entrante = _recibido(conn, mundo, minutos=11)
    ciclo, salida = _ciclo(conn, mundo)

    resultado = ciclo.vuelta()

    assert resultado["huerfanos"] == 1
    assert [(e.chat_id, e.texto) for e in salida.enviados] == [
        (MARCOS, NOTICIA_NEUTRA_INCIDENTE)]
    [incidente] = todos(conn, "select * from incident")
    assert incidente["etapa"] == ETAPA_MENSAJE_HUERFANO
    assert str(incidente["referencia_id"]) == entrante

    ciclo.vuelta()                          # una sola vez
    assert len(salida.enviados) == 1 and cuantas(conn, "incident") == 1


def test_un_mensaje_dentro_de_la_ventana_todavia_no_es_un_huerfano(conn, mundo):
    _recibido(conn, mundo, minutos=2)
    ciclo, salida = _ciclo(conn, mundo)

    ciclo.vuelta()

    assert salida.enviados == [] and cuantas(conn, "incident") == 0


def test_un_mensaje_con_su_respuesta_no_recibe_nada_mas(conn, mundo, escribe):
    Charla(conn, escribe).dice(Jugada("anotar_inicio", {"tarea": "T1"}), texto="arranqué")
    entrante = uno(conn, "select id from inbound_message")["id"]
    _hace(conn, str(entrante), 11)
    ciclo, salida = _ciclo(conn, mundo)

    ciclo.vuelta()

    assert NOTICIA_NEUTRA_INCIDENTE not in [e.texto for e in salida.enviados]
    assert cuantas(conn, "incident") == 0


# --- La entrada del motor --------------------------------------------------------------------

def test_el_mensaje_se_guarda_con_la_hora_de_la_base(conn, mundo):
    """El reloj de las pruebas está fijo el 5 de octubre; el barrido mide con `now()`."""
    escucha, telegram, _ = _escucha(conn, mundo, IAGuionada(jugadas=[[]], redacciones=["Bien."]))
    telegram.lotes = [[mensaje_de_telegram(500, "hola", MARCOS)]]

    escucha.una_vuelta(espera=0)

    assert uno(conn, "select now() - at < interval '1 minute' as reciente "
                     "from inbound_message")["reciente"]


def test_el_texto_fijo_de_un_turno_caido_es_su_respuesta(conn, mundo, monkeypatch):
    import leda.motor.recibir as recibir

    def se_cae(*_, **__):
        raise RuntimeError("defecto")

    monkeypatch.setattr(recibir, "procesar_turno", se_cae)
    escucha, telegram, salida = _escucha(conn, mundo, IAGuionada())
    telegram.lotes = [[mensaje_de_telegram(600, "arranqué", MARCOS)]]
    escucha.una_vuelta(espera=0)
    _hace(conn, str(uno(conn, "select id from inbound_message")["id"]), 11)

    escucha.una_vuelta(espera=0)

    assert [e.texto for e in salida.enviados] == [TEXTO_SI_LA_IA_FALLA]
    assert cuantas(conn, "incident") == 1           # el del turno caído, nada más


def test_un_mensaje_que_ya_recibio_el_aviso_no_corre_su_turno_al_volver_a_llegar(conn, mundo):
    ia = IAGuionada(jugadas=[[]], redacciones=["Tarde."])
    _recibido(conn, mundo, minutos=11, message_id=700)
    escucha, telegram, salida = _escucha(conn, mundo, ia)
    escucha.una_vuelta(espera=0)                    # el barrido manda el aviso neutro

    telegram.lotes = [[mensaje_de_telegram(700, "arranqué", MARCOS)]]
    escucha.una_vuelta(espera=0)                    # Telegram lo reentrega

    assert ia.pedidos_de_jugadas == []
    assert [e.texto for e in salida.enviados] == [NOTICIA_NEUTRA_INCIDENTE]
    assert cuantas(conn, "conversation_turn") == 0
