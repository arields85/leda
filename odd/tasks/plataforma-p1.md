# La plataforma, porción 1: la puerta del equipo, de sólo lectura

**Rama:** `feat/plataforma` · **Carpeta:** `D:\Proyectos\Leda-PM-worktrees\plataforma` (nacida de la rama
del Motor) · **Abierta:** 2026-10-12 · **Copia en Engram:** tema `odd/plataforma-p1/tasks` (proyecto
`prisma-pm`) · **Diseño:** [ADR 0022](../../docs/decisions/0022-plataforma-web-de-tareas.md), aceptado.

## Objetivo

Que cada integrante vea desde el celular lo mismo que le contaría Leda, según su puesto ("Tus tareas",
"Tu sector", "El equipo"), entrando con un enlace de un solo uso que deja la sesión abierta sin vencimiento
(ADR 0022, decisiones 3, 4, 5, 12, 13, 16.1, 17 y 18).

## Por qué en una rama aparte

La prueba por Telegram de la Fase C es el 2026-10-12 (día) y tiene que probar la Fase C tal como está. La
plataforma se construye en `feat/plataforma`; después de la prueba, la rama del Motor pasa a `main` y la
plataforma suma los arreglos que haya dejado la prueba (usuario, 2026-10-12).

## Alcance de esta noche (sin tocar la conversación)

Entra: la base (enlace de un solo uso y sesión; quién ve qué en listas), la API interna, la web con el
aspecto de la "9 · Terminal" y un comando de consola para emitir y cortar un enlace (para probar sin el chat).

**No entra esta noche** (va después de la prueba por Telegram, con el usuario):
- que Leda ofrezca el acceso por chat y el corte por "perdí el celular" (tocan el motor de conversación:
  primero su conversación de prueba, después una ronda con la IA real con permiso del usuario);
- la prueba en el celular (necesita que la PC sea alcanzable: IP de la red local o un túnel; una cookie
  `Secure` pide HTTPS fuera de `localhost`);
- ninguna ronda con la IA real, nada a `main`, nada remoto.

## Restricciones

- **No tocar `src/leda/motor/`** esta noche: si la prueba de mañana deja arreglos, se suman sin choque.
- **Migraciones desde la `0057`**, cada una con su rollback en `db/rollbacks/` y plegada en
  `db/esquema.sql`; las pruebas las descubren solas y exigen paridad. Si un arreglo de la Fase C necesita
  una migración, la de la plataforma se renumera al juntar las ramas.
- **Garantías de la base** (`tests/garantias/test_aislamiento.py`): toda tabla con `workspace_id` con
  `row level security` forzado o en `EXCEPCIONES_SIN_RLS` sin privilegios para `leda_app`/`leda_gateway`;
  toda función `security definer` con dueño que no saltea RLS, `search_path` fijo terminado en `pg_temp`
  y sin `execute` para PUBLIC. El espacio sale de la sesión, nunca del pedido (decisión 11).
- **Tokens:** sólo el hash SHA-256, como `acceso_tarea` (0036). El enlace sirve una vez; la sesión no
  vence y se revalida en cada pedido (membresía activa); se corta si la persona deja el equipo o si un
  administrador la corta (decisiones 4 y 12).
- **Quién ve qué** (decisión 3): integrante, sus tareas, las que espera de otros y las que otros esperan de
  él, sin los atrasos ajenos; referente (`area.referente_membership_id`), todo su sector con fechas,
  atrasos y bloqueos; autoridad final (`rol.autoridad_final`), todo el espacio, sin rankings. Una sola
  regla en SQL que extiende `puede_ver_tarea` (decisión 13).
- **La web:** React, TypeScript, Vite, Tailwind, Lucide (decisión 17), en `web/`, compilada y servida por
  la misma aplicación (`src/leda/entrada.py`), mismo origen, cookie `HttpOnly`, `Secure`,
  `SameSite=Strict`. Versiones exactas en `package.json`.
- **El aspecto** (decisión 18): oscuro, grises, JetBrains Mono; color sólo en los estados que tienen algo
  (vencida `#FFC14D`, trabada `#FF7A6B`, en curso `#9BE39B`, entregada `#8FD0FF`; en 0, gris); cabezal de
  la "11 · Plano"; barra "C" por días hábiles con "hoy" bajo el segmento blanco y la fecha de entrega bajo
  el último; "quedan N días" arriba de la tarjeta en curso; botón "> contarle algo a leda" blanco, con el
  marco de las tarjetas y sin cursor. Referencia: el lienzo https://claude.ai/artifact/VwC3sCvufFZ7DUkv3yJt7f
  (tableros "9 · Terminal", "9b" y "Barras de progreso"; se leen con la herramienta Artifact, `read`).
- Textos de la interfaz en castellano (como Leda); identificadores como el resto del código.

## Cómo se trabaja en la carpeta de la plataforma

- **Pruebas:** desde `D:\Proyectos\Leda-PM-worktrees\plataforma`, con el Python del Motor y el servidor
  local como base descartable (el superusuario local entra sin contraseña; no hace falta `.env.test`, que
  una regla impide copiar):
  `LEDA_TEST_DB_URL="postgresql://postgres@localhost:5432/postgres" ../motor-de-conversacion/.venv/Scripts/python.exe -m pytest -q <pruebas>`
  (comprobado el 2026-10-12: `tests/garantias/test_pagina_de_la_tarea.py`, 30 passed).
- **Qué código corre** (comprobado el 2026-10-12): el `.venv` del Motor tiene `leda` instalado apuntando a
  `motor-de-conversacion/src`. `pytest` antepone el `src/` de esta carpeta y prueba el código de la
  plataforma; un comando suelto (`python -m leda …`, `python -c …`) corre el del Motor salvo con
  `PYTHONPATH=src`.
- **Nada toca las bases de verdad:** cada corrida crea `leda_test_<azar>` y la borra. Los roles `leda_*`
  son del servidor entero (compartidos con `leda_motor`): ninguna migración crea, altera ni borra roles.
- **El puerto 8000 es de la prueba por Telegram:** ningún servidor (uvicorn, vite) queda corriendo; para
  mirar algo, otro puerto, y se cierra.
- **Node 24 y npm 11** instalados; no hay `package.json` todavía.
- **Commits** en `feat/plataforma`, uno por tarea, sin líneas de atribución. **RDD** por commit de código:
  `tools/rdd_ciclo.py <carpeta temporal> <base>` en una carpeta `../_rdd-<nombre>` desprendida, que se
  borra al terminar. La primera base es `093eb33c` (donde nace la rama).
- La rama se puede subir a `origin` como respaldo (misma autorización que la del Motor).

## Tareas

Ruta: escritor delegado en cada una (dos o más archivos no triviales); el coordinador revisa, corre una
comprobación y hace la revisión RDD. Estimación total: más de 400 líneas; cada tarea es su commit.

- [x] **P1-0 · El guion de la prueba de mañana** (rama del Motor, sólo documentos): comprobar que
      `docs/product/guion-telegram-fase-c-parte-1.md` cubre lo construido después del 2026-10-08 (trabas
      y quién destraba, delegar, apodos, el formato de la cocina, la lista del detalle); si no, sumar los
      pasos que falten, como hilo numerado (quién, texto exacto, lo esperado).
- [x] **P1-1 · El enlace y la sesión** (migración `0057`): tablas del enlace de un solo uso y de la sesión
      (sólo hashes; membresía; creada, último uso, cortada y motivo), funciones `security definer` para
      emitir el enlace, canjearlo por una sesión (una sola vez), leer la sesión vigente (revalida la
      membresía y anota el último uso) y cortarla; auditoría de emitir, canjear y cortar. Pruebas de
      garantías: el enlace no sirve dos veces, una sesión cortada o de alguien que dejó el equipo no
      entra, aislamiento entre espacios, catálogo de dueños y RLS, rollback y paridad.
- [ ] **P1-2 · Quién ve qué en listas** (migración `0058`): la función de lista por vista ("tus":
      mías, espero, me esperan; "sector"; "equipo") que extiende `puede_ver_tarea`, sin atrasos ajenos
      para el integrante; qué vistas tiene cada persona. Pruebas por puesto.
- [ ] **P1-3 · La API interna:** canje del enlace (`/app/entrar/{token}` → cookie y redirección a la
      web), `/app/api/yo` (quién es y qué vistas tiene) y `/app/api/tareas?vista=…` (panel por estado,
      semana del calendario del espacio con los días en que vence algo, y cada tarea con su estado, su
      fecha, sus días hábiles para la barra y la cadena de esperas); cabeceras como las de la página de
      la tarea; `TestClient` con `https`. Comando de consola para emitir el enlace de una persona y para
      cortar sus sesiones.
- [ ] **P1-4 · La web:** `web/` con Vite, React, TypeScript, Tailwind y Lucide; los tokens del aspecto;
      las piezas (cabezal, panel de estados, tira de la semana, tarjeta, barra de días, árbol de esperas,
      botón); "Tus tareas", "Tu sector" y "El equipo"; compilada a `web/dist` y servida en `/app`.
      Comprobaciones: tipos, pruebas de las piezas (vitest), compilación, y una prueba de Python que la
      sirve; control del ancho de un teléfono (390 px).
- [ ] **P1-5 · Documentos:** `docs/capacidades.md`, `docs/product/plataforma-pendientes.md`, cómo
      levantarla para probar (`PRUEBA-LOCAL.md`) y este documento con la evidencia.

**Después de la prueba por Telegram** (con el usuario): juntar las ramas; Leda ofrece el acceso por chat
y el corte por "perdí el celular" (conversación de prueba, ronda con la IA real con permiso); la prueba en
el celular del usuario (cierre de la porción).

## Criterio de aceptación

Con datos ficticios, una persona entra con su enlace, la sesión queda abierta, ve exactamente lo que su
puesto le permite con el aspecto de la "9 · Terminal", y el enlace usado o una sesión cortada no entran.
Lo prueba primero `TestClient` y después el usuario en su celular.

## Progreso y evidencia

- 2026-10-12: rama y carpeta creadas desde `093eb33c`; las pruebas corren desde la carpeta (30 passed).
  `leda_motor` al día hasta la `0056` para la prueba de mañana (en la rama del Motor, `6fc7449f`).
- 2026-10-12, noche. **P1-0** (rama del Motor, `6faafce6`): el guion suma la segunda parte, pasos 22 a
  48 (apodos, quién destraba, la pregunta sin contestar, pasar una tarea, enlace y detalle ajeno, la
  lista, el informe al grupo); lo no comprobable, marcado "(a observar)". La prueba del 2026-10-08 había
  dejado "Programar PLC" entregada y "Dashboard" terminada: `leda_motor` se recreó con respaldo
  (`18828013`, detalle en `docs/STATUS.md`).
- **P1-1** (`db782e71`, escritor delegado: dos archivos no triviales): migración `0057`,
  `enlace_de_entrada` y `sesion_web` (sólo hashes, RLS forzado, sin privilegios para `leda_app`), cinco
  funciones `security definer` (emitir, canjear, sesión vigente, cortar una, cortar las de una persona),
  auditoría sin el token. El enlace no vence por tiempo (como la `0036`): deja de servir al canjearse, al
  emitirse otro o al cortarse las sesiones. RED: 25 fallas (`UndefinedFunction`); GREEN: 26 passed.
  `pytest tests/garantias/test_capacidades.py tests/garantias/test_frontera.py`: 7 passed (la de la
  frontera corre todas las garantías en otro proceso). RDD `review-ce739a56c466ff4c`, aprobada.
  Advertencias sin arreglar: dos emisiones simultáneas para la misma persona hacen fallar la segunda con
  un error en vez de reemplazar; un enlace sin canjear de alguien que dejó el equipo vuelve a servir si lo
  reincorporan; la prueba de la carrera no prueba contención real. Las funciones sólo las ejecuta
  `leda_app`: el comando de consola (P1-3) las llama dentro de `espacio()`; `sesion_vigente` mira la
  membresía activa, no el espacio.
