"""Los avisos de la carga desde la web y de lo pedido a otra área (porción J4b de
`odd/tasks/plataforma-jerarquias.md`; ADR 0023, decisión 3; decisiones del usuario del 2026-10-14
D1b, D4, D6, D7, D8, D9 y D14; mecánica §9, §10 y §12).

Cuando Dirección, un referente o la administración cargan una tarea por la web
(`web_app._cargar`, en la misma transacción que la carga), se guardan dos avisos de coordinación
del motor: los causa el acto de otra persona, así que no cuentan para el tope diario (mecánica
§10), salen sólo dentro del horario del espacio (fuera de él, al empezar el siguiente:
`avisos.enviar_avisos`) y los redacta la IA desde los hechos de la cocina, como todos.

- **A quien la hace** (`TAREAS_NUEVAS`, D6), si no se la cargó él mismo: un solo mensaje con todas
  las tareas que le cargaron seguidas, unos minutos después de la última (`VENTANA`): cada carga
  nueva para la misma persona se suma al aviso que todavía no salió y lo corre. De cada tarea, quién
  la cargó (o que la cargó la administración, y quién la decidió), para cuándo, de qué objetivo y
  quién la revisa. Si es un pedido de otra área (D14), quién la pide, desde qué área y a cuál (la de
  quien la recibe), y que quien la recibe decide quién la hace; si es un pedido a Dirección (D1b),
  quién la pide. Un pedido se cuenta como pedido, sin "la cargó" de quien lo pide. Lleva el botón
  que abre su web (ADR 0024: "Ver la tarea", o "Ver mis tareas" si son varias), con la dirección
  pública configurada.
- **A quien la revisa** (`TAREAS_NUEVAS_PARA_REVISAR`, D7), sólo si quien la carga no es quien la
  revisa ni quien la hace: por ejemplo, Ismael le carga a Nahuel y deja a Marcos revisándola. Con
  el mismo margen y la misma suma.
- **Dirección no recibe nada** de lo que un referente se carga a sí mismo o le carga a su gente
  (D4, D8): sólo le llega lo que hace o revisa.
- **Sin Leda conectada** (D9): la vista previa ya lo dice antes de confirmar; al cargar, la
  administración recibe el aviso para conectarla (el mismo incidente que
  `persecucion.avisar_para_que_lo_conecte`, uno por persona y por día), y el aviso a esa persona
  espera (`TipoDeAviso.espera_que_se_conecte`): cuando se conecta, después de la bienvenida, le
  llegan sus tareas juntas en un mensaje.

Al salir, cada aviso se relee: sólo van las tareas que siguen abiertas y siguen siendo de esa
persona (o revisadas por ella); si no queda ninguna, se omite con su motivo.

**Lo pedido a otra área** (D14, pasos 4 a 6; D1b), una vuelta del ciclo del motor
(`avisar_lo_de_los_pedidos`, en `ciclo.py`):

- Cuando una tarea pedida queda terminada (`LO_PEDIDO_TERMINO`), le llega a quien la pidió (salvo
  que la haya aprobado él mismo, como en un pedido a Dirección, D1b) y a quien tenga una tarea
  abierta que la esperaba, con si ya puede seguir. Cada cierre es otro aviso, reconocido por la
  aprobación que lo cerró: si se reabre y se vuelve a aprobar, llega otra vez.
- Cuando quien la pidió la reabre (`LO_PEDIDO_SE_REABRIO`), le llega al referente del área de la
  tarea, que la recibe de vuelta, con el motivo como lo escribió y que decide quién la retoma.

Lo que se guarda en cada aviso son referencias internas (`REFERENCIAS`, que la IA nunca recibe);
los hechos se arman al salir.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import psycopg

from ..db import espacio
from ..incidentes import registrar_incidente_y_si_se_aviso
from .avisos import (LO_PEDIDO_SE_REABRIO, LO_PEDIDO_TERMINO, TAREAS_NUEVAS,
                     TAREAS_NUEVAS_PARA_REVISAR, Momento, es_de_direccion, guardar, integrante,
                     omitir)
from .tiempo import Reloj

# El margen después de la última carga para la misma persona (D6: "unos 10 minutos").
VENTANA = timedelta(minutes=10)

# Los tipos de aviso, declarados en `avisos.TIPOS`.

# Las claves de los hechos (sus significados, en `hechos.SIGNIFICADOS`).
TAREAS_QUE_LE_CARGARON = "tareas_que_le_cargaron"
TAREAS_QUE_VA_A_REVISAR = "tareas_que_va_a_revisar"
LA_CARGO = "la_cargo"
LA_ADMINISTRACION = "la_administracion"
LA_DECIDIO = "la_decidio"
OBJETIVO = "objetivo"
LA_REVISA = "la_revisa"
LA_HACE = "la_hace"
LA_PIDE = "la_pide"
LA_PIDE_DESDE_EL_AREA = "la_pide_desde_el_area"
SE_LA_PIDE_AL_AREA = "se_la_pide_al_area"
DECIDE_QUIEN_LA_HACE = "decide_quien_la_hace"
ES_UN_PEDIDO_A_DIRECCION = "es_un_pedido_a_direccion"
LA_HIZO = "la_hizo"
LA_APROBO = "la_aprobo"
LA_PEDISTE = "la_pediste"
LA_PIDIO = "la_pidio"
TAREAS_QUE_LA_ESPERABAN = "tareas_que_la_esperaban"
YA_PUEDE_SEGUIR = "ya_puede_seguir"
LA_REABRIO = "la_reabrio"
MOTIVO_DE_LA_REAPERTURA = "motivo_de_la_reapertura"
DECIDE_QUIEN_LA_RETOMA = "decide_quien_la_retoma"
LA_TENIA = "la_tenia"
# Qué tareas lleva el aviso: referencias internas, que la IA nunca recibe.
REFERENCIAS = "referencias"

# Por qué un aviso ya no sale (sus significados, en `hechos.SIGNIFICADOS`).
YA_NO_HAY_TAREAS_NUEVAS = "ya_no_hay_tareas_nuevas"
SE_REABRIO_ANTES = "se_reabrio_antes"
YA_SE_CANCELO = "ya_se_cancelo"
LA_APROBO_QUIEN_LA_PIDIO = "la_aprobo_quien_la_pidio"

ABIERTAS = ("asignada", "en_curso", "bloqueada")
CERRADAS = ("terminada", "cancelada")

# El aviso a la administración para conectar a quien no tiene Leda (D9), con la etapa de
# `persecucion.avisar_para_que_lo_conecte`.
ETAPA_SIN_LEDA_CONECTADA = "motor_sin_leda_conectada"


# --- La carga --------------------------------------------------------------------------------

def avisar_la_carga(cur: psycopg.Cursor, workspace_id: str, task_id: str, ahora: datetime, *,
                    cargada_por_app_user: str | None, por_la_administracion: bool,
                    decidio: str | None = None) -> list[str]:
    """Guarda (o suma a los que todavía no salieron) los avisos de una tarea recién cargada por la
    web, en la transacción de la carga y con el espacio fijado. `cargada_por_app_user`: quien la
    cargó; `por_la_administracion`, si fue por la puerta de administración (quien la cargó no es
    del equipo, y `decidio` es quien la decidió). Devuelve los tipos guardados."""
    cur.execute("""select t.responsable_membership_id, t.titulo,
                          quien_revisa_la_tarea(t.id) as revisa
                     from task t where t.id = %s""", (task_id,))
    tarea = cur.fetchone()
    if tarea is None:
        return []
    carga = None
    if not por_la_administracion and cargada_por_app_user is not None:
        cur.execute("""select membership_id from integrante
                        where app_user_id = %s and activo""", (cargada_por_app_user,))
        fila = cur.fetchone()
        carga = str(fila["membership_id"]) if fila else None
    responsable = str(tarea["responsable_membership_id"])
    revisa = str(tarea["revisa"]) if tarea["revisa"] else None
    referencia = {"tarea": task_id, "carga": carga, "decidio": decidio}
    guardados = []
    if responsable != carga:
        _sumar(cur, workspace_id, TAREAS_NUEVAS, responsable, referencia, ahora)
        guardados.append(TAREAS_NUEVAS)
        _si_no_tiene_leda(cur, workspace_id, responsable, task_id, tarea["titulo"], ahora,
                          cargada_por_app_user)
    if revisa is not None and revisa not in (carga, responsable):
        _sumar(cur, workspace_id, TAREAS_NUEVAS_PARA_REVISAR, revisa, referencia, ahora)
        guardados.append(TAREAS_NUEVAS_PARA_REVISAR)
    return guardados


def _sumar(cur, workspace_id: str, tipo: str, destinatario: str, referencia: dict[str, Any],
           ahora: datetime) -> str:
    """El aviso de ese tipo a esa persona que todavía no salió, con esta tarea sumada y corrido al
    margen de esta carga (D6: un mensaje, unos minutos después de la última); si no hay ninguno,
    uno nuevo. Uno que está saliendo ahora (tomado por el envío) no se toca: va uno nuevo."""
    sale = ahora + VENTANA
    cur.execute("""select id, hechos from scheduled_notice
                    where tipo = %s and destinatario_membership_id = %s and estado = 'guardado'
                    order by creado_en limit 1
                    for update skip locked""", (tipo, destinatario))
    aviso = cur.fetchone()
    if aviso is None:
        aviso_id, _ = guardar(cur, workspace_id, tipo, task_id=referencia["tarea"],
                              destinatario=destinatario,
                              hechos={"aviso": tipo, "necesita_respuesta": False,
                                      REFERENCIAS: [referencia]},
                              programado_para=sale, ahora=ahora,
                              clave=f"motor:{tipo}:{referencia['tarea']}:{destinatario}")
        return aviso_id
    hechos = dict(aviso["hechos"] or {})
    referencias = [r for r in hechos.get(REFERENCIAS) or [] if r["tarea"] != referencia["tarea"]]
    hechos[REFERENCIAS] = [*referencias, referencia]
    # Sale a los minutos de la última carga (D6), aunque el que estaba esperando estuviera
    # programado más adelante (el reloj de Leda se adelantó y volvió atrás): nunca queda preso
    # (prueba por Telegram de la J4).
    cur.execute("""update scheduled_notice
                      set hechos = %s, task_id = null, programado_para = %s
                    where id = %s""", (_json(hechos), sale, aviso["id"]))
    return str(aviso["id"])


def _si_no_tiene_leda(cur, workspace_id: str, persona: str, task_id: str, titulo: str,
                      ahora: datetime, app_user_id: str | None) -> None:
    """D9: si la persona no tiene Leda conectada, la administración recibe el aviso para
    conectarla, una vez por persona y por día (el aviso de sus tareas la espera)."""
    quien = integrante(cur, persona)
    if quien is None or quien["telegram_user_id"] is not None:
        return
    registrar_incidente_y_si_se_aviso(
        cur, workspace_id,
        f"Se le cargó a {quien['nombre']} la tarea «{titulo}» desde la web, y {quien['nombre']} "
        f"no tiene un chat con Leda (no conectó su Telegram): el aviso de sus tareas espera a que "
        f"se conecte. Hay que conectarlo.",
        severidad="media", etapa=ETAPA_SIN_LEDA_CONECTADA, referencia_tipo="task",
        referencia_id=task_id, app_user_id=app_user_id,
        clave=f"{ETAPA_SIN_LEDA_CONECTADA}:{persona}:{ahora.date().isoformat()}")


# --- Al salir --------------------------------------------------------------------------------

def vigencia_de_las_tareas_nuevas(m: Momento, aviso) -> tuple[str | None, dict[str, Any]]:
    """Sale con las tareas que siguen abiertas y siguen siendo de quien lo recibe."""
    persona = str(aviso["destinatario_membership_id"])
    tareas = []
    for referencia in (dict(aviso["hechos"] or {})).get(REFERENCIAS) or []:
        tarea = _la_tarea(m.cur, referencia["tarea"])
        if (tarea is None or tarea["estado"] not in ABIERTAS
                or str(tarea["responsable_membership_id"]) != persona):
            continue
        tareas.append(_una_tarea_nueva(m, tarea, referencia, para=persona))
    if not tareas:
        return YA_NO_HAY_TAREAS_NUEVAS, {}
    return None, {"aviso": TAREAS_NUEVAS, "necesita_respuesta": False,
                  TAREAS_QUE_LE_CARGARON: tareas}


def vigencia_de_las_tareas_para_revisar(m: Momento, aviso) -> tuple[str | None, dict[str, Any]]:
    """Sale con las tareas que siguen abiertas y siguen revisadas por quien lo recibe."""
    persona = str(aviso["destinatario_membership_id"])
    tareas = []
    for referencia in (dict(aviso["hechos"] or {})).get(REFERENCIAS) or []:
        tarea = _la_tarea(m.cur, referencia["tarea"])
        if (tarea is None or tarea["estado"] in CERRADAS
                or str(tarea["revisa"] or "") != persona):
            continue
        hecho = _una_tarea_nueva(m, tarea, referencia, para=persona)
        hecho.pop(LA_REVISA, None)
        hecho[LA_HACE] = _nombre(m.cur, tarea["responsable_membership_id"])
        tareas.append(hecho)
    if not tareas:
        return YA_NO_HAY_TAREAS_NUEVAS, {}
    return None, {"aviso": TAREAS_NUEVAS_PARA_REVISAR, "necesita_respuesta": False,
                  TAREAS_QUE_VA_A_REVISAR: tareas}


def _la_tarea(cur, task_id) -> dict[str, Any] | None:
    cur.execute("""select t.id, t.titulo, t.estado::text estado, t.fecha_objetivo,
                          t.responsable_membership_id, t.pedida_por_membership_id,
                          quien_revisa_la_tarea(t.id) as revisa, o.titulo as objetivo,
                          a.nombre as area
                     from task t
                     left join objective o on o.id = t.objective_id
                     left join area a on a.id = t.area_id
                    where t.id = %s""", (str(task_id),))
    return cur.fetchone()


def _una_tarea_nueva(m: Momento, tarea: dict[str, Any], referencia: dict[str, Any], *,
                     para: str) -> dict[str, Any]:
    """Una tarea nueva como la recibe la IA: su título, para cuándo, de qué objetivo, quién la
    cargó (o la administración y quién la decidió), quién la revisa y, si es un pedido, quién la
    pide."""
    cur = m.cur
    hecho: dict[str, Any] = {"tarea": tarea["titulo"],
                             "vence": m.fecha(tarea["fecha_objetivo"]).isoformat()}
    if tarea["objetivo"]:
        hecho[OBJETIVO] = tarea["objetivo"]
    if referencia.get("carga"):
        hecho[LA_CARGO] = _nombre(cur, referencia["carga"])
    else:
        hecho[LA_CARGO] = LA_ADMINISTRACION
        if referencia.get("decidio"):
            hecho[LA_DECIDIO] = _nombre(cur, referencia["decidio"])
    revisa = str(tarea["revisa"]) if tarea["revisa"] else None
    if revisa is not None and revisa != para:
        hecho[LA_REVISA] = _nombre(cur, revisa)
    pide = tarea["pedida_por_membership_id"]
    if pide is not None and str(pide) != para:
        hecho[LA_PIDE] = _nombre(cur, pide)
        if es_de_direccion(cur, tarea):
            hecho[ES_UN_PEDIDO_A_DIRECCION] = True
        else:
            # Un pedido a otra área (D14): desde qué área lo piden y a cuál (la de la tarea, la de
            # quien la recibe), y quien la recibe decide quién la hace. Las dos, para que no se
            # confundan (prueba por Telegram de la J4: "para el área de OT" era la de quien pide).
            area = _area_que_encabeza(cur, str(pide))
            if area:
                hecho[LA_PIDE_DESDE_EL_AREA] = area
            if tarea["area"]:
                hecho[SE_LA_PIDE_AL_AREA] = tarea["area"]
            if str(tarea["responsable_membership_id"]) == para:
                hecho[DECIDE_QUIEN_LA_HACE] = True
        if hecho.get(LA_CARGO) == hecho[LA_PIDE]:
            # Un pedido se cuenta como pedido: quien lo pide no "le cargó" una tarea (prueba por
            # Telegram de la J4: "Marcos te cargó esta tarea… es un pedido a Dirección").
            hecho.pop(LA_CARGO)
    return hecho


def _nombre(cur, membership_id) -> str | None:
    persona = integrante(cur, membership_id)
    return persona["nombre"] if persona else None


def _area_que_encabeza(cur, membership_id: str) -> str | None:
    cur.execute("""select nombre from area where referente_membership_id = %s
                    order by nombre limit 1""", (membership_id,))
    fila = cur.fetchone()
    return fila["nombre"] if fila else None


# --- Lo pedido a otra área --------------------------------------------------------------------

def avisar_lo_de_los_pedidos(conn: psycopg.Connection, workspace_id: str,
                             reloj: Reloj) -> dict[str, int]:
    """Una vuelta: los avisos de los pedidos que terminaron y de los que se reabrieron, que todavía
    no tienen el suyo. Corre en una transacción del espacio; quien llama la confirma."""
    ahora = reloj.ahora()
    resumen = {LO_PEDIDO_TERMINO: 0, LO_PEDIDO_SE_REABRIO: 0}
    with espacio(conn, workspace_id) as cur:
        # Cada cierre se reconoce por la aprobación que lo cerró: desde una reapertura sólo cuenta
        # una aprobación posterior (`motivo_no_cierra_tarea`), así que volver a cerrarla es otra.
        cur.execute(
            """select t.id, coalesce(a.id, t.id) as evento
                 from task t
                 left join lateral (select x.id from approval x
                                     where x.sujeto_tipo = 'tarea' and x.sujeto_id = t.id
                                       and x.decision = 'aprobado'
                                     order by x.at desc, x.id desc limit 1) a on true
                where t.pedida_por_membership_id is not null and t.estado = 'terminada'
                  and not exists (select 1 from scheduled_notice n
                                   where n.tipo = %s
                                     and n.dedupe_key like %s || coalesce(a.id, t.id) || ':%%')
                order by t.titulo, t.id""",
            (LO_PEDIDO_TERMINO, f"motor:{LO_PEDIDO_TERMINO}:"))
        for fila in cur.fetchall():
            resumen[LO_PEDIDO_TERMINO] += _avisar_que_termino(cur, workspace_id, str(fila["id"]),
                                                              str(fila["evento"]), ahora)
        cur.execute(
            """select r.* from reapertura_de_tarea r
                where not exists (select 1 from scheduled_notice n
                                   where n.tipo = %s and n.dedupe_key = %s || r.id)
                order by r.at, r.id""",
            (LO_PEDIDO_SE_REABRIO, f"motor:{LO_PEDIDO_SE_REABRIO}:"))
        for reapertura in cur.fetchall():
            guardar(cur, workspace_id, LO_PEDIDO_SE_REABRIO, task_id=str(reapertura["task_id"]),
                    destinatario=str(reapertura["responsable_membership_id"]),
                    hechos={"aviso": LO_PEDIDO_SE_REABRIO, "necesita_respuesta": False,
                            REFERENCIAS: [{"reapertura": str(reapertura["id"])}]},
                    programado_para=ahora, ahora=ahora,
                    clave=f"motor:{LO_PEDIDO_SE_REABRIO}:{reapertura['id']}")
            resumen[LO_PEDIDO_SE_REABRIO] += 1
    return {k: v for k, v in resumen.items() if v}


def _avisar_que_termino(cur, workspace_id: str, task_id: str, evento: str,
                        ahora: datetime) -> int:
    """Los avisos de un pedido que quedó terminado: a quien lo pidió, salvo que lo haya aprobado
    él, y a quien tenga una tarea abierta que lo esperaba. Uno por persona."""
    tarea = _la_tarea(cur, task_id)
    pidio = str(tarea["pedida_por_membership_id"])
    destinatarios = []
    if _quien_aprobo(cur, task_id) != pidio:
        destinatarios.append(pidio)
    for espera in _las_que_la_esperan(cur, task_id):
        persona = str(espera["responsable_membership_id"])
        if persona not in destinatarios and persona != str(tarea["responsable_membership_id"]):
            destinatarios.append(persona)
    for persona in destinatarios:
        guardar(cur, workspace_id, LO_PEDIDO_TERMINO, task_id=task_id, destinatario=persona,
                hechos={"aviso": LO_PEDIDO_TERMINO, "necesita_respuesta": False,
                        REFERENCIAS: [{"tarea": task_id, "evento": evento}]},
                programado_para=ahora, ahora=ahora,
                clave=f"motor:{LO_PEDIDO_TERMINO}:{evento}:{persona}")
    if not destinatarios:
        # Lo aprobó quien lo pidió y nadie lo esperaba (D1b): no hay a quién contarle. Queda igual
        # el aviso a quien lo pidió, omitido con su motivo, como la marca de que este cierre ya se
        # miró (nunca en silencio: el motivo está a la vista).
        aviso_id, nuevo = guardar(cur, workspace_id, LO_PEDIDO_TERMINO, task_id=task_id,
                                  destinatario=pidio,
                                  hechos={"aviso": LO_PEDIDO_TERMINO, "necesita_respuesta": False,
                                          REFERENCIAS: [{"tarea": task_id, "evento": evento}]},
                                  programado_para=ahora, ahora=ahora,
                                  clave=f"motor:{LO_PEDIDO_TERMINO}:{evento}:{pidio}")
        if nuevo:
            omitir(cur, aviso_id, LA_APROBO_QUIEN_LA_PIDIO, ahora)
    return len(destinatarios)


def _el_ultimo_cierre(cur, task_id: str) -> str:
    """Cómo se reconoce el cierre vigente de una tarea: la última aprobación (o la tarea misma, si
    no tiene ninguna), igual que en `avisar_lo_de_los_pedidos`."""
    cur.execute("""select x.id from approval x
                    where x.sujeto_tipo = 'tarea' and x.sujeto_id = %s and x.decision = 'aprobado'
                    order by x.at desc, x.id desc limit 1""", (task_id,))
    fila = cur.fetchone()
    return str(fila["id"]) if fila else task_id


def _quien_aprobo(cur, task_id: str) -> str | None:
    cur.execute("""select aprobador_membership_id from approval
                    where sujeto_tipo = 'tarea' and sujeto_id = %s and decision = 'aprobado'
                    order by at desc, id desc limit 1""", (task_id,))
    fila = cur.fetchone()
    return str(fila["aprobador_membership_id"]) if fila else None


def _las_que_la_esperan(cur, task_id: str) -> list[dict[str, Any]]:
    """Las tareas abiertas que esperan a ésta (una dependencia bloqueante), y si ya no esperan
    ninguna otra."""
    cur.execute("""select t.id, t.titulo, t.responsable_membership_id,
                          not exists (select 1 from dependency d2 join task o on o.id = d2.origen_task_id
                                       where d2.destino_task_id = t.id and d2.tipo = 'bloqueante'
                                         and o.estado not in ('terminada', 'cancelada'))
                            as ya_puede_seguir
                     from dependency d join task t on t.id = d.destino_task_id
                    where d.origen_task_id = %s and d.tipo = 'bloqueante'
                      and t.estado not in ('terminada', 'cancelada', 'en_revision')
                    order by t.titulo, t.id""", (task_id,))
    return cur.fetchall()


def vigencia_de_lo_pedido_que_termino(m: Momento, aviso) -> tuple[str | None, dict[str, Any]]:
    """Sale mientras el pedido siga terminado por el mismo cierre (si se reabrió antes, no: llega
    el del próximo cierre; revisión de la J4b, R3-termino-duplicado: si se reabrió y se volvió a
    cerrar antes de que éste saliera, el del cierre nuevo ya lo cuenta). A quien lo pidió, lo que
    lo esperaba; a otra persona, sus tareas que lo esperaban."""
    persona = str(aviso["destinatario_membership_id"])
    [referencia] = (dict(aviso["hechos"] or {})).get(REFERENCIAS) or [{}]
    tarea = _la_tarea(m.cur, referencia.get("tarea"))
    if tarea is None or tarea["estado"] != "terminada":
        return SE_REABRIO_ANTES, {}
    if referencia.get("evento") != _el_ultimo_cierre(m.cur, str(tarea["id"])):
        return SE_REABRIO_ANTES, {}
    pidio = str(tarea["pedida_por_membership_id"])
    hechos: dict[str, Any] = {"aviso": LO_PEDIDO_TERMINO, "necesita_respuesta": False,
                              "tarea": tarea["titulo"],
                              LA_HIZO: _nombre(m.cur, tarea["responsable_membership_id"])}
    aprobo = _quien_aprobo(m.cur, str(tarea["id"]))
    if aprobo is not None and aprobo != persona:
        hechos[LA_APROBO] = _nombre(m.cur, aprobo)
    if persona == pidio:
        hechos[LA_PEDISTE] = True
    else:
        hechos[LA_PIDIO] = _nombre(m.cur, pidio)
    esperan = [e for e in _las_que_la_esperan(m.cur, str(tarea["id"]))
               if persona == pidio or str(e["responsable_membership_id"]) == persona]
    if esperan:
        hechos[TAREAS_QUE_LA_ESPERABAN] = [
            {"tarea": e["titulo"], YA_PUEDE_SEGUIR: e["ya_puede_seguir"],
             **({"responsable": _nombre(m.cur, e["responsable_membership_id"])}
                if str(e["responsable_membership_id"]) != persona else {})}
            for e in esperan]
    return None, hechos


def vigencia_de_lo_pedido_que_se_reabrio(m: Momento, aviso) -> tuple[str | None, dict[str, Any]]:
    """Sale mientras la tarea siga sin cancelar: al referente que la recibe de vuelta, quién la
    reabrió, con su motivo, y que decide quién la retoma."""
    [referencia] = (dict(aviso["hechos"] or {})).get(REFERENCIAS) or [{}]
    m.cur.execute("select * from reapertura_de_tarea where id = %s",
                  (referencia.get("reapertura"),))
    reapertura = m.cur.fetchone()
    tarea = _la_tarea(m.cur, reapertura["task_id"]) if reapertura else None
    if tarea is None or tarea["estado"] == "cancelada":
        return YA_SE_CANCELO, {}
    persona = str(aviso["destinatario_membership_id"])
    hechos: dict[str, Any] = {"aviso": LO_PEDIDO_SE_REABRIO, "necesita_respuesta": False,
                              "tarea": tarea["titulo"],
                              LA_REABRIO: _nombre(m.cur, reapertura["pedida_por_membership_id"]),
                              MOTIVO_DE_LA_REAPERTURA: reapertura["motivo"],
                              DECIDE_QUIEN_LA_RETOMA: True}
    antes = reapertura["responsable_anterior_membership_id"]
    if antes is not None and str(antes) != persona:
        hechos[LA_TENIA] = _nombre(m.cur, antes)
    return None, hechos


def _json(valor: Any) -> str:
    import json
    return json.dumps(valor, ensure_ascii=False, default=str)
