from __future__ import annotations

import threading
from datetime import datetime, timezone
from uuid import uuid4

import psycopg
import pytest

from leda import herramientas as H
from leda import pendientes as P
from leda.autoridad import Canal, Denegado, identificar
from leda.calendario import Calendario
from leda.db import admin, autoridad, espacio
from leda.despachador import TransporteDePrueba, despachar


AHORA = datetime(2026, 8, 12, 15, 0, tzinfo=timezone.utc)


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s",
                (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _objetivo(cur, ws):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo, estado)
           values (%s, 'operativo', 'Objetivo simulado', 'activo') returning id""",
        (ws,))
    return str(cur.fetchone()["id"])


def _args(objetivo, **cambios):
    base = {
        "titulo": "Relevar tablero simulado",
        "objetivo_id": objetivo,
        "area_slug": "ot",
        "responsable": "Nahuel Gimenez",
        "fecha_objetivo": "2026-08-20",
        "criterio_aceptacion": "Plano revisado contra el tablero simulado",
    }
    base.update(cambios)
    return base


def _crear_preview(cur, ws, **cambios):
    quien = _quien(cur, "Nahuel Gimenez", ws)
    objetivo = cambios.pop("objetivo_id", None) or _objetivo(cur, ws)
    return H.crear_borrador_tarea(cur, quien, **_args(objetivo, **cambios))


def _token(cur, pending_id):
    return P.opcion_por_etiqueta(cur, pending_id, "Confirmar").token


def _app_user(cur, nombre):
    cur.execute("select app_user_id from integrante where nombre = %s", (nombre,))
    return str(cur.fetchone()["app_user_id"])


def _telegram(cur, nombre):
    cur.execute("select telegram_user_id from integrante where nombre = %s",
                (nombre,))
    return cur.fetchone()["telegram_user_id"]


def _confirmar(authority_conn, ws, token, telegram_user_id):
    with autoridad(authority_conn) as cur:
        resultado = P.resolver_borrador(
            cur, ws, token, telegram_user_id, telegram_user_id)
    return resultado


@pytest.mark.parametrize("faltante", [
    "objetivo_id", "responsable", "fecha_objetivo", "criterio_aceptacion",
])
def test_cada_dato_faltante_deja_solo_un_borrador(corework, conn, faltante):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        args = _args(_objetivo(cur, ws))
        args.pop(faltante)

        resultado = H.crear_borrador_tarea(cur, quien, **args)

        assert resultado["completa"] is False
        assert faltante in resultado["faltantes"]
        cur.execute("select count(*) n from task")
        assert cur.fetchone()["n"] == 0
        cur.execute("select count(*) n from task_draft")
        assert cur.fetchone()["n"] == 1


def test_politica_no_resuelta_deja_borrador_sin_preview(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        cur.execute("delete from task_evidence_policy where workspace_id = %s", (ws,))
    with espacio(conn, ws) as cur:
        resultado = _crear_preview(cur, ws)

        assert resultado["completa"] is False
        assert "politica_evidencia" in resultado["faltantes"]
        cur.execute("select evidencia_requerida from task_draft")
        assert cur.fetchone()["evidencia_requerida"] is None
        cur.execute("select count(*) n from pending_action where draft_id is not null")
        assert cur.fetchone()["n"] == 0


def test_politica_explicita_sin_evidencia_permite_preview(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        cur.execute(
            """update task_evidence_policy set evidencia_requerida = '{}'
                where workspace_id = %s and area_id =
                      (select id from area where workspace_id = %s and slug = 'ot')""",
            (ws, ws))
    with espacio(conn, ws) as cur:
        resultado = _crear_preview(cur, ws)
        assert resultado["completa"] is True
        cur.execute("select evidencia_requerida from task_draft where id = %s",
                    (resultado["draft_id"],))
        assert cur.fetchone()["evidencia_requerida"] == []


def test_borradores_tienen_rls_forzado(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        resultado = _crear_preview(cur, ws, responsable=None)
    with espacio(conn, str(uuid4())) as cur:
        cur.execute("select count(*) n from task_draft where id = %s",
                    (resultado["draft_id"],))
        assert cur.fetchone()["n"] == 0
    with admin(conn) as cur:
        cur.execute(
            """select relrowsecurity, relforcerowsecurity
                 from pg_class where oid = 'leda.task_draft'::regclass""")
        assert tuple(cur.fetchone().values()) == (True, True)


def test_preview_es_privada_para_aprobador_y_no_crea_tarea(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        resultado = _crear_preview(cur, ws)

        assert resultado["completa"] is True
        assert resultado["pendiente_revision"] is True
        cur.execute("select count(*) n from task")
        assert cur.fetchone()["n"] == 0
        cur.execute(
            """select p.draft_id, p.draft_version, p.preview,
                      destinatario.nombre, p.chat_id
                 from pending_action p
                 join integrante destinatario on destinatario.membership_id = p.membership_id
                where p.id = %s""", (resultado["pending_action_id"],))
        preview = cur.fetchone()
        assert preview["nombre"] == "Marcos Tarquini"
        assert preview["draft_id"]
        assert preview["draft_version"] == 1
        assert preview["preview"]["criterio_aceptacion"]
        cur.execute("select telegram_user_id from integrante where nombre = 'Marcos Tarquini'")
        assert preview["chat_id"] == cur.fetchone()["telegram_user_id"]
        cur.execute(
            "select count(*) n from message_outbox where pending_action_id = %s",
            (resultado["pending_action_id"],))
        assert cur.fetchone()["n"] == 1


def test_responsable_raiz_solo_puede_ser_confirmado_por_autoridad_final(
        corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        resultado = H.crear_borrador_tarea(cur, quien, **_args(
            _objetivo(cur, ws), responsable="Ismael Soschinski",
            area_slug="direccion"))

        cur.execute(
            """select i.nombre
                 from pending_action p
                 join integrante i on i.membership_id = p.membership_id
                where p.id = %s""", (resultado["pending_action_id"],))
        assert cur.fetchone()["nombre"] == "Ismael Soschinski"


def test_integrante_no_puede_proponer_trabajo_ajeno(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        with pytest.raises(Denegado):
            H.crear_borrador_tarea(cur, quien, **_args(
                _objetivo(cur, ws), responsable="Lucas Natuche",
                area_slug="it"))
        cur.execute("select count(*) n from task_draft")
        assert cur.fetchone()["n"] == 0


def test_actor_no_autorizado_no_consume_preview_ni_crea_tarea(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        resultado = _crear_preview(cur, ws)
        token = _token(cur, resultado["pending_action_id"])

        with pytest.raises(Denegado):
            P.resolver(cur, token,
                       app_user_id=_app_user(cur, "Nahuel Gimenez"), ahora=AHORA)

        cur.execute("select estado from pending_action where id = %s",
                    (resultado["pending_action_id"],))
        assert cur.fetchone()["estado"] == "esperando"
        cur.execute("select count(*) n from task")
        assert cur.fetchone()["n"] == 0


@pytest.mark.parametrize("obsolescencia", [
    "responsable", "objetivo", "politica", "version", "autoridad",
])
def test_preview_obsoleta_no_crea_tarea(corework, conn, authority_conn,
                                        obsolescencia):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        resultado = _crear_preview(cur, ws)
        token = _token(cur, resultado["pending_action_id"])
        if obsolescencia == "responsable":
            cur.execute(
                """update membership set activo = false
                    where id = (select membership_id from integrante
                                  where nombre = 'Nahuel Gimenez')""")
        elif obsolescencia == "objetivo":
            cur.execute(
                """update objective set titulo = 'Objetivo cambiado'
                    where id = (select objective_id from task_draft
                                  where id = %s)""", (resultado["draft_id"],))
        elif obsolescencia == "politica":
            cur.execute("set local role leda_admin")
            cur.execute(
                """update task_evidence_policy
                      set evidencia_requerida = array['explicacion'],
                          version = version + 1
                    where workspace_id = %s and area_id =
                          (select area_id from task_draft where id = %s)""",
                (ws, resultado["draft_id"]))
            cur.execute("set local role leda_app")
        elif obsolescencia == "version":
            cur.execute("set local role leda_admin")
            cur.execute("update task_draft set version = version + 1 where id = %s",
                        (resultado["draft_id"],))
            cur.execute("set local role leda_app")
        else:
            cur.execute(
                """update membership
                      set aprobador_membership_id =
                          (select membership_id from integrante
                            where nombre = 'Ismael Soschinski')
                    where id = (select responsable_membership_id from task_draft
                                  where id = %s)""", (resultado["draft_id"],))

        telegram = _telegram(cur, "Marcos Tarquini")
    assert _confirmar(authority_conn, ws, token, telegram) is None
    with espacio(conn, ws) as cur:
        cur.execute("select count(*) n from task")
        assert cur.fetchone()["n"] == 0


def test_confirmar_materializa_una_tarea_completa_y_auditable(
        corework, conn, authority_conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        resultado = _crear_preview(cur, ws)
        token = _token(cur, resultado["pending_action_id"])

        telegram = _telegram(cur, "Marcos Tarquini")
    resuelta = _confirmar(authority_conn, ws, token, telegram)

    with espacio(conn, ws) as cur:
        assert resuelta is not None and resuelta.task_id
        cur.execute(
            """select source_draft_id, objective_id, responsable_membership_id,
                      fecha_objetivo, criterio_aceptacion, evidencia_requerida, estado
                 from task where id = %s""", (resuelta.task_id,))
        tarea = cur.fetchone()
        assert str(tarea["source_draft_id"]) == resultado["draft_id"]
        assert tarea["objective_id"] and tarea["responsable_membership_id"]
        assert tarea["fecha_objetivo"] and tarea["criterio_aceptacion"]
        assert tarea["evidencia_requerida"]
        assert tarea["estado"] == "asignada"
        cur.execute("select converted_task_id from task_draft where id = %s",
                    (resultado["draft_id"],))
        assert str(cur.fetchone()["converted_task_id"]) == resuelta.task_id
        actor = _app_user(cur, "Marcos Tarquini")
    with admin(conn) as cur:
        cur.execute(
            """select actor_kind, actor_app_user_id, detalle
                 from audit_log
                where accion = 'confirmar_borrador_tarea' and sujeto_id = %s""",
            (resuelta.task_id,))
        audit = cur.fetchone()
        assert audit["actor_kind"] == "persona"
        assert str(audit["actor_app_user_id"]) == actor
        assert audit["detalle"]["draft_id"] == resultado["draft_id"]
        assert audit["detalle"]["pending_action_id"] == resultado["pending_action_id"]


def test_doble_confirmacion_secuencial_crea_una_sola_tarea(
        corework, conn, authority_conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        resultado = _crear_preview(cur, ws)
        token = _token(cur, resultado["pending_action_id"])
        telegram = _telegram(cur, "Marcos Tarquini")

    first = _confirmar(authority_conn, ws, token, telegram)
    replay = _confirmar(authority_conn, ws, token, telegram)
    assert first is not None
    assert replay is not None and replay.replay and replay.task_id == first.task_id
    with espacio(conn, ws) as cur:
        cur.execute("select count(*) n from task where source_draft_id = %s",
                    (resultado["draft_id"],))
        assert cur.fetchone()["n"] == 1


def test_doble_confirmacion_concurrente_crea_una_sola_tarea(
        corework, conn, authority_uri):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        resultado = _crear_preview(cur, ws)
        token = _token(cur, resultado["pending_action_id"])
        telegram = _telegram(cur, "Marcos Tarquini")
    conn.commit()

    barrera = threading.Barrier(2)
    resultados = []

    def confirmar():
        from leda.db import conectar_autoridad

        otra = conectar_autoridad(authority_uri)
        try:
            with autoridad(otra) as cur:
                barrera.wait()
                resultados.append(P.resolver_borrador(
                    cur, ws, token, telegram, telegram))
        finally:
            otra.close()

    hilos = [threading.Thread(target=confirmar) for _ in range(2)]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()

    assert len(resultados) == 2
    assert sum(not r.replay for r in resultados) == 1
    assert sum(r.replay for r in resultados) == 1
    with admin(conn) as cur:
        cur.execute("select count(*) n from task where source_draft_id = %s",
                    (resultado["draft_id"],))
        assert cur.fetchone()["n"] == 1


def test_fallo_posterior_al_insert_revierte_toda_la_conversion(
        corework, conn, authority_conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        resultado = _crear_preview(cur, ws)
        token = _token(cur, resultado["pending_action_id"])
        telegram = _telegram(cur, "Marcos Tarquini")
    conn.commit()

    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("reset role")
            cur.execute("set search_path = leda, public")
            cur.execute(
                """create function fallar_auditoria_borrador() returns trigger
                   language plpgsql as $$ begin
                     if new.accion = 'confirmar_borrador_tarea' then
                       raise exception 'fallo simulado';
                     end if;
                     return new;
                   end $$""")
            cur.execute(
                """create trigger trg_fallar_auditoria_borrador
                   before insert on audit_log for each row
                   execute function fallar_auditoria_borrador()""")
    conn.commit()

    try:
        with pytest.raises(psycopg.errors.RaiseException):
            with autoridad(authority_conn) as cur:
                P.resolver_borrador(cur, ws, token, telegram, telegram)
    finally:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("reset role")
                cur.execute("set search_path = leda, public")
                cur.execute("drop trigger if exists trg_fallar_auditoria_borrador on audit_log")
                cur.execute("drop function if exists fallar_auditoria_borrador()")
        conn.commit()

    with admin(conn) as cur:
        cur.execute("select count(*) n from task where source_draft_id = %s",
                    (resultado["draft_id"],))
        assert cur.fetchone()["n"] == 0
        cur.execute("select estado from pending_action where id = %s",
                    (resultado["pending_action_id"],))
        assert cur.fetchone()["estado"] == "esperando"
        cur.execute("select converted_task_id from task_draft where id = %s",
                    (resultado["draft_id"],))
        assert cur.fetchone()["converted_task_id"] is None


@pytest.mark.parametrize("campo", [
    "responsable_membership_id", "fecha_objetivo", "criterio_aceptacion",
    "evidencia_requerida", "source_draft_id",
])
def test_leda_app_no_puede_mutar_campos_de_compromiso(
        corework, conn, authority_conn, campo):
    from psycopg.sql import SQL, Identifier

    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        resultado = _crear_preview(cur, ws)
        token = _token(cur, resultado["pending_action_id"])
        telegram = _telegram(cur, "Marcos Tarquini")
    conn.commit()
    resuelta = _confirmar(authority_conn, ws, token, telegram)

    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        with espacio(conn, ws) as cur:
            cur.execute(
                SQL("update task set {} = null where id = %s").format(
                    Identifier(campo)),
                (resuelta.task_id,))


def test_leda_app_no_puede_borrar_task_y_evento_autorizado_sigue_operando(
        corework, conn, authority_conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        resultado = _crear_preview(cur, ws)
        token = _token(cur, resultado["pending_action_id"])
        telegram = _telegram(cur, "Marcos Tarquini")
    conn.commit()
    resuelta = _confirmar(authority_conn, ws, token, telegram)

    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        with espacio(conn, ws) as cur:
            cur.execute("delete from task where id = %s", (resuelta.task_id,))

    with espacio(conn, ws) as cur:
        # El responsable de la tarea es Nahuel Gimenez (`_args`, default de
        # `_crear_preview`); Marcos sólo confirmó el borrador. Con el
        # chequeo de autoridad de T2b (`herramientas._preparar_actualizar_
        # estado`), sólo el responsable puede mover el estado -- se usa acá
        # para seguir probando lo que este test verifica de verdad: que la
        # operación autorizada sigue funcionando después del intento
        # rechazado de arriba, no que Marcos tenga algo que ver con la tarea.
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        assert H.ejecutar(cur, nahuel, "actualizar_estado", {
            "tarea_id": resuelta.task_id, "estado": "en_curso",
        }, ya_confirmada=True)["estado"] == "en_curso"
        cur.execute("select estado from task where id = %s", (resuelta.task_id,))
        assert cur.fetchone()["estado"] == "en_curso"


def test_trigger_defensivo_bloquea_mutacion_administrativa(
        corework, conn, authority_conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        resultado = _crear_preview(cur, ws)
        token = _token(cur, resultado["pending_action_id"])
        telegram = _telegram(cur, "Marcos Tarquini")
    conn.commit()
    resuelta = _confirmar(authority_conn, ws, token, telegram)

    with pytest.raises(psycopg.errors.RaiseException):
        with admin(conn) as cur:
            cur.execute("update task set criterio_aceptacion = null where id = %s",
                        (resuelta.task_id,))


def test_leda_app_no_puede_ejecutar_compromiso_ni_usar_overload_anterior(
        corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        resultado = _crear_preview(cur, ws)
        token = _token(cur, resultado["pending_action_id"])
        telegram = _telegram(cur, "Marcos Tarquini")
        cur.execute(
            """select has_function_privilege(
                 current_user,
                 'leda.confirmar_borrador_tarea(uuid,text,bigint,bigint)',
                 'EXECUTE') as puede""")
        assert cur.fetchone()["puede"] is False

    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        with espacio(conn, ws) as cur:
            cur.execute("select * from confirmar_borrador_tarea(%s, %s, %s, %s)",
                        (ws, token, telegram, telegram))

    with espacio(conn, ws) as cur:
        cur.execute(
            """select to_regprocedure(
                 'leda.confirmar_borrador_tarea(text,uuid,timestamptz)') as fn""")
        assert cur.fetchone()["fn"] is None


def test_compromiso_usa_actor_y_reloj_confiables(
        corework, conn, authority_conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        resultado = _crear_preview(cur, ws)
        token = _token(cur, resultado["pending_action_id"])
        nahuel = _telegram(cur, "Nahuel Gimenez")
        marcos = _telegram(cur, "Marcos Tarquini")
    conn.commit()

    with pytest.raises(Denegado):
        _confirmar(authority_conn, ws, token, nahuel)
    with admin(conn) as cur:
        cur.execute("update pending_action set vence_en = clock_timestamp() - interval '1 second' "
                    "where id = %s", (resultado["pending_action_id"],))

    assert _confirmar(authority_conn, ws, token, marcos) is None
    with admin(conn) as cur:
        cur.execute("select count(*) n from task")
        assert cur.fetchone()["n"] == 0


def test_preview_congelada_debe_coincidir_con_tarea_comprometida(
        corework, conn, authority_conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        resultado = _crear_preview(cur, ws)
        token = _token(cur, resultado["pending_action_id"])
        telegram = _telegram(cur, "Marcos Tarquini")
    with admin(conn) as cur:
        cur.execute(
            """update pending_action
                  set preview = jsonb_set(preview, '{titulo}', '"alterado"')
                where id = %s""", (resultado["pending_action_id"],))

    assert _confirmar(authority_conn, ws, token, telegram) is None
    with admin(conn) as cur:
        cur.execute("select count(*) n from task")
        assert cur.fetchone()["n"] == 0


@pytest.mark.parametrize("obsolescencia", [
    "cambio_aprobador", "aprobador_inactivo", "vencida",
])
def test_dispatch_descarta_preview_obsoleta_sin_entregar(
        corework, conn, obsolescencia):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        resultado = _crear_preview(cur, ws)
    with admin(conn) as cur:
        if obsolescencia == "cambio_aprobador":
            cur.execute(
                """update membership set aprobador_membership_id =
                     (select m.id from membership m join app_user u
                       on u.id = m.app_user_id
                      where m.workspace_id = %s and u.nombre = 'Ismael Soschinski')
                    where id = (select responsable_membership_id from task_draft
                                  where id = %s)""", (ws, resultado["draft_id"]))
        elif obsolescencia == "aprobador_inactivo":
            cur.execute(
                """update membership set activo = false
                    where id = (select membership_id from pending_action where id = %s)""",
                (resultado["pending_action_id"],))
        else:
            cur.execute(
                "update pending_action set vence_en = clock_timestamp() - interval '1 second' "
                "where id = %s", (resultado["pending_action_id"],))

    with espacio(conn, ws) as cur:
        transporte = TransporteDePrueba()
        cal = Calendario.desde_base(cur, ws)
        resumen = despachar(cur, ws, transporte, cal,
                            datetime.now(timezone.utc))
        assert transporte.enviados == []
        assert resumen["descartados"] == 1
        cur.execute("select estado from pending_action where id = %s",
                    (resultado["pending_action_id"],))
        assert cur.fetchone()["estado"] == "vencida"
        cur.execute("select estado from message_outbox where pending_action_id = %s",
                    (resultado["pending_action_id"],))
        assert cur.fetchone()["estado"] == "descartado"


# Antes en `tests/test_task_intake.py`, que se retiró con el alta guiada (E3-4): la
# herramienta vieja de crear tareas sigue oculta para la IA y cerrada en el servidor.
def _actor(cur, world, workspace_slug="north-lab", person="Taylor Quinn"):
    item = world[workspace_slug]
    tg = item["people"][person]["telegram"]
    return identificar(cur, tg, Canal.ESPACIO, item["id"])


def test_legacy_create_task_is_hidden_and_fails_closed(intake_world, conn):
    assert "crear_tarea" not in {tool["name"] for tool in H.esquemas()}
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor = _actor(cur, intake_world)
        with pytest.raises(Denegado):
            H.ejecutar(cur, actor, "crear_tarea", {"titulo": "hidden"})
