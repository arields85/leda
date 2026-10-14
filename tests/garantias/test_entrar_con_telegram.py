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
