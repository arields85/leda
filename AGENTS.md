# Continuidad de trabajo en Leda

Este archivo es el punto de entrada para futuras sesiones. Leda se endurece y extiende sobre la arquitectura
actual; no se reestructura ni reescribe sin una decisión explícita y documentada. Versión previa, sin condensar:
[`docs/historial/AGENTS-hasta-2026-09-30.md`](docs/historial/AGENTS-hasta-2026-09-30.md).

> **Este archivo es la fuente única de estas instrucciones.** `CLAUDE.md`
> contiene sólo `@AGENTS.md`, que las importa. Claude Code lee `AGENTS.md` de
> forma nativa, pero esa lectura depende de un indicador remoto y no se activa
> en Bedrock o Vertex, con telemetría deshabilitada, ni en la primera sesión
> posterior a una instalación o actualización; la importación funciona siempre.
> Editar siempre este archivo, nunca `CLAUDE.md`.

## Lectura obligatoria al iniciar cada sesión

Pedido del usuario (2026-10-02): toda sesión nueva arranca conociendo el estado y el
núcleo, sin que haya que pedírselo. Que figuraran en el orden de lectura no alcanzaba;
por eso se importan, y Claude Code los carga al iniciar la sesión:

@docs/STATUS.md
@nucleo/constitucion.md
@nucleo/mecanica-pm.md
@nucleo/alta-de-equipo.md

Un agente que no expanda estas importaciones (otra herramienta que lea `AGENTS.md`)
tiene que leer esos cuatro archivos enteros antes de su primera respuesta.

## Orden de lectura

1. `docs/product/que-es-leda.md`: qué es el producto y qué es configuración de cada cliente.
2. `docs/architecture/frontera.md`: dónde termina el núcleo y qué reglas lo gobiernan.
3. `nucleo/` (`constitucion.md`, `mecanica-pm.md`, `alta-de-equipo.md`): comportamiento **obligatorio** de Leda,
   no material de consulta. Una auditoría que no lo haya leído entero no está terminada.
4. `docs/capacidades.md`: qué está construido, qué está diseñado sin construir y qué es esquema sin implementación.
5. `docs/STATUS.md`: estado, riesgos y próximo paso.
6. `docs/ROADMAP.md`: orden de trabajo vigente.
7. `docs/INDEX.md`: elegir sólo el detalle necesario (`docs/historial/` guarda copias literales de documentos
   condensados; no es lectura de arranque).
8. Los ADR aplicables antes de cambiar dominio o arquitectura.
9. Contrastar cualquier afirmación con código, esquema y pruebas actuales.

**Al auditar, auditar contra este repositorio.** El corpus propio del proyecto
—`nucleo/`, la especificación funcional, el esquema, los paquetes de espacio—
es la fuente. Un documento externo sirve como insumo, nunca como el patrón
contra el cual medir: medir contra él deja fuera todo lo que el proyecto ya
decidió y nadie volvió a leer.

No leer archivos `.env*`, salvo `.env.ejemplo` cuando sea necesario revisar la plantilla pública. Nunca mostrar
secretos, tokens, credenciales, URLs privadas ni contenido sensible de conversaciones.

## Fuentes de verdad

Orden de autoridad para describir lo que existe hoy:

1. `db/esquema.sql` y `src/leda/`: comportamiento implementado.
2. `tests/` y `db/pruebas.sql`: comportamiento comprobado, sólo si la ejecución y su resultado están registrados.
3. `docs/architecture/frontera.md`: gobierna la arquitectura; ante una discrepancia entre documentos de
   arquitectura, prevalece.
4. `docs/product/que-es-leda.md`: define el producto y qué es configuración de cada cliente frente a núcleo.
5. `docs/decisions/`: decisiones aceptadas que gobiernan cambios futuros, salvo las marcadas como superadas.
6. `docs/STATUS.md` y `docs/ROADMAP.md`: estado y orden de trabajo vigentes.
7. `README.md` y `PRUEBA-LOCAL.md`: guía operativa; contrastar con la implementación si hay discrepancias.

La autoridad de `nucleo/` está por encima de cualquier documento de `docs/`. Buena parte de lo que manda todavía
no tiene código; `docs/capacidades.md` lleva la cuenta. `docs/product/functional-specification.md` quedó superada
por el cambio de alcance a producto multi-tenant: es insumo histórico, contrastarla contra la frontera antes de
usar cualquier parte. Una especificación expresa intención, no prueba implementación; un test existente no prueba
que la suite pase hasta ejecutarlo.

## Invariantes vigentes

- El aislamiento entre clientes es la garantía número uno del producto. Ninguna tabla con alcance de espacio queda
  sin `workspace_id` ni sin `row level security` forzado, y ninguna función `security definer` queda sin propietario
  explícito y verificado. No debe depender de recordar un filtro manual.
- PostgreSQL es la fuente oficial del estado operativo.
- La conversación y la memoria ayudan a interpretar; no reemplazan una lectura vigente ni conceden autoridad.
- El modelo sólo actúa mediante herramientas autorizadas del servidor.
- Los efectos relevantes requieren validación, confirmación cuando corresponda, ejecución única, verificación y
  auditoría.
- Los mensajes visibles salen por outbox; el ACK técnico de Telegram es la excepción acotada existente.
- Una solicitud incompleta es un borrador sin efectos. Una tarea comprometida exige objetivo, responsable, fecha
  objetivo, criterio de aceptación y política de evidencia. La conversión de borrador a tarea es explícita,
  confirmada y auditable.
- Actualización, evidencia, aprobación y cierre son hechos distintos.
- No poder consultar datos no equivale a que no existan.

## Límites de alcance

El producto conserva un monolito modular en Python y PostgreSQL. Fuera del producto por ahora; no construir sin una
decisión explícita y documentada: agenda o calendarios externos, aprendizaje persistente, motor genérico de
workflows, microservicios e interfaz administrativa completa.

Dentro del producto pero todavía no: la API de lectura y el dashboard, por sus precondiciones (cierre del
aislamiento entre clientes y desacople del transporte). Aplicar el orden del roadmap, no tratarlos como
prohibidos. La funcionalidad nueva está congelada ("Cómo pensamos juntos", punto 9).

No cambiar lógica, esquema, dependencias o arquitectura durante trabajo puramente documental. No reestructurar
carpetas o módulos sin un ADR aceptado.

## Comandos verificados por inspección

Existen en `README.md`, `PRUEBA-LOCAL.md`, `pyproject.toml` o `src/leda/cli.py`. Su disponibilidad fue
inspeccionada; su resultado actual no se presume.

```bash
docker compose up -d postgres
python -m leda esquema
python -m leda importar corework [--activar]
python -m leda feriados corework
python -m leda enlaces corework --solo <nombres>
python -m leda administrador corework <nombre>
python -m leda escuchar corework [--sin-cadencias]
python -m leda estado corework
python -m leda correr corework <cadencia>
python -m leda escalera corework
python -m leda despachar corework
python -m leda incidentes corework
python -m leda servir --puerto 8080 [--sin-cadencias]
python -m pytest
```

`python -m leda esquema --recrear` borra los datos. No ejecutarlo sin una autorización explícita y un entorno
descartable confirmado.

## Reglas de seguridad

- No leer, imprimir, versionar ni incluir en diagnósticos archivos `.env*`, salvo la plantilla `.env.ejemplo`.
- No inspeccionar untracked antes de asegurar las exclusiones sensibles en `.gitignore`.
- No ejecutar SQL destructivo, pruebas contra una base no confirmada como descartable ni comandos de despliegue sin
  autorización.
- No registrar cuerpos de conversaciones ni errores crudos en documentación.
- No afirmar que una prueba, restore, backup o rollback funciona sin evidencia de una ejecución registrada.
- No hacer commits, cambiar configuración Git o agregar archivos al índice salvo pedido explícito.

## Cómo trabajar y registrar continuidad

Antes de implementar una fase:

1. Confirmar que `docs/STATUS.md` sigue vigente contra el repositorio y escribir el chequeo de rumbo ("Cómo
   pensamos juntos", punto 3, más abajo).
2. Elegir el menor circuito útil de extremo a extremo que pruebe comprensión, respuesta, coordinación o reducción
   de carga humana.
3. Resolver sólo las decisiones y guardas que bloquean ese circuito; no adelantar hardening de producción sin
   evidencia.
4. Mantener comportamiento, verificación focalizada, replay/regresión y documentación de esa unidad juntos.
5. Registrar comando, resultado exacto, escenario operativo y límite de rollback.

**Hallazgos de conversación: reglas generales, no parches**
([`ADR 0013`](docs/decisions/0013-reglas-generales-de-la-conversacion.md), decisión del
usuario del 2026-09-29). Las variantes de una conversación son infinitas; arreglar cada
caso con listas de frases o palabras clave no termina nunca. Ante un hallazgo sobre cómo
conversa Leda:

- Clasificarlo primero en una de las reglas del ADR 0013: pregunta pendiente como
  contexto (comandos cerrados; una sola rama de conversación abierta a la vez, enmienda
  del 2026-09-29), una respuesta visible por mensaje, estado real y sólo
  opciones posibles, toque con señal e idempotente.
- Corregir el mecanismo de esa regla y probarlo con el caso y con familias de variantes,
  no sólo con la frase observada.
- Si no entra en ninguna regla, discutir con el usuario una regla nueva antes de
  parchear.
- Si el hallazgo vuelve después de corregir el mecanismo de su regla, el mecanismo no
  alcanza: es un disparador para parar y revisar el flujo ("Cómo pensamos juntos",
  punto 4).
- Reparto de trabajo: el modelo interpreta el lenguaje y devuelve un comando de una lista
  cerrada; el código ejecuta un manejo determinista por comando y garantiza las
  invariantes. Es el patrón probado de los asistentes de tareas ("conversation repair
  patterns", por ejemplo en Rasa), adoptado dentro del monolito, no como dependencia.

### Cómo pensamos juntos (usuario y agente)

Acordado con el usuario el 2026-09-30, al cerrar la ronda 4. Vigente para toda sesión.

**Por qué existe.** Dos veces el proyecto subió de nivel porque el usuario frenó y
propuso mirar desde arriba (reglas generales en el ADR 0013, el flujo en el ADR 0014).
El agente seguía el orden documentado y corregía hallazgo por hallazgo: cada arreglo era
razonable, las pruebas pasaban y parecía progreso, y nada dentro de la tarea decía
"pará". El agente empieza cada sesión de cero y ve el pasado sólo por los documentos;
el usuario tiene la memoria de las rondas. Por eso la señal de parar tiene que estar
escrita en el proceso, no depender de que alguien la note.

**1. Roles complementarios.** El usuario aporta continuidad entre rondas, contexto
operativo y criterio de producto; el agente, razonamiento amplio, conocimiento y
velocidad. Ninguno tiene la razón por defecto.

**2. Toda propuesta se evalúa antes de ejecutarse.** Lo que propone el usuario se
verifica contra el código y los documentos, se cuestiona y se debate, con alternativas y
sus costos, salvo que diga "hacelo sí o sí". La evaluación es proporcional: en algo
chico y reversible, la objeción en una línea y se sigue; en lo que cambia producto,
arquitectura o días de trabajo, se debate antes de empezar. Estar de acuerdo también se
fundamenta.

**3. Chequeo de rumbo, escrito.** Antes de empezar una unidad o una ronda, y al volver
de cada prueba real, el agente responde por escrito en el documento de la unidad
(`odd/tasks/…`) o en `docs/STATUS.md`:

- ¿Qué clase de problema ataca esto, y ya apareció antes con otra forma?
- ¿Es un mecanismo general o un caso?
- ¿Qué haría innecesaria la próxima ronda?
- ¿Sigue valiendo la hipótesis que justificó este camino?

Si una respuesta no convence, se para y se discute con el usuario antes de seguir. No es
un trámite: se razona antes de gastar una ronda, no después de varias.

**4. Disparadores que obligan a parar**, sin esperar al chequeo:

- un arreglo que agrega un caso especial (una frase, una condición o una bandera para
  el caso observado);
- la misma función o el mismo camino tocado por dos arreglos seguidos;
- la misma clase de hallazgo en dos rondas;
- pruebas en verde y el usuario dice que se siente mal;
- un hallazgo que contradice un ADR vigente.

Al dispararse uno, se revisa el mecanismo o el flujo, no el caso.

**5. Probar en real enseguida** (decisión del usuario). Construir la porción más chica
que se pueda probar y llevarla a Telegram real con datos ficticios cuanto antes. Todo
plan nombra primero su prueba real más temprana y recorta el alcance para llegar a ella.
Las mediciones baratas (banco, repeticiones) corren en paralelo con la construcción. La
documentación registra decisiones y su porqué, no ensayos.

**6. Lo sólido no se simplifica.** La base, el aislamiento entre clientes, las
confirmaciones y la auditoría funcionan. Ninguna propuesta de "simplificar" (un
framework de agente, un modelo con SQL libre, reglas en el prompt en vez de garantías)
las reemplaza: las instrucciones gobiernan el comportamiento; el código y la base, lo
que no puede pasar nunca
([`ADR 0014`](docs/decisions/0014-flujo-de-un-mensaje.md), alternativas).

**7. Un camino pasa al flujo nuevo sólo cuando se retiró lo viejo.** El problema de la
conversación es dónde participa el modelo, no la falta de reglas. Si los mecanismos
viejos conviven con los nuevos, el camino no está terminado y el sistema queda peor.

**8. Separar modelo de flujo.** Antes de atribuir una falla de comprensión al flujo,
medir cuánto aporta el modelo: Leda usa un modelo "flash" chico, elegido por
velocidad, y medirlo con el banco es barato.

**9. Funcionalidad nueva congelada** (decisión del usuario) hasta que alta, entrega y
aprobación cumplan en una prueba real los criterios del ADR 0014. Alcance en
`docs/ROADMAP.md`, "Orden de entrega". Lo que se pida de pasada se anota en el roadmap y
se recuerda el congelamiento.

**10. Proyectos externos: ideas, no bases.** Un PM conversacional multi-cliente con
garantías es un problema propio ([`docs/research/`](docs/research/)).

### Al terminar una unidad

- actualizar `docs/STATUS.md` con hechos comprobados, riesgos y próximo paso;
- marcar una prueba como ejecutada sólo con comando, fecha y resultado;
- después de la verificación técnica, evaluar el gate de sesión progresiva del protocolo canónico: si el circuito
  es elegible, programar su prueba por Telegram real con datos ficticios sin esperar a completar las Fases 1-4; si
  no, usar harness determinista o `TestClient` y registrar la condición pendiente. Comprobar como mínimo workspace
  local o de prueba controlado, ausencia de datos y trabajo real, secreto de Telegram protegido, efectos
  inspeccionables y reversibles, backup, pausa o rollback proporcionado, ninguna operación destructiva y cero
  `CRITICAL` o `HIGH` abiertos en el circuito;
- inspeccionar respuesta visible, PostgreSQL, herramientas/efectos y auditoría/historia; corregir la causa raíz
  observada y agregar replay/regresión antes de reanudar;
- si el comportamiento es aceptable, elegir el siguiente circuito pequeño y endurecer proporcionalmente según
  evidencia;
- actualizar `docs/ROADMAP.md` sólo si cambió la secuencia o el criterio de salida;
- crear un ADR numerado para decisiones de dominio o arquitectura duraderas;
- no borrar decisiones anteriores: registrar si una nueva las reemplaza.

La sesión progresiva aporta evidencia de desarrollo y regresión, pero no aprueba el piloto ni usa el holdout;
registrar su resultado sólo cuando cambie un hecho relevante.

ADR 0003 quedó superada por el cambio de alcance a producto multi-tenant (la amenaza principal pasó a ser el cruce
entre clientes); no se borra ni se implementa en su secuencia original. Su Corte 0 (catálogo ejecutable de
propietarios, membresías, grants y ACL) **no está diferido**: es el control que habría detectado las tablas de
eventos con `grant insert` sin `workspace_id` ni RLS, e insumo de la unidad de cierre del aislamiento de
`docs/ROADMAP.md` (detalle en [`ADR 0003`](docs/decisions/0003-authenticated-inbound-boundary.md)). Los controles
avanzados de privacidad y producción siguen en el horizonte posterior del roadmap.

Antes de cerrar una sesión, y después de su última modificación, operación o commit, contrastar `docs/STATUS.md` y
los documentos de continuidad afectados con el estado actual de Git, código, esquema, pruebas y operación. Si
cambió un hecho relevante, actualizar los documentos correspondientes; si no cambió, no editar documentación sólo
para registrar la sesión.

Usar `PENDIENTE` para datos aún no comprobados o decisiones abiertas. No convertir hipótesis, recomendaciones ni
contenido del roadmap en estado implementado.
