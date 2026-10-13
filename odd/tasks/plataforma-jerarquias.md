# La plataforma según la jerarquía del equipo (ADR 0023)

**Rama:** `feat/motor-de-conversacion` · **Abierta:** 2026-10-13 · **Copia en Engram:** tema
`odd/plataforma-jerarquias/tasks` (proyecto `prisma-pm`)

## Objetivo

Construir lo que decidió el usuario en el [ADR 0023](../../docs/decisions/0023-quien-crea-en-la-plataforma.md)
(aceptado el 2026-10-13), junto con las dos porciones que el [ADR 0022](../../docs/decisions/0022-plataforma-web-de-tareas.md)
tenía pendientes: que cada uno cree en la web lo que le toca según su lugar en el equipo, y que Leda ayude a
completarlo.

## Por qué

Hoy sólo la puerta de administración carga tareas, los objetivos y las jerarquías salen del pack, y "quién la
decidió" es un campo libre. El usuario quiere que se sepa por qué algo se atrasa (el módem en la pared → el
estante → los tornillos) y que el equipo se organice solo.

## Restricciones

- Cada porción con su diseño corto, test primero (RED → GREEN), sus garantías, revisión RDD por commit y su
  prueba real en el celular antes de la siguiente (ADR 0022, decisión 16). La prueba en el celular necesita al
  usuario y el túnel (`cloudflared`, autorizado para probar).
- Migraciones desde la `0067`, cada una con su rollback y su ensayo de paridad; `leda_motor` con respaldo
  previo (autorizado).
- Por chat no se crea nada (ADR 0017; anotado para más adelante en `docs/ROADMAP.md`).
- No tocar `nucleo/`. Las garantías de la mecánica las exige el código.
- **Antes de cada porción, partir de lo hecho:** el escritor lee "De qué se parte en cada porción" (abajo) y
  reusa esas piezas; lo que agregue nuevo lo justifica en el diseño corto.

## Orden de las porciones (acordado con el usuario, 2026-10-13: "si")

1. **Las esperas en el formulario** (0023, decisión 2).
2. **Los objetivos desde la web** (0023, decisión 1; tipo según dónde cuelga, punto 11).
3. **La carga por la web del equipo para Dirección y los referentes** (0023, decisión 3, puntos 2, 7 y 8), con
   el préstamo de personas.
4. **El pedido de más tiempo y el cambio de fecha** (0022, porción 3, decisión 8).
5. **La propuesta del integrante con la ayuda de la IA** (0023, decisión 3, puntos 3 a 6 y 9).
6. **Las jerarquías y los integrantes desde la web de Dirección** (0023, decisiones 4 y 5, puntos 1 y 10; con
   la porción 4 del 0022).

## Tareas

Ruta: cada porción, delegada (un escritor), porque toca base, servidor, web y pruebas.

### J1 · Las esperas en el formulario

- [x] **J1-1 · Mapa y diseño corto:** cómo carga hoy el formulario (`web/src/admin/LoadForm.tsx`, la API de
      carga, `dependency` y `evitar_ciclo_dependencia`), y qué cambia; escrito acá (abajo).
- [x] **J1-2 · Las garantías, primero en rojo:** no se elige una tarea de otro espacio ni una cerrada; un ciclo
      se rechaza con su motivo; la tarea que espera no pasa a en curso mientras la otra no terminó; la
      auditoría lo guarda. `tests/garantias/test_espera_al_cargar.py`: 14 en rojo antes de la 0067
      (sin la carga de 13 datos, sin `tareas` en las opciones, sin los textos), 14 en verde después.
- [x] **J1-3 · El servidor y la web:** el campo opcional "espera a" en el formulario y la carga. `980a8f2a`
      (la `0067`, su rollback, `esquema.sql`, `web_app.py` y las garantías) y `fb87d121` (el formulario y la
      revisión; `AdminApp.test.tsx`: 3 en rojo antes, en verde después).
- [x] **J1-4 · Verificación** (2026-10-13, sobre `fb87d121`): `pytest -q tests/garantias` 738 passed (13 min);
      `pytest -q tests/test_dependencias.py` 25 passed; `pytest -q tests/garantias/test_migraciones.py` 16
      passed (la paridad y el rollback, con la 0067); en `web/`, `npm test` 60 passed y `npm run build` bien.
      La revisión RDD de los dos commits la corre el coordinador.
- [ ] **J1-5 · Prueba real en el celular** (con el usuario).

**Diseño corto (J1-1, 2026-10-13).** Hoy el formulario (`LoadForm.tsx`) pide a
`GET /admin/api/espacios/{id}/opciones` (función `opciones_de_la_carga`) lo que se puede elegir y manda la carga
a `POST …/tareas` (`cargar_una_tarea` → función `cargar_tarea`, `security definer` de `leda_owner`, que comprueba
la sesión de administración, fija el espacio y devuelve todos los rechazos juntos). La base ya guarda las esperas
(`dependency`: `origen_task_id` es la esperada, `destino_task_id` la que espera) y la regla de §4 ya vive en ella:
`exigir_dependencias_resueltas` no deja pasar a `en_curso` mientras la esperada no esté `terminada` o `cancelada`, y
`evitar_ciclo_dependencia` rechaza un ciclo. Qué cambia (migración `0067_la_espera_al_cargar`):
- **Una sola espera por tarea, siempre bloqueante**, opcional (decisión 2: "un campo"); puede ser de otro objetivo
  del mismo espacio.
- **Qué se ofrece:** las tareas comprometidas y abiertas del espacio (`asignada`, `en_curso`, `bloqueada`,
  `en_revision`), con su responsable y su objetivo. Ni una cerrada ni una propuesta sin aprobar (punto 9: una
  propuesta nunca traba una tarea comprometida).
- **Qué rechaza `cargar_tarea`**, junto con lo demás: una tarea que no está en el espacio (la RLS no la encuentra:
  `no_existe`), una cerrada (`esta_cerrada`), una sin comprometer (`no_esta_comprometida`). Lee la esperada `for
  share`, para que no se cierre entre la comprobación y la espera.
- **El ciclo:** al cargar, la tarea es nueva y nadie la espera todavía, así que una sola espera no puede cerrar un
  círculo; el disparador sigue de guarda y, si alguna vez salta, la carga entera se deshace y vuelve como un rechazo
  más (`haria_un_ciclo`), con su texto, nunca como un error crudo.
- **La auditoría** de la carga guarda `espera_task_id` y `espera_tipo` (sólo con espera); la huella de la clave
  suma la espera sólo si la hay, así una carga sin espera queda exactamente como antes, también su idempotencia.
- **La firma:** `cargar_tarea` suma `p_espera_task_id uuid default null` al final (la de 12 se borra; mismo dueño,
  `search_path` y permisos). El rollback vuelve a la 0064 y no toca datos: una espera cargada queda como espera.
- **La web:** "espera a (opcional)", un `select` como los demás, y en la revisión, "espera a: <tarea>".
- `PENDIENTE` (con los avisos de la decisión 7 del ADR 0022, que todavía no existen): el aviso de §4 a los dos
  referentes cuando la espera cruza áreas.

### J2 a J6

Se detallan al llegar a cada una, con su diseño corto.

- [ ] **J2 · Los objetivos desde la web.**
- [ ] **J3 · La carga por la web del equipo (Dirección y referentes), con el préstamo.**
- [ ] **J4 · El pedido de más tiempo y el cambio de fecha.**
- [ ] **J5 · La propuesta del integrante con la IA.** Se aprovecha lo que ya existe (usuario, 2026-10-13: "no hay que inventar
      nada"): el cliente de la IA del motor (`motor/ia_real.py`, `desde_base`), los chequeos de la entrega
      (`entrega.puntos_del_criterio`, `problema_del_ejemplo`: nada de números ni nombres que nadie dijo) y
      la propuesta de título y criterio del alta del flujo congelado (`alta_turno.py` en la etiqueta
      `respaldo-flujos-antes-de-d`: `CAMPOS_PROPONIBLES`, el criterio que dice cómo se comprueba), como
      referencia para adaptar, no para copiar el flujo.
- [ ] **J6 · Las jerarquías y los integrantes desde la web de Dirección.**

## De qué se parte en cada porción (explorador de sólo lectura, 2026-10-13)

Pedido del usuario: "revisá si ya no tenemos algo creado que pueda servir de base para no arrancar de cero".

- **J2, los objetivos:** `herramientas._preparar_crear_objetivo` y `_crear_objetivo` (las comprobaciones, la
  vista previa y el evento de estado), la convención de tipos de la importación (`importador._importar_objetivo_inicial`:
  la raíz estratégica, cada frente operativo), la tabla `objective` (ya tiene `referente_membership_id`, sin
  usar), `opciones_de_la_carga` (ya trae los objetivos y los integrantes para elegir) y `cargar_tarea` como
  patrón de función de la base (sesión, clave de un solo uso, errores y avisos, auditoría); en la web,
  `FieldBlock`, `Counter`, `DatePicker` y la vista previa. Falta: la regla de qué tipo cuelga de cuál, una
  función `crear_objetivo` para la web, poner el referente y que sólo Dirección cree.
- **J3, la carga del equipo:** `cargar_tarea` entera (sólo cambia la puerta: la sesión del equipo en vez de la
  de administración), `tareas_que_ve` y `vistas_de` (ya distinguen Dirección y referentes), la regla de quién
  revisa (`quien_revisa_la_tarea`) y el pase de tareas del motor (`motor/pase.py`, `autoridad.regla_del_pase`)
  como antecedente de "una tarea para otra persona". Falta: guardar quién revisa una tarea en particular (el
  préstamo), la versión de `cargar_tarea` para la puerta del equipo y **los avisos de la decisión 7 del
  ADR 0022** (al responsable y a quien revisa), que quedaron pendientes en la porción 2
  (`plataforma-p2.md`): se construyen en la J3, junto con el aviso del préstamo.
- **J4, más tiempo y cambio de fecha:** la previsión del chat (`task_forecast`, la jugada `anotar_prevision`,
  los avisos `nueva_prevision`), `ancla.prevision_vigente`, la previsión que ya muestra la web, y el umbral
  de re-aprobación del pack (`corrimiento_de_fecha_dias: 3`), que se guarda y nadie lee. Falta: **la base no
  deja cambiar la fecha de una tarea** (`bloquear_estado_directo`), así que hace falta una función propia,
  auditada y con quién lo decidió; el pedido con su estado (pendiente, aceptado o rechazado); el bloque del
  referente en la web.
- **J6, las jerarquías y los integrantes:** las validaciones de la importación (`importador.validar`: una sola
  autoridad final, áreas y roles existentes, quién aprueba a quién sin ciclos ni a sí mismo), la importación
  de personas y áreas, los enlaces de activación (`onboarding.generar_enlaces`, `activar`,
  `pendientes_de_activar`), "conectado" que ya trae `opciones_de_la_carga`, el corte de sesiones con
  `dejo_el_equipo` al dar de baja, y las ideas rescatadas de la rama auxiliar (`plataforma-p2.md`). Falta: las
  funciones de la base para altas, bajas y cambios de área, rol, referente y quién aprueba, y las preferencias
  de avisos de Dirección.
- **La etiqueta congelada** sólo aporta el mismo `crear_objetivo` de hoy; nada de más tiempo ni de integrantes.

## Criterio de aceptación

Cada porción: sus garantías en verde, `tests/garantias` completa en verde, cada commit de código revisado por
RDD y la prueba del usuario en el celular. Al final, el ejemplo del usuario de punta a punta: Dirección crea
el objetivo del módem, el referente la tarea del estante, el integrante propone los tornillos con la ayuda de
Leda, quien revisa la aprueba y el atraso se explica por la espera.

## Entrega

Una sola rama, como hasta ahora: commits por unidad en `feat/motor-de-conversacion`, subida al cerrar cada
tramo (autorizado); `main` por avance rápido, cuando lo decida el usuario. Previsión: más de 400 líneas por
porción en las 3, 5 y 6; se revisan por tramos con RDD.

## Progreso y evidencia

- 2026-10-13: el usuario aceptó el ADR 0023 y este orden; documento creado.
- 2026-10-13: J1-1 a J1-4 hechas (escritor delegado; ruta delegada: base, servidor, web y pruebas). La
  `0067` todavía no está aplicada en `leda_motor` (la aplica el coordinador, con respaldo previo); sin ella,
  la carga desde la web falla porque el servidor ya manda la espera. Falta J1-5, la prueba en el celular.
