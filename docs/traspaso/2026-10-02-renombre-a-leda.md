# Traspaso: el producto se llama Leda y la carpeta local se muda

Cierre del 2026-10-02. El producto pasó a llamarse **Leda** en todo el repositorio
([ADR 0015](../decisions/0015-renombre-del-producto-a-leda.md)), funciona (alta real de
punta a punta) y lo viejo ya se limpió. Queda una sola mudanza pendiente: la carpeta local.
Este documento permite retomar sin reconstruir nada de memoria. El detalle completo, con
cada comando, verificación y revisión, está en
[`../../odd/tasks/renombre-a-leda.md`](../../odd/tasks/renombre-a-leda.md).

Leelo después de `AGENTS.md` y `docs/STATUS.md`. El traspaso anterior
([`2026-10-01-alta-conducida.md`](2026-10-01-alta-conducida.md)) sigue valiendo para el
diseño del alta conducida, la forma de trabajar y cómo leer una prueba. Sus pendientes y su
punto de retorno los reemplaza este documento.

## Punto exacto de retorno

1. **¿Se hizo la mudanza de la carpeta (R13)?** Si existe `D:\Proyectos\Leda-PM` y no
   existe `D:\Proyectos\Prisma-PM`, sí. La corre el usuario (o una IA que controla su PC)
   con `tools/mudar_carpeta.ps1`, con Claude Code cerrado, porque Windows no deja renombrar
   una carpeta en uso.
   - **Si no se hizo:** ayudar a correrla. Primero `-DryRun` desde una PowerShell fuera de
     la carpeta y con todo cerrado. Instrucciones en R13.
   - **Si se hizo**, en la sesión nueva abierta en `D:\Proyectos\Leda-PM`:
     1. verificar que `git worktree list` muestre sólo rutas con `Leda-PM`, que
        `.venv\Scripts\python.exe -c "import leda"` funcione y que la memoria del agente se
        haya leído;
     2. cambiar `Prisma-PM` por `Leda-PM` en los documentos vivos, las herramientas y la
        memoria del agente, también en las ramas `feat/flujo-de-un-mensaje` y
        `auxiliar/alta-y-google`;
     3. sacar `Prisma-PM` de los tokens protegidos de `tools/renombrar_a_leda.py`, porque
        desde ahí renombrar esas rutas pasa a ser lo correcto;
     4. probar el listener desde la ruta nueva (comando abajo);
     5. recordarle al usuario que borre `D:\Respaldo-mudanza-leda`, el respaldo de los
        `.env` y los volcados que hizo antes de la mudanza, porque tiene secretos;
     6. commit y push a `arields85/leda`.
2. Después, seguir con los pendientes en el orden de abajo.

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
| R13 | Terminar la mudanza de la carpeta (pasos de arriba) | `odd/tasks/renombre-a-leda.md` |
| — | Turno del alta colgado sin fin cuando el proveedor se degrada: `conducir_alta` no tiene plazo total y Ctrl+C no corta el listener. Choca con la decisión de "sin plazo por turno": **discutir con el usuario** | rama de flujo, `odd/tasks/flujo-de-un-mensaje.md` |
| (l) | Espacio muerto entre el stream y el mensaje final. Recomendado: mantener el borrador o "escribiendo…" hasta el final (el ADR 0013 permite varias partes; el límite es la verificación) | rama de flujo |
| (e) | Decisión del usuario: qué hace el alta cuando escribe alguien de Dirección sin objetivos operativos | traspaso del 2026-10-01 |
| — | Advertencia de RDD: doble falla calendario + incidente en `_inicio_de_jornada` (`ingreso_tareas.py`) | rama de flujo |
| — | Mensaje después de cancelar un borrador; calidad del criterio; (k) primer mensaje lento; (j) stream irregular; frecuencia del rechazo de formato de `acceptance_criterion` | traspaso del 2026-10-01 y rama de flujo |
| R12 | Integrar `auxiliar/alta-y-google` a `main` y **seguir ese trabajo desde `main`**, no en una rama aparte (decisión del usuario). Primero se renombra la rama con el script, después se trae `main`. Su `.env` apunta a una base que ya no existe. Bajo el congelamiento: la fecha la decide el usuario | `odd/tasks/renombre-a-leda.md`, R12 |
| C-1…C-3 | Hallazgos del circuito C en `main` | `docs/STATUS.md` |
| — | Borrar `arields85/prisma` y el remoto `respaldo-prisma` cuando el usuario lo dé por obsoleto; borrar la carpeta de memoria vieja `D--Proyectos-Prisma-PM` cuando la nueva funcione | tabla de limpieza de R11 |

## Cómo operar ahora

| Qué | Cómo |
|---|---|
| Arrancar PostgreSQL después de reiniciar la PC | `levantar-postgres.bat` desde la carpeta del repositorio (no es un servicio) |
| Listener de la rama de flujo | Desde su worktree (`…\Leda-PM-worktrees\flujo-de-un-mensaje` después de la mudanza): `$env:PYTHONPATH="src"` y `<repo>\.venv\Scripts\python.exe -m leda escuchar corework` |
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
