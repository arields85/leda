"""Corrida de un escenario del banco por el circuito real y grabación del
proveedor, para poder repetir después una falla con `ProveedorGuionado`
(`docs/validation/README.md`, capa D).

El punto de entrada es `gateway.procesar_update`: el mismo camino que un
mensaje real de Telegram (`odd/tasks/banco-conversacional.md`, "Diseño
acordado"). No se usa `agente.responder` directo porque se saltearía
`route_intent` y el alta guiada de tareas.
"""

from __future__ import annotations

import contextlib
import time
from dataclasses import dataclass, field
from typing import Any

import prisma.llm as llm_modulo
from prisma import gateway
from prisma import pendientes as P
from prisma.db import admin
from prisma.llm import (IntentAction, IntentRoute, Llamada, Proveedor,
                        ProveedorGuionado, Respuesta)

# 'objective', 'evidence' y 'approval' se agregaron en T4 (banco-conversacional
# -> vista-previa-y-confirmacion): son las tablas que escriben crear_objetivo,
# adjuntar_evidencia y aprobar_tarea -- sin ellas, `conteos_delta` nunca podía
# ver esos efectos.
TABLAS_ESTADO = ("task", "task_draft", "blocker", "dependency",
                 "task_state_event", "message_outbox", "objective",
                 "evidence", "approval")


# ---------------------------------------------------------------------------
# Serialización de rutas y respuestas: la forma común entre lo que graba el
# proveedor real y lo que `ProveedorGuionado` sabe reproducir.
# ---------------------------------------------------------------------------


def _ruta_a_dict(ruta: IntentRoute) -> dict:
    return {"action": ruta.action.value, "task": dict(ruta.task),
            "trabajos": list(ruta.trabajos), "personas": list(ruta.personas)}


def _dict_a_ruta(d: dict) -> IntentRoute:
    # `.get(..., ())` con default: una grabación de antes de T2 no tiene
    # estas dos claves y tiene que seguir cargando (`aclaracion-con-botones`,
    # T2).
    return IntentRoute(
        IntentAction(d["action"]), dict(d.get("task", {})),
        tuple(d.get("trabajos", ())), tuple(d.get("personas", ())))


def _respuesta_a_dict(r: Respuesta) -> dict:
    return {"texto": r.texto,
            "llamadas": [{"id": c.id, "nombre": c.nombre, "args": c.args}
                        for c in r.llamadas]}


def _dict_a_respuesta(d: dict) -> Respuesta:
    return Respuesta(
        texto=d.get("texto", ""),
        llamadas=[Llamada(id=c["id"], nombre=c["nombre"], args=c["args"])
                 for c in d.get("llamadas", [])])


@dataclass
class ProveedorGrabador:
    """Envuelve a un proveedor real (o a cualquiera que cumpla `Proveedor`);
    graba cada llamada, su resultado y su latencia, en una forma
    serializable a JSON y recargable en un `ProveedorGuionado` para el
    replay determinista (`tests/banco/test_replays.py`)."""

    interno: Proveedor
    rutas: list[dict] = field(default_factory=list)
    respuestas: list[dict] = field(default_factory=list)

    def route_intent(self, text: str) -> IntentRoute:
        inicio = time.perf_counter()
        ruta = self.interno.route_intent(text)
        latencia = time.perf_counter() - inicio
        self.rutas.append({"entrada": text, "salida": _ruta_a_dict(ruta),
                           "latencia_s": latencia})
        return ruta

    def responder(self, sistema, mensajes, herramientas) -> Respuesta:
        inicio = time.perf_counter()
        r = self.interno.responder(sistema, mensajes, herramientas)
        latencia = time.perf_counter() - inicio
        self.respuestas.append({"salida": _respuesta_a_dict(r),
                                "latencia_s": latencia})
        return r

    def a_json(self) -> dict:
        return {"rutas": list(self.rutas), "respuestas": list(self.respuestas)}


def guionado_desde_grabacion(grabacion: dict) -> ProveedorGuionado:
    """Reconstruye un `ProveedorGuionado` desde el JSON de una grabación
    (`ProveedorGrabador.a_json()`, ya redondeado por un `json.dumps`/`loads`
    o leído de un archivo de replay)."""
    rutas = [_dict_a_ruta(r["salida"]) for r in grabacion.get("rutas", [])]
    guion = [_dict_a_respuesta(r["salida"]) for r in grabacion.get("respuestas", [])]
    return ProveedorGuionado(guion=guion, rutas=rutas)


# ---------------------------------------------------------------------------
# Siembra de precondiciones simuladas
# ---------------------------------------------------------------------------


def _area_id(cur, ws: str, slug: str):
    cur.execute("select id from area where workspace_id = %s and slug = %s", (ws, slug))
    fila = cur.fetchone()
    if not fila:
        raise LookupError(f"No existe el área '{slug}' en este espacio.")
    return fila["id"]


def _membership_id(cur, ws: str, nombre: str):
    cur.execute(
        """select m.id from membership m join app_user u on u.id = m.app_user_id
            where m.workspace_id = %s and u.nombre = %s""", (ws, nombre))
    fila = cur.fetchone()
    if not fila:
        raise LookupError(f"'{nombre}' no es integrante de este espacio.")
    return fila["id"]


def _crear_tarea_semilla(cur, ws: str, *, titulo: str, area: str, responsable: str,
                         estado: str = "asignada", fecha_objetivo=None,
                         criterio_aceptacion: str = "Simulado: criterio de prueba del banco.") -> str:
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo, estado)
           values (%s, 'operativo', %s, 'activo') returning id""",
        (ws, f"Objetivo simulado de {titulo}"))
    obj = cur.fetchone()["id"]
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, fecha_objetivo,
                             criterio_aceptacion, evidencia_requerida)
           values (%s, %s, %s, %s, %s, %s, %s, array['explicacion'])
           returning id""",
        (ws, obj, titulo, _area_id(cur, ws, area), _membership_id(cur, ws, responsable),
         fecha_objetivo, criterio_aceptacion))
    tid = cur.fetchone()["id"]
    cur.execute(
        "insert into task_state_event (task_id, estado_nuevo, actor_kind, at) "
        "values (%s, %s, 'sistema', clock_timestamp())", (tid, estado))
    return str(tid)


def _crear_bloqueo_semilla(cur, ws: str, tarea_id: str, *, causa: str,
                           abierto_por: str | None = None) -> str:
    abierto_por_id = _membership_id(cur, ws, abierto_por) if abierto_por else None
    cur.execute(
        """insert into blocker (workspace_id, task_id, causa, abierto_por)
           values (%s, %s, %s, %s) returning id""",
        (ws, tarea_id, causa, abierto_por_id))
    bid = cur.fetchone()["id"]
    cur.execute(
        """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                         actor_kind, motivo, at)
           values (%s, (select estado from task where id = %s), 'bloqueada',
                   'sistema', %s, clock_timestamp())""",
        (tarea_id, tarea_id, causa))
    return str(bid)


def _crear_dependencia_semilla(cur, ws: str, origen_id: str, destino_id: str,
                               tipo: str = "bloqueante") -> str:
    cur.execute(
        """insert into dependency (workspace_id, origen_task_id, destino_task_id, tipo)
           values (%s, %s, %s, %s) returning id""",
        (ws, origen_id, destino_id, tipo))
    return str(cur.fetchone()["id"])


def recolectar_efectos(cur, ids_semilla: dict[str, str]) -> dict:
    """Estado y efectos observados en la base, con los IDs de semilla del
    escenario (no los UUID reales) -- lo que `comprobar_efectos` compara
    contra `Escenario.efectos`. Sólo mira las tareas que el escenario
    sembró; una dependencia entre dos tareas sembradas aparece traducida a
    sus dos IDs de semilla, en el sentido real que tiene en la base."""
    tareas: dict[str, dict] = {}
    bloqueos_abiertos: dict[str, int] = {}
    for seed_id, uuid_ in ids_semilla.items():
        cur.execute("select estado from task where id = %s", (uuid_,))
        fila = cur.fetchone()
        if not fila:
            continue
        tareas[seed_id] = {"estado": fila["estado"]}
        cur.execute(
            "select count(*) n from blocker where task_id = %s and resuelto_en is null",
            (uuid_,))
        bloqueos_abiertos[seed_id] = cur.fetchone()["n"]

    dependencias: list[dict] = []
    for seed_origen, uuid_origen in ids_semilla.items():
        cur.execute(
            "select destino_task_id, tipo from dependency where origen_task_id = %s",
            (uuid_origen,))
        for fila in cur.fetchall():
            destino_uuid = str(fila["destino_task_id"])
            seed_destino = next(
                (s for s, u in ids_semilla.items() if str(u) == destino_uuid), None)
            if seed_destino:
                dependencias.append(
                    {"origen": seed_origen, "destino": seed_destino, "tipo": fila["tipo"]})

    return {"tareas": tareas, "bloqueos_abiertos": bloqueos_abiertos,
            "dependencias": dependencias}


def filas_respuesta(cur, workspace_id: str, chat_id: int,
                    ids_previos: set) -> list[dict]:
    """Filas nuevas de `message_outbox` que son la respuesta visible de este
    turno, con lo que hace falta para saber si ofrecieron una elección:
    `pending_action_id` (confirmación o elección, `agente.py`,
    `_encolar_confirmacion`/`_encolar_eleccion`) e `intake_choice_set_id`
    (alta guiada de tarea, `ingreso_tareas.py::_open_choices`) -- las mismas
    dos columnas que arma los botones al despachar
    (`despachador.py::_botones`)."""
    cur.execute(
        """select id, cuerpo, pending_action_id, intake_choice_set_id
            from message_outbox
            where workspace_id = %s and chat_id = %s and es_respuesta
            order by programado_para""",
        (workspace_id, chat_id))
    return [f for f in cur.fetchall() if f["id"] not in ids_previos]


def respuesta_ofrecio_opciones(filas: list[dict]) -> bool:
    """True si alguna fila de la respuesta ofreció una elección con botones
    (`filas_respuesta`: `pending_action_id` o `intake_choice_set_id` no
    nulo)."""
    return any(f.get("pending_action_id") is not None
              or f.get("intake_choice_set_id") is not None for f in filas)


def conteos_delta(antes: dict[str, int], despues: dict[str, int]) -> dict[str, int]:
    """Diferencia despues-antes por tabla, para comparar contra
    `Escenario.efectos["conteos_delta"]`."""
    return {tabla: despues.get(tabla, 0) - antes.get(tabla, 0)
           for tabla in set(antes) | set(despues)}


def sembrar_precondiciones(cur, ws: str, precondiciones: dict) -> dict[str, str]:
    """Crea el estado ficticio de un escenario (tareas, bloqueos,
    dependencias) bajo una conexión de administración, y devuelve el mapeo
    de los IDs locales del escenario (p. ej. 't1') a los UUID reales."""
    ids: dict[str, str] = {}
    for t in precondiciones.get("tareas", []):
        ids[t["id"]] = _crear_tarea_semilla(
            cur, ws, titulo=t["titulo"], area=t["area"], responsable=t["responsable"],
            estado=t.get("estado", "asignada"), fecha_objetivo=t.get("fecha_objetivo"))
    for b in precondiciones.get("bloqueos", []):
        _crear_bloqueo_semilla(cur, ws, ids[b["tarea"]], causa=b["causa"],
                               abierto_por=b.get("abierto_por"))
    for d in precondiciones.get("dependencias", []):
        _crear_dependencia_semilla(cur, ws, ids[d["origen"]], ids[d["destino"]],
                                   tipo=d.get("tipo", "bloqueante"))
    return ids


# ---------------------------------------------------------------------------
# Corrida de un escenario
# ---------------------------------------------------------------------------


@dataclass
class ResultadoCorrida:
    escenario_id: str
    indice: int
    respuesta_texto: str
    herramientas_ejecutadas: list[str]
    conteos_antes: dict[str, int]
    conteos_despues: dict[str, int]
    latencia_total_s: float
    grabacion: dict
    bloqueado: bool = False
    motivo_bloqueo: str = ""
    ofrecio_opciones: bool = False
    # Conteos por tabla justo antes de simular el toque en Confirmar (T4,
    # ADR 0005 decisión 1) -- `None` si el turno no dejó ninguna propuesta
    # con botón Confirmar, y entonces no hay nada que tocar ni que comprobar
    # (`comprobadores.comprobar_sin_efectos_antes_de_confirmar`).
    conteos_antes_del_toque: dict[str, int] | None = None
    # Herramientas de las 8 que ya habían dejado su entrada en `audit_log`
    # (`herramienta:<nombre>`) en ese mismo momento -- antes de cualquier
    # toque posible, haya o no propuesta. Señal primaria de la propiedad
    # central: a diferencia de un conteo por tabla, ve una herramienta que
    # sólo actualiza una fila que ya existía (`resolver_bloqueo`,
    # `actualizar_estado`) y, sobre todo, ve una que se ejecutó directo, sin
    # que ninguna propuesta haya llegado a esperar un Confirmar (revisión
    # del orquestador, T4, 2026-09-24).
    herramientas_antes_del_toque: tuple[str, ...] = ()


def _conteos(cur, ws: str) -> dict[str, int]:
    conteos: dict[str, int] = {}
    for tabla in TABLAS_ESTADO:
        cur.execute(f"select count(*) n from {tabla} where workspace_id = %s", (ws,))
        conteos[tabla] = cur.fetchone()["n"]
    return conteos


def _herramientas_registradas(cur, workspace_id: str) -> list[str]:
    """Las herramientas que ya dejaron su entrada `herramienta:<nombre>` en
    `audit_log` hasta este momento -- sólo se escribe cuando la herramienta
    se ejecutó de verdad (`agente.py::responder`, `gateway._toque`), nunca
    al levantar `NecesitaConfirmacion`. Señal primaria de la propiedad
    central (T4): a diferencia de un conteo por tabla, ve una herramienta
    que sólo actualiza una fila que ya existía."""
    cur.execute(
        """select accion from audit_log
            where workspace_id = %s and accion like %s order by at""",
        (workspace_id, "herramienta:%"))
    return [f["accion"].split(":", 1)[1] for f in cur.fetchall()]


def _pendiente_para_confirmar(cur, workspace_id: str, chat_id: int) -> tuple[str, str] | None:
    """La última acción pendiente 'esperando' de este chat que ofrece un
    botón Confirmar -- la vista previa de una herramienta que escribe (T1,
    `pending_action` con huella). Una `NecesitaElegir` (candidatos ambiguos,
    p. ej. a quién asignar) tiene sus propios botones, sin Confirmar, y no se
    toca acá: el banco no adivina una elección por la persona.

    Devuelve `(pending_action_id, token_de_confirmar)`, o `None` si no hay
    ninguna o la que hay no ofrece Confirmar.
    """
    cur.execute(
        """select id from pending_action
            where workspace_id = %s and chat_id = %s and estado = 'esperando'
            order by creado_en desc limit 1""",
        (workspace_id, chat_id))
    fila = cur.fetchone()
    if not fila:
        return None
    pid = str(fila["id"])
    try:
        opcion = P.opcion_por_etiqueta(cur, pid, "Confirmar")
    except LookupError:
        return None
    return pid, opcion.token


def _telegram_id(conn, ws: str, nombre: str) -> int:
    with admin(conn) as cur:
        cur.execute(
            """select u.telegram_user_id t from membership m
                 join app_user u on u.id = m.app_user_id
                where m.workspace_id = %s and u.nombre = %s""",
            (ws, nombre))
        fila = cur.fetchone()
    if not fila or fila["t"] is None:
        raise LookupError(f"'{nombre}' no tiene telegram_user_id en el espacio.")
    return fila["t"]


def ejecutar_escenario(
    conn, workspace_id: str, slug: str, actor_nombre: str, mensajes: list[str],
    proveedor_real: Proveedor, *, escenario_id: str, indice: int,
    chat_id: int | None = None,
) -> ResultadoCorrida:
    """Corre un escenario por `gateway.procesar_update`, con
    `proveedor_real` envuelto en `ProveedorGrabador` e inyectado en lugar de
    `llm.desde_base`, y recolecta la evidencia de la corrida: respuesta
    visible, herramientas ejecutadas, estado antes/después y latencia.

    Un fallo durante el procesamiento (por ejemplo, infraestructura del
    escenario mal declarada) deja la corrida `bloqueado`, con el motivo, en
    vez de propagar la excepción -- así una corrida rota no corta el resto
    del lote.
    """
    tg_id = _telegram_id(conn, workspace_id, actor_nombre)
    chat = chat_id if chat_id is not None else tg_id

    grabador = ProveedorGrabador(proveedor_real)
    desde_base_original = llm_modulo.desde_base
    mantener_chat_activo_original = gateway.mantener_chat_activo
    acusar_toque_original = gateway.acusar_toque
    llm_modulo.desde_base = lambda cur, ws, key: grabador
    # El banco no habla con Telegram de verdad: el token del espacio de
    # pruebas es ficticio (`corework`, fixture) y no hay nada real a lo que
    # avisar que se está escribiendo, ni un acuse real que mandarle al tocar
    # Confirmar (`_toque`, `despachador.acusar_toque`).
    gateway.mantener_chat_activo = lambda *a, **k: contextlib.nullcontext()
    gateway.acusar_toque = lambda *a, **k: None

    with admin(conn) as cur:
        antes = _conteos(cur, workspace_id)
        cur.execute("select id from message_outbox where workspace_id = %s",
                    (workspace_id,))
        ids_previos = {f["id"] for f in cur.fetchall()}

    bloqueado = False
    motivo_bloqueo = ""
    conteos_antes_del_toque: dict[str, int] | None = None
    herramientas_antes_del_toque: list[str] = []
    inicio = time.perf_counter()
    try:
        for texto in mensajes:
            update = {"message": {"message_id": 1, "text": texto,
                                  "chat": {"id": chat}, "from": {"id": tg_id}}}
            gateway.procesar_update(conn, slug, update)

        # El turno pudo haber dejado una propuesta de una herramienta que
        # escribe esperando un Confirmar (T1/T2, ADR 0005 decisión 1): el
        # banco la confirma sola, por el mismo camino que un toque real de
        # Telegram (`gateway.procesar_update` con un `callback_query`,
        # `gateway._toque`) -- no un atajo que ejecute la herramienta
        # directo. Antes de tocar (haya o no propuesta), se guarda el
        # estado: es la evidencia de que hasta acá no se aplicó nada
        # (propiedad central, T4) -- `herramientas_antes_del_toque` se
        # captura siempre, no sólo cuando hay propuesta, porque el hueco que
        # tiene que atrapar es justo el de una herramienta que se ejecutó
        # directo, sin que ninguna propuesta haya llegado a esperar un
        # Confirmar.
        with admin(conn) as cur:
            herramientas_antes_del_toque = _herramientas_registradas(cur, workspace_id)
            pendiente = _pendiente_para_confirmar(cur, workspace_id, chat)
            if pendiente is not None:
                conteos_antes_del_toque = _conteos(cur, workspace_id)

        if pendiente is not None:
            _, token = pendiente
            toque = {"callback_query": {
                "id": "banco-confirmar", "from": {"id": tg_id},
                "data": f"{P.CALLBACK_PREFIJO}{token}",
                "message": {"message_id": 2, "chat": {"id": chat}}}}
            gateway.procesar_update(conn, slug, toque)
    except Exception as exc:  # noqa: BLE001 -- una corrida rota queda bloqueada, no cae la suite
        conn.rollback()
        bloqueado = True
        motivo_bloqueo = f"{type(exc).__name__}: {exc}"
    finally:
        llm_modulo.desde_base = desde_base_original
        gateway.mantener_chat_activo = mantener_chat_activo_original
        gateway.acusar_toque = acusar_toque_original
    latencia_total = time.perf_counter() - inicio

    with admin(conn) as cur:
        despues = _conteos(cur, workspace_id)
        filas = filas_respuesta(cur, workspace_id, chat, ids_previos)
        respuesta_texto = "\n".join(f["cuerpo"] for f in filas)
        ofrecio_opciones = respuesta_ofrecio_opciones(filas)
        herramientas_ejecutadas = _herramientas_registradas(cur, workspace_id)

    return ResultadoCorrida(
        escenario_id=escenario_id, indice=indice, respuesta_texto=respuesta_texto,
        herramientas_ejecutadas=herramientas_ejecutadas, conteos_antes=antes,
        conteos_despues=despues, latencia_total_s=latencia_total,
        grabacion=grabador.a_json(), bloqueado=bloqueado, motivo_bloqueo=motivo_bloqueo,
        ofrecio_opciones=ofrecio_opciones,
        conteos_antes_del_toque=conteos_antes_del_toque,
        herramientas_antes_del_toque=tuple(herramientas_antes_del_toque))
