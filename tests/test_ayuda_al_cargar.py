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
        "criterio": "El estante del módem está colgado en la sala con los 12 tornillos de 8 mm.",
        "como_se_comprueba": "está colgado en la sala",
        "responsable": "lucas",
        "espera": "T1",
        "objetivo": "O2",
        "fecha": VIERNES,
        "como_dijo_la_fecha": "para el viernes",
    }
    respuesta.update(cambios)
    return {k: v for k, v in respuesta.items() if v is not None}


class IADeLaCarga:
    """Una IA de mentira con el contrato de `ia_real.IAReal` que usa la ayuda (`cliente.completar`):
    devuelve lo preparado, en orden, como la llamada a la herramienta; una excepción se levanta,
    como una IA que no responde. Guarda cada pedido."""

    nombre = "de-mentira"

    def __init__(self, *respuestas: Any) -> None:
        self.respuestas = list(respuestas)
        self.pedidos: list[dict[str, Any]] = []
        self.cliente = self
        self.al_llamar = None

    def completar(self, cuerpo: dict[str, Any], al_avanzar=None) -> dict[str, Any]:
        self.pedidos.append(cuerpo)
        if self.al_llamar is not None:
            self.al_llamar()
        r = self.respuestas.pop(0)
        if isinstance(r, BaseException):
            raise r
        if isinstance(r, dict) and "choices" in r:
            return r
        return {"choices": [{"finish_reason": "tool_calls", "message": {"tool_calls": [
            {"function": {"name": "proponer_la_carga", "arguments": json.dumps(r)}}]}}]}

    def entrada(self, i: int = -1) -> dict[str, Any]:
        """Lo que recibió la IA en el pedido `i`: el mensaje de la persona, en JSON."""
        mensajes = self.pedidos[i]["messages"]
        return json.loads(next(m["content"] for m in mensajes if m["role"] == "user"))

    def instrucciones(self, i: int = -1) -> str:
        return next(m["content"] for m in self.pedidos[i]["messages"] if m["role"] == "system")


@pytest.fixture
def ayuda():
    return importlib.import_module("leda.ayuda_al_cargar")


def _proponer(ayuda, respuesta: dict[str, Any], *, texto: str = EJEMPLO, escrito=None,
              coinciden=_coinciden, objetivo_de=_objetivo_de):
    escrito = escrito if escrito is not None else _vacio()
    ia = IADeLaCarga(respuesta)
    entrada = ayuda.entrada_de_la_ia(texto, escrito, OPCIONES)
    crudo = ayuda.pedir(ia, entrada)
    resultado = ayuda.revisar(crudo, texto=texto, escrito=escrito, opciones=OPCIONES,
                              coinciden=coinciden, objetivo_de=objetivo_de)
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
        "criterio": "El estante del módem está colgado en la sala con los 12 tornillos de 8 mm.",
        "responsable_id": "m-lucas",
        "espera_id": "t-tablero",
        # El de la tarea que espera, aunque la IA eligiera otro.
        "objetivo_id": "o-modem",
        "fecha": VIERNES,
    }
    assert resultado.avisos == [] and resultado.elegir == []
    assert ia.pedidos[0]["tools"][0]["function"]["name"] == "proponer_la_carga"


def test_la_ia_recibe_lo_del_espacio_con_codigos_y_sin_los_nombres_del_equipo(ayuda):
    _, ia = _proponer(ayuda, _respuesta_del_ejemplo())
    entrada = ia.entrada()
    assert entrada["texto"] == EJEMPLO
    assert set(entrada["pide"]) == {"titulo", "descripcion", "criterio", "responsable", "espera",
                                    "objetivo", "fecha"}
    assert [o["codigo"] for o in entrada["objetivos"]] == ["O1", "O2"]
    assert entrada["tareas_abiertas"][0]["codigo"] == "T1"
    assert entrada["tareas_abiertas"][0]["titulo"] == "Cablear el tablero de la máquina 3"
    assert any(d.startswith(f"{VIERNES}: viernes 16 de octubre") for d in entrada["dias"])
    assert entrada["dias"][0].startswith(f"{HOY.isoformat()}: miércoles 14 de octubre, hoy")
    plano = json.dumps(entrada, ensure_ascii=False)
    # Ningún id ni el nombre de un integrante que nadie eligió: la IA devuelve las palabras.
    for dato in ("m-lucas", "o-modem", "t-tablero", "Lucas Pérez", "Lucía Benítez", "ws-1"):
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
    cambios = {campo: valor}
    if campo == "criterio":
        cambios["como_se_comprueba"] = "está colgado"
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
        criterio="Lucas Pérez colgó el estante en la sala, después del tablero de la máquina 3.",
        como_se_comprueba="colgó el estante en la sala"))
    assert resultado.propuesta["criterio"].startswith("Lucas Pérez colgó")


@pytest.mark.parametrize("como", ["", "lo revisa alguien", None])
def test_un_criterio_que_no_dice_como_se_comprueba_no_se_propone(ayuda, como):
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(como_se_comprueba=como))
    assert "criterio" not in resultado.propuesta
    assert _avisos(resultado)["criterio"] == (
        "No pude proponer el criterio con lo que escribiste; contame cómo se comprueba.")
    assert {"campo": "criterio", "motivo": "sin_comprobacion"} in resultado.descartados


def test_los_topes_del_formulario(ayuda):
    largo = "Colgar el estante " + "muy " * 60
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(
        titulo=largo, criterio="Está colgado. " * 40, como_se_comprueba="Está colgado"))
    assert "titulo" not in resultado.propuesta and "criterio" not in resultado.propuesta
    assert {"campo": "titulo", "motivo": "largo"} in resultado.descartados
    assert {"campo": "criterio", "motivo": "largo"} in resultado.descartados


def test_lo_que_la_ia_deja_vacio_se_dice(ayuda):
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(titulo="", criterio=None,
                                                           como_se_comprueba=None))
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
    assert _avisos(resultado)["responsable"] == "No encontré a pepe en el equipo."


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
    assert _avisos(resultado)["responsable"] == "No encontré a lucas en el equipo."


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
    ("antes del jueves", "antes del jueves", "2026-10-15"),
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
    ("el 5-1", "5-1", "2027-01-05"),
    ("el 22/10/2026", "22/10/2026", "2026-10-22"),
    ("el 3 de noviembre", "el 3 de noviembre", "2026-11-03"),
    ("el viernes 23", "el viernes 23", "2026-10-23"),
])
def test_el_codigo_calcula_el_dia_de_las_palabras(ayuda, texto, dicho, fecha):
    assert ayuda.fecha_dicha(texto, dicho, HOY) == (date.fromisoformat(fecha), None)


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
])
def test_lo_que_no_es_un_dia_no_se_calcula(ayuda, texto, dicho, motivo):
    assert ayuda.fecha_dicha(texto, dicho, HOY) == (None, motivo)


def test_una_fecha_mal_escrita_no_se_pone(ayuda):
    resultado, _ = _proponer(ayuda, _respuesta_del_ejemplo(fecha="16/10"))
    assert "fecha" not in resultado.propuesta and "fecha" in _avisos(resultado)


def test_la_herramienta_pide_las_palabras_de_la_fecha_solo_con_la_fecha(ayuda):
    def datos(pide):
        return set(ayuda.herramienta(pide)["function"]["parameters"]["properties"])
    assert {"fecha", "como_dijo_la_fecha"} <= datos(["titulo", "fecha"])
    assert "como_dijo_la_fecha" not in datos(["titulo"])


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
    ia = IADeLaCarga({}, _SinCupo())
    monkeypatch.setattr(medir, "la_ia", lambda texto: ia)
    salida = tmp_path / "informe.json"
    assert medir.main(["--ia", "x", "--salida", str(salida)]) == medir.SIN_CUPO
    informe = json.loads(salida.read_text(encoding="utf-8"))
    assert informe["cortada"] == "sin_cupo"
    assert [r["pedido"] for r in informe["resultados"]] == [medir.PEDIDOS[0]["nombre"]]


def test_una_falla_de_la_ia_no_es_un_error_del_programa(medir, monkeypatch, tmp_path):
    from leda.motor.ia_real import PlazoAgotado, RespuestaInvalida

    ia = IADeLaCarga(RespuestaInvalida("x"), PlazoAgotado(40),
                     *([{}] * (len(medir.PEDIDOS) - 2)))
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
    """La IA en seco propone lo esperado para el ejemplo del usuario y un sábado: el ejemplo
    pasa entero y el sábado no pone la fecha; los demás, sin guion, no proponen nada."""
    salida = tmp_path / "informe.json"
    assert medir.main(["--salida", str(salida)]) == 1
    informe = json.loads(salida.read_text(encoding="utf-8"))
    bien = {r["pedido"] for r in informe["resultados"] if r["bien"]}
    assert bien == {"el ejemplo del usuario", "un sábado no es hábil"}
    (sabado,) = [r for r in informe["resultados"] if r["pedido"] == "un sábado no es hábil"]
    assert {"campo": "fecha", "motivo": "no_es_habil"} in sabado["descartados"]
    assert f"2 de {len(medir.PEDIDOS)} bien" in capsys.readouterr().out
