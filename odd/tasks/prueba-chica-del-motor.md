# La prueba chica del Motor (Etapa 2)

**Rama:** `feat/motor-de-conversacion` · **Carpeta:** `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`
**Abierta:** 2026-10-04 · **Copia en Engram:** tema `odd/prueba-chica-del-motor/tasks` (proyecto `prisma-pm`)
**Estado:** borrador; espera las decisiones del usuario (sección 10). Ningún código antes.

## 1. Objetivo

Probar con código descartable, fuera de `src/leda`, el diseño del ADR 0018 en el circuito del recordatorio
(decisión 5a con las precisiones de la 9) y cumplir **M2**: el resultado registrado en la bitácora de flujos,
pase o no, contra los criterios 5b (aprobación) y 5c (corte).

## 2. Chequeo de rumbo

- **Clase de problema:** conversación sin estado explícito y con caminos por caso (rondas 1 a 4, C1 a C6).
- **Mecanismo o caso:** mecanismo: fichas y ocho situaciones generales resueltas una vez. Cada commit del motor
  se mira contra 5c.1 (un caso especial).
- **Qué haría innecesaria la próxima ronda:** que cada falla se resuelva en una ficha o una situación general,
  con su conversación como regresión, y que correr las 14 conversaciones cinco veces sea un comando.
- **Hipótesis:** un motor chico con estado explícito elimina "se pierde o se traba". Lo decide 5b, no el plan.
- **Mecánico o fluido:** fluido: nada se confirma (9a), botones sólo en la duda, varias cosas por mensaje,
  respuesta a cualquier hora (9e). Las garantías no se tocan.
- **Cocina o mozo:** cocina: el atraso, lo que depende y quién se entera y cuándo los calcula el código; las
  instrucciones de la IA describen su trabajo, sin frases ni casos.
- **Qué lo demuestra:** las conversaciones 01 a 14, cinco corridas cada una contra la IA real, y Telegram real.

## 3. Alcance

**Entra (ADR 0018, 5a y 9):** un aviso previo tres días hábiles antes, sin pedir respuesta; desde el
vencimiento, recordatorios que piden el estado y una escalera que avanza sólo sin respuesta, hasta escalar (9b);
inicio, nueva previsión (con su aviso al referente y el atraso) y bloqueo con el arranque de la persecución
(9a, 9c), anotados directo; "qué tengo pendiente" (9g); las ocho situaciones generales (decisión 4, 9d, 9f); el
aviso al administrador de lo que no está en la lista (9g); las fallas de la IA (decisión 8).

**No entra:** entrega y aprobación (y la guarda de la decisión 2), la persecución completa, la plataforma web,
la memoria y el motor definitivo en `src/leda` (Etapa 3).

## 4. Arquitectura

**Dónde vive:** `prueba_chica/`, en la raíz. Fuera de `src/leda` (`AGENTS.md`) y fuera de `tests/`: la suite por
defecto (`testpaths = ["tests"]`) no la corre ni le aplica `tests/conftest.py`, que importa `gateway`. Tiene su
`conftest.py`. En la Etapa 3 se borra entera.

**Imports** (prueba de frontera propia, que recorre los imports en cadena, como `tests/test_capacidades.py`).
Permitidos: `leda.db`, `leda.autoridad`, `leda.herramientas.ejecutar`, `leda.calendario`,
`leda.salida.enqueue_outbox`, `leda.despachador`, `leda.incidentes.registrar_incidente`, `leda.llm`, `leda.jev`,
`leda.config`. Prohibidos: `gateway`, `agente`, `ingreso_tareas`, `contexto`, `respuesta_unica`, `huerfanos`,
`ciclo` y `local` (los dos importan `gateway`), `escalera` y `reloj` (textos fijos). Bordes conocidos:
`despachador._rama_activa_de` llega a `ingreso_tareas` por `pendientes.ver_rama_abierta`, dentro de la función;
`herramientas.crear_borrador_tarea` también, y la prueba no la usa.

**Entrada propia:** un escuchador por long polling (`local.escuchar` importa `gateway`) que guarda el mensaje en
`inbound_message`, identifica a la persona (`identificar_en_espacio`) y llama al turno. Un ciclo propio corre cada
minuto la escalera, los avisos guardados y `despachar`; nunca `reloj` ni `ciclo`, así que la escalera vieja no
corre sobre `leda_motor`.

**Un turno:** (1) lee el estado de la persona, sus tareas y los últimos turnos; (2) la IA elige jugadas de la
lista cerrada con una sola herramienta cuyo esquema es la lista (`Proveedor.responder`, existe en `main`), y nombra
las tareas por un alias de la lista que recibe; (3) el código comprueba cada jugada contra su ficha, aplica las
situaciones generales y ejecuta con `herramientas.ejecutar(..., ya_confirmada=True)`, que verifica la autoridad
igual; (4) el resultado son hechos; (5) la IA redacta desde los hechos con el tono de `persona_config`, una
respuesta por mensaje; (6) todo va al registro de turnos. `PENDIENTE`: si `responder` no fuerza la herramienta,
se trae la llamada estructurada de la rama congelada.

**Jugadas** (ninguna confirma, por 9a):

| Jugada | Comprueba | Hace | Después |
|---|---|---|---|
| `anotar_inicio` (tarea) | responsable; `asignada` (si ya está `en_curso`, lo dice) | `actualizar_estado` a `en_curso` | cierra la espera de esa tarea |
| `anotar_prevision` (tarea, fecha, motivo) | responsable; tarea abierta | hecho de previsión con el atraso (`Calendario.habiles_entre`) | aviso guardado al referente, salvo que vuelva a la fecha comprometida |
| `anotar_bloqueo` (tarea, causa) | responsable; tarea abierta | sin causa, pregunta; con causa, `registrar_bloqueo` | si depende de otro, pregunta quién destraba; propone salidas |
| `anotar_quien_destraba` (integrante, alguien de afuera o "no sabe") | bloqueo abierto | hecho de quién destraba | cierra la espera |
| `consultar_pendientes` | nada | lee con `consultar_tareas` | nada |
| `entregar`, `pedir_reasignacion` | nada | sin efecto; hechos de qué no se puede y quién lo decide | sin aviso al administrador (9g) |
| `elegir`, `corregir`, `cancelar`, `dejar_para_despues` | las de su situación general | | |

**Las ocho situaciones, una vez:** (1) cambio de tema: lo directo se anota y los hechos traen la pregunta
pendiente; si lo nuevo pregunta, la pendiente pasa a "para después" (9d); (2) varias cosas: lo directo en una
respuesta, las preguntas de a una y en orden; (3) corrección: un hecho de corrección, nunca un borrado (9f); (4)
cancelar: cierra la pregunta si su ficha la deja dejar (la de quién destraba espera como un pedido de estado,
9c); (5) duda: las tareas como opciones con botones; (6) escrito en lugar de botón: `elegir`, el mismo camino que
el toque; (7) algo vencido: el toque de una pregunta cerrada no hace nada y se dice con qué se cerró; (8) fuera
de la lista: ninguna jugada, hechos de qué puede hacer Leda y aviso al administrador.

**Escalera.** Propia; `escalera.py` no se toca. El aviso previo sale N días hábiles antes (N en
`workspace_setting`: 3 en CoreWork, mínimo 1, comprimido si la tarea tiene menos días). Desde V, cada
recordatorio pide el estado y abre una espera en `pending_reply` (hoy nada la escribe); sin respuesta, V+1, V+2
(avisa que va a escalar) y V+3, por la ruta `falta_persistente_de_respuesta`. Se detiene con un bloqueo abierto o
una ausencia. Hallazgo: `escalera.evaluar` escala sin mirar si hubo respuesta; la de la prueba avanza sólo con la
espera abierta.

**Avisos guardados.** Todo lo que Leda manda por su cuenta se guarda como hechos. Al llegar su hora, dentro del
horario, el código vuelve a leer la tarea; si corresponde, la IA lo redacta y va al outbox; si no, se omite con su
motivo (9b). El de una nueva previsión va como `es_coordinacion` (lo causa el acto de otra persona, mecánica §10).

**Horario (9e).** `despachador._despachar_fila` ya manda las respuestas a cualquier hora y pospone lo demás;
cuándo sale un aviso a otro es un hecho de la respuesta.

**Fallas de la IA (decisión 8).** En un turno: un reintento; si vuelve a fallar, nada se ejecuta, la persona
recibe el único texto fijo, se registra un incidente y el turno queda registrado. En un aviso: reintentos a 1, 2,
4 y 8 minutos; al quinto fallo, incidente y aviso de falla a quien lo causó.

**Aviso al administrador:** un incidente de severidad baja con etapa propia y referencia al `inbound_message`, que
`registrar_incidente` lleva al bot de administración con el mensaje (`incidentes._texto_disparador`). `PENDIENTE`:
verificar el texto con una etapa que `incidentes.py` no conoce, sin editarlo.

## 5. Datos

**`leda_motor`** (no existe; se crea con autorización), con los pasos de `PRUEBA-LOCAL.md` para una base nueva
(`esquema`, `importar --activar`, `feriados`, `modelo` con GPT-6 sol, `sembrar`), más las migraciones nuevas con
`psql -f` y el valor del aviso previo. `pg_dump` antes de cada prueba real.

**Migraciones `0030` y `0031`**, como las demás: rollback en `db/rollbacks/`, `db/esquema.sql` al día y el ensayo
de paridad, que descubre las nuevas solo (`tests/test_task_intake.py:_migraciones_posteriores_a`). Toda tabla
nueva lleva `workspace_id` y entra en el bucle de `row level security` forzado; ninguna lleva `chat_id` ni
`callback_data` (el `chat_id` sale del integrante al encolar).

| Tabla | Qué guarda |
|---|---|
| `conversation_state` | una fila por persona: pregunta abierta, temas para después, último aviso y su tarea; `mostrado_para_confirmar` y `huella` reservadas (decisión 3.1) |
| `conversation_turn` | el registro de turnos, sólo se agrega: sentido, mensaje o fila del outbox, opción tocada, jugadas, resultado, IA, latencia, error (3.2) |
| `conversation_question` y `conversation_option` | las preguntas de Leda (tipo, tarea, si se puede dejar, cuándo y cómo se cerró) y las opciones de una duda, con `token` único |
| `task_forecast` | las previsiones, sólo se agrega: fecha, motivo, fecha comprometida, atraso, a cuál reemplaza, si es corrección, quién; espacio derivado de la tarea por disparador |
| `blocker_unblocker` | quién destraba: un integrante, alguien de afuera o "no sabe" (exactamente uno), quién lo dijo y cuándo |
| `scheduled_notice` | los avisos guardados: tipo, tarea, destinatario, turno que lo causó, hechos, hora, estado (guardado, enviado, omitido, fallido), intentos, motivo de omisión, clave de deduplicación |

Los momentos de las tablas nuevas los pone el motor con su reloj, nunca un valor por omisión. Queda resuelto
cómo se guarda quién destraba (ADR 0017, 3a); qué pasa si dice que no le corresponde sigue `PENDIENTE`. `PENDIENTE`
de la E2-1: la ejecución única de un mensaje repetido (`inbound_message` no tiene índice único por mensaje).

**Estado inicial.** `sembrar` carga todo a diez días y rechaza un espacio con tareas, así que las corridas usan un
cargador propio que escribe como `admin` el estado de cada conversación (tareas, eventos, bloqueos,
dependencias, previsiones, estado de la conversación, lo ya enviado). Telegram parte de `sembrar` y el mismo
cargador ajusta fechas. Sin dependencias informativas: `herramientas._avisar_dependencia_informativa` les manda
un texto fijo.

## 6. Cómo se corren las conversaciones

- `tests/banco` entra por `gateway.procesar_update`: se toman sólo su idea de grabar la IA para repetir una falla
  con `ProveedorGuionado` y su reporte de latencias (`tests/banco/reporte.py`, sin imports de Leda).
- Cada conversación se traduce a un YAML en `prueba_chica/conversaciones/`; el `.md` sigue siendo la fuente.
- Cada corrida, en una base creada desde una plantilla y borrada al final (como
  `tests/conftest.py:_con_base_efimera`), con reloj simulado en las fechas de referencia (octubre y noviembre de
  2026) y `despachador.TransporteDePrueba`. La IA recibe la fecha de hoy como hecho.
- **Se comprueba solo:** jugadas y datos, efectos en la base, avisos con sus hechos (el atraso), esperas, botones,
  una respuesta por mensaje y estado de la conversación. **Lo que dice cada texto y la comprensión:** decisión
  10.3.
- **Puntaje (5b):** sobre la 01 a la 12, garantías 5 de 5 y comprensión al menos 4 de 5 en cada una; la vez que no
  entiende, pregunta sin efecto. La 13 y la 14 miden a Jev.
- GPT-6 sol decide; luna corre las mismas conversaciones aparte (decisión 6); Jev recibe cada mensaje con las
  tareas candidatas y su elección se registra sin decidir (decisión 7).
- En la bitácora, por ronda: fecha, commit, IA, la tabla de 14 por 5, tiempo por turno (mediana y peor caso, sin
  umbral), costo si el proveedor lo informa y la conclusión frente a 5b y 5c.

## 7. Prueba por Telegram real

Con las condiciones de `AGENTS.md` (espacio de prueba, datos ficticios, secreto protegido, efectos reversibles,
respaldo, nada destructivo, nada `CRITICAL` o `HIGH` abierto). El bot, decisión 10.1; el paso de los días, 10.2;
`tools/restriccion_horario.py` tiene que admitir `leda_motor`. El escuchador lo corre el usuario, con el `.env`
que copia él (el agente no lo lee). Se lee con `tools/leer_conversacion.py` (los toques se ven como su código) y
un lector del registro de turnos de la prueba.

## 8. Criterios

Los del ADR 0018, sin cambios: aprobación con los tres de 5b; corte con cualquiera de los tres de 5c. Pase o no,
el resultado va a la bitácora y cumple M2.

## 9. Tareas

Primero en rojo donde hay una prueba determinista: aislamiento de las tablas nuevas, paridad, frontera de imports,
ejecución única, outbox, días hábiles, escalera y fichas con `ProveedorGuionado`. Lo que hace la IA no tiene rojo:
su evidencia son las corridas. Unas 400 líneas por tarea es una guía, no un tope.

- [ ] **E2-1. Tablas** (delegada): `0030`, `0031`, rollbacks, `esquema.sql`, paridad, aislamiento, ejecución
      única. Unas 450 líneas.
- [ ] **E2-2. Esqueleto y frontera** (delegada): `prueba_chica/`, prueba de imports, turno y registro, falla de la
      IA en un turno, el despachador sin retener en `leda_motor`. Unas 400.
- [ ] **E2-3. Jugadas y fichas** (delegada): lista cerrada, fichas, atraso, aviso al administrador. Unas 450.
- [ ] **E2-4. Situaciones generales** (delegada): las ocho, con preguntas, opciones y correcciones. Unas 400.
- [ ] **E2-5. Escalera y avisos guardados** (delegada): aviso previo, esperas, escalamiento, relectura, omisión y
      reintentos. Unas 450.
- [ ] **E2-6. Redacción, escuchador y ciclo** (delegada): instrucciones de la IA, tono, polling, ciclo, bot de
      administración, lector de turnos, `restriccion_horario`. Unas 400.
- [ ] **E2-7. Corredor** (delegada): los 14 YAML, base por corrida, reloj, comprobaciones, reporte, luna y Jev.
      Unas 650.
- [ ] **E2-8. Primera ronda real:** sol, luna y Jev; lectura de textos; bitácora; chequeo de rumbo contra 5c.
- [ ] **E2-9. Telegram real** con el usuario; su juicio; M2 en la bitácora.

**Previsión:** unas 3.600 líneas (código, pruebas y YAML). **Entrega:** `ask-on-risk`: al pasar las 400 se le
pregunta una vez al usuario la estrategia de cadena. Push y PR, del usuario.

## 10. Decisiones para el usuario

1. **¿Un bot de Telegram aparte para la prueba?** Ejemplo: con el mismo bot y el escuchador viejo abierto en
   `prueba-0-35`, un "arranqué" de Marcos cae en la base congelada. **Recomiendo** un bot nuevo (dos minutos en
   BotFather): las bases no se mezclan. **Alternativa:** el mismo bot, cerrando el escuchador viejo cada vez; sin
   trámite, con el riesgo de olvidarlo.
2. **¿Cómo pasan los días en Telegram?** Ejemplo: del aviso previo al escalamiento hay seis días hábiles.
   **Recomiendo** un comando que adelanta el reloj de Leda sólo en `leda_motor` (al día hábil siguiente, 10:00),
   con el horario prendido: días hábiles y atraso salen bien. **Alternativa:** apagar la restricción de horario;
   todos los días cuentan como hábiles (del 23 al 27 daría cuatro de atraso, no dos) y la escalera tarda días
   reales.
3. **¿Quién juzga lo que dice cada respuesta y si Leda entendió?** Ejemplo: en la 02, que no diga que la fecha
   cambió. **Recomiendo** que el agente lea todas contra la lista de cada flecha y arme la tabla, y que el usuario
   lea al menos una corrida por conversación y todas las marcadas como falla (`AGENTS.md` no acepta la auditoría
   de otro agente como prueba). **Alternativa:** una IA juez; más rápida, pero es otra IA a la que habría que
   medir.
4. **¿Cuánto se puede gastar en IA?** Ejemplo: una ronda son 70 corridas de unos cuatro mensajes; con las cifras
   del flujo C6 (una corrida, otro trabajo), unos USD 5 con sol y centavos con luna. **Recomiendo** un techo de USD
   30 para la etapa y avisar al acercarse. **Alternativa:** sin techo; nunca frena una ronda a la mitad.
5. **¿Los avisos guardados en una tabla nueva en lugar de las columnas de la `0029`?** El ADR 0018 (decisión 8)
   dice que se traen esas columnas a `message_outbox`. Ejemplo: un aviso todavía sin texto en el outbox lo
   mandaría vacío el despachador de `main`, que no las conoce. **Recomiendo** `scheduled_notice`: no toca el
   despachador ni suma columnas a una tabla con `chat_id`; se anota la precisión en el ADR. **Alternativa:** las
   columnas; obliga a enseñarle al despachador a saltear esos avisos.

**Decidido en el plan:** la carpeta; las tablas como migraciones del producto (ADR 0018, decisión 3); el aviso
previo en `workspace_setting`, no en el importador; el referente es quien aprueba según la política del espacio
(`PENDIENTE` la consulta); el aviso al administrador como incidente; el de previsión como coordinación.

## 11. Riesgos y próximo paso

- **El despachador retiene según las ramas de los flujos viejos** (enredo 2); en `leda_motor` esas tablas quedan
  vacías, y la E2-2 lo prueba.
- **El saludo diario** lo antepone el despachador (`saludo.reclamar_y_anteponer`); se mantiene: lo decidió el
  usuario.
- **Columnas viejas en hora real** (`blocker.abierto_en`, `task_state_event.at`) durante las corridas;
  `PENDIENTE` confirmar al escribir los YAML que ninguna conversación depende de ellas.
- **La etapa no es tan chica:** si una tarea pide un caso especial, se frena (5c.1).

**Próximo paso:** que el usuario resuelva la sección 10; después, la E2-1.
