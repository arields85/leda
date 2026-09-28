"""Saludo diario (pack 06).

Un saludo por hora local del espacio (`workspace.zona_horaria`), como mucho
una vez por persona y por fecha local -- nunca de nuevo por una conversación
nueva, `/new`, `/reset` ni un período de inactividad dentro del mismo día.
Ver `src/prisma/saludo.py`.

`docs/decisions/0010-correo-verificado-y-google-en-el-producto.md` deja el
saludo diario explícitamente fuera de su alcance ("unidades de la línea
principal, no de esta decisión"): estas pruebas corren contra `main`, no
contra la rama auxiliar de correo y Google.
"""

from __future__ import annotations

import threading
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from prisma import saludo as S
from prisma.agente import responder
from prisma.autoridad import Canal, identificar
from prisma.calendario import Calendario
from prisma.db import admin, conectar, espacio
from prisma.llm import ProveedorGuionado, Respuesta

BA = ZoneInfo("America/Argentina/Buenos_Aires")


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s",
                (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _limpiar_saludo(cur, membership_id: str) -> None:
    """Vuelve a la persona a "todavía no saludada hoy": deshace la reserva
    lejana que pone `conftest._blindar_contra_saludo` para que el resto de
    la suite no se vuelva, sin querer, una prueba del saludo."""
    cur.execute("delete from greeting_state where membership_id = %s",
                (membership_id,))


def _membership_id(cur, ws: str, nombre: str) -> str:
    # Consulta directa, no la vista `integrante`: corre bajo `admin()`, sin
    # `prisma.workspace_id` en la sesión -- la vista no devolvería nada.
    cur.execute(
        """select m.id from membership m join app_user u on u.id = m.app_user_id
            where m.workspace_id = %s and u.nombre = %s""",
        (ws, nombre))
    return str(cur.fetchone()["id"])


# ---------------------------------------------------------------------------
# Regla exacta de hora local (pack 06 §2)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("hora_local,minuto,esperado", [
    (4, 59, S.SALUDO_MADRUGADA),
    (5, 0, S.SALUDO_MANANA),
    (11, 59, S.SALUDO_MANANA),
    (12, 0, S.SALUDO_TARDE),
    (19, 59, S.SALUDO_TARDE),
    (20, 0, S.SALUDO_MADRUGADA),
    (0, 0, S.SALUDO_MADRUGADA),        # medianoche local
    (23, 59, S.SALUDO_MADRUGADA),
])
def test_saludo_por_hora_en_los_limites_exactos(hora_local, minuto, esperado):
    # `saludo_por_hora` recibe la hora ya local (0-23): probar en el límite
    # de minuto se reduce a probar el entero de esa hora y la anterior --
    # la función no ve minutos.
    assert S.saludo_por_hora(hora_local) == esperado


def test_saludo_convierte_de_verdad_a_la_zona_del_espacio_no_solo_lee_utc():
    # 2026-01-15 02:30 UTC es, en Buenos Aires (UTC-3), 2026-01-14 23:30 --
    # otra hora Y otra fecha local. Si `saludo_por_hora` leyera la hora UTC
    # tal cual, este caso daría "Buen día" (hora UTC 2) en vez de "Buenas
    # noches" (hora local 23).
    momento = datetime(2026, 1, 15, 2, 30, tzinfo=timezone.utc)
    local = momento.astimezone(BA)
    assert local.hour == 23
    assert local.date() == date(2026, 1, 14)
    assert S.saludo_por_hora(local.hour) == S.SALUDO_MADRUGADA
    assert S.fecha_local(momento, BA) == date(2026, 1, 14)


def test_zona_de_workspace_lee_la_zona_real_del_espacio(conn, intake_world):
    with admin(conn) as cur:
        norte = S.zona_de_workspace(cur, intake_world["north-lab"]["id"])
        oeste = S.zona_de_workspace(cur, intake_world["west-studio"]["id"])
    assert norte == ZoneInfo("America/Argentina/Buenos_Aires")
    assert oeste == ZoneInfo("Europe/Madrid")


# ---------------------------------------------------------------------------
# Como mucho una vez por persona y por fecha local
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
    """Un reintento tardío (por ejemplo, cruzando medianoche) con una fecha
    ANTERIOR a la ya guardada no puede hacer retroceder el estado ni
    reclamar un saludo que ya salió -- `reclamar_saludo` compara con `>`,
    no con `is distinct from`."""
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
    """Dos turnos concurrentes de la misma persona (dos conexiones, dos
    transacciones reales) no pueden saludarla dos veces: PostgreSQL
    serializa el segundo `upsert` detrás del primero sobre la misma fila, y
    sólo el que de verdad avanza `ultima_fecha_local` gana."""
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
    assert sorted(resultados) == [False, True]        # exactamente uno gana

    with admin(conn) as cur:
        cur.execute("select ultima_fecha_local from greeting_state "
                    "where membership_id = %s", (mid,))
        assert cur.fetchone()["ultima_fecha_local"] == date(2026, 9, 28)


# ---------------------------------------------------------------------------
# La bienvenida de incorporación cuenta como el saludo del día (pack 06 §3, T28)
# ---------------------------------------------------------------------------

def test_reclamar_para_bienvenida_cuenta_como_el_saludo_de_esa_fecha(
        corework, conn):
    ws = corework.workspace_id
    ahora = datetime(2026, 9, 28, 14, 0, tzinfo=timezone.utc)   # 11:00 en Buenos Aires
    with admin(conn) as cur:
        mid = _membership_id(cur, ws, "Marcos Tarquini")
        _limpiar_saludo(cur, mid)

        S.reclamar_para_bienvenida(cur, workspace_id=ws, membership_id=mid,
                                   ahora=ahora)

        # La misma fecha local: el saludo por hora ya no corresponde, sin
        # que la bienvenida haya escrito ningún "👋" -- sólo reclamó la
        # reserva.
        saludo_mismo_dia = S.saludo_pendiente(
            cur, _SolicitanteFalso(ws, mid), ahora + timedelta(hours=2))
        assert saludo_mismo_dia is None

        # Al día local siguiente, vuelve a corresponder.
        saludo_dia_siguiente = S.saludo_pendiente(
            cur, _SolicitanteFalso(ws, mid), ahora + timedelta(days=1))
        assert saludo_dia_siguiente == S.SALUDO_MANANA


class _SolicitanteFalso:
    """Lo mínimo que `saludo.saludo_pendiente` necesita de un `Solicitante`
    -- evita depender de `autoridad.identificar` cuando ya se tiene el
    `membership_id` a mano."""

    def __init__(self, workspace_id: str, membership_id: str):
        self.workspace_id = workspace_id
        self.membership_id = membership_id


# ---------------------------------------------------------------------------
# Integración: el turno real antepone el saludo a la primera respuesta del
# día, nunca a la segunda -- nunca dejado a criterio del modelo.
# ---------------------------------------------------------------------------

def _con_proveedor(monkeypatch, guion):
    proveedor = ProveedorGuionado(guion=list(guion))
    monkeypatch.setattr("prisma.llm.desde_base", lambda cur, ws, key: proveedor)
    return proveedor


def test_la_primera_respuesta_del_dia_antepone_el_saludo_y_la_segunda_no(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    ahora = datetime(2026, 9, 28, 14, 0, tzinfo=timezone.utc)   # 11:00 en Buenos Aires

    with admin(conn) as cur:
        mid = _membership_id(cur, ws, "Marcos Tarquini")
        _limpiar_saludo(cur, mid)
    conn.commit()

    guion = [Respuesta(texto="Tenés una tarea abierta esta semana."),
            Respuesta(texto="Ya te la había contado.")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)

        r1 = responder(cur, quien, "qué tengo", proveedor, cal, chat_id=9101,
                       ahora=ahora)
        r2 = responder(cur, quien, "y ahora", proveedor, cal, chat_id=9101,
                       ahora=ahora + timedelta(minutes=5))

        cur.execute(
            """select cuerpo from message_outbox
                where chat_id = 9101 and es_respuesta order by programado_para""")
        cuerpos = [f["cuerpo"] for f in cur.fetchall()]

    assert cuerpos[0].startswith(f"{S.SALUDO_MANANA}\n\n")
    assert cuerpos[0] == f"{S.SALUDO_MANANA}\n\n{r1.texto}"
    assert not cuerpos[1].startswith("👋")
    assert cuerpos[1] == r2.texto


def test_al_dia_local_siguiente_vuelve_a_saludar(corework, conn, monkeypatch):
    ws = corework.workspace_id
    hoy = datetime(2026, 9, 28, 14, 0, tzinfo=timezone.utc)      # 11:00 Buenos Aires
    manana = hoy + timedelta(days=1)                             # mismo horario, otro día

    with admin(conn) as cur:
        mid = _membership_id(cur, ws, "Marcos Tarquini")
        _limpiar_saludo(cur, mid)
    conn.commit()

    guion = [Respuesta(texto="Anotado."), Respuesta(texto="Anotado de nuevo.")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "hoy", proveedor, cal, chat_id=9102, ahora=hoy)
        r2 = responder(cur, quien, "mañana", proveedor, cal, chat_id=9102,
                       ahora=manana)

        cur.execute(
            """select cuerpo from message_outbox
                where chat_id = 9102 and es_respuesta order by programado_para""")
        cuerpos = [f["cuerpo"] for f in cur.fetchall()]

    assert cuerpos[0].startswith(f"{S.SALUDO_MANANA}\n\n")
    assert cuerpos[1].startswith(f"{S.SALUDO_MANANA}\n\n")   # otro día: saluda de nuevo
    assert cuerpos[1] == f"{S.SALUDO_MANANA}\n\n{r2.texto}"


def test_la_bienvenida_de_incorporacion_evita_el_saludo_del_resto_del_dia(
        conn, intake_world, monkeypatch):
    """T28 (pack 06 §3): la bienvenida ya trae su propio saludo fijo
    ("Listo, <nombre>..."); la primera respuesta conversacional de esa misma
    fecha local no debe además anteponerle "👋 Buen día". `gateway._activacion`
    usa su propio reloj (`datetime.now`), así que esta prueba no controla
    `ahora`: confirma la reserva contra la fecha local real del espacio en
    vez de una hora fija -- las pruebas de arriba ya cubren la regla de hora
    y de una-vez-por-día con un `ahora` controlado."""
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

    with admin(conn) as cur:
        cur.execute(
            """select cuerpo from message_outbox where chat_id = %s
                order by programado_para""", (tg_user,))
        cuerpos = [f["cuerpo"] for f in cur.fetchall()]
        assert len(cuerpos) == 1
        assert not cuerpos[0].startswith("👋")   # la bienvenida es su propio saludo

        cur.execute("select ultima_fecha_local from greeting_state "
                    "where membership_id = %s", (mid,))
        fila = cur.fetchone()
        zona = S.zona_de_workspace(cur, ws)
    assert fila is not None
    assert fila["ultima_fecha_local"] == S.fecha_local(
        datetime.now(timezone.utc), zona)

    # Con la reserva de hoy ya tomada por la bienvenida, una respuesta
    # conversacional más tarde ese mismo día local no vuelve a saludar.
    ahora = datetime.now(timezone.utc)
    guion = [Respuesta(texto="Tenés tareas abiertas.")]
    proveedor = _con_proveedor(monkeypatch, guion)
    with espacio(conn, ws) as cur:
        quien = _quien_por_telegram(cur, ws, tg_user)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "qué tengo", proveedor, cal, chat_id=tg_user,
                 ahora=ahora)

        cur.execute(
            """select cuerpo from message_outbox where chat_id = %s
                order by programado_para""", (tg_user,))
        cuerpos = [f["cuerpo"] for f in cur.fetchall()]
    assert not cuerpos[-1].startswith("👋")


def _quien_por_telegram(cur, ws, tg_user):
    from prisma.autoridad import identificar_en_espacio
    return identificar_en_espacio(cur, tg_user, ws)
