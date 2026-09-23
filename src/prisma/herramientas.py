"""Herramientas del agente.

Todo lo que Prisma puede hacer en el mundo pasa por acá. El modelo de lenguaje
no escribe en la base: pide una herramienta, y la herramienta valida la
autoridad del solicitante antes de tocar nada.

Es la diferencia entre una regla en el prompt, que se puede convencer, y una
regla en el servidor, que no.

Cada herramienta declara:
  - `accion`, que es lo que `autoridad.verificar` va a evaluar;
  - un esquema de parámetros, que se le pasa al modelo;
  - un handler que recibe el cursor ya acotado al espacio activo.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

import psycopg
from psycopg.types.json import Jsonb

from .autoridad import (Denegado, Solicitante, puede_aprobar_tarea,
                         requiere_confirmacion, verificar)
from .salida import enqueue_outbox, normalize_visible_text, telegram_utf16_units


@dataclass(frozen=True)
class Herramienta:
    nombre: str
    accion: str
    descripcion: str
    parametros: dict[str, Any]
    handler: Callable[..., Any]
    # Algunas verificaciones dependen del área del sujeto, que no viene en los
    # argumentos: hay que leerla de la base primero. Esas herramientas hacen
    # la verificación adentro, con el área ya resuelta.
    valida_en_handler: bool = False
    # El chat desde el que escribieron. No está en el esquema que ve el
    # modelo y lo inyecta el servidor: si el modelo pudiera declararlo,
    # bastaría con que dijera "privado" para sortear una regla que depende
    # de dónde se pidió algo.
    necesita_chat: bool = False


REGISTRO: dict[str, Herramienta] = {}


def herramienta(nombre: str, accion: str, descripcion: str, parametros: dict,
                *, valida_en_handler: bool = False,
                necesita_chat: bool = False):
    def envoltura(fn):
        REGISTRO[nombre] = Herramienta(nombre, accion, descripcion, parametros,
                                       fn, valida_en_handler, necesita_chat)
        return fn
    return envoltura


class NecesitaConfirmacion(Exception):
    """La acción no se ejecuta hasta que una persona diga que sí.

    Los argumentos se llaman `argumentos` y no `args` porque `BaseException`
    ya usa ese nombre: `super().__init__(resumen)` lo pisa con `(resumen,)`.
    Guardar `e.args` acá terminaba persistiendo el texto del resumen donde
    tenían que ir los argumentos de la herramienta.
    """

    def __init__(self, resumen: str, herramienta: str, argumentos: dict) -> None:
        self.resumen = resumen
        self.herramienta = herramienta
        self.argumentos = argumentos
        super().__init__(resumen)


class NecesitaElegir(Exception):
    """Falta un dato que no se puede adivinar y hay candidatos concretos.

    No es un error: es la única respuesta honesta cuando "Mar" son tres
    personas. La herramienta no hace nada, y la elección vuelve como un
    identificador exacto.

    `descarta` nombra los argumentos de texto libre que causaron la
    ambigüedad: no vuelven a viajar, porque volverían a ser ambiguos.
    """

    def __init__(self, resumen: str, campo: str,
                 opciones: list[tuple[str, str]],
                 descarta: tuple[str, ...] = ()) -> None:
        self.resumen = resumen
        self.campo = campo
        self.opciones = opciones
        self.descarta = descarta
        self.herramienta = ""      # los completa `ejecutar`
        self.argumentos: dict = {}   # `args` es de BaseException, no se toca
        super().__init__(resumen)


def candidatos(cur: psycopg.Cursor, texto: str) -> list[tuple[str, str]]:
    """Integrantes cuyo nombre contiene `texto`, por la vista del espacio.

    Devuelve todos los que coinciden. Quedarse con el primero es justamente
    lo que hacía que una tarea terminara asignada a quien no era.
    """
    cur.execute(
        """select membership_id, nombre from integrante
            where nombre ilike %s and activo order by nombre""",
        (f"%{texto}%",))
    return [(f["nombre"], str(f["membership_id"])) for f in cur.fetchall()]


def ejecutar(cur: psycopg.Cursor, quien: Solicitante, nombre: str,
             args: dict[str, Any], *, ya_confirmada: bool = False,
             chat_id: int | None = None) -> Any:
    """Punto único de entrada. Nada llega a la base por otro camino.

    `ya_confirmada` es para lo que vuelve de una acción pendiente: la persona
    ya dijo que sí, y volver a frenarla sería un bucle. La autoridad se
    verifica igual — confirmar no es lo mismo que tener permiso.

    `chat_id` lo pone el servidor desde el update de Telegram, y sólo lo
    reciben las herramientas que lo declaran. No viaja en el esquema que ve
    el modelo: de dónde se pidió algo es un hecho, no un argumento.
    """
    if nombre == "crear_tarea":
        raise Denegado(
            "Para crear una tarea hay que completar primero su borrador guiado.")
    h = REGISTRO.get(nombre)
    if h is None:
        raise Denegado(f"No existe la herramienta '{nombre}'.")

    if not h.valida_en_handler:
        verificar(cur, quien, h.accion, area_id=args.get("area_id"))

    if requiere_confirmacion(h.accion) and not ya_confirmada:
        raise NecesitaConfirmacion(_resumen(h, args), nombre, dict(args))

    llamada = dict(args)
    if h.necesita_chat:
        llamada["chat_id"] = chat_id

    try:
        return h.handler(cur, quien, **llamada)
    except NecesitaElegir as e:
        # La herramienta sabe qué falta; acá se completa con qué hacía falta
        # para ella. El texto ambiguo no vuelve a viajar.
        e.herramienta = nombre
        e.argumentos = {k: v for k, v in args.items() if k not in e.descarta}
        raise


def _resumen(h: Herramienta, args: dict) -> str:
    detalle = ", ".join(f"{k}: {v}" for k, v in args.items() if v is not None)
    return f"{h.descripcion} ({detalle})"


def esquemas() -> list[dict[str, Any]]:
    """Definiciones para pasarle al modelo."""
    return [
        {"name": h.nombre, "description": h.descripcion,
         "input_schema": {
             "type": "object",
             # 'requerido' es marca nuestra: se traduce a `required` y no se
             # manda al proveedor. Gemini rechaza claves que no conoce.
             "properties": {k: {a: b for a, b in v.items() if a != "requerido"}
                            for k, v in h.parametros.items()},
             "required": [k for k, v in h.parametros.items()
                          if v.get("requerido")]}}
        for h in REGISTRO.values()
    ]


# ---------------------------------------------------------------------------
# Consulta
# ---------------------------------------------------------------------------

@herramienta(
    "consultar_tareas", "consultar",
    "Lista tareas del equipo. Sin filtros devuelve las del solicitante.",
    {"responsable": {"type": "string", "description": "nombre de la persona"},
     "estado": {"type": "string", "enum": ["asignada", "en_curso", "bloqueada",
                                           "en_revision", "terminada"]},
     "vencidas": {"type": "boolean"}})
def _consultar_tareas(cur, quien: Solicitante, responsable=None, estado=None,
                      vencidas=False):
    sql = ["""select t.id, t.titulo, t.estado, t.fecha_objetivo, i.nombre,
                     a.slug as area
                from task t
                join integrante i on i.membership_id = t.responsable_membership_id
                join area a on a.id = t.area_id
               where t.workspace_id = %s"""]
    params: list[Any] = [quien.workspace_id]

    if responsable:
        sql.append("and i.nombre ilike %s")
        params.append(f"%{responsable}%")
    elif not estado and not vencidas:
        sql.append("and t.responsable_membership_id = %s")
        params.append(quien.membership_id)
    if estado:
        sql.append("and t.estado = %s")
        params.append(estado)
    if vencidas:
        sql.append("and t.fecha_objetivo < now() "
                   "and t.estado in ('asignada','en_curso','bloqueada')")

    sql.append("order by t.fecha_objetivo nulls last limit 25")
    cur.execute(" ".join(sql), params)
    return [dict(f) for f in cur.fetchall()]


@herramienta(
    "consultar_personas", "consultar",
    "Quiénes son del equipo. Con un nombre parcial devuelve todos los que "
    "coinciden. Usala siempre que no estés seguro de a quién se refieren: "
    "nunca respondas de memoria quiénes coinciden con un nombre.",
    {"nombre": {"type": "string",
                "description": "parte del nombre, p. ej. 'Mar'"}})
def _consultar_personas(cur, quien: Solicitante, nombre=None):
    if not nombre:
        cur.execute(
            """select i.nombre, r.nombre as rol, a.nombre as area
                 from integrante i
                 join rol r on r.id = i.rol_id
                 join area a on a.id = i.area_id
                where i.activo order by i.nombre""")
        return [dict(f) for f in cur.fetchall()]

    cur.execute(
        """select i.nombre, r.nombre as rol, a.nombre as area
             from integrante i
             join rol r on r.id = i.rol_id
             join area a on a.id = i.area_id
            where i.activo and i.nombre ilike %s order by i.nombre""",
        (f"%{nombre}%",))
    return [dict(f) for f in cur.fetchall()]


@herramienta(
    "consultar_bloqueos", "consultar",
    "Bloqueos abiertos del equipo, con su antigüedad en días.", {})
def _consultar_bloqueos(cur, quien: Solicitante):
    cur.execute(
        """select b.id, b.causa, b.impacto, t.titulo, i.nombre,
                  extract(day from now() - b.abierto_en)::int as dias
             from blocker b
             join task t on t.id = b.task_id
             join integrante i on i.membership_id = t.responsable_membership_id
            where b.workspace_id = %s and b.resuelto_en is null
            order by b.abierto_en""",
        (quien.workspace_id,))
    return [dict(f) for f in cur.fetchall()]


# ---------------------------------------------------------------------------
# Trabajo
# ---------------------------------------------------------------------------

@herramienta(
    "crear_objetivo", "crear_tarea",
    "Crea un objetivo. Usalo cuando el trabajo que piden no encaja en ninguno "
    "de los que ya existen. Consultá primero los objetivos actuales.",
    {"titulo": {"type": "string", "requerido": True},
     "tipo": {"type": "string", "requerido": True,
              "enum": ["estrategico", "hito", "operativo"]},
     "padre_id": {"type": "string", "description": "objetivo del que cuelga"},
     "descripcion": {"type": "string"},
     "fecha_objetivo": {"type": "string", "description": "AAAA-MM-DD"}})
def _crear_objetivo(cur, quien: Solicitante, titulo, tipo, padre_id=None,
                    descripcion=None, fecha_objetivo=None):
    cur.execute(
        """insert into objective (workspace_id, parent_id, tipo, titulo,
                                  descripcion, fecha_objetivo, estado)
           values (%s, %s, %s, %s, %s, %s, 'activo') returning id""",
        (quien.workspace_id, padre_id, tipo, titulo, descripcion, fecha_objetivo))
    oid = cur.fetchone()["id"]
    cur.execute(
        """insert into objective_state_event (objective_id, estado_nuevo,
                                              actor_kind, actor_app_user_id)
           values (%s, 'activo', 'persona', %s)""",
        (oid, quien.app_user_id))
    return {"id": str(oid), "titulo": titulo}


def crear_borrador_tarea(cur, quien: Solicitante, titulo, objetivo_id=None,
                         area_slug=None, responsable=None, fecha_objetivo=None,
                         criterio_aceptacion=None, descripcion=None,
                         responsable_membership_id=None):
    """Internal Unit 1A draft boundary; never exposed as a model tool."""
    verificar(cur, quien, "crear_tarea")
    from .ingreso_tareas import (EVIDENCE_COUNT_LIMIT, EVIDENCE_ITEM_LIMIT,
                                 EVIDENCE_TOTAL_LIMIT, USER_FIELD_LIMITS)

    titulo = normalize_visible_text(titulo)
    descripcion = normalize_visible_text(descripcion) if descripcion else None
    criterio_aceptacion = (normalize_visible_text(criterio_aceptacion)
                           if criterio_aceptacion else None)
    responsible_query = normalize_visible_text(responsable) if responsable else None
    controlled = {
        "title": titulo, "description": descripcion or "",
        "responsible": responsible_query or "",
        "acceptance_criterion": criterio_aceptacion or "",
    }
    for field, value in controlled.items():
        if telegram_utf16_units(value) > USER_FIELD_LIMITS[field]:
            raise Denegado(
                f"El campo {field} debe tener hasta {USER_FIELD_LIMITS[field]} unidades.")
    responsable = responsible_query
    # `responsable_membership_id` no está en el esquema que ve el modelo: lo
    # inyecta la opción que eligió la persona. Un identificador exacto no se
    # vuelve a resolver.
    if responsable and not responsable_membership_id:
        posibles = candidatos(cur, responsable)
        if not posibles:
            # Antes esto insertaba NULL y devolvía la tarea como creada, así
            # que Prisma anunciaba una asignación que no existía.
            return {"creada": False,
                    "error": f"No encuentro a nadie que se llame "
                             f"«{responsable}» en el equipo."}
        if len(posibles) > 1:
            raise NecesitaElegir(
                resumen=f"¿A quién le asigno «{titulo}»?",
                campo="responsable_membership_id", opciones=posibles,
                descarta=("responsable",))
        responsable_membership_id = posibles[0][1]

    if responsable_membership_id:
        cur.execute(
            """select aprobador_membership_id, area_id, activo
                 from membership where id = %s""",
            (responsable_membership_id,))
        responsable_actual = cur.fetchone()
        if not responsable_actual or not responsable_actual["activo"]:
            return {"creada": False,
                    "error": "La persona responsable no está activa."}
        propone_propio = str(responsable_membership_id) == str(quien.membership_id)
        asigna_supervisado = (
            str(responsable_actual["aprobador_membership_id"] or "") ==
            str(quien.membership_id))
        if not propone_propio and not asigna_supervisado:
            raise Denegado(
                "Sólo podés proponer trabajo propio o asignar a quien supervisás.")

    cur.execute(
        """select a.id as area_id, p.evidencia_requerida, p.version
             from area a
             left join task_evidence_policy p
               on p.workspace_id = a.workspace_id and p.area_id = a.id
            where a.workspace_id = %s and a.slug = %s""",
        (quien.workspace_id, area_slug))
    politica = cur.fetchone()
    area_id = politica["area_id"] if politica else None
    evidencia = politica["evidencia_requerida"] if politica else None
    policy_version = politica["version"] if politica else None
    if evidencia is not None:
        evidence_units = [telegram_utf16_units(normalize_visible_text(item))
                          for item in evidencia]
        if (len(evidencia) > EVIDENCE_COUNT_LIMIT
                or any(units > EVIDENCE_ITEM_LIMIT for units in evidence_units)
                or sum(evidence_units) > EVIDENCE_TOTAL_LIMIT):
            cur.execute(
                """insert into incident
                     (workspace_id, severidad, resumen_sanitizado)
                   values (%s, 'media', %s)""",
                (quien.workspace_id,
                 "La política de evidencia excede el contrato visible."),
            )
            raise Denegado(
                "No puedo mostrar una opción configurada de este espacio. "
                "Pedile a quien lo administra que la revise.")
    if responsable_membership_id and str(responsable_actual["area_id"]) != str(area_id):
        raise Denegado("La persona responsable no pertenece al área de la tarea.")

    objetivo_snapshot = None
    if objetivo_id:
        cur.execute(
            """select jsonb_build_object('id', id, 'titulo', titulo,
                                          'estado', estado) as snapshot
                 from objective where id = %s""", (objetivo_id,))
        objetivo = cur.fetchone()
        objetivo_snapshot = objetivo["snapshot"] if objetivo else None

    cur.execute(
        """insert into task_draft
             (workspace_id, creado_por_membership_id, objective_id,
              objective_snapshot, titulo, descripcion, area_id,
              responsable_membership_id, fecha_objetivo,
              criterio_aceptacion, evidencia_requerida,
              evidencia_policy_version)
           values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           returning id, version""",
        (quien.workspace_id, quien.membership_id, objetivo_id,
         Jsonb(objetivo_snapshot) if objetivo_snapshot is not None else None,
         titulo, descripcion, area_id,
         responsable_membership_id, fecha_objetivo, criterio_aceptacion,
         evidencia, policy_version))
    borrador = cur.fetchone()

    faltantes = []
    if objetivo_snapshot is None:
        faltantes.append("objetivo_id")
    if responsable_membership_id is None:
        faltantes.append("responsable")
    if fecha_objetivo is None:
        faltantes.append("fecha_objetivo")
    if not criterio_aceptacion or not criterio_aceptacion.strip():
        faltantes.append("criterio_aceptacion")
    if evidencia is None:
        faltantes.append("politica_evidencia")
    if faltantes:
        return {"draft_id": str(borrador["id"]), "completa": False,
                "faltantes": faltantes}

    cur.execute(
        """select m.aprobador_membership_id,
                  aprobador.app_user_id, aprobador.telegram_user_id,
                  aprobador.nombre
             from membership m
             left join integrante aprobador
               on aprobador.membership_id = m.aprobador_membership_id
            where m.id = %s""", (responsable_membership_id,))
    autoridad = cur.fetchone()
    aprobador_id = autoridad["aprobador_membership_id"] if autoridad else None
    if aprobador_id is None:
        cur.execute(
            """select i.membership_id as aprobador_membership_id,
                      i.app_user_id, i.telegram_user_id, i.nombre
                 from integrante i join rol r on r.id = i.rol_id
                where r.autoridad_final and i.activo""")
        autoridad = cur.fetchone()
        aprobador_id = autoridad["aprobador_membership_id"] if autoridad else None
    if autoridad is None or aprobador_id is None or autoridad["telegram_user_id"] is None:
        return {"draft_id": str(borrador["id"]), "completa": True,
                "pendiente_revision": True, "notificada": False}

    cur.execute(
        """select jsonb_build_object(
                 'draft_id', id::text, 'version', version,
                  'titulo', titulo, 'descripcion', descripcion,
                  'objetivo', objective_snapshot,
                 'area_id', area_id::text,
                 'responsable_membership_id', responsable_membership_id::text,
                 'fecha_objetivo', fecha_objetivo::text,
                 'criterio_aceptacion', criterio_aceptacion,
                 'evidencia_requerida', to_jsonb(evidencia_requerida),
                 'evidencia_policy_version', evidencia_policy_version
               ) as preview
             from task_draft where id = %s""", (borrador["id"],))
    preview = cur.fetchone()["preview"]
    resumen = (f"Confirmar tarea: {titulo}. Fecha: {fecha_objetivo}. "
               f"Criterio: {criterio_aceptacion}. Evidencia: "
               f"{', '.join(evidencia) if evidencia else 'ninguna' }.")

    from .autoridad import Canal
    from .pendientes import registrar

    confirmador = Solicitante(
        app_user_id=str(autoridad["app_user_id"]), canal=Canal.ESPACIO,
        workspace_id=quien.workspace_id, membership_id=str(aprobador_id))
    ahora = datetime.now(timezone.utc)
    pendiente = registrar(
        cur, confirmador, herramienta="confirmar_borrador_tarea", args={},
        resumen=resumen, vence_en=ahora + timedelta(hours=8),
        chat_id=autoridad["telegram_user_id"], draft_id=str(borrador["id"]),
        draft_version=borrador["version"], preview=preview)
    enqueue_outbox(
        cur, workspace_id=quien.workspace_id,
        chat_id=autoridad["telegram_user_id"], text=resumen,
        recipient_membership_id=str(aprobador_id), scheduled_for=ahora,
        dedupe_key=(f"{quien.workspace_id}:draft-preview:{borrador['id']}:"
                    f"{borrador['version']}"), pending_action_id=pendiente.id,
    )
    return {"draft_id": str(borrador["id"]), "completa": True,
            "pendiente_revision": True, "notificada": True,
            "pending_action_id": pendiente.id}


@herramienta(
    "actualizar_estado", "actualizar_estado",
    "Mueve una tarea de estado. No cierra: para terminar hace falta que se "
    "cumplan las condiciones de cierre y estén las aprobaciones.",
    {"tarea_id": {"type": "string", "requerido": True},
     "estado": {"type": "string", "requerido": True,
                "enum": ["asignada", "en_curso", "en_revision", "terminada",
                         "cancelada"]},
     "motivo": {"type": "string"}})
def _actualizar_estado(cur, quien: Solicitante, tarea_id, estado, motivo=None):
    cur.execute("select estado from task where id = %s", (tarea_id,))
    fila = cur.fetchone()
    if not fila:
        return {"error": "esa tarea no existe en este equipo"}

    if estado == "terminada":
        cur.execute("select motivo_no_cierra_tarea(%s) as m", (tarea_id,))
        impedimento = cur.fetchone()["m"]
        if impedimento:
            # No es un error: es información que Prisma tiene que transmitir.
            return {"cerrada": False, "falta": impedimento}

    if estado == "en_curso":
        # Chequeo proactivo, igual que el de arriba: sin esto, el disparador
        # `trg_exigir_dependencias_resueltas` igual frena el insert, pero como
        # un error de base -- acá se convierte en información antes de
        # intentarlo (mecánica §4).
        #
        # Corrección tras revisión: si la tarea está `bloqueada`, este mismo
        # `actualizar_estado` puede recibir la transición de vuelta -- la
        # herramienta no exige bloqueos cerrados para salir de `bloqueada`
        # (deuda conocida) --, y volver de un bloqueo es una restauración,
        # no un arranque (mecánica §3).
        #
        # Segunda corrección tras revisión: no alcanza con mirar el estado
        # actual. `asignada` -> `registrar_bloqueo` -> `bloqueada` ->
        # `actualizar_estado(en_curso)` también tiene `fila["estado"] ==
        # "bloqueada"`, y esa tarea nunca arrancó -- eximirla ahí habría
        # dejado pasar justo lo que mecánica §4 prohíbe. La restauración
        # legítima exige además que el estado previo a la ÚLTIMA entrada a
        # `bloqueada` haya sido `en_curso`, igual que el disparador.
        restaura_en_curso = False
        if fila["estado"] == "bloqueada":
            cur.execute("select estado_previo_a_bloqueo(%s) as previo", (tarea_id,))
            restaura_en_curso = cur.fetchone()["previo"] == "en_curso"
        if not restaura_en_curso:
            cur.execute("select motivo_no_arranca_tarea(%s) as m", (tarea_id,))
            impedimento = cur.fetchone()["m"]
            if impedimento:
                return {"iniciada": False, "falta": impedimento}

    # Sin `returning`: `prisma_app` sólo tiene `insert` sobre
    # `task_state_event` (es append-only, ver el `revoke` en
    # `db/esquema.sql`), y `returning` exige además `select`. El token de
    # deduplicación se genera acá, no se lee de la fila insertada.
    cur.execute(
        """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                         actor_kind, actor_app_user_id, motivo)
           values (%s, %s, %s, 'persona', %s, %s)""",
        (tarea_id, fila["estado"], estado, quien.app_user_id, motivo))
    _avisar_dependencia_informativa(cur, quien, tarea_id, estado, uuid.uuid4())
    return {"estado": estado}


@herramienta(
    "registrar_bloqueo", "registrar_bloqueo",
    "Registra que una tarea está trabada, con su causa e impacto.",
    {"tarea_id": {"type": "string", "requerido": True},
     "causa": {"type": "string", "requerido": True},
     "impacto": {"type": "string"}})
def _registrar_bloqueo(cur, quien: Solicitante, tarea_id, causa, impacto=None):
    cur.execute("select estado from task where id = %s", (tarea_id,))
    fila = cur.fetchone()
    if not fila:
        return {"error": "esa tarea no existe en este equipo"}
    if fila["estado"] in ("terminada", "cancelada"):
        return {"error": "esa tarea ya está cerrada, no se le puede agregar un bloqueo"}

    cur.execute(
        """insert into blocker (workspace_id, task_id, causa, impacto, abierto_por)
           values (%s, %s, %s, %s, %s) returning id""",
        (quien.workspace_id, tarea_id, causa, impacto, quien.membership_id))
    bid = cur.fetchone()["id"]

    # Si ya estaba bloqueada, el bloqueo se suma a los que tiene: no hay una
    # segunda transición `bloqueada -> bloqueada` que registrar.
    if fila["estado"] != "bloqueada":
        cur.execute(
            """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                             actor_kind, actor_app_user_id, motivo)
               values (%s, %s, 'bloqueada', 'persona', %s, %s)""",
            (tarea_id, fila["estado"], quien.app_user_id, causa))
        _avisar_dependencia_informativa(cur, quien, tarea_id, "bloqueada", uuid.uuid4())
    return {"bloqueo_id": str(bid)}


@herramienta(
    "resolver_bloqueo", "resolver_bloqueo",
    "Cierra un bloqueo con su resolución. Cuando era el último abierto de la "
    "tarea, la tarea vuelve al estado que tenía antes de bloquearse.",
    {"bloqueo_id": {"type": "string", "requerido": True},
     "resolucion": {"type": "string", "requerido": True}},
    valida_en_handler=True)
def _resolver_bloqueo(cur, quien: Solicitante, bloqueo_id, resolucion):
    resolucion = (resolucion or "").strip()
    if not resolucion:
        raise Denegado("Hace falta contar cómo se resolvió para poder cerrarlo.")

    cur.execute(
        """select b.task_id, b.resuelto_en, b.abierto_por, b.escalado_a,
                  t.responsable_membership_id
             from blocker b join task t on t.id = b.task_id
            where b.id = %s""",
        (bloqueo_id,))
    fila = cur.fetchone()
    if not fila:
        # RLS ya deja pasar sólo lo del espacio activo: un id de otro espacio
        # llega hasta acá igual de vacío que uno que nunca existió.
        return {"error": "ese bloqueo no existe en este equipo"}
    if fila["resuelto_en"] is not None:
        return {"error": "ese bloqueo ya estaba resuelto"}

    autorizados = {str(m) for m in (fila["responsable_membership_id"],
                                    fila["abierto_por"], fila["escalado_a"])
                  if m is not None}
    if str(quien.membership_id) not in autorizados:
        raise Denegado(
            "No podés resolver ese bloqueo: no es tuyo, no lo abriste vos ni "
            "se te escaló.")

    cur.execute(
        "update blocker set resuelto_en = now(), resolucion = %s where id = %s",
        (resolucion, bloqueo_id))

    cur.execute(
        "select count(*) n from blocker where task_id = %s and resuelto_en is null",
        (fila["task_id"],))
    quedan_abiertos = cur.fetchone()["n"] > 0

    tarea_desbloqueada = False
    if not quedan_abiertos:
        # `actualizar_estado` no exige bloqueos cerrados para salir de
        # `bloqueada` (deuda conocida, docs/STATUS.md "Pendiente": no hay
        # disparador que valide transiciones todavía), así que la tarea puede
        # haber salido por otro camino mientras este bloqueo seguía abierto.
        # Si ya no está bloqueada, no hay a qué "volver": resolver el último
        # bloqueo no la mueve.
        cur.execute("select estado from task where id = %s", (fila["task_id"],))
        estado_actual = cur.fetchone()["estado"]
        if estado_actual == "bloqueada":
            # `bloqueada` es una proyección: el estado al que se vuelve es el
            # que tenía el último evento que entró a `bloqueada`, nunca un
            # valor fijo. `task_state_event` es append-only y prisma_app no
            # lo lee directo; esta función security definer es la única
            # puerta.
            cur.execute("select estado_previo_a_bloqueo(%s) as previo",
                       (fila["task_id"],))
            previo = cur.fetchone()["previo"]
            if previo is None:
                # No hay a qué volver y no se inventa un valor: ni null ni
                # `asignada` por defecto. Levanta después del `update` de
                # arriba a propósito -- la excepción deshace toda la
                # herramienta, incluida la resolución del bloqueo, dentro del
                # mismo punto de retorno por herramienta que usa `agente.py`.
                raise Denegado(
                    "No pude determinar a qué estado vuelve la tarea: no "
                    "tiene un estado anterior a bloqueada registrado.")
            cur.execute(
                """insert into task_state_event
                     (task_id, estado_anterior, estado_nuevo, actor_kind,
                      actor_app_user_id, motivo)
                   values (%s, 'bloqueada', %s, 'persona', %s, %s)""",
                (fila["task_id"], previo, quien.app_user_id, resolucion))
            _avisar_dependencia_informativa(
                cur, quien, fila["task_id"], previo, uuid.uuid4())
            tarea_desbloqueada = True
    return {"resuelto": True, "tarea_desbloqueada": tarea_desbloqueada}


@herramienta(
    "adjuntar_evidencia", "adjuntar_evidencia",
    "Registra la prueba de que un trabajo se hizo.",
    {"tarea_id": {"type": "string", "requerido": True},
     "tipo": {"type": "string", "requerido": True},
     "uri": {"type": "string"},
     "descripcion": {"type": "string"}})
def _adjuntar_evidencia(cur, quien: Solicitante, tarea_id, tipo, uri=None,
                        descripcion=None):
    cur.execute(
        """insert into evidence (workspace_id, task_id, tipo, uri, entregado_por)
           values (%s, %s, %s, %s, %s) returning id""",
        (quien.workspace_id, tarea_id, tipo, uri or descripcion,
         quien.membership_id))
    return {"evidencia_id": str(cur.fetchone()["id"])}


@herramienta(
    "aprobar_tarea", "aprobar_tarea",
    "Aprueba el trabajo de una tarea. Sólo puede quien la política del equipo "
    "designa para esa área.",
    {"tarea_id": {"type": "string", "requerido": True},
     "comentario": {"type": "string"}},
    valida_en_handler=True)
def _aprobar_tarea(cur, quien: Solicitante, tarea_id, comentario=None):
    cur.execute(
        "select responsable_membership_id from task where id = %s", (tarea_id,))
    fila = cur.fetchone()
    if not fila:
        return {"error": "esa tarea no existe en este equipo"}
    if fila["responsable_membership_id"] is None:
        return {"error": "esa tarea no tiene responsable asignado"}

    if str(fila["responsable_membership_id"]) == str(quien.membership_id):
        raise Denegado("No podés aprobar tu propio trabajo.")
    if not puede_aprobar_tarea(cur, quien, fila["responsable_membership_id"]):
        raise Denegado("No sos quien revisa el trabajo de esa persona.")
    cur.execute(
        """insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                 aprobador_membership_id, decision, comentario)
           values (%s, 'tarea', %s, %s, 'aprobado', %s)""",
        (quien.workspace_id, tarea_id, quien.membership_id, comentario))
    return {"aprobada": True}


# ---------------------------------------------------------------------------
# Dependencias
# ---------------------------------------------------------------------------

def _persona(cur, membership_id):
    if membership_id is None:
        return None
    cur.execute(
        "select telegram_user_id, nombre from integrante where membership_id = %s",
        (membership_id,))
    return cur.fetchone()


def _avisar(cur, quien: Solicitante, destinatario_membership_id, texto, *,
           dedupe_key, tipo="normal") -> None:
    """Un aviso automático más: si la persona todavía no activó el chat, se
    omite en silencio, igual que la escalera y la cadencia."""
    persona = _persona(cur, destinatario_membership_id)
    if not persona or persona["telegram_user_id"] is None:
        return
    enqueue_outbox(
        cur, workspace_id=quien.workspace_id, chat_id=persona["telegram_user_id"],
        text=texto, recipient_membership_id=destinatario_membership_id,
        message_type=tipo, dedupe_key=dedupe_key)


def _avisar_dependencia_informativa(cur, quien: Solicitante, tarea_id, estado_nuevo,
                                    event_id) -> None:
    """Mecánica §4: una dependencia informativa avisa a las dos partes cuando
    la origen cambia de fecha o de estado. Se llama después de insertar la
    fila de `task_state_event` de cada herramienta que la escribe.

    `fecha_objetivo` es inmutable una vez comprometida la tarea
    (`bloquear_estado_directo` en `db/esquema.sql` la rechaza), y ninguna
    ruta de código la cambia: el aviso por cambio de fecha queda sin
    disparador propio. Cubre sólo el cambio de estado -- gap para
    `docs/STATUS.md`.
    """
    cur.execute(
        """select d.id, o.titulo as origen_titulo,
                  o.responsable_membership_id as origen_resp,
                  t.titulo as destino_titulo,
                  t.responsable_membership_id as destino_resp
             from dependency d
             join task o on o.id = d.origen_task_id
             join task t on t.id = d.destino_task_id
            where d.origen_task_id = %s and d.tipo = 'informativa'""",
        (tarea_id,))
    for dep in cur.fetchall():
        texto = (f"«{dep['origen_titulo']}» pasó a {estado_nuevo}. Es una "
                 f"dependencia informativa con «{dep['destino_titulo']}».")
        for destinatario in {dep["origen_resp"], dep["destino_resp"]}:
            if destinatario is None:
                continue
            _avisar(cur, quien, destinatario, texto, tipo="informativo",
                   dedupe_key=(f"{quien.workspace_id}:dependencia-informativa:"
                               f"{dep['id']}:{event_id}:{destinatario}"))


def _tarea_para_dependencia(cur, tarea_id):
    cur.execute(
        """select id, estado, area_id, responsable_membership_id, titulo
             from task where id = %s""", (tarea_id,))
    return cur.fetchone()


def _autorizado_para_dependencia(cur, quien: Solicitante, origen, destino) -> bool:
    """El responsable de cualquiera de las dos tareas, o su referente
    (decisión de producto, 2026-09-22): una dependencia bloqueante frena la
    tarea de otra persona, así que no la declara cualquiera; pero exigir
    confirmación de la otra parte agrega fricción sin necesidad, porque el
    aviso ya la hace visible. "Referente" es `puede_aprobar_tarea`, la misma
    noción que usa `aprobar_tarea`."""
    quien_id = str(quien.membership_id)
    if quien_id == str(origen["responsable_membership_id"]):
        return True
    if quien_id == str(destino["responsable_membership_id"]):
        return True
    if puede_aprobar_tarea(cur, quien, origen["responsable_membership_id"]):
        return True
    if puede_aprobar_tarea(cur, quien, destino["responsable_membership_id"]):
        return True
    return False


def _destinatarios_dependencia_creada(cur, quien: Solicitante, origen, destino):
    """La otra parte, y entre áreas distintas los dos referentes (mecánica
    §4). "Referente" acá es quien aprueba el trabajo de cada responsable
    (`aprobador_membership_id`) -- la misma noción funcional que
    `puede_aprobar_tarea`, no un rol con un nombre fijo que cada pack puede
    llamar distinto."""
    quien_id = str(quien.membership_id)
    resp_origen = origen["responsable_membership_id"]
    resp_destino = destino["responsable_membership_id"]
    es_resp_origen = resp_origen is not None and quien_id == str(resp_origen)
    es_resp_destino = resp_destino is not None and quien_id == str(resp_destino)

    destinatarios: set[str] = set()
    if es_resp_origen and not es_resp_destino:
        if resp_destino is not None:
            destinatarios.add(str(resp_destino))
    elif es_resp_destino and not es_resp_origen:
        if resp_origen is not None:
            destinatarios.add(str(resp_origen))
    elif not es_resp_origen and not es_resp_destino:
        # Quien crea es referente de una de las dos, no responsable de
        # ninguna: avisa a los dos responsables.
        if resp_origen is not None:
            destinatarios.add(str(resp_origen))
        if resp_destino is not None:
            destinatarios.add(str(resp_destino))
    # Si es responsable de las dos a la vez, no hay "otra parte" a quien avisar.

    if str(origen["area_id"]) != str(destino["area_id"]):
        for resp in (resp_origen, resp_destino):
            if resp is None:
                continue
            cur.execute(
                "select aprobador_membership_id from membership where id = %s",
                (resp,))
            fila = cur.fetchone()
            if fila and fila["aprobador_membership_id"]:
                destinatarios.add(str(fila["aprobador_membership_id"]))

    destinatarios.discard(quien_id)
    return destinatarios


def _texto_dependencia_creada(tipo, origen, destino, creador_nombre) -> str:
    if tipo == "bloqueante":
        texto = (f"{creador_nombre} registró que «{destino['titulo']}» depende de "
                 f"«{origen['titulo']}»: no puede pasar a en curso hasta que esa "
                 f"tarea esté terminada.")
        if destino["estado"] == "en_curso":
            # No la mueve retroactivamente (mecánica §4 sólo frena el pase a
            # en curso, no revierte uno ya hecho); esto lo deja visible.
            texto += (f" «{destino['titulo']}» ya está en curso, así que esta "
                      f"dependencia no la frena ahora.")
        return texto
    return (f"{creador_nombre} registró una dependencia informativa entre "
           f"«{origen['titulo']}» y «{destino['titulo']}»: aviso cuando "
           f"alguna de las dos cambie de estado.")


@herramienta(
    "crear_dependencia", "crear_dependencia",
    "Declara que una tarea depende de otra. 'bloqueante' frena que la "
    "destino pase a en curso hasta que la origen esté terminada; "
    "'informativa' sólo avisa cuando la origen cambia de estado.",
    {"origen_tarea_id": {"type": "string", "requerido": True},
     "destino_tarea_id": {"type": "string", "requerido": True},
     "tipo": {"type": "string", "enum": ["bloqueante", "informativa"]}},
    valida_en_handler=True)
def _crear_dependencia(cur, quien: Solicitante, origen_tarea_id, destino_tarea_id,
                       tipo="bloqueante"):
    if str(origen_tarea_id) == str(destino_tarea_id):
        return {"error": "una tarea no puede depender de sí misma"}

    origen = _tarea_para_dependencia(cur, origen_tarea_id)
    if not origen:
        return {"error": "la tarea de origen no existe en este equipo"}
    destino = _tarea_para_dependencia(cur, destino_tarea_id)
    if not destino:
        return {"error": "la tarea de destino no existe en este equipo"}

    if destino["estado"] in ("terminada", "cancelada"):
        return {"error": "esa tarea ya está cerrada, no se le puede agregar una dependencia"}

    cur.execute(
        "select 1 from dependency where origen_task_id = %s and destino_task_id = %s",
        (origen_tarea_id, destino_tarea_id))
    if cur.fetchone():
        return {"error": "ya existe una dependencia registrada entre esas tareas"}

    if not _autorizado_para_dependencia(cur, quien, origen, destino):
        raise Denegado(
            "No podés declarar una dependencia entre esas tareas: no sos "
            "responsable de ninguna de las dos, ni referente de quien lo es.")

    # Un ciclo lo rechaza `trg_evitar_ciclo_dependencia`: la excepción de la
    # base sube tal cual, y `agente.py` ya la traduce a un mensaje legible
    # para quien llama (no es un incidente).
    cur.execute(
        """insert into dependency (workspace_id, origen_task_id, destino_task_id, tipo)
           values (%s, %s, %s, %s) returning id""",
        (quien.workspace_id, origen_tarea_id, destino_tarea_id, tipo))
    dep_id = cur.fetchone()["id"]

    destinatarios = _destinatarios_dependencia_creada(cur, quien, origen, destino)
    texto = _texto_dependencia_creada(tipo, origen, destino, quien.nombre)
    for destinatario in destinatarios:
        _avisar(cur, quien, destinatario, texto,
               dedupe_key=f"{quien.workspace_id}:dependencia-creada:{dep_id}:{destinatario}")

    return {"dependencia_id": str(dep_id)}


@herramienta(
    "quitar_dependencia", "quitar_dependencia",
    "Elimina una dependencia entre dos tareas.",
    {"dependencia_id": {"type": "string", "requerido": True}},
    valida_en_handler=True)
def _quitar_dependencia(cur, quien: Solicitante, dependencia_id):
    cur.execute(
        """select d.id, o.responsable_membership_id as origen_resp,
                  t.responsable_membership_id as destino_resp
             from dependency d
             join task o on o.id = d.origen_task_id
             join task t on t.id = d.destino_task_id
            where d.id = %s""", (dependencia_id,))
    fila = cur.fetchone()
    if not fila:
        # RLS ya deja pasar sólo lo del espacio activo: una dependencia de
        # otro espacio llega hasta acá igual de vacía que una inventada.
        return {"error": "esa dependencia no existe en este equipo"}

    origen = {"responsable_membership_id": fila["origen_resp"]}
    destino = {"responsable_membership_id": fila["destino_resp"]}
    if not _autorizado_para_dependencia(cur, quien, origen, destino):
        raise Denegado(
            "No podés quitar esa dependencia: no sos responsable de ninguna "
            "de las dos tareas, ni referente de quien lo es.")

    # Baja física, no un estado "quitada": `dependency` no tiene columnas de
    # baja blanda como `blocker.resuelto_en`, y `agente.py` ya audita todo
    # llamado a herramienta (`registrar_auditoria`, accion
    # "herramienta:quitar_dependencia", con los argumentos) con quién, cuándo
    # y qué dependencia, así que el rastro no depende de esta fila.
    cur.execute("delete from dependency where id = %s", (dependencia_id,))
    return {"eliminada": True}


@herramienta(
    "pedir_tablero", "consultar",
    "Devuelve un enlace personal al tablero, con el estado del equipo: avance "
    "de objetivos, carga por persona, vencidas y bloqueos. Usalo cuando "
    "pidan ver el tablero, el panel o un resumen visual.",
    {}, necesita_chat=True)
def _pedir_tablero(cur, quien: Solicitante, chat_id: int | None = None):
    """Emite un enlace al tablero, sólo por chat privado.

    Un enlace en un grupo es acceso para cualquiera que lo lea, ahora y
    dentro de seis meses cuando alguien revise el historial. Por eso el
    chat lo pone el servidor y no el modelo: si el modelo pudiera declararlo,
    bastaría con que dijera "privado".
    """
    from datetime import datetime, timezone

    from . import tablero
    from .config import config

    if chat_id is None or chat_id <= 0:
        return {"emitido": False,
                "explicacion": "El enlace al tablero se pide por chat privado, "
                               "no por el grupo. Escribime por privado y te lo mando."}

    if not config.base_url:
        return {"emitido": False,
                "explicacion": "Todavía no está configurada la dirección "
                               "pública, así que no puedo armar el enlace."}

    token = tablero.emitir(cur, quien.membership_id,
                           datetime.now(timezone.utc))
    minutos = tablero.minutos_de_vigencia(cur)
    return {"emitido": True,
            "enlace": f"{config.base_url.rstrip('/')}/tablero/{token}",
            "vence_en_minutos": minutos}


@herramienta(
    "consultar_objetivos", "consultar",
    "Objetivos del equipo con su avance.", {})
def _consultar_objetivos(cur, quien: Solicitante):
    cur.execute(
        """select o.id, o.titulo, o.tipo, o.estado, o.fecha_objetivo,
                  count(t.id) filter (where t.estado = 'terminada') as hechas,
                  count(t.id) as total
             from objective o left join task t on t.objective_id = o.id
            where o.workspace_id = %s
            group by o.id order by o.tipo, o.creado_en""",
        (quien.workspace_id,))
    return [dict(f) for f in cur.fetchall()]
