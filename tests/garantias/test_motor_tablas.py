"""Las tablas del motor de conversación para la prueba chica (E2-1, migraciones 0030 y 0031).

`odd/tasks/prueba-chica-del-motor.md`, sección 5, y ADR 0018, decisiones 3, 8 y 9. Lo que se
prueba acá es la capa de garantías de esas tablas, no la conversación: aislamiento entre espacios
(RLS forzado, referencias del mismo espacio), lo que sólo se agrega, el "exactamente uno" de quién
destraba, el token único de una opción, el espacio de una previsión derivado de su tarea, el
mínimo del aviso previo y la ejecución única de un mensaje de Telegram repetido.
"""

from __future__ import annotations

import dataclasses
import json
from datetime import date, datetime, timedelta, timezone

import psycopg
import pytest

from leda.db import admin, espacio


NUEVAS = ("conversation_state", "conversation_turn", "conversation_question",
          "conversation_option", "task_forecast", "blocker_unblocker",
          "scheduled_notice")
SOLO_SE_AGREGAN = ("conversation_turn", "task_forecast", "blocker_unblocker")
AHORA = datetime(2026, 10, 5, 13, 0, tzinfo=timezone.utc)
BOT = 7_000_000_001


@dataclasses.dataclass
class Espacio:
    id: str
    persona: str        # membership de quien tiene la tarea
    referente: str      # membership de quien la aprueba
    tarea: str
    bloqueo: str
    entrante: str       # inbound_message
    salida: str         # message_outbox
    chat: int


@pytest.fixture
def espacios(conn, intake_world) -> dict[str, Espacio]:
    """Una tarea, un bloqueo, un mensaje entrante y uno saliente en cada espacio."""
    resultado = {}
    with admin(conn) as cur:
        for slug in ("north-lab", "west-studio"):
            w = intake_world[slug]
            persona = w["people"]["Sam North"]["membership_id"]
            chat = w["people"]["Sam North"]["telegram"]
            cur.execute(
                """insert into task (workspace_id, objective_id, titulo, area_id,
                                     responsable_membership_id, estado, fecha_objetivo)
                   values (%s, %s, 'Revisar el tablero', %s, %s, 'asignada', %s)
                   returning id""",
                (w["id"], w["objectives"][0], w["areas"]["field"], persona,
                 AHORA + timedelta(days=3)))
            tarea = str(cur.fetchone()["id"])
            cur.execute(
                """insert into blocker (workspace_id, task_id, causa, abierto_por)
                   values (%s, %s, 'faltan cables', %s) returning id""",
                (w["id"], tarea, persona))
            bloqueo = str(cur.fetchone()["id"])
            cur.execute(
                """insert into inbound_message
                     (workspace_id, telegram_message_id, chat_id, app_user_id, texto)
                   values (%s, 10, %s, %s, 'arranqué') returning id""",
                (w["id"], chat, w["people"]["Sam North"]["app_user_id"]))
            entrante = str(cur.fetchone()["id"])
            cur.execute(
                """insert into message_outbox (workspace_id, chat_id, cuerpo, dedupe_key)
                   values (%s, %s, 'Anotado.', %s) returning id""",
                (w["id"], chat, f"motor-{slug}"))
            salida = str(cur.fetchone()["id"])
            resultado[slug] = Espacio(
                id=w["id"], persona=persona,
                referente=w["people"]["Taylor Quinn"]["membership_id"],
                tarea=tarea, bloqueo=bloqueo, entrante=entrante, salida=salida,
                chat=chat)
    conn.commit()
    return resultado


# --- Una fila de cada tabla nueva, con las referencias de un espacio ----------------------

def _pregunta(cur, e: Espacio, ws: str | None = None) -> str:
    cur.execute(
        """insert into conversation_question
             (workspace_id, membership_id, tipo, task_id, se_puede_dejar, abierta_en)
           values (%s, %s, 'quien_destraba', %s, false, %s) returning id""",
        (ws or e.id, e.persona, e.tarea, AHORA))
    return str(cur.fetchone()["id"])


def _opcion(cur, e: Espacio, pregunta: str, token: str, ws: str | None = None) -> str:
    cur.execute(
        """insert into conversation_option
             (workspace_id, question_id, token, etiqueta, valor, orden)
           values (%s, %s, %s, 'Revisar el tablero', %s, 1) returning id""",
        (ws or e.id, pregunta, token, json.dumps({"task_id": e.tarea})))
    return str(cur.fetchone()["id"])


def _turno(cur, e: Espacio, ws: str | None = None, entrante: str | None = None,
           numero: int = 1) -> str:
    cur.execute(
        """insert into conversation_turn
             (workspace_id, membership_id, sentido, inbound_message_id, jugadas,
              resultado, ia, latencia_ms, at, numero)
           values (%s, %s, 'entrada', %s, %s, %s, 'gpt-6-sol', 900, %s, %s)
           returning id""",
        (ws or e.id, e.persona, entrante or e.entrante,
         json.dumps([{"jugada": "anotar_inicio"}]), json.dumps({"anotado": True}),
         AHORA, numero))
    return str(cur.fetchone()["id"])


def _aviso(cur, e: Espacio, clave: str, ws: str | None = None,
           destinatario: str | None = None, turno: str | None = None) -> str:
    cur.execute(
        """insert into scheduled_notice
             (workspace_id, tipo, task_id, destinatario_membership_id, turno_id,
              hechos, programado_para, dedupe_key, creado_en)
           values (%s, 'aviso_prevision', %s, %s, %s, %s, %s, %s, %s) returning id""",
        (ws or e.id, e.tarea, destinatario or e.referente, turno,
         json.dumps({"atraso_dias_habiles": 2}), AHORA + timedelta(hours=1), clave,
         AHORA))
    return str(cur.fetchone()["id"])


def _estado(cur, e: Espacio, pregunta: str | None, aviso: str | None,
            ws: str | None = None, persona: str | None = None) -> None:
    cur.execute(
        """insert into conversation_state
             (membership_id, workspace_id, pregunta_abierta_id, ultimo_aviso_id,
              actualizado_en)
           values (%s, %s, %s, %s, %s)""",
        (persona or e.persona, ws or e.id, pregunta, aviso, AHORA))


def _prevision(cur, e: Espacio, ws: str | None = None, tarea: str | None = None,
               quien: str | None = None, es_correccion: bool = False) -> str:
    cur.execute(
        """insert into task_forecast
             (workspace_id, task_id, fecha_prevista, motivo, fecha_comprometida,
              atraso_dias_habiles, es_correccion, dicho_por_membership_id, at)
           values (%s, %s, %s, 'faltan cables', %s, 2, %s, %s, %s) returning id""",
        (ws, tarea or e.tarea, date(2026, 10, 12), AHORA + timedelta(days=3),
         es_correccion, quien or e.persona, AHORA))
    return str(cur.fetchone()["id"])


def _quien_destraba(cur, e: Espacio, *, integrante=None, externo=None, no_sabe=False,
                    ws: str | None = None, bloqueo: str | None = None) -> str:
    cur.execute(
        """insert into blocker_unblocker
             (workspace_id, blocker_id, destraba_membership_id, destraba_externo,
              no_sabe, dicho_por_membership_id, at)
           values (%s, %s, %s, %s, %s, %s, %s) returning id""",
        (ws or e.id, bloqueo or e.bloqueo, integrante, externo, no_sabe, e.persona,
         AHORA))
    return str(cur.fetchone()["id"])


def _una_fila_de_cada_tabla(cur, e: Espacio, sufijo: str) -> None:
    pregunta = _pregunta(cur, e)
    _opcion(cur, e, pregunta, f"tok-{sufijo}-0001")
    turno = _turno(cur, e)
    aviso = _aviso(cur, e, f"aviso-{sufijo}", turno=turno)
    _estado(cur, e, pregunta, aviso)
    _prevision(cur, e)
    _quien_destraba(cur, e, externo="el proveedor de cables")


def _cuantas(cur, tabla: str) -> int:
    cur.execute(f"select count(*) as n from {tabla}")
    return cur.fetchone()["n"]


# --- Aislamiento ---------------------------------------------------------------------------

def test_cada_tabla_nueva_tiene_espacio_obligatorio_y_rls_forzado(conn):
    with admin(conn) as cur:
        for tabla in NUEVAS:
            cur.execute(
                """select relrowsecurity, relforcerowsecurity
                     from pg_class where oid = to_regclass(%s)""", (f"leda.{tabla}",))
            fila = cur.fetchone()
            assert fila is not None, f"{tabla} no existe"
            assert fila["relrowsecurity"] and fila["relforcerowsecurity"], tabla
            cur.execute(
                """select polname from pg_policy where polrelid = to_regclass(%s)""",
                (f"leda.{tabla}",))
            assert [p["polname"] for p in cur.fetchall()] == ["aislamiento_espacio"], tabla
            cur.execute(
                """select column_name, is_nullable, data_type, column_default
                     from information_schema.columns
                    where table_schema = 'leda' and table_name = %s""", (tabla,))
            columnas = {c["column_name"]: c for c in cur.fetchall()}
            assert columnas["workspace_id"]["is_nullable"] == "NO", tabla
            # Reglas 2 y 3 de la frontera: nada propio del transporte.
            assert not {"chat_id", "callback_data"} & set(columnas), tabla
            # Los momentos los pone el motor con su reloj, nunca un valor por omisión.
            for nombre, c in columnas.items():
                if c["data_type"].startswith("timestamp") or c["data_type"] == "date":
                    assert c["column_default"] is None, f"{tabla}.{nombre}"


def test_un_espacio_no_ve_las_filas_del_otro(conn, espacios):
    norte, oeste = espacios["north-lab"], espacios["west-studio"]
    with admin(conn) as cur:
        _una_fila_de_cada_tabla(cur, oeste, "oeste")
    conn.commit()

    with espacio(conn, norte.id) as cur:
        for tabla in NUEVAS:
            assert _cuantas(cur, tabla) == 0, tabla
    with espacio(conn, oeste.id) as cur:
        for tabla in NUEVAS:
            assert _cuantas(cur, tabla) == 1, tabla


def test_un_espacio_no_escribe_filas_del_otro(conn, espacios):
    norte, oeste = espacios["north-lab"], espacios["west-studio"]
    with admin(conn) as cur:
        pregunta_oeste = _pregunta(cur, oeste)
    conn.commit()

    intentos = {
        "conversation_question": lambda cur: _pregunta(cur, oeste),
        "conversation_option": lambda cur: _opcion(cur, oeste, pregunta_oeste,
                                                   "tok-cruce-0001"),
        "conversation_turn": lambda cur: _turno(cur, oeste),
        "scheduled_notice": lambda cur: _aviso(cur, oeste, "aviso-cruce"),
        "conversation_state": lambda cur: _estado(cur, oeste, None, None),
        "blocker_unblocker": lambda cur: _quien_destraba(cur, oeste, no_sabe=True),
    }
    with espacio(conn, norte.id) as cur:
        for tabla, intento in intentos.items():
            # Lo rechaza la política (RLS) o, antes, la comprobación de que sus
            # referencias son de este espacio: para este espacio, las del otro no existen.
            with pytest.raises((psycopg.errors.InsufficientPrivilege,
                                psycopg.errors.ForeignKeyViolation)), conn.transaction():
                intento(cur)
    with espacio(conn, oeste.id) as cur:
        for tabla in NUEVAS:
            esperadas = 1 if tabla == "conversation_question" else 0
            assert _cuantas(cur, tabla) == esperadas, tabla
    with espacio(conn, norte.id) as cur:
        # La previsión no declara su espacio: lo deriva de la tarea, que para este
        # espacio no existe. Falla igual que una tarea inventada.
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            _prevision(cur, oeste)
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            _prevision(cur, oeste, tarea="00000000-0000-0000-0000-000000000000")


def test_las_referencias_tienen_que_ser_del_mismo_espacio(conn, espacios):
    """Una fila del propio espacio que apunta a algo de otro espacio se rechaza: la
    comprobación de una clave foránea no pasa por la RLS, así que la clave lleva el
    espacio."""
    norte, oeste = espacios["north-lab"], espacios["west-studio"]
    ajena = dataclasses.replace(norte, tarea=oeste.tarea)
    with admin(conn) as cur:
        intentos = [
            lambda: _pregunta(cur, ajena),
            lambda: _turno(cur, norte, entrante=oeste.entrante),
            lambda: _aviso(cur, norte, "aviso-mezcla", destinatario=oeste.referente),
            lambda: _quien_destraba(cur, norte, no_sabe=True, bloqueo=oeste.bloqueo),
            lambda: _estado(cur, norte, None, None, persona=oeste.persona),
            lambda: _quien_destraba(cur, norte, integrante=oeste.persona),
            lambda: _prevision(cur, norte, quien=oeste.persona),
        ]
        for intento in intentos:
            with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
                intento()
        pregunta_oeste = _pregunta(cur, oeste)
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            _opcion(cur, norte, pregunta_oeste, "tok-mezcla-0001")
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            _estado(cur, norte, pregunta_oeste, None)


# --- Previsiones ---------------------------------------------------------------------------

def test_el_espacio_de_una_prevision_sale_de_su_tarea(conn, espacios):
    norte, oeste = espacios["north-lab"], espacios["west-studio"]
    with espacio(conn, norte.id) as cur:
        sin_declarar = _prevision(cur, norte)
        cur.execute("select workspace_id from task_forecast where id = %s",
                    (sin_declarar,))
        assert str(cur.fetchone()["workspace_id"]) == norte.id
    # Ni la conexión administrativa puede atribuirla a otro espacio.
    with admin(conn) as cur:
        declarada = _prevision(cur, norte, ws=oeste.id)
        cur.execute("select workspace_id from task_forecast where id = %s", (declarada,))
        assert str(cur.fetchone()["workspace_id"]) == norte.id


def test_una_correccion_reemplaza_a_una_prevision_del_mismo_espacio(conn, espacios):
    norte, oeste = espacios["north-lab"], espacios["west-studio"]
    with admin(conn) as cur:
        anterior_oeste = _prevision(cur, oeste)
    with espacio(conn, norte.id) as cur:
        anterior = _prevision(cur, norte)
        cur.execute(
            """insert into task_forecast
                 (task_id, fecha_prevista, fecha_comprometida, atraso_dias_habiles,
                  reemplaza_id, es_correccion, dicho_por_membership_id, at)
               values (%s, %s, %s, 0, %s, true, %s, %s) returning id""",
            (norte.tarea, date(2026, 10, 8), AHORA + timedelta(days=3), anterior,
             norte.persona, AHORA))
        assert cur.fetchone()["id"]
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            cur.execute(
                """insert into task_forecast
                     (task_id, fecha_prevista, fecha_comprometida, atraso_dias_habiles,
                      reemplaza_id, dicho_por_membership_id, at)
                   values (%s, %s, %s, 0, %s, %s, %s)""",
                (norte.tarea, date(2026, 10, 8), AHORA, anterior_oeste, norte.persona,
                 AHORA))


def test_una_prevision_solo_reemplaza_a_otra_de_la_misma_tarea(conn, espacios, intake_world):
    """Revisión de la E2-1 (`review-03f111a243648455`): reemplazar una previsión de otra
    tarea del mismo espacio mezclaría las historias de dos tareas."""
    norte = espacios["north-lab"]
    w = intake_world["north-lab"]
    with admin(conn) as cur:
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, estado, fecha_objetivo)
               values (%s, %s, 'Revisar los planos', %s, %s, 'asignada', %s)
               returning id""",
            (norte.id, w["objectives"][0], w["areas"]["field"], norte.persona,
             AHORA + timedelta(days=5)))
        otra_tarea = str(cur.fetchone()["id"])
    conn.commit()
    with espacio(conn, norte.id) as cur:
        de_la_otra = _prevision(cur, norte, tarea=otra_tarea)
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            cur.execute(
                """insert into task_forecast
                     (task_id, fecha_prevista, fecha_comprometida, atraso_dias_habiles,
                      reemplaza_id, es_correccion, dicho_por_membership_id, at)
                   values (%s, %s, %s, 0, %s, true, %s, %s)""",
                (norte.tarea, date(2026, 10, 8), AHORA + timedelta(days=3), de_la_otra,
                 norte.persona, AHORA))


# --- Lo que sólo se agrega ------------------------------------------------------------------

def test_turnos_previsiones_y_quien_destraba_solo_se_agregan(conn, espacios):
    norte = espacios["north-lab"]
    with espacio(conn, norte.id) as cur:
        _turno(cur, norte)
        _prevision(cur, norte)
        _quien_destraba(cur, norte, no_sabe=True)
        for tabla in SOLO_SE_AGREGAN:
            assert _cuantas(cur, tabla) == 1, tabla
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                cur.execute(f"update {tabla} set workspace_id = workspace_id")
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                cur.execute(f"delete from {tabla}")


def test_preguntas_opciones_y_avisos_se_cierran_pero_no_se_borran(conn, espacios):
    norte = espacios["north-lab"]
    with espacio(conn, norte.id) as cur:
        pregunta = _pregunta(cur, norte)
        opcion = _opcion(cur, norte, pregunta, "tok-norte-0001")
        aviso = _aviso(cur, norte, "aviso-norte")
        cur.execute(
            """update conversation_question
                  set cerrada_en = %s, cierre = 'respondida'
                where id = %s""", (AHORA, pregunta))
        cur.execute("update conversation_option set elegida_en = %s where id = %s",
                    (AHORA, opcion))
        cur.execute(
            """update scheduled_notice
                  set estado = 'enviado', resuelto_en = %s, outbox_id = %s,
                      intentos = 1
                where id = %s""", (AHORA, norte.salida, aviso))
        for tabla in ("conversation_question", "conversation_option",
                      "scheduled_notice"):
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                cur.execute(f"delete from {tabla}")


def test_una_pregunta_cerrada_dice_como_se_cerro(conn, espacios):
    norte = espacios["north-lab"]
    with espacio(conn, norte.id) as cur:
        pregunta = _pregunta(cur, norte)
        for cambios in ("cerrada_en = %(ahora)s",
                        "cierre = 'cancelada'",
                        "cerrada_en = %(ahora)s, cierre = 'olvidada'"):
            with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
                cur.execute(f"update conversation_question set {cambios} where id = %(id)s",
                            {"ahora": AHORA, "id": pregunta})


# --- Quién destraba -------------------------------------------------------------------------

def test_quien_destraba_es_exactamente_uno(conn, espacios):
    norte = espacios["north-lab"]
    with espacio(conn, norte.id) as cur:
        _quien_destraba(cur, norte, integrante=norte.referente)
        _quien_destraba(cur, norte, externo="el proveedor de cables")
        _quien_destraba(cur, norte, no_sabe=True)
        for valores in ({},
                        {"externo": "   "},
                        {"integrante": norte.referente, "externo": "el proveedor"},
                        {"integrante": norte.referente, "no_sabe": True},
                        {"externo": "el proveedor", "no_sabe": True}):
            with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
                _quien_destraba(cur, norte, **valores)


# --- Opciones -------------------------------------------------------------------------------

def test_el_token_de_una_opcion_es_unico(conn, espacios):
    norte, oeste = espacios["north-lab"], espacios["west-studio"]
    with admin(conn) as cur:
        pregunta_oeste = _pregunta(cur, oeste)
        _opcion(cur, oeste, pregunta_oeste, "tok-repetido-01")
    conn.commit()
    with espacio(conn, norte.id) as cur:
        una = _pregunta(cur, norte)
        otra = _pregunta(cur, norte)
        _opcion(cur, norte, una, "tok-norte-0001")
        with pytest.raises(psycopg.errors.UniqueViolation), conn.transaction():
            _opcion(cur, norte, otra, "tok-norte-0001")
        # También contra el token de otro espacio: el toque se resuelve por el token.
        with pytest.raises(psycopg.errors.UniqueViolation), conn.transaction():
            _opcion(cur, norte, otra, "tok-repetido-01")


# --- Avisos guardados ----------------------------------------------------------------------

def test_un_aviso_guardado_no_se_duplica_y_su_omision_tiene_motivo(conn, espacios):
    norte, oeste = espacios["north-lab"], espacios["west-studio"]
    with espacio(conn, norte.id) as cur:
        aviso = _aviso(cur, norte, "prevision:tarea:1")
        with pytest.raises(psycopg.errors.UniqueViolation), conn.transaction():
            _aviso(cur, norte, "prevision:tarea:1")
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            cur.execute(
                """update scheduled_notice set estado = 'omitido', resuelto_en = %s
                    where id = %s""", (AHORA, aviso))
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            cur.execute("update scheduled_notice set estado = 'enviado' where id = %s",
                        (aviso,))
        cur.execute(
            """update scheduled_notice
                  set estado = 'omitido', resuelto_en = %s,
                      motivo_omision = 'la previsión volvió a la fecha comprometida'
                where id = %s""", (AHORA, aviso))
    # La clave se repite sin problema en otro espacio.
    with espacio(conn, oeste.id) as cur:
        _aviso(cur, oeste, "prevision:tarea:1")


# --- Aviso previo ---------------------------------------------------------------------------

def test_el_aviso_previo_es_un_ajuste_del_espacio_de_al_menos_un_dia_habil(conn, espacios):
    norte, oeste = espacios["north-lab"], espacios["west-studio"]

    def fijar(cur, valor):
        cur.execute(
            """insert into workspace_setting (workspace_id, clave, valor)
               values (%s, 'aviso_previo_dias_habiles', %s)
               on conflict (workspace_id, clave) do update set valor = excluded.valor""",
            (norte.id, json.dumps(valor)))

    with espacio(conn, norte.id) as cur:
        fijar(cur, 3)
        for invalido in (0, -1, 1.5, "tres", None, [3]):
            with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
                fijar(cur, invalido)
        fijar(cur, 1)
        # Las demás claves no cambian: siguen aceptando cualquier valor.
        cur.execute(
            """insert into workspace_setting (workspace_id, clave, valor)
               values (%s, 'bloqueos', %s)""", (norte.id, json.dumps("texto")))
    with espacio(conn, oeste.id) as cur:
        cur.execute("select count(*) as n from workspace_setting "
                    "where clave = 'aviso_previo_dias_habiles'")
        assert cur.fetchone()["n"] == 0


# --- Ejecución única de un mensaje repetido -------------------------------------------------

def _entrante(cur, e: Espacio, message_id: int, bot: int | None = BOT,
              conflicto: str = "") -> list:
    cur.execute(
        f"""insert into inbound_message
              (workspace_id, telegram_bot_id, telegram_message_id, chat_id, texto)
            values (%s, %s, %s, %s, 'arranqué') {conflicto} returning id""",
        (e.id, bot, message_id, e.chat))
    return cur.fetchall()


def test_un_mensaje_de_telegram_repetido_se_recibe_una_sola_vez(conn, espacios):
    norte, oeste = espacios["north-lab"], espacios["west-studio"]
    with espacio(conn, norte.id) as cur:
        assert len(_entrante(cur, norte, 500)) == 1
        with pytest.raises(psycopg.errors.UniqueViolation), conn.transaction():
            _entrante(cur, norte, 500)
        # El escuchador del motor lo absorbe sin error: la reentrega no crea un turno.
        assert _entrante(cur, norte, 500, conflicto="on conflict do nothing") == []
        # Otro mensaje, u otro bot (el mismo número en otra conversación), es nuevo.
        assert len(_entrante(cur, norte, 501)) == 1
        assert len(_entrante(cur, norte, 500, bot=BOT + 1)) == 1
        # Los flujos congelados no informan el bot: su recibo repetido (pasada la cota
        # de reentrega, `gateway._estado_de_entrega`) sigue entrando como antes.
        assert len(_entrante(cur, norte, 900, bot=None)) == 1
        assert len(_entrante(cur, norte, 900, bot=None)) == 1
    with espacio(conn, oeste.id) as cur:
        assert len(_entrante(cur, oeste, 500)) == 1


def test_un_mensaje_tiene_un_solo_turno_de_entrada_y_cada_turno_su_numero(conn, espacios):
    """Revisión de la E2-2: la ejecución única de un turno no depende sólo del motor."""
    norte = espacios["north-lab"]
    with espacio(conn, norte.id) as cur:
        _turno(cur, norte, numero=1)
        with pytest.raises(psycopg.errors.UniqueViolation), conn.transaction():
            _turno(cur, norte, numero=2)
        otro = _entrante(cur, norte, 501)[0]["id"]
        with pytest.raises(psycopg.errors.UniqueViolation), conn.transaction():
            _turno(cur, norte, entrante=str(otro), numero=1)
        assert _turno(cur, norte, entrante=str(otro), numero=2)
