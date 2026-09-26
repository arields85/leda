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
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import psycopg

from . import herramientas as H
from . import pendientes as P
from .autoridad import Denegado, Solicitante
from .calendario import Calendario
from .contexto import construir, historial, revisar_salida
from .db import registrar_auditoria
from .llm import Llamada, Proveedor, Respuesta
from .salida import (BUTTON_TEXT_LIMIT, enqueue_outbox, normalize_visible_text,
                     prepare_payload, telegram_utf16_units,
                     truncar_etiqueta_boton, with_no_effect_status)

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
              entrante_id: str | None = None,
              modificacion: P.ModificacionAbierta | None = None,
              contexto_referencias: str | None = None,
              tareas_resueltas_claras: dict[str, str] | None = None) -> Resultado:
    """`modificacion`, si viene, es la propuesta anterior que la persona pidió
    corregir (T3, ADR 0005 decisión 1): se agrega al sistema como contexto de
    confianza del servidor, nunca como texto de la persona, para que el
    modelo pueda volver a llamar a la herramienta con los argumentos
    corregidos. Si el mensaje resulta ser sobre otra cosa, no se hace nada
    especial: la propuesta anterior sigue cerrada.

    `contexto_referencias`, si viene, es el resultado de resolver contra las
    tareas del espacio las referencias que separó `route_intent`
    (`gateway._turno`, T3 de `aclaracion-con-botones`, ADR 0005 decisión 6 /
    ADR 0006): igual que `modificacion`, es contexto de confianza del
    servidor, nunca texto de la persona.

    `tareas_resueltas_claras`, si viene, mapea id de tarea a título por cada
    tarea que este turno resolvió CLARA vía Jev (T3) o por botón (T4). Es la
    protección determinística de las lecturas (T5, ADR 0006, "toda respuesta
    nombra la tarea por su título"): un prompt no es garantía, así que además
    de la instrucción en el sistema, al cerrar el turno con una respuesta
    visible se comprueba que esa respuesta nombre por su título exacto cada
    una de estas tareas -- si no la nombra, se antepone una línea neutra con
    el título, para que la persona note si Prisma entendió otra tarea.

    Revisión del orquestador sobre la primera versión de esta unidad: la
    condición original exigía además que `consultar_tareas` hubiera devuelto
    la tarea en el mismo turno, así que una respuesta armada con otro
    contexto (p. ej. el bloque de "tareas abiertas" que ya trae
    `contexto.construir`, o cualquier otra herramienta) quedaba sin proteger.
    La comprobación ya no depende de qué herramienta corrió, ni de que haya
    corrido alguna."""
    ahora = ahora or datetime.now(timezone.utc)
    ctx = construir(cur, quien, texto_entrante, ahora=ahora)
    sistema = ctx.sistema
    if contexto_referencias:
        sistema = sistema + "\n\n---\n\n" + contexto_referencias
    if modificacion is not None:
        sistema = sistema + "\n\n---\n\n" + _bloque_modificacion(modificacion)
    esquemas = H.esquemas()

    # Lo que se dijeron hace un rato. `entrante_id` es la fila que el gateway
    # ya guardó de este mismo mensaje: sin excluirla, viajaría dos veces.
    mensajes: list[dict] = historial(cur, chat_id, ahora, entrante_id)
    mensajes.append({"role": "user", "content": texto_entrante})
    acciones: list[str] = []
    confirmaciones: list[str] = []
    elecciones: list[str] = []
    intentos_mutacion: list[str] = []
    # T3 (ADR 0007 punto 3): filas de la ÚLTIMA llamada a `consultar_tareas`
    # de este turno que devolvió alguna -- se sobrescribe sólo cuando hay
    # filas, así que si varias llamadas ocurren en el mismo turno, gana la
    # última que trajo algo, no la última llamada a secas. Vacía si ninguna
    # trajo filas.
    ultima_lista_tareas: list[dict] = []
    salida = ""
    cerro = False

    try:
        for _ in range(MAX_VUELTAS):
            r: Respuesta = proveedor.responder(sistema, mensajes, esquemas)
            # Vale el texto de esta vuelta y nada más. Arrastrar el de una
            # anterior manda "voy a crear la tarea" como respuesta final.
            salida = r.texto

            if not r.llamadas:
                cerro = True
                break

            mensajes.append({"role": "assistant", "content": _bloques(r)})
            resultados = []
            for c in r.llamadas:
                if not c.nombre.startswith("consultar_"):
                    intentos_mutacion.append(c.nombre)
                resultados.append(
                    _ejecutar_una(cur, quien, c, ctx, acciones, confirmaciones,
                                  elecciones, ultima_lista_tareas, chat_id, cal,
                                  ahora, entrante_id, texto_entrante))
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

    salida = normalize_visible_text(
        revisar_salida(salida, ctx.variantes_prohibidas))
    salida = _nombrar_tareas_sin_mencionar(salida, tareas_resueltas_claras)
    if intentos_mutacion and not any(
            not accion.startswith("consultar_") for accion in acciones):
        salida = with_no_effect_status(salida)
    # T3 (ADR 0007 punto 3): el servidor, no el modelo, garantiza que una
    # lista de tareas salga como botones. Llegar acá ya descartó que el turno
    # haya terminado con otro juego de botones (confirmaciones/elecciones
    # cerraron antes, línea ~161) -- nunca compite con ellos.
    if ultima_lista_tareas:
        _encolar_respuesta_con_tareas(cur, quien, chat_id, salida,
                                      ultima_lista_tareas, ahora)
    else:
        _encolar_respuesta(cur, quien, chat_id, salida, cal, ahora)
    auditar(salida)

    return Resultado(salida, acciones, confirmaciones, elecciones=elecciones)


def _normalizar_comparacion(texto: str) -> str:
    """Minúsculas, sin acentos, espacios colapsados -- para comparar si un
    título aparece en la respuesta sin importar cómo lo escribió el modelo
    (T5)."""
    sin_acentos = unicodedata.normalize("NFKD", texto)
    sin_acentos = "".join(c for c in sin_acentos if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sin_acentos).strip().casefold()


def _nombrar_tareas_sin_mencionar(
        texto: str, tareas_resueltas_claras: dict[str, str] | None) -> str:
    """Protección determinística de las lecturas (T5, ADR 0006): el prompt
    del sistema ya le pide al modelo nombrar la tarea por su título, pero un
    prompt no es garantía. Acá se comprueba de verdad: por cada tarea que
    este turno resolvió CLARA (`tareas_resueltas_claras`, id → título, T3/T4),
    si su título exacto no aparece en la respuesta visible, se antepone una
    línea neutra que lo nombra -- así la persona nota si Prisma entendió otra
    tarea. No importa qué herramienta corrió, ni si corrió alguna: una
    respuesta armada con otro contexto (p. ej. "tareas abiertas" de
    `contexto.construir`) protege igual. No toca el resto del texto del
    modelo, y sólo se antepone lo que de verdad falta."""
    if not tareas_resueltas_claras:
        return texto
    comparable = _normalizar_comparacion(texto)
    faltantes = [titulo for titulo in tareas_resueltas_claras.values()
                if _normalizar_comparacion(titulo) not in comparable]
    if not faltantes:
        return texto
    encabezado = "\n".join(f"Sobre «{titulo}»:" for titulo in faltantes)
    return f"{encabezado}\n\n{texto}"


def _bloque_modificacion(m: P.ModificacionAbierta) -> str:
    """Contexto de confianza del servidor para un turno que corrige una
    propuesta anterior (T3). No es texto de la persona: si lo fuera, cualquier
    mensaje libre podría fingir ser una corrección."""
    return (
        "# Corrección a una propuesta anterior\n\n"
        "La persona apretó Modificar en la vista previa de abajo, así que esa "
        "propuesta quedó cerrada y no se aplicó nada.\n\n"
        f"Herramienta: {m.herramienta}\n"
        f"Argumentos con los que se había llamado: "
        f"{json.dumps(m.args, ensure_ascii=False)}\n\n"
        f"Vista previa que se le había mostrado:\n{m.resumen}\n\n"
        "Su próximo mensaje, el que sigue en esta conversación, puede ser la "
        "corrección. Si de verdad se refiere a esto, volvé a llamar a la "
        "misma herramienta con los argumentos corregidos -- conservando los "
        "que no cambiaron -- para armar una vista previa nueva; eso tampoco "
        "aplica nada todavía. Si su mensaje es sobre otra cosa, no toques "
        "esta propuesta: ya quedó cerrada y no hay nada que retomar."
    )


def _bloques(r: Respuesta) -> list[dict]:
    bloques: list[dict] = []
    if r.texto:
        bloques.append({"type": "text", "text": r.texto})
    bloques += [{"type": "tool_use", "id": c.id, "name": c.nombre, "input": c.args}
                for c in r.llamadas]
    return bloques


def _ejecutar_una(cur, quien: Solicitante, c: Llamada, ctx, acciones,
                  confirmaciones, elecciones, ultima_lista_tareas, chat_id,
                  cal, ahora, entrante_id, texto_entrante) -> dict:
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
            resultado = H.ejecutar(cur, quien, c.nombre, c.args,
                                   chat_id=chat_id)
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
    except H.NecesitaOpciones as e:
        _encolar_opciones_modelo(cur, quien, chat_id, e, ahora)
        elecciones.append(c.nombre)
        return bloque({
            "ejecutado": False,
            "estado": "esperando que la persona elija entre las opciones",
            "aclaracion": "Ya le mostré los botones con la pregunta y la "
                          "salida. No preguntes de nuevo ni agregues más "
                          "texto: el turno termina acá."})
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

    if c.nombre == "consultar_tareas" and isinstance(resultado, list) and resultado:
        # T3 (ADR 0007 punto 3): se guarda para que `responder` arme los
        # botones de la lista con la última llamada que trajo filas -- se
        # sobrescribe adrede sólo cuando hay algo, nunca con una lista vacía.
        ultima_lista_tareas[:] = resultado

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
    enqueue_outbox(
        cur, workspace_id=quien.workspace_id, chat_id=chat_id, text=texto,
        recipient_membership_id=quien.membership_id, scheduled_for=ahora,
        dedupe_key=(f"{quien.workspace_id}:respuesta:{quien.app_user_id}:"
                    f"{ahora.timestamp()}"), is_response=True, allow_split=True,
    )


def _encolar_confirmacion(cur, quien: Solicitante, chat_id: int,
                          e: H.NecesitaConfirmacion, cal: Calendario,
                          ahora: datetime) -> None:
    """La acción no se ejecuta: queda congelada esperando el sí.

    Es la sección 7 de la constitución hecha una fila de tabla en vez de una
    promesa del modelo. La herramienta y sus argumentos se guardan enteros:
    sin eso, confirmar no tendría nada que ejecutar.
    """
    # Las 8 herramientas que escriben (las que declaran `preparar`, únicas
    # que llegan acá con huella) ganan el tercer botón, Modificar (T3, ADR
    # 0005 decisión 1). El resto de lo que pasa por `NecesitaConfirmacion`
    # -- hoy, `REQUIEREN_CONFIRMACION` sin `preparar`, que ninguna de las 8
    # usa -- mantiene sus dos botones de siempre: no tiene una preparación
    # que una corrección pueda volver a correr.
    opciones = ([("Confirmar", True), ("Modificar", "modificar"), ("Cancelar", False)]
               if e.huella is not None else None)
    p = P.registrar(cur, quien, herramienta=e.herramienta, args=e.argumentos,
                    resumen=e.resumen, vence_en=ahora + VIGENCIA_PENDIENTE,
                    chat_id=chat_id, huella=e.huella, opciones=opciones)
    # El resumen ya es la vista previa completa -- recurso, estado actual,
    # cambio propuesto y el aviso de que todavía no se aplicó nada (ADR 0005,
    # decisión 1) -- así que sale tal cual, sin envoltorio.
    enqueue_outbox(
        cur, workspace_id=quien.workspace_id, chat_id=chat_id,
        recipient_membership_id=quien.membership_id,
        text=e.resumen, scheduled_for=ahora,
        dedupe_key=(f"{quien.workspace_id}:confirmar:{e.herramienta}:"
                    f"{ahora.timestamp()}"), is_response=True,
        pending_action_id=p.id,
    )


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
    enqueue_outbox(
        cur, workspace_id=quien.workspace_id, chat_id=chat_id,
        recipient_membership_id=quien.membership_id, text=e.resumen,
        scheduled_for=ahora,
        dedupe_key=(f"{quien.workspace_id}:elegir:{e.herramienta}:"
                    f"{ahora.timestamp()}"), is_response=True,
        pending_action_id=p.id,
    )


def _encolar_opciones_modelo(cur, quien: Solicitante, chat_id: int,
                             e: H.NecesitaOpciones, ahora: datetime) -> None:
    """El modelo pidió una elección con `ofrecer_opciones` (T1, ADR 0007):
    arma los botones con la salida de siempre y termina el turno -- a
    diferencia de `_encolar_eleccion`, tocar una opción no vuelve a llamar a
    la herramienta: retoma la conversación en
    `gateway._resolver_toque_opcion_modelo`, con el sentinel compartido en
    `pendientes.SENTINEL_OPCIONES_MODELO`.
    """
    opciones = [(o.etiqueta, o.valor) for o in e.opciones]
    opciones.append((P.ETIQUETA_SALIR_OPCIONES, {"tipo": "salida"}))
    p = P.registrar(cur, quien, herramienta=P.SENTINEL_OPCIONES_MODELO,
                    args={"pregunta": e.pregunta}, resumen=e.pregunta,
                    vence_en=ahora + VIGENCIA_PENDIENTE, campo="eleccion",
                    opciones=opciones, chat_id=chat_id)
    enqueue_outbox(
        cur, workspace_id=quien.workspace_id, chat_id=chat_id,
        recipient_membership_id=quien.membership_id, text=p.resumen,
        scheduled_for=ahora,
        dedupe_key=(f"{quien.workspace_id}:opciones:{quien.app_user_id}:"
                   f"{ahora.timestamp()}"), is_response=True,
        pending_action_id=p.id,
    )


def _opciones_lista_tareas(tareas: list[dict]) -> list[tuple[str, dict]]:
    """Botones de la primera página de una lista de tareas (T3, ADR 0007
    punto 3): hasta `H.MAX_OPCIONES_MODELO` tareas, en el orden que ya trajo
    `consultar_tareas` (`fecha_objetivo`). Cada tarea usa la misma forma de
    valor que una opción de tarea de `ofrecer_opciones` (T1) con
    `accion: "menu"` -- tocarla abre el menú de T2 sin retomar la
    conversación --, así que `gateway._resolver_toque_opcion_modelo` no
    necesita distinguir de dónde salió la opción. Si quedan más de
    `H.MAX_OPCIONES_MODELO`, agrega "Ver más" con los ids restantes, en el
    mismo orden, para que `gateway._mostrar_mas_tareas` arme la página
    siguiente sin llamar al modelo."""
    primera = tareas[:H.MAX_OPCIONES_MODELO]
    resto = tareas[H.MAX_OPCIONES_MODELO:]
    opciones = [
        (truncar_etiqueta_boton(normalize_visible_text(t["titulo"])),
         {"tipo": "tarea", "tarea_id": str(t["id"]), "titulo": t["titulo"],
          "accion": "menu"})
        for t in primera]
    if resto:
        opciones.append((P.ETIQUETA_VER_MAS,
                         {"tipo": "ver_mas",
                          "tarea_ids": [str(t["id"]) for t in resto]}))
    return opciones


_TEXTO_BOTONES_LISTA_TAREAS = "Elegí una tarea:"


def _encolar_respuesta_con_tareas(cur, quien: Solicitante, chat_id: int,
                                  texto: str, tareas: list[dict],
                                  ahora: datetime) -> None:
    """T3 (ADR 0007 punto 3): el servidor, no el modelo, garantiza que una
    lista de tareas salga como botones -- reusando el mecanismo de T1
    (`pendientes.SENTINEL_OPCIONES_MODELO`): tocar una tarea abre su menú
    (T2), tocar "Ver más" pagina en `gateway._mostrar_mas_tareas` sin volver a
    llamar al modelo, y siempre queda la salida de siempre. Costo aceptado
    (decisión del usuario): una respuesta que sólo dio un conteo también
    lleva estos botones.

    Corrección tras revisión del orquestador sobre T3: un mensaje con
    botones nunca se parte y no puede superar `BUTTON_TEXT_LIMIT`
    (`salida.prepare_payload`) -- mandar el texto del modelo CON los botones,
    como hacía la primera versión, levantaba `PayloadValidationError` en
    cuanto la respuesta pasaba ese límite, y la persona se quedaba con el
    aviso neutro de incidente en vez de su lista. Antes de T3, esa misma
    respuesta iba por `_encolar_respuesta`, que sí parte.

    `pendientes.registrar` valida el `resumen` que se le pasa contra
    `BUTTON_TEXT_LIMIT` sin excepción -- es el texto que se manda junto con
    estos botones, así que no alcanza con decidir el mensaje DESPUÉS de
    registrar la `pending_action`: el texto largo tiene que quedar afuera de
    `resumen` desde antes de llamar a `registrar`, o la excepción salta ahí
    mismo (así fallaba la primera versión de esta corrección, que sólo movía
    la decisión a `enqueue_outbox` y seguía pasando el texto completo como
    `resumen`). Por eso la decisión se toma primero, sobre `texto`: si entra
    en `BUTTON_TEXT_LIMIT` (normalizado, medido con la misma regla UTF-16 de
    `prepare_payload`), `resumen` es el texto del modelo y todo sigue como
    siempre (botones en el mismo mensaje). Si no entra, `resumen` pasa a ser
    `_TEXTO_BOTONES_LISTA_TAREAS`, un texto corto fijo que sí entra siempre; el
    texto completo del modelo sale aparte, ANTES, partido exactamente como lo
    partiría `_encolar_respuesta`. El mensaje de botones se programa después
    de la ÚLTIMA parte del texto (`programado_para`, lo único que ordena
    `despachador.despachar`) para que la entrega quede determinística: el
    texto primero -- todas sus partes, en orden -- y los botones después,
    nunca al revés (corrección sobre el defecto de partes con la misma marca,
    revisión del orquestador del 2026-09-26: ver comentario en la llamada de
    abajo y en `salida.enqueue_outbox`).

    `args={"pregunta": texto}` guarda el texto completo del modelo pase lo
    que pase con `resumen` -- por consistencia con la forma que ya tiene
    `pending_action.args` para este sentinel (T1), aunque ninguna de las
    opciones de una lista de tareas lo lee: una tarea con `accion: "menu"`
    nunca retoma la conversación, y "Ver más"/la salida tampoco.
    """
    opciones = _opciones_lista_tareas(tareas)
    opciones.append((P.ETIQUETA_SALIR_OPCIONES, {"tipo": "salida"}))

    cabe_con_botones = (
        telegram_utf16_units(normalize_visible_text(texto)) <= BUTTON_TEXT_LIMIT)
    resumen_botones = texto if cabe_con_botones else _TEXTO_BOTONES_LISTA_TAREAS

    p = P.registrar(cur, quien, herramienta=P.SENTINEL_OPCIONES_MODELO,
                    args={"pregunta": texto}, resumen=resumen_botones,
                    vence_en=ahora + VIGENCIA_PENDIENTE, campo="eleccion",
                    opciones=opciones, chat_id=chat_id)
    # El id de `p` (fresco por cada `registrar`) identifica el mensaje, no la
    # marca de tiempo -- misma lección que T2 (`agente.py:420-421`, revisión
    # del orquestador sobre T1).
    if cabe_con_botones:
        enqueue_outbox(
            cur, workspace_id=quien.workspace_id, chat_id=chat_id,
            recipient_membership_id=quien.membership_id, text=p.resumen,
            scheduled_for=ahora,
            dedupe_key=f"{quien.workspace_id}:lista-tareas:{p.id}",
            is_response=True, pending_action_id=p.id,
        )
        return

    dedupe_key_texto = f"{quien.workspace_id}:lista-tareas:{p.id}:texto"
    enqueue_outbox(
        cur, workspace_id=quien.workspace_id, chat_id=chat_id, text=texto,
        recipient_membership_id=quien.membership_id, scheduled_for=ahora,
        dedupe_key=dedupe_key_texto,
        is_response=True, allow_split=True,
    )
    # `enqueue_outbox` programa cada parte del texto en `ahora +
    # microsegundos(índice)` (0, 1, 2...) para que queden en orden estricto
    # entre sí (defecto de la revisión del orquestador del 2026-09-26: antes
    # todas las partes compartían la misma marca y el orden entre ellas
    # quedaba librado al azar del `id`, un uuid). Los botones tienen que ir
    # después de la ÚLTIMA parte, no de la primera -- `len(partes)`
    # microsegundos alcanza porque las partes ocupan los índices
    # `0..len(partes)-1`. `partes` se recalcula acá con el mismo texto y la
    # misma `dedupe_key` que la llamada de arriba (`prepare_payload` es
    # determinística, ya probado en `test_ordinary_payload_split_is_
    # deterministic_and_dedupe_safe`) sólo para contar cuántas partes salen:
    # `enqueue_outbox` devuelve filas efectivamente insertadas, no partes,
    # porque otras llamadas (`escalera.encolar`, etc.) suman ese número para
    # saber cuánto entregaron de verdad pese al `on conflict (dedupe_key) do
    # nothing`, y ese conteo tiene que seguir reflejando inserciones reales.
    partes = prepare_payload(texto, dedupe_key=dedupe_key_texto, allow_split=True)
    enqueue_outbox(
        cur, workspace_id=quien.workspace_id, chat_id=chat_id,
        recipient_membership_id=quien.membership_id, text=p.resumen,
        scheduled_for=ahora + timedelta(microseconds=len(partes)),
        dedupe_key=f"{quien.workspace_id}:lista-tareas:{p.id}:botones",
        is_response=True, pending_action_id=p.id,
    )


def _incidente(cur, quien: Solicitante, error: Exception) -> None:
    """Registro sanitizado. Al integrante no le llega nada de esto."""
    cur.execute(
        """insert into incident (workspace_id, severidad, resumen_sanitizado,
                                 referencia_cruda)
           values (%s, 'media', %s, %s)""",
        (quien.workspace_id,
         f"Falló un turno de conversación ({type(error).__name__}).",
         str(error)[:2000]))
