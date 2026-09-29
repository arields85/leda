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
from .deteccion_pregunta import hace_pregunta
from .incidentes import registrar_incidente
from .llm import Llamada, Proveedor, Respuesta
from .salida import (ETIQUETA_CANCELAR, ETIQUETA_CONFIRMAR, cabe_en_mensaje,
                     enqueue_outbox, etiquetas_de_tarea,
                     normalize_visible_text, prepare_payload,
                     with_no_effect_status)

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
    # `elecciones` mezcla dos mecanismos distintos (T1 `NecesitaElegir` y
    # `NecesitaOpciones`, `ofrecer_opciones`) para no romper el contrato
    # externo de `Resultado.elecciones` -- `elegir_pendiente` distingue sólo
    # el primero, y `opciones_pendientes` guarda las excepciones del segundo,
    # para que este turno pueda decidir, recién al cerrar, si el texto del
    # modelo acompaña la pregunta (fix del orquestador, evidencia de banco
    # b-0001-a, ADR 0007 punto 2: "el texto da el contexto; la elección se
    # hace tocando" -- antes ese texto se descartaba entero).
    elegir_pendiente: list[str] = []
    opciones_pendientes: list[H.NecesitaOpciones] = []
    texto_al_ofrecer: str | None = None
    intentos_mutacion: list[str] = []
    # T3 (ADR 0007 punto 3; corregido por el hallazgo de sesión 2 del
    # 2026-09-27, evidencia en `audit_log`): unión deduplicada por id de
    # tarea de las filas de TODAS las llamadas a `consultar_tareas` de este
    # turno que devolvieron algo, en orden de primera aparición -- no sólo
    # las de la última llamada que trajo filas. Antes ("gana la última con
    # filas") un turno que arma una lista con varias consultas (una por
    # persona, por ejemplo) contestaba en el texto con todas las tareas pero
    # ofrecía en los botones sólo las de la última consulta. Vacía si
    # ninguna trajo filas.
    tareas_listadas: list[dict] = []
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
            antes_de_opciones = len(opciones_pendientes)
            pendientes_antes = (len(confirmaciones) + len(elegir_pendiente)
                                + len(opciones_pendientes))
            for c in r.llamadas:
                if not c.nombre.startswith("consultar_"):
                    intentos_mutacion.append(c.nombre)
                resultados.append(
                    _ejecutar_una(cur, quien, c, ctx, acciones, confirmaciones,
                                  elecciones, elegir_pendiente, opciones_pendientes,
                                  tareas_listadas, chat_id, cal,
                                  ahora, entrante_id, texto_entrante))
            if len(opciones_pendientes) > antes_de_opciones and texto_al_ofrecer is None:
                # El texto de ESTA vuelta -- la que llamó a `ofrecer_opciones`
                # --, no el de una vuelta posterior: el modelo suele repetir
                # "Listo, ahí tenés las opciones" después, y ese texto no
                # aporta nada (nunca describe qué pasó, el turno ya había
                # terminado para él).
                texto_al_ofrecer = salida
            mensajes.append({"role": "user", "content": resultados})
            if (len(confirmaciones) + len(elegir_pendiente)
                    + len(opciones_pendientes)) > pendientes_antes:
                # Esta vuelta dejó algo esperando a la persona (vista previa,
                # elección u `ofrecer_opciones`): el turno ya terminó, y el
                # resultado de la herramienta le dice al modelo que no agregue
                # nada. Otra llamada sólo produciría un texto que se descarta
                # más abajo (banco del 2026-09-28: 24 de 27 turnos, ~2,8 s
                # cada una). Un rechazo no registra nada pendiente, así que
                # sigue volviendo al modelo para que lo explique.
                break
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

    # Algo quedó esperando a la persona y ya salió (o sale acá abajo) el
    # mensaje que se lo pide, con sus botones.
    if confirmaciones or elecciones:
        texto_opciones = ""
        if opciones_pendientes and not confirmaciones and not elegir_pendiente:
            # La única interacción pendiente de todo el turno es
            # `ofrecer_opciones` (fix del orquestador, ADR 0007 punto 2): acá
            # sí se manda el texto del modelo, junto con la pregunta -- es
            # justo el lugar donde antes se anunciaba como hecho algo que no
            # se hizo (confirmación/`NecesitaElegir` pendiente), pero una
            # pregunta con opciones no anuncia nada: sólo da contexto. Mismas
            # protecciones de veracidad que la salida normal.
            texto_opciones = normalize_visible_text(
                revisar_salida(texto_al_ofrecer or "", ctx.variantes_prohibidas))
            texto_opciones = _nombrar_tareas_sin_mencionar(
                texto_opciones, tareas_resueltas_claras)
            # `ofrecer_opciones` en sí no es una mutación que haya fallado --
            # es la pregunta -- así que no cuenta para "se intentó cambiar
            # algo y no se aplicó nada".
            intentos_reales = [n for n in intentos_mutacion if n != "ofrecer_opciones"]
            if intentos_reales and not any(
                    not accion.startswith("consultar_") for accion in acciones):
                texto_opciones = with_no_effect_status(texto_opciones)
        if opciones_pendientes:
            # Se encola acá, recién ahora que se sabe si el resto del turno
            # dejó además una confirmación o un `NecesitaElegir` pendiente --
            # antes se encolaba apenas se atrapaba la excepción, sin poder
            # saberlo todavía. Se manda de todos modos aunque haya otra cosa
            # pendiente (T2, `test_retomar_con_un_cambio_sigue_pidiendo_
            # confirmar`): lo único que cambia es si lleva texto.
            _encolar_opciones_modelo(cur, quien, chat_id, opciones_pendientes[0],
                                     ahora, texto=texto_opciones)
        auditar(texto_opciones or salida)
        return Resultado(texto_opciones, acciones, confirmaciones, elecciones=elecciones)

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
    if tareas_listadas:
        _encolar_respuesta_con_tareas(cur, quien, chat_id, salida,
                                      tareas_listadas, ahora)
    elif hace_pregunta(salida):
        # T4b (ADR 0007, corrida real b-0007): el modelo cerró preguntando en
        # texto abierto sin ofrecer ningún botón propio -- el servidor agrega
        # el cierre genérico de tres botones (decisión del usuario,
        # 2026-09-26) en vez de dejar pasar la pregunta abierta. Nunca compite
        # con la lista de T3 (rama `elif`, no una condición aparte) ni con
        # confirmaciones/elecciones de una herramienta (ya cerraron el turno
        # antes, línea ~161).
        _encolar_opciones_genericas(cur, quien, chat_id, salida, ahora,
                                    entrante_id, texto_entrante)
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
                  confirmaciones, elecciones, elegir_pendiente,
                  opciones_pendientes, tareas_listadas, chat_id,
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
        elegir_pendiente.append(e.herramienta)
        return bloque({
            "ejecutado": False,
            "estado": "esperando que la persona elija entre las opciones",
            "opciones": [et for et, _ in e.opciones],
            "aclaracion": "Ya le mostré los botones. No elijas vos ni "
                          "supongas cuál era."})
    except H.NecesitaOpciones as e:
        if opciones_pendientes:
            # ADR 0007: un solo juego de botones por turno (`responder`
            # sólo encola `opciones_pendientes[0]`). Sin esta guarda, una
            # segunda llamada a `ofrecer_opciones` en el mismo turno
            # quedaba en `opciones_pendientes` sin encolarse nunca, pero el
            # modelo recibía el mismo texto de éxito que la primera --le
            # mentía diciéndole que ya se mostraron unos botones que en
            # realidad no se armaron. Ahora una llamada de más se rechaza
            # con la verdad, sin sumarse a `elecciones` ni a
            # `opciones_pendientes`: no cuenta como mostrada.
            return bloque({
                "ejecutado": False,
                "explicacion": "ya ofreciste opciones en este turno; no se "
                              "mostraron estas",
                "aclaracion": "Sólo se puede mostrar un juego de botones por "
                              "turno. No lo anuncies como hecho ni supongas "
                              "que la persona las vio."}, error=True)
        # No se encola acá (fix del orquestador, evidencia de banco
        # b-0001-a): recién `responder`, al cerrar el turno completo, sabe
        # si además queda una confirmación o un `NecesitaElegir` pendiente
        # de otra herramienta -- de eso depende si el texto del modelo
        # acompaña esta pregunta. `elecciones` conserva su forma de siempre
        # (contrato externo de `Resultado.elecciones`, sin cambios).
        elecciones.append(c.nombre)
        opciones_pendientes.append(e)
        return bloque({
            "ejecutado": False,
            "estado": "esperando que la persona elija entre las opciones",
            "aclaracion": "Le voy a mostrar los botones con la pregunta y "
                          "la salida. No preguntes de nuevo ni agregues más "
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

    h = H.REGISTRO.get(c.nombre)
    if h is not None and h.preparar is not None and isinstance(resultado, dict):
        # `_ejecutar_una` nunca pasa `ya_confirmada` (queda en su default
        # `False`): con una herramienta que declara `preparar`,
        # `herramientas.ejecutar` sólo puede devolver acá sin excepción
        # cuando `preparar` encontró el mismo rechazo de negocio que
        # encontraría el handler (`if isinstance(prep, dict): return prep`)
        # -- con una preparación que sí puede seguir, siempre levanta
        # `NecesitaConfirmacion` antes de tocar el handler. No es un
        # heurístico sobre la forma del dict (`error`/`falta`): es la única
        # forma en la que un dict puede llegar hasta acá sin haber ejecutado
        # nada, así que no cuenta como acción ni se audita como tal
        # (evidencia de banco b-0005-a, ADR 0005 -- antes se auditaba
        # `herramienta:<nombre>` y se sumaba a `acciones` aunque no se
        # escribió ninguna fila).
        registrar_auditoria(
            cur, accion=f"herramienta_rechazada:{c.nombre}",
            workspace_id=quien.workspace_id,
            actor_app_user_id=quien.app_user_id, actor_kind="prisma",
            detalle={"args": c.args, "rechazo": resultado},
            pack_hash=ctx.pack_hash, nucleo_hash=ctx.nucleo_hash)
        return bloque({
            "ejecutado": False,
            "explicacion": resultado.get("error") or resultado.get("falta")
                          or "no se pudo completar esa operación",
            "aclaracion": "No se aplicó ningún cambio. No lo anuncies como "
                          "hecho."}, error=True)

    if c.nombre == "consultar_tareas" and isinstance(resultado, list) and resultado:
        # T3 (ADR 0007 punto 3; corregido por el hallazgo de sesión 2): se
        # acumula acá, sin repetir ninguna tarea que ya haya traído otra
        # llamada de este mismo turno, para que `responder` arme los botones
        # con la UNIÓN de todas las llamadas a `consultar_tareas` que
        # trajeron filas -- nunca sólo con la última. Nunca se agrega nada
        # con una lista vacía.
        ids_ya_listados = {str(t["id"]) for t in tareas_listadas}
        for t in resultado:
            if str(t["id"]) not in ids_ya_listados:
                tareas_listadas.append(t)
                ids_ya_listados.add(str(t["id"]))

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
    opciones = ([(ETIQUETA_CONFIRMAR, True), ("Modificar", "modificar"),
                (ETIQUETA_CANCELAR, False)]
               if e.huella is not None else None)
    # El resumen ya es la vista previa completa -- recurso, estado actual,
    # cambio propuesto y el aviso de que todavía no se aplicó nada (ADR 0005,
    # decisión 1) -- así que sale tal cual, sin envoltorio.
    p = P.registrar(cur, quien, herramienta=e.herramienta, args=e.argumentos,
                    resumen=e.resumen, vence_en=ahora + VIGENCIA_PENDIENTE,
                    chat_id=chat_id, huella=e.huella, opciones=opciones)
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
                             e: H.NecesitaOpciones, ahora: datetime,
                             texto: str = "") -> None:
    """El modelo pidió una elección con `ofrecer_opciones` (T1, ADR 0007):
    arma los botones con la pregunta y termina el turno -- a diferencia de
    `_encolar_eleccion`, tocar una opción no vuelve a llamar a la
    herramienta: retoma la conversación en
    `gateway._resolver_toque_opcion_modelo`, con el sentinel compartido en
    `pendientes.SENTINEL_OPCIONES_MODELO`.

    `texto`, si viene (fix del orquestador, ADR 0007 punto 2), es lo que el
    modelo escribió en la misma vuelta que llamó a `ofrecer_opciones` --
    `responder` ya decidió que es seguro mandarlo (nada más quedó pendiente
    en el turno) y ya le aplicó las mismas protecciones de veracidad que a
    cualquier salida. Va como contexto ANTES de la pregunta, en el mismo
    mensaje cuando entra en `BUTTON_TEXT_LIMIT`; si no entra, se reusa el
    mismo armado de T3a/T4b (`_encolar_texto_con_opciones`): el texto sale
    partido aparte, primero, y los botones -- con la pregunta sola como
    resumen corto -- después de la última parte. `args` sigue guardando sólo
    `{"pregunta": e.pregunta}`, igual que siempre: es lo único que lee
    `gateway._resolver_toque_opcion_modelo` al retomar.

    Si `texto` ya pregunta algo (`deteccion_pregunta.hace_pregunta`), no se le
    agrega encima `e.pregunta` (hallazgo 6, sesión 2 por Telegram,
    2026-09-27: "Hola Ismael. ¿Con qué te ayudo?\n\n¿Qué querés hacer?" --
    dos preguntas seguidas en el mismo mensaje). El texto del modelo ya
    introduce los botones; `e.pregunta` sigue guardada en `args` igual que
    siempre, para quien retoma el toque.

    Seguimiento de review-149a33fa ("pregunta suprimida"): esa supresión sólo
    tapaba el mensaje único (`texto_combinado` entra en `BUTTON_TEXT_LIMIT`).
    Si no entra, `_encolar_texto_con_opciones` parte `texto` aparte y manda
    `texto_corto` como resumen de los botones DESPUÉS -- pasarle siempre
    `e.pregunta` ahí reintroducía la segunda pregunta exactamente en el caso
    largo, deshaciendo el hallazgo 6 para cualquier texto que la disparara Y
    además superara el límite. `texto_corto` pasa a ser el genérico que ya usa
    `_encolar_opciones_genericas` (T4b, `_TEXTO_BOTONES_GENERICO`) cuando la
    pregunta ya se dijo -- reuso, no una redacción nueva.
    """
    opciones = [(o.etiqueta, o.valor) for o in e.opciones]
    opciones.append((P.ETIQUETA_SALIR_OPCIONES, {"tipo": "salida"}))
    pregunta_ya_dicha = bool(texto) and hace_pregunta(texto)
    if pregunta_ya_dicha:
        texto_combinado = texto
        texto_corto = _TEXTO_BOTONES_GENERICO
    else:
        texto_combinado = f"{texto}\n\n{e.pregunta}" if texto else e.pregunta
        texto_corto = e.pregunta
    _encolar_texto_con_opciones(
        cur, quien, chat_id, texto_combinado, opciones, ahora,
        dedupe_prefijo="opciones-modelo", texto_corto=texto_corto,
        args={"pregunta": e.pregunta})


def _opciones_lista_tareas(tareas: list[dict]) -> list[tuple[str, dict]]:
    """Botones de la primera página de una lista de tareas (T3, ADR 0007
    punto 3): hasta `H.MAX_OPCIONES_MODELO` tareas, en el orden de primera
    aparición de `tareas_listadas` -- la unión deduplicada, por id de tarea,
    de todas las llamadas a `consultar_tareas` del turno que trajeron filas
    (corregido por el hallazgo de sesión 2: antes era sólo el orden de la
    última llamada que trajo filas). Cada tarea usa la misma forma de
    valor que una opción de tarea de `ofrecer_opciones` (T1) con
    `accion: "menu"` -- tocarla abre el menú de T2 sin retomar la
    conversación --, así que `gateway._resolver_toque_opcion_modelo` no
    necesita distinguir de dónde salió la opción. Si quedan más de
    `H.MAX_OPCIONES_MODELO`, agrega "Ver más" con los ids restantes, en el
    mismo orden, para que `gateway._mostrar_mas_tareas` arme la página
    siguiente sin llamar al modelo."""
    primera = tareas[:H.MAX_OPCIONES_MODELO]
    resto = tareas[H.MAX_OPCIONES_MODELO:]
    # Etiquetas cortas por límite de palabra, distinguibles entre sí dentro
    # de esta página (hallazgo de sesión 2 por Telegram: un título completo
    # recortado a mitad de palabra no entra cómodo en un botón de teléfono;
    # `salida.etiquetas_de_tarea` corre `etiquetas_boton_distinguibles` sobre
    # TODA la página para que dos títulos parecidos nunca corten igual, y le
    # antepone el ícono de tarea con su mismo descuento de presupuesto --
    # receta única (R2-002, revisión 2026-09-28+1), antes copiada a mano acá.
    etiquetas = etiquetas_de_tarea(
        [normalize_visible_text(t["titulo"]) for t in primera])
    opciones = [
        (etiqueta,
         {"tipo": "tarea", "tarea_id": str(t["id"]), "titulo": t["titulo"],
          "accion": "menu"})
        for t, etiqueta in zip(primera, etiquetas)]
    if resto:
        opciones.append((P.ETIQUETA_VER_MAS,
                         {"tipo": "ver_mas",
                          "tarea_ids": [str(t["id"]) for t in resto]}))
    return opciones


_TEXTO_BOTONES_LISTA_TAREAS = "Elegí una tarea:"


def _encolar_texto_con_opciones(cur, quien: Solicitante, chat_id: int,
                                texto: str, opciones: list[tuple[str, dict]],
                                ahora: datetime, *, dedupe_prefijo: str,
                                texto_corto: str, args: dict) -> None:
    """Botones de T1 (`pendientes.SENTINEL_OPCIONES_MODELO`) junto con un
    texto que puede superar `BUTTON_TEXT_LIMIT` -- extraído de T3
    (revisión del orquestador sobre `_encolar_respuesta_con_tareas`, T3a)
    para que T4b (el cierre genérico de una pregunta sin opciones) reuse la
    misma decisión en vez de duplicarla.

    `pendientes.registrar` valida el `resumen` que se le pasa contra
    `BUTTON_TEXT_LIMIT` sin excepción -- es el texto que se manda junto con
    estos botones, así que no alcanza con decidir el mensaje DESPUÉS de
    registrar la `pending_action`: el texto largo tiene que quedar afuera de
    `resumen` desde antes de llamar a `registrar`, o la excepción salta ahí
    mismo. Por eso la decisión se toma primero, sobre `texto`: si entra en
    `BUTTON_TEXT_LIMIT` (normalizado, medido con la misma regla UTF-16 de
    `prepare_payload`), `resumen` es el texto tal cual y todo sigue como
    siempre (botones en el mismo mensaje). Si no entra, `resumen` pasa a ser
    `texto_corto` -- un texto corto fijo que sí entra siempre --; el texto
    completo sale aparte, ANTES, partido exactamente como lo partiría
    `_encolar_respuesta`. El mensaje de botones se programa después de la
    ÚLTIMA parte del texto (`programado_para`, lo único que ordena
    `despachador.despachar`) para que la entrega quede determinística: el
    texto primero -- todas sus partes, en orden -- y los botones después,
    nunca al revés.

    `dedupe_prefijo` distingue el mecanismo que llama (`lista-tareas`,
    `opciones-genericas`, `opciones-modelo`) para que las claves de una
    llamada nunca choquen con las de otra; `args` es lo que guarda
    `pending_action.args` (igual para las tres opciones de un mismo cierre,
    nunca algo por opción)."""
    opciones = list(opciones)
    # `cabe_en_mensaje` ya descuenta el margen del saludo diario (R4-001,
    # revisión 2026-09-28+3): comparar a mano contra `BUTTON_TEXT_LIMIT`
    # dejaba pasar un texto que `enqueue_outbox` rechazaba después, en todos
    # los reintentos -- este mensaje siempre es personal (`quien.
    # membership_id`, nunca uno de grupo).
    cabe_con_botones = cabe_en_mensaje(texto, has_buttons=True)
    resumen_botones = texto if cabe_con_botones else texto_corto

    p = P.registrar(cur, quien, herramienta=P.SENTINEL_OPCIONES_MODELO,
                    args=args, resumen=resumen_botones,
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
            dedupe_key=f"{quien.workspace_id}:{dedupe_prefijo}:{p.id}",
            is_response=True, pending_action_id=p.id,
        )
        return

    dedupe_key_texto = f"{quien.workspace_id}:{dedupe_prefijo}:{p.id}:texto"
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
        dedupe_key=f"{quien.workspace_id}:{dedupe_prefijo}:{p.id}:botones",
        is_response=True, pending_action_id=p.id,
    )


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

    `args={"pregunta": texto}` guarda el texto completo del modelo pase lo
    que pase con el `resumen` que arma `_encolar_texto_con_opciones` --por
    consistencia con la forma que ya tiene `pending_action.args` para este
    sentinel (T1), aunque ninguna de las opciones de una lista de tareas lo
    lee: una tarea con `accion: "menu"` nunca retoma la conversación, y "Ver
    más"/la salida tampoco.

    Corrección tras revisión del orquestador sobre T3: un mensaje con
    botones nunca se parte y no puede superar `BUTTON_TEXT_LIMIT`
    (`salida.prepare_payload`) -- mandar el texto del modelo CON los botones,
    como hacía la primera versión, levantaba `PayloadValidationError` en
    cuanto la respuesta pasaba ese límite. El armado (partir el texto largo
    aparte, botones después de la última parte) vive en
    `_encolar_texto_con_opciones` desde T4b, reusado acá tal cual.
    """
    opciones = _opciones_lista_tareas(tareas)
    opciones.append((P.ETIQUETA_SALIR_OPCIONES, {"tipo": "salida"}))
    _encolar_texto_con_opciones(
        cur, quien, chat_id, texto, opciones, ahora,
        dedupe_prefijo="lista-tareas", texto_corto=_TEXTO_BOTONES_LISTA_TAREAS,
        args={"pregunta": texto})


# T4b (ADR 0007, corrida real b-0007 del 2026-09-26): el cierre genérico
# cuando Prisma necesita algo de la persona pero termina el turno
# preguntando en texto abierto, sin ningún botón propio. Mismas etiquetas que
# ya usa "Es una tarea nueva" de la aclaración con botones (T4,
# `aclaracion-con-botones`) para la primera -- coincide a propósito, aunque
# viven en módulos distintos (`gateway._ETIQUETA_NUEVA` no se puede importar
# acá sin ciclo: `gateway.py` ya importa de `agente.py`).
_ETIQUETA_TAREA_NUEVA_GENERICA = "Es una tarea nueva"
_ETIQUETA_TAREA_EXISTENTE_GENERICA = "Es sobre una tarea existente"
_TEXTO_BOTONES_GENERICO = "Elegí una opción:"


def _encolar_opciones_genericas(cur, quien: Solicitante, chat_id: int,
                                texto: str, ahora: datetime,
                                entrante_id: str | None,
                                texto_entrante: str) -> None:
    """Decisión del usuario (2026-09-26, evidencia
    `tests/banco/reportes/replay-candidato-b-0007-*.json`): cuando Prisma
    necesita algo de la persona pero no tiene opciones concretas para
    ofrecer, el modelo debería llamar a `ofrecer_opciones` igual (regla
    reforzada en `contexto.PREAMBULO`) -- esto es la red de seguridad del
    servidor para cuando, aun así, el turno cierra preguntando en texto
    abierto: agrega un juego FIJO de tres botones en vez de dejar pasar la
    pregunta sin opciones (ADR 0007, "Prisma orienta, no charla", sin
    excepción). Reusa el mecanismo de T1
    (`pendientes.SENTINEL_OPCIONES_MODELO`): las tres opciones se resuelven
    en `gateway._resolver_toque_opcion_modelo` por su `tipo`
    (`tarea_nueva`/`tarea_existente`/`salida`), igual que "ver_mas"/"tarea"
    ya lo hacen.

    "Es una tarea nueva" arranca la misma alta guiada que ya usa la
    aclaración con botones (`gateway._iniciar_alta_guiada`) -- necesita el
    `inbound_message` y el texto que originaron esta pregunta, porque un
    toque no es un mensaje nuevo: viajan en `args` (`entrante_id`,
    `mensaje_original`), iguales para las tres opciones, nunca en una opción
    puntual. Sin `entrante_id` (el turno no vino de un mensaje persistido,
    p. ej. al retomar otra opción) el alta guiada lo nota y cierra con
    incidente + aviso neutro (`gateway._iniciar_alta_guiada`, patrón ya
    existente) -- nunca se inventa un mensaje de origen.

    "Es sobre una tarea existente" lista las tareas activas de la propia
    persona (`gateway._mostrar_tareas_propias`), con el mismo armado de
    página + "Ver más" que T3. La salida de siempre cierra sin efecto.

    Sin `entrante_id` (hallazgo del orquestador) "Es una tarea nueva" no se
    ofrece: `_iniciar_alta_guiada` exige un `inbound_message` persistido y,
    sin uno, siempre levanta `ValueError` antes de intentar nada -- no es un
    caso raro que a veces falla, es un botón que garantizado no hace lo que
    promete. Pasa, por ejemplo, al retomar una opción con un toque
    (`gateway._resolver_toque_opcion_modelo` llama a `responder` sin
    `entrante_id`): si esa segunda vuelta también cierra preguntando en
    texto abierto, sólo quedan las otras dos opciones."""
    opciones = []
    if entrante_id is not None:
        opciones.append((_ETIQUETA_TAREA_NUEVA_GENERICA, {"tipo": "tarea_nueva"}))
    opciones.append((_ETIQUETA_TAREA_EXISTENTE_GENERICA, {"tipo": "tarea_existente"}))
    opciones.append((P.ETIQUETA_SALIR_OPCIONES, {"tipo": "salida"}))
    _encolar_texto_con_opciones(
        cur, quien, chat_id, texto, opciones, ahora,
        dedupe_prefijo="opciones-genericas", texto_corto=_TEXTO_BOTONES_GENERICO,
        args={"pregunta": texto, "entrante_id": entrante_id,
             "mensaje_original": texto_entrante})


def _incidente(cur, quien: Solicitante, error: Exception) -> None:
    """Registro sanitizado. Al integrante no le llega nada de esto -- a la
    administración de plataforma sí (`incidentes.registrar_incidente`)."""
    registrar_incidente(
        cur, quien.workspace_id,
        f"Falló un turno de conversación ({type(error).__name__}).",
        referencia_cruda=str(error)[:2000], app_user_id=quien.app_user_id)
