"""Autorización local de Google (rama auxiliar, G2c).

Sin red real: el transporte HTTP es `httpx.MockTransport`, el navegador es una
función que le pega al servidor de loopback REAL con un pedido local (sin
proxy), y el plazo se acorta. Ninguna clave ni credencial sale del entorno
real: se generan acá.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import threading
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from cryptography.fernet import Fernet

from prisma import cli
from prisma.db import admin, espacio
from prisma.google import cifrado, oauth
from prisma.google import credenciales as GC

CLIENTE = oauth.ClienteOAuth("cliente-de-prueba.apps.googleusercontent.com",
                             "SECRETO-DEL-CLIENTE-DE-PRUEBA")
CODIGO = "CODIGO-DE-AUTORIZACION-DE-PRUEBA"
REFRESH = "1//REFRESH-TOKEN-DE-PRUEBA"
ACCESO = "ya29.ACCESS-TOKEN-DE-PRUEBA"
CUENTA = "admin@example.com"
SCOPES_CONCEDIDOS = " ".join(oauth.SCOPES)

SECRETOS = (CODIGO, REFRESH, ACCESO, CLIENTE.client_secret)


def _id_token(**cambios) -> str:
    claims = {"iss": "https://accounts.google.com", "aud": CLIENTE.client_id,
              "exp": int((datetime.now(timezone.utc)
                          + timedelta(hours=1)).timestamp()),
              "email": CUENTA, "email_verified": True}
    claims.update(cambios)
    claims = {k: v for k, v in claims.items() if v is not None}

    def b64(d):
        return base64.urlsafe_b64encode(
            json.dumps(d).encode()).rstrip(b"=").decode()

    return f"{b64({'alg': 'none'})}.{b64(claims)}.firma"


def _respuesta_ok(**cambios) -> dict:
    r = {"access_token": ACCESO, "expires_in": 3599, "refresh_token": REFRESH,
         "scope": SCOPES_CONCEDIDOS, "token_type": "Bearer",
         "id_token": _id_token()}
    r.update(cambios)
    return {k: v for k, v in r.items() if v is not None}


class Transporte:
    """`httpx.Client` de prueba que anota cada pedido."""

    def __init__(self, respuesta=None, *, estado=200, error=None):
        self.pedidos: list[httpx.Request] = []
        self._respuesta = _respuesta_ok() if respuesta is None else respuesta
        self._estado = estado
        self._error = error
        self.cliente = httpx.Client(transport=httpx.MockTransport(self._atender))

    def _atender(self, pedido):
        self.pedidos.append(pedido)
        if self._error:
            raise self._error
        return httpx.Response(self._estado, json=self._respuesta)

    @property
    def formulario(self) -> dict:
        return {k: v[0] for k, v in
                parse_qs(self.pedidos[0].content.decode()).items()}


_SIN_PROXY = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _navegador(**cambios):
    """Un "navegador": arma la devolución de Google contra el redirect_uri de
    la URL que recibe y le pega al servidor de loopback desde otro hilo.
    `cambios` pisa (o quita, con None) parámetros de la devolución."""
    visto: dict = {}

    def abrir(url):
        params = {k: v[0] for k, v in parse_qs(urlsplit(url).query).items()}
        visto.update(url=url, params=params)
        devolucion = {"code": CODIGO, "state": params["state"]}
        devolucion.update(cambios)
        devolucion = {k: v for k, v in devolucion.items() if v is not None}
        destino = params["redirect_uri"] + "?" + "&".join(
            f"{k}={v}" for k, v in devolucion.items())

        def pegar():
            with _SIN_PROXY.open(destino, timeout=5) as r:
                visto["pagina"] = r.read().decode()

        hilo = threading.Thread(target=pegar)
        hilo.start()
        visto["hilo"] = hilo

    abrir.visto = visto
    return abrir


def _correr(transporte=None, abrir=None, **kw):
    transporte = transporte or Transporte()
    abrir = abrir or _navegador()
    kw.setdefault("esperar_segundos", 5)
    kw.setdefault("imprimir", lambda t: None)
    try:
        return oauth.autorizar(CLIENTE, http=transporte.cliente,
                               abrir_navegador=abrir, **kw)
    finally:
        hilo = getattr(abrir, "visto", {}).get("hilo")
        if hilo:
            hilo.join(5)


# ---------------------------------------------------------------------------
# URL de autorización, PKCE y servidor de loopback
# ---------------------------------------------------------------------------


def test_la_url_lleva_todos_los_parametros_y_el_desafio_s256_del_verificador():
    t, abrir = Transporte(), _navegador()
    _correr(t, abrir)

    url = abrir.visto["url"]
    assert url.startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    p = abrir.visto["params"]
    assert p["client_id"] == CLIENTE.client_id
    assert re.fullmatch(r"http://127\.0\.0\.1:\d+/", p["redirect_uri"])
    assert p["response_type"] == "code"
    assert p["scope"] == ("openid email "
                          "https://www.googleapis.com/auth/gmail.send "
                          "https://www.googleapis.com/auth/calendar.events")
    assert p["access_type"] == "offline"
    assert p["prompt"] == "consent"
    assert p["code_challenge_method"] == "S256"
    assert len(p["state"]) >= 16

    verificador = t.formulario["code_verifier"]
    assert 43 <= len(verificador) <= 128
    esperado = base64.urlsafe_b64encode(
        hashlib.sha256(verificador.encode()).digest()).rstrip(b"=").decode()
    assert p["code_challenge"] == esperado


def test_cada_corrida_usa_state_y_verificador_distintos():
    a, b = _navegador(), _navegador()
    ta, tb = Transporte(), Transporte()
    _correr(ta, a)
    _correr(tb, b)
    assert a.visto["params"]["state"] != b.visto["params"]["state"]
    assert ta.formulario["code_verifier"] != tb.formulario["code_verifier"]


def test_el_canje_manda_el_formulario_esperado_al_endpoint_de_google():
    t, abrir = Transporte(), _navegador()
    _correr(t, abrir)
    assert len(t.pedidos) == 1
    assert str(t.pedidos[0].url) == "https://oauth2.googleapis.com/token"
    assert t.pedidos[0].method == "POST"
    f = t.formulario
    assert f["grant_type"] == "authorization_code"
    assert f["code"] == CODIGO
    assert f["client_id"] == CLIENTE.client_id
    assert f["client_secret"] == CLIENTE.client_secret
    assert f["redirect_uri"] == abrir.visto["params"]["redirect_uri"]


def test_el_navegador_recibe_una_pagina_neutra_sin_secretos():
    abrir = _navegador()
    _correr(Transporte(), abrir)
    pagina = abrir.visto["pagina"]
    assert "cerrar esta pestaña" in pagina
    for s in SECRETOS:
        assert s not in pagina


def test_solo_cuenta_la_devolucion_de_google_no_un_favicon():
    t = Transporte()
    visto = {}

    def abrir(url):
        params = {k: v[0] for k, v in parse_qs(urlsplit(url).query).items()}
        base = params["redirect_uri"]

        def pegar():
            try:
                _SIN_PROXY.open(base + "favicon.ico", timeout=5)
            except urllib.error.HTTPError as e:
                visto["favicon"] = e.code
            _SIN_PROXY.open(
                f"{base}?code={CODIGO}&state={params['state']}", timeout=5).read()

        visto["hilo"] = threading.Thread(target=pegar)
        visto["hilo"].start()

    abrir.visto = visto
    r = _correr(t, abrir)
    assert visto["favicon"] == 404
    assert r.cuenta_email == CUENTA


def test_un_state_distinto_se_rechaza_sin_canjear():
    t = Transporte()
    with pytest.raises(oauth.ErrorOAuth, match="state"):
        _correr(t, _navegador(state="otro-state"))
    assert t.pedidos == []


@pytest.mark.parametrize("error", ["access_denied", "invalid_scope"])
def test_un_error_de_google_se_informa_solo_con_su_codigo_sin_canjear(error):
    t = Transporte()
    with pytest.raises(oauth.ErrorOAuth) as e:
        _correr(t, _navegador(code=None, error=error))
    assert error in str(e.value)
    assert t.pedidos == []


def test_si_no_llega_la_devolucion_se_agota_el_tiempo():
    t = Transporte()
    with pytest.raises(oauth.ErrorOAuth, match="tiempo"):
        _correr(t, lambda url: None, esperar_segundos=0.3)
    assert t.pedidos == []


def test_el_servidor_solo_escucha_en_loopback_y_se_cierra_al_terminar():
    abrir = _navegador()
    _correr(Transporte(), abrir)
    redirect = abrir.visto["params"]["redirect_uri"]
    assert redirect.startswith("http://127.0.0.1:")
    with pytest.raises(OSError):
        _SIN_PROXY.open(redirect, timeout=2)


# ---------------------------------------------------------------------------
# Canje y validación
# ---------------------------------------------------------------------------


def test_el_camino_feliz_devuelve_la_autorizacion_validada():
    ahora = datetime(2026, 1, 1, tzinfo=timezone.utc)
    id_token = _id_token(exp=int((ahora + timedelta(hours=1)).timestamp()),
                         email="Admin@Example.com")
    t = Transporte(_respuesta_ok(id_token=id_token))
    a = _correr(t, ahora=lambda: ahora)
    assert a.refresh_token == REFRESH
    assert a.access_token == ACCESO
    assert a.access_token_expira_en == ahora + timedelta(seconds=3599)
    assert a.cuenta_email == CUENTA
    assert set(oauth.SCOPES) <= set(a.scopes)
    for s in (REFRESH, ACCESO):
        assert s not in repr(a)


def test_un_error_del_endpoint_muestra_solo_el_campo_error():
    t = Transporte({"error": "invalid_grant",
                    "error_description": "DETALLE-QUE-NO-DEBE-SALIR"},
                   estado=400)
    with pytest.raises(oauth.ErrorOAuth) as e:
        _correr(t)
    assert "invalid_grant" in str(e.value)
    assert "DETALLE" not in str(e.value)
    assert CODIGO not in str(e.value)


def test_un_cuerpo_de_error_sin_forma_de_codigo_no_se_muestra():
    t = Transporte({"error": "Texto libre con <html> y secretos"}, estado=500)
    with pytest.raises(oauth.ErrorOAuth) as e:
        _correr(t)
    assert "secretos" not in str(e.value)


def test_un_error_de_red_no_filtra_nada():
    t = Transporte(error=httpx.ConnectError(f"boom {CODIGO} {REFRESH}"))
    with pytest.raises(oauth.ErrorOAuth) as e:
        _correr(t)
    for s in SECRETOS:
        assert s not in str(e.value)


def test_sin_refresh_token_explica_como_reintentar():
    t = Transporte(_respuesta_ok(refresh_token=None))
    with pytest.raises(oauth.ErrorOAuth) as e:
        _correr(t)
    assert "permiso de larga duración" in str(e.value)
    assert "myaccount.google.com/permissions" in str(e.value)


@pytest.mark.parametrize("falta,palabras", [
    ("https://www.googleapis.com/auth/gmail.send", "enviar correos"),
    ("https://www.googleapis.com/auth/calendar.events", "eventos"),
])
def test_un_permiso_obligatorio_no_concedido_no_se_guarda(falta, palabras):
    concedidos = " ".join(s for s in oauth.SCOPES if s != falta)
    t = Transporte(_respuesta_ok(scope=concedidos))
    with pytest.raises(oauth.ErrorOAuth) as e:
        _correr(t)
    assert palabras in str(e.value)
    assert falta not in str(e.value)


@pytest.mark.parametrize("cambios", [
    {"iss": "https://evil.example.com"},
    {"aud": "otro-cliente"},
    {"exp": 1},
    {"email_verified": False},
    {"email_verified": "true"},
    {"email": None},
], ids=["iss", "aud", "exp", "email_no_verificado", "verificado_texto",
        "sin_email"])
def test_cada_verificacion_de_la_identidad_rechaza(cambios):
    t = Transporte(_respuesta_ok(id_token=_id_token(**cambios)))
    with pytest.raises(oauth.ErrorOAuth):
        _correr(t)


@pytest.mark.parametrize("emisor", ["accounts.google.com",
                                    "https://accounts.google.com"])
def test_los_dos_emisores_de_google_se_aceptan(emisor):
    t = Transporte(_respuesta_ok(id_token=_id_token(iss=emisor)))
    assert _correr(t).cuenta_email == CUENTA


@pytest.mark.parametrize("id_token", [None, "sin-puntos", "a.b.c", "a..c"])
def test_un_id_token_ausente_o_ilegible_rechaza(id_token):
    t = Transporte(_respuesta_ok(id_token=id_token))
    with pytest.raises(oauth.ErrorOAuth):
        _correr(t)


def test_la_audiencia_puede_ser_una_lista_que_incluye_al_cliente():
    t = Transporte(_respuesta_ok(id_token=_id_token(aud=["x", CLIENTE.client_id])))
    assert _correr(t).cuenta_email == CUENTA


# ---------------------------------------------------------------------------
# Cliente OAuth del entorno
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("entorno,variable", [
    ({oauth.VARIABLE_CLIENT_SECRET: "s"}, oauth.VARIABLE_CLIENT_ID),
    ({oauth.VARIABLE_CLIENT_ID: "i"}, oauth.VARIABLE_CLIENT_SECRET),
    ({oauth.VARIABLE_CLIENT_ID: "  ", oauth.VARIABLE_CLIENT_SECRET: "s"},
     oauth.VARIABLE_CLIENT_ID),
])
def test_cargar_cliente_nombra_la_variable_que_falta_sin_valores(entorno, variable):
    with pytest.raises(oauth.ErrorOAuth) as e:
        oauth.cargar_cliente(entorno)
    assert variable in str(e.value)
    assert "i" != str(e.value)


def test_cargar_cliente_lee_ambos_valores():
    c = oauth.cargar_cliente({oauth.VARIABLE_CLIENT_ID: " id ",
                              oauth.VARIABLE_CLIENT_SECRET: "sec"})
    assert (c.client_id, c.client_secret) == ("id", "sec")
    assert "sec" not in repr(c)


# ---------------------------------------------------------------------------
# Comandos: `google autorizar`, `activar`, `estado`
# ---------------------------------------------------------------------------


class _ConexionEspia:
    def __init__(self, real):
        self._real = real

    def close(self):
        pass

    def __getattr__(self, nombre):
        return getattr(self._real, nombre)


@pytest.fixture
def entorno(conn, monkeypatch):
    """Base de la prueba, clave y cliente descartables, y un Google falso."""
    clave = Fernet.generate_key().decode("ascii")
    monkeypatch.setenv(cifrado.VARIABLE_CLAVE, clave)
    monkeypatch.setenv(oauth.VARIABLE_CLIENT_ID, CLIENTE.client_id)
    monkeypatch.setenv(oauth.VARIABLE_CLIENT_SECRET, CLIENTE.client_secret)
    aperturas = []
    monkeypatch.setattr(
        cli, "conectar", lambda *a, **k: aperturas.append(1) or _ConexionEspia(conn))
    transporte = Transporte()
    monkeypatch.setattr(oauth, "_nuevo_http", lambda: transporte.cliente)
    monkeypatch.setattr(oauth, "ESPERA_MAXIMA_SEGUNDOS", 5.0)
    navegador = _navegador()
    monkeypatch.setattr(oauth, "_abrir_navegador", navegador)

    class E:
        pass

    e = E()
    e.clave, e.aperturas, e.transporte, e.navegador = (
        clave, aperturas, transporte, navegador)
    yield e
    hilo = navegador.visto.get("hilo")
    if hilo:
        hilo.join(5)


def _estado_guardado(conn, ws):
    with admin(conn) as cur:
        cur.execute("select token_cifrado from credencial_google "
                    "where workspace_id = %s", (ws,))
        return cur.fetchone()


def _sin_secretos(salida: str, extra=()):
    for s in SECRETOS + tuple(extra):
        assert s not in salida


def test_autorizar_guarda_el_payload_cifrado_y_avisa_como_activar(
        intake_world, conn, entorno, capsys):
    ws = intake_world["north-lab"]["id"]
    assert cli.main(["google", "autorizar", "north-lab"]) == 0
    salida = capsys.readouterr()

    _sin_secretos(salida.out + salida.err,
                  [entorno.transporte.formulario["code_verifier"]])
    assert CUENTA in salida.out and "north-lab" in salida.out
    assert "python -m prisma google activar north-lab" in salida.out

    crudo = _estado_guardado(conn, ws)["token_cifrado"]
    assert REFRESH not in crudo
    with espacio(conn, ws) as cur:
        assert GC.estado(cur) == "vigente"
        cred = GC.leer(cur, cifrador=cifrado.desde_texto(entorno.clave))
    payload = json.loads(cred.secreto)
    assert payload["refresh_token"] == REFRESH
    assert payload["access_token"] == ACCESO
    assert payload["cuenta_email"] == CUENTA
    assert set(oauth.SCOPES) <= set(payload["scopes"])
    assert payload["access_token_expira_en"]
    assert cred.cuenta_email == CUENTA
    assert set(oauth.SCOPES) <= set(cred.scopes)
    # Recién autorizado no queda encendido.
    with espacio(conn, ws) as cur:
        assert GC.habilitado(cur, ws) is False


def test_autorizar_sin_navegador_no_lo_abre_e_imprime_la_url(
        intake_world, conn, entorno, monkeypatch, capsys):
    llamadas = []
    monkeypatch.setattr(oauth, "_abrir_navegador", llamadas.append)
    monkeypatch.setattr(oauth, "ESPERA_MAXIMA_SEGUNDOS", 0.3)
    assert cli.main(["google", "autorizar", "north-lab", "--sin-navegador"]) == 1
    salida = capsys.readouterr().out
    assert llamadas == []
    assert "https://accounts.google.com/o/oauth2/v2/auth?" in salida
    assert entorno.transporte.pedidos == []


def test_autorizar_sin_clave_no_hace_red_ni_abre_la_base(
        intake_world, conn, entorno, monkeypatch, capsys):
    monkeypatch.delenv(cifrado.VARIABLE_CLAVE)
    assert cli.main(["google", "autorizar", "north-lab"]) == 1
    salida = capsys.readouterr().out
    assert cifrado.VARIABLE_CLAVE in salida
    assert entorno.transporte.pedidos == []
    assert entorno.aperturas == []
    assert entorno.navegador.visto == {}


@pytest.mark.parametrize("variable", [oauth.VARIABLE_CLIENT_ID,
                                      oauth.VARIABLE_CLIENT_SECRET])
def test_autorizar_sin_cliente_oauth_no_hace_red_ni_escribe(
        intake_world, conn, entorno, monkeypatch, capsys, variable):
    monkeypatch.delenv(variable)
    assert cli.main(["google", "autorizar", "north-lab"]) == 1
    salida = capsys.readouterr()
    assert variable in salida.out
    _sin_secretos(salida.out + salida.err)
    assert entorno.transporte.pedidos == []
    assert entorno.aperturas == []
    assert _estado_guardado(conn, intake_world["north-lab"]["id"]) is None


def test_autorizar_con_una_clave_invalida_no_filtra_ni_escribe(
        intake_world, conn, entorno, monkeypatch, capsys):
    monkeypatch.setenv(cifrado.VARIABLE_CLAVE, "no-es-una-clave-SECRETO987")
    assert cli.main(["google", "autorizar", "north-lab"]) == 1
    salida = capsys.readouterr().out
    assert "SECRETO987" not in salida
    assert entorno.transporte.pedidos == []
    assert entorno.aperturas == []


def test_autorizar_un_espacio_inexistente_falla_sin_red(
        intake_world, conn, entorno, capsys):
    assert cli.main(["google", "autorizar", "no-existe"]) == 1
    assert "no-existe" in capsys.readouterr().out
    assert entorno.transporte.pedidos == []
    assert entorno.navegador.visto == {}


@pytest.mark.parametrize("respuesta,estado", [
    ({"error": "invalid_grant", "error_description": "x"}, 400),
    (_respuesta_ok(refresh_token=None), 200),
    (_respuesta_ok(scope="openid email"), 200),
    (_respuesta_ok(id_token=_id_token(email_verified=False)), 200),
], ids=["error_de_google", "sin_refresh", "sin_scopes", "identidad"])
def test_una_falla_del_flujo_sale_con_1_sin_guardar_ni_filtrar(
        intake_world, conn, entorno, monkeypatch, capsys, respuesta, estado):
    monkeypatch.setattr(oauth, "_nuevo_http",
                        lambda: Transporte(respuesta, estado=estado).cliente)
    assert cli.main(["google", "autorizar", "north-lab"]) == 1
    salida = capsys.readouterr()
    _sin_secretos(salida.out + salida.err)
    assert _estado_guardado(conn, intake_world["north-lab"]["id"]) is None


def test_una_falla_de_seguridad_del_callback_sale_con_1_sin_guardar(
        intake_world, conn, entorno, monkeypatch, capsys):
    monkeypatch.setattr(oauth, "_abrir_navegador", _navegador(state="falso"))
    assert cli.main(["google", "autorizar", "north-lab"]) == 1
    salida = capsys.readouterr()
    _sin_secretos(salida.out + salida.err)
    assert entorno.transporte.pedidos == []
    assert _estado_guardado(conn, intake_world["north-lab"]["id"]) is None


def test_activar_rechaza_sin_credencial_vigente(
        intake_world, conn, entorno, capsys):
    ws = intake_world["north-lab"]["id"]
    assert cli.main(["google", "activar", "north-lab"]) == 1
    assert "autorizar" in capsys.readouterr().out
    with espacio(conn, ws) as cur:
        assert GC.habilitado(cur, ws) is False


def test_activar_y_desactivar_con_credencial_vigente(
        intake_world, conn, entorno, capsys):
    ws = intake_world["north-lab"]["id"]
    assert cli.main(["google", "autorizar", "north-lab"]) == 0
    assert cli.main(["google", "activar", "north-lab"]) == 0
    with espacio(conn, ws) as cur:
        assert GC.habilitado(cur, ws) is True
    with espacio(conn, intake_world["west-studio"]["id"]) as cur:
        assert GC.habilitado(cur, intake_world["west-studio"]["id"]) is False

    assert cli.main(["google", "activar", "north-lab", "--desactivar"]) == 0
    with espacio(conn, ws) as cur:
        assert GC.habilitado(cur, ws) is False


def test_desactivar_no_exige_credencial(intake_world, conn, entorno):
    assert cli.main(["google", "activar", "north-lab", "--desactivar"]) == 0


def test_estado_muestra_cuenta_scopes_y_si_esta_encendido_sin_secretos(
        intake_world, conn, entorno, capsys):
    assert cli.main(["google", "estado", "north-lab"]) == 0
    sin = capsys.readouterr().out
    assert "sin_autorizar" in sin and "apagado" in sin.lower()

    assert cli.main(["google", "autorizar", "north-lab"]) == 0
    assert cli.main(["google", "activar", "north-lab"]) == 0
    capsys.readouterr()
    assert cli.main(["google", "estado", "north-lab"]) == 0
    salida = capsys.readouterr().out
    assert "vigente" in salida
    assert CUENTA in salida
    assert "gmail.send" in salida and "calendar.events" in salida
    assert "encendido" in salida.lower()
    _sin_secretos(salida)
    with admin(conn) as cur:
        cur.execute("select token_cifrado from credencial_google")
        for f in cur.fetchall():
            assert f["token_cifrado"] not in salida


def test_estado_de_un_espacio_inexistente_falla(intake_world, conn, entorno, capsys):
    assert cli.main(["google", "estado", "no-existe"]) == 1
    assert "no-existe" in capsys.readouterr().out
