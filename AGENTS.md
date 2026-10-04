# Continuidad de trabajo en Leda

Punto de entrada de cada sesión: qué leer, dónde se trabaja y las reglas estables. **No es un registro de
tareas:** el estado, dónde quedó la última sesión y el próximo paso están en `docs/STATUS.md` ("Punto exacto para
retomar"); las tareas hechas y pendientes, en el documento de la unidad. Este archivo cambia sólo cuando cambia
una regla estable. Versiones anteriores, como historia y no como instrucción, en `docs/historial/AGENTS-*.md`.

> **Este archivo es la fuente única de estas instrucciones.** `CLAUDE.md` contiene sólo `@AGENTS.md`, que las
> importa (la lectura nativa de `AGENTS.md` en Claude Code no está garantizada; la importación sí). Editar
> siempre este archivo, nunca `CLAUDE.md`.

## Lectura obligatoria al iniciar cada sesión

Pedido del usuario (2026-10-02): toda sesión arranca conociendo el estado y el núcleo sin que haya que pedírselo;
como figurar en el orden de lectura no alcanzaba, se importan:

@docs/STATUS.md
@odd/tasks/motor-de-conversacion.md
@nucleo/constitucion.md
@nucleo/mecanica-pm.md

El segundo es el documento de la unidad del Motor. `nucleo/alta-de-equipo.md` no se carga: no aplica en esta
etapa (ADR 0017, decisión 7) y se lee cuando haga falta. Un agente que no expanda las importaciones tiene que
leer esos cuatro archivos enteros antes de su primera respuesta.

## Dónde se trabaja y qué no se hace

El trabajo vigente es **el Motor** ("Nombres que usamos"): se dejó de parchear la conversación y se construye un
motor chico de conversación propio, con el alcance recortado al seguimiento. Principio: *por chat, hechos del
trabajo; por la web, su estructura.* El porqué está en
`docs/research/gestion-del-dialogo-y-arquitecturas-de-agentes.md`; las decisiones, en los ADR 0017 y 0018.

**Dónde.**

- Rama `feat/motor-de-conversacion`, carpeta `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`: **las
  sesiones se abren ahí, siempre como sesión nueva.** Si se abrió en otra carpeta (por ejemplo
  `D:\Proyectos\Leda-PM`, que es `main`), lo cargado puede estar atrasado: leer este archivo y los importados
  desde la carpeta del Motor.
- Nunca se abre una sesión en las carpetas congeladas de `D:\Proyectos\Leda-PM-worktrees\`:
  `flujo-de-un-mensaje`, `alta-y-google`, `c4-medicion`, `flujo-c6` y `prueba-0-35`.
- Una sola casa para los documentos vivos (este archivo, `docs/STATUS.md`, `docs/ROADMAP.md`, la bitácora de
  flujos, los ADR y el documento de la unidad): la rama del Motor. `main` recibe sólo documentos, por avance
  rápido y cuando lo decide el usuario, hasta el paso M2 o M3.

**Qué no se hace.**

- Retomar tareas del alta por chat o de la rama congelada (0-35, 0-36, P-1c, P1-P7, 0-29, 0-17, 0-14 y las
  demás; su destino, en `docs/STATUS.md`, "Qué quedó congelado o superado").
- Corregir, mejorar o extender los flujos A, B o C.
- Escribir código de conversación sin su diseño aceptado (punto 12), o el motor de conversación definitivo (su
  paquete en `src/leda` y su prueba de frontera) antes de la Etapa 3. La prueba chica de la Etapa 2 es
  descartable y vive fuera de `src/leda`.
- Tratar una suite en verde o la auditoría de otro agente como prueba de que la conversación funciona.
- Adoptar Rasa, Engram u otro marco de terceros como componente.
- Construir la creación de tareas u objetivos por chat (ADR 0017, decisiones 1 y 2).
- Escribir código de la plataforma web antes de su propio ADR (ADR 0017, decisión 5).

**Sobre `nucleo/`.** Es el comportamiento obligatorio de Leda: el ideal que tiene que alcanzar, que no se edita.
Su autoridad está por encima de cualquier documento de `docs/`. Los pasajes que necesitan capacidades fuera de
esta etapa todavía no se aplican y vuelven con ellas (cuáles y cómo se cubren hoy: ADR 0017, decisión 7). Las
garantías rigen siempre: confirmación humana antes de un efecto, honestidad, trato con las personas, opacidad
técnica, auditoría y aislamiento entre espacios.

## Nombres que usamos

Acordados con el usuario; usarlos siempre ("conducida", "guiada" o "método nuevo" confunden).

- **El Motor:** toda la línea de trabajo del 2026-10-04: dejar de parchear la conversación; la rama con los
  flujos A, B y C congelados; el recorte al seguimiento; el motor de conversación propio (estado exacto, registro
  completo y, después, memoria); y el método (diseño antes del código, conversaciones reales como pruebas). Su
  pieza de software se escribe completa: "el motor de conversación".
- **La IA:** el modelo de lenguaje que Leda usa por dentro; no se le dice "modelo", para no confundirlo con los
  flujos.
- **Flujo:** cómo procesa Leda un mensaje; una letra por mecanismo y un número por versión. **A**, formulario
  mecánico (el alta guiada de `main`); **B**, IA libre (el resto de `main`); **C**, el del ADR 0014 (C1 a C6, sólo
  del alta, en `feat/flujo-de-un-mensaje`). Los tres, congelados. **D** es sólo el nombre técnico del mecanismo
  del Motor, para compararlo con los anteriores, diseñado en el ADR 0018.
- **Flujos congelados** (usuario, 2026-10-02, "como copiar un archivo de Paint y trabajar sólo en la copia"):
  una etiqueta de Git guarda los anteriores y se trabaja sólo en el actual; los anteriores no se corrigen aunque
  un cambio los rompa (sus pruebas rotas se retiran con su código), y nunca hay dos flujos a la vez ni
  interruptores por circuito. Etiquetas: `respaldo-flujos-antes-de-d`, `respaldo-main-antes-de-d` y
  `respaldo-0-36-en-pausa` (sólo consulta).
- **Etapas y pasos M1 a M3:** Etapa 1, diseño; Etapa 2, prueba chica y descartable; Etapa 3, limpieza y motor
  definitivo. M1, M2 y M3 son los criterios de paso a `main` (`docs/STATUS.md`).
- **Bitácora de flujos** (`docs/product/bitacora-de-flujos.md`): lo probado de cada flujo y de cada IA, y la
  conclusión vigente; se lee antes de proponer un cambio de flujo o de IA y se actualiza tras cada prueba real,
  medición o auditoría.
- **Circuito:** cada cosa que Leda sabe hacer; en el Motor, las ocho cosas por chat del ADR 0017 (decisión 3b),
  cada una declarada con su ficha (ADR 0018, decisión 4).
- **Personalidad** (`nucleo/personalidad.md`): cómo es y se comporta Leda; referencia de diseño, no texto aparte
  para la IA. **Voz:** reservado para cuando Leda responda con audio.
- **"Apagá / prendé la restricción de horario":** para probar por Telegram a cualquier hora, con
  `tools/restriccion_horario.py apagar|prender|estado <espacio>` (`PYTHONPATH=src`, desde el worktree de la
  base). Apagada, el horario del espacio es 00:00-23:59 todos los días y los plazos de los recordatorios se
  acortan; prendida, vuelve el del pack. Hoy sólo admite las bases `leda` y `leda_flujo`: para la Etapa 2 hay que
  sumarle `leda_motor` antes de usarla.

## Orden de lectura y fuentes de verdad

Además de lo importado, según la tarea: `docs/product/que-es-leda.md` (qué es producto y qué es configuración de
cada cliente), `docs/architecture/frontera.md` (dónde termina el núcleo), `docs/capacidades.md` (qué está
construido), los ADR aplicables, `docs/ROADMAP.md` y la bitácora. `docs/INDEX.md` para el resto;
`docs/historial/` y `docs/traspaso/` son historia, no puntos de retorno.

**Autoridad para describir lo que existe hoy:** (1) `db/esquema.sql` y `src/leda/`; (2) `tests/` y
`db/pruebas.sql`, sólo con la ejecución y su resultado registrados; (3) `docs/architecture/frontera.md`, que
prevalece entre los documentos de arquitectura; (4) `docs/product/que-es-leda.md`; (5) los ADR aceptados, salvo
lo marcado como superado (los ADR 0013 y 0014 lo están en parte; lo que los ADR anteriores al Motor digan sobre
cómo conversa Leda no rige si contradice la constitución §8 o los ADR 0017 y 0018); (6) `docs/STATUS.md` y
`docs/ROADMAP.md`; (7) `README.md` y `PRUEBA-LOCAL.md`. `docs/product/functional-specification.md` es insumo
histórico. Una especificación no prueba implementación, un test no prueba nada hasta ejecutarlo, y una suite que
pasa no prueba que la conversación funcione.

**Al auditar, auditar contra este repositorio** (`nucleo/`, esquema, paquetes de espacio): un documento externo
es insumo, nunca el patrón contra el cual medir. Una auditoría que no leyó `nucleo/` entero no está terminada.

## Invariantes vigentes

- El aislamiento entre clientes es la garantía número uno. Ninguna tabla con alcance de espacio queda sin
  `workspace_id` ni sin `row level security` forzado, y ninguna función `security definer` sin propietario
  explícito y verificado. No depende de recordar un filtro manual.
- PostgreSQL es la fuente oficial del estado operativo.
- La conversación y la memoria ayudan a interpretar; no reemplazan una lectura vigente ni conceden autoridad.
- La IA sólo actúa mediante herramientas autorizadas del servidor.
- Los efectos relevantes requieren validación, confirmación cuando corresponda, ejecución única, verificación y
  auditoría.
- Los mensajes visibles salen por outbox; el ACK técnico de Telegram es la excepción acotada.
- Una solicitud incompleta es un borrador sin efectos. Una tarea comprometida exige objetivo, responsable, fecha
  objetivo, criterio de aceptación y política de evidencia; la conversión de borrador a tarea es explícita,
  confirmada y auditable. Una tarea que carga el administrador entra comprometida por declaración: se valida con
  los mismos datos, la auditoría separa quién la cargó y quién la decidió, y Leda nunca la presenta como una
  aprobación hecha en Leda (ADR 0017, decisión 2).
- Actualización, evidencia, aprobación y cierre son hechos distintos.
- No poder consultar datos no equivale a que no existan.

## Límites de alcance

Monolito modular en Python y PostgreSQL. Fuera del producto, salvo decisión explícita y documentada: agenda o
calendarios externos, aprendizaje persistente, motor genérico de workflows y microservicios. Precisiones:

- El motor de conversación no es un motor genérico de workflows: sus circuitos son un conjunto cerrado declarado
  en el código, nunca configuración de un cliente (ADR 0018, decisión 4).
- La plataforma web de tareas (cargar tareas, ver su estado, cambiar fechas por retrasos, gestionar integrantes)
  está dentro del alcance de esta etapa y se diseña en su propio ADR antes del código (ADR 0017, decisión 5).
- La memoria por integrante es aprendizaje persistente: tiene su lugar reservado y no se construye sin su propio
  ADR (ADR 0018, decisión 3). Leda puede aprender sola formas nuevas de decir algo que ya es una jugada; una
  jugada nueva la decide una persona, y el aprendizaje nunca cambia lo que Leda tiene permitido (decisión 1).
- La API de lectura y el dashboard están dentro del producto pero todavía no: esperan sus precondiciones (cierre
  del aislamiento y desacople del transporte) y el criterio del ADR 0017, decisión 5.

El Corte 0 del [ADR 0003](docs/decisions/0003-authenticated-inbound-boundary.md) (catálogo ejecutable de
propietarios, membresías, grants y ACL) no está diferido: es insumo del cierre del aislamiento entre clientes.

No cambiar lógica, esquema, dependencias o arquitectura durante trabajo puramente documental, ni reestructurar
carpetas o módulos sin un ADR aceptado.

## Comandos y operación

Los comandos están en `README.md`, `PRUEBA-LOCAL.md` y `src/leda/cli.py`; su resultado actual no se presume.
Corren el código de la carpeta donde se ejecutan (hoy, en `main` y en la rama del Motor, la conversación de los
flujos A y B, congelada). `python -m leda esquema --recrear` borra los datos: nunca sin autorización explícita y
un entorno descartable confirmado. El listener lo corre el usuario en su terminal; hay uno solo por bot.

## Reglas de seguridad

- No leer, imprimir, versionar ni incluir en diagnósticos archivos `.env*`, salvo la plantilla `.env.ejemplo`.
  Nunca mostrar secretos, tokens, credenciales, URLs privadas ni contenido sensible de conversaciones.
- No inspeccionar untracked antes de asegurar las exclusiones sensibles en `.gitignore`.
- No ejecutar SQL destructivo, pruebas contra una base no confirmada como descartable ni comandos de despliegue
  sin autorización.
- No registrar cuerpos de conversaciones ni errores crudos en documentación.
- No afirmar que una prueba, restore, backup o rollback funciona sin evidencia de una ejecución registrada.
- No hacer commits, cambiar configuración Git o agregar archivos al índice salvo pedido explícito. El usuario dio
  consentimiento permanente para los commits de cada unidad de trabajo y para las revisiones RDD (se aprueban
  sin preguntarle y se informa el resultado); los commits no llevan líneas de atribución; el push lo decide
  siempre el usuario.

## Cómo trabajar y registrar continuidad

Antes de implementar: confirmar que `docs/STATUS.md` sigue vigente, escribir el chequeo de rumbo (punto 3) y tener
el diseño aceptado (punto 12). Elegir el menor circuito útil de punta a punta, resolver sólo lo que lo bloquea, y
mantener juntos comportamiento, verificación, regresión y documentación. Registrar comando, resultado exacto,
escenario y límite de rollback.

**Hallazgos de conversación: reglas generales, no parches**
([ADR 0013](docs/decisions/0013-reglas-generales-de-la-conversacion.md)). Las variantes de una conversación son
infinitas; arreglar cada caso con frases o palabras clave no termina nunca. Leda cumple siempre: pregunta
pendiente como contexto, con una sola rama abierta a la vez; una respuesta visible por mensaje y por toque;
estado real y sólo opciones posibles; toque con señal e idempotente. Y además: botones para elegir, texto para
decir; los botones son atajos, también para confirmar, con una guarda (ADR 0018, decisión 2); un tema a la vez,
con tres salidas (ADR 0018, decisión 4). Ante un hallazgo:

- en un flujo congelado no se arregla;
- primero se escribe como conversación de prueba (punto 12) y después se resuelve en el motor de conversación
  como situación general, nunca como una rama para un camino;
- un "arreglo del mecanismo" dentro de una estructura equivocada también es un parche: no se agregan frases,
  palabras clave ni casos especiales;
- si una prueba real vuelve a fallar después de un arreglo, no se propone otro: se cuestiona el diseño (punto 4);
- si un hallazgo no entra en ninguna regla, se discute con el usuario una regla nueva antes de tocar nada.

### Cómo pensamos juntos (usuario y agente)

Acordado con el usuario el 2026-09-30 y actualizado el 2026-10-04. Cada vez que el proyecto subió de nivel fue
porque el usuario frenó y propuso mirar desde arriba; el agente, que empieza cada sesión de cero, corregía
hallazgo por hallazgo y parecía progreso. Por eso la señal de parar está escrita en el proceso.

1. **Roles complementarios.** El usuario aporta continuidad, contexto operativo y criterio de producto; el agente,
   razonamiento, conocimiento y velocidad. Ninguno tiene la razón por defecto.
2. **Toda propuesta se evalúa antes de ejecutarse**, contra el código y los documentos, con alternativas y sus
   costos, salvo que el usuario diga "hacelo sí o sí". Proporcional: en algo chico y reversible, la objeción en
   una línea; en lo que cambia producto, arquitectura o días de trabajo, se debate antes. Estar de acuerdo
   también se fundamenta.
3. **Chequeo de rumbo, escrito** en el documento de la unidad o en `docs/STATUS.md`, antes de una unidad o una
   ronda y al volver de cada prueba real: ¿qué clase de problema es y ya apareció antes? ¿mecanismo general o
   caso? ¿qué haría innecesaria la próxima ronda? ¿sigue valiendo la hipótesis? ¿es mecánico o puede ser más
   fluido, sin saltear garantías? ¿los datos y efectos salen de la cocina o le enseñamos frases al mozo? ¿qué
   conversación de prueba contra la IA real lo demuestra? Si una respuesta no convence, se para y se discute.
4. **Disparadores que obligan a parar:** un arreglo que agrega un caso especial; la misma función o camino tocado
   por dos arreglos seguidos; la misma clase de hallazgo en dos rondas; pruebas en verde y el usuario dice que se
   siente mal; un hallazgo que contradice un ADR vigente; una prueba real que vuelve a fallar después de un
   arreglo del mecanismo. Se revisa el mecanismo o el diseño, no el caso; con el último, no se propone otro
   arreglo.
5. **Probar en real enseguida.** Diseño corto y escrito; después, la porción más chica que se pueda llevar a
   Telegram real con datos ficticios. Las mediciones baratas corren en paralelo. La documentación registra
   decisiones y su porqué, no ensayos.
6. **Lo sólido no se simplifica.** La base, el aislamiento, las confirmaciones y la auditoría funcionan; ninguna
   "simplificación" (un framework de agente, SQL libre, reglas en el prompt en vez de garantías) los reemplaza.
7. **Un camino pasa al flujo nuevo sólo cuando se retiró lo viejo.** En el Motor, los flujos A y B se borran
   antes de construir el motor de conversación definitivo (Etapa 3), después de mudar las pruebas de garantías.
8. **Separar la IA del flujo.** Antes de culpar al flujo de una falla de comprensión, medir cuánto aporta la IA.
   La prueba chica arranca con GPT-6 sol y mide GPT-6 luna y Jev en paralelo (ADR 0018, decisiones 6 y 7).
9. **Funcionalidad nueva congelada** (ADR 0017, decisión 5): en esta etapa se construyen el seguimiento por chat
   y la plataforma web de tareas; lo demás va a la lista "Anotado para más adelante" del documento de la unidad
   hasta que Leda haga bien el seguimiento en pruebas reales. Lo que se pida de pasada se anota ahí.
10. **Proyectos externos: ideas, no bases** (`docs/research/`). Rasa quedó descartado como componente; Engram es
    sólo referencia de diseño para la memoria.
11. **La regla del mozo** (2026-10-03). La IA es el mozo: escucha, lleva el pedido exacto a la cocina (el código
    y la base) y cuenta con naturalidad lo que la cocina dice. No inventa datos ni efectos ni promete lo que la
    cocina no dijo; una propuesta suya es una sugerencia que la persona acepta; sus instrucciones describen su
    trabajo, sin reglas para casos ni frases de ejemplo; si dice algo mal, primero se mira si la cocina le pasó
    el hecho correcto; la cocina no corrige lo que el mozo escuchó con heurísticas. **Enmienda (ADR 0018,
    decisión 1):** la IA elige qué jugada corresponde, de una lista cerrada, y cómo decirlo; el código decide si
    vale, maneja cada jugada y cada situación general, y ejecuta.
12. **Diseño antes del código y evidencia real** (el método del Motor). Ningún código de conversación antes de
    su diseño escrito en un ADR y aceptado. Un hallazgo es primero una conversación de prueba, que pasa a ser su
    regresión. La evidencia de que la conversación funciona son conversaciones reales contra la IA real,
    corridas varias veces; ni una suite en verde ni la auditoría de otro agente lo muestran. Primero, una prueba
    chica y descartable con criterios de éxito y de corte escritos antes (ADR 0018, decisión 5).

### Al terminar una unidad y al cerrar una sesión

- Actualizar `docs/STATUS.md` ("Punto exacto para retomar", hechos, riesgos) y el documento de la unidad (tareas,
  evidencia, próximo paso). `AGENTS.md` sólo cambia si cambió una regla estable.
- Antes de cerrar la sesión, después de la última modificación, operación o commit, contrastar `docs/STATUS.md` y
  los documentos de continuidad con el estado real de Git, código, esquema, pruebas y operación. Si no cambió un
  hecho relevante, no editar documentación sólo para registrar la sesión. Si cambiaron los archivos importados,
  medir con `LC_ALL=C.UTF-8 wc -m` que lo que se carga al iniciar siga debajo de 150.000 caracteres.
- Marcar una prueba como ejecutada sólo con comando, fecha y resultado. Una prueba real, medición o auditoría de
  la conversación va a la bitácora de flujos, con la conclusión vigente si cambió.
- Antes de una prueba por Telegram real: espacio de prueba controlado, sin datos ni trabajo reales, secreto
  protegido, efectos inspeccionables y reversibles, respaldo, pausa o rollback proporcionados, ninguna operación
  destructiva y nada `CRITICAL` o `HIGH` abierto en el circuito. Si el circuito no cumple esas condiciones, se
  prueba con un arnés determinista o `TestClient` y se registra la condición pendiente.
- Inspeccionar respuesta visible, PostgreSQL, efectos y auditoría. Un hallazgo en la capa de garantías se corrige
  en su causa raíz con su regresión; uno de conversación va primero a una conversación de prueba.
- Un ADR numerado para cada decisión duradera de dominio o arquitectura; no borrar decisiones: registrar cuál
  reemplaza a cuál. Cuando `AGENTS.md` o `docs/STATUS.md` cambian de rumbo, la versión anterior se guarda literal
  en `docs/historial/`, con un aviso de archivo en su primera línea.
- Usar `PENDIENTE` para lo no comprobado o no decidido; no convertir hipótesis ni roadmap en estado implementado.
