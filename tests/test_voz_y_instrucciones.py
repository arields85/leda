"""La personalidad de Leda y las instrucciones del alta conversada, armadas por el
código desde una sola fuente (C0-13 y C0-15, `odd/tasks/circuitos-al-flujo-nuevo.md`).

- `nucleo/personalidad.md` es la personalidad del producto, igual para todos los
  clientes: la referencia con la que se escribe la mecánica de cada circuito. No se le
  manda a la IA (flujo C3, C0-15); el cumplimiento de la mecánica lo comprueba
  `tests/test_personalidad_en_mecanica.py`. El nombre del archivo de pruebas conserva
  "voz" por historia; "voz" queda para las respuestas con audio.
- El tono de cada cliente (trato, formalidad, emojis) sale de su pack
  (`persona_config`) y lo agrega el código según el espacio. Nada de "voseo" escrito
  en el código del alta.
- Orden estable: mecánica del alta, tono del espacio; lo que cambia por turno
  (hechos, historial) viaja aparte.
- La huella de las instrucciones armadas queda en la auditoría de cada turno del alta.
- Un tope de tamaño que falla a la vista.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from leda import alta_turno as T
from leda import instrucciones as INS
from leda.config import config
from leda.db import admin

from tests.test_alta_conducida import chat, conversada, salida  # noqa: F401

RAIZ = Path(__file__).resolve().parent.parent
VOS = INS.Tono(nombre_visible="Leda", registro="vos",
               formalidad="profesional_cordial", longitud="breve", emojis=False)
USTED = INS.Tono(nombre_visible="Leda", registro="usted",
                 formalidad="formal", longitud="breve", emojis=False)


def _texto_de_la_personalidad() -> str:
    return (config.nucleo / "personalidad.md").read_text(encoding="utf-8")


def _cuerpo_de_la_personalidad() -> str:
    """Lo que sigue a la línea divisoria: la personalidad, sin el encabezado de
    núcleo para quien la mantiene."""
    encabezado, separador, cuerpo = _texto_de_la_personalidad().partition("\n---\n")
    assert separador and cuerpo.strip()
    return cuerpo.strip()


# ---------------------------------------------------------- la personalidad

def test_la_personalidad_existe_con_su_encabezado_de_nucleo():
    encabezado = _texto_de_la_personalidad().partition("\n---\n")[0]
    assert "constitucion.md" in encabezado and "administrador" in encabezado
    assert "administrador" not in _cuerpo_de_la_personalidad().split("\n")[0]


def test_la_personalidad_es_del_producto_sin_tono_ni_vocabulario_de_un_cliente():
    cuerpo = _cuerpo_de_la_personalidad().lower()
    for marca in ("voseo", "corework", "usted"):
        assert marca not in cuerpo, marca


def test_las_instrucciones_del_alta_empiezan_por_la_mecanica():
    texto = INS.instrucciones_alta(VOS).texto
    assert texto.startswith(T.MECANICA_ALTA)
    assert _cuerpo_de_la_personalidad() not in texto


def test_el_orden_es_mecanica_y_tono():
    texto = INS.instrucciones_alta(USTED).texto
    mecanica = texto.index(T.MECANICA_ALTA)
    tono = texto.index(INS.bloque_de_tono(USTED))
    assert mecanica < tono


# ------------------------------------------------------------- el tono del pack

def test_con_registro_usted_no_hay_voseo():
    texto = INS.instrucciones_alta(USTED).texto
    assert "usted" in INS.bloque_de_tono(USTED)
    assert "voseo" not in texto.lower() and "de vos" not in texto.lower()


def test_con_registro_vos_el_tono_lo_pide():
    tono = INS.bloque_de_tono(VOS)
    assert "de vos" in tono or "voseo" in tono


def test_el_tono_sale_del_pack_y_no_del_codigo_del_alta():
    fuente = (RAIZ / "src" / "leda" / "alta_turno.py").read_text(encoding="utf-8")
    assert "voseo" not in fuente.lower()
    assert "voseo" not in T.MECANICA_ALTA.lower()


def test_sin_tono_configurado_no_se_inventa_un_registro():
    tono = INS.bloque_de_tono(None)
    assert "vos" not in tono.split() and "usted" not in tono


def test_las_instrucciones_se_arman_una_vez_por_tono():
    assert INS.instrucciones_alta(VOS) is INS.instrucciones_alta(VOS)


# ------------------------------------------------------------------ la huella

def test_la_huella_es_del_texto_armado():
    instr = INS.instrucciones_alta(VOS)
    assert instr.hash == hashlib.sha256(instr.texto.encode("utf-8")).hexdigest()
    assert INS.instrucciones_alta(USTED).hash != instr.hash


def test_el_turno_del_alta_usa_las_instrucciones_y_audita_su_huella(chat):
    c = chat(salida("Anotado. ¿A qué objetivo pertenece?",
                    valores={"title": {"texto": "Calibrar sensores del laboratorio"}},
                    pregunta=["objective"], botones="objective"))

    c.escribir("necesito crear una tarea: calibrar sensores del laboratorio")

    sistema = c.modelo.conducidos[0][0]
    with admin(c.conn) as cur:
        cur.execute("select detalle from audit_log "
                    "where accion = 'alta_conducida_turno'")
        (detalle,) = [f["detalle"] for f in cur.fetchall()]
    assert sistema.startswith(T.MECANICA_ALTA)
    assert _cuerpo_de_la_personalidad() not in sistema
    assert "voz_hash" not in detalle
    assert detalle["instrucciones_hash"] == hashlib.sha256(
        sistema.encode("utf-8")).hexdigest()


# ------------------------------------------------------------------ el tope

@pytest.mark.parametrize("tono", [VOS, USTED, None])
def test_las_instrucciones_del_alta_entran_en_su_tope(tono):
    texto = INS.instrucciones_alta(tono).texto
    tokens = INS.tokens_estimados(texto)
    assert tokens <= INS.TOPE_TOKENS_ALTA, (
        f"Las instrucciones del alta miden ~{tokens} tokens "
        f"({len(texto)} caracteres); el tope es {INS.TOPE_TOKENS_ALTA}.")


# ---------------------------- lo que la personalidad pone en la mecánica, una vez

# Reglas de la personalidad escritas como reglas de la mecánica del alta: cada una
# aparece una sola vez en las instrucciones que recibe la IA.
_REGLAS_EN_LA_MECANICA = (
    "un solo dato",            # una sola pregunta, de un dato
    "no inventa",              # honestidad: sólo hechos del JSON
    "anoté",                   # nunca un efecto sin comprobante (H5)
    "orden seca",              # pide, no ordena
    "para qué hace falta",     # ante un dato faltante
    "entendí que",             # sin fórmulas de formulario
    "texto plano",             # sin Markdown
)


@pytest.mark.parametrize("regla", _REGLAS_EN_LA_MECANICA)
def test_cada_regla_de_la_personalidad_aparece_una_sola_vez(regla):
    def plano(texto: str) -> str:
        return " ".join(texto.lower().split())

    assert plano(INS.instrucciones_alta(VOS).texto).count(regla) == 1, regla


def test_la_mecanica_del_alta_no_le_habla_a_la_ia_de_vos():
    mecanica = T.MECANICA_ALTA.lower()
    for adjetivo in ("colega", "con naturalidad y decí", "ayudá y facilitá"):
        assert adjetivo not in mecanica, adjetivo


# ------------------------------- personalidad y trato (C0-13, 2.ª unidad)

def _seccion(titulo: str) -> str:
    cuerpo = _cuerpo_de_la_personalidad()
    assert f"## {titulo}" in cuerpo, titulo
    return cuerpo.split(f"## {titulo}", 1)[1].split("\n## ", 1)[0]


def test_la_personalidad_tiene_rasgos_como_rasgo_conducta_y_limite():
    seccion = _seccion("Personalidad y trato")
    rasgos = [l for l in seccion.splitlines() if l.startswith("- **")]
    assert len(rasgos) >= 10, rasgos
    for rasgo in ("Cálida", "Cordial", "Amable", "Clara", "Respetuosa",
                  "Persistente", "Transparente"):
        assert f"**{rasgo}" in seccion, rasgo
    plano = " ".join(seccion.split())
    assert "por favor" in plano
    assert "no juzga intenciones" in plano.lower()
    assert "vigilad" in plano            # el seguimiento no hace sentir vigilada a nadie
    assert "falta personal" in plano     # un bloqueo a tiempo no es una falta


def test_la_personalidad_no_nombra_botones_ajenos_ni_saluda_por_su_cuenta():
    plano = " ".join(_cuerpo_de_la_personalidad().split())
    assert ("Leda nunca nombra un botón que no esté entre las opciones que "
            "recibe") in plano
    assert "Leda no saluda por su cuenta: el saludo del día lo agrega el sistema" in plano


def test_los_emojis_no_van_en_la_personalidad():
    assert "emoji" not in _cuerpo_de_la_personalidad().lower()


# ------------------------------------------------------- emojis desde el pack

def test_con_emojis_el_tono_pide_alguno_ocasional_y_no_de_adorno():
    tono = INS.bloque_de_tono(INS.Tono(registro="vos", emojis=True)).lower()
    assert "ocasional" in tono and "no en cada respuesta" in tono and "adorno" in tono
    assert "sin emojis" not in tono


def test_sin_emojis_el_tono_lo_dice():
    assert "sin emojis" in INS.bloque_de_tono(VOS).lower()


def test_el_pack_de_corework_permite_emojis():
    import yaml
    pack = yaml.safe_load((RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    assert pack["persona"]["emojis"] is True


def test_el_tope_del_alta_es_de_1300_tokens():
    assert INS.TOPE_TOKENS_ALTA == 1300
