"""El alta conducida por el modelo, esqueleto andante (ADR 0014, enmienda del
2026-10-01, M3).

Con el ajuste del espacio `alta = conversada`, cada turno del alta (un mensaje o un
toque dentro de ella) es UNA llamada al modelo con la conversación y el borrador: el
código valida cada valor, guarda lo válido, pone los botones y el resumen exacto, y
nada se compromete sin Confirmar. Sin el ajuste, el alta guiada de siempre.

El modelo se guiona (`ProveedorGuionado.conducciones`); ninguna prueba toca la red.
Todo pasa por el webhook real (`TestClient`): mensajes y toques.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
from psycopg.types.json import Jsonb

from prisma import alta_conducida as AC
from prisma import gateway, incidentes
from prisma import ingreso_tareas as I
from prisma.db import admin, espacio
from prisma.incidentes import NOTICIA_NEUTRA_INCIDENTE
from prisma.llm import (IntentAction, IntentRoute, ProveedorGuionado,
                        Respuesta)

from tests.test_alta_eleccion_confirmacion import (
    _campo, _escribir, _nuevas, _salidas, _solicitud, _usuario)
from tests.test_task_intake import _callback_client, _post_intake_callback

ZONA = "America/Argentina/Buenos_Aires"
_toques = iter(range(1, 10_000))


# ------------------------------------------------------------------- andamiaje

def _hoy():
    return datetime.now(ZoneInfo(ZONA)).date()


def _en(dias: int) -> str:
    return (_hoy() + timedelta(days=dias)).isoformat()


def salida(texto="Dale.", intencion="continuar", **campos) -> dict:
    return {"intencion": intencion, "texto": texto, **campos}


def _modelo(*conducciones, rutas=None, respuestas=None) -> ProveedorGuionado:
    return ProveedorGuionado(
        guion=[Respuesta(texto=t) for t in (respuestas or [])],
        rutas=list(rutas if rutas is not None
                   else [IntentRoute(IntentAction.START_TASK_INTAKE)]),
        conducciones=list(conducciones))


@pytest.fixture
def conversada(intake_world, conn, monkeypatch):
    """El espacio con `alta = conversada` y sin Jev (el orden de los objetivos es
    el de la base: ninguno sugerido)."""
    with admin(conn) as cur:
        cur.execute(
            "insert into workspace_setting (workspace_id, clave, valor) "
            "values (%s, 'alta', %s)",
            (intake_world["north-lab"]["id"], Jsonb("conversada")))
    conn.commit()
    monkeypatch.setattr(I, "_ordenar_objetivos",
                        lambda cur, request, who, candidatas: (candidatas, False))
    return intake_world


class Chat:
    """Una persona (Taylor Quinn) conversando con Prisma por el webhook."""

    def __init__(self, conn, monkeypatch, world, modelo):
        self.conn, self.monkeypatch, self.world, self.modelo = (
            conn, monkeypatch, world, modelo)
        self.usuario = _usuario(world)
        self.cliente = None

    def escribir(self, texto: str) -> list[dict]:
        """Lo que salió como respuesta a ese mensaje."""
        antes = _salidas(self.conn, self.usuario)
        _escribir(self.conn, self.monkeypatch, self.world, self.modelo, texto)
        return _nuevas(self.conn, self.usuario, antes)

    def tocar(self, parte: str) -> list[dict]:
        antes = _salidas(self.conn, self.usuario)
        self.cliente = self.cliente or _callback_client(self.conn, self.monkeypatch)
        self.monkeypatch.setattr("prisma.llm.desde_base", lambda *a: self.modelo)
        respuesta = _post_intake_callback(
            self.cliente, self.token(parte), self.usuario,
            callback_id=f"cb-{next(_toques)}")
        assert respuesta.status_code == 200
        return _nuevas(self.conn, self.usuario, antes)

    def token(self, parte: str) -> str:
        with admin(self.conn) as cur:
            cur.execute(
                """select c.token, c.etiqueta from task_intake_choice c
                     join task_intake_choice_set s on s.id = c.choice_set_id
                    where s.estado = 'active' and c.activa""")
            filas = cur.fetchall()
        (token,) = [f["token"] for f in filas if parte in f["etiqueta"]]
        return token

    def etiquetas(self) -> list[str]:
        with admin(self.conn) as cur:
            cur.execute(
                """select c.etiqueta from task_intake_choice c
                     join task_intake_choice_set s on s.id = c.choice_set_id
                    where s.estado = 'active' and c.activa order by c.orden""")
            return [f["etiqueta"] for f in cur.fetchall()]

    def hechos(self, n: int = -1) -> dict:
        return json.loads(self.modelo.conducidos[n][2])

    def id_de(self, campo: str, nombre: str, n: int = -1) -> str:
        clave = "titulo" if campo == "objective" else "nombre"
        return next(o["id"] for o in self.hechos(n)["opciones"][campo]
                    if nombre in o[clave])

    @property
    def rid(self) -> str:
        with admin(self.conn) as cur:
            cur.execute("select id from task_intake_request "
                        "order by creado_en desc limit 1")
            return str(cur.fetchone()["id"])

    def campo(self, campo: str) -> dict:
        return _campo(self.conn, self.rid, campo)

    def estado(self) -> str:
        return _solicitud(self.conn, self.rid)

    def incidentes(self, etapa: str) -> list[dict]:
        with admin(self.conn) as cur:
            cur.execute("select * from incident where etapa = %s", (etapa,))
            return cur.fetchall()


@pytest.fixture
def chat(conversada, conn, monkeypatch):
    def armar(*conducciones, **kwargs) -> Chat:
        return Chat(conn, monkeypatch, conversada, _modelo(*conducciones, **kwargs))

    return armar


def _cuerpos(salidas) -> list[str]:
    return [f["cuerpo"] for f in salidas]


# ------------------------------------------------------------------ el interruptor

def _poner(conn, world, valor):
    with admin(conn) as cur:
        cur.execute("delete from workspace_setting where clave = 'alta'")
        if valor is not None:
            cur.execute(
                "insert into workspace_setting (workspace_id, clave, valor) "
                "values (%s, 'alta', %s)",
                (world["north-lab"]["id"], Jsonb(valor)))
    conn.commit()


@pytest.mark.parametrize("valor,activo", [
    (None, False), ("conversada", True), ({"modo": "conversada"}, True),
    ("guiada", False), ({"modo": "guiada"}, False)])
def test_el_interruptor_lee_el_ajuste_del_espacio(valor, activo, intake_world, conn):
    _poner(conn, intake_world, valor)
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        assert AC.alta_conducida(cur, intake_world["north-lab"]["id"]) is activo


def test_un_valor_desconocido_es_el_alta_de_siempre_y_queda_un_incidente(
        intake_world, conn):
    _poner(conn, intake_world, "inventada")
    ws = intake_world["north-lab"]["id"]
    AC._anomalias_reportadas.clear()
    with espacio(conn, ws) as cur:
        assert AC.alta_conducida(cur, ws) is False
        assert AC.alta_conducida(cur, ws) is False          # se avisa una vez
    with admin(conn) as cur:
        cur.execute("select etapa from incident where etapa = %s",
                    (incidentes.ETAPA_INTERRUPTOR_ALTA,))
        assert len(cur.fetchall()) == 1


def test_sin_el_ajuste_el_alta_es_la_guiada_de_siempre(
        intake_world, conn, monkeypatch):
    modelo = _modelo()                       # sin conducciones: si se llama, falla
    chat = Chat(conn, monkeypatch, intake_world, modelo)

    nuevas = chat.escribir("necesito crear una tarea")

    assert _cuerpos(nuevas) == ["¿Qué hay que hacer?"]
    assert modelo.conducidos == []


# ----------------------------------------------- el primer mensaje, varios datos

def test_el_primer_mensaje_captura_todos_los_datos_que_trae(chat):
    c = chat(salida(
        "Anotado. ¿A qué objetivo pertenece?",
        valores={"title": {"texto": "Calibrar los sensores"},
                 "due_date": {"fecha_iso": _en(3)},
                 "responsible": {"opcion_id": "R1"}},
        pregunta=["objective"], botones="objective"))

    nuevas = c.escribir("necesito crear una tarea: calibrar los sensores, "
                        "la hago yo para el viernes")

    assert c.campo("title")["valor"] == "Calibrar los sensores"
    assert c.campo("due_date")["valor"] == _en(3)
    assert c.campo("responsible")["valor"]["name"].startswith("Taylor Quinn")
    assert c.campo("objective")["estado"] == "missing"
    # Una sola respuesta: el texto del modelo con los botones del objetivo.
    assert _cuerpos(nuevas) == ["Anotado. ¿A qué objetivo pertenece?"]
    assert nuevas[0]["intake_choice_set_id"] is not None
    assert len(c.etiquetas()) == 3
    assert len(c.modelo.conducidos) == 1
    hechos = c.hechos(0)
    assert hechos["evento"] == {"mensaje_de_la_persona":
                                "necesito crear una tarea: calibrar los sensores, "
                                "la hago yo para el viernes"}
    assert hechos["faltan"][0] == "title"


def test_el_modelo_ve_la_conversacion_el_borrador_y_las_opciones_sin_ids_reales(
        chat):
    c = chat(salida("¿Qué hay que hacer?", pregunta=["title"]))

    c.escribir("quiero crear una tarea")

    sistema, historial, crudo = c.modelo.conducidos[0]
    assert "conducir_alta" in sistema
    assert any(m["content"] == "quiero crear una tarea" for m in historial) is False
    hechos = json.loads(crudo)
    assert set(hechos["opciones"]) == {"objective", "responsible"}
    assert all(o["id"].startswith("O") for o in hechos["opciones"]["objective"])
    assert all(o["id"].startswith("R") for o in hechos["opciones"]["responsible"])
    assert sum(1 for o in hechos["opciones"]["responsible"]
               if o.get("es_quien_escribe")) == 1
    import re
    assert re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-", crudo) is None


def test_el_historial_de_la_conversacion_llega_al_modelo(chat, conn):
    c = chat(salida("¿Qué hay que hacer?", pregunta=["title"]),
             salida("Dale. ¿Para cuándo?",
                    valores={"title": {"texto": "Calibrar"}},
                    pregunta=["objective"], botones="objective"))
    c.escribir("quiero crear una tarea")
    with admin(conn) as cur:
        cur.execute("update message_outbox set estado = 'enviado', enviado_en = now() "
                    "where chat_id = %s", (c.usuario,))
    conn.commit()

    c.escribir("calibrar")

    historial = c.modelo.conducidos[1][1]
    assert historial[0] == {"role": "user", "content": "quiero crear una tarea"}
    assert historial[1] == {"role": "assistant", "content": "¿Qué hay que hacer?"}
    assert all(m["content"] != "calibrar" for m in historial)    # el actual va en los hechos


def test_los_datos_pueden_llegar_en_cualquier_orden_en_mensajes_siguientes(chat):
    c = chat(
        salida("¿Qué hay que hacer?", pregunta=["title"]),
        salida("Listo. ¿Quién la hace?", valores={
            "acceptance_criterion": {"texto": "Informe firmado por calidad",
                                     "verificable": "si"},
            "due_date": {"fecha_iso": _en(5)}},
            pregunta=["title"]))
    c.escribir("quiero crear una tarea")

    c.escribir("el informe firmado por calidad, para el lunes")

    assert c.campo("acceptance_criterion")["valor"] == "Informe firmado por calidad"
    assert c.campo("acceptance_criterion")["proposed_by"] == "user"
    assert c.campo("due_date")["estado"] == "confirmed"
    assert c.campo("title")["estado"] == "missing"


# ------------------------------------------------------------------ los toques

def _alta_hasta_objetivo(chat):
    c = chat(salida(
        "Anotado. ¿A qué objetivo pertenece?",
        valores={"title": {"texto": "Calibrar los sensores"},
                 "due_date": {"fecha_iso": _en(3)},
                 "responsible": {"opcion_id": "R1"}},
        pregunta=["objective"], botones="objective"))
    c.escribir("necesito crear una tarea: calibrar los sensores")
    return c


def test_un_toque_lo_responde_el_modelo_y_guarda_la_opcion_elegida(chat):
    c = _alta_hasta_objetivo(chat)
    c.modelo.conducciones.append(salida(
        "Perfecto. ¿Cómo se sabe que está terminada?",
        pregunta=["acceptance_criterion"]))

    nuevas = c.tocar("Reduce service delay")

    objetivo = c.campo("objective")
    assert objetivo["estado"] == "confirmed" and objetivo["proposed_by"] == "server"
    assert objetivo["valor"]["title"].startswith("Reduce service delay")
    assert objetivo["source_choice_id"] is not None
    assert _cuerpos(nuevas) == ["Perfecto. ¿Cómo se sabe que está terminada?"]
    hechos = c.hechos()
    assert hechos["evento"]["toque"] == "objective"
    assert hechos["evento"]["elegida"].startswith("Reduce service delay")
    assert hechos["borrador"]["objective"]["estado"] == "confirmado"
    assert c.etiquetas() == []                      # sus botones ya no valen


def test_un_toque_repetido_o_de_una_eleccion_ya_usada_no_vuelve_a_llamar_al_modelo(
        chat):
    c = _alta_hasta_objetivo(chat)
    c.modelo.conducciones.append(salida("Perfecto. ¿Cómo se sabe?",
                                        pregunta=["acceptance_criterion"]))
    token = c.token("Reduce service delay")
    c.tocar("Reduce service delay")

    repetido = _post_intake_callback(c.cliente, token, c.usuario,
                                     callback_id="cb-repetido")

    assert repetido.status_code == 200
    assert len(c.modelo.conducidos) == 2           # el alta y el primer toque, no el repetido


def test_con_estrella_el_objetivo_que_jev_destaca(conversada, conn, monkeypatch):
    def con_estrella(cur, request, who, candidatas):
        return [candidatas[2], candidatas[0], candidatas[1]], True

    monkeypatch.setattr(I, "_ordenar_objetivos", con_estrella)
    c = Chat(conn, monkeypatch, conversada, _modelo(salida(
        "¿A qué objetivo pertenece?", valores={"title": {"texto": "Calibrar"}},
        pregunta=["objective"], botones="objective")))

    c.escribir("necesito crear una tarea: calibrar")

    # Los botones se arman con lo que el turno acaba de guardar: el título que trajo
    # el mensaje ya permite destacar el objetivo que se le parece.
    assert c.etiquetas()[0].startswith("⭐") and "service delay" in c.etiquetas()[0]
    assert not any(e.startswith("⭐") for e in c.etiquetas()[1:])


def test_una_sola_opcion_posible_se_completa_sola_y_no_se_pregunta(
        conversada, conn, monkeypatch):
    """Si quien escribe sólo puede asignarse a sí misma, el responsable se completa
    solo, como siempre, y no figura entre lo que falta."""
    with admin(conn) as cur:
        cur.execute("update membership set activo = false "
                    "where id in (%s, %s)",
                    (conversada["north-lab"]["people"]["Sam North"]["membership_id"],
                     conversada["north-lab"]["people"]["Sam Noble"]["membership_id"]))
    conn.commit()
    c = Chat(conn, monkeypatch, conversada, _modelo(salida(
        "¿Qué hay que hacer?", pregunta=["title"])))

    c.escribir("necesito crear una tarea")

    responsable = c.campo("responsible")
    assert responsable["estado"] == "confirmed" and responsable["proposed_by"] == "server"
    hechos = c.hechos(0)
    assert "responsible" not in hechos["faltan"]
    assert hechos["borrador"]["responsible"]["estado"] == "confirmado"
    assert hechos["borrador"]["area"]["solo_lectura"] is True


# ------------------------------------------------------ lo que el código rechaza

def test_una_fecha_pasada_se_le_dice_al_modelo_y_la_respuesta_es_la_del_reintento(
        chat):
    c = chat(
        salida("Quedó para ayer.", valores={"due_date": {"fecha_iso": _en(-3)}},
               pregunta=["title"]),
        salida("Esa fecha ya pasó. ¿Para cuándo la necesitás?",
               pregunta=["title", "due_date"]))

    nuevas = c.escribir("necesito crear una tarea para el viernes pasado")

    assert len(c.modelo.conducidos) == 2
    segundo = c.hechos(1)
    assert any("ya pasó" in r for r in segundo["rechazos_anteriores"])
    assert _cuerpos(nuevas) == ["Esa fecha ya pasó. ¿Para cuándo la necesitás?"]
    assert c.campo("due_date")["estado"] == "missing"


def test_una_opcion_que_no_es_del_conjunto_se_rechaza_y_no_se_guarda(chat):
    c = chat(
        salida("Listo. ¿Para cuándo?", valores={"responsible": {"opcion_id": "R9"}},
               pregunta=["due_date"]),
        salida("¿A quién se la asigno?", pregunta=["responsible"],
               botones="responsible"))

    nuevas = c.escribir("necesito crear una tarea para Marcos")

    assert c.campo("responsible")["estado"] == "missing"
    assert any("R9" in r for r in c.hechos(1)["rechazos_anteriores"])
    assert _cuerpos(nuevas) == ["¿A quién se la asigno?"]
    assert nuevas[0]["intake_choice_set_id"] is not None


def test_un_texto_con_un_dato_inventado_se_reintenta_con_el_motivo(chat):
    c = chat(
        salida("Quedó para el 15/03. ¿Quién la hace?", pregunta=["title"]),
        salida("¿Qué hay que hacer?", pregunta=["title"]))

    nuevas = c.escribir("necesito crear una tarea")

    assert c.hechos(1)["rechazos_anteriores"][0].startswith("numero_inventado")
    assert _cuerpos(nuevas) == ["¿Qué hay que hacer?"]


def test_lo_valido_del_primer_intento_se_guarda_aunque_haya_que_reintentar(chat):
    c = chat(
        salida("Quedó.", valores={"title": {"texto": "Calibrar"},
                                  "due_date": {"fecha_iso": _en(-1)}},
               pregunta=["title"]),
        salida("¿Para cuándo la necesitás?", pregunta=["due_date"]))

    c.escribir("necesito crear una tarea: calibrar, para ayer")

    assert c.campo("title")["valor"] == "Calibrar"
    assert c.hechos(1)["borrador"]["title"] == {"estado": "confirmado",
                                                "valor": "Calibrar"}


# ------------------------------------------------------------------ correcciones

def _alta_completa_menos_criterio(chat):
    c = chat(salida(
        "Anotado. ¿Cómo se sabe que está terminada?",
        valores={"title": {"texto": "Calibrar los sensores"},
                 "due_date": {"fecha_iso": _en(3)},
                 "responsible": {"opcion_id": "R1"},
                 "objective": {"opcion_id": "O3"}},
        pregunta=["acceptance_criterion"]))
    c.escribir("necesito crear una tarea: calibrar los sensores, la hago yo")
    return c


def test_corregir_un_dato_confirmado_lo_cambia_y_recalcula_el_area(chat):
    c = _alta_completa_menos_criterio(chat)
    id_noble = c.id_de("responsible", "Sam Noble")
    c.modelo.conducciones.append(salida(
        "Listo, queda Sam Noble. ¿Cómo se sabe que está terminada?",
        intencion="corrige", corrige=["responsible"],
        valores={"responsible": {"opcion_id": id_noble}},
        pregunta=["acceptance_criterion"]))
    antes = c.campo("responsible")["valor"]["id"]

    c.escribir("no, el responsable es Sam Noble")

    despues = c.campo("responsible")
    assert despues["valor"]["name"].startswith("Sam Noble")
    assert despues["valor"]["id"] != antes
    area = c.campo("area")
    assert area["estado"] == "confirmed"
    assert area["valor"]["id"] == despues["valor"]["area_id"]    # la de quien es responsable


def test_un_valor_para_un_dato_confirmado_sin_decir_que_corrige_no_lo_cambia(chat):
    c = _alta_completa_menos_criterio(chat)
    id_noble = c.id_de("responsible", "Sam Noble")
    c.modelo.conducciones.append(salida(
        "Listo. ¿Cómo se sabe?", valores={"responsible": {"opcion_id": id_noble}},
        pregunta=["acceptance_criterion"]))
    c.modelo.conducciones.append(salida(
        "Sigue a cargo de Taylor Quinn. ¿Cómo se sabe que está terminada?",
        pregunta=["acceptance_criterion"]))
    antes = c.campo("responsible")["valor"]["id"]

    nuevas = c.escribir("y que Sam Noble le dé una mano")

    assert c.campo("responsible")["valor"]["id"] == antes
    assert "ya está confirmado" in c.hechos()["rechazos_anteriores"][0]
    assert _cuerpos(nuevas)[0].startswith("Sigue a cargo")


# --------------------------------------------------------------------- criterio

def test_un_criterio_que_no_se_puede_comprobar_se_propone_otro_y_se_acepta(chat):
    c = _alta_completa_menos_criterio(chat)
    c.modelo.conducciones.append(salida(
        "Eso no dice cómo se comprueba. ¿Te sirve esto?",
        valores={"acceptance_criterion": {
            "texto": "que ande bien", "verificable": "no",
            "propuesta": "Prueba de 24 h sin fallas, con el registro adjunto"}},
        pregunta=["acceptance_criterion"]))
    c.escribir("que ande bien")
    propuesto = c.campo("acceptance_criterion")
    assert propuesto["estado"] == "proposed" and propuesto["proposed_by"] == "model"
    assert propuesto["valor"] == "Prueba de 24 h sin fallas, con el registro adjunto"

    c.modelo.conducciones.append(salida(
        "Genial, lo dejo así.",
        valores={"acceptance_criterion": {
            "texto": "Prueba de 24 h sin fallas, con el registro adjunto"}}))
    nuevas = c.escribir("sí, dale")

    assert c.hechos()["propuesta_vigente"].startswith("Prueba de 24 h")
    assert c.hechos()["borrador"]["acceptance_criterion"]["estado"] == "propuesto"
    assert c.campo("acceptance_criterion")["estado"] == "confirmed"
    assert c.campo("acceptance_criterion")["valor"] == (
        "Prueba de 24 h sin fallas, con el registro adjunto")
    assert "Resumen para revisar" in nuevas[0]["cuerpo"]       # ya está todo


@pytest.mark.parametrize("dice", ["me va", "Informe firmado por calidad"])
def test_una_propuesta_hecha_solo_en_la_conversacion_se_acepta_mandando_su_texto(
        chat, dice):
    # Hallazgo de la corrida conversada: Prisma propuso en su respuesta, sin registrar
    # propuesta; aceptar es mandar el texto como criterio, un solo camino.
    c = _alta_completa_menos_criterio(chat)
    c.modelo.conducciones.append(salida(
        "Podría ser: informe firmado por calidad. ¿Te sirve?",
        intencion="ayuda", pregunta=["acceptance_criterion"]))
    c.escribir("ayudame")
    c.modelo.conducciones.append(salida(
        "Listo, revisalo.", valores={"acceptance_criterion": {
            "texto": "Informe firmado por calidad"}}))

    nuevas = c.escribir(dice)

    criterio = c.campo("acceptance_criterion")
    assert criterio["estado"] == "confirmed"
    assert criterio["valor"] == "Informe firmado por calidad"
    assert "Resumen para revisar" in nuevas[0]["cuerpo"]
    assert c.incidentes(incidentes.ETAPA_ALTA_CONDUCIDA_FALLIDA) == []


def test_aceptar_con_la_clave_retirada_se_rechaza_por_formato_y_se_corrige_con_el_texto(
        chat):
    c = _alta_completa_menos_criterio(chat)
    c.modelo.conducciones.append(salida(
        "Listo.", valores={"acceptance_criterion": {"acepta_propuesta": True}}))
    c.modelo.conducciones.append(salida(
        "Listo, revisalo.", valores={"acceptance_criterion": {
            "texto": "Informe firmado por calidad"}}))

    nuevas = c.escribir("me va")

    assert c.campo("acceptance_criterion")["estado"] == "confirmed"
    assert "Resumen para revisar" in nuevas[0]["cuerpo"]
    assert c.incidentes(incidentes.ETAPA_ALTA_CONDUCIDA_FALLIDA) == []


def test_si_insiste_con_su_texto_tras_una_propuesta_se_acepta_y_no_se_vuelve_a_proponer(
        chat):
    c = _alta_completa_menos_criterio(chat)
    c.modelo.conducciones.append(salida(
        "¿Te sirve esto?", valores={"acceptance_criterion": {
            "texto": "que ande bien", "verificable": "no",
            "propuesta": "Prueba de 24 h sin fallas"}},
        pregunta=["acceptance_criterion"]))
    c.escribir("que ande bien")
    c.modelo.conducciones.append(salida(
        "Bueno, lo dejo como pediste.", valores={"acceptance_criterion": {
            "texto": "que ande bien", "verificable": "no",
            "propuesta": "Otra propuesta distinta"}}))

    nuevas = c.escribir("no, que ande bien nomás")

    assert c.hechos()["propuesta_hecha"] is True
    criterio = c.campo("acceptance_criterion")
    assert (criterio["estado"], criterio["valor"]) == ("confirmed", "que ande bien")
    assert "Criterio de aceptación: que ande bien" in nuevas[0]["cuerpo"]


# --------------------------------------------------------------- el resumen

def _hasta_el_resumen(chat):
    c = _alta_completa_menos_criterio(chat)
    c.modelo.conducciones.append(salida(
        "Listo, revisalo.", valores={"acceptance_criterion": {
            "texto": "Informe firmado por calidad", "verificable": "si"}}))
    return c, c.escribir("el informe firmado por calidad")


def test_con_todo_completo_sale_el_resumen_exacto_con_la_frase_del_modelo_y_el_cierre(
        chat):
    c, nuevas = _hasta_el_resumen(chat)

    (mensaje,) = nuevas
    cuerpo = mensaje["cuerpo"]
    assert cuerpo.startswith("Listo, revisalo.\n\nResumen para revisar\n")
    assert "Título: Calibrar los sensores" in cuerpo
    assert "Objetivo: Reduce service delay" in cuerpo
    assert "Área: Field Services" in cuerpo
    assert "Responsable: Taylor Quinn" in cuerpo
    assert f"Fecha objetivo: {datetime.fromisoformat(_en(3)).strftime('%d/%m/%Y')}" in cuerpo
    assert "Criterio de aceptación: Informe firmado por calidad" in cuerpo
    assert "Evidencia: test record" in cuerpo
    assert mensaje["pending_action_id"] is not None          # los botones reales
    assert cuerpo.rstrip().endswith(".")                      # termina en el cierre del código
    assert len(c.modelo.conducidos) == 2                      # sin llamada extra del resumen


def test_el_borrador_no_se_convierte_en_tarea_sin_el_boton(chat, conn):
    c, _ = _hasta_el_resumen(chat)

    with admin(conn) as cur:
        cur.execute("select count(*) n from task")
        assert cur.fetchone()["n"] == 0
        cur.execute("select herramienta, estado from pending_action "
                    "where draft_id = (select task_draft_id from task_intake_request "
                    "where id = %s)", (c.rid,))
        (accion,) = [a for a in cur.fetchall() if a["estado"] == "esperando"]
    assert accion["herramienta"] in ("confirmar_borrador_tarea",
                                     "revisar_borrador_tarea")
    assert c.estado() == "active"


def test_un_cambio_tras_el_resumen_lo_reemplaza_por_uno_nuevo(chat, conn):
    c, primero = _hasta_el_resumen(chat)
    c.modelo.conducciones.append(salida(
        "Cambiado.", intencion="corrige", corrige=["due_date"],
        valores={"due_date": {"fecha_iso": _en(6)}}))

    nuevas = c.escribir("mejor para el lunes")

    assert len(nuevas) == 1 and "Resumen para revisar" in nuevas[0]["cuerpo"]
    assert datetime.fromisoformat(_en(6)).strftime("%d/%m/%Y") in nuevas[0]["cuerpo"]
    with admin(conn) as cur:
        cur.execute("select estado, count(*) n from pending_action where draft_id = "
                    "(select task_draft_id from task_intake_request where id = %s) "
                    "group by estado", (c.rid,))
        estados = {f["estado"]: f["n"] for f in cur.fetchall()}
    assert estados.get("esperando") == 1                      # un solo resumen vigente


def test_una_duda_con_el_resumen_a_la_vista_no_arma_otro_resumen(chat):
    c, primero = _hasta_el_resumen(chat)
    c.modelo.conducciones.append(salida(
        "Con el botón Enviar a aprobación se lo mando a quien lo confirma.",
        intencion="ayuda"))

    nuevas = c.escribir("¿y si confirmo qué pasa?")

    assert _cuerpos(nuevas) == [
        "Con el botón Enviar a aprobación se lo mando a quien lo confirma."]


# ----------------------------------------------------- cancelar, dejar, otro tema

def test_cancelar_cancela_el_borrador_y_responde_el_modelo(chat):
    c = _alta_hasta_objetivo(chat)
    c.modelo.conducciones.append(salida("Listo, cancelé la tarea.",
                                        intencion="cancelar"))

    nuevas = c.escribir("cancelá")

    assert c.estado() == "cancelled"
    assert _cuerpos(nuevas) == ["Listo, cancelé la tarea."]


def test_dejar_pausa_el_borrador_sin_perder_nada(chat):
    c = _alta_hasta_objetivo(chat)
    c.modelo.conducciones.append(salida(
        "Dale, queda guardada la tarea «Calibrar los sensores».", intencion="dejar"))

    nuevas = c.escribir("dejémoslo para después")

    assert c.estado() == "active"
    with admin(c.conn) as cur:
        cur.execute("select terminal_result from task_intake_request where id = %s",
                    (c.rid,))
        assert cur.fetchone()["terminal_result"]["pausado"] is True
    assert c.campo("title")["valor"] == "Calibrar los sensores"
    assert _cuerpos(nuevas) == [
        "Dale, queda guardada la tarea «Calibrar los sensores»."]


def test_con_el_borrador_pausado_el_mensaje_siguiente_sigue_el_camino_normal(chat):
    c = _alta_hasta_objetivo(chat)
    c.modelo.conducciones.append(salida("Queda guardada.", intencion="dejar"))
    c.escribir("después sigo")
    conducidos = len(c.modelo.conducidos)
    c.modelo.rutas.append(IntentRoute(IntentAction.NORMAL_CONVERSATION))
    c.modelo.guion.append(Respuesta(texto="Hay dos tareas abiertas."))

    nuevas = c.escribir("¿qué tengo pendiente?")

    assert len(c.modelo.conducidos) == conducidos             # el alta no interviene
    assert _cuerpos(nuevas) == ["Hay dos tareas abiertas."]


def test_otro_tema_pausa_el_borrador_y_se_atiende_lo_otro_diciendo_que_quedo_guardado(
        chat):
    c = _alta_hasta_objetivo(chat)
    c.modelo.conducciones.append(salida("Eso lo veo aparte.", intencion="otro_tema"))
    c.modelo.rutas.append(IntentRoute(IntentAction.NORMAL_CONVERSATION))
    c.modelo.guion.append(Respuesta(texto="Un bloqueo frena una tarea."))

    nuevas = c.escribir("¿qué es un bloqueo?")

    assert c.estado() == "active"
    assert c.campo("title")["valor"] == "Calibrar los sensores"
    # UN solo mensaje visible: el aviso de la pausa primero, después la respuesta.
    assert _cuerpos(nuevas) == [
        gateway.AVISO_ALTA_PAUSADA.format(titulo=" «Calibrar los sensores»")
        + "\n\nUn bloqueo frena una tarea."]
    assert "¿Seguimos?" not in " ".join(_cuerpos(nuevas))
    with admin(c.conn) as cur:
        cur.execute("select terminal_result from task_intake_request where id = %s",
                    (c.rid,))
        assert cur.fetchone()["terminal_result"]["pausado"] is True


def test_un_borrador_pausado_se_ofrece_retomar_y_continuar_lo_conduce_el_modelo(chat):
    c = _alta_hasta_objetivo(chat)
    c.modelo.conducciones.append(salida("Queda guardada.", intencion="dejar"))
    c.escribir("después sigo")
    c.modelo.rutas.append(IntentRoute(IntentAction.START_TASK_INTAKE))

    nuevas = c.escribir("quiero crear una tarea")

    assert "Ya hay un borrador de tarea en curso" in nuevas[0]["cuerpo"]
    c.modelo.conducciones.append(salida(
        "Retomamos «Calibrar los sensores». ¿A qué objetivo pertenece?",
        pregunta=["objective"], botones="objective"))

    nuevas = c.tocar("Continuar borrador")

    assert _cuerpos(nuevas) == [
        "Retomamos «Calibrar los sensores». ¿A qué objetivo pertenece?"]
    assert c.hechos()["evento"] == {"toque": "continuar"}
    with admin(c.conn) as cur:
        cur.execute("select terminal_result from task_intake_request where id = %s",
                    (c.rid,))
        assert not (cur.fetchone()["terminal_result"] or {}).get("pausado")


def test_la_propuesta_de_criterio_ya_hecha_sobrevive_a_pausar_y_continuar(chat):
    c = _alta_completa_menos_criterio(chat)
    c.modelo.conducciones.append(salida(
        "¿Te sirve esto?", valores={"acceptance_criterion": {
            "texto": "que ande bien", "verificable": "no",
            "propuesta": "Prueba de 24 h sin fallas"}},
        pregunta=["acceptance_criterion"]))
    c.escribir("que ande bien")
    c.modelo.conducciones.append(salida("Queda guardada.", intencion="dejar"))
    c.escribir("después sigo")
    c.modelo.rutas.append(IntentRoute(IntentAction.START_TASK_INTAKE))
    c.escribir("quiero crear una tarea")
    c.modelo.conducciones.append(salida("Retomamos. ¿Te sirve esa propuesta?",
                                        pregunta=["acceptance_criterion"]))

    c.tocar("Continuar borrador")

    with admin(c.conn) as cur:
        cur.execute("select terminal_result from task_intake_request where id = %s",
                    (c.rid,))
        marcas = cur.fetchone()["terminal_result"]
    assert marcas == {"criterio_propuesto": True}       # sin la pausa, con la marca
    assert c.hechos()["propuesta_hecha"] is True


def test_empezar_otro_borrador_cancela_el_pausado_y_el_modelo_conduce_el_nuevo(chat):
    c = _alta_hasta_objetivo(chat)
    c.modelo.conducciones.append(salida("Queda guardada.", intencion="dejar"))
    c.escribir("después sigo")
    viejo = c.rid
    c.modelo.rutas.append(IntentRoute(IntentAction.START_TASK_INTAKE))
    c.escribir("necesito crear otra tarea: pintar el tablero")
    c.modelo.conducciones.append(salida(
        "Dale, empezamos otra. ¿Qué hay que hacer?", pregunta=["title"]))

    nuevas = c.tocar("Empezar otro")

    assert _solicitud(c.conn, viejo) == "cancelled"
    assert c.rid != viejo and c.estado() == "active"
    assert _cuerpos(nuevas) == ["Dale, empezamos otra. ¿Qué hay que hacer?"]
    assert c.hechos()["evento"] == {
        "mensaje_de_la_persona": "necesito crear otra tarea: pintar el tablero"}


def _tocar_modificar(c) -> list[dict]:
    """Toca el botón Modificar del resumen vigente (una acción pendiente, no un
    botón de elección del alta conducida)."""
    cliente = _callback_client(c.conn, c.monkeypatch)
    c.monkeypatch.setattr("prisma.llm.desde_base", lambda *a: c.modelo)
    with admin(c.conn) as cur:
        cur.execute(
            """select o.token from pending_action_option o
                 join pending_action p on p.id = o.pending_action_id
                where p.estado = 'esperando' and o.etiqueta like %s""",
            ("%Modificar%",))
        token = cur.fetchone()["token"]
    antes = _salidas(c.conn, c.usuario)
    respuesta = cliente.post(
        "/telegram/north-lab",
        json={"callback_query": {
            "id": f"cb-modificar-{next(_toques)}", "from": {"id": c.usuario},
            "data": "p:" + token,
            "message": {"message_id": 7, "chat": {"id": c.usuario}}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"})
    assert respuesta.status_code == 200
    return _nuevas(c.conn, c.usuario, antes)


def test_el_boton_modificar_del_resumen_se_lo_deja_al_modelo(chat, conn):
    c, _ = _hasta_el_resumen(chat)
    c.modelo.conducciones.append(salida(
        "Claro, ¿qué querés cambiar?", intencion="ayuda"))

    nuevas = _tocar_modificar(c)

    assert _cuerpos(nuevas) == ["Claro, ¿qué querés cambiar?"]
    assert c.hechos()["evento"] == {"toque": "modificar"}


def test_tras_modificar_una_fecha_rechazada_se_vuelve_a_pedir_sin_incidente(chat):
    """El verificador guarda invariantes, no estilo: con todo completo (la fecha
    vieja sigue guardada) el valor nuevo es una fecha pasada, el código lo rechaza
    y el modelo, con razón, vuelve a pedir la fecha. Esa pregunta llega tal cual."""
    c, _ = _hasta_el_resumen(chat)
    c.modelo.conducciones.append(salida("Claro, ¿qué querés cambiar?",
                                        intencion="ayuda"))
    _tocar_modificar(c)
    fecha_guardada = c.campo("due_date")["valor"]
    c.modelo.conducciones.append(salida(
        "Esa fecha ya pasó. ¿Para cuándo la necesitás?", intencion="corrige",
        corrige=["due_date"], valores={"due_date": {"fecha_iso": _en(-3)}},
        pregunta=["due_date"]))
    c.modelo.conducciones.append(salida(      # el reintento, ya sin el valor rechazado
        "Esa fecha ya pasó. ¿Para cuándo la necesitás?",
        intencion="corrige", corrige=["due_date"], pregunta=["due_date"]))

    nuevas = c.escribir("cambiá la fecha al 15 de agosto")

    assert _cuerpos(nuevas) == ["Esa fecha ya pasó. ¿Para cuándo la necesitás?"]
    assert any("ya pasó" in r for r in c.hechos()["rechazos_anteriores"])
    assert c.incidentes("alta_conducida_fallida") == []
    assert c.campo("due_date")["valor"] == fecha_guardada       # nada cambió
    c.modelo.conducciones.append(salida(
        "Listo, cambiada.", intencion="corrige", corrige=["due_date"],
        valores={"due_date": {"fecha_iso": _en(6)}}))

    nuevas = c.escribir("el lunes")

    assert len(nuevas) == 1 and "Resumen para revisar" in nuevas[0]["cuerpo"]
    assert datetime.fromisoformat(_en(6)).strftime("%d/%m/%Y") in nuevas[0]["cuerpo"]


def test_tras_modificar_los_botones_de_un_dato_confirmado_se_arman_y_el_toque_lo_cambia(
        chat):
    c, _ = _hasta_el_resumen(chat)
    c.modelo.conducciones.append(salida("Claro, ¿qué querés cambiar?",
                                        intencion="ayuda"))
    _tocar_modificar(c)
    c.modelo.conducciones.append(salida(
        "Dale, ¿quién la hace?", intencion="corrige", corrige=["responsible"],
        pregunta=["responsible"], botones="responsible"))

    nuevas = c.escribir("quiero cambiar el responsable")

    assert _cuerpos(nuevas) == ["Dale, ¿quién la hace?"]
    assert any("Sam Noble" in e for e in c.etiquetas())        # las opciones del código
    c.modelo.conducciones.append(salida("Listo, revisalo."))

    nuevas = c.tocar("Sam Noble")

    assert c.campo("responsible")["valor"]["name"].startswith("Sam Noble")
    assert len(nuevas) == 1 and "Resumen para revisar" in nuevas[0]["cuerpo"]
    assert "Responsable: Sam Noble" in nuevas[0]["cuerpo"]
    assert c.incidentes("alta_conducida_fallida") == []


# ----------------------------------------------------------------- si el modelo falla

def test_si_el_modelo_falla_dos_veces_hay_incidente_y_aviso_neutro_no_una_plantilla(
        chat):
    c = chat({"intencion": "inventada", "texto": "x"},
             salida("Quedó para el 15/03.", pregunta=["title"]))

    nuevas = c.escribir("necesito crear una tarea")

    assert len(c.modelo.conducidos) == 2
    (incidente,) = c.incidentes(incidentes.ETAPA_ALTA_CONDUCIDA_FALLIDA)
    assert incidente["severidad"] == "media"
    (cuerpo,) = _cuerpos(nuevas)
    assert cuerpo.startswith(NOTICIA_NEUTRA_INCIDENTE)
    assert "¿Qué hay que hacer?" not in cuerpo               # nunca una plantilla
    assert cuerpo.endswith("Pendiente: el título.")


def test_si_el_modelo_da_error_no_se_reintenta_y_queda_el_aviso(chat):
    c = chat(TimeoutError("colgado"))

    nuevas = c.escribir("necesito crear una tarea")

    assert len(c.modelo.conducidos) == 1
    assert len(c.incidentes(incidentes.ETAPA_ALTA_CONDUCIDA_FALLIDA)) == 1
    assert _cuerpos(nuevas)[0].startswith(NOTICIA_NEUTRA_INCIDENTE)


def test_tras_una_falla_los_botones_dicen_para_que_son_sin_texto_de_plantilla(chat):
    c = _alta_hasta_objetivo(chat)
    c.modelo.conducciones.append(TimeoutError("colgado"))

    # Un mensaje que pasa por el modelo y falla, con el objetivo pendiente.
    nuevas = c.escribir("el de la demora")

    (mensaje,) = nuevas
    assert mensaje["cuerpo"] == f"{NOTICIA_NEUTRA_INCIDENTE}\n\nPendiente: el objetivo."
    assert mensaje["intake_choice_set_id"] is not None
    assert len(c.etiquetas()) == 3


def test_una_falla_tras_un_toque_que_completa_el_borrador_muestra_el_resumen(chat):
    c = chat(salida(
        "Anotado.", valores={"title": {"texto": "Calibrar los sensores"},
                             "due_date": {"fecha_iso": _en(3)},
                             "responsible": {"opcion_id": "R1"},
                             "acceptance_criterion": {
                                 "texto": "Informe firmado por calidad",
                                 "verificable": "si"}},
        pregunta=["objective"], botones="objective"))
    c.escribir("necesito crear una tarea: calibrar los sensores, la hago yo")
    c.modelo.conducciones.append(TimeoutError("colgado"))

    nuevas = c.tocar("Reduce service delay")

    (mensaje,) = nuevas
    assert mensaje["cuerpo"].startswith(NOTICIA_NEUTRA_INCIDENTE)
    assert "Resumen para revisar" in mensaje["cuerpo"]
    assert mensaje["pending_action_id"] is not None
    assert c.campo("objective")["estado"] == "confirmed"


def test_el_aviso_a_la_administracion_de_las_fallas_se_agrupa(chat):
    c = chat(TimeoutError("uno"), TimeoutError("dos"), TimeoutError("tres"))
    AC._ultimo_aviso.clear()

    c.escribir("necesito crear una tarea")
    c.escribir("hola")
    c.escribir("¿hay alguien?")

    incidentes_ = c.incidentes(incidentes.ETAPA_ALTA_CONDUCIDA_FALLIDA)
    assert len(incidentes_) == 3                              # todos quedan registrados
    avisados = [i for i in incidentes_ if i["notificado_admin_en"] is not None
                or "agrupado" not in i["resumen_sanitizado"]]
    sin_aviso = [i for i in incidentes_ if "agrupado" in i["resumen_sanitizado"]]
    assert len(sin_aviso) == 2 and len(avisados) == 1


# ------------------------------------------------- una respuesta visible por mensaje

def test_cada_mensaje_y_cada_toque_tienen_una_sola_respuesta_visible(chat, conn):
    c = _alta_hasta_objetivo(chat)
    c.modelo.conducciones.append(salida("Perfecto. ¿Cómo se sabe?",
                                        pregunta=["acceptance_criterion"]))
    c.tocar("Reduce service delay")
    with admin(conn) as cur:
        cur.execute(
            """select entrante_id, count(distinct coalesce(respuesta_grupo, dedupe_key))
                      n from message_outbox
                where es_respuesta and estado <> 'descartado'
                group by entrante_id""")
        assert all(f["n"] == 1 for f in cur.fetchall())


# ------------------------------------------- tanda 1-4 de la corrida conversada

def _enviar_a_aprobacion(c):
    """Toca el botón Enviar a aprobación del resumen vigente (una acción pendiente)."""
    cliente = _callback_client(c.conn, c.monkeypatch)
    c.monkeypatch.setattr("prisma.llm.desde_base", lambda *a: c.modelo)
    with admin(c.conn) as cur:
        cur.execute(
            """select o.token from pending_action_option o
                 join pending_action p on p.id = o.pending_action_id
                where p.estado = 'esperando' and o.etiqueta like %s""",
            ("%Enviar a aprobación%",))
        token = cur.fetchone()["token"]
    antes = _salidas(c.conn, c.usuario)
    respuesta = cliente.post(
        "/telegram/north-lab",
        json={"callback_query": {
            "id": f"cb-enviar-{next(_toques)}", "from": {"id": c.usuario},
            "data": "p:" + token,
            "message": {"message_id": 7, "chat": {"id": c.usuario}}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"})
    assert respuesta.status_code == 200
    return _nuevas(c.conn, c.usuario, antes)


def _chat_del_aprobador(c) -> int:
    return c.world["north-lab"]["people"]["Morgan Hale"]["telegram"]


def test_el_aprobador_recibe_el_resumen_sin_la_frase_del_turno_de_quien_pidio(chat):
    """Una frase del modelo es de la persona para la que se escribió: la apertura de
    quien pide ("confirmá con el botón…") no viaja al aprobador."""
    c, resumen = _hasta_el_resumen(chat)
    assert resumen[0]["cuerpo"].startswith("Listo, revisalo.\n\nResumen para revisar")

    _enviar_a_aprobacion(c)

    (recibido,) = [f for f in _salidas(c.conn, _chat_del_aprobador(c))
                   if f["pending_action_id"]]
    cuerpo = recibido["cuerpo"]
    assert "Listo, revisalo." not in cuerpo
    assert cuerpo.startswith("Resumen para revisar\nTítulo: Calibrar los sensores")
    assert "Responsable: Taylor Quinn" in cuerpo
    assert cuerpo.endswith(I.CIERRE_CONFIRMAR)
    # Quien pidió conserva SU resumen con su frase (es la respuesta a su turno).
    with admin(c.conn) as cur:
        cur.execute("select resumen from pending_action where draft_id = "
                    "(select task_draft_id from task_intake_request where id = %s) "
                    "order by creado_en limit 1", (c.rid,))
        assert cur.fetchone()["resumen"].startswith("Listo, revisalo.")


@pytest.mark.parametrize("texto,respuesta", [
    ("¿qué es un bloqueo?", "Un bloqueo frena una tarea."),
    ("mostrame mis tareas", "Tenés dos tareas abiertas."),
    ("¿y qué es un hito?", "Un hito marca un punto de control."),
])
def test_cambiar_de_tema_en_medio_del_alta_es_un_solo_mensaje_visible(
        chat, texto, respuesta):
    c = _alta_hasta_objetivo(chat)
    c.modelo.conducciones.append(salida("Eso lo veo aparte.", intencion="otro_tema"))
    c.modelo.rutas.append(IntentRoute(IntentAction.NORMAL_CONVERSATION))
    c.modelo.guion.append(Respuesta(texto=respuesta))

    nuevas = c.escribir(texto)

    assert len(nuevas) == 1
    pausa = gateway.AVISO_ALTA_PAUSADA.format(titulo=" «Calibrar los sensores»")
    assert nuevas[0]["cuerpo"] == f"{pausa}\n\n{respuesta}"
    assert c.incidentes("respuesta_duplicada") == []


def test_si_el_aviso_de_la_pausa_no_entra_con_la_respuesta_sale_como_primera_parte_del_mismo_grupo(
        chat):
    from prisma.respuesta_unica import grupo_de

    c = _alta_hasta_objetivo(chat)
    c.modelo.conducciones.append(salida("Eso lo veo aparte.", intencion="otro_tema"))
    c.modelo.rutas.append(IntentRoute(IntentAction.NORMAL_CONVERSATION))
    largo = "\n\n".join(f"Párrafo {i}. " + "palabra " * 60 for i in range(20))
    c.modelo.guion.append(Respuesta(texto=largo))

    nuevas = c.escribir("explicame todo sobre los bloqueos")

    assert len(nuevas) >= 2
    assert nuevas[0]["cuerpo"] == gateway.AVISO_ALTA_PAUSADA.format(
        titulo=" «Calibrar los sensores»")
    with admin(c.conn) as cur:
        cur.execute("select dedupe_key, respuesta_grupo from message_outbox "
                    "where id = any(%s)", ([f["id"] for f in nuevas],))
        assert len({grupo_de(f) for f in cur.fetchall()}) == 1   # una sola respuesta
    assert c.incidentes("respuesta_duplicada") == []


def test_los_hechos_dicen_que_boton_final_mostrara_el_resumen_de_esta_persona(chat):
    """Taylor Quinn necesita aprobación de otra persona: su resumen tiene Enviar a
    aprobación, no Confirmar; así lo dicen los hechos antes de que el modelo escriba."""
    c = _alta_hasta_objetivo(chat)
    c.modelo.conducciones.append(salida(
        "Dale. ¿Cómo se sabe que está terminada?", pregunta=["acceptance_criterion"]))
    c.escribir("el objetivo es el de las demoras")
    hechos = c.hechos()
    assert hechos["boton_final"] == "Enviar a aprobación"          # ya es responsable
    por_nombre = {o["nombre"]: o.get("boton_final")
                  for o in hechos["opciones"]["responsible"]}
    (yo,) = [b for n, b in por_nombre.items() if n.startswith("Taylor Quinn")]
    assert yo == "Enviar a aprobación"
    assert set(por_nombre.values()) <= {"Confirmar", "Enviar a aprobación"}


def test_el_modelo_que_nombra_confirmar_cuando_el_resumen_trae_enviar_se_corrige(chat):
    c, _ = _hasta_el_resumen(chat)
    c.modelo.conducciones.append(salida(
        "Con el botón Confirmar se crea la tarea.", intencion="ayuda"))
    c.modelo.conducciones.append(salida(
        "Con el botón Enviar a aprobación se lo mando a quien lo confirma.",
        intencion="ayuda"))

    nuevas = c.escribir("¿y ahora qué hago?")

    assert _cuerpos(nuevas) == [
        "Con el botón Enviar a aprobación se lo mando a quien lo confirma."]
    assert c.hechos()["rechazos_anteriores"] == ["boton_inexistente: Confirmar"]


def _auditorias(c) -> list[dict]:
    with admin(c.conn) as cur:
        cur.execute("select detalle from audit_log where accion = 'alta_conducida_turno' "
                    "order by at, (detalle->>'intento')::int")
        return [f["detalle"] for f in cur.fetchall()]


def test_un_intento_rechazado_deja_la_forma_de_la_salida_sin_texto_libre(chat):
    c = chat(
        salida("Anotado, calibrar sensores del laboratorio central.",
               valores={"title": {"texto": "Calibrar sensores del laboratorio central"}},
               pregunta=[]),                      # falta pregunta: se rechaza
        salida("Anotado. ¿A qué objetivo pertenece?",
               valores={"title": {"texto": "Calibrar sensores del laboratorio central"}},
               pregunta=["objective"], botones="objective"))

    c.escribir("necesito crear una tarea: calibrar sensores del laboratorio central")

    rechazada, aceptada = _auditorias(c)
    assert rechazada["resultado"] == "rechazada" and rechazada["intento"] == 1
    assert rechazada["motivo"].startswith("falta_pregunta")
    assert rechazada["salida"] == {
        "intencion": "continuar", "pregunta": [], "botones": None,
        "valores": ["title"], "corrige": [], "texto_tiene_pregunta": False,
        "texto_largo": len("Anotado, calibrar sensores del laboratorio central."),
        "faltan_tras": ["objective", "responsible", "due_date",
                        "acceptance_criterion"]}
    assert "salida" not in aceptada                 # sólo los rechazados
    # Ningún texto libre (del modelo ni de la persona) en la fila de auditoría.
    crudo = json.dumps(rechazada, ensure_ascii=False)
    assert "laboratorio" not in crudo and "Anotado" not in crudo


def test_un_intento_con_formato_roto_guarda_solo_el_motivo(chat):
    c = chat({"intencion": "inventada", "texto": "algo secreto"},
             salida("¿Qué hay que hacer?", pregunta=["title"]))

    c.escribir("quiero crear una tarea")

    rechazada, _ = _auditorias(c)
    assert rechazada["motivo"].startswith("formato")
    assert "salida" not in rechazada


def test_los_hechos_del_primer_mensaje_son_los_de_cualquier_turno(chat):
    """Hallazgo (primer mensaje): no hay una forma distinta de armar los hechos; el
    primer turno y los siguientes tienen las mismas claves y el mismo `evento`."""
    c = chat(salida("¿Qué hay que hacer?", pregunta=["title"]),
             salida("Dale. ¿Para cuándo?", valores={"title": {"texto": "Calibrar"}},
                    pregunta=["due_date"]))
    c.escribir("quiero crear una tarea")
    c.escribir("calibrar")

    primero, segundo = c.hechos(0), c.hechos(1)
    assert set(primero) == set(segundo)
    assert set(primero["evento"]) == set(segundo["evento"]) == {"mensaje_de_la_persona"}
    assert primero["faltan"] == ["title", "objective", "responsible", "due_date",
                                 "acceptance_criterion"]
    assert c.modelo.conducidos[0][1] == []          # nada de conversación previa
