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
5. Cobertura RLS incompleta en registros auxiliares: `absence`, `incident` y
   `audit_log` reciben `insert` sin política de aislamiento
   (`db/esquema.sql:1542-1543`). Misma clase que el riesgo ya cerrado, menor
   impacto.
6. **`confirmar_borrador_tarea` fija el espacio con el valor que recibe.** Está
   acotada a `prisma_gateway` y fuera del alcance de `prisma_app`, pero confiar el
   espacio a quien llama es el patrón que la frontera rechaza. Pertenece al ingreso
   autenticado.

### Cerrado: aislamiento entre clientes

Era el riesgo número uno. Las tablas de eventos de estado no tenían `workspace_id`
ni política, y las cuatro funciones `security definer` pertenecían a `postgres`
—superusuario y `bypassrls`—, así que adentro de sus cuerpos la RLS no aplicaba.
Cerrado por las migraciones `0003` y `0004`; el detalle está en
[`architecture/frontera.md`](architecture/frontera.md#cómo-se-cerró-la-regla-1).

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

1. **Línea base versionada.** Registrar el trabajo acumulado en un commit con historia
   recuperable. Es precondición de cualquier refactor.
2. **Cierre del aislamiento entre clientes.** Agregar `workspace_id` y política de RLS
   a las tablas de eventos de estado, fijar propietario explícito para cada función
   `security definer`, y verificar el propietario efectivo en una instalación limpia.
   El criterio de cierre está en [`ROADMAP.md`](ROADMAP.md#orden-de-entrega).

El resto del orden de trabajo está en [`ROADMAP.md`](ROADMAP.md). No reanudar Telegram
real ni operación hasta cerrar el riesgo 1.
