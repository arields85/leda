# Tablero de cliente, versión funcional mínima

> **Nota del 2026-10-04.** Este documento es anterior al Motor, la línea de trabajo vigente. Lo que
> figure acá como en curso, pendiente o próximo paso no se retoma sin una decisión del usuario. El
> orden de trabajo vigente está en [`docs/STATUS.md`](../../docs/STATUS.md).

**Estado:** en curso
**Creado:** 2026-09-22
**Precondiciones cumplidas:** puerto de lectura (`70685f3`) y credencial de
acceso (`5b1be50`). Lo difícil ya está.

## Objetivo

Que alguien de CoreWork le pida el tablero a Leda por Telegram, reciba su
enlace, lo abra, y vea el estado de su espacio. Punta a punta.

Feo está permitido. Incompleto, no: lo que muestre tiene que ser cierto.

## Qué dejó de ser necesario

El foco es que funcione bien para el primer cliente, no vender al segundo. Eso
saca dos unidades enteras del camino por ahora:

- **La entrevista de alta.** CoreWork ya está configurado.
- **El panel de plataforma con contraseña y TOTP.** Decidido y registrado en
  `docs/decisions/0004-dos-superficies-separadas.md`; se construye cuando
  aparezca el segundo cliente.

## Alcance

**Incluido:** los endpoints HTTP que validan el token y sirven las seis
consultas del puerto de lectura, y una pantalla que las muestre.

**Excluido de esta unidad:** editar configuración desde el tablero. Es real y
está decidido, pero exige el rastro de auditoría por cambio y conviene hacerlo
como unidad propia, con sus pruebas. Primero que se pueda mirar.

## Lo que el tablero no va a poder mostrar, y por qué

La auditoría dejó esto expuesto. Conviene decirlo acá para que nadie lo lea
como un defecto de la pantalla:

| Ausente | Causa |
|---|---|
| Dependencias entre tareas | `dependency.destino_task_id` existe y nadie lo escribe |
| Subtareas | `task.parent_task_id` existe y nadie lo escribe |
| Prioridad | `task.prioridad` existe y nadie lo escribe; toda tarea la tiene nula |
| Cierre de bloqueos | `blocker.resolucion` existe y nadie lo escribe: hoy un bloqueo se abre y no se cierra |

Las cuatro son huecos de coordinación, no del tablero. Son las candidatas
naturales a la unidad siguiente.

## Checklist

- [ ] **T1** — Endpoint que canjea el token por una sesión de lectura y sirve
      las seis consultas. Toda respuesta acotada al espacio del token.
- [ ] **T2** — Pantalla mínima: HTML servido por el mismo proceso, sin
      construcción de front. Legible en teléfono, que es donde se va a mirar.
- [ ] **T3** — Herramienta de Telegram para pedir el enlace, entregado sólo por
      privado.
- [ ] **T4** — Pruebas: token inválido o vencido rechazado, ninguna respuesta
      con datos de otro espacio, el enlace no sale por el grupo.
- [ ] **T5** — `frontera.md`: el adaptador del tablero de cliente pasa a
      existir, con su alcance real.

## Criterios de aceptación

1. El circuito completo funciona: pedir, recibir, abrir, ver.
2. Ninguna respuesta incluye datos de otro espacio, con prueba.
3. Un token vencido o inválido no sirve, con prueba.
4. El enlace nunca se entrega en un chat grupal, con prueba.
5. La pantalla no afirma nada que el dato no sostenga: si algo está vacío
   porque la capacidad no existe, lo dice en vez de mostrar un cero que parece
   un dato.
6. La suite completa sigue en verde.

El criterio 5 importa más de lo que parece. Un tablero que muestra "0
dependencias" cuando en realidad no se pueden crear dependencias está
mintiendo con un número.

## Verificación aplicable

TDD habilitado. Runner: `.venv/Scripts/python.exe -m pytest -q`.

## Progreso

- 2026-09-22 — Documento creado. Ninguna tarea cerrada.

## Próximo paso

T1 y T4 juntas: el endpoint con sus pruebas de aislamiento.
