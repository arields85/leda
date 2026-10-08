"""Los contratos puros del motor: el reloj y la hora de salida (`tiempo`), la IA guionada de las
pruebas (`ia`) y el tono del espacio para la redacción (`instrucciones`).
"""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.motor.ia import GuionAgotado, IAGuionada, Jugada
from leda.motor.instrucciones import (INSTRUCCIONES_JUGADAS, INSTRUCCIONES_REDACCION, Tono,
                                      bloque_de_tono, tono_del_espacio)
from leda.motor.tiempo import HORA_DE_SALIDA, RelojFijo, RelojDelSistema, sale, sale_el

from tests.motor.ayudantes import AHORA

BA = ZoneInfo("America/Argentina/Buenos_Aires")


def _cal(conn, mundo) -> Calendario:
    with espacio(conn, mundo["id"]) as cur:
        return Calendario.desde_base(cur, mundo["id"])


def _local(dia: int, hora: int, minuto: int = 0) -> datetime:
    return datetime(2026, 10, dia, hora, minuto, tzinfo=BA)


def test_lo_que_leda_manda_por_su_cuenta_sale_a_la_hora_de_salida(conn, mundo):
    cal = _cal(conn, mundo)                       # lunes a viernes, 9 a 17
    assert HORA_DE_SALIDA.hour == 10
    assert sale(cal, _local(5, 8)) == _local(5, 10)           # todavía no llegó: a las 10
    assert sale(cal, _local(5, 11, 30)) == _local(5, 11, 30)  # ya pasó, en jornada: enseguida
    assert sale(cal, _local(5, 18)) == _local(6, 10)          # terminó la jornada: mañana
    assert sale(cal, _local(10, 11)) == _local(12, 10)        # sábado: el lunes
    assert sale_el(cal, _local(9, 0).date()) == _local(9, 10)


def test_los_relojes():
    fijo = RelojFijo(AHORA)
    assert (fijo.ahora(), fijo.medir()) == (AHORA, 0.0)
    sistema = RelojDelSistema()
    assert sistema.ahora().tzinfo is timezone.utc
    assert sistema.medir() <= sistema.medir()


def test_la_ia_guionada_devuelve_lo_preparado_en_orden_y_guarda_los_pedidos():
    ia = IAGuionada(jugadas=[[Jugada("iniciar_tarea", {"tarea": "T1"})], RuntimeError("caída")],
                    redacciones=["Anotado."])
    assert ia.elegir_jugadas({"mensaje": "arranqué"}) == [Jugada("iniciar_tarea",
                                                                 {"tarea": "T1"})]
    with pytest.raises(RuntimeError, match="caída"):
        ia.elegir_jugadas({"mensaje": "otra vez"})
    assert ia.redactar({"hechos": []}) == "Anotado."
    with pytest.raises(GuionAgotado):
        ia.redactar({"hechos": []})
    assert [p["mensaje"] for p in ia.pedidos_de_jugadas] == ["arranqué", "otra vez"]
    assert len(ia.pedidos_de_redaccion) == 2


def test_el_tono_sale_del_pack_del_espacio(conn, mundo):
    with admin(conn) as cur:
        cur.execute("""update persona_config set nombre_visible = 'Leda', emojis = true
                        where workspace_id = %s""", (mundo["id"],))
    with espacio(conn, mundo["id"]) as cur:
        tono = tono_del_espacio(cur, mundo["id"])
    assert tono == Tono(nombre_visible="Leda", registro="vos",
                        formalidad="profesional_cordial", longitud="breve", emojis=True)
    assert bloque_de_tono(tono).splitlines() == [
        "Tono de este equipo:", "- Nombre: Leda.", "- Trato: de vos.",
        "- Formalidad: profesional cordial.", "- Longitud: breve.",
        "- Emojis, fuera de las marcas del formato: permitidos."]
    # Sin emojis en el tono, las marcas del formato siguen (segunda vuelta, 2026-10-07).
    assert bloque_de_tono(Tono(emojis=False)).splitlines()[-1] == (
        "- Emojis, fuera de las marcas del formato: no.")


def test_sin_tono_propio_no_se_inventa_un_trato():
    assert bloque_de_tono(None) == ("Tono de este equipo:\n"
                                    "- Sin tono propio: trato neutro y cordial.")


def test_las_instrucciones_son_las_que_pasaron_la_prueba_real():
    """Se portaron sin tocar una palabra: cambiarlas es cambiar lo que se probó."""
    import hashlib

    huellas = {nombre: hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]
               for nombre, texto in (("jugadas", INSTRUCCIONES_JUGADAS),
                                     ("redaccion", INSTRUCCIONES_REDACCION))}
    assert huellas == HUELLAS_DE_LA_PRUEBA_REAL


# Las de `prueba_chica/instrucciones.py`, la ronda 3 (85 de 85) y la prueba por Telegram; la
# de la redacción cambió a propósito el 2026-10-07 con una sola regla, decidida por el usuario
# el 2026-10-06 tras la prueba por Telegram: Leda cuenta lo que pasa en el mundo (quién se
# entera de qué y cuándo), no el estado de la cocina (conversación 18). Antes: "e5c5767b4f7312fd".
# Y otra vez a propósito el 2026-10-07, con otra sola regla decidida por el usuario ese día tras
# la prueba por Telegram ("que es prevision?"): Leda dice el hecho concreto con palabras de todos
# los días y nunca nombra un concepto del sistema (conversación 19). Antes: "3deabdc072e8045d".
# Y otra vez a propósito el 2026-10-07, con el formato de los mensajes pedido por el usuario al
# aprobar M3: negrita para las tareas y lo importante, párrafos y viñetas, en lugar de "sin
# Markdown" (conversación 20). Antes: "11fb65a678d82884".
# Y otra vez a propósito el 2026-10-07, con la segunda vuelta del formato, decidida por el usuario
# después de verlo en Telegram: sin negrita, un renglón por idea, cuatro marcas fijas (📋 ✏️ 📅
# ⚠️) que van aunque el tono no lleve emojis, el título completo una sola vez, fechas cortas
# (`hechos.dia_corto`) y el cierre aparte, al final (conversación 20). Antes: "66f8a2e23d9bbbd9".
# Y otra vez a propósito el 2026-10-07, con la tercera vuelta del formato, decidida por el usuario
# después de la segunda prueba por Telegram: 🗓️ en vez de 📅, el renglón de la tarea primero en su
# bloque, las marcas sólo al principio del renglón y quien se entera, en voz pasiva (conversación
# 20). Antes: "d546932a0f6b9262".
# Y otra vez a propósito el 2026-10-08, con la decisión 11 del usuario: Leda no nombra por su
# cuenta a quien aprueba el trabajo de la persona, que le llega a la redacción en
# `solo_si_pregunta`; la voz pasiva de quien se entera tiene como sujeto a esa persona sólo si
# un hecho la nombra a la vista, y si no, lo que se informa (la regla anterior, "con esa
# persona como sujeto del verbo notificar", pedía el nombre). Antes: "d8c6b0de58c4c2a3".
HUELLAS_DE_LA_PRUEBA_REAL = {"jugadas": "8b25f19b4bfe9b8a", "redaccion": "3f267a24d030de4a"}
