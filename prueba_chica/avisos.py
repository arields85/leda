"""Los avisos guardados: todo lo que Leda manda por su cuenta (E2-5).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Avisos guardados" y "Fallas de la IA"); ADR
0018, decisiones 8 (caso 2) y 9b; mecánica §9, §10 y §12.

Un aviso se guarda como hechos en `scheduled_notice`, con su hora y una clave de
deduplicación: nada se guarda ni sale dos veces. Al llegar su hora, y sólo dentro del horario
del espacio (9e), `enviar_avisos`:

1. vuelve a leer la tarea y comprueba que el aviso todavía corresponda, con la regla de su
   tipo (`TIPOS`); si ya no corresponde, queda `omitido` con su motivo, nunca en silencio;
2. le pide a la IA que lo redacte desde los hechos de ese momento, que quedan guardados como
   los que se mandaron; un efecto que pasa después dice siempre su estado (primer contacto
   real, 2026-10-05);
3. lo encola en el outbox, lo marca `enviado` y lo deja en el registro de turnos de quien lo
   recibe, como su último aviso. Si pide el estado de la tarea, abre la pregunta y cuenta el
   recordatorio en la espera (`pending_reply`).

**Un envío por persona** (mecánica §10; hallazgo de la E2-7): los avisos automáticos de una
persona que salen juntos (los de la escalera de un día se guardan todos en la primera vuelta de
ese día) se redactan en un solo mensaje, desde los hechos de todos, con la pregunta de uno solo
(un tema a la vez: las demás quedan para después). Los de coordinación, que causa el acto de
otra persona, salen aparte y siempre, como las respuestas. El tope diario del pack, si lo hay,
lo aplica el despachador (`despachador._tope_diario`): pospone, nunca descarta; con un envío
por día y por espacio, en la prueba chica no se alcanza.

Si la IA no lo redacta (o redacta un texto que el canal no lleva), el envío entero espera y se
reintenta a los 1, 2, 4 y 8 minutos, con sus avisos juntos; al quinto
fallo queda `fallido` con sus hechos, se registra un incidente y, si una persona lo causó (el
turno que lo guardó), se le guarda un aviso de la falla con lo pendiente, que también redacta
la IA: nunca sale un texto armado a mano. Un destinatario ausente no recibe nada: su aviso
espera a que vuelva (la escalera lo reemplaza por un reencuadre, `escalera.py`).

Cada tipo se declara una vez con su regla (`TipoDeAviso`), como las fichas de las jugadas: el
camino de envío es uno para todos. Cuándo se guardan los de la escalera es de `escalera.py`;
los de una previsión y su corrección, de sus fichas (`fichas.py`).
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from types import MappingProxyType, SimpleNamespace
from typing import Any

import psycopg

from leda.calendario import Calendario
from leda.db import espacio
from leda.incidentes import registrar_incidente
from leda.salida import PayloadValidationError, enqueue_outbox

from . import preguntas
from .ancla import (REPREGUNTA_DE_ESTADO, VENCIMIENTO_CON_PREVISION, ancla, anclaje,
                    clave_del_anclaje, fecha_de_la_clave)
from .ancla import prevision_vigente as _prevision_vigente
from .fichas import GUARDADO_SIN_ENVIAR
from .ia import IA
from .tiempo import Reloj
from .turno import leer_ultimos_turnos, no_vacio, registrar_salida

# Decisión 8, caso 2: tras el 1.º, 2.º, 3.º y 4.º fallo de la IA, la espera hasta el
# intento siguiente; al quinto fallo, el aviso queda `fallido`.
ESPERAS_TRAS_UN_FALLO = (timedelta(minutes=1), timedelta(minutes=2), timedelta(minutes=4),
                         timedelta(minutes=8))
INTENTOS = len(ESPERAS_TRAS_UN_FALLO) + 1

ETAPA_AVISO_GUARDADO = "motor_aviso_guardado"

# La espera de respuesta de un pedido de estado (`pending_reply.tipo`, ADR 0017, decisión 6)
# y la pregunta que la acompaña.
ESPERA_DE_ESTADO = preguntas.ESTADO_DE_LA_TAREA

# La escalera de una pregunta que espera respuesta (`escalera.py`): la pregunta otra vez y,
# agotada sin respuesta, el escalamiento. La clave nombra la pregunta (`q<id>`).
REPREGUNTA = "repregunta"
ESCALAMIENTO_DE_UNA_PREGUNTA = "escalamiento_de_una_pregunta"

ABIERTOS = ("asignada", "en_curso")     # en la escalera: comprometida, sin entregar
ENVIADO = "enviado"                     # el estado de un aviso que ya salió, en un hecho
# De menos a más urgente (mecánica §11): el tipo de un envío que junta varios avisos es el del
# más urgente.
URGENCIA = ("informativo", "normal", "seguimiento", "prioritario", "urgente")
NO_SALIO = "no_salio"                   # un aviso que quedó fallido


@dataclass(frozen=True)
class Momento:
    """La transacción del espacio, su calendario y el momento del motor."""

    cur: psycopg.Cursor
    workspace_id: str
    cal: Calendario
    ahora: datetime

    @property
    def hoy(self) -> date:
        return self.ahora.astimezone(self.cal.zona).date()

    def fecha(self, momento: datetime) -> date:
        return momento.astimezone(self.cal.zona).date()


Vigencia = Callable[[Momento, dict[str, Any]], tuple[str | None, dict[str, Any]]]


@dataclass(frozen=True)
class TipoDeAviso:
    """Un tipo de aviso guardado: cómo sale y cuándo todavía corresponde. `vigente` devuelve
    el motivo para omitirlo, o `None` y los hechos de ese momento."""

    nombre: str
    tipo_de_mensaje: str            # `message_outbox.tipo`
    vigente: Vigencia
    es_coordinacion: bool = False   # lo causa el acto de otra persona (mecánica §10)
    escala: bool = False            # al salir, la espera queda escalada


# --- Guardar --------------------------------------------------------------------------------

def guardar(cur, workspace_id: str, tipo: str, *, task_id: str | None, destinatario: str,
            hechos: dict[str, Any], programado_para: datetime, clave: str, ahora: datetime,
            turno_id: str | None = None) -> tuple[str, bool]:
    """Guarda un aviso, salvo que ya exista uno con la misma clave. (id, si es nuevo)."""
    cur.execute(
        """insert into scheduled_notice (workspace_id, tipo, task_id,
                                         destinatario_membership_id, turno_id, hechos,
                                         programado_para, dedupe_key, creado_en)
           values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
           on conflict (workspace_id, dedupe_key) do nothing
           returning id""",
        (workspace_id, tipo, task_id, destinatario, turno_id, _json(hechos), programado_para,
         clave, ahora))
    fila = cur.fetchone()
    if fila is not None:
        return str(fila["id"]), True
    cur.execute("select id from scheduled_notice where workspace_id = %s and dedupe_key = %s",
                (workspace_id, clave))
    return str(cur.fetchone()["id"]), False


def omitir(cur, aviso_id: str, motivo: str, ahora: datetime) -> None:
    cur.execute("""update scheduled_notice
                      set estado = 'omitido', motivo_omision = %s, resuelto_en = %s,
                          proximo_intento_en = null
                    where id = %s and estado = 'guardado'""", (motivo, ahora, aviso_id))


# --- Enviar ---------------------------------------------------------------------------------

def enviar_avisos(conn: psycopg.Connection, workspace_id: str, ia: IA, reloj: Reloj, *,
                  solo: str | None = None, forzar: bool = False) -> dict[str, int]:
    """Los avisos guardados cuya hora llegó, de a uno. Fuera del horario no sale ninguno. `solo`
    acota a un aviso; `forzar` no espera el próximo intento (el comando que reintenta a mano).
    Corre en una transacción de `db.espacio`; quien llama la confirma. Devuelve cuántos
    terminaron de cada forma (`enviado`, `omitido`, `reintento`, `fallido`, `en_espera`)."""
    ahora = reloj.ahora()
    resumen: Counter[str] = Counter()
    with espacio(conn, workspace_id) as cur:
        m = Momento(cur, workspace_id, Calendario.desde_base(cur, workspace_id), ahora)
        if not m.cal.en_horario(ahora):
            return {"fuera_de_horario": 1}
        cur.execute(
            """select * from scheduled_notice
                where estado = 'guardado' and programado_para <= %s
                  and (%s or proximo_intento_en is null or proximo_intento_en <= %s)
                  and (%s::uuid is null or id = %s::uuid)
                order by programado_para, creado_en
                for update skip locked""",
            (ahora, forzar, ahora, solo, solo))
        listos: list[_Listo] = []
        for aviso in cur.fetchall():
            listo = _preparar(m, aviso)
            if isinstance(listo, str):
                resumen[listo] += 1
            else:
                listos.append(listo)
        for envio in _envios(listos):
            for resultado in _enviar(m, envio, ia):
                resumen[resultado] += 1
    return dict(resumen)


@dataclass(frozen=True)
class _Listo:
    """Un aviso que corresponde y sale ahora, con los hechos de este momento."""

    aviso: dict[str, Any]
    tipo: TipoDeAviso
    destinatario: dict[str, Any]
    hechos: dict[str, Any]


def _envios(listos: list[_Listo]) -> list[list[_Listo]]:
    """Los envíos: uno por persona con sus avisos automáticos, en el orden en que se guardaron,
    y uno por cada aviso de coordinación (mecánica §10)."""
    envios: list[list[_Listo]] = []
    de_la_persona: dict[str, list[_Listo]] = {}
    for listo in listos:
        if listo.tipo.es_coordinacion:
            envios.append([listo])
            continue
        persona = str(listo.destinatario["membership_id"])
        if persona not in de_la_persona:
            de_la_persona[persona] = []
            envios.append(de_la_persona[persona])
        de_la_persona[persona].append(listo)
    return envios


def _preparar(m: Momento, aviso: dict[str, Any]) -> _Listo | str:
    """Si el aviso sale ahora: sus hechos de este momento; si no, cómo terminó (`omitido`,
    `en_espera`)."""
    cur = m.cur
    aviso_id = str(aviso["id"])
    destinatario = integrante(cur, aviso["destinatario_membership_id"])
    if destinatario is None or not destinatario["activo"]:
        omitir(cur, aviso_id, "destinatario_inactivo", m.ahora)
        return "omitido"
    if destinatario["telegram_user_id"] is None:
        omitir(cur, aviso_id, "destinatario_sin_telegram", m.ahora)
        return "omitido"
    if ausente(cur, str(aviso["destinatario_membership_id"]), m.hoy):
        return "en_espera"          # vuelve a mirarse cuando vuelva (mecánica §9, ausencias)
    tipo = TIPOS.get(aviso["tipo"])
    if tipo is None:
        omitir(cur, aviso_id, "tipo_sin_declarar", m.ahora)
        return "omitido"
    if tipo.escala and _responsable_ausente(m, aviso):
        # La escalera no avanza durante la ausencia del responsable (mecánica §9): tampoco su
        # escalamiento, aunque vaya a otra persona. A la vuelta lo reemplaza el reencuadre.
        return "en_espera"
    motivo, hechos = tipo.vigente(m, aviso)
    if motivo is not None:
        omitir(cur, aviso_id, motivo, m.ahora)
        return "omitido"
    return _Listo(aviso, tipo, destinatario, hechos)


def _enviar(m: Momento, envio: list[_Listo], ia: IA) -> list[str]:
    """Un envío: la IA redacta un mensaje desde los hechos de todos sus avisos, con una sola
    pregunta (la del primero que pide respuesta); sale por el outbox una vez y cada aviso queda
    `enviado` con esa fila. Cómo terminó cada aviso."""
    cur = m.cur
    destinatario = envio[0].destinatario
    persona = str(destinatario["membership_id"])
    preguntas_de = [_pregunta_del_aviso(m, x.aviso, x.hechos) for x in envio]
    pregunta = next((q for q in preguntas_de if q is not None), None)
    pedido = {"hoy": m.hoy.isoformat(), "persona": destinatario["nombre"], "mensaje": None,
              "hechos": [x.hechos for x in envio], "pregunta": pregunta,
              "ultimos_turnos": list(leer_ultimos_turnos(cur, persona))}
    try:
        texto = no_vacio(ia.redactar(pedido))
    except Exception as falla:     # la IA es un servicio externo: cualquier falla es no redactar
        return _si_la_ia_no_redacta(m, envio, falla)

    primero = str(envio[0].aviso["id"])
    clave = f"motor:aviso:{primero}"
    try:
        enqueue_outbox(cur, workspace_id=m.workspace_id,
                       chat_id=destinatario["telegram_user_id"], text=texto, dedupe_key=clave,
                       recipient_membership_id=persona,
                       message_type=max((x.tipo.tipo_de_mensaje for x in envio),
                                        key=URGENCIA.index),
                       es_coordinacion=envio[0].tipo.es_coordinacion, scheduled_for=m.ahora)
    except PayloadValidationError as falla:
        # Un texto que el canal no lleva (más largo que su límite: un envío que junta varios
        # avisos lo hace más probable) no es una redacción: se reintenta como si la IA no lo
        # hubiera redactado, y nunca corta la vuelta de los demás avisos. Lo valida antes de
        # escribir nada, así que no queda nada a medias.
        return _si_la_ia_no_redacta(m, envio, falla)
    cur.execute("select id from message_outbox where dedupe_key = %s", (clave,))
    outbox_id = str(cur.fetchone()["id"])
    for x in envio:
        cur.execute("""update scheduled_notice
                          set estado = 'enviado', outbox_id = %s, resuelto_en = %s, hechos = %s,
                              intentos = intentos + 1, proximo_intento_en = null
                        where id = %s""", (outbox_id, m.ahora, _json(x.hechos), x.aviso["id"]))
    registrar_salida(cur, m.workspace_id, persona, outbox_id, ia.nombre, m.ahora)
    # El último aviso es el envío: el primero de sus avisos; los demás comparten su fila.
    cur.execute(
        """insert into conversation_state (membership_id, workspace_id, ultimo_aviso_id,
                                           actualizado_en)
           values (%s, %s, %s, %s)
           on conflict (membership_id) do update
              set ultimo_aviso_id = excluded.ultimo_aviso_id,
                  actualizado_en = excluded.actualizado_en""",
        (persona, m.workspace_id, primero, m.ahora))
    # Las preguntas de un mismo envío, ordenadas como las de un turno: la primera queda
    # abierta y las demás para después (un tema a la vez).
    turno = SimpleNamespace(cur=cur, ahora=m.ahora, preguntas_del_turno=[], dejadas=[],
                            quien=SimpleNamespace(workspace_id=m.workspace_id,
                                                  membership_id=persona))
    for x, q in zip(envio, preguntas_de):
        if q is not None:
            _abrir_la_pregunta(m, turno, x.aviso)
        if x.tipo.escala:
            # La espera que escala: la de su pregunta, o la del estado de la tarea.
            cur.execute("""update pending_reply set escalado_en = %s
                            where task_id = %s and tipo = %s
                              and satisfecho_en is null and escalado_en is null""",
                        (m.ahora, x.aviso["task_id"], _espera_del_aviso(x.hechos)))
    return ["enviado"] * len(envio)


def _espera_del_aviso(hechos: dict[str, Any]) -> str:
    """El tipo de la espera de un aviso: la de la pregunta que lleva, o la del estado."""
    tipo = preguntas.TIPOS.get(hechos.get("pregunta") or "")
    return tipo.espera if tipo is not None and tipo.espera else ESPERA_DE_ESTADO


def _responsable_ausente(m: Momento, aviso) -> bool:
    tarea = leer_tarea(m.cur, aviso["task_id"]) if aviso["task_id"] is not None else None
    return tarea is not None and tarea["responsable_membership_id"] is not None and ausente(
        m.cur, str(tarea["responsable_membership_id"]), m.hoy)


def _pregunta_del_aviso(m: Momento, aviso, hechos: dict[str, Any]) -> dict[str, Any] | None:
    """Un aviso que necesita respuesta pide el estado de su tarea: es la única pregunta que
    se hace en él (la misma regla que en una respuesta)."""
    if hechos.get("necesita_respuesta") is not True or aviso["task_id"] is None:
        return None
    return {"tipo": hechos.get("pregunta") or ESPERA_DE_ESTADO,
            "tarea": {"titulo": hechos.get("tarea")}, "desde_antes": False}


def _abrir_la_pregunta(m: Momento, turno, aviso: dict[str, Any]) -> None:
    """La pregunta del aviso, ordenada con las demás de la persona, y el recordatorio contado
    en su espera. Un pedido de estado abre la pregunta del estado (`preguntas.abrir`; la misma
    si sigue abierta de un recordatorio anterior), que no se puede dejar sin efecto (9b), y
    reemplaza a la pregunta de la fecha de la misma tarea, si quedó sin contestar: es el mismo
    pedido, hecho de nuevo, y un tema a la vez. La repregunta de una pregunta que espera
    respuesta la vuelve a hacer: es la abierta (`preguntas.retomar`)."""
    task_id, tipo_de_aviso = str(aviso["task_id"]), aviso["tipo"]
    persona = turno.quien.membership_id
    if tipo_de_aviso == REPREGUNTA:
        pregunta = pregunta_del_aviso(m.cur, aviso)
        preguntas.retomar(turno, str(pregunta["id"]))
        espera = preguntas.TIPOS[pregunta["tipo"]].espera
    else:
        preguntas.cerrar_de_tipo(turno, preguntas.FECHA_DE_LA_TAREA, task_id, "sin_efecto",
                                 {"reemplazada_por": tipo_de_aviso})
        preguntas.abrir(turno, ESPERA_DE_ESTADO, task_id, jugada={"aviso": tipo_de_aviso})
        espera = ESPERA_DE_ESTADO
    # Sólo en la espera de esta escalera, la más nueva: una escalada de un vencimiento anterior
    # ya terminó (`escalera._abrir_la_espera`).
    m.cur.execute("""update pending_reply set recordatorios = recordatorios + 1
                      where id = (select id from pending_reply
                                   where task_id = %s and membership_id = %s and tipo = %s
                                     and satisfecho_en is null
                                   order by preguntado_en desc limit 1)""",
                  (task_id, persona, espera))


def pregunta_del_aviso(cur, aviso: dict[str, Any]) -> dict[str, Any] | None:
    """La pregunta que repite o escala un aviso de la escalera de una pregunta: su clave la
    nombra (`motor:<tipo>:<tarea>:q<pregunta>:...`)."""
    cur.execute("select * from conversation_question where id = %s",
                (aviso["dedupe_key"].split(":")[3][1:],))
    return cur.fetchone()


def _si_la_ia_no_redacta(m: Momento, envio: list[_Listo], falla: Exception) -> list[str]:
    """Un envío que la IA no redactó se reintenta entero: sus avisos comparten la cuenta de
    intentos (la del que más lleva) y el momento del próximo, así vuelven a salir juntos en un
    solo mensaje (mecánica §10) y ninguno espera más de lo que le toca."""
    intentos = max(x.aviso["intentos"] for x in envio) + 1
    return [_un_aviso_que_no_salio(m, x.aviso, x.destinatario, falla, intentos) for x in envio]


def _un_aviso_que_no_salio(m: Momento, aviso, destinatario, falla: Exception,
                           intentos: int) -> str:
    cur, aviso_id = m.cur, str(aviso["id"])
    if intentos < INTENTOS:
        cur.execute("""update scheduled_notice set intentos = %s, proximo_intento_en = %s
                        where id = %s""",
                    (intentos, m.ahora + ESPERAS_TRAS_UN_FALLO[intentos - 1], aviso_id))
        return "reintento"
    cur.execute("""update scheduled_notice
                      set estado = 'fallido', intentos = %s, resuelto_en = %s,
                          proximo_intento_en = null
                    where id = %s""", (intentos, m.ahora, aviso_id))
    causante = _quien_lo_causo(cur, aviso)
    registrar_incidente(
        cur, m.workspace_id,
        f"La IA no redactó un aviso guardado del motor de conversación ({aviso['tipo']}, "
        f"para {destinatario['nombre']}) tras {INTENTOS} intentos, a los 1, 2, 4 y 8 "
        f"minutos: quedó guardado con sus hechos y no salió."
        + (f" {causante['nombre']}, que lo causó, recibe el aviso de la falla."
           if causante else ""),
        referencia_cruda=f"{type(falla).__name__}: {falla}", etapa=ETAPA_AVISO_GUARDADO)
    if causante is not None:
        guardar(cur, m.workspace_id, "falla_de_aviso", task_id=aviso["task_id"],
                destinatario=str(causante["membership_id"]),
                hechos={"aviso": "no_salio_un_aviso",
                        "aviso_que_no_salio": {"a": destinatario["nombre"],
                                               "estado": NO_SALIO,
                                               "lo_pendiente": aviso["hechos"]},
                        "necesita_respuesta": False},
                programado_para=m.ahora, clave=f"motor:falla_de_aviso:{aviso_id}",
                ahora=m.ahora)
    return "fallido"


def _quien_lo_causo(cur, aviso) -> dict[str, Any] | None:
    """La persona cuyo turno guardó el aviso; nadie si lo guardó Leda por su cuenta (la
    escalera) o si es él mismo el aviso de una falla."""
    if aviso["turno_id"] is None or aviso["tipo"] == "falla_de_aviso":
        return None
    cur.execute("select membership_id from conversation_turn where id = %s",
                (aviso["turno_id"],))
    turno = cur.fetchone()
    return integrante(cur, turno["membership_id"]) if turno else None


# --- Lo que se lee de nuevo -------------------------------------------------------------------

def integrante(cur, membership_id) -> dict[str, Any] | None:
    cur.execute("""select membership_id, nombre, telegram_user_id, activo, rol_id, area_id
                     from integrante where membership_id = %s""", (str(membership_id),))
    return cur.fetchone()


def ausente(cur, membership_id: str, hoy: date) -> bool:
    cur.execute("""select 1 from absence
                    where membership_id = %s and desde <= %s
                      and (hasta is null or hasta >= %s) limit 1""",
                (membership_id, hoy, hoy))
    return cur.fetchone() is not None


def leer_tarea(cur, task_id) -> dict[str, Any] | None:
    cur.execute("""select t.id, t.titulo, t.estado::text estado, t.fecha_objetivo, t.area_id,
                          t.responsable_membership_id,
                          exists (select 1 from blocker b
                                   where b.task_id = t.id and b.resuelto_en is null) bloqueada
                     from task t where t.id = %s""", (str(task_id),))
    return cur.fetchone()


def espera_de_la_pregunta(cur, pregunta: dict[str, Any]) -> dict[str, Any] | None:
    """La espera abierta de una pregunta que espera respuesta, si sigue sin contestar."""
    espera = preguntas.TIPOS[pregunta["tipo"]].espera
    if espera is None or pregunta["task_id"] is None:
        return None
    cur.execute("""select * from pending_reply
                    where membership_id = %s and task_id = %s and tipo = %s
                      and satisfecho_en is null
                    order by preguntado_en desc limit 1""",
                (str(pregunta["membership_id"]), str(pregunta["task_id"]), espera))
    return cur.fetchone()


def espera_abierta(cur, task_id) -> dict[str, Any] | None:
    """La espera de respuesta sobre el estado de la tarea, si hay una sin contestar."""
    cur.execute("""select * from pending_reply
                    where task_id = %s and tipo = %s and satisfecho_en is null
                    order by preguntado_en desc limit 1""", (str(task_id), ESPERA_DE_ESTADO))
    return cur.fetchone()


def quienes_escalan(cur, tarea: dict[str, Any]) -> list[dict[str, Any]]:
    """A quiénes va el escalamiento por falta de respuesta: la ruta del pack
    (`falta_persistente_de_respuesta`), la del área de la tarea antes que la general y por su
    orden; una ruta a un rol llega a todos los que lo tienen. Nunca al responsable mismo."""
    cur.execute(
        """select r.destino_membership_id, r.destino_rol_id from escalation_route r
            where r.disparador = 'falta_persistente_de_respuesta'
              and (r.area_id = %s or r.area_id is null)
            order by (r.area_id is null), r.orden""", (tarea["area_id"],))
    for ruta in cur.fetchall():
        cur.execute(
            """select membership_id, nombre from integrante
                where activo and membership_id <> %s
                  and (membership_id = %s or rol_id = %s)
                order by nombre""",
            (tarea["responsable_membership_id"], ruta["destino_membership_id"],
             ruta["destino_rol_id"]))
        destinos = cur.fetchall()
        if destinos:
            return destinos
    return []


def prevision_vigente(m: Momento, tarea: dict[str, Any]) -> dict[str, Any] | None:
    """La última previsión de la tarea, si no es la fecha comprometida, con el estado de su
    aviso al referente (un efecto que pasa después dice su estado)."""
    f = _prevision_vigente(m.cur, tarea["id"])
    if f is None or f["fecha_prevista"] == m.fecha(tarea["fecha_objetivo"]):
        return None
    dicha: dict[str, Any] = {"fecha": f["fecha_prevista"].isoformat(),
                             "atraso_dias_habiles": f["atraso_dias_habiles"]}
    if f["motivo"]:
        dicha["motivo"] = f["motivo"]
    m.cur.execute("""select a.estado, i.nombre from scheduled_notice a
                       join integrante i on i.membership_id = a.destinatario_membership_id
                      where a.workspace_id = %s and a.dedupe_key = %s""",
                  (m.workspace_id, f"motor:nueva_prevision:{f['id']}"))
    aviso = m.cur.fetchone()
    estados = {"enviado": ENVIADO, "guardado": GUARDADO_SIN_ENVIAR, "fallido": NO_SALIO}
    if aviso is not None and aviso["estado"] in estados:
        dicha["aviso_al_referente"] = {"a": aviso["nombre"],
                                       "estado": estados[aviso["estado"]]}
    return dicha


def dependientes(cur, task_id) -> list[dict[str, Any]]:
    """Las tareas abiertas que dependen de ésta (mecánica §4): una bloqueante no puede arrancar
    hasta que ésta termine."""
    cur.execute("""select t.titulo, d.tipo::text tipo from dependency d
                     join task t on t.id = d.destino_task_id
                    where d.origen_task_id = %s and t.estado not in ('terminada', 'cancelada')
                    order by t.titulo""", (str(task_id),))
    return [{"tarea": f["titulo"], "no_puede_arrancar_hasta_que_termine": f["tipo"] ==
             "bloqueante"} for f in cur.fetchall()]


# --- Los avisos de la escalera ---------------------------------------------------------------
#
# La escalera (`escalera.py`) decide cuándo se guarda cada uno; acá están sus hechos y cuándo
# dejan de corresponder: la tarea ya no está abierta, está bloqueada, cambió su vencimiento o
# su responsable, o la persona ya contestó (la espera se cerró).

# Lo que se lee de nuevo en cada momento; lo demás de un aviso de la escalera es fijo (qué
# aviso es, el número de pedido, la ausencia). `avisa_que_va_a_escalar` es una marca del código
# que nunca llega a la IA: en su lugar van los hechos de a quién se escala.
_DE_ESTE_MOMENTO = frozenset({"tarea", "vence", "dias_habiles_hasta_el_vencimiento",
                              "atraso_dias_habiles", "estado", "responsable",
                              "prevision_vigente", "dependientes", "si_no_hay_respuesta",
                              "pide_el_estado_el"})
AVISA_QUE_VA_A_ESCALAR = "avisa_que_va_a_escalar"


def hechos_de_la_escalera(m: Momento, tipo: str, tarea: dict[str, Any],
                          base: dict[str, Any]) -> dict[str, Any]:
    """Los hechos de un aviso de la escalera, leídos en este momento sobre lo fijo de `base`:
    cuánto falta o cuánto atraso hay, el estado, la previsión vigente con el estado de su
    aviso, lo que depende de la tarea y, en el último pedido, a quién se escala."""
    vence = tarea["fecha_objetivo"]
    hechos = {k: v for k, v in base.items()
              if k not in _DE_ESTE_MOMENTO and k != AVISA_QUE_VA_A_ESCALAR}
    hechos.update(tarea=tarea["titulo"], vence=m.fecha(vence).isoformat())
    if m.hoy < m.fecha(vence):
        hechos["dias_habiles_hasta_el_vencimiento"] = m.cal.habiles_entre(m.ahora, vence)
    else:
        hechos["atraso_dias_habiles"] = m.cal.habiles_entre(vence, m.ahora)
    if tipo != "aviso_previo":
        hechos["estado"] = tarea["estado"]
    if tipo == "escalamiento":
        responsable = integrante(m.cur, tarea["responsable_membership_id"])
        hechos["responsable"] = responsable["nombre"] if responsable else None
    prevision = prevision_vigente(m, tarea)
    if prevision is not None:
        hechos["prevision_vigente"] = prevision
    if tipo != "aviso_previo":
        siguen = dependientes(m.cur, tarea["id"])
        if siguen:
            hechos["dependientes"] = siguen
    if tipo == VENCIMIENTO_CON_PREVISION:   # un efecto que pasa después: cuándo pide el estado
        hasta = ancla(m.cur, tarea["id"], m.fecha(vence))
        hechos["pide_el_estado_el"] = {"fecha": hasta.isoformat(), "estado": "todavia_no"}
    if base.get(AVISA_QUE_VA_A_ESCALAR):
        a_quienes = [d["nombre"] for d in quienes_escalan(m.cur, tarea)]
        if a_quienes:       # un efecto que pasa después: todavía no, y a quién
            hechos["si_no_hay_respuesta"] = {"se_avisa_a": a_quienes, "estado": "todavia_no"}
    return hechos


def _vigencia_de_la_escalera(m: Momento, aviso) -> tuple[str | None, dict[str, Any]]:
    tarea = leer_tarea(m.cur, aviso["task_id"])
    if tarea is None:
        return "tarea_inexistente", {}
    if tarea["estado"] in ("terminada", "cancelada"):
        return "tarea_cerrada", {}
    if tarea["estado"] == "en_revision":
        return "tarea_entregada", {}
    if tarea["bloqueada"] or tarea["estado"] == "bloqueada":
        return "bloqueo_abierto", {}
    if tarea["fecha_objetivo"] is None or \
            m.fecha(tarea["fecha_objetivo"]).isoformat() != aviso["hechos"].get("vence"):
        return "cambio_el_vencimiento", {}
    if aviso["tipo"] != "escalamiento" and \
            str(tarea["responsable_membership_id"]) != str(aviso["destinatario_membership_id"]):
        return "cambio_el_responsable", {}
    if aviso["tipo"] == "aviso_previo" and m.hoy >= m.fecha(tarea["fecha_objetivo"]):
        return "ya_vencio", {}      # un aviso previo que llega al vencimiento ya no es previo
    base = dict(aviso["hechos"])
    if base.get("necesita_respuesta") is True or aviso["tipo"] == "escalamiento":
        if espera_abierta(m.cur, tarea["id"]) is None:
            return "ya_respondio", {}
    # El ancla (9i): un paso de la escalera de otro anclaje ya no corresponde (si la persona
    # contestó, el motivo es ése); el recordatorio del vencimiento, sólo mientras el ancla
    # siga en una previsión posterior; el aviso previo, mientras siga en la fecha comprometida.
    de = anclaje(m.cur, tarea["id"], m.fecha(tarea["fecha_objetivo"]))
    if aviso["tipo"] == VENCIMIENTO_CON_PREVISION:
        if de.fecha <= fecha_de_la_clave(aviso):
            return "volvio_a_la_fecha_comprometida", {}
    elif aviso["tipo"] == "aviso_previo":
        if de.fecha != fecha_de_la_clave(aviso):
            return "hay_una_prevision_mas_nueva", {}
    elif clave_del_anclaje(aviso) not in de.claves:
        return "hay_una_prevision_mas_nueva", {}
    return None, hechos_de_la_escalera(m, aviso["tipo"], tarea, base)


# --- Los avisos de la escalera de una pregunta ---------------------------------------------------
#
# Una pregunta que espera respuesta y no la tuvo (`escalera.py`): Leda la repite, con lo que se
# había anotado y la pregunta, y al final escala. Ya no corresponden si la pregunta se cerró o
# su espera se contestó, o si la tarea se cerró o cambió de responsable.

def hechos_de_una_pregunta(m: Momento, tarea: dict[str, Any],
                           base: dict[str, Any]) -> dict[str, Any]:
    """Lo fijo de `base` (qué aviso es, la pregunta, el número, lo que se había anotado) y lo
    de este momento: la tarea y, en la última repregunta, a quién se escala."""
    hechos = {k: v for k, v in base.items()
              if k not in _DE_ESTE_MOMENTO and k != AVISA_QUE_VA_A_ESCALAR}
    hechos["tarea"] = tarea["titulo"]
    if tarea.get("bloqueada"):
        hechos["estado"] = "bloqueada"
    if base.get(AVISA_QUE_VA_A_ESCALAR):
        a_quienes = [d["nombre"] for d in quienes_escalan(m.cur, tarea)]
        if a_quienes:       # un efecto que pasa después: todavía no, y a quién
            hechos["si_no_hay_respuesta"] = {"se_avisa_a": a_quienes, "estado": "todavia_no"}
    if base.get("aviso") == "falta_de_respuesta":
        responsable = integrante(m.cur, tarea["responsable_membership_id"])
        hechos["responsable"] = responsable["nombre"] if responsable else None
    return hechos


def _vigencia_de_una_pregunta(m: Momento, aviso) -> tuple[str | None, dict[str, Any]]:
    tarea = leer_tarea(m.cur, aviso["task_id"])
    if tarea is None:
        return "tarea_inexistente", {}
    if tarea["estado"] in ("terminada", "cancelada"):
        return "tarea_cerrada", {}
    pregunta = pregunta_del_aviso(m.cur, aviso)
    if pregunta is None or pregunta["cerrada_en"] is not None:
        return "ya_respondio", {}
    if str(tarea["responsable_membership_id"]) != str(pregunta["membership_id"]):
        return "cambio_el_responsable", {}
    if espera_de_la_pregunta(m.cur, pregunta) is None:
        return "ya_respondio", {}
    return None, hechos_de_una_pregunta(m, tarea, dict(aviso["hechos"]))


# --- Los avisos de una previsión ---------------------------------------------------------------

def _vigencia_de_la_prevision(m: Momento, aviso) -> tuple[str | None, dict[str, Any]]:
    """El aviso al referente de una previsión (`nueva_prevision`) o de su corrección
    (`correccion_de_prevision`) corresponde mientras la previsión que lo causó (la última
    parte de su clave) sea la vigente: si después hubo otra, ésa trae su propio aviso, o
    ninguno si volvió a la fecha comprometida (9b). Sus hechos son los de la previsión, que no
    cambian."""
    tarea = leer_tarea(m.cur, aviso["task_id"])
    if tarea is None or tarea["estado"] in ("terminada", "cancelada"):
        return "tarea_cerrada", {}
    m.cur.execute("""select f.id, f.fecha_prevista, f.fecha_comprometida from task_forecast f
                      where f.task_id = %s
                        and not exists (select 1 from task_forecast g where g.reemplaza_id = f.id)
                      order by f.at desc limit 1""", (str(tarea["id"]),))
    vigente = m.cur.fetchone()
    if vigente is None or str(vigente["id"]) != aviso["dedupe_key"].rsplit(":", 1)[-1]:
        return "hay_una_prevision_mas_nueva", {}
    if aviso["tipo"] == "nueva_prevision" and \
            vigente["fecha_prevista"] == m.fecha(vigente["fecha_comprometida"]):
        return "volvio_a_la_fecha_comprometida", {}
    return None, dict(aviso["hechos"])


def _siempre(m: Momento, aviso) -> tuple[str | None, dict[str, Any]]:
    return None, dict(aviso["hechos"])


TIPOS: Mapping[str, TipoDeAviso] = MappingProxyType({t.nombre: t for t in (
    # La escalera (mecánica §9; 9b): sin botones, siempre privados.
    TipoDeAviso("aviso_previo", "informativo", _vigencia_de_la_escalera),
    # Con el ancla en una previsión, el único aviso del vencimiento: no pide nada (9i).
    TipoDeAviso(VENCIMIENTO_CON_PREVISION, "informativo", _vigencia_de_la_escalera),
    TipoDeAviso("pedido_de_estado", "seguimiento", _vigencia_de_la_escalera),
    TipoDeAviso("reencuadre", "seguimiento", _vigencia_de_la_escalera),
    TipoDeAviso("escalamiento", "prioritario", _vigencia_de_la_escalera, escala=True),
    # Después de un avance sin un hecho cierto, el pedido del día hábil siguiente.
    TipoDeAviso(REPREGUNTA_DE_ESTADO, "seguimiento", _vigencia_de_la_escalera),
    # La escalera de una pregunta que espera respuesta: la pregunta otra vez y su escalamiento.
    TipoDeAviso(REPREGUNTA, "seguimiento", _vigencia_de_una_pregunta),
    TipoDeAviso(ESCALAMIENTO_DE_UNA_PREGUNTA, "prioritario", _vigencia_de_una_pregunta,
                escala=True),
    # Lo que causa el acto de una persona: llega aunque se haya alcanzado el tope (§10).
    TipoDeAviso("nueva_prevision", "normal", _vigencia_de_la_prevision, es_coordinacion=True),
    TipoDeAviso("correccion_de_prevision", "normal", _vigencia_de_la_prevision,
                es_coordinacion=True),
    TipoDeAviso("falla_de_aviso", "informativo", _siempre, es_coordinacion=True),
)})


def _json(valor: Any) -> str:
    return json.dumps(valor, ensure_ascii=False, default=str)

