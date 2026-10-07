"""El formato de los mensajes (pedido del usuario, 2026-10-07; diseño en
`odd/tasks/motor-definitivo.md`, "El formato de los mensajes").

La IA escribe un formato mínimo: `**negrita**`, párrafos separados por un renglón en blanco y
viñetas con "• ". El outbox guarda el texto tal como lo escribió. Al enviar, la cocina lo
convierte en texto plano más entidades `bold` de Telegram, nunca con `parse_mode`: no hay nada
que escapar, y una marca mal cerrada sale como texto. Las posiciones se cuentan en unidades
UTF-16 sobre el texto que de verdad sale (con el saludo del día, si lo hubo) y conviven con la
entidad `pre` del texto copiable. Cada parte de un mensaje partido es un mensaje propio: una
entidad nunca cruza de una parte a otra. Si el formato pasa del máximo de entidades de
Telegram, el mensaje sale como texto, sin negritas, en lugar de fallar.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.despachador import TransporteDePrueba, TransporteTelegram, despachar
from leda.salida import (MAX_ENTIDADES_TELEGRAM, enqueue_outbox, formatear,
                         normalize_visible_text, prepare_payload, telegram_utf16_units)

BA = ZoneInfo("America/Argentina/Buenos_Aires")
AHORA = datetime(2026, 7, 27, 10, 0, tzinfo=BA)   # lunes, en horario


def _negrita(offset: int, length: int) -> dict:
    return {"type": "bold", "offset": offset, "length": length}


def _trozo(texto: str, entidad: dict) -> str:
    """Lo que una entidad marca, leído en unidades UTF-16 como lo lee Telegram."""
    unidades = texto.encode("utf-16-le")
    return unidades[entidad["offset"] * 2:
                    (entidad["offset"] + entidad["length"]) * 2].decode("utf-16-le")


class _Respuesta:
    def raise_for_status(self):
        pass

    def json(self):
        return {"result": {"message_id": 1}}


class _Http:
    def __init__(self):
        self.cuerpos = []

    def post(self, url, json=None, **kwargs):
        self.cuerpos.append(json)
        return _Respuesta()


def _por_telegram(texto, bloque=None):
    http = _Http()
    transporte = TransporteTelegram("unused", cliente=http)
    if bloque is None:
        transporte.enviar(1, texto)
    else:
        transporte.enviar(1, texto, bloque=bloque)
    return http.cuerpos[0]


# ------------------------------------------------------------- la conversión

def test_la_negrita_sale_como_texto_plano_y_una_entidad_bold():
    assert formatear("La **Programar PLC** vence hoy.") == (
        "La Programar PLC vence hoy.", [_negrita(3, 13)])


def test_las_posiciones_se_cuentan_en_unidades_utf16():
    texto = "👋 Ojo: **válvula 🔧** y **más**"

    plano, entidades = formatear(texto)

    assert plano == "👋 Ojo: válvula 🔧 y más"
    assert entidades == [_negrita(telegram_utf16_units("👋 Ojo: "),
                                  telegram_utf16_units("válvula 🔧")),
                         _negrita(telegram_utf16_units("👋 Ojo: válvula 🔧 y "), 3)]
    assert [_trozo(plano, e) for e in entidades] == ["válvula 🔧", "más"]


@pytest.mark.parametrize("texto", [
    "**sin cerrar",
    "sin abrir**",
    "vacía: ****",
    "**cruza\n\nun renglón en blanco**",
    "** con espacios adentro **",
    "un * solo * asterisco",
])
def test_una_marca_mal_cerrada_queda_como_texto(texto):
    assert formatear(texto) == (texto, [])


def test_dos_negritas_pegadas_son_dos_entidades():
    assert formatear("**a****b**") == ("ab", [_negrita(0, 1), _negrita(1, 1)])


@pytest.mark.parametrize("texto", [
    "**a **b** c**",
    "***a***",
    "******",
    "**a**b**c**",
    "**uno** **dos** ** tres**",
])
def test_los_casos_raros_son_deterministas_y_nunca_se_pisan(texto):
    plano, entidades = formatear(texto)

    assert formatear(texto) == (plano, entidades)
    fin = 0
    for e in entidades:
        assert e["type"] == "bold" and e["length"] > 0 and e["offset"] >= fin
        fin = e["offset"] + e["length"]
    assert fin <= telegram_utf16_units(plano)


def test_las_vinetas_son_texto_plano_y_un_guion_al_principio_pasa_a_vineta():
    plano, entidades = formatear("Tenés dos:\n- **PLC**, vence el 23\n• **COM**, el 30")

    assert plano == "Tenés dos:\n• PLC, vence el 23\n• COM, el 30"
    assert [_trozo(plano, e) for e in entidades] == ["PLC", "COM"]


def test_un_guion_en_medio_del_renglon_no_es_una_vineta():
    assert formatear("del 23 - al 30") == ("del 23 - al 30", [])


def test_el_renglon_en_blanco_entre_parrafos_sobrevive_a_la_normalizacion():
    assert normalize_visible_text("Uno.\n\nDos.\n• tres") == "Uno.\n\nDos.\n• tres"


# ------------------------------------------------------------- el transporte

def test_telegram_recibe_texto_plano_y_entidades_nunca_parse_mode():
    cuerpo = _por_telegram("Anoté el inicio de **Programar PLC**.\n\nIsmael se entera hoy.")

    assert cuerpo["text"] == "Anoté el inicio de Programar PLC.\n\nIsmael se entera hoy."
    assert cuerpo["entities"] == [_negrita(19, 13)]
    assert "parse_mode" not in cuerpo


def test_un_mensaje_sin_marcas_no_lleva_entidades():
    cuerpo = _por_telegram("hola\n\n• uno")

    assert "entities" not in cuerpo and "parse_mode" not in cuerpo


def test_la_negrita_convive_con_el_bloque_copiable_que_queda_literal():
    """El bloque es lo que la persona escribió: se copia tal cual, con sus asteriscos."""
    texto = "Lo que escribiste en **la tarea**:\n\nRevisar **todo**"

    cuerpo = _por_telegram(texto, bloque="Revisar **todo**")

    assert cuerpo["text"] == "Lo que escribiste en la tarea:\n\nRevisar **todo**"
    negrita, pre = cuerpo["entities"]
    assert (negrita["type"], _trozo(cuerpo["text"], negrita)) == ("bold", "la tarea")
    assert (pre["type"], _trozo(cuerpo["text"], pre)) == ("pre", "Revisar **todo**")
    assert negrita["offset"] + negrita["length"] <= pre["offset"]


def test_el_transporte_de_prueba_registra_lo_mismo_que_sale_por_telegram():
    texto = "**PLC**: en curso.\n\n• **COM**"
    transporte = TransporteDePrueba()

    transporte.enviar(1, texto)

    cuerpo = _por_telegram(texto)
    [entregado] = transporte.enviados
    assert (entregado.texto, entregado.entidades) == (cuerpo["text"], cuerpo["entities"])


def test_sin_marcas_el_transporte_de_prueba_no_registra_entidades():
    transporte = TransporteDePrueba()

    transporte.enviar(1, "hola")

    assert transporte.enviados[0].entidades is None


def test_una_parte_de_un_mensaje_partido_se_formatea_sola():
    """Una negrita que abre en una parte y cierra en otra queda como texto en las dos: ninguna
    entidad cruza el borde de una parte."""
    texto = "**" + "palabra " * 700 + "fin** y **una negrita entera**"
    partes = prepare_payload(texto, dedupe_key="largo", allow_split=True)
    assert len(partes) > 1

    cuerpos = [_por_telegram(p.text) for p in partes]

    assert "entities" not in cuerpos[0] and cuerpos[0]["text"].startswith("(1/")
    assert "**palabra" in cuerpos[0]["text"]
    for cuerpo in cuerpos:
        for e in cuerpo.get("entities", []):
            assert e["offset"] + e["length"] <= telegram_utf16_units(cuerpo["text"])
    assert [_trozo(cuerpos[-1]["text"], e) for e in cuerpos[-1]["entities"]] == [
        "una negrita entera"]


def test_hasta_el_maximo_de_entidades_sale_con_formato():
    texto = " ".join(f"**t{n}**" for n in range(MAX_ENTIDADES_TELEGRAM))

    cuerpo = _por_telegram(texto)

    assert len(cuerpo["entities"]) == MAX_ENTIDADES_TELEGRAM


def test_pasado_el_maximo_de_entidades_sale_como_texto_sin_negritas():
    assert MAX_ENTIDADES_TELEGRAM == 100        # lo que Telegram admite por mensaje
    texto = " ".join(f"**t{n}**" for n in range(MAX_ENTIDADES_TELEGRAM + 1))

    cuerpo = _por_telegram(texto)

    assert "entities" not in cuerpo
    assert "**" not in cuerpo["text"] and cuerpo["text"].startswith("t0 t1 t2")


def test_pasado_el_maximo_con_bloque_se_quitan_las_negritas_y_queda_el_bloque():
    antes = " ".join(f"**t{n}**" for n in range(MAX_ENTIDADES_TELEGRAM)) + ":\n\n"

    cuerpo = _por_telegram(antes + "lo escrito", bloque="lo escrito")

    [pre] = cuerpo["entities"]
    assert (pre["type"], _trozo(cuerpo["text"], pre)) == ("pre", "lo escrito")
    assert "**" not in cuerpo["text"]


# ------------------------------------------------------------- de punta a punta

def test_el_outbox_guarda_las_marcas_y_el_saludo_corre_las_posiciones(corework, conn):
    """El outbox guarda lo que escribió la IA, así la IA ve su formato en el historial; las
    posiciones se calculan sobre lo que sale, con el saludo del día adelante."""
    ws = corework.workspace_id
    texto = "Anoté el inicio de **Programar PLC**.\n\n• **Revisar comunicaciones**"
    with admin(conn) as cur:
        cur.execute(
            """select m.id from membership m join app_user u on u.id = m.app_user_id
                where m.workspace_id = %s and u.nombre = %s""",
            (ws, "Marcos Tarquini"))
        persona = str(cur.fetchone()["id"])
        cur.execute("delete from greeting_state where membership_id = %s", (persona,))
    with espacio(conn, ws) as cur:
        enqueue_outbox(cur, workspace_id=ws, chat_id=500, text=texto, scheduled_for=AHORA,
                       dedupe_key="formato-1", is_response=True,
                       recipient_membership_id=persona)
        cur.execute("select cuerpo from message_outbox where dedupe_key = 'formato-1'")
        assert cur.fetchone()["cuerpo"] == texto
        http = _Http()
        despachar(cur, ws, TransporteTelegram("unused", cliente=http),
                  Calendario.desde_base(cur, ws), AHORA)

    [cuerpo] = http.cuerpos
    plano = "Anoté el inicio de Programar PLC.\n\n• Revisar comunicaciones"
    assert cuerpo["text"] != plano and cuerpo["text"].endswith(plano)     # con saludo
    assert "parse_mode" not in cuerpo
    assert [_trozo(cuerpo["text"], e) for e in cuerpo["entities"]] == [
        "Programar PLC", "Revisar comunicaciones"]
    saludo = cuerpo["text"][:len(cuerpo["text"]) - len(plano)]
    assert cuerpo["entities"][0]["offset"] == telegram_utf16_units(saludo) + 19
