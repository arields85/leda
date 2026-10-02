# ADR 0003: frontera de ingreso autenticado para efectos operativos

> **Superada por cambio de alcance — 2026-09-22.**
>
> Leda dejó de definirse como asistente interno de un único equipo y pasó a ser un
> producto de gestión de proyectos multi-tenant. Este documento se conserva como
> registro histórico y **no debe usarse para decidir**. Para el alcance vigente:
> [`../product/que-es-leda.md`](../product/que-es-leda.md),
> [`../architecture/frontera.md`](../architecture/frontera.md) y
> [`../ROADMAP.md`](../ROADMAP.md).
>
> **Su modelo de amenaza quedó superado, no refutado.** Fue escrito cuando la amenaza
> principal era el compromiso de la credencial de aplicación dentro de un solo equipo.
> En un producto multi-tenant la amenaza principal es el cruce entre clientes. El
> análisis de capacidades, fencing y separación de credenciales conserva valor técnico;
> su secuencia y su prioridad, no.
>
> **Su Corte 0 deja de estar diferido.** El catálogo ejecutable de propietarios,
> membresías, grants y ACL pasa a ser insumo directo de la unidad de cierre del
> aislamiento entre clientes del roadmap. Es precisamente el control que habría
> detectado que `task_state_event` y `objective_state_event` reciben `grant insert` sin
> `workspace_id` ni RLS.

- **Estado:** superada por cambio de alcance
- **Fecha:** 2026-08-13
- **Última enmienda:** 2026-08-14, horizonte diferido para el MVP conductual
- **Alcance:** ingreso Telegram y efectos operativos de la validación local simulada y
  el piloto controlado, incluida la autoridad técnica de salida
- **Implementación:** no implementada
- **Prioridad:** objetivo técnico aceptado y diferido; no bloquea por sí solo una
  sesión progresiva simulada cuyo gate proporcional esté comprobado

## Decisión resumida

Antes de implementar los hechos de tarea de la Unidad 1B.1, Leda incorporará una
frontera que convierta cada update autenticado de Telegram en un recibo inmutable. El
ingreso conservará un identificador privado y estable de despacho, que nunca entrega a
la aplicación; cada claim emitirá en cambio una capacidad opaca nueva, ligada a una
generación monotónica y almacenada sólo mediante su hash. Ningún efecto podrá confiar
en un actor, espacio o update declarados por el modelo, una herramienta o
`leda_app`: la función de aplicación resolverá esos datos desde el recibo, volverá a
validar membresía, autoridad y estado vigente y confirmará todos los efectos junto con
la finalización del claim en una única transacción cercada.

La frontera conserva el monolito modular y no agrega otro proceso antes del piloto.
Sí exige conexiones PostgreSQL separadas por operación y cinco logins técnicos con
membresías disjuntas: ingreso, aplicación, gateway de Unidad 1A, despacho y
administración. Esta ADR define el objetivo y una secuencia de seis cortes dentro de
1B.1-A. Mientras se construye la raíz autenticada, los efectos legacy de dominio
fallarán cerrado; las consultas, la conversación y Unidad 1A continuarán. Los efectos
se reabrirán uno por uno, mediante capacidades y en la unidad de dominio que les
corresponda.

La decisión técnica no cambia, pero su implementación completa deja de ser el próximo
paso general del MVP. Unidad 1A conserva una frontera suficiente para preparar un smoke
progresivo con datos ficticios; esa afirmación no demuestra elegibilidad ni ejecución,
que requieren comprobar el gate del protocolo. Esta ADR y sus Cortes 0 a 5 se retoman
antes del piloto real o la VPS, según el control, y antes si la evidencia progresiva
demuestra que el riesgo alcanza al circuito ejercitado.

## Motivo para usuarios

Leda seguirá conversando, respondiendo consultas y sosteniendo las tareas ya
comprometidas por Unidad 1A mientras se reemplazan accesos demasiado amplios. Durante
esa transición no aceptará crear objetivos ni registrar cambios de estado, bloqueos,
evidencias o aprobaciones. Es una degradación temporal deliberada: es preferible
rechazar un cambio de forma clara antes que atribuírselo a la persona o al espacio
equivocados.

Las nuevas activaciones con `/start` también se pausarán desde la separación real de
credenciales hasta que el onboarding use el ingreso autenticado. Quienes ya estén
activados conservarán conversación y consultas. Cada capacidad de dominio volverá a
abrirse sólo después de demostrar su identidad, autoridad, idempotencia y rollback.

## Contexto

Telegram entrega identificadores de update, chat y usuario, pero el procesamiento
actual lleva esa identidad por el gateway compartido sin un recibo autenticado que
las funciones de efecto puedan verificar. Además, el inbound actual es duplicable y
el webhook sólo comprueba el secreto cuando está configurado: hoy un secreto vacío
deja esa validación desactivada.

La Unidad 1B.1 pretende derivar cambios de estado desde hechos expresados en lenguaje
natural. Proteger únicamente el grafo de estados no alcanza si `leda_app`, el modelo
o una herramienta pueden elegir el actor o el espacio con el que se invoca ese
límite. La autenticidad del origen debe existir antes que los nuevos efectos.

Unidad 1A ya mantiene un gateway dedicado, `leda_gateway`, para convertir un
borrador en tarea comprometida. Ese límite se conserva, pero deberá consumir la
identidad derivada de un recibo autenticado en lugar de aceptar libremente un actor
Telegram.

## Modelo de amenaza y confianza

La frontera protege frente a:

- instrucciones o datos maliciosos que alcancen al LLM;
- herramientas que intenten declarar otro actor, espacio o update;
- SQL ejecutado con una credencial `leda_app` comprometida;
- reentregas, carreras y reintentos que intenten repetir o reinterpretar un efecto;
- una credencial de aplicación que intente crear, cambiar o enumerar recibos.

La frontera confía en Telegram y en la autenticación específica del bot, en el código
mínimo de ingreso que valida y persiste el update, en PostgreSQL y en las funciones
propietarias que resuelven capacidades y aplican autoridad. También confía en que las
credenciales operativas se provisionan y custodian por separado.

No protege frente al compromiso total del proceso Python. Antes del piloto el mismo
monolito puede mantener conexiones con credenciales diferentes; un atacante con
capacidad de leer memoria o ejecutar código arbitrario en todo el proceso podría
alcanzarlas. Reducir ese riesgo mediante separación de procesos pertenece al
endurecimiento posterior y no se presenta como control actual.

## Fronteras de credenciales y privilegios

Los logins PostgreSQL de los siguientes caminos deben ser diferentes y sus membresías
no pueden cruzarse:

| Camino | Login objetivo | Privilegio permitido |
|---|---|---|
| Ingreso Telegram | `leda_ingress` | Autenticar y registrar el recibo; recuperar su despacho y resultado por las interfaces acotadas. |
| Aplicación, LLM y herramientas ordinarias | `leda_app` | Reclamar trabajo por la interfaz autorizada y presentar un plan a su única función superior de aplicación; no crear, modificar ni enumerar recibos ni escribir directamente sus efectos. |
| Conversión de Unidad 1A | `leda_gateway` | Ejecutar únicamente la función superior del callback de compromiso, a partir de identidad derivada del recibo y sin DML directo. |
| Despacho de mensajes | `leda_dispatcher` | Reclamar outbox listo, marcar envío, reintento o fallo y abrir incidentes técnicos de transporte. No crear contenido, cambiar destinatarios ni escribir dominio o auditoría humana. |
| Administración operativa | `leda_admin` | Ejecutar tareas administrativas separadas del servicio y del polling. |

Compartir un login que pueda asumir más de uno de estos roles sensibles invalida el
modelo, aunque cada rol tenga grants individualmente acotados. El servicio web y el
polling no deben cargar la credencial administrativa en el diseño objetivo. Las
tareas administrativas se ejecutan mediante una invocación operacional separada; esto
no exige agregar un servicio ni un proceso permanente antes del piloto.

`leda_gateway` no es un rol general de autoridad: permanece reservado a la
conversión de Unidad 1A. `leda_dispatcher` tampoco decide qué se comunica. Sólo
consume filas de outbox ya autorizadas y listas, registra el resultado técnico del
transporte y, si corresponde, abre un incidente técnico. El contenido, el destinatario
y la clave de deduplicación quedan fijados antes de que el dispatcher los reclame.

Todos estos logins serán `NOINHERIT` y sus membresías serán disjuntas. Los roles
propietarios sin login que respalden funciones `SECURITY DEFINER` no serán asumibles
por ellos. Sus funciones deben fijar un `search_path` seguro, calificar objetos y
exponer sólo la operación mínima. Los grants y privilegios públicos o heredados que
permitan omitir una frontera se revocarán explícitamente. Serving y polling no
cargarán un login administrativo ni uno propietario.

La provisión de roles de clúster es una operación separada de la migración de objetos
de la base. Ambas rutas deben ser reproducibles y restaurables: una instalación limpia
y una base migrada deben terminar con la misma matriz efectiva de owners, membresías,
grants y revokes. La evidencia incluirá un ensayo representativo en un clúster aislado,
no sólo pruebas realizadas con roles preexistentes en el entorno de desarrollo.

## Inventario raíz de escritura legacy

La inspección estática exhaustiva del esquema versionado y de sus rutas conocidas
establece la raíz que debe convertir el Corte 0 en un catálogo ejecutable. No es una
consulta al catálogo efectivo de producción ni prueba que esos privilegios estén hoy
desplegados exactamente así.

| Hallazgo raíz | Conclusión normativa |
|---|---|
| Superficie directa | El esquema versionado deja 26 tablas directamente mutables por `leda_app`. El inventario ejecutable debe nombrarlas y clasificar cada verbo DML como necesario, temporal o prohibido. |
| Mutación indirecta | Insertar un evento de tarea puede mutar la proyección de `task`; retirar `UPDATE task` no cierra ese camino. Los privilegios sobre eventos y toda función o trigger alcanzable forman parte de la misma superficie de efecto. |
| ACL de funciones | Las funciones conservan una superficie potencial por privilegios `EXECUTE` de `PUBLIC`. Cada función debe tener owner, `search_path`, llamadores y ACL explícitos; el endurecimiento revoca `PUBLIC` antes de otorgar la interfaz mínima. |
| Credencial compartida | La topología Docker declarada puede hacer que varios caminos usen una misma credencial con capacidad de superusuario. Separar nombres de rol dentro de una sesión privilegiada no constituye aislamiento real. |
| Límite probatorio | El catálogo efectivo de cada entorno, especialmente producción, sigue `PENDIENTE` de inventario verificado sobre `pg_roles`, membresías, owners, ACL de tablas/secuencias/funciones/esquemas, `PUBLIC`, atributos de superusuario y credenciales cargadas por cada comando. |

El número 26 describe tablas con mutación directa según análisis estático; no incluye
por sí solo mutaciones indirectas, funciones, secuencias, ownership, herencia ni
superusuario. Por eso no puede usarse como afirmación de cierre ni como prueba de la
base operativa.

## Separación de registros y autoridad

Conversación, auditoría autoritativa e incidentes técnicos son registros distintos.
Compartir almacenamiento o una etiqueta genérica de "evento" no les concede la misma
autoridad.

| Registro | Contenido | Quién puede originarlo | Lo que no demuestra |
|---|---|---|---|
| Conversación | Inbound recibido y mensajes visibles preparados/enviados por outbox. | Ingreso autenticado para inbound; fronteras autorizadas para crear outbox; dispatcher sólo actualiza el resultado de transporte. | No demuestra por sí mismo una decisión humana, autoridad de dominio ni éxito del efecto. |
| Auditoría autoritativa | Actor humano derivado, autoridad revalidada, operación, resultado y objetos enlazados. | Únicamente T2b cercada, `leda_gateway` para Unidad 1A o una acción administrativa identificada y acotada. | No puede reconstruirse como verdad humana desde texto libre, tool calls o una escritura de `leda_app`. |
| Incidente técnico | Fallos de ingreso, procesamiento, despacho o transporte y su estado operativo. | Fronteras técnicas mínimas, incluido `leda_dispatcher` para transporte. | No equivale a auditoría humana, aprobación, evidencia ni hecho de dominio. |

`leda_app` no puede fabricar una auditoría que atribuya una intención, hecho o
decisión a una persona. Una T2b puede registrar la interpretación y el resultado sólo
después de derivar la identidad desde el recibo y revalidar la autoridad. Las acciones
administrativas deben identificar al operador y su interfaz; poseer `leda_admin` no
autoriza atribuir una acción a otro humano.

El inbound histórico se conserva como conversación legacy de sólo lectura y no
autoritativa. No se elimina, promueve a recibo autenticado, reintenta ni usa para
producir efectos. Su valor es histórico y contextual; las garantías de esta ADR
comienzan con recibos creados por T1 después de activar la frontera.

## Secuencia normativa de endurecimiento

Los cortes 0 a 5 son subcortes ordenados de 1B.1-A, no una reordenación general de
`ROADMAP.md`. Ningún corte se declara implementado por esta ADR. La secuencia es
obligatoria cuando se retome 1B.1-A, pero no es un prerrequisito para toda prueba
simulada por Telegram de un circuito ya acotado.

| Corte | Objetivo | Alcance | Comportamiento preservado | Degradación temporal explícita | Aceptación | Migración y rollback | Dependencia |
|---|---|---|---|---|---|---|---|
| 0. Catálogo ejecutable | Convertir el inventario estático en una especificación verificable de toda autoridad de escritura. | Tablas, secuencias, funciones, triggers, owners, roles, membresías, `PUBLIC`, superusuario y credencial cargada por camino; pruebas negativas por principal y verbo. | Todo el comportamiento actual; el corte observa y prueba antes de retirar privilegios. | Ninguna funcional deliberada. Una discrepancia bloquea el Corte 1. | El catálogo esperado falla ante una concesión no clasificada; la matriz negativa cubre DML, `EXECUTE`, `SET ROLE`, ownership, RLS y caminos indirectos; el inventario efectivo del entorno objetivo queda registrado sin secretos. | Incorporar catálogo y pruebas antes de migrar ACL. Rollback: retirar sólo el arnés si fuera defectuoso; conservar la evidencia y no cambiar privilegios para hacer pasar una expectativa. | Ninguna; prerrequisito de todos los cortes siguientes. |
| 1. Higiene ACL | Eliminar autoridad implícita o no usada sin cambiar todavía el alcance funcional legítimo. | `REVOKE EXECUTE ... FROM PUBLIC`, ACL explícitas y retiro del DML de `leda_app` que el catálogo demuestre innecesario; owners y `search_path` seguros. | Consultas, conversación, onboarding vigente, Unidad 1A, efectos legacy legítimos y despacho existentes. | Ninguna prevista; toda dependencia de un permiso no clasificado es un fallo de aceptación, no una razón para ampliar ACL. | Baseline legítima y Unidad 1A pasan; pruebas negativas demuestran ausencia de `PUBLIC` y DML no usado; instalación limpia y migración convergen. | Migración versionada desde el catálogo del Corte 0. Rollback restaura sólo ACL previas nominadas si todavía no se abrió un corte posterior y sin grants amplios a `PUBLIC`; una ruta dependiente no documentada vuelve a cerrar el corte. | Corte 0 aceptado. |
| 2. Credenciales reales | Hacer efectivas las fronteras técnicas antes de introducir ingreso autenticado. | Logins `NOINHERIT` y membresías disjuntas para `leda_ingress`, `leda_app`, `leda_gateway`, `leda_dispatcher` y `leda_admin`; serving/polling sin administración; dispatcher mínimo; eliminar superusuario compartido en los caminos operativos. | Usuarios ya activados, consultas, conversación, Unidad 1A y entrega de outbox mediante el dispatcher dedicado. | Se pausan nuevas activaciones `/start` desde este corte hasta aceptar el onboarding autenticado del Corte 4. | Cada comando carga sólo su credencial; `SET ROLE`, ownership y superusuario están negados; gateway sólo ejecuta Unidad 1A; dispatcher sólo reclama outbox listo, marca resultado y abre incidentes de transporte sin alterar contenido, destinatario ni dominio. | Provisionar roles de clúster por separado y migrar grants con ventana controlada. Rollback pausa procesos, revierte el ejecutable y restaura únicamente la matriz nominada del Corte 1; no se continúa a cortes posteriores con credenciales compartidas. | Corte 1 aceptado y credenciales reales disponibles. |
| 3. Cierre de efectos legacy | Impedir que una ruta anterior eluda recibo, capacidad o T2b. | Fail-closed para creación de objetivos, cambios de estado de tarea, bloqueos, evidencias y aprobaciones; revocar DML de eventos que muten dominio indirectamente y cerrar funciones equivalentes. | Consultas, conversación, usuarios activados, Unidad 1A y despacho de outbox continúan. | Las cinco familias de efectos quedan temporalmente no disponibles; `/start` nuevo continúa pausado. | Cada intento por herramienta, función, DML directo, evento, actor/GUC forjado o principal incorrecto falla sin dominio, auditoría autoritativa ni outbox de éxito; las regresiones preservadas siguen pasando. | Migración y cambio de rutas se activan juntos, con mensajes de rechazo explícitos. Rollback seguro mantiene fail-closed; sólo antes de exponer el ingreso nuevo puede restaurarse una ruta legacy nominada, bajo decisión explícita y catálogo actualizado. | Corte 2 aceptado. |
| 4. Ingreso autenticado | Activar T1/T2a/T2b, recuperar onboarding y adaptar Unidad 1A sin reabrir otros efectos. | Recibo inmutable, capacidad cercada, identidad derivada, webhook/polling, recuperación, onboarding autenticado y única T2b de gateway; inbound histórico legacy de sólo lectura. | Consultas, conversación, usuarios activados, Unidad 1A y dispatcher; después de aceptar el corte vuelven nuevas activaciones `/start`. | Los cinco efectos de dominio del Corte 3 permanecen cerrados; durante la ventana se pausa ingreso hasta verificar migración y credenciales. | Todas las pruebas de fencing, replay, rollback por escritura, commit ambiguo, bots, onboarding, Unidad 1A, privilegios y conexiones pasan; ningún inbound histórico se promueve, reintenta ni produce efectos. | Migrar objetos y rutas con ingreso pausado; abrir `/start` sólo tras aceptación. Rollback vuelve al estado fail-closed del Corte 3, pausa onboarding y conserva recibos/resultados T1 para reconciliación; nunca los convierte en inbound legacy. | Corte 3 aceptado. |
| 5. Reapertura por capacidad | Recuperar cada efecto sólo cuando su unidad posea un límite de dominio completo. | Una capacidad y función superior por familia: objetivos, estado de tarea, bloqueos, evidencia y aprobaciones; ordenadas por la unidad vigente, no como apertura masiva. | Todo lo aceptado en cortes anteriores y cualquier capacidad ya reabierta. | Cada familia aún no verificada continúa fail-closed. No existe fecha que fuerce su reapertura. | Por familia: identidad y autoridad derivadas, estado vigente, matriz negativa, concurrencia, replay, auditoría autoritativa, outbox, fallo atómico, migración y escenario operativo pasan con pruebas nominadas. | Migración pequeña por capacidad, sin devolver DML directo a `leda_app`. Rollback revoca esa interfaz y vuelve sólo esa familia a fail-closed, preservando recibos, auditoría y las demás capacidades. | Corte 4 aceptado y contrato de la unidad de dominio correspondiente aprobado. |

La aceptación de un corte exige comando, resultado exacto, entorno, evidencia
sanitizada y límite de rollback registrados. Una revisión estática, un test existente
sin ejecutar o una migración escrita no satisfacen esa aceptación.

## Estado persistido y capacidades

El protocolo separa deliberadamente cuatro conceptos:

| Concepto | Propósito y restricción |
|---|---|
| Recibo inmutable | Conserva la identidad autenticada, el envelope canónico y la clave `(bot_scope, update_id)`. Su contenido no cambia durante claims, reintentos ni recuperación. |
| Identificador privado de despacho | Referencia estable que sólo usa `leda_ingress` para localizar y recuperar el recibo. No autoriza efectos y nunca se expone a `leda_app`, al LLM, a herramientas ni a `leda_gateway`. |
| Capacidad de claim | Secreto opaco de alta entropía emitido para una sola generación. La aplicación o el gateway reciben el valor; PostgreSQL conserva únicamente su hash. Cada claim confirmado rota la capacidad. |
| Ledger de procesamiento | Estado mutable separado del recibo: generación monotónica, estado `pending`, `interpreting` o terminal, propietario del claim, hash de capacidad, vencimiento del lease y resultado determinista. |

El lease sólo determina cuándo un recibo vuelve a ser elegible para reclaim. No es una
prueba de autoridad ni revoca por sí mismo al worker anterior. La revocación efectiva
ocurre cuando una nueva transacción de claim bloquea la fila, incrementa la generación
y rota la capacidad. Una extensión de lease es sólo una ayuda de disponibilidad.

## Secuencia de extremo a extremo

1. El webhook verifica un secreto obligatorio y específico del bot antes de aceptar
   el update. En polling, el cliente obtiene el update mediante la credencial del bot
   correspondiente. Cada bot se representa mediante un `bot_scope` estable.
2. El camino de ingreso usa exclusivamente `leda_ingress` y clasifica el tipo de
   update. Un `edited_message` puede conservarse como historia o corrección, pero se
   marca sin capacidad de producir efectos operativos.
3. En la transacción durable T1, PostgreSQL inserta o reconoce el recibo inmutable y su
   fila `pending` de procesamiento. `leda_ingress` conserva el identificador privado
   y estable de despacho. T1 confirma antes del LLM, de herramientas y del ACK técnico
   que corresponda. Una reentrega idéntica recupera el estado persistido; la misma
   clave con contenido incompatible produce conflicto y ningún efecto.
4. T2a abre una conexión propia y una transacción corta con aislamiento
   `READ COMMITTED`. Selecciona una fila elegible mediante bloqueo explícito y
   `SKIP LOCKED`: `pending` o `interpreting` con lease vencido. Al reclamarla incrementa
   la generación, genera y entrega una capacidad nueva, persiste sólo su hash, fija
   propietario y lease y deja el estado en `interpreting`. Luego confirma y cierra la
   conexión.
5. La interpretación y cualquier llamada al LLM ocurren fuera de toda transacción. El
   worker conserva capacidad y generación; al LLM sólo entrega el contexto autorizado
   obtenido desde el recibo, nunca la capacidad ni otro secreto. Cada claim usa su
   propia conexión; no se comparte una conexión cacheada con heartbeat, aplicación ni
   recuperación.
6. Un heartbeat opcional usa otra conexión y transacción corta. Bloquea la fila y sólo
   extiende un lease todavía vigente cuando coinciden capacidad, generación,
   propietario y estado `interpreting`. No revive un lease vencido, no reduce ni
   reemplaza las comprobaciones de T2b y no constituye un control de seguridad.
7. T2b abre otra conexión y una transacción corta, sin red ni LLM. Cada frontera expone
   exactamente una función superior `SECURITY DEFINER`: aplicación del plan para
   `leda_app` y callback de Unidad 1A para `leda_gateway`. La función bloquea la
   fila de procesamiento y compara en PostgreSQL el hash de capacidad, la generación,
   el estado y el lease todavía vigente.
8. Después de validar el fence, la misma función deriva actor, espacio, tipo y recibo;
   revalida membresía, autoridad y estado vigentes; aplica inbound, efectos u operación,
   ledger de operación, auditoría, outbox y resultado; y finaliza condicionalmente el
   procesamiento cuando corresponde. Unidad 1A consolida tarea, auditoría, resultado y
   outbox dentro de su T2b de gateway.
9. Si cualquier componente del fence no coincide, la función lanza una excepción con
   un `SQLSTATE` definido para pérdida de claim. La excepción revierte todas las
   escrituras de T2b, incluidas las realizadas antes de detectar un fallo inyectado. No
   existe éxito parcial ni finalización separada.
10. `leda_app` y `leda_gateway` no reciben DML directo sobre las tablas involucradas
    ni permisos de ejecución sobre funciones internas que permitan aplicar efectos sin
    finalizar condicionalmente el claim. La función superior no es una comodidad de
    API: es la única estructura autorizada de escritura de cada frontera.
11. Cada operación usa una identidad determinista ligada al recibo y al objeto de
    dominio, como `(receipt, task)`. El resultado también se persiste de forma
    determinista. Timestamps, IDs de tool calls y UUID nuevos de cada interpretación no
    participan en deduplicación ni identidad de operación.
12. Un retry o una recuperación devuelve el resultado o conflicto persistido y no
    reinterpreta una operación terminal. La respuesta visible sale por outbox. Si el
    proceso cae, la recuperación continúa por recibo y captura los errores de cada
    recibo de manera independiente, sin abortar el lote completo.

## Prueba de exclusión entre reclaim y aplicación

T2a y T2b usan `READ COMMITTED` más un bloqueo explícito sobre la misma fila de
procesamiento. Este orden produce las dos únicas carreras admisibles:

- si el reclaimer obtiene primero el bloqueo, incrementa y confirma la generación y
  rota la capacidad; cuando el worker anterior entra a T2b, su fence ya no coincide y
  falla antes de escribir;
- si el worker anterior obtiene primero el bloqueo en T2b con lease todavía vigente,
  el reclaimer no puede incrementar la generación hasta que T2b termine; el worker
  puede confirmar atómicamente y el reclaimer observará después el estado terminal.

La expiración observada fuera del bloqueo no concede revocación. Tampoco se mantiene
una transacción abierta para reservar el turno durante el LLM: la generación
confirmada, no la duración de una transacción ni el heartbeat, es el mecanismo de
fencing.

## Invariantes

- Ningún efecto originado en Telegram se ejecuta sin un recibo autenticado y una
  capacidad válida para la generación vigente.
- En 1B.1-A, cualquier efecto legacy sin interfaz que vuelva a resolver y validar la
  capacidad falla cerrado; las consultas conversacionales no producen efectos.
- La clave inbound es `(bot_scope, update_id)`; no depende de un UUID local nuevo, del
  texto interpretado ni de un ID elegido por el LLM.
- El recibo es inmutable. El identificador estable de despacho permanece privado para
  ingreso; capacidad, generación, estado de procesamiento, resultados y conflictos se
  guardan fuera del recibo y sólo cambian por interfaces acotadas.
- La capacidad se almacena sólo mediante su hash, rota en cada claim y no sobrevive
  como autoridad después de un incremento confirmado de generación.
- `leda_app` no puede insertar, actualizar, borrar ni enumerar recibos, capacidades o
  la cola privada de recuperación, ni aplicar parcialmente un plan por DML directo o
  funciones internas.
- Actor y espacio siempre se derivan dentro de la frontera; nunca se confía en los que
  declare el llamador.
- Poseer una capacidad no reemplaza la autorización: cada efecto revalida membresía,
  autoridad y estado vigente.
- Existe como máximo un hecho que cambie estado por `(receipt, task)`. Un mismo recibo
  puede afectar varias tareas distintas.
- Un `edited_message` nunca produce efectos operativos, aunque se conserve como
  historia. Todo cambio operativo posterior requiere un mensaje nuevo.
- Los retries devuelven el resultado o conflicto persistido; no generan un segundo
  efecto.
- `leda_gateway` continúa siendo el límite dedicado de Unidad 1A. Su única función
  superior deriva identidad del recibo y confirma tarea, auditoría, resultado, outbox y
  finalización condicional dentro de T2b.
- Los mensajes visibles continúan saliendo por outbox; el ACK técnico de Telegram
  permanece como excepción acotada.
- No existe una transacción abierta ni una conexión ociosa en transacción durante el
  LLM. Claim, heartbeat, aplicación y cada recuperación usan conexiones separadas.

## Idempotencia y recuperación

T1, T2a y T2b son transacciones separadas. T1 no queda abierta mientras se consulta al
LLM y no se revierte porque falle el procesamiento posterior. T2a sólo asigna el claim;
T2b confirma atómicamente sus escrituras y la finalización. El ledger distingue
`pending`, `interpreting` y estados terminales de resultado o conflicto; la
recuperación por identificador privado nunca concede a `leda_app` una consulta
general de recibos.

La deduplicación técnica del update no sustituye la idempotencia semántica del efecto.
La primera usa `(bot_scope, update_id)`; la segunda usa `(receipt, task)` y compara la
operación persistida. Una reentrega concurrente converge al mismo recibo. Dos intentos
concurrentes sobre la misma tarea y recibo convergen al mismo resultado o conflicto.

Las caídas y resultados inciertos se resuelven así:

- antes de confirmar T1 no existe recibo durable y Telegram puede reentregar;
- después de T1 y antes de T2a, el recibo `pending` permanece recuperable;
- después de T2a y antes de T2b, un claim abandonado sólo vuelve a ser elegible cuando
  vence el lease, y el reclaim confirmado incrementa la generación;
- durante el LLM no hay escrituras de dominio ni transacciones abiertas que recuperar;
- una excepción o caída antes del commit de T2b revierte todas sus escrituras;
- si el cliente no sabe si el commit de T2b ocurrió, no supone fallo ni vuelve a
  interpretar: consulta o reintenta por recibo y operación determinista. Encontrará el
  resultado terminal confirmado o podrá recuperar el trabajo no confirmado sin
  duplicar efectos;
- un fallo al recuperar un recibo se captura para ese recibo y no impide intentar los
  demás.

## Políticas de edición y multiplicidad

Telegram puede entregar `edited_message`. Leda puede retenerlo para trazabilidad o
como corrección visible, pero no lo interpreta como autorización para modificar un
efecto anterior ni para crear uno nuevo. La respuesta debe indicar que el usuario
envíe un mensaje nuevo si desea producir un cambio operativo.

Un mensaje nuevo puede informar un hecho para cada una de varias tareas. En cambio,
si contiene una secuencia como iniciar y entregar la misma tarea, Leda debe pedir
aclaración porque una sola interpretación estaría eligiendo orden y estados
intermedios. La regla no impide procesar hechos inequívocos de otras tareas del mismo
recibo, pero cada resultado debe quedar identificado y ser recuperable por tarea.

## Alternativas rechazadas

- **Confiar en actor, espacio o update aportados por la aplicación:** rechazado porque
  una herramienta, el LLM o SQL bajo `leda_app` podrían suplantarlos.
- **Identidad de sesión mediante GUC, `SET LOCAL` o un rol compartido:** rechazado
  porque el propio llamador puede forjar ese estado de sesión. No constituye una raíz
  de confianza.
- **Compartir un login con membresía en varios roles sensibles:** rechazado porque un
  compromiso permite asumir la frontera que debía contenerlo.
- **Firmar el contexto con HMAC:** criptográficamente válido, pero rechazado para esta
  etapa por gestión de claves, rotación y complejidad innecesarias frente a una
  capacidad opaca resuelta en PostgreSQL.
- **Permitir que `leda_app` administre o liste recibos:** rechazado porque ampliaría
  el radio de una credencial comprometida y permitiría seleccionar identidades.
- **Procesar T1, LLM y todos los efectos en una única transacción:** rechazado porque
  mantiene una transacción abierta durante trabajo no determinista y pierde el punto
  durable de recuperación del update.
- **Usar el lease o heartbeat como fence:** rechazado porque la expiración por sí sola
  no impide que un worker anterior confirme. La revocación exige incrementar y
  confirmar la generación bajo el mismo bloqueo que usa T2b.
- **Finalizar el claim en una llamada posterior al efecto:** rechazado porque una caída
  o un caller comprometido podría confirmar efectos sin cerrar el procesamiento. La
  aplicación y la finalización condicional pertenecen a la misma función superior y
  transacción.
- **Aceptar efectos desde `edited_message`:** rechazado porque una edición puede
  reescribir retrospectivamente el origen de un efecto ya observado.
- **Agregar un microservicio o proceso de ingreso antes del piloto:** rechazado por no
  ser necesario para cerrar esta amenaza; las credenciales y transacciones separadas
  caben en el monolito actual.
- **Mantener opcional el secreto de webhook:** rechazado para el diseño objetivo. El
  secreto debe ser obligatorio, validarse al arrancar y corresponder al bot receptor.

## Implementación, migración y pruebas esperadas

Cuando se retome Unidad 1B.1, su primera porción implementable debe ejecutar en orden
los Cortes 0 a 4 y verificar la frontera sin introducir todavía hechos de tarea. El
Corte 5 gobierna la reapertura posterior de cada efecto en su unidad correspondiente.
El trabajo debe incluir:

- catálogo ejecutable del inventario estático, incluidas las 26 tablas directamente
  mutables, eventos con mutación indirecta, funciones, secuencias, `PUBLIC`, logins,
  membresías, owners, grants, superusuario y rutas que cargan credenciales, sin
  registrar secretos;
- cierre ordenado de las rutas legacy que permitan omitir recibo, capacidad o
  aplicación cercada, con las degradaciones temporales definidas en esta ADR;
- migración versionada para recibos inmutables, identificador privado de despacho,
  capacidad hasheada y rotatoria y ledger de procesamiento con generación monotónica,
  funciones superiores acotadas y privilegios disjuntos;
- adaptación de webhook y polling a T1/T2a/T2b, con secreto webhook obligatorio y
  específico del bot en el camino objetivo;
- adaptación de `leda_gateway` para consumir identidad derivada del recibo;
- incorporación de `leda_dispatcher` como única autoridad técnica de transporte de
  outbox, sin facultad sobre contenido, destinatarios, dominio o auditoría humana;
- retiro de grants o membresías que permitan a un login asumir más de una frontera;
- provisión separada y restaurable de logins `NOINHERIT` y owners no asumibles, con
  revokes explícitos y paridad comprobada entre instalación limpia y migración;
- arranque de serving y polling sin credencial administrativa;
- conservación del inbound histórico como legacy no autoritativo de sólo lectura, sin
  borrado, promoción, retry ni efectos.

Las pruebas deben ejecutarse contra PostgreSQL descartable confirmado e incluir:

- matriz negativa de cada login contra recibos, capacidades, gateways y funciones que
  no le corresponden, incluidos intentos de asumir roles sensibles;
- secreto ausente, incorrecto, de otro bot y correcto; aislamiento entre bots con el
  mismo `update_id`;
- reentrega secuencial y concurrente, colisión incompatible y caída después de T1;
- claims iniciales y concurrentes, incremento monotónico de generación, rotación y
  almacenamiento hasheado de capacidad, expiración y heartbeat que no revive un lease;
- carrera crítica A/B en ambos órdenes entre reclaim y T2b, demostrando que el worker
  obsoleto falla sin escribir o que el reclaimer espera al worker que bloqueó primero;
- fallos inyectados después de cada escritura de T2b, incluida la finalización,
  verificando rollback total;
- caída después de confirmar un efecto y antes de la respuesta, y commit ambiguo,
  seguidos de recuperación por resultado determinista sin duplicación;
- ausencia de conexión `idle in transaction` durante el LLM y separación de conexiones
  para claim, heartbeat, aplicación y recuperación;
- actor, espacio, update y estado de sesión forjados por `leda_app`;
- capacidad inválida y replay con operación igual o conflictiva;
- múltiples tareas en un recibo, dos cambios secuenciales para la misma tarea y
  solicitud de aclaración;
- `edited_message` retenido sin efecto y mensaje nuevo posterior con efecto único;
- Unidad 1A a través de la única T2b de `leda_gateway`, comprobando atomicidad de
  tarea, auditoría, resultado, outbox y finalización;
- `leda_dispatcher` limitado a reclamar outbox listo, registrar envío, reintento o
  fallo y abrir incidentes técnicos de transporte, con intentos negativos de cambiar
  contenido, destinatario, dominio y auditoría humana;
- separación entre conversación, auditoría autoritativa e incidentes técnicos, con
  intentos de `leda_app` de fabricar una acción humana auditada;
- inbound histórico legible como conversación y rechazado para promoción, retry o
  cualquier efecto;
- fallos de recuperación aislados por recibo, baseline completa y evidencia sanitizada
  de auditoría y outbox;
- avance y rollback de migración, paridad con instalación limpia, matriz efectiva de
  privilegios y ensayo representativo de provisión y restore en un clúster aislado.

No se declara implementada la frontera hasta registrar comando, resultado exacto,
escenario operativo, verificación de privilegios y límite de rollback.

## Rollback esperado

Antes de abrir escritores, el ensayo debe demostrar cómo retirar el enrutamiento nuevo,
funciones, grants, roles y credenciales sin otorgar a `leda_app` acceso directo a
recibos o efectos ni debilitar `leda_gateway`. La ruta de rollback debe conservar la
paridad entre migración e instalación limpia y distinguir objetos de base de roles de
clúster. Los recibos, resultados y auditoría ya persistidos se conservan para
diagnóstico; no se reescriben como inbound antiguo.

Si existen escrituras posteriores a la activación, no se restaura una base de forma
ciega. Se pausa el ingreso, se preservan T1 y sus resultados y se define una
reconciliación explícita. La credencial administrativa no se agrega temporalmente al
servicio como mecanismo de rollback.

## Consecuencias

- El MVP puede validar temprano circuitos simulados con guardas proporcionales sin
  presentar esta ADR como implementada ni aceptar trabajo real.
- El diferimiento termina antes del piloto real/VPS, según el control, o antes si la
  evidencia progresiva demuestra que el riesgo afecta al circuito actual.
- Unidad 1B.1 gana una raíz verificable para actor y espacio antes de ampliar efectos.
- Un compromiso de `leda_app`, del LLM o de una herramienta queda contenido por
  privilegios y capacidades, siempre que no exista compromiso total del proceso.
- El update puede confirmarse y recuperarse sin mantener una transacción abierta
  durante el procesamiento no determinista.
- Un worker reclamado queda cercado por generación antes de cualquier escritura de
  T2b; el lease sólo regula elegibilidad y disponibilidad.
- La operación requiere provisionar y rotar cinco credenciales técnicas realmente
  disjuntas, además de verificar membresías y owners.
- El flujo local sigue siendo un monolito, pero aumenta la disciplina de conexiones y
  transacciones.
- La Unidad 2 conserva el cierre integral de idempotencia inbound; esta ADR adelanta el
  recibo autenticado mínimo que 1B.1 necesita y no cambia la secuencia del roadmap.

## Riesgos residuales

- El compromiso total del proceso Python puede exponer varias credenciales mientras
  convivan en el mismo proceso.
- Una falla en el código de ingreso previo a T1 puede atribuir incorrectamente datos de
  Telegram; por eso su superficie debe ser mínima y probada.
- Las capacidades son secretos operativos: pueden filtrarse por logs, errores o
  telemetría si no se redactan.
- Un lease demasiado corto puede causar reclaim y trabajo de interpretación
  desperdiciado; uno demasiado largo demora recuperación. Este ajuste afecta
  disponibilidad, no la corrección del fence.
- Un commit ambiguo exige consultar el resultado determinista; reintentar la
  interpretación sin esa consulta puede desperdiciar trabajo aunque el efecto siga
  deduplicado.
- La recuperación y retención del ledger pueden crecer sin una política posterior de
  operación y limpieza segura.
- La separación lógica no demuestra por sí sola el aislamiento: grants, membresías,
  owners y rutas reales deben verificarse después de cada migración.
