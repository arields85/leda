"""Los efectos que pasan después, como quedaron al terminar el turno (ADR 0018, decisión 9k).

Un mensaje puede traer varias jugadas, y una puede cambiar lo que otra dejó para después: una
fecha contesta la espera de un avance, y el pedido del estado que el avance guardó para el día
hábil siguiente ya no va a salir; una segunda fecha deja atrás el aviso al referente de la
primera; una jugada contesta la pregunta que abrió otra. El hecho de la primera jugada se armó
antes y diría algo que ya no es cierto.

Por eso cada hecho nombra por su id lo que deja para después (`fichas.EFECTOS`: un aviso
guardado, una espera, una pregunta) y, después de todas las jugadas, el turno los vuelve a leer
de la base y pone en el hecho cómo quedó cada uno. Un solo paso para todas las jugadas, sin una
rama por jugada:

- **Un aviso** guardado se mira con la misma regla con que se mira al salir (`avisos.TIPOS`):
  si ya no corresponde, se retira ahora con su motivo (no saldría) y el hecho dice que no le va
  a llegar a quien iba (`llega`: `no_le_va_a_llegar`, con `motivo`); si corresponde, el hecho
  queda como estaba, con cuándo le llega. Si otra jugada ya lo retiró, o si salió o falló, el
  hecho lo dice igual: que no le va a llegar, que ya le llegó o que no le llegó. Siempre lo que
  pasa en el mundo, nunca el estado interno del aviso (usuario, 2026-10-06).
- **Una espera** dice si Leda sigue esperando (`sigue_abierto`), si la persona ya contestó con
  algo cierto (`ya_contesto`) o si ya se escaló.
- **Una pregunta** se nombra como quedó: la que se hace ahora (`pregunta`), una que quedó para
  después, o una que el mismo mensaje ya cerró (`preguntas_ya_cerradas`), que no se hace.

Las ids se sacan del hecho acá: ni la IA ni los hechos registrados ven una.

**Lo anunciado en un turno anterior** (tercera vuelta de ajuste, usuario, 2026-10-06; ronda 2,
conversación 16): lo que un turno dejó anunciado y pendiente (un aviso guardado que sus hechos
nombraron) lo puede dejar atrás un turno siguiente, aunque ninguna de sus jugadas lo nombre: una
fecha contesta la espera y el pedido del estado que anunció el turno de antes ya no sale. Cada
turno guarda aparte, en su resultado registrado (`ANUNCIADOS`, fuera de los hechos), las ids de
lo que quedó anunciado y pendiente; el turno siguiente las vuelve a leer con la misma regla, y lo
que ya no va a pasar lo dice (`YA_NO_VA_A_PASAR`, junto a los hechos) una sola vez: lo que
sigue pendiente pasa al turno siguiente, y lo que ya no, no. La redacción lo cuenta sólo si a
la persona le sirve (usuario, 2026-10-06).

**Lo que sigue** (la misma vuelta: el próximo paso de cada mensaje): el último hecho anotado de
cada tarea de la persona dice lo próximo que Leda hace en su seguimiento, como quedó al terminar
el turno (`LO_QUE_SIGUE`), cuando el código lo sabe: el próximo aviso guardado para la persona
sobre esa tarea, que el seguimiento está detenido mientras siga trabada, o el día en que Leda le
va a pedir el estado. Así la redacción cuenta el próximo paso sin inventarlo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from . import no_interrumpir, preguntas
from .ancla import anclaje
from .avisos import TIPOS, Momento, ausente, leer_tarea, omitir
from .fichas import (AVISO, EFECTOS, ESPERA, LLEGA, NO_LE_LLEGO, NO_LE_VA_A_LLEGAR,
                     OTRAS_PARA_DESPUES, PREGUNTA, YA_LE_LLEGO, Contexto,
                     nombrar_tipo_de_pregunta)

SIGUE_ABIERTO = "sigue_abierto"
YA_CONTESTO = "ya_contesto"
YA_SE_ESCALO = "ya_se_escalo"
PREGUNTAS_YA_CERRADAS = "preguntas_ya_cerradas"
_CLAVES_DE_PREGUNTA = ("pregunta", "pregunta_para_despues", OTRAS_PARA_DESPUES)


# En el resultado registrado del turno, fuera de los hechos: lo anunciado que sigue pendiente.
ANUNCIADOS = "anunciados"
# Junto a los hechos del pedido de redacción: lo anunciado antes que ya no va a pasar.
YA_NO_VA_A_PASAR = "ya_no_va_a_pasar"
# En el último hecho anotado de cada tarea: lo próximo del seguimiento.
LO_QUE_SIGUE = "lo_que_sigue"
DETENIDO_MIENTRAS_SIGA_TRABADA = "detenido_mientras_siga_trabada"
_CERRADAS = ("terminada", "cancelada", "en_revision")


@dataclass
class AlFinal:
    """Lo que el turno guarda y cuenta además de los hechos: lo anunciado antes que ya no va a
    pasar (`ya_no_sale`) y lo que queda anunciado y pendiente al terminar (`anunciados`)."""

    ya_no_sale: list[dict[str, Any]] = field(default_factory=list)
    anunciados: list[dict[str, Any]] = field(default_factory=list)


def al_final_del_turno(ctx: Contexto, hechos: list[dict[str, Any]]) -> AlFinal:
    """Pone en los hechos el estado final de cada efecto que nombran y les saca las ids; vuelve
    a leer lo que el turno anterior dejó anunciado y pendiente; y dice lo que sigue."""
    m = Momento(ctx.cur, ctx.quien.workspace_id, ctx.calendario, ctx.ahora)
    escribe = (str(ctx.quien.membership_id), ctx.ahora)     # su mensaje, todavía sin registrar
    nombrados: set[str] = set()
    pendientes: list[dict[str, Any]] = []
    for arriba in hechos:
        tarea = arriba.get("tarea") if isinstance(arriba, dict) else None
        titulo = tarea.get("titulo") if isinstance(tarea, dict) else None
        for hecho in list(_con_efectos(arriba)):
            efectos = hecho.pop(EFECTOS)
            for efecto in efectos:
                nombrados.add(efecto["id"])
                if efecto["de"] == AVISO:
                    if _aviso(m, hecho, efecto, escribe=escribe):
                        pendientes.append(_anunciado(hecho, efecto, titulo))
                elif efecto["de"] == ESPERA:
                    _espera(m, hecho, efecto)
            de_preguntas = [e for e in efectos if e["de"] == PREGUNTA]
            if de_preguntas:
                _preguntas(ctx, hecho, de_preguntas)
    ya_no_sale, siguen = _lo_anunciado_antes(m, ctx, nombrados)
    _lo_que_sigue(m, ctx, hechos, nombrados)
    return AlFinal(ya_no_sale=ya_no_sale, anunciados=pendientes + siguen)


def _con_efectos(valor: Any):
    """Cada diccionario de los hechos que nombra efectos, a cualquier profundidad."""
    if isinstance(valor, dict):
        if EFECTOS in valor:
            yield valor
        for clave, v in valor.items():
            if clave != EFECTOS:
                yield from _con_efectos(v)
    elif isinstance(valor, (list, tuple)):
        for v in valor:
            yield from _con_efectos(v)


def _aviso(m: Momento, hecho: dict[str, Any], efecto: dict[str, str], *,
           escribe: tuple[str, datetime] | None = None) -> bool:
    """Pone en el hecho el estado final de un aviso que nombra; `True` si sigue guardado
    (anunciado y pendiente). Si quien lo recibe está conversando, cuándo le llega es cuando
    termine su espera (no interrumpir, `no_interrumpir.cuando_sale`)."""
    m.cur.execute("select * from scheduled_notice where id = %s", (efecto["id"],))
    aviso = m.cur.fetchone()
    dicho = hecho.get(efecto["clave"])
    if aviso is None or not isinstance(dicho, dict):
        return False
    estado, motivo = _vigencia(m, aviso)
    if estado == "guardado":
        sale = no_interrumpir.cuando_sale(m.cur, m.cal, m.workspace_id, aviso, escribe=escribe)
        if sale > aviso["programado_para"] and isinstance(dicho.get(LLEGA), str):
            hecho[efecto["clave"]] = {**dicho, LLEGA: sale.astimezone(m.cal.zona).isoformat()}
        return True                 # sigue pendiente: el hecho dice cuándo le llega
    if estado == "omitido":
        hecho[efecto["clave"]] = {**dicho, LLEGA: NO_LE_VA_A_LLEGAR, "motivo": motivo}
    else:
        hecho[efecto["clave"]] = {**dicho,
                                  LLEGA: YA_LE_LLEGO if estado == "enviado" else NO_LE_LLEGO}
    return False


def _vigencia(m: Momento, aviso: dict[str, Any]) -> tuple[str, str | None]:
    """El estado de un aviso en este momento, con su motivo si se retiró: uno guardado que ya
    no corresponde se retira ahora, con la misma regla con que se mira al salir."""
    estado, motivo = aviso["estado"], aviso["motivo_omision"]
    if estado == "guardado":
        tipo = TIPOS.get(aviso["tipo"])
        motivo = tipo.vigente(m, aviso)[0] if tipo is not None else "tipo_sin_declarar"
        if motivo is None:
            return "guardado", None
        omitir(m.cur, str(aviso["id"]), motivo, m.ahora)
        estado = "omitido"
    return estado, motivo


def _anunciado(hecho: dict[str, Any], efecto: dict[str, str],
               titulo: str | None) -> dict[str, Any]:
    """Lo que el turno deja anunciado y pendiente: el aviso (su id), con qué clave lo nombró el
    hecho, de qué tarea y, si va a otra persona, a quién."""
    dicho = hecho.get(efecto["clave"])
    a = dicho.get("a") if isinstance(dicho, dict) else None
    return {"id": efecto["id"], "clave": efecto["clave"],
            **({"tarea": titulo} if titulo else {}), **({"a": a} if a else {})}


def _lo_anunciado_antes(m: Momento, ctx: Contexto, nombrados: set[str]
                        ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Lo que el turno anterior de la persona dejó anunciado y pendiente, mirado de nuevo: lo
    que ya no va a pasar (se retiró sin salir), para decirlo; y lo que sigue pendiente, para
    pasarlo al turno siguiente. Lo que este turno nombra ya lo dicen sus hechos."""
    m.cur.execute("""select resultado -> 'anunciados' as anunciados from conversation_turn
                      where membership_id = %s and sentido = 'entrada'
                        and resultado is not null
                      order by numero desc limit 1""", (ctx.quien.membership_id,))
    fila = m.cur.fetchone()
    ya_no_sale: list[dict[str, Any]] = []
    siguen: list[dict[str, Any]] = []
    for anunciado in (fila["anunciados"] if fila and fila["anunciados"] else []):
        if anunciado["id"] in nombrados:
            continue
        m.cur.execute("select * from scheduled_notice where id = %s", (anunciado["id"],))
        aviso = m.cur.fetchone()
        if aviso is None:
            continue
        estado, motivo = _vigencia(m, aviso)
        if estado == "guardado":
            siguen.append(anunciado)
        elif estado == "omitido":
            ya_no_sale.append({"anuncio": anunciado["clave"],
                               **{k: anunciado[k] for k in ("tarea", "a") if k in anunciado},
                               LLEGA: NO_LE_VA_A_LLEGAR, "motivo": motivo})
    return ya_no_sale, siguen


def _lo_que_sigue(m: Momento, ctx: Contexto, hechos: list[dict[str, Any]],
                  nombrados: set[str]) -> None:
    """En el último hecho anotado de cada tarea de la persona, lo próximo de su seguimiento."""
    vistas: set[str] = set()
    for hecho in reversed(hechos):
        if not isinstance(hecho, dict) or hecho.get("resultado") != "anotado":
            continue
        tarea = hecho.get("tarea")
        alias = tarea.get("alias") if isinstance(tarea, dict) else None
        suya = ctx.suya(alias) if alias else None
        if suya is None or alias in vistas:
            continue
        vistas.add(alias)
        sigue = _que_sigue(m, ctx, suya["id"], nombrados)
        if sigue:
            hecho[LO_QUE_SIGUE] = sigue


def _que_sigue(m: Momento, ctx: Contexto, task_id: str,
               nombrados: set[str]) -> dict[str, Any] | None:
    """Lo próximo que Leda hace en el seguimiento de la tarea, si el código lo sabe: el próximo
    aviso guardado para la persona (si un hecho de este turno ya lo nombra, lo dice ese hecho),
    que no le pide el estado mientras siga trabada, o el día del ancla en que se lo va a pedir.
    `None` si no hay nada que el código sepa."""
    tarea = leer_tarea(m.cur, task_id)
    persona = ctx.quien.membership_id
    if tarea is None or tarea["estado"] in _CERRADAS or ausente(m.cur, persona, m.hoy):
        return None
    m.cur.execute("""select * from scheduled_notice
                      where task_id = %s and destinatario_membership_id = %s
                        and estado = 'guardado'
                      order by programado_para, creado_en""", (task_id, persona))
    for aviso in m.cur.fetchall():
        if str(aviso["id"]) in nombrados:
            return None
        tipo = TIPOS.get(aviso["tipo"])
        if tipo is not None and tipo.vigente(m, aviso)[0] is None:
            # Le llega cuando termine de conversar (no interrumpir), si es más tarde.
            sale = no_interrumpir.cuando_sale(m.cur, m.cal, m.workspace_id, aviso,
                                              escribe=(persona, m.ahora))
            return {"proximo_aviso": {
                "aviso": aviso["tipo"], LLEGA: sale.astimezone(m.cal.zona).isoformat()}}
    if tarea["bloqueada"] or tarea["estado"] == "bloqueada":
        return {"seguimiento": DETENIDO_MIENTRAS_SIGA_TRABADA}
    if tarea["fecha_objetivo"] is None:
        return None
    de = anclaje(m.cur, task_id, m.fecha(tarea["fecha_objetivo"]))
    if m.hoy < de.fecha:
        return {"pide_el_estado_el": {"fecha": de.fecha.isoformat()}}
    return None


def _espera(m: Momento, hecho: dict[str, Any], efecto: dict[str, str]) -> None:
    m.cur.execute("select satisfecho_en, escalado_en from pending_reply where id = %s",
                  (efecto["id"],))
    espera = m.cur.fetchone()
    if espera is None:
        return
    hecho[efecto["clave"]] = (YA_CONTESTO if espera["satisfecho_en"] is not None
                              else YA_SE_ESCALO if espera["escalado_en"] is not None
                              else SIGUE_ABIERTO)


def _preguntas(ctx: Contexto, hecho: dict[str, Any], efectos: list[dict[str, str]]) -> None:
    """Las preguntas que el hecho abrió, nombradas otra vez como quedaron."""
    for clave in _CLAVES_DE_PREGUNTA:
        hecho.pop(clave, None)
    abierta = preguntas.actual(ctx.cur, ctx.quien.membership_id)
    cerradas: list[str] = []
    for pregunta_id in dict.fromkeys(e["id"] for e in efectos):
        ctx.cur.execute("select tipo, cerrada_en from conversation_question where id = %s",
                        (pregunta_id,))
        q = ctx.cur.fetchone()
        if q is None:
            continue
        if q["cerrada_en"] is not None:
            if q["tipo"] not in cerradas:
                cerradas.append(q["tipo"])
            continue
        ahora = abierta is not None and str(abierta["id"]) == pregunta_id
        nombrar_tipo_de_pregunta(hecho, "pregunta" if ahora else "pregunta_para_despues",
                                 q["tipo"])
    if cerradas:
        hecho[PREGUNTAS_YA_CERRADAS] = cerradas
