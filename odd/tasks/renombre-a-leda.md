# Renombre del producto: Prisma pasa a llamarse Leda

**Estado:** en preparación (2026-10-01). **Decisión del usuario:** renombrar "todo lo que es
Prisma" a Leda. Guía de referencia: `D:\Proyectos\RENAME_PLAYBOOK_prisma_to_leda.md` (renombre
equivalente hecho en otra aplicación del usuario).

> Este documento queda **excluido** del script de sustitución: describe el renombre y tiene
> que seguir nombrando lo viejo para que se entienda qué fue qué (playbook §8).

## Objetivo

Que el producto, el código, el esquema, la configuración y la documentación digan Leda, sin
cambiar comportamiento, y que quede escrito qué se conserva como respaldo y cuándo se borra.

## Chequeo de rumbo ("Cómo pensamos juntos", punto 3)

- **Qué clase de problema es:** un cambio de nombre, sin comportamiento nuevo. No es
  funcionalidad nueva (no lo frena el congelamiento) ni un hallazgo de conversación.
- **Mecanismo general o caso:** general. Una sola sustitución determinista que respeta las
  mayúsculas, verificada aplicándola al árbol anterior y comparando byte a byte (playbook §6.1).
  Sólo se revisa a mano lo que la sustitución no puede hacer.
- **Qué haría innecesaria la próxima ronda:** dejar el script en el repositorio para poder
  aplicarlo idéntico en cada rama viva. Así los merges ven el mismo renombre en los dos lados.
- **¿Sigue valiendo la hipótesis?** Sí: no hay nada desplegado, los datos son ficticios y el
  ORM Prisma no se usa (inventario abajo).

## Inventario (2026-10-01, sobre `main` en `0c5dadb`)

- 290 de 370 archivos versionados. Apariciones: `prisma` 2096, `Prisma` 763, `PRISMA` 176.
- Rutas: el paquete `src/prisma/` (33 archivos) más 4 documentos.
- Sin choque con el ORM Prisma (`@prisma/client`, `schema.prisma`: ninguno). `leda` sólo aparece
  como subcadena en un documento histórico (`docs/historial/prisma-orienta-diario-…`).
- Fuera del repositorio:
  - roles de PostgreSQL de todo el servidor: `prisma_app`, `prisma_owner`, `prisma_gateway`,
    `prisma_admin`, `prisma_dispatcher`, `prisma_ingress`;
  - variables de sesión que usan las políticas de aislamiento (`prisma.workspace_id`,
    `prisma.entrante_id`, `prisma.aplicando_evento`, …);
  - bases `prisma`, `prisma_flujo` y residuales `prisma_test_*` / `prisma_diag_*`;
  - 20 variables de entorno `PRISMA_*` en los `.env` de `main` y de los worktrees;
  - nombres de los bots en BotFather, la carpeta `D:\Proyectos\Prisma-PM`, los worktrees
    `Prisma-PM-worktrees\…` y el repositorio de GitHub `arields85/prisma`.
- Ramas vivas: `main`, `feat/flujo-de-un-mensaje` (101 commits por delante de la base común),
  `feat/flujo-variante-a`, `auxiliar/alta-y-google`.

## Decisiones

| Decisión | Elección | Por qué |
|---|---|---|
| Mapa de mayúsculas | `Leda` (texto), `leda` (código, rutas, roles, variables de sesión), `LEDA` (variables de entorno) | Sale solo de la sustitución que respeta mayúsculas |
| Corte limpio o lecturas de respaldo | Corte limpio | Nada desplegado |
| Documentos históricos | También se renombran | El usuario dijo "todo"; Git conserva el texto original |
| Ramas | El mismo script en `main` y en `feat/flujo-de-un-mensaje`; las congeladas, al retomarlas | El merge ve el mismo renombre en los dos lados |
| Bases de datos | `PENDIENTE` de decisión del usuario. Recomendado: armar bases nuevas desde el esquema renombrado y dejar las `prisma*` intactas como respaldo | No tocar a mano ninguna política de aislamiento |
| Fuera de alcance (lo hace el usuario) | Bots en BotFather, carpeta del repositorio, nombre del repositorio en GitHub | Cambiar la carpeta rompe el `.venv` y las rutas de memoria; conviene hacerlo aparte |
| ADR | Sí, uno nuevo para el renombre | `AGENTS.md` lo exige para renombrar módulos |

## Respaldo antes del renombre: push del 2026-10-01

**Por qué:** hasta este día no había copia fuera de la máquina local (`main` tenía 125 commits
sin subir y ninguna rama existía en GitHub), y el renombre toca casi todos los archivos. El
push deja una copia remota y un punto de retorno exacto.

**Qué se subió:**

- `main` y el tag **`pre-renombre-leda`**: el último commit con el nombre viejo. Es la base de
  la verificación determinista (playbook §6.1) y el punto para volver atrás.
- `feat/flujo-de-un-mensaje`, `feat/flujo-variante-a` y `auxiliar/alta-y-google`, como respaldo.

**Qué quedó sólo local, a propósito:** `auxiliar/alta-y-google-pre-rebase-0929`,
`auxiliar/alta-y-google-pre-unificacion` y `auxiliar/alta-y-google-unificada-un-commit`. Son
copias viejas de un rebase y de una unificación de esa rama: no tienen trabajo que no esté en
`auxiliar/alta-y-google`.

**Control previo:** el repositorio es **público**. Antes de subir se escaneó toda la historia
pendiente buscando tokens de bot, claves de API, contraseñas y URLs con credenciales. Hubo un
solo resultado: un token de prueba en `tests/test_avisos_alta_correo.py`
(`auxiliar/alta-y-google`). Es un dato de la prueba que comprueba que el token nunca se guarda,
no un secreto. No hay `.env` ni volcados de base versionados.

## Tareas

- [x] R0. Inventario de sólo lectura y decisiones (este documento).
- [x] R1. Push de respaldo y tag `pre-renombre-leda` (ver arriba).
- [ ] R2. Decisión del usuario sobre las bases de datos.
- [ ] R3. ADR del renombre.
- [ ] R4. Script determinista (`tools/renombrar_a_leda.py`): primero `git mv` de las rutas,
      después contenido en bytes. Excluye este documento, binarios y archivos de bloqueo.
- [ ] R5. Aplicarlo en `main`, verificar con la comparación byte a byte contra
      `pre-renombre-leda` y listar cada aparición restante con su motivo.
- [ ] R6. Variables de entorno: renombrar `PRISMA_*` a `LEDA_*` en los `.env`, sin mostrar
      valores.
- [ ] R7. Bases según R2; reimportar CoreWork; el usuario reactiva los enlaces de prueba.
- [ ] R8. Suite completa y prueba real por Telegram desde el código renombrado.
- [ ] R9. Aplicar el mismo script en `feat/flujo-de-un-mensaje` y repetir R5 y R8 ahí.
- [ ] R10. Actualizar referencias externas: memoria del agente, Engram, `docs/STATUS.md`.

## Limpieza posterior

Ningún punto se hace antes de que se cumpla su condición. Mientras tanto, todo lo de esta lista
**se conserva como respaldo** y sirve para volver atrás. Lo que no está en la lista no es
respaldo del renombre.

| Qué | Cuándo se puede borrar | Cómo |
|---|---|---|
| Bases `prisma` y `prisma_flujo` (si en R2 se eligen bases nuevas) | Cuando la suite completa pase sobre Leda y haya una prueba real por Telegram buena sobre las bases nuevas | Volcado final a `db/respaldos/` y después `drop database` |
| Respaldo `db/respaldos/prisma-antes-flujo-20260930.dump` | Junto con las bases de arriba | Borrar el archivo |
| Bases residuales `prisma_test_*` y `prisma_diag_*` | Ya mismo: son de corridas viejas, no son respaldo de nada | `drop database` |
| Roles `prisma_*` del servidor | Después de borrar todas las bases `prisma*` (un rol con objetos no se puede borrar) | `drop role` |
| Variables `PRISMA_*` que queden en algún `.env` | Cuando todos los checkouts en uso estén renombrados | Borrar la línea |
| Tag `pre-renombre-leda` | Nunca hace falta borrarlo: es el registro de dónde estaba todo antes | — |
| Ramas `auxiliar/alta-y-google-pre-*` y `-unificada-un-commit` (locales) | Ya mismo, si el usuario confirma que no las necesita (no tienen trabajo propio) | `git branch -D` |
| `feat/flujo-variante-a` (local, remota y su worktree) | Cuando el usuario dé por cerrado el experimento A/B del ADR 0014 | Borrar el worktree, la rama local y la remota |
| Script `tools/renombrar_a_leda.py` | Cuando ninguna rama viva tenga el nombre viejo (incluida `auxiliar/alta-y-google`, si se retoma) | Borrar el archivo |
| Carpeta, worktrees y repositorio de GitHub con el nombre viejo | Cuando el usuario decida renombrarlos (fuera de alcance) | Lo hace el usuario; el agente actualiza después `.venv`, rutas y memoria |
