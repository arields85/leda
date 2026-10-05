"""La escalera del motor de conversación (E2-5).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Escalera"); mecánica §9; ADR 0018, decisión
9b; ADR 0017, decisión 6. Propia: `leda.escalera` no se toca ni se importa (sus textos son
fijos y escala sin mirar si hubo respuesta).

`correr_escalera` la corre para cada tarea abierta (asignada o en curso, con fecha comprometida
y sin un bloqueo abierto) y sólo decide qué aviso guardar; los manda `avisos.enviar_avisos`,
que los vuelve a leer al salir. La corre el ciclo cada minuto (E2-6); con un reloj inyectado,
las pruebas mueven los días. Todo se cuenta en días hábiles del espacio desde el vencimiento V:

- **Aviso previo**, uno solo, N días hábiles antes (`workspace_setting`
  `aviso_previo_dias_habiles`; 3 en CoreWork). Una tarea con menos días por delante lo recibe
  enseguida: la escalera se comprime y no saltea el paso. No pide respuesta.
- **Pedidos de estado**, desde V: el primero abre la espera (`pending_reply`) y, al salir, la
  pregunta del estado de la tarea. El siguiente sale recién un día hábil después del anterior,
  y sólo si la espera sigue abierta: una respuesta (inicio, previsión, bloqueo o quién destraba)
  la cierra y la escalera se detiene. El tercero avisa a quién se va a escalar.
- **Escalamiento**, el paso siguiente, por la ruta `falta_persistente_de_respuesta`: privado, a
  quien diga la ruta, con los hechos (el atraso, los pedidos sin respuesta, lo que depende).

Un paso por vez y nunca dos el mismo día hábil: si el ciclo estuvo parado, la escalera retoma
desde el paso que sigue. Cada paso es un aviso guardado con una clave de deduplicación (la
tarea, su vencimiento y el paso): correrla de nuevo no hace nada nuevo. Una tarea bloqueada no
está en la escalera, y un aviso suyo guardado se omite al salir.

**Ausencias.** Mientras la persona está ausente (`absence`), su escalera no avanza y lo que
tenía guardado no le llega. Cuando vuelve de una ausencia que tocó el período de la escalera, en
lugar del paso que le tocaba recibe un reencuadre (mecánica §9), que reemplaza lo guardado:
desde V pide el estado, como un pedido; antes de V, no pide nada. Después, la escalera retoma
desde donde quedó.

**Sin `aviso_previo_dias_habiles`** (el plan lo dejó `PENDIENTE`): se usa el mínimo del núcleo,
un día hábil (mecánica §9), y cada aviso previo que sale con él deja un incidente de severidad
baja para el administrador: nunca en silencio, y sin escribir la configuración por su cuenta.
**Sin ruta de escalamiento** con alguien que no sea el responsable: no se escala a nadie, se
registra un incidente una vez y la espera queda escalada.
"""

from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from typing import Any

import psycopg

from leda.calendario import Calendario
from leda.db import espacio
from leda.incidentes import registrar_incidente

from .avisos import (ABIERTOS, ESPERA_DE_ESTADO, Momento, ausente, espera_abierta, guardar,
                     hechos_de_la_escalera, leer_tarea, omitir, quienes_escalan)
from .tiempo import Reloj

ETAPA_ESCALERA = "motor_escalera"
CLAVE_AVISO_PREVIO = "aviso_previo_dias_habiles"
MINIMO_DEL_NUCLEO = 1          # mecánica §9: nunca menos de un día hábil entre pasos

TIPOS_DE_LA_ESCALERA = ("aviso_previo", "pedido_de_estado", "reencuadre", "escalamiento")
PEDIDOS = 3                     # V, V+1 y V+2; el paso siguiente es el escalamiento
REEMPLAZADO = "reemplazado_por_el_reencuadre"

# Lo que cada aviso trae fijo; lo demás lo lee `avisos.hechos_de_la_escalera` al guardarlo y
# de nuevo al salir.
HECHOS_DEL_AVISO_PREVIO = {"aviso": "vencimiento_proximo", "necesita_respuesta": False}


def clave(tipo: str, task_id: str, vence: date, *resto: Any) -> str:
    """motor:<tipo>:<tarea>:<vencimiento>[:<paso, destinatario o ausencia>][:<ronda>]. La
    ronda cuenta los reencuadres: un paso reemplazado por uno se vuelve a guardar."""
    return ":".join(["motor", tipo, str(task_id), vence.isoformat(), *map(str, resto)])


def correr_escalera(conn: psycopg.Connection, workspace_id: str,
                    reloj: Reloj) -> dict[str, int]:
    """Guarda los pasos que tocan ahora. Corre en una transacción de `db.espacio`; quien llama
    la confirma. Devuelve cuántos avisos guardó de cada tipo."""
    resumen: Counter[str] = Counter()
    with espacio(conn, workspace_id) as cur:
        m = Momento(cur, workspace_id, Calendario.desde_base(cur, workspace_id), reloj.ahora())
        n = dias_de_aviso_previo(cur, workspace_id)
        cur.execute("""select t.id from task t
                        where t.estado::text = any(%s) and t.fecha_objetivo is not null
                          and not exists (select 1 from blocker b
                                           where b.task_id = t.id and b.resuelto_en is null)
                        order by t.fecha_objetivo, t.titulo""", (list(ABIERTOS),))
        for fila in cur.fetchall():
            guardado = _un_paso(m, leer_tarea(cur, fila["id"]), n)
            if guardado:
                resumen[guardado] += 1
    return dict(resumen)


def dias_de_aviso_previo(cur, workspace_id: str) -> int | None:
    """Los días hábiles del aviso previo del espacio; `None` si no están configurados."""
    cur.execute("""select valor from workspace_setting
                    where workspace_id = %s and clave = %s""", (workspace_id,
                                                               CLAVE_AVISO_PREVIO))
    fila = cur.fetchone()
    return int(fila["valor"]) if fila else None


# --- Un paso ----------------------------------------------------------------------------------

def _un_paso(m: Momento, tarea: dict[str, Any], n: int | None) -> str | None:
    cur, persona = m.cur, str(tarea["responsable_membership_id"])
    if ausente(cur, persona, m.hoy):
        return None                     # pausada: no avanza mientras no está
    vence = m.fecha(tarea["fecha_objetivo"])
    if m.hoy < vence:
        k = -m.cal.habiles_entre(m.ahora, tarea["fecha_objetivo"])
    else:
        k = m.cal.habiles_entre(tarea["fecha_objetivo"], m.ahora)
    avisos = _avisos_de(cur, tarea["id"], vence)
    escalon = [a for a in avisos if a["tipo"] != "aviso_previo"]
    espera = espera_abierta(cur, tarea["id"])

    if any(a["tipo"] == "escalamiento" for a in escalon) or (espera and espera["escalado_en"]):
        return None                     # ya escaló: la escalera terminó
    ultimo = escalon[-1] if escalon else None
    if ultimo and ultimo["estado"] in ("omitido", "fallido") and \
            ultimo["motivo_omision"] != REEMPLAZADO:
        return None                     # detenida: ya no correspondía o la IA no lo redactó
    enviados = sorted((a for a in escalon if a["estado"] == "enviado"),
                      key=lambda a: a["resuelto_en"])
    ultimo_enviado = enviados[-1] if enviados else None
    if ultimo_enviado and ultimo_enviado["hechos"].get("necesita_respuesta") and espera is None:
        return None                     # contestó: la espera se cerró

    dias = n if n is not None else MINIMO_DEL_NUCLEO
    vuelta = _vuelta_de_una_ausencia(m, persona, _restar_habiles(m.cal, vence, dias))
    if vuelta is not None and not any(a["dedupe_key"] == clave("reencuadre", tarea["id"],
                                                               vence, vuelta["id"])
                                      for a in avisos):
        return _reencuadrar(m, tarea, vence, k, vuelta)
    if any(a["estado"] == "guardado" for a in escalon):
        return None                     # el paso anterior todavía no salió

    if k < 0:
        if -k <= dias and not avisos:
            return _guardar_aviso_previo(m, tarea, vence, configurado=n is not None)
        return None
    siguiente = 1 + max((_paso(a) for a in enviados if a["tipo"] == "pedido_de_estado"),
                        default=-1)
    if siguiente > PEDIDOS or k < siguiente:
        return None
    if ultimo_enviado and m.cal.habiles_entre(ultimo_enviado["resuelto_en"], m.ahora) < 1:
        return None                     # nunca dos pasos el mismo día hábil
    # Un paso que un reencuadre reemplazó vuelve a guardarse con otra clave: la de su ronda.
    ronda = [f"r{r}" for r in [sum(a["tipo"] == "reencuadre" for a in avisos)] if r]
    if siguiente < PEDIDOS:
        return _pedir_el_estado(m, tarea, vence, siguiente, ronda)
    return _escalar(m, tarea, vence, [a for a in enviados if a["tipo"] == "pedido_de_estado"],
                    ronda)


def _avisos_de(cur, task_id, vence: date) -> list[dict[str, Any]]:
    """Los avisos de la escalera de la tarea para este vencimiento (está en su clave)."""
    cur.execute("""select * from scheduled_notice
                    where task_id = %s and tipo = any(%s)
                      and split_part(dedupe_key, ':', 4) = %s
                    order by creado_en, dedupe_key""",
                (str(task_id), list(TIPOS_DE_LA_ESCALERA), vence.isoformat()))
    return cur.fetchall()


def _paso(aviso) -> int:
    return int(aviso["dedupe_key"].split(":")[4])


def _guardar(m: Momento, tipo: str, tarea, vence: date, base: dict[str, Any], *resto,
             destinatario: str | None = None) -> str:
    hechos = hechos_de_la_escalera(m, tipo, tarea, base)
    aviso_id, _ = guardar(
        m.cur, m.workspace_id, tipo, task_id=str(tarea["id"]),
        destinatario=destinatario or str(tarea["responsable_membership_id"]),
        hechos={**base, **hechos}, programado_para=m.cal.dentro_de_jornada(m.ahora),
        clave=clave(tipo, tarea["id"], vence, *resto), ahora=m.ahora)
    return aviso_id


def _guardar_aviso_previo(m: Momento, tarea, vence: date, *, configurado: bool) -> str:
    _guardar(m, "aviso_previo", tarea, vence, HECHOS_DEL_AVISO_PREVIO)
    if not configurado:
        registrar_incidente(
            m.cur, m.workspace_id,
            f"El espacio no tiene configurado `{CLAVE_AVISO_PREVIO}`: el aviso previo de una "
            f"tarea se guardó con el mínimo del núcleo, un día hábil antes del vencimiento "
            f"(mecánica §9). Configurarlo en el pack del espacio (en CoreWork, 3).",
            severidad="baja", etapa=ETAPA_ESCALERA)
    return "aviso_previo"


def _pedir_el_estado(m: Momento, tarea, vence: date, paso: int, ronda: list[str]) -> str:
    base = {"aviso": "pedido_de_estado", "numero": paso + 1, "necesita_respuesta": True}
    if paso == PEDIDOS - 1:
        base["avisa_que_va_a_escalar"] = True
    _guardar(m, "pedido_de_estado", tarea, vence, base, paso, *ronda)
    _abrir_la_espera(m, tarea)
    return "pedido_de_estado"


def _escalar(m: Momento, tarea, vence: date, pedidos: list[dict[str, Any]],
             ronda: list[str]) -> str | None:
    destinos = quienes_escalan(m.cur, tarea)
    if not destinos:
        registrar_incidente(
            m.cur, m.workspace_id,
            "La escalera del motor tenía que escalar una tarea por falta de respuesta (tres "
            "pedidos de estado sin contestar) y el espacio no tiene una ruta "
            "`falta_persistente_de_respuesta` con alguien que no sea el responsable: no se "
            "escaló a nadie.", severidad="media", etapa=ETAPA_ESCALERA)
        m.cur.execute("""update pending_reply set escalado_en = %s
                          where task_id = %s and satisfecho_en is null""",
                      (m.ahora, str(tarea["id"])))
        return None
    base = {"aviso": "falta_de_respuesta", "necesita_respuesta": False,
            "pedidos_de_estado_sin_respuesta": len(pedidos),
            "pedido_desde": m.fecha(pedidos[0]["resuelto_en"]).isoformat()}
    for destino in destinos:
        _guardar(m, "escalamiento", tarea, vence, base, destino["membership_id"], *ronda,
                 destinatario=str(destino["membership_id"]))
    return "escalamiento"


def _reencuadrar(m: Momento, tarea, vence: date, k: int, vuelta) -> str:
    """Lo guardado que no salió durante la ausencia queda reemplazado por el reencuadre."""
    m.cur.execute("""select id from scheduled_notice
                      where task_id = %s and estado = 'guardado' and tipo = any(%s)
                        and split_part(dedupe_key, ':', 4) = %s""",
                  (str(tarea["id"]), list(TIPOS_DE_LA_ESCALERA), vence.isoformat()))
    for fila in m.cur.fetchall():
        omitir(m.cur, str(fila["id"]), REEMPLAZADO, m.ahora)
    base = {"aviso": "vuelta_de_ausencia", "necesita_respuesta": k >= 0,
            "ausencia": {"desde": vuelta["desde"].isoformat(),
                         "hasta": vuelta["hasta"].isoformat()}}
    _guardar(m, "reencuadre", tarea, vence, base, vuelta["id"])
    if k >= 0:
        _abrir_la_espera(m, tarea)
    return "reencuadre"


def _abrir_la_espera(m: Momento, tarea) -> None:
    """La espera del estado de la tarea (ADR 0017, decisión 6): una por tarea mientras no se
    conteste; el recordatorio siguiente la mantiene."""
    if espera_abierta(m.cur, tarea["id"]) is not None:
        return
    sale = m.cal.dentro_de_jornada(m.ahora)
    m.cur.execute(
        """insert into pending_reply (workspace_id, membership_id, task_id, tipo,
                                      preguntado_en, vence_en)
           values (%s, %s, %s, %s, %s, %s)""",
        (m.workspace_id, str(tarea["responsable_membership_id"]), str(tarea["id"]),
         ESPERA_DE_ESTADO, sale, m.cal.dentro_de_jornada(m.cal.sumar_habiles(sale, 1))))


def _vuelta_de_una_ausencia(m: Momento, persona: str, inicio: date) -> dict[str, Any] | None:
    """La última ausencia de la persona que ya terminó y tocó el período de la escalera (desde
    el día del aviso previo)."""
    m.cur.execute("""select id, desde, hasta from absence
                      where membership_id = %s and hasta is not null
                        and hasta < %s and hasta >= %s and desde <= %s
                      order by hasta desc limit 1""", (persona, m.hoy, inicio, m.hoy))
    return m.cur.fetchone()


def _restar_habiles(cal: Calendario, dia: date, n: int) -> date:
    while n > 0:
        dia -= timedelta(days=1)
        if cal.es_habil(dia):
            n -= 1
    return dia

