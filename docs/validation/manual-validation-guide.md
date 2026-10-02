# Guía de validación manual por Telegram

Esta guía permite al usuario validar Leda mediante Telegram real sin recibir frases
guionadas. Toda sesión usa exclusivamente situaciones ficticias, simuladas,
inequívocamente identificadas y aisladas del trabajo real.

## Tipos de sesión

| Tipo | Momento y propósito | Autoridad del resultado |
|---|---|---|
| Progresiva por circuito | Tan pronto como una unidad está implementada, técnicamente verificada y su circuito cumple el gate acotado. Detecta temprano defectos de UX, comprensión y coordinación, y alimenta replay, regresión y corpus de desarrollo. | Aporta evidencia de desarrollo; no ejecuta holdout, no completa la capa E y no puede aprobar el piloto. |
| Integral de capa E | Después de completar A-D y cumplir el gate final del [`protocolo canónico`](README.md#gates-manuales). Evalúa el sistema completo. | Sólo la aprobación explícita del usuario puede habilitar el piloto real. |

La capa E no es la primera interacción manual. Tampoco se fuerza una sesión progresiva
si el circuito aún no cumple el gate mínimo proporcional.

## Antes de la sesión

- Identificar si la sesión es progresiva por circuito o integral de capa E.
- Para una sesión progresiva, confirmar workspace local o de prueba controlado, sólo
  datos ficticios y sin trabajo real, secreto de Telegram protegido, efectos
  inspeccionables y reversibles, backup, pausa o rollback proporcionado al circuito,
  ausencia de operaciones destructivas e inexistencia de defectos `CRITICAL` o `HIGH`
  abiertos en ese alcance. Si falta una condición, usar un harness determinista o
  `TestClient` en lugar de Telegram.
- Para capa E, confirmar todas las condiciones del gate final, incluidas A-D completas
  y ausencia de defectos críticos o altos abiertos en el alcance integral.
- Confirmar que el entorno contiene identidades, roles, áreas y autoridad vigentes de
  CoreWork, pero ningún objetivo, tarea, bloqueo, evidencia o situación de trabajo
  real para esta sesión.
- Marcar los datos de prueba como simulados y verificar su aislamiento.
- Preparar una hoja de registro vacía con IDs opacos. El holdout permanece reservado y
  nunca se revela en una sesión progresiva. En la capa correspondiente, el usuario
  revela cada caso holdout sólo al ejecutarlo y no expone su contenido ni los
  resultados esperados a agentes escritores o correctores.
- Acordar quién puede detener la sesión y cómo aislar efectos pendientes.

## Cómo recibir una consigna

La consigna debe expresar un **objetivo de observación**, no una frase para enviar.
Puede indicar la capacidad, el riesgo, las precondiciones simuladas y los invariantes
que deben respetarse. No debe indicar palabras clave, IDs internos, taxonomías,
herramientas ni la respuesta correcta.

El usuario decide cómo iniciar y continuar la conversación. Puede escribir con su
estilo habitual, omitir información, corregirse, cambiar de opinión, hacer
referencias contextuales o guardar silencio. No debe forzar artificialmente una
formulación si Leda toma un camino inesperado.

## Ejecución de una sesión

1. Verificar el actor, rol, canal y precondiciones simuladas.
2. Registrar la hora de inicio y el ID opaco, sin copiar el objetivo en el chat.
3. Iniciar la conversación con palabras propias.
4. Responder como en uso normal; no ayudar a Leda con nombres internos ni con el
   siguiente paso esperado.
5. Observar qué pregunta, afirma, propone, confirma y ejecuta Leda.
6. Antes de aceptar una acción sensible, comprobar que la vista previa y la autoridad
   sean correctas; no confirmar sólo para completar el caso.
7. Al terminar, capturar respuesta visible, estado PostgreSQL, herramientas/efectos y
   auditoría mediante el mecanismo autorizado.
8. Calificar cada dimensión de la rúbrica y registrar el resultado.
9. Si hubo un fallo, corregir su causa raíz y agregar replay/regresión antes de
   reanudar; si el comportamiento fue aceptable, preparar el siguiente circuito
   pequeño y endurecer sólo en proporción a la evidencia.

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
Tipo: PROGRESIVA POR CIRCUITO / CAPA E INTEGRAL
Fecha y actor:
Entorno simulado confirmado:
Objetivos ejecutados (IDs opacos):
Resultados por dimensión:
Fallos y severidad:
Efectos pendientes o aislados:
Evidencia disponible:
Resultado de la sesión: APROBADO / FALLIDO / BLOQUEADO / NO CONCLUYENTE
Decisión de capa E, sólo si corresponde: APROBADA / NO APROBADA / NO APLICA
Condiciones o trabajo pendiente:
```

La decisión de capa E `APROBADA` sólo es válida en una sesión integral, como decisión
explícita del usuario después de revisar la evidencia y confirmar que no quedan
defectos críticos o altos abiertos en alcance. Una sesión progresiva siempre registra
`NO APLICA` en ese campo, aun cuando el circuito ejercitado haya aprobado.
