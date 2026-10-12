"""La puerta de administración de la plataforma web (ADR 0022, decisiones 10, 11 y 12; porción 2,
tarea P2-1 de `odd/tasks/plataforma-p2.md`; migración 0061): la capa de garantías, en la base y
en la entrada HTTP.

- **Sin espacio:** un administrador de plataforma abarca todos los espacios, así que su enlace y
  su sesión viven en tablas propias, sin `workspace_id`, a las que `leda_app` no llega: sólo por
  las funciones `security definer` de `leda_owner`. Emitir un enlace y cortar todas las sesiones
  de un administrador los ejecuta sólo la consola (`leda_admin`).
- **El rol se comprueba en la base, en cada pedido:** sin el rol `administrador` vigente en
  `platform_role` no se emite un enlace, no se canjea ni entra una sesión; un rol revocado corta
  la sesión en el pedido siguiente, con su motivo y su auditoría.
- **El enlace sirve una sola vez** y uno nuevo anula el que estaba sin usar, como el de la puerta
  del equipo; sólo se guarda el hash de cada token.
- **Dos puertas separadas** (constitución §2: el canal define el sombrero): la cookie del equipo
  no abre la administración y la de la administración no abre la API del equipo, también para un
  administrador que además es integrante de un equipo.
- **Auditoría** (constitución §12): emitir, canjear y cortar dejan su fila en `audit_log`, sin
  espacio (son hechos de alcance global), con la versión del núcleo y sin el token ni su hash.
"""

from __future__ import annotations

import contextlib
import hashlib
import re
import secrets
from pathlib import Path

import psycopg
import pytest

from leda.db import admin, espacio

TABLAS = ("enlace_de_administracion", "sesion_de_administracion")
# Las que la web ejecuta (como `leda_app`) y las que sólo ejecuta la consola (`leda_admin`).
DE_LA_WEB = ("canjear_enlace_de_administracion", "sesion_de_administracion_vigente",
             "cerrar_sesion_de_administracion")
DE_LA_CONSOLA = ("emitir_enlace_de_administracion", "cortar_sesiones_de_administrador")

BASE = "https://testserver"
CABECERAS = {"cache-control": "no-store", "referrer-policy": "no-referrer",
             "x-robots-tag": "noindex, nofollow", "x-content-type-options": "nosniff",
             "x-frame-options": "DENY"}
CUATROCIENTOS_DIAS = 400 * 24 * 60 * 60


# --- Ayudas ---------------------------------------------------------------------------------

def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@contextlib.contextmanager
def sin_espacio(conn):
    """La web antes de saber quién es (el canje y cada pedido)."""
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local role leda_app")
            yield cur


def _usuario(mundo: dict, nombre: str, slug: str = "north-lab") -> str:
    return mundo[slug]["people"][nombre]["app_user_id"]


def _otorgar(conn, app_user_id: str, rol: str = "administrador") -> None:
    with admin(conn) as cur:
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, %s)",
                    (app_user_id, rol))
    conn.commit()


def _revocar(conn, app_user_id: str) -> None:
    with admin(conn) as cur:
        cur.execute("delete from platform_role where app_user_id = %s and rol = 'administrador'",
                    (app_user_id,))
    conn.commit()


@pytest.fixture
def administradora(conn, intake_world) -> str:
    """Morgan Hale, de North Lab: administradora de plataforma y, además, autoridad final de su
    equipo (las dos puertas tienen que quedar separadas)."""
    quien = _usuario(intake_world, "Morgan Hale")
    _otorgar(conn, quien)
    return quien


def _emitir(conn, app_user_id: str, actor: str | None = None) -> str | None:
    """Emite el enlace como la consola; devuelve el token en claro o `None`."""
    token = secrets.token_urlsafe(32)
    with admin(conn) as cur:
        cur.execute("select emitir_enlace_de_administracion(%s, %s, %s) as id",
                    (app_user_id, _hash(token), actor))
        emitido = cur.fetchone()["id"]
    conn.commit()
    return token if emitido else None


def _canjear(conn, token: str) -> tuple[str | None, str]:
    sesion = secrets.token_urlsafe(32)
    with sin_espacio(conn) as cur:
        cur.execute("select canjear_enlace_de_administracion(%s, %s) as id",
                    (_hash(token), _hash(sesion)))
        sesion_id = cur.fetchone()["id"]
    conn.commit()
    return (str(sesion_id) if sesion_id else None), sesion


def _entrar(conn, app_user_id: str) -> tuple[str, str]:
    sesion_id, sesion = _canjear(conn, _emitir(conn, app_user_id))
    assert sesion_id
    return sesion_id, sesion


def _vigente(conn, sesion: str) -> dict | None:
    with sin_espacio(conn) as cur:
        cur.execute("select * from sesion_de_administracion_vigente(%s)", (_hash(sesion),))
        fila = cur.fetchone()
    conn.commit()
    return fila


def _auditoria(conn, accion: str) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select * from audit_log where accion = %s order by at, id", (accion,))
        filas = cur.fetchall()
    conn.commit()
    return filas


def _sesion(conn, sesion_id: str) -> dict:
    with admin(conn) as cur:
        cur.execute("select * from sesion_de_administracion where id = %s", (sesion_id,))
        fila = cur.fetchone()
    conn.commit()
    return fila


def _contar(conn, tabla: str, donde: str = "true") -> int:
    with admin(conn) as cur:
        cur.execute(f"select count(*) n from {tabla} where {donde}")
        n = cur.fetchone()["n"]
    conn.commit()
    return n


# --- Las tablas y las funciones -------------------------------------------------------------

def test_las_tablas_no_tienen_espacio_y_la_aplicacion_no_llega_a_ellas(conn, intake_world):
    with admin(conn) as cur:
        for tabla in TABLAS:
            cur.execute("""select column_name from information_schema.columns
                            where table_schema = 'leda' and table_name = %s""", (tabla,))
            columnas = {f["column_name"] for f in cur.fetchall()}
            assert columnas, f"{tabla} no existe"
            assert "workspace_id" not in columnas, tabla
            assert {"app_user_id", "token_hash"} <= columnas, tabla
    conn.commit()
    for como in (sin_espacio(conn), espacio(conn, intake_world["north-lab"]["id"])):
        with como as cur:
            for tabla in TABLAS:
                for orden in (f"select * from {tabla}", f"delete from {tabla}",
                              f"update {tabla} set token_hash = token_hash"):
                    with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                        cur.execute(orden)


def test_las_funciones_son_elevadas_y_cada_una_la_ejecuta_quien_corresponde(conn):
    with admin(conn) as cur:
        cur.execute(
            """select p.proname, r.rolname, p.prosecdef, p.proconfig,
                      has_function_privilege('public', p.oid, 'execute') as de_public,
                      has_function_privilege('leda_app', p.oid, 'execute') as de_app,
                      has_function_privilege('leda_gateway', p.oid, 'execute') as de_gateway,
                      has_function_privilege('leda_admin', p.oid, 'execute') as de_admin
                 from pg_proc p join pg_roles r on r.oid = p.proowner
                 join pg_namespace n on n.oid = p.pronamespace
                where n.nspname = 'leda' and p.proname = any(%s)""",
            (list(DE_LA_WEB + DE_LA_CONSOLA),))
        filas = {f["proname"]: f for f in cur.fetchall()}
    conn.commit()
    assert set(filas) == set(DE_LA_WEB + DE_LA_CONSOLA)
    for nombre, f in filas.items():
        assert f["rolname"] == "leda_owner", nombre
        assert f["prosecdef"], f"{nombre} tiene que ser security definer"
        assert any(c.startswith("search_path=") and c.endswith("pg_temp")
                   for c in f["proconfig"] or []), nombre
        assert not f["de_public"] and not f["de_gateway"], nombre
        if nombre in DE_LA_WEB:
            assert f["de_app"], nombre
        else:
            assert not f["de_app"], f"la web no puede {nombre}"
            assert f["de_admin"], nombre


def test_la_web_no_emite_enlaces_ni_corta_sesiones_de_un_administrador(conn, administradora):
    with sin_espacio(conn) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute("select emitir_enlace_de_administracion(%s, %s, null)",
                        (administradora, _hash("x")))
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute("select cortar_sesiones_de_administrador(%s, 'administrador', null)",
                        (administradora,))
    conn.commit()


# --- El rol de plataforma --------------------------------------------------------------------

def test_a_quien_no_es_administrador_no_se_le_emite_un_enlace(conn, intake_world):
    integrante = _usuario(intake_world, "Sam North")
    assert _emitir(conn, integrante) is None
    operador = _usuario(intake_world, "Taylor Quinn")
    _otorgar(conn, operador, "operador")
    assert _emitir(conn, operador) is None, "el rol de operador no abre la administración"
    assert _contar(conn, "enlace_de_administracion") == 0
    assert _auditoria(conn, "emitir_enlace_de_administracion") == []


def test_un_rol_revocado_antes_del_canje_no_abre_nada(conn, administradora):
    enlace = _emitir(conn, administradora)
    _revocar(conn, administradora)
    assert _canjear(conn, enlace)[0] is None
    assert _contar(conn, "sesion_de_administracion") == 0


def test_un_rol_revocado_corta_la_sesion_en_el_pedido_siguiente(conn, administradora):
    sesion_id, sesion = _entrar(conn, administradora)
    assert _vigente(conn, sesion) is not None
    _revocar(conn, administradora)
    assert _vigente(conn, sesion) is None
    fila = _sesion(conn, sesion_id)
    assert fila["cortada_en"] is not None
    assert fila["motivo_de_corte"] == "dejo_de_ser_administrador"
    cortes = _auditoria(conn, "cortar_sesion_de_administracion")
    assert len(cortes) == 1 and cortes[0]["actor_kind"] == "sistema"
    assert cortes[0]["detalle"]["motivo"] == "dejo_de_ser_administrador"
    # Devolverle el rol no revive la sesión: con el rol de nuevo, un enlace nuevo.
    _otorgar(conn, administradora)
    assert _vigente(conn, sesion) is None


# --- La credencial y el enlace de un solo uso ----------------------------------------------

def test_solo_se_guarda_el_hash_de_cada_token(conn, administradora):
    enlace = _emitir(conn, administradora)
    sesion_id, sesion = _canjear(conn, enlace)
    assert sesion_id
    with admin(conn) as cur:
        cur.execute("select * from enlace_de_administracion")
        enlaces = cur.fetchall()
        cur.execute("select * from sesion_de_administracion")
        sesiones = cur.fetchall()
    conn.commit()
    assert len(enlaces) == 1 and len(sesiones) == 1
    for fila in enlaces + sesiones:
        for columna, valor in fila.items():
            assert enlace not in str(valor), f"el enlace en claro apareció en {columna}"
            assert sesion not in str(valor), f"la sesión en claro apareció en {columna}"
    assert enlaces[0]["token_hash"] == _hash(enlace)
    assert sesiones[0]["token_hash"] == _hash(sesion)


def test_un_hash_mal_formado_no_se_guarda_ni_se_busca(conn, administradora):
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            cur.execute("select emitir_enlace_de_administracion(%s, 'no-es-un-hash', null)",
                        (administradora,))
    conn.commit()
    with sin_espacio(conn) as cur:
        cur.execute("select canjear_enlace_de_administracion('', %s) as id", (_hash("x"),))
        assert cur.fetchone()["id"] is None
        cur.execute("select count(*) n from sesion_de_administracion_vigente(null)")
        assert cur.fetchone()["n"] == 0
        cur.execute("select cerrar_sesion_de_administracion('zz') as cerrada")
        assert cur.fetchone()["cerrada"] is False
    conn.commit()


def test_el_enlace_abre_una_sesion_una_sola_vez(conn, administradora):
    enlace = _emitir(conn, administradora)
    primera, _ = _canjear(conn, enlace)
    segunda, reenviada = _canjear(conn, enlace)
    assert primera is not None
    assert segunda is None, "un enlace ya usado abrió otra sesión"
    assert _vigente(conn, reenviada) is None
    assert _contar(conn, "sesion_de_administracion") == 1


def test_un_enlace_nuevo_anula_el_que_estaba_sin_usar(conn, administradora):
    viejo = _emitir(conn, administradora)
    nuevo = _emitir(conn, administradora)
    assert _canjear(conn, viejo)[0] is None, "el enlace reemplazado todavía abre"
    assert _canjear(conn, nuevo)[0] is not None


def test_la_sesion_dice_quien_es_y_anota_su_ultimo_uso(conn, administradora):
    sesion_id, sesion = _entrar(conn, administradora)
    antes = _sesion(conn, sesion_id)["ultimo_uso_en"]
    fila = _vigente(conn, sesion)
    assert str(fila["sesion_id"]) == sesion_id
    assert str(fila["app_user_id"]) == administradora
    assert fila["nombre"] == "Morgan Hale 1"
    assert _sesion(conn, sesion_id)["ultimo_uso_en"] >= antes


def test_cerrar_la_sesion_la_corta_y_no_vuelve(conn, administradora):
    sesion_id, sesion = _entrar(conn, administradora)
    with sin_espacio(conn) as cur:
        cur.execute("select cerrar_sesion_de_administracion(%s) as cerrada", (_hash(sesion),))
        assert cur.fetchone()["cerrada"] is True
        cur.execute("select cerrar_sesion_de_administracion(%s) as cerrada", (_hash(sesion),))
        assert cur.fetchone()["cerrada"] is False
    conn.commit()
    assert _vigente(conn, sesion) is None
    assert _sesion(conn, sesion_id)["motivo_de_corte"] == "cerro_la_sesion"
    corte = _auditoria(conn, "cortar_sesion_de_administracion")
    assert len(corte) == 1 and corte[0]["actor_kind"] == "persona"
    assert str(corte[0]["actor_app_user_id"]) == administradora


def test_cortar_las_sesiones_de_un_administrador_corta_todas_y_anula_su_enlace(
        conn, intake_world, administradora):
    otro = _usuario(intake_world, "Morgan Hale", "west-studio")
    _otorgar(conn, otro)
    _, una = _entrar(conn, administradora)
    _, dos = _entrar(conn, administradora)
    _, del_otro = _entrar(conn, otro)
    sin_usar = _emitir(conn, administradora)
    with admin(conn) as cur:
        cur.execute("select cortar_sesiones_de_administrador(%s, 'perdio_el_celular', null) n",
                    (administradora,))
        assert cur.fetchone()["n"] == 2
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            cur.execute("select cortar_sesiones_de_administrador(%s, 'porque_si', null)",
                        (administradora,))
    conn.commit()
    assert _vigente(conn, una) is None and _vigente(conn, dos) is None
    assert _vigente(conn, del_otro) is not None
    assert _canjear(conn, sin_usar)[0] is None, "el enlace sin usar sobrevivió al corte"
    cortes = _auditoria(conn, "cortar_sesion_de_administracion")
    assert [c["detalle"]["motivo"] for c in cortes] == ["perdio_el_celular"] * 2
    assert all(c["actor_kind"] == "leda" for c in cortes)


# --- Las dos puertas ------------------------------------------------------------------------

def test_la_sesion_del_equipo_no_es_de_administracion_ni_al_reves(conn, intake_world,
                                                                  administradora):
    """Morgan es autoridad de su equipo y administradora de plataforma: cada puerta, su sesión."""
    equipo = secrets.token_urlsafe(32)
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        cur.execute("select emitir_enlace_de_entrada(%s, %s, null) as id",
                    (intake_world["north-lab"]["people"]["Morgan Hale"]["membership_id"],
                     _hash(equipo)))
    conn.commit()
    sesion_del_equipo = secrets.token_urlsafe(32)
    with sin_espacio(conn) as cur:
        # El enlace del equipo no se canjea por la puerta de administración...
        cur.execute("select canjear_enlace_de_administracion(%s, %s) as id",
                    (_hash(equipo), _hash(secrets.token_urlsafe(32))))
        assert cur.fetchone()["id"] is None
        cur.execute("select canjear_enlace_de_entrada(%s, %s) as id",
                    (_hash(equipo), _hash(sesion_del_equipo)))
        assert cur.fetchone()["id"] is not None
    conn.commit()
    _, de_administracion = _entrar(conn, administradora)
    with sin_espacio(conn) as cur:
        # ... ni una sesión vale en la otra puerta.
        cur.execute("select count(*) n from sesion_de_administracion_vigente(%s)",
                    (_hash(sesion_del_equipo),))
        assert cur.fetchone()["n"] == 0
        cur.execute("select count(*) n from sesion_vigente(%s)", (_hash(de_administracion),))
        assert cur.fetchone()["n"] == 0
    conn.commit()
    with admin(conn) as cur:
        administrador = secrets.token_urlsafe(32)
        cur.execute("select emitir_enlace_de_administracion(%s, %s, null)",
                    (administradora, _hash(administrador)))
    conn.commit()
    with sin_espacio(conn) as cur:
        cur.execute("select canjear_enlace_de_entrada(%s, %s) as id",
                    (_hash(administrador), _hash(secrets.token_urlsafe(32))))
        assert cur.fetchone()["id"] is None
    conn.commit()


# --- Auditoría ------------------------------------------------------------------------------

def test_emitir_canjear_y_cortar_quedan_en_la_auditoria_sin_espacio(conn, intake_world,
                                                                    administradora):
    with admin(conn) as cur:
        cur.execute("select set_config('leda.nucleo_hash', 'nucleo-de-prueba', false)")
    conn.commit()
    enlace = _emitir(conn, administradora)
    sesion_id, sesion = _canjear(conn, enlace)
    _revocar(conn, administradora)
    assert _vigente(conn, sesion) is None

    emitidos = _auditoria(conn, "emitir_enlace_de_administracion")
    canjes = _auditoria(conn, "canjear_enlace_de_administracion")
    cortes = _auditoria(conn, "cortar_sesion_de_administracion")
    assert len(emitidos) == len(canjes) == len(cortes) == 1
    for fila in emitidos + canjes + cortes:
        assert fila["workspace_id"] is None, "la puerta de administración no es de un espacio"
        assert fila["nucleo_hash"] == "nucleo-de-prueba"
        for valor in (enlace, sesion, _hash(enlace), _hash(sesion)):
            assert valor not in str(fila["detalle"]), "un token o su hash quedó en la auditoría"
    assert str(emitidos[0]["sujeto_id"]) == administradora
    assert emitidos[0]["actor_kind"] == "leda"
    assert canjes[0]["actor_kind"] == "persona"
    assert str(canjes[0]["actor_app_user_id"]) == administradora
    assert str(canjes[0]["sujeto_id"]) == sesion_id
    assert str(cortes[0]["sujeto_id"]) == sesion_id


def test_la_auditoria_no_toma_el_espacio_de_quien_llama(conn, intake_world, administradora):
    """Aunque la transacción tenga un espacio fijado, el hecho es de la plataforma."""
    _, sesion = _entrar(conn, administradora)
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        cur.execute("select cerrar_sesion_de_administracion(%s) as cerrada", (_hash(sesion),))
        assert cur.fetchone()["cerrada"] is True
        cur.execute("select current_setting('leda.workspace_id', true) ws")
        assert cur.fetchone()["ws"] == intake_world["north-lab"]["id"]
    conn.commit()
    corte = _auditoria(conn, "cortar_sesion_de_administracion")
    assert len(corte) == 1 and corte[0]["workspace_id"] is None


# --- La vuelta atrás ------------------------------------------------------------------------

def test_el_rollback_de_la_0061_se_niega_si_hay_enlaces_o_sesiones(conn, administradora):
    rollbacks = Path(__file__).resolve().parents[2] / "db" / "rollbacks"
    (archivo,) = rollbacks.glob("0061_*.sql")
    guarda = re.findall(r"do \$\$.*?end \$\$;", archivo.read_text("utf-8"), re.S)[-1]
    _entrar(conn, administradora)
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.RaiseException, match="0061 rollback refused"), \
                conn.transaction():
            cur.execute("set local search_path = leda, public")
            cur.execute(guarda)
        cur.execute("select count(*) n from sesion_de_administracion")
        assert cur.fetchone()["n"] == 1
    conn.commit()


# --- La entrada HTTP ------------------------------------------------------------------------

@pytest.fixture
def web(conn, monkeypatch):
    """Un navegador nuevo por llamada, con la conexión de la prueba."""
    from fastapi.testclient import TestClient

    from leda import entrada, web_app

    monkeypatch.setattr(web_app, "_conn_de_la_web", lambda: conn)

    def nuevo():
        return TestClient(entrada.app, base_url=BASE, follow_redirects=False)
    return nuevo


def _enlace_por_la_consola(conn, app_user_id: str) -> str:
    from leda import web_app

    with admin(conn) as cur:
        token = web_app.emitir_enlace_de_administracion(cur, app_user_id)
    conn.commit()
    assert token
    return token


def _navegador_de_administracion(web, conn, app_user_id: str):
    navegador = web()
    r = navegador.post(f"/app/admin/entrar/{_enlace_por_la_consola(conn, app_user_id)}")
    assert r.status_code == 303, r.text
    return navegador


def _navegador_del_equipo(web, conn, mundo: dict, nombre: str, slug: str = "north-lab"):
    from leda import web_app

    with espacio(conn, mundo[slug]["id"]) as cur:
        token = web_app.emitir_enlace(cur, mundo[slug]["people"][nombre]["membership_id"])
    conn.commit()
    navegador = web()
    assert navegador.post(f"/app/entrar/{token}").status_code == 303
    return navegador


def _tiene_las_cabeceras(r) -> None:
    for nombre, valor in CABECERAS.items():
        assert r.headers.get(nombre) == valor, nombre
    assert "frame-ancestors 'none'" in r.headers.get("content-security-policy", "")


def test_abrir_el_enlace_no_lo_gasta_y_muestra_el_boton(web, conn, administradora):
    token = _enlace_por_la_consola(conn, administradora)
    paginas = []
    for _ in range(2):
        r = web().get(f"/app/admin/entrar/{token}")
        assert r.status_code == 200 and "set-cookie" not in r.headers
        assert 'method="post"' in r.text and ">Entrar<" in r.text and token not in r.text
        politica = r.headers["content-security-policy"]
        assert "form-action 'self'" in politica and "script-src" not in politica
        assert r.headers["referrer-policy"] == "same-origin"
        assert r.headers["cache-control"] == "no-store"
        paginas.append(r.text)
    assert web().get("/app/admin/entrar/inventado").text == paginas[0]
    assert _contar(conn, "sesion_de_administracion") == 0
    assert web().post(f"/app/admin/entrar/{token}").status_code == 303


def test_el_boton_deja_la_cookie_propia_y_lleva_a_la_administracion(web, conn, administradora):
    token = _enlace_por_la_consola(conn, administradora)
    r = web().post(f"/app/admin/entrar/{token}", headers={"origin": BASE})
    assert r.status_code == 303 and r.headers["location"] == "/app/admin/"
    _tiene_las_cabeceras(r)
    cookie = r.headers["set-cookie"]
    partes = {p.strip().split("=")[0].lower(): p.strip() for p in cookie.split(";")}
    assert cookie.startswith("leda_admin=")
    assert "httponly" in partes and "secure" in partes
    assert partes["samesite"].lower() == "samesite=strict"
    assert partes["path"] == "Path=/app/admin"
    assert partes["max-age"] == f"Max-Age={CUATROCIENTOS_DIAS}"
    assert token not in cookie and _hash(token) not in cookie


def test_el_enlace_sirve_una_sola_vez_y_desde_otro_sitio_no_canjea(web, conn, administradora):
    token = _enlace_por_la_consola(conn, administradora)
    for origen in ("https://otro.example", "null"):
        r = web().post(f"/app/admin/entrar/{token}", headers={"origin": origen})
        assert r.status_code == 403 and "set-cookie" not in r.headers
    assert web().post(f"/app/admin/entrar/{token}").status_code == 303
    r = web().post(f"/app/admin/entrar/{token}")
    assert r.status_code == 404 and "ya no sirve" in r.text and "set-cookie" not in r.headers
    for de_la_cocina in ("traceback", "psycopg", "sesion_de_administracion", "error"):
        assert de_la_cocina not in r.text.lower()


def test_yo_dice_quien_es_y_todos_los_espacios(web, conn, intake_world, administradora):
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = navegador.get("/app/admin/api/yo")
    assert r.status_code == 200, r.text
    _tiene_las_cabeceras(r)
    datos = r.json()
    assert datos["administrador"] == "Morgan Hale 1"
    assert {(e["slug"], e["nombre"]) for e in datos["espacios"]} == {
        ("north-lab", "North Lab"), ("west-studio", "West Studio")}
    assert {e["id"] for e in datos["espacios"]} == {
        intake_world["north-lab"]["id"], intake_world["west-studio"]["id"]}
    assert "max-age=" in r.headers["set-cookie"].lower()


def test_sin_una_sesion_de_administracion_es_401(web, conn, administradora):
    assert web().get("/app/admin/api/yo").status_code == 401
    inventada = web()
    inventada.cookies.set("leda_admin", secrets.token_urlsafe(32), domain="testserver",
                          path="/app/admin")
    r = inventada.get("/app/admin/api/yo")
    assert r.status_code == 401 and r.json() == {"error": "sin_sesion"}
    _tiene_las_cabeceras(r)


def test_un_rol_revocado_cierra_la_puerta_en_el_pedido_siguiente(web, conn, administradora):
    navegador = _navegador_de_administracion(web, conn, administradora)
    assert navegador.get("/app/admin/api/yo").status_code == 200
    _revocar(conn, administradora)
    assert navegador.get("/app/admin/api/yo").status_code == 401
    assert _contar(conn, "sesion_de_administracion", "cortada_en is null") == 0


def test_la_cookie_del_equipo_no_abre_la_administracion(web, conn, intake_world, administradora):
    """Morgan es autoridad de North Lab y administradora: con la sesión del equipo, la
    administración no se abre (constitución §2)."""
    equipo = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    assert equipo.get("/app/api/yo").status_code == 200
    assert equipo.get("/app/admin/api/yo").status_code == 401
    # Ni con el token del equipo puesto en la cookie de la administración.
    token = equipo.cookies.get("leda_sesion")
    impostor = web()
    impostor.cookies.set("leda_admin", token, domain="testserver", path="/app/admin")
    assert impostor.get("/app/admin/api/yo").status_code == 401
    assert equipo.get("/app/api/yo").status_code == 200, "la sesión del equipo sigue abierta"


def test_la_cookie_de_administracion_no_abre_la_api_del_equipo(web, conn, administradora):
    navegador = _navegador_de_administracion(web, conn, administradora)
    assert navegador.get("/app/api/yo").status_code == 401
    token = navegador.cookies.get("leda_admin")
    impostor = web()
    impostor.cookies.set("leda_sesion", token, domain="testserver", path="/app")
    for camino in ("/app/api/yo", "/app/api/tareas?vista=tus"):
        assert impostor.get(camino).status_code == 401
    assert navegador.get("/app/admin/api/yo").status_code == 200


def test_las_dos_puertas_abiertas_a_la_vez_siguen_separadas(web, conn, intake_world,
                                                            administradora):
    navegador = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    r = navegador.post(f"/app/admin/entrar/{_enlace_por_la_consola(conn, administradora)}")
    assert r.status_code == 303
    assert navegador.get("/app/api/yo").json()["espacio"] == "North Lab"
    assert navegador.get("/app/admin/api/yo").json()["administrador"] == "Morgan Hale 1"
    # Salir de la administración no cierra la del equipo.
    assert navegador.post("/app/admin/salir").status_code == 204
    assert navegador.get("/app/admin/api/yo").status_code == 401
    assert navegador.get("/app/api/yo").status_code == 200


def test_salir_corta_la_sesion_y_borra_la_cookie(web, conn, administradora):
    navegador = _navegador_de_administracion(web, conn, administradora)
    assert navegador.post("/app/admin/salir",
                          headers={"origin": "https://otro.example"}).status_code == 403
    assert navegador.get("/app/admin/api/yo").status_code == 200
    r = navegador.post("/app/admin/salir")
    assert r.status_code == 204
    _tiene_las_cabeceras(r)
    cookie = r.headers["set-cookie"].lower()
    assert cookie.startswith("leda_admin=") and "path=/app/admin" in cookie
    assert 'leda_admin=""' in cookie or "max-age=0" in cookie
    cortes = _auditoria(conn, "cortar_sesion_de_administracion")
    assert [c["detalle"]["motivo"] for c in cortes] == ["cerro_la_sesion"]
    assert cortes[0]["nucleo_hash"]
    assert navegador.post("/app/admin/salir").status_code == 401


def test_ningun_token_en_las_respuestas_ni_en_la_consola_ni_en_la_auditoria(
        web, conn, administradora, capsys):
    enlace = _enlace_por_la_consola(conn, administradora)
    navegador = web()
    respuestas = [navegador.get(f"/app/admin/entrar/{enlace}"),
                  navegador.post(f"/app/admin/entrar/{enlace}")]
    sesion = navegador.cookies.get("leda_admin")
    assert sesion
    respuestas += [navegador.get("/app/admin/api/yo"),
                   navegador.post(f"/app/admin/entrar/{enlace}"),
                   navegador.post("/app/admin/salir")]
    salida = capsys.readouterr()
    for secreto in (enlace, _hash(enlace), _hash(sesion)):
        for r in respuestas:
            assert secreto not in r.text and secreto not in str(r.headers)
        assert secreto not in salida.out + salida.err
    for r in respuestas[2:]:
        assert sesion not in r.text
    with admin(conn) as cur:
        cur.execute("select coalesce(detalle::text, '') d from audit_log")
        auditoria = " ".join(f["d"] for f in cur.fetchall())
    conn.commit()
    for secreto in (enlace, sesion, _hash(enlace), _hash(sesion)):
        assert secreto not in auditoria


def test_si_la_base_falla_el_administrador_no_ve_nada_tecnico(web, conn, administradora,
                                                             monkeypatch, capsys):
    from leda import web_app

    navegador = _navegador_de_administracion(web, conn, administradora)

    def caida():
        raise psycopg.OperationalError("conexión rechazada por 10.0.0.1")
    monkeypatch.setattr(web_app, "_conn_de_la_web", caida)
    r = navegador.get("/app/admin/api/yo")
    assert r.status_code == 503 and r.json() == {"error": "no_disponible"}
    assert "10.0.0.1" not in capsys.readouterr().out
