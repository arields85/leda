"""How the task page and the web task detail name a task's state (`tarea_vista.ESTADOS`).

The web says "esperando" for a blocked task, never "trabada" (the user's MA-3 decision): the
detail of a task uses the same word as its card and the counters.
"""

from __future__ import annotations

from leda.tarea_vista import ESTADOS


def test_una_tarea_bloqueada_se_lee_esperando():
    assert ESTADOS["bloqueada"] == "esperando"


def test_ningun_estado_dice_trabada():
    assert not [e for e in ESTADOS.values() if "trab" in e]
