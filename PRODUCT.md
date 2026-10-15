# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Integrantes** (quienes hacen el trabajo): el uso más intenso. Abren la web desde el celular, dentro de
  Telegram (la Mini App «Mi espacio»), en momentos cortos y entre otras tareas: ver lo suyo, qué vence, qué
  les falta para seguir, y avisar algo.
- **Referentes de área y Dirección** (la autoridad final del equipo): también la usan sobre todo desde la
  Mini App; van a la computadora sólo para lo más complejo y puntual: cargar tareas y objetivos con la ayuda
  de Leda, organizar el equipo (altas, bajas, áreas, referentes), revisar.
- **Administración de la plataforma**: sólo desde la computadora; se ocupa de la parte técnica y de los
  espacios, no de la organización interna de cada equipo.

## Product Purpose

Leda es un project manager digital para equipos: hace el seguimiento cotidiano del trabajo por chat
(Telegram) para que no recaiga en una persona. La web es donde vive la estructura del trabajo: tareas,
objetivos, quién hace qué, quién aprueba a quién, y el estado de cada cosa. Éxito: que cada persona sepa en
segundos qué tiene, qué vence y qué le falta, y que nada se atrase sin que alguien lo sepa a tiempo.

## Positioning

Por chat, los hechos del trabajo; por la web, su estructura. La conversación la lleva Leda (una IA que elige
qué hacer de una lista cerrada y un código que ejecuta y audita); la web no es un gestor de tareas genérico
sino el reflejo de lo que el equipo y Leda ya saben, con las mismas reglas: confirmación humana antes de un
efecto, honestidad (nunca muestra algo que nadie confirmó) y aislamiento total entre clientes.

## Operating Context

- Telegram Mini App a pantalla completa en el celular (uso principal), y navegador de escritorio con una
  sesión por QR (uso puntual). Las dos puertas: la del equipo y la de administración.
- Equipos de cualquier rubro; el primer cliente (CoreWork) es de automatización industrial: tableros, PLC,
  instalaciones. Todo lo probado hasta ahora es con datos ficticios.
- Cada espacio es un cliente independiente, con sus áreas, roles, horario y vocabulario.

## Capabilities and Constraints

- React y TypeScript (Vite) en `web/`, servida por el monolito en Python (FastAPI); sin otra superficie.
- Dentro de Telegram: respeta el viewport, las áreas seguras y el botón de volver de la Mini App.
- Textos en español rioplatense, cálidos y concretos; nunca nombres internos ni estados técnicos
  («SIN EMPEZAR», «esperando», «decir qué falta y quién se ocupa», nunca «trabada»).
- Estados de una tarea: sin empezar, en curso, esperando algo para seguir, en revisión, terminada, cancelada;
  una fecha comprometida y, si se aceptó una demora, una prevista.
- Cada efecto pasa por una vista previa y una confirmación.

## Brand Commitments

- El nombre es **Leda**. Su personalidad (`nucleo/personalidad.md`, `nucleo/constitucion.md` §8): cordial,
  clara, breve, orientada a soluciones; persistente sin ser hostil; un equipo, no una competencia (nunca
  compara ni arma rankings de personas); informa antes que callar, también las buenas noticias.
- El estilo visual actual (oscuro, grises, monoespaciada, color sólo donde hay algo) es la referencia de lo
  hecho, no una regla: el usuario pidió explorar estilos nuevos (2026-10-15).

## Evidence on Hand

- Datos ficticios del espacio de prueba CoreWork (`espacios/corework.yaml`): Ismael (Dirección), Marcos,
  Martín y Mariano (referentes), Nahuel, Lucas y otros integrantes; tareas como «Armar el tablero» o
  «Pasar los cables». No hay clientes reales, testimonios ni métricas: no se inventan.

## Product Principles

1. Lo de cada persona primero: qué tiene, qué vence y qué le falta, en segundos y desde el celular.
2. Decir lo que es: estado real, sin suavizar atrasos ni inventar avances.
3. Ayudar sin burocracia: Leda propone, la persona confirma; nada de pasos que no aportan.
4. La estructura la decide el equipo según su jerarquía; la web lo refleja y no lo saltea.
5. Un equipo, no una competencia.
