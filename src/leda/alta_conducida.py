"""El alta conducida por el modelo: el turno (ADR 0014, enmienda del 2026-10-01).

Con el ajuste del espacio `alta = conversada` (`workspace_setting`, como
`redaccion.variante_redaccion`; por omisión, el alta guiada de siempre), cada turno
del alta -- un mensaje de quien tiene un borrador en curso, o un toque dentro de él --
es UNA llamada al modelo con la conversación, el borrador (lo que hay y lo que falta),
las opciones que arma el código y lo que la persona dijo o tocó
(`alta_turno.HechosTurno`). El modelo devuelve una salida estructurada y cerrada
(`alta_turno.SalidaTurno`). Este módulo es el lado del servidor del contrato:

- arma los hechos desde la base (el contrato puro no conoce la base);
- valida cada valor (`alta_turno.aplicar_valores`) y guarda lo válido en
  `task_intake_field`, con los mismos estados de siempre;
- si algo se rechazó, o el texto no pasa la verificación, le pide UNA vez más al
  modelo con los motivos (el modelo puro: sin plazo propio y sin plantilla de
  respaldo); si falla de nuevo, o da error, un incidente y el aviso neutro;
- pone los botones del dato que se pregunta, desde el conjunto de opciones;
- con todo completo, el resumen que ya existe (`ingreso_tareas._finalize`): la lista
  exacta de datos y el cierre que nombra el botón real son del código, y la frase de
  apertura es la que dijo el modelo;
- cancelar cancela; dejar el alta o cambiar de tema la PAUSA (nada se pierde: no hay
  "¿Seguimos?").

Nada se compromete sin Confirmar: la conversión del borrador sigue siendo la función
de la base y el botón del resumen.
"""

from __future__ import annotations

import json
import secrets
import time
from dataclasses import dataclass, replace
from datetime import datetime

import psycopg
from psycopg.types.json import Jsonb

from . import alta_turno as T
from . import despachador
from . import ingreso_tareas as I
from . import instrucciones as INS
from . import redaccion
from .db import entrante_atado, registrar_auditoria
from .incidentes import (ETAPA_ALTA_CONDUCIDA_FALLIDA,
                         ETAPA_CRITERIO_SIN_PROPUESTA, ETAPA_INTERRUPTOR_ALTA,
                         ETAPA_INTERRUPTOR_STREAM,
                         NOTICIA_NEUTRA_INCIDENTE, REFERENCIA_INBOUND_MESSAGE,
                         registrar_incidente)
from .valores import sumar_meses
from .salida import (ICONO_RECOMENDADA, con_icono, etiqueta_sin_icono,
                     etiquetas_de_tarea, prepare_buttons, prepare_payload)

CLAVE_ALTA = "alta"
# Respuesta en stream (experimento del 2026-10-01): con `true` (o `{"activo": true}`),
# en un chat privado la persona ve el texto del turno aparecer en el borrador nativo
# mientras el modelo lo escribe. Sin el ajuste, apagado.
CLAVE_STREAM = "stream"
MODO_CONVERSADA = "conversada"
MODO_GUIADA = "guiada"
# `task_intake_choice_set.tipo` de los botones de un dato que pone este módulo: su
# toque no es de `ingreso_tareas.resolve_choice` sino del turno del modelo.
TIPO_ELECCION = "conversada"
# Cada intento del modelo (aceptado, rechazado o fallido) deja una fila de auditoría
# con su duración: la latencia del experimento sale de ahí.
ACCION_TURNO = "alta_conducida_turno"
# Cuántos botones salen para elegir un dato (las demás opciones se dicen por escrito:
# el modelo las conoce todas).
MAX_BOTONES = I.CANDIDATE_PAGE_SIZE
# Cuántas opciones de un dato se le dan al modelo como máximo.
MAX_OPCIONES = 40
# Las fallas del modelo se avisan a la administración una vez por espacio en esta
# ventana (si el modelo cae, cada mensaje falla: no es una tormenta de avisos); todas
# quedan registradas.
VENTANA_AVISO_ADMIN_S = 600
_reloj = time.monotonic
_ultimo_aviso: dict[str, float] = {}
# (espacio, valor) del ajuste ya registrado como anómalo por este proceso.
_anomalias_reportadas: set[tuple[str, str]] = set()
_anomalias_stream: set[tuple[str, str]] = set()
# La elección clara de Jev por (solicitud, título): se pregunta una vez, no en cada
# turno ni en cada intento.
_SUGERIDO: dict[tuple[str, str], tuple[list[str], bool]] = {}
_MAX_SUGERIDOS = 200


@dataclass(frozen=True)
class ResultadoConducido:
    outcome: I.IntakeOutcome
    # La persona cambió de tema: el borrador quedó pausado y el mensaje lo atiende el
    # camino normal (quien llama).
    otro_tema: bool = False


class _ConfiguracionInvalida(Exception):
    """Una opción configurada del espacio no se puede mostrar (largo, vacío)."""

    def __init__(self, campo: str):
        super().__init__(campo)
        self.campo = campo


# ---------------------------------------------------------------------------
# El interruptor
# ---------------------------------------------------------------------------

def alta_conducida(cur, workspace_id: str) -> bool:
    """Si el espacio conduce el alta con el modelo. Sin el ajuste, o con `guiada`,
    no. Un valor que no se entiende es el alta de siempre y queda un incidente (una
    vez por proceso): un interruptor mal escrito no se ignora en silencio."""
    cur.execute(
        "select valor from workspace_setting where workspace_id = %s and clave = %s",
        (workspace_id, CLAVE_ALTA))
    fila = cur.fetchone()
    if not fila:
        return False
    valor = fila["valor"]
    if isinstance(valor, str):
        try:
            valor = json.loads(valor)
        except ValueError:
            pass
    modo = valor.get("modo") if isinstance(valor, dict) else valor
    if modo == MODO_CONVERSADA:
        return True
    if modo != MODO_GUIADA:
        _registrar_anomalia(cur, workspace_id, valor)
    return False


def _registrar_anomalia(cur, workspace_id: str, valor) -> None:
    huella = (workspace_id, json.dumps(valor, sort_keys=True, default=str))
    if huella in _anomalias_reportadas:
        return
    registrar_incidente(
        cur, workspace_id,
        "El ajuste `alta` del espacio no tiene un valor válido (conversada o "
        "guiada): se usa el alta guiada de siempre.", severidad="baja",
        referencia_cruda=f"workspace_setting[{CLAVE_ALTA}]={huella[1]}"[:2000],
        etapa=ETAPA_INTERRUPTOR_ALTA, avisar_admin=False)
    _anomalias_reportadas.add(huella)


def stream_activo(cur, workspace_id: str) -> bool:
    """Si el espacio muestra la respuesta del turno mientras el modelo la escribe.
    Sin el ajuste, o con `false`, no. Un valor que no se entiende es "no" y queda un
    incidente (una vez por proceso), igual que el interruptor `alta`."""
    cur.execute(
        "select valor from workspace_setting where workspace_id = %s and clave = %s",
        (workspace_id, CLAVE_STREAM))
    fila = cur.fetchone()
    if not fila:
        return False
    valor = fila["valor"]
    if isinstance(valor, str):
        try:
            valor = json.loads(valor)
        except ValueError:
            pass
    activo = valor.get("activo") if isinstance(valor, dict) else valor
    if isinstance(activo, bool):
        return activo
    huella = (workspace_id, json.dumps(valor, sort_keys=True, default=str))
    if huella not in _anomalias_stream:
        registrar_incidente(
            cur, workspace_id,
            "El ajuste `stream` del espacio no tiene un valor válido (true o "
            "false): la respuesta no se muestra mientras el modelo la escribe.",
            severidad="baja",
            referencia_cruda=f"workspace_setting[{CLAVE_STREAM}]={huella[1]}"[:2000],
            etapa=ETAPA_INTERRUPTOR_STREAM, avisar_admin=False)
        _anomalias_stream.add(huella)
    return False


def _avance_en_vivo(cur, workspace_id: str):
    """Quien recibe el texto del turno a medida que el modelo lo escribe: el borrador
    del indicador de actividad, sólo en un chat privado (el único que admite
    borradores) y con el ajuste `stream` del espacio. `None` si no corresponde."""
    indicador = despachador.indicador_actual()
    if (indicador is None or not indicador.admite_borrador
            or not stream_activo(cur, workspace_id)):
        return None
    return indicador.actualizar_borrador


def solicitud_conducida(cur, who, chat_id: int):
    """El borrador en curso de esta persona en este chat si el espacio conduce el
    alta y el borrador no está pausado ni enviado a otra persona: ese borrador es su
    rama abierta y sus mensajes son del turno del modelo. `None` si no."""
    cur.execute(
        """select * from task_intake_request
            where workspace_id = %s and membership_id = %s and chat_id = %s
              and estado = 'active' and enviada_en is null for update""",
        (who.workspace_id, who.membership_id, chat_id))
    solicitud = cur.fetchone()
    if not solicitud or (solicitud["terminal_result"] or {}).get(I.PAUSADO):
        return None
    return solicitud if alta_conducida(cur, who.workspace_id) else None


def es_eleccion_conducida(cur, who, token: str) -> bool:
    """Si el botón es de los que pone este módulo (su toque es del turno del
    modelo)."""
    cur.execute(
        """select 1 from task_intake_choice c
             join task_intake_choice_set s on s.id = c.choice_set_id
            where c.token = %s and s.workspace_id = %s and s.tipo = %s""",
        (token, who.workspace_id, TIPO_ELECCION))
    return cur.fetchone() is not None


def titulo_del_borrador(cur, request_id: str) -> str:
    """El título del borrador si ya está confirmado, o `""`."""
    cur.execute(
        "select valor from task_intake_field where request_id = %s "
        "and campo = 'title' and estado = 'confirmed'", (request_id,))
    fila = cur.fetchone()
    return fila["valor"] if fila and isinstance(fila["valor"], str) else ""


# ---------------------------------------------------------------------------
# Puntos de entrada
# ---------------------------------------------------------------------------

def conducir_mensaje(cur, who, request, texto: str, now: datetime,
                     ) -> ResultadoConducido:
    """Un mensaje de quien tiene el borrador en curso."""
    return _turno(cur, who, request, {"mensaje": texto}, now)


def arrancar(cur, who, request_id: str, texto: str, now: datetime) -> I.IntakeOutcome:
    """El primer turno: el mensaje que abrió el alta ("necesito crear una tarea:
    calibrar…"), para que se tomen todos los datos que trae."""
    return _turno(cur, who, I._request(cur, request_id), {"mensaje": texto}, now,
                  permite_otro_tema=False).outcome


def continuar(cur, who, request, now: datetime) -> I.IntakeOutcome:
    """Retoma un borrador pausado: el modelo sigue donde estaban."""
    return _turno(cur, who, request, {"toque": "continuar"}, now,
                  permite_otro_tema=False).outcome


# La pregunta de un dato con opciones elegido en el selector de Modificar (C0-3).
PREGUNTA_AL_MODIFICAR = {
    "objective": "¿A qué objetivo pertenece la tarea?",
    "responsible": "¿Quién es responsable de la tarea?",
}


def campos_modificables(cur, request, who) -> list[str]:
    """Los datos del resumen que la persona puede cambiar con Modificar (C0-3), en
    el orden del resumen: la lista es del código, nunca del modelo. Son los que
    llena el alta (`alta_turno.CAMPOS`; el área y la evidencia salen del
    responsable), sin la descripción vacía (el resumen no la muestra) ni un dato
    con una sola opción posible (ADR 0013, regla 3)."""
    cur.execute(
        "select campo, valor from task_intake_field where request_id = %s",
        (str(request["id"]),))
    valores = {f["campo"]: f["valor"] for f in cur.fetchall()}
    campos = []
    for campo in T.CAMPOS:
        if campo == "description" and not I.normalize_text(
                str(valores.get(campo) or "")):
            continue
        if (campo in T.CAMPOS_DE_OPCION
                and I._unica_opcion(cur, request, who, campo) is not None):
            continue
        campos.append(campo)
    return campos


def pedir_dato(cur, who, request, campo: str, now: datetime) -> I.IntakeOutcome:
    """Lo que sigue a elegir un dato en el selector de Modificar (C0-3). Uno con
    opciones se pregunta con los botones del turno (las mismas opciones que usa el
    alta; el toque lo guarda `conducir_toque`); uno de texto se pide por escrito,
    con lo que tenía para copiar, y la respuesta la atiende el turno del modelo como
    cualquier corrección. Sin llamar al modelo: la pregunta es del código."""
    request_id = str(request["id"])
    clave = (f"intake:{request_id}:v{request['version']}:conducida:"
             f"{_evento_id(cur, now)}")
    if campo in T.CAMPOS_DE_OPCION:
        try:
            opciones = _opciones_de_ahora(cur, request, who, campo)
        except _ConfiguracionInvalida as exc:
            return I._configuration_error(cur, request, who, exc.campo, now)
        return _botones(cur, request, campo, opciones,
                        PREGUNTA_AL_MODIFICAR[campo], now)
    actual = I.text_to_copy(cur, request_id, campo)
    texto = I.modify_text_prompt(campo, actual)
    prepare_payload(texto, dedupe_key="intake-text", has_buttons=bool(actual))
    I._invalidate_open_inputs(cur, request_id)
    I._enqueue(cur, request, texto, now, clave, block=actual or None)
    return I.IntakeOutcome(request_id, texto, changed=True, responded=True)


def conducir_toque(cur, who, *, token: str, chat_id: int, now: datetime,
                   ) -> I.IntakeOutcome:
    """El toque de uno de los botones de este módulo: el código guarda la opción
    elegida (es la decisión de la persona, no del modelo) y el modelo contesta."""
    cur.execute(
        """select c.id choice_id, c.accion, c.valor, c.activa,
                  s.id choice_set_id, s.request_id, s.campo, s.estado set_estado,
                  s.resultado set_resultado, s.request_version,
                  r.membership_id, r.chat_id, r.estado request_estado,
                  r.version request_current_version
             from task_intake_choice c
             join task_intake_choice_set s on s.id = c.choice_set_id
             join task_intake_request r on r.id = s.request_id
            where c.token = %s and s.tipo = %s for update of s, c, r""",
        (token, TIPO_ELECCION))
    eleccion = cur.fetchone()
    if not eleccion:
        return I.IntakeOutcome("", "Ese botón ya no está vigente.", inert=True)
    request_id = str(eleccion["request_id"])
    if (str(eleccion["membership_id"]) != str(who.membership_id)
            or eleccion["chat_id"] != chat_id):
        return I.IntakeOutcome(request_id, "Ese botón corresponde a otro chat.",
                               inert=True)

    def inerte(persistido=None):
        persistido = persistido or eleccion["set_resultado"] or {}
        return I.IntakeOutcome(
            request_id, persistido.get("text", "Ese botón ya no está vigente."),
            inert=True, pending_action_id=persistido.get("pending_action_id"),
            terminal=persistido.get("terminal"))

    if eleccion["set_estado"] != "active" or not eleccion["activa"]:
        return inerte()
    if eleccion["request_estado"] != "active":
        return I.IntakeOutcome(request_id, "Ese borrador ya terminó.", inert=True,
                               terminal=eleccion["request_estado"])
    if eleccion["request_version"] != eleccion["request_current_version"]:
        return I.IntakeOutcome(request_id, "Ese botón ya no está vigente.",
                               inert=True)
    cur.execute(
        """update task_intake_choice_set set estado = 'consumed'
            where id = %s and estado = 'active' returning id""",
        (eleccion["choice_set_id"],))
    if not cur.fetchone():
        cur.execute("select resultado from task_intake_choice_set where id = %s",
                    (eleccion["choice_set_id"],))
        return inerte(cur.fetchone()["resultado"] or {})
    I._cerrar_botones_de(cur, eleccion["choice_set_id"], eleccion["choice_id"])
    request = _request_bloqueada(cur, request_id)
    campo, guardado = eleccion["campo"], eleccion["valor"]
    request = _guardar(
        cur, request, [T.Asignacion(campo, guardado, "", "confirmed",
                                    str(guardado["id"]))], now,
        choice_id=eleccion["choice_id"])
    elegida = guardado.get("title") or guardado.get("name") or ""
    outcome = _turno(cur, who, request, {"toque": campo, "elegida": elegida},
                     now, permite_otro_tema=False).outcome
    persistido = Jsonb(outcome.as_json())
    cur.execute("update task_intake_choice_set set resultado = %s where id = %s",
                (persistido, eleccion["choice_set_id"]))
    cur.execute("update task_intake_choice set resultado = %s where id = %s",
                (persistido, eleccion["choice_id"]))
    return outcome


# ---------------------------------------------------------------------------
# El turno
# ---------------------------------------------------------------------------

def _request_bloqueada(cur, request_id: str):
    cur.execute("select * from task_intake_request where id = %s for update",
                (request_id,))
    return cur.fetchone()


def _subir_version(cur, request, now: datetime):
    cur.execute(
        """update task_intake_request set version = version + 1,
                  actualizado_en = %s where id = %s returning *""",
        (now, request["id"]))
    return cur.fetchone()


def _turno(cur, who, request, evento: dict, now: datetime, *,
           permite_otro_tema: bool = True) -> ResultadoConducido:
    """Un turno: lo que el modelo entendió se valida y se guarda, y la respuesta es
    la suya. Una sola respuesta visible (`respuesta_unica`)."""
    request = _request_bloqueada(cur, str(request["id"]))
    try:
        problema = _completar(cur, request, who, now)
        if problema is not None:
            return ResultadoConducido(problema)
        return _conducir(cur, who, request, evento, now, permite_otro_tema)
    except _ConfiguracionInvalida as exc:
        return ResultadoConducido(
            I._configuration_error(cur, request, who, exc.campo, now))


def _conducir(cur, who, request, evento: dict, now: datetime,
              permite_otro_tema: bool) -> ResultadoConducido:
    workspace_id = str(request["workspace_id"])
    historial = I._conversacion_de(cur, request, now)
    # La mecánica del alta (con la personalidad adentro) y el tono del pack, armados
    # por el código (C0-13, C0-15). Fuera del `try` del modelo: un tono que no se
    # puede leer no es un error del modelo.
    instr = INS.instrucciones_alta_del_espacio(cur, workspace_id)
    proveedor = None
    rechazos: tuple[str, ...] = ()
    motivos: list[str] = []
    # Respuesta en stream: cada intento avisa su texto desde cero, así un reintento
    # tras un rechazo reemplaza en el borrador el texto del intento anterior. El
    # mensaje real es siempre el verificado, por la cola.
    avance = _avance_en_vivo(cur, workspace_id)
    en_vivo = {"al_avanzar": avance} if avance is not None else {}
    for intento in range(1, redaccion.INTENTOS_MODELO_PURO + 1):
        h = _hechos(cur, request, who, evento, now, rechazos, historial)
        inicio = time.perf_counter()
        try:
            proveedor = proveedor or redaccion.proveedor_de_redaccion(
                cur, workspace_id)
            crudo = proveedor.conducir_alta(instr.texto, historial,
                                            T.hechos_a_json(h), **en_vivo)
        except psycopg.Error:
            raise                    # la transacción no sigue: no es del modelo
        except Exception as exc:     # el modelo dio error: no se reintenta
            razon = redaccion._motivo_de_error(exc)
            _auditar(cur, workspace_id, intento, "error", razon, inicio, instr)
            motivos.append(razon)
            break
        salida = T.leer_salida(crudo)
        aplicacion = T.Aplicacion()
        if isinstance(salida, str):
            problemas = [salida]
        else:
            problemas = []
            if salida.intencion == "otro_tema" and not (
                    permite_otro_tema and "mensaje" in evento):
                problemas.append("intencion: otro_tema sólo vale con un mensaje "
                                 "de la persona sobre algo distinto del alta")
            else:
                aplicacion = T.aplicar_valores(salida, h)
                if aplicacion.asignaciones:
                    request = _guardar(cur, request, list(aplicacion.asignaciones),
                                       now, texto=evento.get("mensaje"))
                    problema = _completar(cur, request, who, now)
                    if problema is not None:
                        return ResultadoConducido(problema)
                problemas += aplicacion.rechazos
                motivo = T.verificar_turno(salida, h, aplicacion)
                if motivo:
                    problemas.append(motivo)
        if not problemas:
            _auditar(cur, workspace_id, intento, "aceptada", None, inicio, instr)
            return _responder(cur, who, request, salida, h, aplicacion, evento,
                              now)
        _auditar(cur, workspace_id, intento, "rechazada", "; ".join(problemas),
                 inicio, instr,
                 forma=None if isinstance(salida, str)
                 else _forma_de(salida, h, aplicacion))
        motivos.append("; ".join(problemas))
        rechazos = tuple(problemas)
    return _fallar(cur, who, request, evento, now, motivos)


def _forma_de(salida: T.SalidaTurno, h: T.HechosTurno,
              aplicacion: T.Aplicacion) -> dict:
    """La forma de una salida del modelo, sin ningún texto libre (ni del modelo ni de
    la persona: la auditoría es inmutable y una conversación no va ahí). Sirve para
    diagnosticar por qué se rechazó un intento: qué pidió, qué dio y qué seguía
    faltando."""
    return {
        "intencion": salida.intencion, "pregunta": list(salida.pregunta),
        "botones": salida.botones, "valores": sorted(salida.valores),
        "corrige": list(salida.corrige),
        "texto_tiene_pregunta": T._hay_pregunta(salida.texto),
        "texto_largo": len(salida.texto),
        "faltan_tras": list(aplicacion.faltan_tras(h)),
    }


def _auditar(cur, workspace_id: str, intento: int, resultado: str,
             motivo: str | None, inicio: float, instr: INS.Instrucciones,
             forma: dict | None = None) -> None:
    """Cada intento queda con la huella de las instrucciones que recibió el
    modelo: así se prueba qué versión se cargó (C0-13, C0-15)."""
    detalle = {"resultado": resultado, "intento": intento,
               "duracion_ms": round((time.perf_counter() - inicio) * 1000),
               **instr.auditoria()}
    if motivo:
        detalle["motivo"] = motivo[:300]
    if forma:
        detalle["salida"] = forma
    registrar_auditoria(cur, accion=ACCION_TURNO, workspace_id=workspace_id,
                        actor_kind="leda", detalle=detalle)


# ---------------------------------------------------------------------------
# Los hechos desde la base
# ---------------------------------------------------------------------------

_ESTADO_DEL_DATO = {"missing": "falta", "proposed": "propuesto",
                    "confirmed": "confirmado"}


def _campo_borrador(campo: str, fila) -> T.CampoBorrador:
    estado = _ESTADO_DEL_DATO[fila["estado"]]
    if estado == "falta":
        return T.CampoBorrador("falta")
    valor = fila["valor"]
    if campo in T.CAMPOS_DE_OPCION:
        mostrado, ref = I._mostrar_valor(campo, valor), str(valor["id"])
    elif campo == "due_date":
        mostrado, ref = I.format_due_date(valor), str(valor)
    else:
        mostrado = ref = I.normalize_text(str(valor or ""))
    if campo == "description" and not mostrado:
        return T.CampoBorrador("falta")      # la descripción vacía no es un dato
    return T.CampoBorrador(estado, mostrado, ref)


def _todas_las_candidatas(cur, request, who, campo: str) -> list:
    todas: list = []
    offset = 0
    while True:
        candidatas, hay_mas = I._entity_candidates(cur, request, who, campo, None,
                                                   offset=offset)
        todas += candidatas
        if not hay_mas or len(todas) >= MAX_OPCIONES:
            return todas
        offset += I.CANDIDATE_PAGE_SIZE


def _ordenar(cur, request, who, candidatas: list, titulo: str):
    """Los objetivos con el más probable primero, si Jev lo tiene claro
    (`ingreso_tareas._ordenar_objetivos`): una vez por solicitud y título."""
    clave = (str(request["id"]), titulo)
    if clave not in _SUGERIDO:
        ordenadas, clara = I._ordenar_objetivos(cur, request, who, candidatas)
        if len(_SUGERIDO) >= _MAX_SUGERIDOS:
            _SUGERIDO.clear()
        _SUGERIDO[clave] = ([c[1] for c in ordenadas], bool(clara))
    orden, clara = _SUGERIDO[clave]
    puesto = {ident: n for n, ident in enumerate(orden)}
    return sorted(candidatas, key=lambda c: puesto.get(c[1], len(puesto))), clara


def _opciones(cur, request, who, campo: str, filas: dict
              ) -> tuple[T.OpcionAlta, ...]:
    candidatas = _todas_las_candidatas(cur, request, who, campo)
    if not I._candidates_deliverable(campo, candidatas):
        raise _ConfiguracionInvalida(campo)
    clara = False
    if campo == "objective" and len(candidatas) > 1:
        titulo = filas["title"]["valor"]
        if (filas["objective"]["estado"] != "confirmed"
                and filas["title"]["estado"] == "confirmed"
                and isinstance(titulo, str) and titulo):
            candidatas, clara = _ordenar(cur, request, who, candidatas, titulo)
    prefijo = "O" if campo == "objective" else "R"
    opciones = []
    for n, (_, ident, guardado) in enumerate(candidatas, start=1):
        etiqueta = guardado["title"] if campo == "objective" else guardado["name"]
        opciones.append(T.OpcionAlta(
            f"{prefijo}{n}", etiqueta, guardado,
            sugerido=clara and n == 1,
            es_quien_escribe=(campo == "responsible"
                              and ident == str(who.membership_id)),
            # El botón que mostrará el resumen si esta persona es la responsable: lo
            # decide el código (`ingreso_tareas.boton_final_de`), el modelo lo lee.
            boton_final=(I.boton_final_de(cur, ident, request["membership_id"])
                         if campo == "responsible" else None)))
    return tuple(opciones)


def _hechos(cur, request, who, evento: dict, now: datetime,
            rechazos: tuple[str, ...], historial: list | None = None,
            ) -> T.HechosTurno:
    request_id = str(request["id"])
    cur.execute(
        "select campo, estado, valor from task_intake_field where request_id = %s",
        (request_id,))
    filas = {f["campo"]: f for f in cur.fetchall()}
    borrador = {campo: _campo_borrador(campo, filas[campo]) for campo in T.CAMPOS}
    area = (filas["area"]["valor"]["name"]
            if filas["area"]["estado"] == "confirmed" else "")
    evidencia = ""
    if filas["evidence"]["estado"] == "confirmed":
        evidencia = ", ".join(I.nombre_legible(e)
                              for e in filas["evidence"]["valor"]["items"])
    criterio = borrador["acceptance_criterion"]
    marca = (request["terminal_result"] or {}).get(I.CRITERIO_PROPUESTO)
    ws = str(request["workspace_id"])
    hoy = I._hoy_del_espacio(cur, ws, now)
    meses = I.meses_de_horizonte(cur, ws)
    return T.HechosTurno(
        hoy=hoy, limite_fecha=sumar_meses(hoy, meses), meses_horizonte=meses,
        quien_escribe=who.nombre or "", borrador=borrador, area=area,
        evidencia=evidencia,
        objetivos=_opciones(cur, request, who, "objective", filas),
        responsables=_opciones(cur, request, who, "responsible", filas),
        rechazos_anteriores=rechazos,
        propuesta_vigente=(criterio.mostrado if criterio.estado == "propuesto"
                           else None),
        propuesta_hecha=bool(marca) or criterio.estado == "propuesto",
        evento=evento, limites=I.USER_FIELD_LIMITS,
        conversacion=tuple(m["content"] for m in (historial or [])))


# ---------------------------------------------------------------------------
# Guardar lo que el código aceptó
# ---------------------------------------------------------------------------

def _guardar(cur, request, asignaciones: list, now: datetime, *,
             texto: str | None = None, choice_id=None):
    """Guarda las asignaciones aceptadas (los mismos estados de siempre de
    `task_intake_field`) y sube la versión de la solicitud: lo que estaba abierto
    deja de valer. `texto` es el mensaje que las dijo (su origen); con `choice_id`
    el origen es el botón tocado. Devuelve la solicitud al día."""
    request_id = str(request["id"])
    inbound = entrante_atado(cur) if texto is not None else None
    for a in asignaciones:
        propuesto_por = ("model" if a.estado == "proposed"
                         else "server" if choice_id else "user")
        cur.execute(
            """update task_intake_field
                  set estado = %s, valor = %s, proposed_by = %s,
                      source_inbound_id = %s, source_raw_text = %s,
                      source_choice_id = %s, version = version + 1,
                      actualizado_en = %s
                where request_id = %s and campo = %s""",
            (a.estado, Jsonb(a.valor), propuesto_por, inbound,
             texto if inbound else None, choice_id, now, request_id, a.campo))
        if a.campo == "responsible":
            # El área y la evidencia salen de quien es responsable: se recalculan.
            cur.execute(
                """update task_intake_field
                      set estado = 'missing', valor = null, proposed_by = null,
                          source_inbound_id = null, source_raw_text = null,
                          source_choice_id = null, version = version + 1,
                          actualizado_en = %s
                    where request_id = %s and campo in ('area', 'evidence')""",
                (now, request_id))
        if a.campo == "acceptance_criterion" and a.estado == "proposed":
            cur.execute(
                """update task_intake_request
                      set terminal_result =
                          coalesce(terminal_result, '{}'::jsonb) || %s
                    where id = %s""",
                (Jsonb({I.CRITERIO_PROPUESTO: True}), request_id))
    return _subir_version(cur, request, now)


def _completar(cur, request, who, now: datetime):
    """Lo que el servidor completa solo, como el alta de siempre: un dato con una
    sola opción posible (no se pregunta), el área de quien es responsable, la
    descripción vacía y la evidencia que exige la política del área. El objetivo
    tiene que ser un operativo del área de la tarea (C0-1, C0-2): si el responsable
    pasó a ser de otra área, el objetivo elegido se saca y se dice; si el área no
    tiene ningún objetivo operativo, se dice el estado real (una vez por área: la
    conversación sigue abierta). Devuelve lo que se le dijo a quien actuó, o
    `None`."""
    request_id = str(request["id"])
    cur.execute("select campo, estado from task_intake_field where request_id = %s",
                (request_id,))
    estados = {f["campo"]: f["estado"] for f in cur.fetchall()}

    def confirmar(campo: str, valor) -> None:
        cur.execute(
            """update task_intake_field
                  set estado = 'confirmed', valor = %s, proposed_by = 'server',
                      source_choice_id = null, version = version + 1,
                      actualizado_en = %s
                where request_id = %s and campo = %s""",
            (Jsonb(valor), now, request_id, campo))
        estados[campo] = "confirmed"

    # El responsable primero: de él sale el área de la tarea, y de ella el objetivo.
    if estados["responsible"] != "confirmed":
        unica = I._unica_opcion(cur, request, who, "responsible")
        if unica is not None:
            confirmar("responsible", unica)
    descartado = I.objetivo_de_otra_area(cur, request, who)
    if descartado is not None:
        I.descartar_objetivo(cur, request_id, now)
        estados["objective"] = "missing"
    elif estados["objective"] != "confirmed":
        unica = I._unica_opcion(cur, request, who, "objective")
        if unica is not None:
            confirmar("objective", unica)
    if estados["responsible"] == "confirmed" and estados["area"] != "confirmed":
        unica = I._unica_opcion(cur, request, who, "area")
        if unica is not None:
            confirmar("area", unica)
    if estados["description"] == "missing":
        confirmar("description", "")
    if descartado is not None:
        return _objetivo_descartado(cur, who, request, descartado, now)
    if estados["area"] == "confirmed" and estados["evidence"] != "confirmed":
        problema = I._completar_evidencia(cur, request, who, now)
        if problema is not None:
            return problema
    if estados["objective"] != "confirmed" and estados["responsible"] == "confirmed":
        sin_objetivo = I.sin_objetivo_operativo(cur, request, who, conversada=True)
        if sin_objetivo is not None and _primer_aviso(cur, request_id,
                                                      sin_objetivo[1]):
            return _decir_con_cancelar(cur, request, sin_objetivo[0], now)
    return None


def _primer_aviso(cur, request_id: str, area: str) -> bool:
    """Si es la primera vez que se avisa que el área `area` no tiene objetivo
    operativo en este borrador (la marca vive en `terminal_result`, como la pausa).
    Después del aviso la conversación sigue: el modelo atiende lo que se escriba."""
    cur.execute(
        """select terminal_result ->> %s dado from task_intake_request
            where id = %s""", (I.SIN_OBJETIVO_AVISADO, request_id))
    if cur.fetchone()["dado"] == area:
        return False
    cur.execute(
        """update task_intake_request
              set terminal_result = coalesce(terminal_result, '{}'::jsonb) || %s
            where id = %s""",
        (Jsonb({I.SIN_OBJETIVO_AVISADO: area}), request_id))
    return True


def _decir_con_cancelar(cur, request, texto: str, now: datetime) -> I.IntakeOutcome:
    """Un estado real del alta con el botón Cancelar borrador. No cierra la
    conversación: el mensaje siguiente lo atiende el modelo, como siempre."""
    outcome = I._open_choices(
        cur, request, None, texto, [(I.CANCELAR_BORRADOR, "cancel", None)], now,
        kind="no_candidates_objective",
        clave=(f"intake:{request['id']}:v{request['version']}:conducida:"
               f"{_evento_id(cur, now)}"))
    return replace(outcome, responded=True)


def _objetivo_descartado(cur, who, request, objetivo: dict, now: datetime
                         ) -> I.IntakeOutcome:
    """El objetivo elegido quedó de otra área (cambió el responsable): se dice que
    se sacó y se vuelve a preguntar con los botones del área de la tarea, o con el
    estado real si esa área no tiene ningún objetivo operativo."""
    aviso = I.aviso_objetivo_descartado(cur, request, objetivo)
    sin_objetivo = I.sin_objetivo_operativo(cur, request, who, conversada=True)
    if sin_objetivo is not None:
        _primer_aviso(cur, str(request["id"]), sin_objetivo[1])
        return _decir_con_cancelar(cur, request, f"{aviso} {sin_objetivo[0]}", now)
    return _botones(cur, request, "objective",
                    _opciones_de_ahora(cur, request, who, "objective"),
                    f"{aviso} ¿A qué objetivo de esa área pertenece?", now)


# ---------------------------------------------------------------------------
# La respuesta
# ---------------------------------------------------------------------------

def _evento_id(cur, now: datetime) -> str:
    return entrante_atado(cur) or str(now.timestamp())


def _decir(cur, request, texto: str, now: datetime, **resultado) -> I.IntakeOutcome:
    """Encola `texto` como la respuesta del turno."""
    request_id = str(request["id"])
    I._enqueue(cur, request, texto, now,
               f"intake:{request_id}:v{request['version']}:conducida:"
               f"{_evento_id(cur, now)}")
    return I.IntakeOutcome(request_id, texto, changed=True, responded=True,
                           **resultado)


def _responder(cur, who, request, salida: T.SalidaTurno, h: T.HechosTurno,
               aplicacion: T.Aplicacion, evento: dict, now: datetime,
               ) -> ResultadoConducido:
    request_id = str(request["id"])
    if salida.intencion == "otro_tema":
        I.pause_request(cur, who, request, now)
        return ResultadoConducido(I.IntakeOutcome(request_id, changed=True),
                                  otro_tema=True)
    if salida.intencion == "cancelar":
        I._cancel(cur, request, who, now, enqueue=False)
        return ResultadoConducido(_decir(cur, request, salida.texto, now,
                                         terminal="cancelled"))
    if salida.intencion == "dejar":
        I.pause_request(cur, who, request, now)
        request = I._request(cur, request_id)
        return ResultadoConducido(_decir(cur, request, salida.texto, now))
    if aplicacion.criterio_sin_propuesta:
        registrar_incidente(
            cur, who.workspace_id,
            "El modelo juzgó que el criterio de aceptación no es verificable, pero "
            "no dio una propuesta válida: se tomó el texto de la persona.",
            severidad="baja", etapa=ETAPA_CRITERIO_SIN_PROPUESTA,
            app_user_id=who.app_user_id, avisar_admin=False,
            referencia_tipo=REFERENCIA_INBOUND_MESSAGE if entrante_atado(cur) else None,
            referencia_id=entrante_atado(cur))
    faltan = aplicacion.faltan_tras(h)
    cambio = bool(aplicacion.asignaciones)
    if "objective" in faltan and (salida.botones == "objective"
                                  or "objective" in salida.pregunta):
        # Pedir un objetivo que no tiene de dónde salir es prometer lo que no existe
        # (constitución §4): la respuesta es el estado real (C0-2).
        sin_objetivo = I.sin_objetivo_operativo(cur, request, who, conversada=True)
        if sin_objetivo is not None:
            return ResultadoConducido(_decir_con_cancelar(
                cur, request, sin_objetivo[0], now))
    if not faltan:
        if cambio:
            return ResultadoConducido(_resumen(cur, who, request, salida.texto,
                                               now))
        if salida.botones:
            # Un dato ya confirmado que la persona cambia: sus opciones son las del
            # código y el toque las guarda (`conducir_toque`, sin pasar por `corrige`).
            return ResultadoConducido(_botones(
                cur, request, salida.botones,
                _opciones_de_ahora(cur, request, who, salida.botones),
                salida.texto, now))
        if not salida.pregunta and not _resumen_abierto(cur, request):
            return ResultadoConducido(_resumen(cur, who, request, salida.texto,
                                               now))
        return ResultadoConducido(_decir(cur, request, salida.texto, now))
    if cambio:
        I._invalidate_open_inputs(cur, request_id)   # el resumen y los botones viejos
    if salida.botones:
        # Las opciones con lo que el turno acaba de guardar (el título que trajo el
        # mensaje ya permite destacar el objetivo que se le parece).
        return ResultadoConducido(_botones(
            cur, request, salida.botones,
            _opciones_de_ahora(cur, request, who, salida.botones), salida.texto,
            now))
    return ResultadoConducido(_decir(cur, request, salida.texto, now))


def _opciones_de_ahora(cur, request, who, campo: str):
    cur.execute(
        "select campo, estado, valor from task_intake_field where request_id = %s",
        (str(request["id"]),))
    return _opciones(cur, request, who, campo, {f["campo"]: f for f in cur.fetchall()})


def _resumen_abierto(cur, request) -> bool:
    """Si el borrador ya tiene un resumen esperando su botón."""
    cur.execute(
        "select 1 from pending_action where draft_id = %s and estado = 'esperando'",
        (request["task_draft_id"],))
    return cur.fetchone() is not None


def _resumen(cur, who, request, apertura: str, now: datetime) -> I.IntakeOutcome:
    """Con todo completo: el resumen de siempre (los datos y el cierre que nombra el
    botón son del código) con la frase del modelo delante."""
    request_id = str(request["id"])
    I._invalidate_open_inputs(cur, request_id)
    request = _subir_version(cur, request, now)
    problema = _completar(cur, request, who, now)
    if problema is not None:
        return problema
    return I._finalize(cur, request, who, now, apertura=apertura)


def _botones(cur, request, campo: str, opciones, texto: str, now: datetime,
             ) -> I.IntakeOutcome:
    """El texto con los botones del dato, armados desde el conjunto de opciones de
    este turno (la estrella, la elección clara de Jev). Elegir uno lo guarda el
    código (`conducir_toque`)."""
    request_id = str(request["id"])
    elegidas = list(opciones)[:MAX_BOTONES]
    etiquetas = etiquetas_de_tarea(
        ["Para mí" if o.es_quien_escribe else o.etiqueta for o in elegidas])
    botones = [
        (con_icono(etiqueta_sin_icono(e), ICONO_RECOMENDADA) if o.sugerido else e,
         "select", o.guardado)
        for e, o in zip(etiquetas, elegidas)]
    prepare_payload(texto, dedupe_key="intake-choice", has_buttons=True)
    prepare_buttons([(etiqueta, "i:placeholder") for etiqueta, _, _ in botones])
    I._invalidate_open_inputs(cur, request_id)
    cur.execute(
        """insert into task_intake_choice_set
             (workspace_id, request_id, campo, request_version, tipo)
           values (%s, %s, %s, %s, %s) returning id""",
        (request["workspace_id"], request_id, campo, request["version"],
         TIPO_ELECCION))
    choice_set_id = str(cur.fetchone()["id"])
    for orden, (etiqueta, accion, valor) in enumerate(botones):
        cur.execute(
            """insert into task_intake_choice
                 (workspace_id, choice_set_id, token, etiqueta, accion, valor, orden)
               values (%s, %s, %s, %s, %s, %s, %s)""",
            (request["workspace_id"], choice_set_id, secrets.token_urlsafe(12),
             etiqueta, accion, Jsonb(valor), orden))
    I._enqueue(cur, request, texto, now,
               f"intake:{request_id}:v{request['version']}:conducida:"
               f"{_evento_id(cur, now)}", choice_set_id=choice_set_id)
    return I.IntakeOutcome(request_id, texto, changed=True, responded=True)


# ---------------------------------------------------------------------------
# Si el modelo falla
# ---------------------------------------------------------------------------

def _registrar_falla(cur, who, request, motivos: list[str]) -> None:
    """Un incidente por cada falla; el aviso a la administración, uno por espacio
    en `VENTANA_AVISO_ADMIN_S` (un modelo caído hace fallar cada mensaje: no es una
    tormenta de avisos)."""
    workspace_id = str(request["workspace_id"])
    ahora = _reloj()
    ultimo = _ultimo_aviso.get(workspace_id)
    avisar = ultimo is None or ahora - ultimo >= VENTANA_AVISO_ADMIN_S
    if avisar:
        _ultimo_aviso[workspace_id] = ahora
    evento = entrante_atado(cur)
    registrar_incidente(
        cur, workspace_id,
        "El modelo no pudo conducir un turno del alta de tareas (alta conducida): "
        "salió el aviso neutro y lo ya entendido quedó guardado.",
        severidad="media", referencia_cruda=" | ".join(motivos)[:2000],
        etapa=ETAPA_ALTA_CONDUCIDA_FALLIDA, app_user_id=who.app_user_id,
        chat_id=request["chat_id"],
        referencia_tipo=REFERENCIA_INBOUND_MESSAGE if evento else None,
        referencia_id=evento, avisar_admin=avisar,
        nota_sin_aviso=(" No se avisó a la administración: ya se avisó hace poco "
                        "de la misma causa (aviso agrupado)."))


def _fallar(cur, who, request, evento: dict, now: datetime, motivos: list[str],
            ) -> ResultadoConducido:
    """El modelo no pudo (dos intentos rechazados, o un error): incidente y el aviso
    neutro, nunca una plantilla. Lo único que el código agrega es lo mínimo para que
    la persona sepa qué sigue: el nombre del dato pendiente, con los botones si es
    una elección, o el resumen si ya estaba todo."""
    _registrar_falla(cur, who, request, motivos)
    h = _hechos(cur, request, who, evento, now, ())
    if not h.faltan:
        return ResultadoConducido(
            _resumen(cur, who, request, NOTICIA_NEUTRA_INCIDENTE, now))
    campo = h.faltan[0]
    texto = f"{NOTICIA_NEUTRA_INCIDENTE}\n\nPendiente: {T._SUJETOS[campo]}."
    opciones = h.opciones_de(campo) if campo in T.CAMPOS_DE_OPCION else ()
    if opciones:
        return ResultadoConducido(_botones(cur, request, campo, opciones, texto,
                                           now))
    return ResultadoConducido(_decir(cur, request, texto, now))
