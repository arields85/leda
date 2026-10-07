"""Registro de incidentes y aviso a la administración de plataforma.

Constitución §10: "Los incidentes se registran sanitizados y se avisan al
administrador de plataforma por su canal." Hasta esta unidad (T28, decisión
del usuario, 2026-09-28) eso último no pasaba: cada módulo armaba su propio
`insert into incident` a mano y sólo la persona afectada se enteraba
(`gateway.NOTICIA_NEUTRA_INCIDENTE`) -- quien administra la plataforma recién
se enteraba corriendo `python -m leda incidentes <slug>`.

`registrar_incidente` es el punto único de escritura en `incident`: inserta
la fila y, en la misma llamada, encola un aviso para cada administrador de
plataforma que tenga el bot de administración vinculado. El fan-out corre del
lado de la base (`avisar_incidente_admin`, `security definer`, migración
0017): necesita leer `platform_role` y `audit_log`, sin concesión de lectura
a `leda_app`.

El texto del aviso SÍ incluye qué lo disparó -- el mensaje de la persona, o
la acción que tocó -- corrección del usuario sobre el alcance original de
esta unidad (2026-09-28, mismo día): la Constitución §2 ya le da al
administrador de plataforma acceso a las conversaciones privadas entre
Leda y los integrantes, y §12 dice que ESE acceso se audita, no que haya
que ocultárselo. Lo que §10 exige es que el incidente quede sanitizado --
sin secretos -- no que el aviso salga sin disparador. Por eso este módulo
nunca manda `referencia_cruda` (la traza técnica cruda, que puede traer algo
parecido a un secreto): arma el disparador leyendo `inbound_message` o
`pending_action`, ya con retención por cliente y sin nada de la aplicación.

Cada aviso deja además una fila en `audit_log` (Constitución §12, "el acceso
del administrador a conversaciones también se registra"): una por
administrador realmente avisado, nunca al reprocesar el mismo incidente.

Reusable por el validador de invariantes diario que se agregue después
(`odd/tasks/validador-invariantes.md`): cualquier violación que ese proceso
detecte pasa por este mismo `registrar_incidente`, con `workspace_id` en
`None` cuando el hallazgo no es de un cliente en particular.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from .db import registrar_auditoria

# Segunda capa de defensa (R1-001, revisión 2026-09-28): traduce cualquier
# token de bot de Telegram que haya llegado sin traducir hasta acá -- la
# URL completa de la API (`api.telegram.org/bot<token>/...`) o el patrón
# `bot<digitos>:<token>` suelto -- antes de guardarlo. `despachador.py` ya
# traduce el error en el origen (`pedido_telegram`/`ErrorTelegram`); esto
# es la red de contención si algo aguas arriba se olvida.
_RE_TOKEN_TELEGRAM = re.compile(
    r"(?:https?://)?api\.telegram\.org/bot[^\s'\"]*|bot\d+:[A-Za-z0-9_-]+")


def redactar_secreto_telegram(texto: str | None) -> str | None:
    """Reemplaza cada coincidencia por `bot<oculto>`. `None` y cadena
    vacía pasan sin cambios."""
    if not texto:
        return texto
    return _RE_TOKEN_TELEGRAM.sub("bot<oculto>", texto)

# Qué tipo de fila referencia `incident.referencia_id` -- mismo patrón
# polimórfico que `audit_log.sujeto_tipo`/`sujeto_id`, sin clave foránea:
# apunta a texto, nunca lo copia (docs/ROADMAP.md: la retención de
# `inbound_message` es por cliente). La referencia a un toque
# (`pending_action`) se retiró con los flujos A y B (E3-3).
REFERENCIA_INBOUND_MESSAGE = "inbound_message"
# Un aviso de `admin_notice` que agotó sus reintentos (T28, despachador.py
# `despachar_avisos_admin`): apunta a esa fila, no a un mensaje ni una
# acción -- `referencia_tipo` es texto libre, sin restricción en el esquema
# (mismo patrón polimórfico, sin clave foránea), así que agregar este valor
# no necesita una migración.
REFERENCIA_ADMIN_NOTICE = "admin_notice"

# Lo que ve la persona cuando algo falla y ningún camino específico le contestó
# (T10-2, R3-H2, texto aprobado por el usuario). Vive acá, no en `gateway.py`,
# porque el aviso a la administración cuenta que la persona vio esto
# (`EXPLICACION_POR_ETAPA`); `gateway` lo sigue exponiendo con el mismo nombre.
NOTICIA_NEUTRA_INCIDENTE = (
    "Tuve un problema y no pude responder tu mensaje. Ya quedó registrado "
    "para que lo revise un administrador.")

# Etapas de incidente propias de este módulo y de quien lo comparte (T10-2b): una
# constante con nombre por cada punto donde el código registra un incidente, cada una
# con su entrada en `EXPLICACION_POR_ETAPA`.
ETAPA_TURNO_CONVERSACION = "turno_conversacion"
ETAPA_ENTREGA_MENSAJE = "entrega_mensaje"
ETAPA_ENTREGA_AVISO_ADMIN = "entrega_aviso_admin"
ETAPA_EVIDENCIA_INVALIDA = "politica_de_evidencia_invalida"
# T9-H19e: un recibo viejo sin respuesta que la reentrega no recuperó (`huerfanos`).
ETAPA_MENSAJE_HUERFANO = "mensaje_huerfano_sin_respuesta"
# T9-H19g: el aviso de UN huérfano falló y se lo saltea (el resto del barrido sigue).
ETAPA_MENSAJE_HUERFANO_FALLO = "mensaje_huerfano_fallo_al_avisar"

# Tope del texto disparador en el aviso -- decisión del usuario, 2026-09-28:
# acotado, y el aviso dice cuándo lo recortó.
LIMITE_TEXTO_DISPARADOR = 1000


def _quien_disparo(cur, app_user_id: str | None) -> str | None:
    """El nombre de la persona identificada, si la hay. Por la vista
    `integrante` (acotada al espacio activo de la sesión): nunca consulta
    `app_user` directo, que es global."""
    if not app_user_id:
        return None
    cur.execute("select nombre from integrante where app_user_id = %s", (app_user_id,))
    fila = cur.fetchone()
    return fila["nombre"] if fila else None


def _texto_disparador(cur, referencia_tipo: str | None,
                      referencia_id: str | None) -> str:
    """Qué disparó el incidente: el texto del mensaje. Nunca `referencia_cruda` --
    eso es la traza técnica, no el disparador, y puede traer algo parecido
    a un secreto."""
    texto = None
    if referencia_tipo == REFERENCIA_INBOUND_MESSAGE and referencia_id:
        cur.execute("select texto from inbound_message where id = %s",
                    (referencia_id,))
        fila = cur.fetchone()
        texto = fila["texto"] if fila else None

    if texto is None:
        return "(sin referencia al mensaje o la acción que lo disparó)"
    if len(texto) > LIMITE_TEXTO_DISPARADOR:
        return (texto[:LIMITE_TEXTO_DISPARADOR]
                + f"… (recortado -- {len(texto)} caracteres en total)")
    return texto


@dataclass(frozen=True)
class ExplicacionDeEtapa:
    """Qué pasó, qué vio la persona y qué hacer, en lenguaje llano, para una
    etapa de incidente (T10-2, R3-H1). `que_vio` y `que_hacer` pueden nombrar a
    la persona con `{nombre}`."""
    que_paso: str
    que_vio: str
    que_hacer: str
    # El título del aviso, cuando no es "Leda no pudo responderle a {nombre}": una
    # etapa en la que Leda sí respondió (el Motor, `motor_fuera_de_la_lista`).
    titulo: str | None = None


_BUSCAR_DETALLE = "Buscá el detalle con `python -m leda incidentes <espacio>`"

# Tabla determinista, nunca el modelo: una entrada por etapa con la que el código
# registra un incidente (las constantes `ETAPA_*` de este módulo, más los literales
# de `ciclo`, `saludo` y `despachador`, y algunos literales de los flujos A y B que
# pueden seguir en incidentes ya registrados). Una etapa
# sin entrada cae en `_EXPLICACION_GENERICA`;
# `tests/test_aviso_incidente_legible.py` falla si una etapa conocida queda sin
# entrada.
EXPLICACION_POR_ETAPA: dict[str, ExplicacionDeEtapa] = {
    "turno_texto": ExplicacionDeEtapa(
        que_paso=("Falló algo dentro de Leda mientras procesaba un mensaje de "
                  "texto, y ningún control más específico lo atajó."),
        que_vio=NOTICIA_NEUTRA_INCIDENTE,
        que_hacer=(f"{_BUSCAR_DETALLE} y corregí la causa. Después podés "
                   "pedirle a {nombre} que reenvíe el mensaje.")),
    "toque_boton": ExplicacionDeEtapa(
        que_paso=("Falló algo dentro de Leda mientras procesaba el toque de "
                  "un botón, y ningún control más específico lo atajó."),
        que_vio=NOTICIA_NEUTRA_INCIDENTE,
        que_hacer=(f"{_BUSCAR_DETALLE} y corregí la causa. Revisá que lo que "
                   "{nombre} quería hacer no haya quedado a medias.")),
    "activacion": ExplicacionDeEtapa(
        que_paso="Falló algo al activar a la persona en el espacio.",
        que_vio=NOTICIA_NEUTRA_INCIDENTE,
        que_hacer=(f"{_BUSCAR_DETALLE} y confirmá que {{nombre}} quedó "
                   "activada; si no, repetí la activación.")),
    "accion_menu": ExplicacionDeEtapa(
        que_paso=("Un botón del menú de una tarea llegó a una acción que "
                  "terminó sin un resultado que Leda pueda confirmar."),
        que_vio=NOTICIA_NEUTRA_INCIDENTE,
        que_hacer=("Revisá el estado de la tarea antes de repetir la acción, "
                   "porque no se sabe si algo cambió, y pasale el detalle "
                   "técnico a quien desarrolla.")),
    "fila_terminal_sin_atar": ExplicacionDeEtapa(
        que_paso=("La respuesta final de un borrador no se pudo asociar al "
                  "toque que la provocó."),
        que_vio=("La respuesta con el estado real del borrador, no el aviso "
                 "de problema."),
        que_hacer=("Confirmá que {nombre} recibió una sola respuesta y que el "
                   "borrador está en el estado que espera.")),
    "mensaje_recuperado_sin_respuesta": ExplicacionDeEtapa(
        que_paso=("Un mensaje de {nombre} se recibió pero su turno murió antes de "
                  "responderlo (un reinicio o un corte del proceso); Telegram lo "
                  "reentregó y Leda lo atendió de nuevo."),
        que_vio="La respuesta a su mensaje, con demora.",
        que_hacer=(f"{_BUSCAR_DETALLE} y mirá si hubo un reinicio o un corte del "
                   "servicio a esa hora. No hace falta avisarle a {nombre}.")),
    "mensaje_huerfano_sin_respuesta": ExplicacionDeEtapa(
        que_paso=("Un mensaje de {nombre} se recibió pero su turno murió antes de "
                  "responderlo (un reinicio o un corte del proceso) y Telegram no "
                  "lo reentregó: la red de fondo lo encontró sin respuesta."),
        que_vio=NOTICIA_NEUTRA_INCIDENTE,
        que_hacer=(f"{_BUSCAR_DETALLE} y mirá si hubo un reinicio o un corte del "
                   "servicio a esa hora. {nombre} puede reenviar el mensaje: "
                   "Leda no lo vuelve a procesar solo.")),
    "mensaje_huerfano_fallo_al_avisar": ExplicacionDeEtapa(
        que_paso=("Un mensaje de {nombre} se recibió y quedó sin respuesta, pero "
                  "la red de fondo no pudo avisarle: falló al escribir el aviso "
                  "de ese mensaje. Se reintenta en cada pasada y los demás "
                  "mensajes no se frenan."),
        que_vio="Nada: todavía no recibió ninguna respuesta a ese mensaje.",
        que_hacer=(f"{_BUSCAR_DETALLE} y corregí la causa (está en la referencia "
                   "técnica del incidente); el aviso sale solo en la pasada "
                   "siguiente. Mientras tanto {nombre} puede reenviar el mensaje.")),
    "sin_respuesta": ExplicacionDeEtapa(
        que_paso=("Un mensaje quedó sin ninguna respuesta de Leda; el control "
                  "de respuesta única mandó el aviso de problema."),
        que_vio=NOTICIA_NEUTRA_INCIDENTE,
        que_hacer=(f"{_BUSCAR_DETALLE} para ver qué camino no contestó y "
                   "corregilo. {nombre} puede reenviar el mensaje.")),
    "respuesta_duplicada": ExplicacionDeEtapa(
        que_paso=("Un mismo mensaje generó más de una respuesta; se conservó "
                  "una y se descartaron las demás."),
        que_vio="Una sola respuesta, la que se conservó.",
        que_hacer=("No hace falta avisarle a {nombre}. Mirá en el resumen qué "
                   "camino respondió de más y corregilo.")),
    "nota_sin_respuesta": ExplicacionDeEtapa(
        que_paso=("Una nota que un turno dejó para su respuesta no llegó a "
                  "salir, porque le tocaba a otro mensaje."),
        que_vio="La respuesta de su mensaje, sin esa nota.",
        que_hacer=("Revisá el resumen: si la nota era importante, avisale a "
                   "{nombre}.")),
    "mensaje_admin": ExplicacionDeEtapa(
        que_paso=("Falló el procesamiento de un mensaje enviado al bot de "
                  "administración."),
        que_vio="Nada: este canal no manda ningún aviso de problema.",
        que_hacer=(f"{_BUSCAR_DETALLE} y avisale a {{nombre}} si lo que "
                   "pidió tiene que repetirse.")),
    "ciclo_de_fondo": ExplicacionDeEtapa(
        que_paso=("Falló una tarea del ciclo de fondo (cadencias, avisos y "
                  "demás trabajo sin un mensaje de por medio)."),
        que_vio="Nada: ocurrió en segundo plano.",
        que_hacer=(f"{_BUSCAR_DETALLE}. Mientras no se corrija, lo que esa "
                   "tarea tenía que hacer no se hace.")),
    "saludo_diario": ExplicacionDeEtapa(
        que_paso="Falló el envío del saludo del día.",
        que_vio="Nada: no le llegó el saludo.",
        que_hacer=(f"{_BUSCAR_DETALLE}. El saludo no sale hasta que se "
                   "corrija.")),
    ETAPA_TURNO_CONVERSACION: ExplicacionDeEtapa(
        que_paso=("Falló el turno de conversación con {nombre}: el proveedor del "
                  "modelo, el armado del turno o una herramienta levantó un "
                  "error."),
        que_vio=NOTICIA_NEUTRA_INCIDENTE,
        que_hacer=(_BUSCAR_DETALLE + " y corregí la causa (proveedor caído, "
                   "clave vencida o un defecto). Después {nombre} puede "
                   "reenviar el mensaje.")),
    ETAPA_ENTREGA_MENSAJE: ExplicacionDeEtapa(
        que_paso=("Un mensaje para {nombre} no se pudo entregar por Telegram "
                  "después de varios intentos."),
        que_vio="Nada: el mensaje nunca le llegó.",
        que_hacer=("Revisá que Telegram responda y que {nombre} no haya "
                   "bloqueado el bot. Después decidí si hay que reenviarle lo "
                   "que faltó.")),
    ETAPA_ENTREGA_AVISO_ADMIN: ExplicacionDeEtapa(
        que_paso=("Un aviso a la administración de la plataforma no se pudo "
                  "entregar después de varios intentos."),
        que_vio="Nada: es un aviso interno, no le llega a nadie más.",
        que_hacer=(_BUSCAR_DETALLE + " y revisá que cada administrador haya "
                   "escrito al bot de administración y que Telegram responda.")),
    ETAPA_EVIDENCIA_INVALIDA: ExplicacionDeEtapa(
        que_paso=("La evidencia que exige la política de un área tiene más "
                  "texto del que Telegram puede mostrar."),
        que_vio=("Que no se puede mostrar una opción configurada del espacio y "
                 "que le pida a quien lo administra que la revise."),
        que_hacer=("Acortá la política de evidencia del área (menos ítems o "
                   "textos más cortos) y avisale a {nombre} que puede "
                   "reintentar.")),
    "indicador_actividad": ExplicacionDeEtapa(
        que_paso=("No se pudo retirar el borrador nativo del indicador de "
                  "actividad; puede haber quedado visible."),
        que_vio=("Posiblemente un texto de \"escribiendo\" o un borrador que "
                 "no desapareció."),
        que_hacer=(f"{_BUSCAR_DETALLE} y verificá que el chat de {{nombre}} "
                   "no tenga un borrador suelto.")),
    # El Motor (`prueba_chica/turno.py`, ADR 0018, decisiones 1 y 9g): un pedido que no
    # está en la lista cerrada de jugadas. No es una falla: Leda respondió.
    "motor_fuera_de_la_lista": ExplicacionDeEtapa(
        titulo="Leda recibió de {nombre} un pedido que todavía no sabe hacer",
        que_paso=("Le pidieron a Leda algo que no está en la lista de lo que hace "
                  "por chat. No hizo nada y respondió con lo que sí puede hacer."),
        que_vio=("La respuesta de Leda con lo que puede hacer por chat. Que se "
                 "avisó a la administración se le dice sólo si lo pregunta."),
        que_hacer=("Leé el mensaje y decidí si hace falta una jugada nueva (ADR "
                   "0018, decisión 1); si hace falta, se escribe primero como "
                   "conversación de prueba. No hace falta avisarle a {nombre}.")),
    # El Motor (`prueba_chica/escalera.py`, mecánica §9): falta configuración del espacio
    # para la escalera. Leda siguió con el mínimo del núcleo o sin escalar.
    "motor_escalera": ExplicacionDeEtapa(
        titulo="La escalera de recordatorios necesita atención",
        que_paso=("La escalera de recordatorios del motor de conversación no pudo seguir "
                  "como lo configura el espacio: le falta cuántos días hábiles antes sale el "
                  "aviso previo, o una ruta de escalamiento por falta de respuesta con "
                  "alguien que no sea el responsable. El resumen dice cuál."),
        que_vio=("Sin el aviso previo configurado, {nombre} lo recibió un día hábil antes, "
                 "el mínimo; sin la ruta, la tarea no se escaló a nadie."),
        que_hacer=(f"{_BUSCAR_DETALLE} y completá en el pack del espacio lo que falta "
                   "(`aviso_previo_dias_habiles` o la ruta "
                   "`falta_persistente_de_respuesta`).")),
    # El Motor (`prueba_chica/avisos.py`, ADR 0018, decisión 8): la IA no redactó un aviso
    # guardado tras sus reintentos. Nunca sale un texto armado a mano.
    "motor_aviso_guardado": ExplicacionDeEtapa(
        titulo="Un aviso de Leda no salió",
        que_paso=("La IA no redactó un aviso guardado del motor de conversación (un "
                  "recordatorio, un escalamiento o un aviso al referente) después de cinco "
                  "intentos, a los 1, 2, 4 y 8 minutos. Quedó guardado con sus hechos, sin "
                  "enviar: nunca sale un texto armado a mano."),
        que_vio=("Nada: el aviso no le llegó a {nombre}. Si lo causó lo que escribió otra "
                 "persona, a ella le llega un aviso de la falla."),
        que_hacer=(_BUSCAR_DETALLE + " y corregí la causa (proveedor de la IA caído, clave "
                   "vencida o un defecto). Una escalera sigue con su paso siguiente; decidí "
                   "si hay que decirle a {nombre} lo que no le llegó.")),
    # El Motor (`prueba_chica/ciclo.py`): se cayó un paso del ciclo que corre en el
    # escuchador. Los demás pasos siguieron.
    "motor_ciclo": ExplicacionDeEtapa(
        titulo="Se cayó una parte del ciclo del motor",
        que_paso=("Una parte del ciclo que corre cada minuto en el escuchador del motor (la "
                  "escalera, los avisos guardados, el despacho de mensajes o el de los avisos "
                  "a la administración) se cayó. Las demás siguieron, y ésta se reintenta en "
                  "cada vuelta; mientras siga cayéndose no llega otro aviso."),
        que_vio=("Todavía nada: lo que tenía que salir para {nombre} sale cuando esa parte "
                 "vuelva a andar."),
        que_hacer=(_BUSCAR_DETALLE + " y corregí la causa; la consola del escuchador "
                   "dice en cada vuelta si sigue cayéndose.")),
}

_EXPLICACION_GENERICA = ExplicacionDeEtapa(
    que_paso=("Leda registró un problema en una parte que todavía no tiene "
              "una explicación propia; el resumen técnico dice dónde."),
    que_vio=("No se puede saber con este registro qué vio {nombre}; "
             "revisá su chat."),
    que_hacer=f"{_BUSCAR_DETALLE} y decidí si hay que avisarle a {{nombre}}.")


def _hora_local(momento: datetime, zona_horaria: str | None) -> str:
    """La hora del aviso en la zona del espacio (`workspace.zona_horaria`),
    no en UTC, con la zona a la vista; sin espacio (incidente global), UTC dicho
    como tal."""
    if zona_horaria:
        try:
            zona = ZoneInfo(zona_horaria)
        except Exception:  # noqa: BLE001 -- una zona rota no puede tirar el aviso
            zona = None
        if zona is not None:
            hora = momento.astimezone(zona).strftime("%d/%m %H:%M")
            return f"{hora} (hora local, {zona_horaria})"
    return f"{momento.astimezone(timezone.utc).strftime('%d/%m %H:%M')} UTC"


def armar_aviso_admin(*, incident_id: str, slug: str | None,
                      zona_horaria: str | None, momento: datetime,
                      etapa: str | None, severidad: str, resumen: str,
                      nombre: str | None, mensaje: str) -> str:
    """El aviso a la administración de plataforma (T10-2, R3-H1, formato
    aprobado por el usuario): qué le pasó a la persona primero, lo técnico al
    final. `que_paso`/`que_vio`/`que_hacer` salen de `EXPLICACION_POR_ETAPA`;
    `mensaje` es el disparador que el aviso ya mostraba, sin nada nuevo."""
    explicacion = EXPLICACION_POR_ETAPA.get(etapa or "", _EXPLICACION_GENERICA)
    quien = nombre or "la persona"
    if explicacion.titulo:
        titulo = explicacion.titulo.format(nombre=quien)
    else:
        titulo = (f"⚠️ Leda no pudo responderle a {nombre}" if nombre
                  else "⚠️ Leda tuvo un problema")
    return "\n".join((
        titulo,
        "",
        "Qué pasó",
        explicacion.que_paso,
        "",
        f"Qué vio {quien}",
        explicacion.que_vio.format(nombre=quien),
        "",
        "Qué hacer",
        explicacion.que_hacer.format(nombre=quien),
        "",
        "Mensaje",
        mensaje,
        "",
        "Detalle técnico",
        f"Incidente {incident_id[:8]} · espacio {slug or 'global'} · "
        f"etapa {etapa or 'sin etapa'} · severidad {severidad}",
        _hora_local(momento, zona_horaria),
        f"Resumen: {resumen}",
    ))


def _texto_aviso_admin(cur, incident_id: str, workspace_id: str | None, *,
                       etapa: str | None, severidad: str, resumen: str,
                       referencia_tipo: str | None,
                       referencia_id: str | None,
                       app_user_id: str | None,
                       momento: datetime | None = None) -> str:
    slug = zona_horaria = None
    if workspace_id is not None:
        cur.execute("select slug, zona_horaria from workspace where id = %s",
                    (workspace_id,))
        fila = cur.fetchone()
        if fila:
            slug, zona_horaria = fila["slug"], fila["zona_horaria"]

    return armar_aviso_admin(
        incident_id=incident_id, slug=slug, zona_horaria=zona_horaria,
        momento=momento or datetime.now(timezone.utc), etapa=etapa,
        severidad=severidad, resumen=resumen,
        nombre=_quien_disparo(cur, app_user_id),
        mensaje=_texto_disparador(cur, referencia_tipo, referencia_id))


def avisar_incidente_admin(cur, incident_id: str, *, workspace_id: str | None,
                           cuerpo: str, referencia_tipo: str | None = None,
                           referencia_id: str | None = None) -> list[str]:
    """Encola `cuerpo` para cada administrador de plataforma alcanzable y
    deja un `audit_log` por cada uno realmente avisado ahora (Constitución
    §12) -- nunca duplicado al reprocesar el mismo incidente: la base sólo
    devuelve el administrador cuando el `insert` en `admin_notice` fue
    nuevo, no cuando ya existía.

    "Alcanzable" es haberle escrito al menos una vez al bot de
    administración (`gateway.procesar_update`, canal ADMINISTRACION,
    `accion='mensaje_admin'` en `audit_log`): Telegram no deja que un bot le
    escriba primero a alguien que nunca le escribió.

    `referencia_tipo`/`referencia_id` -- el `inbound_message` o la
    `pending_action` que `cuerpo` ya cita como disparador -- quedan en el
    `audit_log` como `sujeto_tipo`/`sujeto_id` (Constitución §12: "el acceso
    del administrador a conversaciones también se registra"), nunca su
    texto: eso ya está en `admin_notice.cuerpo`, no hace falta copiarlo acá.

    Devuelve el `app_user_id` de cada administrador recién avisado."""
    cur.execute(
        "select app_user_id from avisar_incidente_admin(%s, %s, %s)",
        (incident_id, workspace_id, cuerpo))
    avisados = [str(fila["app_user_id"]) for fila in cur.fetchall()]

    for admin_app_user_id in avisados:
        registrar_auditoria(
            cur, accion="aviso_incidente_admin", workspace_id=workspace_id,
            actor_app_user_id=admin_app_user_id, actor_kind="leda",
            sujeto_tipo=referencia_tipo, sujeto_id=referencia_id,
            detalle={"incident_id": incident_id})
    return avisados


def registrar_incidente(cur, workspace_id: str | None, resumen: str, *,
                        severidad: str = "media",
                        referencia_cruda: str | None = None,
                        etapa: str | None = None,
                        referencia_tipo: str | None = None,
                        referencia_id: str | None = None,
                        chat_id: int | None = None,
                        app_user_id: str | None = None,
                        notificado_en=None,
                        avisar_admin: bool = True) -> str:
    """Inserta un incidente sanitizado y avisa a la administración de
    plataforma (Constitución §10). Helper compartido para que quien necesite
    registrar un incidente no arme el insert a mano en cada lugar nuevo.

    `resumen` es legible para una persona y no lleva texto de mensajes;
    `referencia_cruda` es la traza técnica completa (tipo y mensaje de la
    excepción), sólo para quien administra -- nunca sale en el aviso a la
    administración tampoco: puede traer algo parecido a un secreto, y el
    disparador que el aviso SÍ muestra sale de `inbound_message`/
    `pending_action`, no de la excepción. `referencia_tipo` + `referencia_id`
    apuntan a la fila que originó esto -- el `inbound_message` o la
    `pending_action` -- sin copiar su contenido acá: el texto se abre desde
    ahí, bajo la retención por cliente que define `docs/ROADMAP.md`.
    `workspace_id` puede ser `None` para un hecho global, sin cliente en
    particular (p. ej. el validador de invariantes).

    `notificado_en` es sobre el aviso a la PERSONA afectada -- lo resuelve
    quien llama, como ya hacía `gateway.reportar_incidente_no_manejado`. El
    aviso a la administración lo resuelve esta función sola y queda en
    `notificado_admin_en`, sin mentir si nadie era alcanzable: se lo nota
    dentro del propio `resumen`, igual que ya se hacía para la persona.

    `avisar_admin=False` corta el fan-out a la administración (freno contra
    loop, T28: `despachador.despachar_avisos_admin` lo usa cuando el propio
    aviso admin es lo que agotó sus reintentos -- sin este freno,
    `avisar_incidente_admin` encolaría un `admin_notice` nuevo por el mismo
    canal que acaba de fallar, ese fallaría también, y encadenaría
    incidentes sin fin). Con `avisar_admin=False` nunca se llena
    `notificado_admin_en` -- sería mentir que se avisó por un canal que se
    sabe caído -- y el `resumen` deja una nota honesta, mismo criterio que
    cuando nadie es alcanzable.

    Devuelve el id del incidente insertado."""
    incident_id = str(uuid.uuid4())
    referencia_cruda = redactar_secreto_telegram(referencia_cruda)

    resumen_final = resumen
    notificado_admin_en = None
    if avisar_admin:
        cuerpo_aviso = _texto_aviso_admin(
            cur, incident_id, workspace_id, etapa=etapa, severidad=severidad,
            resumen=resumen, referencia_tipo=referencia_tipo,
            referencia_id=referencia_id, app_user_id=app_user_id)
        avisados = avisar_incidente_admin(
            cur, incident_id, workspace_id=workspace_id, cuerpo=cuerpo_aviso,
            referencia_tipo=referencia_tipo, referencia_id=referencia_id)
        if avisados:
            notificado_admin_en = datetime.now(timezone.utc)
        else:
            resumen_final += (" No se avisó a la administración: ningún "
                              "administrador de plataforma tiene el bot de "
                              "administración vinculado.")
    else:
        resumen_final += (" No se avisó a la administración: el canal de "
                          "administración es justamente el que falló -- "
                          "revisar con `python -m leda incidentes <espacio>`.")

    cur.execute(
        """insert into incident (id, workspace_id, severidad, resumen_sanitizado,
                                 referencia_cruda, etapa, referencia_tipo,
                                 referencia_id, chat_id, app_user_id,
                                 notificado_en, notificado_admin_en)
           values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (incident_id, workspace_id, severidad, resumen_final, referencia_cruda,
         etapa, referencia_tipo, referencia_id, chat_id, app_user_id,
         notificado_en, notificado_admin_en))
    return incident_id
