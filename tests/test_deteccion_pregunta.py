"""Detección de pregunta compartida (T4b, `prisma-orienta`).

`prisma.deteccion_pregunta` es la única implementación de "esto le pregunta
algo a la persona": antes de esta unidad vivía sólo en
`tests/banco/comprobadores.py` (T7); ahora el servidor
(`agente.responder`) la necesita también para el cierre genérico de una
pregunta sin opciones. Estas pruebas repiten, contra el módulo movido, los
casos que ya validaban la heurística en el banco -- si algo se rompió al
mover el código, tiene que fallar acá primero.
"""

from __future__ import annotations

from prisma.deteccion_pregunta import hace_pregunta, pide_elegir_en_imperativo


def test_signo_de_pregunta_alcanza():
    assert hace_pregunta("¿Cómo va?")
    assert not hace_pregunta("Va bien, sin novedades.")


def test_pedido_de_eleccion_en_imperativo_sin_signo():
    assert pide_elegir_en_imperativo("Decime cuál de las dos y lo hago.")
    assert pide_elegir_en_imperativo("Contame qué la está frenando.")
    assert pide_elegir_en_imperativo("Elegí una y seguimos.")
    assert hace_pregunta("Decime cuál de las dos y lo hago.")


def test_verbo_de_pedido_sin_cual_ni_que_no_cuenta():
    # "decime"/"contame"/"confirmame" solos, sin "cuál"/"qué" al lado, no son
    # un pedido de elección -- si no, cualquier cierre cordial contaría.
    assert not pide_elegir_en_imperativo("Decime si necesitás algo más.")
    assert not hace_pregunta("Decime si necesitás algo más.")


def test_que_se_busca_con_borde_de_palabra():
    # "porque"/"aunque" no tienen que disparar un falso positivo por
    # contener "que" como subcadena.
    assert not pide_elegir_en_imperativo("Decime porque me interesa saber.")


def test_negacion_no_es_relevante_para_esta_deteccion():
    # A diferencia de `comprobar_accion_sin_herramienta`, esta detección no
    # mira negaciones: sólo importa si el texto pregunta o pide elegir.
    assert not hace_pregunta("Todo tranquilo, nada que decidir.")


# ---------------------------------------------------------------------------
# Falsos positivos (hallazgo del orquestador): la heurística ahora dispara
# efectos de producción (los botones genéricos, T4b) -- reducir falsos
# positivos sin perder los casos reales que el banco ya valida arriba.
# ---------------------------------------------------------------------------

def test_signo_de_pregunta_dentro_de_una_url_no_cuenta():
    # Un "?" de query string no es Prisma preguntando algo.
    assert not hace_pregunta(
        "Mirá el detalle acá: https://ejemplo.com/tarea?id=5&modo=ver")
    assert not hace_pregunta("Lo subí a www.ejemplo.com/reporte?mes=9")


def test_pregunta_real_junto_a_una_url_sigue_contando():
    assert hace_pregunta(
        "¿Viste esto? Te dejo el link: https://ejemplo.com/tarea?id=5")


def test_elegi_como_subcadena_de_otra_palabra_no_cuenta():
    # "elegido"/"elegida"/"elegimos"/"elegible" no son el imperativo "elegí":
    # antes coincidían porque el marcador buscaba la subcadena "elegi" sin
    # borde de palabra.
    assert not pide_elegir_en_imperativo("Ya fue elegido el responsable.")
    assert not pide_elegir_en_imperativo("La tarea elegida quedó anotada.")
    assert not pide_elegir_en_imperativo("Elegimos seguir con la otra.")
    assert not pide_elegir_en_imperativo("No es elegible para esta ronda.")
    assert not hace_pregunta("Ya fue elegido el responsable.")


def test_cual_como_subcadena_de_cualquier_no_cuenta():
    # "cualquier"/"cualquiera" no son el pedido "cuál" -- mismo motivo que
    # "elegi": el marcador buscaba la subcadena "cual" sin borde de palabra.
    # Sin "qué"/"cuál" como palabra propia al lado (ninguna de las dos frases
    # la tiene), el verbo de pedido solo no alcanza.
    assert not pide_elegir_en_imperativo("Decime cualquier novedad.")
    assert not pide_elegir_en_imperativo("Contame cualquiera de las dos.")
    assert not hace_pregunta("Decime cualquier novedad.")


def test_pregunta_que_termina_con_una_url_sigue_contando():
    # El "?" pegado al final de una URL es el de la pregunta, no parte de la
    # URL: descartar la URL no puede llevarse el signo que cierra la frase.
    assert hace_pregunta("¿Te paso el link del tablero https://ejemplo.com/tablero?")
    assert hace_pregunta("Te paso el link https://ejemplo.com/tablero?")


def test_signo_de_apertura_solo_tambien_cuenta():
    assert hace_pregunta("¿Te lo anoto para mañana")


def test_palabras_dentro_de_una_url_no_cuentan_como_pedido_de_eleccion():
    # Las URLs se descartan para las dos señales, no sólo para el "?": un
    # camino como ".../elegi/..." o ".../cual" no es un pedido de elección.
    assert not hace_pregunta("Decime si sirve: https://ejemplo.com/elegi/cual")
    assert not pide_elegir_en_imperativo("Mirá https://ejemplo.com/elegi")
