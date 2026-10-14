""""Entrar en la compu" por Telegram (ADR 0024, decisiones 3 y 8; `leda.motor.bot_entrar`).

La computadora muestra un QR que abre el chat del bot de su puerta con `/start compu_<código>`:

- el bot del espacio le muestra a quien es del equipo en qué espacio y desde dónde se pidió, con
  el botón "Entrar en la compu"; a un desconocido no le contesta;
- al tocarlo, el pedido queda aprobado y ligado a quien tocó;
- el bot de administración hace lo mismo para su puerta, sólo con un administrador de plataforma,
  y a `/start` le contesta con el botón "Administración", que abre su Mini App.
"""

from __future__ import annotations

import dataclasses
import hashlib
import itertools
import secrets

import pytest

from leda import config as config_mod
from leda.db import admin, sin_espacio
from leda.despachador import TransporteDePrueba
from leda.motor.administracion import atender_admin
from leda.motor.ia import IAGuionada
from leda.motor.recibir import IntentosPorUpdate, Recepcion, recibir_update
from leda.motor.tiempo import RelojFijo

from tests.motor.ayudantes import AHORA, mensaje_de_telegram, todos, toque_de_telegram

ADA = 79600
_UPDATES = itertools.count(5000)


def _hash(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


@pytest.fixture
def direccion(monkeypatch):
    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url="https://leda.invalid/"))


@pytest.fixture
def ada(conn, mundo) -> str:
    with admin(conn) as cur:
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (%s, 'Ada Admin') returning id""", (ADA,))
        usuario = str(cur.fetchone()["id"])
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                    (usuario,))
    conn.commit()
    return usuario


def _pedido(conn, puerta: str = "equipo", slug: str | None = "prueba") -> tuple[str, str, str]:
    """Un pedido de entrada como lo pide la computadora: su id, su código y su secreto."""
    codigo, secreto = "compu_" + secrets.token_urlsafe(24), secrets.token_urlsafe(32)
    with sin_espacio(conn) as cur:
        cur.execute("""select pedir_entrada_por_qr(%s, %s, %s, %s,
                                                   'Chrome en Windows, IP 10.0.0.7') as r""",
                    (puerta, slug, _hash(codigo), _hash(secreto)))
        r = cur.fetchone()["r"]
    conn.commit()
    assert r["ok"], r
    return r["pedido_id"], codigo, secreto


def _al_bot_del_equipo(conn, mundo, update: dict) -> TransporteDePrueba:
    salida = TransporteDePrueba()
    recepcion = Recepcion(conn, mundo["id"], IAGuionada(jugadas=[], redacciones=[]),
                          RelojFijo(AHORA), bot_id=1, imprimir=lambda *_: None,
                          transporte=salida)
    assert recibir_update(recepcion, IntentosPorUpdate(), update)
    return salida


def _estado(conn, pedido: str) -> dict:
    [fila] = todos(conn, "select * from pedido_de_entrada where id = %s", pedido)
    return fila


def test_el_bot_del_equipo_muestra_el_pedido_y_el_boton(conn, mundo):
    pedido, codigo, _ = _pedido(conn)
    marcos = mundo["personas"]["Marcos"]["telegram"]
    salida = _al_bot_del_equipo(conn, mundo, mensaje_de_telegram(
        next(_UPDATES), f"/start {codigo}", marcos))
    [mensaje] = salida.enviados
    assert "Prueba" in mensaje.texto and "Chrome en Windows, IP 10.0.0.7" in mensaje.texto
    [boton] = mensaje.botones
    assert (boton.etiqueta, boton.callback_data) == ("Entrar en la compu", f"compu:{pedido}")
    # Mostrarlo no lo aprueba.
    assert _estado(conn, pedido)["estado"] == "pendiente"


def test_al_tocar_el_boton_queda_aprobado_por_quien_toco(conn, mundo):
    pedido, codigo, _ = _pedido(conn)
    marcos = mundo["personas"]["Marcos"]
    salida = _al_bot_del_equipo(conn, mundo, toque_de_telegram(
        next(_UPDATES), f"compu:{pedido}", marcos["telegram"]))
    [mensaje] = salida.enviados
    assert mensaje.texto.startswith("Listo")
    fila = _estado(conn, pedido)
    assert fila["estado"] == "aprobado"
    assert str(fila["aprobado_por_membership_id"]) == marcos["membership_id"]
    # Otro toque, ya aprobado.
    salida = _al_bot_del_equipo(conn, mundo, toque_de_telegram(
        next(_UPDATES), f"compu:{pedido}", marcos["telegram"]))
    assert salida.enviados[0].texto.startswith("Ya lo habías aprobado")


def test_a_un_desconocido_no_le_contesta_ni_le_aprueba(conn, mundo):
    pedido, codigo, _ = _pedido(conn)
    salida = _al_bot_del_equipo(conn, mundo, mensaje_de_telegram(
        next(_UPDATES), f"/start {codigo}", 999))
    assert salida.enviados == []
    salida = _al_bot_del_equipo(conn, mundo, toque_de_telegram(
        next(_UPDATES), f"compu:{pedido}", 999))
    assert salida.enviados == []
    assert _estado(conn, pedido)["estado"] == "pendiente"


def test_un_codigo_vencido_o_de_la_otra_puerta_ya_no_sirve(conn, mundo, ada):
    pedido, codigo, _ = _pedido(conn)
    with admin(conn) as cur:
        cur.execute("update pedido_de_entrada set vence_en = now() - interval '1 second'")
    conn.commit()
    marcos = mundo["personas"]["Marcos"]["telegram"]
    salida = _al_bot_del_equipo(conn, mundo, mensaje_de_telegram(
        next(_UPDATES), f"/start {codigo}", marcos))
    assert "ya no sirve" in salida.enviados[0].texto and salida.enviados[0].botones == []
    _p, codigo_admin, _s = _pedido(conn, "administracion", None)
    salida = _al_bot_del_equipo(conn, mundo, mensaje_de_telegram(
        next(_UPDATES), f"/start {codigo_admin}", marcos))
    assert "ya no sirve" in salida.enviados[0].texto


# --- El bot de administración -----------------------------------------------------------------

def _al_bot_de_administracion(conn, update: dict) -> tuple[TransporteDePrueba, list[str]]:
    salida, senales = TransporteDePrueba(), []
    atender_admin(conn, update, salida, imprimir=lambda *_: None, senal=senales.append)
    return salida, senales


def test_start_en_el_bot_de_administracion_trae_el_boton_de_la_administracion(conn, mundo, ada,
                                                                               direccion):
    salida, _ = _al_bot_de_administracion(conn, mensaje_de_telegram(next(_UPDATES), "/start",
                                                                    ADA))
    [mensaje] = salida.enviados
    [boton] = mensaje.botones
    assert (boton.etiqueta, boton.web_app) == ("Administración",
                                               "https://leda.invalid/app/abrir/admin/")


def test_el_qr_de_la_administracion_lo_aprueba_un_administrador(conn, mundo, ada):
    pedido, codigo, _ = _pedido(conn, "administracion", None)
    salida, _ = _al_bot_de_administracion(conn, mensaje_de_telegram(
        next(_UPDATES), f"/start {codigo}", ADA))
    [mensaje] = salida.enviados
    assert "administración" in mensaje.texto
    [boton] = mensaje.botones
    assert boton.callback_data == f"compu:{pedido}"
    salida, senales = _al_bot_de_administracion(conn, toque_de_telegram(
        next(_UPDATES), f"compu:{pedido}", ADA, callback_id="cb-ada"))
    assert senales == ["cb-ada"]
    assert salida.enviados[0].texto.startswith("Listo")
    fila = _estado(conn, pedido)
    assert (fila["estado"], str(fila["aprobado_por_app_user_id"])) == ("aprobado", ada)


def test_quien_no_es_administrador_no_aprueba_por_el_bot_de_administracion(conn, mundo, ada):
    pedido, codigo, _ = _pedido(conn, "administracion", None)
    marcos = mundo["personas"]["Marcos"]["telegram"]
    salida, _ = _al_bot_de_administracion(conn, mensaje_de_telegram(
        next(_UPDATES), f"/start {codigo}", marcos))
    assert salida.enviados == []
    salida, _ = _al_bot_de_administracion(conn, toque_de_telegram(
        next(_UPDATES), f"compu:{pedido}", marcos))
    assert salida.enviados == []
    assert _estado(conn, pedido)["estado"] == "pendiente"


# --- La revisión de la MA (RDD) ----------------------------------------------------------------

def test_si_el_bot_de_administracion_no_puede_contestar_queda_un_incidente(conn, mundo, ada,
                                                                            monkeypatch):
    """R3-admin-failure-paths-untested: una falla al mostrar o aprobar un pedido por el bot de
    administración nunca queda en silencio: un incidente, sin caerse."""
    from leda.motor import bot_entrar

    def falla(*_a, **_k):
        raise RuntimeError("la base no contestó")

    pedido, codigo, _ = _pedido(conn, "administracion", None)
    monkeypatch.setattr(bot_entrar, "mostrar_en_la_administracion", falla)
    monkeypatch.setattr(bot_entrar, "aprobar_en_la_administracion", falla)
    salida, _ = _al_bot_de_administracion(conn, mensaje_de_telegram(
        next(_UPDATES), f"/start {codigo}", ADA))
    assert salida.enviados == []
    salida, senales = _al_bot_de_administracion(conn, toque_de_telegram(
        next(_UPDATES), f"compu:{pedido}", ADA, callback_id="cb-x"))
    assert salida.enviados == [] and senales == ["cb-x"]
    incidentes = todos(conn, "select etapa, resumen_sanitizado from incident")
    assert [i["etapa"] for i in incidentes] == ["bot_de_administracion"] * 2
    assert all("la base no contestó" not in i["resumen_sanitizado"] for i in incidentes)
    assert _estado(conn, pedido)["estado"] == "pendiente"


def test_el_boton_de_la_administracion_va_solo_con_la_direccion_y_en_un_chat_privado(
        monkeypatch):
    """R3-admin-button-untested."""
    import dataclasses

    from leda.despachador import _boton_de_la_administracion

    aviso = {"boton": "administracion", "chat_id": ADA, "pedido_de_entrada_id": None}
    assert _boton_de_la_administracion(aviso) is None                 # sin LEDA_BASE_URL
    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url="https://leda.invalid/"))
    boton = _boton_de_la_administracion(aviso)
    assert (boton.etiqueta, boton.web_app) == ("Administración", "https://leda.invalid/app/abrir/admin/")
    assert _boton_de_la_administracion({**aviso, "chat_id": -100123}) is None
    assert _boton_de_la_administracion({**aviso, "boton": None}) is None
