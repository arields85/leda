# Guía de validación manual por Telegram

Esta guía permite al usuario validar Prisma mediante Telegram real sin recibir
frases guionadas. La sesión ocurre sólo después de completar las capas A-D del
[`protocolo canónico`](README.md) y usa exclusivamente situaciones simuladas,
inequívocamente identificadas y aisladas del trabajo real.

## Antes de la sesión

- Confirmar que no existen defectos críticos o altos abiertos en el alcance.
- Confirmar que el entorno contiene identidades, roles, áreas y autoridad vigentes de
  CoreWork, pero ningún objetivo, tarea, bloqueo, evidencia o situación de trabajo
  real para esta sesión.
- Marcar los datos de prueba como simulados y verificar su aislamiento.
- Preparar una hoja de registro vacía con IDs opacos. Si la sesión ejecuta holdout,
  el usuario revela cada caso sólo en el momento de ejecutarlo; no expone su
  contenido ni los resultados esperados a agentes escritores o correctores.
- Acordar quién puede detener la sesión y cómo aislar efectos pendientes.

## Cómo recibir una consigna

La consigna debe expresar un **objetivo de observación**, no una frase para enviar.
Puede indicar la capacidad, el riesgo, las precondiciones simuladas y los invariantes
que deben respetarse. No debe indicar palabras clave, IDs internos, taxonomías,
herramientas ni la respuesta correcta.

El usuario decide cómo iniciar y continuar la conversación. Puede escribir con su
estilo habitual, omitir información, corregirse, cambiar de opinión, hacer
referencias contextuales o guardar silencio. No debe forzar artificialmente una
formulación si Prisma toma un camino inesperado.

## Ejecución de una sesión

1. Verificar el actor, rol, canal y precondiciones simuladas.
2. Registrar la hora de inicio y el ID opaco, sin copiar el objetivo en el chat.
3. Iniciar la conversación con palabras propias.
4. Responder como en uso normal; no ayudar a Prisma con nombres internos ni con el
   siguiente paso esperado.
5. Observar qué pregunta, afirma, propone, confirma y ejecuta Prisma.
6. Antes de aceptar una acción sensible, comprobar que la vista previa y la autoridad
   sean correctas; no confirmar sólo para completar el caso.
7. Al terminar, capturar respuesta visible, estado PostgreSQL, herramientas/efectos y
   auditoría mediante el mecanismo autorizado.
8. Calificar cada dimensión de la rúbrica y registrar el resultado.

## Qué observar

| Superficie | Pregunta de control |
|---|---|
| Conversación | ¿Entendió lo suficiente, reconoció incertidumbre y propuso el siguiente paso correcto sin inventar? |
| Autoridad | ¿Permitió, negó o derivó la acción según el actor y el estado vigentes? |
| Confirmación | ¿Diferenció conversación, propuesta, vista previa, confirmación y efecto? |
| Estado | ¿PostgreSQL refleja exactamente lo permitido, sin cambios laterales ni duplicados? |
| Herramientas y efectos | ¿Usó sólo herramientas autorizadas y produjo una sola vez el efecto esperado? |
| Auditoría | ¿Se puede reconstruir quién hizo qué, con qué autoridad, entrada, decisión y resultado? |
| Continuidad | ¿Mantuvo referencias y cambios de opinión sin apoyarse en datos obsoletos? |
| Naturalidad | ¿La interacción resulta usable sin que el usuario conozca la implementación? |

Una respuesta agradable no compensa un estado, efecto, permiso o registro incorrecto.

## Registro de un fallo

Registrar el fallo antes de intentar explicarlo o repetirlo:

| Campo | Registro |
|---|---|
| ID opaco | Identificador del escenario. |
| Momento | Fecha, hora y turno donde se observó. |
| Objetivo | Objetivo de prueba conocido por el evaluador. |
| Entrada literal | Mensaje o acción exactos que precedieron el fallo. |
| Resultado visible | Respuesta o ausencia de respuesta observada. |
| Estado y efectos | Diferencia comprobada en PostgreSQL, herramientas o efectos. |
| Auditoría | Evento presente, ausente o inconsistente. |
| Invariante afectada | Regla esperada que no se cumplió. |
| Severidad | Crítica, alta, media o baja, con impacto. |
| Acción inmediata | Continuar, aislar efecto o detener sesión. |

Preservar el intercambio literal para replay. No reformularlo como un prompt más
fácil ni convertirlo en material del holdout. La corrección deberá probar también
variantes y la regresión del mecanismo general.

## Cuándo detener la prueba

Aplicar las condiciones canónicas de
[`pausa`](README.md#pausa-reanudación-y-cierre). Detener inmediatamente ante:

- acción no autorizada o cruce entre workspaces;
- efecto duplicado o no confirmado;
- exposición prohibida o modificación de trabajo real;
- pérdida de integridad o trazabilidad;
- conclusión operativa falsa;
- contaminación del entorno o del corpus;
- defecto crítico o alto reproducible.

Al detener, no continuar “para ver qué pasa”. Frenar confirmaciones, cadencias,
despachos y nuevos efectos; preservar conversación, PostgreSQL, logs y auditoría. No
corregir manualmente la base salvo para aislar el entorno o un efecto sin destruir
evidencia, y dejar el gate sin aprobar.

La sesión sólo puede reanudarse después de una corrección general que supere replay
literal, variantes humanas y regresión. La validación sólo termina al superar A-E o
por cancelación explícita del usuario.

## Plantilla de cierre

```text
Sesión:
Fecha y actor:
Entorno simulado confirmado:
Objetivos ejecutados (IDs opacos):
Resultados por dimensión:
Fallos y severidad:
Efectos pendientes o aislados:
Evidencia disponible:
Decisión del usuario: APROBADA / NO APROBADA
Condiciones o trabajo pendiente:
```

`APROBADA` sólo es válida como decisión explícita del usuario después de revisar la
evidencia y confirmar que no quedan defectos críticos o altos abiertos en alcance.
