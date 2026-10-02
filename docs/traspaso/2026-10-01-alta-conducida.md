# Traspaso: el alta conducida por el modelo funciona y se sigue puliendo

Al cierre del 2026-10-01, el alta de tareas conducida por el modelo (enmienda del
[ADR 0014](../decisions/0014-flujo-de-un-mensaje.md)) se probó todo el día por Telegram
real y **funciona**. El modelo entiende el lenguaje desprolijo, propone lo que falta, y el
usuario lo describe como "fluidez increíble". Los hallazgos ya no son de comprensión, sino
de **costura entre el modelo y el código**. Este documento le permite a la sesión siguiente
retomar al mismo ritmo, sin reconstruir nada de memoria.

Leelo después de `AGENTS.md` y `docs/STATUS.md`. El detalle de cada hallazgo, cada
corrección y cada revisión está en `odd/tasks/flujo-de-un-mensaje.md` de la rama
`feat/flujo-de-un-mensaje`. Es largo: buscá por la entrada, no lo leas entero.

## Ruta rápida: el punto exacto de retorno

1. **Contexto:** `mem_context`, después este documento y `docs/STATUS.md` ("Próximo paso").
2. **Verificar el estado de la rama** (el worktree no tiene `.venv`: se usa el del checkout
   principal):
   ```bash
   cd D:/Proyectos/Prisma-PM-worktrees/flujo-de-un-mensaje
   git log --oneline -1          # esperado: 96a139b o posterior
   PYTHONPATH=src "D:/Proyectos/Prisma-PM/.venv/Scripts/python.exe" -m pytest -q -p no:cacheprovider
   ```
   La última suite completa registrada es la de `5cd32b6`, con 3411 passed. Los commits
   posteriores (`dfbb01d` … `96a139b`) se verificaron con pruebas enfocadas. **Lo primero
   es correr la suite completa** (~23 min, en segundo plano).
3. **Revisar con RDD lo que falta:** la frontera revisada es `39bbf59`, y las correcciones
   de esa revisión llegaron en `76721cd`.
   ```bash
   "D:/Proyectos/Prisma-PM/.venv/Scripts/python.exe" tools/rdd_por_tramos.py \
     "D:/Proyectos/Prisma-PM-worktrees/flujo-de-un-mensaje" 39bbf59 tramo-siguiente
   ```
4. **Preguntarle al usuario la decisión (e)**, la de Dirección (ver "Pendientes"). Es lo
   que quedó recomendado como siguiente unidad.

## El diseño que está funcionando

Cada mensaje o toque del alta es **una** llamada al modelo (`conducir_alta`) que recibe
la conversación y los **hechos** del turno, y devuelve una salida estructurada y cerrada.
El código valida los valores, guarda los válidos, verifica el texto y pone los botones.
Nada se compromete sin el botón.

| Pieza | Dónde | Qué hace |
|---|---|---|
| Contrato del turno | `src/prisma/alta_turno.py` | Hechos (`hechos_a_json`), esquema de salida, guía `SISTEMA_ALTA`, `leer_salida`, `aplicar_valores`, `verificar_turno` |
| Conducción | `src/prisma/alta_conducida.py` | `_conducir`: hasta 2 intentos; si los dos fallan, aviso neutro + incidente `alta_conducida_fallida` + aviso a la administración |
| Proveedores | `src/prisma/llm.py` | `conducir_alta` en cada proveedor; NaN/compatible con stream |
| Encendido | `workspace_setting` `alta = conversada` | Ausente o `guiada`: el alta guiada de siempre (todavía convive) |

**Lo que el código garantiza** (el verificador cuida **solo invariantes**, decisión del
usuario):

- no inventar fechas, números, nombres ni títulos que no estén en los hechos;
- no nombrar un botón que no se va a mostrar (`boton_final`: Confirmar o Enviar a aprobación);
- si falta un dato, la respuesta pide algo: lo declara en `pregunta` **o registra una
  propuesta**. El "?" no se exige: "decime la fecha" es pedir;
- los botones corresponden a lo que se pregunta;
- sin llaves ni claves internas; largo máximo de 700 caracteres.

**Lo que el modelo recibe como hechos, porque sin ellos inventa:**

- el borrador, lo que falta, las opciones con ids cortos, el día de hoy y un calendario de
  ayuda (`proximos_dias`, no es un límite);
- la regla real de fechas: desde hoy hasta el límite del margen (`horizonte_tarea`, 2 meses);
- `boton_final`, el botón real del resumen;
- `podes_ofrecer`: la lista cerrada de lo que Prisma puede ofrecer **en ese turno**
  (guardar y retomar cuando la persona quiera, cambiar un dato, cancelar, el botón final,
  una fecha concreta hasta el límite). Nunca dividir tareas, crear objetivos ni retomar en
  un día dado: no existen.

**Propuestas de Prisma** (tres correcciones hasta encontrar la forma): Prisma registra su
propia propuesta de criterio con `{propuesta}` sola (queda `proposed`) y eso cuenta como
preguntar. La persona acepta con un "sí" y el modelo manda `{texto: <propuesta>}`. Para la
fecha, propone una concreta en el texto y el "sí" se manda como `fecha_iso`.

## Cómo se trabajó (el ritmo a mantener)

1. **El usuario prueba en Telegram real** con las cuentas ficticias Marcos, Ismael y Ariel,
   que opera él mismo. Marcos e Ismael los usa por Telegram Web, donde el stream no se ve
   bien; Ariel, desde el celular.
2. **Guion de prueba = un solo hilo numerado:** quién, el texto exacto a escribir o el botón
   a tocar, y una flecha con lo que tiene que pasar. **Nunca tablas** (memoria
   `guion-como-hilo-numerado`). Decir desde qué estado del chat se arranca y dónde parar.
3. **Al volver de cada prueba, leer la evidencia antes de opinar** (ver "Cómo leer una
   prueba"): conversación con botones, intentos del modelo con su motivo, incidentes y
   cola. Nunca concluir desde una captura sola, y nunca afirmar un bug sin verificarlo:
   hoy hubo dos falsas alarmas, una por el corte de 400 caracteres de la herramienta y otra
   por un aviso postergado por horario.
4. **Explicar simple y con ejemplos**, una pregunta por vez, con una recomendación. El
   usuario pide explicaciones sencillas cuando algo es técnico.
5. **Clasificar el hallazgo por mecanismo**, no por caso (ADR 0013 y "Cómo pensamos
   juntos", punto 4). El punto 4 se disparó tres veces hoy y las tres se resolvieron
   **quitando reglas** o **dándole al modelo un hecho o un lugar** que le faltaba. Si un
   arreglo agrega un caso especial, parar y discutir.
6. **Delegar la escritura en un escritor con TDD estricto**: rojo observado, verde,
   documentar en la entrada de la unidad, sin commit. Después el padre **verifica
   corriendo las pruebas enfocadas él mismo**, hace el commit y lanza RDD por tramos y la
   suite completa en segundo plano. Las correcciones chicas de un archivo, inline y con TDD.
7. **Cada advertencia de una revisión RDD se verifica**: se corrige si es real (hubo
   varias: notificaciones que fallaban en silencio, el stream que frenaba al modelo, el
   calendario) y se descarta con evidencia si no lo es.
8. **Registrar cada hecho relevante** en la entrada de la rama, y las decisiones del usuario
   también en memoria. Lo configurable va al inventario de la plataforma.

## Cómo operar

| Qué | Cómo |
|---|---|
| Listener del worktree (lo corre el usuario en su terminal) | `cd D:\Proyectos\Prisma-PM-worktrees\flujo-de-un-mensaje`, `$env:PYTHONPATH="src"`, `D:\Proyectos\Prisma-PM\.venv\Scripts\python.exe -m prisma escuchar corework`. Reiniciar después de cada commit de código |
| Base de la rama | `prisma_flujo` (el `.env` del worktree apunta a ella). Ajustes activos: `alta = conversada`, `stream = true`; sin `horizonte_tarea` (vale 2 meses). La base `prisma` es la de la ronda 4, no se toca |
| Cambiar un ajuste | Script con `prisma.db.conectar` + `admin`, comprobando `current_database() == 'prisma_flujo'` antes de escribir; sólo imprimir valores fijos, nunca derivados del `.env` (memoria `env-sin-imprimir-derivados`) |
| Horario de CoreWork | 09:00-17:00. Fuera de horario los avisos quedan para las 09:00 del día siguiente (no es una falla) |
| Herramientas de lectura | Ver "Cómo leer una prueba" |
| Revisión RDD por tramos | `tools/rdd_por_tramos.py <repo> <base> <etiqueta>` (consentimiento permanente del usuario). Si el tramo excede el presupuesto, commit por commit, con el listener detenido |
| Hook de RDD en `main` | Al cerrar cada turno pide revisar un tramo viejo desde `092c6d3` (22 mil líneas, ya revisado por partes antes). Correr el STATUS y `gentle-ai review assess --base-ref 0ebc27a --committed-only`: lo nuevo en `main` es sólo documentación (`passive`) |

## Cómo leer una prueba

Desde el worktree, con `PYTHONPATH=src`:

```bash
# conversación con botones (--completo: sin cortar en 400 caracteres)
"D:/Proyectos/Prisma-PM/.venv/Scripts/python.exe" "D:/Proyectos/Prisma-PM/tools/leer_conversacion.py" 30 --completo
# por qué falló un turno: intentos del modelo, motivo, forma de la salida, incidentes
"D:/Proyectos/Prisma-PM/.venv/Scripts/python.exe" "D:/Proyectos/Prisma-PM/tools/leer_turnos_alta.py" 30
```

- Un turno con dos intentos rechazados = el aviso "Tuve un problema…". El `motivo` y la
  `salida` (forma, sin texto libre) dicen por qué.
- Latencia: la diferencia entre el mensaje entrante y la respuesta enviada. El `at` de la
  auditoría es el inicio del turno: si está muy después del mensaje, la demora no es del
  modelo (pendiente (k)).
- La cola (`message_outbox`, estado `listo` con `programado_para` futuro) explica los avisos
  que "no llegaron" fuera de horario.

## Decisiones del usuario de esta jornada

- Modelo puro: sin plantillas de respaldo que tapen al modelo.
- Primero fluidez y facilidad de uso, después latencia (el objetivo de 5 s sigue vigente).
- El verificador cuida sólo invariantes.
- Margen de fecha de una tarea por espacio, 2 meses por omisión. La regla de fondo es que la
  fecha de una tarea no pasa la de su objetivo y el margen queda como red de seguridad.
  **Topes y fechas son configuración: no se ajusta Prisma a sus valores actuales.**
- Avisos: a quien pidió, cuando se aprueba su borrador; al responsable, cuando otro le
  asigna una tarea; a quien confirma, si el otro se entera y cuándo.
- Stream real encendido en `prisma_flujo` ("me ayuda a ver cómo se comporta Prisma"), con
  los textos intermedios a la vista, cada 0,15 s.
- Criterios de adopción del alta conducida en la enmienda del ADR 0014. La prueba de
  adopción necesita a alguien que no conozca el guion, y **hoy no lo hay**: mientras tanto
  se avanza con "nuestra parte".
- Todo lo configurable se anota en
  [`product/plataforma-pendientes.md`](../product/plataforma-pendientes.md).

## Pendientes, en orden recomendado

| # | Pendiente | Tipo | Nota |
|---|---|---|---|
| (e) | Alguien de Dirección (sin objetivos operativos) recibe el objetivo estratégico completado solo | Decisión del usuario | ¿Dirección cuelga tareas del estratégico, o se le ofrecen los operativos de las áreas? Preguntar antes de codificar |
| — | Un mensaje enviado después de cancelar un borrador abre una aclaración equivocada sobre tareas | Comportamiento | Misma familia que el borrador pausado (`7faead3`): el camino general no sabe que el borrador se acaba de cancelar |
| — | Calidad del criterio: aceptó "envío videos", que es evidencia y no un resultado (mecánica §13 q2) | Modelo | Medir con el banco antes de tocar la guía |
| (k) | El primer mensaje después de reiniciar el listener empieza a procesarse 20-40 s tarde | Latencia | Visto dos veces; sin investigar |
| (j) | Stream irregular: a veces se queda en las primeras letras y después aparece el texto de golpe | Visual | El usuario: dejarlo así y pulirlo después |
| — | "rango" suena técnico en los mensajes de fecha | Visual | Menor |
| — | Sugerencias de las revisiones (ver la rama) | Calidad | No bloquean |
| M4-M9 | Retirar el alta guiada (formulario, sus expresiones regulares, sus correcciones) | Adopción | Recién cuando se cumplan los criterios del ADR 0014 |
| — | Llevar el patrón a entrega y aprobación | Adopción | Después de M4-M9 |
| C-1…C-3 | Hallazgos del circuito C en `main` (vista previa vencida en silencio, avisos viejos que salen igual, "ya no está vigente" sin salida) | `main` | Ver `docs/STATUS.md` |

En el roadmap, bajo el congelamiento: "Trabajo que no entra en una tarea" (extensión
aprobada, dividir, objetivo propuesto; la regla de fecha acotada por el objetivo) y
"Respuesta que se va escribiendo" (comparar los dos modos de stream con la latencia).

## Lecciones de la jornada

- **El modelo interpreta bien cuando tiene los hechos.** Cuando falló, le faltaba un
  hecho: qué botón, qué fechas valen, qué puede ofrecer, que hay un borrador pausado. La
  corrección fue dárselo, no restringirlo.
- **Los hechos también tienen que ser reales.** Un texto del código ofrecía "tomarlo como
  objetivo" y otro "dividir la tarea" sin mecanismo detrás: el modelo los repitió. Cada
  oferta tiene que tener una acción posible.
- **Seguir lo que el modelo intenta hacer naturalmente** resolvió las propuestas: pedía
  registrar su propuesta y el contrato no lo dejaba.
- **Reglas de estilo en el verificador = respuestas correctas rechazadas.** Se quitaron
  todas.
- **Fallar en silencio aparece en lugares inesperados:** errores de Telegram ignorados,
  avisos perdidos en una transacción, un calendario roto. La revisión RDD los encontró.
- **El stream sirve para diagnosticar:** el usuario vio en vivo cómo el verificador
  rechazaba y el modelo reescribía.
