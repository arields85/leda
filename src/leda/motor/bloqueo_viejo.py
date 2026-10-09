"""El bloqueo viejo (C-5, porción 5; C-5a).

Decisión 7 del usuario (`odd/tasks/fase-c.md`, 2026-10-08, opción A): a los
`bloqueos.escala_solo_a_los_dias` días hábiles (5 en CoreWork, ajustable desde la plataforma,
`docs/product/plataforma-pendientes.md`) Leda le informa al referente aunque la cadena se mueva,
con la historia y las fechas dichas: "el silencio y no informar es peor que avisos informativos
útiles". Mecánica §8: "un bloqueo tiene antigüedad y esa antigüedad es visible. Un bloqueo abierto
hace más de [pack] días escala aunque nadie lo pida". Conversación 36. Con las decisiones 34, 35 y
36 del usuario (2026-10-09): se le cuenta a la persona trabada, con la forma de "quedó asentado"
(`asentado.py`), y se vuelve a asentar mientras siga.

**Cuándo** (`informar_los_viejos`, una pasada de la escalera, `escalera.correr_escalera`): un
bloqueo abierto, de una tarea sin cerrar, que lleva esos días hábiles del espacio desde que se
anotó o, si ya se asentó antes, desde la vez anterior (decisión 36), contados en su calendario
laboral. Los días salen del espacio (`workspace_setting` `bloqueos`, que importa el pack); si no
están o no son un número entero de días, 1 o más, vale el del producto, 5 (`DIAS_POR_OMISION`).

**Cada vez, una sola:** la clave del aviso nombra el bloqueo y la vez (la primera, sin número, como
antes de la decisión 36; `clave`). La vez anterior es la última que se resolvió (salió o se omitió):
una que todavía no salió (la persona estaba ausente, el ciclo parado) sale con los hechos de su
momento y no se guarda otra encima. Al salir la primera queda registrado a quién y cuándo se
informó (`blocker.escalado_a` y `escalado_en`); cada vez, con su fila de auditoría. Sale a la hora
en que Leda manda lo suyo, dentro del horario y sin interrumpir una conversación (decisión 13),
como todo aviso.

**A quién** (`a_quien`): al referente del sector de la tarea trabada; si es la persona trabada
misma, a quien aprueba su trabajo (la misma regla que la cadena de la porción 3,
`persecucion.a_quien_informar`). Se relee al salir (`TipoDeAviso.va_a`). Sin nadie, nada se
guarda: ni al referente ni a la persona trabada (nada queda asentado).

**Qué lleva** (`hechos_del_bloqueo`): la tarea, quién la tiene, lo que la traba, desde cuándo y
cuántos días hábiles lleva, y la historia entera (`historia`): quién dijo quién la destraba y lo
que dijo cada uno, con sus fechas (`blocker_unblocker` y `dicho_de_quien_destraba`), en el orden
en que pasó. Las veces siguientes, en lugar de la historia entera, el día de la vez anterior
(`la_vez_anterior`) y lo que se dijo desde entonces (`desde_la_vez_anterior`, vacío si nada). Es
información: no le pide nada. Es seguimiento que Leda hace por su cuenta (no lo causa el acto de
otra persona): cuenta para el tope diario y sale en un envío por persona (mecánica §10).

**A la persona trabada** (decisión 34; `ASENTADO_QUE_SIGUE_TRABADA`), a la vez y cada vez: un
mensaje corto, informativo, de que quedó asentado que su tarea sigue trabada, cuántos días hábiles
lleva y, sólo si el espacio tiene informe al grupo, que figura ahí (`queda_asentado`, decisión
35). A quién le llegó va en el hecho y la redacción lo dice sólo si la persona lo pregunta
(`hechos.NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO`). También seguimiento que Leda hace por su cuenta.

Al salir se vuelve a mirar (`vigencia`, `vigencia_de_lo_asentado`): si el bloqueo ya se cerró o
la tarea se cerró, no sale; lo de la persona trabada tampoco si lo de esa vez al referente se
omitió (entonces nada quedó asentado) o si la tarea cambió de responsable.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .asentado import QUEDA_ASENTADO, queda_asentado
from .auditoria import auditar
from .avisos import (ASENTADO_QUE_SIGUE_TRABADA, BLOQUEO_QUE_SIGUE_ABIERTO, YA_SE_DESTRABO,
                     Momento, de_la_clave, guardar, integrante, leer_tarea)
from .persecucion import SIN_REFERENTE, a_quien_informar
from .tiempo import sale

CLAVE = "bloqueos"
DIAS = "escala_solo_a_los_dias"
DIAS_POR_OMISION = 5
CAMBIO_EL_RESPONSABLE = "cambio_el_responsable"


def dias_del_bloqueo_viejo(cur, workspace_id: str) -> int:
    """A los cuántos días hábiles se informa un bloqueo abierto: los del espacio o, si no son un
    número entero de días, 1 o más, los del producto."""
    cur.execute("select valor from workspace_setting where workspace_id = %s and clave = %s",
                (workspace_id, CLAVE))
    fila = cur.fetchone()
    valor = fila["valor"].get(DIAS) if fila and isinstance(fila["valor"], dict) else None
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 1:
        return DIAS_POR_OMISION
    return valor


def clave(task_id, bloqueo_id, vez: int = 1, tipo: str = BLOQUEO_QUE_SIGUE_ABIERTO) -> str:
    """La clave del aviso de esa vez: la primera, sin número (como antes de la decisión 36)."""
    base = f"motor:{tipo}:{task_id}:b{bloqueo_id}"
    return base if vez == 1 else f"{base}:{vez}"


def a_quien(cur, tarea: dict[str, Any]) -> dict[str, Any] | None:
    """Al referente del sector de la tarea; si es la persona trabada, a quien aprueba su
    trabajo. `None` si no hay nadie."""
    return a_quien_informar(cur, {"responsable_membership_id": tarea["responsable_membership_id"],
                                  "area_id": tarea["area_id"]}, None)


def _veces(cur, workspace_id: str, task_id, bloqueo_id) -> list[dict[str, Any]]:
    """Las veces que ya se guardó el aviso al referente de este bloqueo, en orden."""
    base = clave(task_id, bloqueo_id)
    cur.execute("""select id, estado, resuelto_en from scheduled_notice
                    where workspace_id = %s and tipo = %s and task_id = %s
                      and (dedupe_key = %s or starts_with(dedupe_key, %s))
                    order by creado_en, dedupe_key""",
                (workspace_id, BLOQUEO_QUE_SIGUE_ABIERTO, str(task_id), base, base + ":"))
    return cur.fetchall()


def informar_los_viejos(m: Momento) -> int:
    """Guarda el aviso de cada bloqueo abierto que llegó a sus días hábiles desde que se anotó o
    desde la vez anterior, y el de la persona trabada. Cuántos bloqueos asentó."""
    cur = m.cur
    dias = dias_del_bloqueo_viejo(cur, m.workspace_id)
    cur.execute("""select b.id, b.task_id, b.abierto_en from blocker b
                     join task t on t.id = b.task_id
                    where b.workspace_id = %s and b.resuelto_en is null
                      and t.estado not in ('terminada', 'cancelada')
                    order by b.abierto_en, b.id""", (m.workspace_id,))
    # El filtro por espacio se suma al RLS forzado de `blocker` y `task`: dos defensas.
    guardados = 0
    for b in cur.fetchall():
        veces = _veces(cur, m.workspace_id, b["task_id"], b["id"])
        if any(v["estado"] == "guardado" for v in veces):
            continue                    # la vez anterior todavía no salió
        desde = max((v["resuelto_en"] for v in veces if v["resuelto_en"] is not None),
                    default=b["abierto_en"])
        if m.cal.habiles_entre(desde, m.ahora) < dias:
            continue
        tarea = leer_tarea(cur, b["task_id"])
        destino = a_quien(cur, tarea) if tarea is not None else None
        if destino is None:
            continue
        vez, cuando = len(veces) + 1, sale(m.cal, m.ahora)
        bloqueo_id = str(b["id"])
        guardar(cur, m.workspace_id, BLOQUEO_QUE_SIGUE_ABIERTO, task_id=str(b["task_id"]),
                destinatario=str(destino["membership_id"]),
                hechos=hechos_del_bloqueo(m, bloqueo_id), programado_para=cuando,
                clave=clave(b["task_id"], b["id"], vez), ahora=m.ahora)
        guardar(cur, m.workspace_id, ASENTADO_QUE_SIGUE_TRABADA, task_id=str(b["task_id"]),
                destinatario=str(tarea["responsable_membership_id"]),
                hechos=hechos_de_lo_asentado(m, bloqueo_id, destino["nombre"]),
                programado_para=cuando,
                clave=clave(b["task_id"], b["id"], vez, ASENTADO_QUE_SIGUE_TRABADA),
                ahora=m.ahora)
        guardados += 1
    return guardados


def _el_bloqueo(cur, bloqueo_id: str) -> dict[str, Any]:
    cur.execute("""select b.task_id, b.causa, b.abierto_en, t.titulo, i.nombre as responsable
                     from blocker b join task t on t.id = b.task_id
                     join integrante i on i.membership_id = t.responsable_membership_id
                    where b.id = %s""", (bloqueo_id,))
    return cur.fetchone()


def _la_vez_anterior(m: Momento, task_id, bloqueo_id: str) -> datetime | None:
    """Cuándo salió la última vez que se le contó al referente, si salió alguna."""
    return max((v["resuelto_en"] for v in _veces(m.cur, m.workspace_id, task_id, bloqueo_id)
                if v["estado"] == "enviado"), default=None)


def hechos_del_bloqueo(m: Momento, bloqueo_id: str) -> dict[str, Any]:
    """Lo que lleva el aviso: la tarea, quién la tiene, lo que la traba, desde cuándo, cuántos
    días hábiles lleva y la historia; si ya se le contó, lo que pasó desde la vez anterior."""
    b = _el_bloqueo(m.cur, bloqueo_id)
    hechos = {"aviso": BLOQUEO_QUE_SIGUE_ABIERTO, "necesita_respuesta": False,
              "tarea": b["titulo"], "responsable": b["responsable"], "causa": b["causa"],
              "trabada_desde": m.fecha(b["abierto_en"]).isoformat(),
              "dias_habiles_trabada": m.cal.habiles_entre(b["abierto_en"], m.ahora)}
    anterior = _la_vez_anterior(m, b["task_id"], bloqueo_id)
    if anterior is None:
        hechos["historia"] = historia(m, bloqueo_id)
    else:
        hechos["la_vez_anterior"] = m.fecha(anterior).isoformat()
        hechos["desde_la_vez_anterior"] = historia(m, bloqueo_id, desde=anterior)
    return hechos


def hechos_de_lo_asentado(m: Momento, bloqueo_id: str, a: str) -> dict[str, Any]:
    """Lo que le llega a la persona trabada: la tarea, lo que la traba, desde cuándo, cuántos
    días hábiles lleva y que quedó asentado (a quién, sólo si lo pregunta)."""
    b = _el_bloqueo(m.cur, bloqueo_id)
    return {"aviso": ASENTADO_QUE_SIGUE_TRABADA, "necesita_respuesta": False,
            "tarea": b["titulo"], "causa": b["causa"],
            "trabada_desde": m.fecha(b["abierto_en"]).isoformat(),
            "dias_habiles_trabada": m.cal.habiles_entre(b["abierto_en"], m.ahora),
            QUEDA_ASENTADO: queda_asentado(m.cur, m.workspace_id, a)}


def historia(m: Momento, bloqueo_id: str, desde: datetime | None = None) -> list[dict[str, Any]]:
    """Lo que se dijo del bloqueo, en el orden en que pasó, cada cosa con su día (`el`) y quién
    la dijo (`de`): a quién le toca destrabarlo, según quien lo dijo, y lo que dijo quien lo
    destraba (para cuándo, que ya está, que no le corresponde, con qué está trabado o sus
    palabras). `desde`: sólo lo dicho después."""
    cur = m.cur
    cur.execute("""select u.at, u.id, u.destraba_membership_id, u.destraba_externo, u.no_sabe,
                          u.dicho_por_membership_id, d.nombre as destraba, p.nombre as de
                     from blocker_unblocker u
                     left join integrante d on d.membership_id = u.destraba_membership_id
                     join integrante p on p.membership_id = u.dicho_por_membership_id
                    where u.blocker_id = %s
                      and (%s::timestamptz is null or u.at > %s::timestamptz)""",
                (bloqueo_id, desde, desde))
    eventos: list[tuple[Any, int, str, dict[str, Any]]] = []
    for u in cur.fetchall():
        e: dict[str, Any] = {"el": m.fecha(u["at"]).isoformat(), "de": u["de"]}
        if u["no_sabe"]:
            e["no_sabe"] = True
        elif u["destraba_membership_id"] == u["dicho_por_membership_id"]:
            e["nadie_mas"] = True
        else:
            e["le_toca_a"] = u["destraba"] or u["destraba_externo"]
        eventos.append((u["at"], 0, str(u["id"]), e))
    cur.execute("""select d.at, d.id, d.para_cuando, d.ya_esta, d.lo_que_dice,
                          d.no_le_corresponde, p.nombre as de, y.causa as su_causa,
                          t.titulo as su_tarea
                     from dicho_de_quien_destraba d
                     join blocker_unblocker u on u.id = d.blocker_unblocker_id
                     join integrante p on p.membership_id = d.dicho_por_membership_id
                     left join blocker y on y.id = d.espera_su_bloqueo_id
                     left join task t on t.id = y.task_id
                    where u.blocker_id = %s
                      and (%s::timestamptz is null or d.at > %s::timestamptz)""",
                (bloqueo_id, desde, desde))
    for d in cur.fetchall():
        e = {"el": m.fecha(d["at"]).isoformat(), "de": d["de"]}
        if d["no_le_corresponde"]:
            e["no_le_corresponde"] = True
        if d["para_cuando"] is not None:
            e["para_cuando"] = d["para_cuando"].isoformat()
        if d["ya_esta"]:
            e["ya_esta"] = True
        if d["su_tarea"] is not None:
            e["su_tarea_trabada"] = {"tarea": d["su_tarea"], "causa": d["su_causa"]}
        if d["lo_que_dice"]:
            e["lo_que_dice"] = d["lo_que_dice"]
        eventos.append((d["at"], 1, str(d["id"]), e))
    return [e for *_orden, e in sorted(eventos, key=lambda x: x[:3])]


# --- Al salir ---------------------------------------------------------------------------------

def _sigue_abierto(m: Momento, aviso: dict[str, Any]
                   ) -> tuple[str | None, dict[str, Any] | None]:
    """Si el bloqueo del aviso sigue abierto y su tarea sin cerrar: el motivo para omitirlo, o
    `None` y la tarea."""
    tarea = leer_tarea(m.cur, aviso["task_id"])
    if tarea is None:
        return "tarea_inexistente", None
    if tarea["estado"] in ("terminada", "cancelada"):
        return "tarea_cerrada", None
    m.cur.execute("select resuelto_en from blocker where id = %s", (de_la_clave(aviso),))
    bloqueo = m.cur.fetchone()
    if bloqueo is None:
        return "tarea_inexistente", None
    if bloqueo["resuelto_en"] is not None:
        return YA_SE_DESTRABO, None
    return None, tarea


def vigencia(m: Momento, aviso: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    """Sale si el bloqueo sigue abierto y la tarea sin cerrar, con los hechos de este momento."""
    motivo, _tarea = _sigue_abierto(m, aviso)
    if motivo is not None:
        return motivo, {}
    return None, hechos_del_bloqueo(m, de_la_clave(aviso))


def vigencia_de_lo_asentado(m: Momento, aviso: dict[str, Any]
                            ) -> tuple[str | None, dict[str, Any]]:
    """Lo de la persona trabada sale si el bloqueo sigue abierto, la tarea sin cerrar y con el
    mismo responsable, y lo de esa vez al referente no se omitió: nada se dice asentado si no
    quedó asentado."""
    motivo, tarea = _sigue_abierto(m, aviso)
    if motivo is not None:
        return motivo, {}
    if str(tarea["responsable_membership_id"]) != str(aviso["destinatario_membership_id"]):
        return CAMBIO_EL_RESPONSABLE, {}
    al_referente = aviso["dedupe_key"].replace(ASENTADO_QUE_SIGUE_TRABADA,
                                               BLOQUEO_QUE_SIGUE_ABIERTO, 1)
    m.cur.execute("""select estado, motivo_omision from scheduled_notice
                      where workspace_id = %s and dedupe_key = %s""",
                  (m.workspace_id, al_referente))
    suyo = m.cur.fetchone()
    if suyo is not None and suyo["estado"] == "omitido":
        return suyo["motivo_omision"], {}
    destino = a_quien(m.cur, tarea)
    if destino is None:
        return SIN_REFERENTE, {}
    return None, hechos_de_lo_asentado(m, de_la_clave(aviso), destino["nombre"])


def va_a(m: Momento, aviso: dict[str, Any]) -> str | None:
    """A quién va al salir, releído."""
    tarea = leer_tarea(m.cur, aviso["task_id"])
    destino = a_quien(m.cur, tarea) if tarea is not None else None
    return str(destino["membership_id"]) if destino is not None else None


def al_salir(m: Momento, aviso: dict[str, Any]) -> None:
    """Queda registrado que el bloqueo se informó, a quién y cuándo (mecánica §8; constitución
    §12): la primera vez en el bloqueo mismo, y cada vez en la auditoría."""
    bloqueo_id = de_la_clave(aviso)
    a = str(aviso["destinatario_membership_id"])
    m.cur.execute("""update blocker set escalado_a = %s, escalado_en = %s
                      where id = %s and escalado_en is null""", (a, m.ahora, bloqueo_id))
    persona = integrante(m.cur, a)
    auditar(m.cur, accion="informar_bloqueo_que_sigue_abierto", workspace_id=m.workspace_id,
            sujeto_tipo="blocker", sujeto_id=bloqueo_id,
            detalle={"aviso_id": str(aviso["id"]), "task_id": str(aviso["task_id"]),
                     "a_membership_id": a, "a": persona["nombre"] if persona else None,
                     "dias_habiles_trabada": (aviso["hechos"] or {}).get("dias_habiles_trabada"),
                     "vez": _vez(aviso), "at": m.ahora.isoformat()})


def _vez(aviso: dict[str, Any]) -> int:
    """Qué vez es, por su clave (`clave`)."""
    partes = aviso["dedupe_key"].split(":")
    return int(partes[4]) if len(partes) > 4 else 1
