"""Un envío que falla nunca queda en silencio (D8, G4; prueba por Telegram del 2026-10-08).

En la prueba, dos respuestas visibles no salieron en su primer intento (un tiempo de espera
agotado de Telegram y el álbum que el despacho inmediato no sabía mandar) y no quedó ningún
incidente: sólo el quinto intento fallido dejaba uno. Ahora cada intento fallido que se reintenta
deja su rastro, de severidad baja y sin avisar a la administración (como los avisos que la IA no
redactó, `2b4afbf`), con la falla saneada; el quinto sigue con su incidente y su aviso.

Telegram es de mentira (`TransporteDePrueba` con `falla_en`); nada sale a la red.
"""

from __future__ import annotations

from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.despachador import MAX_INTENTOS, TransporteDePrueba, despachar
from leda.incidentes import EXPLICACION_POR_ETAPA, ETAPA_ENTREGA_REINTENTO
from leda.salida import enqueue_outbox

from tests.motor.ayudantes import AHORA, administrador, cuantas, todos, uno


def _una_respuesta(conn, mundo, clave: str = "respuesta:1") -> int:
    chat = mundo["personas"]["Marcos"]["telegram"]
    with admin(conn) as cur:
        enqueue_outbox(cur, workspace_id=mundo["id"], chat_id=chat, text="Anoté que arrancaste.",
                       dedupe_key=clave,
                       recipient_membership_id=mundo["personas"]["Marcos"]["membership_id"],
                       is_response=True, scheduled_for=AHORA)
    conn.commit()
    return chat


def _despachar(conn, mundo, transporte) -> dict[str, int]:
    with espacio(conn, mundo["id"]) as cur:
        r = despachar(cur, mundo["id"], transporte, Calendario.desde_base(cur, mundo["id"]),
                      AHORA)
    conn.commit()
    return r


def test_cada_intento_fallido_de_una_respuesta_deja_su_rastro(conn, mundo):
    administrador(conn)
    chat = _una_respuesta(conn, mundo)
    transporte = TransporteDePrueba(falla_en={chat})

    assert _despachar(conn, mundo, transporte)["fallidos"] == 1

    [rastro] = todos(conn, "select * from incident")
    assert rastro["etapa"] == ETAPA_ENTREGA_REINTENTO and rastro["severidad"] == "baja"
    assert rastro["referencia_tipo"] == "message_outbox"
    fila = uno(conn, "select id, intentos, estado::text estado from message_outbox")
    assert str(rastro["referencia_id"]) == str(fila["id"])
    assert (fila["intentos"], fila["estado"]) == (1, "listo")
    assert "intento 1" in rastro["resumen_sanitizado"]
    # La falla, saneada, en la referencia técnica; sin avisar a la administración.
    assert "ConnectionError" in (rastro["referencia_cruda"] or "")
    assert rastro["notificado_admin_en"] is None
    assert cuantas(conn, "admin_notice") == 0


def test_el_quinto_intento_sigue_con_su_incidente_y_su_aviso(conn, mundo):
    administrador(conn)
    chat = _una_respuesta(conn, mundo)
    transporte = TransporteDePrueba(falla_en={chat})

    for _ in range(MAX_INTENTOS):
        with admin(conn) as cur:
            cur.execute("update message_outbox set programado_para = %s", (AHORA,))
        conn.commit()
        _despachar(conn, mundo, transporte)

    etapas = [f["etapa"] for f in todos(conn, "select etapa from incident order by at, etapa desc")]
    assert etapas == [ETAPA_ENTREGA_REINTENTO] * (MAX_INTENTOS - 1) + ["entrega_mensaje"]
    assert uno(conn, "select estado::text estado from message_outbox")["estado"] == "fallido"
    assert cuantas(conn, "admin_notice") == 1


def test_un_envio_que_sale_no_deja_ningun_rastro(conn, mundo):
    _una_respuesta(conn, mundo)

    assert _despachar(conn, mundo, TransporteDePrueba())["enviados"] == 1
    assert cuantas(conn, "incident") == 0


def test_la_explicacion_del_rastro_dice_que_puede_haber_llegado():
    """Una falla esperando la respuesta de Telegram puede querer decir que el mensaje llegó: el
    código no tiene cómo saberlo (`PENDIENTE` en `odd/tasks/fase-c.md`, D8), y la explicación
    lo dice para quien lo revise."""
    explicacion = EXPLICACION_POR_ETAPA[ETAPA_ENTREGA_REINTENTO]
    assert "puede" in explicacion.que_vio and "repite" in explicacion.que_vio
