"""El bot de administración da el enlace de una tarea a un administrador de plataforma (ADR 0019,
7b; porción 5 de la C-3; `leda.motor.administracion`).

El sombrero lo define el canal (constitución §2): el administrador pide el enlace por el bot de
administración, con un pedido cerrado (`/enlace <espacio> <palabras de la tarea>`), y nunca por
el del espacio, donde se lo trata sólo por su rol en ese espacio. Si coinciden varias tareas,
Leda las nombra y pregunta cuál; el enlace sale atado a su usuario de plataforma, y en la base
queda sólo su hash.
"""

from __future__ import annotations

import dataclasses
import hashlib

import pytest

from leda import config as config_mod
from leda.db import admin
from leda.despachador import TransporteDePrueba
from leda.motor.administracion import atender_admin
from leda.motor.avisos import LLEVA_EL_ENLACE
from leda.motor.escucha import BotTelegram, Escucha
from leda.motor.ia import IAGuionada
from leda.motor.tiempo import RelojFijo

from tests.motor.ayudantes import AHORA, TelegramFalso, cuantas, mensaje_de_telegram, todos
from tests.motor.test_aprobacion import _nahuel, _tarea
from tests.motor.test_fichas import otro_espacio  # noqa: F401 -- la fixture del aislamiento
from tests.motor.test_pedir_enlace import _enlaces, _pide

DIRECCION = "https://leda.invalid/"
ADA = 79500


@pytest.fixture
def direccion(monkeypatch):
    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url=DIRECCION))


@pytest.fixture
def ada(conn, mundo) -> str:
    """Ada, administradora de plataforma, sin membresía en ningún espacio."""
    with admin(conn) as cur:
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (%s, 'Ada Admin') returning id""", (ADA,))
        usuario = str(cur.fetchone()["id"])
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                    (usuario,))
    conn.commit()
    return usuario


def _pedir(conn, texto: str, de: int = ADA, falla: bool = False) -> TransporteDePrueba:
    salida = TransporteDePrueba()
    if falla:
        salida.falla_en.add(de)
    atender_admin(conn, mensaje_de_telegram(1, texto, de), salida, imprimir=lambda *_: None)
    return salida


def _accesos(conn) -> list[dict]:
    return todos(conn, """select admin_app_user_id::text admin, membership_id, task_id::text tarea,
                                 workspace_id::text espacio
                            from acceso_tarea""")


def test_el_administrador_recibe_el_enlace_de_la_tarea_que_nombra(conn, mundo, ada, direccion):
    salida = _pedir(conn, "/enlace prueba tablero de marcos")
    [enviado] = salida.enviados
    assert enviado.chat_id == ADA
    assert enviado.sin_vista_previa
    assert "Revisar el tablero" in enviado.texto
    ultimo = enviado.texto.rsplit("\n", 1)[-1]
    assert ultimo.startswith(f"{DIRECCION}tarea/")
    assert _accesos(conn) == [{"admin": ada, "membership_id": None, "tarea": mundo["tarea"],
                               "espacio": mundo["id"]}]
    # En la base, sólo el hash: el token en claro está sólo en el mensaje.
    token = ultimo.rsplit("/", 1)[-1]
    [fila] = todos(conn, "select * from acceso_tarea")
    assert fila["token_hash"] == hashlib.sha256(token.encode()).hexdigest()
    assert all(token not in str(valor) for valor in fila.values())
    assert cuantas(conn, "audit_log", "accion = 'emitir_acceso_tarea_de_administrador'") == 1
    # Escribirle al bot de administración sigue dejando su chat para los avisos.
    assert cuantas(conn, "audit_log", "accion = 'mensaje_admin'") == 1


def test_si_coinciden_varias_las_nombra_y_pregunta_cual(conn, mundo, ada, direccion):
    _tarea(conn, mundo, titulo="Cablear el tablero")
    salida = _pedir(conn, "/enlace prueba tablero")
    [enviado] = salida.enviados
    assert "Revisar el tablero" in enviado.texto and "Cablear el tablero" in enviado.texto
    assert "¿Cuál?" in enviado.texto
    assert "leda.invalid" not in enviado.texto
    assert _accesos(conn) == []


def test_si_ninguna_se_llama_asi_lo_dice(conn, mundo, ada, direccion):
    [enviado] = _pedir(conn, "/enlace prueba bomba de agua").enviados
    assert "ninguna tarea" in enviado.texto
    assert _accesos(conn) == []


def test_un_espacio_que_no_existe_lo_dice(conn, mundo, ada, direccion):
    [enviado] = _pedir(conn, "/enlace nadaque tablero").enviados
    assert "nadaque" in enviado.texto and "espacio" in enviado.texto
    assert _accesos(conn) == []


def test_sin_palabras_explica_el_pedido(conn, mundo, ada, direccion):
    [enviado] = _pedir(conn, "/enlace").enviados
    assert "/enlace <espacio>" in enviado.texto
    assert _accesos(conn) == []


def test_otro_mensaje_no_tiene_respuesta(conn, mundo, ada, direccion):
    """No es un chat general de administración: sólo el pedido cerrado."""
    assert _pedir(conn, "hola, cómo va").enviados == []
    assert cuantas(conn, "audit_log", "accion = 'mensaje_admin'") == 1


def test_sin_la_direccion_publica_no_hay_enlace_y_lo_dice(conn, mundo, ada, monkeypatch):
    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url=""))
    [enviado] = _pedir(conn, "/enlace prueba tablero").enviados
    assert "no está disponible" in enviado.texto
    assert _accesos(conn) == []


def test_quien_no_es_administrador_no_recibe_nada(conn, mundo, direccion):
    """Marcos es del equipo, no de la plataforma: el bot de administración no le contesta."""
    salida = _pedir(conn, "/enlace prueba tablero", de=mundo["personas"]["Marcos"]["telegram"])
    assert salida.enviados == []
    assert _accesos(conn) == []
    assert cuantas(conn, "audit_log", "accion = 'mensaje_admin'") == 0


def test_una_tarea_de_otro_espacio_nunca_aparece(conn, mundo, ada, direccion, otro_espacio):
    [enviado] = _pedir(conn, "/enlace prueba tarea ajena").enviados
    assert "ninguna tarea" in enviado.texto
    [enviado] = _pedir(conn, "/enlace otro tarea ajena").enviados
    assert enviado.texto.rsplit("\n", 1)[-1].startswith(f"{DIRECCION}tarea/")
    assert [a["espacio"] for a in _accesos(conn)] == [otro_espacio["id"]]


def test_si_el_mensaje_no_sale_no_queda_ningun_acceso(conn, mundo, ada, direccion):
    """Un enlace que nunca llegó no queda vigente en la base, y la falla no queda en silencio."""
    salida = _pedir(conn, "/enlace prueba tablero", falla=True)
    assert salida.enviados == []
    assert _accesos(conn) == []
    assert cuantas(conn, "incident") == 1


def test_el_escuchador_atiende_el_pedido_por_el_bot_de_administracion(conn, mundo, ada,
                                                                      direccion):
    telegram, telegram_admin = TelegramFalso(), TelegramFalso()
    salida, salida_admin = TransporteDePrueba(), TransporteDePrueba()
    escucha = Escucha(conn, mundo["id"], IAGuionada(), RelojFijo(AHORA),
                      bot=BotTelegram("token-falso", telegram.cliente()), transporte=salida,
                      bot_admin=BotTelegram("token-admin-falso", telegram_admin.cliente()),
                      transporte_admin=salida_admin, imprimir=lambda *_: None)
    escucha.preparar()
    telegram_admin.lotes = [[mensaje_de_telegram(1, "/enlace prueba tablero", ADA)]]
    escucha.una_vuelta(espera=0)
    [enviado] = salida_admin.enviados
    assert enviado.texto.rsplit("\n", 1)[-1].startswith(f"{DIRECCION}tarea/")
    assert salida.enviados == []


# --- El sombrero lo define el canal --------------------------------------------------------

def test_por_el_bot_del_espacio_un_administrador_es_sólo_su_rol(conn, mundo, escribe,
                                                                direccion):
    """Nahuel es integrante del espacio y además administrador de plataforma: por el bot del
    espacio no ve la tarea de Marcos (no es suya, no la aprueba ni es el referente ni la
    autoridad final), así que recibe el resumen y ningún enlace."""
    _nahuel(conn, mundo)
    with admin(conn) as cur:
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                    (mundo["personas"]["Nahuel"]["app_user_id"],))
    conn.commit()
    hecho, _ = _pide(conn, escribe, "Nahuel", como_la_nombra="tablero de marcos")
    assert hecho["resultado"] == "solo_el_resumen"
    assert LLEVA_EL_ENLACE not in hecho
    assert _enlaces(conn) == []
    assert _accesos(conn) == []
