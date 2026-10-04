> **Archivo del 2026-10-04.** Copia de `AGENTS.md` tal como estaba antes de reducirlo a lo que sirve (después del paso M1, 2026-10-04). Es historia, no una instrucción: el archivo vigente es [`AGENTS.md`](../../AGENTS.md). Todo lo que sigue a este aviso es literal.

# Continuidad de trabajo en Leda

Este archivo es el punto de entrada para futuras sesiones. Leda se endurece y extiende sobre la arquitectura
actual; no se reestructura ni reescribe sin una decisión explícita y documentada. La del 2026-10-04 es una de
esas decisiones y se llama **el Motor**: cambia el cimiento de la capa de conversación y deja intacta la capa
de garantías (ver "Dónde se trabaja y qué no se hace" y "Nombres que usamos"). Versiones previas de este
archivo:
[`docs/historial/AGENTS-hasta-2026-09-30.md`](docs/historial/AGENTS-hasta-2026-09-30.md) (sin condensar),
[`docs/historial/AGENTS-hasta-2026-10-04.md`](docs/historial/AGENTS-hasta-2026-10-04.md) (antes del Motor) y
[`docs/historial/AGENTS-hasta-M1.md`](docs/historial/AGENTS-hasta-M1.md) (hasta el paso M1); las dos últimas son
literales salvo el aviso de archivo de su primera línea. Lo que dicen esas copias es historia, no una
instrucción vigente.

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
@odd/tasks/motor-de-conversacion.md
@nucleo/constitucion.md
@nucleo/mecanica-pm.md
@nucleo/alta-de-equipo.md

El segundo es el documento de la unidad del Motor (etapas, tareas hechas y pendientes, y evidencia); se
importa desde el 2026-10-04, en la rama `feat/motor-de-conversacion`.

Un agente que no expanda estas importaciones (otra herramienta que lea `AGENTS.md`)
tiene que leer esos cinco archivos enteros antes de su primera respuesta.

## Dónde se trabaja y qué no se hace (desde el 2026-10-04)

El trabajo vigente es **el Motor**: la línea de trabajo que el usuario decidió el 2026-10-04. Qué abarca está
definido en "Nombres que usamos". La prueba real de ese día volvió a fallar con fallas nuevas de la misma
clase, después de varias vueltas de arreglos y de cinco auditorías, y un análisis adversarial del proyecto
([`docs/research/gestion-del-dialogo-y-arquitecturas-de-agentes.md`](docs/research/gestion-del-dialogo-y-arquitecturas-de-agentes.md))
mostró que la base es correcta y que la falla está en la capa de conversación, escrita a mano y sin un modelo de
la conversación. Por eso se deja de corregir la conversación de los flujos anteriores y se construye un motor
chico de conversación dentro de Leda, sin marcos de terceros, con el alcance recortado al seguimiento: por
ahora Leda no crea tareas ni objetivos por chat. Principio: *por chat, hechos del trabajo; por la web, su
estructura.*

**Dónde.**

- Rama `feat/motor-de-conversacion`, carpeta `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`, abierta
  desde la etiqueta `respaldo-main-antes-de-d`. **Las sesiones de trabajo se abren en esa carpeta.**
- Si la sesión se abrió en otra carpeta (por ejemplo `D:\Proyectos\Leda-PM`, que es `main`), los documentos
  que se cargaron solos pueden estar atrasados: los vigentes son los de la carpeta nueva. Antes de responder,
  leer de esa carpeta `AGENTS.md`, `docs/STATUS.md`, `odd/tasks/motor-de-conversacion.md` y los tres documentos
  de `nucleo/`. `main` recibe sólo documentos, por avance rápido desde la rama del Motor y cuando lo decide el
  usuario, hasta el paso M2 o M3 (`docs/STATUS.md`, "Criterios de paso a `main`").
- Nunca se abre una sesión de trabajo en las carpetas congeladas de `D:\Proyectos\Leda-PM-worktrees\`:
  `flujo-de-un-mensaje`, `alta-y-google`, `c4-medicion`, `flujo-c6` y `prueba-0-35`. Cada una lleva un aviso de
  congelamiento al comienzo de su `AGENTS.md`; el resto de sus documentos es anterior al Motor.
- Siempre se empieza una sesión nueva. Una sesión iniciada antes del cambio del 2026-10-04 conserva en su
  contexto las instrucciones anteriores y no se continúa.
- Una sola casa para los documentos: `AGENTS.md`, `docs/STATUS.md`, `docs/ROADMAP.md`, la bitácora de flujos,
  los ADR y el documento de la unidad se editan sólo en la rama nueva.

**Dónde quedó el trabajo.** El estado, dónde quedó la última sesión y el próximo paso están en
`docs/STATUS.md` ("Punto exacto para retomar"); las tareas hechas y pendientes, en el documento de la unidad.

**Qué no se hace.**

- Retomar tareas del alta por chat ni de `odd/tasks/circuitos-al-flujo-nuevo.md` (rama congelada): 0-35, 0-36,
  P-1c, P1-P7, 0-29, 0-17, 0-14 y las demás. El destino de cada una está en `docs/STATUS.md`, "Qué quedó
  congelado o superado".
- Corregir, mejorar o extender los flujos A, B o C, ni pasar circuitos al flujo C6.
- Escribir código de conversación sin su diseño aceptado ("Cómo pensamos juntos", punto 12), o crear el
  paquete del motor de conversación definitivo o su prueba de frontera antes de cortar los enredos, mudar las
  pruebas de garantías y borrar los flujos A y B (Etapa 3). La prueba chica de la Etapa 2 es descartable y vive
  fuera de `src/leda`.
- Tratar una suite en verde o la auditoría de otro agente como prueba de que la conversación funciona.
- Adoptar Rasa, Engram u otro marco de terceros como componente.
- Construir la creación de tareas o de objetivos por chat.

**Sobre `nucleo/`.** Los tres documentos de `nucleo/` se cargan al iniciar cada sesión y siguen siendo el
comportamiento obligatorio del producto: el ideal que Leda tiene que alcanzar, que no se edita. Los pasajes que
necesitan capacidades fuera del alcance actual todavía no se aplican y vuelven a medida que se suman
capacidades; cuáles son y cómo se cubre cada uno hoy está en el ADR 0017, decisión 7.

Las garantías de `nucleo/` no cambian: la confirmación humana antes de un efecto, la honestidad, el trato con
las personas, la opacidad técnica, la auditoría y el aislamiento entre espacios.

## Nombres que usamos

Acordado con el usuario el 2026-10-02 y actualizado el 2026-10-04, para hablar el mismo idioma. Usar siempre
estos nombres con el usuario; "conducida", "guiada" o "método nuevo" confunden.

- **El Motor:** el nombre de toda la línea de trabajo que el usuario decidió el 2026-10-04. Cuando el usuario
  dice "el Motor", "seguimos con el Motor" o "esto es del Motor", se refiere a toda esa línea de trabajo, no
  sólo a su pieza de software. Abarca cinco cosas:
  1. la decisión de dejar de parchear la conversación;
  2. la rama nueva `feat/motor-de-conversacion` y su carpeta
     `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`, con los flujos A, B y C congelados;
  3. el recorte de alcance: Leda hace seguimiento y, por ahora, no crea tareas ni objetivos por chat;
  4. el motor de conversación propio, en tres partes: estado exacto, registro completo de la conversación y,
     más adelante, memoria;
  5. el método: diseño antes del código y conversaciones reales como pruebas.

  Sus documentos son `odd/tasks/motor-de-conversacion.md` (el documento de la unidad, en la rama nueva), el
  ADR 0017 (alcance) y el ADR 0018 (motor de conversación). En los documentos,
  "el Motor" a secas nombra siempre la línea de trabajo entera; su pieza de software se escribe completa,
  "el motor de conversación", para no confundirlas.
- **La IA:** el modelo de lenguaje que Leda usa por dentro. No se le dice "modelo", para
  no confundirlo con los flujos.
- **Flujo:** la forma en que Leda procesa un mensaje. Una letra por mecanismo distinto y
  un número por versión (flujo C1, C2…):
  - **Flujo A, formulario mecánico** (congelado): pasos fijos, un dato por vez, botones y reglas fijas en el
    código para entender lo que se escribe. Es el alta guiada de `main`.
  - **Flujo B, IA libre** (congelado): la IA lee toda la constitución, elige herramientas y redacta como le
    parece. Es lo que atiende en `main` todo lo que no es el alta (consultas, menú, cambios, entrega,
    aprobación). Ahí la IA inventó un cambio (hallazgo H5).
  - **Flujo C, el del [ADR 0014](docs/decisions/0014-flujo-de-un-mensaje.md)** (congelado): la IA interpreta,
    el código decide y ejecuta, la IA redacta a partir de los hechos. Sus seis versiones (C1 a C6) sólo
    alcanzaron el alta y viven en la rama `feat/flujo-de-un-mensaje`; no están en `main` ni en la rama nueva.
  - **Flujo D:** sólo el nombre técnico del mecanismo, es decir, cómo procesa un mensaje el Motor:
    estado de la conversación explícito, circuitos declarados y situaciones generales resueltas una sola vez.
    Se usa al compararlo con los flujos A, B y C, por ejemplo en la bitácora de flujos. No es el nombre del
    plan: el plan es el Motor. Su diseño está en el ADR 0018.
- **Flujos congelados** (decisión del usuario, 2026-10-02, "como copiar un archivo de
  Paint y trabajar sólo en la copia"): al empezar un flujo nuevo se pone una **etiqueta
  de Git** a todo el código tal como está. Esa etiqueta es la copia intacta de los flujos anteriores. Desde ahí
  se trabaja **sólo en el flujo actual**: los anteriores no se mejoran ni se corrigen, y si un cambio del
  flujo actual los rompe, no se arreglan (la versión buena está en la etiqueta; sus
  pruebas rotas se retiran junto con su código). No se mantienen dos flujos andando a la
  vez ni interruptores nuevos por circuito. Los flujos anteriores no llegan al producto: el producto final se
  queda con el flujo definitivo y los demás se descartan. Desde el 2026-10-04 están congelados los flujos A, B
  y C: la etiqueta `respaldo-flujos-antes-de-d` guarda la rama de flujo, `respaldo-main-antes-de-d` guarda
  `main`, y `respaldo-0-36-en-pausa` guarda, sólo para consulta, el trabajo parcial de la última tarea del alta,
  que se detuvo y no se retoma.
- **Etapas y pasos M1 a M3:** el orden de trabajo del Motor. Etapa 1, diseño sin código; Etapa 2, prueba
  chica y descartable; Etapa 3, limpieza y motor de conversación definitivo. M1, M2 y M3 son los criterios
  para pasar la rama nueva a `main`. Detalle en `docs/STATUS.md`, "Próximo paso".
- **Bitácora de flujos:** [`docs/product/bitacora-de-flujos.md`](docs/product/bitacora-de-flujos.md)
  junta lo que se probó de cada flujo y de cada modelo, lo bueno y lo malo, y la
  conclusión vigente. Se lee antes de proponer un cambio de flujo o de modelo, y se actualiza al cerrar cada
  prueba real, medición o auditoría.
- **Personalidad:** cómo es y cómo se comporta Leda (`nucleo/personalidad.md`; el archivo está en la rama nueva
  y en la rama congelada, no en `main`). Es una referencia de diseño y no se le manda a la IA como texto aparte:
  así contradecía la mecánica y sumaba latencia (medición del 2026-10-02). Cómo llega el tono de cada cliente a
  la IA en el Motor está `PENDIENTE`: el ADR 0018 no lo fija.
- **Voz:** reservado para cuando Leda responda con audio. No se usa para la personalidad.
- **Circuito:** cada cosa que Leda sabe hacer (entrega, aprobación, bloqueos, seguimiento…). La lista numerada
  del 0 al 10 y sus tareas (0-1, 0-2…) eran de la rama congelada. Los circuitos por chat del Motor están en el
  ADR 0017, decisión 3b.
- **"Apagá / prendé la restricción de horario":** para probar por Telegram a cualquier
  hora. Leda no escribe fuera del horario del espacio (constitución §8), y ese horario
  es un dato de cada cliente (`work_calendar`, cargado del `calendario` del pack), no una
  regla del código. Apagarla pone el horario del espacio en todos los días, 00:00-23:59;
  prenderla lo restaura desde el pack. Se hace con
  `tools/restriccion_horario.py apagar|prender|estado <espacio>`, desde el worktree de la
  base que se quiere tocar y con `PYTHONPATH=src`; hoy sólo admite las bases `leda` y `leda_flujo`, así que
  para la base de la rama nueva hay que ajustarla cuando llegue la Etapa 2.
  Mientras está apagada, todos los días cuentan como hábiles y los plazos de los
  recordatorios se acortan.

## Orden de lectura

1. `docs/product/que-es-leda.md`: qué es el producto y qué es configuración de cada cliente.
2. `docs/architecture/frontera.md`: dónde termina el núcleo y qué reglas lo gobiernan.
3. `nucleo/` (`constitucion.md`, `mecanica-pm.md`, `alta-de-equipo.md`): comportamiento **obligatorio** de Leda,
   no material de consulta. Una auditoría que no lo haya leído entero no está terminada. Ver "Sobre `nucleo/`"
   más arriba para lo que el recorte de alcance deja pendiente.
4. `docs/capacidades.md`: qué está construido, qué está diseñado sin construir y qué es esquema sin implementación.
5. `docs/STATUS.md`: estado, riesgos, próximo paso y punto exacto para retomar.
6. `odd/tasks/motor-de-conversacion.md` (rama nueva): el documento de la unidad del Motor, con el chequeo de
   rumbo, las etapas y la lista de lo que se trae de la rama congelada.
7. `docs/ROADMAP.md`: unidades de trabajo; el criterio de su orden está en el ADR 0017, decisión 5.
8. `docs/product/bitacora-de-flujos.md` y `docs/research/gestion-del-dialogo-y-arquitecturas-de-agentes.md`:
   por qué se congelaron los flujos anteriores y qué evidencia sostiene el Motor.
9. `docs/INDEX.md`: elegir sólo el detalle necesario (`docs/historial/` y `docs/traspaso/` guardan documentos
   anteriores; no son lectura de arranque ni puntos de retorno).
10. Los ADR aplicables antes de cambiar dominio o arquitectura.
11. Contrastar cualquier afirmación con código, esquema y pruebas actuales.

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
   Los ADR 0013 y 0014 están superados en parte desde el 2026-10-04: la nota al comienzo de cada uno dice qué
   sigue vigente, qué quedó reemplazado y qué está `PENDIENTE`. Los demás ADR aceptados son anteriores al
   Motor: sus garantías siguen vigentes, y lo que digan sobre cómo conversa Leda no se toma como regla cuando
   contradice la constitución §8 o las decisiones del 2026-10-04 (por ejemplo, cuándo van botones en el
   ADR 0005, decisión 4, y en el ADR 0007).
6. `docs/STATUS.md` y `docs/ROADMAP.md`: estado y orden de trabajo. El orden vigente es el de `docs/STATUS.md`,
   "Próximo paso"; el criterio del roadmap lo redefine el ADR 0017, decisión 5.
7. `README.md` y `PRUEBA-LOCAL.md`: guía operativa; contrastar con la implementación si hay discrepancias.

La autoridad de `nucleo/` está por encima de cualquier documento de `docs/`. Buena parte de lo que manda todavía
no tiene código; `docs/capacidades.md` lleva la cuenta. `docs/product/functional-specification.md` quedó superada
por el cambio de alcance a producto multi-tenant: es insumo histórico, contrastarla contra la frontera antes de
usar cualquier parte. Una especificación expresa intención, no prueba implementación; un test existente no prueba
que la suite pase hasta ejecutarlo, y una suite que pasa no prueba que la conversación funcione ("Cómo pensamos
juntos", punto 12).

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
  confirmada y auditable. Una tarea que carga el administrador entra comprometida por declaración: se valida
  con los mismos datos, la auditoría separa quién la cargó y quién la decidió, y Leda nunca la presenta como
  una aprobación hecha en Leda (ADR 0017, decisión 2).
- Actualización, evidencia, aprobación y cierre son hechos distintos.
- No poder consultar datos no equivale a que no existan.

## Límites de alcance

El producto conserva un monolito modular en Python y PostgreSQL. Fuera del producto por ahora; no construir sin una
decisión explícita y documentada: agenda o calendarios externos, aprendizaje persistente, motor genérico de
workflows, microservicios e interfaz administrativa completa.

Precisiones de los ADR 0017 y 0018:

- El motor de conversación no es un motor genérico de workflows: sus circuitos son un conjunto cerrado,
  declarado en el código, nunca configuración de un cliente (ADR 0018, decisión 4).
- Las tareas se cargan con un formulario en una plataforma web, donde también se ve su estado, se cambian las
  fechas por retrasos y se gestionan los integrantes. Para eso deja de regir la exclusión de la interfaz
  administrativa. La plataforma se diseña en su propio ADR antes del código; la prueba chica usa tareas
  ficticias cargadas con `sembrar` (ADR 0017, decisión 5).
- La memoria por integrante es aprendizaje persistente: tiene su lugar reservado como tercera parte del motor
  de conversación y no se construye sin su propio ADR (ADR 0018, decisión 3). Leda puede aprender sola formas
  nuevas de decir algo que ya es una jugada; una jugada nueva la decide una persona, y el aprendizaje nunca
  cambia lo que Leda tiene permitido (ADR 0018, decisión 1). Engram es sólo una referencia de diseño.

Dentro del producto pero todavía no: la API de lectura y el dashboard, por sus precondiciones (cierre del
aislamiento entre clientes y desacople del transporte). No se tratan como prohibidos, pero tampoco se empiezan
ahora: la funcionalidad nueva espera según el ADR 0017, decisión 5 ("Cómo pensamos juntos", punto 9).

No cambiar lógica, esquema, dependencias o arquitectura durante trabajo puramente documental. No reestructurar
carpetas o módulos sin un ADR aceptado.

## Comandos verificados por inspección

Existen en `README.md`, `PRUEBA-LOCAL.md`, `pyproject.toml` o `src/leda/cli.py`. Su disponibilidad fue
inspeccionada; su resultado actual no se presume. Corren el código de la carpeta donde se ejecutan: hoy, en
`main` y en la rama nueva, la conversación que levantan es la de los flujos A y B, congelada.

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
- No hacer commits, cambiar configuración Git o agregar archivos al índice salvo pedido explícito. El usuario
  dio consentimiento permanente para los commits de cada unidad de trabajo y para las revisiones RDD; los
  commits no llevan líneas de atribución; el push lo decide siempre el usuario; y `main` recibe sólo
  documentos, por avance rápido, hasta el paso M2 o M3.

## Cómo trabajar y registrar continuidad

Antes de implementar una fase:

1. Confirmar que `docs/STATUS.md` sigue vigente contra el repositorio y escribir el chequeo de rumbo ("Cómo
   pensamos juntos", punto 3, más abajo).
2. Tener el diseño escrito y aceptado antes de escribir código de conversación ("Cómo pensamos juntos",
   punto 12).
3. Elegir el menor circuito útil de extremo a extremo que pruebe comprensión, respuesta, coordinación o reducción
   de carga humana.
4. Resolver sólo las decisiones y guardas que bloquean ese circuito; no adelantar hardening de producción sin
   evidencia.
5. Mantener comportamiento, verificación focalizada, replay/regresión y documentación de esa unidad juntos.
6. Registrar comando, resultado exacto, escenario operativo y límite de rollback.

**Hallazgos de conversación: reglas generales, no parches**
([`ADR 0013`](docs/decisions/0013-reglas-generales-de-la-conversacion.md), decisión del
usuario del 2026-09-29; procedimiento cambiado por el usuario el 2026-10-04). Las variantes de una conversación
son infinitas; arreglar cada caso con listas de frases o palabras clave no termina nunca.

Las reglas del ADR 0013 siguen vigentes como reglas de comportamiento, es decir, lo que Leda tiene que cumplir
en cualquier flujo:

- pregunta pendiente como contexto, con una sola rama de conversación abierta a la vez (enmienda del
  2026-09-29);
- una respuesta visible por mensaje y por toque;
- estado real y sólo opciones posibles;
- toque con señal e idempotente.

A esas reglas se suman tres decisiones del usuario sobre cómo conversa Leda:

- **Botones para elegir, texto para decir** (enmienda del ADR 0013 del 2026-10-02).
- **Los botones son atajos:** lo que hace un botón también tiene que poder decirse por escrito (2026-10-04).
  Alcanza también a una confirmación que crea o cambia algo, con una guarda (ADR 0018, decisión 2).
- **Un tema a la vez:** si la persona cambia de tema con algo abierto, Leda se lo recuerda y le ofrece seguir,
  retomarlo después o cancelarlo, y recién entonces atiende lo nuevo (2026-10-04). Es una de las situaciones
  generales del motor de conversación (ADR 0018, decisión 4).

El procedimiento ante un hallazgo sobre cómo conversa Leda es éste:

- Un hallazgo en un flujo congelado (A, B o C) no se arregla.
- El hallazgo se convierte primero en una conversación de prueba (punto 12). Después se resuelve en el motor
  de conversación, como una situación general que vale para todos los circuitos, nunca como una rama para un
  camino.
- Un "arreglo del mecanismo" hecho dentro de una estructura equivocada también es un parche (usuario,
  2026-10-04: "siempre estamos parcheando fallas"). No se agregan listas de frases, palabras clave ni casos
  especiales, y tampoco reglas nuevas dentro de los caminos viejos.
- Si una prueba real vuelve a fallar después de un arreglo, nadie propone el arreglo siguiente: se para y se
  cuestiona el nivel del diseño (el modelo de la conversación, el motor de conversación, el método), con
  evidencia ("Cómo pensamos juntos", punto 4).
- Si un hallazgo no entra en ninguna regla, se discute con el usuario una regla nueva antes de tocar nada.

Reparto de trabajo (ADR 0013): el modelo interpreta el lenguaje y devuelve un comando de una lista cerrada; el
código ejecuta un manejo determinista por comando y garantiza las invariantes. Es el patrón probado de los
asistentes de tareas ("conversation repair patterns", por ejemplo en Rasa). Hasta el 2026-10-04 se tomó la
idea, pero cada situación se resolvió a mano en cada camino; el motor de conversación existe para resolverlas
una sola vez. No se adopta Rasa ni ningún otro marco como dependencia. En el Motor, qué decide la IA y qué
decide el código lo fija el ADR 0018, decisión 1.

### Cómo pensamos juntos (usuario y agente)

Acordado con el usuario el 2026-09-30, al cerrar la ronda 4, y actualizado el 2026-10-04. Vigente para toda
sesión.

**Por qué existe.** Cada vez que el proyecto subió de nivel fue porque el usuario frenó y
propuso mirar desde arriba: las reglas generales (ADR 0013), el flujo de un mensaje (ADR 0014), la regla del
mozo (2026-10-03) y el Motor (2026-10-04).
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
- ¿Este diseño es mecánico? ¿Se puede hacer más fluido y conversacional? Siempre que se
  pueda, se optimiza para fluidez y practicidad (decisión del usuario, 2026-10-02): la
  persona escribe como habla, varias cosas juntas, y Leda pregunta sólo lo que falta. La
  fluidez nunca saltea una garantía (punto 6): las confirmaciones de la constitución §7,
  la validación del código y la auditoría se quedan.
- ¿Los datos y los efectos salen de la cocina, o le estamos enseñando frases al mozo? (punto 11).
- ¿Qué conversación de prueba, corrida contra la IA real, lo demuestra? (punto 12).

Si una respuesta no convence, se para y se discute con el usuario antes de seguir. No es
un trámite: se razona antes de gastar una ronda, no después de varias.

**4. Disparadores que obligan a parar**, sin esperar al chequeo:

- un arreglo que agrega un caso especial (una frase, una condición o una bandera para
  el caso observado);
- la misma función o el mismo camino tocado por dos arreglos seguidos;
- la misma clase de hallazgo en dos rondas;
- pruebas en verde y el usuario dice que se siente mal;
- un hallazgo que contradice un ADR vigente;
- una prueba real que vuelve a fallar después de un arreglo del mecanismo.

Al dispararse uno, se revisa el mecanismo, el flujo o el diseño, no el caso. Con el último, además, no se
propone otro arreglo: se cuestiona el nivel del diseño.

**5. Probar en real enseguida** (decisión del usuario). Construir la porción más chica
que se pueda probar y llevarla a Telegram real con datos ficticios cuanto antes. Todo
plan nombra primero su prueba real más temprana y recorta el alcance para llegar a ella.
Las mediciones baratas (banco, repeticiones) corren en paralelo con la construcción. La
documentación registra decisiones y su porqué, no ensayos. Desde el 2026-10-04, el diseño corto y escrito va
antes de esa porción (punto 12).

**6. Lo sólido no se simplifica.** La base, el aislamiento entre clientes, las
confirmaciones y la auditoría funcionan. Ninguna propuesta de "simplificar" (un
framework de agente, un modelo con SQL libre, reglas en el prompt en vez de garantías)
las reemplaza: las instrucciones gobiernan el comportamiento; el código y la base, lo
que no puede pasar nunca
([`ADR 0014`](docs/decisions/0014-flujo-de-un-mensaje.md), alternativas).

**7. Un camino pasa al flujo nuevo sólo cuando se retiró lo viejo.** Si los mecanismos
viejos conviven con los nuevos, el camino no está terminado y el sistema queda peor. En el Motor, el código
de los flujos A y B se borra antes de construir el motor de conversación definitivo (Etapa 3), después de
mudar las pruebas de garantías que hoy viven en archivos del código viejo.

**8. Separar modelo de flujo.** Antes de atribuir una falla de comprensión al flujo,
medir cuánto aporta la IA. En las pruebas reales del flujo C6 la más fiel a los hechos fue GPT-6 sol
(bitácora de flujos). En el flujo D, la prueba chica arranca con GPT-6 sol y mide GPT-6 luna y Jev en paralelo
(ADR 0018, decisiones 6 y 7).

**9. Funcionalidad nueva congelada** (decisión del usuario, 2026-09-30; redefinida por el ADR 0017, decisión 5).
En esta etapa se construyen el seguimiento por chat y la plataforma web de tareas; lo demás espera en la lista
"Anotado para más adelante" del documento de la unidad hasta que Leda haga bien el seguimiento en pruebas reales.
Lo que se pida de pasada se anota en esa lista y se recuerda el congelamiento.

**10. Proyectos externos: ideas, no bases.** Un PM conversacional multi-cliente con
garantías es un problema propio ([`docs/research/`](docs/research/)). Rasa quedó descartado como componente (el
usuario no quiere depender de licencias de terceros) y Engram se toma sólo como referencia de diseño para la
memoria por integrante.

**11. La regla del mozo** (decisión del usuario, 2026-10-03). La IA es el mozo: escucha o pregunta qué quiere
la persona, lleva el pedido exacto a la cocina (el código y la base) y trae lo que la cocina dice, contándolo
con naturalidad. Sigue vigente su núcleo:

- La IA no inventa datos ni efectos, y no promete lo que la cocina no dijo. Todo lo que es conocimiento del
  caso (estados, reglas, motivos, opciones, quién hizo qué) llega desde la cocina como hechos.
- Una propuesta de la IA es una sugerencia que la persona ve y acepta, nunca un dato que se guarda solo.
- Las instrucciones de la IA describen su trabajo (escuchar, llevar el pedido, traer y contar lo que dice la
  cocina, no inventar); no llevan reglas para casos puntuales, ejemplos de lo que tiene que decir ni formas de
  pregunta. Su largo no importa: la latencia se trabaja aparte. Un arreglo que le agrega una regla para un caso
  dispara el punto 4.
- Si la IA dice algo mal, primero se mira si la cocina le pasó el hecho correcto, completo y visto desde
  quien lo recibe.
- La cocina no corrige lo que el mozo escuchó con heurísticas propias (comparar palabras, listas de frases):
  valida datos y aplica reglas.

**Enmienda (ADR 0018, decisión 1).** La IA elige qué jugada corresponde, de una lista cerrada, y cómo decirlo;
el código decide si la jugada vale, cómo se maneja cada jugada y cada situación general, y ejecuta. Reemplaza la
extensión de la regla a cada movimiento de la conversación ("la IA no toma decisiones"), que el análisis del
2026-10-04 señaló como una de las causas de que el código tuviera que prever cada situación.

**12. Diseño antes del código y evidencia real** (decisiones del usuario, 2026-10-04; es el método del Motor).

- **Diseño en papel primero.** Ningún código de conversación se escribe antes de que su diseño esté escrito en
  un ADR y aceptado por el usuario. Para el motor de conversación, es el ADR 0018.
- **Un hallazgo es primero una conversación de prueba.** Antes de tocar nada, el hallazgo se escribe como una
  conversación (qué dice cada persona y qué tiene que quedar después), y esa conversación pasa a ser su
  regresión.
- **Qué cuenta como evidencia.** Que la conversación funciona lo muestran conversaciones reales contra la IA
  real, corridas varias veces. Una suite en verde no lo muestra: hasta el 2026-10-04 la suite pasó entera cada
  vez y cada prueba real encontró fallas, porque esas pruebas comprueban el código y las escribe el mismo
  escritor. La auditoría de otro agente tampoco lo muestra. El agente no informa "la suite pasa" como avance de
  la conversación.
- **Prueba chica antes de comprometerse.** El motor de conversación se prueba primero con una porción chica y
  descartable, con los criterios de éxito y de corte escritos antes (ADR 0018).
- **Una sola casa para los documentos.** Los documentos vivos se editan sólo en la rama del Motor ("Dónde se
  trabaja y qué no se hace").

### Al terminar una unidad

- actualizar `docs/STATUS.md` con hechos comprobados, riesgos y próximo paso;
- marcar una prueba como ejecutada sólo con comando, fecha y resultado;
- si fue una prueba real, una medición o una auditoría de la conversación, sumar su
  resultado a la bitácora de flujos y actualizar la conclusión vigente si cambió;
- después de la verificación técnica, evaluar el gate de sesión progresiva del protocolo canónico: si el circuito
  es elegible, programar su prueba por Telegram real con datos ficticios sin esperar a completar las Fases 1-4; si
  no, usar harness determinista o `TestClient` y registrar la condición pendiente. Comprobar como mínimo workspace
  local o de prueba controlado, ausencia de datos y trabajo real, secreto de Telegram protegido, efectos
  inspeccionables y reversibles, backup, pausa o rollback proporcionado, ninguna operación destructiva y cero
  `CRITICAL` o `HIGH` abiertos en el circuito;
- inspeccionar respuesta visible, PostgreSQL, herramientas/efectos y auditoría/historia. Un hallazgo en la
  capa de garantías (estado en PostgreSQL, efectos de herramientas, auditoría, aislamiento) se corrige en su
  causa raíz y se le agrega una regresión antes de seguir. Un hallazgo de conversación se convierte primero en
  una conversación de prueba y se resuelve en el motor de conversación, nunca en un flujo congelado ("Cómo
  pensamos juntos", punto 12);
- si el comportamiento es aceptable, elegir el siguiente circuito pequeño y endurecer proporcionalmente según
  evidencia;
- actualizar `docs/ROADMAP.md` sólo si cambió la secuencia o el criterio de salida;
- crear un ADR numerado para decisiones de dominio o arquitectura duraderas;
- no borrar decisiones anteriores: registrar si una nueva las reemplaza. Cuando `AGENTS.md` o `docs/STATUS.md`
  cambian de rumbo, la versión anterior se guarda en `docs/historial/` como copia literal, con un aviso de
  archivo en su primera línea, y el archivo vivo queda sólo con lo vigente, para que una sesión nueva no retome
  instrucciones viejas.

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
