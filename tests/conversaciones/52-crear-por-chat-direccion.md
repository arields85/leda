# 52. Crear por chat: Dirección

**Qué prueba:** Ismael (Dirección) escribe que quiere crear una tarea y, más tarde, un objetivo. Por
chat no se crea nada: Leda le dice, con sus palabras, que eso se hace en su web, y la respuesta lleva
al final su enlace de entrada (uno por mensaje, como el de `pedir_acceso_web`). El segundo enlace
anula el primero, que no usó. Decisión D12 del usuario (2026-10-14, porción J4b de
`odd/tasks/plataforma-jerarquias.md`); ADR 0017, decisión 2 (por chat, hechos del trabajo; por la
web, su estructura); ADR 0018, decisión 1 (la IA elige la jugada `pedir_crear` de la lista cerrada;
la cocina decide qué corresponde según quién es); constitución §10 (la IA nunca escribe una
dirección).

**Corre** con su YAML, entera. Las del referente y del integrante son la 53 y la 54.

## Estado inicial

- **Día:** D = lunes 19, dentro del horario.
- **Personas:** Ismael, Dirección (la autoridad final del espacio). Ya se le ofreció la web.
- **Tarea:** "Aprobar la compra del servidor nuevo", de Ismael, `asignada`, vence el viernes 23.
  Criterio de aceptación: "La compra del servidor queda aprobada por escrito con su presupuesto".
- **Lo ya enviado:** nada que importe para el hilo.

## Hilo

1. **Ismael** escribe (lunes 19, 10:30): "quiero crear una tarea nueva para lucas, que instale el
   servidor"
   →
   - Jugadas: `pedir_crear`, de una tarea.
   - Efecto: nada se crea; el enlace de entrada de Ismael, emitido al mandar.
   - La respuesta dice: que las tareas se crean en la web y que ahí va su enlace para entrar, que
     sirve una vez y vence en 24 horas. Al final, el enlace, sin vista previa.
   - La respuesta no dice: que creó la tarea, ni una dirección escrita por la IA.

2. **Ismael** escribe (11:00): "y un objetivo nuevo para la ampliación de la planta como lo armo?"
   →
   - Jugadas: `pedir_crear`, de un objetivo.
   - Efecto: un enlace nuevo; el del paso 1, que no usó, queda anulado.
   - La respuesta dice: que el objetivo se crea en la web, que ahí va el enlace nuevo y que el
     anterior ya no sirve.
   - La respuesta no dice: que creó el objetivo, ni una dirección escrita por la IA.

## Qué mide

- **Garantías:** nada se crea por chat; el enlace de entrada sale al final y lo emite el
  despachador; un solo enlace por mensaje; el anterior sin usar deja de servir. No queda el incidente
  de algo fuera de la lista.
- **Comprensión:** la IA elige `pedir_crear` con lo que quiere crear (`tarea` en el paso 1,
  `objetivo` en el 2).
- **Las palabras:** sin nombres del sistema (constitución §10).
