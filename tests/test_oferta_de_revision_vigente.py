"""`_offer_current_review`: las ramas que no son el camino feliz (T10-2b, U2;
ADR 0013 reglas 2 y 3, y "nunca fallar en silencio").

El toque de Enviar a aprobación sobre un resumen que el borrador dejó atrás
responde con el resumen vigente. Si esa respuesta no se puede armar, quien tocó
recibe igual UNA respuesta (el aviso neutro) y queda un incidente; si el
encabezado de "el borrador cambió" no entra en el mensaje, sale sólo el resumen.
"""

from __future__ import annotations

from prisma import gateway
from prisma import ingreso_tareas as I
from prisma.db import admin
from prisma.incidentes import NOTICIA_NEUTRA_INCIDENTE

from tests.test_alta_enviar_a_aprobacion import (_acciones, _alta_en_revision,
                                                 _dejar_atras_el_resumen, _tocar,
                                                 _tg_aprobador)
from tests.test_alta_eleccion_confirmacion import _nuevas, _salidas, _usuario
from tests.test_task_intake import _callback_client


def _incidentes(conn) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select etapa, severidad, chat_id from incident order by at")
        return cur.fetchall()


def test_sin_fila_atada_a_la_revision_quien_toco_recibe_el_aviso_neutro_y_queda_un_incidente(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    client = _callback_client(conn, monkeypatch)
    _dejar_atras_el_resumen(conn, rid)
    real = I._finalize

    def finalizar_sin_fila_atada(cur, request, who, now):
        # Como si `_finalize` no hubiera encolado el resumen: la acción existe, su
        # fila de salida no.
        salida = real(cur, request, who, now)
        cur.execute("delete from message_outbox where pending_action_id = %s",
                    (salida.pending_action_id,))
        return salida

    monkeypatch.setattr(I, "_finalize", finalizar_sin_fila_atada)
    antes = _salidas(conn, user)
    incidentes_antes = len(_incidentes(conn))

    _tocar(client, conn, user, pid, "Enviar a aprobación")

    # Exactamente una respuesta a este toque: el aviso neutro.
    cuerpos = [f["cuerpo"] for f in _nuevas(conn, user, antes)]
    assert cuerpos == [NOTICIA_NEUTRA_INCIDENTE]
    nuevos = _incidentes(conn)[incidentes_antes:]
    assert [i["etapa"] for i in nuevos] == ["resumen_vigente_sin_fila"]
    assert _salidas(conn, _tg_aprobador(intake_world)) == []


def test_si_el_encabezado_no_entra_sale_solo_el_resumen(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    client = _callback_client(conn, monkeypatch)
    _dejar_atras_el_resumen(conn, rid)
    monkeypatch.setattr(I, "DRAFT_CHANGED_REVIEW_AGAIN", "x" * 5000)
    antes = _salidas(conn, user)

    _tocar(client, conn, user, pid, "Enviar a aprobación")

    (unica,) = _nuevas(conn, user, antes)
    (_, nueva) = _acciones(conn, rid)
    assert str(unica["pending_action_id"]) == str(nueva["id"])
    assert unica["cuerpo"] == nueva["resumen"]
    assert "x" * 100 not in unica["cuerpo"]
    assert NOTICIA_NEUTRA_INCIDENTE not in unica["cuerpo"]


def test_el_gateway_conserva_su_alias_del_aviso_neutro():
    assert gateway.NOTICIA_NEUTRA_INCIDENTE == NOTICIA_NEUTRA_INCIDENTE
