"""La entrega con evidencia en el motor (`leda.motor.entrega`; ADR 0019, decisiones 4 y 5; ADR
0018, decisiones 2 y 4; porción 2 de la C-3).

"Terminé" lleva a una vista previa que muestra cada pieza y qué cubre, también lo mandado antes
durante la tarea, que entra sólo si queda; sin la política completa, Leda dice qué falta y la
tarea no se mueve; con la política completa, se confirma con el botón o por escrito, con la
guarda: lo último que la persona vio y sin cambios. Al confirmar, las piezas y el paso a
revisión van en un solo acto; nunca a terminada. Un archivo sin una entrega abierta lleva la
pregunta de para qué tarea es; con una abierta, se suma solo. Una pieza se saca de la vista
previa o, entregada, se retira: nada se borra.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from leda.autoridad import identificar_en_espacio
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.motor import avisos, entrega, hechos
from leda.motor.fichas import FICHAS
from leda.motor.ia import IAGuionada, Jugada
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import procesar_toque, procesar_turno

from tests.motor.ayudantes import (AHORA, VIERNES_16, IAQueRedacta, a_la_vista, avisos_guardados,
                                   cuantas, enviar, estado_de, solo_si_pregunta, todos, uno)

TIPOS = {"explicacion": {"clases": ["texto"], "en_palabras": "cómo quedó el trabajo"},
         "foto": {"clases": ["imagen"], "en_palabras": "una foto del trabajo terminado"},
         "archivo": {"clases": ["archivo", "imagen", "enlace"],
                     "en_palabras": "un archivo del trabajo"},
         "resultado_de_prueba": {"clases": ["texto", "archivo", "imagen", "enlace"],
                                 "en_palabras": "cómo se probó"}}
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01"
ZIP = b"PK\x03\x04" + b"\x00" * 40


# --- Ayudas ---------------------------------------------------------------------------------

def _tarea(conn, mundo, pide=("explicacion", "foto"), titulo="Armar el tablero",
           estado="en_curso", criterio: str | None = None) -> str:
    """Una tarea de Marcos que pide `pide`, con la política del área (sus clases, del pack) y,
    si se da, su criterio de aceptación."""
    with admin(conn) as cur:
        cur.execute("""insert into task_evidence_policy (workspace_id, area_id,
                                                         evidencia_requerida, tipos)
                       values (%s, %s, %s, %s)
                       on conflict (workspace_id, area_id) do update
                          set evidencia_requerida = excluded.evidencia_requerida""",
                    (mundo["id"], mundo["area"], list(pide), json.dumps(TIPOS)))
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, estado, fecha_objetivo,
                                 evidencia_requerida, criterio_aceptacion)
               values (%s, %s, %s, %s, %s, %s, %s, %s, %s) returning id""",
            (mundo["id"], mundo["objetivo"], titulo, mundo["area"],
             mundo["personas"]["Marcos"]["membership_id"], estado, VIERNES_16, list(pide),
             criterio))
        tarea = str(cur.fetchone()["id"])
    conn.commit()
    return tarea


class Marcos:
    """Los mensajes de Marcos, con archivos si los trae, y la IA guionada de cada uno."""

    def __init__(self, conn, mundo) -> None:
        self.conn, self.mundo = conn, mundo
        self.persona = mundo["personas"]["Marcos"]
        self.ia: IAGuionada | None = None
        self.minuto = 0

    def _quien(self, cur):
        return identificar_en_espacio(cur, self.persona["telegram"], self.mundo["id"])

    def manda(self, *jugadas: Jugada, texto: str = "", archivos=(), rechazos=()):
        """Un mensaje: `archivos`, (contenido, que_llego, nombre); `rechazos`, lo que llegó y
        no se guardó (su motivo)."""
        self.minuto += 1
        at = AHORA + timedelta(minutes=self.minuto)
        with espacio(self.conn, self.mundo["id"]) as cur:
            quien = self._quien(cur)
            cur.execute(
                """insert into inbound_message (workspace_id, telegram_message_id, chat_id,
                                                app_user_id, texto, at)
                   values (%s, %s, %s, %s, %s, %s) returning id""",
                (self.mundo["id"], uuid.uuid4().int % 1_000_000, self.persona["telegram"],
                 self.persona["app_user_id"], texto, at))
            entrante = str(cur.fetchone()["id"])
            for i, (contenido, que, nombre) in enumerate(archivos):
                contenido = contenido + uuid.uuid4().bytes
                cur.execute(
                    """insert into archivo (workspace_id, contenido, sha256, tamano, tipo,
                                            clase, nombre_original,
                                            enviado_por_membership_id, recibido_en)
                       values (%s, %s, %s, %s, 'x', %s, %s, %s, %s) returning id""",
                    (self.mundo["id"], contenido, hashlib.sha256(contenido).hexdigest(),
                     len(contenido), "imagen" if que == "foto" else "comprimido", nombre,
                     self.persona["membership_id"], at))
                archivo = str(cur.fetchone()["id"])
                cur.execute(
                    """insert into archivo_de_mensaje (workspace_id, inbound_message_id,
                                                       archivo_id, que_llego, nombre_original,
                                                       telegram_message_id, telegram_file_id,
                                                       telegram_file_unique_id)
                       values (%s, %s, %s, %s, %s, %s, 'f', 'u')""",
                    (self.mundo["id"], entrante, archivo, que, nombre, i + 1))
            for j, motivo in enumerate(rechazos):
                cur.execute(
                    """insert into archivo_de_mensaje (workspace_id, inbound_message_id,
                                                       que_llego, rechazo, telegram_message_id,
                                                       telegram_file_id,
                                                       telegram_file_unique_id)
                       values (%s, %s, 'video', %s, %s, 'f', 'u')""",
                    (self.mundo["id"], entrante, motivo, 100 + j))
        self.conn.commit()
        self.ia = IAGuionada(jugadas=[list(jugadas)], redacciones=["Listo."])
        r = procesar_turno(self.conn, quien, entrante, self.ia, RelojFijo(at))
        self.conn.commit()
        assert r.error is None, r.error
        return r

    def toca(self, token: str):
        self.minuto += 1
        with espacio(self.conn, self.mundo["id"]) as cur:
            quien = self._quien(cur)
        self.conn.commit()
        self.ia = IAGuionada(redacciones=["Listo."])
        r = procesar_toque(self.conn, quien, token, self.persona["telegram"], self.ia,
                           RelojFijo(AHORA + timedelta(minutes=self.minuto)))
        self.conn.commit()
        return r

    @property
    def situacion(self) -> dict:
        return self.ia.pedidos_de_jugadas[-1]

    @property
    def redaccion(self) -> dict:
        return self.ia.pedidos_de_redaccion[-1]


@pytest.fixture
def marcos(conn, mundo) -> Marcos:
    return Marcos(conn, mundo)


def _hecho(r, jugada: str) -> dict:
    return next(h for h in r.hechos if h.get("jugada") == jugada)


def _token_de(conn, etiqueta: str = "Confirmar", *, de_hace: int = 0) -> str:
    filas = todos(conn, """select o.token from conversation_option o
                             join conversation_question q on q.id = o.question_id
                            where o.etiqueta = %s order by q.abierta_en desc""", etiqueta)
    return filas[de_hace]["token"]


def _entregar(tarea: str = "T2", **datos) -> Jugada:
    return Jugada("entregar", {"tarea": tarea, **datos})


# --- La lista cerrada -----------------------------------------------------------------------

def test_la_entrega_es_una_ficha_con_su_confirmacion():
    # Sin arrancar también (decisión 14 del usuario, 2026-10-08).
    assert FICHAS["entregar"].estados == frozenset({"asignada", "en_curso"})
    assert FICHAS["entregar"].se_ofrece
    assert "el_texto_cubre" in FICHAS["entregar"].opcional
    assert not FICHAS["confirmar"].se_ofrece and not FICHAS["guardar_para_la_entrega"].se_ofrece
    assert {"saca", "el_texto_cubre"} <= set(FICHAS["corregir"].opcional)


# --- Lo que falta ---------------------------------------------------------------------------

def test_sin_la_politica_completa_dice_que_falta_y_no_mueve_la_tarea(conn, mundo, marcos):
    tarea = _tarea(conn, mundo)
    r = marcos.manda(_entregar(el_texto_cubre=["explicacion"]),
                     texto="termine el tablero, quedo cerrado")

    hecho = _hecho(r, "entregar")
    assert hecho["resultado"] == "le_falta_evidencia"
    assert hecho["le_falta"] == ["una foto del trabajo terminado"]
    assert hecho["entrega"] == [{"pieza": "P1", "es": "lo_que_escribio",
                                 "dice": "termine el tablero, quedo cerrado",
                                 "cubre": ["cómo quedó el trabajo"]}]
    assert hecho["pregunta"] == "lo_que_falta_de_la_entrega"
    assert hecho["al_confirmar"] == {"estado": "en_revision",
                                     "queda_esperando_la_aprobacion_de": "Ismael"}
    assert estado_de(conn, tarea) == "en_curso"
    assert cuantas(conn, "evidence") == 0
    assert cuantas(conn, "conversation_option") == 0      # nada para confirmar: sin botones


def test_una_frase_sola_no_cubre_la_foto_aunque_la_ia_lo_diga(conn, mundo, marcos):
    """La clase la fija el código: un texto no cubre un tipo que no acepta texto."""
    _tarea(conn, mundo)
    r = marcos.manda(_entregar(el_texto_cubre=["explicacion", "foto"]),
                     texto="termine, le saque foto")
    hecho = _hecho(r, "entregar")
    assert hecho["resultado"] == "le_falta_evidencia"
    assert hecho["le_falta"] == ["una foto del trabajo terminado"]


def test_sin_decir_que_cubre_un_texto_cubre_solo_lo_que_nada_mas_un_texto_puede(conn, mundo,
                                                                                 marcos):
    _tarea(conn, mundo, pide=("explicacion", "resultado_de_prueba"))
    hecho = _hecho(marcos.manda(_entregar(), texto="listo, quedo andando"), "entregar")
    assert hecho["entrega"][0]["cubre"] == ["cómo quedó el trabajo"]
    assert hecho["le_falta"] == ["cómo se probó"]

    otra = _hecho(marcos.manda(_entregar(el_texto_cubre=["explicacion", "resultado_de_prueba"]),
                               texto="lo probe 20 ciclos sin falla"), "entregar")
    assert otra["resultado"] == "para_confirmar"


# --- La vista previa y la confirmación ------------------------------------------------------

def test_con_la_politica_completa_muestra_la_entrega_para_confirmar(conn, mundo, marcos):
    tarea = _tarea(conn, mundo)
    r = marcos.manda(_entregar(el_texto_cubre=["explicacion"]), texto="termine el tablero",
                     archivos=[(JPEG, "foto", None)])

    hecho = _hecho(r, "entregar")
    assert hecho["resultado"] == "para_confirmar" and "le_falta" not in hecho
    assert [p["es"] for p in hecho["entrega"]] == ["lo_que_escribio", "una_foto"]
    assert hecho["entrega"][1]["cubre"] == ["una foto del trabajo terminado"]
    assert hecho["pregunta"] == "confirmar_la_entrega"
    assert r.pregunta["opciones"] == [{"opcion": "O1", "etiqueta": "Confirmar"}]
    estado = uno(conn, "select mostrado_para_confirmar m, huella from conversation_state")
    assert estado["m"]["pregunta"] and estado["huella"]
    assert estado_de(conn, tarea) == "en_curso" and cuantas(conn, "evidence") == 0


def test_la_confirmacion_escrita_entrega_en_un_solo_acto_y_nunca_a_terminada(conn, mundo,
                                                                            marcos):
    tarea = _tarea(conn, mundo)
    marcos.manda(_entregar(el_texto_cubre=["explicacion"]), texto="termine el tablero",
                 archivos=[(JPEG, "foto", None)])
    r = marcos.manda(Jugada("confirmar", {}), texto="dale")

    hecho = _hecho(r, "confirmar")
    assert hecho["resultado"] == "entregada" and hecho["estado"] == "en_revision"
    assert hecho["queda_esperando_la_aprobacion_de"] == "Ismael"
    assert hecho["aviso_a_quien_aprueba"]["a"] == "Ismael"
    assert estado_de(conn, tarea) == "en_revision"
    piezas = todos(conn, "select clase, texto, archivo_id, cubre, entregado_por "
                         "from evidence order by at")
    assert [(p["clase"], p["cubre"]) for p in piezas] == [("texto", ["explicacion"]),
                                                         ("imagen", ["foto"])]
    assert all(str(p["entregado_por"]) == mundo["personas"]["Marcos"]["membership_id"]
               for p in piezas)
    assert cuantas(conn, "audit_log", "accion = 'herramienta:entregar_tarea'") == 1
    assert cuantas(conn, "conversation_question", "cerrada_en is null") == 0
    assert uno(conn, "select mostrado_para_confirmar m from conversation_state")["m"] is None
    # Quien aprueba se entera por el aviso del motor, guardado con sus hechos y con el margen
    # para corregir (porción 3a): en el turno no sale nada más que la respuesta.
    assert cuantas(conn, "message_outbox", "not es_respuesta") == 0
    [aviso] = avisos_guardados(conn, "entrega_para_aprobar")
    assert aviso["estado"] == "guardado"
    assert str(aviso["destinatario_membership_id"]) == \
        mundo["personas"]["Ismael"]["membership_id"]
    confirmado = AHORA + timedelta(minutes=2)
    assert aviso["programado_para"] == confirmado + timedelta(minutes=10)
    assert hecho["aviso_a_quien_aprueba"]["llega"] == aviso["programado_para"].isoformat()


def test_la_redaccion_de_la_entrega_nombra_a_quien_la_revisa_solo_si_se_pregunta(conn, mundo,
                                                                                marcos):
    """Decisiones 11 y 18 del usuario (2026-10-08): Leda no nombra por su cuenta a quien aprueba
    el trabajo de la persona ("Ismael será notificado" invitaba a usarlo como motivo); habla de
    la tarea, que pasa a revisión, y de que la persona se entera cuando la revisen. El nombre
    sigue en los hechos de la cocina y le llega a la redacción en `solo_si_pregunta`, para
    contestar si la persona pregunta quién la revisa."""
    _tarea(conn, mundo)
    vista = marcos.manda(_entregar(el_texto_cubre=["explicacion"]), texto="termine el tablero",
                         archivos=[(JPEG, "foto", None)])
    r = marcos.manda(Jugada("confirmar", {}), texto="dale")
    mostrada, entregada = _hecho(vista, "entregar"), _hecho(r, "confirmar")

    # La cocina guarda a quién va el aviso: lo leen las pruebas y la auditoría.
    assert entregada["aviso_a_quien_aprueba"]["a"] == "Ismael"
    for hecho in (mostrada, entregada):
        redactado = hechos.para_redactar(hecho)
        assert "Ismael" not in a_la_vista(redactado), redactado
        assert "Ismael" in solo_si_pregunta(redactado), redactado
    assert hechos.para_redactar(mostrada)["al_confirmar"] == {
        "estado": "en_revision",
        "solo_si_pregunta": {"queda_esperando_la_revision_de": "Ismael"}}
    redactado = hechos.para_redactar(entregada)
    assert redactado["estado"] == "en_revision"
    assert redactado["se_le_avisa_cuando_decida"] is True
    assert redactado["solo_si_pregunta"] == {"queda_esperando_la_revision_de": "Ismael"}
    assert set(redactado["aviso_a_quien_aprueba"]) == {"llega", "solo_si_pregunta"}


def test_una_pieza_que_llega_con_la_confirmacion_la_deja_sin_valor(conn, mundo, marcos):
    """ADR 0018, decisión 2; ADR 0019, decisión 5: si llegó una pieza después de la vista
    previa, la confirmación escrita no vale y Leda muestra lo nuevo."""
    tarea = _tarea(conn, mundo)
    marcos.manda(_entregar(el_texto_cubre=["explicacion"]), texto="termine el tablero",
                 archivos=[(JPEG, "foto", None)])
    r = marcos.manda(Jugada("confirmar", {}), texto="y esta del tablero cerrado. dale",
                     archivos=[(JPEG, "foto", None)])

    hecho = _hecho(r, "confirmar")
    assert hecho["resultado"] == "no_vale_la_confirmacion"
    assert hecho["motivo"] == "llego_algo_despues"
    assert hecho["como_queda"] == "para_confirmar"
    assert len(hecho["entrega"]) == 3 and hecho["sumo"] == ["P3"]
    assert estado_de(conn, tarea) == "en_curso" and cuantas(conn, "evidence") == 0
    vieja = uno(conn, """select cierre, cierre_detalle from conversation_question
                          where cerrada_en is not null""")
    assert vieja["cierre"] == "sin_efecto" and vieja["cierre_detalle"]["reemplazada"] is True

    entregada = _hecho(marcos.manda(Jugada("confirmar", {}), texto="dale"), "confirmar")
    assert entregada["resultado"] == "entregada"
    assert cuantas(conn, "evidence") == 3


def test_confirmar_en_el_mismo_mensaje_que_la_vista_previa_no_vale(conn, mundo, marcos):
    """Lo que se confirma tiene que ser lo último que la persona vio en un mensaje anterior."""
    _tarea(conn, mundo)
    r = marcos.manda(_entregar(el_texto_cubre=["explicacion"]), Jugada("confirmar", {}),
                     texto="termine el tablero, mandalo", archivos=[(JPEG, "foto", None)])
    hecho = _hecho(r, "confirmar")
    assert hecho["resultado"] == "no_vale_la_confirmacion"
    assert hecho["motivo"] == "no_es_lo_ultimo_que_vio"
    assert cuantas(conn, "evidence") == 0


def test_confirmar_nombrando_otra_tarea_no_entrega_la_que_espera(conn, mundo, marcos):
    """Una confirmación sobre una tarea sin entrega para confirmar no confirma la de otra: eso
    sería confundir la tarea. La vista previa que espera sigue abierta."""
    tablero = _tarea(conn, mundo)
    bomba = _tarea(conn, mundo, titulo="Cablear la bomba")
    marcos.manda(_entregar(el_texto_cubre=["explicacion"]), texto="termine el tablero",
                 archivos=[(JPEG, "foto", None)])
    r = marcos.manda(Jugada("confirmar", {"tarea": "T3"}), texto="dale, la de la bomba")

    hecho = _hecho(r, "confirmar")
    assert hecho["resultado"] == "no_se_puede" and hecho["motivo"] == "nada_para_confirmar"
    assert estado_de(conn, tablero) == "en_curso" and estado_de(conn, bomba) == "en_curso"
    assert cuantas(conn, "evidence") == 0
    assert cuantas(conn, "conversation_question",
                   "cerrada_en is null and tipo = 'confirmar_la_entrega'") == 1


def test_confirmar_sin_nada_mostrado_no_hace_nada(conn, mundo, marcos):
    _tarea(conn, mundo)
    hecho = _hecho(marcos.manda(Jugada("confirmar", {}), texto="dale"), "confirmar")
    assert hecho == {"jugada": "confirmar", "resultado": "no_se_puede",
                     "motivo": "nada_para_confirmar"}


def test_el_boton_de_una_vista_previa_reemplazada_no_entrega(conn, mundo, marcos):
    """Situación general 7: un botón viejo no hace nada y lo dice; el de la vigente entrega."""
    tarea = _tarea(conn, mundo)
    marcos.manda(_entregar(el_texto_cubre=["explicacion"]), texto="termine el tablero",
                 archivos=[(JPEG, "foto", None), (JPEG, "foto", None)])
    marcos.manda(Jugada("corregir", {"corrige": "entregar", "tarea": "T2", "saca": ["P3"]}),
                 texto="la segunda foto sacala")

    viejo = marcos.toca(_token_de(conn, de_hace=1))
    [hecho] = viejo.hechos
    assert hecho["resultado"] == "sin_efecto" and hecho["motivo"] == "pregunta_cerrada"
    assert hecho["cerrada_con"]["reemplazada"] is True
    assert viejo.pregunta["tipo"] == "confirmar_la_entrega" and viejo.pregunta["desde_antes"]
    assert estado_de(conn, tarea) == "en_curso"

    nuevo = marcos.toca(_token_de(conn))
    assert _hecho(nuevo, "confirmar")["resultado"] == "entregada"
    assert cuantas(conn, "evidence") == 2 and estado_de(conn, tarea) == "en_revision"


# --- Lo mandado antes y la corrección -------------------------------------------------------

def test_lo_mandado_antes_entra_aparte_y_solo_si_queda(conn, mundo, marcos):
    tarea = _tarea(conn, mundo)
    duda = marcos.manda(archivos=[(JPEG, "foto", None)])
    assert _hecho(duda, "guardar_para_la_entrega")["pregunta"] == "cual_tarea"
    guardada = marcos.manda(Jugada("elegir", {"opcion": "O2"}), texto="es del tablero")
    assert _hecho(guardada, "guardar_para_la_entrega")["para_cuando_la_entregue"] == [
        {"es": "una_foto"}]
    assert cuantas(conn, "archivo_de_tarea", "task_id = %s", tarea) == 1
    assert cuantas(conn, "evidence") == 0

    r = marcos.manda(_entregar(el_texto_cubre=["explicacion"]), texto="termine el tablero")
    hecho = _hecho(r, "entregar")
    assert hecho["resultado"] == "para_confirmar"
    assert hecho["entrega"][1]["es"] == "una_foto"
    assert hecho["entrega"][1]["mandado_antes_el"] == "2026-10-05"

    sin_ella = marcos.manda(Jugada("corregir", {"corrige": "entregar", "tarea": "T2",
                                                "saca": ["P2"]}),
                            texto="la foto de antes sacala")
    corregido = _hecho(sin_ella, "corregir")
    assert corregido["resultado"] == "corregido"
    assert corregido["como_queda"] == "le_falta_evidencia"
    assert corregido["sacadas"][0]["es"] == "una_foto"
    assert corregido["pregunta"] == "lo_que_falta_de_la_entrega"
    assert cuantas(conn, "evidence") == 0


def test_lo_que_llego_y_tomo_una_jugada_no_se_vuelve_a_atender(conn, mundo, marcos):
    """Hallazgo de la D1 (conversación 22, paso 1): si la IA elige guardar el archivo sin decir
    de qué tarea es, la duda de esa jugada ya atendió lo que llegó. Al terminar las jugadas no
    se vuelve a correr la misma jugada (los hechos salían dos veces), y la elección guarda el
    archivo de aquel mensaje."""
    tarea = _tarea(conn, mundo)
    duda = marcos.manda(Jugada("guardar_para_la_entrega", {}), archivos=[(JPEG, "foto", None)])
    assert [h["jugada"] for h in duda.hechos] == ["guardar_para_la_entrega"]
    assert duda.hechos[0]["resultado"] == "falta_dato"
    assert cuantas(conn, "conversation_question", "tipo = 'cual_tarea'") == 1

    guardada = marcos.manda(Jugada("elegir", {"opcion": "O2"}), texto="es del tablero")
    assert _hecho(guardada, "guardar_para_la_entrega")["resultado"] == "anotado"
    assert cuantas(conn, "archivo_de_tarea", "task_id = %s", tarea) == 1


def test_con_una_entrega_abierta_un_archivo_se_suma_solo(conn, mundo, marcos):
    _tarea(conn, mundo)
    marcos.manda(_entregar(el_texto_cubre=["explicacion"]), texto="termine el tablero")
    r = marcos.manda(archivos=[(JPEG, "foto", None)])
    [hecho] = r.hechos
    assert hecho["jugada"] == "entregar" and hecho["resultado"] == "para_confirmar"
    assert hecho["sumo"] == ["P2"]


def test_lo_que_no_se_pudo_recibir_se_cuenta_con_la_entrega_abierta(conn, mundo, marcos):
    _tarea(conn, mundo)
    marcos.manda(_entregar(el_texto_cubre=["explicacion"]), texto="termine el tablero")
    r = marcos.manda(rechazos=["demasiado_grande"])
    [hecho] = r.hechos
    assert hecho["resultado"] == "le_falta_evidencia" and "sumo" not in hecho
    assert r.pregunta["tipo"] == "lo_que_falta_de_la_entrega"


def test_un_enlace_es_una_pieza_de_la_clase_enlace(conn, mundo, marcos):
    _tarea(conn, mundo, pide=("explicacion", "archivo"))
    marcos.manda(_entregar(el_texto_cubre=["explicacion"]), texto="listo, quedo andando")
    r = marcos.manda(texto="https://ejemplo.com/video-de-la-prueba")
    hecho = r.hechos[0]
    assert hecho["resultado"] == "para_confirmar"
    assert hecho["entrega"][1] == {"pieza": "P2", "es": "un_enlace",
                                   "enlace": "https://ejemplo.com/video-de-la-prueba",
                                   "cubre": ["un archivo del trabajo"]}
    marcos.manda(Jugada("confirmar", {}), texto="si")
    assert [f["clase"] for f in todos(conn, "select clase from evidence order by at")] == [
        "texto", "enlace"]


def test_entregada_una_pieza_se_retira_sin_borrar_nada(conn, mundo, marcos):
    tarea = _tarea(conn, mundo)
    marcos.manda(_entregar(el_texto_cubre=["explicacion"]), texto="termine el tablero",
                 archivos=[(JPEG, "foto", None), (JPEG, "foto", None)])
    marcos.manda(Jugada("confirmar", {}), texto="dale")
    marcos.manda(texto="hola")
    entregado = next(t for t in marcos.situacion["tareas"]
                     if t["alias"] == "T2")["lo_entregado"]
    assert [p["pieza"] for p in entregado] == ["P1", "P2", "P3"]

    r = marcos.manda(Jugada("corregir", {"corrige": "entregar", "tarea": "T2", "saca": ["P3"]}),
                     texto="no, esa foto no era")
    hecho = _hecho(r, "corregir")
    assert hecho["resultado"] == "corregido" and hecho["retiradas"][0]["es"] == "una_foto"
    assert "le_falta" not in hecho              # la otra foto sigue cubriendo
    assert cuantas(conn, "evidence") == 3 and cuantas(conn, "evidencia_retirada") == 1
    assert estado_de(conn, tarea) == "en_revision"


def test_la_ia_recibe_lo_que_pide_la_tarea_en_curso(conn, mundo, marcos):
    _tarea(conn, mundo)
    marcos.manda(texto="hola")
    tarea = next(t for t in marcos.situacion["tareas"] if t["alias"] == "T2")
    assert tarea["evidencia_que_pide"] == [
        {"tipo_de_evidencia": "explicacion", "en_palabras": "cómo quedó el trabajo"},
        {"tipo_de_evidencia": "foto", "en_palabras": "una foto del trabajo terminado"}]
    assert "evidencia_que_pide" not in marcos.situacion["tareas"][0]   # sin política


def test_la_redaccion_no_recibe_ni_ids_ni_huellas_ni_codigos_de_la_politica(conn, mundo,
                                                                           marcos):
    _tarea(conn, mundo)
    marcos.manda(_entregar(el_texto_cubre=["explicacion"]), texto="termine el tablero",
                 archivos=[(JPEG, "foto", "tablero.jpg")])
    texto = json.dumps(marcos.redaccion, ensure_ascii=False, default=str)
    huella = uno(conn, "select huella from conversation_state")["huella"]
    archivo = str(uno(conn, "select id from archivo")["id"])
    assert huella not in texto and archivo not in texto
    for codigo in ('"explicacion"', "tipo_de_evidencia", "evidencia_que_pide"):
        assert codigo not in texto, codigo


def test_cada_pieza_cubre_lo_que_solo_ella_puede_cubrir(conn, mundo, marcos):
    """Una foto puede contar como archivo, pero si hay un archivo, la foto cubre la foto y el
    archivo, el archivo (`entrega.cubrir`: las piezas que sirven para menos van primero)."""
    _tarea(conn, mundo, pide=("explicacion", "foto", "archivo"))
    r = marcos.manda(_entregar(el_texto_cubre=["explicacion"]), texto="termine el tablero",
                     archivos=[(JPEG, "foto", None), (JPEG, "foto", None),
                               (ZIP, "archivo", "programa.zip")])
    hecho = _hecho(r, "entregar")
    assert [(p["es"], p["cubre"]) for p in hecho["entrega"]] == [
        ("lo_que_escribio", ["cómo quedó el trabajo"]),
        ("una_foto", ["una foto del trabajo terminado"]),
        ("una_foto", ["una foto del trabajo terminado"]),
        ("un_archivo", ["un archivo del trabajo"])]


# --- El aviso a quien aprueba (ADR 0019, decisión 6; porción 3a) -----------------------------

def _entregada(marcos, archivos=((JPEG, "foto", None), (JPEG, "foto", None))):
    """Marcos entrega con su texto y `archivos`, y confirma por escrito."""
    marcos.manda(_entregar(el_texto_cubre=["explicacion"]), texto="termine el tablero",
                 archivos=list(archivos))
    return marcos.manda(Jugada("confirmar", {}), texto="dale")


def _salida_de(conn, mundo, nombre: str) -> list[dict]:
    return todos(conn, """select o.id, o.cuerpo, o.es_coordinacion, o.respuesta_grupo,
                                 o.dedupe_key,
                                 (select count(*) from message_outbox_adjunto a
                                   where a.outbox_id = o.id) as adjuntos
                            from message_outbox o
                           where not o.es_respuesta and o.chat_id = %s
                           order by o.dedupe_key""", mundo["personas"][nombre]["telegram"])


def test_el_aviso_sale_al_terminar_el_margen_con_la_evidencia_de_ese_momento(conn, mundo,
                                                                            marcos):
    """Al salir, el código relee la evidencia vigente: la foto que Marcos retiró dentro del
    margen no le llega a Ismael. Las fotos van adjuntas, en otra fila de la misma respuesta; un
    archivo sólo se nombra."""
    _tarea(conn, mundo)
    _entregada(marcos, [(JPEG, "foto", None), (JPEG, "foto", None),
                        (ZIP, "archivo", "programa.zip")])
    marcos.manda(Jugada("corregir", {"corrige": "entregar", "tarea": "T2", "saca": ["P3"]}),
                 texto="no, esa foto no era")
    ia = IAQueRedacta()
    assert enviar(conn, mundo, ia, AHORA + timedelta(minutes=5)).get("enviado") is None

    assert enviar(conn, mundo, ia, AHORA + timedelta(minutes=13)) == {"enviado": 1}
    [pedido] = ia.pedidos_de_redaccion
    [hechos] = pedido["hechos"]
    assert hechos["aviso"] == "entrega_para_aprobar" and hechos["responsable"] == "Marcos"
    assert hechos["necesita_respuesta"] is True and hechos["fotos_adjuntas"] == 1
    assert hechos["pregunta"] == "decision_de_la_entrega"   # aprobar o pedir cambios (3b)
    assert [(p["es"], p.get("va_adjunta")) for p in hechos["lo_que_entrego"]] == [
        ("lo_que_escribio", None), ("una_foto", True), ("un_archivo", None)]
    assert hechos["lo_que_entrego"][2]["nombre_del_archivo"] == "programa.zip"
    assert all("pieza" not in p for p in hechos["lo_que_entrego"])
    assert "todavia_le_falta" not in hechos

    texto, album = _salida_de(conn, mundo, "Ismael")
    assert texto["adjuntos"] == 0 and album["adjuntos"] == 1
    assert texto["es_coordinacion"] and album["es_coordinacion"]    # fuera del tope (§10)
    assert texto["respuesta_grupo"] == album["respuesta_grupo"] == texto["dedupe_key"]
    adjunta = uno(conn, "select archivo_id from message_outbox_adjunto")["archivo_id"]
    assert uno(conn, "select clase from evidence where archivo_id = %s",
               adjunta)["clase"] == "imagen"
    [aviso] = avisos_guardados(conn, "entrega_para_aprobar")
    assert aviso["estado"] == "enviado" and str(aviso["outbox_id"]) == str(texto["id"])
    detalle = uno(conn, """select detalle from audit_log where accion = 'enviar_aviso'""")
    assert detalle["detalle"]["adjuntos"] == 1


def test_repetir_el_aviso_no_duplica_filas(conn, mundo, marcos):
    _tarea(conn, mundo)
    _entregada(marcos)
    ia = IAQueRedacta()
    enviar(conn, mundo, ia, AHORA + timedelta(minutes=13))
    enviar(conn, mundo, ia, AHORA + timedelta(minutes=14))
    assert len(ia.pedidos_de_redaccion) == 1
    assert len(_salida_de(conn, mundo, "Ismael")) == 2
    assert cuantas(conn, "message_outbox_adjunto") == 2
    assert len(avisos_guardados(conn, "entrega_para_aprobar")) == 1


def test_si_la_tarea_ya_no_espera_la_aprobacion_el_aviso_no_sale_y_dice_por_que(conn, mundo,
                                                                               marcos):
    tarea = _tarea(conn, mundo)
    _entregada(marcos)
    with admin(conn) as cur:
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind)
                       values (%s, 'en_revision', 'asignada', 'leda')""", (tarea,))
    conn.commit()
    assert enviar(conn, mundo, IAQueRedacta(), AHORA + timedelta(minutes=13)) == {"omitido": 1}
    [aviso] = avisos_guardados(conn, "entrega_para_aprobar")
    assert aviso["motivo_omision"] == "ya_no_esta_entregada"
    assert _salida_de(conn, mundo, "Ismael") == []


def test_una_entrega_nueva_reemplaza_al_aviso_que_espera(conn, mundo, marcos):
    """ADR 0009, enmienda T6i: evidencia nueva sobre la tarea retira el aviso que espera y
    guarda otro, que al salir lleva toda la evidencia vigente."""
    tarea = _tarea(conn, mundo)
    _entregada(marcos)
    [primero] = avisos_guardados(conn, "entrega_para_aprobar")
    persona = mundo["personas"]["Marcos"]
    with espacio(conn, mundo["id"]) as cur:
        ctx = SimpleNamespace(
            cur=cur, ahora=AHORA + timedelta(minutes=4),
            calendario=Calendario.desde_base(cur, mundo["id"]),
            quien=SimpleNamespace(workspace_id=mundo["id"], nombre="Marcos",
                                  membership_id=persona["membership_id"]))
        avisos.guardar_aviso_de_entrega(ctx, {"id": tarea, "titulo": "Armar el tablero"},
                                        "otra-entrega")
    conn.commit()
    viejo, nuevo = avisos_guardados(conn, "entrega_para_aprobar")
    assert viejo["id"] == primero["id"] and viejo["estado"] == "omitido"
    assert viejo["motivo_omision"] == "hay_una_entrega_mas_nueva"
    assert nuevo["estado"] == "guardado"
    assert nuevo["dedupe_key"] == "motor:entrega_para_aprobar:otra-entrega"
    ia = IAQueRedacta()
    assert enviar(conn, mundo, ia, AHORA + timedelta(minutes=15)) == {"enviado": 1}
    assert len(ia.pedidos_de_redaccion[0]["hechos"][0]["lo_que_entrego"]) == 3


@pytest.mark.parametrize("pieza, va", [
    ({"clase": "imagen", "archivo_id": "a", "tipo_del_archivo": "image/jpeg", "tamano": 10},
     True),
    ({"clase": "imagen", "archivo_id": "a", "tipo_del_archivo": "image/heic", "tamano": 10},
     False),
    ({"clase": "imagen", "archivo_id": "a", "tipo_del_archivo": "image/png",
      "tamano": 11 * 1024 * 1024}, False),
    ({"clase": "archivo", "archivo_id": "a", "tipo_del_archivo": "application/zip",
      "tamano": 10}, False)])
def test_va_adjunta_la_foto_que_el_canal_muestra_como_foto(pieza, va):
    assert avisos._es_foto_adjunta(pieza) is va


# --- El enlace a la página de la tarea (ADR 0019, decisiones 6 y 7a; porción 4) ---------------

DIRECCION = "https://leda.invalid"


@pytest.fixture
def con_direccion(monkeypatch):
    import dataclasses

    from leda import config as config_mod

    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url=DIRECCION))


def _despachar(conn, mundo, at):
    from leda.despachador import TransporteDePrueba, despachar

    transporte = TransporteDePrueba()
    with espacio(conn, mundo["id"]) as cur:
        despachar(cur, mundo["id"], transporte, Calendario.desde_base(cur, mundo["id"]), at)
    conn.commit()
    return transporte


def test_el_aviso_lleva_el_enlace_a_la_pagina_sin_que_la_ia_lo_vea(conn, mundo, marcos,
                                                                   con_direccion):
    """La IA sabe que el mensaje lleva el enlace; el código lo agrega al mandar. Ni el pedido a
    la IA, ni la salida, ni el registro de turnos tienen el enlace."""
    import re

    from leda import pagina_de_tarea
    from leda.db import sin_espacio

    tarea = _tarea(conn, mundo)
    _entregada(marcos)
    ia = IAQueRedacta()
    enviar(conn, mundo, ia, AHORA + timedelta(minutes=13))
    [pedido] = ia.pedidos_de_redaccion
    assert pedido["hechos"][0]["lleva_el_enlace_a_la_pagina_de_la_tarea"] is True
    assert DIRECCION not in json.dumps(pedido, ensure_ascii=False, default=str)

    texto, _album = _salida_de(conn, mundo, "Ismael")
    marca = uno(conn, "select * from message_outbox_enlace")
    assert str(marca["outbox_id"]) == str(texto["id"]) and str(marca["task_id"]) == tarea
    assert str(marca["membership_id"]) == mundo["personas"]["Ismael"]["membership_id"]
    [aviso] = avisos_guardados(conn, "entrega_para_aprobar")
    assert aviso["hechos"]["lleva_el_enlace_a_la_pagina_de_la_tarea"] is True

    transporte = _despachar(conn, mundo, AHORA + timedelta(minutes=13))
    [mensaje] = [e for e in transporte.enviados if e.fotos is None
                 and e.chat_id == mundo["personas"]["Ismael"]["telegram"]]
    encontrado = re.search(r"\n" + re.escape(DIRECCION) + r"/tarea/([\w-]+)$", mensaje.texto)
    assert encontrado and mensaje.sin_vista_previa
    token = encontrado.group(1)
    registro = todos(conn, """select coalesce(o.cuerpo, '') cuerpo, t.jugadas
                                from conversation_turn t
                                left join message_outbox o on o.id = t.outbox_id""")
    assert registro and token not in json.dumps(registro, default=str)
    assert DIRECCION not in json.dumps(registro, default=str)
    with sin_espacio(conn) as cur:
        assert pagina_de_tarea.leer(cur, token)["tarea"]["titulo"] == "Armar el tablero"
    conn.commit()


def test_sin_direccion_publica_el_aviso_no_promete_ningun_enlace(conn, mundo, marcos,
                                                                  monkeypatch):
    import dataclasses

    from leda import config as config_mod

    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url=""))
    _tarea(conn, mundo)
    _entregada(marcos)
    ia = IAQueRedacta()
    enviar(conn, mundo, ia, AHORA + timedelta(minutes=13))
    [pedido] = ia.pedidos_de_redaccion
    assert "lleva_el_enlace_a_la_pagina_de_la_tarea" not in pedido["hechos"][0]
    assert cuantas(conn, "message_outbox_enlace") == 0


# --- Lo descrito frente al criterio de aceptación (decisión 10 del usuario, 2026-10-08; D3) ---

CRITERIO = "El tablero queda cerrado y rotulado; pasa la prueba de aislación con 500 V"
CERRADO, AISLACION = ("El tablero queda cerrado y rotulado",
                      "pasa la prueba de aislación con 500 V")
EJEMPLO = "Pasó la prueba de aislación con 500 V."


def test_el_criterio_se_lee_por_sus_renglones_y_sus_oraciones():
    """Un punto por renglón, por oración o separado con punto y coma, sin viñetas; una oración
    es un solo punto aunque diga dos cosas: el código no parte el criterio por sus palabras."""
    assert entrega.puntos_del_criterio(CRITERIO) == [CERRADO, AISLACION]
    assert entrega.puntos_del_criterio("- Arranca desde el PLC.\n2) Completa 20 ciclos.") == [
        "Arranca desde el PLC", "Completa 20 ciclos"]
    assert entrega.puntos_del_criterio("Mide 1.5 m y queda nivelado") == [
        "Mide 1.5 m y queda nivelado"]
    assert entrega.puntos_del_criterio(None) == entrega.puntos_del_criterio("  ") == []


def test_la_ia_recibe_el_criterio_por_puntos_para_juzgar_lo_descrito(conn, mundo, marcos):
    _tarea(conn, mundo, criterio=CRITERIO)
    marcos.manda(texto="hola")
    tarea = next(t for t in marcos.situacion["tareas"] if t["alias"] == "T2")
    assert tarea["criterio_de_aceptacion"] == [{"punto": "C1", "lo_que_pide": CERRADO},
                                               {"punto": "C2", "lo_que_pide": AISLACION}]


def test_lo_descrito_que_cubre_el_criterio_va_a_la_vista_previa_sin_preguntar(conn, mundo,
                                                                               marcos):
    _tarea(conn, mundo, pide=("explicacion",), criterio=CRITERIO)
    r = marcos.manda(_entregar(lo_descrito_cubre=["C1", "C2"]),
                     texto="quedo cerrado y rotulado, paso la aislacion con 500 V")
    hecho = _hecho(r, "entregar")
    assert hecho["resultado"] == "para_confirmar"
    assert "le_falta_del_criterio" not in hecho and "ejemplo" not in hecho
    assert hecho["entrega"][0]["describe"] == [CERRADO, AISLACION]
    assert r.pregunta["tipo"] == "confirmar_la_entrega"
    assert cuantas(conn, "conversation_option", "etiqueta = 'Confirmar'") == 1


def test_lo_que_falta_del_criterio_se_pide_con_un_ejemplo_y_no_se_entrega(conn, mundo,
                                                                          marcos):
    tarea = _tarea(conn, mundo, pide=("explicacion",), criterio=CRITERIO)
    r = marcos.manda(_entregar(lo_descrito_cubre=["C1"], ejemplo=EJEMPLO),
                     texto="termine el tablero, quedo cerrado y rotulado")
    hecho = _hecho(r, "entregar")
    assert hecho["resultado"] == "le_falta_evidencia"
    assert hecho["le_falta_del_criterio"] == [AISLACION]
    assert hecho["ejemplo"] == EJEMPLO
    assert "le_falta" not in hecho                      # la política está completa
    assert hecho["pregunta"] == "lo_que_falta_de_la_entrega"
    assert cuantas(conn, "conversation_option") == 0     # nada para confirmar: sin botones
    assert estado_de(conn, tarea) == "en_curso" and cuantas(conn, "evidence") == 0
    # La pregunta lo lleva: para volver a decirlo ("¿y qué pongo?") y para aceptarlo.
    assert r.pregunta["ejemplo"] == EJEMPLO
    assert r.pregunta["le_falta_del_criterio"] == [AISLACION]


def test_un_ejemplo_con_un_dato_que_nadie_dijo_no_se_propone(conn, mundo, marcos):
    """El verificador (como `_problema_de_propuesta` del flujo C): cada número y cada nombre del
    ejemplo tiene que estar en el criterio, en la tarea o en lo que la persona escribió. Si no,
    se propone el punto del criterio tal cual."""
    _tarea(conn, mundo, pide=("explicacion",), criterio=CRITERIO)
    r = marcos.manda(_entregar(lo_descrito_cubre=["C1"],
                               ejemplo="Pasó la prueba de aislación con 1000 V en Siemens."),
                     texto="quedo cerrado y rotulado")
    assert _hecho(r, "entregar")["ejemplo"] == "pasa la prueba de aislación con 500 V."
    assert entrega.problema_del_ejemplo("Pasó 20 ciclos", ["Completa 20 ciclos"]) is None
    assert entrega.problema_del_ejemplo("Pasó 30 ciclos", ["Completa 20 ciclos"]) == "dato: 30"
    assert entrega.problema_del_ejemplo("Arranca desde el PLC", ["arranca desde el plc"]) is None
    assert entrega.problema_del_ejemplo("Lo probó con Juan", ["Lo probó"]) == "nombre: Juan"
    assert entrega.problema_del_ejemplo("  ", ["x"]) == "vacio"


def test_sin_el_juicio_de_la_ia_el_criterio_no_queda_cubierto(conn, mundo, marcos):
    _tarea(conn, mundo, pide=("explicacion",), criterio=CRITERIO)
    r = marcos.manda(_entregar(), texto="listo el tablero")
    hecho = _hecho(r, "entregar")
    assert hecho["resultado"] == "le_falta_evidencia"
    assert hecho["le_falta_del_criterio"] == [CERRADO, AISLACION]
    assert hecho["ejemplo"] == f"{CERRADO}. {AISLACION}."


def test_aceptar_el_ejemplo_lo_suma_como_lo_que_describe_la_persona(conn, mundo, marcos):
    """El ejemplo cuenta como lo descrito sólo si la persona lo acepta: entonces es una pieza
    más, con lo que describe, y la entrega se confirma como siempre."""
    tarea = _tarea(conn, mundo, pide=("explicacion",), criterio=CRITERIO)
    marcos.manda(_entregar(lo_descrito_cubre=["C1"], ejemplo=EJEMPLO),
                 texto="quedo cerrado y rotulado")
    r = marcos.manda(_entregar(acepta_el_ejemplo=True), texto="si")
    hecho = _hecho(r, "entregar")
    assert hecho["resultado"] == "para_confirmar"
    assert [(p["es"], p.get("dice"), p.get("describe")) for p in hecho["entrega"]] == [
        ("lo_que_escribio", "quedo cerrado y rotulado", [CERRADO]),
        ("lo_que_escribio", EJEMPLO, [AISLACION])]
    marcos.manda(Jugada("confirmar", {}), texto="dale")
    assert estado_de(conn, tarea) == "en_revision"
    assert [(f["texto"], list(f["d"])) for f in todos(
        conn, "select texto, describe_del_criterio d from evidence order by at")] == [
        ("quedo cerrado y rotulado", [CERRADO]), (EJEMPLO, [AISLACION])]


def test_el_ejemplo_no_se_acepta_en_el_mismo_mensaje_que_se_propone(conn, mundo, marcos):
    _tarea(conn, mundo, pide=("explicacion",), criterio=CRITERIO)
    r = marcos.manda(_entregar(lo_descrito_cubre=["C1"], acepta_el_ejemplo=True,
                               ejemplo=EJEMPLO),
                     texto="quedo cerrado y rotulado")
    hecho = _hecho(r, "entregar")
    assert hecho["resultado"] == "le_falta_evidencia"
    assert len(hecho["entrega"]) == 1


def test_insistir_sin_cubrir_el_criterio_no_entrega_y_vuelve_a_proponer(conn, mundo, marcos):
    tarea = _tarea(conn, mundo, pide=("explicacion",), criterio=CRITERIO)
    marcos.manda(_entregar(lo_descrito_cubre=["C1"], ejemplo=EJEMPLO),
                 texto="quedo cerrado y rotulado")
    r = marcos.manda(Jugada("confirmar", {}), texto="no, asi esta, mandala")
    hecho = _hecho(r, "confirmar")
    assert hecho["resultado"] == "no_vale_la_confirmacion"
    assert hecho["motivo"] == "le_falta_algo"
    assert hecho["le_falta_del_criterio"] == [AISLACION]
    assert hecho["ejemplo"] == EJEMPLO
    assert estado_de(conn, tarea) == "en_curso" and cuantas(conn, "evidence") == 0


def test_sin_jugada_la_pregunta_vuelve_con_su_ejemplo(conn, mundo, marcos):
    """"¿Y qué pongo?" no es una jugada: la pregunta abierta vuelve con el ejemplo."""
    _tarea(conn, mundo, pide=("explicacion",), criterio=CRITERIO)
    marcos.manda(_entregar(lo_descrito_cubre=["C1"], ejemplo=EJEMPLO),
                 texto="quedo cerrado y rotulado")
    r = marcos.manda(texto="y que pongo?")
    assert r.pregunta["tipo"] == "lo_que_falta_de_la_entrega" and r.pregunta["desde_antes"]
    assert r.pregunta["ejemplo"] == EJEMPLO
    assert marcos.situacion["estado"]["pregunta_abierta"]["ejemplo"] == EJEMPLO


def test_corregir_lo_que_describe_un_texto_rehace_la_vista_previa(conn, mundo, marcos):
    """La lectura de la IA la corrige la persona en la vista previa."""
    _tarea(conn, mundo, pide=("explicacion",), criterio=CRITERIO)
    marcos.manda(_entregar(lo_descrito_cubre=["C1"], ejemplo=EJEMPLO),
                 texto="quedo cerrado y rotulado y paso la aislacion con 500 V")
    r = marcos.manda(Jugada("corregir", {"corrige": "entregar", "tarea": "T2",
                                         "lo_descrito_cubre": ["C1", "C2"]}),
                     texto="ya te dije lo de la aislacion")
    hecho = _hecho(r, "corregir")
    assert hecho["resultado"] == "corregido" and hecho["como_queda"] == "para_confirmar"
    assert hecho["entrega"][0]["describe"] == [CERRADO, AISLACION]


def test_un_texto_siempre_cubre_lo_que_solo_un_texto_puede_cubrir(conn, mundo, marcos):
    """Hallazgo 1 de la bitácora: la IA leyó un texto como resultado de la prueba y no como
    explicación, y la entrega se trabó. Lo que sólo un texto puede cubrir lo cubre siempre; lo
    que la IA dice que cubre se suma."""
    _tarea(conn, mundo, pide=("explicacion", "resultado_de_prueba"))
    r = marcos.manda(_entregar(el_texto_cubre=["resultado_de_prueba"]),
                     texto="20 ciclos sin una falla")
    hecho = _hecho(r, "entregar")
    assert hecho["resultado"] == "para_confirmar"
    assert hecho["entrega"][0]["cubre"] == ["cómo quedó el trabajo", "cómo se probó"]


# --- Una tarea que nunca se arrancó (decisión 14 del usuario, 2026-10-08; D3) ----------------

def test_la_terminada_sin_arrancar_se_recibe_igual_y_queda_arrancada_al_entregarla(conn, mundo,
                                                                                   marcos):
    tarea = _tarea(conn, mundo, pide=("explicacion",), estado="asignada")
    r = marcos.manda(_entregar(), texto="la termine, quedo cerrado")
    hecho = _hecho(r, "entregar")
    assert hecho["resultado"] == "para_confirmar"
    assert hecho["al_confirmar"]["arranca_al_entregarla"] is True
    assert estado_de(conn, tarea) == "asignada"

    r = marcos.manda(Jugada("confirmar", {}), texto="dale")
    hecho = _hecho(r, "confirmar")
    assert hecho["resultado"] == "entregada" and hecho["arranco_al_entregarla"] is True
    assert estado_de(conn, tarea) == "en_revision"
    assert [(e["estado_anterior"], e["estado_nuevo"]) for e in todos(
        conn, """select estado_anterior, estado_nuevo from task_state_event
                  where task_id = %s and estado_anterior is not null order by at""", tarea)] == [
        ("asignada", "en_curso"), ("en_curso", "en_revision")]


def test_la_ia_recibe_lo_que_pide_la_tarea_sin_arrancar(conn, mundo, marcos):
    _tarea(conn, mundo, estado="asignada", criterio=CRITERIO)
    marcos.manda(texto="hola")
    tarea = next(t for t in marcos.situacion["tareas"] if t["alias"] == "T2")
    assert [t["tipo_de_evidencia"] for t in tarea["evidencia_que_pide"]] == ["explicacion", "foto"]
    assert [p["punto"] for p in tarea["criterio_de_aceptacion"]] == ["C1", "C2"]
