"""Ver el equipo (migración 0082; J7-3 de `odd/tasks/plataforma-jerarquias.md`; ADR 0023, decisiones 4
y 5): la capa de garantías, en la base y en la entrada HTTP. Nada cambia el equipo todavía.

- **Quién lo ve:** Dirección (el rol con la autoridad final), por la puerta del equipo, sólo el suyo;
  el administrador de plataforma, por su puerta, el de cualquier espacio. Un referente o un
  integrante, no (403), aunque la web le esconda el botón.
- **Lo ven funciones de la base** (`equipo_de` y `cambios_del_equipo`, `security definer` de
  `leda_owner`, sólo para `leda_app`): comprueban la sesión de la puerta en cada llamada
  (`quien_organiza_el_equipo`) y fijan ellas mismas el espacio, así que la RLS no deja ver otro.
- **Qué ven:** las áreas (con su referente, si declararon la autoaprobación, su gente, cuántas
  tareas abiertas tienen y si están archivadas), las personas (área, rol, quién las aprueba, si
  siguen en el equipo y si conectaron Leda: «sin conectar»), los roles, los problemas del equipo
  (`problemas_del_equipo`) y la historia de `cambio_del_equipo`, lo más nuevo primero.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

import psycopg
import pytest
from psycopg.types.json import Jsonb

from leda.db import admin, espacio
from tests.garantias.test_carga_de_tareas import (  # noqa: F401 -- `administradora`, `sesion`
    _hash,                                         # y `web` son las fixtures
    _navegador_de_administracion,
    _navegador_del_equipo,
    administradora,
    sesion,
    sin_espacio,
    web,
)

FUNCIONES_DE_LA_WEB = ("equipo_de", "cambios_del_equipo")

EQUIPO = "/app/api/equipo"
INVENTADO = "00000000-0000-4000-8000-000000000000"


def _admin_del_equipo(espacio_id: str) -> str:
    return f"/app/admin/api/espacios/{espacio_id}/equipo"


# --- Ayudas ---------------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _referente_de_field(request):
    """Taylor Quinn es la referente de Field Services en los dos espacios."""
    if "intake_world" not in request.fixturenames:
        return
    mundo, conn = request.getfixturevalue("intake_world"), request.getfixturevalue("conn")
    with admin(conn) as cur:
        for datos in mundo.values():
            cur.execute("update area set referente_membership_id = %s where id = %s",
                        (datos["people"]["Taylor Quinn"]["membership_id"], datos["areas"]["field"]))
    conn.commit()


def _persona(mundo: dict, nombre: str, slug: str = "north-lab") -> str:
    return mundo[slug]["people"][nombre]["membership_id"]


def _sesion_del_equipo(conn, mundo: dict, nombre: str, slug: str = "north-lab") -> str:
    """Abre una sesión de la puerta del equipo y devuelve su token en claro."""
    enlace, equipo = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    with espacio(conn, mundo[slug]["id"]) as cur:
        cur.execute("select emitir_enlace_de_entrada(%s, %s, null)",
                    (_persona(mundo, nombre, slug), _hash(enlace)))
    conn.commit()
    with sin_espacio(conn) as cur:
        cur.execute("select canjear_enlace_de_entrada(%s, %s) as id",
                    (_hash(enlace), _hash(equipo)))
        assert cur.fetchone()["id"]
    conn.commit()
    return equipo


def _llamar(conn, funcion: str, puerta: str, token: str, espacio_id: str | None) -> dict:
    with sin_espacio(conn) as cur:
        cur.execute(f"select {funcion}(%s, %s, %s) as r", (puerta, _hash(token), espacio_id))
        r = cur.fetchone()["r"]
    conn.commit()
    return r


def _errores(resultado: dict) -> set[tuple[str, str]]:
    assert resultado["ok"] is False, resultado
    return {(e["campo"], e["motivo"]) for e in resultado["errores"]}


def _cambio(conn, ws: str, *, clase: str, at: datetime, quien_app_user: str,
            quien_membership: str | None, antes=None, despues=None) -> str:
    with admin(conn) as cur:
        cur.execute(
            """insert into cambio_del_equipo
                 (workspace_id, clase, puerta, hecho_por_app_user_id, hecho_por_membership_id,
                  antes, despues, clave, huella, at)
               values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) returning id""",
            (ws, clase, "equipo" if quien_membership else "administracion", quien_app_user,
             quien_membership, Jsonb(antes) if antes is not None else None,
             Jsonb(despues) if despues is not None else None,
             secrets.token_urlsafe(18), secrets.token_hex(32), at))
        cambio = str(cur.fetchone()["id"])
    conn.commit()
    return cambio


# --- Las funciones ----------------------------------------------------------------------------

def test_las_funciones_son_elevadas_y_las_ejecuta_solo_la_web(conn):
    with admin(conn) as cur:
        cur.execute(
            """select p.proname, r.rolname, p.prosecdef, p.proconfig,
                      has_function_privilege('public', p.oid, 'execute') as de_public,
                      has_function_privilege('leda_app', p.oid, 'execute') as de_app,
                      has_function_privilege('leda_gateway', p.oid, 'execute') as de_gateway
                 from pg_proc p join pg_roles r on r.oid = p.proowner
                 join pg_namespace n on n.oid = p.pronamespace
                where n.nspname = 'leda' and p.proname = any(%s)""",
            (list(FUNCIONES_DE_LA_WEB) + ["quien_organiza_el_equipo"],))
        filas = {f["proname"]: f for f in cur.fetchall()}
    conn.commit()
    assert set(filas) == set(FUNCIONES_DE_LA_WEB) | {"quien_organiza_el_equipo"}
    for nombre, f in filas.items():
        assert f["rolname"] == "leda_owner", nombre
        assert any(c.startswith("search_path=") and c.endswith("pg_temp")
                   for c in f["proconfig"] or []), nombre
        assert not f["de_public"] and not f["de_gateway"], nombre
    for nombre in FUNCIONES_DE_LA_WEB:
        assert filas[nombre]["prosecdef"] and filas[nombre]["de_app"], nombre
    # Quién organiza se resuelve adentro de las dos: la web no la llama sola.
    assert not filas["quien_organiza_el_equipo"]["de_app"]
    assert not filas["quien_organiza_el_equipo"]["prosecdef"]


def test_la_aplicacion_sigue_sin_leer_los_cambios_del_equipo_directo(conn, intake_world):
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute("select * from cambio_del_equipo")
    conn.commit()


def test_quien_lo_ve_en_la_base(conn, intake_world, sesion):
    norte, oeste = intake_world["north-lab"], intake_world["west-studio"]
    direccion = _sesion_del_equipo(conn, intake_world, "Morgan Hale")
    for funcion in FUNCIONES_DE_LA_WEB:
        assert _llamar(conn, funcion, "equipo", direccion, None)["ok"] is True
        assert _llamar(conn, funcion, "equipo", direccion, norte["id"])["ok"] is True
        # Otro espacio no existe para Dirección, aunque lo nombre.
        assert _errores(_llamar(conn, funcion, "equipo", direccion, oeste["id"])) == {
            ("espacio", "no_existe")}
        for nombre in ("Taylor Quinn", "Sam North"):
            token = _sesion_del_equipo(conn, intake_world, nombre)
            assert _errores(_llamar(conn, funcion, "equipo", token, None)) == {
                ("sesion", "sin_autoridad")}
        # El administrador de plataforma, en cualquier espacio; uno que no existe, no.
        assert _llamar(conn, funcion, "administracion", sesion, oeste["id"])["ok"] is True
        assert _errores(_llamar(conn, funcion, "administracion", sesion, INVENTADO)) == {
            ("espacio", "no_existe")}
        # Sin sesión, o con la de la otra puerta, nada.
        assert _errores(_llamar(conn, funcion, "administracion", direccion, norte["id"])) == {
            ("sesion", "sin_sesion")}
        assert _errores(_llamar(conn, funcion, "equipo", "inventado", None)) == {
            ("sesion", "sin_sesion")}
        assert _errores(_llamar(conn, funcion, "otra", sesion, norte["id"])) == {
            ("sesion", "sin_sesion")}


def test_el_espacio_fijado_antes_se_respeta_al_salir(conn, intake_world, sesion):
    oeste = intake_world["west-studio"]
    with sin_espacio(conn) as cur:
        cur.execute("select set_config('leda.workspace_id', '', true)")
        cur.execute("select equipo_de('administracion', %s, %s) as r", (_hash(sesion), oeste["id"]))
        assert cur.fetchone()["r"]["ok"] is True
        cur.execute("select current_setting('leda.workspace_id', true) as ws")
        assert cur.fetchone()["ws"] == ""
    conn.commit()


# --- La entrada HTTP: quién entra ----------------------------------------------------------------

def test_direccion_ve_su_equipo(conn, intake_world, web):
    navegador = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    respuesta = navegador.get(EQUIPO)
    assert respuesta.status_code == 200, respuesta.text
    datos = respuesta.json()
    assert set(datos) == {"espacio", "areas", "personas", "roles", "problemas", "cambios",
                          "tipos_de_evidencia"}
    assert datos["espacio"] == {"id": intake_world["north-lab"]["id"], "nombre": "North Lab"}
    assert [a["nombre"] for a in datos["areas"]] == ["Field Services", "Quality Guild"]
    field = datos["areas"][0]
    assert set(field) == {"id", "slug", "nombre", "archivada", "referente", "autoaprobacion",
                          "personas", "tareas_abiertas"}
    assert field["slug"] == "field" and field["archivada"] is False
    assert field["referente"] == {"membership_id": _persona(intake_world, "Taylor Quinn"),
                                  "nombre": "Taylor Quinn 1", "activo": True}
    assert field["autoaprobacion"] is False and field["tareas_abiertas"] == 0
    assert set(field["personas"]) == {_persona(intake_world, n)
                                      for n in ("Morgan Hale", "Taylor Quinn", "Sam North")}
    assert datos["areas"][1]["referente"] is None
    personas = {p["nombre"]: p for p in datos["personas"]}
    assert set(personas) == {"Morgan Hale 1", "Taylor Quinn 1", "Sam North 1", "Sam Noble 1"}
    noble = personas["Sam Noble 1"]
    assert set(noble) == {"membership_id", "nombre", "activo", "conectado", "area_id", "area",
                          "rol_id", "rol", "autoridad_final", "aprobador", "referente_de"}
    assert noble["area"] == "Quality Guild" and noble["rol"] == "Member"
    assert noble["aprobador"] == {"membership_id": _persona(intake_world, "Taylor Quinn"),
                                  "nombre": "Taylor Quinn 1", "activo": True}
    assert noble["activo"] is True and noble["conectado"] is True
    morgan = personas["Morgan Hale 1"]
    assert morgan["autoridad_final"] is True and morgan["aprobador"] is None
    assert personas["Taylor Quinn 1"]["referente_de"] == ["Field Services"]
    assert [r["nombre"] for r in datos["roles"]] == ["Director", "Lead", "Member"]
    assert datos["roles"][0] == {"id": datos["roles"][0]["id"], "slug": "director",
                                 "nombre": "Director", "autoridad_final": True, "personas": 1}
    assert datos["problemas"] == [] and datos["cambios"] == []
    # Nada de otro espacio.
    assert "Morgan Hale 2" not in respuesta.text


@pytest.mark.parametrize("nombre", ["Taylor Quinn", "Sam North"])
def test_un_referente_o_un_integrante_no_lo_ve(conn, intake_world, web, nombre):
    navegador = _navegador_del_equipo(web, conn, intake_world, nombre)
    respuesta = navegador.get(EQUIPO)
    assert respuesta.status_code == 403
    assert respuesta.json() == {"error": "sin_autoridad",
                                "texto": "Organizar el equipo le corresponde a Dirección."}
    assert "Sam Noble" not in respuesta.text


def test_sin_sesion_no_se_ve_nada(conn, intake_world, web, sesion):
    assert web().get(EQUIPO).status_code == 401
    assert web().get(_admin_del_equipo(intake_world["north-lab"]["id"])).status_code == 401
    # La cookie del equipo no abre la puerta de administración.
    navegador = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    assert navegador.get(_admin_del_equipo(intake_world["north-lab"]["id"])).status_code == 401


def test_el_administrador_ve_el_equipo_de_cualquier_espacio(conn, intake_world, web,
                                                             administradora):
    navegador = _navegador_de_administracion(web, conn, administradora)
    oeste = intake_world["west-studio"]
    respuesta = navegador.get(_admin_del_equipo(oeste["id"]))
    assert respuesta.status_code == 200, respuesta.text
    datos = respuesta.json()
    assert datos["espacio"]["nombre"] == "West Studio"
    assert {p["nombre"] for p in datos["personas"]} == {
        "Morgan Hale 2", "Taylor Quinn 2", "Sam North 2", "Sam Noble 2"}
    assert "Morgan Hale 1" not in respuesta.text
    # Un espacio que no existe, o un id que no es un id: 404.
    assert navegador.get(_admin_del_equipo(INVENTADO)).status_code == 404
    assert navegador.get(_admin_del_equipo("no-es-un-id")).status_code == 404
    # La puerta del equipo de la administradora (es Dirección de North Lab) ve sólo el suyo.
    equipo = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    assert equipo.get(EQUIPO).json()["espacio"]["nombre"] == "North Lab"


def test_un_administrador_revocado_ya_no_lo_ve(conn, intake_world, web, administradora):
    from tests.garantias.test_carga_de_tareas import _revocar

    navegador = _navegador_de_administracion(web, conn, administradora)
    _revocar(conn, administradora)
    assert navegador.get(_admin_del_equipo(intake_world["north-lab"]["id"])).status_code == 401


# --- Lo que muestra ---------------------------------------------------------------------------

def test_sin_conectar_es_quien_todavia_no_activo_su_enlace(conn, intake_world, web):
    with admin(conn) as cur:
        cur.execute("""update app_user set telegram_user_id = null where id = %s""",
                    (intake_world["north-lab"]["people"]["Sam Noble"]["app_user_id"],))
    conn.commit()
    navegador = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    personas = {p["nombre"]: p for p in navegador.get(EQUIPO).json()["personas"]}
    assert personas["Sam Noble 1"]["conectado"] is False
    assert personas["Sam North 1"]["conectado"] is True


def test_las_tareas_abiertas_de_cada_area(conn, intake_world, web):
    norte = intake_world["north-lab"]
    with admin(conn) as cur:
        for titulo, estado in (("Abierta", "asignada"), ("En curso", "en_curso"),
                               ("Hecha", "terminada"), ("Cancelada", "cancelada")):
            cur.execute("""insert into task (workspace_id, objective_id, titulo, area_id, estado)
                           values (%s, %s, %s, %s, %s)""",
                        (norte["id"], norte["objectives"][0], titulo, norte["areas"]["field"],
                         estado))
    conn.commit()
    navegador = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    areas = {a["nombre"]: a for a in navegador.get(EQUIPO).json()["areas"]}
    assert areas["Field Services"]["tareas_abiertas"] == 2
    assert areas["Quality Guild"]["tareas_abiertas"] == 0


def test_un_area_archivada_va_al_final_marcada(conn, intake_world, web):
    norte = intake_world["north-lab"]
    with admin(conn) as cur:
        cur.execute("""insert into area (workspace_id, slug, nombre, archivada_en)
                       values (%s, 'archivo', 'Archivo', now())""", (norte["id"],))
        cur.execute("""insert into approval_policy
                         (workspace_id, sujeto, area_id, autoaprobacion_declarada, motivo)
                       values (%s, 'tarea', %s, true, 'se autoaprueba')""",
                    (norte["id"], norte["areas"]["quality"]))
    conn.commit()
    navegador = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    areas = navegador.get(EQUIPO).json()["areas"]
    assert [(a["nombre"], a["archivada"]) for a in areas] == [
        ("Field Services", False), ("Quality Guild", False), ("Archivo", True)]
    assert areas[1]["autoaprobacion"] is True


def test_los_problemas_del_equipo_se_ven(conn, intake_world, web):
    """Una persona que ya no está sigue en la lista, marcada, y lo que deja sin cuadrar se dice."""
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (_persona(intake_world, "Taylor Quinn"),))
    conn.commit()
    navegador = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    datos = navegador.get(EQUIPO).json()
    codigos = sorted(p["codigo"] for p in datos["problemas"])
    assert codigos == ["aprobador_inactivo", "aprobador_inactivo", "referente_inactivo"]
    assert all(p["mensaje"] for p in datos["problemas"])
    taylor = next(p for p in datos["personas"] if p["nombre"] == "Taylor Quinn 1")
    assert taylor["activo"] is False
    # Las que siguen van primero.
    assert datos["personas"][-1]["nombre"] == "Taylor Quinn 1"
    field = next(a for a in datos["areas"] if a["slug"] == "field")
    assert _persona(intake_world, "Taylor Quinn") not in field["personas"]
    assert field["referente"]["activo"] is False


# --- Los cambios del equipo -------------------------------------------------------------------

def test_los_cambios_del_equipo_lo_mas_nuevo_primero(conn, intake_world, web, administradora):
    norte, oeste = intake_world["north-lab"], intake_world["west-studio"]
    hace = datetime.now(timezone.utc)
    morgan = norte["people"]["Morgan Hale"]
    _cambio(conn, norte["id"], clase="area_creada", at=hace - timedelta(days=2),
            quien_app_user=morgan["app_user_id"], quien_membership=morgan["membership_id"],
            despues={"nombre": "Compras"})
    _cambio(conn, norte["id"], clase="cambio_de_rol", at=hace - timedelta(days=1),
            quien_app_user=morgan["app_user_id"], quien_membership=None,
            antes={"rol": "Member"}, despues={"rol": "Lead"})
    _cambio(conn, oeste["id"], clase="area_creada", at=hace,
            quien_app_user=oeste["people"]["Morgan Hale"]["app_user_id"],
            quien_membership=oeste["people"]["Morgan Hale"]["membership_id"],
            despues={"nombre": "De otro espacio"})
    navegador = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    cambios = navegador.get(EQUIPO).json()["cambios"]
    assert [c["clase"] for c in cambios] == ["cambio_de_rol", "area_creada"]
    rol, area = cambios
    assert set(rol) == {"id", "clase", "puerta", "quien", "at", "antes", "despues"}
    assert rol["puerta"] == "administracion" and rol["quien"] == "Morgan Hale 1"
    assert rol["antes"] == {"rol": "Member"} and rol["despues"] == {"rol": "Lead"}
    assert area["puerta"] == "equipo" and area["antes"] is None
    assert "De otro espacio" not in navegador.get(EQUIPO).text
    # La administración, los del espacio que mira.
    admin_web = _navegador_de_administracion(web, conn, administradora)
    oeste_cambios = admin_web.get(_admin_del_equipo(oeste["id"])).json()["cambios"]
    assert [c["despues"] for c in oeste_cambios] == [{"nombre": "De otro espacio"}]
    # Un referente no los ve.
    referente = _navegador_del_equipo(web, conn, intake_world, "Taylor Quinn")
    respuesta = referente.get(EQUIPO)
    assert respuesta.status_code == 403 and "Compras" not in respuesta.text


def test_la_web_no_cae_en_el_indice_de_la_pagina(conn, intake_world, web):
    """La ruta de la API se mira antes que la de las páginas de `/app`."""
    navegador = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    respuesta = navegador.get(EQUIPO)
    assert respuesta.headers["content-type"].startswith("application/json")
    assert respuesta.headers.get("cache-control") == "no-store"
