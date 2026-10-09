# 31. Pedir el enlace a la página de una tarea

**Qué prueba:** una persona pide por chat el enlace a la página de una tarea y Leda se lo pasa, el
personal, sólo si esa persona puede ver la tarea; si no puede, se lo dice con palabras simples y no
manda ningún enlace. Vale para una tarea suya, para una que no está entre las que Leda le sigue (una
ya terminada, o una de otra persona) y para la autoridad final del espacio, que ve todas. ADR 0019,
decisión 7a ("cualquiera de los que pueden verla, cuando lo pide por chat: una jugada nueva de la
lista cerrada") y 7b (quién la ve); ADR 0018, decisión 1 (la IA elige la jugada; la cocina decide si
vale); constitución §10 (opacidad técnica) y decisión 11 del usuario (2026-10-08: Leda no nombra por
su cuenta a quien aprueba ni al referente). Porción 4 de la C-3, su `PENDIENTE` "pedir el enlace por
chat" (`odd/tasks/fase-c.md`).

**Corre desde su unidad de la C-3** (`odd/tasks/fase-c.md`, "Pedir el enlace por chat"), entera,
con su YAML.

## La regla

1. **Es una jugada de la lista cerrada** (`pedir_enlace`): la IA dice qué tarea nombra la persona,
   por su alias si está en su lista o por cómo la nombró si no está (sus palabras del título y, si lo
   dijo, de quién es). La cocina la busca entre las tareas del espacio, también las terminadas.
2. **Quién puede verla lo decide la base** (`puede_ver_tarea`, ADR 0019, 7b): la persona responsable,
   quien aprueba su trabajo, quien ya decidió sobre esa tarea, el referente del área y la autoridad
   final. El enlace se emite al mandar y la base lo vuelve a comprobar (7a).
3. **Si no puede verla, ningún enlace sale**, y Leda dice que ese no se lo puede pasar: sin nombres
   de la base, sin decir quién sí la ve.

## Estado inicial

- **Día:** D = viernes 23, dentro del horario.
- **Personas:** Marcos (referente de OT; su trabajo lo aprueba Ismael), Ismael (Dirección, la
  autoridad final del espacio), Lucas (su trabajo lo aprueba Martín) y Nahuel (de OT; su trabajo lo
  aprueba Marcos). Ninguno tiene una pregunta de Leda abierta.
- **Tareas:**
  - "Programar PLC de la comprimidora", de Marcos, `en_curso` desde el lunes 19, vence el viernes 30.
    Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
  - "Revisar comunicaciones industriales de la comprimidora", de Marcos, `terminada` desde el
    miércoles 21, vencía el viernes 23. Criterio de aceptación: "Los equipos de la comprimidora se
    comunican con el PLC por la red de planta sin errores durante una hora".
  - "Instalar el servidor de la planta", de Lucas, `en_curso` desde el lunes 19, vence el viernes 30.
    Criterio de aceptación: "El servidor queda en el rack de la planta, con su respaldo diario
    funcionando y probado una vez".
- **Lo ya enviado:** nada que importe para el hilo.

## Hilo

1. **Marcos** escribe (10:30): "me pasas el link de la tarea del plc"
   →
   - Jugadas: `pedir_enlace`, la tarea del PLC.
   - Efecto: ninguno.
   - La respuesta dice: que ahí va el enlace a la página de la tarea del PLC.
   - Al final, el enlace personal a la página de la tarea (lo agrega el código, no la IA).
   - Botones: ninguno.

2. **Ismael** escribe (10:45): "pasame el link de la de comunicaciones de marcos q ya la termino"
   →
   - Jugadas: `pedir_enlace`, nombrada por cómo la dijo (no está en su lista: está terminada y no
     espera su revisión).
   - Efecto: ninguno.
   - La respuesta dice: que ahí va el enlace a la página de la tarea de comunicaciones de Marcos.
   - Al final, el enlace personal a la página de esa tarea.

3. **Ismael** escribe (10:50): "y el de la del servidor de lucas"
   →
   - Jugadas: `pedir_enlace`, nombrada por cómo la dijo. Ismael no aprueba el trabajo de Lucas: la
     ve por ser la autoridad final.
   - Efecto: ninguno.
   - La respuesta dice: que ahí va el enlace a la página de la tarea del servidor.
   - Al final, el enlace personal a la página de esa tarea.

4. **Nahuel** escribe (11:00): "hola leda me pasas el link del plc de marcos? quiero ver como viene"
   →
   - Jugadas: `pedir_enlace`, nombrada por cómo la dijo.
   - Efecto: ninguno; no se emite ningún enlace.
   - La respuesta dice: que el enlace de esa tarea no se lo puede pasar, en palabras simples.
   - La respuesta no dice: quién puede verla; nombres de la base, de funciones o de permisos; que la
     tarea no existe.
   - Sin enlace al final.

## Qué mide

- **Garantías:** el enlace sale sólo para quien puede ver la tarea (pasos 1 a 3) y nunca para quien
  no (paso 4); la IA nunca escribe una dirección; ningún efecto en las tareas.
- **Comprensión:** la IA elige `pedir_enlace` y nombra la tarea por su alias cuando está en la lista
  (paso 1) y por cómo la dijo la persona cuando no está (pasos 2 a 4).
- **Las palabras:** sin nombres del sistema (constitución §10); a Nahuel no se le nombra quién ve la
  tarea (decisión 11).
- **El formato:** el de la conversación 20 en cada mensaje.
