"""El turno del agente.

Un mensaje entra, Prisma piensa, y la respuesta sale por la cola. Nunca
directo a Telegram: eso mantiene la idempotencia, la confirmación humana y la
auditoría en un solo lugar.

El bucle es corto porque el trabajo de Prisma es acotado. Entiende el mensaje,
llama a herramientas validadas, y contesta. No navega, no programa, no decide
sola.

Tres cosas que este módulo garantiza pase lo que pase:

  - una acción denegada no toca la base y la persona recibe una explicación
    humana, sin detalles técnicos;
  - una acción que exige confirmación queda esperando en la cola, no se
    ejecuta;
  - si algo falla, el integrante recibe un mensaje genérico y el incidente
    queda registrado para el administrador.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import psycopg

from . import herramientas as H
from .autoridad import Denegado, Solicitante
from .calendario import Calendario
from .contexto import construir, historial, revisar_salida
from .db import registrar_auditoria
from .llm import Llamada, Proveedor, Respuesta

MAX_VUELTAS = 5

# Cuánto vale una pregunta con botones. Lo suficiente para contestar después
# de una reunión; no tanto como para que se conteste sobre un contexto que ya
# cambió.
VIGENCIA_PENDIENTE = timedelta(hours=8)

DISCULPA = ("Perdón, no pude completar la respuesta. Ya quedó registrado para "
            "que lo revisen.")


@dataclass
class Resultado:
    texto: str
    acciones: list[str]
    confirmaciones: list[str]
    incidente: bool = False
    elecciones: list[str] = field(default_factory=list)


INCOMPLETO = ("Me quedé a mitad de camino con esto. Lo dejo anotado para "
              "revisarlo; si es urgente, decímelo y lo retomamos.")


def responder(cur: psycopg.Cursor, quien: Solicitante, texto_entrante: str,
              proveedor: Proveedor, cal: Calendario, chat_id: int,
              ahora: datetime | None = None,
              entrante_id: str | None = None) -> Resultado:
    ahora = ahora or datetime.now(timezone.utc)
    ctx = construir(cur, quien, texto_entrante)
    esquemas = H.esquemas()

    # Lo que se dijeron hace un rato. `entrante_id` es la fila que el gateway
    # ya guardó de este mismo mensaje: sin excluirla, viajaría dos veces.
    mensajes: list[dict] = historial(cur, chat_id, ahora, entrante_id)
    mensajes.append({"role": "user", "content": texto_entrante})
    acciones: list[str] = []
    confirmaciones: list[str] = []
    elecciones: list[str] = []
    salida = ""
    cerro = False

    try:
        for _ in range(MAX_VUELTAS):
            r: Respuesta = proveedor.responder(ctx.sistema, mensajes, esquemas)
            # Vale el texto de esta vuelta y nada más. Arrastrar el de una
            # anterior manda "voy a crear la tarea" como respuesta final.
            salida = r.texto

            if not r.llamadas:
                cerro = True
                break

            mensajes.append({"role": "assistant", "content": _bloques(r)})
            resultados = []
            for c in r.llamadas:
                resultados.append(
                    _ejecutar_una(cur, quien, c, ctx, acciones, confirmaciones,
                                  elecciones, chat_id, cal, ahora))
            mensajes.append({"role": "user", "content": resultados})
    except Exception as e:  # noqa: BLE001
        _incidente(cur, quien, e)
        _encolar_respuesta(cur, quien, chat_id, DISCULPA, cal, ahora)
        return Resultado(DISCULPA, acciones, confirmaciones, incidente=True)

    def auditar(texto: str) -> None:
        registrar_auditoria(
            cur, accion="turno_agente", workspace_id=quien.workspace_id,
            actor_app_user_id=quien.app_user_id, actor_kind="persona",
            detalle={"acciones": acciones, "confirmaciones": confirmaciones,
                     "elecciones": elecciones, "dijo": texto},
            pack_hash=ctx.pack_hash, nucleo_hash=ctx.nucleo_hash)

    # Algo quedó esperando a la persona y ya salió el mensaje que se lo pide,
    # con sus botones. Lo que el modelo haya escrito además no se manda: es
    # justo el lugar donde anunciaría como hecho algo que no hizo. No alcanza
    # con pedírselo en el preámbulo — un modelo se distrae, una condición no.
    if confirmaciones or elecciones:
        auditar(salida)
        return Resultado("", acciones, confirmaciones, elecciones=elecciones)

    # Se acabaron las vueltas con herramientas todavía en curso: el modelo
    # nunca vio cómo terminó lo que pidió, así que su texto no describe nada
    # que haya pasado.
    if not cerro:
        _incidente(cur, quien, RuntimeError(
            f"El turno agotó {MAX_VUELTAS} vueltas sin cerrar."))
        _encolar_respuesta(cur, quien, chat_id, INCOMPLETO, cal, ahora)
        auditar(INCOMPLETO)
        return Resultado(INCOMPLETO, acciones, confirmaciones,
                         incidente=True, elecciones=elecciones)

    if not salida.strip():
        salida = "Anotado."

    salida = revisar_salida(salida, ctx.variantes_prohibidas)
    _encolar_respuesta(cur, quien, chat_id, salida, cal, ahora)
    auditar(salida)

    return Resultado(salida, acciones, confirmaciones, elecciones=elecciones)


def _bloques(r: Respuesta) -> list[dict]:
    bloques: list[dict] = []
    if r.texto:
        bloques.append({"type": "text", "text": r.texto})
    bloques += [{"type": "tool_use", "id": c.id, "name": c.nombre, "input": c.args}
                for c in r.llamadas]
    return bloques


def _ejecutar_una(cur, quien: Solicitante, c: Llamada, ctx, acciones,
                  confirmaciones, elecciones, chat_id, cal, ahora) -> dict:
    """Ejecuta una herramienta y devuelve el bloque de resultado para el modelo.

    Los rechazos no son excepciones que cortan el turno: son información que
    Prisma tiene que saber transmitir.
    """
    def bloque(contenido, error=False):
        return {"type": "tool_result", "tool_use_id": c.id,
                "content": json.dumps(contenido, default=str, ensure_ascii=False),
                "is_error": error}

    # Punto de retorno por herramienta: si una falla, se deshace sólo ella y
    # el turno puede seguir. Sin esto, un error deja la transacción abortada y
    # se cae hasta el registro del incidente.
    punto = cur.connection.transaction(force_rollback=False)
    try:
        with punto:
            resultado = H.ejecutar(cur, quien, c.nombre, c.args)
    except Denegado as e:
        return bloque({"permitido": False, "explicacion": str(e)}, error=True)
    except H.NecesitaConfirmacion as e:
        _encolar_confirmacion(cur, quien, chat_id, e, cal, ahora)
        confirmaciones.append(e.herramienta)
        return bloque({
            "ejecutado": False,
            "estado": "esperando confirmación de la persona",
            "aclaracion": "No lo anuncies como hecho. Pedile que confirme."})
    except H.NecesitaElegir as e:
        _encolar_eleccion(cur, quien, chat_id, e, ahora)
        elecciones.append(e.herramienta)
        return bloque({
            "ejecutado": False,
            "estado": "esperando que la persona elija entre las opciones",
            "opciones": [et for et, _ in e.opciones],
            "aclaracion": "Ya le mostré los botones. No elijas vos ni "
                          "supongas cuál era."})
    except psycopg.errors.RaiseException as e:
        # Una regla de la base rechazó la operación. El texto de esas
        # excepciones está escrito para ser leído por una persona.
        return bloque({"permitido": False,
                       "explicacion": str(e).split("\n")[0]}, error=True)
    except psycopg.Error as e:
        # Falla técnica: el modelo se entera de que no se pudo, sin detalles,
        # y el incidente queda para el administrador.
        _incidente(cur, quien, e)
        return bloque({"ejecutado": False,
                       "explicacion": "no se pudo completar esa operación"},
                      error=True)

    if isinstance(resultado, dict) and resultado.get("pendiente_revision"):
        confirmaciones.append(c.nombre)
        return bloque({
            "ejecutado": False,
            "estado": "esperando confirmación de la autoridad vigente",
            "aclaracion": "La vista previa ya se envió en privado. No lo "
                           "anuncies como hecho."})

    acciones.append(c.nombre)
    registrar_auditoria(
        cur, accion=f"herramienta:{c.nombre}", workspace_id=quien.workspace_id,
        actor_app_user_id=quien.app_user_id, actor_kind="prisma",
        detalle={"args": c.args}, pack_hash=ctx.pack_hash,
        nucleo_hash=ctx.nucleo_hash)
    return bloque(resultado)


def _encolar_respuesta(cur, quien: Solicitante, chat_id: int, texto: str,
                       cal: Calendario, ahora: datetime) -> None:
    cur.execute(
        """insert into message_outbox
             (workspace_id, chat_id, destinatario_membership_id, tipo, cuerpo,
              estado, programado_para, dedupe_key, es_respuesta)
           values (%s, %s, %s, 'normal', %s, 'listo', %s, %s, true)
           on conflict (dedupe_key) do nothing""",
        (quien.workspace_id, chat_id, quien.membership_id, texto, ahora,
         f"{quien.workspace_id}:respuesta:{quien.app_user_id}:{ahora.timestamp()}"))


def _encolar_confirmacion(cur, quien: Solicitante, chat_id: int,
                          e: H.NecesitaConfirmacion, cal: Calendario,
                          ahora: datetime) -> None:
    """La acción no se ejecuta: queda congelada esperando el sí.

    Es la sección 7 de la constitución hecha una fila de tabla en vez de una
    promesa del modelo. La herramienta y sus argumentos se guardan enteros:
    sin eso, confirmar no tendría nada que ejecutar.
    """
    from .pendientes import registrar

    p = registrar(cur, quien, herramienta=e.herramienta, args=e.argumentos,
                  resumen=e.resumen, vence_en=ahora + VIGENCIA_PENDIENTE,
                  chat_id=chat_id)
    cur.execute(
        """insert into message_outbox
             (workspace_id, chat_id, destinatario_membership_id, tipo, cuerpo,
              estado, programado_para, dedupe_key, es_respuesta,
              pending_action_id)
           values (%s, %s, %s, 'normal', %s, 'listo', %s, %s, true, %s)
           on conflict (dedupe_key) do nothing""",
        (quien.workspace_id, chat_id, quien.membership_id,
         f"Antes de hacerlo, confirmame: {e.resumen}",
         ahora,
         f"{quien.workspace_id}:confirmar:{e.herramienta}:{ahora.timestamp()}",
         p.id))


def _encolar_eleccion(cur, quien: Solicitante, chat_id: int,
                      e: H.NecesitaElegir, ahora: datetime) -> None:
    """Prisma pregunta con opciones y la acción espera la elección.

    La pregunta sale con botones porque lo que vuelve tiene que ser un
    identificador. Si la persona contestara escribiendo, habría que resolver
    el mismo nombre ambiguo otra vez.
    """
    from .pendientes import registrar

    p = registrar(cur, quien, herramienta=e.herramienta, args=e.argumentos,
                  resumen=e.resumen, vence_en=ahora + VIGENCIA_PENDIENTE,
                  campo=e.campo, opciones=e.opciones, chat_id=chat_id)
    cur.execute(
        """insert into message_outbox
             (workspace_id, chat_id, destinatario_membership_id, tipo, cuerpo,
              estado, programado_para, dedupe_key, es_respuesta,
              pending_action_id)
           values (%s, %s, %s, 'normal', %s, 'listo', %s, %s, true, %s)
           on conflict (dedupe_key) do nothing""",
        (quien.workspace_id, chat_id, quien.membership_id, e.resumen, ahora,
         f"{quien.workspace_id}:elegir:{e.herramienta}:{ahora.timestamp()}",
         p.id))


def _incidente(cur, quien: Solicitante, error: Exception) -> None:
    """Registro sanitizado. Al integrante no le llega nada de esto."""
    cur.execute(
        """insert into incident (workspace_id, severidad, resumen_sanitizado,
                                 referencia_cruda)
           values (%s, 'media', %s, %s)""",
        (quien.workspace_id,
         f"Falló un turno de conversación ({type(error).__name__}).",
         str(error)[:2000]))
