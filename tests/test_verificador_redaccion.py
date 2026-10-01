"""El verificador del texto de la variante A (ADR 0014, etapa 6, F6a).

Es determinista y opera sobre los hechos estructurados del turno, no sobre
frases: un texto sale sólo si todo lo que los hechos exigen aparece y nada que
los hechos no tienen (un cambio, un estado, una fecha, un número, una clave
interna) se afirma. Las pruebas cubren familias de variantes de cada garantía,
no una frase observada. Sin base, sin modelo.
"""

from __future__ import annotations

import pytest

from prisma.resultado_turno import (
    Cambio, Estado, Falta, OpcionDisponible, Rechazo, ResultadoTurno, Resumen,
    SinCambio, ValorAceptado,
)
from prisma.valores import TipoValor
from prisma.verificador_redaccion import LARGO_MAXIMO, verificar

TAREA = "la tarea «Revisar PLC»"

EN_CURSO = ResultadoTurno(
    cambios=(Cambio(TAREA, "quedó en curso"),),
    estado=(Estado("«Revisar PLC»", "en curso"),))

FECHA = ResultadoTurno(
    valores_aceptados=(ValorAceptado("la fecha objetivo", "04/10/2026"),),
    falta=Falta("el criterio de aceptación", TipoValor.TEXTO,
                pregunta="¿Cómo sabemos que quedó terminada?"))

PREGUNTA = ResultadoTurno(
    falta=Falta("la fecha objetivo", TipoValor.FECHA,
                pregunta="¿Para cuándo debería estar?"))


def _acepta(resultado, texto):
    assert verificar(resultado, texto) is None, texto


def _rechaza(resultado, texto, motivo):
    razon = verificar(resultado, texto)
    assert razon is not None and razon.startswith(motivo), (texto, razon)


# ------------------------------------------------ lo que sí pasa, dicho distinto

@pytest.mark.parametrize("texto", [
    "Listo, la tarea «Revisar PLC» quedó en curso.",
    "Ya está: «Revisar PLC» quedó en curso.",
    "Algo bueno: la tarea «Revisar PLC» quedó en curso, así que está en curso.",
])
def test_un_cambio_dicho_de_otra_forma_pasa(texto):
    _acepta(EN_CURSO, texto)


@pytest.mark.parametrize("texto", [
    "Anotado: la fecha objetivo queda el 04/10/2026. ¿Cómo sabemos que quedó "
    "terminada?",
    "Dejé la fecha objetivo para el 4 de octubre. ¿Cómo sabemos que quedó "
    "terminada?",
])
def test_una_fecha_aceptada_pasa_en_cualquier_formato(texto):
    _acepta(FECHA, texto)


# ------------------------------------------------ (a) un cambio que no ocurrió

@pytest.mark.parametrize("texto", [
    "Creé la tarea. ¿Para cuándo debería estar?",
    "Anoté tu respuesta. ¿Para cuándo debería estar?",
    "Guardé el cambio y listo. ¿Para cuándo debería estar?",
    "Registré la fecha, gracias. ¿Para cuándo debería estar?",
    "Todo bien, ya lo cancelé. ¿Para cuándo debería estar?",
])
def test_sin_ningun_cambio_no_se_afirma_una_accion_hecha(texto):
    _rechaza(PREGUNTA, texto, "accion_no_ocurrida")


def test_negar_una_accion_no_es_afirmarla():
    sin_cambio = ResultadoTurno(
        sin_cambios=(SinCambio(TAREA, "ya estaba en curso"),))
    _acepta(sin_cambio, "No cambié la tarea «Revisar PLC»: ya estaba en curso.")


def test_con_un_cambio_real_se_puede_decir_lo_hecho():
    _acepta(EN_CURSO, "Listo, dejé la tarea «Revisar PLC» en curso.")


# ------------------------------------------------ (b) contradice los hechos

@pytest.mark.parametrize("texto", [
    "Anoté la fecha objetivo: 5 de octubre. ¿Cómo sabemos que quedó terminada?",
    "Anoté la fecha objetivo: 05/10/2026. ¿Cómo sabemos que quedó terminada?",
    "Anoté la fecha objetivo: 10/04/2026. ¿Cómo sabemos que quedó terminada?",
    "Anoté la fecha objetivo: 4 de noviembre. ¿Cómo sabemos que quedó terminada?",
])
def test_una_fecha_distinta_de_la_aceptada_se_rechaza(texto):
    razon = verificar(FECHA, texto)
    assert razon is not None and razon.split(":")[0] in {
        "numero_inventado", "fecha_distinta", "mes_inventado"}, razon


@pytest.mark.parametrize("texto", [
    "Listo, la tarea «Revisar el PLC» quedó en curso.",
    "Listo, la tarea «Revisar PLC 2» quedó en curso.",
])
def test_un_titulo_distinto_se_rechaza(texto):
    assert verificar(EN_CURSO, texto) is not None


@pytest.mark.parametrize("texto", [
    "La tarea «Revisar PLC» está terminada.",
    "La tarea «Revisar PLC» está completada.",
    "La tarea «Revisar PLC» quedó bloqueada y en curso.",
    "La tarea «Revisar PLC» está en revisión y en curso.",
])
def test_un_estado_que_los_hechos_no_tienen_se_rechaza(texto):
    _rechaza(EN_CURSO, texto, "estado_inventado")


# ------------------------------------------------ (c) omite un hecho exigido

def test_se_exige_la_pregunta_de_lo_que_falta():
    _rechaza(PREGUNTA, "Gracias, sigo con lo tuyo.", "falta_pregunta")
    _acepta(PREGUNTA, "Gracias. ¿Para cuándo debería estar?")
    _acepta(PREGUNTA, "¿Me decís para qué día lo necesitás?")


def test_una_pregunta_dicha_como_instruccion_se_exige_por_su_contenido():
    instruccion = ResultadoTurno(falta=Falta(
        "el objetivo", TipoValor.TEXTO,
        pregunta="Escribí parte del nombre del objetivo."))
    _acepta(instruccion, "Dale. Escribime parte del nombre del objetivo.")
    _rechaza(instruccion, "Dale, seguimos con lo tuyo.", "falta_pregunta")


def test_se_exige_la_fecha_interpretada():
    _rechaza(FECHA, "Anotado. ¿Cómo sabemos que quedó terminada?", "falta_hecho")


def test_se_exige_el_nombre_citado():
    _rechaza(EN_CURSO, "Listo, la tarea quedó en curso.", "falta_hecho")


def test_se_exige_lo_que_dice_un_rechazo():
    rechazo = ResultadoTurno(
        rechazo=Rechazo("Esa fecha ya pasó.",
                        "Decime una fecha desde hoy en adelante."),
        falta=Falta("la fecha objetivo", TipoValor.FECHA))
    _acepta(rechazo, "Esa fecha ya pasó: pasame otra de hoy en adelante, ¿sí?")
    _rechaza(rechazo, "Gracias por avisar, ¿para cuándo?", "falta_hecho")


def test_el_resumen_exige_todos_sus_datos():
    resumen = Resumen("Resumen para revisar",
                      (("Título", "Revisar PLC"), ("Responsable", "Sam North"),
                       ("Fecha objetivo", "04/10/2026")),
                      "Con Confirmar se crea la tarea con estos datos.")
    r = ResultadoTurno(resumen=resumen)
    _acepta(r, "Resumen para revisar\nTítulo: Revisar PLC\nResponsable: Sam North\n"
               "Fecha objetivo: 4 de octubre")
    _rechaza(r, "Resumen para revisar\nTítulo: Revisar PLC\nResponsable: Sam North",
             "falta_hecho")


# ------------------------------------------------ inventos de otro tipo y largo

@pytest.mark.parametrize("texto", [
    "Listo, la tarea «Revisar PLC» quedó en curso, junto con 3 tareas más.",
    "Listo, la tarea «Revisar PLC» quedó en curso en 2 minutos.",
])
def test_un_numero_que_los_hechos_no_tienen_se_rechaza(texto):
    _rechaza(EN_CURSO, texto, "numero_inventado")


@pytest.mark.parametrize("texto", [
    "Listo, la tarea «Revisar PLC» quedó en curso (task_state=en_curso).",
    "Listo, la tarea «Revisar PLC» quedó en curso {estado}.",
])
def test_una_clave_interna_se_rechaza(texto):
    assert verificar(EN_CURSO, texto) is not None


def test_un_texto_vacio_se_rechaza():
    _rechaza(EN_CURSO, "   ", "vacio")


def test_un_texto_demasiado_largo_se_rechaza():
    largo = "Listo, la tarea «Revisar PLC» quedó en curso. " + "y además " * 600
    _rechaza(EN_CURSO, largo, "largo")
    assert LARGO_MAXIMO < 5000


def test_el_largo_se_mide_contra_la_plantilla_cuando_hay():
    corto = "Listo, la tarea «Revisar PLC» quedó en curso."
    razon = verificar(EN_CURSO, corto + " " + "más " * 100,
                      texto_b="Listo: la tarea «Revisar PLC» quedó en curso.")
    assert razon is not None and razon.startswith("largo")


def test_las_opciones_no_cuentan_como_hechos_ni_se_exigen():
    con_opciones = ResultadoTurno(
        cambios=EN_CURSO.cambios,
        opciones=(OpcionDisponible("Ver evidencia", "ver"),))
    _acepta(con_opciones, "Listo, la tarea «Revisar PLC» quedó en curso.")
