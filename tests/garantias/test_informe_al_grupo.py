"""El informe al grupo, en la capa de garantías (C-6, decisión 25; migración 0048).

Un aviso del motor va a una persona o al grupo del espacio, nunca a los dos ni a nadie; el que va al
grupo no guarda el chat (`docs/architecture/frontera.md`): el identificador sale de la configuración
del espacio (`workspace.grupo_chat_id`, del pack) al encolarlo en el outbox. El aislamiento entre
espacios (constitución §13) rige igual: el informe de un espacio va a su grupo, con sus tareas, y
nunca al de otro ni con las de otro.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg
import pytest

from leda.db import admin, espacio
from leda.motor.avisos import enviar_avisos
from leda.motor.escalera import correr_escalera
from leda.motor.informe_al_grupo import INFORME_AL_GRUPO
from leda.motor.tiempo import RelojFijo

# Un viernes a las 16:15 en Buenos Aires (19:15 UTC) es también las 21:15 en Madrid: dentro del
# horario de los dos espacios (08:00 a 18:00) sólo para el primero. Cada espacio tiene su cadencia
# a una hora suya.
VIERNES = datetime(2026, 10, 9, 19, 15, tzinfo=timezone.utc)
GRUPOS = {"north-lab": -100_701, "west-studio": -100_702}


class IAQueRedacta:
    nombre = "guionada"

    def __init__(self) -> None:
        self.pedidos: list[dict] = []

    def redactar(self, pedido):
        self.pedidos.append(pedido)
        return f"Informe {len(self.pedidos)}."


@pytest.fixture
def con_informe(conn, intake_world) -> dict[str, dict]:
    """Cada espacio con su grupo, su cadencia al grupo y una tarea en curso de Sam North."""
    tareas = {}
    with admin(conn) as cur:
        for slug, w in intake_world.items():
            cur.execute("update workspace set grupo_chat_id = %s where id = %s",
                        (GRUPOS[slug], w["id"]))
            cur.execute("""insert into cadence_job (workspace_id, nombre, cron, audiencia,
                                                    plantilla_clave)
                           values (%s, 'informe_semanal', %s, 'grupo', 'informe_semanal')""",
                        (w["id"], "15 16 * * 5" if slug == "north-lab" else "0 10 * * 5"))
            cur.execute(
                """insert into task (workspace_id, objective_id, titulo, area_id,
                                     responsable_membership_id, estado, fecha_objetivo)
                   values (%s, %s, %s, %s, %s, 'asignada', %s) returning id""",
                (w["id"], w["objectives"][0], f"Tarea de {slug}", w["areas"]["field"],
                 w["people"]["Sam North"]["membership_id"], VIERNES + timedelta(days=14)))
            tareas[slug] = str(cur.fetchone()["id"])
    conn.commit()
    return tareas


def _ciclo(conn, workspace_id: str, at: datetime, ia) -> None:
    correr_escalera(conn, workspace_id, RelojFijo(at))
    conn.commit()
    enviar_avisos(conn, workspace_id, ia, RelojFijo(at))
    conn.commit()


def test_el_informe_de_un_espacio_va_a_su_grupo_con_sus_tareas(conn, intake_world, con_informe):
    norte, oeste = intake_world["north-lab"], intake_world["west-studio"]
    ia = IAQueRedacta()

    _ciclo(conn, norte["id"], VIERNES, ia)

    [pedido] = ia.pedidos
    [hechos] = pedido["hechos"]
    assert [r["tarea"] for r in hechos["siguen"]] == ["Tarea de north-lab"]
    assert {r["la_tiene"] for r in hechos["siguen"]} == {norte["people"]["Sam North"]["name"]}
    with admin(conn) as cur:
        cur.execute("""select workspace_id, chat_id from message_outbox
                        where chat_id = any(%s)""", (list(GRUPOS.values()),))
        filas = cur.fetchall()
    assert [(str(f["workspace_id"]), f["chat_id"]) for f in filas] == [
        (norte["id"], GRUPOS["north-lab"])]

    # El otro espacio, a su hora (el viernes a las 10:00 de Madrid): a su grupo, con lo suyo.
    _ciclo(conn, oeste["id"], datetime(2026, 10, 9, 8, 0, tzinfo=timezone.utc), ia)
    _, otro = ia.pedidos
    assert [r["tarea"] for r in otro["hechos"][0]["siguen"]] == ["Tarea de west-studio"]
    with admin(conn) as cur:
        cur.execute("""select chat_id from message_outbox where workspace_id = %s
                        and chat_id = any(%s)""", (oeste["id"], list(GRUPOS.values())))
        assert [f["chat_id"] for f in cur.fetchall()] == [GRUPOS["west-studio"]]


def test_un_espacio_no_ve_el_informe_del_otro(conn, intake_world, con_informe):
    norte, oeste = intake_world["north-lab"], intake_world["west-studio"]
    _ciclo(conn, norte["id"], VIERNES, IAQueRedacta())
    with espacio(conn, oeste["id"]) as cur:
        cur.execute("select count(*) n from scheduled_notice where tipo = %s",
                    (INFORME_AL_GRUPO,))
        assert cur.fetchone()["n"] == 0
    with espacio(conn, norte["id"]) as cur:
        cur.execute("select count(*) n from scheduled_notice where tipo = %s",
                    (INFORME_AL_GRUPO,))
        assert cur.fetchone()["n"] == 1
    conn.commit()


def test_un_aviso_va_a_una_persona_o_al_grupo_nunca_a_los_dos_ni_a_nadie(conn, intake_world):
    w = intake_world["north-lab"]
    persona = w["people"]["Sam North"]["membership_id"]
    with admin(conn) as cur:
        for i, (al_grupo, destinatario) in enumerate(((True, persona), (False, None))):
            with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
                cur.execute(
                    """insert into scheduled_notice (workspace_id, tipo, destinatario_membership_id,
                                                     al_grupo, hechos, programado_para,
                                                     dedupe_key, creado_en)
                       values (%s, 'prueba', %s, %s, '{}', now(), %s, now())""",
                    (w["id"], destinatario, al_grupo, f"prueba:{i}"))
        cur.execute(
            """insert into scheduled_notice (workspace_id, tipo, destinatario_membership_id,
                                             al_grupo, hechos, programado_para, dedupe_key,
                                             creado_en)
               values (%s, 'prueba', null, true, '{}', now(), 'prueba:grupo', now())""",
            (w["id"],))
    conn.rollback()


def test_el_aviso_al_grupo_no_guarda_el_chat(conn):
    """Frontera (regla 2): el núcleo no conoce el `chat_id`; el del grupo sale del espacio al
    encolar en el outbox."""
    with admin(conn) as cur:
        cur.execute("""select column_name from information_schema.columns
                        where table_schema = 'leda' and table_name = 'scheduled_notice'""")
        columnas = {f["column_name"] for f in cur.fetchall()}
    conn.commit()
    assert "al_grupo" in columnas
    assert not {c for c in columnas if "chat" in c}


def test_el_rollback_de_la_0048_se_niega_con_un_aviso_al_grupo(conn, intake_world):
    """Deshacerla volvería obligatorio el destinatario: con un aviso al grupo guardado, perdería
    ese aviso sin avisar. Se ejercita la guarda tal como está escrita en el archivo."""
    script = (Path(__file__).resolve().parents[2] / "db" / "rollbacks"
              / "0048_aviso_al_grupo.sql").read_text("utf-8")
    guarda = re.search(r"do \$\$.*?end \$\$;", script, re.S).group(0)
    w = intake_world["north-lab"]
    with admin(conn) as cur:
        cur.execute(
            """insert into scheduled_notice (workspace_id, tipo, destinatario_membership_id,
                                             al_grupo, hechos, programado_para, dedupe_key,
                                             creado_en)
               values (%s, 'informe_al_grupo', null, true, '{}', now(), 'prueba:grupo', now())""",
            (w["id"],))
        with pytest.raises(psycopg.errors.RaiseException, match="0048 rollback refused"), \
                conn.transaction():
            cur.execute("set local search_path = leda, public")
            cur.execute(guarda)
    conn.rollback()
