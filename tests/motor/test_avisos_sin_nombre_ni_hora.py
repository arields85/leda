"""Un aviso a otra persona se cuenta sin su nombre ni su hora (decisión 77 del usuario,
2026-10-12; constitución §8, "Leda dice que algo quedó asentado, no a quién se lo contó"; decisión
35; `odd/tasks/correcciones-prueba-telegram.md`, T3).

En la prueba por Telegram, ocho mensajes dijeron a quién y a qué hora llegaba un aviso ("Recibirá
mi pregunta hoy a las 12:15", "Marcos será informado hoy de lo que dijiste", "Mañana a las 10:00 te
voy a preguntar cómo te fue"): robótico, la hora no aporta y nombrar a quien se entera suena
acusatorio. La causa era de la cocina: cada hecho de un aviso le pasaba a la IA que redacta el
destinatario (`a`) y la hora exacta (`llega`).

La regla vive en el borde de la redacción (`hechos.para_redactar`), para todos los avisos a la
vez: los hechos de la cocina no cambian (la base, el registro de turnos, las pruebas y la
auditoría los leen).

- Un aviso a otra persona: la IA ve que hay un aviso (el dato que lo nombra) y si ya le llegó o no
  (un código); a quién va y cuándo le llega, dentro de `solo_si_pregunta`.
- Lo que Leda le va a escribir a la misma persona (`hechos.AVISOS_A_LA_PERSONA`): cuándo, sólo el
  día, que la redacción escribe con las palabras de todos los días (`dias`: hoy, mañana, pasado
  mañana o "vie 16/10"); la hora, dentro de `solo_si_pregunta`.
- Ninguna hora del reloj de un hecho llega a la vista; las de lo que alguien escribió, sí.
- Si la persona pregunta a quién se le avisó y cuándo, la redacción lo tiene en
  `solo_si_pregunta`, también desde los últimos turnos (paso 7 del guion de la Fase C).

La lista de los avisos se recorre en el código del motor, no a mano: un aviso nuevo que la regla no
cubre hace fallar `test_cada_aviso_del_motor_tiene_su_lugar_en_la_regla`.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from leda.motor import hechos

from tests.motor.ayudantes import (ProveedorFalso, a_la_vista, ia_real_falsa, respuesta_de_texto,
                                   solo_si_pregunta)

HORA = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}")
HOY = "2026-10-13"
MAS_TARDE = "2026-10-13T12:15:00-03:00"
MANANA = "2026-10-14T10:00:00-03:00"
VIERNES = "2026-10-16T10:00:00-03:00"


def _lo_que_recibe_la_redaccion(pedido: dict) -> dict:
    """Los datos que la IA real recibe para redactar (con `dias`, como en `ia_real.redactar`)."""
    proveedor = ProveedorFalso([respuesta_de_texto("Hola.")])
    ia_real_falsa(proveedor).redactar(pedido)
    _, usuario = proveedor.pedidos[0]["cuerpo"]["messages"]
    return json.loads(usuario["content"])


def _pedido(*hechos_: dict, ultimos_turnos: list | None = None) -> dict:
    return {"hoy": HOY, "persona": "Marcos", "mensaje": "listo", "hechos": list(hechos_),
            "pregunta": None, "ultimos_turnos": ultimos_turnos or []}


# --- Un aviso a otra persona: quedó asentado; a quién y cuándo, sólo si pregunta -------------

# Los de la prueba por Telegram y uno de cada forma: con hora, con un código, en una lista, con
# varias personas, un aviso que ya no va a pasar y uno al administrador.
A_OTRAS_PERSONAS = [
    {"jugada": "anotar_quien_destraba", "se_le_pregunta_a": {"a": "Ariel", "llega": MAS_TARDE}},
    {"jugada": "pasar_la_tarea", "le_pregunta_a": {"a": "Ariel", "llega": MAS_TARDE}},
    {"jugada": "decir_cuando_destraba",
     "aviso_a_quien_esta_trabado": {"a": "Marcos", "llega": MAS_TARDE}},
    {"jugada": "contestar_el_pase", "aviso_a_quien_pidio": {"a": "Ariel", "llega": MAS_TARDE}},
    {"jugada": "aprobar", "aviso_al_responsable": {"a": "Marcos", "llega": MAS_TARDE}},
    {"jugada": "contar_lo_que_arreglaron",
     "aviso_a_quien_destraba": {"a": "Ariel", "llega": MAS_TARDE}},
    {"jugada": "decir_que_no_le_toca",
     "aviso_a_quien_destrababa": {"a": "Ariel", "llega": "ya_le_llego"}},
    {"jugada": "contestar_el_pedido_del_detalle",
     "aviso_a_quienes_lo_pidieron": {"a": ["Ariel", "Marcos"], "llega": MAS_TARDE}},
    {"resultado": "anotado", "avisos_a_quienes_esperan": [
        {"aviso_a_quien_espera": {"a": "Lucas", "tarea": "Cablear", "llega": MANANA}}]},
    {"aviso": "pregunta_a_quien_esta_trabado", "se_le_pregunta_a": {"a": "Juan"}},
    {"aprobada_por": "Ismael", "se_cierra_sola": {"se_avisa_a": ["Marcos", "Ismael"]}},
]


def test_un_aviso_a_otra_persona_llega_a_la_redaccion_sin_su_nombre_ni_su_hora():
    recibido = _lo_que_recibe_la_redaccion(_pedido(*A_OTRAS_PERSONAS))

    visible = a_la_vista(recibido["hechos"])
    for nombre in ("Ariel", "Marcos", "Lucas", "Juan"):
        assert nombre not in visible, visible
    assert not HORA.search(visible), visible
    aparte = solo_si_pregunta(recibido["hechos"])
    for nombre in ("Ariel", "Marcos", "Lucas", "Juan", "Ismael"):
        assert nombre in aparte, aparte
    assert MAS_TARDE in aparte and MANANA in aparte


def test_lo_demas_del_aviso_queda_a_la_vista():
    """Que hay un aviso lo dice el dato; si ya le llegó o no, su código; de qué tarea, su título."""
    recibido = _lo_que_recibe_la_redaccion(_pedido(*A_OTRAS_PERSONAS))["hechos"]

    assert recibido[0]["se_le_consulta_a"] == {
        "solo_si_pregunta": {"a": "Ariel", "llega": MAS_TARDE}}
    assert recibido[6]["aviso_a_quien_se_ocupaba_de_lo_que_faltaba"] == {
        "llega": "ya_le_llego", "solo_si_pregunta": {"a": "Ariel"}}
    assert recibido[8]["avisos_a_quienes_esperan"] == [
        {"aviso_a_quien_espera": {"tarea": "Cablear",
                                  "solo_si_pregunta": {"a": "Lucas", "llega": MANANA}}}]
    assert recibido[9]["se_le_consulta_a"] == {"solo_si_pregunta": {"a": "Juan"}}


def test_un_aviso_que_ya_no_va_a_pasar_tampoco_nombra_a_quien_iba():
    pedido = {**_pedido({"jugada": "corregir", "resultado": "corregido"}),
              "ya_no_va_a_pasar": [{"anuncio": "aviso_a_quien_esta_trabado", "tarea": "Cablear",
                                    "a": "Ariel", "llega": "no_le_va_a_llegar",
                                    "motivo": "ya_no_esta_entregada"}]}

    recibido = _lo_que_recibe_la_redaccion(pedido)

    assert recibido["ya_no_va_a_pasar"] == [
        {"anuncio": "aviso_a_quien_le_falta_algo_para_seguir", "tarea": "Cablear",
         "llega": "no_le_va_a_llegar", "motivo": "ya_no_esta_entregada",
         "solo_si_pregunta": {"a": "Ariel"}}]


def test_el_aviso_al_administrador_no_dice_la_hora():
    """"El administrador será avisado hoy a las 11:12 para que lo conecte conmigo": el aviso al
    administrador no lleva el nombre de una persona, pero tampoco su hora."""
    hecho = {"no_se_le_puede_escribir_a": {"a": "Juan", "motivo": "destinatario_sin_telegram"},
             "se_le_aviso_al_administrador": {"para_que_conecte": "Juan", "llega": MAS_TARDE}}

    recibido = _lo_que_recibe_la_redaccion(_pedido(hecho))["hechos"][0]

    assert recibido["se_le_aviso_al_administrador"] == {
        "para_que_conecte": "Juan", "solo_si_pregunta": {"llega": MAS_TARDE}}
    # A quién Leda no le puede escribir no es un aviso: es lo que la persona tiene que saber.
    assert recibido["no_se_le_puede_escribir_a"]["a"] == "Juan"


def test_lo_que_dijo_la_persona_no_cambia():
    """El dato `a` de una jugada es lo que dijo la persona (a quién pasarle la tarea): no es un
    aviso. Y lo que alguien escribió, con una hora, queda tal cual."""
    turno = {"sentido": "entrada", "texto": "pasasela a Ariel, a las 15:00 ya esta",
             "at": "2026-10-13T11:00:00-03:00",
             "jugadas": [{"nombre": "pedir_reasignacion", "datos": {"a": "Ariel"}}],
             "hechos": [{"jugada": "pedir_reasignacion", "dice": "2026-10-13T15:00"}]}

    recibido = _lo_que_recibe_la_redaccion(_pedido(ultimos_turnos=[turno]))["ultimos_turnos"][0]

    assert recibido["jugadas"][0]["datos"] == {"a": "Ariel"}
    assert recibido["texto"] == turno["texto"]
    assert recibido["at"] == turno["at"]          # cuándo pasó el turno no es un hecho
    assert recibido["hechos"][0]["dice"] == "2026-10-13T15:00"


# --- Lo que Leda le va a escribir a la misma persona: cuándo, en palabras de todos los días ---

A_LA_PERSONA = [
    {"jugada": "pedirselo_y_contar", "le_pregunta_como_le_fue": {"llega": MANANA}},
    {"jugada": "decir_cuando_destraba", "le_vuelve_a_preguntar": {"llega": VIERNES}},
    {"jugada": "informar_avance", "vuelve_a_pedir_el_estado": {"llega": MAS_TARDE}},
    {"jugada": "informar_avance", "antes_le_recuerda_que_vence": {"llega": MANANA}},
    {"jugada": "anotar_inicio", "resultado": "anotado",
     "lo_que_sigue": {"proximo_aviso": {"aviso": "aviso_previo", "llega": MANANA}}},
    {"resultado": "anotado", "lo_esperan": [
        {"le_pregunta_para_cuando": {"responsable": "Lucas", "tarea": "Cablear",
                                     "causa": "el cable", "llega": MAS_TARDE}}]},
]


def test_cuando_leda_le_vuelve_a_escribir_a_la_persona_va_sin_la_hora():
    recibido = _lo_que_recibe_la_redaccion(_pedido(*A_LA_PERSONA))
    hechos_ = recibido["hechos"]

    assert not HORA.search(a_la_vista(hechos_)), a_la_vista(hechos_)
    assert hechos_[0]["le_consulta_como_le_fue"] == {
        "llega": "2026-10-14", "solo_si_pregunta": {"llega": MANANA}}
    assert hechos_[1]["le_vuelve_a_consultar"]["llega"] == "2026-10-16"
    assert hechos_[2]["vuelve_a_consultar_como_viene"]["llega"] == "2026-10-13"
    assert hechos_[4]["lo_que_sigue"]["proximo_aviso"]["llega"] == "2026-10-14"
    # Quien espera es de quien es la tarea, no a quién va el aviso: queda a la vista.
    assert hechos_[5]["lo_esperan"][0]["le_consulta_para_cuando"]["responsable"] == "Lucas"
    assert hechos_[5]["lo_esperan"][0]["le_consulta_para_cuando"]["llega"] == "2026-10-13"


def test_el_dia_lo_escribe_con_las_palabras_de_todos_los_dias():
    """Cada día que queda a la vista tiene en `dias` su palabra: hoy, mañana o su forma corta."""
    dias = _lo_que_recibe_la_redaccion(_pedido(*A_LA_PERSONA))["dias"]

    assert "2026-10-13: mar 13/10, hoy" in dias
    assert "2026-10-14: mié 14/10, mañana" in dias
    assert "2026-10-16: vie 16/10" in dias


def test_ninguna_hora_de_un_hecho_llega_a_la_vista():
    """La regla es para toda hora del reloj de un hecho, no sólo la de un aviso: queda el día, y
    la hora aparte."""
    hecho = {"jugada": "consultar", "se_lo_pregunto_el": MAS_TARDE,
             "historia": [{"el": MANANA, "dijo": "mañana"}]}

    recibido = _lo_que_recibe_la_redaccion(_pedido(hecho))["hechos"][0]

    assert not HORA.search(a_la_vista(recibido)), a_la_vista(recibido)
    assert recibido["se_lo_consulto_el"] == "2026-10-13"
    assert recibido["solo_si_pregunta"] == {"se_lo_consulto_el": MAS_TARDE}
    assert recibido["historia"] == [{"el": "2026-10-14", "dijo": "mañana",
                                     "solo_si_pregunta": {"el": MANANA}}]


# --- Si la persona pregunta a quién se le avisó: el nombre y cuándo (paso 7 del guion) -------

def test_si_pregunta_a_quien_le_aviso_lo_tiene_desde_los_ultimos_turnos():
    """"A quién le avisaste?": un turno sin hechos nuevos se contesta desde los últimos turnos,
    con lo de `solo_si_pregunta` (instrucciones de redacción). El nombre y cuándo están ahí."""
    antes = {"sentido": "entrada", "texto": "lo destraba Ariel", "at": "2026-10-13T11:45:00-03:00",
             "hechos": [A_OTRAS_PERSONAS[0]]}

    recibido = _lo_que_recibe_la_redaccion(_pedido(ultimos_turnos=[antes]))

    turno = recibido["ultimos_turnos"][0]
    assert "Ariel" not in a_la_vista(turno["hechos"])
    assert turno["hechos"][0]["se_le_consulta_a"]["solo_si_pregunta"] == {
        "a": "Ariel", "llega": MAS_TARDE}


def test_los_hechos_de_la_cocina_no_cambian():
    pedido = _pedido(*A_OTRAS_PERSONAS, *A_LA_PERSONA)
    copia = json.loads(json.dumps(pedido))

    hechos.para_redactar(pedido)

    assert pedido == copia


# --- Cada aviso del motor tiene su lugar en la regla -------------------------------------------

MOTOR = Path(hechos.__file__).parent

# Lo que el código del motor arma con `a` o con `llega` y no es el hecho de un aviso: a quién Leda
# no le puede escribir y quién ya está trabado son lo que la persona tiene que saber; los demás
# no son hechos (la lista de significados, los datos de una jugada, una fila de la base, los
# cambios de estado del turno).
NO_SON_AVISOS = {"no_se_le_puede_escribir_a", "ya_esta_trabado", "SIGNIFICADOS", "DATOS",
                 "bloqueo_viejo.py:al_salir", "cambios_de_estado.py:del_turno"}
# Los avisos que el código arma sin la clave que los nombra a la vista: dónde y cuál es.
SIN_SU_CLAVE_A_LA_VISTA = {
    # `{**dicho, LLEGA: …}`: el mismo aviso que nombró el hecho, con su estado final.
    "efectos.py:_aviso": "el aviso que nombra el hecho",
    # Lo anunciado que ya no va a pasar (`ya_no_va_a_pasar`), con su `a` si iba a otra persona.
    "efectos.py:_anunciado": "ya_no_va_a_pasar",
    "efectos.py:_lo_anunciado_antes": "ya_no_va_a_pasar",
    "fichas.py:_escalado_a": "escalado_a",
    "fichas.py:_rearmar_aviso_de_la_anterior": "aviso_de_la_prevision_anterior",
    "pase.py:_como_termino": "aviso_a_quien_pidio, aviso_a_quien_decidio, …",
    "persecucion.py:avisar_para_que_lo_conecte": "se_le_aviso_al_administrador",
    "persecucion.py:_decirle_que_sigue_haciendo_falta": "aviso_de_que_sigue_haciendo_falta",
}


def _constantes() -> dict[str, str]:
    """Los nombres de las constantes de texto de los módulos del motor, con su valor."""
    valores: dict[str, str] = {}
    for archivo in MOTOR.glob("*.py"):
        for nodo in ast.parse(archivo.read_text(encoding="utf-8")).body:
            if (isinstance(nodo, ast.Assign) and isinstance(nodo.value, ast.Constant)
                    and isinstance(nodo.value.value, str)):
                for destino in nodo.targets:
                    if isinstance(destino, ast.Name):
                        valores[destino.id] = nodo.value.value
    return valores


def _avisos_del_motor() -> dict[str, set[str]]:
    """Cada diccionario del código del motor que lleva `a` o `llega`, por la clave que lo nombra
    (o, si no la tiene a la vista, `archivo:función`), con las claves que lleva."""
    constantes = _constantes()

    def nombre(n: ast.AST | None) -> str | None:
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            return n.value
        if isinstance(n, ast.Name):
            return constantes.get(n.id)
        if isinstance(n, ast.Attribute):
            return constantes.get(n.attr)
        return None

    encontrados: dict[str, set[str]] = {}
    for archivo in sorted(MOTOR.glob("*.py")):
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        padre = {h: n for n in ast.walk(arbol) for h in ast.iter_child_nodes(n)}
        for nodo in ast.walk(arbol):
            if not isinstance(nodo, ast.Dict):
                continue
            claves = {nombre(k) for k in nodo.keys if k is not None}
            if not claves & {"a", hechos.LLEGA}:
                continue
            donde, arriba = nodo, padre.get(nodo)
            # Un `**(…)` o un `… if … else …` dentro de otro diccionario es parte de ése.
            while isinstance(arriba, (ast.IfExp, ast.Dict)) and not (
                    isinstance(arriba, ast.Dict) and donde in arriba.values
                    and arriba.keys[arriba.values.index(donde)] is not None):
                donde, arriba = arriba, padre.get(arriba)
            clave = None
            if isinstance(arriba, ast.Dict):
                clave = nombre(arriba.keys[arriba.values.index(donde)])
            elif isinstance(arriba, (ast.Assign, ast.AnnAssign)):
                destino = arriba.targets[0] if isinstance(arriba, ast.Assign) else arriba.target
                if isinstance(destino, ast.Subscript):
                    clave = nombre(destino.slice)
                elif isinstance(destino, ast.Name) and destino.id.isupper():
                    clave = destino.id
            if clave is None:
                funcion = next((f.name for f in _funciones(padre, nodo)), "")
                clave = f"{archivo.name}:{funcion}"
            encontrados.setdefault(clave, set()).update(c for c in claves if c)
    return encontrados


def _funciones(padre: dict, nodo: ast.AST):
    while nodo in padre:
        nodo = padre[nodo]
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield nodo


def test_cada_aviso_del_motor_tiene_su_lugar_en_la_regla():
    """Un aviso nuevo, con `a` o con `llega`, tiene que estar en `hechos.AVISOS` (y, si es lo que
    Leda le va a escribir a la misma persona, en `hechos.AVISOS_A_LA_PERSONA`); si no es un
    aviso, en `NO_SON_AVISOS`; si el código no lo arma con su clave a la vista, en
    `SIN_SU_CLAVE_A_LA_VISTA`, diciendo cuál es."""
    encontrados = _avisos_del_motor()

    sin_lugar = {c for c in encontrados
                 if c not in hechos.AVISOS and c not in NO_SON_AVISOS
                 and c not in SIN_SU_CLAVE_A_LA_VISTA}
    assert not sin_lugar, sorted(sin_lugar)
    sobran = (set(SIN_SU_CLAVE_A_LA_VISTA) | NO_SON_AVISOS) - set(encontrados)
    assert not sobran, sorted(sobran)


def test_lo_que_leda_le_escribe_a_la_misma_persona_nunca_lleva_a_quien():
    encontrados = _avisos_del_motor()

    assert hechos.AVISOS_A_LA_PERSONA <= hechos.AVISOS
    for clave in hechos.AVISOS_A_LA_PERSONA:
        assert "a" not in encontrados.get(clave, set()), clave
    # Cada uno dice, en su significado, que es para la persona a la que Leda le escribe.
    assert all(hechos.significado(c) for c in hechos.AVISOS)
