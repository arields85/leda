# Puerto de lectura

**Estado:** en curso
**Creado:** 2026-09-22
**Precondición cumplida:** aislamiento entre clientes cerrado (`675184a`).
Sin eso, una superficie de lectura sería una fuga entre clientes.

## Objetivo

Que exista una forma de leer el estado consolidado de un espacio —y sólo de
ese espacio— sin pasar por la superficie conversacional.

## Por qué se adelantó a la unidad anterior

El roadmap ordenaba antes el desacople del transporte, afirmando que era
precondición del dashboard. Al explorarlo, esa dependencia no se sostuvo:
`message_outbox` es la cola de **notificaciones empujadas a personas**, y un
dashboard no recibe notificaciones, lee estado. El desacople habilita un
segundo canal de notificación, no una superficie de lectura.

Lo que sí bloquea al dashboard: no existen consultas agregadas, no hay
superficie HTTP más allá del webhook, y no hay autenticación para un cliente
que no sea Telegram.

## Alcance de esta unidad

**Incluido:** el puerto de lectura. Un módulo con consultas agregadas,
acotadas por espacio a través de `espacio()`, de modo que el aislamiento lo
garantice la RLS y no el cuidado de quien escribe la consulta.

**Excluido deliberadamente:** el adaptador HTTP. No por tamaño, sino porque
esconde una decisión de producto que no me corresponde: **cómo se autentica
una superficie que no es Telegram.** Un token de lectura por espacio, sesiones,
claves por integrante y su rotación son opciones con consecuencias distintas.
Se plantea antes de construirla, no durante.

El puerto sin adaptador no es especulativo: es donde vive la propiedad de
seguridad —que una lectura no cruce de espacio— y deja el HTTP como una capa
fina encima.

## Consultas de este primer corte

Tomadas de lo que `product/que-es-leda.md` promete de la superficie de
lectura y del §16 del documento del primer cliente.

1. Objetivos con su avance, medido en tareas terminadas sobre el total.
2. Tareas por estado.
3. Carga por persona: tareas activas por responsable.
4. Tareas vencidas.
5. Bloqueos abiertos con su antigüedad.
6. Aprobaciones pendientes.

Quedan para después, sin bloquear nada: dependencias entre áreas, historial de
decisiones y actividad semanal o mensual.

## Checklist

- [x] **T1/T3** — `tests/test_lectura.py`: una prueba de aislamiento sobre las
      seis consultas y una de corrección por consulta, con datos distintos
      cargados en los dos espacios. *Ruta: delegada.*
- [x] **T2** — `src/leda/lectura.py`. *Ruta: delegada.*
- [x] **T4** — `frontera.md`: el puerto de lectura pasa a implementado; el
      adaptador HTTP sigue marcado como inexistente, que es lo correcto.
- [x] **T5** — `intake_world` movida a `tests/conftest.py` para que la usen
      los dos archivos de prueba. *Añadida durante la ejecución.*

## El hallazgo de la sexta consulta

La especificación pedía `aprobaciones_pendientes`. **Esa consulta no se puede
escribir**: `approval.decision` es del tipo `decision_aprobacion`, un enum de
`('aprobado', 'rechazado')`, y la columna es `not null` (`db/esquema.sql:51,493`).
Cada fila es una decisión ya tomada. La tabla es el registro de aprobaciones,
no una cola de pendientes.

Lo que el dominio sí expresa es el estado del trabajo: `task.estado` en
`pendiente_aprobacion` o `en_revision`, y `objective.estado` en
`completo_pendiente_aprobacion`. Eso se implementó, con el nombre
`trabajo_esperando_aprobacion` — no el de la especificación, justamente para
no sugerir que lee `approval`.

Una cola real de aprobaciones pendientes exige un dato que hoy no existe: una
solicitud de aprobación con estado propio. Es una decisión de dominio, no una
consulta.

## Decisión de diseño heredada

Ninguna consulta lleva filtro de espacio en su SQL. El aislamiento es
enteramente de la RLS, lo que hace que la prueba de aislamiento signifique
algo: si la política fallara, las consultas devolverían los dos espacios y la
prueba lo vería. Diverge del estilo de `src/leda/herramientas.py:177`, que sí
filtra explícitamente, y coincide con lo que declara el propio esquema: *el
aislamiento no depende de que el modelo se acuerde*.

## Criterios de aceptación

1. Ninguna consulta devuelve filas de un espacio distinto al de la sesión.
2. Ninguna consulta recibe el espacio como parámetro de quien llama: sale de
   la sesión, igual que en el resto del sistema.
3. Las seis devuelven resultados correctos sobre datos de prueba, no sólo
   listas vacías: una consulta rota y una sin datos se ven igual.
4. La suite completa sigue en verde.

## Verificación aplicable

TDD habilitado. Runner: `.venv/Scripts/python.exe -m pytest -q`.
PostgreSQL 18.6 en `localhost:5432`, `LEDA_TEST_DB_URL` en `.env.test`.

El criterio 3 importa: una prueba que sólo comprueba aislamiento pasaría con
seis funciones que devuelven siempre vacío.

## Estrategia de entrega

`ask-on-risk`. Un módulo nuevo y un archivo de pruebas; bastante por debajo de
las 400 líneas autoradas. Un commit.

## Progreso

- 2026-09-22 — Documento creado tras explorar y descartar la dependencia que
  el roadmap afirmaba. Ninguna tarea cerrada.

## Próximo paso

Escribir T1 y observar el rojo.
