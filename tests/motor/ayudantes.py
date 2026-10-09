"""Lo que comparten las pruebas del motor: el momento fijo, el contexto mínimo de un turno,
lecturas cortas de la base y los turnos de Marcos con la IA guionada.

Las pruebas de `prueba_chica/` se importaban unas a otras como bibliotecas de ayudantes; acá
lo compartido vive en este módulo, y ningún archivo de prueba importa otro. Los nombres de
allá, sin el guion bajo: `_tarea` es `nueva_tarea`, `_hora` es `octubre`, `_dice` es `dice`,
`_prevision` es `jugada_prevision`, `_bloqueo` es `jugada_bloqueo`, `_abierta` es
`abierta`, `_quien` es `solicitante` y `_toca`, `toca`; el `_avisos` de
`test_escalera.py` es `avisos_guardados`, su `_espera` es `espera_del_estado` y su `_para`,
`lo_que_salio_para`; el `_prevision` de `test_ancla.py` es `dice_una_prevision`; el
`_administrador` de `test_ciclo.py` es `administrador`. La IA que redacta, los días de la
escalera (`Dias`) y el reloj monótono a mano (`Monotono`) van con su nombre de allá; las
fixtures `espacio_con_escalera` y `dias`, en `conftest.py`. De `test_ia_real.py`, el proveedor
falso (`ProveedorFalso`) y la situación de ejemplo (`SITUACION`) van con su nombre; su `_ia` es
`ia_real_falsa`, su `_llamada`, `llamada_de_jugadas` y su `_texto`, `respuesta_de_texto`. De
`test_escuchar.py`, el Telegram falso (`TelegramFalso`) y el id de su bot van con su nombre; su
`_mensaje` es `mensaje_de_telegram` y su `_toque`, `toque_de_telegram`.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import httpx

from leda.autoridad import identificar_en_espacio
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.motor.avisos import enviar_avisos
from leda.motor.escalera import correr_escalera
from leda.motor.fichas import JUGADAS
from leda.motor.ia import IAGuionada, Jugada
from leda.motor.ia_real import NOMBRE_HERRAMIENTA, ClienteCompatible, IAReal
from leda.motor.instrucciones import Tono
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import procesar_toque, procesar_turno

AHORA = datetime(2026, 10, 5, 13, 0, tzinfo=timezone.utc)   # lunes, 10:00 en Buenos Aires
VIERNES_16 = datetime(2026, 10, 16, 20, 0, tzinfo=timezone.utc)
# Las dos tareas de Marcos en las conversaciones: la del mundo y la que agrega `nueva_tarea`.
T1 = {"alias": "T1", "titulo": "Revisar el tablero"}
T2 = {"alias": "T2", "titulo": "Probar las comunicaciones"}


@dataclass
class Quien:
    """Lo que el motor lee de quien escribe: su espacio y su membresía."""

    workspace_id: str
    membership_id: str
    nombre: str = ""


@dataclass
class ContextoMinimo:
    """Lo que `preguntas` lee del contexto de un turno (`fichas.Contexto`, en la capa 2): el
    cursor, quién, el momento, sus tareas y las preguntas de este mensaje."""

    cur: Any
    quien: Quien
    ahora: datetime
    calendario: Calendario
    tareas: list[dict[str, Any]] = field(default_factory=list)
    preguntas_del_turno: list[str] = field(default_factory=list)
    dejadas: list[str] = field(default_factory=list)


def contexto(cur, mundo: dict, persona: str = "Marcos", ahora: datetime = AHORA,
             tareas: list[dict[str, Any]] | None = None) -> ContextoMinimo:
    quien = Quien(mundo["id"], mundo["personas"][persona]["membership_id"], persona)
    return ContextoMinimo(cur, quien, ahora, Calendario.desde_base(cur, mundo["id"]),
                          tareas=list(tareas or []))


def uno(conn, sql: str, *args) -> dict | None:
    with admin(conn) as cur:
        cur.execute(sql, args)
        return cur.fetchone()


def todos(conn, sql: str, *args) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(sql, args)
        return cur.fetchall()


def cuantas(conn, tabla: str, donde: str = "true", *args) -> int:
    fila = uno(conn, f"select count(*) n from {tabla} where {donde}", *args)
    return fila["n"]


# --- Las tareas -------------------------------------------------------------------------------

def nueva_tarea(conn, mundo, titulo: str, estado: str = "asignada",
                fecha: datetime = VIERNES_16) -> str:
    """Otra tarea de Marcos, en el objetivo y el área de la del mundo."""
    with admin(conn) as cur:
        cur.execute("select objective_id, area_id from task where id = %s", (mundo["tarea"],))
        base = cur.fetchone()
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, estado, fecha_objetivo)
               values (%s, %s, %s, %s, %s, %s, %s) returning id""",
            (mundo["id"], base["objective_id"], titulo, base["area_id"],
             mundo["personas"]["Marcos"]["membership_id"], estado, fecha))
        tarea = str(cur.fetchone()["id"])
    conn.commit()
    return tarea


def estado_de(conn, tarea: str) -> str:
    return uno(conn, "select estado::text e from task where id = %s", tarea)["e"]


def poner_estado(conn, tarea: str, estado: str) -> None:
    """El estado inicial de una conversación, como un evento (el estado es su proyección)."""
    with admin(conn) as cur:
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind, motivo)
                       select id, estado, %s, 'sistema', 'estado inicial de la prueba'
                         from task where id = %s""", (estado, tarea))
    conn.commit()


def cambiar_el_vencimiento(conn, mundo, vence: datetime | None) -> None:
    """La fecha comprometida es inmutable en la base; la cambiará la plataforma (ADR 0017,
    decisión 4). La prueba la cambia como lo haría ella, con la guarda apagada un momento."""
    with conn.transaction(), conn.cursor() as cur:
        cur.execute("alter table task disable trigger trg_bloquear_estado_directo")
        cur.execute("update task set fecha_objetivo = %s where id = %s", (vence, mundo["tarea"]))
        cur.execute("alter table task enable trigger trg_bloquear_estado_directo")
    conn.commit()


def abierta(conn) -> tuple[str, str | None] | None:
    """La pregunta abierta de la conversación: su tipo y su tarea."""
    fila = uno(conn, """select q.tipo, q.task_id from conversation_state s
                          join conversation_question q on q.id = s.pregunta_abierta_id
                         where q.cerrada_en is null""")
    return (fila["tipo"], str(fila["task_id"]) if fila["task_id"] else None) if fila else None


def avisos_guardados(conn, tipo: str | None = None) -> list[dict]:
    """Los avisos guardados, de un tipo o todos, en el orden en que se guardaron."""
    return todos(conn, """select * from scheduled_notice
                           where %s::text is null or tipo = %s
                           order by creado_en, dedupe_key""", tipo, tipo)


# --- Los turnos de Marcos y lo que Leda manda por su cuenta ----------------------------------

def octubre(dia: int, hora: int, minuto: int = 0) -> datetime:
    """Octubre de 2026, hora de Buenos Aires."""
    return datetime(2026, 10, dia, hora + 3, minuto, tzinfo=timezone.utc)


def dice(conn, escribe, *jugadas: Jugada, at: datetime = AHORA):
    """Un mensaje de Marcos, con las jugadas que elige la IA guionada."""
    quien, entrante = escribe("Marcos", "-", at=at)
    resultado = procesar_turno(conn, quien, entrante,
                               IAGuionada(jugadas=[list(jugadas)], redacciones=["Listo."]),
                               RelojFijo(at))
    conn.commit()
    assert resultado.error is None
    return resultado


def enviar(conn, mundo, ia: IAGuionada, at: datetime) -> dict:
    """Manda los avisos guardados cuya hora llegó (`avisos.enviar_avisos`)."""
    resumen = enviar_avisos(conn, mundo["id"], ia, RelojFijo(at))
    conn.commit()
    return resumen


def jugada_prevision(tarea: str, fecha: str, motivo: str | None = None) -> Jugada:
    return Jugada("anotar_prevision", {"tarea": tarea, "fecha": fecha,
                                       **({"motivo": motivo} if motivo else {})})


def jugada_bloqueo(tarea: str, causa: str | None = None) -> Jugada:
    return Jugada("anotar_bloqueo", {"tarea": tarea, **({"causa": causa} if causa else {})})


class Charla:
    """Los turnos de Marcos, uno por mensaje, con la IA guionada de cada uno."""

    def __init__(self, conn, escribe) -> None:
        self.conn, self.escribe = conn, escribe
        self.ia: IAGuionada | None = None

    def dice(self, *jugadas: Jugada, texto: str = "-"):
        quien, entrante = self.escribe("Marcos", texto)
        self.ia = IAGuionada(jugadas=[list(jugadas)], redacciones=["Listo."])
        resultado = procesar_turno(self.conn, quien, entrante, self.ia, RelojFijo(AHORA))
        self.conn.commit()
        assert resultado.error is None
        return resultado

    @property
    def redaccion(self) -> dict:
        return self.ia.pedidos_de_redaccion[-1]

    @property
    def situacion(self) -> dict:
        return self.ia.pedidos_de_jugadas[-1]


def solicitante(conn, mundo, nombre: str = "Marcos"):
    """Quién es la persona en el espacio, como la identifica el escuchador."""
    with espacio(conn, mundo["id"]) as cur:
        quien = identificar_en_espacio(cur, mundo["personas"][nombre]["telegram"], mundo["id"])
    conn.commit()
    return quien


def toca(conn, mundo, token: str, ia: IAGuionada | None = None, nombre: str = "Marcos"):
    """Un toque de la opción `token`; devuelve el resultado del turno y la IA guionada."""
    ia = ia or IAGuionada(redacciones=["Listo."])
    resultado = procesar_toque(conn, solicitante(conn, mundo, nombre), token,
                               mundo["personas"][nombre]["telegram"], ia, RelojFijo(AHORA))
    conn.commit()
    return resultado, ia


# --- La escalera, día por día --------------------------------------------------------------

@dataclass
class IAQueRedacta:
    """La IA de lo que Leda manda por su cuenta: redacta siempre y guarda lo que recibió."""

    nombre: str = "guionada"
    pedidos_de_redaccion: list[dict[str, Any]] = field(default_factory=list)

    def redactar(self, pedido: dict[str, Any]) -> str:
        self.pedidos_de_redaccion.append(pedido)
        return f"Aviso {len(self.pedidos_de_redaccion)}."

    def elegir_jugadas(self, situacion):     # la escalera nunca elige jugadas
        raise AssertionError("La escalera no le pide jugadas a la IA.")


class Dias:
    """Los ciclos de la escalera, día por día, con la IA que redacta."""

    def __init__(self, conn, mundo) -> None:
        self.conn, self.mundo = conn, mundo
        self.ia = IAQueRedacta()

    def ciclo(self, at: datetime) -> list[dict[str, Any]]:
        """Corre la escalera y manda lo guardado; devuelve lo que se redactó en este ciclo."""
        antes = len(self.ia.pedidos_de_redaccion)
        correr_escalera(self.conn, self.mundo["id"], RelojFijo(at))
        self.conn.commit()
        enviar_avisos(self.conn, self.mundo["id"], self.ia, RelojFijo(at))
        self.conn.commit()
        return self.ia.pedidos_de_redaccion[antes:]


def espera_del_estado(conn) -> dict | None:
    """La espera del estado de la tarea (`pending_reply`)."""
    return uno(conn, "select * from pending_reply where tipo = 'estado_de_la_tarea'")


def lo_que_salio_para(conn, mundo, nombre: str) -> list[str]:
    """Lo que salió por cuenta de Leda para esa persona, en orden."""
    return [f["cuerpo"] for f in todos(
        conn, """select cuerpo from message_outbox
                  where not es_respuesta and chat_id = %s order by programado_para, cuerpo""",
        mundo["personas"][nombre]["telegram"])]


def dice_una_prevision(conn, escribe, fecha: str, at) -> None:
    """Marcos da una fecha prevista para T1, con su motivo."""
    dice(conn, escribe, Jugada("anotar_prevision", {"tarea": "T1", "fecha": fecha,
                                                    "motivo": "el proveedor"}), at=at)


# --- El ciclo -------------------------------------------------------------------------------

class Monotono:
    """Los segundos que pasan entre vueltas, a mano."""

    def __init__(self) -> None:
        self.s = 0.0

    def __call__(self) -> float:
        return self.s


def administrador(conn) -> None:
    """Un administrador de plataforma con su chat registrado: recibe los avisos."""
    with admin(conn) as cur:
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (90000, 'Admin') returning id""")
        quien = str(cur.fetchone()["id"])
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                    (quien,))
        cur.execute("""insert into audit_log (actor_app_user_id, actor_kind, accion, detalle)
                       values (%s, 'persona', 'mensaje_admin', %s)""",
                    (quien, json.dumps({"chat_id": 90000})))
    conn.commit()


# --- La IA real, con un proveedor de mentira -------------------------------------------------

SITUACION = {"hoy": "2026-10-20", "mensaje": "llego el 27, el proveedor se demoró",
             "estado": None, "ultimo_aviso": {"tipo": "aviso_previo", "tarea": "T1"},
             "tareas": [{"alias": "T1", "titulo": "Programar PLC", "estado": "en_curso",
                         "fecha_objetivo": "2026-10-23T20:00:00+00:00"}],
             "ultimos_turnos": [], "jugadas_posibles": sorted(JUGADAS)}


@dataclass
class ProveedorFalso:
    """Un proveedor compatible con OpenAI, de mentira: contesta en orden lo preparado (un
    dict de respuesta, una excepción de httpx o un código de error) y guarda los pedidos."""

    respuestas: list
    pedidos: list = None
    demora: float = 0.0

    def __post_init__(self) -> None:
        self.pedidos = []

    def __call__(self, pedido: httpx.Request) -> httpx.Response:
        self.pedidos.append({"url": str(pedido.url), "cuerpo": json.loads(pedido.content),
                             "autorizacion": pedido.headers.get("authorization")})
        if self.demora:
            time.sleep(self.demora)
        respuesta = self.respuestas.pop(0)
        if isinstance(respuesta, Exception):
            raise respuesta
        if isinstance(respuesta, int):
            return httpx.Response(respuesta, json={"error": {"message": "x"}})
        return httpx.Response(200, json=respuesta)


def llamada_de_jugadas(argumentos) -> dict:
    """Una respuesta del proveedor que llama a la herramienta de las jugadas."""
    texto = argumentos if isinstance(argumentos, str) else json.dumps(argumentos)
    return {"choices": [{"message": {"content": None, "tool_calls": [{
        "id": "c1", "type": "function",
        "function": {"name": NOMBRE_HERRAMIENTA, "arguments": texto}}]}}]}


def respuesta_de_texto(texto: str | None) -> dict:
    """Una respuesta del proveedor con texto, sin herramienta."""
    return {"choices": [{"message": {"content": texto}}]}


def ia_real_falsa(proveedor: ProveedorFalso, *, tono: Tono | None = None,
                  plazo: float = 5.0) -> IAReal:
    """La IA real del motor sobre el proveedor de mentira: nunca sale a la red."""
    cliente = ClienteCompatible.crear(
        "openai/gpt-6-sol", "clave-de-prueba", "https://proveedor.invalid/v1",
        {"plazo_s": plazo}, transporte=httpx.MockTransport(proveedor))
    return IAReal(cliente, tono, nombre="openrouter/openai/gpt-6-sol")


# --- La entrada: Telegram, de mentira --------------------------------------------------------

ID_DEL_BOT = 7000


@dataclass
class TelegramFalso:
    """La API de un bot, de mentira: `getUpdates` entrega los lotes preparados, de a uno, y
    guarda cada llamada. Nunca sale a la red (`httpx.MockTransport`)."""

    lotes: list[list[dict]] = field(default_factory=list)
    webhook: str = ""
    llamadas: list[tuple[str, dict]] = field(default_factory=list)

    def __call__(self, pedido: httpx.Request) -> httpx.Response:
        metodo = pedido.url.path.rsplit("/", 1)[-1]
        parametros = json.loads(pedido.content) if pedido.content else {}
        self.llamadas.append((metodo, parametros))
        if metodo == "getUpdates":      # sólo este pedido consume un lote
            resultado = self.lotes.pop(0) if self.lotes else []
        else:
            resultado = {
                "getMe": {"id": ID_DEL_BOT, "username": "leda_motor_bot"},
                "deleteWebhook": True,
                "getWebhookInfo": {"url": self.webhook},
                "answerCallbackQuery": True,
                "setWebhook": True,
                # El indicador de actividad (el webhook usa este mismo cliente): el borrador,
                # "escribiendo…" y su retiro, la semilla como mensaje y su borrado (D8).
                "sendMessageDraft": True,
                "sendChatAction": True,
                "sendMessage": {"message_id": 900 + len(self.llamadas)},
                "deleteMessage": True,
            }[metodo]
        return httpx.Response(200, json={"ok": True, "result": resultado})

    def metodos(self) -> list[str]:
        return [m for m, _ in self.llamadas]

    def cliente(self) -> httpx.Client:
        return httpx.Client(transport=httpx.MockTransport(self))


def mensaje_de_telegram(update_id: int, texto: str, de: int, message_id: int | None = None,
                        tipo: str = "private") -> dict:
    """Un update de Telegram con un mensaje escrito."""
    return {"update_id": update_id, "message": {
        "message_id": message_id or update_id, "text": texto,
        "from": {"id": de, "first_name": "X"}, "chat": {"id": de, "type": tipo}}}


def toque_de_telegram(update_id: int, data: str, de: int, callback_id: str | None = None) -> dict:
    """Un update de Telegram con un botón tocado."""
    return {"update_id": update_id, "callback_query": {
        "id": callback_id or f"cb{update_id}", "from": {"id": de, "first_name": "X"},
        "data": data,
        "message": {"message_id": 1, "chat": {"id": de, "type": "private"}}}}


def a_la_vista(valor: Any) -> str:
    """Lo que un pedido de redacción deja decir por cuenta propia, como texto: todo menos lo que
    va dentro de `solo_si_pregunta` (decisión 11 del usuario, 2026-10-08)."""
    def sin(v: Any) -> Any:
        if isinstance(v, dict):
            return {k: sin(x) for k, x in v.items() if k != "solo_si_pregunta"}
        if isinstance(v, (list, tuple)):
            return [sin(x) for x in v]
        return v
    return json.dumps(sin(valor), ensure_ascii=False, default=str)


def solo_si_pregunta(valor: Any) -> str:
    """Lo que un pedido de redacción tiene dentro de `solo_si_pregunta`, en cualquier lugar,
    como texto."""
    encontrado: list[Any] = []

    def buscar(v: Any) -> None:
        if isinstance(v, dict):
            for k, x in v.items():
                if k == "solo_si_pregunta":
                    encontrado.append(x)
                else:
                    buscar(x)
        elif isinstance(v, (list, tuple)):
            for x in v:
                buscar(x)
    buscar(valor)
    return json.dumps(encontrado, ensure_ascii=False, default=str)
