# 53. Crear por chat: un referente

**Enmienda (ADR 0024, 2026-10-14; prueba por Telegram de la J4):** en lugar del enlace, la respuesta
del paso 1 lleva el botón "Cargar la tarea", que abre el formulario. En el paso 2, sólo que los
objetivos los crea Dirección (Ismael), sin decir que por chat no se creó. El YAML es la versión
vigente.

**Qué prueba:** Marcos (referente de OT) quiere cargarle una tarea a Nahuel y, después, crear un
objetivo. Una tarea la crea él en su web: la respuesta lleva su enlace de entrada al final. Un
objetivo no: los crea Dirección, y Leda se lo dice nombrando a Ismael, sin enlace. Por chat no se
crea nada. Decisión D12 del usuario (2026-10-14, porción J4b de
`odd/tasks/plataforma-jerarquias.md`; desde la J6, un referente le podrá proponer un objetivo a
Dirección desde su web: hasta entonces, sólo que los crea Dirección); ADR 0017, decisión 2; ADR
0018, decisión 1; ADR 0023, decisiones 1 y 3.

**Corre** con su YAML, entera.

## Estado inicial

- **Día:** D = lunes 19, dentro del horario.
- **Personas:** Marcos, referente de OT (su trabajo lo aprueba Ismael); Nahuel, de OT; Ismael,
  Dirección. A Marcos ya se le ofreció la web.
- **Tarea:** "Programar PLC de la comprimidora", de Marcos, `asignada`, vence el lunes 26. Criterio
  de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
- **Lo ya enviado:** nada que importe para el hilo.

## Hilo

1. **Marcos** escribe (lunes 19, 10:30): "necesito cargarle una tarea a nahuel para que revise los
   sensores"
   →
   - Jugadas: `pedir_crear`, de una tarea.
   - Efecto: nada se crea; el enlace de entrada de Marcos, emitido al mandar.
   - La respuesta dice: que las tareas se cargan en la web y que ahí va su enlace para entrar, que
     sirve una vez y vence en 24 horas. Al final, el enlace.
   - La respuesta no dice: que cargó la tarea, ni una dirección escrita por la IA.

2. **Marcos** escribe (11:00): "y si quiero crear un objetivo para la linea 3?"
   →
   - Jugadas: `pedir_crear`, de un objetivo.
   - Efecto: ninguno; sin enlace.
   - La respuesta dice: que los objetivos los crea Dirección, Ismael.
   - La respuesta no dice: que creó el objetivo, ni que él lo puede crear en la web.

## Qué mide

- **Garantías:** nada se crea por chat; el enlace sale sólo cuando la persona puede crearlo (paso 1)
  y nunca con un objetivo de un referente (paso 2).
- **Comprensión:** la IA elige `pedir_crear` con `tarea` en el paso 1 y `objetivo` en el 2.
- **Las palabras:** sin nombres del sistema (constitución §10).
