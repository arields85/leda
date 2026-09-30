# Continuidad de trabajo en Prisma

Este archivo es el punto de entrada para futuras sesiones. Prisma se endurece y
extiende sobre la arquitectura actual; no se reestructura ni reescribe sin una
decisión explícita y documentada.

> **Este archivo es la fuente única de estas instrucciones.** `CLAUDE.md`
> contiene sólo `@AGENTS.md`, que las importa. Claude Code lee `AGENTS.md` de
> forma nativa, pero esa lectura depende de un indicador remoto y no se activa
> en Bedrock o Vertex, con telemetría deshabilitada, ni en la primera sesión
> posterior a una instalación o actualización; la importación funciona siempre.
> Editar siempre este archivo, nunca `CLAUDE.md`.

## Orden de lectura

1. Leer `docs/product/que-es-prisma.md` para conocer qué es el producto y qué es
   configuración de cada cliente.
2. Leer `docs/architecture/frontera.md` para conocer dónde termina el núcleo y qué
   reglas lo gobiernan.
3. Leer `nucleo/`: `constitucion.md`, `mecanica-pm.md` y `alta-de-equipo.md`.
   Son el comportamiento **obligatorio** de Prisma, no material de consulta.
   Una auditoría que no los lea no es una auditoría del proyecto.
4. Leer `docs/capacidades.md` para saber qué está construido, qué está
   diseñado sin construir y qué es esquema sin implementación.
5. Leer `docs/STATUS.md` para conocer estado, riesgos y próximo paso.
6. Leer `docs/ROADMAP.md` para conocer el orden de trabajo vigente.
7. Leer `docs/INDEX.md` para elegir sólo el detalle necesario.
8. Leer los ADR aplicables antes de cambiar dominio o arquitectura.
9. Contrastar cualquier afirmación con código, esquema y pruebas actuales.

**Al auditar, auditar contra este repositorio.** El corpus propio del proyecto
—`nucleo/`, la especificación funcional, el esquema, los paquetes de espacio—
es la fuente. Un documento externo sirve como insumo, nunca como el patrón
contra el cual medir: medir contra él deja fuera todo lo que el proyecto ya
decidió y nadie volvió a leer.

No leer archivos `.env*`, salvo `.env.ejemplo` cuando sea necesario revisar la
plantilla pública. Nunca mostrar secretos, tokens, credenciales, URLs privadas ni
contenido sensible de conversaciones.

## Fuentes de verdad

Orden de autoridad para describir lo que existe hoy:

1. `db/esquema.sql` y `src/prisma/`: comportamiento implementado.
2. `tests/` y `db/pruebas.sql`: comportamiento comprobado por pruebas, sólo si la
   ejecución y su resultado están registrados.
3. `docs/architecture/frontera.md`: gobierna la arquitectura. Ante una discrepancia
   entre documentos de arquitectura, prevalece esta frontera.
4. `docs/product/que-es-prisma.md`: define el producto y qué es configuración de cada
   cliente frente a núcleo.
5. `docs/decisions/`: decisiones aceptadas que gobiernan cambios futuros, salvo las
   marcadas como superadas.
6. `docs/STATUS.md` y `docs/ROADMAP.md`: estado y orden de trabajo vigentes.
7. `README.md` y `PRUEBA-LOCAL.md`: guía operativa; contrastar con la
   implementación si hay discrepancias.

`nucleo/` no es material de consulta: es el comportamiento obligatorio. Su
autoridad está por encima de cualquier documento de `docs/`, y una auditoría
de este proyecto que no lo haya leído entero no está terminada. Buena parte de
lo que manda todavía no tiene código; `docs/capacidades.md` lleva la cuenta.

`docs/product/functional-specification.md` quedó superada por el cambio de alcance a
producto multi-tenant. Se conserva como insumo histórico y no describe el alcance
vigente; contrastarla contra la frontera antes de usar cualquier parte.

Una especificación expresa intención, no prueba implementación. Un test existente
no prueba que la suite pase hasta ejecutarlo.

## Invariantes vigentes

- El aislamiento entre clientes es la garantía número uno del producto. Ninguna tabla
  con alcance de espacio queda sin `workspace_id` ni sin `row level security` forzado,
  y ninguna función `security definer` queda sin propietario explícito y verificado.
- PostgreSQL es la fuente oficial del estado operativo.
- La conversación y la memoria ayudan a interpretar; no reemplazan una lectura
  vigente ni conceden autoridad.
- El modelo sólo actúa mediante herramientas autorizadas del servidor.
- Los efectos relevantes requieren validación, confirmación cuando corresponda,
  ejecución única, verificación y auditoría.
- El aislamiento entre espacios no debe depender de recordar un filtro manual.
- Los mensajes visibles salen por outbox; el ACK técnico de Telegram es la
  excepción acotada existente.
- Una solicitud incompleta es un borrador sin efectos.
- Una tarea comprometida exige objetivo, responsable, fecha objetivo, criterio de
  aceptación y política de evidencia.
- La conversión de borrador a tarea es explícita, confirmada y auditable.
- Actualización, evidencia, aprobación y cierre son hechos distintos.
- No poder consultar datos no equivale a que no existan.

## Límites de alcance

El producto conserva un monolito modular en Python y PostgreSQL.

Fuera del producto por ahora. No construir sin una decisión explícita y documentada:

- agenda o calendarios externos;
- aprendizaje persistente;
- motor genérico de workflows;
- microservicios;
- interfaz administrativa completa.

Dentro del producto pero todavía no: la API de lectura y el dashboard pertenecen al
producto y están ordenados en `docs/ROADMAP.md`. No se construyen todavía porque
tienen precondiciones —cierre del aislamiento entre clientes y desacople del
transporte—, no porque estén fuera de alcance. Aplicar el orden del roadmap, no
tratarlos como prohibidos.

No cambiar lógica, esquema, dependencias o arquitectura durante trabajo puramente
documental. No reestructurar carpetas o módulos sin un ADR aceptado.

## Comandos verificados por inspección

Estos comandos existen en `README.md`, `PRUEBA-LOCAL.md`, `pyproject.toml` o
`src/prisma/cli.py`. Su disponibilidad fue inspeccionada; su resultado actual no
se presume.

```bash
docker compose up -d postgres
python -m prisma esquema
python -m prisma importar corework
python -m prisma importar corework --activar
python -m prisma feriados corework
python -m prisma enlaces corework --solo <nombres>
python -m prisma administrador corework <nombre>
python -m prisma escuchar corework
python -m prisma escuchar corework --sin-cadencias
python -m prisma estado corework
python -m prisma correr corework <cadencia>
python -m prisma escalera corework
python -m prisma despachar corework
python -m prisma incidentes corework
python -m prisma servir --puerto 8080
python -m prisma servir --puerto 8080 --sin-cadencias
python -m pytest
```

`python -m prisma esquema --recrear` borra los datos. No ejecutarlo sin una
autorización explícita y un entorno descartable confirmado.

## Reglas de seguridad

- No leer, imprimir, versionar ni incluir en diagnósticos archivos `.env*`, salvo
  la plantilla permitida `.env.ejemplo`.
- No inspeccionar untracked antes de asegurar las exclusiones sensibles en
  `.gitignore`.
- No ejecutar SQL destructivo, pruebas contra una base no confirmada como
  descartable ni comandos de despliegue sin autorización.
- No registrar cuerpos de conversaciones ni errores crudos en documentación.
- No afirmar que una prueba, restore, backup o rollback funciona sin evidencia de
  una ejecución registrada.
- No hacer commits, cambiar configuración Git o agregar archivos al índice salvo
  pedido explícito.

## Cómo trabajar y registrar continuidad

Antes de implementar una fase:

1. Confirmar que `docs/STATUS.md` sigue vigente contra el repositorio.
2. Elegir el menor circuito útil de extremo a extremo que pruebe comprensión,
   respuesta, coordinación o reducción de carga humana.
3. Resolver sólo las decisiones y guardas que bloquean ese circuito; no adelantar
   hardening de producción sin evidencia.
4. Mantener comportamiento, verificación focalizada, replay/regresión y documentación
   de esa unidad juntos.
5. Registrar comando, resultado exacto, escenario operativo y límite de rollback.

**Hallazgos de conversación: reglas generales, no parches**
([`ADR 0013`](docs/decisions/0013-reglas-generales-de-la-conversacion.md), decisión del
usuario del 2026-09-29). Las variantes de una conversación son infinitas; arreglar cada
caso con listas de frases o palabras clave no termina nunca. Ante un hallazgo sobre cómo
conversa Prisma:

- Clasificarlo primero en una de las reglas del ADR 0013: pregunta pendiente como
  contexto (comandos cerrados; una sola rama de conversación abierta a la vez, enmienda
  del 2026-09-29), una respuesta visible por mensaje, estado real y sólo
  opciones posibles, toque con señal e idempotente.
- Corregir el mecanismo de esa regla y probarlo con el caso y con familias de variantes,
  no sólo con la frase observada.
- Si no entra en ninguna regla, discutir con el usuario una regla nueva antes de
  parchear.
- Reparto de trabajo: el modelo interpreta el lenguaje y devuelve un comando de una lista
  cerrada; el código ejecuta un manejo determinista por comando y garantiza las
  invariantes. Es el patrón probado de los asistentes de tareas ("conversation repair
  patterns", por ejemplo en Rasa), adoptado dentro del monolito, no como dependencia.

**Lecciones de trabajo (2026-09-30, al cerrar la ronda 4).** Vigentes para toda sesión:

- **Probar en real enseguida** (decisión del usuario). Construir la porción más chica
  que se pueda probar y llevarla a Telegram real con datos ficticios cuanto antes. Todo
  plan nombra primero su prueba real más temprana y recorta el alcance para llegar a
  ella. La documentación registra decisiones, no ensayos; las mediciones baratas (banco,
  repeticiones) corren en paralelo con la construcción. Diseñar mucho sin probar costó
  horas.
- **Lo sólido no se simplifica.** La base, el aislamiento entre clientes, las
  confirmaciones y la auditoría funcionan. Ninguna propuesta de "simplificar" (un
  framework de agente, un modelo con SQL libre, reglas en el prompt en vez de
  garantías) reemplaza esas garantías: las instrucciones gobiernan el comportamiento;
  el código y la base, lo que no puede pasar nunca
  ([`ADR 0014`](docs/decisions/0014-flujo-de-un-mensaje.md), alternativas).
- **El problema de la conversación es dónde participa el modelo, no la falta de
  reglas.** Un camino pasa al flujo del ADR 0014 sólo cuando se retiraron sus
  mecanismos viejos; si conviven, no está terminado y el sistema queda peor.
- **Separar modelo de flujo.** Antes de atribuir una falla de comprensión al flujo,
  saber cuánto aporta el modelo: Prisma usa un modelo "flash" chico, elegido por
  velocidad. Medirlo con el banco es barato.
- **La superficie crece más rápido de lo que se estabiliza.** Cada ronda prueba
  funcionalidad nueva, y por eso los hallazgos no bajan. Decisión del usuario: la
  funcionalidad nueva queda congelada hasta que el núcleo de la conversación (alta,
  entrega, aprobación) cumpla en una prueba real los criterios del ADR 0014. Alcance
  en `docs/ROADMAP.md`, "Orden de entrega". No construir funcionalidad nueva mientras
  rija, aunque se pida de pasada: anotarla en el roadmap y recordar el congelamiento.
- **Ningún proyecto externo resuelve esto listo para usar.** Un PM conversacional
  multi-cliente con garantías es un problema propio. Relevar proyectos externos para
  tomar ideas, no bases ([`docs/research/`](docs/research/)).

Al terminar una unidad:

- actualizar `docs/STATUS.md` con hechos comprobados, riesgos y próximo paso;
- marcar una prueba como ejecutada sólo con comando, fecha y resultado;
- después de la verificación técnica, evaluar el gate de sesión progresiva del
  protocolo canónico; si el circuito es elegible, programar su prueba por Telegram
  real con datos ficticios sin esperar a completar las Fases 1-4; si no lo es, usar
  harness determinista o `TestClient` y registrar la condición pendiente;
- comprobar como mínimo workspace local o de prueba controlado, ausencia de datos y
  trabajo real, secreto de Telegram protegido, efectos inspeccionables y reversibles,
  backup, pausa o rollback proporcionado, ninguna operación destructiva y cero
  `CRITICAL` o `HIGH` abiertos en el circuito;
- inspeccionar respuesta visible, PostgreSQL, herramientas/efectos y
  auditoría/historia; corregir la causa raíz observada y agregar replay/regresión antes
  de reanudar;
- si el comportamiento es aceptable, elegir el siguiente circuito pequeño y endurecer
  proporcionalmente según evidencia;
- actualizar `docs/ROADMAP.md` sólo si cambió la secuencia o el criterio de salida;
- crear un ADR numerado para decisiones de dominio o arquitectura duraderas;
- no borrar decisiones anteriores: registrar si una nueva las reemplaza.

La sesión progresiva aporta evidencia de desarrollo y regresión, pero no aprueba el
piloto ni usa el holdout. Registrar su resultado en continuidad sólo cuando cambie un
hecho relevante; no editar documentación únicamente para dejar constancia de que se
evaluó el gate.

ADR 0003 quedó superada por el cambio de alcance a producto multi-tenant y está
marcada como tal. Su modelo de amenaza fue escrito cuando la amenaza principal era el
compromiso de la credencial de aplicación dentro de un solo equipo; en un producto
multi-tenant la amenaza principal es el cruce entre clientes. No se borra ni se
implementa en su secuencia original.

Su Corte 0 —el catálogo ejecutable de propietarios, membresías, grants y ACL— deja de
estar diferido: es insumo urgente de la unidad de cierre del aislamiento entre
clientes de `docs/ROADMAP.md`, porque es el control que habría detectado que las
tablas de eventos de estado reciben `grant insert` sin `workspace_id` ni RLS. Los
controles avanzados de privacidad y producción permanecen en el horizonte posterior
del roadmap.

Antes de cerrar una sesión, y después de su última modificación, operación o commit,
contrastar `docs/STATUS.md` y los documentos de continuidad afectados con el estado
actual de Git, código, esquema, pruebas y operación. Si cambió un hecho relevante,
actualizar los documentos correspondientes antes del cierre; si no cambió, no editar
documentación sólo para registrar la sesión.

Usar `PENDIENTE` para datos aún no comprobados o decisiones abiertas. No convertir
hipótesis, recomendaciones ni contenido del roadmap en estado implementado.
