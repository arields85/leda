"""Las áreas desde la web (migración 0083; J7-4 de `odd/tasks/plataforma-jerarquias.md`; ADR 0023,
decisión 4; mecánica §7): crear, renombrar y archivar un área, por las dos puertas.

- **Quién:** Dirección, por la puerta del equipo, en el suyo; el administrador de plataforma, por la
  suya, en cualquier espacio (`quien_organiza_el_equipo`). Un referente o un integrante, no (403).
- **Primero la vista previa** (`vista_previa_de_area`): lo que cambiaría, con su huella, y los
  problemas del equipo que dejaría; no escribe nada. Después se confirma con la clave de un solo
  uso y esa huella (`crear_area`, `renombrar_area`, `archivar_area`): la misma clave con la misma
  huella devuelve lo mismo; si el equipo cambió desde la vista previa, no se confirma.
- **Crear:** un nombre que no repite el de otra área vigente (el `slug` sale de él y no cambia);
  quién aprueba su trabajo (su referente, un integrante activo; el área misma, declarado a
  propósito; o lo decide Dirección), y su evidencia: tipos del espacio o «no pide evidencia», a
  propósito. Así una tarea del área se puede cargar.
- **Renombrar** cambia sólo el nombre que se ve. **Archivar**, sólo sin gente ni tareas abiertas.
- Cada cambio deja una fila en `cambio_del_equipo` con el antes y el después, y el equipo sigue
  cuadrando (`problemas_del_equipo`).
"""

from __future__ import annotations

import secrets

import pytest
from psycopg.types.json import Jsonb

from leda.db import admin
from tests.garantias.test_carga_de_tareas import (  # noqa: F401 -- `administradora`, `sesion`
    _cargar,                                       # y `web` son las fixtures
    _hash,
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

FUNCIONES_DE_LA_WEB = ("vista_previa_de_area", "crear_area", "renombrar_area", "archivar_area",
                       "opciones_de_areas")
FUNCIONES_DE_ADENTRO = ("cambiar_un_area", "confirmar_cambio_de_area",
                        "tipos_de_evidencia_del_espacio")

EQUIPO = "/app/api/equipo"
REVISAR = "/app/api/equipo/areas/revisar"
CONFIRMAR = "/app/api/equipo/areas"


def _admin(espacio_id: str, que: str = "") -> str:
    return f"/app/admin/api/espacios/{espacio_id}/equipo{que}"


# --- Ayudas ---------------------------------------------------------------------------------

def _previa(conn, puerta: str, token: str, ws: str | None, accion: str, **datos) -> dict:
    with sin_espacio(conn) as cur:
        cur.execute("select vista_previa_de_area(%s, %s, %s, %s, %s) as r",
                    (puerta, _hash(token), ws, accion, Jsonb(datos)))
        r = cur.fetchone()["r"]
    conn.commit()
    return r


def _crear(conn, puerta: str, token: str, ws: str | None, *, nombre: str | None,
           aprobacion: str | None, referente_id: str | None = None,
           evidencia: list[str] | None = None, sin_evidencia: bool = False,
           clave: str | None = "", huella: str | None = "") -> dict:
    """Crea como lo hace la web: la vista previa y, si salió bien, la confirmación con su huella.
    `clave` o `huella` en `None` se mandan así; vacías, se completan."""
    if huella == "":
        previa = _previa(conn, puerta, token, ws, "crear", nombre=nombre, aprobacion=aprobacion,
                         referente_id=referente_id, evidencia=evidencia,
                         sin_evidencia=sin_evidencia)
        if not previa["ok"]:
            return previa
        huella = previa["huella"]
    if clave == "":
        clave = secrets.token_urlsafe(18)
    with sin_espacio(conn) as cur:
        cur.execute("select crear_area(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) as r",
                    (puerta, _hash(token), ws, nombre, aprobacion, referente_id, evidencia,
                     sin_evidencia, clave, huella))
        r = cur.fetchone()["r"]
    conn.commit()
    return r


def _renombrar(conn, puerta: str, token: str, ws: str | None, area_id: str, nombre: str,
               clave: str | None = "", huella: str | None = "") -> dict:
    if huella == "":
        previa = _previa(conn, puerta, token, ws, "renombrar", area_id=area_id, nombre=nombre)
        if not previa["ok"]:
            return previa
        huella = previa["huella"]
    with sin_espacio(conn) as cur:
        cur.execute("select renombrar_area(%s, %s, %s, %s, %s, %s, %s) as r",
                    (puerta, _hash(token), ws, area_id, nombre,
                     secrets.token_urlsafe(18) if clave == "" else clave, huella))
        r = cur.fetchone()["r"]
    conn.commit()
    return r


def _archivar(conn, puerta: str, token: str, ws: str | None, area_id: str) -> dict:
    previa = _previa(conn, puerta, token, ws, "archivar", area_id=area_id)
    if not previa["ok"]:
        return previa
    with sin_espacio(conn) as cur:
        cur.execute("select archivar_area(%s, %s, %s, %s, %s, %s) as r",
                    (puerta, _hash(token), ws, area_id, secrets.token_urlsafe(18),
                     previa["huella"]))
        r = cur.fetchone()["r"]
    conn.commit()
    return r


def _filas(conn, consulta: str, *args) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(consulta, args)
        filas = cur.fetchall()
    conn.commit()
    return filas


def _area(conn, area_id: str) -> dict:
    (fila,) = _filas(conn, "select * from area where id = %s", area_id)
    return fila


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


@pytest.fixture
def direccion(conn, intake_world) -> str:
    return _sesion_del_equipo(conn, intake_world, "Morgan Hale")


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
    datos = {"nombre": "Compras", "aprobacion": "direccion", "evidencia": ["test record"]}
    assert _previa(conn, "equipo", direccion, None, "crear", **datos)["ok"] is True
    assert _previa(conn, "equipo", direccion, norte["id"], "crear", **datos)["ok"] is True
    # Otro espacio no existe para Dirección, aunque lo nombre.
    assert _errores(_previa(conn, "equipo", direccion, oeste["id"], "crear", **datos)) == {
        ("espacio", "no_existe")}
    for nombre in ("Taylor Quinn", "Sam North"):
        token = _sesion_del_equipo(conn, intake_world, nombre)
        assert _errores(_previa(conn, "equipo", token, None, "crear", **datos)) == {
            ("sesion", "sin_autoridad")}
        assert _errores(_crear(conn, "equipo", token, None, nombre="Compras",
                               aprobacion="direccion", evidencia=["test record"],
                               huella="0" * 64)) == {("sesion", "sin_autoridad")}
    # El administrador de plataforma, en cualquier espacio; uno que no existe, no.
    assert _previa(conn, "administracion", sesion, oeste["id"], "crear", **datos)["ok"] is True
    assert _errores(_previa(conn, "administracion", sesion, INVENTADO, "crear", **datos)) == {
        ("espacio", "no_existe")}
    assert _errores(_previa(conn, "equipo", "inventado", None, "crear", **datos)) == {
        ("sesion", "sin_sesion")}
    # Nada se escribió.
    assert _cambios(conn, norte["id"]) == [] and _cambios(conn, oeste["id"]) == []


def test_la_vista_previa_no_escribe_nada(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    previa = _previa(conn, "equipo", direccion, None, "crear", nombre="Compras",
                     aprobacion="referente", referente_id=_persona(intake_world, "Sam North"),
                     evidencia=["test record"])
    assert previa["ok"] is True, previa
    assert previa["accion"] == "crear" and previa["antes"] is None
    assert previa["despues"]["nombre"] == "Compras"
    assert previa["despues"]["referente"] == "Sam North 1"
    assert len(previa["huella"]) == 64
    assert previa["problemas"] == [] and previa["problemas_nuevos"] == []
    assert _filas(conn, "select 1 from area where workspace_id = %s and nombre = 'Compras'",
                  norte["id"]) == []
    assert _cambios(conn, norte["id"]) == []
    # La misma vista previa da la misma huella.
    otra = _previa(conn, "equipo", direccion, None, "crear", nombre="Compras",
                   aprobacion="referente", referente_id=_persona(intake_world, "Sam North"),
                   evidencia=["test record"])
    assert otra["huella"] == previa["huella"]


# --- Crear ------------------------------------------------------------------------------------

def test_crear_un_area_con_referente(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    sam = _persona(intake_world, "Sam North")
    r = _crear(conn, "equipo", direccion, None, nombre="  Compras y Logística ",
               aprobacion="referente", referente_id=sam, evidencia=["test record"])
    assert r["ok"] is True and r["repetida"] is False, r
    area = _area(conn, r["area_id"])
    assert area["nombre"] == "Compras y Logística" and area["slug"] == "compras-y-logistica"
    assert str(area["referente_membership_id"]) == sam and area["archivada_en"] is None
    (politica,) = _filas(conn, "select * from task_evidence_policy where area_id = %s",
                         r["area_id"])
    assert politica["evidencia_requerida"] == ["test record"]
    assert _filas(conn, "select 1 from approval_policy where area_id = %s", r["area_id"]) == []
    (cambio,) = _cambios(conn, norte["id"])
    assert cambio["clase"] == "area_creada" and cambio["puerta"] == "equipo"
    assert cambio["antes"] is None
    assert cambio["despues"]["nombre"] == "Compras y Logística"
    assert cambio["despues"]["referente"] == "Sam North 1"
    assert cambio["despues"]["area_id"] == r["area_id"]
    assert str(cambio["hecho_por_membership_id"]) == _persona(intake_world, "Morgan Hale")
    assert _filas(conn, """select 1 from audit_log where workspace_id = %s
                            and accion = 'area_creada' and sujeto_id = %s""",
                  norte["id"], r["area_id"])
    assert _problemas(conn, norte["id"]) == []


def test_crear_un_area_que_se_autoaprueba(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    r = _crear(conn, "equipo", direccion, None, nombre="Compras", aprobacion="autoaprobacion",
               evidencia=["test record"])
    assert r["ok"] is True, r
    (politica,) = _filas(conn, "select * from approval_policy where area_id = %s", r["area_id"])
    assert politica["autoaprobacion_declarada"] is True
    assert _area(conn, r["area_id"])["referente_membership_id"] is None
    assert _problemas(conn, norte["id"]) == []


def test_crear_un_area_que_decide_direccion_y_no_pide_evidencia(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    r = _crear(conn, "equipo", direccion, None, nombre="Compras", aprobacion="direccion",
               sin_evidencia=True)
    assert r["ok"] is True, r
    area = _area(conn, r["area_id"])
    assert area["referente_membership_id"] is None
    assert _filas(conn, "select 1 from approval_policy where area_id = %s", r["area_id"]) == []
    (politica,) = _filas(conn, "select * from task_evidence_policy where area_id = %s",
                         r["area_id"])
    assert politica["evidencia_requerida"] == []
    (cambio,) = _cambios(conn, norte["id"])
    assert cambio["despues"]["evidencia"] == "no pide evidencia"
    assert _problemas(conn, norte["id"]) == []


def test_la_evidencia_se_elige_a_proposito(conn, intake_world, direccion):
    def crear(**datos):
        return _previa(conn, "equipo", direccion, None, "crear", nombre="Compras",
                       aprobacion="direccion", **datos)

    assert ("evidencia", "falta") in _errores(crear())
    assert ("evidencia", "falta") in _errores(crear(evidencia=[]))
    assert ("evidencia", "contradice") in _errores(crear(evidencia=["test record"],
                                                         sin_evidencia=True))
    assert ("evidencia", "no_es_del_espacio") in _errores(crear(evidencia=["una foto"]))
    assert crear(sin_evidencia=True)["ok"] is True
    assert crear(evidencia=["test record", "test record"])["ok"] is True


def test_quien_aprueba_se_dice(conn, intake_world, direccion):
    oeste = intake_world["west-studio"]

    def crear(**datos):
        return _previa(conn, "equipo", direccion, None, "crear", nombre="Compras",
                       evidencia=["test record"], **datos)

    assert ("aprobacion", "falta") in _errores(crear())
    assert ("aprobacion", "no_existe") in _errores(crear(aprobacion="nadie"))
    assert ("referente", "falta") in _errores(crear(aprobacion="referente"))
    assert ("referente", "no_es_integrante_activo") in _errores(
        crear(aprobacion="referente", referente_id=_persona(intake_world, "Sam North",
                                                            "west-studio")))
    assert ("referente", "no_es_integrante_activo") in _errores(
        crear(aprobacion="referente", referente_id=INVENTADO))
    assert ("referente", "mal_formado") in _errores(
        crear(aprobacion="referente", referente_id="no-es-un-id"))
    assert ("referente", "no_corresponde") in _errores(
        crear(aprobacion="direccion", referente_id=_persona(intake_world, "Sam North")))
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (_persona(intake_world, "Sam Noble"),))
    conn.commit()
    assert ("referente", "no_es_integrante_activo") in _errores(
        crear(aprobacion="referente", referente_id=_persona(intake_world, "Sam Noble")))
    assert _cambios(conn, oeste["id"]) == []


def test_el_nombre_no_repite_el_de_otra_area_vigente(conn, intake_world, direccion):
    norte = intake_world["north-lab"]

    def crear(nombre):
        return _crear(conn, "equipo", direccion, None, nombre=nombre, aprobacion="direccion",
                      evidencia=["test record"])

    assert ("nombre", "falta") in _errores(crear("   "))
    assert ("nombre", "demasiado_largo") in _errores(crear("x" * 81))
    assert ("nombre", "ya_existe") in _errores(crear(" field services "))
    # Con un área archivada del mismo nombre, sí: su slug no se repite.
    with admin(conn) as cur:
        cur.execute("""insert into area (workspace_id, slug, nombre, archivada_en)
                       values (%s, 'compras', 'Compras', now())""", (norte["id"],))
    conn.commit()
    r = crear("Compras")
    assert r["ok"] is True, r
    assert _area(conn, r["area_id"])["slug"] == "compras-2"


def test_un_area_creada_acepta_la_carga_de_una_tarea(conn, intake_world, direccion, sesion):
    norte = intake_world["north-lab"]
    r = _crear(conn, "equipo", direccion, None, nombre="Compras", aprobacion="direccion",
               evidencia=["test record"])
    assert r["ok"] is True, r
    # Sam North pasa a Compras (el cambio de área es de la J7-7).
    with admin(conn) as cur:
        cur.execute("update membership set area_id = %s where id = %s",
                    (r["area_id"], _persona(intake_world, "Sam North")))
    conn.commit()
    carga = _cargar(conn, sesion, intake_world)
    assert carga["ok"] is True, carga
    (tarea,) = _filas(conn, "select area_id from task where id = %s", carga["task_id"])
    assert str(tarea["area_id"]) == r["area_id"]
    assert _problemas(conn, norte["id"]) == []


# --- Renombrar ----------------------------------------------------------------------------------

def test_renombrar_cambia_solo_el_nombre(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    field = norte["areas"]["field"]
    r = _renombrar(conn, "equipo", direccion, None, field, "Servicios de campo")
    assert r["ok"] is True, r
    area = _area(conn, field)
    assert area["nombre"] == "Servicios de campo" and area["slug"] == "field"
    assert str(area["referente_membership_id"]) == _persona(intake_world, "Taylor Quinn")
    (cambio,) = _cambios(conn, norte["id"])
    assert cambio["clase"] == "area_renombrada"
    assert cambio["antes"] == {"nombre": "Field Services"}
    assert cambio["despues"]["nombre"] == "Servicios de campo"
    assert _problemas(conn, norte["id"]) == []
    # Ni el nombre de otra vigente, ni el mismo, ni un área de otro espacio.
    assert ("nombre", "ya_existe") in _errores(
        _renombrar(conn, "equipo", direccion, None, field, "Quality Guild"))
    assert ("nombre", "sin_cambio") in _errores(
        _renombrar(conn, "equipo", direccion, None, field, "Servicios de campo"))
    assert ("area", "no_existe") in _errores(
        _renombrar(conn, "equipo", direccion, None,
                   intake_world["west-studio"]["areas"]["field"], "Otra"))


# --- Archivar -----------------------------------------------------------------------------------

def test_archivar_se_niega_con_gente(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    r = _archivar(conn, "equipo", direccion, None, norte["areas"]["quality"])
    assert ("area", "tiene_personas") in _errores(r)
    assert _area(conn, norte["areas"]["quality"])["archivada_en"] is None
    assert _cambios(conn, norte["id"]) == []


def test_archivar_se_niega_con_tareas_abiertas_y_se_puede_sin_ellas(conn, intake_world,
                                                                     direccion):
    norte = intake_world["north-lab"]
    abierta = _crear(conn, "equipo", direccion, None, nombre="Ventas", aprobacion="direccion",
                     evidencia=["test record"])
    nueva = _crear(conn, "equipo", direccion, None, nombre="Compras", aprobacion="direccion",
                   evidencia=["test record"])
    with admin(conn) as cur:
        for area, estado in ((abierta["area_id"], "en_curso"), (nueva["area_id"], "terminada"),
                             (nueva["area_id"], "cancelada")):
            cur.execute("""insert into task (workspace_id, objective_id, titulo, area_id, estado)
                           values (%s, %s, 'Comprar el switch', %s, %s)""",
                        (norte["id"], norte["objectives"][0], area, estado))
    conn.commit()
    assert ("area", "tiene_tareas_abiertas") in _errores(
        _archivar(conn, "equipo", direccion, None, abierta["area_id"]))
    # Con sus tareas cerradas, sí.
    r = _archivar(conn, "equipo", direccion, None, nueva["area_id"])
    assert r["ok"] is True, r
    assert _area(conn, nueva["area_id"])["archivada_en"] is not None
    cambio = _cambios(conn, norte["id"])[-1]
    assert cambio["clase"] == "area_archivada"
    assert cambio["antes"]["nombre"] == "Compras" and cambio["despues"]["estado"] == "archivada"
    assert _problemas(conn, norte["id"]) == []
    # Ya archivada: ni otra vez, ni renombrarla.
    assert ("area", "ya_archivada") in _errores(
        _archivar(conn, "equipo", direccion, None, nueva["area_id"]))
    assert ("area", "archivada") in _errores(
        _renombrar(conn, "equipo", direccion, None, nueva["area_id"], "Compras viejas"))


# --- La clave y la huella -----------------------------------------------------------------------

def test_la_misma_clave_devuelve_lo_mismo(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    previa = _previa(conn, "equipo", direccion, None, "crear", nombre="Compras",
                     aprobacion="direccion", evidencia=["test record"])
    clave = secrets.token_urlsafe(18)
    primera = _crear(conn, "equipo", direccion, None, nombre="Compras", aprobacion="direccion",
                     evidencia=["test record"], clave=clave, huella=previa["huella"])
    otra_vez = _crear(conn, "equipo", direccion, None, nombre="Compras", aprobacion="direccion",
                      evidencia=["test record"], clave=clave, huella=previa["huella"])
    assert primera["ok"] and otra_vez["ok"]
    assert otra_vez["repetida"] is True and otra_vez["area_id"] == primera["area_id"]
    assert len(_cambios(conn, norte["id"])) == 1
    assert len(_filas(conn, "select 1 from area where workspace_id = %s and nombre = 'Compras'",
                      norte["id"])) == 1
    # La misma clave con otros datos, no.
    assert ("clave", "usada_con_otros_datos") in _errores(
        _crear(conn, "equipo", direccion, None, nombre="Ventas", aprobacion="direccion",
               evidencia=["test record"], clave=clave))


def test_sin_clave_o_sin_huella_no_se_escribe(conn, intake_world, direccion):
    norte = intake_world["north-lab"]
    assert ("clave", "falta") in _errores(
        _crear(conn, "equipo", direccion, None, nombre="Compras", aprobacion="direccion",
               evidencia=["test record"], clave=None))
    assert ("clave", "mal_formada") in _errores(
        _crear(conn, "equipo", direccion, None, nombre="Compras", aprobacion="direccion",
               evidencia=["test record"], clave="corta"))
    assert ("huella", "falta") in _errores(
        _crear(conn, "equipo", direccion, None, nombre="Compras", aprobacion="direccion",
               evidencia=["test record"], huella=None))
    assert _cambios(conn, norte["id"]) == []


def test_si_el_equipo_cambio_desde_la_vista_previa_no_se_confirma(conn, intake_world,
                                                                   direccion):
    norte = intake_world["north-lab"]
    field = norte["areas"]["field"]
    previa = _previa(conn, "equipo", direccion, None, "renombrar", area_id=field,
                     nombre="Servicios de campo")
    # Mientras tanto, otro la renombró.
    with admin(conn) as cur:
        cur.execute("update area set nombre = 'Campo' where id = %s", (field,))
    conn.commit()
    r = _renombrar(conn, "equipo", direccion, None, field, "Servicios de campo",
                   huella=previa["huella"])
    assert ("huella", "el_equipo_cambio") in _errores(r)
    assert _area(conn, field)["nombre"] == "Campo"
    assert _cambios(conn, norte["id"]) == []


def test_el_administrador_crea_en_cualquier_espacio(conn, intake_world, sesion):
    oeste = intake_world["west-studio"]
    r = _crear(conn, "administracion", sesion, oeste["id"], nombre="Compras",
               aprobacion="direccion", evidencia=["test record"])
    assert r["ok"] is True, r
    (cambio,) = _cambios(conn, oeste["id"])
    assert cambio["puerta"] == "administracion" and cambio["hecho_por_membership_id"] is None
    assert _filas(conn, "select 1 from area where id = %s and workspace_id = %s",
                  r["area_id"], oeste["id"])


# --- La entrada HTTP ----------------------------------------------------------------------------

def _cuerpo(**datos) -> dict:
    return {"accion": "crear", "nombre": "Compras", "aprobacion": "direccion",
            "evidencia": ["test record"], "sin_evidencia": False, **datos}


def test_direccion_crea_un_area_desde_la_web(conn, intake_world, web):
    navegador = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    opciones = navegador.get(EQUIPO).json()
    assert opciones["tipos_de_evidencia"] == [{"tipo": "test record",
                                               "en_palabras": "test record"}]
    previa = navegador.post(REVISAR, json=_cuerpo())
    assert previa.status_code == 200, previa.text
    vista = previa.json()
    assert vista["despues"]["nombre"] == "Compras" and vista["problemas_nuevos"] == []
    clave = secrets.token_urlsafe(18)
    cuerpo = _cuerpo(clave=clave, huella=vista["huella"])
    creada = navegador.post(CONFIRMAR, json=cuerpo)
    assert creada.status_code == 201, creada.text
    assert creada.json()["repetida"] is False
    otra_vez = navegador.post(CONFIRMAR, json=cuerpo)
    assert otra_vez.status_code == 200 and otra_vez.json()["repetida"] is True
    equipo = navegador.get(EQUIPO).json()
    assert "Compras" in [a["nombre"] for a in equipo["areas"]]
    assert [c["clase"] for c in equipo["cambios"]] == ["area_creada"]
    assert equipo["problemas"] == []


def test_lo_que_no_se_puede_se_dice_con_palabras(conn, intake_world, web):
    norte = intake_world["north-lab"]
    navegador = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    respuesta = navegador.post(REVISAR, json={"accion": "archivar",
                                             "area_id": norte["areas"]["field"]})
    assert respuesta.status_code == 422
    (error,) = respuesta.json()["errores"]
    assert error["motivo"] == "tiene_personas" and "3 personas" in error["texto"]
    respuesta = navegador.post(REVISAR, json=_cuerpo(evidencia=None))
    assert respuesta.status_code == 422
    assert any(e["campo"] == "evidencia" and e["texto"] for e in respuesta.json()["errores"])
    # Un dato con otra forma, o una acción que no existe.
    assert navegador.post(REVISAR, json=_cuerpo(evidencia="test record")).status_code == 422
    assert navegador.post(REVISAR, json={"accion": "borrar"}).status_code == 422


@pytest.mark.parametrize("nombre", ["Taylor Quinn", "Sam North"])
def test_un_referente_o_un_integrante_no_puede(conn, intake_world, web, nombre):
    navegador = _navegador_del_equipo(web, conn, intake_world, nombre)
    for camino, cuerpo in ((REVISAR, _cuerpo()),
                           (CONFIRMAR, _cuerpo(clave=secrets.token_urlsafe(18),
                                               huella="0" * 64))):
        respuesta = navegador.post(camino, json=cuerpo)
        assert respuesta.status_code == 403
        assert respuesta.json()["texto"] == "Organizar el equipo le corresponde a Dirección."
    assert _cambios(conn, intake_world["north-lab"]["id"]) == []


def test_otro_sitio_o_sin_sesion_no_cambia_nada(conn, intake_world, web):
    navegador = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    assert navegador.post(REVISAR, json=_cuerpo(),
                          headers={"origin": "https://otro.example"}).status_code == 403
    assert web().post(REVISAR, json=_cuerpo()).status_code == 401
    assert web().post(_admin(intake_world["north-lab"]["id"], "/areas/revisar"),
                      json=_cuerpo()).status_code == 401


def test_el_administrador_por_su_puerta(conn, intake_world, web, administradora):
    oeste = intake_world["west-studio"]
    navegador = _navegador_de_administracion(web, conn, administradora)
    previa = navegador.post(_admin(oeste["id"], "/areas/revisar"), json=_cuerpo())
    assert previa.status_code == 200, previa.text
    creada = navegador.post(_admin(oeste["id"], "/areas"),
                            json=_cuerpo(clave=secrets.token_urlsafe(18),
                                         huella=previa.json()["huella"]))
    assert creada.status_code == 201, creada.text
    (cambio,) = _cambios(conn, oeste["id"])
    assert cambio["puerta"] == "administracion"
    # Un espacio que no existe, o un id que no es un id: 404.
    assert navegador.post(_admin(INVENTADO, "/areas/revisar"), json=_cuerpo()).status_code == 404
    assert navegador.post(_admin("no-es-un-id", "/areas/revisar"),
                          json=_cuerpo()).status_code == 404
    # Renombrar y archivar, por la misma puerta.
    area = creada.json()["area_id"]
    previa = navegador.post(_admin(oeste["id"], "/areas/revisar"),
                            json={"accion": "renombrar", "area_id": area, "nombre": "Ventas"})
    assert previa.status_code == 200, previa.text
    renombrada = navegador.post(_admin(oeste["id"], "/areas"),
                                json={"accion": "renombrar", "area_id": area, "nombre": "Ventas",
                                      "clave": secrets.token_urlsafe(18),
                                      "huella": previa.json()["huella"]})
    assert renombrada.status_code == 201, renombrada.text
    previa = navegador.post(_admin(oeste["id"], "/areas/revisar"),
                            json={"accion": "archivar", "area_id": area})
    archivada = navegador.post(_admin(oeste["id"], "/areas"),
                               json={"accion": "archivar", "area_id": area,
                                     "clave": secrets.token_urlsafe(18),
                                     "huella": previa.json()["huella"]})
    assert archivada.status_code == 201, archivada.text
    assert [c["clase"] for c in _cambios(conn, oeste["id"])] == [
        "area_creada", "area_renombrada", "area_archivada"]
    assert _problemas(conn, oeste["id"]) == []
