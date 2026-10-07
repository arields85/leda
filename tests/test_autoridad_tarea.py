"""T2b (`leda-orienta`): autoridad sobre tareas ajenas.

Hallazgo del orquestador, evidencia de la sesión real por Telegram del
2026-09-25: sin un chequeo explícito, `actualizar_estado`, `registrar_bloqueo`
y `adjuntar_evidencia` estaban permitidas a CUALQUIER integrante autenticado
del espacio, sobre CUALQUIER tarea -- un integrante podía mover el estado de
la tarea de otra persona, declararle un bloqueo o adjuntarle evidencia. En la
sesión real, sólo la reticencia del modelo evitó hacerlo ("Ese no es tuyo");
no había nada en el servidor que lo impidiera. El menú de tarea (T2), que sólo
ofrecía estos botones a quien correspondía, se retiró con los flujos A y B (E3-3):
el filtro que vale es el de las herramientas.

Decisiones (citas de `nucleo/`):

- `actualizar_estado` / `registrar_bloqueo`: sólo el responsable de la
  tarea. `nucleo/constitucion.md` §3: "la persona responsable informa
  hechos como inicio, bloqueo, resolución y entrega en lenguaje natural";
  los referentes "aceptan las tareas... y luego aprueban o rechazan el
  trabajo entregado. No persiguen avances ni administran estados
  intermedios" -- por eso el aprobador NO se suma acá, a diferencia de lo
  que el enunciado dejaba abierto a decidir ("back from review"):
  `mecánica-pm.md` §3 tampoco describe ninguna transición de vuelta desde
  `en_revision` que no sea `aprobar_tarea` (ya con su propio chequeo de
  autoridad) o el `motivo_no_cierra_tarea`/impedimento de negocio, que no
  necesita autoridad ampliada.
- `adjuntar_evidencia`: responsable O aprobador. `nucleo/mecanica-pm.md` §6
  lista "confirmación del referente" entre la evidencia que Leda
  solicita -- el aprobador de la tarea (`puede_aprobar_tarea`, un solo
  nivel: a un integrante lo aprueba su referente) también puede adjuntarla.
"""

from __future__ import annotations


import pytest

from leda import herramientas as H
from leda.autoridad import Canal, Denegado, identificar
from leda.db import admin, espacio


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _tarea(cur, ws, *, titulo="Programar HMI línea 2", area="ot",
          persona="Nahuel Gimenez", estado="asignada"):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', 'Objetivo de prueba') returning id""", (ws,))
    obj = cur.fetchone()["id"]
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, criterio_aceptacion,
                             evidencia_requerida)
           values (%s, %s, %s,
                   (select id from area where workspace_id = %s and slug = %s),
                   (select m.id from membership m join app_user u on u.id = m.app_user_id
                     where m.workspace_id = %s and u.nombre = %s),
                    'Criterio de prueba', array['explicacion'])
           returning id""",
        (ws, obj, titulo, ws, area, ws, persona))
    t = cur.fetchone()["id"]
    cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                "values (%s, %s, 'leda')", (t, estado))
    return str(t)


# ---------------------------------------------------------------------------
# actualizar_estado -- sólo el responsable
# ---------------------------------------------------------------------------

def test_actualizar_estado_ajeno_se_rechaza(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)   # responsable: Nahuel Gimenez
    conn.commit()

    with espacio(conn, ws) as cur:
        ajeno = _quien(cur, "Ariel De Simone", ws)
        with pytest.raises(Denegado):
            H.ejecutar(cur, ajeno, "actualizar_estado",
                      {"tarea_id": tid, "estado": "en_curso"}, ya_confirmada=True)
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"


def test_actualizar_estado_del_aprobador_tambien_se_rechaza(corework, conn):
    """Constitución §3: el referente aprueba o rechaza el trabajo entregado,
    no administra estados intermedios -- aunque sea quien revisa a Nahuel."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)   # aprobador de Nahuel
        with pytest.raises(Denegado):
            H.ejecutar(cur, marcos, "actualizar_estado",
                      {"tarea_id": tid, "estado": "en_curso"}, ya_confirmada=True)


def test_actualizar_estado_lo_puede_el_responsable(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        r = H.ejecutar(cur, quien, "actualizar_estado",
                       {"tarea_id": tid, "estado": "en_curso"}, ya_confirmada=True)
        assert r == {"estado": "en_curso"}


# ---------------------------------------------------------------------------
# registrar_bloqueo -- sólo el responsable
# ---------------------------------------------------------------------------

def test_registrar_bloqueo_ajeno_se_rechaza(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()

    with espacio(conn, ws) as cur:
        ajeno = _quien(cur, "Ariel De Simone", ws)
        with pytest.raises(Denegado):
            H.ejecutar(cur, ajeno, "registrar_bloqueo",
                      {"tarea_id": tid, "causa": "algo"}, ya_confirmada=True)
        cur.execute("select count(*) n from blocker where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 0


def test_registrar_bloqueo_del_aprobador_tambien_se_rechaza(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        with pytest.raises(Denegado):
            H.ejecutar(cur, marcos, "registrar_bloqueo",
                      {"tarea_id": tid, "causa": "algo"}, ya_confirmada=True)


def test_registrar_bloqueo_lo_puede_el_responsable(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        r = H.ejecutar(cur, quien, "registrar_bloqueo",
                       {"tarea_id": tid, "causa": "algo"}, ya_confirmada=True)
        assert "bloqueo_id" in r


# ---------------------------------------------------------------------------
# adjuntar_evidencia -- responsable o aprobador (mecánica §6: "confirmación
# del referente" es un tipo de evidencia)
# ---------------------------------------------------------------------------

def test_adjuntar_evidencia_ajeno_se_rechaza(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()

    with espacio(conn, ws) as cur:
        ajeno = _quien(cur, "Ariel De Simone", ws)
        with pytest.raises(Denegado):
            H.ejecutar(cur, ajeno, "adjuntar_evidencia",
                      {"tarea_id": tid, "tipo": "explicacion",
                       "descripcion": "listo"}, ya_confirmada=True)
        cur.execute("select count(*) n from evidence where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 0


def test_adjuntar_evidencia_lo_puede_el_responsable(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        r = H.ejecutar(cur, quien, "adjuntar_evidencia",
                       {"tarea_id": tid, "tipo": "explicacion",
                        "descripcion": "listo"}, ya_confirmada=True)
        assert "evidencia_id" in r


def test_adjuntar_evidencia_lo_puede_el_aprobador(corework, conn):
    """Mecánica §6: "confirmación del referente" es evidencia -- a
    diferencia de actualizar_estado/registrar_bloqueo, acá sí se amplía más
    allá del responsable."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, marcos, "adjuntar_evidencia",
                       {"tarea_id": tid, "tipo": "explicacion",
                        "descripcion": "confirmo, lo revisé"}, ya_confirmada=True)
        assert "evidencia_id" in r


def test_adjuntar_evidencia_de_otra_persona_se_rechaza(corework, conn):
    """Ni responsable ni aprobador -- Ariel no es ninguno de los dos."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()

    with espacio(conn, ws) as cur:
        ajeno = _quien(cur, "Ariel De Simone", ws)
        with pytest.raises(Denegado):
            H.ejecutar(cur, ajeno, "adjuntar_evidencia",
                      {"tarea_id": tid, "tipo": "explicacion",
                       "descripcion": "listo"}, ya_confirmada=True)

