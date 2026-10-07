# El motor de conversación definitivo (Etapa 3 del Motor)

**Rama:** `feat/motor-de-conversacion` · **Carpeta:** `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`
**Abierta:** 2026-10-06 · **Copia en Engram:** tema `odd/motor-definitivo/tasks` (proyecto `prisma-pm`)
**Estado:** aceptado por el usuario (2026-10-06). Las decisiones que siguen marcadas `PENDIENTE` las
toma el usuario, una por vez, al llegar a ellas.

Plan propio de la Etapa 3 (`odd/tasks/motor-de-conversacion.md`, "Etapas y criterios de paso"). Las
decisiones duraderas están en los ADR [0017](../../docs/decisions/0017-por-chat-los-hechos-por-la-web-la-estructura.md)
y [0018](../../docs/decisions/0018-motor-de-conversacion.md), aceptado el 2026-10-06; la prueba chica, en
[`prueba-chica-del-motor.md`](prueba-chica-del-motor.md).

## 1. Objetivo y criterio de paso

Que la conversación de Leda en `src/leda` sea el motor del ADR 0018 y nada más. Para eso:

- se cortan los enredos entre la capa sólida y el código viejo;
- las pruebas de garantías se mudan a archivos limpios;
- los flujos A y B se borran;
- recién entonces se construye el motor, con lo aprendido en la prueba chica.

**M3** (`docs/STATUS.md`): motor construido, flujos viejos borrados, garantías en verde y prueba real
aprobada. Con M3, `main` recibe la rama.

## 2. Chequeo de rumbo (2026-10-06)

- **Clase de problema:** no es un hallazgo de conversación. Es mudar un diseño ya probado a su lugar
  definitivo y retirar lo viejo. El riesgo conocido es reescribir y perder en el camino lo que funcionó.
- **Mecanismo o caso:** mecanismo. Las 17 conversaciones de prueba y su corredor pasan a ser la regresión
  del motor definitivo. Corren antes de borrar `prueba_chica/` y otra vez sobre el motor nuevo.
- **Qué haría innecesaria la próxima ronda:** que sumar un circuito sea declarar su ficha y escribir su
  conversación de prueba, sin tocar el motor.
- **Hipótesis:** la de la prueba chica se sostuvo (bitácora, "Prueba por Telegram real del flujo D"). La
  nueva: el motor definitivo, con los mismos contratos, da el mismo resultado sin el andamiaje de la prueba.
- **Fluidez:** se mantiene lo que funcionó: sin botones salvo para elegir y escritura libre. Entra la regla
  de hablar del mundo y no de la cocina.
- **Cocina o frases al mozo:** cocina. Ningún arreglo agrega frases.
- **Qué conversación real lo demuestra:** la misma guía de la E2-9, repetida por Telegram sobre el motor
  definitivo.

## 3. Lo que se sabe hoy (relevamiento del 2026-10-06)

- **Los cinco enredos siguen** (`motor-de-conversacion.md`, "Enredos a cortar"):
  - (1) entregar crea estado que sólo `gateway` resuelve: `herramientas._notificar_entrega_al_aprobador`;
  - (2) el despachador arma botones y retiene mensajes según las ramas de los flujos A y B
    (`despachador._botones`, `_retener`);
  - (3) `huerfanos.py` importa tres símbolos de `gateway`. Por eso `ciclo` y `reloj`, que figuraban como
    sólidos, alcanzan `gateway`;
  - (4) la entrada HTTP vive en `gateway.py`;
  - (5) `tests/conftest.py` parchea `gateway`. 54 archivos de prueba dependen de él, y las garantías de
    aislamiento, RLS y paridad de migraciones están en `tests/test_task_intake.py`.
- **Lo que se borra:** unas 8.700 líneas.
  - `gateway.py` (salvo la entrada HTTP), `ingreso_tareas.py`, `agente.py`, `contexto.py`,
    `respuesta_unica.py`, `deteccion_pregunta.py` y `jev.py`;
  - `huerfanos.py`, según la decisión de E3-2;
  - `local.py`, que se reemplaza por la entrada del motor;
  - las cinco tablas `task_intake_*`.
- **Lo que trae la prueba chica:** el diseño, no el código. `prueba_chica/` se borra entero
  (`prueba_chica/README.md`). Se traen:
  - las fichas y jugadas, el estado por persona y el registro de turnos;
  - los avisos guardados con sus reintentos, la escalera propia y el reloj de Leda;
  - el corredor con las conversaciones YAML, el lector y la prueba de frontera.
  - Las migraciones `0030` y `0031` ya son del producto y se quedan.
- **Circuitos del ADR 0017 (3b) que la prueba chica no cubrió:**
  - 5, el pedido de estado de las cadencias;
  - 7, la entrega con evidencia;
  - 8, la aprobación o el pedido de cambios;
  - la persecución completa de un bloqueo (3a).

## 4. Tareas

Ruta y disparadores de delegación por tarea, como pide el método; cada una cierra con su commit y su
revisión por tramos.

- **Rutas:** E3-1 a E3-4 y E3-6, delegadas a un escritor, porque tocan muchos archivos no triviales. E3-5,
  E3-7 y E3-8, según su tamaño al llegar.
- **Entrega:** `main` no recibe nada hasta M3 (usuario, 2026-10-06). Las porciones son los commits de
  cada tarea, revisados por tramos desde el último revisado.
- **RDD apagado para los borrados puros** (usuario, 2026-10-06, `gentle-ai review mode disable --scope
  clone`). Los commits que sólo borran código viejo (`6a0d9ee`, `81da712`, `03c941e` y `d002c99`) exceden
  al revisor y aportan poco a la revisión. Quedan sin revisar por decisión del usuario. Se vuelve a
  prender (`enable --scope clone`) para el código que agrega o cambia comportamiento: la migración 0032
  y la Fase B.
- **Previsión:** la Fase A borra mucho más de lo que escribe. La Fase B ronda las 4.000 líneas, por
  referencia a la prueba chica sin su andamiaje.

**Fase A. Limpieza, sin cambiar el comportamiento de las garantías.**

- [x] **E3-1. Las pruebas de garantías en archivos limpios.** Aislamiento y RLS, paridad de migraciones,
      vista previa con huella y ejecución única, outbox, auditoría e idempotencia de toques y mensajes.
      `tests/conftest.py` deja de importar `gateway`. Criterio: esas pruebas pasan sin importar `gateway`,
      `ingreso_tareas` ni `agente`, y su número no baja frente a la línea base (`2286 passed`).
      **Hecho (2026-10-06), delegada a un escritor.**
      - 80 pruebas pasaron a `tests/garantias/`. Son movidas, no copiadas. `test_vista_previa_confirmacion`
        sólo cambió la preparación: ahora usa `herramientas.ejecutar` y `pendientes.registrar`, en lugar de
        `agente`. Sus comprobaciones son las mismas.
      - Los dos fixtures automáticos de `conftest` no importan `gateway` ni `huerfanos` cuando la prueba es
        de garantías.
      - Hay cuatro pruebas de frontera nuevas: una revisa los imports, incluso los de adentro de funciones;
        otra corre `tests/garantias` en un subproceso y exige que no se carguen los módulos viejos.
      - Evidencia:
        - Prueba de frontera en rojo antes del cambio de `conftest`: `1 failed, 3 passed`.
        - Suite completa antes: `2306 passed, 333 deselected, 1 warning in 853.80s`.
        - Suite completa después: `2310 passed, 333 deselected, 1 warning in 837.96s`, las mismas más las
          cuatro nuevas.
        - `pytest tests/garantias`: `84 passed`, repetido por el agente principal (95 s).
      - Quedan afuera, con su motivo:
        - Unas 22 pruebas de borrador y compromiso de `test_task_drafts.py`. Pasan por
          `crear_borrador_tarea`, que importa `ingreso_tareas` adentro de la función; se mudan cuando
          E3-4 saque esas constantes.
        - Las de las tablas `task_intake_*`, que se van con el flujo A.
        - Toque idempotente, mensaje repetido y una respuesta, que viven en `gateway` y se rehacen en
          E3-7.
        - `test_tablero.py`, que usa `gateway.app` y se resuelve en E3-2.
      - **Commits:** `0878774`, `409bcf0`, `7430227`, `a94dc18`, `24f8184` y `d0dc25b`. Son el commit único
        partido, porque entero excedía al revisor. El árbol final es idéntico.
      - **Revisiones RDD**, una por porción, en una carpeta temporal: `review-e1bf029b10af9371`,
        `review-479495d38a9d816d`, `review-fd4f99bf05a6275f`, `review-7e46ba5f58814a99` y
        `review-67b04fa09a959e61`. Todas aprobadas y reconocidas. `d0dc25b` queda pendiente para el
        próximo tramo.
      - **Observaciones para tareas siguientes:**
        - `test_vista_previa_confirmacion` registra la acción pendiente por su cuenta, copiando lo que
          hacía `agente`, con la vigencia de 8 h repetida. En la E3-6 tiene que usar el camino real del
          motor.
        - `test_aislamiento` usa el fixture `intake_world`; en la E3-4, que no se borre con el flujo A.
        - `test_migraciones` importa `tests.historia_previa_a_leda`; anda porque pytest corre desde la
          raíz.
- [x] **E3-2. Enredos 3 y 4.** La entrada HTTP (`/telegram/{slug}`, `/tablero/{token}`, `/salud`,
      webhooks) sale de `gateway.py` a un módulo propio. `huerfanos.py`: la garantía se queda, porque un
      mensaje que quedó sin respuesta por una caída se vuelve a procesar y nunca se pierde en silencio. Su
      versión atada a `gateway` se retira, y el motor la rehace en su entrada (E3-7). Es decisión del
      agente, por la regla de no fallar en silencio.
      **Hecho (2026-10-06), delegada a un escritor.**
      - La entrada HTTP está en `src/leda/entrada.py`: la app, las rutas `/telegram/{slug}`,
        `/tablero/{token}` y `/salud`, y los webhooks. `gateway.app` es un alias de esa app.
        `/telegram` le pasa el mensaje a `gateway.webhook` con un import dentro de la función; ese
        borde se reemplaza en la E3-7.
      - `huerfanos` importa de `entrada` los cuatro símbolos que usaba. El cuarto, `sql_respondido`,
        venía de `respuesta_unica`; la copia que quedó ahí se borró.
      - `ciclo` y `reloj` ya no alcanzan el código viejo al importarse.
      - `cli` arranca `leda.entrada:app`.
      - La prueba del tablero pasó a `tests/garantias/test_tablero.py`.
      - `tests/garantias/test_frontera_de_la_entrada.py` tiene seis pruebas. Los bordes que quedan, todos
        dentro de funciones, son cuatro: `entrada.webhook` hacia `gateway`, de la E3-7;
        `despachador._botones` y `pendientes.ver_rama_abierta` hacia `ingreso_tareas`, de las E3-3 y
        E3-4; y `herramientas.crear_borrador_tarea`, de la E3-4.
      - Evidencia:
        - La frontera nueva en rojo antes del cambio: `4 failed, 2 passed`.
        - `pytest tests/garantias`: `105 passed`.
        - Suite completa: `2316 passed, 333 deselected, 1 warning in 845.33s`, es decir 2310 más las 6
          nuevas.
        - `import leda.ciclo` no carga ningún módulo viejo.
        - Después de borrar la copia: garantías, una respuesta y huérfanos, `175 passed`.
      - Commits `3b5eb9f` y `09a1111`. Revisión `review-03c2a8fcefc22a0e`, aprobada y reconocida; base
        `24f8184`, el tramo incluye `d0dc25b` y `f063874`.
- [x] **E3-3. Enredos 1 y 2.** El despachador queda como transporte: sin botones ni retenciones de los
      flujos viejos. La entrega deja de crear estado de conversación; se rediseña con los circuitos 7 y 8.
      **Se hace junto con la E3-4** (decisión del agente, 2026-10-06). Si se cortaran primero, los flujos
      viejos quedarían rotos y sus pruebas en rojo hasta borrarlos. Se borran los flujos y, en el mismo
      movimiento, lo que en la capa sólida sólo les servía a ellos, en commits que dejan la suite en
      verde.
      - Hasta la E3-7, Leda no conversa: la ruta `/telegram`, el registro de webhooks y `local.py` salen
        con los flujos, y la entrada del motor los reemplaza.
      - No afecta a nadie: no hay equipo real, y `main` no recibe nada hasta M3.
      - `prueba_chica/` sigue andando: lo que use de lo borrado (por ejemplo, Jev, ya retirado) se le
        quita.
- [x] **E3-4. Borrar los flujos A y B**, con sus pruebas (se retiran con su código) y una migración que
      borra las tablas `task_intake_*`, con rollback. El banco `tests/banco/` prueba los flujos viejos y se
      retira con ellos. Criterio: suite en verde y ningún import de lo borrado.
      **E3-3 y E3-4 hechas (2026-10-06)**, delegadas a dos escritores, con un mapa previo de un
      explorador.
      - **Commits:**
        - `fd919ed`: Jev fuera de la prueba chica.
        - `6a0d9ee`: el banco viejo.
        - `81da712` y `03c941e`: las pruebas de los flujos.
        - `d002c99`: los ocho módulos, la ruta `/telegram`, el registro de webhooks y `cli escuchar` y
          `correr`.
        - `95f4c5a`, `b4ae70f`, `472ac22` y `6cf0782`: la limpieza de la capa sólida, partida en cuatro.
        - `0a5390b`: la migración `0032`, que borra las cinco tablas `task_intake_*`, la columna del
          outbox y su restricción, y redefine `confirmar_borrador_tarea`.
        - `e7f2eed`: las pruebas de borradores, a `tests/garantias/test_borradores.py`.
        - `52909f0`: README, PRUEBA-LOCAL, capacidades y frontera. Se borró `tools/medir_modelos.py`.
      - **Qué quedó:**
        - El despachador es transporte: sin retención por ramas, y con los botones de copiar y de
          acción pendiente.
        - El aviso de entrega al aprobador sale sin el menú viejo, como aviso de coordinación.
        - `llm` conserva sólo lo que usan `cli` y la prueba chica.
        - `huerfanos` se queda: es la garantía de no fallar en silencio, y queda inactivo hasta que el
          motor vuelva a recibir mensajes.
        - Hasta la E3-7, Leda no conversa.
      - **Evidencia, la suite completa por porción:**
        - 2316 al empezar.
        - 1928 sin el banco (0 deselected).
        - 1675 y 912 sin las pruebas de los flujos.
        - 849 sin los módulos.
        - 626 después de la limpieza.
        - Al final, 626 passed; `tests/garantias` 139 (repetido por el agente principal); `prueba_chica`
          410.
      - **Revisiones:**
        - `review-3ab131579ae22f62` (Jev).
        - Limpieza: `review-4ba85c420eef8e2f`, `review-de6bef5bc667d393`, `review-1e436b587bf08e95` y
          `review-dc5f902a0a66d06b`.
        - Migración y borradores: `review-5bd666e70e446bd5`.
        - Todas aprobadas y reconocidas.
        - Los cuatro borrados puros quedan sin revisar, por decisión del usuario: RDD estuvo apagado
          para ellos y se volvió a prender.
        - La limpieza se partió en cuatro reescribiendo commits sin subir. El árbol final es idéntico
          (etiqueta local `respaldo-antes-de-partir-limpieza`).
      - **Pendientes:**
        - Cancelar un borrador no deja fila de auditoría. Antes sólo la dejaba el camino del alta; ver
          con la plataforma.
        - `0032` se niega a correr con filas en `task_intake_request`, como la `0002`.
        - `pending_action.modificar_pedido_en` y `modificacion_consumida_en` siguen, porque las escribe
          `resolver_pendiente`.
        - Cuatro columnas que sólo escribe el SQL quedaron declaradas en `test_capacidades`.
        - `despachador._preview_vigente` todavía lee `task_draft`.
        - El escalón del incidente de `pending_action` y las etapas viejas de `incidentes` quedan por
          los incidentes históricos.

**Fase B. El motor definitivo.**

- [x] **E3-5. El paquete del motor** en `src/leda`, con su prueba de frontera (lista permitida de módulos
      y de tablas; bordes conocidos que sólo achican).
      **Decisiones técnicas (agente, 2026-10-06, con el mapa de la prueba chica):**
      - **Primero, la auditoría en la cocina.** Desde que se borró `agente.py` (`d002c99`),
        `herramientas.ejecutar` no deja ninguna fila en `audit_log`; antes la dejaba `agente`, con
        `pack_hash` y `nucleo_hash`. Vuelve a `herramientas.ejecutar`, con su prueba en
        `tests/garantias`, en rojo antes del arreglo. Lo que el motor escribe directo (previsiones,
        quién destraba, avisos) audita con el mismo ayudante. Es la segunda entrada de la prueba real.
      - **Paquete `src/leda/motor/`.** `escalera.py`, `reloj.py` y `ciclo.py` ya existen en `src/leda`:
        son la cadencia y la escalera viejas. Se retiran cuando el motor tenga su ciclo propio (E3-7),
        porque un camino nuevo entra sólo cuando se retiró el viejo (`AGENTS.md`, punto 7).
      - **Se porta el código de la prueba chica, limpiándolo.** Es el camino más fiel a lo que pasó la
        prueba. `prueba_chica/` queda intacta hasta la E3-8.
      - **Capas:**
        1. Contratos y partes puras: `tiempo`, `ia`, `ancla`, `cambios_de_estado`, `preguntas`,
           `instrucciones` y un `registro` nuevo con el registro de turnos. Ese registro corta el
           ciclo `turno` → `efectos` → `avisos` → `turno`.
        2. Turnos: `fichas`, `situaciones`, `hechos`, `avisos`, `efectos` y `turno`.
        3. Tiempo y afuera: `escalera`, `botones`, `ciclo`, `reloj` e `ia_real`.
      - **El SQL del motor no se junta en un solo módulo.** Son unas 130 consultas en 12 módulos, y
        juntarlas arriesga cambiar lo que funcionó. La garantía que buscaba esa regla la da la prueba de
        frontera, con una lista permitida de tablas que revisa el SQL de cada módulo del paquete.
      - **Las pruebas del motor van en `tests/motor/`.** Las auxiliares compartidas van en un módulo
        propio, y no importando un archivo de prueba desde otro.
      - **Un solo corredor para los dos motores:** el corredor y las conversaciones YAML se mudan con un
        parámetro para elegir el motor (`prueba_chica` o `leda.motor`), para la regresión de la E3-8.
      **Hecha (2026-10-06), delegada a un escritor.**
      - `d9517d5`: la auditoría vuelve a la cocina. Cada llamada a `herramientas.ejecutar` deja una fila
        con la versión de las reglas, en la misma transacción que el efecto.
        - Es la semántica vieja de `agente`: `herramienta:<nombre>` cuando se ejecutó, también una
          consulta; `herramienta_rechazada:<nombre>` en un rechazo de negocio; nada cuando quedó
          negado o esperando una confirmación.
        - Ahora lleva además el sujeto y si hubo confirmación.
        - Las huellas viven en `src/leda/versiones.py`.
      - `be0f0a3`: el paquete `src/leda/motor/` con la capa 1 (`tiempo`, `ia`, `ancla`,
        `cambios_de_estado`, `preguntas`, `instrucciones` y `registro`). Sus pruebas están en
        `tests/motor/`, con una frontera de módulos y de tablas permitidas, y una prueba fija la huella
        de las instrucciones de la IA que pasaron la prueba real.
      - `12e63d9`: si falta un archivo del núcleo, la huella falla en vez de calcularse sobre nada.
        Viene de una advertencia de la revisión.
      - **Evidencia:**
        - La auditoría en rojo antes del arreglo: `4 failed, 2 passed`.
        - Suite completa: 674.
        - `tests/garantias`: 145 al cerrar el commit `be0f0a3`, y uno más con `12e63d9`.
        - `tests/motor`: 42.
        - Garantías y motor, después de `12e63d9`: 188.
        - `prueba_chica`: 410.
      - **Revisiones:** `review-fb5aae5abbb4e2a8` y `review-6e0da2c028ca5d98`, aprobadas y reconocidas.
- [x] **E3-6. Mudar el diseño probado:** estado, registro de turnos, fichas de los circuitos probados,
      avisos guardados, escalera y reloj. Entran las dos entradas de la prueba real: hablar del mundo y no
      de la cocina, con su conversación de prueba escrita primero; y los efectos en `audit_log` con la
      versión de las reglas.
      **Portado (2026-10-06 y 07), delegado a dos escritores.**
      - **Capa 2:** `4e3c16d` (jugadas, situaciones y hechos), `fd8f833` (turno, avisos y efectos) y
        `8d6d195` (pruebas por el turno). Revisiones `review-9b72635703d52896`,
        `review-f713d77c04cb3163` y `review-4edb74708eee992b`.
      - **Auditoría de lo que el motor escribe directo:** `59cf884` (`motor/auditoria.py`). Se auditan
        las previsiones, sus correcciones, quién destraba, el avance y cada aviso que sale. No se audita
        la conversación, que ya está en el registro de turnos. Revisión `review-ea83c61eeba28416`.
      - **Capa 3:** `3025384` (escalera, botones, ciclo y reloj, con `python -m leda.motor.reloj`),
        `34f3336` (pruebas por la escalera) y `3d51094` (cliente real de la IA; `llm.tiempos` pasa a
        público). Revisiones `review-f1e7ebdcd9a28451`, `review-2978709cb62e3a74` y
        `review-d0e2467fbbdb4240`. Todas aprobadas.
      - **Diferencias con la prueba chica:** ninguna en comportamiento, salvo la auditoría.
      - **Arreglo de la fecha:** `8edd1fc` le da a la IA la fecha de hoy en la zona del espacio, no en
        UTC (de noche se contaba un día de más). Viene de una advertencia de revisión. La prueba nueva
        falló primero: `assert '2026-10-06' == '2026-10-05'`.
      - **Evidencia:** `tests/motor` 363; suite completa 995, más 1 con el arreglo; `tests/garantias`
        146; `prueba_chica` 410.
      - **Hablar del mundo y no de la cocina (2026-10-07):**
        - `c0ccaf1`: la conversación de prueba 18, escrita primero.
        - `9c83ead`: el arreglo en la cocina, como regla general.
          - Los hechos de un aviso dicen `llega`: cuándo le llega a quien lo recibe, o `ya_le_llego`,
            `no_le_va_a_llegar` (con su motivo) o `no_le_llego`. Desaparecen los estados internos y `sale`.
          - Lo anunciado que ya no pasa se llama `ya_no_va_a_pasar`.
          - La instrucción de redacción describe el trabajo: contar qué pasa en el mundo, nunca cómo
            funciona el sistema por dentro, y en futuro lo que todavía no pasó.
        - **Evidencia con GPT-6 sol:** en rojo, la 18 falló en las 5 corridas; en verde, 5 de 5. La
          regresión de las 18 conversaciones dio 90 de 90 en garantías y 89 de 90 en comprensión, con
          5,4 s de mediana y 12,9 s la más lenta.
        - **La falla de la regresión, en la conversación 08:** una fecha a 15 días, cuando la lista de
          días que recibe la IA llega a 14 (`DIAS_PROXIMOS`). Es previa al cambio; en la ronda 3 ese
          paso dio 5 de 5. Queda para mirar en la comparación de IA.
        - **Gasto:** unos USD 3,36. Quedan unos USD 6,2 de crédito en OpenRouter.
        - **Revisiones:** `review-4398edb6b3eba398` y `review-08872659140a6e5d`, aprobadas. Quedan
          tres advertencias de honestidad en casos de borde para mirar antes de M3: un aviso guardado
          cuya hora ya pasó (`avisos.py`), el aviso al administrador y los códigos de `hechos`.
      - **El corredor, mudado (2026-10-07):** está en `tests/conversaciones/`
        (`python -m tests.conversaciones.correr`), con `--motor leda.motor|prueba_chica` y `--ia`
        para cualquier proveedor y modelo. Lo de `nan` queda con precio desconocido.
        - Commits `b94247e`, `34adf8f`, `fb4754a` y `4271efb` (informes).
        - Ronda en seco con la IA guionada: 85 de 85 en los dos motores.
        - Revisiones `review-00e186be5d35696a`, `review-b3cba4591a49db01` y
          `review-3c1620b13c66e741`, aprobadas.
      - **Pendiente:**
        - Dos pruebas del escuchador esperan la E3-7.
        - Una prueba de `prueba_chica` falló una vez sin explicación y pasó al repetirla
          (intermitente, sin identificar).
- [x] **E3-7. La entrada del motor:** escuchador y webhook propios, sin `gateway`.
      **Hecha (2026-10-07), delegada a un escritor. Leda vuelve a conversar.**
      - `075bd9c`: el escuchador del motor (`motor/escucha.py`, `cli escuchar <slug>`). Lo que pasa con
        cada mensaje vive en `motor/recibir.py`, compartido con el webhook.
      - `3a1be85`: la ruta `POST /telegram/{slug}`, `python -m leda webhooks`, y `servir` corre el ciclo
        del motor de cada espacio activo (`motor/fondo.py`).
        - El secreto del webhook es propio de cada bot: un HMAC del secreto general y el espacio. Sin
          secreto configurado, el webhook rechaza todo.
      - `c5d7c88`: el barrido de mensajes sin respuesta corre en cada vuelta del ciclo del motor.
        - Los mensajes entrantes llevan la hora de la base, que es la que usa el barrido.
        - El texto fijo de un turno caído cuenta como su respuesta, para que no salga un segundo aviso.
        - El turno toma el mismo candado que el barrido.
      - `829ca4b`: las pruebas del despachador, fuera de la prueba vieja del ciclo.
      - `e4213e5`: se retiran `escalera.py`, `reloj.py`, `ciclo.py` y `cli cadencia` y `escalera`.
        La cadencia vuelve con el circuito 5, después de M3.
      - `4529c6e`: README y PRUEBA-LOCAL.
      - Si no hay IA configurada, la persona recibe el texto fijo y queda un incidente. Un espacio sin
        token de bot deja un incidente nuevo, `motor_sin_bot`.
      - **Evidencia:**
        - Antes del cambio, el webhook dio `1 failed, 13 errors` y el barrido `3 failed, 3 passed`.
        - Suite completa: 1060.
        - `prueba_chica`: 356.
        - Ronda en seco: 18 de 18.
      - **Pendiente:** `apscheduler` en `pyproject.toml` ya no lo usa nadie. El importador sigue
        cargando `cadence_job` para el circuito 5.
- [ ] **E3-8. Regresión y prueba real:** las 17 conversaciones, cinco veces con GPT-6 sol, y la guía de
      la E2-9 por Telegram. Después se borra `prueba_chica/`.
      **Comparación de IA** (pedido del usuario, 2026-10-06; el gasto en IA real está autorizado):
      - Las 17 conversaciones, cinco veces, sobre el motor definitivo terminado, con cinco IA:
        - GPT-6 sol, la referencia (85 de 85 en la ronda 3);
        - GPT-6 luna (`openai/gpt-6-luna`) y GPT-6 luna pro (`openai/gpt-6-luna-pro`), por OpenRouter;
        - DeepSeek flash (`deepseek-v4-flash`) y GLM 5.3 flash (`glm5.3-flash`), por el proveedor `nan`,
          no por OpenRouter.
      - Verificado el 2026-10-06:
        - Los dos modelos de `nan` responden.
        - GPT-6.1 luna no existe en OpenRouter. El usuario eligió luna y luna pro, que cuestan lo mismo
          por token (USD 0,10 de entrada y 0,50 de salida por millón), contra 2,00 y 10,00 de sol.
        - Crédito en OpenRouter: USD 9,75.
      - Se miden garantías, comprensión, latencia y costo, y el resultado va a la bitácora.
      - Luna se descartó en la ronda 1 (38 de 80), con el motor anterior a la revisión del contrato
        (ADR 0018, 9k y 9m).

**Fase C. Lo que la prueba chica no cubrió, después de M3** (usuario, 2026-10-06). Son los circuitos 7
y 8 (entrega y aprobación), el 5 (cadencias) y la persecución completa (3a). Cada uno lleva primero sus
conversaciones de prueba y después una pasada corta por Telegram. M3 es el motor definitivo haciendo bien
lo ya probado.

**La plataforma web va después de M3** (usuario, 2026-10-06). Reemplaza la decisión del mismo día de
escribir su ADR en paralelo con la Fase A. El porqué: mantener el foco en el motor y construir la
plataforma cuando Leda tenga una base más completa.

- **Para no rehacer:** cambiar una fecha, asignar o crear una tarea son una sola operación de la cocina,
  con su confirmación y su auditoría, y los dos canales la llaman.
- **El costo de esperar:** hoy no hay ninguno. Leda no se va a usar con un equipo real hasta que el
  usuario lo indique (2026-10-06); las pruebas usan datos ficticios.
- **Lo que dice el ADR 0017:** cambiar la fecha por chat está anotado para el futuro, con confirmación
  (decisión 4). Crear y asignar por chat quedan fuera del chat (decisión 2); si se quieren, llevan su
  propio ADR.

**Avance de la E3-8 (2026-10-07):**
- **Regresión del motor definitivo con GPT-6 sol:** 89 de 90 con todo lo automático bien, 90 de 90 en
  garantías, 5,1 s de mediana (`ac24f67`).
- **Comparación de cinco IA,** en la bitácora de flujos ("El motor definitivo con cinco IA"). Se queda sol.
- **Parámetros por modelo** para el corredor y para producción: `444de7c`, `9bf64f2` y `a732017`, con las
  revisiones `review-20540c248f5c00d5`, `review-bae1ec2c67963df8` y `review-b54c532f98b721d7`.
- **Falta:**
  1. Decidir el mecanismo de las fechas a más de dos semanas. La IA sólo recibe los nombres de los días de
     las próximas 14 (`DIAS_PROXIMOS`) y pierde fechas más lejanas: es la misma clase de falla en dos
     rondas, un disparador de parar.
  2. Recrear `leda_motor` y hacer la prueba por Telegram del usuario (M3); recrear la base necesita su
     autorización.
  3. Borrar `prueba_chica/` después de M3.

## 4b. Guía de la prueba por Telegram (M3)

La misma prueba de la E2-9 (`prueba_chica/README.md`), sobre el motor definitivo.

**Preparación** (la hace el agente; recrear `leda_motor` necesita la autorización del usuario):

1. `pg_dump` de `leda_motor` a `db/respaldos/`. Después, borrar la base, crearla y cargarla con los pasos
   de la E2-9: `esquema`, `importar corework --activar`, `feriados`, `modelo openai/gpt-6-sol --proveedor
   openrouter`, `sembrar … corework.semilla-ficticia.yaml` y `administrador corework Ariel`.
2. Poner `aviso_previo_dias_habiles` en 3.
3. Las 12 tareas vencen 10 días corridos después de la siembra. **V** es ese día.

**Antes de empezar** (el usuario):

- Terminal 1: `.venv\Scripts\python.exe -m leda escuchar corework` (queda corriendo).
- Ariel, Ismael y Marcos: `/start` al bot del equipo del Motor. Ariel: un "hola" al bot de
  administración.
- Terminal 2, el reloj: `.venv\Scripts\python.exe -m leda.motor.reloj corework adelantar` lleva al
  día hábil siguiente, a las 10:00. Después de cada salto, esperar **dos minutos**: la escalera corre una
  vez por minuto real, y en la E2-9 un salto rápido se salteó un día.

**El hilo** (el mismo de la E2-9, con lo que cambió):

1. Reloj: adelantar un día. **Marcos:** "qué tengo pendiente?" → sus dos tareas, con estado y
   vencimiento.
2. **Ariel:** "arranqué con la integración de la comprimidora" → en curso, sin confirmación.
3. Reloj hasta V − 3 días hábiles → el aviso previo a Marcos y a Ariel, sin pedir respuesta.
4. Reloj hasta V → el primer pedido de estado.
5. **Marcos:** "con el PLC estoy trabado, me falta el cable de programación. comunicaciones la termino
   el <V + 5 días hábiles>" → el bloqueo y la previsión. Dice **que Ismael se va a enterar y cuándo**,
   sin "guardado", "en cola" ni "todavía no salió". Una sola pregunta: quién lo destraba.
6. **Marcos:** "qué más tengo?" → no pierde la pregunta abierta.
7. **Marcos:** "el cable lo trae Juan de compras" → anotado quién lo destraba.
8. Reloj un día → a Ismael le llega el aviso de la previsión, y a Ariel el segundo pedido.
9. **Marcos:** "llegó el cable" → el bloqueo se cierra; el PLC vuelve a asignada y no lo da por
   empezado.
10. Reloj un día → a Marcos, un pedido de estado del PLC; a Ariel, el tercero, que avisa que se va a
    enterar Ismael.
11. **Marcos:** "arranqué recién" → en curso.
12. **Marcos:** "la de comunicaciones me la podés pasar a Nahuel?" → lo decide Ismael; ofrece una fecha
    nueva.
13. Reloj un día → a Ismael le llega el escalamiento por Ariel, factual y sin culpar a nadie.
14. **Ariel:** "perdón, estuve a full. la integración la termino el <V + 5 días hábiles>" → anotado;
    dice cuándo se entera Ismael.
15. Reloj un día → a Ismael le llega el aviso.
16. **Escribir de noche** (lo nuevo desde la E2-9): con el reloj en tiempo real
    (`… reloj corework volver`) después de las 21, **Marcos:** "lo termino mañana" → la fecha anotada es
    la de mañana en Argentina, no la de pasado.
17. Al terminar: `… reloj corework volver` y Ctrl+C en el escuchador.

**Qué mirar:** que Leda no se pierda ni se trabe y que se sienta natural, como en la E2-9; que no hable
de la cocina; y que nunca diga que algo pasó si todavía no pasó.

## 5. Criterios de corte

Los del ADR 0018 (5c) siguen valiendo para el motor definitivo:

- un caso especial frena;
- una falla repetida después de un arreglo del mecanismo lleva a revisar el diseño, no a otro arreglo.

Además, si la regresión de las 17 conversaciones da peor que la ronda 3 de la prueba chica (85 de 85), no
se borra `prueba_chica/` hasta entender por qué.

## 6. Pendientes que este plan hereda

- Si se avisa que se cargaron tareas (ADR 0017, decisión 2).
- Qué pasa si quien destraba dice que no le corresponde (3a).
- La tensión entre preguntarle al referente y "Leda es la PM".
- Qué hace la persona con una tarea terminada antes del circuito de entrega.
- Cómo llega el tono de cada cliente a la IA.
- `avisos.espera_saber` con una tarea en revisión.
- `PENDIENTE` del roadmap: si el grafo de transiciones y el desacople del transporte van antes del
  seguimiento.

## 7. Próximo paso

Decidir con el usuario los `PENDIENTE` de las secciones 4 y 6 que bloquean el orden. El alcance antes de
M3 ya está decidido: la Fase C va después.
