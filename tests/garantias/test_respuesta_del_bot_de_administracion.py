"""La respuesta del bot de administración sale por la cola (`admin_notice`), y el enlace se emite
al mandarla (porción 5 de la C-3, su `PENDIENTE`; la corrección chica; migración 0054).

Hasta acá la respuesta al pedido `/enlace` salía directo, sin cola, porque la cola guarda el texto
y el token en claro no puede quedar en la base (ADR 0019, 7a). Ahora, como el enlace de una
persona del equipo (`message_outbox_enlace`), la respuesta queda en la cola sin el enlace, con una
marca de qué tarea y para qué administrador (`admin_notice_enlace`), y el despachador emite el
acceso recién al mandarla, dentro del punto de retorno del envío:

- **la base guarda sólo el hash**, nunca el token: ni en la cola, ni en la marca;
- **si el envío falla, no queda ningún acceso** (el punto de retorno se deshace) y queda un
  incidente; se reintenta como todo aviso a la administración, y al salir se emite uno solo;
- **el rol se revalida al mandarla**: si quien lo pidió dejó de ser administrador, no sale ningún
  enlace, la respuesta se descarta y queda un incidente;
- **la aplicación no llega a la cola ni a la marca** (sólo la conexión administrativa), y una
  fila de la cola es un incidente o una respuesta, nunca otra cosa;
- lo de la porción 5 sigue: la emisión auditada, sólo en un chat privado, una respuesta por
  pedido aunque Telegram lo entregue dos veces.
"""

from __future__ import annotations

import dataclasses
import hashlib

import psycopg
import pytest

from leda import config as config_mod
from leda.db import admin
from leda.despachador import TransporteDePrueba, despachar_avisos_admin
from leda.motor.administracion import atender_admin

from tests.garantias.test_pagina_de_la_tarea import mundo  # noqa: F401 -- la fixture
from tests.motor.ayudantes import mensaje_de_telegram

DIRECCION = "https://leda.invalid/"
ADA = 79001


@pytest.fixture
def ada(conn, mundo, monkeypatch) -> str:
    """Ada, administradora de plataforma, sin membresía; la página tiene su dirección."""
    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url=DIRECCION))
    with admin(conn) as cur:
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (%s, 'Ada Admin') returning id""", (ADA,))
        usuario = str(cur.fetchone()["id"])
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                    (usuario,))
    conn.commit()
    return usuario


def _pedir(conn, salida: TransporteDePrueba, update_id: int = 1,
           texto: str = "/enlace north-lab balanza") -> None:
    atender_admin(conn, mensaje_de_telegram(update_id, texto, ADA), salida,
                  imprimir=lambda *_: None)


def _filas(conn, sql: str, *args) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(sql, args)
        filas = cur.fetchall()
    conn.commit()
    return filas


def _accesos(conn) -> list[dict]:
    return _filas(conn, "select * from acceso_tarea where admin_app_user_id is not null")


def _respuestas(conn) -> list[dict]:
    return _filas(conn, "select * from admin_notice where es_respuesta order by id")


def _despachar(conn, salida: TransporteDePrueba, **mas) -> dict[str, int]:
    with admin(conn) as cur:
        r = despachar_avisos_admin(cur, salida, **mas)
    conn.commit()
    return r


def _el_token(texto: str) -> str:
    ultimo = texto.rsplit("\n", 1)[-1]
    assert ultimo.startswith(f"{DIRECCION}tarea/")
    return ultimo.rsplit("/", 1)[-1]


# --- La cola guarda la respuesta sin el enlace ----------------------------------------------------

def test_la_respuesta_pasa_por_la_cola_y_la_base_guarda_solo_el_hash(conn, mundo, ada):
    salida = TransporteDePrueba()
    _pedir(conn, salida)

    [enviado] = salida.enviados
    assert enviado.chat_id == ADA and enviado.sin_vista_previa
    token = _el_token(enviado.texto)
    [respuesta] = _respuestas(conn)
    assert respuesta["estado"] == "enviado" and respuesta["incident_id"] is None
    assert respuesta["chat_id"] == ADA
    assert str(respuesta["destinatario_app_user_id"]) == ada
    assert "Calibrar la balanza" in respuesta["cuerpo"]
    [marca] = _filas(conn, "select * from admin_notice_enlace")
    assert (str(marca["admin_notice_id"]), str(marca["task_id"]),
            str(marca["admin_app_user_id"]), str(marca["workspace_id"])) == (
        str(respuesta["id"]), mundo["norte"]["id"], ada, mundo["north-lab"]["id"])
    # El token en claro está sólo en el mensaje: en la base, el hash.
    [acceso] = _accesos(conn)
    assert acceso["token_hash"] == hashlib.sha256(token.encode()).hexdigest()
    for fila in (respuesta, marca, acceso):
        assert all(token not in str(valor) for valor in fila.values())
    assert len(_filas(conn, """select 1 from audit_log
                               where accion = 'emitir_acceso_tarea_de_administrador'""")) == 1


def test_una_respuesta_sin_enlace_tambien_pasa_por_la_cola(conn, mundo, ada):
    salida = TransporteDePrueba()
    _pedir(conn, salida, texto="/enlace north-lab")
    [enviado] = salida.enviados
    assert "/enlace <espacio>" in enviado.texto
    [respuesta] = _respuestas(conn)
    assert respuesta["estado"] == "enviado"
    assert _filas(conn, "select * from admin_notice_enlace") == []
    assert _accesos(conn) == []


def test_el_mismo_pedido_entregado_dos_veces_tiene_una_sola_respuesta(conn, mundo, ada):
    salida = TransporteDePrueba()
    _pedir(conn, salida, update_id=7)
    _pedir(conn, salida, update_id=7)
    assert len(salida.enviados) == 1
    assert len(_respuestas(conn)) == 1 and len(_accesos(conn)) == 1


# --- Si no sale, no queda ningún acceso -----------------------------------------------------------

def test_si_el_envio_falla_no_queda_ningun_acceso_y_al_reintentar_sale_uno(conn, mundo, ada):
    falla = TransporteDePrueba(falla_en={ADA})
    _pedir(conn, falla)
    assert falla.enviados == []
    assert _accesos(conn) == []
    [respuesta] = _respuestas(conn)
    assert (respuesta["estado"], respuesta["intentos"]) == ("listo", 1)
    [incidente] = _filas(conn, "select etapa, resumen_sanitizado, referencia_cruda from incident")
    assert incidente["etapa"] == "respuesta_del_bot_de_administracion"
    assert DIRECCION not in (incidente["referencia_cruda"] or "")

    anda = TransporteDePrueba()
    r = _despachar(conn, anda, ahora=respuesta["programado_para"])
    assert r["enviados"] == 1
    [enviado] = anda.enviados
    token = _el_token(enviado.texto)
    [acceso] = _accesos(conn)
    assert acceso["token_hash"] == hashlib.sha256(token.encode()).hexdigest()


def test_si_deja_de_ser_administrador_antes_de_salir_no_sale_ningun_enlace(conn, mundo, ada):
    falla = TransporteDePrueba(falla_en={ADA})
    _pedir(conn, falla)
    with admin(conn) as cur:
        cur.execute("delete from platform_role where app_user_id = %s", (ada,))
    conn.commit()
    [respuesta] = _respuestas(conn)

    anda = TransporteDePrueba()
    r = _despachar(conn, anda, ahora=respuesta["programado_para"])
    assert anda.enviados == [] and r["enviados"] == 0
    assert _accesos(conn) == []
    [respuesta] = _respuestas(conn)
    assert respuesta["estado"] == "descartado"
    etapas = [f["etapa"] for f in _filas(conn, "select etapa from incident order by at")]
    assert etapas == ["respuesta_del_bot_de_administracion"] * 2


def test_sin_la_direccion_publica_al_salir_no_sale_un_enlace_inventado(conn, mundo, ada,
                                                                       monkeypatch):
    falla = TransporteDePrueba(falla_en={ADA})
    _pedir(conn, falla)
    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url=""))
    [respuesta] = _respuestas(conn)
    anda = TransporteDePrueba()
    _despachar(conn, anda, ahora=respuesta["programado_para"])
    assert anda.enviados == [] and _accesos(conn) == []
    assert _respuestas(conn)[0]["estado"] == "descartado"


# --- La base ---------------------------------------------------------------------------------------

def test_la_aplicacion_no_llega_a_la_cola_ni_a_la_marca(conn):
    with admin(conn) as cur:
        for tabla in ("admin_notice", "admin_notice_enlace"):
            for privilegio in ("select", "insert", "update", "delete"):
                cur.execute("select has_table_privilege('leda_app', %s, %s) as puede",
                            (f"leda.{tabla}", privilegio))
                assert cur.fetchone()["puede"] is False, (tabla, privilegio)
    conn.commit()


def test_una_fila_de_la_cola_es_un_incidente_o_una_respuesta(conn, mundo, ada):
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            cur.execute("""insert into admin_notice (incident_id, es_respuesta,
                                                     destinatario_app_user_id, chat_id, cuerpo,
                                                     dedupe_key)
                           values (null, false, %s, %s, 'x', 'prueba:sin-incidente')""",
                        (ada, ADA))
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            cur.execute("""insert into admin_notice (incident_id, es_respuesta,
                                                     destinatario_app_user_id, chat_id, cuerpo,
                                                     dedupe_key)
                           values (gen_random_uuid(), true, %s, %s, 'x', 'prueba:las-dos')""",
                        (ada, ADA))
    conn.rollback()


def test_la_marca_del_enlace_es_de_una_tarea_de_su_espacio(conn, mundo, ada):
    """Como `message_outbox_enlace`: la tarea de la marca es del espacio que dice la marca."""
    with admin(conn) as cur:
        cur.execute("""insert into admin_notice (es_respuesta, workspace_id,
                                                 destinatario_app_user_id, chat_id, cuerpo,
                                                 dedupe_key)
                       values (true, %s, %s, %s, 'x', 'prueba:marca') returning id""",
                    (mundo["north-lab"]["id"], ada, ADA))
        aviso = cur.fetchone()["id"]
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            cur.execute("""insert into admin_notice_enlace (admin_notice_id, workspace_id,
                                                            task_id, admin_app_user_id)
                           values (%s, %s, %s, %s)""",
                        (aviso, mundo["west-studio"]["id"], mundo["norte"]["id"], ada))
    conn.rollback()
