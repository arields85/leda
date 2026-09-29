"""Lo que Prisma inicia por su cuenta espera mientras la persona tiene una rama
abierta (T9-R1d-2, ADR 0013 regla 1, enmienda "una sola rama de conversación
abierta", decisión del usuario del 2026-09-29, opción A).

Un mensaje que NO es la respuesta a lo que la persona escribió o tocó
(cadencias, avisos, escalera, el aviso de entrega que le piden aprobar) y que
va dirigido a alguien que tiene una rama abierta en ESE chat queda en la cola,
sin enviar, y sale apenas la rama se cierra o vence la pregunta. Se retiene sólo
lo dirigido a esa persona en ese chat, nunca una respuesta, y se reporta:
`despachar` cuenta `retenidos`, y la fila sigue `listo` en la cola.

"Rama abierta" es la misma definición que usa la conversación
(`pendientes.ver_rama_abierta`): el dato que se pidió por escrito (Modificar), la
elección con botones que Prisma pidió y la vista previa del cambio que la persona
pidió. Las preguntas del alta guiada no tienen vencimiento todavía y no retienen
(decisión pendiente, ver `odd/tasks/prisma-orienta.md`).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from prisma import pendientes as P
from prisma.calendario import Calendario
from prisma.db import admin, espacio
from prisma.despachador import TransporteDePrueba, despachar
from prisma.salida import enqueue_outbox

from tests.test_menu_tarea import _quien

BA = ZoneInfo("America/Argentina/Buenos_Aires")
AHORA = datetime(2026, 7, 27, 10, 0, tzinfo=BA)   # lunes, en horario
PERSONA = "Marcos Tarquini"
OTRA = "Nahuel Gimenez"
AVISO = "Recordatorio de Prisma"


def _telegram_id(cur, nombre: str) -> int:
    cur.execute("select telegram_user_id t from integrante where nombre = %s",
                (nombre,))
    return cur.fetchone()["t"]


def _abrir(cur, quien, tg: int, *, herramienta="registrar_bloqueo", campo=None,
           opciones=None, vence=AHORA + timedelta(hours=8)) -> str:
    """Deja abierta una pregunta de esta persona en su chat."""
    return P.registrar(
        cur, quien, herramienta=herramienta, args={}, resumen="¿Confirmás?",
        vence_en=vence, campo=campo, opciones=opciones, chat_id=tg).id


def _abrir_vista_previa(cur, quien, tg, **kw) -> str:
    return _abrir(cur, quien, tg, **kw)


def _abrir_eleccion(cur, quien, tg, **kw) -> str:
    return _abrir(cur, quien, tg, herramienta="_aclarar_referencia",
                  campo="eleccion", opciones=[("Una", "a"), ("Otra", "b")], **kw)


def _abrir_dato(cur, quien, tg, *, pedido=AHORA, **kw) -> str:
    """El dato que se pidió por escrito (Modificar): espera el mensaje siguiente."""
    pid = _abrir_vista_previa(cur, quien, tg, **kw)
    cur.execute(
        """update pending_action set estado = 'cancelada', modificar_pedido_en = %s
            where id = %s""", (pedido, pid))
    return pid


def _encolar(cur, ws, quien, tg, *, clave: str, respuesta=False,
             cuando=AHORA - timedelta(minutes=5), **kw) -> None:
    enqueue_outbox(
        cur, workspace_id=ws, chat_id=tg, text=f"{AVISO} {clave}",
        recipient_membership_id=quien.membership_id, scheduled_for=cuando,
        dedupe_key=f"retencion:{clave}", is_response=respuesta, **kw)


def _despachar(conn, ws, cuando=AHORA, **kw):
    transporte = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        resumen = despachar(cur, ws, transporte, cal, cuando, **kw)
    conn.commit()
    return resumen, transporte


def _estados(conn, prefijo: str = "retencion:") -> dict[str, str]:
    with admin(conn) as cur:
        cur.execute("select dedupe_key, estado from message_outbox "
                    "where dedupe_key like %s", (prefijo + "%",))
        return {f["dedupe_key"].removeprefix(prefijo): f["estado"]
                for f in cur.fetchall()}


def _preparar(conn, ws, abrir, **kw):
    """La persona con una rama abierta y un aviso de Prisma esperando."""
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tg = _telegram_id(cur, PERSONA)
        pid = abrir(cur, quien, tg, **kw)
        _encolar(cur, ws, quien, tg, clave="aviso")
    conn.commit()
    return quien, tg, pid


# ---------------------------------------------------------------------------
# Retenido mientras hay una rama abierta, de cualquiera de los tres tipos
# ---------------------------------------------------------------------------

def test_un_aviso_queda_retenido_con_la_vista_previa_abierta(corework, conn):
    ws = corework.workspace_id
    _preparar(conn, ws, _abrir_vista_previa)

    resumen, transporte = _despachar(conn, ws)

    assert transporte.enviados == []
    assert resumen["retenidos"] == 1 and resumen["enviados"] == 0
    assert _estados(conn) == {"aviso": "listo"}      # sigue en la cola, visible


def test_un_aviso_queda_retenido_con_la_eleccion_abierta(corework, conn):
    ws = corework.workspace_id
    _preparar(conn, ws, _abrir_eleccion)

    resumen, transporte = _despachar(conn, ws)

    assert transporte.enviados == [] and resumen["retenidos"] == 1


def test_un_aviso_queda_retenido_con_el_dato_pedido_por_escrito(corework, conn):
    ws = corework.workspace_id
    _preparar(conn, ws, _abrir_dato)

    resumen, transporte = _despachar(conn, ws)

    assert transporte.enviados == [] and resumen["retenidos"] == 1


def test_sin_rama_abierta_el_aviso_sale_y_no_hay_retenidos(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        _encolar(cur, ws, quien, _telegram_id(cur, PERSONA), clave="aviso")
    conn.commit()

    resumen, transporte = _despachar(conn, ws)

    assert len(transporte.enviados) == 1
    assert resumen["retenidos"] == 0 and resumen["enviados"] == 1


# ---------------------------------------------------------------------------
# Se libera cuando la rama se cierra o vence
# ---------------------------------------------------------------------------

def test_sale_apenas_la_rama_se_cierra_por_un_toque(corework, conn):
    ws = corework.workspace_id
    quien, _tg, pid = _preparar(conn, ws, _abrir_vista_previa)
    assert _despachar(conn, ws)[0]["retenidos"] == 1

    with espacio(conn, ws) as cur:
        token = P.opcion_por_etiqueta(cur, pid, "Confirmar").token
        assert P.resolver(cur, token, app_user_id=quien.app_user_id,
                          ahora=AHORA) is not None
    conn.commit()
    resumen, transporte = _despachar(conn, ws, AHORA + timedelta(seconds=30))

    assert len(transporte.enviados) == 1 and resumen["retenidos"] == 0
    assert _estados(conn) == {"aviso": "enviado"}


def test_sale_apenas_la_rama_se_cancela_o_se_deja(corework, conn):
    ws = corework.workspace_id
    quien, _tg, pid = _preparar(conn, ws, _abrir_eleccion)
    assert _despachar(conn, ws)[0]["retenidos"] == 1

    with espacio(conn, ws) as cur:       # el camino de "cancela" / "Dejarlo"
        assert P.cancelar_vista_previa(cur, quien, pid, AHORA)
    conn.commit()
    resumen, transporte = _despachar(conn, ws, AHORA + timedelta(seconds=30))

    assert len(transporte.enviados) == 1 and resumen["retenidos"] == 0


def test_sale_apenas_el_dato_pedido_se_consume(corework, conn):
    ws = corework.workspace_id
    quien, _tg, pid = _preparar(conn, ws, _abrir_dato)
    assert _despachar(conn, ws)[0]["retenidos"] == 1

    with espacio(conn, ws) as cur:
        assert P.consumir_modificacion(cur, pid, AHORA)
    conn.commit()
    resumen, transporte = _despachar(conn, ws, AHORA + timedelta(seconds=30))

    assert len(transporte.enviados) == 1


def test_sale_cuando_la_pregunta_vence(corework, conn):
    ws = corework.workspace_id
    _preparar(conn, ws, _abrir_vista_previa, vence=AHORA + timedelta(minutes=30))
    assert _despachar(conn, ws, AHORA + timedelta(minutes=29))[0]["retenidos"] == 1

    resumen, transporte = _despachar(conn, ws, AHORA + timedelta(minutes=31))

    assert len(transporte.enviados) == 1 and resumen["retenidos"] == 0


def test_la_eleccion_abandonada_tambien_deja_de_retener_al_vencer(corework, conn):
    ws = corework.workspace_id
    _preparar(conn, ws, _abrir_eleccion, vence=AHORA + timedelta(minutes=30))

    _resumen, transporte = _despachar(conn, ws, AHORA + timedelta(minutes=31))

    assert len(transporte.enviados) == 1


def test_el_dato_pedido_vence_con_la_ventana_de_modificar(corework, conn):
    """El dato que se pidió por escrito sólo se espera `VENTANA_MODIFICACION`
    (30 minutos) desde que se tocó Modificar, aunque la propuesta venza mucho
    después: pasada la ventana, la conversación ya no lo trata como rama."""
    ws = corework.workspace_id
    _preparar(conn, ws, _abrir_dato, pedido=AHORA)
    dentro = AHORA + P.VENTANA_MODIFICACION - timedelta(minutes=1)
    assert _despachar(conn, ws, dentro)[0]["retenidos"] == 1

    resumen, transporte = _despachar(
        conn, ws, AHORA + P.VENTANA_MODIFICACION + timedelta(minutes=1))

    assert len(transporte.enviados) == 1 and resumen["retenidos"] == 0


# ---------------------------------------------------------------------------
# Sólo lo dirigido a esa persona, en ese chat, y nunca una respuesta
# ---------------------------------------------------------------------------

def test_a_las_demas_personas_les_sigue_saliendo(corework, conn):
    ws = corework.workspace_id
    _preparar(conn, ws, _abrir_vista_previa)
    with espacio(conn, ws) as cur:
        otra = _quien(cur, OTRA, ws)
        _encolar(cur, ws, otra, _telegram_id(cur, OTRA), clave="otra")
    conn.commit()

    resumen, transporte = _despachar(conn, ws)

    assert _estados(conn) == {"aviso": "listo", "otra": "enviado"}
    assert len(transporte.enviados) == 1 and resumen["retenidos"] == 1


def test_a_la_misma_persona_en_otro_chat_le_sigue_saliendo(corework, conn):
    ws = corework.workspace_id
    quien, tg, _pid = _preparar(conn, ws, _abrir_vista_previa)
    with espacio(conn, ws) as cur:
        _encolar(cur, ws, quien, -1001, clave="grupo")
    conn.commit()

    _resumen, transporte = _despachar(conn, ws)

    assert _estados(conn) == {"aviso": "listo", "grupo": "enviado"}
    assert [e.chat_id for e in transporte.enviados] == [-1001]


def test_una_respuesta_nunca_se_retiene(corework, conn):
    ws = corework.workspace_id
    quien, tg, _pid = _preparar(conn, ws, _abrir_vista_previa)
    with espacio(conn, ws) as cur:
        _encolar(cur, ws, quien, tg, clave="respuesta", respuesta=True)
    conn.commit()

    resumen, transporte = _despachar(conn, ws)

    assert _estados(conn) == {"aviso": "listo", "respuesta": "enviado"}
    assert resumen["retenidos"] == 1 and len(transporte.enviados) == 1


def test_lo_que_le_llega_para_decidir_no_es_una_rama_y_no_se_retiene_a_si_mismo(
        corework, conn):
    """El aviso de entrega (`SENTINEL_MENU_TAREA`, con botones) es un mensaje que
    inicia Prisma: no cuenta como rama de quien lo recibe, así que no se retiene
    a sí mismo ni retiene a los demás."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tg = _telegram_id(cur, PERSONA)
        aviso = _abrir(cur, quien, tg, herramienta=P.SENTINEL_MENU_TAREA,
                       campo="eleccion",
                       opciones=[("Aprobar", {"accion": "aprobar"}),
                                 ("Pedir cambios", {"accion": "pedir_cambios"})])
        _encolar(cur, ws, quien, tg, clave="entrega", pending_action_id=aviso)
        _encolar(cur, ws, quien, tg, clave="otro")
    conn.commit()

    resumen, _transporte = _despachar(conn, ws)

    assert _estados(conn) == {"entrega": "enviado", "otro": "enviado"}
    assert resumen["retenidos"] == 0


def test_el_mensaje_de_la_propia_pregunta_no_se_retiene_a_si_mismo(corework, conn):
    """Si el mensaje no-respuesta es el que muestra la propia rama (su
    `pending_action_id` es la pregunta abierta), esperaría a su propio cierre:
    sale igual."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tg = _telegram_id(cur, PERSONA)
        pid = _abrir_vista_previa(cur, quien, tg)
        _encolar(cur, ws, quien, tg, clave="propia", pending_action_id=pid)
    conn.commit()

    resumen, transporte = _despachar(conn, ws)

    assert len(transporte.enviados) == 1 and resumen["retenidos"] == 0


# ---------------------------------------------------------------------------
# Sin perder, duplicar ni reordenar; el saludo y el lote
# ---------------------------------------------------------------------------

def test_al_liberarse_salen_todos_una_sola_vez_y_en_su_orden(corework, conn):
    ws = corework.workspace_id
    quien, tg, pid = _preparar(conn, ws, _abrir_vista_previa)
    with espacio(conn, ws) as cur:
        _encolar(cur, ws, quien, tg, clave="segundo",
                 cuando=AHORA - timedelta(minutes=2))
        _encolar(cur, ws, quien, tg, clave="tercero",
                 cuando=AHORA - timedelta(minutes=1))
    conn.commit()
    assert _despachar(conn, ws)[0]["retenidos"] == 3

    with espacio(conn, ws) as cur:
        assert P.cancelar_vista_previa(cur, quien, pid, AHORA)
    conn.commit()
    _resumen, transporte = _despachar(conn, ws, AHORA + timedelta(seconds=30))
    _resumen2, transporte2 = _despachar(conn, ws, AHORA + timedelta(seconds=60))

    assert [e.texto for e in transporte.enviados] == [
        f"{AVISO} aviso", f"{AVISO} segundo", f"{AVISO} tercero"]
    assert transporte2.enviados == []                 # ni duplicado ni perdido


def test_retener_no_gasta_el_saludo_del_dia(corework, conn):
    """El saludo lo lleva el primer mensaje que SALE: uno retenido no lo reclama."""
    ws = corework.workspace_id
    quien, tg, pid = _preparar(conn, ws, _abrir_vista_previa)
    with admin(conn) as cur:
        cur.execute("delete from greeting_state where membership_id = %s",
                    (quien.membership_id,))
    conn.commit()

    _despachar(conn, ws)
    with admin(conn) as cur:
        cur.execute("select count(*) n from greeting_state where membership_id = %s",
                    (quien.membership_id,))
        assert cur.fetchone()["n"] == 0               # nada reclamó el saludo

    with espacio(conn, ws) as cur:
        assert P.cancelar_vista_previa(cur, quien, pid, AHORA)
    conn.commit()
    _resumen, transporte = _despachar(conn, ws, AHORA + timedelta(seconds=30))

    assert len(transporte.enviados) == 1
    assert transporte.enviados[0].texto.startswith("👋 Buen día")


def test_lo_retenido_no_frena_al_resto_del_lote(corework, conn):
    """Con más retenidos que el tamaño del lote, lo que sigue en la cola igual se
    despacha: retener no puede dejar sin servicio a las demás personas."""
    ws = corework.workspace_id
    quien, tg, _pid = _preparar(conn, ws, _abrir_vista_previa)
    with espacio(conn, ws) as cur:
        for i in range(3):
            _encolar(cur, ws, quien, tg, clave=f"retenido{i}",
                     cuando=AHORA - timedelta(minutes=10 + i))
        otra = _quien(cur, OTRA, ws)
        _encolar(cur, ws, otra, _telegram_id(cur, OTRA), clave="otra",
                 cuando=AHORA - timedelta(minutes=1))
    conn.commit()

    resumen, transporte = _despachar(conn, ws, lote=2)

    assert _estados(conn)["otra"] == "enviado"
    assert len(transporte.enviados) == 1 and resumen["retenidos"] == 4


def test_una_cadencia_retenida_pasada_su_ventana_se_descarta_no_se_pierde_en_silencio(
        corework, conn):
    """`vence_en` del mensaje sigue mandando: retener no lo salva de la ventana
    (ya se descartaba tarde), y queda contado en `descartados`."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tg = _telegram_id(cur, PERSONA)
        _abrir_vista_previa(cur, quien, tg)
        _encolar(cur, ws, quien, tg, clave="ventana", expires_at=AHORA)
    conn.commit()

    resumen, transporte = _despachar(conn, ws, AHORA + timedelta(minutes=1))

    assert transporte.enviados == [] and resumen["descartados"] == 1
    assert _estados(conn) == {"ventana": "descartado"}
