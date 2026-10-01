"""Server-owned conversational intake for Unit 1A task drafts."""

from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import psycopg
from psycopg.types.json import Jsonb

from .autoridad import Denegado, Solicitante
from .db import entrante_atado, registrar_auditoria
from .incidentes import (ETAPA_CONFIGURACION_ALTA, ETAPA_CRITERIO_SIN_PROPUESTA,
                         ETAPA_HORIZONTE_TAREA, ETAPA_OBJETIVO_SIN_ORDENAR, ETAPA_REDACCION_RECHAZADA,
                         ETAPA_RESUMEN_SIN_CIERRE,
                         ETAPA_RESUMEN_VIGENTE_SIN_FILA, ETAPA_VALOR_SIN_INTERPRETAR, NOTICIA_NEUTRA_INCIDENTE,
                         REFERENCIA_INBOUND_MESSAGE, REFERENCIA_PENDING_ACTION,
                         registrar_incidente)
from .pendientes import HERRAMIENTA_REVISION_BORRADOR
from .redaccion import (TextoRedactado, _resumen_b, nombre_legible,
                        redactar_partes, redactar_turno, variante_redaccion)
from .resultado_turno import (Cambio, Falta, OpcionDisponible, Rechazo,
                              ResultadoTurno, Resumen, SinCambio, ValorAceptado)
from .salida import (BUTTON_TEXT_LIMIT, ETIQUETA_CANCELAR, ETIQUETA_CONFIRMAR,
                     ETIQUETA_ENVIAR, ETIQUETA_MODIFICAR, ETIQUETA_RECHAZAR,
                     ICONO_CANCELAR, ICONO_OTRA_OPCION, ICONO_RECOMENDADA,
                     ICONO_VER_MAS, PayloadValidationError, con_icono,
                     enqueue_outbox, etiqueta_sin_icono, etiquetas_de_tarea,
                     normalize_visible_text, prepare_buttons, prepare_payload, telegram_utf16_units,
                     with_no_effect_status)
from .valores import (OPCION_NINGUNA, VERIFICABLE_NO, MotivoRechazo, Rechazado,
                      TipoValor, ValorEsperado, opciones_numeradas, sumar_meses,
                      validar_valor)


CALLBACK_PREFIX = "i:"
SAFE_TELEGRAM_TEXT = BUTTON_TEXT_LIMIT
CANDIDATE_PAGE_SIZE = 7
# El orden en que el alta pregunta (decisión del usuario, 2026-09-30): primero
# qué hay que hacer y después el objetivo.
FIELDS = (
    "title", "objective", "description", "responsible", "area", "due_date",
    "evidence", "acceptance_criterion",
)
CONFIRM = "Sí"
REJECT = "No"
OTHER = con_icono("Otra opción", ICONO_OTRA_OPCION)
# Íconos de botón (decisión del usuario, 2026-09-28): "Ver más" y "Cancelar
# borrador" se repiten en varios puntos de este módulo -- una sola etiqueta
# por texto, nunca un literal por lugar.
VER_MAS = con_icono("Ver más", ICONO_VER_MAS)
CANCELAR_BORRADOR = con_icono("Cancelar borrador", ICONO_CANCELAR)
# Lo que se le dice a quien escribe mientras su borrador espera la confirmación
# (T9-R1c-2): la tarea se crea sólo con el botón Confirmar, nunca con un
# mensaje. Redacción pendiente de revisión de voz en T10.
DRAFT_AWAITING_CONFIRMATION = (
    "El borrador de la tarea está esperando confirmación: se confirma con el "
    "botón Confirmar del resumen, no con un mensaje.")
# Lo que se le dice a quien pidió el borrador mientras su resumen espera su revisión
# (T9-R1c-4): cuando lo confirma otra persona, se le envía sólo con el botón Enviar a
# aprobación, nunca con un mensaje. Redacción pendiente de revisión de voz en T10.
DRAFT_AWAITING_SEND = (
    "El borrador de la tarea está esperando tu revisión: se envía a aprobación con "
    "el botón Enviar a aprobación del resumen, no con un mensaje. Con Modificar "
    "cambiás un dato y con Cancelar lo cancelás.")
# Antes del resumen vigente, cuando quien pidió toca Enviar a aprobación sobre uno que
# el borrador dejó atrás (T9-R1c-4b): nada se envió y tiene que mirar de nuevo.
# Redacción pendiente de revisión de voz en T10.
DRAFT_CHANGED_REVIEW_AGAIN = (
    "El borrador cambió desde que lo revisaste. Mirá de nuevo este resumen antes de "
    "enviarlo:")
# Lo que se le dice a quien terminó el alta cuando no es quien la confirma (T9-R3,
# ADR 0013 regla 3: cómo quedó y qué falta): a quién se le mandó y que la tarea
# todavía no existe. Redacción pendiente de revisión de voz en T10.
# Estados reales del alta que no dejan avanzar: son la respuesta a quien actuó
# (regla 3), no un aviso neutro. Redacción pendiente de revisión de voz en T10.
NO_EVIDENCE_POLICY = "No hay una política de evidencia vigente para esa área."
CONFIRMED_OPTION_STALE = "Alguna opción confirmada ya no está vigente."
NO_ACTIVE_AUTHORITY = "No hay una autoridad activa que pueda revisar el borrador."
DRAFT_SENT_TO_APPROVER = (
    "Le mandé el borrador de la tarea a {name} para que lo confirme. La tarea "
    "se crea cuando lo confirme.")
DRAFT_SENT_TO_SOMEONE_ELSE = (
    "Le mandé el borrador de la tarea a otra persona del equipo para que lo "
    "confirme. La tarea se crea cuando lo confirme.")
CHOICE_FALLBACK_PROMPT = "Elegí una opción para seguir con la tarea."
# Modificar en la vista previa del borrador (T9-R1c-3, ADR 0005 decisión 1): el
# selector "qué dato cambiar" es una elección del alta con un botón por dato, y su
# `tipo` (`task_intake_choice_set.tipo`) lo distingue de las elecciones de un dato.
# Un dato de texto se corrige copiando y pegando lo que la persona tenía; uno que se
# elige con botones vuelve a mostrar sus opciones. Redacción pendiente de revisión
# de voz en T10.
MODIFY_PICKER_KIND = "modify_picker"
MODIFY_PICKER_PROMPT = "¿Qué dato querés cambiar del borrador?"
MODIFY_FIELD_LABELS = {
    "title": "Título", "description": "Descripción", "objective": "Objetivo",
    "responsible": "Responsable", "area": "Área", "due_date": "Fecha objetivo",
    "acceptance_criterion": "Criterio de aceptación",
}
# Salir del selector sin cambiar nada: vuelve a mostrar la vista previa actual.
# Redacción pendiente de revisión de voz en T10.
BACK_TO_SUMMARY = "Volver al resumen"
CHOICE_FIELDS = ("objective", "responsible", "area")
NOT_YOURS = "Eso se lo pregunté a otra persona del equipo."
USER_FIELD_LIMITS = {
    "title": 200,
    "description": 800,
    "objective": 120,
    "responsible": 120,
    "area": 120,
    "due_date": 64,
    "acceptance_criterion": 500,
}
CONFIG_LABEL_LIMIT = 80
EVIDENCE_ITEM_LIMIT = 160
EVIDENCE_TOTAL_LIMIT = 800
EVIDENCE_COUNT_LIMIT = 8
CONFIG_ERROR = (
    "No puedo mostrar una opción configurada de este espacio. Pedile a quien lo "
    "administra que la revise o cancelá este borrador."
)
NO_CANDIDATES = (
    "No hay opciones disponibles para este dato. Pedile a quien administra el "
    "espacio que las configure o cancelá este borrador."
)


@dataclass(frozen=True)
class IntakeOutcome:
    request_id: str
    text: str = ""
    changed: bool = False
    inert: bool = False
    pending_action_id: str | None = None
    terminal: str | None = None
    # El botón tocado ya no vale (su elección se usó, se cerró o se reemplazó): el
    # gateway lo contesta como cualquier otro toque que no está vigente (sólo el
    # selector de Modificar lo marca). No se persiste: es del toque, no del resultado.
    stale: bool = False
    # El texto del resultado ya se encoló como la respuesta a quien actuó (un
    # estado real del alta, ADR 0013 regla 3): quien llama no vuelve a preguntar
    # ni encola otro texto encima. Tampoco se persiste.
    responded: bool = False
    # La solicitud quedó creada y falta el turno del modelo (alta conducida,
    # `alta_conducida.arrancar`): quien llama lo corre, con el mensaje que la abrió.
    # Tampoco se persiste.
    conducir: bool = False

    def as_json(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "text": self.text,
            "changed": self.changed,
            "inert": self.inert,
            "pending_action_id": self.pending_action_id,
            "terminal": self.terminal,
        }


def draft_sent_text(approver_name) -> str:
    """El aviso de a quién se le mandó el borrador; sin un nombre legible no se
    inventa ninguno."""
    name = normalize_text(approver_name) if isinstance(approver_name, str) else ""
    if not name:
        return DRAFT_SENT_TO_SOMEONE_ELSE
    return DRAFT_SENT_TO_APPROVER.format(name=name)


def normalize_text(raw: str) -> str:
    return normalize_visible_text(raw)


def token_de(callback: str) -> str | None:
    if not callback.startswith(CALLBACK_PREFIX):
        return None
    return callback[len(CALLBACK_PREFIX):] or None


def callback_data(token: str) -> str:
    return f"{CALLBACK_PREFIX}{token}"


def start(cur: psycopg.Cursor, who: Solicitante, *, chat_id: int,
          source_inbound_id: str, source_raw_text: str,
          proposals: dict[str, Any], now: datetime,
          conducido: bool = False) -> IntakeOutcome:
    """Abre el alta. Con `conducido` (el alta conducida por el modelo) la solicitud
    se crea sin proponer ni preguntar nada: devuelve `conducir` y quien llama corre
    el primer turno del modelo con el mensaje que la abrió, así los datos que ese
    mensaje trae se toman todos. Con un borrador en curso, la elección de siempre
    (continuar, cancelar, empezar otro)."""
    if chat_id <= 0:
        return IntakeOutcome("", "Podemos armar el borrador sólo en un chat privado.",
                             inert=True)
    cur.execute(
        "select pg_advisory_xact_lock(hashtextextended(%s, 0))",
        (f"task-intake:{who.workspace_id}:{who.membership_id}:{chat_id}",),
    )
    cur.execute(
        """select * from task_intake_request
            where workspace_id = %s and membership_id = %s and chat_id = %s
              and estado = 'active' and enviada_en is null for update""",
        (who.workspace_id, who.membership_id, chat_id),
    )
    existing = cur.fetchone()
    if existing:
        payload = {
            "source_inbound_id": source_inbound_id,
            "source_raw_text": source_raw_text,
            "proposals": proposals,
        }
        _invalidate_open_inputs(cur, str(existing["id"]))
        return _open_choices(
            cur, existing, None,
            "Ya hay un borrador de tarea en curso. Elegí cómo seguir.",
            [
                ("Continuar borrador", "continue", None),
                (CANCELAR_BORRADOR, "cancel", None),
                ("Empezar otro", "start_new", payload),
            ],
            now, kind="conflict",
        )

    cur.execute(
        """insert into task_draft (workspace_id, creado_por_membership_id)
           values (%s, %s) returning id""",
        (who.workspace_id, who.membership_id),
    )
    draft_id = str(cur.fetchone()["id"])
    cur.execute(
        """insert into task_intake_request
             (workspace_id, membership_id, chat_id, task_draft_id,
              source_inbound_id, source_raw_text)
           values (%s, %s, %s, %s, %s, %s) returning *""",
        (who.workspace_id, who.membership_id, chat_id, draft_id,
         source_inbound_id, source_raw_text),
    )
    request = cur.fetchone()
    request_id = str(request["id"])
    for field in FIELDS:
        cur.execute(
            """insert into task_intake_field (request_id, workspace_id, campo)
               values (%s, %s, %s)""",
            (request_id, who.workspace_id, field),
        )
    if conducido:
        return IntakeOutcome(request_id, changed=True, conducir=True)
    avisos = _store_proposals(
        cur, request_id, proposals, source_inbound_id, source_raw_text, now,
        who.workspace_id,
    )
    cur.execute("select * from task_intake_request where id = %s", (request_id,))
    return _advance(cur, cur.fetchone(), who, now, prefijo=avisos)


def _hoy_del_espacio(cur, workspace_id, now: datetime) -> date:
    """El día de hoy en la zona horaria del espacio: el reloj entra por acá."""
    cur.execute("select zona_horaria from workspace where id = %s", (workspace_id,))
    return now.astimezone(ZoneInfo(cur.fetchone()["zona_horaria"])).date()


# Qué tipo de valor espera cada campo de texto libre del alta (ADR 0014, M1); los
# que no están son texto. Las entidades (objetivo, persona, área) se buscan
# después entre las de la base.
TIPO_DE_CAMPO = {
    "due_date": TipoValor.FECHA,
    "objective": TipoValor.ENTIDAD,
    "responsible": TipoValor.ENTIDAD,
    "area": TipoValor.ENTIDAD,
}
_SUJETO_DEL_CAMPO = {
    "title": "el título", "description": "la descripción",
    "objective": "el objetivo", "responsible": "la persona responsable",
    "area": "el área", "due_date": "la fecha objetivo",
    "acceptance_criterion": "el criterio de aceptación",
}


# F-B7: lo que se dice cuando lo que la persona escribió como criterio de aceptación
# no dice cómo se comprueba que la tarea está hecha, y se le propone otro.
RECHAZO_CRITERIO = Rechazo(
    "Eso todavía no dice cómo se comprueba que la tarea está hecha.",
    "Te propongo uno; usalo o escribí otro.")


def _criterio_a_proponer(cur, request_id, who, valor, dicho, inbound_id):
    """El criterio que se le propone a la persona (F-B7), o `None` si se toma lo que
    escribió. Sólo se propone si el modelo juzgó que lo que dijo no es verificable,
    si todavía no se le propuso nada en esta alta (una sola propuesta: si insiste
    con su texto, se acepta) y si el código valida la propuesta (no vacía, dentro
    del límite y distinta de lo que dijo)."""
    if not isinstance(valor, dict) or valor.get("verificable") != VERIFICABLE_NO:
        return None
    cur.execute(
        """select 1 from task_intake_choice_set
            where request_id = %s and campo = 'acceptance_criterion' limit 1""",
        (request_id,))
    if cur.fetchone():
        return None
    propuesta = normalize_text(str(valor.get("propuesta") or ""))
    if (propuesta and propuesta != dicho
            and telegram_text_length(propuesta) <= USER_FIELD_LIMITS[
                "acceptance_criterion"]):
        return propuesta
    registrar_incidente(
        cur, who.workspace_id,
        "El modelo juzgó que el criterio de aceptación no es verificable, pero no "
        "dio una propuesta válida: se tomó el texto de la persona.",
        severidad="baja", etapa=ETAPA_CRITERIO_SIN_PROPUESTA,
        app_user_id=who.app_user_id, avisar_admin=False,
        referencia_tipo=REFERENCIA_INBOUND_MESSAGE if inbound_id else None,
        referencia_id=inbound_id)
    return None


CLAVE_HORIZONTE = "horizonte_tarea"
HORIZONTE_POR_OMISION = 2
# El mayor margen que se acepta: más allá es un error de tipeo (y un número enorme
# rompería el cálculo de la fecha límite).
HORIZONTE_MAXIMO = 120
# (espacio, valor) del ajuste ya registrado como inválido por este proceso.
_anomalias_horizonte: set[tuple[str, str]] = set()


def meses_de_horizonte(cur, workspace_id: str) -> int:
    """Cuántos meses de calendario, desde hoy, puede ir la fecha de una tarea: el
    ajuste `horizonte_tarea` del espacio (`{"meses": N}`, del pack). Sin él, 2. Un
    valor que no se entiende usa 2 y deja un incidente (una vez por proceso): un
    ajuste mal escrito no se ignora en silencio."""
    cur.execute(
        "select valor from workspace_setting where workspace_id = %s and clave = %s",
        (workspace_id, CLAVE_HORIZONTE))
    fila = cur.fetchone()
    if not fila:
        return HORIZONTE_POR_OMISION
    valor = fila["valor"]
    if isinstance(valor, str):
        try:
            valor = json.loads(valor)
        except ValueError:
            pass
    meses = valor.get("meses") if isinstance(valor, dict) else None
    if (isinstance(meses, int) and not isinstance(meses, bool)
            and 1 <= meses <= HORIZONTE_MAXIMO):
        return meses
    huella = (workspace_id, json.dumps(valor, sort_keys=True, default=str))
    if huella not in _anomalias_horizonte:
        registrar_incidente(
            cur, workspace_id,
            "El ajuste `horizonte_tarea` del espacio no tiene un valor válido: "
            f"se usan {HORIZONTE_POR_OMISION} meses como margen de la fecha de una "
            "tarea.", severidad="baja",
            referencia_cruda=f"workspace_setting[{CLAVE_HORIZONTE}]={huella[1]}"[:2000],
            etapa=ETAPA_HORIZONTE_TAREA, avisar_admin=False)
        _anomalias_horizonte.add(huella)
    return HORIZONTE_POR_OMISION


def limite_de_fecha(cur, workspace_id: str, hoy: date) -> date:
    """El último día que vale como fecha objetivo de una tarea (se incluye)."""
    return sumar_meses(hoy, meses_de_horizonte(cur, workspace_id))


def _esperado_del_campo(cur, workspace_id, field: str, now: datetime) -> ValorEsperado:
    tipo = TIPO_DE_CAMPO.get(field, TipoValor.TEXTO)
    if tipo is TipoValor.FECHA:
        hoy = _hoy_del_espacio(cur, workspace_id, now)
        return ValorEsperado(tipo, hoy=hoy,
                             hasta=limite_de_fecha(cur, workspace_id, hoy))
    return ValorEsperado(tipo)


def _store_proposals(cur, request_id, proposals, inbound_id, raw, now, workspace_id):
    """Guarda lo que el modelo propuso, ya validado por el código. Devuelve el
    aviso (texto, o vacío) de lo que propuso y no sirvió: una propuesta que no
    se puede tomar se dice, nunca se descarta sin avisar."""
    key_map = {
        "title": "title", "description": "description",
        "objective": "objective", "responsible": "responsible",
        "area": "area", "due_date": "due_date",
        "acceptance_criterion": "acceptance_criterion",
    }
    avisos: list[str] = []
    for key, field in key_map.items():
        supplied = proposals.get(key)
        if supplied is None:
            continue
        value: Any = normalize_text(str(supplied))
        if not value:
            continue
        if telegram_text_length(value) > USER_FIELD_LIMITS[field]:
            continue
        if field == "due_date":
            esperado = _esperado_del_campo(cur, workspace_id, field, now)
            resultado = validar_valor({"fecha_iso": value}, esperado,
                                      limite_texto=USER_FIELD_LIMITS[field])
            if isinstance(resultado, Rechazado):
                avisos.append(_aviso_de_propuesta(field, value, resultado))
                continue
            value = resultado.valor.isoformat()
        cur.execute(
            """update task_intake_field
                  set estado = 'proposed', valor = %s, proposed_by = 'model',
                      source_inbound_id = %s, source_raw_text = %s,
                      actualizado_en = %s
                where request_id = %s and campo = %s""",
            (Jsonb(value), inbound_id, raw, now, request_id, field),
        )
    return "\n".join(avisos) + "\n\n" if avisos else ""


def _aviso_de_propuesta(field: str, propuesto: str, rechazo: Rechazado) -> str:
    """Lo que se dice de un dato que el mensaje trajo y no se pudo tomar: cuál,
    por qué, y que se vuelve a preguntar."""
    razon = rechazo.razon.rstrip(".")
    razon = razon[:1].lower() + razon[1:]
    return (f"No pude tomar {_SUJETO_DEL_CAMPO[field]} que dijiste («{propuesto}»): "
            f"{razon}. Te lo vuelvo a preguntar más adelante.")


def resolve_choice(cur: psycopg.Cursor, who: Solicitante, *, token: str,
                   chat_id: int, now: datetime) -> IntakeOutcome:
    cur.execute(
        """select c.id choice_id, c.accion, c.valor, c.activa,
                   s.id choice_set_id, s.request_id, s.campo, s.estado set_estado,
                   s.resultado set_resultado, s.request_version, s.tipo set_tipo,
                   r.membership_id, r.chat_id, r.estado request_estado,
                   r.version request_current_version
             from task_intake_choice c
             join task_intake_choice_set s on s.id = c.choice_set_id
             join task_intake_request r on r.id = s.request_id
            where c.token = %s for update of s, c, r""",
        (token,),
    )
    choice = cur.fetchone()
    if not choice:
        return IntakeOutcome("", "Ese botón ya no está vigente.", inert=True)
    request_id = str(choice["request_id"])
    if str(choice["membership_id"]) != str(who.membership_id) or choice["chat_id"] != chat_id:
        return IntakeOutcome(request_id, "Ese botón corresponde a otro chat.", inert=True)
    stale = choice["set_tipo"] == MODIFY_PICKER_KIND
    if choice["set_estado"] != "active" or not choice["activa"]:
        persisted = choice["set_resultado"] or {}
        return IntakeOutcome(
            request_id, persisted.get("text", "Ese botón ya no está vigente."),
            inert=True, pending_action_id=persisted.get("pending_action_id"),
            terminal=persisted.get("terminal"), stale=stale,
        )
    if choice["request_estado"] != "active":
        return IntakeOutcome(request_id, "Ese borrador ya terminó.", inert=True,
                             terminal=choice["request_estado"], stale=stale)
    if choice["request_version"] != choice["request_current_version"]:
        return IntakeOutcome(request_id, "Ese botón ya no está vigente.", inert=True,
                             stale=stale)

    cur.execute(
        """update task_intake_choice_set set estado = 'consumed'
            where id = %s and estado = 'active' returning id""",
        (choice["choice_set_id"],),
    )
    if not cur.fetchone():
        cur.execute("select resultado from task_intake_choice_set where id = %s",
                    (choice["choice_set_id"],))
        persisted = cur.fetchone()["resultado"] or {}
        return IntakeOutcome(
            request_id, persisted.get("text", "Ese botón ya no está vigente."),
            inert=True, pending_action_id=persisted.get("pending_action_id"),
            terminal=persisted.get("terminal"), stale=stale,
        )
    _cerrar_botones_de(cur, choice["choice_set_id"], choice["choice_id"])
    cur.execute(
        """update task_intake_request
              set version = version + 1, actualizado_en = %s,
                  terminal_result = case
                      when terminal_result ? %s
                      then jsonb_build_object(%s::text, true) else null end
            where id = %s returning *""",
        (now, CRITERIO_PROPUESTO, CRITERIO_PROPUESTO, request_id),
    )
    request = cur.fetchone()
    action = choice["accion"]
    if action == "continue":
        outcome = _seguir_con_el_borrador(cur, request, who, now)
    elif action == "cancel":
        outcome = _cancel(cur, request, who, now)
    elif action == "start_new":
        payload = choice["valor"]
        _cancel(cur, request, who, now, enqueue=False)
        from . import alta_conducida

        conducido = alta_conducida.alta_conducida(cur, who.workspace_id)
        outcome = start(
            cur, who, chat_id=chat_id,
            source_inbound_id=payload["source_inbound_id"],
            source_raw_text=payload["source_raw_text"],
            proposals=payload["proposals"], now=now, conducido=conducido,
        )
        if outcome.conducir:
            outcome = alta_conducida.arrancar(
                cur, who, outcome.request_id, payload["source_raw_text"], now)
    elif action == "other":
        outcome = _open_free_text(
            cur, request, choice["campo"],
            _free_text_prompt(choice["campo"]), now,
        )
    elif action == "modify_field":
        outcome = _ask_field_change(cur, request, who, choice["valor"]["field"], now)
    elif action == "back_to_summary":
        # Sin cambiar ningún dato: la vista previa vuelve tal como estaba.
        outcome = _finalize(cur, request, who, now)
    elif action == "more":
        page = choice["valor"]
        outcome = _open_entity_page(
            cur, request, who, page["field"], page.get("query"),
            int(page["offset"]), now,
        )
    elif action in {"confirm", "select"}:
        if action == "confirm":
            cur.execute(
                """update task_intake_field
                      set estado = 'confirmed', source_choice_id = %s,
                          version = version + 1, actualizado_en = %s
                    where request_id = %s and campo = %s and estado = 'proposed'""",
                (choice["choice_id"], now, request_id, choice["campo"]),
            )
        else:
            cur.execute(
                """update task_intake_field
                      set estado = 'confirmed', valor = %s, proposed_by = 'server',
                          source_choice_id = %s, version = version + 1,
                          actualizado_en = %s
                    where request_id = %s and campo = %s""",
                (Jsonb(choice["valor"]), choice["choice_id"], now,
                 request_id, choice["campo"]),
            )
        outcome = _advance(cur, request, who, now)
    elif action == "reject":
        cur.execute(
            """update task_intake_field
                  set estado = 'missing', valor = null, proposed_by = null,
                      source_inbound_id = null, source_raw_text = null,
                      source_choice_id = null, version = version + 1,
                      actualizado_en = %s
                where request_id = %s and campo = %s""",
            (now, request_id, choice["campo"]),
        )
        outcome = _advance(cur, request, who, now)
    else:
        outcome = IntakeOutcome(request_id, "Ese botón ya no está vigente.", inert=True)

    persisted = outcome.as_json()
    cur.execute(
        "update task_intake_choice_set set resultado = %s where id = %s",
        (Jsonb(persisted), choice["choice_set_id"]),
    )
    cur.execute(
        "update task_intake_choice set resultado = %s where id = %s",
        (Jsonb(persisted), choice["choice_id"]),
    )
    return outcome


def _seguir_con_el_borrador(cur, request, who, now) -> IntakeOutcome:
    """"Continuar borrador" (`resolve_choice`): con el alta conducida, el modelo
    retoma la conversación donde estaba; si no, la próxima pregunta de siempre."""
    from . import alta_conducida

    if alta_conducida.alta_conducida(cur, who.workspace_id):
        return alta_conducida.continuar(cur, who, request, now)
    return _advance(cur, request, who, now)


def consume_pending_text(cur: psycopg.Cursor, who: Solicitante, *, chat_id: int,
                         source_inbound_id: str, source_raw_text: str,
                         now: datetime, slot_id: str | None = None,
                         valor: dict | None = None,
                         propuestas: dict | None = None,
                         ) -> IntakeOutcome | None:
    """Toma el mensaje como el campo que espera el alta. `slot_id`, si viene,
    es el campo que la persona respondió (el que el gateway leyó al
    interpretar el mensaje, T9-R1c-1): si ese campo ya no está abierto no se
    consume ningún otro.

    `valor` es lo que el modelo interpretó del mensaje para este campo (ADR
    0014, M1: `fecha_iso`, `texto`); el código sólo lo valida, nunca interpreta
    el texto. Un valor que no sirve deja el campo abierto y dice la razón; uno
    que falta (el modelo no pudo interpretar) lo deja abierto, registra un
    incidente y manda el aviso neutro."""
    cur.execute(
        """select s.*, r.version, r.estado request_estado
             from task_intake_free_text_slot s
             join task_intake_request r on r.id = s.request_id
            where s.workspace_id = %s and r.membership_id = %s
              and r.chat_id = %s and s.estado = 'active' and r.estado = 'active'
              and r.enviada_en is null
              and (%s::uuid is null or s.id = %s::uuid)
            for update of s, r""",
        (who.workspace_id, who.membership_id, chat_id, slot_id, slot_id),
    )
    slot = cur.fetchone()
    if not slot:
        return None
    request_id = str(slot["request_id"])
    field = slot["campo"]
    esperado = _esperado_del_campo(cur, who.workspace_id, field, now)
    resultado = validar_valor(valor, esperado,
                              limite_texto=USER_FIELD_LIMITS[field])
    if isinstance(resultado, Rechazado):
        return _rechazar_valor(cur, _request(cur, request_id), who, field,
                               resultado, source_inbound_id, now)
    if field == "due_date":
        value = resultado.valor.isoformat()
    else:
        value = normalize_text(resultado.valor)
        if not value:
            return _rechazar_valor(
                cur, _request(cur, request_id), who, field,
                Rechazado(MotivoRechazo.TEXTO_VACIO, "Ese texto está vacío.",
                          "Escribilo de nuevo."), source_inbound_id, now)
        if telegram_text_length(value) > USER_FIELD_LIMITS[field]:
            return _reject_user_value(
                cur, _request(cur, request_id), field,
                _user_limit_prompt(field), source_inbound_id, now,
            )

    propuesta = (_criterio_a_proponer(cur, request_id, who, valor, value,
                                      source_inbound_id)
                 if field == "acceptance_criterion" else None)
    cur.execute(
        """update task_intake_free_text_slot
              set estado = 'consumed', source_inbound_id = %s,
                  source_raw_text = %s, consumido_en = %s
            where id = %s""",
        (source_inbound_id, source_raw_text, now, slot["id"]),
    )
    cur.execute(
        """update task_intake_request set version = version + 1,
                  actualizado_en = %s where id = %s returning *""",
        (now, request_id),
    )
    request = cur.fetchone()
    if field in {"objective", "responsible", "area"}:
        return _resolve_user_entity(cur, request, who, field, value,
                                    source_inbound_id, source_raw_text, now)
    if propuesta:
        # La persona no eligió este criterio: queda propuesto, con los botones para
        # usarlo o escribir otro (F-B7).
        cur.execute(
            """update task_intake_field
                  set estado = 'proposed', valor = %s, proposed_by = 'model',
                      source_inbound_id = %s, source_raw_text = %s,
                      source_choice_id = null, version = version + 1,
                      actualizado_en = %s
                where request_id = %s and campo = 'acceptance_criterion'""",
            (Jsonb(propuesta), source_inbound_id, source_raw_text, now, request_id))
        return _advance(cur, request, who, now, rechazo=RECHAZO_CRITERIO,
                        campo_del_rechazo="acceptance_criterion")
    avisos = ""
    if field == "title" and propuestas is not None:
        avisos = _rehacer_propuestas(cur, request_id, propuestas, source_inbound_id,
                                     source_raw_text, now, who.workspace_id)
    _confirm_user_value(cur, request_id, field, value, source_inbound_id,
                        source_raw_text, now)
    return _advance(cur, request, who, now, prefijo=avisos)


def _rehacer_propuestas(cur, request_id, propuestas, inbound_id, raw, now,
                        workspace_id) -> str:
    """El título lo dio un mensaje que es en sí un pedido de tarea nueva (F-B8): lo
    propuesto por otro mensaje y que nadie confirmó era de la tarea que ese otro
    mensaje pedía (por ejemplo, el que se dejó de lado para ver otra cosa), no de
    esta. Esas propuestas caen, y quedan las que trae el mensaje nuevo. Lo que la
    persona ya confirmó en esta alta no se toca. Devuelve el aviso de lo que el
    mensaje nuevo propuso y no sirvió, como `_store_proposals`."""
    cur.execute(
        """update task_intake_field
              set estado = 'missing', valor = null, proposed_by = null,
                  source_inbound_id = null, source_raw_text = null,
                  source_choice_id = null, version = version + 1,
                  actualizado_en = %s
            where request_id = %s and estado = 'proposed' and proposed_by = 'model'
              and source_inbound_id is distinct from %s""",
        (now, request_id, inbound_id))
    propias = {k: v for k, v in propuestas.items() if k != "title"}
    return _store_proposals(cur, request_id, propias, inbound_id, raw, now,
                            workspace_id)


def _rechazar_valor(cur, request, who, field, rechazo: Rechazado, inbound_id,
                    now, *, choice_set_id=None) -> IntakeOutcome:
    """Un valor que el código no aceptó (ADR 0014, M1). La misma pregunta sigue
    abierta -- el campo de texto, o la elección con sus botones -- y:

    - un valor que no sirve (una fecha pasada, una opción que no se ofreció) es
      conversación normal: se dice la razón real y qué sirve, sin incidente;
    - un valor que falta (`SIN_VALOR`: el modelo no pudo interpretar) es una
      falla: incidente y el aviso neutro, delante de la misma pregunta."""
    if rechazo.motivo is MotivoRechazo.SIN_VALOR:
        registrar_incidente(
            cur, who.workspace_id,
            "El modelo no pudo interpretar el valor de la respuesta a una "
            "pregunta del alta de tareas; la pregunta sigue abierta.",
            etapa=ETAPA_VALOR_SIN_INTERPRETAR, app_user_id=who.app_user_id,
            chat_id=request["chat_id"],
            referencia_tipo=REFERENCIA_INBOUND_MESSAGE if inbound_id else None,
            referencia_id=inbound_id)
        aviso = f"{NOTICIA_NEUTRA_INCIDENTE}\n\n"
    elif rechazo.motivo is MotivoRechazo.TEXTO_LARGO:
        aviso = f"{_user_limit_prompt(field)}\n\n"
    else:
        hecho = Rechazo(rechazo.razon, rechazo.se_acepta)
        aviso = redactar_partes(ResultadoTurno(rechazo=hecho), "B").texto + "\n\n"
        if (field in _SUJETO_DEL_CAMPO and variante_redaccion(
                cur, str(request["workspace_id"])) == "A"):
            return _rechazo_entero(cur, request, who, field, hecho, aviso,
                                   inbound_id, choice_set_id, now)
    if choice_set_id is not None:
        if resend_choice_prompt(cur, who, choice_set_id, now, prefix=aviso):
            return IntakeOutcome(str(request["id"]), aviso.strip(), inert=True,
                                 responded=True)
        return IntakeOutcome(str(request["id"]), "", inert=True)
    if rechazo.motivo is MotivoRechazo.SIN_VALOR:
        texto = aviso + _free_text_prompt(field)
    else:
        texto = aviso.strip()
    return _reject_user_value(cur, request, field, texto, inbound_id, now)


def _rechazo_entero(cur, request, who, field, hecho: Rechazo, aviso: str,
                    inbound_id, choice_set_id, now) -> IntakeOutcome:
    """Un valor que no sirve con la variante A: UN mensaje del modelo con la razón
    y la misma pregunta (antes eran dos llamadas, la razón y la pregunta
    pegadas). Si el modelo no sirve, sale lo de B: la razón sola para un campo de
    texto, o la razón delante de la pregunta guardada para una elección. Una
    elección que ya no está abierta no se redacta: no se llama al modelo para un
    mensaje que no se manda."""
    if choice_set_id is not None:
        if not _request_of_question(cur, who, QUESTION_CHOICE, choice_set_id,
                                    lock=False):
            return IntakeOutcome(str(request["id"]), "", inert=True)
        cur.execute(
            """select etiqueta from task_intake_choice
                where choice_set_id = %s and activa order by orden""",
            (choice_set_id,))
        etiquetas = [f["etiqueta"] for f in cur.fetchall()]
        guardada = _first_choice_prompt(cur, choice_set_id)
        texto = _decir_pregunta(
            cur, request, field, TipoValor.OPCION, aviso + guardada, now,
            pregunta=guardada, opciones=etiquetas, rechazo=hecho)
        if resend_choice_prompt(cur, who, choice_set_id, now, texto=texto):
            return IntakeOutcome(str(request["id"]), texto.strip(), inert=True,
                                 responded=True)
        return IntakeOutcome(str(request["id"]), "", inert=True)
    texto = _decir_pregunta(
        cur, request, field, TIPO_DE_CAMPO.get(field, TipoValor.TEXTO),
        aviso.strip(), now, pregunta=_free_text_prompt(field), rechazo=hecho)
    return _reject_user_value(cur, request, field, texto, inbound_id, now)


def _mostrar_valor(campo: str, valor) -> str:
    """Un dato del alta como lo lee una persona."""
    if campo == "due_date":
        return format_due_date(valor)
    if isinstance(valor, dict):
        return str(valor.get("title") or valor.get("name") or "")
    return str(valor or "")


def _entendido_del_turno(cur, request_id: str, now: datetime
                         ) -> tuple[ValorAceptado, ...] | None:
    """Lo que la persona dio en ESTE turno, leído de la base: los datos que
    quedaron confirmados por lo que dijo o tocó (no los que el código completa
    solo: la descripción vacía, la evidencia o un dato con una sola opción). El
    turno es el mensaje al que está atado (el dato lo dio ese mensaje) o, para un
    toque, la hora del turno. Es contexto para que el modelo lo diga en su
    mensaje. `None` si un dato no tiene cómo nombrarse: quien llama cae a B."""
    atado = entrante_atado(cur)
    cur.execute(
        """select campo, valor from task_intake_field
            where request_id = %s and estado = 'confirmed'
              and (actualizado_en = %s
                   or (%s::text is not null and source_inbound_id::text = %s))
              and campo <> all(%s)
              and not (proposed_by = 'server' and source_choice_id is null)
            order by array_position(%s::text[], campo)""",
        (request_id, now, atado, atado,
         ["description", "evidence"], list(FIELDS)))
    dados = []
    for fila in cur.fetchall():
        if fila["campo"] not in _SUJETO_DEL_CAMPO:
            return None
        mostrado = _mostrar_valor(fila["campo"], fila["valor"])
        if mostrado:
            dados.append(ValorAceptado(_SUJETO_DEL_CAMPO[fila["campo"]], mostrado))
    return tuple(dados)


def _conversacion_de(cur, request, now: datetime) -> list[dict]:
    """La conversación reciente de la persona del alta (`contexto.historial`: lo
    que de verdad se dijeron, sin el mensaje que dispara este turno), para que el
    modelo que redacta vea lo que ya dijo y no repita sus fórmulas (F-C4)."""
    from .contexto import historial

    return historial(cur, request["chat_id"], now, entrante_atado(cur))


def _quien_escribe(cur, request) -> tuple[str, ...]:
    """El nombre de la persona del alta: un nombre que el turno ya conoce y el
    verificador deja decir sin que esté en los hechos."""
    cur.execute(
        "select nombre from integrante where membership_id = %s",
        (request["membership_id"],))
    fila = cur.fetchone()
    return (fila["nombre"],) if fila and fila["nombre"] else ()


def _decir_pregunta(cur, request, field: str, tipo: TipoValor, prompt: str,
                    now: datetime, *, pregunta: str | None = None, opciones=(),
                    rechazo: Rechazo | None = None,
                    busqueda: str | None = None,
                    propuesto: str | None = None) -> str:
    """El mensaje con que se pide un dato (ADR 0014, etapa 6 completa). Con B es
    `prompt` tal cual. Con A, el modelo escribe el mensaje entero (lo que
    entendió, el rechazo si lo hubo, la pregunta y para qué sirven las opciones)
    y el código lo verifica; si no sirve, sale `prompt` como con B. `pregunta` es
    la pregunta limpia cuando `prompt` es un aviso (una búsqueda sin
    resultados). `propuesto` es el valor que se pide confirmar: tiene que salir
    tal cual en el mensaje (es lo que la persona confirma), de cualquier largo."""
    workspace_id = str(request["workspace_id"])
    if variante_redaccion(cur, workspace_id) != "A":
        return prompt
    entendido = (_entendido_del_turno(cur, str(request["id"]), now)
                 if field in _SUJETO_DEL_CAMPO else None)
    if entendido is None:
        # Un dato sin cómo nombrarse (un defecto del código, no de la persona):
        # sale el texto de B y queda registrado; nunca un error en el turno.
        registrar_incidente(
            cur, workspace_id,
            "Un dato del alta no tiene sujeto para redactar (variante A): se usó "
            "la respuesta de la variante B.", severidad="baja",
            referencia_cruda=f"campo: {field}",
            etapa=ETAPA_REDACCION_RECHAZADA, avisar_admin=False)
        return prompt
    if busqueda:
        entendido += (ValorAceptado("lo que buscaste", busqueda),)
    resultado = ResultadoTurno(
        falta=Falta(_SUJETO_DEL_CAMPO[field], tipo, pregunta=pregunta or prompt,
                    campo=field),
        opciones=tuple(OpcionDisponible(etiqueta_sin_icono(o), "elegir")
                       for o in opciones),
        entendido=entendido, rechazo=rechazo,
        valores_aceptados=((ValorAceptado(_SUJETO_DEL_CAMPO[field], propuesto),)
                           if propuesto else ()),
        nombres_conocidos=_quien_escribe(cur, request))
    texto = redactar_turno(cur, workspace_id, resultado, "A",
                           base=TextoRedactado(prompt),
                           historial=_conversacion_de(cur, request, now))
    if texto.fallida and propuesto:
        # El modelo no pudo redactar y los botones confirman un valor: ese valor
        # sale a la vista, nadie lo confirma a ciegas.
        return f"{texto.texto}\n\n{propuesto}"
    return texto.texto


def _decir_envio(cur, request, aprobador_nombre) -> str:
    """A quién se le mandó el borrador. Con A lo cuenta el modelo como un efecto
    del resultado (el único que hubo) y nada más; si no sirve, el aviso de
    siempre."""
    base = draft_sent_text(aprobador_nombre)
    workspace_id = str(request["workspace_id"])
    if variante_redaccion(cur, workspace_id) != "A":
        return base
    nombre = (normalize_text(aprobador_nombre)
              if isinstance(aprobador_nombre, str) else "")
    resultado = ResultadoTurno(
        cambios=(Cambio("el borrador de la tarea",
                        f"quedó enviado a {nombre or 'otra persona del equipo'} "
                        "para que lo confirme", id="borrador_enviado"),),
        sin_cambios=(SinCambio("la tarea", "se crea cuando lo confirme"),),
        nombres_conocidos=_quien_escribe(cur, request))
    return redactar_turno(cur, workspace_id, resultado, "A",
                          base=TextoRedactado(base),
                          historial=_conversacion_de(
                              cur, request, datetime.now(timezone.utc))).texto


def handle_active_text(cur: psycopg.Cursor, who: Solicitante, *, chat_id: int,
                       source_inbound_id: str, source_raw_text: str,
                       now: datetime) -> IntakeOutcome | None:
    """Atiende el mensaje de quien tiene un alta activa y ninguna pregunta
    abierta que leer: el recordatorio de la elección o del estado del borrador.

    Las preguntas del alta (un campo de texto libre, una elección con botones
    y el borrador esperando su confirmación) ya no se toman acá (T9-R1c-1 y
    T9-R1c-2, ADR 0013 regla 1): un mensaje que responde a una pregunta
    pendiente se interpreta antes, y el gateway las lee con
    `open_intake_question`. Esto queda para el estado que no es ninguna de
    ellas, y como red de seguridad de las otras dos."""
    cur.execute(
        """select r.*, s.id choice_set_id
             from task_intake_request r
             left join task_intake_choice_set s
               on s.request_id = r.id and s.estado = 'active'
            where r.workspace_id = %s and r.membership_id = %s
              and r.chat_id = %s and r.estado = 'active'
              and r.enviada_en is null
            for update of r""",
        (who.workspace_id, who.membership_id, chat_id),
    )
    request = cur.fetchone()
    if not request:
        return None
    if (request["terminal_result"] or {}).get(PAUSADO):
        # Un borrador pausado no es una rama abierta (F-C6): el mensaje sigue el
        # camino normal, no se traga con un recordatorio.
        return None
    request_id = str(request["id"])
    if request["choice_set_id"]:
        prompt = _first_choice_prompt(cur, request["choice_set_id"])
        _enqueue(
            cur, request, prompt, now,
            f"intake:{request_id}:reminder:{source_inbound_id}",
            choice_set_id=str(request["choice_set_id"]),
        )
        return IntakeOutcome(request_id, prompt, inert=True)

    cur.execute(
        """select membership_id, herramienta from pending_action
            where draft_id = %s and estado = 'esperando'
            order by creado_en desc limit 1""",
        (request["task_draft_id"],),
    )
    waiting = cur.fetchone()
    if waiting and str(waiting["membership_id"]) != str(who.membership_id):
        # Espera la confirmación de otra persona (ya se la envió): no es una rama
        # abierta de quien lo pidió y su mensaje sigue el camino normal. Desde la
        # migración 0026 las enviadas ni llegan acá (`enviada_en`); queda para las
        # enviadas antes de aplicarla.
        return None
    if waiting:
        prompt = _awaiting_prompt(waiting["herramienta"])
    else:
        prompt = with_no_effect_status(
            "No pude continuar el borrador de la tarea. "
            "Probá cancelarlo y empezar de nuevo.")
    _enqueue(cur, request, prompt, now,
             f"intake:{request_id}:state:{source_inbound_id}")
    return IntakeOutcome(request_id, prompt, inert=True)


# Cómo se nombra cada campo de texto libre del alta ante la persona (la
# pregunta abierta, T9-R1c-1): "¿Seguimos con el título de la tarea nueva?".
FREE_TEXT_NAMES = {
    "title": "el título",
    "description": "la descripción",
    "objective": "el objetivo",
    "responsible": "la persona responsable",
    "area": "el área",
    "due_date": "la fecha objetivo",
    "acceptance_criterion": "el criterio de aceptación",
}


def free_text_question(field: str) -> str:
    """La pregunta que se le hizo a la persona para ese campo, la misma al
    volver a hacerla."""
    return _free_text_prompt(field)


def open_free_text_slot(cur: psycopg.Cursor, who: Solicitante,
                        chat_id: int) -> dict | None:
    """Lee, sin consumir, el campo de texto libre que espera el alta de esta
    persona en este chat: `{slot_id, request_id, campo, titulo}` (`titulo`, el
    de la tarea si ya está confirmado) o `None`."""
    cur.execute(
        """select s.id slot_id, s.request_id, s.campo,
                  (select f.valor from task_intake_field f
                    where f.request_id = r.id and f.campo = 'title'
                      and f.estado = 'confirmed') titulo
             from task_intake_free_text_slot s
             join task_intake_request r on r.id = s.request_id
            where s.workspace_id = %s and r.membership_id = %s
              and r.chat_id = %s and s.estado = 'active' and r.estado = 'active'
              and r.enviada_en is null
            order by s.creado_en desc limit 1""",
        (who.workspace_id, who.membership_id, chat_id),
    )
    row = cur.fetchone()
    if not row:
        return None
    titulo = row["titulo"] if isinstance(row["titulo"], str) else None
    return {"slot_id": str(row["slot_id"]), "request_id": str(row["request_id"]),
            "campo": row["campo"], "titulo": titulo}


# Las preguntas abiertas del alta (T9-R1c-1 y T9-R1c-2, ADR 0013 regla 1): lo
# que espera la persona mientras la solicitud está activa. `tipo` dice cuál.
QUESTION_FREE_TEXT = "free_text"      # un campo de texto libre
QUESTION_CHOICE = "choice"            # una elección con botones
QUESTION_CONFIRMATION = "confirmation"  # el borrador esperando su confirmación
# La marca de un borrador pausado en `terminal_result` (`pause_from_intake_question`).
PAUSADO = "pausado"
# La marca de que el alta conducida ya le propuso un criterio de aceptación a la
# persona (una sola propuesta por alta): vive en `terminal_result` junto a la pausa,
# sin cambiar el esquema, y `resolve_choice` la conserva.
CRITERIO_PROPUESTO = "criterio_propuesto"
_TITLE_OF_REQUEST = """(select f.valor from task_intake_field f
                         where f.request_id = r.id and f.campo = 'title'
                           and f.estado = 'confirmed')"""


def open_intake_question(cur: psycopg.Cursor, who: Solicitante,
                         chat_id: int) -> dict | None:
    """Lee, sin consumir, la pregunta que espera el alta de esta persona en
    este chat, o `None`: `{tipo, id, request_id, campo, titulo, resumen,
    opciones}` (y `bloque` en un campo de texto libre: lo que la persona tenía, si
    lo está corrigiendo). `id` es el del campo de texto libre, el de la elección o el de
    la vista previa (su `pending_action`); `resumen` es la pregunta que se le
    hizo; `opciones` (sólo en una elección) son las etiquetas de sus botones,
    sin íconos, y `clase` el `tipo` de la elección (`MODIFY_PICKER_KIND` para el
    selector de Modificar). Con varias, gana el campo de texto libre, después la elección:
    una solicitud tiene una sola a la vez. La vista previa del borrador es una
    pregunta abierta sólo de quien tiene sus botones: quien confirma o, si lo
    confirma otra persona, quien lo pidió mientras revisa su resumen antes de
    enviarlo (`revision`, T9-R1c-4: Enviar a aprobación, Modificar y Cancelar).
    Una vez enviado, quien lo pidió no tiene una rama abierta (ADR 0013 regla 1,
    enmienda del 2026-09-29) y sus mensajes siguen el camino normal."""
    slot = open_free_text_slot(cur, who, chat_id)
    if slot is not None:
        # Un dato ya confirmado que se está corrigiendo (Modificar) lleva lo que la
        # persona tenía, para volver a mostrárselo al repreguntar (`bloque`).
        block = text_to_copy(cur, slot["request_id"], slot["campo"],
                             confirmed_only=True)
        return {"tipo": QUESTION_FREE_TEXT, "id": slot["slot_id"],
                "request_id": slot["request_id"], "campo": slot["campo"],
                "titulo": slot["titulo"],
                "resumen": free_text_question(slot["campo"]), "opciones": None,
                "bloque": block or None}
    cur.execute(
        f"""select s.id, s.request_id, s.campo, s.tipo, {_TITLE_OF_REQUEST} titulo
              from task_intake_choice_set s
              join task_intake_request r on r.id = s.request_id
             where s.workspace_id = %s and r.membership_id = %s
               and r.chat_id = %s and s.estado = 'active' and r.estado = 'active'
              and r.enviada_en is null
             order by s.creado_en desc limit 1""",
        (who.workspace_id, who.membership_id, chat_id),
    )
    row = cur.fetchone()
    if row:
        cur.execute(
            """select etiqueta from task_intake_choice
                where choice_set_id = %s and activa order by orden""",
            (row["id"],),
        )
        options = [etiqueta_sin_icono(c["etiqueta"]) for c in cur.fetchall()]
        return {"tipo": QUESTION_CHOICE, "id": str(row["id"]),
                "request_id": str(row["request_id"]), "campo": row["campo"],
                "clase": row["tipo"], "titulo": _text_or_none(row["titulo"]),
                "resumen": _first_choice_prompt(cur, row["id"]),
                "opciones": options}
    cur.execute(
        f"""select p.id, p.herramienta, r.id request_id,
                   {_TITLE_OF_REQUEST} titulo
              from task_intake_request r
              join pending_action p on p.draft_id = r.task_draft_id
                                   and p.workspace_id = r.workspace_id
             where r.workspace_id = %s and r.membership_id = %s
               and r.chat_id = %s and r.estado = 'active'
               and r.enviada_en is null
               and p.estado = 'esperando' and p.membership_id = %s
             order by p.creado_en desc limit 1""",
        (who.workspace_id, who.membership_id, chat_id, who.membership_id),
    )
    row = cur.fetchone()
    if row:
        return {"tipo": QUESTION_CONFIRMATION, "id": str(row["id"]),
                "request_id": str(row["request_id"]), "campo": None,
                "titulo": _text_or_none(row["titulo"]),
                "resumen": _awaiting_prompt(row["herramienta"]), "opciones": None,
                "revision": row["herramienta"] == HERRAMIENTA_REVISION_BORRADOR}
    return None


def _awaiting_prompt(tool: str) -> str:
    """Lo que se le dice a quien escribe mientras su resumen espera un botón: su
    revisión antes de enviar a aprobación (T9-R1c-4) o la confirmación del borrador.
    Cada uno nombra los botones que esa persona de verdad tiene."""
    return (DRAFT_AWAITING_SEND if tool == HERRAMIENTA_REVISION_BORRADOR
            else DRAFT_AWAITING_CONFIRMATION)


def _text_or_none(value) -> str | None:
    return value if isinstance(value, str) else None


# Cada tipo de pregunta se ata a su solicitud activa por su propia tabla.
_REQUEST_OF_QUESTION = {
    QUESTION_FREE_TEXT: (
        """select r.* from task_intake_free_text_slot s
             join task_intake_request r on r.id = s.request_id
            where s.id = %s and s.workspace_id = %s and r.membership_id = %s
              and s.estado = 'active' and r.estado = 'active'""",
        "for update of s, r"),
    QUESTION_CHOICE: (
        """select r.* from task_intake_choice_set s
             join task_intake_request r on r.id = s.request_id
            where s.id = %s and s.workspace_id = %s and r.membership_id = %s
              and s.estado = 'active' and r.estado = 'active'""",
        "for update of s, r"),
    QUESTION_CONFIRMATION: (
        """select r.* from pending_action p
             join task_intake_request r on r.task_draft_id = p.draft_id
                                       and r.workspace_id = p.workspace_id
            where p.id = %s and p.workspace_id = %s and r.membership_id = %s
              and p.estado = 'esperando' and r.estado = 'active'""",
        "for update of p, r"),
}


def _request_of_question(cur, who, kind: str, question_id: str, *, lock: bool):
    query, lock_clause = _REQUEST_OF_QUESTION[kind]
    cur.execute(f"{query} {lock_clause if lock else ''}",
                (question_id, who.workspace_id, who.membership_id))
    return cur.fetchone()


def intake_question_active(cur: psycopg.Cursor, who: Solicitante, kind: str,
                           question_id: str) -> bool:
    """Si esa pregunta sigue esperando la respuesta (`tipo` e `id` de
    `open_intake_question`)."""
    return _request_of_question(cur, who, kind, question_id, lock=False) is not None


def cancel_from_intake_question(cur: psycopg.Cursor, who: Solicitante, kind: str,
                                question_id: str, now: datetime) -> bool:
    """La persona deja el alta desde una pregunta abierta (T9-R1c-1 y
    T9-R1c-2): cancela el borrador por el mismo camino que el botón "Cancelar
    borrador", sin encolar su aviso (lo dice el gateway). `False` si esa
    pregunta ya no estaba abierta: no cancela nada."""
    request = _request_of_question(cur, who, kind, question_id, lock=True)
    if not request:
        return False
    _cancel(cur, request, who, now, enqueue=False)
    return True


def pause_from_intake_question(cur: psycopg.Cursor, who: Solicitante, kind: str,
                               question_id: str, now: datetime) -> bool:
    """La persona deja el alta para ver otra cosa ("Dejarlo y ver lo otro"): el
    borrador se GUARDA, no se cancela (F-C6: lo perdía detrás de una clasificación
    que puede fallar). Queda activo y pausado -- sin ninguna pregunta abierta que
    tome sus mensajes siguientes ni botones vivos --, y el próximo pedido de una
    tarea ofrece continuarlo (`start`: "Ya hay un borrador en curso"). Sólo un
    Cancelar explícito lo cancela. La pausa es una marca en `terminal_result` de la
    solicitud (que un borrador activo no usa), sin cambiar el esquema; `Continuar`
    la quita (`resolve_choice`). `False` si esa pregunta ya no estaba abierta."""
    request = _request_of_question(cur, who, kind, question_id, lock=True)
    if not request:
        return False
    pause_request(cur, who, request, now)
    return True


def pause_request(cur, who: Solicitante, request, now: datetime) -> None:
    """Pausa el borrador de `request` (ya leído y bloqueado): lo guarda sin
    ninguna pregunta abierta ni botones vivos, y lo audita. Lo usan "Dejarlo" y el
    alta conducida (la persona lo deja para después o cambia de tema)."""
    request_id = str(request["id"])
    cur.execute(
        """update task_intake_request
              set terminal_result = coalesce(terminal_result, '{}'::jsonb) || %s,
                  version = version + 1, actualizado_en = %s
            where id = %s""",
        (Jsonb({PAUSADO: True}), now, request_id))
    _invalidate_open_inputs(cur, request_id)
    registrar_auditoria(
        cur, accion="pausar_ingreso_tarea", workspace_id=who.workspace_id,
        actor_app_user_id=who.app_user_id, actor_kind="persona",
        sujeto_tipo="task_draft", sujeto_id=str(request["task_draft_id"]),
        detalle={"request_id": request_id})


def open_modify_picker(cur: psycopg.Cursor, who: Solicitante, question_id: str,
                       now: datetime, *, via: str) -> IntakeOutcome | None:
    """Modificar en la vista previa del borrador (T9-R1c-3, ADR 0005 decisión 1):
    la cierra sin aplicar nada -- la tarea se crea sólo con Confirmar -- y abre el
    selector "qué dato cambiar", con un botón por dato y otro para volver al resumen
    sin cambiar nada (`BACK_TO_SUMMARY`). `question_id` es el de la
    vista previa (`open_intake_question`, `QUESTION_CONFIRMATION`); `via` es cómo
    llegó la persona (`boton` o `texto`, un mensaje que corrige) y sólo se
    audita. `None` si la vista previa ya no esperaba: no abre nada."""
    request = _request_of_question(cur, who, QUESTION_CONFIRMATION, question_id,
                                   lock=True)
    if not request:
        return None
    registrar_auditoria(
        cur, accion="modificar_ingreso_tarea", workspace_id=who.workspace_id,
        actor_app_user_id=who.app_user_id, actor_kind="persona",
        sujeto_tipo="task_draft", sujeto_id=str(request["task_draft_id"]),
        detalle={"request_id": str(request["id"]), "via": via})
    # Sólo lo que se puede cambiar (regla 3 del ADR 0013): un dato con una sola
    # opción posible, como el área de quien tiene un solo lugar, no se ofrece.
    options = [(MODIFY_FIELD_LABELS[field], "modify_field", {"field": field})
               for field in MODIFY_FIELD_LABELS
               if field not in CHOICE_FIELDS
               or _unica_opcion(cur, request, who, field) is None]
    options.append((BACK_TO_SUMMARY, "back_to_summary", None))
    return _open_choices(cur, request, None, MODIFY_PICKER_PROMPT, options, now,
                         kind=MODIFY_PICKER_KIND)


# Los valores de los botones de la vista previa del borrador que no llegan a la
# autoridad: los intercepta el gateway (la conversión es sólo del botón Confirmar).
VALUE_MODIFY = "modificar"
VALUE_SEND = "enviar"
# Rechazar, el botón de quien confirma el borrador de otra persona: pide el motivo
# y cancela recién con él (`reject_from_preview`, `reject_draft`). Nunca llega a la
# autoridad: `resolver_ingreso_borrador` lo rechaza (migración 0025).
VALUE_REJECT = "rechazar"

_DRAFT_BUTTON = """select p.id, p.draft_id, p.membership_id, p.chat_id, p.estado,
                  p.vence_en > %s as vigente
             from pending_action_option o
             join pending_action p on p.id = o.pending_action_id
            where o.token = %s and o.workspace_id = %s and p.draft_id is not null
              and o.valor = to_jsonb(%s::text)"""


def _draft_button(cur, who: Solicitante, token: str, now: datetime, value: str):
    cur.execute(_DRAFT_BUTTON, (now, token, who.workspace_id, value))
    return cur.fetchone()


def es_modificar_de_borrador(cur: psycopg.Cursor, who: Solicitante, token: str,
                             now: datetime) -> bool:
    """Si `token` es el del botón Modificar de una vista previa de borrador."""
    return _draft_button(cur, who, token, now, VALUE_MODIFY) is not None


def es_enviar_de_borrador(cur: psycopg.Cursor, who: Solicitante, token: str,
                          now: datetime) -> bool:
    """Si `token` es el del botón Enviar a aprobación del resumen de quien pidió
    el borrador (T9-R1c-4)."""
    return _draft_button(cur, who, token, now, VALUE_SEND) is not None


def es_rechazar_de_borrador(cur: psycopg.Cursor, who: Solicitante, token: str,
                            now: datetime) -> bool:
    """Si `token` es el del botón Rechazar de la vista previa que ve quien confirma
    el borrador de otra persona."""
    return _draft_button(cur, who, token, now, VALUE_REJECT) is not None


def reject_from_preview(cur: psycopg.Cursor, who: Solicitante, *, token: str,
                        chat_id: int, now: datetime) -> dict | None:
    """El botón Rechazar de la vista previa de quien confirma. No cancela nada: dice
    de qué borrador se trata (`draft_id`, `titulo`) para que el gateway le pida el
    motivo. Sólo lo toca quien confirma, en su chat (`Denegado` si no), y sólo
    mientras la vista previa espera y no venció; `None` si ya no (un toque tardío)."""
    button = _draft_button(cur, who, token, now, VALUE_REJECT)
    if not button:
        return None
    if str(button["membership_id"]) != str(who.membership_id) \
            or button["chat_id"] != chat_id:
        raise Denegado(NOT_YOURS)
    if button["estado"] != "esperando" or not button["vigente"]:
        return None
    cur.execute("select titulo from task_draft where id = %s", (button["draft_id"],))
    draft = cur.fetchone()
    if not draft:
        return None
    return {"draft_id": str(button["draft_id"]), "titulo": draft["titulo"]}


def rejected_text(title: str, requester_name: str) -> str:
    """El recibo de quien rechazó: lo que hizo y a quién le avisó."""
    return (f"Listo, rechacé el borrador de la tarea «{title}» y le avisé a "
            f"{requester_name}.")


def rejection_notice_text(rejecter_name: str, title: str, reason: str) -> str:
    """El aviso de coordinación a quien pidió el borrador: quién lo rechazó, cuál y
    por qué."""
    return (f"{rejecter_name} rechazó el borrador de la tarea «{title}»: "
            f"{reason}")


def reject_draft(cur: psycopg.Cursor, who: Solicitante, *, draft_id: str,
                 reason: str, now: datetime) -> str | None:
    """Rechaza el borrador de otra persona con el motivo que quien confirma acaba de
    dar: lo cancela por el mismo camino que Cancelar (`_cancel`, con el motivo en la
    auditoría), le encola a quien lo pidió el aviso de coordinación y devuelve el
    recibo de quien rechazó, que el gateway le dice como respuesta a su mensaje.
    Todo en la transacción del turno: o pasa todo o nada.

    `None` si ya no correspondía -- el borrador se confirmó, venció o lo cancelaron
    entre el toque y el motivo, o `who` no es quien confirma --: no cambia ni avisa
    nada. Sólo rechaza quien tiene la vista previa vigente, la misma que Confirmar
    convertiría."""
    cur.execute(
        """select p.id from pending_action p
            where p.draft_id = %s and p.membership_id = %s
              and p.estado = 'esperando' and p.vence_en > %s
              and p.workspace_id = %s
            for update""",
        (draft_id, who.membership_id, now, who.workspace_id))
    if not cur.fetchone():
        return None
    cur.execute(
        """select * from task_intake_request
            where task_draft_id = %s and workspace_id = %s and estado = 'active'
            for update""", (draft_id, who.workspace_id))
    request = cur.fetchone()
    if not request or str(request["membership_id"]) == str(who.membership_id):
        return None
    cur.execute("select titulo from task_draft where id = %s", (draft_id,))
    title = cur.fetchone()["titulo"]
    cur.execute("select nombre from integrante where membership_id = %s",
                (request["membership_id"],))
    requester = cur.fetchone()
    _cancel(cur, request, who, now, enqueue=False, reason=reason)
    enqueue_outbox(
        cur, workspace_id=str(request["workspace_id"]), chat_id=request["chat_id"],
        recipient_membership_id=str(request["membership_id"]),
        text=rejection_notice_text(who.nombre, title, reason),
        scheduled_for=now, dedupe_key=f"intake:{request['id']}:rejected-notice",
        allow_split=True, es_coordinacion=True,
    )
    return rejected_text(title, requester["nombre"] if requester else "quien lo pidió")


def approval_notice_text(confirmer_name: str, title: str) -> str:
    """El aviso de coordinación a quien pidió el borrador cuando otra persona lo
    confirmó: quién lo confirmó y cuál tarea quedó creada. Mismo estilo que el aviso
    del rechazo (`rejection_notice_text`)."""
    return (f"{confirmer_name} confirmó el borrador de la tarea «{title}»: "
            "la tarea quedó creada.")


def notify_requester_of_approval(cur: psycopg.Cursor, who: Solicitante, *,
                                 pending_action_id: str, now: datetime) -> bool:
    """Le avisa a quien pidió el borrador que `who` (quien confirma) lo convirtió en
    tarea: sin esto, quien lo pidió no se enteraba de que su tarea existía (el
    rechazo sí avisaba). Es un aviso de coordinación (fuera del tope diario, igual
    que el del rechazo), sin modelo, una sola vez por borrador (`dedupe_key`) y
    auditado. No manda nada si quien confirma es quien pidió (confirmó lo suyo) ni si
    la acción no es de un borrador. Devuelve si lo encoló."""
    cur.execute(
        """select r.id, r.workspace_id, r.chat_id, r.membership_id, r.task_draft_id,
                  d.titulo
             from pending_action p
             join task_intake_request r on r.task_draft_id = p.draft_id
                                       and r.workspace_id = p.workspace_id
             join task_draft d on d.id = r.task_draft_id
            where p.id = %s and p.workspace_id = %s""",
        (pending_action_id, who.workspace_id))
    request = cur.fetchone()
    if not request or str(request["membership_id"]) == str(who.membership_id):
        return False
    request_id = str(request["id"])
    enqueued = enqueue_outbox(
        cur, workspace_id=str(request["workspace_id"]), chat_id=request["chat_id"],
        recipient_membership_id=str(request["membership_id"]),
        text=approval_notice_text(who.nombre, request["titulo"]),
        scheduled_for=now, dedupe_key=f"intake:{request_id}:approved-notice",
        allow_split=True, es_coordinacion=True,
    )
    if not enqueued:
        return False
    registrar_auditoria(
        cur, accion="avisar_aprobacion_ingreso_tarea",
        workspace_id=who.workspace_id, actor_app_user_id=who.app_user_id,
        actor_kind="persona", sujeto_tipo="task_draft",
        sujeto_id=str(request["task_draft_id"]),
        detalle={"request_id": request_id})
    return True


def assignment_notice_text(assigner_name: str, title: str, due_date: date | None,
                           criterion: str) -> str:
    """El aviso de coordinación al responsable de una tarea que le asignó otra
    persona: quién, cuál, para cuándo y cómo se da por hecha. Mismo estilo que los
    avisos de aprobación y de rechazo; no promete botones ni acciones que no
    existen."""
    # Un espacio puede no exigir fecha (mecánica §2): sin ella, no se nombra.
    cuando = f", para el {due_date.strftime('%d/%m/%Y')}" if due_date else ""
    return (f"{assigner_name} te asignó la tarea «{title}»{cuando}. Se da por hecha "
            f"cuando: {criterion.rstrip('.')}.")


def notify_responsible_of_assignment(cur: psycopg.Cursor, who: Solicitante, *,
                                     pending_action_id: str, now: datetime) -> bool:
    """Le avisa al responsable que `who` (quien confirma) convirtió el borrador en
    una tarea suya que pidió otra persona: sin esto el responsable no se enteraba
    (hallazgo de la prueba real del 2026-10-01). Aviso de coordinación (fuera del
    tope diario), de código y sin modelo, una sola vez por solicitud (`dedupe_key`) y
    auditado.

    No manda nada si el responsable es quien confirma (lo acaba de hacer él) ni si es
    quien pidió (a esa persona ya le llega el aviso de aprobación o lo confirmó ella).
    Va al chat privado del responsable sólo si lo activó (constitución §7): sin chat
    no se encola nada, igual que el resto de los avisos, pero queda en la auditoría
    (`omitir_aviso_asignacion_ingreso_tarea`) para no perderse en silencio. Devuelve
    si lo encoló."""
    cur.execute(
        """select r.id, r.workspace_id, r.membership_id requester_id,
                  t.id task_id, t.titulo, t.criterio_aceptacion,
                  t.responsable_membership_id responsible_id,
                  (t.fecha_objetivo at time zone w.zona_horaria)::date due_date
             from pending_action p
             join task_intake_request r on r.task_draft_id = p.draft_id
                                       and r.workspace_id = p.workspace_id
             join task t on t.source_draft_id = r.task_draft_id
             join workspace w on w.id = t.workspace_id
            where p.id = %s and p.workspace_id = %s""",
        (pending_action_id, who.workspace_id))
    task = cur.fetchone()
    if not task or task["responsible_id"] is None:
        return False
    responsible_id = str(task["responsible_id"])
    if responsible_id in (str(who.membership_id), str(task["requester_id"])):
        return False
    request_id = str(task["id"])
    detail = {"request_id": request_id}
    cur.execute("select telegram_user_id from integrante where membership_id = %s",
                (responsible_id,))
    responsible = cur.fetchone()
    cur.execute("select nombre from integrante where membership_id = %s",
                (task["requester_id"],))
    requester = cur.fetchone()
    if not responsible or responsible["telegram_user_id"] is None:
        registrar_auditoria(
            cur, accion="omitir_aviso_asignacion_ingreso_tarea",
            workspace_id=who.workspace_id, actor_app_user_id=who.app_user_id,
            actor_kind="persona", sujeto_tipo="task", sujeto_id=str(task["task_id"]),
            detalle={**detail, "motivo": "sin_chat"})
        return False
    enqueued = enqueue_outbox(
        cur, workspace_id=str(task["workspace_id"]),
        chat_id=responsible["telegram_user_id"],
        recipient_membership_id=responsible_id,
        text=assignment_notice_text(
            requester["nombre"] if requester else "Alguien", task["titulo"],
            task["due_date"], task["criterio_aceptacion"] or ""),
        scheduled_for=now, dedupe_key=f"intake:{request_id}:assigned-notice",
        allow_split=True, es_coordinacion=True,
    )
    if not enqueued:
        return False
    registrar_auditoria(
        cur, accion="avisar_asignacion_ingreso_tarea",
        workspace_id=who.workspace_id, actor_app_user_id=who.app_user_id,
        actor_kind="persona", sujeto_tipo="task", sujeto_id=str(task["task_id"]),
        detalle=detail)
    return True


def modify_from_preview(cur: psycopg.Cursor, who: Solicitante, *, token: str,
                        chat_id: int, now: datetime) -> IntakeOutcome | None:
    """El botón Modificar de la vista previa del borrador. Sólo lo toca su
    dueño, en su chat (`Denegado` si no), y sólo mientras la vista previa espera y
    no venció; `None` si ya no (un toque tardío, un segundo toque)."""
    preview = _draft_button(cur, who, token, now, VALUE_MODIFY)
    if not preview:
        return None
    if str(preview["membership_id"]) != str(who.membership_id)        or preview["chat_id"] != chat_id:
        raise Denegado(NOT_YOURS)
    if preview["estado"] != "esperando" or not preview["vigente"]:
        return None
    from . import alta_conducida

    if alta_conducida.alta_conducida(cur, who.workspace_id):
        # El alta conducida no tiene un selector de datos: lo conversa el modelo.
        request = _request_of_question(cur, who, QUESTION_CONFIRMATION,
                                       str(preview["id"]), lock=True)
        if not request:
            return None
        return alta_conducida.modificar(cur, who, request, now)
    return open_modify_picker(cur, who, str(preview["id"]), now, via="boton")


def send_to_approval(cur: psycopg.Cursor, who: Solicitante, *, token: str,
                     chat_id: int, now: datetime) -> IntakeOutcome | None:
    """El botón Enviar a aprobación del resumen de quien pidió el borrador (T9-R1c-4,
    ADR 0005 decisión 1). Sólo lo toca su dueño, en su chat (`Denegado` si no), y
    sólo mientras el resumen espera y no venció; `None` si ya no (un toque tardío, un
    segundo toque). Un resumen que el borrador dejó atrás no se envía: se vence y la
    respuesta es el resumen vigente para revisarlo (`_offer_current_review`).

    Cierra su resumen de una vez (`cancelada`, marcada `enviada`: el borrador sigue
    vivo) y le registra a quien confirma su propia acción con Confirmar y Cancelar,
    con la vista previa vigente del borrador al enviar; a quien pidió le dice a quién
    se lo mandó (la respuesta a su toque). Si no hay a quién mandárselo, lo dice y su
    resumen sigue abierto: nada se cierra sin haberse enviado."""
    button = _draft_button(cur, who, token, now, VALUE_SEND)
    if not button:
        return None
    if str(button["membership_id"]) != str(who.membership_id)        or button["chat_id"] != chat_id:
        raise Denegado(NOT_YOURS)
    cur.execute(
        """select r.*, p.args review_args, p.preview review_preview
             from pending_action p
             join task_intake_request r on r.task_draft_id = p.draft_id
                                       and r.workspace_id = p.workspace_id
            where p.id = %s and p.estado = 'esperando' and p.vence_en > %s
              and r.estado = 'active'
            for update of p, r""",
        (button["id"], now),
    )
    request = cur.fetchone()
    if not request:
        return None
    request_id = str(request["id"])
    preview, version = _current_preview(cur, request["task_draft_id"])
    if preview != request["review_preview"]:
        # El borrador siguió después de ese resumen: lo que vio quien pide ya no es
        # lo que se enviaría. Nunca se manda lo que no revisó.
        cur.execute(
            "update pending_action set estado = 'vencida' where id = %s",
            (button["id"],))
        cur.execute(
            "update pending_action_option set activa = false "
            "where pending_action_id = %s", (button["id"],))
        return _offer_current_review(cur, who, request_id, now)
    authority = _find_confirmer(cur, _draft_responsible(cur, request))
    if authority is None:
        return _say_real_state(cur, request, NO_ACTIVE_AUTHORITY, now,
                               "no-active-authority")
    cur.execute(
        """update pending_action
              set estado = 'cancelada', resuelta_en = %s, resuelta_por = %s,
                  resultado = jsonb_build_object('resultado', 'enviada')
            where id = %s and estado = 'esperando'""",
        (now, who.app_user_id, button["id"]),
    )
    cur.execute(
        "update pending_action_option set activa = false "
        "where pending_action_id = %s", (button["id"],))
    registrar_auditoria(
        cur, accion="enviar_ingreso_tarea_a_aprobacion",
        workspace_id=who.workspace_id, actor_app_user_id=who.app_user_id,
        actor_kind="persona", sujeto_tipo="task_draft",
        sujeto_id=str(request["task_draft_id"]),
        detalle={"request_id": request_id,
                 "confirmador_membership_id":
                     str(authority["aprobador_membership_id"])})
    # Quien confirma recibe el mismo resumen con el cierre de SU botón.
    texto_para_confirmar = _con_cierre(
        request["review_args"]["cuerpo_resumen"], CIERRE_CONFIRMAR)
    pending, requester_confirms = _send_to_confirmer(
        cur, request, now, texto_para_confirmar, preview, version, authority)
    if requester_confirms:
        # Cambió quién aprueba y ahora es quien pidió: el resumen que recibe, con
        # sus tres botones, es la respuesta a su toque.
        return IntakeOutcome(request_id, texto_para_confirmar, changed=True,
                             pending_action_id=pending.id)
    # Desde que está en manos de otra persona deja de ser la rama abierta de quien
    # lo pidió (ADR 0013, enmienda; F-B3): puede pedir otra tarea sin tocarlo. La
    # solicitud sigue `active`: quien confirma la convierte o la cancela así.
    cur.execute(
        "update task_intake_request set enviada_en = %s where id = %s",
        (now, request_id))
    text = _decir_envio(cur, request, authority["aprobador_nombre"])
    _enqueue(cur, request, text, now, f"intake:{request_id}:sent:v{version}")
    return IntakeOutcome(request_id, text, changed=True,
                         pending_action_id=pending.id)


def _offer_current_review(cur, who: Solicitante, request_id: str,
                          now: datetime) -> IntakeOutcome:
    """El resumen que quien pidió tenía delante quedó atrás del borrador: la respuesta
    a su toque es el resumen vigente, con sus botones (ADR 0013 reglas 2 y 3: un solo
    mensaje con el estado real y una opción posible; nunca una persona sin botón). Se
    arma como toda vuelta al resumen (`_finalize`: sube la versión de la solicitud y
    rehace el resumen desde sus datos), y no se le manda nada a quien confirma."""
    cur.execute(
        """update task_intake_request
              set version = version + 1, actualizado_en = %s
            where id = %s returning *""", (now, request_id))
    outcome = _finalize(cur, cur.fetchone(), who, now)
    if outcome.pending_action_id is not None:
        # El aviso encabeza el mismo mensaje: una sola respuesta. Si con él no cabe
        # en un mensaje, el resumen sale solo.
        cur.execute(
            "select id, cuerpo from message_outbox where pending_action_id = %s",
            (outcome.pending_action_id,))
        row = cur.fetchone()
        if row is None:
            # El resumen vigente quedó registrado pero su mensaje no: quien tocó no
            # puede quedarse sin respuesta ni recibir un error. Un incidente, y el
            # aviso neutro como la única respuesta a su toque.
            return _resumen_vigente_sin_fila(cur, who, request_id, outcome, now)
        text = f"{DRAFT_CHANGED_REVIEW_AGAIN}\n\n{row['cuerpo']}"
        try:
            prepare_payload(text, dedupe_key="intake-review-changed",
                            has_buttons=True)
        except PayloadValidationError:
            return outcome
        cur.execute("update message_outbox set cuerpo = %s where id = %s",
                    (text, row["id"]))
    return outcome


def _resumen_vigente_sin_fila(cur, who: Solicitante, request_id: str,
                              outcome: IntakeOutcome, now: datetime) -> IntakeOutcome:
    request = _request(cur, request_id)
    registrar_incidente(
        cur, who.workspace_id,
        "El resumen vigente de un borrador se registró pero su mensaje no quedó "
        "encolado; quien tocó Enviar a aprobación recibió el aviso neutro.",
        severidad="alta", etapa=ETAPA_RESUMEN_VIGENTE_SIN_FILA,
        referencia_tipo=REFERENCIA_PENDING_ACTION,
        referencia_id=outcome.pending_action_id, chat_id=request["chat_id"],
        app_user_id=who.app_user_id, notificado_en=now)
    _enqueue(cur, request, NOTICIA_NEUTRA_INCIDENTE, now,
             f"intake:{request_id}:review-missing:v{request['version']}")
    return IntakeOutcome(request_id, NOTICIA_NEUTRA_INCIDENTE, inert=True,
                         responded=True)


def modify_text_prompt(field: str, current: str) -> str:
    """La pregunta de un dato de texto que se corrige: lo que la persona tenía,
    al final del mensaje, en el bloque que se copia con un toque. Sin nada que
    copiar (una descripción vacía), la pregunta de siempre del campo."""
    if not current:
        return _free_text_prompt(field)
    return (f"Esto tenías en {FREE_TEXT_NAMES[field]}. Tocalo para copiarlo, "
            f"corregilo y mandámelo: cambio "
            f"sólo eso.\n\n{current}")


def format_due_date(value) -> str:
    """La fecha objetivo como la lee una persona: DD/MM/AAAA. El dato se guarda
    como fecha ISO (ya resuelta en la zona horaria del espacio, sin hora: no hay
    nada que convertir); lo que se muestra y se pega de vuelta pasa por la
    resolución de fechas de siempre. Lo que no es una fecha ISO se deja tal cual;
    una fecha vacía es vacía, nunca la palabra "None"."""
    if value is None or not str(value).strip():
        return ""
    try:
        return date.fromisoformat(value).strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return str(value)


def text_to_copy(cur, request_id: str, field: str, *,
                 confirmed_only: bool = False) -> str:
    """Lo que la persona tenía en un dato de texto, como se le muestra y se
    copia. Un campo sin fila es un campo vacío: nada que copiar; con
    `confirmed_only`, tampoco lo que todavía no confirmó (una propuesta)."""
    cur.execute(
        "select estado, valor from task_intake_field "
        "where request_id = %s and campo = %s", (request_id, field))
    row = cur.fetchone()
    if row and confirmed_only and row["estado"] != "confirmed":
        row = None
    current = normalize_text(_text_or_none(row["valor"] if row else None) or "")
    return format_due_date(current) if field == "due_date" and current else current


def _ask_field_change(cur, request, who, field, now):
    """Lo que sigue a elegir un dato en el selector de Modificar. Uno de texto
    abre su campo para que el mensaje siguiente lo reemplace (con su validación de
    siempre), mostrando lo que tenía; uno que se elige con botones vuelve a
    mostrar sus opciones. Cambia sólo ese dato: lo demás queda como estaba."""
    if field in CHOICE_FIELDS:
        return _open_entity_page(cur, request, who, field, None, 0, now)
    current = text_to_copy(cur, str(request["id"]), field)
    return _open_free_text(cur, request, field, modify_text_prompt(field, current),
                           now, block=current or None)


def resolve_typed_choice(cur: psycopg.Cursor, who: Solicitante, *,
                         choice_set_id: str, valor: dict | None, chat_id: int,
                         now: datetime, source_inbound_id: str | None = None,
                         source_raw_text: str = "") -> IntakeOutcome | None:
    """Resuelve la elección abierta con lo que la persona escribió (ADR 0014,
    M1). El modelo interpreta el mensaje y dice qué opción eligió por su
    identificador ("1", "2", ... en el orden en que se mostraron, o "ninguna");
    acá el código sólo valida que sea una de las ofrecidas y sigue como el
    toque (`resolve_choice`). Ya no se compara texto con etiquetas: eso queda
    sólo para el toque de un botón.

    - Una opción que no se ofreció, o que falta: la misma elección sigue abierta
      con sus botones y se dice por qué (`_rechazar_valor`).
    - "Ninguna" con un texto que nombra algo (objetivo, persona, área): se busca
      entre los de la base, como siempre (etapa 3 del flujo, todavía sin Jev:
      PENDIENTE). Sin texto, es "Otra opción" si la elección la tiene.
    - `None` si no se pudo resolver sin decir nada (la elección ya no está
      abierta, o "ninguna" sin otra opción): quien llama repite la pregunta."""
    cur.execute(
        """select c.token, c.etiqueta, c.accion, s.campo, s.request_id
             from task_intake_choice c
             join task_intake_choice_set s on s.id = c.choice_set_id
             join task_intake_request r on r.id = s.request_id
            where s.id = %s and s.workspace_id = %s and r.membership_id = %s
              and s.estado = 'active' and r.estado = 'active' and c.activa
            order by c.orden""",
        (choice_set_id, who.workspace_id, who.membership_id),
    )
    filas = cur.fetchall()
    if not filas:
        return None
    campo = filas[0]["campo"]
    request = _request(cur, str(filas[0]["request_id"]))
    opciones = opciones_numeradas(etiqueta_sin_icono(f["etiqueta"]) for f in filas)
    elegida = validar_valor(valor, ValorEsperado(TipoValor.OPCION, opciones),
                            limite_texto=0)
    if isinstance(elegida, Rechazado):
        return _rechazar_valor(cur, request, who, campo, elegida,
                               source_inbound_id, now,
                               choice_set_id=choice_set_id)
    fila = None if elegida.valor == OPCION_NINGUNA else filas[int(elegida.valor) - 1]
    texto = normalize_text((valor or {}).get("texto") or "")
    if campo in CHOICE_FIELDS and texto and (fila is None or fila["accion"] == "other"):
        if telegram_text_length(texto) > USER_FIELD_LIMITS[campo]:
            return _rechazar_valor(
                cur, request, who, campo,
                Rechazado(MotivoRechazo.TEXTO_LARGO, "", ""), source_inbound_id,
                now, choice_set_id=choice_set_id)
        return _resolver_entidad_escrita(
            cur, who, choice_set_id=choice_set_id, campo=campo, texto=texto,
            inbound_id=source_inbound_id, raw=source_raw_text, now=now)
    if fila is None:
        fila = next((f for f in filas if f["accion"] == "other"), None)
    if fila is None:
        return None
    return resolve_choice(cur, who, token=fila["token"], chat_id=chat_id, now=now)


def _resolver_entidad_escrita(cur, who, *, choice_set_id, campo, texto, inbound_id,
                              raw, now) -> IntakeOutcome | None:
    """La persona escribió algo que no es una de las opciones ofrecidas: cierra
    la elección y busca lo escrito entre las opciones de la base (objetivos,
    personas, áreas), como el campo de "Otra opción"."""
    cur.execute(
        """update task_intake_choice_set set estado = 'consumed'
            where id = %s and estado = 'active' returning request_id""",
        (choice_set_id,))
    fila = cur.fetchone()
    if not fila:
        return None
    _cerrar_botones_de(cur, choice_set_id, None)
    cur.execute(
        """update task_intake_request set version = version + 1, actualizado_en = %s
            where id = %s returning *""", (now, fila["request_id"]))
    outcome = _resolve_user_entity(cur, cur.fetchone(), who, campo, texto,
                                   inbound_id, raw, now)
    cur.execute("update task_intake_choice_set set resultado = %s where id = %s",
                (Jsonb(outcome.as_json()), choice_set_id))
    return outcome


def _cerrar_botones_de(cur, choice_set_id, elegida) -> None:
    """Una elección que se consumió: su pregunta deja de enviarse y sus botones
    dejan de valer (`elegida` es el que se tocó, si alguno)."""
    cur.execute(
        """update message_outbox set estado = 'descartado'
            where intake_choice_set_id = %s
              and estado in ('pendiente', 'esperando_confirmacion', 'listo')""",
        (choice_set_id,),
    )
    cur.execute(
        """update task_intake_choice
              set activa = false,
                  elegida = (%s::uuid is not null and id = %s::uuid)
            where choice_set_id = %s""",
        (elegida, elegida, choice_set_id),
    )


def _first_choice_prompt(cur: psycopg.Cursor, choice_set_id) -> str:
    """El cuerpo con que se hizo la pregunta de una elección: su primer mensaje
    en `message_outbox` (los reenvíos llevan el mismo `intake_choice_set_id`,
    a veces con un prefijo), o el genérico si no hay ninguno."""
    cur.execute(
        """select cuerpo from message_outbox where intake_choice_set_id = %s
            order by programado_para, id limit 1""",
        (choice_set_id,),
    )
    row = cur.fetchone()
    return row["cuerpo"] if row else CHOICE_FALLBACK_PROMPT


def resend_choice_prompt(cur: psycopg.Cursor, who: Solicitante,
                         choice_set_id: str, now: datetime,
                         ref: str | None = None, prefix: str = "",
                         texto: str | None = None) -> bool:
    """Vuelve a mandar la pregunta de la elección abierta con sus botones
    (`prefix`, si viene, va delante en el mismo mensaje). `False` si la
    elección ya no estaba abierta: no manda nada. `ref` distingue este
    reenvío de otros (el mensaje que lo causó) y, si viene, siempre gana (T9-R4b).
    Sin él, con un turno atado a un evento (`db.atar_al_entrante`: un mensaje o un
    toque), la referencia es ese evento (T9-R4): una entrega repetida del mismo
    evento no reenvía dos veces, y un evento nuevo sí. Sin ninguno de los dos, es
    el número de mensajes que la elección ya tiene (`n1`, `n2`, ...): cada
    reenvío es un mensaje propio y ninguno depende del reloj. `texto`, si viene,
    es el mensaje entero (lo redactó el modelo con A): reemplaza a `prefix` y a la
    pregunta guardada."""
    request = _request_of_question(cur, who, QUESTION_CHOICE, choice_set_id,
                                   lock=False)
    if not request:
        return False
    prompt = _first_choice_prompt(cur, choice_set_id)
    ref = ref or entrante_atado(cur)
    if ref is None:
        cur.execute(
            """select count(*) n from message_outbox
                where intake_choice_set_id = %s""", (choice_set_id,))
        ref = f"n{cur.fetchone()['n']}"
    _enqueue(cur, request, f"{prefix}{prompt}" if texto is None else texto, now,
             f"intake:{request['id']}:reask:{ref}", choice_set_id=choice_set_id)
    return True


def _reject_user_value(cur, request, field, prompt, inbound_id, now):
    _enqueue(
        cur, request, prompt, now,
        f"intake:{request['id']}:validation:{field}:{inbound_id}",
    )
    return IntakeOutcome(str(request["id"]), prompt, inert=True)


def _resolve_user_entity(cur, request, who, field, value, inbound_id, raw, now):
    candidates, has_more = _entity_candidates(cur, request, who, field, value)
    if not _candidates_deliverable(field, candidates):
        return _configuration_error(cur, request, who, field, now)
    if len(candidates) == 1 and not has_more:
        _confirm_user_value(cur, str(request["id"]), field, candidates[0][2],
                            inbound_id, raw, now)
        return _advance(cur, request, who, now)
    return _open_entity_page(cur, request, who, field, value, 0, now)


def _confirm_user_value(cur, request_id, field, value, inbound_id, raw, now):
    cur.execute(
        """update task_intake_field
              set estado = 'confirmed', valor = %s, proposed_by = 'user',
                  source_inbound_id = %s, source_raw_text = %s,
                  source_choice_id = null, version = version + 1,
                  actualizado_en = %s
            where request_id = %s and campo = %s""",
        (Jsonb(value), inbound_id, raw, now, request_id, field),
    )


def _candidates_deliverable(field, candidates) -> bool:
    for label, _, stored in candidates:
        if telegram_text_length(normalize_text(label)) > CONFIG_LABEL_LIMIT:
            return False
        if field == "objective" and not _config_text(stored.get("title")):
            return False
        if field == "responsible" and not _config_text(stored.get("name")):
            return False
        if field == "area" and (
                not _config_text(stored.get("name"))
                or not _config_text(stored.get("slug"))):
            return False
    return True


def _config_text(value) -> bool:
    raw = str(value or "")
    normalized = normalize_text(raw)
    return bool(normalized and normalized == raw
                and telegram_text_length(normalized) <= CONFIG_LABEL_LIMIT)


def _evidence_deliverable(items) -> bool:
    values = list(items or [])
    if len(values) > EVIDENCE_COUNT_LIMIT:
        return False
    total = 0
    for item in values:
        raw = str(item)
        normalized = normalize_text(raw)
        units = telegram_text_length(normalized)
        if not normalized or normalized != raw or units > EVIDENCE_ITEM_LIMIT:
            return False
        total += units
    return total <= EVIDENCE_TOTAL_LIMIT


def _configuration_error(cur, request, who, field, now):
    request_id = str(request["id"])
    registrar_incidente(
        cur, who.workspace_id,
        "Una opción configurada del intake excede el contrato visible.",
        etapa=ETAPA_CONFIGURACION_ALTA, app_user_id=who.app_user_id)
    registrar_auditoria(
        cur, accion="configuracion_intake_invalida",
        workspace_id=who.workspace_id,
        actor_app_user_id=who.app_user_id, actor_kind="prisma",
        sujeto_tipo="task_draft", sujeto_id=str(request["task_draft_id"]),
        detalle={"request_id": request_id, "field": field},
    )
    return _open_choices(
        cur, request, None, CONFIG_ERROR,
        [(CANCELAR_BORRADOR, "cancel", None)], now, kind="config_error",
    )


def _advance(cur, request, who, now, *, prefijo: str = "",
             rechazo: Rechazo | None = None,
             campo_del_rechazo: str | None = None) -> IntakeOutcome:
    """Sigue con el próximo dato que falta, en el orden de `FIELDS`. `prefijo`
    (lo que se dice antes de la pregunta, en el mismo mensaje) sólo va delante
    de la primera pregunta que se abre. `rechazo`, si viene, es por qué lo que la
    persona dijo no sirvió y se le propone un valor: va delante de la propuesta de
    `campo_del_rechazo` y de ninguna otra (el aviso es de ese dato)."""
    request_id = str(request["id"])
    cur.execute(
        """select campo, estado, valor from task_intake_field
            where request_id = %s order by array_position(%s::text[], campo)""",
        (request_id, list(FIELDS)),
    )
    fields = {row["campo"]: row for row in cur.fetchall()}
    for field in FIELDS:
        row = fields[field]
        if row["estado"] == "confirmed":
            continue
        if field == "title" and row["estado"] == "proposed":
            # La tarea que ya trajo el mensaje se toma como título y se sigue con
            # el objetivo: no se la vuelve a preguntar (decisión del usuario,
            # 2026-09-30). Igual se revisa entera en el resumen final.
            cur.execute(
                """update task_intake_field
                      set estado = 'confirmed', version = version + 1,
                          actualizado_en = %s
                    where request_id = %s and campo = 'title'""",
                (now, request_id),
            )
            continue
        if field == "description" and row["estado"] == "missing":
            cur.execute(
                """update task_intake_field
                      set estado = 'confirmed', valor = %s, proposed_by = 'server',
                          version = version + 1, actualizado_en = %s
                    where request_id = %s and campo = 'description'""",
                (Jsonb(""), now, request_id),
            )
            continue
        if field in {"title", "description", "due_date", "acceptance_criterion"}:
            if row["estado"] == "proposed":
                prompt = _proposal_prompt(field, row["valor"])
                pregunta = None
                del_campo = rechazo if field == campo_del_rechazo else None
                if del_campo is not None:
                    pregunta = prompt
                    prompt = f"{del_campo.razon} {del_campo.se_acepta}\n\n{prompt}"
                return _open_choices(
                    cur, request, field, prompt,
                    [(CONFIRM, "confirm", None), (REJECT, "reject", None),
                     (OTHER, "other", None)], now, prefijo=prefijo,
                    pregunta=pregunta, rechazo=del_campo,
                    propuesto=_mostrar_valor(field, row["valor"]),
                )
            return _open_free_text(cur, request, field, _free_text_prompt(field),
                                   now, prefijo=prefijo)
        if field == "evidence":
            problema = _completar_evidencia(cur, request, who, now)
            if problema is not None:
                return problema
            continue
        unica = _unica_opcion(cur, request, who, field)
        if unica is not None:
            # Una sola opción posible: no se pregunta. Se completa sola y queda a
            # la vista en el resumen (decisión del usuario, 2026-09-30).
            cur.execute(
                """update task_intake_field
                      set estado = 'confirmed', valor = %s, proposed_by = 'server',
                          source_choice_id = null, version = version + 1,
                          actualizado_en = %s
                    where request_id = %s and campo = %s""",
                (Jsonb(unica), now, request_id, field),
            )
            continue
        return _open_entity_page(
            cur, request, who, field,
            row["valor"] if row["estado"] == "proposed" else None, 0, now,
            prefijo=prefijo,
        )
    return _finalize(cur, request, who, now)


def _completar_evidencia(cur, request, who, now) -> IntakeOutcome | None:
    """La evidencia que exige la política del área ya confirmada del borrador: la
    pone el servidor, nunca la persona. `None` si quedó completa; si no, el estado
    real que lo impide (sin política, o una política que no se puede mostrar), ya
    dicho a quien actuó."""
    request_id = str(request["id"])
    cur.execute(
        """select valor from task_intake_field
            where request_id = %s and campo = 'area'
              and estado = 'confirmed'""",
        (request_id,),
    )
    area = cur.fetchone()
    cur.execute(
        """select evidencia_requerida, version
             from task_evidence_policy
            where workspace_id = %s and area_id = %s""",
        (who.workspace_id, area["valor"]["id"]),
    )
    policy = cur.fetchone()
    if not policy:
        return _say_real_state(cur, request, NO_EVIDENCE_POLICY, now,
                               "no-evidence-policy")
    if not _evidence_deliverable(policy["evidencia_requerida"]):
        return _configuration_error(cur, request, who, "evidence", now)
    cur.execute(
        """update task_intake_field
              set estado = 'confirmed', valor = %s,
                  proposed_by = 'server', version = version + 1,
                  actualizado_en = %s
            where request_id = %s and campo = 'evidence'""",
        (Jsonb({"items": list(policy["evidencia_requerida"]),
                "version": policy["version"]}), now, request_id),
    )
    return None


# Los objetivos que se ofrecen a quien pide (F-B11): los de su área. Una persona
# no pide tareas de otro sector; lo que cruza áreas va por una dependencia de una
# tarea propia. Sólo si el área no tiene ningún objetivo propio se ofrecen los que
# no son de ningún área: el estratégico y los datos anteriores a la migración 0027.
# Los de otra área no se ofrecen nunca. Los parámetros son (espacio, área, espacio,
# área), en ese orden.
_OBJETIVOS_DEL_AREA = """
      o.workspace_id = %s and o.estado in ('activo', 'propuesto')
      and (o.area_id = %s
           or (o.area_id is null and not exists (
                 select 1 from objective p
                  where p.workspace_id = o.workspace_id and p.area_id = %s
                    and p.estado in ('activo', 'propuesto'))))"""


def _objetivos_del_area(cur, who, *, filtro: str = "", params=(), offset=0):
    cur.execute(
        f"""select o.id, o.titulo, o.estado from objective o
             where {_OBJETIVOS_DEL_AREA}{filtro}
             order by o.titulo, o.id limit %s offset %s""",
        (who.workspace_id, who.area_id, who.area_id, *params,
         CANDIDATE_PAGE_SIZE + 1, offset))
    return cur.fetchall()


def _entity_candidates(cur, request, who, field, query, offset=0):
    query_text = normalize_text(str(query or "")).casefold()
    if field == "objective":
        if query_text:
            rows = _objetivos_del_area(
                cur, who, filtro=" and lower(o.titulo) = lower(%s)",
                params=(normalize_text(str(query)),), offset=offset)
            if not rows:
                rows = _objetivos_del_area(
                    cur, who, filtro=" and position(lower(%s) in lower(o.titulo)) > 0",
                    params=(normalize_text(str(query)),), offset=offset)
        else:
            rows = _objetivos_del_area(cur, who, offset=offset)
        has_more = len(rows) > CANDIDATE_PAGE_SIZE
        chosen = rows[:CANDIDATE_PAGE_SIZE]
        return [(r["titulo"], str(r["id"]),
                  {"id": str(r["id"]), "title": r["titulo"], "state": r["estado"]})
                 for r in chosen], has_more
    if field == "responsible":
        query_filter = ""
        params: list[Any] = [who.membership_id, who.membership_id]
        if query_text:
            query_filter = (
                " and (i.membership_id = %s "
                "or position(lower(%s) in lower(i.nombre)) > 0)"
            )
            params.extend([who.membership_id, normalize_text(str(query))])
        params.extend([who.membership_id, CANDIDATE_PAGE_SIZE + 1, offset])
        cur.execute(
            f"""select i.membership_id, i.nombre, i.area_id
                  from integrante i
                 where i.activo and (i.membership_id = %s
                    or i.aprobador_membership_id = %s){query_filter}
                 order by (i.membership_id = %s) desc, i.nombre, i.membership_id
                 limit %s offset %s""",
            params,
        )
        rows = cur.fetchall()
        selected = []
        for row in rows[:CANDIDATE_PAGE_SIZE]:
            is_self = str(row["membership_id"]) == str(who.membership_id)
            label = "Para mí" if is_self else row["nombre"]
            selected.append((label, str(row["membership_id"]), {
                "id": str(row["membership_id"]), "name": row["nombre"],
                "area_id": str(row["area_id"]),
            }))
        return selected, len(rows) > CANDIDATE_PAGE_SIZE
    if field == "area":
        cur.execute(
            """select valor from task_intake_field
                where request_id = %s and campo = 'responsible'
                  and estado = 'confirmed'""",
            (request["id"],),
        )
        responsible = cur.fetchone()
        if not responsible:
            return []
        cur.execute(
            """select a.id, a.slug, a.nombre
                 from area a join membership m on m.area_id = a.id
                where m.id = %s""",
            (responsible["valor"]["id"],),
        )
        rows = cur.fetchall()
        candidates = [(r["nombre"], str(r["id"]),
                       {"id": str(r["id"]), "slug": r["slug"], "name": r["nombre"]})
                      for r in rows if not query_text
                      or query_text in normalize_text(r["nombre"]).casefold()
                      or query_text in normalize_text(r["slug"]).casefold()]
        return candidates[offset:offset + CANDIDATE_PAGE_SIZE], False
    return [], False


def _open_entity_page(cur, request, who, field, query, offset, now, *,
                      prefijo: str = ""):
    candidates, has_more = _entity_candidates(
        cur, request, who, field, query, offset=offset)
    no_match = bool(normalize_text(str(query or ""))) and not candidates
    buscado = normalize_text(str(query or ""))
    if no_match:
        query = None
        offset = 0
        candidates, has_more = _entity_candidates(
            cur, request, who, field, None, offset=0)
    if not _candidates_deliverable(field, candidates):
        return _configuration_error(cur, request, who, field, now)
    recomendada = False
    if field == "objective" and not query and offset == 0 and len(candidates) > 1:
        candidates, recomendada = _ordenar_objetivos(cur, request, who, candidates)
    if not candidates:
        return _open_choices(
            cur, request, field, NO_CANDIDATES,
            [(CANCELAR_BORRADOR, "cancel", None)], now,
            kind=f"no_candidates_{field}",
        )
    # Cada candidata es un botón que representa algo que va a quedar dentro
    # de la tarea en curso (objetivo, responsable, área) -- mismo ícono que
    # cualquier otro botón de tarea (íconos, decisión del usuario,
    # 2026-09-28), armado con `salida.etiquetas_de_tarea` -- la receta única
    # (R2-002/R3-003, revisión 2026-09-28+1): antes esta etiqueta se
    # iconizaba sin descontarle el costo del ícono al presupuesto, así que
    # una candidata (un objetivo, una persona) con un nombre cerca del límite
    # podía superarlo y romper la validación del botón.
    etiquetas = etiquetas_de_tarea([label for label, _, _ in candidates])
    if recomendada:
        etiquetas[0] = con_icono(etiqueta_sin_icono(etiquetas[0]), ICONO_RECOMENDADA)
    options = [(etiqueta, "select", stored)
              for etiqueta, (_, _, stored) in zip(etiquetas, candidates)]
    if has_more:
        options.append((VER_MAS, "more", {
            "field": field, "query": query,
            "offset": offset + CANDIDATE_PAGE_SIZE,
        }))
    if _hay_otra_opcion(cur, request, who, field, candidates, offset, has_more):
        options.append((OTHER, "other", None))
    rechazo = busqueda = None
    if no_match:
        prompt = (f"No encontré nada parecido a «{buscado}». Estas son las "
                  "opciones que hay.")
        rechazo = Rechazo(f"No encontré nada parecido a «{buscado}».",
                          "Estas son las opciones que hay.")
    else:
        prompt = (_candidate_prompt(field) if not query else
                  f"Para «{query}» encontré estas opciones. {_candidate_prompt(field)}")
        if recomendada:
            prompt = f"{prompt} {MARCA_RECOMENDADA}"
        busqueda = str(query) if query else None
    pregunta = _candidate_prompt(field)
    if recomendada:
        pregunta = f"{pregunta} {MARCA_RECOMENDADA}"
    return _open_choices(cur, request, field, prompt, options, now,
                         prefijo=prefijo, pregunta=pregunta,
                         rechazo=rechazo, busqueda=busqueda)


# El aviso del objetivo que Jev eligió sin duda: va en la misma pregunta.
MARCA_RECOMENDADA = f"Con {ICONO_RECOMENDADA} marqué el que más se parece a la tarea."
# Una falta de credencial se registra una vez por espacio y proceso (es un dato de
# configuración, no una falla por pregunta); una falla de Jev, cada vez que ocurre.
_SIN_ORDENAR_AVISADO: set[str] = set()


def _ordenar_objetivos(cur, request, who, candidates):
    """Los objetivos candidatos con el más probable primero (F-B10, etapa 3 del ADR
    0014): Jev decide entre los candidatos que salieron de la base según el título
    de la tarea. Devuelve `(candidatos, destacado)`; `destacado` sólo es verdadero
    con una decisión clara, y entonces el primero lleva la estrella. Con duda, sin
    Jev o con una falla, quedan en el orden de siempre y se registra (nunca en
    silencio)."""
    from . import jev as jev_modulo
    from .config import config
    from .contexto import vocabulario

    workspace_id = str(who.workspace_id)
    cur.execute(
        """select valor from task_intake_field
            where request_id = %s and campo = 'title'""", (request["id"],))
    fila = cur.fetchone()
    titulo = normalize_text(str(fila["valor"] or "")) if fila else ""
    if not titulo:
        return candidates, False
    cliente = jev_modulo.desde_base(config.openrouter_api_key)
    if cliente is None:
        if workspace_id not in _SIN_ORDENAR_AVISADO:
            _SIN_ORDENAR_AVISADO.add(workspace_id)
            registrar_incidente(
                cur, workspace_id,
                "Falta la credencial de Jev (PRISMA_OPENROUTER_API_KEY): los "
                "objetivos se ofrecen en el orden de siempre, sin destacar el más "
                "probable.", severidad="baja", etapa=ETAPA_OBJETIVO_SIN_ORDENAR,
                app_user_id=who.app_user_id, avisar_admin=False)
        return candidates, False
    try:
        orden = jev_modulo.ordenar_objetivos(
            cliente, titulo=titulo,
            objetivos=[(ident, label) for label, ident, _ in candidates],
            vocabulario=vocabulario(cur, workspace_id))
    except psycopg.Error:
        raise                       # la transacción no sigue: no es de Jev
    except Exception as exc:        # Jev caído o con una respuesta sin forma
        registrar_incidente(
            cur, workspace_id,
            "Jev no pudo ordenar los objetivos por la tarea: se ofrecen en el orden "
            "de siempre, sin destacar el más probable.", severidad="baja",
            referencia_cruda=type(exc).__name__, etapa=ETAPA_OBJETIVO_SIN_ORDENAR,
            app_user_id=who.app_user_id, avisar_admin=False)
        return candidates, False
    por_id = {ident: (label, ident, stored) for label, ident, stored in candidates}
    return [por_id[ident] for ident in orden.ids], orden.clara


def _hay_otra_opcion(cur, request, who, field, mostradas, offset, has_more) -> bool:
    """Si hay otra opción posible además de las que están en pantalla (regla 3 del
    ADR 0013: sólo opciones posibles). "Otra opción" abre la búsqueda por nombre
    entre las opciones de la base, así que sin opciones fuera de la pantalla no
    hay nada que buscar."""
    if has_more or offset:
        return True
    todas, hay_mas = _entity_candidates(cur, request, who, field, None)
    ids = {candidata[1] for candidata in mostradas}
    return hay_mas or any(candidata[1] not in ids for candidata in todas)


def _unica_opcion(cur, request, who, field):
    """El valor guardado de la única opción posible de un dato (objetivo,
    responsable o área), o `None` si hay más de una, ninguna o no se puede
    mostrar. Un dato con una sola opción no se pregunta: se completa solo."""
    encontradas = _entity_candidates(cur, request, who, field, None)
    if not isinstance(encontradas, tuple):
        return None
    candidatas, hay_mas = encontradas
    if hay_mas or len(candidatas) != 1 or not _candidates_deliverable(
            field, candidatas):
        return None
    return candidatas[0][2]


def _open_choices(cur, request, field, prompt, options, now, kind=None, *,
                  prefijo: str = "", pregunta: str | None = None,
                  rechazo: Rechazo | None = None, busqueda: str | None = None,
                  propuesto: str | None = None):
    request_id = str(request["id"])
    kind = kind or field or "choice"
    if field is not None and not kind.startswith("no_candidates"):
        # La pregunta de un dato sale por la redacción del espacio (ADR 0014,
        # etapa 6); el aviso que va delante no es la pregunta. Sin opciones que
        # ofrecer no hay nada que redactar: es un estado, no una pregunta.
        prompt = prefijo + _decir_pregunta(
            cur, request, field, TipoValor.OPCION, prompt, now, pregunta=pregunta,
            opciones=[label for label, _, _ in options], rechazo=rechazo,
            busqueda=busqueda, propuesto=propuesto)
    elif field is not None:
        prompt = prefijo + prompt
    else:
        prompt = prefijo + prompt
    prepare_payload(prompt, dedupe_key="intake-choice", has_buttons=True)
    prepare_buttons([(label, "i:placeholder") for label, _, _ in options])
    _invalidate_open_inputs(cur, request_id)
    cur.execute(
        """insert into task_intake_choice_set
             (workspace_id, request_id, campo, request_version, tipo)
           values (%s, %s, %s, %s, %s) returning id""",
        (request["workspace_id"], request_id, field, request["version"], kind),
    )
    choice_set_id = str(cur.fetchone()["id"])
    for order, (label, action, value) in enumerate(options):
        cur.execute(
            """insert into task_intake_choice
                 (workspace_id, choice_set_id, token, etiqueta, accion, valor, orden)
               values (%s, %s, %s, %s, %s, %s, %s)""",
            (request["workspace_id"], choice_set_id, secrets.token_urlsafe(12),
             label, action, Jsonb(value), order),
        )
    _enqueue(
        cur, request, prompt, now,
        f"intake:{request_id}:v{request['version']}:choice:{kind}:{field or 'none'}",
        choice_set_id=choice_set_id,
    )
    return IntakeOutcome(request_id, prompt, changed=True)


def _open_free_text(cur, request, field, prompt, now, replace=False, block=None,
                    *, prefijo: str = ""):
    request_id = str(request["id"])
    # Con un bloque copiable (Modificar) el texto tiene que terminar en él: no se
    # redacta.
    prompt = prefijo + (prompt if block else _decir_pregunta(
        cur, request, field, TIPO_DE_CAMPO.get(field, TipoValor.TEXTO), prompt,
        now))
    prepare_payload(prompt, dedupe_key="intake-text", has_buttons=bool(block))
    cur.execute(
        """update task_intake_free_text_slot set estado = 'invalidated'
            where request_id = %s and estado = 'active'""",
        (request_id,),
    )
    cur.execute(
        """insert into task_intake_free_text_slot
             (workspace_id, request_id, campo, request_version)
           values (%s, %s, %s, %s)""",
        (request["workspace_id"], request_id, field, request["version"]),
    )
    _enqueue(
        cur, request, prompt, now,
        f"intake:{request_id}:v{request['version']}:text:{field}", block=block,
    )
    return IntakeOutcome(request_id, prompt, changed=not replace)


def _invalidate_open_inputs(cur, request_id):
    cur.execute(
        """update message_outbox set estado = 'descartado'
            where estado in ('pendiente', 'esperando_confirmacion', 'listo')
              and (intake_choice_set_id in (
                    select id from task_intake_choice_set
                     where request_id = %s and estado = 'active')
                   or pending_action_id in (
                    select p.id from pending_action p
                     join task_intake_request r on r.task_draft_id = p.draft_id
                    where r.id = %s and p.estado = 'esperando'))""",
        (request_id, request_id),
    )
    cur.execute(
        """update task_intake_choice_set set estado = 'invalidated'
            where request_id = %s and estado = 'active'""",
        (request_id,),
    )
    cur.execute(
        """update task_intake_choice set activa = false
            where choice_set_id in (
              select id from task_intake_choice_set
               where request_id = %s and estado <> 'active')""",
        (request_id,),
    )
    cur.execute(
        """update task_intake_free_text_slot set estado = 'invalidated'
            where request_id = %s and estado = 'active'""",
        (request_id,),
    )
    cur.execute(
        """update pending_action set estado = 'cancelada',
                  resuelta_en = clock_timestamp()
            where draft_id = (select task_draft_id from task_intake_request
                                where id = %s)
              and estado = 'esperando'""",
        (request_id,),
    )
    cur.execute(
        """update pending_action_option set activa = false
            where pending_action_id in (
              select p.id from pending_action p
               join task_intake_request r on r.task_draft_id = p.draft_id
              where r.id = %s and p.estado = 'cancelada')""",
        (request_id,),
    )


def _finalize(cur, request, who, now, apertura: str | None = None):
    """Arma el resumen del borrador completo y se lo ofrece a quien confirma. Con
    `apertura` (el alta conducida: la frase con que el modelo ya contestó el turno)
    el resumen sale con esa frase delante y sin otra llamada al modelo; los datos y el
    cierre que nombra el botón siguen siendo del código."""
    request_id = str(request["id"])
    cur.execute(
        "select campo, valor from task_intake_field where request_id = %s",
        (request_id,),
    )
    values = {row["campo"]: row["valor"] for row in cur.fetchall()}
    for field in ("title", "description", "due_date", "acceptance_criterion"):
        if telegram_text_length(str(values[field])) > USER_FIELD_LIMITS[field]:
            cur.execute(
                """update task_intake_field
                      set estado = 'missing', valor = null, proposed_by = null,
                          source_inbound_id = null, source_raw_text = null,
                          source_choice_id = null, version = version + 1
                    where request_id = %s and campo = %s""",
                (request_id, field),
            )
            return _open_free_text(
                cur, request, field, _user_limit_prompt(field), now,
            )
    objective = values["objective"]
    responsible = values["responsible"]
    area = values["area"]
    cur.execute(
        """select id, titulo, estado from objective
            where id = %s and workspace_id = %s
              and estado in ('activo', 'propuesto')""",
        (objective["id"], who.workspace_id),
    )
    current_objective = cur.fetchone()
    cur.execute(
        """select i.membership_id id, i.nombre, i.area_id, i.activo,
                  i.aprobador_membership_id
             from integrante i where i.membership_id = %s""",
        (responsible["id"],),
    )
    current_responsible = cur.fetchone()
    cur.execute(
        "select id, slug, nombre from area where id = %s and workspace_id = %s",
        (area["id"], who.workspace_id),
    )
    current_area = cur.fetchone()
    if not current_objective or not current_responsible or not current_responsible["activo"] \
       or not current_area:
        return _say_real_state(cur, request, CONFIRMED_OPTION_STALE, now,
                               "stale-option")
    objective = {"id": str(current_objective["id"]),
                 "title": current_objective["titulo"],
                 "state": current_objective["estado"]}
    responsible = {"id": str(current_responsible["id"]),
                   "name": current_responsible["nombre"],
                   "area_id": str(current_responsible["area_id"])}
    area = {"id": str(current_area["id"]), "slug": current_area["slug"],
            "name": current_area["nombre"]}
    current_candidates = [
        (objective["title"], objective["id"], objective),
        (responsible["name"], responsible["id"], responsible),
        (area["name"], area["id"], area),
    ]
    for field, candidate in zip(("objective", "responsible", "area"),
                                current_candidates, strict=True):
        if not _candidates_deliverable(field, [candidate]):
            return _configuration_error(cur, request, who, field, now)
    for field, value in (("objective", objective), ("responsible", responsible),
                         ("area", area)):
        cur.execute(
            """update task_intake_field set valor = %s, actualizado_en = %s
                where request_id = %s and campo = %s and estado = 'confirmed'""",
            (Jsonb(value), now, request_id, field),
        )
    if responsible["area_id"] != area["id"]:
        cur.execute(
            """update task_intake_field set estado = 'missing', valor = null,
                      source_inbound_id = null, source_raw_text = null,
                      source_choice_id = null
                where request_id = %s and campo = 'area'""",
            (request_id,),
        )
        return _advance(cur, request, who, now)
    cur.execute(
        """select evidencia_requerida, version from task_evidence_policy
            where workspace_id = %s and area_id = %s""",
        (who.workspace_id, area["id"]),
    )
    policy = cur.fetchone()
    if not policy:
        return _say_real_state(cur, request, NO_EVIDENCE_POLICY, now,
                               "no-evidence-policy")
    if not _evidence_deliverable(policy["evidencia_requerida"]):
        return _configuration_error(cur, request, who, "evidence", now)
    cur.execute(
        """update task_intake_field set valor = %s, proposed_by = 'server',
                  actualizado_en = %s
            where request_id = %s and campo = 'evidence'
              and estado = 'confirmed'""",
        (Jsonb({"items": list(policy["evidencia_requerida"]),
                "version": policy["version"]}), now, request_id),
    )
    cur.execute("select zona_horaria from workspace where id = %s", (who.workspace_id,))
    zone = ZoneInfo(cur.fetchone()["zona_horaria"])
    due = datetime.combine(date.fromisoformat(values["due_date"]), time(12), zone)
    cur.execute(
        """update task_draft
              set objective_id = %s, objective_snapshot = %s, titulo = %s,
                  descripcion = %s,
                  area_id = %s, responsable_membership_id = %s,
                  fecha_objetivo = %s, criterio_aceptacion = %s,
                  evidencia_requerida = %s, evidencia_policy_version = %s,
                  version = %s, actualizado_en = %s
            where id = %s""",
        (objective["id"], Jsonb({"id": objective["id"], "titulo": objective["title"],
                                 "estado": objective["state"]}),
         values["title"], values["description"], area["id"], responsible["id"], due,
         values["acceptance_criterion"], policy["evidencia_requerida"],
         policy["version"], request["version"], now, request["task_draft_id"]),
    )
    datos = dict(
        title=values["title"], description=values["description"],
        objective=objective["title"], area=area["name"],
        responsible=responsible["name"],
        due_date=format_due_date(values["due_date"]),
        acceptance_criterion=values["acceptance_criterion"],
        evidence=list(policy["evidencia_requerida"]),
        variante=variante_redaccion(cur, str(request["workspace_id"])),
    )
    resumen = render_resumen(**datos, cur=cur,
                             workspace_id=str(request["workspace_id"]),
                             historial=(None if apertura is not None
                                        else _conversacion_de(cur, request, now)),
                             apertura=apertura)
    preview_text = resumen.texto
    # La apertura del alta conducida es la frase con que el modelo le contestó a quien
    # pidió el borrador en SU turno: quien confirma recibe sólo el resumen (el cuerpo
    # de siempre, sin esa frase). El alta guiada no cambia.
    cuerpo_para_quien_confirma = (resumen.cuerpo if apertura is None
                                  else render_resumen(**datos).cuerpo)
    try:
        prepare_payload(preview_text, dedupe_key="intake-preview", has_buttons=True)
    except PayloadValidationError:
        return _configuration_error(cur, request, who, "aggregate", now)

    preview, _ = _current_preview(cur, request["task_draft_id"])
    authority = _find_confirmer(cur, responsible["id"])
    if authority is None:
        return _say_real_state(cur, request, NO_ACTIVE_AUTHORITY, now,
                               "no-active-authority")
    if requiere_aprobacion(authority, request["membership_id"]):
        # Confirma otra persona (T9-R1c-4): quien pidió el borrador lo revisa primero
        # y es él quien lo envía; a quien confirma no le llega nada todavía. Su
        # resumen dice lo que hace su botón, no el de quien confirma (R4c-H9).
        texto_de_revision = resumen.con_cierre(
            cierre_enviar(authority["aprobador_nombre"])).texto
        try:
            prepare_payload(texto_de_revision, dedupe_key="intake-review",
                            has_buttons=True)
        except PayloadValidationError:
            return _configuration_error(cur, request, who, "aggregate", now)
        return _offer_review(cur, request, who, now, texto_de_revision, preview,
                             cuerpo_para_quien_confirma)
    pending, _ = _send_to_confirmer(cur, request, now, preview_text, preview,
                                    request["version"], authority)
    return IntakeOutcome(request_id, preview_text, changed=True,
                         pending_action_id=pending.id)


def _current_preview(cur, draft_id):
    """La vista previa vigente del borrador tal como la revalida la autoridad
    (`confirmar_borrador_tarea`) y su versión."""
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
               'evidencia_policy_version', evidencia_policy_version) preview,
               version
             from task_draft where id = %s""",
        (draft_id,),
    )
    row = cur.fetchone()
    return row["preview"], row["version"]


def _draft_responsible(cur, request):
    cur.execute("select responsable_membership_id from task_draft where id = %s",
                (request["task_draft_id"],))
    return cur.fetchone()["responsable_membership_id"]


def _find_confirmer(cur, responsible_id):
    """Quien confirma el borrador de esa persona responsable (su aprobador o, sin
    uno, la autoridad final) con Telegram, o `None` si no hay a quién mandárselo:
    `{aprobador_membership_id, app_user_id, telegram_user_id, aprobador_nombre}`."""
    cur.execute(
        """select m.aprobador_membership_id, aprobador.app_user_id,
                  aprobador.telegram_user_id, aprobador.nombre aprobador_nombre
             from membership m
             left join integrante aprobador
               on aprobador.membership_id = m.aprobador_membership_id
            where m.id = %s""",
        (responsible_id,),
    )
    authority = cur.fetchone()
    approver_id = authority["aprobador_membership_id"] if authority else None
    if approver_id is None:
        cur.execute(
            """select i.membership_id aprobador_membership_id, i.app_user_id,
                      i.telegram_user_id, i.nombre aprobador_nombre
                 from integrante i join rol r on r.id = i.rol_id
                where r.autoridad_final and i.activo"""
        )
        authority = cur.fetchone()
        approver_id = authority["aprobador_membership_id"] if authority else None
    if not authority or not approver_id or authority["telegram_user_id"] is None:
        return None
    return authority


def requiere_aprobacion(authority, requester_membership_id) -> bool:
    """Si el borrador lo confirma otra persona (quien pidió lo envía con Enviar a
    aprobación) y no quien lo pidió (Confirmar). Es la política que decide el botón del
    resumen: `_finalize` y `boton_final_de` la comparten."""
    return (str(authority["aprobador_membership_id"])
            != str(requester_membership_id))


def boton_final_de(cur, responsible_id, requester_membership_id) -> str | None:
    """El botón que cierra el resumen de quien pidió el borrador si `responsible_id`
    es el responsable (Confirmar o Enviar a aprobación, tal como se muestra), o `None`
    si no hay a quién mandárselo (`_find_confirmer`) y no se sabe."""
    authority = _find_confirmer(cur, responsible_id)
    if authority is None:
        return None
    return etiqueta_sin_icono(
        ETIQUETA_ENVIAR if requiere_aprobacion(authority, requester_membership_id)
        else ETIQUETA_CONFIRMAR)


def _offer_review(cur, request, who, now, preview_text, preview, cuerpo_resumen):
    """El resumen de quien pidió el borrador cuando lo confirma otra persona
    (T9-R1c-4): la misma vista previa con Enviar a aprobación, Modificar y Cancelar,
    como respuesta a su acto (ADR 0013 regla 2). Es una rama abierta suya hasta que
    lo envía. A quien confirma no le llega nada.

    El cuerpo del resumen se guarda aparte de su cierre (`args`): al enviar, quien
    confirma recibe el mismo cuerpo con el cierre de SU botón, sin recuperarlo
    cortando el texto visible (R8)."""
    from .pendientes import registrar

    request_id = str(request["id"])
    pending = registrar(
        cur, who, herramienta=HERRAMIENTA_REVISION_BORRADOR,
        args={"cuerpo_resumen": cuerpo_resumen},
        resumen=preview_text, vence_en=now + timedelta(hours=8),
        chat_id=request["chat_id"], draft_id=str(request["task_draft_id"]),
        draft_version=request["version"], preview=preview,
        opciones=[(ETIQUETA_ENVIAR, VALUE_SEND), (ETIQUETA_MODIFICAR, VALUE_MODIFY),
                  (ETIQUETA_CANCELAR, False)],
    )
    enqueue_outbox(
        cur, workspace_id=who.workspace_id, chat_id=request["chat_id"],
        text=preview_text, recipient_membership_id=str(request["membership_id"]),
        scheduled_for=now,
        # Distinta de la de la vista previa de quien confirma (`preview`).
        dedupe_key=f"intake:{request_id}:review:v{request['version']}",
        pending_action_id=pending.id, is_response=True,
    )
    return IntakeOutcome(request_id, preview_text, changed=True,
                         pending_action_id=pending.id)


def request_line(requester_name: str | None) -> str:
    """La primera línea del pedido de aprobación: quién manda la tarea."""
    return (f"{requester_name or 'Alguien del equipo'} te manda esta tarea para "
            "que la confirmes.")


def _quien_pide(cur, request) -> str:
    cur.execute("select nombre from integrante where membership_id = %s",
                (request["membership_id"],))
    fila = cur.fetchone()
    return request_line(fila["nombre"] if fila else None)


def _send_to_confirmer(cur, request, now, preview_text, preview, version,
                       authority):
    """Registra la vista previa del borrador para quien lo confirma y la encola.
    Devuelve la acción y si quien confirma es quien pidió el borrador.

    Modificar (T9-R1c-3) es de quien pidió el borrador y lo confirma él mismo: es
    quien tiene la rama abierta. Si confirma otra persona, ella sólo ve Confirmar y
    Rechazar (T9-R1c-4: quien pidió ya lo revisó y lo envió)."""
    from .autoridad import Canal
    from .pendientes import registrar

    approver_id = str(authority["aprobador_membership_id"])
    workspace_id = str(request["workspace_id"])
    confirmer = Solicitante(
        app_user_id=str(authority["app_user_id"]), canal=Canal.ESPACIO,
        workspace_id=workspace_id, membership_id=approver_id,
    )
    requester_confirms = approver_id == str(request["membership_id"])
    if not requester_confirms:
        # Quien confirma lo de otra persona tiene que saber de quién es (2026-10-01).
        preview_text = f"{_quien_pide(cur, request)}\n\n{preview_text}"
    if requester_confirms:
        options = [(ETIQUETA_CONFIRMAR, True), (ETIQUETA_MODIFICAR, VALUE_MODIFY),
                   (ETIQUETA_CANCELAR, False)]
    else:
        # Quien confirma lo de otra persona lo rechaza, con un motivo que le llega
        # a quien lo pidió (2026-09-30); cancelar lo propio sigue siendo Cancelar.
        options = [(ETIQUETA_CONFIRMAR, True), (ETIQUETA_RECHAZAR, VALUE_REJECT)]
    pending = registrar(
        cur, confirmer, herramienta="confirmar_borrador_tarea", args={},
        resumen=preview_text, vence_en=now + timedelta(hours=8),
        chat_id=authority["telegram_user_id"], draft_id=str(request["task_draft_id"]),
        draft_version=version, preview=preview, opciones=options,
    )
    enqueue_outbox(
        cur, workspace_id=workspace_id,
        chat_id=authority["telegram_user_id"], text=preview_text,
        recipient_membership_id=approver_id, scheduled_for=now,
        dedupe_key=f"intake:{request['id']}:preview:v{version}",
        pending_action_id=pending.id,
        # Quien actúa (un toque o un mensaje) es quien confirma: el resumen le
        # contesta a ese acto y no queda sujeto a horario, tope ni retención
        # (ADR 0013 regla 2). Si confirma otra persona, es un mensaje que Prisma
        # le inicia a ella.
        is_response=requester_confirms, es_coordinacion=not requester_confirms,
    )
    return pending, requester_confirms



# Lo que dice el cierre del resumen sobre el botón que le toca a quien lo lee: no
# es el mismo para quien confirma (Confirmar) que para quien pidió el borrador y
# lo revisa antes de enviarlo (Enviar a aprobación, R4c-H9).
CIERRE_CONFIRMAR = "Con Confirmar se crea la tarea con estos datos."


def cierre_enviar(confirma: str | None) -> str:
    """Lo que dice el resumen de quien pidió el borrador cuando lo confirma otra
    persona: qué hace su botón y cuándo se crea la tarea."""
    nombre = normalize_text(confirma) if isinstance(confirma, str) else ""
    a_quien = nombre or "quien lo confirma"
    return (f"Con Enviar a aprobación se lo mando a {a_quien} para que lo "
            "confirme: la tarea se crea cuando lo confirme.")


def render_resumen(*, title, description="", objective, area, responsible, due_date,
                   acceptance_criterion, evidence, cierre=CIERRE_CONFIRMAR,
                   variante="B", cur=None, workspace_id=None,
                   historial=None, apertura=None) -> TextoRedactado:
    """El resumen para revisar, redactado por `redaccion` (ADR 0014, etapa 6), en
    cuerpo y cierre. Con `cur` la variante A puede llamar al modelo (y registra el
    intento); sin él son las plantillas. Sólo muestra lo que tiene: una
    descripción que nadie dio no se dice "sin descripción". La evidencia se
    nombra como la lee una persona."""
    evidence_text = (", ".join(nombre_legible(e) for e in evidence)
                     if evidence else "No requiere evidencia")
    lineas = [("Título", title)]
    if description:
        lineas.append(("Descripción", description))
    lineas += [("Objetivo", objective), ("Área", area),
               ("Responsable", responsible), ("Fecha objetivo", due_date),
               ("Criterio de aceptación", acceptance_criterion),
               ("Evidencia", evidence_text)]
    resultado = ResultadoTurno(resumen=Resumen(
        "Resumen para revisar", tuple(lineas), cierre))
    if apertura is not None:
        # La frase ya la dijo el modelo en su turno: sólo se arma el resumen.
        return TextoRedactado(f"{apertura}\n\n{_resumen_b(resultado.resumen)}",
                              cierre)
    if cur is None:
        return redactar_partes(resultado, variante)
    texto = redactar_turno(cur, workspace_id, resultado, variante,
                           historial=historial)
    if texto.cierre != cierre or not texto.texto.endswith(cierre):
        # El cierre es del código y nunca falta (F-C5): quien confirma tiene el
        # botón y necesita el texto que dice qué hace. Si algún camino de la
        # redacción lo perdió, se vuelve a poner y queda registrado.
        registrar_incidente(
            cur, workspace_id,
            "Un resumen para revisar salió de la redacción sin su cierre: se volvió "
            "a poner.", severidad="media", etapa=ETAPA_RESUMEN_SIN_CIERRE)
        cuerpo = texto.cuerpo.rstrip()
        if cuerpo.endswith(cierre):
            cuerpo = cuerpo[:-len(cierre)].rstrip()
        texto = TextoRedactado(cuerpo, cierre, texto.fallida)
    return texto


def render_preview(**datos) -> str:
    """El resumen para revisar como un solo texto (`render_resumen`)."""
    return render_resumen(**datos).texto


def _con_cierre(cuerpo: str, cierre: str) -> str:
    """El mismo cuerpo de resumen con otro cierre: el cuerpo es el que se guardó
    al armarlo, no un texto que se vuelve a cortar (R8)."""
    return TextoRedactado(cuerpo, cierre).texto


def _preview_offenders(**values):
    rendered = {
        "title": f"Title: {values['title']}\n",
        "description": f"Description: {values['description'] or 'No description'}\n",
        "objective": f"Objective: {values['objective']}\n",
        "area": f"Area: {values['area']}\n",
        "responsible": f"Responsible: {values['responsible']}\n",
        "due_date": f"Due date: {values['due_date']}\n",
        "acceptance_criterion":
            f"Acceptance criterion: {values['acceptance_criterion']}\n",
        "evidence": f"Evidence: {', '.join(values['evidence'])}\n",
    }
    total = telegram_text_length(render_preview(**values))
    offenders = []
    for field, text in sorted(
            rendered.items(), key=lambda item: telegram_text_length(item[1]),
            reverse=True):
        offenders.append(field)
        label_only = text.split(":", 1)[0] + ": \n"
        total -= max(0, telegram_text_length(text) - telegram_text_length(label_only))
        if total <= SAFE_TELEGRAM_TEXT:
            break
    return offenders


def telegram_text_length(text: str) -> int:
    return telegram_utf16_units(text)


def _cancel(cur, request, who, now, enqueue=True, reason=None):
    request_id = str(request["id"])
    result = {"estado": "cancelled", "request_id": request_id}
    cur.execute(
        """update task_intake_request
              set estado = 'cancelled', terminal_result = %s, actualizado_en = %s
            where id = %s and estado = 'active'""",
        (Jsonb(result), now, request_id),
    )
    cur.execute(
        "update task_draft set estado = 'cancelled', actualizado_en = %s where id = %s",
        (now, request["task_draft_id"]),
    )
    cur.execute(
        """update pending_action set estado = 'cancelada', resuelta_en = %s,
                  resuelta_por = %s
            where draft_id = %s and estado = 'esperando'""",
        (now, who.app_user_id, request["task_draft_id"]),
    )
    cur.execute(
        """update pending_action_option set activa = false
            where pending_action_id in
              (select id from pending_action where draft_id = %s)""",
        (request["task_draft_id"],),
    )
    _invalidate_open_inputs(cur, request_id)
    # Un rechazo (quien confirma lo de otra persona) deja su motivo en la auditoría.
    registrar_auditoria(
        cur, accion=("cancelar_ingreso_tarea" if reason is None
                     else "rechazar_ingreso_tarea"),
        workspace_id=who.workspace_id,
        actor_app_user_id=who.app_user_id, actor_kind="persona",
        sujeto_tipo="task_draft", sujeto_id=str(request["task_draft_id"]),
        detalle={"request_id": request_id,
                 **({} if reason is None else {"motivo": reason})},
    )
    text = "Listo, cancelé el borrador de la tarea."
    if enqueue:
        _enqueue(cur, request, text, now, f"intake:{request_id}:terminal:cancelled")
    return IntakeOutcome(request_id, text, changed=True, terminal="cancelled")


def _enqueue(cur, request, text, now, dedupe, choice_set_id=None, block=None):
    enqueue_outbox(
        cur, workspace_id=str(request["workspace_id"]), chat_id=request["chat_id"],
        recipient_membership_id=str(request["membership_id"]), text=text,
        scheduled_for=now, dedupe_key=dedupe, is_response=True,
        intake_choice_set_id=choice_set_id, bloque_copiable=block,
    )


def _say_real_state(cur, request, text, now, key) -> IntakeOutcome:
    """Un estado real del alta que impide seguir: su texto es la respuesta a quien
    actuó (ADR 0013 regla 3). El resultado sigue siendo inerte (no cambió nada) y
    dice que ya se respondió, para que nadie repregunte encima."""
    # La clave incluye el mensaje o toque que dispara el estado (T9-R4, review
    # R3-001): sin eso, un reintento mientras el mismo estado sigue trabado se
    # descartaba como duplicado y la persona no recibía nada. Sin evento atado
    # (una llamada directa, sin turno) queda como antes.
    disparador = entrante_atado(cur)
    _enqueue(cur, request, text, now,
             f"intake:{request['id']}:state:{key}:v{request['version']}"
             + (f":{disparador}" if disparador else ""))
    return IntakeOutcome(str(request["id"]), text, inert=True, responded=True)


def _request(cur, request_id):
    cur.execute("select * from task_intake_request where id = %s", (request_id,))
    return cur.fetchone()


# Las preguntas del alta, en castellano neutro y sin jerga: nada de límites ni de
# "exacto" (R4c-H7). El límite se dice sólo cuando un valor lo pasa
# (`_user_limit_prompt`).
_PREGUNTA_DEL_CAMPO = {
    "title": "¿Qué hay que hacer?",
    "description": "Escribí la descripción de la tarea.",
    "objective": "Escribí parte del nombre del objetivo.",
    "responsible": "Escribí parte del nombre de la persona responsable.",
    "area": "Escribí parte del nombre del área.",
    "due_date": "¿Para cuándo la necesitás? Decime la fecha.",
    "acceptance_criterion": ("¿Cómo se sabe que la tarea está terminada? "
                             "Escribí el criterio de aceptación."),
}
_CONFIRMA_EL_CAMPO = {
    "title": "¿Confirmás este título?",
    "description": "¿Confirmás esta descripción?",
    "due_date": "¿Confirmás esta fecha objetivo?",
    "acceptance_criterion": "¿Confirmás este criterio de aceptación?",
}


def _proposal_prompt(field, value):
    if field == "due_date":
        value = format_due_date(value)
    return f"{_CONFIRMA_EL_CAMPO[field]} {value}"


def _candidate_prompt(field):
    return {
        "objective": "¿A qué objetivo pertenece la tarea?",
        "responsible": "¿Quién va a ser responsable de la tarea?",
        "area": "¿De qué área es la tarea?",
    }[field]


def _free_text_prompt(field):
    return _PREGUNTA_DEL_CAMPO[field]


def _user_limit_prompt(field):
    names = {
        "title": "título de la tarea",
        "description": "descripción de la tarea",
        "objective": "texto para buscar el objetivo",
        "responsible": "texto para buscar a la persona responsable",
        "area": "texto para buscar el área",
        "due_date": "texto de la fecha objetivo",
        "acceptance_criterion": "criterio de aceptación",
    }
    return f"Acortá sólo {names[field]} a {USER_FIELD_LIMITS[field]} caracteres como máximo."
