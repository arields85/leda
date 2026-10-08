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

import pytest

from leda.autoridad import identificar_en_espacio
from leda.db import admin, espacio
from leda.motor.fichas import FICHAS
from leda.motor.ia import IAGuionada, Jugada
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import procesar_toque, procesar_turno

from tests.motor.ayudantes import AHORA, VIERNES_16, cuantas, estado_de, todos, uno

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
           estado="en_curso") -> str:
    """Una tarea de Marcos que pide `pide`, con la política del área (sus clases, del pack)."""
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
                                 evidencia_requerida)
               values (%s, %s, %s, %s, %s, %s, %s, %s) returning id""",
            (mundo["id"], mundo["objetivo"], titulo, mundo["area"],
             mundo["personas"]["Marcos"]["membership_id"], estado, VIERNES_16, list(pide)))
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
    assert FICHAS["entregar"].estados == frozenset({"en_curso"})
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
    assert hecho["al_confirmar"] == {"queda_esperando_la_aprobacion_de": "Ismael"}
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
    # Quien aprueba se entera (el aviso de la cocina, hasta la porción 3).
    assert cuantas(conn, "message_outbox", "chat_id = %s and not es_respuesta",
                   mundo["personas"]["Ismael"]["telegram"]) == 1


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
