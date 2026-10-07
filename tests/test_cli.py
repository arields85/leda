"""`cli.py` no tenía ninguna prueba (docs/capacidades.md, "Trampas
conocidas"). Estas cubren sólo el cableado de `servir`, `webhooks` y
`escuchar` -- nunca tocan Telegram, uvicorn ni un hilo de fondo real."""

from __future__ import annotations

import pytest

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


# --- `modelo`: los parámetros del modelo (E3-8) -----------------------------------------------
#
# Producción configura un modelo de `nan` igual que el corredor de las conversaciones: con los
# mismos parámetros, revisados igual (`leda.motor.ia_real.validar_parametros`). Uno que no vale
# no se guarda y el modelo activo queda como estaba.

SIN_RAZONAR = {"cuerpo_extra": {"reasoning_effort": "low"}, "timeout_s": 60, "plazo_s": 90}


def _modelos(conn) -> list[dict]:
    from leda.db import admin

    with admin(conn) as cur:
        cur.execute("select proveedor, modelo, parametros, activo from model_config "
                    "where ambito = 'global' order by activo")
        filas = cur.fetchall()
    conn.commit()
    return filas


def test_modelo_guarda_sus_parametros_y_el_motor_los_usa(conn, monkeypatch, capsys):
    import json

    from leda.db import admin
    from leda.motor.ia_real import desde_base

    monkeypatch.setattr(cli, "conectar", lambda: conn)

    assert cli.main(["modelo", "glm5.3-flash", "--proveedor", "nan",
                     "--parametros", json.dumps(SIN_RAZONAR)]) == 0

    [fila] = _modelos(conn)
    assert (fila["proveedor"], fila["modelo"], fila["activo"]) == ("nan", "glm5.3-flash", True)
    assert fila["parametros"] == SIN_RAZONAR          # lo escrito, sin los de omisión
    assert "reasoning_effort" in capsys.readouterr().out

    class _Claves:
        def clave_llm(self, proveedor):
            return "clave-de-prueba"

    with admin(conn) as cur:
        ia = desde_base(cur, "00000000-0000-0000-0000-000000000000", _Claves())
    assert ia.cliente.parametros["cuerpo_extra"] == {"reasoning_effort": "low"}
    assert ia.cliente.http.timeout.read == 60


def test_modelo_sin_parametros_guarda_ninguno(conn, monkeypatch):
    monkeypatch.setattr(cli, "conectar", lambda: conn)
    assert cli.main(["modelo", "openai/gpt-6-sol", "--proveedor", "openrouter"]) == 0
    [fila] = _modelos(conn)
    assert fila["parametros"] == {}


def test_modelo_con_parametros_que_no_valen_no_cambia_nada(conn, monkeypatch, capsys):
    monkeypatch.setattr(cli, "conectar", lambda: conn)
    assert cli.main(["modelo", "openai/gpt-6-sol", "--proveedor", "openrouter"]) == 0
    capsys.readouterr()

    for texto, nombrado in (('{"plazo_s": 0}', "plazo_s"),
                            ('{"cuerpo_extra": {"model": "otro"}}', "model"),
                            ('{"plazo": 90}', "plazo"),
                            ("{no es json", "JSON"),
                            ("[1]", "objeto")):
        assert cli.main(["modelo", "glm5.3-flash", "--proveedor", "nan",
                         "--parametros", texto]) == 1
        assert nombrado in capsys.readouterr().out
        [fila] = _modelos(conn)                      # el de antes, activo y sin tocar
        assert (fila["modelo"], fila["activo"]) == ("openai/gpt-6-sol", True)


def test_modelo_con_parametros_sin_identificador_no_los_ignora(monkeypatch, capsys):
    monkeypatch.setattr(cli, "conectar", lambda: pytest.fail("no debía abrir la base"))
    assert cli.main(["modelo", "--parametros", '{"plazo_s": 90}']) == 1
    assert "--parametros" in capsys.readouterr().out
