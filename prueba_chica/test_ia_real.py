"""La IA real del motor: la llamada estructurada y la redacción (E2-3b).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Un turno"); ADR 0018, decisiones 1 y 8.
Nunca se llama a un proveedor de verdad: el HTTP es un transporte falso que guarda cada
pedido y contesta lo preparado, como lo haría un proveedor compatible con OpenAI.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass

import httpx
import pytest

from prueba_chica.conftest import AHORA
from prueba_chica.fichas import FICHAS, JUGADAS
from prueba_chica.ia import Jugada
from prueba_chica.ia_real import (FUERA_DE_LA_LISTA, NOMBRE_HERRAMIENTA, ClienteCompatible,
                                  IAReal, PlazoAgotado, RespuestaInvalida, desde_base,
                                  esquema_de_jugadas)
from prueba_chica.instrucciones import (INSTRUCCIONES_JUGADAS, INSTRUCCIONES_REDACCION,
                                        Tono)
from prueba_chica.tiempo import RelojFijo
from prueba_chica.turno import SOLO_SI_PREGUNTA, TEXTO_SI_LA_IA_FALLA, procesar_turno

from leda.db import admin, espacio
from leda.incidentes import ETAPA_TURNO_CONVERSACION

SITUACION = {"hoy": "2026-10-20", "mensaje": "llego el 27, el proveedor se demoró",
             "estado": None, "ultimo_aviso": {"tipo": "aviso_previo", "tarea": "T1"},
             "tareas": [{"alias": "T1", "titulo": "Programar PLC", "estado": "en_curso",
                         "fecha_objetivo": "2026-10-23T20:00:00+00:00"}],
             "ultimos_turnos": [], "jugadas_posibles": sorted(JUGADAS)}


@dataclass
class ProveedorFalso:
    """Un proveedor compatible con OpenAI, de mentira: contesta en orden lo preparado (un
    dict de respuesta, una excepción de httpx o un código de error) y guarda los pedidos."""

    respuestas: list
    pedidos: list = None
    demora: float = 0.0

    def __post_init__(self) -> None:
        self.pedidos = []

    def __call__(self, pedido: httpx.Request) -> httpx.Response:
        self.pedidos.append({"url": str(pedido.url), "cuerpo": json.loads(pedido.content),
                             "autorizacion": pedido.headers.get("authorization")})
        if self.demora:
            time.sleep(self.demora)
        respuesta = self.respuestas.pop(0)
        if isinstance(respuesta, Exception):
            raise respuesta
        if isinstance(respuesta, int):
            return httpx.Response(respuesta, json={"error": {"message": "x"}})
        return httpx.Response(200, json=respuesta)


def _llamada(argumentos) -> dict:
    texto = argumentos if isinstance(argumentos, str) else json.dumps(argumentos)
    return {"choices": [{"message": {"content": None, "tool_calls": [{
        "id": "c1", "type": "function",
        "function": {"name": NOMBRE_HERRAMIENTA, "arguments": texto}}]}}]}


def _texto(texto: str | None) -> dict:
    return {"choices": [{"message": {"content": texto}}]}


def _ia(proveedor: ProveedorFalso, *, tono: Tono | None = None, plazo: float = 5.0) -> IAReal:
    cliente = ClienteCompatible.crear(
        "openai/gpt-6-sol", "clave-de-prueba", "https://proveedor.invalid/v1",
        {"plazo_s": plazo}, transporte=httpx.MockTransport(proveedor))
    return IAReal(cliente, tono, nombre="openrouter/openai/gpt-6-sol")


# --- La llamada estructurada ----------------------------------------------------------------

def test_la_eleccion_ofrece_la_herramienta_con_la_lista_cerrada_y_la_lee():
    proveedor = ProveedorFalso([_llamada({"jugadas": [
        {"nombre": "anotar_prevision", "tarea": "T1", "fecha": "2026-10-27",
         "motivo": "el proveedor se demoró", "causa": "", "quien": None}]})])

    jugadas = _ia(proveedor).elegir_jugadas(SITUACION)

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
    assert json.loads(usuario["content"]) == SITUACION


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
    proveedor = ProveedorFalso([_llamada({"jugadas": [
        {"nombre": FUERA_DE_LA_LISTA, "que_pide": "un recordatorio personal",
         "tarea": "T1"},
        {"nombre": "inventada", "tarea": "T1"}]})])

    jugadas = _ia(proveedor).elegir_jugadas(SITUACION)

    # Las dos quedan fuera de la lista: el turno no las ejecuta y avisa al administrador.
    assert jugadas == [Jugada(FUERA_DE_LA_LISTA, {"que_pide": "un recordatorio personal"}),
                       Jugada("inventada", {})]
    assert not {j.nombre for j in jugadas} & set(JUGADAS)


def test_una_lista_vacia_es_ninguna_jugada():
    assert _ia(ProveedorFalso([_llamada({"jugadas": []})])).elegir_jugadas(SITUACION) == []


@pytest.mark.parametrize("respuesta", [
    _texto("Anoté la previsión."),                       # contestó en vez de elegir
    _texto(None),                                        # ni texto ni herramienta
    {"choices": [{"message": {"content": "Listo.", "tool_calls": []}}]},
    {"choices": [{"message": {"content": None, "tool_calls": [{   # otra herramienta
        "id": "c1", "type": "function",
        "function": {"name": "otra", "arguments": "{\"jugadas\": []}"}}]}}]},
    {"choices": [{"message": None}]},
    {"choices": [{}]},
    _llamada("{no es json"),
    _llamada({"otra_cosa": []}),
    _llamada({"jugadas": [{"tarea": "T1"}]}),             # una jugada sin nombre
    _llamada({"jugadas": "anotar_inicio"}),
    {"choices": []},
])
def test_una_respuesta_que_no_es_la_herramienta_es_no_responder(respuesta):
    """Nunca una lista vacía: sin la herramienta, la IA no eligió nada, ni siquiera "ninguna
    jugada" (`RespuestaInvalida`, que el turno trata como no responder)."""
    with pytest.raises(RespuestaInvalida):
        _ia(ProveedorFalso([respuesta])).elegir_jugadas(SITUACION)


@pytest.mark.parametrize("falla", [httpx.ReadTimeout("tarde"), httpx.ConnectError("sin red"),
                                   500, 429])
def test_una_falla_del_proveedor_se_levanta_sin_reintentar_adentro(falla):
    """El reintento es uno solo y lo hace el turno (decisión 8): el cliente no reintenta."""
    proveedor = ProveedorFalso([falla, _llamada({"jugadas": []})])

    with pytest.raises(Exception):
        _ia(proveedor).elegir_jugadas(SITUACION)
    assert len(proveedor.pedidos) == 1


def test_el_plazo_acota_el_tiempo_total_de_la_llamada():
    proveedor = ProveedorFalso([_llamada({"jugadas": []})], demora=1.0)
    inicio = time.perf_counter()

    with pytest.raises(PlazoAgotado):
        _ia(proveedor, plazo=0.2).elegir_jugadas(SITUACION)
    assert time.perf_counter() - inicio < 0.9


# --- La redacción ---------------------------------------------------------------------------

def test_la_redaccion_recibe_sus_instrucciones_el_tono_y_el_pedido():
    proveedor = ProveedorFalso([_texto("  Listo, quedó anotado.  ")])
    tono = Tono(nombre_visible="Leda", registro="vos", formalidad="profesional_cordial",
                longitud="breve", emojis=True)
    pedido = {"hoy": "2026-10-20", "persona": "Marcos", "mensaje": "arranqué",
              "hechos": [{"jugada": "anotar_inicio", "resultado": "anotado"}],
              "ultimos_turnos": []}

    texto = _ia(proveedor, tono=tono).redactar(pedido)

    assert texto == "Listo, quedó anotado."
    cuerpo = proveedor.pedidos[0]["cuerpo"]
    assert "tools" not in cuerpo and "tool_choice" not in cuerpo
    sistema, usuario = cuerpo["messages"]
    assert sistema["content"].startswith(INSTRUCCIONES_REDACCION)
    for linea in ("- Trato: de vos.", "- Formalidad: profesional cordial.",
                  "- Longitud: breve.", "- Emojis: permitidos."):
        assert linea in sistema["content"]
    assert json.loads(usuario["content"]) == pedido


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


def test_la_redaccion_lee_el_estado_de_lo_que_pasa_despues():
    """Primer contacto real (2026-10-05): un aviso guardado se contó como hecho. La regla es
    de lectura de los hechos, para todo efecto que pasa después, sin frases de ejemplo."""
    assert "estado" in INSTRUCCIONES_REDACCION
    assert "guardado_sin_enviar" not in INSTRUCCIONES_REDACCION   # una regla, no un caso
    assert "todavía no pasó" in INSTRUCCIONES_REDACCION


def test_una_redaccion_vacia_se_devuelve_vacia_y_el_turno_la_toma_como_falla():
    assert _ia(ProveedorFalso([_texto(None)])).redactar({"hechos": []}) == ""


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
        _llamada({"jugadas": [{"nombre": "anotar_prevision", "tarea": "T1",
                               "fecha": "2026-10-13", "motivo": "el proveedor se demoró"}]}),
        _texto("Anoté que llegás el 13."),
    ])

    resultado = procesar_turno(conn, quien, entrante, _ia(proveedor), RelojFijo(AHORA))
    conn.commit()

    assert resultado.error is None and resultado.texto == "Anoté que llegás el 13."
    assert resultado.hechos[0]["resultado"] == "anotado"
    redaccion = json.loads(proveedor.pedidos[1]["cuerpo"]["messages"][1]["content"])
    assert redaccion["persona"] == "Marcos" and redaccion["hoy"] == "2026-10-05"
    assert redaccion["hechos"] == resultado.hechos
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
    proveedor = ProveedorFalso([_texto("Anoté que llegás el 13."), _texto("Listo.")])

    resultado = procesar_turno(conn, quien, entrante, _ia(proveedor), RelojFijo(AHORA))
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
        _texto("Anoté que llegás el 13."),
        _llamada({"jugadas": [{"nombre": "anotar_prevision", "tarea": "T1",
                               "fecha": "2026-10-13", "motivo": "el proveedor se demoró"}]}),
        _texto("Anoté que llegás el 13."),
    ])

    resultado = procesar_turno(conn, quien, entrante, _ia(proveedor), RelojFijo(AHORA))
    conn.commit()

    assert len(proveedor.pedidos) == 3
    assert resultado.error is None and resultado.hechos[0]["resultado"] == "anotado"
