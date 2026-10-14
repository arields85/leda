"""La entrada a la web por chat (ADR 0022, decisión 4; migración 0066; tarea A-3 de
`odd/tasks/acceso-por-chat.md`): la capa de garantías.

Lo que se prueba acá es la base, la salida y el despachador, no la conversación:

- **La marca, no el enlace.** La fila de la salida sólo dice que lleva el botón de la web de
  esta persona (`message_outbox_entrada_web`, con su destino desde la 0073; ADR 0024); el
  despachador lo arma al mandar, como Mini App del bot del espacio, sin emitir ningún enlace.
  Sin la dirección pública, o en un chat que no es privado, el mensaje sale sin botón y deja su
  incidente. Un mensaje lleva uno solo.
- **Lo que la cocina pregunta sin leer las tablas:** si la persona entró alguna vez a la web
  (`entro_a_la_web`) y si tiene un enlace sin usar (`tiene_un_enlace_sin_usar`), en el espacio de
  quien llama.
- **El corte siempre deja su auditoría** (decisión técnica 3), también sin sesiones abiertas.
- **Aislamiento:** las dos tablas nuevas con `workspace_id` obligatorio y `row level security`
  forzado; desde un espacio no se ve nada de otro.
"""

from __future__ import annotations

import dataclasses
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path

import psycopg
import pytest

from leda import config as config_mod
from leda import web_app
from leda.calendario import Calendario
from leda.db import admin, espacio, sin_espacio
from leda.despachador import TransporteDePrueba, despachar
from leda.salida import PayloadValidationError, enqueue_outbox

AHORA = datetime(2026, 10, 22, 15, 0, tzinfo=timezone.utc)      # jueves, 12:00 en Buenos Aires
BASE = "https://leda.invalid"
ENLACE = re.compile(r"\n" + re.escape(BASE) + r"/app/entrar/([A-Za-z0-9_-]{43})$")
TABLAS = ("message_outbox_entrada_web", "ofrecimiento_web")
FUNCIONES = ("entro_a_la_web", "tiene_un_enlace_sin_usar", "cortar_sesiones_de_membresia")


@pytest.fixture
def direccion(monkeypatch):
    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url=BASE + "/"))


# --- Ayudas ---------------------------------------------------------------------------------

def _persona(mundo: dict, nombre: str = "Sam Noble", slug: str = "north-lab") -> str:
    return mundo[slug]["people"][nombre]["membership_id"]


def _filas(conn, sql: str, *args) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(sql, args)
        filas = cur.fetchall()
    conn.commit()
    return filas


def _auditoria(conn, accion: str) -> list[dict]:
    return _filas(conn, "select * from audit_log where accion = %s order by at, id", accion)


def _emitir(conn, mundo: dict, nombre: str = "Sam Noble", slug: str = "north-lab") -> str:
    with espacio(conn, mundo[slug]["id"]) as cur:
        token = web_app.emitir_enlace(cur, _persona(mundo, nombre, slug))
    conn.commit()
    assert token
    return token


def _canjear(conn, token: str) -> str | None:
    with sin_espacio(conn) as cur:
        cur.execute("select canjear_enlace_de_entrada(%s, %s) as id",
                    (web_app._hash(token), web_app._hash(secrets.token_urlsafe(32))))
        sesion = cur.fetchone()["id"]
    conn.commit()
    return str(sesion) if sesion else None


def _pregunta(conn, mundo: dict, funcion: str, nombre: str = "Sam Noble",
              slug: str = "north-lab", en: str | None = None) -> bool:
    with espacio(conn, mundo[en or slug]["id"]) as cur:
        cur.execute(f"select {funcion}(%s) as si", (_persona(mundo, nombre, slug),))
        si = cur.fetchone()["si"]
    conn.commit()
    return si


def _cortar(conn, mundo: dict, nombre: str = "Sam Noble", slug: str = "north-lab",
            en: str | None = None, **como) -> int:
    with espacio(conn, mundo[en or slug]["id"]) as cur:
        cortadas = web_app.cortar_sesiones(cur, _persona(mundo, nombre, slug), **como)
    conn.commit()
    return cortadas


def _encolar(conn, mundo: dict, nombre: str = "Taylor Quinn", *, clave: str = "respuesta:1",
             texto: str = "Ahí va tu enlace.", **mas) -> str:
    ws = mundo["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        enqueue_outbox(cur, workspace_id=ws,
                       chat_id=mundo["north-lab"]["people"][nombre]["telegram"], text=texto,
                       recipient_membership_id=_persona(mundo, nombre), dedupe_key=clave,
                       is_response=True, scheduled_for=AHORA,
                       enlace_de_entrada_web=_persona(mundo, nombre), **mas)
        cur.execute("select id from message_outbox where dedupe_key = %s", (clave,))
        fila = str(cur.fetchone()["id"])
    conn.commit()
    return fila


def _despachar(conn, mundo: dict, transporte) -> dict:
    ws = mundo["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        r = despachar(cur, ws, transporte, Calendario.desde_base(cur, ws), AHORA)
    conn.commit()
    return r


# --- Las tablas y las funciones -------------------------------------------------------------

def test_las_tablas_tienen_espacio_obligatorio_y_rls_forzado(conn):
    with admin(conn) as cur:
        for tabla in TABLAS:
            cur.execute("""select relrowsecurity, relforcerowsecurity
                             from pg_class where oid = to_regclass(%s)""", (f"leda.{tabla}",))
            fila = cur.fetchone()
            assert fila is not None, f"{tabla} no existe"
            assert fila["relrowsecurity"] and fila["relforcerowsecurity"], tabla
            cur.execute("""select is_nullable from information_schema.columns
                            where table_schema = 'leda' and table_name = %s
                              and column_name = 'workspace_id'""", (tabla,))
            assert cur.fetchone()["is_nullable"] == "NO", tabla
            cur.execute("select polname from pg_policy where polrelid = to_regclass(%s)",
                        (f"leda.{tabla}",))
            assert {p["polname"] for p in cur.fetchall()} == {"aislamiento_espacio"}, tabla


def test_la_aplicacion_agrega_y_lee_la_marca_y_maneja_el_ofrecimiento(conn):
    """La marca sólo se agrega y se lee (como la del enlace de una tarea); el ofrecimiento se
    reserva, se marca ofrecido y se libera. Nada para `public` ni para la autoridad."""
    esperado = {"message_outbox_entrada_web": {"select", "insert"},
                "ofrecimiento_web": {"select", "insert", "update", "delete"}}
    with admin(conn) as cur:
        for tabla, privilegios in esperado.items():
            for rol, deberia in (("leda_app", privilegios), ("leda_gateway", set()),
                                 ("public", set())):
                tiene = set()
                for privilegio in ("select", "insert", "update", "delete"):
                    cur.execute("select has_table_privilege(%s, %s, %s) as si",
                                (rol, f"leda.{tabla}", privilegio))
                    if cur.fetchone()["si"]:
                        tiene.add(privilegio)
                assert tiene == deberia, (tabla, rol, tiene)
            cur.execute("select has_table_privilege('leda_admin', %s, 'insert') as si",
                        (f"leda.{tabla}",))
            assert cur.fetchone()["si"], f"{tabla}: la bienvenida se escribe como leda_admin"


def test_las_funciones_son_elevadas_de_leda_owner_y_solo_las_ejecuta_la_aplicacion(conn):
    with admin(conn) as cur:
        for funcion in FUNCIONES:
            cur.execute("""select p.prosecdef, r.rolname dueno,
                                  has_function_privilege('leda_app', p.oid, 'execute') app,
                                  has_function_privilege('public', p.oid, 'execute') pub
                             from pg_proc p join pg_roles r on r.oid = p.proowner
                             join pg_namespace n on n.oid = p.pronamespace
                            where n.nspname = 'leda' and p.proname = %s""", (funcion,))
            fila = cur.fetchone()
            assert fila is not None, f"{funcion} no existe"
            assert fila["prosecdef"] and fila["dueno"] == "leda_owner", funcion
            assert fila["app"] and not fila["pub"], funcion


# --- Si entró alguna vez y si tiene un enlace sin usar --------------------------------------

def test_entro_a_la_web_solo_cuando_canjeo_un_enlace(conn, intake_world):
    assert _pregunta(conn, intake_world, "entro_a_la_web") is False
    token = _emitir(conn, intake_world)
    assert _pregunta(conn, intake_world, "entro_a_la_web") is False, "emitido no es entrar"
    assert _canjear(conn, token)
    assert _pregunta(conn, intake_world, "entro_a_la_web") is True
    # Y sigue habiendo entrado aunque después se le corte el acceso.
    _cortar(conn, intake_world)
    assert _pregunta(conn, intake_world, "entro_a_la_web") is True


def test_tiene_un_enlace_sin_usar_hasta_que_lo_canjea_o_se_anula(conn, intake_world):
    assert _pregunta(conn, intake_world, "tiene_un_enlace_sin_usar") is False
    token = _emitir(conn, intake_world)
    assert _pregunta(conn, intake_world, "tiene_un_enlace_sin_usar") is True
    assert _canjear(conn, token)
    assert _pregunta(conn, intake_world, "tiene_un_enlace_sin_usar") is False
    _emitir(conn, intake_world)
    _cortar(conn, intake_world)
    assert _pregunta(conn, intake_world, "tiene_un_enlace_sin_usar") is False


def test_un_enlace_vencido_sin_usar_todavia_cuenta_como_sin_usar(conn, intake_world):
    """El que un enlace nuevo deja sin servir, vencido o no (la 0065 no lo marca)."""
    _emitir(conn, intake_world)
    with admin(conn) as cur:
        cur.execute("update enlace_de_entrada set emitido_en = now() - interval '25 hours'")
    conn.commit()
    assert _pregunta(conn, intake_world, "tiene_un_enlace_sin_usar") is True


def test_desde_otro_espacio_las_preguntas_dan_que_no(conn, intake_world):
    """Una membresía de West Studio, vista desde North Lab, es igual a una que no existe."""
    token = _emitir(conn, intake_world, slug="west-studio")
    _emitir(conn, intake_world, nombre="Sam North", slug="west-studio")
    assert _canjear(conn, token)
    for funcion, nombre in (("entro_a_la_web", "Sam Noble"),
                            ("tiene_un_enlace_sin_usar", "Sam North")):
        assert _pregunta(conn, intake_world, funcion, nombre, slug="west-studio") is True
        assert _pregunta(conn, intake_world, funcion, nombre, slug="west-studio",
                         en="north-lab") is False, funcion


# --- El corte siempre deja su auditoría -----------------------------------------------------

def test_el_corte_sin_sesiones_deja_su_auditoria_con_el_motivo_y_quien(conn, intake_world):
    _emitir(conn, intake_world)                         # un enlace sin usar, ninguna sesión
    quien = intake_world["north-lab"]["people"]["Sam Noble"]["app_user_id"]
    assert _cortar(conn, intake_world, motivo="perdio_el_celular",
                   actor_app_user_id=quien) == 0
    [corte] = _auditoria(conn, "cortar_acceso_web")
    assert str(corte["workspace_id"]) == intake_world["north-lab"]["id"]
    assert (corte["sujeto_tipo"], str(corte["sujeto_id"])) == (
        "membership", _persona(intake_world))
    assert corte["actor_kind"] == "persona" and str(corte["actor_app_user_id"]) == quien
    assert corte["detalle"] == {"motivo": "perdio_el_celular", "sesiones_cortadas": 0,
                                "enlace_anulado": True}
    assert corte["pack_hash"] == "hash-0" and corte["nucleo_hash"]
    assert _auditoria(conn, "cortar_sesion_web") == []


def test_el_corte_sin_nada_que_cortar_tambien_queda(conn, intake_world):
    assert _cortar(conn, intake_world) == 0
    [corte] = _auditoria(conn, "cortar_acceso_web")
    assert corte["detalle"] == {"motivo": "administrador", "sesiones_cortadas": 0,
                                "enlace_anulado": False}
    assert corte["actor_kind"] == "leda" and corte["actor_app_user_id"] is None


def test_el_corte_con_sesiones_deja_cada_sesion_y_el_corte(conn, intake_world):
    for _ in range(2):
        assert _canjear(conn, _emitir(conn, intake_world))
    assert _cortar(conn, intake_world, motivo="perdio_el_celular") == 2
    sesiones = _auditoria(conn, "cortar_sesion_web")
    assert [s["detalle"]["motivo"] for s in sesiones] == ["perdio_el_celular"] * 2
    [corte] = _auditoria(conn, "cortar_acceso_web")
    assert corte["detalle"] == {"motivo": "perdio_el_celular", "sesiones_cortadas": 2,
                                "enlace_anulado": False}


def test_un_espacio_no_corta_ni_audita_a_alguien_de_otro(conn, intake_world):
    sesion = _canjear(conn, _emitir(conn, intake_world, slug="west-studio"))
    assert _cortar(conn, intake_world, slug="west-studio", en="north-lab") == 0
    assert _auditoria(conn, "cortar_acceso_web") == []
    [fila] = _filas(conn, "select cortada_en from sesion_web where id = %s", sesion)
    assert fila["cortada_en"] is None


def test_un_motivo_desconocido_no_corta_ni_audita(conn, intake_world):
    with pytest.raises(psycopg.errors.RaiseException, match="motivo desconocido"):
        _cortar(conn, intake_world, motivo="porque_si")
    conn.rollback()
    assert _auditoria(conn, "cortar_acceso_web") == []


# --- La marca en la salida y el despachador -------------------------------------------------

def test_la_salida_guarda_la_marca_y_no_el_enlace(conn, intake_world, direccion):
    fila = _encolar(conn, intake_world)
    [marca] = _filas(conn, "select * from message_outbox_entrada_web")
    assert str(marca["outbox_id"]) == fila
    assert str(marca["membership_id"]) == _persona(intake_world, "Taylor Quinn")
    assert marca["es_ofrecimiento"] is False
    [salida] = _filas(conn, "select cuerpo from message_outbox")
    assert "/app/entrar/" not in salida["cuerpo"] and BASE not in salida["cuerpo"]
    assert _filas(conn, "select * from enlace_de_entrada") == []    # se emite al mandar


def test_el_ofrecimiento_queda_marcado_como_tal(conn, intake_world, direccion):
    _encolar(conn, intake_world, es_ofrecimiento=True)
    [marca] = _filas(conn, "select es_ofrecimiento from message_outbox_entrada_web")
    assert marca["es_ofrecimiento"] is True


def test_el_despachador_arma_el_boton_de_la_mini_app_al_mandar(conn, intake_world, direccion):
    """ADR 0024 (migración 0073): la marca lleva un botón que abre la web como Mini App del bot
    del espacio; ni el texto ni la base llevan un enlace de entrada, y no se emite ninguno."""
    _encolar(conn, intake_world)
    transporte = TransporteDePrueba()
    assert _despachar(conn, intake_world, transporte)["enviados"] == 1
    [mensaje] = transporte.enviados
    assert mensaje.texto == "Ahí va tu enlace."
    [boton] = mensaje.botones
    assert (boton.etiqueta, boton.web_app) == ("Ver mis tareas", f"{BASE}/app/e/north-lab/")
    assert _filas(conn, "select * from enlace_de_entrada") == []


@pytest.mark.parametrize("destino, tarea, etiqueta, consulta", [
    ("equipo", False, "Ver el equipo", "?vista=equipo"),
    ("tarea", True, "Ver la tarea", "?tarea="),
    ("cargar_tarea", False, "Cargar la tarea", "?nueva=tarea"),
    ("crear_objetivo", False, "Crear el objetivo", "?nueva=objetivo"),
])
def test_cada_boton_dice_lo_que_va_a_pasar_y_lleva_directo_a_eso(conn, intake_world, direccion,
                                                                  destino, tarea, etiqueta,
                                                                  consulta):
    task_id = None
    if tarea:
        with admin(conn) as cur:
            cur.execute("select id from task limit 1")
            fila = cur.fetchone()
            if fila is None:
                cur.execute("""insert into task (workspace_id, objective_id, titulo, area_id,
                                                 responsable_membership_id)
                               values (%s, %s, 'Una', %s, %s) returning id""",
                            (intake_world["north-lab"]["id"],
                             intake_world["north-lab"]["objectives"][0],
                             intake_world["north-lab"]["areas"]["field"],
                             _persona(intake_world, "Taylor Quinn")))
                fila = cur.fetchone()
            task_id = str(fila["id"])
        conn.commit()
    _encolar(conn, intake_world, destino_web=destino, tarea_web=task_id)
    transporte = TransporteDePrueba()
    _despachar(conn, intake_world, transporte)
    [boton] = transporte.enviados[0].botones
    assert boton.etiqueta == etiqueta
    assert boton.web_app == f"{BASE}/app/e/north-lab/{consulta}" + (task_id or "")


def test_en_un_grupo_no_va_el_boton_y_queda_un_incidente(conn, intake_world, direccion):
    """La Bot API no deja un botón de Mini App en un grupo (ADR 0024, decisión 2)."""
    ws = intake_world["north-lab"]["id"]
    persona = _persona(intake_world, "Taylor Quinn")
    with espacio(conn, ws) as cur:
        enqueue_outbox(cur, workspace_id=ws, chat_id=-100123, text="Al grupo.",
                       recipient_membership_id=persona, dedupe_key="grupo",
                       scheduled_for=AHORA, enlace_de_entrada_web=persona)
    conn.commit()
    transporte = TransporteDePrueba()
    _despachar(conn, intake_world, transporte)
    assert transporte.enviados[0].botones == []
    assert [i["etapa"] for i in _filas(conn, "select etapa from incident")] == [
        "enlace_de_entrada_web"]


def test_sin_direccion_publica_sale_sin_enlace_y_deja_un_incidente(conn, intake_world,
                                                                    monkeypatch):
    _encolar(conn, intake_world)
    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url=""))
    transporte = TransporteDePrueba()
    assert _despachar(conn, intake_world, transporte)["enviados"] == 1
    [mensaje] = transporte.enviados
    assert "/app/entrar/" not in mensaje.texto and mensaje.botones == []
    assert _filas(conn, "select * from enlace_de_entrada") == []
    [incidente] = _filas(conn, "select etapa from incident")
    assert incidente["etapa"] == "enlace_de_entrada_web"


def test_repetir_el_encolado_no_duplica_la_marca(conn, intake_world, direccion):
    _encolar(conn, intake_world)
    _encolar(conn, intake_world)
    assert len(_filas(conn, "select * from message_outbox_entrada_web")) == 1


def test_la_marca_no_va_partida_con_adjuntos_ni_con_bloque_ni_con_otro_enlace(
        conn, intake_world, direccion):
    ws = intake_world["north-lab"]["id"]
    persona = _persona(intake_world, "Taylor Quinn")
    with admin(conn) as cur:
        cur.execute("""insert into task (workspace_id, objective_id, titulo, area_id,
                                         responsable_membership_id, criterio_aceptacion,
                                         evidencia_requerida)
                       values (%s, %s, 'Una', %s, %s, 'Que ande', '{}') returning id""",
                    (ws, intake_world["north-lab"]["objectives"][0],
                     intake_world["north-lab"]["areas"]["field"], persona))
        tarea = str(cur.fetchone()["id"])
    conn.commit()
    for extra in ({"allow_split": True}, {"adjuntos": [str(secrets.token_hex(4))]},
                  {"bloque_copiable": "x"}, {"enlace_de_tarea": (tarea, persona)}):
        with espacio(conn, ws) as cur, pytest.raises(PayloadValidationError):
            enqueue_outbox(cur, workspace_id=ws, chat_id=71001, text="x", dedupe_key="x",
                           recipient_membership_id=persona, enlace_de_entrada_web=persona,
                           **extra)
        conn.rollback()
    with espacio(conn, ws) as cur, pytest.raises(PayloadValidationError):
        enqueue_outbox(cur, workspace_id=ws, chat_id=71001, text="x", dedupe_key="x",
                       recipient_membership_id=persona, es_ofrecimiento=True)
    conn.rollback()


def test_el_boton_no_le_quita_lugar_al_texto(conn, intake_world, direccion):
    """El botón no va en el texto: un texto que entra solo entra también con el botón."""
    from leda.salida import TELEGRAM_TEXT_LIMIT, margen_saludo

    largo = TELEGRAM_TEXT_LIMIT - margen_saludo(personal=True) - 10
    ws = intake_world["north-lab"]["id"]
    persona = _persona(intake_world, "Taylor Quinn")
    with espacio(conn, ws) as cur:
        assert enqueue_outbox(cur, workspace_id=ws, chat_id=71001, text="a" * largo,
                              dedupe_key="con", recipient_membership_id=persona,
                              enlace_de_entrada_web=persona) == 1
    conn.rollback()


# --- Aislamiento ----------------------------------------------------------------------------

def test_desde_un_espacio_no_se_ven_las_marcas_ni_los_ofrecimientos_de_otro(conn, intake_world):
    oeste = intake_world["west-studio"]
    persona = _persona(intake_world, slug="west-studio")
    with espacio(conn, oeste["id"]) as cur:
        enqueue_outbox(cur, workspace_id=oeste["id"], chat_id=71103, text="Hola.",
                       recipient_membership_id=persona, dedupe_key="oeste")
        cur.execute("""insert into message_outbox_entrada_web (workspace_id, outbox_id,
                                                             membership_id)
                       select workspace_id, id, %s from message_outbox
                        where dedupe_key = 'oeste'""", (persona,))
        cur.execute("insert into ofrecimiento_web (workspace_id, membership_id) values (%s, %s)",
                    (oeste["id"], persona))
    conn.commit()
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        for tabla in TABLAS:
            cur.execute(f"select count(*) n from {tabla}")
            assert cur.fetchone()["n"] == 0, f"{tabla}: se ven filas de otro espacio"
        # Ni se puede escribir una del otro espacio.
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            cur.execute("""insert into ofrecimiento_web (workspace_id, membership_id)
                           values (%s, %s)""",
                        (oeste["id"], _persona(intake_world, "Sam North", "west-studio")))
    conn.rollback()


# --- La vuelta atrás ------------------------------------------------------------------------

def test_el_rollback_de_la_0066_se_niega_si_hay_marcas_u_ofrecimientos(conn, intake_world):
    script = (Path(__file__).resolve().parents[2] / "db" / "rollbacks"
              / "0066_la_entrada_a_la_web_por_chat.sql").read_text("utf-8")
    guarda = re.findall(r"do \$\$.*?end \$\$;", script, re.S)[-1]
    ws = intake_world["north-lab"]["id"]
    with admin(conn) as cur:
        cur.execute("insert into ofrecimiento_web (workspace_id, membership_id) values (%s, %s)",
                    (ws, _persona(intake_world)))
    conn.commit()
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.RaiseException, match="0066 rollback refused"), \
                conn.transaction():
            cur.execute("set local search_path = leda, public")
            cur.execute(guarda)
        cur.execute("select count(*) n from ofrecimiento_web")
        assert cur.fetchone()["n"] == 1
