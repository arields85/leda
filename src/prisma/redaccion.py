"""Cómo se redacta la respuesta de un turno (ADR 0014, etapa 6).

Dos variantes, seleccionables por espacio con un dato
(`workspace_setting['redaccion']`, `{"variante": "A" | "B"}`, sembrado desde
la sección `conversacion` del pack; `docs/architecture/frontera.md`, regla 5):

- **B.** Plantillas del código para lo que cambió, cómo quedó y qué falta.
- **A.** El modelo redacta a partir del resultado del turno y el código
  verifica el texto (F6a). Mientras no exista, `redactar` cae en B.

Nada de acá conoce el transporte: recibe un `ResultadoTurno` y devuelve
texto plano. Los botones los dibuja quien transporta, desde
`ResultadoTurno.opciones`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from .incidentes import registrar_incidente
from .resultado_turno import ResultadoTurno, Resumen
from .valores import TipoValor  # noqa: F401 -- el tipo de `Falta.tipo`

CLAVE_REDACCION = "redaccion"
VARIANTES = ("A", "B")
VARIANTE_POR_OMISION = "B"
ETAPA_INTERRUPTOR_REDACCION = "interruptor_redaccion"

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
    no tener la forma `cuerpo + párrafo`."""
    cuerpo: str
    cierre: str = ""

    @property
    def texto(self) -> str:
        return f"{self.cuerpo}\n\n{self.cierre}" if self.cierre else self.cuerpo

    def con_cierre(self, cierre: str) -> TextoRedactado:
        return TextoRedactado(self.cuerpo, cierre)


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
    # La variante A (el modelo redacta y el código verifica) llega con F6a;
    # hasta entonces cae en las plantillas.
    return _redactar_b(resultado)


def redactar(resultado: ResultadoTurno, variante: str) -> str:
    """El texto de un turno a partir de sus hechos (`redactar_partes`)."""
    return redactar_partes(resultado, variante).texto
