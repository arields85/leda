# 54. Crear por chat: un integrante

**Enmienda (ADR 0024, 2026-10-14):** a un integrante no le sale ningún botón para crear; la
respuesta dice quiénes las cargan, sin decir que por chat no se creó. El YAML es la versión vigente.

**Qué prueba:** Nahuel (de OT, no es referente) quiere crear una tarea y después un objetivo. No
puede crear ninguno de los dos: Leda le dice, sin enlace, que las tareas las cargan su referente
(Marcos) o Dirección (Ismael), y que pronto podrá proponerlas desde su web; con un objetivo, lo
mismo. Por chat no se crea nada. Decisión D12 del usuario (2026-10-14, porción J4b de
`odd/tasks/plataforma-jerarquias.md`; la propuesta del integrante llega con la J6); ADR 0017,
decisión 2; ADR 0018, decisión 1; ADR 0023, decisiones 1 y 3.

**Corre** con su YAML, entera.

## Estado inicial

- **Día:** D = lunes 19, dentro del horario.
- **Personas:** Nahuel, de OT (su trabajo lo aprueba Marcos, el referente de OT); Marcos; Ismael,
  Dirección. A Nahuel ya se le ofreció la web.
- **Tarea:** "Revisar los sensores de la comprimidora", de Nahuel, `asignada`, vence el viernes 23.
  Criterio de aceptación: "Los sensores de la comprimidora miden dentro del rango del fabricante".
- **Lo ya enviado:** nada que importe para el hilo.

## Hilo

1. **Nahuel** escribe (lunes 19, 10:30): "quiero crear una tarea para cambiar el sensor roto"
   →
   - Jugadas: `pedir_crear`, de una tarea.
   - Efecto: ninguno; sin enlace.
   - La respuesta dice: que las tareas las cargan Marcos o Ismael (se las puede pedir a ellos) y que
     pronto va a poder proponerlas desde su web.
   - La respuesta no dice: que creó la tarea, ni que él la puede crear en la web.

2. **Nahuel** escribe (11:00): "y un objetivo? se puede?"
   →
   - Jugadas: `pedir_crear`, de un objetivo.
   - Efecto: ninguno; sin enlace.
   - La respuesta dice: lo mismo, para un objetivo.
   - La respuesta no dice: que creó el objetivo.

## Qué mide

- **Garantías:** nada se crea por chat y a un integrante nunca le sale un enlace para crear.
- **Comprensión:** la IA elige `pedir_crear` con `tarea` en el paso 1 y `objetivo` en el 2.
- **Las palabras:** sin nombres del sistema (constitución §10).
