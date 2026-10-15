"""How the task page and the web task detail name a task's state (`tarea_vista.ESTADOS`).

The web says "esperando" for a blocked task, never "trabada" (the user's MA-3 decision): the
detail of a task uses the same word as its card and the counters.
"""

from __future__ import annotations

import re
from zoneinfo import ZoneInfo

from leda.tarea_vista import ESTADOS, _hecho

ZONA = ZoneInfo("America/Argentina/Buenos_Aires")
TRABADA = re.compile(r"(?<![a-z])(?:des)?trab(?!aj)|bloque[oa]", re.IGNORECASE)


def test_una_tarea_bloqueada_se_lee_esperando():
    assert ESTADOS["bloqueada"] == "esperando"


def test_ningun_estado_dice_trabada():
    assert not [e for e in ESTADOS.values() if "trab" in e]


def test_la_historia_dice_que_quedo_esperando_y_que_ya_pudo_seguir():
    """User decision (2026-10-15): the task history says what was missing and that it could go
    on, never "Se trabó" or "Se destrabó"."""
    renglon = _hecho({"que": "bloqueo", "causa": "el cable", "quien": "Marcos",
                      "resuelto_en": "2026-10-20T10:00:00-03:00",
                      "cuando": "2026-10-19T10:00:00-03:00"}, ZONA)

    assert "Quedó esperando: el cable (lo dijo Marcos). Ya pudo seguir el " in renglon
    assert not TRABADA.search(renglon), renglon
