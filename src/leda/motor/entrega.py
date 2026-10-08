"""La entrega de una tarea con su evidencia (ADR 0019, decisiones 3 a 5; ADR 0018, decisiones 2 y 4).

Porción 2 de la C-3 (`odd/tasks/fase-c.md`). "Terminé" con o sin fotos lleva a una **vista
previa de la entrega** que muestra cada pieza: lo que la persona escribió, cada foto, video o
archivo y cada enlace, también lo que mandó antes durante la tarea (`archivo_de_tarea`), que
entra sólo si queda; qué cubre cada pieza de lo que pide la política, en palabras de todos los
días; y qué falta. Nada entra a la evidencia sin que la persona lo vea. Con la política
completa, la vista previa se confirma con el botón o por escrito; al confirmar, la cocina escribe
las piezas y el paso a revisión en un solo acto (`herramientas.entregar_tarea`). "Terminé" nunca
lleva a terminada (constitución §11).

**El tema abierto.** La entrega en curso es una pregunta de Leda (ADR 0018, decisión 3): la de
confirmar (`CONFIRMAR_ENTREGA`, con el botón "Confirmar") o la de lo que falta
(`LO_QUE_FALTA_DE_LA_ENTREGA`, sin botones). Su jugada guarda las piezas, su huella y lo que se
le mostró a la persona (`muestra`, lo que la IA recibe en el estado). Cada cambio de la entrega
(una pieza que llega, una que se saca, lo que cubre un texto) cierra la vista previa anterior,
registrada como reemplazada, y abre la nueva: un botón viejo cae en la situación general 7.

**Lo que trae un mensaje** (`lo_que_trae`): los archivos guardados, los enlaces y el texto sin
ellos. Con una entrega abierta, los archivos y los enlaces se suman solos a esa entrega (el
estado dice que Leda la estaba esperando; ADR 0019, decisión 4); el texto, sólo si la persona
entrega o suma algo (la jugada `entregar`). Sin una entrega abierta, un archivo que ninguna
jugada tomó lleva la pregunta de para qué tarea es (situación general 5), y queda dicho de esa
tarea (`guardar_para_la_entrega`) sin ser evidencia.

**La confirmación escrita, con su guarda** (ADR 0018, decisión 2): vale sólo si lo que se
confirma es lo último que la persona vio (la vista previa de `conversation_state.
mostrado_para_confirmar`, mostrada en un mensaje anterior) y no cambió desde entonces (su huella,
que incluye la de cada archivo). Si en el mismo mensaje llegó una pieza, la entrega cambia antes
de confirmar, la confirmación no vale y Leda muestra lo nuevo.

**Qué cubre cada pieza** lo cuenta el código: un texto, los tipos que la persona dice con él (la
IA los nombra en `el_texto_cubre`; sin decirlo, sólo los que nada más un texto puede cubrir);
cada foto, archivo o enlace, un tipo que su clase acepta, repartidos para cubrir lo más posible
(`cubrir`). La regla de qué falta es una sola, la de la base (`tipos_de_evidencia_que_faltan`).
El código cuenta; quien aprueba juzga: que haya una foto no dice qué muestra (mecánica §5).

**Corregir** (`corregir`, situación general 3): "la foto del martes sacala" saca una pieza de la
vista previa; después de entregada, la retira (`herramientas.retirar_evidencia`): se agrega un
retiro, nada se borra (9f).
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ..herramientas import ejecutar

from . import preguntas
from .auditoria import auditar

BOTON_CONFIRMAR = "Confirmar"
DE_LA_ENTREGA = (preguntas.CONFIRMAR_ENTREGA, preguntas.LO_QUE_FALTA_DE_LA_ENTREGA)

# Qué es cada pieza, como se le dice a la IA (`es`).
LO_QUE_ESCRIBIO, UNA_FOTO, UN_VIDEO, UN_ARCHIVO, UN_ENLACE = (
    "lo_que_escribio", "una_foto", "un_video", "un_archivo", "un_enlace")

# Los códigos de los hechos de una entrega.
PARA_CONFIRMAR = "para_confirmar"
LE_FALTA_EVIDENCIA = "le_falta_evidencia"
ENTREGADA = "entregada"
NO_VALE_LA_CONFIRMACION = "no_vale_la_confirmacion"
LLEGO_ALGO_DESPUES = "llego_algo_despues"
CAMBIO_LO_QUE_SE_MOSTRO = "cambio_lo_que_se_mostro"
NO_ES_LO_ULTIMO_QUE_VIO = "no_es_lo_ultimo_que_vio"
NADA_PARA_CONFIRMAR = "nada_para_confirmar"

_ENLACE = re.compile(r"https?://\S+", re.IGNORECASE)


def _fichas():
    from . import fichas            # se importan entre sí: fichas declara estas jugadas
    return fichas


# --- Lo que trae un mensaje ------------------------------------------------------------------

def lo_que_trae(cur, entrante_id: str | None, texto: str | None) -> dict[str, Any]:
    """Las piezas posibles de un mensaje: el texto sin sus enlaces, cada enlace y cada archivo
    guardado (lo que no se pudo recibir no es una pieza: la IA lo cuenta aparte). `tomada`
    dice si una jugada ya las sumó a algo."""
    if entrante_id is None:
        return {"texto": None, "enlaces": [], "archivos": [], "tomada": False}
    cur.execute("""select a.id, a.clase, a.sha256, a.nombre_original, a.recibido_en,
                          m.que_llego
                     from archivo_de_mensaje m
                     join archivo a on a.workspace_id = m.workspace_id and a.id = m.archivo_id
                    where m.inbound_message_id = %s
                    order by m.telegram_message_id, m.at""", (entrante_id,))
    vistos: set[str] = set()
    archivos = []
    for f in cur.fetchall():
        if str(f["id"]) in vistos:
            continue
        vistos.add(str(f["id"]))
        archivos.append(_pieza_de_archivo(f))
    cur.execute("""select count(*) n from archivo_de_mensaje
                    where inbound_message_id = %s and rechazo is not null""", (entrante_id,))
    rechazados = cur.fetchone()["n"]
    escrito = texto or ""
    enlaces = _ENLACE.findall(escrito)
    sin_enlaces = " ".join(_ENLACE.sub(" ", escrito).split())
    return {"texto": sin_enlaces or None, "enlaces": enlaces, "archivos": archivos,
            "rechazados": rechazados, "entrante": entrante_id, "tomada": False}


def _pieza_de_archivo(f: Mapping[str, Any], *, antes: bool = False) -> dict[str, Any]:
    clase = "imagen" if f["clase"] == "imagen" else "archivo"
    es = UNA_FOTO if clase == "imagen" else UN_VIDEO if f["clase"] == "video" else UN_ARCHIVO
    return {"id": f"a:{f['id']}", "clase": clase, "es": es, "archivo_id": str(f["id"]),
            "sha256": f["sha256"], "nombre": f["nombre_original"],
            "llego_el": f["recibido_en"].isoformat(), "antes": antes}


def _piezas_del_mensaje(ctx, el_texto_cubre: Sequence[str] | None, *,
                        con_el_texto: bool) -> list[dict[str, Any]]:
    """Las piezas que trae el mensaje del turno, y lo marca tomado. El texto va sólo si
    `con_el_texto` (la persona entrega o suma algo con lo que escribe)."""
    llegada = ctx.llegada
    if not llegada or llegada.get("tomada"):
        return []
    llegada["tomada"] = True
    ahora = ctx.ahora.isoformat()
    piezas = []
    if con_el_texto and llegada.get("texto"):
        piezas.append({"id": f"t:{llegada['entrante']}", "clase": "texto",
                       "es": LO_QUE_ESCRIBIO, "texto": llegada["texto"], "llego_el": ahora,
                       "cubre_dicho": None if el_texto_cubre is None else list(el_texto_cubre),
                       "antes": False})
    for i, enlace in enumerate(llegada.get("enlaces") or []):
        piezas.append({"id": f"e:{llegada['entrante']}:{i}", "clase": "enlace",
                       "es": UN_ENLACE, "uri": enlace, "llego_el": ahora, "antes": False})
    piezas += [dict(a) for a in llegada.get("archivos") or []]
    return piezas


def trae_algo(ctx) -> bool:
    """Si el mensaje trajo algo que se suma a una entrega abierta sin que se lo pidan: un
    archivo o un enlace (o un archivo que no se pudo recibir, que se cuenta con la entrega)."""
    llegada = ctx.llegada or {}
    return bool(llegada.get("archivos") or llegada.get("enlaces")
                or llegada.get("rechazados"))


# --- La política de la tarea -----------------------------------------------------------------

@dataclass(frozen=True)
class Politica:
    """Lo que pide la tarea (`task.evidencia_requerida`) y, por tipo, las clases que acepta y
    cómo se dice (del pack, `task_evidence_policy.tipos`)."""

    pide: tuple[str, ...]
    tipos: Mapping[str, Any]
    version: int | None

    def clases(self, tipo: str) -> tuple[str, ...]:
        return tuple((self.tipos.get(tipo) or {}).get("clases") or ())

    def en_palabras(self, tipo: str) -> str:
        return (self.tipos.get(tipo) or {}).get("en_palabras") or tipo


def politica(cur, task_id: str) -> Politica:
    cur.execute("""select t.evidencia_requerida, p.tipos, p.version
                     from task t
                     left join task_evidence_policy p
                       on p.workspace_id = t.workspace_id and p.area_id = t.area_id
                    where t.id = %s""", (task_id,))
    fila = cur.fetchone()
    return Politica(tuple(fila["evidencia_requerida"] or ()), fila["tipos"] or {},
                    fila["version"])


def para_la_ia(cur, tareas: Sequence[dict[str, Any]], zona) -> tuple[dict[str, Any], ...]:
    """Lo de la entrega que la IA necesita para elegir, en cada tarea: lo que pide una tarea en
    curso (cada tipo con su código, para nombrarlo en `el_texto_cubre`, y sus palabras) y lo
    entregado de una tarea en revisión, por pieza (para retirar una)."""
    con = []
    for t in tareas:
        t = dict(t)
        if t["estado"] == "en_curso":
            pol = politica(cur, t["id"])
            if pol.pide:
                t["evidencia_que_pide"] = [{"tipo_de_evidencia": tipo,
                                            "en_palabras": pol.en_palabras(tipo)}
                                           for tipo in pol.pide]
        elif t["estado"] == "en_revision":
            entregado = _lo_entregado(cur, t["id"])
            if entregado:
                pol = politica(cur, t["id"])
                t["lo_entregado"] = mostrar(entregado, pol, zona)
        con.append(t)
    return tuple(con)


# --- Qué cubre cada pieza --------------------------------------------------------------------

def cubrir(piezas: list[dict[str, Any]], pol: Politica) -> None:
    """Pone en cada pieza los tipos de la política que cubre (`cubre`). Un texto, los que la
    persona dice con él, si un texto los cubre; sin decirlo, sólo los que nada más un texto
    puede cubrir. Cada foto, archivo o enlace, un tipo que su clase acepta: primero se reparten
    para cubrir lo más posible (los tipos más exigentes primero, las piezas de esta entrega
    antes que las mandadas antes); las que sobran cubren lo mismo que la primera de su clase."""
    textos = [p for p in piezas if p["clase"] == "texto"]
    for p in textos:
        dicho = p.get("cubre_dicho")
        con_texto = [t for t in pol.pide if "texto" in pol.clases(t)]
        p["cubre"] = ([t for t in con_texto if pol.clases(t) == ("texto",)] if dicho is None
                      else [t for t in con_texto if t in dicho])
    cubiertos = {t for p in textos for t in p["cubre"]}
    tipos = sorted((t for t in pol.pide if t not in cubiertos),
                   key=lambda t: (len(pol.clases(t)), pol.pide.index(t)))
    otras = ([p for p in piezas if p["clase"] != "texto" and not p.get("antes")]
             + [p for p in piezas if p["clase"] != "texto" and p.get("antes")])
    de_pieza: dict[int, str] = {}

    def asignar(tipo: str, vistas: set[int]) -> bool:
        for i, p in enumerate(otras):
            if i in vistas or p["clase"] not in pol.clases(tipo):
                continue
            vistas.add(i)
            if i not in de_pieza or asignar(de_pieza[i], vistas):
                de_pieza[i] = tipo
                return True
        return False

    for tipo in tipos:
        asignar(tipo, set())
    for i, p in enumerate(otras):
        if i in de_pieza:
            p["cubre"] = [de_pieza[i]]
            continue
        igual = next((de_pieza[j] for j, q in enumerate(otras)
                      if j in de_pieza and q["clase"] == p["clase"]), None)
        p["cubre"] = [igual] if igual else [t for t in pol.pide
                                            if p["clase"] in pol.clases(t)][:1]


def _faltan(cur, task_id: str, piezas: Sequence[dict[str, Any]]) -> list[str]:
    """Los tipos que quedan sin cubrir con estas piezas y la evidencia vigente: la regla de la
    base, la misma que exige la cocina al entregar y al aprobar."""
    cur.execute("select tipos_de_evidencia_que_faltan(%s, %s) as t",
                (task_id, json.dumps([{"clase": p["clase"], "cubre": p["cubre"]}
                                      for p in piezas])))
    return list(cur.fetchone()["t"] or [])


def _huella(task_id: str, estado: str, pol: Politica, piezas: Sequence[dict]) -> str:
    """La huella de lo que se muestra: la tarea y su estado, la versión de la política y cada
    pieza con su contenido (la huella de cada archivo) y lo que cubre."""
    datos = [task_id, estado, pol.version,
             [[p["id"], p["clase"], p.get("sha256") or p.get("texto") or p.get("uri"),
               p["cubre"]] for p in piezas]]
    return hashlib.sha256(json.dumps(datos, ensure_ascii=False).encode()).hexdigest()


def _ordenar(piezas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Las de esta entrega primero, en el orden en que llegaron; las mandadas antes, aparte."""
    return ([p for p in piezas if not p.get("antes")]
            + sorted((p for p in piezas if p.get("antes")), key=lambda p: p["llego_el"]))


def mostrar(piezas: Sequence[dict[str, Any]], pol: Politica, zona) -> list[dict[str, Any]]:
    """Cada pieza como la recibe la IA: su alias, qué es, lo que dice (un texto), su nombre (un
    archivo) o el enlace, qué cubre en palabras de todos los días y, si es de antes, de qué día
    es. Ningún id, ninguna huella ni el nombre de un tipo de la política."""
    vistas = []
    for i, p in enumerate(piezas, 1):
        una: dict[str, Any] = {"pieza": f"P{i}", "es": p["es"]}
        if p.get("texto"):
            una["dice"] = p["texto"]
        if p.get("uri"):
            una["enlace"] = p["uri"]
        if p.get("nombre"):
            una["nombre_del_archivo"] = p["nombre"]
        una["cubre"] = [pol.en_palabras(t) for t in p.get("cubre") or []]
        if p.get("antes"):
            una["mandado_antes_el"] = datetime.fromisoformat(p["llego_el"]).astimezone(
                zona).date().isoformat()
        vistas.append(una)
    return vistas


# --- La entrega abierta ----------------------------------------------------------------------

def abierta(ctx, task_id: str | None = None) -> dict[str, Any] | None:
    """La entrega sin cerrar de la persona: la de esa tarea o, sin tarea, la que es su pregunta
    abierta ahora."""
    if task_id is None:
        q = preguntas.actual(ctx.cur, ctx.quien.membership_id)
        return q if q is not None and q["tipo"] in DE_LA_ENTREGA else None
    ctx.cur.execute("""select * from conversation_question
                        where membership_id = %s and task_id = %s and tipo = any(%s)
                          and cerrada_en is null
                        order by abierta_en desc limit 1""",
                    (ctx.quien.membership_id, task_id, list(DE_LA_ENTREGA)))
    return ctx.cur.fetchone()


def _ciclo_desde(cur, task_id: str):
    """Desde cuándo corre el ciclo de entrega de la tarea: el último pedido de cambios."""
    cur.execute("""select max(at) as desde from approval
                    where sujeto_tipo = 'tarea' and sujeto_id = %s
                      and decision = 'rechazado'""", (task_id,))
    return cur.fetchone()["desde"]


def _mandado_antes(ctx, task_id: str) -> list[dict[str, Any]]:
    """Lo que la persona dijo que es de la tarea durante el ciclo y todavía no es evidencia:
    entra en la vista previa, aparte, y sólo si queda (ADR 0019, decisión 4)."""
    desde = _ciclo_desde(ctx.cur, task_id)
    ctx.cur.execute(
        """select distinct on (a.id) a.id, a.clase, a.sha256, a.nombre_original,
                  a.recibido_en, d.at
             from archivo_de_tarea d
             join archivo a on a.workspace_id = d.workspace_id and a.id = d.archivo_id
            where d.task_id = %s and d.dicho_por_membership_id = %s
              and (%s::timestamptz is null or d.at > %s::timestamptz)
              and not exists (select 1 from evidence e
                               where e.task_id = d.task_id and e.archivo_id = a.id
                                 and (%s::timestamptz is null or e.at > %s::timestamptz))
            order by a.id, d.at""",
        (task_id, ctx.quien.membership_id, desde, desde, desde, desde))
    return [_pieza_de_archivo(f, antes=True)
            for f in sorted(ctx.cur.fetchall(), key=lambda f: f["recibido_en"])]


def _lo_entregado(cur, task_id: str) -> list[dict[str, Any]]:
    """La evidencia vigente de una tarea entregada, por pieza, en el orden en que se escribió:
    la del ciclo vigente, sin las retiradas. Con su id, para retirar una."""
    desde = _ciclo_desde(cur, task_id)
    cur.execute(
        """select e.id, e.clase, e.texto, e.uri, e.cubre, e.at, a.nombre_original,
                  a.clase as clase_del_archivo, a.sha256
             from evidence e
             left join archivo a on a.workspace_id = e.workspace_id and a.id = e.archivo_id
            where e.task_id = %s
              and (%s::timestamptz is null or e.at > %s::timestamptz)
              and not exists (select 1 from evidencia_retirada w where w.evidence_id = e.id)
            order by e.at, e.id""", (task_id, desde, desde))
    piezas = []
    for f in cur.fetchall():
        es = {"texto": LO_QUE_ESCRIBIO, "enlace": UN_ENLACE, "imagen": UNA_FOTO}.get(
            f["clase"], UN_VIDEO if f["clase_del_archivo"] == "video" else UN_ARCHIVO)
        piezas.append({"evidencia_id": str(f["id"]), "id": f"v:{f['id']}", "clase": f["clase"],
                       "es": es, "texto": f["texto"], "uri": f["uri"],
                       "nombre": f["nombre_original"], "sha256": f["sha256"],
                       "cubre": list(f["cubre"] or []), "llego_el": f["at"].isoformat(),
                       "antes": False})
    return piezas


# --- La vista previa -------------------------------------------------------------------------

def _tarea_de(ctx, task_id: str) -> dict[str, Any]:
    ctx.cur.execute("select titulo, estado::text estado from task where id = %s", (task_id,))
    fila = ctx.cur.fetchone()
    de = next((t for t in ctx.tareas if t["id"] == str(task_id)), None)
    return {"id": str(task_id), "alias": de["alias"] if de else None,
            "titulo": fila["titulo"], "estado": fila["estado"]}


def _quien_aprueba(ctx) -> dict[str, str] | None:
    return _fichas().referente(ctx.cur, ctx.quien.membership_id)


def _mostrar_la_entrega(ctx, tarea: dict[str, Any], piezas: list[dict[str, Any]],
                        vieja: dict[str, Any] | None) -> dict[str, Any]:
    """Calcula la vista previa de la entrega (qué cubre cada pieza, qué falta y su huella), la
    deja como el tema abierto y devuelve sus hechos. Si no cambió, la de antes sigue valiendo;
    si cambió, la de antes queda reemplazada (situación general 7)."""
    cur = ctx.cur
    piezas = _ordenar(piezas)
    pol = politica(cur, tarea["id"])
    cubrir(piezas, pol)
    faltan = _faltan(cur, tarea["id"], piezas)
    huella = _huella(tarea["id"], tarea["estado"], pol, piezas)
    tipo = preguntas.LO_QUE_FALTA_DE_LA_ENTREGA if faltan else preguntas.CONFIRMAR_ENTREGA
    muestra = mostrar(piezas, pol, ctx.calendario.zona)
    fichas = _fichas()

    sigue = (vieja is not None and vieja["tipo"] == tipo
             and (vieja["jugada"] or {}).get("huella") == huella)
    if sigue:
        pregunta_id = str(vieja["id"])
        ahora_si = True
        vigente = preguntas.actual(cur, ctx.quien.membership_id)
        if vigente is None or str(vigente["id"]) != pregunta_id:
            preguntas.retomar(ctx, pregunta_id)
    else:
        if vieja is not None:
            preguntas.cerrar(ctx, str(vieja["id"]), "sin_efecto",
                             {"reemplazada": True, "tarea": tarea["id"]})
        jugada = {"nombre": "entregar", "piezas": piezas, "huella": huella, "muestra": muestra}
        opciones = ([(BOTON_CONFIRMAR, {"tarea": tarea["id"], "jugada": "confirmar"})]
                    if not faltan else [])
        ahora_si, pregunta_id = preguntas.abrir_con_id(ctx, tipo, tarea["id"], jugada=jugada,
                                                       opciones=opciones)
    _que_sea_lo_mostrado(ctx, pregunta_id if not faltan else None, huella)

    quien = _quien_aprueba(ctx)
    hecho: dict[str, Any] = {
        "resultado": LE_FALTA_EVIDENCIA if faltan else PARA_CONFIRMAR,
        "tarea": {"alias": tarea["alias"], "titulo": tarea["titulo"]}, "entrega": muestra}
    if faltan:
        hecho["le_falta"] = [pol.en_palabras(t) for t in faltan]
    if quien is not None:
        hecho["al_confirmar"] = {"queda_esperando_la_aprobacion_de": quien["nombre"]}
    fichas.nombrar_pregunta(hecho, "pregunta" if ahora_si else "pregunta_para_despues", tipo,
                            pregunta_id)
    return hecho


def _que_sea_lo_mostrado(ctx, pregunta_id: str | None, huella: str | None) -> None:
    """Lo último que Leda mostró para confirmar y su huella (ADR 0018, decisión 3.1): la
    vista previa completa que espera confirmación, o nada."""
    ctx.cur.execute(
        """insert into conversation_state (membership_id, workspace_id,
                                           mostrado_para_confirmar, huella, actualizado_en)
           values (%s, %s, %s, %s, %s)
           on conflict (membership_id) do update
              set mostrado_para_confirmar = excluded.mostrado_para_confirmar,
                  huella = excluded.huella, actualizado_en = excluded.actualizado_en""",
        (ctx.quien.membership_id, ctx.quien.workspace_id,
         json.dumps({"pregunta": pregunta_id}) if pregunta_id else None,
         huella if pregunta_id else None, ctx.ahora))


def _lo_mostrado(ctx) -> tuple[str | None, str | None]:
    ctx.cur.execute("""select mostrado_para_confirmar, huella from conversation_state
                        where membership_id = %s""", (ctx.quien.membership_id,))
    fila = ctx.cur.fetchone()
    if fila is None or not fila["mostrado_para_confirmar"]:
        return None, None
    return (fila["mostrado_para_confirmar"] or {}).get("pregunta"), fila["huella"]


def _piezas_de(q: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    return [dict(p) for p in ((q or {}).get("jugada") or {}).get("piezas") or []]


# --- Las jugadas -----------------------------------------------------------------------------

def entregar(ctx, datos: dict, tarea: dict) -> dict:
    """"Terminé", con o sin fotos: la vista previa de la entrega, con lo que trae el mensaje (y
    lo que escribió) sumado a la entrega abierta de esa tarea o, si no hay, a lo que mandó antes
    durante la tarea. Nada se escribe en la tarea hasta confirmar."""
    vieja = abierta(ctx, tarea["id"])
    piezas = _piezas_de(vieja) if vieja is not None else _mandado_antes(ctx, tarea["id"])
    dicho = datos.get("el_texto_cubre")
    dicho = [str(t) for t in dicho] if isinstance(dicho, list) else None
    suma = _piezas_del_mensaje(ctx, dicho, con_el_texto=True)
    piezas = _sin_repetidas(piezas + suma)
    if dicho is not None and not any(p["clase"] == "texto" and p in suma for p in piezas):
        # Lo que dice que cubre lo que escribió antes en esta entrega.
        for p in piezas:
            if p["clase"] == "texto":
                p["cubre_dicho"] = list(dicho)
    hecho = _mostrar_la_entrega(ctx, _tarea_de(ctx, tarea["id"]), piezas, vieja)
    if suma:
        hecho["sumo"] = mostrar_sumadas(ctx, suma, hecho)
    return hecho


def mostrar_sumadas(ctx, suma: Sequence[dict], hecho: dict) -> list[str]:
    """Los alias de las piezas que se sumaron en este mensaje, de lo que muestra la entrega."""
    ids = {p["id"] for p in suma}
    q = abierta(ctx, _id_de_la_tarea(ctx, hecho))
    piezas = _piezas_de(q)
    return [f"P{i}" for i, p in enumerate(piezas, 1) if p["id"] in ids]


def _id_de_la_tarea(ctx, hecho: dict) -> str | None:
    alias = (hecho.get("tarea") or {}).get("alias")
    t = ctx.tarea(alias) if alias else None
    return t["id"] if t else None


def _sin_repetidas(piezas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    vistas, unicas = set(), []
    for p in piezas:
        if p["id"] not in vistas:
            vistas.add(p["id"])
            unicas.append(p)
    return unicas


def al_terminar_las_jugadas(ctx) -> list[dict[str, Any]]:
    """Lo que trajo el mensaje y ninguna jugada tomó. Con una entrega abierta, sus archivos y
    enlaces se suman a ella (y lo que no se pudo recibir se cuenta con ella). Sin una, los
    archivos guardados llevan la pregunta de para qué tarea son (`guardar_para_la_entrega`)."""
    llegada = ctx.llegada
    if not llegada or llegada.get("tomada") or not trae_algo(ctx):
        return []
    q = abierta(ctx)
    if q is not None:
        tarea = _tarea_de(ctx, str(q["task_id"]))
        suma = _piezas_del_mensaje(ctx, None, con_el_texto=False)
        hecho = {"jugada": "entregar",
                 **_mostrar_la_entrega(ctx, tarea, _sin_repetidas(_piezas_de(q) + suma), q)}
        if suma:
            hecho["sumo"] = mostrar_sumadas(ctx, suma, hecho)
        return [hecho]
    if not llegada.get("archivos"):
        return []
    fichas = _fichas()
    from .ia import Jugada
    archivos = [a["archivo_id"] for a in llegada["archivos"]]
    llegada["tomada"] = True
    return [fichas.correr(fichas.FICHAS["guardar_para_la_entrega"], ctx,
                          Jugada("guardar_para_la_entrega", {"archivos": archivos}))]


def guardar_para_la_entrega(ctx, datos: dict, tarea: dict) -> dict:
    """La persona dice de qué tarea es un archivo que mandó sin entregarla: queda dicho de esa
    tarea, sin ser evidencia, para mostrárselo cuando la entregue (ADR 0019, decisión 4). Los
    archivos son los de la pregunta que contesta o, si no, los de este mensaje."""
    archivos = [str(a) for a in datos.get("archivos") or []]
    if not archivos:
        archivos = [p["archivo_id"] for p in _piezas_del_mensaje(ctx, None, con_el_texto=False)
                    if p.get("archivo_id")]
    if not archivos:
        return {"resultado": "no_se_puede", "motivo": "sin_archivos",
                "tarea": {"alias": tarea["alias"], "titulo": tarea["titulo"]}}
    cur = ctx.cur
    cur.execute("""select id, clase, nombre_original from archivo where id = any(%s::uuid[])
                    order by recibido_en""", (archivos,))
    filas = cur.fetchall()
    for f in filas:
        cur.execute("""insert into archivo_de_tarea (workspace_id, archivo_id, task_id,
                                                     dicho_por_membership_id, at)
                       values (%s, %s, %s, %s, %s)""",
                    (ctx.quien.workspace_id, f["id"], tarea["id"], ctx.quien.membership_id,
                     ctx.ahora))
    auditar(cur, accion="guardar_para_la_entrega", workspace_id=ctx.quien.workspace_id,
            sujeto_tipo="task", sujeto_id=tarea["id"], quien=ctx.quien,
            detalle={"archivos": [str(f["id"]) for f in filas], "at": ctx.ahora.isoformat(),
                     "inbound_message_id": ctx.entrante_id})
    return {"resultado": "anotado", "tarea": {"alias": tarea["alias"], "titulo": tarea["titulo"]},
            "para_cuando_la_entregue": [
                {"es": UNA_FOTO if f["clase"] == "imagen"
                 else UN_VIDEO if f["clase"] == "video" else UN_ARCHIVO,
                 **({"nombre_del_archivo": f["nombre_original"]} if f["nombre_original"]
                    else {})} for f in filas]}


def confirmar(ctx, datos: dict, tarea: dict | None) -> dict:
    """La confirmación de la entrega, tocada o escrita. Con el botón vale la vista previa de ese
    botón, si sigue igual; escrita, la guarda de la decisión 2: lo último que la persona vio,
    en un mensaje anterior, y sin cambios. Si no vale, Leda muestra lo nuevo y no entrega."""
    cur = ctx.cur
    tocada = datos.get("de_la_pregunta")
    if tocada:
        cur.execute("select * from conversation_question where id = %s", (tocada,))
        q = cur.fetchone()
    else:
        q = abierta(ctx, tarea["id"] if tarea else None) or abierta(ctx)
    if q is None:
        return {"resultado": "no_se_puede", "motivo": NADA_PARA_CONFIRMAR}
    tarea_q = _tarea_de(ctx, str(q["task_id"]))
    piezas = _piezas_de(q)

    # Lo que llegó con este mensaje se suma antes: si cambió algo, no es lo que vio.
    suma = _piezas_del_mensaje(ctx, None, con_el_texto=False) \
        if not tocada and trae_algo(ctx) else []
    motivo = None
    if suma:
        motivo = LLEGO_ALGO_DESPUES
    elif not tocada:
        mostrada, huella = _lo_mostrado(ctx)
        vigente = preguntas.actual(cur, ctx.quien.membership_id)
        if (q["tipo"] != preguntas.CONFIRMAR_ENTREGA or mostrada != str(q["id"])
                or vigente is None or str(vigente["id"]) != str(q["id"])
                or str(q["id"]) in ctx.preguntas_del_turno):
            motivo = NO_ES_LO_ULTIMO_QUE_VIO
    if motivo is None:
        pol = politica(cur, tarea_q["id"])
        cubrir(piezas, pol)
        if (_huella(tarea_q["id"], tarea_q["estado"], pol, _ordenar(piezas))
                != (q["jugada"] or {}).get("huella")
                or _faltan(cur, tarea_q["id"], piezas)):
            motivo = CAMBIO_LO_QUE_SE_MOSTRO
    if motivo is not None:
        vieja = q if q["cerrada_en"] is None else None
        hecho = _mostrar_la_entrega(ctx, tarea_q, _sin_repetidas(piezas + suma), vieja)
        hecho.update({"resultado": NO_VALE_LA_CONFIRMACION, "motivo": motivo,
                      "como_queda": hecho.pop("resultado")})
        if suma:
            hecho["sumo"] = mostrar_sumadas(ctx, suma, hecho)
        return hecho

    r = ejecutar(cur, ctx.quien, "entregar_tarea",
                 {"tarea_id": tarea_q["id"], "piezas": [_para_la_cocina(p) for p in piezas]},
                 ya_confirmada=True)
    fichas = _fichas()
    if r.get("estado") != "en_revision":
        return fichas.no_hecho(r, {"alias": tarea_q["alias"], "titulo": tarea_q["titulo"]})
    if q["cerrada_en"] is None:
        preguntas.cerrar(ctx, str(q["id"]), "respondida",
                         {"jugada": "confirmar", "tarea": tarea_q["id"]})
    _que_sea_lo_mostrado(ctx, None, None)
    fichas.cerrar_esperas(ctx, tarea_q["id"])
    pol = politica(cur, tarea_q["id"])
    hecho: dict[str, Any] = {
        "resultado": ENTREGADA,
        "tarea": {"alias": tarea_q["alias"], "titulo": tarea_q["titulo"]},
        "estado": "en_revision", "entrega": mostrar(_ordenar(piezas), pol, ctx.calendario.zona)}
    quien = _quien_aprueba(ctx)
    if quien is not None:
        hecho["queda_esperando_la_aprobacion_de"] = quien["nombre"]
        hecho["aviso_a_quien_aprueba"] = {
            "a": quien["nombre"],
            fichas.LLEGA: ctx.calendario.dentro_de_jornada(ctx.ahora).isoformat()}
    return hecho


def _para_la_cocina(p: Mapping[str, Any]) -> dict[str, Any]:
    """Una pieza como la recibe `entregar_tarea`: su contenido y lo que cubre. La clase la
    vuelve a fijar la cocina por el contenido."""
    if p.get("archivo_id"):
        return {"archivo_id": p["archivo_id"], "cubre": list(p["cubre"])}
    return {"texto": p.get("texto") or p.get("uri"), "cubre": list(p["cubre"])}


def corregir(ctx, datos: dict, tarea: dict) -> dict:
    """La corrección de una entrega (situación general 3): antes de confirmar, saca piezas de la
    vista previa o cambia lo que cubre lo que escribió, y la vista previa se rehace; después de
    entregada, retira las piezas que la persona saca (se agrega un retiro, nada se borra)."""
    saca = [str(a).strip().upper() for a in datos.get("saca") or []]
    dicho = datos.get("el_texto_cubre")
    base = {"corrige": "entregar", "tarea": {"alias": tarea["alias"], "titulo": tarea["titulo"]}}
    q = abierta(ctx, tarea["id"])
    if q is not None:
        piezas = _piezas_de(q)
        por_alias = {f"P{i}": p for i, p in enumerate(piezas, 1)}
        desconocidas = [a for a in saca if a not in por_alias]
        if desconocidas or (not saca and not isinstance(dicho, list)):
            return {"resultado": "falta_dato", "falta": ["saca"], **base}
        sacadas = [por_alias[a] for a in saca]
        pol = politica(ctx.cur, tarea["id"])
        vistas = mostrar(piezas, pol, ctx.calendario.zona)
        quedan = [p for p in piezas if p not in sacadas]
        if isinstance(dicho, list):
            for p in quedan:
                if p["clase"] == "texto":
                    p["cubre_dicho"] = [str(t) for t in dicho]
        hecho = _mostrar_la_entrega(ctx, _tarea_de(ctx, tarea["id"]), quedan, q)
        return {**hecho, "resultado": "corregido", "como_queda": hecho["resultado"], **base,
                **({"sacadas": [vistas[piezas.index(p)] for p in sacadas]} if sacadas else {})}
    if tarea["estado"] == "en_revision" and saca:
        entregado = _lo_entregado(ctx.cur, tarea["id"])
        por_alias = {f"P{i}": p for i, p in enumerate(entregado, 1)}
        if any(a not in por_alias for a in saca):
            return {"resultado": "falta_dato", "falta": ["saca"], **base}
        pol = politica(ctx.cur, tarea["id"])
        vistas = mostrar(entregado, pol, ctx.calendario.zona)
        retiradas, faltan = [], []
        for a in saca:
            r = ejecutar(ctx.cur, ctx.quien, "retirar_evidencia",
                         {"evidencia_id": por_alias[a]["evidencia_id"],
                          "motivo": (ctx.texto or "").strip() or None}, ya_confirmada=True)
            if not r.get("retirada"):
                return {"resultado": "no_se_puede", "motivo": "ya_aprobada", **base}
            retiradas.append(vistas[entregado.index(por_alias[a])])
            faltan = r.get("faltan") or []
        return {"resultado": "corregido", **base, "retiradas": retiradas,
                **({"le_falta": [pol.en_palabras(t) for t in faltan]} if faltan else {})}
    return {"resultado": "no_se_puede", "motivo": "nada_que_corregir", **base}
