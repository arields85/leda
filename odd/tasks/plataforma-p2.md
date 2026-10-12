# Plataforma, porción 2: la puerta de administración y la carga de tareas

**Rama:** `feat/plataforma` · **Carpeta:** `D:\Proyectos\Leda-PM-worktrees\plataforma`
**Abierta:** 2026-10-12 · **Copia en Engram:** tema `odd/plataforma-p2/tasks` (proyecto `prisma-pm`)
**Diseño:** [ADR 0022](../../docs/decisions/0022-plataforma-web-de-tareas.md), decisiones 6, 7, 9, 10, 11, 12,
15 y 16.2. La porción anterior, en [`plataforma-p1.md`](plataforma-p1.md).

## Objetivo

Que un administrador cargue una tarea comprometida desde la web, por la puerta de administración, con
los controles de la decisión 9, su evento, su auditoría (quién la cargó y quién la decidió) y sin poder
romper el aislamiento entre espacios.

## Por qué ahora, antes de probar la porción 1 en el celular

El ADR pide probar cada porción en el celular antes de la siguiente. El usuario lo salteó esta vez
(2026-10-12: "saltemos la regla en esta ocasión así ganamos tiempo hasta que pueda hacer las pruebas"):
él hace la prueba por Telegram y la de la porción 1 en el celular; mientras tanto se construye esta.

## Alcance

- **La puerta de administración** (decisiones 10 y 12): enlace de un solo uso y sesión de un
  administrador de plataforma, con su propia cookie, separada de la del equipo. Abarca todos los
  espacios; el enlace lo emite por ahora un comando de consola (como en la porción 1). Que lo ofrezca el
  bot de administración toca el Motor: va después de juntar las ramas.
- **La carga en la base** (decisiones 9, 11 y 15): una función `security definer` que valida, escribe la
  tarea y su evento `asignada` y deja la auditoría. El espacio lo elige el administrador entre los que
  existen y la función comprueba en la base que su rol de plataforma está vigente: nunca se confía en el
  valor sin esa comprobación (riesgo 4 de `docs/STATUS.md`). Un doble envío del formulario no carga dos
  tareas (clave de un solo uso).
- **El formulario** (decisión 6 y la vista ancha): en el aspecto "9 · Terminal", pensado para la
  computadora y usable en el celular.

**Fuera de esta porción, por ahora:**
- Los avisos de la decisión 7 (al responsable y a quien revisa): son avisos del motor; después de juntar
  las ramas.
- Que Leda proponga un criterio comprobable cuando el escrito es vago: usa la IA real; necesita permiso
  para probarlo.
- Lo que el usuario todavía no decidió (abajo).

## Restricciones

- No tocar `src/leda/motor/` ni las bases `leda`, `leda_flujo` y `leda_motor`.
- Migraciones desde la `0061` (la `0060` es de la P1-6), cada una con su rollback y su ensayo de paridad;
  `db/esquema.sql` al día; tablas nuevas en el lazo de RLS o declaradas como excepción con su porqué.
- Las mismas de la porción 1 (`plataforma-p1.md`, "Restricciones").

## Tareas

Ruta: un escritor delegado por tarea (dos o más archivos no triviales cada una).

- [x] **P2-1 · La puerta de administración:** tablas del enlace y de la sesión del administrador
      (sin espacio: un administrador abarca todos), canje con el botón "Entrar", cookie propia, corte
      de sesiones, comando `enlace-admin` y `/app/admin/api/yo`. Garantías: un integrante sin rol de
      plataforma no abre la puerta; un rol revocado corta la sesión en el pedido siguiente; la cookie del
      equipo no abre la de administración ni al revés.
- [ ] **P2-2 · La carga en la base:** el día hábil del espacio en SQL (`work_calendar` y `holiday`, como
      `calendario.es_habil`); la función de carga con los controles de la decisión 9 (objetivo,
      responsable, fecha, criterio y evidencia; fecha hábil y no pasada; integrante activo; quien la
      hace no la revisa, incluido el caso de la autoridad final sin aprobador); el evento `asignada`; la
      auditoría con quién la cargó y quién la decidió; la clave de un solo uso. La API de escritura con
      protección contra pedidos cruzados.
- [ ] **P2-3 · El formulario:** elegir espacio, objetivo, responsable (con "sin conectar" a la vista),
      fecha (sólo días hábiles), criterio y evidencia (la de la política del área como punto de
      partida); vista previa y confirmación; la vista ancha de escritorio.
- [ ] **P2-4 · Documentos:** `docs/capacidades.md`, `docs/product/plataforma-pendientes.md`,
      `PRUEBA-LOCAL.md` y este documento con la evidencia.

## Para decidir (el usuario)

Mientras no se decida, lo más restrictivo; abrirlo después no rehace nada.

1. **Los objetivos.** Toda tarea cuelga de un objetivo, pero el ADR no dice quién crea los objetivos ni
   dónde. Hoy los crea sólo el paquete del espacio al importarse (uno por frente). Mientras tanto, el
   formulario deja elegir sólo entre los objetivos que ya existen.
2. **Las esperas.** Si "esta tarea espera a aquella" se carga en el mismo formulario. Mientras tanto, no.
3. **Quién "decidió" la tarea.** La auditoría guarda quién la decidió (ADR 0017, decisión 2). Mientras
   tanto, el formulario pide elegir a un integrante activo del espacio, sin restringir su rol.

## Criterio de aceptación

Las garantías de la carga y de la puerta, en verde; la suite `tests/garantias` completa, en verde; cada
commit de código revisado por RDD; una tarea cargada desde la web aparece en "Tus tareas" de su
responsable.

## Progreso y evidencia

### P2-1 · La puerta de administración (2026-10-12)

**Ruta:** delegated (2+ non-trivial files): migración, esquema, `web_app.py`, `cli.py` y sus pruebas.

**Qué quedó:**
- Migración `0061_la_puerta_de_administracion.sql` (con su rollback y `db/esquema.sql` al día):
  `enlace_de_administracion` y `sesion_de_administracion`, de un `app_user` y sin `workspace_id`
  (un administrador abarca todos los espacios), sin política por espacio y sin ningún privilegio
  para `leda_app`. Funciones `security definer` de `leda_owner`: `emitir_enlace_de_administracion`
  y `cortar_sesiones_de_administrador` sólo para `leda_admin` (la consola);
  `canjear_enlace_de_administracion`, `sesion_de_administracion_vigente` y
  `cerrar_sesion_de_administracion` (la sesión propia, por el hash de su token) sólo para
  `leda_app`. El rol `administrador` de `platform_role` se comprueba al emitir, al canjear y en
  cada pedido; revocado, la sesión queda cortada (`dejo_de_ser_administrador`). Auditoría sin
  espacio, aunque quien llama tenga uno fijado (`auditar_acceso_de_administracion`).
- `web_app.py`: `GET` y `POST /app/admin/entrar/{token}` (el mismo botón y las mismas cabeceras
  que la porción 1), cookie `leda_admin` (`HttpOnly`, `Secure`, `SameSite=Strict`,
  `Path=/app/admin`, 400 días), `GET /app/admin/api/yo` (nombre y espacios) y
  `POST /app/admin/salir`. Las páginas de `/app/admin/` son las de la web; su API, su enlace y
  salir nunca caen en el índice.
- `cli.py`: `python -m leda enlace-admin <nombre>` y `cortar-sesiones-admin <nombre>`; a quien no
  tiene el rol vigente, no.
- Pruebas: `tests/garantias/test_puerta_de_administracion.py` (nueva), más
  `test_web_servida.py`, `test_capacidades.py` (`TABLAS_POR_FUNCION`), `test_migraciones.py`
  (`TABLAS_DE_LA_ADMINISTRACION`) y `tests/test_cli_plataforma.py`.

**Evidencia:**
- RED, antes del código: `pytest -q tests/garantias/test_puerta_de_administracion.py
  tests/garantias/test_web_servida.py tests/test_cli_plataforma.py` → 34 failed, 27 passed.
- GREEN, lo mismo → 61 passed.
- `pytest -q tests/garantias/test_puerta_de_administracion.py tests/garantias/test_enlace_y_sesion.py
  tests/garantias/test_api_de_la_plataforma.py tests/garantias/test_web_servida.py
  tests/garantias/test_capacidades.py tests/garantias/test_frontera.py
  tests/garantias/test_aislamiento.py tests/garantias/test_migraciones.py
  tests/test_cli_plataforma.py` (con `LEDA_TEST_DB_URL` al servidor local de pruebas) →
  155 passed (16 min 30 s), con el ensayo de paridad y de rollback de la `0061`.
- Commit de código y pruebas: `16f630ca`. La suite `tests/garantias` completa y la revisión RDD:
  `PENDIENTE` (las corre el coordinador).

**Para confirmar con el usuario** (anotado en `docs/product/plataforma-pendientes.md`): el enlace
de la administración no vence por tiempo, como el del equipo; el rol `operador` no abre la
puerta; `/app/admin/api/yo` lista todos los espacios, también los importados sin activar.
