"""La voz de Leda y las instrucciones del alta conversada, armadas por el código
desde una sola fuente (C0-13, `odd/tasks/circuitos-al-flujo-nuevo.md`).

- `nucleo/voz.md` es la voz del producto, igual para todos los clientes; el tono de
  cada cliente (trato, formalidad, emojis) sale de su pack (`persona_config`) y lo
  agrega el código según el espacio. Nada de "voseo" escrito en el código del alta.
- Orden estable: voz, mecánica del alta, tono del espacio; lo que cambia por turno
  (hechos, historial) viaja aparte.
- La huella de la voz y la de las instrucciones armadas quedan en la auditoría de
  cada turno del alta: se puede probar qué voz se cargó.
- Un tope de tamaño que falla a la vista.
- Lo que cubre la voz no se repite en la mecánica del alta.
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


def _cuerpo_de_la_voz() -> str:
    texto = (config.nucleo / "voz.md").read_text(encoding="utf-8")
    return INS.cuerpo_de_la_voz(texto)


# ------------------------------------------------------------------ la voz

def test_la_voz_existe_con_su_encabezado_de_nucleo_y_cuerpo_para_el_modelo():
    texto = (config.nucleo / "voz.md").read_text(encoding="utf-8")
    encabezado, _, cuerpo = texto.partition("\n---\n")
    assert "constitucion.md" in encabezado and "administrador" in encabezado
    assert cuerpo.strip()
    # El encabezado es para las personas que la mantienen; el modelo lee el cuerpo.
    assert "administrador" not in INS.cuerpo_de_la_voz(texto).split("\n")[0]


def test_la_voz_es_del_producto_sin_tono_ni_vocabulario_de_un_cliente():
    cuerpo = _cuerpo_de_la_voz().lower()
    for marca in ("voseo", "corework", "usted"):
        assert marca not in cuerpo, marca


def test_las_instrucciones_del_alta_empiezan_por_la_voz():
    texto = INS.instrucciones_alta(VOS).texto
    assert texto.startswith(_cuerpo_de_la_voz())
    assert T.MECANICA_ALTA in texto


def test_el_orden_es_voz_mecanica_y_tono():
    texto = INS.instrucciones_alta(USTED).texto
    voz = texto.index(_cuerpo_de_la_voz())
    mecanica = texto.index(T.MECANICA_ALTA)
    tono = texto.index(INS.bloque_de_tono(USTED))
    assert voz < mecanica < tono


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


# ------------------------------------------------------------------ las huellas

def test_las_huellas_son_de_la_voz_y_del_texto_armado():
    instr = INS.instrucciones_alta(VOS)
    voz = (config.nucleo / "voz.md").read_text(encoding="utf-8")
    assert instr.voz_hash == hashlib.sha256(voz.encode("utf-8")).hexdigest()
    assert instr.hash == hashlib.sha256(instr.texto.encode("utf-8")).hexdigest()
    assert INS.instrucciones_alta(USTED).hash != instr.hash
    assert INS.instrucciones_alta(USTED).voz_hash == instr.voz_hash


def test_el_turno_del_alta_usa_las_instrucciones_y_audita_sus_huellas(chat):
    c = chat(salida("Anotado. ¿A qué objetivo pertenece?",
                    valores={"title": {"texto": "Calibrar sensores del laboratorio"}},
                    pregunta=["objective"], botones="objective"))

    c.escribir("necesito crear una tarea: calibrar sensores del laboratorio")

    sistema = c.modelo.conducidos[0][0]
    with admin(c.conn) as cur:
        cur.execute("select detalle from audit_log "
                    "where accion = 'alta_conducida_turno'")
        (detalle,) = [f["detalle"] for f in cur.fetchall()]
    assert sistema.startswith(_cuerpo_de_la_voz())
    voz = (config.nucleo / "voz.md").read_text(encoding="utf-8")
    assert detalle["voz_hash"] == hashlib.sha256(voz.encode("utf-8")).hexdigest()
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


# ------------------------------------------------- lo que dice la voz, una vez

# Reglas que ahora cubre la voz: no se repiten en la mecánica del alta.
_REGLAS_DE_LA_VOZ = (
    "una sola pregunta",       # ante un dato faltante, una sola pregunta clara
    "no inventa",              # honestidad
    "anoté",                   # nunca un efecto sin comprobante (H5)
    "voy a consultar",         # no anunciar: responder con el resultado
    "no sé todavía",           # es seguro no saber
    "entendí que",             # sin fórmulas de formulario
    "jerga",                   # sin detalles técnicos
    "markdown",                # texto plano de chat
)


@pytest.mark.parametrize("regla", _REGLAS_DE_LA_VOZ)
def test_cada_regla_de_la_voz_aparece_una_sola_vez(regla):
    def plano(texto: str) -> str:          # el Markdown corta líneas en cualquier lado
        return " ".join(texto.lower().split())

    assert regla in plano(_cuerpo_de_la_voz()), regla
    assert regla not in plano(T.MECANICA_ALTA), regla
    assert plano(INS.instrucciones_alta(VOS).texto).count(regla) == 1, regla


def test_la_mecanica_del_alta_no_repite_el_trato_de_la_voz():
    mecanica = T.MECANICA_ALTA.lower()
    for adjetivo in ("cordial", "colega", "con naturalidad y decí", "ayudá y facilitá"):
        assert adjetivo not in mecanica, adjetivo


# ------------------------------------------- personalidad y trato (C0-13, 2.ª unidad)

def _seccion(titulo: str) -> str:
    cuerpo = _cuerpo_de_la_voz()
    assert f"## {titulo}" in cuerpo, titulo
    return cuerpo.split(f"## {titulo}", 1)[1].split("\n## ", 1)[0]


def test_la_voz_tiene_personalidad_y_trato_como_rasgo_conducta_y_limite():
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


def test_la_voz_no_nombra_botones_ajenos_ni_saluda_por_su_cuenta():
    plano = " ".join(_cuerpo_de_la_voz().split())
    assert ("Leda nunca nombra un botón que no esté entre las opciones que "
            "recibe") in plano
    assert "Leda no saluda por su cuenta: el saludo del día lo agrega el sistema" in plano


def test_los_emojis_no_van_en_la_voz():
    assert "emoji" not in _cuerpo_de_la_voz().lower()


# ------------------------------------------------------- emojis desde el pack

def test_con_emojis_el_tono_pide_alguno_ocasional_y_no_de_adorno():
    tono = INS.bloque_de_tono(INS.Tono(registro="vos", emojis=True)).lower()
    assert "ocasional" in tono and "no en cada respuesta" in tono and "adorno" in tono
    assert "sin emojis" not in tono


def test_sin_emojis_el_tono_lo_dice():
    assert "sin emojis" in INS.bloque_de_tono(VOS).lower()


def test_el_tope_del_alta_es_de_2500_tokens():
    assert INS.TOPE_TOKENS_ALTA == 2500
