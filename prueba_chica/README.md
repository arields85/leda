# La prueba chica del Motor

Código descartable de la Etapa 2 del Motor: prueba el diseño del ADR 0018 en el circuito del
recordatorio. El plan, las tareas y la evidencia están en `odd/tasks/prueba-chica-del-motor.md`.

**En la Etapa 3 esta carpeta se borra entera.** El motor de conversación definitivo se escribe
de nuevo en `src/leda`, con su propia prueba de frontera.

## Qué hay

- `turno.py`: un turno. Lee el estado de la persona, sus tareas, el último aviso y sus últimos
  turnos; le pide a la IA las jugadas; maneja cada una; le pide a la IA la respuesta desde los
  hechos; la encola y deja todo en el registro de turnos. Si la IA no responde, un reintento y
  después el único texto fijo, con un incidente para el administrador.
- `fichas.py`: la lista cerrada de jugadas y sus fichas.
- `preguntas.py` y `situaciones.py`: las situaciones generales, una vez para todas las fichas
  (E2-4). Las preguntas de Leda, de a una y en orden, con lo que queda para después; la duda
  con las tareas como opciones; y las jugadas `elegir`, `corregir`, `cancelar` y
  `dejar_para_despues`.
- `botones.py`: las opciones de una duda salen como botones con la respuesta, por el outbox.
  Un toque corre el mismo turno que la elección escrita (`turno.procesar_toque`).
- `ia.py`: lo que el motor le pide a la IA y una IA guionada para las pruebas.
- `ia_real.py` e `instrucciones.py`: la IA real. Una llamada que fuerza a la IA a contestar con
  la lista cerrada (o con `fuera_de_la_lista`) y una que redacta desde los hechos, con el tono
  del espacio. El modelo sale de `model_config`; la clave, del entorno.
- `escuchar.py`: el escuchador por long polling (bot del equipo y bot de administración),
  con el ciclo.
- `avisos.py`: los avisos guardados, todo lo que Leda manda por su cuenta. Al llegar su hora,
  sólo dentro del horario, se vuelve a leer la tarea; si todavía corresponde, la IA lo redacta
  desde los hechos de ese momento y va al outbox; si no, queda omitido con su motivo. Si la IA
  no lo redacta, se reintenta a los 1, 2, 4 y 8 minutos; al quinto fallo, un incidente y el
  aviso de la falla a quien lo causó, que también redacta la IA.
- `escalera.py`: la escalera propia (mecánica §9; ADR 0018, 9b), en días hábiles desde el
  vencimiento: un aviso previo, pedidos de estado desde V que abren una espera y avanzan sólo
  sin respuesta, y el escalamiento por la ruta del pack. Un bloqueo la detiene; una ausencia
  la pausa y la vuelta lleva un reencuadre. Sólo guarda avisos: los manda `avisos.py`. Termina
  al escalar o con una respuesta; un paso que no llegó (la IA no lo redactó) no la apaga.
- `ciclo.py`: el ciclo, dentro del escuchador. Cada minuto, la escalera y los avisos guardados;
  en cada vuelta, el despacho (con el reloj de Leda) y los avisos a la administración. Cada
  paso aislado: si uno se cae, un incidente para el administrador y los demás siguen.
- `avisar.py`: el comando que dispara a mano el aviso previo de una tarea, por el mismo
  camino que los demás avisos guardados.
- `tiempo.py`: el reloj del motor. Los momentos los pone el motor, nunca la base.
- `reloj.py`: el reloj de Leda en `leda_motor` y el comando que lo adelanta (decisión 10.2).
- `test_frontera.py`: qué puede importar esta carpeta de `src/leda` y qué nunca debe alcanzar.

## Cómo se corren sus pruebas

Desde la raíz de la carpeta del Motor:

```
.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider prueba_chica
```

La suite de siempre (`pytest` sin ruta) no las corre: sólo mira `tests/`. Usan una base
efímera en el servidor de `LEDA_TEST_DB_URL` (`.env.test`), que se crea y se borra en cada
corrida, y nunca leen el `.env` de la carpeta ni tocan `leda`, `leda_flujo` o `leda_motor`.
Sin esa variable, las pruebas que piden la base se saltean. Telegram y la IA son transportes
falsos: ninguna prueba llama a un servicio de verdad.

## El paso de los días (E2-6)

Sólo en `leda_motor`, con la restricción de horario prendida (decisión 10.2 del usuario):

```
python -m prueba_chica.reloj corework adelantar   # al día hábil siguiente, 10:00
python -m prueba_chica.reloj corework estado      # hora real, reloj de Leda y horario
python -m prueba_chica.reloj corework volver      # vuelve al tiempo real
```

El adelanto se guarda en el espacio y el escuchador lo toma en su próxima vuelta: el turno, la
escalera, los avisos guardados y el horario del despacho ven el mismo momento. `adelantar`
saltea fines de semana y feriados; correrlo otra vez adelanta otro día. Lo que la base fecha
sola (los eventos de estado, la apertura de un bloqueo) queda en hora real. `volver` no
deshace lo escrito con el reloj adelantado: va al terminar la prueba.

## Primer contacto real (E2-3b)

Con `leda_motor` preparada (`odd/tasks/prueba-chica-del-motor.md`, sección 5) y el `.env` de
la carpeta apuntando a ella, con el bot de prueba del equipo y el de administración.

**El escuchador**, en una terminal propia, durante toda la prueba:

```
python -m prueba_chica.escuchar corework
```

Un solo escuchador por bot. Nunca imprime los tokens. Ctrl+C corta al terminar la vuelta en
curso (hasta 25 segundos).

**El aviso previo**, en otra terminal, cuando lo pida el guion:

```
python -m prueba_chica.avisar corework Marcos PLC
```

La persona y la tarea se nombran con palabras enteras del nombre y del título. El aviso se
guarda como hechos, la IA lo redacta y se encola. Correrlo de nuevo no repite el aviso de la
misma tarea (`--de-nuevo` manda otro). **Fuera del horario de CoreWork (lunes a viernes, 09:00
a 17:00) el aviso no sale:** queda guardado, sin redactar, y sale al volver a correr el comando en
horario. Las respuestas a lo
que escribe la persona salen a cualquier hora. Por eso el primer contacto se corre en horario.

Antes de empezar, cada cuenta que participa le escribe `/start` una vez al bot de prueba
(Telegram no deja que un bot escriba primero) y el administrador de plataforma le escribe
cualquier cosa al bot de administración con el escuchador corriendo, para que le lleguen los
avisos de incidentes.

### Guía (un solo hilo)

1. **Usuario**, en la terminal, en horario: `python -m prueba_chica.avisar corework Marcos PLC`
   → Leda le manda a Marcos el aviso previo de "Programar PLC de la comprimidora": cuándo
   vence y que no hace falta contestar. Sin botones. Nada de la otra tarea de Marcos.
2. **Marcos** escribe: "arranqué"
   → La tarea del PLC pasa de asignada a en curso (la tarea sale del último aviso). Leda dice
   que lo anotó, nombrando la tarea. No pide confirmación.
3. **Marcos** escribe: "llego el 27, el proveedor se demoró"
   → Una previsión para el 27 con su motivo, el atraso en días hábiles calculado por el
   código y la tarea que depende de ésta. La fecha comprometida no cambia. Leda dice qué anotó
   y que Ismael se va a enterar. No anota un bloqueo.
4. **Marcos** escribe: "estoy trabado, falta el repuesto"
   → Un bloqueo en la tarea del PLC con esa causa; la tarea queda bloqueada. Leda lo dice y
   hace una sola pregunta: quién lo puede destrabar (todo bloqueo con causa la lleva, 9c).
   Ningún aviso a Ismael.
5. **Marcos** escribe: "ni idea quién lo está comprando"
   → Queda anotado que no se sabe quién lo destraba. Leda lo dice y propone salidas: que
   alguien ayude o anotar una fecha nueva.

Después, leer la conversación con `tools/leer_conversacion.py` y la base (`conversation_turn`,
`task_forecast`, `blocker_unblocker`, `scheduled_notice`, `incident`).

### Límites conocidos

- **Las situaciones generales están desde la E2-4** (cambio de tema, varias cosas, corrección,
  cancelar, duda con botones, escrito en lugar de botón y toque viejo). Los botones viejos no
  se quitan del chat: un toque de una pregunta ya cerrada no hace nada y Leda dice con qué se
  cerró. Una corrección que vuelve a una previsión anterior no rearma el aviso de aquélla si se
  había retirado (`PENDIENTE`, plan, E2-4).
- **El aviso de la nueva previsión a Ismael se guarda pero no se envía** hasta la E2-5:
  queda en `scheduled_notice`, estado `guardado`. El hecho de la respuesta lo dice
  (`guardado_sin_enviar`, con la hora en que sale): Leda le dice a Marcos que Ismael se va a
  enterar, nunca que ya está avisado (primer contacto real, 2026-10-05).
- **El escuchador corre el ciclo** (E2-6): la escalera guarda el aviso previo sola, a su hora,
  y los avisos guardados salen con sus reintentos. El comando `avisar` lo adelanta a mano.
- **Pedidos fuera de la lista:** Leda dice qué puede hacer y el administrador recibe un aviso
  por el bot de administración; a la persona no se le dice que se avisó, salvo que lo pregunte.
- **`tools/restriccion_horario.py` todavía no admite `leda_motor`** (E2-6).
- **La bienvenida de `/start`** es el texto fijo de siempre (`leda.onboarding.bienvenida`).
