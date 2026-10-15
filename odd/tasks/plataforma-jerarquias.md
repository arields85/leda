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

## Orden de las porciones (acordado con el usuario, 2026-10-13; reordenado el mismo día)

**Regla del usuario:** "la IA debe ayudar desde el principio con todo lo que pueda". Por eso la ayuda de la
IA al cargar va segunda, sobre el formulario que ya existe, y cada porción siguiente la trae desde el primer
día donde sirva (por ejemplo, proponer el nombre o el tipo de un objetivo a partir de lo que se describe).

1. **J1 · Las esperas en el formulario** (0023, decisión 2).
2. **J2 · La ayuda de la IA al cargar, para todos** (0023, punto 4): se describe como se habla y Leda completa
   título, criterio, fecha y evidencia; primero en el formulario de la puerta de administración.
3. **J3 · Los objetivos desde la web** (0023, decisión 1; tipo según dónde cuelga, punto 11).
4. **J4 · La carga por la web del equipo para Dirección y los referentes** (0023, decisión 3, puntos 2, 7 y 8),
   con el préstamo de personas y los avisos de la carga.
5. **J5 · El pedido de más tiempo y el cambio de fecha** (0022, porción 3, decisión 8).
6. **J6 · La propuesta del integrante** (0023, decisión 3, puntos 3 a 6 y 9); necesita la puerta del equipo
   de la J4.
7. **J7 · Las jerarquías y los integrantes desde la web de Dirección** (0023, decisiones 4 y 5, puntos 1 y 10;
   con la porción 4 del 0022).

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
      **RDD:** `review-9a7a5167ab61833e` (`980a8f2a`) y `review-b2b971d7afdbe9bc` (`fb87d121`), aprobadas.
      Advertencias: el texto del ciclo depende del mensaje del disparador (`db/esquema.sql:3522`); la lista de
      tareas para elegir no tiene tope (`0067:88`). Sugerencia: una espera elegida que dejó de estar abierta
      se manda sin que se vea (`draft.ts:40-43`).
- [x] **J1-5 · Prueba real en el celular** (con el usuario; pasada el 2026-10-13: "ahora si, perfecto").
      En el celular cargó "Poner tornillo" (de Lucas) que espera a "Cablear tablero de la máquina 3": la espera,
      bloqueante, y la auditoría de la carga con `espera_task_id`, en `leda_motor`. Tras dos rondas de arreglos
      (J1-6 y J1-7), los últimos detalles a pedido del usuario: un color propio para lo que falta,
      `--color-falta: #ff931f` (`27f13459`, `a2976722`; las vencidas siguen con el suyo), y el ícono
      `CircleAlert` de Lucide en vez del "!" (`b45778eb`).
      Preparación: el túnel (`cloudflared tunnel --no-autoupdate --url http://127.0.0.1:8000`), la web
      reiniciada (`.venv\Scripts\python.exe -m uvicorn leda.entrada:app --host 127.0.0.1 --port 8000
      --no-access-log`), y el usuario emite su enlace con `$env:LEDA_BASE_URL = "<dirección del túnel>"` y
      `.venv\Scripts\python.exe -m leda enlace-admin Ariel`. Guion: (1) abre el enlace en el celular y toca
      "Entrar" → la puerta de administración; (2) empieza a cargar "Colocar el estante" como siempre; (3) el
      campo "Espera a" muestra sólo las tareas abiertas del espacio, con su responsable, sin las terminadas;
      (4) elige una (por ejemplo la de integrar de Marcos) → la vista previa dice "espera a: …" con la tarea y
      la persona; (5) confirma → cargada; (6) carga otra sin espera → igual que antes. Después, el coordinador
      revisa en la base la espera (`dependency`) y la fila de auditoría con `espera_task_id`.
      Se repite con el usuario después de la J1-6. Sumar al guion: (7) tocar "> confirmar" con el criterio,
      la evidencia y "quién la decidió" vacíos → al lado del botón, "Falta completar: criterio de
      aceptación, evidencia, quién la decidió.", y el foco en el criterio; (8) tocar cada campo, el
      calendario y "Espera a" → la página no se agranda ni se corre de costado.
      **RDD:** `review-88f93736d2c3d327` (`cc9cc41d`), aprobada. Advertencia: reiniciar el formulario por un
      conflicto mientras se manda (`LoadForm.tsx:499-510`); sugerencia: el chequeo de "demasiado largo" de
      `checkDraft` sin prueba propia (`draft.ts:105-111`).
- [x] **J1-6 · Arreglos de la prueba del usuario** (2026-10-13; ruta delegada, un escritor, sólo `web/`).
      **Lo que vio:** (1) tocó confirmar con el criterio, la evidencia y "quién la decidió" vacíos; el
      servidor respondió bien (422 con los tres `errores`), pero nada lo decía cerca de donde miraba, y no
      supo por qué no se cargó; (2) el paso "> revisar" repetía la vista previa que ya estaba a la vista
      ("debería tener un título o algo que diga vista previa y abajo directamente los botones de
      confirmar"); (3) en el navegador de Telegram del iPhone la página se corría de costado: el selector
      de quién la hace, el calendario y "Espera a" pasaban el borde derecho.
      **Qué cambió** (`cc9cc41d`): una sola pantalla, con la vista previa en vivo titulada "Vista previa" y
      "> confirmar" justo debajo (en la computadora, fija al bajar; en el celular, debajo del formulario);
      sin "revisar" ni "volver"; mientras se manda, el formulario queda trabado (lo que se ve es lo que
      va); la clave de un solo uso, "no llegó la respuesta, probá de nuevo", el aviso de clave usada con
      otros datos y "cargar otra" siguen igual. Al lado de confirmar, un resumen (`role="alert"`): "Falta
      completar: …" y "Hay que corregir: …" con el nombre de cada campo, que lleva a él; el foco va al
      primero con problema, y cada campo conserva su mensaje (`aria-invalid`, `aria-describedby`). Lo que
      falta o se pasa del tope se ve antes de mandar (`draft.checkDraft`, con los textos de
      `TEXTOS_DE_LA_CARGA`); lo demás lo dice el servidor y va al mismo resumen. El ancho: cada campo y
      el calendario `w-full min-w-0 max-w-full`, y 16 px en pantallas táctiles (`pointer-coarse:`), porque
      el iPhone agranda la página al tocar un campo de menos de 16 px (los campos tenían 13); en la puerta
      del equipo, la línea del espacio del cabezal no podía achicarse (`truncate` sin `min-w-0`).
      **Evidencia:** `AdminApp.test.tsx` 15 en rojo y 10 en verde antes, 25 en verde después (5 pruebas
      nuevas: una sola pantalla, lo que falta con el foco, el formulario vacío, el 422 del servidor, los
      anchos); `App.test.tsx` 1 en rojo antes (el cabezal), 11 en verde después; `npm test` 65 passed;
      `npm run build` bien (la regla de 16 px está en el CSS compilado). Medido con Chrome sin ventana en
      marcos de 360 y 390 px (345 y 375 px de contenido), con textos largos: ningún elemento pasa el
      borde, ni antes ni después del arreglo; Chrome no reproduce lo del iPhone, así que la causa más
      probable es el agrandado al tocar un campo, y sólo la prueba en el celular lo confirma (J1-5).
- [x] **J1-7 · Segunda ronda de arreglos de la prueba** (2026-10-13; ruta delegada, un escritor, sólo
      `web/` y documentos). **Lo que vio** el usuario en el iPhone, después de `cc9cc41d`: (1) antes de
      tocar "> confirmar" la página entraba; al tocarlo con un campo vacío se podía correr de costado (el
      resumen y la vista previa pasaban el borde derecho); (2) los textos de lo que falta, blancos, no se
      distinguían; (3) lo que faltaba aparecía recién al confirmar, y había que bajar a buscarlo; (4)
      "confirmar" se veía igual aunque faltara algo. Y pidió (por el coordinador): con varios campos
      vacíos, cada toque lleva al próximo.
      **La causa del corrimiento:** en Chrome con emulación de celular (`mobile: true`, táctil, 360 y 390
      px, textos largos) ningún elemento pasa el borde, ni antes ni después de confirmar
      (`scrollWidth` = ancho), y los campos ya tienen 16 px; así que no es un desborde del diseño. Lo único
      que pasa al confirmar es que aparece el resumen y que el foco salta por programa a un campo lejano,
      dentro del mismo toque: el navegador hacía su propio desplazamiento para mostrarlo (y en el iPhone
      además abre el teclado), y ese desplazamiento nativo es lo que puede mover la vista de costado. Es
      la causa más probable, no comprobada: Chrome no reproduce lo del iPhone.
      **Qué cambió** (`b7fb4ea7`): (a) llevar a un campo es ahora un desplazamiento sólo vertical
      (`window.scrollTo({ top })`, suave salvo con movimiento reducido, con el bloque entero del campo y
      su mensaje en el medio) y después `focus({ preventScroll: true })`; (b) la red de seguridad:
      `overflow-x: clip` en `html`, `body` y `#root` (`clip` y no `hidden`, para que la vista previa fija
      siga funcionando), `overflow-x-clip` en la raíz de cada puerta y `max-w-full` en la grilla, el
      formulario y la vista previa; (c) los mensajes de cada campo, el resumen y el borde del campo (y
      del calendario) con un problema van en el color de atención que ya tenía la paleta (`vencida`,
      ámbar), con el "!"; (d) "! Falta completar: …" está siempre arriba de "confirmar" mientras falte
      algo, desde el principio y en vivo, y se va cuando está todo; los campos no se marcan antes de
      tocar confirmar; (e) "confirmar" se ve apagado mientras falta algo (`aria-disabled`, nunca
      `disabled`); tocarlo no manda, marca los campos y lleva al primero que falta; cada toque siguiente,
      al próximo en el orden del formulario, y del último vuelve al primero; los que se completan salen
      de la vuelta. El 422 del servidor sigue yendo a los mismos mensajes y lleva al primero.
      **Evidencia:** `AdminApp.test.tsx`, 4 en rojo y 24 en verde antes (la línea en vivo, la vuelta
      por los campos con `scrollTo` sin `left` y `focus` con `preventScroll`, la red de seguridad, el
      desplazamiento del 422), 28 en verde después; `npm test` 68 passed; `npm run build` bien (en el CSS
      compilado: `overflow-x:clip`, `#root`, `aria-disabled`, `border-vencida`). Chrome con emulación de
      celular a 360 y 390 px, antes y después del arreglo: `scrollWidth` igual al ancho antes y después
      de confirmar. **Sólo el celular confirma** que ya no se corre (J1-5). Sumar al guion: (9) con el
      formulario vacío, "! Falta completar: …" en ámbar arriba de "confirmar", que se ve apagado; (10)
      tocarlo tres veces con tres campos vacíos → lleva a cada uno, en orden, sin correrse de costado.

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

### J2 a J7

Se detallan al llegar a cada una, con su diseño corto, y cada una con la ayuda de la IA donde sirva.

      **RDD:** `review-71dd3cfc8a337a10` (`b7fb4ea7`), aprobada. Advertencias, de las pruebas: la del CSS depende
      de la carpeta desde donde se corre (`AdminApp.test.tsx:307`) y la de "los completados salen de la ronda"
      no lo prueba del todo (`:291-297`); sugerencia: restaurar los espías (`:258-259`). Las tres, arregladas
      en `ddb822e8` (J2-3). La revisión de estilo de los últimos detalles de la J1-5 (el color de lo que
      falta y el ícono), `review-62463f212ed0f53d`, aprobada con dos sugerencias: la marca del resumen
      ("Falta completar") y la de los avisos no tienen prueba propia. Sin arreglar todavía.
- [x] **J2 · La ayuda de la IA al cargar, para todos.** Se describe como se habla y Leda completa título,
      criterio, fecha y evidencia; la persona corrige y confirma (ADR 0023, punto 4). Para todos los que
      cargan: la puerta de administración primero, y después Dirección, referentes e integrantes en sus
      porciones. Se aprovecha lo que ya existe (usuario, 2026-10-13: "no hay que inventar nada"): el
      cliente de la IA del motor (`motor/ia_real.py`, `desde_base`), los chequeos de la entrega
      (`entrega.puntos_del_criterio`, `problema_del_ejemplo`: nada de números ni nombres que nadie dijo) y la
      propuesta de título y criterio del alta del flujo congelado (`alta_turno.py` en la etiqueta
      `respaldo-flujos-antes-de-d`: `CAMPOS_PROPONIBLES`, el criterio que dice cómo se comprueba), como
      referencia para adaptar, no para copiar el flujo.
      Ruta: delegada (un escritor; servidor, web, pruebas y la herramienta de medición).
  - [x] **J2-1 · Diseño corto** (abajo, "Diseño corto (J2-1)"); la entrada, cambiada por el usuario el
        2026-10-13: un solo recuadro libre. Sin migración (`leda_app` ya escribe `audit_log` e
        `incident` en un espacio).
  - [x] **J2-2 · Las garantías, primero en rojo**, con una IA de mentira (`IADeLaCarga`, en
        `tests/test_ayuda_al_cargar.py`; nunca la real). Servidor: 41 en rojo en
        `tests/test_ayuda_al_cargar.py` (sin el módulo) y 13 en `tests/garantias/test_ayuda_al_cargar.py`
        (sin la ruta), con el ejemplo del usuario en las dos; 54 en verde después. Web: 11 en rojo en
        `AdminApp.test.tsx` contra el formulario de antes (el recuadro, las marcas, nunca pisar lo
        escrito, lo que no pudo, elegir entre dos, la falla, el recuadro vacío, lo que no ofrecen las
        opciones, confirmar una vez, y el micrófono: sin reconocimiento, con él y sin permiso), en
        verde después.
  - [x] **J2-3 · El servidor y la web.** `65b2469f` (`ayuda_al_cargar.py`, la ruta
        `/ayuda` de `web_app.py`, la etapa `ayuda_al_cargar` de `incidentes.py` y sus pruebas) y
        `ddb822e8` (`HelpBox.tsx`, `speech.ts`, el formulario, y las tres advertencias de la J1-7:
        el CSS se lee desde la carpeta de la prueba, `import.meta.dirname`, y pasa también corriendo
        desde `web/src`; la vuelta prueba que un campo completado sale; los espías, restaurados en un
        `finally`). **Verificación** (2026-10-13): `pytest -q tests/garantias tests/test_ayuda_al_cargar.py`
        792 passed (13 min); `pytest -q tests/test_aviso_incidente_legible.py
        tests/motor/test_incidentes_del_motor.py` 18 passed; en `web/`, `npm test` 79 passed y
        `npm run build` bien.
  - [x] **J2-4 · La herramienta de medición** para una ronda real (no se corre sin permiso):
        `tools/medir_ayuda_al_cargar.py`, 11 pedidos escritos como en un chat (el ejemplo del
        usuario, los tornillos, un apodo, "mañana", un sábado, alguien de afuera, dos nombres, el
        número del día, una espera por su nombre, faltas de ortografía), con la misma función y los
        mismos controles. Con la IA real, desde la carpeta del Motor: `$env:PYTHONPATH = "src"` y
        `.venv\Scripts\python.exe tools\medir_ayuda_al_cargar.py --ia sol-suscripcion --veces 3
        --salida tests\conversaciones\resultados\ayuda-al-cargar.json` (11 llamadas por vuelta; sale
        con 4 si se acaba el cupo). En seco (`--ia guionada`, sin red) corrió: 0 de 11, como debe,
        porque la IA de mentira no propone nada (cambiado en la J2-7: ahora tiene guion).
        **RDD de la J2** (el coordinador): `review-6a44e26466b95395` (`65b2469f`), aprobada con
        advertencias: el chequeo de "la fecha está dicha" era flojo (`ayuda_al_cargar.py:299-304`: un
        número cualquiera, un día de la semana o una palabra relativa en cualquier lugar del texto) y
        la sugerencia del tope de salida (`:249`, el de elegir jugadas para una propuesta más larga);
        `review-03b5c3a74d3719b7` (`ddb822e8`), aprobada con advertencias: una respuesta vieja podía
        completar después de un cambio (`LoadForm.tsx:301-302`) y el 422 de `api.ts:210-213` sin
        prueba; `review-5457837d11cb0618` (`0669ab63`), aprobada con cinco hallazgos de la
        herramienta: sin cupo se perdía el informe, `--veces` menor que 1 corría, toda excepción se
        contaba como de la IA, los nombres se buscaban con una copia de la función del servidor y la
        corrida en seco no probaba nada. Todos, arreglados en la J2-7.
  - [x] **J2-5 · Prueba real en el celular** (con el usuario). **Lo que vio el usuario**
        (2026-10-13): la ayuda completó bien el título, la descripción, quién la hace (Marcos) y el
        objetivo ("me sorprendió, lo hizo perfecto"); el criterio que propuso sólo repetía el
        resultado, y una tarea cargada antes a mano tenía de criterio "No se" (las dos cosas, en la
        J2-9). El dictado por el teclado del celular se cortaba una y otra vez (probablemente por el
        bloqueo de la pantalla), así que lo escribió: insumo para la J2b, que la pantalla no se
        apague mientras graba (la Wake Lock API). Queda sin marcar hasta repetirla con la J2-9.
  - [x] **J2-6 · La ronda con la IA real** (la lanzó el coordinador, con permiso; 2026-10-13):
        `tools/medir_ayuda_al_cargar.py --ia sol-suscripcion --veces 3` (chatgpt/gpt-6-sol),
        **29 de 33 bien** (`tests/conversaciones/resultados/ayuda-al-cargar.json`). Fallas: 3 ×
        "antes del jueves" con la fecha vacía (el código leía "antes del jueves" como ningún día;
        lo decidió el usuario y se arregló en la J2-8) y 1 × el criterio sin proponer en "los
        tornillos, sin quién ni cuándo" (el dato quedó vacío, con su mensaje).
  - [x] **J2-7 · Arreglos de las revisiones** (2026-10-13; ruta delegada, un escritor: servidor, web,
        herramienta y pruebas).
        **La fecha** (`dd5bd617`): la IA devuelve, junto a la fecha, las palabras con que la persona la
        dijo (`como_dijo_la_fecha`). El código (`fecha_dicha`) comprueba que están tal cual en el texto
        (sin mayúsculas ni acentos) y calcula él mismo el día con hoy, con la frase entera del texto
        donde están (si la persona escribió "el viernes de la semana que viene" y la IA copió "el
        viernes", el día es el de la semana que viene). Entiende "hoy", "mañana" (no "por la mañana",
        "a la mañana" ni "esta mañana", que son una hora), "pasado mañana", el nombre de un día (el
        próximo, nunca hoy; "el viernes que viene" es el mismo; "de la semana que viene" o "de la
        próxima semana", el de la semana siguiente), "el 22", "del 22", "el día 22" (de este mes o, si
        ya pasó, del que viene), "22/10" o "22-10" (de este año o del que viene), "22/10/2026", "el 22
        de octubre" y "el viernes 23" (tiene que ser viernes). Un número suelto ("12 tornillos", "la
        máquina 3 10 tornillos") nunca es un día, y "la semana que viene" sola no dice cuál. Vale sólo
        si el día del código es el de la IA y es hábil; si no, queda vacío con el porqué: "No puse la
        fecha: dijiste "el sábado", pero el sábado 17 de octubre no es día hábil en este espacio…",
        "… está fuera del calendario…", "No puse la fecha: no entendí qué día es "12"…" (también
        cuando la IA calculó otro día) y "no encontré en lo que escribiste qué día es…" (sin las
        palabras o con unas que no están). El motor no tiene un lector de días en el código (la IA de
        las jugadas los saca de la lista `dias`, `instrucciones.py:89`), así que no había uno para
        reusar: se usan sus nombres (`calendario.DIAS`, `hechos.dia`). **El tope de salida:**
        3000, y nunca menos que `tope_jugadas` ni `tope_redaccion` del espacio (la propuesta lleva
        hasta 1500 caracteres de texto más el JSON, y un modelo que razona gasta parte antes).
        **La respuesta vieja** (`b8ebc49c`): si mientras Leda respondía la persona cambió el texto
        libre o un dato, la respuesta no completa nada y el recuadro dice "Cambiaste lo escrito
        mientras Leda completaba; tocá completar de nuevo."; un 422 sin sus motivos se lee como "Leda
        no pudo completar ahora…", nunca en silencio. **La herramienta** (`577d3dd0`): sin cupo
        escribe el informe hasta donde llegó (`cortada: sin_cupo`) y sale con 4; `--veces` menor que 1
        se rechaza; sólo una falla de la llamada a la IA cuenta como de la IA (`falla: ia`), y un error
        del programa corta en ese pedido (`falla: programa`), sale con 3 y no gasta más llamadas;
        quién la hace se busca con `fichas.integrantes_que_coinciden` del servidor sobre el equipo
        fijo (`EquipoFijo`, un cursor que contesta sus dos lecturas); en seco tiene un guion para el
        ejemplo del usuario y para el sábado: da 2 de 11 (el sábado, con la fecha descartada por no
        ser hábil).
        **Evidencia (2026-10-13):** `pytest -q tests/test_ayuda_al_cargar.py` con las pruebas nuevas
        de la fecha y del tope contra el código de antes: 47 en rojo y 30 en verde; después, 77 en
        verde. `tests/garantias/test_ayuda_al_cargar.py` con la nueva (la fecha que nadie dijo, por la
        puerta): 1 en rojo y 13 en verde con el código de antes; las dos juntas, 91 en verde. Las de la
        herramienta: 6 en rojo, después 83 en verde en `tests/test_ayuda_al_cargar.py`. En la web,
        `AdminApp.test.tsx` 3 en rojo y 40 en verde (la respuesta vieja por un dato y por el texto, el
        422 sin motivos), 43 en verde después; `npm test` 83 passed y `npm run build` bien. La
        herramienta en seco (`$env:PYTHONPATH="src"; .venv\Scripts\python.exe
        tools\medir_ayuda_al_cargar.py --ia guionada --veces 1`): 2 de 11, sale con 1.
        `pytest -q tests/garantias` completa: 752 passed (12 min 27 s).
        Quedan sin marcar la J2-5 (el celular) y la J2-6 (la ronda real, que ahora mide también si la
        IA copia bien las palabras de la fecha).
        **RDD de la J2-7** (el coordinador): `review-6eec478c3a4ddc11` (`dd5bd617`), con una
        advertencia: "22-10" con guion se leía como día y mes, así que un rango ("del 10-12", "10-12
        tornillos") daba una fecha (`ayuda_al_cargar.py:139-141`); y una sugerencia: "de mañana"
        (`:132-133`) se leía como mañana, y suele ser una hora del día. `review-22a7da5ecc0b44dc`
        (`b8ebc49c`), con dos sugerencias sobre las pruebas de la respuesta vieja.
        `review-f7886a8a6481af78` (`577d3dd0`), con una advertencia en la herramienta
        (`tools/medir_ayuda_al_cargar.py:259-260`: `LookupError` y `OSError` también atrapan un
        `KeyError`, un `IndexError` o un archivo que falta, que son errores del programa). Las dos
        advertencias y la sugerencia de "de mañana", arregladas en la J2-8; las dos sugerencias de
        las pruebas de la respuesta vieja quedan anotadas, sin tocar.
  - [x] **J2-8 · "Antes del" y los rangos** (2026-10-13; ruta inline del escritor delegado: un
        archivo de código, sus pruebas y la herramienta). La decisión del usuario, después de la
        ronda real: "si la persona dijo antes del jueves, leda deberia proponer el miercoles, porque
        la persona dijo 'antes del jueves' no 'el jueves'".
        **Qué cambió** (`f000059e`): `fecha_dicha` lee "antes de" uno de los días que ya entendía
        ("antes del jueves", "antes del 22", "antes del día 22", "antes del 22/10", "antes del 22 de
        octubre", "antes de mañana", "antes de pasado mañana", "antes del viernes de la semana que
        viene"), calcula ese día con las mismas reglas y propone el día hábil anterior del calendario
        del espacio (`dias_habiles` de las opciones de la carga, con sus feriados), desde hoy:
        "antes del jueves" un miércoles es hoy; "antes del lunes", el viernes; con el miércoles
        feriado, el martes. Si no hay un día hábil desde hoy ("antes de hoy", o "antes de mañana"
        pasada la hora de cierre) o el día anterior queda fuera del calendario, queda vacío: "No puse
        la fecha: dijiste "antes de hoy", pero no encontré el día hábil anterior en el calendario de
        este espacio; elegila en el calendario." (`sin_habil_antes`). Las palabras de la IA tienen
        que traer el "antes" ("jueves" solo, `no_entendida`) y su fecha tiene que ser la del código
        (la regla de la J2-7); con una cantidad delante ("dos días antes del jueves") no se entiende.
        La IA puede dar ese día: la lista de días que recibe marca ", no es día hábil" en los que no
        lo son, y la herramienta dice, sin frases de ejemplo, que si la persona dijo que tiene que
        estar antes de un día es el hábil anterior, y que las palabras van enteras, con las que dicen
        si es antes. **Los rangos:** un par con guion sin el año ("10-12", "22-10", "5-1") queda como
        una ficha que no es un día y cuyos números no se leen sueltos; con el año ("22-10-2026"), sí
        es un día. Dos días unidos ("del 10 al 12", "entre el 10 y el 12", "del 10 a 12", "el lunes o
        el martes") o uno con "entre" delante no son una fecha, tampoco copiando una sola parte.
        **"De mañana"** es una hora del día, como "por la mañana", salvo en "antes de mañana".
        **La herramienta:** "un apodo y un día de la semana" espera el miércoles 2026-10-14 (su hoy
        es el miércoles 14 y es hábil, así que el hábil anterior al jueves 15 es hoy) y tiene guion
        en seco; `KeyError`, `IndexError` y un `OSError` que no es de la red son errores del
        programa (sale con 3), y una IA sin configurar, sin red o sin plazo sigue siendo de la IA.
        **Evidencia (2026-10-13):** con el código de antes, `pytest -q tests/test_ayuda_al_cargar.py`
        84 en rojo y 46 en verde (la mayoría por la firma nueva de `fecha_dicha`, con el
        calendario); con la función de antes llamada a mano, los 11 casos nuevos ("antes del jueves",
        "antes del lunes", "antes del 22", "del 10-12", "10-12 tornillos", "el 12" de "entre el 10 y
        el 12", "del 10" de "del 10 al 12", "el martes" de "el lunes o el martes", "de mañana",
        "jueves" de "antes del jueves" y "dos días antes del jueves") daban un día: 11 de 11 en
        rojo. `tests/garantias/test_ayuda_al_cargar.py` contra el código de antes (`-o
        pythonpath=` con una copia de `src` de `6be0fcdf`, el mismo que `a9d99d0e`): las dos nuevas, por la puerta, en rojo
        (el rango y "antes del viernes de la semana que viene" con `es_dia_habil` de la base).
        Después: `.venv\Scripts\python.exe -m pytest -q tests/test_ayuda_al_cargar.py
        tests/garantias/test_ayuda_al_cargar.py`, 146 passed. La herramienta en seco
        (`$env:PYTHONPATH="src"; .venv\Scripts\python.exe tools\medir_ayuda_al_cargar.py --ia
        guionada --veces 1`): 3 de 11 bien (el ejemplo, el sábado y "antes del jueves"), sale con 1.
        Sin tocar la ruta: `tests/garantias` completa no se corrió.
  - [x] **J2-9 · Un criterio que diga cómo se comprueba** (2026-10-13; ruta delegada, un escritor:
        servidor, web, herramienta y pruebas).
        **Lo que encontró el usuario en el celular:** (1) con la ayuda, Leda propuso "El PLC de la
        comprimidora Fette 2000 y sus variables quedan listos para que Ariel la integre a la
        interfaz. Se comprueba revisando que el PLC y sus variables estén listos para esa
        integración.": circular, la parte de cómo se comprueba sólo repite el resultado; pasó
        porque el código sólo miraba que esa parte existiera y estuviera dentro del criterio. (2)
        Una tarea escrita a mano antes se cargó con el criterio "No se", y el formulario la aceptó.
        **Lo que decidió** (2026-10-13): si la persona no dijo cómo se comprueba, Leda propone una
        manera concreta (por ejemplo "las variables del PLC se leen bien desde la interfaz"),
        marcada para revisar; y el código rechaza un criterio que sólo repite el resultado o no dice
        nada comprobable: el campo, en el color de lo que falta, con "Contame cómo se sabe que está
        terminada."
        **Diseño corto.** Una regla general, la misma en los dos caminos, sin frases ni palabras de
        respuestas malas (`AGENTS.md`, "reglas generales, no parches"); mecánica §13: "¿el
        resultado esperado es concreto y verificable?".
        - **La regla de lo que agrega** (`lo_que_agrega`, en `ayuda_al_cargar.py`): la parte del
          criterio que dice cómo se comprueba tiene que traer al menos una palabra con contenido que
          no esté en el resto del criterio ni en el título. Se comparan sin mayúsculas ni acentos,
          sin las palabras de función del castellano (artículos, preposiciones, conjunciones,
          pronombres y las formas de los verbos que sólo unen, ser, estar, haber y quedar: una
          lista general y chica) y sin el
          vocabulario del acto mismo de comprobar o de estar terminada (comprobar, verificar,
          revisar, controlar, chequear, constatar, confirmar, probar, asegurar; listo, terminado,
          hecho, completo, finalizado, acabado): ese vocabulario es el marco de cualquier
          comprobación y nunca dice qué se mira, así que no cuenta como contenido. Dos palabras son
          la misma si, sin la s o la n final ni la vocal final, son iguales o empiezan con las
          mismas cinco letras ("integre" e "integración", "colgado" y "colgar", "listos" y
          "lista"). Con el ejemplo del usuario no queda nada
          ("revisando" y "listos" son del marco, "PLC", "variables" e "integración" ya están en el
          resultado, "estén" es de estar): no pasa. "Las variables del PLC se leen bien desde la
          interfaz" trae "leen" y "bien": pasa.
        - **Al proponer** (la ayuda): la IA devuelve, como hoy, el criterio y la parte que dice cómo
          se comprueba (`como_se_comprueba`, copiada tal cual); el código comprueba que está dentro
          del criterio y que agrega algo. Si no, el criterio no se propone y el campo pide "contame
          cómo se comprueba" (como hoy). Las instrucciones de la IA dicen, sin frases de ejemplo, que
          si la persona no dijo cómo se comprueba proponga una manera concreta (qué se mira, se prueba
          o se entrega) con lo que contó, la tarea, el objetivo o la evidencia del área, y que nunca
          repita el resultado con otras palabras; el control de números y nombres que nadie dijo
          (`problema_del_ejemplo`) sigue igual. La marca "propuesto por Leda" ya existe.
        - **Al cargar** (`POST …/tareas`, el servidor, con o sin la ayuda), antes de `cargar_tarea`:
          1. **Sin la IA:** si el criterio, sin las palabras de función ni el marco, no agrega nada
             al título, se rechaza ahí ("No se", "No sé", "listo"): no hace falta preguntarle a
             nadie, y vale también con la IA caída.
          2. **Con la IA del espacio**, el mismo juicio que la entrega del motor (la IA lee, el
             código decide): una sola llamada, fuera del candado de la web (como la ayuda), con el
             título, la descripción y el criterio; devuelve la parte del criterio que dice cómo se
             comprueba, copiada tal cual, o vacío si no lo dice o sólo repite el resultado. El código
             aplica la regla de lo que agrega. Vacío o sin nada nuevo: 422 `criterio` /
             `sin_comprobacion`, "Contame cómo se sabe que está terminada.", y no se carga nada (la
             base igual dice todo lo demás junto, sin la clave, como con un dato mal formado). La
             llamada sólo se hace con una sesión de administración vigente y un criterio que la
             base no va a rechazar por vacío o largo.
          3. **Si la IA no responde** (sin configurar, sin sesión, plazo, cupo, respuesta ilegible,
             o una parte que no está en el criterio): no se traba la carga ni se finge la revisión.
             Se carga con un aviso que no bloquea, "No pude revisar el criterio ahora: la tarea quedó
             cargada con el criterio como lo escribiste.", y un incidente (etapa
             `criterio_al_cargar`, sin el error). Una carga repetida (la misma clave) no suma ni el
             aviso ni el incidente: los tuvo la primera.
        - **El costo:** una llamada más por cada carga confirmada (las cargas son pocas, a mano; una
          ronda de conversaciones son 1.500 a 1.800), con una entrada chica (título, descripción y
          criterio, hasta unos 1.500 caracteres). La espera la ve quien confirma: lo que tarde la
          IA en contestar, que todavía no está medido; la herramienta ahora guarda los segundos de
          cada llamada para medirlo en la próxima ronda real. No hace falta una decisión del
          usuario: si la espera molesta en el celular, la alternativa es no volver a juzgar un
          criterio que Leda propuso y la persona no tocó (ya pasó la regla al proponerlo), con su
          huella en la auditoría de la ayuda.
        - **La web:** el 422 ya va al campo, en el color de lo que falta, y "confirmar" lleva a él;
          el aviso de la carga ya se muestra. Lo nuevo: un `sin_comprobacion` no miró la clave (como
          un dato mal formado), así que después de un envío sin respuesta la web conserva la clave al
          corregir, para que el servidor diga si aquella ya cargó la tarea.
        - `PENDIENTE` (advertencia, caso de borde): si la respuesta de una carga se perdió y al
          reintentarla la IA juzga distinto, la persona ve el rechazo aunque la tarea esté cargada;
          al corregir, la misma clave con otros datos lo dice ("Puede que ya se haya cargado").
        **Qué cambió:** `3d4ab5fa` (`ayuda_al_cargar.py`: `lo_que_agrega`, `juzgar_el_criterio`;
        `web_app.py`: el juicio antes de `cargar_tarea`; `incidentes.py`: la etapa
        `criterio_al_cargar`; la herramienta y las pruebas) y `c0a0b206` (la web conserva la clave
        después de un `sin_comprobacion`). La herramienta suma el pedido del PLC y cuatro criterios
        escritos (16 pedidos, 15 llamadas por vuelta), guarda los segundos de cada llamada y cuenta
        como de la IA un error de la red que no es `ConnectionError` ni `TimeoutError` (la
        advertencia de la J2-8, que era real: un `socket.gaierror` cortaba la medición como error
        del programa). Una IA que ni siquiera se puede preparar tampoco traba la carga.
        **Evidencia (2026-10-13):** contra el código de antes, `pytest -q
        tests/test_ayuda_al_cargar.py` 16 en rojo y 131 en verde (el criterio circular se proponía,
        sin `lo_que_agrega` ni `juzgar_el_criterio`); `tests/garantias/test_criterio_verificable.py`
        9 en rojo y 3 en verde (pasaban la carga concreta, sin sesión y el dato mal formado); las de
        la herramienta contra su versión anterior, 5 en rojo (la corrida en seco, el juicio y los
        tres errores de la red). En la web, `AdminApp.test.tsx`: 1 en rojo (la clave después de un
        envío sin respuesta) y 2 en verde ya antes (el mensaje en su campo, con el color de lo que
        falta y "confirmar" que lleva a él, y el aviso de la carga: la web ya lo hacía en general).
        Después: `pytest -q tests/test_ayuda_al_cargar.py` 151 passed; `pytest -q tests/garantias`
        completa, 766 passed (13 min 51 s; corrió antes de la última prueba, la de la IA que no se
        puede preparar); `pytest -q tests/garantias/test_criterio_verificable.py
        tests/garantias/test_carga_de_tareas.py tests/garantias/test_ayuda_al_cargar.py
        tests/test_ayuda_al_cargar.py tests/test_aviso_incidente_legible.py`, 228 passed, con ella;
        en `web/`, `npm test` 86 passed y `npm run build` bien; la herramienta en seco
        (`$env:PYTHONPATH="src"; .venv\Scripts\python.exe tools\medir_ayuda_al_cargar.py --ia
        guionada --veces 1`): 8 de 16 bien, sale con 1. **Falta:** la ronda con la IA real (con
        permiso) y repetir la J2-5 en el celular.
        **La revisión de la J2-8**, `review-ded34de579ff3bc5` (`f000059e`), aprobada: una
        advertencia, la herramienta acotó `OSError` a `ConnectionError` y `TimeoutError`
        (`medir_ayuda_al_cargar.py:271`), así que un error de red que no es de esas dos clases
        (`socket.gaierror` al no encontrar el servidor, `ssl.SSLError`, "red inalcanzable") se
        contaría como error del programa; y dos sugerencias: el año de dos cifras con guion
        (`ayuda_al_cargar.py:156`, "22-10-26" no se lee) y una prueba de garantía negativa floja.
  - [x] **J2-10 · La jerarquía visual del formulario** (2026-10-13; ruta delegada, un escritor, sólo
        `web/` y este documento).
        **Lo que vio el usuario en el iPhone:** (1) en la vista previa, los nombres de los datos
        (objetivo, fecha, criterio de aceptación, evidencia, la hace, la revisa…) iban en minúscula y
        más chicos que el valor, y se perdían; (2) en el formulario, el título del campo (ESPERA A,
        CRITERIO DE ACEPTACIÓN…) y su ayuda ("Si no puede empezar hasta que otra tarea esté
        terminada.") se veían casi iguales; (3) las listas para elegir (personas, "espera a",
        objetivo) se veían más grandes que los campos de texto.
        **Lo que decidió** (2026-10-13, "hay que probar"): los **títulos** de los campos y los
        nombres de la vista previa, en mayúsculas, con un poco de espacio entre letras, sin negrita,
        del mismo tamaño que los valores y en `ink` (#e6e6e3, el blanco roto); **lo que la persona
        escribe o elige** (el texto de los campos y los valores de la vista previa), en `ink-soft`
        (#b0b2b6, gris claro), en el tamaño principal; las **ayudas**, más chicas, en `ink-dim`
        (#6f7277). Los mensajes de lo que falta siguen en su ámbar. Para (3), no se achican las
        listas (los 16 px en pantallas táctiles evitan que el iPhone agrande la página, J1-6): todos
        los campos quedan iguales.
        **Qué cambió** (`ee1c0aff`): un solo lugar para los estilos, `web/src/admin/typography.ts`,
        que usan el formulario, la ayuda, el calendario y la vista previa: `FIELD_TITLE`,
        `FIELD_VALUE` y `FIELD_HINT` (el tamaño principal es 13 px, y 16 px en pantallas táctiles,
        el mismo para títulos y valores; la ayuda, 12 px y 13 px en el celular), y `CONTROL`, la caja
        de todos los campos (texto, área de texto, lista y la caja de la ayuda: el mismo marco,
        relleno, alto de renglón y texto). Las listas dejan el aspecto propio del teléfono
        (`appearance-none`), que las hacía más grandes, y llevan una flecha propia (`Select`, en
        `LoadForm.tsx`; el id, la etiqueta y el foco siguen en la lista). En el calendario, el mes y
        los días van en el tamaño principal y los días en `ink-soft`; las letras de la semana, como
        ayuda. Las notas dentro de un valor de la vista previa ("Es posterior a la del objetivo…",
        "[SIN CONECTAR]…") pasan a ser ayudas, para no confundirse con el valor. La tarjeta de la
        tarea de la puerta del equipo (`TaskCard.tsx`) no tiene pares de nombre y valor, así que las
        páginas del equipo no cambian.
        **Evidencia (2026-10-13):** dos pruebas nuevas en `AdminApp.test.tsx`, en rojo contra el
        código de antes (2 failed): todos los campos con la misma caja y las listas sin el aspecto
        del teléfono, y los tres estilos en un título, un valor y una ayuda del formulario y en un
        nombre y su valor de la vista previa. Después, en `web/`: `npm test` 88 passed; `npm run
        build` bien (en el CSS compilado están `appearance:none`, `pointer-coarse:text-[16px]` y
        `pointer-coarse:text-body`). Son pruebas de estructura: **cómo se ve sólo lo confirma la
        prueba en el celular** (si los títulos de 16 px en mayúsculas pesan demasiado, o la caja
        "Contame qué querés hacer y te ayudo", que ahora también va en mayúsculas como título).
- **Segunda ronda con la IA real** (2026-10-13, autorizada; sobre `ee1c0aff`): `tools/medir_ayuda_al_cargar.py --ia sol-suscripcion --veces 3`, 16 casos, **48 de 48 bien** (`ayuda-al-cargar-2.json`). La ayuda tarda una mediana de 6,3 s (máx. 15,8 s); la revisión del criterio al confirmar, 1,9 s (máx. 7,8 s). RDD de J2-9: `review-f4fa0b6aca5a841e` (`3d4ab5fa`, WARNING: la raíz común puede rechazar un criterio bien, `ayuda_al_cargar.py:789-810`; sugerencia: la carga espera a la IA) y `review-47eb28dd67f113be` (`c0a0b206`, sin observaciones); de J2-10: `review-298d3d9895306faf` (una sugerencia en las pruebas). Ajuste del usuario en el celular: títulos sin mayúsculas, del tamaño de las ayudas (`cc7f9893`).
- **Segundo ajuste del usuario en el iPhone** (2026-10-13, sobre `cc7f9893`): los títulos de los campos, los nombres de la vista previa y "Vista previa" empiezan con mayúscula y tienen el estilo de título (`FIELD_TITLE`); en el resumen "Falta completar: …" los nombres siguen en minúscula, en medio de la oración (`FIELD_NAME`). Los valores de la vista previa (y su "—") van como las ayudas (`PREVIEW_VALUE`). "Que no quede ningún tamaño de letra grande": todo el formulario (campos, listas, calendario, botones y la lista de espacios) va en el tamaño de los títulos (`TEXT_SIZE`); los 16 px de los campos se reemplazaron por una regla sólo para iOS (iPhone, iPad y el navegador de Telegram), que al arrancar agrega `maximum-scale=1` al viewport (`web/src/admin/viewport.ts`, desde `main.tsx`; en Android no se aplica, para no bloquear el zoom con los dedos). `080049cd`; `npm test`: 95 passed; `npm run build`: sin errores. **Falta la prueba en el celular:** confirmar que al tocar un campo la página no se agranda ni se corre de costado.
      **Pasada en el celular** (2026-10-13, usuario: la ayuda "me sorprendió, lo hizo perfecto"; lo visual, tras J2-10 y J2-11, "quedó perfecto la parte visual"). El rechazo del criterio circular y de "no se" lo probó la segunda ronda con la IA real (48 de 48), no el usuario en el celular. **Decisión del usuario (opción A):** la regla de `maximum-scale=1` sólo en iOS se queda aunque dentro de Telegram bloquee también el agrandado con dos dedos (comprobado por el usuario: "no, no pude"); queda el Zoom de accesibilidad del sistema, y se revisa con la Mini App (`docs/ROADMAP.md`).
- [ ] **J2-12 · Repetir la prueba en el celular después de J2-8 y J2-9** (el usuario lo pidió el 2026-10-13: el
      primer paso fue antes de esos arreglos): "antes del jueves" propone el miércoles; un criterio "No sé" escrito a
      mano no se carga y pide "Contame cómo se sabe que está terminada"; cuánto tarda la ayuda y si se nota que Leda
      está trabajando.
      **Hecha** (2026-10-13, 17:44-17:50, iPhone, túnel `observations-guide-tsunami-guitar`): la fecha (mié 21.10),
      Lucas, el aviso "No encontré a «el tano»" en su campo, la caja que nombra lo que no pudo completar y los puntos
      animados ("quedó muy bien"), bien. **Hallazgos del usuario:** (1) el criterio escrito a mano se rechaza sin
      decir qué falta ni proponer cómo arreglarlo ("El ups queda cambiado y funcionando", "Quedo ordenado y
      limpio": "no le veo nada de malo… quedé totalmente encerrado", varias veces), aunque la evidencia que pide el
      área, justo abajo, ya dice cómo se comprueba; (2) los puntos animados también en "cargando…" al confirmar;
      (3) las listas desplegables abren con la letra y el tamaño del sistema (el menú nativo de iOS), no los de la
      web; (4) no propuso objetivo para el UPS (la regla: "si se entiende de lo que contó").
      **Disparador** (`AGENTS.md`, punto 4): el criterio es la tercera vez (J2-9, J2-13 y ahora) y el usuario dice
      que se siente mal con las pruebas en verde: no se propone otro arreglo, se cuestiona el diseño con el
      usuario. Además contradice la constitución §8 (Leda propone lo que falta en lugar de sólo pedirlo; ningún
      mensaje deja a la persona sin un próximo paso).
      RDD de J2-11: `review-23dc736a9afe1fb0` (`080049cd`; WARNING: el agrandado con dos dedos en el navegador de las apps, confirmado; WARNING: una prueba de tamaños que no discrimina, `AdminApp.test.tsx:419-421`; sugerencia en `viewport.test.ts`).
- [x] **J2-13 · El criterio, desde la evidencia y juzgado por su sentido** (2026-10-13; ruta delegada, un
      escritor: servidor, herramienta, web y pruebas).
      **La prueba del usuario en el celular** (2026-10-13, después de J2-9 y J2-10), con "hay que cambiar el ups
      de la sala de servidores que lo vea el tano antes del jueves se corta todo": Leda propuso "El UPS de la
      sala de servidores está cambiado; se comprueba verificando en la sala de servidores que el UPS fue
      reemplazado.": circular otra vez, con sinónimos ("cambiado" y "reemplazado"), que la regla de palabras de la
      J2-9 (`lo_que_agrega`: una palabra nueva con contenido, sin una lista fija de palabras de comprobar y de
      estar terminada) no puede ver. Lo demás estuvo bien: la fecha 21.10 era la correcta, porque el reloj de
      prueba de Leda dice que hoy es el jueves 15; y "el tano" no es un apodo de Marcos en `leda_motor`, así que
      "responsable no encontrado" era correcto, pero **la pantalla no lo dijo** donde ella miraba.
      **Disparador** (`AGENTS.md`, punto 4): la misma clase de hallazgo después de un arreglo del mecanismo; no se
      propone otro arreglo de palabras, se cambia el diseño.
      **Lo que decidió el usuario** (2026-10-13, "si"):
      1. Si la persona no dijo cómo se comprueba, Leda arma la comprobación con la evidencia que pide el área, que
         es una manera concreta y real, no inventada.
      2. Si un criterio dice cómo se comprueba lo juzga la IA por su sentido, como la entrega del motor
         (`lo_descrito_cubre`); se quita la lista de palabras y la regla de lo que agrega.
      3. Las instrucciones de la IA describen su trabajo, sin frases de ejemplo ni casos.
      Y, de la misma prueba: que todo lo que la ayuda no pudo completar se vea en su campo, y que los tres puntos de
      "completando…" se animen, **siempre** (usuario: "quiero que se animen siempre").
      **Diseño.**
      - **Al proponer** (`ayuda_al_cargar.revisar`): la IA ya no devuelve el criterio entero sino el resultado
        (`resultado`) y, aparte, cómo se comprueba (`como_se_comprueba`): la manera que dijo la persona o, si
        recibió la evidencia del área de quien la hace (cuando ya está elegida), esa evidencia aplicada a lo que
        hay que hacer; si no, vacío. El código arma el criterio, en este orden: (1) el resultado con esa manera,
        sólo si el juicio por el sentido (`juzgar_la_propuesta`, el mismo `juzgar_el_criterio` de la carga, una
        llamada más y fuera del candado) dice que es concreta; (2) si no, el resultado con la evidencia que pide
        el área de quien la hace, en palabras de todos los días (la misma política que marca las casillas): "Se
        comprueba con lo que pide el área: una foto del trabajo terminado; cómo se probó y qué dio la prueba.";
        sin quién la hace, la del área del objetivo, si la tuviera (**hoy la base no les da un área a los
        objetivos**: `objective` no tiene `area_id` y `opciones_de_la_carga` no la manda, así que este paso queda
        listo para cuando la tengan; agregarla es una migración, fuera de esta tarea); (3) sin evidencia, el
        criterio no se propone y el campo dice "Contame cómo se sabe que está terminada.". El control de números
        y nombres que nadie dijo (`problema_del_ejemplo`) sigue igual, sobre el resultado y sobre cada criterio
        armado. Si el juicio no responde, esa manera no se propone (vale la evidencia) y queda un incidente
        `ayuda_al_cargar`; la auditoría guarda `juicio_del_criterio`.
      - **Al cargar** (`juzgar_el_criterio`): la IA dice si el criterio dice una manera concreta de comprobar el
        resultado, distinta del resultado mismo (`dice_como_se_comprueba`, sí o no), y copia la parte que lo dice;
        el código decide: sí, sólo si la IA dijo que sí y la parte está dentro del criterio; no, si dijo que no; y
        cualquier otra cosa (sin juicio, otra forma, una parte vacía o que no está) es `sin_revisar`, nunca un
        visto bueno. La única guarda sin la IA, que no es una lista de palabras: un criterio vacío o igual al
        título (`sin_nada_que_juzgar`). **Cambia una garantía de la J2-9:** "No se" ya no se rechaza sin la IA;
        lo rechaza el juicio, y con la IA caída se carga con el aviso "No pude revisar el criterio ahora…" y un
        incidente, como cualquier otro criterio (lo que se acordó: nunca fingir que se revisó).
      - **Quitado:** `lo_que_agrega`, `no_agrega_nada`, `_DE_FUNCION`, `_DEL_MARCO`, `_raiz`, `_misma` y la
        "raíz común" (la advertencia de `review-f4fa0b6aca5a841e` desaparece con ella).
      - **La web** (pedido del coordinador, de la misma prueba). **Por qué no se vio "No encontré a…":** el
        servidor sí lo mandaba (`avisos`, con `responsable` / `no_encontrado`), pero la web lo mostraba sólo como
        un renglón gris (`text-ink-soft`) dentro del recuadro de la ayuda, arriba, fuera de la vista en el
        celular, y nunca en el campo. Ahora cada dato que la ayuda no pudo completar dice su texto en su campo, en
        el color de lo que falta y con su marca (como los mensajes de la carga, y en el `aria-describedby` del
        campo), hasta que la persona lo completa o vuelve a pedir; junto al recuadro, "No pude completar: quién la
        hace, criterio de aceptación." en el mismo color. El texto del servidor: "No encontré a «el tano» en el
        equipo; elegí quién la hace.". **Los tres puntos** de "completando…" se encienden y se apagan uno después
        del otro (`--animate-puntos`, 1,2 s, con 0, 200 y 400 ms de diferencia), **siempre**, también con
        movimiento reducido: por eso sólo cambia la opacidad, sin moverse, agrandarse ni rebotar. El botón se
        sigue llamando "completando…" para un lector de pantalla.
      - **La marca "propuesto por Leda"** en un verde agua suave, pedido del usuario: `be4c2830`
        (`--color-propuesto: #8ccfc0`).
      **Evidencia (2026-10-13):** con las pruebas nuevas contra el código de antes, `pytest -q
      tests/test_ayuda_al_cargar.py` 56 en rojo y 109 en verde (el UPS circular, la comprobación desde la
      evidencia, sin quién ni área, la lista de palabras que ya no existe, el juicio por el sentido y la
      herramienta); `tests/garantias/test_ayuda_al_cargar.py` y `tests/garantias/test_criterio_verificable.py`,
      20 en rojo y 16 en verde. En la web, `AdminApp.test.tsx` 2 en rojo y 49 en verde (el mensaje en el campo del
      responsable descartado y los puntos). Después: `pytest -q tests/test_ayuda_al_cargar.py
      tests/garantias/test_ayuda_al_cargar.py tests/garantias/test_criterio_verificable.py
      tests/garantias/test_carga_de_tareas.py` 237 passed; `pytest -q tests/garantias` completa, 774 passed (13 min 36 s); en `web/`, `npm test` 97 passed y
      `npm run build` bien (en el CSS, `@keyframes puntos{0%,60%,to{opacity:.25}30%{opacity:1}}` y los tres
      `animation-delay`); la herramienta en seco (`$env:PYTHONPATH="src"; .venv\Scripts\python.exe
      tools\medir_ayuda_al_cargar.py --ia guionada --veces 1`): 12 de 20 bien, sale con 1. La herramienta suma el
      pedido del usuario tal cual ("el UPS de la prueba del usuario", con los apodos de `leda_motor`: "el tano" no
      es nadie), el UPS circular escrito, un criterio concreto con "revisa" y "quede", y uno igual al título (20
      pedidos; unas 20 llamadas por vuelta con la IA real). Commits: `a4428fd9` (servidor, herramienta, pruebas y `docs/capacidades.md`) y `73a32f9e` (la web).
      **Falta:** una ronda con la IA real (con permiso: mide si la IA deja vacía la manera cuando la persona no la
      dijo, y el juicio por el sentido) y la prueba del usuario en el celular (J2-12).
      **RDD de J2-13:** `review-bfa79042ca12447b` (`a4428fd9`, WARNING: la herramienta de medición descarta una falla del juicio, `tools/medir_ayuda_al_cargar.py:437-440`) y `review-97374544422a6d97` (`73a32f9e`, WARNING: el resumen de la caja puede no coincidir con los avisos de cada campo, `HelpBox.tsx:156-157`); las dos aprobadas, sus avisos para arreglar con el cierre de la J2.
      **Ronda con la IA real** (2026-10-13, autorizada; sobre `c258ee37`): `tools/medir_ayuda_al_cargar.py --ia sol-suscripcion --veces 3 --salida tests/conversaciones/resultados/ayuda-al-cargar-3.json`, 20 casos, **59 de 60 bien** (sale con 1). La falla, "sin apuro" (vuelta 1): la IA dejó el criterio vacío en vez de proponer uno que el juicio descartara; para la persona, lo mismo. La ayuda, mediana 3,5 s (máx. 7,2 s). Detalle en la bitácora de flujos.
      **Los dos avisos de RDD, arreglados** (2026-10-13; ruta delegada, un escritor: herramienta y web): un juicio que no respondió queda en el resultado (`falla_del_juicio`, `falla: ia`, el caso sale mal como en `medir_el_juicio`), `67ca78df`; el resumen de la caja sale de los mismos avisos vivos que cada campo, `bfa3943e`. RED observado en las dos pruebas nuevas. `npm test`: 98 passed; `npm run typecheck`: sin errores; `pytest -q tests/test_ayuda_al_cargar.py tests/garantias/test_ayuda_al_cargar.py`: 187 passed. RDD: `review-5f52a868a430fd86`, aprobada (una sugerencia, `tools/medir_ayuda_al_cargar.py:442`). **Falta sólo la J2-12** (la prueba del usuario en el celular).
- [x] **J2-14 · El criterio escrito a mano se toma como el que propone Leda, y un rechazo trae su propuesta**
      (decisión del usuario, 2026-10-13, "si", tras la J2-12). **Chequeo de rumbo:** es la tercera vez que se toca el
      criterio; la clase de problema no es de palabras sino de diseño: al proponer, el criterio es el resultado más
      la evidencia del área; al escribirlo a mano, se le exigía al texto solo decir cómo se comprueba, sin mirar la
      evidencia que el área ya pide, y el rechazo no proponía nada (constitución §8). Lo decidido:
      1. La persona escribe el resultado; cómo se comprueba sale de la evidencia que pide el área (la misma de la
         propuesta). Un criterio con un resultado se carga aunque no diga cómo se comprueba.
      2. Sólo se rechaza lo que no dice ningún resultado ("No sé", vacío o igual al título). Si el área no pide
         ninguna evidencia, el criterio sigue teniendo que decir cómo se comprueba.
      3. Todo rechazo trae al lado un criterio propuesto por Leda (resultado más la evidencia del área), que la
         persona usa con un toque o corrige; y el aviso dice en palabras simples qué falta.
      Lo que se acepta perder: un resultado general ("queda funcionando") pasa, sostenido por la evidencia.
      Ruta: delegada, un escritor (servidor, web, herramienta y pruebas). Después, una ronda con la IA real (con
      permiso) y la prueba en el celular.
      **Hecha** (escritor delegado): `01bd93bb`. El juicio con evidencia del área pregunta si el criterio dice un
      resultado (`sin_resultado`) y, en la misma llamada, escribe el resultado para la propuesta
      (`criterio_con_la_evidencia`, la misma de la ayuda); sin evidencia, el juicio de la J2-13 (`sin_comprobacion`)
      sin propuesta; se guarda el texto de la persona; el rechazo trae "Leda propone:" y "> usar este criterio";
      sin propuesta, un incidente (`propuesta_del_criterio`). RED observado (15 + 10 + 2 + 3 pruebas). `pytest` de
      las cuatro pruebas del criterio y la ayuda: 272 passed; `npm test`: 101 passed; typecheck y build bien; en
      seco 15 de 23. RDD `review-88b227055a98f635`, aprobada; WARNING para el cierre: si las opciones de la carga
      no se pueden leer, el criterio se juzga con la regla vieja sin dejar incidente (`web_app.py:974-985`).
      **Ronda con la IA real** (autorizada): 65 de 69, los criterios escritos todos bien (bitácora). Falta la prueba
      en el celular.
- [x] **J2-15 · Los puntos animados también en "cargando…"** al confirmar (usuario, J2-12). Ruta: delegada, con la J2-16.
      Hecha: `ec3a3f37` (`Completing.tsx`, compartido por "completando…" y "cargando…").
- [ ] **J2-16 · Las listas desplegables propias**, con la letra y el tamaño de la web, como el calendario: el
      menú nativo de iOS no se puede estilar (usuario, J2-12).
      Hecha (escritor delegado, junto con la J2-15 y el aviso de RDD de la J2-14): `Dropdown.tsx` (botón y lista,
      teclado, Escape, toque afuera), en las cuatro listas de la carga y en la de espacios, sin ningún `<select>`;
      `ec3a3f37`. El aviso de RDD de la J2-14: si las opciones de la carga no se leen, no se juzga con la regla vieja:
      se carga con el aviso de "no pude revisar" y un incidente (`evidencia_del_criterio`), `86c790d0`. RDD
      `review-9ed467d37d43f402`, aprobada; su WARNING (en el iPhone, un toque para cerrar la lista la volvía a
      abrir) arreglado en `309b6ac4` con su prueba (RED observado). `npm test`: 111 passed; typecheck y build bien;
      `pytest` del criterio y la ayuda: 240 passed. **Falta la prueba en el celular.**
- [ ] **J2-17 · El criterio en palabras de Leda, y lo que Leda escribe, bien escrito** (segunda prueba en el
      celular de la J2-12, 2026-10-13, 18:42). **Hallazgos del usuario:** (1) la propuesta del criterio "es muy
      rebuscada… parece sacada del código y no lo que dice la IA… es muy estructurada": es cierto, la arma una
      plantilla del código (`criterio_con_la_evidencia`: "<resultado> Se comprueba con lo que pide el área: <a>; <b>.");
      (2) Leda no corrige la ortografía: escribió "cirelabs" aunque eligió bien el objetivo ("…con CoreLabs").
      **Chequeo de rumbo:** cuarta vez sobre el criterio. La clase de problema: la cocina escribe el texto visible
      en lugar del mozo (regla del mozo: la cocina da el hecho, la IA lo dice con naturalidad). La evidencia ya se
      ve en su lista, justo debajo, y se guarda aparte: el criterio no necesita repetirla.
      **De qué se parte:** el flujo C (`feat/flujo-de-un-mensaje:src/leda/alta_turno.py:1047-1068`, `:1155-1157`,
      `:1644-1646`): la IA escribía el criterio entero con sus palabras, con la evidencia del área como dato, y "no
      sé" era un pedido de ayuda (pasó en real, C6, 2026-10-03); su hueco: la propuesta no se revisaba contra datos
      inventados. El F-B7 (`respaldo-flujos-antes-de-d:src/leda/llm.py:429-440`) proponía sólo con el título.
      **Lo que decidió el usuario** (2026-10-13, "si, vamos por ahí pero… para todos los otros campos también, así
      queda natural"; y sobre la ortografía: "no es cambiar el significado de mis palabras, es corregir la
      ortografía… me está ayudando"):
      1. La IA escribe con naturalidad todo lo que propone: título, descripción y criterio (el criterio entero, con
         la evidencia del área como dato para decir cómo se comprueba, no pegada como lista). Ninguna oración
         armada por el código; `criterio_con_la_evidencia` queda sólo de reserva si la IA no responde.
      2. Siguen los controles de la cocina sobre cada texto entero: nada inventado (`_problema_del_texto`) y, en el
         criterio, que diga un resultado (el juicio por su sentido).
      3. "No sé" es un pedido de ayuda: Leda propone siempre, también sin evidencia del área (con el título y la
         descripción).
      4. La ortografía, en todo: Leda corrige lo que propone y lo que la persona escribió a mano, y pone los nombres
         como están en los datos del equipo (personas, objetivos, tareas: "cirelabs" → "CoreLabs"); nunca cambia
         cómo está redactado. Las correcciones se ven en la vista previa antes de confirmar, marcadas; el código
         comprueba que sólo cambió la ortografía (palabra por palabra) o un nombre de los datos.
      Ruta: delegada, un escritor (servidor, web, herramienta y pruebas). Después, ronda con la IA real (autorizada
      por el usuario) y la prueba en el celular.
- [x] **J2-18 · Leda completa todo lo que puede** (decisión del usuario, 2026-10-13, "si"). La ronda de la J2-17
      (66 de 81, bitácora) mostró que, sin quién la hace, la IA inventaba una comprobación floja ("se comprueba al
      verlo"), la misma clase que el UPS de la J2-13. El usuario: "Leda debería en lo posible completar todos los
      campos; yo reviso y corrijo lo que quiera o lo dejo tal cual"; y la evidencia no es cerrada (el formulario
      ofrece los cinco tipos del pack; el área fija un mínimo, no un límite). **Chequeo de rumbo:** la causa no era
      la redacción sino que Leda proponía sin los datos de los que sale la comprobación; con la persona y la
      evidencia propuestas, el criterio dice cómo se comprueba con lo que se ve tildado. Lo decidido:
      1. Leda propone quién la hace según el trabajo y las áreas del equipo, aunque no se haya dicho (marcado como
         propuesto); si la persona nombró a alguien que no está en el equipo, se dice en su campo y no se reemplaza
         por otro.
      2. Leda propone la evidencia que corresponde a esta tarea, sumada al mínimo del área (que no se puede quitar).
      3. El criterio dice cómo se comprueba con esa evidencia, con naturalidad.
      4. El objetivo y la tarea que espera, cuando se entienda.
      5. La fecha, sólo si la persona la dijo (cualquier otra sería inventada).
      Con la misma unidad: la ortografía palabra por palabra (una palabra que no pasa el control queda como estaba,
      sin perder las demás: "q" no anula "batería"), los avisos de RDD de la J2-17 (`review-0f1f6e1e0eacf371`,
      `review-297cc946aa4740af`, `review-b5e1ca58c61b942f`; entre ellos: sin la IA, un criterio igual al título
      podía cargarse sin revisar) y el chequeo de naturalidad de la herramienta, que marcaba de más.
      **Hecha** (escritor delegado): `2a760fdc` (servidor), `2ec540e9` (pruebas y herramienta), `bba1efc6` (web);
      y, inline, el importador: cada área conoce los cinco tipos del pack y lo que pide es el mínimo (`c99791b7`,
      RED observado; `leda_motor` reimportada con respaldo `db/respaldos/leda_motor-antes-tipos-de-evidencia-20261013.dump`).
      `pytest` de la ayuda, el criterio y la ortografía: 362 passed; garantías y entrega (`LEDA_BASE_URL=` vacío):
      888 passed; `npm test`: 122 passed. RDD aprobadas: `review-baa23ace8bea44a1`, `review-fc656fe6eb091158`,
      `review-756b1bb3b4c0b845`, `review-5eca561410caecb7`; WARNINGs para una tanda: la evidencia escrita sin
      validar (`web_app.py:1280-1286`), `nombres_mal_escritos` amplio (`ayuda_al_cargar.py:836`), `LoadForm.tsx:403`
      y los tipos malformados del pack (`importador.py:552-553`). Ronda con la IA real: 76 de 81 (bitácora).
      **Falta la prueba en el celular.** Nota: `test_el_enganche_de_la_cocina_da_la_marca…` falla si `LEDA_BASE_URL`
      está en el `.env` (la prueba depende del entorno).
- [x] **J2-19 · En la evidencia, tildado sólo lo que propone Leda** (prueba en el celular de la J2-18,
      2026-10-13, 21:07). Hallazgos: (1) al elegir a Nahuel (OT) quedaron tildados los cuatro tipos que pide el
      área más la foto que propuso Leda, y "una foto o una captura" con "una foto del trabajo terminado" a la vez;
      el usuario: "debería quedar sólo tildado lo que Leda propone, no todos; si la persona lo quiere modificar, lo
      hace". (2) Sin quién la hace, la IA no propuso a nadie para "pintar el cartel" (ninguna área pinta) y por eso
      tampoco evidencia; con la persona elegida a mano y el criterio borrado, el segundo "completar" propuso la
      foto y un criterio natural con cómo se comprueba. **Lo decidido:** la lista de cada área del pack deja de ser
      un mínimo que se tilda solo: es un dato que Leda tiene en cuenta; Leda propone la evidencia que corresponde a
      la tarea (sin repetir tipos que dicen lo mismo) y sólo eso queda tildado; la persona agrega o saca (la base
      exige al menos una). "· la pide el área" sigue como información. Con la misma unidad, los WARNING de RDD de
      la J2-18 (ver arriba). Ruta: delegada, un escritor.
      **De la misma prueba en el celular** (2026-10-13, 21:15-21:30), sumado al escritor de la J2-19. El usuario: "estamos
      puliendo pero la ayuda que está dando Leda al completar los campos es muy buena". Pasaron: CoreLabs, Lucas, el
      viernes 16 y el objetivo propuestos solos; "arvol → árbol, bateria → batería" marcados; "No sé" con su propuesta.
      Hallazgos: el nombre de los datos en la ortografía salió al revés ("CoreLabs → cirelabs", sin aplicar).
- [x] **J2-20 · "> empezar de nuevo"**: limpiar el formulario entero, preguntando antes (usuario: "falta algo básico…
      no le queda otra alternativa que borrar campo por campo").
- [x] **J2-21 · El rechazo del criterio antes que la ortografía**: corregir "No se" → "No sé" y después rechazarlo
      obligaba a confirmar dos veces (lo detectó el agente; el usuario: "no lo dije a ver si lo notabas").
- [x] **J2-22 · El criterio, desde quien hace la tarea**: qué hace y qué entrega, nunca "quien revise puede ver…"
      (usuario: esa parte "está de más"); con sólo la evidencia que corresponde, sale corto.
      Y en la vista previa, lo que Leda corrigió resaltado con el verde agua de "propuesto por Leda".
      **J2-19 a J2-22 hechas** (escritor delegado; el título resaltado, inline): `9d8bbc6a` (servidor), `b3791619`
      (pruebas, herramienta y capacidades), `b7c98613` (web). RED observado salvo J2-21 (rojo apagando el arreglo) y
      la marca de J2-22 (escrita después). `pytest` de la ayuda, el criterio, la evidencia y la ortografía: 426
      passed; `npm test`: 138 passed; typecheck y build bien. RDD aprobadas con WARNINGs: `review-13a33db35d62cdde`,
      `review-799c8ba1b905e81a`, `review-4f7c39f0d5f744a7`.
- [x] **J2-23 · La ortografía, corregida directamente** (usuario, 2026-10-13: "que lo corrija directamente sin
      resaltarlo, ya dijimos que corrige palabras puntuales, no lo que dice la persona"): sin marca, sin resaltado y
      sin la vuelta de "revisalo y confirmá"; el control palabra por palabra y la auditoría siguen. Con la misma
      unidad, los WARNINGs de las tres revisiones de arriba.
      **Hecha** (escritor delegado): `7a5d6b60` (servidor), `06a8a7ed` (pruebas), `4b21a034` (web). Un toque en
      "> confirmar": primero `/tareas/revisar` (un rechazo frena y no se corrige ese campo), después `/ortografia`,
      después la carga con el texto corregido, sin marcas. `pytest`: 433 passed; `npm test`: 135 passed; typecheck y
      build bien. RDD aprobadas: `review-e7206d73feefec16`, `review-a2b0c18ddedf102d`, `review-d5dcc44710b44c3f`;
      **deuda** (no se siguen persiguiendo en esta unidad): la equivalencia de las dos búsquedas del integrante
      (`web_app.py:1432-1433`), pruebas del vencimiento y de otros datos del juicio guardado más aisladas
      (`test_criterio_verificable.py:563-598`), y un pedido directo a la API con evidencia sin quién la hace.
- [x] **J2-24 · La ortografía, corregida en la vista previa** (prueba en el celular, 2026-10-13: "la idea es que
      la corrija en la vista previa, sin tener que apretar confirmar; lo demás parece que quedó bien"): al salir de
      un campo de texto, Leda corrige su ortografía y el campo y la vista previa la muestran corregida, sin marcas.
- [x] **J2-25 · El criterio en tercera persona**: tras la J2-22 salió en primera persona ("Dejo pintado el cartel…
      y entrego una foto"; lo notó el agente en la captura); tiene que nombrar a quien la hace: qué hace y qué entrega.
      Las dos, con el escritor de la J2b (comparten archivos).
- [x] **J2b · El dictado, con Gemini en el servidor** (usuario, 2026-10-13: "directamente con Gemini tal cual la
      documentación"; la comparación con OpenAI, anotada en `docs/ROADMAP.md`). **Por qué:** el dictado del
      navegador (`web/src/admin/speech.ts`, reconocimiento del teclado) se cortaba en el iPhone con el bloqueo de la
      pantalla (J2-5). **De qué se parte:** `docs/research/gemini-voz-del-otro-proyecto.md`, sección 3 (modelo
      `gemini-3.8-flash`, audio en línea sin convertir, `thinking_budget=0`, `temperature=0`, límites de tamaño,
      tiempos y errores) y 6; `llm.GEMINI_BASE` y `httpx` (sin sumar dependencias); `LEDA_GEMINI_API_KEY` en el `.env`
      (la puso el usuario, comprobada sin leerla). **Diseño:**
      1. "> dictar" graba en el navegador (`MediaRecorder`, el formato que dé cada celular) y mantiene la pantalla
         encendida mientras graba (`navigator.wakeLock`); "> dejar de dictar" corta. Hasta 2 minutos.
      2. El audio va a un camino nuevo de la puerta de administración, con su sesión; el servidor lo manda a Gemini
         con los nombres del equipo, los objetivos y las áreas como palabras a favorecer, y devuelve el texto, que se
         suma a la caja "Contame qué querés hacer" para que la persona lo vea y lo corrija.
      3. El audio no se guarda; la auditoría registra el pedido sin el contenido. Toda falla deja un incidente y un
         aviso neutro (nunca en silencio); la clave nunca sale del servidor.
      Ruta: delegada, un escritor, después de la J2-23 (comparten la caja). Prueba: unos dictados del usuario en el
      celular.
      **Hecha, con la J2-24 y la J2-25** (escritor delegado): `81b9aa7e` (servidor: `dictado.py`, la ruta
      `POST /app/admin/api/espacios/{id}/dictado`, audio crudo con su tipo, hasta 10 MB, `gemini-3.8-flash` por REST con
      la clave en la cabecera, los nombres del espacio como palabras a favorecer, plazo de 30 s; el criterio en
      tercera persona), `3d72ba96` (pruebas y la marca `en_primera_persona` de la herramienta), `d200681b` (web:
      `dictation.ts`, pantalla encendida, "grabando · 0:12 de 2:00", "pasando a texto…"; la ortografía en la vista
      previa a la pausa de 1,5 s y en el campo al salir). `pytest` del dictado, la ayuda y la ortografía: 370 passed;
      `npm test`: 155 passed; typecheck y build bien. Sin llamar a Gemini de verdad. RDD aprobadas:
      `review-0f465303e17d9ce6`, `review-13901a14989af226`, `review-fe347cca3b99b434`; **deuda**: el plazo de Gemini
      no es total (`dictado.py:115-117`), una transcripción cortada por el tope no avisa (`dictado.py:160-170`),
      ramas de `api.ts:323-353` sin prueba, falsos positivos posibles de la marca de primera persona.
      **Falta la prueba en el celular:** si Gemini acepta `audio/webm` (Android) y `audio/mp4` (iPhone), si la
      pantalla sigue encendida los 2 minutos, y el tope de 1000 caracteres de la caja.
- [x] **J2-26 · El criterio sin nombres** (usuario, 2026-10-13, "confirmo ese cambio"): la ronda de la J2-25
      (76 de 81) mostró que nombrar a la persona ata el criterio al responsable (si cambia, o con un pase, queda
      mal), cuela nombres que no son del equipo ("pepe", "el tano") y una vez tomó por responsable a quien
      necesitaba la tarea. El criterio va en tercera persona y sin nombres: qué queda hecho y qué se entrega; el
      nombre está en "La hace". Con la misma unidad, la deuda del dictado: el plazo total de Gemini y avisar si la
      transcripción se cortó por el tope. Ruta: delegada, un escritor.
      **Prueba en el celular de la J2b, la J2-24 y la J2-25** (2026-10-13, de noche): pasó. Usuario: "salió
      perfecta, tanto la ortografía como el dictado; lo transcribe perfecto y muy rápido". Gemini aceptó el audio
      del iPhone.
- [x] **J2-27 · Un gráfico del audio mientras se dicta** (usuario: "que vayan apareciendo un gráfico de audio o
      algo más visual, además de la duración, como lo hacen las apps de mensajería"): barras que se mueven con la
      voz, al lado de "grabando · 0:12 de 2:00". Con el escritor de la J2-26.
- [x] **J2-28 · Tres detalles de la vista** (prueba en el celular, 22:58): las casillas de evidencia sin fondo, con
      una tilde clara; "dictar" como ícono de ancho fijo (`Mic` / `Square`); la ayuda de la caja, corta ("Escribilo
      o dictalo como lo dirías; Leda completa lo que falta.").
      **J2-26, J2-27 y J2-28 hechas** (escritor delegado): `362f03c6` (servidor: el criterio sin nombres y su red de
      la cocina `nombra_a_alguien`, el plazo total de 35 s del dictado y el aviso del dictado cortado), `377633fa`
      (pruebas y la marca `con_nombre`), `8db49ea7` (web: `AudioBars`, el botón del micrófono, las casillas).
      `pytest`: 437 + 103 passed; `npm test`: 178 passed; typecheck y build bien. RDD aprobadas:
      `review-1f9aa239975efa97`, `review-a910b5e6f99bca07`, `review-911e312bbe09f01d`; **deuda**: una palabra con
      mayúscula al empezar una oración que coincide con un nombre ("Marcos de la puerta…") puede descartar un buen
      criterio (`ayuda_al_cargar.py:864-867`), apodos sin distinguir mayúsculas (`:851-855`), el hilo del dictado que
      queda vivo tras el plazo (`dictado.py:156-161`), una prueba atada al reloj real (`test_dictado.py:307-314`).
      **Prueba en el celular de J2-26 a J2-28** (2026-10-13, de noche): "quedó perfecto todo". En la base, ningún
      incidente en las pruebas del día; la auditoría del dictado sin audio ni texto (el iPhone mandó `audio/webm`).
- [x] **J2-29 · Revisión independiente de toda la J2** (pedido del usuario, 2026-10-13: "revisá la tarea por tu
      cuenta"; después: "hagamos la revisión pero no ahora"): un revisor de sólo lectura sobre todo lo de la J2
      (desde `c258ee37`): garantías (aislamiento, sesión en cada ruta nueva, una sola vez, auditoría sin contenido,
      opacidad técnica, nunca en silencio), el flujo de confirmar de punta a punta (respuestas viejas, "empezar de
      nuevo" en el medio, doble envío), honestidad de lo propuesto, las reglas del criterio y su juicio guardado, el
      formulario y las pruebas que no prueban. Las deudas anotadas en J2-23, J2b y J2-28 son su punto de partida.
      Cuándo: el usuario lo pidió para la noche del 2026-10-13, mientras duerme.
      **Hecha** (revisor de sólo lectura, 2026-10-13, noche, sobre `c258ee37..eaf84ed4`): **ningún hallazgo
      CRITICAL ni HIGH.** Se sostienen la sesión antes y después de la IA en las cuatro rutas nuevas, el candado
      nunca esperando a la IA, la auditoría sólo con huellas, la carga con "no pude revisar" e incidente si la IA
      falta, la fecha calculada por el código, y la persona elegida por quien carga cuando hay más de una. La J2 no
      tocó `db/`. Hallazgos:
      - **MEDIUM:** una respuesta tardía de la ortografía durante "confirmar" borra la clave de un solo uso
        (`LoadForm.tsx:298-334`).
      - **MEDIUM:** el dictado lee hasta 10 MB antes de validar la sesión (`web_app.py:1861-1869`).
      - **LOW-MEDIUM:** el criterio se descarta cuando una palabra al principio de la oración o un apodo en
        minúscula parecen un nombre (`ayuda_al_cargar.py:852-868`, deuda de J2-28).
      - **LOW:** "sí, borrar" no corta el dictado.
      - **LOW:** evidencia marcada que queda oculta cuando Leda completa quién la hace.
      - **LOW:** un audio sin tipo falla sin dejar incidente.
      - **LOW:** el hilo de Gemini sobrevive al plazo total (deuda de J2-28).
      - **LOW:** un comentario y una documentación desactualizados.
      - **Pruebas que faltan:** las respuestas tardías después de "empezar de nuevo", y una prueba atada al reloj
        real (deuda de J2-28).
      Las deudas de J2-23 y casi todas las de J2b ya estaban resueltas. La de la herramienta de medición (falsos
      positivos de "primera persona") sigue abierta y no afecta al producto. Se arreglan en la J2-30.
- [x] **J2-30 · Los arreglos de la J2-29** (escritor delegado; hallazgos 1 a 10, cada uno con su prueba).
      Ruta: delegada. Fuera de alcance: la regla de `maximum-scale=1` en iOS (decisión del usuario, opción A).
      **Hecha** en los commits `8a0b6b56`, `94887d44`, `25b215dd`, `f70f77d5`, `b67f81eb` y `269ba8bd`:
      - **La carga:** mientras se confirma, se ignoran las respuestas tardías y la clave de un solo uso no se borra.
      - **El dictado:** valida la sesión antes de leer el audio, admite hasta 4 a la vez, el plazo total es real y
        un audio sin tipo deja un incidente.
      - **"Sí, borrar":** corta el dictado.
      - **La evidencia** que el área nueva no conoce se quita.
      - **Comentarios** actualizados, y la prueba que dependía del reloj real ahora usa uno simulado.
      **Hallazgo 3, los nombres en el criterio:** el primer arreglo dejaba de contar cualquier mayúscula al empezar
      una oración, y así pasaba "Luz cambia la lámpara…", que nombra a una persona. El coordinador lo cambió por
      una regla general. Al empezar una oración, la palabra cuenta como nombre salvo que la persona la haya usado
      en minúscula en lo que escribió (el recuadro y los campos). Ejemplo: con "pintar los marcos de la puerta",
      "Marcos de la puerta…" no es Marcos. Ante la duda, Leda propone menos y lo dice.
      Queda abierto: si la persona escribe en minúscula el nombre de un compañero ("que lo haga lucas"), al cargar
      también exime a "Lucas cambia…".
      Pruebas: `npm test` 185 passed y `npm run build` sin errores. `pytest` de la ayuda, el dictado, la
      ortografía, el criterio y la carga: 484 passed. Control del coordinador: `tests/test_ayuda_al_cargar.py`,
      316 passed. **RDD** del tramo `eaf84ed4..269ba8bd`: `review-0ea10b790daf0d56`, aprobada. Sus advertencias
      quedan como deuda menor:
      - el filtro de evidencia de `apply` no tiene prueba (no se llega desde la pantalla);
      - el lugar del dictado queda tomado mientras sube el audio (`web_app.py:1908`);
      - con `audio/mp4` como último recurso, se pierde el tipo real (`api.ts:333`);
      - el transporte con plazo ignora un proxy del entorno (`dictado.py:216`).
      Las dos sugerencias: el hilo abandonado sin prueba y la excepción al empezar una oración.
- [x] **J3 · Los objetivos desde la web** (ADR 0023, decisión 1, decisión 5 y punto 11). Dirección crea los
      objetivos de su equipo desde su web; el administrador, desde la suya, en cualquier espacio. Con la ayuda
      de la IA desde el primer día, **reutilizando la J2** (usuario, 2026-10-13: "la j2 tiene muy buena base y
      podés reutilizar muchas cosas"): se generaliza lo que ya probó el usuario en el celular, no se escribe un
      formulario nuevo al lado.

      **Diseño corto (J3-1, 2026-10-13, noche; mapa del explorador de sólo lectura).**
      - **Qué se carga:** el nombre (hasta 200), de qué objetivo cuelga (o de ninguno), el tipo y el referente
        (cualquier integrante activo del espacio); la descripción, opcional (hasta 800). Sin fecha en esta
        porción (ver "Para decidir al despertar"). Nace `activo`, con su evento de estado: lo crea quien decide
        (Dirección o el administrador); `propuesto` queda para lo que proponga un integrante (J6).
      - **El tipo, según dónde cuelga** (punto 11): sin padre, estratégico, sin preguntar; colgado de un
        estratégico, hito u operativo, con operativo marcado; colgado de un hito, operativo, sin preguntar.
        Con los nombres de los niveles del pack: hoy el importador no los guarda (`motor/enlace.py:59-61`); se
        guardan en `workspace_setting` al importar y la web los lee con las opciones.
      - **De qué puede colgar:** sólo un objetivo abierto del mismo espacio (los mismos que ofrece
        `opciones_de_la_carga`); nunca de otro espacio, nunca de un operativo (debajo de un operativo van
        tareas, mecánica §1).
      - **La base** (migración `0068`, con su rollback y su paridad): `objective` se cierra como `task`. Se
        agregan `unique (workspace_id, id)` y claves compuestas para el padre y el referente, y se revocan las
        escrituras directas de `leda_app` si nada vivo las usa. La herramienta de chat `crear_objetivo`
        (`herramientas._crear_objetivo`, abierta a cualquier integrante en `autoridad.py:190`) se retira si
        ninguna jugada del motor la usa, porque por chat no se crean objetivos (ADR 0017, decisión 1; ADR 0023,
        decisión 6). Si alguna la usa, se para y se anota. Una función `crear_objetivo_web`, `security
        definer` de `leda_owner` y sólo ejecutable por `leda_app`, con el patrón de `cargar_tarea`: acepta la
        sesión de administración o la de un integrante con `autoridad_final`, fija el espacio, usa una clave
        de un solo uso (tabla `creacion_de_objetivo`, como `carga_de_tarea`) y junta los errores en una sola
        respuesta. Escribe la fila, el evento y la auditoría (`crear_objetivo`, con quién y por qué puerta).
      - **El servidor:**
        - La puerta de administración: `GET/POST /app/admin/api/espacios/{id}/objetivos`, con los controles de
          la carga (otro sitio, JSON, tamaño, la cookie).
        - La puerta del equipo, sólo para Dirección: `GET/POST /app/api/objetivos`. Es la primera ruta del
          equipo que escribe; deja armados los controles que reusa la J4.
      - **La ayuda de la IA:** el recuadro "Contame qué querés hacer y te ayudo", el dictado, "> completar con
        Leda", "completando…" y la ortografía, reutilizados. La ayuda propone el nombre, de qué cuelga, el tipo
        y las palabras con que se nombró al referente (el código lo busca con `integrantes_que_coinciden`; si
        hay más de uno, elige la persona). Se generaliza el recorrido en tres pasos de `ayudar_a_cargar`: con el
        candado, sin el candado mientras responde la IA, y otra vez con el candado, con la sesión revalidada.
        Lo propio de la tarea (el juicio del criterio, la fecha y la evidencia) no entra. La ayuda y la
        ortografía se abren también a Dirección por la puerta del equipo: la ayuda es para todos los que
        cargan (ADR 0023, punto 4).
      - **La web:** `FieldBlock` y `Counter` salen de `LoadForm.tsx` a sus archivos; `HelpBox`, `Dropdown`,
        `Completing`, la vista previa, "confirmar" y "> empezar de nuevo" se comparten. Las funciones de la API
        se inyectan para que sirvan a las dos puertas. Arriba del formulario se elige "tarea" u "objetivo". En
        la web del equipo, Dirección ve "Nuevo objetivo"; los demás no lo ven, y el servidor igual lo rechaza.
      - **Garantías** (ADR 0023, porción 1):
        - un integrante o un referente no crea objetivos;
        - un objetivo no cuelga de otro espacio ni de dos padres;
        - la auditoría guarda quién lo creó y por qué puerta;
        - una sesión de un espacio no crea en otro;
        - la clave de un solo uso no repite;
        - la IA nunca elige a una persona que no se nombró.
      Ruta: delegada. Un escritor por tramo (base y servidor; web; ayuda), con RDD por tramo.
  - [x] J3-2 · La base y el servidor sin la IA (`0068`, `crear_objetivo_web`, las dos puertas, garantías).
        Construida (escritor delegado) en los commits `81a52ee6`, `fbf70369`, `c281e6c6`, `83c51b5e`, `15e69bfa` y
        `f6482d32`:
        - la herramienta de chat `crear_objetivo` retirada, porque ninguna jugada la usaba;
        - `objective` con claves compuestas y cerrado a escrituras directas de `leda_app`;
        - `aplicar_evento_objetivo`, ahora `security definer`;
        - `crear_objetivo_web` y `opciones_del_objetivo`, con los nombres de los niveles en `niveles`;
        - las rutas de las dos puertas, con un ayudante de controles para la puerta del equipo.
        Las pruebas nuevas fallaron 40 de 40 antes de escribir el código y después pasaron 40 de 40.
        RDD `review-bef6a4c90272c9c7`, aprobada. Su WARNING (el evento de estado después de quitar el permiso de
        escritura) se arregló en `f6482d32`, con su prueba.
        `leda_motor`: respaldo `db/respaldos/leda_motor-antes-0068-20261014.dump` (`pg_restore --list` sin error).
        Ensayo en una copia descartable, sin error y borrada después. La `0068` se aplicó con `psql -v
        ON_ERROR_STOP=1` como `postgres`, sin error. Los nombres de los niveles se llenan al reimportar el pack;
        hasta entonces la web muestra los de siempre, que son los de CoreWork.
        Windows se reinició solo a la noche y cortó la sesión; la suite completa se está corriendo de nuevo.
  - [x] J3-2b · Las decisiones del usuario del 2026-10-14: la fecha obligatoria, en día hábil, y el
        referente, que tiene que ser un referente activo de un área (`0069`).
  - [x] J3-3 · La web: el formulario de objetivos en las dos puertas, compartiendo las piezas de la J2.
  - [x] J3-3b · La decisión 5 (un hijo no vence después que su padre, con "> cargarlo aparte") y las
        advertencias de la RDD `review-12308947b06404e4`, aprobada sobre `15e69bfa..953c2fab`. Son tres:
        - el reloj del espacio se lee antes de validar la sesión de administración (`web_app.py:1471`);
        - cambiar entre tarea y objetivo pierde lo escrito (`AdminApp.tsx:181`);
        - la `0068` editada después de escrita: falsa alarma, porque se editó antes de aplicarla en
          cualquier base, y `leda_motor` tiene la versión final.
        `leda_motor`: la `0069` se aplicó con respaldo (`leda_motor-antes-0069-20261014.dump`) y ensayo previo.
        **Hecha** en los commits `d03e27b0`, `482e3172`, `584fafa2` y `4e56c086`, con la migración
        `0070_nada_vence_despues_de_su_objetivo`:
        - **Las tareas:** una tarea no vence después que su objetivo. El formulario frena antes de confirmar y
          la base la rechaza.
        - **Los objetivos:** un objetivo no vence después que su padre. La vista previa ofrece "cambiar la
          fecha" y "> cargarlo aparte", y deja el lugar para "aceptar la demora" de la J5.
        - **Los arreglos de RDD:** el reloj se lee después de validar la sesión, y cambiar entre tarea y
          objetivo ya no pierde lo escrito.
        Cada caso con su prueba, que falló antes del arreglo y pasó después. `pytest tests/garantias`: 938
        passed. `npm test`: 213 passed. Build sin errores.
        RDD `review-e9df8c837fa7a6ea`, aprobada, con dos sugerencias menores: una prueba de la web no mira el
        día tope y la `0070` no comprueba de antemano la `0069`.
        `leda_motor`: la `0070` se aplicó con respaldo (`leda_motor-antes-0070-20261014.dump`) y ensayo previo.
  - [ ] J3-4 · La ayuda de la IA para objetivos (y la ortografía y el dictado en la puerta del equipo), con su
        herramienta de medición; una ronda con la IA real.
        **Construida** (escritor delegado) en los commits `21ccaca3`, `2a7c7752`, `41976b3a`, `2910ef93` y
        `f8d257f1`:
        - **Un solo recorrido de tres pasos** para la ayuda de tareas, la de objetivos y la ortografía.
        - **`ayuda_al_crear_objetivo.py`,** con la herramienta `proponer_el_objetivo`. La IA propone y el código
          decide qué vale:
          - el padre, de la lista;
          - el tipo, según el padre;
          - el referente, sólo un referente de área nombrado en el texto;
          - la fecha, sólo si se dijo y en día hábil;
          - el nombre y la descripción, con las comprobaciones de honestidad de la J2.
        - **La auditoría** `proponer_al_crear_objetivo` guarda huellas, no el texto. Si la IA falla, deja un
          incidente y la persona ve un 503 neutro.
        - **La puerta del equipo:** la ortografía y el dictado, sólo para Dirección.
        - **La web:** el recuadro de ayuda en el formulario de objetivos de las dos puertas.
        - **La herramienta** `tools/medir_ayuda_al_crear_objetivo.py`, con 15 casos escritos como en el chat.
        Pruebas: las nuevas fallaron antes del código y pasan después (salvo dos de la web, escritas después).
        `pytest tests/garantias`: 964 passed. `npm test`: 223 passed. Build sin errores.
        Quedan para la J3-4b, porque las piden las reglas ya acordadas ("Leda completa todo lo que puede" y la
        ortografía de la J2-24):
        - proponer el referente por el área de lo que se describe, aunque nadie lo nombre, como en la J2-18;
        - corregir la ortografía de la vista previa en la pausa;
        - que las instrucciones del dictado no digan sólo "una tarea".
        **RDD:** el tramo entero no entraba en el presupuesto del revisor, así que se revisó commit por commit.
        Cinco revisiones, todas aprobadas: `review-fb930886587de8eb`, `review-d7b10e1a0bbd8f09`,
        `review-2c829c10d1ff7207`, `review-a2d2a9636529b999` y `review-b2a852e448439273`. Sus cinco WARNING pasan a
        la J3-4b:
        - la equivalencia del ayudante de pedidos;
        - el tipo corregido sin prueba;
        - una clave de auditoría renombrada;
        - la ortografía que puede tocar la clave al reintentar;
        - un chequeo de la herramienta de medición.
        **IA real**, primera ronda: 45 de 45 (bitácora, `ayuda-al-crear-objetivo-1.json`).
  - [x] J3-4b · Los tres ajustes de la J3-4 (referente por el área, ortografía en la pausa, dictado general) y
        los cinco WARNING de su RDD.
  - [x] J3-5 · La prueba en el celular (usuario), con su guion.
        **Pasada** (2026-10-14, guion `docs/product/guion-celular-j3.md`, túnel
        `pharmaceutical-configuring-unix-while`):
        - **Web de administración:** "salió perfecto", con unas cosas menores que el usuario va a contar.
        - **Web de Dirección:** primero Leda no contestaba, porque el reinicio de Windows había cortado el
          escuchador. Al levantarlo: "Muy bueno! está quedando todo muy bien".
        IA real: 45 de 45 y 57 de 57. RDD aprobada en todos los tramos.
  - [x] J3-6 · Las cosas menores de la prueba (usuario, 2026-10-14, con capturas). Van con el escritor de la
        J4a, que toca los mismos componentes:
        1. un botón con ícono al lado del micrófono para borrar el recuadro;
        2. "confirmar" apagado no parecía apagado, y "cargarlo aparte" y "empezar de nuevo", activos, parecían
           apagados;
        3. las pestañas "tarea" y "objetivo" con la letra del encabezado ("LEDA · ADMINISTRACIÓN ·
           COREWORK"); si no convence, "Tarea" y "Objetivo". Cambiado por el usuario: como las pestañas "Tus
        tareas / Tu sector" de la web del equipo, con mayúscula ("Tarea", "Objetivo").
  - [x] J3-7 · Las palabras del formulario de objetivos (usuario, 2026-10-14: "no me gustaron y no me quedó
        claro"). Los niveles de CoreWork pasan a **objetivo general, etapa, objetivo de área**, tarea y subtarea,
        en el pack (mecánica §1). En el formulario:
        - "De qué cuelga" pasa a "Es parte de", y la opción vacía a "de ninguno (es un objetivo general)";
        - debajo del tipo, una línea corta que lo explica;
        - los avisos dicen "es parte de".
        Va con el escritor de la J4a. Después hay que reimportar el pack en `leda_motor`.
      **J3 cerrada (2026-10-14, noche).** El usuario revisó la J3-6 y la J3-7 en la compu: las pestañas "Tarea" y
      "Objetivo", "Es parte de", el botón de borrar, "confirmar" apagado frente a "cargarlo aparte" y "empezar de
      nuevo" activos, y los tipos con su explicación. Pidió un nombre más claro para el tercer nivel: pasó a
      "objetivo de un área" ("lo que le toca lograr a un área del equipo para que se cumpla lo de arriba"), en
      `3ab0f9e1`, con el pack reimportado.
- [x] **J4 · La carga por la web del equipo (Dirección y referentes), con el préstamo.** Cerrada el 2026-10-15,
      madrugada, con la prueba de cierre de la MA (ver allí).
      **Decisiones del usuario (2026-10-14, antes de escribir código):**
      - **D1. A quién le carga un referente:** a su área, a sí mismo y, como préstamo, a cualquiera de otra área,
        también a otro referente. Cómo funciona el préstamo quedó revisado más abajo ("D1, revisada": lo aprueba
        el referente de esa persona).
      - **D1b. El pedido a Dirección:** una tarea puede frenarse porque depende de una decisión o una ejecución de
        Dirección. Ejemplo: Lucas no puede instalar el servidor nuevo hasta que Dirección apruebe la compra.
        - Un referente puede cargarle a Dirección un **pedido** ("Aprobar la compra del servidor", para Ismael), y
          su tarea **espera** ese pedido, con la espera de la J1.
        - Se ve en la web y a Dirección le llega un aviso por chat.
        - Leda le hace el seguimiento como a cualquiera, sin escalar.
        - Lo da por cumplido el referente que lo pidió.
        - Cuando se cumple, quien espera se entera de que puede seguir.
      - **Revisadas una por una con el usuario (2026-10-14):**
        - **D1, revisada (reemplazada por D14 más abajo: sólo se pide al referente).** Ejemplo: Martín (IT) necesita
          que alguien de OT cuelgue el módem para poder configurarlo.
          - **Pedir prestado** (Martín elige a la persona): carga la tarea para Nahuel. La tarea no arranca hasta
            que **Marcos, el referente de Nahuel, la aprueba**. Si aprueba, le llega a Nahuel; si rechaza, Martín se
            entera del motivo. La revisa Martín.
          - **Delegar en el referente** (Marcos elige a la persona): Martín carga la tarea para Marcos, y Marcos la
            hace o se la pasa a Nahuel (el pase, también desde la web). La revisa Martín.
          - En los dos casos, la tarea de Martín puede esperar a la otra. Esta aprobación es el **primer circuito de
            aprobación**: se construye en la J4 y la J6 lo reutiliza para las propuestas.
        - **D2. El área de una tarea prestada:** la del referente que la pidió. "Medir el rack" para Nahuel, pedida
          por Martín, es de IT y pide la evidencia de IT. Nahuel sigue en OT. Marcos la ve como "Nahuel, prestado
          a IT".
        - **D3. Cuando carga Dirección:** Ismael elige quién revisa, con el referente de esa persona preseleccionado;
          puede poner a sí mismo o a otro referente. Nunca el responsable.
        - **D4, revisada. Dirección no revisa las tareas de los referentes:** le importa el objetivo, no cada tarea
          (mecánica §7: Leda no convierte a Dirección en aprobadora de tareas menores). La tarea propia de un
          referente la revisa él mismo, y la de su gente también. Ismael sólo revisa lo que él carga y elige
          revisar, y aprueba el objetivo al cerrarse. Por la tarea propia de un referente, a Ismael no le llega
          nada.
        - **D5. Bajo qué objetivo:** cualquier objetivo abierto.
        - **D6. El aviso al responsable:** un solo mensaje con todas las tareas cargadas seguidas, unos 10
          minutos después de la última, dentro del horario. Fuera de horario sale al empezar el siguiente. Es de
          coordinación: no cuenta para el tope diario.
        - **D7. El aviso a quien revisa:** sólo cuando carga uno y revisa otro. Ejemplo: Ismael le carga a Nahuel
          y deja a Marcos de revisor. Mismo margen, en horario.
        - **D9. Responsable sin Leda conectada:**
          1. la vista previa lo avisa antes de confirmar;
          2. a administración le llega un aviso para conectarlo;
          3. al conectarse, Leda le manda sus tareas juntas como bienvenida.
        - **D10. "Quién la decidió"** (web de administración): sólo Dirección o el referente del área de la tarea.
          El usuario ya lo había visto y se le había pasado mencionarlo.
        - **D11. La ayuda de la IA en la web del equipo:** propone sólo a quienes puede cargarles quien carga.
          Nombrar a alguien de otra área lo propone como préstamo y avisa que su referente tiene que aprobarlo. Sin
          nadie nombrado, "quién la hace" queda vacío. Lo demás, igual que la J2.
        - **D12. "Quiero crear una tarea" (u objetivo) por Telegram:** Leda lo dice con sus palabras, desde los
          datos de quién es y qué puede cargar.
          - **Tarea:** a Dirección y a los referentes, el enlace a su web. A un integrante, sin enlace: que las
            cargan su referente o Dirección, y que pronto podrá proponerlas.
          - **Objetivo:** a Dirección, el enlace. A un referente, que los crea Dirección; desde la J6, que puede
            proponerle uno desde su web. A un integrante, lo mismo que con una tarea.
          - Lleva su conversación de prueba contra la IA real.
        - **D13. Las tareas propias de Dirección:** Ismael puede cargarse tareas y las revisa él, con el
          seguimiento de cualquier tarea. Es distinto de la secretaria del ROADMAP: un recordatorio no es una
          tarea; aquélla es personal, por chat, a una hora, privada, y lleva su ADR.
        - **D14 y la revisión final de D1 y D2. Lo de otra área se le pide a su referente** (usuario: "esto puede
          traer conflictos"). No hay préstamo eligiendo a la persona.
          1. Martín necesita que OT cuelgue el módem: carga "Colgar el módem en la pared" **para Marcos**.
          2. Marcos decide quién la hace (Nahuel, otro de OT o él mismo).
          3. Si Nahuel no llega, lo maneja Marcos, con la regla del pase de hoy. Martín no interviene.
          4. **La revisa Marcos.** Cuando la aprueba, queda terminada y a Martín le llega el aviso.
          5. **Martín puede pedir cambios** sobre la tarea terminada, con su motivo: se reabre y vuelve a Marcos,
             que decide quién la retoma. La reabre sólo quien la pidió desde otra área, y queda auditado.
          6. Cuando Marcos la vuelve a aprobar, a Martín le llega el aviso otra vez. La tarea de Martín puede
             esperar a ésta.
          - Así se van el préstamo directo y su aprobación; el primer circuito de aprobación vuelve a la J6. La
            tarea es del área de quien la hace (OT, con su evidencia), y guarda quién la pidió.
          - D11 cambia en consecuencia: si Martín nombra a alguien de otra área, la ayuda propone a su referente y
            lo explica.
        - **Orden:** "> aceptar la demora" de Dirección espera a la J5; en la J4, la única salida es cambiar la
          fecha.
      Incluye (usuario, 2026-10-14): si alguien escribe por Telegram "quiero crear una tarea" (o un objetivo),
      Leda le dice que eso se hace en la web y le ofrece el enlace, según lo que esa persona puede cargar.
      Es un hecho de la cocina, no frases (regla del mozo), y lleva su conversación de prueba contra la IA real.
      Hoy cae en "fuera de la lista": no se crea nada, Leda dice lo que sí puede hacer y deja un incidente de
      prioridad baja (`turno._manejar`). Con la Mini App cambia a ofrecer abrirla (`docs/ROADMAP.md`).
      Incluye también (usuario, 2026-10-14): cuando Dirección o administración carga una tarea que vence después
      que su objetivo, "> aceptar la demora" la carga directo, con una fecha prevista para el objetivo
      (decisión 7). El referente del objetivo recibe un aviso con la decisión. Necesita las previsiones de
      objetivos de la J5: si la J4 llega antes, esa salida espera a la J5.
      **J4a, construida** (escritor delegado, 2026-10-14). Commits:
      - `311e5b56`: la base y la migración `0071_la_carga_del_equipo`;
      - `9ce0b235`: el servidor;
      - `9d2fa373`: la web;
      - `cedc94d0`, `e48fa4d6`, `e7b176e0`, `1387c38c`, `3a29a51e` y `2ed6759d`: arreglos de RDD, la J3-6, la J3-7
        y pruebas.
      Qué trae:
      - **Cada tarea guarda quién la revisa y quién la pidió.** `quien_revisa_la_tarea` lee primero el de la
        tarea, así que la página, la escalera, la aprobación y el pase lo siguen.
      - **`cargar_tarea_web`** sirve a las dos puertas, con quién le carga a quién (D1b, D3, D4, D10, D13 y D14).
      - **La reapertura** por quien pidió la tarea: la tarea vuelve a `asignada`, con el referente del área como
        responsable.
      - **La web del equipo:** "> nueva tarea", "Lo que pediste" con "> pedir cambios" y "> pasarla" en el sector.
      - **Para la J4b:** la auditoría de cada carga guarda la puerta, quién revisa y quién pidió.
      Pruebas: las 30 de la base fallaron antes del código y pasan después. `tests/garantias`: 1004 passed, y las
      3 fallas eran de dos pruebas, ya arregladas. `npm test`: 244 passed.
      `leda_motor`: respaldo `leda_motor-antes-0071-20261014.dump`, ensayo en una copia descartable, `0071`
      aplicada y el pack reimportado (`niveles` con los nombres nuevos).
      **RDD** commit por commit: nueve revisiones, todas aprobadas, con 13 WARNING que pasan a la J4b. Entre ellos:
      - quién revisa queda fijo aunque la persona cambie de rol;
      - borrar el recuadro mientras arranca el dictado;
      - errores de pase y de reapertura mal clasificados;
      - quién decidió quedaba viejo al cambiar de espacio;
      - la línea del tipo y el artículo de los nombres;
      - la exención por nombre en `test_capacidades`;
      - pruebas atadas a la posición de una oración.
  - [x] **J4b · Los avisos de la carga y "quiero crear una tarea" por Telegram**, más los WARNING de la RDD de
        la J4a.
        **Construida** (escritor delegado, 2026-10-14) en los commits `c65917c2`, `034bc34d`, `542b621d`,
        `1a2bed65` y `463c5a12`, más la migración `0072_quien_revisa_sigue_activo`:
        - **Los WARNING de la J4a:** si quien revisa ya no está activo, revisa el aprobador de siempre; si nadie
          está activo, la escalera deja un incidente.
        - **Los avisos de la carga** (`motor/carga.py`): al responsable, uno solo a los 10 minutos y en horario;
          a quien revisa, cuando no es quien cargó; nada a Dirección por lo de un referente; el ciclo de los
          pedidos entre áreas (terminado y reabierto); Dirección como responsable no escala.
        - **La jugada `pedir_crear`** y las conversaciones 52 a 54.
        Pruebas: `tests/motor` 1461 passed, `tests/garantias` 1015 passed, `npm test` 261 passed, y en seco 53 de
        53. IA real, conversaciones 52 a 54: 9 de 9 (bitácora).
        `leda_motor`: respaldo `leda_motor-antes-0072-20261014.dump`, ensayo previo y la `0072` aplicada.
        **RDD** commit por commit: cinco revisiones, todas aprobadas. Sus 8 WARNING pasan a la primera unidad de la
        MA; entre ellos, una carga sin clave que no deja avisos y un aviso de "terminada" duplicado.
  - [ ] **J4-P · La prueba en el celular** (2026-10-14, guion `docs/product/guion-celular-j4.md`, completo).
        **Anduvo:**
        - los avisos de los pedidos: a Ismael el pedido a Dirección, a Ariel el de Marcos, y a administración que
          hay que conectar a Nahuel;
        - nada a Marcos por su tarea propia, ni a Ismael por lo que Marcos se cargó;
        - "Lo que pediste".
        **Hallazgos** (van con el escritor de la MA, en una unidad aparte):
        1. la vista previa de un pedido no dice qué es ("Es un pedido al área de Ariel: Ariel decide quién lo hace");
        2. un aviso de administración salió con `{nombre}` sin reemplazar;
        3. las respuestas por chat a "quiero crear" salieron toscas ("por chat no se creó": un dato de la cocina);
        4. "espera a" no muestra lo recién cargado, porque no se vuelven a leer las opciones;
        5. la ortografía al confirmar falla siempre en la web del equipo (la IA no usa la herramienta);
        6. "Tarea cargada" va al lado de "confirmar", en verde agua;
        7. no llegó el aviso a quien revisa (Marcos) por la tarea que Ismael le cargó a Nahuel, que no tiene
           Telegram;
        8. el aviso a Ariel dice el área al revés ("para el área de OT");
        9. las tarjetas no se abren: falta el detalle, que es también el destino de "Ver la tarea";
        10. las advertencias tienen que ir en color;
        11. "Lo que pediste" pasa a pestaña propia, sin repetir el pedido en las tareas;
        12. los nombres de las pestañas (usuario: "mucho mejor"):
            - Dirección: "Mis tareas" y "Todo el equipo";
            - un referente: "Mis tareas", el nombre de su área ("OT y automatización") y "Lo que pedí";
            - un integrante: "Mis tareas", y "Lo que pedí" desde la J6.
        La prueba se repite con la MA.
- [x] **MA · La web como Mini App de Telegram** (cerrada el 2026-10-15, madrugada), adelantada por el usuario (2026-10-14: "quisiera atacar antes
      lo de la mini app"; opción A: apenas termine la J4, antes de J5 a J7). Así las pruebas de J5 a J7 se hacen
      desde el botón del bot, sin pedir enlaces.
      - **No espera a la VPS:** el túnel ya es HTTPS, y Leda manda en el chat un botón "Abrir Leda" con la
        dirección del momento. El botón fijo del menú queda para el servidor definitivo.
      - **La entrada:** Telegram le pasa a la web quién es la persona, con una firma que el servidor verifica con
        el token del bot. Es una enmienda a la decisión 4 del ADR 0022, y primero va su diseño escrito.
      - **Por Telegram:** se resuelve lo de ofrecer abrirla ante "quiero crear una tarea" (ROADMAP).
      Las decisiones se le traen al usuario antes de escribir código.
      **En la prueba de la MA, recordarle al usuario que mire también la J3-6 y la J3-7** (2026-10-14: "lo miro junto
      con la prueba de la mini app, recordámelo"): el botón de borrar, "confirmar" apagado, las pestañas "Tarea" y
      "Objetivo", los nombres objetivo general, etapa y objetivo de área, y "Es parte de". Con su visto bueno se
      cierra la J3. Va como pasos del guion de la MA.
      **Construida** (escritor delegado, 2026-10-14), con la migración `0073_entrar_con_telegram` y los commits
      `b907b9ae`, `f5b03cd4`, `70c0900b`, `ad46fd6a`, `cc57015b`, `3dc4c206`, `7ebf2a8c` y `c324bfcf`:
      - **La entrada:** la firma de Telegram se comprueba en el servidor, vale 10 minutos y una sola vez.
      - **El QR** para la computadora, con `src/leda/qr.py`, un codificador sin dependencias.
      - **Los bots:** "Entrar en la compu" y "Administración".
      - **Botones en lugar de enlaces,** que llevan directo a lo que dicen.
      - **La Mini App en la web:** `ready`, `expand`, los colores de Leda y el botón "Atrás".
      - **El tiempo de la computadora,** configurable por equipo.
      - **Los arreglos de la prueba de la J4,** salvo lo que sigue.
      Pendientes:
      - el detalle de la tarea no muestra quién la pidió, qué espera ni quién la espera;
      - la ortografía de la puerta del equipo: las dos puertas mandan lo mismo a la IA, así que hay que mirarla
        con la IA real;
      - cuánto dura la sesión de administración en la computadora (hoy, sin vencimiento);
      - desde Telegram Web no apareció ningún QR (usuario, 2026-10-14): resuelto por la MA-5, que entra sin QR
        desde Telegram en la compu (prueba de cierre, 2026-10-15).
      IA real, conversaciones 50 y 52 a 54: 12 de 12. `leda_motor`: respaldo
      `leda_motor-antes-0073-20261014.dump`, ensayo previo y la `0073` aplicada. Guion de la prueba:
      `docs/product/guion-celular-ma.md`.
      RDD commit por commit: siete revisiones aprobadas, con WARNING de casos de borde. El `70c0900b` no entraba en
      el presupuesto del revisor y se revisa en cuatro tramos.
      Los cuatro tramos del `70c0900b` quedaron aprobados: `review-7ad295d37cfb5b24`, `review-fa42ef1720de99d4` (con los
      cuatro lentes, entre ellos el de riesgo, con dos WARNING de seguridad), `review-d86ed7bfa16f651a` y
      `review-14e9d271659c29c9`. Todos los WARNING de la MA pasan a una última unidad del escritor, primero los de
      seguridad. Lo que haya que cambiar en la base va en la `0074`, porque la `0073` ya está aplicada.
      **Hecho, tras el paso 1 de la prueba:**
      - el botón fijo del menú, en `58d91ba3`;
      - "abrí la app" y el mensaje sin jugada, en `2edebfb6` y `bf961074`, con la conversación 55;
      - los WARNING de RDD, en `c5815851` y `0beaf5cc`, con la migración `0074`.
      Suite: 3595 passed; la única falla era una huella esperada y quedó actualizada. En seco, 54 de 54.
      `leda_motor`: respaldo `leda_motor-antes-0074-20261014.dump`, ensayo previo y la `0074` aplicada.
      Algunos archivos habían quedado con fin de línea CRLF y git veía esos commits como reescritos enteros. Se
      restauró LF en `32a374d0`. RDD de `2edebfb6`, `58d91ba3`, `c5815851` y `0beaf5cc` (los tres últimos sobre una copia en
      LF): las cuatro aprobadas. Sus WARNING van con los hallazgos de la prueba de la MA en una última tanda; entre
      ellos, una falla del botón del menú que corta el registro de los webhooks, y la ventana de la firma, cuyo
      comentario contradice el valor. IA real, 50 y 52 a 55: 14 de 15, con garantías 15 de 15; la falla es de
      formato.
      **Prueba de la MA (2026-10-14):** en Telegram de escritorio, la Mini App mostró "rechazó la conexión", porque
      Telegram la abre dentro de un marco y la web no se deja enmarcar. Decisión del usuario: en Telegram de escritorio,
      el botón lleva a la página del QR en el navegador, como cualquier compu. El usuario sólo tiene a Ariel en el
      celular: la Mini App se prueba con Ariel, y Marcos e Ismael con Telegram de escritorio. Un escritor (MA-2) hace
      lo de escritorio, los WARNING de las últimas revisiones y el detalle de la tarea completo.
      **Prueba de la MA con Ariel en el iPhone (2026-10-14).** El botón del menú y la Mini App anduvieron. Correcciones
      del usuario (MA-3, al mismo escritor):
      1. El botón del menú se llama "Mi panel".
      2. El detalle de la tarea se ve dentro de la app, con su estilo y "> volver".
      3. La Mini App ocupa la pantalla completa.
      4. "salir" se va de la Mini App y queda sólo en la compu. "> Nueva tarea", con mayúscula, va abajo como botón
         principal. "Volver al chat" va abajo a la izquierda, chico. Se va "> consultar a leda".
      5. Las pestañas "Mis tareas", "Mi equipo" y "Lo que pedí" van en una sola fila, como pestañas de verdad.
         "Mi equipo" muestra sólo las tareas de la gente del referente, con el nombre del área como dato, y no
         aparece si no tiene a nadie a cargo.
      6. El título y el nombre de la persona en la misma línea. "N activas" pasa al bloque de contadores, donde sirve.
         Todo entra en una pantalla: sólo se desplazan las tarjetas de tareas.
      7. Los contadores quedan Vencidas · Sin empezar · En curso · Trabadas · Entregadas, sin "Activas" ni total. Una
         vencida también cuenta en su estado. El nombre de la persona nunca se corta: si no entra, sigue en una segunda
         línea alineada a la derecha, sin mover el título.
      En Telegram de escritorio el mensaje dice "Abrí Leda en el navegador".
      **MA-2 y MA-3, hechas** en los commits `90516634`, `9288fd54`, `cf2fa4cc`, `dd7574b9`, `10b6bbe5` y `e46044e9`, con la
      migración `0075`:
      - el lanzador para Telegram en computadora (ADR 0024, punto 12);
      - el botón del menú ya no corta los webhooks ni el escuchador;
      - el detalle de la tarea dentro de la app, con quién la pidió, qué espera y quién la espera;
      - todas las correcciones del iPhone.
      Suite: 3623 passed, más una lista de importaciones corregida y verificada en su archivo. En seco, 54 de 54.
      `npx vitest`: 310 passed. `leda_motor`: respaldo `leda_motor-antes-0075-20261014.dump`, ensayo previo y la `0075`
      aplicada. La web, rearmada y reiniciada. RDD de los seis commits, sobre una copia en LF: aprobados. Quedan WARNING
      menores para una tanda posterior, sin ninguno de seguridad:
      - el motivo de una falla del menú se clasifica por el texto del mensaje;
      - "Mi equipo" filtra las terminadas por el nombre;
      - si falla la pantalla completa, no hay alternativa;
      - la pantalla fija no se adapta a un celular muy bajo;
      - algunas pruebas no demuestran lo que dicen.
      Falta la prueba del usuario.
      **Prueba de MA-2 y MA-3 (2026-10-14, noche):** "muy bueno como quedó", con Ariel en el iPhone e Ismael y Marcos en
      el navegador de la compu. Los botones de arriba de la Mini App: "espectaculares". Ajustes (MA-4, escritor
      delegado):
      1. el botón se llama "Mi espacio" (el del menú y el del chat), y Leda lo ofrece en pocas palabras;
      2. la barra de desplazamiento con el estilo de la app, y la web usa todo el ancho en la compu;
      3. las pestañas "Mi área" (antes "Todo el equipo") y "Mis pedidos" (antes "Lo que pedí");
      4. el nombre y el área de la persona arriba a la derecha, en lugar de la semana y la fecha, fijos en todas las
         pestañas;
      5. se eliminan "Volver al chat" y "salir"; la sesión de la compu se cierra por chat;
      6. "> Nuevo objetivo" va abajo, junto a "> Nueva tarea".
      **MA-4, construida (2026-10-14, noche; escritor delegado, ruta delegada por tocar web y servidor):**
      `4816e96b` (la web: nombre y área arriba, las dos altas abajo, todo el ancho, la barra, sin "Volver al chat"
      ni "salir"), `266d0d7c` (el botón del menú "Mi espacio"; el "dentro de Telegram" salía de los hechos de la
      cocina, `hechos.py` y `fichas.py`, y se corrigió ahí, sin tocar las instrucciones de la IA) y `719b59e2` (el
      botón del chat que abre la app dice "Mi espacio" para todos; Dirección sigue entrando por "Mi área"; los
      botones que llevan a algo concreto conservan su nombre, MA3). `npm test` 313 passed; pytest de los archivos
      tocados 145 passed y 41 de 41 en la API; repetido por el coordinador: 43 passed. RDD (`tools/rdd_ciclo.py`,
      base `6cd5541e`): **aprobada**, reconocida `review-78fd7aaba69d3c5d`; dos WARNING (no queda forma de cerrar la
      sesión de la compu; el componente `SignOut` quedó sin uso) y seis sugerencias menores. IA real, 50 y 55,
      `--veces 3`: **5 de 6**, garantías 6 de 6; la falla es la deuda de formato conocida (55, vez 3: la pregunta
      a Marcos en un renglón de más de 140 caracteres). Pendiente: **cómo se cierra la sesión de la compu por
      chat** (hoy sólo "perdí el celular", que corta todas) y la prueba del usuario.
      **MA-5 y MA-6 (2026-10-14, noche; escritor delegado):** `98c5758f` (pedir abrir la app → "tocá «Mi
      espacio»", sin botón; la bienvenida conserva el suyo), `0ee6162c` (una Mini App recargada con la firma
      vencida sigue con su sesión; sin sesión, el aviso dice «Cerrar» y «Mi espacio»), `30d8d8f0` (Telegram en la
      compu abre el navegador ya adentro con un pase de un minuto; migración `0076_el_pase_a_la_compu`, aplicada en
      `leda_motor` con respaldo `db/respaldos/leda_motor-antes-0076-20261014.dump` y ensayo en una copia),
      `86196393`, `11be9cc3`, `f5eb1e34` (el referente ve "Mi área", sin el área bajo el título) y `b4b9df87`
      (Dirección: "Mis tareas" y "Áreas", con una tarjeta por área, por orden alfabético porque la base no guarda
      el del pack). `npm test` 325 passed y 29 archivos; pytest de lo tocado 304 y 171 passed. RDD aprobada:
      `review-70c1859cc3a81102` (MA-5; WARNING: si Telegram no fijó el botón del menú, Leda igual lo nombra; no hay
      prueba de que el pase no quede en un registro de accesos) y `review-43a52c1abab65531` (MA-6; un WARNING
      menor en `web/src/App.tsx:117`). Falla vista en el celular y resuelta: el primer servidor web de la sesión
      rechazaba toda firma (causa no encontrada; al reiniciarlo, entró); un registro temporal confirmó dos
      entradas aceptadas.
      **Prueba de cierre (usuario, 2026-10-15, madrugada): pasada.** Dirección con "Mis tareas" y "Áreas"; el
      referente con "Mi área"; Telegram en la compu entra sin QR; Marcos carga para su área y le pide a Dirección
      (las tareas aparecen; los avisos por chat quedaron guardados hasta el horario del espacio, como corresponde);
      "quiero crear una tarea" ofrece "Cargar la tarea". El "te espera" que se esperaba en el pedido a Dirección
      era un error del guion: sólo aparece cuando una tarea de otro espera la de la persona.
      Ronda con la IA real de las conversaciones 50 y 55 sobre la MA-5 (2026-10-15, `--veces 5`, sobre `ee3fb859`):
      10 de 10, garantías, comprensión y formato (bitácora).
      **Cómo se cierra la sesión de la compu** (usuario, 2026-10-15, madrugada): la compu sigue recordada el
      tiempo que elige el administrador para cada equipo (cerrar la pestaña no la cierra; opción A), y vuelve
      un **botón "Cerrar sesión" sólo en la compu**, debajo del nombre y el área de arriba a la derecha; nunca
      en la Mini App. Es la **MA-7**, para la próxima sesión (no se empezó).
- [x] **MA-7 · "Cerrar sesión" en la compu** (decisión de arriba). Reusar `/app/salir` y `/app/admin/salir`, que
      siguen en el servidor; borrar el `SignOut` sin uso; también en la administración en la compu. Prueba
      primero (vitest: se ve en el navegador, no en la Mini App), RDD y la mirada del usuario cuando esté.
      **Hecha (2026-10-15; escritor delegado):** `f89f5599`. El `SignOut` pasó a ser el "Cerrar sesión" del
      encabezado, debajo del nombre y el área, chico y gris, con su confirmación ("Para volver a entrar vas a
      tener que escanear el código otra vez." · "no, seguir" / "sí, cerrar") y su aviso si falla; en la página
      del equipo y en la administración (el "salir" del pie de la administración se fue). Nunca adentro de
      Telegram (`insideTelegram()`, en las dos puertas: desde ahí no se puede escanear el QR). Después de
      cerrar, la página del equipo dice "Cerraste la sesión." con la entrada por Telegram, igual que la
      administración. Prueba primero: `web/src/ma7.test.tsx` (8 casos) y los de MA-3, MA-4 y `AdminApp`
      ajustados; RED observado (7 fallas), después `npm test` 338 passed y 30 archivos, `npm run build` bien
      (`web/dist` no está en Git). El comentario de `web/src/components/Footer.tsx` se corrigió en `e8b81a99`.
      RDD aprobada, `review-07077f99f348d3fc` (un WARNING: no hay prueba de volver a entrar después de cerrar,
      `web/src/App.tsx:275-278`; va con las deudas de la MA). Pendiente: la mirada del usuario en la compu.
- [x] **Deudas de la MA** (2026-10-15; escritor delegado; prueba primero en cada una):
      - **Quién pidió una tarea propia** (`cc286185`): en "Mis tareas", una tarea propia que pidió otra
        persona dice debajo del título "└─ te la pidió Marcos Tarquini" (el nombre entero, como lo da la
        base); la que pidió la misma persona, o la que nadie pidió, no. El servidor lo agrega a la lista
        de "Mis tareas" (`_quien_las_pidio`: `task.pedida_por_membership_id`, sólo de las tareas que la
        base ya le mostró a la sesión y en su espacio); sin migración. **Se hizo así y se puede
        cambiar** (anotado en "Para decidir al despertar"). RED observado (`KeyError: 'pidio'` y la
        tarjeta sin la línea), después verde.
      - **El pase de la compu en los registros** (`a713e751`, advertencia de la MA-5): ningún registro
        del servidor, a ningún nivel, escribe el pase ni la firma (emitir y canjear, usado o no, en las
        dos puertas; la prueba confirma que la captura anda porque el navegador de la prueba sí anota la
        dirección), y `python -m leda servir` arranca uvicorn sin el registro de accesos. Pasó de
        entrada: no se registraba; queda como guarda. El riesgo que queda es arrancar uvicorn a mano
        sin `--no-access-log`.
      - **Volver a entrar después de cerrar la sesión** (`476e86aa`, advertencia de la MA-7): el QR de
        "Cerraste la sesión." vuelve a pedir quién es y sus tareas. Pasó de entrada; rompiendo `enter`
        a propósito, falla.
      - **El área de la dirección** (`0585cd6c`, advertencia de la MA-6, `App.tsx:117`): un área que el
        servidor no conoce para esa persona (404) vuelve a "Áreas", sin la página de error; quien no
        tiene "Áreas" ve sus tareas y no le aparece el «Atrás» de Telegram. El servidor ya lo negaba
        (`test_areas_es_solo_de_direccion_y_de_su_espacio`: área de otro espacio o inventada, 404; quien
        no es Dirección, 403). RED observado (dos fallas), después verde.
      Verificación: `npm test` 343 passed y 30 archivos; `npm run build` bien; pytest de
      `test_quien_ve_que`, `test_entrar_con_telegram`, `test_enlace_y_sesion`, `test_lectura`,
      `test_api_de_la_plataforma` y `test_capacidades`: 184 passed. Comentario de `test_capacidades`
      puesto al día (`web_app.py` ya lee `pedida_por_membership_id`). RDD aprobada sobre todo el tramo
      desde `825676d7` (con el ensayo de propiedad), `review-f874480b32eaa102`; advertencias sin arreglar,
      casos de borde: un 404 de un área vuelve con `history.back()` y podría caer en otra entrada vieja
      (`App.tsx:180-182`); la prueba de otro espacio en "te la pidió" podría pasar vacía
      (`test_quien_ve_que.py:657-666`). La ortografía con la IA real (`tools/medir_ayuda_al_cargar.py
      --veces 1`, 2026-10-15): los tres casos de ortografía bien (bitácora); las dos fallas del 14/10 no se
      repitieron.
      **Prueba en el celular, paso 1** (usuario, 2026-10-14): "quiero ver mis tareas" se contestó bien, con la lista en el
      chat y sin botón. Decisión del usuario: el **botón fijo del menú del bot** ("Tareas"; "Administración" en el
      bot de administración) siempre a mano; se arma ya con el túnel, porque cada arranque del escuchador actualiza
      la dirección (`setChatMenuButton`). Leda ofrece un botón **sólo para lo que se hace sí o sí en la app** (crear
      una tarea, ver una tarea cargada), no en cada respuesta.
      **Decisiones del usuario (2026-10-14):**
      - **MA1. En el celular, sólo la Mini App: los enlaces desaparecen.** Hay que revisar cada lugar donde Leda
        ofrece o manda un enlace (el pedido de acceso, el ofrecimiento de una sola vez, la bienvenida, los avisos
        y "quiero crear una tarea"). Ahí Leda pregunta si querés abrir la Mini App, u ofrece el botón para
        abrirla cuando quieras. Leda nunca sugiere pedir un enlace.
      - **MA1b. En la computadora, ni Telegram Web ni enlaces** ("son bastante molestos"): **un código por
        Telegram, sin contraseña.**
        - La persona pone su usuario y Leda le manda por Telegram un código de 6 números que vence en minutos y
          sirve una vez.
        - La computadora queda recordada el tiempo que elige el administrador **para cada equipo**, desde la web
          de administración: 1, 7, 30 o 90 días, o **sin vencimiento**, que es el valor de entrada para todos.
        - Se corta al cerrar la sesión, con "perdí el celular", con la baja o cuando lo corta el administrador.
        - "Iniciar sesión con Telegram" (el botón oficial) queda para la VPS, porque pide una dirección fija.
      - **MA2. La administración también como Mini App,** en `@Leda_Admin_bot`, y por la web de la computadora
        con el código por Telegram, que llega por ese bot. Ahí se van a usar más las opciones y la configuración,
        así que la pantalla se diseña para la computadora. El canal decide el sombrero: la Mini App del bot del
        equipo entra como integrante, y la del bot de administración como administrador.
      - **MA3. Dónde aparece el botón y qué dice.** Dice lo que va a pasar, nunca "Abrir Leda", y **lleva
        directo a eso, no a la página principal**:
        - cuando lo pide la persona y en la bienvenida: **"Ver mis tareas"** (a Dirección, **"Ver el equipo"**);
        - en un aviso de carga: **"Ver la tarea"**, que abre esa tarea;
        - ante "quiero crear una tarea": **"Cargar la tarea"**, que abre el formulario;
        - ante "quiero crear un objetivo" (Dirección): **"Crear el objetivo"**;
        - en el bot de administración: **"Administración"**;
        - con la VPS, el botón fijo del menú: **"Tareas"**.
        No va en cada mensaje (recordatorios, preguntas) ni en grupos, donde Telegram no lo permite. Si se
        reinicia el túnel, los botones viejos dejan de andar: se toca uno nuevo.
        - **2026-10-14, noche (usuario, MA-5):** cuando la persona le pide a Leda abrir o entrar a la app
          (`pedir_acceso_web`), la respuesta ya no lleva botón: Leda le dice que la abre con el botón fijo
          "Mi espacio" del menú, al lado de donde escribe. La bienvenida conserva su botón "Mi espacio"
          exactamente como hoy; los de un destino concreto ("Ver la tarea", "Cargar la tarea", "Crear el
          objetivo") siguen igual.
        - **2026-10-14, noche (usuario, MA-6):** las pestañas de Dirección pasan a "Mis tareas" y "Áreas", sin
          "Mis pedidos". "Áreas" abre con una tarjeta por área (nombre · referente, y debajo sólo los números
          que tienen algo, con los colores de siempre; sin nada abierto, en gris); al tocarla, la lista y la
          semana de esa área, con "‹ Áreas" para volver; la dirección guarda dónde está (`?vista=areas&area=`).
          Los números los cuenta el servidor con las mismas reglas que los de arriba. El orden de las áreas
          es por nombre: la base no guarda el orden del pack. El botón del chat a todo el equipo
          (`?vista=equipo`) abre "Áreas". Referentes e integrantes, sin cambios.
      - **MA4. Cómo se ve:**
        - el aspecto oscuro de Leda, gris y con letra de máquina, sin tomar los colores de cada Telegram;
        - grande, pero dejando la barrita de Telegram con "Cerrar": se usa `expand()`, no la pantalla completa;
        - el zoom con dos dedos se prueba en el celular. Si dentro de la Mini App la página ya no se agranda sola
          al tocar un campo, se libera; si se agranda, queda bloqueado como hoy.
      - **MA5. Fuera de Telegram, siempre el código por Telegram,** también en el navegador del celular. Es una
        sola puerta para todo lo que no es la Mini App. Adentro de Telegram, cada apertura vuelve a identificar a
        la persona, así que no hace falta un "Salir".
      - **MA1c. El código pasa a ser un QR, como WhatsApp Web** (usuario, 2026-10-14: "el qr es mucho mejor").
        La compu muestra un QR; se escanea con la cámara del celular y Telegram abre el chat de Leda con
        "Entrar en la compu". No hay usuario ni código para tipear. En el navegador de un celular, fuera de
        Telegram, aparece "Entrar con Telegram". La dirección es fija con la VPS; mientras dure el túnel, Leda
        la pasa por chat si se le pide.
      Con esto, las decisiones de la MA están completas. Su diseño escrito es el
      [ADR 0024](../../docs/decisions/0024-entrar-con-telegram.md), aceptado por el usuario el 2026-10-14
      ("si").
- [ ] **J5 · El pedido de más tiempo y el cambio de fecha.**
      Incluye la decisión 7 del 2026-10-14: la fecha prevista de los objetivos y "> aceptar la demora", con
      la fecha original intacta, para los objetivos hijos (decisión 5) y para las tareas de Dirección
      (decisión 6).
      **Decisiones del usuario (2026-10-14):**
      - **J5-D1. Dos botones distintos, por chat y por la Mini App:**
        - **"> Me falta algo para seguir"**, cuando la demora depende de otro ("no llegó el cable"). Arranca el
          circuito del bloqueo que ya tiene el motor (`motor/persecucion.py`): pregunta qué falta y quién se
          ocupa, le escribe a esa persona, le repite cada día hábil sin escalar, sigue la cadena y avisa lo que
          diga. Mientras tanto, la demora no es de quien la espera.
        - **"> pedir más tiempo"**, sólo cuando la demora es del propio trabajo. Ése es el pedido que alguien
          decide.
        Si se pide más tiempo con un motivo que es de otro, Leda pregunta si le falta algo y sigue por el bloqueo.
      - **El lenguaje (usuario: "trabado" no deja claro que depende de otra cosa):** en todo lo que ve la persona,
        en el chat y en la web, se reemplazan "trabado" y "bloqueada". La web dice "Esperando el cable
        (Mariano)". Los nombres internos no cambian. Es una tarea aparte, antes de la J5.
      - **J5-D2. Quién decide más tiempo, con la misma regla de la J4 (D4):** decide quien revisa la tarea. Si
        Lucas lo pide, decide Martín. Un referente, en una tarea suya, lo cambia él mismo, y Leda sólo lo anota
        con la fecha original y la prevista. Lo mismo Dirección en una tarea propia. **Si la fecha nueva pasa la
        del objetivo,** es igual que la decisión 6: Leda frena, avisa que el objetivo se demoraría, y lo **aprueba**
        el referente del objetivo (Ismael, si el objetivo es de Dirección). Hasta que aprueba, no corre.
      - **J5-D3. Todo pedido de más tiempo de un integrante lo decide su referente,** sea de 1 o de 10 días
        (usuario: si un integrante corre la fecha solo, el plan del referente se mueve sin que lo decida). Hasta
        que decide, vale la fecha original y los recordatorios siguen sobre ella. El umbral de 3 días del pack
        no se usa para esto; queda anotado por si sirve, por ejemplo, para avisarle a Dirección de los
        corrimientos grandes.
      - **J5-D3b. El pedido le muestra al referente qué impacta aceptarlo** (mecánica §4, el impacto en cadena),
        antes de decidir:
        - qué tareas esperan a ésta y cómo se correrían, con sus responsables;
        - si se pasa la fecha del objetivo y, entonces, quién tiene que aprobarlo;
        - si no impacta nada, que lo diga: "No demora a nadie más".
        Ejemplo: "Si aceptás, «Pasar los cables» de Lucas no puede empezar hasta el 23 y vence el 24: llegaría
        justo".
      - **J5-D3c. "En qué afecta", regla general** (usuario: "recontra importante… cualquier cosa que modifique un
        plazo de una tarea tiene que dar ese informe"). Todo cambio de plazo trae su informe de impacto: un
        pedido de más tiempo, una demora aceptada, un cambio de fecha directo o una tarea que espera algo de otro y
        se demora. El informe dice:
        - qué depende de esa tarea y cómo se correría, con su responsable, y si llega justo o se atrasa;
        - si se pasa la fecha de un objetivo;
        - si no afecta nada, "No demora a nadie más".
        Lo reciben quien decide y los referentes de las tareas afectadas. Dirección lo recibe sólo cuando toca la
        fecha de un objetivo o una cadena que cruza áreas.
        **Siempre antes de decidir** (usuario: "si no, no tiene ningún sentido"): va dentro del pedido, antes de
        "aceptar" o "no"; y cuando el cambio no necesita aprobación (un referente en una tarea suya), en la vista previa,
        antes de confirmar. Después de decidir sólo se avisa lo que se decidió.
      - **J5-D4. Al aceptar más tiempo, la fecha original queda y se anota la prevista** (el modelo de la
        decisión 7), con el motivo y quién la aceptó. Leda sigue la prevista. La web muestra "21/10 → previsto
        28/10, aceptado por Marcos: era más trabajo". El informe de "en qué afecta" se ve antes de aceptar, lo
        afecte o no.
      - **J5-D5. El cambio de fecha directo, cuando cambió el plan** (nadie lo pidió; ejemplo: Marcos corre "Revisar
        el tablero" del 22/10 al 30/10 porque primero va otra cosa). Lo hacen quien revisa la tarea y Dirección, con
        "> cambiar la fecha": motivo obligatorio y el informe de "en qué afecta" antes de confirmar. La fecha nueva
        pasa a ser el compromiso, sin "previsto" ni atraso, porque no fue un atraso de nadie; la anterior queda en el
        historial con el motivo y quién la cambió. Al responsable le llega el aviso, y si se la adelantan, se lo dice
        claro.
      - **J5-D6. Decir que no lleva motivo, y le llega al que pidió:** "Marcos no aceptó pasar la tarea al 28: la
        necesita para la auditoría del 22. Sigue para el 21/10". Ningún mensaje deja a la persona sin saber qué sigue.
      - **J5-D7. Un pedido sin contestar:** Leda se lo recuerda a quien decide cada día hábil, como una pregunta
        sin contestar, sin escalar. Mientras tanto vale la fecha original y los recordatorios siguen sobre ella. A
        quien pidió le avisa que su pedido sigue esperando. Nunca se acepta solo.
      - **J5-D8. Un pedido nuevo reemplaza al pendiente:** a quien decide le llega uno solo, con su informe, sin la
        línea "antes había pedido…" (cambiado por la regla general de los avisos, J6-D4). Nunca se decide sobre un
        pedido viejo.
      Con esto, las decisiones de la J5 están completas.
      **Plan en porciones** (planificador de sólo lectura, 2026-10-15, noche; las preguntas que dejó abiertas
      están en "Para decidir al despertar", "J5: lo que las decisiones no alcanzan a fijar"):
      - **S0.** ADR 0025 (enmienda el 0018, 9a y 9i: una fecha más tarde deja de anotarse sola; y el 0022,
        decisiones 8 y 9), propuesta hasta que la acepte el usuario.
      - **S1.** Conversaciones de prueba primero: 56 (pedir más tiempo por el propio trabajo), 57 (el motivo es
        de otro: los dos botones), 58 (quien decide se la cambia a sí mismo, con vista previa), 59 (pasa la
        fecha del objetivo), 60 (no aceptado, con motivo), 61 (un pedido nuevo reemplaza al pendiente), 62
        (cambio de fecha directo); reescribir la 02 y revisar las doce que usan `anotar_prevision`.
      - **S2.** La base: el cambio de fecha auditado (`cambio_de_fecha`, con el molde de
        `cambio_de_responsable`); hoy `bloquear_estado_directo` no deja cambiar la fecha.
        **S2 hecha (2026-10-15; escritor delegado):** `44747b27`, con la migración `0077_el_cambio_de_fecha`
        (y su rollback; `leda_motor` sigue en la `0076`, sin aplicarla). Sólo el mecanismo: la fecha de una
        tarea cambia sólo al agregarse una fila en `cambio_de_fecha` (fecha anterior, nueva, motivo
        obligatorio, quién lo hizo, quién lo decidió y la clase `cambio_directo`), que nadie edita ni borra.
        Su disparador (`aplicar_cambio_de_fecha`, de `leda_owner`) rechaza un cambio pensado sobre otra
        fecha, una tarea cerrada, una de otro espacio (igual que un id inventado) y una fecha que ya pasó o
        que no es un día hábil del espacio (`es_dia_habil`). No escribe auditoría: el molde tampoco; la
        escribe la función que lo use (S6). Quién puede cambiar una fecha y la fecha del objetivo quedan
        para la S6. Evidencia: `pytest tests/garantias/test_cambio_de_fecha.py test_migraciones.py
        test_capacidades.py test_aislamiento.py`, 42 passed (antes, en rojo: 10 de las 15 nuevas);
        `pytest tests/garantias`, 1124 passed (22 min). RDD aprobada, `review-36dd84fc5a98440e`; advertencia: "ya
        pasó" se mide contra el `at` que trae la fila (el reloj de Leda, como el resto de los eventos), así que
        quien escribe la fila lo fija; la S6 lo pasa siempre desde `reloj.ahora()`.
      - **S3.** El pedido con su estado, la previsión aceptada y la fecha prevista de los objetivos.
      - **S4.** "En qué afecta", una sola regla en la base para el chat y la web.
      - **S5.** "> aceptar la demora" en los objetivos (web; decisiones 5 a 7).
      - **S6.** "> cambiar la fecha" directo (J5-D5).
      - **S7 a S9.** El chat: pedir más tiempo, el motivo de otro y los dos botones, decidir y lo que sigue.
      - **S10 y S11.** La web: los dos botones de quien la hace y el bloque de decisión del referente.
      - **S12.** Rondas con la IA real de las conversaciones tocadas, la prueba en el celular y RDD por commit.

- [ ] **J6 · La propuesta del integrante** (sólo el integrante propone; Dirección y los referentes crean
      directo).
      Incluye la decisión 6 del 2026-10-14: seguir con una tarea que vence después que su objetivo pide la
      aprobación del referente del objetivo, con la misma maquinaria de las propuestas.
      Incluye también (usuario, 2026-10-14): **la propuesta de objetivo de un referente**. Martín toca "> proponer
      un objetivo" en su web, con el mismo formulario y la ayuda de la IA. A Ismael le llega un aviso, y lo aprueba
      (tal cual o con cambios) o lo rechaza con el motivo, que Martín recibe. Por Telegram, Leda le ofrece el enlace
      para proponerlo.
      Si quien carga es Dirección o administración (usuario, 2026-10-14): Leda le avisa que demora el objetivo;
      si acepta, se carga directo, sin pedirle la aprobación al referente del objetivo, y el referente recibe un
      aviso de Leda con la decisión de Dirección. Esa parte va en la J4, con la carga de Dirección y sus avisos.
      **Decisiones del usuario (2026-10-14, antes del código; mapa del explorador en esta sesión):**
      - **J6-D1. Hacerlo lo más simple posible para el integrante** (usuario: "él se basa en sus tareas"). Nahuel no
        ve objetivos en ningún formulario.
        - **Subtareas** (mecánica §1, `task.parent_task_id`, que hoy no se usa): desde su tarea, "> agregar una
          subtarea" ("Comprar los tornillos" dentro de "Colocar el estante"), con la ayuda de la IA. Hereda el
          objetivo. La tarea no se da por terminada con subtareas abiertas, así que no hace falta marcar una espera.
          La aprueba su referente, que ve antes el informe de "en qué afecta".
        - **Sólo para sí mismo:** si necesita que lo haga otro, lo pide.
      - **J6-D2. "Lo que pedí" también para el integrante, unificado con "Me falta algo para seguir".** Lo que no
        depende de él ("necesito el cable de 10 metros") se lo pide a su referente.
        - Marcos decide: lo hace él (la compra), lo pasa, o dice que no, con el motivo.
        - Nahuel ve en "Lo que pedí" en qué está su pedido.
        - Al resolverse, le llega el aviso y su tarea puede seguir.
        - "Me falta algo para seguir" (J5-D1) es lo mismo: queda como un pedido en "Lo que pedí" a quien se ocupa,
          con el seguimiento del bloqueo que ya hace el motor, y la tarea lo espera. Antes de trabarse se llama
          "pedir", después "me falta algo": es una sola cosa.
        - La regla para todos: a quien está arriba se le pide lo que no depende de uno.
      - **J6-D3. Cómo decide el referente una subtarea:** aprobarla tal cual, corregirla y aprobarla (a Nahuel le llega
        qué cambió), o decir que no con el motivo. También puede dársela a otro de su gente ("que los compre Juan"),
        avisándoles a los dos. Avisa Leda, por chat: el referente decide en la web y Leda avisa a quien corresponda.
      - **J6-D4. El circuito**, con el molde de la J5:
        - el aviso al referente lleva "Ver la subtarea" o "Ver el pedido" y llega en horario; las que se proponen
          seguidas van juntas, con 10 minutos de margen;
        - lo propuesto un sábado sale el lunes, y Nahuel ve cuándo lo va a ver Marcos;
        - sin respuesta, un recordatorio cada día hábil, sin escalar; nunca se aprueba sola;
        - antes de que decidan, Nahuel puede retirarla o corregirla.
      - **Regla general de los avisos** (usuario: "no importa lo que decía antes, importa lo que dice ahora"): se cuenta
        lo que vale ahora, no la historia; la historia queda en el detalle.
        - Si se corrige, sólo la versión nueva, sin "antes decía".
        - Si se retira, no se manda ningún mensaje: desaparece de lo que hay para aprobar, y quien abra el aviso
          viejo ve "Ya no hace falta".
        - Esto cambia la J5-D8: sin la línea "antes había pedido hasta el 28".
        - **El botón de Nahuel dice "> ya no hace falta"** (no "retirar", que genera dudas) y pregunta por qué en una
          línea. Si lo resolvió él: "Ya no hace falta: Nahuel lo resolvió (los encontró en el taller)". Si fue otra
          cosa: sólo "Ya no hace falta", sin inventar que lo resolvió.
      - **J6-D5. La propuesta de objetivo de un referente no existe para nadie hasta que Dirección la aprueba.** Martín
        la ve sólo en "Lo que pedí" ("esperando a Ismael") y no le puede cargar tareas. Ismael aprueba, corrige o dice
        que no con el motivo.
      - **J6-D6. A quién se pide:** siempre al referente propio. Algo de otra área lo pide a Marcos, que si está de
        acuerdo lo convierte en un pedido entre áreas (J4); Nahuel nunca tiene que saber a quién pedirle. Si no hay
        referente (Gestión) o el referente ya no está activo, los pedidos van a Dirección, y **cada pedido le dice por
        qué le llega** ("Gestión no tiene referente: mientras no se designe uno, los pedidos de su gente te llegan a
        vos"), así Dirección se entera de que falta un referente. Nombrar uno es de la J7.
      - **J6-D7. Una subtarea que vence después que su tarea:** la vista previa de Nahuel lo avisa; el referente lo ve en
        el informe antes de decidir; si la aprueba así, es aceptar la demora de la tarea (fecha original más prevista,
        J5-D4); si además pasa la fecha del objetivo, también la aprueba el referente del objetivo (decisión 6).
      Con esto, las decisiones de la J6 están completas.
      **Plan en porciones** (planificador de sólo lectura, 2026-10-15, noche; preguntas en "Para decidir al
      despertar", "J6: lo que las decisiones no alcanzan a fijar"). La propuesta vive en su propia tabla y la
      tarea nace al aprobarla: la base no deja corregir una tarea ya cargada (`bloquear_estado_directo`), y
      una tarea "propuesta" contaría como abierta para unos 20 lugares que mandan recordatorios; un objetivo
      "propuesto" ya cuenta como abierto para la carga, así que tampoco puede ser una fila de `objective`.
      - **J6-0.** ADR 0026, "La propuesta y el pedido" (propuesta): enmienda el 0023 §3 y el punto 9.
      - **J6-1.** Conversaciones de prueba 63 a 70 primero, y reescribir la 53 y la 54.
      - **J6-2 y J6-3.** La base: la propuesta y sus acciones (proponer, corregir, "ya no hace falta") y
        decidirla (aprobar, corregir y aprobar, no, dársela a otro); la carga comparte una sola función con
        `cargar_tarea_web`; "subtareas abiertas" entra en `motivo_no_cierra_tarea`.
      - **J6-4 y J6-5.** El servidor y los avisos (`motor/propuestas.py`, con el molde de `carga.py`, que ya
        agrupa diez minutos y relee al salir), y la web del integrante ("> agregar una subtarea", "Mis
        pedidos").
      - **J6-6.** El bloque "Para decidir" del referente (espera "en qué afecta", J5 S4).
      - **J6-7 y J6-8.** El chat ofrece el lugar correcto; un referente propone un objetivo (J6-D5).
      - **J6-9 a J6-11.** Lo que espera a la J5: la tarea después de su objetivo, la subtarea después de su
        tarea madre, y el pedido junto con "Me falta algo para seguir".
      - **J6-12.** Rondas con la IA real, la prueba en el celular y RDD por commit.
- [ ] **J7 · Las jerarquías y los integrantes desde la web de Dirección.**

**Diseño corto (J2-1, 2026-10-13; la entrada, del usuario).** Arriba del formulario de carga, un recuadro
libre, "Contame qué querés hacer y te ayudo" (escrito o dictado), y el botón "> completar con Leda". Es
opcional: cargar a mano sigue igual. El micrófono aparece sólo si el navegador reconoce la voz
(`SpeechRecognition` o `webkitSpeechRecognition`); sin permiso dice "No tengo permiso para el micrófono;
escribilo acá." y el recuadro sigue. Nada es automático: Leda completa sólo al tocar el botón.
- **El pedido:** `POST /app/admin/api/espacios/{id}/ayuda` (los controles de la carga: otro sitio, JSON,
  tamaño, la sesión de administración), con el texto libre (hasta 1000 caracteres) y lo que ya tiene el
  formulario. Leda propone sólo lo que está vacío; sin texto o sin nada vacío, 422 con su motivo.
- **Tres pasos, para que el candado de la web nunca espere a la IA:** (1) con el candado, la sesión, las
  opciones de ese espacio (`opciones_de_la_carga`, las mismas del formulario) y la IA del espacio
  (`entrada._ia_de`); (2) sin el candado, una sola llamada, sin reintento (la persona puede volver a tocar);
  (3) con el candado, dentro del espacio, la sesión otra vez, los controles y la auditoría.
- **Qué recibe la IA**, sólo de ese espacio: el texto, lo que ya está escrito, hoy y los días que vienen con
  su día de la semana (`hechos.dia`), los objetivos abiertos (O1, O2…), las tareas abiertas para esperar
  (T1, T2…, con su responsable y su objetivo) y, si ya se eligió quién la hace, su área y la evidencia que
  pide. Los nombres de los integrantes no van: la IA devuelve las palabras con que se nombró a la persona.
- **Qué devuelve:** título, descripción (lo contado, ordenado, sin agregar nada), criterio con la parte que
  dice cómo se comprueba copiada tal cual (`como_se_comprueba`), las palabras de quién la hace, el código de
  la espera, el del objetivo y la fecha (AAAA-MM-DD). Las instrucciones describen el trabajo, sin casos.
- **Lo que decide el código** (cada dato que no pasa queda vacío y se dice por qué):
  - **quién la hace**, sólo si sus palabras están en el texto: `fichas.integrantes_que_coinciden` (con los
    apodos) en una transacción del espacio, después de la sesión. Nadie: "No encontré a X en el equipo.";
    dos o más: se muestran para elegir, Leda no elige (ADR 0020, decisión 3). Elegirla marca la evidencia
    del área, como hoy (la evidencia la pone el código, nunca la IA);
  - **la espera**, un código de la lista; **el objetivo**, el de la tarea que espera si la hay y está
    abierto; si no, un código de la lista;
  - **la fecha** (cambiada en la J2-7): la IA copia las palabras con que la persona la dijo
    (`como_dijo_la_fecha`); el código comprueba que están en el texto, calcula él mismo el día con la
    frase entera donde están, y la pone sólo si es el mismo día que dio la IA y es hábil; si no, "No
    puse la fecha: …" con el porqué (constitución §4: nunca una fecha que nadie dijo). "Antes de" un
    día es el día hábil anterior del calendario del espacio, y un rango no es una fecha (J2-8);
  - **título, descripción y criterio:** el tope del formulario (200, 800 y 500); ningún número ni nombre que
    no esté en lo que escribió la persona o en los datos de esta tarea (objetivo, espera, quién la hace y su
    área, la evidencia), con `entrega.problema_del_ejemplo`, el criterio punto por punto
    (`puntos_del_criterio`); y el criterio, con `como_se_comprueba` dentro de él. Si no pasa: "No pude
    proponer el criterio con lo que escribiste; contame cómo se comprueba." (y lo mismo para los otros).
- **Si la IA no responde** (sin configurar, sin sesión, plazo, cupo, respuesta ilegible): 503, en pantalla
  "Leda no pudo completar ahora…", nada cambia y queda un incidente (`ayuda_al_cargar`), sin el error.
- **La auditoría** (`proponer_al_cargar`, en el espacio, quien pidió como actor): qué se pidió, qué se
  propuso y qué no (con su motivo), la IA, la sesión y la huella (sha256) de cada texto propuesto, no el
  texto; con la sesión, que ya guarda la carga, se ve si lo cargado fue lo propuesto. **Sin migración:**
  `leda_app` ya escribe `audit_log` e `incident` dentro de un espacio.
- **En la web:** cada dato propuesto se completa sólo si sigue vacío al llegar la respuesta (nunca pisa lo
  escrito), con la marca "propuesto por Leda" hasta que la persona lo cambia; el texto libre queda en su
  recuadro. La vista previa y "confirmar" no cambian: se carga lo que la persona ve y confirma.

- [x] **Lenguaje (porción 1, lo claro)** (2026-10-15, escritor delegado; prueba primero en cada arreglo). Sólo
  lo que no depende de la palabra que reemplaza a "trabada": esa palabra espera en "Para decidir al
  despertar" y no se tocó nada con "trab" o "bloque" en el motor, los hechos, los significados ni el chat.
  - `74170e5e`: la web dice lo mismo en todas partes. Una tarea asignada se lee «SIN EMPEZAR» en su
    tarjeta (decía «[ASIGNADA]»); en "Lo que pediste", una bloqueada dice «esperando» (decía «trabada») y
    una asignada «sin empezar»; el estado del detalle de una tarea (`tarea_vista.ESTADOS`) dice «esperando».
    El historial de la tarea («Se trabó», «Se destrabó») sigue igual hasta que se decida la palabra.
  - `597c284c`: los textos fijos. La bienvenida dice «Ahora tenés 1 tarea abierta.» o «Ahora tenés 3
    tareas abiertas.» (decía «tarea(s) abierta(s)»); un dato mal formado en la web, «Esto no se pudo leer;
    revisalo.»; el incidente al administrador cuando una cadena no le llega a nadie dice el motivo con
    palabras («todavía no tiene Leda conectada» o «ya no está activo en el equipo»), sin el código.
  - `9cb79d63`: una prueba nueva revisa también los significados (`hechos.SIGNIFICADOS`) y el para qué de
    cada jugada (`Ficha.para_que`) contra los conceptos de la cocina. Encontró cinco y se reescribieron con
    el mismo sentido: «el reencuadre», «un aviso previo», «pedir el estado» (dos) y «lo que escribió»
    (cinco significados de la entrega, que ahora dicen «su descripción»). Quedan anotadas, con su porqué,
    las coincidencias que no nombran un concepto (el estado de una tarea como sustantivo, las preguntas de
    este mensaje y «aprobar» para la decisión misma). Las huellas de las instrucciones no cambiaron, pero
    los significados sí llegan a la IA: **queda pendiente una ronda con la IA real** de las conversaciones
    que usan esos datos.
  - Sin hacer: borrar `NO_EFFECT_STATUS` de `salida.py`. No es código muerto del todo: lo usa
    `with_no_effect_status`, que nada usa en `src/` pero sí prueba `tests/garantias/test_contrato_de_salida.py`.
    Borrarlo es retirar esa prueba de garantías, y eso queda para otra porción.
  - Evidencia (2026-10-15): `npm test` en `web/`, 343 passed; `npm run build`, bien; `pytest -q tests/motor`,
    1492 passed y 1 failed, que ya fallaba antes (`test_frontera.py::test_el_motor_importa_de_leda_solo_lo_permitido`:
    `fichas.py` importa `leda.menu_del_bot`, desde `98c5758f`, MA-5); `pytest` de `test_onboarding`,
    `test_tarea_vista`, `test_pagina_de_la_tarea`, `test_carga_del_equipo` y `test_api_de_la_plataforma`, en
    verde; `correr --ia guionada --veces 1` (en seco), 54 de 54 bien.
- [x] **Lenguaje (porción 2, "trabada")** (2026-10-15, escritor delegado; prueba primero en cada arreglo). La
  decisión del usuario: en lo que ve la persona, qué falta y quién se ocupa, nunca "trabada", "se trabó",
  "destrabar" ni "bloqueo". Los nombres de la cocina (el estado `bloqueada`, las jugadas, los hechos
  guardados) no cambiaron.
  - `8f48c5e2`: lo que lee la IA para redactar. Como con "previsión", en el borde de la redacción
    (`hechos.PARA_LA_REDACCION`): 62 nombres y códigos con "trab" o "bloque" tienen el suyo (por ejemplo
    `si_esta_trabada` → `si_le_falta_algo_para_seguir`, `bloqueada` → `esperando_algo_para_seguir`,
    `quien_destraba` → `quien_se_ocupa_de_lo_que_falta`, `se_destrabo` → `dijo_que_ya_puede_seguir`), y los de
    seis jugadas que todavía lo decían; se reescribieron 106 significados y el para qué de ocho jugadas, con el
    mismo sentido. La prueba de las palabras de la redacción suma "trabad", "trabo", "destrab", "bloqueo" y
    "bloquead" a los conceptos de la cocina y revisa nombres, valores, significados y para qué ("trabajo" queda
    afuera). Los avisos de incidente al administrador lo dicen igual.
  - `25fa8835`: los textos fijos. La bienvenida dice «para ver cómo venís y si te falta algo para seguir»; el
    historial de la tarea, «Quedó esperando: el cable (lo dijo Marcos). Ya pudo seguir el …» (decía «Se trabó»
    y «Se destrabó»); el tablero, «Esperando algo para seguir» y «Ninguna tarea está esperando algo para
    seguir.»; los errores de la espera en la web, «otra no puede quedar esperándola» (decía «no puede trabar a
    otra»).
  - `b12eb445`: el resto del historial de la tarea (con la superficie ampliada por el coordinador a
    `tests/garantias/test_pagina_web_de_la_tarea.py`): «dijo que no sabe quién se ocupa de lo que falta», «dijo
    que no hay otra persona que se ocupe», «dijo que de eso se ocupa Mariano», «dijo que lo consigue el vie
    23/10», «Quedó asentado que sigue esperando: 5 días hábiles» y «Quedó asentado que nadie se ocupa de lo que
    le falta» (decían «quién la destraba», «que la destrabe», «la destraba», «sigue trabada» y «nadie toma el
    bloqueo»). En `tarea_vista.py` sólo quedan nombres internos y comentarios.
  - **Sin tocar, a propósito:** lo que lee la IA para elegir jugadas (`Ficha.es`, `ia_real.DATOS`,
    `INSTRUCCIONES_JUGADAS`), que no se le escribe a la persona; `herramientas.py` (las vistas previas de las
    herramientas, como «Registré el bloqueo…», que el motor no muestra) y `cli.py` («Bloqueos abiertos», para
    quien opera), fuera de esta porción; y el texto de resolución que guarda `destrabar` cuando la persona no
    escribió nada («la causa del bloqueo ya no está», `fichas.py`), que nada muestra hoy.
  - Evidencia (2026-10-15): `LEDA_BASE_URL= pytest -q tests/motor tests/test_onboarding.py
    tests/test_tarea_vista.py tests/garantias/test_tablero.py`, 1537 passed y 2 failed, las dos de
    `test_avisos_sin_nombre_ni_hora.py` que esperaban los nombres viejos y se corrigieron en el mismo commit (12
    passed al repetirlas); sin `LEDA_BASE_URL=` vacío fallan 15 de la cadena por el ofrecimiento de la web, del
    entorno y no del cambio. `npm test` en `web/`, 343 passed. `correr --ia guionada --veces 1` (en seco), 54
    de 54 bien. Con `b12eb445`: `pytest -q tests/garantias/test_pagina_web_de_la_tarea.py
    tests/test_tarea_vista.py tests/motor/test_palabras_de_la_redaccion.py`, 52 passed. **La ronda con la IA real** (coordinador, 2026-10-15, de mañana; 55, 32 a 35, 40 y 42, `--veces 3`, informe
    `2026-10-15-0845`): garantías 19 de 21, todo lo automático 10 de 21; "trabada" en la 55, de 25 renglones a 0; en
    las siete, de 77 a 3, y los 3 repiten la palabra de la persona. Ninguna falla sale del cambio (detalle en la
    bitácora). RDD de `8f48c5e2`, `25fa8835` y `b12eb445`: aprobados, sólo sugerencias (textos de incidentes y de
    esperas sin una prueba que los mire).
- [x] **Grafo de transiciones (parte 1, lo que dice la mecánica)** (2026-10-15, escritor delegado; prueba
  primero). Sólo lo que la mecánica §3 dice explícitamente; lo demás espera las preguntas de "Para decidir al
  despertar" (quién cancela, reabrir, deshacer el empecé, los objetivos) y no se restringió nada de eso.
  - `36c6120a`: la migración `0079_el_grafo_de_transiciones` (con su rollback y la misma parte en
    `esquema.sql`) agrega dos disparadores `before insert`, `security definer` de `leda_owner`, sobre
    `task_state_event` y `objective_state_event`: el evento sale del estado vigente (la fila tomada
    `for update`; sin estado de partida, sólo el que la crea y si todavía no tiene ninguno), de `cancelada` y de
    `cancelado` no se sale, y de `bloqueada` se vuelve al estado previo (`estado_previo_a_bloqueo`) o se
    cancela. El error es `transicion_invalida: …`; una tarea de otro espacio sigue fallando antes, igual que un
    id inventado. Nada en `src/` anotaba un estado de partida viejo.
  - Pruebas: `tests/garantias/test_grafo_de_estados.py` (13; rojo antes de la `0079`: 9 fallaban, 4 caminos
    válidos pasaban). Dos pruebas viejas se reescribieron por pasos válidos: `test_cierre_con_aprobacion.py`
    creaba la tarea sin su evento de alta, y `test_bloqueos.py` sacaba una tarea de `bloqueada` a `en_curso`
    sin haber arrancado (ahora vuelve a `asignada`, su estado previo). `db/pruebas.sql`: un `insert` de tres
    eventos pasó a tres sentencias (la proyección se aplica al final de cada una).
  - Evidencia (2026-10-15): `pytest -q tests/garantias/test_grafo_de_estados.py`, 13 passed; `pytest -q tests/garantias`, 1131
    passed, 1 failed y 5 errores, todos por la regla nueva (`test_cierre_con_aprobacion.py`, reescrita: 5 passed)
    o arrastrados por ellos (`test_frontera.py`, que corre las garantías en otro proceso: repetida, 4 passed);
    `pytest -q tests/motor`, 1493 passed; `pytest -q tests/conversaciones`, 231 passed; el resto de
    `tests/*.py`, 824 passed y 1 failed (`test_bloqueos.py`, reescrita: 14 passed); `correr --ia guionada
    --veces 1` (en seco), 54 de 54 bien. `db/pruebas.sql` no se corrió. Revisión RDD: pendiente.
      RDD aprobada por commit: T8 (`81bd7f0d`), `review-9d14e51631b3b100` (advertencia: el rollback de la 0078 sobre
      una instalación limpia le sacaría privilegios que ésta espera; los rollbacks se usan sobre bases migradas);
      el grafo (`36c6120a`), `review-32c808e9334f970d`, con una **advertencia que se arregla**: varios eventos de la
      misma tarea en una sola sentencia se comparan todos contra el estado de antes de la sentencia, así que dos
      saltos desde el mismo estado pasarían (por ejemplo, cancelar y seguir en la misma sentencia). Arreglo:
      comparar contra el último evento de la tarea, que dentro de la misma sentencia sí se ve.
      **Arreglada** (2026-10-15, escritor delegado; prueba primero), `b81b89ff`: la migración
      `0080_el_grafo_en_una_sola_sentencia` (con su rollback y `esquema.sql`) le da a cada evento de tarea y de
      objetivo su número en la historia (`numero`, único por tarea y por objetivo; lo pone el disparador con la
      fila tomada `for update`, aunque quien inserta mande otro) y compara contra el último evento numerado, que
      dentro de la misma sentencia sí se ve; sin eventos numerados, contra el estado de la fila. No se ordena por
      `at`: el de los objetivos es `now()`, igual en toda la transacción. `estado_previo_a_bloqueo` ordena por el
      número antes que por la hora. Una cadena válida en una sola sentencia pasa (empezar y entregar juntos).
      Pruebas: 6 nuevas en `test_grafo_de_estados.py` (rojo antes de la `0080`: 5 fallaban; la de salir de
      `cancelada` en la segunda fila ya se rechazaba). Evidencia (2026-10-15): `pytest -q
      tests/garantias/test_grafo_de_estados.py tests/garantias/test_migraciones.py`, 35 passed; `pytest -q
      tests/garantias`, 1143 passed; `pytest -q tests/motor`, 1502 passed. RDD aprobada,
      `review-59287add32800be2`; advertencias sin arreglar (son el segundo arreglo seguido del mismo mecanismo:
      se para y se mira con el usuario, AGENTS.md punto 4): el control confía en el último evento numerado antes
      que en el estado de la fila, y el camino de los eventos viejos sin número no tiene prueba propia.
      `leda_motor` llevada hasta la `0080` el 2026-10-15 (respaldo
      `db/respaldos/leda_motor-antes-0077-a-0080-20261015.dump`, `pg_restore --list` bien; las cuatro ensayadas
      en una copia descartable, que se borró; aplicadas con `psql -v ON_ERROR_STOP=1 -f` como `postgres`).
- [x] **Candado de la sesión de ChatGPT** (2026-10-15, escritor delegado; prueba primero; deuda de
  `docs/STATUS.md`). La escucha y una ronda del corredor podían renovar la sesión a la vez y romperla.
  - `5ad5fd2e`: `src/leda/motor/chatgpt.py` renueva con un candado del sistema (`msvcrt` en Windows, `flock`
    en los demás) sobre `chatgpt.json.lock`, al lado de la sesión; ya con el candado vuelve a leer el archivo
    y, si otro ya renovó, usa eso sin renovar. Si un proceso muere con el candado, el sistema lo suelta solo.
    Espera hasta 45 s (el plazo del emisor y un margen) y después falla a la vista con
    `SesionChatGPTOcupada`, un `SesionChatGPTVencida` (incidente y texto fijo, como las demás fallas de la
    sesión). La sesión se guarda entera o nada, con un temporal propio por escritura que se borra si algo
    falla; el ingreso (`login`) también toma el candado antes de guardar.
  - Pruebas: `tests/motor/test_chatgpt_candado.py` (9; rojo antes del cambio: 7 fallaban): dos sesiones a la
    vez piden una sola renovación y quedan con el mismo token; otro proceso con el candado hace fallar a la
    vista al vencer la espera; el candado de un proceso muerto no traba; una escritura que falla deja la sesión
    anterior entera y sin temporales.
  - Evidencia (2026-10-15): `pytest -q tests/motor -k chatgpt`, 70 passed; `pytest -q tests/motor`, 1502
    passed. Revisión RDD: pendiente.
      RDD aprobada, `review-48b161fe6bc6f276` (advertencias: el reintento de `os.replace` en Windows no tiene
      prueba propia, y una prueba lee de un subproceso sin tiempo límite). Con la sesión real, las conversaciones 01
      y 02 una vez (2026-10-15, 03:59): garantías 2 de 2; la 02 falla sólo el formato, una clase conocida.

## De qué se parte en cada porción (explorador de sólo lectura, 2026-10-13)

Pedido del usuario: "revisá si ya no tenemos algo creado que pueda servir de base para no arrancar de cero".

- **J3, los objetivos:** `herramientas._preparar_crear_objetivo` y `_crear_objetivo` (las comprobaciones, la
  vista previa y el evento de estado), la convención de tipos de la importación (`importador._importar_objetivo_inicial`:
  la raíz estratégica, cada frente operativo), la tabla `objective` (ya tiene `referente_membership_id`, sin
  usar), `opciones_de_la_carga` (ya trae los objetivos y los integrantes para elegir) y `cargar_tarea` como
  patrón de función de la base (sesión, clave de un solo uso, errores y avisos, auditoría); en la web,
  `FieldBlock`, `Counter`, `DatePicker` y la vista previa. Falta: la regla de qué tipo cuelga de cuál, una
  función `crear_objetivo` para la web, poner el referente y que sólo Dirección cree.
- **J4, la carga del equipo:** `cargar_tarea` entera (sólo cambia la puerta: la sesión del equipo en vez de la
  de administración), `tareas_que_ve` y `vistas_de` (ya distinguen Dirección y referentes), la regla de quién
  revisa (`quien_revisa_la_tarea`) y el pase de tareas del motor (`motor/pase.py`, `autoridad.regla_del_pase`)
  como antecedente de "una tarea para otra persona". Falta: guardar quién revisa una tarea en particular (el
  préstamo), la versión de `cargar_tarea` para la puerta del equipo y **los avisos de la decisión 7 del
  ADR 0022** (al responsable y a quien revisa), que quedaron pendientes en la porción 2
  (`plataforma-p2.md`): se construyen en la J4, junto con el aviso del préstamo.
- **J5, más tiempo y cambio de fecha:** la previsión del chat (`task_forecast`, la jugada `anotar_prevision`,
  los avisos `nueva_prevision`), `ancla.prevision_vigente`, la previsión que ya muestra la web, y el umbral
  de re-aprobación del pack (`corrimiento_de_fecha_dias: 3`), que se guarda y nadie lee. Falta: **la base no
  deja cambiar la fecha de una tarea** (`bloquear_estado_directo`), así que hace falta una función propia,
  auditada y con quién lo decidió; el pedido con su estado (pendiente, aceptado o rechazado); el bloque del
  referente en la web.
- **J7, las jerarquías y los integrantes:** las validaciones de la importación (`importador.validar`: una sola
  autoridad final, áreas y roles existentes, quién aprueba a quién sin ciclos ni a sí mismo), la importación
  de personas y áreas, los enlaces de activación (`onboarding.generar_enlaces`, `activar`,
  `pendientes_de_activar`), "conectado" que ya trae `opciones_de_la_carga`, el corte de sesiones con
  `dejo_el_equipo` al dar de baja, y las ideas rescatadas de la rama auxiliar (`plataforma-p2.md`). Falta: las
  funciones de la base para altas, bajas y cambios de área, rol, referente y quién aprueba, y las preferencias
  de avisos de Dirección.
- **La etiqueta congelada** sólo aporta el mismo `crear_objetivo` de hoy; nada de más tiempo ni de integrantes.

## Para decidir al despertar

**Sesión autónoma que sigue al 2026-10-15** (el usuario se fue a dormir y pidió trabajar solo, con la IA real
autorizada): el agente agrega acá, debajo de esta línea, cada pregunta que dependa del usuario (MA-7 a J7), con
ejemplo y recomendación, y sigue con otra cosa.

- **Quién pidió una tarea propia, en "Mis tareas"** (deuda de la MA, `cc286185`): **se hizo así y se puede
  cambiar.** Ejemplo: en "Mis tareas" de Ismael, la tarjeta "Aprobar la compra del módem" dice debajo del
  título "└─ te la pidió Marcos Tarquini", chico y gris, como el "└─ de Ariel · te espera". Sólo en sus propias
  tareas, sólo si la pidió otra persona, y con el nombre entero. *Recomendación:* dejarlo así; si se prefiere
  el nombre corto ("te la pidió Marcos") o que diga también el área, es un cambio chico.
- **Lenguaje: qué palabra reemplaza a "trabada" y "bloqueada"** — **DECIDIDO (usuario, 2026-10-15, "si"):
  la recomendación. En lo que ve la persona, decir qué falta y quién se ocupa («¿te falta algo para seguir?»,
  «está esperando el cable, que consigue Mariano», «ya puede seguir»); los nombres internos no cambian.
  En curso: tarea "Lenguaje (porción 2)".** (Tarea "Lenguaje"; un explorador midió las
  rondas del 14/10). Leda dijo "trabada" 25 veces, todas en "cómo vienen tus tareas" (conversación 55): «Contame
  si la empezaste, para cuándo la terminás o si está trabada.» Sale de un código interno que la IA copia tal
  cual (`si_esta_trabada`), igual que pasó con "previsión"; hay 64 nombres de datos más con "trab" o "bloque"
  que le llegan a la IA, y lo mismo dicen la bienvenida («si algo te está trabando»), el historial de la tarea
  en la web («Se trabó: …», «Se destrabó el …») y el tablero («Bloqueos abiertos»). Lo que ya decidiste (J5-D1,
  14/10): "trabado" no deja claro que depende de otra cosa; la web dice «Esperando el cable (Mariano)» y el
  botón es «> Me falta algo para seguir». Falta la forma en el chat. *Recomendación:* la misma idea que la web,
  decir qué falta y quién se ocupa: «¿te falta algo para seguir?», «está esperando el cable, que consigue
  Mariano», «ya puede seguir». Se descartó "frenada" (era la primera idea del agente): tampoco dice que
  depende de otro. Con la respuesta, se renombran los datos en el borde de la redacción (como "previsión"), se
  reescriben sus explicaciones, una prueba impide que vuelvan, y una ronda con la IA real
  lo comprueba. Mientras tanto se arregla sólo lo que no depende de la palabra.
- **El mensaje cuando la IA falla** — **DECIDIDO (usuario, 2026-10-15):** que Leda avise que contesta sola cuando
  vuelva ("así la persona no tiene que andar probando cada rato"): «Ahora no puedo contestarte; ya avisé para que
  lo revisen. En cuanto vuelva, te respondo yo, no hace falta que me escribas de nuevo.» Como hoy no se reintenta
  después del turno, hace falta construirlo antes de decirlo (tarea "La respuesta que quedó pendiente"); hasta
  entonces sigue el mensaje de hoy. (Tarea "Lenguaje"). Hoy, si la IA no responde, la persona recibe: «Tuve un
  problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.» Suena frío
  y técnico. *Recomendación:* «Uy, no pude contestarte ahora. Ya avisé para que lo revisen; probá de nuevo en un
  rato.» (la constitución §10 pide un mensaje humano y genérico, y lo cumple). Alternativa: lo mismo sin "probá
  de nuevo".
- **«Mi espacio» cuando Telegram no fijó el botón del menú** — **DECIDIDO (usuario, 2026-10-15): la
  recomendación** (el botón debajo del mensaje sólo en ese caso). (Advertencia de RDD de la MA-5). Ante "quiero ver
  mis tareas", Leda contesta que toque «Mi espacio», el botón fijo del menú, sin botón en el mensaje (tu
  decisión del 14/10). Si al arrancar Telegram no aceptó fijar ese botón (queda un incidente), Leda igual lo
  nombra y la persona no lo encuentra. *Recomendación:* cuando el botón del menú no se pudo fijar, Leda manda
  el botón «Mi espacio» debajo del mensaje, como excepción. Es raro (pasa sólo si falla Telegram o falta la
  dirección pública), por eso no se construyó sin preguntarte.
- **Cuánto dura la sesión de administración en la compu** — **DECIDIDO (usuario, 2026-10-15): 12 horas sin
  uso por omisión, configurable desde la plataforma de administración** (inventario en
  `docs/product/plataforma-pendientes.md`). (Deuda de la MA). Hoy no vence nunca: quien entró a
  la administración desde una compu sigue adentro hasta que toca «Cerrar sesión». La del equipo dura lo que
  elige el administrador para cada equipo. *Recomendación:* que la de administración venza sola a las 12 horas
  sin uso, porque desde ahí se cargan tareas y objetivos de cualquier espacio. Ejemplo: Ariel entra a la
  administración a la mañana, se olvida la compu abierta y a la noche ya pide el QR de nuevo.
- **Grafo de transiciones de estado** — **CONTESTADO (usuario, 2026-10-15):** 1. cancelar, sólo quien la
  pidió (o su referente) y Dirección, con motivo obligatorio, desde cualquier estado menos "terminada"; si el
  responsable cree que no tiene sentido, Leda se lo plantea a quien decide; 2. reabrir una terminada, sí, las
  mismas personas, con motivo y aviso al responsable; 3. **deshacer "la empecé", siempre y sin límite de tiempo**
  (usuario: "si dice que no la empezó, no la empezó. Es la realidad"; el margen de 10 minutos que recomendaba el
  agente era burocrático); 4. los estados de los objetivos, cuando se construya cerrar un objetivo (`ROADMAP.md`).
  Lo de abajo es la pregunta tal como se hizo. (Tarea agregada el 15/10; un explorador mapeó el código). Hoy nada
  impide que una tarea pase de cualquier estado a cualquier otro por la herramienta `actualizar_estado`
  (aunque la conversación sólo la usa para "empecé" y para deshacerlo). Esta noche se construye sólo lo que la
  mecánica §3 ya dice: el estado de partida anotado tiene que ser el real, de "cancelada" no se sale, y al
  destrabar se vuelve al estado anterior. Para el resto, de a una:
  1. **¿Quién puede cancelar una tarea, desde qué estados, y con motivo obligatorio?** Hoy lo puede hacer el
     responsable, desde cualquier estado y sin motivo (sólo por la herramienta; nadie lo usa en el chat). La
     mecánica pide "razón y autoridad". *Recomendación:* sólo quien la pidió o Dirección, con motivo
     obligatorio, desde cualquier estado salvo "terminada".
  2. **¿Reabrir una tarea terminada sigue permitido?** Hoy quien la pidió puede reabrirla (vuelve a
     "asignada"). *Recomendación:* sí, y queda declarado en el grafo.
  3. **¿Se mantiene "deshacer el empecé"** (de "en curso" a "asignada", cuando la persona se corrige)? La
     mecánica no lo prevé. *Recomendación:* sí, sólo como corrección dentro del margen para corregir.
  4. **Los estados de los objetivos** (suspender, cancelar, "completo, falta la aprobación"): hoy ningún código
     los mueve después de crearlos. *Recomendación:* dejarlos para cuando se construya cerrar un objetivo, y por
     ahora sólo impedir saltos inválidos.

- **J7 · las jerarquías y los integrantes desde la web de Dirección** — **CONTESTADO (usuario, 2026-10-15, de mañana):**
  1. manda la web; el archivo del espacio es sólo plantilla para arrancar con la web en cero y respaldo exportable
  (`ROADMAP.md`, `1d7efb4b`); 2. entra todo lo del equipo (altas, bajas, área, rol, referentes, quién aprueba,
  áreas, los avisos informativos que elige cada persona, pasar la autoridad final); ausencias y suplente de
  Dirección, en la porción siguiente; 3 y 4. «> nombrar referente» es un paso (decisión 33) cuya vista previa
  muestra todo lo que arrastra y **pregunta qué pasa con el anterior** (usuario: "es raro que de referente pase
  a ser integrante"): se va (camino de la baja), pasa a otro sector, o queda como integrante; lo que lo
  esperaba pasa al nuevo con un solo aviso; las tareas con él como revisor a mano pasan al nuevo (sin opción si
  se va; por omisión, destildables, si se queda); 5. la baja reparte cada tarea abierta (o "que lo decida el
  referente"), no borra, corta sesiones, y la autoridad final se pasa antes; 6. alta con nombre, área y rol,
  aprobador = referente del área, «> copiar el enlace de activación», "sin conectar" hasta abrirlo; 7. al
  cambiar de área, cada tarea abierta por omisión la termina él y la revisa el referente del área de la tarea, o
  pasa a otro de esa área; 8. un área no se borra con gente ni con tareas abiertas; renombrar cambia sólo el
  nombre; 9. aviso corto a cada afectado, historial "Cambios del equipo" para Dirección, auditoría; **al
  administrador de la plataforma no le llega nada de la organización interna** (usuario: "se ocupa de la parte
  técnica, no de los grupos de trabajo"; el administrador del equipo es Dirección); 10. ya estaba en el ADR
  0023, decisión 5. Lo de abajo es la pregunta tal como se hizo. (preguntas preparadas el 2026-10-15 a la
  noche; nada construido). Hoy no hay ninguna función, comando ni pantalla para dar de alta o de baja a alguien,
  ni para cambiar su área, su rol o quién lo aprueba: todo sale del pack (`espacios/corework.yaml`). Las
  preguntas van de la que más frena a la que menos; se contestan de a una.
  1. **¿Quién manda después de la J7, el pack o la web?** Ejemplo: Ismael nombra en la web a Nahuel referente
     de OT. Si después alguien vuelve a importar el pack, Marcos vuelve a ser referente sin que nadie se entere
     (el importador pisa área, rol, aprobador y referentes). *Recomendación:* la base manda; el pack sólo arma
     el equipo la primera vez. Al reimportar, la parte de personas y jerarquía no se aplica sola: se muestran
     las diferencias y las aplica el administrador.
  2. **Qué entra en la J7.** Altas y bajas, cambiar de área, de rol, nombrar referente, elegir quién aprueba a
     quién, crear, renombrar y borrar áreas, cómo quiere enterarse Dirección de los avisos y pasar la autoridad
     final (punto 10 del ADR 0023). *Recomendación:* todo eso, con tres opciones de avisos para Dirección (en el
     momento, juntos en el resumen semanal, ninguno). Las ausencias y el suplente de Dirección, en una porción
     posterior.
  3. **Nombrar referente, ¿arrastra lo demás?** Ejemplo: OT pasa de Marcos a Nahuel. *Recomendación:* una sola
     acción, "nombrar referente", cuya vista previa propone los cambios que siguen (Nahuel pasa a referente y
     lo aprueba Dirección; los de OT pasan a ser aprobados por Nahuel; el aviso de un problema técnico de OT
     va a Nahuel; Marcos queda como integrante de OT) y se confirman juntos. Cambiar quién aprueba a una persona
     sola sigue disponible aparte.
  4. **Lo que estaba esperando al que deja de revisar.** Ejemplo: Marcos tenía dos entregas de Nahuel por
     revisar cuando deja de ser referente. *Recomendación:* pasan al nuevo, que recibe un solo aviso con lo que
     hereda; las tareas que se cargaron con un revisor elegido a mano lo conservan mientras siga activo. Nada
     se aprueba solo.
  5. **Dar de baja a alguien con tareas abiertas.** Ejemplo: Lucas se va con tres tareas en curso.
     *Recomendación:* la vista previa lista sus tareas y Dirección elige un responsable para cada una (o "lo
     decide Martín"): esa confirmación es la aprobación que pide la mecánica (§8). No se puede dar de baja a
     quien aprueba a otros sin nombrar reemplazo, ni a Ismael (la autoridad final se pasa con el punto 10). La
     baja no borra: deja a la persona inactiva y corta sus sesiones.
  6. **Dar de alta a alguien.** *Recomendación:* nombre, área y rol; quién lo aprueba, el referente del área
     por omisión. La web muestra "copiar el enlace de activación" para mandarlo por donde se hablen, y la
     persona figura "sin conectar" hasta que lo abre.
  7. **Cambiar a alguien de área.** Ejemplo: Lucas pasa de IT a OT. *Recomendación:* cada tarea conserva su
     área; la vista previa avisa que sus tareas de IT las revisaría Marcos y ofrece dejar a Martín como revisor
     de esas.
  8. **Crear y borrar áreas.** *Recomendación:* un área nueva lleva referente o dice explícitamente que se
     autoaprueba (mecánica §7); se borra sólo sin personas ni tareas abiertas; renombrar cambia sólo el nombre
     que se ve.
  9. **Quién se entera de cada cambio.** *Recomendación:* queda en la auditoría con el antes y el después;
     Dirección ve un historial "cambios del equipo"; cada persona afectada recibe un aviso corto ("Desde hoy tu
     trabajo lo revisa Martín"); el administrador, sólo el paso de la autoridad final y las bajas.
  10. **¿Reorganizar el equipo es ampliar la autoridad de Leda (constitución §2, dos firmas)?**
      *Recomendación:* no: cambia la autoridad del equipo, no lo que Leda puede hacer, así que alcanza con la
      confirmación de Dirección. Las excepciones: la autoridad final (la acepta quien la recibe) y que Dirección
      cambie su propio rol, que no se puede.
- **Tres hallazgos de la ronda del 15/10** — **DECIDIDO (usuario, 2026-10-15): las recomendaciones del 1
  y del 3** ("perdí el celular" dicho al pasar pregunta antes de cortar; el nombre se separa del área dicha al
  lado, como regla general, y si el área no coincide, pregunta). El 2 no necesita decisión: va con la regla de
  las preguntas. Primero, sus conversaciones de prueba. (Todas las conversaciones, una vez; repetidas 3 veces: el 1 y el 3 fallan siempre, el 2 una de tres).** Ninguno viene de los cambios de
  la noche; se anotan como conversación de prueba antes de tocar nada (regla general, no parche).
  1. **"Perdí el celular" dicho al pasar corta el acceso a la web.** En la conversación 42, Ariel escribe
     "perdon perdi el celular, …" en medio de otro tema y Leda le corta el acceso a la web (lo que decidiste
     para "perdí el celular": cortar enseguida, sin confirmar). *Recomendación:* que siga cortando sin
     confirmar, pero sólo cuando es lo que la persona está pidiendo; dicho al pasar ("perdón, perdí el celular
     y no vi tu mensaje"), Leda pregunta "¿querés que corte el acceso desde ese celular?".
  2. **Elegir una opción en una pregunta que no tiene opciones** (conversación 43: "se lo pido yo y te
     cuento"). La cocina lo rechaza y Leda vuelve a preguntar; el seguimiento que tocaba no sale. Se mira
     junto con la regla de las preguntas; sin decisión tuya por ahora.
  3. **"martin de IT" no se reconoce como Martín Forte** (conversación 05): Leda pregunta "¿quién es martin de
     IT?". *Recomendación:* que el reconocimiento de nombres ignore el área dicha al lado ("de IT", "el de
     OT"), y si el área no coincide, que pregunte.
- **J5: lo que las decisiones no alcanzan a fijar** — **CONTESTADO (usuario, 2026-10-15, de mañana):** las
  respuestas están en el [ADR 0025](../../docs/decisions/0025-mas-tiempo-y-cambio-de-fecha.md), puntos 12 a 23, y el
  ADR quedó aceptado (`d5ddedd6`). Cambiaron respecto de las recomendaciones el 2 ("¿cómo venís?" sin botones;
  los recordatorios desde el vencimiento con «> Ya la terminé» primero), el 3 (la tarea que espera conserva su
  ventana de días hábiles), el 4 (al aceptar, la cadena se corre sola como prevista) y el 5 (el informe muestra
  también la descripción). El 10: cambiar directo la fecha de un objetivo, a `ROADMAP.md` (`35d9a8cb`). Lo de
  abajo es la pregunta tal como se hizo. (un planificador armó la J5 en porciones el 15/10 a la
  noche). Ojo, un cambio grande: hoy, si Nahuel dice "lo termino el 28", Leda lo anota enseguida y los
  recordatorios pasan al 28 (la conversación 02 lo prueba). Con la J5-D3 eso deja de ser así: queda como pedido
  para Marcos y sigue valiendo el 21. Esta noche se construye sólo la base que no depende de estas preguntas (el
  cambio de fecha auditado en la base) y se escribe el ADR 0025 como propuesta. De a una:
  1. **Una fecha anterior a la que tenía** ("lo termino el 18", vence el 21). *Recomendación:* se anota
     directo, como hoy, sin que nadie decida: no atrasa a nadie.
  2. **Qué mensajes llevan los dos botones** ("> Me falta algo para seguir" y "> pedir más tiempo").
     *Recomendación:* el pedido de cómo viene y los recordatorios desde el día del vencimiento; nunca el aviso
     del día anterior, que no pide respuesta.
  3. **Cuándo una tarea que espera "llega justo" y cuándo "se atrasa".** *Recomendación:* la que espera puede
     empezar el día hábil siguiente a la fecha nueva; si eso cae después de su vencimiento, se atrasa; si no,
     llega justo. El informe dice un nivel con fechas y nombra los de más abajo sin fechas.
  4. **Al aceptar más tiempo, ¿se corren solas las fechas de las tareas que esperan?** Ejemplo: aceptan el 28 y
     «Pasar los cables» de Lucas vencía el 24. *Recomendación:* no se corren solas: se avisa y cada referente
     decide (es el mismo pedido o un cambio de fecha suyo).
  5. **El informe nombra una tarea que quien decide no puede ver** (de otra área). *Recomendación:* que vea sólo
     el título, el responsable y las fechas, como excepción escrita en el ADR.
  6. **Quien decide la tarea y el referente del objetivo son personas distintas.** Ejemplo: Lucas pide el 30,
     decide Martín, pero eso pasa la fecha del objetivo de Ismael. *Recomendación:* primero decide Martín y
     después aprueba Ismael; si es la misma persona, es una sola decisión.
  7. **Los recordatorios mientras el pedido espera.** *Recomendación:* a Lucas le siguen llegando sobre la
     fecha original y le dicen que su pedido sigue esperando; el escalamiento por esa tarea se reemplaza por el
     recordatorio a quien tiene que decidir.
  8. **El freno de un objetivo que ya tiene fecha prevista:** ¿se compara con la original o con la prevista?
     *Recomendación:* con la prevista, que es la que se sigue.
  9. **"> ya no hace falta" para retirar un pedido que espera** (lo pide la J6-D4 para las propuestas).
     *Recomendación:* sí, también acá.
  10. **Cambiar la fecha desde la administración, y cambiar la fecha de un objetivo directamente.**
      *Recomendación:* desde la administración sí, como la carga; la fecha de un objetivo, más adelante.
  11. **"Una tarea que espera algo de otro y se demora"** (J5-D3c). *Recomendación:* cuando quien se ocupa da un
      día que pasa el vencimiento de la tarea que espera, el referente de esa tarea recibe el informe, como
      información.
  12. **Cada cuánto se le recuerda a quien decide.** Hoy una pregunta sin contestar se repite cada día los
      primeros tres y después día por medio. *Recomendación:* cada día hábil, como dice la J5-D7.
- **J6: lo que las decisiones no alcanzan a fijar** — **CONTESTADO (usuario, 2026-10-15, de mañana):**
  1. la subtarea la aprueba el revisor elegido a mano; 2. un referente o Dirección agrega una subtarea a una
  tarea suya directo, sin propuesta (la regla de la J2: "con subtareas se cumple lo mismo"); 3. a otra área
  nunca se asigna directo: es un pedido a su referente, que elige a quién (la J4, "ya lo habíamos resuelto");
  4. si la tarea madre se cierra, la propuesta se retira sola, sin mensaje; 5. una corrección antes de decidir
  no manda otro aviso (la J6-D4, "ya lo habíamos resuelto"); 6. el referente de un objetivo propuesto es quien
  lo propuso, y Dirección lo puede cambiar al aprobar; 7. sale de la J6-D5 y la J6-D7 (no existe para quien
  la va a hacer hasta que se aprueba; quien la cargó la ve "esperando a Ismael"); 8. la administración ve las
  propuestas y no las decide; 9. un recordatorio por día hábil (como la J5). Lección para el agente: varias de
  estas preguntas ya estaban decididas; antes de preguntar, cruzarlas con las decisiones J2 a J6. Lo de abajo
  es la pregunta tal como se hizo. (un planificador armó la J6 en porciones el 15/10 a la
  noche; plan en la J6). La propuesta vive en una tabla propia y la tarea nace recién al aprobarla (la base no
  deja corregir una tarea ya cargada, y una tarea "propuesta" recibiría recordatorios). De a una:
  1. **Quién decide una subtarea de una tarea con revisor elegido a mano.** Ejemplo: Ismael le carga una tarea
     a Nahuel y pone de revisor a Martín; Nahuel propone una subtarea. *Recomendación:* quien revisa la tarea
     madre (Martín), para que proponer, entregar y aprobar pasen por la misma persona.
  2. **Un referente o Dirección agrega una subtarea a una tarea propia.** Ejemplo: Marcos agrega "Pedir el
     plano" a "Revisar el tablero". *Recomendación:* entra directo, con el mismo formulario, sin propuesta.
  3. **"Dársela a otro" fuera del área del referente.** Ejemplo: Marcos quiere que la haga Lucas (IT).
     *Recomendación:* sólo a gente de su área; si no, pasa a ser un pedido a la otra área (como en la J4).
  4. **La tarea madre se cierra mientras una propuesta espera.** Ejemplo: Marcos aprueba "Colocar el estante"
     con "Comprar los tornillos" sin decidir. *Recomendación:* la propuesta pasa a "ya no hace falta: la tarea
     se cerró", sin mensaje.
  5. **Una corrección después de que el aviso ya salió.** Ejemplo: a las 10:10 le llegó a Marcos "12
     tornillos" y a las 10:30 Nahuel lo cambia a 16. *Recomendación:* no sale otro mensaje; la web y el próximo
     recordatorio muestran la versión de ahora.
  6. **El referente de un objetivo propuesto.** Ejemplo: Martín propone "Migrar el correo". *Recomendación:*
     Martín, y Ismael lo puede cambiar al corregir.
  7. **Una tarea que vence después de su objetivo, mientras espera la aprobación.** Ejemplo: Marcos se la carga
     a Nahuel y la tiene que aprobar Ismael. *Recomendación:* Nahuel no la ve hasta que se apruebe; Marcos la
     ve en "Mis pedidos" como "esperando a Ismael".
  8. **La administración y las propuestas.** *Recomendación:* las ve pero no las decide: decidir es del equipo.
  9. **Cada cuánto se le recuerda a quien decide** (la misma que la pregunta 12 de la J5). *Recomendación:* cada
     día hábil.
  Decidido por el agente, por ser técnico (se puede cambiar): los pedidos de más tiempo de la J5 y las
  propuestas de la J6 comparten una sola tabla, con su clase, para que los recordatorios, "ya no hace falta" y
  "uno nuevo reemplaza al pendiente" vivan en un solo lugar.

Lo que el agente, trabajando solo desde la noche del 2026-10-13, necesita que decida el usuario. Cada punto,
con un ejemplo y lo que el agente recomienda; mientras tanto, el agente sigue con lo que no depende de eso.

- **Decididas por el usuario (2026-10-14, a la mañana):**
  1. **El objetivo lleva fecha, obligatoria,** con el mismo calendario que las tareas (sólo días hábiles del
     espacio).
  2. **Nace activo:** "ok".
  3. **El referente es siempre un referente activo de un área,** no cualquier integrante.
  Se construyen en la J3-2b (migración nueva, porque la `0068` ya está aplicada en `leda_motor`).
  4. **Dirección también puede ser referente de un objetivo** (Ismael es el referente del área Dirección):
     queda como está.
  5. **Un objetivo que vence después que el objetivo del que cuelga** (revisada por el usuario el 2026-10-14:
     "aparte" sólo no alcanza, porque puede ser de verdad una parte que se atrasa). Lo que cuelga es parte del
     padre, y el padre no cierra hasta que cierran sus hijos (mecánica §5). La vista previa frena y ofrece tres
     salidas:
     - **cambiar la fecha;**
     - **"> cargarlo aparte",** si no es parte del padre: pasa a colgar del mismo lugar que el padre, o de
       ninguno, y se vuelve a ofrecer el tipo. Ejemplo: el laboratorio después de abrir la planta.
     - **"> aceptar la demora",** si es parte del padre. No hace falta otra aprobación, porque los objetivos
       sólo los crean Dirección y administración. Va en la J5, con el modelo de la decisión 7.
     Sin aceptar, la base no acepta un hijo que vence después que su padre. La J3-3b construye el freno, "cambiar
     la fecha" y "cargarlo aparte".
  6. **Una tarea que vence después que su objetivo** (usuario, 2026-10-14: "leda tiene que frenar esas cosas y
     dar aviso"). Una tarea no puede ir "aparte": el objetivo la necesita, y "Poner el módem en la pared" no
     termina sin "Comprar el estante". Leda frena antes de cargar: "Esta tarea vence después que «Poner el
     módem en la pared» (21/10): el objetivo se demoraría." La persona puede cambiar la fecha, o seguir y
     pedirle la aprobación al referente del objetivo. Mientras tanto la tarea queda pendiente: si el
     referente aprueba se carga, y si rechaza no, y quien la pidió se entera del motivo. Si quien carga es ese
     referente, su confirmación ya es la aprobación. El freno va en la J3-3b. El pedido de aprobación va en la
     J6, con la maquinaria de las propuestas; hasta entonces la única salida es cambiar la fecha.
  7. **Aceptar una demora no borra la fecha original** (usuario, 2026-10-14, "pensemos juntos": pisar la fecha
     haría parecer que nunca hubo un retraso, y dejarla sola haría perseguir un atraso ya decidido). La fecha
     original del objetivo queda como compromiso, y se anota una **fecha prevista** nueva con su motivo, quién
     lo decidió y cuándo. Leda sigue la fecha prevista, y la web muestra las dos: "21/10 → previsto 28/10, por
     «Comprar el estante», lo decidió Ismael". Hacia arriba, igual: si la fecha prevista pasa la del abuelo, se
     anota su fecha prevista. Es el mismo modelo que la previsión de las tareas (mecánica §9). Se construye en la
     J5, junto con las previsiones, y vale para "aceptar la demora" de un objetivo hijo (decisión 5) y de una
     tarea cargada por Dirección o administración (decisión 6).

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
  `0067` aplicada en `leda_motor` (respaldo `db/respaldos/leda_motor-antes-0067-20261013.dump`, `pg_restore
  --list` sin error; ensayo en una copia restaurada, borrada después; `cargar_tarea` con 13 argumentos, de
  `leda_owner` y `security definer`; aplicada con `psql -v ON_ERROR_STOP=1 -f` como `postgres`, sin error).
  Falta J1-5, la prueba en el celular.
- 2026-10-13: la primera prueba del usuario en el celular encontró tres cosas (J1-6): no se decía qué
  faltaba, el paso "revisar" sobraba y la página se corría de costado en el iPhone. Arregladas en
  `cc9cc41d` (escritor delegado); J1-5 se repite con el usuario.
- 2026-10-13: J2-1 a J2-4 hechas (escritor delegado): la entrada es un recuadro libre (usuario), Leda
  propone lo vacío y el código decide qué vale. Faltan la prueba en el celular (J2-5) y la ronda con
  la IA real (J2-6), con permiso.
- 2026-10-13: la segunda prueba encontró cuatro más (J1-7): al confirmar con un campo vacío la página
  se corría de costado, los mensajes blancos no se distinguían, lo que faltaba no estaba a la vista y
  "confirmar" no se veía apagado. Arregladas en `b7fb4ea7` (escritor delegado); J1-5 se repite con el usuario.
- 2026-10-13: J2-7 hecha (escritor delegado): los arreglos de las tres revisiones RDD de la J2 (la
  fecha la calcula el código con las palabras de la persona; la respuesta vieja no completa nada;
  la herramienta de medición). Siguen la prueba en el celular (J2-5) y la ronda real (J2-6).
- 2026-10-13: la ronda real de la J2 (J2-6), 29 de 33; el usuario decidió que "antes del jueves" es el
  miércoles. J2-8 hecha (escritor delegado, `f000059e`): "antes de" un día es el hábil anterior del
  espacio, los rangos no son fechas, "de mañana" es una hora, y la herramienta separa mejor los
  errores del programa. Sigue la prueba en el celular (J2-5).
- 2026-10-13: la prueba en el celular (J2-5) completó bien todo menos el criterio, que propuso
  circular; una tarea se había cargado con "No se". J2-9 hecha (escritor delegado, `3d4ab5fa` y
  `c0a0b206`): el criterio tiene que decir cómo se comprueba, al proponerlo y al cargarlo. Siguen
  la ronda real y repetir la J2-5.
- 2026-10-13: la repetición en el celular dio otro criterio circular, con sinónimos (el UPS): se
  disparó el punto 4 y el usuario cambió el diseño. J2-13 hecha (escritor delegado, `a4428fd9` y
  `73a32f9e`): la comprobación sale de la evidencia del área y el criterio lo juzga la IA por su
  sentido (sin la lista de palabras de la J2-9); lo que la ayuda no completa se ve en su campo, y
  los puntos de "completando…" se animan. Siguen una ronda real (con permiso) y la J2-12.
- 2026-10-13, noche: la J2 pasó en el celular (J2-14 a J2-28 y J2b; "quedó perfecto todo"; IA real 79 de 84).
  El usuario se fue a dormir y pidió: cerrar la J2 con su revisión de conjunto (J2-29) y la suite completa, y
  seguir solo con J3 a J7, anotando en "Para decidir al despertar" lo que necesite de él.
- 2026-10-13, noche: la J2-29 se hizo sin CRITICAL ni HIGH y sus arreglos son la J2-30. La suite completa sobre
  `eaf84ed4` dio `3286 passed, 1 warning in 1889.71s`, con `salida=0` (`LEDA_BASE_URL= LEDA_GEMINI_API_KEY=
  .venv/Scripts/python.exe -m pytest -q -p no:cacheprovider`).
