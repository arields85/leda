"""El alta de una persona desde la web (migración 0084; J7-5 de `odd/tasks/plataforma-jerarquias.md`;
ADR 0023, decisión 4; ADR 0024; respuesta 6 de la J7).

- **Quién:** Dirección, por la puerta del equipo, en el suyo; el administrador de plataforma, por la
  suya, en cualquier espacio (`quien_organiza_el_equipo`). Un referente o un integrante, no (403).
- **El alta:** nombre, área (vigente) y rol; quién la aprueba, por omisión el referente activo del
  área y, sin él, Dirección (J6-D6); se puede elegir a cualquier integrante activo. Siempre es una
  persona nueva: nunca se la busca por el nombre. Quien vuelve al equipo se reactiva a propósito
  (`reactivar_integrante`), con su membresía de antes.
- **Primero la vista previa**, después la confirmación con la clave de un solo uso y su huella, como
  las áreas (J7-4); cada cambio deja una fila en `cambio_del_equipo` y su auditoría, y el equipo
  sigue cuadrando (`problemas_del_equipo`).
- **El enlace de activación** (`emitir_enlace_de_activacion`): uno nuevo para quien no conectó, que
  anula el anterior sin usar; se muestra una sola vez y la base guarda sólo su huella. Vence en 14
  días y sirve una vez.
- **Quien ya está en otro espacio:** al abrir el enlace con su Telegram, la membresía nueva queda
  unida a su cuenta (el mismo `app_user`), sólo por quien abre el enlace y nunca por el nombre; el
  espacio nuevo no ve nada del otro.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import psycopg
import pytest
from psycopg.types.json import Jsonb

from leda.autoridad import Denegado, identificar_en_espacio
from leda.db import admin, espacio
from leda.onboarding import ActivacionInvalida, activar, pendientes_de_activar
from tests.garantias.test_carga_de_tareas import (  # noqa: F401 -- `administradora`, `sesion`
    _hash,                                         # y `web` son las fixtures
    _navegador_de_administracion,
    _navegador_del_equipo,
    administradora,
    sesion,
    sin_espacio,
    web,
)
from tests.garantias.test_ver_el_equipo import (  # noqa: F401 -- `_referente_de_field` es autouse
    INVENTADO,
    _errores,
    _persona,
    _referente_de_field,
    _sesion_del_equipo,
)

FUNCIONES_DE_LA_WEB = ("vista_previa_de_alta", "dar_de_alta", "reactivar_integrante",
                       "emitir_enlace_de_activacion")
FUNCIONES_DE_ADENTRO = ("cambiar_el_alta", "confirmar_alta")

EQUIPO = "/app/api/equipo"
REVISAR = "/app/api/equipo/personas/revisar"
CONFIRMAR = "/app/api/equipo/personas"
ENLACE = "/app/api/equipo/personas/enlace"
BOT = "leda_norte_bot"


def _admin(espacio_id: str, que: str = "") -> str:
    return f"/app/admin/api/espacios/{espacio_id}/equipo{que}"


# --- Ayudas ---------------------------------------------------------------------------------

def _filas(conn, consulta: str, *args) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(consulta, args)
        filas = cur.fetchall()
    conn.commit()
    return filas


def _rol(conn, ws: str, slug: str) -> str:
    (fila,) = _filas(conn, "select id from rol where workspace_id = %s and slug = %s", ws, slug)
    return str(fila["id"])


def _previa(conn, puerta: str, token: str, ws: str | None, accion: str, **datos) -> dict:
    with sin_espacio(conn) as cur:
        cur.execute("select vista_previa_de_alta(%s, %s, %s, %s, %s) as r",
                    (puerta, _hash(token), ws, accion, Jsonb(datos)))
        r = cur.fetchone()["r"]
    conn.commit()
    return r


def _alta(conn, puerta: str, token: str, ws: str | None, *, nombre: str | None,
          area_id: str | None, rol_id: str | None, aprobador_id: str | None = None,
          clave: str | None = "", huella: str | None = "") -> dict:
    """Da de alta como lo hace la web: la vista previa y, si salió bien, la confirmación con su
    huella. `clave` o `huella` en `None` se mandan así; vacías, se completan."""
    if huella == "":
        previa = _previa(conn, puerta, token, ws, "alta", nombre=nombre, area_id=area_id,
                         rol_id=rol_id, aprobador_id=aprobador_id)
        if not previa["ok"]:
            return previa
        huella = previa["huella"]
    with sin_espacio(conn) as cur:
        cur.execute("select dar_de_alta(%s, %s, %s, %s, %s, %s, %s, %s, %s) as r",
                    (puerta, _hash(token), ws, nombre, area_id, rol_id, aprobador_id,
                     secrets.token_urlsafe(18) if clave == "" else clave, huella))
        r = cur.fetchone()["r"]
    conn.commit()
    return r


def _reactivar(conn, puerta: str, token: str, ws: str | None, *, membership_id: str,
               area_id: str | None, rol_id: str | None, aprobador_id: str | None = None) -> dict:
    previa = _previa(conn, puerta, token, ws, "reactivar", membership_id=membership_id,
                     area_id=area_id, rol_id=rol_id, aprobador_id=aprobador_id)
    if not previa["ok"]:
        return previa
    with sin_espacio(conn) as cur:
        cur.execute("select reactivar_integrante(%s, %s, %s, %s, %s, %s, %s, %s, %s) as r",
                    (puerta, _hash(token), ws, membership_id, area_id, rol_id, aprobador_id,
                     secrets.token_urlsafe(18), previa["huella"]))
        r = cur.fetchone()["r"]
    conn.commit()
    return r


def _emitir(conn, puerta: str, token: str, ws: str | None, membership_id: str | None,
            enlace: str | None = None) -> tuple[dict, str]:
    """Emite un enlace como la web: el token en claro queda acá; a la base va su huella."""
    enlace = enlace or secrets.token_urlsafe(24)
    with sin_espacio(conn) as cur:
        cur.execute("select emitir_enlace_de_activacion(%s, %s, %s, %s, %s) as r",
                    (puerta, _hash(token), ws, membership_id, _hash(enlace)))
        r = cur.fetchone()["r"]
    conn.commit()
    return r, enlace


def _cambios(conn, ws: str) -> list[dict]:
    return _filas(conn, "select * from cambio_del_equipo where workspace_id = %s order by at, id",
                  ws)


def _problemas(conn, ws: str) -> list:
    with admin(conn) as cur:
        cur.execute("select set_config('leda.workspace_id', %s, true)", (ws,))
        cur.execute("select problemas_del_equipo(%s) as p", (ws,))
        problemas = cur.fetchone()["p"]
    conn.commit()
    return problemas


def _membresia(conn, membership_id: str) -> dict:
    (fila,) = _filas(conn, """select m.*, u.telegram_user_id
                                from membership m join app_user u on u.id = m.app_user_id
                               where m.id = %s""", membership_id)
    return fila


def _bot(conn, ws: str, valor: str | None = BOT) -> None:
    with admin(conn) as cur:
        cur.execute("delete from workspace_setting where workspace_id = %s and clave = 'bot_usuario'",
                    (ws,))
        if valor is not None:
            cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                           values (%s, 'bot_usuario', to_jsonb(%s::text))""", (ws, valor))
    conn.commit()


@pytest.fixture
def direccion(conn, intake_world) -> str:
    _bot(conn, intake_world["north-lab"]["id"])
    return _sesion_del_equipo(conn, intake_world, "Morgan Hale")


def _lucas(conn, mundo: dict, token: str, area: str = "field", **datos) -> str:
    """Lucas Pérez, recién dado de alta en North Lab como integrante."""
    norte = mundo["north-lab"]
    r = _alta(conn, "equipo", token, None, nombre=datos.pop("nombre", "Lucas Pérez"),
              area_id=norte["areas"][area], rol_id=_rol(conn, norte["id"], "member"), **datos)
    assert r["ok"] is True, r
    return str(r["membership_id"])


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
            (list(FUNCIONES_DE_LA_WEB + FUNCIONES_DE_ADENTRO),))
        filas = {f["proname"]: f for f in cur.fetchall()}
    conn.commit()
    assert set(filas) == set(FUNCIONES_DE_LA_WEB + FUNCIONES_DE_ADENTRO)
    for nombre, f in filas.items():
        assert f["rolname"] == "leda_owner", nombre
        assert any(c.startswith("search_path=") and c.endswith("pg_temp")
                   for c in f["proconfig"] or []), nombre
        assert not f["de_public"] and not f["de_gateway"], nombre
    for nombre in FUNCIONES_DE_LA_WEB:
        assert filas[nombre]["prosecdef"] and filas[nombre]["de_app"], nombre
    for nombre in FUNCIONES_DE_ADENTRO:
        assert not filas[nombre]["prosecdef"] and not filas[nombre]["de_app"], nombre


def test_quien_puede_en_la_base(conn, intake_world, sesion, direccion):
    norte, oeste = intake_world["north-lab"], intake_world["west-studio"]
    datos = {"nombre": "Lucas Pérez", "area_id": norte["areas"]["field"],
             "rol_id": _rol(conn, norte["id"], "member")}
    assert _previa(conn, "equipo", direccion, None, "alta", **datos)["ok"] is True
    # Otro espacio no existe para Dirección, aunque lo nombre.
    assert _errores(_previa(conn, "equipo", direccion, oeste["id"], "alta", **datos)) == {
        ("espacio", "no_existe")}
    for nombre in ("Taylor Quinn", "Sam North"):
        token = _sesion_del_equipo(conn, intake_world, nombre)
        assert _errores(_previa(conn, "equipo", token, None, "alta", **datos)) == {
            ("sesion", "sin_autoridad")}
        assert _errores(_alta(conn, "equipo", token, None, **datos, huella="0" * 64)) == {
            ("sesion", "sin_autoridad")}
        assert _errores(_emitir(conn, "equipo", token, None,
                                _persona(intake_world, "Sam North"))[0]) == {
            ("sesion", "sin_autoridad")}
    # El administrador de plataforma, en cualquier espacio; uno que no existe, no.
    datos_oeste = {"nombre": "Lucas Pérez", "area_id": oeste["areas"]["field"],
                   "rol_id": _rol(conn, oeste["id"], "member")}
    assert _previa(conn, "administracion", sesion, oeste["id"], "alta", **datos_oeste)["ok"]
    assert _errores(_previa(conn, "administracion", sesion, INVENTADO, "alta", **datos)) == {
        ("espacio", "no_existe")}
    assert _errores(_previa(conn, "equipo", "inventado", None, "alta", **datos)) == {
        ("sesion", "sin_sesion")}
    assert _cambios(conn, norte["id"]) == [] and _cambios(conn, oeste["id"]) == []


def test_la_vista_previa_no_escribe_nada_y_propone_al_referente(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    previa = _previa(conn, "equipo", direccion, None, "alta", nombre="Lucas Pérez",
                     area_id=norte["areas"]["field"], rol_id=_rol(conn, norte["id"], "member"))
    assert previa["ok"] is True, previa
    assert previa["accion"] == "alta" and previa["antes"] is None
    assert previa["despues"] == {"nombre": "Lucas Pérez", "area": "Field Services",
                                 "rol": "Member", "quien_aprueba": "Taylor Quinn 1"}
    assert previa["aprobador"] == {"membership_id": _persona(intake_world, "Taylor Quinn"),
                                   "nombre": "Taylor Quinn 1", "por_omision": True}
    assert len(previa["huella"]) == 64 and previa["problemas_nuevos"] == []
    assert previa["avisos"] == []
    assert _filas(conn, "select 1 from app_user where nombre = 'Lucas Pérez'") == []
    assert _cambios(conn, norte["id"]) == []


# --- Quién la aprueba -------------------------------------------------------------------------

def test_sin_referente_activo_la_aprueba_direccion(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    morgan = _persona(intake_world, "Morgan Hale")
    member = _rol(conn, norte["id"], "member")

    def aprobador(area: str) -> dict:
        previa = _previa(conn, "equipo", direccion, None, "alta", nombre="Lucas Pérez",
                         area_id=norte["areas"][area], rol_id=member)
        assert previa["ok"] is True, previa
        return previa["aprobador"]

    # Quality Guild no tiene referente.
    assert aprobador("quality") == {"membership_id": morgan, "nombre": "Morgan Hale 1",
                                    "por_omision": True}
    # Con la autoaprobación declarada y sin referente, también Dirección.
    with admin(conn) as cur:
        cur.execute("""insert into approval_policy (workspace_id, sujeto, area_id,
                                                    autoaprobacion_declarada, motivo)
                       values (%s, 'tarea', %s, true, 'prueba')""",
                    (norte["id"], norte["areas"]["quality"]))
    conn.commit()
    assert aprobador("quality")["membership_id"] == morgan
    # Con un referente que ya no está, también.
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (_persona(intake_world, "Sam Noble"),))
        cur.execute("update area set referente_membership_id = %s where id = %s",
                    (_persona(intake_world, "Sam Noble"), norte["areas"]["quality"]))
    conn.commit()
    assert aprobador("quality")["membership_id"] == morgan


def test_se_puede_elegir_quien_la_aprueba(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    member = _rol(conn, norte["id"], "member")
    sam = _persona(intake_world, "Sam North")
    lucas = _lucas(conn, intake_world, direccion, aprobador_id=sam)
    assert str(_membresia(conn, lucas)["aprobador_membership_id"]) == sam
    (cambio,) = _cambios(conn, norte["id"])
    assert cambio["despues"]["quien_aprueba"] == "Sam North 1"

    def previa(aprobador_id):
        return _previa(conn, "equipo", direccion, None, "alta", nombre="Ana Ruiz",
                       area_id=norte["areas"]["field"], rol_id=member, aprobador_id=aprobador_id)

    assert ("aprobador", "no_es_integrante_activo") in _errores(
        previa(_persona(intake_world, "Sam North", "west-studio")))
    assert ("aprobador", "no_es_integrante_activo") in _errores(previa(INVENTADO))
    assert ("aprobador", "mal_formado") in _errores(previa("no-es-un-id"))
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (_persona(intake_world, "Sam Noble"),))
    conn.commit()
    assert ("aprobador", "no_es_integrante_activo") in _errores(
        previa(_persona(intake_world, "Sam Noble")))


# --- El alta ----------------------------------------------------------------------------------

def test_el_alta_crea_una_persona_sin_conectar(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    lucas = _lucas(conn, intake_world, direccion, nombre="  Lucas   Pérez ")
    persona = _membresia(conn, lucas)
    assert persona["nombre"] == "Lucas Pérez" and persona["telegram_user_id"] is None
    assert persona["activo"] is True and str(persona["area_id"]) == norte["areas"]["field"]
    assert str(persona["rol_id"]) == _rol(conn, norte["id"], "member")
    assert str(persona["aprobador_membership_id"]) == _persona(intake_world, "Taylor Quinn")
    (cambio,) = _cambios(conn, norte["id"])
    assert cambio["clase"] == "alta" and cambio["puerta"] == "equipo" and cambio["antes"] is None
    assert cambio["despues"] == {"nombre": "Lucas Pérez", "area": "Field Services",
                                 "rol": "Member", "quien_aprueba": "Taylor Quinn 1",
                                 "membership_id": lucas}
    assert str(cambio["hecho_por_membership_id"]) == _persona(intake_world, "Morgan Hale")
    assert _filas(conn, """select 1 from audit_log where workspace_id = %s and accion = 'alta'
                            and sujeto_tipo = 'membership' and sujeto_id = %s""",
                  norte["id"], lucas)
    assert _problemas(conn, norte["id"]) == []
    with admin(conn) as cur:
        assert "Lucas Pérez" in pendientes_de_activar(cur, norte["id"])
    conn.commit()
    with sin_espacio(conn) as cur:
        cur.execute("select equipo_de('equipo', %s, null) as r", (_hash(direccion),))
        equipo = cur.fetchone()["r"]
    conn.commit()
    (visto,) = [p for p in equipo["personas"] if p["membership_id"] == lucas]
    assert visto["conectado"] is False and visto["activo"] is True


def test_siempre_es_una_persona_nueva(conn, intake_world, direccion):
    """Nunca se la busca por el nombre: otra con el mismo nombre es otra persona."""
    norte = intake_world["north-lab"]
    previa = _previa(conn, "equipo", direccion, None, "alta", nombre="sam north 1",
                     area_id=norte["areas"]["quality"], rol_id=_rol(conn, norte["id"], "member"))
    assert previa["ok"] is True
    assert [a["codigo"] for a in previa["avisos"]] == ["mismo_nombre"]
    otra = _lucas(conn, intake_world, direccion, area="quality", nombre="Sam North 1")
    sam = _persona(intake_world, "Sam North")
    assert otra != sam
    assert _membresia(conn, otra)["app_user_id"] != _membresia(conn, sam)["app_user_id"]
    assert _membresia(conn, otra)["telegram_user_id"] is None
    # La de antes, intacta.
    assert str(_membresia(conn, sam)["area_id"]) == norte["areas"]["field"]
    # Alguien que ya no está con ese nombre: se avisa que se la puede volver a sumar.
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (_persona(intake_world, "Sam Noble"),))
    conn.commit()
    previa = _previa(conn, "equipo", direccion, None, "alta", nombre="Sam Noble 1",
                     area_id=norte["areas"]["quality"], rol_id=_rol(conn, norte["id"], "member"))
    assert [a["codigo"] for a in previa["avisos"]] == ["estuvo_en_el_equipo"]


def test_lo_que_no_se_puede_dar_de_alta(conn, intake_world, direccion):
    norte, oeste = intake_world["north-lab"], intake_world["west-studio"]
    member = _rol(conn, norte["id"], "member")
    field = norte["areas"]["field"]

    def previa(**datos):
        base = {"nombre": "Lucas Pérez", "area_id": field, "rol_id": member}
        return _previa(conn, "equipo", direccion, None, "alta", **{**base, **datos})

    assert ("nombre", "falta") in _errores(previa(nombre="   "))
    assert ("nombre", "demasiado_largo") in _errores(previa(nombre="x" * 81))
    assert ("area", "falta") in _errores(previa(area_id=None))
    assert ("area", "no_existe") in _errores(previa(area_id=oeste["areas"]["field"]))
    assert ("area", "mal_formada") in _errores(previa(area_id="no-es-un-id"))
    assert ("rol", "falta") in _errores(previa(rol_id=None))
    assert ("rol", "no_existe") in _errores(previa(rol_id=_rol(conn, oeste["id"], "member")))
    # La autoridad final sólo se pasa (punto 10 del ADR 0023): no se da con un alta.
    assert ("rol", "es_de_direccion") in _errores(previa(rol_id=_rol(conn, norte["id"],
                                                                     "director")))
    with admin(conn) as cur:
        cur.execute("""insert into area (workspace_id, slug, nombre, archivada_en)
                       values (%s, 'viejo', 'Depósito', now()) returning id""", (norte["id"],))
        viejo = str(cur.fetchone()["id"])
    conn.commit()
    assert ("area", "archivada") in _errores(previa(area_id=viejo))
    assert ("accion", "no_existe") in _errores(
        _previa(conn, "equipo", direccion, None, "borrar", nombre="Lucas"))
    assert _cambios(conn, norte["id"]) == []


def test_la_misma_clave_devuelve_lo_mismo(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    datos = {"nombre": "Lucas Pérez", "area_id": norte["areas"]["field"],
             "rol_id": _rol(conn, norte["id"], "member")}
    previa = _previa(conn, "equipo", direccion, None, "alta", **datos)
    clave = secrets.token_urlsafe(18)
    primera = _alta(conn, "equipo", direccion, None, **datos, clave=clave, huella=previa["huella"])
    otra_vez = _alta(conn, "equipo", direccion, None, **datos, clave=clave,
                     huella=previa["huella"])
    assert primera["ok"] and otra_vez["ok"] and otra_vez["repetida"] is True
    assert otra_vez["membership_id"] == primera["membership_id"]
    assert len(_filas(conn, "select 1 from app_user where nombre = 'Lucas Pérez'")) == 1
    assert len(_cambios(conn, norte["id"])) == 1
    assert ("clave", "usada_con_otros_datos") in _errores(
        _alta(conn, "equipo", direccion, None, **{**datos, "nombre": "Ana Ruiz"}, clave=clave))
    assert ("clave", "falta") in _errores(_alta(conn, "equipo", direccion, None, **datos,
                                                clave=None))
    assert ("huella", "falta") in _errores(_alta(conn, "equipo", direccion, None, **datos,
                                                 huella=None))


def test_si_el_equipo_cambio_desde_la_vista_previa_no_se_confirma(conn, intake_world,
                                                                   direccion):
    norte = intake_world["north-lab"]
    datos = {"nombre": "Lucas Pérez", "area_id": norte["areas"]["field"],
             "rol_id": _rol(conn, norte["id"], "member")}
    previa = _previa(conn, "equipo", direccion, None, "alta", **datos)
    # Mientras tanto, Field Services cambió de referente: el aprobador por omisión ya no es el que
    # se vio.
    with admin(conn) as cur:
        cur.execute("update area set referente_membership_id = %s where id = %s",
                    (_persona(intake_world, "Sam North"), norte["areas"]["field"]))
    conn.commit()
    r = _alta(conn, "equipo", direccion, None, **datos, huella=previa["huella"])
    assert ("huella", "el_equipo_cambio") in _errores(r)
    assert _filas(conn, "select 1 from app_user where nombre = 'Lucas Pérez'") == []


def test_el_administrador_da_de_alta_en_cualquier_espacio(conn, intake_world, sesion):
    oeste = intake_world["west-studio"]
    r = _alta(conn, "administracion", sesion, oeste["id"], nombre="Lucas Pérez",
              area_id=oeste["areas"]["quality"], rol_id=_rol(conn, oeste["id"], "member"))
    assert r["ok"] is True, r
    persona = _membresia(conn, str(r["membership_id"]))
    assert str(persona["workspace_id"]) == oeste["id"]
    # Quality Guild no tiene referente: lo aprueba Dirección de ese espacio.
    assert str(persona["aprobador_membership_id"]) == _persona(intake_world, "Morgan Hale",
                                                               "west-studio")
    (cambio,) = _cambios(conn, oeste["id"])
    assert cambio["puerta"] == "administracion" and cambio["hecho_por_membership_id"] is None


# --- Volver a sumar a quien estuvo ------------------------------------------------------------

def test_reactivar_a_quien_vuelve(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    noble = _persona(intake_world, "Sam Noble")
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s", (noble,))
    conn.commit()
    r = _reactivar(conn, "equipo", direccion, None, membership_id=noble,
                   area_id=norte["areas"]["field"], rol_id=_rol(conn, norte["id"], "member"))
    assert r["ok"] is True, r
    assert str(r["membership_id"]) == noble
    persona = _membresia(conn, noble)
    assert persona["activo"] is True and str(persona["area_id"]) == norte["areas"]["field"]
    assert str(persona["aprobador_membership_id"]) == _persona(intake_world, "Taylor Quinn")
    # Su cuenta de Telegram sigue: no hace falta otro enlace.
    assert persona["telegram_user_id"] == norte["people"]["Sam Noble"]["telegram"]
    (cambio,) = _cambios(conn, norte["id"])
    assert cambio["clase"] == "reactivacion"
    assert cambio["antes"]["area"] == "Quality Guild" and cambio["antes"]["estado"] == (
        "fuera del equipo")
    assert cambio["despues"]["area"] == "Field Services"
    assert cambio["despues"]["estado"] == "en el equipo"
    assert _problemas(conn, norte["id"]) == []
    # Ni quien ya está, ni alguien de otro espacio.
    member = _rol(conn, norte["id"], "member")
    assert ("persona", "ya_esta_en_el_equipo") in _errores(
        _previa(conn, "equipo", direccion, None, "reactivar", membership_id=noble,
                area_id=norte["areas"]["field"], rol_id=member))
    assert ("persona", "no_existe") in _errores(
        _previa(conn, "equipo", direccion, None, "reactivar",
                membership_id=_persona(intake_world, "Sam Noble", "west-studio"),
                area_id=norte["areas"]["field"], rol_id=member))
    assert ("persona", "falta") in _errores(
        _previa(conn, "equipo", direccion, None, "reactivar",
                area_id=norte["areas"]["field"], rol_id=member))


def test_reactivar_no_deja_que_se_apruebe_a_si_misma(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    noble = _persona(intake_world, "Sam Noble")
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s", (noble,))
    conn.commit()
    assert ("aprobador", "es_la_misma_persona") in _errores(
        _previa(conn, "equipo", direccion, None, "reactivar", membership_id=noble,
                area_id=norte["areas"]["field"], rol_id=_rol(conn, norte["id"], "member"),
                aprobador_id=noble))


# --- El enlace de activación ------------------------------------------------------------------

def test_el_enlace_se_guarda_solo_como_huella(conn, intake_world, direccion):
    lucas = _lucas(conn, intake_world, direccion)
    r, token = _emitir(conn, "equipo", direccion, None, lucas)
    assert r["ok"] is True, r
    assert r["nombre"] == "Lucas Pérez" and r["bot_usuario"] == BOT
    (fila,) = _filas(conn, "select * from activation_token where membership_id = %s", lucas)
    assert fila["token_hash"] == hashlib.sha256(token.encode()).hexdigest()
    # El token en claro no está en ninguna columna.
    assert all(token not in str(valor) for valor in fila.values())
    assert "token" not in fila
    # Vence en 14 días.
    vence = fila["expira_en"] - datetime.now(timezone.utc)
    assert timedelta(days=13, hours=23) < vence <= timedelta(days=14)
    assert fila["usado_en"] is None
    assert _filas(conn, """select 1 from audit_log where accion = 'enlace_de_activacion'
                            and sujeto_id = %s""", lucas)


def test_un_enlace_nuevo_anula_el_anterior(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    lucas = _lucas(conn, intake_world, direccion)
    _, viejo = _emitir(conn, "equipo", direccion, None, lucas)
    _, nuevo = _emitir(conn, "equipo", direccion, None, lucas)
    assert len(_filas(conn, "select 1 from activation_token where membership_id = %s",
                      lucas)) == 1
    with admin(conn) as cur:
        with pytest.raises(ActivacionInvalida, match="no es válido"):
            activar(cur, norte["id"], viejo, 990001)
    conn.rollback()
    with admin(conn) as cur:
        assert activar(cur, norte["id"], nuevo, 990001) == "Lucas Pérez"
        # Sirve una sola vez.
        with pytest.raises(ActivacionInvalida, match="ya se usó"):
            activar(cur, norte["id"], nuevo, 990002)
    conn.commit()
    assert _membresia(conn, lucas)["telegram_user_id"] == 990001


def test_el_enlace_vence_a_los_14_dias(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    lucas = _lucas(conn, intake_world, direccion)
    _, token = _emitir(conn, "equipo", direccion, None, lucas)
    with admin(conn) as cur:
        with pytest.raises(ActivacionInvalida, match="venció"):
            activar(cur, norte["id"], token, 990001,
                    ahora=datetime.now(timezone.utc) + timedelta(days=15))
    conn.rollback()


def test_a_quien_no_corresponde_no_se_le_emite(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    # Quien ya conectó.
    assert ("persona", "ya_conectada") in _errores(
        _emitir(conn, "equipo", direccion, None, _persona(intake_world, "Sam North"))[0])
    # Alguien de otro espacio, o que no existe.
    assert ("persona", "no_existe") in _errores(
        _emitir(conn, "equipo", direccion, None,
                _persona(intake_world, "Sam North", "west-studio"))[0])
    assert ("persona", "falta") in _errores(_emitir(conn, "equipo", direccion, None, None)[0])
    lucas = _lucas(conn, intake_world, direccion)
    # Sin el usuario del bot del espacio no se puede armar el enlace: no se escribe nada.
    _bot(conn, norte["id"], None)
    assert ("bot", "sin_usuario") in _errores(_emitir(conn, "equipo", direccion, None, lucas)[0])
    assert _filas(conn, "select 1 from activation_token where membership_id = %s", lucas) == []
    _bot(conn, norte["id"])
    # Quien ya no está en el equipo.
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s", (lucas,))
    conn.commit()
    assert ("persona", "no_esta_en_el_equipo") in _errores(
        _emitir(conn, "equipo", direccion, None, lucas)[0])
    # Una huella con otra forma.
    with sin_espacio(conn) as cur:
        cur.execute("select emitir_enlace_de_activacion('equipo', %s, null, %s, 'corta') as r",
                    (_hash(direccion), _persona(intake_world, "Sam North")))
        r = cur.fetchone()["r"]
    conn.commit()
    assert ("enlace", "mal_formado") in _errores(r)


def test_la_aplicacion_no_lee_los_enlaces(conn, intake_world):
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute("select * from activation_token")


# --- Quien ya está en otro espacio --------------------------------------------------------------

def test_quien_ya_esta_en_otro_espacio_une_su_cuenta(conn, intake_world, direccion):
    """Sam Noble 2 trabaja en West Studio y ahora también en North Lab: abre el enlace con su
    Telegram y la membresía nueva queda unida a su cuenta."""
    norte, oeste = intake_world["north-lab"], intake_world["west-studio"]
    de_oeste = oeste["people"]["Sam Noble"]
    lucas = _lucas(conn, intake_world, direccion, nombre="Samuel Noble")
    _, token = _emitir(conn, "equipo", direccion, None, lucas)
    with admin(conn) as cur:
        activar(cur, norte["id"], token, de_oeste["telegram"])
    conn.commit()
    persona = _membresia(conn, lucas)
    assert str(persona["app_user_id"]) == de_oeste["app_user_id"]
    assert persona["telegram_user_id"] == de_oeste["telegram"]
    # Una sola cuenta con ese Telegram, y cada espacio la reconoce como la suya.
    assert len(_filas(conn, "select 1 from app_user where telegram_user_id = %s",
                      de_oeste["telegram"])) == 1
    with espacio(conn, norte["id"]) as cur:
        assert identificar_en_espacio(cur, de_oeste["telegram"],
                                      norte["id"]).membership_id == lucas
    conn.commit()
    with espacio(conn, oeste["id"]) as cur:
        assert identificar_en_espacio(cur, de_oeste["telegram"], oeste["id"]).membership_id == (
            de_oeste["membership_id"])
    conn.commit()
    # North Lab no ve nada de West Studio: ni su membresía ni sus áreas.
    with espacio(conn, norte["id"]) as cur:
        cur.execute("select id, workspace_id from membership where app_user_id = %s",
                    (de_oeste["app_user_id"],))
        assert [str(f["id"]) for f in cur.fetchall()] == [lucas]
        cur.execute("select count(*) n from area where workspace_id = %s", (oeste["id"],))
        assert cur.fetchone()["n"] == 0
    conn.commit()
    with sin_espacio(conn) as cur:
        cur.execute("select equipo_de('equipo', %s, null) as r", (_hash(direccion),))
        equipo = cur.fetchone()["r"]
    conn.commit()
    assert {a["id"] for a in equipo["areas"]} == set(norte["areas"].values())
    assert all(p["area_id"] in norte["areas"].values() for p in equipo["personas"])
    (visto,) = [p for p in equipo["personas"] if p["membership_id"] == lucas]
    assert visto["conectado"] is True
    # West Studio, igual que antes: su Sam Noble sigue en su área.
    assert str(_membresia(conn, de_oeste["membership_id"])["area_id"]) == (
        oeste["areas"]["quality"])


def test_se_une_solo_quien_abre_el_enlace_nunca_por_el_nombre(conn, intake_world, direccion):
    """Un alta con el mismo nombre que alguien de otro espacio no se une a esa persona: queda
    unida a la cuenta de quien abre el enlace."""
    norte, oeste = intake_world["north-lab"], intake_world["west-studio"]
    homonimo = _lucas(conn, intake_world, direccion, nombre="Sam Noble 2")
    _, token = _emitir(conn, "equipo", direccion, None, homonimo)
    with admin(conn) as cur:
        activar(cur, norte["id"], token, 990777)
    conn.commit()
    persona = _membresia(conn, homonimo)
    assert persona["telegram_user_id"] == 990777
    assert str(persona["app_user_id"]) != oeste["people"]["Sam Noble"]["app_user_id"]


def test_una_cuenta_de_este_equipo_no_toma_otra_identidad(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    lucas = _lucas(conn, intake_world, direccion)
    _, token = _emitir(conn, "equipo", direccion, None, lucas)
    with admin(conn) as cur:
        with pytest.raises(ActivacionInvalida, match="ya está en uso"):
            activar(cur, norte["id"], token, norte["people"]["Sam North"]["telegram"])
    conn.rollback()
    assert _membresia(conn, lucas)["telegram_user_id"] is None


def test_un_enlace_de_otro_espacio_no_sirve_en_este(conn, intake_world, direccion):
    oeste = intake_world["west-studio"]
    lucas = _lucas(conn, intake_world, direccion)
    _, token = _emitir(conn, "equipo", direccion, None, lucas)
    with admin(conn) as cur:
        with pytest.raises(ActivacionInvalida, match="no es válido"):
            activar(cur, oeste["id"], token, 990001)
    conn.rollback()
    with espacio(conn, oeste["id"]) as cur:
        with pytest.raises(Denegado):
            identificar_en_espacio(cur, 990001, oeste["id"])
    conn.rollback()


# --- La entrada HTTP ----------------------------------------------------------------------------

def _cuerpo(mundo: dict, conn, **datos) -> dict:
    norte = mundo["north-lab"]
    return {"accion": "alta", "nombre": "Lucas Pérez", "area_id": norte["areas"]["field"],
            "rol_id": _rol(conn, norte["id"], "member"), **datos}


def test_direccion_da_de_alta_y_copia_el_enlace_desde_la_web(conn, intake_world, web):
    norte = intake_world["north-lab"]
    _bot(conn, norte["id"])
    navegador = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    previa = navegador.post(REVISAR, json=_cuerpo(intake_world, conn))
    assert previa.status_code == 200, previa.text
    vista = previa.json()
    assert vista["despues"]["quien_aprueba"] == "Taylor Quinn 1"
    assert vista["aprobador"]["por_omision"] is True
    cuerpo = _cuerpo(intake_world, conn, clave=secrets.token_urlsafe(18), huella=vista["huella"])
    hecha = navegador.post(CONFIRMAR, json=cuerpo)
    assert hecha.status_code == 201, hecha.text
    lucas = hecha.json()["membership_id"]
    otra_vez = navegador.post(CONFIRMAR, json=cuerpo)
    assert otra_vez.status_code == 200 and otra_vez.json()["repetida"] is True
    assert otra_vez.json()["membership_id"] == lucas
    # El enlace, una vez: el de Telegram con el token; la base guarda sólo su huella.
    enlace = navegador.post(ENLACE, json={"membership_id": lucas})
    assert enlace.status_code == 200, enlace.text
    datos = enlace.json()
    assert datos["nombre"] == "Lucas Pérez" and datos["vence_en_dias"] == 14
    url = urlparse(datos["enlace"])
    assert url.scheme == "https" and url.netloc == "t.me" and url.path == f"/{BOT}"
    (token,) = parse_qs(url.query)["start"]
    (fila,) = _filas(conn, "select token_hash from activation_token where membership_id = %s",
                     lucas)
    assert fila["token_hash"] == hashlib.sha256(token.encode()).hexdigest() != token
    assert "no-store" in enlace.headers.get("cache-control", "")
    equipo = navegador.get(EQUIPO).json()
    (visto,) = [p for p in equipo["personas"] if p["membership_id"] == lucas]
    assert visto["conectado"] is False
    assert [c["clase"] for c in equipo["cambios"]] == ["alta"]


def test_lo_que_no_se_puede_se_dice_con_palabras(conn, intake_world, web):
    norte = intake_world["north-lab"]
    _bot(conn, norte["id"])
    navegador = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    respuesta = navegador.post(REVISAR, json=_cuerpo(intake_world, conn, nombre=" "))
    assert respuesta.status_code == 422
    (error,) = respuesta.json()["errores"]
    assert error["campo"] == "nombre" and error["texto"]
    assert navegador.post(REVISAR, json=_cuerpo(intake_world, conn,
                                                 area_id=123)).status_code == 422
    assert navegador.post(REVISAR, json={"accion": "borrar"}).status_code == 422
    conectada = navegador.post(ENLACE, json={"membership_id": _persona(intake_world, "Sam North")})
    assert conectada.status_code == 422
    assert conectada.json()["errores"][0]["texto"] == "Esa persona ya conectó su Telegram."
    assert navegador.post(ENLACE, json={"membership_id": "no-es-un-id"}).status_code == 422


@pytest.mark.parametrize("nombre", ["Taylor Quinn", "Sam North"])
def test_un_referente_o_un_integrante_no_puede(conn, intake_world, web, nombre):
    navegador = _navegador_del_equipo(web, conn, intake_world, nombre)
    for camino, cuerpo in ((REVISAR, _cuerpo(intake_world, conn)),
                           (CONFIRMAR, _cuerpo(intake_world, conn,
                                               clave=secrets.token_urlsafe(18),
                                               huella="0" * 64)),
                           (ENLACE, {"membership_id": _persona(intake_world, "Sam North")})):
        respuesta = navegador.post(camino, json=cuerpo)
        assert respuesta.status_code == 403, camino
        assert respuesta.json()["texto"] == "Organizar el equipo le corresponde a Dirección."
    assert _cambios(conn, intake_world["north-lab"]["id"]) == []
    assert _filas(conn, "select 1 from activation_token") == []


def test_otro_sitio_o_sin_sesion_no_cambia_nada(conn, intake_world, web):
    navegador = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    assert navegador.post(REVISAR, json=_cuerpo(intake_world, conn),
                          headers={"origin": "https://otro.example"}).status_code == 403
    assert web().post(ENLACE, json={"membership_id": INVENTADO}).status_code == 401
    assert web().post(_admin(intake_world["north-lab"]["id"], "/personas/enlace"),
                      json={"membership_id": INVENTADO}).status_code == 401


def test_el_administrador_por_su_puerta(conn, intake_world, web, administradora):
    oeste = intake_world["west-studio"]
    _bot(conn, oeste["id"], "leda_oeste_bot")
    navegador = _navegador_de_administracion(web, conn, administradora)
    cuerpo = {"accion": "alta", "nombre": "Lucas Pérez", "area_id": oeste["areas"]["field"],
              "rol_id": _rol(conn, oeste["id"], "member")}
    previa = navegador.post(_admin(oeste["id"], "/personas/revisar"), json=cuerpo)
    assert previa.status_code == 200, previa.text
    hecha = navegador.post(_admin(oeste["id"], "/personas"),
                           json={**cuerpo, "clave": secrets.token_urlsafe(18),
                                 "huella": previa.json()["huella"]})
    assert hecha.status_code == 201, hecha.text
    enlace = navegador.post(_admin(oeste["id"], "/personas/enlace"),
                            json={"membership_id": hecha.json()["membership_id"]})
    assert enlace.status_code == 200, enlace.text
    assert enlace.json()["enlace"].startswith("https://t.me/leda_oeste_bot?start=")
    assert navegador.post(_admin(INVENTADO, "/personas/revisar"), json=cuerpo).status_code == 404
    # Volver a sumar a alguien, por la misma puerta.
    noble = _persona(intake_world, "Sam Noble", "west-studio")
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s", (noble,))
    conn.commit()
    vuelta = {"accion": "reactivar", "membership_id": noble, "area_id": oeste["areas"]["field"],
              "rol_id": _rol(conn, oeste["id"], "member")}
    previa = navegador.post(_admin(oeste["id"], "/personas/revisar"), json=vuelta)
    assert previa.status_code == 200, previa.text
    hecha = navegador.post(_admin(oeste["id"], "/personas"),
                           json={**vuelta, "clave": secrets.token_urlsafe(18),
                                 "huella": previa.json()["huella"]})
    assert hecha.status_code == 201, hecha.text
    assert [c["clase"] for c in _cambios(conn, oeste["id"])] == ["alta", "reactivacion"]
    assert _problemas(conn, oeste["id"]) == []
