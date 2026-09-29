"""Lo que quedó pendiente no se vuelve a proponer mientras se atiende otro tema
(T9-R1b-3, ADR 0013 regla 1, "Precisión" del banco b-0020-c).

Con una pregunta abierta cuya acción y tarea se conocen (Modificar: la
herramienta de la propuesta y su `tarea_id`; un dato del menú: la herramienta a
la que lleva la acción y su tarea), el turno de `otro_tema` no puede registrar
una propuesta NUEVA de esa misma herramienta sobre esa misma tarea: un
prompt no lo garantiza (el banco real lo repitió 3 de 3), lo garantiza el
código. La guarda es sobre (herramienta, tarea), nunca sobre el texto.

Los ruteos y el modelo se guionan con `ProveedorGuionado`; nada toca la red.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from prisma import gateway
from prisma import pendientes as P
from prisma.db import admin, espacio
from prisma.llm import Llamada, RespectoPendiente, Respuesta

from tests.test_menu_tarea import (_abrir_menu, _mensaje, _quien,  # noqa: F401
                                   _tarea as _tarea_menu, _telegram_id, _tocar,
                                   _tocar_accion, cliente)
from tests.test_modificar import _proponer, _tarea as _tarea_modificar
from tests.test_pregunta_pendiente_otras import (_abiertas, _con_rutas,
                                                 _filas_del_chat, _ruta,
                                                 _salidas, _tocar_boton)

PERSONA = "Marcos Tarquini"
CAUSA = "falta el switch"
TITULO_MENU = "Programar HMI línea 2"
FRAGMENTO_RECHAZO = "ya está pendiente con la persona"


def _vistas_previas(conn, herramienta: str, tarea_id: str) -> int:
    """Vistas previas esperando Confirmar de `herramienta` sobre `tarea_id`."""
    with admin(conn) as cur:
        cur.execute(
            """select count(*) n from pending_action
                where estado = 'esperando' and herramienta = %s
                  and args->>'tarea_id' = %s""", (herramienta, tarea_id))
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


def _guion(herramienta: str, args: dict, *,
           consultando: bool = True) -> list[Respuesta]:
    """El modelo consulta las tareas (opcional), vuelve a llamar a
    `herramienta` y cierra con un texto. Una consulta con filas deja los
    botones de la lista: entonces el turno ya dejó algo pendiente y no hay
    retome (`_retomar_dato_pendiente`), así que el test del retome no consulta."""
    consulta = ([Respuesta(llamadas=[Llamada("q1", "consultar_tareas", {})])]
                if consultando else [])
    return [*consulta,
            Respuesta(llamadas=[Llamada("q2", herramienta, args)]),
            Respuesta(texto="Tenés dos tareas abiertas.")]


def test_modificar_otro_tema_no_vuelve_a_proponer_la_misma_herramienta_en_la_misma_tarea(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, a, _b = _abrir_modificar(cliente, conn, ws)
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA)],
        guion=_guion("registrar_bloqueo", {"tarea_id": a, "causa": CAUSA},
                     consultando=False))
    previas = _vistas_previas(conn, "registrar_bloqueo", a)
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "¿qué tareas tengo abiertas?")

    assert _vistas_previas(conn, "registrar_bloqueo", a) == previas  # ninguna nueva
    rechazo = _resultados_de_herramientas(proveedor)[-1]
    assert rechazo["tool_use_id"] == "q2" and rechazo["is_error"] is True
    assert FRAGMENTO_RECHAZO in rechazo["content"]           # el modelo lo supo
    assert len(proveedor.recibidos) == 2                     # el bucle siguió
    filas = _filas_del_chat(conn, tg)
    assert _salidas(conn, tg) == antes + 2                   # texto + retome
    assert filas[-2]["cuerpo"].startswith("Tenés dos tareas abiertas.")
    assert "no se aplicó" not in filas[-2]["cuerpo"].lower()  # no es un fallo
    assert filas[-1]["cuerpo"].startswith("¿Seguimos con")
    assert _abiertas(conn) == 1                              # Modificar sigue


def test_la_llamada_rechazada_por_la_guarda_se_audita_sin_texto(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, a, _b = _abrir_modificar(cliente, conn, ws)
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA)],
               guion=_guion("registrar_bloqueo",
                            {"tarea_id": a, "causa": CAUSA}))

    _mensaje(cliente, tg, "¿qué tareas tengo abiertas?")

    with admin(conn) as cur:
        cur.execute(
            """select detalle from audit_log
                where accion = 'herramienta_rechazada:registrar_bloqueo'""")
        (fila,) = cur.fetchall()
    assert fila["detalle"]["args"]["tarea_id"] == a
    assert "qué tareas tengo abiertas" not in str(fila["detalle"])


def test_modificar_otro_tema_permite_la_misma_herramienta_en_otra_tarea(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, _a, b = _abrir_modificar(cliente, conn, ws)
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA)],
        guion=_guion("registrar_bloqueo", {"tarea_id": b, "causa": CAUSA}))
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "anotá que la de variador está bloqueada")

    assert _vistas_previas(conn, "registrar_bloqueo", b) == 1  # vista previa de B
    assert all(FRAGMENTO_RECHAZO not in r["content"]
               for r in _resultados_de_herramientas(proveedor))
    assert _abiertas(conn) == 1
    # Hay una vista previa esperando: no se agrega el retome, una sola salida.
    assert _salidas(conn, tg) == antes + 1
    assert not _filas_del_chat(conn, tg)[-1]["cuerpo"].startswith("¿Seguimos con")


@pytest.mark.parametrize("es_la_misma", [True, False],
                         ids=["misma_tarea_rechaza", "otra_tarea_permite"])
def test_dato_del_menu_otro_tema_guarda_la_herramienta_de_la_accion(
        cliente, conn, corework, monkeypatch, es_la_misma):
    ws = corework.workspace_id
    tg, a, b = _abrir_dato_menu(cliente, conn, ws, monkeypatch)
    destino = a if es_la_misma else b
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA)],
        guion=_guion("actualizar_estado",
                     {"tarea_id": destino, "estado": "en_revision"}))

    _mensaje(cliente, tg, "¿qué tareas tengo abiertas?")

    rechazos = [r for r in _resultados_de_herramientas(proveedor)
                if FRAGMENTO_RECHAZO in r["content"]]
    assert bool(rechazos) is es_la_misma
    if es_la_misma:
        assert _vistas_previas(conn, "actualizar_estado", a) == 0
    assert _abiertas(conn) == 1


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
    assert all(FRAGMENTO_RECHAZO not in r["content"]
               for r in _resultados_de_herramientas(proveedor))


def test_no_es_otra_cosa_tambien_tiene_la_guarda(
        cliente, conn, corework, monkeypatch):
    # "No, es otra cosa" es `otro_tema` por el botón: mismo camino, misma guarda.
    ws = corework.workspace_id
    tg, a, _b = _abrir_modificar(cliente, conn, ws)
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.DUDOSO), _ruta(None)],
        guion=_guion("registrar_bloqueo", {"tarea_id": a, "causa": CAUSA}))
    _mensaje(cliente, tg, "puede ser")
    antes = _vistas_previas(conn, "registrar_bloqueo", a)

    _tocar_boton(cliente, conn, ws, "No", tg)

    assert _vistas_previas(conn, "registrar_bloqueo", a) == antes
    assert any(FRAGMENTO_RECHAZO in r["content"]
               for r in _resultados_de_herramientas(proveedor))
    assert _abiertas(conn) == 1
    assert gateway.MARCA_PREGUNTA_PENDIENTE in proveedor.recibidos[0][0]
