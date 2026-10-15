# Cierre del aislamiento entre clientes

> **Nota del 2026-10-04.** Este documento es anterior al Motor, la línea de trabajo vigente. Lo que
> figure acá como en curso, pendiente o próximo paso no se retoma sin una decisión del usuario. El
> orden de trabajo vigente está en [`docs/STATUS.md`](../../docs/STATUS.md).

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
| Sí reciben `grant insert` para `leda_app` | `db/esquema.sql:1542` |
| El disparador que proyecta el estado es `security definer` y no valida espacio | `db/esquema.sql:1215-1225` |
| El esquema versionado no fija propietario de ninguna función | `db/esquema.sql`, sin ninguna sentencia `alter ... owner to` |

Consecuencia: una conexión del espacio A inserta un evento que referencia una
tarea del espacio B y le muta el estado. La clave foránea confirma además que
ese identificador existe, lo que habilita enumeración.

## La trampa de diseño

`leda_admin` es **`bypassrls`** (`db/esquema.sql:1463`). Darle a ese rol la
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

**D3 — El disparador conserva `security definer`.** `leda_app` no tiene
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
- [x] **T3** — `leda_owner` (`nologin noinherit nobypassrls nosuperuser`) es
      dueño de las cuatro funciones elevadas. Migración `0004` y su rollback.
      **Desvío deliberado de la especificación:** no se le dieron privilegios
      mínimos sino acceso amplio a las tablas del esquema. Lo que contiene a
      este rol es la RLS, no la lista de privilegios; una lista exacta habría
      que derivarla leyendo los cuerpos de las funciones y se rompería, en
      producción y en silencio, en el próximo cambio. *Ruta: inline.*
- [x] **T4 (VERDE)** — T1 pasa. La prueba exige además que una tarea ajena y un
      identificador inexistente produzcan el **mismo** error: sin esa
      indistinguibilidad el rechazo sería en sí mismo un oráculo.
- [x] **T5** — Rollbacks de `0003` y `0004` escritos **y ejercitados** por
      `test_los_rollbacks_devuelven_la_base_al_estado_anterior`: aplica cada
      migración, exige que haya cambiado algo observable, la revierte y compara
      el catálogo contra el estado previo. Escribir la prueba destapó que el
      rollback de `0004` era parcial: revertía propiedad y privilegios pero
      dejaba el cuerpo nuevo de `aplicar_evento_tarea`, que existe únicamente
      porque el dueño dejó de saltear la RLS. Corregido. *Ruta: inline.*
- [x] **T6** — Verificar el propietario efectivo contra un clúster limpio, no
      contra el entorno de desarrollo. Cierra el `PENDIENTE` registrado en
      `docs/architecture/frontera.md` ("Límite que se conserva"). Hecho el
      2026-10-15 con `tools/ensayo_propiedad.py`; comandos y resultados en
      "Ensayo sobre un clúster limpio (T6)". Pasa la propiedad (criterio 3) y la
      RLS; la convergencia de la matriz (criterio 5) pasa contra `leda_motor`
      pero no contra una base migrada desde el principio: queda T8. *Ruta:
      delegada.*
- [x] **T7** — Actualizar `frontera.md` (regla 1 pasa a cumplida) y `STATUS.md`.
      `frontera.md`, 2026-10-15: el límite del clúster limpio quedó cerrado.
      `STATUS.md` ("Seguridad de la base") sigue diciendo `PENDIENTE` y lo
      actualiza el coordinador: el escritor de T6 no tenía ese archivo en su
      alcance.
- [ ] **T8** — Que una base migrada desde el principio converja a la misma
      matriz de privilegios que la instalación limpia (criterio 5). El ensayo
      de T6 encontró tres diferencias; causa y arreglo propuesto en "Ensayo
      sobre un clúster limpio (T6)". La prueba de paridad no las ve porque sólo
      compara los privilegios de `leda_app`.

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
   `leda_app`.

## Verificación aplicable

TDD habilitado. Fuente: `CLAUDE.md`. Runner verificado en esta máquina:

    .venv/Scripts/python.exe -m pytest -q

Entorno: PostgreSQL 18.6 nativo en `localhost:5432`, con `LEDA_TEST_DB_URL`
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
`leda_app`. Además afirma explícitamente que la RLS está encendida y forzada,
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
| `esquema.sql`: tablas en el bucle de RLS y `update`/`delete` revocados | Correcto (`:1523`, `:1557-1558`); `leda_app` conserva sólo `insert` |

## Lo que T3 destapó

Las cuatro funciones pertenecían a `postgres`: superusuario y `bypassrls`.
Medido, no supuesto. Eso cierra el `PENDIENTE` que arrastraba
`docs/architecture/frontera.md`.

Al quitarles el privilegio cayeron **diez** pruebas. Causa raíz: el disparador
que proyecta `task.estado` se apoyaba en saltear la RLS. `src/leda/db.py:56`
muestra por qué — la conexión administrativa fija `role leda_admin` pero
**nunca define `leda.workspace_id`**: ve todos los espacios por `bypassrls`,
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

## Ampliación autorizada: registros auxiliares (migración 0005)

Estaba fuera de alcance y se incorporó al continuar. Lo comprobado justificó el
cambio de prioridad: el rojo fue `assert 1 == 0` — un espacio escribió una
entrada de `audit_log` **atribuida a otro**. La auditoría autoritativa es la
evidencia que se le muestra a un cliente; si otro puede escribir en ella, deja
de serlo. Figuraba quinto porque esa lista se escribió cuando Leda era un bot
de un solo equipo y nadie más podía escribir.

Dos problemas distintos en tres tablas. `audit_log` e `incident` ya tenían
`workspace_id`, pero nullable y sin política: bastaba declarar el ajeno. Ahora
lo fija la sesión mediante `derivar_espacio_registro()`. `absence` no tenía
espacio propio en absoluto; se agregó derivándolo de la membresía, con el mismo
patrón de privilegios del llamador que `0003`.

Excepción conservada a propósito: `audit_log` e `incident` admiten espacio nulo
para los hechos de alcance global, que sólo origina la conexión administrativa.
Una fila sin espacio no queda atribuida a ningún cliente, así que no puede
falsificar su registro.

A diferencia de `0004`, no rompió ninguna prueba.

**Cuarta aparición del patrón de migraciones nombradas a mano**, y esta vez el
defecto era mío: la prueba de rollbacks que escribí una hora antes tenía `0003`
y `0004` cableadas, así que el rollback de `0005` nacía sin ejercitar. Ahora
recorre la cadena descubriéndola del directorio y exige que cada migración
tenga su rollback.

## Ensayo sobre un clúster limpio (T6)

2026-10-15, autorizado por el usuario. Un clúster nuevo, sin ningún rol `leda_*`,
con los mismos binarios que el servidor de la máquina (PostgreSQL 18.6, Scoop), en
una carpeta temporal fuera del repositorio:

| Paso | Comando | Resultado |
|---|---|---|
| Crear el clúster | `initdb -D <tmp>/cluster-limpio/datos -U postgres --auth=trust --encoding=UTF8 --locale=C` | Completado (`trust` sólo para `127.0.0.1/32`, `::1/128` y el socket local) |
| Arrancarlo | `pg_ctl -D <tmp>/cluster-limpio/datos -l <tmp>/cluster-limpio/servidor.log -o "-p 5433 -c listen_addresses=localhost" -w start` | `pg_isready -p 5433`: aceptando conexiones; `select count(*) from pg_roles where rolname like 'leda%'` = 0 |
| Instalación limpia | `psql -c "create database leda_limpia"` y `PGCLIENTENCODING=UTF8 psql -v ON_ERROR_STOP=1 -1 -f db/esquema.sql` (una transacción, como `python -m leda esquema`) | salida 0, sin errores; crea `leda_admin`, `leda_app`, `leda_gateway` y `leda_owner` |
| Base migrada desde el principio | `leda_migrada`: `db/esquema.sql` de `efa8ee2` con `a_nombres_actuales` (igual que la prueba de paridad) y después cada `db/migrations/0002..0076` con `psql -v ON_ERROR_STOP=1 -f`, en orden | 71 migraciones aplicadas, ningún `ERROR` en el registro |
| Ensayo contra `leda_motor` | `python tools/ensayo_propiedad.py "host=localhost port=5433 user=postgres dbname=leda_limpia" "host=localhost port=5432 user=postgres dbname=leda_motor"` (sólo lectura) | salida 0: a y b pasan en las dos; la matriz **converge** en las 11 categorías (1921 privilegios por relación, 178 `execute`, 97 funciones, 77 dueños) |
| Ensayo contra la migrada | `python tools/ensayo_propiedad.py "...dbname=leda_limpia" "...dbname=leda_migrada"` (las dos en 5433) | salida 1: a y b pasan en las dos; la matriz **difiere** en "privilegios por relación" (1921 contra 1913) |
| Apagar | `pg_ctl -D <tmp>/cluster-limpio/datos stop` | detenido; la carpeta queda |

Lo comprobado en la instalación limpia: las 48 funciones `security definer` son de
`leda_owner` (no superusuario, sin `bypassrls`, sin login, `noinherit`), todas con
`search_path` terminado en `pg_temp` y ninguna ejecutable por `public`; las 69
tablas con `workspace_id` tienen RLS encendida y forzada, salvo las siete
excepciones declaradas en `tests/garantias/test_aislamiento.py`, a las que no
llegan ni `leda_app` ni `leda_gateway`.

**Las tres diferencias** de la base migrada desde el principio (todas de roles sin
login o con `bypassrls`; ninguna da a `leda_app` ni a `leda_gateway` algo que la
limpia no da):

1. `admin_notice_enlace`: en la limpia `leda_owner` tiene todos los privilegios; en
   la migrada, ninguno. `db/esquema.sql` crea la tabla antes del
   `grant all privileges on all tables in schema leda to leda_owner` general; la
   `0054` sólo la concede a `leda_admin`, y el `grant` general de la `0004` corrió
   antes de que la tabla existiera.
2. `greeting_state`: en la limpia `leda_admin` tiene todos los privilegios; en la
   migrada, ninguno. La limpia los recibe del `grant all on all tables in schema
   leda to leda_admin` del final de `esquema.sql`; la `0018` concede a `leda_owner`
   y a `leda_app`, no a `leda_admin`.
3. La vista `integrante`: en la migrada `leda_owner` tiene todos los privilegios; en
   la limpia, ninguno. La vista ya existía cuando corrió el `grant` general de la
   `0004`; en `esquema.sql` se crea después del `grant` general a `leda_owner`.

`leda_motor` no muestra ninguna porque se recreó desde `esquema.sql` el 2026-10-12 y
sólo recibió por migración de la `0057` en adelante. La prueba de paridad
(`test_instalacion_limpia_y_base_migrada_convergen_en_el_aislamiento`) no las ve
porque compara sólo los privilegios de `leda_app`.

**Arreglo propuesto (T8, sin hacer):** una migración nueva que lleve la base migrada
a la matriz de la limpia (`grant all on admin_notice_enlace to leda_owner`,
`grant all on greeting_state to leda_admin`, `revoke all on integrante from
leda_owner`), con su rollback; o, si se decide que lo correcto es lo de la migrada,
el cambio inverso en `esquema.sql`. Y que la prueba de paridad compare la matriz
completa de los cuatro roles (lo que hace `tools/ensayo_propiedad.py`), para que la
próxima diferencia aparezca en la suite.

## Estado de la unidad

Cerradas T1 a T7 (T6 y T7, el 2026-10-15); abierta T8. Suite en **310 passed, 0 failed**. La regla 1 de
`docs/architecture/frontera.md` pasó a cumplida.

Queda abierto, todo registrado en `docs/STATUS.md`:

- **T6 cerrada el 2026-10-15** (ver "Ensayo sobre un clúster limpio (T6)"). Queda
  **T8**: tres diferencias de privilegios entre la instalación limpia y una base
  migrada desde el principio.
- `confirmar_borrador_tarea` fija el espacio con el valor que recibe de quien
  la llama. Contenida a `leda_gateway` y fuera del alcance de `leda_app`,
  pero es el patrón que la regla 6 rechaza. Pertenece al ingreso autenticado.
- Riesgo 5 de `STATUS.md`: `absence`, `incident` y `audit_log` reciben `insert`
  sin política. Misma clase que lo ya cerrado, menor impacto. No se incluyó sin
  autorización explícita.

## Próximo paso

Decidir con el usuario si sigue el riesgo 5, o la siguiente unidad del
roadmap: el desacople del transporte, que es la precondición del dashboard y
de cualquier canal que no sea el conversacional.
