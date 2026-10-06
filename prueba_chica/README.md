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
- `leer.py`: el lector del registro de turnos, de sólo lectura.
- El corredor de las conversaciones de prueba (E2-7): `conversaciones/` (las 15 de
  `tests/conversaciones/` en YAML, con lo que se comprueba solo; el `.md` es la fuente),
  `carga.py` (el estado inicial de cada una), `corredor.py` (una corrida, paso por paso, por el
  código de verdad), `comprobar.py` (qué se compara y cómo se clasifica una falla), `grabar.py`
  (la IA guionada con las jugadas esperadas, la que graba y la que repite), `jev_paralelo.py`,
  `gasto.py` (el techo de USD 30, decisión 10.4), `informe.py` y `correr.py` (el comando).
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

## Correr las conversaciones (E2-7)

```
python -m prueba_chica.correr --ia guionada --veces 1          # en seco, sin gasto
python -m prueba_chica.correr --ia sol --veces 5 --paralelo 5 --grabar prueba_chica/grabaciones
python -m prueba_chica.correr --ia luna --veces 5 --paralelo 5 --grabar prueba_chica/grabaciones
python -m prueba_chica.correr --ia sol --veces 5 --conversacion 13 14 --jev
python -m prueba_chica.correr --repetir prueba_chica/grabaciones/03-sol-2.json
```

Cada corrida va en una base nueva del servidor de `LEDA_TEST_DB_URL`, copia de una plantilla, y
se borra al terminar; nunca toca `leda`, `leda_flujo` ni `leda_motor`. El reloj se mueve a los
momentos que dice cada `.md`; el transporte es falso. Con `sol` o `luna` la clave sale del
entorno (`LEDA_OPENROUTER_API_KEY`) y nunca se imprime. **El techo:** antes de empezar se
estima la ronda; si con eso el gasto de la etapa pasa de USD 30, no corre (`--pasar-el-techo`,
sólo con el OK del usuario); avisa desde el 80 %. **El crédito:** también antes de empezar se
pregunta a OpenRouter cuánto le queda a la cuenta y, si no alcanza para lo estimado, no corre
(sale con 3; si no se puede preguntar, avisa y sigue); un HTTP 402 a mitad de ronda la corta
(sale con 3) y las corridas que lo tuvieron quedan inválidas, aparte en el informe. La cuenta queda en `resultados/gasto.json` y
el informe de la ronda, con sus transcripciones, en `resultados/` (las grabaciones crudas, en
`grabaciones/`, no se versionan). La comprensión automática del informe es provisional: la que
vale es la lectura del usuario (decisión 10.3).

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

## Leer una prueba (E2-6)

```
python -m prueba_chica.leer corework [--persona Marcos] [--desde 10:30] [--completo]
```

Muestra los turnos en orden (lo que escribió o tocó cada persona, con las jugadas, los hechos,
la IA, la latencia y el error; lo que salió de Leda, con el estado del mensaje), las preguntas
abiertas y para después, las esperas sin contestar y los avisos guardados con su estado. Un
toque se ve como la opción tocada. `--desde` es la hora de hoy en el reloj de Leda (o
`"AAAA-MM-DD HH:MM"`). Sólo lee.

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

Después, leer la conversación con `python -m prueba_chica.leer corework` y la base
(`task_forecast`, `blocker_unblocker`, `incident`).

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
- **`tools/restriccion_horario.py` admite `leda_motor`** (E2-6), pero en esta prueba la
  restricción va prendida y los días pasan con el reloj de Leda (decisión 10.2).
- **La bienvenida de `/start`** es el texto fijo de siempre (`leda.onboarding.bienvenida`).

## Prueba por Telegram real (E2-9)

`leda_motor` recreada el 2026-10-06 (respaldo previo en
`db/respaldos/leda_motor-antes-e2-9-20261006.dump`), con la semilla ficticia: las 12 tareas
vencen el **viernes 16/10**. Marcos tiene "Programar PLC de la comprimidora" (asignada) y
"Revisar comunicaciones industriales de la comprimidora" (en curso, depende del PLC); Ariel,
"Dashboard de lotes en CoreLabs" (en curso) e "Integrar datos de la comprimidora en CoreLabs"
(asignada). Ismael no tiene tareas: es el referente de los dos y a quien se escala.

**Antes de empezar:**

- Terminal 1: `.venv\Scripts\python.exe -m prueba_chica.escuchar corework` (queda corriendo).
- Ariel, Ismael y Marcos: `/start` al bot nuevo del equipo; Ariel, un "hola" al bot nuevo de
  administración.
- Terminal 2, para el reloj: `.venv\Scripts\python.exe -m prueba_chica.reloj corework
  adelantar` lleva a Leda al día hábil siguiente, 10:00 (saltea fines de semana y el feriado
  del lunes 12). Después de cada salto, esperar un minuto: el ciclo corre por minuto real.

**Qué mirar:** que Leda no se pierda ni se trabe (5b.2) y que se sienta natural (5b.3). Cuando
Leda le escribe a alguien por su cuenta, junta sus dos tareas en un mensaje pero pregunta por
una sola; la otra queda para después. Las respuestas de abajo sirven pregunte por cuál
pregunte.

### Guía (un solo hilo)

1. **Reloj:** adelantar → miércoles 07/10, 10:00.
2. **Marcos** escribe: "qué tengo pendiente?"
   → Leda le lista sus dos tareas, con su estado y que vencen el viernes 16. No inventa nada.
3. **Ariel** escribe: "arranqué con la integración de la comprimidora"
   → "Integrar datos de la comprimidora en CoreLabs" pasa a en curso. Leda lo dice nombrando la
   tarea, sin pedir confirmación ni preguntar de más.
4. **Reloj:** adelantar tres veces → jueves 08, viernes 09 y martes 13 (el lunes es feriado).
   → El martes 13, Marcos y Ariel reciben el aviso previo: un mensaje cada uno, con el saludo
   del día, que dice que sus tareas vencen el viernes y que no hace falta contestar. Nadie
   contesta.
5. **Reloj:** adelantar tres veces → miércoles 14, jueves 15 y viernes 16 (el vencimiento).
   → El viernes, Marcos y Ariel reciben el primer pedido de estado, con una pregunta.
6. **Marcos** escribe: "con el PLC estoy trabado, me falta el cable de programación. comunicaciones la termino el 23"
   → Leda toma las dos cosas: un bloqueo en la del PLC, con esa causa, y una previsión para
   el viernes 23 en la de comunicaciones (la fecha comprometida no cambia). Dice qué anotó,
   que Ismael se va a enterar de la fecha nueva, y hace una sola pregunta: quién lo puede
   destrabar.
7. **Marcos**, sin contestar eso, escribe: "qué más tengo?"
   → Leda le contesta o le ofrece dejarlo para después, pero no pierde la pregunta abierta ni
   la da por contestada.
8. **Marcos** escribe: "el cable lo trae Juan de compras"
   → Queda anotado quién lo destraba (alguien de afuera del equipo). Leda lo dice. Ariel no
   contesta nada en todo este día.
9. **Reloj:** adelantar → lunes 19.
   → Ismael recibe el aviso de la previsión de Marcos: comunicaciones para el 23, con el
   motivo. Ariel recibe el segundo pedido de estado. Marcos no recibe nada del PLC (está
   trabado).
10. **Marcos** escribe: "llegó el cable"
    → El bloqueo se cierra y el PLC vuelve a como estaba (asignada). Leda lo dice; no lo da
    por empezado.
11. **Reloj:** adelantar → martes 20.
    → Marcos recibe un pedido de estado del PLC. Ariel recibe el tercero, que dice que si no
    contesta se le avisa a Ismael.
12. **Marcos** escribe: "arranqué recién"
    → El PLC pasa a en curso. Leda lo dice y no lo vuelve a perseguir por eso.
13. **Marcos** escribe: "la de comunicaciones me la podés pasar a Nahuel?"
    → Leda no la reasigna: dice que eso lo decide Ismael y ofrece anotar una fecha nueva.
14. **Reloj:** adelantar → miércoles 21.
    → Ismael recibe, en privado, el escalamiento por Ariel: no contestó sobre sus tareas.
    Factual y respetuoso, sin culpar a nadie.
15. **Ariel** escribe: "perdón, estuve a full. la integración la termino el viernes 23"
    → Una previsión para el 23 en "Integrar datos…". Leda lo dice sin retarlo y avisa que
    Ismael se va a enterar.
16. **Reloj:** adelantar → jueves 22.
    → Ismael recibe el aviso de la previsión de Ariel.
17. **Al terminar:** `.venv\Scripts\python.exe -m prueba_chica.reloj corework volver` y cortar
    el escuchador con Ctrl+C.

**Ruido esperado:** Martín, Lucas, Nahuel y Mariano tienen tareas pero no Telegram; sus avisos
no les llegan, y el miércoles 21 Ismael puede recibir escalamientos por ellos y Ariel avisos
de incidente por el bot de administración. No es parte del juicio, salvo que Leda diga algo
falso (por ejemplo, que no contestaron a un mensaje que nunca les llegó): eso sí se anota.

Después, el agente lee la conversación con `python -m prueba_chica.leer corework` y la base;
el usuario cuenta cómo se sintió.
