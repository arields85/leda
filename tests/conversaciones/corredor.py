"""El corredor de las conversaciones de prueba: una corrida de una conversación (E2-7).

`odd/tasks/prueba-chica-del-motor.md`, sección 6; ADR 0018, decisiones 5b, 6 y 7. Cada
conversación de `tests/conversaciones/` (la fuente, en Markdown) está copiada en un YAML al lado,
con lo que se comprueba solo. Una corrida, sobre una base ya creada para ella:

1. carga el estado inicial (`carga.py`) y corre el **preludio**, si lo hay: lo que pasó antes,
   por el motor mismo, con las jugadas del YAML y los textos de la IA de la corrida;
2. corre cada paso por el código de verdad, con el reloj en el momento que dice el `.md`:
   - **una persona escribe** (`escribe`): se guarda como lo guarda el escuchador, corre el turno
     (`turno.procesar_turno`) y el despacho entrega la respuesta;
   - **una persona manda** fotos o archivos (`manda`, con o sin `escribe`): se guardan como los
     guarda el adaptador (`archivo` y `archivo_de_mensaje`; lo que el canal no deja bajar, con
     su rechazo) y corre el turno como con un mensaje escrito;
   - **una persona toca** una opción (`toca`): `turno.procesar_toque` con el token de esa opción
     (de una tarea, por su clave; si no, por su etiqueta, y `vieja` toca la de la pregunta
     anterior que la ofreció, un botón viejo; con `de_la_tarea`, la de esa tarea: el botón del
     aviso de una de varias entregas);
   - **Leda por su cuenta o nadie escribe** (`relojes`): en cada momento, una vuelta del ciclo
     (`ciclo.Ciclo`): la escalera, los cierres que esperaban, los avisos guardados, el despacho
     y los avisos a la administración;
   - **lo que pasa aparte** (`aparte: true`): un paso que la conversación da por pasado en el
     medio sin mirarlo (la entrega y la aprobación de otra tarea), corrido por el motor como el
     preludio, con las jugadas del YAML, y sin comprobar;
3. compara lo que pasó con lo esperado (`comprobar.py`), mide el formato de cada mensaje de Leda
   (`comprobar.fallas_de_formato`) y guarda lo que la persona que lee la
   corrida necesita: lo que dijo cada uno, las jugadas, los hechos y la latencia.

El transporte es falso (`despachador.TransporteDePrueba`): nada sale a Telegram. La IA es la que
se le pasa: la guionada con las jugadas esperadas (`grabar.IAPerfecta`), una real o una
grabación (`grabar.IARepetida`). El motor de conversación es el de `motores.py`: el definitivo
(el de la prueba chica se borró el 2026-10-07); la corrida dice cuál corrió.
"""

from __future__ import annotations

import contextlib
import hashlib
import re
import time
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import yaml

from leda.autoridad import identificar_en_espacio
from leda.db import espacio
from leda.despachador import TransporteDePrueba
from leda.motor.archivos import MB
from leda.motor.ia import IA
from leda.salida import formatear

from . import comprobar as cp
from .carga import Mundo, cargar, contenido_de, momento
from .grabar import IAMixta, IAPerfecta
from .motores import POR_OMISION, Motor
from .motores import cargar as cargar_motor

CARPETA = Path(__file__).resolve().parent
RAIZ = Path(__file__).resolve().parents[2]
# Lo que deja bajar el canal, como el adaptador de Telegram (`recibir.LIMITE_DE_TELEGRAM`): un
# archivo más grande llega como rechazado, y la IA recibe este límite.
LIMITE_DEL_CANAL = 20 * MB

# La dirección pública de una corrida (`_con_la_direccion_de_prueba`): un dominio reservado, que
# no es de nadie. El enlace a la página de una tarea que el despachador agrega al final de un
# mensaje (ADR 0019, decisión 6) se reconoce por ella.
DIRECCION_DE_PRUEBA = "https://leda.invalid"
ENLACE_DE_PRUEBA = re.compile(r"\n" + re.escape(DIRECCION_DE_PRUEBA) + r"/tarea/[A-Za-z0-9_-]+$")


# La definición del usuario (2026-10-06; ADR 0018, decisión 9, tercera vuelta): todo mensaje de
# Leda termina con un próximo paso concreto. Vale para cada paso en que Leda escribe, así que la
# casilla para leerlo se agrega sola donde el paso no dice ya cuál es su próximo paso.
PROXIMO_PASO = ("el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y "
                "cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda "
                "nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace "
                "falta contestar")


class SinBoton(LookupError):
    """El paso toca una opción que ninguna pregunta de la persona ofreció."""


class RelojDeCorrida:
    """El reloj del motor en una corrida: el momento del paso, y un contador real para la
    latencia de la IA."""

    def __init__(self, inicio: datetime) -> None:
        self.momento = inicio

    def ahora(self) -> datetime:
        return self.momento

    def medir(self) -> float:
        return time.perf_counter()


# --- Las conversaciones --------------------------------------------------------------------

def leer(ruta: Path) -> dict[str, Any]:
    conv = yaml.safe_load(Path(ruta).read_text("utf-8"))
    conv["archivo"] = Path(ruta).name
    return conv


def todas(carpeta: Path = CARPETA) -> list[dict[str, Any]]:
    return [leer(p) for p in sorted(carpeta.glob("*.yaml"))]


def elegir(numeros: list[str] | None, carpeta: Path = CARPETA) -> list[dict[str, Any]]:
    convs = todas(carpeta)
    if not numeros:
        return convs
    pedidas = {n.zfill(2) for n in numeros}
    elegidas = [c for c in convs if str(c["numero"]).zfill(2) in pedidas]
    faltan = pedidas - {str(c["numero"]).zfill(2) for c in elegidas}
    if faltan:
        raise LookupError(f"No hay conversación {', '.join(sorted(faltan))}.")
    return elegidas


def llamadas_previstas(conv: dict[str, Any]) -> int:
    """Cuántas veces se le pide algo a la IA en una corrida, según lo esperado: dos por mensaje
    escrito, una por toque y una por cada mensaje que Leda manda por su cuenta (también en el
    preludio, donde las jugadas son guionadas y los textos los redacta la IA)."""
    n = 0
    for paso in (conv.get("preludio") or []) + (conv.get("pasos") or []):
        if "escribe" in paso or "manda" in paso:
            n += 2 if paso in (conv.get("pasos") or []) and not paso.get("aparte") else 1
        elif "toca" in paso:
            n += 1
        n += len(paso.get("salen") or [])
    return n


# --- Una corrida ---------------------------------------------------------------------------

@dataclass
class Salida:
    """Un mensaje entregado. Si lo mandó Leda por su cuenta, con sus avisos: un envío puede
    juntar varios (mecánica §10), y entonces trae los tipos, las tareas y los hechos de todos."""

    a: str | None
    texto: str
    botones: list[str]
    es_respuesta: bool
    tipo: str | None = None             # el tipo de aviso, si todos sus avisos son de uno
    tareas: list[str] = field(default_factory=list)
    hechos: Any = None                  # los de su aviso; una lista, si juntó varios
    el: str | None = None
    tipos: list[str] = field(default_factory=list)
    # Cada aviso del envío con su tipo, su tarea y sus hechos: lo esperado de un tipo y una
    # tarea se compara con ese aviso, no con cualquiera del envío.
    avisos: list[dict[str, Any]] = field(default_factory=list)
    # Lo que escribió la IA, tal como quedó en el outbox: sin el saludo del día que antepone el
    # sistema. Es lo que mide el formato (`comprobar.fallas_de_formato`).
    redactado: str | None = None
    # Las fotos que salieron adjuntas, en el álbum que sigue al texto (ADR 0019, decisión 6). Un
    # álbum que salió sin su texto antes es una falla de garantía (`album_suelto`).
    fotos: int = 0
    album_suelto: bool = False
    # El enlace a la página de la tarea, que el despachador agrega al final al mandar (ADR 0019,
    # decisión 6), y si salió sin vista previa. El texto de la salida nunca lo lleva.
    enlace: bool = False
    sin_vista_previa: bool = False


@dataclass
class ResultadoPaso:
    paso: Any
    quien: str
    cuando: str
    texto: str | None = None
    jugadas: list[dict[str, Any]] = field(default_factory=list)
    hechos: list[Any] = field(default_factory=list)
    pregunta: Any = None
    ya_no_sale: list[Any] = field(default_factory=list)   # lo anunciado que ya no va a pasar
    salidas: list[Salida] = field(default_factory=list)
    latencia_ms: int | None = None
    fallas: list[cp.Falla] = field(default_factory=list)
    dice: list[str] = field(default_factory=list)
    no_dice: list[str] = field(default_factory=list)
    preludio: bool = False


@dataclass
class Corrida:
    numero: str
    titulo: str
    fuente: str
    vez: int
    ia: str
    mide: str
    pasos: list[ResultadoPaso] = field(default_factory=list)
    error: str | None = None
    llamadas: list[dict[str, Any]] = field(default_factory=list)
    costo: dict[str, Any] | None = None
    # El motor de conversación que corrió (`motores.MOTORES`); `motor`, abajo, es otra cosa:
    # si el código hizo lo esperado con las jugadas esperadas.
    motor_usado: str = POR_OMISION

    def fallas(self, clase: str | None = None) -> list[tuple[Any, cp.Falla]]:
        return [(p.paso, f) for p in self.pasos for f in p.fallas
                if clase is None or f.clase == clase]

    @property
    def garantias(self) -> bool:
        return self.error is None and not self.fallas(cp.GARANTIA)

    @property
    def comprension(self) -> bool:
        return self.error is None and not self.fallas(cp.COMPRENSION)

    @property
    def motor(self) -> bool:
        return self.error is None and not self.fallas(cp.MOTOR)

    @property
    def formato(self) -> bool:
        return self.error is None and not self.fallas(cp.FORMATO)

    @property
    def bien(self) -> bool:
        return self.error is None and not self.fallas()

    def latencias(self) -> list[int]:
        return [p.latencia_ms for p in self.pasos if p.latencia_ms is not None and
                not p.preludio]


class _Corredor:
    def __init__(self, conn, conv: dict[str, Any], ia: IA, motor: Motor) -> None:
        self.conn, self.conv, self.ia, self.motor = conn, conv, ia, motor
        self.persona = conv.get("persona", "Marcos")
        self.mundo: Mundo = cargar(conn, conv)
        self.reloj = RelojDeCorrida(momento(conv["inicio"]))
        self.transporte = TransporteDePrueba()
        self.transporte_admin = TransporteDePrueba()
        callar = lambda _texto: None    # noqa: E731 -- el ciclo cuenta lo que hace en la consola
        # Las claves y los códigos sin significado de lo que la IA recibe (`hechos.py`): una
        # falla del motor en el paso en que aparecen (revisión del contrato, 2026-10-05).
        self.sin_significado: set[str] = set()
        ia = _QueMira(ia, [], self.sin_significado, motor.sin_significado)
        self.ciclo = motor.Ciclo(conn, self.mundo.workspace_id, ia, self.reloj, self.transporte,
                           transporte_admin=self.transporte_admin, cada_s=0.0,
                           monotono=lambda: 0.0, imprimir=callar)
        self.despacho = motor.Ciclo(conn, self.mundo.workspace_id, ia, self.reloj,
                                    self.transporte, transporte_admin=self.transporte_admin,
                                    seguimiento=False, imprimir=callar)
        self.foco = set(conv.get("foco") or self.mundo.tareas)
        self.enlazadas: set[str] = set()     # filas del outbox ya enlazadas a un entregado

    # -- el paso ---------------------------------------------------------------------------

    def correr(self, paso: dict[str, Any], *, preludio: bool = False) -> ResultadoPaso:
        antes = cp.foto(self.conn, self.mundo)
        entregados = len(self.transporte.enviados)
        r = ResultadoPaso(paso.get("paso", "·"), paso.get("quien", self.persona), "",
                          dice=list(paso.get("dice") or []),
                          no_dice=list(paso.get("no_dice") or []), preludio=preludio)
        resultado = None
        if "escribe" in paso or "toca" in paso or "manda" in paso:
            self.reloj.momento = momento(paso["a_las"])
            r.cuando = paso["a_las"]
            ia = self.ia
            if preludio:
                guion = IAPerfecta(self.mundo.titulos, jugada=self.motor.Jugada)
                guion.preparar(paso)
                ia = IAMixta(guion, self.ia)
            elif hasattr(self.ia, "preparar"):
                self.ia.preparar(paso)
            try:
                resultado, r.texto, r.jugadas, r.latencia_ms = self._turno(paso, ia)
            except SinBoton:
                if preludio:
                    raise
                # Sin la pregunta con botones (un paso anterior no la hizo), no hay qué tocar:
                # es una falla del paso, consecuencia de no haber entendido, y la corrida sigue
                # (ronda 1, conversación 09).
                r.texto = f"[toca] {paso['toca']}"
                r.fallas = [cp.Falla(cp.COMPRENSION, "no hay un botón para tocar",
                                     paso["toca"], None)]
                return r
            self.despacho.vuelta()
        else:
            for cuando in paso["relojes"]:
                self.reloj.momento = momento(cuando)
                self.ciclo.vuelta()
                r.salidas += self._salidas(entregados, cp.foto(self.conn, self.mundo))
                entregados = len(self.transporte.enviados)
            r.cuando = ", ".join(paso["relojes"])
        despues = cp.foto(self.conn, self.mundo)
        if resultado is not None:
            r.salidas = self._salidas(entregados, despues)
        if resultado is not None:
            r.hechos = cp.normalizar(resultado.hechos, self.mundo.titulos)
            r.pregunta = cp.normalizar(resultado.pregunta, self.mundo.titulos)
            r.ya_no_sale = list(resultado.ya_no_sale)
        if not preludio and (r.texto or r.salidas) and not any(
                "próximo paso" in d for d in r.dice):
            r.dice.append(PROXIMO_PASO)
        if not preludio:
            r.fallas = self._comprobar(paso, r, resultado, antes, despues).fallas
            if self.sin_significado:        # lo del preludio, en el primer paso
                r.fallas.append(cp.Falla(cp.MOTOR, "hechos sin significado", [],
                                         sorted(self.sin_significado)))
                self.sin_significado.clear()
        return r

    def _turno(self, paso, ia):
        quien_corto = paso.get("quien", self.persona)
        persona = self.mundo.personas[quien_corto]
        with espacio(self.conn, self.mundo.workspace_id) as cur:
            quien = identificar_en_espacio(cur, persona["telegram"], self.mundo.workspace_id)
        self.conn.commit()
        situaciones: list[dict[str, Any]] = []
        ia_que_mira = _QueMira(ia, situaciones, self.sin_significado,
                               self.motor.sin_significado)
        if "escribe" in paso or "manda" in paso:
            texto = paso.get("escribe", "")
            entrante = self._guardar_mensaje(quien, persona, texto, paso.get("manda") or [])
            resultado = self.motor.procesar_turno(self.conn, quien, entrante, ia_que_mira,
                                                  self.reloj, limite_del_canal=LIMITE_DEL_CANAL)
            texto = texto + "".join(f" [{m['que']}]" for m in paso.get("manda") or [])
            self.conn.commit()
            jugadas = [self._jugada(j.nombre, j.datos, situaciones[-1] if situaciones else {})
                       for j in resultado.jugadas]
            latencia = self._latencia(persona["membership_id"])
        else:
            token, etiqueta = self._token(persona["membership_id"], paso["toca"],
                                          vieja=bool(paso.get("vieja")),
                                          de_la_tarea=paso.get("de_la_tarea"))
            texto = f"[toca] {etiqueta}"
            resultado = self.motor.procesar_toque(self.conn, quien, token, persona["telegram"],
                                                  ia_que_mira, self.reloj)
            self.conn.commit()
            if resultado is None:
                raise LookupError(f"El toque de {paso['toca']} no es de una pregunta suya.")
            jugadas = [{"nombre": "elegir", "opcion": paso["toca"]}]
            latencia = self._latencia(persona["membership_id"])
            if paso.get("repetir_toque"):
                otra = self.motor.procesar_toque(self.conn, quien, token, persona["telegram"],
                                                 ia_que_mira, self.reloj)
                self.conn.commit()
                self._repetido = otra is not None and otra.repetido
        return resultado, texto, jugadas, latencia

    def _guardar_mensaje(self, quien, persona, texto: str,
                         manda: list[dict[str, Any]] | None = None) -> str:
        """El mensaje, como lo guarda el escuchador, y lo que trajo, como lo guarda el adaptador
        (`recibir.py`): cada archivo en `archivo`, atado al mensaje en `archivo_de_mensaje`; uno
        más grande que lo que deja bajar el canal (`mb`), sólo anotado con su rechazo. Varias
        fotos juntas son un álbum: un solo mensaje."""
        manda = list(manda or [])
        with espacio(self.conn, self.mundo.workspace_id) as cur:
            cur.execute(
                """insert into inbound_message (workspace_id, telegram_message_id, chat_id,
                                                app_user_id, texto, at)
                   values (%s, %s, %s, %s, %s, %s) returning id""",
                (self.mundo.workspace_id, uuid.uuid4().int % 2_000_000_000, persona["telegram"],
                 persona["app_user_id"], texto, self.reloj.ahora()))
            entrante = str(cur.fetchone()["id"])
            album = f"album-{entrante}" if len(manda) > 1 else None
            for i, m in enumerate(manda):
                archivo, rechazo = None, None
                if float(m.get("mb") or 0) * MB > LIMITE_DEL_CANAL:
                    rechazo = "demasiado_grande"
                else:
                    contenido, clase = contenido_de(m["que"], m.get("nombre"), f"{entrante}-{i}")
                    cur.execute(
                        """insert into archivo (workspace_id, contenido, sha256, tamano, tipo,
                                                clase, nombre_original,
                                                enviado_por_membership_id, recibido_en)
                           values (%s, %s, %s, %s, 'x', %s, %s, %s, %s) returning id""",
                        (self.mundo.workspace_id, contenido,
                         hashlib.sha256(contenido).hexdigest(), len(contenido), clase,
                         m.get("nombre"), persona["membership_id"], self.reloj.ahora()))
                    archivo = str(cur.fetchone()["id"])
                cur.execute(
                    """insert into archivo_de_mensaje (workspace_id, inbound_message_id,
                                                       archivo_id, que_llego, nombre_original,
                                                       rechazo, telegram_message_id,
                                                       telegram_file_id,
                                                       telegram_file_unique_id,
                                                       telegram_media_group_id)
                       values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (self.mundo.workspace_id, entrante, archivo, m["que"], m.get("nombre"),
                     rechazo, i + 1, f"archivo-{i}", f"unico-{entrante}-{i}", album))
        self.conn.commit()
        return entrante

    def _token(self, membership_id: str, clave: str, *, vieja: bool = False,
               de_la_tarea: str | None = None) -> tuple[str, str]:
        """El token de la opción de esa tarea en la última pregunta con opciones de la persona
        (abierta o ya cerrada: tocar un botón viejo es la situación general 7). Si `clave` no es
        una tarea, la opción con esa etiqueta (el "Confirmar" de una entrega), de la tarea
        `de_la_tarea` si se la nombra (el "Pedir cambios" del aviso de una de varias entregas);
        con `vieja`, la de la pregunta anterior que la ofreció."""
        with espacio(self.conn, self.mundo.workspace_id) as cur:
            if clave in self.mundo.tareas:
                cur.execute("""select o.token, o.etiqueta from conversation_option o
                                 join conversation_question q on q.id = o.question_id
                                where q.membership_id = %s and o.valor ->> 'tarea' = %s
                                  and not (o.valor ? 'jugada')
                                order by q.abierta_en desc limit 1 offset %s""",
                            (membership_id, self.mundo.tareas[clave], int(vieja)))
            else:
                tarea = self.mundo.tareas[de_la_tarea] if de_la_tarea else None
                cur.execute("""select o.token, o.etiqueta from conversation_option o
                                 join conversation_question q on q.id = o.question_id
                                where q.membership_id = %s and o.etiqueta = %s
                                  and (%s::text is null or o.valor ->> 'tarea' = %s::text)
                                order by q.abierta_en desc limit 1 offset %s""",
                            (membership_id, clave, tarea, tarea, int(vieja)))
            fila = cur.fetchone()
        self.conn.commit()
        if fila is None:
            raise SinBoton(f"No hay un botón de {clave} para tocar.")
        return fila["token"], fila["etiqueta"]

    def _latencia(self, membership_id: str) -> int | None:
        """La del turno que acaba de correr: el último de entrada de la persona."""
        with espacio(self.conn, self.mundo.workspace_id) as cur:
            cur.execute("""select latencia_ms from conversation_turn
                            where sentido = 'entrada' and membership_id = %s
                            order by numero desc limit 1""", (membership_id,))
            fila = cur.fetchone()
        self.conn.commit()
        return fila["latencia_ms"] if fila else None

    def _jugada(self, nombre: str, datos: dict[str, Any], situacion: dict[str, Any]) -> dict:
        """Una jugada con sus tareas y opciones por su clave (`comprobar.normalizar`)."""
        de_alias = {t["alias"]: self.mundo.clave_de_titulo(t["titulo"])
                    for t in situacion.get("tareas") or []}
        abierta = ((situacion.get("estado") or {}).get("pregunta_abierta") or {})
        # La opción de una tarea, por la clave de su tarea; la que corre su propia jugada (el
        # "Aprobar" de una pregunta de dos lecturas), por su alias, como la nombra el YAML.
        de_opcion = {o["opcion"]: de_alias.get(o.get("tarea"), o["opcion"])
                     for o in abierta.get("opciones") or []}
        salida = {"nombre": nombre}
        for k, v in (datos or {}).items():
            if k in ("tarea", "tarea_correcta"):
                v = de_alias.get(v, v)
            elif k == "opcion":
                v = de_opcion.get(v, v)
            salida[k] = v
        return salida

    def _salidas(self, desde: int, despues: dict[str, Any]) -> list[Salida]:
        """Lo entregado desde `desde`, cada uno con su fila del outbox (la primera que no se
        enlazó antes en la corrida) y, si lo mandó Leda por su cuenta, con su aviso."""
        salidas = []
        usados = self.enlazadas
        avisos_de: dict[str, list[dict[str, Any]]] = {}
        for aviso_id, a in despues["avisos"].items():
            if a["outbox_id"]:
                avisos_de.setdefault(a["outbox_id"], []).append({**a, "id": aviso_id})
        for e in self.transporte.enviados[desde:]:
            quien = self.mundo.persona_de_chat(e.chat_id)
            if e.fotos is not None:
                # Un álbum es parte del mensaje de Leda que salió antes a la misma persona: el
                # texto de su respuesta (`despachador`, `respuesta_grupo`). Sin ése, salió suelto.
                previo = next((s for s in reversed(salidas) if s.a == quien), None)
                if previo is not None and not previo.fotos:
                    previo.fotos = len(e.fotos)
                else:
                    salidas.append(Salida(quien, "", [], False, el=cp.dia(self.reloj.ahora()),
                                          fotos=len(e.fotos), album_suelto=True))
                continue
            # El enlace a la página de la tarea va al final de lo que se entregó, nunca en la
            # salida: se compara sin él.
            enlace = ENLACE_DE_PRUEBA.search(e.texto)
            entregado = e.texto[:enlace.start()] if enlace else e.texto
            # El outbox guarda el texto con las marcas de formato de la IA y el transporte
            # entrega el texto plano (`salida.formatear`): se comparan ya convertidos.
            fila_id = next((k for k, s in despues["salidas"].items()
                            if k not in usados and s["a"] == quien
                            and entregado.endswith(formatear(s["cuerpo"])[0])), None)
            if fila_id is not None:
                usados.add(fila_id)
            fila = despues["salidas"].get(fila_id, {})
            texto = entregado
            if fila:
                # La transcripción muestra lo que escribió la IA, con sus marcas, después
                # del saludo del día si lo hubo.
                plano = formatear(fila["cuerpo"])[0]
                texto = entregado[:len(entregado) - len(plano)] + fila["cuerpo"]
            avisos, hechos = _avisos_del_envio(avisos_de.get(fila_id, []), self.mundo.titulos)
            tipos = sorted({a["tipo"] for a in avisos})
            botones = [self.mundo.clave_de_titulo(b.etiqueta) or b.etiqueta for b in e.botones]
            salidas.append(Salida(
                quien, texto, botones, bool(fila.get("es_respuesta")),
                tipo=tipos[0] if len(tipos) == 1 else None,
                tareas=list(dict.fromkeys(a["tarea"] for a in avisos if a["tarea"])),
                hechos=(hechos[0] if len(hechos) == 1 else hechos) if hechos else None,
                el=cp.dia(self.reloj.ahora()), tipos=tipos,
                avisos=avisos, redactado=fila.get("cuerpo"), enlace=enlace is not None,
                sin_vista_previa=e.sin_vista_previa))
        return salidas

    # -- lo que se comprueba ------------------------------------------------------------------

    def _comprobar(self, paso, r: ResultadoPaso, resultado, antes, despues) -> cp.Comprobacion:
        c = cp.Comprobacion()
        hubo = cp.efectos(antes, despues)
        titulos = self.mundo.titulos
        quien = paso.get("quien", self.persona)
        if "escribe" in paso or "toca" in paso or "manda" in paso:
            jugadas_bien = cp.comprobar_jugadas(c, paso.get("jugadas") or [], r.jugadas,
                                                paso.get("escribe", ""), motor=self.motor) \
                if "toca" not in paso else True
            _, falta = cp.comprobar_efectos(c, paso.get("efectos") or {}, hubo, titulos)
            # Lo que depende de haber entendido: con las jugadas esperadas, una diferencia es
            # del código; si no, es la consecuencia de no haber entendido.
            clase = cp.MOTOR if jugadas_bien and not falta else cp.COMPRENSION
            respuestas = [s for s in r.salidas if s.es_respuesta and s.a == quien]
            if len(respuestas) != 1:
                c.falla(cp.GARANTIA, "una respuesta por mensaje", 1, len(respuestas))
            botones = respuestas[0].botones if respuestas else []
            if botones != list(paso.get("botones") or []):
                c.falla(clase, "botones", list(paso.get("botones") or []), botones)
            if "pregunta" in paso:
                e = paso["pregunta"]
                if (e is None) != (r.pregunta is None) or (
                        e is not None and not cp.coincide(e, r.pregunta)):
                    c.falla(clase, "la pregunta de la respuesta", e, r.pregunta)
            if "hechos" in paso and not cp.coincide(paso["hechos"], r.hechos):
                c.falla(clase, "hechos", paso["hechos"], r.hechos)
            if paso.get("repetir_toque") and not getattr(self, "_repetido", False):
                c.falla(cp.GARANTIA, "un toque repetido no repite el efecto", "repetido",
                        "atendido otra vez")
        else:
            clase = cp.MOTOR
            self._comprobar_salen(c, paso.get("salen") or [], r.salidas)
            cp.comprobar_incidentes(c, hubo["incidentes"])
        estado = dict(paso.get("estado_despues") or {})
        de = estado.pop("de", self.persona)
        cp.comprobar_estado(c, estado, despues, de, clase)
        cp.comprobar_avisos_en_estado(c, paso.get("estado_avisos") or [], despues, titulos)
        # El formato de cada mensaje de Leda del paso, respuesta o aviso, a quien sea (segunda
        # vuelta del formato, 2026-10-07): sobre lo que escribió la IA, sin el saludo del día.
        for s in r.salidas:
            if s.album_suelto:
                c.falla(cp.GARANTIA, "el álbum sale después de su texto", "texto y álbum",
                        _resumen(s))
                continue
            if s.enlace and not s.sin_vista_previa:
                c.falla(cp.GARANTIA, "el enlace a la página sale sin vista previa",
                        "sin vista previa", _resumen(s))
            if s.redactado is not None and "/tarea/" in s.redactado:
                c.falla(cp.GARANTIA, "el enlace a la página no queda en la salida",
                        "sin el enlace", _resumen(s))
            cp.comprobar_formato(c, s.redactado if s.redactado is not None else s.texto,
                                 titulos.values(), a=s.a)
        return c

    def _comprobar_salen(self, c: cp.Comprobacion, esperadas: list[dict],
                         salidas: list[Salida]) -> None:
        """Lo que Leda mandó por su cuenta sobre las tareas de la conversación (`foco`) contra lo
        esperado. Uno que falta o uno de más es del código."""
        # En el orden de la conversación, no en el de entrega: dos del mismo momento pueden
        # salir en cualquier orden.
        reales = sorted((s for s in salidas if not s.es_respuesta
                         and (not s.tareas or set(s.tareas) & self.foco)),
                        key=lambda s: (s.el or "", s.a or "", s.tareas, s.tipo or ""))
        sobran = list(reales)
        for e in esperadas:
            i = next((i for i, s in enumerate(sobran) if _sale_coincide(e, s, self.foco)),
                     None)
            if i is None:
                c.falla(cp.MOTOR, "no salió lo esperado", e,
                        [_resumen(s) for s in reales if s.a == e.get("a")])
            else:
                sobran.pop(i)
        for s in sobran:
            c.falla(cp.MOTOR, "salió algo de más", None, _resumen(s))


def _avisos_del_envio(avisos: list[dict[str, Any]], titulos: dict[str, str]
                      ) -> tuple[list[dict[str, Any]], list[Any]]:
    """Los avisos de un envío, en el orden de las tareas (uno solo, o los que juntó), cada uno
    con su tipo, su tarea y sus propios hechos, tomados del aviso mismo y nunca por posición; y
    los hechos de los que tienen, en ese orden."""
    de_cada_uno = [{"id": a.get("id"), "tipo": a["tipo"], "tarea": a["tarea"],
                    "hechos": (cp.normalizar(a["hechos"], titulos)
                               if a.get("hechos") is not None else None)}
                   for a in sorted(avisos, key=lambda a: (a["tarea"] or "", a["tipo"],
                                                          str(a.get("id") or "")))]
    return de_cada_uno, [a["hechos"] for a in de_cada_uno if a["hechos"] is not None]


class _QueMira:
    """Deja ver la situación que recibió la IA para elegir (los alias de ese turno) y junta en
    `sin_significado` las claves y los códigos de cada pedido que no tienen significado, según
    el vocabulario del motor (`buscar`, su `hechos.sin_significado`)."""

    def __init__(self, ia: IA, situaciones: list[dict[str, Any]], sin_significado: set[str],
                 buscar: Callable[[Any], set[str]]) -> None:
        self.ia, self.situaciones, self.faltan = ia, situaciones, sin_significado
        self.buscar = buscar

    @property
    def nombre(self) -> str:
        return self.ia.nombre

    def preparar(self, paso: dict[str, Any]) -> None:
        if hasattr(self.ia, "preparar"):
            self.ia.preparar(paso)

    def elegir_jugadas(self, situacion):
        self.situaciones.append(situacion)
        self.faltan |= self.buscar(situacion)
        if _elige_el_guion(self.ia):
            return self.ia.elegir_jugadas(_para_el_guion(situacion))
        return self.ia.elegir_jugadas(situacion)


    def redactar(self, pedido):
        self.faltan |= self.buscar(pedido)
        return self.ia.redactar(pedido)


def _elige_el_guion(ia) -> bool:
    """Si las jugadas las elige la IA guionada, aunque vaya envuelta (la que graba, la mixta)."""
    while not isinstance(ia, IAPerfecta):
        if isinstance(ia, IAMixta):
            ia = ia.jugadas_de
        elif hasattr(ia, "ia"):
            ia = ia.ia
        else:
            return False
    return True


def _para_el_guion(situacion: dict[str, Any]) -> dict[str, Any]:
    """La situación para la IA guionada: cada opción de la pregunta abierta que no elige una
    tarea (la que corre su propia jugada, como el "Aprobar" de una pregunta de dos lecturas)
    lleva una marca propia en lugar de la tarea, para que el guion la nombre por su alias (O1)
    y no la confunda con otra sin tarea. Sólo la guionada: una IA real recibe la de siempre."""
    abierta = (situacion.get("estado") or {}).get("pregunta_abierta") or {}
    if not any("tarea" not in o for o in abierta.get("opciones") or []):
        return situacion
    opciones = [o if "tarea" in o else {**o, "tarea": f"opcion:{o['opcion']}"}
                for o in abierta["opciones"]]
    return {**situacion, "estado": {**situacion["estado"],
                                    "pregunta_abierta": {**abierta, "opciones": opciones}}}


def _sale_coincide(e: dict[str, Any], s: Salida, foco: set[str] | None = None) -> bool:
    """Un mensaje de Leda por su cuenta contra lo esperado. Un envío que juntó avisos de varias
    tareas (mecánica §10) cumple lo esperado de las tareas de la conversación (`foco`): la
    tarea o las tareas, y un aviso de ese tipo (y de esa tarea, si la dice) con esos hechos
    entre los suyos: los hechos de otro aviso del mismo envío no cuentan."""
    tareas = [t for t in s.tareas if foco is None or t in foco]
    if e.get("a") and e["a"] != s.a:
        return False
    if e.get("tipo") and e["tipo"] not in (s.tipos or [s.tipo]):
        return False
    if "tarea" in e and tareas != [e["tarea"]]:
        return False
    if "tareas" in e and sorted(tareas) != sorted(e["tareas"]):
        return False
    if e.get("el") and e["el"] != s.el:
        return False
    if "fotos" in e and e["fotos"] != s.fotos:
        return False
    if "botones" in e and list(e["botones"] or []) != s.botones:
        return False
    if "enlace" in e and bool(e["enlace"]) != s.enlace:
        return False
    if "hechos" not in e:
        return True
    if not s.avisos:        # un envío sin avisos guardados detrás: sus hechos, como vinieron
        de_cada_aviso = s.hechos if isinstance(s.hechos, list) else [s.hechos or {}]
        return any(cp.coincide(e["hechos"], h) for h in de_cada_aviso)
    candidatos = [a for a in s.avisos
                  if (not e.get("tipo") or a["tipo"] == e["tipo"])
                  and ("tarea" not in e or a["tarea"] == e["tarea"])
                  and (foco is None or a["tarea"] is None or a["tarea"] in foco)]
    return any(cp.coincide(e["hechos"], a["hechos"]) for a in candidatos)


def _resumen(s: Salida) -> dict[str, Any]:
    return {"a": s.a, "tipo": s.tipo or s.tipos, "tareas": s.tareas, "el": s.el,
            "hechos": s.hechos, **({"fotos": s.fotos} if s.fotos else {}),
            **({"enlace": True} if s.enlace else {})}


def correr_conversacion(conn, conv: dict[str, Any], ia: IA, *, vez: int = 1,
                        motor: Motor | None = None) -> Corrida:
    """Una corrida de la conversación sobre la base de `conn`, que tiene que estar vacía, con el
    motor de conversación `motor` (por omisión, el definitivo)."""
    motor = motor or cargar_motor()
    with _con_la_direccion_de_prueba():
        return _correr_conversacion(conn, conv, ia, vez=vez, motor=motor)


@contextlib.contextmanager
def _con_la_direccion_de_prueba():
    """La dirección pública de la corrida: la de prueba, que no es de nadie (`.invalid`), así el
    enlace a la página de una tarea sale y se puede comprobar, y nunca apunta a un servidor."""
    import dataclasses

    from leda import config as config_mod

    antes = config_mod.config
    config_mod.config = dataclasses.replace(antes, base_url=DIRECCION_DE_PRUEBA)
    try:
        yield
    finally:
        config_mod.config = antes


def _correr_conversacion(conn, conv: dict[str, Any], ia: IA, *, vez: int,
                         motor: Motor) -> Corrida:
    corrida = Corrida(str(conv["numero"]).zfill(2), conv["titulo"], conv["fuente"], vez,
                      ia.nombre, conv.get("mide", "garantias"), motor_usado=motor.nombre)
    try:
        corredor = _Corredor(conn, conv, ia, motor)
        for paso in conv.get("preludio") or []:
            corrida.pasos.append(corredor.correr(paso, preludio=True))
        for paso in conv["pasos"]:
            corrida.pasos.append(corredor.correr(paso, preludio=bool(paso.get("aparte"))))
    except Exception as e:      # una corrida que se cae se informa entera, nunca se pierde
        conn.rollback()
        corrida.error = "".join(traceback.format_exception_only(type(e), e)).strip()
        corrida.error += "\n" + "".join(traceback.format_tb(e.__traceback__)[-3:])
    corrida.llamadas = list(getattr(ia, "llamadas", []))
    return corrida
