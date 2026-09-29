"""Formato y carga de escenarios del banco.

Sigue "Estructura mínima de un escenario" de `docs/validation/README.md`: el
escenario declara sólo el objetivo, las precondiciones simuladas, el actor y
el mensaje inicial. No hay IDs internos, herramientas ni estados esperados
en el texto que Prisma recibe -- eso vive en `herramientas_esperadas` /
`herramientas_prohibidas`, que nunca se le muestran al modelo.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass, field

import yaml

SEVERIDADES = ("baja", "media", "alta", "critica")

_CAMPOS_OBLIGATORIOS = ("id", "objetivo", "actor", "mensajes")

# Las precondiciones que dejan una pregunta ya esperando a la persona
# (`corrida.sembrar_precondiciones` y `corrida.ejecutar_escenario`): con
# cualquiera de ellas el escenario no necesita un primer mensaje.
PREGUNTAS_SEMBRADAS = ("borrador_de_alta", "vista_previa", "aclaracion")


class EscenarioInvalido(ValueError):
    pass


@dataclass(frozen=True)
class Escenario:
    id: str
    objetivo: str
    actor: str
    mensajes: list[str]
    herramientas_esperadas: tuple[str, ...] = ()
    herramientas_prohibidas: tuple[str, ...] = ()
    nombres_permitidos: tuple[str, ...] = ()
    precondiciones: dict = field(default_factory=dict)
    severidad: str = "media"
    # Estado y efectos esperados (protocolo, "Estructura mínima de un
    # escenario"): sin esto sólo se verificaba el nombre de la herramienta,
    # nunca si dejó el estado, el bloqueo o la dependencia correctos.
    efectos: dict = field(default_factory=dict)
    respuesta_menciona: tuple[str, ...] = ()
    respuesta_no_contiene_patron: tuple[str, ...] = ()
    # Mensajes humanos reales (odd/tasks/banco-mensajes-humanos.md, T1):
    # `variante_de` agrupa una redacción desprolija con su escenario base en
    # el reporte (`reporte.py`); `debe_preguntar` activa la comprobación
    # nueva "ante la duda, preguntó en vez de actuar"
    # (`comprobadores.comprobar_pregunta`). `permite_borrador_de_tarea`
    # excepciona el único caso en que abrir un `task_draft` SÍ es la
    # respuesta correcta a una ambigüedad: un escenario que es justamente
    # sobre dar de alta una tarea.
    variante_de: str | None = None
    debe_preguntar: bool = False
    permite_borrador_de_tarea: bool = False
    # Aclaración con botones (T6, `aclaracion-con-botones`): qué títulos
    # tienen que aparecer como candidatas cuando una referencia a tarea es
    # ambigua, y cuál tocar para retomar el pedido original
    # (`corrida.ejecutar_escenario`). Vacío: el corredor no espera ninguna
    # aclaración con botones para este escenario (referencia clara, sin
    # referencia, o el caso "debe preguntar" de siempre, en texto).
    aclaracion_esperada: dict = field(default_factory=dict)
    # Toques genéricos de escenario (T4, `prisma-orienta`): una secuencia de
    # botones a tocar, EN ORDEN, después de los mensajes (y de la aclaración
    # con botones de arriba, si la hay) -- antes del toque automático en
    # Confirmar de siempre (`corrida.ejecutar_escenario`). Cada elemento
    # resuelve contra las opciones REALES que dejó el turno anterior, nunca
    # un token inventado: `{"etiqueta": "..."}` (coincidencia exacta de
    # texto) o `{"indice": N}` (posición 0-based en el orden en que se
    # ofrecieron). Sirve para simular, por ejemplo, tocar una tarea de una
    # lista (T3) y después una acción de su menú (T2) hasta llegar a la
    # vista previa de siempre. Vacío: ningún toque de escenario más allá del
    # de Confirmar, que ya corre siempre.
    toques: tuple[dict, ...] = ()
    # ADR 0007 ("Prisma orienta, no charla"), T4: opt-out explícito, por
    # escenario, de `comprobadores.comprobar_pregunta_con_opciones` (activa
    # por defecto para todo escenario) -- para un escenario legado que
    # necesite seguir pasando con una pregunta en texto abierto sin botones.
    permite_pregunta_sin_opciones: bool = False
    # Mensajes de texto que se mandan DESPUÉS de los toques y antes del
    # Confirmar automático (T9-R1a-2, ADR 0013 regla 1): sirven para contestar
    # la pregunta que abrió un toque (p. ej. "Ya la terminé" pide la
    # evidencia). La respuesta visible que se evalúa es la de estos mensajes
    # y lo que sigue, no la de la pregunta que ya estaba abierta
    # (`corrida.ejecutar_escenario`).
    mensajes_tras_toques: tuple[str, ...] = ()
    # Toques que se hacen DESPUÉS de `mensajes_tras_toques` (T9-R1d, ADR 0013
    # regla 1, enmienda "una sola rama abierta"): sirven para tocar la pregunta
    # que abrió uno de esos mensajes -- la de la rama de conversación, con
    # "Seguir" y "Dejarlo y ver lo otro". Mismo formato y misma resolución que
    # `toques`. La respuesta visible que se evalúa pasa a ser la de estos
    # toques y lo que sigue (`corrida.ejecutar_escenario`).
    toques_tras_mensajes: tuple[dict, ...] = ()


def _validar_toques(datos: dict, campo: str, origen: pathlib.Path) -> None:
    """`toques` y `toques_tras_mensajes` tienen el mismo formato: una lista de
    mapeos con `etiqueta` o `indice`, exactamente uno de los dos."""
    toques = datos.get(campo, [])
    if not isinstance(toques, list):
        raise EscenarioInvalido(f"{origen}: '{campo}' tiene que ser una lista.")
    for i, t in enumerate(toques):
        if not isinstance(t, dict):
            raise EscenarioInvalido(f"{origen}: '{campo}[{i}]' tiene que ser un mapeo.")
        tiene_etiqueta = "etiqueta" in t
        tiene_indice = "indice" in t
        if tiene_etiqueta == tiene_indice:
            raise EscenarioInvalido(
                f"{origen}: '{campo}[{i}]' tiene que traer 'etiqueta' o 'indice', "
                "exactamente uno de los dos.")
        if tiene_etiqueta:
            if not isinstance(t["etiqueta"], str) or not t["etiqueta"].strip():
                raise EscenarioInvalido(
                    f"{origen}: '{campo}[{i}].etiqueta' tiene que ser texto no vacío.")
        else:
            indice = t["indice"]
            if not isinstance(indice, int) or isinstance(indice, bool) or indice < 0:
                raise EscenarioInvalido(
                    f"{origen}: '{campo}[{i}].indice' tiene que ser un entero >= 0.")


def _validar_estructura(datos: dict, origen: pathlib.Path) -> None:
    if not isinstance(datos, dict):
        raise EscenarioInvalido(f"{origen}: el escenario tiene que ser un mapeo.")

    faltantes = [c for c in _CAMPOS_OBLIGATORIOS if c not in datos or datos[c] in (None, "")]
    if faltantes:
        raise EscenarioInvalido(f"{origen}: faltan campos obligatorios {faltantes}.")

    if not isinstance(datos["id"], str) or not datos["id"].strip():
        raise EscenarioInvalido(f"{origen}: 'id' tiene que ser texto no vacío.")
    if not isinstance(datos["objetivo"], str) or not datos["objetivo"].strip():
        raise EscenarioInvalido(f"{origen}: 'objetivo' tiene que ser texto no vacío.")
    if not isinstance(datos["actor"], str) or not datos["actor"].strip():
        raise EscenarioInvalido(f"{origen}: 'actor' tiene que ser texto no vacío.")

    mensajes = datos["mensajes"]
    # Con una pregunta ya sembrada -- el borrador del alta
    # (`precondiciones.borrador_de_alta`, T9-R1c-2b), la vista previa de un
    # cambio (`vista_previa`) o la aclaración con botones (`aclaracion`, T9-R1d-1c)
    # -- no hace falta un primer mensaje: alcanza con lo que se escribe después
    # de los toques.
    con_pregunta_sembrada = (
        isinstance(datos.get("precondiciones"), dict)
        and any(datos["precondiciones"].get(c) for c in PREGUNTAS_SEMBRADAS)
        and bool(datos.get("mensajes_tras_toques")))
    if (not isinstance(mensajes, list)
            or (not mensajes and not con_pregunta_sembrada)
            or not all(isinstance(m, str) and m.strip() for m in mensajes)):
        raise EscenarioInvalido(
            f"{origen}: 'mensajes' tiene que ser una lista no vacía de texto.")

    for campo in ("herramientas_esperadas", "herramientas_prohibidas",
                 "nombres_permitidos"):
        valor = datos.get(campo, [])
        if not isinstance(valor, list) or not all(isinstance(v, str) for v in valor):
            raise EscenarioInvalido(f"{origen}: '{campo}' tiene que ser una lista de texto.")

    precondiciones = datos.get("precondiciones", {})
    if not isinstance(precondiciones, dict):
        raise EscenarioInvalido(f"{origen}: 'precondiciones' tiene que ser un mapeo.")

    efectos = datos.get("efectos", {})
    if not isinstance(efectos, dict):
        raise EscenarioInvalido(f"{origen}: 'efectos' tiene que ser un mapeo.")

    for campo in ("respuesta_menciona", "respuesta_no_contiene_patron"):
        valor = datos.get(campo, [])
        if not isinstance(valor, list) or not all(isinstance(v, str) for v in valor):
            raise EscenarioInvalido(f"{origen}: '{campo}' tiene que ser una lista de texto.")

    severidad = datos.get("severidad", "media")
    if severidad not in SEVERIDADES:
        raise EscenarioInvalido(
            f"{origen}: 'severidad' tiene que ser una de {SEVERIDADES}, no {severidad!r}.")

    variante_de = datos.get("variante_de")
    if variante_de is not None and (not isinstance(variante_de, str) or not variante_de.strip()):
        raise EscenarioInvalido(f"{origen}: 'variante_de' tiene que ser texto no vacío.")

    for campo in ("debe_preguntar", "permite_borrador_de_tarea",
                 "permite_pregunta_sin_opciones"):
        valor = datos.get(campo, False)
        if not isinstance(valor, bool):
            raise EscenarioInvalido(f"{origen}: '{campo}' tiene que ser un booleano.")

    _validar_toques(datos, "toques", origen)

    tras_toques = datos.get("mensajes_tras_toques", [])
    if (not isinstance(tras_toques, list)
            or not all(isinstance(m, str) and m.strip() for m in tras_toques)):
        raise EscenarioInvalido(
            f"{origen}: 'mensajes_tras_toques' tiene que ser una lista de texto "
            "no vacío.")

    _validar_toques(datos, "toques_tras_mensajes", origen)
    if datos.get("toques_tras_mensajes") and not tras_toques:
        raise EscenarioInvalido(
            f"{origen}: 'toques_tras_mensajes' toca la pregunta que abrió un "
            "mensaje: hace falta 'mensajes_tras_toques'.")

    aclaracion_esperada = datos.get("aclaracion_esperada", {})
    if not isinstance(aclaracion_esperada, dict):
        raise EscenarioInvalido(f"{origen}: 'aclaracion_esperada' tiene que ser un mapeo.")
    if aclaracion_esperada:
        candidatas = aclaracion_esperada.get("candidatas")
        if (not isinstance(candidatas, list) or not candidatas
                or not all(isinstance(c, str) and c.strip() for c in candidatas)):
            raise EscenarioInvalido(
                f"{origen}: 'aclaracion_esperada.candidatas' tiene que ser una "
                "lista no vacía de texto.")
        elegir = aclaracion_esperada.get("elegir")
        if not isinstance(elegir, str) or not elegir.strip():
            raise EscenarioInvalido(
                f"{origen}: 'aclaracion_esperada.elegir' tiene que ser texto no vacío.")
        if elegir not in candidatas:
            raise EscenarioInvalido(
                f"{origen}: 'aclaracion_esperada.elegir' tiene que ser una de "
                "'aclaracion_esperada.candidatas'.")


def cargar_escenario(ruta: pathlib.Path | str) -> Escenario:
    """Carga y valida un único escenario desde un archivo YAML."""
    ruta = pathlib.Path(ruta)
    datos = yaml.safe_load(ruta.read_text("utf-8"))
    _validar_estructura(datos, ruta)

    return Escenario(
        id=datos["id"].strip(),
        objetivo=datos["objetivo"].strip(),
        actor=datos["actor"].strip(),
        mensajes=list(datos["mensajes"]),
        herramientas_esperadas=tuple(datos.get("herramientas_esperadas", [])),
        herramientas_prohibidas=tuple(datos.get("herramientas_prohibidas", [])),
        nombres_permitidos=tuple(datos.get("nombres_permitidos", [])),
        precondiciones=datos.get("precondiciones", {}) or {},
        severidad=datos.get("severidad", "media"),
        efectos=datos.get("efectos", {}) or {},
        respuesta_menciona=tuple(datos.get("respuesta_menciona", [])),
        respuesta_no_contiene_patron=tuple(datos.get("respuesta_no_contiene_patron", [])),
        variante_de=(datos.get("variante_de") or "").strip() or None,
        debe_preguntar=bool(datos.get("debe_preguntar", False)),
        permite_borrador_de_tarea=bool(datos.get("permite_borrador_de_tarea", False)),
        aclaracion_esperada=datos.get("aclaracion_esperada", {}) or {},
        toques=tuple(datos.get("toques", []) or []),
        permite_pregunta_sin_opciones=bool(datos.get("permite_pregunta_sin_opciones", False)),
        mensajes_tras_toques=tuple(datos.get("mensajes_tras_toques", []) or []),
        toques_tras_mensajes=tuple(datos.get("toques_tras_mensajes", []) or []),
    )


def cargar_escenarios(directorio: pathlib.Path | str) -> list[Escenario]:
    """Carga todos los `*.yaml` de un directorio. Rechaza IDs repetidos: dos
    escenarios con el mismo ID opaco no se pueden distinguir en el reporte."""
    directorio = pathlib.Path(directorio)
    escenarios = [cargar_escenario(p) for p in sorted(directorio.glob("*.yaml"))]

    vistos: dict[str, pathlib.Path] = {}
    for e, p in zip(escenarios, sorted(directorio.glob("*.yaml"))):
        if e.id in vistos:
            raise EscenarioInvalido(
                f"ID de escenario repetido: {e.id!r} en {vistos[e.id]} y {p}.")
        vistos[e.id] = p

    ids = set(vistos)
    for e, p in zip(escenarios, sorted(directorio.glob("*.yaml"))):
        if e.variante_de is not None and e.variante_de not in ids:
            raise EscenarioInvalido(
                f"{p}: 'variante_de' referencia {e.variante_de!r}, que no existe "
                f"entre los escenarios cargados.")
    return escenarios
