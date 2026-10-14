"""La creación de un objetivo desde la web (ADR 0023, decisiones 1 y 5 y punto 11; porción J3 de
`odd/tasks/plataforma-jerarquias.md`, tarea J3-2; migración 0068): la capa de garantías, en la
base y en la entrada HTTP.

- **Quién crea:** el administrador de plataforma, por su puerta, en cualquier espacio; Dirección
  (el integrante cuyo rol tiene la autoridad final), por la puerta del equipo, sólo en su espacio.
  Un integrante o un referente no crea objetivos, aunque la web le esconda el botón.
- **La crea una función de la base** (`crear_objetivo_web`, `security definer` de `leda_owner`,
  sólo para `leda_app`): comprueba la sesión de la puerta en cada llamada y fija ella misma el
  espacio, así que la RLS no le deja encontrar un objetivo ni una persona de otro.
- **De qué cuelga:** de ninguno o de un objetivo abierto del mismo espacio que no sea operativo
  (mecánica §1: debajo de un operativo van tareas); nunca de otro espacio, tampoco por la base
  (claves compuestas). Un solo padre: la tabla tiene una sola columna.
- **El tipo, según dónde cuelga** (punto 11): sin padre, estratégico; de un estratégico, hito u
  operativo; de un hito, operativo.
- **Lo que deja:** el objetivo, su evento `activo` (el estado es la proyección) y la auditoría
  `crear_objetivo` con quién lo creó y por qué puerta. Una sola vez por clave.
- **Las opciones:** los objetivos de los que puede colgar, con los tipos que admite cada uno, los
  referentes de área activos para el referente, los nombres de los niveles del pack y los días
  hábiles para la fecha.
- **Las decisiones del usuario del 2026-10-14** (tarea J3-2b; migración 0069): el objetivo lleva
  fecha, obligatoria, con el mismo calendario que las tareas (un día hábil del espacio, hoy o
  después, y hoy sólo si la jornada no cerró); y el referente es siempre un referente activo de un
  área de ese espacio, no cualquier integrante.
"""

from __future__ import annotations

import re
import secrets
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import psycopg
import pytest

from leda.db import admin, espacio
from tests.garantias.test_carga_de_tareas import (  # noqa: F401 -- `administradora`, `sesion`
    AHORA,                                         # y `web` son las fixtures
    AYER,
    FERIADO,
    HOY,
    SABADO,
    VIERNES,
    _entrar,
    _hash,
    _navegador_de_administracion,
    _navegador_del_equipo,
    _proximo_habil_real,
    _revocar,
    administradora,
    sesion,
    sin_espacio,
    web,
)

FUNCIONES_DE_LA_WEB = ("crear_objetivo_web", "opciones_del_objetivo")

NIVELES_POR_DEFECTO = {"estrategico": "objetivo estratégico", "hito": "hito",
                       "operativo": "objetivo operativo"}


# --- Ayudas ---------------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _referentes_de_area(request):
    """Los referentes de área de los dos espacios (decisión del usuario, 2026-10-14: el referente
    de un objetivo es un referente activo de un área): Taylor Quinn, de Field Services; Sam Noble,
    de Quality Guild. Sam North y Morgan Hale no son referentes de ningún área."""
    if "intake_world" not in request.fixturenames:
        return
    mundo, conn = request.getfixturevalue("intake_world"), request.getfixturevalue("conn")
    with admin(conn) as cur:
        for datos in mundo.values():
            for area, nombre in (("field", "Taylor Quinn"), ("quality", "Sam Noble")):
                cur.execute("update area set referente_membership_id = %s where id = %s",
                            (datos["people"][nombre]["membership_id"], datos["areas"][area]))
    conn.commit()


def _norte(mundo: dict) -> dict:
    return mundo["north-lab"]


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


def _objetivo(conn, ws: str, tipo: str, titulo: str, *, padre: str | None = None,
              estado: str = "activo") -> str:
    with admin(conn) as cur:
        cur.execute("""insert into objective (workspace_id, parent_id, tipo, titulo, estado)
                       values (%s, %s, %s, %s, %s) returning id""",
                    (ws, padre, tipo, titulo, estado))
        oid = str(cur.fetchone()["id"])
    conn.commit()
    return oid


def _datos(mundo: dict, **cambios) -> dict:
    """Un objetivo estratégico válido en North Lab, con Taylor Quinn (referente de Field
    Services) de referente y para el viernes 16/10/2026, visto el miércoles 14 al mediodía."""
    datos = {
        "puerta": "administracion",
        "espacio": _norte(mundo)["id"],
        "titulo": "Poner el módem colgando en la pared",
        "descripcion": None,
        "padre": None,
        "tipo": "estrategico",
        "referente": _persona(mundo, "Taylor Quinn"),
        "fecha": VIERNES,
        "clave": secrets.token_urlsafe(18),
        "ahora": AHORA,
    }
    datos.update(cambios)
    return datos


def _llamar(cur, token: str, d: dict) -> dict:
    cur.execute(
        """select crear_objetivo_web(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) as r""",
        (d["puerta"], _hash(token), d["espacio"], d["titulo"], d["descripcion"], d["padre"],
         d["tipo"], d["referente"], d["fecha"], d["clave"], d["ahora"]))
    return cur.fetchone()["r"]


def _crear(conn, token: str, mundo: dict, **cambios) -> dict:
    with sin_espacio(conn) as cur:
        resultado = _llamar(cur, token, _datos(mundo, **cambios))
    conn.commit()
    return resultado


def _como_direccion(conn, mundo: dict, **cambios) -> dict:
    token = _sesion_del_equipo(conn, mundo, "Morgan Hale")
    return _crear(conn, token, mundo, **{"puerta": "equipo", "espacio": None, **cambios})


def _errores(resultado: dict) -> set[tuple[str, str]]:
    assert resultado["ok"] is False, resultado
    return {(e["campo"], e["motivo"]) for e in resultado["errores"]}


def _contar(conn, tabla: str, donde: str = "true", *args) -> int:
    with admin(conn) as cur:
        cur.execute(f"select count(*) n from {tabla} where {donde}", args)
        n = cur.fetchone()["n"]
    conn.commit()
    return n


def _fila(conn, consulta: str, *args) -> dict | None:
    with admin(conn) as cur:
        cur.execute(consulta, args)
        fila = cur.fetchone()
    conn.commit()
    return fila


def _creados(conn) -> int:
    return _contar(conn, "objective", "titulo = 'Poner el módem colgando en la pared'")


def _nada_creado(conn) -> None:
    assert _creados(conn) == 0
    assert _contar(conn, "creacion_de_objetivo") == 0
    assert _contar(conn, "audit_log", "accion = 'crear_objetivo'") == 0


def _opciones(conn, puerta: str, token: str, espacio_id: str | None,
              ahora: datetime = AHORA) -> dict:
    with sin_espacio(conn) as cur:
        cur.execute("select opciones_del_objetivo(%s, %s, %s, %s) as r",
                    (puerta, _hash(token), espacio_id, ahora))
        r = cur.fetchone()["r"]
    conn.commit()
    return r


# --- Las funciones y la tabla ---------------------------------------------------------------

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
            (list(FUNCIONES_DE_LA_WEB) + ["quien_crea_el_objetivo"],))
        filas = {f["proname"]: f for f in cur.fetchall()}
    conn.commit()
    assert set(filas) == set(FUNCIONES_DE_LA_WEB) | {"quien_crea_el_objetivo"}
    for nombre, f in filas.items():
        assert f["rolname"] == "leda_owner", nombre
        assert any(c.startswith("search_path=") and c.endswith("pg_temp")
                   for c in f["proconfig"] or []), nombre
        assert not f["de_public"] and not f["de_gateway"], nombre
    for nombre in FUNCIONES_DE_LA_WEB:
        assert filas[nombre]["prosecdef"] and filas[nombre]["de_app"], nombre
    # Quién crea se resuelve adentro de las dos funciones: la web no la llama sola.
    assert not filas["quien_crea_el_objetivo"]["de_app"]


def test_la_aplicacion_no_toca_las_claves_de_creacion(conn, intake_world):
    norte = _norte(intake_world)
    with espacio(conn, norte["id"]) as cur:
        for orden in ("select * from creacion_de_objetivo", "delete from creacion_de_objetivo",
                      "insert into creacion_de_objetivo (workspace_id, clave, huella, "
                      "objective_id) values (gen_random_uuid(), 'x', 'x', gen_random_uuid())"):
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                cur.execute(orden)
    conn.commit()


def test_la_aplicacion_no_escribe_objetivos_directo_y_la_funcion_si(conn, intake_world, sesion):
    """Como `task`: `leda_app` lee los objetivos y no los escribe; los crea la base."""
    norte = _norte(intake_world)
    objetivo = norte["objectives"][0]
    with espacio(conn, norte["id"]) as cur:
        for orden, args in (
                ("insert into objective (workspace_id, tipo, titulo) "
                 "values (%s, 'estrategico', 'Directo')", (norte["id"],)),
                ("update objective set titulo = 'Cambiado' where id = %s", (objetivo,)),
                ("update objective set estado = 'cancelado' where id = %s", (objetivo,)),
                ("delete from objective where id = %s", (objetivo,))):
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                cur.execute(orden, args)
        cur.execute("select count(*) n from objective")
        assert cur.fetchone()["n"] == 3, "leer, sí"
    conn.commit()
    fila = _fila(conn, "select titulo, estado::text e from objective where id = %s", objetivo)
    assert (fila["e"], fila["titulo"]) == ("activo", "Reduce service delay 1")
    assert _contar(conn, "objective", "titulo = 'Directo'") == 0
    assert _crear(conn, sesion, intake_world)["ok"] is True
    assert _creados(conn) == 1


def test_el_estado_de_un_objetivo_sigue_cambiando_por_su_evento(conn, intake_world):
    """Revisión RDD `review-bef6a4c90272c9c7`: sin `update` sobre `objective`, la proyección del
    estado la aplica la base (`aplicar_evento_objetivo`, elevada, como la de la tarea) cuando
    `leda_app` agrega el evento; y el evento sigue sin cruzar de espacio."""
    norte, oeste = _norte(intake_world), intake_world["west-studio"]
    objetivo = norte["objectives"][0]
    with espacio(conn, norte["id"]) as cur:
        cur.execute("""insert into objective_state_event
                         (objective_id, estado_anterior, estado_nuevo, actor_kind, motivo)
                       values (%s, 'activo', 'suspendido', 'persona', 'en pausa')""",
                    (objetivo,))
        cur.execute("select current_setting('leda.workspace_id', true) ws")
        assert cur.fetchone()["ws"] == norte["id"], "el disparador no devolvió el espacio"
    conn.commit()
    assert _fila(conn, "select estado::text e from objective where id = %s",
                 objetivo)["e"] == "suspendido"
    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.Error), conn.transaction():
            cur.execute("""insert into objective_state_event
                             (objective_id, estado_nuevo, actor_kind)
                           values (%s, 'cancelado', 'persona')""", (oeste["objectives"][0],))
    conn.commit()
    assert _fila(conn, "select estado::text e from objective where id = %s",
                 oeste["objectives"][0])["e"] == "activo"


def test_la_funcion_que_aplica_el_estado_es_elevada_y_no_la_llama_nadie(conn):
    fila = _fila(conn, """select r.rolname, p.prosecdef, p.proconfig,
                                 has_function_privilege('public', p.oid, 'execute') de_public
                            from pg_proc p join pg_roles r on r.oid = p.proowner
                           where p.oid = 'leda.aplicar_evento_objetivo()'::regprocedure""")
    assert fila["rolname"] == "leda_owner" and fila["prosecdef"] and not fila["de_public"]
    assert any(c.startswith("search_path=") and c.endswith("pg_temp")
               for c in fila["proconfig"] or [])


def test_la_tabla_de_claves_tiene_rls_forzada(conn):
    fila = _fila(conn, """select relrowsecurity r, relforcerowsecurity f from pg_class
                           where oid = 'leda.creacion_de_objetivo'::regclass""")
    assert fila["r"] and fila["f"]


def test_la_herramienta_de_chat_para_crear_objetivos_se_retiro():
    """ADR 0017, decisión 1; ADR 0023, decisión 6: por chat no se crean objetivos."""
    from leda import herramientas

    assert "crear_objetivo" not in herramientas.REGISTRO
    assert not hasattr(herramientas, "_crear_objetivo")


# --- Ningún objetivo cuelga de otro espacio, tampoco por la base -------------------------------

def test_la_base_no_deja_colgar_un_objetivo_de_otro_espacio(conn, intake_world):
    norte, oeste = _norte(intake_world), intake_world["west-studio"]
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            cur.execute("""insert into objective (workspace_id, parent_id, tipo, titulo)
                           values (%s, %s, 'hito', 'Cruzado')""",
                        (norte["id"], oeste["objectives"][0]))
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            cur.execute("""insert into objective (workspace_id, tipo, titulo,
                                                  referente_membership_id)
                           values (%s, 'estrategico', 'Cruzado', %s)""",
                        (norte["id"], _persona(intake_world, "Sam North", "west-studio")))
    conn.commit()
    assert _contar(conn, "objective", "titulo = 'Cruzado'") == 0


# --- Crear por la puerta de administración ---------------------------------------------------

def test_el_administrador_crea_un_objetivo_con_su_evento_y_su_auditoria(
        conn, intake_world, sesion, administradora):
    with admin(conn) as cur:
        cur.execute("select set_config('leda.nucleo_hash', 'nucleo-de-prueba', false)")
    conn.commit()
    norte = _norte(intake_world)
    r = _crear(conn, sesion, intake_world, descripcion="  Con los tarugos del depósito  ",
               titulo="  Poner el módem colgando en la pared  ")
    assert r["ok"] is True and r["repetida"] is False, r
    objetivo = _fila(conn, "select * from objective where id = %s", r["objective_id"])
    assert str(objetivo["workspace_id"]) == norte["id"]
    assert objetivo["titulo"] == "Poner el módem colgando en la pared"
    assert objetivo["descripcion"] == "Con los tarugos del depósito"
    assert objetivo["tipo"] == "estrategico" and objetivo["parent_id"] is None
    assert str(objetivo["referente_membership_id"]) == _persona(intake_world, "Taylor Quinn")
    assert objetivo["estado"] == "activo"
    assert objetivo["fecha_objetivo"] == VIERNES

    eventos = _fila(conn, "select count(*) n, min(estado_nuevo::text) e, "
                          "min(actor_kind::text) k, min(actor_app_user_id::text) a "
                          "from objective_state_event where objective_id = %s",
                    r["objective_id"])
    assert (eventos["n"], eventos["e"], eventos["k"], eventos["a"]) == (
        1, "activo", "persona", administradora)

    auditoria = _fila(conn, "select * from audit_log where accion = 'crear_objetivo'")
    assert str(auditoria["workspace_id"]) == norte["id"]
    assert auditoria["sujeto_tipo"] == "objective"
    assert str(auditoria["sujeto_id"]) == r["objective_id"]
    assert str(auditoria["actor_app_user_id"]) == administradora
    assert auditoria["actor_kind"] == "persona"
    assert auditoria["pack_hash"] == "hash-0"
    assert auditoria["nucleo_hash"] == "nucleo-de-prueba"
    detalle = auditoria["detalle"]
    assert detalle["origen"] == "web" and detalle["puerta"] == "administracion"
    assert detalle["creado_por_app_user_id"] == administradora
    assert detalle["creado_por_membership_id"] is None
    assert detalle["sesion_de_administracion_id"]
    assert detalle["tipo"] == "estrategico" and detalle["parent_id"] is None
    assert detalle["referente_membership_id"] == _persona(intake_world, "Taylor Quinn")
    assert detalle["fecha_objetivo"] == VIERNES.isoformat()
    # Sin texto libre ni el token: lo escrito está en el objetivo, no en la auditoría.
    texto = str(detalle)
    assert "módem" not in texto and "tarugos" not in texto
    assert sesion not in texto and _hash(sesion) not in texto
    assert _contar(conn, "creacion_de_objetivo") == 1


def test_el_administrador_crea_en_cualquier_espacio_y_queda_en_ese(
        conn, intake_world, sesion):
    oeste = intake_world["west-studio"]
    with espacio(conn, _norte(intake_world)["id"]) as cur:
        r = _llamar(cur, sesion, _datos(
            intake_world, espacio=oeste["id"],
            referente=_persona(intake_world, "Taylor Quinn", "west-studio")))
        cur.execute("select current_setting('leda.workspace_id', true) ws")
        assert cur.fetchone()["ws"] == _norte(intake_world)["id"], (
            "la función no devolvió el espacio previo")
    conn.commit()
    assert r["ok"] is True, r
    for tabla, columna in (("objective", "id"), ("creacion_de_objetivo", "objective_id")):
        fila = _fila(conn, f"select workspace_id w from {tabla} where {columna} = %s",
                     r["objective_id"])
        assert str(fila["w"]) == oeste["id"], tabla
    assert str(_fila(conn, "select workspace_id w from audit_log "
                           "where accion = 'crear_objetivo'")["w"]) == oeste["id"]


# --- Crear por la puerta del equipo: sólo Dirección ------------------------------------------

def test_direccion_crea_un_objetivo_de_su_equipo(conn, intake_world):
    norte = _norte(intake_world)
    morgan = norte["people"]["Morgan Hale"]
    raiz = _objetivo(conn, norte["id"], "estrategico", "Ordenar la sala de racks")
    r = _como_direccion(conn, intake_world, padre=raiz, tipo="hito")
    assert r["ok"] is True, r
    objetivo = _fila(conn, "select * from objective where id = %s", r["objective_id"])
    assert (objetivo["tipo"], str(objetivo["parent_id"])) == ("hito", raiz)
    assert str(objetivo["workspace_id"]) == norte["id"] and objetivo["estado"] == "activo"
    evento = _fila(conn, "select actor_app_user_id a from objective_state_event "
                         "where objective_id = %s", r["objective_id"])
    assert str(evento["a"]) == morgan["app_user_id"]
    auditoria = _fila(conn, "select * from audit_log where accion = 'crear_objetivo'")
    assert str(auditoria["actor_app_user_id"]) == morgan["app_user_id"]
    detalle = auditoria["detalle"]
    assert detalle["puerta"] == "equipo"
    assert detalle["creado_por_membership_id"] == morgan["membership_id"]
    assert detalle["sesion_web_id"]
    assert "sesion_de_administracion_id" not in detalle


def test_un_integrante_o_un_referente_no_crea_objetivos(conn, intake_world):
    norte = _norte(intake_world)
    # Taylor Quinn, referente del área, y Sam North, integrante.
    with admin(conn) as cur:
        cur.execute("update area set referente_membership_id = %s where id = %s",
                    (_persona(intake_world, "Taylor Quinn"), norte["areas"]["field"]))
    conn.commit()
    for nombre in ("Taylor Quinn", "Sam North"):
        token = _sesion_del_equipo(conn, intake_world, nombre)
        assert _errores(_crear(conn, token, intake_world, puerta="equipo", espacio=None)) == {
            ("sesion", "sin_autoridad")}, nombre
        assert _errores(_opciones(conn, "equipo", token, None)) == {
            ("sesion", "sin_autoridad")}, nombre
    _nada_creado(conn)


def test_una_sesion_de_un_espacio_no_crea_en_otro(conn, intake_world, sesion):
    oeste = intake_world["west-studio"]
    token = _sesion_del_equipo(conn, intake_world, "Morgan Hale")
    r = _crear(conn, token, intake_world, puerta="equipo", espacio=oeste["id"],
               referente=_persona(intake_world, "Taylor Quinn", "west-studio"))
    assert _errores(r) == {("espacio", "no_existe")}
    assert _errores(_opciones(conn, "equipo", token, oeste["id"])) == {
        ("espacio", "no_existe")}
    # Y lo de otro espacio no entra: ni el padre ni el referente.
    r = _crear(conn, token, intake_world, puerta="equipo", espacio=None,
               padre=oeste["objectives"][0], tipo="operativo",
               referente=_persona(intake_world, "Taylor Quinn", "west-studio"))
    assert _errores(r) == {("padre", "no_existe"), ("referente", "no_es_integrante_activo")}
    # Con la sesión de administración, lo mismo: el referente de un área de otro espacio no es
    # referente acá.
    r = _crear(conn, sesion, intake_world, padre=oeste["objectives"][0], tipo="operativo",
               referente=_persona(intake_world, "Taylor Quinn", "west-studio"))
    assert _errores(r) == {("padre", "no_existe"), ("referente", "no_es_integrante_activo")}
    _nada_creado(conn)
    assert _contar(conn, "objective", "workspace_id = %s", oeste["id"]) == 3


def test_cada_puerta_pide_su_propia_sesion(conn, intake_world, administradora):
    administracion = _entrar(conn, administradora)
    equipo = _sesion_del_equipo(conn, intake_world, "Morgan Hale")
    # La sesión del equipo no abre la puerta de administración ni la de administración la del
    # equipo; un token cualquiera, ninguna.
    assert _errores(_crear(conn, equipo, intake_world)) == {("sesion", "sin_sesion")}
    assert _errores(_crear(conn, administracion, intake_world, puerta="equipo",
                           espacio=None)) == {("sesion", "sin_sesion")}
    for puerta in ("administracion", "equipo"):
        assert _errores(_crear(conn, secrets.token_urlsafe(32), intake_world,
                               puerta=puerta)) == {("sesion", "sin_sesion")}
    assert _errores(_crear(conn, administracion, intake_world, puerta="otra")) == {
        ("sesion", "sin_sesion")}
    # Con el rol revocado, la sesión de administración se corta en la llamada.
    _revocar(conn, administradora)
    assert _errores(_crear(conn, administracion, intake_world)) == {("sesion", "sin_sesion")}
    _nada_creado(conn)


def test_un_espacio_que_no_existe_no_crea(conn, intake_world, sesion):
    r = _crear(conn, sesion, intake_world, espacio="00000000-0000-0000-0000-000000000000")
    assert _errores(r) == {("espacio", "no_existe")}
    assert _errores(_crear(conn, sesion, intake_world, espacio=None)) == {
        ("espacio", "no_existe")}
    _nada_creado(conn)


# --- Lo que no se crea ----------------------------------------------------------------------

def test_sin_los_datos_obligatorios_se_rechaza_todo_junto(conn, intake_world, sesion):
    r = _crear(conn, sesion, intake_world, titulo="   ", tipo=None, referente=None, fecha=None,
               clave=None)
    assert _errores(r) == {("titulo", "falta"), ("tipo", "falta"), ("referente", "falta"),
                           ("fecha", "falta"), ("clave", "falta")}
    r = _crear(conn, sesion, intake_world, clave="corta", tipo="campaña")
    assert _errores(r) == {("clave", "mal_formada"), ("tipo", "no_existe")}
    _nada_creado(conn)


def test_textos_demasiado_largos_no_se_crean(conn, intake_world, sesion):
    r = _crear(conn, sesion, intake_world, titulo="x" * 201, descripcion="y" * 801)
    assert _errores(r) == {("titulo", "demasiado_largo"), ("descripcion", "demasiado_largo")}
    assert _crear(conn, sesion, intake_world, titulo="x" * 200,
                  descripcion="y" * 800)["ok"] is True


@pytest.mark.parametrize("padre, tipo, vale", [
    (None, "estrategico", True), (None, "hito", False), (None, "operativo", False),
    ("estrategico", "hito", True), ("estrategico", "operativo", True),
    ("estrategico", "estrategico", False),
    ("hito", "operativo", True), ("hito", "hito", False), ("hito", "estrategico", False),
])
def test_el_tipo_depende_de_donde_cuelga(conn, intake_world, sesion, padre, tipo, vale):
    norte = _norte(intake_world)
    padre_id = _objetivo(conn, norte["id"], padre, f"Padre {padre}") if padre else None
    r = _crear(conn, sesion, intake_world, padre=padre_id, tipo=tipo)
    if vale:
        assert r["ok"] is True, r
        assert _fila(conn, "select tipo::text t from objective where id = %s",
                     r["objective_id"])["t"] == tipo
    else:
        assert _errores(r) == {("tipo", "no_corresponde")}
        _nada_creado(conn)


def test_de_un_operativo_no_cuelga_un_objetivo(conn, intake_world, sesion):
    operativo = _norte(intake_world)["objectives"][0]
    r = _crear(conn, sesion, intake_world, padre=operativo, tipo="operativo")
    assert _errores(r) == {("padre", "es_operativo")}
    _nada_creado(conn)


def test_el_padre_tiene_que_estar_abierto(conn, intake_world, sesion):
    norte = _norte(intake_world)
    cerrado = _objetivo(conn, norte["id"], "estrategico", "Cerrado", estado="terminado")
    r = _crear(conn, sesion, intake_world, padre=cerrado, tipo="hito")
    assert _errores(r) == {("padre", "no_esta_abierto")}
    propuesto = _objetivo(conn, norte["id"], "estrategico", "Propuesto", estado="propuesto")
    assert _crear(conn, sesion, intake_world, padre=propuesto, tipo="hito")["ok"] is True


def test_el_referente_tiene_que_ser_integrante_activo(conn, intake_world, sesion):
    # Sam Noble es el referente de Quality Guild, pero ya no es integrante activo.
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (_persona(intake_world, "Sam Noble"),))
    conn.commit()
    r = _crear(conn, sesion, intake_world, referente=_persona(intake_world, "Sam Noble"))
    assert _errores(r) == {("referente", "no_es_integrante_activo")}
    _nada_creado(conn)


@pytest.mark.parametrize("nombre", ["Sam North", "Morgan Hale"])
def test_el_referente_tiene_que_ser_referente_de_un_area(conn, intake_world, sesion, nombre):
    """Decisión del usuario (2026-10-14): un integrante activo que no es referente de ningún área
    (Sam North, integrante; Morgan Hale, Dirección) no es el referente de un objetivo."""
    r = _crear(conn, sesion, intake_world, referente=_persona(intake_world, nombre))
    assert _errores(r) == {("referente", "no_es_referente_de_un_area")}
    r = _como_direccion(conn, intake_world, referente=_persona(intake_world, nombre))
    assert _errores(r) == {("referente", "no_es_referente_de_un_area")}
    _nada_creado(conn)


def test_quien_deja_de_ser_referente_de_su_area_ya_no_es_referente(conn, intake_world, sesion):
    norte = _norte(intake_world)
    assert _crear(conn, sesion, intake_world,
                  referente=_persona(intake_world, "Sam Noble"))["ok"] is True
    with admin(conn) as cur:
        cur.execute("update area set referente_membership_id = null where id = %s",
                    (norte["areas"]["quality"],))
    conn.commit()
    r = _crear(conn, sesion, intake_world, titulo="Otro objetivo",
               referente=_persona(intake_world, "Sam Noble"))
    assert _errores(r) == {("referente", "no_es_referente_de_un_area")}
    assert _contar(conn, "objective", "titulo = 'Otro objetivo'") == 0


# --- La fecha, con el calendario de las tareas ------------------------------------------------

def test_la_fecha_se_guarda_y_hoy_vale_si_es_habil(conn, intake_world, sesion):
    r = _crear(conn, sesion, intake_world, fecha=HOY)
    assert r["ok"] is True, r
    assert _fila(conn, "select fecha_objetivo f from objective where id = %s",
                 r["objective_id"])["f"] == HOY


def test_la_fecha_tiene_que_ser_un_dia_habil_del_espacio(conn, intake_world, sesion):
    norte = _norte(intake_world)
    with admin(conn) as cur:
        cur.execute("insert into holiday (workspace_id, fecha, nombre) values (%s, %s, 'Feriado')",
                    (norte["id"], FERIADO))
    conn.commit()
    for fecha in (SABADO, SABADO + timedelta(days=1), FERIADO):
        assert _errores(_crear(conn, sesion, intake_world, fecha=fecha)) == {
            ("fecha", "no_es_dia_habil")}, fecha
    assert _errores(_crear(conn, sesion, intake_world, fecha=AYER)) == {
        ("fecha", "en_el_pasado")}
    _nada_creado(conn)
    # El feriado es de North Lab: en West Studio ese lunes es hábil.
    oeste = intake_world["west-studio"]
    assert _crear(conn, sesion, intake_world, espacio=oeste["id"], fecha=FERIADO,
                  referente=_persona(intake_world, "Taylor Quinn", "west-studio"))["ok"] is True


def test_hoy_ya_no_vale_cuando_cerro_la_jornada_del_espacio(conn, intake_world, sesion):
    al_cierre = datetime(2026, 10, 14, 18, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
    assert _errores(_crear(conn, sesion, intake_world, fecha=HOY, ahora=al_cierre)) == {
        ("fecha", "ya_cerro_el_dia")}
    _nada_creado(conn)
    assert _crear(conn, sesion, intake_world, fecha=VIERNES, ahora=al_cierre)["ok"] is True


def test_la_misma_clave_con_otra_fecha_se_rechaza(conn, intake_world, sesion):
    clave = secrets.token_urlsafe(18)
    assert _crear(conn, sesion, intake_world, clave=clave)["ok"] is True
    r = _crear(conn, sesion, intake_world, clave=clave, fecha=VIERNES + timedelta(days=3))
    assert _errores(r) == {("clave", "usada_con_otros_datos")}
    assert _creados(conn) == 1


# --- Una sola vez por clave -------------------------------------------------------------------

def test_la_misma_clave_con_los_mismos_datos_devuelve_el_mismo_objetivo(
        conn, intake_world, sesion):
    clave = secrets.token_urlsafe(18)
    primera = _crear(conn, sesion, intake_world, clave=clave)
    segunda = _crear(conn, sesion, intake_world, clave=clave)
    assert primera["ok"] and segunda["ok"]
    assert segunda["objective_id"] == primera["objective_id"]
    assert (primera["repetida"], segunda["repetida"]) == (False, True)
    assert _creados(conn) == 1
    assert _contar(conn, "audit_log", "accion = 'crear_objetivo'") == 1


def test_la_misma_clave_con_otros_datos_se_rechaza(conn, intake_world, sesion):
    clave = secrets.token_urlsafe(18)
    assert _crear(conn, sesion, intake_world, clave=clave)["ok"] is True
    r = _crear(conn, sesion, intake_world, clave=clave, titulo="Otro objetivo")
    assert _errores(r) == {("clave", "usada_con_otros_datos")}
    assert _contar(conn, "objective", "titulo = 'Otro objetivo'") == 0


def test_la_misma_clave_por_otra_puerta_es_otro_pedido(conn, intake_world, sesion):
    clave = secrets.token_urlsafe(18)
    assert _crear(conn, sesion, intake_world, clave=clave)["ok"] is True
    r = _como_direccion(conn, intake_world, clave=clave)
    assert _errores(r) == {("clave", "usada_con_otros_datos")}
    assert _creados(conn) == 1


# --- Las opciones del formulario --------------------------------------------------------------

def test_las_opciones_dicen_de_que_puede_colgar_y_quien_puede_ser_referente(
        conn, intake_world, sesion):
    norte = _norte(intake_world)
    raiz = _objetivo(conn, norte["id"], "estrategico", "Ordenar la sala de racks")
    hito = _objetivo(conn, norte["id"], "hito", "Primer rack", padre=raiz)
    _objetivo(conn, norte["id"], "estrategico", "Cerrado", estado="terminado")
    _objetivo(conn, intake_world["west-studio"]["id"], "estrategico", "Ajeno")
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (_persona(intake_world, "Sam Noble"),))
    conn.commit()
    r = _opciones(conn, "administracion", sesion, norte["id"])
    assert r["ok"] is True
    assert r["espacio"]["id"] == norte["id"]
    assert r["sin_padre"] == ["estrategico"]
    padres = {p["id"]: p for p in r["padres"]}
    assert set(padres) == {raiz, hito}, "ni los operativos, ni los cerrados, ni los ajenos"
    assert padres[raiz]["tipos"] == ["hito", "operativo"]
    assert padres[hito]["tipos"] == ["operativo"]
    assert padres[hito]["tipo"] == "hito"
    # El referente: sólo los referentes de área activos (Sam Noble, el de Quality Guild, no está
    # activo); ni Dirección ni un integrante.
    referentes = {p["nombre"]: p for p in r["referentes"]}
    assert set(referentes) == {"Taylor Quinn 1"}
    assert referentes["Taylor Quinn 1"]["membership_id"] == _persona(intake_world, "Taylor Quinn")
    assert referentes["Taylor Quinn 1"]["areas"] == ["Field Services"]
    assert "integrantes" not in r
    assert r["niveles"] == NIVELES_POR_DEFECTO
    assert "Ajeno" not in str(r) and "Taylor Quinn 2" not in str(r)
    # Dirección, por la puerta del equipo, ve lo mismo de su espacio.
    equipo = _opciones(conn, "equipo", _sesion_del_equipo(conn, intake_world, "Morgan Hale"),
                       None)
    assert equipo["ok"] is True and {p["id"] for p in equipo["padres"]} == {raiz, hito}


def test_las_opciones_traen_los_dias_habiles_para_la_fecha(conn, intake_world, sesion):
    norte = _norte(intake_world)
    with admin(conn) as cur:
        cur.execute("insert into holiday (workspace_id, fecha, nombre) values (%s, %s, 'Feriado')",
                    (norte["id"], FERIADO))
    conn.commit()
    r = _opciones(conn, "administracion", sesion, norte["id"])
    assert r["hoy"] == HOY.isoformat()
    habiles = r["calendario"]["dias_habiles"]
    assert habiles[0] == HOY.isoformat() and VIERNES.isoformat() in habiles
    assert SABADO.isoformat() not in habiles and FERIADO.isoformat() not in habiles
    # Un objetivo puede ir más lejos que una tarea: hasta un año.
    assert date.fromisoformat(habiles[-1]) >= HOY + timedelta(days=360)
    assert r["calendario"]["hasta"] >= habiles[-1]
    assert {"fecha": FERIADO.isoformat(), "nombre": "Feriado"} in r["calendario"]["feriados"]
    assert r["calendario"]["dias"] == ["lunes", "martes", "miercoles", "jueves", "viernes"]
    # Cerrada la jornada, hoy ya no se ofrece.
    al_cierre = datetime(2026, 10, 14, 18, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
    r = _opciones(conn, "administracion", sesion, norte["id"], al_cierre)
    assert r["calendario"]["dias_habiles"][0] == "2026-10-15"


def test_las_opciones_usan_los_nombres_de_los_niveles_del_pack(conn, intake_world, sesion):
    norte = _norte(intake_world)
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, 'niveles', %s::jsonb)""",
                    (norte["id"], '{"estrategico": "plan anual", "hito": "campaña"}'))
    conn.commit()
    r = _opciones(conn, "administracion", sesion, norte["id"])
    assert r["niveles"] == {"estrategico": "plan anual", "hito": "campaña",
                            "operativo": "objetivo operativo"}


def test_la_base_no_acepta_nombres_de_niveles_mal_formados(conn, intake_world):
    norte = _norte(intake_world)
    for valor in ('["hito"]', '{"tarea": "orden"}', '{"hito": ""}', '{"hito": 3}',
                  '{"hito": "%s"}' % ("x" * 61)):
        with admin(conn) as cur:
            with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
                cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                               values (%s, 'niveles', %s::jsonb)""", (norte["id"], valor))
        conn.commit()


def test_las_opciones_piden_una_sesion_y_un_espacio_que_exista(conn, intake_world,
                                                               administradora):
    norte = _norte(intake_world)
    assert _errores(_opciones(conn, "administracion", secrets.token_urlsafe(32),
                              norte["id"])) == {("sesion", "sin_sesion")}
    sesion = _entrar(conn, administradora)
    assert _errores(_opciones(conn, "administracion", sesion,
                              "00000000-0000-0000-0000-000000000000")) == {
        ("espacio", "no_existe")}


# --- El importador guarda los nombres de los niveles -----------------------------------------

def _importar_corework(conn, tmp_path, monkeypatch, niveles):
    import yaml

    from leda.importador import importar
    from tests.conftest import RAIZ

    monkeypatch.setenv("LEDA_BOT_TOKEN_COREWORK", "prueba:token")
    pack = yaml.safe_load((RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    pack["telegram"]["grupo_gestion_id"] = -1001
    pack.pop("niveles", None)
    if niveles is not None:
        pack["niveles"] = niveles
    ruta = tmp_path / "corework.yaml"
    ruta.write_text(yaml.safe_dump(pack, allow_unicode=True), "utf-8")
    r = importar(conn, ruta)
    fila = _fila(conn, """select valor from workspace_setting
                           where workspace_id = %s and clave = 'niveles'""", r.workspace_id)
    return r, (fila["valor"] if fila else None)


def test_el_importador_guarda_los_nombres_de_los_niveles_de_objetivo(
        conn, tmp_path, monkeypatch):
    r, guardado = _importar_corework(conn, tmp_path, monkeypatch, {
        "objetivo_estrategico": " plan anual de mantenimiento ", "hito": "campaña",
        "objetivo_operativo": "equipo o línea", "tarea": "orden de trabajo",
        "subtarea": "paso"})
    assert guardado == {"estrategico": "plan anual de mantenimiento", "hito": "campaña",
                        "operativo": "equipo o línea"}
    # Uno que falta o que no es un nombre no se guarda (y el pack lo avisa); sin niveles, se saca.
    r, guardado = _importar_corework(conn, tmp_path, monkeypatch, {
        "objetivo_estrategico": "plan", "hito": "", "objetivo_operativo": ["x"]})
    assert guardado == {"estrategico": "plan"}
    assert any("niveles" in a for a in r.advertencias)
    _, guardado = _importar_corework(conn, tmp_path, monkeypatch, None)
    assert guardado is None


# --- La vuelta atrás ------------------------------------------------------------------------

def test_el_rollback_de_la_0068_se_niega_si_hay_objetivos_creados(conn, intake_world, sesion):
    rollbacks = Path(__file__).resolve().parents[2] / "db" / "rollbacks"
    (archivo,) = rollbacks.glob("0068_*.sql")
    guarda = re.findall(r"do \$\$.*?end \$\$;", archivo.read_text("utf-8"), re.S)[0]
    assert _crear(conn, sesion, intake_world)["ok"] is True
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.RaiseException, match="0068 rollback refused"), \
                conn.transaction():
            cur.execute("set local search_path = leda, public")
            cur.execute(guarda)
    conn.commit()
    assert _contar(conn, "creacion_de_objetivo") == 1


# --- La entrada HTTP ------------------------------------------------------------------------

def _cuerpo(mundo: dict, **cambios) -> dict:
    cuerpo = {
        "titulo": "Poner el módem colgando en la pared",
        "tipo": "estrategico",
        "referente_id": _persona(mundo, "Taylor Quinn"),
        "fecha": _proximo_habil_real().isoformat(),
        "clave": secrets.token_urlsafe(18),
    }
    cuerpo.update(cambios)
    return cuerpo


def test_la_puerta_de_administracion_ofrece_y_crea(web, conn, intake_world, administradora):
    norte = _norte(intake_world)
    base = f"/app/admin/api/espacios/{norte['id']}/objetivos"
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = navegador.get(f"{base}/opciones")
    assert r.status_code == 200, r.text
    assert r.headers["cache-control"] == "no-store"
    assert "ok" not in r.json() and r.json()["sin_padre"] == ["estrategico"]
    cuerpo = _cuerpo(intake_world)
    r = navegador.post(base, json=cuerpo)
    assert r.status_code == 201, r.text
    assert r.headers["cache-control"] == "no-store"
    objetivo = r.json()["objective_id"]
    otra = navegador.post(base, json=cuerpo)
    assert otra.status_code == 200 and otra.json()["objective_id"] == objetivo
    assert otra.json()["repetida"] is True
    assert _creados(conn) == 1
    assert navegador.get("/app/admin/api/espacios/no-es-un-id/objetivos/opciones"
                         ).status_code == 404
    assert navegador.post("/app/admin/api/espacios/00000000-0000-0000-0000-000000000000/"
                          "objetivos", json=_cuerpo(intake_world)).status_code == 404


def test_la_api_devuelve_todo_lo_que_falta_en_palabras(web, conn, intake_world,
                                                         administradora):
    norte = _norte(intake_world)
    base = f"/app/admin/api/espacios/{norte['id']}/objetivos"
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = navegador.post(base, json=_cuerpo(intake_world, titulo="", tipo=7,
                                          referente_id="no-es-un-id", fecha="16/10",
                                          padre_id=norte["objectives"][0]))
    assert r.status_code == 422, r.text
    errores = {(e["campo"], e["motivo"]) for e in r.json()["errores"]}
    assert errores == {("titulo", "falta"), ("tipo", "mal_formado"),
                       ("referente", "mal_formado"), ("fecha", "mal_formada"),
                       ("padre", "es_operativo")}
    for error in r.json()["errores"]:
        assert error["texto"]
        for de_la_cocina in ("traceback", "psycopg", "crear_objetivo", "sql"):
            assert de_la_cocina not in error["texto"].lower()
    _nada_creado(conn)
    # Sin fecha, un día no hábil o alguien que no es referente: cada uno con su texto.
    sabado = _proximo_habil_real()
    while sabado.weekday() != 5:
        sabado += timedelta(days=1)
    for cambios, esperado, texto in (
            ({"fecha": None}, ("fecha", "falta"), "Elegí la fecha."),
            ({"fecha": sabado.isoformat()}, ("fecha", "no_es_dia_habil"),
             "Ese día no es hábil en este espacio."),
            ({"referente_id": _persona(intake_world, "Sam North")},
             ("referente", "no_es_referente_de_un_area"),
             "El referente tiene que ser el referente de un área del equipo.")):
        r = navegador.post(base, json=_cuerpo(intake_world, **cambios))
        assert r.status_code == 422, r.text
        (error,) = r.json()["errores"]
        assert (error["campo"], error["motivo"], error["texto"]) == (*esperado, texto)
    _nada_creado(conn)


def test_la_puerta_de_administracion_se_protege(web, conn, intake_world, administradora):
    norte = _norte(intake_world)
    base = f"/app/admin/api/espacios/{norte['id']}/objetivos"
    navegador = _navegador_de_administracion(web, conn, administradora)
    for origen in ("https://otro.example", "null"):
        assert navegador.post(base, json=_cuerpo(intake_world),
                              headers={"origin": origen}).status_code == 403
    assert navegador.post(base, content="titulo=x", headers={
        "content-type": "application/x-www-form-urlencoded"}).status_code == 415
    assert navegador.post(base, content=b"{" + b" " * (64 * 1024) + b"}", headers={
        "content-type": "application/json"}).status_code == 413
    _un_cuerpo_ilegible_es_un_pedido_mal_formado(navegador, base)
    assert web().post(base, json=_cuerpo(intake_world)).status_code == 401
    assert web().get(f"{base}/opciones").status_code == 401
    equipo = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    assert equipo.post(base, json=_cuerpo(intake_world)).status_code == 401
    assert equipo.get(f"{base}/opciones").status_code == 401
    impostor = web()
    impostor.cookies.set("leda_admin", equipo.cookies.get("leda_sesion"), domain="testserver",
                         path="/app/admin")
    assert impostor.post(base, json=_cuerpo(intake_world)).status_code == 401
    _revocar(conn, administradora)
    assert navegador.post(base, json=_cuerpo(intake_world)).status_code == 401
    _nada_creado(conn)


def _un_cuerpo_ilegible_es_un_pedido_mal_formado(navegador, camino: str) -> None:
    """Como en la carga: un cuerpo que no se puede leer (anidado hasta el fondo, o que no es
    JSON) es un pedido mal formado, 422 con lo que falta, nunca un 500 ni un objetivo."""
    for cuerpo in ("[" * 30000 + "]" * 30000, '{"a":' * 5000 + "1" + "}" * 5000, "{no es json"):
        r = navegador.post(camino, content=cuerpo, headers={"content-type": "application/json"})
        assert r.status_code == 422, r.text
        assert ("clave", "falta") in {(e["campo"], e["motivo"]) for e in r.json()["errores"]}


def test_la_puerta_del_equipo_crea_solo_para_direccion(web, conn, intake_world):
    base = "/app/api/objetivos"
    direccion = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    r = direccion.get(f"{base}/opciones")
    assert r.status_code == 200, r.text
    assert r.headers["cache-control"] == "no-store"
    assert "ok" not in r.json() and r.json()["sin_padre"] == ["estrategico"]
    assert r.json()["referentes"] and r.json()["calendario"]["dias_habiles"]
    cuerpo = _cuerpo(intake_world)
    r = direccion.post(base, json=cuerpo)
    assert r.status_code == 201, r.text
    assert direccion.post(base, json=cuerpo).status_code == 200
    assert _creados(conn) == 1
    assert _fila(conn, "select fecha_objetivo f from objective where id = %s",
                 r.json()["objective_id"])["f"].isoformat() == cuerpo["fecha"]
    detalle = _fila(conn, "select detalle from audit_log where accion = 'crear_objetivo'"
                    )["detalle"]
    assert detalle["puerta"] == "equipo"
    for nombre in ("Sam North", "Taylor Quinn"):
        otro = _navegador_del_equipo(web, conn, intake_world, nombre)
        r = otro.post(base, json=_cuerpo(intake_world))
        assert r.status_code == 403, (nombre, r.text)
        assert r.json()["error"] == "sin_autoridad"
        assert otro.get(f"{base}/opciones").status_code == 403
    assert _creados(conn) == 1


def test_la_puerta_del_equipo_se_protege(web, conn, intake_world, administradora):
    base = "/app/api/objetivos"
    direccion = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    for origen in ("https://otro.example", "null"):
        assert direccion.post(base, json=_cuerpo(intake_world),
                              headers={"origin": origen}).status_code == 403
    assert direccion.post(base, content="titulo=x", headers={
        "content-type": "application/x-www-form-urlencoded"}).status_code == 415
    assert direccion.post(base, content=b"{" + b" " * (64 * 1024) + b"}", headers={
        "content-type": "application/json"}).status_code == 413
    _un_cuerpo_ilegible_es_un_pedido_mal_formado(direccion, base)
    assert web().post(base, json=_cuerpo(intake_world)).status_code == 401
    assert web().get(f"{base}/opciones").status_code == 401
    # La cookie de administración no abre la puerta del equipo, ni puesta como la del equipo.
    administracion = _navegador_de_administracion(web, conn, administradora)
    assert administracion.post(base, json=_cuerpo(intake_world)).status_code == 401
    impostor = web()
    impostor.cookies.set("leda_sesion", administracion.cookies.get("leda_admin"),
                         domain="testserver", path="/app")
    assert impostor.post(base, json=_cuerpo(intake_world)).status_code == 401
    _nada_creado(conn)
