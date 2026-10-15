"""Entrar a la web con Telegram (ADR 0024; unidad MA; migración 0073): la capa de garantías, en la
base y en la entrada HTTP.

- **La firma de Telegram se comprueba en el servidor** con el token del bot de esa puerta: una
  firma de otro bot, alterada, vencida o repetida no abre nada; el bot de un espacio no abre otro
  espacio; la puerta de administración, sólo con el bot de administración.
- **La sesión es de la membresía activa** del espacio del bot que firmó (o del rol de plataforma),
  por `app_user.telegram_user_id`; queda auditada con su origen, y se corta igual que siempre (la
  baja, "perdí el celular", la administración).
- **El QR** sirve una vez, vence a los 5 minutos, lo aprueba sólo quien toca "Entrar en la compu"
  en el bot de esa puerta, y lo canjea sólo la computadora que lo pidió (su secreto).
- **La sesión de la computadora** dura lo que eligió la administración para el espacio, o no vence.
- Nunca quedan en la base ni en la auditoría `initData`, la firma ni los tokens.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import secrets
import time
from urllib.parse import urlencode

import pytest

from leda.db import admin, espacio, sin_espacio

TOKEN_NORTE = "111111:token-del-bot-de-north-lab"
TOKEN_OESTE = "222222:token-del-bot-de-west-studio"
TOKEN_ADMIN = "333333:token-del-bot-de-administracion"
BASE = "https://testserver"


# --- Ayudas ---------------------------------------------------------------------------------

def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def firmar(token: str, telegram_user_id: int, *, auth_date: int | None = None,
           extra: dict | None = None) -> str:
    """`initData` como la arma Telegram, firmada con el token de ese bot."""
    campos = {"query_id": "AAH" + secrets.token_hex(6),
              "user": json.dumps({"id": telegram_user_id, "first_name": "Prueba"},
                                 separators=(",", ":")),
              "auth_date": str(int(time.time()) if auth_date is None else auth_date)}
    campos.update(extra or {})
    a_revisar = "\n".join(f"{k}={campos[k]}" for k in sorted(campos))
    secreto = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    campos["hash"] = hmac.new(secreto, a_revisar.encode(), hashlib.sha256).hexdigest()
    return urlencode(campos)


def _tg(mundo: dict, nombre: str, slug: str = "north-lab") -> int:
    return mundo[slug]["people"][nombre]["telegram"]


def _membresia(mundo: dict, nombre: str, slug: str = "north-lab") -> str:
    return mundo[slug]["people"][nombre]["membership_id"]


def _otorgar(conn, app_user_id: str) -> None:
    with admin(conn) as cur:
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                    (app_user_id,))
    conn.commit()


@pytest.fixture
def bots(monkeypatch):
    monkeypatch.setenv("LEDA_BOT_TOKEN_NORTH-LAB", TOKEN_NORTE)
    monkeypatch.setenv("LEDA_BOT_TOKEN_WEST-STUDIO", TOKEN_OESTE)
    monkeypatch.setenv("LEDA_BOT_TOKEN_ADMIN", TOKEN_ADMIN)
    monkeypatch.setenv("LEDA_BOT_USUARIO_ADMIN", "Leda_Admin_bot")


def _abrir(conn, slug: str, telegram_user_id: int, huella: str | None = None) -> dict:
    """La función de la base, como la llama la web después de validar la firma."""
    with sin_espacio(conn) as cur:
        cur.execute("""select abrir_sesion_por_telegram(%s, %s, %s, now() + interval '10 minutes',
                                                        %s) as r""",
                    (slug, telegram_user_id, huella or secrets.token_hex(32),
                     _hash(secrets.token_urlsafe(32))))
        r = cur.fetchone()["r"]
    conn.commit()
    return r


# --- La base ------------------------------------------------------------------------------------

def test_leda_app_no_tiene_privilegios_sobre_las_tablas_nuevas(conn, intake_world):
    with admin(conn) as cur:
        for tabla in ("firma_de_telegram", "pedido_de_entrada"):
            for privilegio in ("select", "insert", "update", "delete"):
                cur.execute("select has_table_privilege('leda_app', %s, %s) as si",
                            (f"leda.{tabla}", privilegio))
                assert cur.fetchone()["si"] is False, (tabla, privilegio)
        cur.execute("""select has_function_privilege('leda_app',
                         'leda.gastar_firma_de_telegram(text, text, timestamptz)', 'execute')
                         as si""")
        assert cur.fetchone()["si"] is False


def test_la_sesion_es_de_la_membresia_activa_del_espacio_del_bot(conn, intake_world):
    r = _abrir(conn, "north-lab", _tg(intake_world, "Sam North"))
    assert r["ok"] is True
    with admin(conn) as cur:
        cur.execute("select * from sesion_web where id = %s", (r["sesion_id"],))
        sesion = cur.fetchone()
        assert (str(sesion["membership_id"]), sesion["origen"], sesion["enlace_id"]) == (
            _membresia(intake_world, "Sam North"), "mini_app", None)
        cur.execute("""select actor_app_user_id, accion, detalle from audit_log
                        where sujeto_id = %s""", (r["sesion_id"],))
        [auditoria] = cur.fetchall()
    assert auditoria["accion"] == "abrir_sesion_web"
    assert auditoria["detalle"] == {"origen": "mini_app",
                                    "membership_id": _membresia(intake_world, "Sam North")}


def test_el_bot_de_un_espacio_no_abre_otro_espacio(conn, intake_world):
    """Sam North de West Studio no es de North Lab: con el bot de North Lab no entra."""
    assert _abrir(conn, "north-lab", _tg(intake_world, "Sam North", "west-studio")) == {
        "ok": False, "motivo": "sin_membresia"}
    assert _abrir(conn, "no-existe", _tg(intake_world, "Sam North")) == {
        "ok": False, "motivo": "sin_espacio"}


def test_una_membresia_inactiva_no_entra(conn, intake_world):
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (_membresia(intake_world, "Sam North"),))
    conn.commit()
    assert _abrir(conn, "north-lab", _tg(intake_world, "Sam North"))["motivo"] == "sin_membresia"


def test_cada_firma_sirve_una_sola_vez(conn, intake_world):
    huella = secrets.token_hex(32)
    assert _abrir(conn, "north-lab", _tg(intake_world, "Sam North"), huella)["ok"] is True
    assert _abrir(conn, "north-lab", _tg(intake_world, "Sam North"), huella) == {
        "ok": False, "motivo": "firma_usada"}


def test_la_sesion_de_la_mini_app_vence_a_las_24_horas(conn, intake_world):
    sesion = secrets.token_urlsafe(32)
    with sin_espacio(conn) as cur:
        cur.execute("""select abrir_sesion_por_telegram('north-lab', %s, %s,
                                                        now() + interval '10 minutes', %s) as r""",
                    (_tg(intake_world, "Sam North"), secrets.token_hex(32), _hash(sesion)))
        sesion_id = cur.fetchone()["r"]["sesion_id"]
        cur.execute("select * from sesion_vigente(%s)", (_hash(sesion),))
        assert cur.fetchone() is not None
    with admin(conn) as cur:
        cur.execute("update sesion_web set creada_en = now() - interval '25 hours' where id = %s",
                    (sesion_id,))
    with sin_espacio(conn) as cur:
        cur.execute("select * from sesion_vigente(%s)", (_hash(sesion),))
        assert cur.fetchone() is None
    with admin(conn) as cur:
        cur.execute("select motivo_de_corte from sesion_web where id = %s", (sesion_id,))
        assert cur.fetchone()["motivo_de_corte"] == "vencio"


def test_la_puerta_de_administracion_pide_el_rol_de_plataforma(conn, intake_world):
    def abrir(telegram_user_id):
        with sin_espacio(conn) as cur:
            cur.execute("""select abrir_sesion_de_administracion_por_telegram(
                             %s, %s, now() + interval '10 minutes', %s) as r""",
                        (telegram_user_id, secrets.token_hex(32),
                         _hash(secrets.token_urlsafe(32))))
            r = cur.fetchone()["r"]
        conn.commit()
        return r

    morgan = intake_world["north-lab"]["people"]["Morgan Hale"]
    assert abrir(morgan["telegram"]) == {"ok": False, "motivo": "sin_rol"}
    _otorgar(conn, morgan["app_user_id"])
    r = abrir(morgan["telegram"])
    assert r["ok"] is True
    with admin(conn) as cur:
        cur.execute("select origen, app_user_id from sesion_de_administracion where id = %s",
                    (r["sesion_id"],))
        fila = cur.fetchone()
        assert (fila["origen"], str(fila["app_user_id"])) == ("mini_app", morgan["app_user_id"])


# --- El QR, en la base ----------------------------------------------------------------------------

def _pedir(conn, puerta="equipo", slug="north-lab"):
    codigo, secreto = "compu_" + secrets.token_urlsafe(24), secrets.token_urlsafe(32)
    with sin_espacio(conn) as cur:
        cur.execute("select pedir_entrada_por_qr(%s, %s, %s, %s, 'Chrome en Windows') as r",
                    (puerta, slug, _hash(codigo), _hash(secreto)))
        r = cur.fetchone()["r"]
    conn.commit()
    return r, codigo, secreto


def _aprobar(conn, pedido_id, telegram_user_id, puerta="equipo", slug="north-lab"):
    with espacio(conn, "00000000-0000-0000-0000-000000000000") as cur:
        cur.execute("select aprobar_pedido_de_entrada(%s, %s, %s, %s) as r",
                    (pedido_id, puerta, slug, telegram_user_id))
        r = cur.fetchone()["r"]
    conn.commit()
    return r


def _canjear(conn, pedido_id, secreto, puerta="equipo"):
    sesion = secrets.token_urlsafe(32)
    with sin_espacio(conn) as cur:
        cur.execute("select canjear_pedido_de_entrada(%s, %s, %s, %s) as r",
                    (pedido_id, puerta, _hash(secreto), _hash(sesion)))
        r = cur.fetchone()["r"]
    conn.commit()
    return r, sesion


def test_el_qr_lo_aprueba_quien_toca_y_lo_canjea_una_vez_la_computadora(conn, intake_world):
    r, codigo, secreto = _pedir(conn)
    pedido = r["pedido_id"]
    with sin_espacio(conn) as cur:
        cur.execute("select * from ver_pedido_de_entrada(%s, 'equipo', 'north-lab')",
                    (_hash(codigo),))
        visto = cur.fetchone()
        # Desde el bot de otro espacio, no se ve.
        cur.execute("select * from ver_pedido_de_entrada(%s, 'equipo', 'west-studio')",
                    (_hash(codigo),))
        assert cur.fetchone() is None
    conn.commit()
    assert (visto["espacio"], visto["desde"]) == ("North Lab", "Chrome en Windows")
    assert _canjear(conn, pedido, secreto)[0] == {"estado": "pendiente"}
    # Alguien de otro espacio, o por el bot de otro espacio, no lo aprueba.
    assert _aprobar(conn, pedido, _tg(intake_world, "Sam North", "west-studio"))["motivo"] == \
        "sin_membresia"
    assert _aprobar(conn, pedido, _tg(intake_world, "Sam North"), slug="west-studio")["motivo"] \
        == "no_esta"
    assert _aprobar(conn, pedido, _tg(intake_world, "Sam North"))["ok"] is True
    assert _aprobar(conn, pedido, _tg(intake_world, "Taylor Quinn"))["motivo"] == "ya_aprobado"
    # Otra computadora (otro secreto) no lo canjea.
    assert _canjear(conn, pedido, secrets.token_urlsafe(32))[0] == {"estado": "no_esta"}
    resultado, sesion = _canjear(conn, pedido, secreto)
    assert resultado["estado"] == "adentro"
    assert _canjear(conn, pedido, secreto)[0] == {"estado": "no_esta"}
    with sin_espacio(conn) as cur:
        cur.execute("select membership_id from sesion_vigente(%s)", (_hash(sesion),))
        assert str(cur.fetchone()["membership_id"]) == _membresia(intake_world, "Sam North")
    with admin(conn) as cur:
        cur.execute("select origen from sesion_web where id = %s", (resultado["sesion_id"],))
        assert cur.fetchone()["origen"] == "qr"
        cur.execute("""select accion, detalle from audit_log
                        where sujeto_id in (%s, %s) order by at""", (pedido, resultado["sesion_id"]))
        filas = cur.fetchall()
    assert [f["accion"] for f in filas] == ["aprobar_pedido_de_entrada", "abrir_sesion_web"]
    assert filas[1]["detalle"]["origen"] == "qr"


def test_el_qr_vence_a_los_5_minutos(conn, intake_world):
    r, _codigo, secreto = _pedir(conn)
    with admin(conn) as cur:
        cur.execute("update pedido_de_entrada set vence_en = now() - interval '1 second' "
                    "where id = %s", (r["pedido_id"],))
    conn.commit()
    assert _aprobar(conn, r["pedido_id"], _tg(intake_world, "Sam North"))["motivo"] == "vencido"
    assert _canjear(conn, r["pedido_id"], secreto)[0] == {"estado": "vencido"}


def test_el_qr_no_cruza_de_puerta(conn, intake_world):
    """Un pedido de la puerta del equipo no lo aprueba el bot de administración, ni al revés."""
    r, _c, secreto = _pedir(conn)
    morgan = intake_world["north-lab"]["people"]["Morgan Hale"]
    _otorgar(conn, morgan["app_user_id"])
    assert _aprobar(conn, r["pedido_id"], morgan["telegram"], puerta="administracion",
                    slug=None)["motivo"] == "no_esta"
    assert _canjear(conn, r["pedido_id"], secreto, puerta="administracion")[0] == {
        "estado": "no_esta"}
    r, _c, secreto = _pedir(conn, puerta="administracion", slug=None)
    assert _aprobar(conn, r["pedido_id"], morgan["telegram"])["motivo"] == "no_esta"
    assert _aprobar(conn, r["pedido_id"], _tg(intake_world, "Sam North"),
                    puerta="administracion", slug=None)["motivo"] == "sin_rol"
    assert _aprobar(conn, r["pedido_id"], morgan["telegram"], puerta="administracion",
                    slug=None)["ok"] is True
    resultado, _s = _canjear(conn, r["pedido_id"], secreto, puerta="administracion")
    assert resultado["estado"] == "adentro"
    with admin(conn) as cur:
        cur.execute("select origen from sesion_de_administracion where id = %s",
                    (resultado["sesion_id"],))
        assert cur.fetchone()["origen"] == "qr"


def test_la_sesion_de_la_computadora_dura_lo_que_dice_el_espacio(conn, intake_world):
    r, _c, secreto = _pedir(conn)
    _aprobar(conn, r["pedido_id"], _tg(intake_world, "Sam North"))
    resultado, sesion = _canjear(conn, r["pedido_id"], secreto)

    def vigente() -> bool:
        with sin_espacio(conn) as cur:
            cur.execute("select * from sesion_vigente(%s)", (_hash(sesion),))
            fila = cur.fetchone()
        conn.commit()
        return fila is not None

    with admin(conn) as cur:
        cur.execute("update sesion_web set creada_en = now() - interval '400 days' where id = %s",
                    (resultado["sesion_id"],))
    conn.commit()
    assert vigente()                       # sin el ajuste, no vence
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, 'sesion_en_la_compu_dias', '30')""",
                    (intake_world["north-lab"]["id"],))
        cur.execute("update sesion_web set creada_en = now() - interval '29 days' where id = %s",
                    (resultado["sesion_id"],))
    conn.commit()
    assert vigente()
    with admin(conn) as cur:
        cur.execute("update sesion_web set creada_en = now() - interval '31 days' where id = %s",
                    (resultado["sesion_id"],))
    conn.commit()
    assert not vigente()
    with admin(conn) as cur:
        cur.execute("select motivo_de_corte from sesion_web where id = %s",
                    (resultado["sesion_id"],))
        assert cur.fetchone()["motivo_de_corte"] == "vencio"
    with pytest.raises(Exception, match="workspace_setting_sesion_en_la_compu"):
        with admin(conn) as cur:
            cur.execute("""update workspace_setting set valor = '3'
                            where clave = 'sesion_en_la_compu_dias'""")


def test_las_sesiones_nuevas_se_cortan_como_siempre(conn, intake_world):
    """La baja, "perdí el celular" y la administración cortan también las de la Mini App y el QR."""
    from leda import web_app

    for motivo in ("perdio_el_celular", "administrador"):
        sesiones = []
        r = _abrir(conn, "north-lab", _tg(intake_world, "Sam North"))
        sesiones.append(r["sesion_id"])
        pedido, _c, secreto = _pedir(conn)
        _aprobar(conn, pedido["pedido_id"], _tg(intake_world, "Sam North"))
        sesiones.append(_canjear(conn, pedido["pedido_id"], secreto)[0]["sesion_id"])
        with espacio(conn, intake_world["north-lab"]["id"]) as cur:
            assert web_app.cortar_sesiones(cur, _membresia(intake_world, "Sam North"),
                                           motivo=motivo) == 2
        conn.commit()
        with admin(conn) as cur:
            cur.execute("select motivo_de_corte from sesion_web where id = any(%s::uuid[])",
                        (sesiones,))
            assert {f["motivo_de_corte"] for f in cur.fetchall()} == {motivo}
    # La baja: la sesión que queda abierta se corta en el próximo pedido.
    sesion = secrets.token_urlsafe(32)
    with sin_espacio(conn) as cur:
        cur.execute("""select abrir_sesion_por_telegram('north-lab', %s, %s,
                                                        now() + interval '10 minutes', %s)""",
                    (_tg(intake_world, "Sam North"), secrets.token_hex(32), _hash(sesion)))
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (_membresia(intake_world, "Sam North"),))
    with sin_espacio(conn) as cur:
        cur.execute("select * from sesion_vigente(%s)", (_hash(sesion),))
        assert cur.fetchone() is None


def test_el_ajuste_lo_cambia_solo_una_sesion_de_administracion(conn, intake_world):
    from tests.garantias.test_puerta_de_administracion import _canjear as canjear_admin
    from tests.garantias.test_puerta_de_administracion import _emitir

    ws = intake_world["north-lab"]["id"]
    with sin_espacio(conn) as cur:
        cur.execute("select fijar_sesion_en_la_compu(%s, %s, 7) as r",
                    (_hash(secrets.token_urlsafe(32)), ws))
        assert cur.fetchone()["r"] == {"ok": False, "motivo": "sin_sesion"}
    conn.commit()
    morgan = intake_world["north-lab"]["people"]["Morgan Hale"]
    _otorgar(conn, morgan["app_user_id"])
    _id, sesion = canjear_admin(conn, _emitir(conn, morgan["app_user_id"]))
    with sin_espacio(conn) as cur:
        cur.execute("select fijar_sesion_en_la_compu(%s, %s, 3) as r", (_hash(sesion), ws))
        assert cur.fetchone()["r"]["motivo"] == "mal_formado"
        cur.execute("select fijar_sesion_en_la_compu(%s, %s, 7) as r", (_hash(sesion), ws))
        assert cur.fetchone()["r"] == {"ok": True, "dias": 7}
        cur.execute("select sesion_en_la_compu(%s, %s) as r", (_hash(sesion), ws))
        assert cur.fetchone()["r"] == {"ok": True, "dias": 7}
        cur.execute("select fijar_sesion_en_la_compu(%s, %s, null) as r", (_hash(sesion), ws))
        cur.execute("select sesion_en_la_compu(%s, %s) as r", (_hash(sesion), ws))
        assert cur.fetchone()["r"] == {"ok": True, "dias": None}
    conn.commit()
    with admin(conn) as cur:
        cur.execute("""select actor_app_user_id, detalle from audit_log
                        where accion = 'fijar_sesion_en_la_compu' order by at""")
        filas = cur.fetchall()
    assert [f["detalle"] for f in filas] == [{"dias": 7, "antes": None},
                                             {"dias": None, "antes": 7}]
    assert {str(f["actor_app_user_id"]) for f in filas} == {morgan["app_user_id"]}


def test_ni_la_firma_ni_los_tokens_quedan_en_la_base(conn, intake_world):
    huella = secrets.token_hex(32)
    _abrir(conn, "north-lab", _tg(intake_world, "Sam North"), huella)
    with admin(conn) as cur:
        cur.execute("select detalle::text as d from audit_log")
        detalles = " ".join(f["d"] for f in cur.fetchall())
        # La huella de la firma, sí (es lo que la gasta); la firma, nunca.
        cur.execute("select count(*) as n from firma_de_telegram where huella = %s", (huella,))
        assert cur.fetchone()["n"] == 1
    assert huella not in detalles


# --- La entrada HTTP ------------------------------------------------------------------------------

@pytest.fixture
def web(conn, monkeypatch, bots):
    """Un navegador nuevo por llamada, con la conexión de la prueba."""
    from fastapi.testclient import TestClient

    from leda import entrada, web_app

    monkeypatch.setattr(web_app, "_conn_de_la_web", lambda: conn)

    def nuevo():
        return TestClient(entrada.app, base_url=BASE, follow_redirects=False)
    return nuevo


def _con_bot_del_equipo(conn, mundo, slug="north-lab", usuario="North_Lab_bot"):
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, 'bot_usuario', to_jsonb(%s::text))""",
                    (mundo[slug]["id"], usuario))
    conn.commit()


def _mini_app(navegador, init_data, slug="north-lab"):
    return navegador.post("/app/api/entrar-telegram",
                          json={"espacio": slug, "init_data": init_data})


def test_la_mini_app_abre_la_puerta_del_equipo_con_la_firma_del_bot_del_espacio(web, conn,
                                                                                intake_world):
    navegador = web()
    r = _mini_app(navegador, firmar(TOKEN_NORTE, _tg(intake_world, "Sam North")))
    assert r.status_code == 200, r.text
    cookie = r.headers["set-cookie"]
    assert "leda_sesion=" in cookie and "HttpOnly" in cookie and "Secure" in cookie
    assert "SameSite=strict" in cookie and "Path=/app" in cookie
    yo = navegador.get("/app/api/yo")
    assert yo.status_code == 200
    assert yo.json()["persona"] == "Sam North 1"


def _alterada(mundo):
    return firmar(TOKEN_NORTE, _tg(mundo, "Sam North")).replace("Prueba", "Otro")


@pytest.mark.parametrize("init_data, motivo", [
    (lambda m: firmar(TOKEN_OESTE, _tg(m, "Sam North")), "firmada por el bot de otro espacio"),
    (lambda m: firmar(TOKEN_ADMIN, _tg(m, "Sam North")), "firmada por el bot de administración"),
    (lambda m: firmar(TOKEN_NORTE, _tg(m, "Sam North"), auth_date=int(time.time()) - 11 * 60),
     "vencida"),
    (_alterada, "alterada"),
    (lambda m: "user=%7B%22id%22%3A1%7D&auth_date=1&hash=" + "0" * 64, "inventada"),
    (lambda m: "", "vacía"),
])
def test_una_firma_que_no_es_del_bot_del_espacio_no_abre_nada(web, conn, intake_world, init_data,
                                                              motivo):
    r = _mini_app(web(), init_data(intake_world))
    assert r.status_code == 401, motivo
    assert "set-cookie" not in r.headers, motivo
    with admin(conn) as cur:
        cur.execute("select count(*) as n from sesion_web")
        assert cur.fetchone()["n"] == 0, motivo


def test_la_misma_firma_no_abre_dos_sesiones(web, conn, intake_world):
    init_data = firmar(TOKEN_NORTE, _tg(intake_world, "Sam North"))
    assert _mini_app(web(), init_data).status_code == 200
    r = _mini_app(web(), init_data)
    assert (r.status_code, r.json()) == (409, {"error": "firma_usada"})


def test_el_espacio_de_la_direccion_solo_no_abre_otro_espacio(web, conn, intake_world):
    """Alguien de West Studio, con una firma válida del bot de West Studio, no entra a North Lab
    cambiando el espacio de la dirección: la firma no verifica con el token de North Lab."""
    init_data = firmar(TOKEN_OESTE, _tg(intake_world, "Sam North", "west-studio"))
    assert _mini_app(web(), init_data).status_code == 401
    assert _mini_app(web(), init_data, slug="west-studio").status_code == 200


def test_quien_no_es_del_equipo_no_entra(web, conn, intake_world):
    r = _mini_app(web(), firmar(TOKEN_NORTE, 999999))
    assert r.status_code == 403
    assert r.json()["error"] == "sin_membresia"
    assert "set-cookie" not in r.headers


def test_la_puerta_de_administracion_solo_con_el_bot_de_administracion(web, conn, intake_world):
    morgan = intake_world["north-lab"]["people"]["Morgan Hale"]
    _otorgar(conn, morgan["app_user_id"])
    navegador = web()
    r = navegador.post("/app/admin/api/entrar-telegram",
                       json={"init_data": firmar(TOKEN_NORTE, morgan["telegram"])})
    assert r.status_code == 401
    r = navegador.post("/app/admin/api/entrar-telegram",
                       json={"init_data": firmar(TOKEN_ADMIN, morgan["telegram"])})
    assert r.status_code == 200, r.text
    assert "leda_admin=" in r.headers["set-cookie"]
    assert navegador.get("/app/admin/api/yo").status_code == 200
    # El canal decide el sombrero: esa sesión no abre la puerta del equipo.
    assert navegador.get("/app/api/yo").status_code == 401
    r = web().post("/app/admin/api/entrar-telegram",
                   json={"init_data": firmar(TOKEN_ADMIN, _tg(intake_world, "Sam North"))})
    assert (r.status_code, r.json()["error"]) == (403, "sin_rol")


def test_otro_sitio_no_entra(web, conn, intake_world):
    r = web().post("/app/api/entrar-telegram", headers={"origin": "https://otro.example"},
                   json={"espacio": "north-lab",
                         "init_data": firmar(TOKEN_NORTE, _tg(intake_world, "Sam North"))})
    assert r.status_code == 403


def test_el_qr_por_la_web_de_punta_a_punta(web, conn, intake_world):
    from leda import entrar_con_telegram as e

    _con_bot_del_equipo(conn, intake_world)
    compu = web()
    r = compu.post("/app/api/entrar/qr", json={"espacio": "north-lab"},
                   headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0) Chrome/130.0 Safari/537"})
    assert r.status_code == 201, r.text
    datos = r.json()
    assert datos["enlace"].startswith("https://t.me/North_Lab_bot?start=compu_")
    assert len(datos["qr"]) == len(datos["qr"][0]) and set("".join(datos["qr"])) == {"0", "1"}
    cookie = r.headers["set-cookie"]
    assert "leda_qr=" in cookie and "HttpOnly" in cookie and "Path=/app/api/entrar/qr" in cookie
    pedido = datos["pedido_id"]
    assert compu.get(f"/app/api/entrar/qr/{pedido}").json() == {"estado": "pendiente"}
    # Otra computadora que vio el QR no lo canjea: no tiene el secreto.
    assert web().get(f"/app/api/entrar/qr/{pedido}").status_code == 404
    codigo = datos["enlace"].rsplit("=", 1)[1]
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        visto = e.ver_pedido(cur, codigo, "equipo", "north-lab")
        assert visto["desde"].startswith("Chrome en Windows")
        assert e.aprobar_pedido(cur, pedido, "equipo", "north-lab",
                                _tg(intake_world, "Sam North"))["ok"] is True
    conn.commit()
    r = compu.get(f"/app/api/entrar/qr/{pedido}")
    assert r.json() == {"estado": "adentro"}
    assert "leda_sesion=" in r.headers["set-cookie"]
    assert compu.get("/app/api/yo").json()["persona"] == "Sam North 1"
    assert compu.get(f"/app/api/entrar/qr/{pedido}").status_code == 404


def test_el_qr_de_la_administracion_lleva_al_bot_de_administracion(web, conn, intake_world):
    r = web().post("/app/admin/api/entrar/qr", json={})
    assert r.status_code == 201, r.text
    assert r.json()["enlace"].startswith("https://t.me/Leda_Admin_bot?start=compu_")
    assert "Path=/app/admin/api/entrar/qr" in r.headers["set-cookie"]


def test_sin_el_bot_del_espacio_no_hay_qr(web, conn, intake_world):
    assert web().post("/app/api/entrar/qr", json={"espacio": "north-lab"}).status_code == 404
    assert web().post("/app/api/entrar/qr", json={"espacio": "no-existe"}).status_code == 404


def test_el_ajuste_de_la_sesion_por_la_web_de_administracion(web, conn, intake_world):
    from tests.garantias.test_puerta_de_administracion import _emitir

    morgan = intake_world["north-lab"]["people"]["Morgan Hale"]
    _otorgar(conn, morgan["app_user_id"])
    navegador = web()
    enlace = _emitir(conn, morgan["app_user_id"])
    assert navegador.post(f"/app/admin/entrar/{enlace}").status_code == 303
    camino = f"/app/admin/api/espacios/{intake_world['north-lab']['id']}/sesion-en-la-compu"
    assert navegador.get(camino).json() == {"dias": None}
    assert navegador.post(camino, json={"dias": 30}).json() == {"dias": 30}
    assert navegador.get(camino).json() == {"dias": 30}
    assert navegador.post(camino, json={"dias": 3}).status_code == 422
    assert navegador.post(camino, json={"dias": None}).json() == {"dias": None}
    assert web().get(camino).status_code == 401


def test_la_validacion_no_registra_init_data(web, conn, intake_world, capsys):
    init_data = firmar(TOKEN_OESTE, _tg(intake_world, "Sam North"))
    _mini_app(web(), init_data)
    salida = capsys.readouterr()
    assert init_data not in salida.out + salida.err
    assert TOKEN_NORTE not in salida.out + salida.err


# --- La revisión de la MA (RDD) ----------------------------------------------------------------

def _pedido_http(cliente: str, cabeceras: dict[str, str]):
    from starlette.requests import Request

    return Request({"type": "http", "method": "POST", "path": "/", "client": (cliente, 5000),
                    "headers": [(k.lower().encode(), v.encode()) for k, v in cabeceras.items()]})


def test_la_ip_que_se_muestra_no_se_puede_inventar_con_una_cabecera():
    """R1-001: cualquiera puede escribir `CF-Connecting-IP` o `X-Forwarded-For`. Se cree la del
    túnel sólo si quien se conecta es el túnel en esta máquina; si no, la de quien se conecta."""
    from leda.entrar_con_telegram import desde_donde

    agente = {"user-agent": "Mozilla/5.0 (Windows NT 10.0) Chrome/130"}
    falsa = {**agente, "cf-connecting-ip": "10.1.2.3", "x-forwarded-for": "10.9.9.9"}
    assert desde_donde(_pedido_http("203.0.113.5", falsa)) == "Chrome en Windows, IP 203.0.113.5"
    assert desde_donde(_pedido_http("127.0.0.1", falsa)) == "Chrome en Windows, IP 10.1.2.3"
    assert desde_donde(_pedido_http("127.0.0.1", {**agente, "x-forwarded-for": "10.9.9.9"})) == (
        "Chrome en Windows, IP 127.0.0.1")
    assert desde_donde(_pedido_http("127.0.0.1", {**agente, "cf-connecting-ip": "no es una ip"})
                       ) == "Chrome en Windows, IP 127.0.0.1"
    assert desde_donde(_pedido_http("testclient", agente)) == "Chrome en Windows"
    # R3-003: el túnel en esta máquina también puede llegar por IPv6 (`::1`, o una IPv4 escrita
    # como IPv6); una dirección de la red local no es el túnel.
    assert desde_donde(_pedido_http("::1", falsa)) == "Chrome en Windows, IP 10.1.2.3"
    assert desde_donde(_pedido_http("::ffff:127.0.0.1", falsa)) == "Chrome en Windows, IP 10.1.2.3"
    assert desde_donde(_pedido_http("192.168.0.10", falsa)) == "Chrome en Windows, IP 192.168.0.10"


def test_la_puerta_del_equipo_nunca_acepta_el_espacio_del_bot_de_administracion(web, conn,
                                                                                intake_world):
    """R3-team-door-accepts-admin-slug: la firma del bot de administración no abre la puerta del
    equipo aunque la dirección diga `admin`, ni pide un QR de equipo para ese bot."""
    morgan = intake_world["north-lab"]["people"]["Morgan Hale"]
    r = _mini_app(web(), firmar(TOKEN_ADMIN, morgan["telegram"]), slug="admin")
    assert r.status_code == 422
    assert web().post("/app/api/entrar/qr", json={"espacio": "admin"}).status_code == 422


def test_un_motivo_desconocido_de_la_base_no_es_una_firma_invalida():
    """R2-catchall-firma-invalida."""
    from leda.entrar_con_telegram import _respuesta_de_la_apertura

    r = _respuesta_de_la_apertura({"ok": False, "motivo": "otro"}, "equipo", "x")
    assert r.status_code == 503
    r = _respuesta_de_la_apertura({"ok": False, "motivo": "firma_vencida"}, "equipo", "x")
    assert r.status_code == 401


def test_el_usuario_del_bot_de_administracion_se_pide_fuera_del_candado_de_la_web(
        web, conn, intake_world, monkeypatch):
    """R4-getme-under-lock-in-db-work: `getMe` es una llamada a Telegram; nunca con el candado de
    la web tomado (la web entera esperaría a la red)."""
    from leda import entrar_con_telegram, web_app

    monkeypatch.delenv("LEDA_BOT_USUARIO_ADMIN", raising=False)
    # R3-002: lo que se aprende de `getMe` vive por proceso; la prueba usa uno propio, vacío, que
    # se devuelve solo aunque falle (ni hereda el de otra prueba ni le deja el suyo).
    monkeypatch.setattr(entrar_con_telegram, "_USUARIO_DEL_BOT_DE_ADMINISTRACION", {})
    con_el_candado = []

    def pedir(token):
        con_el_candado.append(web_app._WEB.locked())
        return "Leda_Admin_bot"

    monkeypatch.setattr(entrar_con_telegram, "_pedir_el_usuario", pedir)
    r = web().post("/app/admin/api/entrar/qr", json={})
    assert r.status_code == 201, r.text
    assert con_el_candado == [False]


# --- La 0074 (la revisión de la MA) -------------------------------------------------------------

def test_la_base_no_abre_una_sesion_con_una_firma_vencida(conn, intake_world):
    """R3-firma-expiry-not-enforced: también la base exige que la firma esté vigente."""
    with sin_espacio(conn) as cur:
        for vence in ("now() - interval '1 second'", "now() + interval '1 hour'"):
            cur.execute(f"""select abrir_sesion_por_telegram('north-lab', %s, %s, {vence}, %s)
                              as r""",
                        (_tg(intake_world, "Sam North"), secrets.token_hex(32),
                         _hash(secrets.token_urlsafe(32))))
            assert cur.fetchone()["r"] == {"ok": False, "motivo": "firma_vencida"}
            cur.execute(f"""select abrir_sesion_de_administracion_por_telegram(%s, %s, {vence}, %s)
                              as r""",
                        (_tg(intake_world, "Sam North"), secrets.token_hex(32),
                         _hash(secrets.token_urlsafe(32))))
            assert cur.fetchone()["r"] == {"ok": False, "motivo": "firma_vencida"}
    conn.commit()


def test_las_firmas_viejas_se_purgan_y_una_repetida_no_abre(conn, intake_world):
    """R3-no-behavioral-tests: la huella de una firma vencida hace más de un día se purga al
    gastar otra; una repetida dentro de su vigencia sigue sin abrir."""
    vieja = secrets.token_hex(32)
    with admin(conn) as cur:
        cur.execute("""insert into firma_de_telegram (huella, puerta, vence_en)
                       values (%s, 'equipo', now() - interval '2 days')""", (vieja,))
    conn.commit()
    huella = secrets.token_hex(32)
    assert _abrir(conn, "north-lab", _tg(intake_world, "Sam North"), huella)["ok"] is True
    assert _abrir(conn, "north-lab", _tg(intake_world, "Sam North"), huella)["motivo"] == \
        "firma_usada"
    with admin(conn) as cur:
        cur.execute("select count(*) as n from firma_de_telegram where huella = %s", (vieja,))
        assert cur.fetchone()["n"] == 0


def test_purgar_un_pedido_viejo_no_borra_los_mensajes_que_lo_nombraban(conn, intake_world):
    """R3-cascade-purge-deletes-notices: la purga de un pedido vencido hace más de un día deja el
    mensaje (y la respuesta del bot de administración) con el pedido en nulo, sin borrarlos; el
    despachador no le pone el botón."""
    from leda.despachador import _boton_de_la_administracion, _boton_de_la_marca
    from leda.salida import enqueue_outbox

    r, _c, _s = _pedir(conn)
    ws = intake_world["north-lab"]["id"]
    persona = _membresia(intake_world, "Sam North")
    with espacio(conn, ws) as cur:
        enqueue_outbox(cur, workspace_id=ws, chat_id=_tg(intake_world, "Sam North"),
                       text="Pediste entrar.", dedupe_key="compu-1", recipient_membership_id=persona,
                       is_response=True, enlace_de_entrada_web=persona,
                       destino_web="entrar_en_la_compu", pedido_de_entrada=r["pedido_id"])
    with admin(conn) as cur:
        cur.execute("""insert into admin_notice (es_respuesta, destinatario_app_user_id, chat_id,
                                                 cuerpo, dedupe_key, boton, pedido_de_entrada_id)
                       values (true, %s, 1, 'Pediste entrar.', 'compu-admin', 'entrar_en_la_compu',
                               %s)""",
                    (intake_world["north-lab"]["people"]["Morgan Hale"]["app_user_id"],
                     r["pedido_id"]))
        cur.execute("update pedido_de_entrada set vence_en = now() - interval '2 days'")
    conn.commit()
    _pedir(conn)                       # purga el viejo
    with admin(conn) as cur:
        cur.execute("select count(*) as n from pedido_de_entrada where id = %s", (r["pedido_id"],))
        assert cur.fetchone()["n"] == 0
        cur.execute("""select w.pedido_de_entrada_id from message_outbox_entrada_web w
                        join message_outbox o on o.id = w.outbox_id where o.dedupe_key = 'compu-1'""")
        [marca] = cur.fetchall()
        cur.execute("select * from admin_notice where dedupe_key = 'compu-admin'")
        aviso = cur.fetchone()
    conn.commit()
    assert marca["pedido_de_entrada_id"] is None
    assert aviso is not None and aviso["pedido_de_entrada_id"] is None
    assert _boton_de_la_administracion(aviso) is None
    assert _boton_de_la_marca(None, ws, {"entrada_web_persona": persona, "chat_id": 1,
                                         "entrada_web_destino": "entrar_en_la_compu",
                                         "entrada_web_pedido": None}) is None


def _pedir_en(cur, slug: str) -> dict:
    cur.execute("select pedir_entrada_por_qr('equipo', %s, %s, %s, 'Chrome en Windows') as r",
                (slug, _hash(secrets.token_urlsafe(24)), _hash(secrets.token_urlsafe(32))))
    return cur.fetchone()["r"]


def test_el_tope_de_pedidos_pendientes_se_cuenta_con_un_candado(conn, uri, intake_world):
    """R3-pending-cap-race, por lo que hace y no por su texto: mientras un pedido de una puerta y
    un espacio no terminó, otro de esa misma puerta y espacio espera su turno (con un tope de
    espera, se ve que no pasa); uno de otro espacio no espera; terminado el primero, pasa."""
    import psycopg

    from leda.db import conectar

    otra = conectar(uri)
    try:
        with sin_espacio(conn) as cur:
            assert _pedir_en(cur, "north-lab")["ok"] is True
            with pytest.raises(psycopg.errors.LockNotAvailable):
                with sin_espacio(otra) as cur_otra:
                    cur_otra.execute("set local lock_timeout = '300ms'")
                    _pedir_en(cur_otra, "north-lab")
            with sin_espacio(otra) as cur_otra:
                cur_otra.execute("set local lock_timeout = '300ms'")
                assert _pedir_en(cur_otra, "west-studio")["ok"] is True
        with sin_espacio(otra) as cur_otra:
            cur_otra.execute("set local lock_timeout = '300ms'")
            assert _pedir_en(cur_otra, "north-lab")["ok"] is True
    finally:
        otra.close()


# --- El lanzador: Telegram en la computadora abre la web en el navegador (MA-2) ----------------
#
# Telegram de escritorio muestra la Mini App dentro de un marco, y la web no se deja enmarcar
# (`frame-ancestors 'none'`). Decisión del usuario (2026-10-14): ahí el botón abre la web en el
# navegador, con el QR. Sólo el lanzador se deja enmarcar, y sólo por Telegram: no tiene sesión,
# ni datos, ni formularios.

TELEGRAM_EN_LA_WEB = "https://web.telegram.org"


@pytest.fixture
def todo_el_servidor(conn, monkeypatch, tmp_path, bots):
    """Todas las rutas del servidor con la conexión de la prueba y una web compilada de mentira:
    nada toca otra base."""
    from fastapi.testclient import TestClient

    from leda import entrada, web_app

    (tmp_path / "index.html").write_text("<!doctype html><title>Leda</title>", encoding="utf-8")
    (tmp_path / "abrir.js").write_text("// lanzador", encoding="utf-8")
    monkeypatch.setattr(web_app, "CARPETA_DE_LA_WEB", tmp_path)
    monkeypatch.setattr(web_app, "_conn_de_la_web", lambda: conn)
    monkeypatch.setattr(entrada, "_conn_de_paginas", lambda: conn)
    monkeypatch.setattr(entrada, "_conn", lambda: conn)
    return TestClient(entrada.app, base_url=BASE, follow_redirects=False)


def _directivas(r) -> dict[str, str]:
    partes = [p.strip() for p in r.headers["content-security-policy"].split(";") if p.strip()]
    return {p.split()[0]: " ".join(p.split()[1:]) for p in partes}


@pytest.mark.parametrize("camino", ["/app/abrir/e/north-lab/", "/app/abrir/e/north-lab/?tarea=x",
                                    "/app/abrir/admin/"])
def test_el_lanzador_solo_se_deja_enmarcar_por_telegram(todo_el_servidor, camino):
    r = todo_el_servidor.get(camino)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    politica = _directivas(r)
    assert politica["frame-ancestors"] == TELEGRAM_EN_LA_WEB
    assert "x-frame-options" not in r.headers
    # Sólo sus propios scripts (el de Telegram y el del lanzador), sin formularios.
    assert politica["script-src"] == "'self'"
    assert politica["default-src"] == "'none'"
    # Sólo a este mismo sitio: el pase de la computadora (MA-5).
    assert politica["connect-src"] == "'self'"
    assert politica["form-action"] == "'none'"
    assert r.headers["cache-control"] == "no-store"
    assert '<script src="/app/telegram-web-app.js"></script>' in r.text
    assert '<script src="/app/abrir.js" defer></script>' in r.text
    assert "<form" not in r.text.lower()


def test_el_lanzador_es_el_mismo_para_cualquiera_y_nunca_toca_una_sesion(todo_el_servidor):
    """Ni lee ni pone una cookie: con la sesión del equipo o de la administración, o sin ninguna,
    la misma página; y nada del pedido vuelve en ella."""
    from leda.web_app import COOKIE, COOKIE_DE_ADMINISTRACION

    sin = todo_el_servidor.get("/app/abrir/e/north-lab/?tarea=%3Cscript%3E")
    con = todo_el_servidor.get("/app/abrir/e/north-lab/?tarea=%3Cscript%3E",
                               cookies={COOKIE: "a" * 43, COOKIE_DE_ADMINISTRACION: "b" * 43})
    admin_ = todo_el_servidor.get("/app/abrir/admin/")
    assert sin.text == con.text == admin_.text
    for r in (sin, con, admin_):
        assert "set-cookie" not in r.headers
        assert "north-lab" not in r.text and "script%3E" not in r.text


@pytest.mark.parametrize("camino", ["/app/abrir/", "/app/abrir/e/", "/app/abrir/e/admin/",
                                    "/app/abrir/e/North_Lab/", "/app/abrir/api/yo",
                                    "/app/abrir/admin/x"])
def test_un_lanzador_que_no_lleva_a_una_puerta_no_existe_y_no_se_enmarca(todo_el_servidor, camino):
    r = todo_el_servidor.get(camino)
    assert r.status_code == 404
    assert r.headers["x-frame-options"] == "DENY"
    assert _directivas(r)["frame-ancestors"] == "'none'"


def _caminos_de_prueba(app) -> list[tuple[str, str]]:
    """Cada ruta del servidor, con valores de mentira en sus partes variables."""
    caminos = []
    rutas = []
    for ruta in app.routes:
        # Las de un router incluido (FastAPI las guarda aparte), con su camino entero.
        incluido = getattr(ruta, "original_router", None)
        rutas.extend(incluido.routes if incluido is not None else [ruta])
    for ruta in rutas:
        metodos = getattr(ruta, "methods", None) or set()
        camino = re.sub(r"\{[^}]+\}", "x", getattr(ruta, "path", ""))
        for metodo in sorted(metodos & {"GET", "POST"}):
            caminos.append((metodo, camino))
    return caminos


def test_ninguna_otra_ruta_se_deja_enmarcar(todo_el_servidor):
    """Todo lo que no es el lanzador sigue con `frame-ancestors 'none'` y `X-Frame-Options:
    DENY`: la web, la API, las páginas, el webhook y la salud."""
    from leda import entrada

    caminos = _caminos_de_prueba(entrada.app)
    assert ("GET", "/app/abrir/x") in caminos and ("POST", "/telegram/x") in caminos
    for metodo, camino in caminos:
        r = todo_el_servidor.request(metodo, camino, json={})
        assert r.headers.get("x-frame-options") == "DENY", (metodo, camino)
        assert _directivas(r).get("frame-ancestors") == "'none'", (metodo, camino)


def test_los_botones_de_la_mini_app_pasan_por_el_lanzador_y_la_direccion_para_la_compu_no():
    """El botón `web_app` (y el del menú) abre el lanzador; la dirección que Leda pasa para la
    computadora es la de la web, sin lanzador."""
    from leda.despachador import (direccion_de_la_administracion, direccion_de_la_mini_app,
                                  direccion_de_la_mini_app_de_administracion,
                                  direccion_de_la_web)

    assert direccion_de_la_mini_app("https://l.example/", "north-lab", "tarea", "t-1") == (
        "https://l.example/app/abrir/e/north-lab/?tarea=t-1")
    assert direccion_de_la_mini_app("https://l.example", "north-lab", "inicio") == (
        "https://l.example/app/abrir/e/north-lab/")
    assert direccion_de_la_mini_app_de_administracion("https://l.example/") == (
        "https://l.example/app/abrir/admin/")
    assert direccion_de_la_web("https://l.example", "north-lab", "inicio") == (
        "https://l.example/app/e/north-lab/")
    assert direccion_de_la_administracion("https://l.example") == "https://l.example/app/admin/"


# --- El pase de la computadora: Telegram en la computadora entra sin el QR (MA-5) ---------------
#
# Decisión del usuario (2026-10-14, noche): en Telegram de escritorio o Telegram Web, el lanzador
# manda la firma de Telegram al servidor, que la valida como la puerta de la Mini App y devuelve un
# pase de un solo uso, que vence al minuto y del que la base guarda sólo la huella; el navegador lo
# canjea al abrirse y queda adentro con la sesión de la computadora (la del QR).

def _emitir_pase(conn, telegram_user_id, *, puerta="equipo", slug="north-lab", huella=None,
                 vence="now() + interval '10 minutes'"):
    pase = secrets.token_urlsafe(32)
    with sin_espacio(conn) as cur:
        cur.execute(f"""select emitir_pase_a_la_compu(%s, %s, %s, %s, {vence}, %s,
                                                      'Telegram en Windows') as r""",
                    (puerta, slug if puerta == "equipo" else None, telegram_user_id,
                     huella or secrets.token_hex(32), _hash(pase)))
        r = cur.fetchone()["r"]
    conn.commit()
    return r, pase


def test_el_pase_abre_la_sesion_de_la_computadora_una_sola_vez(conn, intake_world):
    r, pase = _emitir_pase(conn, _tg(intake_world, "Sam North"))
    assert r["ok"] is True
    pedido = r["pedido_id"]
    with admin(conn) as cur:
        cur.execute("""select estado, extract(epoch from vence_en - pedido_en) as dura,
                              secreto_hash, aprobado_por_membership_id from pedido_de_entrada
                        where id = %s""", (pedido,))
        fila = cur.fetchone()
    assert fila["estado"] == "aprobado" and 50 <= fila["dura"] <= 70
    assert fila["secreto_hash"] == _hash(pase) and pase not in str(fila)
    assert str(fila["aprobado_por_membership_id"]) == _membresia(intake_world, "Sam North")
    resultado, _sesion = _canjear(conn, pedido, pase)
    assert resultado["estado"] == "adentro"
    assert _canjear(conn, pedido, pase)[0] == {"estado": "no_esta"}
    with admin(conn) as cur:
        cur.execute("select origen from sesion_web where id = %s", (resultado["sesion_id"],))
        assert cur.fetchone()["origen"] == "qr"
        cur.execute("""select accion, detalle from audit_log
                        where sujeto_id in (%s, %s) order by at""", (pedido, resultado["sesion_id"]))
        filas = cur.fetchall()
    assert [f["accion"] for f in filas] == ["emitir_pase_a_la_compu", "abrir_sesion_web"]
    assert filas[0]["detalle"]["membership_id"] == _membresia(intake_world, "Sam North")
    assert filas[1]["detalle"]["origen"] == "qr"


def test_el_pase_vence_al_minuto(conn, intake_world):
    r, pase = _emitir_pase(conn, _tg(intake_world, "Sam North"))
    with admin(conn) as cur:
        cur.execute("""update pedido_de_entrada set vence_en = now() - interval '1 second',
                              pedido_en = now() - interval '61 seconds' where id = %s""",
                    (r["pedido_id"],))
    conn.commit()
    assert _canjear(conn, r["pedido_id"], pase)[0] == {"estado": "vencido"}


def test_la_firma_del_pase_sirve_una_sola_vez_tambien_con_la_mini_app(conn, intake_world):
    huella = secrets.token_hex(32)
    assert _emitir_pase(conn, _tg(intake_world, "Sam North"), huella=huella)[0]["ok"] is True
    assert _emitir_pase(conn, _tg(intake_world, "Sam North"), huella=huella)[0] == {
        "ok": False, "motivo": "firma_usada"}
    otra = secrets.token_hex(32)
    assert _abrir(conn, "north-lab", _tg(intake_world, "Sam North"), otra)["ok"] is True
    usada = _emitir_pase(conn, _tg(intake_world, "Sam North"), huella=otra)[0]
    assert usada["motivo"] == "firma_usada"


def test_el_pase_pide_la_membresia_del_espacio_del_bot_y_una_firma_vigente(conn, intake_world):
    otro = _tg(intake_world, "Sam North", "west-studio")
    assert _emitir_pase(conn, otro)[0] == {"ok": False, "motivo": "sin_membresia"}
    assert _emitir_pase(conn, otro, slug="no-existe")[0] == {"ok": False, "motivo": "sin_espacio"}
    for vence in ("now() - interval '1 second'", "now() + interval '30 minutes'"):
        assert _emitir_pase(conn, _tg(intake_world, "Sam North"), vence=vence)[0] == {
            "ok": False, "motivo": "firma_vencida"}
    with admin(conn) as cur:
        cur.execute("select count(*) n from pedido_de_entrada")
        assert cur.fetchone()["n"] == 0


def test_el_pase_de_la_administracion_pide_el_rol_de_plataforma(conn, intake_world):
    morgan = intake_world["north-lab"]["people"]["Morgan Hale"]
    assert _emitir_pase(conn, morgan["telegram"], puerta="administracion")[0] == {
        "ok": False, "motivo": "sin_rol"}
    _otorgar(conn, morgan["app_user_id"])
    r, pase = _emitir_pase(conn, morgan["telegram"], puerta="administracion")
    assert r["ok"] is True
    # Por la puerta del equipo no se canjea.
    assert _canjear(conn, r["pedido_id"], pase)[0] == {"estado": "no_esta"}
    resultado, _ = _canjear(conn, r["pedido_id"], pase, puerta="administracion")
    assert resultado["estado"] == "adentro"
    with admin(conn) as cur:
        cur.execute("select origen from sesion_de_administracion where id = %s",
                    (resultado["sesion_id"],))
        assert cur.fetchone()["origen"] == "qr"


def test_leda_app_emite_el_pase_y_la_funcion_es_del_dueno(conn, intake_world):
    firma = "leda.emitir_pase_a_la_compu(text, text, bigint, text, timestamptz, text, text)"
    with admin(conn) as cur:
        cur.execute("select has_function_privilege('leda_app', %s, 'execute') as si", (firma,))
        assert cur.fetchone()["si"] is True
        cur.execute("""select p.proowner::regrole::text dueno, p.prosecdef
                         from pg_proc p where p.oid = %s::regprocedure""", (firma,))
        fila = cur.fetchone()
    assert (fila["dueno"], fila["prosecdef"]) == ("leda_owner", True)


def _pase(navegador, init_data, slug="north-lab"):
    return navegador.post("/app/api/entrar/pase", json={"espacio": slug, "init_data": init_data})


def test_telegram_en_la_compu_abre_el_navegador_ya_adentro(web, conn, intake_world):
    r = _pase(web(), firmar(TOKEN_NORTE, _tg(intake_world, "Sam North")))
    assert r.status_code == 201, r.text
    direccion = r.json()["direccion"]
    assert re.fullmatch(r"/app/entrar/pase/[0-9a-f-]{36}/[A-Za-z0-9_-]{43}", direccion)
    # Telegram no queda con ninguna sesión: es la del navegador.
    assert "set-cookie" not in r.headers
    navegador = web()
    r = navegador.get(direccion, params={"a": "/app/e/north-lab/?tarea=t-1"})
    assert r.status_code == 303
    assert r.headers["location"] == "/app/e/north-lab/?tarea=t-1"
    cookie = r.headers["set-cookie"]
    assert "leda_sesion=" in cookie and "HttpOnly" in cookie and "Secure" in cookie
    assert "SameSite=strict" in cookie and "Path=/app" in cookie
    assert navegador.get("/app/api/yo").json()["persona"] == "Sam North 1"
    # Una sola vez: otra vez lleva al mismo lugar, sin sesión (ahí está el QR).
    r = web().get(direccion, params={"a": "/app/e/north-lab/"})
    assert (r.status_code, r.headers["location"]) == (303, "/app/e/north-lab/")
    assert "set-cookie" not in r.headers


def test_la_firma_del_pase_no_sirve_dos_veces_ni_de_otro_bot(web, conn, intake_world):
    init_data = firmar(TOKEN_NORTE, _tg(intake_world, "Sam North"))
    assert _pase(web(), init_data).status_code == 201
    assert _pase(web(), init_data).status_code == 409
    r = _pase(web(), firmar(TOKEN_OESTE, _tg(intake_world, "Sam North")))
    assert (r.status_code, r.json()["error"]) == (401, "firma_invalida")
    r = _pase(web(), firmar(TOKEN_NORTE, _tg(intake_world, "Sam North", "west-studio")))
    assert (r.status_code, r.json()["error"]) == (403, "sin_membresia")
    assert r.json()["texto"]
    r = web().post("/app/api/entrar/pase", headers={"origin": "https://otro.example"},
                   json={"espacio": "north-lab",
                         "init_data": firmar(TOKEN_NORTE, _tg(intake_world, "Sam North"))})
    assert r.status_code == 403


@pytest.mark.parametrize("a", ["//otro.example/", "https://otro.example/", "/app/../x",
                               "/app/e/north-lab/?x=<script>", "/otro/", "", "/app/admin/",
                               "/app/e/north-lab//x"])
def test_el_pase_nunca_lleva_fuera_de_su_puerta(web, conn, intake_world, a):
    r = _pase(web(), firmar(TOKEN_NORTE, _tg(intake_world, "Sam North")))
    r = web().get(r.json()["direccion"], params={"a": a})
    assert (r.status_code, r.headers["location"]) == (303, "/app/")


def test_el_pase_de_la_administracion_solo_con_su_bot(web, conn, intake_world):
    morgan = intake_world["north-lab"]["people"]["Morgan Hale"]
    _otorgar(conn, morgan["app_user_id"])
    r = web().post("/app/admin/api/entrar/pase",
                   json={"init_data": firmar(TOKEN_NORTE, morgan["telegram"])})
    assert r.status_code == 401
    r = web().post("/app/admin/api/entrar/pase",
                   json={"init_data": firmar(TOKEN_ADMIN, morgan["telegram"])})
    assert r.status_code == 201, r.text
    direccion = r.json()["direccion"]
    assert direccion.startswith("/app/admin/entrar/pase/")
    navegador = web()
    r = navegador.get(direccion, params={"a": "/app/admin/"})
    assert (r.status_code, r.headers["location"]) == (303, "/app/admin/")
    assert "leda_admin=" in r.headers["set-cookie"]
    assert "Path=/app/admin" in r.headers["set-cookie"]
    assert navegador.get("/app/admin/api/yo").status_code == 200
    # El pase de la administración no abre la puerta del equipo.
    assert navegador.get("/app/api/yo").status_code == 401
    r = web().get(direccion, params={"a": "/app/e/north-lab/"})
    assert r.headers["location"] == "/app/admin/"
    r = web().post("/app/admin/api/entrar/pase",
                   json={"init_data": firmar(TOKEN_ADMIN, _tg(intake_world, "Sam North"))})
    assert (r.status_code, r.json()["error"]) == (403, "sin_rol")


def test_el_pase_no_queda_en_la_consola(web, conn, intake_world, capsys):
    init_data = firmar(TOKEN_NORTE, _tg(intake_world, "Sam North"))
    direccion = _pase(web(), init_data).json()["direccion"]
    web().get(direccion, params={"a": "/app/e/north-lab/"})
    web().get(direccion, params={"a": "/app/e/north-lab/"})
    salida = capsys.readouterr()
    pase = direccion.rsplit("/", 1)[1]
    assert init_data not in salida.out + salida.err and pase not in salida.out + salida.err
