"""Una lista de hasta tres tareas las nombra en el texto (T10-5, R3-H3 y R3-H7).

Regla del usuario (H7): con hasta 3 tareas, el texto de la respuesta las nombra
enteras; con más, resume y los nombres quedan en los botones. Siempre igual: el
modelo alterna, así que lo garantiza el servidor (ADR 0013, reglas generales) con
la misma técnica que `_nombrar_tareas_sin_mencionar` -- se comprueba contra las
tareas que las lecturas trajeron en el turno, no contra palabras del modelo.
Cada nombre que el servidor agrega lleva su estado (H3), así "una asignada y la
otra en curso" nunca queda sin decir cuál es cuál.
"""

from __future__ import annotations

from datetime import datetime, timezone

from prisma import contexto
from prisma.agente import MAX_TAREAS_NOMBRADAS, _nombrar_tareas_listadas, responder
from prisma.calendario import Calendario
from prisma.db import admin, espacio
from prisma.llm import Llamada, Respuesta
from tests.test_lista_botones import (_con_proveedor, _quien, _tarea,
                                      _tareas_en_orden)


def _fila(titulo, estado="asignada", n=1):
    return {"id": f"id-{n}", "titulo": titulo, "estado": estado}


# ---------------------------------------------------------------------------
# La guarda, sin base
# ---------------------------------------------------------------------------

def test_el_limite_de_la_regla_es_de_tres_tareas():
    assert MAX_TAREAS_NOMBRADAS == 3


def test_una_tarea_sin_nombrar_se_nombra_con_su_estado():
    salida = _nombrar_tareas_listadas(
        "Tenés una tarea abierta.", [_fila("Revisar variador", "en_curso")])
    assert salida == "«Revisar variador» (en curso)\n\nTenés una tarea abierta."


def test_dos_y_tres_tareas_sin_nombrar_salen_todas_con_su_estado_en_orden():
    filas = [_fila("Cablear tablero", "asignada", 1),
             _fila("Revisar variador", "en_curso", 2),
             _fila("Calibrar sensor", "bloqueada", 3)]
    salida = _nombrar_tareas_listadas("Tenés tres tareas.", filas[:2])
    assert salida.split("\n\n")[0].split("\n") == [
        "«Cablear tablero» (asignada)", "«Revisar variador» (en curso)"]
    salida = _nombrar_tareas_listadas("Tenés tres tareas.", filas)
    assert salida.split("\n\n")[0].split("\n") == [
        "«Cablear tablero» (asignada)", "«Revisar variador» (en curso)",
        "«Calibrar sensor» (bloqueada)"]
    assert salida.endswith("\n\nTenés tres tareas.")


def test_h3_una_lista_sin_decir_cual_es_cual_queda_atada_a_los_nombres():
    salida = _nombrar_tareas_listadas(
        "Tenés dos: una todavía asignada y la otra ya en curso.",
        [_fila("Cablear tablero", "asignada", 1),
         _fila("Revisar variador", "en_curso", 2)])
    assert "«Cablear tablero» (asignada)" in salida
    assert "«Revisar variador» (en curso)" in salida


def test_solo_se_agregan_las_que_faltan():
    filas = [_fila("Cablear tablero", "asignada", 1),
             _fila("Revisar variador", "en_curso", 2)]
    salida = _nombrar_tareas_listadas(
        "Tenés cablear tablero para arrancar y otra más.", filas)
    assert salida.startswith("«Revisar variador» (en curso)\n\n")
    assert "«Cablear tablero» (asignada)" not in salida


def test_la_respuesta_que_ya_las_nombra_a_todas_no_se_toca():
    filas = [_fila("Cablear tablero", "asignada", 1),
             _fila("Revisar variador", "en_curso", 2)]
    texto = "Tenés «Cablear tablero» asignada y Revisar Variador en curso."
    assert _nombrar_tareas_listadas(texto, filas) == texto


def test_no_distingue_mayusculas_ni_acentos_al_buscar_el_titulo():
    fila = _fila("Revisar la calibración")
    texto = "Está pendiente REVISAR LA CALIBRACIÓN."
    assert _nombrar_tareas_listadas(texto, [fila]) == texto
    texto = "Está pendiente revisar la calibracion."
    assert _nombrar_tareas_listadas(texto, [fila]) == texto


def test_con_mas_de_tres_tareas_el_texto_no_se_toca():
    filas = [_fila(f"Tarea {n}", n=n) for n in range(1, 5)]
    assert _nombrar_tareas_listadas("Tenés cuatro tareas.", filas) == \
        "Tenés cuatro tareas."


def test_sin_tareas_listadas_el_texto_no_se_toca():
    assert _nombrar_tareas_listadas("Hola.", []) == "Hola."


def test_aplicarla_dos_veces_no_duplica_nada():
    filas = [_fila("Cablear tablero", "asignada", 1),
             _fila("Revisar variador", "en_curso", 2)]
    una = _nombrar_tareas_listadas("Tenés dos.", filas)
    assert _nombrar_tareas_listadas(una, filas) == una


def test_el_estado_desconocido_no_rompe():
    salida = _nombrar_tareas_listadas("Hay una.", [{"id": "x", "titulo": "Algo"}])
    assert salida.startswith("«Algo» (sin estado)")


# ---------------------------------------------------------------------------
# Por el turno real
# ---------------------------------------------------------------------------

def _responder(conn, ws, monkeypatch, texto_del_modelo):
    proveedor = _con_proveedor(monkeypatch, [
        Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
        Respuesta(texto=texto_del_modelo)])
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        return responder(cur, quien, "qué tengo pendiente", proveedor,
                         Calendario.desde_base(cur, ws), chat_id=1,
                         ahora=datetime.now(timezone.utc))


def test_el_turno_con_tres_tareas_las_nombra_aunque_el_modelo_solo_las_cuente(
        conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Cablear tablero", estado="asignada",
               dias_para_vencer=1)
        _tarea(cur, ws, titulo="Revisar variador", estado="en_curso",
               dias_para_vencer=2)
        _tarea(cur, ws, titulo="Calibrar sensor", estado="bloqueada",
               dias_para_vencer=3)
    conn.commit()

    r = _responder(conn, ws, monkeypatch, "Tenés 3 tareas abiertas.")

    assert r.texto == ("«Cablear tablero» (asignada)\n"
                       "«Revisar variador» (en curso)\n"
                       "«Calibrar sensor» (bloqueada)\n\n"
                       "Tenés 3 tareas abiertas.")


def test_el_turno_con_tareas_ya_nombradas_queda_como_lo_escribio_el_modelo(
        conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Cablear tablero", estado="asignada",
               dias_para_vencer=1)
        _tarea(cur, ws, titulo="Revisar variador", estado="en_curso",
               dias_para_vencer=2)
    conn.commit()
    texto = ("Tenés «Cablear tablero» (todavía asignada) y «Revisar variador» "
             "(ya en curso).")

    assert _responder(conn, ws, monkeypatch, texto).texto == texto


def test_el_turno_con_mas_de_tres_tareas_resume_y_los_nombres_quedan_en_los_botones(
        conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tareas_en_orden(cur, ws, 4)
    conn.commit()

    r = _responder(conn, ws, monkeypatch, "Tenés 4 tareas abiertas.")

    assert r.texto == "Tenés 4 tareas abiertas."
    with admin(conn) as cur:
        cur.execute(
            """select o.etiqueta from pending_action_option o
                 join pending_action p on p.id = o.pending_action_id
                where p.workspace_id = %s order by o.orden""", (ws,))
        etiquetas = [f["etiqueta"] for f in cur.fetchall()]
    assert all(any(f"Tarea {n}" in e for e in etiquetas) for n in range(1, 5))


# ---------------------------------------------------------------------------
# El preámbulo dice la misma regla (H7) y responder lo pedido (H12)
# ---------------------------------------------------------------------------

def test_el_preambulo_dice_la_regla_h7_y_solo_prohibe_enumerar_desde_cuatro():
    texto = " ".join(contexto.PREAMBULO.lower().split())
    assert "hasta tres tareas, nombralas enteras" in texto
    assert "con más de tres, no las enumeres" in texto
    assert "no las enumeres una por una" not in texto
    assert "nombres quedan en los botones" in texto


def test_el_preambulo_pide_responder_lo_pedido_sin_estado_no_pedido():
    texto = " ".join(contexto.PREAMBULO.lower().split())
    assert "sólo lo que te preguntaron" in texto
    assert "no pedido" in texto
