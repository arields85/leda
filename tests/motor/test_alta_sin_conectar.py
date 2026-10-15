"""Quien se dio de alta desde la web (J7-5, migración 0084) y todavía no abrió su enlace figura
«sin conectar»: Leda no le manda nada hasta entonces. Y el canje del enlace por el bot del equipo
(`motor.recibir`): busca el token por su huella y, si la cuenta de quien lo abre ya es de alguien de
otro espacio, la une a ella y lo deja en la auditoría.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta

from psycopg.types.json import Jsonb

from leda.db import admin, espacio
from leda.motor.ia import IAGuionada

from tests.motor.ayudantes import AHORA, cuantas, dice, enviar, jugada_prevision, todos, uno
from tests.motor.test_escucha import _mensaje, _montar

SALE = AHORA + timedelta(minutes=10)


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _sesion_de_ismael(conn, mundo) -> str:
    """Una sesión de la web de Ismael (Dirección del espacio de prueba), en claro."""
    enlace, sesion = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    with espacio(conn, mundo["id"]) as cur:
        cur.execute("select emitir_enlace_de_entrada(%s, %s, null)",
                    (mundo["personas"]["Ismael"]["membership_id"], _hash(enlace)))
    conn.commit()
    with conn.transaction(), conn.cursor() as cur:
        cur.execute("set local role leda_app")
        cur.execute("select canjear_enlace_de_entrada(%s, %s) as id",
                    (_hash(enlace), _hash(sesion)))
        assert cur.fetchone()["id"]
    conn.commit()
    return sesion


def _de_la_web(conn, sql: str, *args) -> dict:
    with conn.transaction(), conn.cursor() as cur:
        cur.execute("set local role leda_app")
        cur.execute(sql, args)
        r = cur.fetchone()["r"]
    conn.commit()
    return r


def _dar_de_alta(conn, mundo, sesion: str, nombre: str = "Lucas Pérez") -> str:
    rol = uno(conn, "select id from rol where workspace_id = %s and slug = 'integrante'",
              mundo["id"])["id"]
    datos = {"nombre": nombre, "area_id": mundo["area"], "rol_id": str(rol)}
    previa = _de_la_web(conn, "select vista_previa_de_alta('equipo', %s, null, 'alta', %s) as r",
                        _hash(sesion), Jsonb(datos))
    assert previa["ok"] is True, previa
    hecha = _de_la_web(conn, """select dar_de_alta('equipo', %s, null, %s, %s, %s, null, %s, %s)
                                   as r""",
                       _hash(sesion), nombre, mundo["area"], str(rol),
                       secrets.token_urlsafe(18), previa["huella"])
    assert hecha["ok"] is True, hecha
    persona = str(hecha["membership_id"])
    # Sin esto el despachador antepone el saludo del día (pack 06), como en `mundo`.
    with admin(conn) as cur:
        cur.execute("""insert into greeting_state (membership_id, workspace_id, ultima_fecha_local)
                       values (%s, %s, date '9999-12-31')""", (persona, mundo["id"]))
    conn.commit()
    return persona


def _emitir(conn, mundo, sesion: str, persona: str) -> str:
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, 'bot_usuario', to_jsonb('leda_prueba_bot'::text))
                       on conflict do nothing""", (mundo["id"],))
    conn.commit()
    token = secrets.token_urlsafe(24)
    r = _de_la_web(conn, "select emitir_enlace_de_activacion('equipo', %s, null, %s, %s) as r",
                   _hash(sesion), persona, _hash(token))
    assert r["ok"] is True, r
    return token


def test_a_quien_no_conecto_leda_no_le_manda_nada(conn, mundo, escribe):
    sesion = _sesion_de_ismael(conn, mundo)
    lucas = _dar_de_alta(conn, mundo, sesion)
    # Lucas pasa a aprobar el trabajo de Marcos (el cambio de quién aprueba es de la J7-7): el
    # aviso de la nueva fecha de Marcos es para él.
    with admin(conn) as cur:
        cur.execute("update membership set aprobador_membership_id = %s where id = %s",
                    (lucas, mundo["personas"]["Marcos"]["membership_id"]))
    conn.commit()
    dice(conn, escribe, jugada_prevision("T1", "2026-10-14", "el proveedor"))
    ia = IAGuionada(redacciones=["Aviso."])

    assert enviar(conn, mundo, ia, SALE) == {"omitido": 1}
    assert ia.pedidos_de_redaccion == []
    assert cuantas(conn, "message_outbox", "destinatario_membership_id = %s", lucas) == 0
    assert [a["motivo_omision"] for a in todos(
        conn, "select motivo_omision from scheduled_notice where destinatario_membership_id = %s",
        lucas)] == ["destinatario_sin_telegram"]


def test_el_enlace_de_la_web_se_canjea_por_el_bot_del_equipo(conn, mundo):
    sesion = _sesion_de_ismael(conn, mundo)
    lucas = _dar_de_alta(conn, mundo, sesion)
    token = _emitir(conn, mundo, sesion, lucas)
    m = _montar(conn, mundo, IAGuionada())
    m.telegram.lotes = [[_mensaje(950, f"/start {token}", de=83100)]]

    m.escucha.una_vuelta(espera=0)

    assert uno(conn, """select u.telegram_user_id t from membership m
                          join app_user u on u.id = m.app_user_id where m.id = %s""",
               lucas)["t"] == 83100
    [bienvenida] = m.salida.enviados
    assert bienvenida.chat_id == 83100 and bienvenida.texto.startswith("Listo, Lucas.")
    registro = uno(conn, "select detalle from audit_log where accion = 'activacion'")
    assert registro["detalle"]["cuenta_unida"] is False
    assert registro["detalle"]["membership_id"] == lucas


def test_quien_ya_esta_en_otro_espacio_queda_unido_por_el_bot(conn, mundo):
    """Nora trabaja en otro espacio y ahora también en este: abre el enlace y su membresía nueva
    queda unida a su cuenta. La auditoría lo dice sin nada del otro espacio."""
    with admin(conn) as cur:
        cur.execute("""insert into workspace (slug, nombre, zona_horaria, activo)
                       values ('otro', 'Otro', 'America/Argentina/Buenos_Aires', true)
                       returning id""")
        otro = str(cur.fetchone()["id"])
        cur.execute("insert into area (workspace_id, slug, nombre) values (%s, 'x', 'X') "
                    "returning id", (otro,))
        area = str(cur.fetchone()["id"])
        cur.execute("""insert into rol (workspace_id, slug, nombre, autoridad_final)
                       values (%s, 'lider', 'lider', true) returning id""", (otro,))
        rol = str(cur.fetchone()["id"])
        cur.execute("insert into app_user (telegram_user_id, nombre) values (83200, 'Nora Sosa') "
                    "returning id")
        nora = str(cur.fetchone()["id"])
        cur.execute("""insert into membership (workspace_id, app_user_id, nombre, area_id, rol_id)
                       values (%s, %s, (select nombre from app_user where id = %s), %s, %s) returning id""", (otro, nora, nora, area, rol))
        de_otro = str(cur.fetchone()["id"])
    conn.commit()
    sesion = _sesion_de_ismael(conn, mundo)
    nueva = _dar_de_alta(conn, mundo, sesion, nombre="Nora")
    token = _emitir(conn, mundo, sesion, nueva)
    m = _montar(conn, mundo, IAGuionada())
    m.telegram.lotes = [[_mensaje(951, f"/start {token}", de=83200)]]

    m.escucha.una_vuelta(espera=0)

    assert str(uno(conn, "select app_user_id from membership where id = %s",
                   nueva)["app_user_id"]) == nora
    assert cuantas(conn, "app_user", "telegram_user_id = 83200") == 1
    # Su membresía del otro espacio, intacta.
    assert str(uno(conn, "select workspace_id from membership where id = %s",
                   de_otro)["workspace_id"]) == otro
    [bienvenida] = m.salida.enviados
    assert bienvenida.chat_id == 83200 and bienvenida.texto.startswith("Listo, Nora.")
    registro = uno(conn, "select detalle from audit_log where accion = 'activacion'")
    assert registro["detalle"]["cuenta_unida"] is True
    assert otro not in str(registro["detalle"]) and de_otro not in str(registro["detalle"])
