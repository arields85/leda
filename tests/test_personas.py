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

import pytest

from leda import herramientas as H
from leda.autoridad import Canal, identificar
from leda.db import espacio


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
