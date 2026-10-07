"""Cómo llega un archivo por Telegram (ADR 0019, decisión 4; `leda.motor.recibir`).

- **El adaptador lo baja antes del turno**: la foto de mayor resolución, un documento o un
  video, con o sin texto. Comprueba tamaño y tipo, lo guarda en `archivo` y lo ata al mensaje
  entrante (`archivo_de_mensaje`). A un desconocido no se le baja nada.
- **Un álbum es un solo mensaje**, con un solo turno, después de una espera corta
  (`recibir.ESPERA_ALBUM_S`): por el escuchador y por el webhook.
- **La IA sabe que llegó un archivo, no lo mira**: recibe qué llegó (`archivos`), nunca el
  contenido.
- **Fuera de límite** (más grande que lo que se puede recibir, o de un tipo fuera de la lista):
  no se guarda, queda anotado con su motivo y la IA lo cuenta con lo que la persona puede hacer.
  Nunca en silencio.
- **Si la descarga falla**, se reintenta como cualquier update y, al agotarse, un incidente y el
  texto fijo.

Telegram es de mentira: la descarga es una función preparada (`Bajadas`); la IA, guionada.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

import pytest

from leda import entrada
from leda.db import admin
from leda.despachador import TransporteDePrueba
from leda.motor import archivos, hechos, recibir
from leda.motor.escucha import BotTelegram, Escucha
from leda.motor.ia import IAGuionada
from leda.motor.recibir import IntentosPorUpdate, Recepcion, recibir_update
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import TEXTO_SI_LA_IA_FALLA

from tests.motor.ayudantes import AHORA, ID_DEL_BOT, TelegramFalso, cuantas, todos, uno

MARCOS = 81001
MB = 1024 * 1024
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01" + b"\x00" * 64 + b"\xff\xd9"
JPEG_2 = JPEG + b"\x01"
PDF = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\n%%EOF\n"
MP4 = b"\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2avc1mp41" + b"\x00" * 64
EXE = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff" + b"\x00" * 64


@dataclass
class Bajadas:
    """La descarga de Telegram, de mentira: lo preparado por cada `file_id`, o la excepción
    que levanta. Anota cada pedido."""

    contenidos: dict[str, bytes | BaseException] = field(default_factory=dict)
    pedidos: list[str] = field(default_factory=list)

    def __call__(self, file_id: str, maximo: int) -> bytes:
        self.pedidos.append(file_id)
        contenido = self.contenidos[file_id]
        if isinstance(contenido, BaseException):
            raise contenido
        if len(contenido) > maximo:
            raise archivos.Rechazo(archivos.DEMASIADO_GRANDE)
        return contenido


def _mensaje(update_id: int, *, de: int = MARCOS, caption: str | None = None,
             album: str | None = None, **media) -> dict:
    mensaje = {"message_id": update_id, "from": {"id": de, "first_name": "X"},
               "chat": {"id": de, "type": "private"}, **media}
    if caption is not None:
        mensaje["caption"] = caption
    if album is not None:
        mensaje["media_group_id"] = album
    return {"update_id": update_id, "message": mensaje}


def _foto(update_id: int, file_id: str, contenido: bytes = JPEG, **mas) -> dict:
    return _mensaje(update_id, photo=[
        {"file_id": f"{file_id}-chica", "file_unique_id": f"u-{file_id}-chica",
         "width": 90, "height": 90, "file_size": 100},
        {"file_id": file_id, "file_unique_id": f"u-{file_id}", "width": 1280,
         "height": 960, "file_size": len(contenido)}], **mas)


def _documento(update_id: int, file_id: str, nombre: str, tamano: int | None, **mas) -> dict:
    documento = {"file_id": file_id, "file_unique_id": f"u-{file_id}", "file_name": nombre,
                 "mime_type": "application/pdf"}
    if tamano is not None:
        documento["file_size"] = tamano
    return _mensaje(update_id, document=documento, **mas)


def _recepcion(conn, mundo, ia, bajadas: Bajadas, salida: TransporteDePrueba | None = None
               ) -> Recepcion:
    return Recepcion(conn, mundo["id"], ia, RelojFijo(AHORA), bot_id=ID_DEL_BOT,
                     imprimir=lambda *_: None, transporte=salida or TransporteDePrueba(),
                     bajar=bajadas)


def _recibir(recepcion: Recepcion, *updates: dict) -> None:
    intentos = IntentosPorUpdate()
    for u in updates:
        assert recibir_update(recepcion, intentos, u)


def _ia(redaccion: str = "Recibí la foto. ¿Para qué es?") -> IAGuionada:
    return IAGuionada(jugadas=[[]], redacciones=[redaccion])


# --- Una foto, un documento, un video ---------------------------------------------------------

def test_una_foto_sin_texto_se_baja_se_guarda_y_corre_su_turno(conn, mundo):
    ia, bajadas, salida = _ia(), Bajadas({"F1": JPEG}), TransporteDePrueba()

    _recibir(_recepcion(conn, mundo, ia, bajadas, salida), _foto(500, "F1"))

    assert bajadas.pedidos == ["F1"]            # la de mayor resolución, una vez
    guardado = uno(conn, """select id, sha256, tamano, tipo, clase, nombre_original,
                                   enviado_por_membership_id, recibido_en from archivo""")
    assert guardado["sha256"] == hashlib.sha256(JPEG).hexdigest()
    assert (guardado["tamano"], guardado["tipo"], guardado["clase"]) == (
        len(JPEG), "image/jpeg", "imagen")
    assert str(guardado["enviado_por_membership_id"]) == mundo["personas"]["Marcos"][
        "membership_id"]
    assert guardado["recibido_en"] == AHORA
    atado = uno(conn, "select * from archivo_de_mensaje")
    entrante = uno(conn, "select id, telegram_message_id from inbound_message")
    assert atado["inbound_message_id"] == entrante["id"]
    assert atado["archivo_id"] == guardado["id"] and atado["rechazo"] is None
    assert (atado["que_llego"], atado["telegram_file_id"], atado["telegram_file_unique_id"],
            atado["telegram_message_id"]) == ("foto", "F1", "u-F1", 500)
    # La IA sabe qué llegó, nunca el contenido.
    assert ia.pedidos_de_jugadas[0]["mensaje"] == ""
    assert ia.pedidos_de_jugadas[0]["archivos"] == [{"que_llego": "foto"}]
    assert ia.pedidos_de_redaccion[0]["archivos"] == [{"que_llego": "foto"}]
    assert cuantas(conn, "conversation_turn", "sentido = 'entrada'") == 1
    assert [e.texto for e in salida.enviados] == ["Recibí la foto. ¿Para qué es?"]


def test_un_documento_con_texto_llega_con_su_nombre(conn, mundo):
    ia, bajadas = _ia("Recibí el informe."), Bajadas({"D1": PDF})

    _recibir(_recepcion(conn, mundo, ia, bajadas),
             _documento(501, "D1", "informe.pdf", len(PDF), caption="el informe del tablero"))

    assert ia.pedidos_de_jugadas[0]["mensaje"] == "el informe del tablero"
    assert ia.pedidos_de_jugadas[0]["archivos"] == [
        {"que_llego": "archivo", "nombre_del_archivo": "informe.pdf"}]
    guardado = uno(conn, "select tipo, clase, nombre_original from archivo")
    assert dict(guardado) == {"tipo": "application/pdf", "clase": "pdf",
                              "nombre_original": "informe.pdf"}


def test_un_video_se_guarda_como_video(conn, mundo):
    ia, bajadas = _ia("Recibí el video."), Bajadas({"V1": MP4})

    _recibir(_recepcion(conn, mundo, ia, bajadas), _mensaje(
        502, video={"file_id": "V1", "file_unique_id": "u-V1", "file_size": len(MP4),
                    "file_name": "prueba.mp4", "duration": 3}))

    assert uno(conn, "select clase from archivo")["clase"] == "video"
    assert ia.pedidos_de_jugadas[0]["archivos"] == [
        {"que_llego": "video", "nombre_del_archivo": "prueba.mp4"}]


def test_a_alguien_que_no_es_del_equipo_no_se_le_baja_nada(conn, mundo):
    ia, bajadas = IAGuionada(), Bajadas({"F1": JPEG})

    _recibir(_recepcion(conn, mundo, ia, bajadas), _foto(503, "F1", de=99999))

    assert bajadas.pedidos == [] and ia.pedidos_de_jugadas == []
    assert cuantas(conn, "inbound_message") == 0 and cuantas(conn, "archivo") == 0


def test_un_archivo_que_vuelve_a_llegar_no_se_baja_ni_se_atiende_dos_veces(conn, mundo):
    ia, bajadas = _ia(), Bajadas({"F1": JPEG})
    recepcion = _recepcion(conn, mundo, ia, bajadas)

    _recibir(recepcion, _foto(504, "F1"), _foto(504, "F1"))

    assert bajadas.pedidos == ["F1"]
    assert cuantas(conn, "archivo_de_mensaje") == 1
    assert cuantas(conn, "conversation_turn", "sentido = 'entrada'") == 1


# --- Un álbum ---------------------------------------------------------------------------------

def test_un_album_es_un_solo_mensaje_con_un_solo_turno_despues_de_la_espera(conn, mundo,
                                                                            monkeypatch):
    ia, salida = _ia("Recibí las dos fotos."), TransporteDePrueba()
    recepcion = _recepcion(conn, mundo, ia, Bajadas({"A1": JPEG, "A2": JPEG_2}), salida)

    _recibir(recepcion, _foto(510, "A1", album="g1"),
             _foto(511, "A2", JPEG_2, album="g1", caption="el tablero terminado"))

    # Todavía en la espera: nada se atendió.
    assert recepcion.atender_albumes() == 1
    assert ia.pedidos_de_jugadas == [] and salida.enviados == []

    monkeypatch.setattr(recibir, "ESPERA_ALBUM_S", 0)
    assert recepcion.atender_albumes() == 0
    recepcion.despachar_ahora()

    assert cuantas(conn, "inbound_message") == 1
    assert cuantas(conn, "archivo_de_mensaje") == 2 and cuantas(conn, "archivo") == 2
    assert cuantas(conn, "conversation_turn", "sentido = 'entrada'") == 1
    assert ia.pedidos_de_jugadas[0]["mensaje"] == "el tablero terminado"
    assert ia.pedidos_de_jugadas[0]["archivos"] == [{"que_llego": "foto"},
                                                    {"que_llego": "foto"}]
    assert [e.texto for e in salida.enviados] == ["Recibí las dos fotos."]
    # Atenderlo otra vez no hace nada.
    assert recepcion.atender_albumes() == 0
    assert cuantas(conn, "conversation_turn", "sentido = 'entrada'") == 1


def test_el_escuchador_espera_poco_mientras_hay_un_album_y_despues_lo_atiende(conn, mundo,
                                                                            monkeypatch):
    telegram, salida = TelegramFalso(), TransporteDePrueba()
    ia = _ia("Recibí las dos fotos.")
    escucha = Escucha(conn, mundo["id"], ia, RelojFijo(AHORA),
                      bot=BotTelegram("token-falso", telegram.cliente()), transporte=salida,
                      imprimir=lambda *_: None, bajar=Bajadas({"A1": JPEG, "A2": JPEG_2}))
    escucha.preparar()
    telegram.lotes = [[_foto(520, "A1", album="g2"), _foto(521, "A2", JPEG_2, album="g2")]]

    escucha.una_vuelta()
    assert salida.enviados == []
    escucha.una_vuelta()
    pedidos = [p for metodo, p in telegram.llamadas if metodo == "getUpdates"]
    assert pedidos[-1]["timeout"] == recibir.ESPERA_ALBUM_S

    monkeypatch.setattr(recibir, "ESPERA_ALBUM_S", 0)
    escucha.una_vuelta()

    assert [e.texto for e in salida.enviados] == ["Recibí las dos fotos."]
    assert cuantas(conn, "conversation_turn", "sentido = 'entrada'") == 1
    escucha.una_vuelta()
    assert [p for m, p in telegram.llamadas if m == "getUpdates"][-1]["timeout"] == 25


def test_el_webhook_junta_el_album_y_lo_atiende_una_vez(conn, mundo, monkeypatch):
    ia, salida = _ia("Recibí las dos fotos."), TransporteDePrueba()
    bajadas = Bajadas({"A1": JPEG, "A2": JPEG_2})
    monkeypatch.setattr(entrada, "_conn", lambda: conn)
    monkeypatch.setattr(entrada, "_token_de", lambda slug: f"{ID_DEL_BOT}:token-falso")
    monkeypatch.setattr(entrada, "_ia_de", lambda conn, ws: ia)
    monkeypatch.setattr(entrada, "_reloj_de", lambda conn, ws: RelojFijo(AHORA))
    monkeypatch.setattr(entrada, "_cliente_http", TelegramFalso().cliente)
    monkeypatch.setattr(entrada, "_INTENTOS", {})
    monkeypatch.setattr(entrada, "_transporte_de", lambda token: salida)
    monkeypatch.setattr(entrada, "_indicador", lambda token: None)
    monkeypatch.setattr(entrada, "_bajar_de", lambda token: bajadas)
    monkeypatch.setattr(recibir, "ESPERA_ALBUM_S", 0)
    esperas: list[float] = []
    monkeypatch.setattr(entrada, "_esperar", esperas.append)

    entrada.atender_update("prueba", _foto(530, "A1", album="g3"))
    entrada.atender_update("prueba", _foto(531, "A2", JPEG_2, album="g3"))

    assert esperas == [0, 0]
    assert cuantas(conn, "inbound_message") == 1
    assert cuantas(conn, "conversation_turn", "sentido = 'entrada'") == 1
    assert [e.texto for e in salida.enviados] == ["Recibí las dos fotos."]


# --- Fuera de límite: nunca en silencio -------------------------------------------------------

def test_uno_demasiado_grande_no_se_baja_y_la_ia_lo_sabe(conn, mundo):
    ia, bajadas, salida = _ia("Es muy pesado."), Bajadas(), TransporteDePrueba()

    _recibir(_recepcion(conn, mundo, ia, bajadas, salida),
             _documento(540, "D9", "recorrida.mp4", 25 * MB))

    assert bajadas.pedidos == [] and cuantas(conn, "archivo") == 0
    atado = uno(conn, "select archivo_id, rechazo, nombre_original from archivo_de_mensaje")
    assert dict(atado) == {"archivo_id": None, "rechazo": "demasiado_grande",
                           "nombre_original": "recorrida.mp4"}
    assert ia.pedidos_de_redaccion[0]["archivos"] == [
        {"que_llego": "archivo", "nombre_del_archivo": "recorrida.mp4",
         "no_se_pudo_recibir": "demasiado_grande", "limite_mb": 20,
         "en_cambio_puede": ["mandar_uno_mas_chico", "mandar_un_enlace"]}]
    assert [e.texto for e in salida.enviados] == ["Es muy pesado."]


def test_el_limite_del_espacio_vale_si_es_menor_que_el_del_canal(conn, mundo):
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, 'archivo_tamano_maximo_mb', '5')""", (mundo["id"],))
    conn.commit()
    ia = _ia("Es muy pesado.")

    _recibir(_recepcion(conn, mundo, ia, Bajadas()),
             _documento(541, "D8", "planos.pdf", 6 * MB))

    assert ia.pedidos_de_jugadas[0]["archivos"][0]["limite_mb"] == 5


def test_uno_que_resulta_mas_grande_al_bajarlo_tampoco_se_guarda(conn, mundo):
    """Sin el tamaño declarado, la descarga se corta en el límite."""
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, 'archivo_tamano_maximo_mb', '1')""", (mundo["id"],))
    conn.commit()
    ia = _ia("Es muy pesado.")

    _recibir(_recepcion(conn, mundo, ia, Bajadas({"D7": PDF + b"\x00" * MB})),
             _documento(542, "D7", "grande.pdf", None))

    assert cuantas(conn, "archivo") == 0
    assert uno(conn, "select rechazo from archivo_de_mensaje")["rechazo"] == "demasiado_grande"


def test_un_tipo_fuera_de_la_lista_no_se_guarda_y_la_ia_lo_sabe(conn, mundo):
    ia = _ia("Ese archivo no lo puedo recibir.")

    _recibir(_recepcion(conn, mundo, ia, Bajadas({"D6": EXE})),
             _documento(543, "D6", "informe.pdf", len(EXE)))

    assert cuantas(conn, "archivo") == 0
    assert ia.pedidos_de_jugadas[0]["archivos"] == [
        {"que_llego": "archivo", "nombre_del_archivo": "informe.pdf",
         "no_se_pudo_recibir": "tipo_no_admitido", "en_cambio_puede": ["mandar_un_enlace"]}]


# --- La descarga que falla --------------------------------------------------------------------

def test_si_la_descarga_falla_se_reintenta_y_al_final_incidente_y_texto_fijo(conn, mundo):
    ia, salida = IAGuionada(), TransporteDePrueba()
    recepcion = _recepcion(conn, mundo, ia, Bajadas({"F5": RuntimeError("sin red")}), salida)
    intentos = IntentosPorUpdate()
    update = _foto(550, "F5")

    resultados = [recibir_update(recepcion, intentos, update)
                  for _ in range(recibir.INTENTOS_POR_UPDATE)]

    assert resultados == [False] * (recibir.INTENTOS_POR_UPDATE - 1) + [True]
    assert cuantas(conn, "archivo") == 0 and ia.pedidos_de_jugadas == []
    incidente = uno(conn, "select etapa, app_user_id from incident")
    assert incidente["etapa"] == "turno_conversacion"
    assert str(incidente["app_user_id"]) == mundo["personas"]["Marcos"]["app_user_id"]
    assert [e.texto for e in salida.enviados] == [TEXTO_SI_LA_IA_FALLA]


def test_una_descarga_que_falla_una_vez_se_recibe_al_reintentar(conn, mundo):
    ia = _ia()
    bajadas = Bajadas({"F4": RuntimeError("sin red")})
    recepcion = _recepcion(conn, mundo, ia, bajadas)
    intentos = IntentosPorUpdate()

    assert not recibir_update(recepcion, intentos, _foto(551, "F4"))
    bajadas.contenidos["F4"] = JPEG
    assert recibir_update(recepcion, intentos, _foto(551, "F4"))

    assert cuantas(conn, "archivo") == 1 and cuantas(conn, "inbound_message") == 1
    assert cuantas(conn, "incident") == 0


# --- Lo que la IA lee -------------------------------------------------------------------------

def test_lo_que_la_ia_recibe_de_un_archivo_tiene_su_significado():
    valor = {"archivos": [
        {"que_llego": "foto"},
        {"que_llego": "archivo", "nombre_del_archivo": "informe_final"},
        {"que_llego": "video", "nombre_del_archivo": "recorrida.mp4",
         "no_se_pudo_recibir": "demasiado_grande", "limite_mb": 20,
         "en_cambio_puede": ["mandar_uno_mas_chico", "mandar_un_enlace"]},
        {"que_llego": "archivo", "nombre_del_archivo": "x.exe",
         "no_se_pudo_recibir": "tipo_no_admitido", "en_cambio_puede": ["mandar_un_enlace"]}]}

    assert hechos.sin_significado(valor) == set()
    # El nombre de un archivo es de quien lo mandó: nunca se lee como un código ni se cambia.
    assert hechos.para_redactar(valor)["archivos"][1]["nombre_del_archivo"] == "informe_final"
    assert "informe_final" not in hechos.bloque(valor)
    assert "contenido" in hechos.significado("archivos")
