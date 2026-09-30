"""Las opciones salen de lo que el sistema puede hacer (T9-R3, ADR 0013 regla 3,
hallazgo R3-H18: el modelo ofreció "Adjunto una captura o archivo", algo que el
sistema no puede recibir).

- El preámbulo ya no obliga al modelo a inventar opciones "razonables": le dice
  qué no puede hacer el sistema hoy y que, sin alternativas reales, pregunte una
  sola vez sin inventarlas.
- Las opciones que arma el código (el cierre genérico de una pregunta sin
  botones) se derivan de las capacidades del momento: "Es una tarea nueva" sólo
  si el alta guiada puede arrancar (chat privado, mensaje de origen) y la persona
  no acaba de dejarla de lado.
"""

from __future__ import annotations

import pytest

from prisma.agente import NoProponer, responder
from prisma.calendario import Calendario
from prisma.contexto import PREAMBULO
from prisma.db import admin, espacio
from prisma.llm import ProveedorGuionado, Respuesta

from tests.test_veracidad import AHORA, _quien

ENTRANTE = "00000000-0000-0000-0000-0000000000e1"
PREGUNTA = "¿Cuál de las dos querés ver primero?"


def test_el_preambulo_dice_que_el_sistema_no_recibe_archivos():
    texto = PREAMBULO.lower()
    assert "archivos" in texto and "fotos" in texto and "audios" in texto
    assert "link" in texto                       # la evidencia es texto o un link
    assert "nunca ofrezcas" in texto


def test_el_preambulo_no_obliga_a_inventar_opciones():
    texto = PREAMBULO.lower()
    assert "más razonables" not in texto
    assert "no las inventes" in texto


def _etiquetas_del_cierre(conn, ws, *, chat_id, entrante_id, no_proponer=None):
    proveedor = ProveedorGuionado([Respuesta(texto=PREGUNTA)])
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        responder(cur, quien, "mostrame algo", proveedor,
                  Calendario.desde_base(cur, ws), chat_id=chat_id, ahora=AHORA,
                  entrante_id=entrante_id, no_proponer=no_proponer)
    with admin(conn) as cur:
        cur.execute(
            """select o.etiqueta from pending_action_option o
                 join pending_action p on p.id = o.pending_action_id
                where p.workspace_id = %s order by o.orden""", (ws,))
        return [f["etiqueta"] for f in cur.fetchall()]


def test_en_un_chat_privado_el_cierre_ofrece_la_tarea_nueva(corework, conn):
    etiquetas = _etiquetas_del_cierre(conn, corework.workspace_id, chat_id=9100,
                                      entrante_id=ENTRANTE)

    assert any("Es una tarea nueva" in e for e in etiquetas)


def test_en_un_grupo_el_cierre_no_ofrece_lo_que_el_alta_no_puede_hacer(
        corework, conn):
    etiquetas = _etiquetas_del_cierre(conn, corework.workspace_id, chat_id=-100200,
                                      entrante_id=ENTRANTE)

    assert etiquetas and not any("tarea nueva" in e for e in etiquetas)
    assert any("tarea existente" in e for e in etiquetas)


def test_tras_dejar_el_alta_el_cierre_no_la_vuelve_a_ofrecer(corework, conn):
    alta = NoProponer(None, None, None, dejado="el título de la tarea nueva",
                      alta=True)

    etiquetas = _etiquetas_del_cierre(conn, corework.workspace_id, chat_id=9100,
                                      entrante_id=ENTRANTE, no_proponer=alta)

    assert etiquetas and not any("tarea nueva" in e for e in etiquetas)
    assert any("tarea existente" in e for e in etiquetas)


@pytest.mark.parametrize("dejado", [
    NoProponer("registrar_bloqueo", "tarea_id", "t1", dejado="el bloqueo"),
    None])
def test_dejar_otra_cosa_no_cambia_el_cierre(corework, conn, dejado):
    etiquetas = _etiquetas_del_cierre(conn, corework.workspace_id, chat_id=9100,
                                      entrante_id=ENTRANTE, no_proponer=dejado)

    assert any("Es una tarea nueva" in e for e in etiquetas)
