# Estado actual

**Alcance:** Prisma es un producto de gestión de proyectos multi-tenant. CoreWork es
su primer cliente, no su definición.

**Última actualización documental:** 2026-09-22.

## Resumen

El alcance del proyecto cambió: Prisma dejó de tratarse como asistente interno de un
equipo y pasó a definirse como producto ofrecible a varios clientes, con superficie
conversacional, superficie de lectura y eventual aplicación móvil.

La base documental se reescribió en consecuencia:

- [`product/que-es-prisma.md`](product/que-es-prisma.md) define el producto y separa
  configuración de cliente de núcleo del producto.
- [`architecture/frontera.md`](architecture/frontera.md) define dónde termina el
  núcleo y qué reglas lo gobiernan. Gobierna a los demás documentos de arquitectura.
- [`ROADMAP.md`](ROADMAP.md) ordena qué se aprovecha, qué se corrige y qué queda
  superado.

Los documentos del piloto local por fases quedaron superados y están marcados como
tales. Ver [`INDEX.md`](INDEX.md#documentos-superados).

## Estado comprobado

- La fundación multi-tenant existe y es la parte mejor construida del sistema: 28
  tablas con `row level security` forzado y política de aislamiento contra el espacio
  vigente (`db/esquema.sql:1474-1492`).
- No hay vocabulario de cliente congelado en el esquema: `area` y `rol` son tablas con
  alcance de espacio (`db/esquema.sql:106,114`), no tipos enumerados. Incorporar un
  segundo cliente no exige modificar el esquema.
- El estado de tarea es proyección de eventos, no campo editable
  (`db/esquema.sql:1231`).
- La superficie HTTP se limita a `POST /telegram/{slug}` y `GET /salud`
  (`src/prisma/gateway.py:47,434`). No existe API de lectura.
- La Unidad 1A (borrador y compromiso de tarea) está implementada, verificada de forma
  independiente y fue activada en su momento sobre la base local. Su evidencia
  detallada se conserva en
  [`phases/01-local-pilot-foundations.md`](phases/01-local-pilot-foundations.md).
- Las migraciones `0001` y `0002` se ensayaron contra bases descartables, incluida
  paridad entre instalación limpia y migración, y rollback guardado. **No fueron
  aplicadas a ninguna base operativa.**
- El repositorio tiene un único commit, `efa8ee2`. El árbol de trabajo acumula cambios
  sin comitear. El remoto `origin` quedó conectado a GitHub el 2026-09-22 y está
  vacío; no se hizo push.

## Baseline de pruebas

| Campo | Valor |
|---|---|
| Comando | `.venv\Scripts\python.exe -m pytest` |
| Fecha | 2026-08-15 |
| Resultado exacto | 306 passed, 0 failed. |

**Esta ejecución no fue repetida desde el 2026-08-15 y el árbol de trabajo cambió
después.** El resultado vale como registro histórico, no como estado verificado de la
suite hoy. Debe reejecutarse antes de afirmar cualquier cosa sobre ella.

## Correcciones anteriores

Tres ejercicios progresivos sobre Telegram se detuvieron sin crear trabajo real y
produjeron correcciones sucesivas: un circuito de alta de tareas propiedad del
servidor, un router de intención con salida tipada y validada, la reubicación del
commit del gateway fuera del bloque de espacio, y una guarda de codificación UTF-8 en
la migración `0002`. El detalle de cada corrección vive en la historia del repositorio
y en los documentos superados; no se reproduce aquí.

La conclusión que sobrevive a ese ciclo está registrada en
[`architecture/frontera.md`](architecture/frontera.md): cada corrección movió autoridad
hacia el servidor sin una decisión de arquitectura explícita, y esa frontera existe
para que la próxima corrección tenga un lugar declarado al que pertenecer.

## Operación

- El listener está detenido.
- No hay Telegram real, base operativa, Docker ni staging en uso.
- No hay datos ni trabajo real cargados.

## Riesgos prioritarios

1. **El outbox está atado a un transporte.** `message_outbox` tiene `chat_id` y
   `telegram_message_id` y no tiene columna de canal (`db/esquema.sql:533,548`).
   Bloquea toda superficie que no sea la conversacional.
2. **Un límite de transporte decide validez de negocio.** `telegram_utf16_units`
   (`src/prisma/salida.py:39`) se usa para aceptar o rechazar datos de negocio en
   `src/prisma/ingreso_tareas.py:532,547,554,1118`.
3. **No existe grafo de transiciones de estado.** `actualizar_estado` acepta cualquier
   destino del tipo enumerado sin validar que la transición sea legítima
   (`src/prisma/herramientas.py:464-491`).
4. **`pending_reply` no es operativo.** La tabla y la escalera existen, pero el ingreso
   no crea ni satisface el ciclo de respuesta, de modo que el seguimiento no puede
   afirmar silencio sobre evidencia real.
5. **`confirmar_borrador_tarea` fija el espacio con el valor que recibe.** Está
   acotada a `prisma_gateway` y fuera del alcance de `prisma_app`, pero confiar el
   espacio a quien llama es el patrón que la frontera rechaza. Pertenece al ingreso
   autenticado.

### Cerrado: aislamiento entre clientes

Era el riesgo número uno. Las tablas de eventos de estado no tenían `workspace_id`
ni política, y las cuatro funciones `security definer` pertenecían a `postgres`
—superusuario y `bypassrls`—, así que adentro de sus cuerpos la RLS no aplicaba.
Cerrado por las migraciones `0003` y `0004`; el detalle está en
[`architecture/frontera.md`](architecture/frontera.md#cómo-se-cerró-la-regla-1).

La migración `0005` cerró el resto: `audit_log`, `incident` y `absence` recibían
`insert` sin política. Figuraba como riesgo menor, pero lo comprobado fue que un
espacio podía **fabricar auditoría atribuida a otro**. La auditoría autoritativa es
la evidencia que se le muestra a un cliente; si otro puede escribir en ella, deja
de serlo. Su posición en la lista venía de cuando Prisma era un bot de un solo
equipo y nadie más podía escribir.

`audit_log` e `incident` conservan a propósito la posibilidad de espacio nulo, para
los hechos de alcance global que sólo origina la conexión administrativa: una fila
sin espacio no queda atribuida a ningún cliente y por eso no falsifica su registro.

Queda `PENDIENTE` un ensayo de propiedad sobre un clúster enteramente limpio: hoy
se verifica sobre una base nueva dentro de un clúster existente.

## Deudas registradas

- **Revisión del contexto LLM.** Comparar calidad, completitud, costo, latencia y
  exposición del contexto amplio frente a variantes reducidas o adaptativas. No es
  todavía una política aprobada; requiere ADR antes de operar en internet.
- **Capacidades de producción.** Cola de entrada, pool de conexiones, secreto
  obligatorio de webhook, observabilidad, respaldo y restauración. Ordenadas en el
  horizonte posterior del roadmap.
- **Alta de un segundo cliente.** El mecanismo de paquetes es genérico, pero el
  proceso de alta no está definido.

## Próximo paso

**Aclaración con botones**, según el diseño vivo
[`architecture/interpretacion-y-confirmacion.md`](architecture/interpretacion-y-confirmacion.md)
y las decisiones [`ADR 0005`](decisions/0005-interpretacion-y-confirmacion.md) (puntos
3 a 5) y [`ADR 0006`](decisions/0006-jev-para-resolver-referencias-e-intencion.md):
Jev resuelve a qué tarea se refiere cada mensaje, con la pregunta de verificación, y
detecta la intención dudosa; ante una ambigüedad material, botones con propuestas
completas y "Ninguna, lo escribo"; las preguntas de Prisma con botones; apodos y
vocabulario del equipo aprendidos preguntando. Incluye la corrección del router de
intención, el defecto que encontró el banco (`b-0005`, 0 de 10: `route_intent` no ve
las tareas del espacio; ver `docs/capacidades.md`, "Trampas conocidas").
`PENDIENTE`: confirmar la pregunta de verificación con un lote de mensajes no visto
(diseño §5.8).

Después, una sesión progresiva por Telegram real con datos ficticios para los circuitos
ya verificados (consulta, bloqueos, estados, vista previa y confirmación) y, luego, la
conversación de bloqueos (mecánica §8, pasos 2 a 7). Las dependencias no entran en esa
sesión hasta cerrar el defecto del router.

El resto del orden de trabajo está en [`ROADMAP.md`](ROADMAP.md).

## Cerrado: vista previa y confirmación de todo cambio

Feature `odd/tasks/vista-previa-y-confirmacion.md` (commits `2bd2200`, `763b427` y el
de cierre). Las 8 herramientas que escriben muestran estado vigente y cambio propuesto
y esperan Confirmar, Modificar o Cancelar; al confirmar se recalcula una huella del
estado y, si cambió, no se aplica. Modificar acepta la corrección durante 30 minutos.
El banco toca Confirmar por el mismo camino que Telegram y falla si alguna de las 8
herramientas se ejecutó o cambió la base antes del toque.

Verificación, 2026-09-24: `.venv/Scripts/python.exe -m pytest -q` → 536 passed, 90
deselected; `tests/banco` → 124 passed. El banco con el modelo real no se volvió a
correr con este cambio. Pendiente conocido: un ciclo de dependencias se detecta recién
al confirmar (lo frena la base), no en la vista previa.

## Cerrado: banco conversacional con el modelo real

`tests/banco/` (feature `odd/tasks/banco-conversacional.md`). Cómo se corre, en
[`docs/validation/README.md`](validation/README.md). Primera corrida real, 2026-09-23,
NaN `deepseek-v4-flash`, 7 escenarios × 10 corridas, base descartable de pruebas:

| Escenario | Aprobadas | Nota |
|---|---|---|
| b-0001 consulta de tareas propias | 10/10 | |
| b-0002 registrar un bloqueo relatado vagamente | 10/10 | |
| b-0003 resolver un bloqueo | 9/10 | la falla era del comprobador, corregido |
| b-0004 pasar una tarea a revisión | 10/10 | |
| b-0005 declarar una dependencia | 0/10 | defecto real del router, abierto |
| b-0006 pedir una tarea nueva | 10/10 | |
| b-0007 persona que no está en el equipo | 9/10 + 1 no concluyente | el no concluyente era del comprobador, corregido |

Latencia por corrida, línea base sin umbral: mediana 8,1 s, mínima 1,2 s, máxima
100,7 s (un pico aislado en `b-0002`). Suite por defecto: 473 passed, el banco no
corre en ella.

Entorno local: PostgreSQL 18.6 instalado con scoop, sin servicio de Windows; se levanta
con `levantar-postgres.bat`. Modelo activo `nan / deepseek-v4-flash`.

## Cerrado: dependencias entre tareas

Era el próximo paso anterior. `crear_dependencia`/`quitar_dependencia`
(`src/prisma/herramientas.py`) crean y quitan con la autoridad decidida —responsable de
cualquiera de las dos tareas, o su referente— y avisan a la otra parte y, entre áreas
distintas, a los dos referentes; un ciclo lo rechaza `trg_evitar_ciclo_dependencia` con
un mensaje legible. El freno de `en_curso` vive en la base
(`motivo_no_arranca_tarea`/`trg_exigir_dependencias_resueltas`, migración `0008` con su
rollback). El aviso en cadena por atraso o por fecha corrida corre en la misma pasada
que la escalera (`escalera.evaluar_dependencias_en_riesgo`), deduplicado por
(origen, su fecha objetivo vigente) por destinatario. La dependencia informativa avisa a
las dos partes cuando la origen cambia de estado; el aviso por cambio de fecha queda sin
disparador porque `bloquear_estado_directo` vuelve `fecha_objetivo` inmutable una vez
comprometida la tarea y ninguna ruta de código la cambia — deuda registrada, no
implementada.
