"""La API interna de la plataforma web, la puerta del equipo (ADR 0022, decisiones 3, 4, 5, 11,
12, 13 y 18; porción 1, tarea P1-3; migraciones 0057 a 0059): la entrada HTTP sobre las
funciones de la base, con `TestClient` sobre `https` (la cookie es `Secure`) y sin red.

- **El enlace sirve una vez:** abrirlo no lo gasta (la vista previa de Telegram o de un correo lo
  abre antes que la persona): muestra una página con el botón "Entrar", igual para cualquier
  enlace. El botón lo canjea: deja la cookie de la sesión (`HttpOnly`, `Secure`,
  `SameSite=Strict`, sólo `/app`) y lleva a la web; usado, inventado o anulado, muestra siempre la
  misma página humana, sin detalles técnicos (constitución §10).
- **Quién ve qué** sale de la base y de la sesión, nunca del pedido (decisiones 11 y 13): cada
  puesto ve su vista; de una tarea ajena, un integrante ve lo que cuenta el informe al grupo
  (decisiones del usuario del 2026-10-12, 1, 5, 6 y 7; migración 0060): trabada con su cadena,
  y vencida recién cuando el atraso ya se habló, con la previsión si la hay; una vista que la
  persona no tiene se niega.
- **Lo que muestra cada vista** (decisión 18): el panel por estado, la semana del calendario del
  espacio, la barra de días hábiles de una tarea en curso, los días que quedan, la cadena de
  esperas de una tarea trabada, en árbol (la función de la 0059), las dos marcas de una tarea
  trabada y vencida, y las terminadas de los últimos 30 días (decisión 3 del usuario).
- **El chat con Leda** (decisión 8 del usuario): `/app/api/yo` da la dirección del bot del
  equipo si el pack la declara (`telegram.bot_usuario`); si no, nada.
- **Una sesión que no entra** (sin cookie, inventada, cortada, de alguien que dejó el equipo)
  recibe 401; salir corta la sesión.
- **Aislamiento entre espacios, tokens que no aparecen** en respuestas ni en la consola, y las
  cabeceras de la página de la tarea en todo `/app`.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import date, datetime, timedelta, timezone

import psycopg
import pytest

from leda.db import admin, espacio

from tests.garantias.test_quien_ve_que import (AHORA, ANTES, DESPUES,  # noqa: F401
                                               _bloqueo, _escalamiento, _persona, _prevision,
                                               _tarea, _terminada, _trabada_y_vencida, mundo)

BASE = "https://testserver"
CABECERAS = {"cache-control": "no-store", "referrer-policy": "no-referrer",
             "x-robots-tag": "noindex, nofollow", "x-content-type-options": "nosniff",
             "x-frame-options": "DENY"}


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@pytest.fixture
def web(conn, monkeypatch):
    """Un navegador nuevo por llamada, con la conexión de la prueba y el reloj de Leda fijo en
    `AHORA` (un jueves)."""
    from fastapi.testclient import TestClient

    from leda import entrada, web_app

    monkeypatch.setattr(web_app, "_conn_de_la_web", lambda: conn)
    monkeypatch.setattr(web_app, "_ahora", lambda _conn, _ws: AHORA)

    def nuevo():
        return TestClient(entrada.app, base_url=BASE, follow_redirects=False)
    return nuevo


def _enlace(conn, mundo: dict, nombre: str, slug: str = "north-lab") -> str:
    """Emite el enlace de entrada de una persona, como la consola, y devuelve el token."""
    from leda import web_app

    with espacio(conn, mundo[slug]["id"]) as cur:
        token = web_app.emitir_enlace(cur, _persona(mundo, nombre, slug))
    conn.commit()
    assert token
    return token


def _entrar(web, conn, mundo: dict, nombre: str, slug: str = "north-lab"):
    """Un navegador con la sesión de esa persona abierta."""
    navegador = web()
    r = navegador.post(f"/app/entrar/{_enlace(conn, mundo, nombre, slug)}")
    assert r.status_code == 303, r.text
    return navegador


def _tiene_las_cabeceras(r) -> None:
    for nombre, valor in CABECERAS.items():
        assert r.headers.get(nombre) == valor, nombre
    politica = r.headers.get("content-security-policy", "")
    assert "frame-ancestors 'none'" in politica
    assert "unsafe-eval" not in politica


def _vista(navegador, vista: str = "tus") -> dict:
    r = navegador.get("/app/api/tareas", params={"vista": vista})
    assert r.status_code == 200, r.text
    _tiene_las_cabeceras(r)
    return r.json()


def _por_titulo(datos: dict) -> dict[str, dict]:
    return {t["titulo"]: t for t in datos["tareas"]}


def _auditadas(conn, accion: str) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select actor_kind, detalle, nucleo_hash from audit_log where accion = %s",
                    (accion,))
        filas = cur.fetchall()
    conn.commit()
    return filas


# --- La función de la cadena (0059) -----------------------------------------------------------

def test_la_cadena_de_la_sesion_es_elevada_y_la_regla_no_la_llama_leda_app(conn):
    with admin(conn) as cur:
        for funcion, de_la_sesion in (("esperas_de_la_sesion", True),
                                      ("esperas_que_ve", False)):
            cur.execute(
                """select p.prosecdef, r.rolname dueno, p.proconfig,
                          has_function_privilege('leda_app', p.oid, 'execute') app,
                          exists (select 1 from aclexplode(coalesce(p.proacl,
                                    acldefault('f', p.proowner))) a
                                   where a.grantee = 0 and a.privilege_type = 'EXECUTE') publico
                     from pg_proc p
                     join pg_roles r on r.oid = p.proowner
                     join pg_namespace n on n.oid = p.pronamespace
                    where n.nspname = 'leda' and p.proname = %s""", (funcion,))
            filas = cur.fetchall()
            assert len(filas) == 1, funcion
            f = filas[0]
            assert f["dueno"] == "leda_owner" and not f["publico"], funcion
            assert "search_path=leda, public, pg_temp" in (f["proconfig"] or []), funcion
            assert f["prosecdef"] is de_la_sesion and f["app"] is de_la_sesion, funcion
    conn.commit()


def test_la_cadena_no_entra_sin_sesion_ni_con_una_vista_desconocida(conn, mundo):
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local role leda_app")
            cur.execute("select * from esperas_de_la_sesion(%s, 'equipo', %s)",
                        (_hash("inventado"), AHORA))
            assert cur.fetchall() == []
    with pytest.raises(psycopg.errors.RaiseException, match="vista desconocida"):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("set local role leda_app")
                cur.execute("select * from esperas_de_la_sesion(%s, 'todo', %s)",
                            (_hash("inventado"), AHORA))


# --- Entrar -----------------------------------------------------------------------------------

def _sesiones(conn) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from sesion_web")
        n = cur.fetchone()["n"]
    conn.commit()
    return n


def test_abrir_el_enlace_no_lo_gasta_y_muestra_el_boton_entrar(web, conn, mundo):
    """La vista previa de Telegram (o el revisor de un correo) abre el enlace antes que la
    persona: abrirlo, las veces que sea, no canjea nada."""
    token = _enlace(conn, mundo, "Sam North")
    for _ in range(2):
        r = web().get(f"/app/entrar/{token}")
        assert r.status_code == 200
        assert "set-cookie" not in r.headers
        assert 'method="post"' in r.text and ">Entrar<" in r.text and "Leda" in r.text
        assert token not in r.text
        politica = r.headers["content-security-policy"]
        assert "form-action 'self'" in politica and "script-src" not in politica
        assert "frame-ancestors 'none'" in politica
        assert r.headers["cache-control"] == "no-store"
        assert r.headers["x-frame-options"] == "DENY"
        # El botón manda el origen del sitio (con `no-referrer` el navegador mandaría "null"),
        # y la dirección con el token no sale nunca hacia otro sitio.
        assert r.headers["referrer-policy"] == "same-origin"
    assert _sesiones(conn) == 0
    assert _auditadas(conn, "canjear_enlace_de_entrada") == []
    assert web().post(f"/app/entrar/{token}").status_code == 303


@pytest.mark.parametrize("camino", ["/app/entrar/inventado", "/app/entrar/" + "x" * 300])
def test_abrir_cualquier_enlace_muestra_la_misma_pagina(web, conn, mundo, camino):
    """La página del botón no dice si el enlace sirve."""
    de_verdad = web().get(f"/app/entrar/{_enlace(conn, mundo, 'Sam North')}")
    r = web().get(camino)
    assert r.status_code == 200 and r.text == de_verdad.text


def test_el_boton_abre_la_sesion_con_la_cookie_y_lleva_a_la_web(web, conn, mundo):
    token = _enlace(conn, mundo, "Sam North")
    r = web().post(f"/app/entrar/{token}", headers={"origin": BASE})
    assert r.status_code == 303 and r.headers["location"] == "/app/"
    _tiene_las_cabeceras(r)
    cookie = r.headers["set-cookie"]
    partes = {p.strip().split("=")[0].lower(): p.strip() for p in cookie.split(";")}
    assert cookie.startswith("leda_sesion=")
    assert "httponly" in partes and "secure" in partes
    assert partes["samesite"].lower() == "samesite=strict"
    assert partes["path"] == "Path=/app"
    assert token not in cookie and _hash(token) not in cookie
    assert _auditadas(conn, "canjear_enlace_de_entrada")[0]["nucleo_hash"]
    assert _sesiones(conn) == 1


def test_el_enlace_sirve_una_sola_vez(web, conn, mundo):
    token = _enlace(conn, mundo, "Sam North")
    assert web().post(f"/app/entrar/{token}").status_code == 303
    r = web().post(f"/app/entrar/{token}")
    assert r.status_code == 404
    assert "ya no sirve" in r.text and "Leda" in r.text
    assert "set-cookie" not in r.headers
    _tiene_las_cabeceras(r)
    assert "script-src" not in r.headers["content-security-policy"]
    assert token not in r.text
    assert _sesiones(conn) == 1


@pytest.mark.parametrize("camino", ["/app/entrar/inventado", "/app/entrar/" + "x" * 300])
def test_un_enlace_inventado_muestra_la_misma_pagina(web, mundo, camino):
    r = web().post(camino)
    assert r.status_code == 404 and "ya no sirve" in r.text
    for de_la_cocina in ("traceback", "psycopg", "sesion_web", "enlace_de_entrada", "error"):
        assert de_la_cocina not in r.text.lower()


def test_el_boton_desde_otro_sitio_no_canjea_nada(web, conn, mundo):
    token = _enlace(conn, mundo, "Sam North")
    for origen in ("https://otro.example", "null"):
        r = web().post(f"/app/entrar/{token}", headers={"origin": origen})
        assert r.status_code == 403 and "set-cookie" not in r.headers
        _tiene_las_cabeceras(r)
    assert _sesiones(conn) == 0
    assert web().post(f"/app/entrar/{token}").status_code == 303


def test_un_enlace_anulado_por_otro_no_entra(web, conn, mundo):
    viejo = _enlace(conn, mundo, "Sam North")
    nuevo = _enlace(conn, mundo, "Sam North")
    assert web().post(f"/app/entrar/{viejo}").status_code == 404
    assert web().post(f"/app/entrar/{nuevo}").status_code == 303


# --- Quién es ---------------------------------------------------------------------------------

def test_yo_dice_quien_es_de_que_espacio_y_sus_vistas(web, conn, mundo):
    # Las pestañas (decisiones del usuario del 2026-10-14): Dirección no tiene sector; quien puede
    # pedir tiene "Mis pedidos"; el sector es "Mi equipo" (MA-3; el área va como dato aparte), y
    # lo de todo el equipo, de Dirección, "Mi área" (MA-4).
    esperado = {"Sam North": ["tus"], "Taylor Quinn": ["tus", "sector", "pedidas"],
                "Morgan Hale": ["tus", "equipo", "pedidas"]}
    for nombre, vistas in esperado.items():
        r = _entrar(web, conn, mundo, nombre).get("/app/api/yo")
        assert r.status_code == 200
        _tiene_las_cabeceras(r)
        datos = r.json()
        assert datos["persona"] == f"{nombre} 1" and datos["espacio"] == "North Lab"
        assert [v["vista"] for v in datos["vistas"]] == vistas
        # MA-4: arriba a la derecha, el nombre y debajo su área, la de la base.
        with admin(conn) as cur:
            cur.execute("""select a.nombre from membership m join area a on a.id = m.area_id
                            where m.id = %s""", (_persona(mundo, nombre),))
            assert datos["area"] == cur.fetchone()["nombre"]
    titulos = {v["vista"]: v["titulo"]
               for v in _entrar(web, conn, mundo, "Morgan Hale").get("/app/api/yo").json()["vistas"]}
    assert titulos == {"tus": "Mis tareas", "equipo": "Mi área", "pedidas": "Mis pedidos"}
    titulos = {v["vista"]: v["titulo"]
               for v in _entrar(web, conn, mundo, "Taylor Quinn").get("/app/api/yo").json()["vistas"]}
    assert titulos == {"tus": "Mis tareas", "sector": "Mi equipo", "pedidas": "Mis pedidos"}


def test_yo_renueva_la_cookie_sin_cambiar_la_sesion(web, conn, mundo):
    navegador = _entrar(web, conn, mundo, "Sam North")
    antes = navegador.cookies.get("leda_sesion")
    r = navegador.get("/app/api/yo")
    assert "max-age=" in r.headers["set-cookie"].lower()
    assert navegador.cookies.get("leda_sesion") == antes


def test_sin_una_sesion_que_entre_es_401(web, conn, mundo):
    assert web().get("/app/api/yo").status_code == 401
    inventada = web()
    inventada.cookies.set("leda_sesion", secrets.token_urlsafe(32), domain="testserver",
                          path="/app")
    for camino in ("/app/api/yo", "/app/api/tareas?vista=tus"):
        r = inventada.get(camino)
        assert r.status_code == 401 and r.json() == {"error": "sin_sesion"}
        _tiene_las_cabeceras(r)


def test_una_sesion_cortada_o_de_quien_dejo_el_equipo_no_entra(web, conn, mundo):
    from leda import web_app

    cortada = _entrar(web, conn, mundo, "Sam North")
    se_fue = _entrar(web, conn, mundo, "Sam Noble")
    with espacio(conn, mundo["north-lab"]["id"]) as cur:
        assert web_app.cortar_sesiones(cur, _persona(mundo, "Sam North")) == 1
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (_persona(mundo, "Sam Noble"),))
    conn.commit()
    for navegador in (cortada, se_fue):
        assert navegador.get("/app/api/yo").status_code == 401
        assert navegador.get("/app/api/tareas").status_code == 401


# --- Las vistas -------------------------------------------------------------------------------

def test_el_integrante_ve_lo_suyo_y_lo_ajeno_sin_un_atraso_que_no_se_hablo(web, conn, mundo):
    datos = _vista(_entrar(web, conn, mundo, "Sam North"))
    assert datos["vista"] == "tus" and datos["titulo"] == "Mis tareas"
    tareas = _por_titulo(datos)
    assert {t: f["papel"] for t, f in tareas.items()} == {
        "Pintar el galpón": "mia", "Medir el ruido": "mia", "Montar la línea": "mia",
        "Calibrar la balanza": "espero"}
    ajena = tareas["Calibrar la balanza"]
    # Venció el lunes, pero nadie lo habló con Sam Noble: su estado y su fecha, sin la marca.
    assert ajena["vencida"] is False and ajena["bloqueo_abierto"] is False
    assert ajena["esperas"] is None and ajena["responsable"] == "Sam Noble 1"
    assert ajena["marca"] == "en_curso" and ajena["marcas"] == ["en_curso"]
    assert ajena["fecha_objetivo"] == "2026-10-19" and ajena["prevision"] is None
    assert tareas["Pintar el galpón"]["vencida"] is True
    assert tareas["Pintar el galpón"]["marcas"] == ["vencida"]
    assert tareas["Medir el ruido"]["marcas"] == ["trabada"]
    assert tareas["Montar la línea"]["marca"] is None
    assert tareas["Montar la línea"]["marcas"] == []
    assert datos["panel"] == {"vencida": 1, "trabada": 1, "en_curso": 1, "entregada": 0}
    assert datos["activas"] == 4


def test_la_cadena_de_una_tarea_trabada_propia(web, conn, mundo):
    medir = _por_titulo(_vista(_entrar(web, conn, mundo, "Sam North")))["Medir el ruido"]
    assert medir["bloqueo_abierto"] is True
    assert medir["esperas"] == [{"que": "falta una pieza", "quien": "Sam Noble 1",
                                 "esperas": []}]


def test_quien_destraba_ve_la_tarea_que_lo_espera_trabada_con_su_cadena(web, conn, mundo):
    tareas = _por_titulo(_vista(_entrar(web, conn, mundo, "Sam Noble")))
    medir = tareas["Medir el ruido"]
    assert medir["papel"] == "me_esperan"
    assert medir["bloqueo_abierto"] is True and medir["vencida"] is False
    assert medir["marcas"] == ["trabada"]
    assert medir["esperas"] == [{"que": "falta una pieza", "quien": "Sam Noble 1",
                                 "esperas": []}]


def test_lo_que_espero_vencido_y_hablado_lleva_la_marca_y_la_prevision(web, conn, mundo):
    """Regla a del informe al grupo: Sam Noble dio un día posterior al vencimiento."""
    with admin(conn) as cur:
        _prevision(cur, mundo["north-lab"], mundo["t"]["calibrar"], "Sam Noble",
                   date(2026, 10, 28), ANTES)
    conn.commit()
    datos = _vista(_entrar(web, conn, mundo, "Sam North"))
    calibrar = _por_titulo(datos)["Calibrar la balanza"]
    assert calibrar["vencida"] is True and calibrar["marcas"] == ["vencida"]
    assert calibrar["prevision"] == "2026-10-28"
    assert calibrar["dias_de_atraso"] == 3
    assert datos["panel"]["vencida"] == 2


def test_trabada_y_vencida_lleva_las_dos_marcas(web, conn, mundo):
    """Decisión 5: las dos marcas en la tarjeta, y el panel la cuenta en las dos."""
    afinar = _trabada_y_vencida(conn, mundo)
    with admin(conn) as cur:
        _escalamiento(cur, mundo["north-lab"], afinar, "2026-10-19")
    conn.commit()
    datos = _vista(_entrar(web, conn, mundo, "Sam Noble"))
    fila = _por_titulo(datos)["Afinar el motor"]
    assert fila["marcas"] == ["trabada", "vencida"] and fila["marca"] == "trabada"
    assert fila["dias_de_atraso"] == 3
    # Trabadas: "Medir el ruido" y "Afinar el motor", las dos de Sam North que destraba.
    # Vencidas: las dos suyas ("Calibrar la balanza", "Auditar proveedores") y "Afinar".
    assert datos["panel"]["trabada"] == 2 and datos["panel"]["vencida"] == 3
    propia = _por_titulo(_vista(_entrar(web, conn, mundo, "Sam North")))["Afinar el motor"]
    assert propia["marcas"] == ["trabada", "vencida"]


def test_la_cadena_sigue_en_arbol_hasta_quien_puede_destrabar(web, conn, mundo):
    """Sam Noble destraba lo de Sam North y dijo que está trabado con "Calibrar la balanza", que
    espera un patrón que destraba Taylor Quinn: la cadena de "Medir el ruido" baja dos pasos."""
    norte, t = mundo["north-lab"], mundo["t"]
    with admin(conn) as cur:
        suyo, _ = _bloqueo(cur, norte, t["calibrar"], "Sam Noble", "Taylor Quinn")
        cur.execute("update blocker set causa = 'falta el patrón' where id = %s", (suyo,))
        cur.execute(
            """insert into dicho_de_quien_destraba (workspace_id, blocker_unblocker_id,
                                                    dicho_por_membership_id,
                                                    espera_su_bloqueo_id, at)
               values (%s, %s, %s, %s, %s)""",
            (norte["id"], t["destraba_medir"], _persona(mundo, "Sam Noble"), suyo, AHORA))
    conn.commit()
    cadena = [{"que": "Calibrar la balanza", "quien": "Sam Noble 1",
               "esperas": [{"que": "falta el patrón", "quien": "Taylor Quinn 1",
                            "esperas": []}]}]
    assert _por_titulo(_vista(_entrar(web, conn, mundo, "Sam North")))[
        "Medir el ruido"]["esperas"] == cadena
    equipo = _por_titulo(_vista(_entrar(web, conn, mundo, "Morgan Hale"), "equipo"))
    assert equipo["Medir el ruido"]["esperas"] == cadena
    assert equipo["Calibrar la balanza"]["esperas"] == [
        {"que": "falta el patrón", "quien": "Taylor Quinn 1", "esperas": []}]
    # Sam North, que espera "Calibrar la balanza", ve que está trabada y su cadena (decisiones
    # 6 y 7 del usuario, 2026-10-12).
    calibrar = _por_titulo(_vista(_entrar(web, conn, mundo, "Sam North")))["Calibrar la balanza"]
    assert calibrar["bloqueo_abierto"] is True
    assert calibrar["esperas"] == [{"que": "falta el patrón", "quien": "Taylor Quinn 1",
                                    "esperas": []}]


def test_una_cadena_que_da_vueltas_se_corta(web, conn, mundo):
    """La base no deja una dependencia en ciclo, pero lo dicho sí puede cerrar una vuelta:
    "Montar la línea" depende de "Calibrar la balanza", y Sam Noble se trabó con "Calibrar" y
    lo destraba Sam North, que dijo estar trabado con "Montar"."""
    norte, t = mundo["north-lab"], mundo["t"]
    with admin(conn) as cur:
        de_montar, _ = _bloqueo(cur, norte, t["montar"], "Sam North", "Taylor Quinn")
        _, destraba_calibrar = _bloqueo(cur, norte, t["calibrar"], "Sam Noble", "Sam North")
        cur.execute(
            """insert into dicho_de_quien_destraba (workspace_id, blocker_unblocker_id,
                                                    dicho_por_membership_id,
                                                    espera_su_bloqueo_id, at)
               values (%s, %s, %s, %s, %s)""",
            (norte["id"], destraba_calibrar, _persona(mundo, "Sam North"), de_montar, AHORA))
    conn.commit()
    equipo = _por_titulo(_vista(_entrar(web, conn, mundo, "Morgan Hale"), "equipo"))
    pieza = {"que": "falta una pieza", "quien": "Taylor Quinn 1", "esperas": []}
    # Cada tarea, una sola vez por rama: al volver a la de arriba, no se abre otra vez.
    assert equipo["Montar la línea"]["esperas"] == [
        {"que": "Calibrar la balanza", "quien": "Sam Noble 1",
         "esperas": [{"que": "Montar la línea", "quien": "Sam North 1", "esperas": []}]},
        pieza]
    assert equipo["Calibrar la balanza"]["esperas"] == [
        {"que": "Montar la línea", "quien": "Sam North 1",
         "esperas": [{"que": "Calibrar la balanza", "quien": "Sam Noble 1", "esperas": []},
                     pieza]}]


def test_el_referente_ve_su_sector_con_atrasos_y_bloqueos(web, conn, mundo):
    navegador = _entrar(web, conn, mundo, "Taylor Quinn")
    datos = _vista(navegador, "sector")
    tareas = _por_titulo(datos)
    assert datos["titulo"] == "Mi equipo" and datos["area_del_equipo"] == "Field Services"
    # "Mi equipo" es su gente (MA-3): su propia tarea, "Ordenar el depósito", queda en "Mis
    # tareas" y no se repite acá.
    assert set(tareas) == {"Pintar el galpón", "Medir el ruido", "Montar la línea"}
    suyas = _por_titulo(_vista(navegador, "tus"))
    assert suyas["Ordenar el depósito"]["papel"] == "mia"
    assert tareas["Pintar el galpón"]["vencida"] is True
    assert tareas["Medir el ruido"]["bloqueo_abierto"] is True
    assert tareas["Medir el ruido"]["esperas"][0]["que"] == "falta una pieza"
    r = navegador.get("/app/api/tareas", params={"vista": "equipo"})
    assert r.status_code == 403 and r.json() == {"error": "vista_no_disponible"}
    _tiene_las_cabeceras(r)


def test_la_autoridad_ve_el_equipo_y_nada_de_otro_espacio(web, conn, mundo):
    datos = _vista(_entrar(web, conn, mundo, "Morgan Hale"), "equipo")
    tareas = _por_titulo(datos)
    assert set(tareas) == {"Pintar el galpón", "Medir el ruido", "Montar la línea",
                           "Calibrar la balanza", "Auditar proveedores", "Ordenar el depósito"}
    assert tareas["Auditar proveedores"]["vencida"] is True
    assert datos["titulo"] == "Mi área"
    assert datos["panel"] == {"vencida": 3, "trabada": 1, "en_curso": 0, "entregada": 0}


def test_una_vista_desconocida_o_ajena_no_es_un_error_del_servidor(web, conn, mundo):
    navegador = _entrar(web, conn, mundo, "Sam North")
    r = navegador.get("/app/api/tareas", params={"vista": "todo"})
    assert r.status_code == 404 and r.json() == {"error": "vista_desconocida"}
    _tiene_las_cabeceras(r)
    for vista in ("sector", "equipo"):
        assert navegador.get("/app/api/tareas", params={"vista": vista}).status_code == 403


def test_el_pedido_no_elige_persona_ni_espacio(web, conn, mundo):
    navegador = _entrar(web, conn, mundo, "Sam North")
    oeste = mundo["west-studio"]
    sin_nada = _vista(navegador)
    r = navegador.get("/app/api/tareas", params={
        "vista": "tus", "workspace_id": oeste["id"],
        "membership_id": _persona(mundo, "Morgan Hale"), "persona": "Morgan Hale 1"})
    assert r.json()["tareas"] == sin_nada["tareas"]
    assert navegador.get("/app/api/yo", params={"membership_id": _persona(
        mundo, "Morgan Hale")}).json()["persona"] == "Sam North 1"


def test_aislamiento_entre_espacios(web, conn, mundo):
    oeste = _vista(_entrar(web, conn, mundo, "Sam North", "west-studio"))
    assert set(_por_titulo(oeste)) == {"Galpón del oeste"}
    yo = _entrar(web, conn, mundo, "Morgan Hale", "west-studio").get("/app/api/yo").json()
    assert yo["espacio"] == "West Studio" and yo["persona"] == "Morgan Hale 2"
    with admin(conn) as cur:
        cur.execute("""select a.nombre from membership m join area a on a.id = m.area_id
                        where m.id = %s""",
                    (_persona(mundo, "Morgan Hale", "west-studio"),))
        assert yo["area"] == cur.fetchone()["nombre"]
    equipo_oeste = _por_titulo(_vista(_entrar(web, conn, mundo, "Morgan Hale", "west-studio"),
                                      "equipo"))
    assert set(equipo_oeste) == {"Secreto del oeste", "Galpón del oeste"}
    norte = _por_titulo(_vista(_entrar(web, conn, mundo, "Morgan Hale"), "equipo"))
    assert not {"Secreto del oeste", "Galpón del oeste"} & set(norte)


# --- La semana, la barra y los días que quedan ------------------------------------------------

def test_la_semana_los_dias_que_quedan_y_la_barra(web, conn, mundo):
    with admin(conn) as cur:
        # En curso, asignada el lunes 12/10 y para el martes 27/10.
        _tarea(cur, mundo["north-lab"], "Cablear el tablero", "Sam North", "field", "en_curso",
               datetime(2026, 10, 27, 20, 0, tzinfo=timezone.utc))
    conn.commit()
    datos = _vista(_entrar(web, conn, mundo, "Sam North"))
    assert datos["hoy"] == "2026-10-22" and datos["semana_iso"] == 43
    assert [(d["fecha"], d["dia"], d["hoy"], d["vence_algo"]) for d in datos["semana"]] == [
        ("2026-10-19", "lun", False, True),     # vencían "Pintar" y "Calibrar"
        ("2026-10-20", "mar", False, False),
        ("2026-10-21", "mié", False, False),
        ("2026-10-22", "jue", True, False),
        ("2026-10-23", "vie", False, False)]
    assert all(d["habil"] for d in datos["semana"])
    tareas = _por_titulo(datos)
    cablear = tareas["Cablear el tablero"]
    assert cablear["fecha_objetivo"] == "2026-10-27" and cablear["asignada_el"] == "2026-10-12"
    assert cablear["quedan_dias_habiles"] == 3          # viernes, lunes y martes
    momentos = [s["momento"] for s in cablear["barra"]]
    assert momentos == ["pasado"] * 8 + ["hoy"] + ["futuro"] * 3
    assert cablear["barra"][0]["fecha"] == "2026-10-12"
    assert cablear["barra"][-1]["fecha"] == "2026-10-27"
    # Lo que ya venció no cuenta días (para quien no ve su atraso, tampoco por la cuenta).
    assert tareas["Pintar el galpón"]["quedan_dias_habiles"] is None
    assert tareas["Calibrar la balanza"]["quedan_dias_habiles"] is None
    assert tareas["Montar la línea"]["quedan_dias_habiles"] == 6
    assert tareas["Montar la línea"]["barra"] is None   # no está en curso


def test_los_dias_de_atraso_solo_para_quien_ve_el_atraso(web, conn, mundo):
    """El "[VENCIDA +3d]" de la tarjeta: días hábiles desde la fecha, sólo si la base mostró el
    atraso a esta persona."""
    tareas = _por_titulo(_vista(_entrar(web, conn, mundo, "Sam North")))
    assert tareas["Pintar el galpón"]["dias_de_atraso"] == 3     # el lunes 19; hoy, jueves 22
    # Ajena y sin hablar: su atraso no se ve.
    assert tareas["Calibrar la balanza"]["dias_de_atraso"] is None
    assert tareas["Montar la línea"]["dias_de_atraso"] is None       # no venció
    sector = _por_titulo(_vista(_entrar(web, conn, mundo, "Taylor Quinn"), "sector"))
    assert sector["Pintar el galpón"]["dias_de_atraso"] == 3


def test_un_feriado_no_es_un_segmento_de_la_barra(web, conn, mundo):
    with admin(conn) as cur:
        cur.execute("insert into holiday (workspace_id, fecha, nombre) values (%s, %s, 'Feriado')",
                    (mundo["north-lab"]["id"], "2026-10-23"))
        _tarea(cur, mundo["north-lab"], "Cablear el tablero", "Sam North", "field", "en_curso",
               datetime(2026, 10, 27, 20, 0, tzinfo=timezone.utc))
    conn.commit()
    datos = _vista(_entrar(web, conn, mundo, "Sam North"))
    viernes = next(d for d in datos["semana"] if d["fecha"] == "2026-10-23")
    assert viernes["habil"] is False
    cablear = _por_titulo(datos)["Cablear el tablero"]
    assert "2026-10-23" not in [s["fecha"] for s in cablear["barra"]]
    assert cablear["quedan_dias_habiles"] == 2


# --- Las terminadas de los últimos 30 días ----------------------------------------------------

def test_las_terminadas_van_aparte_con_quien_las_hizo(web, conn, mundo):
    with admin(conn) as cur:
        _terminada(cur, mundo["north-lab"], "Cerrar el tablero", "Sam North", "field",
                   AHORA - timedelta(days=2))
        _terminada(cur, mundo["north-lab"], "Pesar la carga", "Sam Noble", "quality",
                   AHORA - timedelta(days=31))
    conn.commit()
    datos = _vista(_entrar(web, conn, mundo, "Sam North"))
    assert datos["terminadas"] == [{"id": datos["terminadas"][0]["id"],
                                    "titulo": "Cerrar el tablero", "responsable": "Sam North 1",
                                    "area": "Field Services", "terminada_el": "2026-10-20"}]
    # Las abiertas, el panel y la cuenta de activas siguen siendo sólo las abiertas.
    assert "Cerrar el tablero" not in _por_titulo(datos) and datos["activas"] == 4
    equipo = _vista(_entrar(web, conn, mundo, "Morgan Hale"), "equipo")
    assert [t["titulo"] for t in equipo["terminadas"]] == ["Cerrar el tablero"]
    oeste = _vista(_entrar(web, conn, mundo, "Morgan Hale", "west-studio"), "equipo")
    assert oeste["terminadas"] == []


# --- El chat con Leda -------------------------------------------------------------------------

def _bot(conn, mundo: dict, valor: str | None, slug: str = "north-lab") -> None:
    with admin(conn) as cur:
        cur.execute("delete from workspace_setting where workspace_id = %s and clave = %s",
                    (mundo[slug]["id"], "bot_usuario"))
        if valor is not None:
            cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                           values (%s, 'bot_usuario', to_jsonb(%s::text))""",
                        (mundo[slug]["id"], valor))
    conn.commit()


def test_yo_da_el_chat_del_bot_del_equipo_si_el_espacio_lo_tiene(web, conn, mundo):
    _bot(conn, mundo, "LedaNorteBot")
    yo = _entrar(web, conn, mundo, "Sam North").get("/app/api/yo").json()
    assert yo["chat_con_leda"] == "https://t.me/LedaNorteBot"
    # Cada espacio, el suyo: el oeste no declaró ninguno.
    oeste = _entrar(web, conn, mundo, "Sam North", "west-studio").get("/app/api/yo").json()
    assert oeste["chat_con_leda"] is None


def test_un_usuario_de_bot_que_no_es_valido_no_entra_en_la_base(conn, mundo):
    for malo in ("no vale", "a/../b", "x", "https://t.me/otro", "ab_c"):
        with pytest.raises(psycopg.errors.CheckViolation):
            _bot(conn, mundo, malo)
        conn.rollback()
    with pytest.raises(psycopg.errors.CheckViolation):
        with admin(conn) as cur:
            cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                           values (%s, 'bot_usuario', '42'::jsonb)""",
                        (mundo["north-lab"]["id"],))
    conn.rollback()


def _importar_corework(conn, tmp_path, monkeypatch, bot):
    """Importa CoreWork con `telegram.bot_usuario` (o sin él, con `None`) y devuelve el
    resultado y lo guardado."""
    import yaml

    from leda.importador import importar
    from tests.conftest import RAIZ

    monkeypatch.setenv("LEDA_BOT_TOKEN_COREWORK", "prueba:token")
    pack = yaml.safe_load((RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    pack["telegram"]["grupo_gestion_id"] = -1001
    pack["telegram"].pop("bot_usuario", None)
    if bot is not None:
        pack["telegram"]["bot_usuario"] = bot
    ruta = tmp_path / "corework.yaml"
    ruta.write_text(yaml.safe_dump(pack, allow_unicode=True), "utf-8")
    r = importar(conn, ruta)
    with admin(conn) as cur:
        cur.execute("""select valor #>> '{}' v from workspace_setting
                        where workspace_id = %s and clave = 'bot_usuario'""", (r.workspace_id,))
        fila = cur.fetchone()
    conn.commit()
    return r, (fila["v"] if fila else None)


def test_el_pack_declara_el_usuario_del_bot_y_se_puede_sacar(conn, tmp_path, monkeypatch):
    _, guardado = _importar_corework(conn, tmp_path, monkeypatch, "@CoreWorkLedaBot")
    assert guardado == "CoreWorkLedaBot"
    _, guardado = _importar_corework(conn, tmp_path, monkeypatch, None)
    assert guardado is None


def test_un_usuario_del_bot_mal_escrito_en_el_pack_avisa_y_no_se_guarda(
        conn, tmp_path, monkeypatch):
    r, guardado = _importar_corework(conn, tmp_path, monkeypatch, "t.me/CoreWorkLedaBot")
    assert guardado is None
    assert any("usuario del bot" in a for a in r.advertencias)


# --- Salir ------------------------------------------------------------------------------------

def test_salir_corta_la_sesion_y_borra_la_cookie(web, conn, mundo):
    navegador = _entrar(web, conn, mundo, "Sam North")
    r = navegador.post("/app/salir")
    assert r.status_code == 204
    _tiene_las_cabeceras(r)
    assert 'leda_sesion=""' in r.headers["set-cookie"] or "max-age=0" in r.headers[
        "set-cookie"].lower()
    cortes = _auditadas(conn, "cortar_sesion_web")
    assert [c["detalle"]["motivo"] for c in cortes] == ["cerro_la_sesion"]
    assert cortes[0]["actor_kind"] == "persona" and cortes[0]["nucleo_hash"]
    assert navegador.post("/app/salir").status_code == 401
    with admin(conn) as cur:
        cur.execute("select count(*) n from sesion_web where cortada_en is null")
        assert cur.fetchone()["n"] == 0
    conn.commit()


def test_salir_desde_otro_sitio_no_corta_nada(web, conn, mundo):
    navegador = _entrar(web, conn, mundo, "Sam North")
    r = navegador.post("/app/salir", headers={"origin": "https://otro.example"})
    assert r.status_code == 403
    assert navegador.get("/app/api/yo").status_code == 200


# --- Tokens, consola y fallas -----------------------------------------------------------------

def test_ningun_token_en_las_respuestas_ni_en_la_consola_ni_en_la_auditoria(
        web, conn, mundo, capsys):
    enlace = _enlace(conn, mundo, "Taylor Quinn")
    navegador = web()
    respuestas = [navegador.get(f"/app/entrar/{enlace}"), navegador.post(f"/app/entrar/{enlace}")]
    sesion = navegador.cookies.get("leda_sesion")
    assert sesion
    respuestas += [navegador.get("/app/api/yo"), navegador.get("/app/api/tareas?vista=sector"),
                   navegador.post(f"/app/entrar/{enlace}"), navegador.post("/app/salir")]
    salida = capsys.readouterr()
    for secreto in (enlace, _hash(enlace), _hash(sesion)):
        for r in respuestas:
            assert secreto not in r.text
            assert secreto not in str(r.headers)
        assert secreto not in salida.out + salida.err
    for r in respuestas[2:]:
        assert sesion not in r.text
    with admin(conn) as cur:
        cur.execute("select detalle::text d from audit_log")
        auditoria = " ".join(f["d"] for f in cur.fetchall())
    conn.commit()
    for secreto in (enlace, sesion, _hash(enlace), _hash(sesion)):
        assert secreto not in auditoria


def test_si_la_base_falla_la_persona_no_ve_nada_tecnico(web, conn, mundo, monkeypatch, capsys):
    from leda import web_app

    navegador = _entrar(web, conn, mundo, "Sam North")

    def caida():
        raise psycopg.OperationalError("conexión rechazada por 10.0.0.1")
    monkeypatch.setattr(web_app, "_conn_de_la_web", caida)
    r = navegador.get("/app/api/tareas")
    assert r.status_code == 503 and r.json() == {"error": "no_disponible"}
    _tiene_las_cabeceras(r)
    assert "10.0.0.1" not in capsys.readouterr().out


# --- MA-3: "Mi equipo" y "Sin empezar" (prueba del usuario en el iPhone) ------------------------

def test_mi_equipo_no_aparece_si_el_referente_no_tiene_a_nadie_a_cargo(web, conn, mundo):
    """Sin nadie activo en sus áreas, "Mi equipo" quedaría vacía o con sus propias tareas: no hay
    pestaña, y la vista se niega."""
    taylor = _persona(mundo, "Taylor Quinn")
    with admin(conn) as cur:
        cur.execute("""update membership set activo = false
                        where workspace_id = %s and id <> %s
                          and area_id in (select id from area where referente_membership_id = %s)""",
                    (mundo["north-lab"]["id"], taylor, taylor))
    conn.commit()
    navegador = _entrar(web, conn, mundo, "Taylor Quinn")
    vistas = [v["vista"] for v in navegador.get("/app/api/yo").json()["vistas"]]
    assert "sector" not in vistas and vistas[0] == "tus"
    r = navegador.get("/app/api/tareas", params={"vista": "sector"})
    assert r.status_code == 403 and r.json() == {"error": "vista_no_disponible"}


def test_sin_empezar_cuenta_las_asignadas_que_nadie_empezo(web, conn, mundo):
    for nombre, vista in (("Morgan Hale", "equipo"), ("Taylor Quinn", "sector"),
                          ("Sam North", "tus")):
        datos = _vista(_entrar(web, conn, mundo, nombre), vista)
        assert datos["sin_empezar"] == sum(1 for t in datos["tareas"] if t["estado"] == "asignada")
    datos = _vista(_entrar(web, conn, mundo, "Morgan Hale"), "equipo")
    assert datos["sin_empezar"] > 0, "el mundo de la prueba tiene alguna sin empezar"

