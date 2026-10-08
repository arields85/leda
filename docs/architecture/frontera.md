# La frontera

> **Nota del 2026-10-04, actualizada después del paso M1.** El
> [ADR 0017](../decisions/0017-por-chat-los-hechos-por-la-web-la-estructura.md) (aceptado) recortó
> la superficie conversacional: por chat, Leda registra hechos del trabajo (el seguimiento); la
> estructura (crear, aceptar o reasignar tareas, cambiar fechas, gestionar integrantes) va a una
> plataforma web que lleva su propio ADR antes del código. El
> [ADR 0018](../decisions/0018-motor-de-conversacion.md) (aceptado el 2026-10-06, después de
> la prueba chica) diseña el motor de conversación que reemplaza a los flujos A y B. Ese motor **no está
> construido**: su lugar en esta frontera está en "El motor de conversación", más abajo. Las tablas
> de puertos y de adaptadores ya reflejan los dos ADR.

Este documento define dónde termina el núcleo de Leda y dónde empiezan sus
adaptadores. Gobierna a los demás documentos de arquitectura: ante una discrepancia,
prevalece esta frontera.

## Por qué existe

Sin una frontera declarada, cada falla operativa empuja la lógica hacia donde
resulta más fácil escribirla. Eso ya ocurrió en este proyecto.

Dos ejercicios progresivos fallaron porque el modelo no iniciaba de forma confiable
el circuito de creación de tareas. En ambos casos la corrección movió autoridad hacia
el servidor. El resultado acumulado fue que `src/leda/ingreso_tareas.py` llegó a 1218
líneas, más que `src/leda/agente.py` (290) y `src/leda/herramientas.py` (573)
sumados. Los dos primeros se borraron con los flujos A y B (E3-4).

Cada una de esas correcciones fue técnicamente razonable. Ninguna fue una decisión
de arquitectura tomada de frente. La frontera existe para que la próxima corrección
tenga un lugar declarado al que pertenecer.

## Mapa

```text
        ┌─────────────────────────────────────────────────┐
        │                  ADAPTADORES                    │
        │                                                 │
        │   Telegram    HTTP lectura    Móvil    Packs    │
        │   Proveedores LLM                               │
        └────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────────────────────────────────────┐
        │                    PUERTOS                      │
        │                                                 │
        │  Intención   Notificación   Lectura             │
        │  Configuración   Razonamiento                   │
        └────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────────────────────────────────────┐
        │                     NÚCLEO                      │
        │                                                 │
        │  Objetivos e hitos      Autoridad y membresías  │
        │  Tareas y estados       Seguimiento             │
        │  Dependencias           Cadencias               │
        │  Bloqueos               Evidencias              │
        │  Aprobaciones           Auditoría               │
        └─────────────────────────────────────────────────┘
```

## Núcleo de dominio

El núcleo contiene el modelo de gestión de proyectos y las reglas que lo hacen
confiable:

- objetivos, hitos y objetivos operativos;
- tareas, y su estado como **proyección de eventos**, nunca como campo editable;
- dependencias entre trabajos y entre áreas;
- bloqueos, con causa, impacto y antigüedad;
- evidencias y aprobaciones;
- autoridad, membresías y revalidación de permisos;
- el ciclo de seguimiento y la escalera de recordatorios;
- las cadencias y el calendario laboral.

**Regla del núcleo:** no sabe qué es Telegram. No conoce un `chat_id`, un botón, un
límite de caracteres ni un identificador de mensaje de un canal concreto. Si el
núcleo necesita avisarle algo a una persona, expresa *a quién* y *qué*, nunca *por
dónde* ni *con qué formato*.

## Puertos

Un puerto es un contrato que el núcleo define y un adaptador implementa.

| Puerto | Contrato |
|---|---|
| Intención | Recibe la intención de una persona ya identificada y autorizada, sin formato de canal. |
| Notificación | Entrega un mensaje dirigido a una persona, sin conocer su transporte. |
| Lectura | Expone consultas agregadas del estado para cualquier superficie de lectura. Implementado en `src/leda/lectura.py`; ninguna de sus funciones recibe el espacio, lo toman de la sesión. |
| Configuración | Materializa y modifica la configuración de un cliente. Tiene dos productores: el paquete versionado, que la siembra una vez, y la edición desde el tablero del cliente. El paquete es formato de transporte, no fuente de verdad: después de sembrar, manda la base. Toda edición queda atribuida en la auditoría. |
| Razonamiento | Interpreta lenguaje natural y devuelve salida tipada y validada: el comando y los valores normalizados de lo que la persona dijo. Redacta la respuesta a partir del resultado del turno ([`ADR 0014`](../decisions/0014-flujo-de-un-mensaje.md)). En el motor de conversación, la IA elige una o más jugadas de una lista cerrada declarada en el código y redacta desde lo que el código informa ([`ADR 0018`](../decisions/0018-motor-de-conversacion.md), decisión 1; diseñado, sin construir). |
| Decisión con duda | Elige entre candidatos de la base (una tarea, una persona, un objetivo) con probabilidades; el núcleo aplica los cortes. No interpreta lenguaje libre ni decide efectos ([`ADR 0014`](../decisions/0014-flujo-de-un-mensaje.md)). En la prueba chica corre en paralelo sin decidir y se queda sólo si evita errores ([`ADR 0018`](../decisions/0018-motor-de-conversacion.md), decisión 7). |

## Adaptadores

| Adaptador | Estado | Evidencia |
|---|---|---|
| Telegram | Existe | `src/leda/despachador.py:66` |
| Proveedores LLM | Existe uno, descartable | El cliente de la prueba chica (`prueba_chica/ia_real.py`), compatible con OpenAI; `src/leda/llm.py` guarda sólo las direcciones de los proveedores y el tiempo máximo. Los proveedores de los flujos A y B se borraron (E3-3). |
| Jev (decisión con duda) | No existe | `src/leda/jev.py` se borró con los flujos A y B (E3-4); la prueba chica lo dejó fuera ([`ADR 0018`](../decisions/0018-motor-de-conversacion.md), nota de la decisión 7). |
| Importador de paquetes | Existe | `src/leda/importador.py:211` |
| Tablero de cliente | Existe en parte | La lectura: `GET /tablero/{token}` (`src/leda/entrada.py`), con enlace personal, consume el puerto de Lectura. La parte que consume el de Configuración no existe. Alcanza un solo espacio. |
| Panel de plataforma | No existe | Alcanza todos los espacios: da de alta clientes y conduce la entrevista de alta (que no aplica en esta etapa: ADR 0017, decisión 7). Su autenticación es una decisión abierta. |
| Plataforma web de tareas | No existe | [`ADR 0017`](../decisions/0017-por-chat-los-hechos-por-la-web-la-estructura.md), decisión 5: carga de tareas con un formulario, su estado, cambio de fechas por retrasos e integrantes. Lleva su propio ADR antes del código; si es parte del tablero, del panel o una superficie aparte, y cómo cumple el [`ADR 0004`](../decisions/0004-dos-superficies-separadas.md), está `PENDIENTE` en ese ADR. |
| Aplicación móvil | No existe | — |

Las dos superficies web son adaptadores distintos y aplicaciones separadas, por
[`ADR 0004`](../decisions/0004-dos-superficies-separadas.md). No es una preferencia
de organización: el dato de todos los clientes no debe existir en el proceso que
atiende a uno solo.

El adaptador de Telegram está bien construido: `TransporteTelegram` queda aislado
detrás de una interfaz de envío y tiene un doble de prueba equivalente. El problema
no es el adaptador, es que el núcleo lo conoce.

## El motor de conversación

Diseñado en el [`ADR 0018`](../decisions/0018-motor-de-conversacion.md) y **sin construir**. Hoy
la conversación de `main` son los flujos A y B, congelados, que se borran en la Etapa 3 del Motor.

| Qué | Dónde queda respecto de la frontera |
|---|---|
| La IA | Del lado del puerto de Razonamiento: elige jugadas de una lista cerrada y redacta desde los hechos. No decide efectos (decisión 1). |
| Las jugadas y las situaciones generales | Fichas declaradas en el código, un conjunto cerrado, nunca configuración de un cliente (decisión 4). El código comprueba cada jugada y ejecuta con las operaciones del dominio y su confirmación. |
| El estado por persona y el registro de turnos | Tablas nuevas, con `workspace_id` y `row level security` forzado, sin `chat_id` ni `callback_data`: cumplen las reglas 1, 2 y 3 (decisión 3). Sus columnas, `PENDIENTE` hasta el plan de la Etapa 2. |
| El paquete del motor | Propuesta del documento de la unidad, no fijada por el ADR: un paquete que sólo alcanza una lista permitida de módulos sólidos, con su prueba de frontera. Se construye en la Etapa 3. |
| Los archivos y la evidencia de la entrega ([`ADR 0019`](../decisions/0019-evidencia-y-pagina-de-la-tarea.md); migraciones `0033` y `0034`) | `archivo` es del dominio: el contenido con su huella, sin ningún identificador de Telegram (regla 2); los de Telegram quedan en `archivo_de_mensaje`, del lado del transporte. `evidence` guarda la clase de cada pieza (texto, imagen, archivo o enlace, que fija el código por el contenido), el archivo y los tipos de la política que cubre; `evidencia_retirada` (el retiro de una pieza) y `archivo_de_tarea` (lo que la persona dijo que es de una tarea antes de entregarla) sólo se agregan. Todas con `workspace_id`, `row level security` forzado y referencias del mismo espacio (regla 1); ninguna función nueva es `security definer`. Qué clases cubre cada tipo es dato del pack, versionado con la política (`task_evidence_policy.tipos`, regla 5). |

La prueba chica de la Etapa 2 vive fuera de `src/leda` y no cambia esta frontera.

## Reglas invariantes

1. **El aislamiento entre clientes es la invariante número uno.** Toda tabla con
   alcance de espacio lleva `workspace_id`, tiene `row level security` forzado y una
   política de aislamiento. Ninguna función `security definer` queda sin propietario
   explícito y verificado.
2. **El núcleo no conoce el transporte.** Ningún identificador propio de un canal
   cruza hacia el dominio ni hacia el modelo de datos de dominio.
3. **Ningún límite de transporte decide la validez de un dato de negocio.** Los
   límites de tamaño, formato y división pertenecen al adaptador de salida.
4. **El estado se escribe por eventos.** Nunca por `update` directo sobre la
   proyección.
5. **La configuración del cliente es dato versionado.** Nunca código, nunca tipo
   enumerado, nunca constante.
6. **La autoridad se revalida en la frontera.** Nunca se confía en el actor, el
   espacio ni el permiso que declare el llamador.

## Cumplimiento actual

Esta tabla es el estado real, no el deseado. Dos de las seis reglas siguen
incumplidas hoy, y una es parcial.

| Regla | Estado | Evidencia |
|---|---|---|
| 1. Aislamiento entre clientes | **Cumplida** | Migración `0003`: ambas tablas de eventos llevan `workspace_id`, con RLS forzado y política de aislamiento. El valor lo deriva un disparador `before insert` desde la fila padre, con privilegios del llamador, de modo que una tarea de otro espacio y una inexistente fallan idéntico. Migración `0004`: las cuatro funciones `security definer` pertenecen a `leda_owner`, que no inicia sesión, no tiene miembros y no saltea la RLS. Migración `0005`: `audit_log`, `incident` y `absence` quedan bajo política; el espacio de la auditoría lo fija la sesión, nunca quien escribe. |
| 2. El núcleo no conoce el transporte | **Incumplida** | `message_outbox` tiene `chat_id` y `telegram_message_id` y no tiene columna de canal (`db/esquema.sql:533,548`). |
| 3. Límites de transporte fuera del negocio | **Incumplida** | `telegram_utf16_units` (`src/leda/salida.py:39`) se usa para decidir la validez de datos de negocio en `herramientas.crear_borrador_tarea` (límites de los campos y de la evidencia); antes, también en `ingreso_tareas.py`, borrado en la E3-4. |
| 4. Estado por eventos | **Cumplida** | `bloquear_estado_directo()` impide el `update` directo sobre la tarea (`db/esquema.sql:1231`); el estado es proyección. |
| 5. Configuración como dato versionado | **Cumplida** | `area` y `rol` son tablas con alcance de espacio (`db/esquema.sql:106,114`); el importador de paquetes es genérico (`src/leda/importador.py:211`). |
| 6. Autoridad revalidada en la frontera | **Parcial** | Existe la resolución de identidad y autoridad (`src/leda/autoridad.py`) y el límite dedicado de conversión. Falta el grafo de transiciones: `actualizar_estado` acepta cualquier destino del tipo enumerado sin validar que la transición sea legítima (`src/leda/herramientas.py:464-491`). |

### Cómo se cerró la regla 1

El propietario efectivo de las funciones elevadas **se midió**, no se supuso: eran
propiedad de `postgres`, superusuario y `bypassrls`. Adentro de sus cuerpos la RLS
no aplicaba. Eso cierra el `PENDIENTE` que este documento registraba antes.

Al quitarles ese privilegio apareció una dependencia oculta: el disparador que
proyecta `task.estado` se apoyaba en saltear la RLS. La conexión administrativa no
define espacio alguno, así que su `update` pasó a no encontrar ninguna fila y a
fallar **en silencio**. Ahora se acota al espacio del propio evento, ya derivado, y
restaura el valor previo para no angostar el resto de la transacción.

Dos verificaciones sostienen la regla, ambas contra bases reales: el rechazo del
cruce con indistinguibilidad frente a un identificador inexistente, y la
convergencia entre instalación limpia y base migrada leyendo el catálogo efectivo.

Límite que se conserva: la propiedad se verifica sobre una base nueva dentro de un
clúster existente. Un ensayo sobre un clúster enteramente limpio sigue siendo una
comprobación más fuerte y está `PENDIENTE`.

`confirmar_borrador_tarea` todavía fija el espacio con el valor que recibe de quien
la llama. Está acotada a `leda_gateway` y fuera del alcance de `leda_app`, pero
es el patrón que la regla 6 rechaza; pertenece al ingreso autenticado, no a esta
regla.

## Cómo se usa esta frontera

Antes de escribir código nuevo, ubicarlo: ¿es núcleo, puerto o adaptador? Si una
corrección obliga a que el núcleo conozca un detalle de canal, la corrección está mal
ubicada.

Antes de aceptar un requisito de un cliente, aplicar la tabla de
[`product/que-es-leda.md`](../product/que-es-leda.md): ¿es configuración de ese
cliente o es núcleo del producto?
