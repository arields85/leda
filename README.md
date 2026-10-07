# Leda

> **Nota del 2026-10-04.** Esta es la guía operativa del código de `main`. El estado, el orden de
> trabajo y el próximo paso están en [`docs/STATUS.md`](docs/STATUS.md): la línea de trabajo
> vigente es el Motor, en la rama `feat/motor-de-conversacion`. La sección "Qué falta", al final,
> es historia y no un orden de trabajo.

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
  siembra.py           Datos ficticios para probar (python -m leda sembrar)
  calendario.py        Días hábiles y feriados
  salida.py            Lo que sale: validación del texto y la cola (outbox)
  despachador.py       Cola de salida hacia Telegram
  saludo.py            El saludo del día, una vez por persona
  autoridad.py         Permisos, verificados del lado del servidor
  onboarding.py        Enlaces de activación individuales
  herramientas.py      Lo único que Leda puede hacer en el mundo
  pendientes.py        Acciones congeladas hasta que una persona confirma o elige
  menu_tarea.py        Los cambios pedidos vigentes de una tarea
  lectura.py           Lecturas del estado de un espacio
  huerfanos.py         Aviso neutro a un mensaje que quedó sin respuesta
  incidentes.py        Incidentes sanitizados y aviso a la administración
  llm.py               Direcciones de los proveedores y tiempo máximo de la IA
  entrada.py           Aplicación HTTP: webhook de Telegram, tablero y salud
  motor/               El motor de conversación: turnos, escalera, ciclo, reloj de Leda,
                       escuchador (escucha.py) y lo que se hace con cada update (recibir.py)
  tablero.py           El tablero de sólo lectura de un espacio
  tablero_vista.py     Su página
  cli.py               python -m leda …
```

La conversación de los flujos A y B (`gateway`, `agente`, `contexto`, `ingreso_tareas`
y sus módulos) se borró en la Etapa 3 del Motor (`docs/STATUS.md`), y con ella la escalera,
la cadencia y el ciclo de fondo viejos (`escalera.py`, `reloj.py`, `ciclo.py`, E3-7). Leda
conversa con el motor de conversación (`src/leda/motor/`): en una máquina, por long polling
con `python -m leda escuchar <espacio>`; en un servidor, por webhook con `python -m leda
servir` (`PRUEBA-LOCAL.md`). Las cadencias vuelven después de M3. El motor de la prueba
chica, descartable, sigue en `prueba_chica/` hasta la E3-8.

## El turno del agente

> El turno que describe esta sección era el de los flujos A y B, que se borraron (E3-3 y
> E3-4). El principio sigue: el motor de conversación definitivo pide herramientas y el
> servidor las valida (ADR 0018).

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
python -m leda webhooks   # registra el webhook de cada bot (LEDA_BASE_URL, LEDA_WEBHOOK_SECRET)
python -m leda servir     # webhook, tablero, salud y el ciclo del motor de cada espacio
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
- Herramientas validadas en el servidor y respuesta por la cola. El turno del
  agente de los flujos A y B se borró; vuelve con el motor de conversación (E3-7).
- Acciones pendientes: una herramienta con sus argumentos queda congelada
  hasta que la persona confirma o elige. El toque de un botón la ejecuta; el
  de otro integrante, no. Dos toques ejecutan una sola vez.

## Qué falta

- Consola de administración y panel de equipo.
- Onboarding por Telegram: enlaces de activación individuales.
- Guion de alta conversacional (hoy el pack se escribe a mano).
- Migraciones con Alembic a partir del primer despliegue real.
- Grafo de transiciones de estado permitidas.

`LEDA_DOCUMENTO_MAESTRO.md` (v1.5) es el borrador original del que salió todo
esto. Queda como referencia histórica; la fuente de verdad es este árbol.
