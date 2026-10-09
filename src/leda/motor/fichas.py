"""La lista cerrada de jugadas y sus fichas.

Diseño probado en la Etapa 2 (E2-3; `odd/tasks/prueba-chica-del-motor.md`, sección 4,
"Jugadas"); ADR 0018, decisiones 1, 4 y 9.

Cada jugada se declara con una ficha: qué datos necesita, qué comprueba el código, qué efecto
hace y qué pasa después. La comprobación común (los datos que faltan, la tarea por su alias y
los estados en que la jugada vale) la hace `correr` igual para todas; el manejador de cada
ficha hace sólo lo suyo. Las jugadas del recordatorio no confirman (9a): el efecto va directo,
con `herramientas.ejecutar(..., ya_confirmada=True)`, que verifica la autoridad igual y lo
audita. La entrega sí lleva confirmación (ADR 0018, decisión 4): `entregar` muestra la vista
previa y `confirmar`, con la guarda de la decisión 2, la ejecuta (`entrega.py`).
Lo que una ficha escribe directo, sin la cocina (una previsión y su corrección, quién destraba,
un avance), lo audita ella, con la versión de las reglas (`auditoria.py`).

El resultado de una jugada son hechos (un dict), nunca un texto: la IA redacta desde ellos. Una
jugada que existe pero no se puede hacer ahora devuelve por qué (`no_se_puede`), sin aviso al
administrador (decisión 1). Las tareas viajan por su alias; un id de la base nunca llega a la
IA. Cada jugada corre en su propio punto de guardado: si falla, lo suyo se deshace.

Las jugadas de las situaciones generales (`elegir`, `corregir`, `cancelar`,
`dejar_para_despues`) están en `situaciones.py`, y las preguntas, en `preguntas.py` (E2-4); acá
se declaran con las demás. Cada ficha declara lo suyo para ellas: qué preguntas contesta
(`contesta`) y cómo se deshace lo que anota (`deshacer`, para una corrección, 9f). La duda
también es común: si a una jugada le falta la tarea, se pregunta con las tareas en que vale
como opciones (situación general 5). Y lo que una jugada le propone a la persona (`propone`)
queda como tema abierto, una pregunta como cualquier otra (`preguntas.PROPUESTA`; decisión del
usuario, 2026-10-05).

**Una fecha que atrasa lleva su explicación** (decisión del usuario, 2026-10-07; ADR 0018, 9n):
si la previsión queda después del vencimiento y la persona no dio el porqué, se anota igual y
Leda pregunta qué la atrasa (`preguntas.MOTIVO_DEL_ATRASO`); el aviso al referente espera la
respuesta hasta el final del día de trabajo (`margen.sale_esperando_el_motivo`) y, si sale sin
ella, lo dice. El porqué llega como otra previsión de la misma fecha, que reemplaza el aviso.
Una fecha que corre otra vez un atraso de la misma tarea explicado hace menos de una hora, sin
que la persona hablara de otra cosa en el medio, conserva ese porqué; si no, se pregunta de
nuevo (`_el_porque_sigue_valiendo`).

**Con la tarea vencida, una respuesta sin fecha lleva la pregunta de para cuándo** (decisión del
usuario, 2026-10-05; ADR 0018, 9j; conversación 16), también común: si la tarea pasó su fecha de
seguimiento (la comprometida o, si es posterior, la previsión: el ancla, 9i), lo que la jugada
anotó queda anotado y, si no es algo cierto sobre cuándo (`Ficha.algo_cierto`: una fecha o un
bloqueo lo son; un inicio o un avance, no), la espera del estado sigue abierta, Leda vuelve a
pedirlo el día hábil siguiente con la cuenta de nuevo (como después de un avance, 9h) y, en esa
misma respuesta, pregunta para qué día la va a tener. Los hechos dicen que venció y el atraso.
"""

from __future__ import annotations

import json
import unicodedata
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from functools import cached_property
from types import MappingProxyType
from typing import Any

import psycopg

from ..autoridad import Denegado, Solicitante
from ..calendario import Calendario
from ..herramientas import (EstadoCambio, NecesitaConfirmacion, NecesitaElegir,
                            NecesitaOpciones, ejecutar)

from . import cambios_de_estado, preguntas, situaciones
from .ancla import (REEMPLAZADO_POR_UN_AVANCE, REPREGUNTA_DE_ESTADO, anclaje, candado, escalo,
                    pasos)
from .auditoria import auditar
from .ia import Jugada
from .margen import sale_con_margen, sale_esperando_el_motivo
from .tiempo import sale_el


@dataclass(frozen=True)
class Contexto:
    """Lo que un manejador de jugada necesita: la transacción del espacio, quién escribió,
    el momento del motor y lo leído al empezar el turno. `avisos_guardados` junta los
    avisos que guardan las jugadas del turno, para atarlos al turno al registrarlo."""

    cur: psycopg.Cursor
    quien: Solicitante
    entrante_id: str | None         # None: el turno es un toque
    chat_id: int
    texto: str
    ahora: datetime
    estado: dict[str, Any] | None
    tareas: tuple[dict[str, Any], ...]
    ultimos_turnos: tuple[dict[str, Any], ...]
    avisos_guardados: list[str] = field(default_factory=list)
    ultimo_aviso: dict[str, Any] | None = None     # el último que Leda le mandó, y su tarea
    preguntas_del_turno: list[str] = field(default_factory=list)   # abiertas en este turno
    dejadas: list[str] = field(default_factory=list)   # dejadas para después en este turno
    toque: str | None = None        # si el turno es un toque, la etiqueta de la opción tocada
    # La lista cerrada de este turno (nombre → manejador): una opción elegida corre la jugada que
    # esperaba por ella, como una jugada escrita. `None`: la de siempre (`JUGADAS`).
    jugadas: Mapping[str, Callable[..., dict[str, Any]]] | None = None
    # Lo que trajo el mensaje y puede ir a una entrega (`entrega.lo_que_trae`): el texto sin sus
    # enlaces, los enlaces y los archivos guardados; `tomada`, si una jugada ya lo sumó.
    llegada: dict[str, Any] = field(default_factory=dict)
    # Las entregas de otras personas que esperan la decisión de quien escribe (porción 3b de la
    # C-3; `aprobacion.para_decidir`), con su alias, después de las suyas: no son tareas suyas.
    para_aprobar: tuple[dict[str, Any], ...] = ()
    # Las tareas trabadas de otras personas que destraba quien escribe (C-5; `persecucion.
    # para_destrabar`), con su alias, después de las anteriores: no son tareas suyas.
    para_destrabar: tuple[dict[str, Any], ...] = ()
    # Las tareas de otras personas cuyo pase espera algo de quien escribe: su decisión o que la
    # tome (C-7; `pase.para_contestar`), con su alias, después de las anteriores.
    pases: tuple[dict[str, Any], ...] = ()
    # Las decisiones ofrecidas en la respuesta de este turno (`preguntas.ofrecer_en_la_
    # respuesta`): sus botones salen con ella, sin ser un tema abierto (C-3d, D4).
    ofrecidas: list[str] = field(default_factory=list)
    # Lo que la respuesta lleva además de su texto cuando muestra una entrega (`aprobacion.
    # ver_entrega`; decisión 17): las fotos, en un álbum después del texto, y el enlace a la
    # página de la tarea, uno solo por mensaje: `(tarea, persona)`.
    adjuntos_de_la_respuesta: list[str] = field(default_factory=list)
    enlace_de_la_respuesta: list[tuple[str, str]] = field(default_factory=list)
    # Los nombres de las jugadas que la IA eligió para este mensaje, también las que quedan fuera
    # de la lista: una jugada mira si el mensaje también dice otra cosa (`entrega.
    # _contesta_otra_cosa`, D7).
    elegidas: list[str] = field(default_factory=list)

    def tarea(self, alias: str) -> dict[str, Any] | None:
        """Una tarea por su alias: de las suyas, de las que esperan su decisión, de las que
        destraba o de las que le quieren pasar."""
        return next((t for t in self.tareas + self.para_aprobar + self.para_destrabar
                     + self.pases if t["alias"] == alias), None)

    def suya(self, alias: str) -> dict[str, Any] | None:
        """Una tarea suya por su alias: de la que es responsable."""
        return next((t for t in self.tareas if t["alias"] == alias), None)

    @cached_property
    def calendario(self) -> Calendario:
        return Calendario.desde_base(self.cur, self.quien.workspace_id)


Manejador = Callable[[Contexto, Jugada], dict[str, Any]]


# Una tarea abierta: comprometida y sin cerrar (mecánica §3).
ESTADOS_ABIERTOS = frozenset({"asignada", "en_curso", "bloqueada", "en_revision"})


@dataclass(frozen=True)
class Ficha:
    """Una jugada de la lista cerrada (ADR 0018, decisión 4)."""

    nombre: str
    para_que: str                   # qué hace, para decirle a la persona qué puede pedir
    necesita: tuple[str, ...]       # datos sin los que no se hace
    opcional: tuple[str, ...]
    comprueba: str
    hace: str
    despues: str
    manejar: Callable[[Contexto, dict[str, Any], dict[str, Any] | None], dict[str, Any]]
    del_responsable: bool = False   # la tarea tiene que ser de quien escribe
    # En qué estados de la tarea vale, si es del responsable: por omisión, abierta.
    estados: frozenset[str] = ESTADOS_ABIERTOS
    # False: no está entre lo que Leda dice que puede hacer: se reconoce pero no se hace por
    # chat (9g), o es de una situación general.
    se_ofrece: bool = True
    contesta: tuple[str, ...] = ()  # las preguntas sobre su tarea que contesta al anotarse
    # Si al anotarse decide la entrega de su tarea (aprobar, pedir cambios): las demás preguntas
    # sin cerrar sobre esa tarea, de cualquier persona, se cierran con esa decisión (D8: el botón
    # para ver una entrega ya decidida quedaba abierto para siempre).
    decide_la_tarea: bool = False
    # Cómo se deshace lo que anotó, agregando hechos (9f): `None` si no hay nada que deshacer;
    # si no, los hechos de la corrección y los datos para anotarlo en la tarea correcta.
    deshacer: Callable[[Contexto, dict[str, Any]], dict[str, Any] | None] | None = None
    # Lo que Leda le propone a la persona en sus hechos (las jugadas o salidas que puede elegir):
    # queda como tema abierto (`preguntas.PROPUESTA`). `None`: no propone nada.
    propone: Callable[[dict[str, Any]], list[str] | None] | None = None
    # Cómo se corrige lo que la jugada mostró o escribió, si lo sabe ella (una vista previa que
    # todavía no se confirmó, o piezas ya entregadas): `corregir` la llama en lugar de deshacer.
    corregir: Callable[[Contexto, dict[str, Any], dict[str, Any]], dict[str, Any]] | None = None
    # Si lo que anota es algo cierto sobre la tarea (una fecha, un bloqueo): con la tarea
    # vencida, lo que no lo es lleva la pregunta de para cuándo (9j).
    algo_cierto: bool = False
    # Si su manejador ya sigue el pedido de estado (un avance, 9h): la regla de la tarea vencida
    # no guarda otro pedido.
    sigue_el_pedido: bool = False
    # Qué es la jugada para la IA que elige: lo que la persona dice para que sea ésta y en qué se
    # distingue de las parecidas, desde el núcleo (mecánica §3 y §8). Va en el esquema de la
    # herramienta, junto a sus datos (revisión del contrato, 2026-10-05). Describe la jugada,
    # nunca un caso ni una frase.
    es: str = ""
    # La etiqueta con que se ofrece como opción (un botón), si se ofrece.
    boton: str | None = None
    # La jugada que dice lo contrario sobre la misma tarea: las dos juntas en un mensaje admiten
    # dos lecturas y ninguna se hace (`dos_lecturas`).
    opuesta: str | None = None
    # Si toma lo que trajo el mensaje (sus archivos, sus enlaces y su texto: `entrega.py`). Si le
    # falta la tarea, su duda se queda con eso (`_duda`): lo que una jugada ya atendió no se
    # vuelve a atender al terminar las jugadas, y la elección lo usa.
    toma_lo_que_llego: bool = False


# Lo que Leda propone cuando no hay otra persona que destrabe el bloqueo (la persona no sabe
# quién, o le toca a la persona misma; 9c, corregida el 2026-10-05): que alguien la ayude, o más tiempo,
# que es la jugada de la nueva previsión.
SALIDAS_DE_UN_BLOQUEO = ("que_alguien_ayude", "anotar_prevision")

# Lo que pasa después se cuenta como pasa en el mundo: a quién le llega y cuándo (`llega`, con
# la fecha y hora en que se entera, que todavía no pasó), o que ya le llegó, que no le va a
# llegar o que no le llegó. Nunca el estado interno de un aviso (guardado, en cola, sin enviar):
# en la prueba por Telegram real Leda lo repetía ("el aviso a Ismael está guardado, todavía no
# salió"), y el usuario decidió el 2026-10-06 que Leda habla del mundo y no de la cocina. La
# honestidad sigue (constitución §4; primer contacto real, 2026-10-05, un aviso con sólo `a` y
# su hora se contó como enviado): lo que todavía no pasó trae cuándo pasa, nunca se da por hecho.
LLEGA = "llega"
YA_LE_LLEGO = "ya_le_llego"
NO_LE_VA_A_LLEGAR = "no_le_va_a_llegar"
NO_LE_LLEGO = "no_le_llego"

# Un avance sin un hecho cierto (`informar_avance`, decisión del usuario, 2026-10-05): la espera
# sigue abierta y Leda vuelve a pedir el estado el día hábil siguiente con un aviso de la
# escalera (`REPREGUNTA_DE_ESTADO`, `escalera.py`), que espera algo cierto. Los pasos de la
# escalera que todavía no salieron quedan reemplazados por él (`REEMPLAZADO_POR_UN_AVANCE`): ya
# no es silencio. Lo que espera saber depende del estado de la tarea (`avisos.espera_saber`):
# esto es lo de una tarea en curso.
ESPERA_ALGO_CIERTO = ("si_la_termino", "para_cuando_la_termina", "si_esta_trabada")

# Una fecha que atrasa y llegó sin su porqué (usuario, 2026-10-07; ADR 0018, 9n): su aviso al
# referente lo espera (`ESPERA_EL_MOTIVO`, en el hecho de la persona) y, si sale sin él, lo dice
# (`SIN_MOTIVO_TODAVIA`, en los hechos del aviso). Si el porqué llega antes, el aviso que lo
# esperaba no sale (`LLEGO_EL_MOTIVO`): sale otro que lo lleva. Sus significados, en `hechos.py`.
ESPERA_EL_MOTIVO = "espera_el_motivo"
SIN_MOTIVO_TODAVIA = "sin_motivo_todavia"
LLEGO_EL_MOTIVO = "llego_el_motivo"

# Cuánto vale el porqué que la persona ya dio para el atraso de una tarea, cuando corre otra vez
# la fecha sin decirlo (usuario, 2026-10-07: "Marcos habla con Leda a la mañana sobre el motivo,
# durante el día tienen otras conversaciones o no, y al final del día dice directamente otra
# fecha… para Leda es difícil saber que se refiere a ese motivo; hay que poner un límite de
# tiempo más corto"): en minutos desde que lo dijo, del espacio en `workspace_setting`. 60 es el
# valor del producto. Un valor que no es un número entero de minutos, 0 o más, usa el del
# producto.
CLAVE_MOTIVO_VALE = "motivo_vale_minutos"
MOTIVO_VALE_POR_OMISION = timedelta(minutes=60)


def motivo_vale(cur, workspace_id: str) -> timedelta:
    """Cuánto vale un porqué ya dicho: el del espacio o, si no es un número entero de minutos,
    0 o más, el del producto."""
    cur.execute("select valor from workspace_setting where workspace_id = %s and clave = %s",
                (workspace_id, CLAVE_MOTIVO_VALE))
    fila = cur.fetchone()
    valor = fila["valor"] if fila else None
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
        return MOTIVO_VALE_POR_OMISION
    return timedelta(minutes=valor)


def _cuando_lo_dijo(cur, prevision: dict[str, Any]) -> datetime:
    """Cuándo dio la persona el porqué de una previsión: la más vieja de la cadena que lleva el
    mismo porqué sin interrupción. Así un porqué que se conservó no vuelve a empezar la cuenta."""
    momento, f, vistas = prevision["at"], prevision, {str(prevision["id"])}
    while f["reemplaza_id"] is not None and str(f["reemplaza_id"]) not in vistas:
        cur.execute("""select id, motivo, at, reemplaza_id from task_forecast
                        where id = %s""", (f["reemplaza_id"],))
        antes = cur.fetchone()
        if antes is None or antes["motivo"] != prevision["motivo"]:
            break
        vistas.add(str(antes["id"]))
        momento, f = antes["at"], antes
    return momento


def _siguio_en_la_tarea(ctx: Contexto, titulo: str, desde: datetime) -> bool:
    """Si, desde el mensaje en que la persona dio el porqué (el primero suyo registrado a partir
    de `desde`), cada mensaje suyo habló sólo de esa tarea: cada hecho de su turno nombra esa
    tarea. Un mensaje sobre otra tarea, una jugada sin tarea (contar sus pendientes) o uno sin
    jugadas (una pregunta sobre otra cosa) cortan el hilo. Lo que manda Leda no cuenta: sólo los
    turnos de entrada."""
    ctx.cur.execute("""select resultado -> 'hechos' as hechos from conversation_turn
                        where membership_id = %s and sentido = 'entrada' and at >= %s
                        order by numero""", (ctx.quien.membership_id, desde))
    despues = ctx.cur.fetchall()[1:]        # el primero es el que dio el porqué
    for turno in despues:
        hechos = turno["hechos"] if isinstance(turno["hechos"], list) else []
        if not hechos or any(not isinstance(h, dict)
                             or (h.get("tarea") or {}).get("titulo") != titulo
                             for h in hechos):
            return False
    return True


def _el_porque_sigue_valiendo(ctx: Contexto, tarea: dict[str, Any],
                              anterior: dict[str, Any]) -> bool:
    """Si el porqué de la previsión anterior todavía explica una fecha nueva de la misma tarea que
    llega sin porqué (usuario, 2026-10-07). Valen las dos condiciones juntas:

    1. lo dijo hace menos de una hora (`motivo_vale`, del espacio; se cuenta desde que lo dijo,
       no desde la última fecha que lo conservó, `_cuando_lo_dijo`);
    2. desde entonces la persona habló sólo de esa tarea (`_siguio_en_la_tarea`).

    Si una falla, Leda no sabe si se refiere a ese porqué: lo pregunta otra vez (9n)."""
    dicho_en = _cuando_lo_dijo(ctx.cur, anterior)
    return (ctx.ahora - dicho_en <= motivo_vale(ctx.cur, ctx.quien.workspace_id)
            and _siguio_en_la_tarea(ctx, tarea["titulo"], dicho_en))

# El atraso que tendrá la tarea si se cumple una previsión: distinto del atraso de hoy
# (`atraso_dias_habiles`), con su propia clave (revisión del contrato, 2026-10-05; ronda 1: el
# del aviso al referente se contó como el atraso de hoy). Su significado, en `hechos.py`.
ATRASO_SI_SE_CUMPLE = "atraso_si_se_cumple_la_prevision_dias_habiles"


# Lo que un hecho nombra y pasa después (un aviso guardado, una espera, una pregunta) puede
# cambiar por otra jugada del mismo mensaje: una fecha contesta la espera de un avance y su
# pedido del día siguiente ya no sale. Por eso el hecho lleva, en esta clave interna, el id de
# cada efecto que nombra, y al terminar todas las jugadas el turno vuelve a leerlos de la base y
# pone su estado final (`efectos.al_final_del_turno`; ADR 0018, 9k). La clave se saca antes de
# redactar: ni la IA ni el registro de turnos ven un id.
EFECTOS = "_efectos"
AVISO, ESPERA, PREGUNTA = "aviso", "espera", "pregunta"     # de qué tabla es el efecto


def nombrar_efecto(hecho: dict[str, Any], clave: str, de: str, efecto_id: Any) -> None:
    """Anota en el hecho que `clave` nombra el efecto `efecto_id` (un aviso, una espera o una
    pregunta), para leerlo al terminar el turno."""
    hecho.setdefault(EFECTOS, []).append({"clave": clave, "de": de, "id": str(efecto_id)})


def _juntar(hecho: dict[str, Any], mas: dict[str, Any]) -> None:
    """`hecho.update(mas)`, sin perder los efectos que ya nombraba el hecho."""
    for clave, valor in mas.items():
        if clave == EFECTOS:
            hecho.setdefault(EFECTOS, []).extend(valor)
        else:
            hecho[clave] = valor


def _es_un_aviso_al_referente(tipo: str) -> dict[str, Any]:
    """Los hechos de un aviso al referente dicen qué aviso son y que no piden respuesta: es
    información para él (9i)."""
    return {"aviso": tipo, "necesita_respuesta": False}
_PASOS_QUE_REEMPLAZA = ("pedido_de_estado", REPREGUNTA_DE_ESTADO, "escalamiento")


# --- Comprobación común --------------------------------------------------------------------

def correr(ficha: Ficha, ctx: Contexto, jugada: Jugada) -> dict[str, Any]:
    """La comprobación común y el manejador de la ficha; si la jugada se anotó, contesta las
    preguntas que esperaban eso (`preguntas.contestar`)."""
    datos = dict(jugada.datos or {})
    faltan = [k for k in ficha.necesita if _vacio(datos.get(k))]
    if "tarea" in faltan:
        return _duda(ficha, ctx, datos)
    if faltan:
        return _hecho(ficha, "falta_dato", falta=faltan)
    tarea = None
    if not _vacio(datos.get("tarea")) and "tarea" in ficha.necesita + ficha.opcional:
        tarea = ctx.tarea(str(datos["tarea"]))
        if tarea is None:
            return _hecho(ficha, "no_se_puede", motivo="tarea_desconocida")
    try:
        with ctx.cur.connection.transaction():
            if tarea is not None and ficha.del_responsable:
                # Leída de nuevo, bajo la RLS del espacio: el estado vigente, no el del
                # principio del turno (otra jugada del mismo mensaje pudo cambiarlo).
                fila = _exigir_responsable(ctx.cur, ctx.quien, tarea["id"])
                tarea = {**tarea, "estado": str(fila["estado"])}
                if tarea["estado"] not in ficha.estados:
                    # Desde cuándo, si el motor lo sabe (`cambios_de_estado.py`).
                    return _hecho(ficha, "no_se_puede", motivo="estado",
                                  tarea=_tarea(tarea), estado=tarea["estado"],
                                  estado_desde=cambios_de_estado.desde(
                                      ctx.cur, tarea["id"], ctx.quien.membership_id,
                                      tarea["estado"], ctx.calendario.zona))
            hecho = {"jugada": ficha.nombre, **ficha.manejar(ctx, datos, tarea)}
            de_la_tarea = tarea or ctx.tarea((hecho.get("tarea") or {}).get("alias", ""))
            if (de_la_tarea is not None and ficha.del_responsable
                    and hecho["jugada"] == ficha.nombre
                    and hecho.get("resultado") != "no_se_puede"):
                # Lo que dice de una tarea de la lista de la cadencia la contesta en la lista
                # (C-6, decisión 8): también lo que todavía no se anota (una entrega que espera
                # su confirmación, un bloqueo sin su causa), que sigue su propia pregunta.
                preguntas.marcar_en_la_lista(ctx, de_la_tarea["id"])
            if hecho.get("resultado") == "anotado" and hecho["jugada"] == ficha.nombre:
                if de_la_tarea is not None:
                    preguntas.contestar(ctx, ficha.nombre, ficha.contesta, de_la_tarea["id"])
                    if ficha.decide_la_tarea:
                        preguntas.cerrar_las_de_la_tarea(
                            ctx, de_la_tarea["id"], "sin_efecto",
                            {"tarea": de_la_tarea["id"], "ya_decidio": True})
            if hecho["jugada"] == ficha.nombre:
                # Primero la pregunta de la tarea vencida (9j) y después lo propuesto: si ya se
                # pregunta algo en esta respuesta, lo propuesto queda para después (un tema a
                # la vez; nunca dos preguntas juntas).
                _si_esta_vencida(ficha, ctx, hecho, de_la_tarea)
                _proponer(ficha, ctx, hecho, de_la_tarea)
            return hecho
    except Exception as e:      # el punto de guardado ya deshizo lo de esta jugada
        rechazo = _rechazo_del_dominio(e)
        if rechazo is None:
            raise
        resultado, mas = rechazo
        return _hecho(ficha, resultado, tarea=_tarea(tarea) if tarea else None, **mas)


def _proponer(ficha: Ficha, ctx: Contexto, hecho: dict[str, Any],
              tarea: dict[str, Any] | None) -> None:
    """Lo que la jugada le propone a la persona queda como tema abierto: una pregunta con lo
    propuesto, ordenada con las demás (un tema a la vez). Los hechos la nombran como a
    cualquier pregunta (`pregunta` o `pregunta_para_despues`)."""
    propuesto = ficha.propone(hecho) if ficha.propone is not None else None
    if not propuesto:
        return
    ahora, pregunta_id = preguntas.abrir_con_id(
        ctx, preguntas.PROPUESTA, tarea["id"] if tarea else None,
        jugada={"nombre": ficha.nombre, "propone": list(propuesto)})
    _nombrar_pregunta(hecho, _clave_de_pregunta(ahora), preguntas.PROPUESTA, pregunta_id)


def _si_esta_vencida(ficha: Ficha, ctx: Contexto, hecho: dict[str, Any],
                     tarea: dict[str, Any] | None) -> None:
    """La regla de la tarea vencida (9j, ver el módulo), igual para toda jugada que anota algo
    sobre una tarea del responsable sin que sea algo cierto sobre cuándo."""
    if (hecho.get("resultado") != "anotado" or tarea is None or ficha.algo_cierto
            or not ficha.del_responsable):
        return
    vencida = _vencida(ctx, tarea)
    if vencida is None:
        return
    hecho["vencida"] = vencida
    if not ficha.sigue_el_pedido:
        candado(ctx.cur, tarea["id"])
        _juntar(hecho, _seguir_pidiendo(ctx, tarea, _espera_del_estado(ctx, tarea),
                                        {"jugada": ficha.nombre,
                                         "dijo": (ctx.texto or ctx.toque or "").strip()}))
    fecha = preguntas.FECHA_DE_LA_TAREA
    if fecha not in (hecho.get("pregunta"), hecho.get("pregunta_para_despues")):
        _abrir_pregunta(ctx, hecho, fecha, tarea["id"], jugada={"nombre": ficha.nombre})


def _vencida(ctx: Contexto, tarea: dict[str, Any]) -> dict[str, Any] | None:
    """Si la tarea pasó su fecha de seguimiento (el ancla, 9i): la fecha comprometida, el atraso
    contra ella (lo calcula el código) y, si el ancla era una previsión, cuál. `None` si no."""
    cal = ctx.calendario
    ctx.cur.execute("select fecha_objetivo from task where id = %s", (tarea["id"],))
    fila = ctx.cur.fetchone()
    if fila is None or fila["fecha_objetivo"] is None:
        return None
    vence = fila["fecha_objetivo"].astimezone(cal.zona).date()
    de = anclaje(ctx.cur, tarea["id"], vence)
    if ctx.ahora.astimezone(cal.zona).date() <= de.fecha:
        return None
    return {"fecha_comprometida": vence.isoformat(),
            "atraso_dias_habiles": cal.habiles_entre(fila["fecha_objetivo"], ctx.ahora),
            **({"prevision_vencida": de.fecha.isoformat()} if de.fecha > vence else {})}


def _espera_del_estado(ctx: Contexto, tarea: dict[str, Any]) -> dict[str, Any]:
    """La espera del estado de la tarea: la abierta o, si la jugada la contestó (un inicio),
    una nueva: la respuesta no fue algo cierto sobre cuándo, así que se sigue esperando."""
    cur, persona = ctx.cur, ctx.quien.membership_id
    cur.execute("""select * from pending_reply
                    where membership_id = %s and task_id = %s and tipo = %s
                      and satisfecho_en is null
                    order by preguntado_en desc limit 1""",
                (persona, tarea["id"], preguntas.ESTADO_DE_LA_TAREA))
    espera = cur.fetchone()
    if espera is not None:
        return espera
    cal = ctx.calendario
    cur.execute(
        """insert into pending_reply (workspace_id, membership_id, task_id, tipo,
                                      preguntado_en, vence_en)
           values (%s, %s, %s, %s, %s, %s) returning *""",
        (ctx.quien.workspace_id, persona, tarea["id"], preguntas.ESTADO_DE_LA_TAREA, ctx.ahora,
         cal.dentro_de_jornada(cal.sumar_habiles(ctx.ahora, 1))))
    return cur.fetchone()


def _duda(ficha: Ficha, ctx: Contexto, datos: dict[str, Any]) -> dict[str, Any]:
    """Situación general 5: la jugada no dice de qué tarea habla. Leda no adivina: pregunta
    con las tareas de la persona en que la jugada vale como opciones, y la jugada espera la
    elección. Sin ninguna en que valga, lo dice."""
    candidatas = [t for t in ctx.tareas if t["estado"] in ficha.estados]
    if not candidatas:
        return _hecho(ficha, "no_se_puede", motivo="ninguna_tarea_posible")
    if ficha.toma_lo_que_llego:
        from . import entrega        # entrega importa fichas
        datos = {**datos, **entrega.para_la_duda(ctx)}
    ahora, pregunta_id = preguntas.abrir_con_id(
        ctx, preguntas.CUAL_TAREA, None, jugada={"nombre": ficha.nombre, "datos": datos},
        opciones_de_tareas=candidatas)
    hecho = _hecho(ficha, "falta_dato", falta=["tarea"])
    _nombrar_pregunta(hecho, _clave_de_pregunta(ahora), preguntas.CUAL_TAREA, pregunta_id)
    return hecho


def _nombrar_pregunta(hecho: dict[str, Any], clave: str, tipo: str,
                     pregunta_id: str | None = None) -> None:
    """Pone en los hechos la pregunta que abrió la jugada, siempre como un nombre (`pregunta` o
    `pregunta_para_despues`). Si la clave ya nombra otra (dos que quedaron para después), la
    nueva va a `otras_preguntas_para_despues`, una lista: nunca se pierde una y cada clave
    tiene siempre la misma forma. Con su id, el turno la vuelve a leer al terminar (`EFECTOS`)
    y la nombra como quedó."""
    if pregunta_id is not None:
        nombrar_efecto(hecho, clave, PREGUNTA, pregunta_id)
    nombrar_tipo_de_pregunta(hecho, clave, tipo)


def nombrar_tipo_de_pregunta(hecho: dict[str, Any], clave: str, tipo: str) -> None:
    antes = hecho.get(clave)
    if antes is None or antes == tipo:
        hecho[clave] = tipo
    elif tipo not in hecho.setdefault(OTRAS_PARA_DESPUES, []):
        hecho[OTRAS_PARA_DESPUES].append(tipo)


OTRAS_PARA_DESPUES = "otras_preguntas_para_despues"


def _clave_de_pregunta(ahora: bool) -> str:
    """En el hecho de una jugada, la pregunta que abrió: la que se hace ahora (`pregunta`) o
    una que quedó para después (`pregunta_para_despues`), que no se hace en esta respuesta."""
    return "pregunta" if ahora else "pregunta_para_despues"


def _rechazo_del_dominio(e: Exception) -> tuple[str, dict[str, Any]] | None:
    """Lo que `herramientas.ejecutar` levanta como respuesta del dominio, en hechos; `None`
    si es una falla de verdad. Nunca su texto: puede traer detalles técnicos (§10)."""
    if isinstance(e, Denegado):
        return "no_se_puede", {"motivo": "no_autorizado"}
    if isinstance(e, NecesitaElegir):
        return "falta_dato", {"falta": [e.campo],
                              "coinciden": [nombre for nombre, _ in e.opciones]}
    if isinstance(e, (NecesitaConfirmacion, EstadoCambio, NecesitaOpciones)):
        # Con `ya_confirmada` no deberían llegar: piden un paso que esta jugada no tiene.
        return "no_se_puede", {"motivo": "pide_otro_paso"}
    if isinstance(e, psycopg.errors.RaiseException):
        # Una regla del trabajo que la base hace cumplir (un disparador), no una falla.
        return "no_se_puede", {"motivo": "regla_del_trabajo"}
    return None


def _no_hecho(r: dict[str, Any], tarea: dict[str, Any]) -> dict[str, Any]:
    """Un rechazo de negocio que la operación devuelve como dict, en hechos."""
    if r.get("falta"):
        return {"resultado": "no_se_puede", "motivo": "falta", "falta": r["falta"],
                "tarea": _tarea(tarea)}
    motivo = ("tarea_cerrada" if "cerrada" in str(r.get("error", ""))
              else "tarea_desconocida")
    return {"resultado": "no_se_puede", "motivo": motivo, "tarea": _tarea(tarea)}


def _vacio(valor: Any) -> bool:
    return valor is None or (isinstance(valor, str) and not valor.strip())


def _hecho(ficha: Ficha, resultado: str, **mas: Any) -> dict[str, Any]:
    return {"jugada": ficha.nombre, "resultado": resultado,
            **{k: v for k, v in mas.items() if v is not None}}


def _tarea(tarea: dict[str, Any]) -> dict[str, str]:
    return {"alias": tarea["alias"], "titulo": tarea["titulo"]}


# --- Lo que comparten las fichas -----------------------------------------------------------

def _auditar(ctx: Contexto, accion: str, sujeto_tipo: str, sujeto_id: Any,
             detalle: dict[str, Any]) -> None:
    """Un hecho del trabajo que la ficha escribe directo, atribuido a quien lo dijo, con la
    versión de las reglas y en el punto de guardado de la jugada (`auditoria`): el momento del
    motor y el mensaje que lo dijo van con él."""
    auditar(ctx.cur, accion=accion, workspace_id=ctx.quien.workspace_id,
            sujeto_tipo=sujeto_tipo, sujeto_id=sujeto_id, quien=ctx.quien,
            detalle={**detalle, "at": ctx.ahora.isoformat(),
                     "inbound_message_id": ctx.entrante_id})


def _cerrar_esperas(ctx: Contexto, task_id: str) -> None:
    """Un hecho informado sobre una tarea contesta la espera de esa tarea (9b)."""
    ctx.cur.execute(
        """update pending_reply set satisfecho_en = %s
            where membership_id = %s and task_id = %s and satisfecho_en is null""",
        (ctx.ahora, ctx.quien.membership_id, task_id))


def _abrir_pregunta(ctx: Contexto, hecho: dict[str, Any], tipo: str, task_id: str, *,
                    jugada: dict[str, Any]) -> None:
    """Una pregunta de Leda, ordenada con las demás (`preguntas.abrir`: nunca dos juntas, 9d);
    si su tipo espera respuesta, con su espera. El hecho la nombra con su clave
    (`_clave_de_pregunta`) y su id (`_nombrar_pregunta`)."""
    ahora, pregunta_id = preguntas.abrir_con_id(ctx, tipo, task_id, jugada=jugada)
    _nombrar_pregunta(hecho, _clave_de_pregunta(ahora), tipo, pregunta_id)


def referente(cur, responsable_membership_id: str) -> dict[str, str] | None:
    """Quien aprueba el trabajo de una persona, según la política del espacio
    (`membership.aprobador_membership_id`). El de una tarea es `quien_revisa`: una tarea que
    cambió de manos la sigue revisando quien la revisaba (C-7)."""
    cur.execute("""select i.membership_id, i.nombre
                     from membership m
                     join integrante i on i.membership_id = m.aprobador_membership_id
                    where m.id = %s""", (responsable_membership_id,))
    fila = cur.fetchone()
    return {"membership_id": str(fila["membership_id"]), "nombre": fila["nombre"]} \
        if fila else None


# La tarea la revisa quien la hace: la de alguien de su sector que tomó el encargado (decisión 28
# del usuario). Su significado, en `hechos.py`.
LA_REVISA_QUIEN_LA_HACE = "la_revisa_quien_la_hace"


def quien_revisa(cur, task_id: str) -> dict[str, str] | None:
    """Quien revisa el trabajo de una tarea (`autoridad.quien_revisa_la_tarea`, la regla de la
    base): quien aprueba el trabajo de su responsable o, si la tarea cambió de manos, el de quien
    era la tarea (C-7, decisión 28). Es a quien le llega el aviso de una nueva previsión y el de
    una entrega, salvo que sea quien la hace."""
    cur.execute("""select membership_id, nombre from integrante
                    where membership_id = quien_revisa_la_tarea(%s)""", (str(task_id),))
    fila = cur.fetchone()
    return {"membership_id": str(fila["membership_id"]), "nombre": fila["nombre"]} \
        if fila else None


def _exigir_responsable(cur, quien: Solicitante, task_id: str) -> dict[str, Any]:
    """La tarea, leída bajo la RLS del espacio, si la persona es su responsable (constitución
    §3: la persona responsable informa los hechos de su tarea)."""
    cur.execute("""select id, titulo, estado, fecha_objetivo, responsable_membership_id
                     from task where id = %s""", (task_id,))
    fila = cur.fetchone()
    if fila is None or str(fila["responsable_membership_id"]) != quien.membership_id:
        raise Denegado("La tarea no es de quien la nombra.")
    return fila


# --- Las fichas ----------------------------------------------------------------------------

def _anotar_inicio(ctx: Contexto, datos: dict, tarea: dict) -> dict:
    r = ejecutar(ctx.cur, ctx.quien, "actualizar_estado",
                 {"tarea_id": tarea["id"], "estado": "en_curso"}, ya_confirmada=True)
    if r.get("estado") != "en_curso":
        return _no_hecho(r, tarea)
    _cerrar_esperas(ctx, tarea["id"])
    return {"resultado": "anotado", "tarea": _tarea(tarea), "estado": "en_curso"}


def _anotar_prevision(ctx: Contexto, datos: dict, tarea: dict) -> dict:
    cur, cal = ctx.cur, ctx.calendario
    try:
        prevista = date.fromisoformat(str(datos["fecha"]).strip())
    except ValueError:
        return {"resultado": "falta_dato", "falta": ["fecha"], "tarea": _tarea(tarea)}
    fila = _exigir_responsable(cur, ctx.quien, tarea["id"])
    if fila["fecha_objetivo"] is None:
        return {"resultado": "no_se_puede", "motivo": "sin_fecha_comprometida",
                "tarea": _tarea(tarea)}
    comprometida = fila["fecha_objetivo"]
    vence = comprometida.astimezone(cal.zona).date()
    atraso = cal.habiles_entre(comprometida, datetime.combine(prevista, time(12), cal.zona))
    dicho = None if _vacio(datos.get("motivo")) else str(datos["motivo"]).strip()

    # La previsión vigente es la última de la cadena: la que ninguna otra reemplaza.
    cur.execute("""select f.id, f.fecha_prevista, f.motivo, f.at, f.reemplaza_id
                     from task_forecast f
                    where f.task_id = %s
                      and not exists (select 1 from task_forecast g where g.reemplaza_id = f.id)
                    order by f.at desc limit 1""", (tarea["id"],))
    anterior = cur.fetchone()
    # Una fecha que atrasa lleva su explicación (9n). Si la persona corre otra vez una fecha que
    # ya atrasaba la tarea, cuyo porqué dio hace menos de una hora y sin hablar de otra cosa en
    # el medio (`_el_porque_sigue_valiendo`), ese porqué sigue siendo el del atraso de esta
    # tarea: no se le vuelve a preguntar (constitución §8: ninguna pregunta que no aporte). Si
    # no, puede no referirse a él: se pregunta. El porqué es de la tarea: nunca pasa de una
    # tarea a otra (`_deshacer_prevision`).
    atrasa = prevista > vence
    de_antes = bool(dicho is None and atrasa and anterior is not None and anterior["motivo"]
                    and anterior["fecha_prevista"] > vence
                    and _el_porque_sigue_valiendo(ctx, tarea, anterior))
    motivo = anterior["motivo"] if de_antes else dicho
    cur.execute(
        """insert into task_forecast (task_id, fecha_prevista, motivo, fecha_comprometida,
                                      atraso_dias_habiles, reemplaza_id,
                                      dicho_por_membership_id, at)
           values (%s, %s, %s, %s, %s, %s, %s, %s) returning id""",
        (tarea["id"], prevista, motivo, comprometida, atraso,
         anterior["id"] if anterior else None, ctx.quien.membership_id, ctx.ahora))
    prevision_id = str(cur.fetchone()["id"])
    _auditar(ctx, "anotar_prevision", "task", tarea["id"], {
        "prevision_id": prevision_id, "fecha_prevista": prevista,
        "fecha_comprometida": comprometida.astimezone(cal.zona).date(),
        "atraso_dias_habiles": atraso, "motivo": motivo,
        **({"motivo_dicho_antes": True} if de_antes else {}),
        "reemplaza_id": anterior["id"] if anterior else None})
    _cerrar_esperas(ctx, tarea["id"])

    # Un aviso de previsión que todavía no salió queda atrás: lo reemplaza el de ésta, o
    # ninguno si volvió a la fecha comprometida (9b). Nunca en silencio: con su motivo, que es
    # otro si ésta trae el porqué de la misma fecha que esperaba el aviso (9n).
    llego_el_motivo = (dicho is not None and anterior is not None and not anterior["motivo"]
                       and anterior["fecha_prevista"] == prevista)
    cur.execute(
        """update scheduled_notice
              set estado = 'omitido', motivo_omision = %s, resuelto_en = %s
            where task_id = %s and tipo = 'nueva_prevision' and estado = 'guardado'""",
        (LLEGO_EL_MOTIVO if llego_el_motivo else "hay_una_prevision_mas_nueva", ctx.ahora,
         tarea["id"]))

    cur.execute("""select t.titulo from dependency d join task t on t.id = d.destino_task_id
                    where d.origen_task_id = %s and t.estado not in ('terminada', 'cancelada')
                    order by t.titulo""", (tarea["id"],))
    dependientes = [r["titulo"] for r in cur.fetchall()]
    hecho = {"resultado": "anotado", "tarea": _tarea(tarea), "prevision": prevista.isoformat(),
             "motivo": motivo,
             "fecha_comprometida": comprometida.astimezone(cal.zona).date().isoformat(),
             ATRASO_SI_SE_CUMPLE: atraso, "dependientes": dependientes,
             "aviso_al_referente": None}
    # Quien espera esta tarea, más abajo en una cadena de bloqueos, se entera del día nuevo
    # (C-5, porción 4: "Juan da fecha").
    from . import encadenados               # encadenados importa este módulo
    _juntar(hecho, encadenados.dio_otro_dia(ctx, tarea["id"], prevision_id, prevista.isoformat()))

    # Sin el porqué de un atraso, Leda pregunta qué la atrasa (con su espera, como toda pregunta
    # que espera respuesta). Con el porqué, o con una fecha que ya no atrasa, la pregunta que
    # quedaba de antes se cierra.
    sin_motivo = atrasa and motivo is None
    if not sin_motivo:
        preguntas.cerrar_de_tipo(ctx, preguntas.MOTIVO_DEL_ATRASO, tarea["id"],
                                 "respondida" if motivo is not None else "sin_efecto",
                                 {"jugada": "anotar_prevision", "tarea": tarea["id"]})
    else:
        _abrir_pregunta(ctx, hecho, preguntas.MOTIVO_DEL_ATRASO, tarea["id"],
                        jugada={"nombre": "anotar_prevision",
                                "datos": {"fecha": prevista.isoformat()}})

    quien_aprueba = quien_revisa(cur, tarea["id"])
    if prevista == comprometida.astimezone(cal.zona).date():
        return {**hecho, "sin_aviso": "misma_fecha_comprometida"}
    if quien_aprueba is None:
        return {**hecho, "sin_aviso": "sin_referente"}
    if quien_aprueba["membership_id"] == ctx.quien.membership_id:
        # La revisa quien la hace (la tarea de su gente que tomó el encargado; decisión 28): es
        # trabajo del sector, y nadie más se entera.
        return {**hecho, "sin_aviso": LA_REVISA_QUIEN_LA_HACE}
    # Le llega a otra persona por lo que dijo ésta: espera el margen para corregir, y el hecho
    # dice esa hora, la real (`margen.py`; usuario, 2026-10-07). Sin el porqué de un atraso,
    # espera además la respuesta hasta el final del día de trabajo y, si sale sin ella, lo dice
    # (9n): nunca un porqué que nadie dio.
    sale = (sale_esperando_el_motivo if sin_motivo else sale_con_margen)(
        cur, cal, ctx.quien.workspace_id, ctx.ahora)
    hechos_del_aviso = {k: hecho[k] for k in ("prevision", "motivo", "fecha_comprometida",
                                              ATRASO_SI_SE_CUMPLE, "dependientes")}
    if sin_motivo:
        hechos_del_aviso[SIN_MOTIVO_TODAVIA] = True
    cur.execute(
        """insert into scheduled_notice (workspace_id, tipo, task_id,
                                         destinatario_membership_id, hechos, programado_para,
                                         dedupe_key, creado_en)
           values (%s, 'nueva_prevision', %s, %s, %s, %s, %s, %s) returning id""",
        (ctx.quien.workspace_id, tarea["id"], quien_aprueba["membership_id"],
         json.dumps({**_es_un_aviso_al_referente("nueva_prevision"), "tarea": tarea["titulo"],
                     "responsable": ctx.quien.nombre, **hechos_del_aviso}, ensure_ascii=False),
         sale, f"motor:nueva_prevision:{prevision_id}", ctx.ahora))
    aviso_id = str(cur.fetchone()["id"])
    ctx.avisos_guardados.append(aviso_id)
    hecho["aviso_al_referente"] = {"a": quien_aprueba["nombre"], LLEGA: sale.isoformat(),
                                   **({ESPERA_EL_MOTIVO: True} if sin_motivo else {})}
    nombrar_efecto(hecho, "aviso_al_referente", AVISO, aviso_id)
    return hecho


def _anotar_bloqueo(ctx: Contexto, datos: dict, tarea: dict) -> dict:
    jugada = {"nombre": "anotar_bloqueo", "datos": datos}
    if _vacio(datos.get("causa")):
        # Sin causa no hay bloqueo (mecánica §3): se pregunta y no se anota nada (9c, 1).
        sin_causa = {"resultado": "falta_dato", "falta": ["causa"], "tarea": _tarea(tarea)}
        _abrir_pregunta(ctx, sin_causa, preguntas.CAUSA_DEL_BLOQUEO, tarea["id"], jugada=jugada)
        return sin_causa
    causa = str(datos["causa"]).strip()
    r = ejecutar(ctx.cur, ctx.quien, "registrar_bloqueo",
                 {"tarea_id": tarea["id"], "causa": causa}, ya_confirmada=True)
    if "bloqueo_id" not in r:
        return _no_hecho(r, tarea)
    # Desde cuándo está trabada, con el momento del motor, como todo lo que anota: la operación
    # lo fecha con la hora real de la base, y el bloqueo viejo cuenta sus días hábiles desde ahí
    # (C-5, porción 5; `bloqueo_viejo.py`). Con el reloj de verdad, son el mismo momento.
    ctx.cur.execute("update blocker set abierto_en = %s where id = %s",
                    (ctx.ahora, r["bloqueo_id"]))
    _cerrar_esperas(ctx, tarea["id"])
    # La causa contesta su pregunta antes de que se abra la siguiente.
    preguntas.contestar(ctx, "anotar_bloqueo", (preguntas.CAUSA_DEL_BLOQUEO,), tarea["id"])
    # Todo bloqueo con causa: quién lo puede destrabar, una pregunta que espera respuesta (su
    # ficha de pregunta lo dice: abre su espera y la escalera la repite). Lo decide la respuesta
    # de la persona, no un juicio de la IA sobre la causa (9c, corregida el 2026-10-05).
    anotado = {"resultado": "anotado", "tarea": _tarea(tarea), "causa": causa}
    # Si la tarea es lo que destraba la de otra persona, los dos bloqueos quedan enlazados: la
    # pregunta de para cuándo la destraba ya tiene respuesta, y quien espera se entera (C-5,
    # porción 4; `encadenados.py`). Antes de preguntar quién lo destraba: es la que sigue.
    from . import encadenados               # encadenados importa este módulo
    _juntar(anotado, encadenados.se_trabo(ctx, tarea["id"], r["bloqueo_id"], causa))
    _abrir_pregunta(ctx, anotado, preguntas.QUIEN_DESTRABA, tarea["id"],
                    jugada={**jugada, "bloqueo_id": r["bloqueo_id"]})
    return anotado


def _anotar_quien_destraba(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    cur = ctx.cur
    no_sabe = datos.get("no_sabe") is True
    nadie_mas = datos.get("nadie_mas") is True      # le toca a la persona misma
    quien_texto = None if _vacio(datos.get("quien")) else str(datos["quien"]).strip()
    if no_sabe + nadie_mas + (quien_texto is not None) != 1:
        # Una sola respuesta, de las tres que puede ser (revisión de la E2-3b).
        return {"resultado": "falta_dato", "falta": ["quien_destraba"],
                "puede_ser": ["alguien", "no_sabe", "nadie_mas"]}

    # El bloqueo: el de la tarea nombrada o, si no la nombra, el de la pregunta abierta.
    if tarea is not None:
        task_id = tarea["id"]
    else:
        cur.execute("""select task_id from conversation_question
                        where membership_id = %s and tipo = 'quien_destraba'
                          and cerrada_en is null
                        order by para_despues_en nulls first, abierta_en limit 1""",
                    (ctx.quien.membership_id,))
        pregunta = cur.fetchone()
        task_id = str(pregunta["task_id"]) if pregunta else None
    bloqueo = None
    if task_id is not None:
        fila = _exigir_responsable(cur, ctx.quien, task_id)
        cur.execute("""select id, causa from blocker where task_id = %s and resuelto_en is null
                        order by abierto_en desc limit 1""", (task_id,))
        bloqueo = cur.fetchone()
    if bloqueo is None:
        return {"resultado": "no_se_puede", "motivo": "sin_bloqueo_abierto",
                **({"tarea": _tarea(tarea)} if tarea else {})}
    alias = next((t for t in ctx.tareas if t["id"] == task_id), None)

    integrante = None
    if quien_texto is not None:
        coinciden = integrantes_que_coinciden(cur, quien_texto)
        if len(coinciden) > 1:
            return {"resultado": "falta_dato", "falta": ["integrante"],
                    "coinciden": [c["nombre"] for c in coinciden]}
        integrante = coinciden[0] if coinciden else None
        # Nombrarse a sí misma es decir que le toca a la persona que escribe.
        nadie_mas = (integrante is not None
                     and str(integrante["membership_id"]) == ctx.quien.membership_id)
    if nadie_mas:
        integrante = {"membership_id": ctx.quien.membership_id, "nombre": ctx.quien.nombre}
    cur.execute(
        """insert into blocker_unblocker (workspace_id, blocker_id, destraba_membership_id,
                                          destraba_externo, no_sabe,
                                          dicho_por_membership_id, at)
           values (%s, %s, %s, %s, %s, %s, %s) returning id""",
        (ctx.quien.workspace_id, bloqueo["id"],
         integrante["membership_id"] if integrante else None,
         quien_texto if quien_texto is not None and integrante is None else None,
         no_sabe, ctx.quien.membership_id, ctx.ahora))
    anotado = str(cur.fetchone()["id"])
    _auditar(ctx, "anotar_quien_destraba", "blocker", bloqueo["id"], {
        "blocker_unblocker_id": anotado, "task_id": task_id,
        "destraba_membership_id": integrante["membership_id"] if integrante else None,
        "destraba_externo": quien_texto if quien_texto is not None and integrante is None
        else None,
        "no_sabe": no_sabe})
    preguntas.cerrar_de_tipo(ctx, "quien_destraba", task_id, "respondida",
                             {"blocker_unblocker_id": anotado})
    _cerrar_esperas(ctx, task_id)
    hecho = {"resultado": "anotado", **({"tarea": _tarea(alias)} if alias else {}),
             "quien_destraba": ({"no_sabe": True} if no_sabe
                                else {"nadie_mas": True} if nadie_mas
                                else {"integrante": integrante["nombre"]} if integrante
                                else {"externo": quien_texto})}
    # Con otro integrante que lo destraba, Leda le escribe (la persecución, ADR 0017, decisión
    # 3a; C-5, `persecucion.py`); sin otra persona, las salidas (9c, corregida el 2026-10-05).
    if integrante is not None and not nadie_mas:
        from . import persecucion           # persecucion importa este módulo
        _juntar(hecho, persecucion.preguntarle(ctx, fila, bloqueo, anotado, integrante))
    sin_otra_persona = no_sabe or nadie_mas
    return {**hecho, "salidas": list(SALIDAS_DE_UN_BLOQUEO)} if sin_otra_persona else hecho


def _destrabar(ctx: Contexto, datos: dict, tarea: dict) -> dict:
    """La persona dice que la causa del bloqueo ya no está (decisión del usuario, 2026-10-05; ADR
    0018, 9l). Se cierra directo, como se anotó (9a), con la operación del dominio
    (`resolver_bloqueo`): la tarea vuelve al estado que tenía antes de bloquearse (mecánica §3).
    Lo que esperaba algo del bloqueo se cierra con él: la pregunta de quién lo destraba (la
    contesta, por su ficha), lo propuesto para salir de él y sus esperas. Con más de un bloqueo
    abierto no se elige cuál: se dice, con sus causas.

    La tarea vuelve al seguimiento (la escalera sólo sigue las que no tienen un bloqueo
    abierto). Antes de su fecha, la escalera sigue sola. Si su seguimiento ya había empezado (hoy
    es su fecha, o la pasó), la respuesta no es algo cierto sobre cuándo la termina: la espera
    del estado queda abierta y Leda vuelve a pedirlo el día hábil siguiente con la cuenta de
    nuevo, como después de un avance (9h); vencida, además, la pregunta de para cuándo (9j,
    `_si_esta_vencida`)."""
    cur = ctx.cur
    cur.execute("""select id, causa from blocker where task_id = %s and resuelto_en is null
                    order by abierto_en, causa""", (tarea["id"],))
    abiertos = cur.fetchall()
    if not abiertos:
        return {"resultado": "no_se_puede", "motivo": "sin_bloqueo_abierto",
                "tarea": _tarea(tarea)}
    if len(abiertos) > 1:
        return {"resultado": "no_se_puede", "motivo": "varios_bloqueos_abiertos",
                "tarea": _tarea(tarea), "causas": [b["causa"] for b in abiertos]}
    [bloqueo] = abiertos
    dijo = (ctx.texto or ctx.toque or "").strip() or "la causa del bloqueo ya no está"
    r = ejecutar(cur, ctx.quien, "resolver_bloqueo",
                 {"bloqueo_id": str(bloqueo["id"]), "resolucion": dijo}, ya_confirmada=True)
    if not r.get("resuelto"):
        return _no_hecho(r, tarea)
    _cerrar_esperas(ctx, tarea["id"])
    preguntas.cerrar_las_de_una_jugada(ctx, "anotar_quien_destraba", tarea["id"], "sin_efecto",
                                       {"jugada": "destrabar", "tarea": tarea["id"]})
    from . import persecucion               # persecucion importa este módulo
    persecucion.al_destrabarse(ctx, tarea["id"])
    cur.execute("select estado::text estado from task where id = %s", (tarea["id"],))
    hecho: dict[str, Any] = {"resultado": "anotado", "tarea": _tarea(tarea),
                             "bloqueo_resuelto": {"causa": bloqueo["causa"]},
                             "estado": cur.fetchone()["estado"]}
    # Quien espera esta tarea, más abajo en una cadena de bloqueos, se entera (C-5, porción 4).
    from . import encadenados               # encadenados importa este módulo
    _juntar(hecho, encadenados.se_destrabo(ctx, tarea["id"], str(bloqueo["id"])))
    fila = _exigir_responsable(cur, ctx.quien, tarea["id"])
    if fila["fecha_objetivo"] is not None:
        cal = ctx.calendario
        de = anclaje(cur, tarea["id"], fila["fecha_objetivo"].astimezone(cal.zona).date())
        if ctx.ahora.astimezone(cal.zona).date() >= de.fecha:
            candado(cur, tarea["id"])
            _juntar(hecho, _seguir_pidiendo(ctx, tarea, _espera_del_estado(ctx, tarea),
                                            {"jugada": "destrabar", "dijo": dijo}))
    return hecho


def palabras(texto: str) -> list[str]:
    """Las palabras de un nombre, sin mayúsculas ni acentos."""
    sin_acentos = unicodedata.normalize("NFKD", texto.casefold())
    sin_acentos = "".join(c for c in sin_acentos if not unicodedata.combining(c))
    return "".join(c if c.isalnum() else " " for c in sin_acentos).split()


def integrantes_que_coinciden(cur, dicho: str) -> list[dict[str, Any]]:
    """Los integrantes del espacio cuyo nombre tiene, como palabras enteras, todas las
    palabras de lo dicho: "ismael" es Ismael Soschinski; "Mar" no es Marcos. Se compara
    acá y no con un patrón de la base, así nada de lo dicho actúa como comodín."""
    buscadas = palabras(dicho)
    if not buscadas:
        return []
    cur.execute("select membership_id, nombre from integrante where activo order by nombre")
    return [f for f in cur.fetchall() if set(buscadas) <= set(palabras(f["nombre"]))]


def _informar_avance(ctx: Contexto, datos: dict, tarea: dict) -> dict:
    """La respuesta a un pedido de estado que cuenta un avance sin un hecho cierto (no dice que
    la terminó, ni para cuándo, ni que está trabada). Se anota con las palabras de la persona,
    atribuido y auditado, sin cambiar estado ni fecha; la espera sigue abierta, porque la
    respuesta no es cierta, y Leda vuelve a pedir el estado el día hábil siguiente, dentro de la
    escalera de su ancla (la previsión, si es posterior al vencimiento; 9i). No es silencio: la
    escalera cuenta sólo los pedidos sin respuesta (`escalera.py`). A la segunda respuesta así
    para la misma espera, Leda pregunta directo para cuándo (decisión del usuario, 2026-10-05);
    con la tarea vencida, ya a la primera (9j, `_si_esta_vencida`).

    Si no hay un pedido siguiente, los hechos lo dicen (nunca en silencio): la tarea no tiene
    vencimiento, o la escalera de su ancla ya terminó al escalar (y a quién se le avisó)."""
    cur, persona = ctx.cur, ctx.quien.membership_id
    dijo = str(datos["palabras"]).strip() if not _vacio(datos.get("palabras")) \
        else ctx.texto.strip()
    if not dijo:
        return {"resultado": "falta_dato", "falta": ["palabras"], "tarea": _tarea(tarea)}
    # La escalera no toca la tarea mientras se reemplazan sus pasos (`ancla.candado`).
    candado(cur, tarea["id"])
    cur.execute("""select * from pending_reply
                    where membership_id = %s and task_id = %s and tipo = %s
                      and satisfecho_en is null
                    order by preguntado_en desc limit 1""",
                (persona, tarea["id"], preguntas.ESTADO_DE_LA_TAREA))
    espera = cur.fetchone()
    if espera is None:
        if preguntas.en_la_lista(cur, persona, tarea["id"]):
            return _avance_de_la_lista(ctx, tarea, dijo)
        return {"resultado": "no_se_puede", "motivo": "nadie_pidio_el_estado",
                "tarea": _tarea(tarea)}

    _auditar(ctx, "informar_avance", "task", tarea["id"],
             {"dijo": dijo, "dicho_por_membership_id": persona})
    hecho: dict[str, Any] = {"resultado": "anotado", "tarea": _tarea(tarea),
                             "avance": {"dijo": dijo}, "el_pedido_de_estado": "sigue_abierto"}
    nombrar_efecto(hecho, "el_pedido_de_estado", ESPERA, espera["id"])
    _juntar(hecho, _seguir_pidiendo(ctx, tarea, espera, {"dijo": dijo}))
    if hecho.get("veces_sin_algo_cierto", 0) > 1:
        _abrir_pregunta(ctx, hecho, preguntas.FECHA_DE_LA_TAREA, tarea["id"],
                        jugada={"nombre": "informar_avance", "datos": datos})
    return hecho


def _avance_de_la_lista(ctx: Contexto, tarea: dict, dijo: str) -> dict:
    """Cómo viene una tarea de la lista de la cadencia que su escalera todavía no siguió (no
    vence todavía): Leda pidió el estado en la lista, así que se anota igual, con las palabras de
    la persona, atribuido y auditado (C-6, decisión 8). No abre ninguna espera: Leda vuelve a
    preguntar en la próxima lista o el día en que la escalera pide el estado, lo que llegue
    antes (`cadencias.cuando_vuelve_a_preguntar`), no al día hábil siguiente."""
    from . import cadencias                 # cadencias importa este módulo por `avisos`

    _auditar(ctx, "informar_avance", "task", tarea["id"],
             {"dijo": dijo, "dicho_por_membership_id": ctx.quien.membership_id,
              "en_la_lista": True})
    fila = _exigir_responsable(ctx.cur, ctx.quien, tarea["id"])
    vuelve = cadencias.cuando_vuelve_a_preguntar(
        ctx.cur, ctx.calendario, ctx.quien.workspace_id,
        {"id": tarea["id"], "fecha_objetivo": fila["fecha_objetivo"]}, ctx.ahora)
    hecho: dict[str, Any] = {"resultado": "anotado", "tarea": _tarea(tarea),
                             "avance": {"dijo": dijo}}
    if vuelve is not None:
        hecho["vuelve_a_pedir_el_estado"] = {LLEGA: vuelve.isoformat()}
    else:
        hecho["no_vuelve_a_pedir_el_estado"] = {"motivo": "sin_fecha_comprometida"}
    return hecho


def _seguir_pidiendo(ctx: Contexto, tarea: dict[str, Any], espera: dict[str, Any],
                     contesto: dict[str, Any]) -> dict[str, Any]:
    """Una respuesta que no es algo cierto deja la espera abierta y Leda vuelve a pedir el
    estado el día hábil siguiente, dentro de la escalera de su ancla (la previsión, si es
    posterior al vencimiento; 9i): ese pedido es el primero de una cuenta nueva y reemplaza los
    pasos guardados que no salieron (9h). Los hechos que agrega: cuándo vuelve a pedirlo y
    cuántas respuestas así lleva la espera, o por qué no vuelve a pedirlo (nunca en silencio:
    sin vencimiento, o con la escalera de su ancla ya escalada). `contesto`: lo que contestó,
    que el pedido siguiente recuerda (`avance_anterior`). Quien llama tiene la tarea tomada
    (`ancla.candado`)."""
    cur, cal, persona = ctx.cur, ctx.calendario, ctx.quien.membership_id
    fila = _exigir_responsable(cur, ctx.quien, tarea["id"])
    if fila["fecha_objetivo"] is None:      # sin vencimiento no hay escalera que vuelva a pedir
        return {"no_vuelve_a_pedir_el_estado": {"motivo": "sin_fecha_comprometida"}}
    vence = fila["fecha_objetivo"].astimezone(cal.zona).date()
    de = anclaje(cur, tarea["id"], vence)      # la escalera de la previsión, si es posterior
    escalon = pasos(cur, tarea["id"], de)
    if escalo(escalon, espera):
        return {"no_vuelve_a_pedir_el_estado": {
            "motivo": "ya_se_escalo", "escalado_a": _escalado_a(cur, escalon)}}

    # Los pasos de la escalera de esta ancla que todavía no salieron ya no corresponden: la
    # persona contestó. Los reemplaza el pedido del día hábil siguiente.
    cur.execute("""update scheduled_notice
                      set estado = 'omitido', motivo_omision = %s, resuelto_en = %s,
                          proximo_intento_en = null
                    where id = any(%s) and estado = 'guardado'""",
                (REEMPLAZADO_POR_UN_AVANCE, ctx.ahora,
                 [p["id"] for p in escalon if p["tipo"] in _PASOS_QUE_REEMPLAZA]))
    # La cuenta es de la espera, que la clave del pedido nombra: la misma espera y la misma
    # cuenta dan la misma clave, así que nada se guarda dos veces.
    de_la_espera = f"e{espera['id']}"
    veces = 1 + sum(p["tipo"] == REPREGUNTA_DE_ESTADO
                    and p["dedupe_key"].split(":")[5:6] == [de_la_espera] for p in escalon)
    hoy = ctx.ahora.astimezone(cal.zona).date()
    sale = sale_el(cal, cal.proximo_habil(hoy + timedelta(days=1)))
    # Lo manda Leda por su cuenta, como los demás pasos de la escalera: sin turno que lo cause.
    clave = f"motor:{REPREGUNTA_DE_ESTADO}:{tarea['id']}:{de.clave}:0:{de_la_espera}:a{veces}"
    cur.execute(
        """insert into scheduled_notice (workspace_id, tipo, task_id,
                                         destinatario_membership_id, hechos, programado_para,
                                         dedupe_key, creado_en)
           values (%s, %s, %s, %s, %s, %s, %s, %s)
           on conflict (workspace_id, dedupe_key) do nothing""",
        (ctx.quien.workspace_id, REPREGUNTA_DE_ESTADO, tarea["id"], persona,
         json.dumps({"aviso": REPREGUNTA_DE_ESTADO, "necesita_respuesta": True,
                     "avance_anterior": {**contesto, "el": hoy.isoformat()},
                     "tarea": tarea["titulo"], "vence": vence.isoformat(),
                     **({"seguimiento_por": "prevision"} if de.fecha > vence else {})},
                    ensure_ascii=False),
         sale, clave, ctx.ahora))
    cur.execute("select id from scheduled_notice where workspace_id = %s and dedupe_key = %s",
                (ctx.quien.workspace_id, clave))
    pidiendo = {"vuelve_a_pedir_el_estado": {LLEGA: sale.isoformat()},
                "veces_sin_algo_cierto": veces}
    nombrar_efecto(pidiendo, "vuelve_a_pedir_el_estado", AVISO, cur.fetchone()["id"])
    return pidiendo


def _escalado_a(cur, escalon: list[dict[str, Any]]) -> list[dict[str, str]]:
    """A quiénes se les avisó por el escalamiento de la escalera, y si les llegó."""
    ids = [str(p["id"]) for p in escalon
           if p["tipo"] == "escalamiento" and p["estado"] in ("enviado", "fallido")]
    if not ids:
        return []
    cur.execute("""select i.nombre, a.estado from scheduled_notice a
                     join integrante i on i.membership_id = a.destinatario_membership_id
                    where a.id = any(%s::uuid[]) order by i.nombre""", (ids,))
    return [{"a": f["nombre"], LLEGA: YA_LE_LLEGO if f["estado"] == "enviado" else NO_LE_LLEGO}
            for f in cur.fetchall()]


def _consultar_pendientes(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    filas = ejecutar(ctx.cur, ctx.quien, "consultar_tareas", {})
    alias = {t["id"]: t["alias"] for t in ctx.tareas}
    zona = ctx.calendario.zona
    tareas = [
        {"alias": alias.get(str(f["id"])), "titulo": f["titulo"], "estado": str(f["estado"]),
         "vence": f["fecha_objetivo"].astimezone(zona).date().isoformat()
         if f["fecha_objetivo"] else None,
         **({"cambios_pedidos": f["cambios_pedidos"]} if f.get("cambios_pedidos") else {})}
        for f in filas if str(f["estado"]) not in ("terminada", "cancelada")]
    return {"resultado": "leido", "tareas": tareas}


# La entrega (ADR 0019, decisiones 4 y 5; porción 2 de la C-3): sus jugadas están en
# `entrega.py`, que importa este módulo.

def _entregar(ctx: Contexto, datos: dict, tarea: dict) -> dict:
    from . import entrega
    return entrega.entregar(ctx, datos, tarea)


def _confirmar(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    """Lo último que Leda mostró para confirmar: la vista previa de un pase (C-7) o una
    entrega."""
    from . import entrega, pase
    q = pase.la_que_se_confirma(ctx, datos, tarea)
    if q is not None:
        return pase.confirmar(ctx, datos, q)
    return entrega.confirmar(ctx, datos, tarea)


def _guardar_para_la_entrega(ctx: Contexto, datos: dict, tarea: dict) -> dict:
    from . import entrega
    return entrega.guardar_para_la_entrega(ctx, datos, tarea)


def _corregir_la_entrega(ctx: Contexto, datos: dict, tarea: dict) -> dict:
    from . import entrega
    return entrega.corregir(ctx, datos, tarea)


# La aprobación (circuito 8; porción 3b de la C-3): sus jugadas están en `aprobacion.py`, que
# importa este módulo.

def _aprobar(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    from . import aprobacion
    return aprobacion.aprobar(ctx, datos, tarea)


def _pedir_cambios(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    from . import aprobacion
    return aprobacion.pedir_cambios(ctx, datos, tarea)


def _ver_entrega(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    from . import aprobacion
    return aprobacion.ver_entrega(ctx, datos, tarea)


# El enlace a la página de una tarea, pedido por chat (ADR 0019, decisión 7a): la jugada está en
# `enlace.py`, que importa este módulo.

def _pedir_enlace(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    from . import enlace
    return enlace.pedir_enlace(ctx, datos, tarea)


# La persecución del bloqueo (C-5, porción 1): las jugadas están en `persecucion.py`, que
# importa este módulo.

def _decir_cuando_destraba(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    from . import persecucion
    return persecucion.decir_cuando_destraba(ctx, datos, tarea)


def _decir_que_no_le_toca(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    from . import persecucion
    return persecucion.decir_que_no_le_toca(ctx, datos, tarea)


def _no_escribirle(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    from . import persecucion
    return persecucion.no_escribirle(ctx, datos, tarea)


# Delegar por chat (C-7; ADR 0017, enmienda a la decisión 2): las jugadas están en `pase.py`, que
# importa este módulo. Hasta la C-7, pasar una tarea no se hacía por chat y Leda decía quién lo
# decidía (9g; decisión del usuario del 2026-10-08: "queda así hasta que exista delegar").

def _pedir_reasignacion(ctx: Contexto, datos: dict, tarea: dict) -> dict:
    from . import pase
    return pase.pedir(ctx, datos, tarea)


def _contestar_el_pase(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    from . import pase
    return pase.contestar(ctx, datos, tarea)


# --- Cómo se deshace lo anotado (9f) -------------------------------------------------------
#
# Una corrección agrega hechos, nunca borra (constitución §12): la tarea vuelve a como estaba
# por la misma operación del dominio con que cambia siempre, y la historia guarda los dos.

MOTIVO_DE_LA_CORRECCION = "corrección: se había anotado en la tarea equivocada"


def _deshacer_inicio(ctx: Contexto, tarea: dict) -> dict | None:
    """Un inicio sólo se anota desde `asignada` (su ficha), así que vuelve a `asignada`."""
    fila = _exigir_responsable(ctx.cur, ctx.quien, tarea["id"])
    if str(fila["estado"]) != "en_curso":
        return None
    r = ejecutar(ctx.cur, ctx.quien, "actualizar_estado",
                 {"tarea_id": tarea["id"], "estado": "asignada",
                  "motivo": MOTIVO_DE_LA_CORRECCION}, ya_confirmada=True)
    if r.get("estado") != "asignada":
        return None
    return {"hechos": {"vuelve_a": {"estado": "asignada"}}, "datos": {}}


def _deshacer_prevision(ctx: Contexto, tarea: dict) -> dict | None:
    """Una previsión de corrección que reemplaza a la equivocada con la de antes (o con la
    fecha comprometida, si no había). Su aviso al referente: si no salió, se retira; si salió,
    se guarda una corrección breve para él (9f). Si no salió y la de antes tenía un aviso que
    se había retirado por ella, ése se vuelve a guardar (`_rearmar_aviso_de_la_anterior`). A la
    tarea correcta pasa sólo la fecha: su porqué era de ésta (9n)."""
    cur, cal = ctx.cur, ctx.calendario
    cur.execute("""select * from task_forecast f
                    where f.task_id = %s
                      and not exists (select 1 from task_forecast g where g.reemplaza_id = f.id)
                    order by f.at desc limit 1""", (tarea["id"],))
    equivocada = cur.fetchone()
    if (equivocada is None or equivocada["es_correccion"]
            or str(equivocada["dicho_por_membership_id"]) != ctx.quien.membership_id):
        return None
    anterior = None
    if equivocada["reemplaza_id"] is not None:
        cur.execute("select * from task_forecast where id = %s", (equivocada["reemplaza_id"],))
        anterior = cur.fetchone()
    comprometida = equivocada["fecha_comprometida"].astimezone(cal.zona).date()
    vuelve = anterior["fecha_prevista"] if anterior else comprometida
    cur.execute(
        """insert into task_forecast (task_id, fecha_prevista, motivo, fecha_comprometida,
                                      atraso_dias_habiles, reemplaza_id, es_correccion,
                                      dicho_por_membership_id, at)
           values (%s, %s, %s, %s, %s, %s, true, %s, %s) returning id""",
        (tarea["id"], vuelve, anterior["motivo"] if anterior else None,
         equivocada["fecha_comprometida"],
         anterior["atraso_dias_habiles"] if anterior else 0, equivocada["id"],
         ctx.quien.membership_id, ctx.ahora))
    correccion_id = str(cur.fetchone()["id"])
    _auditar(ctx, "corregir_prevision", "task", tarea["id"], {
        "prevision_id": correccion_id, "corrige_prevision_id": equivocada["id"],
        "fecha_prevista": vuelve})
    hechos: dict[str, Any] = {
        "vuelve_a": ({"prevision": vuelve.isoformat()} if anterior
                     else {"fecha_comprometida": comprometida.isoformat()}),
        "prevision_corregida": equivocada["fecha_prevista"].isoformat()}

    cur.execute("""select id, estado from scheduled_notice
                    where workspace_id = %s and dedupe_key = %s""",
                (ctx.quien.workspace_id, f"motor:nueva_prevision:{equivocada['id']}"))
    aviso = cur.fetchone()
    quien_aprueba = quien_revisa(cur, tarea["id"])
    if aviso is not None and aviso["estado"] == "guardado":
        cur.execute("""update scheduled_notice
                          set estado = 'omitido', motivo_omision = 'prevision_corregida',
                              resuelto_en = %s
                        where id = %s""", (ctx.ahora, aviso["id"]))
        hechos["aviso_de_la_prevision_corregida"] = {
            **({"a": quien_aprueba["nombre"]} if quien_aprueba is not None else {}),
            LLEGA: NO_LE_VA_A_LLEGAR}
    elif aviso is not None and aviso["estado"] == "enviado" and quien_aprueba is not None:
        sale = sale_con_margen(cur, cal, ctx.quien.workspace_id, ctx.ahora)
        cur.execute(
            """insert into scheduled_notice (workspace_id, tipo, task_id,
                                             destinatario_membership_id, hechos,
                                             programado_para, dedupe_key, creado_en)
               values (%s, 'correccion_de_prevision', %s, %s, %s, %s, %s, %s) returning id""",
            (ctx.quien.workspace_id, tarea["id"], quien_aprueba["membership_id"],
             json.dumps({**_es_un_aviso_al_referente("correccion_de_prevision"),
                         "tarea": tarea["titulo"], "responsable": ctx.quien.nombre,
                         "prevision_que_no_vale": equivocada["fecha_prevista"].isoformat(),
                         "motivo": "se_anoto_en_la_tarea_equivocada",
                         **hechos["vuelve_a"]}, ensure_ascii=False),
             sale, f"motor:correccion_de_prevision:{correccion_id}", ctx.ahora))
        correccion_aviso = str(cur.fetchone()["id"])
        ctx.avisos_guardados.append(correccion_aviso)
        hechos["correccion_al_referente"] = {"a": quien_aprueba["nombre"],
                                             LLEGA: sale.isoformat()}
        nombrar_efecto(hechos, "correccion_al_referente", AVISO, correccion_aviso)
    if (anterior is not None and quien_aprueba is not None
            and (aviso is None or aviso["estado"] != "enviado")):
        rearmado = _rearmar_aviso_de_la_anterior(ctx, tarea, anterior, correccion_id,
                                                 quien_aprueba)
        if rearmado is not None:
            rearmado_id, hechos["aviso_de_la_prevision_anterior"] = rearmado
            nombrar_efecto(hechos, "aviso_de_la_prevision_anterior", AVISO, rearmado_id)
    # A la tarea correcta pasa sólo la fecha (usuario, 2026-10-07; ADR 0018, 9n): el porqué se
    # dijo de esta tarea y no viaja. Si la fecha atrasa la otra, su ficha pregunta el suyo.
    return {"hechos": hechos, "datos": {"fecha": equivocada["fecha_prevista"].isoformat()}}


def _rearmar_aviso_de_la_anterior(ctx: Contexto, tarea: dict, anterior: dict,
                                  correccion_id: str,
                                  quien_aprueba: dict) -> tuple[str, dict] | None:
    """La corrección vuelve a una previsión anterior cuyo aviso al referente se había retirado
    sin salir (la reemplazó la equivocada): el referente nunca supo de ella, así que su aviso
    se vuelve a guardar, con los hechos de esa previsión, atado a la corrección, que es la
    previsión vigente. Si el aviso de la anterior ya había salido, el referente ya la sabe
    (pendiente de la E2-4)."""
    cur, cal = ctx.cur, ctx.calendario
    cur.execute("""select estado from scheduled_notice
                    where workspace_id = %s and dedupe_key = %s""",
                (ctx.quien.workspace_id, f"motor:nueva_prevision:{anterior['id']}"))
    suyo = cur.fetchone()
    comprometida = anterior["fecha_comprometida"].astimezone(cal.zona).date()
    if suyo is None or suyo["estado"] != "omitido" or anterior["fecha_prevista"] == comprometida:
        return None
    cur.execute("""select t.titulo from dependency d join task t on t.id = d.destino_task_id
                    where d.origen_task_id = %s and t.estado not in ('terminada', 'cancelada')
                    order by t.titulo""", (tarea["id"],))
    sale = sale_con_margen(cur, cal, ctx.quien.workspace_id, ctx.ahora)
    cur.execute(
        """insert into scheduled_notice (workspace_id, tipo, task_id,
                                         destinatario_membership_id, hechos, programado_para,
                                         dedupe_key, creado_en)
           values (%s, 'nueva_prevision', %s, %s, %s, %s, %s, %s) returning id""",
        (ctx.quien.workspace_id, tarea["id"], quien_aprueba["membership_id"],
         json.dumps({**_es_un_aviso_al_referente("nueva_prevision"), "tarea": tarea["titulo"],
                     "responsable": ctx.quien.nombre,
                     "prevision": anterior["fecha_prevista"].isoformat(),
                     "motivo": anterior["motivo"],
                     "fecha_comprometida": comprometida.isoformat(),
                     ATRASO_SI_SE_CUMPLE: anterior["atraso_dias_habiles"],
                     "dependientes": [r["titulo"] for r in cur.fetchall()]},
                    ensure_ascii=False),
         sale, f"motor:nueva_prevision:{correccion_id}", ctx.ahora))
    aviso_id = str(cur.fetchone()["id"])
    ctx.avisos_guardados.append(aviso_id)
    return aviso_id, {"a": quien_aprueba["nombre"], LLEGA: sale.isoformat()}


def _deshacer_bloqueo(ctx: Contexto, tarea: dict) -> dict | None:
    """El bloqueo se resuelve como corrección (`resolver_bloqueo`): la tarea vuelve al estado
    que tenía antes de bloquearse."""
    cur = ctx.cur
    cur.execute("""select id, causa from blocker
                    where task_id = %s and resuelto_en is null and abierto_por = %s
                    order by abierto_en desc limit 1""", (tarea["id"], ctx.quien.membership_id))
    bloqueo = cur.fetchone()
    if bloqueo is None:
        return None
    r = ejecutar(cur, ctx.quien, "resolver_bloqueo",
                 {"bloqueo_id": str(bloqueo["id"]), "resolucion": MOTIVO_DE_LA_CORRECCION},
                 ya_confirmada=True)
    if not r.get("resuelto"):
        return None
    from . import persecucion               # persecucion importa este módulo
    persecucion.al_destrabarse(ctx, tarea["id"])
    cur.execute("select estado::text estado from task where id = %s", (tarea["id"],))
    return {"hechos": {"vuelve_a": {"estado": cur.fetchone()["estado"]}},
            "datos": {"causa": bloqueo["causa"]}}


FICHAS: Mapping[str, Ficha] = MappingProxyType({f.nombre: f for f in (
    Ficha("anotar_inicio", "anotar que arrancó una tarea",
          necesita=("tarea",), opcional=(),
          comprueba="que sea el responsable y que la tarea esté asignada",
          hace="la pasa a en curso (actualizar_estado)",
          despues="cierra la espera de esa tarea",
          manejar=_anotar_inicio, del_responsable=True,
          estados=frozenset({"asignada"}),
          contesta=(preguntas.ESTADO_DE_LA_TAREA, preguntas.FECHA_DE_LA_TAREA),
          deshacer=_deshacer_inicio,
          es="La persona dice que empezó a trabajar en una tarea. Es sólo el comienzo: no "
             "trae la fecha para la que la termina ni dice que no puede avanzar. Seguir con "
             "una tarea que estaba trabada no es empezarla: es salir del bloqueo."),
    Ficha("anotar_prevision", "anotar para cuándo va a terminar una tarea, y por qué",
          necesita=("tarea", "fecha"), opcional=("motivo",),
          comprueba="que sea el responsable, que la tarea esté abierta y tenga fecha "
                    "comprometida",
          hace="anota la previsión con el atraso en días hábiles del espacio; la fecha "
               "comprometida no cambia",
          despues="guarda el aviso al referente, salvo que vuelva a la fecha comprometida; "
                  "con una fecha que atrasa sin su porqué, pregunta qué la atrasa y el aviso "
                  "espera la respuesta hasta el final del día de trabajo (9n); cierra la espera "
                  "de esa tarea",
          manejar=_anotar_prevision, del_responsable=True,
          contesta=(preguntas.ESTADO_DE_LA_TAREA, preguntas.FECHA_DE_LA_TAREA),
          deshacer=_deshacer_prevision, algo_cierto=True,
          es="La persona da la fecha para la que espera terminar una tarea, con su porqué o "
             "sin él. Es un atraso (o un adelanto) previsto, no un bloqueo: quien da una fecha "
             "dice cuándo va a terminar, aunque el porqué sea algo que espera, y no dice que "
             "no puede avanzar. Una fecha nueva que reemplaza otra que dio antes es otra "
             "previsión, no una corrección. El porqué de una fecha que ya dio, cuando Leda se "
             "lo pregunta, también es esta jugada, con esa misma fecha."),
    Ficha("anotar_bloqueo", "anotar que una tarea está trabada y por qué",
          necesita=("tarea",), opcional=("causa",),
          comprueba="que sea el responsable y que la tarea esté abierta",
          hace="sin causa, nada; con causa, registra el bloqueo (registrar_bloqueo)",
          despues="sin causa, pregunta la causa; con causa, pregunta quién lo puede "
                  "destrabar. Ningún aviso al referente (9c)",
          manejar=_anotar_bloqueo, del_responsable=True,
          contesta=("causa_del_bloqueo", preguntas.ESTADO_DE_LA_TAREA,
                    preguntas.FECHA_DE_LA_TAREA),
          deshacer=_deshacer_bloqueo, algo_cierto=True,
          es="La persona dice que no puede avanzar con una tarea: está trabada o parada. Su "
             "causa es lo que le falta o lo que frena el trabajo, si la dice. Explicar por qué "
             "se corre una fecha no es un bloqueo: es el porqué de una previsión."),
    Ficha("anotar_quien_destraba", "anotar quién puede destrabar un bloqueo",
          necesita=(), opcional=("tarea", "quien", "no_sabe", "nadie_mas"),
          comprueba="que haya un bloqueo abierto en una tarea suya",
          hace="anota quién destraba: un integrante, alguien de afuera, que no se sabe o "
               "que le toca a la persona misma",
          despues="cierra la pregunta y la espera; si no se sabe o le toca a la persona "
                  "que escribe, propone salidas, que quedan como tema abierto",
          manejar=_anotar_quien_destraba,
          contesta=(preguntas.QUIEN_DESTRABA, preguntas.ESTADO_DE_LA_TAREA),
          propone=lambda hecho: hecho.get("salidas"),
          es="La persona dice quién puede destrabar un bloqueo (alguien del equipo o de "
             "afuera), que no sabe quién, o que nadie más: le toca a la persona que escribe. "
             "El bloqueo es uno abierto antes o el que anota una jugada anterior del mismo "
             "mensaje. Quién lo destraba es un hecho distinto de la causa, aunque los dos "
             "vengan en la misma frase: cada uno va en su jugada."),
    Ficha("destrabar", "anotar que una tarea trabada ya puede seguir",
          necesita=("tarea",), opcional=(),
          comprueba="que sea el responsable y que la tarea esté bloqueada, con un solo bloqueo "
                    "abierto",
          hace="cierra el bloqueo (resolver_bloqueo): la tarea vuelve al estado que tenía "
               "antes de bloquearse",
          despues="cierra la pregunta de quién lo destraba, lo propuesto para salir del bloqueo "
                  "y sus esperas; la escalera vuelve a seguir la tarea y, si su seguimiento ya "
                  "había empezado, Leda vuelve a pedir el estado el día hábil siguiente",
          manejar=_destrabar, del_responsable=True, estados=frozenset({"bloqueada"}),
          contesta=(preguntas.QUIEN_DESTRABA,), sigue_el_pedido=True,
          es="La persona dice que la causa de un bloqueo ya no está: llegó lo que le faltaba "
             "o se resolvió lo que frenaba el trabajo, y la tarea puede seguir. El bloqueo es "
             "uno abierto antes o el que anota una jugada anterior del mismo mensaje. Es salir "
             "de un bloqueo: no es empezar la tarea, ni dar la fecha para la que la termina, "
             "ni contar cómo viene; si además dice uno de esos hechos, ése es otra jugada."),
    Ficha("informar_avance", "anotar cómo viene una tarea cuando la persona cuenta un avance "
                             "sin un hecho cierto",
          necesita=("tarea",), opcional=("palabras",),
          comprueba="que sea el responsable, que la tarea esté abierta y que Leda le haya "
                    "pedido el estado (una espera abierta)",
          hace="anota el avance con las palabras de la persona, atribuido y auditado; no "
               "cambia el estado ni la fecha",
          despues="la espera sigue abierta y Leda vuelve a pedir el estado el día hábil "
                  "siguiente, sin contarlo como silencio; a la segunda respuesta sin nada "
                  "cierto, pregunta para cuándo. Sin un pedido siguiente (sin vencimiento, o "
                  "ya escaló), lo dice",
          manejar=_informar_avance, del_responsable=True,
          contesta=(preguntas.ESTADO_DE_LA_TAREA,), sigue_el_pedido=True,
          es="La persona cuenta cómo viene una tarea sin un hecho cierto: no dice que la "
             "terminó, ni para cuándo, ni que arrancó, ni que no puede avanzar. Si dice uno de "
             "esos hechos, es la jugada de ese hecho, no ésta."),
    Ficha("consultar_pendientes", "contar qué tareas tiene pendientes",
          necesita=(), opcional=(),
          comprueba="nada", hace="lee sus tareas abiertas (consultar_tareas)",
          despues="nada", manejar=_consultar_pendientes,
          es="La persona pregunta qué tareas tiene pendientes, o cómo están sus tareas. Leda "
             "las lee de la base."),
    Ficha("entregar", "recibir la entrega de una tarea con su evidencia",
          necesita=("tarea",),
          opcional=("el_texto_cubre", "lo_descrito_cubre", "ejemplo", "acepta_el_ejemplo"),
          comprueba="que sea el responsable y que la tarea esté en curso, sin arrancar o, "
                    "si se retiró algo, en revisión con la entrega incompleta; qué cubre cada "
                    "pieza de lo que pide la política (la base), qué puntos del criterio de "
                    "aceptación dice lo descrito y qué falta (el código)",
          hace="muestra la entrega, pieza por pieza (también lo que mandó antes, que entra "
               "sólo si queda), con qué cubre cada una, qué describe del criterio y qué "
               "falta; nada se escribe en la tarea todavía",
          despues="con la política y el criterio completos, espera la confirmación (botón o "
                  "escrito); si falta algo, lo dice, con un ejemplo para lo que falta del "
                  "criterio, y espera lo que falta: no se entrega aunque la persona insista",
          manejar=_entregar, del_responsable=True,
          estados=frozenset({"asignada", "en_curso", "en_revision"}),
          corregir=_corregir_la_entrega, toma_lo_que_llego=True,
          es="La persona dice que terminó una tarea, suma algo a la entrega de una tarea que "
             "ya está mostrando (lo que escribe, fotos, archivos o enlaces) o acepta, tal cual, "
             "el ejemplo que Leda le propuso para lo que falta (acepta_el_ejemplo). Terminarla "
             "no es decir que le falta poco: eso es un avance. Lo que escribe puede describir "
             "de qué trabajo se trata y cómo se probó: el_texto_cubre nombra lo que dice de lo que "
             "pide la tarea, y lo_descrito_cubre, los puntos de su criterio de aceptación que "
             "dice todo lo que describió en la entrega. Si le falta alguno, ejemplo es cómo "
             "podría describirlo la persona."),
    Ficha("confirmar", "confirmar lo último que Leda mostró para confirmar",
          necesita=(), opcional=("tarea",),
          comprueba="la guarda: que lo que confirma sea lo último que la persona vio, en un "
                    "mensaje anterior, y que no haya cambiado desde entonces (su huella)",
          hace="entrega la tarea: las piezas de evidencia y el paso a revisión en un solo acto "
               "(entregar_tarea), nunca a terminada; o pide el pase de una tarea a otra persona "
               "(pedir_pase_de_tarea), que todavía no la cambia de manos",
          despues="de una entrega, quien aprueba se entera; de un pase, Leda le pregunta a quien "
                  "lo decide o a quien la recibe; si la guarda falla, muestra lo nuevo y no hace "
                  "nada",
          manejar=_confirmar, se_ofrece=False,
          es="La persona confirma, sin dudas, lo último que Leda le mostró para confirmar (la "
             "entrega de una tarea o pasarle una tarea a otra persona), escribiendo en lugar de "
             "tocar el botón, o pide que la entrega que Leda le mostró vaya como está, también "
             "si Leda le dijo que le falta algo. Una respuesta con un pero, una pregunta o un "
             "cambio no es una confirmación."),
    Ficha("guardar_para_la_entrega", "dejar un archivo para cuando entregue una tarea",
          necesita=("tarea",), opcional=(),
          comprueba="que sea el responsable y que la tarea esté abierta, sin entregar",
          hace="deja dicho de qué tarea son los archivos del mensaje (o los de la pregunta que "
               "contesta), sin que sean evidencia",
          despues="los muestra en la vista previa cuando entregue esa tarea, aparte, y entran "
                  "sólo si los deja",
          manejar=_guardar_para_la_entrega, del_responsable=True,
          estados=frozenset({"asignada", "en_curso", "bloqueada"}), se_ofrece=False,
          toma_lo_que_llego=True,
          es="La persona dice de qué tarea es una foto, un video o un archivo que mandó, sin "
             "decir que la terminó."),
    Ficha("aprobar", "aprobar la entrega de una tarea que espera su decisión",
          necesita=(), opcional=("tarea", "comentario", "el_comentario_pide_algo", "de"),
          comprueba="que quien escribe sea quien aprueba el trabajo del responsable, que la "
                    "tarea esté entregada y que lo entregado cubra lo que pide (la cocina); con "
                    "el botón del aviso, que la entrega no haya cambiado desde que se mostró",
          hace="anota la aprobación (aprobar_tarea) y, si el sistema comprueba que se cumple "
               "todo lo demás, la tarea queda terminada en el mismo acto; si algo más frena el "
               "cierre, la aprobación queda anotada. Con un comentario que le pide algo a "
               "alguien (o sin saber si lo pide), antes pregunta una sola vez cuál de las dos "
               "(aprobarla con el comentario o pedir el cambio), salvo que sea la respuesta a "
               "esa pregunta: nada cambia hasta que elija",
          despues="le avisa al responsable enseguida; si no se cerró, el sistema la cierra solo "
                  "cuando se resuelve lo que faltaba y les avisa a los dos",
          manejar=_aprobar, boton="Aprobar", opuesta="pedir_cambios",
          decide_la_tarea=True,
          contesta=(preguntas.DECISION_DE_LA_ENTREGA, preguntas.QUE_CAMBIOS_PIDE,
                    preguntas.CUAL_DE_LAS_DOS),
          es="La persona que escribe aprueba el trabajo entregado de una tarea que espera su "
             "decisión, sin pedir que se cambie nada; puede sumar un comentario, lo que le pasa "
             "a la persona responsable para que lo tenga en cuenta, y si ese comentario le "
             "pide algo a alguien (el_comentario_pide_algo). Si además pide "
             "que se cambie o se revise algo, eso es también pedir cambios: van las dos "
             "jugadas, salvo cuando contesta la pregunta de cuál de las dos: entonces lo que "
             "elige es una sola decisión (elegir, o esta jugada con lo demás como comentario). "
             "Una tarea que no está en la lista se nombra por su responsable (de)."),
    Ficha("pedir_cambios", "pedirle cambios a la entrega de una tarea que espera su decisión",
          necesita=(), opcional=("tarea", "comentario", "de"),
          comprueba="que quien escribe sea quien aprueba el trabajo del responsable y que la "
                    "tarea esté entregada (la cocina)",
          hace="sin decir qué falta, nada: lo pregunta; con lo que falta, anota el pedido de "
               "cambios (pedir_cambios_tarea) y la tarea vuelve al estado que tenía antes de "
               "entregarla",
          despues="le avisa al responsable enseguida, con lo que pidió",
          manejar=_pedir_cambios, boton="Pedir cambios", opuesta="aprobar",
          decide_la_tarea=True,
          contesta=(preguntas.DECISION_DE_LA_ENTREGA, preguntas.QUE_CAMBIOS_PIDE,
                    preguntas.CUAL_DE_LAS_DOS),
          es="La persona que escribe le pide al responsable que cambie, complete o revise algo "
             "de lo que entregó en una tarea que espera su decisión, con lo que falta "
             "(comentario) si lo dice. Lo que falta, cuando Leda lo pregunta, también es esta "
             "jugada. Una tarea que no está en la lista se nombra por su responsable (de)."),
    Ficha("ver_entrega", "mostrar la entrega de una tarea que espera su revisión",
          necesita=(), opcional=("tarea", "de"),
          comprueba="que quien escribe sea quien aprueba el trabajo del responsable y que la "
                    "tarea esté entregada, esperando su decisión",
          hace="lee lo entregado; no cambia nada",
          despues="la muestra con sus fotos adjuntas y el enlace a la página de la tarea, con "
                  "los botones Aprobar y Pedir cambios, sin que sea una pregunta",
          manejar=_ver_entrega,
          es="La persona que revisa pide ver lo que se entregó de una tarea que espera su "
             "decisión (lo que describió quien la hizo, sus fotos, archivos y enlaces), tocando "
             "su botón o escribiéndolo. No decide nada: aprobarla o pedirle cambios son otras "
             "jugadas. Una tarea que no está en la lista se nombra por su responsable (de)."),
    Ficha("pedir_enlace", "pasar el enlace a la página de una tarea",
          necesita=(), opcional=("tarea", "como_la_nombra"),
          comprueba="que la tarea sea del espacio y que la persona pueda verla (la base: quien "
                    "la tiene, quien aprueba su trabajo, quien decidió sobre ella, el referente "
                    "del área y la autoridad final)",
          hace="lee la tarea; no cambia nada",
          despues="la respuesta lleva al final el enlace personal a la página de la tarea, que "
                  "el código agrega; si no puede verla, ningún enlace sale",
          manejar=_pedir_enlace,
          es="La persona pide el enlace (o el link) a la página de una tarea, para verla: una "
             "suya, una que espera su revisión o cualquier otra que nombre. Si la tarea no está "
             "en la lista, como_la_nombra dice cómo la nombró. Pedir ver lo entregado de una "
             "tarea que espera su revisión es otra jugada."),
    Ficha("decir_cuando_destraba", "anotar para cuándo destraba la tarea trabada de otra "
                                   "persona",
          necesita=(), opcional=("tarea", "para_cuando", "ya_esta", "lo_que_dice",
                                 "ya_lo_hablaron", "su_tarea_trabada"),
          comprueba="que quien escribe sea quien destraba ahora un bloqueo abierto de esa tarea "
                    "(lo último que dijo la persona trabada)",
          hace="anota lo que dice, atribuido y auditado, como un hecho del bloqueo: para "
               "cuándo, que ya está o sus palabras; no cierra el bloqueo. Si sólo dice que ya "
               "lo habló con la persona trabada, no anota nada todavía: pregunta una vez qué "
               "arreglaron y para cuándo. Si dice que está trabado con una tarea suya, la anota "
               "con el bloqueo de esa tarea, que enlaza los dos",
          despues="cierra su pregunta y su espera; la persona trabada se entera terminado el "
                  "margen para corregir, como información",
          manejar=_decir_cuando_destraba, se_ofrece=False,
          contesta=(preguntas.CUANDO_SE_DESTRABA,),
          es="La persona que escribe puede destrabar una tarea trabada de otra persona (está "
             "en la lista como espera_que_la_destrabe) y dice para cuándo lo resuelve "
             "(para_cuando), que ya lo resolvió (ya_esta), qué pasa con eso (lo_que_dice) o "
             "que ya lo habló con la persona trabada (ya_lo_hablaron), o que no puede porque "
             "una tarea suya está trabada (su_tarea_trabada). Es lo que dice sobre lo que traba "
             "la tarea de otro: no es un hecho de una tarea suya."),
    Ficha("decir_que_no_le_toca", "decir que no le corresponde destrabar la tarea trabada de "
                                  "otra persona",
          necesita=(), opcional=("tarea", "quien", "no_sabe", "lo_que_dice"),
          comprueba="que quien escribe sea quien destraba ahora un bloqueo abierto de esa tarea",
          hace="anota que no le corresponde y, si lo dice, quién se encarga, atribuido y "
               "auditado; si es la primera persona de la cadena y no dice de quién es, no anota "
               "nada todavía: pregunta una vez quién se encarga",
          despues="cierra su pregunta y su espera; con un integrante nombrado por la primera, "
                  "Leda le escribe a esa persona; si no, le informa la cadena entera al "
                  "referente, sin pedirle nada; la persona trabada se entera, como información",
          manejar=_decir_que_no_le_toca, se_ofrece=False,
          contesta=(preguntas.CUANDO_SE_DESTRABA,),
          es="La persona que escribe es a quien se le preguntó por una tarea trabada de otra "
             "persona (está en la lista como espera_que_la_destrabe) y dice que no le "
             "corresponde destrabarla: quien es quién se encarga, como lo nombró, si lo dice; "
             "no_sabe, si dice que no sabe quién; lo_que_dice, sus palabras. No es una fecha "
             "para destrabarla ni que ya está."),
    Ficha("no_escribirle", "no escribirle a quien destraba una tarea trabada",
          necesita=(), opcional=("tarea", "quien"),
          comprueba="que sea el responsable de la tarea y que Leda le haya guardado un mensaje "
                    "a quien la destraba",
          hace="si el mensaje todavía no salió, no sale (queda retirado con su motivo); si ya "
               "salió, nada",
          despues="la respuesta dice que no le escribe o, si ya salió, que ya le llegó",
          manejar=_no_escribirle, del_responsable=True, se_ofrece=False,
          es="La persona trabada pide que Leda no le escriba a quien destraba su tarea (por "
             "ejemplo, porque ya habló con esa persona). quien es a quién, como lo nombró. No "
             "cambia quién destraba ni cierra el bloqueo."),
    Ficha("pedir_reasignacion", "pasarle una tarea suya a otra persona del equipo",
          necesita=(), opcional=("tarea", "a", "como_la_nombra"),
          comprueba="que sea el responsable o, si nombra una que no está en su lista, el "
                    "encargado del sector de quien la tiene (decisión 27), que la tarea esté "
                    "asignada, en curso o trabada, que quien la recibe sea del equipo y tenga un "
                    "chat con Leda, y que la persona pueda pedirlo: el encargado de un sector, a "
                    "cualquiera; un integrante, sólo a alguien de su sector (la cocina)",
          hace="nada todavía: muestra la vista previa del pase (de quién a quién, quién lo "
               "decide y que quien la recibe tiene que tomarla, o que con su confirmación pasa "
               "a ser suya)",
          despues="espera la confirmación (botón o escrito); al confirmar, Leda le pregunta a "
                  "quien lo decide o a quien la recibe o, si se la queda él, la tarea pasa a "
                  "ser suya. Si no se puede, dice por qué y, si es de otro sector, quién lo "
                  "decide",
          manejar=_pedir_reasignacion, del_responsable=True,
          estados=frozenset({"asignada", "en_curso", "bloqueada"}),
          es="La persona pide que una tarea suya pase a otra persona del equipo (a, como la "
             "nombró): que se la pasen, que la haga o la tome otra persona. El encargado de un "
             "sector también puede pedirlo para una tarea de alguien de su sector, que no está "
             "en su lista (como_la_nombra dice cómo la nombró), y quedársela él: entonces a es "
             "su propio nombre."),
    Ficha("contestar_el_pase", "decir si aprueba que una tarea pase a otra persona, o si toma "
                               "la que le quieren pasar",
          necesita=(), opcional=("tarea", "acepta", "por_que"),
          comprueba="que la tarea espere su decisión o que la tome (la cocina: quien decide es "
                    "el encargado del sector de quien la recibe)",
          hace="anota la decisión o la respuesta (decidir_pase_de_tarea o "
               "contestar_pase_de_tarea); si la toma, la tarea pasa a ser suya, con la misma "
               "fecha y el mismo criterio",
          despues="si aprueba, Leda le pregunta a quien la recibe si la toma; si no, o si no la "
                  "toma, la tarea sigue con quien la tenía; quien pidió se entera de cómo "
                  "terminó y, si la toma, también quien decidió",
          manejar=_contestar_el_pase, se_ofrece=False,
          contesta=(preguntas.DECIDIR_EL_PASE, preguntas.TOMAR_LA_TAREA),
          es="La persona dice si aprueba que una tarea de otra persona pase a alguien (la tarea "
             "está en la lista como espera_su_decision_del_pase) o si toma la tarea que le "
             "quieren pasar (espera_que_la_tome), tocando su botón o escribiéndolo: acepta es "
             "verdadero si dice que sí, falso si dice que no; por_que, sus palabras si dice "
             "por qué."),
    # Las situaciones generales (`situaciones.py`): valen igual para todas las fichas.
    Ficha("elegir", "elegir una de las opciones de la pregunta abierta",
          necesita=("opcion",), opcional=(),
          comprueba="que la opción sea de una pregunta suya; si la pregunta ya se cerró, no "
                    "hace nada y dice con qué se cerró",
          hace="cierra la pregunta con esa opción y hace la jugada que esperaba, con la "
               "opción como dato y las comprobaciones de su ficha",
          despues="vuelve la pregunta que quedó para después, si hay",
          manejar=situaciones.elegir, se_ofrece=False,
          es="La persona elige una de las opciones de la pregunta abierta de Leda (o una de "
             "las jugadas que Leda le propuso), tocando o escribiendo. Sin una pregunta abierta "
             "con opciones, no es esta jugada."),
    Ficha("corregir", "corregir algo ya anotado que era de otra tarea o que no pasó",
          necesita=("corrige", "tarea"),
          opcional=("tarea_correcta", "saca", "el_texto_cubre", "lo_descrito_cubre"),
          comprueba="que sea el responsable y que eso haya quedado anotado en esa tarea en "
                    "sus últimos turnos",
          hace="agrega un hecho de corrección: la tarea vuelve a como estaba y, si la dice, "
               "el hecho va a la tarea correcta; nada se borra (9f)",
          despues="un aviso que no salió se retira; uno que ya salió lleva una corrección "
                  "al referente",
          manejar=situaciones.corregir, del_responsable=True, se_ofrece=False,
          es="La persona dice que algo que ya quedó anotado estaba mal: era de otra tarea o no "
             "pasó. Dar un hecho nuevo que reemplaza al de antes no es corregir: es la jugada "
             "de ese hecho. En una entrega (corrige: entregar), sacar una pieza de lo mostrado o "
             "de lo ya entregado (saca, por su alias), o decir qué cubre lo que escribió "
             "(el_texto_cubre) o qué dice del criterio de aceptación (lo_descrito_cubre)."),
    Ficha("cancelar", "dejar sin efecto la pregunta abierta",
          necesita=(), opcional=(),
          comprueba="que haya una pregunta abierta y que se pueda dejar (la de quién destraba "
                    "espera respuesta, 9c)",
          hace="la cierra sin anotar nada",
          despues="no se vuelve a preguntar; vuelve la que quedó para después, si hay",
          manejar=situaciones.cancelar, se_ofrece=False,
          es="La persona deja sin efecto la pregunta abierta de Leda: no la va a contestar. "
             "Dejar sin efecto algo que la persona dijo antes no es cancelar: es corregirlo o "
             "dar el hecho nuevo."),
    Ficha("dejar_para_despues", "dejar la pregunta abierta para más tarde",
          necesita=(), opcional=(),
          comprueba="que haya una pregunta abierta",
          hace="la deja para después, sin cerrarla",
          despues="vuelve en un mensaje siguiente, cuando no haya otra abierta",
          manejar=situaciones.dejar_para_despues, se_ofrece=False,
          es="La persona deja la pregunta abierta de Leda para más tarde, sin contestarla ni "
             "dejarla sin efecto."),
)})


def _manejador(ficha: Ficha) -> Manejador:
    return lambda ctx, jugada: correr(ficha, ctx, jugada)


# --- Lo que admite dos lecturas ------------------------------------------------------------

def opuestas(jugadas: list[Jugada]) -> dict[int, int]:
    """Las jugadas del mensaje que dicen lo contrario de otra sobre la misma tarea (`Ficha.
    opuesta`): de cada par, la primera → la segunda. Una tarea sin nombrar no forma un par."""
    pares: dict[int, int] = {}
    usadas: set[int] = set()
    for i, a in enumerate(jugadas):
        ficha = FICHAS.get(a.nombre)
        alias = (a.datos or {}).get("tarea")
        if ficha is None or ficha.opuesta is None or _vacio(alias) or i in usadas:
            continue
        j = next((j for j, b in enumerate(jugadas) if j > i and j not in usadas
                  and b.nombre == ficha.opuesta and (b.datos or {}).get("tarea") == alias), None)
        if j is not None:
            pares[i] = j
            usadas.update((i, j))
    return pares


def dos_lecturas(ctx: Contexto, a: Jugada, b: Jugada) -> dict[str, Any]:
    """Dos jugadas opuestas sobre la misma tarea en un mensaje ("aprobado, pero que revise el
    cable"): ninguna se hace. Leda pregunta una sola vez cuál de las dos, con las dos como
    opciones (constitución §8: algo con más de una lectura); cada opción corre su jugada, con los
    datos que la persona dio (lo que dijo con una sirve para la otra). Si la tarea no existe, la
    primera jugada corre sola y dice por qué no se puede.

    La pregunta se hace una sola vez (decisión 12 del usuario, 2026-10-08): si ya se hizo en un
    mensaje anterior, volver a mezclar las dos tampoco elige, y no se repite: Leda no decide, y
    la entrega sigue esperando con sus opciones como botones (`situaciones.no_eligio`). La
    pregunta guarda la huella de lo entregado: lo que se elija decide sobre lo que valía al
    preguntar (ADR 0018, decisión 2)."""
    tarea = ctx.tarea(str(a.datos["tarea"]))
    if tarea is None:
        return correr(FICHAS[a.nombre], ctx, a)
    ctx.cur.execute("""select * from conversation_question
                        where membership_id = %s and tipo = %s and task_id = %s
                          and cerrada_en is null and not (id = any(%s::uuid[]))
                        order by abierta_en limit 1""",
                    (ctx.quien.membership_id, preguntas.CUAL_DE_LAS_DOS, tarea["id"],
                     list(ctx.preguntas_del_turno)))
    hecha = ctx.cur.fetchone()
    if hecha is not None:
        return {"jugada": a.nombre, **situaciones.no_eligio(ctx, hecha)}
    from . import entrega        # entrega importa fichas
    opciones = []
    for una, otra in ((a, b), (b, a)):
        datos = {k: v for k, v in {**(otra.datos or {}), **(una.datos or {})}.items()
                 if k != "tarea" and not _vacio(v)}
        opciones.append((FICHAS[una.nombre].boton or una.nombre,
                         {"tarea": tarea["id"], "jugada": una.nombre, "datos": datos}))
    hecho = {"jugada": a.nombre, "resultado": "dos_lecturas", "tarea": _tarea(tarea),
             "lecturas": [a.nombre, b.nombre]}
    ahora, pregunta_id = preguntas.abrir_con_id(
        ctx, preguntas.CUAL_DE_LAS_DOS, tarea["id"],
        jugada={"nombre": a.nombre,
                "huella": entrega.huella_de_lo_entregado(ctx.cur, tarea["id"])},
        opciones=opciones)
    _nombrar_pregunta(hecho, _clave_de_pregunta(ahora), preguntas.CUAL_DE_LAS_DOS, pregunta_id)
    return hecho


# La lista cerrada: nombre de la jugada → su manejador.
JUGADAS: Mapping[str, Manejador] = MappingProxyType(
    {nombre: _manejador(ficha) for nombre, ficha in FICHAS.items()})


def lo_que_puede_hacer(jugadas: Mapping[str, Manejador]) -> list[str]:
    """Lo que Leda puede hacer por chat, para el hecho de algo fuera de la lista."""
    return [FICHAS[n].para_que for n in sorted(jugadas) if n in FICHAS and FICHAS[n].se_ofrece]


# Para las situaciones generales (`situaciones.py`), la entrega (`entrega.py`) y la aprobación
# (`aprobacion.py`).
vacio = _vacio
tarea_hecho = _tarea
nombrar_pregunta = _nombrar_pregunta
no_hecho = _no_hecho
cerrar_esperas = _cerrar_esperas
juntar = _juntar
abrir_pregunta = _abrir_pregunta
