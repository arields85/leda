"""Respuestas que nombran la tarea por su título (T5, `aclaracion-con-
botones`; ADR 0006, "las consultas no pasan por vista previa: toda respuesta
nombra la tarea por su título, para que la persona note si Prisma entendió
otra cosa").

La instrucción vive en el sistema (`contexto.py`, `gateway.
_bloque_contexto_referencias`), pero un prompt no es garantía: estas pruebas
cubren la protección determinística de `agente.responder` -- comprueba,
después de que el modelo cerró el turno con una respuesta visible, que esa
respuesta nombra por su título exacto cada tarea que este turno resolvió
CLARA (`tareas_resueltas_claras`, id de tarea → título -- el mismo dato que
arma `gateway._avanzar_aclaracion` a partir de `_ReferenciasResueltas.
titulos_resueltas` de T3/T4).

Revisión del orquestador sobre la primera versión de esta unidad: la
condición original exigía además que `consultar_tareas` hubiera devuelto la
tarea en el mismo turno -- una respuesta armada con otro contexto (p. ej. el
bloque de "tareas abiertas" que ya trae `contexto.construir`) quedaba sin
proteger. La comprobación ya no depende de qué herramienta corrió, ni de que
haya corrido alguna. Sin red ni modelo real: proveedor guionado, como el
resto de `tests/test_agente.py`.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from prisma.agente import responder
from prisma.autoridad import Canal, identificar
from prisma.calendario import Calendario
from prisma.db import admin, espacio
from prisma.llm import Llamada, ProveedorGuionado, Respuesta

BA = ZoneInfo("America/Argentina/Buenos_Aires")
AHORA = datetime(2026, 7, 27, 10, 0, tzinfo=BA)


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _tarea(cur, ws, titulo="Cablear tablero máq. 3", area="ot",
          persona="Marcos Tarquini"):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', 'Objetivo de prueba') returning id""", (ws,))
    obj = cur.fetchone()["id"]
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, fecha_objetivo,
                             criterio_aceptacion, evidencia_requerida)
           values (%s, %s, %s,
                   (select id from area where workspace_id = %s and slug = %s),
                   (select m.id from membership m join app_user u on u.id = m.app_user_id
                     where m.workspace_id = %s and u.nombre = %s),
                    '2026-08-14', 'Criterio de prueba', array['explicacion'])
           returning id""",
        (ws, obj, titulo, ws, area, ws, persona))
    t = cur.fetchone()["id"]
    cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                "values (%s, 'asignada', 'prisma')", (t,))
    return str(t)


def test_titulo_ausente_sin_llamar_a_ninguna_herramienta_se_antepone(corework, conn):
    """El caso que motivó la revisión: el modelo cierra el turno con texto
    propio -- sin llamar a ninguna herramienta -- y no nombra la tarea que
    este turno resolvió CLARA. La protección tiene que actuar igual."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Cablear tablero máq. 3")

    guion = [Respuesta(texto="Va bien, avanza rápido.")]
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "¿cómo va lo del tablero?",
                      ProveedorGuionado(guion), cal, chat_id=9106, ahora=AHORA,
                      tareas_resueltas_claras={tid: "Cablear tablero máq. 3"})

        assert r.texto == "Sobre «Cablear tablero máq. 3»:\n\nVa bien, avanza rápido."
        cur.execute("select cuerpo from message_outbox "
                    "where destinatario_membership_id = %s", (quien.membership_id,))
        assert cur.fetchone()["cuerpo"] == r.texto


def test_titulo_ausente_con_una_herramienta_distinta_igual_se_antepone(corework, conn):
    """Sigue sin importar qué herramienta corrió: acá el modelo consulta
    personas, no la tarea, y aun así la respuesta tiene que nombrarla."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Cablear tablero máq. 3")

    guion = [
        Respuesta(llamadas=[Llamada("c1", "consultar_personas", {})]),
        Respuesta(texto="Va bien, avanza rápido."),
    ]
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "¿cómo va lo del tablero?",
                      ProveedorGuionado(guion), cal, chat_id=9101, ahora=AHORA,
                      tareas_resueltas_claras={tid: "Cablear tablero máq. 3"})

        assert r.texto == "Sobre «Cablear tablero máq. 3»:\n\nVa bien, avanza rápido."


def test_titulo_presente_con_otra_forma_no_se_toca(corework, conn):
    """Distinta mayúscula y sin el acento de «máq.»: sigue siendo el mismo
    título, así que no hace falta anteponer nada."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Cablear tablero máq. 3")

    guion = [Respuesta(texto="Avance de CABLEAR TABLERO maq. 3: bien, sin bloqueos.")]
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "¿cómo va lo del tablero?",
                      ProveedorGuionado(guion), cal, chat_id=9102, ahora=AHORA,
                      tareas_resueltas_claras={tid: "Cablear tablero máq. 3"})

        assert r.texto == "Avance de CABLEAR TABLERO maq. 3: bien, sin bloqueos."
        assert "Sobre «" not in r.texto


def test_sin_referencia_resuelta_no_se_toca(corework, conn):
    """Sin `tareas_resueltas_claras` (el default), la guarda de T5 no antepone
    ningún "Sobre «...»:". (La lista de una sola tarea sí se nombra: T10-5, H7.)"""
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Cablear tablero máq. 3")

    guion = [
        Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
        Respuesta(texto="Va bien, avanza rápido."),
    ]
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "¿qué tengo?", ProveedorGuionado(guion), cal,
                      chat_id=9103, ahora=AHORA)

        assert r.texto == ("«Cablear tablero máq. 3» (asignada)\n\n"
                           "Va bien, avanza rápido.")


def test_herramienta_de_escritura_con_vista_previa_no_se_toca(corework, conn):
    """Una vista previa (Confirmar/Modificar/Cancelar) nunca lleva la línea
    de T5: el texto que sale es el resumen de la vista previa de siempre, y
    lo que devuelve `agente.responder` es vacío -- no hay respuesta visible
    del modelo sobre la que anteponer nada."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Cablear tablero máq. 3")

    guion = [
        Respuesta(llamadas=[Llamada("c1", "actualizar_estado",
                                    {"tarea_id": tid, "estado": "en_curso"})]),
        Respuesta(texto="Listo."),
    ]
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "arranco con esto", ProveedorGuionado(guion),
                      cal, chat_id=9104, ahora=AHORA,
                      tareas_resueltas_claras={tid: "Cablear tablero máq. 3"})

        assert r.texto == ""
        assert r.confirmaciones == ["actualizar_estado"]
        cur.execute("select cuerpo from message_outbox "
                    "where destinatario_membership_id = %s", (quien.membership_id,))
        cuerpo = cur.fetchone()["cuerpo"]
        assert "Sobre «" not in cuerpo


def test_dos_tareas_resueltas_una_ausente_nombra_sólo_esa(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        t1 = _tarea(cur, ws, titulo="Cablear tablero máq. 3")
        t2 = _tarea(cur, ws, titulo="Revisar tablero máq. 4")

    guion = [Respuesta(texto="Revisar tablero máq. 4 sigue en curso, sin novedades.")]
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "¿cómo van las dos del tablero?",
                      ProveedorGuionado(guion), cal, chat_id=9105, ahora=AHORA,
                      tareas_resueltas_claras={
                          t1: "Cablear tablero máq. 3",
                          t2: "Revisar tablero máq. 4"})

        assert r.texto == (
            "Sobre «Cablear tablero máq. 3»:\n\n"
            "Revisar tablero máq. 4 sigue en curso, sin novedades.")


# ---------------------------------------------------------------------------
# T10-5c: seguimientos de review-eca94d14a705c5c4 sobre las guardas de nombres
# ---------------------------------------------------------------------------

import subprocess
import sys

from prisma.agente import (_nombrar_tareas_listadas, _nombrar_tareas_sin_mencionar,
                           _titulos_nombrados)


def test_un_titulo_con_enfasis_o_formato_pegado_cuenta_como_nombrado():
    """El texto visible pierde `**`, `*` y las comillas invertidas
    (`contexto._sin_markdown`); el guión bajo queda literal y NO es parte del
    título: `_Revisar variador_` nombra la tarea. Se compara contra la misma forma
    normalizada, no contra el texto crudo del modelo."""
    claras = {"t1": "Revisar variador"}
    for texto in ("Sobre _Revisar variador_ va bien.",
                  "Sobre __Revisar variador__ va bien.",
                  "Sobre **Revisar variador** va bien.",
                  "Sobre *Revisar variador*: va bien.",
                  "Sobre `Revisar variador`, va bien.",
                  "Sobre _*Revisar variador*_. Va bien.",
                  "va bien_Revisar variador_"):
        assert _nombrar_tareas_sin_mencionar(texto, claras) == texto, texto
    listadas = [{"id": "t1", "titulo": "Revisar variador", "estado": "asignada"}]
    assert (_nombrar_tareas_listadas("Tenés _Revisar variador_.", listadas)
            == "Tenés _Revisar variador_.")


def test_un_titulo_con_guion_bajo_propio_se_sigue_encontrando():
    claras = {"t1": "Ajustar PLC_2"}
    assert _nombrar_tareas_sin_mencionar("Sobre Ajustar PLC_2 va bien.",
                                         claras) == "Sobre Ajustar PLC_2 va bien."
    assert _nombrar_tareas_sin_mencionar("Sobre otra cosa.", claras).startswith(
        "Sobre «Ajustar PLC_2»:")


def test_titulos_de_igual_largo_que_se_pisan_se_resuelven_en_orden_estable():
    """Con igual largo, el orden entre títulos no puede depender del hash del
    conjunto: se desempata por el título. "aaa bbb" y "bbb ccc" se pisan en "bbb":
    el primero por orden alfabético consume la aparición."""
    assert _titulos_nombrados("aaa bbb ccc", ["bbb ccc", "aaa bbb"]) == {"aaa bbb"}
    codigo = ("from prisma.agente import _titulos_nombrados as f\n"
              "print(sorted(f('aaa bbb ccc', ['bbb ccc', 'aaa bbb', 'ccc ddd'])))")
    salidas = set()
    for semilla in range(8):
        r = subprocess.run(
            [sys.executable, "-c", codigo], capture_output=True, text=True,
            env={**__import__("os").environ, "PYTHONHASHSEED": str(semilla)})
        assert r.returncode == 0, r.stderr
        salidas.add(r.stdout.strip())
    assert salidas == {"['aaa bbb']"}


def test_texto_vacio_deja_el_encabezado_sin_parrafo_final():
    assert (_nombrar_tareas_sin_mencionar("", {"t1": "Revisar variador"})
            == "Sobre «Revisar variador»:")
    assert (_nombrar_tareas_sin_mencionar("  \n", {"t1": "Revisar variador"})
            == "Sobre «Revisar variador»:")


def _ofrecer(texto=None):
    return Respuesta(texto=texto, llamadas=[Llamada("c1", "ofrecer_opciones", {
        "pregunta": "¿Cuál preferís?",
        "opciones": [{"texto": "A"}, {"texto": "B"}]})])


def test_la_rama_de_opciones_nombra_la_tarea_una_vez_y_filtra_el_encabezado(
        corework, conn):
    """`ofrecer_opciones` con una tarea resuelta clara: el encabezado se antepone
    ANTES de los filtros de salida (el formato del título sale como en cualquier
    texto visible) y no se duplica."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "algo",
                      ProveedorGuionado([_ofrecer("Elegí cómo seguimos.")]), cal,
                      chat_id=9201, ahora=AHORA,
                      tareas_resueltas_claras={"t1": "Cablear **tablero** 3"})
        assert r.elecciones == ["ofrecer_opciones"]
        assert r.texto == "Sobre «Cablear tablero 3»:\n\nElegí cómo seguimos."
        assert r.texto.count("Sobre «") == 1


def test_la_rama_de_opciones_no_repite_un_titulo_ya_nombrado(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "algo",
                      ProveedorGuionado([_ofrecer("Sobre _Cablear tablero_: elegí.")]),
                      cal, chat_id=9202, ahora=AHORA,
                      tareas_resueltas_claras={"t1": "Cablear tablero"})
        assert "Sobre «" not in r.texto
        assert r.texto.count("ablear tablero") == 1


def test_la_rama_de_opciones_sin_texto_no_deja_parrafo_vacio(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "algo", ProveedorGuionado([_ofrecer()]), cal,
                      chat_id=9203, ahora=AHORA,
                      tareas_resueltas_claras={"t1": "Cablear tablero"})
        assert r.texto == "Sobre «Cablear tablero»:"
