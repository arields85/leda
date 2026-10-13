"""Las reglas de comparación del corredor, sin base (revisión de la E2-7).

`tests/conversaciones/comprobar.py`: lo esperado de un paso contra lo que pasó, y cómo se
clasifica cada diferencia (garantía, comprensión o motor).
"""

from __future__ import annotations

import pytest

from leda import salida
from tests.conversaciones import comprobar as cp


def _hubo(**mas) -> dict:
    vacio = {"estados": {}, "previsiones": [], "bloqueos": [], "bloqueos_resueltos": [],
             "destraban": [], "avisos_guardados": [], "salidas": [], "incidentes": [],
             "avisos_al_administrador": 0, "avances": [], "evidencias": [],
             "confirmadas": []}
    return {**vacio, **mas}


def test_un_bloqueo_resuelto_que_falta_es_de_comprension_y_uno_de_mas_de_garantia():
    falta = cp.Comprobacion()
    de_mas, falto = cp.comprobar_efectos(falta, {"bloqueos_resueltos": ["PLC"]}, _hubo(), {})
    assert (de_mas, falto) == (False, True)
    assert [(f.clase, f.que) for f in falta.fallas] == [
        (cp.COMPRENSION, "falta un efecto: bloqueo resuelto")]

    sobra = cp.Comprobacion()
    de_mas, falto = cp.comprobar_efectos(sobra, {}, _hubo(bloqueos_resueltos=["PLC"]), {})
    assert (de_mas, falto) == (True, False)
    assert [(f.clase, f.que) for f in sobra.fallas] == [
        (cp.GARANTIA, "efecto de más: bloqueo resuelto")]


def test_un_responsable_que_cambia_sin_esperarlo_es_de_garantia_y_uno_que_falta_de_comprension():
    """C-7: ninguna tarea cambia de manos sin las confirmaciones; el corredor lo mira como un
    efecto, igual que un estado."""
    sobra = cp.Comprobacion()
    assert cp.comprobar_efectos(sobra, {}, _hubo(responsables={"COM": "Nahuel"}), {}) == (
        True, False)
    assert [(f.clase, f.que) for f in sobra.fallas] == [
        (cp.GARANTIA, "efecto de más: responsable")]

    falta = cp.Comprobacion()
    assert cp.comprobar_efectos(falta, {"responsables": {"COM": "Nahuel"}}, _hubo(), {}) == (
        False, True)
    assert [(f.clase, f.que) for f in falta.fallas] == [
        (cp.COMPRENSION, "falta un efecto: responsable")]

    bien = cp.Comprobacion()
    assert cp.comprobar_efectos(bien, {"responsables": {"COM": "Nahuel"}},
                                _hubo(responsables={"COM": "Nahuel"}), {}) == (False, False)
    assert bien.fallas == []


def test_el_estado_dice_quien_tiene_cada_tarea_nombrada():
    c = cp.Comprobacion()
    foto = {"preguntas": {}, "esperas": {}, "ultimo_aviso": {},
            "responsables": {"COM": "Nahuel", "PLC": "Marcos"}}
    cp.comprobar_estado(c, {"responsables": {"COM": "Nahuel"}}, foto, "Marcos")
    assert c.fallas == []
    cp.comprobar_estado(c, {"responsables": {"PLC": "Lucas"}}, foto, "Marcos")
    assert [(f.que, f.esperado, f.real) for f in c.fallas] == [("quién tiene PLC", "Lucas",
                                                                 "Marcos")]


def test_el_emparejamiento_no_se_deja_ganar_por_el_primero_que_coincide():
    """Un esperado general no se queda con el real que otro esperado más preciso necesita."""
    esperados = [{"tarea": "PLC"}, {"tarea": "PLC", "fecha": "2026-10-27"}]
    reales = [{"tarea": "PLC", "fecha": "2026-10-27"}, {"tarea": "PLC", "fecha": "2026-10-30"}]

    assert cp._emparejar(esperados, reales) == ([], [])


def test_un_envio_que_junto_avisos_de_dos_tareas_cumple_lo_esperado_de_las_dos():
    """Un mensaje de Leda por su cuenta puede juntar avisos de varias tareas (mecánica §10):
    el corredor lo compara con todas, no con una sola (revisión de la E2-7)."""
    from tests.conversaciones.corredor import Salida, _sale_coincide

    junto = Salida("Marcos", "texto", [], False, tipo="aviso_previo", tareas=["PLC", "COM"],
                   hechos=[{"tarea": "PLC", "vence": "2026-10-23"},
                           {"tarea": "COM", "vence": "2026-10-23"}], tipos=["aviso_previo"])

    assert _sale_coincide({"a": "Marcos", "tipo": "aviso_previo", "tareas": ["PLC", "COM"]},
                          junto)
    assert _sale_coincide({"tipo": "aviso_previo", "tareas": ["COM", "PLC"],
                           "hechos": {"tarea": "COM"}}, junto)
    # Con una sola tarea de la conversación en el foco, el envío cumple lo de esa tarea.
    assert _sale_coincide({"tarea": "PLC", "hechos": {"vence": "2026-10-23"}}, junto, {"PLC"})
    assert not _sale_coincide({"tarea": "PLC"}, junto)


def test_los_hechos_esperados_se_comparan_con_el_aviso_de_ese_tipo_y_esa_tarea():
    """En un envío que junta avisos, los hechos esperados de un tipo y una tarea son los de ese
    aviso, no los de cualquiera del envío (revisión de la corrida en seco con las 16)."""
    from tests.conversaciones.corredor import Salida, _sale_coincide

    previo_com = {"aviso": "vencimiento_proximo", "necesita_respuesta": False,
                  "vence": "2026-11-06"}
    pedido_plc = {"aviso": "pedido_de_estado", "necesita_respuesta": True, "numero": 1}
    junto = Salida("Marcos", "texto", [], False, tareas=["PLC", "COM"],
                   hechos=[pedido_plc, previo_com], tipos=["aviso_previo", "pedido_de_estado"],
                   avisos=[{"tipo": "pedido_de_estado", "tarea": "PLC", "hechos": pedido_plc},
                           {"tipo": "aviso_previo", "tarea": "COM", "hechos": previo_com}])

    assert _sale_coincide({"tipo": "pedido_de_estado", "tareas": ["PLC", "COM"],
                           "hechos": {"numero": 1}}, junto)
    # Los hechos del aviso previo de COM no cumplen lo esperado del pedido de estado.
    assert not _sale_coincide({"tipo": "pedido_de_estado", "tareas": ["PLC", "COM"],
                               "hechos": {"necesita_respuesta": False}}, junto)
    # Con una sola tarea en el foco, sólo cuentan los avisos de esa tarea.
    assert not _sale_coincide({"tarea": "PLC", "hechos": {"vence": "2026-11-06"}}, junto,
                              {"PLC"})
    assert _sale_coincide({"tarea": "PLC", "hechos": {"numero": 1}}, junto, {"PLC"})


def test_cada_aviso_de_un_envio_va_con_sus_propios_hechos():
    """Los avisos de un envío se emparejan con sus hechos por el aviso mismo, no por posición:
    uno sin hechos no corre a los demás (revisión de la corrida en seco con las 16)."""
    from tests.conversaciones.corredor import _avisos_del_envio

    titulos = {"PLC": "Programar PLC", "COM": "Revisar comunicaciones"}
    avisos = [{"id": "b", "tipo": "pedido_de_estado", "tarea": "PLC",
               "hechos": {"tarea": "Programar PLC", "numero": 1}},
              {"id": "a", "tipo": "aviso_previo", "tarea": "COM", "hechos": None}]

    de_cada_uno, hechos = _avisos_del_envio(avisos, titulos)

    assert de_cada_uno == [
        {"id": "a", "tipo": "aviso_previo", "tarea": "COM", "hechos": None},
        {"id": "b", "tipo": "pedido_de_estado", "tarea": "PLC",
         "hechos": {"tarea": "PLC", "numero": 1}}]
    assert hechos == [{"tarea": "PLC", "numero": 1}]        # sólo los que tienen hechos


def test_un_dato_que_puede_traer_vale_si_son_palabras_de_la_persona():
    """Revisión del contrato (2026-10-05): con `puede_traer`, el dato libre puede venir, pero
    sólo con las palabras de la persona (sin importar mayúsculas ni acentos); uno inventado
    sigue siendo una falla. Sin `puede_traer`, nada cambia."""
    esperada = {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30",
                "puede_traer": ["motivo"]}
    mensaje = "olvidate lo del 4, llegó el switch, la termino para el 30"

    def real(**datos):
        return {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", **datos}

    assert cp.jugada_coincide(esperada, real(), mensaje)
    assert cp.jugada_coincide(esperada, real(motivo="Llego el switch"), mensaje)
    assert not cp.jugada_coincide(esperada, real(motivo="el proveedor se demoró"), mensaje)
    # Sin el mensaje (un toque), un dato que puede venir se acepta como antes.
    assert cp.jugada_coincide(esperada, real(motivo="el proveedor se demoró"))
    # Sin puede_traer, un dato libre que no se esperaba sigue siendo una falla.
    sin = {k: v for k, v in esperada.items() if k != "puede_traer"}
    assert not cp.jugada_coincide(sin, real(motivo="llego el switch"), mensaje)


def test_un_dato_que_puede_traer_con_su_valor_puede_faltar_pero_si_viene_es_ese():
    """C-3d, D1: `puede_traer` con el valor del dato (la tarea de `confirmar`, que la ficha
    declara opcional): puede no venir; si viene, tiene que ser ése."""
    esperada = {"nombre": "confirmar", "tarea": "COM", "puede_traer": ["tarea"]}

    assert cp.jugada_coincide(esperada, {"nombre": "confirmar"}, "si")
    assert cp.jugada_coincide(esperada, {"nombre": "confirmar", "tarea": "COM"}, "si")
    assert not cp.jugada_coincide(esperada, {"nombre": "confirmar", "tarea": "PLC"}, "si")
    # Sin `puede_traer`, la tarea que el YAML no nombra sigue siendo una falla.
    assert not cp.jugada_coincide({"nombre": "confirmar"},
                                  {"nombre": "confirmar", "tarea": "COM"}, "si")


def test_puede_traer_solo_nombra_datos_que_la_ficha_declara_opcionales():
    """Un YAML no puede aflojar más de lo que permite la ficha: `puede_traer` con un dato que
    la ficha no declara opcional es un error del YAML, no una coincidencia."""
    import pytest

    with pytest.raises(ValueError, match="opcional"):
        cp.jugada_coincide({"nombre": "anotar_inicio", "tarea": "PLC",
                            "puede_traer": ["fecha"]},
                           {"nombre": "anotar_inicio", "tarea": "PLC"}, "arranque el plc")
    # Un dato que la ficha necesita tampoco: no es opcional.
    with pytest.raises(ValueError, match="opcional"):
        cp.jugada_coincide({"nombre": "entregar", "puede_traer": ["tarea"]},
                           {"nombre": "entregar", "tarea": "PLC"}, "termine el plc")


def test_cada_puede_traer_de_las_conversaciones_es_un_dato_opcional_de_su_ficha():
    from tests.conversaciones.corredor import todas
    from tests.conversaciones.motores import cargar

    fichas = cargar().FICHAS
    vistos = 0
    for conv in todas():
        for paso in conv["pasos"]:
            for j in paso.get("jugadas") or []:
                for dato in j.get("puede_traer") or ():
                    vistos += 1
                    assert dato in fichas[j["nombre"]].opcional, (conv["numero"], paso["paso"],
                                                                  j["nombre"], dato)
    assert vistos


# --- La evidencia: lo escrito es lo confirmado (C-3d, D1) ------------------------------------

def _pieza(clase: str, *cubre: str, tarea: str = "PLC") -> dict:
    return {"tarea": tarea, "clase": clase, "cubre": list(cubre)}


# La 21, vez 1, paso 5 de `resultados/fase-c-c3-regresion.md`: la IA leyó el primer mensaje como
# el resultado de la prueba y no como la explicación, Marcos sumó un texto con la explicación, y
# la cocina escribió las seis piezas de la vista previa que Marcos confirmó. El camino ideal del
# YAML tenía cinco, con un solo texto que cubría las dos cosas.
ESPERADAS_21 = [_pieza("texto", "explicacion", "resultado_de_prueba"), _pieza("imagen", "captura"),
                _pieza("imagen", "captura"), _pieza("imagen", "captura"),
                _pieza("archivo", "archivo")]
ESCRITAS_21 = [_pieza("texto", "resultado_de_prueba"), _pieza("imagen", "captura"),
               _pieza("imagen", "captura"), _pieza("texto", "explicacion"),
               _pieza("imagen", "captura"), _pieza("archivo", "archivo")]


def test_la_evidencia_que_es_la_vista_previa_confirmada_no_es_una_falla_de_garantia():
    """La falsa alarma de la 21: lo escrito es lo que la persona confirmó, así que la garantía
    se cumple; que difiera del camino ideal es de comprensión (o del motor, si las jugadas del
    paso eran las esperadas), con todo lo escrito a la vista."""
    hubo = _hubo(estados={"PLC": "en_revision"}, evidencias=list(ESCRITAS_21),
                 confirmadas=[{"tarea": "PLC", "piezas": list(ESCRITAS_21)}])
    efectos = {"estados": {"PLC": "en_revision"}, "evidencias": ESPERADAS_21}

    c = cp.Comprobacion()
    de_mas, falta = cp.comprobar_efectos(c, efectos, hubo, {})

    assert not c.de(cp.GARANTIA)
    assert (de_mas, falta) == (False, True)
    [f] = c.fallas
    assert (f.clase, f.que) == (cp.COMPRENSION, "lo escrito no es el camino esperado: evidencia")
    assert f.esperado == ESPERADAS_21
    assert f.real["escrito"] == ESCRITAS_21
    assert f.real["confirmado"] == ESCRITAS_21

    # Con las jugadas esperadas en el paso, la diferencia es del motor.
    c = cp.Comprobacion()
    cp.comprobar_efectos(c, efectos, hubo, {}, jugadas_bien=True)
    assert [(f.clase, f.que) for f in c.fallas] == [
        (cp.MOTOR, "lo escrito no es el camino esperado: evidencia")]


def test_la_evidencia_confirmada_que_es_el_camino_esperado_no_tiene_fallas():
    hubo = _hubo(estados={"PLC": "en_revision"}, evidencias=list(ESPERADAS_21),
                 confirmadas=[{"tarea": "PLC", "piezas": list(reversed(ESPERADAS_21))}])
    c = cp.Comprobacion()

    assert cp.comprobar_efectos(c, {"estados": {"PLC": "en_revision"},
                                    "evidencias": ESPERADAS_21}, hubo, {}) == (False, False)
    assert c.fallas == []


def test_la_evidencia_que_no_es_la_vista_previa_confirmada_es_una_falla_de_garantia():
    """La garantía es "lo escrito es lo confirmado": una pieza de más, de menos o que cubre otra
    cosa que lo que la persona confirmó es de garantía, aunque sea el camino del YAML."""
    confirmado = ESPERADAS_21[:4]
    hubo = _hubo(estados={"PLC": "en_revision"}, evidencias=list(ESPERADAS_21),
                 confirmadas=[{"tarea": "PLC", "piezas": confirmado}])
    c = cp.Comprobacion()

    de_mas, _ = cp.comprobar_efectos(c, {"estados": {"PLC": "en_revision"},
                                         "evidencias": ESPERADAS_21}, hubo, {})

    assert de_mas
    [f] = c.de(cp.GARANTIA)
    assert f.que == "lo escrito no es lo confirmado: evidencia"
    assert f.esperado == confirmado
    assert f.real == {"escrito": ESPERADAS_21, "de_mas": [_pieza("archivo", "archivo")]}


def test_la_evidencia_sin_una_confirmacion_en_el_paso_es_de_mas_con_todo_lo_escrito():
    """Una pieza escrita sin que nadie confirmara nada en el paso, o de otra tarea que la
    confirmada, sigue siendo un efecto de más: de garantía, con la lista entera de lo escrito."""
    escrita = [_pieza("texto", "explicacion", tarea="COM")]
    for confirmadas in ([], [{"tarea": "PLC", "piezas": [_pieza("texto", "explicacion")]}]):
        c = cp.Comprobacion()
        de_mas, _ = cp.comprobar_efectos(c, {}, _hubo(evidencias=list(escrita),
                                                      confirmadas=confirmadas), {})
        assert de_mas
        garantia = c.de(cp.GARANTIA)
        assert ("efecto de más: evidencia", {"escrito": escrita, "de_mas": escrita}) in [
            (f.que, f.real) for f in garantia], confirmadas


def test_un_efecto_que_falta_o_sobra_se_muestra_con_todo_lo_escrito():
    """Revisión de la C-4: el informe mostraba como "real" sólo lo que no se emparejó. Ahora
    va siempre la lista entera de lo escrito, junto a lo que sobra o falta."""
    plc = {"tarea": "PLC", "fecha": "2026-10-27"}
    com = {"tarea": "COM", "fecha": "2026-10-30"}

    c = cp.Comprobacion()
    cp.comprobar_efectos(c, {"previsiones": [plc]}, _hubo(previsiones=[plc, com]), {})
    [f] = c.fallas
    assert (f.clase, f.que, f.esperado) == (cp.GARANTIA, "efecto de más: previsión", [plc])
    assert f.real == {"escrito": [plc, com], "de_mas": [com]}

    c = cp.Comprobacion()
    cp.comprobar_efectos(c, {"previsiones": [plc, com]}, _hubo(previsiones=[plc]), {})
    [f] = c.fallas
    assert (f.clase, f.que, f.esperado) == (cp.COMPRENSION, "falta un efecto: previsión",
                                            [plc, com])
    assert f.real == {"escrito": [plc], "faltan": [com]}


def test_de_la_falla_de_un_aviso_el_informe_sabe_la_clase_y_el_codigo_nunca_el_texto():
    """Usuario, 2026-10-07: el informe se publica. De la referencia técnica de un intento que
    falló, sólo la clase de la excepción y su código HTTP, con las dos formas que lo traen."""
    assert cp.falla_sin_texto("HTTPStatusError: ChatGPT respondió HTTP 429 (x).") == {
        "falla": "HTTPStatusError", "http": 429}
    assert cp.falla_sin_texto("HTTPStatusError: Server error '503 Service Unavailable' for "
                              "url 'https://ejemplo'") == {"falla": "HTTPStatusError",
                                                           "http": 503}
    assert cp.falla_sin_texto("ReadTimeout: la red se cortó en 30 s") == {"falla": "ReadTimeout"}
    # Algo que no es una clase no pasa como si lo fuera.
    assert cp.falla_sin_texto("un texto suelto sin clase: con datos") == {"falla": "desconocida"}
    assert cp.falla_sin_texto(None) == {"falla": "desconocida"}

    c = cp.Comprobacion()
    cp.comprobar_incidentes(c, [
        {"etapa": "motor_aviso_reintento", "severidad": "baja", "falla": {"falla": "X"}},
        {"etapa": cp.ETAPA_FUERA_DE_LA_LISTA, "severidad": "baja"},
        {"etapa": "motor_ciclo", "severidad": "alta"}])
    # Un intento que se reintenta es una falla del servicio de la IA (429, 503, un plazo
    # agotado), que Leda reintentó como dice la decisión 8: se informa aparte y no es de Leda.
    assert [(f.clase, f.que, f.real) for f in c.fallas] == [
        (cp.SERVICIO, cp.AVISO_SIN_REDACTAR, {"falla": "X"}),
        (cp.MOTOR, "incidente", [{"etapa": "motor_ciclo", "severidad": "alta"}])]


def test_un_aviso_que_no_salio_tras_sus_intentos_sigue_siendo_una_falla_del_motor():
    """El quinto fallo deja el aviso `fallido`, con su incidente: eso sí se cuenta, como hoy;
    los cuatro intentos antes, como fallas del servicio."""
    c = cp.Comprobacion()
    cp.comprobar_incidentes(c, [
        *[{"etapa": "motor_aviso_reintento", "severidad": "baja", "falla": {"falla": "X"}}] * 4,
        {"etapa": "motor_aviso_guardado", "severidad": "media"}])
    assert [f.clase for f in c.fallas] == [cp.SERVICIO] * 4 + [cp.MOTOR]
    assert c.fallas[-1].que == "incidente"


def test_un_incidente_esperado_no_es_una_falla_y_uno_que_falta_si():
    """Lo que el paso espera que llegue al administrador por su canal (`incidentes`, por su
    etapa; C-5b: quien destraba no tiene Leda conectada, decisión 37): uno esperado no es una
    falla; uno que falta es del motor, y uno de más sigue siendo un incidente."""
    sin_leda = {"etapa": "motor_sin_leda_conectada", "severidad": "media"}
    bien = cp.Comprobacion()
    cp.comprobar_incidentes(bien, [sin_leda], ["motor_sin_leda_conectada"])
    assert bien.fallas == []

    falta = cp.Comprobacion()
    cp.comprobar_incidentes(falta, [], ["motor_sin_leda_conectada"])
    assert [(f.clase, f.que) for f in falta.fallas] == [(cp.MOTOR, "falta un incidente")]

    de_mas = cp.Comprobacion()
    cp.comprobar_incidentes(de_mas, [sin_leda, sin_leda], ["motor_sin_leda_conectada"])
    assert [(f.clase, f.que, f.real) for f in de_mas.fallas] == [
        (cp.MOTOR, "incidente", [sin_leda])]

    efectos = cp.Comprobacion()
    cp.comprobar_efectos(efectos, {"incidentes": ["motor_sin_leda_conectada"]},
                         _hubo(incidentes=[sin_leda]), {})
    assert efectos.fallas == []


# --- El formato de los mensajes (segunda vuelta, usuario, 2026-10-07) ---------------------------

PLC = "Programar PLC de la comprimidora"
COM = "Revisar comunicaciones industriales de la comprimidora"
TITULOS = (PLC, COM)


def _reglas(texto: str) -> set[str]:
    return {regla for regla, _ in cp.fallas_de_formato(texto, TITULOS)}


# Mensajes con el formato que pidió el usuario (fixtures: datos ficticios de las conversaciones).
BIEN_CON_PREGUNTA = f"""Anoté lo que me contaste.

📋 {PLC}
✏️ La arrancaste hoy.
✏️ Te pregunto cómo viene el vie 23/10.

📋 {COM}
✏️ La terminás el mié 4/11: esperás el switch nuevo.
✏️ Ismael será notificado hoy.
⚠️ Vence el vie 30/10: serían 3 días hábiles de atraso.

¿Quién te trae el switch?"""

BIEN_SIN_RESPUESTA = f"""Marcos va a terminar más tarde una tarea.

📋 {COM}
✏️ La termina el mié 4/11: espera el switch nuevo.
⚠️ Vencía el vie 30/10: son 3 días hábiles de atraso.

No hace falta que respondas."""

BIEN_LISTA = f"""Tenés dos tareas pendientes.

🗓️ {PLC}: sin empezar, vence vie 23/10
🗓️ {COM}: en curso, vence vie 30/10

Conviene empezar por la del PLC, que vence primero."""


def test_el_icono_del_estado_que_pone_la_cocina_tambien_es_marca_de_tarea():
    # Decisión 79: en una lista, la cocina cambia 🗓️ por el ícono del estado de cada tarea.
    for icono in salida.ICONOS_DE_ESTADO:
        assert _reglas(BIEN_LISTA.replace("🗓️", icono)) == set(), icono


def test_un_mensaje_con_el_formato_pedido_no_tiene_fallas_de_formato():
    for texto in (BIEN_CON_PREGUNTA, BIEN_SIN_RESPUESTA, BIEN_LISTA, "¿Cuál de las dos?",
                  "Listo, quedó anotado.\n\nNo hace falta que respondas."):
        assert cp.fallas_de_formato(texto, TITULOS) == [], texto


def test_cada_regla_del_formato_se_reconoce_con_su_renglon():
    assert _reglas(BIEN_LISTA.replace("Tenés dos", "Tenés **dos**")) == {cp.SIN_NEGRITA}
    # El nombre completo, en un renglón que no es de una tarea, y dos veces.
    assert _reglas(BIEN_LISTA.replace("la del PLC", PLC)) == {cp.TAREA_EN_SU_RENGLON,
                                                               cp.TAREA_UNA_VEZ}
    assert _reglas(BIEN_SIN_RESPUESTA.replace(f"📋 {COM}", f"📋 {COM}, en curso")) == {
        cp.TAREA_SOLA}
    largo = "✏️ " + "una idea que se estira " * 7
    assert len(largo) > cp.RENGLON_MAXIMO
    assert _reglas(BIEN_SIN_RESPUESTA.replace("✏️ La termina", largo + "\n✏️ La termina")) == {
        cp.RENGLON_CORTO}
    assert _reglas(BIEN_LISTA.replace("vence vie 23/10", "vence el viernes 23 de octubre")) == {
        cp.FECHA_CORTA}


def test_el_tope_del_renglon_es_el_de_la_cocina():
    """Uno solo: el corredor mide con el mismo número con el que la cocina parte los renglones."""
    assert cp.RENGLON_MAXIMO is salida.RENGLON_MAXIMO


# Mensajes de la ronda real de las decisiones 66 a 73 (`fase-c-decisiones-66-73.md`) que el
# corredor marcó por un renglón largo o por el cierre pegado a lo anterior.
REALES_CON_LA_FORMA_DE_LA_IA = [
    (f"📋 {COM}\n⚠️ Sigue frenada porque falta el switch nuevo.\n\n"
     "Cuando puedas seguir, avisame. No hace falta responder ahora."),
    (f"📋 {PLC}\n✏️ Quedó pedido el pase a Martín.\n"
     "Marcos y Martín serán avisados hoy a las 12:10. No hace falta que respondas."),
    ("Marcos dijo que le toca a Ariel. Ariel primero dijo que la tendría para el jue 22/10; "
     "después avisó que se le complicó con otra cosa y que la tendría ayer. No hay confirmación "
     "de que ya esté."),
    (f"📋 {COM}\n✏️ Quedó asentado que seguís trabado porque te falta la IP del servidor de "
     "Corelabs. Van 10 días hábiles desde que lo contaste, el mar 20/10.\n\n"
     "¿Seguís esperando la IP?"),
]


def test_lo_que_la_cocina_le_da_forma_ya_no_falla_por_el_renglon_ni_por_el_cierre():
    for texto in REALES_CON_LA_FORMA_DE_LA_IA:
        assert _reglas(texto) & {cp.RENGLON_CORTO, cp.CIERRE_APARTE}, texto
        assert not _reglas(salida.dar_forma(texto)) & {cp.RENGLON_CORTO, cp.CIERRE_APARTE}, texto


# --- Tercera vuelta (usuario, 2026-10-07, después de la segunda prueba por Telegram) ------------

def test_la_marca_de_una_tarea_con_su_vencimiento_es_el_calendario_de_espiral():
    """Telegram dibuja 📅 con una fecha fija, que confunde al lado de un vencimiento: la marca de
    la lista es 🗓️, con o sin el selector de emoji que la sigue."""
    assert _reglas(BIEN_LISTA.replace("🗓️", "🗓")) == set()
    con_la_vieja = BIEN_LISTA.replace("🗓️", "📅")
    assert cp.MARCA_DE_LA_LISTA in _reglas(con_la_vieja)
    assert dict(cp.fallas_de_formato(con_la_vieja, TITULOS))[cp.MARCA_DE_LA_LISTA] == (
        f"📅 {PLC}: sin empezar, vence vie 23/10")


# Lo que escribió la IA en la prueba por Telegram (datos ficticios): lo anotado antes que la tarea.
REAL_ANOTADO_ANTES = f"""Quedó anotado.

✏️ Anoté que estás trabado: te falta el cable de programación.
📋 {PLC}
⚠️ Vence el vie 23/10.

¿Quién te puede conseguir el cable?"""


# El aviso a Ismael que escribió la IA en la prueba por Telegram (datos ficticios): quién dijo qué
# antes de la tarea, y una marca en el medio del renglón.
REAL_AVISO_A_ISMAEL_DESORDENADO = f"""Marcos dijo que terminará esta tarea el vie 23/10:
📋 {COM}

Vence el vie 16/10. ⚠️ Si la termina el día que dijo, tendrá 5 días hábiles de atraso.

No hace falta responder."""
# Lo que pidió el usuario en su lugar.
AVISO_A_ISMAEL_ORDENADO = f"""📋 {COM}
Marcos dijo que terminará esta tarea el vie 23/10.

Vence el vie 16/10.

⚠️ Si la termina el día que dijo, tendrá 5 días hábiles de atraso.

No hace falta responder."""


def test_en_un_bloque_con_una_tarea_su_renglon_es_el_primero():
    """Usuario, 2026-10-07: todo lo de la tarea, también quién dijo qué, va debajo de su renglón
    con 📋. Un bloque sin 📋 no tiene orden que cumplir."""
    assert _reglas(AVISO_A_ISMAEL_ORDENADO) == set()
    reales = dict(cp.fallas_de_formato(REAL_AVISO_A_ISMAEL_DESORDENADO, TITULOS))
    assert set(reales) == {cp.TAREA_PRIMERO, cp.MARCA_AL_PRINCIPIO}
    assert reales[cp.TAREA_PRIMERO] == "Marcos dijo que terminará esta tarea el vie 23/10:"
    assert reales[cp.MARCA_AL_PRINCIPIO] == (
        "Vence el vie 16/10. ⚠️ Si la termina el día que dijo, tendrá 5 días hábiles de atraso.")


def test_una_marca_va_solo_al_principio_de_su_renglon():
    """Usuario, 2026-10-07: 📋 🗓️ ✏️ ⚠️ abren su renglón; nunca van en el medio, tampoco una
    segunda marca después de la que lo abre."""
    for renglon in (f"Arrancaste 📋 {PLC}", "Quedó anotado ✏️ la arrancaste hoy.",
                    "⚠️ Vence hoy. ⚠️ Son 3 días de atraso.", "Vence vie 23/10 🗓️",
                    "✏ La arrancaste hoy, ⚠ vence mañana."):
        assert cp.MARCA_AL_PRINCIPIO in _reglas(renglon), renglon
    for renglon in ("⚠️ Vence hoy.", "⚠ Vence hoy.", "✏️ La arrancaste hoy.", f"📋 {PLC}"):
        assert _reglas(renglon) == set(), renglon


def test_en_cada_bloque_la_tarea_va_primero_y_despues_lo_anotado():
    assert _reglas(REAL_ANOTADO_ANTES) == {cp.TAREA_PRIMERO}
    assert dict(cp.fallas_de_formato(REAL_ANOTADO_ANTES, TITULOS))[cp.TAREA_PRIMERO] == (
        "✏️ Anoté que estás trabado: te falta el cable de programación.")
    # Una consecuencia antes de la tarea, también; con o sin el selector de emoji.
    assert _reglas(BIEN_SIN_RESPUESTA.replace(
        f"📋 {COM}\n✏️ La termina el mié 4/11: espera el switch nuevo.\n⚠",
        f"⚠ Vencía el vie 30/10.\n📋 {COM}\n✏️ La termina el mié 4/11: espera el switch nuevo.\n⚠"
    )) == {cp.TAREA_PRIMERO}
    # Con la tarea primero, bien; un bloque sin tarea puede llevar lo anotado solo.
    ordenado = REAL_ANOTADO_ANTES.replace(
        f"✏️ Anoté que estás trabado: te falta el cable de programación.\n📋 {PLC}",
        f"📋 {PLC}\n✏️ Anoté que estás trabado: te falta el cable de programación.")
    assert _reglas(ordenado) == set()
    assert _reglas("✏️ Quedó anotado.\n\n📋 " + PLC + "\n✏️ La arrancaste hoy.") == set()
    # Lo que va debajo de una tarea no cuenta contra la siguiente del mismo bloque.
    assert _reglas(f"📋 {PLC}\n✏️ La arrancaste hoy.\n📋 {COM}\n✏️ La terminás el mié 4/11."
                   ) == set()


# El aviso de escalamiento que escribió la IA en la prueba por Telegram (datos ficticios).
REAL_AVISARE = "Si no respondés, le avisaré a Ismael sobre las dos."


def test_cuando_otra_persona_se_entera_se_dice_en_pasiva_sobre_ella():
    """Usuario, 2026-10-07: "Ismael será notificado", "Ismael fue notificado"; nunca Leda como
    quien le avisa a otro. Lo que la persona que lee va a saber (te aviso) no es un tercero."""
    assert _reglas(REAL_AVISARE) == {cp.NOTIFICADO_EN_PASIVA}
    for activa in ("Le voy a avisar a Ismael hoy.", "Voy a avisarle a Ismael hoy.",
                   "Ya le avisé a Ismael.", "Le aviso a Ismael hoy.",
                   "Les avisaré a los dos.", "Le notifiqué a Ismael el cambio.",
                   "Avisé a Ismael.", "Voy a notificar a Ismael hoy.",
                   "Le acabo de avisar a Ismael."):
        assert _reglas(activa) == {cp.NOTIFICADO_EN_PASIVA}, activa
    for bien in ("Ismael será notificado sobre las dos.", "Ismael fue notificado hoy.",
                 "Ismael se va a enterar hoy.", "Te aviso cuando responda.",
                 "El aviso a Ismael sale hoy.", "Te voy a avisar el vie 23/10.",
                 "Te voy a avisar a las 10.", "¿Querés que le avise a Ismael?"):
        assert _reglas(bien) == set(), bien


def test_el_cierre_va_solo_y_al_final():
    # La pregunta no es el último renglón, o hay dos.
    assert _reglas(BIEN_CON_PREGUNTA.replace("Anoté lo que me contaste.",
                                             "¿Te anoto todo?")) == {cp.PREGUNTA_AL_FINAL}
    assert _reglas(BIEN_CON_PREGUNTA + "\n\nOtra cosa más.") == {cp.PREGUNTA_AL_FINAL}
    # Que no hace falta responder, pero no al final.
    assert _reglas(BIEN_SIN_RESPUESTA + "\n\nSigo atenta.") == {cp.NO_HACE_FALTA_AL_FINAL}
    # El cierre pegado a lo anterior: en el mismo renglón o sin un renglón en blanco antes.
    assert _reglas(BIEN_SIN_RESPUESTA.replace(
        "\n\nNo hace falta", " No hace falta")) == {cp.CIERRE_APARTE}
    assert _reglas(BIEN_CON_PREGUNTA.replace("\n\n¿Quién", "\n¿Quién")) == {cp.CIERRE_APARTE}


# Mensajes reales de la primera vuelta del formato (`resultados/formato-regresion-sol-suscripcion-
# transcripciones.md`, conversación 20, vez 1; GPT-6 sol con la instrucción de negrita, párrafos y
# viñetas): bloques con negrita que la segunda vuelta deja de aceptar.
REAL_AVISO_PREVIO = (f"**{PLC}** vence el **viernes 23 de octubre**, dentro de tres días "
                     "hábiles. No hace falta que respondas.")
REAL_PENDIENTES = f"""Tenés pendientes:

• **{PLC}**: todavía sin empezar; vence el **viernes 23 de octubre**.
• **{COM}**: en curso; vence el **viernes 30 de octubre**.

Podés empezar por **{PLC}**, que vence primero."""
REAL_DOS_HECHOS = f"""Quedó anotado que arrancaste **{PLC}**. Te voy a preguntar cómo viene el \
**viernes 23 de octubre**.

También quedó anotado que prevés terminar **{COM}** el **miércoles 4 de noviembre** porque \
esperás el switch nuevo. Sigue venciendo el **viernes 30 de octubre**; si la terminás el 4, \
serán **3 días hábiles de atraso**. Ismael Soschinski se enterará hoy a las 10:15.

Te voy a preguntar cómo viene esa tarea el **miércoles 4 de noviembre**."""
REAL_AVISO_A_ISMAEL = f"""Marcos dijo que terminará **{COM}** el miércoles 4 de noviembre \
porque espera el switch nuevo. La tarea vence el viernes 30 de octubre; si la termina el día \
que indicó, serán **3 días hábiles de atraso**.

Es solo para que estés al tanto; no hace falta responder."""


def test_los_mensajes_de_la_primera_vuelta_no_cumplen_el_formato_nuevo():
    """La evidencia en rojo: con la instrucción anterior, los mensajes reales de la IA son
    bloques con negrita, las tareas en medio del texto y las fechas largas."""
    assert _reglas(REAL_AVISO_PREVIO) >= {cp.SIN_NEGRITA, cp.TAREA_EN_SU_RENGLON,
                                          cp.FECHA_CORTA, cp.CIERRE_APARTE}
    assert _reglas(REAL_PENDIENTES) >= {cp.SIN_NEGRITA, cp.TAREA_EN_SU_RENGLON,
                                        cp.TAREA_UNA_VEZ, cp.FECHA_CORTA}
    assert _reglas(REAL_DOS_HECHOS) >= {cp.SIN_NEGRITA, cp.TAREA_EN_SU_RENGLON,
                                        cp.RENGLON_CORTO, cp.FECHA_CORTA}
    assert _reglas(REAL_AVISO_A_ISMAEL) >= {cp.SIN_NEGRITA, cp.TAREA_EN_SU_RENGLON,
                                            cp.RENGLON_CORTO, cp.FECHA_CORTA}


def test_una_falla_de_formato_es_de_su_propia_clase_con_el_renglon():
    c = cp.Comprobacion()

    cp.comprobar_formato(c, REAL_AVISO_PREVIO, TITULOS, a="Marcos")

    assert c.fallas and {f.clase for f in c.fallas} == {cp.FORMATO}
    assert all(f.que == "formato del mensaje a Marcos" for f in c.fallas)
    assert (cp.SIN_NEGRITA, REAL_AVISO_PREVIO) in {(f.esperado, f.real) for f in c.fallas}
    assert not c.de(cp.GARANTIA) and not c.de(cp.COMPRENSION) and not c.de(cp.MOTOR)


# --- Otra lectura válida de un mensaje (`o_bien`; decisión 63, la 34) --------------------------

_PASO_CON_OTRA_LECTURA = {
    "paso": 7, "quien": "Mariano", "a_las": "2026-10-20 11:40",
    "escribe": "ni idea yo eso no lo manejo",
    "jugadas": [{"nombre": "decir_que_no_le_toca", "no_sabe": True,
                 "puede_traer": ["tarea", "lo_que_dice"]}],
    "efectos": {"destraban": [{"tarea": "PLA", "no_sabe": True, "de": "Mariano"}]},
    "dice": ["que quedó anotado"],
    "o_bien": {
        "jugadas": [{"nombre": "decir_que_no_le_toca", "puede_traer": ["tarea", "lo_que_dice"]}],
        "pregunta": {"tipo": "cuando_se_destraba", "tarea": "PLA"},
        "dice": ["una sola pregunta: quién se encarga de eso"],
        "luego": [{"paso": "7b", "quien": "Mariano", "a_las": "2026-10-20 11:40",
                   "escribe": "no", "jugadas": [{"nombre": "decir_que_no_le_toca"}]}]}}


def test_un_paso_se_compara_con_la_lectura_que_eligio_la_ia_y_la_otra_trae_sus_pasos():
    """Un mensaje con dos lecturas válidas (`o_bien`): con las jugadas de la principal, lo
    esperado es el paso y no sigue nada; con las de la otra, lo esperado es sólo lo de la otra
    (lo que el paso escribe, más sus propias expectativas: nada se hereda de la principal, así un
    efecto que la otra no declara es de más) y siguen sus pasos (`luego`)."""
    principal = [{"nombre": "decir_que_no_le_toca", "no_sabe": True}]
    otra = [{"nombre": "decir_que_no_le_toca", "lo_que_dice": "yo eso no lo manejo"}]

    esperado, luego = cp.elegir_lectura(_PASO_CON_OTRA_LECTURA, principal)
    assert esperado is _PASO_CON_OTRA_LECTURA and luego == []

    esperado, luego = cp.elegir_lectura(_PASO_CON_OTRA_LECTURA, otra)
    assert esperado == {"paso": 7, "quien": "Mariano", "a_las": "2026-10-20 11:40",
                        "escribe": "ni idea yo eso no lo manejo",
                        "jugadas": _PASO_CON_OTRA_LECTURA["o_bien"]["jugadas"],
                        "pregunta": {"tipo": "cuando_se_destraba", "tarea": "PLA"},
                        "dice": ["una sola pregunta: quién se encarga de eso"],
                        "lectura": cp.O_BIEN}
    assert [p["paso"] for p in luego] == ["7b"]

    # Ninguna de las dos: se compara con la principal, y la falla es la de siempre.
    esperado, luego = cp.elegir_lectura(_PASO_CON_OTRA_LECTURA, [])
    assert esperado is _PASO_CON_OTRA_LECTURA and luego == []
    sin_otra = {k: v for k, v in _PASO_CON_OTRA_LECTURA.items() if k != "o_bien"}
    assert cp.elegir_lectura(sin_otra, otra) == (sin_otra, [])


def test_otra_lectura_mal_escrita_es_un_error_del_yaml():
    """La otra lectura es del mismo mensaje: no cambia lo que la persona escribe ni quién, y un
    toque no tiene lecturas (sus jugadas no se comparan)."""
    import pytest

    con_otro_texto = {**_PASO_CON_OTRA_LECTURA,
                      "o_bien": {**_PASO_CON_OTRA_LECTURA["o_bien"], "escribe": "otra cosa"}}
    with pytest.raises(ValueError, match="escribe"):
        cp.elegir_lectura(con_otro_texto, [])
    un_toque = {"paso": 3, "quien": "Marcos", "a_las": "2026-10-20 11:40", "toca": "PLC",
                "o_bien": {"jugadas": []}}
    with pytest.raises(ValueError, match="toque"):
        cp.elegir_lectura(un_toque, [])


# --- Más de una otra lectura de un mensaje (`o_bien` como lista; decisión 75, la 48, paso 10) --

_FUERA_DE_LA_LISTA = {"jugadas": [{"nombre": "fuera_de_la_lista"}],
                      "efectos": {"avisos_al_administrador": 1},
                      "dice": ["que por ahora no tiene a quién pedírselo"]}
_SIN_JUGADA = {"jugadas": [], "efectos": {}, "hechos": [],
               "dice": ["que por ahora no tiene a quién pedírselo"],
               "luego": [{"paso": "10b", "quien": "Nahuel", "a_las": "2026-10-26 11:31",
                          "escribe": "ok", "jugadas": []}]}
_PASO_CON_DOS_OTRAS = {
    "paso": 10, "quien": "Nahuel", "a_las": "2026-10-26 11:30",
    "escribe": "y lo del switch no se lo podes pedir igual a martin?",
    "jugadas": [{"nombre": "pedir_el_detalle", "tarea": "SW"}],
    "efectos": {},
    "dice": ["que por ahora no tiene a quién pedírselo"],
    "o_bien": [_FUERA_DE_LA_LISTA, _SIN_JUGADA]}


def _lo_que_hace(paso: dict) -> dict:
    return {k: paso[k] for k in ("paso", "quien", "a_las", "escribe")}


def test_con_varias_otras_lecturas_se_elige_la_primera_cuyas_jugadas_coinciden():
    """Decisión 75: un paso puede tener más de una otra lectura (`o_bien` como lista). Con las
    jugadas de la principal, la principal; si no, la primera otra cuyas jugadas coinciden, con sus
    propias expectativas y sus pasos (`luego`); con las de ninguna, la principal."""
    paso = _PASO_CON_DOS_OTRAS

    esperado, luego = cp.elegir_lectura(paso, [{"nombre": "pedir_el_detalle", "tarea": "SW"}])
    assert esperado is paso and luego == []

    esperado, luego = cp.elegir_lectura(paso, [{"nombre": "fuera_de_la_lista"}])
    assert esperado == {**_lo_que_hace(paso), **_FUERA_DE_LA_LISTA, "lectura": cp.O_BIEN}
    assert luego == []

    esperado, luego = cp.elegir_lectura(paso, [])
    assert esperado == {**_lo_que_hace(paso),
                        **{k: v for k, v in _SIN_JUGADA.items() if k != "luego"},
                        "lectura": cp.O_BIEN}
    assert [p["paso"] for p in luego] == ["10b"]

    # Ninguna: se compara con la principal, y la falla es la de siempre.
    esperado, luego = cp.elegir_lectura(paso, [{"nombre": "anotar_inicio", "tarea": "SW"}])
    assert esperado is paso and luego == []


def test_con_dos_otras_lecturas_que_coinciden_vale_la_primera():
    primera = {**_SIN_JUGADA, "dice": ["la primera"], "luego": []}
    paso = {**_PASO_CON_DOS_OTRAS, "o_bien": [primera, _SIN_JUGADA]}

    esperado, luego = cp.elegir_lectura(paso, [])

    assert esperado["dice"] == ["la primera"] and luego == []


def test_un_solo_o_bien_y_una_lista_de_uno_eligen_lo_mismo():
    otra = [{"nombre": "decir_que_no_le_toca", "lo_que_dice": "yo eso no lo manejo"}]
    como_lista = {**_PASO_CON_OTRA_LECTURA, "o_bien": [_PASO_CON_OTRA_LECTURA["o_bien"]]}

    assert cp.elegir_lectura(como_lista, otra) == cp.elegir_lectura(_PASO_CON_OTRA_LECTURA, otra)
    assert cp.elegir_lectura(como_lista, [])[0] is como_lista


@pytest.mark.parametrize("mal", [{"escribe": "otra cosa"}, {"toca": "PLC"}, {"relojes": []},
                                 {"o_bien": {"jugadas": []}}, {"manda": "foto"}],
                         ids=["escribe", "toca", "relojes", "o_bien", "manda"])
def test_cada_otra_lectura_de_la_lista_se_valida(mal):
    """Cada otra lectura de la lista es del mismo mensaje: la segunda se valida como la primera,
    aunque la IA elija la principal."""
    paso = {**_PASO_CON_DOS_OTRAS, "o_bien": [_FUERA_DE_LA_LISTA, {**_SIN_JUGADA, **mal}]}

    with pytest.raises(ValueError, match="no lleva"):
        cp.elegir_lectura(paso, [{"nombre": "pedir_el_detalle", "tarea": "SW"}])


def test_una_lista_de_otras_lecturas_no_vale_en_un_toque_ni_con_algo_que_no_es_una_lectura():
    un_toque = {"paso": 3, "quien": "Marcos", "a_las": "2026-10-20 11:40", "toca": "PLC",
                "o_bien": [{"jugadas": []}, {"jugadas": [{"nombre": "fuera_de_la_lista"}]}]}
    with pytest.raises(ValueError, match="toque"):
        cp.elegir_lectura(un_toque, [])
    con_un_texto = {**_PASO_CON_DOS_OTRAS, "o_bien": [_FUERA_DE_LA_LISTA, "sin jugadas"]}
    with pytest.raises(ValueError, match="o_bien"):
        cp.elegir_lectura(con_un_texto, [])


def test_la_48_paso_10_admite_la_lectura_sin_ninguna_jugada():
    """La ronda real `fase-c-formato-2` (la 48, vez 2, paso 10): la IA no eligió ninguna jugada y
    Leda contestó por el contexto, sin hacer nada (decisión 75). Es la segunda otra lectura del
    paso, después del pedido fuera de la lista (decisión 69)."""
    from tests.conversaciones.corredor import elegir

    [conv] = elegir(["48"])
    paso = next(p for p in conv["pasos"] if p["paso"] == 10)

    esperado, luego = cp.elegir_lectura(paso, [])

    assert esperado.get("lectura") == cp.O_BIEN and luego == []
    assert esperado["jugadas"] == [] and esperado["hechos"] == [] and esperado["efectos"] == {}
    assert esperado["dice"] == paso["dice"] and esperado["no_dice"] == paso["no_dice"]
    fuera, _ = cp.elegir_lectura(paso, [{"nombre": "fuera_de_la_lista"}])
    assert fuera["jugadas"] == [{"nombre": "fuera_de_la_lista"}]


# --- El orden en que la IA nombra las jugadas de un mensaje no importa (la 35, paso 4) ---------

# Las jugadas que eligió la IA en la ronda real `fase-c-formato` (la 35, vez 5, paso 4): las de la
# otra lectura, en otro orden. La cocina las juzga igual en cualquier orden (`fichas.en_orden`).
_REALES_35_VEZ_5 = [
    {"nombre": "anotar_bloqueo", "tarea": "SRV", "causa": "falta el switch nuevo"},
    {"nombre": "decir_cuando_destraba", "tarea": "PLC",
     "lo_que_dice": "todavia no la tengo, estoy parado con el servidor xq falta el switch nuevo",
     "su_tarea_trabada": "SRV"},
    {"nombre": "anotar_quien_destraba", "tarea": "SRV", "quien": "lucas"}]


def _paso_4_de_la_35() -> dict:
    from tests.conversaciones.corredor import elegir

    [conv] = elegir(["35"])
    return next(p for p in conv["pasos"] if p["paso"] == 4)


def test_las_jugadas_de_un_mensaje_coinciden_en_cualquier_orden():
    paso = _paso_4_de_la_35()
    esperadas, mensaje = paso["o_bien"]["jugadas"], paso["escribe"]

    assert cp.jugadas_coinciden(esperadas, _REALES_35_VEZ_5, mensaje)
    assert cp.comprobar_jugadas(cp.Comprobacion(), esperadas, _REALES_35_VEZ_5, mensaje)
    assert cp.jugadas_coinciden(esperadas, list(reversed(_REALES_35_VEZ_5)), mensaje)


def test_una_jugada_distinta_de_menos_o_de_mas_sigue_sin_coincidir_en_cualquier_orden():
    paso = _paso_4_de_la_35()
    esperadas, mensaje = paso["o_bien"]["jugadas"], paso["escribe"]
    bloqueo, decir, quien = _REALES_35_VEZ_5

    distinta = [bloqueo, {**decir, "tarea": "SRV"}, quien]
    assert not cp.jugadas_coinciden(esperadas, distinta, mensaje)
    assert not cp.jugadas_coinciden(esperadas, [quien, bloqueo], mensaje)
    assert not cp.jugadas_coinciden(esperadas, [*_REALES_35_VEZ_5, bloqueo], mensaje)
    # Dos iguales no cubren dos esperadas distintas: cada real va con una sola esperada.
    assert not cp.jugadas_coinciden(esperadas, [bloqueo, bloqueo, quien], mensaje)
    c = cp.Comprobacion()
    assert not cp.comprobar_jugadas(c, esperadas, [quien, bloqueo], mensaje)
    assert [(f.clase, f.que) for f in c.fallas] == [(cp.COMPRENSION, "jugadas")]


def test_la_otra_lectura_se_elige_con_sus_jugadas_en_otro_orden():
    """La 35, vez 5, paso 4: la IA nombró las tres jugadas de la otra lectura en otro orden, y lo
    que hizo Leda fue lo de esa lectura; el corredor la elige igual, y no la principal."""
    paso = _paso_4_de_la_35()

    esperado, luego = cp.elegir_lectura(paso, _REALES_35_VEZ_5)

    assert esperado.get("lectura") == cp.O_BIEN and luego == []
    assert esperado["jugadas"] == paso["o_bien"]["jugadas"]


def test_las_palabras_no_dichas_se_buscan_aunque_las_jugadas_vengan_en_otro_orden():
    mensaje = "no, esa hacela vos nahuel que la conoces mejor"
    esperadas = [{"nombre": "anotar_inicio", "tarea": "PLC"},
                 {"nombre": "contestar_el_pase", "tarea": "SEN", "acepta": False,
                  "puede_traer": ["por_que"]}]
    reales = [{"nombre": "contestar_el_pase", "tarea": "SEN", "acepta": False,
               "por_que": "nahuel la sabe mejor"},
              {"nombre": "anotar_inicio", "tarea": "PLC"}]

    assert cp.palabras_no_dichas(esperadas, reales, mensaje) == "por_que: sabe"


def test_los_hechos_de_un_mensaje_coinciden_en_cualquier_orden():
    """Los hechos de un paso siguen el orden de las jugadas de la IA: se comparan como ellas."""
    bloqueo = {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "SRV"}
    decir = {"jugada": "decir_cuando_destraba", "resultado": "anotado", "tarea": "PLC"}
    quien = {"jugada": "anotar_quien_destraba", "resultado": "anotado"}
    reales = [{**bloqueo, "causa": "falta el switch nuevo"}, {**decir, "lo_que_dice": "x"},
              {**quien, "tarea": "SRV"}]

    assert cp.hechos_coinciden([decir, bloqueo, quien], reales)
    assert cp.hechos_coinciden([bloqueo, decir, quien], reales)
    assert not cp.hechos_coinciden([{**decir, "tarea": "SRV"}, bloqueo, quien], reales)
    assert not cp.hechos_coinciden([decir, bloqueo], reales)
    assert not cp.hechos_coinciden([decir, bloqueo, quien, quien], reales)
    # Lo que no es una lista se compara como siempre.
    assert cp.hechos_coinciden("presente", reales)
    assert cp.hechos_coinciden({"resultado": "anotado"}, {"resultado": "anotado", "tarea": "SRV"})
    assert not cp.hechos_coinciden([decir], {"jugada": "decir_cuando_destraba"})


# --- Una fila con un dato distinto no es un efecto de más (`fase-c.md`, "De las pruebas") ------

def test_una_fila_que_es_la_esperada_con_un_dato_distinto_no_es_de_garantia():
    """La previsión de la tarea que se esperaba, con otra fecha: Leda hizo lo que tenía que
    hacer, con un dato mal entendido. Es una diferencia de ese dato (de comprensión; del motor si
    las jugadas eran las esperadas), no un efecto que nadie pidió."""
    esperada = {"tarea": "PLC", "fecha": "2026-10-27"}
    real = {"tarea": "PLC", "fecha": "2026-10-30"}

    c = cp.Comprobacion()
    assert cp.comprobar_efectos(c, {"previsiones": [esperada]},
                                _hubo(previsiones=[real]), {}) == (False, True)
    [f] = c.fallas
    assert (f.clase, f.que, f.esperado) == (cp.COMPRENSION, "un dato distinto: previsión",
                                            [esperada])
    assert f.real == {"escrito": [real], "distintas": [real]}

    c = cp.Comprobacion()
    cp.comprobar_efectos(c, {"previsiones": [esperada]}, _hubo(previsiones=[real]), {},
                         jugadas_bien=True)
    assert [(f.clase, f.que) for f in c.fallas] == [(cp.MOTOR, "un dato distinto: previsión")]


def test_una_fila_de_verdad_de_mas_sigue_siendo_de_garantia_junto_a_una_con_un_dato_distinto():
    esperada = {"tarea": "PLC", "fecha": "2026-10-27"}
    distinta = {"tarea": "PLC", "fecha": "2026-10-30"}
    de_mas = {"tarea": "COM", "fecha": "2026-10-30"}

    c = cp.Comprobacion()
    assert cp.comprobar_efectos(c, {"previsiones": [esperada]},
                                _hubo(previsiones=[distinta, de_mas]), {}) == (True, True)
    assert [(f.clase, f.que, f.real) for f in c.fallas] == [
        (cp.COMPRENSION, "un dato distinto: previsión",
         {"escrito": [distinta, de_mas], "distintas": [distinta]}),
        (cp.GARANTIA, "efecto de más: previsión",
         {"escrito": [distinta, de_mas], "de_mas": [de_mas]})]


def test_un_aviso_a_otra_persona_no_es_un_dato_distinto():
    """Lo que identifica una fila no es un dato: un aviso a otra persona, o una decisión sobre
    una entrega distinta de la dicha, siguen siendo de más."""
    esperado = {"tipo": "como_termino_el_pase", "tarea": "SEN", "a": "Nahuel",
                "estado": "guardado"}
    a_otra = {**esperado, "a": "Ismael"}
    c = cp.Comprobacion()
    cp.comprobar_efectos(c, {"avisos_guardados": [esperado]},
                         _hubo(avisos_guardados=[a_otra]), {})
    assert [(f.clase, f.que) for f in c.fallas] == [
        (cp.GARANTIA, "efecto de más: aviso guardado")]

    # El mismo aviso con otros hechos sí es un dato distinto.
    otros_hechos = {**esperado, "hechos": {"la_tomo": True}}
    c = cp.Comprobacion()
    cp.comprobar_efectos(c, {"avisos_guardados": [{**esperado, "hechos": {"la_tomo": False}}]},
                         _hubo(avisos_guardados=[otros_hechos]), {})
    assert [(f.clase, f.que) for f in c.fallas] == [
        (cp.COMPRENSION, "un dato distinto: aviso guardado")]

    aprobada = {"tarea": "PLC", "decision": "aprobado", "de": "Ismael"}
    c = cp.Comprobacion()
    cp.comprobar_efectos(c, {"aprobaciones": [{**aprobada, "decision": "rechazado"}]},
                         _hubo(aprobaciones=[aprobada]), {})
    assert [(f.clase, f.que) for f in c.fallas] == [
        (cp.GARANTIA, "efecto de más: decisión sobre una entrega")]


# --- Por qué no coincide una jugada (la 38, paso 23, ronda `fase-c-apodos-regresion-b`) --------

def test_la_falla_de_jugadas_dice_las_palabras_de_un_dato_libre_que_la_persona_no_dijo():
    """Lo esperado y lo real se ven iguales: el informe dice qué palabra del dato libre no
    escribió la persona."""
    mensaje = "no, esa hacela vos nahuel que la conoces mejor"
    esperada = {"nombre": "contestar_el_pase", "tarea": "SEN", "acepta": False,
                "puede_traer": ["por_que"]}
    real = {"nombre": "contestar_el_pase", "tarea": "SEN", "acepta": False,
            "por_que": "nahuel la sabe mejor"}

    c = cp.Comprobacion()
    assert not cp.comprobar_jugadas(c, [esperada], [real], mensaje)
    [f] = c.fallas
    assert (f.clase, f.que) == (cp.COMPRENSION,
                                "jugadas (palabras que la persona no dijo: por_que: sabe)")
    # Con las palabras de la persona, coincide; y una falla de otra clase no agrega nada.
    assert cp.comprobar_jugadas(cp.Comprobacion(), [esperada],
                                [{**real, "por_que": "nahuel la conoces mejor"}], mensaje)
    c = cp.Comprobacion()
    cp.comprobar_jugadas(c, [esperada], [{**real, "acepta": True, "por_que": "la conoces"}],
                         mensaje)
    assert [f.que for f in c.fallas] == ["jugadas"]


def test_un_dato_libre_puede_llevar_el_verbo_de_la_persona_en_otra_persona():
    """Decisión 70 del usuario (2026-10-11; la 38, paso 23): la IA anota `por_que: "nahuel la
    conoce mejor"` de "que la conoces mejor". Se compara la raíz de cada palabra, no su forma
    exacta; una palabra que la persona no dijo sigue fallando."""
    mensaje = "no, esa hacela vos nahuel que la conoces mejor"
    esperada = {"nombre": "contestar_el_pase", "tarea": "SEN", "acepta": False,
                "puede_traer": ["por_que"]}

    def real(por_que: str) -> dict:
        return {"nombre": "contestar_el_pase", "tarea": "SEN", "acepta": False,
                "por_que": por_que}

    assert cp.jugada_coincide(esperada, real("nahuel la conoce mejor"), mensaje)
    assert cp.jugada_coincide(esperada, real("Nahuel la CONOCE mejor"), mensaje)
    assert not cp.jugada_coincide(esperada, real("nahuel la sabe mejor"), mensaje)
    assert not cp.jugada_coincide(esperada, real("nahuel la conoce mejor que nadie"), mensaje)
    assert cp.palabras_no_dichas([esperada], [real("nahuel la conoce mejor")], mensaje) == ""


def test_la_raiz_saca_solo_la_terminacion_y_deja_las_palabras_cortas():
    assert cp.raiz("conoces") == cp.raiz("conoce") == "conoc"
    assert cp.raiz("termino") == cp.raiz("terminas") == "termin"
    assert cp.raiz("la") == "la" and cp.raiz("los") == "los"
    assert cp.raiz("mejor") == "mejor"
    assert cp.raiz("sabe") != cp.raiz("conoce")


def test_dos_palabras_distintas_con_la_misma_raiz_cuentan_como_dichas():
    """Revisión de `fcb8c17`: comparar raíces (decisión 70) deja pasar una palabra distinta que
    termina igual que una de la persona ("caso" por "casa", "paso" por "pase"): el corredor es
    más laxo en eso, a sabiendas. Una palabra con otra raíz sigue faltando, y una corta
    (`_RAIZ_MINIMA`) se compara entera: "mes" no es "mas"."""
    from tests.conversaciones.motores import cargar

    palabras = cargar().palabras
    assert cp.raiz("caso") == cp.raiz("casa") and cp.raiz("paso") == cp.raiz("pase")
    assert cp.palabras_que_no_dijo("el caso", "la casa", palabras) == ["el"]
    assert cp.palabras_que_no_dijo("nahuel la sabe mejor", "que la conoces mejor",
                                   palabras) == ["nahuel", "sabe"]
    assert cp.palabras_que_no_dijo("mes", "mas", palabras) == ["mes"]


def test_un_nombre_se_compara_sin_mayusculas_ni_acentos():
    """La 47, paso 7: la IA escribió "Mariano" y el YAML espera "mariano". Otro nombre sigue
    siendo otro."""
    esperada = {"nombre": "decir_quien_es", "quien_es": "mariano"}

    assert cp.jugada_coincide(esperada, {"nombre": "decir_quien_es", "quien_es": "Mariano"},
                              "mariano")
    assert cp.jugada_coincide({"nombre": "decir_quien_es", "quien_es": "martin"},
                              {"nombre": "decir_quien_es", "quien_es": "Martín"}, "martin")
    assert cp.jugada_coincide(
        {"nombre": "decir_quien_es", "apodo": "el chino", "quien_es": "marcos"},
        {"nombre": "decir_quien_es", "apodo": "El Chino", "quien_es": "Marcos"},
        "el chino es marcos")
    assert not cp.jugada_coincide(esperada, {"nombre": "decir_quien_es", "quien_es": "Marcos"},
                                  "mariano")
    # Los valores especiales del YAML siguen valiendo para un nombre.
    def quien(esperado, real):
        jugada = {"nombre": "decir_quien_es"}
        if real is not None:
            jugada["quien_es"] = real
        return cp.jugada_coincide({"nombre": "decir_quien_es", "quien_es": esperado}, jugada,
                                  "mariano")
    assert quien("presente", "Mariano")
    assert not quien("presente", "")
    assert quien("ausente", "")
    assert quien("ausente", None)
    assert not quien("ausente", "Mariano")
    assert quien("~mar", "Mariano")
    assert quien("~már", "mariano")
    assert not quien("~mart", "Mariano")
    # Un dato que no nombra a nadie se sigue comparando igual que siempre.
    assert not cp.jugada_coincide({"nombre": "anotar_prevision", "tarea": "PLC",
                                   "fecha": "2026-10-30"},
                                  {"nombre": "anotar_prevision", "tarea": "plc",
                                   "fecha": "2026-10-30"}, "la termino el 30")


# --- El acceso a la web (la 50; `odd/tasks/acceso-por-chat.md`, A-1) ---------------------------

def _foto_de_la_web(enlaces: dict | None = None, sesiones: dict | None = None) -> dict:
    """Una foto sin nada más que el acceso a la web: los enlaces de entrada y las sesiones."""
    return {"estados": {}, "previsiones": {}, "bloqueos": {}, "destraban": {},
            "dicen_quien_destraba": {}, "avisos": {}, "salidas": {}, "incidentes": {},
            "avisos_admin": 0, "avances": {}, "evidencias": {}, "archivos_de_tarea": {},
            "aprobaciones": {}, "confirmadas": {}, "compartidas": {}, "apodos": {},
            "enlaces_de_entrada": enlaces or {}, "sesiones_web": sesiones or {}}


def test_los_efectos_del_acceso_a_la_web_son_lo_emitido_lo_anulado_y_lo_cortado_en_el_paso():
    antes = _foto_de_la_web(
        {"e1": {"de": "Marcos", "anulado": False}, "e0": {"de": "Ariel", "anulado": False}},
        {"s0": {"de": "Ariel", "cortada": False, "motivo": None}})
    # Un enlace nuevo de Marcos anula el suyo sin usar; el de Ariel, ya canjeado, no cambia.
    despues = _foto_de_la_web(
        {"e1": {"de": "Marcos", "anulado": True}, "e0": {"de": "Ariel", "anulado": False},
         "e2": {"de": "Marcos", "anulado": False}},
        {"s0": {"de": "Ariel", "cortada": False, "motivo": None}})

    hubo = cp.efectos(antes, despues)

    assert hubo["enlaces_de_entrada"] == [{"de": "Marcos"}]
    assert hubo["enlaces_anulados"] == [{"de": "Marcos"}]
    assert hubo["sesiones_cortadas"] == []
    # Lo que ya estaba anulado o cortado antes del paso no es un efecto del paso.
    cortada = _foto_de_la_web(despues["enlaces_de_entrada"],
                              {"s0": {"de": "Ariel", "cortada": True,
                                      "motivo": "perdio_el_celular"}})
    hubo = cp.efectos(despues, cortada)
    assert (hubo["enlaces_de_entrada"], hubo["enlaces_anulados"]) == ([], [])
    assert hubo["sesiones_cortadas"] == [{"de": "Ariel", "motivo": "perdio_el_celular"}]
    assert cp.efectos(cortada, cortada)["sesiones_cortadas"] == []


def test_un_acceso_a_la_web_de_mas_es_de_garantia_y_uno_que_falta_de_comprension():
    """Nadie recibe ni pierde el acceso a la web sin haberlo pedido o sin que se le ofrezca: un
    enlace emitido, uno anulado o una sesión cortada de más son de garantía (la 50, paso 5: "casi
    pierdo el celular" no corta nada); uno esperado que no pasó, de comprensión."""
    for nombre, que, fila in (
            ("enlaces_de_entrada", "enlace de entrada a la web", {"de": "Marcos"}),
            ("enlaces_anulados", "enlace de entrada a la web anulado", {"de": "Marcos"}),
            ("sesiones_cortadas", "sesión de la web cortada",
             {"de": "Marcos", "motivo": "perdio_el_celular"})):
        sobra = cp.Comprobacion()
        assert cp.comprobar_efectos(sobra, {}, _hubo(**{nombre: [fila]}), {}) == (True, False)
        assert [(f.clase, f.que) for f in sobra.fallas] == [(cp.GARANTIA, f"efecto de más: {que}")]

        falta = cp.Comprobacion()
        assert cp.comprobar_efectos(falta, {nombre: [fila]}, _hubo(), {}) == (False, True)
        assert [(f.clase, f.que) for f in falta.fallas] == [
            (cp.COMPRENSION, f"falta un efecto: {que}")]

        bien = cp.Comprobacion()
        assert cp.comprobar_efectos(bien, {nombre: [fila]}, _hubo(**{nombre: [fila]}),
                                    {}) == (False, False)
        assert bien.fallas == []
