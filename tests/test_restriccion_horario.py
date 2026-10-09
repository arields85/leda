"""`tools/restriccion_horario.py` sólo corre sobre las bases de desarrollo.

Desde la E2-6 del Motor (`odd/tasks/prueba-chica-del-motor.md`) admite también `leda_motor`,
la base de la prueba chica; cualquier otra base se rechaza antes de tocar nada. La conexión es
de mentira: la prueba no toca ninguna base.
"""

from __future__ import annotations

import contextlib

import importlib.util
import pathlib
from datetime import time
from types import SimpleNamespace

import pytest

RUTA = pathlib.Path(__file__).resolve().parents[1] / "tools" / "restriccion_horario.py"


def _herramienta():
    spec = importlib.util.spec_from_file_location("restriccion_horario", RUTA)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class _Cursor:
    def __init__(self, filas: list[dict]) -> None:
        self.filas = filas
        self.sentencias: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, sql: str, params=None) -> None:
        self.sentencias.append(sql)

    def fetchone(self):
        return self.filas.pop(0)


class _Conexion:
    def __init__(self, base: str) -> None:
        horario = {"dias": ["lunes", "martes", "miercoles", "jueves", "viernes"],
                   "hora_inicio": time(9, 0), "hora_fin": time(17, 0)}
        self.info = SimpleNamespace(dbname=base)
        self.cur = _Cursor([{"id": "espacio"}, dict(horario), dict(horario)])

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def cursor(self) -> _Cursor:
        return self.cur

    def transaction(self):
        # `admin()` abre una transacción y toma el rol de administración (work_calendar tiene
        # RLS forzado desde la 0041).
        return contextlib.nullcontext()


@pytest.mark.parametrize("base", ["leda", "leda_flujo", "leda_motor"])
def test_admite_las_bases_de_desarrollo(monkeypatch, capsys, base):
    herramienta = _herramienta()
    conexion = _Conexion(base)
    monkeypatch.setattr(herramienta, "conectar", lambda: conexion)
    monkeypatch.setattr("sys.argv", ["restriccion_horario.py", "estado", "corework"])

    assert herramienta.main() == 0

    salida = capsys.readouterr().out
    assert f"base: {base}" in salida and "restricción de horario: prendida" in salida
    assert conexion.cur.sentencias[0] == "set local role leda_admin"


def test_rechaza_cualquier_otra_base_sin_tocarla(monkeypatch, capsys):
    herramienta = _herramienta()
    conexion = _Conexion("leda_produccion")
    monkeypatch.setattr(herramienta, "conectar", lambda: conexion)
    monkeypatch.setattr("sys.argv", ["restriccion_horario.py", "apagar", "corework"])

    assert herramienta.main() == 1

    assert "STOP" in capsys.readouterr().out and conexion.cur.sentencias == []
