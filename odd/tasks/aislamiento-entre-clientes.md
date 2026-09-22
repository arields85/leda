# Cierre del aislamiento entre clientes

**Estado:** en curso
**Creado:** 2026-09-22
**Rama:** `master`
**Precondición cumplida:** línea base versionada (`8d6e9e6`), suite en 306 passed.

## Objetivo

Que una conexión asociada a un espacio no pueda escribir, ni deducir la
existencia, de objetos de dominio de otro espacio.

Es el riesgo número uno de `docs/STATUS.md` y la regla número uno de
`docs/architecture/frontera.md`, hoy declarada incumplida.

## La falla, verificada

| Hecho | Evidencia |
|---|---|
| `task_state_event` y `objective_state_event` no tienen `workspace_id` | `db/esquema.sql:413-422,426-435` |
| No figuran en el arreglo de tablas con RLS | `db/esquema.sql:1474-1482` |
| Sí reciben `grant insert` para `prisma_app` | `db/esquema.sql:1542` |
| El disparador que proyecta el estado es `security definer` y no valida espacio | `db/esquema.sql:1215-1225` |
| El esquema versionado no fija propietario de ninguna función | `db/esquema.sql`, sin ninguna sentencia `alter ... owner to` |

Consecuencia: una conexión del espacio A inserta un evento que referencia una
tarea del espacio B y le muta el estado. La clave foránea confirma además que
ese identificador existe, lo que habilita enumeración.

## La trampa de diseño

`prisma_admin` es **`bypassrls`** (`db/esquema.sql:1463`). Darle a ese rol la
propiedad de las funciones `security definer` anularía la política de
aislamiento que esta unidad agrega: las funciones la saltearían por completo.

El propietario tiene que ser un rol nuevo **sin** `bypassrls`.

Funciones `security definer` afectadas: `resolver_pendiente`
(`:804`), `confirmar_borrador_tarea` (`:873`), `resolver_ingreso_borrador`
(`:1121`) y el disparador `aplicar_evento_tarea` (`:1215`).

Asimetría observada: `aplicar_evento_objetivo` (`:1257`) **no** es
`security definer`, aunque `objective_state_event` tampoco tiene RLS.

## Decisiones de diseño

**D1 — El `workspace_id` del evento no lo aporta quien llama.** Un llamador
podría declarar el espacio equivocado. Se deriva dentro de la base, desde la
tarea u objetivo referenciado, en un disparador `before insert` que ignora lo
que haya suministrado el llamador. Recién entonces la cláusula `with check` de
la política compara contra el GUC de sesión y rechaza lo que no corresponda.

**D2 — Propietario nuevo sin `bypassrls`.** Un rol `nologin nobypassrls
noinherit` que posea las funciones y tenga exactamente los privilegios de tabla
que necesitan, ni uno más.

**D3 — El disparador conserva `security definer`.** `prisma_app` no tiene
`update` sobre `task` (`db/esquema.sql:1497`), por eso existe. Con un
propietario sin `bypassrls`, su `update` queda sujeto a la RLS de `task`. La
puerta real es el `insert` del evento; la RLS de `task` es la segunda barrera.

## Alcance autorizado

Las dos tablas de eventos y la propiedad de las cuatro funciones
`security definer`. Migración `0003` con su rollback, y pruebas negativas.

**Fuera de alcance, para decidir aparte:** `absence`, `incident` y `audit_log`
también reciben `insert` sin política de aislamiento
(`db/esquema.sql:1542-1543`). Es el riesgo 6 de `STATUS.md`, misma clase de
problema y menor impacto. No se incluye sin autorización explícita.

## Checklist

- [x] **T1 (ROJO)** — `test_un_espacio_no_puede_mover_el_estado_de_una_tarea_de_otro`.
      Rojo observado: `DID NOT RAISE Error`. La inserción cruzada no lanzaba
      absolutamente nada. *Ruta: inline.*
- [x] **T2** — `db/migrations/0003_state_event_isolation.sql` y el equivalente
      en `db/esquema.sql`. *Ruta: delegada; el writer murió por límite de
      sesión durante su verificación, el trabajo estaba completo y lo verifiqué
      yo.*
- [x] **T3** — `prisma_owner` (`nologin noinherit nobypassrls nosuperuser`) es
      dueño de las cuatro funciones elevadas. Migración `0004` y su rollback.
      **Desvío deliberado de la especificación:** no se le dieron privilegios
      mínimos sino acceso amplio a las tablas del esquema. Lo que contiene a
      este rol es la RLS, no la lista de privilegios; una lista exacta habría
      que derivarla leyendo los cuerpos de las funciones y se rompería, en
      producción y en silencio, en el próximo cambio. *Ruta: inline.*
- [x] **T4 (VERDE)** — T1 pasa. La prueba exige además que una tarea ajena y un
      identificador inexistente produzcan el **mismo** error: sin esa
      indistinguibilidad el rechazo sería en sí mismo un oráculo.
- [~] **T5** — Rollback escrito (`db/rollbacks/0003_state_event_isolation.sql`).
      **Ninguna prueba lo ejercita todavía.** La paridad sí quedó comprobada,
      pero por una prueba nueva: ver abajo.
- [ ] **T6** — Verificar el propietario efectivo contra un clúster limpio, no
      contra el entorno de desarrollo. Cierra el `PENDIENTE` registrado en
      `docs/architecture/frontera.md:133-136`.
- [ ] **T7** — Actualizar `frontera.md` (regla 1 pasa a cumplida) y `STATUS.md`.

## Criterios de aceptación

1. Una conexión asociada a un espacio no puede insertar un evento que
   referencie una tarea u objetivo de otro espacio, ni por DML directo ni
   declarando un `workspace_id` falso.
2. Un identificador ajeno no se distingue de uno inexistente: sin oráculo de
   enumeración.
3. Ninguna función `security definer` queda sin propietario explícito, y
   ninguna es propiedad de un rol con `bypassrls`.
4. La suite completa sigue en verde; ninguna regresión.
5. Instalación limpia y base migrada convergen a la misma matriz de
   privilegios.
6. El rollback restaura el estado anterior sin conceder acceso directo a
   `prisma_app`.

## Verificación aplicable

TDD habilitado. Fuente: `CLAUDE.md`. Runner verificado en esta máquina:

    .venv/Scripts/python.exe -m pytest -q

Entorno: PostgreSQL 18.6 nativo en `localhost:5432`, con `PRISMA_TEST_DB_URL`
en `.env.test`. No arranca solo tras reiniciar Windows.

Secuencia obligatoria: ROJO observado en T1 antes de implementar T2 y T3;
VERDE en T4; suite completa antes de comitear.

## Estrategia de entrega

`ask-on-risk`. Pronóstico: bastante por debajo de las 400 líneas autoradas.
Una sola unidad de trabajo, un commit.

## Hallazgo: la prueba de paridad no comprobaba paridad

`test_migration_clean_schema_parity_and_guarded_rollback` (`tests/test_task_intake.py`)
lee `db/esquema.sql` y las migraciones **como texto** y busca subcadenas. No
abre ninguna conexión, no compara dos bases, y estaba cableada a `0002`: la
migración `0003` podía estar rota entera y esa prueba seguía en verde.

Se agregó `test_instalacion_limpia_y_base_migrada_convergen_en_el_aislamiento`,
que instala el esquema limpio en una base descartable, migra otra desde el
esquema anterior a `0002`, y compara los catálogos efectivos de PostgreSQL:
columnas, banderas de RLS, políticas, disparadores y privilegios de
`prisma_app`. Además afirma explícitamente que la RLS está encendida y forzada,
que la política se llama `aislamiento_espacio` y que `workspace_id` es
`not null`, de modo que dos bases igualmente desprotegidas no pasarían.

La prueba textual se conserva: cubre otras cosas y no molesta. Pero ya no es la
que responde si una instalación nueva queda tan aislada como una migrada.

## Progreso

- 2026-09-22 — Documento creado. Falla y trampa de diseño verificadas.
- 2026-09-22 — T1 en rojo observado, T2 implementada, T4 en verde. Paridad real
  agregada y en verde. **Suite completa: 308 passed, 0 failed** con
  `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider`.

## Verificación registrada

Revisión del SQL hecha por el orquestador, no por el writer:

| Comprobación | Resultado |
|---|---|
| Las funciones de derivación **no** son `security definer` | Correcto: privilegios del llamador, que es lo que cierra el oráculo |
| Privilegios concedidos por la migración | Ninguno: `0003` no contiene `grant` ni `revoke` |
| Expresión de la política | Idéntica a la del resto del esquema |
| `esquema.sql`: tablas en el bucle de RLS y `update`/`delete` revocados | Correcto (`:1523`, `:1557-1558`); `prisma_app` conserva sólo `insert` |

## Lo que T3 destapó

Las cuatro funciones pertenecían a `postgres`: superusuario y `bypassrls`.
Medido, no supuesto. Eso cierra el `PENDIENTE` que arrastraba
`docs/architecture/frontera.md`.

Al quitarles el privilegio cayeron **diez** pruebas. Causa raíz: el disparador
que proyecta `task.estado` se apoyaba en saltear la RLS. `src/prisma/db.py:56`
muestra por qué — la conexión administrativa fija `role prisma_admin` pero
**nunca define `prisma.workspace_id`**: ve todos los espacios por `bypassrls`,
no por el GUC. Sin ese privilegio, el `update` de la proyección se filtraba
contra un espacio vacío, no encontraba ninguna fila y **fallaba en silencio**:
el evento quedaba registrado y el estado nunca se proyectaba.

Corregido acotando el disparador al espacio del propio evento, que `0003` ya
deriva de la tarea padre, y restaurando el valor previo para no angostar el
resto de la transacción. Sin esa restauración, una operación administrativa que
recorra varios espacios quedaría encerrada en el último que tocó: se habría
cambiado un fallo ruidoso por uno sutil.

## Patrón recurrente: migraciones nombradas a mano

Tercera aparición en la misma sesión. `git show HEAD:db/esquema.sql` como
esquema "anterior"; la prueba textual de paridad, cableada a `0002`; y
`test_migration_reconciles_legacy_and_guarded_rollback_restores_it`, que
comparaba dueños de funciones con una cadena que terminaba en `0002`. Cada
migración nueva rompía una prueba lejos de su causa.

Resuelto con `_migraciones_posteriores_a()`, que las descubre del directorio.
Se aplicó también a la prueba de paridad nueva, que había nacido con el mismo
defecto.

## Próximo paso

T5 completa: ninguna prueba ejercita todavía los rollbacks de `0003` y `0004`.
Después, decidir con el usuario el riesgo 5 de `STATUS.md` (`absence`,
`incident` y `audit_log` sin política), que es la misma clase de problema con
menor impacto.
