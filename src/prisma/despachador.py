"""Despachador de la cola de salida.

Prisma nunca llama a Telegram: escribe en `message_outbox` y este worker
entrega. Eso da tres cosas de una sola vez:

  - idempotencia, porque la clave de deduplicación sobrevive a un reinicio;
  - confirmación humana, que es un estado de la misma tabla;
  - tope de mensajes por persona, que se aplica al despachar y no al generar,
    así se cuenta lo que efectivamente llega.

El transporte está detrás de una interfaz para poder probar todo el circuito
sin tocar Telegram.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import NamedTuple, Protocol

import psycopg

from .calendario import Calendario


class Boton(NamedTuple):
    etiqueta: str
    callback_data: str


class Entregado(NamedTuple):
    """Lo que se entregó. Es tupla para que `(chat_id, texto)` siga sirviendo."""
    chat_id: int
    texto: str
    botones: list[Boton]


class Transporte(Protocol):
    def enviar(self, chat_id: int, texto: str,
               botones: list[Boton] | None = None) -> int:
        """Devuelve el identificador del mensaje entregado."""


@dataclass
class TransporteDePrueba:
    enviados: list[Entregado] = field(default_factory=list)
    falla_en: set[int] = field(default_factory=set)

    def enviar(self, chat_id: int, texto: str,
               botones: list[Boton] | None = None) -> int:
        if chat_id in self.falla_en:
            raise ConnectionError(f"no se pudo entregar a {chat_id}")
        self.enviados.append(Entregado(chat_id, texto, list(botones or [])))
        return len(self.enviados)


class TransporteTelegram:
    def __init__(self, token: str, cliente=None) -> None:
        import httpx
        self._url = f"https://api.telegram.org/bot{token}/sendMessage"
        self._cliente = cliente or httpx.Client(timeout=15)

    def enviar(self, chat_id: int, texto: str,
               botones: list[Boton] | None = None) -> int:
        cuerpo: dict = {"chat_id": chat_id, "text": texto,
                        "disable_notification": False}
        if botones:
            # Uno por fila: las etiquetas son nombres de personas o frases
            # cortas, y en el teléfono dos por fila se cortan.
            cuerpo["reply_markup"] = {"inline_keyboard": [
                [{"text": b.etiqueta, "callback_data": b.callback_data}]
                for b in botones]}
        r = self._cliente.post(self._url, json=cuerpo)
        r.raise_for_status()
        return r.json()["result"]["message_id"]


def acusar_toque(token: str, callback_id: str, cliente=None) -> None:
    """Le avisa a Telegram que el toque de un botón llegó.

    **Es la única llamada a Telegram que no pasa por la cola, y tiene que
    seguir siéndolo.**

    La regla del proyecto es que Prisma escribe en `message_outbox` y un
    worker entrega. Eso da reintentos, auditoría e idempotencia, y vale para
    todo lo que Prisma le dice a una persona.

    Esto no es eso. Es un acuse del protocolo, entre máquinas: no aparece en
    el chat, nadie lo lee, y Telegram lo exige en un par de segundos o le deja
    el reloj girando a quien apretó. La cola corre cada treinta: por ahí no
    llega a tiempo.

    Lo que la limita, y lo que hay que sostener si mañana aparece otro caso
    parecido:

      - no lleva contenido: sólo dice "llegó";
      - no cambia nada en la base;
      - si falla, no se pierde trabajo — quien llama la ignora.

    Todo lo que la persona sí tiene que leer sigue saliendo por la cola.
    """
    import httpx

    cliente = cliente or httpx.Client(timeout=5)
    cliente.post(f"https://api.telegram.org/bot{token}/answerCallbackQuery",
                 json={"callback_query_id": callback_id})


MAX_INTENTOS = 5


def _botones(cur, m) -> list[Boton]:
    """Las opciones de la acción pendiente que el mensaje está preguntando.

    Se leen al despachar, no al encolar: entre que Prisma pregunta y el
    mensaje sale puede pasar tiempo, y lo que vale es lo vigente al entregar.
    """
    if not m["pending_action_id"]:
        return []

    from .pendientes import callback_data, opciones

    return [Boton(o.etiqueta, callback_data(o))
            for o in opciones(cur, m["pending_action_id"])]


def _preview_vigente(cur, m) -> bool:
    if not m["pending_action_id"]:
        return True
    cur.execute(
        """select p.estado, p.draft_id, p.membership_id,
                  p.vence_en > clock_timestamp() as no_vencida,
                  d.responsable_membership_id
             from pending_action p
             left join task_draft d on d.id = p.draft_id
            where p.id = %s
            for update of p""",
        (m["pending_action_id"],))
    accion = cur.fetchone()
    if not accion or accion["draft_id"] is None:
        return True
    cur.execute(
        """select destinatario.activo as destinatario_activo,
                  responsable.aprobador_membership_id as aprobador_actual
             from membership destinatario, membership responsable
            where destinatario.id = %s and responsable.id = %s
            for share of destinatario, responsable""",
        (accion["membership_id"], accion["responsable_membership_id"]))
    autoridad = cur.fetchone()
    if not autoridad:
        autoridad = {"destinatario_activo": False, "aprobador_actual": None}
    accion.update(autoridad)
    if accion["aprobador_actual"] is None:
        cur.execute(
            """select raiz.id
                 from membership raiz join rol r on r.id = raiz.rol_id
                where raiz.workspace_id = %s and raiz.activo
                  and r.autoridad_final
                for share of raiz""", (m["workspace_id"],))
        raiz = cur.fetchone()
        accion["aprobador_actual"] = raiz["id"] if raiz else None
    vigente = (
        accion["estado"] == "esperando"
        and accion["no_vencida"]
        and accion["destinatario_activo"]
        and accion["membership_id"] == accion["aprobador_actual"]
    )
    if vigente:
        return True
    cur.execute(
        """update pending_action set estado = 'vencida'
            where id = %s and estado = 'esperando'""",
        (m["pending_action_id"],))
    cur.execute("update message_outbox set estado = 'descartado' where id = %s",
                (m["id"],))
    return False


def _tope_diario(cur, workspace_id: str) -> int | None:
    cur.execute(
        "select valor from workspace_setting "
        "where workspace_id = %s and clave = 'limites_de_contacto'",
        (workspace_id,))
    fila = cur.fetchone()
    if not fila:
        return None
    valor = fila["valor"]
    if isinstance(valor, str):
        valor = json.loads(valor)
    return valor.get("max_mensajes_automaticos_por_persona_por_dia")


def despachar(cur: psycopg.Cursor, workspace_id: str, transporte: Transporte,
              cal: Calendario, ahora: datetime | None = None,
              lote: int = 50) -> dict[str, int]:
    ahora = ahora or datetime.now(timezone.utc)
    tope = _tope_diario(cur, workspace_id)
    resumen = {"enviados": 0, "pospuestos": 0, "fallidos": 0, "descartados": 0}

    cur.execute(
        """
        select id, workspace_id, chat_id, cuerpo, tipo,
               destinatario_membership_id, intentos,
               vence_en, es_respuesta, pending_action_id
          from message_outbox
         where workspace_id = %s
           and estado = 'listo'
           and programado_para <= %s
         order by programado_para
         limit %s
         for update skip locked
        """,
        (workspace_id, ahora, lote))
    pendientes = cur.fetchall()

    for m in pendientes:
        if not _preview_vigente(cur, m):
            resumen["descartados"] += 1
            continue
        # Contestarle a quien escribió no es "escribir fuera de horario", ni
        # cuenta contra el tope de mensajes automáticos: no es automático.
        if m["es_respuesta"]:
            try:
                tg_id = transporte.enviar(m["chat_id"], m["cuerpo"],
                                          _botones(cur, m))
            except Exception as e:  # noqa: BLE001
                _fallo(cur, workspace_id, m, e, cal, ahora)
                resumen["fallidos"] += 1
                continue
            cur.execute(
                """update message_outbox
                      set estado = 'enviado', enviado_en = %s, telegram_message_id = %s
                    where id = %s""",
                (ahora, tg_id, m["id"]))
            resumen["enviados"] += 1
            continue

        # Un mensaje de cadencia cuya ventana ya pasó no se manda tarde.
        if m["vence_en"] and m["vence_en"] < ahora:
            cur.execute(
                "update message_outbox set estado = 'descartado' where id = %s",
                (m["id"],))
            resumen["descartados"] += 1
            continue

        # Fuera de horario se pospone, no se descarta. La urgencia autorizada
        # es la única que sale igual.
        if m["tipo"] != "urgente" and not cal.en_horario(ahora):
            cur.execute(
                "update message_outbox set programado_para = %s where id = %s",
                (cal.dentro_de_jornada(ahora), m["id"]))
            resumen["pospuestos"] += 1
            continue

        if tope and m["destinatario_membership_id"] and _ya_recibio(
                cur, m["destinatario_membership_id"], ahora) >= tope:
            cur.execute(
                "update message_outbox set programado_para = %s where id = %s",
                (cal.dentro_de_jornada(cal.sumar_habiles(ahora, 1)), m["id"]))
            resumen["pospuestos"] += 1
            continue

        try:
            tg_id = transporte.enviar(m["chat_id"], m["cuerpo"],
                                      _botones(cur, m))
        except Exception as e:  # noqa: BLE001 — el error se registra, no se propaga
            _fallo(cur, workspace_id, m, e, cal, ahora)
            resumen["fallidos"] += 1
            continue

        cur.execute(
            """update message_outbox
                  set estado = 'enviado', enviado_en = %s, telegram_message_id = %s
                where id = %s""",
            (ahora, tg_id, m["id"]))
        resumen["enviados"] += 1

    return resumen


def _fallo(cur, workspace_id: str, m, error: Exception, cal: Calendario,
           ahora: datetime) -> None:
    intentos = m["intentos"] + 1
    estado = "fallido" if intentos >= MAX_INTENTOS else "listo"
    proximo = cal.dentro_de_jornada(ahora) if estado == "listo" else None
    cur.execute(
        """update message_outbox
              set intentos = %s, ultimo_error = %s, estado = %s,
                  programado_para = coalesce(%s, programado_para)
            where id = %s""",
        (intentos, str(error)[:500], estado, proximo, m["id"]))
    if estado == "fallido":
        cur.execute(
            """insert into incident (workspace_id, severidad, resumen_sanitizado)
               values (%s, 'alta', %s)""",
            (workspace_id,
             f"Un mensaje no se pudo entregar tras {MAX_INTENTOS} intentos."))


def _ya_recibio(cur, membership_id: str, ahora: datetime) -> int:
    """Cuántos mensajes automáticos le llegaron hoy a esta persona.

    El tope es por persona, no por espacio: alguien en tres equipos no debería
    recibir tres seguimientos el mismo día.
    """
    cur.execute(
        """
        select count(*) n
          from message_outbox o
          join membership m  on m.id = o.destinatario_membership_id
          join membership m2 on m2.app_user_id = m.app_user_id
         where m2.id = %s
           and o.estado = 'enviado'
           and o.enviado_en::date = %s
        """,
        (membership_id, ahora.date()))
    return cur.fetchone()["n"]


def confirmar(cur: psycopg.Cursor, outbox_id: str, app_user_id: str) -> bool:
    """Pasa un mensaje de 'esperando_confirmacion' a 'listo'.

    Las acciones que el núcleo obliga a confirmar entran a la cola en ese
    estado y no salen hasta que una persona las aprueba.
    """
    cur.execute(
        """update message_outbox
              set estado = 'listo', confirmado_por = %s, confirmado_en = now()
            where id = %s and estado = 'esperando_confirmacion'""",
        (app_user_id, outbox_id))
    return cur.rowcount > 0
