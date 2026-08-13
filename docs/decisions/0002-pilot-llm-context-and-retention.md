# ADR 0002: contexto LLM y retención durante el piloto

- **Estado:** aceptada
- **Fecha:** 2026-08-12
- **Alcance:** validación local simulada y piloto controlado real

## Contexto

Prisma necesita validar si sus respuestas son útiles, completas y operativamente
correctas. Aplicar minimización funcional del contexto antes de contar con evidencia
real podría degradar esas respuestas y agregar otra variable al diagnóstico.

Al mismo tiempo, el contexto amplio aumenta costo y exposición potencial. La
retención de las conversaciones y el tratamiento del proveedor externo también
deben ser explícitos para participantes y administradores. Esta ADR define la
política aceptada; no afirma que los controles administrativos o la selección de
proveedor estén implementados.

## Decisión

Durante la validación local simulada y el piloto controlado real, Prisma usará
**contexto operativo amplio** y no aplicará minimización funcional prematura. Podrá
enviar al modelo los datos operativos autorizados que sean necesarios para priorizar
calidad y completitud de las respuestas.

La política se completa con estas decisiones:

- Anthropic es el proveedor inicial.
- Una futura interfaz permitirá seleccionar proveedor y modelo. Cada proveedor se
  autenticará sólo mediante los métodos oficiales que soporte. Esta capacidad
  futura no queda aprobada como implementada por esta ADR.
- Las conversaciones almacenadas por Prisma en local o en la VPS tienen retención
  indefinida hasta que un administrador autorizado las elimine.
- Los participantes no pueden solicitar el borrado de conversaciones.
- El acceso y la eliminación administrativos deben estar restringidos y auditados.
- La retención externa depende de las condiciones de cada proveedor y debe
  informarse a los participantes.

## Fronteras obligatorias

Contexto amplio no significa contexto sin fronteras. Prisma nunca debe enviar al
proveedor:

- secretos, credenciales o material equivalente;
- datos pertenecientes a otros espacios de trabajo;
- información que el actor no esté autorizado a consultar o utilizar.

También deben respetarse los límites técnicos del proveedor. La conversación y la
memoria no amplían permisos ni reemplazan las reglas de autoridad del sistema.

## Consecuencias

- El piloto reduce el riesgo de atribuir a minimización prematura una respuesta
  incompleta o de baja calidad durante la validación y el piloto.
- El diagnóstico inicial conserva menos variables, pero puede consumir más tokens,
  aumentar latencia y exponer más datos autorizados al proveedor.
- La retención local o en VPS no determina ni modifica la retención externa del
  proveedor.
- Antes de incorporar participantes deben informarse la retención administrada por
  Prisma y las condiciones vigentes del proveedor.
- Restringir y auditar acceso y eliminación requiere implementación y verificación
  separadas; aceptar esta política no demuestra que esos controles existan.
- Cambiar de proveedor, modelo o método de autenticación exigirá respetar las
  capacidades y condiciones oficiales del proveedor elegido.

## Temporalidad

Esta es una decisión temporal para la validación simulada y el piloto controlado, no
la política final de minimización. No debe extenderse por inercia al endurecimiento
VPS. La revisión comienza con evidencia de validación simulada y puede incorporar
evidencia del piloto real si hace falta, según
[`ROADMAP.md`](../ROADMAP.md#revisión-inicial-contexto-llm). Su resultado debe quedar
registrado en una nueva decisión antes del endurecimiento VPS.

## Evidencia que debe capturarse

La evaluación debe permitir comparar, sin incorporar secretos ni datos no
autorizados:

- calidad y utilidad de las respuestas;
- completitud de hechos operativos relevantes y omisiones detectadas;
- categorías y volumen de contexto utilizado;
- tokens y costo por interacción o intención comparable;
- latencia de extremo a extremo;
- exposición de datos autorizados al proveedor e incidentes de frontera;
- límites técnicos y condiciones vigentes de retención, ubicación y uso de datos
  del proveedor;
- casos comparables con contexto amplio y con variantes reducidas o adaptativas en
  una evaluación controlada.

El acceso a muestras de conversación utilizadas como evidencia debe seguir la misma
restricción y auditoría administrativas definidas para las conversaciones.

## Criterio de revisión

La revisión comienza después de la Fase 5 y debe cerrarse antes de iniciar la Fase 7.
Puede usar evidencia adicional de la Fase 6 cuando la validación simulada no alcance.
Para superarla:

1. debe existir evidencia suficiente para comparar calidad, completitud, costo,
   latencia y exposición;
2. deben identificarse degradaciones y riesgos de cada variante evaluada;
3. los responsables organizacionales y técnicos deben tomar una decisión explícita;
4. una ADR posterior debe adoptar, ajustar o reemplazar esta política antes del
   endurecimiento VPS de Fase 7.

El contexto adaptativo por intención es una opción futura para esa revisión. No está
aprobado por esta ADR.

## Alternativas no elegidas

- **Minimización funcional estricta desde el inicio:** descartada para la validación
  y el piloto porque puede degradar respuestas y confundir el diagnóstico sin
  evidencia previa.
- **Contexto adaptativo por intención desde el inicio:** diferido hasta poder
  diseñarlo y validarlo con evidencia real.
- **Contexto sin fronteras de seguridad:** rechazado; autorización, aislamiento,
  exclusión de secretos y límites del proveedor son obligatorios.
- **Vencimiento fijo o borrado solicitado por participantes:** no elegidos para el
  almacenamiento administrado por Prisma durante esta etapa.
