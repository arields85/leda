"""Las reglas de comparación del corredor, sin base (revisión de la E2-7).

`tests/conversaciones/comprobar.py`: lo esperado de un paso contra lo que pasó, y cómo se
clasifica cada diferencia (garantía, comprensión o motor).
"""

from __future__ import annotations

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
    assert [(f.clase, f.que, f.real) for f in c.fallas] == [
        (cp.MOTOR, cp.AVISO_SIN_REDACTAR, {"falla": "X"}),
        (cp.MOTOR, "incidente", [{"etapa": "motor_ciclo", "severidad": "alta"}])]


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
