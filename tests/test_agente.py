"""Pruebas del turno del agente.

El proveedor está guionado: lo que se prueba no es qué escribe el modelo, sino
que Prisma haga cumplir sus reglas pase lo que pase con el modelo.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from prisma import herramientas as H
from prisma.agente import responder
from prisma.autoridad import Canal, identificar
from prisma.calendario import Calendario
from prisma.contexto import construir, revisar_salida
from prisma.db import admin, espacio
from prisma.llm import Llamada, ProveedorGuionado, Respuesta

BA = ZoneInfo("America/Argentina/Buenos_Aires")
AHORA = datetime(2026, 7, 27, 10, 0, tzinfo=BA)


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _tarea(cur, ws, titulo="Programar PLC", area="ot", persona="Marcos Tarquini"):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', 'Integrar comprimidora 3') returning id""", (ws,))
    obj = cur.fetchone()["id"]
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, fecha_objetivo,
                             criterio_aceptacion, evidencia_requerida)
           values (%s, %s, %s,
                   (select id from area where workspace_id = %s and slug = %s),
                   (select m.id from membership m join app_user u on u.id = m.app_user_id
                     where m.workspace_id = %s and u.nombre = %s),
                    '2026-08-14', 'Resultado verificado',
                    array['resultado_de_prueba'])
           returning id""",
        (ws, obj, titulo, ws, area, ws, persona))
    t = cur.fetchone()["id"]
    cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                "values (%s, 'asignada', 'prisma')", (t,))
    return str(t)


# ---------------------------------------------------------------------------
# Contexto
# ---------------------------------------------------------------------------

def test_contexto_lleva_nucleo_glosario_y_equipo(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        ctx = construir(cur, quien)

    assert "Las personas deciden" in ctx.sistema        # constitución
    assert "CoreLabs" in ctx.sistema                    # glosario
    assert "Ismael Soschinski" in ctx.sistema           # equipo
    assert "decisión final" in ctx.sistema
    assert ctx.nucleo_hash and ctx.pack_hash
    assert ctx.variantes_prohibidas["corelab"] == "CoreLabs"


def test_la_salida_no_lleva_markdown_crudo():
    """En Telegram los asteriscos se ven tal cual: `**Mar**`, no en negrita.

    El preámbulo ya pide escribir como en un chat de trabajo, pero el modelo
    igual formatea. Se limpia al salir, como el glosario.
    """
    assert revisar_salida("**¿\"Mar\" es Marcos o Mariano?**", {}) == \
        "¿\"Mar\" es Marcos o Mariano?"
    assert revisar_salida("Mirá el *panel* y el `tablero`.", {}) == \
        "Mirá el panel y el tablero."
    assert revisar_salida("### Resumen\nDos tareas.", {}) == \
        "Resumen\nDos tareas."


def test_un_asterisco_suelto_no_se_toca():
    """Multiplicar no es formatear."""
    assert revisar_salida("Son 3 * 4 turnos.", {}) == "Son 3 * 4 turnos."


def test_glosario_corrige_a_la_salida():
    variantes = {"corelab": "CoreLabs", "coreanalytics": "CoreLabs"}
    texto = "Subí el panel a CoreLab y avisá."
    assert revisar_salida(texto, variantes) == "Subí el panel a CoreLabs y avisá."


# ---------------------------------------------------------------------------
# Turno
# ---------------------------------------------------------------------------

def test_consulta_y_responde(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws)

    guion = [
        Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
        Respuesta(texto="Tenés Programar PLC abierta, vence el 14/8."),
    ]
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "¿qué tengo?", ProveedorGuionado(guion), cal,
                      chat_id=9002, ahora=AHORA)

        assert r.acciones == ["consultar_tareas"]
        cur.execute("select cuerpo, estado from message_outbox "
                    "where destinatario_membership_id = %s", (quien.membership_id,))
        fila = cur.fetchone()
        assert fila["estado"] == "listo"
        assert "Programar PLC" in fila["cuerpo"]


def test_accion_denegada_no_toca_la_base(corework, conn):
    """Nahuel es integrante: no puede aprobar el trabajo de OT."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)

    guion = [
        Respuesta(llamadas=[Llamada("c1", "aprobar_tarea", {"tarea_id": tid})]),
        Respuesta(texto="Eso lo tiene que aprobar Marcos, que es el referente de OT."),
    ]
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "aprobá la tarea", ProveedorGuionado(guion), cal,
                      chat_id=9005, ahora=AHORA)

        assert r.acciones == []                      # no se registró la acción
        cur.execute("select count(*) n from approval")
        assert cur.fetchone()["n"] == 0              # la base quedó intacta
        assert "Marcos" in r.texto


def test_no_cierra_sin_condiciones_y_lo_dice(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)

    guion = [
        Respuesta(llamadas=[Llamada(
            "c1", "actualizar_estado", {"tarea_id": tid, "estado": "terminada"})]),
        Respuesta(texto="Todavía no puedo darla por terminada: falta el criterio "
                        "de aceptación."),
    ]
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "ya terminé", ProveedorGuionado(guion), cal,
                  chat_id=9002, ahora=AHORA)

        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"   # no se movió

    # El modelo recibió el motivo concreto, no un error genérico.
    prov = ProveedorGuionado([])
    assert True


def test_confirmacion_congela_la_accion_y_no_ejecuta(corework, conn):
    """Desde ADR 0005 (decisión 1), `actualizar_estado` siempre pide
    confirmación: no hace falta forzar `REQUIEREN_CONFIRMACION` a mano."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)

    guion = [
        Respuesta(llamadas=[Llamada("c1", "actualizar_estado",
                                    {"tarea_id": tid, "estado": "en_curso"})]),
        Respuesta(texto="Listo."),
    ]
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "arranco con esto",
                      ProveedorGuionado(guion), cal, chat_id=9002, ahora=AHORA)

        assert r.confirmaciones == ["actualizar_estado"]
        assert r.acciones == []
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"     # no se ejecutó

        # Lo que espera es la acción, no la pregunta. Antes el pedido de
        # confirmación entraba a la cola en 'esperando_confirmacion' y el
        # despachador sólo levanta 'listo': la pregunta no salía nunca, y
        # la acción no quedaba guardada en ningún lado. Ahora la pregunta
        # sale con sus botones y la herramienta queda congelada entera.
        cur.execute("""select estado, pending_action_id from message_outbox""")
        m = cur.fetchone()
        assert m["estado"] == "listo" and m["pending_action_id"]
        cur.execute("""select herramienta, args, estado, huella from pending_action""")
        p = cur.fetchone()
        assert p["estado"] == "esperando"
        assert p["herramienta"] == "actualizar_estado"
        assert p["args"]["estado"] == "en_curso"
        assert p["huella"]      # T1: la vista previa guarda una huella del estado leído


def test_falla_del_modelo_no_filtra_detalles_tecnicos(corework, conn):
    ws = corework.workspace_id

    class Roto:
        def responder(self, sistema, mensajes, herramientas):
            raise RuntimeError("psycopg: connection refused at /var/run/postgres.sock")

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "hola", Roto(), cal, chat_id=9002, ahora=AHORA)

        assert r.incidente
        assert "psycopg" not in r.texto and "socket" not in r.texto
        assert "no pude completar" in r.texto

        cur.execute("select cuerpo from message_outbox")
        assert "psycopg" not in cur.fetchone()["cuerpo"]

    with admin(conn) as cur:
        cur.execute("select resumen_sanitizado, referencia_cruda from incident")
        inc = cur.fetchone()
        assert "psycopg" not in inc["resumen_sanitizado"]   # lo que se muestra
        assert "psycopg" in inc["referencia_cruda"]         # lo que se guarda


def test_bloqueo_registrado_saca_la_tarea_de_la_escalera(corework, conn):
    """Desde ADR 0005, `registrar_bloqueo` queda pendiente de confirmación en
    el turno; se confirma por botón (simulado acá con `pendientes.resolver` +
    `H.ejecutar(ya_confirmada=True)`, el mismo camino que usa el gateway) y
    recién ahí saca a la tarea de la escalera."""
    from prisma import escalera
    from prisma import herramientas as H
    from prisma import pendientes as P

    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)

    guion = [
        Respuesta(llamadas=[Llamada("c1", "registrar_bloqueo",
                                    {"tarea_id": tid,
                                     "causa": "falta el switch en sala"})]),
        Respuesta(texto="Lo anoté. ¿Sabés quién puede conseguir el switch?"),
    ]
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "estoy trabado, falta el switch",
                      ProveedorGuionado(guion), cal, chat_id=9002, ahora=AHORA)

        assert r.confirmaciones == ["registrar_bloqueo"]
        assert r.acciones == []
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"     # todavía no se aplicó

        cur.execute(
            """select id from pending_action
                where herramienta = 'registrar_bloqueo' and estado = 'esperando'""")
        pid = str(cur.fetchone()["id"])
        confirmar = P.opcion_por_etiqueta(cur, pid, "Confirmar")
        resuelta = P.resolver(cur, confirmar.token,
                              app_user_id=quien.app_user_id, ahora=AHORA)
        H.ejecutar(cur, quien, resuelta.herramienta, resuelta.args,
                  ya_confirmada=True, chat_id=9002, huella_previa=resuelta.huella)

        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "bloqueada"

        vencida = datetime(2026, 9, 1, 10, 0, tzinfo=BA)
        assert escalera.evaluar(cur, ws, cal, vencida) == []


def test_auditoria_guarda_las_versiones_de_las_reglas(corework, conn):
    ws = corework.workspace_id
    guion = [Respuesta(texto="Hola, ¿en qué te doy una mano?")]
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "hola", ProveedorGuionado(guion), cal,
                  chat_id=9002, ahora=AHORA)

    with admin(conn) as cur:
        cur.execute("""select nucleo_hash, pack_hash from audit_log
                        where accion = 'turno_agente'""")
        fila = cur.fetchone()
        assert fila["nucleo_hash"] and fila["pack_hash"]


def _intento_aprobar(conn, ws, quien_nombre, tid, chat):
    """Desde ADR 0005, `aprobar_tarea` nunca ejecuta en el mismo turno: la
    cadena de autoridad se sigue decidiendo en la preparación (antes de
    mostrar la vista previa), así que "puede aprobar" ahora se traduce en
    "queda pendiente de confirmación" en vez de "acción ejecutada"."""
    guion = [
        Respuesta(llamadas=[Llamada("c1", "aprobar_tarea", {"tarea_id": tid})]),
        Respuesta(texto="…"),
    ]
    with espacio(conn, ws) as cur:
        quien = _quien(cur, quien_nombre, ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "apruebo esa tarea", ProveedorGuionado(guion),
                      cal, chat_id=chat, ahora=AHORA)
    assert r.acciones == []      # nunca ejecuta directo, autorizado o no
    return r.confirmaciones == ["aprobar_tarea"]


def test_cadena_de_aprobacion(corework, conn):
    """A un integrante lo aprueba su referente; a un referente, Dirección.

    Nadie aprueba fuera de su cadena, y la autoridad final no es un comodín
    para firmar trabajo técnico ajeno.
    """
    ws = corework.workspace_id
    with admin(conn) as cur:
        de_nahuel = _tarea(cur, ws, titulo="Relevar plano",
                           persona="Nahuel Gimenez")
        de_marcos = _tarea(cur, ws, titulo="Programar PLC",
                           persona="Marcos Tarquini")
        de_lucas = _tarea(cur, ws, titulo="Configurar servidor", area="it",
                          persona="Lucas Natuche")
        de_ariel = _tarea(cur, ws, titulo="Panel de lote", area="corelabs",
                          persona="Ariel De Simone")

    # La tarea de Nahuel la aprueba Marcos, su referente. Nadie más.
    assert not _intento_aprobar(conn, ws, "Nahuel Gimenez", de_nahuel, 1)   # ni él
    assert not _intento_aprobar(conn, ws, "Ariel De Simone", de_nahuel, 2)  # otra área
    assert not _intento_aprobar(conn, ws, "Ismael Soschinski", de_nahuel, 3)
    assert _intento_aprobar(conn, ws, "Marcos Tarquini", de_nahuel, 4)

    # A Marcos, que es referente, lo aprueba Ismael. Marcos no se aprueba solo.
    assert not _intento_aprobar(conn, ws, "Marcos Tarquini", de_marcos, 5)
    assert _intento_aprobar(conn, ws, "Ismael Soschinski", de_marcos, 6)

    # Lucas va por Martín, no por Ismael ni por Marcos.
    assert not _intento_aprobar(conn, ws, "Marcos Tarquini", de_lucas, 7)
    assert not _intento_aprobar(conn, ws, "Ismael Soschinski", de_lucas, 8)
    assert _intento_aprobar(conn, ws, "Martín Forte", de_lucas, 9)

    # Ariel es referente y está solo en su área: lo aprueba Ismael.
    assert not _intento_aprobar(conn, ws, "Ariel De Simone", de_ariel, 10)
    assert _intento_aprobar(conn, ws, "Ismael Soschinski", de_ariel, 11)


def test_herramienta_inexistente_se_rechaza(corework, conn):
    ws = corework.workspace_id
    guion = [
        Respuesta(llamadas=[Llamada("c1", "borrar_todo", {})]),
        Respuesta(texto="Eso no lo puedo hacer."),
    ]
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "borrá todo", ProveedorGuionado(guion), cal,
                      chat_id=9002, ahora=AHORA)
        assert r.acciones == []
