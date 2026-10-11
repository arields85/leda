"""Las jugadas de un mensaje se aplican en orden (tercera vuelta de ajuste, usuario, 2026-10-06;
ADR 0018, decisión 9).

Una frase puede traer dos hechos distintos, cada uno en su jugada: "falta que martin de IT me
habilite el acceso" es la causa de un bloqueo y, a la vez, quién lo destraba (conversación 05,
paso 5). Las jugadas de un mensaje se aplican en el orden en que vienen, en la misma
transacción, así que una jugada posterior se apoya en lo que anotó una anterior: el bloqueo que
anotó la primera es el bloqueo abierto de la segunda, con su tarea o sin ella (por la pregunta
de quién lo destraba que abrió la primera). La regla vale para cualquier par de jugadas, no para
una conversación.

Lo que impide anotar dos veces una misma cosa (conversación 11, paso 3: una previsión con su
porqué no es además un bloqueo) son las definiciones de las jugadas, no una regla de "una sola
jugada": la IA guionada elige las jugadas naturales y el código hace lo de cada una.
"""

from __future__ import annotations

from leda.motor.fichas import FICHAS
from leda.motor.hechos import sin_significado
from leda.motor.ia import Jugada
from leda.motor.instrucciones import INSTRUCCIONES_JUGADAS

from tests.motor.ayudantes import dice, no_es_del_equipo, octubre, uno

CAUSA = "falta que martin de IT me habilite el acceso a la red de planta"


def _bloqueo() -> Jugada:
    return Jugada("anotar_bloqueo", {"tarea": "T1", "causa": CAUSA})


def _destraba(**datos) -> Jugada:
    return Jugada("anotar_quien_destraba", {"quien": "martin de IT", **datos})


def _pregunta_de_quien_destraba(conn) -> dict | None:
    return uno(conn, """select cerrada_en, cierre from conversation_question
                          where tipo = 'quien_destraba' order by abierta_en desc limit 1""")


def test_la_causa_y_quien_destraba_en_una_frase_se_anotan_las_dos(conn, mundo, escribe):
    resultado = dice(conn, escribe, _bloqueo(), _destraba(tarea="T1"), at=octubre(6, 16, 35))

    bloqueo, destraba = resultado.hechos
    assert bloqueo["resultado"] == "anotado"
    # "martin de IT" no es nadie del equipo: antes de anotarlo, Leda pregunta quién es (decisión
    # 65 del usuario, 2026-10-11); la pregunta de quién lo destraba espera esa respuesta.
    assert (destraba["resultado"], destraba["falta"]) == ("falta_dato", ["quien_es"])
    assert resultado.pregunta["tipo"] == "quien_es_esa_persona"
    assert _pregunta_de_quien_destraba(conn)["cerrada_en"] is None
    assert sin_significado(resultado.hechos) == set()

    resultado = dice(conn, escribe, no_es_del_equipo(), at=octubre(6, 16, 37))

    [destraba] = resultado.hechos
    assert destraba["resultado"] == "anotado"
    assert destraba["quien_destraba"] == {"externo": "martin de IT"}
    assert "salidas" not in destraba
    assert resultado.pregunta is None
    assert _pregunta_de_quien_destraba(conn)["cerrada_en"] is not None
    assert uno(conn, "select destraba_externo from blocker_unblocker")["destraba_externo"] \
        == "martin de IT"
    assert sin_significado(resultado.hechos) == set()


def test_quien_destraba_sin_tarea_se_apoya_en_el_bloqueo_que_anoto_la_jugada_anterior(
        conn, mundo, escribe):
    resultado = dice(conn, escribe, _bloqueo(), _destraba(), at=octubre(6, 16, 35))

    _, destraba = resultado.hechos
    # Encontró el bloqueo de T1 (sin él diría `sin_bloqueo_abierto`); como "martin de IT" no es
    # nadie del equipo, pregunta quién es antes de anotarlo (decisión 65).
    assert destraba["resultado"] == "falta_dato"
    assert destraba["tarea"]["alias"] == "T1"
    assert resultado.pregunta["tipo"] == "quien_es_esa_persona"


def test_destrabar_se_apoya_en_el_bloqueo_que_anoto_la_jugada_anterior(conn, mundo, escribe):
    """Trabarse y destrabarse en un mismo mensaje: el orden de las jugadas manda."""
    resultado = dice(conn, escribe, _bloqueo(), Jugada("destrabar", {"tarea": "T1"}),
                     at=octubre(6, 16, 35))

    bloqueo, destrabe = resultado.hechos
    assert bloqueo["resultado"] == destrabe["resultado"] == "anotado"
    assert destrabe["bloqueo_resuelto"] == {"causa": CAUSA}
    assert uno(conn, "select estado from task where id = %s",
               mundo["tarea"])["estado"] == "asignada"
    assert resultado.pregunta is None


def test_el_orden_importa_quien_destraba_antes_del_bloqueo_no_tiene_bloqueo(conn, mundo,
                                                                           escribe):
    """En el orden inverso, la segunda jugada no ve nada que no exista todavía: lo dice."""
    resultado = dice(conn, escribe, _destraba(tarea="T1"), _bloqueo(), at=octubre(6, 16, 35))

    destraba, bloqueo = resultado.hechos
    assert destraba == {"jugada": "anotar_quien_destraba", "resultado": "no_se_puede",
                        "motivo": "sin_bloqueo_abierto",
                        "tarea": {"alias": "T1", "titulo": "Revisar el tablero"}}
    assert bloqueo["resultado"] == "anotado"


# --- Lo que dicen las instrucciones y las fichas ---------------------------------------------

def test_las_instrucciones_describen_jugadas_en_orden_sin_la_regla_de_una_sola_jugada():
    assert "una sola jugada" not in INSTRUCCIONES_JUGADAS
    assert "nunca se anota como dos hechos" not in INSTRUCCIONES_JUGADAS
    assert "en orden" in INSTRUCCIONES_JUGADAS
    assert "anterior" in INSTRUCCIONES_JUGADAS


def test_las_jugadas_sobre_un_bloqueo_admiten_el_que_anota_el_mismo_mensaje():
    for nombre in ("anotar_quien_destraba", "destrabar"):
        assert "mismo mensaje" in FICHAS[nombre].es, nombre



# --- Revisión de `f0d18e6`: lo que se difiere y lo que no (ADR 0018, 9m.1) ----------------------
#
# Una jugada que mira cómo está otra tarea de quien escribe (`Ficha.mira_otra_tarea`) se maneja
# después de las demás del mensaje. El resto conserva su orden entre sí, así que lo que una jugada
# anota sigue estando para las que vienen después; dos diferidas conservan el suyo; y los hechos
# quedan en el orden en que la persona lo dijo.

def _enlazada(tarea: str) -> Jugada:
    return Jugada("decir_cuando_destraba", {"tarea": tarea, "su_tarea_trabada": "T1",
                                            "lo_que_dice": "todavia no la tengo"})


def test_las_que_miran_otra_tarea_van_al_final_en_su_orden():
    from leda.motor.fichas import en_orden

    jugadas = [_enlazada("T2"), _bloqueo(), _enlazada("T3"), _destraba(tarea="T1"),
               Jugada("decir_cuando_destraba", {"tarea": "T4", "lo_que_dice": "el lunes"})]

    assert en_orden(jugadas) == [1, 3, 4, 0, 2]


def test_diferir_no_cambia_lo_que_ven_las_demas_y_los_hechos_quedan_como_se_dijeron():
    """Con manejadores que anotan lo que ven: cada jugada no diferida ve lo de las anteriores
    no diferidas, como sin diferir; las diferidas ven todo el mensaje y conservan su orden."""
    from types import SimpleNamespace

    from leda.motor.turno import _manejar_todas

    vistos: list[tuple[str, tuple[str, ...]]] = []

    def anota(ctx, jugada):
        clave = f"{jugada.nombre}:{(jugada.datos or {}).get('tarea')}"
        vistos.append((clave, tuple(ctx.anotado)))
        ctx.anotado.append(clave)
        return {"jugada": jugada.nombre, "tarea": (jugada.datos or {}).get("tarea")}

    jugadas = {n: anota for n in ("decir_cuando_destraba", "anotar_bloqueo",
                                  "anotar_quien_destraba")}
    elegidas = [_enlazada("T2"), _bloqueo(), _enlazada("T3"), _destraba(tarea="T1")]

    hechos = _manejar_todas(SimpleNamespace(anotado=[]), elegidas, jugadas)

    assert vistos == [
        ("anotar_bloqueo:T1", ()),
        ("anotar_quien_destraba:T1", ("anotar_bloqueo:T1",)),
        ("decir_cuando_destraba:T2", ("anotar_bloqueo:T1", "anotar_quien_destraba:T1")),
        ("decir_cuando_destraba:T3", ("anotar_bloqueo:T1", "anotar_quien_destraba:T1",
                                      "decir_cuando_destraba:T2"))]
    assert [(h["jugada"], h["tarea"]) for h in hechos] == [
        ("decir_cuando_destraba", "T2"), ("anotar_bloqueo", "T1"),
        ("decir_cuando_destraba", "T3"), ("anotar_quien_destraba", "T1")]
