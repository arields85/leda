"""El estado real de una tarea tras "Pedir cambios" (R4-H8, ADR 0013 regla 3).

En la cuarta ronda por Telegram, después de que Ismael pidió cambios (con su
motivo), Ariel preguntó por su tarea y Leda contestó "sigue en curso… No tuvo
cambios de estado." -- falso, y sin el motivo que el menú de la misma tarea sí
muestra ("Cambios pedidos por …: …"). El servidor tiene que decir el estado real
sin depender de cómo lo redacte el modelo:

1. las lecturas de tareas traen los cambios pedidos vigentes, de la misma fuente
   que el menú (`menu_tarea.cambios_pedidos`);
2. si el turno resolvió UNA tarea clara y su motivo no aparece en la respuesta, el
   servidor agrega la línea del menú (se compara el dato guardado con el texto, no
   se buscan frases del modelo);
3. los botones de esa respuesta son de esa tarea, no la lista de todas.
"""

from __future__ import annotations

from datetime import datetime, timezone

from leda import herramientas as H
from leda.agente import responder
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.llm import Llamada, ProveedorGuionado, Respuesta

from tests.banco.corrida import sembrar_precondiciones
from tests.test_menu_tarea import _quien

MOTIVO = "falta la captura con la hora"
LINEA = f"Cambios pedidos por Marcos Tarquini: {MOTIVO}"
FALSO = "«Dashboard de lotes» sigue en curso, con fecha objetivo el 10/10. No tuvo cambios de estado."


def _sembrar(conn, ws, *, con_cambios=True):
    with admin(conn) as cur:
        tareas = [{"id": "t1", "titulo": "Dashboard de lotes", "area": "ot",
                   "responsable": "Nahuel Gimenez"},
                  {"id": "t2", "titulo": "Reporte semanal", "area": "ot",
                   "responsable": "Nahuel Gimenez"}]
        if con_cambios:
            tareas[0]["cambios_pedidos"] = {"por": "Marcos Tarquini",
                                            "motivo": MOTIVO}
        ids = sembrar_precondiciones(cur, ws, {"tareas": tareas})
    conn.commit()
    return ids


def _turno(conn, ws, guion, claras, texto="¿qué pasó con mi tarea?"):
    proveedor = ProveedorGuionado(guion=list(guion))
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, texto, proveedor, cal, chat_id=9005,
                  ahora=datetime.now(timezone.utc),
                  tareas_resueltas_claras=claras)
    conn.commit()
    with admin(conn) as cur:
        cur.execute(
            """select cuerpo, pending_action_id from message_outbox
                where workspace_id = %s and chat_id = 9005
               order by programado_para desc, dedupe_key desc limit 1""", (ws,))
        return cur.fetchone()


def _leer_y_responder(texto):
    return [Respuesta(llamadas=[Llamada("c1", "consultar_tareas",
                                        {"responsable": "Nahuel"})]),
            Respuesta(texto=texto)]


def _botones(conn, pending_action_id):
    with admin(conn) as cur:
        cur.execute("select etiqueta from pending_action_option "
                    "where pending_action_id = %s order by orden",
                    (pending_action_id,))
        return [f["etiqueta"] for f in cur.fetchall()]


# ---------------------------------------------------------------------------
# 1. La lectura trae los hechos
# ---------------------------------------------------------------------------

def test_consultar_tareas_trae_los_cambios_pedidos_vigentes(corework, conn):
    ws = corework.workspace_id
    ids = _sembrar(conn, ws)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        filas = {str(f["id"]): f for f in H.ejecutar(
            cur, quien, "consultar_tareas", {"responsable": "Nahuel"})}

    assert filas[ids["t1"]]["cambios_pedidos"] == LINEA
    assert "cambios_pedidos" not in filas[ids["t2"]]


def test_una_tarea_ya_reentregada_no_trae_cambios_pedidos(corework, conn):
    """El pedido deja de estar vigente cuando la tarea vuelve a revisión: la misma
    regla que el menú (`menu_tarea.cambios_pedidos`)."""
    ws = corework.workspace_id
    ids = _sembrar(conn, ws)
    with admin(conn) as cur:
        cur.execute("insert into task_state_event (task_id, estado_anterior, "
                    "estado_nuevo, actor_kind, at) values (%s, 'asignada', "
                    "'en_revision', 'sistema', clock_timestamp())", (ids["t1"],))
    conn.commit()

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        filas = {str(f["id"]): f for f in H.ejecutar(
            cur, quien, "consultar_tareas", {"responsable": "Nahuel"})}

    assert "cambios_pedidos" not in filas[ids["t1"]]


# ---------------------------------------------------------------------------
# 2. La garantía: el hecho sale aunque el modelo escriba otra cosa
# ---------------------------------------------------------------------------

def test_el_motivo_de_los_cambios_pedidos_se_agrega_si_la_respuesta_no_lo_dice(
        corework, conn):
    ws = corework.workspace_id
    ids = _sembrar(conn, ws)

    fila = _turno(conn, ws, _leer_y_responder(FALSO),
                  {ids["t1"]: "Dashboard de lotes"})

    assert LINEA in fila["cuerpo"]
    assert "sigue en curso" in fila["cuerpo"]          # el resto no se toca


def test_una_respuesta_que_ya_incluye_el_motivo_no_se_toca(corework, conn):
    ws = corework.workspace_id
    ids = _sembrar(conn, ws)
    dicho = ("«Dashboard de lotes» volvió a estar en curso: Marcos Tarquini pidió "
             f"cambios, {MOTIVO}.")

    fila = _turno(conn, ws, _leer_y_responder(dicho),
                  {ids["t1"]: "Dashboard de lotes"})

    assert "Cambios pedidos por" not in fila["cuerpo"]
    assert fila["cuerpo"].count(MOTIVO) == 1


def test_una_tarea_sin_cambios_pedidos_no_recibe_la_linea(corework, conn):
    ws = corework.workspace_id
    ids = _sembrar(conn, ws, con_cambios=False)

    fila = _turno(conn, ws, _leer_y_responder(FALSO),
                  {ids["t1"]: "Dashboard de lotes"})

    assert "Cambios pedidos" not in fila["cuerpo"]


def test_sin_una_tarea_clara_no_se_agrega_la_linea(corework, conn):
    """La guarda habla de la tarea que el turno resolvió clara: con ninguna, o con
    más de una, la persona no preguntó por una puntual."""
    ws = corework.workspace_id
    ids = _sembrar(conn, ws)

    ninguna = _turno(conn, ws, _leer_y_responder(FALSO), {})
    dos = _turno(conn, ws, _leer_y_responder(FALSO),
                 {ids["t1"]: "Dashboard de lotes", ids["t2"]: "Reporte semanal"})

    assert "Cambios pedidos" not in ninguna["cuerpo"]
    assert "Cambios pedidos" not in dos["cuerpo"]


# ---------------------------------------------------------------------------
# 3. Los botones son de la tarea de la que se habló
# ---------------------------------------------------------------------------

def test_con_una_tarea_clara_los_botones_son_los_de_esa_tarea(corework, conn):
    ws = corework.workspace_id
    ids = _sembrar(conn, ws)

    fila = _turno(conn, ws, _leer_y_responder(FALSO),
                  {ids["t1"]: "Dashboard de lotes"})

    etiquetas = _botones(conn, fila["pending_action_id"])
    assert any("Dashboard" in e for e in etiquetas)
    assert not any("Reporte" in e for e in etiquetas)


def test_sin_tarea_clara_la_lista_sigue_ofreciendo_todas(corework, conn):
    ws = corework.workspace_id
    _sembrar(conn, ws)

    fila = _turno(conn, ws, _leer_y_responder("Tenés dos tareas abiertas."), {})

    etiquetas = _botones(conn, fila["pending_action_id"])
    assert any("Dashboard" in e for e in etiquetas)
    assert any("Reporte" in e for e in etiquetas)


# ---------------------------------------------------------------------------
# 4. Ya dicho = el hecho entero (quién y el motivo completo), no un pedazo
# ---------------------------------------------------------------------------

def _sembrar_pedido(conn, ws, *, titulo, motivo, por="Marcos Tarquini"):
    with admin(conn) as cur:
        ids = sembrar_precondiciones(cur, ws, {"tareas": [{
            "id": "t1", "titulo": titulo, "area": "ot",
            "responsable": "Nahuel Gimenez",
            "cambios_pedidos": {"por": por, "motivo": motivo}}]})
    conn.commit()
    return ids


def test_un_motivo_de_una_palabra_que_aparece_de_casualidad_no_da_el_hecho_por_dicho(
        corework, conn):
    ws = corework.workspace_id
    ids = _sembrar_pedido(conn, ws, titulo="Dashboard de lotes", motivo="certificado")
    dicho = ("«Dashboard de lotes» sigue en curso, esperando el certificado del "
             "proveedor.")

    fila = _turno(conn, ws, _leer_y_responder(dicho),
                  {ids["t1"]: "Dashboard de lotes"})

    assert "Cambios pedidos por Marcos Tarquini: certificado" in fila["cuerpo"]


def test_un_motivo_que_es_un_pedazo_del_titulo_no_se_da_por_dicho(corework, conn):
    ws = corework.workspace_id
    ids = _sembrar_pedido(conn, ws, titulo="Certificado de calidad",
                          motivo="calidad")

    fila = _turno(conn, ws, _leer_y_responder("«Certificado de calidad» sigue en curso."),
                  {ids["t1"]: "Certificado de calidad"})

    assert "Cambios pedidos por Marcos Tarquini: calidad" in fila["cuerpo"]


def test_el_motivo_sin_quien_lo_pidio_no_alcanza(corework, conn):
    ws = corework.workspace_id
    ids = _sembrar(conn, ws)

    fila = _turno(conn, ws, _leer_y_responder(
        f"«Dashboard de lotes» sigue en curso: {MOTIVO}."),
        {ids["t1"]: "Dashboard de lotes"})

    assert LINEA in fila["cuerpo"]


def test_quien_y_el_motivo_completo_dichos_con_el_nombre_de_pila_no_se_repiten(
        corework, conn):
    ws = corework.workspace_id
    ids = _sembrar(conn, ws)
    dicho = f"«Dashboard de lotes» volvió a estar en curso: Marcos pidió {MOTIVO}."

    fila = _turno(conn, ws, _leer_y_responder(dicho),
                  {ids["t1"]: "Dashboard de lotes"})

    assert "Cambios pedidos por" not in fila["cuerpo"]


def test_un_motivo_largo_dicho_entero_no_se_repite(corework, conn):
    """El motivo del menú se acota con "…"; la comparación usa el completo."""
    ws = corework.workspace_id
    largo = ("falta la captura del tablero con la hora visible y el certificado "
             "de calibración firmado por el proveedor de la planta norte, más el "
             "informe de la prueba de aceptación en sitio")
    ids = _sembrar_pedido(conn, ws, titulo="Dashboard de lotes", motivo=largo)
    dicho = f"«Dashboard de lotes» sigue en curso. Marcos Tarquini pidió: {largo}."

    fila = _turno(conn, ws, _leer_y_responder(dicho),
                  {ids["t1"]: "Dashboard de lotes"})

    assert "Cambios pedidos por" not in fila["cuerpo"]


# ---------------------------------------------------------------------------
# 5. Idempotencia y bordes de la guarda (revisión review-167e3c98261bbc91)
# ---------------------------------------------------------------------------

def _guarda(conn, ws, claras, texto):
    from leda.agente import _cambios_pedidos_sin_mencionar

    with espacio(conn, ws) as cur:
        return _cambios_pedidos_sin_mencionar(cur, texto, claras)


def test_aplicar_la_guarda_dos_veces_con_un_motivo_largo_da_lo_mismo(corework, conn):
    """La línea que agrega lleva el motivo acotado con puntos suspensivos: la
    segunda aplicación tiene que reconocerla, no agregarla otra vez."""
    from leda.menu_tarea import LIMITE_MOTIVO_CAMBIOS

    ws = corework.workspace_id
    motivo = "falta el detalle de la captura " * 20
    assert len(motivo) > LIMITE_MOTIVO_CAMBIOS
    ids = _sembrar_pedido(conn, ws, titulo="Dashboard de lotes", motivo=motivo)
    claras = {ids["t1"]: "Dashboard de lotes"}

    una = _guarda(conn, ws, claras, FALSO)
    dos = _guarda(conn, ws, claras, una)

    assert "Cambios pedidos por Marcos Tarquini" in una
    assert dos == una


def test_aplicar_la_guarda_dos_veces_con_el_titulo_dentro_del_motivo_da_lo_mismo(
        corework, conn):
    ws = corework.workspace_id
    ids = _sembrar_pedido(conn, ws, titulo="Dashboard de lotes",
                          motivo="el Dashboard de lotes no muestra el turno noche")
    claras = {ids["t1"]: "Dashboard de lotes"}

    una = _guarda(conn, ws, claras, FALSO)
    dos = _guarda(conn, ws, claras, una)

    assert "Cambios pedidos por Marcos Tarquini" in una
    assert dos == una


def test_quien_pidio_los_cambios_con_un_nombre_en_blanco_no_rompe_la_guarda(
        monkeypatch):
    from leda import menu_tarea
    from leda.agente import _cambios_pedidos_sin_mencionar

    pedido = menu_tarea.CambiosPedidos(
        motivo=MOTIVO, linea=f"Cambios pedidos por    : {MOTIVO}", por="   ",
        completo=MOTIVO)
    monkeypatch.setattr(menu_tarea, "cambios_pedidos_vigentes",
                        lambda cur, tarea_id: pedido)

    salida = _cambios_pedidos_sin_mencionar(
        None, "«Dashboard de lotes» sigue en curso.", {"t1": "Dashboard de lotes"})

    assert MOTIVO in salida
