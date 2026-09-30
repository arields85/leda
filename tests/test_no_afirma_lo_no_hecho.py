"""Ninguna respuesta afirma un efecto que no se ejecutó (T9-R3, ADR 0013 regla 3).

Banco real `b-0020-f-1`: tras "Dejarlo y ver lo otro" la guarda rechazó
`registrar_bloqueo` (la persona acababa de dejarlo) y el modelo, que había visto
el rechazo, igual escribió "registré". Un prompt no lo garantiza y una lista de
frases ("registré", "pasé", "aprobé"...) no termina nunca: el mecanismo mira lo
que pasó en el turno, no lo que el modelo dijo.

- El resultado de una llamada rechazada le dice al modelo, sin ambigüedad, que no
  se registró ni se cambió nada.
- Si el turno intentó cambiar algo y ninguna herramienta que cambia algo se
  ejecutó, la respuesta del modelo no se toma tal cual (dijera lo que dijera): se
  le pide UNA vez que la reescriba sabiendo qué no se ejecutó, y sale con el
  estado "sin cambios". Si no puede reescribirla, sale sólo el estado.
- Un turno sin ese intento (una lectura, una conversación, algo que sí se
  ejecutó o que espera la confirmación de la persona) no cambia.

Los proveedores se guionan; ninguna prueba toca la red ni el modelo real.
"""

from __future__ import annotations

import json

import pytest

from prisma import agente
from prisma.agente import NoProponer, responder
from prisma.calendario import Calendario
from prisma.db import admin, espacio
from prisma.llm import Llamada, ProveedorGuionado, Respuesta
from prisma.salida import NO_EFFECT_STATUS

from tests.test_veracidad import AHORA, _quien, _tarea

PERSONA = "Marcos Tarquini"
AFIRMA = "Listo, ya quedó registrado el bloqueo."
CORRIGE = "No se hizo ningún cambio: eso ya estaba pendiente."


def _cuerpos(cur) -> list[str]:
    cur.execute("select cuerpo from message_outbox order by programado_para, id")
    return [f["cuerpo"] for f in cur.fetchall()]


def _tarea_de_marcos(conn, ws) -> str:
    with admin(conn) as cur:
        return _tarea(cur, ws)


def _turno(conn, ws, guion, *, no_proponer=None, texto="registrá el bloqueo"):
    """Un turno de Marcos con el modelo guionado. Devuelve (proveedor, resultado,
    cuerpos que salieron)."""
    proveedor = ProveedorGuionado(list(guion))
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, texto, proveedor, cal, chat_id=9100,
                      ahora=AHORA, no_proponer=no_proponer)
        return proveedor, r, _cuerpos(cur)


def _guarda(tid) -> NoProponer:
    return NoProponer("registrar_bloqueo", "tarea_id", tid, dejado="el bloqueo")


def _llamada_rechazada(tid) -> Llamada:
    return Llamada("c1", "registrar_bloqueo", {"tarea_id": tid, "causa": "falta el switch"})


def _resultados(proveedor) -> list[dict]:
    """Los `tool_result` que el modelo recibió, sin repetir."""
    vistos, salida = set(), []
    for _sistema, mensajes in proveedor.recibidos:
        for m in mensajes:
            if m["role"] == "user" and isinstance(m["content"], list):
                for b in m["content"]:
                    if b.get("type") == "tool_result" and b["tool_use_id"] not in vistos:
                        vistos.add(b["tool_use_id"])
                        salida.append(b)
    return salida


def _ultimo_mensaje_de_usuario(proveedor) -> str:
    """El último mensaje que recibió el modelo, como texto plano."""
    _sistema, mensajes = proveedor.recibidos[-1]
    contenido = mensajes[-1]["content"]
    assert mensajes[-1]["role"] == "user"
    if isinstance(contenido, str):
        return contenido
    return " ".join(b.get("text", "") for b in contenido if b.get("type") == "text")


# ------------------------------------------- el rechazo dice que no se hizo nada

def test_el_rechazo_de_la_guarda_le_dice_al_modelo_que_no_se_registro_nada(
        corework, conn):
    ws = corework.workspace_id
    tid = _tarea_de_marcos(conn, ws)

    proveedor, _r, _c = _turno(
        conn, ws, [Respuesta(llamadas=[_llamada_rechazada(tid)]),
                   Respuesta(texto=AFIRMA), Respuesta(texto=CORRIGE)],
        no_proponer=_guarda(tid))

    (rechazo,) = _resultados(proveedor)
    contenido = json.loads(rechazo["content"])
    assert contenido["ejecutado"] is False and rechazo["is_error"] is True
    assert agente.NADA_SE_REGISTRO in rechazo["content"]
    assert agente.NADA_SE_REGISTRO in contenido["aclaracion"]


def test_el_rechazo_de_la_segunda_pregunta_tambien_dice_que_no_se_registro_nada(
        corework, conn):
    # El turno termina en la pregunta y el modelo no llega a ver este resultado,
    # pero es el mismo formato: nunca ambiguo.
    from types import SimpleNamespace

    ws = corework.workspace_id
    tid = _tarea_de_marcos(conn, ws)
    ctx = SimpleNamespace(pack_hash=None, nucleo_hash=None)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        rechazo = agente._rechazar_segunda_pregunta(
            cur, quien, _llamada_rechazada(tid), ctx)

    contenido = json.loads(rechazo["content"])
    assert contenido["ejecutado"] is False and rechazo["is_error"] is True
    assert agente.NADA_SE_REGISTRO in contenido["aclaracion"]


# ---------------------- lo que dice se comprueba contra lo que se ejecutó

def test_bench_b_0020_f_1_el_modelo_afirma_lo_que_la_guarda_rechazo(corework, conn):
    """El caso del banco: la guarda rechaza `registrar_bloqueo`, el modelo vio el
    rechazo y escribe que lo registró. La persona no lo lee: el modelo reescribe
    la respuesta una vez sabiendo qué no se ejecutó."""
    ws = corework.workspace_id
    tid = _tarea_de_marcos(conn, ws)

    proveedor, r, cuerpos = _turno(
        conn, ws, [Respuesta(llamadas=[_llamada_rechazada(tid)]),
                   Respuesta(texto=AFIRMA), Respuesta(texto=CORRIGE)],
        no_proponer=_guarda(tid))

    assert r.acciones == []
    assert len(proveedor.recibidos) == 3                  # una reescritura, no más
    correccion = _ultimo_mensaje_de_usuario(proveedor)
    assert "registrar_bloqueo" in correccion               # qué no se ejecutó
    assert "No llames" in correccion and "no afirmes" in correccion.lower()
    # Lo que sale es la reescritura con el estado; lo que afirmaba, nunca.
    assert cuerpos == [f"{CORRIGE.rstrip('.')}\n\n{NO_EFFECT_STATUS}"]
    assert AFIRMA not in "".join(cuerpos)


@pytest.mark.parametrize("afirma", [
    "Listo, ya quedó registrado el bloqueo.",
    "Registré el bloqueo y avisé al equipo.",
    "Quedó anotado en el sistema.",          # ninguna palabra de una lista de frases
    "Hecho.",
])
def test_la_correccion_no_depende_de_las_palabras_que_use_el_modelo(
        corework, conn, afirma):
    ws = corework.workspace_id
    tid = _tarea_de_marcos(conn, ws)

    proveedor, _r, cuerpos = _turno(
        conn, ws, [Respuesta(llamadas=[_llamada_rechazada(tid)]),
                   Respuesta(texto=afirma), Respuesta(texto=CORRIGE)],
        no_proponer=_guarda(tid))

    assert len(proveedor.recibidos) == 3
    assert afirma not in "".join(cuerpos)


# Cada efecto que el modelo puede afirmar, con una llamada que la base rechaza
# antes de escribir: el mecanismo es el mismo para todos.
_RECHAZADAS = {
    "actualizar_estado": lambda tid: {"tarea_id": tid, "estado": "terminada"},
    "aprobar_tarea": lambda tid: {"tarea_id": tid},
    "adjuntar_evidencia": lambda tid: {
        "tarea_id": "00000000-0000-0000-0000-000000000000", "tipo": "texto",
        "descripcion": "x"},
    "crear_dependencia": lambda tid: {
        "origen_tarea_id": tid,
        "destino_tarea_id": "00000000-0000-0000-0000-000000000000"},
}


@pytest.mark.parametrize("herramienta, afirma", [
    ("actualizar_estado", "Listo, la pasé a terminada y la cerré."),
    ("aprobar_tarea", "Aprobé la tarea."),
    ("adjuntar_evidencia", "Adjunté la evidencia."),
    ("crear_dependencia", "Creé la dependencia entre las dos."),
])
def test_ningun_efecto_afirmado_sin_haberse_ejecutado_sale_como_hecho(
        corework, conn, herramienta, afirma):
    ws = corework.workspace_id
    tid = _tarea_de_marcos(conn, ws)
    llamada = Llamada("c1", herramienta, _RECHAZADAS[herramienta](tid))

    proveedor, r, cuerpos = _turno(
        conn, ws, [Respuesta(llamadas=[llamada]), Respuesta(texto=afirma),
                   Respuesta(texto=CORRIGE)])

    assert r.acciones == []
    assert len(proveedor.recibidos) == 3
    assert afirma not in "".join(cuerpos)
    assert cuerpos[-1].endswith(NO_EFFECT_STATUS)


def test_si_no_puede_reescribirla_sale_solo_el_estado_sin_cambios(corework, conn):
    ws = corework.workspace_id
    tid = _tarea_de_marcos(conn, ws)

    _p, r, cuerpos = _turno(
        conn, ws, [Respuesta(llamadas=[_llamada_rechazada(tid)]),
                   Respuesta(texto=AFIRMA), Respuesta(texto="")],
        no_proponer=_guarda(tid))

    assert cuerpos == [NO_EFFECT_STATUS]
    assert r.texto == NO_EFFECT_STATUS


def test_si_la_reescritura_falla_sale_el_estado_y_queda_el_incidente(corework, conn):
    class _Cae(ProveedorGuionado):
        def responder(self, sistema, mensajes, herramientas):
            if len(self.recibidos) >= 2:
                self.recibidos.append((sistema, list(mensajes)))
                raise RuntimeError("el proveedor no respondió")
            return super().responder(sistema, mensajes, herramientas)

    ws = corework.workspace_id
    tid = _tarea_de_marcos(conn, ws)
    proveedor = _Cae([Respuesta(llamadas=[_llamada_rechazada(tid)]),
                      Respuesta(texto=AFIRMA)])
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        r = responder(cur, quien, "registrá el bloqueo", proveedor,
                      Calendario.desde_base(cur, ws), chat_id=9100, ahora=AHORA,
                      no_proponer=_guarda(tid))
        cuerpos = _cuerpos(cur)

    assert cuerpos == [NO_EFFECT_STATUS] and r.texto == NO_EFFECT_STATUS
    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 1


# ------------------------------------------------- lo que no se toca

def test_una_lectura_no_pide_ninguna_reescritura(corework, conn):
    ws = corework.workspace_id
    _tarea_de_marcos(conn, ws)

    proveedor, _r, cuerpos = _turno(
        conn, ws, [Respuesta(llamadas=[Llamada("q1", "consultar_tareas", {})]),
                   Respuesta(texto="Tenés una tarea abierta.")])

    assert len(proveedor.recibidos) == 2
    assert cuerpos == ["Tenés una tarea abierta."]


def test_una_conversacion_sin_herramientas_sale_tal_cual(corework, conn):
    ws = corework.workspace_id

    proveedor, _r, cuerpos = _turno(conn, ws, [Respuesta(texto="Hola, ¿cómo va?")])

    assert len(proveedor.recibidos) == 1
    assert cuerpos == ["Hola, ¿cómo va?"]


def test_lo_que_espera_la_confirmacion_no_pide_reescritura(corework, conn):
    ws = corework.workspace_id
    tid = _tarea_de_marcos(conn, ws)

    proveedor, r, _c = _turno(
        conn, ws, [Respuesta(llamadas=[Llamada(
            "c1", "actualizar_estado", {"tarea_id": tid, "estado": "en_curso"})]),
            Respuesta(texto="Listo.")])

    assert r.confirmaciones == ["actualizar_estado"]
    assert len(proveedor.recibidos) == 1     # el turno terminó en la vista previa


def test_una_opcion_rechazada_por_la_guarda_no_es_un_cambio_que_no_se_hizo(
        corework, conn):
    """`ofrecer_opciones` nunca cambia nada: que la guarda del alta la rechace no
    agrega "Estado: sin cambios." ni pide reescribir."""
    ws = corework.workspace_id
    _tarea_de_marcos(conn, ws)
    alta = NoProponer(None, None, None, dejado="el título de la tarea nueva",
                      alta=True)
    ofrece = Llamada("q1", "ofrecer_opciones", {
        "pregunta": "¿Qué objetivo?", "opciones": [{"texto": "A"}]})

    proveedor, _r, cuerpos = _turno(
        conn, ws, [Respuesta(llamadas=[ofrece]), Respuesta(texto="Tenés una tarea.")],
        no_proponer=alta)

    assert len(proveedor.recibidos) == 2
    assert cuerpos == ["Tenés una tarea."]
