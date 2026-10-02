# Relevamiento: NotebookLM y respuestas ancladas en fuentes

- **Fecha:** 2026-10-01
- **Pedido:** del usuario, que comparó lo que quiere de Leda con NotebookLM: un modelo
  que conversa con fluidez y responde sólo con hechos de una base, sin inventar.
- **Veredicto:** la analogía sirve para la lectura; Leda suma efectos con confirmación.
  Tres ideas para adoptar dentro del flujo del
  [`ADR 0014`](../decisions/0014-flujo-de-un-mensaje.md).

## Qué es

NotebookLM (Google; hoy la ayuda lo llama "Gemini Notebook") conversa sobre las fuentes
que sube el usuario y responde "based on the information provided in your uploaded
sources", con citas en línea; si la información no está en las fuentes, lo dice
(https://support.google.com/notebooklm/answer/16164461). Corre sobre Gemini, con una
ventana de contexto de hasta un millón de tokens en el chat
(https://blog.google/innovation-and-ai/models-and-research/google-labs/notebooklm-custom-personas-engine-upgrade/).
Google no documenta si recupera fragmentos o carga los documentos enteros, ni cómo
verifica las citas.

## Técnicas en juego

- **Recuperación más generación (RAG).** La recuperación puede ser determinista (SQL,
  índices) o semántica; la redacción es del modelo.
- **Citas.** La API de citas de Anthropic devuelve el texto con referencias a la fuente
  (https://claude.com/blog/introducing-citations-api); las produce el modelo.
- **Verificación posterior.** "Check grounding" de Google puntúa cuánto de un texto está
  respaldado por una lista de hechos; una fecha equivocada le quita el respaldo a la
  afirmación entera (https://docs.cloud.google.com/generative-ai-app-builder/docs/check-grounding).
  Es un modelo de inferencia, no un control determinista.

## Diferencias con Leda

- NotebookLM sólo lee documentos. Leda además escribe: crea tareas, aprueba, avisa.
  Eso sigue pasando por herramientas con autoridad, validación del código y botón de
  confirmar.
- Los datos de Leda son estructurados: la "recuperación" son consultas y herramientas,
  deterministas y auditables, y el aislamiento entre clientes lo da RLS, no el prompt.

## Ideas para adoptar

1. **Cada dato cita su registro.** La respuesta remite a la tarea, la persona o el
   objetivo de donde sale cada dato, y el código comprueba que lo citado esté entre lo
   que devolvió la base en ese turno.
2. **Verificación determinista de valores.** Fechas, responsables, estados y títulos de
   la respuesta se comparan con las filas devueltas (es lo que ya hace el verificador
   de la etapa 6 con los hechos del turno). Un verificador de inferencia queda como
   segundo nivel opcional para prosa libre.
3. **"No está en los datos" explícito**, distinto de "no pude consultar" (invariante
   vigente: no poder consultar no equivale a que no exista).

## No verificado

La arquitectura interna de NotebookLM (recuperación o contexto largo, aislamiento entre
cuadernos, verificación de citas); Perplexity y ChatGPT con archivos no se relevaron con
fuentes primarias.
