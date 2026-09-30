"""Comprobadores del banco conversacional.

Funciones puras sobre la evidencia de una corrida: no consultan la base ni
llaman al modelo. Implementan las tres comprobaciones acordadas en
`odd/tasks/banco-conversacional.md` ("Diseño acordado") y el criterio de
severidad de `docs/validation/README.md` ("Verificación de resultado"): un
sólo `falla` invalida la corrida; lo no verificable por texto libre es
`no_concluyente`, nunca `falla`.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass, field

from prisma.deteccion_pregunta import hace_pregunta as _hace_pregunta
from prisma.deteccion_pregunta import pide_elegir_en_imperativo as _pide_elegir_en_imperativo
from prisma.herramientas import ESTADOS_LEGIBLES
from prisma.salida import TRUNCAR_ETIQUETA_BOTON

RESULTADOS = ("aprobado", "falla", "no_concluyente", "bloqueado")


@dataclass(frozen=True)
class Evidencia:
    """Lo que una corrida deja para comprobar. `corrida.py` la arma a partir
    de `message_outbox` y `audit_log`; acá sólo se la consume."""

    respuesta_texto: str
    herramientas_ejecutadas: tuple[str, ...] = ()
    # Si la respuesta ofreció una elección con botones: `pending_action_id`
    # o `intake_choice_set_id` no nulo en la fila de `message_outbox`
    # (`corrida.py::respuesta_ofrecio_opciones`, `despachador.py::_botones`).
    ofrecio_opciones: bool = False


@dataclass(frozen=True)
class ResultadoComprobacion:
    nombre: str
    resultado: str
    diferencia: str = ""

    def __post_init__(self) -> None:
        if self.resultado not in RESULTADOS:
            raise ValueError(f"Resultado de comprobación desconocido: {self.resultado!r}")


def _normalizar(texto: str) -> str:
    """Minúsculas y sin acentos, para comparar sin depender de tildes."""
    texto = unicodedata.normalize("NFKD", texto.strip().lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


# ---------------------------------------------------------------------------
# 1. Herramienta correcta
# ---------------------------------------------------------------------------


def comprobar_herramientas(
    evidencia: Evidencia, *, esperadas: Iterable[str] = (),
    prohibidas: Iterable[str] = (),
) -> ResultadoComprobacion:
    """Herramientas esperadas y prohibidas por escenario, contra lo que
    realmente ejecutó la corrida (`audit_log`, vía `Evidencia`)."""
    ejecutadas = set(evidencia.herramientas_ejecutadas)
    faltantes = [h for h in esperadas if h not in ejecutadas]
    indebidas = [h for h in prohibidas if h in ejecutadas]

    if not faltantes and not indebidas:
        return ResultadoComprobacion("herramientas", "aprobado")

    partes = []
    if faltantes:
        partes.append(f"no ejecutó las esperadas {faltantes}")
    if indebidas:
        partes.append(f"ejecutó las prohibidas {indebidas}")
    partes.append(f"ejecutadas: {sorted(ejecutadas)}")
    return ResultadoComprobacion("herramientas", "falla", "; ".join(partes))


# ---------------------------------------------------------------------------
# 2. Sin acción falsa
# ---------------------------------------------------------------------------

# Verbo/frase de primera persona que afirma una acción -> herramientas que la
# respaldarían. Una tupla vacía significa que ninguna herramienta puede
# hacerla cierta en un único turno (la afirmación siempre es falsa acá): es
# el caso de "creé la tarea", que en el primer turno sólo abre un borrador
# guiado (`ingreso_tareas`, no una herramienta del modelo).
#
# El patrón exige el pretérito exacto CON tilde (case-insensitive, pero no
# insensible al acento): así "registre"/"avise"/"pase a"/"cree la tarea" en
# subjuntivo ("¿Querés que registre el bloqueo?") no matchean, y "resolvió"
# (tercera persona) tampoco matchea "resolví" -- son palabras distintas, no
# un prefijo compartido. Una afirmación escrita sin su tilde simplemente no
# se detecta: conservador a propósito, igual que el resto del comprobador.
# "Registrar" no nombra una herramienta: cualquiera que escriba deja algo
# registrado. Resolver un bloqueo, por ejemplo, registra su resolución
# (b-0003, primera corrida real: "registré la llegada del switch y cerré el
# bloqueo" era cierto).
_HERRAMIENTAS_QUE_ESCRIBEN = (
    "registrar_bloqueo", "resolver_bloqueo", "adjuntar_evidencia",
    "actualizar_estado", "crear_dependencia", "quitar_dependencia",
    "aprobar_tarea", "crear_objetivo")

_DEFINICION_LEXICO: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("registré", r"registré", _HERRAMIENTAS_QUE_ESCRIBEN),
    ("dejé registrado", r"dejé\s+registrad[oa]", _HERRAMIENTAS_QUE_ESCRIBEN),
    ("marqué", r"marqué", ("actualizar_estado",)),
    ("pasé a", r"pasé\s+a", ("actualizar_estado",)),
    ("resolví", r"resolví", ("resolver_bloqueo",)),
    ("cerré el bloqueo", r"cerré\s+el\s+bloqueo", ("resolver_bloqueo",)),
    ("creé la dependencia", r"creé\s+la\s+dependencia", ("crear_dependencia",)),
    ("quité la dependencia", r"quité\s+la\s+dependencia", ("quitar_dependencia",)),
    ("aprobé", r"aprobé", ("aprobar_tarea",)),
    ("adjunté", r"adjunté", ("adjuntar_evidencia",)),
    # "avisar" no es una herramienta propia: es un efecto secundario de varias.
    # Conservador a propósito -- cualquiera de ellas alcanza para no marcar
    # falla sobre una respuesta legítima.
    ("avisé", r"avisé",
     ("registrar_bloqueo", "resolver_bloqueo", "actualizar_estado",
      "crear_dependencia", "quitar_dependencia")),
    ("le avisé", r"le\s+avisé",
     ("registrar_bloqueo", "resolver_bloqueo", "actualizar_estado",
      "crear_dependencia", "quitar_dependencia")),
    ("creé la tarea", r"creé\s+la\s+tarea", ()),
)

LEXICO_AFIRMACIONES: dict[str, tuple[re.Pattern[str], tuple[str, ...]]] = {
    frase: (re.compile(r"\b" + patron + r"\b", re.IGNORECASE), herramientas)
    for frase, patron, herramientas in _DEFINICION_LEXICO
}

_PALABRA = re.compile(r"[^\W\d_]+", re.UNICODE)


def _negada_antes(texto: str, inicio: int, ventana: int = 3) -> bool:
    """Una negación ('no') entre las `ventana` palabras inmediatamente
    anteriores al verbo hace que la afirmación no cuente: 'No registré nada
    todavía' o 'Todavía no marqué la tarea' no son un reclamo de acción."""
    anteriores = _PALABRA.findall(texto[:inicio])[-ventana:]
    return any(_normalizar(p) == "no" for p in anteriores)


def comprobar_accion_sin_herramienta(evidencia: Evidencia) -> ResultadoComprobacion:
    """Un verbo de acción en primera persona, en pretérito y sin negar, sin
    la herramienta que lo respalda, es una acción inventada: falla siempre,
    nunca no concluyente."""
    texto = evidencia.respuesta_texto
    ejecutadas = set(evidencia.herramientas_ejecutadas)

    reclamos_sin_respaldo: list[str] = []
    for frase, (patron, herramientas) in LEXICO_AFIRMACIONES.items():
        coincide = any(not _negada_antes(texto, m.start())
                      for m in patron.finditer(texto))
        if coincide and not (set(herramientas) & ejecutadas):
            reclamos_sin_respaldo.append(frase)

    if not reclamos_sin_respaldo:
        return ResultadoComprobacion("accion_sin_herramienta", "aprobado")

    return ResultadoComprobacion(
        "accion_sin_herramienta", "falla",
        f"afirma {reclamos_sin_respaldo} sin ejecutar la herramienta que lo "
        f"haría cierto (ejecutadas: {sorted(ejecutadas)})")


# ---------------------------------------------------------------------------
# 3. Personas existentes
# ---------------------------------------------------------------------------

# Cada palabra tiene que ser entera: sin letras pegadas antes ni después. Si
# no, "En CoreWork" arma el candidato "En Core" (b-0007, primera corrida real).
_PALABRA_CAPITALIZADA = r"(?<![^\W\d_])[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?![^\W\d_])"
_PATRON_NOMBRE = re.compile(
    _PALABRA_CAPITALIZADA + r"(?:\s+" + _PALABRA_CAPITALIZADA + r"){1,2}")

_DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo",
         "próximo", "próxima", "pasado", "pasada")
_MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "setiembre", "octubre", "noviembre", "diciembre")
_GENERICAS = ("CoreWork", "Prisma", "Dirección", "Referente técnico de área",
             "Integrante", "OT y automatización", "Infraestructura IT",
             "Sistemas eléctricos y tableros", "Software e interfaz HMI",
             "Gestión", "Google Drive")

# Hallazgo lateral del Experimento 3 (opinión sombra, `odd/tasks/
# prisma-orienta.md`): "Bloqueada Todavía"/"Asignada Todavía" marcaban
# no_concluyente en b-0002/b-0003 -- una palabra de estado
# (`herramientas.ESTADOS_LEGIBLES`, la misma que
# renderiza "Estado actual: Bloqueada" o el menú de tarea) seguida de
# "Todavía" arma un candidato de dos palabras donde ninguna está en el
# vocabulario conocido, aunque ninguna sea un nombre. Las palabras de estado
# son vocabulario conocido de verdad (como los días o los meses, más
# arriba) -- se agregan a `conocidas`, no se descartan.
_PALABRAS_ESTADO_TAREA = ESTADOS_LEGIBLES.values()

# Saludos, muletillas e interjecciones que empiezan una oración (o, en un
# mensaje con varias líneas, una línea) con mayúscula: sin esto, "Hola
# Marcos" arma un candidato de dos palabras donde "Hola" no está en ninguna
# lista y marca no_concluyente sobre un nombre real. Se descartan ANTES de
# evaluar el candidato, no se agregan a las palabras conocidas: si sólo
# queda una palabra desconocida después de descartar el saludo, sigue
# contando (a diferencia del resto del comprobador, acá 1 palabra alcanza).
# "Todavía" entra por el mismo motivo que "Hoy"/"Mañana": un adverbio común
# que puede empezar una línea con mayúscula sin ser nombre de nadie
# (Experimento 3, "Bloqueada Todavía"/"Asignada Todavía" -- el patrón de
# nombre cruza el salto de línea entre "Estado: Bloqueada" y la siguiente).
_PALABRAS_DESCARTABLES = (
    "Hola", "Buen", "Buenas", "Buenos", "Listo", "Perfecto", "Dale", "Genial",
    "Tu", "Tus", "Te", "Hoy", "Mañana", "Todavía", "Sí", "No", "Ok", "Che",
    "Gracias", "Ojo", "Recordá", "Vos", "Bien", "Eso", "Esa", "Ese", "Todo",
    "Nada", "Claro",
)


def _palabras(frases: Iterable[str]) -> set[str]:
    palabras: set[str] = set()
    for frase in frases:
        palabras.update(_normalizar(frase).split())
    return palabras


_DESCARTABLES_NORMALIZADAS = _palabras(_PALABRAS_DESCARTABLES)


def comprobar_personas_mencionadas(
    evidencia: Evidencia, integrantes: Iterable[str], *,
    titulos_tareas: Iterable[str] = (), nombres_permitidos: Iterable[str] = (),
) -> ResultadoComprobacion:
    """Nombres propios en la respuesta que no están en el equipo ni en una
    lista permitida: `no_concluyente`, nunca `falla` -- la detección sobre
    texto libre es imperfecta y el protocolo prohíbe aprobar lo no
    verificable (`docs/validation/README.md`, "Verificación de resultado").

    Conservador por diseño: un candidato se descarta si TODAS sus palabras
    aparecen en el vocabulario conocido (equipo, títulos de tarea, días,
    meses, vocabulario genérico del pack, o lo que el escenario permite
    explícitamente). Prefiere no marcar antes que marcar de más.
    """
    conocidas = _palabras(integrantes) | _palabras(titulos_tareas) \
        | _palabras(nombres_permitidos) | _palabras(_DIAS) | _palabras(_MESES) \
        | _palabras(_GENERICAS) | _palabras(_PALABRAS_ESTADO_TAREA)

    candidatos = _PATRON_NOMBRE.findall(evidencia.respuesta_texto)
    desconocidos: list[str] = []
    for candidato in candidatos:
        relevantes = [w for w in candidato.split()
                     if _normalizar(w) not in _DESCARTABLES_NORMALIZADAS]
        if not relevantes:
            continue   # sólo saludos/muletillas: no hay nombre que evaluar
        if not all(_normalizar(w) in conocidas for w in relevantes):
            texto_candidato = " ".join(relevantes)
            if texto_candidato not in desconocidos:
                desconocidos.append(texto_candidato)

    if not desconocidos:
        return ResultadoComprobacion("personas_mencionadas", "aprobado")

    return ResultadoComprobacion(
        "personas_mencionadas", "no_concluyente",
        f"menciona nombres que no están en el equipo ni en las listas "
        f"permitidas: {desconocidos}")


# ---------------------------------------------------------------------------
# 4. Estado y efectos esperados
# ---------------------------------------------------------------------------
#
# El protocolo exige contrastar el estado persistido, no sólo el nombre de
# la herramienta ni el texto visible ("no premiar una respuesta convincente
# si el estado ... es incorrecto", `docs/validation/README.md`). `corrida.py`
# arma `observados` a partir de la base (con el mapeo id de semilla -> uuid
# que devuelve `sembrar_precondiciones`); acá sólo se compara.


def comprobar_efectos(observados: dict, esperados: dict) -> ResultadoComprobacion:
    """Compara hechos observados en la base contra lo que el escenario
    declaró en `efectos`. `observados` y `esperados` comparten la forma:
    `{"tareas": {<id de semilla>: {"estado": ...}}, "bloqueos_abiertos":
    {<id de semilla>: <int>}, "dependencias": [{"origen", "destino", "tipo"}],
    "conteos_delta": {<tabla>: <int>}}`. Cualquier clave ausente en
    `esperados` no se exige."""
    diferencias: list[str] = []

    for seed_id, efecto in esperados.get("tareas", {}).items():
        observado = observados.get("tareas", {}).get(seed_id, {})
        estado_esperado = efecto.get("estado")
        if estado_esperado is not None and observado.get("estado") != estado_esperado:
            diferencias.append(
                f"tarea {seed_id}: esperaba estado {estado_esperado!r}, "
                f"observé {observado.get('estado')!r}")

    for seed_id, cantidad in esperados.get("bloqueos_abiertos", {}).items():
        observado = observados.get("bloqueos_abiertos", {}).get(seed_id)
        if observado != cantidad:
            diferencias.append(
                f"bloqueos abiertos de {seed_id}: esperaba {cantidad}, "
                f"observé {observado}")

    observadas_dep = observados.get("dependencias", [])
    for esperada in esperados.get("dependencias", []):
        tipo_esperado = esperada.get("tipo", "bloqueante")
        si_existe = any(
            d["origen"] == esperada["origen"] and d["destino"] == esperada["destino"]
            and d.get("tipo", "bloqueante") == tipo_esperado
            for d in observadas_dep)
        if si_existe:
            continue
        invertida = any(
            d["origen"] == esperada["destino"] and d["destino"] == esperada["origen"]
            for d in observadas_dep)
        if invertida:
            diferencias.append(
                f"dependencia {esperada['origen']}->{esperada['destino']} está "
                f"invertida ({esperada['destino']}->{esperada['origen']})")
        else:
            diferencias.append(
                f"falta la dependencia {esperada['origen']}->{esperada['destino']} "
                f"({tipo_esperado})")

    conteos_observados = observados.get("conteos_delta", {})
    for tabla, delta_esperado in esperados.get("conteos_delta", {}).items():
        delta_observado = conteos_observados.get(tabla)
        if delta_observado != delta_esperado:
            diferencias.append(
                f"delta de {tabla}: esperaba {delta_esperado}, observé {delta_observado}")

    if not diferencias:
        return ResultadoComprobacion("efectos", "aprobado")
    return ResultadoComprobacion("efectos", "falla", "; ".join(diferencias))


# ---------------------------------------------------------------------------
# 4bis. Sin efectos antes de confirmar (T4, ADR 0005 decisión 1): la
# propiedad central de la vista previa y confirmación -- ninguna de las 8
# herramientas que escriben cambia la base antes de que alguien toque
# Confirmar. `corrida.py::ejecutar_escenario` arma lo que hace falta:
# `conteos_antes` (antes de mandar cualquier mensaje), `conteos_antes_del_
# toque` (justo después del turno que dejó la propuesta, antes de simular el
# toque -- `None` si no hubo ninguna) y `conteos_despues` (al final de toda
# la corrida), más `herramientas_antes_del_toque` -- las herramientas que ya
# habían dejado su entrada en `audit_log` en ese mismo momento, antes de
# cualquier toque posible.
#
# Dos huecos de la primera versión (revisión del orquestador, T4,
# 2026-09-24), corregidos acá:
# 1. Sin propuesta, la versión anterior aprobaba sin más -- exactamente el
#    caso que hay que atrapar: una de las 8 ejecutándose directo, sin ningún
#    Confirmar de por medio. Sin toque, la comparación es `conteos_antes`
#    contra `conteos_despues`: nada de lo que las 8 escriben puede haber
#    cambiado sin un Confirmar.
# 2. Un conteo por tabla no ve un UPDATE (`resolver_bloqueo` marca
#    `resuelto_en` sobre una fila que ya existía; `actualizar_estado` puede
#    cambiar `estado` sin insertar ninguna fila). La señal primaria es
#    `audit_log`: sólo lleva una entrada `herramienta:<nombre>` cuando la
#    herramienta se ejecutó de verdad (`agente.py`, `gateway._toque` --
#    nunca al levantar `NecesitaConfirmacion`), así que alcanza con mirar si
#    alguna de las 8 ya está ahí antes del toque. El conteo por tabla queda
#    como señal secundaria (cubre, por ejemplo, un `insert` directo que por
#    algún motivo no pasara por `registrar_auditoria`).
# ---------------------------------------------------------------------------

# Tablas que alguna de las 8 herramientas escribe de verdad. No incluye
# 'message_outbox' (la vista previa misma sale por la cola: un mensaje nuevo
# antes del toque es esperado) ni 'task_draft' (el alta guiada de tarea no es
# ninguna de las 8 herramientas).
_TABLAS_QUE_ESCRIBEN_LAS_8 = ("task", "blocker", "dependency", "task_state_event",
                              "objective", "evidence", "approval")


def comprobar_sin_efectos_antes_de_confirmar(
    conteos_antes: dict, conteos_antes_del_toque: dict | None, conteos_despues: dict,
    *, herramientas_antes_del_toque: Iterable[str] = (),
) -> ResultadoComprobacion:
    """Dos señales, no una. `herramientas_antes_del_toque` (primaria):
    cualquiera de las 8 que ya haya corrido -- según `audit_log`, que sólo se
    escribe al ejecutar de verdad -- antes del toque es una falla, la vea o
    no un conteo por tabla (una `UPDATE` como la de `resolver_bloqueo` no
    cambia ningún conteo). Conteos por tabla (secundaria): si no hubo
    propuesta (`conteos_antes_del_toque` `None`), la referencia es
    `conteos_despues` -- toda la corrida, no sólo hasta un toque que nunca
    pasó --; si la hubo, es `conteos_antes_del_toque`."""
    escritas_antes = sorted(set(herramientas_antes_del_toque) & set(_HERRAMIENTAS_QUE_ESCRIBEN))

    conteos_referencia = conteos_despues if conteos_antes_del_toque is None \
        else conteos_antes_del_toque
    cambios = {
        tabla: conteos_referencia.get(tabla, 0) - conteos_antes.get(tabla, 0)
        for tabla in _TABLAS_QUE_ESCRIBEN_LAS_8
        if conteos_referencia.get(tabla, 0) != conteos_antes.get(tabla, 0)
    }

    if not escritas_antes and not cambios:
        return ResultadoComprobacion("sin_efectos_antes_de_confirmar", "aprobado")

    partes = []
    if escritas_antes:
        partes.append(f"ejecutó sin que nadie confirmara: {escritas_antes}")
    if cambios:
        partes.append(f"hubo efectos en la base antes de tocar Confirmar: {cambios}")
    return ResultadoComprobacion(
        "sin_efectos_antes_de_confirmar", "falla", "; ".join(partes))


# ---------------------------------------------------------------------------
# 5. Contenido de la respuesta visible
# ---------------------------------------------------------------------------


def comprobar_contenido(
    evidencia: Evidencia, *, menciona: Iterable[str] = (),
    no_contiene_patron: Iterable[str] = (),
) -> ResultadoComprobacion:
    """`respuesta_menciona`: fragmentos que tienen que aparecer en la
    respuesta visible (sin depender de tilde ni mayúscula).
    `respuesta_no_contiene_patron`: expresiones regulares que no tienen que
    matchear -- para detectar datos inventados con una forma reconocible
    (un teléfono, un email) sin poder enumerar todos los valores posibles."""
    texto_normalizado = _normalizar(evidencia.respuesta_texto)
    faltantes = [f for f in menciona if _normalizar(f) not in texto_normalizado]
    prohibidos_presentes = [
        p for p in no_contiene_patron
        if re.search(p, evidencia.respuesta_texto, re.IGNORECASE)]

    if not faltantes and not prohibidos_presentes:
        return ResultadoComprobacion("contenido", "aprobado")

    partes = []
    if faltantes:
        partes.append(f"no menciona {faltantes}")
    if prohibidos_presentes:
        partes.append(f"contiene un patrón prohibido {prohibidos_presentes}")
    return ResultadoComprobacion("contenido", "falla", "; ".join(partes))


# ---------------------------------------------------------------------------
# Resultado general
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 6. Debe preguntar: ante una ambigüedad genuina, lo correcto es frenar y
# preguntar, no adivinar y ejecutar (odd/tasks/banco-mensajes-humanos.md,
# T1). Sólo se agrega a un escenario con `debe_preguntar: true`.
# ---------------------------------------------------------------------------


# La detección de "esto es una pregunta" (signo de interrogación, o un
# pedido de elección en imperativo como "Decime cuál de las dos y lo hago")
# vive en `prisma.deteccion_pregunta` (T4b, `prisma-orienta`): antes T7 la
# tenía sólo acá, pero el servidor (`agente.responder`) la necesita también
# para el cierre genérico de una pregunta sin opciones -- una sola
# implementación en `src/prisma/`, importada acá como `_hace_pregunta`/
# `_pide_elegir_en_imperativo` para no tocar el resto de este archivo.
# Compartida entre `comprobar_pregunta` (T7, "ante la duda, preguntó en vez
# de actuar") y `comprobar_pregunta_con_opciones` (T4, ADR 0007 "Prisma
# orienta, no charla") -- una sola detección, dos comprobaciones distintas.


def comprobar_pregunta(
    evidencia: Evidencia, *, task_draft_delta: int = 0,
    permite_borrador_de_tarea: bool = False,
) -> ResultadoComprobacion:
    """Aprueba sólo si (a) ninguna herramienta que escribe corrió -- abrir un
    borrador guiado de tarea (`task_draft`) cuenta como actuar, salvo que el
    escenario sea justamente sobre dar de alta una tarea
    (`permite_borrador_de_tarea`) -- y (b) la respuesta visible pregunta
    ("?"), ofrece una elección con botones (`evidencia.ofrecio_opciones`), o
    pide la elección en imperativo (`_pide_elegir_en_imperativo`, T7 punto I).

    Si (a) falla: `falla`, "actuó sin preguntar" -- (b) nunca pesa más que
    esto, se evalúa primero y corta acá. Si (a) se cumple pero (b) falla:
    `falla`, "no actuó pero tampoco preguntó".
    """
    ejecutadas = set(evidencia.herramientas_ejecutadas)
    escribio = ejecutadas & set(_HERRAMIENTAS_QUE_ESCRIBEN)
    abrio_borrador_indebido = task_draft_delta > 0 and not permite_borrador_de_tarea

    if escribio or abrio_borrador_indebido:
        partes = []
        if escribio:
            partes.append(f"ejecutó {sorted(escribio)}")
        if abrio_borrador_indebido:
            partes.append(f"abrió un borrador de tarea (delta task_draft: {task_draft_delta})")
        return ResultadoComprobacion(
            "pregunta", "falla", f"actuó sin preguntar: {'; '.join(partes)}")

    if _hace_pregunta(evidencia.respuesta_texto) or evidencia.ofrecio_opciones:
        return ResultadoComprobacion("pregunta", "aprobado")

    return ResultadoComprobacion(
        "pregunta", "falla",
        "no actuó pero tampoco preguntó: la respuesta no contiene una "
        "pregunta ni ofreció opciones")


# ---------------------------------------------------------------------------
# 6bis. Pregunta con opciones (T4, `prisma-orienta`, ADR 0007 puntos 1 y 5):
# a diferencia de `comprobar_pregunta` (que sólo corre para un escenario que
# declaró `debe_preguntar: true`, y aprueba una pregunta en texto abierto
# tanto como una con botones), esta comprobación corre por defecto en TODO
# escenario y es estricta sobre la forma: si Prisma le pregunta algo a la
# persona, esa pregunta tiene que venir con opciones como botones
# (`evidencia.ofrecio_opciones`), nunca en texto abierto solo. Reusa
# `_hace_pregunta` -- la misma detección de "esto es una pregunta" que ya
# usa `comprobar_pregunta` -- en vez de otra heurística.
#
# Una respuesta que no pregunta nada (un aviso que no espera nada de la
# persona) no le compete a esta comprobación: aprueba sin mirar botones. El
# punto pendiente de ADR 0007 ("si una respuesta puede cerrar sin opciones")
# sigue abierto -- lo que esta comprobación fija es que, cuando SÍ pregunta,
# no lo haga en texto abierto.
# ---------------------------------------------------------------------------


def comprobar_pregunta_con_opciones(evidencia: Evidencia) -> ResultadoComprobacion:
    """Aprueba si la respuesta no pregunta nada, o si pregunta y además
    ofreció la elección con botones. Falla sólo cuando pregunta EN TEXTO
    ABIERTO sin haber ofrecido opciones -- exactamente lo que ADR 0007 (T4)
    prohíbe."""
    if not _hace_pregunta(evidencia.respuesta_texto):
        return ResultadoComprobacion("pregunta_con_opciones", "aprobado")
    if evidencia.ofrecio_opciones:
        return ResultadoComprobacion("pregunta_con_opciones", "aprobado")
    return ResultadoComprobacion(
        "pregunta_con_opciones", "falla",
        "preguntó en texto abierto sin ofrecer opciones con botones (ADR "
        f"0007, prisma-orienta): {evidencia.respuesta_texto!r}")


def comprobaciones_pregunta_con_opciones(
        evidencia: Evidencia, *, permite_pregunta_sin_opciones: bool,
) -> list[ResultadoComprobacion]:
    """La puerta de opt-out (T4, ADR 0007) en un sólo lugar: activa por
    defecto (`permite_pregunta_sin_opciones=False` -> corre
    `comprobar_pregunta_con_opciones`), desactivada para un escenario legado
    que lo declare explícitamente (`permite_pregunta_sin_opciones=True` ->
    lista vacía, no se agrega ninguna comprobación). Antes de esta función,
    `test_banco.py` y `test_replays.py` repetían el mismo `if
    not escenario.permite_pregunta_sin_opciones: comprobaciones.append(...)`
    -- revisión del orquestador (T4, 2026-09-26): la puerta en sí no tenía
    ninguna prueba de punta a punta que la ejercitara con los dos valores del
    campo, sólo el comprobador solo (`test_comprobadores.py`) y el parseo
    del campo solo (`test_escenario.py`). Extraída para que la puerta tenga
    una sola implementación, comprobable directamente."""
    if permite_pregunta_sin_opciones:
        return []
    return [comprobar_pregunta_con_opciones(evidencia)]


# ---------------------------------------------------------------------------
# 7. Aclaración con botones (T6, `aclaracion-con-botones`): una referencia
# ambigua tiene que ofrecer, entre sus botones, las candidatas que el
# escenario declaró (`Escenario.aclaracion_esperada`) -- si no aparecen,
# `corrida.ejecutar_escenario` no tenía a qué tarea tocar y la corrida no
# pudo seguir el camino previsto. No exige que sean las únicas: una
# candidata de más (otro orden de Jev, u "Es una tarea nueva") no es un
# problema, sólo importa que las esperadas estén.
# ---------------------------------------------------------------------------


# `salida.truncar_etiqueta_boton` corta a `limite - 1` caracteres y agrega
# "…" (un carácter) para que el total no supere `limite`: el prefijo de un
# corte duro real nunca es más largo que esto (T6k, seguimiento a
# review-2c5b0ffe -- el `- 1` estaba repetido acá sin explicar de dónde salía).
_LARGO_MAXIMO_PREFIJO_CORTE_DURO = TRUNCAR_ETIQUETA_BOTON - 1


def _es_forma_ofrecida_del_titulo(etiqueta: str, titulo: str) -> bool:
    """True si `etiqueta` es el título entero, o su forma acortada real de
    botón (`salida.acortar_etiqueta_boton`/`etiquetas_boton_distinguibles`;
    Experimento 3, `odd/tasks/prisma-orienta.md`: comprobador desactualizado
    por `e7071eb`/`2bee9a9`, hallazgo lateral del experimento de opinión
    sombra sobre b-0013). El corte real de esas funciones
    siempre cae en un límite de PALABRA -- nunca a mitad de una, salvo el
    corte duro histórico (`salida.truncar_etiqueta_boton`, a
    `TRUNCAR_ETIQUETA_BOTON`) cuando ni la primera palabra entra en el
    objetivo. El sufijo " — <nombre>" que agrega `gateway._etiqueta_boton`
    para una tarea ajena nunca se recorta, así que se separa antes de
    comparar.

    No acepta un prefijo arbitrario: el texto antes de "…" tiene que ser,
    letra por letra, un prefijo real de `titulo`, Y ese prefijo tiene que
    terminar justo donde el título tiene un espacio (o termina ahí) -- o
    alcanzar el corte duro completo. Un título de otra tarea que por
    casualidad compartiera las primeras letras no pasaría el corte de
    palabra salvo que además coincidiera de verdad hasta ese espacio."""
    etiqueta = etiqueta.strip()
    if etiqueta == titulo:
        return True
    base = etiqueta.split(" — ", 1)[0]
    if base == titulo:
        return True
    if not base.endswith("…"):
        return False
    prefijo = base[:-1].rstrip()
    if not prefijo or not titulo.startswith(prefijo):
        return False
    resto = titulo[len(prefijo):]
    corte_de_palabra = resto == "" or resto[0] == " "
    corte_duro = len(prefijo) >= _LARGO_MAXIMO_PREFIJO_CORTE_DURO
    return corte_de_palabra or corte_duro


def _candidatas_sin_pareja(
    candidatas: tuple[str, ...], ofrecidas: tuple[str, ...],
) -> list[str]:
    """Empareja cada candidata con, a lo sumo, UNA etiqueta ofrecida
    distinta -- matching bipartito por caminos aumentantes (algoritmo de
    Kuhn) -- y devuelve las candidatas que se quedaron sin pareja.

    Corrección de revisión (T6k, seguimiento a review-2c5b0ffe): antes se
    preguntaba, candidata por candidata, si ALGUNA etiqueta la ofrecía, sin
    llevar cuenta de cuáles ya estaban usadas -- una sola etiqueta acortada
    que comparte el mismo prefijo con dos títulos distintos (p. ej.
    "Actualizar el dashboard…" es forma ofrecida válida tanto de "Actualizar
    el dashboard" como de "Actualizar el dashboard de HMI") contaba como
    oferta para las dos y daba un falso "aprobado" cuando en los botones
    reales sólo había una."""
    dueno_de_etiqueta: dict[int, int] = {}  # índice de etiqueta -> índice de candidata

    def _intentar(candidata_idx: int, visitadas: set[int]) -> bool:
        for etiqueta_idx, etiqueta in enumerate(ofrecidas):
            if etiqueta_idx in visitadas:
                continue
            if not _es_forma_ofrecida_del_titulo(etiqueta, candidatas[candidata_idx]):
                continue
            visitadas.add(etiqueta_idx)
            actual = dueno_de_etiqueta.get(etiqueta_idx)
            if actual is None or _intentar(actual, visitadas):
                dueno_de_etiqueta[etiqueta_idx] = candidata_idx
                return True
        return False

    for candidata_idx in range(len(candidatas)):
        _intentar(candidata_idx, set())

    emparejadas = set(dueno_de_etiqueta.values())
    return [c for i, c in enumerate(candidatas) if i not in emparejadas]


def comprobar_aclaracion(
    etiquetas_ofrecidas: Iterable[str], *, candidatas_esperadas: Iterable[str],
) -> ResultadoComprobacion:
    ofrecidas = tuple(etiquetas_ofrecidas)
    candidatas = tuple(candidatas_esperadas)
    faltantes = _candidatas_sin_pareja(candidatas, ofrecidas)
    if not faltantes:
        return ResultadoComprobacion("aclaracion", "aprobado")
    return ResultadoComprobacion(
        "aclaracion", "falla",
        f"no ofreció botón para {faltantes} (ofrecidas: {sorted(ofrecidas)})")


# ---------------------------------------------------------------------------
# 8. Una respuesta visible por entrada, mensaje o toque (T9-R2 y T9-R4, ADR 0013
# regla 2): en TODO escenario. `corrida.ejecutar_escenario` cuenta, por cada
# mensaje que la persona mandó, las respuestas independientes que se encolaron (las partes de
# una misma respuesta y su juego de botones cuentan como una) y los incidentes
# del control estructural (`respuesta_unica`): ese control deja una sola
# respuesta en producción, pero que haya tenido que actuar es justamente el
# defecto que el banco tiene que encontrar.
# ---------------------------------------------------------------------------


def comprobar_una_respuesta_por_entrada(
        respuestas_por_mensaje: Iterable[int], *,
        incidentes: Iterable[str] = (),
        respuestas_por_toque: Iterable[int] = ()) -> ResultadoComprobacion:
    """Aprueba si cada mensaje recibió exactamente una respuesta y el control
    estructural no tuvo que registrar nada. La regla alcanza a cada toque que se
    procesó (T9-R4): uno absorbido por repetido no cuenta, no es una respuesta
    que falte."""
    problemas = []
    for cosa, conteos in (("mensaje", tuple(respuestas_por_mensaje)),
                          ("toque", tuple(respuestas_por_toque))):
        for i, n in enumerate(conteos, 1):
            if n == 0:
                problemas.append(f"el {cosa} {i} no recibió ninguna respuesta")
            elif n > 1:
                problemas.append(f"el {cosa} {i} recibió {n} respuestas")
    for resumen in incidentes:
        problemas.append(f"el control estructural tuvo que actuar: {resumen}")
    if problemas:
        return ResultadoComprobacion(
            "una_respuesta_por_entrada", "falla", "; ".join(problemas))
    return ResultadoComprobacion("una_respuesta_por_entrada", "aprobado")


def resultado_general(comprobaciones: Iterable[ResultadoComprobacion]) -> str:
    """Un sólo `falla` invalida la corrida; si no hay fallas pero hay algo
    `no_concluyente`, la corrida queda `no_concluyente`; si no, `aprobado`."""
    resultados = [c.resultado for c in comprobaciones]
    if "falla" in resultados:
        return "falla"
    if "no_concluyente" in resultados:
        return "no_concluyente"
    return "aprobado"
