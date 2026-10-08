"""La IA real del motor (`leda.motor.ia_real`): la llamada estructurada y la redacción (diseño
probado en la Etapa 2, E2-3b).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Un turno"); ADR 0018, decisiones 1 y 8.
Nunca se llama a un proveedor de verdad: el HTTP es un transporte falso que guarda cada
pedido y contesta lo preparado, como lo haría un proveedor compatible con OpenAI.

Portadas de `prueba_chica/test_ia_real.py`.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import time

import httpx
import pytest

from leda.db import admin, espacio
from leda.incidentes import ETAPA_TURNO_CONVERSACION
from leda.motor import hechos
from leda.motor.fichas import FICHAS, JUGADAS
from leda.motor.ia import Jugada
from leda.motor.ia_real import (DIAS_PROXIMOS, FUERA_DE_LA_LISTA, NOMBRE_HERRAMIENTA, PLAZO_S,
                                TOPE_JUGADAS, TOPE_REDACCION, ClienteCompatible, IAReal,
                                ParametrosInvalidos, PlazoAgotado, RespuestaInvalida, desde_base,
                                esquema_de_jugadas, validar_parametros)
from leda.motor.instrucciones import INSTRUCCIONES_JUGADAS, INSTRUCCIONES_REDACCION, Tono
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import SOLO_SI_PREGUNTA, TEXTO_SI_LA_IA_FALLA, procesar_turno

from tests.motor.ayudantes import (AHORA, SITUACION, ProveedorFalso, ia_real_falsa,
                                   llamada_de_jugadas, respuesta_de_texto)


SITUACION = {"hoy": "2026-10-20", "mensaje": "llego el 27, el proveedor se demoró",
             "estado": None, "ultimo_aviso": {"tipo": "aviso_previo", "tarea": "T1"},
             "tareas": [{"alias": "T1", "titulo": "Programar PLC", "estado": "en_curso",
                         "fecha_objetivo": "2026-10-23T20:00:00+00:00"}],
             "ultimos_turnos": [], "jugadas_posibles": sorted(JUGADAS)}


# --- La llamada estructurada ----------------------------------------------------------------

def test_la_eleccion_ofrece_la_herramienta_con_la_lista_cerrada_y_la_lee():
    proveedor = ProveedorFalso([llamada_de_jugadas({"jugadas": [
        {"nombre": "anotar_prevision", "tarea": "T1", "fecha": "2026-10-27",
         "motivo": "el proveedor se demoró", "causa": "", "quien": None}]})])

    jugadas = ia_real_falsa(proveedor).elegir_jugadas(SITUACION)

    # Los datos vacíos no viajan: la ficha los lee como "no lo dijo".
    assert jugadas == [Jugada("anotar_prevision", {
        "tarea": "T1", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"})]
    [pedido] = proveedor.pedidos
    assert pedido["url"] == "https://proveedor.invalid/v1/chat/completions"
    assert pedido["autorizacion"] == "Bearer clave-de-prueba"
    cuerpo = pedido["cuerpo"]
    assert cuerpo["model"] == "openai/gpt-6-sol"
    # Sin forzar la herramienta: Claude Sonnet 5.5 rechaza `tool_choice` forzado (`tool` o
    # `any`, error 400 por OpenRouter, 2026-10-05). Una sola herramienta ofrecida, con
    # "auto" y las instrucciones que piden llamarla siempre. Con "auto" la IA puede contestar
    # con texto: eso es no responder, nunca "ninguna jugada" (las pruebas de abajo: la lectura y
    # el turno con su reintento y su camino de falla).
    assert cuerpo["tool_choice"] == "auto"
    [herramienta] = cuerpo["tools"]
    assert herramienta["function"]["name"] == NOMBRE_HERRAMIENTA
    variantes = _variantes(herramienta)
    assert list(variantes) == sorted(JUGADAS) + [FUERA_DE_LA_LISTA]
    # Quién destraba lo dice la persona; la IA no juzga si la causa depende de otro (9c).
    destraba = variantes["anotar_quien_destraba"]["properties"]
    assert "depende_de_otro" not in destraba
    assert destraba["no_sabe"]["type"] == "boolean"
    assert destraba["nadie_mas"]["type"] == "boolean"
    # La IA recibe sus instrucciones y la situación tal cual, como datos.
    sistema, usuario = cuerpo["messages"]
    assert sistema["role"] == "system"
    assert sistema["content"].startswith(INSTRUCCIONES_JUGADAS)
    assert json.loads(usuario["content"]) == {
        **SITUACION, "dias": hechos.dias(SITUACION, proximos=DIAS_PROXIMOS)}


def _variantes(herramienta) -> dict:
    """Cada jugada del esquema, por su nombre."""
    items = herramienta["function"]["parameters"]["properties"]["jugadas"]["items"]
    return {v["properties"]["nombre"]["enum"][0]: v for v in items["anyOf"]}


def test_cada_jugada_ofrece_solo_sus_datos_y_dice_que_la_distingue():
    """Revisión del contrato (2026-10-05, ronda 1): un esquema plano le ofrecía todos los datos
    a todas las jugadas, y la IA llenaba una causa con palabras que no eran una causa. Cada
    jugada es una variante con sólo sus datos y su definición; nada más se acepta."""
    variantes = _variantes(esquema_de_jugadas(sorted(JUGADAS)))
    for nombre, variante in variantes.items():
        ficha = FICHAS.get(nombre)
        datos = set(ficha.necesita + ficha.opcional) if ficha else {"que_pide"}
        assert set(variante["properties"]) == {"nombre"} | datos, nombre
        assert variante["properties"]["nombre"]["enum"] == [nombre]
        assert variante["additionalProperties"] is False
        assert variante["description"].strip(), nombre
        for dato in datos:
            assert variante["properties"][dato]["description"].strip(), (nombre, dato)
    # Cada definición es propia: ninguna jugada se describe como otra.
    descripciones = [v["description"] for v in variantes.values()]
    assert len(set(descripciones)) == len(descripciones)


def test_el_esquema_es_un_objeto_arriba_y_la_union_va_en_cada_jugada():
    """Una sola forma para todos los proveedores: Anthropic exige un objeto en la raíz de los
    parámetros de una herramienta. La raíz es un objeto plano, sin uniones, y la unión por
    jugada va dentro de los elementos de la lista (así la aceptan GPT-6 sol y Claude Sonnet
    5.5 por OpenRouter, 2026-10-05)."""
    parametros = esquema_de_jugadas(sorted(JUGADAS))["function"]["parameters"]
    assert parametros["type"] == "object"
    assert not {"anyOf", "oneOf", "allOf"} & set(parametros)
    assert set(parametros["properties"]) == {"jugadas"}
    lista = parametros["properties"]["jugadas"]
    assert lista["type"] == "array"
    assert all(v["type"] == "object" for v in lista["items"]["anyOf"])


def test_las_instrucciones_piden_llamar_siempre_a_la_herramienta():
    """Sin `tool_choice` forzado, la instrucción es la que pide la herramienta: nunca contestarle
    a la persona con texto, una sola llamada, y también cuando no hay ninguna jugada (la lista
    vacía). La oración entera, no palabras sueltas que podrían estar en otra regla."""
    texto = " ".join(INSTRUCCIONES_JUGADAS.split())
    assert ("No le respondés a la persona: contestás siempre llamando a la herramienta, una "
            "sola vez, también cuando no hay ninguna jugada (con la lista vacía).") in texto


def test_la_tarea_nunca_es_obligatoria_en_el_esquema():
    """La duda (situación general 5): si la jugada es clara y la tarea no, la IA elige la
    jugada sin la tarea y el código pregunta cuál con opciones. Sólo el nombre es obligatorio:
    ningún dato se fuerza, para que nunca se complete uno que la persona no dijo."""
    for variante in _variantes(esquema_de_jugadas(sorted(JUGADAS))).values():
        assert variante["required"] == ["nombre"]


def test_las_instrucciones_de_las_jugadas_dicen_que_hacer_con_la_duda_y_las_preguntas():
    """Ronda 1: "si no queda claro, no ponés ninguna" perdía la pregunta con botones (13), y
    una pregunta sobre lo que Leda hizo se elegía como fuera de la lista (12). Reglas
    generales, sin frases de las conversaciones."""
    texto = INSTRUCCIONES_JUGADAS.lower()
    assert "no ponés ninguna" not in texto
    assert "sin la tarea" in texto
    assert "no lleva jugada" in texto
    for frase in ("le avisaste", "comprimidora", "switch", "turno con el medico"):
        assert frase not in texto, frase


def test_lo_que_no_esta_en_la_lista_llega_como_fuera_de_la_lista():
    proveedor = ProveedorFalso([llamada_de_jugadas({"jugadas": [
        {"nombre": FUERA_DE_LA_LISTA, "que_pide": "un recordatorio personal",
         "tarea": "T1"},
        {"nombre": "inventada", "tarea": "T1"}]})])

    jugadas = ia_real_falsa(proveedor).elegir_jugadas(SITUACION)

    # Las dos quedan fuera de la lista: el turno no las ejecuta y avisa al administrador.
    assert jugadas == [Jugada(FUERA_DE_LA_LISTA, {"que_pide": "un recordatorio personal"}),
                       Jugada("inventada", {})]
    assert not {j.nombre for j in jugadas} & set(JUGADAS)


def test_una_lista_vacia_es_ninguna_jugada():
    proveedor = ProveedorFalso([llamada_de_jugadas({"jugadas": []})])
    assert ia_real_falsa(proveedor).elegir_jugadas(SITUACION) == []


@pytest.mark.parametrize("respuesta", [
    respuesta_de_texto("Anoté la previsión."),           # contestó en vez de elegir
    respuesta_de_texto(None),                            # ni texto ni herramienta
    {"choices": [{"message": {"content": "Listo.", "tool_calls": []}}]},
    {"choices": [{"message": {"content": None, "tool_calls": [{   # otra herramienta
        "id": "c1", "type": "function",
        "function": {"name": "otra", "arguments": "{\"jugadas\": []}"}}]}}]},
    {"choices": [{"message": None}]},
    {"choices": [{}]},
    llamada_de_jugadas("{no es json"),
    llamada_de_jugadas({"otra_cosa": []}),
    llamada_de_jugadas({"jugadas": [{"tarea": "T1"}]}),   # una jugada sin nombre
    llamada_de_jugadas({"jugadas": "anotar_inicio"}),
    {"choices": []},
])
def test_una_respuesta_que_no_es_la_herramienta_es_no_responder(respuesta):
    """Nunca una lista vacía: sin la herramienta, la IA no eligió nada, ni siquiera "ninguna
    jugada" (`RespuestaInvalida`, que el turno trata como no responder)."""
    with pytest.raises(RespuestaInvalida):
        ia_real_falsa(ProveedorFalso([respuesta])).elegir_jugadas(SITUACION)


@pytest.mark.parametrize("falla", [httpx.ReadTimeout("tarde"), httpx.ConnectError("sin red"),
                                   500, 429])
def test_una_falla_del_proveedor_se_levanta_sin_reintentar_adentro(falla):
    """El reintento es uno solo y lo hace el turno (decisión 8): el cliente no reintenta."""
    proveedor = ProveedorFalso([falla, llamada_de_jugadas({"jugadas": []})])

    with pytest.raises(Exception):
        ia_real_falsa(proveedor).elegir_jugadas(SITUACION)
    assert len(proveedor.pedidos) == 1


def test_el_plazo_acota_el_tiempo_total_de_la_llamada():
    proveedor = ProveedorFalso([llamada_de_jugadas({"jugadas": []})], demora=1.0)
    inicio = time.perf_counter()

    with pytest.raises(PlazoAgotado):
        ia_real_falsa(proveedor, plazo=0.2).elegir_jugadas(SITUACION)
    assert time.perf_counter() - inicio < 0.9


# --- La redacción ---------------------------------------------------------------------------

def test_la_redaccion_recibe_sus_instrucciones_el_tono_y_el_pedido():
    proveedor = ProveedorFalso([respuesta_de_texto("  Listo, quedó anotado.  ")])
    tono = Tono(nombre_visible="Leda", registro="vos", formalidad="profesional_cordial",
                longitud="breve", emojis=True)
    pedido = {"hoy": "2026-10-20", "persona": "Marcos", "mensaje": "arranqué",
              "hechos": [{"jugada": "anotar_inicio", "resultado": "anotado"}],
              "ultimos_turnos": []}

    texto = ia_real_falsa(proveedor, tono=tono).redactar(pedido)

    assert texto == "Listo, quedó anotado."
    cuerpo = proveedor.pedidos[0]["cuerpo"]
    assert "tools" not in cuerpo and "tool_choice" not in cuerpo
    sistema, usuario = cuerpo["messages"]
    assert sistema["content"].startswith(INSTRUCCIONES_REDACCION)
    for linea in ("- Trato: de vos.", "- Formalidad: profesional cordial.",
                  "- Longitud: breve.", "- Emojis, fuera de las marcas del formato: permitidos."):
        assert linea in sistema["content"]
    # Con los nombres que dicen el hecho (`hechos.para_redactar`, 2026-10-07).
    assert json.loads(usuario["content"]) == hechos.para_redactar(
        {**pedido, "dias": hechos.dias(pedido)})
    assert json.loads(usuario["content"])["hechos"][0]["jugada"] == "anotar_que_arranco"


def test_un_proveedor_sin_flujo_no_avisa_ningun_avance_y_redacta_igual():
    """Por OpenRouter la respuesta llega entera: sin texto en vivo, quedan los tres puntos del
    borrador hasta que sale el mensaje (pedido del usuario, 2026-10-07)."""
    proveedor = ProveedorFalso([respuesta_de_texto("Listo, quedó anotado.")])
    vistos: list[str] = []

    texto = ia_real_falsa(proveedor).redactar({"hoy": "2026-10-20", "hechos": []},
                                              al_avanzar=vistos.append)

    assert texto == "Listo, quedó anotado." and vistos == []
    assert "stream" not in proveedor.pedidos[0]["cuerpo"]


def test_las_instrucciones_describen_el_trabajo_y_el_marcador():
    """Las instrucciones nombran el marcador de lo que se dice sólo si se pregunta (9g) y
    la opción de lo que no está en la lista; nunca un nombre de modelo ni de proveedor."""
    assert SOLO_SI_PREGUNTA in INSTRUCCIONES_REDACCION
    assert FUERA_DE_LA_LISTA in INSTRUCCIONES_JUGADAS
    for texto in (INSTRUCCIONES_JUGADAS, INSTRUCCIONES_REDACCION):
        assert "gpt" not in texto.lower() and "openrouter" not in texto.lower()
        assert "¿te sirve" not in texto.lower()


def test_las_instrucciones_describen_las_situaciones_generales():
    """E2-4: la IA sabe que hay una pregunta abierta y las jugadas que la completan, dejan o
    corrigen; la redacción hace una sola pregunta, la que trae el pedido, y sabe qué es lo que
    quedó para después, un toque y una pregunta de antes. Nombres de datos, no frases."""
    for jugada in ("elegir", "corregir", "cancelar", "dejar_para_despues", "corrige",
                   "tarea_correcta", "opcion"):
        assert jugada in INSTRUCCIONES_JUGADAS, jugada
    for marcador in ("pregunta", "desde_antes", "pregunta_para_despues", "toco", "opciones",
                     "cerrada_con"):
        assert marcador in INSTRUCCIONES_REDACCION, marcador


def test_las_instrucciones_describen_el_avance_sin_algo_cierto():
    """Decisión del usuario, 2026-10-05: un avance sin un hecho cierto es `informar_avance`,
    con las palabras de la persona; la redacción no lo cuenta como un hecho cierto. Una
    descripción de la jugada, sin frases de las conversaciones."""
    assert "informar_avance" in INSTRUCCIONES_JUGADAS
    assert "palabras" in INSTRUCCIONES_JUGADAS
    assert "espera_algo_cierto" in INSTRUCCIONES_REDACCION
    for texto in (INSTRUCCIONES_JUGADAS, INSTRUCCIONES_REDACCION):
        for frase in ("casi lista", "voy bien", "todo en orden"):
            assert frase not in texto.lower(), frase


def test_las_instrucciones_describen_destrabar_sin_frases():
    """Decisión del usuario, 2026-10-05 (ADR 0018, 9l): que la causa de un bloqueo ya no esté es
    `destrabar`, distinta de un inicio, una fecha o un avance. Sin frases de la conversación 17."""
    texto = INSTRUCCIONES_JUGADAS.lower()
    assert "destrabar" in texto
    for frase in ("switch", "llego el", "fuente"):
        assert frase not in texto, frase


def test_la_redaccion_cuenta_lo_que_pasa_en_el_mundo_y_no_da_por_hecho_lo_que_no_paso():
    """Primer contacto real (2026-10-05): un aviso guardado se contó como hecho. Prueba por
    Telegram real (2026-10-06): con el estado interno del aviso, Leda lo repetía; el usuario
    decidió que habla del mundo, no de la cocina. Una regla del trabajo, sin frases ni casos."""
    texto = INSTRUCCIONES_REDACCION
    assert "lo que pasa en el mundo" in texto and "quién se entera de qué y cuándo" in texto
    assert "todavía no pasó" in texto and "nunca lo das por hecho" in texto
    for palabra in ("guardado", "en cola", "sin enviar", "cuándo sale"):
        assert palabra not in texto, palabra


def test_la_redaccion_describe_el_formato_sin_frases_de_ejemplo():
    """Segunda vuelta del formato (usuario, 2026-10-07, después de verlo en Telegram;
    conversación 20): sin negrita, un renglón por idea, cuatro marcas fijas al principio del
    renglón que van aunque el tono no lleve emojis, el título completo una vez, fechas cortas y
    el cierre aparte. La instrucción describe el trabajo, sin frases de ejemplo."""
    texto = INSTRUCCIONES_REDACCION
    assert "sin Markdown" not in texto and "**" not in texto and '"• "' not in texto
    assert "breve" in texto and "renglón en blanco" in texto and "Sin negrita" in texto
    for marca in ("📋", "🗓️", "✏️", "⚠️"):
        assert marca in texto, marca
    assert "aunque el tono del equipo no lleve emojis" in texto
    assert "una sola vez" in texto and "último renglón" in texto and "forma corta" in texto
    for palabra in ("programar plc", "comunicaciones", "vence el", "anoté", "vie ", "/10"):
        assert palabra not in texto.lower(), palabra


def test_la_redaccion_describe_la_tercera_vuelta_del_formato_sin_frases_de_ejemplo():
    """Tercera vuelta (usuario, 2026-10-07, después de la segunda prueba por Telegram): 🗓️ en vez
    de 📅, que Telegram dibuja con una fecha fija; en un bloque con una tarea, su renglón es el
    primero y todo lo de la tarea va debajo; una marca va sólo al principio de su renglón; y
    quien se entera se dice en voz pasiva, en futuro o en pasado según si ya pasó. La
    instrucción describe el trabajo: ni la frase del usuario ni las que no quiere."""
    texto = INSTRUCCIONES_REDACCION
    assert "📅" not in texto
    assert "el primero del bloque" in texto and "va debajo" in texto
    assert "al principio de su renglón" in texto and "nunca en el medio" in texto
    assert "voz pasiva" in texto and "Nunca lo contás como algo que hacés vos" in texto
    # Decisión 11 (2026-10-08): a quien se entera se lo nombra sólo si un hecho lo nombra a la
    # vista; si no, el sujeto es lo que se informa.
    assert "fuera de solo_si_pregunta; si no, lo que se informa" in texto
    assert "como sujeto del verbo notificar" not in texto
    for frase in ("ismael", "marcos", "será notificad", "fue notificad", "le avis", "avisarle",
                  "le voy a"):
        assert frase not in texto.lower(), frase


def test_una_redaccion_vacia_se_devuelve_vacia_y_el_turno_la_toma_como_falla():
    assert ia_real_falsa(ProveedorFalso([respuesta_de_texto(None)])).redactar({"hechos": []}) == ""


# --- El modelo del espacio ------------------------------------------------------------------

@dataclass
class Claves:
    clave: str = "clave-de-prueba"

    def clave_llm(self, proveedor: str) -> str:
        return self.clave

    def variable_clave_llm(self, proveedor: str) -> str:
        return "LEDA_OPENROUTER_API_KEY"


def _modelo(conn, proveedor: str, modelo: str, workspace_id: str | None = None,
            parametros: dict | None = None) -> None:
    with admin(conn) as cur:
        cur.execute("update model_config set activo = false")
        cur.execute(
            """insert into model_config (ambito, workspace_id, proveedor, modelo, parametros,
                                         activo)
               values (%s, %s, %s, %s, %s, true)""",
            ("espacio" if workspace_id else "global", workspace_id, proveedor, modelo,
             json.dumps(parametros or {})))
    conn.commit()


def test_el_modelo_sale_de_la_configuracion_del_espacio(conn, mundo):
    _modelo(conn, "openrouter", "openai/gpt-6-sol", parametros={"timeout_s": 30})
    with admin(conn) as cur:
        cur.execute("update persona_config set emojis = true where workspace_id = %s",
                    (mundo["id"],))
    conn.commit()

    with espacio(conn, mundo["id"]) as cur:
        ia = desde_base(cur, mundo["id"], Claves())

    assert ia.nombre == "openrouter/openai/gpt-6-sol"
    assert ia.cliente.base_url == "https://openrouter.ai/api/v1"
    assert ia.tono.emojis is True and ia.tono.registro == "vos"


def test_sin_clave_falla_nombrando_la_variable(conn, mundo):
    _modelo(conn, "openrouter", "openai/gpt-6-sol")
    with espacio(conn, mundo["id"]) as cur, pytest.raises(LookupError,
                                                         match="LEDA_OPENROUTER_API_KEY"):
        desde_base(cur, mundo["id"], Claves(clave=""))


def test_un_proveedor_que_no_habla_el_protocolo_compatible_no_se_usa(conn, mundo):
    _modelo(conn, "anthropic", "un-modelo")
    with espacio(conn, mundo["id"]) as cur, pytest.raises(LookupError, match="compatible"):
        desde_base(cur, mundo["id"], Claves())


# --- De punta a punta, con el turno ---------------------------------------------------------

def test_un_turno_con_la_ia_real_anota_y_redacta_desde_los_hechos(conn, mundo, escribe):
    quien, entrante = escribe("Marcos", "llego el 13, el proveedor se demoró")
    proveedor = ProveedorFalso([
        llamada_de_jugadas({"jugadas": [{"nombre": "anotar_prevision", "tarea": "T1",
                                         "fecha": "2026-10-13",
                                         "motivo": "el proveedor se demoró"}]}),
        respuesta_de_texto("Anoté que llegás el 13."),
    ])

    resultado = procesar_turno(conn, quien, entrante, ia_real_falsa(proveedor), RelojFijo(AHORA))
    conn.commit()

    assert resultado.error is None and resultado.texto == "Anoté que llegás el 13."
    assert resultado.hechos[0]["resultado"] == "anotado"
    redaccion = json.loads(proveedor.pedidos[1]["cuerpo"]["messages"][1]["content"])
    assert redaccion["persona"] == "Marcos" and redaccion["hoy"] == "2026-10-05"
    # Los hechos guardados quedan con los nombres de la cocina; la redacción, con los suyos.
    assert redaccion["hechos"] == hechos.para_redactar(resultado.hechos)
    assert resultado.hechos[0]["jugada"] == "anotar_prevision"
    with admin(conn) as cur:
        cur.execute("select fecha_prevista::text f, ia from task_forecast, conversation_turn "
                    "where conversation_turn.sentido = 'entrada'")
        fila = cur.fetchone()
    assert fila == {"f": "2026-10-13", "ia": "openrouter/openai/gpt-6-sol"}


def test_un_texto_en_lugar_de_la_herramienta_es_no_responder_tambien_en_el_turno(conn, mundo,
                                                                                escribe):
    """Con `tool_choice: auto` (revisión, 2026-10-05): si la IA contesta con texto dos veces, el
    turno no lo toma como "ninguna jugada": un reintento y después el camino de falla (decisión
    8): nada se ejecuta ni se redacta, la persona recibe el texto fijo y queda el incidente."""
    quien, entrante = escribe("Marcos", "llego el 13, el proveedor se demoró")
    proveedor = ProveedorFalso([respuesta_de_texto("Anoté que llegás el 13."),
                                respuesta_de_texto("Listo.")])

    resultado = procesar_turno(conn, quien, entrante, ia_real_falsa(proveedor), RelojFijo(AHORA))
    conn.commit()

    assert len(proveedor.pedidos) == 2                  # el pedido y su único reintento
    assert all(p["cuerpo"]["tools"] for p in proveedor.pedidos)     # ninguna redacción
    assert resultado.texto == TEXTO_SI_LA_IA_FALLA and resultado.error
    assert resultado.jugadas == [] and resultado.hechos == []
    with admin(conn) as cur:
        cur.execute("select count(*) n from task_forecast")
        assert cur.fetchone()["n"] == 0
        cur.execute("select etapa from incident")
        assert [f["etapa"] for f in cur.fetchall()] == [ETAPA_TURNO_CONVERSACION]


def test_un_texto_y_despues_la_herramienta_es_el_reintento_que_responde(conn, mundo, escribe):
    quien, entrante = escribe("Marcos", "llego el 13, el proveedor se demoró")
    proveedor = ProveedorFalso([
        respuesta_de_texto("Anoté que llegás el 13."),
        llamada_de_jugadas({"jugadas": [{"nombre": "anotar_prevision", "tarea": "T1",
                                         "fecha": "2026-10-13",
                                         "motivo": "el proveedor se demoró"}]}),
        respuesta_de_texto("Anoté que llegás el 13."),
    ])

    resultado = procesar_turno(conn, quien, entrante, ia_real_falsa(proveedor), RelojFijo(AHORA))
    conn.commit()

    assert len(proveedor.pedidos) == 3
    assert resultado.error is None and resultado.hechos[0]["resultado"] == "anotado"


# --- Una respuesta cortada (tercera vuelta de ajuste, 2026-10-06) ----------------------------
#
# Ronda 2 (Sonnet): mensajes que llegaron cortados a la persona. El proveedor dice que cortó por
# el tope (`finish_reason`); una respuesta cortada es que la IA no respondió (decisión 8): un
# reintento y después el camino de falla, nunca un texto a medias.

def _cortada(respuesta: dict) -> dict:
    respuesta["choices"][0]["finish_reason"] = "length"
    return respuesta


def test_una_redaccion_cortada_por_el_tope_es_no_responder():
    with pytest.raises(RespuestaInvalida):
        cortada = _cortada(respuesta_de_texto("Quedó anotado que llegás el"))
        ia_real_falsa(ProveedorFalso([cortada])).redactar({"hechos": []})


def test_una_eleccion_cortada_por_el_tope_es_no_responder():
    cortada = _cortada(llamada_de_jugadas({"jugadas": []}))
    with pytest.raises(RespuestaInvalida):
        ia_real_falsa(ProveedorFalso([cortada])).elegir_jugadas(SITUACION)


def test_una_respuesta_que_termino_normal_se_lee():
    terminada = respuesta_de_texto("Listo.")
    terminada["choices"][0]["finish_reason"] = "stop"
    assert ia_real_falsa(ProveedorFalso([terminada])).redactar({"hechos": []}) == "Listo."


def test_el_tope_de_la_redaccion_alcanza_para_un_mensaje_entero():
    proveedor = ProveedorFalso([respuesta_de_texto("Listo.")])
    ia_real_falsa(proveedor).redactar({"hechos": []})
    assert proveedor.pedidos[0]["cuerpo"]["max_tokens"] >= 2000


def test_una_redaccion_cortada_se_reintenta_en_el_turno(conn, mundo, escribe):
    quien, entrante = escribe("Marcos", "llego el 13, el proveedor se demoró")
    proveedor = ProveedorFalso([
        llamada_de_jugadas({"jugadas": [{"nombre": "anotar_prevision", "tarea": "T1",
                                         "fecha": "2026-10-13"}]}),
        _cortada(respuesta_de_texto("Quedó anotado que")),
        respuesta_de_texto("Quedó anotado que la tenés el martes 13."),
    ])

    resultado = procesar_turno(conn, quien, entrante, ia_real_falsa(proveedor), RelojFijo(AHORA))
    conn.commit()

    assert len(proveedor.pedidos) == 3
    assert resultado.error is None
    assert resultado.texto == "Quedó anotado que la tenés el martes 13."


# --- Los parámetros por modelo (E3-8, la comparación de IA) ---------------------------------
#
# La regresión de la E3-8 con los dos modelos flash de `nan` falló sobre todo por los límites:
# el corredor creaba el cliente sin parámetros. Cada modelo lleva los suyos (en
# `model_config.parametros` o, para el corredor, como argumento): el tiempo por fase, el plazo
# total, los dos topes de salida y campos propios del pedido (`cuerpo_extra`, por ejemplo para
# que un modelo no razone por dentro). Un valor que no vale se rechaza nombrándolo; nunca se
# reemplaza en silencio por el de omisión.

def _ia_con(proveedor: ProveedorFalso, parametros: dict) -> IAReal:
    cliente = ClienteCompatible.crear(
        "glm5.3-flash", "clave-de-prueba", "https://proveedor.invalid/v1", parametros,
        transporte=httpx.MockTransport(proveedor))
    return IAReal(cliente, None, nombre="nan/glm5.3-flash")


SIN_RAZONAR = {"cuerpo_extra": {"reasoning_effort": "low"}, "timeout_s": 60, "plazo_s": 90,
               "tope_jugadas": 3000, "tope_redaccion": 4000}


def test_los_campos_extra_viajan_en_los_dos_pedidos_y_los_topes_se_aplican():
    proveedor = ProveedorFalso([llamada_de_jugadas({"jugadas": []}),
                                respuesta_de_texto("Listo.")])
    ia = _ia_con(proveedor, SIN_RAZONAR)

    assert ia.elegir_jugadas(SITUACION) == []
    assert ia.redactar({"hechos": []}) == "Listo."

    eleccion, redaccion = (p["cuerpo"] for p in proveedor.pedidos)
    assert eleccion["reasoning_effort"] == "low" and redaccion["reasoning_effort"] == "low"
    assert eleccion["max_tokens"] == 3000 and redaccion["max_tokens"] == 4000
    # Lo demás del pedido es el de siempre: el extra no lo pisa.
    assert eleccion["model"] == "glm5.3-flash" and eleccion["tool_choice"] == "auto"
    assert ia.cliente.http.timeout.read == 60


def test_un_campo_extra_anidado_viaja_tal_cual():
    proveedor = ProveedorFalso([respuesta_de_texto("Listo.")])
    extra = {"chat_template_kwargs": {"enable_thinking": False}}
    _ia_con(proveedor, {"cuerpo_extra": extra}).redactar({"hechos": []})
    assert proveedor.pedidos[0]["cuerpo"]["chat_template_kwargs"] == {"enable_thinking": False}


def test_sin_parametros_quedan_los_de_omision_y_ningun_campo_extra():
    proveedor = ProveedorFalso([llamada_de_jugadas({"jugadas": []}),
                                respuesta_de_texto("Listo.")])
    ia = _ia_con(proveedor, {})
    ia.elegir_jugadas(SITUACION)
    ia.redactar({"hechos": []})

    eleccion, redaccion = (p["cuerpo"] for p in proveedor.pedidos)
    assert set(eleccion) == {"model", "temperature", "max_tokens", "messages", "tools",
                             "tool_choice"}
    assert set(redaccion) == {"model", "temperature", "max_tokens", "messages"}
    assert (eleccion["max_tokens"], redaccion["max_tokens"]) == (TOPE_JUGADAS, TOPE_REDACCION)
    assert validar_parametros({})["plazo_s"] == PLAZO_S


def test_el_plazo_de_los_parametros_acota_la_llamada():
    proveedor = ProveedorFalso([llamada_de_jugadas({"jugadas": []})], demora=1.0)
    inicio = time.perf_counter()
    with pytest.raises(PlazoAgotado):
        _ia_con(proveedor, {"plazo_s": 0.2}).elegir_jugadas(SITUACION)
    assert time.perf_counter() - inicio < 0.9


@pytest.mark.parametrize(("parametros", "nombrado"), [
    ({"plazo_s": 0}, "plazo_s"),
    ({"plazo_s": -5}, "plazo_s"),
    ({"plazo_s": "90"}, "plazo_s"),
    ({"plazo_s": True}, "plazo_s"),
    ({"plazo_s": None}, "plazo_s"),
    ({"plazo_s": 100_000}, "plazo_s"),
    ({"timeout_s": 0}, "timeout_s"),
    ({"timeout_s": 100_000}, "timeout_s"),
    ({"reintentos": -1}, "reintentos"),
    ({"tope_jugadas": 0}, "tope_jugadas"),
    ({"tope_jugadas": 1.5}, "tope_jugadas"),
    ({"tope_jugadas": "1500"}, "tope_jugadas"),
    ({"tope_redaccion": 10_000_000}, "tope_redaccion"),
    ({"tope_redaccion": False}, "tope_redaccion"),
    ({"temperature": 5}, "temperature"),
    ({"cuerpo_extra": "reasoning_effort=low"}, "cuerpo_extra"),
    ({"cuerpo_extra": ["reasoning_effort"]}, "cuerpo_extra"),
    ({"cuerpo_extra": {"model": "otro"}}, "model"),
    ({"cuerpo_extra": {"messages": []}}, "messages"),
    ({"cuerpo_extra": {"tools": []}}, "tools"),
    ({"cuerpo_extra": {"tool_choice": "required"}}, "tool_choice"),
    ({"cuerpo_extra": {"max_tokens": 10}}, "max_tokens"),
    ({"cuerpo_extra": {"max_completion_tokens": 10}}, "max_completion_tokens"),
    ({"cuerpo_extra": {"temperature": 1}}, "temperature"),
    ({"cuerpo_extra": {"stream": True}}, "stream"),
    ({"plazo": 90}, "plazo"),                       # un nombre mal escrito no se ignora
])
def test_un_parametro_que_no_vale_se_rechaza_nombrandolo(parametros, nombrado):
    with pytest.raises(ParametrosInvalidos, match=nombrado):
        validar_parametros(parametros)
    with pytest.raises(ParametrosInvalidos, match=nombrado):
        _ia_con(ProveedorFalso([]), parametros)


def test_los_parametros_validos_se_normalizan():
    validos = validar_parametros({"timeout_s": 60, "plazo_s": 90.0, "tope_jugadas": 3000.0,
                                  "reintentos": 2.0, "cuerpo_extra": {"reasoning_effort": "low"},
                                  "base_url": "https://otro.invalid/v1", "temperature": 0.3})
    assert validos["tope_jugadas"] == 3000 and isinstance(validos["tope_jugadas"], int)
    assert validos["plazo_s"] == 90.0 and validos["timeout_s"] == 60
    assert validos["cuerpo_extra"] == {"reasoning_effort": "low"}


@pytest.mark.parametrize("respuesta", [
    # GLM cuenta lo que razona dentro del tope: puede volver sin nada y cortada.
    {"choices": [{"message": {"content": ""}, "finish_reason": "length"}]},
    {"choices": [{"message": {"content": None, "tool_calls": []}, "finish_reason": "length"}]},
])
def test_una_respuesta_vacia_cortada_por_el_tope_es_no_responder_con_parametros(respuesta):
    with pytest.raises(RespuestaInvalida):
        _ia_con(ProveedorFalso([respuesta]), SIN_RAZONAR).elegir_jugadas(SITUACION)
    with pytest.raises(RespuestaInvalida):
        _ia_con(ProveedorFalso([respuesta]), SIN_RAZONAR).redactar({"hechos": []})


def test_el_modelo_del_espacio_lleva_sus_parametros(conn, mundo):
    _modelo(conn, "nan", "glm5.3-flash", parametros=SIN_RAZONAR)
    with espacio(conn, mundo["id"]) as cur:
        ia = desde_base(cur, mundo["id"], Claves())
    assert ia.cliente.parametros["cuerpo_extra"] == {"reasoning_effort": "low"}
    assert ia.cliente.parametros["plazo_s"] == 90
    assert ia.cliente.http.timeout.read == 60


def test_parametros_invalidos_en_la_base_son_un_modelo_no_configurado(conn, mundo):
    """Quien llama trata `LookupError` como "la IA no está configurada" (incidente y aviso
    neutro); un parámetro que no vale es eso, nombrándolo, nunca el valor de omisión."""
    _modelo(conn, "nan", "glm5.3-flash", parametros={"cuerpo_extra": {"model": "otro"}})
    with espacio(conn, mundo["id"]) as cur, pytest.raises(LookupError, match="model"):
        desde_base(cur, mundo["id"], Claves())
