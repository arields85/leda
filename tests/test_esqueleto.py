"""Pruebas del esqueleto: importación, calendario, despacho y autoridad.

La escalera y la cadencia viejas de `leda` (`escalera.py`, `reloj.py`) se retiraron con sus
pruebas en la E3-7: la escalera es la del motor (`tests/motor/test_escalera.py`) y las
cadencias vuelven después de M3."""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

import pytest

from leda.autoridad import Canal, Denegado, identificar, verificar
from leda.incidentes import ETAPA_ENTREGA_REINTENTO
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.despachador import TransporteDePrueba, despachar
from leda.importador import PackInvalido, importar
from leda.salida import enqueue_outbox

BA = ZoneInfo("America/Argentina/Buenos_Aires")


# ---------------------------------------------------------------------------
# Importación
# ---------------------------------------------------------------------------

def test_importa_corework(corework, conn):
    assert corework.slug == "corework"
    assert corework.activo
    with conn.cursor() as cur:
        cur.execute("set role leda_admin")
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
    # Sin grupo Leda no tiene dónde publicar: eso sí bloquea.
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

def _seguimiento(cur, ws, ahora) -> None:
    """Un mensaje que Leda manda por su cuenta a Marcos, en la cola. Antes lo armaba la
    cadencia vieja (`reloj.ejecutar_cadencia`, retirada en la E3-7); lo que se prueba acá es el
    despacho, no quién lo encola."""
    cur.execute("""select membership_id, telegram_user_id from integrante
                    where workspace_id = %s and nombre = 'Marcos Tarquini'""", (ws,))
    marcos = cur.fetchone()
    enqueue_outbox(cur, workspace_id=ws, chat_id=marcos["telegram_user_id"],
                   text="Tus tareas abiertas: Programar PLC.", message_type="seguimiento",
                   recipient_membership_id=str(marcos["membership_id"]),
                   scheduled_for=ahora, dedupe_key=f"{ws}:seguimiento:prueba")



# ---------------------------------------------------------------------------
# Despacho
# ---------------------------------------------------------------------------

def test_no_escribe_fuera_de_horario(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        lunes = datetime(2026, 7, 27, 9, 15, tzinfo=BA)
        _seguimiento(cur, ws, lunes)

        transporte = TransporteDePrueba()
        sabado = datetime(2026, 8, 1, 11, 0, tzinfo=BA)
        r = despachar(cur, ws, transporte, cal, sabado)
        assert r["enviados"] == 0 and r["pospuestos"] == 1
        assert transporte.enviados == []


def test_reintenta_y_abre_incidente(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        lunes = datetime(2026, 7, 27, 9, 15, tzinfo=BA)
        _seguimiento(cur, ws, lunes)

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
        cur.execute("select count(*) n from incident where workspace_id = %s"
                    " and etapa is distinct from %s", (ws, ETAPA_ENTREGA_REINTENTO))
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


def test_ismael_no_puede_configurar_leda(corework, conn):
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

    La regla de no molestar fuera de hora es para lo que Leda inicia; dejar
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
