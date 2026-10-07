"""`cli.py` no tenía ninguna prueba (docs/capacidades.md, "Trampas
conocidas"). Estas cubren sólo el cableado de `servir`, `webhooks` y
`escuchar` -- nunca tocan Telegram, uvicorn ni un hilo de fondo real."""

from __future__ import annotations

from leda import cli


class _SchedulerFalso:
    def start(self) -> None:
        pass


class _ConnFalsa:
    def close(self) -> None:
        pass


def test_servir_arranca_el_ciclo_del_motor_y_el_servidor(monkeypatch):
    """E3-7: `servir` corre el ciclo del motor en un hilo de fondo (`leda.motor.fondo`), no
    el reloj ni el ciclo viejos, retirados con sus cadencias."""
    import uvicorn

    from leda.motor import fondo

    llamadas = []

    def _montar_falso(conn_factory, **kw):
        llamadas.append(kw)
        return _SchedulerFalso()

    monkeypatch.setattr(cli, "conectar", lambda *a, **k: _ConnFalsa())
    monkeypatch.setattr(cli, "_verificar_esquema_o_salir", lambda conn: None)
    monkeypatch.setattr(fondo, "montar", _montar_falso)
    monkeypatch.setattr(uvicorn, "run", lambda *a, **k: llamadas.append(a))

    assert cli.main(["servir"]) == 0
    assert llamadas == [{}, ("leda.entrada:app",)]


def test_servir_rechaza_arrancar_si_falta_una_migracion(monkeypatch):
    """R4-003 (revisión 2026-09-28+3): sin `greeting_state`/`message_outbox.
    es_bienvenida`, todo el mensajería rompe con UndefinedTable/
    UndefinedColumn en el primer envío -- `servir` no puede arrancar el
    ciclo de fondo ni el servidor si falta una migración."""
    import uvicorn

    from leda.motor import fondo

    llamadas_montar = []
    llamadas_uvicorn = []

    monkeypatch.setattr(cli, "conectar", lambda *a, **k: _ConnFalsa())
    monkeypatch.setattr(cli, "_verificar_esquema_o_salir", lambda conn: 1)
    monkeypatch.setattr(fondo, "montar",
                        lambda *a, **k: llamadas_montar.append(1))
    monkeypatch.setattr(uvicorn, "run", lambda *a, **k: llamadas_uvicorn.append(1))

    assert cli.main(["servir"]) == 1
    assert llamadas_montar == []
    assert llamadas_uvicorn == []


def test_webhooks_registra_cada_bot_y_falla_si_telegram_no_acepta_alguno(monkeypatch, capsys):
    from leda import entrada

    monkeypatch.setattr(entrada, "registrar_webhooks",
                        lambda: {"corework": True, "admin": False})

    assert cli.main(["webhooks"]) == 1
    salida = capsys.readouterr().out
    assert "corework" in salida and "registrado" in salida and "no lo aceptó" in salida


def test_webhooks_sin_direccion_o_secreto_no_registra_nada(monkeypatch, capsys):
    from leda import entrada

    def _sin_configurar():
        raise LookupError("Faltan LEDA_BASE_URL o LEDA_WEBHOOK_SECRET en el entorno.")

    monkeypatch.setattr(entrada, "registrar_webhooks", _sin_configurar)

    assert cli.main(["webhooks"]) == 1
    assert "LEDA_WEBHOOK_SECRET" in capsys.readouterr().out


def test_escuchar_corre_el_escuchador_del_motor_con_el_espacio(monkeypatch):
    """E3-7: `escuchar` es el escuchador del motor (`leda.motor.escucha`), no el de los
    flujos viejos; abre su propia conexión, así que el comando no abre otra."""
    from leda.motor import escucha

    llamadas = []
    monkeypatch.setattr(escucha, "main", lambda argv: llamadas.append(argv) or 0)
    monkeypatch.setattr(cli, "conectar", lambda *a, **k: (_ for _ in ()).throw(
        AssertionError("escuchar no abre una conexión propia")))

    assert cli.main(["escuchar", "corework"]) == 0
    assert llamadas == [["corework"]]
