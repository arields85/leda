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
está en la escalera, y un aviso suyo guardado se omite al salir. Al destrabarse (`destrabar`,
ADR 0018, 9l) vuelve a estar: antes de su fecha, sigue sola; con el seguimiento ya empezado, la
jugada guarda el pedido del día hábil siguiente y la cuenta empieza de nuevo, como con un avance
(abajo), así que lo que la detuvo antes no la detiene.

**Cuándo termina** (revisión de la E2-5). La escalera es de un vencimiento: termina al escalar
(nada más se le pide a nadie por ese vencimiento) o cuando la persona contesta o se bloquea la
tarea. Un paso que no llegó por otra cosa (la IA no lo redactó tras sus reintentos, con su
incidente; el destinatario no se podía alcanzar) no la apaga: cuenta como dado, la escalera
sigue con el próximo y sus hechos dicen cuántos no le llegaron. Un vencimiento nuevo empieza su
propia escalera de cero, aunque la anterior haya escalado sin respuesta.

**Con una previsión, el seguimiento se mueve a la previsión** (ADR 0018, 9i; usuario,
2026-10-05; `ancla.py`). La escalera corre sobre su ancla: la fecha comprometida V o, si la
previsión vigente es posterior, la fecha prevista F. Con el ancla en F, el día de V sale un solo
recordatorio que no pide nada (`vencimiento_con_prevision`: vencía hoy, la previsión y el estado
de su aviso al referente, y cuándo se le pide el estado), salvo que la escalera de V ya haya
empezado; hasta F no se pide nada, ni hay aviso previo (la fecha la dio la persona); el día de F
se pide el estado como si fuera V y, sin respuesta, la escalera sigue desde ahí hasta escalar. Un
ancla nueva es una escalera nueva (el ancla va en la clave de cada paso). La fecha comprometida no
cambia por chat (ADR 0017, decisión 4): el atraso se cuenta contra ella.

**Un avance sin un hecho cierto** (`informar_avance`, decisión del usuario, 2026-10-05). La
escalera escala sólo el silencio: un avance contesta el pedido, aunque no traiga nada cierto, así
que la cuenta de pedidos sin respuesta empieza de nuevo desde él. La espera sigue abierta, y el
pedido del día hábil siguiente (`repregunta_de_estado`, que guarda la ficha) es el primero de la
cuenta nueva: si queda sin respuesta, la escalera sigue desde ahí, un paso por día hábil, y el
escalamiento dice el último avance. Un paso que no había salido cuando llegó el avance queda
reemplazado (`REEMPLAZADO_POR_UN_AVANCE`): no cuenta como dado ni como escalamiento. Un avance
después de escalar no guarda otro pedido (la escalera de esa ancla terminó) y sus hechos lo
dicen. La escalera y el avance toman la tarea de a uno (`ancla.candado`).

**Ausencias.** Mientras la persona está ausente (`absence`), su escalera no avanza y lo que
tenía guardado no le llega. Cuando vuelve de una ausencia que tocó el período de la escalera, en
lugar del paso que le tocaba recibe un reencuadre (mecánica §9), que reemplaza lo guardado:
desde V pide el estado, como un pedido; antes de V, no pide nada. Después, la escalera retoma
desde donde quedó.

**Una pregunta que espera respuesta** (su ficha de pregunta lo dice, `preguntas.TIPOS`; la de
quién destraba un bloqueo, 9c; decisión del usuario, 2026-10-05) tiene la misma escalera de quien
no contestó, contada desde el día en que se hizo, que es su primer pedido: sin respuesta, el día
hábil siguiente Leda la repite (`repregunta`, con lo que se había anotado), al otro la repite
avisando a quién se va a escalar, y al siguiente escala por la ruta de falta de respuesta
(`escalamiento_de_una_pregunta`). Un paso por día hábil; termina al escalar o cuando llega la
respuesta (la pregunta se cierra o su espera se contesta). La del estado de la tarea y la de su
fecha esperan con el pedido de estado: las repite la escalera de la tarea, no ésta. Una espera
cuya pregunta se cerró sin contestarse (una corrección la dejó sin efecto) ya no espera nada y
se cierra. Una ausencia la pausa, como a la de la tarea.

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

from .ancla import (NO_DADOS, REEMPLAZADO, REPREGUNTA_DE_ESTADO, TIPOS_DE_LA_ESCALERA,
                    VENCIMIENTO_CON_PREVISION, Anclaje, al_mediodia, anclaje, candado, escalo,
                    pasos)
from .avisos import (ABIERTOS, ESCALAMIENTO_DE_UNA_PREGUNTA, ESPERA_DE_ESTADO, REPREGUNTA,
                     Momento, ausente, espera_abierta, guardar, hechos_de_la_escalera,
                     hechos_de_una_pregunta, leer_tarea, omitir, quienes_escalan)
from .tiempo import Reloj, sale

ETAPA_ESCALERA = "motor_escalera"
CLAVE_AVISO_PREVIO = "aviso_previo_dias_habiles"
MINIMO_DEL_NUCLEO = 1          # mecánica §9: nunca menos de un día hábil entre pasos

PEDIDOS = 3                     # el ancla, +1 y +2; el paso siguiente es el escalamiento
# Los motivos de omisión que detienen la escalera de un vencimiento: la persona contestó o se
# bloqueó la tarea antes de que el paso saliera (9b; mecánica §9). Cualquier otro paso que no
# llegó (la IA no lo redactó, el destinatario no se podía alcanzar) cuenta como dado y la
# escalera sigue con el próximo: nunca se apaga en silencio.
BLOQUEO_ABIERTO = "bloqueo_abierto"
DETIENEN = frozenset({"ya_respondio", BLOQUEO_ABIERTO})

# Lo que cada aviso trae fijo; lo demás lo lee `avisos.hechos_de_la_escalera` al guardarlo y
# de nuevo al salir.
HECHOS_DEL_AVISO_PREVIO = {"aviso": "vencimiento_proximo", "necesita_respuesta": False}
HECHOS_DEL_VENCIMIENTO_CON_PREVISION = {"aviso": VENCIMIENTO_CON_PREVISION,
                                        "necesita_respuesta": False}
# Los pasos de una escalera anclada en una previsión lo dicen: el pedido es por la fecha que dio
# la persona, no por la comprometida.
POR_LA_PREVISION = {"seguimiento_por": "prevision"}


def clave(tipo: str, task_id: str, de: Anclaje | date, *resto: Any) -> str:
    """motor:<tipo>:<tarea>:<anclaje>[:<paso, destinatario o ausencia>][:<ronda>]. El anclaje es
    el del seguimiento (`ancla.py`); el aviso previo y el recordatorio del vencimiento van con
    la fecha comprometida sola. La ronda cuenta los reencuadres y los avances: un paso
    reemplazado por uno se vuelve a guardar."""
    parte = de.clave if isinstance(de, Anclaje) else de.isoformat()
    return ":".join(["motor", tipo, str(task_id), parte, *map(str, resto)])


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
        # Las preguntas que esperan respuesta con su propia espera (la del estado es de la
        # escalera de la tarea, arriba).
        cur.execute("""select * from pending_reply
                        where tipo <> %s and task_id is not null
                          and satisfecho_en is null and escalado_en is null
                        order by preguntado_en""", (ESPERA_DE_ESTADO,))
        for espera in cur.fetchall():
            guardado = _un_paso_de_una_pregunta(m, espera)
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
    if not candado(cur, tarea["id"], esperar=False):
        return None                     # un turno la tiene tomada: la vuelta siguiente
    if ausente(cur, persona, m.hoy):
        return None                     # pausada: no avanza mientras no está
    vence = m.fecha(tarea["fecha_objetivo"])
    de = anclaje(cur, tarea["id"], vence)           # V, o la previsión si es posterior
    hasta = de.fecha
    por = POR_LA_PREVISION if hasta > vence else {}
    k = m.cal.habiles_entre(al_mediodia(hasta, m.cal.zona), m.ahora)
    avisos = pasos(cur, tarea["id"], de)
    escalon = [a for a in avisos if a["tipo"] != "aviso_previo"]
    espera = espera_abierta(cur, tarea["id"])

    avance = _ultimo_avance(escalon)
    if escalo(escalon, espera):
        return None                     # la escalera de esta ancla terminó
    # Lo que detuvo una cuenta anterior no detiene la que empezó con un avance (o al
    # destrabarse, 9l): la persona contestó después, y la cuenta nueva corre desde ahí.
    if any(a["estado"] == "omitido" and a["motivo_omision"] in DETIENEN
           and (avance is None or a["creado_en"] >= avance["creado_en"]) for a in escalon):
        return None                     # contestó o se bloqueó antes de que saliera un paso
    # Los pasos dados: salieron, fallaron o se omitieron por otra cosa. Uno que la IA no
    # redactó ya dejó su incidente y no apaga el seguimiento: la escalera sigue con el próximo.
    dados = sorted((a for a in escalon if a["estado"] != "guardado"
                    and a["motivo_omision"] not in NO_DADOS), key=lambda a: a["resuelto_en"])
    ultimo_dado = dados[-1] if dados else None
    if espera is None and any(a["hechos"].get("necesita_respuesta") for a in dados):
        return None                     # contestó: la espera que abrió se cerró

    dias = n if n is not None else MINIMO_DEL_NUCLEO
    vuelta = _vuelta_de_una_ausencia(m, persona, _restar_habiles(m.cal, hasta, dias))
    if vuelta is not None and not any(a["dedupe_key"] == clave("reencuadre", tarea["id"],
                                                               de, vuelta["id"])
                                      for a in avisos):
        return _reencuadrar(m, tarea, de, vence, k, vuelta, por)
    if any(a["estado"] == "guardado" for a in escalon):
        return None                     # el paso anterior todavía no salió

    if k < 0:
        # Un aviso previo que el bloqueo omitió no se dio: destrabada antes del vencimiento, la
        # tarea vuelve a tenerlo mientras siga siendo previo (revisión de destrabar, 9l).
        dados_antes = [a for a in avisos if not _omitido_por_el_bloqueo(a)]
        if hasta == vence and -k <= dias and not dados_antes                 and not _hubo_aviso_previo(m, tarea, vence):
            return _guardar_aviso_previo(m, tarea, vence, configurado=n is not None,
                                         ronda=len(avisos) - len(dados_antes))
        if hasta > vence and m.hoy >= vence:
            return _recordar_el_vencimiento(m, tarea, vence)
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
        return _pedir_el_estado(m, tarea, de, siguiente, ronda, pedidos, por)
    return _escalar(m, tarea, de, pedidos, ronda, avance, por)


def _ultimo_avance(escalon: list[dict[str, Any]]) -> dict[str, Any] | None:
    """El pedido que guardó el último avance sin un hecho cierto, si hubo uno."""
    avances = [a for a in escalon if a["tipo"] == REPREGUNTA_DE_ESTADO]
    return max(avances, key=lambda a: a["creado_en"]) if avances else None


def _no_llegaron(pedidos: list[dict[str, Any]]) -> int:
    return sum(a["estado"] != "enviado" for a in pedidos)


def _paso(aviso) -> int:
    return int(aviso["dedupe_key"].split(":")[4])


def _guardar(m: Momento, tipo: str, tarea, fecha: Anclaje | date, base: dict[str, Any], *resto,
             destinatario: str | None = None) -> str:
    hechos = hechos_de_la_escalera(m, tipo, tarea, base)
    aviso_id, _ = guardar(
        m.cur, m.workspace_id, tipo, task_id=str(tarea["id"]),
        destinatario=destinatario or str(tarea["responsable_membership_id"]),
        hechos={**base, **hechos}, programado_para=sale(m.cal, m.ahora),
        clave=clave(tipo, tarea["id"], fecha, *resto), ahora=m.ahora)
    return aviso_id


def _guardar_aviso_previo(m: Momento, tarea, vence: date, *, configurado: bool,
                          ronda: int = 0) -> str:
    """`ronda`: cuántos avisos previos omitió un bloqueo; el que vuelve lleva su ronda en la
    clave (`b<n>`), así no choca con el omitido."""
    _guardar(m, "aviso_previo", tarea, vence, HECHOS_DEL_AVISO_PREVIO,
             *([f"b{ronda}"] if ronda else []))
    if not configurado:
        registrar_incidente(
            m.cur, m.workspace_id,
            f"El espacio no tiene configurado `{CLAVE_AVISO_PREVIO}`: el aviso previo de una "
            f"tarea se guardó con el mínimo del núcleo, un día hábil antes del vencimiento "
            f"(mecánica §9). Configurarlo en el pack del espacio (en CoreWork, 3).",
            severidad="baja", etapa=ETAPA_ESCALERA)
    return "aviso_previo"


def _hubo_aviso_previo(m: Momento, tarea, vence: date) -> bool:
    """El aviso previo es de la fecha comprometida, no de un anclaje: uno solo (9b). Uno que el
    bloqueo omitió no cuenta: no se dio."""
    base = clave("aviso_previo", tarea["id"], vence)
    m.cur.execute("""select 1 from scheduled_notice
                      where workspace_id = %s
                        and (dedupe_key = %s or dedupe_key like %s)
                        and not (estado = 'omitido' and motivo_omision = %s)""",
                  (m.workspace_id, base, base + ":b%", BLOQUEO_ABIERTO))
    return m.cur.fetchone() is not None


def _omitido_por_el_bloqueo(aviso: dict[str, Any]) -> bool:
    return aviso["estado"] == "omitido" and aviso["motivo_omision"] == BLOQUEO_ABIERTO


def _recordar_el_vencimiento(m: Momento, tarea, vence: date) -> str | None:
    """Con el ancla en una previsión, el único aviso del vencimiento (9i): uno solo, desde el día
    de V, y sólo si la escalera de V no empezó (si ya pidió el estado, la previsión llegó
    después y ya está contestado)."""
    if any(a["tipo"] != "aviso_previo" for a in pasos(m.cur, tarea["id"], vence)):
        return None
    la_clave = clave(VENCIMIENTO_CON_PREVISION, tarea["id"], vence)
    m.cur.execute("select 1 from scheduled_notice where workspace_id = %s and dedupe_key = %s",
                  (m.workspace_id, la_clave))
    if m.cur.fetchone() is not None:
        return None
    _guardar(m, VENCIMIENTO_CON_PREVISION, tarea, vence, HECHOS_DEL_VENCIMIENTO_CON_PREVISION)
    return VENCIMIENTO_CON_PREVISION


def _pedir_el_estado(m: Momento, tarea, hasta: Anclaje, paso: int, ronda: list[str],
                     anteriores: list[dict[str, Any]], por: dict[str, str]) -> str:
    base = {"aviso": "pedido_de_estado", "numero": paso + 1, "necesita_respuesta": True, **por}
    if _no_llegaron(anteriores):        # que no le hable como si ya le hubiera preguntado
        base["pedidos_anteriores_que_no_le_llegaron"] = _no_llegaron(anteriores)
    if paso == PEDIDOS - 1:
        base["avisa_que_va_a_escalar"] = True
    _guardar(m, "pedido_de_estado", tarea, hasta, base, paso, *ronda)
    _abrir_la_espera(m, tarea)
    return "pedido_de_estado"


def _escalar(m: Momento, tarea, hasta: Anclaje, pedidos: list[dict[str, Any]],
             ronda: list[str], avance: dict[str, Any] | None, por: dict[str, str]) -> str | None:
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
            "pedidos_de_estado_sin_respuesta": len(llegaron), **por}
    if llegaron:
        base["pedido_desde"] = m.fecha(llegaron[0]["resuelto_en"]).isoformat()
    if _no_llegaron(pedidos):
        base["pedidos_de_estado_que_no_le_llegaron"] = _no_llegaron(pedidos)
    if avance is not None:      # contestó antes, sin nada cierto: también es un hecho
        base["avance_sin_algo_cierto"] = avance["hechos"]["avance_anterior"]
    for destino in destinos:
        _guardar(m, "escalamiento", tarea, hasta, base, destino["membership_id"], *ronda,
                 destinatario=str(destino["membership_id"]))
    return "escalamiento"


def _reencuadrar(m: Momento, tarea, hasta: Anclaje, vence: date, k: int, vuelta,
                 por: dict[str, str]) -> str:
    """Lo guardado que no salió durante la ausencia (de este anclaje, y el aviso previo)
    queda reemplazado por el reencuadre."""
    m.cur.execute("""select id from scheduled_notice
                      where task_id = %s and estado = 'guardado' and tipo = any(%s)
                        and (split_part(dedupe_key, ':', 4) = any(%s) or dedupe_key = %s)""",
                  (str(tarea["id"]), list(TIPOS_DE_LA_ESCALERA), list(hasta.claves),
                   clave("aviso_previo", tarea["id"], vence)))
    for fila in m.cur.fetchall():
        omitir(m.cur, str(fila["id"]), REEMPLAZADO, m.ahora)
    base = {"aviso": "vuelta_de_ausencia", "necesita_respuesta": k >= 0,
            "ausencia": {"desde": vuelta["desde"].isoformat(),
                         "hasta": vuelta["hasta"].isoformat()},
            **(por if k >= 0 else {})}
    _guardar(m, "reencuadre", tarea, hasta, base, vuelta["id"])
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
    sale_en = sale(m.cal, m.ahora)
    m.cur.execute(
        """insert into pending_reply (workspace_id, membership_id, task_id, tipo,
                                      preguntado_en, vence_en)
           values (%s, %s, %s, %s, %s, %s)""",
        (m.workspace_id, str(tarea["responsable_membership_id"]), str(tarea["id"]),
         ESPERA_DE_ESTADO, sale_en,
         m.cal.dentro_de_jornada(m.cal.sumar_habiles(sale_en, 1))))


# --- La escalera de una pregunta que espera respuesta -------------------------------------------

def _un_paso_de_una_pregunta(m: Momento, espera: dict[str, Any]) -> str | None:
    """El paso que toca de la escalera de una pregunta: desde el día en que se hizo (el pedido
    0, en la respuesta), una repregunta por día hábil hasta la que avisa que va a escalar, y
    después el escalamiento. Sólo con la espera abierta y la pregunta sin cerrar."""
    cur = m.cur
    task_id, persona = str(espera["task_id"]), str(espera["membership_id"])
    if not candado(cur, task_id, esperar=False):
        return None                     # un turno la tiene tomada: la vuelta siguiente
    if ausente(cur, persona, m.hoy):
        return None                     # pausada: no avanza mientras no está
    cur.execute("""select * from conversation_question
                    where membership_id = %s and task_id = %s and tipo = %s
                      and cerrada_en is null
                    order by abierta_en desc limit 1""", (persona, task_id, espera["tipo"]))
    pregunta = cur.fetchone()
    if pregunta is None:
        # Se cerró sin contestarse (una corrección la dejó sin efecto): ya no espera nada.
        cur.execute("update pending_reply set satisfecho_en = %s where id = %s",
                    (m.ahora, espera["id"]))
        return None
    tarea = leer_tarea(cur, task_id)
    if tarea is None or tarea["estado"] in ("terminada", "cancelada"):
        return None
    de = f"q{pregunta['id']}"
    cur.execute("""select * from scheduled_notice
                    where task_id = %s and tipo = any(%s)
                      and split_part(dedupe_key, ':', 4) = %s
                    order by creado_en, dedupe_key""",
                (task_id, [REPREGUNTA, ESCALAMIENTO_DE_UNA_PREGUNTA], de))
    escalon = cur.fetchall()
    if any(a["estado"] == "guardado" for a in escalon):
        return None                     # el paso anterior todavía no salió
    if any(a["tipo"] == ESCALAMIENTO_DE_UNA_PREGUNTA for a in escalon):
        return None                     # terminó al escalar
    if any(a["estado"] == "omitido" and a["motivo_omision"] in DETIENEN for a in escalon):
        return None                     # contestó antes de que saliera
    dados = sorted(escalon, key=lambda a: a["resuelto_en"])
    siguiente = 1 + len(dados)          # el pedido 0 es la pregunta misma
    if siguiente > PEDIDOS or m.cal.habiles_entre(espera["preguntado_en"], m.ahora) < siguiente:
        return None
    if dados and m.cal.habiles_entre(dados[-1]["resuelto_en"], m.ahora) < 1:
        return None                     # nunca dos pasos el mismo día hábil
    sobre = _lo_anotado(pregunta)
    if siguiente < PEDIDOS:
        base = {"aviso": REPREGUNTA, "pregunta": pregunta["tipo"], "numero": siguiente + 1,
                "necesita_respuesta": True, **({"sobre": sobre} if sobre else {})}
        if _no_llegaron(dados):
            base["pedidos_anteriores_que_no_le_llegaron"] = _no_llegaron(dados)
        if siguiente == PEDIDOS - 1:
            base["avisa_que_va_a_escalar"] = True
        _guardar_de_una_pregunta(m, REPREGUNTA, tarea, base, de, siguiente)
        return REPREGUNTA
    destinos = quienes_escalan(cur, tarea)
    if not destinos:
        registrar_incidente(
            cur, m.workspace_id,
            "La escalera de una pregunta del motor tenía que escalar por falta de respuesta y "
            "el espacio no tiene una ruta `falta_persistente_de_respuesta` con alguien que no "
            "sea el responsable: no se escaló a nadie.", severidad="media", etapa=ETAPA_ESCALERA)
        cur.execute("update pending_reply set escalado_en = %s where id = %s",
                    (m.ahora, espera["id"]))
        return None
    base = {"aviso": "falta_de_respuesta", "pregunta": pregunta["tipo"],
            "necesita_respuesta": False, "preguntas_sin_respuesta": siguiente,
            "preguntado_el": m.fecha(espera["preguntado_en"]).isoformat(),
            **({"sobre": sobre} if sobre else {})}
    for destino in destinos:
        _guardar_de_una_pregunta(m, ESCALAMIENTO_DE_UNA_PREGUNTA, tarea, base, de,
                                 destino["membership_id"],
                                 destinatario=str(destino["membership_id"]))
    return ESCALAMIENTO_DE_UNA_PREGUNTA


def _lo_anotado(pregunta: dict[str, Any]) -> dict[str, Any]:
    """Lo que se había anotado cuando Leda hizo la pregunta (la jugada y sus datos, sin la
    tarea ni ids): lo que la repregunta recuerda."""
    jugada = pregunta["jugada"] or {}
    if not jugada.get("nombre"):
        return {}
    datos = {k: v for k, v in (jugada.get("datos") or {}).items() if k != "tarea"}
    return {"jugada": jugada["nombre"], **datos}


def _guardar_de_una_pregunta(m: Momento, tipo: str, tarea, base: dict[str, Any], de: str,
                             *resto, destinatario: str | None = None) -> str:
    aviso_id, _ = guardar(
        m.cur, m.workspace_id, tipo, task_id=str(tarea["id"]),
        destinatario=destinatario or str(tarea["responsable_membership_id"]),
        hechos={**base, **hechos_de_una_pregunta(m, tarea, base)},
        programado_para=sale(m.cal, m.ahora),
        clave=":".join(["motor", tipo, str(tarea["id"]), de, *map(str, resto)]), ahora=m.ahora)
    return aviso_id


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

