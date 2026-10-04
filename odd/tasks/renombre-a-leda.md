# Renombre del producto: Prisma pasa a llamarse Leda

> **Nota del 2026-10-04.** Este documento es anterior al Motor, la línea de trabajo vigente. Lo que
> figure acá como en curso, pendiente o próximo paso no se retoma sin una decisión del usuario. El
> orden de trabajo vigente está en [`docs/STATUS.md`](../../docs/STATUS.md).

**Estado:** Leda funciona correctamente (2026-10-02). Limpieza (R11) hecha salvo lo que depende de alta y Google; integración de `auxiliar/alta-y-google` pendiente (R12). **Decisión del usuario:** renombrar "todo lo que es
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
| Bases de datos | **Bases nuevas** `leda` (código de `main`) y `leda_flujo` (rama de flujo) armadas desde el esquema renombrado; las `prisma*` quedan intactas como respaldo (usuario, 2026-10-01) | No tocar a mano ninguna política de aislamiento ([ADR 0015](../../docs/decisions/0015-renombre-del-producto-a-leda.md)) |
| `.env` | Se les aplica la misma sustitución: cambian los nombres `PRISMA_*`, el `dbname` y el `application_name`. El usuario de conexión no lleva el nombre | Comprobado por estructura, sin mostrar valores |
| Paquete instalado | Reinstalar en modo editable (`pip install -e .`) después de desinstalar `prisma` | El `.venv` tiene una instalación editable que se llama `prisma` |
| Fuera de alcance (lo hace el usuario) | Bots en BotFather, carpeta del repositorio, nombre del repositorio en GitHub | Cambiar la carpeta rompe el `.venv` y las rutas de memoria; conviene hacerlo aparte |
| ADR | Sí, uno nuevo para el renombre | `AGENTS.md` lo exige para renombrar módulos |

## Respaldo antes del renombre: push del 2026-10-01

**Por qué:** hasta este día no había copia fuera de la máquina local (`main` tenía 125 commits
sin subir y ninguna rama existía en GitHub), y el renombre toca casi todos los archivos. El
push deja una copia remota y un punto de retorno exacto.

**Qué se subió:**

- `main` y el tag **`pre-renombre-leda`**: el último commit subido con el nombre viejo, que es el
  punto para volver atrás. La verificación determinista (playbook §6.1) no compara contra
  el tag, sino contra el commit inmediatamente anterior al mecánico (`0bbc21b`, ver R5):
  entre el tag y ese commit entraron el ADR y el script.
- `feat/flujo-de-un-mensaje`, `feat/flujo-variante-a` y `auxiliar/alta-y-google`, como respaldo.

**Qué quedó sólo local, a propósito:** `auxiliar/alta-y-google-pre-rebase-0929`,
`auxiliar/alta-y-google-pre-unificacion` y `auxiliar/alta-y-google-unificada-un-commit`, que
son copias de un rebase y de una unificación de esa rama. La primera versión de este documento
decía que no tenían trabajo propio, y no estaba verificado. Comparadas el 2026-10-02 con
`git cherry`, tienen commits sin equivalente exacto en `auxiliar/alta-y-google` (1, 33 y 1).
Probablemente es el mismo trabajo antes de unificarlo, pero no está probado. Se conservan.

**Control previo:** el repositorio es **público**. Antes de subir se escaneó toda la historia
pendiente buscando tokens de bot, claves de API, contraseñas y URLs con credenciales. Hubo un
solo resultado: un token de prueba en `tests/test_avisos_alta_correo.py`
(`auxiliar/alta-y-google`). Es un dato de la prueba que comprueba que el token nunca se guarda,
no un secreto. No hay `.env` ni volcados de base versionados.

## Tareas

- [x] R0. Inventario de sólo lectura y decisiones (este documento).
- [x] R1. Push de respaldo y tag `pre-renombre-leda` (ver arriba).
- [x] R2. Decisión del usuario sobre las bases de datos: bases nuevas.
- [x] R3. ADR del renombre: [ADR 0015](../../docs/decisions/0015-renombre-del-producto-a-leda.md).
- [x] R4. Script determinista (`tools/renombrar_a_leda.py`): primero `git mv` de las rutas,
      después contenido en bytes. Excluye este documento, binarios y archivos de bloqueo.
- [x] R5. Aplicado sobre `main` en la rama `refactor/renombre-a-leda` (worktree
      `Prisma-PM-worktrees/renombre-a-leda`), commit mecánico `58d2bed` sobre `0bbc21b`.
      Ruta inline: script determinista, sin escritor delegado.
      - Comando: `python tools/renombrar_a_leda.py aplicar` y después
        `verificar 0bbc21b 58d2bed`, el 2026-10-01.
      - Resultado: 37 rutas movidas y 290 archivos reescritos. Verificación:
        **373 de 373 archivos son pura sustitución** (differ 0, missing 0, added 0).
      - Apariciones restantes, todas intencionales: los tres archivos excluidos (este
        documento, el ADR 0015 y el script) y los tokens protegidos. Esos son las rutas a la
        carpeta `D:\Proyectos\Prisma-PM` y a `Prisma-PM-worktrees` (16, en documentos y en
        dos herramientas) y `db/respaldos/prisma-antes-flujo-20260930.dump` (1).
      - Correcciones a mano, en un commit aparte: en `docs/STATUS.md` y en el traspaso, la
        base de la ronda 4 y los residuales siguen siendo `prisma*`, porque son bases reales
        que no cambian de nombre.
- [x] R6. Variables de entorno. Hecho: el `.env` y el `.env.test` del worktree del renombre
      se copiaron del checkout principal y se les aplicó `renombrar_a_leda.py env`. Quedaron
      con 0 claves `PRISMA` y sin ninguna aparición de "prisma", sin mostrar valores.
      Worktree de flujo: hecho el 2026-10-02, con copias `.env.antes-leda`. Pendiente: el
      `.env` del checkout principal, cuando `main` reciba el renombre.
- [x] R7. Bases. Hecho: base `leda` creada el 2026-10-01 con `esquema`,
      `importar corework --activar`, `feriados`, `sembrar` (12 tareas, 1 dependencia),
      `modelo deepseek-v4-flash --proveedor nan` y `administrador corework Ariel`.
      `leda_flujo`: creada el 2026-10-02 desde la rama de flujo renombrada (con las migraciones
      0026 y 0027) con los mismos pasos, más `alta = conversada`, `stream = true` y
      `redaccion = A`, igual que `prisma_flujo` (el pack de la rama trae B). El modelo es
      idéntico en las dos bases (`nan/deepseek-v4-flash`, sin parámetros). **No hace falta
      reactivar enlaces:** Ariel, Ismael y Marcos quedan vinculados desde el pack.
- [x] R8. Suite completa y prueba real por Telegram desde el código renombrado.
      - Primera suite sobre `460b413` (2026-10-01): **9 failed, 2277 passed**. Las 9 son pruebas
        de migración de `tests/test_task_intake.py` que arman una base vieja con
        `git show efa8ee2:db/esquema.sql`. Ese commit es anterior al renombre (roles
        `prisma_*`, variables `prisma.*`) y las migraciones que se le aplican ya dicen
        `leda`. No es un error del código renombrado: la historia de Git no cambia de
        nombre.
      - Arreglo general (`de654d3`): un único ayudante `esquema_base()` traduce el esquema
        histórico con la misma sustitución (`tests/historia_previa_a_leda.py`, permanente
        y excluido del script en `a3c5ce8`). RED: las 9 observadas. GREEN: 9 passed. RDD
        `review-ff793423fcb4995a` aprobada. Su WARNING sobre la ruta del import se descarta:
        es el estilo existente (`from tests.toques …`) y las 9 pasan.
      - Suite completa repetida sobre `481af9b` (2026-10-01):
        `PYTHONPATH=src python -m pytest -q -p no:cacheprovider` → **2286 passed**, 333
        deselected, 15 min. Es toda la suite de `main`, sin fallas. Falta la parte real de
        R8, la prueba por Telegram, que se hace sobre la rama de flujo (R9).
- [x] R9. Aplicar el mismo script en `feat/flujo-de-un-mensaje` y repetir R5 y R8 ahí.
      - Commit mecánico `3b75117` sobre `aeea562`: **408 de 408 archivos son pura
        sustitución**. Los restos son rutas a `Prisma-PM`. Arreglo de las pruebas de
        migración con cherry-pick (`1adcfd0`, RDD `review-7ea5dbadc4239272`).
      - Suite completa sobre `1adcfd0` (2026-10-02): **3432 passed**, igual que antes del
        renombre (3432 en `e506ddd`).
      - Prueba real (2026-10-02 00:10): el listener arrancó con `python -m leda escuchar
        corework` sobre `leda_flujo` y el saludo dijo "Soy Leda". El primer mensaje del alta
        se colgó esperando al proveedor `nan`, que estaba degradado (11-30 s o sin respuesta
        para un "ok"). No es del renombre; queda registrado como hallazgo en la rama de
        flujo (llamada sin plazo total). `PENDIENTE`: repetir el alta cuando `nan` se
        recupere.
      - Segunda prueba real (2026-10-02, 08:48-09:07, con `nan` recuperado): el alta de
        Marcos anduvo de punta a punta hasta "Enviar a aprobación" y el aviso a Ismael salió
        al instante. Al confirmar, Ismael recibió el aviso neutro y quedó el incidente
        `toque_boton` (alta, avisado a la administración): `permission denied to set role
        "leda_gateway"`.
        - Causa, **del renombre**: el login de `LEDA_AUTHORITY_DB_URL` era miembro sólo de
          `prisma_gateway` (`SET` sí, `INHERIT` y `ADMIN` no; `db/README.md`). Es una
          membresía del servidor que se otorgó a mano, y `esquema.sql` no la crea para el
          rol nuevo. La suite no podía verla porque arma su propio login de autoridad
          (`tests/conftest.py`, `authority_uri`).
        - Arreglo (2026-10-02 09:1x): `grant leda_gateway to <login de autoridad> with
          inherit false, set true, admin false`, con las mismas opciones. Verificado: puede
          hacer `set role leda_gateway` y no puede asumir `leda_app`. La membresía vieja
          queda hasta la limpieza.
        - Lección para el inventario de cualquier renombre: además de roles, variables y
          bases, revisar **las membresías de los logins** en `pg_auth_members`.
- [x] R10. Referencias externas (2026-10-02): memoria del agente
      (`producto-se-llama-leda`, con su línea en el índice), Engram (tema
      `odd/renombre-a-leda/estado`) y `docs/STATUS.md` (operación y Git).
- [ ] R11. **Limpiar lo de Prisma cuando quede obsoleto**, según la tabla de abajo. Se hace
      recién cuando se cumpla "Leda funciona correctamente".

- [ ] R12. **Integrar `auxiliar/alta-y-google` con el renombre** (pedido del usuario,
      2026-10-02). La rama tiene trabajo avanzado sin terminar (alta con correo verificado y
      credencial de Google, migraciones `0100` y `0101`, ADR 0010) que se integra a `main`.
      **Decisión del usuario (2026-10-02): después de integrarla, ese trabajo continúa desde
      `main`. No se sigue en una rama aparte.** La rama y su worktree se retiran una vez
      integrados. Se hace con el procedimiento de abajo cuando el usuario lo indique; la
      funcionalidad nueva sigue congelada (ROADMAP, "Orden de entrega"), así que la fecha
      la decide el usuario.

- [x] R13. **Mudar la carpeta local** `D:\Proyectos\Prisma-PM` → `D:\Proyectos\Leda-PM`, y
      `Prisma-PM-worktrees` → `Leda-PM-worktrees` (pedido del usuario, 2026-10-02).
      - Windows no deja renombrar una carpeta en uso, y la sesión de Claude Code corre
        adentro. Por eso la mudanza la corre el usuario con
        `tools/mudar_carpeta.ps1` (primero `-DryRun`), con Claude Code, los editores, el
        listener y las pruebas cerrados, desde una PowerShell fuera de las dos carpetas.
        La simulación del 2026-10-02 detectó los procesos en uso y se negó a seguir, como
        corresponde.
      - El script: renombra (y deshace el primer renombre si falla el segundo), hace
        `git worktree repair`, recrea el `.venv` con los mismos paquetes (conserva el viejo
        hasta que el nuevo importa `leda`), copia la memoria del agente a
        `D--Proyectos-Leda-PM`, borra los índices viejos de CodeGraph y crea el nuevo, y
        verifica.
      - No dependen de la ruta: Engram (fijado en `.engram/config.json`), PostgreSQL (datos
        en scoop) y los `.env`.
      - Después de la mudanza, en una sesión nueva abierta en `D:\Proyectos\Leda-PM`:
        cambiar `Prisma-PM` por `Leda-PM` en los documentos vivos, las herramientas y la
        memoria del agente (también en las ramas de flujo y de alta y Google); sacar
        `Prisma-PM` de los tokens protegidos de `tools/renombrar_a_leda.py`, porque desde ahí
        renombrar esas rutas pasa a ser lo correcto; y comprobar el listener desde la ruta
        nueva. Claude Code va a pedir confiar en la carpeta nueva.
      - RDD del script: `review-a7221ca544b0a4ec`, `review-be7cbb8e4124fef5` y
        `review-da00320656b0f75e`, aprobadas. Corregidas: restaurar el `.venv` viejo si falla
        la reconstrucción, que la verificación final falle de verdad, leer los códigos de
        salida antes de canalizar, y normalizar `/` en las rutas de los worktrees (probado:
        hoy detecta la ruta vieja). Se descarta "prefijo con falso positivo": después de la
        mudanza ninguna ruta debe contener `Prisma-PM`, tampoco `Prisma-PM-worktrees`.
        Sintaxis verificada con el analizador de PowerShell; `-DryRun` frena por los procesos
        en uso, como corresponde.
      - **Hecho (2026-10-02).** El usuario corrió el script después de reiniciar la PC.
        Hizo los pasos 1 a 5 y frenó en la verificación: `leda estado` agotó el tiempo
        contra `localhost:5432`. La causa fue que PostgreSQL no estaba corriendo, porque no
        es un servicio de Windows y no arranca después de reiniciar. El script frenó como
        debía. Con PostgreSQL levantado, el paso 6 pasó entero desde `D:\Proyectos\Leda-PM`:
        `git worktree list` muestra sólo rutas `Leda-PM`, `import leda` funciona y
        `leda estado corework` termina con código 0.
      - Prueba real del alta desde la carpeta nueva, el 2026-10-02 de 11:07 a 11:09, con el
        listener de la rama de flujo y la base `leda_flujo`: **pasa**. Marcos creó el
        borrador, eligió el objetivo y "Para mí", escribió el criterio y lo envió a
        aprobación. Ismael lo confirmó. La tarea `02168c89` quedó `asignada`, y su borrador y
        su solicitud de alta quedaron `converted` y apuntan a ella. La auditoría registra
        enviar → avisar → confirmar, más el evento `→ asignada`. Los cuatro turnos salieron
        "aceptada" al primer intento (de 4,9 a 8,2 segundos), sin incidentes nuevos y sin
        "Prisma" en ningún mensaje.
      - Rutas: `Prisma-PM` → `Leda-PM` en los documentos vivos de `main` (`docs/STATUS.md`,
        ADR 0010, traspaso del 2026-10-01, `odd/tasks/alta-y-google.md` y el procedimiento
        de R12), en la rama de flujo (`5ce55e0`) y en la memoria del agente. Se conservan
        como registro histórico: `docs/historial/`, el ADR 0015, el relato de R5 a R13, el
        diario `leda-orienta.md` de la rama de flujo y `tools/mudar_carpeta.ps1`.
        `auxiliar/alta-y-google` no se tocó a mano: la cubre R12, porque
        `renombrar_a_leda.py` ya no protege `Prisma-PM` (autoprueba 11/11).

## Procedimiento para integrar `auxiliar/alta-y-google` (R12)

Estado de la rama al 2026-10-02: 30 commits sobre `main` (el último, `9b4d8eb`, G2c del
2026-09-29), worktree `Leda-PM-worktrees/alta-y-google` limpio, código todavía con el
nombre Prisma, y su `.env` todavía con `PRISMA_*`, apuntando a la base `prisma`. **Esa base
ya no existe**: se borró el 2026-10-02 con volcado final, y no tenía las tablas de `0100` ni
`0101` (la rama se probó con bases efímeras), así que no se perdió nada propio de la rama.
Sus tres copias locales (`-pre-rebase-0929`, `-pre-unificacion`, `-unificada-un-commit`) se
conservan.

Orden, aplicado igual que en `feat/flujo-de-un-mensaje`:

1. **Preparar.** Detener cualquier proceso que corra desde ese worktree. Árbol limpio.
   Correr la suite completa de la rama **antes** del renombre y registrar el resultado, que
   es la línea de base contra la que se compara.
2. **Las copias locales.** Compararlas con `auxiliar/alta-y-google` (`git range-diff` o
   `git cherry`). Borrar una copia sólo si todo su contenido está en la rama; si no, se
   conserva o se rescata lo que falte.
3. **Renombrar la rama antes de traer `main`.** Desde el worktree:
   `D:/Proyectos/Leda-PM/.venv/Scripts/python.exe D:/Proyectos/Leda-PM/tools/renombrar_a_leda.py aplicar`.
   Commit `refactor: rename the product from Prisma to Leda across the repository`.
   Después, `renombrar_a_leda.py verificar <commit previo> HEAD` tiene que dar differ,
   missing y added en 0, y `restos` sólo tiene que mostrar tokens protegidos. **Por qué
   antes:** así `main` y la rama tienen el mismo renombre, y el merge sólo muestra
   conflictos reales. Al revés, cada archivo que la rama tocó chocaría con su versión
   renombrada.
4. **Traer `main`** (`git merge main`) y resolver sólo conflictos reales:
   - Con `main` llega `tests/historia_previa_a_leda.py`. La rama tiene en
     `tests/test_task_intake.py` lecturas `git show {BASELINE_REF}:db/esquema.sql`: tienen
     que pasar por `esquema_base()`, como en `main`. Es un conflicto esperable en ese
     archivo.
   - Las migraciones `0100` y `0101` no chocan en número con `0026` y `0027` (rama de
     flujo), pero `db/esquema.sql` tiene que converger: lo comprueba el ensayo de paridad
     de la suite.
5. **`.env` y `.env.test`.** `renombrar_a_leda.py env .env .env.test`, que deja la copia
   `.env.antes-leda`. Esta rama además lee `PRISMA_CLAVE_CREDENCIALES`,
   `PRISMA_GOOGLE_CLIENT_ID` y `PRISMA_GOOGLE_CLIENT_SECRET`: quedan como `LEDA_…`.
   Comprobar que el código renombrado las lee (al 2026-10-02 no figuraban en el `.env` del
   worktree).
6. **Base nueva.** Crear una base propia para la rama (por ejemplo `leda_google`) con
   `python -m leda esquema`, más `importar`, `feriados`, `sembrar`, `modelo` y
   `administrador`, como `leda_flujo`. Poner su nombre en `dbname` de `LEDA_DB_URL` y de
   `LEDA_AUTHORITY_DB_URL`. La credencial de Google se guarda cifrada en la base: en una
   base nueva hay que cargarla de nuevo.
7. **Roles y membresías.** Los roles `leda_*` ya existen y el login de autoridad ya tiene
   `SET ROLE leda_gateway`. Si `0100` o `0101` crean roles nuevos o necesitan que un login
   pueda asumirlos, replicar la membresía con las mismas opciones. Es la lección del
   renombre: revisar `pg_auth_members`, no sólo roles y bases.
8. **Verificar.** La suite completa tiene que dar el mismo resultado que la línea de base
   del paso 1. RDD por tramos de todo lo escrito a mano (el commit mecánico se prueba con
   el paso 3). Prueba real por Telegram de un alta con correo sobre la base nueva.
9. **Integrar a `main` y seguir desde ahí.** Merge de la rama a `main`. Desde ese momento
   el trabajo de alta y Google (G2c-2, G2d y lo que siga del documento de la rama) se
   continúa en `main`, con su documento `odd/tasks/alta-y-google.md` traído de la rama,
   que es la versión completa. Después: borrar el worktree `alta-y-google`, la rama y sus
   copias locales (si el paso 2 confirmó que no tienen nada propio), las copias
   `.env.antes-leda` y, si ninguna rama viva conserva el nombre viejo, el script.

## Repositorio en GitHub: `arields85/leda` (2026-10-02)

Decisión del usuario: no renombrar `arields85/prisma`. Queda **congelado como respaldo**
(sin más push) y se crea **`arields85/leda`, público**, con toda la historia. Desde ahora los
push van ahí. Cuando `arields85/prisma` quede realmente obsoleto, se borra.

- Remotos locales: `origin` pasa a apuntar a `arields85/leda`. El remoto viejo queda como
  `respaldo-prisma`, sólo de lectura por convención.
- Se suben `main`, `feat/flujo-de-un-mensaje`, `auxiliar/alta-y-google`, sus tres copias
  locales (como respaldo, porque tienen commits sin equivalente verificado) y el tag
  `pre-renombre-leda`.
- Control previo (el repo es público): se escaneó la historia sin publicar. Las
  coincidencias son ejemplos (plantilla `.env.ejemplo`, contraseñas de muestra en las
  guías, datos de prueba y un token falso), y la verificación byte a byte prueba que son el
  mismo contenido ya público en `arields85/prisma`, renombrado.
- **Engram no se pierde.** Según su documentación (`DOCS.md`, "Detection algorithm"),
  la identidad del proyecto es una etiqueta privada guardada en `.git` que se conserva a
  través de cambios de remoto y mudanzas del repositorio. Como seguro se fijó con
  `engram init prisma-pm` (`.engram/config.json`, la máxima prioridad). El nombre interno
  queda `prisma-pm`, porque Engram no permite renombrar proyectos (`projects merge` sólo une
  variantes de separador) y forzar `leda` partiría las memorias.

## Leda funciona correctamente: la condición para limpiar

Pedido del usuario: dejar asentado que Leda funciona antes de borrar nada de Prisma. Se
considera cumplido sólo con **las cuatro** comprobaciones registradas aquí, con comando, fecha
y resultado:

1. **Suite completa en verde** sobre el código renombrado, en `main` y en
   `feat/flujo-de-un-mensaje`, con el mismo resultado que antes del renombre (sin fallas
   nuevas).
2. **Verificación determinista** (playbook §6.1): todo archivo que no sea pura sustitución
   está listado y justificado, y toda aparición restante de `prisma` tiene su motivo.
3. **Prueba real por Telegram** sobre `leda_flujo` desde la rama renombrada: un alta
   conversada de punta a punta (Ariel, Ismael o Marcos), sin incidentes nuevos, y la
   respuesta visible, PostgreSQL y la auditoría coinciden.
4. **Nada lee los nombres viejos:** el listener y los comandos corren sin ninguna variable
   `PRISMA_*` en el `.env`, y no hay conexiones a las bases `prisma*`.

Registro:

1. Cumplido. `main` renombrado: 2286 passed (`481af9b`, 2026-10-01). Flujo renombrada: 3432
   passed (`1adcfd0`, 2026-10-02). Los dos son iguales a sus resultados previos.
2. Cumplido. `main`: 373/373 pura sustitución (`0bbc21b`→`58d2bed`). Flujo: 408/408
   (`aeea562`→`3b75117`). Restos justificados en R5 y R9.
3. Cumplido (2026-10-02, 09:12). Alta conversada de Marcos de punta a punta sobre
   `leda_flujo`: cuatro turnos, "Enviar a aprobación" (09:02:35), aviso a Ismael (09:02:44),
   confirmación de Ismael (09:12:30) y tarea «Revisar las alarmas del tablero de la línea 2»
   creada desde su borrador, `asignada` a las 09:12:36, con el aviso a Marcos. La auditoría
   (`enviar_ingreso_tarea_a_aprobacion`, `avisar_aprobacion_ingreso_tarea`,
   `confirmar_borrador_tarea`) coincide con la conversación y la base. El único incidente
   nuevo fue el permiso de `leda_gateway` (R9), un defecto del renombre que se corrigió
   antes de la confirmación final; después de eso no hubo ninguno más.
4. Cumplido (2026-10-02). `refactor/renombre-a-leda` entró a `main` por fast-forward
   (`2d56952`). El `.env` y el `.env.test` del checkout principal quedaron renombrados con
   copia, con 0 claves `PRISMA` y sin "prisma". Se borraron `src/prisma` (sólo 33 `.pyc`) y
   `src/prisma.egg-info`, y el paquete se reinstaló en modo editable como `leda` (`prisma`
   ya no se puede importar). `python -m leda estado corework` corre contra la base `leda`,
   y no hay conexiones a bases `prisma*`. El worktree congelado `alta-y-google` conserva su
   `.env` viejo hasta que se retome (no está en uso).

**RDD sobre el renombre en `main`.** El tramo `647fcc7..074d044` no se puede revisar con
RDD: el commit mecánico `58d2bed` (290 archivos) supera el presupuesto del revisor
(`lens_context_budget_exceeded`, linaje `review-c9f2673498baa540`, sin autoridad creada).
Tampoco se puede partir, porque es una sustitución atómica y cualquier corte intermedio
deja el código roto. Su prueba es la verificación determinista (373/373, playbook §6.1).
Todo lo escrito a mano sí pasó por RDD y quedó aprobado: script y ADR
(`review-ea0a694a9f86e303`, `review-f74eddb63ce99ff0`, `review-5be02e0e1d31830a`,
`review-72ee922c2dfa1f26`) y arreglo de las pruebas (`review-ff793423fcb4995a`, y en la
rama de flujo `review-7ea5dbadc4239272`).

**Conclusión: Leda funciona correctamente (2026-10-02).** Ya se puede hacer la limpieza
(R11) siguiendo la tabla. Los borrados destructivos (bases, roles) se confirman con el
usuario antes de ejecutarse.

## Limpieza posterior

Ningún punto se hace antes de que se cumpla su condición. Mientras tanto, todo lo de esta lista
**se conserva como respaldo** y sirve para volver atrás. Lo que no está en la lista no es
respaldo del renombre.

| Qué | Cuándo se puede borrar | Cómo |
|---|---|---|
| Bases `prisma` y `prisma_flujo` | **Hecho** (2026-10-02) | Volcados finales verificados con `pg_restore --list` (unas 530 entradas y 48 tablas con datos cada uno): `db/respaldos/prisma-final-antes-de-borrar-20261002.dump` y `db/respaldos/prisma_flujo-final-antes-de-borrar-20261002.dump`. Después, `drop database` |
| Volcados intermedios viejos en `db/respaldos/` (12: 10 `prisma-antes-*` y 2 `prisma_flujo-antes-*`, del 27/09 al 01/10) | **Hecho** (2026-10-02) | Borrados. Quedan sólo los tres `*-final-antes-de-borrar-20261002.dump` |
| Worktree `Prisma-PM-worktrees/renombre-a-leda` y su rama `refactor/renombre-a-leda` (ya en `main`; su `.env` tiene secretos) | **Hecho** (2026-10-02) | Worktree borrado (sólo tenía cachés y copias del `.env`); rama borrada, ya estaba en `main` |
| Bases residuales `prisma_test_*` y `prisma_diag_*` | **Hecho** (2026-10-02) | Se borraron 15 (8 `prisma_diag_*` y 7 `prisma_test_*`), todas sin conexiones; `prisma` y `prisma_flujo` siguen como respaldo |
| Membresía del login de autoridad en `prisma_gateway` | **Hecho** (2026-10-02) | Se fue con el rol |
| Roles `prisma_*` del servidor | **Hecho** (2026-10-02) | Primero los 5 `prisma_gateway_test_*`. Después se volcó el esquema `prisma` viejo de la base `postgres` (sesiones 1 y 2; `db/respaldos/postgres-esquema-prisma-final-antes-de-borrar-20261002.dump`, 508 entradas, 46 tablas con datos, verificado), se hizo `drop schema prisma cascade` en `postgres` y se borraron `prisma_app`, `prisma_admin`, `prisma_gateway` y `prisma_owner`. No queda ningún rol `prisma*`. Verificado después: la autoridad asume `leda_gateway` y `leda estado` corre en las dos bases |
| Variables `PRISMA_*` que queden en algún `.env` | **Hecho** en los checkouts en uso (`main`, flujo). El worktree congelado `alta-y-google` las conserva hasta que se retome; ahí se le aplica el script | — |
| Copias `.env.antes-leda` (las deja `renombrar_a_leda.py env`, ignoradas por Git) | **Hecho** (2026-10-02) | Borradas en `main` y en flujo (`.env.antes-leda` y `.env.test.antes-leda`) |
| Tag `pre-renombre-leda` | Nunca hace falta borrarlo: es el registro de dónde estaba todo antes | — |
| Ramas `auxiliar/alta-y-google-pre-*` y `-unificada-un-commit` (locales) | **No se borran por la limpieza del renombre.** Son parte del trabajo de alta y Google (rama aparte, `odd/tasks/alta-y-google.md`, ADR 0010), que se retoma para integrarlo. Se decide sobre ellas al retomar esa rama, después de comparar su contenido | — |
| `feat/flujo-variante-a` (local, remota y su worktree) | **Hecho en local** (2026-10-02, decisión del usuario) | Worktree y rama local borrados. Sus 20 commits ya estaban todos en `feat/flujo-de-un-mensaje` (0 fuera), y el experimento A/B se cerró el 2026-10-01 (ADR 0014). Queda la rama remota `origin/feat/flujo-variante-a`, que se borra cuando el usuario decida el push |
| Script `tools/renombrar_a_leda.py` | Cuando `auxiliar/alta-y-google` esté renombrada (R12, pasos 3 y 5) y ninguna otra rama viva conserve el nombre viejo | Borrar el archivo |
| `tests/historia_previa_a_leda.py` | **Nunca**: las pruebas de migración leen commits anteriores al renombre y lo necesitan siempre. No es un resto de Prisma | — |
| Carpeta de memoria vieja `~/.claude/projects/D--Proyectos-Prisma-PM` (después de R13) | **Hecho** (2026-10-02, autorizado por el usuario) | Borrada después de comprobar que los 18 archivos de memoria estaban en `D--Proyectos-Leda-PM`; se perdieron las transcripciones viejas (372 MB). Queda `D--Proyectos-Prisma-PM-worktrees-alta-y-google` (sólo dos transcripciones de las sesiones de ese worktree, 50 MB, sin memoria ni trabajo de la rama): por decisión del usuario se borra después de integrar R12 |
| Repositorio `arields85/prisma` (respaldo congelado) y el remoto local `respaldo-prisma` | Cuando el usuario lo dé por obsoleto | Borrar el repositorio en GitHub (lo hace o lo autoriza el usuario) y `git remote remove respaldo-prisma` |
| Carpeta, worktrees y repositorio de GitHub con el nombre viejo | Cuando el usuario decida renombrarlos (fuera de alcance) | Lo hace el usuario; el agente actualiza después `.venv`, rutas y memoria |
