"""Prueba de punta a punta de "Pedir cambios" (T6e, `odd/tasks/prisma-orienta.md`;
seguimiento de review-c112506a).

ADR 0009 y su enmienda del 2026-09-27 (T6a-T6d) ya tienen cobertura a nivel de
`herramientas.ejecutar` (`tests/test_entrega_con_evidencia.py`) y a nivel de
menú (`tests/test_menu_tarea.py`). Lo que falta es recorrer el circuito
completo por el webhook real (`POST /telegram/{slug}`, igual que
`tests/test_gateway.py`), con toques (`callback_query`) y mensajes de texto
libre -- nunca llamando a `herramientas.ejecutar`/`pedir_cambios_tarea`
directo, que es justo lo que este archivo agrega.

Abrir el menú de una tarea reusa el patrón de
`tests/test_menu_tarea.py::_abrir_menu` (un guion de `ofrecer_opciones`
servido por un `ProveedorGuionado`, nunca un modelo real): es el único turno
que toca al proveedor. Todo lo que sigue -- "Ya la terminé", la evidencia, los
tres botones de la vista previa, la notificación al aprobador, "Pedir
cambios", "Aprobar" -- corre por toques y mensajes contra `_turno`/`_toque`,
sin volver a consultarlo (los sentinelas de T1/T2 lo garantizan: ver
`gateway._resolver_toque_menu_tarea`/`_resumir_dato_menu_tarea`).
"""

from __future__ import annotations

from contextlib import nullcontext
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from prisma import gateway
from prisma import pendientes as P
from prisma.agente import responder
from prisma.autoridad import Canal, identificar
from prisma.calendario import Calendario
from prisma.db import admin, espacio
from prisma.llm import Llamada, ProveedorGuionado, Respuesta

# ---------------------------------------------------------------------------
# Helpers -- mismo patrón que tests/test_menu_tarea.py y tests/test_gateway.py
# ---------------------------------------------------------------------------


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _tg(cur, nombre) -> int:
    # `integrante` es una vista filtrada por `prisma.workspace_id`
    # (documentado en `tests/test_entrega_con_evidencia.py::_tg`); `app_user`
    # es la tabla real, sin ese filtro -- se usa siempre bajo `admin(conn)`.
    cur.execute("select telegram_user_id t from app_user where nombre = %s", (nombre,))
    return cur.fetchone()["t"]


def _tarea(cur, ws, *, titulo="Programar HMI línea 2", area="ot",
          persona="Nahuel Gimenez", estado="en_curso",
          evidencia_requerida=("explicacion",)):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', 'Objetivo de prueba') returning id""", (ws,))
    obj = cur.fetchone()["id"]
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, criterio_aceptacion,
                             evidencia_requerida)
           values (%s, %s, %s,
                   (select id from area where workspace_id = %s and slug = %s),
                   (select m.id from membership m join app_user u on u.id = m.app_user_id
                     where m.workspace_id = %s and u.nombre = %s),
                    'Criterio de prueba', %s)
           returning id""",
        (ws, obj, titulo, ws, area, ws, persona,
         list(evidencia_requerida) if evidencia_requerida else []))
    t = cur.fetchone()["id"]
    cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                "values (%s, %s, 'prisma')", (t, estado))
    return str(t)


def _dependencia_bloqueante(cur, ws, destino):
    """Una dependencia bloqueante abierta sobre `destino` (variante T6c):
    la origen queda `asignada` y esta prueba nunca la cierra, así que sigue
    abierta durante todo "Pedir cambios"."""
    origen = _tarea(cur, ws, titulo="Programar PLC", estado="asignada",
                    evidencia_requerida=None)
    cur.execute(
        """insert into dependency (workspace_id, origen_task_id, destino_task_id, tipo)
           values (%s, %s, %s, 'bloqueante')""", (ws, origen, destino))
    return origen


def _outbox_ultimo(cur, ws, chat_id) -> str:
    # T6g (`odd/tasks/prisma-orienta.md`; review-8b7dde28): `programado_para`
    # no tiene desempate -- dos filas pueden compartir la misma hora dentro
    # de la misma transacción --, y `message_outbox.id` (`db/esquema.sql`) es
    # un `uuid` al azar (`gen_random_uuid()`, sin ningún orden temporal), así
    # que tampoco sirve como desempate de "la más reciente". `dedupe_key`
    # (`unique`, `db/esquema.sql`) sí garantiza un orden total determinístico
    # -- nunca hay dos filas iguales para desempatar --, así que un empate en
    # `programado_para` deja de depender del orden, no definido, en que
    # Postgres devuelva las filas iguales.
    cur.execute(
        """select cuerpo from message_outbox
            where workspace_id = %s and chat_id = %s
           order by programado_para desc, dedupe_key desc limit 1""", (ws, chat_id))
    return cur.fetchone()["cuerpo"]


@pytest.fixture
def cliente(conn, monkeypatch):
    monkeypatch.setattr(gateway, "acusar_toque", lambda *a, **k: None)
    monkeypatch.setattr(gateway, "mantener_chat_activo",
                        lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    import dataclasses
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, webhook_secret="s3cr3t"))
    return TestClient(gateway.app)


def _tocar(cliente, token, user_id):
    return cliente.post(
        "/telegram/corework",
        json={"callback_query": {
            "id": "cb1", "from": {"id": user_id}, "data": f"p:{token}",
            "message": {"message_id": 7, "chat": {"id": user_id}}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _mensaje(cliente, user_id, texto):
    return cliente.post(
        "/telegram/corework",
        json={"message": {"message_id": 2, "text": texto,
                          "chat": {"id": user_id}, "from": {"id": user_id}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _opciones(cur, pid):
    cur.execute(
        """select token, etiqueta, valor from pending_action_option
            where pending_action_id = %s order by orden""", (pid,))
    return cur.fetchall()


def _pendiente(cur, ws, herramienta, *, chat_id=None) -> str:
    """La `pending_action` `esperando` más reciente de `herramienta` -- de
    cualquier chat, o de uno puntual cuando dos personas pueden tener una
    vista previa de la misma herramienta al mismo tiempo (p. ej. Nahuel y
    Marcos, los dos con una vista previa de `actualizar_estado`/
    `pedir_cambios_tarea` en distintos chats)."""
    if chat_id is None:
        cur.execute(
            """select id from pending_action
                where workspace_id = %s and herramienta = %s and estado = 'esperando'
                order by creado_en desc limit 1""",
            (ws, herramienta))
    else:
        cur.execute(
            """select id from pending_action
                where workspace_id = %s and herramienta = %s and chat_id = %s
                  and estado = 'esperando'
                order by creado_en desc limit 1""",
            (ws, herramienta, chat_id))
    fila = cur.fetchone()
    assert fila is not None, f"no hay pending_action esperando de {herramienta}"
    return str(fila["id"])


def _confirmar(cliente, conn, ws, herramienta, chat_id, tg_user):
    """Encuentra la vista previa `esperando` de `herramienta` para `chat_id`
    y toca su botón "Confirmar" -- el mismo camino que cualquier persona
    real, nunca `herramientas.ejecutar` directo."""
    with admin(conn) as cur:
        pid = _pendiente(cur, ws, herramienta, chat_id=chat_id)
        token = next(f["token"] for f in _opciones(cur, pid) if f["etiqueta"] == "Confirmar")
    return _tocar(cliente, token, tg_user)


def _abrir_menu(cliente, conn, ws, monkeypatch, tarea_id, quien_nombre, tg, *,
                chat_id=None):
    """Igual que `tests/test_menu_tarea.py::_abrir_menu`: arma el guion de
    `ofrecer_opciones` (T1) con `accion: "menu"` sobre `tarea_id`, toca esa
    opción por el webhook y devuelve las opciones del menú ya abierto. Es el
    único turno de esta prueba que consulta al proveedor -- todo lo que
    sigue corre por sentinelas (`SENTINEL_MENU_TAREA`/`SENTINEL_DATO_MENU_
    TAREA`), nunca vuelve a llamarlo."""
    guion = [Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
        "pregunta": "¿De qué tarea hablamos?",
        "opciones": [{"tarea_id": tarea_id, "accion": "menu"}]})])]
    proveedor = ProveedorGuionado(guion=list(guion))
    monkeypatch.setattr("prisma.llm.desde_base", lambda cur, ws, key: proveedor)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, quien_nombre, ws)
        cal = Calendario.desde_base(cur, ws)
        cid = chat_id if chat_id is not None else tg
        responder(cur, quien, "tarea", proveedor, cal, chat_id=cid,
                 ahora=datetime.now(timezone.utc))
        pid_opciones = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO)
        token = _opciones(cur, pid_opciones)[0]["token"]

    assert _tocar(cliente, token, tg).status_code == 200

    with admin(conn) as cur:
        pid_menu = _pendiente(cur, ws, P.SENTINEL_MENU_TAREA, chat_id=tg)
        filas = _opciones(cur, pid_menu)
    return filas


def _tocar_etiqueta(cliente, filas, etiqueta, tg):
    fila = next(f for f in filas if f["etiqueta"] == etiqueta)
    assert _tocar(cliente, fila["token"], tg).status_code == 200


# ---------------------------------------------------------------------------
# El circuito completo
# ---------------------------------------------------------------------------

def test_pedir_cambios_punta_a_punta_por_telegram(cliente, conn, corework, monkeypatch):
    """Circuito completo de "Pedir cambios" (ADR 0009 y su enmienda del
    2026-09-27) por el webhook real, con Nahuel Gimenez como responsable y
    Marcos Tarquini como su aprobador (`aprobado_por` de OT, mismo elenco que
    `tests/test_menu_tarea.py`):

    1. Nahuel entrega ("Ya la terminé"), Prisma pide la evidencia, la
       escribe, Confirmar -> `en_revision`, evidencia registrada, Marcos
       recibe la notificación con "Aprobar"/"Pedir cambios" (decisión 3).
    2. Marcos toca "Pedir cambios", escribe el comentario, la vista previa
       nombra el destino ("en curso"), Confirmar -> `approval` 'rechazado',
       la tarea vuelve a `en_curso`, Nahuel recibe el aviso con el
       comentario (decisión 4).
    3. Nahuel entrega de nuevo -- Prisma pide evidencia NUEVA, la vieja ya no
       cuenta (T6b) -- Confirmar -> `en_revision` otra vez, una segunda fila
       de evidencia, una segunda notificación a Marcos con una `pending_
       action` y una clave de dedupe distintas de la primera (T6d).
    4. Marcos toca "Aprobar", Confirmar -> la tarea cierra (ADR 0008): la
       aprobación fresca es la que cuenta (T6a) aunque antes hubiera una
       entrega sin aprobar de por medio.
    """
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        tg_nahuel = _tg(cur, "Nahuel Gimenez")
        tg_marcos = _tg(cur, "Marcos Tarquini")
    conn.commit()

    # -- 1. Entrega con evidencia -------------------------------------------------
    filas = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Nahuel Gimenez", tg_nahuel)
    _tocar_etiqueta(cliente, filas, "Ya la terminé", tg_nahuel)

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_curso"      # todavía nada aplicado
        assert "qué hiciste" in _outbox_ultimo(cur, ws, tg_nahuel).lower()

    assert _mensaje(cliente, tg_nahuel,
                    "Terminé la instalación, con foto del tablero.").status_code == 200
    assert _confirmar(cliente, conn, ws, "actualizar_estado", tg_nahuel,
                      tg_nahuel).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_revision"
        cur.execute("select count(*) n from evidence where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 1

        pid_aviso_1 = _pendiente(cur, ws, P.SENTINEL_MENU_TAREA, chat_id=tg_marcos)
        opciones_aviso_1 = _opciones(cur, pid_aviso_1)
        cuerpo_aviso_1 = _outbox_ultimo(cur, ws, tg_marcos)
        # Mismo desempate que `_outbox_ultimo` (review-8b7dde28): `dedupe_key`
        # es `unique`, así que ordenar también por ella deja el resultado
        # determinístico frente a un empate en `programado_para`.
        cur.execute(
            """select dedupe_key from message_outbox
                where workspace_id = %s and chat_id = %s
               order by programado_para desc, dedupe_key desc limit 1""",
            (ws, tg_marcos))
        dedupe_1 = cur.fetchone()["dedupe_key"]
    assert "Nahuel Gimenez entregó" in cuerpo_aviso_1
    assert "instalación" in cuerpo_aviso_1.lower()
    assert [f["etiqueta"] for f in opciones_aviso_1] == ["Aprobar", "Pedir cambios"]

    # -- 2. Marcos pide cambios ----------------------------------------------------
    token_pedir = next(f["token"] for f in opciones_aviso_1 if f["etiqueta"] == "Pedir cambios")
    assert _tocar(cliente, token_pedir, tg_marcos).status_code == 200

    with admin(conn) as cur:
        assert "corregir" in _outbox_ultimo(cur, ws, tg_marcos).lower()

    assert _mensaje(cliente, tg_marcos,
                    "Falta el certificado del proveedor.").status_code == 200

    with admin(conn) as cur:
        pid_vista_cambios = _pendiente(cur, ws, "pedir_cambios_tarea", chat_id=tg_marcos)
        cur.execute("select resumen from pending_action where id = %s",
                   (pid_vista_cambios,))
        resumen_cambios = cur.fetchone()["resumen"]
    assert "vuelve a en curso" in resumen_cambios.lower()
    assert "certificado del proveedor" in resumen_cambios.lower()

    assert _confirmar(cliente, conn, ws, "pedir_cambios_tarea", tg_marcos,
                      tg_marcos).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_curso"
        cur.execute(
            """select decision, comentario from approval where sujeto_id = %s
               order by at desc limit 1""", (tid,))
        decision = cur.fetchone()
        assert decision["decision"] == "rechazado"
        assert decision["comentario"] == "Falta el certificado del proveedor."
        cuerpo_a_nahuel = _outbox_ultimo(cur, ws, tg_nahuel)
    assert "Marcos Tarquini pidió cambios" in cuerpo_a_nahuel
    assert "certificado del proveedor" in cuerpo_a_nahuel.lower()

    # -- Seguimiento de review-8b7dde28 (T6g): el aviso 1 ("Aprobar"/"Pedir
    # cambios") es una sola `pending_action` con dos opciones -- tocar
    # cualquiera de las dos la resuelve entera (`resolver_pendiente`,
    # `db/esquema.sql`: `update ... where id = a.id`, no `where token = ...`).
    # Después de tocar "Pedir cambios", el "Aprobar" viejo del MISMO aviso
    # queda muerto sin hacer falta nada más: nunca abre una vista previa de
    # `aprobar_tarea` ni cambia el estado de la tarea que "Pedir cambios" ya
    # devolvió a `en_curso`.
    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid_aviso_1,))
        assert cur.fetchone()["estado"] == "resuelta"

    token_aprobar_viejo = next(f["token"] for f in opciones_aviso_1
                               if f["etiqueta"] == "Aprobar")
    assert _tocar(cliente, token_aprobar_viejo, tg_marcos).status_code == 200

    with admin(conn) as cur:
        assert "ya no está vigente" in _outbox_ultimo(cur, ws, tg_marcos).lower()
        cur.execute(
            """select count(*) n from pending_action
                where herramienta = 'aprobar_tarea' and estado = 'esperando'""")
        assert cur.fetchone()["n"] == 0
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_curso"

    # -- 3. Nahuel entrega otra vez: evidencia NUEVA (T6b), aviso NUEVO (T6d) -----
    filas = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Nahuel Gimenez",
                       tg_nahuel)
    _tocar_etiqueta(cliente, filas, "Ya la terminé", tg_nahuel)

    with admin(conn) as cur:
        # T6b: la evidencia de la primera entrega ya no cuenta -- vuelve a
        # pedirla, no pasa directo a la vista previa.
        assert "qué hiciste" in _outbox_ultimo(cur, ws, tg_nahuel).lower()

    assert _mensaje(cliente, tg_nahuel,
                    "Ahora sí, con el certificado adjunto.").status_code == 200
    assert _confirmar(cliente, conn, ws, "actualizar_estado", tg_nahuel,
                      tg_nahuel).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_revision"
        cur.execute("select count(*) n from evidence where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 2      # se suma, no reemplaza a la primera

        pid_aviso_2 = _pendiente(cur, ws, P.SENTINEL_MENU_TAREA, chat_id=tg_marcos)
        opciones_aviso_2 = _opciones(cur, pid_aviso_2)
        cur.execute(
            """select dedupe_key from message_outbox
                where workspace_id = %s and chat_id = %s
               order by programado_para desc, dedupe_key desc limit 1""",
            (ws, tg_marcos))
        dedupe_2 = cur.fetchone()["dedupe_key"]
    assert pid_aviso_2 != pid_aviso_1          # T6d: otra pending_action
    assert dedupe_2 != dedupe_1                # T6d: otra clave de dedupe

    # -- 4. Marcos aprueba: cierra por la aprobación fresca (T6a, ADR 0008) ------
    token_aprobar = next(f["token"] for f in opciones_aviso_2 if f["etiqueta"] == "Aprobar")
    assert _tocar(cliente, token_aprobar, tg_marcos).status_code == 200
    assert _confirmar(cliente, conn, ws, "aprobar_tarea", tg_marcos,
                      tg_marcos).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "terminada"
        cur.execute(
            """select count(*) n from approval
                where sujeto_id = %s and decision = 'aprobado'""", (tid,))
        assert cur.fetchone()["n"] == 1


# ---------------------------------------------------------------------------
# Variante (T6c): "Pedir cambios" sigue funcionando por el webhook con una
# dependencia bloqueante todavía abierta -- antes de la corrección, el
# insert a `en_curso` chocaba con el disparador de `0008` y el aprobador no
# podía pedir cambios en absoluto.
# ---------------------------------------------------------------------------

def test_pedir_cambios_con_dependencia_bloqueante_sigue_por_telegram(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        _dependencia_bloqueante(cur, ws, tid)
        tg_nahuel = _tg(cur, "Nahuel Gimenez")
        tg_marcos = _tg(cur, "Marcos Tarquini")
    conn.commit()

    filas = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Nahuel Gimenez", tg_nahuel)
    _tocar_etiqueta(cliente, filas, "Ya la terminé", tg_nahuel)
    assert _mensaje(cliente, tg_nahuel, "Listo, con foto.").status_code == 200
    assert _confirmar(cliente, conn, ws, "actualizar_estado", tg_nahuel,
                      tg_nahuel).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_revision"
        pid_aviso = _pendiente(cur, ws, P.SENTINEL_MENU_TAREA, chat_id=tg_marcos)
        token_pedir = next(f["token"] for f in _opciones(cur, pid_aviso)
                          if f["etiqueta"] == "Pedir cambios")

    assert _tocar(cliente, token_pedir, tg_marcos).status_code == 200
    assert _mensaje(cliente, tg_marcos,
                    "Falta terminar la otra tarea antes.").status_code == 200
    assert _confirmar(cliente, conn, ws, "pedir_cambios_tarea", tg_marcos,
                      tg_marcos).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        # T6c: restauración a `en_curso`, exenta del gate de arranque -- no
        # el `psycopg.errors.RaiseException` que el disparador de `0008`
        # devolvía antes de la corrección.
        assert cur.fetchone()["estado"] == "en_curso"


# ---------------------------------------------------------------------------
# T6i (`odd/tasks/prisma-orienta.md`; ADR 0009, enmienda 2026-09-27):
# evidencia nueva sobre una tarea en_revision, de alguien que no es el
# aprobador, retira el aviso de entrega que tiene esperando y manda uno
# nuevo con toda la evidencia -- acá por "Adjuntar evidencia", de punta a
# punta por el webhook (la entrega repetida y el caso del propio aprobador
# ya tienen cobertura a nivel de `herramientas.ejecutar`, en
# `tests/test_entrega_con_evidencia.py`).
# ---------------------------------------------------------------------------

def test_adjuntar_evidencia_en_revision_retira_el_aviso_del_aprobador_por_telegram(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        tg_nahuel = _tg(cur, "Nahuel Gimenez")
        tg_marcos = _tg(cur, "Marcos Tarquini")
    conn.commit()

    filas = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Nahuel Gimenez", tg_nahuel)
    _tocar_etiqueta(cliente, filas, "Ya la terminé", tg_nahuel)
    assert _mensaje(cliente, tg_nahuel, "Primera entrega.").status_code == 200
    assert _confirmar(cliente, conn, ws, "actualizar_estado", tg_nahuel,
                      tg_nahuel).status_code == 200

    with admin(conn) as cur:
        pid_aviso_1 = _pendiente(cur, ws, P.SENTINEL_MENU_TAREA, chat_id=tg_marcos)
        token_aprobar_1 = next(f["token"] for f in _opciones(cur, pid_aviso_1)
                               if f["etiqueta"] == "Aprobar")

    # Antes de que Marcos toque nada, Nahuel manda evidencia nueva por
    # "Adjuntar evidencia" -- no una entrega repetida.
    filas = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Nahuel Gimenez", tg_nahuel)
    _tocar_etiqueta(cliente, filas, "Adjuntar evidencia", tg_nahuel)
    assert _mensaje(cliente, tg_nahuel,
                    "Segunda evidencia, por si falta.").status_code == 200
    assert _confirmar(cliente, conn, ws, "adjuntar_evidencia", tg_nahuel,
                      tg_nahuel).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid_aviso_1,))
        assert cur.fetchone()["estado"] != "esperando"      # retirado, no esperando más

        pid_aviso_2 = _pendiente(cur, ws, P.SENTINEL_MENU_TAREA, chat_id=tg_marcos)
        assert pid_aviso_2 != pid_aviso_1                   # T6i: otro aviso
        cuerpo_aviso_2 = _outbox_ultimo(cur, ws, tg_marcos)
    assert "Primera entrega." in cuerpo_aviso_2
    assert "Segunda evidencia, por si falta." in cuerpo_aviso_2

    # El "Aprobar" del aviso viejo ya no vale: mismo criterio que el
    # "Aprobar" viejo tras "Pedir cambios" (arriba, seguimiento de
    # review-8b7dde28) -- nunca aplica nada.
    assert _tocar(cliente, token_aprobar_1, tg_marcos).status_code == 200
    with admin(conn) as cur:
        assert "ya no está vigente" in _outbox_ultimo(cur, ws, tg_marcos).lower()
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_revision"    # nunca se aprobó
        cur.execute("select count(*) n from approval where sujeto_id = %s", (tid,))
        assert cur.fetchone()["n"] == 0
