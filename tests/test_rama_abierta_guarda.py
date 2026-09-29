"""Lo que la persona acaba de dejar no se vuelve a proponer al atender lo otro
(T9-R1d-1a-fix, ADR 0013 regla 1 y su enmienda "una sola rama abierta").

Con "Dejarlo y ver lo otro" (o "No, es otra cosa" de `dudoso`) el mensaje
guardado se atiende por el camino normal, y el modelo ve en el historial la
propuesta que se acaba de dejar (banco b-0020-f, 0/3: volvió a llamar a
`registrar_bloqueo` sobre la misma tarea). La guarda es de código, sobre
(herramienta, id): un prompt no lo garantiza. Nunca mira el texto.

Los ruteos y el modelo se guionan con `ProveedorGuionado`; nada toca la red.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from prisma import pendientes as P
from prisma.db import admin, espacio
from prisma.llm import Llamada, RespectoPendiente, Respuesta

from tests.test_menu_tarea import (_abrir_menu, _bloquear, _mensaje, _quien,  # noqa: F401
                                   _tarea as _tarea_menu, _telegram_id,
                                   _tocar, _tocar_accion, cliente)
from tests.test_modificar import _proponer, _tarea as _tarea_modificar
from tests.test_pregunta_pendiente_otras import (_abiertas, _con_rutas, _ruta,
                                                 _tocar_boton)

PERSONA = "Marcos Tarquini"
CAUSA = "falta el switch"
TITULO_MENU = "Programar HMI línea 2"
OTRO_MENSAJE = "¿qué tareas tengo abiertas?"
FRAGMENTO_RECHAZO = "ya está pendiente con la persona"


def _vistas_previas(conn, herramienta: str, valor: str,
                    campo: str = "tarea_id") -> int:
    with admin(conn) as cur:
        cur.execute(
            """select count(*) n from pending_action
                where estado = 'esperando' and herramienta = %s
                  and args->>%s = %s""", (herramienta, campo, valor))
        return cur.fetchone()["n"]


def _resultados_de_herramientas(proveedor) -> list[dict]:
    """Los `tool_result` que el modelo recibió, en orden y sin repetir."""
    vistos, unicos = set(), []
    for _sistema, mensajes in proveedor.recibidos:
        for m in mensajes:
            if m["role"] == "user" and isinstance(m["content"], list):
                for b in m["content"]:
                    if (b.get("type") == "tool_result"
                            and b["tool_use_id"] not in vistos):
                        vistos.add(b["tool_use_id"])
                        unicos.append(b)
    return unicos


def _rechazos(proveedor) -> list[dict]:
    return [r for r in _resultados_de_herramientas(proveedor)
            if FRAGMENTO_RECHAZO in r["content"]]


def _abrir_modificar(cliente, conn, ws) -> tuple[int, str, str]:
    """Una vista previa de `registrar_bloqueo` sobre la tarea A, el toque en
    "Modificar", y una tarea B distinta. Devuelve (chat, A, B)."""
    with admin(conn) as cur:
        a = _tarea_modificar(cur, ws)
        b = _tarea_modificar(cur, ws, titulo="Revisar variador línea 2")
    conn.commit()
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tg = _telegram_id(cur, PERSONA)
        pid = _proponer(cur, ws, quien, "registrar_bloqueo",
                        {"tarea_id": a, "causa": CAUSA}, chat_id=tg,
                        ahora=datetime.now(timezone.utc))
        modificar = P.opcion_por_etiqueta(cur, pid, "Modificar")
    conn.commit()
    assert _tocar(cliente, modificar.token, tg).status_code == 200
    assert _abiertas(conn) == 1
    return tg, a, b


def _abrir_dato_menu(cliente, conn, ws, monkeypatch) -> tuple[int, str, str]:
    """"Ya la terminé" sobre la tarea A (pide la evidencia) y una tarea B."""
    with admin(conn) as cur:
        a = _tarea_menu(cur, ws, titulo=TITULO_MENU, estado="asignada")
        b = _tarea_menu(cur, ws, titulo="Revisar variador línea 2",
                        estado="asignada")
    conn.commit()
    _pid, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, a,
                                  "Nahuel Gimenez")
    _tocar_accion(cliente, conn, ws, filas, "Ya la terminé", tg)
    assert _abiertas(conn) == 1
    return tg, a, b


def _guion(herramienta: str, args: dict) -> list[Respuesta]:
    """El modelo consulta las tareas, vuelve a llamar a `herramienta` y cierra
    con un texto: lo que hizo en el banco real."""
    return [Respuesta(llamadas=[Llamada("q1", "consultar_tareas", {})]),
            Respuesta(llamadas=[Llamada("q2", herramienta, args)]),
            Respuesta(texto="Tenés dos tareas abiertas.")]


def _dejar_y_ver_lo_otro(cliente, conn, ws, tg, monkeypatch, guion):
    """`otro_tema` con la pregunta abierta, y el toque en "Dejarlo y ver lo
    otro": el mensaje guardado se atiende con el modelo guionado."""
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA), _ruta(None)],
        guion=guion)
    _mensaje(cliente, tg, OTRO_MENSAJE)
    _tocar_boton(cliente, conn, ws, "Dejarlo", tg)
    return proveedor


@pytest.mark.parametrize("es_la_misma", [True, False],
                         ids=["misma_tarea_rechaza", "otra_tarea_permite"])
def test_dejar_un_modificar_no_vuelve_a_proponer_la_misma_herramienta_en_la_misma_tarea(
        cliente, conn, corework, monkeypatch, es_la_misma):
    ws = corework.workspace_id
    tg, a, b = _abrir_modificar(cliente, conn, ws)
    destino = a if es_la_misma else b
    previas_a = _vistas_previas(conn, "registrar_bloqueo", a)

    proveedor = _dejar_y_ver_lo_otro(
        cliente, conn, ws, tg, monkeypatch,
        _guion("registrar_bloqueo", {"tarea_id": destino, "causa": CAUSA}))

    assert bool(_rechazos(proveedor)) is es_la_misma
    assert _vistas_previas(conn, "registrar_bloqueo", a) == previas_a
    if es_la_misma:
        rechazo = _rechazos(proveedor)[0]
        assert rechazo["tool_use_id"] == "q2" and rechazo["is_error"] is True
    else:
        # Aserción positiva: sobre otra tarea la propuesta sí se arma.
        assert _vistas_previas(conn, "registrar_bloqueo", b) == 1


def test_dejar_un_modificar_permite_otra_herramienta_sobre_la_misma_tarea(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, a, _b = _abrir_modificar(cliente, conn, ws)

    proveedor = _dejar_y_ver_lo_otro(
        cliente, conn, ws, tg, monkeypatch,
        _guion("actualizar_estado", {"tarea_id": a, "estado": "en_revision",
                                     "evidencia_texto": "quedó probada"}))

    assert _rechazos(proveedor) == []
    assert _vistas_previas(conn, "actualizar_estado", a) == 1


def test_la_llamada_rechazada_se_audita_sin_el_texto_de_la_persona(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, a, _b = _abrir_modificar(cliente, conn, ws)

    _dejar_y_ver_lo_otro(
        cliente, conn, ws, tg, monkeypatch,
        _guion("registrar_bloqueo", {"tarea_id": a, "causa": CAUSA}))

    with admin(conn) as cur:
        cur.execute(
            """select detalle from audit_log
                where accion = 'herramienta_rechazada:registrar_bloqueo'""")
        (fila,) = cur.fetchall()
    assert fila["detalle"]["args"]["tarea_id"] == a
    assert "qué tareas tengo abiertas" not in str(fila["detalle"])


@pytest.mark.parametrize("es_la_misma", [True, False],
                         ids=["misma_tarea_rechaza", "otra_tarea_permite"])
def test_dejar_un_dato_del_menu_guarda_la_herramienta_de_la_accion(
        cliente, conn, corework, monkeypatch, es_la_misma):
    ws = corework.workspace_id
    tg, a, b = _abrir_dato_menu(cliente, conn, ws, monkeypatch)
    destino = a if es_la_misma else b

    proveedor = _dejar_y_ver_lo_otro(
        cliente, conn, ws, tg, monkeypatch,
        _guion("actualizar_estado", {"tarea_id": destino, "estado": "en_revision",
                                     "evidencia_texto": "quedó probada"}))

    assert bool(_rechazos(proveedor)) is es_la_misma
    assert _vistas_previas(conn, "actualizar_estado", a) == 0
    if not es_la_misma:
        assert _vistas_previas(conn, "actualizar_estado", b) == 1


def test_dudoso_no_es_otra_cosa_tambien_tiene_la_guarda(
        cliente, conn, corework, monkeypatch):
    # Es la misma salida que "Dejarlo y ver lo otro": misma guarda.
    ws = corework.workspace_id
    tg, a, _b = _abrir_modificar(cliente, conn, ws)
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.DUDOSO), _ruta(None)],
        guion=_guion("registrar_bloqueo", {"tarea_id": a, "causa": CAUSA}))
    _mensaje(cliente, tg, "puede ser")
    previas = _vistas_previas(conn, "registrar_bloqueo", a)

    _tocar_boton(cliente, conn, ws, "No, es otra cosa", tg)

    assert _vistas_previas(conn, "registrar_bloqueo", a) == previas
    assert _rechazos(proveedor)


def test_sin_pregunta_pendiente_registrar_bloqueo_funciona_como_siempre(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        a = _tarea_modificar(cur, ws)
    conn.commit()
    with espacio(conn, ws) as cur:
        tg = _telegram_id(cur, PERSONA)
    conn.commit()
    proveedor = _con_rutas(
        monkeypatch, [_ruta(None)],
        guion=[Respuesta(llamadas=[Llamada("q2", "registrar_bloqueo", {
                   "tarea_id": a, "causa": CAUSA})]),
               Respuesta(texto="listo")])

    _mensaje(cliente, tg, "anotá un bloqueo")

    assert _vistas_previas(conn, "registrar_bloqueo", a) == 1
    assert _rechazos(proveedor) == []


def _bloqueo_de(conn, tarea_id: str) -> str:
    with admin(conn) as cur:
        cur.execute("select id from blocker where task_id = %s", (tarea_id,))
        return str(cur.fetchone()["id"])


@pytest.mark.parametrize("es_el_mismo", [True, False],
                         ids=["mismo_bloqueo_rechaza", "otro_bloqueo_permite"])
def test_dejar_un_modificar_de_resolver_bloqueo_guarda_por_bloqueo_id(
        cliente, conn, corework, monkeypatch, es_el_mismo):
    ws = corework.workspace_id
    with admin(conn) as cur:
        a = _tarea_modificar(cur, ws)
        b = _tarea_modificar(cur, ws, titulo="Revisar variador línea 2")
        _bloquear(cur, ws, a)
        _bloquear(cur, ws, b, causa="Falta un cable")
    conn.commit()
    bloqueo_a, bloqueo_b = _bloqueo_de(conn, a), _bloqueo_de(conn, b)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tg = _telegram_id(cur, PERSONA)
        pid = _proponer(cur, ws, quien, "resolver_bloqueo",
                        {"bloqueo_id": bloqueo_a, "resolucion": "llegó el switch"},
                        chat_id=tg, ahora=datetime.now(timezone.utc))
        modificar = P.opcion_por_etiqueta(cur, pid, "Modificar")
    conn.commit()
    assert _tocar(cliente, modificar.token, tg).status_code == 200
    previas_a = _vistas_previas(conn, "resolver_bloqueo", bloqueo_a, "bloqueo_id")
    destino = bloqueo_a if es_el_mismo else bloqueo_b

    proveedor = _dejar_y_ver_lo_otro(
        cliente, conn, ws, tg, monkeypatch,
        _guion("resolver_bloqueo",
               {"bloqueo_id": destino, "resolucion": "llegó el switch"}))

    assert bool(_rechazos(proveedor)) is es_el_mismo
    assert _vistas_previas(conn, "resolver_bloqueo", bloqueo_a,
                           "bloqueo_id") == previas_a
    if not es_el_mismo:
        assert _vistas_previas(conn, "resolver_bloqueo", bloqueo_b,
                               "bloqueo_id") == 1
