"""`cli.py` no tenía ninguna prueba (docs/capacidades.md, "Trampas
conocidas"). Estas cubren sólo el cableado del interruptor `--sin-cadencias`
sobre `escuchar` y `servir` -- nunca tocan Telegram, uvicorn ni un scheduler
real."""

from __future__ import annotations

from leda import cli


def test_escuchar_sin_cadencias_llega_a_local_escuchar(conn, corework, monkeypatch):
    from leda import local

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
    from leda import local

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


class _ConnFalsa:
    def close(self) -> None:
        pass


def test_servir_sin_cadencias_llega_a_reloj_montar(monkeypatch):
    import uvicorn

    from leda import reloj

    llamadas = []

    def _montar_falso(conn_factory, **kw):
        llamadas.append(kw)
        return _SchedulerFalso()

    monkeypatch.setattr(cli, "conectar", lambda *a, **k: _ConnFalsa())
    monkeypatch.setattr(cli, "_verificar_esquema_o_salir", lambda conn: None)
    monkeypatch.setattr(reloj, "montar", _montar_falso)
    monkeypatch.setattr(uvicorn, "run", lambda *a, **k: None)

    assert cli.main(["servir", "--sin-cadencias"]) == 0
    assert llamadas == [{"con_cadencias": False}]


def test_servir_sin_el_flag_deja_las_cadencias_activas(monkeypatch):
    import uvicorn

    from leda import reloj

    llamadas = []

    def _montar_falso(conn_factory, **kw):
        llamadas.append(kw)
        return _SchedulerFalso()

    monkeypatch.setattr(cli, "conectar", lambda *a, **k: _ConnFalsa())
    monkeypatch.setattr(cli, "_verificar_esquema_o_salir", lambda conn: None)
    monkeypatch.setattr(reloj, "montar", _montar_falso)
    monkeypatch.setattr(uvicorn, "run", lambda *a, **k: None)

    assert cli.main(["servir"]) == 0
    assert llamadas == [{"con_cadencias": True}]


def test_servir_rechaza_arrancar_si_falta_una_migracion(monkeypatch):
    """R4-003 (revisión 2026-09-28+3): sin `greeting_state`/`message_outbox.
    es_bienvenida`, todo el mensajería rompe con UndefinedTable/
    UndefinedColumn en el primer envío -- `servir` no puede arrancar el
    scheduler ni el servidor si falta una migración."""
    import uvicorn

    from leda import reloj

    llamadas_montar = []
    llamadas_uvicorn = []

    monkeypatch.setattr(cli, "conectar", lambda *a, **k: _ConnFalsa())
    monkeypatch.setattr(cli, "_verificar_esquema_o_salir", lambda conn: 1)
    monkeypatch.setattr(reloj, "montar",
                        lambda *a, **k: llamadas_montar.append(1))
    monkeypatch.setattr(uvicorn, "run", lambda *a, **k: llamadas_uvicorn.append(1))

    assert cli.main(["servir"]) == 1
    assert llamadas_montar == []
    assert llamadas_uvicorn == []


def test_escuchar_rechaza_arrancar_si_falta_una_migracion(
        conn, corework, monkeypatch):
    from leda import local

    monkeypatch.setattr(cli, "conectar", lambda *a, **k: conn)
    monkeypatch.setattr(cli, "_verificar_esquema_o_salir", lambda conn: 1)
    llamadas = []
    monkeypatch.setattr(local, "escuchar", lambda *a, **k: llamadas.append(1))

    assert cli.main(["escuchar", "corework"]) == 1
    assert llamadas == []
