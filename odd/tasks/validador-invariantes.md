# Validador diario de invariantes

**Estado:** propuesto, no iniciado. **Creado:** 2026-09-27.
**Origen:** decisión del usuario (2026-09-27) tras el experimento 1 registrado en
`odd/tasks/prisma-orienta.md` ("Experimento 1 — validador de invariantes").

## Objetivo

Un chequeo diario de sólo lectura que busca en la base violaciones de los
invariantes del núcleo y registra un incidente por cada una, para detectar lo que el
código debería impedir pero igual aparece (un defecto que se escapó, un dato
cargado a mano, una migración a medias). No corrige nada: avisa.

## Evidencia de que vale la pena

Sobre una copia de la base local con los datos ficticios de las sesiones 1 y 2, el
chequeo de evidencia faltante en revisión encontró las dos tareas que el usuario vio
aprobarse a ciegas en la sesión 2 (hallazgos 8 y 9), sin saber nada de ese defecto.
El resto de los chequeos dio cero.

## Chequeos que se quedan (recomendados por el experimento)

1. **a** — tareas `en_revision` con `evidencia_pendiente` verdadero.
2. **f** — entradas a `en_curso` no exentas con una dependencia bloqueante abierta en
   ese instante (reconstruido por la hora de los eventos).
3. **l** — filas hijas cuyo `workspace_id` no coincide con el de su tarea o membresía
   (hoy sin constraint en `blocker`, `evidence`, `dependency`, `pending_reply`,
   `approval`, `task_state_event`).
4. **c** — `task.estado` distinto del último `task_state_event`.
5. **j** — el último mensaje entrante de un chat sin ninguna salida posterior.

Los demás (b, d, e, g, h, i, k, m) quedan como candidatos; `d` hoy marca todas las
tareas por `evidencia_policy_version` vacía (hueco de trazabilidad, no de la
garantía) e `i3` dio un falso positivo por textos cortos genéricos.

## Decisiones del usuario (2026-09-28)

1. **Cuándo corre:** automáticamente todos los días y además a mano. A mano, hoy con
   un comando (`python -m prisma validar <slug>`); cuando exista el panel de
   plataforma, desde un botón del panel que llame a la misma función. Automático: en
   modo servidor (`servir`), como un trabajo diario más del planificador que ya
   programa las cadencias (`reloj.montar`); en modo local (`escuchar`), una vez por día
   dentro del mismo ciclo que hoy corre la escalera y despacha la cola
   (`local.tareas_de_fondo`).
2. **A quién avisa:** al administrador de la plataforma, por el bot de administración
   y por el panel de plataforma. Cada violación queda además como incidente. Nunca a
   los integrantes del equipo.

Hechos que condicionan el diseño (verificados en el código el 2026-09-28): hoy un
incidente avisa a la **persona afectada** con un texto neutral
(`gateway.reportar_incidente_no_manejado`), no al administrador; el administrador los
ve con `python -m prisma incidentes <slug>`. El bot de administración es un cascarón
(identifica, audita y responde `ok`, `docs/capacidades.md`) y no manda avisos; el
panel de plataforma no existe. Por eso el aviso por el bot de administración es parte
de esta unidad, y el del panel queda para cuando el panel exista.

3. **Frecuencia (2026-09-28):** cada 30 minutos, junto con la escalera, los chequeos
   urgentes y livianos (persona sin respuesta, mensajes trabados en la cola, botones
   esperando sin su mensaje); una vez por día los estructurales (estado contra su
   último evento, arranque con dependencia abierta reconstruido por hora,
   `workspace_id` cruzado, evidencia faltante en revisión); y a mano cuando se pida.
   Cada violación se avisa una sola vez, cuando aparece, no en cada corrida mientras
   siga (clave estable por violación).
4. **Aviso al administrador:** por el mismo camino que los incidentes (#28), con el
   texto que disparó el problema cuando lo hay (constitución §2 y §12: el
   administrador accede a las conversaciones y ese acceso queda auditado).

Pendiente de decidir al diseñarlo: el texto del aviso y si también corre como
`postflight` antes de una sesión real.

## Consultas del experimento (referencia, no código de producción)

Escritas contra `db/esquema.sql` con las migraciones hasta `0015`; se corrieron
dentro de una sesión `default_transaction_read_only = on`.

```sql
-- Invariantes de Prisma para chequeo diario de solo lectura.
-- Derivados de: nucleo/constitucion.md, nucleo/mecanica-pm.md,
-- AGENTS.md "Invariantes vigentes", docs/decisions/0008 y 0009 (con su
-- enmienda T6a/T6b/T6c), y db/esquema.sql (tablas y funciones deterministas
-- motivo_no_cierra_tarea, evidencia_pendiente, motivo_no_arranca_tarea).
--
-- Cada bloque se ejecuta con `set default_transaction_read_only = on` ya
-- activo. Nunca selecciona texto libre, cuerpos de mensaje ni nombres reales:
-- sólo ids, timestamps, estados y columnas estructurales.

-- @check:a
-- Mecánica §3/§5: "Ya la terminé" nunca debería dejar una tarea en
-- en_revision con evidencia todavía pendiente según su propia política
-- (ADR 0009, evidencia_pendiente sobre la definición nueva de 0014).
select id, workspace_id, estado, actualizado_en
  from task
 where estado = 'en_revision'
   and evidencia_pendiente(id);
-- @endcheck

-- @check:b
-- Constitución §11 / mecánica §5: una tarea terminada tiene que seguir
-- cumpliendo, HOY, la misma comprobación determinista que la cerró
-- (motivo_no_cierra_tarea, ya con las definiciones de 0013/0014). Un
-- resultado no nulo es sospechoso: o cerró sin cumplir, o algo cambió
-- después (bloqueo reabierto, dependencia reabierta, política editada).
select id, workspace_id, motivo_no_cierra_tarea(id) as motivo, actualizado_en
  from task
 where estado = 'terminada'
   and motivo_no_cierra_tarea(id) is not null;
-- @endcheck

-- @check:c
-- Mecánica §3: "El estado actual es una proyección del último evento, no
-- un campo suelto." task.estado tiene que coincidir siempre con el
-- estado_nuevo del último task_state_event; una tarea sin ningún evento
-- tampoco debería existir (todo alta pasa por confirmar_borrador_tarea).
with ultimo as (
  select task_id, estado_nuevo,
         row_number() over (partition by task_id order by at desc, id desc) rn
    from task_state_event
)
select t.id, t.workspace_id, t.estado as estado_tabla,
       u.estado_nuevo as estado_ultimo_evento,
       (u.estado_nuevo is null) as sin_eventos
  from task t
  left join ultimo u on u.task_id = t.id and u.rn = 1
 where u.estado_nuevo is null or t.estado is distinct from u.estado_nuevo;
-- @endcheck

-- @check:d
-- AGENTS.md "Una tarea comprometida exige objetivo, responsable, fecha
-- objetivo, criterio de aceptación y política de evidencia." objective_id
-- es not null por esquema (no puede faltar); se chequean las columnas que
-- sí son nullable: responsable, fecha objetivo, criterio de aceptación y
-- evidencia_policy_version (la versión de política de evidencia vigente al
-- comprometerse).
select id, workspace_id,
       (responsable_membership_id is null) as falta_responsable,
       (fecha_objetivo is null) as falta_fecha,
       (criterio_aceptacion is null or btrim(criterio_aceptacion) = '') as falta_criterio,
       (evidencia_policy_version is null) as falta_politica_evidencia
  from task
 where responsable_membership_id is null
    or fecha_objetivo is null
    or criterio_aceptacion is null or btrim(criterio_aceptacion) = ''
    or evidencia_policy_version is null;
-- @endcheck

-- @check:e1
-- Mecánica §3: "bloqueada requiere un bloqueo abierto asociado."
select id, workspace_id, estado, actualizado_en
  from task t
 where t.estado = 'bloqueada'
   and not exists (select 1 from blocker b
                    where b.task_id = t.id and b.resuelto_en is null);
-- @endcheck

-- @check:e2
-- Mismo invariante, del otro lado: un bloqueo abierto sobre una tarea que
-- ya no está bloqueada (se movió sin resolver el bloqueo).
select b.id, b.workspace_id, t.estado as estado_tarea, b.abierto_en
  from blocker b
  join task t on t.id = b.task_id
 where b.resuelto_en is null
   and t.estado <> 'bloqueada';
-- @endcheck

-- @check:f
-- Mecánica §4: "la tarea destino no puede pasar a en_curso hasta que la
-- origen esté terminada" (cancelada libera igual, mismo criterio que
-- motivo_no_arranca_tarea). Reconstruye, a partir de los timestamps de
-- task_state_event, si en el momento exacto de cada entrada a en_curso NO
-- exenta (0007/0015: restauración desde bloqueada o desde en_revision) había
-- alguna dependencia bloqueante cuyo origen todavía no tenía un evento
-- terminada/cancelada con `at` <= ese instante.
with entradas as (
  select tse.id as evento_id, tse.task_id, tse.workspace_id, tse.at,
         tse.estado_anterior
    from task_state_event tse
   where tse.estado_nuevo = 'en_curso'
),
exento as (
  select e.evento_id,
    case
      when e.estado_anterior = 'bloqueada' then
        (select tse2.estado_anterior from task_state_event tse2
          where tse2.task_id = e.task_id and tse2.estado_nuevo = 'bloqueada'
            and tse2.at <= e.at
          order by tse2.at desc limit 1) = 'en_curso'
      when e.estado_anterior = 'en_revision' then
        (select tse2.estado_anterior from task_state_event tse2
          where tse2.task_id = e.task_id and tse2.estado_nuevo = 'en_revision'
            and tse2.at <= e.at
          order by tse2.at desc limit 1) = 'en_curso'
      else false
    end as restauracion
  from entradas e
)
select e.evento_id, e.task_id, e.workspace_id, e.at
  from entradas e
  join exento x on x.evento_id = e.evento_id
 where not x.restauracion
   and exists (
     select 1
       from dependency d
       join task o on o.id = d.origen_task_id
      where d.destino_task_id = e.task_id
        and d.tipo = 'bloqueante'
        and not exists (
          select 1 from task_state_event tse3
           where tse3.task_id = o.id
             and tse3.estado_nuevo in ('terminada', 'cancelada')
             and tse3.at <= e.at));
-- @endcheck

-- @check:g
-- Mecánica §7 / esquema: la aprobación de una tarea la da
-- membership.aprobador_membership_id del responsable (o, si es null, quien
-- tenga autoridad_final del espacio -- misma resolución que
-- confirmar_borrador_tarea). Prisma nunca se cuenta a sí misma como
-- aprobador (constitución §7) y el responsable no se autoaprueba.
with aprobador_esperado as (
  select t.id as task_id, t.workspace_id, t.responsable_membership_id,
         coalesce(
           resp.aprobador_membership_id,
           (select m.id from membership m join rol r on r.id = m.rol_id
             where m.workspace_id = t.workspace_id and m.activo and r.autoridad_final
             limit 1)
         ) as aprobador_esperado_id
    from task t
    left join membership resp on resp.id = t.responsable_membership_id
)
select a.id, a.workspace_id, a.sujeto_id as task_id, a.aprobador_membership_id,
       ae.aprobador_esperado_id,
       (a.aprobador_membership_id = ae.responsable_membership_id) as autoaprobacion
  from approval a
  join aprobador_esperado ae on ae.task_id = a.sujeto_id
 where a.sujeto_tipo = 'tarea'
   and (a.aprobador_membership_id = ae.responsable_membership_id
        or (ae.aprobador_esperado_id is not null
            and a.aprobador_membership_id <> ae.aprobador_esperado_id));
-- @endcheck

-- @check:h1
-- Mecánica §12: "Un mensaje que requiere confirmación humana espera en la
-- cola hasta que la recibe o hasta que caduca." Una pending_action
-- 'esperando' con vence_en ya pasado debería haber caducado.
select id, workspace_id, herramienta, creado_en, vence_en
  from pending_action
 where estado = 'esperando'
   and vence_en <= now();
-- @endcheck

-- @check:h2
-- Toda acción pendiente que espera un toque debería tener un mensaje en la
-- cola que la ofrezca (si no, nadie puede resolverla nunca).
select pa.id, pa.workspace_id, pa.herramienta, pa.creado_en
  from pending_action pa
 where pa.estado = 'esperando'
   and not exists (select 1 from message_outbox mo
                    where mo.pending_action_id = pa.id);
-- @endcheck

-- @check:i1
-- Mecánica §12: reintentos con espera creciente; un mensaje no debería
-- quedar 'pendiente'/'listo' mucho después de su hora programada (worker
-- caído o cola trabada). Umbral: 24h, proporcional a que esta es una copia
-- estática sin worker corriendo.
select id, workspace_id, chat_id, tipo, estado, programado_para
  from message_outbox
 where estado in ('pendiente', 'listo')
   and programado_para < now() - interval '24 hours';
-- @endcheck

-- @check:i2
select id, workspace_id, chat_id, tipo, estado, intentos, programado_para
  from message_outbox
 where estado = 'fallido';
-- @endcheck

-- @check:i3
-- Mecánica §12: "La clave combina espacio, destinatario, tipo de mensaje y
-- ventana temporal." dos filas con el mismo cuerpo (comparado sólo por
-- hash, nunca por texto) al mismo chat dentro de 60s son un aviso
-- duplicado -- la deduplicación por dedupe_key no debería permitirlo salvo
-- que la clave misma varíe por error.
select a.id as id_a, b.id as id_b, a.workspace_id, a.chat_id, a.tipo,
       extract(epoch from (b.programado_para - a.programado_para)) as delta_segundos
  from message_outbox a
  join message_outbox b
    on b.workspace_id = a.workspace_id and b.chat_id = a.chat_id
   and b.id > a.id
   and md5(a.cuerpo) = md5(b.cuerpo)
   and abs(extract(epoch from (b.programado_para - a.programado_para))) <= 60;
-- @endcheck

-- @check:j
-- "Nunca fallar en silencio": alguien que le escribió a Prisma y no recibió
-- ninguna salida por ese chat después. Se mira sólo el último inbound de
-- cada chat -- uno anterior ya resuelto por un outbox intermedio no cuenta.
with ultimo_inbound as (
  select workspace_id, chat_id, max(at) as at
    from inbound_message
   group by workspace_id, chat_id
)
select ui.workspace_id, ui.chat_id, ui.at as ultimo_inbound_en
  from ultimo_inbound ui
 where not exists (
   select 1 from message_outbox mo
    where mo.workspace_id = ui.workspace_id and mo.chat_id = ui.chat_id
      and mo.programado_para >= ui.at);
-- @endcheck

-- @check:k
-- Constitución §10: "Los incidentes se registran sanitizados y se avisan al
-- administrador de plataforma por su canal." Si el incidente tiene a quién
-- avisar (app_user_id), notificado_en no debería quedar nulo.
select id, workspace_id, severidad, at, etapa
  from incident
 where notificado_en is null
   and app_user_id is not null;
-- @endcheck

-- @check:l
-- AGENTS.md "Invariantes vigentes": "Ninguna tabla con alcance de espacio
-- queda sin workspace_id ni sin row level security forzado." blocker,
-- evidence, dependency, pending_reply y approval NO tienen una constraint
-- compuesta que fuerce su workspace_id a coincidir con el de la tarea/
-- membresía padre (a diferencia de task_draft, pending_action o
-- message_outbox, que sí la tienen) -- dependen de que la aplicación
-- escriba bien. Esto es exactamente lo que ADR 0003 (enmienda) señala como
-- el control que faltó.
select 'blocker' as tabla, b.id, b.workspace_id, t.workspace_id as workspace_padre
  from blocker b join task t on t.id = b.task_id
 where b.workspace_id <> t.workspace_id
union all
select 'evidence', e.id, e.workspace_id, t.workspace_id
  from evidence e join task t on t.id = e.task_id
 where e.workspace_id <> t.workspace_id
union all
select 'dependency_origen', d.id, d.workspace_id, o.workspace_id
  from dependency d join task o on o.id = d.origen_task_id
 where d.workspace_id <> o.workspace_id
union all
select 'dependency_destino', d.id, d.workspace_id, dt.workspace_id
  from dependency d join task dt on dt.id = d.destino_task_id
 where d.workspace_id <> dt.workspace_id
union all
select 'pending_reply', pr.id, pr.workspace_id, t.workspace_id
  from pending_reply pr join task t on t.id = pr.task_id
 where pr.workspace_id <> t.workspace_id
union all
select 'approval_tarea', a.id, a.workspace_id, t.workspace_id
  from approval a join task t on t.id = a.sujeto_id and a.sujeto_tipo = 'tarea'
 where a.workspace_id <> t.workspace_id
union all
select 'task_state_event', tse.id, tse.workspace_id, t.workspace_id
  from task_state_event tse join task t on t.id = tse.task_id
 where tse.workspace_id <> t.workspace_id;
-- @endcheck

-- @check:m
-- AGENTS.md / diseño: pending_reply es la tabla que sostendría la escalera
-- de recordatorios; se espera vacía mientras esa mecánica no esté cableada.
select count(*) as filas from pending_reply;
-- @endcheck
```
