"""El verificador del texto de la variante A (ADR 0014, etapa 6).

Es determinista y comprueba sólo lo que el código puede verificar contra los
hechos estructurados del turno: las fechas, los números, los títulos y los
nombres que el texto dice existen en los hechos; el texto pide el dato que falta
(el modelo declara cuál con `pregunta`, de una lista cerrada, y el texto
pregunta); los efectos que cuenta (`afirma`, ids cerrados) son cambios del
resultado. No hay listas de palabras ni morfología: un "Escribí" o un "Creé" no
decide nada por su forma. Las pruebas cubren familias de variantes de cada
garantía, no una frase observada. Sin base, sin modelo.
"""

from __future__ import annotations

import pytest

from prisma.resultado_turno import (
    Cambio, Estado, Falta, OpcionDisponible, Rechazo, ResultadoTurno, Resumen,
    SinCambio, ValorAceptado, ids_de_cambios,
)
from prisma.valores import TipoValor
from prisma.verificador_redaccion import (Borrador, LARGO_MAXIMO, leer_borrador,
                                          verificar)

TAREA = "la tarea «Revisar PLC»"

EN_CURSO = ResultadoTurno(
    cambios=(Cambio(TAREA, "quedó en curso", id="en_curso"),),
    estado=(Estado("«Revisar PLC»", "en curso"),))

FECHA = ResultadoTurno(
    valores_aceptados=(ValorAceptado("la fecha objetivo", "04/10/2026"),),
    falta=Falta("el criterio de aceptación", TipoValor.TEXTO,
                pregunta="¿Cómo sabemos que quedó terminada?",
                campo="acceptance_criterion"))

CRITERIO = ResultadoTurno(
    falta=Falta("el criterio de aceptación", TipoValor.TEXTO,
                campo="acceptance_criterion"))

PREGUNTA = ResultadoTurno(
    falta=Falta("la fecha objetivo", TipoValor.FECHA,
                pregunta="¿Para cuándo debería estar?", campo="due_date"))


def _b(texto, pregunta=None, afirma=()):
    return Borrador(texto, pregunta, tuple(afirma))


def _acepta(resultado, texto, pregunta=None, afirma=()):
    assert verificar(resultado, _b(texto, pregunta, afirma)) is None, texto


def _rechaza(resultado, texto, motivo, pregunta=None, afirma=()):
    razon = verificar(resultado, _b(texto, pregunta, afirma))
    assert razon is not None and razon.startswith(motivo), (texto, razon)


# ------------------------------------------------ lo que sí pasa, dicho distinto

@pytest.mark.parametrize("texto", [
    "Listo, la tarea «Revisar PLC» quedó en curso.",
    "Ya está: «Revisar PLC» quedó en curso.",
    "Algo bueno: la tarea «Revisar PLC» quedó en curso, así que está en curso.",
])
def test_un_cambio_dicho_de_otra_forma_pasa(texto):
    _acepta(EN_CURSO, texto, afirma=["en_curso"])


@pytest.mark.parametrize("texto", [
    "Anotado: la fecha objetivo queda el 04/10/2026. ¿Cómo sabemos que quedó "
    "terminada?",
    "Dejé la fecha objetivo para el 4 de octubre. ¿Cómo sabemos que quedó "
    "terminada?",
])
def test_una_fecha_aceptada_pasa_en_cualquier_formato(texto):
    _acepta(FECHA, texto, pregunta="acceptance_criterion")


@pytest.mark.parametrize("texto", [
    "Escribí el criterio de aceptación: ¿cómo sabemos que quedó terminada?",
    "Anoté la fecha. Escribime el criterio de aceptación, ¿cómo sabemos que "
    "quedó terminada?",
    "Creé el borrador con la fecha y ahora necesito el criterio: ¿cómo lo "
    "comprobamos?",
    "Entendí la fecha. Pasame el criterio de aceptación, ¿me lo decís?",
])
def test_la_forma_verbal_no_decide_nada_un_imperativo_o_un_pasado_pasan(texto):
    # El imperativo "Escribí" (y un "Entendí" o un "Creé") ya no se confunde con
    # una acción hecha: eso se verifica con `afirma`, no con la morfología.
    _acepta(CRITERIO, texto, pregunta="acceptance_criterion")


# ------------------------------------------------ (a) un efecto que no ocurrió

@pytest.mark.parametrize("texto, afirma", [
    ("Listo, ya lo cancelé. ¿Para cuándo debería estar?", ["cancelada"]),
    ("Creé la tarea. ¿Para cuándo debería estar?", ["c1"]),
    ("Anoté la fecha. ¿Para cuándo debería estar?", ["en_curso"]),
])
def test_sin_cambios_no_se_puede_afirmar_un_efecto(texto, afirma):
    _rechaza(PREGUNTA, texto, "efecto_no_ocurrido", pregunta="due_date",
             afirma=afirma)


def test_un_efecto_que_no_es_de_los_cambios_se_rechaza():
    _rechaza(EN_CURSO, "Listo, «Revisar PLC» quedó en curso y la cancelé.",
             "efecto_no_ocurrido", afirma=["en_curso", "cancelada"])


def test_se_exige_contar_cada_efecto_que_hubo():
    dos = ResultadoTurno(cambios=(
        Cambio("la tarea «Revisar PLC»", "quedó en curso", id="en_curso"),
        Cambio("el borrador", "quedó enviado", id="enviado")))
    assert ids_de_cambios(dos) == ("en_curso", "enviado")
    _rechaza(dos, "Listo, la tarea «Revisar PLC» quedó en curso.",
             "efecto_omitido", afirma=["en_curso"])
    _acepta(dos, "Listo, «Revisar PLC» quedó en curso y el borrador quedó "
                 "enviado.", afirma=["enviado", "en_curso"])


def test_los_cambios_sin_id_se_numeran_por_posicion():
    r = ResultadoTurno(cambios=(Cambio(TAREA, "quedó en curso"),))
    assert ids_de_cambios(r) == ("c1",)
    _acepta(r, "Listo, la tarea «Revisar PLC» quedó en curso.", afirma=["c1"])


def test_negar_una_accion_no_es_afirmarla():
    sin_cambio = ResultadoTurno(
        sin_cambios=(SinCambio(TAREA, "ya estaba en curso"),))
    _acepta(sin_cambio, "No cambié la tarea «Revisar PLC»: ya estaba en curso.")


# ------------------------------------------------ (b) contradice los hechos

@pytest.mark.parametrize("texto", [
    "Anoté la fecha objetivo: 5 de octubre. ¿Cómo sabemos que quedó terminada?",
    "Anoté la fecha objetivo: 05/10/2026. ¿Cómo sabemos que quedó terminada?",
    "Anoté la fecha objetivo: 10/04/2026. ¿Cómo sabemos que quedó terminada?",
    "Anoté la fecha objetivo: 4 de noviembre. ¿Cómo sabemos que quedó terminada?",
])
def test_una_fecha_distinta_de_la_aceptada_se_rechaza(texto):
    razon = verificar(FECHA, _b(texto, "acceptance_criterion"))
    assert razon is not None and razon.split(":")[0] in {
        "numero_inventado", "fecha_distinta", "mes_inventado"}, razon


@pytest.mark.parametrize("texto", [
    "Listo, la tarea «Revisar el PLC» quedó en curso.",
    "Listo, la tarea «Revisar PLC 2» quedó en curso.",
])
def test_un_titulo_distinto_se_rechaza(texto):
    assert verificar(EN_CURSO, _b(texto, afirma=["en_curso"])) is not None


@pytest.mark.parametrize("texto", [
    "Gracias José, ¿para cuándo debería estar?",
    "Dale, se lo paso a Marcos. ¿Para cuándo debería estar?",
    "Anotado. Lo ve Telegram también: ¿para cuándo debería estar?",
])
def test_un_nombre_propio_que_los_hechos_no_tienen_se_rechaza(texto):
    _rechaza(PREGUNTA, texto, "nombre_inventado", pregunta="due_date")


def test_un_nombre_que_esta_en_los_hechos_pasa_aunque_no_vaya_entre_comillas():
    con_persona = ResultadoTurno(
        valores_aceptados=(ValorAceptado("la persona responsable", "José Pérez"),),
        falta=Falta("la fecha objetivo", TipoValor.FECHA, campo="due_date"))
    _acepta(con_persona, "Dejé a José Pérez como responsable. ¿Para cuándo?",
            pregunta="due_date")


def test_un_nombre_de_las_opciones_cuenta_como_un_hecho_pero_no_se_exige():
    con_opciones = ResultadoTurno(
        falta=Falta("el objetivo", TipoValor.OPCION, campo="objective"),
        opciones=(OpcionDisponible("Planta Norte", "elegir"),))
    _acepta(con_opciones, "Elegí el objetivo, ¿cuál es?", pregunta="objective")
    _acepta(con_opciones, "¿Es de Planta Norte o de otro objetivo?",
            pregunta="objective")


def test_la_mayuscula_al_empezar_una_oracion_no_es_un_nombre():
    _acepta(PREGUNTA, "Gracias. Perfecto. ¿Para cuándo debería estar? Contame.",
            pregunta="due_date")


# ------------------------------------------------ (c) omite lo que falta

def test_se_exige_la_pregunta_de_lo_que_falta():
    _rechaza(PREGUNTA, "Gracias, sigo con lo tuyo.", "falta_pregunta",
             pregunta="due_date")
    _acepta(PREGUNTA, "Gracias. ¿Para cuándo debería estar?", pregunta="due_date")
    _acepta(PREGUNTA, "¿Me decís para qué día lo necesitás?", pregunta="due_date")


def test_la_pregunta_tiene_que_ser_la_del_dato_que_falta():
    # Ningún "?" no alcanza como declaración, ni la declaración como pregunta.
    _rechaza(PREGUNTA, "Gracias. ¿Todo bien por ahí?", "falta_pregunta",
             pregunta="title")
    _rechaza(PREGUNTA, "Gracias. ¿Todo bien por ahí?", "falta_pregunta",
             pregunta=None)
    _rechaza(PREGUNTA, "Pasame la fecha.", "falta_pregunta", pregunta="due_date")


def test_sin_un_dato_que_falta_el_texto_no_abre_una_pregunta():
    _rechaza(EN_CURSO, "Listo, «Revisar PLC» quedó en curso. ¿Algo más?",
             "pregunta_sin_falta", afirma=["en_curso"])
    _rechaza(EN_CURSO, "Listo, «Revisar PLC» quedó en curso.",
             "pregunta_sin_falta", pregunta="due_date", afirma=["en_curso"])


def test_un_dato_sin_campo_propio_se_declara_por_su_nombre():
    sin_campo = ResultadoTurno(falta=Falta("la fecha objetivo", TipoValor.FECHA))
    _acepta(sin_campo, "¿Para cuándo?", pregunta="la fecha objetivo")


def test_se_exige_la_fecha_interpretada():
    _rechaza(FECHA, "Anotado. ¿Cómo sabemos que quedó terminada?", "falta_hecho",
             pregunta="acceptance_criterion")


def test_se_exige_el_nombre_citado():
    _rechaza(EN_CURSO, "Listo, la tarea quedó en curso.", "falta_hecho",
             afirma=["en_curso"])


def test_se_exige_lo_que_dice_un_rechazo():
    rechazo = ResultadoTurno(
        rechazo=Rechazo("Esa fecha ya pasó.",
                        "Decime una fecha desde hoy en adelante."),
        falta=Falta("la fecha objetivo", TipoValor.FECHA, campo="due_date"))
    _acepta(rechazo, "Esa fecha ya pasó: pasame otra de hoy en adelante, ¿sí?",
            pregunta="due_date")
    _rechaza(rechazo, "Gracias por avisar, ¿para cuándo?", "falta_hecho",
             pregunta="due_date")


def test_lo_entendido_se_exige_si_es_corto():
    entendido = ResultadoTurno(
        entendido=(ValorAceptado("la fecha objetivo", "04/10/2026"),),
        falta=Falta("el criterio de aceptación", TipoValor.TEXTO,
                    campo="acceptance_criterion"))
    _acepta(entendido, "Tomé el 4 de octubre. ¿Cómo sabemos que terminó?",
            pregunta="acceptance_criterion")
    _rechaza(entendido, "Tomé la fecha. ¿Cómo sabemos que terminó?", "falta_hecho",
             pregunta="acceptance_criterion")


# ------------------------------------------------ el resumen: bloque del código

def test_con_un_resumen_el_texto_es_una_apertura_sin_preguntas():
    resumen = Resumen("Resumen para revisar",
                      (("Título", "Revisar PLC"), ("Fecha objetivo", "04/10/2026")),
                      "Con Confirmar se crea la tarea con estos datos.")
    r = ResultadoTurno(resumen=resumen)
    # Los datos los agrega el código, exactos: la apertura no tiene que traerlos.
    _acepta(r, "Listo, ya tengo todo. Revisalo con calma:")
    _acepta(r, "Armé el borrador de «Revisar PLC» para el 4 de octubre.")
    _rechaza(r, "Listo, ya tengo todo. ¿Lo revisás?", "pregunta_sin_falta")
    _rechaza(r, "Armé el borrador para el 10 de octubre.", "fecha_distinta")
    _rechaza(r, "Armé el borrador de «Revisar el PLC».", "nombre_inventado")


# ------------------------------------------------ inventos de otro tipo y largo

@pytest.mark.parametrize("texto", [
    "Listo, la tarea «Revisar PLC» quedó en curso, junto con 3 tareas más.",
    "Listo, la tarea «Revisar PLC» quedó en curso en 2 minutos.",
])
def test_un_numero_que_los_hechos_no_tienen_se_rechaza(texto):
    _rechaza(EN_CURSO, texto, "numero_inventado", afirma=["en_curso"])


@pytest.mark.parametrize("texto", [
    "Listo, la tarea «Revisar PLC» quedó en curso (task_state=en_curso).",
    "Listo, la tarea «Revisar PLC» quedó en curso {estado}.",
])
def test_una_clave_interna_se_rechaza(texto):
    assert verificar(EN_CURSO, _b(texto, afirma=["en_curso"])) is not None


def test_un_texto_vacio_se_rechaza():
    _rechaza(EN_CURSO, "   ", "vacio", afirma=["en_curso"])


def test_un_texto_demasiado_largo_se_rechaza():
    largo = "Listo, la tarea «Revisar PLC» quedó en curso. " + "y además " * 600
    _rechaza(EN_CURSO, largo, "largo", afirma=["en_curso"])
    assert LARGO_MAXIMO < 5000


def test_el_largo_se_mide_contra_la_plantilla_cuando_hay():
    corto = "Listo, la tarea «Revisar PLC» quedó en curso."
    razon = verificar(EN_CURSO, _b(corto + " " + "más " * 100, afirma=["en_curso"]),
                      texto_b="Listo: la tarea «Revisar PLC» quedó en curso.")
    assert razon is not None and razon.startswith("largo")


def test_las_opciones_no_se_exigen():
    con_opciones = ResultadoTurno(
        cambios=EN_CURSO.cambios,
        opciones=(OpcionDisponible("Ver evidencia", "ver"),))
    _acepta(con_opciones, "Listo, la tarea «Revisar PLC» quedó en curso.",
            afirma=["en_curso"])


# ------------------------------------------------ la salida estructurada

def test_se_lee_el_json_del_modelo():
    b = leer_borrador('{"texto": "Hola. ¿Para cuándo?", "pregunta": "due_date", '
                      '"afirma": ["c1"]}')
    assert b == Borrador("Hola. ¿Para cuándo?", "due_date", ("c1",))


@pytest.mark.parametrize("crudo", [
    '```json\n{"texto": "Hola", "pregunta": null, "afirma": []}\n```',
    'Acá va: {"texto": "Hola", "pregunta": null, "afirma": []} Gracias.',
    '{"texto": "Hola", "pregunta": null}',
    '{"texto": "Hola"}',
])
def test_se_lee_el_json_aunque_venga_con_vallas_o_sin_las_claves_opcionales(crudo):
    assert leer_borrador(crudo) == Borrador("Hola", None, ())


@pytest.mark.parametrize("crudo, motivo", [
    ("", "formato"),
    ("Hola, ¿para cuándo?", "formato"),
    ("[1, 2]", "formato"),
    ('{"pregunta": null}', "formato"),
    ('{"texto": "", "pregunta": null}', "formato"),
    ('{"texto": 3}', "formato"),
    ('{"texto": "Hola", "pregunta": 3}', "formato"),
    ('{"texto": "Hola", "afirma": "c1"}', "formato"),
    ('{"texto": "Hola", "afirma": [1]}', "formato"),
])
def test_una_salida_que_no_es_la_pedida_se_rechaza_con_su_motivo(crudo, motivo):
    resultado = leer_borrador(crudo)
    assert isinstance(resultado, str) and resultado.startswith(motivo)
