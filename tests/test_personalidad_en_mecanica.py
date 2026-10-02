"""La personalidad de Leda va adentro de la mecánica del alta, no aparte (flujo C3,
C0-15, `odd/tasks/circuitos-al-flujo-nuevo.md`).

`nucleo/personalidad.md` es la referencia de cómo es y cómo se comporta Leda: con ella
se escribe la mecánica de cada circuito, pero no se le manda a la IA. La medición del
2026-10-02 mostró que una personalidad aparte contradecía la mecánica ("hasta dos
datos" contra "una sola pregunta") y sumaba latencia. Estas pruebas comprueban que la
mecánica del alta cumple la personalidad como reglas concretas de su contrato, sin
contradicciones, y que el tono de cada cliente sigue saliendo de su pack.
"""

from __future__ import annotations

import re

import pytest

from leda import alta_turno as T
from leda import instrucciones as INS
from leda.config import config

VOS = INS.Tono(nombre_visible="Leda", registro="vos",
               formalidad="profesional_cordial", longitud="breve", emojis=True)
USTED = INS.Tono(nombre_visible="Leda", registro="usted",
                 formalidad="formal", longitud="breve", emojis=False)


def _plano(texto: str) -> str:
    """Sin cortes de línea ni mayúsculas: las reglas se buscan por su sentido."""
    return " ".join(texto.lower().split())


MECANICA = _plano(T.MECANICA_ALTA)


def _cuerpo_de_la_personalidad() -> str:
    texto = (config.nucleo / "personalidad.md").read_text(encoding="utf-8")
    return texto.partition("\n---\n")[2].strip()


# ---------------------------------------------- la personalidad no viaja a la IA

def test_la_personalidad_es_un_archivo_del_nucleo_y_la_voz_ya_no_existe():
    assert (config.nucleo / "personalidad.md").is_file()
    assert not (config.nucleo / "voz.md").exists()


def test_el_encabezado_dice_que_es_referencia_y_no_se_le_manda_a_la_ia():
    texto = (config.nucleo / "personalidad.md").read_text(encoding="utf-8")
    encabezado = _plano(texto.partition("\n---\n")[0])
    assert encabezado.startswith("# la personalidad de leda")
    assert "referencia" in encabezado and "no se le manda a la ia" in encabezado
    assert "constitucion.md" in encabezado and "administrador" in encabezado
    assert "audio" in encabezado        # "voz" queda para las respuestas con audio


def test_la_referencia_no_le_habla_a_la_ia():
    # Era instrucciones para la IA; ahora es referencia (flujo C4, aprobado por el
    # usuario el 2026-10-02).
    assert "quien lee estas instrucciones" not in _plano(_cuerpo_de_la_personalidad())


@pytest.mark.parametrize("tono", [VOS, USTED, None])
def test_las_instrucciones_del_alta_no_llevan_la_personalidad(tono):
    texto = INS.instrucciones_alta(tono).texto
    cuerpo = _cuerpo_de_la_personalidad()
    assert cuerpo not in texto
    for seccion in ("## Personalidad y trato", "## Cómo conversa",
                    "## Honestidad", "## Lo que nunca muestra"):
        assert seccion in cuerpo and seccion not in texto, seccion


def test_las_instrucciones_son_la_mecanica_y_el_tono_del_pack():
    texto = INS.instrucciones_alta(USTED).texto
    assert texto.startswith(T.MECANICA_ALTA)
    assert texto.endswith(INS.bloque_de_tono(USTED))


def test_la_auditoria_lleva_solo_la_huella_de_lo_que_recibe_la_ia():
    instr = INS.instrucciones_alta(VOS)
    assert instr.auditoria() == {"instrucciones_hash": instr.hash}
    assert not hasattr(instr, "voz_hash")


# ---------------------------------------------------- un solo dato por pregunta

def test_la_pregunta_pide_un_solo_dato():
    assert "un solo dato" in MECANICA


@pytest.mark.parametrize("permiso", ["hasta dos", "dos datos", "o dos datos",
                                     "uno o dos", "dos preguntas"])
def test_ninguna_regla_permite_pedir_dos_datos(permiso):
    assert permiso not in MECANICA, permiso
    esquema = _plano(str(T.ESQUEMA_SALIDA))
    assert permiso not in esquema, permiso


# ------------------------------------------------- el largo, una sola regla

_LARGO = re.compile(r"\b(una|uno)\s+(?:a|o)\s+(dos|tres|cuatro)\s+oraciones")


def test_el_largo_del_texto_es_el_mismo_en_el_esquema_y_en_la_mecanica():
    descripcion = _plano(T.ESQUEMA_SALIDA["properties"]["texto"]["description"])
    en_esquema = {m.group(0) for m in _LARGO.finditer(descripcion)}
    en_mecanica = {m.group(0) for m in _LARGO.finditer(MECANICA)}
    assert en_esquema == en_mecanica == {"una o dos oraciones"}, (
        en_esquema, en_mecanica)
    assert "tres oraciones" not in MECANICA + descripcion


# ------------------------------------------- las reglas de la personalidad

def test_primero_reconoce_lo_que_dijo_la_persona_y_despues_pregunta():
    assert "primero reconoce" in MECANICA and "después la pregunta" in MECANICA
    regla = MECANICA[MECANICA.index("primero reconoce"):
                     MECANICA.index("después la pregunta")]
    assert "repetir datos ya claros" in regla


@pytest.mark.parametrize("efecto", ["anoté", "quedó registrado", "guardado"])
def test_nunca_da_por_hecho_un_efecto_que_el_sistema_no_hizo(efecto):
    # Los nombra para prohibirlos, junto con la razón: la tarea no existe todavía.
    assert efecto in MECANICA, efecto
    regla = MECANICA[MECANICA.index("anoté") - 200:MECANICA.index("anoté") + 200]
    assert "nunca" in regla and "efecto" in regla


def test_pide_con_una_pregunta_y_nunca_con_una_orden_seca():
    assert "orden seca" in MECANICA
    assert "«decime" in MECANICA         # nombrada como lo que no se hace


def test_ante_una_duda_propone_algo_concreto():
    assert "no sé" in MECANICA
    regla = MECANICA[MECANICA.index("no sé"):MECANICA.index("no sé") + 200]
    assert "propone" in regla and "concret" in regla


def test_ante_la_frustracion_lo_reconoce_y_sigue():
    assert "ya te lo dije" in MECANICA
    regla = MECANICA[MECANICA.index("ya te lo dije"):
                     MECANICA.index("ya te lo dije") + 120]
    assert "reconoce" in regla and "sigue" in regla


def test_ante_un_dato_faltante_dice_para_que_hace_falta():
    assert "para qué hace falta" in MECANICA


# ----------------------- flujo C4: ajustes después de la medición C3 (2026-10-02)

def _alrededor(clave: str, ancho: int = 220) -> str:
    assert clave in MECANICA, clave
    i = MECANICA.index(clave)
    return MECANICA[max(0, i - ancho):i + ancho]


def test_al_pedir_un_dato_usa_por_favor_o_el_condicional():
    # Con la regla blanda, 0 de 90 textos medidos lo decían.
    regla = _alrededor("«por favor»")
    assert "condicional" in regla and "pedir un dato" in regla


def test_un_titulo_que_no_dice_que_hacer_se_aclara_antes_de_seguir():
    # C3 aceptó «lo del tablero» como título en 3 de 3 corridas.
    regla = _alrededor("no dice qué hay que hacer")
    assert "propone un título" in regla and "aceptar o cambiar" in regla
    assert "antes de seguir" in regla


def test_usa_el_nombre_de_pila_de_vez_en_cuando():
    regla = _alrededor("nombre_de_pila")
    assert "de vez en cuando" in regla and "no en cada mensaje" in regla


def test_si_el_mensaje_trae_varios_datos_no_los_repasa_todos():
    # Todas las variantes repasaron cada dato en el primer turno (9 de 9).
    regla = _alrededor("varios datos")
    assert "no los repasa" in regla and "lo esencial" in regla
    assert "sólo lo que falta" in regla


def test_la_personalidad_general_en_pocas_lineas():
    for rasgo in ("cálida", "cordial", "breve", "soluciones", "elogios",
                  "fórmula de cortesía"):
        assert rasgo in MECANICA, rasgo


@pytest.mark.parametrize("regla", [
    "texto plano",                  # sin Markdown ni listas
    "no saluda",                    # el saludo del día lo agrega el sistema
    "sólo hechos",                  # no inventa: los datos salen del JSON
    "podes_ofrecer",                # sólo ofrece lo que se puede
    "boton_final",                  # nunca un botón que no se muestra
])
def test_las_reglas_operativas_del_alta_siguen_en_la_mecanica(regla):
    assert regla in MECANICA, regla


def test_no_muestra_nada_interno():
    assert "nunca muestra nada interno" in MECANICA
    regla = MECANICA[MECANICA.index("nunca muestra nada interno"):][:120]
    for interno in ("campos", "ids", "herramientas", "errores", "razonamiento"):
        assert interno in regla, interno


# ------------------------------------------------- el tono sigue en el pack

def test_el_trato_y_los_emojis_salen_del_pack_y_no_de_la_mecanica():
    for marca in ("voseo", "de vos", "usted", "emoji"):
        assert marca not in MECANICA, marca
    con_vos = INS.instrucciones_alta(VOS).texto
    con_usted = INS.instrucciones_alta(USTED).texto
    assert "de vos" in con_vos and "ocasional" in con_vos
    assert "de usted" in con_usted and "sin emojis" in con_usted.lower()
    assert "de vos" not in con_usted


# ---------------------------------------------------------------- el tope

def test_el_tope_del_alta_es_de_1300_tokens():
    assert INS.TOPE_TOKENS_ALTA == 1300


@pytest.mark.parametrize("tono", [VOS, USTED, None])
def test_las_instrucciones_del_alta_entran_en_el_tope_nuevo(tono):
    texto = INS.instrucciones_alta(tono).texto
    assert INS.tokens_estimados(texto) <= 1300, (
        f"~{INS.tokens_estimados(texto)} tokens ({len(texto)} caracteres)")
