"""Una rama se cierra cuando su flujo termina (R4-H7, ADR 0013 regla 1).

En la cuarta ronda por Telegram los avisos que inicia Prisma ("X entregó…", "X
pidió cambios…") quedaron `listo` sin enviarse y los flujos ya terminados dejaban
su pregunta en `esperando` (`_opciones_modelo` de una respuesta con pregunta
abierta, `_dato_menu_tarea` de "Pedir cambios" y de "Ya la terminé"). Estas
pruebas recorren la ronda por el webhook real (`POST /telegram/corework`), con
proveedores guionados, y después corren una pasada del despachador en horario
laboral con un transporte de prueba: el aviso tiene que SALIR aunque quien lo
recibe haya escrito o tocado algo hace segundos, y de su flujo no puede quedar
ninguna pregunta `esperando`.

Además hay una prueba unitaria por cada tipo de pendiente que un flujo puede
dejar abierto, y la de qué es y qué no es una rama para lo que llega sin que la
persona lo haya pedido (el aviso con sus propios botones).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from prisma import pendientes as P
from prisma.calendario import Calendario
from prisma.db import admin, espacio
from prisma.despachador import TransporteDePrueba, despachar
from prisma.llm import Llamada, ProveedorGuionado, Respuesta
from prisma.salida import enqueue_outbox

from tests.test_pedir_cambios_extremo_a_extremo import (  # noqa: F401
    _abrir_menu, _confirmar, _mensaje, _opciones, _pendiente, _quien, _tarea,
    _tg, _tocar, _tocar_etiqueta, cliente)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _guion(monkeypatch, *respuestas) -> ProveedorGuionado:
    proveedor = ProveedorGuionado(guion=list(respuestas))
    monkeypatch.setattr("prisma.llm.desde_base", lambda cur, ws, key: proveedor)
    return proveedor


def _en_horario(conn, ws) -> datetime:
    """Un `ahora` de la pasada dentro de la jornada. El webhook escribe con el
    reloj real, así que se corre la línea de tiempo de lo que ya escribió hasta
    ese `ahora`: las distancias entre la actividad de la persona, los avisos y sus
    vencimientos son las mismas que tuvo la ronda; sólo cambia la hora del día."""
    real = datetime.now(timezone.utc)
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
    ahora = cal.dentro_de_jornada(real + timedelta(seconds=5))
    delta = ahora - real
    with admin(conn) as cur:
        cur.execute("update inbound_message set at = at + %s where workspace_id = %s",
                    (delta, ws))
        cur.execute(
            """update message_outbox
                  set programado_para = programado_para + %(d)s,
                      vence_en = vence_en + %(d)s
                where workspace_id = %(ws)s""", {"d": delta, "ws": ws})
        cur.execute(
            """update pending_action set vence_en = vence_en + %(d)s
                where workspace_id = %(ws)s""", {"d": delta, "ws": ws})
    conn.commit()
    return ahora


def _pasada(conn, ws, ahora):
    transporte = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        resumen = despachar(cur, ws, transporte, cal, ahora)
    conn.commit()
    return resumen, transporte


def _esperando(conn, ws, tg: int) -> list[str]:
    """Las preguntas de un flujo que esta persona todavía tiene `esperando` en su
    chat. El aviso con sus propios botones (`args.aviso`) es lo que le llegó para
    decidir: sigue esperando su respuesta hasta que la dé, no es de ningún flujo
    suyo que haya terminado."""
    with admin(conn) as cur:
        cur.execute(
            """select herramienta from pending_action
                where workspace_id = %s and chat_id = %s and estado = 'esperando'
                  and args ->> 'aviso' is null
                order by creado_en""", (ws, tg))
        return [f["herramienta"] for f in cur.fetchall()]


def _enviados_a(transporte, chat_id: int) -> list[str]:
    return [e.texto for e in transporte.enviados if e.chat_id == chat_id]


def _activa(conn, ws, nombre: str, tg: int) -> None:
    """La persona escribió algo en su chat hace segundos."""
    with espacio(conn, ws) as cur:
        quien = _quien(cur, nombre, ws)
        cur.execute(
            """insert into inbound_message (workspace_id, chat_id, app_user_id, texto)
               values (%s, %s, %s, 'hola')""", (ws, tg, quien.app_user_id))
    conn.commit()


def _escenario(conn, ws):
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        tg_resp = _tg(cur, "Nahuel Gimenez")
        tg_aprob = _tg(cur, "Marcos Tarquini")
    conn.commit()
    return tid, tg_resp, tg_aprob


def _entregar_por_el_menu(cliente, conn, ws, monkeypatch, tid, tg_resp):
    """Nahuel entrega por "Ya la terminé" con evidencia y confirma."""
    filas = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Nahuel Gimenez", tg_resp)
    _tocar_etiqueta(cliente, filas, "Ya la terminé", tg_resp)
    assert _mensaje(cliente, tg_resp, "Listo, con foto del tablero.").status_code == 200
    assert _confirmar(cliente, conn, ws, "actualizar_estado", tg_resp,
                      tg_resp).status_code == 200


def _pedir_cambios(cliente, conn, ws, tg_aprob) -> None:
    """El aprobador toca "Pedir cambios" en el aviso, escribe el motivo y confirma."""
    with admin(conn) as cur:
        pid_aviso = _pendiente(cur, ws, P.SENTINEL_MENU_TAREA, chat_id=tg_aprob)
        token = next(f["token"] for f in _opciones(cur, pid_aviso)
                     if f["etiqueta"] == "Pedir cambios")
    assert _tocar(cliente, token, tg_aprob).status_code == 200
    assert _mensaje(cliente, tg_aprob, "Falta el certificado.").status_code == 200
    assert _confirmar(cliente, conn, ws, "pedir_cambios_tarea", tg_aprob,
                      tg_aprob).status_code == 200


# ---------------------------------------------------------------------------
# R4-H7, de punta a punta por el webhook (la ronda)
# ---------------------------------------------------------------------------

def test_entrega_por_texto_sin_evidencia_cierra_la_pregunta_de_opciones_y_el_aviso_sale(
        cliente, conn, corework, monkeypatch):
    """(a) Pide entregar por texto sin evidencia: la guarda rechaza, la respuesta
    termina con una pregunta abierta y el servidor le pone las tres opciones
    genéricas (`_opciones_modelo`). Contesta con un link POR TEXTO -> vista previa
    -> Confirmar. La pregunta genérica no puede quedar `esperando` y el aviso al
    aprobador sale, aunque los dos estuvieron activos hace segundos."""
    ws = corework.workspace_id
    tid, tg_resp, tg_aprob = _escenario(conn, ws)

    _guion(monkeypatch,
           Respuesta(llamadas=[Llamada("c1", "actualizar_estado", {
               "tarea_id": tid, "estado": "en_revision"})]),
           Respuesta(texto="Listo, la entrego."),
           # La reescritura del turno que intentó cambiar algo y no pudo.
           Respuesta(texto="Para entregarla necesito la evidencia. Contame en una "
                           "línea qué quedó hecho o pasame el link"))
    assert _mensaje(cliente, tg_resp,
                    "Entregá la tarea Programar HMI línea 2").status_code == 200
    with admin(conn) as cur:
        assert _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO, chat_id=tg_resp)

    _guion(monkeypatch,
           Respuesta(llamadas=[Llamada("c2", "actualizar_estado", {
               "tarea_id": tid, "estado": "en_revision",
               "evidencia_texto": "https://ejemplo.test/tablero"})]),
           Respuesta(texto="Revisá el resumen y confirmá."))
    assert _mensaje(cliente, tg_resp,
                    "https://ejemplo.test/tablero").status_code == 200
    assert _confirmar(cliente, conn, ws, "actualizar_estado", tg_resp,
                      tg_resp).status_code == 200
    _activa(conn, ws, "Marcos Tarquini", tg_aprob)

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_revision"
    assert _esperando(conn, ws, tg_resp) == []

    resumen, transporte = _pasada(conn, ws, _en_horario(conn, ws))

    assert any("Nahuel Gimenez entregó" in t for t in _enviados_a(transporte, tg_aprob))
    assert resumen["retenidos"] == 0


def test_pedir_cambios_cierra_su_dato_y_el_aviso_al_responsable_sale(
        cliente, conn, corework, monkeypatch):
    """(b) El aprobador toca "Pedir cambios" en el aviso, escribe el motivo, ve la
    vista previa y confirma. Su pregunta del motivo (`_dato_menu_tarea`) no queda
    `esperando` y el aviso "pidió cambios" le sale al responsable."""
    ws = corework.workspace_id
    tid, tg_resp, tg_aprob = _escenario(conn, ws)
    _entregar_por_el_menu(cliente, conn, ws, monkeypatch, tid, tg_resp)
    _pedir_cambios(cliente, conn, ws, tg_aprob)

    assert _esperando(conn, ws, tg_aprob) == []
    assert _esperando(conn, ws, tg_resp) == []

    resumen, transporte = _pasada(conn, ws, _en_horario(conn, ws))

    assert any("Marcos Tarquini pidió cambios" in t
               for t in _enviados_a(transporte, tg_resp))
    assert resumen["retenidos"] == 0


def test_ya_la_termine_cierra_su_dato_y_la_segunda_entrega_llega_al_aprobador(
        cliente, conn, corework, monkeypatch):
    """(c) Ronda completa: entrega, cambios pedidos, "Ya la terminé" otra vez con
    evidencia nueva. Ninguno de los dos queda con una pregunta `esperando` y el
    aviso de la segunda entrega sale hacia el aprobador."""
    ws = corework.workspace_id
    tid, tg_resp, tg_aprob = _escenario(conn, ws)
    _entregar_por_el_menu(cliente, conn, ws, monkeypatch, tid, tg_resp)
    _pedir_cambios(cliente, conn, ws, tg_aprob)
    # Lo que se acumuló hasta acá sale antes de la segunda entrega.
    _pasada(conn, ws, _en_horario(conn, ws))

    filas = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Nahuel Gimenez", tg_resp)
    _tocar_etiqueta(cliente, filas, "Ya la terminé", tg_resp)
    assert _mensaje(cliente, tg_resp,
                    "Ahora sí, con el certificado adjunto.").status_code == 200
    assert _confirmar(cliente, conn, ws, "actualizar_estado", tg_resp,
                      tg_resp).status_code == 200
    _activa(conn, ws, "Marcos Tarquini", tg_aprob)

    assert _esperando(conn, ws, tg_resp) == []
    assert _esperando(conn, ws, tg_aprob) == []

    resumen, transporte = _pasada(conn, ws, _en_horario(conn, ws))

    assert any("Nahuel Gimenez entregó" in t and "certificado adjunto" in t
               for t in _enviados_a(transporte, tg_aprob))
    assert resumen["retenidos"] == 0


# ---------------------------------------------------------------------------
# Un pendiente por tipo: cuando su flujo termina deja de esperar
# ---------------------------------------------------------------------------

def _abrir_dato_menu(cur, quien, tg: int, ahora, *, accion="terminar"):
    p = P.registrar(cur, quien, herramienta=P.SENTINEL_DATO_MENU_TAREA,
                    args={"accion": accion, "tarea_id": "t", "titulo": "X"},
                    resumen="¿Qué hiciste?", vence_en=ahora + timedelta(hours=8),
                    chat_id=tg, opciones=[])
    P.marcar_para_corregir(cur, quien, p.id, tg, ahora)
    return p.id


def _estado(conn, pid: str) -> str:
    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid,))
        return cur.fetchone()["estado"]


def test_el_dato_del_menu_deja_de_esperar_cuando_se_responde(corework, conn):
    ws = corework.workspace_id
    ahora = datetime.now(timezone.utc)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        pid = _abrir_dato_menu(cur, quien, 9004, ahora)
        assert P.ver_rama_abierta(cur, quien, 9004, ahora, ()) is not None
        assert P.consumir_modificacion(cur, pid, ahora) is True
    conn.commit()

    assert _estado(conn, pid) == "resuelta"
    with espacio(conn, ws) as cur:
        assert P.ver_rama_abierta(cur, quien, 9004, ahora, ()) is None


def test_el_dato_del_menu_deja_de_esperar_cuando_se_deja_de_lado(corework, conn):
    ws = corework.workspace_id
    ahora = datetime.now(timezone.utc)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        pid = _abrir_dato_menu(cur, quien, 9004, ahora, accion="pedir_cambios")
        assert P.consumir_modificacion(cur, pid, ahora, cancelada=True) is True
    conn.commit()

    assert _estado(conn, pid) == "cancelada"


def test_la_correccion_reclamada_deja_de_esperar(corework, conn):
    """El otro camino que consume el dato (`reclamar_modificacion_abierta`)."""
    ws = corework.workspace_id
    ahora = datetime.now(timezone.utc)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        pid = _abrir_dato_menu(cur, quien, 9004, ahora)
        assert P.reclamar_modificacion_abierta(cur, quien, 9004, ahora) is not None
    conn.commit()

    assert _estado(conn, pid) == "resuelta"


def test_modificar_una_vista_previa_la_deja_cancelada_no_resuelta(corework, conn):
    """El estado de una fila que ya cerró otro camino no se pisa."""
    ws = corework.workspace_id
    ahora = datetime.now(timezone.utc)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        p = P.registrar(cur, quien, herramienta="registrar_bloqueo", args={},
                        resumen="¿Confirmás?", vence_en=ahora + timedelta(hours=8),
                        chat_id=9004)
        assert P.modificar_vista_previa(cur, quien, p.id, ahora) is not None
        assert P.reclamar_modificacion_abierta(cur, quien, 9004, ahora) is None
    conn.commit()

    assert _estado(conn, p.id) == "cancelada"


def _ultimo_id(cur, herramienta: str) -> str:
    cur.execute("select id from pending_action where herramienta = %s "
                "order by creado_en desc limit 1", (herramienta,))
    return str(cur.fetchone()["id"])


def test_la_pregunta_con_botones_de_la_rama_se_retira_al_cerrarse_la_rama(
        corework, conn):
    """`_respuesta_dato_menu` ("¿Esto es la evidencia?") acompaña a la pregunta
    abierta: si esa pregunta se consume o se deja, sus botones ya no valen."""
    from prisma import gateway

    ws = corework.workspace_id
    ahora = datetime.now(timezone.utc)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        pid = _abrir_dato_menu(cur, quien, 9004, ahora)
        abierta = P.ver_modificacion_abierta(cur, quien, 9004, ahora)
        gateway._preguntar_si_es_el_dato(cur, quien, ws, 9004, "un texto", abierta,
                                         None, ahora)
        pid_botones = _ultimo_id(cur, P.SENTINEL_RESPUESTA_DATO_MENU)
        assert gateway._consumir_pregunta(cur, quien, 9004, abierta, ahora) is True
    conn.commit()

    assert _estado(conn, pid) == "resuelta"
    assert _estado(conn, pid_botones) == "vencida"


def test_escribir_contesta_la_pregunta_abierta_y_retira_sus_botones_genericos(
        cliente, conn, corework, monkeypatch):
    """Los botones genéricos existen porque la respuesta terminó preguntando en
    texto abierto: la persona que escribe la contesta y dejan de valer. Una lista
    de tareas (otra oferta de camino), el aviso que le llegó para decidir y lo de
    otra persona no se tocan."""
    ws = corework.workspace_id
    tid, tg_resp, tg_aprob = _escenario(conn, ws)
    ahora = datetime.now(timezone.utc)

    def oferta(cur, quien, tg, **extra):
        return P.registrar(cur, quien, herramienta=P.SENTINEL_OPCIONES_MODELO,
                           args={"pregunta": "¿Cuál?", **extra}, resumen="¿Cuál?",
                           vence_en=ahora + timedelta(hours=8), campo="eleccion",
                           opciones=[("Una", {"tipo": "salida"})], chat_id=tg).id

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        marcos = _quien(cur, "Marcos Tarquini", ws)
        generica = oferta(cur, nahuel, tg_resp, cierre_generico=True)
        lista = oferta(cur, nahuel, tg_resp)
        ajena = oferta(cur, marcos, tg_aprob, cierre_generico=True)
        aviso = P.registrar(cur, nahuel, herramienta=P.SENTINEL_MENU_TAREA,
                            args={"tarea_id": tid, "aviso": P.AVISO_ENTREGA},
                            resumen="Aviso", vence_en=ahora + timedelta(hours=8),
                            campo="eleccion", opciones=[("Aprobar", {})],
                            chat_id=tg_resp).id
    conn.commit()

    _guion(monkeypatch, Respuesta(texto="Anotado."))
    assert _mensaje(cliente, tg_resp, "Es la del HMI.").status_code == 200

    assert _estado(conn, generica) == "vencida"
    assert [_estado(conn, p) for p in (lista, ajena, aviso)] == ["esperando"] * 3


# ---------------------------------------------------------------------------
# Qué no es una rama: lo que le llega a alguien para decidir
# ---------------------------------------------------------------------------

def test_el_aviso_con_sus_botones_no_es_una_rama_ni_retiene_a_otros_ni_a_si_mismo(
        corework, conn):
    """Un aviso todavía sin responder (ni siquiera enviado) no es una conversación
    en la que la persona esté: no la retiene a ella ni a otros avisos, ni se
    retiene a sí mismo (ADR 0013: "lo que empezó otra persona y le llega para
    decidir" es un mensaje que inicia Prisma, no una rama)."""
    from prisma import herramientas as H

    ws = corework.workspace_id
    ahora = datetime.now(timezone.utc)
    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        tg = 9004
        cur.execute(
            """insert into inbound_message (workspace_id, chat_id, app_user_id, texto)
               values (%s, %s, %s, 'hola')""", (ws, tg, marcos.app_user_id))
        aviso = P.registrar(
            cur, marcos, herramienta=P.SENTINEL_MENU_TAREA,
            args={"tarea_id": "t", "aviso": P.AVISO_ENTREGA}, resumen="Entregó X",
            vence_en=ahora + timedelta(hours=8), campo="eleccion",
            opciones=[("Aprobar", {}), ("Pedir cambios", {})], chat_id=tg)
        enqueue_outbox(cur, workspace_id=ws, chat_id=tg, text="Entregó X",
                       recipient_membership_id=marcos.membership_id,
                       scheduled_for=ahora - timedelta(minutes=1),
                       dedupe_key="rama:aviso", pending_action_id=aviso.id)
        enqueue_outbox(cur, workspace_id=ws, chat_id=tg, text="Otro aviso",
                       recipient_membership_id=marcos.membership_id,
                       scheduled_for=ahora - timedelta(minutes=1),
                       dedupe_key="rama:otro")
        assert P.ver_rama_abierta(cur, marcos, tg, ahora, H.REGISTRO,
                                  alta=True) is None
    conn.commit()

    resumen, transporte = _pasada(conn, ws, _en_horario(conn, ws))

    assert resumen["retenidos"] == 0
    assert {e.texto for e in transporte.enviados
            if e.chat_id == 9004} >= {"Entregó X", "Otro aviso"}


# ---------------------------------------------------------------------------
# El tope diario cuenta lo automático, no lo que se le contesta
# ---------------------------------------------------------------------------

def test_las_respuestas_no_cuentan_contra_el_tope_diario_de_avisos(corework, conn):
    """`despachar` dice que contestarle a quien escribió "no cuenta contra el tope
    de mensajes automáticos: no es automático" (ADR 0011), y el tope de corework es
    de 3 por día. Una persona que ya recibió más de tres respuestas hoy sigue
    recibiendo el aviso que Prisma le inicia."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        tg = 9005
        for i in range(5):
            enqueue_outbox(cur, workspace_id=ws, chat_id=tg, text=f"Respuesta {i}",
                           recipient_membership_id=nahuel.membership_id,
                           scheduled_for=datetime.now(timezone.utc)
                           - timedelta(minutes=2), dedupe_key=f"tope:r{i}",
                           is_response=True)
        enqueue_outbox(cur, workspace_id=ws, chat_id=tg, text="Aviso de Prisma",
                       recipient_membership_id=nahuel.membership_id,
                       scheduled_for=datetime.now(timezone.utc)
                       - timedelta(minutes=1), dedupe_key="tope:aviso")
    conn.commit()

    resumen, transporte = _pasada(conn, ws, _en_horario(conn, ws))

    assert "Aviso de Prisma" in _enviados_a(transporte, 9005)
    assert resumen["pospuestos"] == 0
