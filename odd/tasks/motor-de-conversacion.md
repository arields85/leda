# El Motor

**Rama:** `feat/motor-de-conversacion` · **Carpeta:** `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`
**Abierta:** 2026-10-04 · **Copia en Engram:** tema `odd/motor-de-conversacion/tasks` (proyecto `prisma-pm`)

Documento de la unidad: objetivo, etapas, tareas hechas y pendientes, evidencia y próximo paso. Las decisiones
duraderas están en los ADR [0017](../../docs/decisions/0017-por-chat-los-hechos-por-la-web-la-estructura.md) y
[0018](../../docs/decisions/0018-motor-de-conversacion.md); las pruebas reales, en la bitácora de flujos. La
versión hasta el paso M1, con las preguntas al usuario y la evidencia completa, está en
[`docs/historial/motor-de-conversacion-hasta-M1.md`](../../docs/historial/motor-de-conversacion-hasta-M1.md).

## Objetivo

Que Leda converse sobre el seguimiento del trabajo sin perderse ni trabarse, con un motor de conversación chico,
propio y único, apoyado sólo en la capa sólida (base, garantías, operaciones del dominio, salida y auditoría).

## Problema y por qué

La conversación eran unas 16.000 líneas escritas a mano por situación, sin un modelo de la conversación, con
tres flujos conviviendo y pruebas que miraban el código. El 2026-10-04 la prueba real volvió a fallar con la
misma clase de falla y el usuario frenó el parcheo (análisis en `docs/research/`).

## Decisiones del usuario que dan origen a la unidad (2026-10-04)

1. Motor chico de conversación dentro de Leda, sin marcos de terceros; Engram sólo como referencia.
2. Tres partes: estado exacto, registro completo de la conversación (con los toques) y memoria (después, con su
   ADR).
3. Leda hace seguimiento y no crea tareas ni objetivos por chat: *por chat, hechos del trabajo; por la web, su
   estructura.*
4. Carga de tareas: se pensó una importación por archivo; el ADR 0017 (decisión 5) la cambió por un formulario
   en una plataforma web, con su propio ADR. La prueba chica usa tareas ficticias cargadas con `sembrar`.
5. Arranque limpio desde `main`; los flujos A, B y C1 a C6, congelados en `respaldo-flujos-antes-de-d`.
6. Los botones son atajos (ADR 0018, decisión 2) y un tema a la vez (decisión 4; nació en la tarea 0-36,
   detenida, archivada en `respaldo-0-36-en-pausa`).

## Reglas de trabajo de la unidad

- Diseño escrito y acordado con el usuario antes de cualquier código.
- Cada hallazgo de conversación es primero una conversación de prueba.
- Una suite en verde no es evidencia: lo son las conversaciones de prueba contra la IA real, corridas varias
  veces, y la prueba por Telegram.
- Una sola casa para los documentos: esta rama. `main` recibe sólo documentos, por avance rápido, hasta M2 o M3.
- Migraciones nuevas desde `0030` (`0026` a `0029` son de la rama congelada).
- El paquete del motor de conversación definitivo y su prueba de frontera esperan a la Etapa 3.

## Chequeo de rumbo (2026-10-04)

- **Clase de problema:** conversación por ramas de código, sin estado explícito; ya pasó en las rondas 1 a 4,
  en el flujo de un mensaje y en C1-C6, y las tres veces frenó el usuario.
- **Mecanismo o caso:** mecanismo; un motor con estado explícito, circuitos declarados y situaciones generales
  resueltas una vez, más el método (diseño antes del código, conversaciones reales como pruebas).
- **Qué haría innecesaria la próxima ronda:** que una situación nueva se resuelva en el motor para todos los
  circuitos, con su conversación de prueba, y que sumar un circuito sea declararlo.
- **Hipótesis:** la del ADR 0014 sigue para datos y efectos. La nueva, a probar en la Etapa 2: un motor chico
  con estado explícito elimina la clase "se pierde o se traba" con mucho menos código. No es un hecho.
- **Fluidez:** por chat queda lo que es conversación; sale lo que es formulario. Las confirmaciones de la
  constitución §7 se mantienen.
- **Cocina o frases al mozo:** cocina; la IA elige jugadas y redacta desde los hechos (ADR 0018, decisión 1).

## Etapas y criterios de paso

| Etapa | Qué | Criterio de paso |
|---|---|---|
| 0 | Arranque limpio: etiquetas, cierre en `main`, rama y carpeta nuevas | Hecho |
| 1 | Diseño sin código: ADR 0017, ADR 0018, conversaciones de prueba | **M1**, el usuario acepta los dos ADR: **cumplido el 2026-10-04** (el 0018 queda "propuesta" hasta que pase la prueba) |
| 2 | Prueba chica y descartable, por Telegram real, con tareas de `sembrar` y base `leda_motor` | **M2:** resultado registrado en la bitácora, pase o no, contra los criterios del ADR 0018 (decisión 5) |
| 3 | Cortar los enredos, mudar las pruebas de garantías, borrar los flujos A y B, construir el motor; la plataforma web, con su ADR | **M3:** motor construido, flujos viejos borrados, garantías en verde, prueba real aprobada |

Las etapas 2 y 3 tienen cada una su plan propio, que se escribe al llegar.

## Tareas

- [x] **E0-1 a E0-4** (2026-10-04): atribuciones fuera de los commits sin subir de `main`; etiquetas; cierre en
      `main`; rama, carpeta, ADR 0016 y `nucleo/personalidad.md` traídos, migraciones `0026` a `0029` reservadas.
- [x] **E1-1.** ADR 0017, alcance, decisiones 1 a 7. Aceptado (M1).
- [x] **E1-2.** ADR 0018, motor de conversación, decisiones 1 a 8. Diseño aceptado para la prueba (M1).
- [x] **E1-4.** Los documentos que cambian los ADR: `AGENTS.md`, `docs/INDEX.md`, frontera, producto,
      capacidades, `docs/ROADMAP.md` (con "Anotado para más adelante") y notas de los ADR 0013, 0014 y 0016.
- [x] **E1-3.** `tests/conversaciones/`: README del formato y catorce conversaciones: doce del recordatorio
      (las cuatro respuestas del ADR 0018, decisión 5a, y las ocho situaciones generales) y dos para Jev.

Las preguntas al usuario están todas resueltas en los ADR 0017 (1 a 7) y 0018 (1 a 8); lo que sigue
`PENDIENTE` dentro de ellos está en `docs/STATUS.md`, "Decisiones pendientes del usuario". La lista de
decisiones que los ADR tenían que dejar escritas está resuelta y quedó en la copia de archivo.

## Anotado para más adelante

La lista vive en `docs/ROADMAP.md`, "Anotado para más adelante" (desde la E1-4).

## Reglas del arranque limpio

Propuesta de la unidad; el ADR 0018 no las fija.

- El motor vive en un paquete nuevo que sólo alcanza una lista permitida de módulos sólidos; su prueba recorre
  los imports en cadena, incluidos los de dentro de funciones (`herramientas.py`, `pendientes.py` y
  `despachador.py` importan `ingreso_tareas`), con bordes conocidos que sólo pueden achicarse (patrón de
  `tests/test_capacidades.py`).
- Lista permitida de tablas, con el SQL del motor en un solo módulo. Entrada propia: no llama a
  `gateway.procesar_update` ni agrega interruptores. La prueba chica vive fuera de `src/leda`.

## Lo sólido que se reutiliza

`herramientas.ejecutar` (con `db.espacio()` y `autoridad.Solicitante`); la vista previa con huella
(`Preparacion`, `pendientes.registrar` y `pendientes.resolver`, SQL `resolver_pendiente`);
`menu_tarea.calcular_menu`; `lectura.py`; `salida.enqueue_outbox` y `despachador.py`; `escalera.py`, `reloj.py`
y `ciclo.py`; `siembra.py` e `importador.py`.

Enredos a cortar en la Etapa 3 (verificados en `main`; contrastar contra el símbolo): (1) entregar una tarea crea
estado de conversación que sólo `gateway` resuelve (`herramientas.py`); (2) el despachador arma botones y
retiene mensajes con código de conversación; (3) `huerfanos.py` importa `gateway`; (4) la entrada de un mensaje
y la aplicación HTTP viven en `gateway.py`, mezcladas con el flujo A; (5) las garantías clave se prueban en
`tests/test_task_intake.py`, y `tests/conftest.py` importa `gateway`.

## Qué se trae de la rama congelada

De la etiqueta `respaldo-flujos-antes-de-d`. El ADR 0018 (decisión 8) confirmó los avisos del ADR 0016; lo demás
es propuesta.

| Pieza | Propuesta |
|---|---|
| Orden de despacho y bloqueo por espacio; indicador de escritura (`despachador.py`, unas 45 líneas) | Traer |
| Quitar botones vencidos y escribir la opción tocada (`0028`, `despachador.py`, unas 310 líneas) | Traer cuando el motor tenga botones |
| Avisos guardados como hechos, con reintentos (columnas de la `0029`, `salida.py`, `despachador.py`) | Confirmado: migración nueva desde la `0030`; el redactor se rehace |
| `verificador_redaccion.verificar_afirmaciones`; tono del cliente (`instrucciones.py`) | Extraer |
| Contrato del aviso (`alta_turno.py`: `HechosAviso`, `verificar_aviso`) | Rehacer dentro del motor |
| `llm.py`: historial al ruteo, topes por modelo, `llamar_con_plazo`, llamada estructurada | Traer por porciones |
| Respuesta en vivo (streaming) | Fuera de la prueba; decidir después |
| Área de los objetivos (`0027`, `importador.py`) | Traer con la carga de tareas |
| Alta conversada y sus contratos, migración `0026` | No se trae |

Pendientes heredados: verificar si `llamar_con_plazo` cubre todas las llamadas antes de traerlo (dos
exploraciones no coinciden); `llm._limpiar_esquema` no limpia dentro de `items` (Gemini); la prueba
intermitente del indicador de escritura; adaptar `tools/medir_modelos.py`; `tools/restriccion_horario.py` tiene
que admitir `leda_motor`; `python -m leda modelo` ya existe (`docs/product/plataforma-pendientes.md`).

## Evidencia

- **E0-1 a E0-4.** Árbol de `main` igual tras quitar atribuciones (`4de06366…`; la punta anterior, en
  `refs/original/refs/heads/main`). Cierre de `main` (37 archivos de documentación) revisado en cuatro tramos:
  `review-d620b2bb22b7427d`, `review-8a63e809807fd809`, `review-ee3d1ae8de587d93` y `review-02333b9633db361d`.
  Primer commit de la rama, `02fe502`: `review-cec1109be28beca9`. Todas aprobadas y reconocidas.
- **E1-1.** ADR 0017 en `3a96a3a` a `abadf04`. El rango desde `aa32a02` excedió al revisor
  (`review-91bc5e5ee5e6c06c`, sin autoridad); con `main` subido se aprobaron `6f9b9a3..014d7fc`
  (`review-d0498e6bf332490c`) y la rama hasta `abadf04` (`review-2b17d83ab052cefa`).
- **E1-2.** ADR 0018 en `21eaee4`: `review-6cd67d4cee8cb62d`, aprobada; cuatro observaciones corregidas.
- **M1 (2026-10-04).** `41c2077` registra la aceptación; `dc813e6` aplica las notas de su revisión; `main` subió
  por avance rápido hasta `dc813e6` (decisión del usuario), registrado en `9b91393`.
- **E1-4, parte de `AGENTS.md` (2026-10-04).** Cambiado sólo lo que estaba mal o era estado de sesión;
  `docs/STATUS.md` y este documento, condensados; sus versiones hasta M1, literales en `docs/historial/`.
- **E1-4, el resto (2026-10-04).** `74f6f35` (frontera, producto, capacidades), `38ba14b` (roadmap, índice,
  notas de los ADR 0013, 0014 y 0016) y `5795df5` (`docs/STATUS.md` y acá): `review-8127a3bf7edea0bd`, aprobada.
- **E1-3 (2026-10-04).** `5fa7705` (formato y respuestas), `442d34b` (situaciones generales), `f8cb9bb` (Jev) y
  el commit que registra esto. Son documentos: las corre la Etapa 2.
- **Línea base de las garantías.** `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` sobre
  `respaldo-main-antes-de-d`: `2286 passed, 333 deselected, 1 warning in 631.96s`. Mide el código, no la
  conversación.

## Próximo paso

Escribir el plan de la Etapa 2, con las decisiones `PENDIENTE` P1 a P16 de `tests/conversaciones/README.md`.
