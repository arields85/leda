"""Dependencias entre tareas: crear, quitar, freno de `en_curso` y aviso en
cadena.

Implementa la sección 4 de `nucleo/mecanica-pm.md`. Antes de esto el esquema
estaba completo (`dependency`, `evitar_ciclo_dependencia`,
`motivo_no_cierra_tarea`) y ninguna ruta de código escribía una fila: nada
frenaba `en_curso` y nadie avisaba de un atraso en cadena.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import psycopg
import pytest

from prisma import escalera, herramientas as H, reloj
from prisma.autoridad import Canal, Denegado, identificar
from prisma.calendario import Calendario
from prisma.db import admin, espacio

BA = ZoneInfo("America/Argentina/Buenos_Aires")


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _membership(cur, ws, nombre):
    """Sólo bajo `admin(conn)`: `app_user` no está en la vista `integrante`."""
    cur.execute(
        """select m.id from membership m join app_user u on u.id = m.app_user_id
            where m.workspace_id = %s and u.nombre = %s""", (ws, nombre))
    return str(cur.fetchone()["id"])


def _mid(cur, nombre):
    """Bajo `espacio(conn, ws)`: la vista `integrante` ya está acotada."""
    cur.execute("select membership_id from integrante where nombre = %s", (nombre,))
    return str(cur.fetchone()["membership_id"])


def _tarea(cur, ws, *, titulo, area, persona, estado_inicial="asignada",
          fecha_objetivo=None):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', %s) returning id""", (ws, f"Objetivo de {titulo}"))
    obj = cur.fetchone()["id"]
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, fecha_objetivo,
                             criterio_aceptacion, evidencia_requerida)
           values (%s, %s, %s,
                   (select id from area where workspace_id = %s and slug = %s),
                   (select m.id from membership m join app_user u on u.id = m.app_user_id
                     where m.workspace_id = %s and u.nombre = %s),
                    %s, 'Resultado verificado', array['resultado_de_prueba'])
           returning id""",
        (ws, obj, titulo, ws, area, ws, persona, fecha_objetivo))
    t = cur.fetchone()["id"]
    cur.execute(
        "insert into task_state_event (task_id, estado_nuevo, actor_kind, at) "
        "values (%s, %s, 'prisma', clock_timestamp())", (t, estado_inicial))
    return str(t)


def _dependencia(cur, ws, origen, destino, tipo="bloqueante"):
    cur.execute(
        """insert into dependency (workspace_id, origen_task_id, destino_task_id, tipo)
           values (%s, %s, %s, %s) returning id""", (ws, origen, destino, tipo))
    return str(cur.fetchone()["id"])


def _outbox(cur):
    cur.execute(
        "select destinatario_membership_id, cuerpo, tipo from message_outbox order by cuerpo")
    return cur.fetchall()


# ---------------------------------------------------------------------------
# T1 -- crear_dependencia
# ---------------------------------------------------------------------------

def test_crear_dependencia_la_puede_el_responsable_de_origen(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini")

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        r = H.ejecutar(cur, quien, "crear_dependencia",
                       {"origen_tarea_id": origen, "destino_tarea_id": destino,
                        "tipo": "bloqueante"})
        assert "dependencia_id" in r

        cur.execute("select tipo from dependency where origen_task_id = %s", (origen,))
        assert cur.fetchone()["tipo"] == "bloqueante"

        avisos = _outbox(cur)
        assert len(avisos) == 1
        marcos_mid = _mid(cur, "Marcos Tarquini")
        assert str(avisos[0]["destinatario_membership_id"]) == str(marcos_mid)


def test_crear_dependencia_la_puede_el_referente_de_cualquiera_de_las_dos(corework, conn):
    """Ismael es el aprobador (referente) de Marcos, responsable de destino.

    No es responsable de ninguna de las dos tareas, así que avisa a los dos
    responsables (decisión de producto, 2026-09-22).
    """
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini")

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        r = H.ejecutar(cur, quien, "crear_dependencia",
                       {"origen_tarea_id": origen, "destino_tarea_id": destino})
        assert "dependencia_id" in r

        avisos = _outbox(cur)
        destinatarios = {str(a["destinatario_membership_id"]) for a in avisos}
        assert destinatarios == {
            _mid(cur, "Nahuel Gimenez"),
            _mid(cur, "Marcos Tarquini"),
        } and len(avisos) == 2


def test_crear_dependencia_entre_areas_avisa_a_los_dos_referentes(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Aprovisionar servidor", area="it",
                         persona="Lucas Natuche")

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        H.ejecutar(cur, quien, "crear_dependencia",
                  {"origen_tarea_id": origen, "destino_tarea_id": destino})

        avisos = _outbox(cur)
        destinatarios = {str(a["destinatario_membership_id"]) for a in avisos}
        assert destinatarios == {
            _mid(cur, "Lucas Natuche"),      # la otra parte
            _mid(cur, "Marcos Tarquini"),    # referente de OT
            _mid(cur, "Martín Forte"),       # referente de IT
        }


def test_crear_dependencia_nunca_avisa_a_quien_la_crea(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        # Marcos es responsable de las dos: no hay "otra parte" a quien avisar.
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Marcos Tarquini")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini")

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        H.ejecutar(cur, quien, "crear_dependencia",
                  {"origen_tarea_id": origen, "destino_tarea_id": destino})
        assert _outbox(cur) == []


def test_crear_dependencia_avisa_a_la_otra_parte_aunque_sea_su_referente(corework, conn):
    """Marcos es responsable de origen y también el referente (aprobador) de
    Nahuel, responsable de destino. Sigue siendo "la otra parte": la regla es
    sobre de qué tarea es responsable quien crea, no sobre a quién más
    aprueba."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Marcos Tarquini")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Nahuel Gimenez")

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        H.ejecutar(cur, quien, "crear_dependencia",
                  {"origen_tarea_id": origen, "destino_tarea_id": destino})
        avisos = _outbox(cur)
        assert [str(a["destinatario_membership_id"]) for a in avisos] == [
            _mid(cur, "Nahuel Gimenez")]


def test_crear_dependencia_sin_autoridad_se_rechaza(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini")

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ariel De Simone", ws)   # ajeno a las dos tareas
        with pytest.raises(Denegado):
            H.ejecutar(cur, quien, "crear_dependencia",
                       {"origen_tarea_id": origen, "destino_tarea_id": destino})


def test_crear_dependencia_tarea_inexistente_dice_que_no_existe(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini")

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, quien, "crear_dependencia",
                       {"origen_tarea_id": "00000000-0000-0000-0000-000000000000",
                        "destino_tarea_id": destino})
        assert "no existe" in r["error"]


def test_crear_dependencia_misma_tarea_en_las_dos_puntas_se_rechaza(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                    persona="Marcos Tarquini")

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, quien, "crear_dependencia",
                       {"origen_tarea_id": tid, "destino_tarea_id": tid})
        assert "error" in r


def test_crear_dependencia_duplicada_se_rechaza(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini")
        _dependencia(cur, ws, origen, destino)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, quien, "crear_dependencia",
                       {"origen_tarea_id": origen, "destino_tarea_id": destino})
        assert "error" in r
        cur.execute(
            "select count(*) n from dependency where origen_task_id = %s", (origen,))
        assert cur.fetchone()["n"] == 1


def test_crear_dependencia_con_destino_ya_cerrada_se_rechaza(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini")
        cur.execute(
            """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                             actor_kind, motivo)
               values (%s, 'asignada', 'cancelada', 'sistema', 'ya no aplica')""",
            (destino,))

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, quien, "crear_dependencia",
                       {"origen_tarea_id": origen, "destino_tarea_id": destino})
        assert "error" in r


def test_crear_dependencia_que_forma_un_ciclo_da_un_mensaje_claro(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        a = _tarea(cur, ws, titulo="A", area="ot", persona="Nahuel Gimenez")
        b = _tarea(cur, ws, titulo="B", area="ot", persona="Marcos Tarquini")
        _dependencia(cur, ws, a, b)   # A bloquea a B

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        with pytest.raises(psycopg.errors.RaiseException, match="ciclo"):
            H.ejecutar(cur, quien, "crear_dependencia",
                       {"origen_tarea_id": b, "destino_tarea_id": a})


def test_crear_dependencia_bloqueante_sobre_destino_ya_en_curso_lo_menciona(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini", estado_inicial="en_curso")

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        H.ejecutar(cur, quien, "crear_dependencia",
                  {"origen_tarea_id": origen, "destino_tarea_id": destino})

        cur.execute("select estado from task where id = %s", (destino,))
        assert cur.fetchone()["estado"] == "en_curso"   # no la mueve retroactivamente

        avisos = _outbox(cur)
        assert any("en curso" in a["cuerpo"] for a in avisos)


# ---------------------------------------------------------------------------
# T1 -- quitar_dependencia
# ---------------------------------------------------------------------------

def test_quitar_dependencia_la_puede_el_responsable_de_cualquiera(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini")
        dep_id = _dependencia(cur, ws, origen, destino)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, quien, "quitar_dependencia", {"dependencia_id": dep_id})
        assert r["eliminada"] is True
        cur.execute("select count(*) n from dependency where id = %s", (dep_id,))
        assert cur.fetchone()["n"] == 0


def test_quitar_dependencia_sin_autoridad_se_rechaza(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini")
        dep_id = _dependencia(cur, ws, origen, destino)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ariel De Simone", ws)
        with pytest.raises(Denegado):
            H.ejecutar(cur, quien, "quitar_dependencia", {"dependencia_id": dep_id})
        cur.execute("select count(*) n from dependency where id = %s", (dep_id,))
        assert cur.fetchone()["n"] == 1


def test_quitar_dependencia_inexistente_dice_que_no_existe(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, quien, "quitar_dependencia",
                       {"dependencia_id": "00000000-0000-0000-0000-000000000000"})
        assert "no existe" in r["error"]


def test_quitar_dependencia_queda_auditada(corework, conn):
    """No hay baja blanda en `dependency` (a diferencia de `blocker.resuelto_en`):
    el rastro de quién quitó qué y cuándo lo da el mismo mecanismo genérico
    que audita cualquier herramienta (`agente._ejecutar_una`,
    `registrar_auditoria` con accion `herramienta:<nombre>` y los argumentos),
    así que se prueba a través del turno completo, no de `H.ejecutar` directo."""
    from prisma.agente import responder
    from prisma.llm import Llamada, ProveedorGuionado, Respuesta

    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini")
        dep_id = _dependencia(cur, ws, origen, destino)

    guion = [
        Respuesta(llamadas=[Llamada("c1", "quitar_dependencia",
                                    {"dependencia_id": dep_id})]),
        Respuesta(texto="Listo, la quité."),
    ]
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "sacá esa dependencia",
                     ProveedorGuionado(guion), cal, chat_id=9002,
                     ahora=datetime(2026, 7, 27, 10, 0, tzinfo=BA))
        assert r.acciones == ["quitar_dependencia"]

    with admin(conn) as cur:
        cur.execute(
            """select detalle from audit_log
                where accion = 'herramienta:quitar_dependencia'""")
        f = cur.fetchone()
        assert f is not None
        assert f["detalle"]["args"]["dependencia_id"] == dep_id


# ---------------------------------------------------------------------------
# T2 -- freno de en_curso
# ---------------------------------------------------------------------------

def test_en_curso_se_frena_con_bloqueante_sin_terminar(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini")
        _dependencia(cur, ws, origen, destino)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, quien, "actualizar_estado",
                       {"tarea_id": destino, "estado": "en_curso"})
        assert r["iniciada"] is False
        assert "Programar PLC" not in r["falta"] or "bloqueante" in r["falta"].lower() \
            or "dependencia" in r["falta"].lower()

        cur.execute("select estado from task where id = %s", (destino,))
        assert cur.fetchone()["estado"] == "asignada"


def test_en_curso_se_libera_cuando_la_origen_termina(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini")
        _dependencia(cur, ws, origen, destino)
        cur.execute(
            """insert into evidence (workspace_id, task_id, tipo, entregado_por)
               values (%s, %s, 'resultado_de_prueba', null)""", (ws, origen))
        # Marcos es el referente (aprobador) de Nahuel: hace falta su
        # aprobación para que `motivo_no_cierra_tarea` deje cerrar.
        cur.execute(
            """insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                     aprobador_membership_id, decision)
               values (%s, 'tarea', %s,
                       (select m.id from membership m join app_user u
                          on u.id = m.app_user_id
                        where m.workspace_id = %s and u.nombre = 'Marcos Tarquini'),
                       'aprobado')""", (ws, origen, ws))

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        r = H.ejecutar(cur, quien, "actualizar_estado",
                       {"tarea_id": origen, "estado": "terminada"})
        assert r == {"estado": "terminada"}

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, quien, "actualizar_estado",
                       {"tarea_id": destino, "estado": "en_curso"})
        assert r == {"estado": "en_curso"}


def test_en_curso_no_se_frena_por_dependencia_informativa(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini")
        _dependencia(cur, ws, origen, destino, tipo="informativa")

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, quien, "actualizar_estado",
                       {"tarea_id": destino, "estado": "en_curso"})
        assert r == {"estado": "en_curso"}


def test_en_curso_no_se_frena_si_el_origen_ya_estaba_cancelada(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini")
        _dependencia(cur, ws, origen, destino)
        cur.execute(
            """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                             actor_kind, motivo)
               values (%s, 'asignada', 'cancelada', 'sistema', 'ya no aplica')""",
            (origen,))

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, quien, "actualizar_estado",
                       {"tarea_id": destino, "estado": "en_curso"})
        assert r == {"estado": "en_curso"}


def test_en_curso_directo_por_base_sigue_bloqueado_por_el_disparador(corework, conn):
    """El freno vive en la base, no sólo en el handler de Python."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini")
        _dependencia(cur, ws, origen, destino)

        with pytest.raises(psycopg.errors.RaiseException, match="en curso"):
            cur.execute(
                """insert into task_state_event (task_id, estado_anterior,
                                                 estado_nuevo, actor_kind)
                   values (%s, 'asignada', 'en_curso', 'sistema')""", (destino,))


# ---------------------------------------------------------------------------
# T3 -- aviso en cadena
# ---------------------------------------------------------------------------

def test_dependencia_bloqueante_vencida_avisa_a_la_cadena_completa(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez",
                        fecha_objetivo=datetime(2026, 7, 20, 17, 0, tzinfo=BA))
        medio = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                       persona="Marcos Tarquini",
                       fecha_objetivo=datetime(2026, 8, 1, 17, 0, tzinfo=BA))
        final = _tarea(cur, ws, titulo="Entregar máquina", area="ot",
                       persona="Nahuel Gimenez",
                       fecha_objetivo=datetime(2026, 8, 10, 17, 0, tzinfo=BA))
        _dependencia(cur, ws, origen, medio)
        _dependencia(cur, ws, medio, final)

    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        ahora = datetime(2026, 7, 28, 10, 0, tzinfo=BA)
        acciones = escalera.evaluar_dependencias_en_riesgo(cur, ws, cal, ahora)
        destinatarios = {a.destinatario_membership_id for a in acciones}
        assert destinatarios == {
            _mid(cur, "Marcos Tarquini"),
            _mid(cur, "Nahuel Gimenez"),
        }

        encoladas = escalera.encolar_dependencias(cur, ws, acciones, ahora)
        assert encoladas == len(acciones)

        # un reinicio que vuelve a evaluar el mismo momento no duplica
        acciones2 = escalera.evaluar_dependencias_en_riesgo(cur, ws, cal, ahora)
        assert escalera.encolar_dependencias(cur, ws, acciones2, ahora) == 0


def test_dependencia_en_riesgo_por_fecha_posterior_a_la_del_dependiente(corework, conn):
    """No hace falta estar vencida: alcanza con que la fecha de la bloqueante
    quede después de la de quien depende de ella."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez",
                        fecha_objetivo=datetime(2026, 8, 20, 17, 0, tzinfo=BA))
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini",
                         fecha_objetivo=datetime(2026, 8, 10, 17, 0, tzinfo=BA))
        _dependencia(cur, ws, origen, destino)

    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        ahora = datetime(2026, 7, 28, 10, 0, tzinfo=BA)   # nada vencido todavía
        acciones = escalera.evaluar_dependencias_en_riesgo(cur, ws, cal, ahora)
        assert [a.destinatario_membership_id for a in acciones] == [
            _mid(cur, "Marcos Tarquini")]


def test_dependencia_sin_riesgo_no_avisa(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez",
                        fecha_objetivo=datetime(2026, 8, 1, 17, 0, tzinfo=BA))
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini",
                         fecha_objetivo=datetime(2026, 8, 20, 17, 0, tzinfo=BA))
        _dependencia(cur, ws, origen, destino)

    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        ahora = datetime(2026, 7, 28, 10, 0, tzinfo=BA)
        assert escalera.evaluar_dependencias_en_riesgo(cur, ws, cal, ahora) == []


def test_ejecutar_escalera_tambien_avisa_dependencias_en_riesgo(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez",
                        fecha_objetivo=datetime(2026, 7, 20, 17, 0, tzinfo=BA))
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini",
                         fecha_objetivo=datetime(2026, 8, 1, 17, 0, tzinfo=BA))
        _dependencia(cur, ws, origen, destino)

    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        ahora = datetime(2026, 7, 28, 10, 0, tzinfo=BA)
        n = reloj.ejecutar_escalera(cur, ws, cal, ahora)
        assert n >= 1


def test_dependencia_informativa_avisa_a_ambos_al_cambiar_de_estado(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini")
        _dependencia(cur, ws, origen, destino, tipo="informativa")

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        H.ejecutar(cur, quien, "actualizar_estado",
                  {"tarea_id": origen, "estado": "en_curso"})

        avisos = _outbox(cur)
        destinatarios = {str(a["destinatario_membership_id"]) for a in avisos}
        assert destinatarios == {
            _mid(cur, "Nahuel Gimenez"),
            _mid(cur, "Marcos Tarquini"),
        }


def test_dependencia_informativa_no_avisa_dos_veces_por_el_mismo_evento(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini")
        _dependencia(cur, ws, origen, destino, tipo="informativa")

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        H.ejecutar(cur, quien, "actualizar_estado",
                  {"tarea_id": origen, "estado": "en_curso"})
        primero = len(_outbox(cur))

        H.ejecutar(cur, quien, "actualizar_estado",
                  {"tarea_id": origen, "estado": "en_revision"})
        segundo = len(_outbox(cur))
        assert segundo > primero   # es un cambio de estado distinto, avisa de nuevo


# ---------------------------------------------------------------------------
# Corrección tras revisión
# ---------------------------------------------------------------------------

def test_resolver_bloqueo_no_se_frena_por_dependencia_bloqueante_abierta(corework, conn):
    """Defecto: volver de `bloqueada` es una restauración al estado previo
    (mecánica §3), no un arranque -- el freno de `en_curso` es para arrancar.
    Escenario: X está en curso; se crea una bloqueante con X de destino y la
    origen sin terminar (T1 lo permite, sin mover X retroactivamente); X se
    bloquea; se resuelve el último bloqueo. Antes de la corrección,
    `trg_exigir_dependencias_resueltas` rechazaba el insert `bloqueada ->
    en_curso` y el bloqueo quedaba imposible de resolver mientras la
    dependencia siguiera abierta."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini", estado_inicial="en_curso")
        _dependencia(cur, ws, origen, destino)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, quien, "registrar_bloqueo",
                       {"tarea_id": destino, "causa": "algo urgente"})
        bloqueo_id = r["bloqueo_id"]

        r = H.ejecutar(cur, quien, "resolver_bloqueo",
                       {"bloqueo_id": bloqueo_id, "resolucion": "listo"})
        assert r == {"resuelto": True, "tarea_desbloqueada": True}

        cur.execute("select estado from task where id = %s", (destino,))
        assert cur.fetchone()["estado"] == "en_curso"


def test_actualizar_estado_de_bloqueada_a_en_curso_no_se_frena_por_dependencia(corework, conn):
    """Mismo criterio por el camino directo: `actualizar_estado` no exige
    bloqueos cerrados para salir de `bloqueada` (deuda conocida), así que
    puede recibir la misma transición que `resolver_bloqueo`. El chequeo
    proactivo de la herramienta tiene que coincidir con el disparador: si la
    base ya la permite, la herramienta no puede seguir devolviendo
    `iniciada: False`."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini", estado_inicial="en_curso")
        _dependencia(cur, ws, origen, destino)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        H.ejecutar(cur, quien, "registrar_bloqueo",
                  {"tarea_id": destino, "causa": "algo"})
        r = H.ejecutar(cur, quien, "actualizar_estado",
                       {"tarea_id": destino, "estado": "en_curso"})
        assert r == {"estado": "en_curso"}


def test_dependencia_en_riesgo_reavisa_al_pasar_de_posterior_a_vencida(corework, conn):
    """Defecto: la clave de deduplicación no distinguía el motivo del riesgo.
    Si el primer aviso salía por "la fecha queda después de la del
    dependiente" y más tarde la origen se vencía de verdad, el segundo aviso
    -- más grave -- reusaba la misma clave y se perdía en silencio."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez",
                        fecha_objetivo=datetime(2026, 8, 20, 17, 0, tzinfo=BA))
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini",
                         fecha_objetivo=datetime(2026, 8, 10, 17, 0, tzinfo=BA))
        _dependencia(cur, ws, origen, destino)

    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)

        # corrida 1: no vencida todavía, pero la fecha queda después de la
        # del dependiente.
        ahora1 = datetime(2026, 7, 28, 10, 0, tzinfo=BA)
        acciones1 = escalera.evaluar_dependencias_en_riesgo(cur, ws, cal, ahora1)
        assert "vencida" not in acciones1[0].cuerpo
        assert escalera.encolar_dependencias(cur, ws, acciones1, ahora1) == 1

        # corrida 2, mismo momento: no duplica.
        acciones2 = escalera.evaluar_dependencias_en_riesgo(cur, ws, cal, ahora1)
        assert escalera.encolar_dependencias(cur, ws, acciones2, ahora1) == 0

        # corrida 3: la origen ya está vencida -- motivo distinto, reavisa.
        ahora2 = datetime(2026, 8, 25, 10, 0, tzinfo=BA)
        acciones3 = escalera.evaluar_dependencias_en_riesgo(cur, ws, cal, ahora2)
        assert "vencida" in acciones3[0].cuerpo
        assert escalera.encolar_dependencias(cur, ws, acciones3, ahora2) == 1

        # corrida 4, mismo momento vencido: no duplica de nuevo.
        acciones4 = escalera.evaluar_dependencias_en_riesgo(cur, ws, cal, ahora2)
        assert escalera.encolar_dependencias(cur, ws, acciones4, ahora2) == 0

        cur.execute("select count(*) n from message_outbox")
        assert cur.fetchone()["n"] == 2


def test_dependencia_en_riesgo_nombra_las_tareas_afectadas_directas_e_indirectas(
        corework, conn):
    """Defecto: el aviso no nombraba ninguna tarea ("de ella depende esta
    tarea"), así que el destinatario no tenía sobre qué actuar, y para un
    dependiente indirecto la frase además era inexacta."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez",
                        fecha_objetivo=datetime(2026, 7, 20, 17, 0, tzinfo=BA))
        medio = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                       persona="Marcos Tarquini",
                       fecha_objetivo=datetime(2026, 8, 1, 17, 0, tzinfo=BA))
        final = _tarea(cur, ws, titulo="Entregar máquina", area="ot",
                       persona="Nahuel Gimenez",
                       fecha_objetivo=datetime(2026, 8, 10, 17, 0, tzinfo=BA))
        _dependencia(cur, ws, origen, medio)
        _dependencia(cur, ws, medio, final)

    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        ahora = datetime(2026, 7, 28, 10, 0, tzinfo=BA)
        acciones = escalera.evaluar_dependencias_en_riesgo(cur, ws, cal, ahora)

        por_destinatario = {a.destinatario_membership_id: a for a in acciones}
        marcos = _mid(cur, "Marcos Tarquini")
        nahuel = _mid(cur, "Nahuel Gimenez")

        # Marcos: dependiente directo de la origen.
        assert "Cablear tablero" in por_destinatario[marcos].cuerpo
        assert "cadena" not in por_destinatario[marcos].cuerpo

        # Nahuel: dependiente indirecto, a través de "Cablear tablero".
        assert "Entregar máquina" in por_destinatario[nahuel].cuerpo
        assert "cadena" in por_destinatario[nahuel].cuerpo


def test_en_curso_desde_bloqueada_sigue_frenado_si_nunca_arranco(corework, conn):
    """Segunda corrección tras revisión: eximir por `estado_anterior =
    'bloqueada'' a secas era demasiado amplio. Una tarea que nunca arrancó
    (`asignada` -> `registrar_bloqueo` -> `bloqueada`) no puede colarse a
    `en_curso` sólo porque pasó por un bloqueo: mecánica §4 exige la origen
    terminada para arrancar, y esto nunca arrancó. La restauración legítima
    exige que el estado previo a la última entrada a `bloqueada` haya sido
    `en_curso` -- acá fue `asignada`, así que el freno tiene que seguir."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Programar PLC", area="ot",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero", area="ot",
                         persona="Marcos Tarquini")   # asignada, nunca en curso
        _dependencia(cur, ws, origen, destino)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        H.ejecutar(cur, quien, "registrar_bloqueo",
                  {"tarea_id": destino, "causa": "algo"})
        r = H.ejecutar(cur, quien, "actualizar_estado",
                       {"tarea_id": destino, "estado": "en_curso"})
        assert r["iniciada"] is False
        assert "dependencia" in r["falta"].lower() or "bloqueante" in r["falta"].lower()

        cur.execute("select estado from task where id = %s", (destino,))
        assert cur.fetchone()["estado"] == "bloqueada"
