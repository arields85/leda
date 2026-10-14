"""La carga de tareas por la puerta del equipo, para Dirección y los referentes (ADR 0023, decisión
3; porción J4 de `odd/tasks/plataforma-jerarquias.md`, tarea J4a; decisiones del usuario del
2026-10-14 D1b, D3, D4, D10, D13 y D14; migración 0071): la capa de garantías, en la base.

El equipo de prueba es North Lab con tres áreas, cada una con su referente, como CoreWork:

- **Morgan Hale** es Dirección (la autoridad final) y la referente del área Direction (Ismael).
- **Taylor Quinn** es el referente de Field Services (Martín); **Sam North**, de su gente (Lucas).
- **Sam Noble** es la referente de Quality Guild (Marcos); **Alex Rivera**, de su gente (Nahuel).

Lo que se comprueba:

- **Quién le carga a quién:** Dirección, a cualquiera, también a sí misma (D13); un referente, a su
  gente y a sí mismo, al referente de otra área como un pedido a esa área (D14: nunca directo a la
  gente de otra área) y a Dirección como un pedido a Dirección (D1b). Un integrante, a nadie.
- **Quién la revisa, guardado en la tarea:** el referente que carga para su gente o para sí; quien
  elige Dirección (D3: preseleccionado el referente del área de esa persona; ella misma u otro
  referente, nunca quien la hace); el referente que recibe un pedido de otra área, también después
  de pasarla a su gente; y el que pidió algo a Dirección. `quien_revisa_la_tarea` lo lee primero, y
  con él la página, la escalera y la aprobación.
- **Quién la pidió:** la ve y es el único que la reabre, terminada y con su motivo; vuelve al
  referente del área de la tarea, y desde ahí no cuentan ni la aprobación ni la evidencia de antes.
- **La puerta de administración:** "quién la decidió" tiene que ser Dirección o el referente del
  área de la tarea (D10), y también puede elegir quién la revisa (D3).
- La sesión de la puerta, el espacio, la clave de un solo uso y la auditoría, como en la carga de
  administración.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

import psycopg
import pytest

from leda.autoridad import identificar_en_espacio
from leda.db import admin, espacio
from leda.herramientas import ejecutar
from tests.garantias.test_carga_de_tareas import (  # noqa: F401 -- `administradora` y `sesion`
    AHORA,                                         # son las fixtures
    VIERNES,
    _hash,
    _revocar,
    administradora,
    sesion,
    sin_espacio,
)
from tests.garantias.test_creacion_de_objetivos import _sesion_del_equipo

FUNCIONES_DE_LA_WEB = ("cargar_tarea_web", "opciones_de_la_carga_del_equipo", "reabrir_tarea",
                       "pedidas_de_la_sesion")
AYUDANTES = ("como_carga", "quien_revisaria", "puede_ser_quien_revisa",
             "quien_carga_en_el_equipo", "opciones_de_la_carga_en", "pedidas_que_ve")


# --- El equipo ------------------------------------------------------------------------------------

@pytest.fixture
def equipo(conn, intake_world) -> dict:
    """North Lab con un área de Dirección y un referente en cada área (ver el docstring)."""
    norte = intake_world["north-lab"]
    gente = norte["people"]
    with admin(conn) as cur:
        cur.execute("""insert into area (workspace_id, slug, nombre)
                       values (%s, 'direction', 'Direction') returning id""", (norte["id"],))
        norte["areas"]["direction"] = str(cur.fetchone()["id"])
        cur.execute("""insert into task_evidence_policy (workspace_id, area_id,
                                                         evidencia_requerida, version)
                       values (%s, %s, array['test record'], 1)""",
                    (norte["id"], norte["areas"]["direction"]))
        cur.execute("""update task_evidence_policy
                          set tipos = '{"test record": {"clases": ["texto"],
                                                        "en_palabras": "un registro"}}'
                        where workspace_id = %s""", (norte["id"],))
        cur.execute("update membership set area_id = %s where id = %s",
                    (norte["areas"]["direction"], gente["Morgan Hale"]["membership_id"]))
        for area, nombre in (("direction", "Morgan Hale"), ("field", "Taylor Quinn"),
                             ("quality", "Sam Noble")):
            cur.execute("update area set referente_membership_id = %s where id = %s",
                        (gente[nombre]["membership_id"], norte["areas"][area]))
        cur.execute("update membership set aprobador_membership_id = %s where id = %s",
                    (gente["Morgan Hale"]["membership_id"], gente["Sam Noble"]["membership_id"]))
        cur.execute("select id from rol where workspace_id = %s and slug = 'member'",
                    (norte["id"],))
        miembro = cur.fetchone()["id"]
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (79001, 'Alex Rivera 1') returning id""")
        usuario = str(cur.fetchone()["id"])
        cur.execute("""insert into membership (workspace_id, app_user_id, area_id, rol_id,
                                               aprobador_membership_id)
                       values (%s, %s, %s, %s, %s) returning id""",
                    (norte["id"], usuario, norte["areas"]["quality"], miembro,
                     gente["Sam Noble"]["membership_id"]))
        gente["Alex Rivera"] = {"app_user_id": usuario, "telegram": 79001,
                                "name": "Alex Rivera 1",
                                "membership_id": str(cur.fetchone()["id"])}
        cur.execute("""insert into greeting_state (membership_id, workspace_id, ultima_fecha_local)
                       values (%s, %s, date '9999-12-31')""",
                    (gente["Alex Rivera"]["membership_id"], norte["id"]))
    conn.commit()
    return intake_world


def _id(mundo: dict, nombre: str, slug: str = "north-lab") -> str:
    return mundo[slug]["people"][nombre]["membership_id"]


def _norte(mundo: dict) -> dict:
    return mundo["north-lab"]


def _datos(mundo: dict, **cambios) -> dict:
    """Una tarea válida en North Lab para Sam North, el viernes 16/10/2026, vista el miércoles 14 al
    mediodía."""
    datos = {
        "puerta": "equipo",
        "espacio": None,
        "objetivo": _norte(mundo)["objectives"][0],
        "titulo": "Colgar el módem en la pared",
        "descripcion": None,
        "responsable": _id(mundo, "Sam North"),
        "fecha": VIERNES,
        "criterio": "El módem queda colgado y prende",
        "evidencia": ["test record"],
        "decidio": None,
        "revisa": None,
        "clave": secrets.token_urlsafe(18),
        "ahora": AHORA,
        "espera": None,
    }
    datos.update(cambios)
    return datos


def _llamar(cur, token: str, d: dict) -> dict:
    cur.execute(
        """select cargar_tarea_web(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::text[], %s, %s, %s, %s,
                                   %s::uuid) as r""",
        (d["puerta"], _hash(token), d["espacio"], d["objetivo"], d["titulo"], d["descripcion"],
         d["responsable"], d["fecha"], d["criterio"], d["evidencia"], d["decidio"], d["revisa"],
         d["clave"], d["ahora"], d["espera"]))
    return cur.fetchone()["r"]


def _cargar(conn, token: str, mundo: dict, **cambios) -> dict:
    with sin_espacio(conn) as cur:
        resultado = _llamar(cur, token, _datos(mundo, **cambios))
    conn.commit()
    return resultado


def _como(conn, mundo: dict, quien: str, **cambios) -> dict:
    """Carga por la puerta del equipo con la sesión de `quien`."""
    return _cargar(conn, _sesion_del_equipo(conn, mundo, quien), mundo, **cambios)


def _errores(resultado: dict) -> set[tuple[str, str]]:
    assert resultado["ok"] is False, resultado
    return {(e["campo"], e["motivo"]) for e in resultado["errores"]}


def _fila(conn, consulta: str, *args) -> dict | None:
    with admin(conn) as cur:
        cur.execute(consulta, args)
        fila = cur.fetchone()
    conn.commit()
    return fila


def _contar(conn, tabla: str, donde: str = "true", *args) -> int:
    return _fila(conn, f"select count(*) n from {tabla} where {donde}", *args)["n"]


def _tarea(conn, task_id: str) -> dict:
    return _fila(conn, "select *, quien_revisa_la_tarea(id) as revisa from task where id = %s",
                 task_id)


def _nada_cargado(conn) -> None:
    assert _contar(conn, "task") == 0
    assert _contar(conn, "carga_de_tarea") == 0
    assert _contar(conn, "audit_log", "accion = 'cargar_tarea'") == 0


# --- Las funciones ----------------------------------------------------------------------------------

def test_las_funciones_de_la_web_son_elevadas_y_sus_ayudantes_no_los_ejecuta_nadie_mas(conn):
    with admin(conn) as cur:
        cur.execute(
            """select p.proname, r.rolname, p.prosecdef, p.proconfig,
                      has_function_privilege('public', p.oid, 'execute') as de_public,
                      has_function_privilege('leda_app', p.oid, 'execute') as de_app,
                      has_function_privilege('leda_gateway', p.oid, 'execute') as de_gateway
                 from pg_proc p join pg_roles r on r.oid = p.proowner
                 join pg_namespace n on n.oid = p.pronamespace
                where n.nspname = 'leda' and p.proname = any(%s)""",
            (list(FUNCIONES_DE_LA_WEB + AYUDANTES),))
        filas = {f["proname"]: f for f in cur.fetchall()}
    conn.commit()
    assert set(filas) == set(FUNCIONES_DE_LA_WEB + AYUDANTES)
    for nombre, f in filas.items():
        assert f["rolname"] == "leda_owner", nombre
        assert any(c.startswith("search_path=") and c.endswith("pg_temp")
                   for c in f["proconfig"] or []), nombre
        assert not f["de_public"] and not f["de_gateway"], nombre
    for nombre in FUNCIONES_DE_LA_WEB:
        assert filas[nombre]["prosecdef"] and filas[nombre]["de_app"], nombre
    for nombre in AYUDANTES:
        assert not filas[nombre]["prosecdef"] and not filas[nombre]["de_app"], nombre


def test_la_aplicacion_no_escribe_quien_revisa_ni_reaperturas(conn, equipo):
    norte = _norte(equipo)
    with espacio(conn, norte["id"]) as cur:
        for orden in ("update task set revisor_membership_id = null",
                      "update task set pedida_por_membership_id = null",
                      "insert into reapertura_de_tarea (workspace_id, task_id, "
                      "pedida_por_membership_id, responsable_membership_id, motivo) "
                      "values (gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), "
                      "gen_random_uuid(), 'x')",
                      "delete from reapertura_de_tarea"):
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                cur.execute(orden)
        # La lee (el cierre la consulta con la RLS de quien llama).
        cur.execute("select count(*) n from reapertura_de_tarea")
    conn.commit()


# --- Quién le carga a quién y quién la revisa --------------------------------------------------------

@pytest.mark.parametrize(("quien", "responsable", "revisa", "pedida_por", "area"), [
    # Dirección, a cualquiera: preseleccionado el referente de su área (D3).
    ("Morgan Hale", "Sam North", "Taylor Quinn", None, "field"),
    ("Morgan Hale", "Alex Rivera", "Sam Noble", None, "quality"),
    # A un referente: su área es la de él, que no se revisa a sí mismo; la revisa Dirección.
    ("Morgan Hale", "Taylor Quinn", "Morgan Hale", None, "field"),
    # Su propia tarea (D13).
    ("Morgan Hale", "Morgan Hale", "Morgan Hale", None, "direction"),
    # Un referente, a su gente y a sí mismo (D4): la revisa él.
    ("Taylor Quinn", "Sam North", "Taylor Quinn", None, "field"),
    ("Taylor Quinn", "Taylor Quinn", "Taylor Quinn", None, "field"),
    # Un pedido a otra área (D14): para su referente, que la revisa; es de esa área.
    ("Taylor Quinn", "Sam Noble", "Sam Noble", "Taylor Quinn", "quality"),
    # Un pedido a Dirección (D1b): la da por cumplida el referente que la pidió.
    ("Taylor Quinn", "Morgan Hale", "Taylor Quinn", "Taylor Quinn", "direction"),
])
def test_quien_le_carga_a_quien_y_quien_la_revisa(conn, equipo, quien, responsable, revisa,
                                                   pedida_por, area):
    r = _como(conn, equipo, quien, responsable=_id(equipo, responsable))
    assert r["ok"] is True, r
    tarea = _tarea(conn, r["task_id"])
    assert str(tarea["responsable_membership_id"]) == _id(equipo, responsable)
    assert str(tarea["revisor_membership_id"]) == _id(equipo, revisa)
    assert str(tarea["revisa"]) == _id(equipo, revisa), "quien_revisa_la_tarea lee la de la tarea"
    assert (str(tarea["pedida_por_membership_id"]) if tarea["pedida_por_membership_id"]
            else None) == (_id(equipo, pedida_por) if pedida_por else None)
    assert str(tarea["area_id"]) == _norte(equipo)["areas"][area]
    assert tarea["estado"] == "asignada"


def test_un_referente_no_le_carga_directo_a_la_gente_de_otra_area(conn, equipo):
    """D14: lo de otra área se le pide a su referente, que decide quién la hace."""
    r = _como(conn, equipo, "Taylor Quinn", responsable=_id(equipo, "Alex Rivera"))
    assert _errores(r) == {("responsable", "no_le_puede_cargar")}
    _nada_cargado(conn)


def test_un_integrante_no_carga_tareas(conn, equipo):
    for responsable in ("Sam North", "Taylor Quinn"):
        r = _como(conn, equipo, "Sam North", responsable=_id(equipo, responsable))
        assert _errores(r) == {("sesion", "sin_autoridad")}
    _nada_cargado(conn)


def test_direccion_elige_quien_la_revisa_pero_nunca_quien_la_hace(conn, equipo):
    otra = _como(conn, equipo, "Morgan Hale", revisa=_id(equipo, "Sam Noble"))
    assert otra["ok"] is True
    assert str(_tarea(conn, otra["task_id"])["revisa"]) == _id(equipo, "Sam Noble")
    ella = _como(conn, equipo, "Morgan Hale", revisa=_id(equipo, "Morgan Hale"))
    assert str(_tarea(conn, ella["task_id"])["revisa"]) == _id(equipo, "Morgan Hale")
    assert _errores(_como(conn, equipo, "Morgan Hale", revisa=_id(equipo, "Sam North"))) == {
        ("revisa", "es_quien_la_hace"), ("revisa", "no_puede_revisarla")}
    assert _errores(_como(conn, equipo, "Morgan Hale", responsable=_id(equipo, "Taylor Quinn"),
                          revisa=_id(equipo, "Taylor Quinn"))) == {("revisa", "es_quien_la_hace")}
    # Sólo Dirección o un referente de área.
    assert _errores(_como(conn, equipo, "Morgan Hale", revisa=_id(equipo, "Alex Rivera"))) == {
        ("revisa", "no_puede_revisarla")}


def test_un_referente_no_elige_quien_la_revisa(conn, equipo):
    r = _como(conn, equipo, "Taylor Quinn", revisa=_id(equipo, "Sam Noble"))
    assert _errores(r) == {("revisa", "no_corresponde")}
    # Elegir el que corresponde no cambia nada.
    assert _como(conn, equipo, "Taylor Quinn", revisa=_id(equipo, "Taylor Quinn"))["ok"] is True


def test_por_la_puerta_del_equipo_la_decidio_quien_la_carga(conn, equipo):
    r = _como(conn, equipo, "Taylor Quinn", decidio=_id(equipo, "Morgan Hale"))
    assert _errores(r) == {("decidio", "no_corresponde")}
    assert _como(conn, equipo, "Taylor Quinn", decidio=_id(equipo, "Taylor Quinn"))["ok"] is True


def test_nada_de_otro_espacio_entra_en_una_carga_del_equipo(conn, equipo):
    oeste = equipo["west-studio"]
    r = _como(conn, equipo, "Morgan Hale",
              responsable=_id(equipo, "Sam North", "west-studio"),
              objetivo=oeste["objectives"][0])
    assert _errores(r) == {("responsable", "no_es_integrante_activo"),
                           ("objetivo", "no_existe")}
    assert _errores(_como(conn, equipo, "Morgan Hale", espacio=oeste["id"])) == {
        ("espacio", "no_existe")}
    _nada_cargado(conn)


def test_sin_una_sesion_del_equipo_vigente_no_carga(conn, equipo, sesion):
    assert _errores(_cargar(conn, secrets.token_urlsafe(32), equipo)) == {("sesion", "sin_sesion")}
    # La sesión de administración no abre la puerta del equipo, y al revés.
    assert _errores(_cargar(conn, sesion, equipo)) == {("sesion", "sin_sesion")}
    token = _sesion_del_equipo(conn, equipo, "Morgan Hale")
    assert _errores(_cargar(conn, token, equipo, puerta="administracion",
                            espacio=_norte(equipo)["id"],
                            decidio=_id(equipo, "Morgan Hale"))) == {("sesion", "sin_sesion")}
    # Quien deja de ser referente deja de cargar, aunque su sesión siga.
    token = _sesion_del_equipo(conn, equipo, "Taylor Quinn")
    with admin(conn) as cur:
        cur.execute("update area set referente_membership_id = null where referente_membership_id = %s",
                    (_id(equipo, "Taylor Quinn"),))
    conn.commit()
    assert _errores(_cargar(conn, token, equipo)) == {("sesion", "sin_autoridad")}
    _nada_cargado(conn)


def test_la_misma_clave_devuelve_la_misma_tarea_y_con_otros_datos_se_rechaza(conn, equipo):
    token = _sesion_del_equipo(conn, equipo, "Taylor Quinn")
    clave = secrets.token_urlsafe(18)
    primera = _cargar(conn, token, equipo, clave=clave)
    otra_vez = _cargar(conn, token, equipo, clave=clave)
    assert otra_vez == {**primera, "repetida": True}
    assert _errores(_cargar(conn, token, equipo, clave=clave, titulo="Otra cosa")) == {
        ("clave", "usada_con_otros_datos")}
    assert _contar(conn, "task") == 1


def test_la_carga_del_equipo_deja_su_evento_y_su_auditoria(conn, equipo):
    token = _sesion_del_equipo(conn, equipo, "Taylor Quinn")
    r = _cargar(conn, token, equipo, responsable=_id(equipo, "Sam Noble"))
    taylor = equipo["north-lab"]["people"]["Taylor Quinn"]["app_user_id"]
    evento = _fila(conn, "select * from task_state_event where task_id = %s", r["task_id"])
    assert (evento["estado_nuevo"], evento["actor_kind"], str(evento["actor_app_user_id"])) == (
        "asignada", "persona", taylor)
    auditoria = _fila(conn, "select * from audit_log where accion = 'cargar_tarea'")
    assert str(auditoria["actor_app_user_id"]) == taylor
    assert str(auditoria["workspace_id"]) == _norte(equipo)["id"]
    detalle = auditoria["detalle"]
    assert detalle["puerta"] == "equipo" and detalle["origen"] == "web"
    assert detalle["sesion_web_id"]
    assert detalle["cargada_por_membership_id"] == _id(equipo, "Taylor Quinn")
    assert detalle["decidida_por_membership_id"] == _id(equipo, "Taylor Quinn")
    assert detalle["decision_declarada_al_cargar"] is False
    assert detalle["como"] == "pedido_a_otra_area"
    assert detalle["revisa_membership_id"] == _id(equipo, "Sam Noble")
    assert detalle["pedida_por_membership_id"] == _id(equipo, "Taylor Quinn")
    assert token not in str(detalle) and _hash(token) not in str(detalle)


# --- Las opciones del equipo ---------------------------------------------------------------------------

def _opciones(conn, token: str) -> dict:
    with sin_espacio(conn) as cur:
        cur.execute("select opciones_de_la_carga_del_equipo(%s, %s) as r", (_hash(token), AHORA))
        r = cur.fetchone()["r"]
    conn.commit()
    return r


def test_las_opciones_ofrecen_solo_a_quienes_les_puede_cargar(conn, equipo):
    def integrantes(nombre):
        opciones = _opciones(conn, _sesion_del_equipo(conn, equipo, nombre))
        assert opciones["ok"] is True
        return {i["membership_id"]: (i["como"], i["revisa"]["membership_id"])
                for i in opciones["integrantes"]}, opciones

    de_taylor, opciones = integrantes("Taylor Quinn")
    assert de_taylor == {
        _id(equipo, "Taylor Quinn"): ("propia", _id(equipo, "Taylor Quinn")),
        _id(equipo, "Sam North"): ("su_area", _id(equipo, "Taylor Quinn")),
        _id(equipo, "Sam Noble"): ("pedido_a_otra_area", _id(equipo, "Sam Noble")),
        _id(equipo, "Morgan Hale"): ("pedido_a_direccion", _id(equipo, "Taylor Quinn")),
    }
    assert opciones["yo"]["membership_id"] == _id(equipo, "Taylor Quinn")
    assert opciones["yo"]["elige_quien_revisa"] is False
    # Las áreas con su referente (D14) y quiénes pueden revisar (D3).
    assert {a["nombre"]: a["referente"]["membership_id"] for a in opciones["areas"]} == {
        "Direction": _id(equipo, "Morgan Hale"), "Field Services": _id(equipo, "Taylor Quinn"),
        "Quality Guild": _id(equipo, "Sam Noble")}
    assert {r["membership_id"] for r in opciones["revisores"]} == {
        _id(equipo, "Morgan Hale"), _id(equipo, "Taylor Quinn"), _id(equipo, "Sam Noble")}

    de_morgan, opciones = integrantes("Morgan Hale")
    assert set(de_morgan) == {_id(equipo, n) for n in (
        "Morgan Hale", "Taylor Quinn", "Sam North", "Sam Noble", "Alex Rivera")}
    assert de_morgan[_id(equipo, "Alex Rivera")] == ("direccion", _id(equipo, "Sam Noble"))
    assert opciones["yo"]["elige_quien_revisa"] is True
    # Nada de otro espacio.
    assert _id(equipo, "Sam North", "west-studio") not in de_morgan


def test_las_opciones_del_equipo_piden_una_sesion_de_direccion_o_de_un_referente(conn, equipo):
    assert _opciones(conn, _sesion_del_equipo(conn, equipo, "Sam North"))["errores"] == [
        {"campo": "sesion", "motivo": "sin_autoridad"}]
    assert _opciones(conn, secrets.token_urlsafe(32))["errores"] == [
        {"campo": "sesion", "motivo": "sin_sesion"}]


# --- La puerta de administración: D10 y D3 ------------------------------------------------------------

def _como_administracion(conn, sesion: str, mundo: dict, **cambios) -> dict:
    return _cargar(conn, sesion, mundo, **{"puerta": "administracion",
                                           "espacio": _norte(mundo)["id"],
                                           "decidio": _id(mundo, "Morgan Hale"), **cambios})


def test_la_decidio_direccion_o_el_referente_del_area_de_la_tarea(conn, equipo, sesion):
    """D10: para una tarea de Field Services, Dirección o Taylor; nunca Sam North ni la referente
    de otra área."""
    for quien in ("Morgan Hale", "Taylor Quinn"):
        assert _como_administracion(conn, sesion, equipo, decidio=_id(equipo, quien))["ok"]
    for quien in ("Sam North", "Sam Noble"):
        r = _como_administracion(conn, sesion, equipo, decidio=_id(equipo, quien))
        assert _errores(r) == {("decidio", "no_puede_decidirla")}


def test_la_administracion_elige_quien_la_revisa_como_direccion(conn, equipo, sesion):
    r = _como_administracion(conn, sesion, equipo, revisa=_id(equipo, "Sam Noble"))
    assert str(_tarea(conn, r["task_id"])["revisa"]) == _id(equipo, "Sam Noble")
    assert _errores(_como_administracion(conn, sesion, equipo, revisa=_id(equipo, "Sam North"))) \
        == {("revisa", "es_quien_la_hace"), ("revisa", "no_puede_revisarla")}
    # Sin elegirla, la regla de siempre, leída ahora: nada guardado en la tarea.
    sin = _como_administracion(conn, sesion, equipo)
    tarea = _tarea(conn, sin["task_id"])
    assert tarea["revisor_membership_id"] is None
    assert str(tarea["revisa"]) == _id(equipo, "Taylor Quinn")
    detalle = _fila(conn, "select detalle from audit_log where sujeto_id = %s",
                    sin["task_id"])["detalle"]
    assert detalle["puerta"] == "administracion"
    assert detalle["revisa_membership_id"] == _id(equipo, "Taylor Quinn")


# --- Quien la revisa: la página, la escalera y la aprobación -------------------------------------------

def _entregar(conn, mundo: dict, task_id: str) -> None:
    """Su evidencia y su entrega, como las deja el motor."""
    with admin(conn) as cur:
        cur.execute(
            """insert into evidence (workspace_id, task_id, tipo, clase, texto, cubre)
               values (%s, %s, 'test record', 'texto', 'Quedó colgado', array['test record'])""",
            (_norte(mundo)["id"], task_id))
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind)
                       values (%s, 'asignada', 'en_revision', 'persona')""", (task_id,))
    conn.commit()


def _aprobar(conn, mundo: dict, task_id: str, quien: str) -> None:
    with admin(conn) as cur:
        cur.execute("""insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                             aprobador_membership_id, decision)
                       values (%s, 'tarea', %s, %s, 'aprobado')""",
                    (_norte(mundo)["id"], task_id, _id(mundo, quien)))
    conn.commit()


def _no_cierra(conn, task_id: str) -> str | None:
    return _fila(conn, "select motivo_no_cierra_tarea(%s) as m", task_id)["m"]


def test_quien_la_revisa_en_la_tarea_manda_en_la_pagina_la_escalera_y_la_aprobacion(conn,
                                                                                      equipo):
    """Dirección le carga a Sam North y la deja revisando a Sam Noble (D3). La página la ve Sam
    Noble; la escalera le pide a ella la decisión; la aprobación de Taylor (que aprueba a Sam North
    por la regla de siempre) no la cierra, la de Sam Noble sí."""
    r = _como(conn, equipo, "Morgan Hale", revisa=_id(equipo, "Sam Noble"))
    tarea = r["task_id"]
    ws = _norte(equipo)["id"]
    with espacio(conn, ws) as cur:
        cur.execute("select puede_ver_tarea(%s, %s) as si", (_id(equipo, "Sam Noble"), tarea))
        assert cur.fetchone()["si"] is True
        cur.execute("select puede_ver_tarea(%s, %s) as si", (_id(equipo, "Alex Rivera"), tarea))
        assert cur.fetchone()["si"] is False
    conn.commit()
    _entregar(conn, equipo, tarea)
    # La escalera de las entregas que esperan una decisión (`escalera.correr_escalera`).
    with espacio(conn, ws) as cur:
        cur.execute("""select t.id, quien_revisa_la_tarea(t.id) as aprobador_membership_id
                         from task t
                        where t.estado = 'en_revision' and quien_revisa_la_tarea(t.id) is not null""")
        assert [(str(f["id"]), str(f["aprobador_membership_id"])) for f in cur.fetchall()] == [
            (tarea, _id(equipo, "Sam Noble"))]
    conn.commit()
    _aprobar(conn, equipo, tarea, "Taylor Quinn")
    assert _no_cierra(conn, tarea) == "Falta la aprobación de quien revisa ese trabajo."
    _aprobar(conn, equipo, tarea, "Sam Noble")
    assert _no_cierra(conn, tarea) is None


def test_quien_revisa_por_la_regla_de_la_aplicacion_es_el_de_la_tarea(conn, equipo):
    from leda.autoridad import puede_revisar_la_tarea

    r = _como(conn, equipo, "Morgan Hale", revisa=_id(equipo, "Sam Noble"))
    ws = _norte(equipo)["id"]
    with espacio(conn, ws) as cur:
        noble = identificar_en_espacio(cur, 71003, ws)
        taylor = identificar_en_espacio(cur, 71001, ws)
        assert puede_revisar_la_tarea(cur, noble, r["task_id"]) is True
        assert puede_revisar_la_tarea(cur, taylor, r["task_id"]) is False
    conn.commit()


# --- El pase de un pedido de otra área -------------------------------------------------------------------

def _hacer(conn, mundo: dict, quien: str, herramienta: str, args: dict):
    ws = _norte(mundo)["id"]
    with espacio(conn, ws) as cur:
        solicitante = identificar_en_espacio(cur, mundo["north-lab"]["people"][quien]["telegram"],
                                             ws)
        r = ejecutar(cur, solicitante, herramienta, args, ya_confirmada=True)
    conn.commit()
    return r


def _pasar(conn, mundo: dict, task_id: str, de: str, a: str) -> None:
    """El referente se la pasa a alguien de su gente (su pedido es la decisión) y esa persona la
    toma."""
    r = _hacer(conn, mundo, de, "pedir_pase_de_tarea",
               {"tarea_id": task_id, "a_membership_id": _id(mundo, a)})
    assert r["estado"] == "esperando_que_la_tome", r
    tomado = _hacer(conn, mundo, a, "contestar_pase_de_tarea",
                    {"pase_id": r["pase_id"], "acepta": True})
    assert "error" not in tomado, tomado


def test_el_pedido_a_otra_area_lo_pasa_su_referente_y_lo_sigue_revisando(conn, equipo):
    """D14, pasos 2 y 3: Sam Noble (Marcos) se lo pasa a Alex Rivera (Nahuel); lo sigue revisando
    ella y sigue pedido por Taylor."""
    r = _como(conn, equipo, "Taylor Quinn", responsable=_id(equipo, "Sam Noble"))
    _pasar(conn, equipo, r["task_id"], "Sam Noble", "Alex Rivera")
    tarea = _tarea(conn, r["task_id"])
    assert str(tarea["responsable_membership_id"]) == _id(equipo, "Alex Rivera")
    assert str(tarea["revisa"]) == _id(equipo, "Sam Noble")
    assert str(tarea["pedida_por_membership_id"]) == _id(equipo, "Taylor Quinn")
    cambio = _fila(conn, "select revisa_membership_id from cambio_de_responsable where task_id = %s",
                   r["task_id"])
    assert str(cambio["revisa_membership_id"]) == _id(equipo, "Sam Noble")


# --- La reapertura -------------------------------------------------------------------------------------

def _reabrir(conn, token: str, task_id: str, motivo: str | None) -> dict:
    with sin_espacio(conn) as cur:
        cur.execute("select reabrir_tarea(%s, %s, %s) as r", (_hash(token), task_id, motivo))
        r = cur.fetchone()["r"]
    conn.commit()
    return r


def _pedida_y_terminada(conn, mundo: dict) -> str:
    """Taylor le pide a Sam Noble colgar el módem, Sam Noble se la pasa a Alex, Alex la entrega y
    Sam Noble la aprueba."""
    r = _como(conn, mundo, "Taylor Quinn", responsable=_id(mundo, "Sam Noble"))
    _pasar(conn, mundo, r["task_id"], "Sam Noble", "Alex Rivera")
    _entregar(conn, mundo, r["task_id"])
    _aprobar(conn, mundo, r["task_id"], "Sam Noble")
    with admin(conn) as cur:
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind)
                       values (%s, 'en_revision', 'terminada', 'persona')""", (r["task_id"],))
    conn.commit()
    assert _tarea(conn, r["task_id"])["estado"] == "terminada"
    return r["task_id"]


def test_quien_la_pidio_la_reabre_y_vuelve_al_referente_del_area(conn, equipo):
    tarea = _pedida_y_terminada(conn, equipo)
    token = _sesion_del_equipo(conn, equipo, "Taylor Quinn")
    r = _reabrir(conn, token, tarea, "  El módem quedó torcido  ")
    assert r["ok"] is True and r["responsable_membership_id"] == _id(equipo, "Sam Noble")
    fila = _tarea(conn, tarea)
    # Vuelve abierta a Sam Noble, que decide quién la retoma; la sigue revisando ella.
    assert fila["estado"] == "asignada"
    assert str(fila["responsable_membership_id"]) == _id(equipo, "Sam Noble")
    assert str(fila["revisa"]) == _id(equipo, "Sam Noble")
    reapertura = _fila(conn, "select * from reapertura_de_tarea where task_id = %s", tarea)
    assert reapertura["motivo"] == "El módem quedó torcido"
    assert str(reapertura["pedida_por_membership_id"]) == _id(equipo, "Taylor Quinn")
    assert str(reapertura["responsable_anterior_membership_id"]) == _id(equipo, "Alex Rivera")
    evento = _fila(conn, """select * from task_state_event where task_id = %s
                             order by at desc limit 1""", tarea)
    assert (evento["estado_anterior"], evento["estado_nuevo"]) == ("terminada", "asignada")
    auditoria = _fila(conn, "select * from audit_log where accion = 'reabrir_tarea'")
    assert str(auditoria["sujeto_id"]) == tarea
    assert auditoria["detalle"]["reapertura_id"] == str(reapertura["id"])
    assert auditoria["detalle"]["pedida_por_membership_id"] == _id(equipo, "Taylor Quinn")
    # Desde la reapertura, ni la aprobación ni la evidencia de antes la cierran.
    with admin(conn) as cur:
        cur.execute("select tipos_de_evidencia_que_faltan(%s) as t", (tarea,))
        assert cur.fetchone()["t"] == ["test record"]
    conn.commit()
    with admin(conn) as cur:
        cur.execute("""insert into evidence (workspace_id, task_id, tipo, clase, texto, cubre)
                       values (%s, %s, 'test record', 'texto', 'Derecho', array['test record'])""",
                    (_norte(equipo)["id"], tarea))
    conn.commit()
    assert _no_cierra(conn, tarea) == "Falta la aprobación de quien revisa ese trabajo."
    _aprobar(conn, equipo, tarea, "Sam Noble")
    assert _no_cierra(conn, tarea) is None


def test_solo_la_reabre_quien_la_pidio_terminada_y_con_su_motivo(conn, equipo):
    tarea = _pedida_y_terminada(conn, equipo)
    for otra in ("Sam Noble", "Morgan Hale", "Alex Rivera"):
        r = _reabrir(conn, _sesion_del_equipo(conn, equipo, otra), tarea, "No me gusta")
        assert _errores(r) == {("tarea", "no_la_pediste")}
    token = _sesion_del_equipo(conn, equipo, "Taylor Quinn")
    assert _errores(_reabrir(conn, token, tarea, "   ")) == {("motivo", "falta")}
    assert _errores(_reabrir(conn, token, tarea, "x" * 501)) == {("motivo", "demasiado_largo")}
    assert _errores(_reabrir(conn, secrets.token_urlsafe(32), tarea, "Torcido")) == {
        ("sesion", "sin_sesion")}
    assert _contar(conn, "reapertura_de_tarea") == 0
    # Una tarea abierta no se reabre.
    abierta = _como(conn, equipo, "Taylor Quinn", responsable=_id(equipo, "Sam Noble"))
    assert _errores(_reabrir(conn, token, abierta["task_id"], "Torcido")) == {
        ("tarea", "no_esta_terminada")}
    # Una tarea de su propia área no es un pedido: no la reabre él.
    propia = _como(conn, equipo, "Taylor Quinn")
    assert _errores(_reabrir(conn, token, propia["task_id"], "Torcido")) == {
        ("tarea", "no_la_pediste")}
    assert _contar(conn, "reapertura_de_tarea") == 0
    assert _tarea(conn, tarea)["estado"] == "terminada"


# --- Lo que ve cada uno -----------------------------------------------------------------------------------

def _pedidas(conn, token: str) -> list[dict]:
    with sin_espacio(conn) as cur:
        cur.execute("select * from pedidas_de_la_sesion(%s, %s)", (_hash(token), AHORA))
        filas = cur.fetchall()
    conn.commit()
    return filas


def _tareas_de(conn, token: str, vista: str) -> list[dict]:
    with sin_espacio(conn) as cur:
        cur.execute("select * from tareas_de_la_sesion(%s, %s, %s)", (_hash(token), vista, AHORA))
        filas = cur.fetchall()
    conn.commit()
    return filas


def test_cada_uno_ve_lo_que_pidio_lo_que_le_pidieron_y_lo_de_direccion(conn, equipo):
    terminada = _pedida_y_terminada(conn, equipo)
    abierta = _como(conn, equipo, "Taylor Quinn", responsable=_id(equipo, "Sam Noble"),
                    titulo="Medir el rack")["task_id"]
    a_direccion = _como(conn, equipo, "Taylor Quinn", responsable=_id(equipo, "Morgan Hale"),
                        titulo="Aprobar la compra del servidor")["task_id"]
    propia = _como(conn, equipo, "Taylor Quinn", titulo="Configurar el módem")["task_id"]

    # Taylor ve lo que pidió, con su estado; su propia tarea no es un pedido.
    taylor = _sesion_del_equipo(conn, equipo, "Taylor Quinn")
    pedidas = {str(f["task_id"]): f for f in _pedidas(conn, taylor)}
    assert set(pedidas) == {terminada, abierta, a_direccion}
    assert pedidas[terminada]["estado"] == "terminada" and pedidas[terminada]["terminada_en"]
    assert pedidas[abierta]["estado"] == "asignada" and pedidas[abierta]["terminada_en"] is None
    assert propia not in pedidas
    with espacio(conn, _norte(equipo)["id"]) as cur:
        for tarea in (terminada, abierta, a_direccion):
            cur.execute("select puede_ver_tarea(%s, %s) as si", (_id(equipo, "Taylor Quinn"),
                                                                 tarea))
            assert cur.fetchone()["si"] is True
    conn.commit()

    # Sam Noble ve en su sector lo que le pidieron a su área; Morgan, en las suyas, lo que le
    # pidieron a Dirección.
    noble = _sesion_del_equipo(conn, equipo, "Sam Noble")
    assert abierta in {str(f["task_id"]) for f in _tareas_de(conn, noble, "sector")}
    morgan = _sesion_del_equipo(conn, equipo, "Morgan Hale")
    assert (a_direccion, "mia") in {(str(f["task_id"]), f["papel"])
                                    for f in _tareas_de(conn, morgan, "tus")}
    # Lo pedido de otro no es de nadie más.
    assert _pedidas(conn, noble) == []
    assert _pedidas(conn, secrets.token_urlsafe(32)) == []


def test_lo_pedido_terminado_hace_mas_de_30_dias_ya_no_se_lista(conn, equipo):
    tarea = _pedida_y_terminada(conn, equipo)
    taylor = _sesion_del_equipo(conn, equipo, "Taylor Quinn")
    with sin_espacio(conn) as cur:
        cur.execute("select task_id from pedidas_de_la_sesion(%s, %s)",
                    (_hash(taylor), datetime.now(timezone.utc) + timedelta(days=60)))
        assert cur.fetchall() == []
    conn.commit()
    assert tarea


# --- La entrada HTTP de la puerta del equipo ---------------------------------------------------------

@pytest.fixture
def web(conn, monkeypatch):
    """Un navegador nuevo por llamada, con la conexión de la prueba y el reloj de la prueba (el
    miércoles 14/10/2026 al mediodía). El juicio del criterio usa una IA de mentira que lo da por
    comprobable: nunca la real."""
    from fastapi.testclient import TestClient

    from leda import entrada, web_app
    from tests.test_ayuda_al_cargar import IAQueCopiaElCriterio

    monkeypatch.setattr(web_app, "_conn_de_la_web", lambda: conn)
    monkeypatch.setattr(web_app, "_ahora", lambda _conn, _ws: AHORA)
    monkeypatch.setattr(web_app, "_ia_del_criterio",
                        lambda conn, espacio: IAQueCopiaElCriterio())

    def nuevo():
        return TestClient(entrada.app, base_url="https://testserver", follow_redirects=False)
    return nuevo


def _navegador(web, conn, mundo: dict, nombre: str):
    from leda import web_app

    with espacio(conn, _norte(mundo)["id"]) as cur:
        token = web_app.emitir_enlace(cur, _id(mundo, nombre))
    conn.commit()
    navegador = web()
    assert navegador.post(f"/app/entrar/{token}").status_code == 303
    return navegador


def _cuerpo(mundo: dict, **cambios) -> dict:
    cuerpo = {"objetivo_id": _norte(mundo)["objectives"][0],
              "titulo": "Colgar el módem en la pared", "descripcion": "",
              "responsable_id": _id(mundo, "Sam Noble"), "fecha": VIERNES.isoformat(),
              "criterio": "El módem queda colgado y prende", "evidencia": ["test record"],
              "clave": secrets.token_urlsafe(18)}
    cuerpo.update(cambios)
    return cuerpo


def test_la_web_sabe_quien_carga_tareas(web, conn, equipo):
    for nombre, carga in (("Morgan Hale", True), ("Taylor Quinn", True), ("Sam North", False)):
        r = _navegador(web, conn, equipo, nombre).get("/app/api/yo")
        assert r.json()["carga_tareas"] is carga, nombre


def test_las_opciones_por_la_api_son_de_quien_carga(web, conn, equipo):
    r = _navegador(web, conn, equipo, "Taylor Quinn").get("/app/api/carga/opciones")
    assert r.status_code == 200, r.text
    assert "ok" not in r.json()
    assert {i["membership_id"] for i in r.json()["integrantes"]} == {
        _id(equipo, n) for n in ("Taylor Quinn", "Sam North", "Sam Noble", "Morgan Hale")}
    r = _navegador(web, conn, equipo, "Sam North").get("/app/api/carga/opciones")
    assert r.status_code == 403
    assert r.json() == {"error": "sin_autoridad", "texto": (
        "Cargar tareas le corresponde a Dirección y a los referentes de área.")}
    assert web().get("/app/api/carga/opciones").status_code == 401


def test_cargar_por_la_api_del_equipo(web, conn, equipo, administradora):
    from tests.garantias.test_carga_de_tareas import _navegador_de_administracion

    taylor = _navegador(web, conn, equipo, "Taylor Quinn")
    cuerpo = _cuerpo(equipo)
    assert taylor.post("/app/api/tareas/revisar", json=cuerpo).json() == {"errores": []}
    r = taylor.post("/app/api/tareas", json=cuerpo)
    assert r.status_code == 201, r.text
    tarea = _tarea(conn, r.json()["task_id"])
    assert str(tarea["pedida_por_membership_id"]) == _id(equipo, "Taylor Quinn")
    assert str(tarea["revisa"]) == _id(equipo, "Sam Noble")
    assert taylor.post("/app/api/tareas", json=cuerpo).status_code == 200
    # Un referente no elige quién la revisa, y lo dice con palabras.
    r = taylor.post("/app/api/tareas", json=_cuerpo(equipo, revisa_id=_id(equipo, "Morgan Hale")))
    assert r.status_code == 422
    assert r.json()["errores"] == [{"campo": "revisa", "motivo": "no_corresponde", "texto": (
        "Quién revisa esta tarea no se elige: la revisa quien corresponde.")}]
    r = taylor.post("/app/api/tareas", json=_cuerpo(equipo, responsable_id=_id(equipo,
                                                                               "Alex Rivera")))
    assert {(e["campo"], e["motivo"]) for e in r.json()["errores"]} == {
        ("responsable", "no_le_puede_cargar")}
    # Un integrante no carga; otro sitio no carga; la cookie de administración no abre esta puerta.
    assert _navegador(web, conn, equipo, "Sam North").post(
        "/app/api/tareas", json=_cuerpo(equipo)).status_code == 403
    assert taylor.post("/app/api/tareas", json=_cuerpo(equipo),
                       headers={"origin": "https://otro.example"}).status_code == 403
    administracion = _navegador_de_administracion(web, conn, administradora)
    assert administracion.post("/app/api/tareas", json=_cuerpo(equipo)).status_code == 401
    assert _contar(conn, "task") == 1


def test_direccion_elige_quien_la_revisa_por_la_api(web, conn, equipo):
    morgan = _navegador(web, conn, equipo, "Morgan Hale")
    r = morgan.post("/app/api/tareas", json=_cuerpo(
        equipo, responsable_id=_id(equipo, "Sam North"), revisa_id=_id(equipo, "Sam Noble")))
    assert r.status_code == 201, r.text
    assert str(_tarea(conn, r.json()["task_id"])["revisa"]) == _id(equipo, "Sam Noble")


def test_el_referente_pasa_un_pedido_a_su_gente_desde_la_web(web, conn, equipo):
    tarea = _como(conn, equipo, "Taylor Quinn", responsable=_id(equipo, "Sam Noble"))["task_id"]
    noble = _navegador(web, conn, equipo, "Sam Noble")
    sector = noble.get("/app/api/tareas?vista=sector").json()
    assert sector["pasar_a"] == [{"membership_id": _id(equipo, "Alex Rivera"),
                                  "nombre": "Alex Rivera 1", "area": "Quality Guild"}]
    # A alguien de otra área, no.
    r = noble.post(f"/app/api/tareas/{tarea}/pase",
                   json={"a_membership_id": _id(equipo, "Sam North")})
    assert r.status_code == 422
    assert r.json()["errores"][0]["motivo"] == "no_es_de_tu_area"
    r = noble.post(f"/app/api/tareas/{tarea}/pase",
                   json={"a_membership_id": _id(equipo, "Alex Rivera")})
    assert r.status_code == 200, r.text
    assert r.json()["estado"] == "esperando_que_la_tome"
    # Sigue con ella hasta que Alex la toma, y a Alex le llega la pregunta del pase.
    assert str(_tarea(conn, tarea)["responsable_membership_id"]) == _id(equipo, "Sam Noble")
    aviso = _fila(conn, "select * from scheduled_notice where task_id = %s", tarea)
    assert aviso["tipo"] == "pase_para_tomar"
    assert str(aviso["destinatario_membership_id"]) == _id(equipo, "Alex Rivera")
    # Taylor no es el referente de esa tarea; Alex no es referente.
    r = _navegador(web, conn, equipo, "Taylor Quinn").post(
        f"/app/api/tareas/{tarea}/pase", json={"a_membership_id": _id(equipo, "Sam North")})
    assert r.status_code == 422
    assert {e["campo"] for e in r.json()["errores"]} == {"tarea"}
    assert _navegador(web, conn, equipo, "Alex Rivera").post(
        f"/app/api/tareas/{tarea}/pase",
        json={"a_membership_id": _id(equipo, "Sam Noble")}).status_code == 403


def test_quien_la_pidio_ve_lo_pedido_y_pide_cambios_desde_la_web(web, conn, equipo):
    tarea = _pedida_y_terminada(conn, equipo)
    taylor = _navegador(web, conn, equipo, "Taylor Quinn")
    pedidas = taylor.get("/app/api/tareas?vista=tus").json()["pedidas"]
    assert [(p["id"], p["estado"], p["puede_pedir_cambios"]) for p in pedidas] == [
        (tarea, "terminada", True)]
    r = _navegador(web, conn, equipo, "Sam Noble").post(f"/app/api/tareas/{tarea}/reabrir",
                                                        json={"motivo": "Torcido"})
    assert r.status_code == 422 and r.json()["errores"][0]["motivo"] == "no_la_pediste"
    r = taylor.post(f"/app/api/tareas/{tarea}/reabrir", json={"motivo": ""})
    assert r.status_code == 422
    assert r.json()["errores"] == [{"campo": "motivo", "motivo": "falta",
                                    "texto": "Contá qué hay que cambiar."}]
    r = taylor.post(f"/app/api/tareas/{tarea}/reabrir", json={"motivo": "Quedó torcido"})
    assert r.status_code == 200, r.text
    assert r.json()["responsable_membership_id"] == _id(equipo, "Sam Noble")
    assert _tarea(conn, tarea)["estado"] == "asignada"


def test_la_ortografia_y_el_dictado_del_equipo_se_abren_a_los_referentes(web, conn, equipo):
    """Sin textos no se llama a la IA: alcanza para ver quién pasa la puerta."""
    taylor = _navegador(web, conn, equipo, "Taylor Quinn")
    assert taylor.post("/app/api/ortografia", json={}).json() == {"corregidos": {},
                                                                    "sin_revisar": []}
    integrante = _navegador(web, conn, equipo, "Sam North")
    assert integrante.post("/app/api/ortografia", json={}).status_code == 403
    assert integrante.post("/app/api/dictado", content=b"x",
                           headers={"content-type": "audio/mp4"}).status_code == 403


# --- La ayuda de la IA por la puerta del equipo (D11) ---------------------------------------------

@pytest.fixture
def ia(monkeypatch):
    from leda import web_app
    from tests.test_ayuda_al_cargar import IADeLaCarga, juzga_que_si

    falsa = IADeLaCarga(juzga=juzga_que_si)
    monkeypatch.setattr(web_app, "_ia_de_la_ayuda", lambda conn, espacio: falsa)
    return falsa


def _ayuda(navegador, texto: str):
    return navegador.post("/app/api/ayuda", json={
        "texto": texto, "objetivo_id": "", "titulo": "", "descripcion": "", "responsable_id": "",
        "fecha": "", "espera_id": "", "criterio": ""})


def test_la_ayuda_propone_al_referente_de_quien_es_de_otra_area_y_lo_explica(web, conn, equipo,
                                                                              ia):
    ia.respuestas.append({"titulo": "Colgar el módem en la pared", "responsable": "Alex"})
    r = _ayuda(_navegador(web, conn, equipo, "Taylor Quinn"),
               "que Alex cuelgue el módem en la pared")
    assert r.status_code == 200, r.text
    assert r.json()["propuesta"]["responsable_id"] == _id(equipo, "Sam Noble")
    assert {"campo": "ayuda", "motivo": "de_otra_area", "texto": (
        "«Alex» es de Quality Guild: lo de otra área se le pide a su referente, Sam Noble 1, que "
        "decide quién la hace.")} in r.json()["avisos"]
    detalle = _fila(conn, "select detalle from audit_log where accion = 'proponer_al_cargar'")[
        "detalle"]
    assert detalle["puerta"] == "equipo" and detalle["sesion_web_id"]
    assert detalle["responsable_de"] == "su_referente"


def test_la_ayuda_del_equipo_no_propone_a_nadie_que_no_se_nombro(web, conn, equipo, ia):
    ia.respuestas.append({"titulo": "Colgar el módem en la pared", "quien_la_hace": "P1"})
    r = _ayuda(_navegador(web, conn, equipo, "Taylor Quinn"), "hay que colgar el módem")
    assert r.status_code == 200, r.text
    assert "responsable_id" not in r.json()["propuesta"]


def test_la_ayuda_del_equipo_no_es_para_un_integrante(web, conn, equipo, ia):
    ia.respuestas.append({"titulo": "Colgar el módem en la pared"})
    assert _ayuda(_navegador(web, conn, equipo, "Sam North"),
                  "colgar el módem").status_code == 403
    assert ia.pedidos == []
