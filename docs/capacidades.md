# Qué está construido y qué no

Para entender en cinco minutos dónde está parado el proyecto, sin volver a
auditarlo. El detalle vive en los documentos que se citan; acá está el mapa.

## El hallazgo de fondo

El esquema y los documentos describen un producto cerca del doble del código,
y la brecha no es al azar: está sistemáticamente de un lado. Lo construido es
**el registro** —capturar trabajo, aislarlo, entregar mensajes— y ahora
también las dependencias entre tareas. Lo ausente sigue siendo el resto de
**la coordinación** —subtareas, prioridad, reuniones, informes, calendario,
correo, umbral de re-aprobación—, que es justamente la misión del §2: reducir
"dependencias invisibles" y "reuniones dedicadas únicamente a recopilar
estado".

Prisma hoy es un registro de tareas bien construido con interfaz de Telegram.

## Construido y sólido

No se rehace.

| Capacidad | Evidencia |
|---|---|
| Aislamiento entre clientes | Migraciones `0003`–`0005`; regla 1 de [`frontera.md`](architecture/frontera.md) cumplida |
| Estado como proyección de eventos | `bloquear_estado_directo()`; `task.estado` no es editable |
| Reglas de cierre aplicadas en la base | `motivo_no_cierra_tarea()`, `motivo_no_cierra_objetivo()` |
| Alta de tarea propiedad del servidor | `ingreso_tareas.py`: lineage, opciones atómicas, vista previa |
| Router de intención tipado | `llm.py`: un validador cerrado para cuatro proveedores |
| Contrato único de salida | `salida.py`: normalización, medición UTF-16, división |
| Escalera de recordatorios | `escalera.py`: cinco pasos en días hábiles, respeta ausencias |
| Ciclo de vida de un bloqueo | `resolver_bloqueo` cierra y devuelve la tarea al estado previo a `bloqueada`; un bloqueo abierto hace más de `bloqueos.escala_solo_a_los_dias` días hábiles escala solo por la ruta transversal del pack |
| Despacho idempotente | `dedupe_key`, reintento con incidente, respeta jornada |
| Puerto de lectura | `lectura.py`: seis consultas agregadas, el espacio sale de la sesión |
| Tablero de cliente | Credencial por enlace con vencimiento + pantalla |
| Importador de paquetes | Genérico, con validaciones cruzadas y hash versionado |
| Banco conversacional con modelo real | `tests/banco/`: escenarios ficticios en YAML corridos N veces por `gateway.procesar_update` con el proveedor real; comprueba herramientas, acciones afirmadas sin herramienta, personas fuera del equipo, efectos en PostgreSQL y contenido de la respuesta. Fuera de la suite por defecto (`-m modelo_real`); las fallas se guardan para replay |
| Dependencias entre tareas | `crear_dependencia`/`quitar_dependencia` (`herramientas.py`), autoridad del responsable de cualquiera de las dos o su referente; freno de `en_curso` en la base (`motivo_no_arranca_tarea`, migración `0008`); aviso en cadena por atraso o por fecha corrida (`escalera.evaluar_dependencias_en_riesgo`) y aviso de la informativa al cambiar de estado |

## Diseñado y sin construir

Cada uno tiene diseño escrito y cero código.

| Área | Lo manda | Estado |
|---|---|---|
| **Entrevista de alta de espacios** | [`nucleo/alta-de-equipo.md`](../nucleo/alta-de-equipo.md), 195 líneas | Sin una sola línea. Sólo existe el importador, que consume un paquete ya escrito. Sin esto, cada cliente nuevo exige que alguien lo escriba a mano |
| **Panel de plataforma** | [`ADR 0004`](decisions/0004-dos-superficies-separadas.md) | Decidido: contraseña + TOTP. Sin construir |
| **Integración de calendario** | Especificación §17.3, constitución §7 | Consultar disponibilidad, proponer, crear, modificar, asistentes. `calendario.py` es el calendario **laboral**, no externo |
| **Correo** | Especificación §18 | Sólo existe el nombre del permiso |
| **Almacenamiento documental** | Especificación §11 | `evidence.drive_file_id` sin uso |
| **Reuniones e informes** | Especificación §17.2 y §23 | Anunciar, pedir temas, consolidar, agenda, minutas. `corework.yaml` declara `reunion_periodica` y el importador no la consume |
| **Conversación de bloqueos** | Mecánica §8, pasos 2 a 7 | Abrir y cerrar un bloqueo ya funciona. Pedir la información mínima, proponer soluciones, preguntar por ayuda y proponer reasignaciones siguen sin construir. Su precondición —dependencias entre tareas— ya está resuelta; es la unidad siguiente en `docs/ROADMAP.md` |
| **Umbral de re-aprobación** | Mecánica §7 | El importador lo guarda en la base y ningún código lo lee |
| **Privacidad configurable** | Especificación §19 | Sin código **ni** esquema. No existe matriz de visibilidad |
| **Aprendizaje** | Mecánica §14 | Tabla `learning` vacía de uso |
| **Bot de administración** | Constitución §2 | Cascarón: identifica, audita y devuelve `ok` |
| **Atribución de mensajes** | Constitución §7 | Preguntar en nombre de quién va un mensaje. Sólo hay un comentario |

## Trampas conocidas

Verificadas. Cada una engaña a quien la lea.

**Un comentario que miente.** `despachador.py:390` afirma que el tope de
contacto es por persona y no por espacio. El SQL hace el join correcto por
`app_user_id`, pero corre bajo `espacio()` y la RLS confina las tablas al
espacio actual: **el join no puede cruzar**. Quien esté en tres equipos recibe
el triple, y el comentario garantiza que nadie lo revise. Lo exige la mecánica
§10.

**El router de intención no ve las tareas que ya existen.** `route_intent`
recibe sólo el texto del mensaje (`llm.ROUTER_SYSTEM`), no las tareas del
espacio. "El cableado del tablero no puede arrancar hasta que yo termine de
programar el PLC, dejalo anotado" —dos tareas ya cargadas— se clasificó como
pedido de tarea nueva en 10 de 10 corridas del banco (escenario `b-0005`,
2026-09-23, NaN `deepseek-v4-flash`): abre el alta guiada y la dependencia nunca
se crea. Un replay guionado no sirve de regresión, porque repite la
clasificación grabada; la regresión es el escenario contra el modelo real.

**`cli.py` no tiene ninguna prueba.** 403 líneas y trece comandos operativos
—`esquema`, `importar`, `despachar`, `escuchar`, `servir`—: lo que se usa para
operar Prisma de verdad.

**El puerto de lectura no lista tareas.** Sus seis consultas son agregadas, y
las únicas que nombran tareas son vencidas, bloqueadas y esperando aprobación.
Una tarea asignada sin fecha no aparece en ninguna parte del tablero.

## Capacidades construidas que ningún documento describe

Conocimiento que sólo vive en el código: la detección de ambigüedad de nombres
(`contexto.py`), las validaciones cruzadas del importador —cadencia en día no
laboral, volumen de contacto contra el tope, exigencia de suplente— y el
rechazo del token de bot dentro del paquete, porque el paquete se versiona en
git.

## Esquema sin implementación

El inventario **no está acá a propósito**: vive en `tests/test_capacidades.py`,
ejecutable. Dos listas de lo mismo divergen; una prueba no puede pudrirse.

Esa prueba funciona en los dos sentidos. Si alguien implementa una de esas
capacidades, falla y pide que se saque de la lista. Si alguien agrega esquema
nuevo que nadie usa, falla y obliga a decidir si es deuda aceptada o un olvido.

## Vigencia

Levantado el 2026-09-22 auditando `nucleo/`, la especificación funcional y el
código completo. Todo lo de arriba es una foto y envejece; la única parte que
se mantiene sola es la prueba.
