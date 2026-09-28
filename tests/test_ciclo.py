"""Ciclo compartido de fondo (`ciclo.py`): cadencias vencidas calculadas por
cron, escalera y despacho por espacio, más el aviso a la administración una
vez por pasada -- lo que hoy usan `local.Escucha.tareas_de_fondo` y `servir`.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from prisma import ciclo, reloj
from prisma.calendario import Calendario
from prisma.db import admin, espacio
from prisma.despachador import TransporteDePrueba

BA = ZoneInfo("America/Argentina/Buenos_Aires")


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
        "values (%s, %s, 'prisma')", (t, estado))
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
    assert [j["nombre"] for j, _e in fallidas] == ["cadencia_rota"]
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
    assert [j["nombre"] for j, _e in resumen["cadencias_fallidas"]] == ["cadencia_rota"]


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
    assert [j["nombre"] for j, _e in resumen["cadencias_fallidas"]] == ["objetivos_semanales"]
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
    from prisma import incidentes
    from prisma.db import registrar_auditoria

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

    monkeypatch.setenv("PRISMA_BOT_TOKEN_SEGUNDO-EQUIPO", "tok-segundo")
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "tok-admin-ciclo")
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

    monkeypatch.setenv("PRISMA_BOT_TOKEN_SIN-CALENDARIO", "tok-roto")
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
            "values (%s, 'asignada', 'prisma')", (tid,))
        cur.execute("select count(*) n from cadence_job where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 0   # sin cadencias configuradas
    conn.commit()

    monkeypatch.setenv("PRISMA_BOT_TOKEN_NORTH-LAB", "tok-north-lab")
    _fake_transportes(monkeypatch)

    c = ciclo.Ciclo(lambda: conn, arranque=datetime(2026, 7, 1, tzinfo=BA))
    resultados = c.tick(ahora=datetime(2026, 7, 20, 15, 0, tzinfo=BA))

    assert "error" not in resultados["north-lab"]
    assert resultados["north-lab"]["escalera_encoladas"] == 1
    assert resultados["north-lab"]["enviados"] == 1


# ---------------------------------------------------------------------------
# Requisito 7: `servir` y `escuchar` corriendo a la vez no duplican envíos
# ---------------------------------------------------------------------------

def test_despachar_con_fila_tomada_por_otra_conexion_no_la_duplica(
        corework, conn, uri):
    """`for update skip locked` es lo que permite correr `servir` y
    `escuchar` sobre el mismo espacio sin que ambos entreguen el mismo
    mensaje: mientras otra conexión sostiene el lock (transacción sin
    `commit` todavía), esta lo saltea en vez de bloquearse o reprocesarlo."""
    from prisma.db import conectar
    from prisma.despachador import despachar

    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 8, 14, 17, 0, tzinfo=BA))
    conn.commit()

    ahora = datetime(2026, 7, 27, 9, 16, tzinfo=BA)
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        assert reloj.ejecutar_cadencia(cur, ws, "objetivos_semanales", cal, ahora) == 1

    otra = conectar(uri)
    try:
        with otra.transaction():
            with otra.cursor() as cur_otra:
                cur_otra.execute("set local role prisma_app")
                cur_otra.execute(
                    "select set_config('prisma.workspace_id', %s, true)", (ws,))
                cur_otra.execute(
                    """select id from message_outbox
                        where workspace_id = %s and estado = 'listo'
                        for update skip locked""", (ws,))
                assert len(cur_otra.fetchall()) == 1  # sostiene el lock, sin commit

            transporte = TransporteDePrueba()
            with espacio(conn, ws) as cur:
                cal = Calendario.desde_base(cur, ws)
                r = despachar(cur, ws, transporte, cal, ahora)
            conn.commit()
            assert r["enviados"] == 0        # la fila estaba tomada: la salteó
            assert transporte.enviados == []
        # el `with otra.transaction()` ya confirmó al salir: lock liberado
    finally:
        otra.close()

    transporte2 = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        r2 = despachar(cur, ws, transporte2, cal, ahora)
    conn.commit()
    assert r2["enviados"] == 1               # liberado el lock, ahora sí la entrega


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
# local.Escucha: usa el mismo ciclo compartido -- cadencias automáticas
# ---------------------------------------------------------------------------

def test_escucha_tareas_de_fondo_dispara_cadencia_vencida_automaticamente(
        corework, conn):
    """Hasta ahora una cadencia sólo se disparaba a mano
    (`python -m prisma correr`); `tareas_de_fondo` ahora la dispara sola
    cuando su cron ya venció."""
    from prisma.local import Escucha

    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 8, 14, 17, 0, tzinfo=BA))
    conn.commit()

    e = Escucha(conn, "corework", ws, "tok")
    e.transporte = TransporteDePrueba()
    e.arranque = datetime(2026, 7, 27, 9, 0, tzinfo=BA)

    resumen = e.tareas_de_fondo(ahora=datetime(2026, 7, 27, 9, 16, tzinfo=BA))

    assert resumen["cadencias_encoladas"] == 1
    assert resumen["enviados"] == 1
    assert len(e.transporte.enviados) == 1


def test_escucha_tareas_de_fondo_con_sin_cadencias_no_dispara_cadencia(
        corework, conn):
    from prisma.local import Escucha

    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 8, 14, 17, 0, tzinfo=BA))
    conn.commit()

    e = Escucha(conn, "corework", ws, "tok", con_cadencias=False)
    e.transporte = TransporteDePrueba()
    e.arranque = datetime(2026, 7, 27, 9, 0, tzinfo=BA)

    resumen = e.tareas_de_fondo(ahora=datetime(2026, 7, 27, 9, 16, tzinfo=BA))

    assert resumen["cadencias_encoladas"] == 0


# ---------------------------------------------------------------------------
# Fix C: sin aluvión de incidentes -- deduplicado mientras la falla persiste
# ---------------------------------------------------------------------------

def test_ciclo_no_repite_incidente_mientras_la_falla_persiste(
        conn, corework, monkeypatch):
    with admin(conn) as cur:
        _espacio_activo(cur, "persistente", con_calendario=False)
    conn.commit()

    monkeypatch.setenv("PRISMA_BOT_TOKEN_PERSISTENTE", "tok-persistente")
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

    monkeypatch.setenv("PRISMA_BOT_TOKEN_INTERMITENTE", "tok-intermitente")
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
# Fix D: `escuchar` sobrevive a una pasada rota
# ---------------------------------------------------------------------------

def test_tareas_de_fondo_con_excepcion_no_rompe_y_reporta_una_vez(
        conn, corework, monkeypatch):
    from prisma.local import Escucha

    ws = corework.workspace_id
    e = Escucha(conn, "corework", ws, "tok")
    e.transporte = TransporteDePrueba()

    def _revienta(*a, **k):
        raise RuntimeError("falla simulada de la pasada de fondo")

    monkeypatch.setattr(ciclo, "ejecutar_ciclo_espacio", _revienta)

    resumen1 = e.tareas_de_fondo()   # no debe levantar
    assert resumen1["enviados"] == 0

    resumen2 = e.tareas_de_fondo()   # sigue fallando -- tampoco debe levantar
    assert resumen2["enviados"] == 0

    with admin(conn) as cur:
        cur.execute(
            """select count(*) n from incident where etapa = 'ciclo_de_fondo'
                and resumen_sanitizado like %s""", ("%corework%",))
        total = cur.fetchone()["n"]
    conn.commit()
    assert total == 1   # deduplicado: una sola vez mientras sigue igual


def test_tareas_de_fondo_la_consola_no_filtra_el_texto_crudo_del_error(
        conn, corework, monkeypatch, capsys):
    from prisma.local import Escucha

    ws = corework.workspace_id
    e = Escucha(conn, "corework", ws, "tok")
    e.transporte = TransporteDePrueba()

    secreto = "postgresql://prisma_app:s3cr3t-p4ss@db.interno:5432/prisma"

    def _revienta(*a, **k):
        raise RuntimeError(f"no se pudo conectar: {secreto}")

    monkeypatch.setattr(ciclo, "ejecutar_ciclo_espacio", _revienta)

    e.tareas_de_fondo()

    salida = capsys.readouterr().out
    assert secreto not in salida
    assert "s3cr3t-p4ss" not in salida
    assert "RuntimeError" in salida


def test_tareas_de_fondo_reporta_cadencia_rota_sin_frenar_escalera_ni_despacho(
        conn, corework, monkeypatch):
    from prisma.local import Escucha

    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 7, 20, 12, 0, tzinfo=BA))
        cur.execute(
            """insert into cadence_job (workspace_id, nombre, cron, audiencia)
               values (%s, 'cadencia_rota', 'xx yy * * 1', 'grupo')""", (ws,))
    conn.commit()

    e = Escucha(conn, "corework", ws, "tok")
    e.transporte = TransporteDePrueba()
    e.arranque = datetime(2026, 7, 27, 9, 0, tzinfo=BA)

    resumen = e.tareas_de_fondo(ahora=datetime(2026, 7, 27, 9, 16, tzinfo=BA))

    assert resumen["enviados"] >= 1   # la escalera se despachó igual

    with admin(conn) as cur:
        cur.execute(
            """select count(*) n from incident where etapa = 'ciclo_de_fondo'
                and resumen_sanitizado like %s""", ("%cadencia_rota%",))
        total = cur.fetchone()["n"]
    conn.commit()
    assert total == 1


def test_tareas_de_fondo_avisa_admin_aunque_la_pasada_del_espacio_falle(
        conn, corework, monkeypatch):
    from prisma import incidentes
    from prisma.db import registrar_auditoria
    from prisma.local import Escucha, _AdminBot

    ws = corework.workspace_id
    with admin(conn) as cur:
        cur.execute(
            "insert into app_user (telegram_user_id, nombre) values (%s, %s) "
            "returning id", (777001, "Admin Fondo"))
        admin_id = str(cur.fetchone()["id"])
        cur.execute(
            "insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
            (admin_id,))
        registrar_auditoria(
            cur, accion="mensaje_admin", actor_app_user_id=admin_id,
            actor_kind="persona", detalle={"chat_id": 777001})
        incidentes.registrar_incidente(
            cur, ws, "Falló algo en una prueba.", etapa="prueba_directa")
    conn.commit()

    e = Escucha(conn, "corework", ws, "tok")
    e.transporte = TransporteDePrueba()
    transporte_admin = TransporteDePrueba()
    e._admin_bot = _AdminBot(token="tok-admin-ya-resuelto", transporte=transporte_admin)

    def _revienta(*a, **k):
        raise RuntimeError("falla simulada de la pasada de fondo")

    monkeypatch.setattr(ciclo, "ejecutar_ciclo_espacio", _revienta)

    resumen = e.tareas_de_fondo()

    assert resumen["avisos_admin_enviados"] == 1
    assert len(transporte_admin.enviados) == 1


# ---------------------------------------------------------------------------
# Fix E: nunca un cliente HTTP nuevo por pasada -- se cachea por token
# ---------------------------------------------------------------------------

def test_transporte_telegram_cerrar_cierra_el_cliente_http():
    from prisma.despachador import TransporteTelegram

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
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "tok-admin-reuso")

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
    monkeypatch.setenv("PRISMA_BOT_TOKEN_COREWORK", "tok-v1")
    # Esta máquina puede tener un PRISMA_BOT_TOKEN_ADMIN real en `.env`: sin
    # sacarlo, el ciclo construiría un segundo transporte (el de admin) y el
    # conteo de abajo, que es sobre el total, no sobre "corework" en
    # particular, no sería determinístico.
    monkeypatch.delenv("PRISMA_BOT_TOKEN_ADMIN", raising=False)

    c = ciclo.Ciclo(lambda: conn, arranque=datetime(2026, 1, 1, tzinfo=timezone.utc))
    ahora = datetime(2026, 1, 2, tzinfo=timezone.utc)
    c.tick(ahora=ahora)

    assert len(creados) == 1
    primero = creados[0]
    assert not primero.cerrado

    monkeypatch.setenv("PRISMA_BOT_TOKEN_COREWORK", "tok-v2")
    c.tick(ahora=ahora)

    assert len(creados) == 2       # se construyó uno nuevo
    assert primero.cerrado         # y se cerró el viejo
