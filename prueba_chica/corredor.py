"""El corredor de las conversaciones de prueba: una corrida de una conversación (E2-7).

`odd/tasks/prueba-chica-del-motor.md`, sección 6; ADR 0018, decisiones 5b, 6 y 7. Cada
conversación de `tests/conversaciones/` (la fuente) está copiada en un YAML de
`prueba_chica/conversaciones/` con lo que se comprueba solo. Una corrida, sobre una base ya
creada para ella:

1. carga el estado inicial (`carga.py`) y corre el **preludio**, si lo hay: lo que pasó antes,
   por el motor mismo, con las jugadas del YAML y los textos de la IA de la corrida;
2. corre cada paso por el código de verdad, con el reloj en el momento que dice el `.md`:
   - **una persona escribe** (`escribe`): se guarda como lo guarda el escuchador, corre el turno
     (`turno.procesar_turno`) y el despacho entrega la respuesta;
   - **una persona toca** una opción (`toca`): `turno.procesar_toque` con el token de esa opción;
   - **Leda por su cuenta o nadie escribe** (`relojes`): en cada momento, una vuelta del ciclo
     (`ciclo.Ciclo`): la escalera, los avisos guardados, el despacho y los avisos a la
     administración;
3. compara lo que pasó con lo esperado (`comprobar.py`) y guarda lo que la persona que lee la
   corrida necesita: lo que dijo cada uno, las jugadas, los hechos, la latencia y, con `--jev`,
   lo que Jev habría elegido.

El transporte es falso (`despachador.TransporteDePrueba`): nada sale a Telegram. La IA es la que
se le pasa: la guionada con las jugadas esperadas (`grabar.IAPerfecta`), una real o una
grabación (`grabar.IARepetida`).
"""

from __future__ import annotations

import concurrent.futures
import time
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from leda.autoridad import identificar_en_espacio
from leda.db import espacio
from leda.despachador import TransporteDePrueba
from leda.jev import Jev, TareaCandidata

from . import comprobar as cp
from . import hechos
from .carga import AREAS, PERSONAS, Mundo, cargar, momento
from .ciclo import Ciclo
from .grabar import IAMixta, IAPerfecta
from .ia import IA
from .jev_paralelo import eleccion_de_la_ia, preguntar
from .turno import procesar_toque, procesar_turno

CARPETA = Path(__file__).resolve().parent / "conversaciones"
RAIZ = Path(__file__).resolve().parents[1]


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
        if "escribe" in paso:
            n += 2 if paso in (conv.get("pasos") or []) else 1
        elif "toca" in paso:
            n += 1
        n += len(paso.get("salen") or [])
    return n


def consultas_a_jev(conv: dict[str, Any]) -> int:
    return sum(1 for p in conv.get("pasos") or [] if p.get("jev"))


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


@dataclass
class ResultadoPaso:
    paso: Any
    quien: str
    cuando: str
    texto: str | None = None
    jugadas: list[dict[str, Any]] = field(default_factory=list)
    hechos: list[Any] = field(default_factory=list)
    pregunta: Any = None
    salidas: list[Salida] = field(default_factory=list)
    latencia_ms: int | None = None
    jev: dict[str, Any] | None = None
    eleccion_de_la_ia: str | None = None
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
    def bien(self) -> bool:
        return self.error is None and not self.fallas()

    def latencias(self) -> list[int]:
        return [p.latencia_ms for p in self.pasos if p.latencia_ms is not None and
                not p.preludio]


class _Corredor:
    def __init__(self, conn, conv: dict[str, Any], ia: IA, *, jev: Jev | None) -> None:
        self.conn, self.conv, self.ia, self.jev = conn, conv, ia, jev
        self.persona = conv.get("persona", "Marcos")
        self.mundo: Mundo = cargar(conn, conv)
        self.reloj = RelojDeCorrida(momento(conv["inicio"]))
        self.transporte = TransporteDePrueba()
        self.transporte_admin = TransporteDePrueba()
        callar = lambda _texto: None    # noqa: E731 -- el ciclo cuenta lo que hace en la consola
        # Las claves y los códigos sin significado de lo que la IA recibe (`hechos.py`): una
        # falla del motor en el paso en que aparecen (revisión del contrato, 2026-10-05).
        self.sin_significado: set[str] = set()
        ia = _QueMira(ia, [], self.sin_significado)
        self.ciclo = Ciclo(conn, self.mundo.workspace_id, ia, self.reloj, self.transporte,
                           transporte_admin=self.transporte_admin, cada_s=0.0,
                           monotono=lambda: 0.0, imprimir=callar)
        self.despacho = Ciclo(conn, self.mundo.workspace_id, ia, self.reloj, self.transporte,
                              transporte_admin=self.transporte_admin, seguimiento=False,
                              imprimir=callar)
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
        if "escribe" in paso or "toca" in paso:
            self.reloj.momento = momento(paso["a_las"])
            r.cuando = paso["a_las"]
            ia = self.ia
            if preludio:
                guion = IAPerfecta(self.mundo.titulos)
                guion.preparar(paso)
                ia = IAMixta(guion, self.ia)
            elif hasattr(self.ia, "preparar"):
                self.ia.preparar(paso)
            try:
                resultado, r.texto, r.jugadas, r.latencia_ms, r.jev = self._turno(paso, ia,
                                                                                  preludio)
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
            r.eleccion_de_la_ia = eleccion_de_la_ia(r.jugadas)
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

    def _turno(self, paso, ia, preludio: bool):
        quien_corto = paso.get("quien", self.persona)
        persona = self.mundo.personas[quien_corto]
        with espacio(self.conn, self.mundo.workspace_id) as cur:
            quien = identificar_en_espacio(cur, persona["telegram"], self.mundo.workspace_id)
        self.conn.commit()
        situaciones: list[dict[str, Any]] = []
        ia_que_mira = _QueMira(ia, situaciones, self.sin_significado)
        jev = None
        if "escribe" in paso:
            texto = paso["escribe"]
            entrante = self._guardar_mensaje(quien, persona, texto)
            futuro = self._jev(paso, texto, persona) if not preludio else None
            resultado = procesar_turno(self.conn, quien, entrante, ia_que_mira, self.reloj)
            self.conn.commit()
            if futuro is not None:
                jev = futuro.result()
            jugadas = [self._jugada(j.nombre, j.datos, situaciones[-1] if situaciones else {})
                       for j in resultado.jugadas]
            latencia = self._latencia(persona["membership_id"])
        else:
            token, etiqueta = self._token(persona["membership_id"], paso["toca"])
            texto = f"[toca] {etiqueta}"
            resultado = procesar_toque(self.conn, quien, token, persona["telegram"], ia_que_mira,
                                       self.reloj)
            self.conn.commit()
            if resultado is None:
                raise LookupError(f"El toque de {paso['toca']} no es de una pregunta suya.")
            jugadas = [{"nombre": "elegir", "opcion": paso["toca"]}]
            latencia = self._latencia(persona["membership_id"])
            if paso.get("repetir_toque"):
                otra = procesar_toque(self.conn, quien, token, persona["telegram"], ia_que_mira,
                                      self.reloj)
                self.conn.commit()
                self._repetido = otra is not None and otra.repetido
        return resultado, texto, jugadas, latencia, jev

    def _guardar_mensaje(self, quien, persona, texto: str) -> str:
        with espacio(self.conn, self.mundo.workspace_id) as cur:
            cur.execute(
                """insert into inbound_message (workspace_id, telegram_message_id, chat_id,
                                                app_user_id, texto, at)
                   values (%s, %s, %s, %s, %s, %s) returning id""",
                (self.mundo.workspace_id, uuid.uuid4().int % 2_000_000_000, persona["telegram"],
                 persona["app_user_id"], texto, self.reloj.ahora()))
            entrante = str(cur.fetchone()["id"])
        self.conn.commit()
        return entrante

    def _token(self, membership_id: str, clave: str) -> tuple[str, str]:
        """El token de la opción de esa tarea en la última pregunta con opciones de la persona
        (abierta o ya cerrada: tocar un botón viejo es la situación general 7)."""
        with espacio(self.conn, self.mundo.workspace_id) as cur:
            cur.execute("""select o.token, o.etiqueta from conversation_option o
                             join conversation_question q on q.id = o.question_id
                            where q.membership_id = %s and o.valor ->> 'tarea' = %s
                            order by q.abierta_en desc limit 1""",
                        (membership_id, self.mundo.tareas[clave]))
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
        de_opcion = {o["opcion"]: de_alias.get(o.get("tarea"), o.get("etiqueta"))
                     for o in abierta.get("opciones") or []}
        salida = {"nombre": nombre}
        for k, v in (datos or {}).items():
            if k in ("tarea", "tarea_correcta"):
                v = de_alias.get(v, v)
            elif k == "opcion":
                v = de_opcion.get(v, v)
            salida[k] = v
        return salida

    def _jev(self, paso, texto: str, persona: dict[str, Any]):
        if self.jev is None or not paso.get("jev"):
            return None
        consulta = paso["jev"]
        estados = cp.foto(self.conn, self.mundo)["estados"]
        candidatas = []
        for clave, t in (self.conv.get("tareas") or {}).items():
            if estados.get(clave) in ("terminada", "cancelada"):
                continue
            nombre, _, area, _ = PERSONAS[t["responsable"]]
            candidatas.append((clave, TareaCandidata(
                id=self.mundo.tareas[clave], titulo=t["titulo"], area=AREAS[area],
                responsable=nombre)))
        ejecutor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        futuro = ejecutor.submit(preguntar, self.jev, mensaje=texto,
                                 referencia=consulta.get("referencia", texto),
                                 candidatas=candidatas, quien=persona["nombre"],
                                 correcta=consulta.get("correcta"))
        ejecutor.shutdown(wait=False)
        return futuro

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
            fila_id = next((k for k, s in despues["salidas"].items()
                            if k not in usados and s["a"] == quien
                            and e.texto.endswith(s["cuerpo"])), None)
            if fila_id is not None:
                usados.add(fila_id)
            fila = despues["salidas"].get(fila_id, {})
            avisos, hechos = _avisos_del_envio(avisos_de.get(fila_id, []), self.mundo.titulos)
            tipos = sorted({a["tipo"] for a in avisos})
            botones = [self.mundo.clave_de_titulo(b.etiqueta) or b.etiqueta for b in e.botones]
            salidas.append(Salida(
                quien, e.texto, botones, bool(fila.get("es_respuesta")),
                tipo=tipos[0] if len(tipos) == 1 else None,
                tareas=list(dict.fromkeys(a["tarea"] for a in avisos if a["tarea"])),
                hechos=(hechos[0] if len(hechos) == 1 else hechos) if hechos else None,
                el=cp.dia(self.reloj.ahora()), tipos=tipos,
                avisos=avisos))
        return salidas

    # -- lo que se comprueba ------------------------------------------------------------------

    def _comprobar(self, paso, r: ResultadoPaso, resultado, antes, despues) -> cp.Comprobacion:
        c = cp.Comprobacion()
        hubo = cp.efectos(antes, despues)
        titulos = self.mundo.titulos
        quien = paso.get("quien", self.persona)
        if "escribe" in paso or "toca" in paso:
            jugadas_bien = cp.comprobar_jugadas(c, paso.get("jugadas") or [], r.jugadas,
                                                paso["escribe"]) \
                if "escribe" in paso else True
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
            otros = [i for i in hubo["incidentes"] if i["etapa"] != cp.ETAPA_FUERA_DE_LA_LISTA]
            if otros:
                c.falla(cp.MOTOR, "incidente", [], otros)
        estado = dict(paso.get("estado_despues") or {})
        de = estado.pop("de", self.persona)
        cp.comprobar_estado(c, estado, despues, de, clase)
        cp.comprobar_avisos_en_estado(c, paso.get("estado_avisos") or [], despues, titulos)
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
    `sin_significado` las claves y los códigos de cada pedido que no tienen significado."""

    def __init__(self, ia: IA, situaciones: list[dict[str, Any]],
                 sin_significado: set[str]) -> None:
        self.ia, self.situaciones, self.faltan = ia, situaciones, sin_significado

    @property
    def nombre(self) -> str:
        return self.ia.nombre

    def preparar(self, paso: dict[str, Any]) -> None:
        if hasattr(self.ia, "preparar"):
            self.ia.preparar(paso)

    def elegir_jugadas(self, situacion):
        self.situaciones.append(situacion)
        self.faltan |= hechos.sin_significado(situacion)
        return self.ia.elegir_jugadas(situacion)

    def redactar(self, pedido):
        self.faltan |= hechos.sin_significado(pedido)
        return self.ia.redactar(pedido)


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
            "hechos": s.hechos}


def correr_conversacion(conn, conv: dict[str, Any], ia: IA, *, vez: int = 1,
                        jev: Jev | None = None) -> Corrida:
    """Una corrida de la conversación sobre la base de `conn`, que tiene que estar vacía."""
    corrida = Corrida(str(conv["numero"]).zfill(2), conv["titulo"], conv["fuente"], vez,
                      ia.nombre, conv.get("mide", "garantias"))
    try:
        corredor = _Corredor(conn, conv, ia, jev=jev)
        for paso in conv.get("preludio") or []:
            corrida.pasos.append(corredor.correr(paso, preludio=True))
        for paso in conv["pasos"]:
            corrida.pasos.append(corredor.correr(paso))
    except Exception as e:      # una corrida que se cae se informa entera, nunca se pierde
        conn.rollback()
        corrida.error = "".join(traceback.format_exception_only(type(e), e)).strip()
        corrida.error += "\n" + "".join(traceback.format_tb(e.__traceback__)[-3:])
    corrida.llamadas = list(getattr(ia, "llamadas", []))
    return corrida
