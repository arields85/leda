"""Server-owned conversational intake for Unit 1A task drafts."""

from __future__ import annotations

import json
import re
import secrets
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import psycopg
from psycopg.types.json import Jsonb

from .autoridad import Denegado, Solicitante
from .db import registrar_auditoria
from .incidentes import registrar_incidente
from .salida import (BUTTON_TEXT_LIMIT, ETIQUETA_CANCELAR, ETIQUETA_CONFIRMAR,
                     ETIQUETA_MODIFICAR, ICONO_CANCELAR, ICONO_OTRA_OPCION,
                     ICONO_VER_MAS, PayloadValidationError, con_icono,
                     enqueue_outbox, etiqueta_sin_icono, etiquetas_de_tarea,
                     normalize_visible_text, prepare_buttons, prepare_payload, telegram_utf16_units,
                     with_no_effect_status)


CALLBACK_PREFIX = "i:"
SAFE_TELEGRAM_TEXT = BUTTON_TEXT_LIMIT
CANDIDATE_PAGE_SIZE = 7
FIELDS = (
    "title", "description", "objective", "responsible", "area", "due_date",
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


class AmbiguousDate(ValueError):
    pass


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

    def as_json(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "text": self.text,
            "changed": self.changed,
            "inert": self.inert,
            "pending_action_id": self.pending_action_id,
            "terminal": self.terminal,
        }


def normalize_text(raw: str) -> str:
    return normalize_visible_text(raw)


_MONTHS = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5,
    "junio": 6, "julio": 7, "agosto": 8, "septiembre": 9,
    "setiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
}


def resolve_date(raw: str, now: datetime, timezone_name: str) -> date:
    text = normalize_text(raw).casefold()
    local_today = now.astimezone(ZoneInfo(timezone_name)).date()
    relative = {"hoy": 0, "mañana": 1, "manana": 1, "pasado mañana": 2,
                "pasado manana": 2}
    if text in relative:
        result = local_today + timedelta(days=relative[text])
    else:
        result = _parse_absolute_date(text, local_today)
    if result < local_today:
        raise AmbiguousDate("La fecha indicada ya pasó.")
    return result


def _parse_absolute_date(text: str, today: date) -> date:
    try:
        if re.fullmatch(r"\d{4}-\d{1,2}-\d{1,2}", text):
            year, month, day = map(int, text.split("-"))
            return date(year, month, day)

        numeric = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})(?:[/-](\d{4}))?", text)
        if numeric:
            day, month = int(numeric[1]), int(numeric[2])
            return _next_occurrence(day, month, int(numeric[3]) if numeric[3] else None,
                                    today)

        named = re.fullmatch(
            r"(?:el\s+)?(\d{1,2})\s+(?:de\s+)?([a-záéíóú]+)(?:\s+(?:de\s+)?(\d{4}))?",
            text,
        )
        if named and named[2] in _MONTHS:
            return _next_occurrence(
                int(named[1]), _MONTHS[named[2]],
                int(named[3]) if named[3] else None, today,
            )
    except ValueError as exc:
        raise AmbiguousDate("La fecha no es válida.") from exc
    raise AmbiguousDate("La fecha es ambigua o no tiene un formato reconocido.")


def _next_occurrence(day: int, month: int, year: int | None, today: date) -> date:
    if year is not None:
        return date(year, month, day)
    for candidate_year in range(today.year, today.year + 9):
        try:
            candidate = date(candidate_year, month, day)
        except ValueError:
            continue
        if candidate >= today:
            return candidate
    raise AmbiguousDate("No hay una próxima ocurrencia válida.")


def token_de(callback: str) -> str | None:
    if not callback.startswith(CALLBACK_PREFIX):
        return None
    return callback[len(CALLBACK_PREFIX):] or None


def callback_data(token: str) -> str:
    return f"{CALLBACK_PREFIX}{token}"


def start(cur: psycopg.Cursor, who: Solicitante, *, chat_id: int,
          source_inbound_id: str, source_raw_text: str,
          proposals: dict[str, Any], now: datetime,
          buttons_first: bool = False) -> IntakeOutcome:
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
              and estado = 'active' for update""",
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
    _store_proposals(
        cur, request_id, proposals, source_inbound_id, source_raw_text, now,
        who.workspace_id,
    )
    cur.execute("select * from task_intake_request where id = %s", (request_id,))
    return _advance(cur, cur.fetchone(), who, now,
                    buttons_first=buttons_first)


def _store_proposals(cur, request_id, proposals, inbound_id, raw, now, workspace_id):
    key_map = {
        "title": "title", "description": "description",
        "objective": "objective", "responsible": "responsible",
        "area": "area", "due_date": "due_date",
        "acceptance_criterion": "acceptance_criterion",
    }
    cur.execute("select zona_horaria from workspace where id = %s", (workspace_id,))
    timezone_name = cur.fetchone()["zona_horaria"]
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
            try:
                value = resolve_date(value, now, timezone_name).isoformat()
            except AmbiguousDate:
                continue
        cur.execute(
            """update task_intake_field
                  set estado = 'proposed', valor = %s, proposed_by = 'model',
                      source_inbound_id = %s, source_raw_text = %s,
                      actualizado_en = %s
                where request_id = %s and campo = %s""",
            (Jsonb(value), inbound_id, raw, now, request_id, field),
        )


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
    cur.execute(
        """update message_outbox set estado = 'descartado'
            where intake_choice_set_id = %s
              and estado in ('pendiente', 'esperando_confirmacion', 'listo')""",
        (choice["choice_set_id"],),
    )
    cur.execute(
        """update task_intake_choice
              set activa = false, elegida = (id = %s)
            where choice_set_id = %s""",
        (choice["choice_id"], choice["choice_set_id"]),
    )
    cur.execute(
        """update task_intake_request
              set version = version + 1, actualizado_en = %s
            where id = %s returning *""",
        (now, request_id),
    )
    request = cur.fetchone()
    action = choice["accion"]
    if action == "continue":
        outcome = _advance(cur, request, who, now)
    elif action == "cancel":
        outcome = _cancel(cur, request, who, now)
    elif action == "start_new":
        payload = choice["valor"]
        _cancel(cur, request, who, now, enqueue=False)
        outcome = start(
            cur, who, chat_id=chat_id,
            source_inbound_id=payload["source_inbound_id"],
            source_raw_text=payload["source_raw_text"],
            proposals=payload["proposals"], now=now,
        )
    elif action == "other":
        outcome = _open_free_text(
            cur, request, choice["campo"],
            _free_text_prompt(choice["campo"]), now,
        )
    elif action == "modify_field":
        outcome = _ask_field_change(cur, request, who, choice["valor"]["field"], now)
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


def consume_pending_text(cur: psycopg.Cursor, who: Solicitante, *, chat_id: int,
                         source_inbound_id: str, source_raw_text: str,
                         now: datetime, slot_id: str | None = None,
                         ) -> IntakeOutcome | None:
    """Toma el mensaje como el campo que espera el alta. `slot_id`, si viene,
    es el campo que la persona respondió (el que el gateway leyó al
    interpretar el mensaje, T9-R1c-1): si ese campo ya no está abierto no se
    consume ningún otro."""
    cur.execute(
        """select s.*, r.version, r.estado request_estado
             from task_intake_free_text_slot s
             join task_intake_request r on r.id = s.request_id
            where s.workspace_id = %s and r.membership_id = %s
              and r.chat_id = %s and s.estado = 'active' and r.estado = 'active'
              and (%s::uuid is null or s.id = %s::uuid)
            for update of s, r""",
        (who.workspace_id, who.membership_id, chat_id, slot_id, slot_id),
    )
    slot = cur.fetchone()
    if not slot:
        return None
    request_id = str(slot["request_id"])
    value = normalize_text(source_raw_text)
    if not value:
        return _reject_user_value(
            cur, _request(cur, request_id), slot["campo"],
            "Necesito un texto no vacío.", source_inbound_id, now,
        )

    field = slot["campo"]
    if telegram_text_length(value) > USER_FIELD_LIMITS[field]:
        return _reject_user_value(
            cur, _request(cur, request_id), field,
            _user_limit_prompt(field), source_inbound_id, now,
        )

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
    if field == "due_date":
        cur.execute("select zona_horaria from workspace where id = %s",
                    (who.workspace_id,))
        try:
            value = resolve_date(value, now, cur.fetchone()["zona_horaria"]).isoformat()
        except AmbiguousDate as exc:
            return _open_free_text(cur, request, field, str(exc), now)
    if field in {"objective", "responsible", "area"}:
        return _resolve_user_entity(cur, request, who, field, value,
                                    source_inbound_id, source_raw_text, now)
    _confirm_user_value(cur, request_id, field, value, source_inbound_id,
                        source_raw_text, now)
    return _advance(cur, request, who, now)


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
            for update of r""",
        (who.workspace_id, who.membership_id, chat_id),
    )
    request = cur.fetchone()
    if not request:
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
        """select membership_id from pending_action
            where draft_id = %s and estado = 'esperando' limit 1""",
        (request["task_draft_id"],),
    )
    waiting = cur.fetchone()
    if waiting and str(waiting["membership_id"]) != str(who.membership_id):
        # Espera la confirmación de otra persona: no es una rama abierta de
        # quien lo pidió y su mensaje sigue el camino normal.
        return None
    if waiting:
        prompt = DRAFT_AWAITING_CONFIRMATION
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
    pregunta abierta sólo de quien tiene el botón Confirmar (el aprobador):
    si confirma otra persona, quien lo pidió no tiene una rama abierta (ADR
    0013 regla 1, enmienda del 2026-09-29) y sus mensajes siguen el camino
    normal."""
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
        f"""select p.id, r.id request_id, {_TITLE_OF_REQUEST} titulo
              from task_intake_request r
              join pending_action p on p.draft_id = r.task_draft_id
                                   and p.workspace_id = r.workspace_id
             where r.workspace_id = %s and r.membership_id = %s
               and r.chat_id = %s and r.estado = 'active'
               and p.estado = 'esperando' and p.membership_id = %s
             order by p.creado_en desc limit 1""",
        (who.workspace_id, who.membership_id, chat_id, who.membership_id),
    )
    row = cur.fetchone()
    if row:
        return {"tipo": QUESTION_CONFIRMATION, "id": str(row["id"]),
                "request_id": str(row["request_id"]), "campo": None,
                "titulo": _text_or_none(row["titulo"]),
                "resumen": DRAFT_AWAITING_CONFIRMATION, "opciones": None}
    return None


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


def open_modify_picker(cur: psycopg.Cursor, who: Solicitante, question_id: str,
                       now: datetime, *, via: str) -> IntakeOutcome | None:
    """Modificar en la vista previa del borrador (T9-R1c-3, ADR 0005 decisión 1):
    la cierra sin aplicar nada -- la tarea se crea sólo con Confirmar -- y abre el
    selector "qué dato cambiar", con un botón por dato. `question_id` es el de la
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
    options = [(MODIFY_FIELD_LABELS[field], "modify_field", {"field": field})
               for field in MODIFY_FIELD_LABELS]
    return _open_choices(cur, request, None, MODIFY_PICKER_PROMPT, options, now,
                         kind=MODIFY_PICKER_KIND)


_MODIFY_OPTION = """select p.id, p.membership_id, p.chat_id, p.estado,
                  p.vence_en > %s as vigente
             from pending_action_option o
             join pending_action p on p.id = o.pending_action_id
            where o.token = %s and o.workspace_id = %s and p.draft_id is not null
              and o.valor = to_jsonb('modificar'::text)"""


def es_modificar_de_borrador(cur: psycopg.Cursor, who: Solicitante, token: str,
                             now: datetime) -> bool:
    """Si `token` es el del botón Modificar de una vista previa de borrador."""
    cur.execute(_MODIFY_OPTION, (now, token, who.workspace_id))
    return cur.fetchone() is not None


def modify_from_preview(cur: psycopg.Cursor, who: Solicitante, *, token: str,
                        chat_id: int, now: datetime) -> IntakeOutcome | None:
    """El botón Modificar de la vista previa del borrador. Sólo lo toca su
    dueño, en su chat (`Denegado` si no), y sólo mientras la vista previa espera y
    no venció; `None` si ya no (un toque tardío, un segundo toque)."""
    cur.execute(_MODIFY_OPTION, (now, token, who.workspace_id))
    preview = cur.fetchone()
    if not preview:
        return None
    if str(preview["membership_id"]) != str(who.membership_id)             or preview["chat_id"] != chat_id:
        raise Denegado(NOT_YOURS)
    if preview["estado"] != "esperando" or not preview["vigente"]:
        return None
    return open_modify_picker(cur, who, str(preview["id"]), now, via="boton")


def modify_text_prompt(field: str, current: str) -> str:
    """La pregunta de un dato de texto que se corrige: lo que la persona tenía,
    al final del mensaje, en el bloque que se copia con un toque. Sin nada que
    copiar (una descripción vacía), la pregunta de siempre del campo."""
    if not current:
        return _free_text_prompt(field)
    return (f"Esto tenías en {FREE_TEXT_NAMES[field]}. Tocalo para copiarlo, "
            f"corregilo y mandámelo (hasta {USER_FIELD_LIMITS[field]}): cambio "
            f"sólo eso.\n\n{current}")


def format_due_date(value) -> str:
    """La fecha objetivo como la lee una persona: DD/MM/AAAA. El dato se guarda
    como fecha ISO (ya resuelta en la zona horaria del espacio, sin hora: no hay
    nada que convertir); lo que se muestra y se pega de vuelta pasa por la
    resolución de fechas de siempre. Lo que no es una fecha ISO se deja tal cual."""
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
                         choice_set_id: str, text: str, chat_id: int,
                         now: datetime) -> IntakeOutcome | None:
    """Resuelve la elección abierta con lo que la persona escribió, igual que
    su toque (`resolve_choice`), sólo si el texto es exactamente UNA de las
    opciones activas: mismo texto normalizado, sin mayúsculas y sin el ícono
    del botón. Una opción de entidad (objetivo, persona, área) también se
    reconoce por su nombre completo, que el botón puede acortar. Ninguna
    coincidencia parcial ni aproximada: con cero o con varias opciones, no
    resuelve y devuelve `None`; las opciones son las únicas respuestas."""
    cur.execute(
        """select c.token, c.etiqueta, c.valor
             from task_intake_choice c
             join task_intake_choice_set s on s.id = c.choice_set_id
             join task_intake_request r on r.id = s.request_id
            where s.id = %s and s.workspace_id = %s and r.membership_id = %s
              and s.estado = 'active' and r.estado = 'active' and c.activa
            order by c.orden""",
        (choice_set_id, who.workspace_id, who.membership_id),
    )
    wanted = _match_key(text)
    matches = [row for row in cur.fetchall()
               if wanted and wanted in _option_keys(row)]
    if len(matches) != 1:
        return None
    return resolve_choice(cur, who, token=matches[0]["token"],
                          chat_id=chat_id, now=now)


def _match_key(text: str) -> str:
    return normalize_text(text).casefold()


def _option_keys(option) -> set[str]:
    keys = {_match_key(etiqueta_sin_icono(option["etiqueta"]))}
    value = option["valor"]
    if isinstance(value, dict):
        for name in (value.get("title"), value.get("name")):
            if isinstance(name, str):
                keys.add(_match_key(name))
    return keys


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
                         ref: str | None = None, prefix: str = "") -> bool:
    """Vuelve a mandar la pregunta de la elección abierta con sus botones
    (`prefix`, si viene, va delante en el mismo mensaje). `False` si la
    elección ya no estaba abierta: no manda nada. `ref` distingue este
    reenvío de otros (el mensaje que lo causó); sin él, la referencia es el
    número de mensajes que la elección ya tiene (`n1`, `n2`, ...): cada
    reenvío es un mensaje propio y ninguno depende del reloj."""
    request = _request_of_question(cur, who, QUESTION_CHOICE, choice_set_id,
                                   lock=False)
    if not request:
        return False
    prompt = _first_choice_prompt(cur, choice_set_id)
    if ref is None:
        cur.execute(
            """select count(*) n from message_outbox
                where intake_choice_set_id = %s""", (choice_set_id,))
        ref = f"n{cur.fetchone()['n']}"
    _enqueue(cur, request, f"{prefix}{prompt}", now,
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
        app_user_id=who.app_user_id)
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


def _advance(cur, request, who, now, *, buttons_first=False) -> IntakeOutcome:
    request_id = str(request["id"])
    cur.execute(
        """select campo, estado, valor from task_intake_field
            where request_id = %s order by array_position(%s::text[], campo)""",
        (request_id, list(FIELDS)),
    )
    fields = {row["campo"]: row for row in cur.fetchall()}
    field_order = (("objective",) + tuple(f for f in FIELDS if f != "objective")
                   if buttons_first else FIELDS)
    for field in field_order:
        row = fields[field]
        if row["estado"] == "confirmed":
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
                return _open_choices(
                    cur, request, field, _proposal_prompt(field, row["valor"]),
                    [(CONFIRM, "confirm", None), (REJECT, "reject", None),
                     (OTHER, "other", None)], now,
                )
            return _open_free_text(cur, request, field, _free_text_prompt(field), now)
        if field == "evidence":
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
                return IntakeOutcome(
                    request_id,
                    "No hay una política de evidencia vigente para esa área.",
                    inert=True,
                )
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
            continue
        return _open_entity_page(
            cur, request, who, field,
            row["valor"] if row["estado"] == "proposed" else None, 0, now,
        )
    return _finalize(cur, request, who, now)


def _entity_candidates(cur, request, who, field, query, offset=0):
    query_text = normalize_text(str(query or "")).casefold()
    if field == "objective":
        if query_text:
            cur.execute(
                """select id, titulo, estado from objective
                    where workspace_id = %s and estado in ('activo', 'propuesto')
                      and lower(titulo) = lower(%s)
                    order by titulo, id limit %s offset %s""",
                (who.workspace_id, normalize_text(str(query)),
                 CANDIDATE_PAGE_SIZE + 1, offset),
            )
            rows = cur.fetchall()
            if not rows:
                cur.execute(
                    """select id, titulo, estado from objective
                        where workspace_id = %s and estado in ('activo', 'propuesto')
                          and position(lower(%s) in lower(titulo)) > 0
                        order by titulo, id limit %s offset %s""",
                    (who.workspace_id, normalize_text(str(query)),
                     CANDIDATE_PAGE_SIZE + 1, offset),
                )
                rows = cur.fetchall()
        else:
            cur.execute(
                """select id, titulo, estado from objective
                    where workspace_id = %s and estado in ('activo', 'propuesto')
                    order by titulo, id limit %s offset %s""",
                (who.workspace_id, CANDIDATE_PAGE_SIZE + 1, offset),
            )
            rows = cur.fetchall()
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


def _open_entity_page(cur, request, who, field, query, offset, now):
    candidates, has_more = _entity_candidates(
        cur, request, who, field, query, offset=offset)
    no_match = bool(normalize_text(str(query or ""))) and not candidates
    if no_match:
        query = None
        offset = 0
        candidates, has_more = _entity_candidates(
            cur, request, who, field, None, offset=0)
    if not _candidates_deliverable(field, candidates):
        return _configuration_error(cur, request, who, field, now)
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
    options = [(etiqueta, "select", stored)
              for etiqueta, (_, _, stored) in zip(etiquetas, candidates)]
    if has_more:
        options.append((VER_MAS, "more", {
            "field": field, "query": query,
            "offset": offset + CANDIDATE_PAGE_SIZE,
        }))
    options.append((OTHER, "other", None))
    if no_match:
        prompt = ("No encontré esa opción. Elegí una de las opciones vigentes "
                  f"o tocá «{OTHER}».")
    else:
        prompt = (_candidate_prompt(field) if not query else
                  f"Opciones que coinciden con «{query}».")
    return _open_choices(cur, request, field, prompt, options, now)


def _open_choices(cur, request, field, prompt, options, now, kind=None):
    request_id = str(request["id"])
    kind = kind or field or "choice"
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


def _open_free_text(cur, request, field, prompt, now, replace=False, block=None):
    request_id = str(request["id"])
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


def _finalize(cur, request, who, now):
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
        return IntakeOutcome(request_id,
                             "Alguna opción confirmada ya no está vigente.", inert=True)
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
        return IntakeOutcome(request_id,
                              "No hay una política de evidencia vigente para esa área.",
                              inert=True)
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
    preview_text = render_preview(
        title=values["title"], description=values["description"],
        objective=objective["title"], area=area["name"],
        responsible=responsible["name"],
        due_date=format_due_date(values["due_date"]),
        acceptance_criterion=values["acceptance_criterion"],
        evidence=list(policy["evidencia_requerida"]),
    )
    try:
        prepare_payload(preview_text, dedupe_key="intake-preview", has_buttons=True)
    except PayloadValidationError:
        return _configuration_error(cur, request, who, "aggregate", now)

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
               'evidencia_policy_version', evidencia_policy_version) preview
             from task_draft where id = %s""",
        (request["task_draft_id"],),
    )
    preview = cur.fetchone()["preview"]
    cur.execute(
        """select m.aprobador_membership_id, aprobador.app_user_id,
                  aprobador.telegram_user_id
             from membership m
             left join integrante aprobador
               on aprobador.membership_id = m.aprobador_membership_id
            where m.id = %s""",
        (responsible["id"],),
    )
    authority = cur.fetchone()
    approver_id = authority["aprobador_membership_id"] if authority else None
    if approver_id is None:
        cur.execute(
            """select i.membership_id aprobador_membership_id, i.app_user_id,
                      i.telegram_user_id
                 from integrante i join rol r on r.id = i.rol_id
                where r.autoridad_final and i.activo"""
        )
        authority = cur.fetchone()
        approver_id = authority["aprobador_membership_id"] if authority else None
    if not authority or not approver_id or authority["telegram_user_id"] is None:
        return IntakeOutcome(request_id,
                              "No hay una autoridad activa que pueda revisar el borrador.",
                              inert=True)

    from .autoridad import Canal
    from .pendientes import registrar

    confirmer = Solicitante(
        app_user_id=str(authority["app_user_id"]), canal=Canal.ESPACIO,
        workspace_id=who.workspace_id, membership_id=str(approver_id),
    )
    # Modificar (T9-R1c-3) es de quien pidió el borrador y lo confirma él mismo:
    # es quien tiene la rama abierta. Si confirma otra persona, ella sólo ve
    # Confirmar y Cancelar.
    options = [(ETIQUETA_CONFIRMAR, True), (ETIQUETA_CANCELAR, False)]
    requester_confirms = str(approver_id) == str(request["membership_id"])
    if requester_confirms:
        options.insert(1, (ETIQUETA_MODIFICAR, "modificar"))
    pending = registrar(
        cur, confirmer, herramienta="confirmar_borrador_tarea", args={},
        resumen=preview_text, vence_en=now + timedelta(hours=8),
        chat_id=authority["telegram_user_id"], draft_id=str(request["task_draft_id"]),
        draft_version=request["version"], preview=preview, opciones=options,
    )
    enqueue_outbox(
        cur, workspace_id=who.workspace_id,
        chat_id=authority["telegram_user_id"], text=preview_text,
        recipient_membership_id=str(approver_id), scheduled_for=now,
        dedupe_key=f"intake:{request_id}:preview:v{request['version']}",
        pending_action_id=pending.id,
        # Quien actúa (un toque o un mensaje) es quien confirma: el resumen le
        # contesta a ese acto y no queda sujeto a horario, tope ni retención
        # (ADR 0013 regla 2). Si confirma otra persona, es un mensaje que Prisma
        # le inicia a ella.
        is_response=requester_confirms,
    )
    return IntakeOutcome(request_id, preview_text, changed=True,
                         pending_action_id=pending.id)


def render_preview(*, title, description="", objective, area, responsible, due_date,
                   acceptance_criterion, evidence):
    evidence_text = ", ".join(evidence) if evidence else "No requiere evidencia"
    return (
        "Resumen para revisar\n"
        f"Título: {title}\n"
        f"Descripción: {description or 'Sin descripción'}\n"
        f"Objetivo: {objective}\n"
        f"Área: {area}\n"
        f"Responsable: {responsible}\n"
        f"Fecha objetivo: {due_date}\n"
        f"Criterio de aceptación: {acceptance_criterion}\n"
        f"Evidencia: {evidence_text}\n\n"
        "Al confirmar se comprometen todos los datos mostrados."
    )


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


def _cancel(cur, request, who, now, enqueue=True):
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
    registrar_auditoria(
        cur, accion="cancelar_ingreso_tarea", workspace_id=who.workspace_id,
        actor_app_user_id=who.app_user_id, actor_kind="persona",
        sujeto_tipo="task_draft", sujeto_id=str(request["task_draft_id"]),
        detalle={"request_id": request_id},
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


def _request(cur, request_id):
    cur.execute("select * from task_intake_request where id = %s", (request_id,))
    return cur.fetchone()


def _proposal_prompt(field, value):
    labels = {
        "title": "título", "description": "descripción",
        "due_date": "fecha objetivo",
        "acceptance_criterion": "criterio de aceptación",
    }
    return f"¿Confirmás este {labels[field]}? {value}"


def _candidate_prompt(field):
    return {
        "objective": "Elegí el objetivo de la tarea.",
        "responsible": "Elegí a la persona responsable.",
        "area": "Elegí el área.",
    }[field]


def _free_text_prompt(field):
    return {
        "title": f"Escribí el título exacto de la tarea (hasta {USER_FIELD_LIMITS['title']}).",
        "description": ("Escribí la descripción exacta de la tarea "
                        f"(hasta {USER_FIELD_LIMITS['description']})."),
        "objective": ("Escribí parte del nombre del objetivo "
                      f"(hasta {USER_FIELD_LIMITS['objective']})."),
        "responsible": ("Escribí parte del nombre de la persona responsable "
                        f"(hasta {USER_FIELD_LIMITS['responsible']})."),
        "area": ("Escribí parte del nombre del área "
                 f"(hasta {USER_FIELD_LIMITS['area']})."),
        "due_date": f"Escribí la fecha objetivo exacta (hasta {USER_FIELD_LIMITS['due_date']}).",
        "acceptance_criterion": ("Escribí el criterio de aceptación exacto "
                                 f"(hasta {USER_FIELD_LIMITS['acceptance_criterion']})."),
    }[field]


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
