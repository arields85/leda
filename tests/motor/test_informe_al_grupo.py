"""El informe al grupo (`leda.motor.informe_al_grupo`; C-6, decisión 25 del usuario, 2026-10-09,
opción A; decisiones 8, 35, 45 y 49; constitución §8; mecánica §10 y §12; conversación 41).

El día de una cadencia al grupo del espacio (`cadence_job.audiencia = 'grupo'`, como
`informe_semanal` de CoreWork), Leda le manda al grupo del equipo (`workspace.grupo_chat_id`, del
pack `telegram.grupo_gestion_id`) lo que pasó con las tareas: las terminadas desde el informe
anterior, las que siguen, las entregadas, las trabadas con lo que las traba y los atrasos ya
hablados en privado, con el nombre de quien la tiene en cada renglón. Un atraso aparece con el día
en que vencía, el día que dio la persona y su motivo, como información (decisión 25); uno que la
persona todavía no habló con Leda no aparece (constitución §8: primero en privado); lo que quedó
asentado por falta de respuesta, sí (decisiones 35 y 49). Sin nada que informar, no sale nada. Leda
no conversa en el grupo: no pide respuesta ni abre ninguna pregunta.

El reloj es el de `test_escalera.py`: "Revisar el tablero" (T1) vence el viernes 9 de octubre de
2026; el lunes 12 es feriado.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from leda.db import admin, espacio
from leda.motor import hechos as hechos_mod
from leda.motor.asentado import hay_informe_al_grupo
from leda.motor.avisos import INTENTOS
from leda.motor.informe_al_grupo import (INFORME_AL_GRUPO, NADA_PARA_INFORMAR,
                                         guardar_los_informes)
from leda.motor.ia import Jugada

from tests.motor.ayudantes import avisos_guardados, cuantas, dice, octubre, todos, uno

GRUPO = -100_500
VIERNES = "15 16 * * 5"         # `informe_semanal` del pack: viernes 16:15
MARTES = "15 16 * * 2"
T2, T3, T4, T5 = ("Probar las comunicaciones", "Instalar el panel", "Cablear la línea 2",
                  "Cambiar el motor")


def _con_informe(conn, mundo, cron: str = VIERNES, *, grupo: int | None = GRUPO,
                 activa: bool = True) -> None:
    with admin(conn) as cur:
        cur.execute("update workspace set grupo_chat_id = %s where id = %s", (grupo, mundo["id"]))
        cur.execute("""insert into cadence_job (workspace_id, nombre, cron, audiencia,
                                                plantilla_clave, activo)
                       values (%s, 'informe_semanal', %s, 'grupo', 'informe_semanal', %s)""",
                    (mundo["id"], cron, activa))
    conn.commit()


def _al_grupo(pedidos: list[dict]) -> list[dict]:
    return [p for p in pedidos if p["persona"] is None]


def _el_informe(dias, at: datetime) -> dict:
    [informe] = _al_grupo(dias.ciclo(at))
    [hechos] = informe["hechos"]
    return hechos


def _titulos(renglones) -> list[str]:
    return [r["tarea"] for r in renglones]


def _estado(conn, mundo, titulo: str, estado: str, at: datetime, *,
            vence: datetime | None = None, bloqueo: str | None = None) -> str:
    """Otra tarea de Marcos en ese estado desde `at`, como la cargaría la plataforma: trabada con
    su bloqueo abierto, terminada con la aprobación que su cierre exige."""
    with admin(conn) as cur:
        # Con su criterio de aceptación: el cierre lo comprueba la base (mecánica §5).
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, estado, fecha_objetivo,
                                 criterio_aceptacion)
               values (%s, %s, %s, %s, %s, 'asignada', %s, 'Queda hecho y probado')
               returning id""",
            (mundo["id"], mundo["objetivo"], titulo, mundo["area"],
             mundo["personas"]["Marcos"]["membership_id"], vence or octubre(30, 17)))
        tarea = str(cur.fetchone()["id"])
        if bloqueo:
            cur.execute("""insert into blocker (workspace_id, task_id, causa, abierto_en,
                                                abierto_por)
                           values (%s, %s, %s, %s, %s)""",
                        (mundo["id"], tarea, bloqueo, at,
                         mundo["personas"]["Marcos"]["membership_id"]))
        if estado == "terminada":
            cur.execute("""insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                                 aprobador_membership_id, decision)
                           values (%s, 'tarea', %s, %s, 'aprobado')""",
                        (mundo["id"], tarea, mundo["personas"]["Ismael"]["membership_id"]))
        if estado != "asignada":
            cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                         actor_kind, motivo, at)
                           values (%s, 'asignada', %s, 'sistema', 'estado inicial de la prueba',
                                   %s)""", (tarea, estado, at))
    conn.commit()
    return tarea


def _cancelar_el_tablero(conn, mundo) -> None:
    with admin(conn) as cur:
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind, motivo, at)
                       values (%s, 'asignada', 'cancelada', 'sistema', 'prueba', %s)""",
                    (mundo["tarea"], octubre(5, 10)))
    conn.commit()


# --- Cuándo y a dónde sale ------------------------------------------------------------------------

def test_el_dia_de_la_cadencia_el_informe_sale_al_grupo_del_espacio(conn, mundo, dias):
    _con_informe(conn, mundo)
    _estado(conn, mundo, T2, "en_curso", octubre(5, 10))

    hechos = _el_informe(dias, octubre(9, 16, 15))

    assert hechos["aviso"] == INFORME_AL_GRUPO and hechos["necesita_respuesta"] is False
    [aviso] = avisos_guardados(conn, INFORME_AL_GRUPO)
    assert aviso["al_grupo"] is True and aviso["destinatario_membership_id"] is None
    assert (aviso["estado"], aviso["task_id"]) == ("enviado", None)
    [fila] = todos(conn, "select * from message_outbox where chat_id = %s", GRUPO)
    assert str(fila["id"]) == str(aviso["outbox_id"])
    assert fila["destinatario_membership_id"] is None
    assert (fila["es_respuesta"], fila["tipo"], fila["es_coordinacion"]) == (
        False, "informativo", False)
    assert fila["vence_en"] is not None          # un informe de un día no sale otro día (§12)
    auditado = uno(conn, """select * from audit_log where accion = 'enviar_aviso'
                             and sujeto_id = %s""", str(aviso["id"]))
    assert auditado["detalle"]["al_grupo"] is True
    assert auditado["detalle"]["outbox_id"] == str(fila["id"])


def test_sale_una_vez_por_dia_de_la_cadencia(conn, mundo, dias):
    _con_informe(conn, mundo)
    _estado(conn, mundo, T2, "en_curso", octubre(5, 10))
    dias.ciclo(octubre(9, 16, 15))

    assert _al_grupo(dias.ciclo(octubre(9, 16, 20))) == []
    assert len(avisos_guardados(conn, INFORME_AL_GRUPO)) == 1


def test_leda_no_conversa_en_el_grupo(conn, mundo, dias):
    """El informe no pide respuesta ni abre ninguna pregunta, y no es el último aviso de nadie."""
    _con_informe(conn, mundo)
    _cancelar_el_tablero(conn, mundo)               # sólo el informe sale en esa vuelta
    _estado(conn, mundo, T2, "en_curso", octubre(5, 10))
    preguntas_antes = cuantas(conn, "conversation_question")

    _el_informe(dias, octubre(9, 16, 15))

    [aviso] = avisos_guardados(conn, INFORME_AL_GRUPO)
    assert cuantas(conn, "conversation_question") == preguntas_antes
    assert cuantas(conn, "conversation_state", "ultimo_aviso_id = %s", str(aviso["id"])) == 0


def test_sin_nada_que_informar_no_sale_nada(conn, mundo, dias):
    """Sin tareas abiertas ni terminadas, el informe queda omitido con su motivo: nunca un
    mensaje vacío al grupo, nunca en silencio."""
    _con_informe(conn, mundo)
    _cancelar_el_tablero(conn, mundo)

    assert _al_grupo(dias.ciclo(octubre(9, 16, 15))) == []

    [aviso] = avisos_guardados(conn, INFORME_AL_GRUPO)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", NADA_PARA_INFORMAR)
    assert cuantas(conn, "message_outbox", "chat_id = %s", GRUPO) == 0


def test_un_dia_de_la_cadencia_que_paso_sin_atenderse_no_sale_tarde(conn, mundo, dias):
    """Mecánica §12: el informe del viernes que no salió a su hora (fuera del horario, el ciclo
    parado) no sale el día hábil siguiente: queda omitido con su motivo."""
    _con_informe(conn, mundo, "45 16 * * 5")
    _estado(conn, mundo, T2, "en_curso", octubre(5, 10))
    dias.ciclo(octubre(8, 10))                      # la primera vuelta

    assert _al_grupo(dias.ciclo(octubre(9, 17, 30))) == []      # fuera del horario
    assert _al_grupo(dias.ciclo(octubre(13, 10))) == []

    [aviso] = avisos_guardados(conn, INFORME_AL_GRUPO)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "ya_paso_su_momento")


def test_si_la_ia_no_lo_redacta_se_reintenta_y_nunca_sale_un_texto_armado(conn, mundo):
    """Decisión 8, caso 2: si la IA no lo redacta, se reintenta a los 1, 2, 4 y 8 minutos; al
    quinto fallo queda `fallido` con sus hechos y un incidente para la administración. Al grupo
    no le llega nada armado a mano."""
    from datetime import timedelta

    from leda.motor.avisos import enviar_avisos
    from leda.motor.escalera import correr_escalera
    from leda.motor.tiempo import RelojFijo

    class NoRedacta:
        nombre = "falla"

        def redactar(self, pedido):
            raise TimeoutError("la IA no contestó")

    _con_informe(conn, mundo)
    _cancelar_el_tablero(conn, mundo)               # sólo el informe sale en esa vuelta
    _estado(conn, mundo, T2, "en_curso", octubre(5, 10))
    at = octubre(9, 16, 15)
    correr_escalera(conn, mundo["id"], RelojFijo(at))
    conn.commit()
    for minutos in (0, 1, 3, 7, 15):
        enviar_avisos(conn, mundo["id"], NoRedacta(), RelojFijo(at + timedelta(minutes=minutos)))
        conn.commit()

    [aviso] = avisos_guardados(conn, INFORME_AL_GRUPO)
    assert (aviso["estado"], aviso["intentos"]) == ("fallido", INTENTOS)
    assert cuantas(conn, "message_outbox", "chat_id = %s", GRUPO) == 0
    assert cuantas(conn, "incident", "etapa = 'motor_aviso_guardado'") == 1


# --- Si el espacio tiene informe al grupo (un solo predicado) ------------------------------------

@pytest.mark.parametrize("como", ["sin_grupo", "apagada", "ritmo_roto"])
def test_sin_un_informe_que_de_verdad_corra_no_se_guarda_nada_ni_figura(conn, mundo, dias, como):
    """`asentado.hay_informe_al_grupo` es verdadero sólo si el informe de verdad sale: el espacio
    tiene su grupo y una cadencia al grupo activa con un ritmo que se entiende. Es el mismo
    predicado que decide si se guarda el informe."""
    _con_informe(conn, mundo, "cada viernes" if como == "ritmo_roto" else VIERNES,
                 grupo=None if como == "sin_grupo" else GRUPO, activa=como != "apagada")
    _estado(conn, mundo, T2, "en_curso", octubre(5, 10))

    dias.ciclo(octubre(9, 16, 15))

    assert avisos_guardados(conn, INFORME_AL_GRUPO) == []
    with admin(conn) as cur:
        assert hay_informe_al_grupo(cur, mundo["id"]) is False


def test_con_grupo_y_cadencia_que_corre_figura_en_el_informe(conn, mundo):
    _con_informe(conn, mundo)
    with admin(conn) as cur:
        assert hay_informe_al_grupo(cur, mundo["id"]) is True


# --- Lo que dice --------------------------------------------------------------------------------

def test_cada_renglon_dice_de_quien_es_y_como_esta(conn, mundo, dias):
    """Decisiones 8 y 25: las terminadas, las que siguen (con su estado y cuándo vencen), las
    entregadas y las trabadas (con lo que las traba y desde cuándo); todas las líneas llevan el
    nombre de quien la tiene."""
    _con_informe(conn, mundo)
    _estado(conn, mundo, T2, "terminada", octubre(7, 11))
    _estado(conn, mundo, T3, "en_revision", octubre(8, 11))
    _estado(conn, mundo, T4, "bloqueada", octubre(6, 10), bloqueo="esperando el repuesto")
    _estado(conn, mundo, T5, "en_curso", octubre(5, 10), vence=octubre(23, 17))

    hechos = _el_informe(dias, octubre(9, 16, 15))

    assert hechos["terminadas"] == [{"tarea": T2, "la_tiene": "Marcos"}]
    assert hechos["entregadas"] == [{"tarea": T3, "la_tiene": "Marcos"}]
    assert hechos["trabadas"] == [{"tarea": T4, "la_tiene": "Marcos",
                                   "causas": ["esperando el repuesto"],
                                   "trabada_desde": "2026-10-06", "dias_habiles_trabada": 3}]
    assert hechos["siguen"] == [
        {"tarea": "Revisar el tablero", "la_tiene": "Marcos", "estado": "asignada",
         "vence": "2026-10-09"},
        {"tarea": T5, "la_tiene": "Marcos", "estado": "en_curso", "vence": "2026-10-23"}]
    assert "atrasadas" not in hechos
    assert hechos_mod.sin_significado(hechos) == set()


def test_un_atraso_hablado_en_privado_figura_con_el_dia_que_dio_y_su_motivo(conn, mundo,
                                                                             escribe, dias):
    """Decisión 25: el PLC venció el viernes; Marcos le dijo a Leda en privado que lo termina el
    miércoles, porque falta el cable. El informe del martes lo dice, con su nombre, el día en que
    vencía, el que dio y su motivo, como información."""
    _con_informe(conn, mundo, MARTES)
    dias.ciclo(octubre(9, 10))                              # el pedido del día que vence
    dice(conn, escribe, Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-14",
                                                    "motivo": "falta el cable"}),
         at=octubre(9, 10, 30))

    hechos = _el_informe(dias, octubre(13, 16, 15))

    assert hechos["atrasadas"] == [{"tarea": "Revisar el tablero", "la_tiene": "Marcos",
                                    "vence": "2026-10-09", "prevision": "2026-10-14",
                                    "motivo": "falta el cable"}]
    assert "siguen" not in hechos


def test_un_atraso_que_no_se_hablo_en_privado_no_figura(conn, mundo, dias):
    """Constitución §8 y decisión 8: Leda le preguntó a Marcos en privado y todavía no contestó.
    El informe del martes no nombra el tablero, ni como atrasado ni como algo que sigue."""
    _con_informe(conn, mundo, MARTES)
    _estado(conn, mundo, T5, "en_curso", octubre(5, 10), vence=octubre(23, 17))
    dias.ciclo(octubre(9, 10))

    hechos = _el_informe(dias, octubre(13, 16, 15))

    assert "atrasadas" not in hechos
    assert _titulos(hechos["siguen"]) == [T5]


def test_lo_asentado_por_falta_de_respuesta_figura_en_el_informe(conn, mundo, dias):
    """Decisiones 21, 35 y 49: al tercer pedido sin respuesta Leda le dijo a Marcos que iba a
    quedar asentado que la tarea está atrasada, para que el equipo esté al tanto. Al escalar,
    quedó asentado: el informe siguiente lo dice, sin un día que nadie dio."""
    _con_informe(conn, mundo)
    _estado(conn, mundo, T5, "en_curso", octubre(5, 10), vence=octubre(23, 17))
    for dia in (9, 13, 14):
        dias.ciclo(octubre(dia, 10))
    [escala] = dias.ciclo(octubre(15, 10))
    assert escala["persona"] == "Ismael"

    hechos = _el_informe(dias, octubre(16, 16, 15))

    assert hechos["atrasadas"] == [{"tarea": "Revisar el tablero", "la_tiene": "Marcos",
                                    "vence": "2026-10-09"}]


def test_las_terminadas_son_las_de_despues_del_informe_anterior(conn, mundo, dias):
    _con_informe(conn, mundo)
    _estado(conn, mundo, T2, "terminada", octubre(7, 11))
    _el_informe(dias, octubre(9, 16, 15))
    _estado(conn, mundo, T3, "terminada", octubre(13, 11))

    hechos = _el_informe(dias, octubre(16, 16, 15))

    assert _titulos(hechos["terminadas"]) == [T3]


def test_guardar_sin_cadencias_no_hace_nada(conn, mundo):
    from leda.calendario import Calendario
    from leda.motor.avisos import Momento

    with espacio(conn, mundo["id"]) as cur:
        m = Momento(cur, mundo["id"], Calendario.desde_base(cur, mundo["id"]), octubre(9, 16, 15))
        assert guardar_los_informes(m) == 0
    conn.commit()
