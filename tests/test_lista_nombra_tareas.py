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

from leda import contexto
from leda.agente import MAX_TAREAS_NOMBRADAS, _nombrar_tareas_listadas, responder
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.llm import Llamada, Respuesta
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


def test_si_el_turno_resolvio_una_tarea_puntual_la_respuesta_no_es_una_lista():
    """Si la persona preguntó por una tarea concreta (el turno la resolvió
    clara), la respuesta es sobre esa tarea aunque la lectura haya traído otras:
    agregar las demás sería información no pedida (H12). La nombra
    `_nombrar_tareas_sin_mencionar`; la guarda de listas no se mete."""
    filas = [_fila("Cablear tablero", "asignada", 1),
             _fila("Revisar variador", "en_curso", 2),
             _fila("Calibrar sensor", "bloqueada", 3)]
    texto = "Está asignada; arrancala cuando puedas."
    assert _nombrar_tareas_listadas(
        texto, filas, tareas_resueltas_claras={"id-1": "Cablear tablero"}) == texto


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


# ---------------------------------------------------------------------------
# Sólo toca una respuesta informativa (revisión review-5e28a95f618e8212, 1)
# ---------------------------------------------------------------------------

def _dos_tareas(conn, ws):
    with admin(conn) as cur:
        t1 = _tarea(cur, ws, titulo="Cablear tablero", estado="asignada",
                    dias_para_vencer=1)
        _tarea(cur, ws, titulo="Revisar variador", estado="en_curso",
               dias_para_vencer=2)
    conn.commit()
    return t1


def _turno_con_guion(conn, ws, monkeypatch, guion, **kwargs):
    proveedor = _con_proveedor(monkeypatch, guion)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        return responder(cur, quien, "qué tengo pendiente", proveedor,
                         Calendario.desde_base(cur, ws), chat_id=1,
                         ahora=datetime.now(timezone.utc), **kwargs)


def test_un_turno_sin_efecto_no_antepone_filas_a_la_respuesta_reescrita(
        conn, corework, monkeypatch):
    """El turno leyó tareas pero además intentó un cambio que no se aplicó: la
    respuesta es el aviso "sin cambios", no una lista."""
    from leda.agente import NoProponer
    from leda.salida import NO_EFFECT_STATUS
    ws = corework.workspace_id
    tid = _dos_tareas(conn, ws)
    guion = [
        Respuesta(llamadas=[
            Llamada("c1", "consultar_tareas", {}),
            Llamada("c2", "registrar_bloqueo",
                    {"tarea_id": tid, "causa": "falta el switch"})]),
        Respuesta(texto="Listo, quedó registrado."),
        Respuesta(texto="No se hizo ningún cambio.")]

    r = _turno_con_guion(conn, ws, monkeypatch, guion, no_proponer=NoProponer(
        "registrar_bloqueo", "tarea_id", tid, dejado="el bloqueo"))

    assert r.texto == f"No se hizo ningún cambio\n\n{NO_EFFECT_STATUS}"


def test_un_turno_que_termina_en_vista_previa_no_recibe_filas(
        conn, corework, monkeypatch):
    ws = corework.workspace_id
    tid = _dos_tareas(conn, ws)
    guion = [
        Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
        Respuesta(llamadas=[Llamada("c2", "actualizar_estado",
                                    {"tarea_id": tid, "estado": "en_curso"})]),
        Respuesta(texto="Listo.")]

    r = _turno_con_guion(conn, ws, monkeypatch, guion)

    assert r.confirmaciones == ["actualizar_estado"]
    assert r.texto == ""


def test_un_turno_que_ofrece_opciones_no_recibe_filas(conn, corework, monkeypatch):
    ws = corework.workspace_id
    _dos_tareas(conn, ws)
    guion = [
        Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
        Respuesta(texto="Tenés dos tareas.", llamadas=[Llamada(
            "c2", "ofrecer_opciones", {
                "pregunta": "¿Cuál preferís?",
                "opciones": [{"texto": "Cablear tablero"},
                             {"texto": "Revisar variador"}]})])]

    r = _turno_con_guion(conn, ws, monkeypatch, guion)

    assert r.elecciones == ["ofrecer_opciones"]
    assert r.texto == "Tenés dos tareas."


def test_un_turno_que_no_cierra_no_recibe_filas(conn, corework, monkeypatch):
    from leda.agente import INCOMPLETO, MAX_VUELTAS
    ws = corework.workspace_id
    _dos_tareas(conn, ws)
    guion = [Respuesta(texto="Sigo.", llamadas=[Llamada(f"c{n}", "consultar_tareas", {})])
             for n in range(MAX_VUELTAS)]

    r = _turno_con_guion(conn, ws, monkeypatch, guion)

    assert r.texto == INCOMPLETO


def test_un_turno_con_incidente_no_recibe_filas(conn, corework, monkeypatch):
    from leda.agente import DISCULPA
    ws = corework.workspace_id
    _dos_tareas(conn, ws)
    guion = [Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})])]

    class _Cae(type(_con_proveedor(monkeypatch, []))):
        def responder(self, sistema, mensajes, herramientas):
            if len(self.recibidos) >= 1:
                raise RuntimeError("el proveedor no respondió")
            return super().responder(sistema, mensajes, herramientas)

    proveedor = _Cae(guion=guion)
    monkeypatch.setattr("leda.llm.desde_base", lambda cur, ws, key: proveedor)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = responder(cur, quien, "qué tengo pendiente", proveedor,
                      Calendario.desde_base(cur, ws), chat_id=1,
                      ahora=datetime.now(timezone.utc))

    assert r.texto == DISCULPA


# ---------------------------------------------------------------------------
# Coincidencia de títulos por título entero (revisión, 2)
# ---------------------------------------------------------------------------

def test_un_titulo_que_es_fragmento_de_otro_listado_no_se_da_por_nombrado():
    filas = [_fila("Revisar variador", n=1), _fila("Revisar variador 2", n=2)]
    salida = _nombrar_tareas_listadas("Sólo va bien Revisar variador 2.", filas)
    assert salida.startswith("«Revisar variador» (asignada)\n\n")
    assert "«Revisar variador 2»" not in salida


def test_ambos_nombrados_no_agrega_nada_aunque_uno_contenga_al_otro():
    filas = [_fila("Revisar variador", n=1), _fila("Revisar variador 2", n=2)]
    texto = "Van Revisar variador 2 y también revisar variador."
    assert _nombrar_tareas_listadas(texto, filas) == texto


def test_un_titulo_dentro_de_otras_palabras_no_cuenta_como_nombrado():
    fila = _fila("Cable")
    salida = _nombrar_tareas_listadas("Hay que cablear el tablero.", [fila])
    assert salida.startswith("«Cable» (asignada)")
    salida = _nombrar_tareas_listadas("Falta el cable del tablero.", [fila])
    assert salida == "Falta el cable del tablero."


def test_un_titulo_vacio_no_cuenta_como_nombrado_ni_produce_fila():
    filas = [_fila("", n=1), _fila("   ", n=2), _fila("Cablear tablero", n=3)]
    salida = _nombrar_tareas_listadas("Tenés tres.", filas)
    assert salida == "«Cablear tablero» (asignada)\n\nTenés tres."
    assert _nombrar_tareas_listadas("Tenés una.", filas[:2]) == "Tenés una."


def test_sobre_la_tarea_resuelta_exige_el_titulo_entero():
    from leda.agente import _nombrar_tareas_sin_mencionar
    salida = _nombrar_tareas_sin_mencionar(
        "Sólo va bien Revisar variador 2.",
        {"a": "Revisar variador", "b": "Revisar variador 2"})
    assert salida.startswith("Sobre «Revisar variador»:\n\n")
    assert "Sobre «Revisar variador 2»" not in salida
    salida = _nombrar_tareas_sin_mencionar(
        "Va bien el revariador.", {"a": "variador"})
    assert salida.startswith("Sobre «variador»:\n\n")
    texto = "Sólo va bien Revisar variador."
    assert _nombrar_tareas_sin_mencionar(texto, {"a": "Revisar variador"}) == texto
    assert _nombrar_tareas_sin_mencionar(texto, {"a": ""}) == texto


# ---------------------------------------------------------------------------
# Las filas pasan por los mismos filtros de salida (revisión, 3) y el texto
# vacío no deja un párrafo en blanco (revisión, 4)
# ---------------------------------------------------------------------------

def test_las_filas_del_servidor_pasan_por_el_glosario_de_salida(
        conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Revisar corelab", estado="asignada",
               dias_para_vencer=1)
    conn.commit()

    r = _responder(conn, ws, monkeypatch, "Tenés 1 tarea abierta.")

    assert r.texto == "«Revisar CoreLabs» (asignada)\n\nTenés 1 tarea abierta."


def test_un_texto_vacio_no_deja_un_parrafo_en_blanco():
    assert _nombrar_tareas_listadas("", [_fila("Cablear tablero")]) == \
        "«Cablear tablero» (asignada)"
