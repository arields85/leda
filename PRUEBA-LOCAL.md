# Prueba local con Ismael, Ariel y Marcos

Todo corre en tu máquina. Telegram no necesita que seas alcanzable desde
internet: en vez de webhook, Leda pregunta cada tanto si hay algo nuevo. Al
pasar a la VPS se cambia por webhook y no se toca nada más — los dos caminos
llaman a la misma función.

---

## 1. Preparar

```bash
cp .env.ejemplo .env
```

En `.env`:

```
LEDA_DB_URL=postgresql://leda:loquesea@localhost:5432/leda
LEDA_BOT_TOKEN_COREWORK=<el token de BotFather>
LEDA_LLM_API_KEY=<tu credencial>
```

`LEDA_WEBHOOK_SECRET` y `LEDA_BASE_URL` quedan vacíos: son para la VPS.

Base de datos:

```bash
docker compose up -d postgres
python -m leda esquema
```

## 2. Cargar el equipo

El token del bot **no** va en `espacios/corework.yaml`: ese archivo se versiona
en git. Vive en `.env`, como `LEDA_BOT_TOKEN_COREWORK`.

Lo único que el pack necesita es el `grupo_gestion_id`, que ya está cargado. Si
alguna vez cambia el grupo, Leda lo averigua sola:

```bash
python -m leda grupo corework
```

Después, tres comandos:

```bash
python -m leda importar corework --activar
python -m leda feriados corework
python -m leda modelo <identificador> --proveedor anthropic
```

El modelo no va en el pack ni en el núcleo: es configuración, y se cambia sin
tocar un archivo. Para ver cuáles ofrece un proveedor, `python -m leda
modelos --proveedor anthropic`; sin argumentos, `python -m leda modelo`
muestra el que está activo. La credencial depende del proveedor: `openrouter`
usa `LEDA_OPENROUTER_API_KEY` (la misma de Jev) y los demás
`LEDA_LLM_API_KEY`; si falta la que corresponde, Leda lo registra como
incidente en vez de usar la otra.

Cada llamada al modelo tiene un tiempo máximo por intento y reintentos acotados,
para que un pedido colgado del proveedor no deje esperando a la persona más de lo
razonable. Se ajustan en `parametros` de `model_config` con `timeout_s` (por
defecto 20 segundos) y `reintentos` (por defecto 2). Un timeout que agota los
reintentos se trata como cualquier otro error del proveedor: incidente y disculpa.

## 3. Dar de alta a los tres

```bash
python -m leda enlaces corework --solo Ismael Ariel Marcos
```

Mandale a cada uno **su** enlace, por privado. No los pegues en el grupo: un
enlace a la vista deja que cualquiera tome la identidad de otro y pase a
recibir su seguimiento.

Cada uno abre el suyo y aprieta Iniciar. Los otros cuatro quedan sin activar:
existen, tienen tareas y cuentan para cerrar objetivos, pero no reciben nada.

## 4. Escuchar

```bash
python -m leda escuchar corework
```

Ese proceso hace todo: recibe mensajes, contesta, dispara las cadencias que
ya vencieron, corre la escalera de recordatorios y despacha la cola. Ctrl+C
para cortar. Para probar sin que dispare cadencias automáticas (por ejemplo,
para no mezclar los mensajes de una cadencia con lo que se está probando a
mano), agregá `--sin-cadencias`; la escalera y el despacho siguen igual:

```bash
python -m leda escuchar corework --sin-cadencias
```

En otra terminal, para ver cómo va:

```bash
python -m leda estado corework
```

---

## Un guion para probar el circuito de aprobación

La aprobación sube un nivel: cada referente aprueba las tareas de su área, y a
los referentes los aprueba Ismael.

| Trabajo de | Lo aprueba | ¿Está en el piloto? |
|---|---|---|
| Nahuel (OT) | Marcos | sí |
| Lucas (IT) | Martín | no |
| Marcos, Martín, Ariel, Mariano | Ismael | sí, para Marcos y Ariel |
| Ismael | nadie — es la raíz | — |

Con Ismael, Ariel y Marcos podés probar los dos escalones: Marcos aprobando a
Nahuel, e Ismael aprobando a Marcos o a Ariel.

Nahuel no está en el piloto, pero se le pueden asignar tareas igual: existen,
aparecen en los informes y cuentan para cerrar el objetivo. Lo único que no va
a recibir es el seguimiento privado.

### Circuito corto — Ismael aprueba

1. Creá una tarea de CoreLabs. Desde el chat de Ariel:

   > *creá una tarea en corelabs para el panel de lote activo, responsable
   > Ariel, para el 14 de agosto, criterio: el panel muestra el lote en curso
   > con datos de EPPI*

2. Ariel dice que terminó:

   > *terminé el panel de lote*

   Leda la mueve a **en revisión**, no a terminada. Si intenta cerrarla, la
   base responde qué falta.

3. Ariel adjunta la evidencia:

   > *subí una captura del panel andando*

4. Ismael aprueba desde su chat:

   > *apruebo la tarea del panel de lote*

5. Ahora sí cierra. Verificá con `python -m leda estado corework`.

### Los dos escalones

Creá una tarea de OT con responsable **Nahuel** y otra con responsable
**Marcos**. La primera la aprueba Marcos; la segunda no puede aprobarla él
—aunque sea el referente del área— y le corresponde a Ismael.

Ese contraste es lo que muestra que la cadena es por persona y no por área.

### Qué probar que salga mal

- **Que Ariel apruebe su propia tarea.** Es referente, pero está solo en su
  área: lo aprueba Ismael.
- **Que Marcos apruebe una tarea suya.** Aprueba a Nahuel, no a sí mismo.
- **Que Ismael apruebe una tarea de Nahuel.** Tiene la decisión final del
  equipo, pero eso no lo habilita a firmar en lugar de Marcos.
- **Que Marcos apruebe una de CoreLabs.** No es su cadena.
- **Que alguien diga "esto es urgente".** Leda no debería marcarlo como
  urgente: sólo Ismael puede declararlo.
- **Que Ismael pida cambiar la configuración de Leda.** Tiene que derivarlo
  a la administración, cordialmente.
- **Un bloqueo.** Que Marcos diga que está trabado por algo. La tarea sale de
  la escalera de recordatorios y deja de recibir avisos.

### Cadencias sin esperar al lunes

Con `escuchar` (o `servir`) corriendo, cada cadencia se dispara sola apenas
vence su horario -- no hace falta reiniciar el proceso ni volver a importar
el pack para que un horario editado tome efecto. Para no esperar ni eso:

```bash
python -m leda correr corework objetivos_semanales
python -m leda correr corework resumen_grupal
```

### Escalera de recordatorios

Se calcula desde el vencimiento en días hábiles. Para verla sin esperar,
poné una tarea con fecha pasada:

```sql
update leda.task set fecha_objetivo = now() - interval '2 days'
 where titulo like 'Relevar%';
```

Y esperá una vuelta del proceso, o corré `python -m leda escalera corework`.

---

## Cuando algo falle

Al integrante nunca le llega un error técnico, sólo un mensaje genérico. Lo
que pasó queda acá:

```bash
python -m leda incidentes corework
```

---

## Qué mirar en estas dos semanas

Lo técnico está cubierto por las pruebas. Lo que no se puede probar solo es
si el equipo lo tolera:

- ¿Cinco toques semanales son muchos? Con tres personas se nota rápido.
- ¿El tono suena bien o suena a robot de RRHH?
- ¿Los recordatorios llegan cuando sirven o cuando molestan?
- ¿Alguien deja de contestar? Eso importa más que cualquier error.

Todo eso se ajusta editando `espacios/corework.yaml` y reimportando. No hace
falta tocar código.

---

## 5. Base nueva para la tercera ronda (sin "(simulado)" en los títulos)

Las 12 tareas ficticias de las sesiones 1 y 2 quedaron con " (simulado)" al
final del título. No se pueden renombrar: el título es un campo de
compromiso y `bloquear_estado_directo` (`db/esquema.sql`) lo protege como
inmutable. La salida es una base **nueva**, sembrada sin el sufijo -- estos
pasos no tocan la base actual (`postgres`, con los datos de las sesiones 1 y
2), pero que quede sin tocar no es lo mismo que tener un respaldo: mientras
no se corra el paso 1, sigue siendo la única copia. Esa misma base
`postgres` es además la base de mantenimiento a la que se conecta la suite
de pruebas (`LEDA_TEST_DB_URL`, `tests/conftest.py`) para crear y borrar
sus propias bases descartables (`leda_test_<id>`, una por sesión de
pruebas); las pruebas nunca escriben datos de sesión ahí, sólo la usan para
crear y borrar las suyas, pero nadie debería confiar en dejarla intacta como
si fuera la copia de respaldo.

**1. Respaldo real de la base actual**, antes de cualquier otra cosa -- este
`pg_dump` es la única copia independiente de los datos de las sesiones 1 y 2,
no "no tocar `postgres`":

```bash
mkdir -p db/respaldos
pg_dump "$LEDA_DB_URL" -Fc -f db/respaldos/leda-antes-base-nueva-<fecha>.dump
```

(`<fecha>` en `AAAAMMDD`, igual que los respaldos anteriores en esa carpeta.)

**2. Crear la base vacía `leda`**, en el mismo servidor:

```sql
create database leda;
```

o, equivalente, `createdb leda` con el mismo usuario y host que usa
`LEDA_DB_URL` hoy.

**3. Cambiar el nombre de la base en `.env`.** La variable es `LEDA_DB_URL`:
es una URL completa (`postgresql://usuario:contraseña@host:puerto/basededatos`)
y el nombre de la base es sólo el último segmento, después de la última `/` --
cambiá únicamente ese segmento, a `leda`; dejá usuario, contraseña, host y
puerto como están. Si `LEDA_AUTHORITY_DB_URL` también apunta a esta base
(no hay fallback entre las dos: `db/README.md`), cambiale el mismo segmento --
si sólo se cambia una de las dos, la sesión real terminaría escribiendo tareas
en una base y confirmándolas en otra.

**4. Aplicar el esquema completo** (ya con las migraciones `0013` a `0016`
incluidas: `esquema.sql` es el estado actual, no hace falta aplicar
migraciones sueltas sobre una base nueva):

```bash
python -m leda esquema
```

Es una base recién creada: `esquema.sql` crea los roles del clúster
(`leda_app`, `leda_admin`, `leda_gateway`, `leda_owner`) si todavía no
existen -- como suelen ya existir en el mismo servidor por la base anterior,
esa parte no hace nada la segunda vez -- así que sólo hace falta que el
usuario de `LEDA_DB_URL` pueda crear roles y el esquema `leda` en esta
base nueva, ni más ni menos que lo que ya hacía falta para la base actual.

> **Nunca correr `python -m leda esquema --recrear` contra la base
> anterior.** Borra todos los datos. La base nueva se crea recién, así que
> acá no hace falta -- y contra la anterior jamás, es el respaldo.

**5. Importar el pack, feriados y sembrar:**

```bash
python -m leda importar corework --activar
python -m leda feriados corework
python -m leda sembrar corework --semilla espacios/corework.semilla-ficticia.yaml
```

`sembrar` rechaza con un mensaje claro si el espacio ya tiene alguna tarea
(no mezcla datos ficticios con datos reales) o si el espacio no existe
todavía (correr `importar` primero). Sólo imprime cuántas tareas y
dependencias quedaron, y cuántas por estado inicial -- nunca los títulos ni
los nombres de las personas.

**5b. Configurar el modelo de lenguaje.** Una base nueva no hereda el modelo de
la anterior: sin este paso, cada mensaje de texto termina en un incidente
("No hay modelo configurado"). Ver el activo con `python -m leda modelo` y
configurarlo, por ejemplo:

```bash
python -m leda modelo <identificador> --proveedor openrouter
```

**6. Volver a vincular las cuentas de Telegram** (son las mismas personas del
pack, pero es una base nueva: sin activaciones previas). Con `--solo` y los
nombres de quienes participan de esta ronda, igual que en el punto 3 más
arriba; sin `--solo`, genera el enlace de las siete:

```bash
python -m leda enlaces corework --solo <nombres>
```

**7. Arrancar el proceso** que escucha Telegram, igual que en las sesiones
anteriores:

```bash
python -m leda escuchar corework
```

La semilla deja, para probar entrega con evidencia y "Pedir cambios" (ADR
0009 y su enmienda T6c): una tarea `en_curso` por cada responsable con
aprobador, lista para "Ya la terminé" con evidencia; una tarea `en_curso`
con una dependencia bloqueante abierta hacia otra tarea sin terminar, para
pedirle cambios a esa entrega y comprobar que vuelve a `en_curso` (no a
`asignada`); el resto, `asignada`. Nada preaprobado, nada en revisión.
Detalle completo en `espacios/corework.semilla-ficticia.yaml`.

**8. Designar administrador de plataforma y vincular el bot de
administración** (T11, Constitución §10): un aviso de incidente sólo le
llega a quien tiene `platform_role.rol = 'administrador'` **y** ya le
escribió al bot de administración -- Telegram no deja que un bot le escriba
primero a quien nunca le escribió. Ninguna de las dos cosas pasa sola en un
entorno local nuevo.

Agregá a `.env` el token de un bot de administración **aparte** -- nunca el
mismo que `LEDA_BOT_TOKEN_COREWORK`: un integrante no puede terminar
recibiendo avisos de administración por el bot de su propio equipo:

```
LEDA_BOT_TOKEN_ADMIN=<el token de BotFather del bot de administración>
```

Elegí a alguien del equipo ya vinculado (punto 6) y otorgale el rol:

```bash
python -m leda administrador corework Ismael
```

Es idempotente: correrlo de nuevo no duplica el rol, y avisa si la persona
ya lo tenía. Si todavía no activó su cuenta de Telegram, igual se lo otorga
-- pero avisa que los incidentes no le van a llegar hasta que la active y
escriba una vez al bot de administración.

Con `python -m leda escuchar corework` corriendo (punto 7 -- ahora también
sondea el bot de administración, sin bloquear, si `LEDA_BOT_TOKEN_ADMIN`
está puesto), esa persona le escribe **una vez** cualquier cosa al bot de
administración. Sin ese mensaje no hay a qué `chat_id` mandarle nada.
Hacelo mientras el listener está corriendo: Telegram descarta las
actualizaciones no leídas después de 24 horas, así que un mensaje mandado
con el listener apagado se puede perder.

**Nunca pongas en `LEDA_BOT_TOKEN_ADMIN` el token de un bot de
administración que ya está servido por webhook en otro lado** (p. ej. el
de producción, el que atiende `servir`): antes de sondear, `escuchar`
CONSULTA si el bot ya tiene un webhook puesto -- si lo tiene, nunca lo toca
ni lo sondea, para no robarle los updates a quien lo está sirviendo; sólo
avisa por consola, una vez. Si ese aviso aparece y el webhook es un resto
de una prueba local anterior sobre ESTE MISMO bot de administración (nunca
sobre uno de producción), sacalo a mano una vez con:

```bash
curl "https://api.telegram.org/bot<token>/deleteWebhook"
```

y el listener lo detecta solo, dentro de un minuto aproximadamente, sin
reiniciar nada.
