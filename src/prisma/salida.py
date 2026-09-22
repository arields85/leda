"""Single Telegram-visible payload contract for producers and transport."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable


TELEGRAM_TEXT_LIMIT = 4096
BUTTON_TEXT_LIMIT = 3900
BUTTON_LABEL_LIMIT = 80
CALLBACK_DATA_BYTES = 64
_SPLIT_BODY_LIMIT = 4000
NO_EFFECT_STATUS = "Estado: sin cambios."
_NO_EFFECT_PATTERNS = tuple(re.compile(pattern, re.IGNORECASE) for pattern in (
    r"\bno se (?:registr[oó]|modific[oó]|cambi[oó]) (?:nada|ning[uú]n cambio)\b",
    r"\bno se registr[oó] (?:la|una|ninguna) (?:tarea|operaci[oó]n|actualizaci[oó]n|solicitud)\b",
    r"\bnada (?:se )?(?:registr[oó]|modific[oó]|cambi[oó])\b",
    r"\bsin cambios\b",
    r"\bno pude (?:hacer|realizar|aplicar|completar) (?:el|ese|ning[uú]n) cambio(?: solicitado)?\b",
    r"\bnothing (?:was |has been )?(?:changed|modified|updated|saved|applied)\b",
    r"\bno changes? (?:were |was |have been )?(?:made|saved|applied|recorded)\b",
))


class PayloadValidationError(ValueError):
    """The visible payload cannot be represented safely by Telegram."""


@dataclass(frozen=True)
class PreparedPayload:
    text: str
    dedupe_key: str


def telegram_utf16_units(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def normalize_visible_text(raw: Any) -> str:
    text = unicodedata.normalize("NFC", str(raw or ""))
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    dangerous_format_controls = {
        "\u00ad", "\u061c", "\u200b", "\u200e", "\u200f", "\ufeff",
        *map(chr, range(0x202A, 0x202F)),
        *map(chr, range(0x2066, 0x206A)),
    }
    text = "".join(
        char for char in text
        if char in "\n\t"
        or (unicodedata.category(char) != "Cc"
            and char not in dangerous_format_controls)
    )
    return re.sub(r"[ ]{2,}", " ", text).strip()


def with_no_effect_status(raw: Any, *, required: bool = True) -> str:
    text = normalize_visible_text(raw)
    marker = re.compile(
        rf"(?im)^\s*{re.escape(NO_EFFECT_STATUS)}\s*$")
    text = normalize_visible_text(marker.sub("", text))
    if not required:
        return text
    for pattern in _NO_EFFECT_PATTERNS:
        text = pattern.sub("", text)
    text = normalize_visible_text(text).strip(" .,;:-")
    return f"{text}\n\n{NO_EFFECT_STATUS}" if text else NO_EFFECT_STATUS


def prepare_buttons(buttons: Iterable[Any]) -> list[tuple[str, str]]:
    prepared = []
    for button in buttons:
        label = normalize_visible_text(
            getattr(button, "etiqueta", button[0] if isinstance(button, tuple) else ""))
        callback = str(getattr(
            button, "callback_data", button[1] if isinstance(button, tuple) else ""))
        if not label or telegram_utf16_units(label) > BUTTON_LABEL_LIMIT:
            raise PayloadValidationError(
                f"La etiqueta de un botón excede {BUTTON_LABEL_LIMIT} unidades UTF-16.")
        if not callback or len(callback.encode("utf-8")) > CALLBACK_DATA_BYTES:
            raise PayloadValidationError(
                f"El callback de un botón excede {CALLBACK_DATA_BYTES} bytes.")
        prepared.append((label, callback))
    return prepared


def prepare_payload(text: Any, *, dedupe_key: str, has_buttons: bool = False,
                    buttons: Iterable[Any] = (),
                    allow_split: bool = False) -> list[PreparedPayload]:
    normalized = normalize_visible_text(text)
    if not normalized:
        raise PayloadValidationError("El mensaje visible no puede quedar vacío.")
    prepared_buttons = prepare_buttons(buttons)
    has_buttons = has_buttons or bool(prepared_buttons)
    limit = BUTTON_TEXT_LIMIT if has_buttons else TELEGRAM_TEXT_LIMIT
    if telegram_utf16_units(normalized) <= limit:
        return [PreparedPayload(normalized, dedupe_key)]
    if has_buttons:
        raise PayloadValidationError(
            f"Un mensaje con botones no puede exceder {BUTTON_TEXT_LIMIT} unidades UTF-16.")
    if not allow_split:
        raise PayloadValidationError(
            f"El mensaje no puede exceder {TELEGRAM_TEXT_LIMIT} unidades UTF-16.")

    chunks = _split(normalized)
    total = len(chunks)
    result = []
    for index, chunk in enumerate(chunks, 1):
        rendered = f"({index}/{total})\n{chunk}"
        if telegram_utf16_units(rendered) > TELEGRAM_TEXT_LIMIT:
            raise PayloadValidationError("No se pudo dividir el mensaje de forma segura.")
        result.append(PreparedPayload(
            rendered, f"{dedupe_key}:part:{index:03d}-of-{total:03d}"))
    return result


def _split(text: str) -> list[str]:
    chunks = []
    remaining = text
    while telegram_utf16_units(remaining) > _SPLIT_BODY_LIMIT:
        end = _prefix_index(remaining, _SPLIT_BODY_LIMIT)
        candidate = remaining[:end]
        floor = max(1, int(end * 0.6))
        boundaries = [candidate.rfind("\n\n", floor),
                      candidate.rfind("\n", floor),
                      candidate.rfind(" ", floor)]
        boundary = max(boundaries)
        if boundary > 0:
            end = boundary
        chunks.append(remaining[:end].rstrip())
        remaining = remaining[end:].lstrip()
    if remaining:
        chunks.append(remaining)
    return chunks


def _prefix_index(text: str, max_units: int) -> int:
    low, high = 0, len(text)
    while low < high:
        middle = (low + high + 1) // 2
        if telegram_utf16_units(text[:middle]) <= max_units:
            low = middle
        else:
            high = middle - 1
    return low


def enqueue_outbox(cur, *, workspace_id: str, chat_id: int,
                   text: Any, dedupe_key: str,
                   recipient_membership_id: str | None = None,
                   message_type: str = "normal", state: str = "listo",
                   scheduled_for: datetime | None = None,
                   expires_at: datetime | None = None,
                   is_response: bool = False,
                   pending_action_id: str | None = None,
                   intake_choice_set_id: str | None = None,
                   allow_split: bool = False) -> int:
    has_buttons = pending_action_id is not None or intake_choice_set_id is not None
    payloads = prepare_payload(
        text, dedupe_key=dedupe_key, has_buttons=has_buttons,
        allow_split=allow_split,
    )
    inserted = 0
    for payload in payloads:
        cur.execute(
            """insert into message_outbox
                 (workspace_id, chat_id, destinatario_membership_id, tipo, cuerpo,
                  estado, programado_para, vence_en, dedupe_key, es_respuesta,
                  pending_action_id, intake_choice_set_id)
               values (%s, %s, %s, %s, %s, %s, coalesce(%s, now()), %s, %s,
                       %s, %s, %s)
               on conflict (dedupe_key) do nothing""",
            (workspace_id, chat_id, recipient_membership_id, message_type,
             payload.text, state, scheduled_for, expires_at, payload.dedupe_key,
             is_response, pending_action_id, intake_choice_set_id),
        )
        inserted += cur.rowcount
    return inserted
