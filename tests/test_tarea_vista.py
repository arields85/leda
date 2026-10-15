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


def _renglon(**h):
    return _hecho({"cuando": "2026-10-19T10:00:00-03:00", "quien": "Marcos", **h}, ZONA)


def test_la_historia_dice_quien_se_ocupa_de_lo_que_falta():
    """Who handles what is missing, never "quién la destraba" (user, 2026-10-15)."""
    renglones = {
        "no sabe": _renglon(que="quien_destraba", no_sabe=True),
        "nadie mas": _renglon(que="quien_destraba", nadie_mas=True),
        "otra persona": _renglon(que="quien_destraba", destraba="Mariano"),
        "para cuando": _renglon(que="dicho_del_bloqueo", para_cuando="2026-10-23"),
        "sigue": _renglon(que="asentado", por="sigue_trabada", dias_habiles=5),
        "nadie la toma": _renglon(que="asentado", por="nadie_la_toma"),
    }

    assert "Marcos dijo que no sabe quién se ocupa de lo que falta" in renglones["no sabe"]
    assert "Marcos dijo que no hay otra persona que se ocupe" in renglones["nadie mas"]
    assert "Marcos dijo que de eso se ocupa Mariano" in renglones["otra persona"]
    assert "Marcos dijo que lo consigue el vie 23/10" in renglones["para cuando"]
    assert "Quedó asentado que sigue esperando: 5 días hábiles" in renglones["sigue"]
    assert "Quedó asentado que nadie se ocupa de lo que le falta" in renglones["nadie la toma"]
    assert not [r for r in renglones.values() if TRABADA.search(r)]
