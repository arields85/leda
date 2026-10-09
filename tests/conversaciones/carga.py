"""El estado inicial de cada conversación de prueba, escrito en una base efímera (E2-7).

`odd/tasks/prueba-chica-del-motor.md`, secciones 5 ("Estado inicial") y 6. `sembrar` no sirve:
carga todo a diez días y rechaza un espacio con tareas. Esto escribe, como `admin`, exactamente
lo que cada conversación da por hecho (`tests/conversaciones/README.md`, "Formato"):

- **el espacio**, CoreWork en chico y con sus datos de verdad para el seguimiento: el horario
  (lunes a viernes, 09:00 a 17:00, sin feriados en el período de referencia), el aviso previo a
  tres días hábiles, la falta de respuesta escalada a Dirección y el tono del pack;
- **las personas** de `espacios/corework.yaml` que nombran las conversaciones, con quién aprueba
  el trabajo de cada una (Ismael aprueba el de Marcos), el referente técnico de cada área, como
  en el pack (a quien va la cadena de un bloqueo que nadie toma, C-5, conversación 34), y un
  administrador de plataforma con el bot de administración alcanzable;
- **las tareas** de la conversación: título, responsable, vencimiento (17:00 del día, el fin de
  la jornada), estado (un inicio, como el evento del día que dice; una `terminada`, con la
  aprobación que su cierre exige, de quien aprueba el trabajo del responsable; una `bloqueada`,
  con el bloqueo abierto que dice `bloqueo`, desde ese día), dependencias y
  su criterio de aceptación (`criterio`): concreto y comprobable, como lo pide la mecánica §13,
  porque la entrega lo compara con lo que la persona describe (`odd/tasks/fase-c.md`, decisión
  10). Si la conversación no lo dice, va uno de reserva, también concreto: sin criterio, ninguna
  tarea se podría cerrar al aprobarla (mecánica §5);
- **la política de evidencia** (`evidencia`, por área), si la conversación la nombra: lo que pide
  cada área y, por tipo, las clases que lo cubren y cómo se dice, de `espacios/corework.yaml`
  (ADR 0019, decisión 5); cada tarea pide lo de su área;
- **lo mandado antes** (`mandado_antes`): fotos y archivos que la persona dijo que eran de una
  tarea antes de entregarla (`archivo_de_tarea`), con el mensaje que los trajo;
- **las personas sin un chat con Leda** (`sin_telegram`): como en el pack, donde su Telegram está
  `PENDIENTE`; Leda no les puede escribir (C-5, conversación 32). Ninguna de ellas escribe en la
  conversación;
- **las cadencias** (`cadencias`), sólo las que la conversación nombra, como las carga el importador
  del pack (`cadence_job`, con su día y su hora traducidos a cron): las demás conversaciones las
  suponen apagadas (`README.md`, "Datos ficticios"; la 37, C-6);
- **el grupo del espacio** (`grupo`), el identificador de su chat de Telegram, como
  `telegram.grupo_gestion_id` del pack: con una cadencia al grupo (`audiencia: grupo`), el espacio
  tiene informe al grupo (decisión 35; la 36).

Lo que pasó antes en la conversación (avisos ya enviados, una pregunta ya contestada) no se
escribe a mano: lo corre el motor mismo como **preludio** (`corredor.py`), así queda igual que
si hubiera pasado. El saludo del día se apaga, como en las pruebas: si no, el despachador lo
antepone y cada texto cambia.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date, datetime, time
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import yaml

from leda.db import admin

ZONA = ZoneInfo("America/Argentina/Buenos_Aires")
FIN_DE_JORNADA = time(17, 0)

# Las personas de `espacios/corework.yaml` que nombran las conversaciones: nombre, rol, área y
# quién aprueba su trabajo (`aprobado_por`). Los Telegram son ficticios: el transporte es falso.
PERSONAS = {
    "Ismael": ("Ismael Soschinski", "direccion", "direccion", None),
    "Ariel": ("Ariel De Simone", "referente", "corelabs", "Ismael"),
    "Martin": ("Martín Forte", "referente", "it", "Ismael"),
    "Marcos": ("Marcos Tarquini", "referente", "ot", "Ismael"),
    "Nahuel": ("Nahuel Gimenez", "integrante", "ot", "Marcos"),
    "Mariano": ("Mariano Naim", "referente", "electricidad", "Ismael"),
    "Lucas": ("Lucas Natuche", "integrante", "it", "Martin"),
}
AREAS = {"direccion": "Dirección", "ot": "OT y automatización", "it": "Infraestructura IT",
         "corelabs": "Software e interfaz HMI",
         "electricidad": "Sistemas eléctricos y tableros"}
# El referente técnico de cada área, como en el pack (`referente`, ADR 0019, decisión 7b): a quien
# va la cadena de un bloqueo que nadie toma (C-5, decisión 5; la 34).
REFERENTES = {"direccion": "Ismael", "ot": "Marcos", "it": "Martin", "electricidad": "Mariano",
              "corelabs": "Ariel"}
# El de reserva, para una tarea cuya conversación no dice el suyo (C-3d, D1: cada tarea de las
# conversaciones lleva uno propio en su YAML).
CRITERIO_DE_LA_PRUEBA = ("Lo que pide el título de la tarea queda hecho y probado, y quien lo hizo "
                         "describe cómo lo probó y qué dio la prueba")
ROLES = {"direccion": ("Dirección", True), "referente": ("Referente técnico de área", False),
         "integrante": ("Integrante", False)}
OBJETIVO = "Conectar y automatizar equipos para que produzcan y entreguen datos"
PACK = Path(__file__).resolve().parents[2] / "espacios" / "corework.yaml"
TELEGRAM_BASE = 70_001
TELEGRAM_ADMIN = 79_999
# El tono del pack (`persona` en `espacios/corework.yaml`).
TONO = {"nombre_visible": "Leda", "registro": "vos", "formalidad": "profesional_cordial",
        "longitud": "breve", "emojis": False}


@dataclass
class Mundo:
    """Lo cargado: el espacio, las personas (por su nombre corto) y las tareas (por su clave
    en la conversación)."""

    workspace_id: str
    personas: dict[str, dict[str, Any]] = field(default_factory=dict)
    areas: dict[str, str] = field(default_factory=dict)            # slug -> area_id
    tareas: dict[str, str] = field(default_factory=dict)          # clave -> task_id
    titulos: dict[str, str] = field(default_factory=dict)         # clave -> título

    def clave_de_titulo(self, titulo: str) -> str | None:
        return next((k for k, t in self.titulos.items() if t == titulo), None)

    def persona_de_membresia(self, membership_id) -> str | None:
        return next((k for k, p in self.personas.items()
                     if p["membership_id"] == str(membership_id)), None)

    def persona_de_chat(self, chat_id: int) -> str | None:
        return next((k for k, p in self.personas.items() if p["telegram"] == chat_id), None)


def momento(texto: str) -> datetime:
    """"AAAA-MM-DD HH:MM", hora de Buenos Aires."""
    return datetime.strptime(texto, "%Y-%m-%d %H:%M").replace(tzinfo=ZONA)


def fin_del_dia(dia: str) -> datetime:
    return datetime.combine(date.fromisoformat(dia), FIN_DE_JORNADA, ZONA)


def cargar(conn, conversacion: dict[str, Any]) -> Mundo:
    """Escribe el estado inicial de la conversación y lo confirma."""
    with admin(conn) as cur:
        mundo, objetivo = _espacio(cur)
        pide = _politica(cur, mundo, conversacion.get("evidencia") or {})
        _tareas(cur, mundo, objetivo, conversacion.get("tareas") or {}, pide)
        _mandado_antes(cur, mundo, conversacion.get("mandado_antes") or [])
        _sin_telegram(cur, mundo, conversacion.get("sin_telegram") or [])
        _cadencias(cur, mundo, conversacion.get("cadencias") or [])
        if conversacion.get("grupo") is not None:
            cur.execute("update workspace set grupo_chat_id = %s where id = %s",
                        (int(conversacion["grupo"]), mundo.workspace_id))
    conn.commit()
    return mundo


def _cadencias(cur, mundo: Mundo, cadencias: list[dict[str, Any]]) -> None:
    """Las cadencias que nombra la conversación, con el día y la hora traducidos como los traduce
    el importador del pack (`importador._a_cron`)."""
    from leda.importador import _a_cron

    for c in cadencias:
        cur.execute("""insert into cadence_job (workspace_id, nombre, cron, audiencia,
                                               plantilla_clave)
                       values (%s, %s, %s, %s, %s)""",
                    (mundo.workspace_id, c["nombre"], _a_cron(c["cuando"]),
                     c.get("audiencia", "privado_cada_integrante"), c["nombre"]))


def _sin_telegram(cur, mundo: Mundo, personas: list[str]) -> None:
    """Las personas que no conectaron su chat con Leda: sin Telegram, como lo dice el pack."""
    for corto in personas:
        persona = mundo.personas[corto]
        cur.execute("update app_user set telegram_user_id = null where id = %s",
                    (persona["app_user_id"],))
        persona["telegram"] = None


def _espacio(cur) -> tuple[Mundo, str]:
    cur.execute("""insert into workspace (slug, nombre, zona_horaria, activo)
                   values ('corework', 'CoreWork', %s, true) returning id""", (ZONA.key,))
    ws = str(cur.fetchone()["id"])
    cur.execute("""insert into work_calendar (workspace_id, dias, hora_inicio, hora_fin)
                   values (%s, array['lunes','martes','miercoles','jueves','viernes'],
                           '09:00', '17:00')""", (ws,))
    cur.execute("""insert into persona_config (workspace_id, nombre_visible, registro, formalidad,
                                               longitud, emojis)
                   values (%s, %s, %s, %s, %s, %s)""",
                (ws, TONO["nombre_visible"], TONO["registro"], TONO["formalidad"],
                 TONO["longitud"], TONO["emojis"]))
    cur.execute("""insert into workspace_version (workspace_id, version, pack_hash)
                   values (%s, 1, 'corredor-prueba-chica')""", (ws,))
    cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                   values (%s, 'aviso_previo_dias_habiles', '3')""", (ws,))
    # Los días hábiles del bloqueo viejo, como en el pack (C-5, porción 5; la 36).
    cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                   values (%s, 'bloqueos', '{"escala_solo_a_los_dias": 5}')""", (ws,))
    areas = {}
    for slug, nombre in AREAS.items():
        cur.execute("""insert into area (workspace_id, slug, nombre) values (%s, %s, %s)
                       returning id""", (ws, slug, nombre))
        areas[slug] = str(cur.fetchone()["id"])
    roles = {}
    for slug, (nombre, final) in ROLES.items():
        cur.execute("""insert into rol (workspace_id, slug, nombre, autoridad_final)
                       values (%s, %s, %s, %s) returning id""", (ws, slug, nombre, final))
        roles[slug] = str(cur.fetchone()["id"])
    cur.execute("""insert into escalation_route (workspace_id, disparador, destino_rol_id)
                   values (%s, 'falta_persistente_de_respuesta', %s)""", (ws, roles["direccion"]))

    mundo = Mundo(ws)
    mundo.areas = areas
    for i, (corto, (nombre, rol, area, aprobado_por)) in enumerate(PERSONAS.items()):
        telegram = TELEGRAM_BASE + i
        cur.execute("insert into app_user (telegram_user_id, nombre) values (%s, %s) returning id",
                    (telegram, nombre))
        app_user = str(cur.fetchone()["id"])
        aprobador = mundo.personas[aprobado_por]["membership_id"] if aprobado_por else None
        cur.execute("""insert into membership (workspace_id, app_user_id, area_id, rol_id,
                                               aprobador_membership_id)
                       values (%s, %s, %s, %s, %s) returning id""",
                    (ws, app_user, areas[area], roles[rol], aprobador))
        mundo.personas[corto] = {"nombre": nombre, "app_user_id": app_user,
                                 "membership_id": str(cur.fetchone()["id"]),
                                 "telegram": telegram, "area_id": areas[area],
                                 "area": area}
    for area, corto in REFERENTES.items():
        cur.execute("update area set referente_membership_id = %s where id = %s",
                    (mundo.personas[corto]["membership_id"], areas[area]))
    # Sin esto el despachador antepone el saludo del día y cada texto cambia.
    cur.execute("""insert into greeting_state (membership_id, workspace_id, ultima_fecha_local)
                   select id, workspace_id, date '9999-12-31' from membership
                    where workspace_id = %s""", (ws,))
    # El administrador de plataforma, con el bot de administración alcanzable (le escribió una
    # vez): recibe los avisos de lo que no está en la lista (9g).
    cur.execute("""insert into app_user (telegram_user_id, nombre)
                   values (%s, 'Administración de la plataforma') returning id""",
                (TELEGRAM_ADMIN,))
    administrador = str(cur.fetchone()["id"])
    cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                (administrador,))
    cur.execute("""insert into audit_log (actor_app_user_id, actor_kind, accion, detalle)
                   values (%s, 'persona', 'mensaje_admin', %s)""",
                (administrador, json.dumps({"chat_id": TELEGRAM_ADMIN})))
    cur.execute("""insert into objective (workspace_id, tipo, titulo, estado)
                   values (%s, 'operativo', %s, 'activo') returning id""", (ws, OBJETIVO))
    return mundo, str(cur.fetchone()["id"])


def _politica(cur, mundo: Mundo, por_area: dict[str, list[str]]) -> dict[str, list[str]]:
    """La política de evidencia de las áreas que nombra la conversación, con las clases y las
    palabras de cada tipo del pack de CoreWork; devuelve lo que pide cada área."""
    if not por_area:
        return {}
    tipos = (yaml.safe_load(PACK.read_text("utf-8")).get("evidencia") or {}).get("tipos") or {}
    for area, pide in por_area.items():
        cur.execute("""insert into task_evidence_policy (workspace_id, area_id,
                                                         evidencia_requerida, tipos)
                       values (%s, %s, %s, %s)""",
                    (mundo.workspace_id, mundo.areas[area], list(pide),
                     json.dumps({t: tipos[t] for t in pide}, ensure_ascii=False)))
    return {area: list(pide) for area, pide in por_area.items()}


def _mandado_antes(cur, mundo: Mundo, mandado: list[dict[str, Any]]) -> None:
    """Lo que la persona dijo que era de una tarea antes de entregarla: cada archivo, con el
    mensaje que lo trajo y su anotación del lado del transporte, y dicho de esa tarea."""
    for i, m in enumerate(mandado):
        persona = mundo.personas[m.get("quien", "Marcos")]
        el = momento(m["el"])
        cur.execute(
            """insert into inbound_message (workspace_id, telegram_message_id, chat_id,
                                            app_user_id, texto, at)
               values (%s, %s, %s, %s, '', %s) returning id""",
            (mundo.workspace_id, 900_000 + i, persona["telegram"], persona["app_user_id"], el))
        entrante = str(cur.fetchone()["id"])
        contenido, clase = contenido_de(m["que"], m.get("nombre"), f"antes-{i}")
        cur.execute(
            """insert into archivo (workspace_id, contenido, sha256, tamano, tipo, clase,
                                    nombre_original, enviado_por_membership_id, recibido_en)
               values (%s, %s, %s, %s, 'x', %s, %s, %s, %s) returning id""",
            (mundo.workspace_id, contenido, hashlib.sha256(contenido).hexdigest(),
             len(contenido), clase, m.get("nombre"), persona["membership_id"], el))
        archivo = str(cur.fetchone()["id"])
        cur.execute(
            """insert into archivo_de_mensaje (workspace_id, inbound_message_id, archivo_id,
                                               que_llego, nombre_original, telegram_message_id,
                                               telegram_file_id, telegram_file_unique_id)
               values (%s, %s, %s, %s, %s, %s, 'antes', %s)""",
            (mundo.workspace_id, entrante, archivo, m["que"], m.get("nombre"), 900_000 + i,
             f"antes-{i}"))
        cur.execute(
            """insert into archivo_de_tarea (workspace_id, archivo_id, task_id,
                                             dicho_por_membership_id, at)
               values (%s, %s, %s, %s, %s)""",
            (mundo.workspace_id, archivo, mundo.tareas[m["tarea"]], persona["membership_id"],
             el))


def contenido_de(que: str, nombre: str | None, semilla: str) -> tuple[bytes, str]:
    """Un contenido ficticio de lo que llegó, distinto para cada semilla, y su clase (la que
    detectaría `archivos.detectar`): una foto es un JPEG; un archivo, un comprimido o un texto
    según su nombre."""
    marca = semilla.encode("utf-8")
    if que == "foto":
        return b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + marca + b"\xff\xd9", "imagen"
    if que == "video":
        return b"\x00\x00\x00\x20ftypisom" + marca, "video"
    if (nombre or "").lower().endswith((".zip", ".7z", ".rar")):
        return b"PK\x03\x04" + marca, "comprimido"
    return b"configuracion " + marca + b"\n", "texto"


def _tareas(cur, mundo: Mundo, objetivo: str, tareas: dict[str, dict[str, Any]],
            pide: dict[str, list[str]] | None = None) -> None:
    pide = pide or {}
    for clave, t in tareas.items():
        persona = mundo.personas[t["responsable"]]
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, estado, fecha_objetivo,
                                 evidencia_requerida, criterio_aceptacion)
               values (%s, %s, %s, %s, %s, 'asignada', %s, %s, %s) returning id""",
            (mundo.workspace_id, objetivo, t["titulo"], persona["area_id"],
             persona["membership_id"], fin_del_dia(str(t["vence"])),
             pide.get(persona["area"], []), t.get("criterio", CRITERIO_DE_LA_PRUEBA)))
        task_id = str(cur.fetchone()["id"])
        mundo.tareas[clave], mundo.titulos[clave] = task_id, t["titulo"]
        if t.get("bloqueo"):
            # Una tarea trabada (`estado: bloqueada`), con la causa que dijo la persona y desde
            # el día que dice: el bloqueo abierto que la traba, antes que su estado (mecánica
            # §3: no hay bloqueo sin causa; la 40, C-6).
            cur.execute("""insert into blocker (workspace_id, task_id, causa, abierto_en,
                                                abierto_por)
                           values (%s, %s, %s, %s, %s)""",
                        (mundo.workspace_id, task_id, t["bloqueo"],
                         momento(f"{t['desde']} 10:00"), persona["membership_id"]))
        estado = t.get("estado", "asignada")
        if estado != "asignada":
            # El estado es la proyección de sus eventos: el inicio, con el día que dice.
            desde = t.get("desde")
            if estado == "terminada":
                # El cierre lo comprueba la base (mecánica §5): sin la aprobación de quien
                # aprueba el trabajo del responsable, no queda terminada.
                cur.execute("""insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                                     aprobador_membership_id, decision)
                               select %s, 'tarea', %s, aprobador_membership_id, 'aprobado'
                                 from membership where id = %s""",
                            (mundo.workspace_id, task_id, persona["membership_id"]))
            cur.execute(
                """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                 actor_kind, actor_app_user_id, motivo, at)
                   values (%s, 'asignada', %s, 'persona', %s, 'estado inicial de la prueba',
                           %s)""",
                (task_id, estado, persona["app_user_id"],
                 momento(f"{desde} 10:00") if desde else datetime.now(ZONA)))
    for clave, t in tareas.items():
        if t.get("depende_de"):
            cur.execute("""insert into dependency (workspace_id, origen_task_id, destino_task_id,
                                                   tipo)
                           values (%s, %s, %s, 'bloqueante')""",
                        (mundo.workspace_id, mundo.tareas[t["depende_de"]], mundo.tareas[clave]))
