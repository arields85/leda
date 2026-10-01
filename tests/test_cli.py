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


class _ConnFalsa:
    def close(self) -> None:
        pass


def test_servir_sin_cadencias_llega_a_reloj_montar(monkeypatch):
    import uvicorn

    from prisma import reloj

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

    from prisma import reloj

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

    from prisma import reloj

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
    from prisma import local

    monkeypatch.setattr(cli, "conectar", lambda *a, **k: conn)
    monkeypatch.setattr(cli, "_verificar_esquema_o_salir", lambda conn: 1)
    llamadas = []
    monkeypatch.setattr(local, "escuchar", lambda *a, **k: llamadas.append(1))

    assert cli.main(["escuchar", "corework"]) == 1
    assert llamadas == []


def test_redaccion_imprime_la_latencia_y_los_rechazos_de_la_variante_a(
        conn, corework, monkeypatch, capsys):
    """F6a: cómo se lee la mediana de la prueba A/B, sin entrar a la base."""
    from prisma import redaccion
    from prisma.db import admin, registrar_auditoria

    monkeypatch.setattr(cli, "conectar", lambda *a, **k: conn)
    with admin(conn) as cur:
        for resultado, ms in (("aceptada", 1000), ("aceptada", 3000),
                              ("rechazada", 5000), ("error", 10000)):
            registrar_auditoria(
                cur, accion=redaccion.ACCION_REDACCION_A,
                workspace_id=corework.workspace_id, actor_kind="prisma",
                detalle={"resultado": resultado, "duracion_ms": ms,
                         "caracteres": 10})

    assert cli.main(["redaccion", "corework"]) == 0

    salida = capsys.readouterr().out
    assert "llamadas: 4" in salida
    assert "aceptadas: 2" in salida and "rechazadas: 1" in salida
    assert "errores: 1" in salida
    assert "mediana: 4,0 s" in salida


def test_redaccion_sin_intentos_no_inventa_una_mediana(conn, corework, monkeypatch,
                                                       capsys):
    monkeypatch.setattr(cli, "conectar", lambda *a, **k: conn)
    assert cli.main(["redaccion", "corework"]) == 0
    assert "Sin intentos de la variante A." in capsys.readouterr().out
