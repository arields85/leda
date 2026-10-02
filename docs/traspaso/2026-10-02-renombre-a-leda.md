# Traspaso: el producto se llama Leda y la carpeta local se mudó

Cierre del 2026-10-02. El producto pasó a llamarse **Leda** en todo el repositorio
([ADR 0015](../decisions/0015-renombre-del-producto-a-leda.md)), funciona (alta real de
punta a punta) y lo viejo ya se limpió. La carpeta local también se mudó (R13).
Este documento permite retomar sin reconstruir nada de memoria. El detalle completo, con
cada comando, verificación y revisión, está en
[`../../odd/tasks/renombre-a-leda.md`](../../odd/tasks/renombre-a-leda.md).

Leelo después de `AGENTS.md` y `docs/STATUS.md`. El traspaso anterior
([`2026-10-01-alta-conducida.md`](2026-10-01-alta-conducida.md)) sigue valiendo para el
diseño del alta conducida, la forma de trabajar y cómo leer una prueba. Sus pendientes y su
punto de retorno los reemplaza este documento.

## Punto exacto de retorno

La mudanza de la carpeta (R13) quedó hecha y verificada el 2026-10-02: el paso 6 del
script, rutas actualizadas en `main`, en la rama de flujo y en la memoria del agente, y una
prueba real del alta que pasa desde `D:\Proyectos\Leda-PM` (detalle en R13). Lo que sigue:

1. Cuando el usuario pregunte qué queda pendiente, nombrarle los pendientes de la tabla
   de abajo y dejar que elija. Los marcados como **decididos** se empiezan sin volver a
   discutir su diseño: todo lo resuelto está en el documento que señala la tabla.
2. Si la PC se reinició, levantar PostgreSQL antes de cualquier cosa
   (`levantar-postgres.bat`). Sin eso `leda estado` agota el tiempo contra
   `localhost:5432`, y así fue como frenó la mudanza.
3. El guion de abajo sirve como prueba de humo del alta cada vez que haga falta comprobar
   que todo sigue funcionando.

## Guion de la prueba real del alta

Es la misma prueba que pasó el 2026-10-02 (09:12, tarea creada sin incidentes). Antes de
empezar, PostgreSQL tiene que estar corriendo (`levantar-postgres.bat`, si se reinició la
PC). Hacerla dentro del horario de CoreWork (09:00 a 17:00), así el aviso a Ismael llega
al instante. Las cuentas de prueba las opera el usuario. Se arranca desde el chat de Marcos
sin nada pendiente.

0. **El usuario, en una PowerShell:**
   `cd D:\Proyectos\Leda-PM-worktrees\flujo-de-un-mensaje`, después
   `$env:PYTHONPATH="src"`, después
   `D:\Proyectos\Leda-PM\.venv\Scripts\python.exe -m leda escuchar corework`
   → "Escuchando como @PM_prisma_agent_bot — espacio 'corework'". El nombre del bot sigue
   siendo el viejo hasta que el usuario lo cambie en BotFather.
1. **Marcos escribe** `necesito preparar el informe de paradas de la línea 1 para el viernes que viene`
   → en pocos segundos, Leda anota el borrador con título y fecha y pregunta el objetivo
   con botones. En ningún lado dice "Prisma".
2. **Marcos toca un botón de objetivo** → Leda sigue con lo que falta: responsable y
   criterio de aceptación.
3. **Marcos toca "Para mí"** → Leda pregunta el criterio o propone uno.
4. **Marcos acepta la propuesta con `sí`, o escribe** `el informe tiene las paradas de la semana con su causa`
   → aparece el resumen completo con "Enviar a aprobación", "Modificar" y "Cancelar".
5. **Marcos toca "Enviar a aprobación"** → Leda le confirma que se lo mandó a Ismael, y a
   Ismael le llega el borrador con "Confirmar".
6. **Ismael toca "Confirmar"** → la tarea queda creada; a Marcos le llega "Ismael
   Soschinski confirmó el borrador de la tarea «…»: la tarea quedó creada" y a Ismael
   "Hecho. La tarea quedó comprometida."
7. **El usuario para y avisa.** El agente lee la evidencia antes de opinar:
   `tools/leer_conversacion.py 20 --completo` y `tools/leer_turnos_alta.py 20` (con
   `PYTHONPATH=src` desde el worktree de flujo), la tarea en `leda_flujo` (que venga de su
   borrador y esté `asignada`), la auditoría y los incidentes.

**Pasa** si la tarea queda creada, la conversación, la base y la auditoría coinciden y no
hay incidentes nuevos. Si los "…" duran más de 30 segundos, mirar en vivo antes de
esperar: el 2026-10-02 un turno quedó colgado porque el proveedor `nan` estaba degradado
(pendiente del plazo total, más abajo).

## Qué se hizo (2026-10-01 y 2026-10-02)

- **Renombre** con un script determinista (`tools/renombrar_a_leda.py`) en `main` y en
  `feat/flujo-de-un-mensaje`. Verificación byte a byte: 373/373 y 408/408 archivos son pura
  sustitución. Suites iguales que antes: 2286 y 3432 passed.
- **Leda funciona correctamente**, con las cuatro comprobaciones: suites, verificación, alta
  real por Telegram de punta a punta (Marcos → Ismael, tarea creada) y nada que lea los
  nombres viejos. Hallazgo de esa prueba, corregido: el login de autoridad necesitaba
  `SET ROLE leda_gateway`.
- **Limpieza (R11):** se borraron las bases `prisma`, `prisma_flujo` y las residuales, el
  esquema viejo dentro de la base `postgres` y los roles `prisma_*`, siempre con volcado
  final verificado (`db/respaldos/*-final-antes-de-borrar-20261002.dump`). También los
  volcados intermedios, las copias `.env.antes-leda`, el worktree del renombre y la rama
  `feat/flujo-variante-a` en local (sus commits ya estaban en la rama de flujo).
- **GitHub:** el repositorio nuevo es `arields85/leda` (público, `origin`), con todas las
  ramas y el tag `pre-renombre-leda`. `arields85/prisma` queda congelado como respaldo
  (remoto `respaldo-prisma`): **nunca se hace push ahí**.
- **Engram** conserva su proyecto `prisma-pm`, fijado en `.engram/config.json`. Engram no
  permite renombrar proyectos, y forzar `leda` partiría las memorias.

## Pendientes, en orden recomendado

| # | Pendiente | Dónde está el detalle |
|---|---|---|
| C0-C9 | **PRIORIDAD** (decisión del usuario, 2026-10-02). Pasar cada circuito de Leda al flujo nuevo del ADR 0014 y probarlo en real: variantes del alta, entrega con evidencia, aprobación de la entrega, estados y bloqueos, consultas y menú, dependencias, aclaraciones, cambio de tema, seguimiento automático y cambios sobre una tarea creada. En C0 ya hay tareas decididas, listas para hacer (C0-1 a C0-7). Checklist con la regla de cada uno (diseño, construcción, retiro de lo viejo, prueba real). Cada circuito se diseña con el usuario antes de construirlo | rama de flujo, `odd/tasks/circuitos-al-flujo-nuevo.md` |
| P1-P7 | **Decidido, listo para hacer** (2026-10-02). Falla del proveedor del modelo: plazo total de 2 min por turno, aviso certero (promete "te respondo" sólo si la falla es del proveedor; constitución §10), cola que se reprocesa contra el estado actual, respuesta dentro del horario, límite de 4 h hábiles, alcance a todo turno del modelo. Todo está decidido: se empieza directamente por P1 | rama de flujo, `odd/tasks/flujo-de-un-mensaje.md`, "Decisión: plazo total, aviso certero y cola cuando falla el proveedor" |
| (l) | Espacio muerto entre el stream y el mensaje final. Recomendado: mantener el borrador o "escribiendo…" hasta el final (el ADR 0013 permite varias partes; el límite es la verificación) | rama de flujo |
| (e) | **Resuelto por decisión** (2026-10-02): no era una decisión de producto, era un mecanismo. Los objetivos salían del área de quien pide y no de la tarea. Se corrige con C0-1 y C0-2 (decidido, listo para hacer) | rama de flujo, `odd/tasks/circuitos-al-flujo-nuevo.md`, ronda C0-A |
| — | Advertencia de RDD: doble falla calendario + incidente en `_inicio_de_jornada` (`ingreso_tareas.py`) | rama de flujo |
| — | Mensaje después de cancelar un borrador; calidad del criterio; (k) primer mensaje lento; (j) stream irregular; frecuencia del rechazo de formato de `acceptance_criterion` | traspaso del 2026-10-01 y rama de flujo |
| R12 | Integrar `auxiliar/alta-y-google` a `main` y **seguir ese trabajo desde `main`**, no en una rama aparte (decisión del usuario). Primero se renombra la rama con el script, después se trae `main`. Su `.env` apunta a una base que ya no existe. Bajo el congelamiento: la fecha la decide el usuario | `odd/tasks/renombre-a-leda.md`, R12 |
| C-1…C-3 | Hallazgos del circuito C en `main` | `docs/STATUS.md` |
| — | Borrar `arields85/prisma` y el remoto `respaldo-prisma` cuando el usuario lo dé por obsoleto (la carpeta de memoria vieja `D--Proyectos-Prisma-PM` ya se borró) | tabla de limpieza de R11 |

## Congelado hasta cumplir el ADR 0014

No se construye hasta que el alta, la entrega y la aprobación (C0, C1 y C2) aprueben las
pruebas reales que hacen el usuario y el agente, con los criterios del
[ADR 0014](../decisions/0014-flujo-de-un-mensaje.md) (congelamiento del 2026-09-30,
precisado el 2026-10-02: no espera a la prueba final con alguien nuevo;
`docs/ROADMAP.md`, "Orden de entrega"). Figura acá para que
la lista de pendientes esté completa. Descongelar una unidad lo decide el usuario.

| Unidad | Qué le falta además del descongelamiento | Dónde está el detalle |
|---|---|---|
| Panel de plataforma | Decidir cómo se autentica quien opera Leda; en el código no depende de nada | `docs/ROADMAP.md`, "Panel de plataforma"; inventario en `docs/product/plataforma-pendientes.md` |
| Tablero de cliente | La credencial de acceso del puerto de lectura (el puerto está hecho; la credencial quedó en pausa sin commitear) | `docs/ROADMAP.md`, "Tablero de cliente" |
| Alta con correo verificado y Google (ADR 0010) | Integrar la rama a `main` (R12) | `odd/tasks/renombre-a-leda.md`, R12 |

## Cómo operar ahora

| Qué | Cómo |
|---|---|
| Arrancar PostgreSQL después de reiniciar la PC | `levantar-postgres.bat` desde la carpeta del repositorio (no es un servicio) |
| Listener de la rama de flujo | Desde su worktree (`…\Leda-PM-worktrees\flujo-de-un-mensaje`): `$env:PYTHONPATH="src"` y `<repo>\.venv\Scripts\python.exe -m leda escuchar corework` |
| Bases | `leda` (código de `main`) y `leda_flujo` (rama de flujo: `alta = conversada`, `stream = true`, `redaccion = A`). Ariel, Ismael y Marcos quedan vinculados desde el pack |
| Leer una prueba | `tools/leer_conversacion.py [minutos] --completo` y `tools/leer_turnos_alta.py [minutos]`, con `PYTHONPATH=src` desde el worktree de la rama |
| RDD de `main` | El tramo desde `647fcc7` incluye el commit mecánico del renombre y siempre corta por presupuesto (`lens_context_budget_exceeded`). Está documentado: el commit se prueba con la verificación byte a byte. Revisar lo escrito a mano por tramos que no lo incluyan |
| Push | Sólo a `origin` (`arields85/leda`) y cuando el usuario lo decida |

## Lecciones del renombre

- **El inventario tiene que incluir lo que vive fuera del repositorio:** roles, variables
  de sesión, bases, `.env`, **membresías de los logins** (`pg_auth_members`), esquemas
  dentro de otras bases (había uno en `postgres`) y la carpeta de memoria del agente.
- **La historia de Git no cambia de nombre.** Las pruebas que leen commits viejos necesitan
  una traducción permanente (`tests/historia_previa_a_leda.py`).
- **Verificar antes de afirmar que algo "no tiene trabajo propio".** Las copias de alta y
  Google sí tenían commits sin equivalente, y quedaron a salvo porque se comparó antes de
  borrar.
- **Probar un script destructivo en un repo descartable**, nunca sobre el checkout real. Un
  `aplicar` de prueba reescribió dos documentos ya commiteados, y se restauraron desde Git.
