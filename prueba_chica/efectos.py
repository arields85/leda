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
  si ya no corresponde, se retira ahora con su motivo (no saldría) y el hecho lo dice
  (`retirado_sin_enviar` y `motivo`, sin `sale`); si corresponde, el hecho queda como estaba. Uno
  que otra jugada ya retiró, salió o falló, con su estado.
- **Una espera** dice si Leda sigue esperando (`sigue_abierto`), si la persona ya contestó con
  algo cierto (`ya_contesto`) o si ya se escaló.
- **Una pregunta** se nombra como quedó: la que se hace ahora (`pregunta`), una que quedó para
  después, o una que el mismo mensaje ya cerró (`preguntas_ya_cerradas`), que no se hace.

Las ids se sacan del hecho acá: ni la IA ni el registro de turnos ven una.
"""

from __future__ import annotations

from typing import Any

from . import preguntas
from .avisos import ENVIADO, NO_SALIO, TIPOS, Momento, omitir
from .fichas import (AVISO, EFECTOS, ESPERA, OTRAS_PARA_DESPUES, PREGUNTA, Contexto,
                     nombrar_tipo_de_pregunta)

RETIRADO_SIN_ENVIAR = "retirado_sin_enviar"
SIGUE_ABIERTO = "sigue_abierto"
YA_CONTESTO = "ya_contesto"
YA_SE_ESCALO = "ya_se_escalo"
PREGUNTAS_YA_CERRADAS = "preguntas_ya_cerradas"
_CLAVES_DE_PREGUNTA = ("pregunta", "pregunta_para_despues", OTRAS_PARA_DESPUES)


def al_final_del_turno(ctx: Contexto, hechos: list[dict[str, Any]]) -> None:
    """Pone en los hechos el estado final de cada efecto que nombran y les saca las ids."""
    m = Momento(ctx.cur, ctx.quien.workspace_id, ctx.calendario, ctx.ahora)
    for hecho in list(_con_efectos(hechos)):
        efectos = hecho.pop(EFECTOS)
        for efecto in efectos:
            if efecto["de"] == AVISO:
                _aviso(m, hecho, efecto)
            elif efecto["de"] == ESPERA:
                _espera(m, hecho, efecto)
        de_preguntas = [e for e in efectos if e["de"] == PREGUNTA]
        if de_preguntas:
            _preguntas(ctx, hecho, de_preguntas)


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


def _aviso(m: Momento, hecho: dict[str, Any], efecto: dict[str, str]) -> None:
    m.cur.execute("select * from scheduled_notice where id = %s", (efecto["id"],))
    aviso = m.cur.fetchone()
    dicho = hecho.get(efecto["clave"])
    if aviso is None or not isinstance(dicho, dict):
        return
    estado, motivo = aviso["estado"], aviso["motivo_omision"]
    if estado == "guardado":
        tipo = TIPOS.get(aviso["tipo"])
        motivo = tipo.vigente(m, aviso)[0] if tipo is not None else "tipo_sin_declarar"
        if motivo is None:
            return                  # sigue guardado: el hecho ya dice su estado y cuándo sale
        omitir(m.cur, efecto["id"], motivo, m.ahora)
        estado = "omitido"
    sin_sale = {k: v for k, v in dicho.items() if k != "sale"}
    if estado == "omitido":
        hecho[efecto["clave"]] = {**sin_sale, "estado": RETIRADO_SIN_ENVIAR, "motivo": motivo}
    else:
        hecho[efecto["clave"]] = {**sin_sale,
                                  "estado": ENVIADO if estado == "enviado" else NO_SALIO}


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
