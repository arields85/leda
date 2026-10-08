"""La hoja de aprobación (circuito 8; `leda.motor.aprobacion`; porción 3b de la C-3).

Decidido por el usuario (`odd/tasks/fase-c.md`, preguntas 2 y 3): lo claro va directo, sin vista
previa, porque es la decisión de quien aprueba; lo que mezcla aprobar y pedir un cambio lleva una
sola pregunta con dos botones; el aviso de la entrega ofrece "Aprobar" y "Pedir cambios" como
atajos (escribir vale igual); una aprobación que todavía no puede cerrar queda anotada y, cuando
se resuelve lo que faltaba, el código vuelve a comprobar y la cierra sola, con aviso al
responsable y a quien aprobó. Sólo quien aprueba ese trabajo decide; Leda nunca aprueba; el
cierre lo comprueba el sistema (mecánica §5), y "terminé" nunca llega a terminada.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import pytest

from leda.autoridad import identificar_en_espacio
from leda.db import admin, espacio
from leda.despachador import TransporteDePrueba
from leda.motor import aprobacion, preguntas
from leda.motor.ciclo import Ciclo
from leda.motor.fichas import FICHAS
from leda.motor.ia import IAGuionada, Jugada
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import procesar_toque, procesar_turno

from tests.motor.ayudantes import (AHORA, VIERNES_16, IAQueRedacta, avisos_guardados, cuantas,
                                   enviar, estado_de, todos, uno)

ENTREGADA = "Armar el tablero"
DESPUES_DEL_MARGEN = AHORA + timedelta(minutes=20)


# --- Ayudas ---------------------------------------------------------------------------------

def _tarea(conn, mundo, titulo: str = ENTREGADA, quien: str = "Marcos",
           estado: str = "en_curso", pide: tuple[str, ...] = (),
           criterio: str | None = "El tablero armado y probado") -> str:
    persona = mundo["personas"][quien]
    with admin(conn) as cur:
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, estado, fecha_objetivo,
                                 evidencia_requerida, criterio_aceptacion)
               values (%s, %s, %s, %s, %s, 'asignada', %s, %s, %s) returning id""",
            (mundo["id"], mundo["objetivo"], titulo, mundo["area"], persona["membership_id"],
             VIERNES_16, list(pide), criterio))
        tarea = str(cur.fetchone()["id"])
        if estado != "asignada":
            cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                         actor_kind, motivo, at)
                           values (%s, 'asignada', %s, 'persona', 'prueba', %s)""",
                        (tarea, estado, AHORA - timedelta(days=3)))
    conn.commit()
    return tarea


def _nahuel(conn, mundo) -> None:
    """Otra persona del espacio, cuyo trabajo aprueba Marcos: no aprueba el de Marcos."""
    with admin(conn) as cur:
        cur.execute("select rol_id from membership where id = %s",
                    (mundo["personas"]["Marcos"]["membership_id"],))
        rol = cur.fetchone()["rol_id"]
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (81009, 'Nahuel Gimenez') returning id""")
        usuario = str(cur.fetchone()["id"])
        cur.execute("""insert into membership (workspace_id, app_user_id, area_id, rol_id,
                                               aprobador_membership_id)
                       values (%s, %s, %s, %s, %s) returning id""",
                    (mundo["id"], usuario, mundo["area"], rol,
                     mundo["personas"]["Marcos"]["membership_id"]))
        mundo["personas"]["Nahuel"] = {"app_user_id": usuario, "telegram": 81009,
                                       "membership_id": str(cur.fetchone()["id"])}
        cur.execute("""insert into greeting_state (membership_id, workspace_id, ultima_fecha_local)
                       values (%s, %s, date '9999-12-31')""",
                    (mundo["personas"]["Nahuel"]["membership_id"], mundo["id"]))
    conn.commit()


class Turnos:
    """Los mensajes y los toques de cualquier persona del mundo, con la IA guionada."""

    def __init__(self, conn, mundo) -> None:
        self.conn, self.mundo = conn, mundo
        self.minuto = 0
        self.ia: IAGuionada | None = None

    def _quien(self, nombre: str):
        with espacio(self.conn, self.mundo["id"]) as cur:
            quien = identificar_en_espacio(cur, self.mundo["personas"][nombre]["telegram"],
                                           self.mundo["id"])
        self.conn.commit()
        return quien

    def _at(self, at: datetime | None) -> datetime:
        self.minuto += 1
        return at or AHORA + timedelta(minutes=self.minuto)

    def dice(self, nombre: str, *jugadas: Jugada, texto: str = "-",
             at: datetime | None = None):
        at = self._at(at)
        quien = self._quien(nombre)
        persona = self.mundo["personas"][nombre]
        with espacio(self.conn, self.mundo["id"]) as cur:
            cur.execute(
                """insert into inbound_message (workspace_id, telegram_message_id, chat_id,
                                                app_user_id, texto, at)
                   values (%s, %s, %s, %s, %s, %s) returning id""",
                (self.mundo["id"], uuid.uuid4().int % 1_000_000, persona["telegram"],
                 persona["app_user_id"], texto, at))
            entrante = str(cur.fetchone()["id"])
        self.conn.commit()
        self.ia = IAGuionada(jugadas=[list(jugadas)], redacciones=["Listo."])
        r = procesar_turno(self.conn, quien, entrante, self.ia, RelojFijo(at))
        self.conn.commit()
        assert r.error is None, r.error
        return r

    def toca(self, nombre: str, token: str, at: datetime | None = None):
        at = self._at(at)
        quien = self._quien(nombre)
        self.ia = IAGuionada(redacciones=["Listo."])
        r = procesar_toque(self.conn, quien, token, self.mundo["personas"][nombre]["telegram"],
                           self.ia, RelojFijo(at))
        self.conn.commit()
        return r

    @property
    def situacion(self) -> dict:
        return self.ia.pedidos_de_jugadas[-1]

    @property
    def redaccion(self) -> dict:
        return self.ia.pedidos_de_redaccion[-1]


@pytest.fixture
def turnos(conn, mundo) -> Turnos:
    return Turnos(conn, mundo)


def _entregada(conn, mundo, turnos, titulo: str = ENTREGADA, alias: str = "T2",
               **de_la_tarea) -> str:
    """Marcos entrega `titulo`, con lo que describe el criterio de aceptación (C-3d, D3), y la
    confirma por escrito; la tarea queda en revisión."""
    tarea = _tarea(conn, mundo, titulo, **de_la_tarea)
    turnos.dice("Marcos", Jugada("entregar", {"tarea": alias, "lo_descrito_cubre": ["C1"]}),
                texto="termine, quedo armado y probado")
    turnos.dice("Marcos", Jugada("confirmar", {}), texto="dale")
    assert estado_de(conn, tarea) == "en_revision"
    return tarea


def _con_el_aviso(conn, mundo, turnos, **kw) -> tuple[str, IAQueRedacta]:
    """La entrega y su aviso a Ismael, ya salido (terminado el margen para corregir)."""
    tarea = _entregada(conn, mundo, turnos, **kw)
    ia = IAQueRedacta()
    assert enviar(conn, mundo, ia, DESPUES_DEL_MARGEN) == {"enviado": 1}
    return tarea, ia


def _hecho(r, jugada: str) -> dict:
    return next(h for h in r.hechos if h.get("jugada") == jugada)


def _token(conn, etiqueta: str, tarea: str | None = None) -> str:
    filas = todos(conn, """select o.token from conversation_option o
                             join conversation_question q on q.id = o.question_id
                            where o.etiqueta = %s
                              and (%s::uuid is null or o.valor ->> 'tarea' = %s::text)
                            order by q.abierta_en desc""", etiqueta, tarea, tarea)
    return filas[0]["token"]


def _decisiones(conn, tarea: str) -> list[tuple[str, str | None]]:
    return [(f["decision"], f["comentario"]) for f in todos(
        conn, """select decision::text decision, comentario from approval
                  where sujeto_id = %s order by at""", tarea)]


def _salida_para(conn, mundo, nombre: str) -> list[dict]:
    return todos(conn, """select cuerpo, es_respuesta from message_outbox
                           where chat_id = %s and not es_respuesta order by dedupe_key""",
                 mundo["personas"][nombre]["telegram"])


# --- La lista cerrada -----------------------------------------------------------------------

def test_aprobar_y_pedir_cambios_son_fichas_de_la_lista_cerrada():
    for nombre, boton in (("aprobar", "Aprobar"), ("pedir_cambios", "Pedir cambios")):
        ficha = FICHAS[nombre]
        assert ficha.se_ofrece and ficha.boton == boton
        assert {"tarea", "comentario", "de"} <= set(ficha.opcional)
        assert preguntas.DECISION_DE_LA_ENTREGA in ficha.contesta
    assert FICHAS["aprobar"].opuesta == "pedir_cambios"
    assert FICHAS["pedir_cambios"].opuesta == "aprobar"


def test_quien_aprueba_ve_las_entregas_que_esperan_su_decision(conn, mundo, turnos):
    _entregada(conn, mundo, turnos)
    turnos.dice("Ismael", texto="hola")
    [entrega] = [t for t in turnos.situacion["tareas"] if t["titulo"] == ENTREGADA]
    assert entrega["para_decidir"] is True and entrega["responsable"] == "Marcos"
    assert "id" not in entrega
    turnos.dice("Marcos", texto="hola")
    assert not any(t.get("para_decidir") for t in turnos.situacion["tareas"])


# --- Aprobar --------------------------------------------------------------------------------

def test_lo_claro_va_directo_cierra_la_tarea_y_avisa_al_responsable(conn, mundo, turnos):
    tarea = _entregada(conn, mundo, turnos)
    # Sin comentario: con uno, antes pregunta cuál de las dos (decisión 22, más abajo).
    r = turnos.dice("Ismael", Jugada("aprobar", {"tarea": "T1"}), texto="aprobado")

    hecho = _hecho(r, "aprobar")
    assert hecho["resultado"] == "anotado" and hecho["quedo_terminada"] is True
    assert estado_de(conn, tarea) == "terminada"
    assert _decisiones(conn, tarea) == [("aprobado", None)]
    # El aviso al responsable lo redacta el motor y sale enseguida; ningún texto fijo.
    [aviso] = avisos_guardados(conn, "tarea_aprobada")
    assert str(aviso["destinatario_membership_id"]) == mundo["personas"]["Marcos"]["membership_id"]
    assert hecho["aviso_al_responsable"]["a"] == "Marcos"
    assert _salida_para(conn, mundo, "Marcos") == []
    ia = IAQueRedacta()
    # Marcos acaba de confirmar la entrega: el aviso le llega cuando pasan 30 minutos sin que
    # escriba (no interrumpir una conversación, decisión 13).
    assert enviar(conn, mundo, ia, turnos._at(None) + timedelta(minutes=30)).get(
        "enviado", 0) >= 1
    hechos = next(h for p in ia.pedidos_de_redaccion for h in p["hechos"]
                  if h["aviso"] == "tarea_aprobada")
    assert hechos["aprobada_por"] == "Ismael" and "comentario" not in hechos
    assert hechos["quedo_terminada"] is True and hechos["necesita_respuesta"] is False


def test_el_responsable_no_aprueba_su_propio_trabajo(conn, mundo, turnos):
    tarea = _entregada(conn, mundo, turnos)
    r = turnos.dice("Marcos", Jugada("aprobar", {"tarea": "T2"}), texto="aprobada")
    hecho = _hecho(r, "aprobar")
    assert hecho["resultado"] == "no_se_puede" and hecho["motivo"] == "su_propio_trabajo"
    assert hecho["quien_aprueba"] == "Ismael"
    assert estado_de(conn, tarea) == "en_revision" and _decisiones(conn, tarea) == []


def test_quien_no_aprueba_ese_trabajo_recibe_un_no_y_nada_cambia(conn, mundo, turnos):
    tarea = _entregada(conn, mundo, turnos)
    _nahuel(conn, mundo)
    r = turnos.dice("Nahuel", Jugada("aprobar", {"de": "marcos"}),
                    texto="lo de marcos aprobalo")
    hecho = _hecho(r, "aprobar")
    assert hecho["resultado"] == "no_se_puede" and hecho["motivo"] == "no_es_quien_aprueba"
    assert hecho["quien_aprueba"] == "Ismael"
    assert estado_de(conn, tarea) == "en_revision" and _decisiones(conn, tarea) == []
    assert avisos_guardados(conn, "tarea_aprobada") == []
    assert cuantas(conn, "incident", "etapa = 'motor_fuera_de_la_lista'") == 0


def test_sin_tarea_con_una_sola_entrega_de_esa_persona_es_esa(conn, mundo, turnos):
    tarea = _entregada(conn, mundo, turnos)
    turnos.dice("Ismael", Jugada("aprobar", {"de": "Marcos"}), texto="lo de marcos aprobado")
    assert estado_de(conn, tarea) == "terminada"


def test_aprobar_exige_la_evidencia_que_pide_la_politica(conn, mundo, turnos):
    """La política de evidencia se cumple con lo entregado vigente: lo retirado no cuenta, y sin
    eso no se aprueba (mecánica §5). A quien aprueba se le dice que la entrega se está
    completando y que se le avisa (decisión 15 del usuario, 2026-10-08)."""
    with admin(conn) as cur:
        cur.execute("""insert into task_evidence_policy (workspace_id, area_id,
                                                         evidencia_requerida, tipos)
                       values (%s, %s, '{explicacion}', %s)""",
                    (mundo["id"], mundo["area"],
                     '{"explicacion": {"clases": ["texto"], "en_palabras": "cómo quedó"}}'))
    conn.commit()
    tarea = _tarea(conn, mundo, pide=("explicacion",))
    turnos.dice("Marcos", Jugada("entregar", {"tarea": "T2", "el_texto_cubre": ["explicacion"],
                                              "lo_descrito_cubre": ["C1"]}),
                texto="quedo armado y probado")
    turnos.dice("Marcos", Jugada("confirmar", {}), texto="dale")
    turnos.dice("Marcos", Jugada("corregir", {"corrige": "entregar", "tarea": "T2",
                                             "saca": ["P1"]}), texto="no, eso no va")
    r = turnos.dice("Ismael", Jugada("aprobar", {"tarea": "T1"}), texto="aprobado")
    hecho = _hecho(r, "aprobar")
    assert hecho["resultado"] == "no_se_puede"
    assert hecho["motivo"] == "la_entrega_se_esta_completando"
    assert hecho["se_le_avisa_cuando_este_completa"] is True
    assert estado_de(conn, tarea) == "en_revision" and _decisiones(conn, tarea) == []


def test_una_tarea_que_no_esta_entregada_no_se_aprueba(conn, mundo, turnos):
    _tarea(conn, mundo)
    r = turnos.dice("Ismael", Jugada("aprobar", {"de": "Marcos"}), texto="aprobado lo de marcos")
    hecho = _hecho(r, "aprobar")
    assert hecho["resultado"] == "no_se_puede" and hecho["motivo"] == "nada_para_decidir"


# --- La aprobación que todavía no puede cerrar ----------------------------------------------

def _con_una_dependencia(conn, mundo, tarea: str) -> str:
    """La tarea espera, con una dependencia bloqueante, otra de Nahuel que está en curso."""
    _nahuel(conn, mundo)
    origen = _tarea(conn, mundo, "Cambiar el switch", quien="Nahuel")
    with admin(conn) as cur:
        cur.execute("""insert into dependency (workspace_id, origen_task_id, destino_task_id,
                                               tipo)
                       values (%s, %s, %s, 'bloqueante')""", (mundo["id"], origen, tarea))
    conn.commit()
    return origen


def _terminar(conn, tarea: str) -> None:
    with admin(conn) as cur:
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind, motivo)
                       values (%s, 'en_curso', 'cancelada', 'persona', 'prueba')""", (tarea,))
    conn.commit()


def test_una_aprobacion_que_no_puede_cerrar_queda_anotada_y_lo_dice(conn, mundo, turnos):
    tarea = _entregada(conn, mundo, turnos)
    _con_una_dependencia(conn, mundo, tarea)
    r = turnos.dice("Ismael", Jugada("aprobar", {"tarea": "T1"}), texto="aprobado")
    hecho = _hecho(r, "aprobar")
    assert hecho["resultado"] == "anotado" and "quedo_terminada" not in hecho
    assert hecho["no_se_cierra_todavia"]["espera_que_terminen"] == [
        {"tarea": "Cambiar el switch", "estado": "en_curso", "responsable": "Nahuel Gimenez"}]
    assert hecho["se_cierra_sola"]["se_avisa_a"] == ["Marcos", "Ismael"]
    assert estado_de(conn, tarea) == "en_revision"
    assert _decisiones(conn, tarea) == [("aprobado", None)]
    # Otra vez "aprobado": ya la aprobó, no se anota dos veces.
    r = turnos.dice("Ismael", Jugada("aprobar", {"tarea": "T1"}), texto="aprobado")
    assert _hecho(r, "aprobar")["motivo"] == "ya_la_aprobo"
    assert len(_decisiones(conn, tarea)) == 1


def test_cuando_se_resuelve_lo_que_faltaba_el_codigo_la_cierra_solo(conn, mundo, turnos):
    tarea = _entregada(conn, mundo, turnos)
    origen = _con_una_dependencia(conn, mundo, tarea)
    turnos.dice("Ismael", Jugada("aprobar", {"tarea": "T1"}), texto="aprobado")
    cuando = turnos._at(None)
    assert aprobacion.cerrar_las_que_ya_pueden(conn, mundo["id"], RelojFijo(cuando)) == 0
    conn.commit()
    assert estado_de(conn, tarea) == "en_revision"

    _terminar(conn, origen)
    assert aprobacion.cerrar_las_que_ya_pueden(conn, mundo["id"], RelojFijo(cuando)) == 1
    conn.commit()
    assert estado_de(conn, tarea) == "terminada"
    assert len(_decisiones(conn, tarea)) == 1          # nadie tuvo que volver a aprobarla
    cierre = uno(conn, """select actor_kind::text actor, motivo from task_state_event
                           where task_id = %s and estado_nuevo = 'terminada'""", tarea)
    assert cierre["actor"] == "sistema"
    auditado = uno(conn, """select actor_kind::text actor, detalle from audit_log
                             where accion = 'herramienta:cerrar_tarea_aprobada'""")
    assert auditado["actor"] == "leda"
    avisos = avisos_guardados(conn, "cerrada_con_la_aprobacion")
    destinos = sorted(str(a["destinatario_membership_id"]) for a in avisos)
    assert destinos == sorted([mundo["personas"]["Marcos"]["membership_id"],
                               mundo["personas"]["Ismael"]["membership_id"]])
    # Una segunda vuelta no la vuelve a cerrar ni a avisar.
    assert aprobacion.cerrar_las_que_ya_pueden(conn, mundo["id"], RelojFijo(cuando)) == 0
    conn.commit()
    assert len(avisos_guardados(conn, "cerrada_con_la_aprobacion")) == 2
    ia = IAQueRedacta()
    enviar(conn, mundo, ia, cuando + timedelta(minutes=30))     # sin interrumpir (decisión 13)
    hechos = [h for p in ia.pedidos_de_redaccion for h in p["hechos"]
              if h["aviso"] == "cerrada_con_la_aprobacion"]
    assert len(hechos) == 2
    assert all(h["aprobada_por"] == "Ismael" and h["quedo_terminada"] is True for h in hechos)
    assert all(h["se_resolvio"] == {"tareas_que_esperaba": [
        {"tarea": "Cambiar el switch", "estado": "cancelada"}]} for h in hechos)


def test_sin_aprobacion_el_codigo_nunca_cierra_una_tarea_entregada(conn, mundo, turnos):
    tarea = _entregada(conn, mundo, turnos)
    assert aprobacion.cerrar_las_que_ya_pueden(conn, mundo["id"], RelojFijo(AHORA)) == 0
    conn.commit()
    assert estado_de(conn, tarea) == "en_revision"


def test_un_pedido_de_cambios_deja_sin_efecto_la_aprobacion_anotada(conn, mundo, turnos):
    tarea = _entregada(conn, mundo, turnos)
    origen = _con_una_dependencia(conn, mundo, tarea)
    turnos.dice("Ismael", Jugada("aprobar", {"tarea": "T1"}), texto="aprobado")
    turnos.dice("Ismael", Jugada("pedir_cambios", {"tarea": "T1", "comentario": "falta la foto"}),
                texto="mejor no, falta la foto")
    _terminar(conn, origen)
    assert aprobacion.cerrar_las_que_ya_pueden(conn, mundo["id"], RelojFijo(AHORA)) == 0
    conn.commit()
    assert estado_de(conn, tarea) == "en_curso"


# --- Pedir cambios --------------------------------------------------------------------------

def test_pedir_cambios_con_su_comentario_devuelve_la_tarea_y_avisa(conn, mundo, turnos):
    tarea = _entregada(conn, mundo, turnos)
    r = turnos.dice("Ismael", Jugada("pedir_cambios", {"tarea": "T1",
                                                      "comentario": "falta el diagrama"}),
                    texto="le falta el diagrama")
    hecho = _hecho(r, "pedir_cambios")
    assert hecho["resultado"] == "anotado" and hecho["estado"] == "en_curso"
    assert estado_de(conn, tarea) == "en_curso"
    assert _decisiones(conn, tarea) == [("rechazado", "falta el diagrama")]
    assert _salida_para(conn, mundo, "Marcos") == []
    ia = IAQueRedacta()
    enviar(conn, mundo, ia, turnos._at(None) + timedelta(minutes=30))   # sin interrumpir
    hechos = next(h for p in ia.pedidos_de_redaccion for h in p["hechos"]
                  if h["aviso"] == "pedido_de_cambios")
    assert hechos["pidio_cambios"] == "Ismael" and hechos["comentario"] == "falta el diagrama"
    assert hechos["estado"] == "en_curso" and hechos["vence"] == "2026-10-16"


def test_pedir_cambios_sin_decir_que_falta_lo_pregunta_y_no_cambia_nada(conn, mundo, turnos):
    tarea = _entregada(conn, mundo, turnos)
    r = turnos.dice("Ismael", Jugada("pedir_cambios", {"tarea": "T1"}), texto="pedile cambios")
    hecho = _hecho(r, "pedir_cambios")
    assert hecho["resultado"] == "falta_dato" and hecho["falta"] == ["comentario"]
    assert hecho["pregunta"] == preguntas.QUE_CAMBIOS_PIDE
    assert estado_de(conn, tarea) == "en_revision" and _decisiones(conn, tarea) == []
    r = turnos.dice("Ismael", Jugada("pedir_cambios", {"tarea": "T1", "comentario": "el cable"}),
                    texto="que revise el cable")
    assert estado_de(conn, tarea) == "en_curso"
    assert preguntas.QUE_CAMBIOS_PIDE not in {
        f["tipo"] for f in todos(conn, "select tipo from conversation_question "
                                       "where cerrada_en is null")}


# --- El aviso de la entrega, con sus botones -----------------------------------------------

def test_el_aviso_de_la_entrega_ofrece_aprobar_y_pedir_cambios(conn, mundo, turnos):
    tarea, ia = _con_el_aviso(conn, mundo, turnos)
    [pedido] = ia.pedidos_de_redaccion
    [hechos] = pedido["hechos"]
    assert hechos["necesita_respuesta"] is True
    assert hechos["pregunta"] == preguntas.DECISION_DE_LA_ENTREGA
    assert pedido["pregunta"]["tipo"] == preguntas.DECISION_DE_LA_ENTREGA
    assert [o["etiqueta"] for o in pedido["pregunta"]["opciones"]] == ["Aprobar",
                                                                       "Pedir cambios"]
    # Lo ofrecido no es un tema abierto: Ismael no le debe una respuesta a la conversación.
    ofrecida = uno(conn, "select * from conversation_question where tipo = %s",
                   preguntas.DECISION_DE_LA_ENTREGA)
    assert ofrecida["para_despues_en"] is None and ofrecida["cerrada_en"] is None
    assert uno(conn, "select pregunta_abierta_id from conversation_state where membership_id = %s",
               mundo["personas"]["Ismael"]["membership_id"])["pregunta_abierta_id"] is None
    # Los botones van con el texto del aviso.
    transporte = TransporteDePrueba()
    Ciclo(conn, mundo["id"], IAQueRedacta(), RelojFijo(DESPUES_DEL_MARGEN), transporte,
          seguimiento=False).vuelta()
    [entregado] = [e for e in transporte.enviados
                   if e.chat_id == mundo["personas"]["Ismael"]["telegram"]]
    assert [b.etiqueta for b in entregado.botones] == ["Aprobar", "Pedir cambios"]


def test_tocar_aprobar_aprueba_una_sola_vez(conn, mundo, turnos):
    tarea, _ = _con_el_aviso(conn, mundo, turnos)
    token = _token(conn, "Aprobar", tarea)
    r = turnos.toca("Ismael", token)
    assert _hecho(r, "aprobar")["resultado"] == "anotado"
    assert estado_de(conn, tarea) == "terminada"
    assert turnos.toca("Ismael", token).repetido
    assert _decisiones(conn, tarea) == [("aprobado", None)]


def test_el_boton_de_una_entrega_ya_decidida_no_hace_nada_y_lo_dice(conn, mundo, turnos):
    tarea, _ = _con_el_aviso(conn, mundo, turnos)
    turnos.dice("Ismael", Jugada("aprobar", {"tarea": "T1"}), texto="aprobado")
    r = turnos.toca("Ismael", _token(conn, "Aprobar", tarea))
    hecho = r.hechos[0]
    assert hecho["resultado"] == "sin_efecto" and hecho["motivo"] == "pregunta_cerrada"
    assert _decisiones(conn, tarea) == [("aprobado", None)]


def test_el_boton_de_un_aviso_cuya_entrega_cambio_no_vale(conn, mundo, turnos):
    """La guarda (ADR 0018, decisión 2): lo que se aprueba con el botón es lo que mostró el
    aviso. Si la entrega cambió desde entonces, el toque no aprueba."""
    # Sin criterio de aceptación ni política: retirar lo escrito cambia la entrega y no la deja
    # incompleta (eso es la decisión 15, abajo).
    tarea, _ = _con_el_aviso(conn, mundo, turnos, criterio=None)
    turnos.dice("Marcos", Jugada("corregir", {"corrige": "entregar", "tarea": "T2",
                                             "saca": ["P1"]}), texto="eso no iba")
    r = turnos.toca("Ismael", _token(conn, "Aprobar", tarea))
    hecho = _hecho(r, "aprobar")
    assert hecho["resultado"] == "no_se_puede" and hecho["motivo"] == "cambio_la_entrega"
    assert estado_de(conn, tarea) == "en_revision" and _decisiones(conn, tarea) == []


def test_aprobar_mientras_la_entrega_se_completa_no_cambia_nada_y_lo_dice(conn, mundo, turnos):
    """Decisión 15 del usuario (2026-10-08): el aviso ya salió y Marcos retiró lo que decía el
    criterio. Tocar Aprobar no cambia nada: la entrega se está completando, y a quien aprueba le
    llega un aviso nuevo cuando esté completa."""
    tarea, _ = _con_el_aviso(conn, mundo, turnos)
    turnos.dice("Marcos", Jugada("corregir", {"corrige": "entregar", "tarea": "T2",
                                             "saca": ["P1"]}), texto="eso no iba")
    r = turnos.toca("Ismael", _token(conn, "Aprobar", tarea))
    hecho = _hecho(r, "aprobar")
    assert hecho["resultado"] == "no_se_puede"
    assert hecho["motivo"] == "la_entrega_se_esta_completando"
    assert hecho["se_le_avisa_cuando_este_completa"] is True
    assert estado_de(conn, tarea) == "en_revision" and _decisiones(conn, tarea) == []


def test_tocar_pedir_cambios_pregunta_que_falta_y_lo_escrito_lo_completa(conn, mundo, turnos):
    tarea, _ = _con_el_aviso(conn, mundo, turnos)
    r = turnos.toca("Ismael", _token(conn, "Pedir cambios", tarea))
    hecho = _hecho(r, "pedir_cambios")
    assert hecho["resultado"] == "falta_dato" and hecho["pregunta"] == preguntas.QUE_CAMBIOS_PIDE
    assert estado_de(conn, tarea) == "en_revision"
    assert r.pregunta["tipo"] == preguntas.QUE_CAMBIOS_PIDE and "opciones" not in r.pregunta
    turnos.dice("Ismael", Jugada("pedir_cambios", {"tarea": "T1",
                                                  "comentario": "falta el diagrama"}),
                texto="le falta el diagrama")
    assert estado_de(conn, tarea) == "en_curso"
    assert _decisiones(conn, tarea) == [("rechazado", "falta el diagrama")]


# --- Lo que admite dos lecturas -------------------------------------------------------------

def test_aprobar_y_pedir_cambios_juntos_no_hacen_nada_y_preguntan_cual(conn, mundo, turnos):
    tarea = _entregada(conn, mundo, turnos)
    comentario = "que revise los colores"
    r = turnos.dice("Ismael", Jugada("aprobar", {"tarea": "T1", "comentario": comentario}),
                    Jugada("pedir_cambios", {"tarea": "T1", "comentario": comentario}),
                    texto="aprobado, pero que revise los colores")
    [hecho] = r.hechos
    assert hecho["resultado"] == "dos_lecturas"
    assert hecho["lecturas"] == ["aprobar", "pedir_cambios"]
    assert r.pregunta["tipo"] == preguntas.CUAL_DE_LAS_DOS
    assert [o["etiqueta"] for o in r.pregunta["opciones"]] == ["Aprobar", "Pedir cambios"]
    assert estado_de(conn, tarea) == "en_revision" and _decisiones(conn, tarea) == []

    # Escrito vale igual que el botón: la primera lectura aprueba con el comentario, que va al
    # responsable como comentario y no como un pedido de cambios (decisión 12).
    r = turnos.dice("Ismael", Jugada("elegir", {"opcion": "O1"}),
                    texto="aprobala nomas y pasale lo de los colores")
    assert estado_de(conn, tarea) == "terminada"
    assert _decisiones(conn, tarea) == [("aprobado", comentario)]
    [aviso] = avisos_guardados(conn, "tarea_aprobada")
    assert aviso["hechos"]["comentario"] == comentario
    assert avisos_guardados(conn, "pedido_de_cambios") == []


# --- Aprobar con un comentario (decisión 22 del usuario, 2026-10-08) --------------------------

def test_aprobar_con_un_comentario_pregunta_cual_de_las_dos_antes_de_cerrar(conn, mundo,
                                                                            turnos):
    """D7 (la 28, paso 3, 1 de 5 con la IA real): "esta bien pero que mariano revise el rotulo de
    los cables" llegó como `aprobar` con su comentario, sin `pedir_cambios`, y la tarea quedó
    terminada. Lo decide la cocina, no la IA: una aprobación que trae un comentario para el
    responsable nunca cierra directo; Leda pregunta una vez cuál de las dos."""
    tarea = _entregada(conn, mundo, turnos)
    comentario = "que revise el rotulo de los cables"
    r = turnos.dice("Ismael", Jugada("aprobar", {"tarea": "T1", "comentario": comentario}),
                    texto="esta bien pero que revise el rotulo de los cables")
    [hecho] = r.hechos
    assert hecho["jugada"] == "aprobar" and hecho["resultado"] == "dos_lecturas"
    assert hecho["lecturas"] == ["aprobar", "pedir_cambios"]
    assert r.pregunta["tipo"] == preguntas.CUAL_DE_LAS_DOS
    assert [o["etiqueta"] for o in r.pregunta["opciones"]] == ["Aprobar", "Pedir cambios"]
    assert estado_de(conn, tarea) == "en_revision" and _decisiones(conn, tarea) == []
    assert avisos_guardados(conn, "tarea_aprobada") == []

    # La respuesta es la elección: el botón Aprobar aprueba con el comentario, sin otra pregunta.
    r = turnos.toca("Ismael", _token(conn, "Aprobar", tarea))
    assert _hecho(r, "aprobar")["resultado"] == "anotado"
    assert estado_de(conn, tarea) == "terminada"
    assert _decisiones(conn, tarea) == [("aprobado", comentario)]
    [aviso] = avisos_guardados(conn, "tarea_aprobada")
    assert aviso["hechos"]["comentario"] == comentario


def test_la_pregunta_de_un_comentario_tambien_deja_pedir_el_cambio(conn, mundo, turnos):
    tarea = _entregada(conn, mundo, turnos)
    comentario = "que revise el rotulo de los cables"
    turnos.dice("Ismael", Jugada("aprobar", {"tarea": "T1", "comentario": comentario}),
                texto="esta bien pero que revise el rotulo de los cables")
    r = turnos.dice("Ismael", Jugada("elegir", {"opcion": "O2"}), texto="pedile el cambio")
    assert _hecho(r, "pedir_cambios")["resultado"] == "anotado"
    assert _decisiones(conn, tarea) == [("rechazado", comentario)]
    assert avisos_guardados(conn, "tarea_aprobada") == []


@pytest.mark.parametrize("dos_jugadas", [True, False])
def test_aprobar_con_un_comentario_que_contesta_cual_de_las_dos_aprueba_directo(
        conn, mundo, turnos, dos_jugadas):
    """Decisión 12: "aprobala nomás y pasale lo de los colores", escrito como `aprobar` con su
    comentario, es la respuesta a la pregunta abierta: aprueba y pasa el comentario, sin otra
    pregunta. Igual si la pregunta la abrieron las dos jugadas o una aprobación con comentario."""
    tarea = _entregada(conn, mundo, turnos)
    jugadas = [Jugada("aprobar", {"tarea": "T1", "comentario": "que revise los colores"})]
    if dos_jugadas:
        jugadas.append(Jugada("pedir_cambios",
                              {"tarea": "T1", "comentario": "que revise los colores"}))
    r = turnos.dice("Ismael", *jugadas, texto="aprobado, pero que revise los colores")
    assert r.pregunta["tipo"] == preguntas.CUAL_DE_LAS_DOS
    r = turnos.dice("Ismael", Jugada("aprobar", {"tarea": "T1",
                                                 "comentario": "pasale lo de los colores"}),
                    texto="aprobala nomas y pasale lo de los colores")
    hecho = _hecho(r, "aprobar")
    assert hecho["resultado"] == "anotado" and hecho["quedo_terminada"] is True
    assert r.pregunta is None
    assert estado_de(conn, tarea) == "terminada"
    assert _decisiones(conn, tarea) == [("aprobado", "pasale lo de los colores")]
    assert cuantas(conn, "conversation_question",
                   "tipo = %s and cerrada_en is null", preguntas.CUAL_DE_LAS_DOS) == 0


def test_aprobar_sin_comentario_sigue_yendo_directo(conn, mundo, turnos):
    tarea = _entregada(conn, mundo, turnos)
    r = turnos.dice("Ismael", Jugada("aprobar", {"tarea": "T1"}), texto="aprobado")
    assert _hecho(r, "aprobar")["resultado"] == "anotado" and r.pregunta is None
    assert estado_de(conn, tarea) == "terminada"


def test_el_comentario_de_una_aprobacion_es_algo_para_el_responsable():
    """La IA sólo dice que la aprobación trae un comentario (decisión 22): el dato dice qué es."""
    from leda.motor.ia_real import DATOS
    assert "persona responsable" in DATOS["comentario"][1]
    assert "persona responsable" in FICHAS["aprobar"].es


def _botones_de_la_respuesta(conn, mundo, at, nombre: str = "Ismael") -> list[str]:
    transporte = TransporteDePrueba()
    Ciclo(conn, mundo["id"], IAQueRedacta(), RelojFijo(at), transporte, seguimiento=False).vuelta()
    respuestas = [e for e in transporte.enviados
                  if e.chat_id == mundo["personas"][nombre]["telegram"]]
    return [b.etiqueta for b in respuestas[-1].botones]


def _cual_de_las_dos(conn, mundo, turnos, comentario: str) -> str:
    tarea = _entregada(conn, mundo, turnos)
    turnos.dice("Ismael", Jugada("aprobar", {"tarea": "T1", "comentario": comentario}),
                Jugada("pedir_cambios", {"tarea": "T1", "comentario": comentario}),
                texto="aprobado, pero que revise los colores")
    return tarea


def test_si_la_respuesta_no_elige_leda_no_decide_ni_repite_la_pregunta(conn, mundo, turnos):
    """Decisión 12 del usuario (2026-10-08): "y bueno, fijate vos" no elige. Leda no decide: la
    entrega sigue esperando su decisión, con los dos botones en la respuesta, y la pregunta no se
    repite (se cierra sin elegir)."""
    comentario = "que revise los colores"
    tarea = _cual_de_las_dos(conn, mundo, turnos, comentario)
    r = turnos.dice("Ismael", texto="y bueno, fijate vos")
    [hecho] = r.hechos
    assert hecho["resultado"] == "no_eligio"
    assert hecho["pregunta_hecha_una_vez"] == preguntas.CUAL_DE_LAS_DOS
    assert hecho["tarea"]["titulo"] == ENTREGADA
    assert hecho["botones"] == ["Aprobar", "Pedir cambios"]
    assert r.pregunta is None
    assert estado_de(conn, tarea) == "en_revision" and _decisiones(conn, tarea) == []
    cual = uno(conn, "select * from conversation_question where tipo = %s",
               preguntas.CUAL_DE_LAS_DOS)
    assert cual["cerrada_en"] is not None and cual["cierre"] == "sin_efecto"
    # Los botones van con la respuesta, y no es un tema abierto.
    assert _botones_de_la_respuesta(conn, mundo, turnos._at(None)) == ["Aprobar",
                                                                       "Pedir cambios"]
    assert uno(conn, "select pregunta_abierta_id from conversation_state where membership_id = %s",
               mundo["personas"]["Ismael"]["membership_id"])["pregunta_abierta_id"] is None
    # Otro mensaje sin elegir no vuelve a preguntar nada.
    r = turnos.dice("Ismael", texto="ok")
    assert r.pregunta is None and r.hechos == []
    # Tocar uno de esos botones decide, con lo que había dicho.
    r = turnos.toca("Ismael", _token(conn, "Aprobar", tarea))
    assert _hecho(r, "aprobar")["resultado"] == "anotado"
    assert _decisiones(conn, tarea) == [("aprobado", comentario)]


def test_no_elegir_con_algo_fuera_de_la_lista_no_avisa_a_la_administracion(conn, mundo,
                                                                           turnos):
    """D7 (la 28, paso 4, 5 de 5 con la IA real): "y bueno fijate vos" llegó como algo fuera de
    la lista, y cada vez le llegó un aviso a la administración. Es la respuesta a la pregunta
    abierta: la maneja esa pregunta (no eligió: la entrega espera su decisión con los botones)
    y no es un pedido nuevo."""
    tarea = _cual_de_las_dos(conn, mundo, turnos, "que revise los colores")
    r = turnos.dice("Ismael", Jugada("fuera_de_la_lista",
                                     {"que_pide": "que Leda decida por él",
                                      "contesta_la_pregunta": True}),
                    texto="y bueno fijate vos")
    [hecho] = r.hechos
    assert hecho["resultado"] == "no_eligio" and r.pregunta is None
    assert hecho["botones"] == ["Aprobar", "Pedir cambios"]
    assert cuantas(conn, "incident", "etapa = 'motor_fuera_de_la_lista'") == 0
    assert estado_de(conn, tarea) == "en_revision" and _decisiones(conn, tarea) == []


def test_las_dos_lecturas_otra_vez_no_repiten_la_pregunta(conn, mundo, turnos):
    """Si la respuesta vuelve a mezclar aprobar y pedir cambios, tampoco elige: no se repite la
    pregunta, y la entrega sigue esperando con los botones."""
    comentario = "que revise los colores"
    tarea = _cual_de_las_dos(conn, mundo, turnos, comentario)
    r = turnos.dice("Ismael", Jugada("aprobar", {"tarea": "T1", "comentario": comentario}),
                    Jugada("pedir_cambios", {"tarea": "T1", "comentario": comentario}),
                    texto="aprobado pero que revise")
    [hecho] = r.hechos
    assert hecho["resultado"] == "no_eligio" and r.pregunta is None
    assert cuantas(conn, "conversation_question", "tipo = %s", preguntas.CUAL_DE_LAS_DOS) == 1
    assert cuantas(conn, "conversation_question",
                   "tipo = %s and cerrada_en is null", preguntas.CUAL_DE_LAS_DOS) == 0
    assert estado_de(conn, tarea) == "en_revision" and _decisiones(conn, tarea) == []


def test_lo_que_no_elige_en_el_mismo_mensaje_no_cierra_la_pregunta(conn, mundo, turnos):
    """La pregunta se hace una vez: en el mensaje que la abre, todavía no se contestó."""
    _cual_de_las_dos(conn, mundo, turnos, "que revise los colores")
    assert cuantas(conn, "conversation_question",
                   "tipo = %s and cerrada_en is null", preguntas.CUAL_DE_LAS_DOS) == 1


# --- Las entregas en listas (decisión 17 del usuario, 2026-10-08; C-3d, D4) ------------------

OTRA = "Cablear la bomba"


def _dos_entregadas(conn, mundo, turnos) -> tuple[str, str]:
    """Marcos entrega dos tareas, una detrás de otra: sus avisos a Ismael salen juntos."""
    primera = _entregada(conn, mundo, turnos)
    segunda = _entregada(conn, mundo, turnos, titulo=OTRA, alias="T3")
    return primera, segunda


def test_ver_una_entrega_es_una_ficha_de_la_lista_cerrada():
    ficha = FICHAS["ver_entrega"]
    assert ficha.se_ofrece and {"tarea", "de"} <= set(ficha.opcional)


def test_las_entregas_que_salen_juntas_van_en_una_lista_con_un_boton_por_tarea(conn, mundo,
                                                                               turnos):
    _dos_entregadas(conn, mundo, turnos)
    ia = IAQueRedacta()
    assert enviar(conn, mundo, ia, DESPUES_DEL_MARGEN) == {"enviado": 2}
    [pedido] = ia.pedidos_de_redaccion          # un solo mensaje
    for hechos in pedido["hechos"]:
        assert hechos["aviso"] == "entrega_para_aprobar"
        assert hechos["fotos_que_trae"] == 0 and hechos["responsable"] == "Marcos"
        assert "lo_que_entrego" not in hechos and "fotos_adjuntas" not in hechos
        assert "lleva_el_enlace_a_la_pagina_de_la_tarea" not in hechos
        assert hechos["botones"] == [f"Ver {hechos['tarea']}"]
    assert pedido["pregunta"] is None
    assert cuantas(conn, "message_outbox", "not es_respuesta") == 1
    # Sin Aprobar ni Pedir cambios en la lista: se ofrecen al ver cada una.
    assert cuantas(conn, "conversation_question", "tipo = %s",
                   preguntas.DECISION_DE_LA_ENTREGA) == 0
    transporte = TransporteDePrueba()
    Ciclo(conn, mundo["id"], IAQueRedacta(), RelojFijo(DESPUES_DEL_MARGEN), transporte,
          seguimiento=False).vuelta()
    [entregado] = [e for e in transporte.enviados
                   if e.chat_id == mundo["personas"]["Ismael"]["telegram"]]
    assert [b.etiqueta for b in entregado.botones] == [f"Ver {ENTREGADA}", f"Ver {OTRA}"]


def test_las_entregas_que_esperan_mientras_quien_revisa_conversa_salen_en_una_lista(
        conn, mundo, turnos):
    """Dos entregas confirmadas con minutos de diferencia, mientras Ismael conversa con Leda: sus
    avisos esperan juntos (no interrumpir, decisión 13) y salen en una sola lista (decisión 17)
    cuando termina la espera (el `PENDIENTE` de la D4, en la D5 de la C-3d)."""
    turnos.dice("Ismael", texto="hola", at=AHORA)
    _entregada(conn, mundo, turnos)                          # su aviso, a los 10 minutos
    turnos.dice("Ismael", texto="y como viene todo", at=AHORA + timedelta(minutes=11))
    _entregada(conn, mundo, turnos, titulo=OTRA, alias="T3")
    ia = IAQueRedacta()
    assert enviar(conn, mundo, ia, AHORA + timedelta(minutes=13)) == {"en_espera": 1}
    assert enviar(conn, mundo, ia, AHORA + timedelta(minutes=30)) == {"en_espera": 2}
    assert enviar(conn, mundo, ia, AHORA + timedelta(minutes=41)) == {"enviado": 2}
    [pedido] = ia.pedidos_de_redaccion
    assert sorted(h["tarea"] for h in pedido["hechos"]) == sorted([ENTREGADA, OTRA])


def test_ver_una_entrega_la_muestra_con_los_botones_para_decidir(conn, mundo, turnos):
    primera, _ = _dos_entregadas(conn, mundo, turnos)
    enviar(conn, mundo, IAQueRedacta(), DESPUES_DEL_MARGEN)
    # La lista ya salió, con sus botones; lo que sigue es la respuesta al toque.
    assert _botones_de_la_respuesta(conn, mundo, DESPUES_DEL_MARGEN) == [f"Ver {ENTREGADA}",
                                                                         f"Ver {OTRA}"]
    r = turnos.toca("Ismael", _token(conn, f"Ver {ENTREGADA}"), at=DESPUES_DEL_MARGEN)
    hecho = _hecho(r, "ver_entrega")
    assert hecho["resultado"] == "leido" and hecho["tarea"]["titulo"] == ENTREGADA
    assert hecho["responsable"] == "Marcos" and hecho["lo_que_entrego"]
    assert hecho["fotos_adjuntas"] == 0 and hecho["botones"] == ["Aprobar", "Pedir cambios"]
    assert r.pregunta is None
    assert estado_de(conn, primera) == "en_revision" and _decisiones(conn, primera) == []
    assert _botones_de_la_respuesta(conn, mundo, DESPUES_DEL_MARGEN) == ["Aprobar",
                                                                         "Pedir cambios"]
    # El botón de esa respuesta decide sobre lo que mostró.
    turnos.toca("Ismael", _token(conn, "Aprobar", primera))
    assert estado_de(conn, primera) == "terminada"


def test_escribir_que_la_muestre_vale_igual_que_el_boton(conn, mundo, turnos):
    _dos_entregadas(conn, mundo, turnos)
    enviar(conn, mundo, IAQueRedacta(), DESPUES_DEL_MARGEN)
    r = turnos.dice("Ismael", Jugada("ver_entrega", {"tarea": "T2"}),
                    texto="mostrame la de la bomba", at=DESPUES_DEL_MARGEN)
    hecho = _hecho(r, "ver_entrega")
    assert hecho["resultado"] == "leido" and hecho["tarea"]["titulo"] == OTRA


def test_quien_no_la_revisa_no_ve_la_entrega(conn, mundo, turnos):
    _entregada(conn, mundo, turnos)
    r = turnos.dice("Marcos", Jugada("ver_entrega", {"tarea": "T2"}), texto="mostrame")
    assert _hecho(r, "ver_entrega")["resultado"] == "no_se_puede"


def test_despues_de_decidir_una_muestra_lo_que_queda_por_revisar(conn, mundo, turnos):
    primera, segunda = _dos_entregadas(conn, mundo, turnos)
    r = turnos.dice("Ismael", Jugada("aprobar", {"tarea": "T1"}), texto="lo del tablero ok",
                    at=DESPUES_DEL_MARGEN)
    hecho = _hecho(r, "aprobar")
    assert hecho["quedo_terminada"] is True
    assert hecho["queda_por_revisar"] == [{"tarea": OTRA, "responsable": "Marcos"}]
    assert _botones_de_la_respuesta(conn, mundo, DESPUES_DEL_MARGEN) == [f"Ver {OTRA}"]
    # Sin insistir: ningún aviso nuevo a Ismael por lo que queda.
    assert [a["tipo"] for a in avisos_guardados(conn)
            if str(a["destinatario_membership_id"])
            == mundo["personas"]["Ismael"]["membership_id"]] == ["entrega_para_aprobar"] * 2
    # Lo ya aprobado que espera otra cosa no queda "por revisar".
    r = turnos.dice("Ismael", Jugada("aprobar", {"tarea": "T1"}), texto="la bomba ok",
                    at=DESPUES_DEL_MARGEN)
    assert "queda_por_revisar" not in _hecho(r, "aprobar")


# --- Si cambia quién aprueba (decisión 16 del usuario, 2026-10-08; C-3d, D4) -----------------

def _ahora_lo_aprueba(conn, mundo, de: str, a: str) -> None:
    """Lo que hace la plataforma: el trabajo de `de` lo aprueba ahora `a`."""
    with admin(conn) as cur:
        cur.execute("update membership set aprobador_membership_id = %s where id = %s",
                    (mundo["personas"][a]["membership_id"], mundo["personas"][de]["membership_id"]))
    conn.commit()


def test_el_aviso_de_la_entrega_va_a_quien_aprueba_al_salir(conn, mundo, turnos):
    _nahuel(conn, mundo)
    _entregada(conn, mundo, turnos)
    _ahora_lo_aprueba(conn, mundo, "Marcos", "Nahuel")      # antes de que salga el aviso
    assert enviar(conn, mundo, IAQueRedacta(), DESPUES_DEL_MARGEN) == {"enviado": 1}
    [aviso] = avisos_guardados(conn, "entrega_para_aprobar")
    assert str(aviso["destinatario_membership_id"]) == mundo["personas"]["Nahuel"]["membership_id"]
    assert aviso["estado"] == "enviado"
    assert _salida_para(conn, mundo, "Ismael") == []


def test_si_cambia_despues_al_nuevo_le_llega_lo_que_espera_su_decision(conn, mundo, turnos):
    from leda.motor.escalera import correr_escalera

    _nahuel(conn, mundo)
    tarea, _ = _con_el_aviso(conn, mundo, turnos)            # ya le llegó a Ismael
    _ahora_lo_aprueba(conn, mundo, "Marcos", "Nahuel")
    luego = DESPUES_DEL_MARGEN + timedelta(minutes=5)
    correr_escalera(conn, mundo["id"], RelojFijo(luego))
    conn.commit()
    nuevo = [a for a in avisos_guardados(conn, "entrega_para_aprobar")
             if str(a["destinatario_membership_id"])
             == mundo["personas"]["Nahuel"]["membership_id"]]
    assert len(nuevo) == 1 and nuevo[0]["hechos"]["antes_la_revisaba_otra_persona"] is True
    ia = IAQueRedacta()
    assert enviar(conn, mundo, ia, luego) == {"enviado": 1}
    # Una vez: otra vuelta de la escalera no guarda otro.
    correr_escalera(conn, mundo["id"], RelojFijo(luego + timedelta(minutes=1)))
    conn.commit()
    assert len(avisos_guardados(conn, "entrega_para_aprobar")) == 2
    # El botón del aviso viejo le dice a Ismael que ya no la revisa él, y no cambia nada.
    [viejo] = todos(conn, """select o.token from conversation_option o
                               join conversation_question q on q.id = o.question_id
                              where o.etiqueta = 'Aprobar' and q.membership_id = %s""",
                    mundo["personas"]["Ismael"]["membership_id"])
    r = turnos.toca("Ismael", viejo["token"], at=luego)
    hecho = _hecho(r, "aprobar")
    assert hecho["resultado"] == "no_se_puede" and hecho["motivo"] == "ya_no_le_corresponde"
    assert hecho["la_revisa_otra_persona"] is True and hecho["estado"] == "en_revision"
    assert _decisiones(conn, tarea) == [] and estado_de(conn, tarea) == "en_revision"


def _al_nuevo(conn, mundo) -> list[dict]:
    return [a for a in avisos_guardados(conn, "entrega_para_aprobar")
            if str(a["destinatario_membership_id"]) == mundo["personas"]["Nahuel"]["membership_id"]]


def test_si_el_nuevo_ya_decidio_no_se_le_guarda_lo_que_espera_su_decision(conn, mundo, turnos):
    """La advertencia de la revisión de la D4 (`escalera.py`): el aviso al nuevo se guardaba
    aunque el nuevo ya hubiera aprobado una entrega que todavía no puede cerrar (C-3d, D5)."""
    from leda.motor.escalera import correr_escalera

    tarea, _ = _con_el_aviso(conn, mundo, turnos)            # ya le llegó a Ismael
    _con_una_dependencia(conn, mundo, tarea)                 # y no puede cerrar todavía
    _ahora_lo_aprueba(conn, mundo, "Marcos", "Nahuel")
    luego = DESPUES_DEL_MARGEN + timedelta(minutes=5)
    r = turnos.dice("Nahuel", Jugada("aprobar", {"de": "Marcos"}), texto="lo de marcos ok",
                    at=luego)
    assert _hecho(r, "aprobar")["resultado"] == "anotado"
    assert estado_de(conn, tarea) == "en_revision"
    correr_escalera(conn, mundo["id"], RelojFijo(luego + timedelta(minutes=1)))
    conn.commit()
    assert _al_nuevo(conn, mundo) == []


def test_si_el_nuevo_decide_antes_de_que_salga_el_aviso_se_omite(conn, mundo, turnos):
    """Al salir se relee (9b): si quien lo recibe ya decidió (una aprobación que todavía no
    cierra también es su decisión), el aviso de lo que espera su decisión no sale."""
    from leda.motor.escalera import correr_escalera

    tarea, _ = _con_el_aviso(conn, mundo, turnos)
    _con_una_dependencia(conn, mundo, tarea)
    _ahora_lo_aprueba(conn, mundo, "Marcos", "Nahuel")
    # Fuera del horario: la escalera lo guarda para el día hábil siguiente.
    noche = AHORA + timedelta(hours=10)
    correr_escalera(conn, mundo["id"], RelojFijo(noche))
    conn.commit()
    [guardado] = _al_nuevo(conn, mundo)
    assert guardado["estado"] == "guardado"
    turnos.dice("Nahuel", Jugada("aprobar", {"de": "Marcos"}), texto="lo de marcos ok",
                at=noche + timedelta(minutes=1))
    enviar(conn, mundo, IAQueRedacta(), guardado["programado_para"] + timedelta(hours=2))
    [aviso] = _al_nuevo(conn, mundo)
    assert aviso["estado"] == "omitido" and aviso["motivo_omision"] == "ya_decidio"
