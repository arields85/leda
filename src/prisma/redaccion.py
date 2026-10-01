"""Cómo se redacta la respuesta de un turno (ADR 0014, etapa 6).

Dos variantes, seleccionables por espacio con un dato
(`workspace_setting['redaccion']`, `{"variante": "A" | "B"}`, sembrado desde
la sección `conversacion` del pack; `docs/architecture/frontera.md`, regla 5):

- **B.** Plantillas del código para lo que cambió, cómo quedó y qué falta.
- **A.** El modelo redacta a partir del resultado del turno y el código
  verifica el texto (`verificador_redaccion`). Con `MODELO_PURO` (por omisión,
  mientras dure el experimento) no hay plazo propio ni plantilla de respaldo: un
  rechazo se corrige una vez con el motivo y, si no sale un texto, queda un
  incidente y el aviso neutro. Sin `MODELO_PURO`, si el texto no sirve o el
  modelo falla, sale el de B, que lo reemplaza, y queda registrado
  (`redactar_turno`). `redactar` y `redactar_partes` no llaman al modelo: son
  siempre las plantillas.

Nada de acá conoce el transporte: recibe un `ResultadoTurno` y devuelve
texto plano. Los botones los dibuja quien transporta, desde
`ResultadoTurno.opciones`.
"""

from __future__ import annotations

import json
import re
import statistics
import time
from dataclasses import dataclass

import httpx
import psycopg

from .db import registrar_auditoria
from .incidentes import (ETAPA_CHARLA_SIN_RESPUESTA, ETAPA_REDACCION_FALLIDA,
                         ETAPA_REDACCION_RECHAZADA, NOTICIA_NEUTRA_INCIDENTE,
                         registrar_incidente)
from .llm import PlazoAgotado, llamar_con_plazo
from .resultado_turno import Falta, ResultadoTurno, Resumen, ids_de_cambios
from .valores import TipoValor  # noqa: F401 -- el tipo de `Falta.tipo`
from .verificador_redaccion import leer_borrador, verificar

CLAVE_REDACCION = "redaccion"
VARIANTES = ("A", "B")
VARIANTE_POR_OMISION = "B"
ETAPA_INTERRUPTOR_REDACCION = "interruptor_redaccion"
# Cada borrador de A (aceptado, rechazado o fallido) deja una fila de auditoría
# con su duración: de ahí sale la mediana de la prueba (`estadistica_variante_a`).
ACCION_REDACCION_A = "redaccion_variante_a"
_reloj = time.perf_counter
# El plazo TOTAL de la redacción de A: una llamada, sin reintentos. Pasado el plazo
# sale la plantilla de B de inmediato y queda registrado. Cada texto y cada toque
# espera esa llamada; el plazo acota lo peor que la persona puede esperar. Medido en
# vivo (nan/deepseek-v4-flash, la llamada de redacción): p50 0,93 s, p90 3,06 s,
# máximo 6,6 s; con 3 s caerían ~10 % de los turnos a B, con 4 s ~4 %.
PLAZO_REDACCION_S = 4.0
# El modelo puro (pedido del usuario, 2026-10-01; mientras dure el experimento): sin
# plazo propio (queda el timeout HTTP normal del proveedor, para que nada se cuelgue
# para siempre) y sin plantilla de respaldo. Si el verificador rechaza el texto se le
# pide UNA vez más al modelo, con el motivo (`INTENTOS_MODELO_PURO` en total); si
# falla de nuevo, o da error, queda un incidente y sale un aviso neutro y corto.
# `MODELO_PURO = False` restaura el plazo de `PLAZO_REDACCION_S` y el respaldo de B.
MODELO_PURO = True
INTENTOS_MODELO_PURO = 2

# (espacio, valor) ya registrados por este proceso: la anomalía del interruptor
# se nota una vez, no en cada turno (mismo criterio que el supresor de
# incidentes de fondo de `ciclo`). `incident` no se puede leer con el rol de la
# aplicación, así que la deduplicación no puede salir de la base.
_anomalias_reportadas: set[tuple[str, str]] = set()


def interpretar_variante(valor) -> tuple[str, bool]:
    """La variante que dice el dato guardado y si el dato es anómalo. Una
    variante que no existe, o una forma equivocada, es B: nunca se adivina
    (`A` en minúscula tampoco), y quien llama lo registra."""
    if isinstance(valor, dict):
        variante = valor.get("variante")
        if isinstance(variante, str) and variante in VARIANTES:
            return variante, False
    return VARIANTE_POR_OMISION, True


def variante_redaccion(cur, workspace_id: str) -> str:
    """La variante de redacción del espacio. Sin la clave, B (un espacio que
    nunca eligió no es un defecto). Con un valor que no es una variante, B y
    un incidente: un interruptor mal escrito no se ignora en silencio."""
    cur.execute(
        "select valor from workspace_setting "
        "where workspace_id = %s and clave = %s",
        (workspace_id, CLAVE_REDACCION))
    fila = cur.fetchone()
    if not fila:
        return VARIANTE_POR_OMISION
    valor = fila["valor"]
    if isinstance(valor, str):
        try:
            valor = json.loads(valor)
        except ValueError:
            pass
    variante, anomalo = interpretar_variante(valor)
    if anomalo:
        _registrar_anomalia(cur, workspace_id, valor)
    return variante


def _registrar_anomalia(cur, workspace_id: str, valor) -> None:
    huella = (workspace_id, json.dumps(valor, sort_keys=True, default=str))
    if huella in _anomalias_reportadas:
        return
    registrar_incidente(
        cur, workspace_id,
        "El interruptor de redacción del espacio no tiene una variante "
        "válida (A o B): se usa la variante B.",
        referencia_cruda=f"workspace_setting[{CLAVE_REDACCION}]={huella[1]}"[:2000],
        etapa=ETAPA_INTERRUPTOR_REDACCION)
    _anomalias_reportadas.add(huella)


# ---------------------------------------------------------------------------
# Variante B: plantillas
# ---------------------------------------------------------------------------

def nombre_legible(clave: str) -> str:
    """Un nombre interno del pack (`resultado_de_prueba`) como lo lee una
    persona (`resultado de prueba`). Sólo separa las palabras: el pack todavía
    no trae una etiqueta propia por tipo de evidencia (PENDIENTE), así que no
    se inventa ninguna."""
    return " ".join(clave.replace("_", " ").split())


@dataclass(frozen=True)
class TextoRedactado:
    """Un texto en sus dos partes: el cuerpo y el cierre del botón que le toca
    a quien lo lee (R8). El cierre es una parte propia, nunca el último
    párrafo de un texto que habría que volver a cortar: otra redacción puede
    no tener la forma `cuerpo + párrafo`. `fallida` dice que el modelo no pudo
    redactarlo (modelo puro) y el cuerpo es el aviso neutro."""
    cuerpo: str
    cierre: str = ""
    fallida: bool = False

    @property
    def texto(self) -> str:
        return f"{self.cuerpo}\n\n{self.cierre}" if self.cierre else self.cuerpo

    def con_cierre(self, cierre: str) -> TextoRedactado:
        return TextoRedactado(self.cuerpo, cierre, self.fallida)


def _resumen_b(r: Resumen) -> str:
    lineas = "\n".join(f"{etiqueta}: {valor}" for etiqueta, valor in r.lineas)
    return f"{r.titulo}\n{lineas}"


def _redactar_b(r: ResultadoTurno) -> TextoRedactado:
    partes: list[str] = []
    if r.resumen:
        partes.append(_resumen_b(r.resumen))
    if r.rechazo:
        partes.append(f"{r.rechazo.razon} {r.rechazo.se_acepta}")
    if len(r.cambios) == 1:
        c = r.cambios[0]
        partes.append(f"Listo: {c.sujeto} {c.que}.")
    elif r.cambios:
        partes.append("Listo:\n" + "\n".join(
            f"- {c.sujeto} {c.que}" for c in r.cambios))
    if r.sin_cambios:
        partes.append("\n".join(
            f"No cambié {s.sujeto}: {s.motivo}." for s in r.sin_cambios))
    if r.valores_aceptados:
        partes.append("\n".join(
            f"Anoté {v.dato}: {v.mostrado}." for v in r.valores_aceptados))
    if r.estado:
        partes.append("\n".join(f"{e.sujeto} está {e.estado}." for e in r.estado))
    if r.falta:
        partes.append(r.falta.pregunta or f"Me falta {r.falta.dato}.")
    # El cierre del resumen va al final, como parte propia (R8).
    return TextoRedactado("\n\n".join(partes),
                          r.resumen.cierre if r.resumen else "")


def redactar_partes(resultado: ResultadoTurno, variante: str) -> TextoRedactado:
    """El texto de un turno a partir de sus hechos, en cuerpo y cierre. Un
    resultado sin ningún hecho o una variante que no existe son un defecto de
    quien llama: fallan fuerte, nunca salen como un texto vacío."""
    if variante not in VARIANTES:
        raise ValueError(f"Variante de redacción desconocida: {variante!r}.")
    if resultado.vacio:
        raise ValueError("El resultado del turno no tiene ningún hecho que decir.")
    # Las plantillas, también para A: el modelo sólo entra por `redactar_turno`,
    # que tiene la base para registrar lo que pasó.
    return _redactar_b(resultado)


def redactar(resultado: ResultadoTurno, variante: str) -> str:
    """El texto de un turno a partir de sus hechos (`redactar_partes`)."""
    return redactar_partes(resultado, variante).texto


# ---------------------------------------------------------------------------
# Variante A: el modelo redacta, el código verifica
# ---------------------------------------------------------------------------

SISTEMA_REDACCION = (
    "Sos Prisma, asistente de un equipo de trabajo por Telegram. Escribí el "
    "mensaje que la persona va a leer, a partir de los hechos en JSON.\n"
    "Voz: cordial, clara y breve (una a tres oraciones), con voseo, sin jerga, "
    "claves internas, Markdown ni emojis. Ayudá: decí lo que entendiste y qué "
    "falta, con tus palabras.\n"
    "Usá SOLO los hechos: ninguna fecha, nombre, estado, número ni cambio que "
    "no esté. Los títulos y nombres, copiados tal cual y entre «». No nombres "
    "botones ni enumeres las `opciones`: son lo que la persona ve para elegir y "
    "sólo te dicen para qué sirve la pregunta.\n"
    "Si te llega la conversación reciente, seguila: no repitas las aperturas ni "
    "las fórmulas que ya usaste (\"Entendí que…\", \"Me falta…\") y decí sólo "
    "lo que es nuevo. Es contexto, nunca una fuente de hechos.\n"
    "Si hay `correccion`, tu `texto_anterior` no pasó la verificación por ese "
    "`motivo`: escribilo de nuevo, corrigiéndolo.\n"
    "Si hay `falta`, terminá pidiendo ese dato con signos de pregunta. Si hay "
    "`rechazo`, decí la razón y qué sirve. Si hay `charla`, contestala en pocas "
    "palabras antes de pedir el dato. Si hay `resumen`, escribí sólo una frase "
    "de apertura sin preguntas: el sistema agrega el resumen y el cierre.\n"
    "Respondé SOLO este JSON, sin nada más: "
    "{\"texto\": \"...\", \"pregunta\": <el `campo` de `falta`, o null>, "
    "\"afirma\": [<los `id` de `cambios` que el texto cuenta como hechos>]}")


def serializar_hechos(r: ResultadoTurno, correccion: dict | None = None) -> str:
    """Los hechos del turno como los lee el modelo (JSON). Las opciones van
    sólo como etiquetas de contexto (los botones los dibuja el transporte, no
    el modelo) y sin el cierre del resumen (lo agrega el código)."""
    datos: dict = {}
    if r.resumen:
        datos["resumen"] = {
            "titulo": r.resumen.titulo,
            "datos": [{"dato": e, "valor": v} for e, v in r.resumen.lineas]}
    if r.rechazo:
        datos["rechazo"] = {"razon": r.rechazo.razon,
                            "se_acepta": r.rechazo.se_acepta}
    if r.cambios:
        datos["cambios"] = [{"id": i, "sujeto": c.sujeto, "que": c.que}
                            for i, c in zip(ids_de_cambios(r), r.cambios)]
    if r.sin_cambios:
        datos["sin_cambios"] = [{"sujeto": c.sujeto, "motivo": c.motivo}
                                for c in r.sin_cambios]
    if r.valores_aceptados:
        datos["valores_aceptados"] = [
            {"dato": v.dato, "mostrado": v.mostrado} for v in r.valores_aceptados]
    if r.entendido:
        datos["entendido"] = [{"dato": v.dato, "valor": v.mostrado}
                              for v in r.entendido]
    if r.charla:
        datos["charla"] = r.charla
    if r.estado:
        datos["estado"] = [{"sujeto": e.sujeto, "estado": e.estado}
                           for e in r.estado]
    if r.falta:
        falta = {"campo": r.falta.clave, "dato": r.falta.dato,
                 "tipo": r.falta.tipo.value}
        if r.falta.pregunta:
            falta["pregunta"] = r.falta.pregunta
        datos["falta"] = falta
    if r.opciones:
        datos["opciones"] = [o.etiqueta for o in r.opciones]
    if correccion:
        # El segundo intento del modelo puro: por qué no sirvió el primero.
        datos["correccion"] = correccion
    return json.dumps(datos, ensure_ascii=False)


def proveedor_de_redaccion(cur, workspace_id: str):
    """El modelo del espacio para redactar: el mismo que conversa."""
    from .config import config
    from .llm import desde_base

    return desde_base(cur, workspace_id, config)


def _registrar_intento(cur, workspace_id: str, resultado: str, motivo: str | None,
                       duracion_ms: int, caracteres: int, *,
                       incidente: bool = True) -> None:
    """Deja el intento en la auditoría (con la duración, para la mediana) y, si
    no se usó el texto del modelo, en un incidente de baja severidad que no
    avisa a la administración: es un dato del experimento, no una falla de la
    persona, y nunca queda en silencio."""
    detalle = {"resultado": resultado, "duracion_ms": duracion_ms,
               "caracteres": caracteres}
    if motivo:
        detalle["motivo"] = motivo[:300]
    registrar_auditoria(cur, accion=ACCION_REDACCION_A, workspace_id=workspace_id,
                        actor_kind="prisma", detalle=detalle)
    if resultado == "aceptada" or not incidente:
        return
    queja = {"error": "El modelo no pudo redactar la respuesta",
             "timeout": "El modelo no contestó a tiempo"}.get(
        resultado, "El texto que redactó el modelo no pasó la verificación")
    registrar_incidente(
        cur, workspace_id,
        f"{queja} (variante A): se usó la respuesta de la variante B.",
        severidad="baja", referencia_cruda=(motivo or "")[:2000],
        etapa=ETAPA_REDACCION_RECHAZADA, avisar_admin=False)


def _timeout_de(exc: BaseException) -> BaseException | None:
    """El timeout que explica la excepción, por su TIPO (no por su nombre): el
    plazo propio, el de Python o el de httpx, también si un cliente lo envolvió
    (`APITimeoutError` lo trae como causa)."""
    visto: set[int] = set()
    while exc is not None and id(exc) not in visto:
        if isinstance(exc, (PlazoAgotado, TimeoutError, httpx.TimeoutException)):
            return exc
        visto.add(id(exc))
        exc = exc.__cause__
    return None


def _motivo_de_timeout(exc: BaseException, plazo: float) -> str:
    """"Más de N s sin respuesta" sólo es verdad para el plazo propio; un timeout
    de conexión o de pool no dice que el modelo tardó."""
    if isinstance(_timeout_de(exc), PlazoAgotado):
        return f"timeout: más de {plazo:g} s sin respuesta"
    return f"timeout: {type(_timeout_de(exc)).__name__}"


_URL = re.compile(r"\b[a-zA-Z][a-zA-Z0-9+.-]*://\S*|\bwww\.\S+")
_CREDENCIAL = re.compile(r"(?i)\b(?:authorization|bearer|basic)\b[:\s]*\S*(?:\s+\S+)?")
_ASIGNACION = re.compile(r"\S*=\S*")
_CONSULTA = re.compile(r"\?\S*")
_OPACO = re.compile(r"\b(?=[\w-]*\d)(?=[\w-]*[A-Za-z])[\w-]{12,}\b")
_LARGO_RAZON = 120
# Los únicos tipos cuyo mensaje es del propio proyecto (una configuración que
# falta). Un subtipo (un error de JSON, de URL, de HTTP) trae texto de un tercero.
_TIPOS_CON_RAZON = (LookupError, ValueError, KeyError)


def _razon_corta(mensaje: str) -> str:
    """El mensaje sin nada que parezca una dirección, una credencial o un
    parámetro (`clave=valor`, `?consulta`, un identificador opaco), y corto."""
    for patron, reemplazo in ((_URL, "[dirección]"), (_CREDENCIAL, "[credencial]"),
                              (_ASIGNACION, "[parámetro]"), (_CONSULTA, ""),
                              (_OPACO, "[opaco]")):
        mensaje = patron.sub(reemplazo, mensaje)
    return " ".join(mensaje.split())[:_LARGO_RAZON]


def _motivo_de_error(exc: Exception) -> str:
    """Qué falló, sin el texto de la excepción de un tercero (podría traer una
    dirección con credencial): siempre el tipo y, sólo de `LookupError`,
    `ValueError` y `KeyError` tal cual (los del propio proyecto, una configuración
    que falta), una razón corta depurada. Nunca el mensaje de un error de HTTP,
    de URL o de JSON, aunque hereden de `ValueError`."""
    nombre = type(exc).__name__
    if type(exc) in _TIPOS_CON_RAZON:
        razon = _razon_corta(str(exc))
        if razon:
            return f"{nombre}: {razon}"
    return nombre


def redactar_turno(cur, workspace_id: str, resultado: ResultadoTurno, variante: str,
                   *, proveedor=None, base: TextoRedactado | None = None,
                   plazo: float = PLAZO_REDACCION_S,
                   historial: list[dict] | None = None) -> TextoRedactado:
    """El texto de un turno con la variante del espacio. Con A, el modelo
    redacta el mensaje entero sobre los hechos (salida estructurada) y el
    código lo verifica; si no sirve, o el modelo falla o se cuelga, sale la
    plantilla de B (reemplaza, nunca se suma: es UNA respuesta) y queda
    registrado con la duración de la llamada. `base` es la plantilla de B cuando
    no es la genérica (un texto que B ya tenía antes de existir el resultado).
    Con un resumen, el modelo escribe sólo la apertura: los datos y el cierre son
    siempre del código. `plazo` es el tiempo máximo de la llamada, sin
    reintentos: pasado, sale B. `historial` es la conversación reciente (F-C4): el
    modelo ve lo que ya dijo y no repite sus fórmulas; es contexto, los hechos
    siguen siendo lo único que puede afirmar."""
    base = base or redactar_partes(resultado, variante)   # valida y arma B
    if variante != "A":
        return base
    if MODELO_PURO:
        return _redactar_modelo_puro(cur, workspace_id, resultado, base,
                                     proveedor, historial)
    inicio = _reloj()
    duracion_ms = 0
    caracteres = 0
    try:
        modelo = proveedor or proveedor_de_redaccion(cur, workspace_id)
        hechos = serializar_hechos(resultado)
        conversacion = {"historial": historial} if historial else {}
        crudo = llamar_con_plazo(
            lambda: modelo.redactar(SISTEMA_REDACCION, hechos, plazo=plazo,
                                    **conversacion), plazo)
        duracion_ms = round((_reloj() - inicio) * 1000)
        caracteres = len((crudo or "").strip())
        borrador = leer_borrador(crudo)
        # El verificador corre dentro del mismo `try`: un defecto suyo cae a B
        # y queda registrado, nunca deja al turno sin texto (R13).
        motivo = (borrador if isinstance(borrador, str)
                  else verificar(resultado, borrador, base.texto))
    except psycopg.Error:
        raise                       # la transacción no sigue: no es del modelo
    except Exception as exc:        # un modelo que falla o se cuelga: sale B
        duracion_ms = duracion_ms or round((_reloj() - inicio) * 1000)
        if _timeout_de(exc):
            _registrar_intento(cur, workspace_id, "timeout",
                               _motivo_de_timeout(exc, plazo), duracion_ms,
                               caracteres)
        else:
            _registrar_intento(cur, workspace_id, "error", _motivo_de_error(exc),
                               duracion_ms, caracteres)
        return base
    if motivo:
        _registrar_intento(cur, workspace_id, "rechazada", motivo, duracion_ms,
                           caracteres)
        return base
    _registrar_intento(cur, workspace_id, "aceptada", None, duracion_ms,
                       caracteres)
    if resultado.resumen:
        return TextoRedactado(
            f"{borrador.texto}\n\n{_resumen_b(resultado.resumen)}", base.cierre)
    return TextoRedactado(borrador.texto, base.cierre)


def _aviso_de_modelo_puro(resultado: ResultadoTurno,
                         base: TextoRedactado) -> TextoRedactado:
    """Lo que sale cuando el modelo no pudo redactar (modelo puro): el aviso neutro y
    corto, sin texto de plantilla. Lo único que se agrega es lo que la persona
    necesita ver para decidir con los botones de ese mensaje: el resumen que
    confirma (sus datos y el cierre que nombra el botón real, F-C5); el valor que
    se pide confirmar lo agrega quien lo pide (`ingreso_tareas._decir_pregunta`)."""
    if resultado.resumen:
        return TextoRedactado(
            f"{NOTICIA_NEUTRA_INCIDENTE}\n\n{_resumen_b(resultado.resumen)}",
            base.cierre, fallida=True)
    return TextoRedactado(NOTICIA_NEUTRA_INCIDENTE, fallida=True)


def _redactar_modelo_puro(cur, workspace_id: str, resultado: ResultadoTurno,
                          base: TextoRedactado, proveedor,
                          historial: list[dict] | None) -> TextoRedactado:
    """El texto de un turno con el modelo solo (`MODELO_PURO`): sin plazo propio y
    sin plantilla. Cada intento deja su fila de auditoría con la duración. Un
    rechazo del verificador se corrige UNA vez (el modelo ve su texto anterior y
    el motivo); un error del modelo no se reintenta (el proveedor ya reintentó). Si
    no sale un texto, un incidente con los motivos y el aviso neutro."""
    conversacion = {"historial": historial} if historial else {}
    correccion: dict | None = None
    motivos: list[str] = []
    for _ in range(INTENTOS_MODELO_PURO):
        inicio = _reloj()
        duracion_ms = caracteres = 0
        try:
            modelo = proveedor or proveedor_de_redaccion(cur, workspace_id)
            crudo = modelo.redactar(
                SISTEMA_REDACCION, serializar_hechos(resultado, correccion),
                **conversacion)
            duracion_ms = round((_reloj() - inicio) * 1000)
            caracteres = len((crudo or "").strip())
            borrador = leer_borrador(crudo)
            motivo = (borrador if isinstance(borrador, str)
                      else verificar(resultado, borrador, base.texto))
        except psycopg.Error:
            raise                   # la transacción no sigue: no es del modelo
        except Exception as exc:    # el modelo dio error: no se reintenta
            duracion_ms = duracion_ms or round((_reloj() - inicio) * 1000)
            if _timeout_de(exc):
                tipo, razon = "timeout", _motivo_de_timeout(exc, 0)
            else:
                tipo, razon = "error", _motivo_de_error(exc)
            _registrar_intento(cur, workspace_id, tipo, razon, duracion_ms,
                               caracteres, incidente=False)
            motivos.append(razon)
            break
        if not motivo:
            _registrar_intento(cur, workspace_id, "aceptada", None, duracion_ms,
                               caracteres, incidente=False)
            if resultado.resumen:
                return TextoRedactado(
                    f"{borrador.texto}\n\n{_resumen_b(resultado.resumen)}",
                    base.cierre)
            return TextoRedactado(borrador.texto, base.cierre)
        _registrar_intento(cur, workspace_id, "rechazada", motivo, duracion_ms,
                           caracteres, incidente=False)
        motivos.append(motivo)
        correccion = {
            "motivo": motivo,
            "texto_anterior": (borrador.texto if not isinstance(borrador, str)
                               else (crudo or "").strip())[:500]}
    registrar_incidente(
        cur, workspace_id,
        "El modelo no pudo redactar la respuesta (variante A, modelo puro): salió "
        "el aviso neutro.", severidad="media",
        referencia_cruda=" | ".join(motivos)[:2000],
        etapa=ETAPA_REDACCION_FALLIDA)
    return _aviso_de_modelo_puro(resultado, base)


# ---------------------------------------------------------------------------
# La charla con una pregunta pendiente (ADR 0013 regla 1, F-B5)
# ---------------------------------------------------------------------------

SISTEMA_CHARLA = (
    "Sos Prisma, una asistente que coordina el trabajo de un equipo por "
    "Telegram. La persona escribió un saludo, un agradecimiento o una charla "
    "suelta mientras Prisma esperaba la respuesta a una pregunta (te llega en "
    "JSON como `mensaje` y `pregunta_pendiente`).\n"
    "- Respondé en una sola oración corta, en español neutro con voseo, cálida "
    "y sin vueltas.\n"
    "- No hagas ninguna pregunta: la pregunta pendiente la vuelve a hacer el "
    "sistema después de tu respuesta.\n"
    "- No prometas, no afirmes cambios ni estados, y no inventes datos, fechas "
    "ni nombres.\n"
    "- Sin Markdown, sin emojis, sin jerga técnica y sin nombrar botones.\n"
    "Devolvé únicamente el texto de la respuesta.")

MAX_CARACTERES_CHARLA = 240


def motivo_de_charla_invalida(texto: str) -> str | None:
    """Por qué el texto no sirve como respuesta breve de una charla, o `None`
    si sirve. Determinista: una respuesta vacía, de más de un párrafo, larga o
    que abre otra pregunta (la pregunta pendiente es la única) no sale."""
    texto = (texto or "").strip()
    if not texto:
        return "el modelo no devolvió texto"
    if len(texto) > MAX_CARACTERES_CHARLA:
        return f"la respuesta pasa de {MAX_CARACTERES_CHARLA} caracteres"
    if "\n" in texto:
        return "la respuesta tiene más de un párrafo"
    if "?" in texto or "¿" in texto:
        return "la respuesta abre otra pregunta"
    return None


def redactar_charla_con_pregunta(cur, workspace_id: str, mensaje: str,
                                 pregunta: str, campo: str, dato: str, *,
                                 proveedor=None,
                                 nombres: tuple[str, ...] = (),
                                 historial: list[dict] | None = None,
                                 ) -> TextoRedactado:
    """Con A, la charla y la pregunta pendiente son UN mensaje natural del modelo
    (F-A2): contesta en pocas palabras y pide el dato, en vez de una frase suelta
    delante de la plantilla. `campo` y `dato` identifican la pregunta (el campo
    del alta, o `pendiente`). Si el modelo no sirve, sale sólo la pregunta (la
    plantilla de B) y queda registrado."""
    resultado = ResultadoTurno(
        charla=mensaje,
        falta=Falta(dato, TipoValor.TEXTO, pregunta=pregunta, campo=campo),
        nombres_conocidos=nombres)
    return redactar_turno(cur, workspace_id, resultado, "A", proveedor=proveedor,
                          base=TextoRedactado(pregunta), historial=historial)


def redactar_charla(cur, workspace_id: str, mensaje: str, pregunta: str, *,
                    proveedor=None, historial: list[dict] | None = None) -> str:
    """La respuesta breve a una charla con una pregunta pendiente, en las dos
    variantes (ADR 0014: el modelo redacta la charla y las preguntas). La
    persona la lee delante de la pregunta, en la misma respuesta. `""` si el
    modelo falla o su texto no sirve: sale sólo la pregunta y queda un incidente
    de baja severidad que no avisa a la administración -- nunca en silencio."""
    try:
        modelo = proveedor or proveedor_de_redaccion(cur, workspace_id)
        pedido = json.dumps({"mensaje": mensaje, "pregunta_pendiente": pregunta},
                            ensure_ascii=False)
        conversacion = {"historial": historial} if historial else {}
        borrador = llamar_con_plazo(
            lambda: modelo.redactar(SISTEMA_CHARLA, pedido,
                                    plazo=PLAZO_REDACCION_S, **conversacion),
            PLAZO_REDACCION_S)
    except psycopg.Error:
        raise                       # la transacción no sigue: no es del modelo
    except Exception as exc:        # un modelo que falla o se cuelga
        _registrar_charla_sin_respuesta(cur, workspace_id, _motivo_de_error(exc))
        return ""
    borrador = (borrador or "").strip()
    motivo = motivo_de_charla_invalida(borrador)
    if motivo:
        _registrar_charla_sin_respuesta(cur, workspace_id, motivo)
        return ""
    return borrador


def _registrar_charla_sin_respuesta(cur, workspace_id: str, motivo: str) -> None:
    registrar_incidente(
        cur, workspace_id,
        "El modelo no pudo redactar la respuesta breve de una charla con una "
        "pregunta pendiente: sale sólo la pregunta.",
        severidad="baja", referencia_cruda=motivo[:2000],
        etapa=ETAPA_CHARLA_SIN_RESPUESTA, avisar_admin=False)


def estadistica_variante_a(cur, workspace_id: str) -> dict:
    """Los intentos de la variante A del espacio: cuántos, cómo terminaron y la
    latencia de la llamada de redacción (mediana, p90, máximo, en ms; `None`
    sin intentos). La mediana de todos los intentos es la del criterio del ADR
    0014 (hasta 5 s por respuesta)."""
    cur.execute(
        "select detalle from audit_log where workspace_id = %s and accion = %s",
        (workspace_id, ACCION_REDACCION_A))
    filas = [f["detalle"] for f in cur.fetchall()]
    todos = sorted(d["duracion_ms"] for d in filas)
    aceptadas = sorted(d["duracion_ms"] for d in filas
                       if d["resultado"] == "aceptada")

    def mediana(valores):
        return statistics.median(valores) if valores else None

    return {
        "llamadas": len(filas),
        "aceptadas": len(aceptadas),
        "rechazadas": sum(1 for d in filas if d["resultado"] == "rechazada"),
        "errores": sum(1 for d in filas if d["resultado"] == "error"),
        "timeouts": sum(1 for d in filas if d["resultado"] == "timeout"),
        "mediana_ms": mediana(todos),
        "mediana_aceptadas_ms": mediana(aceptadas),
        "p90_ms": todos[min(len(todos) - 1, int(len(todos) * 0.9))] if todos else None,
        "maximo_ms": todos[-1] if todos else None,
    }
