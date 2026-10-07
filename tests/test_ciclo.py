"""Ciclo compartido de fondo (`ciclo.py`): cadencias vencidas calculadas por
cron, escalera y despacho por espacio, más el aviso a la administración una
vez por pasada -- lo que hoy usan `local.Escucha.tareas_de_fondo` y `servir`.
"""

from __future__ import annotations

import contextlib
import threading
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import httpx
import pytest

from leda import ciclo, reloj
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.despachador import TransporteDePrueba

BA = ZoneInfo("America/Argentina/Buenos_Aires")

# Token de bot falso, sólo para probar que un error de Telegram no lo
# filtra -- nunca se compara contra `os.environ` (regla de seguridad del
# proyecto: no afirmar directo contra variables de entorno).
TOKEN_FALSO = "123456789:AAAA-SECRETO-DE-PRUEBA-FALSO"


def _tarea(cur, ws, *, area="ot", persona="Marcos Tarquini", vence=None,
          estado="asignada"):
    cur.execute("select id from objective where workspace_id = %s limit 1", (ws,))
    obj = cur.fetchone()
    if not obj:
        cur.execute(
            """insert into objective (workspace_id, tipo, titulo)
               values (%s, 'operativo', 'Integrar comprimidora 3') returning id""",
            (ws,))
        obj = cur.fetchone()
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, fecha_objetivo,
                             criterio_aceptacion, evidencia_requerida)
           values (%s, %s, 'Programar PLC',
                   (select id from area where workspace_id = %s and slug = %s),
                   (select m.id from membership m join app_user u on u.id = m.app_user_id
                     where m.workspace_id = %s and u.nombre = %s),
                    %s, 'Resultado verificado', array['resultado_de_prueba'])
           returning id""",
        (ws, obj["id"], ws, area, ws, persona, vence))
    t = cur.fetchone()["id"]
    cur.execute(
        "insert into task_state_event (task_id, estado_nuevo, actor_kind) "
        "values (%s, %s, 'leda')", (t, estado))
    return t


def _espacio_activo(cur, slug: str, *, con_calendario: bool = True) -> str:
    """Un espacio activo mínimo, sin el pack de CoreWork -- para probar el
    ciclo con más de un espacio a la vez sin el costo de importar un pack
    completo."""
    cur.execute(
        """insert into workspace (slug, nombre, zona_horaria, activo)
           values (%s, %s, 'America/Argentina/Buenos_Aires', true) returning id""",
        (slug, slug))
    ws = str(cur.fetchone()["id"])
    if con_calendario:
        cur.execute(
            """insert into work_calendar (workspace_id, dias, hora_inicio, hora_fin)
               values (%s, array['lunes','martes','miercoles','jueves','viernes'],
                       '08:00', '18:00')""", (ws,))
    cur.execute("insert into persona_config (workspace_id) values (%s)", (ws,))
    return ws


def _esperar_bloqueada_por_lock(uri: str, pid: int, *, timeout: float = 5.0) -> None:
    """Espera hasta que el proceso `pid` quede bloqueado esperando un lock,
    sondeando `pg_stat_activity` -- reemplaza un `sleep` fijo, que es lento
    en el caso normal y flaco bajo carga (R3-003, revisión 2026-09-28)."""
    from leda.db import conectar

    polling = conectar(uri)
    try:
        limite = time.monotonic() + timeout
        with polling.cursor() as cur:
            while time.monotonic() < limite:
                cur.execute(
                    "select wait_event_type = 'Lock' as bloqueada "
                    "from pg_stat_activity where pid = %s", (pid,))
                fila = cur.fetchone()
                polling.rollback()
                if fila and fila["bloqueada"]:
                    return
                time.sleep(0.01)
    finally:
        polling.close()
    raise AssertionError(f"el proceso {pid} nunca quedó bloqueado esperando un lock")


def _fake_transportes(monkeypatch):
    """Un `TransporteDePrueba` por token, para inspeccionar qué se mandó por
    cada bot sin pegarle nunca a Telegram."""
    transportes: dict[str, TransporteDePrueba] = {}

    def _fabrica(token, cliente=None):
        transportes.setdefault(token, TransporteDePrueba())
        return transportes[token]

    monkeypatch.setattr(ciclo, "TransporteTelegram", _fabrica)
    return transportes


# ---------------------------------------------------------------------------
# cadencias_vencidas: el cálculo, sin tocar la cola ni el despacho
# ---------------------------------------------------------------------------

def test_cadencias_vencidas_detecta_disparo_desde_el_arranque(corework, conn):
    ws = corework.workspace_id
    arranque = datetime(2026, 7, 27, 9, 0, tzinfo=BA)
    ahora = datetime(2026, 7, 27, 9, 16, tzinfo=BA)
    with espacio(conn, ws) as cur:
        vencidas, fallidas, ok = ciclo.cadencias_vencidas(cur, ws, ahora, arranque)
    assert "objetivos_semanales" in {j["nombre"] for j in vencidas}
    assert fallidas == []
    assert "objetivos_semanales" in {j["nombre"] for j in ok}


def test_cadencias_vencidas_nada_antes_de_la_hora_del_cron(corework, conn):
    ws = corework.workspace_id
    arranque = datetime(2026, 7, 27, 9, 0, tzinfo=BA)
    ahora = datetime(2026, 7, 27, 9, 10, tzinfo=BA)  # antes de las 9:15
    with espacio(conn, ws) as cur:
        vencidas, fallidas, ok = ciclo.cadencias_vencidas(cur, ws, ahora, arranque)
    assert "objetivos_semanales" not in {j["nombre"] for j in vencidas}
    assert fallidas == []


def test_cadencias_vencidas_no_repone_disparo_anterior_al_arranque(corework, conn):
    """El proceso arrancó después de las 9:15 del lunes: esa ventana ya
    pasó y no se repone -- el próximo disparo es el lunes siguiente."""
    ws = corework.workspace_id
    arranque = datetime(2026, 7, 27, 9, 20, tzinfo=BA)
    ahora = datetime(2026, 7, 27, 9, 21, tzinfo=BA)
    with espacio(conn, ws) as cur:
        vencidas, fallidas, ok = ciclo.cadencias_vencidas(cur, ws, ahora, arranque)
    assert "objetivos_semanales" not in {j["nombre"] for j in vencidas}


def test_cadencias_vencidas_no_repone_disparo_perdido_tras_reiniciar(corework, conn):
    """R3-001: si el proceso corrió hace dos semanas (`ultima_corrida` vieja)
    y se reinició recién el martes -- perdiéndose el disparo del lunes en el
    medio -- el piso de búsqueda tiene que ser el MÁS TARDE de los dos
    (`arranque`), no `ultima_corrida` sola: si no, se repone el lunes
    perdido, contra la mecánica §12 ("una ventana que ya pasó no se envía
    tarde")."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 8, 14, 17, 0, tzinfo=BA))
    conn.commit()

    dos_lunes_atras = datetime(2026, 7, 13, 9, 15, tzinfo=BA)
    with espacio(conn, ws) as cur:
        cur.execute(
            "update cadence_job set ultima_corrida = %s "
            "where workspace_id = %s and nombre = 'objetivos_semanales'",
            (dos_lunes_atras, ws))
    conn.commit()

    # El proceso se reinicia el martes 21 -- el lunes 20 (intermedio) se
    # perdió y no debe reponerse.
    arranque = datetime(2026, 7, 21, 9, 0, tzinfo=BA)
    ahora = datetime(2026, 7, 21, 9, 16, tzinfo=BA)
    with espacio(conn, ws) as cur:
        vencidas, fallidas, ok = ciclo.cadencias_vencidas(cur, ws, ahora, arranque)

    assert "objetivos_semanales" not in {j["nombre"] for j in vencidas}
    assert fallidas == []


def test_cadencias_vencidas_no_repite_tras_actualizar_ultima_corrida(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 8, 14, 17, 0, tzinfo=BA))
    conn.commit()

    arranque = datetime(2026, 7, 27, 9, 0, tzinfo=BA)
    lunes_915 = datetime(2026, 7, 27, 9, 15, tzinfo=BA)
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        assert reloj.ejecutar_cadencia(cur, ws, "objetivos_semanales", cal, lunes_915) == 1
        vencidas, fallidas, ok = ciclo.cadencias_vencidas(
            cur, ws, lunes_915 + timedelta(minutes=1), arranque)
    assert "objetivos_semanales" not in {j["nombre"] for j in vencidas}


def test_cadencias_vencidas_usa_el_dia_de_semana_del_cron_no_el_de_apscheduler(
        corework, conn):
    """`CronTrigger.from_crontab` no corrige el corrimiento histórico de
    APScheduler (lunes=0 para APScheduler, domingo=0 para el cron de
    `cadence_job`): sin corregirlo, un cron de lunes dispara en martes.
    Corework tiene 'objetivos_semanales' en '15 9 * * 1' -- lunes 09:15."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 8, 14, 17, 0, tzinfo=BA))
    conn.commit()

    # El arranque queda apenas DESPUÉS del lunes 09:15 -- si el día de
    # semana no se corrigiera, APScheduler leería el "1" del cron como su
    # propio martes y encontraría un disparo ese mismo martes a las 9:16;
    # corregido, el próximo disparo es el lunes siguiente (3/8), así que el
    # martes no cuenta como vencido.
    arranque = datetime(2026, 7, 27, 9, 20, tzinfo=BA)
    with espacio(conn, ws) as cur:
        martes, fallidas, ok = ciclo.cadencias_vencidas(
            cur, ws, datetime(2026, 7, 28, 9, 16, tzinfo=BA), arranque)

    assert "objetivos_semanales" not in {j["nombre"] for j in martes}


def test_cadencias_vencidas_recoge_cadencia_agregada_sin_reiniciar(corework, conn):
    """Una fila de `cadence_job` nueva -- lo que deja un pack reimportado --
    se recoge en la próxima lectura, sin reiniciar ningún proceso."""
    ws = corework.workspace_id
    arranque = datetime(2026, 7, 20, 9, 0, tzinfo=BA)
    with admin(conn) as cur:
        cur.execute(
            """insert into cadence_job (workspace_id, nombre, cron, audiencia)
               values (%s, 'cadencia_nueva', '0 10 * * 1', 'grupo')""", (ws,))
    conn.commit()

    ahora = datetime(2026, 7, 27, 10, 1, tzinfo=BA)
    with espacio(conn, ws) as cur:
        vencidas, fallidas, ok = ciclo.cadencias_vencidas(cur, ws, ahora, arranque)
    assert "cadencia_nueva" in {j["nombre"] for j in vencidas}


# ---------------------------------------------------------------------------
# Fix A: una cadencia rota no frena a las demás
# ---------------------------------------------------------------------------

def test_cadencias_vencidas_aisla_una_fila_con_cron_invalido(corework, conn):
    """Un cron que `importador._a_cron` no supo traducir (o una edición a
    mano futura) queda tal cual en la base -- `xx yy` no es un minuto/hora
    válido para APScheduler. Esa fila va a `fallidas`; las demás se evalúan
    igual."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 8, 14, 17, 0, tzinfo=BA))
        cur.execute(
            """insert into cadence_job (workspace_id, nombre, cron, audiencia)
               values (%s, 'cadencia_rota', 'xx yy * * 1', 'grupo')""", (ws,))
    conn.commit()

    arranque = datetime(2026, 7, 27, 9, 0, tzinfo=BA)
    ahora = datetime(2026, 7, 27, 9, 16, tzinfo=BA)
    with espacio(conn, ws) as cur:
        vencidas, fallidas, ok = ciclo.cadencias_vencidas(cur, ws, ahora, arranque)

    assert "objetivos_semanales" in {j["nombre"] for j in vencidas}
    assert [j["nombre"] for j, _e, _c in fallidas] == ["cadencia_rota"]
    assert [c for _j, _e, c in fallidas] == [ciclo.CAUSA_CRON_INVALIDO]
    assert "cadencia_rota" not in {j["nombre"] for j in ok}


def test_ejecutar_ciclo_espacio_con_cadencia_rota_sigue_despachando_las_demas(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 8, 14, 17, 0, tzinfo=BA))
        cur.execute(
            """insert into cadence_job (workspace_id, nombre, cron, audiencia)
               values (%s, 'cadencia_rota', 'xx yy * * 1', 'grupo')""", (ws,))
    conn.commit()

    arranque = datetime(2026, 7, 27, 9, 0, tzinfo=BA)
    ahora = datetime(2026, 7, 27, 9, 16, tzinfo=BA)
    transporte = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        resumen = ciclo.ejecutar_ciclo_espacio(cur, ws, transporte, ahora, arranque)
    conn.commit()

    assert resumen["cadencias_encoladas"] == 1     # objetivos_semanales, igual
    assert resumen["enviados"] == 1                 # despacho sin frenarse
    assert [j["nombre"] for j, _e, _c in resumen["cadencias_fallidas"]] == ["cadencia_rota"]
    assert [c for _j, _e, c in resumen["cadencias_fallidas"]] == [ciclo.CAUSA_CRON_INVALIDO]


def test_cadencia_que_falla_en_la_base_al_ejecutarse_no_aborta_el_ciclo(
        corework, conn, monkeypatch):
    """Una cadencia con cron válido que falla DENTRO de la base al ejecutarse
    no deja la transacción abortada: la escalera y el despacho siguen."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 8, 14, 17, 0, tzinfo=BA))
    conn.commit()

    def _falla_en_la_base(cur, workspace_id, nombre, cal, ahora):
        cur.execute("select 1/0")

    monkeypatch.setattr(ciclo.reloj, "ejecutar_cadencia", _falla_en_la_base)

    arranque = datetime(2026, 7, 27, 9, 0, tzinfo=BA)
    ahora = datetime(2026, 7, 27, 9, 16, tzinfo=BA)
    transporte = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        resumen = ciclo.ejecutar_ciclo_espacio(cur, ws, transporte, ahora, arranque)
    conn.commit()

    # Escalera y despacho corrieron sobre la misma transacción, sin abortar.
    assert isinstance(resumen["escalera_encoladas"], int)
    assert "enviados" in resumen
    assert [j["nombre"] for j, _e, _c in resumen["cadencias_fallidas"]] == ["objetivos_semanales"]
    # El cron era válido: lo que falló fue la ejecución, causa distinta de
    # un cron roto (R4-002/R2-001/R3-005).
    assert [c for _j, _e, c in resumen["cadencias_fallidas"]] == [ciclo.CAUSA_FALLO_EJECUCION]
    assert "objetivos_semanales" not in [j["nombre"] for j in resumen["cadencias_ok"]]


# ---------------------------------------------------------------------------
# Fix B: _dia_semana_apscheduler contra disparos reales, forma por forma
# ---------------------------------------------------------------------------

_NOMBRES_DIA = ("domingo", "lunes", "martes", "miercoles", "jueves", "viernes", "sabado")


def _dias_que_disparan(dia_semana_expr: str) -> set[str]:
    """Para cada día de una semana de referencia (26/7/2026, domingo, a
    1/8/2026, sábado), si el cron `0 0 * * <expr>` dispara ese día."""
    trigger = ciclo._trigger_de(f"0 0 * * {dia_semana_expr}", "UTC")
    base = datetime(2026, 7, 26, tzinfo=timezone.utc)
    disparan = set()
    for i, nombre in enumerate(_NOMBRES_DIA):
        dia = base + timedelta(days=i)
        arranque = dia - timedelta(minutes=1)
        ahora = dia + timedelta(minutes=1)
        siguiente = trigger.get_next_fire_time(arranque, ahora)
        if siguiente is not None and siguiente <= ahora:
            disparan.add(nombre)
    return disparan


def test_dia_semana_apscheduler_domingo_como_0():
    assert _dias_que_disparan("0") == {"domingo"}


def test_dia_semana_apscheduler_domingo_como_7():
    assert _dias_que_disparan("7") == {"domingo"}


def test_dia_semana_apscheduler_rango_que_empieza_en_domingo():
    """El caso que rompía: corregir sólo las puntas de "0-5" da "6-4",
    invertido -- hay que expandir el rango y corregir cada día por separado."""
    assert _dias_que_disparan("0-5") == {
        "domingo", "lunes", "martes", "miercoles", "jueves", "viernes"}


def test_dia_semana_apscheduler_lista():
    assert _dias_que_disparan("1,3,5") == {"lunes", "miercoles", "viernes"}


def test_dia_semana_apscheduler_paso_desde_asterisco():
    assert _dias_que_disparan("*/2") == {"domingo", "martes", "jueves", "sabado"}


def test_dia_semana_apscheduler_paso_dentro_de_un_rango():
    assert _dias_que_disparan("1-5/2") == {"lunes", "miercoles", "viernes"}


def test_dia_semana_apscheduler_nombre_no_se_traduce():
    assert _dias_que_disparan("mon") == {"lunes"}


def test_dia_semana_apscheduler_rango_de_nombres_no_se_traduce():
    assert _dias_que_disparan("mon-fri") == {
        "lunes", "martes", "miercoles", "jueves", "viernes"}


def test_dia_semana_apscheduler_asterisco_dispara_todos_los_dias():
    assert _dias_que_disparan("*") == set(_NOMBRES_DIA)


def test_dia_semana_apscheduler_rango_1_a_7_es_toda_la_semana():
    """R3-002: `%7` sobre las PUNTAS antes de ordenar convertía "1-7" en
    "1-0", invertido, y el rango se rechazaba -- 7 es la otra forma de
    domingo, no un día aparte de una semana."""
    assert _dias_que_disparan("1-7") == set(_NOMBRES_DIA)


def test_dia_semana_apscheduler_rango_5_a_7_es_viernes_a_domingo():
    assert _dias_que_disparan("5-7") == {"viernes", "sabado", "domingo"}


def test_dia_semana_apscheduler_rango_0_a_7_es_toda_la_semana():
    """0 y 7 son el mismo domingo: "0-7" no puede quedar como "sólo
    domingo" (`range(0 % 7, 7 % 7 + 1)` daba eso)."""
    assert _dias_que_disparan("0-7") == set(_NOMBRES_DIA)


def test_dia_semana_apscheduler_valor_fuera_de_rango_se_rechaza():
    """R3-002: "9" no es un día de semana -- ni siquiera con la otra forma
    de domingo (7) -- y `%7` lo plegaba en silencio a "martes" (2) en vez de
    rechazarlo."""
    import pytest

    with pytest.raises(ValueError):
        ciclo._expandir_dia_cron("9")


def test_dia_semana_apscheduler_rango_fuera_de_rango_se_rechaza():
    import pytest

    with pytest.raises(ValueError):
        ciclo._expandir_dia_cron("1-9")


# ---------------------------------------------------------------------------
# ejecutar_ciclo_espacio: cadencia + escalera + despacho, en una pasada
# ---------------------------------------------------------------------------

def test_ejecutar_ciclo_espacio_encola_y_despacha_la_cadencia_vencida(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 8, 14, 17, 0, tzinfo=BA))
    conn.commit()

    arranque = datetime(2026, 7, 27, 9, 0, tzinfo=BA)
    ahora = datetime(2026, 7, 27, 9, 16, tzinfo=BA)
    transporte = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        resumen = ciclo.ejecutar_ciclo_espacio(cur, ws, transporte, ahora, arranque)
    conn.commit()

    assert resumen["cadencias_encoladas"] == 1
    assert resumen["enviados"] == 1
    assert len(transporte.enviados) == 1


def test_ejecutar_ciclo_espacio_sin_cadencias_no_encola_pero_despacha_igual(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 7, 20, 12, 0, tzinfo=BA))
    conn.commit()

    arranque = datetime(2026, 7, 27, 9, 0, tzinfo=BA)
    ahora = datetime(2026, 7, 27, 9, 16, tzinfo=BA)  # cadencia vencida, pero apagada
    transporte = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        resumen = ciclo.ejecutar_ciclo_espacio(
            cur, ws, transporte, ahora, arranque, con_cadencias=False)
    conn.commit()

    assert resumen["cadencias_encoladas"] == 0
    assert resumen["escalera_encoladas"] >= 1   # la escalera sigue corriendo
    assert resumen["enviados"] >= 1              # y el despacho también


# ---------------------------------------------------------------------------
# Ciclo.tick: todos los espacios activos, más el aviso admin una vez
# ---------------------------------------------------------------------------

def test_ciclo_tick_despacha_admin_una_sola_vez_con_dos_espacios(
        conn, corework, monkeypatch):
    from leda import incidentes
    from leda.db import registrar_auditoria

    with admin(conn) as cur:
        ws2 = _espacio_activo(cur, "segundo-equipo")
        cur.execute(
            "insert into app_user (telegram_user_id, nombre) values (%s, %s) "
            "returning id", (900001, "Admin Ciclo"))
        admin_id = str(cur.fetchone()["id"])
        cur.execute(
            "insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
            (admin_id,))
        registrar_auditoria(
            cur, accion="mensaje_admin", actor_app_user_id=admin_id,
            actor_kind="persona", detalle={"chat_id": 900001})
        incidentes.registrar_incidente(
            cur, corework.workspace_id, "Falló algo en una prueba.",
            etapa="prueba_directa")
    conn.commit()

    monkeypatch.setenv("LEDA_BOT_TOKEN_SEGUNDO-EQUIPO", "tok-segundo")
    monkeypatch.setenv("LEDA_BOT_TOKEN_ADMIN", "tok-admin-ciclo")
    transportes = _fake_transportes(monkeypatch)

    # `admin_notice.programado_para` sale de `now()` al registrar el
    # incidente (arriba): el "ahora" del ciclo tiene que ser posterior a
    # ese instante real, no una fecha fija de prueba.
    arranque = datetime.now(timezone.utc) - timedelta(days=1)
    ahora = datetime.now(timezone.utc) + timedelta(minutes=1)
    c = ciclo.Ciclo(lambda: conn, arranque=arranque)
    resultados = c.tick(ahora=ahora)

    assert "corework" in resultados and "segundo-equipo" in resultados
    assert len(transportes["tok-admin-ciclo"].enviados) == 1  # una sola vez
    assert resultados["_admin"]["enviados"] == 1


def test_ciclo_tick_espacio_sin_token_se_avisa_una_vez_y_los_demas_siguen(
        conn, corework, monkeypatch):
    with admin(conn) as cur:
        _espacio_activo(cur, "sin-token")
    conn.commit()

    transportes = _fake_transportes(monkeypatch)
    c = ciclo.Ciclo(lambda: conn, arranque=datetime(2026, 1, 1, tzinfo=timezone.utc))

    r1 = c.tick(ahora=datetime(2026, 1, 2, tzinfo=timezone.utc))
    assert r1["sin-token"] == {"error": "sin_token_de_bot"}
    assert "corework" in r1 and "error" not in r1["corework"]

    with admin(conn) as cur:
        cur.execute(
            """select count(*) n from incident where etapa = 'ciclo_de_fondo'
                and resumen_sanitizado like %s""", ("%sin-token%",))
        avisos_tras_primera = cur.fetchone()["n"]
    conn.commit()
    assert avisos_tras_primera == 1

    r2 = c.tick(ahora=datetime(2026, 1, 2, 0, 5, tzinfo=timezone.utc))
    assert r2["sin-token"] == {"error": "sin_token_de_bot"}

    with admin(conn) as cur:
        cur.execute(
            """select count(*) n from incident where etapa = 'ciclo_de_fondo'
                and resumen_sanitizado like %s""", ("%sin-token%",))
        avisos_tras_segunda = cur.fetchone()["n"]
    conn.commit()
    assert avisos_tras_segunda == 1   # no se repite en cada pasada


def test_ciclo_tick_excepcion_en_un_espacio_no_frena_los_demas(
        conn, corework, monkeypatch):
    """El segundo espacio no tiene calendario laboral: `Calendario.desde_base`
    revienta con `LookupError` al procesarlo -- eso no debe frenar a
    `corework`, y queda un incidente."""
    with admin(conn) as cur:
        _espacio_activo(cur, "sin-calendario", con_calendario=False)
    conn.commit()

    monkeypatch.setenv("LEDA_BOT_TOKEN_SIN-CALENDARIO", "tok-roto")
    transportes = _fake_transportes(monkeypatch)

    c = ciclo.Ciclo(lambda: conn, arranque=datetime(2026, 1, 1, tzinfo=timezone.utc))
    resultados = c.tick(ahora=datetime(2026, 1, 2, tzinfo=timezone.utc))

    assert resultados["sin-calendario"] == {"error": "LookupError"}
    assert "error" not in resultados["corework"]  # el otro espacio siguió andando

    with admin(conn) as cur:
        cur.execute(
            """select count(*) n from incident where etapa = 'ciclo_de_fondo'
                and resumen_sanitizado like %s""", ("%sin-calendario%",))
        avisos = cur.fetchone()["n"]
    conn.commit()
    assert avisos == 1


def test_ciclo_tick_corre_escalera_en_espacio_activo_sin_cadence_job(
        conn, monkeypatch, intake_world):
    """El gap que tenía `reloj.montar`: un espacio sin ninguna fila de
    `cadence_job` seguía sin escalera. `Ciclo.tick` enumera todos los
    espacios activos, no sólo los que tienen cadencias."""
    ws = intake_world["north-lab"]["id"]
    persona = intake_world["north-lab"]["people"]["Sam North"]
    area_id = intake_world["north-lab"]["areas"]["field"]
    objetivo = intake_world["north-lab"]["objectives"][0]

    with admin(conn) as cur:
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, fecha_objetivo,
                                 criterio_aceptacion, evidencia_requerida)
               values (%s, %s, 'Tarea atrasada', %s, %s, %s,
                       'Listo', array['resultado_de_prueba']) returning id""",
            (ws, objetivo, area_id, persona["membership_id"],
             datetime(2026, 7, 20, 12, 0, tzinfo=BA)))
        tid = cur.fetchone()["id"]
        cur.execute(
            "insert into task_state_event (task_id, estado_nuevo, actor_kind) "
            "values (%s, 'asignada', 'leda')", (tid,))
        cur.execute("select count(*) n from cadence_job where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 0   # sin cadencias configuradas
    conn.commit()

    monkeypatch.setenv("LEDA_BOT_TOKEN_NORTH-LAB", "tok-north-lab")
    _fake_transportes(monkeypatch)

    c = ciclo.Ciclo(lambda: conn, arranque=datetime(2026, 7, 1, tzinfo=BA))
    resultados = c.tick(ahora=datetime(2026, 7, 20, 15, 0, tzinfo=BA))

    assert "error" not in resultados["north-lab"]
    assert resultados["north-lab"]["escalera_encoladas"] == 1
    assert resultados["north-lab"]["enviados"] == 1


# ---------------------------------------------------------------------------
# R4-001: un mensaje ya entregado y marcado no se reenvía porque OTRO
# mensaje del mismo lote falló después
# ---------------------------------------------------------------------------

def test_despachar_no_reenvia_el_primero_si_el_segundo_falla_al_marcarse(
        corework, conn, monkeypatch):
    """Antes, sólo el ENVÍO estaba protegido: si la marca de 'enviado' (el
    UPDATE posterior) fallaba, la excepción escapaba de `despachar` sin
    contenerse y el `rollback` de la transacción entera -- compartida con la
    escalera -- devolvía a 'listo' TAMBIÉN los mensajes anteriores del mismo
    lote, que se reenviaban en la próxima pasada."""
    from leda import despachador as desp

    ws = corework.workspace_id
    ahora = datetime(2026, 7, 27, 10, 0, tzinfo=BA)  # lunes, en horario

    with espacio(conn, ws) as cur:
        for i in range(2):
            cur.execute(
                """insert into message_outbox
                     (workspace_id, chat_id, cuerpo, estado, programado_para,
                      dedupe_key)
                   values (%s, %s, %s, 'listo', %s, %s)""",
                (ws, 5000 + i, f"mensaje de prueba {i}",
                 ahora - timedelta(microseconds=2 - i), f"prueba-r4-001-{i}"))
    conn.commit()

    llamadas = {"n": 0}
    original = desp._marcar_enviado

    def _falla_en_el_segundo(cur, ahora, outbox_id):
        llamadas["n"] += 1
        if llamadas["n"] == 2:
            raise RuntimeError("falla simulada al marcar 'enviado'")
        return original(cur, ahora, outbox_id)

    monkeypatch.setattr(desp, "_marcar_enviado", _falla_en_el_segundo)

    transporte = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        r1 = desp.despachar(cur, ws, transporte, cal, ahora)
    conn.commit()

    assert r1["enviados"] == 1   # el primero se entregó y quedó marcado
    assert r1["fallidos"] == 1   # el segundo falló al marcarse

    # "próxima pasada": si el primero hubiera vuelto a 'listo' por un
    # rollback de todo el lote, se reenviaría acá.
    monkeypatch.setattr(desp, "_marcar_enviado", original)
    transporte2 = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        r2 = desp.despachar(cur, ws, transporte2, cal, ahora)
    conn.commit()

    assert len(transporte2.enviados) == 1   # sólo el segundo (reintento)
    assert r2["enviados"] == 1


# ---------------------------------------------------------------------------
# R3-001 (revisión 2026-09-28): marcar 'enviado' va ANTES de enviar, no
# después -- si el envío ya salió y la marca falla, se reenvía seguro.
# ---------------------------------------------------------------------------

def test_intentar_envio_no_envia_si_falla_la_marca_de_enviado(
        corework, conn, monkeypatch):
    """Si el UPDATE que marca 'enviado' falla, el mensaje NUNCA se manda:
    la marca -- el cambio de estado durable -- va antes del envío, no
    después."""
    from leda import despachador as desp

    ws = corework.workspace_id
    ahora = datetime(2026, 7, 27, 10, 0, tzinfo=BA)  # lunes, en horario

    with espacio(conn, ws) as cur:
        cur.execute(
            """insert into message_outbox
                 (workspace_id, chat_id, cuerpo, estado, programado_para,
                  dedupe_key)
               values (%s, 6000, 'mensaje de prueba', 'listo', %s, %s)""",
            (ws, ahora, "prueba-r3-001-marca"))
    conn.commit()

    def _marca_rota(cur, ahora, outbox_id):
        raise RuntimeError("falla simulada al marcar 'enviado'")

    monkeypatch.setattr(desp, "_marcar_enviado", _marca_rota)

    transporte = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        r = desp.despachar(cur, ws, transporte, cal, ahora)
    conn.commit()

    assert transporte.enviados == []   # nunca se llegó a llamar a enviar
    assert r["fallidos"] == 1

    with admin(conn) as cur:
        cur.execute("select estado from message_outbox where dedupe_key = %s",
                    ("prueba-r3-001-marca",))
        fila = cur.fetchone()
    conn.commit()
    assert fila["estado"] == "listo"   # sigue pendiente, nunca quedó 'enviado'


def test_intentar_envio_conserva_la_marca_si_falla_guardar_el_id_de_telegram(
        corework, conn, monkeypatch, capsys):
    """El mensaje YA se entregó cuando se intenta guardar el id de
    Telegram: si ese UPDATE falla, la marca 'enviado' tiene que quedar en
    pie -- no se reenvía en la próxima pasada -- y el fallo se reporta sin
    el texto crudo de la excepción."""
    from leda import despachador as desp

    ws = corework.workspace_id
    ahora = datetime(2026, 7, 27, 10, 0, tzinfo=BA)

    with espacio(conn, ws) as cur:
        cur.execute(
            """insert into message_outbox
                 (workspace_id, chat_id, cuerpo, estado, programado_para,
                  dedupe_key)
               values (%s, 6001, 'mensaje de prueba', 'listo', %s, %s)""",
            (ws, ahora, "prueba-r3-001-id"))
    conn.commit()

    original_guardar = desp._guardar_id_telegram
    texto_secreto = "falla simulada al guardar el id de Telegram"

    def _id_roto(cur, tg_id, outbox_id):
        raise RuntimeError(texto_secreto)

    monkeypatch.setattr(desp, "_guardar_id_telegram", _id_roto)

    transporte = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        r = desp.despachar(cur, ws, transporte, cal, ahora)
    conn.commit()

    assert len(transporte.enviados) == 1   # sí se entregó
    assert r["enviados"] == 1              # cuenta como éxito: ya se entregó

    salida = capsys.readouterr().out
    assert texto_secreto not in salida     # nunca el texto crudo de la excepción
    assert "RuntimeError" in salida

    with admin(conn) as cur:
        cur.execute(
            """select estado, telegram_message_id from message_outbox
                where dedupe_key = %s""",
            ("prueba-r3-001-id",))
        fila = cur.fetchone()
    conn.commit()
    assert fila["estado"] == "enviado"          # la marca queda en pie
    assert fila["telegram_message_id"] is None  # el id no se pudo guardar

    # "próxima pasada": si la marca se hubiera deshecho, se reenviaría acá.
    monkeypatch.setattr(desp, "_guardar_id_telegram", original_guardar)
    transporte2 = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        r2 = desp.despachar(cur, ws, transporte2, cal, ahora)
    conn.commit()

    assert transporte2.enviados == []   # no se reenvía: ya estaba 'enviado'
    assert r2["enviados"] == 0


# ---------------------------------------------------------------------------
# R3-004: `servir` y `escuchar` evaluando la misma cadencia a la vez no la
# encolan dos veces
# ---------------------------------------------------------------------------

def test_ejecutar_cadencia_evaluada_a_la_vez_por_dos_conexiones_no_duplica(
        corework, conn, uri):
    """Lo que evita encolar la misma cadencia dos veces cuando `servir` y
    `escuchar` la evalúan casi al mismo tiempo es el `dedupe_key` ÚNICO de
    `message_outbox` -- no una coordinación en Python -- así que tiene que
    seguir siéndolo bajo concurrencia real, no sólo en llamadas
    secuenciales."""
    from leda.db import conectar

    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 8, 14, 17, 0, tzinfo=BA))
    conn.commit()

    ahora = datetime(2026, 7, 27, 9, 16, tzinfo=BA)
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)

    otra = conectar(uri)
    pid_otra = otra.info.backend_pid
    resultado_otra: dict = {}
    seguir = threading.Event()

    def _en_otro_hilo():
        with espacio(otra, ws) as cur2:
            seguir.wait(timeout=5)
            resultado_otra["n"] = reloj.ejecutar_cadencia(
                cur2, ws, "objetivos_semanales", cal, ahora)
        otra.commit()

    hilo = threading.Thread(target=_en_otro_hilo)
    hilo.start()
    try:
        with espacio(conn, ws) as cur1:
            n1 = reloj.ejecutar_cadencia(cur1, ws, "objetivos_semanales", cal, ahora)
            # La otra conexión intenta el mismo `insert` AHORA, mientras esta
            # transacción sigue abierta -- Postgres la obliga a esperar en
            # vez de dejarla pasar sin ver este `insert` todavía sin commit.
            # Se espera a que quede REALMENTE bloqueada (sondeo, no un
            # `sleep` a ciegas) antes de confirmar.
            seguir.set()
            _esperar_bloqueada_por_lock(uri, pid_otra)
        conn.commit()
    finally:
        hilo.join(timeout=5)
        otra.close()

    assert "n" in resultado_otra
    n2 = resultado_otra["n"]
    assert n1 + n2 == 1   # sólo una de las dos transacciones lo encoló

    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from message_outbox where workspace_id = %s", (ws,))
        total = cur.fetchone()["n"]
    conn.commit()
    assert total == 1


# ---------------------------------------------------------------------------
# reloj.montar: un solo job de intervalo que llama al ciclo compartido
# ---------------------------------------------------------------------------

class _SchedulerFalso:
    """Nunca arranca un hilo real: sólo registra qué se le pidió agendar."""

    def __init__(self) -> None:
        self.jobs: list[dict] = []

    def add_job(self, func, trigger=None, args=None, kwargs=None, id=None,
               replace_existing=False, **trigger_args):
        self.jobs.append({
            "func": func, "trigger": trigger, "kwargs": kwargs, "id": id,
            "replace_existing": replace_existing, "trigger_args": trigger_args,
        })

    def start(self):
        raise AssertionError("montar() no debe arrancar el scheduler")


def test_montar_registra_un_solo_job_de_intervalo_sin_iniciar_nada(conn):
    fake = _SchedulerFalso()
    resultado = reloj.montar(lambda: conn, scheduler=fake, con_cadencias=False)

    assert resultado is fake
    assert len(fake.jobs) == 1
    job = fake.jobs[0]
    assert job["trigger"] == "interval"
    assert job["trigger_args"].get("seconds") == ciclo.INTERVALO_SEGUNDOS
    assert job["kwargs"] == {"con_cadencias": False}
    assert isinstance(job["func"].__self__, ciclo.Ciclo)  # método atado, mismo ciclo cada vez


def test_montar_default_es_con_cadencias_activas(conn):
    fake = _SchedulerFalso()
    reloj.montar(lambda: conn, scheduler=fake)

    assert fake.jobs[0]["kwargs"] == {"con_cadencias": True}


# ---------------------------------------------------------------------------
# Fix C: sin aluvión de incidentes -- deduplicado mientras la falla persiste
# ---------------------------------------------------------------------------

def test_ciclo_no_repite_incidente_mientras_la_falla_persiste(
        conn, corework, monkeypatch):
    with admin(conn) as cur:
        _espacio_activo(cur, "persistente", con_calendario=False)
    conn.commit()

    monkeypatch.setenv("LEDA_BOT_TOKEN_PERSISTENTE", "tok-persistente")
    _fake_transportes(monkeypatch)

    c = ciclo.Ciclo(lambda: conn, arranque=datetime(2026, 1, 1, tzinfo=timezone.utc))
    ahora = datetime(2026, 1, 2, tzinfo=timezone.utc)
    for _ in range(3):
        r = c.tick(ahora=ahora)
        assert r["persistente"] == {"error": "LookupError"}

    with admin(conn) as cur:
        cur.execute(
            """select count(*) n from incident where etapa = 'ciclo_de_fondo'
                and resumen_sanitizado like %s""", ("%persistente%",))
        total = cur.fetchone()["n"]
    conn.commit()
    assert total == 1   # tres pasadas, la misma falla: un solo incidente


def test_ciclo_reporta_de_nuevo_tras_recuperarse_y_fallar_de_nuevo(
        conn, corework, monkeypatch):
    with admin(conn) as cur:
        ws = _espacio_activo(cur, "intermitente", con_calendario=False)
    conn.commit()

    monkeypatch.setenv("LEDA_BOT_TOKEN_INTERMITENTE", "tok-intermitente")
    _fake_transportes(monkeypatch)

    c = ciclo.Ciclo(lambda: conn, arranque=datetime(2026, 1, 1, tzinfo=timezone.utc))
    ahora = datetime(2026, 1, 2, tzinfo=timezone.utc)

    r1 = c.tick(ahora=ahora)
    assert r1["intermitente"] == {"error": "LookupError"}

    with admin(conn) as cur:
        cur.execute(
            """insert into work_calendar (workspace_id, dias, hora_inicio, hora_fin)
               values (%s, array['lunes','martes','miercoles','jueves','viernes'],
                       '08:00', '18:00')""", (ws,))
    conn.commit()
    r2 = c.tick(ahora=ahora)
    assert "error" not in r2["intermitente"]      # se recuperó

    with admin(conn) as cur:
        cur.execute("delete from work_calendar where workspace_id = %s", (ws,))
    conn.commit()
    r3 = c.tick(ahora=ahora)
    assert r3["intermitente"] == {"error": "LookupError"}  # y volvió a fallar

    with admin(conn) as cur:
        cur.execute(
            """select count(*) n from incident where etapa = 'ciclo_de_fondo'
                and resumen_sanitizado like %s""", ("%intermitente%",))
        total = cur.fetchone()["n"]
    conn.commit()
    assert total == 2   # una por cada aparición de la falla, no por pasada


# ---------------------------------------------------------------------------
# Fix E: nunca un cliente HTTP nuevo por pasada -- se cachea por token
# ---------------------------------------------------------------------------

def test_transporte_telegram_cerrar_cierra_el_cliente_http():
    from leda.despachador import TransporteTelegram

    class _ClienteFalso:
        def __init__(self) -> None:
            self.cerrado = False

        def close(self) -> None:
            self.cerrado = True

    cliente = _ClienteFalso()
    transporte = TransporteTelegram("tok", cliente=cliente)
    transporte.cerrar()
    assert cliente.cerrado


def test_ciclo_reusa_el_transporte_para_el_mismo_token_entre_pasadas(
        conn, corework, monkeypatch):
    construcciones: list[str] = []

    def _fabrica(token, cliente=None):
        construcciones.append(token)
        return TransporteDePrueba()

    monkeypatch.setattr(ciclo, "TransporteTelegram", _fabrica)

    c = ciclo.Ciclo(lambda: conn, arranque=datetime(2026, 1, 1, tzinfo=timezone.utc))
    ahora = datetime(2026, 1, 2, tzinfo=timezone.utc)
    c.tick(ahora=ahora)
    c.tick(ahora=ahora)

    assert construcciones.count("prueba:token") == 1  # nunca uno nuevo por pasada


def test_ciclo_reusa_el_transporte_admin_entre_pasadas(conn, corework, monkeypatch):
    construcciones: list[str] = []

    def _fabrica(token, cliente=None):
        construcciones.append(token)
        return TransporteDePrueba()

    monkeypatch.setattr(ciclo, "TransporteTelegram", _fabrica)
    monkeypatch.setenv("LEDA_BOT_TOKEN_ADMIN", "tok-admin-reuso")

    c = ciclo.Ciclo(lambda: conn, arranque=datetime(2026, 1, 1, tzinfo=timezone.utc))
    ahora = datetime(2026, 1, 2, tzinfo=timezone.utc)
    c.tick(ahora=ahora)
    c.tick(ahora=ahora)

    assert construcciones.count("tok-admin-reuso") == 1


def test_ciclo_cierra_el_transporte_viejo_si_el_token_cambia(
        conn, corework, monkeypatch):
    creados: list = []

    class _TransporteFalso(TransporteDePrueba):
        def __init__(self, token, cliente=None) -> None:
            super().__init__()
            self.token = token
            self.cerrado = False
            creados.append(self)

        def cerrar(self) -> None:
            self.cerrado = True

    monkeypatch.setattr(ciclo, "TransporteTelegram", _TransporteFalso)
    monkeypatch.setenv("LEDA_BOT_TOKEN_COREWORK", "tok-v1")
    # Esta máquina puede tener un LEDA_BOT_TOKEN_ADMIN real en `.env`: sin
    # sacarlo, el ciclo construiría un segundo transporte (el de admin) y el
    # conteo de abajo, que es sobre el total, no sobre "corework" en
    # particular, no sería determinístico.
    monkeypatch.delenv("LEDA_BOT_TOKEN_ADMIN", raising=False)

    c = ciclo.Ciclo(lambda: conn, arranque=datetime(2026, 1, 1, tzinfo=timezone.utc))
    ahora = datetime(2026, 1, 2, tzinfo=timezone.utc)
    c.tick(ahora=ahora)

    assert len(creados) == 1
    primero = creados[0]
    assert not primero.cerrado

    monkeypatch.setenv("LEDA_BOT_TOKEN_COREWORK", "tok-v2")
    c.tick(ahora=ahora)

    assert len(creados) == 2       # se construyó uno nuevo
    assert primero.cerrado         # y se cerró el viejo


# ---------------------------------------------------------------------------
# R4-003/R3-003: una conexión por ciclo, no una nueva por pasada
# ---------------------------------------------------------------------------

def test_ciclo_tick_reusa_la_conexion_entre_pasadas(conn, corework, monkeypatch):
    """Antes, `tick` llamaba a `conn_factory()` en cada pasada y nunca
    cerraba la anterior: una conexión nueva cada `INTERVALO_SEGUNDOS`, para
    siempre."""
    conteo = {"n": 0}

    def _fabrica():
        conteo["n"] += 1
        return conn

    c = ciclo.Ciclo(_fabrica, arranque=datetime(2026, 1, 1, tzinfo=timezone.utc))
    ahora = datetime(2026, 1, 2, tzinfo=timezone.utc)
    c.tick(ahora=ahora)
    c.tick(ahora=ahora)
    c.tick(ahora=ahora)

    assert conteo["n"] == 1


def test_ciclo_tick_conexion_inalcanzable_se_reporta_una_vez_sin_traceback(capsys):
    """Si `conn_factory()` (o el primer uso de la conexión) falla, `tick` no
    puede dejar escapar la excepción -- eso rompería el job de APScheduler
    cada `INTERVALO_SEGUNDOS`, sin deduplicar nada -- y tiene que reintentar
    conectar en la próxima pasada, no quedarse pegado a la misma conexión
    rota."""
    intentos = {"n": 0}

    def _fabrica_rota():
        intentos["n"] += 1
        raise ConnectionError("no hay servidor en este puerto")

    c = ciclo.Ciclo(_fabrica_rota, arranque=datetime(2026, 1, 1, tzinfo=timezone.utc))
    ahora = datetime(2026, 1, 2, tzinfo=timezone.utc)

    for _ in range(3):
        r = c.tick(ahora=ahora)   # no debe levantar
        assert r == {"_error": {"tipo": "ConnectionError"}}

    assert intentos["n"] == 3     # reintenta conectar en cada pasada
    salida = capsys.readouterr().out
    assert salida.count("no pudo conectar") == 1   # deduplicado, no un aluvión


# ---------------------------------------------------------------------------
# R3-002 (revisión 2026-09-28): cerrar la conexión ANTES de descartarla
# ---------------------------------------------------------------------------

def test_ciclo_tick_cierra_la_conexion_antes_de_descartarla_si_falla_al_listar_espacios(
        monkeypatch):
    """Antes, una falla persistente al listar espacios activos descartaba
    `self._conn` (la ponía en `None` para que la próxima pasada reconecte)
    sin cerrarla nunca: una conexión filtrada por pasada, para siempre."""

    class _ConexionFalsa:
        def __init__(self) -> None:
            self.closed = False
            self.cierres = 0

        def rollback(self) -> None:
            pass

        def close(self) -> None:
            self.cierres += 1
            self.closed = True

    def _admin_roto(conn):
        raise RuntimeError("no se pudo listar espacios activos")

    monkeypatch.setattr(ciclo, "admin", _admin_roto)

    fake = _ConexionFalsa()
    c = ciclo.Ciclo(lambda: fake, arranque=datetime(2026, 1, 1, tzinfo=timezone.utc))
    ahora = datetime(2026, 1, 2, tzinfo=timezone.utc)

    r = c.tick(ahora=ahora)

    assert r == {"_error": {"tipo": "RuntimeError"}}
    assert fake.cierres == 1        # se cerró, no se filtró
    assert fake.closed
    assert c._conn is None          # y se descartó de verdad


def test_ciclo_tick_descarta_la_conexion_aunque_falle_el_reporte(monkeypatch):
    """Si el reporte del incidente también falla, la conexión rota igual se
    cierra y se descarta: la pasada siguiente no la reusa."""

    class _ConexionFalsa:
        closed = False
        cierres = 0

        def rollback(self) -> None:
            pass

        def close(self) -> None:
            self.cierres += 1
            self.closed = True

    def _admin_roto(conn):
        raise RuntimeError("no se pudo listar espacios activos")

    def _reporte_roto(*args, **kwargs):
        raise RuntimeError("tampoco se pudo reportar")

    monkeypatch.setattr(ciclo, "admin", _admin_roto)
    monkeypatch.setattr(ciclo, "reportar_fallo", _reporte_roto)

    fake = _ConexionFalsa()
    c = ciclo.Ciclo(lambda: fake, arranque=datetime(2026, 1, 1, tzinfo=timezone.utc))

    # El `finally` que cierra y descarta la conexión corre antes de que la
    # segunda falla (la del propio reporte) se propague -- `tick()` SÍ
    # levanta acá, no la traga (R3-005, revisión 2026-09-28+2: antes esta
    # prueba aceptaba cualquiera de los dos resultados).
    with pytest.raises(RuntimeError, match="tampoco se pudo reportar"):
        c.tick(ahora=datetime(2026, 1, 2, tzinfo=timezone.utc))

    assert fake.cierres == 1
    assert c._conn is None


# ---------------------------------------------------------------------------
# R3-004 (revisión 2026-09-28): reconexión de `Ciclo._conectar`
# ---------------------------------------------------------------------------

def test_ciclo_conectar_reconecta_si_la_conexion_guardada_esta_cerrada():
    """`_conectar` reusa la conexión guardada mientras esté viva, pero la
    reemplaza si quedó cerrada -- no la sigue devolviendo."""
    from types import SimpleNamespace

    conexiones = [SimpleNamespace(closed=False), SimpleNamespace(closed=False)]
    fabrica = iter(conexiones)

    c = ciclo.Ciclo(lambda: next(fabrica))

    primera = c._conectar()
    assert primera is conexiones[0]
    assert c._conectar() is conexiones[0]   # sigue viva: no reconecta

    conexiones[0].closed = True
    segunda = c._conectar()
    assert segunda is conexiones[1]         # quedó cerrada: reconecta
    assert c._conectar() is conexiones[1]   # y ahora reusa la nueva


def test_ciclo_tick_reconecta_en_la_proxima_pasada_tras_una_conexion_muerta_a_mitad(
        uri, corework, monkeypatch):
    """Si la conexión se vuelve inservible a mitad de una pasada -- una
    falla fatal, no un simple error de aplicación -- `_conectar` tiene que
    reemplazarla en la próxima pasada en vez de reintentar para siempre con
    una conexión muerta."""
    from leda.db import conectar

    monkeypatch.setenv("LEDA_BOT_TOKEN_COREWORK", "tok-reconexion")
    monkeypatch.delenv("LEDA_BOT_TOKEN_ADMIN", raising=False)
    _fake_transportes(monkeypatch)

    conexiones: list = []

    def _fabrica():
        c = conectar(uri)
        conexiones.append(c)
        return c

    original = ciclo.ejecutar_ciclo_espacio
    llamadas = {"n": 0}

    def _muere_en_la_primera(cur, *a, **k):
        llamadas["n"] += 1
        if llamadas["n"] == 1:
            cur.connection.close()   # simula una falla fatal de red
            raise RuntimeError("conexión perdida a mitad de la pasada")
        return original(cur, *a, **k)

    monkeypatch.setattr(ciclo, "ejecutar_ciclo_espacio", _muere_en_la_primera)

    c = ciclo.Ciclo(_fabrica, arranque=datetime(2026, 1, 1, tzinfo=timezone.utc))
    ahora = datetime(2026, 1, 2, tzinfo=timezone.utc)

    try:
        r1 = c.tick(ahora=ahora)
        assert "error" in r1["corework"]
        assert conexiones[0].closed

        r2 = c.tick(ahora=ahora)
        assert "error" not in r2["corework"]
        assert len(conexiones) == 2       # reconectó en la próxima pasada
        assert c._conn is conexiones[1]
    finally:
        for cx in conexiones:
            with contextlib.suppress(Exception):
                cx.close()


# ---------------------------------------------------------------------------
# R4-002/R2-001/R3-005: causa distinta en el texto según qué falló
# ---------------------------------------------------------------------------

def test_reportar_cadencias_rotas_distingue_cron_invalido_de_fallo_en_ejecucion(
        conn, corework):
    """Un cron VÁLIDO que falla al ejecutarse no puede quedar reportado como
    "cron inválido" -- son causas distintas, con textos distintos y claves
    de deduplicación distintas (para que una no suprima a la otra)."""
    ws = corework.workspace_id
    supresor = ciclo.SupresorDeRepetidos()

    resumen_cron_invalido = {
        "cadencias_ok": [],
        "cadencias_fallidas": [
            ({"nombre": "objetivos_semanales"}, ValueError("mal"),
             ciclo.CAUSA_CRON_INVALIDO)],
    }
    reportados = []
    ciclo.reportar_cadencias_rotas(
        conn, supresor, ws, "corework", resumen_cron_invalido,
        imprimir=reportados.append)
    assert len(reportados) == 1
    assert "cron inválido" in reportados[0]

    resumen_fallo_ejecucion = {
        "cadencias_ok": [],
        "cadencias_fallidas": [
            ({"nombre": "cierre_semanal"}, ZeroDivisionError("x"),
             ciclo.CAUSA_FALLO_EJECUCION)],
    }
    reportados2 = []
    ciclo.reportar_cadencias_rotas(
        conn, supresor, ws, "corework", resumen_fallo_ejecucion,
        imprimir=reportados2.append)
    assert len(reportados2) == 1
    assert "cron inválido" not in reportados2[0]
    assert "falló al ejecutarse" in reportados2[0]


# ---------------------------------------------------------------------------
# R2-002: una sola implementación del reporte de cadencias rotas, y que
# imprime sólo cuando `reportar_fallo` de verdad reportó
# ---------------------------------------------------------------------------

def test_reportar_cadencias_rotas_imprime_solo_cuando_reportar_fallo_reporta(
        conn, corework):
    """`ciclo.reportar_cadencias_rotas` es ahora la única implementación que
    usan `Ciclo.tick` y `Escucha.tareas_de_fondo` (R2-002): antes,
    `tareas_de_fondo` tenía su propia copia que imprimía en cada pasada sin
    mirar si `reportar_fallo` de verdad reportó, a diferencia de `Ciclo`."""
    ws = corework.workspace_id
    supresor = ciclo.SupresorDeRepetidos()

    def _resumen() -> dict:
        return {
            "cadencias_ok": [],
            "cadencias_fallidas": [
                ({"nombre": "objetivos_semanales"}, ValueError("mal"),
                 ciclo.CAUSA_CRON_INVALIDO)],
        }

    llamadas_imprimir: list[str] = []
    ciclo.reportar_cadencias_rotas(
        conn, supresor, ws, "corework", _resumen(), imprimir=llamadas_imprimir.append)
    ciclo.reportar_cadencias_rotas(
        conn, supresor, ws, "corework", _resumen(), imprimir=llamadas_imprimir.append)

    # La misma falla, sin recuperarse en el medio: se imprime (y se
    # registra el incidente) sólo la primera vez.
    assert len(llamadas_imprimir) == 1


# ---------------------------------------------------------------------------
# R3-006: la supresión de un fallo se marca sólo después de escribirlo
# ---------------------------------------------------------------------------

def test_reportar_fallo_no_suprime_si_la_escritura_del_incidente_falla(
        conn, corework, monkeypatch):
    """Antes, `debe_reportar` marcaba la clave como reportada ANTES de
    escribir el incidente: si la escritura fallaba, esa falla quedaba
    deduplicada para siempre -- ni el reintento de la próxima pasada podía
    volver a escribirla."""
    ws = corework.workspace_id
    intentos = {"n": 0}
    original = ciclo.registrar_incidente

    def _falla_la_primera_vez(cur, *a, **k):
        intentos["n"] += 1
        if intentos["n"] == 1:
            raise RuntimeError("falla simulada al escribir el incidente")
        return original(cur, *a, **k)

    monkeypatch.setattr(ciclo, "registrar_incidente", _falla_la_primera_vez)

    supresor = ciclo.SupresorDeRepetidos()
    r1 = ciclo.reportar_fallo(
        conn, supresor, ws, "prueba", "algo falló en la prueba", RuntimeError("x"))
    assert r1 is False   # la escritura falló: no se marca como reportado

    r2 = ciclo.reportar_fallo(
        conn, supresor, ws, "prueba", "algo falló en la prueba", RuntimeError("x"))
    assert r2 is True    # se reintenta y esta vez se escribe

    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where workspace_id = %s", (ws,))
        total = cur.fetchone()["n"]
    conn.commit()
    assert total == 1


# ---------------------------------------------------------------------------
# R1-001 (revisión 2026-09-28): un error de la API de Telegram nunca lleva
# la URL del pedido -- la URL de la API de Telegram lleva el token del bot.
# ---------------------------------------------------------------------------

def test_pedido_telegram_traduce_un_401_con_descripcion_sin_token():
    from leda import despachador as desp

    pedido = httpx.Request(
        "POST", f"https://api.telegram.org/bot{TOKEN_FALSO}/sendMessage")
    respuesta = httpx.Response(
        401, request=pedido,
        json={"ok": False, "error_code": 401, "description": "Unauthorized"})

    with pytest.raises(desp.ErrorTelegram) as info:
        desp.pedido_telegram(respuesta.raise_for_status)

    error = info.value
    filtra = TOKEN_FALSO in str(error) or TOKEN_FALSO in repr(error)
    assert not filtra, "el error traducido filtra el token del bot"
    assert str(error) == "HTTPStatusError HTTP 401: Unauthorized"


def test_pedido_telegram_traduce_un_500_sin_descripcion_sin_token():
    from leda import despachador as desp

    pedido = httpx.Request(
        "POST", f"https://api.telegram.org/bot{TOKEN_FALSO}/sendMessage")
    respuesta = httpx.Response(500, request=pedido)  # sin cuerpo JSON

    with pytest.raises(desp.ErrorTelegram) as info:
        desp.pedido_telegram(respuesta.raise_for_status)

    error = info.value
    filtra = TOKEN_FALSO in str(error) or TOKEN_FALSO in repr(error)
    assert not filtra, "el error traducido filtra el token del bot"
    assert str(error) == "HTTPStatusError HTTP 500"


def test_pedido_telegram_traduce_un_error_de_conexion_que_lleva_la_url():
    """Un error de red puede traer la URL en su propio mensaje -- no sólo un
    `HTTPStatusError` -- y se traduce igual, sin mirar `str(e)` del original."""
    from leda import despachador as desp

    url = f"https://api.telegram.org/bot{TOKEN_FALSO}/getUpdates"
    pedido = httpx.Request("GET", url)
    error_original = httpx.ConnectError(f"sin red para {url}", request=pedido)

    def _falla():
        raise error_original

    with pytest.raises(desp.ErrorTelegram) as info:
        desp.pedido_telegram(_falla)

    error = info.value
    filtra = TOKEN_FALSO in str(error) or TOKEN_FALSO in repr(error)
    assert not filtra, "el error traducido filtra el token del bot"
    assert str(error) == "ConnectError"


def test_pedido_telegram_corta_la_cadena_de_excepciones():
    """`from None`: ni `__cause__` ni el traceback del error ya traducido
    arrastran el original -- que sí llevaba el token."""
    from leda import despachador as desp

    def _falla():
        raise RuntimeError(f"secreto en bot{TOKEN_FALSO}")

    with pytest.raises(desp.ErrorTelegram) as info:
        desp.pedido_telegram(_falla)

    error = info.value
    assert error.__cause__ is None
    assert error.__suppress_context__ is True


def test_texto_error_seguro_no_retraduce_un_error_ya_traducido():
    from leda import despachador as desp

    ya_traducido = desp.ErrorTelegram("HTTPStatusError HTTP 401: Unauthorized")
    assert desp.texto_error_seguro(ya_traducido) == str(ya_traducido)


def test_mantener_chat_activo_traduce_el_error_del_ping_de_typing(monkeypatch):
    """El `sendChatAction` de fondo hoy descarta su error entero (es
    cosmético) -- pero pasa por el mismo traductor que el resto de las
    llamadas a Telegram, así que si algún día deja de descartarse, ya no
    puede filtrar el token."""
    from leda import despachador as desp

    capturados: list[Exception] = []
    original = desp.pedido_telegram

    def _pedido_que_registra(fn, *a, **k):
        try:
            return original(fn, *a, **k)
        except desp.ErrorTelegram as e:
            capturados.append(e)
            raise

    monkeypatch.setattr(desp, "pedido_telegram", _pedido_que_registra)

    class _ClienteQueFalla:
        def post(self, url, json=None):
            pedido = httpx.Request("POST", url)
            raise httpx.HTTPStatusError(
                "fallo", request=pedido, response=httpx.Response(401, request=pedido))

    with desp.mantener_chat_activo(
            TOKEN_FALSO, 123, cliente=_ClienteQueFalla(), intervalo=0.01,
            espera_cierre=0.5, umbral=0):
        time.sleep(0.1)

    assert capturados, "el ping de typing nunca intentó llamar a Telegram"
    for error in capturados:
        filtra = TOKEN_FALSO in str(error) or TOKEN_FALSO in repr(error)
        assert not filtra, "el ping de typing filtra el token del bot"


def test_despachar_no_guarda_el_token_en_ultimo_error_si_telegram_falla(
        corework, conn):
    """`message_outbox.ultimo_error` -- lo que queda tras `_fallo` -- nunca
    lleva el token del bot, ni siquiera cuando el transporte real de
    Telegram es el que fallò (R1-001, revisión 2026-09-28): antes,
    `TransporteTelegram.enviar` dejaba escapar el `HTTPStatusError` de
    httpx tal cual, y su `str()` lleva la URL completa con el token."""
    from leda import despachador as desp

    class _ClienteQueFalla:
        def post(self, url, json=None):
            pedido = httpx.Request("POST", url)
            raise httpx.HTTPStatusError(
                "fallo", request=pedido,
                response=httpx.Response(
                    401, request=pedido,
                    json={"ok": False, "description": "Unauthorized"}))

    ws = corework.workspace_id
    ahora = datetime(2026, 7, 27, 10, 0, tzinfo=BA)

    with espacio(conn, ws) as cur:
        cur.execute(
            """insert into message_outbox
                 (workspace_id, chat_id, cuerpo, estado, programado_para,
                  dedupe_key)
               values (%s, 6002, 'mensaje de prueba', 'listo', %s, %s)""",
            (ws, ahora, "prueba-r1-001-ultimo-error"))
    conn.commit()

    transporte = desp.TransporteTelegram(TOKEN_FALSO, cliente=_ClienteQueFalla())
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        desp.despachar(cur, ws, transporte, cal, ahora)
    conn.commit()

    with admin(conn) as cur:
        cur.execute(
            "select ultimo_error from message_outbox where dedupe_key = %s",
            ("prueba-r1-001-ultimo-error",))
        ultimo_error = cur.fetchone()["ultimo_error"]
    conn.commit()

    filtra = TOKEN_FALSO in (ultimo_error or "")
    assert not filtra, "message_outbox.ultimo_error guarda el token del bot"
    assert "401" in ultimo_error
