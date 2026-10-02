# ADR 0015: El producto pasa a llamarse Leda

- **Estado:** aceptada (decisión del usuario, 2026-10-01)
- **Fecha:** 2026-10-01
- **Alcance:** el nombre del producto en todo el repositorio: paquete Python, comando,
  esquema (roles y variables de sesión), variables de entorno, bases de datos locales,
  instrucciones del modelo y documentación. No cambia comportamiento.
- **Detalle de ejecución:** [`odd/tasks/renombre-a-leda.md`](../../odd/tasks/renombre-a-leda.md).

## Contexto

El usuario decidió renombrar el producto de Prisma a Leda. La misma decisión ya se aplicó
en otra aplicación suya, con un procedimiento probado (inventario, decisiones por adelantado,
una sustitución determinista y verificación byte a byte).

`AGENTS.md` exige un ADR para renombrar módulos. El renombre mueve `src/prisma/` a
`src/leda/` y cambia los nombres de los roles de PostgreSQL y de las variables de sesión
sobre las que se apoyan las políticas de aislamiento.

## Decisión

1. Una sola sustitución que respeta mayúsculas (`PRISMA` → `LEDA`, `Prisma` → `Leda`,
   `prisma` → `leda`), aplicada a rutas y contenido de todos los archivos versionados.
   No toca binarios, archivos de bloqueo, los archivos que describen el renombre (el
   documento de la unidad, este ADR y el script `tools/renombrar_a_leda.py`) ni los
   nombres protegidos que quedan fuera de alcance: la carpeta `Prisma-PM`, el repositorio
   `arields85/prisma` y el archivo de respaldo `prisma-antes-flujo-*`.
2. Corte limpio: el código no lee nombres viejos de variables, roles ni bases.
3. **Bases nuevas**, no migración en el lugar. Las bases `leda` y `leda_flujo` se arman desde
   el esquema renombrado y se reimporta el espacio CoreWork. Las bases `prisma*` y sus roles
   quedan intactos como respaldo hasta que se cumpla la condición de limpieza.
4. Las migraciones numeradas se renombran junto con el esquema. Describen cómo se arma una
   base nueva, y ninguna base existente las va a volver a aplicar.
5. Quedan fuera de alcance y los decide el usuario: el nombre de los bots en BotFather, la
   carpeta del repositorio y el nombre del repositorio en GitHub.

## Alternativas descartadas

- **Migrar en el lugar** (renombrar roles y bases, rehacer cada política y función que lee
  `prisma.*`). Conserva datos ficticios y enlaces de prueba, pero exige SQL escrito a mano
  sobre todas las políticas de aislamiento, que son la garantía número uno del producto.
  Además, renombrar los roles cambia el servidor entero de una vez.
- **Renombrar sólo lo visible** y conservar `prisma_*` en roles, variables y paquete. Es
  más barato, pero deja dos nombres para lo mismo, y el usuario pidió "todo".

## Consecuencias

- Hay que volver a activar los enlaces de las cuentas de prueba sobre las bases nuevas, y se
  pierde el historial ficticio de las pruebas (las bases viejas lo conservan).
- Cada rama viva necesita el mismo script antes de un merge. Las ramas congeladas lo reciben
  al retomarse.
- Los nombres viejos de las bases y los roles del servidor se borran sólo cuando Leda funcione
  correctamente, según la definición del documento de la unidad.
