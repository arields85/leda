"""La página de la tarea y su enlace (ADR 0019, decisión 7; migración 0036): la capa de garantías.

Lo que se prueba acá es la base y la credencial, no la conversación:

- **Aislamiento.** `acceso_tarea`, `vista_de_tarea` y `message_outbox_enlace` tienen `row level
  security` forzado y el espacio obligatorio. Un token de un espacio no lee nada de otro, y el id
  de una evidencia de otra tarea (del mismo espacio o de otro) no se sirve: devuelve lo mismo que
  un enlace inválido.
- **La credencial.** Sólo se guarda el hash del token; `leda_app` no tiene ningún privilegio sobre
  `acceso_tarea` ni sobre el registro de vistas, sólo `execute` sobre las funciones que los
  emiten y los leen, que son `security definer` con dueño `leda_owner`.
- **Quién ve** (7b): el responsable, quien aprueba su trabajo hoy y quien ya decidió sobre esa
  tarea, el referente del área de la tarea (un dato del espacio, no el nombre de un rol) y la
  autoridad final del espacio. Otro integrante, una membresía inactiva y un token revocado
  reciben lo mismo que un token inexistente. El derecho a ver se revalida en cada pedido: un
  cambio de quien aprueba se refleja en el siguiente.
- **El registro de quién mira** (7e): cada vista y cada descarga dejan una fila, sin dirección
  ni navegador.
"""

from __future__ import annotations

import contextlib
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb
import pytest

from leda import pagina_de_tarea as P
from leda.db import admin, espacio

AHORA = datetime(2026, 10, 22, 18, 0, tzinfo=timezone.utc)
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01" + b"\x00" * 32 + b"\xff\xd9"
PDF = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<>>\nendobj\n%%EOF\n"
NUEVAS = ("acceso_tarea", "vista_de_tarea", "message_outbox_enlace")
FUNCIONES = ("puede_ver_tarea", "emitir_acceso_tarea", "acceso_tarea_vigente",
             "leer_pagina_de_tarea", "leer_archivo_de_tarea")


# --- Ayudas ---------------------------------------------------------------------------------

@contextlib.contextmanager
def sin_espacio(conn):
    """La aplicación antes de saber a qué espacio pertenece el pedido (como el tablero)."""
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local role leda_app")
            yield cur


def _archivo(cur, ws: str, por: str, contenido: bytes, tipo: str, clase: str,
             nombre: str) -> str:
    cur.execute(
        """insert into archivo (workspace_id, contenido, sha256, tamano, tipo, clase,
                                nombre_original, enviado_por_membership_id, recibido_en)
           values (%s, %s, %s, %s, %s, %s, %s, %s, %s) returning id""",
        (ws, contenido, hashlib.sha256(contenido).hexdigest(), len(contenido), tipo, clase,
         nombre, por, AHORA))
    return str(cur.fetchone()["id"])


def _tarea(cur, mundo: dict, *, titulo: str, persona: str = "Sam Noble",
           area: str = "quality") -> dict:
    """Una tarea entregada con tres piezas: lo que escribió, una foto y un PDF."""
    ws = mundo["id"]
    responsable = mundo["people"][persona]["membership_id"]
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, criterio_aceptacion,
                             evidencia_requerida)
           values (%s, %s, %s, %s, %s, 'Que ande', '{}') returning id""",
        (ws, mundo["objectives"][0], titulo, mundo["areas"][area], responsable))
    tarea = str(cur.fetchone()["id"])
    cur.execute("""insert into task_state_event (task_id, estado_nuevo, actor_kind)
                   values (%s, 'en_curso', 'leda')""", (tarea,))
    marca = titulo.encode()
    foto = _archivo(cur, ws, responsable, JPEG + marca, "image/jpeg", "imagen",
                    "pantalla.jpg")
    pdf = _archivo(cur, ws, responsable, PDF + marca, "application/pdf", "pdf",
                   "informe.pdf")
    piezas = {}
    for clave, clase, texto, archivo in (("texto", "texto", "Quedó andando", None),
                                         ("foto", "imagen", None, foto),
                                         ("pdf", "archivo", None, pdf)):
        cur.execute(
            """insert into evidence (workspace_id, task_id, tipo, clase, texto, archivo_id,
                                     entregado_por)
               values (%s, %s, %s, %s, %s, %s, %s) returning id""",
            (ws, tarea, clase, clase, texto, archivo, responsable))
        piezas[clave] = str(cur.fetchone()["id"])
    cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                 actor_kind)
                   values (%s, 'en_curso', 'en_revision', 'persona')""", (tarea,))
    return {"id": tarea, "ws": ws, "piezas": piezas}


@pytest.fixture
def mundo(conn, intake_world) -> dict:
    """North Lab: la tarea de Sam Noble (área quality), que aprueba Taylor Quinn; la de Sam
    North (área field). West Studio: una tarea de Sam Noble. Morgan Hale es la autoridad final
    de cada espacio."""
    with admin(conn) as cur:
        norte = _tarea(cur, intake_world["north-lab"], titulo="Calibrar la balanza")
        vecina = _tarea(cur, intake_world["north-lab"], titulo="Pintar el galpón",
                        persona="Sam North", area="field")
        oeste = _tarea(cur, intake_world["west-studio"], titulo="Secreto del oeste")
    conn.commit()
    return {"norte": norte, "vecina": vecina, "oeste": oeste, **intake_world}


def _persona(mundo: dict, nombre: str, slug: str = "north-lab") -> str:
    return mundo[slug]["people"][nombre]["membership_id"]


def _emitir(conn, mundo: dict, nombre: str, tarea: dict | None = None,
            slug: str = "north-lab") -> str | None:
    tarea = tarea or mundo["norte"]
    with espacio(conn, mundo[slug]["id"]) as cur:
        token = P.emitir(cur, _persona(mundo, nombre, slug), tarea["id"])
    conn.commit()
    return token


def _leer(conn, token: str) -> dict | None:
    with sin_espacio(conn) as cur:
        datos = P.leer(cur, token)
    conn.commit()
    return datos


def _leer_archivo(conn, token: str, evidencia: str) -> dict | None:
    with sin_espacio(conn) as cur:
        datos = P.leer_archivo(cur, token, evidencia)
    conn.commit()
    return datos


# --- Las tablas y las funciones -------------------------------------------------------------

def test_las_tablas_nuevas_tienen_espacio_obligatorio_y_rls_forzado(conn):
    with admin(conn) as cur:
        for tabla in NUEVAS:
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
            assert "aislamiento_espacio" in {p["polname"] for p in cur.fetchall()}, tabla


def test_el_registro_de_vistas_no_guarda_direccion_ni_navegador(conn):
    """7e: qué acceso, cuándo y qué se sirvió; nada que identifique la máquina de quien mira."""
    with admin(conn) as cur:
        cur.execute("""select column_name from information_schema.columns
                        where table_schema = 'leda' and table_name = 'vista_de_tarea'""")
        columnas = {f["column_name"] for f in cur.fetchall()}
    assert columnas == {"id", "workspace_id", "acceso_tarea_id", "at", "que", "evidence_id"}


def test_la_aplicacion_no_tiene_privilegios_sobre_los_accesos_ni_las_vistas(conn, mundo):
    with espacio(conn, mundo["north-lab"]["id"]) as cur:
        for tabla in ("acceso_tarea", "vista_de_tarea"):
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                cur.execute(f"select * from {tabla}")
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                cur.execute(f"delete from {tabla}")


def test_las_funciones_nuevas_son_de_leda_owner(conn):
    with admin(conn) as cur:
        cur.execute(
            """select p.proname, r.rolname, p.prosecdef
                 from pg_proc p join pg_roles r on r.oid = p.proowner
                 join pg_namespace n on n.oid = p.pronamespace
                where n.nspname = 'leda' and p.proname = any(%s)""", (list(FUNCIONES),))
        filas = {f["proname"]: f for f in cur.fetchall()}
    assert set(filas) == set(FUNCIONES)
    assert {f["rolname"] for f in filas.values()} == {"leda_owner"}
    for nombre in ("emitir_acceso_tarea", "leer_pagina_de_tarea", "leer_archivo_de_tarea"):
        assert filas[nombre]["prosecdef"], f"{nombre} tiene que ser security definer"


def test_la_aplicacion_no_resuelve_un_token_por_su_cuenta(conn, mundo):
    """El acceso vigente lo usan sólo las funciones de lectura: `leda_app` no puede llamarlo
    para fijar el espacio de otro."""
    token = _emitir(conn, mundo, "Sam Noble")
    with sin_espacio(conn) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute("select * from acceso_tarea_vigente(%s)", (P._hash(token),))


# --- La credencial --------------------------------------------------------------------------

def test_solo_se_guarda_el_hash_del_token(conn, mundo):
    token = _emitir(conn, mundo, "Sam Noble")
    assert token
    with admin(conn) as cur:
        cur.execute("select * from acceso_tarea")
        filas = cur.fetchall()
    assert len(filas) == 1
    for columna, valor in filas[0].items():
        assert token not in str(valor), f"el token en claro apareció en {columna}"
    assert filas[0]["token_hash"] == hashlib.sha256(token.encode()).hexdigest()
    assert filas[0]["revocado_en"] is None


def test_cada_emision_es_un_token_nuevo(conn, mundo):
    """Uno por persona y por tarea en su alcance: emitir otra vez no devuelve el mismo."""
    assert _emitir(conn, mundo, "Sam Noble") != _emitir(conn, mundo, "Sam Noble")


def test_un_token_inventado_no_lee_nada(conn, mundo):
    assert _leer(conn, "token-inventado") is None
    assert _leer(conn, "") is None


# --- Quién ve -------------------------------------------------------------------------------

def test_la_ve_el_responsable(conn, mundo):
    datos = _leer(conn, _emitir(conn, mundo, "Sam Noble"))
    assert datos is not None
    assert datos["tarea"]["titulo"] == "Calibrar la balanza"


def test_la_ve_quien_aprueba_el_trabajo_del_responsable(conn, mundo):
    assert _leer(conn, _emitir(conn, mundo, "Taylor Quinn")) is not None


def test_la_ve_la_autoridad_final_del_espacio(conn, mundo):
    assert _leer(conn, _emitir(conn, mundo, "Morgan Hale")) is not None


def test_otro_integrante_no_la_ve(conn, mundo):
    """Sam North es del equipo, pero no tiene nada que ver con esta tarea (constitución §8)."""
    assert _emitir(conn, mundo, "Sam North") is None
    with admin(conn) as cur:
        cur.execute("select count(*) n from acceso_tarea")
        assert cur.fetchone()["n"] == 0


def test_la_ve_el_referente_del_area_de_la_tarea(conn, mundo):
    """El referente es un dato del espacio (`area.referente_membership_id`), no el nombre de un
    rol: con Sam North como referente de quality, la ve."""
    assert _emitir(conn, mundo, "Sam North") is None
    with admin(conn) as cur:
        cur.execute("update area set referente_membership_id = %s where id = %s",
                    (_persona(mundo, "Sam North"), mundo["north-lab"]["areas"]["quality"]))
    conn.commit()
    assert _leer(conn, _emitir(conn, mundo, "Sam North")) is not None


def test_el_referente_es_del_mismo_espacio(conn, mundo):
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            cur.execute("update area set referente_membership_id = %s where id = %s",
                        (_persona(mundo, "Sam North", "west-studio"),
                         mundo["north-lab"]["areas"]["quality"]))


def test_la_ve_quien_ya_decidio_sobre_ella(conn, mundo):
    """Quien aprobó o pidió cambios sobre esta tarea la sigue viendo aunque ya no sea quien
    aprueba al responsable."""
    with admin(conn) as cur:
        cur.execute(
            """insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                     aprobador_membership_id, decision, comentario)
               values (%s, 'tarea', %s, %s, 'rechazado', 'falta el informe')""",
            (mundo["north-lab"]["id"], mundo["norte"]["id"], _persona(mundo, "Sam North")))
    conn.commit()
    assert _leer(conn, _emitir(conn, mundo, "Sam North")) is not None


def test_el_cambio_de_quien_aprueba_se_refleja_en_el_siguiente_pedido(conn, mundo):
    token = _emitir(conn, mundo, "Taylor Quinn")
    assert _leer(conn, token) is not None
    with admin(conn) as cur:
        cur.execute("update membership set aprobador_membership_id = %s where id = %s",
                    (_persona(mundo, "Morgan Hale"), _persona(mundo, "Sam Noble")))
    conn.commit()
    assert _leer(conn, token) is None


def test_una_membresia_inactiva_pierde_el_acceso(conn, mundo):
    token = _emitir(conn, mundo, "Taylor Quinn")
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (_persona(mundo, "Taylor Quinn"),))
    conn.commit()
    assert _leer(conn, token) is None


def test_un_token_revocado_no_lee_nada(conn, mundo):
    token = _emitir(conn, mundo, "Sam Noble")
    with admin(conn) as cur:
        cur.execute("update acceso_tarea set revocado_en = now()")
    conn.commit()
    assert _leer(conn, token) is None


# --- El aislamiento -------------------------------------------------------------------------

def test_un_token_lee_solo_su_tarea_y_nada_de_otro_espacio(conn, mundo):
    datos = _leer(conn, _emitir(conn, mundo, "Morgan Hale"))
    texto = str(datos)
    assert "Calibrar la balanza" in texto
    assert "Pintar el galpón" not in texto, "la autoridad final ve todas, pero de a una"
    assert "Secreto del oeste" not in texto
    assert "West Studio" not in texto


def test_no_se_emite_un_token_para_una_tarea_de_otro_espacio(conn, mundo):
    with espacio(conn, mundo["north-lab"]["id"]) as cur:
        assert P.emitir(cur, _persona(mundo, "Morgan Hale"), mundo["oeste"]["id"]) is None
        assert P.emitir(cur, _persona(mundo, "Sam Noble", "west-studio"),
                        mundo["oeste"]["id"]) is None
    conn.commit()


def test_un_archivo_se_sirve_solo_si_su_evidencia_es_de_la_tarea_del_token(conn, mundo):
    token = _emitir(conn, mundo, "Morgan Hale")
    propio = _leer_archivo(conn, token, mundo["norte"]["piezas"]["foto"])
    assert propio is not None
    assert propio["contenido"] == JPEG + b"Calibrar la balanza"
    assert propio["tipo"] == "image/jpeg"
    for ajena in (mundo["vecina"]["piezas"]["foto"], mundo["oeste"]["piezas"]["foto"],
                  mundo["oeste"]["piezas"]["pdf"]):
        assert _leer_archivo(conn, token, ajena) is None
    assert _leer_archivo(conn, token, str(uuid.uuid4())) is None
    assert _leer_archivo(conn, token, "no-es-un-id") is None
    assert _leer_archivo(conn, token, mundo["norte"]["piezas"]["texto"]) is None


def test_una_pieza_retirada_no_se_sirve(conn, mundo):
    with admin(conn) as cur:
        cur.execute("""insert into evidencia_retirada (workspace_id, evidence_id,
                                                       retirada_por_membership_id, motivo)
                       values (%s, %s, %s, 'no era esa')""",
                    (mundo["north-lab"]["id"], mundo["norte"]["piezas"]["foto"],
                     _persona(mundo, "Sam Noble")))
    conn.commit()
    token = _emitir(conn, mundo, "Sam Noble")
    assert _leer_archivo(conn, token, mundo["norte"]["piezas"]["foto"]) is None
    datos = _leer(conn, token)
    retiradas = [e for e in datos["evidencia"] if e["retirada"]]
    assert [e["id"] for e in retiradas] == [mundo["norte"]["piezas"]["foto"]]


def test_leer_no_deja_fijado_el_espacio_del_token(conn, mundo):
    """Las funciones de lectura fijan el espacio que sale del token para leer y lo devuelven
    como estaba: la transacción que llama no queda mirando otro espacio."""
    token = _emitir(conn, mundo, "Sam Noble")
    with sin_espacio(conn) as cur:
        P.leer(cur, token)
        cur.execute("select current_setting('leda.workspace_id', true) as ws")
        assert not cur.fetchone()["ws"]
        cur.execute("select count(*) n from task")
        assert cur.fetchone()["n"] == 0
    conn.commit()


# --- Lo que lee -----------------------------------------------------------------------------

def test_la_lectura_trae_la_tarea_su_historia_y_su_evidencia(conn, mundo):
    with admin(conn) as cur:
        cur.execute(
            """insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                     aprobador_membership_id, decision, comentario)
               values (%s, 'tarea', %s, %s, 'rechazado', 'falta el informe')""",
            (mundo["north-lab"]["id"], mundo["norte"]["id"], _persona(mundo, "Taylor Quinn")))
        cur.execute("""insert into blocker (workspace_id, task_id, causa, abierto_por)
                       values (%s, %s, 'falta la pesa patrón', %s)""",
                    (mundo["north-lab"]["id"], mundo["norte"]["id"],
                     _persona(mundo, "Sam Noble")))
    conn.commit()
    datos = _leer(conn, _emitir(conn, mundo, "Taylor Quinn"))
    tarea = datos["tarea"]
    assert tarea["area"] == "Quality Guild"
    assert tarea["responsable"] == "Sam Noble 1"
    assert tarea["quien_aprueba"] == "Taylor Quinn 1"
    assert tarea["estado"] == "en_revision"
    assert tarea["criterio_aceptacion"] == "Que ande"
    assert datos["persona"] == "Taylor Quinn 1"
    assert datos["espacio"] == "North Lab"
    que = [h["que"] for h in datos["historia"]]
    assert "estado" in que and "pedido_de_cambios" in que and "bloqueo" in que
    cambios = next(h for h in datos["historia"] if h["que"] == "pedido_de_cambios")
    assert cambios["comentario"] == "falta el informe"
    assert cambios["quien"] == "Taylor Quinn 1"
    bloqueo = next(h for h in datos["historia"] if h["que"] == "bloqueo")
    assert bloqueo["causa"] == "falta la pesa patrón"
    clases = sorted(e["clase"] for e in datos["evidencia"])
    assert clases == ["archivo", "imagen", "texto"]
    assert all(e["quien"] == "Sam Noble 1" and e["cuando"] for e in datos["evidencia"])


def asentar_un_bloqueo(conn, mundo: dict, tarea: dict | None = None) -> None:
    """Un bloqueo de Sam Noble que destraba Taylor Quinn, con lo que dijo Taylor Quinn y que
    quedó asentado a los cinco días hábiles (C-5, porciones 1 a 5)."""
    ws, tarea = mundo["north-lab"]["id"], (tarea or mundo["norte"])["id"]
    sam, taylor = _persona(mundo, "Sam Noble"), _persona(mundo, "Taylor Quinn")
    with admin(conn) as cur:
        cur.execute("""insert into blocker (workspace_id, task_id, causa, abierto_por, abierto_en)
                       values (%s, %s, 'falta la pesa patrón', %s, %s) returning id""",
                    (ws, tarea, sam, datetime(2026, 10, 19, 13, 0, tzinfo=timezone.utc)))
        bloqueo = str(cur.fetchone()["id"])
        cur.execute("""insert into blocker_unblocker (workspace_id, blocker_id,
                                                      destraba_membership_id,
                                                      dicho_por_membership_id, at)
                       values (%s, %s, %s, %s, %s) returning id""",
                    (ws, bloqueo, taylor, sam, datetime(2026, 10, 19, 13, 5, tzinfo=timezone.utc)))
        fila = str(cur.fetchone()["id"])
        cur.execute("""insert into dicho_de_quien_destraba (workspace_id, blocker_unblocker_id,
                                                            dicho_por_membership_id, para_cuando,
                                                            lo_que_dice, at)
                       values (%s, %s, %s, '2026-10-23', 'la traigo del depósito', %s)""",
                    (ws, fila, taylor, datetime(2026, 10, 19, 14, 0, tzinfo=timezone.utc)))
        cur.execute("""insert into audit_log (workspace_id, actor_kind, accion, sujeto_tipo,
                                              sujeto_id, detalle)
                       values (%s, 'leda', 'asentar_bloqueo_que_sigue_abierto', 'blocker', %s,
                               %s)""",
                    (ws, bloqueo, Jsonb(
                        {"task_id": tarea, "vez": 1, "dias_habiles_trabada": 5,
                         "a_membership_id": taylor, "at": "2026-10-26T13:00:00+00:00"})))
    conn.commit()


def test_la_historia_trae_lo_que_quedo_asentado_de_un_bloqueo(conn, mundo):
    """Decisión 49 del usuario (C-5c): lo asentado de un bloqueo queda en la historia de la tarea:
    quién dijo que lo destraba, lo que dijo esa persona y que quedó asentado, sin decir a quién se
    le informó."""
    asentar_un_bloqueo(conn, mundo)

    historia = _leer(conn, _emitir(conn, mundo, "Taylor Quinn"))["historia"]

    quien = next(h for h in historia if h["que"] == "quien_destraba")
    assert (quien["quien"], quien["destraba"]) == ("Sam Noble 1", "Taylor Quinn 1")
    dicho = next(h for h in historia if h["que"] == "dicho_del_bloqueo")
    assert (dicho["quien"], dicho["para_cuando"]) == ("Taylor Quinn 1", "2026-10-23")
    assert dicho["lo_que_dice"] == "la traigo del depósito"
    asentado = next(h for h in historia if h["que"] == "asentado")
    assert (asentado["por"], asentado["dias_habiles"]) == ("sigue_trabada", 5)
    assert asentado["cuando"].startswith("2026-10-26")
    assert "a_membership_id" not in asentado and "a" not in asentado
    # En el orden en que pasó: se trabó, quién lo destraba, lo que dijo, quedó asentado.
    orden = [h["que"] for h in historia if h["que"] in ("bloqueo", "quien_destraba",
                                                        "dicho_del_bloqueo", "asentado")]
    assert orden == ["bloqueo", "quien_destraba", "dicho_del_bloqueo", "asentado"]


def test_lo_asentado_de_un_bloqueo_no_se_ve_en_otra_tarea(conn, mundo):
    asentar_un_bloqueo(conn, mundo)

    historia = _leer(conn, _emitir(conn, mundo, "Morgan Hale", mundo["vecina"]))["historia"]

    assert not [h for h in historia
                if h["que"] in ("quien_destraba", "dicho_del_bloqueo", "asentado")]


def test_quien_hablo_sin_decir_quien_la_destraba_no_figura_como_quien_la_destraba(conn,
                                                                                  mundo):
    """Migración 0051 (decisión 41, revisión de la C-5d): a quien se le informó que la tarea sigue
    trabada dice algo sin que nadie haya dicho quién la destraba. La historia trae lo que dijo,
    nunca que la destraba esa persona (constitución §4)."""
    ws, tarea = mundo["north-lab"]["id"], mundo["norte"]["id"]
    sam, taylor = _persona(mundo, "Sam Noble"), _persona(mundo, "Taylor Quinn")
    with admin(conn) as cur:
        cur.execute("""insert into blocker (workspace_id, task_id, causa, abierto_por, abierto_en)
                       values (%s, %s, 'falta la pesa patrón', %s, %s) returning id""",
                    (ws, tarea, sam, datetime(2026, 10, 19, 13, 0, tzinfo=timezone.utc)))
        bloqueo = str(cur.fetchone()["id"])
        cur.execute("""insert into blocker_unblocker (workspace_id, blocker_id, sin_decir_quien,
                                                      dicho_por_membership_id, at)
                       values (%s, %s, true, %s, %s) returning id""",
                    (ws, bloqueo, taylor, datetime(2026, 10, 26, 14, 0, tzinfo=timezone.utc)))
        fila = str(cur.fetchone()["id"])
        cur.execute("""insert into dicho_de_quien_destraba (workspace_id, blocker_unblocker_id,
                                                            dicho_por_membership_id, para_cuando,
                                                            at)
                       values (%s, %s, %s, '2026-10-27', %s)""",
                    (ws, fila, taylor, datetime(2026, 10, 26, 14, 0, tzinfo=timezone.utc)))
    conn.commit()

    historia = _leer(conn, _emitir(conn, mundo, "Taylor Quinn"))["historia"]

    assert not [h for h in historia if h["que"] == "quien_destraba"]
    dicho = next(h for h in historia if h["que"] == "dicho_del_bloqueo")
    assert (dicho["quien"], dicho["para_cuando"]) == ("Taylor Quinn 1", "2026-10-27")


def test_cada_vista_y_cada_descarga_quedan_registradas(conn, mundo):
    token = _emitir(conn, mundo, "Taylor Quinn")
    _leer(conn, token)
    _leer_archivo(conn, token, mundo["norte"]["piezas"]["pdf"])
    _leer_archivo(conn, token, mundo["vecina"]["piezas"]["pdf"])     # no se sirve: no cuenta
    with admin(conn) as cur:
        cur.execute("select que, evidence_id from vista_de_tarea order by at")
        vistas = [(f["que"], f["evidence_id"] and str(f["evidence_id"]))
                  for f in cur.fetchall()]
    assert vistas == [("pagina", None), ("archivo", mundo["norte"]["piezas"]["pdf"])]


# --- El referente de cada área, del pack ----------------------------------------------------

def test_el_pack_carga_el_referente_de_cada_area(conn, corework):
    with admin(conn) as cur:
        cur.execute("""select a.slug, u.nombre from area a
                         left join membership m on m.id = a.referente_membership_id
                         left join app_user u on u.id = m.app_user_id
                        where a.workspace_id = %s""", (corework.workspace_id,))
        referentes = {f["slug"]: f["nombre"] for f in cur.fetchall()}
    assert referentes["ot"] == "Marcos Tarquini"
    assert referentes["electricidad"] == "Mariano Naim"
    assert referentes["gestion"] is None


def test_un_referente_que_no_es_del_pack_no_se_importa():
    import yaml

    from leda.importador import validar

    pack = yaml.safe_load((Path(__file__).resolve().parents[2] / "espacios" / "corework.yaml")
                          .read_text("utf-8"))
    pack["areas"][1]["referente"] = "alguien"
    assert any("referente que no existe" in b for b in validar(pack)[0])
