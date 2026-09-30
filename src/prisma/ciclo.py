"""Ciclo compartido de fondo.

`local.Escucha.tareas_de_fondo` (polling) y `servir` (webhook) necesitan la
misma secuencia por espacio -- cadencias vencidas, escalera, despacho -- más
el aviso a la administración una vez por pasada. Vivía duplicada porque
`servir` nunca la corría (`reloj.montar` sólo encolaba). Este módulo la
define una sola vez; `reloj.py` sigue sin enviar nada, `despachador.py` sigue
siendo el único que le habla a Telegram.

Una cadencia vencida se calcula, no se programa de antemano: en cada pasada
se relee `cadence_job` y se compara su cron contra `ultima_corrida` (o el
arranque del proceso, si nunca corrió) con `CronTrigger.get_next_fire_time`.
Así un cambio en la base -- un pack nuevo, un horario editado -- se aplica en
la próxima pasada, sin reiniciar el proceso. El piso de búsqueda es el MÁS
TARDE entre `ultima_corrida` y el arranque del proceso: nunca repone un
disparo anterior al arranque, ni uno cuya ventana ya pasó antes de un
reinicio con una corrida vieja.

Un cron roto (edición a mano, futuro tablero de cliente) no frena a las
demás cadencias del espacio ni a la escalera ni al despacho: se aísla por
fila (`cadencias_vencidas`) y se reporta una sola vez mientras persiste
(`SupresorDeRepetidos`, `reportar_fallo`) -- nunca en aluvión, nunca en
silencio.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from .calendario import Calendario
from .config import config
from .db import admin, espacio
from .despachador import TransporteTelegram, despachar, despachar_avisos_admin
from .incidentes import registrar_incidente
from . import huerfanos, reloj

# ---------------------------------------------------------------------------
# Día de semana: cron estándar (domingo=0 o 7) vs. el propio de APScheduler
# (lunes=0). `CronTrigger.from_crontab` no corrige esa diferencia (su propio
# docstring la documenta como "a historical mistake").
# ---------------------------------------------------------------------------

_RE_TOKEN_DIA = re.compile(r"^(?P<base>\*|\d+(?:-\d+)?)(?:/(?P<paso>\d+))?$")


def _expandir_dia_cron(token: str) -> list[int]:
    """Un token del campo día-de-semana estándar (`*`, `n`, `n-m`, con o sin
    `/paso`) a la lista de valores 0-6 (domingo=0) que representa -- 7, la
    otra forma de domingo, se pliega a 0.

    El rango y el paso se validan y se aplican sobre los valores CRUDOS
    (0-7), antes de plegar 7 a 0 (R3-002, revisión 2026-09-28+1): plegar
    antes rompía "1-7" (toda la semana) en "1-0", invertido, y aceptaba
    cualquier entero fuera de 0-7 plegándolo en silencio (`9 % 7` = 2,
    martes) en vez de rechazarlo como cadencia rota."""
    m = _RE_TOKEN_DIA.match(token)
    if not m:
        raise ValueError(f"día de semana no reconocido: {token!r}")
    base = m.group("base")
    paso = int(m.group("paso")) if m.group("paso") else None

    if base == "*":
        primero, ultimo = 0, 6
    elif "-" in base:
        a, b = base.split("-", 1)
        primero, ultimo = int(a), int(b)
    else:
        primero = ultimo = int(base)

    for valor in (primero, ultimo):
        if not 0 <= valor <= 7:
            raise ValueError(f"día de semana fuera de rango (0-7): {token!r}")
    if primero > ultimo:
        raise ValueError(f"rango de día de semana invertido: {token!r}")

    crudos = range(primero, ultimo + 1)
    if paso:
        crudos = [v for v in crudos if (v - primero) % paso == 0]
    return sorted({v % 7 for v in crudos})


def _dia_semana_apscheduler(valor: str) -> str:
    """Corrige el corrimiento de APScheduler antes de construir el trigger.

    Un nombre de día (`mon`, `mon-fri`, ...) no se toca: APScheduler ya lo
    interpreta con su propia numeración, sin ambigüedad. Un valor numérico
    -- único, lista, rango o con paso -- se expande a los días concretos que
    representa en el cron estándar y cada uno se corrige por separado antes
    de unirlos: corregir sólo las puntas de un rango rompe cuando empieza en
    domingo (`0-5` pasaría a `6-4`, invertido)."""
    if valor == "*":
        return valor

    tokens = []
    for parte in valor.split(","):
        parte = parte.strip()
        if any(c.isalpha() for c in parte):
            tokens.append(parte)  # nombre de día: ya en la numeración de APScheduler
            continue
        tokens.extend(str((v - 1) % 7) for v in _expandir_dia_cron(parte))
    return ",".join(tokens)


def _trigger_de(cron: str, zona_horaria: str):
    from apscheduler.triggers.cron import CronTrigger

    minuto, hora, dia, mes, dia_semana = cron.split()
    return CronTrigger(minute=minuto, hour=hora, day=dia, month=mes,
                       day_of_week=_dia_semana_apscheduler(dia_semana),
                       timezone=zona_horaria)


def cadencias_vencidas(
    cur, workspace_id: str, ahora: datetime, arranque: datetime,
) -> tuple[list[dict], list[tuple[dict, Exception, str]], list[dict]]:
    """`cadence_job` activos con un disparo entre su última corrida (o el
    arranque del proceso, el que sea más tarde) y ahora.

    Devuelve `(vencidas, fallidas, ok)`: un cron roto, o cualquier valor que
    APScheduler rechace, va a `fallidas` (con su causa, `CAUSA_CRON_INVALIDO`
    acá) sin frenar la evaluación de las demás filas. `ok` son todas las que
    se pudieron evaluar (vencidas o no) -- lo que necesita quien llama para
    marcar una falla anterior como recuperada."""
    cur.execute(
        """select c.id, c.nombre, c.cron, c.ultima_corrida, w.zona_horaria
             from cadence_job c join workspace w on w.id = c.workspace_id
            where c.workspace_id = %s and c.activo and w.activo""",
        (workspace_id,))
    vencidas: list[dict] = []
    fallidas: list[tuple[dict, Exception, str]] = []
    ok: list[dict] = []
    for job in cur.fetchall():
        try:
            # El piso de búsqueda es el MÁS TARDE de los dos, nunca la
            # última corrida sola (R3-001, revisión 2026-09-28+1): un
            # reinicio con una corrida vieja repondría un disparo cuya
            # ventana ya pasó, contra la mecánica §12 ("un mensaje de
            # cadencia cuya ventana ya pasó no se envía tarde, se
            # descarta").
            ultima = job["ultima_corrida"]
            desde = max(ultima, arranque) if ultima is not None else arranque
            trigger = _trigger_de(job["cron"], job["zona_horaria"])
            siguiente = trigger.get_next_fire_time(desde, ahora)
        except Exception as e:  # noqa: BLE001 -- una cadencia rota no frena a las demás
            fallidas.append((job, e, CAUSA_CRON_INVALIDO))
            continue
        ok.append(job)
        if siguiente is not None and siguiente <= ahora:
            vencidas.append(job)
    return vencidas, fallidas, ok


def ejecutar_ciclo_espacio(cur, workspace_id: str, transporte, ahora: datetime,
                          arranque: datetime, *, con_cadencias: bool = True,
                          lote: int = 50) -> dict:
    """Cadencias vencidas (si `con_cadencias`) + escalera + despacho, de un
    espacio. Mismo resumen que `despachar`, con `cadencias_encoladas`,
    `escalera_encoladas`, `huerfanos_avisados` y `huerfanos_fallo` (el barrido de
    `huerfanos`, T9-H19e), `cadencias_fallidas` (lista de `(job, error,
    causa)`, para que quien llama la reporte deduplicada) y `cadencias_ok`
    (para marcar una falla anterior como recuperada) agregados. Una cadencia
    rota nunca frena la escalera ni el despacho."""
    cal = Calendario.desde_base(cur, workspace_id)

    cadencias_encoladas = 0
    fallidas: list[tuple[dict, Exception, str]] = []
    ok: list[dict] = []
    if con_cadencias:
        vencidas, fallidas, ok = cadencias_vencidas(cur, workspace_id, ahora, arranque)
        for job in vencidas:
            # Savepoint propio: si falla dentro de la base, la transacción no
            # queda abortada para la escalera y el despacho que siguen.
            try:
                with cur.connection.transaction():
                    cadencias_encoladas += reloj.ejecutar_cadencia(
                        cur, workspace_id, job["nombre"], cal, ahora)
            except Exception as e:  # noqa: BLE001 -- se reporta, no se propaga
                # El cron ya era válido (pasó `cadencias_vencidas`): lo que
                # falló fue EJECUTARLA, causa distinta de un cron roto
                # (R4-002/R2-001/R3-005, revisión 2026-09-28+1).
                fallidas.append((job, e, CAUSA_FALLO_EJECUCION))
                ok = [j for j in ok if j["id"] != job["id"]]

    escalera_encoladas = reloj.ejecutar_escalera(cur, workspace_id, cal, ahora)
    # T9-H19e: antes de despachar, para que el aviso de un mensaje huérfano salga
    # en esta misma pasada. Con su savepoint: una falla del barrido no frena el
    # despacho y se reporta (`huerfanos_fallo`), nunca en silencio.
    huerfanos_avisados = 0
    huerfanos_fallo = None
    try:
        with cur.connection.transaction():
            huerfanos_avisados = huerfanos.barrer(cur, workspace_id, ahora)
    except Exception as e:  # noqa: BLE001 -- se reporta, no se propaga
        huerfanos_fallo = e
    resumen = despachar(cur, workspace_id, transporte, cal, ahora, lote)
    resumen["cadencias_encoladas"] = cadencias_encoladas
    resumen["escalera_encoladas"] = escalera_encoladas
    resumen["huerfanos_avisados"] = huerfanos_avisados
    resumen["huerfanos_fallo"] = huerfanos_fallo
    resumen["cadencias_fallidas"] = fallidas
    resumen["cadencias_ok"] = ok
    return resumen


def despachar_admin(conn, transporte_admin, ahora: datetime,
                    lote: int = 50) -> dict[str, int]:
    """Una pasada de `despachar_avisos_admin`, con su propio commit. Lo
    llaman `Escucha.tareas_de_fondo` (con el transporte que ya resolvió
    sondeando) y `Ciclo.tick` (con uno cacheado por token, sin sondear)."""
    with admin(conn) as cur:
        resumen = despachar_avisos_admin(cur, transporte_admin, ahora, lote)
    conn.commit()
    return resumen


# ---------------------------------------------------------------------------
# Reporte deduplicado: cada incidente fanea un aviso a la administración
# (`incidentes.registrar_incidente`) -- repetirlo cada pasada sería un
# aluvión. Se reporta una vez por `(workspace_id, clave)` mientras la falla
# sigue igual, y de nuevo sólo si se recuperó y volvió a fallar.
# ---------------------------------------------------------------------------

class SupresorDeRepetidos:
    def __init__(self) -> None:
        self._activas: set[tuple] = set()

    def debe_reportar(self, clave: tuple) -> bool:
        """Marca y decide en un solo paso -- para un aviso que no tiene nada
        más que escribir aparte (sólo consola, sin incidente en la base:
        p. ej. cuando ni hay conexión para intentarlo)."""
        if clave in self._activas:
            return False
        self._activas.add(clave)
        return True

    def activa(self, clave: tuple) -> bool:
        """Sólo consulta, sin marcar (R3-006, revisión 2026-09-28+1): la
        usa `reportar_fallo`, que necesita decidir ANTES de escribir el
        incidente, y marcar recién si la escritura salió bien."""
        return clave in self._activas

    def marcar(self, clave: tuple) -> None:
        self._activas.add(clave)

    def recuperada(self, clave: tuple) -> None:
        self._activas.discard(clave)


def _revertir_best_effort(conn) -> None:
    """`rollback` best-effort compartido -- antes había una copia idéntica
    en `Ciclo._revertir` y otra en `Escucha._revertir` (R2-004, revisión
    2026-09-28+1). Nunca deja escapar una excepción propia, y tolera
    `conn=None` (todavía no se pudo conectar)."""
    if conn is None:
        return
    try:
        conn.rollback()
    except Exception:  # noqa: BLE001
        pass


def _cerrar_best_effort(conn) -> None:
    """Cierra una conexión antes de descartarla -- best-effort, mismo
    patrón que `_revertir_best_effort`. Sin esto, `Ciclo.tick` descartaba
    `self._conn` (lo pone en `None` para que la próxima pasada reconecte)
    sin cerrar la conexión vieja: una falla persistente al listar espacios
    activos filtraba una conexión por pasada, para siempre (R3-002,
    revisión 2026-09-28). Nunca deja escapar una excepción propia, y
    tolera `conn=None`."""
    if conn is None:
        return
    try:
        conn.close()
    except Exception:  # noqa: BLE001
        pass


def _resumen_vacio() -> dict:
    """Resumen sin ningún efecto -- lo usa quien necesita seguir el resto
    del ciclo (reportar cadencias rotas, avisar admin) después de una
    pasada que falló entera y no llegó a construir uno real (R2-003,
    revisión 2026-09-28+1)."""
    return {"enviados": 0, "pospuestos": 0, "fallidos": 0, "descartados": 0,
            "retenidos": 0,
            "cadencias_encoladas": 0, "escalera_encoladas": 0,
            "huerfanos_avisados": 0, "huerfanos_fallo": None,
            "cadencias_fallidas": [], "cadencias_ok": []}


def reportar_fallo(conn, supresor: SupresorDeRepetidos, workspace_id: str | None,
                   clave: str, descripcion: str, error: Exception) -> bool:
    """Un incidente por `(workspace_id, clave)` mientras esa falla persiste.
    Nunca deja escapar una excepción propia -- si ni esto funciona, sólo se
    pierde el aviso. Devuelve si esta vez se reportó de verdad.

    La clave se marca como reportada sólo DESPUÉS de escribir el incidente
    (R3-006, revisión 2026-09-28+1): antes se marcaba antes de escribir, así
    que si la escritura fallaba esa falla quedaba deduplicada para siempre,
    sin que ni el reintento de la próxima pasada pudiera volver a
    registrarla. Si la escritura falla, se avisa por consola -- nunca en
    silencio -- y se devuelve `False` para que la próxima pasada reintente."""
    tupla = (workspace_id, clave)
    if supresor.activa(tupla):
        return False
    try:
        with admin(conn) as cur:
            registrar_incidente(
                cur, workspace_id, descripcion, severidad="alta",
                referencia_cruda=str(error)[:2000], etapa="ciclo_de_fondo")
        conn.commit()
    except Exception as exc:  # noqa: BLE001 -- no se marca: se reintenta la próxima vez
        _revertir_best_effort(conn)
        print(f"  ! no se pudo registrar el incidente de fondo "
             f"({type(exc).__name__}): {descripcion}")
        return False
    supresor.marcar(tupla)
    return True


# Causa de una cadencia en `cadencias_fallidas`: distingue un cron que
# APScheduler rechazó de uno válido que falló al EJECUTARSE
# (R4-002/R2-001/R3-005, revisión 2026-09-28+1) -- antes las dos quedaban
# reportadas como "cron inválido", aunque el cron fuera correcto.
CAUSA_CRON_INVALIDO = "cron_invalido"
CAUSA_FALLO_EJECUCION = "fallo_en_ejecucion"


def _texto_cadencia_fallida(causa: str, nombre: str, slug: str,
                            error: Exception) -> tuple[str, str]:
    tipo = type(error).__name__
    if causa == CAUSA_CRON_INVALIDO:
        return (
            f"Cron inválido en la cadencia '{nombre}' de '{slug}' ({tipo}).",
            f"  ! la cadencia '{nombre}' de '{slug}' tiene un cron inválido: {tipo}")
    return (
        f"La cadencia '{nombre}' de '{slug}' falló al ejecutarse ({tipo}).",
        f"  ! la cadencia '{nombre}' de '{slug}' falló al ejecutarse: {tipo}")


def reportar_cadencias_rotas(conn, supresor: SupresorDeRepetidos,
                             workspace_id: str, slug: str, resumen: dict, *,
                             imprimir=print) -> None:
    """Aísla y reporta -- deduplicado -- lo que `cadencias_vencidas` encontró
    roto en este espacio, sin frenar el resto del ciclo. Única implementación
    compartida por `Ciclo.tick` y `Escucha.tareas_de_fondo` (R2-002, revisión
    2026-09-28+1): antes cada uno tenía su propia copia, y la de
    `tareas_de_fondo` imprimía en cada pasada sin mirar si `reportar_fallo`
    de verdad reportó."""
    fallo = resumen.pop("huerfanos_fallo", None)
    clave_barrido = "barrido_huerfanos"
    if fallo is None:
        supresor.recuperada((workspace_id, clave_barrido))
    elif reportar_fallo(
            conn, supresor, workspace_id, clave_barrido,
            f"Falló el barrido de mensajes huérfanos de '{slug}' "
            f"({type(fallo).__name__}).", fallo):
        imprimir(f"  ! el barrido de mensajes huérfanos de '{slug}' falló: "
                 f"{type(fallo).__name__}")
    for job in resumen.pop("cadencias_ok", []):
        nombre = job["nombre"]
        supresor.recuperada((workspace_id, f"cadencia:{nombre}:{CAUSA_CRON_INVALIDO}"))
        supresor.recuperada((workspace_id, f"cadencia:{nombre}:{CAUSA_FALLO_EJECUCION}"))
    for job, error, causa in resumen.pop("cadencias_fallidas", []):
        nombre = job["nombre"]
        descripcion, texto_consola = _texto_cadencia_fallida(causa, nombre, slug, error)
        clave = f"cadencia:{nombre}:{causa}"
        if reportar_fallo(conn, supresor, workspace_id, clave, descripcion, error):
            imprimir(texto_consola)


# Intervalo del job único que arma `reloj.montar` para `servir`. Acotado y
# corto a propósito: en modo webhook, la respuesta a una persona también
# sale por esta misma pasada (`message_outbox`), así que el intervalo es la
# demora máxima hasta que alguien la recibe -- similar al ciclo de
# `escuchar`, que repasa cada ~25s por el `timeout` del long poll.
INTERVALO_SEGUNDOS = 20


class Ciclo:
    """Ciclo de fondo para `servir`: todos los espacios activos con token de
    bot, más el aviso a la administración una vez por pasada.

    Nunca deja que la falla de un espacio (ni de una sola cadencia rota
    dentro de él) frene a los demás ni al ciclo -- cada falla queda como
    incidente, deduplicado por `(espacio, clave)` mientras persiste. Cachea
    un `TransporteTelegram` por slug (y uno para "admin"): nunca abre un
    cliente HTTP nuevo por pasada, y cierra el anterior si el token cambió."""

    def __init__(self, conn_factory, *, arranque: datetime | None = None) -> None:
        self.conn_factory = conn_factory
        self.arranque = arranque or datetime.now(timezone.utc)
        self._fallas = SupresorDeRepetidos()
        self._transportes: dict[str, tuple[str, TransporteTelegram]] = {}
        # Una sola conexión por CICLO, no una nueva por pasada
        # (R4-003/R3-003, revisión 2026-09-28+1): `_conectar` la reusa
        # mientras siga viva y reconecta sola si se cerró o se descartó.
        self._conn = None

    def _transporte_de(self, slug: str, token: str) -> TransporteTelegram:
        actual = self._transportes.get(slug)
        if actual is not None and actual[0] == token:
            return actual[1]
        if actual is not None:
            actual[1].cerrar()
        nuevo = TransporteTelegram(token)
        self._transportes[slug] = (token, nuevo)
        return nuevo

    def _conectar(self):
        if self._conn is None or self._conn.closed:
            self._conn = self.conn_factory()
        return self._conn

    def tick(self, ahora: datetime | None = None, *,
            con_cadencias: bool = True, lote: int = 50) -> dict[str, dict]:
        ahora = ahora or datetime.now(timezone.utc)
        resultados: dict[str, dict] = {}

        conn = None
        try:
            conn = self._conectar()
            with admin(conn) as cur:
                cur.execute("select id, slug from workspace where activo order by slug")
                activos = cur.fetchall()
            conn.commit()
            self._fallas.recuperada((None, "listar_espacios"))
        except Exception as e:  # noqa: BLE001
            # La conexión puede haber quedado inservible: se reporta con ella
            # y después, pase lo que pase con el reporte, se cierra y se
            # descarta para que la pasada siguiente reconecte.
            _revertir_best_effort(conn)
            try:
                if conn is None:
                    # Sin conexión no se puede escribir el incidente: se
                    # deduplica en memoria y sólo se imprime.
                    if self._fallas.debe_reportar((None, "listar_espacios")):
                        print(f"  ! el ciclo de fondo no pudo conectar a la base "
                             f"({type(e).__name__}).")
                elif reportar_fallo(
                        conn, self._fallas, None, "listar_espacios",
                        f"Falló el ciclo de fondo al listar espacios activos "
                        f"({type(e).__name__}).", e):
                    print(f"  ! el ciclo de fondo no pudo listar espacios activos: "
                         f"{type(e).__name__}")
            finally:
                _cerrar_best_effort(conn)
                self._conn = None
            resultados["_error"] = {"tipo": type(e).__name__}
            return resultados

        tokens = config.espacios_con_token()
        for w in activos:
            slug, ws_id = w["slug"], str(w["id"])
            token = tokens.get(slug)
            if token is None:
                resultados[slug] = {"error": "sin_token_de_bot"}
                if reportar_fallo(
                        conn, self._fallas, ws_id, "sin_token",
                        f"'{slug}' está activo sin PRISMA_BOT_TOKEN_"
                        f"{slug.upper()} en el entorno.",
                        LookupError(f"Falta PRISMA_BOT_TOKEN_{slug.upper()}")):
                    print(f"  ! '{slug}' está activo sin PRISMA_BOT_TOKEN_"
                         f"{slug.upper()}: no se despacha su cola hasta que "
                         "se configure.")
                continue
            self._fallas.recuperada((ws_id, "sin_token"))

            try:
                transporte = self._transporte_de(slug, token)
                with espacio(conn, ws_id) as cur:
                    resumen = ejecutar_ciclo_espacio(
                        cur, ws_id, transporte, ahora, self.arranque,
                        con_cadencias=con_cadencias, lote=lote)
                conn.commit()
                self._fallas.recuperada((ws_id, "tick"))
                reportar_cadencias_rotas(conn, self._fallas, ws_id, slug, resumen)
                resultados[slug] = resumen
            except Exception as e:  # noqa: BLE001
                _revertir_best_effort(conn)
                resultados[slug] = {"error": type(e).__name__}
                if reportar_fallo(
                        conn, self._fallas, ws_id, "tick",
                        f"Falló el ciclo de fondo de '{slug}' "
                        f"({type(e).__name__}).", e):
                    print(f"  ! el ciclo de fondo de '{slug}' falló: {type(e).__name__}")

        try:
            token_admin = config.token_bot("admin")
        except LookupError:
            token_admin = None
        if token_admin:
            try:
                transporte_admin = self._transporte_de("admin", token_admin)
                resultados["_admin"] = despachar_admin(conn, transporte_admin, ahora, lote)
                self._fallas.recuperada((None, "admin"))
            except Exception as e:  # noqa: BLE001
                _revertir_best_effort(conn)
                resultados["_admin"] = {"error": type(e).__name__}
                reportar_fallo(
                    conn, self._fallas, None, "admin",
                    f"Falló el aviso a la administración ({type(e).__name__}).", e)

        return resultados
