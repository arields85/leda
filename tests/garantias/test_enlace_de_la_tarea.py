"""El enlace a la página de una tarea en un mensaje (ADR 0019, decisiones 6 y 7a; migración 0036).

Lo que se prueba acá es la salida y el despachador, no la conversación:

- **El enlace no se guarda en claro en ningún lado.** La fila de la salida sólo dice que lleva
  el enlace de esta tarea para esta persona (`message_outbox_enlace`); el despachador lo emite
  al mandar, y la base guarda sólo su hash. El texto de la salida (que es el del registro de
  turnos) no lo lleva.
- **Sale sin vista previa**, para que Telegram no abra la página por su cuenta.
- **Nunca se inventa:** sin la dirección pública configurada, o si la persona ya no puede ver la
  tarea, el mensaje sale sin enlace (y lo segundo deja su incidente); un envío que falla no deja
  ningún acceso emitido.
"""

from __future__ import annotations

import dataclasses
import re
from datetime import datetime, timezone

import pytest

from leda import config as config_mod
from leda import pagina_de_tarea
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.despachador import TransporteDePrueba, TransporteTelegram, despachar
from leda.salida import PayloadValidationError, enqueue_outbox

from tests.garantias.test_pagina_de_la_tarea import (_persona, mundo,  # noqa: F401
                                                     sin_espacio)

AHORA = datetime(2026, 10, 22, 15, 0, tzinfo=timezone.utc)      # jueves, 12:00 en Buenos Aires
BASE = "https://leda.invalid"
ENLACE = re.compile(r"\n" + re.escape(BASE) + r"/tarea/([A-Za-z0-9_-]{43})$")


@pytest.fixture
def direccion(monkeypatch):
    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url=BASE + "/"))


def _encolar(conn, mundo, persona: str = "Taylor Quinn", *, clave: str = "aviso:1",
             texto: str = "Sam entregó **la balanza**.") -> str:
    ws = mundo["north-lab"]["id"]
    gente = mundo["north-lab"]["people"]
    with espacio(conn, ws) as cur:
        enqueue_outbox(cur, workspace_id=ws, chat_id=gente[persona]["telegram"], text=texto,
                       recipient_membership_id=_persona(mundo, persona), dedupe_key=clave,
                       es_coordinacion=True, scheduled_for=AHORA,
                       enlace_de_tarea=(mundo["norte"]["id"], _persona(mundo, persona)))
        cur.execute("select id from message_outbox where dedupe_key = %s", (clave,))
        fila = str(cur.fetchone()["id"])
    conn.commit()
    return fila


def _despachar(conn, mundo, transporte) -> dict:
    ws = mundo["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        r = despachar(cur, ws, transporte, Calendario.desde_base(cur, ws), AHORA)
    conn.commit()
    return r


def _filas(conn, sql: str, *args) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(sql, args)
        filas = cur.fetchall()
    conn.commit()
    return filas


def test_la_salida_guarda_la_marca_del_enlace_y_no_el_enlace(conn, mundo, direccion):
    fila = _encolar(conn, mundo)
    [marca] = _filas(conn, "select * from message_outbox_enlace")
    assert str(marca["outbox_id"]) == fila
    assert str(marca["task_id"]) == mundo["norte"]["id"]
    assert str(marca["membership_id"]) == _persona(mundo, "Taylor Quinn")
    [salida] = _filas(conn, "select cuerpo from message_outbox")
    assert "/tarea/" not in salida["cuerpo"] and BASE not in salida["cuerpo"]
    assert _filas(conn, "select * from acceso_tarea") == []     # se emite al mandar


def test_el_despachador_emite_el_enlace_al_mandar_y_sale_sin_vista_previa(conn, mundo,
                                                                          direccion):
    _encolar(conn, mundo)
    transporte = TransporteDePrueba()
    assert _despachar(conn, mundo, transporte)["enviados"] == 1
    [mensaje] = transporte.enviados
    encontrado = ENLACE.search(mensaje.texto)
    assert encontrado, mensaje.texto
    assert mensaje.texto.startswith("Sam entregó la balanza.")
    assert mensaje.sin_vista_previa is True
    token = encontrado.group(1)
    # Sólo el hash queda en la base; en ninguna fila de la salida ni del acceso está el token.
    [acceso] = _filas(conn, "select * from acceso_tarea")
    assert acceso["token_hash"] == pagina_de_tarea._hash(token)
    for tabla in ("acceso_tarea", "message_outbox", "message_outbox_enlace", "audit_log",
                  "incident"):
        for f in _filas(conn, f"select * from {tabla}"):
            assert token not in str(dict(f)), tabla
    # Y el enlace abre la página de esa tarea.
    with sin_espacio(conn) as cur:
        assert pagina_de_tarea.leer(cur, token)["tarea"]["titulo"] == "Calibrar la balanza"
    conn.commit()


def test_un_mensaje_sin_la_marca_sale_como_siempre(conn, mundo, direccion):
    ws = mundo["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        enqueue_outbox(cur, workspace_id=ws, chat_id=71001, text="Hola.",
                       recipient_membership_id=_persona(mundo, "Taylor Quinn"),
                       dedupe_key="sin-enlace", scheduled_for=AHORA)
    conn.commit()
    transporte = TransporteDePrueba()
    _despachar(conn, mundo, transporte)
    [mensaje] = transporte.enviados
    assert "/tarea/" not in mensaje.texto and mensaje.sin_vista_previa is False


def test_sin_direccion_publica_sale_sin_enlace_y_sin_emitir_nada(conn, mundo, monkeypatch):
    _encolar(conn, mundo)
    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url=""))
    transporte = TransporteDePrueba()
    assert _despachar(conn, mundo, transporte)["enviados"] == 1
    [mensaje] = transporte.enviados
    assert "/tarea/" not in mensaje.texto
    assert _filas(conn, "select * from acceso_tarea") == []


def test_si_la_persona_ya_no_puede_verla_sale_sin_enlace_y_deja_un_incidente(conn, mundo,
                                                                              direccion):
    _encolar(conn, mundo)
    with admin(conn) as cur:
        cur.execute("update membership set aprobador_membership_id = %s where id = %s",
                    (_persona(mundo, "Morgan Hale"), _persona(mundo, "Sam Noble")))
    conn.commit()
    transporte = TransporteDePrueba()
    assert _despachar(conn, mundo, transporte)["enviados"] == 1
    [mensaje] = transporte.enviados
    assert "/tarea/" not in mensaje.texto
    assert _filas(conn, "select * from acceso_tarea") == []
    [incidente] = _filas(conn, "select etapa from incident")
    assert incidente["etapa"] == "enlace_de_tarea"


def test_un_envio_que_falla_no_deja_un_acceso_emitido(conn, mundo, direccion):
    _encolar(conn, mundo)
    transporte = TransporteDePrueba(falla_en={mundo["north-lab"]["people"]["Taylor Quinn"]
                                              ["telegram"]})
    assert _despachar(conn, mundo, transporte)["fallidos"] == 1
    assert _filas(conn, "select * from acceso_tarea") == []


def test_repetir_el_encolado_no_duplica_la_marca(conn, mundo, direccion):
    _encolar(conn, mundo)
    _encolar(conn, mundo)
    assert len(_filas(conn, "select * from message_outbox_enlace")) == 1


def test_la_marca_no_va_con_adjuntos_ni_en_un_mensaje_partido(conn, mundo, direccion):
    ws = mundo["north-lab"]["id"]
    for extra in ({"adjuntos": [mundo["norte"]["piezas"]["foto"]]}, {"allow_split": True}):
        with espacio(conn, ws) as cur, pytest.raises(PayloadValidationError):
            enqueue_outbox(cur, workspace_id=ws, chat_id=71001, text="x", dedupe_key="x",
                           recipient_membership_id=_persona(mundo, "Taylor Quinn"),
                           enlace_de_tarea=(mundo["norte"]["id"],
                                            _persona(mundo, "Taylor Quinn")), **extra)
        conn.rollback()


def test_telegram_recibe_el_mensaje_con_la_vista_previa_desactivada():
    class Cliente:
        def __init__(self):
            self.cuerpos = []

        def post(self, url, json=None, **_):
            self.cuerpos.append(json)

            class R:
                status_code = 200

                def raise_for_status(self):
                    return None

                def json(self):
                    return {"ok": True, "result": {"message_id": 7}}
            return R()

    cliente = Cliente()
    transporte = TransporteTelegram("123:abc", cliente=cliente)
    transporte.enviar(1, f"Hola.\n{BASE}/tarea/x", sin_vista_previa=True)
    transporte.enviar(1, "Hola.")
    con, sin = cliente.cuerpos
    assert con["link_preview_options"] == {"is_disabled": True}
    assert "link_preview_options" not in sin


def test_el_enganche_de_la_cocina_da_la_marca_y_nunca_una_direccion(conn, mundo, monkeypatch):
    """`_enlace_portal_tarea` (ADR 0009, el pendiente del enlace): la marca `(tarea, persona)`
    que lleva la fila de la salida, sólo con la dirección pública y si la persona ve la tarea."""
    from leda import herramientas as H

    tarea = mundo["norte"]["id"]
    with espacio(conn, mundo["north-lab"]["id"]) as cur:
        assert H._enlace_portal_tarea(cur, tarea, _persona(mundo, "Taylor Quinn")) is None
        monkeypatch.setattr(config_mod, "config",
                            dataclasses.replace(config_mod.config, base_url=BASE))
        assert H._enlace_portal_tarea(cur, tarea, _persona(mundo, "Taylor Quinn")) == (
            tarea, _persona(mundo, "Taylor Quinn"))
        assert H._enlace_portal_tarea(cur, tarea, _persona(mundo, "Sam North")) is None
    conn.commit()
