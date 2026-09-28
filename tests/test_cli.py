"""`cli.py` no tenía ninguna prueba (docs/capacidades.md, "Trampas
conocidas"). Estas cubren sólo el cableado del interruptor `--sin-cadencias`
sobre `escuchar` y `servir` -- nunca tocan Telegram, uvicorn ni un scheduler
real."""

from __future__ import annotations

from prisma import cli


def test_escuchar_sin_cadencias_llega_a_local_escuchar(conn, corework, monkeypatch):
    from prisma import local

    monkeypatch.setattr(cli, "conectar", lambda *a, **k: conn)
    llamadas = []
    monkeypatch.setattr(
        local, "escuchar",
        lambda conn_, slug, ws, **kw: llamadas.append((slug, ws, kw)))

    assert cli.main(["escuchar", "corework", "--sin-cadencias"]) == 0

    assert len(llamadas) == 1
    slug, ws, kw = llamadas[0]
    assert slug == "corework"
    assert ws == corework.workspace_id
    assert kw == {"con_cadencias": False}


def test_escuchar_sin_el_flag_deja_las_cadencias_activas(conn, corework, monkeypatch):
    from prisma import local

    monkeypatch.setattr(cli, "conectar", lambda *a, **k: conn)
    llamadas = []
    monkeypatch.setattr(
        local, "escuchar",
        lambda conn_, slug, ws, **kw: llamadas.append(kw))

    assert cli.main(["escuchar", "corework"]) == 0

    assert llamadas == [{"con_cadencias": True}]


class _SchedulerFalso:
    def start(self) -> None:
        pass


def test_servir_sin_cadencias_llega_a_reloj_montar(monkeypatch):
    import uvicorn

    from prisma import reloj

    llamadas = []

    def _montar_falso(conn_factory, **kw):
        llamadas.append(kw)
        return _SchedulerFalso()

    monkeypatch.setattr(reloj, "montar", _montar_falso)
    monkeypatch.setattr(uvicorn, "run", lambda *a, **k: None)

    assert cli.main(["servir", "--sin-cadencias"]) == 0
    assert llamadas == [{"con_cadencias": False}]


def test_servir_sin_el_flag_deja_las_cadencias_activas(monkeypatch):
    import uvicorn

    from prisma import reloj

    llamadas = []

    def _montar_falso(conn_factory, **kw):
        llamadas.append(kw)
        return _SchedulerFalso()

    monkeypatch.setattr(reloj, "montar", _montar_falso)
    monkeypatch.setattr(uvicorn, "run", lambda *a, **k: None)

    assert cli.main(["servir"]) == 0
    assert llamadas == [{"con_cadencias": True}]
