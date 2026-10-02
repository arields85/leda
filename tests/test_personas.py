"""Pruebas de la resolución de personas.

El hueco que cierran: `where nombre ilike '%Mar%' limit 1` se queda con el
primero que devuelva el planificador —Marcos, Martín o Mariano, da igual— y si
no coincide nadie inserta NULL sin decir nada. La tarea queda creada, sin
responsable, y Leda contesta que la asignó. No miente el modelo: le mintió
la base.

Una persona se resuelve exacto o no se resuelve. Cuando hay más de una
candidata, Leda pregunta con botones, y lo que vuelve es un identificador,
no un nombre para volver a adivinar.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from leda import gateway
from leda import herramientas as H
from leda import pendientes as P
from leda.agente import responder
from leda.autoridad import Canal, identificar
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.llm import Llamada, ProveedorGuionado, Respuesta
from leda.salida import NO_EFFECT_STATUS

BA = ZoneInfo("America/Argentina/Buenos_Aires")
AHORA = datetime(2026, 7, 27, 10, 0, tzinfo=BA)


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s",
                (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _objetivo(cur, ws):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', 'Integrar comprimidora 3') returning id""",
        (ws,))
    return str(cur.fetchone()["id"])


# ---------------------------------------------------------------------------
# Resolver sin adivinar
# ---------------------------------------------------------------------------

def test_un_nombre_que_identifica_a_una_sola_persona_se_guarda_en_borrador(
        corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        r = H.crear_borrador_tarea(cur, quien, **{
            "titulo": "Relevar tablero", "objetivo_id": _objetivo(cur, ws),
            "area_slug": "ot", "responsable": "Marcos"})

        cur.execute(
            """select i.nombre from task_draft d
                 join integrante i on i.membership_id = d.responsable_membership_id
                where d.id = %s""", (r["draft_id"],))
        assert cur.fetchone()["nombre"] == "Marcos Tarquini"
        assert r["completa"] is False


def test_un_nombre_ambiguo_no_crea_nada_y_pregunta(corework, conn):
    """"Mar" son tres personas. Antes se quedaba con una en silencio."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)

        with pytest.raises(H.NecesitaElegir) as e:
            H.crear_borrador_tarea(cur, quien, **{
                "titulo": "Relevar tablero", "objetivo_id": _objetivo(cur, ws),
                "area_slug": "ot", "responsable": "Mar"})

        etiquetas = sorted(et for et, _ in e.value.opciones)
        assert etiquetas == ["Marcos Tarquini", "Mariano Naim", "Martín Forte"]
        assert e.value.campo == "responsable_membership_id"

        cur.execute("select count(*) n from task")
        assert cur.fetchone()["n"] == 0        # no se creó nada


def test_un_nombre_que_no_existe_no_crea_la_tarea_sin_responsable(corework, conn):
    """El peor caso viejo: NULL silencioso y "listo, se la asigné"."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)

        r = H.crear_borrador_tarea(cur, quien, **{
            "titulo": "Relevar tablero", "objetivo_id": _objetivo(cur, ws),
            "area_slug": "ot", "responsable": "Ronaldinho"})

        assert r.get("creada") is False
        assert "Ronaldinho" in r.get("error", "")
        cur.execute("select count(*) n from task")
        assert cur.fetchone()["n"] == 0


def test_sin_responsable_el_pedido_queda_como_borrador(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        r = H.crear_borrador_tarea(cur, quien, **{
            "titulo": "Relevar tablero", "objetivo_id": _objetivo(cur, ws),
            "area_slug": "ot"})

        cur.execute(
            "select responsable_membership_id r from task_draft where id = %s",
            (r["draft_id"],))
        assert cur.fetchone()["r"] is None
        cur.execute("select count(*) n from task")
        assert cur.fetchone()["n"] == 0


def test_consultar_personas_devuelve_todos_los_que_coinciden(corework, conn):
    """Sin esta herramienta, el modelo enumera de memoria — y se equivoca.

    En la primera prueba real contestó que "Mar" era Marcos o Mariano, con la
    lista completa del equipo delante en su propio contexto. Martín Forte no
    apareció.
    """
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        r = H.ejecutar(cur, quien, "consultar_personas", {"nombre": "Mar"})

        assert sorted(p["nombre"] for p in r) == [
            "Marcos Tarquini", "Mariano Naim", "Martín Forte"]


def test_consultar_personas_sin_coincidencias_devuelve_vacio(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        assert H.ejecutar(cur, quien, "consultar_personas",
                          {"nombre": "Ronaldinho"}) == []


def test_consultar_personas_sin_filtro_lista_el_equipo(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        assert len(H.ejecutar(cur, quien, "consultar_personas", {})) == 7


# ---------------------------------------------------------------------------
# Resolver la ambigüedad antes de que el modelo hable
# ---------------------------------------------------------------------------

def test_el_contexto_avisa_que_un_nombre_del_mensaje_es_ambiguo(corework, conn):
    """La herramienta no alcanza: el modelo la llama a veces sí y a veces no.

    En dos corridas idénticas de la prueba real llamó `consultar_personas` una
    vez y la otra no, y sin ella se comió a Martín Forte. Esto no depende de
    que decida nada: los candidatos se resuelven con un select y le llegan ya
    en el contexto del turno.
    """
    from leda.contexto import construir

    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        ctx = construir(cur, quien, "creá una tarea, responsable Mar")

        assert "Marcos Tarquini" in ctx.sistema
        assert "Mariano Naim" in ctx.sistema
        assert "Martín Forte" in ctx.sistema
        assert "Mar" in ctx.sistema
        assert "ambiguo" in ctx.sistema.lower()


def test_un_nombre_sin_ambiguedad_no_agrega_ruido(corework, conn):
    from leda.contexto import construir

    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        ctx = construir(cur, quien, "creá una tarea para Nahuel")

        assert "ambiguo" not in ctx.sistema.lower()


def test_un_mensaje_sin_nombres_no_agrega_nada(corework, conn):
    from leda.contexto import construir

    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        ctx = construir(cur, quien, "cómo venimos con el tablero esta semana")

        assert "ambiguo" not in ctx.sistema.lower()


def test_contexto_expone_identidad_y_reloj_confiables(corework, conn):
    from leda.contexto import construir

    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        ctx = construir(cur, quien, "hola", ahora=AHORA)

        assert quien.nombre == "Ismael Soschinski"
        assert (
            "Su nombre verificado por la membresía es Ismael Soschinski"
            in ctx.sistema)
        assert "No le preguntes su nombre" in ctx.sistema
        assert "2026-07-27 10:00:00 -0300" in ctx.sistema
        assert "America/Argentina/Buenos_Aires" in ctx.sistema


# ---------------------------------------------------------------------------
# El circuito completo: el agente pregunta, la persona elige
# ---------------------------------------------------------------------------

def test_el_agente_legacy_no_puede_abrir_una_eleccion(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        obj = _objetivo(cur, ws)
        cal = Calendario.desde_base(cur, ws)

        guion = [
            Respuesta(llamadas=[Llamada("c1", "crear_tarea", {
                "titulo": "Relevar tablero", "objetivo_id": obj,
                "area_slug": "ot", "responsable": "Mar"})]),
            Respuesta(texto="No se registró la tarea."),
        ]
        r = responder(cur, quien, "creá una tarea para Mar",
                      ProveedorGuionado(guion), cal, chat_id=9000, ahora=AHORA)

        assert r.acciones == []
        assert r.texto == NO_EFFECT_STATUS
        cur.execute("select count(*) n from pending_action")
        assert cur.fetchone()["n"] == 0
        cur.execute("select count(*) n from task_draft")
        assert cur.fetchone()["n"] == 0


@pytest.fixture
def cliente(corework, conn, monkeypatch):
    monkeypatch.setattr(gateway, "acusar_toque", lambda *a, **k: None)
    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, webhook_secret="s3cr3t"))
    return TestClient(gateway.app)


def test_callback_legacy_crear_tarea_falla_cerrado(
        cliente, conn, corework):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        cur.execute("select membership_id m from integrante where nombre = %s",
                    ("Marcos Tarquini",))
        marcos = str(cur.fetchone()["m"])

        p = P.registrar(
            cur, quien, herramienta="crear_tarea",
            args={"titulo": "Relevar tablero", "objetivo_id": _objetivo(cur, ws),
                  "area_slug": "ot"},
            resumen="crear Relevar tablero",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=2),
            campo="responsable_membership_id",
            opciones=[("Marcos Tarquini", marcos)], chat_id=9000)
        token = P.opcion_por_etiqueta(cur, p.id, "Marcos Tarquini").token
        cur.execute("select telegram_user_id t from integrante where nombre = %s",
                    ("Ismael Soschinski",))
        tg = cur.fetchone()["t"]
    conn.commit()

    cliente.post("/telegram/corework",
                 json={"callback_query": {
                     "id": "cb1", "from": {"id": tg}, "data": f"p:{token}",
                     "message": {"message_id": 7, "chat": {"id": tg}}}},
                 headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})

    with admin(conn) as cur:
        cur.execute("select count(*) n from task_draft")
        assert cur.fetchone()["n"] == 0
        cur.execute("select count(*) n from task")
        assert cur.fetchone()["n"] == 0
        cur.execute("select estado from pending_action where id = %s", (p.id,))
        assert cur.fetchone()["estado"] == "resuelta"
