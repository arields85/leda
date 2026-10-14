"""La ayuda de la IA al cargar una tarea (ADR 0023, punto 4; porción J2 de
`odd/tasks/plataforma-jerarquias.md`): las reglas del código, sin base, con una IA de mentira.

La persona cuenta en un recuadro libre qué quiere hacer y Leda propone sólo lo que el formulario
tiene vacío. Lo que propone la IA cuenta sólo si pasa los controles del código: ningún número ni
nombre que nadie dijo (`entrega.problema_del_ejemplo`), el criterio dice cómo se comprueba, quién
la hace sólo si se la nombró y es del equipo (Leda no elige entre dos), la espera y el objetivo de
las listas, y la fecha sólo si la persona la dijo y es un día hábil (constitución §4).
"""

from __future__ import annotations

import importlib
import json
from datetime import date, timedelta
from typing import Any

import pytest

EJEMPLO = ("hay que colgar el estante del modem en la sala que lo haga lucas necesita 12 "
           "tornillos de 8 mm para el viernes no puede hasta que terminen de cablear el tablero "
           "de la maquina 3")

# Lo que propondría una IA que entendió el ejemplo: el criterio entero, con sus palabras (J2-17), y
# el resultado solo, para el criterio de reserva.
RESULTADO_DEL_EJEMPLO = "El estante del módem está colgado en la sala con los 12 tornillos de 8 mm"
CRITERIO_DEL_EJEMPLO = ("El estante del módem está colgado en la sala con los 12 tornillos de "
                        "8 mm. Se comprueba con una foto del estante colgado.")

HOY = date(2026, 10, 14)          # miércoles
VIERNES = "2026-10-16"
SABADO = "2026-10-17"


def _habiles(desde: date, dias: int = 80) -> list[str]:
    return [(desde + timedelta(days=n)).isoformat() for n in range(dias)
            if (desde + timedelta(days=n)).weekday() < 5]


OPCIONES: dict[str, Any] = {
    "espacio": {"id": "ws-1", "nombre": "CoreWork", "zona_horaria": "America/Argentina/Buenos_Aires"},
    "hoy": HOY.isoformat(),
    "objetivos": [
        {"id": "o-modem", "titulo": "Instalar el módem de la sala", "tipo": "operativo",
         "estado": "activo", "fecha_objetivo": "2026-10-30"},
        {"id": "o-anual", "titulo": "Mantenimiento anual", "tipo": "operativo",
         "estado": "activo", "fecha_objetivo": None},
    ],
    "tareas": [
        {"id": "t-tablero", "titulo": "Cablear el tablero de la máquina 3", "estado": "en_curso",
         "fecha_objetivo": "2026-10-15", "responsable": "Marcos Díaz",
         "objetivo": "Instalar el módem de la sala"},
        {"id": "t-informe", "titulo": "Escribir el informe de octubre", "estado": "asignada",
         "fecha_objetivo": "2026-10-28", "responsable": "Ismael Soschinski",
         "objetivo": "Mantenimiento anual"},
    ],
    "integrantes": [
        {"membership_id": "m-lucas", "nombre": "Lucas Pérez", "area_id": "a-infra",
         "area": "Infraestructura", "autoridad_final": False, "conectado": True,
         "revisa": {"membership_id": "m-ismael", "nombre": "Ismael Soschinski"}},
        {"membership_id": "m-lucas-b", "nombre": "Lucía Benítez", "area_id": "a-auto",
         "area": "Automatización", "autoridad_final": False, "conectado": True,
         "revisa": {"membership_id": "m-ismael", "nombre": "Ismael Soschinski"}},
        {"membership_id": "m-marcos", "nombre": "Marcos Díaz", "area_id": "a-auto",
         "area": "Automatización", "autoridad_final": False, "conectado": True,
         "revisa": {"membership_id": "m-ismael", "nombre": "Ismael Soschinski"}},
        {"membership_id": "m-ismael", "nombre": "Ismael Soschinski", "area_id": "a-dir",
         "area": "Dirección", "autoridad_final": True, "conectado": True, "revisa": None},
    ],
    "politicas": [
        {"area_id": "a-infra", "area": "Infraestructura", "evidencia_requerida": ["foto"],
         "version": 1, "tipos": {"foto": {"clases": ["imagen"], "en_palabras": "una foto"}}},
    ],
    "calendario": {"dias": ["lunes", "martes", "miercoles", "jueves", "viernes"],
                   "hasta": "2027-04-14", "feriados": [], "dias_habiles": _habiles(HOY)},
}

CALENDARIO = OPCIONES["calendario"]

# Los apodos del equipo de mentira: "lucas" es sólo Lucas Pérez (su apodo) y "el tano", Marcos.
APODOS = {"m-lucas": ["lucas"], "m-marcos": ["el tano"]}


def _coinciden(dicho: str) -> list[dict[str, Any]]:
    """Como `fichas.integrantes_que_coinciden`: todas las palabras de lo dicho en el nombre o en
    un apodo."""
    from leda.motor.fichas import palabras

    buscadas = set(palabras(dicho))
    if not buscadas:
        return []
    return [{"membership_id": m["membership_id"], "nombre": m["nombre"]}
            for m in OPCIONES["integrantes"]
            if buscadas <= set(palabras(m["nombre"]))
            or any(buscadas <= set(a.split()) for a in APODOS.get(m["membership_id"], []))]


def _objetivo_de(task_id: str) -> str | None:
    return {"t-tablero": "o-modem", "t-informe": "o-cerrado"}.get(task_id)


def _vacio(**cambios) -> dict[str, Any]:
    escrito = {"objetivo_id": "", "titulo": "", "descripcion": "", "responsable_id": "",
               "fecha": "", "espera_id": "", "criterio": ""}
    escrito.update(cambios)
    return escrito


def _respuesta_del_ejemplo(**cambios) -> dict[str, Any]:
    respuesta = {
        "titulo": "Colgar el estante del módem en la sala",
        "descripcion": ("Colgar el estante del módem en la sala. Hacen falta 12 tornillos de 8 mm. "
                        "No se puede empezar hasta que terminen de cablear el tablero de la "
                        "máquina 3."),
        "criterio": CRITERIO_DEL_EJEMPLO,
        "resultado": RESULTADO_DEL_EJEMPLO,
        "responsable": "lucas",
        "espera": "T1",
        "objetivo": "O2",
        "fecha": VIERNES,
        "como_dijo_la_fecha": "para el viernes",
    }
    respuesta.update(cambios)
    return {k: v for k, v in respuesta.items() if v is not None}


def juzga_que_si(entrada: dict[str, Any]) -> dict[str, Any]:
    """El juicio de mentira que dice que el criterio sirve (para las pruebas que no miran el
    juicio): sin evidencia del área, que dice cómo se comprueba, con todo el criterio como la
    parte que lo dice; con ella (J2-14), que dice un resultado. Nunca la IA real."""
    if "evidencia_que_pide_el_area" in entrada:
        return {"dice_un_resultado": True, "resultado": entrada.get("criterio", "")}
    return {"dice_como_se_comprueba": True, "como_se_comprueba": entrada.get("criterio", "")}


def juez(*que_repiten: str, propone: str | None = None):
    """Un juicio de mentira que juzga por el sentido lo que la prueba ya sabe: los criterios de
    `que_repiten` sólo vuelven a decir el resultado (aunque sea con otras palabras); los demás
    dicen cómo se comprueba. Con `propone`, el criterio que escribe el juicio (J2-17)."""
    def juzga(entrada: dict[str, Any]) -> dict[str, Any]:
        if entrada.get("criterio") in que_repiten:
            rechazo = {"dice_como_se_comprueba": False, "como_se_comprueba": ""}
            return {**rechazo, "criterio": propone} if propone else rechazo
        return juzga_que_si(entrada)
    return juzga


class IADeLaCarga:
    """Una IA de mentira con el contrato de `ia_real.IAReal` que usa la ayuda (`cliente.completar`):
    devuelve lo preparado, en orden, como la llamada a la herramienta; una excepción se levanta,
    como una IA que no responde. Con `juzga`, el juicio del criterio lo contesta esa función con lo
    que recibió (sin gastar lo preparado). Guarda cada pedido."""

    nombre = "de-mentira"

    def __init__(self, *respuestas: Any, juzga=None) -> None:
        self.respuestas = list(respuestas)
        self.pedidos: list[dict[str, Any]] = []
        self.cliente = self
        self.al_llamar = None
        self.juzga = juzga

    def completar(self, cuerpo: dict[str, Any], al_avanzar=None) -> dict[str, Any]:
        self.pedidos.append(cuerpo)
        if self.al_llamar is not None:
            self.al_llamar()
        herramienta = ((cuerpo.get("tools") or [{}])[0].get("function") or {}).get("name")
        if herramienta == "revisar_el_criterio" and self.juzga is not None:
            entrada = json.loads(next(m["content"] for m in cuerpo["messages"]
                                      if m["role"] == "user"))
            self.respuestas.insert(0, self.juzga(entrada))
        r = self.respuestas.pop(0)
        if isinstance(r, BaseException):
            raise r
        if isinstance(r, dict) and "choices" in r:
            return r
        # La herramienta que se le pidió: la de la propuesta o la del juicio del criterio.
        nombre = ((cuerpo.get("tools") or [{}])[0].get("function") or {}).get(
            "name", "proponer_la_carga")
        return {"choices": [{"finish_reason": "tool_calls", "message": {"tool_calls": [
            {"function": {"name": nombre, "arguments": json.dumps(r)}}]}}]}

    def entrada(self, i: int = 0) -> dict[str, Any]:
        """Lo que recibió la IA en el pedido `i` (el primero: el de la propuesta, que puede venir
        seguido del juicio del criterio): el mensaje de la persona, en JSON."""
        mensajes = self.pedidos[i]["messages"]
        return json.loads(next(m["content"] for m in mensajes if m["role"] == "user"))

    def instrucciones(self, i: int = 0) -> str:
        return next(m["content"] for m in self.pedidos[i]["messages"] if m["role"] == "system")


class IAQueCopiaElCriterio(IADeLaCarga):
    """La IA de mentira del juicio del criterio al cargar, para las pruebas que no lo miran: dice
    que el criterio dice cómo se comprueba (`juzga_que_si`). Nunca la real."""

    def __init__(self) -> None:
        super().__init__(juzga=juzga_que_si)


@pytest.fixture
def ayuda():
    return importlib.import_module("leda.ayuda_al_cargar")


def _proponer(ayuda, respuesta: dict[str, Any], *, texto: str = EJEMPLO, escrito=None,
              coinciden=_coinciden, objetivo_de=_objetivo_de, juzga=juzga_que_si,
              opciones=None):
    """Como la ruta de la ayuda: la propuesta, lo que decide el código, el juicio por el sentido
    del criterio que escribió la IA (`juzgar_la_propuesta`, J2-13 y J2-17, ya con la evidencia
    del área de quien la hace) y el criterio que se propone."""
    escrito = escrito if escrito is not None else _vacio()
    opciones = opciones if opciones is not None else OPCIONES
    ia = IADeLaCarga(respuesta, juzga=juzga)
    entrada = ayuda.entrada_de_la_ia(texto, escrito, opciones)
    crudo = ayuda.pedir(ia, entrada)
    resultado = ayuda.revisar(crudo, texto=texto, escrito=escrito, opciones=opciones,
                              coinciden=coinciden, objetivo_de=objetivo_de)
    ayuda.cerrar_el_criterio(resultado, ayuda.juzgar_la_propuesta(ia, resultado))
    return resultado, ia


def _avisos(resultado) -> dict[str, str]:
    return {a["campo"]: a["texto"] for a in resultado.avisos}


# --- El ejemplo del usuario -------------------------------------------------------------------

def test_el_ejemplo_del_usuario_completa_todo_lo_que_dijo(ayuda):
    resultado, ia = _proponer(ayuda, _respuesta_del_ejemplo())
    assert resultado.propuesta == {
        "titulo": "Colgar el estante del módem en la sala",
        "descripcion": ("Colgar el estante del módem en la sala. Hacen falta 12 tornillos de 8 mm. "
                        "No se puede empezar hasta que terminen de cablear el tablero de la "
                        "máquina 3."),
        "criterio": CRITERIO_DEL_EJEMPLO,
        "responsable_id": "m-lucas",
        "espera_id": "t-tablero",
        # El de la tarea que espera, aunque la IA eligiera otro.
        "objetivo_id": "o-modem",
        "fecha": VIERNES,
    }
    assert resultado.avisos == [] and resultado.elegir == []
    assert ia.pedidos[0]["tools"][0]["function"]["name"] == "proponer_la_carga"


def test_la_ia_recibe_lo_del_espacio_con_codigos_y_sin_ids(ayuda):
    """J2-18: el equipo también, como hechos con un código (para proponer quién la hace); antes,
    la IA no recibía sus nombres."""
    _, ia = _proponer(ayuda, _respuesta_del_ejemplo())
    entrada = ia.entrada()
    assert entrada["texto"] == EJEMPLO
    assert set(entrada["pide"]) == {"titulo", "descripcion", "criterio", "responsable", "espera",
                                    "objetivo", "fecha", "evidencia"}
    assert [m["nombre"] for m in entrada["equipo"]] == ["Lucas Pérez", "Lucía Benítez",
                                                        "Marcos Díaz"]
    assert [o["codigo"] for o in entrada["objetivos"]] == ["O1", "O2"]
    assert entrada["tareas_abiertas"][0]["codigo"] == "T1"
    assert entrada["tareas_abiertas"][0]["titulo"] == "Cablear el tablero de la máquina 3"
    assert any(d.startswith(f"{VIERNES}: viernes 16 de octubre") for d in entrada["dias"])
    assert entrada["dias"][0].startswith(f"{HOY.isoformat()}: miércoles 14 de octubre, hoy")
    plano = json.dumps(entrada, ensure_ascii=False)
    # Ningún id: la IA devuelve las palabras o los códigos, y el código los busca.
    for dato in ("m-lucas", "o-modem", "t-tablero", "a-infra", "ws-1"):
        assert dato not in plano
    # Las instrucciones describen el trabajo, sin frases de ejemplo.
    for frase in ("tornillos", "estante", "lucas"):
        assert frase not in ia.instrucciones().lower()


# --- Sólo lo vacío ----------------------------------------------------------------------------

def test_solo_se_pide_y_se_propone_lo_que_esta_vacio(ayuda):
    escrito = _vacio(titulo="Poner el estante", responsable_id="m-marcos", fecha="2026-10-20")
    resultado, ia = _proponer(ayuda, _respuesta_del_ejemplo(), escrito=escrito)
    assert set(ia.entrada()["pide"]) == {"descripcion", "criterio", "espera", "objetivo"}
    assert "titulo" not in resultado.propuesta
    assert "responsable_id" not in resultado.propuesta and "fecha" not in resultado.propuesta
    # Lo ya elegido es parte de la tarea: quién la hace, con su área y la evidencia que pide.
    assert ia.entrada()["ya_escrito"]["titulo"] == "Poner el estante"
    assert ia.entrada()["ya_escrito"]["quien_la_hace"]["area"] == "Automatización"


def test_lo_que_falta_es_lo_vacio_del_formulario(ayuda):
    assert ayuda.lo_que_falta(_vacio(titulo="  ", criterio="x")) == [
        "objetivo_id", "titulo", "descripcion", "responsable_id", "fecha", "espera_id"]
    assert ayuda.lo_que_falta({k: "x" for k in _vacio()}) == []


# --- Título, descripción y criterio -----------------------------------------------------------

@pytest.mark.parametrize("campo, valor", [
    ("titulo", "Colgar el estante con 14 tornillos"),
    ("titulo", "Colgar el estante con Roberto"),
    ("descripcion", "Hay que colgarlo antes del 30 de octubre."),
    ("criterio", "El estante está colgado y Roberto lo revisó."),
])
def test_un_numero_o_un_nombre_que_nadie_dijo_no_se_propone(ayuda, campo, valor):
    # Sin el resultado, el criterio no tiene reserva: el que inventa no se propone y se dice.
    cambios = {campo: valor, **({"resultado": None} if campo == "criterio" else {})}
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(**cambios))
    assert campo not in resultado.propuesta
    assert _avisos(resultado)[campo].startswith("No pude proponer")
    assert "otros" not in _avisos(resultado)
    assert {"campo": campo, "motivo": "dato" if any(c.isdigit() for c in valor) else "nombre"} \
        in resultado.descartados


def test_un_nombre_de_los_datos_de_la_tarea_vale(ayuda):
    """El objetivo, la tarea que espera, quién la hace y su área son de esta tarea: nombrarlos no
    es inventar."""
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(
        criterio=("Lucas Pérez colgó el estante en la sala, después del tablero de la "
                  "máquina 3, y se ve en una foto.")))
    assert resultado.propuesta["criterio"].startswith("Lucas Pérez colgó")


def test_los_topes_del_formulario(ayuda):
    largo = "Colgar el estante " + "muy " * 60
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(
        titulo=largo, criterio="Está colgado. " * 40, resultado=None))
    assert "titulo" not in resultado.propuesta and "criterio" not in resultado.propuesta
    assert {"campo": "titulo", "motivo": "largo"} in resultado.descartados
    assert {"campo": "criterio", "motivo": "largo"} in resultado.descartados


def test_lo_que_la_ia_deja_vacio_se_dice(ayuda):
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(titulo="", resultado=None,
                                                           criterio=None))
    assert _avisos(resultado)["titulo"] == (
        "No pude proponer el título con lo que escribiste; contame qué hay que hacer.")
    assert "criterio" in _avisos(resultado)


# --- Quién la hace ----------------------------------------------------------------------------

def test_quien_la_hace_por_su_apodo_o_su_nombre(ayuda):
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(responsable="el tano"),
                             texto=EJEMPLO.replace("lucas", "el tano"))
    assert resultado.propuesta["responsable_id"] == "m-marcos"


def test_nadie_con_ese_nombre_se_dice(ayuda):
    texto = EJEMPLO.replace("lucas", "pepe")
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(responsable="pepe"), texto=texto)
    assert "responsable_id" not in resultado.propuesta
    assert _avisos(resultado)["responsable"] == (
        "No encontré a «pepe» en el equipo; elegí quién la hace.")


def test_dos_personas_se_muestran_para_elegir_y_leda_no_elige(ayuda):
    """ADR 0020, decisión 3: "Lucas" es Lucas Pérez (también su apodo) y Lucía Benítez."""
    def por_nombre(dicho):
        return _coinciden("lucas pérez") + _coinciden("lucía benítez")
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(), coinciden=por_nombre)
    assert "responsable_id" not in resultado.propuesta
    assert [e["membership_id"] for e in resultado.elegir] == ["m-lucas", "m-lucas-b"]
    assert resultado.elegir[0]["area"] == "Infraestructura"
    assert "elegí quién la hace" in _avisos(resultado)["responsable"]


def test_un_nombre_que_no_esta_en_el_texto_no_se_busca(ayuda):
    llamadas = []

    def coinciden(dicho):
        llamadas.append(dicho)
        return _coinciden(dicho)
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(responsable="Marcos"),
                             coinciden=coinciden)
    assert "responsable_id" not in resultado.propuesta and llamadas == []
    assert {"campo": "responsable", "motivo": "no_lo_dijo"} in resultado.descartados


def test_alguien_que_no_esta_en_las_opciones_no_se_propone(ayuda):
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(), coinciden=lambda d: [
        {"membership_id": "m-de-otro-lado", "nombre": "Lucas"}])
    assert "responsable_id" not in resultado.propuesta
    assert _avisos(resultado)["responsable"] == (
        "No encontré a «lucas» en el equipo; elegí quién la hace.")


# --- La espera y el objetivo ------------------------------------------------------------------

def test_una_espera_que_no_esta_en_la_lista_no_se_propone(ayuda):
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(espera="T9", objetivo="O2"))
    assert "espera_id" not in resultado.propuesta
    assert resultado.propuesta["objetivo_id"] == "o-anual"
    assert {"campo": "espera", "motivo": "no_existe"} in resultado.descartados


def test_el_objetivo_de_la_espera_si_esta_abierto_y_si_no_el_de_la_ia(ayuda):
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(espera="T2", objetivo="O1"))
    # El de la espera (o-cerrado) no está entre los abiertos: vale el código de la IA.
    assert resultado.propuesta["espera_id"] == "t-informe"
    assert resultado.propuesta["objetivo_id"] == "o-modem"
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(espera=None, objetivo="O7"))
    assert "objetivo_id" not in resultado.propuesta


def test_la_espera_elegida_a_mano_da_el_objetivo(ayuda):
    resultado, ia = _proponer(ayuda, _respuesta_del_ejemplo(objetivo="O2"),
                              escrito=_vacio(espera_id="t-tablero"))
    assert "espera" not in ia.entrada()["pide"]
    assert resultado.propuesta["objetivo_id"] == "o-modem"
    assert ia.entrada()["ya_escrito"]["espera"] == "Cablear el tablero de la máquina 3"


# --- La fecha ---------------------------------------------------------------------------------
#
# Constitución §4: nunca una fecha que nadie dijo. La IA devuelve, con la fecha, las palabras con
# que la persona la dijo (`como_dijo_la_fecha`); el código comprueba que están tal cual en el texto
# y calcula él mismo el día con esas palabras: vale sólo si es el mismo que dio la IA y es hábil.

def test_una_fecha_que_no_es_un_dia_habil_no_se_pone(ayuda):
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(fecha=SABADO,
                                                           como_dijo_la_fecha="para el sabado"),
                             texto=EJEMPLO.replace("viernes", "sabado"))
    assert "fecha" not in resultado.propuesta
    assert _avisos(resultado)["fecha"] == (
        'No puse la fecha: dijiste "para el sabado", pero el sábado 17 de octubre no es día '
        'hábil en este espacio; elegila en el calendario.')
    assert {"campo": "fecha", "motivo": "no_es_habil"} in resultado.descartados


def test_una_fecha_fuera_del_calendario_no_se_pone(ayuda):
    texto = EJEMPLO.replace("para el viernes", "para el 3 de mayo")
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(
        fecha="2027-05-03", como_dijo_la_fecha="para el 3 de mayo"), texto=texto)
    assert "fecha" not in resultado.propuesta
    assert _avisos(resultado)["fecha"] == (
        'No puse la fecha: dijiste "para el 3 de mayo", pero el lunes 3 de mayo está fuera del '
        'calendario de este espacio; elegila en el calendario.')


def test_una_fecha_que_la_persona_no_dijo_no_se_pone(ayuda):
    texto = EJEMPLO.replace(" para el viernes", "")
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(fecha="2026-10-15"), texto=texto)
    assert "fecha" not in resultado.propuesta
    assert _avisos(resultado)["fecha"].startswith("No puse la fecha: no encontré")
    assert {"campo": "fecha", "motivo": "no_dicha"} in resultado.descartados


def test_una_fecha_sin_las_palabras_de_la_persona_no_se_pone(ayuda):
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(como_dijo_la_fecha=None))
    assert "fecha" not in resultado.propuesta
    assert {"campo": "fecha", "motivo": "no_dicha"} in resultado.descartados


def test_el_dia_que_calcula_el_codigo_tiene_que_ser_el_de_la_ia(ayuda):
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(fecha="2026-10-23"))  # otro viernes
    assert "fecha" not in resultado.propuesta
    assert {"campo": "fecha", "motivo": "no_coincide"} in resultado.descartados
    assert _avisos(resultado)["fecha"] == (
        'No puse la fecha: no entendí qué día es "para el viernes"; elegila en el calendario.')


def test_el_numero_de_unos_tornillos_no_es_una_fecha(ayuda):
    """La revisión `review-6a44e26466b95395`: "12 tornillos" dejaba pasar el 12."""
    texto = EJEMPLO.replace(" para el viernes", "")
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(fecha="2026-11-12",
                                                           como_dijo_la_fecha="12"), texto=texto)
    assert "fecha" not in resultado.propuesta
    assert {"campo": "fecha", "motivo": "no_entendida"} in resultado.descartados
    assert _avisos(resultado)["fecha"] == (
        'No puse la fecha: no entendí qué día es "12"; elegila en el calendario.')


def test_por_la_manana_es_una_hora_y_no_un_dia(ayuda):
    texto = "revisar las alarmas del scada por la mañana que lo haga lucas"
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(fecha="2026-10-15",
                                                           como_dijo_la_fecha="mañana"),
                             texto=texto)
    assert "fecha" not in resultado.propuesta
    assert {"campo": "fecha", "motivo": "no_entendida"} in resultado.descartados


@pytest.mark.parametrize("texto, dicho, fecha", [
    ("colgar el estante para el viernes", "para el viernes", "2026-10-16"),
    ("colgar el estante para el VIERNES", "Para el viernes", "2026-10-16"),
    ("colgar el estante el viernes", "viernes", "2026-10-16"),
    ("colgar el estante para mañana", "mañana", "2026-10-15"),
    ("colgar el estante para manana", "para mañana", "2026-10-15"),
    ("colgar el estante mañana a la mañana", "mañana a la mañana", "2026-10-15"),
    ("hoy mismo", "hoy", "2026-10-14"),
    ("pasado mañana", "pasado mañana", "2026-10-16"),
    # Hoy es miércoles: "el miércoles" es el que viene, no hoy.
    ("el miercoles", "el miércoles", "2026-10-21"),
    ("el viernes que viene", "el viernes que viene", "2026-10-16"),
    ("el lunes q viene", "el lunes q viene", "2026-10-19"),
    ("el viernes de la semana que viene", "el viernes de la semana que viene", "2026-10-23"),
    # Las palabras de la IA eligen la frase del texto, entera: no se pierde "de la semana que viene".
    ("el viernes de la semana que viene", "el viernes", "2026-10-23"),
    ("el viernes de la proxima semana", "viernes de la próxima semana", "2026-10-23"),
    ("para el 22", "para el 22", "2026-10-22"),
    ("para el 22", "22", "2026-10-22"),
    ("el dia 20", "el dia 20", "2026-10-20"),
    # Un día que ya pasó este mes es el del mes que viene.
    ("para el 10", "el 10", "2026-11-10"),
    ("el 22/10", "22/10", "2026-10-22"),
    ("el 22 / 10", "22/10", "2026-10-22"),
    ("el 5/1", "5/1", "2027-01-05"),
    ("el 22/10/2026", "22/10/2026", "2026-10-22"),
    # Con el guion, sólo con el año: sin él, "10-12" puede ser del 10 al 12.
    ("el 22-10-2026", "22-10-2026", "2026-10-22"),
    ("el 3 de noviembre", "el 3 de noviembre", "2026-11-03"),
    ("el viernes 23", "el viernes 23", "2026-10-23"),
])
def test_el_codigo_calcula_el_dia_de_las_palabras(ayuda, texto, dicho, fecha):
    assert ayuda.fecha_dicha(texto, dicho, HOY, CALENDARIO) == (date.fromisoformat(fecha), None)


@pytest.mark.parametrize("texto, dicho, motivo", [
    ("necesita 12 tornillos", "12", "no_entendida"),
    ("necesita 12 tornillos para el viernes", "12 tornillos", "no_entendida"),
    ("lo hago por la mañana", "mañana", "no_entendida"),
    ("lo hago a la mañana", "a la mañana", "no_entendida"),
    ("esta mañana se cortó", "mañana", "no_entendida"),
    ("la semana que viene", "la semana que viene", "no_entendida"),
    ("pronto", "pronto", "no_entendida"),
    # El 22 es jueves: "viernes 22" no es un día.
    ("el viernes 22", "el viernes 22", "no_entendida"),
    ("mañana o el viernes", "mañana o el viernes", "no_entendida"),
    ("el 31 de febrero", "el 31 de febrero", "no_entendida"),
    ("la maquina 3 10 tornillos", "3 10", "no_entendida"),
    ("colgar el estante para el viernes", "para el jueves", "no_dicha"),
    ("colgar el estante para el viernes", "", "no_dicha"),
    ("colgar el estante para el viernes", None, "no_dicha"),
    # "De mañana" es una hora del día ("lo hago de mañana"), como "por la mañana".
    ("lo hago de mañana", "mañana", "no_entendida"),
    ("lo hago de mañana", "de mañana", "no_entendida"),
    # Un rango no es un día (revisión `review-6eec478c3a4ddc11`): ni con el guion ni con palabras.
    ("del 10-12", "del 10-12", "no_entendida"),
    ("del 10-12", "10-12", "no_entendida"),
    ("del 10-12", "del 10", "no_dicha"),
    ("necesita 10-12 tornillos", "10-12", "no_entendida"),
    ("el 5-1", "5-1", "no_entendida"),
    ("el 22-10", "el 22-10", "no_entendida"),
    ("entre el 10 y el 12", "entre el 10 y el 12", "no_entendida"),
    ("entre el 10 y el 12", "el 12", "no_entendida"),
    ("entre el 10 y el 12", "el 10", "no_entendida"),
    ("del 10 al 12", "al 12", "no_entendida"),
    ("del 10 al 12", "del 10", "no_entendida"),
    ("del 10 a 12", "del 10", "no_entendida"),
    ("el lunes o el martes", "el martes", "no_entendida"),
    ("entre el lunes y el miercoles", "el lunes", "no_entendida"),
])
def test_lo_que_no_es_un_dia_no_se_calcula(ayuda, texto, dicho, motivo):
    assert ayuda.fecha_dicha(texto, dicho, HOY, CALENDARIO) == (None, motivo)


# --- "Antes de un día" ------------------------------------------------------------------------
#
# El usuario (2026-10-13): "si la persona dijo antes del jueves, leda deberia proponer el miercoles,
# porque la persona dijo 'antes del jueves' no 'el jueves'". El código calcula el día que nombran
# las palabras, con las mismas reglas, y propone el día hábil anterior del calendario del espacio.

@pytest.mark.parametrize("texto, dicho, fecha", [
    # Hoy es miércoles 14 y es hábil: antes del jueves 15 es hoy.
    ("antes del jueves", "antes del jueves", "2026-10-14"),
    ("lo tiene que ver antes del viernes porq se corta", "antes del viernes", "2026-10-15"),
    # Antes del lunes es el viernes anterior.
    ("antes del lunes", "antes del lunes", "2026-10-16"),
    ("para antes del 22", "antes del 22", "2026-10-21"),
    ("antes del dia 22", "antes del dia 22", "2026-10-21"),
    ("antes del 22/10", "antes del 22/10", "2026-10-21"),
    ("antes del 22 de octubre", "antes del 22 de octubre", "2026-10-21"),
    ("antes del 20-10-2026", "antes del 20-10-2026", "2026-10-19"),
    ("antes de pasado mañana", "antes de pasado mañana", "2026-10-15"),
    ("antes de mañana", "antes de mañana", "2026-10-14"),
    ("antes del viernes de la semana que viene", "antes del viernes", "2026-10-22"),
    ("ANTES DEL JUEVES", "antes del jueves", "2026-10-14"),
])
def test_antes_de_un_dia_es_el_dia_habil_anterior(ayuda, texto, dicho, fecha):
    assert ayuda.fecha_dicha(texto, dicho, HOY, CALENDARIO) == (date.fromisoformat(fecha), None)


def test_antes_de_un_dia_saltea_lo_que_no_es_habil_en_el_espacio(ayuda):
    """El miércoles 21 es feriado: antes del jueves 22 es el martes 20."""
    calendario = {**CALENDARIO, "dias_habiles": [d for d in CALENDARIO["dias_habiles"]
                                                 if d != "2026-10-21"]}
    assert ayuda.fecha_dicha("antes del jueves 22", "antes del jueves 22", HOY, calendario) == (
        date(2026, 10, 20), None)


@pytest.mark.parametrize("texto, dicho, motivo", [
    # Las palabras de la IA tienen que traer el "antes": "jueves" solo no es lo que dijo.
    ("antes del jueves", "jueves", "no_entendida"),
    ("antes del jueves", "del jueves", "no_entendida"),
    # Una cantidad antes del "antes" no es el día hábil anterior.
    ("dos dias antes del jueves", "antes del jueves", "no_entendida"),
    ("una semana antes del 22", "antes del 22", "no_entendida"),
    # Ningún día hábil desde hoy hasta antes de ese día, o fuera del calendario.
    ("antes de hoy", "antes de hoy", "sin_habil_antes"),
    ("antes del 3 de mayo", "antes del 3 de mayo", "sin_habil_antes"),
])
def test_antes_de_un_dia_que_no_se_puede_proponer(ayuda, texto, dicho, motivo):
    assert ayuda.fecha_dicha(texto, dicho, HOY, CALENDARIO) == (None, motivo)


def test_antes_de_manana_sin_hoy_habil_no_tiene_dia(ayuda):
    """Pasada la hora de cierre, hoy no está entre los días hábiles para cargar."""
    calendario = {**CALENDARIO, "dias_habiles": CALENDARIO["dias_habiles"][1:]}
    assert ayuda.fecha_dicha("antes de mañana", "antes de mañana", HOY, calendario) == (
        None, "sin_habil_antes")


def test_antes_del_jueves_propone_el_miercoles(ayuda):
    texto = EJEMPLO.replace("para el viernes", "antes del jueves")
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(
        fecha="2026-10-14", como_dijo_la_fecha="antes del jueves"), texto=texto)
    assert resultado.propuesta["fecha"] == "2026-10-14"
    assert not any(a["campo"] == "fecha" for a in resultado.avisos)


def test_antes_del_jueves_no_es_el_jueves(ayuda):
    texto = EJEMPLO.replace("para el viernes", "antes del jueves")
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(
        fecha="2026-10-15", como_dijo_la_fecha="antes del jueves"), texto=texto)
    assert "fecha" not in resultado.propuesta
    assert {"campo": "fecha", "motivo": "no_coincide"} in resultado.descartados


def test_sin_dia_habil_antes_se_dice_por_que(ayuda):
    texto = EJEMPLO.replace("para el viernes", "antes de hoy")
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(
        fecha="2026-10-13", como_dijo_la_fecha="antes de hoy"), texto=texto)
    assert "fecha" not in resultado.propuesta
    assert {"campo": "fecha", "motivo": "sin_habil_antes"} in resultado.descartados
    assert _avisos(resultado)["fecha"] == (
        'No puse la fecha: dijiste "antes de hoy", pero no encontré el día hábil anterior en el '
        'calendario de este espacio; elegila en el calendario.')


def test_la_ia_sabe_que_dias_son_habiles_y_que_es_antes_de_un_dia(ayuda):
    """Para que la IA pueda dar el día hábil anterior, la lista de días dice cuáles no son
    hábiles, y la herramienta lo describe en general (sin frases de ejemplo)."""
    _, ia = _proponer(ayuda, _respuesta_del_ejemplo())
    dias = ia.entrada()["dias"]
    assert next(d for d in dias if d.startswith(SABADO)).endswith("no es día hábil")
    assert not next(d for d in dias if d.startswith(VIERNES)).endswith("no es día hábil")
    datos = ia.pedidos[0]["tools"][0]["function"]["parameters"]["properties"]
    assert "día hábil anterior" in datos["fecha"]["description"]
    assert "antes" in datos["como_dijo_la_fecha"]["description"]


def test_una_fecha_mal_escrita_no_se_pone(ayuda):
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(fecha="16/10"))
    assert "fecha" not in resultado.propuesta and "fecha" in _avisos(resultado)


def test_la_herramienta_pide_las_palabras_de_la_fecha_solo_con_la_fecha(ayuda):
    def datos(pide):
        return set(ayuda.herramienta(pide)["function"]["parameters"]["properties"])
    assert {"fecha", "como_dijo_la_fecha"} <= datos(["titulo", "fecha"])
    assert "como_dijo_la_fecha" not in datos(["titulo"])


# --- El criterio, desde la evidencia y juzgado por su sentido (J2-13) ---------------------------
#
# J2-9 juzgaba con palabras: la parte de cómo se comprueba tenía que traer una palabra que el
# resultado no dijera. En la prueba del usuario en el celular (2026-10-13) Leda propuso "El UPS de
# la sala de servidores está cambiado; se comprueba verificando en la sala de servidores que el UPS
# fue reemplazado.": circular con sinónimos, que una regla de palabras no ve. La decisión del
# usuario: si la persona no dijo cómo se comprueba, Leda lo arma con la evidencia que pide el área;
# y si un criterio dice cómo se comprueba lo juzga la IA por su sentido (como la entrega del motor,
# `lo_descrito_cubre`): la IA dice si lo dice y copia la parte, y el código decide.

UPS = ("hay que cambiar el ups de la sala de servidores que lo vea el tano antes del jueves se "
       "corta todo")
TITULO_UPS = "Cambiar el UPS de la sala de servidores"
RESULTADO_UPS = "El UPS de la sala de servidores está cambiado"
COMO_UPS_CIRCULAR = "se comprueba verificando en la sala de servidores que el UPS fue reemplazado"
CIRCULAR_UPS = ("El UPS de la sala de servidores está cambiado. Se comprueba verificando en la sala "
                "de servidores que el UPS fue reemplazado.")

PLC = "hay que dejar el plc de la comprimidora fette 2000 y sus variables listos para que ariel " \
      "la integre a la interfaz"
TITULO_PLC = "Dejar listo el PLC de la comprimidora Fette 2000"
CIRCULAR = ("El PLC de la comprimidora Fette 2000 y sus variables quedan listos para que Ariel la "
            "integre a la interfaz. Se comprueba revisando que el PLC y sus variables estén "
            "listos para esa integración.")
COMO_CIRCULAR = ("Se comprueba revisando que el PLC y sus variables estén listos para esa "
                 "integración")
CONCRETO = ("El PLC de la comprimidora Fette 2000 y sus variables quedan listos para que Ariel la "
            "integre a la interfaz. Las variables del PLC se leen bien desde la interfaz.")
COMO_CONCRETO = "Las variables del PLC se leen bien desde la interfaz"

DE_LA_EVIDENCIA = "Se comprueba con lo que pide el área:"


def _nadie(dicho: str) -> list[dict[str, Any]]:
    """Nadie del equipo se llama así (en `leda_motor`, "el tano" no es un apodo de nadie)."""
    return []


def _respuesta_del_ups(**cambios) -> dict[str, Any]:
    respuesta = {"titulo": TITULO_UPS, "criterio": CIRCULAR_UPS, "resultado": RESULTADO_UPS,
                 "responsable": "el tano"}
    respuesta.update(cambios)
    return {k: v for k, v in respuesta.items() if v is not None}


def _juicios(ia) -> list[dict[str, Any]]:
    """Lo que recibió el juicio del criterio, en cada llamada."""
    return [json.loads(next(m["content"] for m in p["messages"] if m["role"] == "user"))
            for p in ia.pedidos
            if p["tools"][0]["function"]["name"] == "revisar_el_criterio"]


# Lo que escribe el juicio de mentira como el criterio de Leda (J2-17), sin un nombre ni un número
# que pueda faltar en la tarea.
DEL_JUICIO = "Queda hecho lo que dice la tarea y quien la revisa lo ve terminado en su lugar."


def test_el_criterio_circular_del_ups_no_se_propone(ayuda):
    """El caso del usuario: la IA escribió una comprobación que repite el resultado con un
    sinónimo; el juicio por el sentido la rechaza (sin quién la hace, nadie es "el tano", no hay
    evidencia de un área) y se propone el criterio que escribió el juicio (J2-17)."""
    resultado, ia = _proponer(ayuda, _respuesta_del_ups(), texto=UPS, coinciden=_nadie,
                              juzga=juez(CIRCULAR_UPS, propone=DEL_JUICIO))
    assert resultado.propuesta["criterio"] == DEL_JUICIO
    assert _juicios(ia) == [{"titulo": TITULO_UPS, "descripcion": "", "criterio": CIRCULAR_UPS}]
    assert {"campo": "criterio", "motivo": "sin_comprobacion"} in resultado.descartados
    assert "criterio" not in _avisos(resultado)
    assert _avisos(resultado)["responsable"] == (
        "No encontré a «el tano» en el equipo; elegí quién la hace.")
    assert resultado.propuesta["titulo"] == TITULO_UPS


def test_si_ni_la_ia_ni_el_juicio_escriben_uno_se_dice(ayuda):
    """Sin un criterio que pase y sin evidencia para el de reserva, el campo lo dice (nunca en
    silencio)."""
    resultado, _ = _proponer(ayuda, _respuesta_del_ups(), texto=UPS, coinciden=_nadie,
                             juzga=juez(CIRCULAR_UPS))
    assert "criterio" not in resultado.propuesta
    assert _avisos(resultado)["criterio"] == (
        "No pude proponer el criterio con lo que escribiste; contame cómo se comprueba.")
    assert {"campo": "criterio", "motivo": "sin_propuesta"} in resultado.descartados


def test_el_circular_con_evidencia_se_reemplaza_por_el_del_juicio(ayuda):
    """Con quién la hace, el juicio tiene la evidencia que propuso Leda (J2-19: E1, la foto): si
    el criterio de la IA no dice un resultado, se propone el que escribió el juicio, con sus
    palabras."""
    def juzga(entrada):
        assert entrada["evidencia_que_pide_el_area"] == ["una foto"]
        return {"dice_un_resultado": False, "resultado": RESULTADO_DEL_EJEMPLO,
                "criterio": DEL_JUICIO}
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(evidencia="E1"), juzga=juzga)
    assert resultado.propuesta["criterio"] == DEL_JUICIO
    assert {"campo": "criterio", "motivo": "sin_resultado"} in resultado.descartados


def test_quien_la_hace_ya_elegido_da_su_evidencia(ayuda):
    """La evidencia que pide su área llega a la IA como dato; el juicio, con la que tildó la
    persona (J2-19: nada se tilda solo)."""
    escrito = {**_vacio(responsable_id="m-lucas"), "evidencia": ["foto"]}
    resultado, ia = _proponer(ayuda, _respuesta_del_ups(criterio=RESULTADO_UPS, responsable=None),
                              texto=UPS, escrito=escrito)
    assert ia.entrada(0)["ya_escrito"]["quien_la_hace"]["evidencia_que_pide"] == ["una foto"]
    assert _juicios(ia)[0]["evidencia_que_pide_el_area"] == ["una foto"]
    assert resultado.propuesta["criterio"] == RESULTADO_UPS


def test_sin_quien_la_hace_vale_el_area_del_objetivo(ayuda):
    """Sin quién la hace, el área del objetivo elegido, si la tiene (hoy la base no se la da a
    los objetivos: queda para cuando la tengan)."""
    opciones = json.loads(json.dumps(OPCIONES))
    opciones["objetivos"][0]["area_id"] = "a-infra"
    _, ia = _proponer(ayuda, _respuesta_del_ups(), texto=UPS, coinciden=_nadie,
                      escrito=_vacio(objetivo_id="o-modem"), opciones=opciones)
    assert _juicios(ia)[0]["evidencia_que_pide_el_area"] == ["una foto"]


def test_la_evidencia_de_reserva_de_varios_tipos_se_nombra_entera(ayuda):
    """El criterio de reserva (sólo si el juicio no respondió) nombra toda la evidencia propuesta
    (J2-19: la que eligió Leda, acá los dos tipos del área)."""
    opciones = json.loads(json.dumps(OPCIONES))
    opciones["politicas"][0].update({
        "evidencia_requerida": ["explicacion", "resultado_de_prueba"],
        "tipos": {"explicacion": {"clases": ["texto"],
                                  "en_palabras": "cómo quedó el trabajo, descrito por quien lo hizo"},
                  "resultado_de_prueba": {"clases": ["texto"],
                                          "en_palabras": "cómo se probó y qué dio la prueba"}}})
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(evidencia="E1, E2"), opciones=opciones,
                             juzga=lambda entrada: TimeoutError("plazo"))
    comprobacion = resultado.propuesta["criterio"].split(f"{DE_LA_EVIDENCIA} ", 1)[1]
    assert comprobacion == ("cómo quedó el trabajo, descrito por quien lo hizo; cómo se probó y qué "
                            "dio la prueba.")


@pytest.mark.parametrize("falla", [TimeoutError("plazo"), {"como_se_comprueba": "x"}])
def test_si_el_juicio_no_responde_al_proponer_no_se_finge(ayuda, falla):
    """Sin el juicio, el criterio de la IA no se propone como revisado: vale el de reserva, con la
    evidencia propuesta."""
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(evidencia="E1"),
                             juzga=lambda entrada: falla)
    assert resultado.propuesta["criterio"] == (
        f"{RESULTADO_DEL_EJEMPLO}. {DE_LA_EVIDENCIA} una foto.")
    assert {"campo": "criterio", "motivo": "sin_revisar"} in resultado.descartados


def test_si_el_juicio_no_responde_sin_evidencia_no_se_propone(ayuda):
    resultado, _ = _proponer(ayuda, _respuesta_del_ups(), texto=UPS, coinciden=_nadie,
                             juzga=lambda entrada: TimeoutError("plazo"))
    assert "criterio" not in resultado.propuesta
    assert {"campo": "criterio", "motivo": "sin_revisar"} in resultado.descartados
    assert "criterio" in _avisos(resultado)


def test_la_regla_de_palabras_de_la_j2_9_ya_no_existe(ayuda):
    for nombre in ("lo_que_agrega", "no_agrega_nada", "_DE_FUNCION", "_DEL_MARCO", "_MARCO",
                   "_con_contenido", "_raiz", "criterio_propuesto", "_revisar_el_criterio"):
        assert not hasattr(ayuda, nombre), nombre


def test_un_criterio_con_palabras_del_marco_no_se_rechaza_por_ellas(ayuda):
    """"Revisar" o "listo" ya no deciden nada: lo decide el juicio de la IA por el sentido."""
    criterio = "Se revisa que la luz verde del tablero esté encendida y queda listo."
    ia = IADeLaCarga(juzga=juzga_que_si)
    juicio = ayuda.juzgar_el_criterio(ia, titulo="Colocar el tablero", descripcion="",
                                      criterio=criterio)
    assert juicio.motivo is None and len(ia.pedidos) == 1
    ia = IADeLaCarga(juzga=juzga_que_si)
    assert ayuda.juzgar_el_criterio(ia, titulo="Colocar el tablero", descripcion="",
                                    criterio="listo").motivo is None
    assert len(ia.pedidos) == 1


def test_las_instrucciones_describen_el_trabajo_sin_frases_de_ejemplo(ayuda):
    _, ia = _proponer(ayuda, _respuesta_del_ups(), texto=UPS, coinciden=_nadie,
                      juzga=juez(CIRCULAR_UPS))
    datos = ia.pedidos[0]["tools"][0]["function"]["parameters"]["properties"]
    assert {"criterio", "resultado"} <= set(datos) and "como_se_comprueba" not in datos
    assert "evidencia" in ia.instrucciones(0)
    textos = " ".join([ia.instrucciones(0), ia.instrucciones(1),
                       json.dumps(ia.pedidos[0]["tools"], ensure_ascii=False),
                       json.dumps(ia.pedidos[1]["tools"], ensure_ascii=False)]).lower()
    for frase in ("ups", "servidores", "tano", "foto", "estante", "interfaz", "variables",
                  "listo"):
        assert frase not in textos, frase


# El criterio escrito por la persona, al cargar: el juicio de la IA por el sentido y lo que decide
# el código.

def _juicio(ayuda, ia, criterio, *, titulo=TITULO_PLC, descripcion=""):
    return ayuda.juzgar_el_criterio(ia, titulo=titulo, descripcion=descripcion, criterio=criterio)


NO_LO_DICE = {"dice_como_se_comprueba": False, "como_se_comprueba": "", "criterio": DEL_JUICIO}


@pytest.mark.parametrize("titulo, criterio", [(TITULO_PLC, CIRCULAR), (TITULO_UPS, CIRCULAR_UPS),
                                              ("Colocar el estante", "No se"),
                                              ("Colocar el estante", "Hacerlo con cuidado")])
def test_al_cargar_lo_que_no_dice_como_se_comprueba_se_rechaza_por_el_juicio(ayuda, titulo,
                                                                             criterio):
    ia = IADeLaCarga(NO_LO_DICE)
    juicio = _juicio(ayuda, ia, criterio, titulo=titulo)
    assert juicio.motivo == "sin_comprobacion" and juicio.falla is None
    # J2-17: el rechazo trae el criterio que escribió la IA con sus palabras.
    assert juicio.propuesta == DEL_JUICIO and not juicio.de_reserva
    assert len(ia.pedidos) == 1
    assert ia.pedidos[0]["tools"][0]["function"]["name"] == ayuda.NOMBRE_DEL_JUICIO


@pytest.mark.parametrize("criterio", ["Cambiar el UPS de la sala de servidores.",
                                      "  cambiar el ups de la sala de SERVIDORES ", "...", ""])
def test_al_cargar_sin_nada_que_juzgar_se_rechaza_diga_lo_que_diga_la_ia(ayuda, criterio):
    """La única guarda sin la IA, y sin una lista de palabras: un criterio vacío o igual al
    título. J2-17: la IA se llama igual, sólo para proponer uno (sin ella, sin propuesta y con la
    falla para el incidente)."""
    ia = IADeLaCarga({"dice_como_se_comprueba": True, "como_se_comprueba": criterio or "x",
                      "criterio": DEL_JUICIO})
    juicio = _juicio(ayuda, ia, criterio, titulo=TITULO_UPS)
    assert juicio.motivo == "sin_comprobacion" and juicio.propuesta == DEL_JUICIO
    assert ayuda.sin_nada_que_juzgar(TITULO_UPS, criterio)
    assert len(ia.pedidos) == 1
    juicio = _juicio(ayuda, IADeLaCarga(TimeoutError("plazo")), criterio, titulo=TITULO_UPS)
    assert juicio.motivo == "sin_comprobacion" and juicio.propuesta is None
    assert isinstance(juicio.falla, TimeoutError)


def test_al_cargar_un_criterio_con_una_comprobacion_concreta_pasa(ayuda):
    ia = IADeLaCarga({"dice_como_se_comprueba": True, "como_se_comprueba": COMO_CONCRETO})
    juicio = _juicio(ayuda, ia, CONCRETO)
    assert juicio.motivo is None and juicio.falla is None


def test_al_cargar_la_ia_recibe_solo_la_tarea(ayuda):
    ia = IADeLaCarga({"dice_como_se_comprueba": True, "como_se_comprueba": COMO_CONCRETO})
    _juicio(ayuda, ia, CONCRETO, descripcion="Dejarlo para la integración.")
    assert ia.entrada() == {"titulo": TITULO_PLC, "descripcion": "Dejarlo para la integración.",
                            "criterio": CONCRETO}
    parametros = ia.pedidos[0]["tools"][0]["function"]["parameters"]
    assert parametros["required"] == ["dice_como_se_comprueba", "como_se_comprueba", "criterio"]
    assert parametros["properties"]["dice_como_se_comprueba"]["type"] == "boolean"


@pytest.mark.parametrize("respuesta", [
    TimeoutError("plazo"),
    {"choices": [{"finish_reason": "stop", "message": {"content": "hola"}}]},
    # Sin el juicio, con otra forma, o con una parte vacía o que no está en el criterio: no se sabe.
    {},
    {"como_se_comprueba": COMO_CONCRETO},
    {"dice_como_se_comprueba": "si", "como_se_comprueba": COMO_CONCRETO},
    {"dice_como_se_comprueba": True, "como_se_comprueba": ""},
    {"dice_como_se_comprueba": True, "como_se_comprueba": 3},
    {"dice_como_se_comprueba": True, "como_se_comprueba": "las alarmas suenan en la sala"},
])
def test_al_cargar_si_la_ia_no_juzga_no_se_finge_la_revision(ayuda, respuesta):
    juicio = _juicio(ayuda, IADeLaCarga(respuesta), CONCRETO)
    assert juicio.motivo == "sin_revisar" and juicio.falla is not None


def test_al_cargar_sin_ia_configurada_no_se_revisa(ayuda):
    from leda.motor.recibir import IANoConfigurada

    juicio = _juicio(ayuda, IANoConfigurada("No hay modelo configurado."), CONCRETO)
    assert juicio.motivo == "sin_revisar" and isinstance(juicio.falla, LookupError)


# --- El criterio escrito, con la evidencia que pide el área (J2-14) ------------------------------
#
# La prueba del usuario en el celular (2026-10-13): "El ups queda cambiado y funcionando" se
# rechazaba con "Contame cómo se sabe que está terminada." aunque el área ya pedía "cómo se probó y
# qué dio la prueba", y el rechazo no proponía nada. La decisión del usuario: la persona escribe el
# resultado y cómo se comprueba sale de la evidencia que pide el área, como en la propuesta de
# Leda; sólo se rechaza lo que no dice ningún resultado, y todo rechazo trae un criterio propuesto
# (el resultado más la evidencia del área). Sin evidencia del área, sigue el juicio de la J2-13.

PRUEBA = "cómo se probó y qué dio la prueba"
FOTO = "una foto del trabajo terminado"
UPS_DEL_CELULAR = "El ups queda cambiado y funcionando"
ORDENADO = "Quedó ordenado y limpio"
RESULTADO_PROPUESTO = "El UPS de la sala de servidores queda cambiado y funcionando"
SIN_RESULTADO = {"dice_un_resultado": False, "resultado": RESULTADO_PROPUESTO}


def _con_evidencia(ayuda, ia, criterio, *, titulo=TITULO_UPS, evidencia=(PRUEBA,)):
    return ayuda.juzgar_el_criterio(ia, titulo=titulo, descripcion="", criterio=criterio,
                                    evidencia=list(evidencia))


@pytest.mark.parametrize("titulo, criterio, evidencia", [
    (TITULO_UPS, UPS_DEL_CELULAR, (PRUEBA,)),
    ("Ordenar el depósito", ORDENADO, (FOTO,)),
])
def test_con_evidencia_un_resultado_escrito_se_carga_aunque_no_diga_como(ayuda, titulo, criterio,
                                                                       evidencia):
    """Los dos casos del celular: dicen un resultado y el área ya dice cómo se comprueba."""
    ia = IADeLaCarga({"dice_un_resultado": True, "resultado": criterio})
    juicio = _con_evidencia(ayuda, ia, criterio, titulo=titulo, evidencia=evidencia)
    assert juicio.motivo is None and juicio.propuesta is None
    assert ia.entrada() == {"titulo": titulo, "descripcion": "", "criterio": criterio,
                            "evidencia_que_pide_el_area": list(evidencia)}
    parametros = ia.pedidos[0]["tools"][0]["function"]["parameters"]
    assert parametros["required"] == ["dice_un_resultado", "resultado", "criterio"]
    assert parametros["properties"]["dice_un_resultado"]["type"] == "boolean"
    assert ia.pedidos[0]["tools"][0]["function"]["name"] == ayuda.NOMBRE_DEL_JUICIO


def test_con_evidencia_lo_que_no_dice_un_resultado_trae_un_criterio_propuesto(ayuda):
    ia = IADeLaCarga(SIN_RESULTADO)
    juicio = _con_evidencia(ayuda, ia, "No se")
    assert juicio.motivo == "sin_resultado" and juicio.falla is None
    assert juicio.propuesta == (f"{RESULTADO_PROPUESTO}. Se comprueba con lo que pide el área: "
                                f"{PRUEBA}.")
    assert juicio.propuesta == ayuda.criterio_con_la_evidencia(RESULTADO_PROPUESTO, [PRUEBA])
    # Sin el criterio de la IA, es el de reserva (J2-17).
    assert juicio.de_reserva


@pytest.mark.parametrize("dice", [True, False])
def test_con_evidencia_igual_al_titulo_se_rechaza_igual_y_trae_la_propuesta(ayuda, dice):
    """El código decide que igual al título no dice un resultado, diga lo que diga la IA; la IA se
    llama sólo para proponer el resultado."""
    ia = IADeLaCarga({"dice_un_resultado": dice, "resultado": RESULTADO_PROPUESTO})
    juicio = _con_evidencia(ayuda, ia, f"{TITULO_UPS}.")
    assert juicio.motivo == "sin_resultado"
    assert juicio.propuesta.startswith(f"{RESULTADO_PROPUESTO}. Se comprueba con lo que pide")
    assert len(ia.pedidos) == 1


def test_con_evidencia_y_la_ia_caida_igual_al_titulo_se_rechaza_sin_propuesta(ayuda):
    """Sin propuesta, el rechazo igual dice qué falta, con la falla para el incidente."""
    from leda.motor.recibir import IANoConfigurada

    juicio = _con_evidencia(ayuda, IANoConfigurada("No hay modelo configurado."), TITULO_UPS)
    assert juicio.motivo == "sin_resultado" and juicio.propuesta is None
    assert isinstance(juicio.falla, LookupError)


@pytest.mark.parametrize("respuesta", [
    TimeoutError("plazo"),
    {},
    {"dice_un_resultado": "si", "resultado": RESULTADO_PROPUESTO},
])
def test_con_evidencia_si_la_ia_no_juzga_no_se_finge_la_revision(ayuda, respuesta):
    juicio = _con_evidencia(ayuda, IADeLaCarga(respuesta), UPS_DEL_CELULAR)
    assert juicio.motivo == "sin_revisar" and juicio.falla is not None


@pytest.mark.parametrize("resultado", ["", 3, "El UPS de las 4 salas queda cambiado"])
def test_un_resultado_propuesto_que_no_sirve_no_se_propone(ayuda, resultado):
    """Un resultado vacío, con otra forma o con un número que nadie dijo: el rechazo queda, sin
    propuesta y con la falla (nunca en silencio)."""
    juicio = _con_evidencia(ayuda, IADeLaCarga({"dice_un_resultado": False,
                                                "resultado": resultado}), "No se")
    assert juicio.motivo == "sin_resultado" and juicio.propuesta is None
    assert juicio.falla is not None


def test_sin_evidencia_del_area_sigue_pidiendo_como_se_comprueba(ayuda):
    """Sin evidencia, el criterio tiene que decir cómo se comprueba (el juicio de la J2-13)."""
    ia = IADeLaCarga(NO_LO_DICE)
    juicio = _con_evidencia(ayuda, ia, UPS_DEL_CELULAR, evidencia=())
    # J2-17: el rechazo sin evidencia también trae un criterio propuesto.
    assert juicio.motivo == "sin_comprobacion" and juicio.propuesta == DEL_JUICIO
    assert "evidencia_que_pide_el_area" not in ia.entrada()
    assert ia.pedidos[0]["tools"][0]["function"]["parameters"]["required"] == [
        "dice_como_se_comprueba", "como_se_comprueba", "criterio"]


def test_la_evidencia_de_la_carga_sale_de_la_politica_en_palabras(ayuda):
    """La evidencia que se eligió en el formulario, en palabras de todos los días y en el orden
    del área; un tipo que el área no conoce no cuenta (la base lo rechaza igual)."""
    opciones = json.loads(json.dumps(OPCIONES))
    opciones["politicas"][0]["tipos"]["prueba"] = {"clases": ["texto"], "en_palabras": PRUEBA}
    assert ayuda.evidencia_de_la_carga(opciones, "m-lucas", ["prueba", "foto", "otra"]) == [
        "una foto", PRUEBA]
    assert ayuda.evidencia_de_la_carga(opciones, "m-lucas", []) == []
    assert ayuda.evidencia_de_la_carga(opciones, "m-marcos", ["foto"]) == []


def test_las_instrucciones_del_resultado_describen_el_trabajo_sin_frases_de_ejemplo(ayuda):
    ia = IADeLaCarga(SIN_RESULTADO)
    _con_evidencia(ayuda, ia, "No se")
    textos = " ".join([ia.instrucciones(0),
                       json.dumps(ia.pedidos[0]["tools"], ensure_ascii=False)]).lower()
    assert "evidencia" in textos and "resultado" in textos
    for frase in ("ups", "servidores", "foto", "ordenado", "limpio", "no sé", "funcionando",
                  "cambiado"):
        assert frase not in textos, frase


# --- El tope de salida ------------------------------------------------------------------------

def test_el_tope_de_salida_alcanza_para_la_propuesta_entera(ayuda):
    """La revisión `review-6a44e26466b95395`: la propuesta puede llevar hasta 1500 caracteres de
    texto más el JSON, y un modelo que razona gasta parte del tope antes de contestar; con el tope
    de elegir jugadas (1500) se podía cortar. Nunca menos que el de redactar un mensaje."""
    _, ia = _proponer(ayuda, _respuesta_del_ejemplo())
    assert ia.pedidos[0]["max_tokens"] >= 3000
    ia = IADeLaCarga(_respuesta_del_ejemplo())
    ia.parametros = {"tope_jugadas": 1500, "tope_redaccion": 6000}
    ayuda.pedir(ia, ayuda.entrada_de_la_ia(EJEMPLO, _vacio(), OPCIONES))
    assert ia.pedidos[0]["max_tokens"] == 6000


# --- La IA que no responde --------------------------------------------------------------------

def test_sin_ia_configurada_la_ayuda_no_responde(ayuda):
    from leda.motor.recibir import IANoConfigurada

    with pytest.raises(LookupError):
        ayuda.pedir(IANoConfigurada("No hay modelo configurado."), {"texto": "x"})


@pytest.mark.parametrize("respuesta", [
    {"choices": [{"finish_reason": "stop", "message": {"content": "hola"}}]},
    {"choices": [{"finish_reason": "length", "message": {"tool_calls": []}}]},
    {"choices": [{"finish_reason": "tool_calls", "message": {"tool_calls": [
        {"function": {"name": "proponer_la_carga", "arguments": "no es json"}}]}}]},
    {"choices": []},
])
def test_una_respuesta_que_no_se_puede_leer_es_que_la_ia_no_respondio(ayuda, respuesta):
    from leda.motor.ia_real import RespuestaInvalida

    with pytest.raises(RespuestaInvalida):
        ayuda.pedir(IADeLaCarga(respuesta), ayuda.entrada_de_la_ia(EJEMPLO, _vacio(), OPCIONES))


def test_datos_con_otra_forma_se_ignoran(ayuda):
    resultado, _ = _proponer(ayuda, {"titulo": 3, "responsable": ["lucas"], "fecha": None,
                                     "espera": {"x": 1}})
    assert resultado.propuesta == {}


# --- La herramienta de medición (`tools/medir_ayuda_al_cargar.py`) ----------------------------
#
# La revisión `review-5457837d11cb0618`: con el cupo agotado el informe se perdía, `--veces 0`
# corría sin medir nada, toda excepción se contaba como de la IA, los nombres se buscaban con una
# copia de la función del servidor y la corrida en seco daba 0 de 11 sin probar nada.

@pytest.fixture
def medir():
    import importlib.util
    from pathlib import Path

    ruta = Path(__file__).resolve().parents[1] / "tools" / "medir_ayuda_al_cargar.py"
    spec = importlib.util.spec_from_file_location("medir_ayuda_al_cargar", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class _SinCupo(Exception):
    def __init__(self) -> None:
        super().__init__("cupo")
        self.response = type("R", (), {"status_code": 429})()


def test_la_medicion_rechaza_menos_de_una_vuelta(medir):
    for veces in ("0", "-1"):
        with pytest.raises(SystemExit) as salida:
            medir.main(["--veces", veces])
        assert salida.value.code == 2


def test_sin_cupo_la_medicion_guarda_lo_medido_antes_de_salir(medir, monkeypatch, tmp_path):
    # El primer pedido gasta dos llamadas: la propuesta y el juicio del criterio (J2-17).
    ia = IADeLaCarga({}, {}, _SinCupo())
    monkeypatch.setattr(medir, "la_ia", lambda texto: ia)
    salida = tmp_path / "informe.json"
    assert medir.main(["--ia", "x", "--salida", str(salida)]) == medir.SIN_CUPO
    informe = json.loads(salida.read_text(encoding="utf-8"))
    assert informe["cortada"] == "sin_cupo"
    assert [r["pedido"] for r in informe["resultados"]] == [medir.PEDIDOS[0]["nombre"]]


def test_una_falla_de_la_ia_no_es_un_error_del_programa(medir, monkeypatch, tmp_path):
    from leda.motor.ia_real import PlazoAgotado, RespuestaInvalida

    # Cada propuesta gasta dos llamadas (J2-17): alcanza con el doble.
    ia = IADeLaCarga(RespuestaInvalida("x"), PlazoAgotado(40),
                     *([{}] * (2 * len(medir.PEDIDOS))))
    monkeypatch.setattr(medir, "la_ia", lambda texto: ia)
    salida = tmp_path / "informe.json"
    assert medir.main(["--ia", "x", "--salida", str(salida)]) == 1
    informe = json.loads(salida.read_text(encoding="utf-8"))
    assert informe["cortada"] is None
    assert [r["falla"] for r in informe["resultados"][:2]] == ["ia", "ia"]
    assert informe["resultados"][0]["fallas"] == ["la IA no respondió (RespuestaInvalida)"]


def test_un_error_del_programa_corta_y_se_informa_como_tal(medir, monkeypatch, tmp_path):
    ia = IADeLaCarga(*([{}] * len(medir.PEDIDOS)))
    monkeypatch.setattr(medir, "la_ia", lambda texto: ia)

    def revisar_roto(*a, **k):
        raise KeyError("dato")
    monkeypatch.setattr(medir.ayuda_al_cargar, "revisar", revisar_roto)
    salida = tmp_path / "informe.json"
    assert medir.main(["--ia", "x", "--salida", str(salida)]) == medir.ERROR_DEL_PROGRAMA
    informe = json.loads(salida.read_text(encoding="utf-8"))
    assert informe["cortada"] == "error_del_programa"
    (resultado,) = informe["resultados"]
    assert resultado["falla"] == "programa"
    assert "KeyError" in resultado["fallas"][0]
    # Cortó en el primero: no gasta más llamadas.
    assert len(ia.pedidos) == 1


def test_la_medicion_busca_los_nombres_con_la_funcion_del_servidor(medir, monkeypatch):
    from leda.motor import fichas

    llamadas = []
    original = fichas.integrantes_que_coinciden

    def espia(cur, dicho):
        llamadas.append(dicho)
        return original(cur, dicho)
    monkeypatch.setattr(fichas, "integrantes_que_coinciden", espia)
    assert [f["membership_id"] for f in medir.coinciden("lucas")] == ["m-lucas"]
    assert [f["membership_id"] for f in medir.coinciden("el tano")] == ["m-marcos"]
    assert medir.coinciden("pepe") == []
    assert llamadas == ["lucas", "el tano", "pepe"]


def test_en_seco_la_medicion_prueba_algo(medir, tmp_path, capsys):
    """La IA en seco propone lo esperado para el ejemplo del usuario, un sábado, "antes del
    jueves", el PLC, el UPS de la prueba del usuario y "cirelabs", juzga los criterios por su
    sentido y corrige la ortografía: el ejemplo pasa entero (el criterio, con las palabras de la
    IA), el sábado no pone la fecha, "antes del jueves" pone el miércoles, el UPS circular se
    reemplaza por el criterio que escribió el juicio (J2-17), "cirelabs" sale como CoreLabs, el
    código decide cada criterio escrito (J2-14: todo rechazo trae uno propuesto, con naturalidad) y
    acepta las correcciones que son sólo de ortografía; los demás, sin guion, no proponen nada."""
    salida = tmp_path / "informe.json"
    assert medir.main(["--salida", str(salida)]) == 1
    informe = json.loads(salida.read_text(encoding="utf-8"))
    bien = {r["pedido"] for r in informe["resultados"] if r["bien"]}
    assert bien == {"el ejemplo del usuario", "un sábado no es hábil",
                    "un apodo y un día de la semana", "el PLC, sin quién ni cómo se comprueba",
                    "el UPS de la prueba del usuario", "cirelabs",
                    "el criterio circular del usuario", "un criterio con una comprobación concreta",
                    "un criterio con palabras y sin resultado", "no se",
                    "el UPS circular, escrito", "un criterio concreto con palabras de revisar",
                    "igual al título", "el UPS del celular", "ordenado y limpio",
                    "el UPS del celular, sin evidencia del área",
                    "ortografía: el árbol y CoreLabs", "ortografía: bien escrito no se toca",
                    "ortografía: como en un chat",
                    # J2-18: Leda propone quién la hace y la evidencia; a "pepe" no lo reemplaza.
                    "los tornillos, sin quién ni cuándo", "alguien que no es del equipo"}
    assert len(medir.PEDIDOS) == 27
    (tornillos,) = [r for r in informe["resultados"]
                    if r["pedido"] == "los tornillos, sin quién ni cuándo"]
    assert tornillos["propuesta"]["responsable_id"] == "m-lucas"
    assert tornillos["responsable_de"] == "leda"
    assert tornillos["propuesta"]["evidencia"] == ["foto"]
    assert tornillos["sin_naturalidad"] == {}
    (pepe,) = [r for r in informe["resultados"] if r["pedido"] == "alguien que no es del equipo"]
    assert "responsable_id" not in pepe["propuesta"] and pepe["responsable_de"] is None
    (chat,) = [r for r in informe["resultados"] if r["pedido"] == "ortografía: como en un chat"]
    assert chat["corregidos"]["titulo"]["texto"] == "Cambiar la batería del UPS q no anda"
    assert chat["palabras_rechazadas"] == [{"campo": "titulo", "cantidad": 1}]
    assert all(isinstance(r["segundos"], float) for r in informe["resultados"])
    (sabado,) = [r for r in informe["resultados"] if r["pedido"] == "un sábado no es hábil"]
    assert {"campo": "fecha", "motivo": "no_es_habil"} in sabado["descartados"]
    (antes,) = [r for r in informe["resultados"]
                if r["pedido"] == "un apodo y un día de la semana"]
    assert antes["propuesta"]["fecha"] == "2026-10-14"
    (ejemplo,) = [r for r in informe["resultados"] if r["pedido"] == "el ejemplo del usuario"]
    assert ejemplo["propuesta"]["criterio"] == medir.GUION["el ejemplo del usuario"]["criterio"]
    assert ejemplo["criterio_de"] == "ia" and ejemplo["sin_naturalidad"] == {}
    (ups,) = [r for r in informe["resultados"] if r["pedido"] == "el UPS de la prueba del usuario"]
    assert ups["juicio"] == "sin_comprobacion" and ups["criterio_de"] == "juicio"
    assert "Contame cómo se sabe que está terminada." not in ups["avisos"]
    (no_se,) = [r for r in informe["resultados"] if r["pedido"] == "no se"]
    assert no_se["juicio"] == "sin_resultado" and no_se["de_reserva"] is False
    assert "Se comprueba con lo que pide el área" not in no_se["propuesta"]
    (arbol,) = [r for r in informe["resultados"]
                if r["pedido"] == "ortografía: el árbol y CoreLabs"]
    assert arbol["corregidos"]["titulo"]["texto"] == "Plantar el árbol de la entrada"
    assert f"21 de {len(medir.PEDIDOS)} bien" in capsys.readouterr().out


def test_la_medicion_marca_lo_escrito_sin_naturalidad(medir):
    """J2-17, sólo en la medición: una propuesta con una etiqueta de la evidencia copiada tal cual,
    la frase de la plantilla o una lista armada con ";" sale mal, para que la ronda con la IA real
    muestre si la IA escribe como una persona del equipo."""
    etiquetas = medir._etiquetas({})
    assert medir.sin_naturalidad("El UPS queda cambiado y se ve encendido.", etiquetas) == []
    # Una etiqueta corta se dice naturalmente: no cuenta.
    assert medir.sin_naturalidad("Queda colgado y se ve en una foto.", etiquetas) == []
    plantilla = "El UPS queda cambiado. Se comprueba con lo que pide el área: una foto."
    assert medir.sin_naturalidad(plantilla, etiquetas) == ["la frase de la plantilla"]
    # J2-18: una etiqueta pegada como un fragmento cuenta; un solo ";" une dos oraciones.
    copiada = "El UPS queda cambiado; cómo se probó y qué dio la prueba."
    assert medir.sin_naturalidad(copiada, etiquetas) == [
        "la etiqueta «cómo se probó y qué dio la prueba» pegada como un fragmento"]
    # J2-18: lo que marcaba de más la ronda de la J2-17, dicho dentro de una oración natural.
    for natural in ("El estante queda colocado y se puede ver en una foto del trabajo terminado.",
                    "La batería queda cambiada; se prueba que el UPS aguanta sin luz.",
                    "Queda andando, y cómo se probó y qué dio la prueba lo cuenta quien lo hizo."):
        assert medir.sin_naturalidad(natural, etiquetas) == [], natural
    # Una lista sí: un "·", o dos ";" en una oración.
    assert medir.sin_naturalidad("Queda cambiado · se prueba.", etiquetas) == [
        "una lista con ; o ·"]
    assert medir.sin_naturalidad("Queda cambiado; se prueba; se mide.", etiquetas) == [
        "una lista con ; o ·"]
    assert medir.sin_naturalidad("Una foto del trabajo terminado.", etiquetas) == [
        "la etiqueta «una foto del trabajo terminado» pegada como un fragmento"]
    # Un rechazo cuyo criterio propuesto es la plantilla (el de reserva) sale mal.
    (no_se,) = [p for p in medir.PEDIDOS if p["nombre"] == "no se"]
    ok, detalle = medir.medir(IADeLaCarga({"dice_un_resultado": False,
                                           "resultado": "El estante queda colocado"}), no_se)
    assert ok is False and detalle["de_reserva"] is True
    assert detalle["sin_naturalidad"] == [
        "la frase de la plantilla",
        "la etiqueta «una foto del trabajo terminado» pegada como un fragmento"]


def test_la_medicion_juzga_los_criterios_escritos_y_cuenta_la_falla_de_la_ia(medir):
    """J2-9, J2-13, J2-14 y J2-17: un criterio escrito se mide con el mismo juicio que la carga,
    con la evidencia del pedido; si la IA no lo juzgó, o lo rechazó sin un criterio propuesto, es
    una falla de la IA, nunca un juicio."""
    from leda.motor.ia_real import PlazoAgotado

    (circular,) = [p for p in medir.PEDIDOS if p["nombre"] == "el criterio circular del usuario"]
    ok, detalle = medir.medir(IADeLaCarga(PlazoAgotado(40)), circular)
    assert ok is False and detalle["falla"] == "ia"
    # Con la evidencia del área, una respuesta sin el juicio del resultado no se da por juzgada.
    ok, detalle = medir.medir(IADeLaCarga({"dice_como_se_comprueba": True,
                                           "como_se_comprueba": "las variables se leen bien"}),
                              circular)
    assert ok is False and detalle["falla"] == "ia"
    estante = {"dice_un_resultado": False, "resultado": "El estante queda colocado",
               # J2-22: contado desde quien la hace (desde quien revisa, la medición lo marca).
               "criterio": "El estante queda colocado y firme, y quien lo colocó cuenta cómo quedó."}
    (igual,) = [p for p in medir.PEDIDOS if p["nombre"] == "igual al título"]
    ia = IADeLaCarga({**estante, "dice_un_resultado": True})
    assert medir.medir(ia, igual)[0] is True and len(ia.pedidos) == 1
    # Igual al título se rechaza sin la IA, pero sin ella no hay propuesta: es una falla de la IA.
    ok, detalle = medir.medir(IADeLaCarga(PlazoAgotado(40)), igual)
    assert ok is False and detalle["falla"] == "ia"
    assert detalle["fallas"] == ["propuesta: la IA no respondió (PlazoAgotado)"]
    (no_se,) = [p for p in medir.PEDIDOS if p["nombre"] == "no se"]
    ia = IADeLaCarga(estante)
    assert medir.medir(ia, no_se)[0] is True and len(ia.pedidos) == 1
    # Un criterio y un resultado que no pasan los controles no dan propuesta: el pedido sale mal.
    ok, detalle = medir.medir(IADeLaCarga({**estante, "resultado": "Los 4 estantes",
                                           "criterio": "Los 4 estantes."}), no_se)
    assert ok is False and detalle["falla"] == "ia"


def test_j2_19_la_medicion_marca_dos_evidencias_que_dicen_lo_mismo(medir):
    """J2-19: la herramienta (no el código de Leda) marca la evidencia propuesta con dos tipos que
    dicen lo mismo, los que el usuario vio tildados juntos; con uno solo, el pedido sale bien."""
    (tornillos,) = [p for p in medir.PEDIDOS if p["nombre"] == "los tornillos, sin quién ni cuándo"]
    guion = medir.GUION["los tornillos, sin quién ni cuándo"]
    ok, detalle = medir.medir(IADeLaCarga({**guion, "evidencia": "E2, E4"}, juzga=juzga_que_si),
                              tornillos)
    assert ok is False
    assert detalle["propuesta"]["evidencia"] == ["captura", "foto"]
    assert any("dicen lo mismo" in f for f in detalle["fallas"])
    ok, detalle = medir.medir(IADeLaCarga(guion, juzga=juzga_que_si), tornillos)
    assert ok is True and detalle["propuesta"]["evidencia"] == ["foto"]


def test_la_medicion_de_la_ortografia_cuenta_lo_que_el_codigo_rechaza(medir):
    (arbol,) = [p for p in medir.PEDIDOS if p["nombre"] == "ortografía: el árbol y CoreLabs"]
    ok, detalle = medir.medir(IADeLaCarga({"titulo": "Plantar el árbol de la entrada",
                                           "descripcion": "Coordinar con CoreLabs el envío"}),
                              arbol)
    assert ok is False
    assert detalle["rechazados"] == [{"campo": "descripcion", "motivo": "no_es_ortografia"}]
    assert detalle["corregidos"]["titulo"]["texto"] == "Plantar el árbol de la entrada"


def test_la_medicion_trae_los_criterios_del_celular_con_su_evidencia(medir):
    """J2-14: los dos criterios de la segunda prueba del usuario, con la evidencia que mostraba
    el formulario, se tienen que cargar; sin evidencia del área, el mismo no alcanza."""
    pedidos = {p["nombre"]: p for p in medir.PEDIDOS}
    ups = pedidos["el UPS del celular"]
    assert ups["criterio_escrito"] == UPS_DEL_CELULAR
    assert ups["evidencia"] == [PRUEBA]
    assert ups["juicio"] is None
    assert pedidos["ordenado y limpio"]["criterio_escrito"] == "Quedó ordenado y limpio"
    assert pedidos["ordenado y limpio"]["evidencia"] == ["una foto del trabajo terminado"]
    assert pedidos["ordenado y limpio"]["juicio"] is None
    sin = pedidos["el UPS del celular, sin evidencia del área"]
    assert (sin["evidencia"], sin["juicio"]) == ([], "sin_comprobacion")


def test_si_el_juicio_de_la_propuesta_no_responde_la_medicion_lo_cuenta(medir):
    """La revisión `review-bfa79042ca12447b`: que la IA no juzgara la manera de comprobarla que
    propuso se descartaba y el pedido podía salir bien. Como en `medir_el_juicio`, es una falla de
    la IA: el pedido sale mal y el informe lo dice, con lo que la propuesta dio igual."""
    from leda.motor.ia_real import PlazoAgotado

    (ups,) = [p for p in medir.PEDIDOS if p["nombre"] == "el UPS de la prueba del usuario"]
    ia = IADeLaCarga(medir.GUION[ups["nombre"]], PlazoAgotado(40))
    ok, detalle = medir.medir(ia, ups)
    assert len(ia.pedidos) == 2
    assert ok is False and detalle["falla"] == "ia"
    assert detalle["falla_del_juicio"] == "la IA no respondió (PlazoAgotado)"
    assert "juicio: la IA no respondió (PlazoAgotado)" in detalle["fallas"]
    assert detalle["juicio"] == "sin_revisar"
    assert detalle["propuesta"]["titulo"] == medir.GUION[ups["nombre"]]["titulo"]


def test_sin_cupo_en_el_juicio_de_la_propuesta_la_medicion_se_corta(medir):
    (ups,) = [p for p in medir.PEDIDOS if p["nombre"] == "el UPS de la prueba del usuario"]
    with pytest.raises(medir.SinCupo):
        medir.medir(IADeLaCarga(medir.GUION[ups["nombre"]], _SinCupo()), ups)


def test_la_medicion_trae_el_ups_de_la_prueba_del_usuario(medir):
    (ups,) = [p for p in medir.PEDIDOS if p["nombre"] == "el UPS de la prueba del usuario"]
    assert ups["texto"] == ("hay que cambiar el ups de la sala de servidores que lo vea el tano "
                            "antes del jueves se corta todo")
    # En `leda_motor` "el tano" no es nadie.
    assert medir.coinciden("el tano", ups["apodos"]) == []


@pytest.mark.parametrize("falla", [
    __import__("socket").gaierror(11001, "getaddrinfo failed"),
    __import__("ssl").SSLError("certificado"),
    OSError(__import__("errno").ENETUNREACH, "Network is unreachable"),
])
def test_un_error_de_la_red_que_no_es_de_conexion_es_de_la_ia(medir, monkeypatch, tmp_path,
                                                              falla):
    """La revisión `review-ded34de579ff3bc5`: acotar `OSError` a `ConnectionError` y
    `TimeoutError` dejaba afuera no encontrar el servidor, el certificado y una red
    inalcanzable, que son de la red y no del programa."""
    ia = IADeLaCarga(falla, *([{}] * (2 * len(medir.PEDIDOS))))
    monkeypatch.setattr(medir, "la_ia", lambda texto: ia)
    salida = tmp_path / "informe.json"
    assert medir.main(["--ia", "x", "--salida", str(salida)]) == 1
    informe = json.loads(salida.read_text(encoding="utf-8"))
    assert informe["resultados"][0]["falla"] == "ia"


def test_antes_del_jueves_en_la_medicion_espera_el_miercoles(medir):
    """Hoy, en la medición, es el miércoles 14: antes del jueves 15 es hoy."""
    (pedido,) = [p for p in medir.PEDIDOS if p["nombre"] == "un apodo y un día de la semana"]
    assert "antes del jueves" in pedido["texto"]
    assert medir.HOY == date(2026, 10, 14)
    assert pedido["propone"]["fecha"] == "2026-10-14"


@pytest.mark.parametrize("falla", [KeyError("dato"), IndexError("lista"),
                                   FileNotFoundError("archivo")])
def test_un_error_del_programa_dentro_de_la_llamada_no_es_de_la_ia(medir, monkeypatch, tmp_path,
                                                                    falla):
    """La revisión `review-f7886a8a6481af78`: `LookupError` y `OSError` también son `KeyError`,
    `IndexError` o un archivo que falta; un error así es del programa, no de la IA."""
    ia = IADeLaCarga(falla)
    monkeypatch.setattr(medir, "la_ia", lambda texto: ia)
    salida = tmp_path / "informe.json"
    assert medir.main(["--ia", "x", "--salida", str(salida)]) == medir.ERROR_DEL_PROGRAMA
    informe = json.loads(salida.read_text(encoding="utf-8"))
    assert informe["resultados"][0]["falla"] == "programa"


@pytest.mark.parametrize("falla", [LookupError("sin configurar"), ConnectionError("red"),
                                   TimeoutError("plazo")])
def test_una_ia_sin_configurar_o_sin_red_si_es_de_la_ia(medir, monkeypatch, tmp_path, falla):
    ia = IADeLaCarga(falla, *([{}] * (2 * len(medir.PEDIDOS))))
    monkeypatch.setattr(medir, "la_ia", lambda texto: ia)
    salida = tmp_path / "informe.json"
    assert medir.main(["--ia", "x", "--salida", str(salida)]) == 1
    informe = json.loads(salida.read_text(encoding="utf-8"))
    assert informe["resultados"][0]["falla"] == "ia"


# --- J2-17: lo que Leda escribe, con sus palabras y bien escrito ----------------------------------
#
# La segunda prueba del usuario en el celular (2026-10-13): la propuesta del criterio "es muy
# rebuscada… parece sacada del código": la armaba una plantilla (`criterio_con_la_evidencia`). Lo
# decidido: la IA escribe con naturalidad todo lo que propone (el criterio entero, con la evidencia
# del área como dato); la plantilla queda sólo de reserva; "no sé" es un pedido de ayuda (Leda
# propone siempre, también sin evidencia del área); y la ortografía se corrige en todo, sin cambiar
# cómo está redactado, con el código comprobando que sólo cambió la ortografía.

PLANTILLA = "Se comprueba con lo que pide el área"
CRITERIO_NATURAL = ("El estante del módem queda colgado en la sala con los 12 tornillos de 8 mm, y "
                    "una foto lo muestra firme en su lugar.")
CRITERIO_NATURAL_UPS = ("El UPS de la sala de servidores queda cambiado y funcionando, y se ve "
                        "encendido en la sala de servidores.")


def _respuesta_natural(**cambios) -> dict[str, Any]:
    return _respuesta_del_ejemplo(**{"criterio": CRITERIO_NATURAL, **cambios})


def test_j2_17_el_criterio_lo_escribe_la_ia_entero(ayuda):
    resultado, ia = _proponer(ayuda, _respuesta_natural(evidencia="E1"))
    assert resultado.propuesta["criterio"] == CRITERIO_NATURAL
    datos = ia.pedidos[0]["tools"][0]["function"]["parameters"]["properties"]
    assert "criterio" in datos and "como_se_comprueba" not in datos
    (juicio,) = _juicios(ia)
    assert juicio["criterio"] == CRITERIO_NATURAL
    assert juicio["evidencia_que_pide_el_area"] == ["una foto"]


def test_j2_17_el_codigo_no_arma_ni_agrega_texto_cuando_la_ia_responde(ayuda):
    """Pedido del usuario: nada escrito con forma de código. Lo que propone la IA llega tal cual:
    el código no arma oraciones ni les pega una plantilla."""
    respuesta = _respuesta_natural()
    resultado, _ = _proponer(ayuda, respuesta)
    for campo in ("titulo", "descripcion", "criterio"):
        assert resultado.propuesta[campo] == respuesta[campo]
        assert PLANTILLA not in resultado.propuesta[campo]


def test_j2_17_la_plantilla_queda_de_reserva_si_el_juicio_no_responde(ayuda):
    resultado, _ = _proponer(ayuda, _respuesta_natural(evidencia="E1"),
                             juzga=lambda e: TimeoutError("plazo"))
    assert resultado.propuesta["criterio"] == ayuda.criterio_con_la_evidencia(
        RESULTADO_DEL_EJEMPLO, ["una foto"])
    assert {"campo": "criterio", "motivo": "sin_revisar"} in resultado.descartados
    assert resultado.criterio_de == "reserva"


def test_j2_17_si_el_criterio_de_la_ia_inventa_un_dato_propone_el_del_juicio(ayuda):
    def juzga(entrada):
        assert entrada["criterio"] == ""
        return {"dice_un_resultado": False, "resultado": RESULTADO_DEL_EJEMPLO,
                "criterio": CRITERIO_NATURAL}
    resultado, _ = _proponer(ayuda, _respuesta_natural(
        criterio="El estante queda colgado y Roberto lo revisa."), juzga=juzga)
    assert {"campo": "criterio", "motivo": "nombre"} in resultado.descartados
    assert resultado.propuesta["criterio"] == CRITERIO_NATURAL
    assert resultado.criterio_de == "juicio"


def test_j2_17_no_se_sin_evidencia_del_area_igual_propone(ayuda):
    """"No sé" es un pedido de ayuda: sin quién la hace (nadie es "el tano") no hay evidencia de un
    área, y Leda igual propone un criterio, juzgado por su sentido."""
    def juzga(entrada):
        assert "evidencia_que_pide_el_area" not in entrada
        return {"dice_como_se_comprueba": False, "como_se_comprueba": "",
                "criterio": CRITERIO_NATURAL_UPS}
    resultado, ia = _proponer(ayuda, {"titulo": TITULO_UPS, "criterio": "",
                                      "responsable": "el tano"},
                              texto=UPS, coinciden=_nadie, juzga=juzga)
    assert resultado.propuesta["criterio"] == CRITERIO_NATURAL_UPS
    assert "Contame cómo se sabe que está terminada." not in _avisos(resultado).values()
    assert len(_juicios(ia)) == 1


def test_j2_17_al_cargar_no_se_sin_evidencia_trae_un_criterio_propuesto(ayuda):
    ia = IADeLaCarga({"dice_como_se_comprueba": False, "como_se_comprueba": "",
                      "criterio": CRITERIO_NATURAL_UPS})
    juicio = ayuda.juzgar_el_criterio(ia, titulo=TITULO_UPS, descripcion="", criterio="No se")
    assert juicio.motivo == "sin_comprobacion" and juicio.propuesta == CRITERIO_NATURAL_UPS
    # Vacío o igual al título también: la IA se llama sólo para proponer.
    ia = IADeLaCarga({"dice_como_se_comprueba": True, "como_se_comprueba": "x",
                      "criterio": CRITERIO_NATURAL_UPS})
    juicio = ayuda.juzgar_el_criterio(ia, titulo=TITULO_UPS, descripcion="", criterio=TITULO_UPS)
    assert juicio.motivo == "sin_comprobacion" and juicio.propuesta == CRITERIO_NATURAL_UPS
    assert len(ia.pedidos) == 1


def test_j2_17_al_cargar_el_rechazo_con_evidencia_trae_el_criterio_de_la_ia(ayuda):
    ia = IADeLaCarga({"dice_un_resultado": False, "resultado": RESULTADO_PROPUESTO,
                      "criterio": CRITERIO_NATURAL_UPS})
    juicio = _con_evidencia(ayuda, ia, "No se")
    assert juicio.motivo == "sin_resultado" and juicio.propuesta == CRITERIO_NATURAL_UPS
    assert not juicio.de_reserva
    parametros = ia.pedidos[0]["tools"][0]["function"]["parameters"]
    assert "criterio" in parametros["properties"]


def test_j2_17_al_cargar_la_plantilla_es_de_reserva(ayuda):
    """Si el criterio que escribió la IA inventa un dato, vale el de reserva."""
    ia = IADeLaCarga({"dice_un_resultado": False, "resultado": RESULTADO_PROPUESTO,
                      "criterio": "Lo revisa Roberto."})
    juicio = _con_evidencia(ayuda, ia, "No se")
    assert juicio.propuesta == ayuda.criterio_con_la_evidencia(RESULTADO_PROPUESTO, [PRUEBA])
    assert juicio.de_reserva


def test_j2_17_las_instrucciones_piden_naturalidad_y_ortografia_sin_frases(ayuda):
    _, ia = _proponer(ayuda, _respuesta_natural())
    textos = " ".join([ia.instrucciones(0), ia.instrucciones(1),
                       json.dumps(ia.pedidos[0]["tools"], ensure_ascii=False),
                       json.dumps(ia.pedidos[1]["tools"], ensure_ascii=False)]).lower()
    assert "ortografía" in textos and "naturalidad" in textos
    for frase in ("se comprueba con", "foto", "estante", "ups", "una captura", "cómo se probó"):
        assert frase not in textos, frase


# La ortografía (J2-17, punto 4): Leda corrige lo que la persona escribió a mano, sin cambiar cómo
# está redactado; el código acepta la corrección sólo si cambió la ortografía palabra por palabra.

NOMBRES = ["Lucas Pérez", "Marcos Díaz", "Ismael Soschinski", "Integrar el PLC con CoreLabs"]


@pytest.mark.parametrize("original, corregido, cambios", [
    ("integrar el plc con cirelabs", "Integrar el PLC con CoreLabs",
     [("integrar", "Integrar"), ("plc", "PLC"), ("cirelabs", "CoreLabs")]),
    ("plantar el arvol de la entrada", "Plantar el árbol de la entrada",
     [("plantar", "Plantar"), ("arvol", "árbol")]),
    ("hay que aser la limpiesa", "Hay que hacer la limpieza",
     [("hay", "Hay"), ("aser", "hacer"), ("limpiesa", "limpieza")]),
    ("que lo haga ismael", "Que lo haga Ismael", [("que", "Que"), ("ismael", "Ismael")]),
    ("Todo bien escrito.", "Todo bien escrito.", []),
])
def test_j2_17_una_correccion_de_ortografia_se_acepta(ayuda, original, corregido, cambios):
    texto, hechos, rechazadas = ayuda.palabra_por_palabra(original, corregido, NOMBRES)
    assert [(c["antes"], c["despues"]) for c in hechos] == cambios
    assert texto == corregido and rechazadas == 0


@pytest.mark.parametrize("original, corregido", [
    ("colgar el estante", "instalar el estante"),              # otra palabra
    ("colgar el estante", "colgar el estante nuevo"),          # una palabra más
    ("colgar el estante rapido", "colgar el estante"),         # una palabra menos
    ("comprar 12 tornillos", "comprar 13 tornillos"),          # otro número
    ("que lo haga juan", "que lo haga Marcos"),                # otra persona
    ("el estante queda colgado", "queda colgado el estante"),  # otro orden
])
def test_j2_17_lo_que_no_es_ortografia_se_rechaza(ayuda, original, corregido):
    """J2-18: con otra cantidad de palabras no se puede comparar; con la misma, cada palabra que
    no es la misma mal escrita queda como la escribió la persona, y se cuenta."""
    hecho = ayuda.palabra_por_palabra(original, corregido, NOMBRES)
    if len(original.split()) != len(corregido.split()):
        assert hecho is None
    else:
        texto, cambios, rechazadas = hecho
        assert (texto, cambios) == (original, []) and rechazadas >= 1


def test_j2_17_la_correccion_respeta_los_renglones_de_la_persona(ayuda):
    texto, _, _ = ayuda.palabra_por_palabra("primero el arvol\nluego la sanja",
                                            "Primero el árbol. Luego la zanja.", NOMBRES)
    assert texto == "Primero el árbol\nLuego la zanja"


def test_j2_17_revisar_la_ortografia_separa_lo_corregido_de_lo_rechazado(ayuda):
    textos = {"titulo": "integrar el plc con cirelabs", "descripcion": "colgar el estante",
              "criterio": "todo bien"}
    crudo = {"titulo": "Integrar el PLC con CoreLabs", "descripcion": "instalar el estante"}
    opciones = {**OPCIONES, "objetivos": [
        *OPCIONES["objetivos"], {"id": "o-core", "titulo": "Integrar el PLC con CoreLabs"}]}
    r = ayuda.revisar_la_ortografia(crudo, textos, opciones)
    assert r.corregidos == {"titulo": {
        "texto": "Integrar el PLC con CoreLabs",
        "cambios": [{"antes": "integrar", "despues": "Integrar"},
                    {"antes": "plc", "despues": "PLC"},
                    {"antes": "cirelabs", "despues": "CoreLabs"}]}}
    # J2-18: "instalar" no es "colgar" mal escrito: queda como lo escribió la persona, y se cuenta.
    assert r.rechazados == [{"campo": "criterio", "motivo": "sin_respuesta"}]
    assert r.palabras_rechazadas == [{"campo": "descripcion", "cantidad": 1}]


def test_j2_17_la_ia_de_la_ortografia_recibe_los_nombres_del_equipo(ayuda):
    entrada = ayuda.entrada_de_la_ortografia({"titulo": "x"}, OPCIONES)
    assert entrada["textos"] == {"titulo": "x"}
    for nombre in ("Lucas Pérez", "Instalar el módem de la sala",
                   "Cablear el tablero de la máquina 3", "Infraestructura"):
        assert nombre in entrada["nombres"]
    herramienta = ayuda.herramienta_de_la_ortografia(["titulo"])
    assert set(herramienta["function"]["parameters"]["properties"]) == {"titulo"}
    for frase in ("cirelabs", "arvol", "corelabs"):
        assert frase not in ayuda.INSTRUCCIONES_DE_LA_ORTOGRAFIA.lower()


# --- J2-18: Leda completa todo lo que puede ---------------------------------------------------
#
# La ronda de la J2-17 (66 de 81): sin quién la hace, la IA inventaba una comprobación floja, porque
# proponía sin los datos de los que sale la comprobación. El usuario: "Leda debería en lo posible
# completar todos los campos; yo reviso y corrijo lo que quiera o lo dejo tal cual". Leda propone
# quién la hace por el trabajo y las áreas del equipo (aunque no se dijo), la evidencia que sirve
# para esta tarea además del mínimo del área, y el criterio dice cómo se comprueba con ella. Si la
# persona nombró a alguien que no es del equipo, se dice y no se reemplaza por otro.

PRUEBA_DE_LA_BATERIA = ("hay que cambiar la bateria del ups de la sala de servidores para el "
                        "viernes")


def _opciones_del_pack() -> dict[str, Any]:
    """Las opciones con la evidencia como en el pack: cada área pide un mínimo y conoce los tipos
    del pack (en `espacios/corework.yaml`, cinco; acá, cuatro)."""
    opciones = json.loads(json.dumps(OPCIONES))
    tipos = {"captura": {"clases": ["imagen"],
                         "en_palabras": "una foto o una captura de la pantalla"},
             "explicacion": {"clases": ["texto"],
                             "en_palabras": "cómo quedó el trabajo, descrito por quien lo hizo"},
             "foto": {"clases": ["imagen"], "en_palabras": "una foto"},
             "resultado_de_prueba": {"clases": ["texto"], "en_palabras": PRUEBA}}
    opciones["politicas"] = [
        {"area_id": "a-infra", "area": "Infraestructura", "evidencia_requerida": ["foto"],
         "version": 1, "tipos": tipos},
        {"area_id": "a-auto", "area": "Automatización", "evidencia_requerida": ["explicacion"],
         "version": 1, "tipos": {k: tipos[k] for k in ("captura", "explicacion")}},
    ]
    return opciones


def _de_la_bateria(**cambios) -> dict[str, Any]:
    respuesta = {"titulo": "Cambiar la batería del UPS de la sala de servidores",
                 "criterio": ("La batería del UPS de la sala de servidores queda cambiada, y la "
                              "prueba muestra que aguanta sin luz."),
                 "resultado": "La batería del UPS de la sala de servidores queda cambiada",
                 "quien_la_hace": "P1", "evidencia": "E4",
                 "fecha": VIERNES, "como_dijo_la_fecha": "para el viernes"}
    respuesta.update(cambios)
    return {k: v for k, v in respuesta.items() if v is not None}


def test_j2_18_la_ia_recibe_el_equipo_las_areas_y_la_evidencia_como_hechos(ayuda):
    _, ia = _proponer(ayuda, _de_la_bateria(), texto=PRUEBA_DE_LA_BATERIA,
                      opciones=_opciones_del_pack())
    entrada = ia.entrada()
    # Sólo quien puede hacerla: alguien a quien otro revisa (Ismael no tiene quién lo revise).
    assert entrada["equipo"] == [
        {"codigo": "P1", "nombre": "Lucas Pérez", "area": "Infraestructura"},
        {"codigo": "P2", "nombre": "Lucía Benítez", "area": "Automatización"},
        {"codigo": "P3", "nombre": "Marcos Díaz", "area": "Automatización"}]
    assert entrada["areas"] == [
        {"area": "Infraestructura", "evidencia_que_pide": ["una foto"]},
        {"area": "Automatización",
         "evidencia_que_pide": ["cómo quedó el trabajo, descrito por quien lo hizo"]}]
    assert entrada["tipos_de_evidencia"] == [
        {"codigo": "E1", "en_palabras": "una foto o una captura de la pantalla"},
        {"codigo": "E2", "en_palabras": "cómo quedó el trabajo, descrito por quien lo hizo"},
        {"codigo": "E3", "en_palabras": "una foto"},
        {"codigo": "E4", "en_palabras": PRUEBA}]
    assert "evidencia" in entrada["pide"]
    datos = ia.pedidos[0]["tools"][0]["function"]["parameters"]["properties"]
    assert {"responsable", "quien_la_hace", "evidencia"} <= set(datos)
    # Ningún id: la IA devuelve códigos y el código los busca.
    plano = json.dumps(entrada, ensure_ascii=False)
    for dato in ("m-lucas", "a-infra", "resultado_de_prueba", "ws-1"):
        assert dato not in plano


def test_j2_18_leda_propone_quien_la_hace_aunque_no_se_dijo(ayuda):
    resultado, ia = _proponer(ayuda, _de_la_bateria(), texto=PRUEBA_DE_LA_BATERIA,
                              opciones=_opciones_del_pack())
    assert resultado.propuesta["responsable_id"] == "m-lucas"
    assert resultado.responsable_de == "leda"
    assert "responsable" not in _avisos(resultado)
    # J2-19: la evidencia es la que propone Leda para esta tarea, sin el mínimo del área encima, y
    # el criterio se juzga con exactamente esa.
    assert resultado.propuesta["evidencia"] == ["resultado_de_prueba"]
    (juicio,) = _juicios(ia)
    assert juicio["evidencia_que_pide_el_area"] == [PRUEBA]
    assert resultado.propuesta["criterio"].startswith("La batería del UPS")


def test_j2_18_quien_se_nombro_gana_sobre_la_propuesta(ayuda):
    resultado, _ = _proponer(ayuda, _de_la_bateria(responsable="el tano"),
                             texto=f"{PRUEBA_DE_LA_BATERIA} que lo haga el tano",
                             opciones=_opciones_del_pack())
    assert resultado.propuesta["responsable_id"] == "m-marcos"
    assert resultado.responsable_de == "dicho"
    # La evidencia de Leda tiene que ser del área de Marcos: la prueba no la conoce.
    assert "evidencia" not in resultado.propuesta
    assert {"campo": "evidencia", "motivo": "no_es_del_area"} in resultado.descartados


def test_j2_18_alguien_que_no_es_del_equipo_no_se_reemplaza_por_otro(ayuda):
    """El usuario: si nombró a alguien que no está en el equipo, se dice en su campo y Leda no
    pone a otro."""
    resultado, ia = _proponer(ayuda, _de_la_bateria(responsable="pepe"),
                              texto=f"{PRUEBA_DE_LA_BATERIA} que lo haga pepe",
                              opciones=_opciones_del_pack())
    assert "responsable_id" not in resultado.propuesta
    assert _avisos(resultado)["responsable"] == (
        "No encontré a «pepe» en el equipo; elegí quién la hace.")
    assert resultado.responsable_de is None
    # Sin quién la hace no hay área de dónde salga la evidencia.
    assert "evidencia" not in resultado.propuesta
    assert "evidencia_que_pide_el_area" not in _juicios(ia)[0]


def test_j2_18_entre_dos_nombrados_leda_no_elige_ni_propone_otro(ayuda):
    def por_nombre(dicho):
        return _coinciden("lucas pérez") + _coinciden("lucía benítez")
    resultado, _ = _proponer(ayuda, _de_la_bateria(responsable="lucas"),
                             texto=f"{PRUEBA_DE_LA_BATERIA} lucas", coinciden=por_nombre,
                             opciones=_opciones_del_pack())
    assert "responsable_id" not in resultado.propuesta
    assert [e["membership_id"] for e in resultado.elegir] == ["m-lucas", "m-lucas-b"]


@pytest.mark.parametrize("codigo", ["P9", "P0", "Lucas", "m-lucas"])
def test_j2_18_un_codigo_que_no_es_del_equipo_no_se_propone(ayuda, codigo):
    resultado, _ = _proponer(ayuda, _de_la_bateria(quien_la_hace=codigo),
                             texto=PRUEBA_DE_LA_BATERIA, opciones=_opciones_del_pack())
    assert "responsable_id" not in resultado.propuesta
    assert {"campo": "responsable", "motivo": "no_existe"} in resultado.descartados


def test_j2_18_quien_ya_se_eligio_no_se_pide(ayuda):
    resultado, ia = _proponer(ayuda, _de_la_bateria(), texto=PRUEBA_DE_LA_BATERIA,
                              escrito=_vacio(responsable_id="m-lucas"),
                              opciones=_opciones_del_pack())
    assert "responsable_id" not in resultado.propuesta
    assert "quien_la_hace" not in ia.pedidos[0]["tools"][0]["function"]["parameters"][
        "properties"]
    assert resultado.propuesta["evidencia"] == ["resultado_de_prueba"]


@pytest.mark.parametrize("evidencia, propuesta, descartado", [
    ("E4", ["resultado_de_prueba"], None),
    ("E1, E4", ["captura", "resultado_de_prueba"], None),
    ("E3", ["foto"], None),                           # J2-19: la del área, si Leda la elige
    ("E4, E4", ["resultado_de_prueba"], None),
    ("E9", None, "no_existe"),
    ("una foto", None, "no_existe"),
    ("", None, None),
])
def test_j2_18_la_evidencia_que_propone_leda_es_de_los_tipos_del_area(ayuda, evidencia,
                                                                     propuesta, descartado):
    resultado, _ = _proponer(ayuda, _de_la_bateria(evidencia=evidencia),
                             texto=PRUEBA_DE_LA_BATERIA, opciones=_opciones_del_pack())
    assert resultado.propuesta.get("evidencia") == propuesta
    if descartado:
        assert {"campo": "evidencia", "motivo": descartado} in resultado.descartados


def test_j2_18_si_la_persona_ya_tildo_otra_evidencia_no_se_propone(ayuda):
    """Lo que la persona eligió es suyo: la IA lo recibe como dato y no propone otra."""
    escrito = {**_vacio(responsable_id="m-lucas"), "evidencia": ["foto", "captura"]}
    resultado, ia = _proponer(ayuda, _de_la_bateria(), texto=PRUEBA_DE_LA_BATERIA,
                              escrito=escrito, opciones=_opciones_del_pack())
    assert "evidencia" not in ia.entrada()["pide"]
    assert ia.entrada()["ya_escrito"]["evidencia_elegida"] == [
        "una foto", "una foto o una captura de la pantalla"]
    assert "evidencia" not in resultado.propuesta
    assert _juicios(ia)[0]["evidencia_que_pide_el_area"] == [
        "una foto", "una foto o una captura de la pantalla"]


def test_j2_18_sin_el_criterio_por_pedir_no_se_propone_evidencia(ayuda):
    resultado, ia = _proponer(ayuda, _de_la_bateria(), texto=PRUEBA_DE_LA_BATERIA,
                              escrito=_vacio(criterio="La batería queda cambiada."),
                              opciones=_opciones_del_pack())
    assert "evidencia" not in ia.entrada()["pide"]
    assert "evidencia" not in resultado.propuesta


def test_j2_18_sin_quien_la_hace_el_criterio_no_inventa_como_se_comprueba(ayuda):
    """Si Leda no puede saber quién la hace, el criterio dice qué tiene que quedar hecho y cómo se
    comprueba sólo si la persona lo dijo: el juicio, sin la evidencia de un área, escribe el suyo
    con esa misma regla (cómo se comprueba lo va a decir la evidencia de quien la haga)."""
    resultado, ia = _proponer(ayuda, _respuesta_del_ups(), texto=UPS, coinciden=_nadie,
                              juzga=juez(CIRCULAR_UPS, propone=RESULTADO_UPS + "."))
    assert resultado.propuesta["criterio"] == RESULTADO_UPS + "."
    assert ia.instrucciones(1) == ayuda.INSTRUCCIONES_DEL_JUICIO_SIN_QUIEN
    assert ia.instrucciones(1) != ayuda.INSTRUCCIONES_DEL_JUICIO
    # Al cargar, sin evidencia del área, sigue la regla de siempre.
    juicio_ia = IADeLaCarga(NO_LO_DICE)
    ayuda.juzgar_el_criterio(juicio_ia, titulo=TITULO_UPS, descripcion="", criterio="No se")
    assert juicio_ia.instrucciones() == ayuda.INSTRUCCIONES_DEL_JUICIO
    assert "lo que la tarea misma deja ver" not in ayuda.INSTRUCCIONES


def test_j2_18_un_nombre_de_los_datos_mal_escrito_se_propone_como_esta_en_los_datos(ayuda):
    """"cirelabs" es CoreLabs: la IA lo escribe como está en los datos, y el código lo deja pasar
    porque es la misma palabra mal escrita, no un nombre inventado."""
    opciones = json.loads(json.dumps(OPCIONES))
    opciones["objetivos"].append({"id": "o-core", "titulo": "Integrar el PLC con CoreLabs",
                                  "tipo": "operativo", "estado": "activo",
                                  "fecha_objetivo": None})
    texto = "hay q integrar el plc de la fette con cirelabs"
    resultado, _ = _proponer(ayuda, {"titulo": "Integrar el PLC de la Fette con CoreLabs",
                                     "descripcion": "Integrar el PLC de la Fette con CoreLabs.",
                                     "criterio": ("El PLC de la Fette queda integrado con "
                                                  "CoreLabs.")},
                             texto=texto, opciones=opciones)
    assert resultado.propuesta["titulo"] == "Integrar el PLC de la Fette con CoreLabs"
    assert resultado.propuesta["descripcion"] == "Integrar el PLC de la Fette con CoreLabs."
    # Un nombre que no se parece a nada de lo que escribió la persona sigue sin pasar.
    resultado, _ = _proponer(ayuda, {"titulo": "Integrar el PLC con Siemens"}, texto=texto,
                             opciones=opciones)
    assert "titulo" not in resultado.propuesta


def test_j2_18_las_instrucciones_describen_el_trabajo_sin_frases_ni_casos(ayuda):
    _, ia = _proponer(ayuda, _de_la_bateria(), texto=PRUEBA_DE_LA_BATERIA,
                      opciones=_opciones_del_pack())
    textos = " ".join([ia.instrucciones(0),
                       json.dumps(ia.pedidos[0]["tools"], ensure_ascii=False),
                       ayuda.INSTRUCCIONES_DEL_JUICIO_SIN_QUIEN]).lower()
    assert "equipo" in textos and "evidencia" in textos and "ortografía" in textos
    for frase in ("batería", "ups", "lucas", "foto", "captura", "cirelabs", "corelabs", "pepe"):
        assert frase not in textos, frase


# --- J2-19: en la evidencia, tildado sólo lo que propone Leda --------------------------------
#
# La prueba en el celular de la J2-18: al elegir a quien la hace quedaban tildados todos los tipos
# que pide su área más el que propuso Leda. El usuario: "debería quedar sólo tildado lo que Leda
# propone; si la persona lo quiere modificar, lo hace". La lista del área es un dato que Leda tiene
# en cuenta, no un mínimo: la propuesta es el conjunto que eligió Leda, y lo que la persona tildó
# (cualquier tipo, también uno de los que pide el área) es suyo.

def test_j2_19_la_persona_que_tildo_lo_que_pide_el_area_eligio_ella(ayuda):
    """Nada se tilda solo: si llegó un tipo tildado, lo tildó la persona (o lo aceptó de Leda), y
    Leda no propone encima, aunque sea justo el que pide el área."""
    escrito = {**_vacio(responsable_id="m-lucas"), "evidencia": ["foto"]}
    resultado, ia = _proponer(ayuda, _de_la_bateria(), texto=PRUEBA_DE_LA_BATERIA,
                              escrito=escrito, opciones=_opciones_del_pack())
    assert "evidencia" not in ia.entrada()["pide"]
    assert "evidencia" not in resultado.propuesta
    assert _juicios(ia)[0]["evidencia_que_pide_el_area"] == ["una foto"]


def test_j2_19_sin_evidencia_propuesta_ni_tildada_el_criterio_se_juzga_sin_ella(ayuda):
    """Lo que se juzga es lo que va a quedar tildado: si Leda no propone ninguna y la persona no
    tildó nada, el criterio tiene que decir cómo se comprueba (el área no pone la suya sola)."""
    resultado, ia = _proponer(ayuda, _de_la_bateria(evidencia=""), texto=PRUEBA_DE_LA_BATERIA,
                              opciones=_opciones_del_pack())
    assert "evidencia" not in resultado.propuesta
    assert "evidencia_que_pide_el_area" not in _juicios(ia)[0]


def test_j2_19_las_instrucciones_dicen_que_lo_del_area_es_un_dato_y_sin_repetir(ayuda):
    """La regla del mozo: las instrucciones describen el trabajo (la lista del área es un dato,
    no un mínimo; sin dos tipos que digan lo mismo), sin casos ni tipos del pack."""
    texto = " ".join([ayuda.INSTRUCCIONES, ayuda._DATOS["evidencia"]]).lower()
    assert "mínimo" not in texto and "va siempre" not in texto
    assert "lo mismo" in texto
    assert "además de los que pide el área" not in texto


@pytest.mark.parametrize("texto", [
    "hay que pintar las marcas del piso",      # "marcas" no es Marcos
    "hay que revisar el modelo de la sala",    # "modelo" no es "módem"
])
def test_j2_19_una_palabra_comun_no_habilita_un_nombre_de_los_datos(ayuda, texto):
    """`nombres_mal_escritos` (advertencia de RDD de la J2-18): sólo la misma palabra mal escrita
    (letras de más, de menos, dadas vuelta o que se confunden en el teclado o al oído) habilita el
    nombre de los datos; una palabra común con otra letra cualquiera es otra palabra."""
    assert ayuda.nombres_mal_escritos(texto, OPCIONES) == []


def test_j2_19_una_palabra_que_ya_es_un_nombre_no_habilita_otro(ayuda):
    """Quien escribió bien un nombre de los datos no escribió mal otro parecido."""
    opciones = json.loads(json.dumps(OPCIONES))
    opciones["integrantes"].append({**opciones["integrantes"][0], "membership_id": "m-lucio",
                                    "nombre": "Lucio Pereda"})
    assert "Lucio" not in ayuda.nombres_mal_escritos("que lo haga lucas", opciones)


def test_j2_19_el_nombre_mal_escrito_sigue_valiendo(ayuda):
    opciones = json.loads(json.dumps(OPCIONES))
    opciones["objetivos"].append({"id": "o-core", "titulo": "Integrar el PLC con CoreLabs"})
    assert ayuda.nombres_mal_escritos("integrar con cirelabs", opciones) == ["CoreLabs"]


# --- La ortografía palabra por palabra (J2-18) ------------------------------------------------
#
# La ronda de la J2-17: con "q" (una abreviatura de chat) la corrección del campo entero se
# rechazaba y "bateria" quedaba sin tilde. Ahora cada palabra que pasa el control se corrige y la
# que no queda como la escribió la persona; el incidente cuenta sólo las rechazadas.

def test_j2_18_la_ortografia_se_acepta_palabra_por_palabra(ayuda):
    texto, cambios, rechazadas = ayuda.palabra_por_palabra(
        "cambiar la bateria del ups q no anda", "Cambiar la batería del UPS que no anda", NOMBRES)
    assert texto == "Cambiar la batería del UPS q no anda"
    assert [(c["antes"], c["despues"]) for c in cambios] == [
        ("cambiar", "Cambiar"), ("bateria", "batería"), ("ups", "UPS")]
    assert rechazadas == 1


def test_j2_18_con_otra_cantidad_de_palabras_no_se_puede_comparar(ayuda):
    assert ayuda.palabra_por_palabra("colgar el estante", "colgar el estante nuevo",
                                     NOMBRES) is None


def test_j2_18_revisar_la_ortografia_corrige_lo_que_pasa_y_cuenta_lo_que_no(ayuda):
    r = ayuda.revisar_la_ortografia({"titulo": "Cambiar la batería del UPS que no anda",
                                     "descripcion": "instalar el estante"},
                                    {"titulo": "cambiar la bateria del ups q no anda",
                                     "descripcion": "colgar el estante"}, OPCIONES)
    assert r.corregidos["titulo"]["texto"] == "Cambiar la batería del UPS q no anda"
    assert "descripcion" not in r.corregidos
    assert r.rechazados == []
    assert r.palabras_rechazadas == [{"campo": "titulo", "cantidad": 1},
                                     {"campo": "descripcion", "cantidad": 1}]


@pytest.mark.parametrize("antes, despues", [
    ("arvol", "árbol"), ("limpiesa", "limpieza"), ("aser", "hacer"),       # suenan igual
    ("tablreo", "tablero"), ("trabjo", "trabajo"), ("tsblero", "tablero"),  # un dedo
    ("bateria", "batería"), ("ups", "UPS"),
    ("cirelabs", "CoreLabs"),                                              # un nombre de los datos
])
def test_j2_18_la_misma_palabra_mal_escrita_se_corrige(ayuda, antes, despues):
    assert ayuda._misma_palabra(antes, despues, {"corelabs"})


@pytest.mark.parametrize("antes, despues", [
    ("mesa", "masa"), ("cosa", "casa"), ("pelo", "peso"), ("pase", "pose"),  # otra palabra
    ("a", "ha"), ("e", "he"), ("o", "ho"),                                   # otra palabra corta
    ("q", "que"), ("xq", "porque"),                                          # abreviaturas
    ("12", "13"),
])
def test_j2_18_otra_palabra_no_es_una_falta(ayuda, antes, despues):
    assert not ayuda._misma_palabra(antes, despues, {"corelabs"})


# La prueba en el celular de la J2-18 (2026-10-13, 21:19): "cirelabs" y CoreLabs, en las dos
# direcciones. La de la persona se corrige al nombre de los datos; el nombre de los datos nunca se
# cambia por su forma mal escrita (la regla de la misma palabra era simétrica).
OBJETIVO_STEIGEN = "Vincular los equipos y máquinas de Steigen con CoreLabs"


def test_j2_19_cirelabs_se_corrige_a_corelabs_en_el_titulo(ayuda):
    opciones = {**OPCIONES, "objetivos": [*OPCIONES["objetivos"],
                                         {"id": "o-steigen", "titulo": OBJETIVO_STEIGEN}]}
    r = ayuda.revisar_la_ortografia({"titulo": "Integrar la paila 3 a CoreLabs"},
                                    {"titulo": "Integrar la paila 3 a cirelabs"}, opciones)
    assert r.corregidos["titulo"] == {"texto": "Integrar la paila 3 a CoreLabs",
                                      "cambios": [{"antes": "cirelabs", "despues": "CoreLabs"}]}


def test_j2_19_corelabs_no_se_cambia_por_cirelabs(ayuda):
    opciones = {**OPCIONES, "objetivos": [*OPCIONES["objetivos"],
                                         {"id": "o-steigen", "titulo": OBJETIVO_STEIGEN}]}
    r = ayuda.revisar_la_ortografia({"titulo": "Integrar la paila 3 a cirelabs"},
                                    {"titulo": "Integrar la paila 3 a CoreLabs"}, opciones)
    assert "titulo" not in r.corregidos
    assert r.palabras_rechazadas == [{"campo": "titulo", "cantidad": 1}]
    assert not ayuda._misma_palabra("CoreLabs", "cirelabs", {"corelabs"})
    assert ayuda._misma_palabra("corelabs", "CoreLabs", {"corelabs"})


# --- J2-22: cómo se comprueba, desde quien hace la tarea -----------------------------------------
#
# El usuario (2026-10-13) rechazó un criterio que contaba la comprobación desde quien revisa, como
# algo que se "puede ver", y prefirió el que dice qué hace y qué entrega quien la hace. La regla del
# mozo: va como parte de la descripción del trabajo, sin frases de ejemplo ni listas de palabras.

def test_j2_22_las_instrucciones_piden_la_comprobacion_desde_quien_la_hace(ayuda):
    textos = {
        "la propuesta": ayuda.INSTRUCCIONES + ayuda._DATOS["criterio"],
        "el juicio": ayuda.INSTRUCCIONES_DEL_JUICIO,
        "el juicio sin quién": ayuda.INSTRUCCIONES_DEL_JUICIO_SIN_QUIEN,
        "el resultado": ayuda.INSTRUCCIONES_DEL_RESULTADO,
        "el criterio del juicio": ayuda._CRITERIO_DE_LEDA["description"],
    }
    for donde, texto in textos.items():
        plano = " ".join(texto.lower().split())
        assert "desde quien hace la tarea" in plano, donde
        assert "qué hace y qué entrega" in plano, donde
        assert "cómo sabe quien la revise" not in plano, donde
    # Corto: sólo con la evidencia propuesta (J2-19).
    assert "y sólo con esa" in " ".join(ayuda.INSTRUCCIONES.split())


@pytest.mark.parametrize("criterio, marcado", [
    ("Quien revise la tarea puede ver cómo quedó el trabajo.", True),
    ("El estante queda colgado y quienes lo revisan lo encuentran firme.", True),
    ("El revisor confirma que suenan las alarmas.", True),
    ("Marcos describe cómo quedó y cómo lo probó, con el resultado de la prueba.", False),
    ("El cartel queda pintado y se ve terminado.", False),     # "se ve": no se distingue
])
def test_j2_22_la_medicion_marca_el_criterio_contado_desde_quien_revisa(medir, criterio, marcado):
    assert bool(medir.desde_quien_revisa(criterio)) is marcado


def test_j2_22_la_medicion_hace_fallar_la_propuesta_desde_quien_revisa(medir):
    (no_se,) = [p for p in medir.PEDIDOS if p["nombre"] == "no se"]
    estante = {"dice_un_resultado": False, "resultado": "El estante queda colocado",
               "criterio": "El estante queda colocado y quien lo revisa lo ve terminado."}
    ok, detalle = medir.medir(IADeLaCarga(estante), no_se)
    assert ok is False
    assert detalle["desde_quien_revisa"] == ["quien lo revisa"]


# --- Advertencia de RDD de la J2-19: quién la hace y su área, con una sola búsqueda --------------

def test_quien_y_su_politica_es_la_misma_busqueda_que_la_propuesta(ayuda):
    integrante, politica = ayuda.quien_y_su_politica(OPCIONES, "m-lucas")
    assert integrante["nombre"] == "Lucas Pérez" and politica["area_id"] == "a-infra"
    assert ayuda.quien_y_su_politica(OPCIONES, "m-marcos")[1] is None    # su área no tiene
    assert ayuda.quien_y_su_politica(OPCIONES, None) == (None, None)
    assert ayuda.quien_y_su_politica(OPCIONES, "m-de-otro-espacio") == (None, None)


def test_un_integrante_sin_area_no_toma_la_politica_de_nadie(ayuda):
    """Sin área no hay política: nunca la primera que tampoco dice su área."""
    opciones = {**OPCIONES,
                "integrantes": [{**OPCIONES["integrantes"][0], "area_id": None}],
                "politicas": [{**OPCIONES["politicas"][0], "area_id": None}]}
    assert ayuda.quien_y_su_politica(opciones, "m-lucas")[1] is None
    assert ayuda.evidencia_de_la_carga(opciones, "m-lucas", ["foto"]) == []
