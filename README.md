# Leda

Project manager digital que se asigna a un equipo de personas y se encarga de que
el trabajo tenga objetivos, responsables, fechas, dependencias y criterios claros.

La navegación documental comienza en [`docs/INDEX.md`](docs/INDEX.md). El estado
activo y el roadmap vigente se mantienen en `docs/STATUS.md` y `docs/ROADMAP.md`.

Leda no es específica de ninguna disciplina. El mismo núcleo sirve para un
equipo de ingeniería, de mantenimiento o de administración. Lo que cambia entre
un equipo y otro son los datos del espacio de trabajo.

---

## Estructura

```
nucleo/
  constitucion.md      Reglas que ningún equipo puede cambiar
  mecanica-pm.md       Jerarquía, estados, cierre, recordatorios, bloqueos
  alta-de-equipo.md    Guion de entrevista para dar de alta un espacio

espacios/
  corework.yaml        Configuración del equipo CoreWork

plantillas/
  mantenimiento.yaml   Punto de partida para un equipo de mantenimiento

db/
  esquema.sql          Estado completo de la base
  pruebas.sql          15 comprobaciones de las reglas del núcleo

src/leda/
  config.py            Credenciales y rutas. Nada de política.
  db.py                Conexión, rol y espacio activo
  importador.py        Pack YAML → base, con las validaciones del alta
  calendario.py        Días hábiles y feriados
  escalera.py          Recordatorios anclados al vencimiento
  reloj.py             Cadencia y planificador
  despachador.py       Cola de salida hacia Telegram
  autoridad.py         Permisos, verificados del lado del servidor
  onboarding.py        Enlaces de activación individuales
  herramientas.py      Lo único que Leda puede hacer en el mundo
  contexto.py          Núcleo, espacio y momento, en ese orden
  llm.py               Proveedor de modelo detrás de una interfaz
  agente.py            El turno: mensaje entra, respuesta a la cola
  gateway.py           Webhook, un bot por espacio
  cli.py               python -m leda …
```

## El turno del agente

El modelo no escribe en la base. Pide una herramienta; la herramienta valida la
autoridad de quien la pidió y recién ahí toca algo. Es la diferencia entre una
regla en el prompt, que se puede convencer, y una regla en el servidor, que no.

```
mensaje → contexto (núcleo + espacio + momento)
        → modelo propone herramientas
        → autoridad valida  ──rechaza→  el modelo recibe el motivo y lo explica
        → base ejecuta      ──impide→   idem
        → glosario corrige la salida
        → cola de salida → Telegram
```

Tres cosas que se cumplen pase lo que pase con el modelo:

- una acción denegada no toca la base, y la persona recibe una explicación
  humana, sin detalles técnicos;
- una acción que exige confirmación queda esperando en la cola sin ejecutarse;
- si algo falla, el integrante recibe un mensaje genérico y el incidente queda
  registrado, con la traza cruda separada de lo que se muestra.

## Poner en marcha

```bash
cp .env.ejemplo .env          # completar tokens y credenciales
docker compose up -d postgres
python -m leda esquema
python -m leda importar corework            # revisar advertencias
python -m leda feriados corework
python -m leda importar corework --activar
python -m leda servir
```

Después, el alta de cada persona:

```bash
python -m leda enlaces corework --solo Marcos Nahuel
python -m leda presentar corework
```

```bash
python -m pytest              # 99 pruebas sobre PostgreSQL real
```

Las pruebas levantan su propio PostgreSQL descartable con `pgserver`, que no
tiene ruedas para Windows. Ahí, y en cualquier máquina donde se prefiera un
servidor propio, alcanza con dejar en `.env.test`:

```
LEDA_TEST_DB_URL=postgresql://postgres:CONTRASENA@localhost:5432/postgres
```

Cada corrida crea su propia base, le aplica el esquema y la borra al terminar.
El usuario necesita permiso para crear bases y roles, y la URL tiene que
apuntar a la base de mantenimiento: las pruebas truncan todas las tablas.

## Alta de integrantes

Telegram no deja que un bot escriba primero a alguien que nunca interactuó con
él. Cada persona abre su enlace y aprieta Iniciar una vez; recién ahí Leda
puede hacerle seguimiento privado.

**Los enlaces se entregan uno a uno.** Publicarlos en el grupo permitiría que
cualquiera tome la identidad de otro y pase a recibir su seguimiento.

Un espacio se activa aunque nadie haya activado su enlace todavía: las personas
existen, tienen tareas y cuentan para el cierre de un objetivo. Lo único que
falta hasta entonces es el canal privado. Eso permite empezar con dos o tres
personas y sumar al resto cuando la cadencia ya esté ajustada.

### Núcleo

Es código y reglas fijas. Se versiona en git y se carga al arrancar. Cada acción
registrada guarda con qué versión del núcleo se tomó.

Cambiarlo requiere una intervención deliberada del administrador de plataforma
sobre el repositorio. No se cambia por conversación ni por configuración.

### Espacios

Un espacio es un equipo. Cada uno tiene su pack de configuración y su propio bot
de Telegram. Un pack define personas, áreas, autoridad, política de aprobación,
cadencia, horarios, vocabulario, tono y rutas de escalamiento.

Un pack no puede contradecir el núcleo. Si lo intenta, se rechaza al importarse.

### Plantillas

Packs de arranque por tipo de equipo. En el alta, Leda parte de una plantilla y
entrevista sólo sobre lo que difiere.

---

## Los dos ejes de rol

Son independientes. Tener uno no otorga nada del otro.

| | Rol de plataforma | Rol de espacio |
|---|---|---|
| Alcance | Leda entera | un equipo |
| Habilita | crear y configurar espacios, modelos, incidentes, respaldos, acceso a conversaciones | tener tareas, aprobar, escalar |
| Dónde se ejerce | bot de administración | bot del espacio |

El sombrero lo define el canal. En el bot de un espacio, Leda trata a quien le
escribe según su rol en ese espacio, aunque sea administrador de plataforma.

Ampliar la autoridad de Leda dentro de un equipo requiere dos actos de dos
personas: la autoridad del espacio **autoriza**, el administrador de plataforma
**aplica**. El registro guarda ambas firmas.

---

## Qué anda hoy

- Importación de un pack a la base, con las validaciones del alta: rechaza
  activar un espacio con áreas sin aprobador, sin autoridad final o con valores
  sin definir.
- Calendario laboral con feriados. La escalera avanza en días hábiles.
- Escalera de recordatorios anclada al vencimiento, con ausencias y con salida
  automática cuando la tarea se bloquea.
- Cadencia declarada en el pack, convertida a cron e idempotente por semana.
- Cola de salida: no escribe fuera de horario, reintenta, abre incidente al
  agotar intentos y respeta el tope de mensajes por persona.
- Autoridad verificada del lado del servidor, con los dos ejes de rol.
- Turno del agente completo: webhook, contexto, herramientas validadas,
  corrección de vocabulario y respuesta por la cola.
- Acciones pendientes: una herramienta con sus argumentos queda congelada
  hasta que la persona confirma o elige. El toque de un botón la ejecuta; el
  de otro integrante, no. Dos toques ejecutan una sola vez.
- Memoria de la conversación: el turno trae lo que se dijeron en las últimas
  horas de ese chat. De su propio lado sólo cuenta lo que efectivamente salió.

## Qué falta

- Consola de administración y panel de equipo.
- Onboarding por Telegram: enlaces de activación individuales.
- Guion de alta conversacional (hoy el pack se escribe a mano).
- Migraciones con Alembic a partir del primer despliegue real.
- Grafo de transiciones de estado permitidas.

`LEDA_DOCUMENTO_MAESTRO.md` (v1.5) es el borrador original del que salió todo
esto. Queda como referencia histórica; la fuente de verdad es este árbol.
