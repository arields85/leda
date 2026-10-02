"""Modificar en la vista previa del borrador del alta (T9-R1c-3, ADR 0005
decisión 1, precisión del 2026-09-29; ADR 0013 regla 1, enmienda "una sola rama
abierta").

La vista previa del borrador pasa a tener Confirmar, Modificar y Cancelar.
Modificar pregunta qué dato cambiar, con un botón por dato; un dato de texto
muestra lo que la persona tenía en un bloque que se copia con un toque (y el
botón de copiar si entra en 256), y el mensaje siguiente lo reemplaza; un dato
que se elige con botones vuelve a mostrar sus opciones. Cambia sólo ese dato y
vuelve la vista previa con los mismos tres botones. La tarea se crea sólo con
Confirmar. `corrige` escrito sobre la vista previa lleva al mismo selector.

Los ruteos y el modelo se guionan; ninguna prueba toca la red ni el modelo real.
"""

from __future__ import annotations

from datetime import time
from zoneinfo import ZoneInfo

import pytest

from leda import gateway
from leda import ingreso_tareas as I
from leda import pendientes as P
from leda.calendario import Calendario
from leda.db import admin, autoridad, espacio
from leda.despachador import TransporteDePrueba, despachar
from leda.llm import RespectoPendiente
from leda.salida import (COPY_TEXT_LIMIT, ETIQUETA_COPIAR, ETIQUETA_MODIFICAR,
                           etiqueta_sin_icono)

from tests.test_alta_eleccion_confirmacion import (TITULO, _alta_en_confirmacion,
                                                   _alta_enviada, _escribir,
                                                   _nuevas, _ruta,
                                                   _salidas, _solicitud, _tocar_boton,
                                                   _usuario)
from tests.toques import FUERA_DE_LA_VENTANA, envejecer_toques
from tests.test_task_intake import (_RoutingProvider, _active_choices,
                                    _callback_client, _choose,
                                    _post_intake_callback, _start)

ETIQUETAS_DE_LOS_DATOS = ["Título", "Descripción", "Objetivo", "Responsable",
                          "Área", "Fecha objetivo", "Criterio de aceptación"]
ETIQUETAS_DEL_SELECTOR = ETIQUETAS_DE_LOS_DATOS + ["Volver al resumen"]
AVISO_TOQUE_YA_USADO = ("Ese pedido ya no está vigente. Si sigue haciendo falta, "
                        "escribime y lo vemos de nuevo.")


# ----------------------------------------------------------------- ayudas

def _campos(conn, rid) -> dict:
    with admin(conn) as cur:
        cur.execute("select campo, estado, valor from task_intake_field "
                    "where request_id = %s order by campo", (rid,))
        return {f["campo"]: (f["estado"], f["valor"]) for f in cur.fetchall()}


def _previews(conn, rid) -> list[dict]:
    """Las vistas previas del borrador de la solicitud, la más vieja primero."""
    with admin(conn) as cur:
        cur.execute(
            """select p.id, p.estado, p.resumen from pending_action p
                 join task_intake_request r on r.task_draft_id = p.draft_id
                where r.id = %s order by p.creado_en, p.id""", (rid,))
        return cur.fetchall()


def _etiquetas_de_la_vista_previa(conn, pid) -> list[str]:
    with admin(conn) as cur:
        return [etiqueta_sin_icono(o.etiqueta) for o in P.opciones(cur, pid)]


def _tareas(conn) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from task")
        return cur.fetchone()["n"]


def _conjunto_activo(conn, rid):
    with admin(conn) as cur:
        cur.execute("""select id, tipo, campo from task_intake_choice_set
                        where request_id = %s and estado = 'active'""", (rid,))
        return cur.fetchone()


def _opciones_activas(conn, rid) -> dict:
    """Las etiquetas (sin ícono) de la elección activa y su token."""
    with admin(conn) as cur:
        return {etiqueta_sin_icono(e): t
                for e, t in _active_choices(cur, rid).items()}


def _ultima_salida(conn, chat_id, antes: list[dict]) -> dict:
    """La última salida posterior a `antes` (`_salidas`): el armado del alta usa
    un reloj fijo, así que no se ordena por hora contra lo anterior."""
    vistos = {f["id"] for f in antes}
    with admin(conn) as cur:
        cur.execute(
            """select id, cuerpo, bloque_copiable, pending_action_id,
                      intake_choice_set_id
                 from message_outbox where chat_id = %s
                order by programado_para, id""", (chat_id,))
        filas = [f for f in cur.fetchall() if f["id"] not in vistos]
    assert filas, "no salió ningún mensaje nuevo"
    return filas[-1]


def _despachar(conn, ws, transporte=None):
    transporte = transporte or TransporteDePrueba()
    with espacio(conn, ws) as cur:
        despachar(cur, ws, transporte, Calendario.desde_base(cur, ws))
    return transporte


def _toque_de_modificar(client, conn, user, pid):
    with admin(conn) as cur:
        # Aunque la vista previa ya esté cerrada: un toque tardío usa el mismo
        # botón de siempre.
        cur.execute("select token from pending_action_option "
                    "where pending_action_id = %s and etiqueta = %s",
                    (pid, ETIQUETA_MODIFICAR))
        token = cur.fetchone()["token"]
    return _tocar_boton(client, conn, token, user)


def _modificar(conn, monkeypatch, world, responsable="Sam North"):
    """El alta en confirmación con Modificar ya tocado: el selector abierto.
    Devuelve (request_id, id de la vista previa cerrada, cliente, chat)."""
    rid, pid = _alta_en_confirmacion(conn, world, responsable=responsable)
    user = _usuario(world)
    client = _callback_client(conn, monkeypatch)
    assert _toque_de_modificar(client, conn, user, pid).status_code == 200
    return rid, pid, client, user


def _elegir_dato(conn, client, user, rid, etiqueta):
    opciones = _opciones_activas(conn, rid)
    assert _post_intake_callback(client, opciones[etiqueta], user).status_code == 200


def _responder_con(conn, monkeypatch, world, texto):
    provider = _RoutingProvider([_ruta(RespectoPendiente.RESPONDE)])
    _escribir(conn, monkeypatch, world, provider, texto)
    return provider


# ------------------------------------------------- la vista previa: 3 botones

def test_la_vista_previa_del_alta_ofrece_confirmar_modificar_y_cancelar(
        intake_world, conn):
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")

    assert _etiquetas_de_la_vista_previa(conn, pid) == [
        "Confirmar", "Modificar", "Cancelar"]


def test_si_confirma_otra_persona_su_vista_previa_no_ofrece_modificar(
        intake_world, conn):
    """Quien pidió el borrador no es quien confirma: Modificar es de quien tiene
    la rama abierta, y esa persona no es quien recibe este botón. Lo tuvo antes, en
    su resumen previo al envío (T9-R1c-4, `test_alta_enviar_a_aprobacion.py`)."""
    rid, pid = _alta_enviada(conn, intake_world)

    assert _etiquetas_de_la_vista_previa(conn, pid) == ["Confirmar", "Rechazar"]


# ----------------------------------------------------- tocar Modificar

def test_tocar_modificar_cierra_la_vista_previa_y_pregunta_que_dato_cambiar(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_confirmacion(conn, intake_world)
    user = _usuario(intake_world)
    client = _callback_client(conn, monkeypatch)
    antes = _salidas(conn, user)

    assert _toque_de_modificar(client, conn, user, pid).status_code == 200

    # Nada se aplicó: la vista previa quedó cerrada y sigue sin haber tarea.
    assert [p["estado"] for p in _previews(conn, rid)] == ["cancelada"]
    assert _tareas(conn) == 0
    assert _solicitud(conn, rid) == "active"
    # Una sola respuesta: el selector, con un botón por dato.
    salidas = _nuevas(conn, user, antes)
    assert [f["cuerpo"] for f in salidas] == [I.MODIFY_PICKER_PROMPT]
    assert salidas[0]["intake_choice_set_id"]
    assert list(_opciones_activas(conn, rid)) == ETIQUETAS_DEL_SELECTOR


def test_el_selector_es_la_pregunta_abierta_de_la_rama(intake_world, conn,
                                                       monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)

    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        from leda.autoridad import Canal, identificar
        quien = identificar(cur, user, Canal.ESPACIO,
                            intake_world["north-lab"]["id"])
        pregunta = I.open_intake_question(cur, quien, user)
    assert pregunta["tipo"] == I.QUESTION_CHOICE
    assert pregunta["request_id"] == rid
    assert pregunta["opciones"] == ETIQUETAS_DEL_SELECTOR


def test_modificar_dos_veces_la_segunda_dice_que_ya_no_esta_vigente(
        intake_world, conn, monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    envejecer_toques(conn, FUERA_DE_LA_VENTANA)                  # fuera de la ventana (T9-R4)
    antes = _salidas(conn, user)

    assert _toque_de_modificar(client, conn, user, pid).status_code == 200

    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [AVISO_TOQUE_YA_USADO]
    assert list(_opciones_activas(conn, rid)) == ETIQUETAS_DEL_SELECTOR


def test_modificar_de_una_vista_previa_vencida_dice_que_ya_no_esta_vigente(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_confirmacion(conn, intake_world)
    user = _usuario(intake_world)
    with admin(conn) as cur:
        cur.execute("update pending_action set vence_en = now() - interval '1 minute' "
                    "where id = %s", (pid,))
    client = _callback_client(conn, monkeypatch)
    antes = _salidas(conn, user)

    _toque_de_modificar(client, conn, user, pid)

    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [AVISO_TOQUE_YA_USADO]
    assert _conjunto_activo(conn, rid) is None
    assert _tareas(conn) == 0


def test_modificar_tocado_por_otra_persona_no_abre_nada(intake_world, conn,
                                                        monkeypatch):
    rid, pid = _alta_en_confirmacion(conn, intake_world)
    ajena = intake_world["north-lab"]["people"]["Morgan Hale"]["telegram"]
    client = _callback_client(conn, monkeypatch)
    antes = _salidas(conn, ajena)

    _toque_de_modificar(client, conn, ajena, pid)

    assert [p["estado"] for p in _previews(conn, rid)] == ["esperando"]
    assert _conjunto_activo(conn, rid) is None
    assert [f["cuerpo"] for f in _nuevas(conn, ajena, antes)] == [
        "Eso se lo pregunté a otra persona del equipo."]


# ---------------------------------------------- un dato de texto: copiar y pegar

@pytest.mark.parametrize("campo, etiqueta, actual, nuevo", [
    ("title", "Título", TITULO, "Inspect pressure valve"),
    ("acceptance_criterion", "Criterio de aceptación",
     "Signed test record attached", "Signed and photographed test record"),
    ("due_date", "Fecha objetivo", "29/02/2028", "10/3/2028"),
])
def test_un_dato_de_texto_muestra_lo_que_tenia_en_un_bloque_copiable_y_abre_su_campo(
        campo, etiqueta, actual, nuevo, intake_world, conn, monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    antes = _salidas(conn, user)

    _elegir_dato(conn, client, user, rid, etiqueta)

    salidas = _nuevas(conn, user, antes)
    assert len(salidas) == 1
    fila = _ultima_salida(conn, user, antes)
    assert fila["bloque_copiable"] == actual         # lo que tenía, para copiar
    assert fila["cuerpo"].endswith(actual)
    assert fila["intake_choice_set_id"] is None and fila["pending_action_id"] is None
    # El campo queda abierto: el mensaje siguiente lo reemplaza.
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        from leda.autoridad import Canal, identificar
        quien = identificar(cur, user, Canal.ESPACIO,
                            intake_world["north-lab"]["id"])
        pregunta = I.open_intake_question(cur, quien, user)
    assert pregunta["tipo"] == I.QUESTION_FREE_TEXT and pregunta["campo"] == campo
    assert _tareas(conn) == 0


@pytest.mark.parametrize("campo, etiqueta, actual, nuevo", [
    ("title", "Título", TITULO, "Inspect pressure valve"),
    ("acceptance_criterion", "Criterio de aceptación",
     "Signed test record attached", "Signed and photographed test record"),
    ("due_date", "Fecha objetivo", "29/02/2028", "10/3/2028"),
])
def test_el_dato_corregido_cambia_solo_ese_dato_y_vuelve_la_vista_previa(
        campo, etiqueta, actual, nuevo, intake_world, conn, monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    _elegir_dato(conn, client, user, rid, etiqueta)
    campos_antes = _campos(conn, rid)
    antes = _salidas(conn, user)

    provider = _responder_con(conn, monkeypatch, intake_world, nuevo)

    campos_despues = _campos(conn, rid)
    cambiados = {c for c in campos_antes if campos_antes[c] != campos_despues[c]}
    assert cambiados == {campo}                        # sólo ese dato
    assert provider.main_calls == 0
    # La vista previa vuelve actualizada, con los mismos tres botones.
    previews = _previews(conn, rid)
    assert [p["estado"] for p in previews] == ["cancelada", "esperando"]
    nueva = previews[-1]
    valor = campos_despues[campo][1]
    if campo == "due_date":
        assert valor == "2028-03-10"                   # se guarda como fecha...
        valor = "10/03/2028"                           # ...y se muestra en formato de persona
    assert valor != actual and str(valor) in nueva["resumen"]
    assert _etiquetas_de_la_vista_previa(conn, nueva["id"]) == [
        "Confirmar", "Modificar", "Cancelar"]
    salidas = _nuevas(conn, user, antes)
    assert [str(f["pending_action_id"]) for f in salidas] == [str(nueva["id"])]
    # Ninguna tarea sin Confirmar.
    assert _tareas(conn) == 0 and _solicitud(conn, rid) == "active"


def test_una_fecha_corregida_pasa_por_su_resolucion_de_siempre(
        intake_world, conn, monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    _elegir_dato(conn, client, user, rid, "Fecha objetivo")
    antes = _salidas(conn, user)

    _responder_con(conn, monkeypatch, intake_world, "quizás pronto")

    # Ambigua: el campo sigue abierto y la vista previa no volvió.
    assert _campos(conn, rid)["due_date"][1] == "2028-02-29"
    assert [p["estado"] for p in _previews(conn, rid)] == ["cancelada"]
    assert _ultima_salida(conn, user, antes)["cuerpo"].startswith("La fecha")


def test_un_dato_corregido_demasiado_largo_deja_el_campo_abierto(
        intake_world, conn, monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    _elegir_dato(conn, client, user, rid, "Título")
    antes = _salidas(conn, user)

    _responder_con(conn, monkeypatch, intake_world,
                   "x" * (I.USER_FIELD_LIMITS["title"] + 1))

    assert _campos(conn, rid)["title"][1] == TITULO
    assert _ultima_salida(conn, user, antes)["cuerpo"] == I._user_limit_prompt("title")
    with admin(conn) as cur:
        cur.execute("select count(*) n from task_intake_free_text_slot "
                    "where request_id = %s and estado = 'active'", (rid,))
        assert cur.fetchone()["n"] == 1


def test_una_descripcion_vacia_no_muestra_bloque_y_se_puede_agregar(
        intake_world, conn, monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    assert _campos(conn, rid)["description"][1] == ""
    antes = _salidas(conn, user)

    _elegir_dato(conn, client, user, rid, "Descripción")

    fila = _ultima_salida(conn, user, antes)
    assert fila["bloque_copiable"] is None
    _responder_con(conn, monkeypatch, intake_world, "Revisar la válvula de alivio")
    assert _campos(conn, rid)["description"][1] == "Revisar la válvula de alivio"
    assert _previews(conn, rid)[-1]["estado"] == "esperando"


@pytest.mark.parametrize("largo, con_boton", [(COPY_TEXT_LIMIT, True),
                                              (COPY_TEXT_LIMIT + 1, False)])
def test_el_boton_de_copiar_esta_hasta_256_caracteres_y_el_bloque_siempre(
        largo, con_boton, intake_world, conn, monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    descripcion = "d" * largo
    with admin(conn) as cur:
        cur.execute("""update task_intake_field set valor = to_jsonb(%s::text)
                        where request_id = %s and campo = 'description'""",
                    (descripcion, rid))
    _elegir_dato(conn, client, user, rid, "Descripción")

    transporte = _despachar(conn, intake_world["north-lab"]["id"])

    enviado = [e for e in transporte.enviados if e.bloque == descripcion]
    assert len(enviado) == 1
    assert enviado[0].texto.endswith(descripcion)
    assert [b.etiqueta for b in enviado[0].botones] == (
        [ETIQUETA_COPIAR] if con_boton else [])


# ---------------------------------------- un dato con opciones: sus botones

def test_un_dato_con_opciones_vuelve_a_mostrar_sus_botones(intake_world, conn,
                                                            monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    antes = _salidas(conn, user)

    _elegir_dato(conn, client, user, rid, "Objetivo")

    salidas = _nuevas(conn, user, antes)
    assert len(salidas) == 1 and salidas[0]["intake_choice_set_id"]
    opciones = _opciones_activas(conn, rid)
    assert any("Raise delivery quality" in e for e in opciones)
    assert any("Reduce service delay" in e for e in opciones)
    assert _conjunto_activo(conn, rid)["campo"] == "objective"
    assert _tareas(conn) == 0


def test_elegir_otro_objetivo_cambia_solo_el_objetivo_y_vuelve_la_vista_previa(
        intake_world, conn, monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    campos_antes = _campos(conn, rid)
    _elegir_dato(conn, client, user, rid, "Objetivo")
    otro = next(t for e, t in _opciones_activas(conn, rid).items()
                if "Raise delivery quality" in e)

    assert _post_intake_callback(client, otro, user).status_code == 200

    campos_despues = _campos(conn, rid)
    assert {c for c in campos_antes if campos_antes[c] != campos_despues[c]} == {
        "objective"}
    assert campos_despues["objective"][1]["title"] == "Raise delivery quality 1"
    previews = _previews(conn, rid)
    assert [p["estado"] for p in previews] == ["cancelada", "esperando"]
    assert "Raise delivery quality 1" in previews[-1]["resumen"]
    assert _etiquetas_de_la_vista_previa(conn, previews[-1]["id"]) == [
        "Confirmar", "Modificar", "Cancelar"]
    assert _tareas(conn) == 0


def test_elegir_un_responsable_de_otra_area_pide_el_area_y_vuelve_la_vista_previa(
        intake_world, conn, monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    _elegir_dato(conn, client, user, rid, "Responsable")
    noble = next(t for e, t in _opciones_activas(conn, rid).items()
                 if "Sam Noble" in e)

    _post_intake_callback(client, noble, user)

    # Su área es otra: el alta la vuelve a pedir, como siempre.
    assert _conjunto_activo(conn, rid)["campo"] == "area"
    area = next(t for e, t in _opciones_activas(conn, rid).items()
                if "Quality Guild" in e)
    _post_intake_callback(client, area, user)

    campos = _campos(conn, rid)
    assert campos["responsible"][1]["name"] == "Sam Noble 1"
    assert campos["area"][1]["name"] == "Quality Guild"
    assert _previews(conn, rid)[-1]["estado"] == "esperando"
    assert "Sam Noble 1" in _previews(conn, rid)[-1]["resumen"]


def test_modificar_el_area_vuelve_a_mostrar_su_opcion(intake_world, conn,
                                                      monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)

    _elegir_dato(conn, client, user, rid, "Área")

    assert _conjunto_activo(conn, rid)["campo"] == "area"
    assert any("Field Services" in e for e in _opciones_activas(conn, rid))


# ----------------------------------------------- escribir `corrige` en la vista previa

def test_corrige_sobre_la_vista_previa_lleva_al_selector(intake_world, conn,
                                                         monkeypatch):
    rid, pid = _alta_en_confirmacion(conn, intake_world)
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(RespectoPendiente.CORRIGE)])

    _escribir(conn, monkeypatch, intake_world, provider,
              "cambiá la fecha para el viernes")

    assert [p["estado"] for p in _previews(conn, rid)] == ["cancelada"]
    assert _tareas(conn) == 0 and _solicitud(conn, rid) == "active"
    salidas = _nuevas(conn, user, antes)
    assert [f["cuerpo"] for f in salidas] == [I.MODIFY_PICKER_PROMPT]
    assert list(_opciones_activas(conn, rid)) == ETIQUETAS_DEL_SELECTOR
    assert provider.main_calls == 0


# --------------------------------------------- una sola rama abierta

def test_otro_tema_en_el_selector_pregunta_por_la_rama_y_no_abre_otra(
        intake_world, conn, monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(RespectoPendiente.OTRO_TEMA)])

    _escribir(conn, monkeypatch, intake_world, provider, "¿qué es un bloqueo?")

    salidas = _nuevas(conn, user, antes)
    assert len(salidas) == 1
    assert salidas[0]["cuerpo"] == gateway.PREGUNTA_RAMA_ABIERTA.format(
        nombre="qué dato cambiar del borrador de la tarea nueva")
    assert provider.main_calls == 0
    assert list(_opciones_activas(conn, rid)) == ETIQUETAS_DEL_SELECTOR


def test_otro_tema_en_la_pregunta_del_dato_pregunta_por_la_rama(
        intake_world, conn, monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    _elegir_dato(conn, client, user, rid, "Título")
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(RespectoPendiente.OTRO_TEMA)])

    _escribir(conn, monkeypatch, intake_world, provider, "¿qué es un bloqueo?")

    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [
        gateway.PREGUNTA_RAMA_ABIERTA.format(
            nombre="el título de la tarea nueva")]
    assert _campos(conn, rid)["title"][1] == TITULO


def test_un_dato_escrito_en_el_selector_elige_ese_dato(intake_world, conn,
                                                       monkeypatch):
    """El selector es una elección con botones: escribir exactamente una de sus
    opciones es tocarla."""
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    antes = _salidas(conn, user)

    _responder_con(conn, monkeypatch, intake_world, "título")

    fila = _ultima_salida(conn, user, antes)
    assert fila["bloque_copiable"] == TITULO


# ------------------------------------------------------ botones que ya no valen

def test_tocar_dos_veces_el_mismo_dato_del_selector_dice_que_ya_no_esta_vigente(
        intake_world, conn, monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    token = _opciones_activas(conn, rid)["Título"]
    assert _post_intake_callback(client, token, user).status_code == 200
    envejecer_toques(conn, FUERA_DE_LA_VENTANA)                  # fuera de la ventana (T9-R4)
    antes = _salidas(conn, user)

    assert _post_intake_callback(client, token, user).status_code == 200

    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [AVISO_TOQUE_YA_USADO]


def test_un_boton_del_selector_de_antes_ya_no_vale_despues_de_cerrarlo(
        intake_world, conn, monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    viejo = _opciones_activas(conn, rid)["Objetivo"]
    _elegir_dato(conn, client, user, rid, "Título")     # el selector se consume
    _responder_con(conn, monkeypatch, intake_world, "Inspect pressure valve")
    antes = _salidas(conn, user)

    _post_intake_callback(client, viejo, user)

    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [AVISO_TOQUE_YA_USADO]
    assert _conjunto_activo(conn, rid) is None
    assert _tareas(conn) == 0


# ------------------------------------ sólo Confirmar convierte el borrador

def test_solo_confirmar_convierte_y_lo_hace_con_el_dato_corregido(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    _elegir_dato(conn, client, user, rid, "Título")
    _responder_con(conn, monkeypatch, intake_world, "Inspect pressure valve")
    ws = intake_world["north-lab"]["id"]
    nueva = _previews(conn, rid)[-1]["id"]
    with espacio(conn, ws) as cur:
        confirmar = P.opcion_por_etiqueta(cur, nueva, "Confirmar").token
        cur.execute(
            """select o.token from pending_action_option o
                where o.pending_action_id = %s and o.valor = 'true'::jsonb""",
            (pid,))
        viejo_confirmar = cur.fetchone()["token"]
    conn.commit()
    assert _tareas(conn) == 0                      # todo lo anterior: sin efecto

    with autoridad(authority_conn) as cur:
        # El botón de la vista previa anterior no convierte nada.
        assert P.resolver_borrador(cur, ws, viejo_confirmar, user, user) is None
    assert _tareas(conn) == 0
    with autoridad(authority_conn) as cur:
        resuelta = P.resolver_borrador(cur, ws, confirmar, user, user)

    assert resuelta and resuelta.task_id
    with admin(conn) as cur:
        cur.execute("select titulo from task")
        assert [f["titulo"] for f in cur.fetchall()] == ["Inspect pressure valve"]
    assert _solicitud(conn, rid) == "converted"


def test_cancelar_despues_de_modificar_cancela_el_borrador(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    _elegir_dato(conn, client, user, rid, "Título")
    _responder_con(conn, monkeypatch, intake_world, "Inspect pressure valve")
    ws = intake_world["north-lab"]["id"]
    nueva = _previews(conn, rid)[-1]["id"]
    with admin(conn) as cur:
        cancelar = P.opcion_por_etiqueta(cur, nueva, "Cancelar").token

    with autoridad(authority_conn) as cur:
        resuelta = P.resolver_borrador(cur, ws, cancelar, user, user)

    assert resuelta is not None and resuelta.cancelada
    assert _solicitud(conn, rid) == "cancelled"
    assert _tareas(conn) == 0
    assert _previews(conn, rid)[-1]["estado"] == "cancelada"


# ------------------------- la vista previa que responde a un acto es una respuesta

def _es_respuesta(conn, pid) -> bool:
    with admin(conn) as cur:
        cur.execute("select es_respuesta from message_outbox "
                    "where pending_action_id = %s", (pid,))
        return cur.fetchone()["es_respuesta"]


def _calendario_cerrado(conn, ws) -> Calendario:
    """Sin ningún día hábil: todo lo que inicia Leda queda fuera de horario."""
    with espacio(conn, ws) as cur:
        zona = Calendario.desde_base(cur, ws).zona
    return Calendario(frozenset(), time(9), time(18), frozenset(), zona)


def _despachar_fuera_de_horario(conn, ws):
    transporte = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        despachar(cur, ws, transporte, _calendario_cerrado(conn, ws))
    conn.commit()
    return transporte


def test_la_vista_previa_que_sigue_a_modificar_es_una_respuesta_y_sale_fuera_de_horario(
        intake_world, conn, monkeypatch):
    """Quien corrige un dato es quien confirma: la vista previa actualizada le
    contesta a ese acto (ADR 0013 regla 2), sin horario ni tope diario."""
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    _elegir_dato(conn, client, user, rid, "Título")
    _responder_con(conn, monkeypatch, intake_world, "Inspect pressure valve")
    nueva = _previews(conn, rid)[-1]

    assert _es_respuesta(conn, nueva["id"]) is True
    transporte = _despachar_fuera_de_horario(conn, intake_world["north-lab"]["id"])

    resumenes = [e for e in transporte.enviados
                 if e.texto.startswith("Resumen para revisar")]
    assert len(resumenes) == 1 and "Inspect pressure valve" in resumenes[0].texto


def test_la_vista_previa_del_alta_de_quien_la_confirma_es_una_respuesta(
        intake_world, conn):
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")

    assert _es_respuesta(conn, pid) is True


def test_si_confirma_otra_persona_su_vista_previa_la_inicia_leda(
        intake_world, conn):
    """Para el aprobador es un mensaje que Leda le inicia: horario y tope."""
    rid, pid = _alta_enviada(conn, intake_world)

    assert _es_respuesta(conn, pid) is False
    transporte = _despachar_fuera_de_horario(conn, intake_world["north-lab"]["id"])
    assert [e for e in transporte.enviados
            if e.texto.startswith("Resumen para revisar")] == []


def test_un_dato_sin_fila_en_la_solicitud_no_rompe_y_pregunta_como_si_estuviera_vacio(
        intake_world, conn, monkeypatch):
    """Un campo sin `task_intake_field` (valor vacío): sin nada que copiar, la
    pregunta de siempre del campo y su campo abierto; ningún error."""
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    with admin(conn) as cur:
        cur.execute("delete from task_intake_field where request_id = %s "
                    "and campo = 'title'", (rid,))
    antes = _salidas(conn, user)

    _elegir_dato(conn, client, user, rid, "Título")

    fila = _ultima_salida(conn, user, antes)
    assert fila["bloque_copiable"] is None
    assert fila["cuerpo"] == I.free_text_question("title")
    with admin(conn) as cur:
        cur.execute("select count(*) n from task_intake_free_text_slot "
                    "where request_id = %s and estado = 'active'", (rid,))
        assert cur.fetchone()["n"] == 1


# ------------------------------------------- la fecha, en el formato de la persona

def test_la_vista_previa_muestra_la_fecha_en_el_formato_de_la_persona_no_iso(
        intake_world, conn):
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")

    with admin(conn) as cur:
        cur.execute("select resumen from pending_action where id = %s", (pid,))
        resumen = cur.fetchone()["resumen"]
    assert "Fecha objetivo: 29/02/2028\n" in resumen
    assert "2028-02-29" not in resumen
    assert _campos(conn, rid)["due_date"][1] == "2028-02-29"     # se guarda como fecha


def test_la_fecha_del_bloque_copiable_se_pega_de_vuelta_sin_cambiar_nada(
        intake_world, conn, monkeypatch):
    """Lo que la persona pega es lo que se le mostró: la resolución de fechas de
    siempre lo entiende y la fecha guardada no cambia."""
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    antes = _salidas(conn, user)
    _elegir_dato(conn, client, user, rid, "Fecha objetivo")
    bloque = _ultima_salida(conn, user, antes)["bloque_copiable"]
    assert bloque == "29/02/2028"

    _responder_con(conn, monkeypatch, intake_world, bloque)

    assert _campos(conn, rid)["due_date"] == ("confirmed", "2028-02-29")
    assert _previews(conn, rid)[-1]["estado"] == "esperando"


# -------------------------- volver a preguntar un dato de Modificar trae el bloque

@pytest.mark.parametrize("comando, prefijo", [
    (RespectoPendiente.CHARLA, ""),
    (RespectoPendiente.NO_PUEDO, gateway.AVISO_NO_PUEDO_DATO_PENDIENTE + " "),
])
@pytest.mark.parametrize("etiqueta, actual, campo, guardado", [
    ("Título", TITULO, "title", TITULO),
    ("Fecha objetivo", "29/02/2028", "due_date", "2028-02-29")])
def test_repreguntar_un_dato_de_modificar_tras_una_charla_vuelve_con_su_bloque(
        comando, prefijo, etiqueta, actual, campo, guardado, intake_world, conn,
        monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    _elegir_dato(conn, client, user, rid, etiqueta)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(comando)])

    _escribir(conn, monkeypatch, intake_world, provider, "hola, ¿cómo va?")

    assert len(_nuevas(conn, user, antes)) == 1          # una sola respuesta visible
    fila = _ultima_salida(conn, user, antes)
    assert fila["bloque_copiable"] == actual             # lo que tenía, para copiar
    assert fila["cuerpo"].startswith(prefijo) and fila["cuerpo"].endswith(actual)
    assert provider.main_calls == 0
    # El campo que se parametriza (el título o la fecha) sigue sin cambiar y su
    # espacio de texto libre sigue activo: el mensaje siguiente lo reemplaza.
    assert _campos(conn, rid)[campo] == ("confirmed", guardado)
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        from leda.autoridad import Canal, identificar
        quien = identificar(cur, user, Canal.ESPACIO,
                            intake_world["north-lab"]["id"])
        pregunta = I.open_intake_question(cur, quien, user)
    assert pregunta["tipo"] == I.QUESTION_FREE_TEXT and pregunta["campo"] == campo


def test_repreguntar_un_dato_del_alta_que_no_es_de_modificar_no_lleva_bloque(
        intake_world, conn, monkeypatch):
    """Un campo todavía sin confirmar no tiene nada que copiar."""
    user = _usuario(intake_world)
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        actor, outcome = _start(cur, intake_world, chat_id=user)
        _choose(cur, actor, outcome.request_id, "No", chat_id=user)   # rechaza el título
        pregunta = I.open_intake_question(cur, actor, user)
        assert pregunta["tipo"] == I.QUESTION_FREE_TEXT
        assert pregunta["campo"] == "title" and pregunta["bloque"] is None
    conn.commit()
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(RespectoPendiente.CHARLA)])

    _escribir(conn, monkeypatch, intake_world, provider, "hola")

    fila = _ultima_salida(conn, user, antes)
    assert fila["bloque_copiable"] is None
    assert fila["cuerpo"] == I.free_text_question("title")


# --------------------------------------------- [Volver al resumen] en el selector

def _tocar_volver(conn, client, user, rid):
    return _elegir_dato(conn, client, user, rid, "Volver al resumen")


def test_el_selector_ofrece_un_boton_por_dato_y_volver_al_resumen(
        intake_world, conn, monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)

    assert list(_opciones_activas(conn, rid)) == ETIQUETAS_DE_LOS_DATOS + [
        "Volver al resumen"]


def test_volver_al_resumen_muestra_la_vista_previa_actual_sin_cambiar_nada(
        intake_world, conn, monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    campos_antes = _campos(conn, rid)
    resumen_antes = _previews(conn, rid)[0]["resumen"]
    antes = _salidas(conn, user)

    _tocar_volver(conn, client, user, rid)

    assert _campos(conn, rid) == campos_antes                 # nada cambió
    previews = _previews(conn, rid)
    assert [p["estado"] for p in previews] == ["cancelada", "esperando"]
    assert previews[-1]["resumen"] == resumen_antes           # el mismo resumen
    assert _etiquetas_de_la_vista_previa(conn, previews[-1]["id"]) == [
        "Confirmar", "Modificar", "Cancelar"]
    salidas = _nuevas(conn, user, antes)                      # una sola respuesta
    assert [str(f["pending_action_id"]) for f in salidas] == [str(previews[-1]["id"])]
    assert _es_respuesta(conn, previews[-1]["id"]) is True
    assert _conjunto_activo(conn, rid) is None                # el selector se cerró
    assert _tareas(conn) == 0 and _solicitud(conn, rid) == "active"


def test_volver_al_resumen_escrito_es_tocar_el_boton(intake_world, conn, monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    campos_antes = _campos(conn, rid)
    antes = _salidas(conn, user)

    provider = _responder_con(conn, monkeypatch, intake_world, "volver al resumen")

    assert provider.main_calls == 0
    assert _campos(conn, rid) == campos_antes
    previews = _previews(conn, rid)
    assert [p["estado"] for p in previews] == ["cancelada", "esperando"]
    assert [str(f["pending_action_id"]) for f in _nuevas(conn, user, antes)] == [
        str(previews[-1]["id"])]


def test_volver_al_resumen_dos_veces_dice_que_ya_no_esta_vigente(
        intake_world, conn, monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    token = _opciones_activas(conn, rid)["Volver al resumen"]
    assert _post_intake_callback(client, token, user).status_code == 200
    envejecer_toques(conn, FUERA_DE_LA_VENTANA)                  # fuera de la ventana (T9-R4)
    antes = _salidas(conn, user)

    assert _post_intake_callback(client, token, user).status_code == 200

    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [AVISO_TOQUE_YA_USADO]
    assert [p["estado"] for p in _previews(conn, rid)] == ["cancelada", "esperando"]


def test_un_boton_del_selector_de_antes_no_vale_despues_de_volver_al_resumen(
        intake_world, conn, monkeypatch):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    viejo = _opciones_activas(conn, rid)["Título"]
    _tocar_volver(conn, client, user, rid)
    antes = _salidas(conn, user)

    _post_intake_callback(client, viejo, user)

    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [AVISO_TOQUE_YA_USADO]
    assert _conjunto_activo(conn, rid) is None


def test_despues_de_volver_al_resumen_solo_confirmar_crea_la_tarea(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid, client, user = _modificar(conn, monkeypatch, intake_world)
    _tocar_volver(conn, client, user, rid)
    ws = intake_world["north-lab"]["id"]
    nueva = _previews(conn, rid)[-1]["id"]
    with admin(conn) as cur:
        confirmar = P.opcion_por_etiqueta(cur, nueva, "Confirmar").token
    assert _tareas(conn) == 0

    with autoridad(authority_conn) as cur:
        resuelta = P.resolver_borrador(cur, ws, confirmar, user, user)

    assert resuelta and resuelta.task_id
    with admin(conn) as cur:
        cur.execute("select titulo from task")
        assert [f["titulo"] for f in cur.fetchall()] == [TITULO]


# ---------------- seguimiento de review-5125015caf2e7767: una fecha vacía no es "None"

@pytest.mark.parametrize("vacia", [None, "", "   "])
def test_una_fecha_objetivo_vacia_no_se_muestra_como_la_palabra_none(vacia):
    from leda import ingreso_tareas as I

    assert I.format_due_date(vacia) == ""
    vista = I.render_preview(
        title="T", description="", objective="O", area="A", responsible="R",
        due_date=I.format_due_date(vacia), acceptance_criterion="C",
        evidence=["explicacion"])
    assert "None" not in vista


def test_una_fecha_iso_sigue_mostrandose_como_dia_mes_anio():
    from leda import ingreso_tareas as I

    assert I.format_due_date("2028-02-29") == "29/02/2028"
    assert I.format_due_date("pasado mañana") == "pasado mañana"   # no ISO: tal cual
