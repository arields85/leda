"""Modificar en el alta conducida: un botón por dato, armado por el código (C0-3).

Ronda C0-A (2026-10-02, 12:40): al tocar Modificar en el resumen del alta conducida,
Leda contestó con un texto del modelo ("puede ser el título, el responsable, la
fecha o el criterio"), sin botones y sin el objetivo, que sí se podía cambiar. La
lista de datos es un hecho del borrador, no una redacción: ADR 0013, regla 3 (estado
real y sólo opciones posibles) y "botones donde hay opciones".

Ahora Modificar abre el selector de siempre ("¿Qué dato querés cambiar del
borrador?"), armado desde el resumen vigente y sin llamar al modelo. Un dato con
opciones (objetivo, responsable) se pregunta con los botones de las mismas opciones
que ya usa el alta; uno de texto (título, fecha, criterio) se pide por escrito, con lo
que tenía para copiar, y la respuesta la atiende el turno del modelo como siempre.
Escribir el cambio en vez de tocar sigue funcionando.

El modelo se guiona (`ProveedorGuionado.conducciones`); ninguna prueba toca la red.
"""

from __future__ import annotations

from datetime import datetime

from leda.db import admin
from leda.salida import etiqueta_sin_icono

from tests.test_alta_conducida import (  # noqa: F401  (fixtures)
    _cuerpos, _en, _hasta_el_resumen, _tocar_modificar, chat, conversada, salida)

SELECTOR = "¿Qué dato querés cambiar del borrador?"


def _resumen_vigente(c) -> list[dict]:
    with admin(c.conn) as cur:
        cur.execute(
            """select p.id from pending_action p
                 join task_intake_request r on r.task_draft_id = p.draft_id
                where r.id = %s and p.estado = 'esperando'""", (c.rid,))
        return cur.fetchall()


def _bloque(c, fila: dict) -> str | None:
    with admin(c.conn) as cur:
        cur.execute("select bloque_copiable from message_outbox where id = %s",
                    (fila["id"],))
        return cur.fetchone()["bloque_copiable"]


def _en_el_selector(chat):
    c, _ = _hasta_el_resumen(chat)
    llamadas = len(c.modelo.conducidos)
    nuevas = _tocar_modificar(c)
    return c, nuevas, llamadas


def test_modificar_muestra_un_boton_por_dato_del_resumen_sin_llamar_al_modelo(chat):
    c, nuevas, llamadas = _en_el_selector(chat)

    assert len(c.modelo.conducidos) == llamadas          # la lista no la decide el modelo
    assert _cuerpos(nuevas) == [SELECTOR]
    assert nuevas[0]["intake_choice_set_id"] is not None
    # El objetivo está (había tres del área de la tarea); el área y la evidencia
    # salen del responsable y la descripción vacía no está en el resumen.
    assert c.etiquetas() == ["Título", "Objetivo", "Responsable", "Fecha objetivo",
                             "Criterio de aceptación", "Volver al resumen"]
    assert _resumen_vigente(c) == []                     # nada se aplica sin Confirmar
    assert c.incidentes("alta_conducida_fallida") == []


def test_una_descripcion_del_resumen_tambien_se_ofrece(chat):
    c, _ = _hasta_el_resumen(chat)
    with admin(c.conn) as cur:
        cur.execute("update task_intake_field set valor = to_jsonb(%s::text) "
                    "where request_id = %s and campo = 'description'",
                    ("Los de la línea 2", c.rid))
    c.conn.commit()

    _tocar_modificar(c)

    assert "Descripción" in c.etiquetas()


def test_elegir_el_objetivo_ofrece_los_objetivos_del_area_y_el_toque_vuelve_al_resumen(
        chat):
    c, _, llamadas = _en_el_selector(chat)
    actual = c.campo("objective")["valor"]["title"]

    nuevas = c.tocar("Objetivo")

    assert len(c.modelo.conducidos) == llamadas
    assert len(nuevas) == 1 and nuevas[0]["intake_choice_set_id"] is not None
    etiquetas = [etiqueta_sin_icono(e) for e in c.etiquetas()]
    assert sorted(etiquetas) == sorted(
        [f"{t} 1" for t in ("Reduce service delay", "Raise delivery quality",
                            "Expand regional coverage")])
    assert actual in etiquetas
    otro = next(e for e in etiquetas if e != actual)
    c.modelo.conducciones.append(salida("Listo, revisalo."))

    nuevas = c.tocar(otro)

    assert c.campo("objective")["valor"]["title"] == otro
    assert len(nuevas) == 1
    assert "Resumen para revisar" in nuevas[0]["cuerpo"]
    assert f"Objetivo: {otro}" in nuevas[0]["cuerpo"]
    assert nuevas[0]["pending_action_id"] is not None    # Confirmar, Modificar, Cancelar
    assert len(_resumen_vigente(c)) == 1


def test_elegir_la_fecha_la_pide_por_escrito_y_la_respuesta_vuelve_al_resumen(chat):
    c, _, llamadas = _en_el_selector(chat)
    vieja = datetime.fromisoformat(_en(3)).strftime("%d/%m/%Y")

    nuevas = c.tocar("Fecha objetivo")

    assert len(c.modelo.conducidos) == llamadas
    (pregunta,) = _cuerpos(nuevas)
    assert "la fecha objetivo" in pregunta and pregunta.endswith(vieja)
    assert _bloque(c, nuevas[0]) == vieja                 # para copiar y corregir
    assert c.etiquetas() == []
    c.modelo.conducciones.append(salida(
        "Listo, cambiada.", intencion="corrige", corrige=["due_date"],
        valores={"due_date": {"fecha_iso": _en(6)}}))

    nuevas = c.escribir("el lunes")

    assert c.campo("due_date")["valor"] == _en(6)
    assert len(nuevas) == 1 and "Resumen para revisar" in nuevas[0]["cuerpo"]
    assert datetime.fromisoformat(_en(6)).strftime("%d/%m/%Y") in nuevas[0]["cuerpo"]
    assert nuevas[0]["pending_action_id"] is not None


def test_volver_al_resumen_lo_muestra_sin_cambios(chat):
    c, _, _ = _en_el_selector(chat)
    titulo = c.campo("title")["valor"]

    nuevas = c.tocar("Volver al resumen")

    assert len(nuevas) == 1 and "Resumen para revisar" in nuevas[0]["cuerpo"]
    assert f"Título: {titulo}" in nuevas[0]["cuerpo"]
    assert len(_resumen_vigente(c)) == 1


def test_escribir_el_dato_en_vez_de_tocar_sigue_yendo_al_modelo(chat):
    c, _, _ = _en_el_selector(chat)
    c.modelo.conducciones.append(salida(
        "Dale, ¿a qué objetivo pertenece?", intencion="corrige",
        corrige=["objective"], pregunta=["objective"], botones="objective"))

    nuevas = c.escribir("el objetivo")

    assert _cuerpos(nuevas) == ["Dale, ¿a qué objetivo pertenece?"]
    assert c.hechos()["evento"] == {"mensaje_de_la_persona": "el objetivo"}
    assert len(c.etiquetas()) == 3                       # los objetivos del área


def test_un_segundo_toque_del_selector_no_abre_nada(chat):
    c, _, _ = _en_el_selector(chat)
    token = c.token("Objetivo")
    c.tocar("Objetivo")
    llamadas = len(c.modelo.conducidos)
    etiquetas = c.etiquetas()

    from tests.test_task_intake import _post_intake_callback
    respuesta = _post_intake_callback(c.cliente, token, c.usuario,
                                      callback_id="cb-repetido-c0-3")

    assert respuesta.status_code == 200
    assert len(c.modelo.conducidos) == llamadas
    assert c.etiquetas() == etiquetas                    # los botones del objetivo siguen
