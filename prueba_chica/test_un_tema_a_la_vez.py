"""Un tema a la vez, también cuando las reglas comunes de las fichas se juntan (revisión de la
corrida en seco con las 16 conversaciones, 2026-10-05).

ADR 0018, decisiones 4, 9d y 9j; `fichas.correr` y `preguntas.abrir`. Tres reglas generales,
para toda ficha y toda pregunta:

- **Nunca dos preguntas juntas:** si una jugada sobre una tarea vencida lleva la pregunta de
  para cuándo (9j) y además propone algo (`Ficha.propone`), se pregunta la fecha y lo propuesto
  queda para después, sin perder ninguno de los dos en los hechos.
- **Una opción elegida pasa por las mismas comprobaciones de su ficha** que la jugada escrita,
  escrita o tocada: con la tarea vencida, lleva la misma pregunta de para cuándo.
- **Una pregunta que queda para después no cuenta silencio:** su espera (y la escalera que la
  repite) empieza recién cuando Leda la hace, no cuando quedó guardada sin preguntarse.

El reloj es el de `test_escalera.py`: "Revisar el tablero" (T1) de Marcos vence el viernes 9 de
octubre de 2026; el lunes 12 es feriado.
"""

from __future__ import annotations

from datetime import datetime

from prueba_chica import fichas
from prueba_chica.ia import IAGuionada, Jugada
from prueba_chica.test_avisos import _dice, _hora
from prueba_chica.test_escalera import (  # noqa: F401 (las fixtures se usan por su nombre)
    dias, espacio_con_escalera)
from prueba_chica.test_situaciones import _cuantas, _tarea, _todos
from prueba_chica.test_toques import _quien
from prueba_chica.tiempo import RelojFijo
from prueba_chica.turno import procesar_toque, procesar_turno

FECHA = "fecha_de_la_tarea"
PROPUESTA = "propuesta"


def _vencida(dias) -> None:
    """El pedido del vencimiento (viernes 9) y el del martes 13, sin respuesta."""
    dias.ciclo(_hora(9, 10))
    dias.ciclo(_hora(13, 10))


def _abierta(conn) -> str | None:
    fila = _todos(conn, """select q.tipo from conversation_state s
                            join conversation_question q on q.id = s.pregunta_abierta_id
                           where q.cerrada_en is null""")
    return fila[0]["tipo"] if fila else None


def _para_despues(conn) -> list[str]:
    return [f["tipo"] for f in _todos(conn, """select tipo from conversation_question
                                                where cerrada_en is null
                                                  and para_despues_en is not null
                                                order by abierta_en""")]


# --- Nunca dos preguntas juntas ------------------------------------------------------------

def _anotar_y_proponer(ctx, datos, tarea):
    """Una jugada cualquiera que anota algo que no es cierto sobre cuándo y propone salidas."""
    return {"resultado": "anotado", "tarea": fichas.tarea_hecho(tarea),
            "salidas": ["anotar_prevision"]}


PROPONE = fichas.Ficha(
    "anotar_y_proponer", "una jugada de prueba", necesita=("tarea",), opcional=(),
    comprueba="", hace="", despues="", manejar=_anotar_y_proponer, del_responsable=True,
    propone=lambda hecho: hecho.get("salidas"))


def test_con_la_tarea_vencida_lo_propuesto_espera_y_se_pregunta_la_fecha(conn, mundo, dias,
                                                                        escribe):
    _vencida(dias)
    jugadas = {**fichas.JUGADAS, PROPONE.nombre: lambda ctx, j: fichas.correr(PROPONE, ctx, j)}
    quien, entrante = escribe("Marcos", "-", at=_hora(13, 10, 20))
    ia = IAGuionada(jugadas=[[Jugada(PROPONE.nombre, {"tarea": "T1"})]], redacciones=["Ok."])

    r = procesar_turno(conn, quien, entrante, ia, RelojFijo(_hora(13, 10, 20)), jugadas)
    conn.commit()

    [hecho] = r.hechos
    assert r.pregunta["tipo"] == FECHA and _abierta(conn) == FECHA     # una sola, la fecha
    assert hecho["pregunta"] == FECHA
    assert hecho["pregunta_para_despues"] == PROPUESTA                 # lo propuesto, después
    assert PROPUESTA in _para_despues(conn)


# --- Una opción elegida pasa por las comprobaciones de su ficha ----------------------------

def _duda_con_la_tarea_vencida(conn, mundo, dias, escribe) -> dict[str, str]:
    """T1 vencida, y Marcos dice que arrancó sin decir cuál: Leda pregunta con las dos."""
    _tarea(conn, mundo, "Probar las comunicaciones")
    _vencida(dias)
    r = _dice(conn, escribe, Jugada("anotar_inicio", {}), at=_hora(13, 10, 20))
    assert r.pregunta["tipo"] == "cual_tarea"
    return {o["etiqueta"]: o["token"] for o in _todos(conn, "select etiqueta, token "
                                                           "from conversation_option")}


def _es_la_regla_de_la_tarea_vencida(conn, r) -> None:
    [hecho] = [h for h in r.hechos if h.get("jugada") == "anotar_inicio"]
    assert (hecho["resultado"], hecho["estado"]) == ("anotado", "en_curso")
    assert hecho["vencida"] == {"fecha_comprometida": "2026-10-09", "atraso_dias_habiles": 1}
    assert hecho["pregunta"] == FECHA and r.pregunta["tipo"] == FECHA
    assert _cuantas(conn, "conversation_question", "tipo = %s and cerrada_en is null",
                    FECHA) == 1


def test_una_opcion_escrita_lleva_la_pregunta_de_la_tarea_vencida(conn, mundo, dias, escribe):
    _duda_con_la_tarea_vencida(conn, mundo, dias, escribe)

    r = _dice(conn, escribe, Jugada("elegir", {"opcion": "O1"}), at=_hora(13, 10, 25))

    _es_la_regla_de_la_tarea_vencida(conn, r)


def test_una_opcion_tocada_lleva_la_pregunta_de_la_tarea_vencida(conn, mundo, dias, escribe):
    tokens = _duda_con_la_tarea_vencida(conn, mundo, dias, escribe)

    r = procesar_toque(conn, _quien(conn, mundo), tokens["Revisar el tablero"],
                       mundo["personas"]["Marcos"]["telegram"],
                       IAGuionada(redacciones=["Ok."]), RelojFijo(_hora(13, 10, 25)))
    conn.commit()

    _es_la_regla_de_la_tarea_vencida(conn, r)


def test_una_opcion_que_la_lista_del_turno_no_tiene_no_corre(conn, mundo, dias, escribe):
    """La jugada que esperaba la duda se busca en la lista cerrada del turno, como una escrita:
    si no está, no se corre por la puerta de la opción."""
    _duda_con_la_tarea_vencida(conn, mundo, dias, escribe)
    sin_inicio = {k: v for k, v in fichas.JUGADAS.items() if k != "anotar_inicio"}
    quien, entrante = escribe("Marcos", "la primera", at=_hora(13, 10, 25))
    ia = IAGuionada(jugadas=[[Jugada("elegir", {"opcion": "O1"})]], redacciones=["Ok."])

    r = procesar_turno(conn, quien, entrante, ia, RelojFijo(_hora(13, 10, 25)), sin_inicio)
    conn.commit()

    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["motivo"]) == ("no_se_puede", "fuera_de_la_lista")
    assert hecho["pregunta_sigue_abierta"] is True and _abierta(conn) == "cual_tarea"
    assert _cuantas(conn, "task_state_event", "estado_nuevo = 'en_curso'") == 0


# --- Una pregunta para después no cuenta silencio ------------------------------------------

def _dos_bloqueos(conn, mundo, escribe, at: datetime) -> None:
    """Dos bloqueos con causa en un mensaje: la pregunta de quién destraba el primero se hace;
    la del segundo queda para después (situación general 2)."""
    _tarea(conn, mundo, "Probar las comunicaciones")
    r = _dice(conn, escribe, Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "falta el PLC"}),
              Jugada("anotar_bloqueo", {"tarea": "T2", "causa": "falta el switch"}), at=at)
    assert r.pregunta["tipo"] == "quien_destraba"
    assert _para_despues(conn) == ["quien_destraba"]


def _esperas_de_quien_destraba(conn) -> int:
    return _cuantas(conn, "pending_reply", "tipo = 'quien_destraba' and satisfecho_en is null")


def test_una_pregunta_que_queda_para_despues_no_abre_su_espera(conn, mundo, dias, escribe):
    _dos_bloqueos(conn, mundo, escribe, _hora(6, 10))

    assert _esperas_de_quien_destraba(conn) == 1          # sólo la que se hizo

    # Al día siguiente, la escalera repite sólo la que se hizo.
    [repregunta] = [p for p in dias.ciclo(_hora(7, 10)) if p["persona"] == "Marcos"]
    assert [h.get("aviso") for h in repregunta["hechos"]] == ["repregunta"]


def test_la_pregunta_de_despues_abre_su_espera_cuando_se_hace(conn, mundo, dias, escribe):
    _dos_bloqueos(conn, mundo, escribe, _hora(6, 10))

    r = _dice(conn, escribe, Jugada("anotar_quien_destraba", {"tarea": "T1", "no_sabe": True}),
              at=_hora(6, 10, 5))

    assert r.pregunta["tipo"] == PROPUESTA       # las salidas del primero, antes que la otra
    r = _dice(conn, escribe, Jugada("cancelar", {}), at=_hora(6, 10, 10))
    assert r.pregunta["tipo"] == "quien_destraba"           # ahora sí se hace la del segundo
    [espera] = _todos(conn, """select preguntado_en from pending_reply
                                where tipo = 'quien_destraba' and satisfecho_en is null""")
    assert espera["preguntado_en"] == _hora(6, 10, 10)


def test_cada_clave_de_pregunta_de_los_hechos_tiene_siempre_la_misma_forma():
    hecho: dict = {}
    fichas._nombrar_pregunta(hecho, "pregunta_para_despues", PROPUESTA)
    fichas._nombrar_pregunta(hecho, "pregunta_para_despues", FECHA)
    fichas._nombrar_pregunta(hecho, "pregunta_para_despues", FECHA)

    assert hecho == {"pregunta_para_despues": PROPUESTA,
                     "otras_preguntas_para_despues": [FECHA]}
