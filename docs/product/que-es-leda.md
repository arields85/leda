# Qué es Leda

Leda es un project manager digital ofrecido como producto. Cada organización que lo
usa es un cliente independiente, con sus propios integrantes, áreas, políticas y
cadencias, y sin visibilidad alguna sobre los datos de otro cliente.

Este documento define el producto. La frontera técnica que lo sostiene está en
[`architecture/frontera.md`](../architecture/frontera.md); el orden de trabajo está en
[`ROADMAP.md`](../ROADMAP.md).

## Un espacio es un cliente

En el modelo de datos, un cliente se representa como un *espacio* (`workspace`). Todo
objetivo, tarea, integrante, política y mensaje pertenece a un espacio y no existe
fuera de él.

La configuración de cada cliente es dato, no código. Esa es la diferencia entre un
producto y una instalación a medida.

El paquete versionado es el **formato de transporte** de esa configuración, no su
fuente de verdad: lo produce la entrevista de alta, una exportación o el desarrollo,
y el importador lo consume una sola vez para sembrar el espacio. Desde ese momento la
base es la verdad operativa y el tablero del cliente la edita.

## Las cuatro superficies

Leda se atiende desde cuatro superficies distintas sobre el mismo núcleo.

| Superficie | Propósito | Estado |
|---|---|---|
| Conversacional | Interacción cotidiana: informar avances, pedir estado, resolver confirmaciones. Hoy sobre Telegram. | Existe |
| Tablero de cliente | Visión consolidada de objetivos, avance, cumplimiento, bloqueos y carga por persona, **y ajuste de la configuración propia**. | No existe; su credencial está en curso |
| Panel de plataforma | Alta de clientes y entrevista de alta de un espacio nuevo. | No existe |
| Aplicación móvil | Acceso rápido a lo propio y a las confirmaciones pendientes. | No existe |

Hoy sólo existe la primera. La superficie HTTP del sistema se limita a dos rutas:
`POST /telegram/{slug}` y `GET /salud` (`src/leda/gateway.py:47,434`).

El puerto de lectura sí existe (`src/leda/lectura.py`): las consultas agregadas
están, lo que falta es la superficie que las muestre.

**Las dos superficies web son aplicaciones separadas, no una con niveles de
permiso.** El tablero de cliente alcanza un solo espacio; el panel de plataforma los
alcanza todos, y por eso no puede convivir con el otro a un error de autorización de
distancia. El razonamiento completo está en
[`ADR 0004`](../decisions/0004-dos-superficies-separadas.md).

## Qué hace Leda

- Convierte objetivos aprobados en trabajo con responsable, fecha objetivo, criterio
  de aceptación y política de evidencia.
- Hace el seguimiento cotidiano para que no recaiga en una persona.
- Solicita avances, evidencias y explicaciones según las reglas del cliente.
- Detecta bloqueos y dependencias entre áreas, y propone caminos.
- Escala atrasos y silencios siguiendo las rutas configuradas, empezando en privado.
- Prepara informes periódicos y material de reunión.
- Registra decisiones, aprobaciones y cambios de forma auditable.

## Qué no hace Leda

- No decide prioridades: las propone y las registra, pero la decisión es humana.
- No aprueba en nombre de nadie ni da por aprobado lo que requiere validación.
- No toma decisiones técnicas que pertenecen a los referentes del cliente.
- No opera sistemas productivos, industriales ni de infraestructura del cliente.
- No inventa fechas, aprobaciones, evidencias ni avances. Cuando falta un dato, lo
  pide.
- No amplía su propia autoridad. Toda ampliación es explícita y queda registrada.

## Configuración del cliente y núcleo del producto

Esta separación es la que hace que Leda sea un producto y no una implementación
para un equipo. Lo que está a la izquierda cambia con cada cliente; lo que está a la
derecha es el producto y no se negocia por cliente.

| Configuración por cliente | Núcleo del producto |
|---|---|
| Áreas de trabajo | Jerarquía objetivo, hito, objetivo operativo, tarea |
| Roles y niveles de autoridad | Conjunto de estados de tarea y sus transiciones válidas |
| Integrantes y membresías | Modelo de autoridad y revalidación en la frontera |
| Políticas de aprobación por tipo de trabajo | Ciclo de seguimiento y escalera de recordatorios |
| Políticas de evidencia exigible | Registro de evidencias y aprobaciones |
| Cadencias, horarios y días laborales | Auditoría de decisiones y cambios |
| Calendario laboral y ausencias | Aislamiento entre clientes |
| Glosario y vocabulario propio | Modelo de borrador y compromiso de tarea |
| Rutas de escalamiento | Contrato de salida y deduplicación de mensajes |
| Objetivo inicial y prioridades | Portabilidad y exportación de los datos |

Esta separación ya está sostenida por el esquema, no sólo por intención: `area` y
`rol` son tablas con `workspace_id` (`db/esquema.sql:106,114`), no tipos enumerados.
Los tipos enumerados del esquema contienen únicamente vocabulario genérico de gestión
de proyectos. En `src/`, el vocabulario de un cliente concreto aparece sólo en
comentarios y en ejemplos de la ayuda de consola; no hay ninguna dependencia
funcional.

La consecuencia práctica: incorporar un segundo cliente no exige modificar el
esquema.

Dónde se edita cada columna: lo de la izquierda entra por la entrevista de alta y
después se ajusta desde el tablero del cliente, con cada cambio atribuido en la
auditoría. Lo de la derecha no se edita desde ninguna superficie: cambia con el
producto.

## Principios invariantes

1. Las personas deciden; Leda organiza, propone y hace seguimiento.
2. La decisión final pertenece a quien el cliente designe como dirección.
3. La autoridad técnica pertenece a los referentes que el cliente configure.
4. Una parte terminada no equivale a un objetivo integral terminado.
5. Toda tarea relevante tiene responsable, fecha, criterio de aceptación y evidencia.
6. Los atrasos se tratan primero en privado; la exposición grupal es el último
   recurso y siempre factual.
7. El seguimiento existe para facilitar el trabajo, no para vigilar personas.
8. La memoria operativa es estructurada, auditable y portable.
9. Leda nunca opera los sistemas productivos del cliente.
10. El aislamiento entre clientes es una garantía del producto, no una configuración.

## CoreWork como primer cliente

CoreWork es el primer cliente de Leda, no su definición. Su paquete vive en
[`espacios/corework.yaml`](../../espacios/corework.yaml) y entra por el mismo
importador que usará cualquier otro cliente.

Con una diferencia que conviene no olvidar: ese paquete se escribió a mano, porque
quien lo escribió conocía al equipo. Un cliente nuevo no tiene a nadie que pueda
hacer eso, y por eso la entrevista de alta —hoy diseñada en
[`nucleo/alta-de-equipo.md`](../../nucleo/alta-de-equipo.md) y sin implementar— es lo
que separa a Leda de ser una instalación a medida.

El documento maestro de CoreWork pasa a ser **insumo de configuración de ese
cliente**: describe sus integrantes, su autoridad, sus cadencias y su objetivo anual.
No define el alcance del producto ni gobierna decisiones de arquitectura.

Cuando un requisito aparezca en el documento de un cliente, la pregunta previa a
implementarlo es siempre la misma: ¿es configuración de ese cliente o es núcleo del
producto? La tabla anterior es el criterio.
