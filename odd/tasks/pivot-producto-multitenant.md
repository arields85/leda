# Pivot a producto multi-tenant — base documental

**Estado:** en curso
**Creado:** 2026-09-22
**Rama:** `master` (sin rama de trabajo todavía; ver Restricciones)

## Objetivo

Reemplazar la base documental escrita para "bot interno de CoreWork" por la base
documental de "Leda, producto PM multi-tenant", y dejar registrado con evidencia
qué se aprovecha, qué se corrige y qué queda superado.

## Problema

La documentación vigente define a Leda como un asistente interno para un único
equipo. El alcance real declarado es un producto ofrecible a varios clientes, cada
uno con su propia configuración de integrantes, áreas, tareas y políticas, con
dashboard web y eventualmente aplicación móvil.

Esa diferencia de alcance cambia el modelo de amenaza (el aislamiento entre clientes
pasa a ser la amenaza principal) y cambia la arquitectura objetivo (el canal
conversacional pasa a ser un adaptador entre varios, no el sistema).

## Por qué ahora

Escribir la frontera antes de tocar código evita repetir la deriva que ya ocurrió:
cada falla operativa empujó autoridad hacia el servidor sin que existiera un
documento que dijera dónde termina el núcleo y dónde empieza el adaptador.

## Hallazgos que fundamentan este trabajo

Verificados en esta sesión sobre el árbol de trabajo actual.

| Hallazgo | Evidencia |
|---|---|
| Aislamiento multi-tenant real: 28 tablas con `force row level security` y policy contra el GUC `leda.workspace_id` | `db/esquema.sql:1474-1492` |
| Cero vocabulario de cliente congelado en esquema: `area` y `rol` son tablas con `workspace_id`, no enums | `db/esquema.sql:106,114` |
| Estado de tarea es proyección de eventos, no campo editable | `db/esquema.sql:1231` |
| Escritura cross-tenant: las tablas de eventos no tienen `workspace_id` ni RLS, pero sí `grant insert` | `db/esquema.sql:413-422,426-435,1474-1482,1542` |
| El trigger que proyecta el estado es `security definer` y no valida workspace | `db/esquema.sql:1215-1225` |
| No existe ningún `alter ... owner to` en el esquema versionado | `db/esquema.sql` (grep sin resultados) |
| Telegram filtrado al núcleo: `message_outbox` sin columna de canal | `db/esquema.sql:533,548` |
| Un límite de transporte decide validez de negocio | `src/leda/ingreso_tareas.py:532,547,554,1118` |
| No existe API de lectura: la superficie HTTP es webhook + salud | `src/leda/gateway.py:47,434` |

## Alcance autorizado

Sólo documentación dentro del repositorio. Ningún cambio de código, esquema ni
migración en esta unidad.

Fuera de alcance explícito: el parche cross-tenant, el desacople de Telegram, la API
de lectura y el commit de línea base. Quedan para unidades siguientes, en ese orden.

## Restricciones

- No se borra documentación existente. Lo superado se marca como superado y se
  conserva.
- Los documentos nuevos van en español neutro/profesional: el proyecto entero está
  en español, incluidos identificadores y esquema.
- Documentos cortos y orientados a decisión. El proyecto no se ahogó por falta de
  documentación sino por exceso: un ADR de 508 líneas describe una frontera marcada
  como no implementada.
- El usuario difirió el commit de línea base. Esta unidad no comitea.

## Checklist

- [x] **T1** — `docs/product/que-es-leda.md`: definición de producto, superficies,
      qué hace y qué no, qué es configuración por cliente vs núcleo, CoreWork como
      primer cliente. *Ruta: delegada (writer trigger: 3+ archivos no triviales).*
      **111 líneas.**
- [x] **T2** — `docs/architecture/frontera.md`: mapa hexagonal (núcleo, puertos,
      adaptadores), reglas invariantes de la frontera, y tabla honesta de
      cumplimiento actual con evidencia archivo:línea. *Ruta: delegada.*
      **146 líneas.** Declara 3 de 6 reglas incumplidas.
- [x] **T3** — `docs/ROADMAP.md`: reescritura. Qué se aprovecha, qué se corrige, qué
      se descarta, y orden de entrega. Sin fases 0-8. *Ruta: delegada.*
      **138 líneas** (antes 163).
- [x] **T4** — `docs/INDEX.md`: navegación nueva, y marcado de documentos superados.
      *Ruta: delegada junto a T1-T3 (mismo writer).* **66 líneas** (antes 56).
- [x] **T5** — Marcar como superados sin borrar: encabezado de
      `docs/decisions/0003-authenticated-inbound-boundary.md` (529 líneas, antes 508;
      su estado pasó a `superada por cambio de alcance`), `docs/phases/00-pilot-scope.md`
      (149, antes 139), `docs/phases/01-local-pilot-foundations.md` (755, antes 742) y
      `docs/product/functional-specification.md` (1412, antes 1397). *Ruta: delegada.*
- [x] **T6** — Reconciliar `docs/STATUS.md` con el alcance de producto.
      **133 líneas, antes 465.** *Ruta: delegada.*
- [x] **T7** — Reconciliar `AGENTS.md`, que enrutaba a los documentos superados como
      fuentes de verdad. Cinco ediciones quirúrgicas: orden de lectura, fuentes de
      verdad, invariante de aislamiento como número uno, límites de alcance
      (dashboard y API de lectura pasan de prohibidos a ordenados por el roadmap) y
      el párrafo de ADR 0003. **188 líneas, antes 161.** *Ruta: delegada.*
      *Tarea añadida durante la ejecución: sin ella, la base documental nueva fallaba
      en su punto de entrada.*
- [x] **T8** — Corregir el motivo de superación de
      `docs/product/functional-specification.md` en `ROADMAP.md` e `INDEX.md`.
      *Ruta: inline (dos ediciones mecánicas). Ver Corrección registrada.*

## Criterios de aceptación

1. Un lector nuevo entiende, leyendo sólo T1 y T2, qué es Leda como producto y
   dónde termina el núcleo.
2. T2 nombra el aislamiento entre clientes como invariante número uno y documenta la
   violación conocida con su evidencia.
3. T3 ordena el trabajo sin reintroducir un plan por fases numeradas.
4. Ningún documento nuevo afirma como implementado algo que no lo está.
5. Ningún documento existente se borra.

## Verificación aplicable

TDD está habilitado en el proyecto (fuente: `CLAUDE.md`, runner
`.venv\Scripts\python.exe -m pytest`), pero **no aplica a esta unidad**: son archivos
de documentación sin comportamiento ejecutable. Aplica a las unidades de código
siguientes.

Verificación de esta unidad: lectura estructural de los archivos producidos contra
los cinco criterios de aceptación, y comprobación de que cada afirmación técnica
citada corresponde a la evidencia registrada arriba.

## Estrategia de entrega

`ask-on-risk`. Pronóstico de líneas autoradas: ~700 (documentación). Supera el
umbral orientativo de ~400, por lo que antes de comitear se decide si esta base
documental viaja como una sola unidad o se divide. Nota: el árbol ya tiene ~2271
inserciones sin comitear previas a esta unidad, y el usuario difirió esa decisión.

## Progreso

- 2026-09-22 — Documento creado. Exploración y auditoría completas.
- 2026-09-22 — T1 a T4 cerradas por un único writer delegado. 461 líneas en cuatro
  archivos, por debajo del pronóstico de ~700.

## Verificación registrada

Lectura estructural completa de los cuatro archivos producidos, hecha por el
orquestador, no por el writer.

| Criterio | Resultado | Evidencia observada |
|---|---|---|
| 1. Un lector nuevo entiende producto y frontera con T1 y T2 | Cumplido | `que-es-leda.md` define espacio como cliente y la tabla configuración/núcleo; `frontera.md` mapea núcleo, puertos y adaptadores. |
| 2. T2 nombra el aislamiento como invariante 1 y documenta la violación | Cumplido | `frontera.md:97-100` regla 1; `frontera.md:119` fila de incumplimiento con las cuatro citas de esquema; `frontera.md:126-136` consecuencia. |
| 3. T3 ordena sin fases numeradas | Cumplido | `ROADMAP.md:54-127`, siete unidades con entrega, dependencia y cierre. |
| 4. Ningún documento afirma implementado lo que no está | Cumplido | `que-es-leda.md:28-29,31-33` marcan las superficies inexistentes; `frontera.md:88-89` marca los adaptadores ausentes. |
| 5. Ningún documento existente se borra | Cumplido | `git status --short docs/` no muestra ninguna eliminación; sólo dos archivos nuevos y dos modificados. |

Alcance respetado: el writer tocó exactamente los cuatro archivos indicados. El resto
de las modificaciones del árbol son preexistentes a esta unidad.

Limitación honesta heredada al roadmap: el propietario efectivo de las funciones
`security definer` no se verificó contra un clúster vivo. `frontera.md:133-136` lo
declara como tal y lo deriva a la unidad de cierre del aislamiento.

## Corrección registrada

La directiva que se le pasó al writer de T5 contenía una afirmación falsa: describía
`docs/product/functional-specification.md` como "escrita para un único equipo". El
writer se apartó de la directiva antes que escribir algo falso y lo reportó.

Verificado: ese documento se titula "Especificación funcional **genérica**" y declara
su ámbito como "Leda como Project Manager digital configurable para cualquier
equipo" (`docs/product/functional-specification.md:1,19`). El motivo correcto es otro:
precede al modelo multi-tenant, no separa configuración de cliente de núcleo del
producto y no trata el aislamiento como garantía.

T8 corrigió las dos filas que repetían el motivo equivocado, en `ROADMAP.md` e
`INDEX.md`.

## Hallazgos de entorno

Encontrados al intentar reejecutar la suite, fuera del alcance documental de esta
unidad pero relevantes para la línea base:

- **El entorno virtual está roto.** `.venv/pyvenv.cfg` declara `home = C:\Python314`
  y fue creado en `D:\Laboratorios\Leda\Leda\.venv`. Ninguna de las dos rutas
  existe. Todo comando de la sección "Comandos verificados" que use
  `.venv\Scripts\python.exe` falla hoy. No se modificó.
- **`.codegraph/` no figura en `.gitignore`** y aparece sin seguimiento. Es un índice
  local y no debería incorporarse a la línea base.
- `.venv/` y `.env*` sí están correctamente excluidos.

## Próximo paso

Armar el commit de línea base con el usuario. Decisiones abiertas para ese commit:
agregar `.codegraph/` a `.gitignore`, resolver si `odd/` se versiona, y decidir si la
línea base viaja como un commit único o en varios.
