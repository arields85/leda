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

**Cuándo termina** (revisión de la E2-5). La escalera es de un vencimiento: termina al escalar
(nada más se le pide a nadie por ese vencimiento) o cuando la persona contesta o se bloquea la
tarea. Un paso que no llegó por otra cosa (la IA no lo redactó tras sus reintentos, con su
incidente; el destinatario no se podía alcanzar) no la apaga: cuenta como dado, la escalera
sigue con el próximo y sus hechos dicen cuántos no le llegaron. Un vencimiento nuevo empieza su
propia escalera de cero, aunque la anterior haya escalado sin respuesta. La fecha comprometida
no cambia por chat (ADR 0017, decisión 4): una previsión no empieza otra escalera. Qué sigue
cuando vence una previsión queda `PENDIENTE` de decisión del usuario.

**Un avance sin un hecho cierto** (`informar_avance`, decisión del usuario, 2026-10-05). La
escalera escala sólo el silencio: un avance contesta el pedido, aunque no traiga nada cierto, así
que la cuenta de pedidos sin respuesta empieza de nuevo desde él. La espera sigue abierta, y el
pedido del día hábil siguiente (`repregunta_de_estado`, que guarda la ficha) es el primero de la
cuenta nueva: si queda sin respuesta, la escalera sigue desde ahí, un paso por día hábil, y el
escalamiento dice el último avance. Un paso que no había salido cuando llegó el avance queda
reemplazado (`REEMPLAZADO_POR_UN_AVANCE`): no cuenta como dado ni como escalamiento.

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
from .fichas import REEMPLAZADO_POR_UN_AVANCE, REPREGUNTA_DE_ESTADO
from .tiempo import Reloj

ETAPA_ESCALERA = "motor_escalera"
CLAVE_AVISO_PREVIO = "aviso_previo_dias_habiles"
MINIMO_DEL_NUCLEO = 1          # mecánica §9: nunca menos de un día hábil entre pasos

TIPOS_DE_LA_ESCALERA = ("aviso_previo", "pedido_de_estado", "reencuadre", "escalamiento",
                        REPREGUNTA_DE_ESTADO)
PEDIDOS = 3                     # V, V+1 y V+2; el paso siguiente es el escalamiento
REEMPLAZADO = "reemplazado_por_el_reencuadre"
# Los pasos que no salieron porque otro los reemplazó: no cuentan como dados.
NO_DADOS = frozenset({REEMPLAZADO, REEMPLAZADO_POR_UN_AVANCE})
# Los motivos de omisión que detienen la escalera de un vencimiento: la persona contestó o se
# bloqueó la tarea antes de que el paso saliera (9b; mecánica §9). Cualquier otro paso que no
# llegó (la IA no lo redactó, el destinatario no se podía alcanzar) cuenta como dado y la
# escalera sigue con el próximo: nunca se apaga en silencio.
DETIENEN = frozenset({"ya_respondio", "bloqueo_abierto"})

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

    avance = _ultimo_avance(escalon)
    if _ya_escalo(escalon, espera):
        return None                     # la escalera de este vencimiento terminó
    if any(a["estado"] == "omitido" and a["motivo_omision"] in DETIENEN for a in escalon):
        return None                     # contestó o se bloqueó antes de que saliera un paso
    # Los pasos dados: salieron, fallaron o se omitieron por otra cosa. Uno que la IA no
    # redactó ya dejó su incidente y no apaga el seguimiento: la escalera sigue con el próximo.
    dados = sorted((a for a in escalon if a["estado"] != "guardado"
                    and a["motivo_omision"] not in NO_DADOS), key=lambda a: a["resuelto_en"])
    ultimo_dado = dados[-1] if dados else None
    if espera is None and any(a["hechos"].get("necesita_respuesta") for a in dados):
        return None                     # contestó: la espera que abrió se cerró

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
    # Los pedidos sin respuesta: desde el último avance, si hubo uno (su repregunta es el paso 0).
    pedidos = [a for a in dados if a["tipo"] in ("pedido_de_estado", REPREGUNTA_DE_ESTADO)
               and (avance is None or a["creado_en"] >= avance["creado_en"])]
    siguiente = 1 + max((_paso(a) for a in pedidos), default=-1)
    if siguiente > PEDIDOS or k < siguiente:
        return None
    if ultimo_dado and m.cal.habiles_entre(ultimo_dado["resuelto_en"], m.ahora) < 1:
        return None                     # nunca dos pasos el mismo día hábil
    # Un paso que un reencuadre reemplazó vuelve a guardarse con otra clave: la de su ronda.
    # Los pasos de la cuenta que empieza después de un avance, también: la de sus avances.
    ronda = [f"a{v}" for v in [sum(a["tipo"] == REPREGUNTA_DE_ESTADO for a in avisos)] if v]
    ronda += [f"r{r}" for r in [sum(a["tipo"] == "reencuadre" for a in avisos)] if r]
    if siguiente < PEDIDOS:
        return _pedir_el_estado(m, tarea, vence, siguiente, ronda, pedidos)
    return _escalar(m, tarea, vence, pedidos, ronda, avance)


def _ya_escalo(escalon: list[dict[str, Any]], espera: dict[str, Any] | None) -> bool:
    """La escalera de un vencimiento termina al escalar (mecánica §9): con su aviso de
    escalamiento o, sin ruta, con la espera escalada. La espera cuenta sólo si la abrió esta
    escalera: la de un vencimiento anterior, escalada y sin contestar, no frena a la nueva,
    que empieza de cero (la fecha comprometida la cambiará la plataforma, ADR 0017,
    decisión 4). Un escalamiento cuenta sólo si se dio: uno guardado todavía puede quedar
    reemplazado (por un reencuadre o un avance), y uno reemplazado no salió (revisión de
    `informar_avance`)."""
    if any(a["tipo"] == "escalamiento" and a["estado"] != "guardado"
           and a["motivo_omision"] not in NO_DADOS for a in escalon):
        return True
    if espera is None or espera["escalado_en"] is None or not escalon:
        return False
    return espera["preguntado_en"] >= min(a["creado_en"] for a in escalon)


def _ultimo_avance(escalon: list[dict[str, Any]]) -> dict[str, Any] | None:
    """El pedido que guardó el último avance sin un hecho cierto, si hubo uno."""
    avances = [a for a in escalon if a["tipo"] == REPREGUNTA_DE_ESTADO]
    return max(avances, key=lambda a: a["creado_en"]) if avances else None


def _no_llegaron(pedidos: list[dict[str, Any]]) -> int:
    return sum(a["estado"] != "enviado" for a in pedidos)


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


def _pedir_el_estado(m: Momento, tarea, vence: date, paso: int, ronda: list[str],
                     anteriores: list[dict[str, Any]]) -> str:
    base = {"aviso": "pedido_de_estado", "numero": paso + 1, "necesita_respuesta": True}
    if _no_llegaron(anteriores):        # que no le hable como si ya le hubiera preguntado
        base["pedidos_anteriores_que_no_le_llegaron"] = _no_llegaron(anteriores)
    if paso == PEDIDOS - 1:
        base["avisa_que_va_a_escalar"] = True
    _guardar(m, "pedido_de_estado", tarea, vence, base, paso, *ronda)
    _abrir_la_espera(m, tarea)
    return "pedido_de_estado"


def _escalar(m: Momento, tarea, vence: date, pedidos: list[dict[str, Any]],
             ronda: list[str], avance: dict[str, Any] | None = None) -> str | None:
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
    llegaron = [a for a in pedidos if a["estado"] == "enviado"]
    base = {"aviso": "falta_de_respuesta", "necesita_respuesta": False,
            "pedidos_de_estado_sin_respuesta": len(llegaron)}
    if llegaron:
        base["pedido_desde"] = m.fecha(llegaron[0]["resuelto_en"]).isoformat()
    if _no_llegaron(pedidos):
        base["pedidos_de_estado_que_no_le_llegaron"] = _no_llegaron(pedidos)
    if avance is not None:      # contestó antes, sin nada cierto: también es un hecho
        base["avance_sin_algo_cierto"] = avance["hechos"]["avance_anterior"]
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
    conteste; el recordatorio siguiente la mantiene. Una escalada es de una escalera que ya
    terminó: la nueva abre la suya (una respuesta las contesta a las dos)."""
    abierta = espera_abierta(m.cur, tarea["id"])
    if abierta is not None and abierta["escalado_en"] is None:
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

