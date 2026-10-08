"""Los avisos guardados: todo lo que Leda manda por su cuenta.

Diseño probado en la Etapa 2 (E2-5; `odd/tasks/prueba-chica-del-motor.md`, sección 4, "Avisos
guardados" y "Fallas de la IA"); ADR 0018, decisiones 8 (caso 2) y 9b; mecánica §9, §10 y §12.

Un aviso se guarda como hechos en `scheduled_notice`, con su hora y una clave de
deduplicación: nada se guarda ni sale dos veces. Al llegar su hora, y sólo dentro del horario
del espacio (9e), `enviar_avisos`:

1. vuelve a leer la tarea y comprueba que el aviso todavía corresponda, con la regla de su
   tipo (`TIPOS`); si ya no corresponde, queda `omitido` con su motivo, nunca en silencio;
2. le pide a la IA que lo redacte desde los hechos de ese momento, que quedan guardados como
   los que se mandaron; un efecto que pasa después dice siempre a quién le llega y cuándo,
   o si ya le llegó (primer contacto real, 2026-10-05; hablar del mundo y no de la cocina,
   usuario, 2026-10-06);
3. lo encola en el outbox, lo marca `enviado`, lo audita como un envío de Leda, con la versión
   de las reglas (`auditoria.py`), y lo deja en el registro de turnos de quien lo recibe, como
   su último aviso. Si pide el estado de la tarea, abre la pregunta y cuenta el recordatorio
   en la espera (`pending_reply`).

**Un envío por persona** (mecánica §10; hallazgo de la E2-7): los avisos automáticos de una
persona que salen juntos (los de la escalera de un día se guardan todos en la primera vuelta de
ese día) se redactan en un solo mensaje, desde los hechos de todos, con la pregunta de uno solo
(un tema a la vez: las demás quedan para después). Los de coordinación, que causa el acto de
otra persona, salen aparte y siempre, como las respuestas. El tope diario del pack, si lo hay,
lo aplica el despachador (`despachador._tope_diario`): pospone, nunca descarta; con un envío
por día y por espacio, no se alcanza.

Si la IA no lo redacta (o redacta un texto que el canal no lleva), el envío entero espera y se
reintenta a los 1, 2, 4 y 8 minutos, con sus avisos juntos. Cada intento que se reintenta deja
un incidente de severidad baja, sin avisar a la administración, para poder probar la causa de un
aviso que se demoró (usuario, 2026-10-07); al quinto
fallo queda `fallido` con sus hechos, se registra un incidente y, si una persona lo causó (el
turno que lo guardó), se le guarda un aviso de la falla con lo pendiente, que también redacta
la IA: nunca sale un texto armado a mano. Un destinatario ausente no recibe nada: su aviso
espera a que vuelva (la escalera lo reemplaza por un reencuadre, `escalera.py`).

Cada tipo se declara una vez con su regla (`TipoDeAviso`), como las fichas de las jugadas: el
camino de envío es uno para todos. Cuándo se guardan los de la escalera es de `escalera.py`;
los de una previsión y su corrección, de sus fichas (`fichas.py`), que los guardan para después
del margen para corregir (`margen.py`): lo que una persona dijo le llega a otra sólo cuando ya
tuvo tiempo de corregirlo.

**El aviso de una entrega a quien la aprueba** (`entrega_para_aprobar`; ADR 0019, decisión 6;
porción 3a de la C-3) reemplaza al texto fijo de la cocina. Lo guarda la confirmación de la
entrega (`guardar_aviso_de_entrega`), con el margen para corregir. Al salir, el código relee la
tarea y la evidencia vigente (la del ciclo, sin lo retirado): si la tarea ya no espera la
aprobación, queda omitido con su motivo. Es de coordinación: fuera del tope diario. Las fotos de
la evidencia van adjuntas, hasta diez, como un álbum que sale después del texto, en otra fila de
la misma respuesta (`adjuntos` del tipo; `message_outbox_adjunto`); los demás archivos sólo se
nombran. Una entrega nueva de la misma tarea retira el aviso que todavía espera y guarda otro
con toda la evidencia vigente (ADR 0009, enmienda T6i).

**El enlace a la página de la tarea** (ADR 0019, decisiones 6 y 7a; porción 4): lo llevan el
aviso de una entrega, a quien la aprueba, y los de la decisión (`tarea_aprobada`,
`pedido_de_cambios` y `cerrada_con_la_aprobacion`), al responsable (`TipoDeAviso.enlace`). La IA
sabe que el mensaje lo lleva (`LLEVA_EL_ENLACE`), nunca lo ve: la fila de la salida lleva la
marca (`enlace_de_tarea`) y el despachador lo emite al mandar, sin vista previa. Sólo con la
dirección pública configurada y si la persona puede ver la tarea (`puede_ver_tarea`, en la base):
nunca se promete un enlace que no va a salir.

**Lo que ofrece decidir** (porción 3b): el aviso de una entrega le pide a quien aprueba que
decida, con los botones "Aprobar" y "Pedir cambios" como atajos (`TipoDeAviso.ofrece`). Al salir
abre la decisión con sus opciones (`preguntas.ofrecer`): sus botones van con el texto del aviso,
nunca con su álbum (`botones.ConOpciones`), y la redacción la recibe como la única pregunta del
mensaje. No es un tema abierto: quien aprueba no le debe una respuesta a la conversación. La
decisión de quien aprueba le llega al responsable en su propio aviso (`tarea_aprobada`,
`pedido_de_cambios`), y el cierre que hace el sistema cuando se resuelve lo que faltaba, al
responsable y a quien aprobó (`cerrada_con_la_aprobacion`; `aprobacion.py`).

**Quien aprueba no contesta** (porción 3c): los recordatorios a quien aprueba
(`recordatorio_de_la_decision`) recuerdan la decisión que ofreció el aviso de la entrega
(`TipoDeAviso.recuerda`): la redacción la recibe como la pregunta del mensaje, ya hecha antes,
y al salir no abren otra ni llevan botones. El aviso a quien está arriba
(`aprobacion_trabada`) es sólo informativo. Los dos son seguimiento que Leda hace por su cuenta:
cuentan para el tope diario y salen en un envío por persona. Se omiten al salir si quien aprueba
ya decidió, si la entrega ya no espera o hay una más nueva, o si cambió quién aprueba o quién
está arriba. Que se destrabó (`aprobacion_destrabada`) lo causa la decisión: es de coordinación.
Cuándo se guardan, `escalera.py`.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta
from types import MappingProxyType, SimpleNamespace
from typing import Any

import psycopg

from ..calendario import Calendario
from ..db import espacio
from ..incidentes import registrar_incidente
from ..salida import MAX_ADJUNTOS, PayloadValidationError, enqueue_outbox

from . import cambios_de_estado, entrega, preguntas
from .ancla import (REPREGUNTA_DE_ESTADO, VENCIMIENTO_CON_PREVISION, ancla, anclaje,
                    clave_del_anclaje, fecha_de_la_clave)
from .ancla import prevision_vigente as _prevision_vigente
from .auditoria import auditar
from .fichas import (ATRASO_SI_SE_CUMPLE, ESPERA_ALGO_CIERTO, FICHAS, LLEGA, NO_LE_LLEGO,
                     YA_LE_LLEGO, referente)
from .margen import sale_con_margen
from .ia import IA
from .registro import leer_ultimos_turnos, no_vacio, registrar_salida
from .tiempo import Reloj

# Decisión 8, caso 2: tras el 1.º, 2.º, 3.º y 4.º fallo de la IA, la espera hasta el
# intento siguiente; al quinto fallo, el aviso queda `fallido`.
ESPERAS_TRAS_UN_FALLO = (timedelta(minutes=1), timedelta(minutes=2), timedelta(minutes=4),
                         timedelta(minutes=8))
INTENTOS = len(ESPERAS_TRAS_UN_FALLO) + 1

ETAPA_AVISO_GUARDADO = "motor_aviso_guardado"
# Un intento fallido que se reintenta: sólo el rastro (usuario, 2026-10-07).
ETAPA_AVISO_REINTENTO = "motor_aviso_reintento"

# La espera de respuesta de un pedido de estado (`pending_reply.tipo`, ADR 0017, decisión 6)
# y la pregunta que la acompaña.
ESPERA_DE_ESTADO = preguntas.ESTADO_DE_LA_TAREA

# La escalera de una pregunta que espera respuesta (`escalera.py`): la pregunta otra vez y,
# agotada sin respuesta, el escalamiento. La clave nombra la pregunta (`q<id>`).
REPREGUNTA = "repregunta"
ESCALAMIENTO_DE_UNA_PREGUNTA = "escalamiento_de_una_pregunta"

ABIERTOS = ("asignada", "en_curso")     # en la escalera: comprometida, sin entregar
# De menos a más urgente (mecánica §11): el tipo de un envío que junta varios avisos es el del
# más urgente.
URGENCIA = ("informativo", "normal", "seguimiento", "prioritario", "urgente")


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
# Los archivos que un aviso lleva adjuntos al salir, en orden (ADR 0019, decisión 6).
Adjuntos = Callable[[Momento, dict[str, Any]], list[str]]


@dataclass(frozen=True)
class TipoDeAviso:
    """Un tipo de aviso guardado: cómo sale y cuándo todavía corresponde. `vigente` devuelve
    el motivo para omitirlo, o `None` y los hechos de ese momento."""

    nombre: str
    tipo_de_mensaje: str            # `message_outbox.tipo`
    vigente: Vigencia
    es_coordinacion: bool = False   # lo causa el acto de otra persona (mecánica §10)
    escala: bool = False            # al salir, la espera queda escalada
    adjuntos: Adjuntos | None = None    # sólo un aviso de coordinación, que sale solo
    # La decisión que ofrece al salir: las jugadas cuyas opciones lleva como botones
    # (`Ficha.boton`). Sólo un aviso de coordinación, que sale solo (porción 3b).
    ofrece: tuple[str, ...] = ()
    # La decisión que recuerda (el tipo de su pregunta): la ofreció otro aviso y sigue sin
    # cerrar. Al salir no abre ninguna pregunta ni lleva botones (9b): la redacción la recibe
    # como la pregunta del mensaje, ya hecha antes, y se contesta escribiendo o con los botones
    # de aquel aviso (porción 3c).
    recuerda: str | None = None
    # A quién le lleva el enlace a la página de su tarea (ADR 0019, 7a): `destinatario`, siempre
    # a quien lo recibe; `responsable`, sólo si quien lo recibe es el responsable de la tarea.
    # Sólo un aviso de coordinación, que sale solo.
    enlace: str | None = None


# El hecho que le dice a la IA que el mensaje lleva al final el enlace a la página de la tarea.
LLEVA_EL_ENLACE = "lleva_el_enlace_a_la_pagina_de_la_tarea"


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
    enlace = _enlace_del_envio(m, envio)
    if enlace is not None:
        envio = [replace(envio[0], hechos={**envio[0].hechos, LLEVA_EL_ENLACE: True}),
                 *envio[1:]]
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
    # Lo que lleva adjunto (las fotos de una entrega): otra fila de la misma respuesta, que el
    # despachador manda después del texto. Sólo el aviso de coordinación que sale solo.
    tipo = envio[0].tipo
    adjuntos = (tipo.adjuntos(m, envio[0].aviso)
                if tipo.adjuntos is not None and len(envio) == 1 else [])
    tipo_de_mensaje = max((x.tipo.tipo_de_mensaje for x in envio), key=URGENCIA.index)
    try:
        enqueue_outbox(cur, workspace_id=m.workspace_id,
                       chat_id=destinatario["telegram_user_id"], text=texto, dedupe_key=clave,
                       recipient_membership_id=persona, message_type=tipo_de_mensaje,
                       es_coordinacion=tipo.es_coordinacion, scheduled_for=m.ahora,
                       grupo_respuesta=clave if adjuntos else None, enlace_de_tarea=enlace)
        if adjuntos:
            # El texto de la fila del álbum es sólo el registro de lo que lleva: el álbum sale
            # sin texto (`salida.enqueue_outbox`, `adjuntos`).
            enqueue_outbox(cur, workspace_id=m.workspace_id,
                           chat_id=destinatario["telegram_user_id"],
                           text=f"(adjuntos: {len(adjuntos)})", dedupe_key=f"{clave}:adjuntos",
                           recipient_membership_id=persona, message_type=tipo_de_mensaje,
                           es_coordinacion=tipo.es_coordinacion, scheduled_for=m.ahora,
                           grupo_respuesta=clave, adjuntos=adjuntos)
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
        _auditar_el_envio(m, x.aviso, persona, outbox_id, len(adjuntos))
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
        if q is not None and x.tipo.ofrece:
            _ofrecer_la_decision(m, turno, x.aviso, x.tipo)
        elif q is not None and x.tipo.recuerda:
            pass                # la decisión sigue abierta desde el aviso que la ofreció
        elif q is not None:
            _abrir_la_pregunta(m, turno, x.aviso)
        if x.tipo.escala:
            # La espera que escala: la de su pregunta, o la del estado de la tarea.
            cur.execute("""update pending_reply set escalado_en = %s
                            where task_id = %s and tipo = %s
                              and satisfecho_en is null and escalado_en is null""",
                        (m.ahora, x.aviso["task_id"], _espera_del_aviso(x.hechos)))
    return ["enviado"] * len(envio)


def _enlace_del_envio(m: Momento, envio: list[_Listo]) -> tuple[str, str] | None:
    """La tarea y la persona del enlace a la página que lleva el envío, o `None`: sólo un aviso
    de un tipo que lo lleva (`TipoDeAviso.enlace`) y sale solo, con la dirección pública
    configurada, y si quien lo recibe puede ver la tarea (la regla vive en la base)."""
    x = envio[0]
    if len(envio) != 1 or x.tipo.enlace is None or x.aviso["task_id"] is None:
        return None
    from ..config import config

    if not config.base_url:
        return None
    task_id, persona = str(x.aviso["task_id"]), str(x.destinatario["membership_id"])
    if x.tipo.enlace == "responsable":
        tarea = leer_tarea(m.cur, task_id)
        if tarea is None or str(tarea["responsable_membership_id"]) != persona:
            return None
    m.cur.execute("select puede_ver_tarea(%s, %s) as ve", (persona, task_id))
    return (task_id, persona) if m.cur.fetchone()["ve"] else None


def _auditar_el_envio(m: Momento, aviso: dict[str, Any], persona: str, outbox_id: str,
                      adjuntos: int = 0) -> None:
    """Un aviso que sale es un envío de Leda (constitución §12): una fila por aviso, sobre su
    tarea, con la versión de las reglas (`auditoria`). El texto queda en el outbox, y lo que
    lleva adjunto, en `message_outbox_adjunto`."""
    sujeto = ("task", aviso["task_id"]) if aviso["task_id"] is not None \
        else ("scheduled_notice", aviso["id"])
    auditar(m.cur, accion="enviar_aviso", workspace_id=m.workspace_id,
            sujeto_tipo=sujeto[0], sujeto_id=sujeto[1],
            detalle={"aviso_id": aviso["id"], "tipo": aviso["tipo"],
                     "destinatario_membership_id": persona, "outbox_id": outbox_id,
                     **({"adjuntos": adjuntos} if adjuntos else {}),
                     "at": m.ahora.isoformat()})


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
    pregunta: dict[str, Any] = {"tipo": hechos.get("pregunta") or ESPERA_DE_ESTADO,
                                "tarea": {"titulo": hechos.get("tarea")}, "desde_antes": False}
    tipo = TIPOS.get(aviso["tipo"])
    if tipo is not None and tipo.ofrece:
        pregunta["opciones"] = [{"etiqueta": FICHAS[n].boton} for n in tipo.ofrece]
    if tipo is not None and tipo.recuerda:
        pregunta["desde_antes"] = True      # la hizo el aviso que la ofreció
    return pregunta


def _ofrecer_la_decision(m: Momento, turno, aviso: dict[str, Any], tipo: TipoDeAviso) -> None:
    """La decisión que ofrece el aviso, con una opción por jugada (su botón), atada a lo que el
    aviso mostró (la huella de lo entregado: la guarda del botón, ADR 0018, decisión 2). La que
    ofrecía un aviso anterior de la misma tarea queda reemplazada."""
    task_id = str(aviso["task_id"])
    preguntas.ofrecer(
        turno, preguntas.DECISION_DE_LA_ENTREGA, task_id,
        jugada={"nombre": "decidir_la_entrega", "del_aviso": str(aviso["id"]),
                "huella": entrega.huella_de_lo_entregado(m.cur, task_id)},
        opciones=[(FICHAS[n].boton, {"tarea": task_id, "jugada": n}) for n in tipo.ofrece])


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
    """Un envío que la IA no redactó. Cada aviso cuenta sus propios intentos (decisión 8, caso
    2): al quinto fallo queda `fallido` él solo, y un aviso que ya venía fallando no le quita
    intentos a los demás. Los que siguen vuelven a intentarse juntos, al próximo intento más
    cercano de entre ellos, así salen en un solo mensaje (mecánica §10) y ninguno espera más
    que lo que le toca a él."""
    cur = m.cur
    resultados, siguen = [], []
    for x in envio:
        intentos = x.aviso["intentos"] + 1
        if intentos < INTENTOS:
            siguen.append((x, intentos))
            resultados.append("reintento")
        else:
            resultados.append(_un_aviso_que_fallo(m, x.aviso, x.destinatario, falla, intentos))
    if siguen:
        proximo = min(m.ahora + ESPERAS_TRAS_UN_FALLO[n - 1] for _, n in siguen)
        for x, intentos in siguen:
            cur.execute("""update scheduled_notice set intentos = %s, proximo_intento_en = %s
                            where id = %s""", (intentos, proximo, str(x.aviso["id"])))
        _el_rastro_del_intento(m, siguen, falla, proximo)
    return resultados


def _el_rastro_del_intento(m: Momento, siguen: list[tuple[_Listo, int]], falla: Exception,
                           proximo: datetime) -> None:
    """Un incidente por envío que se reintenta, con la falla en la referencia técnica (que
    `registrar_incidente` sanea): sin él, un aviso que se demoró no deja cómo probar la causa
    (usuario, 2026-10-07). Severidad baja y sin avisar a la administración: un reintento no
    es para molestarla, y el quinto fallo la sigue avisando con su propio incidente."""
    intentos = sorted({n for _, n in siguen})
    cuales = (f"el intento {intentos[0]}" if len(intentos) == 1
              else f"los intentos {', '.join(map(str, intentos[:-1]))} y {intentos[-1]}")
    tipos = ", ".join(x.aviso["tipo"] for x, _ in siguen)
    cuantos = "un aviso guardado" if len(siguen) == 1 else f"{len(siguen)} avisos guardados"
    hora = proximo.astimezone(m.cal.zona).strftime("%H:%M")
    registrar_incidente(
        m.cur, m.workspace_id,
        f"La IA no redactó {cuantos} del motor de conversación ({tipos}, para "
        f"{siguen[0][0].destinatario['nombre']}) en {cuales}: se reintenta a las {hora}, "
        f"con sus hechos guardados.",
        severidad="baja", referencia_cruda=f"{type(falla).__name__}: {falla}",
        etapa=ETAPA_AVISO_REINTENTO, avisar_admin=False,
        sin_avisar_porque="un intento que se reintenta queda sólo como rastro; el quinto "
                          "fallo sí la avisa.")


def _un_aviso_que_fallo(m: Momento, aviso, destinatario, falla: Exception,
                        intentos: int) -> str:
    """El quinto fallo de un aviso: queda `fallido` con sus hechos, con su incidente y, si lo
    causó una persona, el aviso de la falla para ella."""
    cur, aviso_id = m.cur, str(aviso["id"])
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
                                               LLEGA: NO_LE_LLEGO,
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
    """La última previsión de la tarea, si no es la fecha comprometida, con su aviso al
    referente: a quién, y si ya le llegó o cuándo le llega (`fichas.LLEGA`)."""
    f = _prevision_vigente(m.cur, tarea["id"])
    if f is None or f["fecha_prevista"] == m.fecha(tarea["fecha_objetivo"]):
        return None
    # El atraso que tendrá si se cumple, no el de hoy: cada uno con su clave (`hechos.py`).
    dicha: dict[str, Any] = {"fecha": f["fecha_prevista"].isoformat(),
                             ATRASO_SI_SE_CUMPLE: f["atraso_dias_habiles"]}
    if f["motivo"]:
        dicha["motivo"] = f["motivo"]
    m.cur.execute("""select a.estado, a.programado_para, i.nombre from scheduled_notice a
                       join integrante i on i.membership_id = a.destinatario_membership_id
                      where a.workspace_id = %s and a.dedupe_key = %s""",
                  (m.workspace_id, f"motor:nueva_prevision:{f['id']}"))
    aviso = m.cur.fetchone()
    if aviso is not None and aviso["estado"] in ("enviado", "guardado", "fallido"):
        llega = (YA_LE_LLEGO if aviso["estado"] == "enviado"
                 else NO_LE_LLEGO if aviso["estado"] == "fallido"
                 else aviso["programado_para"].astimezone(m.cal.zona).isoformat())
        dicha["aviso_al_referente"] = {"a": aviso["nombre"], LLEGA: llega}
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


def espera_a(cur, task_id) -> list[dict[str, Any]]:
    """Las tareas que tienen que terminar antes de que ésta pueda arrancar, con su estado: sus
    dependencias bloqueantes sin cerrar (mecánica §4; la misma regla que
    `motivo_no_arranca_tarea`, en `db/esquema.sql`)."""
    cur.execute("""select t.titulo, t.estado::text estado from dependency d
                     join task t on t.id = d.origen_task_id
                    where d.destino_task_id = %s and d.tipo = 'bloqueante'
                      and t.estado not in ('terminada', 'cancelada')
                    order by t.titulo""", (str(task_id),))
    return [{"tarea": f["titulo"], "estado": f["estado"]} for f in cur.fetchall()]


# Lo que un pedido de estado espera saber depende del estado de la tarea (cuarta vuelta de
# ajuste, 2026-10-06; ronda 3: a una tarea sin empezar se le preguntó si estaba terminada): en
# curso, si la terminó; sin empezar, si la empezó; esperando a otra, no puede arrancar, así que
# ni una cosa ni la otra. Para cuándo la termina y si está trabada valen siempre.
SIN_EMPEZAR = ("si_la_empezo", "para_cuando_la_termina", "si_esta_trabada")
ESPERANDO_A_OTRA = ("para_cuando_la_termina", "si_esta_trabada")


def espera_saber(estado: str, esperando: list[dict[str, Any]]) -> list[str]:
    """Lo que Leda necesita saber de una tarea en ese estado: un hecho cierto."""
    if estado == "en_curso":
        return list(ESPERA_ALGO_CIERTO)
    return list(ESPERANDO_A_OTRA if esperando else SIN_EMPEZAR)


# --- Los avisos de la escalera ---------------------------------------------------------------
#
# La escalera (`escalera.py`) decide cuándo se guarda cada uno; acá están sus hechos y cuándo
# dejan de corresponder: la tarea ya no está abierta, está bloqueada, cambió su vencimiento o
# su responsable, o la persona ya contestó (la espera se cerró).

# Lo que se lee de nuevo en cada momento; lo demás de un aviso de la escalera es fijo (qué
# aviso es, el número de pedido, la ausencia). `avisa_que_va_a_escalar` es una marca del código
# que nunca llega a la IA: en su lugar van los hechos de a quién se escala.
_DE_ESTE_MOMENTO = frozenset({"tarea", "vence", "dias_habiles_hasta_el_vencimiento",
                              "atraso_dias_habiles", "estado", "estado_desde", "responsable",
                              "prevision_vigente", "dependientes", "espera_a",
                              "espera_algo_cierto", "si_no_hay_respuesta",
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
        _desde_y_espera(m, tarea, hechos)
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
    if base.get("necesita_respuesta") is True:
        hechos["espera_algo_cierto"] = espera_saber(tarea["estado"], hechos.get("espera_a", []))
    if tipo == VENCIMIENTO_CON_PREVISION:   # un efecto que pasa después: cuándo pide el estado
        hasta = ancla(m.cur, tarea["id"], m.fecha(vence))
        hechos["pide_el_estado_el"] = {"fecha": hasta.isoformat()}
    if base.get(AVISA_QUE_VA_A_ESCALAR):
        a_quienes = [d["nombre"] for d in quienes_escalan(m.cur, tarea)]
        if a_quienes:       # un efecto que pasa después: todavía no, y a quién
            hechos["si_no_hay_respuesta"] = {"se_avisa_a": a_quienes}
    return hechos


def _desde_y_espera(m: Momento, tarea: dict[str, Any], hechos: dict[str, Any]) -> None:
    """El estado real de la tarea, además de su nombre: desde cuándo lo tiene, si el motor lo
    sabe (`cambios_de_estado.desde`), y las tareas a las que espera para poder arrancar."""
    desde = cambios_de_estado.desde(m.cur, tarea["id"], tarea["responsable_membership_id"],
                                    tarea["estado"], m.cal.zona)
    if desde is not None:
        hechos["estado_desde"] = desde
    esperando = espera_a(m.cur, tarea["id"])
    if esperando:
        hechos["espera_a"] = esperando


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
    de este momento: la tarea, su vencimiento y, en la última repregunta, a quién se escala."""
    hechos = {k: v for k, v in base.items()
              if k not in _DE_ESTE_MOMENTO and k != AVISA_QUE_VA_A_ESCALAR}
    hechos["tarea"] = tarea["titulo"]
    if tarea["fecha_objetivo"] is not None:
        hechos["vence"] = m.fecha(tarea["fecha_objetivo"]).isoformat()
    if tarea.get("bloqueada"):
        hechos["estado"] = "bloqueada"
    if base.get(AVISA_QUE_VA_A_ESCALAR):
        a_quienes = [d["nombre"] for d in quienes_escalan(m.cur, tarea)]
        if a_quienes:       # un efecto que pasa después: todavía no, y a quién
            hechos["si_no_hay_respuesta"] = {"se_avisa_a": a_quienes}
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


# --- El aviso de una entrega a quien la aprueba (ADR 0019, decisión 6) --------------------------

ENTREGA_PARA_APROBAR = "entrega_para_aprobar"
# Por qué ya no sale: la tarea ya no espera la aprobación (le pidieron cambios, volvió atrás),
# cambió quién aprueba el trabajo del responsable, o hubo una entrega más nueva (T6i).
YA_NO_ESTA_ENTREGADA = "ya_no_esta_entregada"
CAMBIO_QUIEN_APRUEBA = "cambio_quien_aprueba"
HAY_UNA_ENTREGA_MAS_NUEVA = "hay_una_entrega_mas_nueva"
# Una foto se adjunta si el canal la muestra como foto: sin HEIC (Telegram no la muestra) y de
# hasta 10 MB (lo que Telegram deja subir como foto). Las demás se nombran, como los archivos.
_NO_SE_MUESTRA_COMO_FOTO = frozenset({"image/heic"})
_FOTO_HASTA = 10 * 1024 * 1024


def guardar_aviso_de_entrega(ctx, tarea: dict[str, Any], entrega_id: str
                             ) -> tuple[str, datetime] | None:
    """El aviso de una entrega confirmada a quien aprueba el trabajo del responsable: sale
    terminado el margen para corregir (`margen.py`), como todo aviso a otra persona que causa lo
    que alguien dijo. Su clave se ata al acto de la entrega (`entrega_id`, de la cocina). Un aviso
    de una entrega anterior de la misma tarea que todavía espera queda omitido: lo reemplaza éste,
    que al salir lleva toda la evidencia vigente (ADR 0009, enmienda T6i). (id, cuándo sale), o
    `None` si nadie aprueba su trabajo."""
    cur = ctx.cur
    quien = referente(cur, ctx.quien.membership_id)
    if quien is None:
        return None
    cur.execute("""update scheduled_notice
                      set estado = 'omitido', motivo_omision = %s, resuelto_en = %s,
                          proximo_intento_en = null
                    where task_id = %s and tipo = %s and estado = 'guardado'""",
                (HAY_UNA_ENTREGA_MAS_NUEVA, ctx.ahora, tarea["id"], ENTREGA_PARA_APROBAR))
    sale = sale_con_margen(cur, ctx.calendario, ctx.quien.workspace_id, ctx.ahora)
    aviso_id, _ = guardar(
        cur, ctx.quien.workspace_id, ENTREGA_PARA_APROBAR, task_id=tarea["id"],
        destinatario=quien["membership_id"],
        hechos={"aviso": ENTREGA_PARA_APROBAR, "necesita_respuesta": True,
                "pregunta": preguntas.DECISION_DE_LA_ENTREGA,
                "tarea": tarea["titulo"], "responsable": ctx.quien.nombre},
        programado_para=sale, clave=f"motor:{ENTREGA_PARA_APROBAR}:{entrega_id}",
        ahora=ctx.ahora)
    return aviso_id, sale


def _es_foto_adjunta(p: dict[str, Any]) -> bool:
    return (p["clase"] == "imagen" and p.get("archivo_id") is not None
            and p.get("tipo_del_archivo") not in _NO_SE_MUESTRA_COMO_FOTO
            and (p.get("tamano") or 0) <= _FOTO_HASTA)


def _lo_entregado_para_aprobar(m: Momento, task_id) -> tuple[list[dict[str, Any]], list[str]]:
    """Lo que entregó el responsable, releído ahora (la evidencia del ciclo vigente, sin lo
    retirado: `entrega._lo_entregado`), pieza por pieza como lo recibe la IA, y las fotos que van
    adjuntas: las primeras diez que el canal muestra como foto."""
    piezas = entrega._lo_entregado(m.cur, str(task_id))
    pol = entrega.politica(m.cur, str(task_id))
    adjuntas: list[str] = []
    vistas = []
    for p, vista in zip(piezas, entrega.mostrar(piezas, pol, m.cal.zona)):
        vista.pop("pieza", None)            # el alias es para sacar una pieza: acá no sirve
        if p["clase"] == "imagen":
            va = _es_foto_adjunta(p) and len(adjuntas) < MAX_ADJUNTOS
            if va:
                adjuntas.append(p["archivo_id"])
            vista["va_adjunta"] = va
        vistas.append(vista)
    return vistas, adjuntas


def _vigencia_de_la_entrega(m: Momento, aviso) -> tuple[str | None, dict[str, Any]]:
    """El aviso de una entrega corresponde mientras la tarea espere la aprobación de quien lo
    recibe. Sus hechos son los de ahora: lo entregado vigente, cuántas fotos van adjuntas y, si
    después de entregar se retiró algo y la política quedó incompleta, qué falta."""
    tarea = leer_tarea(m.cur, aviso["task_id"])
    if tarea is None:
        return "tarea_inexistente", {}
    if tarea["estado"] in ("terminada", "cancelada"):
        return "tarea_cerrada", {}
    if tarea["estado"] != "en_revision":
        return YA_NO_ESTA_ENTREGADA, {}
    quien = referente(m.cur, str(tarea["responsable_membership_id"]))
    if quien is None or quien["membership_id"] != str(aviso["destinatario_membership_id"]):
        return CAMBIO_QUIEN_APRUEBA, {}
    vistas, adjuntas = _lo_entregado_para_aprobar(m, tarea["id"])
    hechos = {k: v for k, v in dict(aviso["hechos"]).items()
              if k in ("aviso", "necesita_respuesta", "pregunta", "responsable")}
    hechos.update(tarea=tarea["titulo"], lo_que_entrego=vistas, fotos_adjuntas=len(adjuntas))
    faltan = entrega._faltan(m.cur, str(tarea["id"]), [])
    if faltan:
        pol = entrega.politica(m.cur, str(tarea["id"]))
        hechos["todavia_le_falta"] = [pol.en_palabras(t) for t in faltan]
    return None, hechos


def _adjuntos_de_la_entrega(m: Momento, aviso) -> list[str]:
    return _lo_entregado_para_aprobar(m, aviso["task_id"])[1]


def _siempre(m: Momento, aviso) -> tuple[str | None, dict[str, Any]]:
    return None, dict(aviso["hechos"])


# --- Los avisos de la decisión de quien aprueba (porción 3b; `aprobacion.py`) -------------------

TAREA_APROBADA = "tarea_aprobada"
PEDIDO_DE_CAMBIOS = "pedido_de_cambios"
CERRADA_CON_LA_APROBACION = "cerrada_con_la_aprobacion"
# Por qué ya no sale: después de la aprobación hubo un pedido de cambios, o la tarea se cerró
# después y el aviso del cierre lo cuenta.
HAY_UNA_DECISION_MAS_NUEVA = "hay_una_decision_mas_nueva"
SE_CERRO_DESPUES = "se_cerro_despues"


def _vigencia_de_una_aprobacion(m: Momento, aviso) -> tuple[str | None, dict[str, Any]]:
    """El aviso de una aprobación corresponde mientras esa aprobación (la última parte de su
    clave) siga valiendo; el de una que no alcanzaba para cerrar, mientras la tarea no se haya
    cerrado después (ése lo cuenta el aviso del cierre)."""
    tarea = leer_tarea(m.cur, aviso["task_id"])
    if tarea is None:
        return "tarea_inexistente", {}
    aprobacion_id = aviso["dedupe_key"].rsplit(":", 1)[-1]
    m.cur.execute("""select 1 from approval a
                       join approval r on r.sujeto_id = a.sujeto_id
                                      and r.decision = 'rechazado'
                                      and r.aprobador_membership_id = a.aprobador_membership_id
                                      and r.at >= a.at
                      where a.id = %s limit 1""", (aprobacion_id,))
    if m.cur.fetchone() is not None:
        return HAY_UNA_DECISION_MAS_NUEVA, {}
    hechos = dict(aviso["hechos"])
    if not hechos.get("quedo_terminada") and tarea["estado"] == "terminada":
        return SE_CERRO_DESPUES, {}
    return None, hechos


def _vigencia_de_un_pedido_de_cambios(m: Momento, aviso) -> tuple[str | None, dict[str, Any]]:
    """El aviso de un pedido de cambios, con el estado y el vencimiento de la tarea de ahora."""
    tarea = leer_tarea(m.cur, aviso["task_id"])
    if tarea is None:
        return "tarea_inexistente", {}
    hechos = dict(aviso["hechos"])
    hechos["estado"] = tarea["estado"]
    if tarea["fecha_objetivo"] is not None:
        hechos["vence"] = m.fecha(tarea["fecha_objetivo"]).isoformat()
    return None, hechos


# --- Quien aprueba no contesta (porción 3c; `escalera.py`, "La espera de una decisión") ---------

RECORDATORIO_DE_LA_DECISION = "recordatorio_de_la_decision"
APROBACION_TRABADA = "aprobacion_trabada"
APROBACION_DESTRABADA = "aprobacion_destrabada"
# Por qué ya no sale: quien aprueba ya decidió (una aprobación que todavía no cierra también es
# su decisión), o cambió quién aprueba el trabajo de quien aprueba.
YA_DECIDIO = "ya_decidio"
CAMBIO_QUIEN_ESTA_ARRIBA = "cambio_quien_esta_arriba"


def aprobacion_vigente(cur, task_id: str, aprobador: str) -> dict[str, Any] | None:
    """La última aprobación de esa persona sobre la tarea que ningún pedido de cambios suyo
    posterior dejó sin efecto (la misma regla que `motivo_no_cierra_tarea`)."""
    cur.execute("""select a.id, a.at from approval a
                    where a.sujeto_tipo = 'tarea' and a.sujeto_id = %s
                      and a.decision = 'aprobado' and a.aprobador_membership_id = %s
                      and not exists (select 1 from approval r
                                       where r.sujeto_tipo = 'tarea'
                                         and r.sujeto_id = a.sujeto_id
                                         and r.aprobador_membership_id = %s
                                         and r.decision = 'rechazado' and r.at >= a.at)
                    order by a.at desc limit 1""", (str(task_id), aprobador, aprobador))
    return cur.fetchone()


def aviso_de_la_entrega(cur, task_id) -> dict[str, Any] | None:
    """El aviso de la última entrega de la tarea a quien la aprueba, salga o no: el que vale. La
    espera de la decisión se cuenta desde que ése salió."""
    cur.execute("""select * from scheduled_notice where task_id = %s and tipo = %s
                    order by creado_en desc, id desc limit 1""",
                (str(task_id), ENTREGA_PARA_APROBAR))
    return cur.fetchone()


def quien_esta_arriba(cur, aprobador: str, tarea: dict[str, Any]) -> dict[str, str] | None:
    """Quien aprueba el trabajo de quien aprueba la entrega (Nahuel → Marcos → Ismael), si hay
    alguien y no es el responsable de la tarea: a él nunca le llega nada de la espera de su
    decisión (no depende de él)."""
    arriba = referente(cur, aprobador)
    if arriba is None or arriba["membership_id"] == str(tarea["responsable_membership_id"]):
        return None
    return arriba


def hechos_de_una_decision(m: Momento, tarea: dict[str, Any], entrega_aviso: dict[str, Any],
                           base: dict[str, Any]) -> dict[str, Any]:
    """Lo fijo de `base` y lo de este momento: la tarea, quién la entregó y qué día (el del
    aviso de la entrega: lo guardó la confirmación)."""
    responsable = integrante(m.cur, tarea["responsable_membership_id"])
    return {**base, "tarea": tarea["titulo"],
            "responsable": responsable["nombre"] if responsable else None,
            "entregada_el": m.fecha(entrega_aviso["creado_en"]).isoformat()}


def _vigencia_de_una_decision(m: Momento, aviso) -> tuple[str | None, dict[str, Any]]:
    """Un recordatorio a quien aprueba, o el aviso a quien está arriba de que la aprobación está
    trabada, corresponde mientras la entrega de su clave sea la que espera y quien aprueba no
    haya decidido; cada uno, mientras vaya a quien es ahora quien aprueba o quien está arriba."""
    tarea = leer_tarea(m.cur, aviso["task_id"])
    if tarea is None:
        return "tarea_inexistente", {}
    if tarea["estado"] in ("terminada", "cancelada"):
        return "tarea_cerrada", {}
    if tarea["estado"] != "en_revision":
        return YA_NO_ESTA_ENTREGADA, {}
    entrega_aviso = aviso_de_la_entrega(m.cur, tarea["id"])
    if entrega_aviso is None or str(entrega_aviso["id"]) != aviso["dedupe_key"].split(":")[2]:
        return HAY_UNA_ENTREGA_MAS_NUEVA, {}
    aprobador = referente(m.cur, str(tarea["responsable_membership_id"]))
    if aprobador is None or \
            aprobador["membership_id"] != str(entrega_aviso["destinatario_membership_id"]):
        return CAMBIO_QUIEN_APRUEBA, {}
    if aprobacion_vigente(m.cur, str(tarea["id"]), aprobador["membership_id"]) is not None:
        return YA_DECIDIO, {}
    destinatario = str(aviso["destinatario_membership_id"])
    if aviso["tipo"] == APROBACION_TRABADA:
        arriba = quien_esta_arriba(m.cur, aprobador["membership_id"], tarea)
        if arriba is None or arriba["membership_id"] != destinatario:
            return CAMBIO_QUIEN_ESTA_ARRIBA, {}
    elif destinatario != aprobador["membership_id"]:
        return CAMBIO_QUIEN_APRUEBA, {}
    return None, hechos_de_una_decision(m, tarea, entrega_aviso, dict(aviso["hechos"]))


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
    # La entrega de una tarea, a quien la aprueba, con las fotos adjuntas (ADR 0019, decisión 6).
    TipoDeAviso(ENTREGA_PARA_APROBAR, "normal", _vigencia_de_la_entrega, es_coordinacion=True,
                adjuntos=_adjuntos_de_la_entrega, ofrece=("aprobar", "pedir_cambios"),
                enlace="destinatario"),
    # La decisión de quien aprueba, al responsable, y el cierre que hace el sistema (porción 3b).
    TipoDeAviso(TAREA_APROBADA, "informativo", _vigencia_de_una_aprobacion,
                es_coordinacion=True, enlace="responsable"),
    TipoDeAviso(PEDIDO_DE_CAMBIOS, "normal", _vigencia_de_un_pedido_de_cambios,
                es_coordinacion=True, enlace="responsable"),
    TipoDeAviso(CERRADA_CON_LA_APROBACION, "informativo", _siempre, es_coordinacion=True,
                enlace="responsable"),
    # Quien aprueba no contesta (porción 3c): el seguimiento que Leda hace por su cuenta, dentro
    # del tope diario y en un envío por persona (mecánica §10). El recordatorio recuerda la
    # decisión que ofreció el aviso de la entrega, sin botones (9b); el aviso a quien está
    # arriba es sólo informativo. Que se destrabó lo causa la decisión de quien aprueba: es de
    # coordinación, como el aviso de la decisión al responsable.
    TipoDeAviso(RECORDATORIO_DE_LA_DECISION, "seguimiento", _vigencia_de_una_decision,
                recuerda=preguntas.DECISION_DE_LA_ENTREGA),
    TipoDeAviso(APROBACION_TRABADA, "informativo", _vigencia_de_una_decision),
    TipoDeAviso(APROBACION_DESTRABADA, "informativo", _siempre, es_coordinacion=True),
)})


def _json(valor: Any) -> str:
    return json.dumps(valor, ensure_ascii=False, default=str)

