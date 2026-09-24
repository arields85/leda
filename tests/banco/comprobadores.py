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

# Saludos, muletillas e interjecciones que empiezan una oración con
# mayúscula: sin esto, "Hola Marcos" arma un candidato de dos palabras donde
# "Hola" no está en ninguna lista y marca no_concluyente sobre un nombre
# real. Se descartan ANTES de evaluar el candidato, no se agregan a las
# palabras conocidas: si sólo queda una palabra desconocida después de
# descartar el saludo, sigue contando (a diferencia del resto del
# comprobador, acá 1 palabra alcanza).
_PALABRAS_DESCARTABLES = (
    "Hola", "Buen", "Buenas", "Buenos", "Listo", "Perfecto", "Dale", "Genial",
    "Tu", "Tus", "Te", "Hoy", "Mañana", "Sí", "No", "Ok", "Che", "Gracias",
    "Ojo", "Recordá", "Vos", "Bien", "Eso", "Esa", "Ese", "Todo", "Nada", "Claro",
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
        | _palabras(_GENERICAS)

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


# Pedido directo de la elección faltante en imperativo, sin "?" (T7, puntos
# I y N): el banco real mostraba a Prisma frenando y pidiendo la elección
# así -- "Decime cuál de las dos y lo hago" (b-0011), "decime cuál doy por
# resuelto" (b-0012), "Contame qué la está frenando" (b-0010), "decime qué
# preferís y lo muevo" (b-0011) -- y `comprobar_pregunta` lo marcaba como
# que no había preguntado. Lista chica y cerrada, a propósito: "decime"/
# "contame"/"confirmame" (verbos genéricos de pedir información) sólo
# cuentan cuando además aparece "cuál" o "qué" -- si no, cualquier cierre
# cordial ("decime si necesitás algo más") contaría como pregunta y
# debilitaría "actuó sin preguntar". "Elegí" es la excepción: el verbo mismo
# ya es un pedido de elección, sin necesitar "cuál"/"qué" al lado. "qué" se
# busca con borde de palabra (`\bque\b`), no como subcadena -- si no,
# "porque"/"aunque" en cualquier frase de cierre dispararían un falso
# positivo (T7, punto N).
_VERBOS_PEDIDO_ELECCION = ("decime", "decinos", "contame", "confirmame")
_MARCADOR_CUAL = "cual"
_MARCADOR_QUE = re.compile(r"\bque\b")


def _pide_elegir_en_imperativo(texto: str) -> bool:
    normalizado = _normalizar(texto)
    if "elegi" in normalizado:
        return True
    if not any(verbo in normalizado for verbo in _VERBOS_PEDIDO_ELECCION):
        return False
    return _MARCADOR_CUAL in normalizado or bool(_MARCADOR_QUE.search(normalizado))


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

    if ("?" in evidencia.respuesta_texto or evidencia.ofrecio_opciones
            or _pide_elegir_en_imperativo(evidencia.respuesta_texto)):
        return ResultadoComprobacion("pregunta", "aprobado")

    return ResultadoComprobacion(
        "pregunta", "falla",
        "no actuó pero tampoco preguntó: la respuesta no contiene una "
        "pregunta ni ofreció opciones")


# ---------------------------------------------------------------------------
# 7. Aclaración con botones (T6, `aclaracion-con-botones`): una referencia
# ambigua tiene que ofrecer, entre sus botones, las candidatas que el
# escenario declaró (`Escenario.aclaracion_esperada`) -- si no aparecen,
# `corrida.ejecutar_escenario` no tenía a qué tarea tocar y la corrida no
# pudo seguir el camino previsto. No exige que sean las únicas: una
# candidata de más (otro orden de Jev, u "Es una tarea nueva") no es un
# problema, sólo importa que las esperadas estén.
# ---------------------------------------------------------------------------


def comprobar_aclaracion(
    etiquetas_ofrecidas: Iterable[str], *, candidatas_esperadas: Iterable[str],
) -> ResultadoComprobacion:
    ofrecidas = tuple(etiquetas_ofrecidas)
    faltantes = [c for c in candidatas_esperadas if c not in ofrecidas]
    if not faltantes:
        return ResultadoComprobacion("aclaracion", "aprobado")
    return ResultadoComprobacion(
        "aclaracion", "falla",
        f"no ofreció botón para {faltantes} (ofrecidas: {sorted(ofrecidas)})")


def resultado_general(comprobaciones: Iterable[ResultadoComprobacion]) -> str:
    """Un sólo `falla` invalida la corrida; si no hay fallas pero hay algo
    `no_concluyente`, la corrida queda `no_concluyente`; si no, `aprobado`."""
    resultados = [c.resultado for c in comprobaciones]
    if "falla" in resultados:
        return "falla"
    if "no_concluyente" in resultados:
        return "no_concluyente"
    return "aprobado"
