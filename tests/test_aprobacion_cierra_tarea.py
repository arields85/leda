"""Aprobar registra la aprobación y, si alcanza, cierra en el mismo acto
(ADR 0008).

Sesión 2 por Telegram real, 2026-09-27 (hallazgo 5): Ismael aprobó por el
menú de una tarea y Leda contestó "se aprueba el trabajo", pero la tarea
quedó en `en_revision` -- `herramientas._aprobar_tarea` sólo insertaba en
`approval`, nunca corría `motivo_no_cierra_tarea` ni escribía en
`task_state_event`. El responsable de la tarea (Ariel) nunca se enteró, y su
menú en `en_revision` no ofrecía ningún botón para cerrarla.

Estas pruebas cubren la corrección: `aprobar_tarea` siempre escribe la
aprobación; si con ella alcanzan las condiciones de cierre
(`nucleo/mecanica-pm.md` §5), la misma llamada también cierra -- dos filas
distintas (`approval` y `task_state_event`), un solo acto -- y avisa al
responsable en cualquier caso. También cubre el mensaje posterior a
confirmar por botón, que antes repetía el texto de la vista previa en vez de
describir el resultado.
"""

from __future__ import annotations


from leda import herramientas as H
from leda.autoridad import Canal, identificar
from leda.db import admin, espacio


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _tarea(cur, ws, *, titulo="Programar HMI línea 2", persona="Nahuel Gimenez",
          estado="en_revision", criterio_aceptacion="Criterio de prueba",
          evidencia_requerida=("explicacion",)):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', 'Objetivo de prueba') returning id""", (ws,))
    obj = cur.fetchone()["id"]
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, criterio_aceptacion,
                             evidencia_requerida)
           values (%s, %s, %s,
                   (select id from area where workspace_id = %s and slug = 'ot'),
                   (select m.id from membership m join app_user u on u.id = m.app_user_id
                     where m.workspace_id = %s and u.nombre = %s),
                   %s, %s)
           returning id""",
        (ws, obj, titulo, ws, ws, persona, criterio_aceptacion,
         list(evidencia_requerida) if evidencia_requerida else []))
    t = cur.fetchone()["id"]
    cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                "values (%s, %s, 'leda')", (t, estado))
    return str(t)


def _evidencia(cur, ws, tarea_id, *, tipo="explicacion"):
    cur.execute(
        """insert into evidence (workspace_id, task_id, tipo, uri)
           values (%s, %s, %s, 'lista')""", (ws, tarea_id, tipo))


# ---------------------------------------------------------------------------
# El handler: aprueba y, si alcanza, cierra
# ---------------------------------------------------------------------------

def test_aprobar_tarea_cierra_cuando_las_condiciones_estan(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        _evidencia(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(cur, marcos, "aprobar_tarea", {"tarea_id": tid},
                               ya_confirmada=True)

    assert resultado == {"aprobada": True, "cerrada": True, "falta": None,
                         "titulo": "Programar HMI línea 2"}

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "terminada"
        cur.execute("select count(*) n from approval where sujeto_id = %s", (tid,))
        assert cur.fetchone()["n"] == 1
        cur.execute(
            """select count(*) n from task_state_event
                where task_id = %s and estado_nuevo = 'terminada'""", (tid,))
        assert cur.fetchone()["n"] == 1

        cur.execute("select telegram_user_id from app_user where nombre = %s",
                   ("Nahuel Gimenez",))
        tg_nahuel = cur.fetchone()["telegram_user_id"]
        cur.execute(
            """select cuerpo from message_outbox
                where workspace_id = %s and chat_id = %s
               order by programado_para desc limit 1""", (ws, tg_nahuel))
        aviso = cur.fetchone()["cuerpo"]
    assert aviso == "Marcos Tarquini aprobó «Programar HMI línea 2»; quedó terminada."


def test_aprobar_tarea_rechaza_si_falta_la_evidencia_que_exige(corework, conn):
    """Adaptado para ADR 0009 (decisión 2): antes, aprobar sin evidencia
    igual registraba la aprobación y sólo avisaba que no alcanzaba para
    cerrar -- exactamente lo que permitió que Ismael aprobara a ciegas la
    tarea de Ariel (hallazgo 5). Ahora ni siquiera se registra: se rechaza
    antes de escribir nada. Cobertura más completa (el gate, "Pedir
    cambios", la notificación de entrega) en `test_entrega_con_evidencia.py`."""
    from leda.autoridad import Denegado

    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)   # sin evidencia
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        try:
            H.ejecutar(cur, marcos, "aprobar_tarea", {"tarea_id": tid},
                      ya_confirmada=True)
            assert False, "tenía que rechazar"
        except Denegado as e:
            assert "evidencia" in str(e).lower()

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_revision"    # nada cambió
        cur.execute("select count(*) n from approval where sujeto_id = %s", (tid,))
        assert cur.fetchone()["n"] == 0                     # tampoco se aprobó


def test_aprobar_tarea_no_cierra_con_dependencia_bloqueante_sin_resolver(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Instalar tablero",
                        persona="Marcos Tarquini", estado="asignada")
        destino = _tarea(cur, ws, titulo="Programar HMI línea 3")
        _evidencia(cur, ws, destino)
        cur.execute(
            """insert into dependency (workspace_id, origen_task_id,
                                       destino_task_id, tipo)
               values (%s, %s, %s, 'bloqueante')""", (ws, origen, destino))
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(cur, marcos, "aprobar_tarea", {"tarea_id": destino},
                               ya_confirmada=True)

    assert resultado["aprobada"] is True
    assert resultado["cerrada"] is False
    assert "dependencia" in resultado["falta"].lower()

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (destino,))
        assert cur.fetchone()["estado"] == "en_revision"
        cur.execute("select count(*) n from approval where sujeto_id = %s", (destino,))
        assert cur.fetchone()["n"] == 1


# ---------------------------------------------------------------------------
# El comprobante de aprobar, armado por la preparación (T10-2c)
# ---------------------------------------------------------------------------

def _preparar_aprobar(conn, ws, tid) -> dict:
    """Corre la preparación real de `aprobar_tarea` y devuelve lo que arma
    (`cambio` y `hecho`), sin confirmar nada."""
    preparacion: dict = {}
    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        try:
            H.ejecutar(cur, marcos, "aprobar_tarea", {"tarea_id": tid},
                       preparacion=preparacion)
        except H.NecesitaConfirmacion:
            pass
    return preparacion


def test_comprobante_de_aprobar_cuando_la_aprobacion_alcanza_para_cerrar(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        _evidencia(cur, ws, tid)
    conn.commit()

    prep = _preparar_aprobar(conn, ws, tid)

    assert prep["hecho"] == "Listo: aprobaste «Programar HMI línea 2». Quedó terminada."
    assert "Se aprueba «Programar HMI línea 2» y queda terminada" in prep["cambio"]


def test_comprobante_de_aprobar_con_pendientes_dice_el_motivo_como_texto(
        corework, conn):
    """`falta` es el texto que devuelve `motivo_no_cierra_tarea`: nunca una
    tupla, lista o diccionario impreso con sus comillas y paréntesis."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Instalar tablero",
                        persona="Marcos Tarquini", estado="asignada")
        tid = _tarea(cur, ws)
        _evidencia(cur, ws, tid)
        cur.execute(
            """insert into dependency (workspace_id, origen_task_id,
                                       destino_task_id, tipo)
               values (%s, %s, %s, 'bloqueante')""", (ws, origen, tid))
    conn.commit()

    prep = _preparar_aprobar(conn, ws, tid)

    assert prep["hecho"] == (
        "Listo: aprobaste «Programar HMI línea 2»; para cerrarla todavía: "
        "Quedan 1 dependencias bloqueantes sin resolver.")
    assert "para cerrarla todavía: Quedan 1 dependencias bloqueantes sin resolver." \
        in prep["cambio"]
    for texto in (prep["hecho"], prep["cambio"]):
        assert not any(c in texto for c in "[]{}()") and "'" not in texto
