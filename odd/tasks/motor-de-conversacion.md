# El Motor

**Rama:** `feat/motor-de-conversacion` · **Carpeta:** `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`
**Abierta:** 2026-10-04 · **Copia en Engram:** tema `odd/motor-de-conversacion/tasks` (proyecto `prisma-pm`)

**Qué es "el Motor"** (nombre elegido por el usuario el 2026-10-04): toda la línea de trabajo
nueva. Abarca la decisión de dejar de parchear la conversación, esta rama con los flujos A, B y
C congelados, el recorte de alcance (Leda hace seguimiento y por ahora no crea tareas ni
objetivos por chat), el motor de conversación propio y el método (diseño antes del código y
conversaciones reales como pruebas). "Flujo D" es sólo el nombre técnico de su mecanismo, para
compararlo con los flujos A, B y C.

Documento de la unidad. Junta el objetivo, el alcance, las etapas, las tareas y la evidencia.
Las decisiones duraderas van a los ADR 0017 y 0018; los resultados de cada prueba real, a
[`docs/product/bitacora-de-flujos.md`](../../docs/product/bitacora-de-flujos.md).

## Objetivo

Que Leda converse sobre el seguimiento del trabajo sin perderse ni trabarse, con un motor de
conversación chico, propio y único, apoyado sólo en la capa sólida (base, garantías, operaciones
del dominio, salida y auditoría).

## Problema y por qué

La conversación se manejaba con código escrito a mano por situación: unas 16.000 líneas, sin un
modelo de la conversación, con tres flujos conviviendo (A, B y C6) y pruebas que miraban el
código y no las conversaciones. Cada circuito abría casos nuevos y cada falla se arreglaba en
su camino. El 2026-10-04 la prueba real de la tarea 0-35 volvió a fallar con la misma clase de
falla y el usuario frenó el parcheo. El análisis y sus fuentes están en
[`docs/research/gestion-del-dialogo-y-arquitecturas-de-agentes.md`](../../docs/research/gestion-del-dialogo-y-arquitecturas-de-agentes.md).

## Decisiones del usuario que dan origen a la unidad (2026-10-04)

1. Motor chico de conversación dentro de Leda, sin marcos de terceros.
2. Engram no se usa como componente; su diseño es la referencia de una futura memoria por
   integrante en PostgreSQL. El motor de conversación tiene tres partes: estado exacto, registro completo de la
   conversación (con los toques de botones) y memoria (más adelante, con su ADR).
3. Recorte de alcance: por ahora Leda no crea tareas ni objetivos por chat; hace seguimiento.
   Principio: por chat, hechos del trabajo; por la web, su estructura.
4. Carga manual: primero una importación por archivo del administrador; después un formulario
   en el tablero del cliente.
5. Arranque limpio: esta rama sale de `main`; los flujos A, B y C1-C6 quedan congelados en la
   etiqueta `respaldo-flujos-antes-de-d` y no se arreglan.
6. Los botones son atajos: lo que hace un botón también vale escrito.
7. Un tema a la vez: ante un cambio de tema, Leda recuerda lo abierto y ofrece seguir, retomarlo
   después o cancelarlo. Nació en el alta por chat (tarea 0-36, detenida; su trabajo parcial
   quedó archivado en la etiqueta `respaldo-0-36-en-pausa`, sólo para consulta) y pasa al motor
   de conversación como situación general. La otra decisión de esa tarea, "Rechazar y
   cancelar", era del alta por chat y queda fuera del alcance por ahora.

## Reglas de trabajo de la unidad

- Diseño escrito y acordado con el usuario antes de cualquier código.
- Cada hallazgo de conversación se convierte primero en una conversación de prueba.
- Una suite en verde no es evidencia de que la conversación funcione: la evidencia son las
  conversaciones de prueba contra la IA real, corridas varias veces, y la prueba por Telegram.
- Una sola casa para los documentos: esta rama. `main` no recibe commits hasta M1.
- Migraciones nuevas desde `0030` (`0026` a `0029` son de la rama congelada).
- No se crea el paquete del motor de conversación ni su prueba de frontera antes de aceptar el ADR 0018.

## Chequeo de rumbo (2026-10-04)

- **¿Qué clase de problema ataca, y ya apareció antes?** La conversación manejada por ramas de
  código, sin estado explícito. Apareció en las rondas 1 a 4 (dio el ADR 0013), en el flujo de
  un mensaje (ADR 0014) y en C1-C6 (tareas 0-32, 0-34 y 0-35). Las tres veces frenó el usuario.
- **¿Mecanismo general o caso?** Mecanismo: un solo motor de conversación con estado explícito, circuitos
  declarados y situaciones generales resueltas una vez; y un cambio de método (diseño antes del
  código, conversaciones reales como pruebas).
- **¿Qué haría innecesaria la próxima ronda?** Que una situación nueva se resuelva en el motor de conversación
  para todos los circuitos y quede cubierta por una conversación de prueba; que sumar un
  circuito sea declararlo, no escribir ramas.
- **¿Sigue valiendo la hipótesis?** La del ADR 0014 sigue valiendo para datos y efectos: la IA
  interpreta, el código decide los efectos, la IA redacta desde los hechos. Lo que se revisa es
  quién lleva la conversación (ADR 0018). Hipótesis nueva, a probar en la Etapa 2: un motor
  chico con estado explícito elimina la clase "se pierde o se traba" con mucho menos código.
  Es una hipótesis, no un hecho.
- **¿Es mecánico? ¿Puede ser más fluido?** El recorte deja por chat lo que es conversación
  (informar un hecho, responder un recordatorio, pedir estado) y saca lo que es un formulario
  (cargar siete datos). La IA lleva la charla dentro de lo que el estado permite. Las
  confirmaciones de la constitución §7 se mantienen.
- **¿Cocina o frases al mozo?** Cocina: el estado, lo que se puede hacer y los efectos los
  calcula el código; a la IA no se le dan frases ni reglas de casos. Qué movimientos de la
  conversación decide la IA se fija en el ADR 0018, como enmienda explícita del punto 11 de
  `AGENTS.md`.

## Etapas y criterios de paso

| Etapa | Qué | Criterio de paso |
|---|---|---|
| 0 | Arranque limpio: etiquetas, cierre en `main`, rama y carpeta nuevas | Hecho (ver "Evidencia") |
| 1 | Diseño sin código: ADR 0017, ADR 0018, conversaciones de prueba | **M1:** el usuario acepta los dos ADR (el 0018 queda como "propuesta" hasta que pase la prueba); `main` avanza sólo con documentos |
| 2 | Prueba chica y descartable, por Telegram real, con tareas importadas y base `leda_motor` | **M2:** resultado registrado en la bitácora, pase o no, contra criterios escritos antes |
| 3 | Cortar los enredos, mudar las pruebas de garantías, borrar los flujos A y B, construir el motor de conversación y la importación real | **M3:** motor de conversación construido, flujos viejos borrados, garantías en verde, prueba real aprobada |

Las etapas 2 y 3 tienen cada una su plan propio, que se escribe al llegar.

## Tareas

Etapa 0:

- [x] **E0-1.** Sacar las líneas de atribución de los 19 commits sin subir de `main`.
- [x] **E0-2.** Etiquetas `respaldo-0-36-en-pausa`, `respaldo-flujos-antes-de-d` y
      `respaldo-main-antes-de-d`.
- [x] **E0-3.** Commit de cierre en `main` (bitácora, nota de investigación, `STATUS`,
      `ROADMAP`, `INDEX`, `AGENTS.md`).
- [x] **E0-4.** Rama y carpeta nuevas; ADR 0016 y `nucleo/personalidad.md` traídos de la
      etiqueta; migraciones `0026` a `0029` reservadas; este documento.

Etapa 1 (ruta: en línea, con el usuario; son documentos de decisión):

- [ ] **E1-1.** ADR 0017, alcance: `docs/decisions/0017-por-chat-los-hechos-por-la-web-la-estructura.md`.
- [ ] **E1-2.** ADR 0018, motor de conversación: `docs/decisions/0018-motor-de-conversacion.md` (queda
      "propuesta" hasta que pase la prueba).
- [ ] **E1-3.** `tests/conversaciones/`: formato (README) y primeras conversaciones como datos.
- [ ] **E1-4.** Al aceptar los ADR: actualizar `AGENTS.md` (nombres, puntos 9 y 11),
      `docs/architecture/frontera.md`, `docs/product/que-es-leda.md`, `docs/capacidades.md`,
      `docs/ROADMAP.md`, `docs/INDEX.md` y la línea "superada en parte" de los ADR 0013 y 0014.

## Preguntas a resolver con el usuario

Una por vez. Para el ADR 0017:

1. Qué contesta Leda si alguien le pide una tarea nueva por chat (no puede dejar a la persona
   sin salida, constitución §8). **Resuelta (usuario, 2026-10-04):** Leda deriva, sin efectos;
   pasar el pedido queda anotado como alternativa (ADR 0017, decisión 1).
2. La importación del administrador: quién decide y quién aplica (constitución §2), formato,
   si se puede repetir, garantías de una tarea comprometida (objetivo, responsable, fecha,
   criterio y política de evidencia) y la aceptación del referente (mecánica §7 y §13).
   **Resuelta (usuario, 2026-10-04):** en esta etapa ninguna persona del equipo crea tareas; las
   crea a mano el administrador designado, con las condiciones del ADR 0017 (decisión 2). La
   carga no se diseña ahora: se agregan capacidades cuando Leda responda bien en el seguimiento.
3. Qué circuitos quedan por chat y cuáles pasan a la web (dependencias, cambios sobre una
   tarea ya creada). **Resuelta (usuario, 2026-10-04):** el seguimiento persigue los bloqueos de
   persona en persona y, si lo que falta no es una tarea de nadie, sigue el bloqueo mismo con
   quien se encarga de destrabarlo (3a); por chat entran ocho cosas, del aviso antes del
   vencimiento a la aprobación que cierra la tarea (3b). ADR 0017, decisión 3.
4. "Necesito más tiempo": hoy no existe la operación; la previsión se informa por chat y el
   cambio de fecha exige confirmación (constitución §7, mecánica §9). **Resuelta (usuario,
   2026-10-04):** Leda anota la nueva previsión y avisa al referente, sin cambiar la fecha; si
   el referente acepta, la cambia el administrador desde la plataforma. El referente se entera
   por chat y el pedido aparece además en la plataforma (ADR 0017, decisión 4).
5. El criterio del congelamiento de funcionalidad nueva, que nombraba el alta por chat.
   **Resuelta en parte (usuario, 2026-10-04):** en esta etapa se construyen el seguimiento y una
   plataforma web donde se maneja la estructura del trabajo (cargar tareas con un formulario, ver
   su estado, cambiar fechas por retrasos, gestionar integrantes); lo demás espera a que Leda
   haga bien el seguimiento en pruebas reales (ADR 0017, decisión 5). Quién entra a la
   plataforma se decide en su propio ADR. La prueba chica no espera a la plataforma: usa tareas
   ficticias cargadas con `sembrar`.
6. Qué le falta al seguimiento antes de usarlo: enlazar la respuesta con el recordatorio que la
   originó, seguir la falta de respuesta (`pending_reply`), la conversación de bloqueos
   (mecánica §8) y los textos de recordatorios y cadencias, hoy fijos en el código.

Para el ADR 0018:

1. Qué decide la IA y qué decide el código (enmienda de la regla del mozo).
2. Si una confirmación que crea o cambia algo vale escrita, con la guarda de que el resumen sea
   lo último que la persona vio y no haya cambiado.
3. La forma del estado explícito, del registro de turnos y el lugar reservado a la memoria.
4. Qué declara un circuito y cuáles son las situaciones generales.
5. Los criterios de éxito y de corte de la prueba chica, y su primera prueba real.
6. La IA: se sigue con GPT-6 sol; medir de nuevo luna con el motor de conversación (más barata
   y rápida).
7. Jev: medir cuánto aporta frente a la IA principal y retirarlo si no aporta.
8. Qué pasa cuando la IA no responde o falla (en la rama congelada eran las tareas P1-P7), y si
   se trae el mecanismo de avisos guardados como hechos con sus reintentos (ADR 0016), incluido
   qué pasa cuando un aviso a otra persona agota los reintentos.

## Anotado para más adelante

Capacidades que el usuario dejó para después de esta etapa: se retoman cuando Leda haga bien el
seguimiento en pruebas reales. Al aceptar el ADR 0017 pasan a `docs/ROADMAP.md` (tarea E1-4).

| Capacidad | Origen |
|---|---|
| Leda le pasa el pedido de una tarea nueva a quien la carga, con confirmación de quien pide | ADR 0017, decisión 1 (se reevalúa si una prueba real muestra que los pedidos se pierden) |
| Quien decide las tareas las acepta dentro de Leda, en el formulario web; nunca por chat | ADR 0017, decisión 2 |
| Leda le pregunta al referente si acepta una fecha nueva y, si confirma, la cambia ella misma | ADR 0017, decisión 4 (pedido explícito del usuario) |

## Decisiones que los ADR tienen que dejar escritas

1. **Reestructuración:** el paquete nuevo y la prueba de frontera necesitan el ADR 0018
   aceptado (`AGENTS.md`, "Límites de alcance").
2. **"Motor genérico de workflows":** los circuitos son un conjunto cerrado declarado en el
   código, nunca configuración del cliente.
3. **"Aprendizaje persistente":** la memoria espera su ADR. El registro de turnos entra en el
   ADR 0002 y la constitución §9; toda tabla nueva lleva `workspace_id` y RLS forzado.
4. **"Interfaz administrativa completa":** la importación es un comando de consola. El
   formulario posterior amplía el tablero del cliente y enmienda el ADR 0004,
   `que-es-leda.md` y la tabla de puertos.
5. **Autoridad de la importación:** quién decide y quién aplica; cumple la invariante de la
   tarea comprometida y la mecánica §13; no recibe el espacio de quien llama (regla 6 de la
   frontera).
6. **Congelamiento:** el seguimiento de la falta de respuesta, "necesito más tiempo", el
   enlace respuesta-recordatorio y la importación son funcionalidad nueva; el ADR 0017 redefine
   el congelamiento y el orden del roadmap.
7. **Regla del mozo:** el punto 11 dice que la cocina decide qué se pregunta; darle a la IA
   libertad para llevar la charla lo contradice tal como está escrito. Se enmienda de forma
   explícita.
8. **Reglas 2 y 3 de la frontera:** las tablas del motor de conversación no llevan `chat_id` ni
   `callback_data`; un toque se registra como una opción elegida; el motor de conversación queda detrás del
   puerto de intención.
9. **Flujos congelados:** los hallazgos C-1 a C-3 viven en código del despachador que se
   conserva; pasan a ser conversaciones de prueba, no arreglos de flujos viejos.

## Reglas del arranque limpio (las fija el ADR 0018)

- El motor de conversación vive en un paquete nuevo que sólo alcanza una lista permitida de módulos sólidos.
  La prueba recorre los imports en cadena, incluidos los que están dentro de funciones
  (`herramientas.py:778`, `pendientes.py:533` y `despachador.py:496` importan `ingreso_tareas`),
  con una lista de bordes conocidos que sólo puede achicarse (patrón de
  `tests/test_capacidades.py`).
- Lista permitida de tablas, con el SQL del motor de conversación en un solo módulo.
- Entrada propia: el motor de conversación no llama a `gateway.procesar_update` ni agrega interruptores.
- La prueba chica vive fuera de `src/leda`.
- Antes de construir el motor de conversación definitivo se cortan los enredos, se mudan las pruebas de
  garantías a archivos limpios y se borran los flujos A y B.

## Lo sólido que se reutiliza

- Operaciones del dominio: `herramientas.ejecutar(cur, quien, nombre, args, …)`
  (`src/leda/herramientas.py:532-598`), con `db.espacio()` y `autoridad.Solicitante`.
- Vista previa con huella: `Preparacion`, `pendientes.registrar` y `pendientes.resolver`, y la
  función SQL `resolver_pendiente`.
- Qué se puede hacer con una tarea: `menu_tarea.calcular_menu` (`src/leda/menu_tarea.py:113`).
- Lecturas: `src/leda/lectura.py`. Salida: `salida.enqueue_outbox` y `despachador.py`.
- Seguimiento: `escalera.py`, `reloj.py` y `ciclo.py`. Carga: `siembra.py` e `importador.py`.

Enredos a cortar en la Etapa 3 (verificados en `main`):

1. Entregar una tarea crea estado de conversación que sólo `gateway` sabe resolver
   (`herramientas.py:1361, 1987-2057`).
2. El despachador arma botones y retiene mensajes con código de conversación
   (`despachador.py:482-511, 626-653`).
3. El ciclo de fondo carga el código congelado (`huerfanos.py:64-66` importa `gateway`).
4. La entrada de un mensaje son funciones privadas de `gateway.py`, mezcladas con el flujo A
   (`gateway.py:377-612, 839-1042`); la aplicación HTTP también vive ahí.
5. Las garantías clave (aislamiento entre clientes, dueños de funciones, paridad de
   migraciones) se prueban dentro de `tests/test_task_intake.py`, y `tests/conftest.py`
   importa `gateway` en cada prueba.

## Qué se trae de la rama congelada

Propuesta inicial; se confirma en el ADR 0018. Todo está en la etiqueta
`respaldo-flujos-antes-de-d`.

| Pieza | Dónde | Propuesta |
|---|---|---|
| Orden de despacho y bloqueo por espacio | `despachador.py` (unas 25 líneas) y su prueba | Traer |
| Indicador de escritura después de retirar el borrador | `despachador.py` (unas 20 líneas) | Traer |
| Quitar botones vencidos y escribir la opción tocada | migración `0028`, `despachador.py` (unas 310 líneas) | Traer cuando el motor de conversación tenga botones |
| Avisos guardados como hechos, con reintentos (ADR 0016) | columnas de la `0029`, `salida.py`, `despachador.py` | Traer las columnas con una migración nueva; rehacer el redactor |
| Control contra datos inventados | `verificador_redaccion.verificar_afirmaciones` | Extraer |
| Contrato del aviso | `alta_turno.py` (`HechosAviso`, `verificar_aviso`) | Rehacer dentro del motor de conversación |
| Mejoras de `llm.py` | historial al ruteo, topes por modelo, `llamar_con_plazo`, llamada estructurada forzada | Traer por porciones |
| Respuesta en vivo (streaming) | `despachador.py`, `llm.py` | Decidir en el ADR; no entra en la prueba |
| Tono del cliente como instrucciones | `instrucciones.py` | Extraer |
| Área de los objetivos | migración `0027`, `importador.py` | Traer con la importación de tareas |
| Alta conversada y sus contratos | `alta_turno`, `alta_conducida`, `redaccion`, `resultado_turno`, `valores`, cambios del alta en `ingreso_tareas` y `gateway`, migración `0026` | No se trae |

Pendientes heredados de la rama congelada que `docs/STATUS.md` deriva a esta lista:

| Pendiente | Propuesta |
|---|---|
| Tope de salida por modelo (`llm.py`, `tope_ruteo` y `tope_conduccion`) | Traer con las mejoras de `llm.py` |
| Plazo total por llamada a la IA | Verificar contra el código antes de traerlo: las dos exploraciones del 2026-10-04 no coinciden sobre si `llamar_con_plazo` cubre todas las llamadas |
| Elección de la IA desde la plataforma | El comando `python -m leda modelo` ya existe en `main`; mantenerlo anotado en `docs/product/plataforma-pendientes.md` |
| `llm._limpiar_esquema` no limpia dentro de `items` (afecta a Gemini) | Corregir al traer la llamada estructurada, si se usa ese proveedor |
| Prueba intermitente del indicador de escritura | Revisar al tocar el despachador |
| `tools/medir_modelos.py` (importa módulos de la rama congelada) | Adaptar al contrato del motor de conversación cuando exista |
| `tools/restriccion_horario.py` (sólo admite `leda` y `leda_flujo`) | Admitir `leda_motor` en la Etapa 2 |

## Evidencia

- **E0-1 (2026-10-04).** `git filter-branch` sobre `aa32a02..main` con un filtro de mensajes:
  árbol de `main` igual antes y después (`4de063660864bbeb89c02647e09c2e8f4605181a`), 19
  commits sin subir, ninguno con líneas de atribución; la punta anterior quedó en
  `refs/original/refs/heads/main`.
- **E0-2 (2026-10-04).** `respaldo-0-36-en-pausa` apunta al commit del stash y conserva
  `tests/test_alta_un_tema_a_la_vez.py`; `respaldo-flujos-antes-de-d` apunta a `cc732dd`;
  `respaldo-main-antes-de-d` apunta al commit de cierre de `main`.
- **E0-3 (2026-10-04).** Commit de cierre de `main` (etiqueta `respaldo-main-antes-de-d`): 37
  archivos, sólo documentación, sin líneas de atribución. `AGENTS.md` y `docs/STATUS.md` se
  reescribieron enteros y sus versiones anteriores quedaron como copias en `docs/historial/`.
  - *Control de coherencia.* Un auditor independiente simuló el arranque de una sesión nueva.
    Primera pasada: tres hallazgos altos (el traspaso de la memoria seguía viejo; las carpetas
    congeladas cargaban instrucciones anteriores; los ADR 0013 y 0014 no decían qué quedó
    reemplazado) y seis medios. Segunda pasada, sobre lo corregido: ningún hallazgo alto;
    "es seguro etiquetar y abrir la rama".
  - *Carpetas congeladas.* `flujo-de-un-mensaje`, `alta-y-google`, `c4-medicion`, `flujo-c6` y
    `prueba-0-35` llevan como `AGENTS.md` un aviso de carpeta congelada (un commit en cada una).
  - *Revisión RDD.* El commit entero excedía el presupuesto del revisor
    (`lens_context_budget_exceeded`), así que se revisó en cuatro tramos sobre una carpeta
    temporal, con el mismo árbol final que el commit de cierre: linajes
    `review-d620b2bb22b7427d`, `review-8a63e809807fd809` (riesgo bajo, sin lentes),
    `review-ee3d1ae8de587d93` y `review-02333b9633db361d`, todos aprobados y reconocidos. Dos
    observaciones del revisor se corrigieron antes de etiquetar (qué se hace con un hallazgo
    en la capa de garantías, y una sola redacción del paso M1).
- **E0-4 (2026-10-04).** `git worktree add -b feat/motor-de-conversacion … respaldo-main-antes-de-d`:
  la rama nace sin diferencias con la etiqueta. Primer commit, sólo documentos: el ADR 0016 y
  `nucleo/personalidad.md` traídos sin cambios de `respaldo-flujos-antes-de-d` (más una nota en
  el ADR), los números `0026` a `0029` reservados en `db/migrations/README.md`, este documento
  y su importación en `AGENTS.md`. Revisión RDD de ese commit (`02fe502`, base
  `respaldo-main-antes-de-d`): linaje `review-cec1109be28beca9`, aprobada y reconocida. Tres
  sugerencias no bloqueantes: el ADR 0016 cita piezas que no existen en esta rama (lo dice su
  nota), las referencias de línea de este documento van a quedar viejas (conviene contrastar
  contra el símbolo) y la reserva de números de migración no tiene una prueba que la haga
  cumplir.
- **E1-1, en curso (2026-10-04).** Borrador del ADR 0017 con las decisiones 1 a 4, commit `3a96a3a`.
  Revisión RDD: el usuario aceptó revisar el rango completo que propuso el sistema (desde `aa32a02`,
  45 archivos y 4256 líneas, con el cierre de `main` ya revisado en tramos), y falló por tamaño
  (`lens_context_budget_exceeded`, linaje `review-91bc5e5ee5e6c06c`, sin autoridad creada). Lo
  posterior a la última revisión (`02fe502..3a96a3a`, sólo documentos, 207 líneas): `gentle-ai
  review assess` da riesgo `passive` y `review_due = false`, así que no requiere revisión.
- **Línea base de las garantías (2026-10-04).** `.venv\Scripts\python.exe -m pytest -q -p
  no:cacheprovider` sobre el código del punto de partida (`respaldo-main-antes-de-d`), corrido
  desde la carpeta de `main`: `2286 passed, 333 deselected, 1 warning in 631.96s (0:10:31)`. Mide
  el código, incluida la conversación congelada de los flujos A y B; no es evidencia de que la
  conversación funcione.

## Próximo paso

Cerrar el ADR 0017 con el usuario: la pregunta 6 (qué le falta al seguimiento) y la 7 (cómo se
ajusta `nucleo/`, que edita el usuario). Después, el ADR 0018. Las decisiones 1 a 5 ya están
escritas en el borrador del ADR.
