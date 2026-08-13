# Prueba local con Ismael, Ariel y Marcos

Todo corre en tu máquina. Telegram no necesita que seas alcanzable desde
internet: en vez de webhook, Prisma pregunta cada tanto si hay algo nuevo. Al
pasar a la VPS se cambia por webhook y no se toca nada más — los dos caminos
llaman a la misma función.

---

## 1. Preparar

```bash
cp .env.ejemplo .env
```

En `.env`:

```
PRISMA_DB_URL=postgresql://prisma:loquesea@localhost:5432/prisma
PRISMA_BOT_TOKEN_COREWORK=<el token de BotFather>
PRISMA_LLM_API_KEY=<tu credencial>
```

`PRISMA_WEBHOOK_SECRET` y `PRISMA_BASE_URL` quedan vacíos: son para la VPS.

Base de datos:

```bash
docker compose up -d postgres
python -m prisma esquema
```

## 2. Cargar el equipo

El token del bot **no** va en `espacios/corework.yaml`: ese archivo se versiona
en git. Vive en `.env`, como `PRISMA_BOT_TOKEN_COREWORK`.

Lo único que el pack necesita es el `grupo_gestion_id`, que ya está cargado. Si
alguna vez cambia el grupo, Prisma lo averigua sola:

```bash
python -m prisma grupo corework
```

Después, tres comandos:

```bash
python -m prisma importar corework --activar
python -m prisma feriados corework
python -m prisma modelo <identificador> --proveedor anthropic
```

El modelo no va en el pack ni en el núcleo: es configuración, y se cambia sin
tocar un archivo. Para ver cuáles ofrece un proveedor, `python -m prisma
modelos --proveedor anthropic`; sin argumentos, `python -m prisma modelo`
muestra el que está activo.

## 3. Dar de alta a los tres

```bash
python -m prisma enlaces corework --solo Ismael Ariel Marcos
```

Mandale a cada uno **su** enlace, por privado. No los pegues en el grupo: un
enlace a la vista deja que cualquiera tome la identidad de otro y pase a
recibir su seguimiento.

Cada uno abre el suyo y aprieta Iniciar. Los otros cuatro quedan sin activar:
existen, tienen tareas y cuentan para cerrar objetivos, pero no reciben nada.

## 4. Escuchar

```bash
python -m prisma escuchar corework
```

Ese proceso hace todo: recibe mensajes, contesta, corre la escalera de
recordatorios y despacha la cola. Ctrl+C para cortar.

En otra terminal, para ver cómo va:

```bash
python -m prisma estado corework
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

   Prisma la mueve a **en revisión**, no a terminada. Si intenta cerrarla, la
   base responde qué falta.

3. Ariel adjunta la evidencia:

   > *subí una captura del panel andando*

4. Ismael aprueba desde su chat:

   > *apruebo la tarea del panel de lote*

5. Ahora sí cierra. Verificá con `python -m prisma estado corework`.

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
- **Que alguien diga "esto es urgente".** Prisma no debería marcarlo como
  urgente: sólo Ismael puede declararlo.
- **Que Ismael pida cambiar la configuración de Prisma.** Tiene que derivarlo
  a la administración, cordialmente.
- **Un bloqueo.** Que Marcos diga que está trabado por algo. La tarea sale de
  la escalera de recordatorios y deja de recibir avisos.

### Cadencias sin esperar al lunes

```bash
python -m prisma correr corework objetivos_semanales
python -m prisma correr corework resumen_grupal
```

### Escalera de recordatorios

Se calcula desde el vencimiento en días hábiles. Para verla sin esperar,
poné una tarea con fecha pasada:

```sql
update prisma.task set fecha_objetivo = now() - interval '2 days'
 where titulo like 'Relevar%';
```

Y esperá una vuelta del proceso, o corré `python -m prisma escalera corework`.

---

## Cuando algo falle

Al integrante nunca le llega un error técnico, sólo un mensaje genérico. Lo
que pasó queda acá:

```bash
python -m prisma incidentes corework
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
