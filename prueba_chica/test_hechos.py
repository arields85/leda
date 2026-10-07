"""El vocabulario de los hechos: cada dato que el código le pasa a la IA dice qué significa.

Revisión del contrato entre la IA y el código (usuario, 2026-10-05; ADR 0018, decisión 9),
después de la primera ronda real: un hecho sin su significado hizo decir algo falso (el atraso
de una previsión contado como el atraso de hoy, conversaciones 15 y 16). Cada clave y cada
código de los hechos tiene su significado en `hechos.py`, y la IA recibe el de todo lo que le
llega en cada pedido. Un hecho sin significado es una falla del motor en la corrida.
"""

from __future__ import annotations

import json

from prueba_chica import avisos, hechos, preguntas
from prueba_chica.conftest import AHORA
from prueba_chica.fichas import (EN_COLA_SIN_ENVIAR, ESPERA_ALGO_CIERTO, FICHAS,
                                  GUARDADO_SIN_ENVIAR, SALIDAS_DE_UN_BLOQUEO)
from prueba_chica.ia import IAGuionada, Jugada
from prueba_chica.ia_real import DATOS, DIAS_PROXIMOS
from prueba_chica.instrucciones import INSTRUCCIONES_JUGADAS, INSTRUCCIONES_REDACCION
from prueba_chica.test_ia_real import SITUACION, ProveedorFalso, _ia, _llamada, _texto
from prueba_chica.tiempo import RelojFijo
from prueba_chica.turno import SOLO_SI_PREGUNTA, procesar_turno

from leda.db import admin

from tests.conversaciones import motores
from tests.conversaciones.corredor import correr_conversacion, elegir
from tests.conversaciones.grabar import IAPerfecta

# --- El vocabulario ---------------------------------------------------------------------------

def test_cada_codigo_del_motor_tiene_su_significado():
    """Las jugadas y sus datos, los tipos de pregunta y de aviso, los estados de un efecto que
    pasa después, las salidas y lo que Leda espera saber: lo que un hecho nombra con un código,
    la IA lo lee con su significado."""
    codigos = (set(FICHAS) | set(preguntas.TIPOS) | set(avisos.TIPOS) | set(DATOS)
               | {GUARDADO_SIN_ENVIAR, EN_COLA_SIN_ENVIAR} | set(SALIDAS_DE_UN_BLOQUEO)
               | set(ESPERA_ALGO_CIERTO))
    assert not {c for c in codigos if not hechos.significado(c)}, codigos


def test_dos_atrasos_distintos_tienen_dos_claves_distintas():
    """El de hoy (desde la fecha comprometida) y el que tendrá la tarea si se cumple una
    previsión: con una sola clave, la IA contó uno como el otro (ronda 1)."""
    hoy = hechos.significado("atraso_dias_habiles")
    previsto = hechos.significado("atraso_si_se_cumple_la_prevision_dias_habiles")
    assert hoy and previsto and hoy != previsto
    assert "hoy" in hoy and "si se cumple" in previsto


def test_sin_significado_nombra_lo_que_no_esta_en_el_vocabulario():
    valor = {"jugada": "anotar_inicio", "resultado": "anotado", "clave_nueva": 1,
             "tarea": {"alias": "T1", "titulo": "Programar el PLC"},
             "estado": "codigo_nuevo", "texto": "dijo algo con espacios"}

    assert hechos.sin_significado(valor) == {"clave_nueva", "codigo_nuevo"}


def test_el_bloque_de_significados_trae_solo_lo_que_el_pedido_usa():
    pedido = {"hechos": [{"jugada": "anotar_prevision", "resultado": "anotado",
                          "atraso_si_se_cumple_la_prevision_dias_habiles": 3,
                          "aviso_al_referente": {"estado": GUARDADO_SIN_ENVIAR}}]}

    bloque = hechos.bloque(pedido)

    for clave in ("hechos", "jugada", "resultado", "aviso_al_referente", "estado",
                  "atraso_si_se_cumple_la_prevision_dias_habiles", "anotar_prevision",
                  "anotado", GUARDADO_SIN_ENVIAR):
        assert f"- {clave}: {hechos.significado(clave)}" in bloque, clave
    assert "- atraso_dias_habiles:" not in bloque
    assert "- anotar_bloqueo:" not in bloque


# --- La IA real recibe el significado de lo que le llega ------------------------------------

def test_los_dos_pedidos_a_la_ia_llevan_el_significado_de_sus_datos():
    pedido = {"hoy": "2026-10-20", "persona": "Ismael", "mensaje": None,
              "hechos": [{"aviso": "nueva_prevision", "necesita_respuesta": False,
                          "atraso_si_se_cumple_la_prevision_dias_habiles": 3}],
              "pregunta": None, "ultimos_turnos": []}
    proveedor = ProveedorFalso([_llamada({"jugadas": []}), _texto("Hola.")])
    ia = _ia(proveedor)

    ia.elegir_jugadas(SITUACION)
    ia.redactar(pedido)

    eleccion, redaccion = (p["cuerpo"]["messages"][0]["content"] for p in proveedor.pedidos)
    # Los pedidos llevan además el día de cada fecha (`dias`), con su significado.
    con_dias = {**SITUACION, "dias": hechos.dias(SITUACION, proximos=DIAS_PROXIMOS)}
    assert eleccion == f"{INSTRUCCIONES_JUGADAS}\n\n{hechos.bloque(con_dias)}"
    assert redaccion.startswith(f"{INSTRUCCIONES_REDACCION}\n\n"
                                f"{hechos.bloque({**pedido, 'dias': hechos.dias(pedido)})}")
    assert hechos.significado("atraso_si_se_cumple_la_prevision_dias_habiles") in redaccion
    assert hechos.significado("nueva_prevision") in redaccion


def test_las_instrucciones_remiten_a_los_significados_y_piden_un_proximo_paso():
    """Reglas generales de la redacción (constitución §8 y §10): todo mensaje deja un próximo
    paso o dice que no hace falta nada; nunca se narra cómo funciona el sistema; sin hechos
    nuevos, se contesta desde el registro. Sin frases de las conversaciones."""
    for texto in (INSTRUCCIONES_JUGADAS, INSTRUCCIONES_REDACCION):
        assert "lista de significados" in texto
    redaccion = INSTRUCCIONES_REDACCION.lower()
    assert "próximo paso" in redaccion
    assert "por dentro" in redaccion
    assert "últimos turnos" in redaccion
    for frase in ("le avisaste", "switch", "no pude cancelar", "¿te sirve"):
        assert frase not in redaccion, frase


# --- Una pregunta sobre lo que ya está en el registro -----------------------------------------

def test_una_pregunta_sobre_lo_hecho_no_lleva_jugada_ni_aviso_y_se_contesta_del_registro(
        conn, mundo, escribe):
    """Ronda 1, conversación 12: "¿le avisaste a alguien?" no es un pedido. Sin jugada no hay
    aviso al administrador, y la redacción tiene en los últimos turnos el hecho guardado del
    aviso de antes (`solo_si_pregunta`) para contestar con la verdad."""
    ia = IAGuionada(jugadas=[[Jugada("fuera_de_la_lista", {"que_pide": "un recordatorio"})],
                             []],
                    redacciones=["Eso no lo puedo hacer.", "Sí, quedó avisado."])
    for texto in ("me recordás el turno?", "y eso le avisaste a alguien?"):
        quien, entrante = escribe("Marcos", texto)
        resultado = procesar_turno(conn, quien, entrante, ia, RelojFijo(AHORA))
        conn.commit()
        assert resultado.error is None

    assert resultado.jugadas == [] and resultado.hechos == []
    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where etapa = 'motor_fuera_de_la_lista'")
        assert cur.fetchone()["n"] == 1             # sólo el del pedido, no el de la pregunta
    conn.commit()
    registro = json.dumps(ia.pedidos_de_redaccion[-1]["ultimos_turnos"], ensure_ascii=False)
    assert SOLO_SI_PREGUNTA in registro and "aviso_al_administrador" in registro


# --- En la corrida, un hecho sin significado es una falla del motor --------------------------

def test_un_hecho_sin_significado_es_una_falla_del_motor(conn, monkeypatch):
    [conv] = elegir(["01"])
    monkeypatch.setattr(hechos, "SIGNIFICADOS",
                        {k: v for k, v in hechos.SIGNIFICADOS.items() if k != "jugada"})

    motor = motores.cargar("prueba_chica")
    corrida = correr_conversacion(conn, conv, IAPerfecta(
        {k: t["titulo"] for k, t in conv["tareas"].items()}, jugada=motor.Jugada), motor=motor)

    fallas = [f for _, f in corrida.fallas("motor") if f.que == "hechos sin significado"]
    assert fallas and "jugada" in fallas[0].real


# --- Tercera vuelta de ajuste (usuario, 2026-10-06) ------------------------------------------

def test_los_significados_son_para_entender_y_nunca_para_repetir():
    """Ronda 2: "cambiarla lo decide el referente" se le repitió a la persona. El bloque y las
    instrucciones dicen que los significados son de fondo, y ninguno se lee como una frase para
    decir."""
    assert hechos.bloque({"fecha_comprometida": "2026-10-23"}).startswith(
        hechos.ENCABEZADO_DEL_BLOQUE)
    assert "nunca se le cuenta" in hechos.ENCABEZADO_DEL_BLOQUE
    assert "nunca se los contás" in INSTRUCCIONES_REDACCION
    assert "lo decide el referente" not in hechos.significado("fecha_comprometida")


def test_ningun_significado_ni_dato_dice_ella_por_quien_escribe():
    """Ronda 2: "le toca a ella" se leyó como Leda. Se nombra a quién: la persona que escribe."""
    textos = [*hechos.SIGNIFICADOS.values(), *(d for _, d in DATOS.values()),
              *(f.es for f in FICHAS.values())]
    assert not [t for t in textos if "a ella" in t or "ella misma" in t]
    assert "nunca a Leda" in hechos.significado("nadie_mas")
    assert "persona que escribe" in DATOS["nadie_mas"][1]
