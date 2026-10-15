"""J7-2: el pack sólo arma un equipo vacío.

Desde la J7 la web gobierna el equipo (usuario, 2026-10-15, J7 punto 1): el archivo del espacio es
una plantilla para arrancar cuando el espacio todavía no tiene gente. En un espacio con gente, volver
a importar el pack aplica el calendario, las cadencias y lo demás, pero no toca las áreas, los roles,
las personas, quién aprueba a quién, los referentes, la política de aprobación ni las rutas de
escalamiento; y lo dice, en el resultado y en la auditoría.
"""

from __future__ import annotations

import os

import yaml

from leda.db import admin
from leda.importador import importar
from tests.conftest import RAIZ

AVISO = "El equipo ya existe"


def _pack() -> dict:
    pack = yaml.safe_load((RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    pack["telegram"]["grupo_gestion_id"] = -1001
    for i, p in enumerate(pack["personas"]):
        p["telegram_user_id"] = 9000 + i
    pack["evidencia"]["estructura_drive"] = "drive://corework"
    return pack


def _escribir(tmp_path, pack: dict, nombre: str = "corework.yaml"):
    ruta = tmp_path / nombre
    ruta.write_text(yaml.safe_dump(pack, allow_unicode=True), "utf-8")
    return ruta


def _equipo(conn, ws: str) -> dict[str, list]:
    """Una foto de todo lo que es del equipo, para comparar antes y después."""
    consultas = {
        "area": """select slug, nombre, referente_membership_id, archivada_en from area
                    where workspace_id = %s order by slug""",
        "rol": """select slug, nombre, autoridad_final from rol
                   where workspace_id = %s order by slug""",
        "membership": """select m.id, m.app_user_id, m.area_id, m.rol_id, m.aprobador_membership_id,
                                u.nombre, u.telegram_user_id
                           from membership m join app_user u on u.id = m.app_user_id
                          where m.workspace_id = %s order by u.nombre""",
        "approval_policy": """select id, sujeto, area_id, autoaprobacion_declarada, motivo
                                from approval_policy where workspace_id = %s order by id""",
        "approval_requirement": """select r.* from approval_requirement r
                                     join approval_policy p on p.id = r.approval_policy_id
                                    where p.workspace_id = %s order by r.id""",
        "escalation_route": """select * from escalation_route where workspace_id = %s
                                order by orden""",
    }
    foto = {}
    with admin(conn) as cur:
        for tabla, sql in consultas.items():
            cur.execute(sql, (ws,))
            foto[tabla] = cur.fetchall()
    return foto


def _detalle_de_la_importacion(conn, ws: str, version: int) -> dict:
    with admin(conn) as cur:
        cur.execute(
            """select detalle from audit_log
                where workspace_id = %s and accion = 'importar_pack'
                  and (detalle->>'version')::int = %s""", (ws, version))
        return cur.fetchone()["detalle"]


def test_un_espacio_vacio_se_arma_con_el_equipo_del_pack(conn, tmp_path):
    os.environ["LEDA_BOT_TOKEN_COREWORK"] = "prueba:token"
    r = importar(conn, _escribir(tmp_path, _pack()), activar=True)
    conn.commit()

    foto = _equipo(conn, r.workspace_id)
    assert len(foto["membership"]) == 7
    assert len(foto["area"]) == 6
    assert sum(1 for a in foto["area"] if a["referente_membership_id"]) == 5
    assert sum(1 for m in foto["membership"] if m["aprobador_membership_id"]) == 6
    assert foto["approval_policy"] and foto["escalation_route"]
    assert not any(AVISO in a for a in r.advertencias)
    detalle = _detalle_de_la_importacion(conn, r.workspace_id, r.version)
    assert detalle["equipo_del_pack"] == "aplicado"


def test_reimportar_no_pisa_el_equipo_y_aplica_lo_demas(conn, tmp_path):
    os.environ["LEDA_BOT_TOKEN_COREWORK"] = "prueba:token"
    pack = _pack()
    r = importar(conn, _escribir(tmp_path, pack), activar=True)
    conn.commit()
    ws = r.workspace_id

    # Dirección cambia el equipo (lo que mañana hará desde la web): Nahuel pasa a referente de OT y
    # lo aprueba Ismael, Lucas pasa a ser aprobado por Marcos, IT se llama "Sistemas" y entra Paula.
    with admin(conn) as cur:
        cur.execute(
            """select m.id, u.nombre from membership m join app_user u on u.id = m.app_user_id
                where m.workspace_id = %s""", (ws,))
        por_nombre = {f["nombre"].split()[0]: f["id"] for f in cur.fetchall()}
        cur.execute(
            "update area set referente_membership_id = %s where workspace_id = %s and slug = 'ot'",
            (por_nombre["Nahuel"], ws))
        cur.execute("update membership set aprobador_membership_id = %s where id = %s",
                    (por_nombre["Ismael"], por_nombre["Nahuel"]))
        cur.execute("update membership set aprobador_membership_id = %s where id = %s",
                    (por_nombre["Marcos"], por_nombre["Lucas"]))
        cur.execute("update area set nombre = 'Sistemas' where workspace_id = %s and slug = 'it'",
                    (ws,))
        cur.execute("insert into app_user (nombre) values ('Paula Ríos') returning id")
        paula = cur.fetchone()["id"]
        cur.execute(
            """insert into membership
                 (workspace_id, app_user_id, nombre, area_id, rol_id, aprobador_membership_id)
               select %s, %s, 'Paula Ríos', a.id, r.id, %s from area a, rol r
                where a.workspace_id = %s and a.slug = 'it'
                  and r.workspace_id = %s and r.slug = 'integrante'""",
            (ws, paula, por_nombre["Martín"], ws, ws))
    conn.commit()
    antes = _equipo(conn, ws)

    # El pack vuelve a importarse con cambios de configuración y también de equipo.
    pack["calendario"]["horario"] = "08:00-16:00"
    pack["cadencia"][0]["cuando"] = "lunes 10:00"
    pack["glosario"].append({"termino": "tablero nuevo", "definicion": "una prueba"})
    pack["areas"][2]["nombre"] = "IT del archivo"
    pack["personas"] = [p for p in pack["personas"] if p["id"] != "nahuel"]
    pack["personas"][0]["telegram_user_id"] = 1234567
    pack["escalamiento"] = pack["escalamiento"][:1]
    pack["aprobacion"]["reglas"] = pack["aprobacion"]["reglas"][:1]
    r2 = importar(conn, _escribir(tmp_path, pack, "otra.yaml"), activar=True)
    conn.commit()

    assert _equipo(conn, ws) == antes
    assert any(AVISO in a for a in r2.advertencias)
    detalle = _detalle_de_la_importacion(conn, ws, r2.version)
    assert detalle["equipo_del_pack"] == "no_aplicado"
    assert any(AVISO in a for a in detalle["advertencias"])

    with admin(conn) as cur:
        cur.execute("select hora_inicio, hora_fin from work_calendar where workspace_id = %s",
                    (ws,))
        cal = cur.fetchone()
        assert (str(cal["hora_inicio"]), str(cal["hora_fin"])) == ("08:00:00", "16:00:00")
        cur.execute(
            "select cron from cadence_job where workspace_id = %s and nombre = 'objetivos_semanales'",
            (ws,))
        assert cur.fetchone()["cron"] == "0 10 * * 1"
        cur.execute(
            "select 1 from glossary_term where workspace_id = %s and termino = 'tablero nuevo'",
            (ws,))
        assert cur.fetchone()
        cur.execute("select count(*) n from app_user where telegram_user_id = 1234567")
        assert cur.fetchone()["n"] == 0


def test_reimportar_no_borra_la_evidencia_de_un_area_creada_en_la_web(conn, tmp_path):
    """J7-4: un área creada en la web no está en el archivo; volver a importarlo no le borra su
    evidencia (sin ella, sus tareas no se podrían cargar), y las áreas del archivo la reciben."""
    os.environ["LEDA_BOT_TOKEN_COREWORK"] = "prueba:token"
    pack = _pack()
    r = importar(conn, _escribir(tmp_path, pack), activar=True)
    conn.commit()
    ws = r.workspace_id
    with admin(conn) as cur:
        cur.execute("""insert into area (workspace_id, slug, nombre)
                       values (%s, 'compras', 'Compras') returning id""", (ws,))
        compras = cur.fetchone()["id"]
        cur.execute("""insert into task_evidence_policy (workspace_id, area_id, evidencia_requerida)
                       values (%s, %s, array['explicacion'])""", (ws, compras))
    conn.commit()

    pack["evidencia"]["por_area"]["it"] = ["explicacion"]
    importar(conn, _escribir(tmp_path, pack, "otra.yaml"), activar=True)
    conn.commit()

    with admin(conn) as cur:
        cur.execute("select evidencia_requerida from task_evidence_policy where area_id = %s",
                    (compras,))
        assert cur.fetchone()["evidencia_requerida"] == ["explicacion"]
        cur.execute(
            """select p.evidencia_requerida from task_evidence_policy p
                 join area a on a.id = p.area_id
                where a.workspace_id = %s and a.slug = 'it'""", (ws,))
        assert cur.fetchone()["evidencia_requerida"] == ["explicacion"]
    conn.commit()
