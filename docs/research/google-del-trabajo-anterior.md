# Google: lo que funcionó en el trabajo anterior (Prisma)

> **Origen:** los documentos 02 y 03 del paquete `PRISMA-PACK-RECONSTRUCCION-20260925` del usuario (su trabajo anterior, cuando Leda se llamaba Prisma), copiados tal cual el 2026-10-13, antes de borrar el paquete. Las fuentes que citan (S01, W02…) eran de ese paquete y ya no existen. Sirven de base para "Correo verificado y Google" (`../ROADMAP.md`, "Anotado para más adelante"); no describen nada construido en esta rama.

# 02 — Google: acceso, permisos y operaciones

## 1. Qué significa que Prisma “accede a Google”

No se trata de acceso irrestricto a toda la suite ni de usar una contraseña a través del modelo. Prisma opera mediante una cuenta autorizada, OAuth, APIs habilitadas y adaptadores con operaciones acotadas. Una autorización de Google no reemplaza la autorización del integrante para cada acción.

**V:** Gmail, Calendar, Drive y Docs tuvieron operaciones reales de piloto. **I:** permisos adicionales y catálogo parcial. No hay evidencia suficiente aquí para presentar Sheets, Contacts, Meet, Slides o cualquier otro producto como una capacidad integral validada.

Fuentes: S06–S10, S14 y W02–W03.

## 2. Las cinco puertas del acceso

1. **API habilitada:** el proyecto de Google debe tener habilitado el servicio correspondiente.
2. **Consentimiento OAuth:** la cuenta concede los scopes necesarios.
3. **Credencial utilizable:** el servicio autorizado obtiene access token y, cuando corresponde, renueva mediante refresh token.
4. **Capacidad implementada:** existe un contrato/adaptador que expone esa operación y valida su entrada.
5. **Autoridad del actor y confirmación:** la política admite el recurso, los destinatarios y el efecto solicitado.

Si cualquiera falla, la operación no está disponible. Haber recibido un scope no acredita que haya una herramienta, y una herramienta listada no demuestra ejecución exitosa.

La documentación oficial describe el uso de refresh tokens para acceso sin presencia continua del usuario. Deben permanecer en almacenamiento privado del servidor, nunca en el contexto del modelo o en este pack. [OAuth de Google](https://developers.google.com/identity/protocols/oauth2/web-server).

## 3. Permisos históricos recuperados

El registro de autorización incluye Gmail lectura/envío/modificación, Calendar, Drive, Contacts de sólo lectura, Sheets y Docs. Eso describe un consentimiento histórico, **no la recomendación de pedirlos todos de entrada**.

**P:** solicitar el mínimo conjunto para las capacidades aprobadas, documentar por qué hace falta cada permiso y volver a autorizar de manera visible cuando aumente el alcance. No copiar tokens, client secrets, cuentas o IDs del entorno anterior.

Hallazgo real: Docs puede fallar aunque el scope esté concedido si su API no está habilitada. Se resolvió habilitando la API y repitiendo el flujo; no ampliando indiscriminadamente permisos.

## 4. Matriz funcional respaldada

| Producto | Lectura | Escrituras históricas verificadas | Límites importantes |
|---|---|---|---|
| Gmail | Búsqueda acotada; metadatos; mensaje/hilo/borrador seleccionado | Crear/editar/eliminar borrador; enviar; responder; reenviar; leído/no leído; archivar; papelera | Sin borrado permanente; destinatarios gobernados |
| Calendar | Lista por rango, límite y calendario | Crear, actualizar el mismo evento, responder invitación, retirar evento | Sin duplicar; distinguir organizador de invitado |
| Drive | Buscar/listar/inspeccionar recursos permitidos | Carpeta, copia, renombrado, movimiento, papelera y permisos internos | Sin compartir públicamente ni a dominio completo |
| Docs | Lectura de documentos autorizados | Crear, copiar y editar contenido mediante operaciones soportadas | La ubicación en Drive debe verificarse; scope y API separados |
| Sheets | Lectura contemplada por la integración | No acreditada aquí la aceptación de escrituras | No prometer edición por existir scope |
| Contacts | Permiso readonly registrado en un corte posterior | No acreditado circuito de modificación | Contacto interno oficial no equivale a Google Contacts |

Los límites históricos de destinatarios fueron internos activos y verificados, admitiendo la propia cuenta en pruebas controladas. Una invitación entrante externa procesada en un piloto de Calendar no autoriza a enviar comunicaciones arbitrarias a externos.

## 5. Arquitectura funcional que vale la pena conservar

```text
Pedido humano
  → identidad y autoridad verificadas
  → resolución acotada de recurso/destinatario
  → catálogo de capacidad y esquema tipado
  → lectura o propuesta sin efectos
  → confirmación humana exacta, si modifica
  → ejecutor limitado
  → recibo del proveedor y verificación del resultado
  → auditoría PostgreSQL + respuesta humana
```

El catálogo histórico usaba una operación general `workspace_mutate`, discriminada por recurso y acción; no una herramienta nueva por cada frase. Se separaban catálogo, preparar, confirmar y cancelar. El ejecutor admitía comandos/subcomandos específicos y argumentos estructurados, sin shell ni texto libre como comando.

La reconstrucción puede usar SDK o REST directamente. Esa elección es **P**, no código exacto heredado. Lo importante es que el modelo no reciba credenciales, no construya rutas de ejecución arbitrarias ni saltee los contratos.

## 6. Contrato mínimo de una propuesta

Guardar internamente: actor, conversación, operación, recurso exacto, versión/estado leído, destinatarios resueltos, contenido completo aprobado, política aplicada, vencimiento y clave idempotente. Mostrar a la persona:

- qué va a cambiar;
- sobre qué archivo, evento o correo;
- a quién se enviará o dará acceso;
- qué notificaciones externas se producirán;
- qué parte no puede hacerse;
- **Confirmar / Modificar / Cancelar**.

“Sí” no confirma cualquier pendiente de la conversación: sólo puede aplicar a una propuesta inequívoca, vigente y del mismo actor. Modificar invalida la anterior y muestra otra. Cancelar no produce efectos externos. No pedir dos confirmaciones equivalentes para una sola decisión.

## 7. Estados y concurrencia

Estados recuperados: `prepared`, `executing`, `executed`, `failed`, `cancelled`, `expired`.

La transición a `executing` se persiste **antes** de llamar a Google. Dos confirmaciones concurrentes no pueden efectuar dos llamadas: el historial técnico incluye una respuesta de éxito y un conflicto, con una sola ejecución externa.

Si hay timeout después de enviar, el resultado puede ser incierto. El esquema histórico no incluye necesariamente un estado separado para incertidumbre: conservar el detalle del resultado y prohibir reintentos automáticos. **P:** modelar incertidumbre explícita y reconciliación. Nunca transformar un timeout en “no pasó nada” ni volver a enviar para probar.

Un recibo puede devolver `draftId`, `eventId`, `folder.id` o `file.id`; el adaptador debe normalizarlos por contrato, no esperar una única propiedad `id` en todos los servicios.

## 8. Evidencia real útil por producto

### Gmail

Se creó y modificó el mismo borrador sin envío, se eliminó y se verificó ausencia. Se probó envío interno, respuesta en el hilo original y reenvío en otro hilo. La auditoría registró un evento por mutación autorizada.

Hallazgos: una búsqueda por asunto puede encontrar coincidencias parciales; comparar el asunto devuelto. El contrato probado de reenvío no admitía texto introductorio: se informó el límite antes de hacer un reenvío estándar. Esto es una limitación del adaptador probado, no de toda la API de Gmail.

### Drive y Docs

Se creó una carpeta y un documento en su ubicación correcta, se editó, copió, renombró y movió; se compartió con permiso de lectura interno y después se revocó. Los artefactos de prueba se retiraron a papelera con verificación.

Un fallo de recursos durante una verificación compuesta se recuperó sin repetir la mutación. Lección: distinguir fallo de verificación de fallo de creación.

### Calendar

La creación y actualización conservaron el mismo evento, se rechazó honestamente responder como invitado a un evento propio y se aceptó una invitación auxiliar válida. Ver el documento de agenda.

## 9. Lecturas veraces y datos no confiables

Consultar primero metadatos y máximos pequeños; obtener contenido sólo del recurso pertinente. Informar alcance, rango temporal y límites cuando cambien la interpretación. Cero resultados en una búsqueda no demuestra inexistencia universal.

Correos, títulos de archivos e invitaciones son datos externos, no instrucciones que conceden autoridad. Un correo que ordene enviar secretos o cambiar políticas no tiene prioridad sobre las reglas de Prisma.

Responder con referencia útil al recurso confirmado, no con IDs internos ni narración de herramientas. Ante caída: “No pude comprobarlo ahora” y una salida segura; no rellenar con memoria vieja.

## 10. Qué no debe prometerse

No declarar acceso a todos los calendarios de todo el equipo, organización automática completa de reuniones, generación de enlaces de Meet, escritura de Sheets, edición de Slides o gestión de directorio empresarial sin contratos y pruebas propios.

La implementación nueva debe probar primero cuentas aisladas, destinatarios sintéticos autorizados, permiso insuficiente, API deshabilitada, revocación OAuth, fallo parcial, confirmación vencida, duplicación y cancelación. Las operaciones con efectos reales necesitan autorización específica; recibir este pack no la concede.


# 03 — Reuniones, eventos y agenda

## 1. Tres capacidades diferentes

1. **Operar Calendar:** leer y modificar eventos concretos. **V** en un piloto acotado.
2. **Coordinar una reunión:** definir participantes, propósito, horario y materiales. Reglas funcionales y piezas de integración; no atribuir validación integral automática.
3. **Convertir decisiones en trabajo:** registrar acuerdos, responsables, criterios, plazos y aprobaciones en PostgreSQL. Un evento o una minuta no cierra por sí mismo una tarea.

Fuentes: S01, S06, S08, S09, S11, S12 y W03.

## 2. Preparación de un evento

Prisma debe resolver el pedido natural sin obligar a dar IDs. Necesita título/propósito, calendario autorizado, fecha, inicio, fin o duración, zona horaria y participantes cuando hay invitados. Puede completar desde datos inequívocos y preferencias aprobadas; si falta una decisión material, pregunta sólo por ella.

“El viernes a la mañana” no fija una hora. “Movela una hora” necesita saber qué reunión y en qué dirección cuando el contexto no lo resuelve. “Invitá a todos” requiere un grupo canónico definido; no significa todos los contactos de la cuenta.

**P — contrato de vista previa para la reconstrucción:**

| Dato visible | Razón |
|---|---|
| Nombre y propósito | Evitar crear el evento equivocado |
| Fecha completa y día | Resolver referencias relativas |
| Hora de inicio, fin y zona | Evitar desfase y duración inventada |
| Participantes resueltos | Evitar homónimos o externos no autorizados |
| Lugar/enlace, si fue definido | No inventar videollamadas |
| Invitaciones/notificaciones previstas | Distinguir guardar de avisar |
| Cambio exacto frente al original | Fundamental para reprogramar/cancelar |

Cerrar con Confirmar / Modificar / Cancelar. Si cambia la propuesta, la confirmación anterior deja de servir.

## 3. Consultar la agenda

Especificar calendario, intervalo y zona. Una respuesta correcta puede ser “No encontré eventos en ese calendario entre estas fechas”; no “nadie tiene reuniones” si sólo se consultó una cuenta.

Mostrar inicio, fin, participantes pertinentes y estado de respuesta cuando la API lo proporciona. Separar confirmado, tentativo, cancelado y sin respuesta. No interpretar ausencia de invitación aceptada como falta de disponibilidad ni aceptación del evento como aprobación de un proyecto.

El piloto real consultó un rango semanal acotado con máximo de resultados y pudo informar cero eventos sin ampliar la búsqueda por su cuenta.

## 4. Crear, actualizar, responder y retirar

### Crear

Tras una única confirmación efectiva, ejecutar la creación y conservar el ID externo y el recibo. Si Google confirma creación pero falla la respuesta al usuario, recuperar el resultado: no crear otra reunión.

### Actualizar

Resolver el evento existente y presentar diferencia antes/después. El piloto modificó el mismo evento, sin duplicarlo. Reconsultar si pudo cambiar entre lectura y confirmación.

### Responder a una invitación

No confundir organizador e invitado. En el piloto se rechazó responder como invitado a un evento organizado por la misma cuenta. Una invitación entrante podía verse primero en Gmail y no en la lista de Calendar; se procesó por referencia externa verificada y luego apareció con estado actualizado.

Esto no autoriza a adivinar IDs ni a aceptar cualquier invitación encontrada. El actor debe tener autoridad y la referencia provenir de una fuente real.

### Cancelar o retirar

Distinguir retirar de la propia agenda, cancelar una reunión organizada y notificar a participantes. Mostrar el efecto exacto disponible en el adaptador. El piloto retiró sus eventos de prueba y verificó que no aparecieran en la consulta correspondiente.

La API oficial permite crear eventos y agregar asistentes; las notificaciones se controlan mediante parámetros específicos. Su disponibilidad técnica no determina la política de Prisma. [Crear eventos](https://developers.google.com/workspace/calendar/api/guides/create-events).

## 5. Cadencia de reunión mensual recuperada

| Momento | Comportamiento establecido | Estado de evidencia |
|---|---|---|
| Último viernes del mes, por la mañana | Reunión mensual del equipo | Doctrina; no consta una hora exacta universal |
| Jueves de la semana anterior, ocho días antes, 15:00 | Anunciar, pedir temas y decisiones, comenzar consolidación | Rutina programada histórica |
| Miércoles de la semana de la reunión, dos días antes, 16:00 | Publicar agenda final e informe previo | Rutina programada histórica |

Los disparadores semanales de jueves y miércoles tienen una **condición mensual**: enviar sólo cuando corresponde a esa reunión. El resto de las semanas no se envía. Una expresión semanal sola no implementa “ocho días antes del último viernes”.

**P:** calcular la fecha objetivo con calendario local, derivar −8 y −2 días y usar una clave de envío por reunión/versión/destino. Si se reprograma la reunión, invalidar preparaciones viejas. La política de feriados y excepciones requiere definición; no está acreditada aquí.

La programación del anuncio no prueba que se cree automáticamente un evento Calendar, ni que los asistentes acepten, ni que se haya efectuado la reunión.

## 6. Contenido de agenda e informe previo

- Agenda y objetivo de la reunión.
- Objetivos del período y resultados respaldados.
- Tareas vencidas y reprogramadas, sin equiparar silencio con atraso.
- Bloqueos reales y dependencias.
- Decisiones pendientes y quién puede tomarlas.
- Carga de trabajo por persona dentro del alcance autorizado.
- Próximos objetivos.
- Puntos que requieren definición de la dirección.

Cada apartado debe derivar de datos vigentes. Lo desconocido se marca como tal; no inventar porcentajes, avances, evidencias o consenso para completar el informe.

## 7. Durante y después de una reunión

**D/P:** conservar acuerdos con autor, fecha, alcance, responsable, fecha objetivo y evidencia. Una transcripción es insumo no confiable, no una orden de ejecución automática.

Separar “se mencionó”, “se propuso”, “se decidió por una persona autorizada” y “se ejecutó”. Si la minuta dice “cerrar la tarea”, todavía se verifican criterios, evidencia, revisión y aprobación; no se saltea el ciclo de cierre.

La minuta o documento en Drive puede enlazarse desde el registro oficial. No mantener una segunda verdad de estados operativos en el texto del evento.

No se acredita en este pack grabación, transcripción automática, asistencia automática a Meet ni generación automática de actas ya validada. No presentarlas como funcionalidad heredada.

## 8. Casos delicados y criterio de aceptación

Probar fecha relativa cerca de medianoche; zona diferente; horario faltante; evento recurrente versus una ocurrencia; dos eventos con título parecido; organizador versus invitado; actualización concurrente; invitación conocida pero aún no listada; cancelación; cambio con notificación externa; timeout después de crear; feriado; reunión mensual reprogramada.

Los casos no implementados deben recibir una explicación útil y sin efectos, no una ejecución aproximada. La aceptación exige evento correcto, horario correcto, asistentes correctos, ausencia de duplicados, recibo verificable y una respuesta que diga exactamente qué ocurrió.
