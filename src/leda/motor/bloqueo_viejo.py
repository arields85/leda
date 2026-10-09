"""El bloqueo viejo (C-5, porción 5).

Decisión 7 del usuario (`odd/tasks/fase-c.md`, 2026-10-08, opción A): a los
`bloqueos.escala_solo_a_los_dias` días hábiles (5 en CoreWork, ajustable desde la plataforma,
`docs/product/plataforma-pendientes.md`) Leda le informa al referente aunque la cadena se mueva,
con la historia y las fechas dichas: "el silencio y no informar es peor que avisos informativos
útiles". Mecánica §8: "un bloqueo tiene antigüedad y esa antigüedad es visible. Un bloqueo abierto
hace más de [pack] días escala aunque nadie lo pida". Conversación 36.

**Cuándo** (`informar_los_viejos`, una pasada de la escalera, `escalera.correr_escalera`): un
bloqueo abierto, de una tarea sin cerrar, que lleva esos días hábiles del espacio desde que se
anotó, contados en su calendario laboral. Los días salen del espacio (`workspace_setting`
`bloqueos`, que importa el pack); si no están o no son un número entero de días, 1 o más, vale
el del producto, 5 (`DIAS_POR_OMISION`).

**Una sola vez por bloqueo:** la clave del aviso nombra el bloqueo, y al salir queda registrado
a quién y cuándo se informó (`blocker.escalado_a` y `escalado_en`, con su fila de auditoría):
un bloqueo ya informado no se vuelve a mirar. Sale a la hora en que Leda manda lo suyo, dentro
del horario y sin interrumpir una conversación (decisión 13), como todo aviso.

**A quién** (`a_quien`): al referente del sector de la tarea trabada; si es la persona trabada
misma, a quien aprueba su trabajo (la misma regla que la cadena de la porción 3,
`persecucion.a_quien_informar`). Se relee al salir (`TipoDeAviso.va_a`). Sin nadie, nada se
guarda.

**Qué lleva** (`hechos_del_bloqueo`): la tarea, quién la tiene, lo que la traba, desde cuándo y
cuántos días hábiles lleva, y la historia entera (`historia`): quién dijo quién la destraba y lo
que dijo cada uno, con sus fechas (`blocker_unblocker` y `dicho_de_quien_destraba`), en el orden
en que pasó. Es información: no le pide nada. Es seguimiento que Leda hace por su cuenta (no lo
causa el acto de otra persona): cuenta para el tope diario y sale en un envío por persona
(mecánica §10). A la persona trabada no le llega nada por esto.

Al salir se vuelve a mirar (`vigencia`): si el bloqueo ya se cerró o la tarea se cerró, no sale.
"""

from __future__ import annotations

from typing import Any

from .auditoria import auditar
from .avisos import (BLOQUEO_QUE_SIGUE_ABIERTO, YA_SE_DESTRABO, Momento, de_la_clave, guardar,
                     integrante, leer_tarea)
from .persecucion import a_quien_informar
from .tiempo import sale

CLAVE = "bloqueos"
DIAS = "escala_solo_a_los_dias"
DIAS_POR_OMISION = 5


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


def clave(task_id, bloqueo_id) -> str:
    return f"motor:{BLOQUEO_QUE_SIGUE_ABIERTO}:{task_id}:b{bloqueo_id}"


def a_quien(cur, tarea: dict[str, Any]) -> dict[str, Any] | None:
    """Al referente del sector de la tarea; si es la persona trabada, a quien aprueba su
    trabajo. `None` si no hay nadie."""
    return a_quien_informar(cur, {"responsable_membership_id": tarea["responsable_membership_id"],
                                  "area_id": tarea["area_id"]}, None)


def informar_los_viejos(m: Momento) -> int:
    """Guarda el aviso de cada bloqueo abierto que llegó a sus días hábiles y no se informó.
    Cuántos guardó."""
    cur = m.cur
    dias = dias_del_bloqueo_viejo(cur, m.workspace_id)
    cur.execute("""select b.id, b.task_id, b.abierto_en from blocker b
                     join task t on t.id = b.task_id
                    where b.workspace_id = %s
                      and b.resuelto_en is null and b.escalado_en is null
                      and t.estado not in ('terminada', 'cancelada')
                    order by b.abierto_en, b.id""", (m.workspace_id,))
    # El filtro por espacio se suma al RLS forzado de `blocker` y `task`: dos defensas.
    guardados = 0
    for b in cur.fetchall():
        if m.cal.habiles_entre(b["abierto_en"], m.ahora) < dias:
            continue
        la_clave = clave(b["task_id"], b["id"])
        cur.execute("select 1 from scheduled_notice where workspace_id = %s and dedupe_key = %s",
                    (m.workspace_id, la_clave))
        if cur.fetchone() is not None:
            continue                    # una sola vez por bloqueo
        tarea = leer_tarea(cur, b["task_id"])
        destino = a_quien(cur, tarea) if tarea is not None else None
        if destino is None:
            continue
        guardar(cur, m.workspace_id, BLOQUEO_QUE_SIGUE_ABIERTO, task_id=str(b["task_id"]),
                destinatario=str(destino["membership_id"]),
                hechos=hechos_del_bloqueo(m, str(b["id"])), programado_para=sale(m.cal, m.ahora),
                clave=la_clave, ahora=m.ahora)
        guardados += 1
    return guardados


def hechos_del_bloqueo(m: Momento, bloqueo_id: str) -> dict[str, Any]:
    """Lo que lleva el aviso: la tarea, quién la tiene, lo que la traba, desde cuándo, cuántos
    días hábiles lleva y la historia."""
    cur = m.cur
    cur.execute("""select b.causa, b.abierto_en, t.titulo, i.nombre as responsable
                     from blocker b join task t on t.id = b.task_id
                     join integrante i on i.membership_id = t.responsable_membership_id
                    where b.id = %s""", (bloqueo_id,))
    b = cur.fetchone()
    return {"aviso": BLOQUEO_QUE_SIGUE_ABIERTO, "necesita_respuesta": False,
            "tarea": b["titulo"], "responsable": b["responsable"], "causa": b["causa"],
            "trabada_desde": m.fecha(b["abierto_en"]).isoformat(),
            "dias_habiles_trabada": m.cal.habiles_entre(b["abierto_en"], m.ahora),
            "historia": historia(m, bloqueo_id)}


def historia(m: Momento, bloqueo_id: str) -> list[dict[str, Any]]:
    """Lo que se dijo del bloqueo, en el orden en que pasó, cada cosa con su día (`el`) y quién
    la dijo (`de`): a quién le toca destrabarlo, según quien lo dijo, y lo que dijo quien lo
    destraba (para cuándo, que ya está, que no le corresponde, con qué está trabado o sus
    palabras)."""
    cur = m.cur
    cur.execute("""select u.at, u.id, u.destraba_membership_id, u.destraba_externo, u.no_sabe,
                          u.dicho_por_membership_id, d.nombre as destraba, p.nombre as de
                     from blocker_unblocker u
                     left join integrante d on d.membership_id = u.destraba_membership_id
                     join integrante p on p.membership_id = u.dicho_por_membership_id
                    where u.blocker_id = %s""", (bloqueo_id,))
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
                    where u.blocker_id = %s""", (bloqueo_id,))
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

def vigencia(m: Momento, aviso: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    """Sale si el bloqueo sigue abierto y la tarea sin cerrar, con los hechos de este momento."""
    tarea = leer_tarea(m.cur, aviso["task_id"])
    if tarea is None:
        return "tarea_inexistente", {}
    if tarea["estado"] in ("terminada", "cancelada"):
        return "tarea_cerrada", {}
    m.cur.execute("select resuelto_en from blocker where id = %s", (de_la_clave(aviso),))
    bloqueo = m.cur.fetchone()
    if bloqueo is None:
        return "tarea_inexistente", {}
    if bloqueo["resuelto_en"] is not None:
        return YA_SE_DESTRABO, {}
    return None, hechos_del_bloqueo(m, de_la_clave(aviso))


def va_a(m: Momento, aviso: dict[str, Any]) -> str | None:
    """A quién va al salir, releído."""
    tarea = leer_tarea(m.cur, aviso["task_id"])
    destino = a_quien(m.cur, tarea) if tarea is not None else None
    return str(destino["membership_id"]) if destino is not None else None


def al_salir(m: Momento, aviso: dict[str, Any]) -> None:
    """Queda registrado que el bloqueo se informó, a quién y cuándo (mecánica §8; constitución
    §12): ya no se vuelve a mirar."""
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
                     "at": m.ahora.isoformat()})
