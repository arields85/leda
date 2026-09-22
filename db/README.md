# La base de datos

PostgreSQL 18 o posterior, esquema `prisma`. Es la fuente de verdad del estado operativo:
qué se está haciendo, quién lo tiene, en qué estado está y qué se decidió.

> **Actualización mayor:** cambiar la imagen a PostgreSQL 18 no actualiza un volumen
> de datos creado por PostgreSQL 16. No iniciar ese volumen con la nueva imagen: un
> clúster existente requiere una migración planificada mediante `pg_upgrade`,
> dump/restore o replicación lógica. Los entornos realmente descartables pueden
> recrearse. Este repositorio no prescribe ni ejecuta uno de esos procedimientos.
> Desde PostgreSQL 18, la imagen oficial monta el volumen en `/var/lib/postgresql` y
> usa un `PGDATA` versionado dentro de ese directorio.

Lo que **no** vive acá: la identidad y las reglas de Prisma (viven en `nucleo/`,
versionadas en git) y los secretos (tokens y claves, en el archivo de secretos
de la VPS).

```
git          →  quién es Prisma y cómo está configurado cada equipo
PostgreSQL   →  qué está pasando ahora
secretos     →  tokens y claves, nunca en git ni en la base
```

## Probar

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f esquema.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f pruebas.sql
```

`pruebas.sql` carga un CoreWork mínimo y comprueba 15 reglas. Todas tienen que
pasar; si alguna falla, el archivo aborta.

## Grupos de tablas

**Plataforma** — `app_user`, `platform_role`. El eje global. Una persona existe
una sola vez, aunque esté en varios equipos. Ser administrador no otorga nada
dentro de ningún espacio.

**Espacios** — `workspace`, `workspace_version`, `area`, `rol`, `membership`,
`absence`, `work_calendar`, `holiday`. El eje por equipo. `membership` es la
tabla que cruza los dos ejes.

**Política** — `permission`, `approval_policy`, `approval_requirement`,
`escalation_route`, `glossary_term`, `message_template`, `persona_config`,
`workspace_setting`, `task_evidence_policy`, `cadence_job`. Es el pack YAML
convertido en filas. Acá es donde la autoridad deja de ser prosa y pasa a ser
algo que la base puede verificar.

**Trabajo** — `objective`, `task_draft`, `task_intake_request`,
`task_intake_field`, `task_intake_choice_set`, `task_intake_choice`,
`task_intake_free_text_slot`, `task`, `task_state_event`,
`objective_state_event`, `dependency`, `blocker`, `evidence`, `approval`,
`pending_reply`.

`prisma_app` puede insertar borradores, pero no tareas. Una tarea nueva se crea
únicamente mediante `confirmar_borrador_tarea`, que revalida la vista previa y
deja `task.source_draft_id`. `prisma_admin` conserva escritura directa para
mantenimiento controlado y carga de fixtures; ese privilegio residual no es una
ruta de aplicación.

La confirmación usa una conexión separada configurada con
`PRISMA_AUTHORITY_DB_URL`, cuyo login sólo puede asumir `prisma_gateway`.
`prisma_app` no puede ejecutar la función sensible. La función recibe el
`telegram_user_id` autenticado por el webhook, resuelve la identidad humana en
PostgreSQL y usa `clock_timestamp()`; no acepta `app_user_id` ni reloj del
caller. No hay fallback a `PRISMA_DB_URL` porque compartir credencial destruiría
la frontera de autoridad.

La función corre como `SECURITY DEFINER` con search path fijo y sólo
`prisma_gateway` recibe `EXECUTE`. El login de la URL debe ser `NOINHERIT`: no
obtiene privilegios de tablas ni puede administrar datos directamente; el
contexto transaccional asume `prisma_gateway` únicamente durante la llamada.
El rol no tiene `BYPASSRLS`, membresía administrativa ni privilegios generales
de aplicación.

El login de esa URL debe tener únicamente `SET ROLE prisma_gateway`; no debe ser
miembro de `prisma_app` ni `prisma_admin`. La migración crea el rol sin login y
retira el overload anterior que aceptaba actor/reloj. `0002` reemplaza además la firma
de Unidad 1A por `confirmar_borrador_tarea(uuid, text, bigint, bigint)`, que valida el
chat originario y ejecuta el cierre terminal integral; no queda ejecutable la firma de
tres argumentos. Sólo esa firma y
`resolver_ingreso_borrador(uuid, text, bigint, bigint)` se conceden a
`prisma_gateway`.

El owner del proceso debe crear ese login y concederle membresía exclusiva en
`prisma_gateway`; la migración no crea ni guarda credenciales. El login usado
por `PRISMA_DB_URL` no debe ser miembro de `prisma_gateway`.

La resolución terminal vive en esa función; `resolver_ingreso_borrador` es sólo su
entrada nominada. Conversión o cancelación, cierre de request/draft/pending/opciones,
auditoría y respuesta visible deduplicada quedan en la misma transacción de autoridad.
Un doble callback devuelve el resultado persistido y no crea otra tarea ni otro mensaje
terminal.

**Mensajería** — `inbound_message`, `message_outbox`.

**Sistema** — `model_config`, `learning`, `incident`, `audit_log`,
`conversation_access_log`.

## Las cinco decisiones que importan

### El estado es una proyección, no un campo

`task.estado` no se puede escribir. Un `UPDATE` directo lanza excepción. Para
mover una tarea se inserta una fila en `task_state_event` y un disparador aplica
la proyección.

Consecuencia: el historial completo existe siempre, no como algo que alguien se
acordó de registrar, sino porque es el único camino posible.

### Las condiciones de cierre son funciones

`motivo_no_cierra_tarea(uuid)` y `motivo_no_cierra_objetivo(uuid)` devuelven
`null` si se puede cerrar, o el motivo por el que no. Un disparador las llama
antes de aceptar el evento de cierre.

Esto es lo que impide que el modelo de lenguaje dé por terminada una tarea
porque alguien le escribió "ya está". Prisma puede proponer el cierre; quien lo
autoriza es la comprobación más la persona que corresponda.

Un objetivo sólo cierra si todas sus tareas terminaron, todos sus objetivos
hijos terminaron, cada área participante aprobó su componente y existe la
aprobación de la autoridad final del espacio. Es la regla que el documento
original pedía en prosa.

### El aislamiento está en la base

Todas las tablas por espacio tienen RLS activo y forzado. El agente se conecta
con el rol `prisma_app` y declara en qué espacio trabaja:

```sql
set role prisma_app;
set "prisma.workspace_id" = '<uuid del espacio>';
```

A partir de ahí no ve nada de otro equipo, ni por error ni a propósito. No
depende de que el modelo se acuerde de filtrar.

El rol `prisma_admin` tiene `bypassrls` y es el que usa la consola de
administración.

### Nada sale sin pasar por la cola

Prisma nunca llama a Telegram. Escribe en `message_outbox` con una
`dedupe_key` única y un worker despacha. Si la VPS se reinicia y el proceso
vuelve a generar el mismo mensaje, la clave lo rechaza.

`telegram_utf16_units` y `message_outbox_telegram_payload` hacen que una fila
visible nunca exceda el contrato de Telegram: 4096 unidades UTF-16 sin botones
y margen seguro de 3900 cuando referencia opciones. La aplicación valida y
normaliza antes de insertar; el constraint cubre además las respuestas
terminales que Unidad 1A crea atómicamente dentro de PostgreSQL.

Esa misma tabla resuelve la confirmación humana: un mensaje que la requiere se
queda en `esperando_confirmacion` hasta recibirla o caducar.

### El modelo se configura en la base

`model_config`, editable desde la consola. No está en el pack ni en el núcleo,
que fue uno de los errores del documento original. La clave de API va en el
archivo de secretos.

## Migraciones

`esquema.sql` es el estado actual completo y sirve para levantar una base
limpia. Las bases existentes avanzan con los scripts versionados de
`db/migrations/`; no se recrean. La migración `0001_task_commitment.sql` tiene
un preflight que aborta si encuentra tareas incompatibles. Después,
`0002_general_task_intake.sql` agrega el intake y cancela pendientes legacy de
`crear_tarea` sin reinterpretarlos. Antes de DDL toma locks consistentes e inventaría
drafts, pending, previews, opciones y outbox Unit1A: completa sólo previews antiguas
exactas, deriva `open/cancelled/converted` desde los hechos existentes y aborta la
transacción ante cualquier forma que no pueda revalidarse o entregarse exactamente.

Aplicar cada archivo directamente con `psql -f` y `PGCLIENTENCODING=UTF8`; en
PowerShell se fija antes con `$env:PGCLIENTENCODING = "UTF8"`. No usar
`Get-Content`, `type` ni otro pipeline de texto para alimentar `psql`, porque agrega
una decodificación y recodificación fuera del control del repositorio. `0002` además
fija `\encoding UTF8` y aborta antes del DDL si la entrada no conserva su testigo
Unicode.

```
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 \
  -f db/migrations/0001_task_commitment.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 \
  -f db/migrations/0002_general_task_intake.sql
```

El comando es una instrucción operativa, no debe ejecutarse contra la base local
operativa durante desarrollo. Regla: **ningún cambio de esquema a mano en la
VPS.**

Después de aplicar `0001`, reimportar el pack aprobado para materializar
`evidencia.por_area`. Hasta esa reimportación, la ausencia de política se trata
como no resuelta y no se ofrece confirmación de tareas nuevas.

El rollback `db/rollbacks/0002_general_task_intake.sql` toma primero el advisory lock de
la migración y locks de tablas, y sólo opera mientras no exista
lineage de intake. Si encuentra requests o un draft convertido, aborta para evitar
desvincular historia o tareas comprometidas. En una migración vacía restaura los
pendientes legacy reconciliados y sus estados de outbox desde el snapshot guardado.
Las previews cuya descripción completó llevan una marca de migración; sólo se revierte
esa clave y sólo si pending, draft y preview siguen exactamente como quedaron.

Respaldo: `pg_dump` diario más archivado de WAL. La restauración se prueba cada
tres meses — conviene que sea una tarea programada de Prisma, no un recordatorio
en la cabeza de alguien.

## Pendiente

- Disparador que impida transiciones de estado no permitidas (hoy la lista de
  estados está en el tipo, pero las transiciones válidas entre ellos todavía no
  se verifican).
- Índices de búsqueda de texto sobre tareas y bloqueos.
- Política de retención para `inbound_message`.
