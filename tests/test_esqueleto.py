"""Pruebas del esqueleto: importación, calendario, escalera, cadencia,
despacho y autoridad."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from prisma import escalera, reloj
from prisma.autoridad import Canal, Denegado, identificar, verificar
from prisma.calendario import Calendario, cargar_feriados_ar
from prisma.db import admin, espacio
from prisma.despachador import TransporteDePrueba, despachar
from prisma.importador import PackInvalido, importar

BA = ZoneInfo("America/Argentina/Buenos_Aires")


# ---------------------------------------------------------------------------
# Importación
# ---------------------------------------------------------------------------

def test_importa_corework(corework, conn):
    assert corework.slug == "corework"
    assert corework.activo
    with conn.cursor() as cur:
        cur.execute("set role prisma_admin")
        cur.execute("select count(*) n from membership")
        assert cur.fetchone()["n"] == 7
        cur.execute("select count(*) n from cadence_job")
        assert cur.fetchone()["n"] == 5
        cur.execute("select cron from cadence_job where nombre = 'objetivos_semanales'")
        assert cur.fetchone()["cron"] == "15 9 * * 1"


def test_no_activa_con_pendientes(conn, tmp_path):
    import yaml
    from tests.conftest import RAIZ

    pack = yaml.safe_load((RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    # Sin grupo Prisma no tiene dónde publicar: eso sí bloquea.
    pack["telegram"]["grupo_gestion_id"] = "PENDIENTE"
    # Los identificadores de Telegram, en cambio, llegan por activación.
    for p in pack["personas"]:
        p["telegram_user_id"] = "PENDIENTE"

    ruta = tmp_path / "p.yaml"
    ruta.write_text(yaml.safe_dump(pack, allow_unicode=True), "utf-8")
    with pytest.raises(PackInvalido) as e:
        importar(conn, ruta, activar=True)
    assert any("grupo de gestión" in p for p in e.value.problemas)
    assert not any("telegram_user_id" in p for p in e.value.problemas)


def test_rechaza_pack_que_toca_el_nucleo(conn, tmp_path):
    import yaml
    from tests.conftest import RAIZ

    pack = yaml.safe_load((RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    pack["desactivar_auditoria"] = True
    ruta = tmp_path / "p.yaml"
    ruta.write_text(yaml.safe_dump(pack, allow_unicode=True), "utf-8")
    with pytest.raises(PackInvalido) as e:
        importar(conn, ruta, activar=True)
    assert any("núcleo" in p for p in e.value.problemas)


# ---------------------------------------------------------------------------
# Calendario
# ---------------------------------------------------------------------------

def _cal():
    return Calendario(
        dias=frozenset({0, 1, 2, 3, 4}),
        hora_inicio=time(9, 0), hora_fin=time(17, 0),
        feriados=frozenset({date(2026, 7, 9)}), zona=BA)


def test_viernes_mas_un_habil_es_lunes():
    cal = _cal()
    viernes = datetime(2026, 7, 24, 11, 0, tzinfo=BA)
    assert cal.sumar_habiles(viernes, 1).date() == date(2026, 7, 27)


def test_salta_feriado():
    cal = _cal()
    miercoles = datetime(2026, 7, 8, 11, 0, tzinfo=BA)   # 9/7 es feriado
    assert cal.sumar_habiles(miercoles, 1).date() == date(2026, 7, 10)


def test_fuera_de_horario_se_corre_al_proximo_habil():
    cal = _cal()
    sabado = datetime(2026, 7, 25, 10, 0, tzinfo=BA)
    assert cal.dentro_de_jornada(sabado) == datetime(2026, 7, 27, 9, 0, tzinfo=BA)
    tarde = datetime(2026, 7, 24, 22, 0, tzinfo=BA)
    assert cal.dentro_de_jornada(tarde) == datetime(2026, 7, 27, 9, 0, tzinfo=BA)


# ---------------------------------------------------------------------------
# Utilidades para armar trabajo
# ---------------------------------------------------------------------------

def _tarea(cur, ws, *, area="ot", persona="Marcos Tarquini", vence=None):
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
        "values (%s, 'asignada', 'prisma')", (t,))
    return t


# ---------------------------------------------------------------------------
# Escalera
# ---------------------------------------------------------------------------

def test_escalera_avanza_por_dias_habiles(corework, conn):
    ws = corework.workspace_id
    vence = datetime(2026, 7, 24, 17, 0, tzinfo=BA)          # viernes
    with admin(conn) as cur:
        cargar_feriados_ar(cur, ws)
        _tarea(cur, ws, vence=vence)

    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)

        # jueves: todavía falta un día hábil -> aviso
        a = escalera.evaluar(cur, ws, cal, datetime(2026, 7, 23, 10, 0, tzinfo=BA))
        assert [x.paso for x in a] == ["aviso"]

        # el mismo viernes -> primer recordatorio
        a = escalera.evaluar(cur, ws, cal, datetime(2026, 7, 24, 10, 0, tzinfo=BA))
        assert [x.paso for x in a] == ["recordar1"]

        # sábado y domingo no cuentan: sigue en el primer recordatorio
        a = escalera.evaluar(cur, ws, cal, datetime(2026, 7, 26, 10, 0, tzinfo=BA))
        assert [x.paso for x in a] == ["recordar1"]

        # lunes -> segundo
        a = escalera.evaluar(cur, ws, cal, datetime(2026, 7, 27, 10, 0, tzinfo=BA))
        assert [x.paso for x in a] == ["recordar2"]

        # miércoles -> escala
        a = escalera.evaluar(cur, ws, cal, datetime(2026, 7, 29, 10, 0, tzinfo=BA))
        assert [x.paso for x in a] == ["escalar"]
        assert a[0].escalamiento


def test_ausente_no_recibe_ni_avanza(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 7, 24, 17, 0, tzinfo=BA))
        cur.execute(
            """insert into absence (membership_id, desde, hasta)
               select m.id, '2026-07-20', '2026-07-31'
                 from membership m join app_user u on u.id = m.app_user_id
                where u.nombre = 'Marcos Tarquini'""")

    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        a = escalera.evaluar(cur, ws, cal, datetime(2026, 7, 27, 10, 0, tzinfo=BA))
        assert a == []


def test_tarea_bloqueada_sale_de_la_escalera(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        t = _tarea(cur, ws, vence=datetime(2026, 7, 24, 17, 0, tzinfo=BA))
        cur.execute(
            "insert into blocker (workspace_id, task_id, causa) values (%s, %s, %s)",
            (ws, t, "falta el switch en sala"))

    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        a = escalera.evaluar(cur, ws, cal, datetime(2026, 7, 27, 10, 0, tzinfo=BA))
        assert a == []


def test_escalera_no_duplica_al_reintentar(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 7, 24, 17, 0, tzinfo=BA))

    ahora = datetime(2026, 7, 27, 10, 0, tzinfo=BA)
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        a = escalera.evaluar(cur, ws, cal, ahora)
        assert escalera.encolar(cur, ws, a, cal, ahora) == 1
        # el proceso reinicia y vuelve a evaluar el mismo momento
        a = escalera.evaluar(cur, ws, cal, ahora)
        assert escalera.encolar(cur, ws, a, cal, ahora) == 0


# ---------------------------------------------------------------------------
# Cadencia y despacho
# ---------------------------------------------------------------------------

def test_cadencia_encola_y_despacha(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 8, 14, 17, 0, tzinfo=BA))

    lunes = datetime(2026, 7, 27, 9, 15, tzinfo=BA)
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        n = reloj.ejecutar_cadencia(cur, ws, "objetivos_semanales", cal, lunes)
        assert n == 1                      # sólo Marcos tiene tarea abierta

        transporte = TransporteDePrueba()
        r = despachar(cur, ws, transporte, cal, lunes)
        assert r["enviados"] == 1
        assert "Programar PLC" in transporte.enviados[0][1]


def test_cadencia_no_duplica_en_la_misma_semana(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 8, 14, 17, 0, tzinfo=BA))

    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        lunes = datetime(2026, 7, 27, 9, 15, tzinfo=BA)
        assert reloj.ejecutar_cadencia(cur, ws, "objetivos_semanales", cal, lunes) == 1
        # reinicio un minuto después
        assert reloj.ejecutar_cadencia(cur, ws, "objetivos_semanales", cal,
                                       lunes + timedelta(minutes=1)) == 0


def test_no_escribe_fuera_de_horario(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 8, 14, 17, 0, tzinfo=BA))

    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        lunes = datetime(2026, 7, 27, 9, 15, tzinfo=BA)
        reloj.ejecutar_cadencia(cur, ws, "objetivos_semanales", cal, lunes)

        transporte = TransporteDePrueba()
        sabado = datetime(2026, 8, 1, 11, 0, tzinfo=BA)
        r = despachar(cur, ws, transporte, cal, sabado)
        assert r["enviados"] == 0 and r["pospuestos"] == 1
        assert transporte.enviados == []


def test_reintenta_y_abre_incidente(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, vence=datetime(2026, 8, 14, 17, 0, tzinfo=BA))

    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        lunes = datetime(2026, 7, 27, 9, 15, tzinfo=BA)
        reloj.ejecutar_cadencia(cur, ws, "objetivos_semanales", cal, lunes)

        cur.execute("select chat_id from message_outbox limit 1")
        chat = cur.fetchone()["chat_id"]
        transporte = TransporteDePrueba(falla_en={chat})

        for _ in range(5):
            despachar(cur, ws, transporte, cal, lunes)

        cur.execute("select estado, intentos from message_outbox limit 1")
        fila = cur.fetchone()
        assert fila["estado"] == "fallido"
        assert fila["intentos"] == 5

    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 1


# ---------------------------------------------------------------------------
# Autoridad
# ---------------------------------------------------------------------------

def test_ariel_en_el_bot_del_equipo_no_es_administrador(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        cur.execute("select id from app_user where nombre = 'Ariel De Simone'")
        ariel = cur.fetchone()["id"]
        cur.execute(
            "insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
            (ariel,))
        cur.execute("select telegram_user_id t from app_user where id = %s", (ariel,))
        tg = cur.fetchone()["t"]

        # Por el bot de CoreWork es referente de CoreLabs y nada más.
        quien = identificar(cur, tg, Canal.ESPACIO, ws)
        assert quien.rol_slug == "referente"
        with pytest.raises(Denegado, match="consola de administración"):
            verificar(cur, quien, "cambiar_modelo")

        # Por el bot de administración sí.
        quien = identificar(cur, tg, Canal.ADMINISTRACION, None)
        verificar(cur, quien, "cambiar_modelo")


def test_ismael_no_puede_configurar_prisma(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        cur.execute("select telegram_user_id t from app_user where nombre = 'Ismael Soschinski'")
        tg = cur.fetchone()["t"]

        quien = identificar(cur, tg, Canal.ESPACIO, ws)
        assert quien.autoridad_final
        verificar(cur, quien, "definir_prioridad_general")      # sí puede

        with pytest.raises(Denegado):
            verificar(cur, quien, "editar_configuracion")       # no puede

        with pytest.raises(Denegado, match="No sos administrador"):
            identificar(cur, tg, Canal.ADMINISTRACION, None)


def test_integrante_no_define_prioridades(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        cur.execute("select telegram_user_id t from app_user where nombre = 'Nahuel Gimenez'")
        tg = cur.fetchone()["t"]
        quien = identificar(cur, tg, Canal.ESPACIO, ws)
        verificar(cur, quien, "crear_tarea")
        with pytest.raises(Denegado):
            verificar(cur, quien, "declarar_urgencia")


def test_prohibiciones_absolutas(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        cur.execute("select telegram_user_id t from app_user where nombre = 'Ismael Soschinski'")
        quien = identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)
        for accion in ("modificar_plc", "cambiar_produccion", "ampliar_autoridad_propia"):
            with pytest.raises(Denegado):
                verificar(cur, quien, accion)


def test_una_respuesta_sale_fuera_de_horario(corework, conn):
    """Contestarle a quien escribió no es "escribir fuera de horario".

    La regla de no molestar fuera de hora es para lo que Prisma inicia; dejar
    a alguien esperando hasta mañana porque son las 17:05 es peor.
    """
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        tarde = datetime(2026, 7, 27, 20, 30, tzinfo=BA)

        # `programado_para` va explícito: su valor por defecto es now(), o sea
        # la fecha real de hoy, y el despachador sólo levanta lo que ya está en
        # hora (`programado_para <= ahora`). Sin esto, la prueba pasa el día que
        # se escribe y falla al siguiente, cuando el reloj deja atrás a `tarde`.
        cur.execute(
            """insert into message_outbox
                 (workspace_id, chat_id, cuerpo, estado, dedupe_key,
                  es_respuesta, programado_para)
               values (%s, 500, 'te contesto', 'listo', 'r1', true, %s)""",
            (ws, tarde))
        cur.execute(
            """insert into message_outbox
                 (workspace_id, chat_id, cuerpo, estado, dedupe_key,
                  es_respuesta, programado_para)
               values (%s, 500, 'recordatorio', 'listo', 'r2', false, %s)""",
            (ws, tarde))

        transporte = TransporteDePrueba()
        r = despachar(cur, ws, transporte, cal, tarde)

        assert r["enviados"] == 1 and r["pospuestos"] == 1
        assert transporte.enviados[0][1] == "te contesto"


def test_el_pack_crea_el_objetivo_raiz(corework, conn):
    """Sin objetivo no se puede cargar ninguna tarea: el núcleo no admite
    trabajo suelto. El pack tiene que dejar el árbol arrancado."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        cur.execute("select tipo, titulo, parent_id from objective order by tipo")
        objs = cur.fetchall()

    raices = [o for o in objs if o["tipo"] == "estrategico"]
    assert len(raices) == 1
    assert "Steigen" in raices[0]["titulo"]
    # Los frentes del pack cuelgan de la raíz.
    operativos = [o for o in objs if o["tipo"] == "operativo"]
    assert len(operativos) == 5
    assert all(o["parent_id"] is not None for o in operativos)
