"""T2b (`prisma-orienta`): autoridad sobre tareas ajenas.

Hallazgo del orquestador, evidencia de la sesión real por Telegram del
2026-09-25: sin un chequeo explícito, `actualizar_estado`, `registrar_bloqueo`
y `adjuntar_evidencia` estaban permitidas a CUALQUIER integrante autenticado
del espacio, sobre CUALQUIER tarea -- un integrante podía mover el estado de
la tarea de otra persona, declararle un bloqueo o adjuntarle evidencia. En la
sesión real, sólo la reticencia del modelo evitó hacerlo ("Ese no es tuyo");
no había nada en el servidor que lo impidiera. El menú de tarea (T2,
`menu_tarea.calcular_menu`) ya sólo ofrece estos botones a quien corresponde,
pero texto libre seguía llegando a las herramientas sin ese filtro.

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
  necesita autoridad ampliada. Coincide con el menú de T2
  (`test_menu_aprobador_en_revision`, `test_menu_aprobador_otro_estado`):
  el aprobador nunca ve un botón que cambie el estado, sólo "Aprobar".
- `adjuntar_evidencia`: responsable O aprobador. `nucleo/mecanica-pm.md` §6
  lista "confirmación del referente" entre la evidencia que Prisma
  solicita -- el aprobador de la tarea (`puede_aprobar_tarea`, un solo
  nivel: a un integrante lo aprueba su referente) también puede adjuntarla.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from prisma import herramientas as H
from prisma import menu_tarea as M
from prisma.agente import responder
from prisma.autoridad import Canal, Denegado, identificar
from prisma.calendario import Calendario
from prisma.db import admin, espacio
from prisma.llm import Llamada, ProveedorGuionado, Respuesta


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
                "values (%s, %s, 'prisma')", (t, estado))
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


def test_llamada_del_modelo_a_tarea_ajena_no_arma_vista_previa(corework, conn):
    """El rechazo tiene que frenar antes de mostrar cualquier vista previa
    -- no sólo antes de aplicar el cambio -- igual que cualquier otro
    `Denegado` (`agente._ejecutar_una`, `except Denegado` antes de
    `NecesitaConfirmacion`). Sin este chequeo, el modelo podía llegar a
    ofrecerle a Ariel una vista previa para mover la tarea de Nahuel."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()

    guion = [
        Respuesta(llamadas=[Llamada("c1", "actualizar_estado",
                                    {"tarea_id": tid, "estado": "en_curso"})]),
        Respuesta(texto="No pude hacer eso."),
    ]
    with espacio(conn, ws) as cur:
        ajeno = _quien(cur, "Ariel De Simone", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, ajeno, "poné en curso la de Nahuel", ProveedorGuionado(guion),
                 cal, chat_id=1, ahora=datetime.now(timezone.utc))

        cur.execute(
            "select count(*) n from pending_action where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 0
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"


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


# ---------------------------------------------------------------------------
# Consistencia con el menú (T2, `menu_tarea.calcular_menu`): lo que el menú
# ofrece tiene que ser lo que la herramienta permite, y lo que no ofrece
# tiene que seguir rechazado del lado de la herramienta.
# ---------------------------------------------------------------------------

def test_lo_que_el_menu_ofrece_al_responsable_la_herramienta_lo_permite(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada")
    conn.commit()

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        menu = M.calcular_menu(cur, quien, tid)
        codigos = {a.codigo for a in menu.acciones}
        assert "empezar" in codigos and "informar_bloqueo" in codigos

        # Ninguna de las dos debe levantar Denegado: el menú las ofrece.
        H.ejecutar(cur, quien, "actualizar_estado",
                  {"tarea_id": tid, "estado": "en_curso"}, ya_confirmada=True)


def test_lo_que_el_menu_no_ofrece_al_aprobador_la_herramienta_lo_rechaza(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada")
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        menu = M.calcular_menu(cur, marcos, tid)
        codigos = {a.codigo for a in menu.acciones}
        assert "empezar" not in codigos
        assert "informar_bloqueo" not in codigos

        with pytest.raises(Denegado):
            H.ejecutar(cur, marcos, "actualizar_estado",
                      {"tarea_id": tid, "estado": "en_curso"}, ya_confirmada=True)
        with pytest.raises(Denegado):
            H.ejecutar(cur, marcos, "registrar_bloqueo",
                      {"tarea_id": tid, "causa": "algo"}, ya_confirmada=True)


def test_lo_que_el_menu_no_ofrece_a_otra_persona_la_herramienta_lo_rechaza(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada")
    conn.commit()

    with espacio(conn, ws) as cur:
        ajeno = _quien(cur, "Ariel De Simone", ws)
        menu = M.calcular_menu(cur, ajeno, tid)
        codigos = {a.codigo for a in menu.acciones}
        assert codigos == {"ver_detalle", "mi_trabajo_depende"}

        with pytest.raises(Denegado):
            H.ejecutar(cur, ajeno, "actualizar_estado",
                      {"tarea_id": tid, "estado": "en_curso"}, ya_confirmada=True)
        with pytest.raises(Denegado):
            H.ejecutar(cur, ajeno, "registrar_bloqueo",
                      {"tarea_id": tid, "causa": "algo"}, ya_confirmada=True)
        with pytest.raises(Denegado):
            H.ejecutar(cur, ajeno, "adjuntar_evidencia",
                      {"tarea_id": tid, "tipo": "explicacion",
                       "descripcion": "listo"}, ya_confirmada=True)
