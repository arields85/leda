"""Lo que espera una confirmación o un dato no quedó anotado (T7 de las correcciones de la
prueba por Telegram del 2026-10-12; conversación 51).

En la prueba, Ariel empezó una entrega ("termine la integracion…") y, con la entrega todavía sin
confirmar, escribió "no, mejor dejalo pendiente, después lo hago". La IA lo leyó como corregir y
no como cancelar, porque su ficha decía que dejar sin efecto algo dicho antes "es corregirlo";
pero lo de Ariel nunca quedó anotado: vivía sólo en la pregunta abierta. La cocina contestó a
ese corregir sin nada que corregir con otra pregunta ("falta saca") y Leda preguntó qué sacar.
Y antes, del borrador, Leda había escrito "✏️ Anoté que terminaste…": los hechos de una entrega
sin confirmar no decían que nada quedó anotado.

La regla, general: un hecho cuya pregunta espera una confirmación o un dato para anotar lo que la
persona dijo (la entrega, el pase) lo dice (`todavia_no_quedo_anotado`); dejarlo todo es
cancelar la pregunta, y un corregir sin nada que corregir sobre un borrador no abre otra
pregunta: dice lo que se mostraba y que no se anotó nada, y la pregunta abierta sigue siendo el
tema (ADR 0018, decisión 4 y la 9d).
"""

from __future__ import annotations

from leda.motor import hechos
from leda.motor.fichas import FICHAS
from leda.motor.ia import Jugada

from tests.motor.ayudantes import cuantas, estado_de
from tests.motor.test_entrega import JPEG, _entregar, _hecho, _tarea, marcos  # noqa: F401

TODAVIA_NO_QUEDO_ANOTADO = "todavia_no_quedo_anotado"


def _a_medias(marcos) -> dict:
    """Una entrega a la que le falta la foto: el borrador, con su pregunta de lo que falta."""
    return _hecho(marcos.manda(_entregar(el_texto_cubre=["explicacion"]),
                               texto="termine el tablero, quedo cerrado"), "entregar")


# --- Lo que dicen los hechos de un borrador -------------------------------------------------

def test_una_entrega_a_la_que_le_falta_algo_dice_que_todavia_no_quedo_anotada(conn, mundo,
                                                                              marcos):
    tarea = _tarea(conn, mundo)
    hecho = _a_medias(marcos)

    assert hecho["resultado"] == "le_falta_evidencia"
    assert hecho[TODAVIA_NO_QUEDO_ANOTADO] is True
    assert estado_de(conn, tarea) == "en_curso" and cuantas(conn, "evidence") == 0
    # Llega a la redacción con su significado, que dice que nada quedó anotado.
    assert hechos.para_redactar(hecho)[TODAVIA_NO_QUEDO_ANOTADO] is True
    assert "anotado" in hechos.significado(TODAVIA_NO_QUEDO_ANOTADO)
    assert not hechos.sin_significado(hechos.para_redactar(hecho))


def test_la_vista_previa_para_confirmar_tambien_dice_que_todavia_no_quedo_anotada(conn, mundo,
                                                                                 marcos):
    _tarea(conn, mundo)
    hecho = _hecho(marcos.manda(_entregar(el_texto_cubre=["explicacion"]),
                                texto="termine el tablero", archivos=[(JPEG, "foto", None)]),
                   "entregar")

    assert hecho["resultado"] == "para_confirmar"
    assert hecho[TODAVIA_NO_QUEDO_ANOTADO] is True
    # Confirmada, sí quedó: el hecho de la entrega ya no lo dice.
    entregada = _hecho(marcos.manda(Jugada("confirmar", {}), texto="dale"), "confirmar")
    assert entregada["resultado"] == "entregada"
    assert TODAVIA_NO_QUEDO_ANOTADO not in entregada


def test_lo_que_suma_un_mensaje_a_un_borrador_no_queda_anotado(conn, mundo, marcos):
    """Lo que se suma a la entrega abierta se dice con `sumo`, que es lo que se está armando."""
    _tarea(conn, mundo)
    _a_medias(marcos)
    hecho = _hecho(marcos.manda(_entregar(), texto="", archivos=[(JPEG, "foto", None)]),
                   "entregar")

    assert hecho["sumo"] == ["P2"] and hecho[TODAVIA_NO_QUEDO_ANOTADO] is True
    assert "confirm" in hechos.significado("sumo")
    assert cuantas(conn, "evidence") == 0


# --- Corregir sin nada que corregir ---------------------------------------------------------

def test_corregir_un_borrador_sin_decir_que_no_abre_otra_pregunta(conn, mundo, marcos):
    """La lectura de la prueba por Telegram: corregir la entrega sin sacar ni cambiar nada. No
    es un dato que falta: no hay nada que corregir, nada quedó anotado y el borrador sigue como
    el tema abierto, que la respuesta retoma (9d)."""
    tarea = _tarea(conn, mundo)
    mostrada = _a_medias(marcos)

    r = marcos.manda(Jugada("corregir", {"corrige": "entregar", "tarea": "T2"}),
                     texto="no mejor dejalo pendiente despues lo hago")

    hecho = _hecho(r, "corregir")
    assert hecho["resultado"] == "sin_efecto" and hecho["motivo"] == "nada_que_corregir"
    assert hecho["no_se_anoto_nada"] is True
    assert hecho["entrega"] == mostrada["entrega"]
    assert "falta" not in hecho
    assert "pregunta" not in hecho and "pregunta_para_despues" not in hecho
    # Una sola pregunta abierta, la de siempre: la del borrador, retomada.
    assert cuantas(conn, "conversation_question", "cerrada_en is null") == 1
    assert r.pregunta["tipo"] == "lo_que_falta_de_la_entrega" and r.pregunta["desde_antes"]
    assert estado_de(conn, tarea) == "en_curso" and cuantas(conn, "evidence") == 0
    assert not hechos.sin_significado(hechos.para_redactar(hecho))


def test_sacar_una_pieza_que_no_esta_sigue_pidiendo_cual(conn, mundo, marcos):
    """Lo que la persona quiere sacar no es una pieza de lo mostrado: eso sí es un dato que
    falta."""
    _tarea(conn, mundo)
    _a_medias(marcos)
    hecho = _hecho(marcos.manda(Jugada("corregir", {"corrige": "entregar", "tarea": "T2",
                                                    "saca": ["P7"]}),
                                texto="saca la tercera"), "corregir")
    assert hecho["resultado"] == "falta_dato" and hecho["falta"] == ["saca"]


# --- Dejarlo todo es cancelar ---------------------------------------------------------------

def test_cancelar_un_borrador_lo_deja_sin_efecto_y_no_anota_nada(conn, mundo, marcos):
    tarea = _tarea(conn, mundo)
    _a_medias(marcos)

    r = marcos.manda(Jugada("cancelar", {}), texto="no mejor dejalo pendiente despues lo hago")

    hecho = _hecho(r, "cancelar")
    assert hecho["resultado"] == "cancelado" and hecho["no_se_anoto_nada"] is True
    assert hecho["pregunta"]["tipo"] == "lo_que_falta_de_la_entrega"
    assert r.pregunta is None
    assert cuantas(conn, "conversation_question", "cerrada_en is null") == 0
    assert estado_de(conn, tarea) == "en_curso" and cuantas(conn, "evidence") == 0

    # La entrega de después empieza de nuevo: lo dejado no vuelve.
    nueva = _hecho(marcos.manda(_entregar(el_texto_cubre=["explicacion"]),
                                texto="ahora si, quedo cerrado",
                                archivos=[(JPEG, "foto", None)]), "entregar")
    assert [p.get("dice") for p in nueva["entrega"]] == ["ahora si, quedo cerrado", None]


def test_sacar_todo_y_cancelar_tampoco_deja_nada(conn, mundo, marcos):
    """La otra lectura válida de la 51: sacar lo que dijo y dejar la pregunta sin efecto."""
    tarea = _tarea(conn, mundo)
    _a_medias(marcos)

    r = marcos.manda(Jugada("corregir", {"corrige": "entregar", "tarea": "T2", "saca": ["P1"]}),
                     Jugada("cancelar", {}), texto="no mejor dejalo pendiente despues lo hago")

    assert _hecho(r, "corregir")["resultado"] == "corregido"
    assert _hecho(r, "cancelar")["resultado"] == "cancelado"
    assert r.pregunta is None
    assert cuantas(conn, "conversation_question", "cerrada_en is null") == 0
    assert estado_de(conn, tarea) == "en_curso" and cuantas(conn, "evidence") == 0


# --- Las fichas describen el trabajo --------------------------------------------------------

def test_las_fichas_dicen_que_lo_que_espera_confirmacion_no_esta_anotado():
    """Sin frases de ejemplo: qué es cada jugada. Dejar todo lo dicho para una pregunta que
    espera una confirmación o un dato es cancelar; cambiar una parte, corregir."""
    cancelar, corregir = FICHAS["cancelar"].es, FICHAS["corregir"].es
    assert "nada de eso quedó anotado" in cancelar
    assert "no es cancelar: es corregirlo" in cancelar
    assert "ya quedó anotado" in cancelar
    assert "cancelar" in corregir and "no quedó anotado" in corregir


# --- La conversación 51, por su otra lectura ------------------------------------------------

def test_la_51_por_la_otra_lectura_del_paso_2_queda_igual(conn):
    """Si la IA lee el paso 2 como sacar lo que dijo de la entrega y cancelar (`o_bien`), la
    conversación sigue igual: nada abierto, nada anotado y, al entregarla, sólo lo de ese día.
    Como `tests/conversaciones/test_corredor.py`, `_por_la_otra_lectura`."""
    import copy

    from tests.conversaciones import comprobar as cp
    from tests.conversaciones.corredor import correr_conversacion, elegir
    from tests.conversaciones.grabar import IAPerfecta, IAQueGraba

    [conv] = elegir(["51"])
    ia = IAQueGraba(IAPerfecta({k: t["titulo"] for k, t in conv["tareas"].items()}))
    guion = copy.deepcopy(conv)
    paso_2 = next(p for p in guion["pasos"] if p["paso"] == 2)
    paso_2["jugadas"] = paso_2["o_bien"]["jugadas"]
    ia.ia.preparar = lambda p: setattr(ia.ia, "paso", next(
        (q for q in guion["pasos"] if q.get("paso") == p.get("paso")), p))

    corrida = correr_conversacion(conn, conv, ia)

    assert corrida.error is None and corrida.fallas() == [], corrida.fallas()
    assert next(p for p in corrida.pasos if p.paso == 2).lectura == cp.O_BIEN
