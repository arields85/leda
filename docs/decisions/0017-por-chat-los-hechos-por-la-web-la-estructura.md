# ADR 0017: Por chat, los hechos del trabajo; por la web, su estructura

- **Estado:** en preparación con el usuario; `PENDIENTE` de aceptación (paso M1).
- **Fecha:** abierta el 2026-10-04.
- **Alcance:** qué atiende Leda por chat y qué queda por fuera del chat; la carga de tareas; el
  congelamiento de funcionalidad nueva y el orden del roadmap; el ajuste de `nucleo/` al recorte.
- **Evidencia:** decisiones del usuario del 2026-10-04 (`docs/STATUS.md`, "Resumen");
  `docs/research/gestion-del-dialogo-y-arquitecturas-de-agentes.md`;
  `odd/tasks/motor-de-conversacion.md`, "Preguntas a resolver con el usuario"; relevamiento del
  2026-10-04 de `sembrar` (`src/leda/siembra.py`) y `confirmar_borrador_tarea` (`db/esquema.sql`).

> **Cómo se lee este borrador.** El ADR se escribe con el usuario, una decisión por vez. Cada
> decisión lleva la fecha en que el usuario la tomó. Lo que figura como `PENDIENTE` no está
> decidido y no se actúa sobre ello.

## Contexto

El 2026-10-04 el usuario recortó el alcance: en esta primera etapa del Motor, Leda no crea tareas ni
objetivos por chat; hace seguimiento. Este ADR fija qué queda de cada lado.

## Decisiones

### 1. Un pedido de tarea nueva por chat se deriva (usuario, 2026-10-04)

Cuando alguien le pide a Leda por chat una tarea nueva, Leda no la crea ni guarda un borrador. Le
dice que las tareas nuevas no se cargan por chat, quién las carga y qué puede hacer por chat. No
tiene efectos.

- **Quién las carga sale de los datos**, no de un texto fijo en el código ni en las instrucciones de
  la IA (`AGENTS.md`, "Cómo pensamos juntos", punto 11). En esta etapa es el administrador de
  plataforma designado (decisión 2).
- **Es una persona concreta.** "Consultá con la administración" no alcanza: ningún mensaje deja a
  la persona sin un próximo paso (constitución §8).
- **Vale igual para un objetivo nuevo:** el recorte alcanza a los dos.
- **No cubre los cambios sobre una tarea que ya existe** (responsable, fecha, alcance): son las
  decisiones 3 y 4.

**Alternativa anotada, no adoptada ahora: Leda pasa el pedido.** Leda arma un mensaje para quien
carga las tareas y lo manda con la confirmación de quien pide. No se adopta porque:

- es un mensaje privado no rutinario, que exige borrador, confirmación y pregunta de atribución
  (constitución §7);
- necesita el mecanismo de avisos a otras personas, `PENDIENTE` en el ADR 0018;
- el pedido es casi un borrador de tarea: reabre por chat la estructura que el recorte saca.

Se reevalúa si una prueba real muestra que los pedidos derivados se pierden.

**Conversación de prueba:** `PENDIENTE` (tarea E1-3). Una persona del equipo pide una tarea nueva.

### 2. En esta etapa, las tareas las crea a mano el administrador (usuario, 2026-10-04)

En la primera etapa del Motor ninguna persona del equipo crea tareas. Las crea a mano el
administrador de plataforma designado. Las personas del equipo las cumplen y Leda hace el
seguimiento: recordatorios, cadencias, bloqueos. La carga de tareas no se diseña en esta etapa:
cuando Leda responda bien en el seguimiento, se le agregan capacidades.

Condiciones de la carga (usuario, 2026-10-04):

- **Valida los mismos datos que una tarea comprometida:** objetivo, responsable, fecha objetivo,
  criterio de aceptación y política de evidencia.
- **La auditoría guarda quién cargó y quién decidió según el archivo**, esto último como
  declaración. Leda nunca lo presenta como una aprobación hecha en Leda (constitución §4).
- **No hay circuito de aceptación por chat.** A lo sumo, Leda avisa a los responsables y referentes
  que se cargaron tareas. Si ese aviso entra, y con qué mecanismo, está `PENDIENTE` en el ADR 0018
  (avisos a otras personas).

**Anotado para más adelante: la aceptación dentro de Leda.** Quien decide las tareas las acepta en
Leda. Se retoma cuando exista el formulario web, que es donde se haría; nunca por chat.

### 3. Qué hace Leda por chat en esta etapa

#### 3a. El seguimiento persigue los bloqueos hasta quien puede destrabarlos (usuario, 2026-10-04)

Cuando alguien dice que está trabado, Leda no sólo anota el bloqueo: lo sigue de persona en persona
hasta llegar a quien puede destrabarlo, y mantiene la cadena conectada para que nada se atrase. En
palabras del usuario: unir todas las piezas del rompecabezas. Ejemplo:

1. Ismael: "No puedo avanzar, dependo de que Juan termine el cableado". Leda anota que Ismael está
   trabado por Juan.
2. Leda le pregunta a Juan cómo viene el cableado.
3. Juan: "No puedo avanzar, falta el repuesto". La cadena queda Ismael → Juan → repuesto.
4. Leda averigua quién se encarga de conseguir el repuesto: primero le pregunta a Juan y, si Juan no
   sabe, al referente del área.
5. Leda sigue a esa persona. Cuando el repuesto llega, avisa a Juan; cuando Juan termina, avisa a
   Ismael.

- **Si lo que falta no es una tarea de nadie, Leda sigue el bloqueo mismo.** Anota quién se encarga
  de destrabarlo y le hace el seguimiento a esa persona, sin crear una tarea (decisión 2). Un
  bloqueo y quién lo resuelve son hechos del trabajo.
- **Alternativa descartada:** pedirle al administrador que cargue una tarea para lo que falta y
  seguirla recién cuando esté cargada. Depende de la carga manual y demora justo cuando algo está
  trabado.
- **Qué existe hoy:** abrir y cerrar un bloqueo, las dependencias entre tareas, el aviso en cadena
  por atraso y el escalamiento de un bloqueo viejo ya funcionan. La conversación que pregunta,
  conecta y persigue no está construida (`docs/capacidades.md`, "Conversación de bloqueos").
- `PENDIENTE`: cómo se guarda quién se encarga de destrabar un bloqueo, y qué hace Leda si esa
  persona dice que no le corresponde.

**Conversación de prueba:** `PENDIENTE` (tarea E1-3). La cadena del ejemplo, de punta a punta.

#### 3b. Lo que hace Leda por chat en esta etapa (usuario, 2026-10-04)

Con una tarea cargada, en esta etapa Leda hace por chat estas ocho cosas:

1. Avisa un día hábil antes del vencimiento.
2. Anota el inicio cuando la persona dice que arrancó.
3. Persigue los bloqueos (3a).
4. Contesta qué tiene pendiente cada persona.
5. Pide el estado de las tareas según las cadencias del espacio (por ejemplo, los lunes).
6. Si pasa la fecha sin respuesta, recuerda y después escala al referente.
7. Recibe la entrega con su evidencia y pasa la tarea a revisión.
8. Recibe la aprobación, que cierra la tarea, o el pedido de cambios.

Lo que define la estructura del trabajo (crear, aceptar, reasignar) queda fuera del chat
(decisión 2). El pedido de más tiempo es la decisión 4.

### 4. Un pedido de más tiempo se anota y se avisa, sin cambiar la fecha (usuario, 2026-10-04)

Ejemplo: el 18, Ismael escribe "No llego al 20, necesito hasta el 27, el proveedor se demoró".

- **Leda anota la nueva previsión y su motivo** (el 27, el proveedor) como un hecho, y le avisa al
  referente. El mecanismo de avisos a otras personas está `PENDIENTE` en el ADR 0018.
- **La fecha comprometida no cambia:** sigue siendo el 20.
- **Los recordatorios siguen contra la fecha comprometida**, y la IA recibe como hechos la previsión
  y que el referente está avisado: no le habla a Ismael como si no hubiera dicho nada.
- **Si el referente acepta correr la fecha, la cambia a mano el administrador**, como la carga de
  tareas (decisión 2). Hoy esa operación no existe: la fecha de una tarea comprometida queda fija
  en el esquema. Cómo la cambia el administrador no se diseña en esta etapa.
- **Si el motivo es un bloqueo,** Leda además lo persigue (3a).

**Pendiente para el futuro, por pedido del usuario: Leda cambia la fecha con confirmación.** Leda
le pregunta al referente si acepta la nueva fecha y, si confirma, la cambia ella misma, con la
confirmación humana que la constitución §7 exige para un cambio de fecha objetivo. No se hace en
esta etapa: es cambiar la estructura por chat y la operación no existe.

### 5 a 7. `PENDIENTE`

5. El criterio del congelamiento de funcionalidad nueva y el orden del roadmap.
6. Qué le falta al seguimiento antes de usarlo: enlazar la respuesta con el recordatorio que la
   originó, seguir la falta de respuesta (`pending_reply`), la conversación de bloqueos
   (mecánica §8) y los textos de recordatorios y cadencias, hoy fijos en el código.
7. Cómo se ajusta `nucleo/` al recorte. Esa edición la hace el usuario.

## Consecuencias

- **Decisión 1:** Leda necesita el dato de quién carga las tareas. El camino no tiene efectos, así
  que puede entrar en la prueba chica de la Etapa 2 sin código de confirmación.
- **Decisión 2:** `sembrar` no cumple las condiciones de la carga: no hace las comprobaciones de
  `confirmar_borrador_tarea`, no registra quién decidió y su auditoría no dice quién lo corrió. Hoy
  es un cargador de datos ficticios.
- **Decisión 2:** al aceptar este ADR (tarea E1-4), la invariante de `AGENTS.md` sobre la
  conversión de borrador a tarea tiene que decir que una tarea cargada por el administrador entra
  comprometida por declaración, no por una confirmación en Leda.
- **Decisión 2:** la constitución §3 dice que los referentes aceptan las tareas de su área. En esta
  etapa, esa aceptación ocurre fuera de Leda y se declara. Cómo lo refleja `nucleo/` es la
  decisión 7; esa edición la hace el usuario.
- **Decisión 4:** cumple la primera mitad de la mecánica §9 (registrar la nueva previsión). La
  segunda (evaluar el umbral de re-aprobación) la hace el referente fuera de Leda en esta etapa.
  Cómo lo refleja `nucleo/` es la decisión 7.
