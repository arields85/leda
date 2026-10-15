"""Las palabras de la redacción: ningún nombre que la IA recibe para redactar nombra un concepto
de la cocina (`leda.motor.hechos`).

Las palabras de todos los días (usuario, 2026-10-07; conversación 19): con los significados ya
reescritos, la IA real seguía escribiendo "si se cumple esa previsión", porque el pedido de
redacción traía claves y códigos con el nombre del concepto (`prevision`,
`atraso_si_se_cumple_la_prevision_dias_habiles`, `nueva_prevision`, `"jugada":
"anotar_prevision"`). Lo que la IA lee como nombre, lo repite como palabra.

Se recorren las tablas reales del motor, no una lista a mano: cada clave y cada código con
significado, cada jugada, cada tipo de pregunta y de aviso, cada dato de una jugada y lo que un
aviso dice de si llega.
"""

from __future__ import annotations

import json
import re

from leda.motor import avisos, hechos, preguntas
from leda.motor.fichas import (ESPERA_ALGO_CIERTO, FICHAS, LLEGA, NO_LE_LLEGO, NO_LE_VA_A_LLEGAR,
                               SALIDAS_DE_UN_BLOQUEO, YA_LE_LLEGO)
from leda.motor.ia_real import DATOS
from leda.motor.instrucciones import INSTRUCCIONES_REDACCION

from tests.motor.ayudantes import (ProveedorFalso, a_la_vista, ia_real_falsa, respuesta_de_texto,
                                   solo_si_pregunta)

NOMBRES = sorted(set(hechos.SIGNIFICADOS) | set(FICHAS) | set(preguntas.TIPOS)
                 | set(avisos.TIPOS) | set(DATOS)
                 | {LLEGA, YA_LE_LLEGO, NO_LE_VA_A_LLEGAR, NO_LE_LLEGO}
                 | set(SALIDAS_DE_UN_BLOQUEO) | set(ESPERA_ALGO_CIERTO))


def _lo_que_recibe_la_redaccion(pedido: dict) -> tuple[dict, str]:
    """Los datos y las instrucciones (con la lista de significados) que la IA real recibe."""
    proveedor = ProveedorFalso([respuesta_de_texto("Hola.")])
    ia_real_falsa(proveedor).redactar(pedido)
    sistema, usuario = proveedor.pedidos[0]["cuerpo"]["messages"]
    return json.loads(usuario["content"]), sistema["content"]


def _con_todos_los_nombres() -> dict:
    """Un pedido de redacción con cada nombre del motor como clave y como código, en los
    hechos y en los últimos turnos."""
    todos = [{nombre: nombre} for nombre in NOMBRES]
    return {"hoy": "2026-10-20", "persona": "Marcos", "mensaje": None, "hechos": todos,
            "pregunta": None,
            "ultimos_turnos": [{"sentido": "salida", "texto": "Anotado.", "hechos": todos}]}


def test_ningun_nombre_que_recibe_la_redaccion_es_un_concepto_de_la_cocina():
    recibido, _ = _lo_que_recibe_la_redaccion(_con_todos_los_nombres())

    conceptos = {n for n in hechos._nombres(recibido) if hechos.es_un_concepto_de_la_cocina(n)}
    assert not conceptos, sorted(conceptos)


def test_cada_nombre_que_recibe_la_redaccion_tiene_su_significado():
    recibido, sistema = _lo_que_recibe_la_redaccion(_con_todos_los_nombres())

    assert hechos.sin_significado(recibido) == set()
    lista = sistema.split(hechos.ENCABEZADO_DEL_BLOQUE, 1)[1].split("\n\n", 1)[0]
    explicados = [linea[2:].split(":", 1)[0] for linea in lista.strip().splitlines()]
    assert set(explicados) == set(hechos._nombres(recibido))
    for nombre in explicados:
        assert f"- {nombre}: {hechos.significado(nombre)}" in lista.splitlines(), nombre
    assert not [n for n in explicados if hechos.es_un_concepto_de_la_cocina(n)]


def test_cada_nombre_para_redactar_dice_lo_mismo_y_no_choca_con_otro():
    """Un nombre de la cocina y el suyo para redactar significan lo mismo; ninguno para
    redactar es un nombre de la cocina, ni de otra cosa, ni nombra un concepto."""
    cocina = set(NOMBRES)
    para = hechos.PARA_LA_REDACCION
    assert len(set(para.values())) == len(para)
    assert not set(para.values()) & cocina
    assert set(para) <= cocina
    for de, a in para.items():
        assert hechos.significado(a) == hechos.significado(de), de
        assert hechos._CODIGO.match(a), a           # como valor, también se lee como código
        assert not hechos.es_un_concepto_de_la_cocina(a), a
    assert {n for n in NOMBRES if hechos.es_un_concepto_de_la_cocina(n)} == set(para)


# --- The meanings and the moves' sentences also reach the AI (task "Lenguaje", 2026-10-15) ----
#
# The names are guarded above; the AI also reads each name's meaning (`hechos.SIGNIFICADOS`, in
# the list of meanings) and what each move is for (`Ficha.para_que`, when Leda says what she can
# do). A cooking concept written there as prose ("el reencuadre", "un aviso previo") is copied
# just the same, so the same words are checked there, written as prose: without underscores and
# without accents.

# Prose that matches a concept's words but does not name the concept, each with why.
NO_NOMBRAN_EL_CONCEPTO = {
    # The task's state itself, not Leda asking how a task is going.
    ("estado", "el_estado"),
    ("tareas_que_esperaba", "el_estado"),
    # Question types: the question of this message keeps "pregunta" (decision 78).
    ("cuando_se_destraba", "pregunta_a_quien"),
    ("decidir_el_pase", "pregunta_a_quien"),
    ("tomar_la_tarea", "pregunta_a_quien"),
    # "Aprobar" stays for the decision itself (decision 18); rewording it would change what the
    # AI is told about who decides.
    ("la_aprobo_al_entregarla", "para_aprobar"),
}


def _sin_acentos(texto: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower())
                   if unicodedata.category(c) != "Mn")


def _conceptos_en_la_prosa() -> set[tuple[str, str]]:
    textos = [(n, s) for n, s in hechos.SIGNIFICADOS.items()]
    textos += [(n, f.para_que) for n, f in FICHAS.items()]
    return {(nombre, concepto) for nombre, texto in textos
            for concepto in hechos.CONCEPTOS_DE_LA_COCINA
            if re.search(r"\b" + re.escape(concepto.replace("_", " ")), _sin_acentos(texto))}


def test_ningun_significado_ni_para_que_nombra_un_concepto_de_la_cocina():
    encontrados = _conceptos_en_la_prosa()

    assert encontrados - NO_NOMBRAN_EL_CONCEPTO == set()
    # An exception that no longer matches is dropped from the list.
    assert NO_NOMBRAN_EL_CONCEPTO <= encontrados, sorted(NO_NOMBRAN_EL_CONCEPTO - encontrados)


# --- What is missing and who handles it, never "trabada" (task "Lenguaje", porción 2) ----------
#
# User decision (2026-10-15): in everything a person sees, Leda says what is missing and who is
# handling it ("¿te falta algo para seguir?", "está esperando el cable, que consigue Mariano",
# "ya puede seguir"), never "trabada", "se trabó", "destrabar" or "bloqueo". In conversation 55
# Leda wrote 25 times "Contame si la empezaste, para cuándo la terminás o si está trabada.",
# copying the code `si_esta_trabada`. The kitchen keeps its names (the database state
# `bloqueada`, the moves, the stored facts); at the drafting boundary every name, code, meaning
# and move purpose says it with the new words. "Trabajo" is another word and stays.
# Not inside another word ("mostraba"), and "trabajo" is another word.
TRABADA = re.compile(r"(?<![a-z])(?:des)?trab(?!aj)|bloque[oa]")


def test_ningun_nombre_para_redactar_dice_trabada_ni_bloqueo():
    dicen = sorted({hechos.para_redactar(n) for n in NOMBRES
                    if TRABADA.search(hechos.para_redactar(n))})
    assert dicen == []


def test_ningun_significado_ni_para_que_dice_trabada_ni_bloqueo():
    textos = [(n, s) for n, s in hechos.SIGNIFICADOS.items()]
    textos += [(n, f.para_que) for n, f in FICHAS.items()]
    dicen = sorted(n for n, texto in textos if TRABADA.search(_sin_acentos(texto)))
    assert dicen == []


def test_lo_que_recibe_la_redaccion_no_dice_trabada_ni_bloqueo():
    """What the real AI gets to draft: the facts, the last turns and the list of meanings."""
    recibido, sistema = _lo_que_recibe_la_redaccion(_con_todos_los_nombres())

    assert sorted(n for n in hechos._nombres(recibido) if TRABADA.search(n)) == []
    lista = sistema.split(hechos.ENCABEZADO_DEL_BLOQUE, 1)[1].split("\n\n", 1)[0]
    assert [m.group(0) for m in TRABADA.finditer(_sin_acentos(lista))] == []


def test_lo_que_falta_saber_dice_si_le_falta_algo_para_seguir():
    """Conversation 55: the code the AI copied is now what is missing to keep going."""
    assert hechos.para_redactar("si_esta_trabada") == "si_le_falta_algo_para_seguir"
    assert hechos.para_redactar("bloqueada") == "esperando_algo_para_seguir"
    assert hechos.para_redactar("se_destrabo") == "dijo_que_ya_puede_seguir"
    assert hechos.para_redactar("quien_destraba") == "quien_se_ocupa_de_lo_que_falta"
    pedido = {"hoy": "2026-10-20", "persona": "Marcos", "mensaje": None, "pregunta": None,
              "hechos": [{"aviso": "pedido_de_estado", "tarea": "Cablear el tablero",
                          "estado": "asignada",
                          "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina",
                                                 "si_esta_trabada"]},
                         {"jugada": "consultar_pendientes",
                          "tareas": [{"titulo": "Pedir el cable", "estado": "bloqueada"}]}],
              "ultimos_turnos": []}

    recibido, _ = _lo_que_recibe_la_redaccion(pedido)

    assert recibido["hechos"][0]["espera_algo_cierto"] == [
        "si_la_empezo", "para_cuando_la_termina", "si_le_falta_algo_para_seguir"]
    assert recibido["hechos"][1]["tareas"][0]["estado"] == "esperando_algo_para_seguir"
    assert pedido["hechos"][1]["tareas"][0]["estado"] == "bloqueada"   # the kitchen's, untouched


def test_el_motivo_de_un_incidente_al_administrador_no_dice_trabada():
    """The administrator is a person too: the reason an incident gives says it in words."""
    from leda.motor.asentado import por_que_no_hay_a_quien
    from leda.motor.persecucion import INACTIVO, SIN_REFERENTE, SIN_TELEGRAM

    for motivo in (SIN_REFERENTE, INACTIVO, SIN_TELEGRAM):
        assert not TRABADA.search(por_que_no_hay_a_quien(motivo)), motivo


def test_lo_que_alguien_escribio_llega_tal_cual():
    """El mensaje de la persona y los textos de los últimos turnos son lo que alguien escribió:
    nunca se traducen, aunque nombren un concepto o sean una sola palabra de la cocina."""
    pedido = {"hoy": "2026-10-20", "persona": "Marcos", "mensaje": "escalamiento",
              "hechos": [{"jugada": "anotar_prevision", "prevision": "2026-10-27",
                          "motivo": "el proveedor se demoró"}],
              "pregunta": None,
              "ultimos_turnos": [{"sentido": "entrada", "texto": "que es prevision?"},
                                 {"sentido": "salida", "texto": "reencuadre"}]}

    recibido, _ = _lo_que_recibe_la_redaccion(pedido)

    assert recibido["mensaje"] == "escalamiento"
    assert [t["texto"] for t in recibido["ultimos_turnos"]] == ["que es prevision?",
                                                               "reencuadre"]
    assert recibido["hechos"] == [{"jugada": "anotar_para_cuando_la_termina",
                                   "dia_que_dio_para_terminarla": "2026-10-27",
                                   "motivo": "el proveedor se demoró"}]
    assert pedido["hechos"][0]["jugada"] == "anotar_prevision"      # el original, sin tocar


def test_la_instruccion_de_redaccion_no_nombra_un_concepto_de_la_cocina():
    """Si la instrucción nombrara una clave por su nombre de la cocina, la IA no la
    encontraría en los datos."""
    palabras = set(re.findall(r"[a-z_]+", INSTRUCCIONES_REDACCION))
    # Los verbos sueltos de algunas jugadas también son palabras de la instrucción.
    verbos = {"elegir", "corregir", "cancelar", "destrabar", "entregar"}
    assert not palabras & (set(hechos.PARA_LA_REDACCION) - verbos)


# --- Quien aprueba el trabajo de la persona, sólo si lo pregunta (usuario, 2026-10-08) --------

def test_quien_aprueba_el_trabajo_de_la_persona_llega_a_la_redaccion_solo_si_pregunta():
    """Decisión 11: Leda no nombra por su cuenta a quien aprueba el trabajo de la persona a la
    que le escribe, ni como motivo ni al contar un hecho. Cada dato de la cocina que lo nombra
    le llega a la redacción con el nombre dentro de `solo_si_pregunta`, en el mismo lugar; lo
    demás del dato, a la vista."""
    aviso = {"a": "Ismael", "llega": "2026-10-20T15:50:00-03:00"}
    pedido = {"hoy": "2026-10-20", "persona": "Marcos", "mensaje": None, "pregunta": None,
              "hechos": [{"jugada": "anotar_prevision", "aviso_al_referente": aviso,
                          "correccion_al_referente": aviso,
                          "aviso_de_la_prevision_corregida": aviso,
                          "aviso_de_la_prevision_anterior": aviso},
                         {"jugada": "confirmar", "resultado": "entregada",
                          "queda_esperando_la_aprobacion_de": "Ismael",
                          "aviso_a_quien_aprueba": aviso},
                         {"jugada": "aprobar", "aviso_de_que_se_destrabo": aviso},
                         {"no_vuelve_a_pedir_el_estado": {
                             "motivo": "ya_se_escalo",
                             "escalado_a": [{"a": "Ismael", "llega": "ya_le_llego"}]}},
                         {"aviso": "pedido_de_estado",
                          "si_no_hay_respuesta": {"se_avisa_a": ["Ismael"]}},
                         {"aviso": "recordatorio_de_la_decision",
                          "si_sigue_sin_decidir": {"se_avisa_a": ["Ismael"],
                                                   "fecha": "2026-10-21"}},
                         {"aviso": "tarea_aprobada", "aprobada_por": "Ismael"},
                         {"aviso": "pedido_de_cambios", "pidio_cambios": "Ismael",
                          "comentario": "falta el diagrama"}],
              "ultimos_turnos": [{"sentido": "entrada", "texto": "llego el 27",
                                  "hechos": [{"aviso_al_referente": aviso}]}]}

    recibido, _ = _lo_que_recibe_la_redaccion(pedido)

    assert "Ismael" not in a_la_vista(recibido), a_la_vista(recibido)
    assert solo_si_pregunta(recibido).count("Ismael") == 13
    # Cuándo se entera, también sólo si pregunta (D8: "Quien la revisa será informado hoy a las
    # 11:28"; el modelo del usuario no lo dice).
    assert recibido["hechos"][0]["aviso_a_quien_aprueba_su_trabajo"] == {
        "solo_si_pregunta": {"a": "Ismael", "llega": "2026-10-20T15:50:00-03:00"}}
    # Un código de si le llegó o no queda a la vista: no es una hora.
    assert recibido["hechos"][3]["no_vuelve_a_consultar_como_viene"][
        "avisados_de_que_no_contestaba"] == [
        {"llega": "ya_le_llego", "solo_si_pregunta": {"a": "Ismael"}}]
    assert recibido["hechos"][4]["si_no_hay_respuesta"] == {
        "solo_si_pregunta": {"se_avisa_a": ["Ismael"]}}
    assert recibido["hechos"][5]["si_sigue_sin_decidir"] == {
        "fecha": "2026-10-21", "solo_si_pregunta": {"se_avisa_a": ["Ismael"]}}
    assert recibido["hechos"][7]["solo_si_pregunta"] == {"pidio_cambios": "Ismael"}
    assert recibido["hechos"][7]["comentario"] == "falta el diagrama"
    assert pedido["hechos"][1]["queda_esperando_la_aprobacion_de"] == "Ismael"   # sin tocar


def test_lo_anunciado_que_ya_no_va_a_pasar_nombra_a_quien_aprueba_solo_si_pregunta():
    """D7 (la 11, paso 4, 5 de 5 con la IA real): al retirar un aviso, Leda escribía "Ismael no
    será informado del atraso que habías previsto". Lo anunciado que ya no va a pasar nombra el
    dato con que se contó (`anuncio`): si ese dato nombra a quien aprueba el trabajo de la
    persona, el nombre va dentro de `solo_si_pregunta`, igual que en el dato mismo. Vale para
    cada dato de la lista, también en los últimos turnos."""
    retirado = {"anuncio": "aviso_al_referente",
                "tarea": "Revisar comunicaciones industriales de la comprimidora",
                "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar",
                "motivo": "hay_una_prevision_mas_nueva"}
    pedido = {"hoy": "2026-10-23", "persona": "Marcos", "mensaje": "olvidate lo del 4",
              "hechos": [], "pregunta": None,
              "ya_no_va_a_pasar": [retirado,
                                   {**retirado, "anuncio": "aviso_a_quien_aprueba"},
                                   {**retirado, "anuncio": "aviso_al_responsable",
                                    "a": "Mariano"}],
              "ultimos_turnos": [{"sentido": "salida", "texto": "Anotado.",
                                  "hechos": [], "ya_no_va_a_pasar": [retirado]}]}

    recibido, _ = _lo_que_recibe_la_redaccion(pedido)

    assert "Ismael" not in a_la_vista(recibido), a_la_vista(recibido)
    assert solo_si_pregunta(recibido).count("Ismael") == 3
    primero = recibido["ya_no_va_a_pasar"][0]
    assert primero["solo_si_pregunta"] == {"a": "Ismael Soschinski"}
    assert primero["anuncio"] == "aviso_a_quien_aprueba_su_trabajo"
    assert primero["tarea"] == retirado["tarea"]
    # Desde la decisión 77 (2026-10-12), a quién iba cualquier aviso, también.
    assert "Mariano" not in a_la_vista(recibido)
    assert recibido["ya_no_va_a_pasar"][2]["solo_si_pregunta"] == {"a": "Mariano"}


def test_a_quien_aprueba_se_le_nombra_a_la_persona_responsable_y_a_terceros():
    """La regla es sobre quien aprueba el trabajo de la persona a la que Leda le escribe: a quien
    aprueba se le nombra a la persona responsable ("Marcos te entregó…", y que Marcos se va a
    enterar de la decisión); a quien está arriba, quién tiene trabada la decisión; y a quien
    pide algo que decide otro, quién lo decide. Desde la decisión 77 (2026-10-12), a quién va un
    aviso, a cualquiera, sólo si lo pregunta (`test_avisos_sin_nombre_ni_hora.py`): que Marcos
    se va a enterar de la decisión ya no se dice con su nombre."""
    pedido = {"hoy": "2026-10-20", "persona": "Ismael", "mensaje": None, "pregunta": None,
              "hechos": [{"jugada": "aprobar",
                          "aviso_al_responsable": {"a": "Marcos", "llega": "ya_le_llego"}},
                         {"aviso": "aprobacion_trabada", "quien_aprueba": "Marcos",
                          "responsable": "Ariel"},
                         {"jugada": "aprobar", "resultado": "no_se_puede",
                          "motivo": "no_es_quien_aprueba", "quien_aprueba": "Marcos"},
                         {"jugada": "pedir_reasignacion", "resultado": "no_se_puede",
                          "motivo": "otro_sector", "quien_decide": "Marcos"}],
              "ultimos_turnos": []}

    recibido, _ = _lo_que_recibe_la_redaccion(pedido)

    assert solo_si_pregunta(recibido) == '[{"a": "Marcos"}]'
    assert a_la_vista(recibido).count("Marcos") == 3


def test_lo_que_espera_una_decision_se_dice_revision():
    """Decisión 18: lo que espera es una revisión ("Te entregaron 2 tareas para revisar", "pasa a
    revisión"); "aprobar" queda para la decisión misma. Los nombres de la cocina que dicen la
    espera como aprobación son conceptos de la cocina y la redacción recibe el suyo."""
    for de, para in (("queda_esperando_la_aprobacion_de", "queda_esperando_la_revision_de"),
                     ("entrega_para_aprobar", "entrega_para_revisar"),
                     ("aprobacion_trabada", "revision_que_espera_hace_dias"),
                     ("aprobacion_destrabada", "la_revision_que_esperaba_ya_se_decidio")):
        assert hechos.es_un_concepto_de_la_cocina(de), de
        assert hechos.para_redactar(de) == para
    for decision in ("aprobar", "tarea_aprobada", "cerrada_con_la_aprobacion", "ya_la_aprobo"):
        assert "revis" not in hechos.para_redactar(decision), decision
    for nombre in ("queda_esperando_la_aprobacion_de", "entregada", "ya_no_esta_entregada",
                   "entrega_para_aprobar", "recordatorio_de_la_decision", "aprobacion_trabada",
                   "aprobacion_destrabada", "para_decidir"):
        assert "revis" in hechos.significado(nombre), nombre
        assert "esperando la aprobación" not in hechos.significado(nombre), nombre
        assert "espera su aprobación" not in hechos.significado(nombre), nombre


# El modelo que aprobó el usuario (2026-10-08, C-3d, D7) para lo que falta de una entrega: la
# tarea; lo que se sumó ("tu descripción y las dos fotos"); una sola vez qué falta para entregarla,
# hablando de la tarea; y el ejemplo como una propuesta que la persona acepta. No se le dicta a la
# IA (regla del mozo): sale de los hechos y de sus significados.
LO_QUE_FALTA_DE_UNA_ENTREGA = ("le_falta_evidencia", "le_falta", "le_falta_del_criterio",
                               "ejemplo", "lo_que_escribio", "el_ejemplo_que_acepto",
                               "le_falta_algo", "no_vale_la_confirmacion", "entrega", "cubre",
                               "dice", "sumo", "lo_que_falta_de_la_entrega")


# Que todavía no se entrega, dicho de cualquier forma (D7 y D7b).
DICE_QUE_NO_SE_ENTREGA = re.compile(r"revisi|no se (puede )?entreg|no pasa|sigue como estaba"
                                    r"|para (poder )?entregarla|entregarla falta")


def test_que_todavia_no_se_entrega_lo_dice_un_solo_hecho():
    """D7: la IA escribía "Todavía no se puede entregar… La tarea no pasó a revisión.": tres
    significados lo decían (lo que falta, lo que falta del criterio y el resultado) y la entrega
    incompleta traía además qué pasa al confirmarla. D7b: después, el nombre del resultado
    (`para_entregarla_falta`) y su significado ("hasta entonces no se entrega y la tarea sigue
    como estaba") lo decían dos veces, y la IA escribía "Para entregarla falta… por ahora sigue
    como estaba". Lo dice sólo el nombre del resultado, una vez en total."""
    nombres = LO_QUE_FALTA_DE_UNA_ENTREGA + ("criterio_de_aceptacion",)
    lo_dicen = ([hechos.para_redactar(n) for n in nombres
                 if DICE_QUE_NO_SE_ENTREGA.search(hechos.para_redactar(n).replace("_", " "))]
                + [n for n in nombres if DICE_QUE_NO_SE_ENTREGA.search(hechos.significado(n))])
    assert lo_dicen == ["para_entregarla_falta"]


def test_lo_que_falta_de_una_entrega_se_lee_como_su_descripcion():
    """D7 y decisión 10: "describir", no "contar" ("Sumé lo que contaste", "contarlo con tus
    palabras"). Lo que escribió en una entrega es su descripción, y el ejemplo, una descripción que
    acepta o reemplaza por la suya."""
    for nombre in LO_QUE_FALTA_DE_UNA_ENTREGA:
        significado = hechos.significado(nombre)
        assert not re.search(r"(?<![a-z])cont[aáoó]|sus palabras", significado), nombre
    assert hechos.para_redactar("lo_que_escribio") == "su_descripcion"
    assert "descripción" in hechos.significado("lo_que_escribio")


# "Contar" en cualquier forma, menos "contestar" y "por su cuenta" (D7b: la IA seguía escribiendo
# "contaste", "contarlo" y "Marcos contó…" en las entregas).
CONTAR = re.compile(r"\b(?:cont(?:ar|ás|as|ó|o|aste|é|amos|ando|ado|ada)\w*"
                    r"|(?<!por tu )(?<!por su )cuent(?:a|as|an|e|en|o)\b)", re.IGNORECASE)


def test_nada_de_lo_que_lee_la_ia_sobre_la_entrega_dice_contar():
    """D7b: 6 de 10 mensajes de la entrega decían "contaste" o "contarlo", y los avisos a quien
    revisa, "Marcos contó…", aunque los significados de la entrega ya decían "describir". La
    redacción usaba "contás" como el verbo de Leda, y la ficha de `entregar`, "lo que escribe
    puede contar". Las palabras generales dicen "decir" y "describir"."""
    assert [m.group(0) for m in CONTAR.finditer(INSTRUCCIONES_REDACCION)] == []
    assert not CONTAR.search(hechos.ENCABEZADO_DEL_BLOQUE)
    assert not CONTAR.search(FICHAS["entregar"].es)
    for nombre in LO_QUE_FALTA_DE_UNA_ENTREGA + ("tarea", "hechos", "retiradas",
                                                  "criterio_de_aceptacion", "lo_que_entrego"):
        assert not CONTAR.search(hechos.significado(nombre)), nombre


def test_lo_que_la_persona_entrega_lo_describe():
    """Decisión 10: "describir", no "contar", en lo que la IA lee sobre la entrega."""
    for texto in (hechos.significado("el_texto_cubre"), DATOS["el_texto_cubre"][1]):
        assert "describe" in texto and "cont" not in texto, texto


# --- "Consultar", no "preguntar" (decisión 78 del usuario, 2026-10-12) -----------------------
#
# En la prueba por Telegram Leda escribía "Le voy a preguntar a Ariel…", "Mañana a las 10 te voy
# a preguntar si ya se la pasaste" y "Te voy a preguntar cómo te fue": "preguntar" suena a
# interrogatorio. Como con "previsión", la IA toma la palabra de lo que lee: los nombres de los
# datos y sus significados. Cuando Leda le escribe a alguien para saber algo (después, a otra
# persona, o lo que ya le escribió antes), lo que lee la IA dice "consultar".
#
# Lo que sigue siendo una pregunta es la de este mensaje, el dato `pregunta` que nombra la
# instrucción de redacción (abierta, para después, cerrada, sus opciones), y lo que pregunta la
# persona (`solo_si_pregunta`).
LA_PREGUNTA_DE_ESTE_MENSAJE = frozenset({
    "pregunta", "pregunta_abierta", "pregunta_cerrada", "pregunta_hecha_una_vez",
    "pregunta_para_despues", "pregunta_sigue_abierta", "preguntas_ya_cerradas",
    "otras_preguntas_para_despues", "contesta_la_pregunta", "la_pregunta_espera_respuesta",
    "la_misma_pregunta_sale_en_otro_aviso", "sin_pregunta_abierta", "vuelve_la_pregunta",
    "solo_si_pregunta", "dejar_sin_efecto_la_pregunta", "dejar_la_pregunta_para_mas_tarde"})

# Los datos que son, enteros, Leda escribiéndole a alguien para saber algo: su significado no
# dice "pregunta" de ninguna forma.
CONSULTAS_DE_LEDA = (
    "le_pregunta_a", "le_pregunta_como_le_fue", "le_pregunta_para_cuando",
    "le_pregunta_tambien_a", "le_vuelve_a_preguntar", "se_le_pregunta_a", "se_lo_pregunto_el",
    "preguntado_el", "preguntas_sin_respuesta", "pregunta_a_quien_destraba",
    "pregunta_a_quien_esta_trabado", "aviso_a_quien_se_le_preguntaba",
    "vuelve_a_pedir_el_estado", "no_vuelve_a_pedir_el_estado", "pide_el_estado_el",
    "pedidos_de_estado_sin_respuesta", "pedidos_de_estado_que_no_le_llegaron",
    "pedidos_anteriores_que_no_le_llegaron", "nadie_pidio_el_estado", "pedido_de_estado",
    "pedido_desde", "numero", "sin_respuesta_desde", "veces_sin_algo_cierto", "repregunta",
    "repregunta_de_estado", "escalamiento_de_una_pregunta", "repeticion_del_dia",
    "recordatorio_del_pase", "recordatorio_del_pedido_del_detalle",
    "como_le_fue_con_quien_destraba", "el_dia_que_dijo_quien_destraba",
    "quien_mas_puede_destrabar", "pedido_del_detalle", "pase_para_decidir", "pase_para_tomar",
    "ya_lo_conto_quien_destraba", "ya_lo_conto_quien_esta_trabado", "sin_respuesta",
    "no_contesto", "ya_no_espera_su_respuesta", "ya_no_hace_falta_que_destrabe",
    "ya_no_hace_falta_que_destraben", "aviso_a_quien_destrababa", "cambio_quien_la_tiene",
    "como_termino_el_pedido_del_detalle")

# Leda preguntando, en cualquier forma: Leda o un pronombre antes del verbo, volver o ir a
# preguntar, "preguntarle" o "preguntárselo", hacer o hacerle la pregunta, y la pregunta de algo.
LEDA_PREGUNTA = re.compile(
    r"\b(?:Leda|le|les|se le|se lo|se la)\s+(?:no\s+)?(?:(?:vuelve|va|volvía|iba)\s+a\s+)?"
    r"pregunt"
    r"|\b(?:vuelve|volver|va|iba)\s+a\s+pregunt"
    r"|\bpregunt[aá]r(?:le|les|selo|sela)\b"
    r"|\b(?:hac\w*|hizo)\s+(?:una|la)\s+pregunta\b"
    r"|\bpregunta de (?:si|cómo|qué|para)\b")


def test_ningun_nombre_para_redactar_dice_preguntar_salvo_la_pregunta_de_este_mensaje():
    """Decisión 78: el nombre que la IA lee de un dato en que Leda le escribe a alguien dice
    "consultar"; "pregunta" queda sólo para la de este mensaje."""
    dicen = {hechos.para_redactar(n) for n in NOMBRES
             if "pregunt" in hechos.para_redactar(n)}
    assert dicen <= LA_PREGUNTA_DE_ESTE_MENSAJE, sorted(dicen - LA_PREGUNTA_DE_ESTE_MENSAJE)


def test_lo_que_recibe_la_redaccion_dice_consultar():
    """Lo mismo en lo que recibe de verdad la IA real: los hechos, los últimos turnos y la lista
    de significados."""
    recibido, sistema = _lo_que_recibe_la_redaccion(_con_todos_los_nombres())

    nombres = {n for n in hechos._nombres(recibido) if "pregunt" in n}
    assert nombres <= LA_PREGUNTA_DE_ESTE_MENSAJE, sorted(nombres - LA_PREGUNTA_DE_ESTE_MENSAJE)
    lista = sistema.split(hechos.ENCABEZADO_DEL_BLOQUE, 1)[1].split("\n\n", 1)[0]
    assert [m.group(0) for m in LEDA_PREGUNTA.finditer(lista)] == []


def test_ningun_significado_dice_que_leda_pregunta():
    """Decisión 78: Leda consulta. Ningún significado la pone preguntando, y los de los datos en
    que le escribe a alguien para saber algo no dicen "pregunta" de ninguna forma."""
    dicen = {n: LEDA_PREGUNTA.search(hechos.significado(n) or "").group(0)
             for n in NOMBRES if LEDA_PREGUNTA.search(hechos.significado(n) or "")}
    assert dicen == {}
    assert set(CONSULTAS_DE_LEDA) <= set(NOMBRES)
    assert [n for n in CONSULTAS_DE_LEDA if "pregunt" in hechos.significado(n).lower()] == []


def test_lo_que_hizo_leda_con_otra_persona_se_lee_como_consulta():
    """Los avisos de la prueba por Telegram: a quién le escribe Leda por el pase, a quién para
    saber cuándo destraba, cuándo le vuelve a escribir y cuándo le escribe para saber cómo le
    fue."""
    pedido = {"hoy": "2026-10-20", "persona": "Marcos", "mensaje": None, "pregunta": None,
              "hechos": [{"jugada": "pedir_reasignacion",
                          "le_pregunta_a": {"a": "Ariel", "llega": "ya_le_llego"}},
                         {"jugada": "anotar_quien_destraba",
                          "se_le_pregunta_a": {"a": "Ariel", "llega": "ya_le_llego"}},
                         {"jugada": "decir_cuando_destraba",
                          "le_vuelve_a_preguntar": {"llega": "2026-10-21T10:00:00-03:00"}},
                         {"jugada": "pedirselo_y_contar",
                          "le_pregunta_como_le_fue": {"llega": "2026-10-21T10:00:00-03:00"}}],
              "ultimos_turnos": []}

    recibido, _ = _lo_que_recibe_la_redaccion(pedido)

    assert [list(h)[1] for h in recibido["hechos"]] == [
        "le_consulta_a", "se_le_consulta_a", "le_vuelve_a_consultar", "le_consulta_como_le_fue"]
    assert pedido["hechos"][0]["le_pregunta_a"] == {"a": "Ariel", "llega": "ya_le_llego"}
