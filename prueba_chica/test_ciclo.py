"""El ciclo del motor (E2-6).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Entrada propia"): cada minuto corre la
escalera y los avisos guardados; cada vuelta del escuchador, el despacho y los avisos a la
administración. Cada paso va aislado: si uno se cae, deja un incidente (una vez mientras siga
cayéndose) y los demás corren igual. Nunca importa `leda.ciclo`, `leda.reloj` ni
`leda.escalera` (`test_frontera.py`). Reloj fijo, IA guionada, transportes de prueba.
"""

from __future__ import annotations

import json

import pytest

import prueba_chica.ciclo as ciclo_del_motor
from prueba_chica.ciclo import ETAPA_CICLO, Ciclo
from prueba_chica.ia import Jugada
from prueba_chica.test_avisos import _dice, _hora
from prueba_chica.test_escalera import IAQueRedacta, espacio_con_escalera  # noqa: F401
from prueba_chica.test_situaciones import _cuantas, _todos, _uno
from prueba_chica.tiempo import RelojFijo

from leda.db import admin, espacio
from leda.despachador import TransporteDePrueba
from leda.incidentes import registrar_incidente


class Monotono:
    """Los segundos que pasan entre vueltas, a mano."""

    def __init__(self) -> None:
        self.s = 0.0

    def __call__(self) -> float:
        return self.s


def _ciclo(conn, mundo, at, **opciones) -> tuple[Ciclo, TransporteDePrueba]:
    salida = TransporteDePrueba()
    opciones.setdefault("imprimir", lambda *_: None)
    return Ciclo(conn, mundo["id"], IAQueRedacta(), RelojFijo(at), salida, **opciones), salida


def _administrador(conn) -> None:
    """Un administrador de plataforma con su chat registrado: recibe los avisos."""
    with admin(conn) as cur:
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (90000, 'Admin') returning id""")
        quien = str(cur.fetchone()["id"])
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                    (quien,))
        cur.execute("""insert into audit_log (actor_app_user_id, actor_kind, accion, detalle)
                       values (%s, 'persona', 'mensaje_admin', %s)""",
                    (quien, json.dumps({"chat_id": 90000})))
    conn.commit()


# --- Lo que corre -------------------------------------------------------------------------------

def test_una_vuelta_corre_la_escalera_manda_lo_guardado_y_lo_despacha(conn, mundo,
                                                                     espacio_con_escalera):
    marcos = mundo["personas"]["Marcos"]
    ciclo, salida = _ciclo(conn, mundo, _hora(9, 10))

    resultado = ciclo.vuelta()

    assert resultado["escalera"] == {"pedido_de_estado": 1}
    assert resultado["avisos"] == {"enviado": 1}
    assert resultado["despacho"]["enviados"] == 1
    [entregado] = salida.enviados
    assert entregado.chat_id == marcos["telegram"] and entregado.texto == "Aviso 1."
    assert _uno(conn, "select estado from scheduled_notice")["estado"] == "enviado"


def test_la_escalera_y_los_avisos_corren_cada_minuto_y_el_despacho_cada_vuelta(
        conn, mundo, espacio_con_escalera, monkeypatch):
    llamadas: list[str] = []
    for nombre in ("correr_escalera", "enviar_avisos", "despachar"):
        original = getattr(ciclo_del_motor, nombre)
        monkeypatch.setattr(ciclo_del_motor, nombre,
                            lambda *a, _n=nombre, _o=original, **k: (llamadas.append(_n),
                                                                     _o(*a, **k))[1])
    reloj = Monotono()
    ciclo, _ = _ciclo(conn, mundo, _hora(9, 10), monotono=reloj)

    ciclo.vuelta()
    reloj.s = 30
    ciclo.vuelta()
    reloj.s = 60
    ciclo.vuelta()

    assert llamadas == ["correr_escalera", "enviar_avisos", "despachar", "despachar",
                        "correr_escalera", "enviar_avisos", "despachar"]


def test_sin_seguimiento_solo_despacha(conn, mundo, espacio_con_escalera):
    ciclo, salida = _ciclo(conn, mundo, _hora(9, 10), seguimiento=False)

    assert set(ciclo.vuelta()) == {"despacho"}
    assert _cuantas(conn, "scheduled_notice") == 0 and salida.enviados == []


def test_los_avisos_a_la_administracion_salen_con_el_reloj_real(conn, mundo):
    _administrador(conn)
    with espacio(conn, mundo["id"]) as cur:
        registrar_incidente(cur, mundo["id"], "Algo para avisar.", etapa=ETAPA_CICLO)
    conn.commit()
    salida_admin = TransporteDePrueba()
    ciclo, _ = _ciclo(conn, mundo, _hora(9, 10), transporte_admin=salida_admin)

    assert ciclo.vuelta(admin=False).keys() == {"escalera", "avisos", "despacho"}
    assert salida_admin.enviados == []
    assert ciclo.vuelta()["avisos_admin"]["enviados"] == 1
    assert [e.chat_id for e in salida_admin.enviados] == [90000]


# --- Cada paso, aislado ---------------------------------------------------------------------

PASOS = {"escalera": "correr_escalera", "avisos": "enviar_avisos", "despacho": "despachar",
         "avisos_admin": "despachar_avisos_admin"}


@pytest.mark.parametrize("paso", list(PASOS))
def test_un_paso_que_se_cae_no_frena_a_los_demas_y_deja_un_incidente(conn, mundo,
                                                                    espacio_con_escalera,
                                                                    monkeypatch, paso):
    _administrador(conn)
    llamadas: list[str] = []
    for nombre, funcion in PASOS.items():
        original = getattr(ciclo_del_motor, funcion)

        def espia(*a, _n=nombre, _o=original, **k):
            llamadas.append(_n)
            if _n == paso:
                raise RuntimeError("se cayó la base")
            return _o(*a, **k)
        monkeypatch.setattr(ciclo_del_motor, funcion, espia)
    impreso: list[str] = []
    reloj = Monotono()
    ciclo, _ = _ciclo(conn, mundo, _hora(9, 10), transporte_admin=TransporteDePrueba(),
                      monotono=reloj, imprimir=impreso.append)

    resultado = ciclo.vuelta()

    assert llamadas == list(PASOS)                       # los demás corrieron igual
    assert resultado[paso] is None
    [incidente] = _todos(conn, "select * from incident")
    assert incidente["etapa"] == ETAPA_CICLO and incidente["severidad"] == "alta"
    assert paso in incidente["resumen_sanitizado"]
    # El error, sin su texto crudo (`despachador.texto_error_seguro`).
    assert incidente["referencia_cruda"] == "RuntimeError"
    assert any(paso in linea for linea in impreso)      # y en la consola del escuchador
    # El administrador se entera; si lo que se cayó es su canal, no se le avisa por él.
    assert _cuantas(conn, "admin_notice") == (0 if paso == "avisos_admin" else 1)

    reloj.s = 60
    ciclo.vuelta()                                       # sigue cayéndose: no otro incidente
    assert _cuantas(conn, "incident") == 1


def test_un_paso_que_vuelve_a_andar_y_se_cae_de_nuevo_deja_otro_incidente(
        conn, mundo, espacio_con_escalera, monkeypatch):
    falla = {"ahora": True}
    original = ciclo_del_motor.correr_escalera

    def escalera(*a, **k):
        if falla["ahora"]:
            raise RuntimeError("caída")
        return original(*a, **k)
    monkeypatch.setattr(ciclo_del_motor, "correr_escalera", escalera)
    reloj = Monotono()
    ciclo, _ = _ciclo(conn, mundo, _hora(9, 10), monotono=reloj)

    ciclo.vuelta()
    falla["ahora"] = False
    reloj.s = 60
    assert ciclo.vuelta()["escalera"] == {"pedido_de_estado": 1}
    falla["ahora"] = True
    reloj.s = 120
    ciclo.vuelta()

    assert _cuantas(conn, "incident") == 2


def test_lo_que_causa_un_turno_sale_con_el_ciclo(conn, mundo, escribe):
    """El aviso al referente de una previsión lo manda el ciclo, no el comando."""
    _dice(conn, escribe, Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-14"}))
    ciclo, salida = _ciclo(conn, mundo, _hora(5, 10, 1))

    ciclo.vuelta()

    ismael = mundo["personas"]["Ismael"]["telegram"]
    assert [e.chat_id for e in salida.enviados if e.chat_id == ismael] == [ismael]


# --- En el escuchador ---------------------------------------------------------------------------

def test_el_escuchador_corre_el_ciclo_en_cada_vuelta(conn, mundo, espacio_con_escalera):
    import httpx

    from prueba_chica.escuchar import BotTelegram, Escucha
    from prueba_chica.test_escuchar import TelegramFalso

    salida = TransporteDePrueba()
    escucha = Escucha(conn, mundo["id"], IAQueRedacta(), RelojFijo(_hora(9, 10)),
                      bot=BotTelegram("token-falso",
                                      httpx.Client(transport=httpx.MockTransport(
                                          TelegramFalso()))),
                      transporte=salida, seguimiento=True, imprimir=lambda *_: None)
    escucha.preparar()

    escucha.una_vuelta(espera=0)

    assert [e.texto for e in salida.enviados] == ["Aviso 1."]
    assert _uno(conn, "select tipo from scheduled_notice")["tipo"] == "pedido_de_estado"
