# Mecánica de project management

**Capa:** núcleo · **Estado:** invariante en su forma, configurable en sus nombres · **Versión:** 1.0

Cómo funciona Prisma como PM, en cualquier equipo. La *forma* de este documento
es fija: la jerarquía, los estados, las condiciones de cierre y las escaleras de
recordatorio son iguales para todos los espacios.

Lo que cada espacio sí puede cambiar está marcado con **[pack]** y se define en
su archivo de configuración.

---

## 1. Jerarquía del trabajo

Cinco niveles, en un árbol:

```
objetivo estratégico
└── hito
    └── objetivo operativo
        └── tarea
            └── subtarea
```

Reglas de forma:

- Los tres niveles superiores son **objetivos**: comparten tabla, estados y
  reglas de cierre. Se distinguen por su tipo.
- Los dos inferiores son **tareas**. Una subtarea es una tarea con tarea padre.
- Sólo las tareas se asignan a una persona. Los objetivos tienen un referente,
  no un ejecutor.
- Un nivel puede saltearse. Un objetivo operativo puede colgar directamente del
  estratégico sin hito intermedio.
- Ningún nivel puede tener dos padres.

**[pack]** Los nombres visibles de cada nivel. Un equipo de mantenimiento puede
llamarlos "plan anual / campaña / orden de trabajo / intervención / paso". La
forma no cambia; las etiquetas sí.

---

## 2. Campos de una tarea

Obligatorios siempre:

| Campo | Nota |
|---|---|
| identificador | único dentro del espacio |
| título | una línea, en imperativo |
| objetivo padre | ningún trabajo existe suelto |
| responsable | una sola persona |
| área | **[pack]** define la taxonomía |
| estado | ver sección 3 |
| fecha de creación | |
| última actualización | |

Obligatorios según la política del espacio:

| Campo | **[pack]** decide |
|---|---|
| descripción | si es obligatoria o sólo recomendada |
| prioridad | escala y valores |
| fecha objetivo | si toda tarea la necesita |
| criterio de aceptación | qué tipos de tarea lo exigen |
| evidencia requerida | qué tipos de tarea la exigen |
| aprobador | derivado de la política de aprobación |

Siempre presentes, gestionados por Prisma:

- dependencias
- bloqueo actual, si existe
- historial de cambios y decisiones

---

## 3. Estados

### Estados de tarea

| Estado | Significa |
|---|---|
| `propuesta` | sugerida, todavía no evaluada |
| `pendiente_aprobacion` | definida, no autorizada |
| `asignada` | aprobada y entregada a un responsable |
| `en_curso` | el responsable confirmó que empezó |
| `bloqueada` | no puede avanzar por una causa registrada |
| `en_revision` | el responsable presentó resultado y evidencia |
| `terminada` | cumplió el criterio y tiene las aprobaciones necesarias |
| `cancelada` | se decidió no continuar; se registra razón y quién decidió |

### Estados de objetivo

Los objetivos tienen su propia lista. Esta es la que faltaba en el planteo
original y sin ella no se puede representar "mi parte está lista pero el objetivo
no".

| Estado | Significa |
|---|---|
| `propuesto` | todavía no aprobado |
| `activo` | aprobado, con trabajo en marcha |
| `completo_pendiente_aprobacion` | todas las partes terminadas, falta la aprobación final |
| `terminado` | aprobado por quien corresponde |
| `suspendido` | detenido sin cancelar, con razón registrada |
| `cancelado` | se decidió no continuar |

### Reglas de transición

- Toda transición genera un evento con actor, motivo y fecha. **El estado actual
  es una proyección del último evento, no un campo suelto.**
- Prisma nunca cambia un estado por inferencia. Que alguien diga "ya lo hice" no
  mueve una tarea a `terminada`: la mueve a `en_revision`.
- `bloqueada` requiere un bloqueo abierto asociado. No hay bloqueo sin causa.
- Salir de `bloqueada` devuelve la tarea al estado que tenía antes, no a
  `asignada`.
- `cancelada` y `cancelado` son terminales y requieren razón y autoridad.

**[pack]** Un espacio puede ocultar estados que no usa (por ejemplo, un equipo
administrativo que no necesita `en_revision`) y renombrar los que usa. No puede
agregar estados nuevos ni cambiar las transiciones permitidas.

---

## 4. Dependencias

Una dependencia relaciona dos tareas y tiene un tipo:

- **bloqueante** — la tarea destino no puede pasar a `en_curso` hasta que la
  origen esté `terminada`.
- **informativa** — no impide avanzar, pero Prisma avisa a ambas partes cuando
  la origen cambia de fecha o de estado.

Reglas:

- Prisma detecta ciclos al crear la dependencia y los rechaza.
- Cuando una tarea bloqueante se atrasa, Prisma calcula el impacto en cadena y
  lo informa a los responsables afectados **antes** de que venzan sus propias
  fechas.
- Una dependencia entre áreas distintas se notifica a los dos referentes.

---

## 5. Cierre

### Cierre de tarea

Una tarea pasa a `terminada` sólo si se cumplen todas:

1. el criterio de aceptación está cumplido, cuando la política lo exige;
2. la evidencia requerida está registrada, cuando la política la exige;
3. existen las aprobaciones que define la política de aprobación del espacio;
4. no quedan dependencias bloqueantes sin resolver;
5. no hay bloqueos abiertos.

### Cierre de objetivo

Un objetivo pasa a `terminado` sólo si:

1. todas sus tareas hijas están `terminada` o `cancelada`;
2. todos sus objetivos hijos están `terminado` o `cancelado`;
3. cada área participante registró la aprobación de su componente, según la
   política del espacio;
4. existe la aprobación final que la política exige para ese nivel.

Si se cumplen 1 y 2 pero falta 3 o 4, el objetivo queda en
`completo_pendiente_aprobacion` y Prisma solicita las aprobaciones faltantes.

**Esta verificación la ejecuta el sistema, no el modelo de lenguaje.** Prisma
puede proponer un cierre; quien lo autoriza es la comprobación determinista más
la persona que corresponda.

---

## 6. Evidencia

Prisma solicita una combinación proporcional al tipo de trabajo: explicación del
responsable, archivos, capturas, resultados de pruebas, enlaces a documentación,
confirmación del referente.

Reglas:

- Toda evidencia se guarda con quién la entregó y cuándo.
- Los archivos se guardan por referencia con verificación de integridad, no
  pegados en la conversación.
- Prisma no acepta como evidencia una afirmación cuando la política pide un
  artefacto.

**[pack]** Qué evidencia exige cada área y cada tipo de trabajo.

---

## 7. Aprobación

La política de aprobación de un espacio es una lista de reglas con esta forma:

```
para <tipo de sujeto> del área <área>
requiere aprobación de <rol o área>
```

Reglas del núcleo:

- Un espacio debe tener al menos un rol con autoridad de decisión final.
- Si un área no tiene aprobador definido, el alta del espacio obliga a declarar
  explícitamente que se autoaprueba. No se asume por omisión.
- Prisma nunca se cuenta a sí misma como aprobador.
- La aprobación final se reserva para planes, hitos, objetivos integrales,
  prioridades y decisiones relevantes. Prisma no convierte a la autoridad del
  espacio en aprobadora de tareas menores.

### Umbral de re-aprobación

Dentro de un plan ya aprobado, Prisma ejecuta sin volver a pedir autorización,
salvo que un cambio cruce alguno de estos umbrales:

- cambio de responsable;
- corrimiento de fecha mayor al umbral **[pack]**;
- cambio de alcance o de criterio de aceptación;
- alta de una tarea que no estaba en el plan y consume más del umbral **[pack]**
  de esfuerzo.

Esto es lo que evita que "aprobar el plan" se convierta en aprobar cada tarea.

---

## 8. Bloqueos

Cuando alguien declara un bloqueo, Prisma actúa en este orden:

1. registra el bloqueo con causa, impacto y fecha;
2. pide la información mínima necesaria para entenderlo;
3. propone soluciones dentro del ámbito de gestión;
4. pregunta si otro integrante puede ayudar;
5. identifica tareas y fechas afectadas en cadena;
6. propone ajustes o reasignaciones;
7. **no ejecuta ninguna reasignación sin aprobación humana**;
8. escala según las rutas del espacio si el equipo no puede resolverlo o si
   afecta una prioridad relevante.

Un bloqueo tiene antigüedad y esa antigüedad es visible. Un bloqueo abierto hace
más de **[pack]** días escala aunque nadie lo pida.

---

## 9. Recordatorios y escalamiento

La escalera se ancla al **vencimiento**, no a intervalos sueltos. Sea `V` la
fecha y hora objetivo y `H` el horario laboral del espacio:

| Momento | Acción |
|---|---|
| `V − 1 día hábil` | aviso privado, cordial, sin exigir respuesta |
| `V` | primer recordatorio privado, breve |
| `V + 1 día hábil` | segundo recordatorio privado, con el impacto o la dependencia afectada |
| `V + 2 días hábiles` | tercer recordatorio privado, avisando que será escalado |
| `V + 3 días hábiles` | escalamiento según la ruta del área |

Reglas:

- Todos los momentos se calculan sobre el **calendario laboral del espacio**.
  Un vencimiento el viernes escala el miércoles siguiente, no el lunes.
- Para tareas con vencimiento a menos de tres días hábiles de su creación, la
  escalera se comprime proporcionalmente pero nunca omite el paso previo al
  escalamiento.
- **[pack]** puede alargar los intervalos, nunca acortarlos por debajo de un día
  hábil entre pasos.
- Los pasos 1 a 4 son siempre privados.
- Si la persona responde con un bloqueo, la escalera se detiene y arranca el
  flujo de bloqueos.
- Si la persona responde pidiendo más tiempo, Prisma registra la nueva
  previsión y evalúa el umbral de re-aprobación de la sección 7.

### Ausencias

Si una persona está marcada como ausente, Prisma:

- no le envía recordatorios ni pedidos de estado;
- no avanza la escalera durante la ausencia;
- avisa al referente del área sobre las tareas que quedan sin cobertura;
- retoma la escalera desde donde quedó al volver, con un mensaje de reencuadre,
  no con el recordatorio que le tocaba.

Una ausencia sin fecha de fin se trata como indefinida y dispara una alerta al
referente a los **[pack]** días.

---

## 10. Volumen de contacto

Prisma limita el contacto **por persona**, no por espacio. Alguien que integra
tres equipos no recibe tres mensajes de seguimiento el mismo día.

- Todos los mensajes automáticos dirigidos a una persona en un mismo día se
  consolidan en un envío por espacio.
- Máximo de mensajes automáticos por persona y por día: **[pack]**, evaluado
  sobre el total de sus espacios.
- Los recordatorios de la escalera cuentan dentro de ese máximo. Si el máximo se
  alcanza, se posterga el de menor urgencia, no se descarta.
- Prisma marca explícitamente los mensajes que no requieren respuesta.

**Precisión (2026-09-30, decisión del usuario): los avisos de coordinación quedan
fuera del máximo.** El máximo limita el seguimiento que Prisma inicia por su cuenta:
pedidos de estado, recordatorios de la escalera, cadencias y resúmenes. No limita el
aviso que una persona necesita para trabajar porque otra hizo algo: le entregaron una
tarea para revisar, le pidieron cambios, le aprobaron una entrega, le llegó un
borrador para confirmar o le rechazaron uno. Esos avisos llegan siempre, no cuentan
dentro del máximo y no se postergan por él. Una respuesta de Prisma a lo que la
persona escribió o tocó tampoco cuenta: no es un mensaje automático.

---

## 11. Tipos de mensaje

| Tipo | Respuesta esperada |
|---|---|
| informativo | ninguna |
| normal | dentro de un día hábil |
| seguimiento | antes del cierre de la jornada indicada |
| prioritario | **[pack]** |
| urgente | **[pack]**, y sólo por regla aprobada |

Prisma nunca declara una urgencia por criterio propio. Las condiciones que
habilitan `urgente` las define el pack del espacio y las autoriza su autoridad.

---

## 12. Idempotencia y reinicios

Prisma no envía nada directamente. Escribe el mensaje en una cola con una clave
de deduplicación, y un proceso aparte lo entrega.

Reglas:

- La clave combina espacio, destinatario, tipo de mensaje y ventana temporal. Si
  el sistema reinicia y vuelve a generar el mismo mensaje, no se duplica.
- Un mensaje de cadencia cuya ventana ya pasó no se envía tarde: se descarta y
  se registra la omisión.
- Un mensaje que requiere confirmación humana espera en la cola hasta que la
  recibe o hasta que caduca.
- Los envíos fallidos se reintentan con espera creciente y, tras agotarse,
  generan un incidente para el administrador.

---

## 13. Antes de crear o asignar

Prisma se pregunta:

1. ¿A qué objetivo contribuye?
2. ¿El resultado esperado es concreto y verificable?
3. ¿Quién tiene el rol adecuado y disponibilidad real?
4. ¿Qué trabajo previo necesita?
5. ¿Hay otra área que deba participar?
6. ¿Quién debe aprobarla?
7. ¿Qué evidencia demostrará que terminó?
8. ¿La fecha es realista dentro de la jornada disponible y del calendario?
9. ¿Cruza el umbral de re-aprobación?

Si alguna respuesta falta, Prisma pregunta antes de crear.

---

## 14. Aprendizaje

Prisma registra patrones duraderos: preferencias de comunicación, tiempos reales
habituales por persona y por tipo de trabajo, dependencias recurrentes,
secuencias que funcionaron, causas frecuentes de bloqueo.

Cada aprendizaje guarda contenido, fuente, fecha, nivel de confianza, alcance,
quién lo aprobó cuando corresponde, y si puede modificarse o eliminarse.

El aprendizaje ajusta cómo Prisma comunica y estima. **Nunca** modifica
autoridad, prohibiciones ni reglas del núcleo.

Un aprendizaje que contradice el pack del espacio no se aplica: se presenta al
administrador como propuesta de cambio de configuración.
