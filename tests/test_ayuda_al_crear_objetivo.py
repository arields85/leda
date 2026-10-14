"""La ayuda de la IA al crear un objetivo (porción J3, tarea J3-4 de
`odd/tasks/plataforma-jerarquias.md`; ADR 0023, punto 4): la lógica pura, sin base y con una IA de
mentira (nunca la real).

Lo que se prueba es la regla del mozo: la IA propone el nombre, la descripción, de qué cuelga, el
tipo, las palabras con que se nombró al referente y la fecha; el código decide qué vale. El
referente, sólo entre los referentes de área (decisión 3 del usuario, 2026-10-14) y sólo si sus
palabras están en el texto; con dos, la persona elige; con nadie, se dice. De qué cuelga, de la
lista; el tipo, uno que admita ese lugar. La fecha, sólo si se dijo, calculada por el código y en
día hábil (aunque venza después que el padre: el freno de la J3-3b lo dice en el formulario). El
nombre y la descripción, sin un número ni un nombre que nadie dijo, y con sus topes.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any

import pytest

from leda import ayuda_al_crear_objetivo as ayuda
from leda.motor.fichas import palabras
from tests.test_ayuda_al_cargar import IADeLaCarga

HOY = date(2026, 10, 14)          # miércoles


def _habiles(desde: date, dias: int = 120) -> list[str]:
    return [(desde + timedelta(days=n)).isoformat() for n in range(dias)
            if (desde + timedelta(days=n)).weekday() < 5]


OPCIONES: dict[str, Any] = {
    "espacio": {"id": "ws-1", "nombre": "CoreWork", "zona_horaria": "America/Argentina/Buenos_Aires"},
    "hoy": HOY.isoformat(),
    "niveles": {"estrategico": "objetivo estratégico", "hito": "hito",
                "operativo": "objetivo operativo"},
    "sin_padre": ["estrategico"],
    # Como los ordena la base: por su nombre.
    "padres": [
        {"id": "o-planta", "titulo": "Abrir la planta nueva", "tipo": "estrategico",
         "estado": "activo", "fecha_objetivo": "2026-12-18", "padre_id": None,
         "tipos": ["hito", "operativo"]},
        {"id": "o-linea", "titulo": "Arrancar la línea 3", "tipo": "hito", "estado": "activo",
         "fecha_objetivo": "2026-11-27", "padre_id": "o-planta", "tipos": ["operativo"]},
    ],
    "referentes": [
        {"membership_id": "m-ismael", "nombre": "Ismael Soschinski", "areas": ["Dirección"]},
        {"membership_id": "m-lucas", "nombre": "Lucas Pérez", "areas": ["Infraestructura"]},
        {"membership_id": "m-nahuel", "nombre": "Nahuel Gómez", "areas": ["Calidad"]},
    ],
    "calendario": {"dias": ["lunes", "martes", "miercoles", "jueves", "viernes"],
                   "hasta": "2027-10-14", "feriados": [], "dias_habiles": _habiles(HOY)},
}

# El equipo entero, para buscar a quien se nombró: Marcos no es referente de ningún área.
EQUIPO = [("m-ismael", "Ismael Soschinski"), ("m-lucas", "Lucas Pérez"),
          ("m-nahuel", "Nahuel Gómez"), ("m-marcos", "Marcos Díaz")]
APODOS = {"m-lucas": ["el ruso"], "m-nahuel": ["el ruso"], "m-marcos": ["el tano"]}

EJEMPLO = ("hay q dejar la sala de servidores ordenada con el modem colgado en la pared, q lo "
           "lleve lucas, para el viernes")


def _coinciden(dicho: str) -> list[dict[str, Any]]:
    """Como `fichas.integrantes_que_coinciden`: todas las palabras de lo dicho en el nombre o en
    un apodo."""
    buscadas = set(palabras(dicho))
    if not buscadas:
        return []
    return [{"membership_id": m, "nombre": n} for m, n in EQUIPO
            if buscadas <= set(palabras(n))
            or any(buscadas <= set(a.split()) for a in APODOS.get(m, []))]


def _vacio(**cambios) -> dict[str, Any]:
    escrito = {"titulo": "", "descripcion": "", "padre_id": "", "tipo": "", "referente_id": "",
               "fecha": ""}
    escrito.update(cambios)
    return escrito


def _respuesta(**cambios) -> dict[str, Any]:
    respuesta = {"titulo": "Ordenar la sala de servidores",
                 "descripcion": ("Dejar la sala de servidores ordenada, con el módem colgado en "
                                 "la pared."),
                 "padre": "", "tipo": "estrategico", "referente": "lucas",
                 "fecha": "2026-10-16", "como_dijo_la_fecha": "para el viernes"}
    respuesta.update(cambios)
    return {k: v for k, v in respuesta.items() if v is not None}


def _revisar(crudo: dict[str, Any], *, texto: str = EJEMPLO, escrito=None,
             opciones=None) -> ayuda.Resultado:
    return ayuda.revisar(crudo, texto=texto, escrito=escrito or _vacio(),
                         opciones=opciones or OPCIONES, coinciden=_coinciden)


# --- Lo que se pide y lo que recibe la IA ------------------------------------------------------

def test_se_pide_solo_lo_vacio():
    assert ayuda.lo_que_se_pide(_vacio(), OPCIONES) == [
        "titulo", "descripcion", "padre_id", "tipo", "referente_id", "fecha"]
    assert ayuda.lo_que_se_pide(_vacio(titulo="Ordenar la sala", referente_id="m-lucas"),
                                OPCIONES) == ["descripcion", "padre_id", "tipo", "fecha"]
    # Sin objetivos de los que colgar, de qué cuelga no se pide.
    assert "padre_id" not in ayuda.lo_que_se_pide(_vacio(), {**OPCIONES, "padres": []})


def test_la_ia_recibe_codigos_y_nunca_un_id():
    entrada = ayuda.entrada_de_la_ia(EJEMPLO, _vacio(), OPCIONES)
    assert entrada["texto"] == EJEMPLO
    assert entrada["pide"] == ["titulo", "descripcion", "padre", "tipo", "referente", "fecha"]
    assert [p["codigo"] for p in entrada["objetivos"]] == ["P1", "P2"]
    assert entrada["objetivos"][0]["titulo"] == "Abrir la planta nueva"
    assert entrada["objetivos"][0]["debajo_puede_ir"] == ["hito", "operativo"]
    assert entrada["tipos"] == [
        {"codigo": "estrategico", "nombre": "objetivo estratégico"},
        {"codigo": "hito", "nombre": "hito"}, {"codigo": "operativo", "nombre": "objetivo operativo"}]
    assert entrada["sin_padre"] == ["estrategico"]
    assert {r["nombre"] for r in entrada["referentes"]} == {
        "Ismael Soschinski", "Lucas Pérez", "Nahuel Gómez"}
    assert entrada["hoy"].startswith("2026-10-14")
    plano = json.dumps(entrada, ensure_ascii=False)
    for id_ in ("o-planta", "o-linea", "m-lucas", "ws-1"):
        assert id_ not in plano


def test_lo_ya_escrito_va_como_hecho_y_no_se_pide():
    entrada = ayuda.entrada_de_la_ia(EJEMPLO, _vacio(padre_id="o-linea", referente_id="m-nahuel",
                                                     fecha="2026-10-23"), OPCIONES)
    assert entrada["ya_escrito"]["de_que_cuelga"] == "Arrancar la línea 3"
    assert entrada["ya_escrito"]["referente"] == "Nahuel Gómez"
    assert entrada["ya_escrito"]["fecha"].startswith("2026-10-23")
    assert "padre" not in entrada["pide"] and "referente" not in entrada["pide"]


def test_la_herramienta_lleva_solo_lo_que_se_pide():
    propiedades = ayuda.herramienta(["titulo", "fecha"])["function"]["parameters"]["properties"]
    assert set(propiedades) == {"titulo", "fecha", "como_dijo_la_fecha"}
    assert ayuda.herramienta([])["function"]["name"] == "proponer_el_objetivo"


def test_las_instrucciones_describen_el_trabajo_sin_casos():
    # Sin frases de ejemplo entre comillas ni listas de casos.
    for marca in ('"', "«", "por ejemplo", "Ejemplo"):
        assert marca not in ayuda.INSTRUCCIONES


def test_pedir_hace_una_sola_llamada_con_la_herramienta():
    ia = IADeLaCarga(_respuesta())
    crudo = ayuda.pedir(ia, ayuda.entrada_de_la_ia(EJEMPLO, _vacio(), OPCIONES))
    assert crudo["referente"] == "lucas"
    assert len(ia.pedidos) == 1
    assert ia.pedidos[0]["tools"][0]["function"]["name"] == "proponer_el_objetivo"
    assert ia.pedidos[0]["temperature"] == 0


def test_una_ia_sin_configurar_no_responde():
    class SinCliente:
        cliente = None
        motivo = "No hay modelo."

    with pytest.raises(LookupError):
        ayuda.pedir(SinCliente(), {"pide": []})


# --- Lo que decide el código --------------------------------------------------------------------

def test_el_ejemplo_propone_cada_dato():
    r = _revisar(_respuesta())
    assert r.propuesta == {
        "titulo": "Ordenar la sala de servidores",
        "descripcion": "Dejar la sala de servidores ordenada, con el módem colgado en la pared.",
        "tipo": "estrategico", "referente_id": "m-lucas", "fecha": "2026-10-16"}
    assert r.avisos == [] and r.elegir == []


def test_de_que_cuelga_sale_de_la_lista_y_el_tipo_de_ese_lugar():
    texto = "es parte de arrancar la linea 3: capacitar a los operarios, lo ve nahuel"
    r = _revisar(_respuesta(padre="P2", tipo="hito", referente="nahuel", fecha=None),
                 texto=texto)
    # Debajo de un hito sólo va un operativo: el tipo de la IA no corresponde y queda el que va.
    assert r.propuesta["padre_id"] == "o-linea"
    assert r.propuesta["tipo"] == "operativo"
    assert {"campo": "tipo", "motivo": "no_corresponde"} in r.descartados
    r = _revisar(_respuesta(padre="P1", tipo="hito", referente="nahuel", fecha=None), texto=texto)
    assert (r.propuesta["padre_id"], r.propuesta["tipo"]) == ("o-planta", "hito")
    # Sin tipo de la IA, debajo de un estratégico, el operativo (la preselección del formulario).
    r = _revisar(_respuesta(padre="P1", tipo="", referente="nahuel", fecha=None), texto=texto)
    assert r.propuesta["tipo"] == "operativo"


def test_un_codigo_que_no_esta_en_la_lista_no_se_propone():
    r = _revisar(_respuesta(padre="P9"))
    assert "padre_id" not in r.propuesta
    assert {"campo": "padre", "motivo": "no_existe"} in r.descartados
    # Sin padre, el tipo es el que va sin padre.
    assert r.propuesta["tipo"] == "estrategico"


def test_sin_padre_el_tipo_es_estrategico_aunque_la_ia_diga_otro():
    r = _revisar(_respuesta(tipo="operativo"))
    assert r.propuesta["tipo"] == "estrategico"


def test_lo_que_eligio_la_persona_no_se_pide_ni_se_pisa():
    r = _revisar(_respuesta(padre="P1", tipo="hito"),
                 escrito=_vacio(padre_id="o-linea", tipo="operativo"))
    assert "padre_id" not in r.propuesta and "tipo" not in r.propuesta
    # Con de qué cuelga elegido y sin tipo, el que admite ese lugar.
    r = _revisar(_respuesta(tipo="estrategico"), escrito=_vacio(padre_id="o-linea"))
    assert r.propuesta["tipo"] == "operativo"


def test_el_referente_es_solo_un_referente_de_area():
    """Decisión 3 del usuario (2026-10-14): Marcos está en el equipo pero no es referente."""
    texto = EJEMPLO.replace("lucas", "marcos")
    r = _revisar(_respuesta(referente="marcos"), texto=texto)
    assert "referente_id" not in r.propuesta
    assert r.avisos == [{"campo": "referente", "motivo": "no_encontrado",
                         "texto": "No encontré a «marcos» entre los referentes de área; elegí el "
                                  "referente."}]


def test_alguien_que_no_es_del_equipo_no_se_reemplaza():
    texto = EJEMPLO.replace("lucas", "pepe")
    r = _revisar(_respuesta(referente="pepe"), texto=texto)
    assert "referente_id" not in r.propuesta
    assert r.avisos[0]["motivo"] == "no_encontrado"


def test_dos_referentes_con_esas_palabras_se_muestran_para_elegir():
    """ADR 0020, decisión 3: "el ruso" es el apodo de Lucas y de Nahuel; Leda no elige."""
    texto = EJEMPLO.replace("lucas", "el ruso")
    r = _revisar(_respuesta(referente="el ruso"), texto=texto)
    assert "referente_id" not in r.propuesta
    assert r.elegir == [
        {"membership_id": "m-lucas", "nombre": "Lucas Pérez", "area": "Infraestructura"},
        {"membership_id": "m-nahuel", "nombre": "Nahuel Gómez", "area": "Calidad"}]
    assert r.avisos == [{"campo": "referente", "motivo": "varios",
                         "texto": "Encontré a más de un referente para el ruso: elegí el "
                                  "referente."}]


def test_palabras_que_la_persona_no_escribio_no_nombran_a_nadie():
    r = _revisar(_respuesta(referente="ismael"))
    assert "referente_id" not in r.propuesta
    assert {"campo": "referente", "motivo": "no_lo_dijo"} in r.descartados


def test_sin_referente_nombrado_no_se_propone_ninguno():
    texto = "hay q dejar la sala de servidores ordenada para el viernes"
    r = _revisar(_respuesta(referente=""), texto=texto)
    assert "referente_id" not in r.propuesta and r.avisos == []


def test_una_fecha_que_nadie_dijo_no_se_propone():
    texto = "hay q dejar la sala de servidores ordenada, lo lleva lucas"
    r = _revisar(_respuesta(como_dijo_la_fecha="para el viernes"), texto=texto)
    assert "fecha" not in r.propuesta
    assert [a["motivo"] for a in r.avisos if a["campo"] == "fecha"] == ["no_dicha"]
    r = _revisar(_respuesta(fecha="", como_dijo_la_fecha=""), texto=texto)
    assert "fecha" not in r.propuesta and r.avisos == []


def test_la_fecha_la_calcula_el_codigo_y_tiene_que_ser_habil():
    # La IA calculó otro día del que dicen las palabras: no vale.
    r = _revisar(_respuesta(fecha="2026-10-23"))
    assert "fecha" not in r.propuesta
    assert [a["motivo"] for a in r.avisos if a["campo"] == "fecha"] == ["no_entendida"]
    texto = EJEMPLO.replace("para el viernes", "para el sabado")
    r = _revisar(_respuesta(fecha="2026-10-17", como_dijo_la_fecha="para el sabado"), texto=texto)
    assert "fecha" not in r.propuesta
    assert [a["motivo"] for a in r.avisos if a["campo"] == "fecha"] == ["no_es_habil"]
    texto = EJEMPLO.replace("para el viernes", "antes del viernes")
    r = _revisar(_respuesta(fecha="2026-10-15", como_dijo_la_fecha="antes del viernes"),
                 texto=texto)
    assert r.propuesta["fecha"] == "2026-10-15"


def test_la_fecha_despues_del_padre_se_propone_igual():
    """El formulario frena después (J3-3b); la ayuda propone lo que dijo la persona."""
    texto = "parte de arrancar la linea 3, capacitar operarios, lo ve nahuel, para el 4 de diciembre"
    r = _revisar(_respuesta(padre="P2", tipo="operativo", referente="nahuel", fecha="2026-12-04",
                            como_dijo_la_fecha="para el 4 de diciembre",
                            titulo="Capacitar a los operarios",
                            descripcion="Capacitar a los operarios."), texto=texto)
    assert r.propuesta["fecha"] == "2026-12-04"
    assert r.propuesta["padre_id"] == "o-linea"


def test_el_nombre_y_la_descripcion_no_inventan_numeros_ni_nombres():
    r = _revisar(_respuesta(titulo="Ordenar las 3 salas de servidores",
                            descripcion="Lo pidió Ariel para la auditoría."))
    assert "titulo" not in r.propuesta and "descripcion" not in r.propuesta
    assert {"campo": "titulo", "motivo": "dato"} in r.descartados
    assert {"campo": "descripcion", "motivo": "nombre"} in r.descartados
    assert {a["campo"] for a in r.avisos} == {"titulo", "descripcion"}
    assert next(a for a in r.avisos if a["campo"] == "titulo")["texto"] == (
        "No pude proponer el nombre con lo que escribiste; contame qué se quiere lograr.")


def test_los_nombres_de_los_datos_valen_y_los_mal_escritos_se_escriben_bien():
    texto = "parte de la planta nueba, ordenar el deposito, lo ve el ruso"
    r = _revisar(_respuesta(titulo="Ordenar el depósito de la planta nueva",
                            descripcion="Ordenar el depósito de Abrir la planta nueva.",
                            padre="P1", tipo="hito", referente="", fecha=""), texto=texto)
    assert r.propuesta["titulo"] == "Ordenar el depósito de la planta nueva"
    # "Abrir" con mayúscula está en los datos (el nombre del objetivo del que cuelga).
    assert r.propuesta["descripcion"] == "Ordenar el depósito de Abrir la planta nueva."


def test_los_topes_del_formulario():
    r = _revisar(_respuesta(titulo="Ordenar " * 30, descripcion="ordenar " * 120))
    assert "titulo" not in r.propuesta and "descripcion" not in r.propuesta
    assert {"campo": "titulo", "motivo": "largo"} in r.descartados


def test_el_nombre_sin_el_punto_final():
    r = _revisar(_respuesta(titulo="Ordenar la sala de servidores."))
    assert r.propuesta["titulo"] == "Ordenar la sala de servidores"


def test_una_respuesta_vacia_no_propone_nada_y_lo_dice():
    r = _revisar({}, texto="algo")
    assert "titulo" not in r.propuesta
    assert {a["campo"] for a in r.avisos} == {"titulo", "descripcion"}
    # El tipo sin padre se sabe sin la IA.
    assert r.propuesta == {"tipo": "estrategico"}


# --- El referente por el área (J3-4b, como la J2-18 de la carga) ---------------------------------
#
# "Leda completa todo lo que puede": si la persona no nombró a nadie, la IA puede decir de qué área
# es el objetivo, de la lista de áreas con referente, y el código propone a su referente, marcado
# como propuesto. Quien se nombró gana siempre; nombrado alguien que no es referente, se dice y no
# se pone a otro por el área; un área que no está en la lista no propone a nadie.

SIN_NOMBRE = "hay q armar el laboratorio de calidad para medir las piezas"


def test_la_ia_recibe_las_areas_con_referente_con_un_codigo_y_sin_ids():
    entrada = ayuda.entrada_de_la_ia(SIN_NOMBRE, _vacio(), OPCIONES)
    assert entrada["areas"] == [{"codigo": "A1", "area": "Calidad"},
                                {"codigo": "A2", "area": "Dirección"},
                                {"codigo": "A3", "area": "Infraestructura"}]
    propiedades = ayuda.herramienta(["referente"])["function"]["parameters"]["properties"]
    assert set(propiedades) == {"referente", "area"}
    # Sin el referente para completar, tampoco el área.
    assert "area" not in ayuda.herramienta(["titulo"])["function"]["parameters"]["properties"]


def test_un_area_repetida_va_una_vez_y_la_de_dos_referentes_no_va():
    """R3-area-duplicada (RDD de la J3-4b): la IA elige por el nombre del área."""
    opciones = {**OPCIONES, "referentes": [
        {"membership_id": "m1", "nombre": "Uno", "areas": ["Calidad", "calidad", "Planta"]},
        {"membership_id": "m2", "nombre": "Dos", "areas": ["Planta", "Depósito"]}]}
    entrada = ayuda.entrada_de_la_ia(SIN_NOMBRE, _vacio(), opciones)
    assert entrada["areas"] == [{"codigo": "A1", "area": "Calidad"},
                                {"codigo": "A2", "area": "Depósito"}]


def test_sin_nadie_nombrado_el_referente_del_area_que_propone_leda():
    r = _revisar(_respuesta(referente="", area="A1", fecha=None, titulo="Armar el laboratorio",
                            descripcion="Armar el laboratorio de calidad para medir las piezas."),
                 texto=SIN_NOMBRE)
    assert r.propuesta["referente_id"] == "m-nahuel"
    assert r.referente_de == "leda"
    assert r.avisos == [] and r.elegir == []
    # El código del área, escrito como venga.
    r = _revisar(_respuesta(referente="", area="a3", fecha=None), texto=SIN_NOMBRE)
    assert r.propuesta["referente_id"] == "m-lucas"


def test_sin_nadie_nombrado_y_sin_un_area_clara_no_se_propone_referente():
    r = _revisar(_respuesta(referente="", area="", fecha=None), texto=SIN_NOMBRE)
    assert "referente_id" not in r.propuesta and r.referente_de is None
    assert not [a for a in r.avisos if a["campo"] == "referente"]


def test_un_area_que_no_esta_en_la_lista_no_propone_a_nadie():
    r = _revisar(_respuesta(referente="", area="A9", fecha=None), texto=SIN_NOMBRE)
    assert "referente_id" not in r.propuesta and r.referente_de is None
    assert {"campo": "referente", "motivo": "area_no_existe"} in r.descartados


def test_el_referente_nombrado_gana_sobre_el_area():
    r = _revisar(_respuesta(area="A1"))
    assert r.propuesta["referente_id"] == "m-lucas"
    assert r.referente_de == "dicho"


def test_nombrado_alguien_que_no_es_referente_el_area_no_lo_reemplaza():
    texto = EJEMPLO.replace("lucas", "marcos")
    r = _revisar(_respuesta(referente="marcos", area="A3"), texto=texto)
    assert "referente_id" not in r.propuesta and r.referente_de is None
    assert [a["motivo"] for a in r.avisos if a["campo"] == "referente"] == ["no_encontrado"]
    # Palabras que la persona no escribió: igual nombró a alguien, y el área no lo reemplaza.
    r = _revisar(_respuesta(referente="ismael", area="A3"))
    assert "referente_id" not in r.propuesta


def test_con_el_referente_ya_elegido_el_area_no_se_mira():
    r = _revisar(_respuesta(referente="", area="A1"), escrito=_vacio(referente_id="m-lucas"))
    assert "referente_id" not in r.propuesta and r.referente_de is None


def test_el_tipo_que_eligio_la_persona_cambia_si_leda_propone_un_padre_donde_no_va():
    """RDD de la J3-4 (R3-tipo-override-untested): la persona eligió el tipo sin elegir de qué
    cuelga; si Leda propone un padre debajo del cual ese tipo no va, el tipo pasa a uno que vaya
    ahí (como hace la web al cambiar de qué cuelga): el de la IA si va, o el que preselecciona el
    formulario. Si el tipo elegido va ahí, no se toca."""
    texto = "es parte de arrancar la linea 3: capacitar a los operarios, lo ve nahuel"
    # Estratégico no va debajo de un hito, ni el hito que dice la IA: el operativo.
    r = _revisar(_respuesta(padre="P2", tipo="hito", referente="nahuel", fecha=None),
                 texto=texto, escrito=_vacio(tipo="estrategico"))
    assert (r.propuesta["padre_id"], r.propuesta["tipo"]) == ("o-linea", "operativo")
    assert {"campo": "tipo", "motivo": "no_corresponde"} in r.descartados
    # Debajo de un estratégico, el hito que dice la IA va.
    r = _revisar(_respuesta(padre="P1", tipo="hito", referente="nahuel", fecha=None),
                 texto=texto, escrito=_vacio(tipo="estrategico"))
    assert (r.propuesta["padre_id"], r.propuesta["tipo"]) == ("o-planta", "hito")
    # Sin tipo de la IA, el que preselecciona el formulario.
    r = _revisar(_respuesta(padre="P1", tipo="", referente="nahuel", fecha=None),
                 texto=texto, escrito=_vacio(tipo="estrategico"))
    assert r.propuesta["tipo"] == "operativo"
    # El operativo que eligió la persona va debajo de un estratégico: no se toca.
    r = _revisar(_respuesta(padre="P1", tipo="hito", referente="nahuel", fecha=None),
                 texto=texto, escrito=_vacio(tipo="operativo"))
    assert r.propuesta["padre_id"] == "o-planta" and "tipo" not in r.propuesta
