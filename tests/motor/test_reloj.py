"""El reloj de Leda en `leda_motor` (`leda.motor.reloj`; diseño probado en la Etapa 2, E2-6;
decisión del usuario 10.2).

`odd/tasks/prueba-chica-del-motor.md`, sección 10: para la prueba por Telegram, un comando
adelanta el reloj de Leda al día hábil siguiente a las 10:00, sólo en `leda_motor` y con la
restricción de horario prendida, para que los días hábiles, el atraso y el horario salgan bien.
El adelanto se guarda en el espacio (`workspace_setting`) y lo leen el escuchador y su ciclo: la
escalera, los avisos y el horario del despacho ven el mismo momento. La base de las pruebas no
es `leda_motor`: cada prueba nombra la suya, y las que no lo hacen comprueban que se niega.

Portadas de `prueba_chica/test_reloj.py`; la del reloj adelantado que mueve la escalera y el
horario del despacho juntos pasa por el escuchador del motor (E3-7).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from leda.db import admin
from leda.despachador import TransporteDePrueba
from leda.motor.escucha import BotTelegram, Escucha
from leda.motor.reloj import CLAVE_ADELANTO, BaseEquivocada, RelojDeLeda, adelantar, estado, volver
from leda.motor.tiempo import RelojFijo

from tests.motor.ayudantes import IAQueRedacta, Monotono, TelegramFalso, cuantas, octubre, uno


VIERNES_18 = octubre(9, 18)        # fuera del horario; el lunes 12 es feriado


def test_adelantar_va_al_dia_habil_siguiente_a_las_10_y_volver_al_tiempo_real(
        conn, mundo, espacio_con_escalera):
    base = conn.info.dbname
    real = RelojFijo(VIERNES_18)

    primero = adelantar(conn, mundo["id"], real, base=base)

    assert primero.leda == octubre(13, 10)             # salta el fin de semana y el feriado
    assert primero.adelanto == octubre(13, 10) - VIERNES_18
    assert primero.en_horario and primero.restriccion_prendida
    fila = uno(conn, "select valor from workspace_setting where clave = %s", CLAVE_ADELANTO)
    assert fila["valor"] == int(primero.adelanto.total_seconds())
    assert estado(conn, mundo["id"], real, base=base) == primero

    assert adelantar(conn, mundo["id"], real, base=base).leda == octubre(14, 10)

    vuelto = volver(conn, mundo["id"], real, base=base)
    assert vuelto.adelanto == timedelta(0) and vuelto.leda == VIERNES_18
    assert cuantas(conn, "workspace_setting", f"clave = '{CLAVE_ADELANTO}'") == 0


def test_el_reloj_de_leda_corre_con_el_tiempo_real(conn, mundo):
    real = RelojFijo(octubre(5, 10))
    adelantar(conn, mundo["id"], real, base=conn.info.dbname)
    reloj = RelojDeLeda(real=real, base=conn.info.dbname)
    reloj.refrescar(conn, mundo["id"])

    assert reloj.ahora() == octubre(6, 10)
    real.momento += timedelta(minutes=5)
    assert reloj.ahora() == octubre(6, 10, 5)


def test_el_reloj_adelantado_mueve_la_escalera_y_el_horario_del_despacho_juntos(
        conn, mundo, espacio_con_escalera):
    """El viernes a las 18:00 la escalera guarda el primer pedido, pero nada sale: está fuera
    del horario. Adelantado al martes 13 a las 10:00, el pedido sale con el atraso de ese día y
    el despacho lo manda, con la restricción de horario prendida."""
    base = conn.info.dbname
    real = RelojFijo(VIERNES_18)
    salida = TransporteDePrueba()
    ia = IAQueRedacta()
    escucha = Escucha(conn, mundo["id"], ia, RelojDeLeda(real=real, base=base),
                      bot=BotTelegram("token-falso", TelegramFalso().cliente()),
                      transporte=salida, seguimiento=True, imprimir=lambda *_: None)
    escucha.ciclo.monotono = minuto = Monotono()
    escucha.preparar()

    escucha.una_vuelta(espera=0)
    assert salida.enviados == [] and ia.pedidos_de_redaccion == []
    assert uno(conn, "select programado_para from scheduled_notice")["programado_para"] \
        == octubre(13, 10)

    adelantar(conn, mundo["id"], real, base=base)
    minuto.s = 60
    escucha.una_vuelta(espera=0)

    [pedido] = ia.pedidos_de_redaccion
    assert pedido["hoy"] == "2026-10-13" and pedido["hechos"][0]["atraso_dias_habiles"] == 1
    assert [e.texto for e in salida.enviados] == ["Aviso 1."]
    assert uno(conn, "select enviado_en from message_outbox")["enviado_en"] == octubre(13, 10)


# --- Sólo en `leda_motor` ---------------------------------------------------------------------

def test_los_comandos_se_niegan_en_otra_base(conn, mundo):
    real = RelojFijo(VIERNES_18)
    for comando in (adelantar, estado, volver):
        with pytest.raises(BaseEquivocada, match="leda_motor"):
            comando(conn, mundo["id"], real)
    assert cuantas(conn, "workspace_setting") == 0


def test_fuera_de_leda_motor_el_reloj_no_se_adelanta(conn, mundo):
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, %s, '86400')""", (mundo["id"], CLAVE_ADELANTO))
    conn.commit()
    real = RelojFijo(datetime(2026, 10, 5, 13, 0, tzinfo=timezone.utc))
    reloj = RelojDeLeda(real=real)

    reloj.refrescar(conn, mundo["id"])

    assert reloj.adelanto == timedelta(0) and reloj.ahora() == real.momento


def test_a_la_hora_lleva_el_reloj_a_esa_hora_del_mismo_dia_y_nunca_para_atras(
        conn, mundo, espacio_con_escalera):
    """Para probar de noche sin esperar (pedido del usuario, 2026-10-07): el reloj de Leda va a
    una hora del día en que está. Nunca para atrás: lo ya registrado quedaría en el futuro."""
    from datetime import time

    from leda.motor.reloj import HoraAtrasada, a_la_hora

    base = conn.info.dbname
    real = RelojFijo(VIERNES_18)
    adelantar(conn, mundo["id"], real, base=base)                  # martes 13, 10:00

    noche = a_la_hora(conn, mundo["id"], real, time(22, 30), base=base)

    assert noche.leda == octubre(13, 10) + timedelta(hours=12, minutes=30)   # 22:30
    assert not noche.en_horario
    with pytest.raises(HoraAtrasada):
        a_la_hora(conn, mundo["id"], real, time(9, 0), base=base)
