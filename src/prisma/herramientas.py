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

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

import psycopg
from psycopg.types.json import Jsonb

from .autoridad import (Denegado, Solicitante, puede_aprobar_tarea,
                        requiere_confirmacion, verificar)


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


REGISTRO: dict[str, Herramienta] = {}


def herramienta(nombre: str, accion: str, descripcion: str, parametros: dict,
                *, valida_en_handler: bool = False):
    def envoltura(fn):
        REGISTRO[nombre] = Herramienta(nombre, accion, descripcion, parametros,
                                       fn, valida_en_handler)
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
             args: dict[str, Any], *, ya_confirmada: bool = False) -> Any:
    """Punto único de entrada. Nada llega a la base por otro camino.

    `ya_confirmada` es para lo que vuelve de una acción pendiente: la persona
    ya dijo que sí, y volver a frenarla sería un bucle. La autoridad se
    verifica igual — confirmar no es lo mismo que tener permiso.
    """
    h = REGISTRO.get(nombre)
    if h is None:
        raise Denegado(f"No existe la herramienta '{nombre}'.")

    if not h.valida_en_handler:
        verificar(cur, quien, h.accion, area_id=args.get("area_id"))

    if requiere_confirmacion(h.accion) and not ya_confirmada:
        raise NecesitaConfirmacion(_resumen(h, args), nombre, dict(args))

    try:
        return h.handler(cur, quien, **args)
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


@herramienta(
    "crear_tarea", "crear_tarea",
    "Crea una tarea dentro de un objetivo existente. Si no sabés a cuál "
    "pertenece, consultá los objetivos antes de inventar uno.",
    {"titulo": {"type": "string", "requerido": True},
     "objetivo_id": {"type": "string"},
     "area_slug": {"type": "string", "requerido": True},
     "responsable": {"type": "string", "description": "nombre de la persona"},
     "fecha_objetivo": {"type": "string", "description": "AAAA-MM-DD"},
     "criterio_aceptacion": {"type": "string"},
     "descripcion": {"type": "string"}})
def _crear_tarea(cur, quien: Solicitante, titulo, objetivo_id=None, area_slug=None,
                 responsable=None, fecha_objetivo=None,
                 criterio_aceptacion=None, descripcion=None,
                  responsable_membership_id=None):
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
                 'titulo', titulo, 'objetivo', objective_snapshot,
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
    cur.execute(
        """insert into message_outbox
             (workspace_id, chat_id, destinatario_membership_id, tipo, cuerpo,
              estado, programado_para, dedupe_key, es_respuesta,
              pending_action_id)
           values (%s, %s, %s, 'normal', %s, 'listo', %s, %s, false, %s)""",
        (quien.workspace_id, autoridad["telegram_user_id"], aprobador_id,
         resumen, ahora, f"{quien.workspace_id}:draft-preview:{borrador['id']}:"
         f"{borrador['version']}", pendiente.id))
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

    cur.execute(
        """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                         actor_kind, actor_app_user_id, motivo)
           values (%s, %s, %s, 'persona', %s, %s)""",
        (tarea_id, fila["estado"], estado, quien.app_user_id, motivo))
    return {"estado": estado}


@herramienta(
    "registrar_bloqueo", "registrar_bloqueo",
    "Registra que una tarea está trabada, con su causa e impacto.",
    {"tarea_id": {"type": "string", "requerido": True},
     "causa": {"type": "string", "requerido": True},
     "impacto": {"type": "string"}})
def _registrar_bloqueo(cur, quien: Solicitante, tarea_id, causa, impacto=None):
    cur.execute(
        """insert into blocker (workspace_id, task_id, causa, impacto, abierto_por)
           values (%s, %s, %s, %s, %s) returning id""",
        (quien.workspace_id, tarea_id, causa, impacto, quien.membership_id))
    bid = cur.fetchone()["id"]
    cur.execute("select estado from task where id = %s", (tarea_id,))
    cur.execute(
        """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                         actor_kind, actor_app_user_id, motivo)
           values (%s, (select estado from task where id = %s), 'bloqueada',
                   'persona', %s, %s)""",
        (tarea_id, tarea_id, quien.app_user_id, causa))
    return {"bloqueo_id": str(bid)}


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
