"""La evidencia de la entrega (ADR 0019, decisiones 3 y 5; migración 0034): la capa de garantías.

Lo que se prueba acá es la base y la cocina, no la conversación:

- **La política se cumple por tipo.** Cada tipo pedido necesita una pieza propia del ciclo
  vigente, no retirada, de una clase que ese tipo acepta (dato del pack): una frase sola no cubre
  `foto`, una imagen sola no cubre `explicacion`, lo retirado y lo de antes de un pedido de
  cambios no cuentan, y aprobar sigue exigiendo la política completa.
- **La clase la fija el código por el contenido.** La base no deja que una pieza diga ser una
  imagen si su archivo no lo es, ni que un texto apunte a un archivo.
- **Inmutabilidad.** `leda_app` sólo agrega y lee la evidencia, sus retiros y los archivos
  dichos de una tarea; un disparador rechaza cualquier cambio o borrado de una evidencia o de un
  retiro, también para la administración. Retirar no borra nada.
- **Aislamiento.** Las tablas nuevas tienen `row level security` forzado y el espacio
  obligatorio; una pieza no apunta a un archivo, a una tarea ni a una evidencia de otro espacio.
- **La cocina.** `entregar_tarea` escribe las piezas y el paso a revisión en un solo acto, sólo
  con la política completa y nunca a `terminada`; `retirar_evidencia` lo hace sólo quien la
  entregó, mientras la tarea no está aprobada.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

import psycopg
import pytest
from psycopg.types.json import Jsonb

from leda import herramientas as H
from leda.autoridad import Canal, Denegado, identificar
from leda.db import admin, espacio
from leda.importador import validar

NUEVAS = ("evidencia_retirada", "archivo_de_tarea")
AHORA = datetime(2026, 10, 8, 13, 0, tzinfo=timezone.utc)
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01" + b"\x00" * 32 + b"\xff\xd9"
PDF = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<>>\nendobj\n%%EOF\n"


# --- Ayudas ---------------------------------------------------------------------------------

def _membresia(cur, ws: str, nombre: str) -> str:
    cur.execute("""select m.id from membership m join app_user u on u.id = m.app_user_id
                    where m.workspace_id = %s and u.nombre = %s""", (ws, nombre))
    return str(cur.fetchone()["id"])


def _tarea(cur, ws: str, *, persona: str = "Mariano Naim", area: str = "electricidad",
           pide=("explicacion", "foto"), estado: str = "en_curso") -> str:
    """Una tarea con la política que pide `pide`, en curso (como la deja un inicio)."""
    cur.execute("""insert into objective (workspace_id, tipo, titulo)
                   values (%s, 'operativo', 'Objetivo de prueba') returning id""", (ws,))
    objetivo = cur.fetchone()["id"]
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, criterio_aceptacion,
                             evidencia_requerida)
           values (%s, %s, 'Armar el tablero', (select id from area
                                                 where workspace_id = %s and slug = %s),
                   %s, 'Tablero cerrado y probado', %s) returning id""",
        (ws, objetivo, ws, area, _membresia(cur, ws, persona), list(pide)))
    tarea = str(cur.fetchone()["id"])
    if estado == "bloqueada":
        cur.execute("insert into blocker (workspace_id, task_id, causa) values "
                    "(%s, %s, 'falta el repuesto')", (ws, tarea))
    cur.execute("""insert into task_state_event (task_id, estado_nuevo, actor_kind)
                   values (%s, %s, 'leda')""", (tarea, estado))
    return tarea


def _archivo(cur, ws: str, persona: str, contenido: bytes = JPEG, *,
             clase: str = "imagen") -> str:
    cur.execute(
        """insert into archivo (workspace_id, contenido, sha256, tamano, tipo, clase,
                                enviado_por_membership_id, recibido_en)
           values (%s, %s, %s, %s, 'image/jpeg', %s, %s, %s) returning id""",
        (ws, contenido, hashlib.sha256(contenido).hexdigest(), len(contenido), clase,
         persona, AHORA))
    return str(cur.fetchone()["id"])


def _pieza(cur, ws: str, tarea: str, *, clase: str = "texto", cubre=(),
           texto: str | None = "Quedó armado y probado", archivo: str | None = None,
           uri: str | None = None, por: str | None = None) -> str:
    cur.execute(
        """insert into evidence (workspace_id, task_id, tipo, clase, texto, uri, archivo_id,
                                 cubre, entregado_por)
           values (%s, %s, %s, %s, %s, %s, %s, %s, %s) returning id""",
        (ws, tarea, clase, clase, texto if clase == "texto" else None, uri, archivo,
         list(cubre), por))
    return str(cur.fetchone()["id"])


def _faltan(cur, tarea: str, piezas=None) -> list[str]:
    cur.execute("select tipos_de_evidencia_que_faltan(%s, %s) t",
                (tarea, Jsonb(piezas or [])))
    return list(cur.fetchone()["t"])


def _quien(cur, ws: str, nombre: str):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _cuantas(cur, tabla: str, donde: str = "true", *args) -> int:
    cur.execute(f"select count(*) n from {tabla} where {donde}", args)
    return cur.fetchone()["n"]


# --- Las tablas nuevas ----------------------------------------------------------------------

def test_las_tablas_nuevas_tienen_espacio_obligatorio_y_rls_forzado(conn):
    with admin(conn) as cur:
        for tabla in NUEVAS:
            cur.execute("""select relrowsecurity, relforcerowsecurity
                             from pg_class where oid = to_regclass(%s)""", (f"leda.{tabla}",))
            fila = cur.fetchone()
            assert fila is not None, f"{tabla} no existe"
            assert fila["relrowsecurity"] and fila["relforcerowsecurity"], tabla
            cur.execute("select polname from pg_policy where polrelid = to_regclass(%s)",
                        (f"leda.{tabla}",))
            assert [p["polname"] for p in cur.fetchall()] == ["aislamiento_espacio"], tabla
            cur.execute("""select is_nullable from information_schema.columns
                            where table_schema = 'leda' and table_name = %s
                              and column_name = 'workspace_id'""", (tabla,))
            assert cur.fetchone()["is_nullable"] == "NO", tabla


def test_las_funciones_de_la_evidencia_no_son_security_definer(conn):
    with admin(conn) as cur:
        cur.execute("""select proname, prosecdef from pg_proc p
                         join pg_namespace n on n.oid = p.pronamespace
                        where n.nspname = 'leda' and proname = any(%s)""",
                    (["tipos_de_evidencia_que_faltan", "tipos_que_acepta_la_clase",
                      "clases_de_un_tipo_de_evidencia", "evidencia_pendiente",
                      "tipos_de_evidencia_validos", "exigir_clase_de_la_evidencia",
                      "rechazar_cambios_de_evidencia"],))
        filas = {f["proname"]: f["prosecdef"] for f in cur.fetchall()}
    assert len(filas) == 7 and not any(filas.values()), filas


# --- La política por tipo -------------------------------------------------------------------

def test_una_frase_sola_no_cubre_una_foto(corework, conn):
    """Mecánica §6: no se acepta una afirmación cuando la política pide un artefacto. Aunque
    una pieza de texto diga que cubre la foto, un texto no es de una clase que la foto acepte."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws)
        assert _faltan(cur, tarea) == ["explicacion", "foto"]
        assert _faltan(cur, tarea, [{"clase": "texto", "cubre": ["explicacion", "foto"]}]) \
            == ["foto"]
        _pieza(cur, ws, tarea, cubre=["explicacion", "foto"])
        assert _faltan(cur, tarea) == ["foto"]
        cur.execute("select evidencia_pendiente(%s) p", (tarea,))
        assert cur.fetchone()["p"] is True


def test_una_imagen_sola_no_cubre_una_explicacion(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws)
        mariano = _membresia(cur, ws, "Mariano Naim")
        _pieza(cur, ws, tarea, clase="imagen", archivo=_archivo(cur, ws, mariano),
               cubre=["explicacion", "foto"])
        assert _faltan(cur, tarea) == ["explicacion"]
        _pieza(cur, ws, tarea, cubre=["explicacion"])
        assert _faltan(cur, tarea) == []
        cur.execute("select evidencia_pendiente(%s) p", (tarea,))
        assert cur.fetchone()["p"] is False


def test_un_texto_puede_cubrir_varios_tipos(corework, conn):
    """"Terminé, lo probé 20 ciclos sin falla" es explicación y resultado de la prueba (ADR
    0019, decisión 5): un texto cubre los tipos que dice, si todos aceptan texto."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws, persona="Lucas Natuche", area="it",
                       pide=("explicacion", "resultado_de_prueba"))
        _pieza(cur, ws, tarea, cubre=["explicacion", "resultado_de_prueba"])
        assert _faltan(cur, tarea) == []


def test_lo_retirado_y_lo_de_antes_de_un_pedido_de_cambios_no_cuentan(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws)
        mariano = _membresia(cur, ws, "Mariano Naim")
        _pieza(cur, ws, tarea, cubre=["explicacion"])
        foto = _pieza(cur, ws, tarea, clase="imagen", archivo=_archivo(cur, ws, mariano),
                      cubre=["foto"])
        assert _faltan(cur, tarea) == []
        cur.execute("""insert into evidencia_retirada (workspace_id, evidence_id,
                                                       retirada_por_membership_id)
                       values (%s, %s, %s)""", (ws, foto, mariano))
        assert _faltan(cur, tarea) == ["foto"]
        assert _cuantas(cur, "evidence", "task_id = %s", tarea) == 2     # nada se borró
        # Un pedido de cambios deja sin efecto el ciclo: lo de antes ya no cuenta.
        cur.execute("""insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                             aprobador_membership_id, decision)
                       values (%s, 'tarea', %s, %s, 'rechazado')""",
                    (ws, tarea, _membresia(cur, ws, "Ismael Soschinski")))
        assert _faltan(cur, tarea) == ["explicacion", "foto"]


def test_aprobar_sigue_exigiendo_la_politica_completa(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws, estado="en_revision")
        _pieza(cur, ws, tarea, cubre=["explicacion", "foto"])
        cur.execute("""insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                             aprobador_membership_id, decision)
                       values (%s, 'tarea', %s, %s, 'aprobado')""",
                    (ws, tarea, _membresia(cur, ws, "Ismael Soschinski")))
        cur.execute("select motivo_no_cierra_tarea(%s) m", (tarea,))
        assert cur.fetchone()["m"] == "Falta la evidencia requerida."
    conn.commit()
    with espacio(conn, ws) as cur:
        ismael = _quien(cur, ws, "Ismael Soschinski")
        with pytest.raises(Denegado):
            H.ejecutar(cur, ismael, "aprobar_tarea", {"tarea_id": tarea}, ya_confirmada=True)


def test_un_tipo_sin_clases_declaradas_no_lo_cubre_nada(corework, conn):
    """Falla cerrado: un tipo que la política pide y el pack no declaró no lo cubre ninguna
    pieza (ADR 0019, decisión 5; constitución §4)."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws, pide=("explicacion", "plano_firmado"))
        _pieza(cur, ws, tarea, cubre=["explicacion", "plano_firmado"])
        assert _faltan(cur, tarea) == ["plano_firmado"]


def test_el_pack_declara_las_clases_de_cada_tipo_que_pide():
    base = {"roles": [{"slug": "d", "autoridad_final": True}],
            "personas": [{"id": "a", "nombre": "A", "area": "x", "rol": "d",
                          "aprobado_por": None}],
            "areas": [{"slug": "x"}], "calendario": {"dias": ["lunes"]},
            "telegram": {"grupo_gestion_id": 1}}
    sin_tipos = {**base, "evidencia": {"por_area": {"x": ["foto"]}}}
    bloqueantes, _ = validar(sin_tipos)
    assert any("'foto'" in b and "clases" in b for b in bloqueantes)
    mala = {**base, "evidencia": {"por_area": {"x": ["foto"]},
                                  "tipos": {"foto": {"clases": ["video"],
                                                     "en_palabras": "una foto"}}}}
    assert any("clase que no existe" in b for b in validar(mala)[0])
    buena = {**base, "evidencia": {"por_area": {"x": ["foto"]},
                                   "tipos": {"foto": {"clases": ["imagen"],
                                                      "en_palabras": "una foto"}}}}
    assert not any("evidencia" in b for b in validar(buena)[0])


def test_el_pack_de_corework_queda_con_las_clases_de_cada_tipo(corework, conn):
    with admin(conn) as cur:
        cur.execute("""select a.slug, p.tipos from task_evidence_policy p
                         join area a on a.id = p.area_id where p.workspace_id = %s""",
                    (corework.workspace_id,))
        tipos = {f["slug"]: f["tipos"] for f in cur.fetchall()}
    assert tipos["electricidad"]["foto"]["clases"] == ["imagen"]
    assert tipos["ot"]["archivo"]["clases"] == ["archivo", "imagen", "enlace"]
    assert set(tipos["ot"]) == {"explicacion", "resultado_de_prueba", "captura", "archivo"}


def test_la_base_rechaza_unas_clases_que_no_existen(corework, conn):
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            cur.execute("""update task_evidence_policy
                              set tipos = '{"foto": {"clases": ["video"],
                                                     "en_palabras": "una foto"}}'
                            where workspace_id = %s""", (corework.workspace_id,))


# --- La clase la fija el código por el contenido ---------------------------------------------

def test_una_pieza_imagen_apunta_a_una_imagen_y_un_texto_a_ningun_archivo(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws)
        mariano = _membresia(cur, ws, "Mariano Naim")
        pdf = _archivo(cur, ws, mariano, PDF, clase="pdf")
        foto = _archivo(cur, ws, mariano)
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            _pieza(cur, ws, tarea, clase="imagen", archivo=pdf, cubre=["foto"])
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            _pieza(cur, ws, tarea, clase="archivo", archivo=foto)
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            _pieza(cur, ws, tarea, clase="texto", archivo=foto)
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            _pieza(cur, ws, tarea, clase="imagen")
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            _pieza(cur, ws, tarea, clase="video", archivo=foto)
        _pieza(cur, ws, tarea, clase="archivo", archivo=pdf)
        _pieza(cur, ws, tarea, clase="enlace", uri="https://ejemplo.com/video")


def test_la_cocina_fija_la_clase_por_el_contenido_y_no_por_lo_que_le_dicen(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws)
        mariano = _membresia(cur, ws, "Mariano Naim")
        foto = _archivo(cur, ws, mariano)
    conn.commit()
    with espacio(conn, ws) as cur:
        quien = _quien(cur, ws, "Mariano Naim")
        r = H.ejecutar(cur, quien, "entregar_tarea", {"tarea_id": tarea, "piezas": [
            {"texto": "https://ejemplo.com/tablero", "clase": "texto", "cubre": ["explicacion"]},
            {"archivo_id": foto, "clase": "archivo", "cubre": ["foto"]},
            {"texto": "Quedó cerrado y probado", "cubre": ["explicacion", "foto"]}]},
            ya_confirmada=True)
    assert r["estado"] == "en_revision"
    with admin(conn) as cur:
        cur.execute("""select clase, cubre from evidence where task_id = %s order by at""",
                    (tarea,))
        assert [(f["clase"], f["cubre"]) for f in cur.fetchall()] == [
            ("enlace", []), ("imagen", ["foto"]), ("texto", ["explicacion"])]


# --- Inmutabilidad --------------------------------------------------------------------------

def test_leda_app_solo_agrega_y_lee_la_evidencia(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws)
        mariano = _membresia(cur, ws, "Mariano Naim")
        pieza = _pieza(cur, ws, tarea, cubre=["explicacion"], por=mariano)
        cur.execute("""insert into evidencia_retirada (workspace_id, evidence_id,
                                                       retirada_por_membership_id)
                       values (%s, %s, %s)""", (ws, pieza, mariano))
        cur.execute("""insert into archivo_de_tarea (workspace_id, archivo_id, task_id,
                                                     dicho_por_membership_id, at)
                       values (%s, %s, %s, %s, %s)""",
                    (ws, _archivo(cur, ws, mariano), tarea, mariano, AHORA))
    conn.commit()
    with espacio(conn, ws) as cur:
        for tabla in ("evidence",) + NUEVAS:
            assert _cuantas(cur, tabla) == 1, tabla
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                cur.execute(f"update {tabla} set workspace_id = workspace_id")
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                cur.execute(f"delete from {tabla}")


def test_una_evidencia_y_un_retiro_no_se_modifican_ni_con_la_administracion(corework, conn):
    """ADR 0019, decisión 3: un disparador, como garantía aparte de los privilegios."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws)
        mariano = _membresia(cur, ws, "Mariano Naim")
        pieza = _pieza(cur, ws, tarea, cubre=["explicacion"], por=mariano)
        cur.execute("""insert into evidencia_retirada (workspace_id, evidence_id,
                                                       retirada_por_membership_id)
                       values (%s, %s, %s)""", (ws, pieza, mariano))
        for sql in ("update evidence set texto = 'otro'", "delete from evidence",
                    "update evidencia_retirada set motivo = 'otro'",
                    "delete from evidencia_retirada"):
            with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
                cur.execute(sql)
        assert _cuantas(cur, "evidence") == 1 and _cuantas(cur, "evidencia_retirada") == 1


def test_el_rollback_de_la_0034_se_niega_con_una_evidencia_de_texto(corework, conn):
    """El rollback borra la columna `texto`: con una entrega escrita, deshacerlo perdería lo que
    la persona entregó sin avisar. Se ejercita la guarda tal como está escrita en el archivo."""
    script = (Path(__file__).resolve().parents[2] / "db" / "rollbacks"
              / "0034_evidencia_de_la_entrega.sql").read_text("utf-8")
    guarda = re.search(r"do \$\$.*?end \$\$;", script, re.S).group(0)
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws)
        _pieza(cur, ws, tarea, cubre=["explicacion"])
        with pytest.raises(psycopg.errors.RaiseException, match="0034 rollback refused"), \
                conn.transaction():
            cur.execute("set local search_path = leda, public")
            cur.execute(guarda)
        assert _cuantas(cur, "evidence") == 1


# --- Aislamiento ----------------------------------------------------------------------------

def test_una_pieza_no_apunta_a_nada_de_otro_espacio(corework, conn, intake_world):
    ws = corework.workspace_id
    otro = intake_world["north-lab"]
    with admin(conn) as cur:
        tarea = _tarea(cur, ws)
        mariano = _membresia(cur, ws, "Mariano Naim")
        ajeno = _archivo(cur, otro["id"], otro["people"]["Sam North"]["membership_id"])
        cur.execute("""insert into task (workspace_id, objective_id, titulo, area_id,
                                         responsable_membership_id)
                       values (%s, %s, 'Ajena', %s, %s) returning id""",
                    (otro["id"], otro["objectives"][0], otro["areas"]["field"],
                     otro["people"]["Sam North"]["membership_id"]))
        tarea_ajena = str(cur.fetchone()["id"])
        pieza_ajena = _pieza(cur, otro["id"], tarea_ajena)
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            _pieza(cur, ws, tarea, clase="imagen", archivo=ajeno, cubre=["foto"])
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            _pieza(cur, ws, tarea_ajena)
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            _pieza(cur, ws, tarea, por=otro["people"]["Sam North"]["membership_id"])
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            cur.execute("""insert into evidencia_retirada (workspace_id, evidence_id,
                                                           retirada_por_membership_id)
                           values (%s, %s, %s)""", (ws, pieza_ajena, mariano))
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            cur.execute("""insert into archivo_de_tarea (workspace_id, archivo_id, task_id,
                                                         dicho_por_membership_id, at)
                           values (%s, %s, %s, %s, %s)""", (ws, ajeno, tarea, mariano, AHORA))
    conn.commit()
    with espacio(conn, ws) as cur:
        assert _cuantas(cur, "evidence") == 0


# --- La cocina: entregar y retirar ----------------------------------------------------------

def test_entregar_sin_la_politica_completa_no_escribe_nada(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws)
    conn.commit()
    with espacio(conn, ws) as cur:
        quien = _quien(cur, ws, "Mariano Naim")
        r = H.ejecutar(cur, quien, "entregar_tarea", {"tarea_id": tarea, "piezas": [
            {"texto": "Terminé el tablero, quedó cerrado", "cubre": ["explicacion", "foto"]}]},
            ya_confirmada=True)
    assert r["en_revision"] is False and r["faltan"] == ["foto"]
    with admin(conn) as cur:
        assert _cuantas(cur, "evidence") == 0
        cur.execute("select estado from task where id = %s", (tarea,))
        assert cur.fetchone()["estado"] == "en_curso"


def test_entregar_escribe_las_piezas_y_pasa_a_revision_en_un_solo_acto(corework, conn):
    """Nunca `terminada` (constitución §11), y quien aprueba se entera (ADR 0009)."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws)
        foto = _archivo(cur, ws, _membresia(cur, ws, "Mariano Naim"))
    conn.commit()
    with espacio(conn, ws) as cur:
        quien = _quien(cur, ws, "Mariano Naim")
        r = H.ejecutar(cur, quien, "entregar_tarea", {"tarea_id": tarea, "piezas": [
            {"texto": "Quedó cerrado y probado", "cubre": ["explicacion"]},
            {"archivo_id": foto, "cubre": ["foto"]}]}, ya_confirmada=True)
    assert r["estado"] == "en_revision" and len(r["evidencias"]) == 2
    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tarea,))
        assert cur.fetchone()["estado"] == "en_revision"
        cur.execute("""select estado_anterior, estado_nuevo from task_state_event
                        where task_id = %s order by at desc limit 1""", (tarea,))
        assert dict(cur.fetchone()) == {"estado_anterior": "en_curso",
                                        "estado_nuevo": "en_revision"}
        assert _cuantas(cur, "audit_log", "accion = 'herramienta:entregar_tarea'") == 1
        cur.execute("""select cuerpo from message_outbox o join app_user u
                         on u.telegram_user_id = o.chat_id
                        where u.nombre = 'Ismael Soschinski'""")
        assert "Armar el tablero" in cur.fetchone()["cuerpo"]


@pytest.mark.parametrize("estado", ["asignada", "bloqueada", "en_revision"])
def test_entregar_solo_desde_en_curso(corework, conn, estado):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws, pide=("explicacion",), estado=estado)
    conn.commit()
    with espacio(conn, ws) as cur:
        quien = _quien(cur, ws, "Mariano Naim")
        r = H.ejecutar(cur, quien, "entregar_tarea", {"tarea_id": tarea, "piezas": [
            {"texto": "Listo", "cubre": ["explicacion"]}]}, ya_confirmada=True)
    assert r["en_revision"] is False
    with admin(conn) as cur:
        assert _cuantas(cur, "evidence") == 0


def test_solo_el_responsable_entrega(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws, pide=("explicacion",))
    conn.commit()
    with espacio(conn, ws) as cur:
        otro = _quien(cur, ws, "Marcos Tarquini")
        with pytest.raises(Denegado):
            H.ejecutar(cur, otro, "entregar_tarea", {"tarea_id": tarea, "piezas": [
                {"texto": "Listo", "cubre": ["explicacion"]}]}, ya_confirmada=True)


def test_retirar_agrega_un_retiro_y_lo_hace_solo_quien_la_entrego(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws, estado="en_revision")
        mariano = _membresia(cur, ws, "Mariano Naim")
        foto = _pieza(cur, ws, tarea, clase="imagen", archivo=_archivo(cur, ws, mariano),
                      cubre=["foto"], por=mariano)
        _pieza(cur, ws, tarea, cubre=["explicacion"], por=mariano)
    conn.commit()
    with espacio(conn, ws) as cur:
        ismael = _quien(cur, ws, "Ismael Soschinski")
        with pytest.raises(Denegado):
            H.ejecutar(cur, ismael, "retirar_evidencia", {"evidencia_id": foto},
                       ya_confirmada=True)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, ws, "Mariano Naim")
        r = H.ejecutar(cur, quien, "retirar_evidencia",
                       {"evidencia_id": foto, "motivo": "no era esa foto"}, ya_confirmada=True)
        assert r == {"retirada": True, "tarea_id": tarea, "faltan": ["foto"]}
        otra_vez = H.ejecutar(cur, quien, "retirar_evidencia", {"evidencia_id": foto},
                              ya_confirmada=True)
        assert otra_vez["retirada"] is False
    with admin(conn) as cur:
        assert _cuantas(cur, "evidence", "task_id = %s", tarea) == 2
        assert _cuantas(cur, "evidencia_retirada") == 1


def test_no_se_retira_una_evidencia_de_una_tarea_aprobada(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws, estado="en_revision")
        mariano = _membresia(cur, ws, "Mariano Naim")
        foto = _pieza(cur, ws, tarea, clase="imagen", archivo=_archivo(cur, ws, mariano),
                      cubre=["foto"], por=mariano)
        cur.execute("""insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                             aprobador_membership_id, decision)
                       values (%s, 'tarea', %s, %s, 'aprobado')""",
                    (ws, tarea, _membresia(cur, ws, "Ismael Soschinski")))
    conn.commit()
    with espacio(conn, ws) as cur:
        quien = _quien(cur, ws, "Mariano Naim")
        r = H.ejecutar(cur, quien, "retirar_evidencia", {"evidencia_id": foto},
                       ya_confirmada=True)
    assert r["retirada"] is False
    with admin(conn) as cur:
        assert _cuantas(cur, "evidencia_retirada") == 0
