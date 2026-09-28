"""Saludo diario (pack 06).

Decisión del usuario, 2026-09-28+2 (revisión de e83a280, T7b/T7b-follow-up):
el primer mensaje que Prisma le manda a una persona en su fecha local lleva
el saludo, sea cual sea -- una respuesta, una cadencia, un recordatorio de la
escalera, o un aviso que disparó otra persona. Nunca se repite ese día. La
decisión y la reserva corren en `despachador._intentar_envio`, el único
punto que sabe qué sale primero de verdad -- nunca en `agente.py`/
`gateway.py`/`ingreso_tareas.py`, que arman el texto mucho antes de saber si
va a ser lo primero que la persona reciba hoy.

`docs/decisions/0010-correo-verificado-y-google-en-el-producto.md` deja el
saludo diario explícitamente fuera de su alcance: estas pruebas corren
contra `main`, no contra la rama auxiliar de correo y Google.
"""

from __future__ import annotations

import threading
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import psycopg
import pytest

from prisma import saludo as S
from prisma.calendario import Calendario
from prisma.db import admin, conectar, espacio
from prisma.despachador import TransporteDePrueba, despachar
from prisma.incidentes import registrar_incidente
from prisma.salida import BUTTON_TEXT_LIMIT, TELEGRAM_TEXT_LIMIT, enqueue_outbox

BA = ZoneInfo("America/Argentina/Buenos_Aires")


def _membership_id(cur, ws: str, nombre: str) -> str:
    # Consulta directa, no la vista `integrante`: corre bajo `admin()`, sin
    # `prisma.workspace_id` en la sesión -- la vista no devolvería nada.
    cur.execute(
        """select m.id from membership m join app_user u on u.id = m.app_user_id
            where m.workspace_id = %s and u.nombre = %s""",
        (ws, nombre))
    return str(cur.fetchone()["id"])


def _limpiar_saludo(cur, membership_id: str) -> None:
    """Vuelve a la persona a "todavía no saludada hoy": deshace la reserva
    lejana que pone `conftest._blindar_contra_saludo` para que el resto de
    la suite no se vuelva, sin querer, una prueba del saludo."""
    cur.execute("delete from greeting_state where membership_id = %s",
                (membership_id,))


# ---------------------------------------------------------------------------
# Regla exacta de hora local (pack 06 §2)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("hora_local,esperado", [
    (4, S.SALUDO_NOCHE),
    (5, S.SALUDO_MANANA),
    (11, S.SALUDO_MANANA),
    (12, S.SALUDO_TARDE),
    (19, S.SALUDO_TARDE),
    (20, S.SALUDO_NOCHE),
    (0, S.SALUDO_NOCHE),
    (23, S.SALUDO_NOCHE),
])
def test_saludo_por_hora_en_los_limites_exactos(hora_local, esperado):
    # `saludo_por_hora` recibe la hora ya local (0-23): probar en el límite
    # de minuto (04:59 vs 05:00, etc.) se reduce a probar el entero de esa
    # hora y la anterior -- la función no ve minutos.
    assert S.saludo_por_hora(hora_local) == esperado


def test_saludo_convierte_de_verdad_a_la_zona_del_espacio_no_solo_lee_utc():
    # 2026-01-15 02:30 UTC es, en Buenos Aires (UTC-3), 2026-01-14 23:30 --
    # otra hora Y otra fecha local.
    momento = datetime(2026, 1, 15, 2, 30, tzinfo=timezone.utc)
    local = momento.astimezone(BA)
    assert local.hour == 23
    assert local.date() == date(2026, 1, 14)
    assert S.saludo_por_hora(local.hour) == S.SALUDO_NOCHE
    assert S.fecha_local(momento, BA) == date(2026, 1, 14)


def test_zona_de_workspace_lee_la_zona_real_del_espacio(conn, intake_world):
    with admin(conn) as cur:
        norte = S.zona_de_workspace(cur, intake_world["north-lab"]["id"])
        oeste = S.zona_de_workspace(cur, intake_world["west-studio"]["id"])
    assert norte == ZoneInfo("America/Argentina/Buenos_Aires")
    assert oeste == ZoneInfo("Europe/Madrid")


# ---------------------------------------------------------------------------
# Como mucho una vez por persona y por fecha local (`reclamar_saludo`)
# ---------------------------------------------------------------------------

def test_reclamar_saludo_gana_la_primera_vez_del_dia(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        mid = _membership_id(cur, ws, "Marcos Tarquini")
        _limpiar_saludo(cur, mid)
        ganado = S.reclamar_saludo(cur, workspace_id=ws, membership_id=mid,
                                   fecha=date(2026, 9, 28))
    assert ganado is True


def test_reclamar_saludo_pierde_una_segunda_vez_la_misma_fecha(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        mid = _membership_id(cur, ws, "Marcos Tarquini")
        _limpiar_saludo(cur, mid)
        primera = S.reclamar_saludo(cur, workspace_id=ws, membership_id=mid,
                                    fecha=date(2026, 9, 28))
        segunda = S.reclamar_saludo(cur, workspace_id=ws, membership_id=mid,
                                    fecha=date(2026, 9, 28))
    assert primera is True
    assert segunda is False


def test_reclamar_saludo_gana_de_nuevo_al_dia_local_siguiente(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        mid = _membership_id(cur, ws, "Marcos Tarquini")
        _limpiar_saludo(cur, mid)
        assert S.reclamar_saludo(cur, workspace_id=ws, membership_id=mid,
                                 fecha=date(2026, 9, 28)) is True
        assert S.reclamar_saludo(cur, workspace_id=ws, membership_id=mid,
                                 fecha=date(2026, 9, 29)) is True


def test_reclamar_saludo_nunca_retrocede_con_una_fecha_anterior_a_la_guardada(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        mid = _membership_id(cur, ws, "Marcos Tarquini")
        _limpiar_saludo(cur, mid)
        assert S.reclamar_saludo(cur, workspace_id=ws, membership_id=mid,
                                 fecha=date(2026, 9, 28)) is True
        retroceso = S.reclamar_saludo(cur, workspace_id=ws, membership_id=mid,
                                      fecha=date(2026, 9, 27))
        cur.execute("select ultima_fecha_local from greeting_state "
                    "where membership_id = %s", (mid,))
        assert cur.fetchone()["ultima_fecha_local"] == date(2026, 9, 28)
    assert retroceso is False


def test_dos_reclamos_concurrentes_de_la_misma_persona_gana_uno_solo(
        corework, conn, uri):
    ws = corework.workspace_id
    with admin(conn) as cur:
        mid = _membership_id(cur, ws, "Marcos Tarquini")
        _limpiar_saludo(cur, mid)
    conn.commit()

    barrier = threading.Barrier(2)
    resultados: list[bool] = []
    fallas: list[Exception] = []

    def intentar():
        otra = conectar(uri)
        try:
            with otra.cursor() as cur:
                cur.execute("set role prisma_admin")
                barrier.wait()
                resultados.append(S.reclamar_saludo(
                    cur, workspace_id=ws, membership_id=mid,
                    fecha=date(2026, 9, 28)))
            otra.commit()
        except Exception as exc:  # noqa: BLE001
            fallas.append(exc)
            otra.rollback()
        finally:
            otra.close()

    hilos = [threading.Thread(target=intentar) for _ in range(2)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()

    assert fallas == []
    assert sorted(resultados) == [False, True]

    with admin(conn) as cur:
        cur.execute("select ultima_fecha_local from greeting_state "
                    "where membership_id = %s", (mid,))
        assert cur.fetchone()["ultima_fecha_local"] == date(2026, 9, 28)


# ---------------------------------------------------------------------------
# `reclamar_y_anteponer`: grupo, bienvenida, saludo normal
# ---------------------------------------------------------------------------

def test_mensaje_de_grupo_nunca_reclama_ni_lleva_saludo(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        resultado = S.reclamar_y_anteponer(
            cur, workspace_id=ws, membership_id=None, zona=BA,
            ahora=datetime(2026, 9, 28, 14, 0, tzinfo=timezone.utc),
            texto="Estado del equipo: 3 asignada.")
    assert resultado == "Estado del equipo: 3 asignada."


def test_bienvenida_reclama_sin_anteponer_nada(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        mid = _membership_id(cur, ws, "Marcos Tarquini")
        _limpiar_saludo(cur, mid)
        ahora = datetime(2026, 9, 28, 14, 0, tzinfo=timezone.utc)  # 11:00 Buenos Aires

        resultado = S.reclamar_y_anteponer(
            cur, workspace_id=ws, membership_id=mid, zona=BA, ahora=ahora,
            texto="Listo, Marcos. Soy Prisma.", es_bienvenida=True)
        assert resultado == "Listo, Marcos. Soy Prisma."   # sin "👋" antepuesto

        # Pero SÍ quedó reclamada: un mensaje normal después, mismo día, no
        # vuelve a saludar.
        siguiente = S.reclamar_y_anteponer(
            cur, workspace_id=ws, membership_id=mid, zona=BA,
            ahora=ahora + timedelta(hours=1), texto="Tenés una tarea abierta.")
        assert siguiente == "Tenés una tarea abierta."


def test_primer_mensaje_normal_del_dia_antepone_el_saludo_y_el_segundo_no(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        mid = _membership_id(cur, ws, "Marcos Tarquini")
        _limpiar_saludo(cur, mid)
        ahora = datetime(2026, 9, 28, 14, 0, tzinfo=timezone.utc)  # 11:00 Buenos Aires

        primero = S.reclamar_y_anteponer(
            cur, workspace_id=ws, membership_id=mid, zona=BA, ahora=ahora,
            texto="Tenés una tarea abierta.")
        segundo = S.reclamar_y_anteponer(
            cur, workspace_id=ws, membership_id=mid, zona=BA,
            ahora=ahora + timedelta(minutes=5), texto="Otra cosa más.")

    assert primero == f"{S.SALUDO_MANANA}\n\nTenés una tarea abierta."
    assert segundo == "Otra cosa más."


# ---------------------------------------------------------------------------
# R4-001/R4-002: un saludo decorativo nunca puede tirar abajo un envío real
# ---------------------------------------------------------------------------

def test_falla_del_upsert_manda_igual_sin_saludo_y_reporta_un_incidente(
        corework, conn, monkeypatch):
    """Simula "el upsert falla por lo que sea" (tabla `greeting_state`
    faltante, por ejemplo) sin tocar el esquema real de la sesión de
    pruebas: `reclamar_saludo` explota con una excepción cualquiera. La
    respuesta tiene que salir igual, sin saludo, y quedar un incidente
    sanitizado -- nunca en silencio."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        mid = _membership_id(cur, ws, "Marcos Tarquini")
        _limpiar_saludo(cur, mid)

        cur.execute("select count(*) n from incident where workspace_id = %s", (ws,))
        antes = cur.fetchone()["n"]

        def _explota(*a, **k):
            raise psycopg.errors.UndefinedTable(
                'relation "greeting_state" does not exist')

        monkeypatch.setattr(S, "reclamar_saludo", _explota)

        resultado = S.reclamar_y_anteponer(
            cur, workspace_id=ws, membership_id=mid, zona=BA,
            ahora=datetime(2026, 9, 28, 14, 0, tzinfo=timezone.utc),
            texto="Tenés una tarea abierta.")
        assert resultado == "Tenés una tarea abierta."      # sale sin saludo

        cur.execute(
            """select resumen_sanitizado, referencia_cruda from incident
                where workspace_id = %s order by id desc limit 1""", (ws,))
        incidente = cur.fetchone()
        cur.execute("select count(*) n from incident where workspace_id = %s", (ws,))
        despues = cur.fetchone()["n"]

    assert despues == antes + 1
    assert "saludo" in incidente["resumen_sanitizado"].lower()
    assert "greeting_state" in incidente["referencia_cruda"]


def test_zona_invalida_manda_igual_sin_saludo(corework, conn):
    """Una `zona` que no sabe convertir (nunca debería llegar así desde
    `despachador._intentar_envio`, que usa `cal.zona` ya validada -- pero la
    protección es genérica, no depende de por qué falló) no puede tirar
    abajo el envío."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        mid = _membership_id(cur, ws, "Marcos Tarquini")
        _limpiar_saludo(cur, mid)

        resultado = S.reclamar_y_anteponer(
            cur, workspace_id=ws, membership_id=mid,
            zona="no-es-una-zona",  # rompe adentro de `ahora.astimezone(zona)`
            ahora=datetime(2026, 9, 28, 14, 0, tzinfo=timezone.utc),
            texto="Tenés una tarea abierta.")

    assert resultado == "Tenés una tarea abierta."


def test_una_falla_repetida_se_reporta_una_sola_vez(corework, conn, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        mid = _membership_id(cur, ws, "Marcos Tarquini")
        _limpiar_saludo(cur, mid)
        cur.execute("select count(*) n from incident where workspace_id = %s", (ws,))
        antes = cur.fetchone()["n"]

        def _explota(*a, **k):
            raise RuntimeError("falla repetida de prueba")

        monkeypatch.setattr(S, "reclamar_saludo", _explota)
        for _ in range(3):
            S.reclamar_y_anteponer(
                cur, workspace_id=ws, membership_id=mid, zona=BA,
                ahora=datetime(2026, 9, 28, 14, 0, tzinfo=timezone.utc),
                texto="x")

        cur.execute("select count(*) n from incident where workspace_id = %s", (ws,))
        despues = cur.fetchone()["n"]
    assert despues == antes + 1     # deduplicado, no tres incidentes


# ---------------------------------------------------------------------------
# El margen reservado (`MARGEN_SALUDO`) para que el saludo nunca rompa el
# límite real de Telegram
# ---------------------------------------------------------------------------

def test_margen_saludo_es_el_peor_caso_de_los_tres_saludos_mas_el_separador():
    from prisma.salida import telegram_utf16_units

    esperado = max(telegram_utf16_units(s) for s in
                   (S.SALUDO_MANANA, S.SALUDO_TARDE, S.SALUDO_NOCHE)) + 2
    assert S.MARGEN_SALUDO == esperado


def test_enqueue_outbox_reserva_el_margen_solo_para_mensajes_personales(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        mid = _membership_id(cur, ws, "Marcos Tarquini")

        # Exactamente en el límite real, SIN destinatario (mensaje de
        # grupo): entra tal cual, sin reservar nada.
        texto_grupo = "x" * TELEGRAM_TEXT_LIMIT
        n = enqueue_outbox(
            cur, workspace_id=ws, chat_id=-1001, text=texto_grupo,
            dedupe_key="test:grupo:margen", allow_split=True)
        assert n >= 1

        # La misma longitud, CON destinatario: no entra en un solo mensaje
        # sin partir -- el margen se comió el resto del presupuesto, así que
        # ahora tiene que partirse en más de una fila.
        texto_personal = "x" * TELEGRAM_TEXT_LIMIT
        enqueue_outbox(
            cur, workspace_id=ws, chat_id=9001, text=texto_personal,
            recipient_membership_id=mid, dedupe_key="test:personal:margen",
            allow_split=True)
        cur.execute(
            "select count(*) n from message_outbox where dedupe_key like %s",
            ("test:personal:margen%",))
        partes = cur.fetchone()["n"]
    assert partes > 1


def test_enqueue_outbox_con_botones_reserva_el_margen(corework, conn):
    """Un mensaje con botones dirigido a una persona, justo en
    `BUTTON_TEXT_LIMIT`, tiene que quedar afuera del límite reducido y
    rechazarse -- nunca aceptarse para que el saludo lo rompa después."""
    from prisma.salida import PayloadValidationError

    ws = corework.workspace_id
    with admin(conn) as cur:
        mid = _membership_id(cur, ws, "Marcos Tarquini")
        cur.execute(
            """insert into pending_action (workspace_id, membership_id, herramienta,
                                            resumen, vence_en)
               values (%s, %s, 'test', 'x', now() + interval '1 hour')
               returning id""",
            (ws, mid))
        pid = cur.fetchone()["id"]
        with pytest.raises(PayloadValidationError):
            enqueue_outbox(
                cur, workspace_id=ws, chat_id=9001, text="x" * BUTTON_TEXT_LIMIT,
                recipient_membership_id=mid, dedupe_key="test:botones:margen",
                pending_action_id=pid)


# ---------------------------------------------------------------------------
# Integración con el despachador: quién sale primero se lleva el saludo
# ---------------------------------------------------------------------------

AHORA_HABIL = datetime(2026, 9, 28, 14, 0, tzinfo=timezone.utc)   # lunes 11:00 Bs.As.
AHORA_FUERA_DE_HORARIO = datetime(2026, 9, 28, 23, 30, tzinfo=timezone.utc)  # lunes 20:30


def _cal(cur, ws):
    return Calendario.desde_base(cur, ws)


def _mid_y_tg(cur, ws, nombre):
    cur.execute(
        """select m.id as mid, u.telegram_user_id as tg
             from membership m join app_user u on u.id = m.app_user_id
            where m.workspace_id = %s and u.nombre = %s""",
        (ws, nombre))
    fila = cur.fetchone()
    return str(fila["mid"]), fila["tg"]


def test_respuesta_primero_lleva_saludo_y_la_cadencia_despues_no(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    mid = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    tg = intake_world["north-lab"]["people"]["Taylor Quinn"]["telegram"]

    with espacio(conn, ws) as cur:
        _limpiar_saludo(cur, mid)
        cal = _cal(cur, ws)
        enqueue_outbox(
            cur, workspace_id=ws, chat_id=tg, text="Tenés una tarea abierta.",
            recipient_membership_id=mid, is_response=True,
            scheduled_for=AHORA_HABIL, dedupe_key="test:respuesta-primero:1")
        enqueue_outbox(
            cur, workspace_id=ws, chat_id=tg, text="Arranca la semana.",
            recipient_membership_id=mid, message_type="seguimiento",
            scheduled_for=AHORA_HABIL, dedupe_key="test:respuesta-primero:2")
        transporte = TransporteDePrueba()
        despachar(cur, ws, transporte, cal, AHORA_HABIL)
    conn.commit()

    enviados = sorted(transporte.enviados, key=lambda e: e.texto)
    cuerpos = [e.texto for e in transporte.enviados]
    saludados = [c for c in cuerpos if c.startswith("👋")]
    assert len(saludados) == 1
    assert saludados[0].startswith(f"{S.SALUDO_MANANA}\n\n")


def test_cadencia_primero_lleva_saludo_y_la_respuesta_despues_no(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    mid = intake_world["north-lab"]["people"]["Sam North"]["membership_id"]
    tg = intake_world["north-lab"]["people"]["Sam North"]["telegram"]

    with espacio(conn, ws) as cur:
        _limpiar_saludo(cur, mid)
        cal = _cal(cur, ws)
        transporte = TransporteDePrueba()
        # Primera pasada: sólo la cadencia.
        enqueue_outbox(
            cur, workspace_id=ws, chat_id=tg, text="Arranca la semana.",
            recipient_membership_id=mid, message_type="seguimiento",
            scheduled_for=AHORA_HABIL, dedupe_key="test:cadencia-primero:1")
        despachar(cur, ws, transporte, cal, AHORA_HABIL)
        assert len(transporte.enviados) == 1
        assert transporte.enviados[0].texto == f"{S.SALUDO_MANANA}\n\nArranca la semana."

        # Segunda pasada, más tarde el mismo día: la respuesta ya no saluda.
        enqueue_outbox(
            cur, workspace_id=ws, chat_id=tg, text="Ya la termine.",
            recipient_membership_id=mid, is_response=True,
            scheduled_for=AHORA_HABIL + timedelta(hours=1),
            dedupe_key="test:cadencia-primero:2")
        despachar(cur, ws, transporte, cal, AHORA_HABIL + timedelta(hours=1))
    conn.commit()

    assert len(transporte.enviados) == 2
    assert transporte.enviados[1].texto == "Ya la termine."


def test_aviso_de_otra_persona_primero_lleva_saludo(intake_world, conn):
    """Una entrega para el aprobador (herramientas._notificar_entrega_al_
    aprobador, por ejemplo) es un aviso que dispara OTRA persona -- si es lo
    primero que le llega hoy, también saluda."""
    ws = intake_world["north-lab"]["id"]
    mid = intake_world["north-lab"]["people"]["Morgan Hale"]["membership_id"]
    tg = intake_world["north-lab"]["people"]["Morgan Hale"]["telegram"]

    with espacio(conn, ws) as cur:
        _limpiar_saludo(cur, mid)
        cal = _cal(cur, ws)
        enqueue_outbox(
            cur, workspace_id=ws, chat_id=tg,
            text="Taylor Quinn entregó «Revisar bomba».",
            recipient_membership_id=mid, message_type="normal",
            scheduled_for=AHORA_HABIL, dedupe_key="test:aviso-tercero:1")
        transporte = TransporteDePrueba()
        despachar(cur, ws, transporte, cal, AHORA_HABIL)
    conn.commit()

    assert len(transporte.enviados) == 1
    assert transporte.enviados[0].texto == (
        f"{S.SALUDO_MANANA}\n\nTaylor Quinn entregó «Revisar bomba».")


def test_mensaje_pospuesto_saluda_recien_cuando_sale_de_verdad(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    mid = intake_world["north-lab"]["people"]["Sam Noble"]["membership_id"]
    tg = intake_world["north-lab"]["people"]["Sam Noble"]["telegram"]

    with espacio(conn, ws) as cur:
        _limpiar_saludo(cur, mid)
        cal = _cal(cur, ws)
        enqueue_outbox(
            cur, workspace_id=ws, chat_id=tg, text="Arranca la semana.",
            recipient_membership_id=mid, message_type="seguimiento",
            scheduled_for=AHORA_FUERA_DE_HORARIO, dedupe_key="test:pospuesto:1")
        transporte = TransporteDePrueba()

        # Fuera de horario: se pospone, no se manda -- no puede consumir el
        # saludo del día.
        resumen = despachar(cur, ws, transporte, cal, AHORA_FUERA_DE_HORARIO)
        assert resumen["pospuestos"] == 1
        assert transporte.enviados == []
        cur.execute("select ultima_fecha_local from greeting_state "
                    "where membership_id = %s", (mid,))
        assert cur.fetchone() is None      # nada reclamado todavía

        cur.execute("select programado_para from message_outbox "
                    "where dedupe_key = 'test:pospuesto:1'")
        reprogramado = cur.fetchone()["programado_para"]

        # Se despacha de nuevo cuando de verdad toca: ahí sí saluda.
        despachar(cur, ws, transporte, cal, reprogramado)
    conn.commit()

    assert len(transporte.enviados) == 1
    assert transporte.enviados[0].texto.startswith("👋")


def test_mensaje_de_grupo_no_saluda_ni_consume_la_reserva(intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    mid = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    tg_personal = intake_world["north-lab"]["people"]["Taylor Quinn"]["telegram"]

    with admin(conn) as cur:
        cur.execute("select grupo_chat_id from workspace where id = %s", (ws,))
        grupo_chat = cur.fetchone()["grupo_chat_id"]
    if grupo_chat is None:
        with admin(conn) as cur:
            cur.execute("update workspace set grupo_chat_id = -12345 where id = %s",
                        (ws,))
        conn.commit()
        grupo_chat = -12345

    with espacio(conn, ws) as cur:
        _limpiar_saludo(cur, mid)
        cal = _cal(cur, ws)
        # Mensaje de grupo: sin `recipient_membership_id`.
        enqueue_outbox(
            cur, workspace_id=ws, chat_id=grupo_chat, text="Estado del equipo.",
            message_type="seguimiento", scheduled_for=AHORA_HABIL,
            dedupe_key="test:grupo:1")
        transporte = TransporteDePrueba()
        despachar(cur, ws, transporte, cal, AHORA_HABIL)
        assert transporte.enviados[0].texto == "Estado del equipo."  # sin saludo

        # La reserva de Taylor sigue libre: su primer mensaje personal
        # después saluda igual.
        enqueue_outbox(
            cur, workspace_id=ws, chat_id=tg_personal, text="Tenés una tarea.",
            recipient_membership_id=mid, is_response=True,
            scheduled_for=AHORA_HABIL, dedupe_key="test:grupo:2")
        despachar(cur, ws, transporte, cal, AHORA_HABIL)
    conn.commit()

    assert len(transporte.enviados) == 2
    assert transporte.enviados[1].texto.startswith(f"{S.SALUDO_MANANA}\n\n")


def test_mensaje_descartado_no_consume_la_reserva(intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    mid = intake_world["north-lab"]["people"]["Sam North"]["membership_id"]
    tg = intake_world["north-lab"]["people"]["Sam North"]["telegram"]

    with espacio(conn, ws) as cur:
        _limpiar_saludo(cur, mid)
        cal = _cal(cur, ws)
        # `vence_en` ya pasado: se descarta sin despachar.
        enqueue_outbox(
            cur, workspace_id=ws, chat_id=tg, text="Esto ya no vale.",
            recipient_membership_id=mid, message_type="seguimiento",
            scheduled_for=AHORA_HABIL - timedelta(hours=2),
            expires_at=AHORA_HABIL - timedelta(hours=1),
            dedupe_key="test:descartado:1")
        transporte = TransporteDePrueba()
        resumen = despachar(cur, ws, transporte, cal, AHORA_HABIL)
        assert resumen["descartados"] == 1
        assert transporte.enviados == []
        cur.execute("select ultima_fecha_local from greeting_state "
                    "where membership_id = %s", (mid,))
        assert cur.fetchone() is None

        # El próximo mensaje real de la misma persona, mismo día, sí saluda.
        enqueue_outbox(
            cur, workspace_id=ws, chat_id=tg, text="Esto sí vale.",
            recipient_membership_id=mid, is_response=True,
            scheduled_for=AHORA_HABIL, dedupe_key="test:descartado:2")
        despachar(cur, ws, transporte, cal, AHORA_HABIL)
    conn.commit()

    assert len(transporte.enviados) == 1
    assert transporte.enviados[0].texto.startswith(f"{S.SALUDO_MANANA}\n\n")


def test_envio_fallido_revierte_la_reserva_del_saludo(intake_world, conn):
    """"Claim and send consistency": si el envío falla, el mismo punto de
    retorno que deshace la marca 'enviado' deshace la reserva del saludo con
    él -- el reintento vuelve a tener la reserva disponible."""
    ws = intake_world["north-lab"]["id"]
    mid = intake_world["north-lab"]["people"]["Sam Noble"]["membership_id"]
    tg = intake_world["north-lab"]["people"]["Sam Noble"]["telegram"]

    with espacio(conn, ws) as cur:
        _limpiar_saludo(cur, mid)
        cal = _cal(cur, ws)
        enqueue_outbox(
            cur, workspace_id=ws, chat_id=tg, text="Tenés una tarea.",
            recipient_membership_id=mid, is_response=True,
            scheduled_for=AHORA_HABIL, dedupe_key="test:envio-fallido:1")
        transporte = TransporteDePrueba(falla_en={tg})
        resumen = despachar(cur, ws, transporte, cal, AHORA_HABIL)
        assert resumen["fallidos"] == 1
        cur.execute("select ultima_fecha_local from greeting_state "
                    "where membership_id = %s", (mid,))
        assert cur.fetchone() is None      # nada quedó reclamado

        # Reintento con un transporte que sí entrega: reclama y saluda.
        transporte_ok = TransporteDePrueba()
        cur.execute("update message_outbox set estado = 'listo' "
                    "where dedupe_key = 'test:envio-fallido:1'")
        despachar(cur, ws, transporte_ok, cal, AHORA_HABIL + timedelta(minutes=1))
    conn.commit()

    assert len(transporte_ok.enviados) == 1
    assert transporte_ok.enviados[0].texto.startswith(f"{S.SALUDO_MANANA}\n\n")


def test_bienvenida_por_activacion_reclama_y_la_respuesta_del_dia_no_repite(
        conn, intake_world, monkeypatch):
    """R3-004: el camino de activación (`gateway._activacion`, `/start
    <token>`) encola la bienvenida con `es_bienvenida=True`; al
    despacharla, reclama la reserva del día sin saludo propio, y la primera
    respuesta real de esa misma fecha local no vuelve a saludar."""
    from prisma import gateway

    ws = intake_world["north-lab"]["id"]
    persona = intake_world["north-lab"]["people"]["Taylor Quinn"]
    tg_user = persona["telegram"]
    mid = persona["membership_id"]

    monkeypatch.setattr(gateway, "acusar_toque", lambda *a, **k: None)

    with admin(conn) as cur:
        _limpiar_saludo(cur, mid)
    conn.commit()

    resultado = gateway._activacion(conn, ws, "/start", tg_user, tg_user)
    assert resultado == {"ok": True}
    conn.commit()

    # `_activacion` programa la bienvenida con su propio reloj real
    # (`datetime.now`), así que esta prueba despacha con "ahora" real
    # también -- es `es_respuesta=True`, salta el chequeo de horario, así
    # que no importa qué hora sea de verdad.
    ahora = datetime.now(timezone.utc)
    with espacio(conn, ws) as cur:
        cal = _cal(cur, ws)
        transporte = TransporteDePrueba()
        despachar(cur, ws, transporte, cal, ahora)
        assert len(transporte.enviados) == 1
        assert not transporte.enviados[0].texto.startswith("👋")  # bienvenida sola

        enqueue_outbox(
            cur, workspace_id=ws, chat_id=tg_user, text="Tenés tareas abiertas.",
            recipient_membership_id=mid, is_response=True,
            scheduled_for=ahora, dedupe_key="test:bienvenida-activacion:1")
        despachar(cur, ws, transporte, cal, ahora + timedelta(hours=1))
    conn.commit()

    assert len(transporte.enviados) == 2
    assert transporte.enviados[1].texto == "Tenés tareas abiertas."  # sin saludo
