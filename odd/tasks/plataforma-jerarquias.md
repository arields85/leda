# La plataforma según la jerarquía del equipo (ADR 0023)

**Rama:** `feat/motor-de-conversacion` · **Abierta:** 2026-10-13 · **Copia en Engram:** tema
`odd/plataforma-jerarquias/tasks` (proyecto `prisma-pm`)

## Objetivo

Construir lo que decidió el usuario en el [ADR 0023](../../docs/decisions/0023-quien-crea-en-la-plataforma.md)
(aceptado el 2026-10-13), junto con las dos porciones que el [ADR 0022](../../docs/decisions/0022-plataforma-web-de-tareas.md)
tenía pendientes: que cada uno cree en la web lo que le toca según su lugar en el equipo, y que Leda ayude a
completarlo.

## Por qué

Hoy sólo la puerta de administración carga tareas, los objetivos y las jerarquías salen del pack, y "quién la
decidió" es un campo libre. El usuario quiere que se sepa por qué algo se atrasa (el módem en la pared → el
estante → los tornillos) y que el equipo se organice solo.

## Restricciones

- Cada porción con su diseño corto, test primero (RED → GREEN), sus garantías, revisión RDD por commit y su
  prueba real en el celular antes de la siguiente (ADR 0022, decisión 16). La prueba en el celular necesita al
  usuario y el túnel (`cloudflared`, autorizado para probar).
- Migraciones desde la `0067`, cada una con su rollback y su ensayo de paridad; `leda_motor` con respaldo
  previo (autorizado).
- Por chat no se crea nada (ADR 0017; anotado para más adelante en `docs/ROADMAP.md`).
- No tocar `nucleo/`. Las garantías de la mecánica las exige el código.

## Orden de las porciones (acordado con el usuario, 2026-10-13: "si")

1. **Las esperas en el formulario** (0023, decisión 2).
2. **Los objetivos desde la web** (0023, decisión 1; tipo según dónde cuelga, punto 11).
3. **La carga por la web del equipo para Dirección y los referentes** (0023, decisión 3, puntos 2, 7 y 8), con
   el préstamo de personas.
4. **El pedido de más tiempo y el cambio de fecha** (0022, porción 3, decisión 8).
5. **La propuesta del integrante con la ayuda de la IA** (0023, decisión 3, puntos 3 a 6 y 9).
6. **Las jerarquías y los integrantes desde la web de Dirección** (0023, decisiones 4 y 5, puntos 1 y 10; con
   la porción 4 del 0022).

## Tareas

Ruta: cada porción, delegada (un escritor), porque toca base, servidor, web y pruebas.

### J1 · Las esperas en el formulario

- [ ] **J1-1 · Mapa y diseño corto:** cómo carga hoy el formulario (`web/src/admin/LoadForm.tsx`, la API de
      carga, `dependency` y `evitar_ciclo_dependencia`), y qué cambia; escrito acá.
- [ ] **J1-2 · Las garantías, primero en rojo:** no se elige una tarea de otro espacio ni una cerrada; un ciclo
      se rechaza con su motivo; la tarea que espera no pasa a en curso mientras la otra no terminó; la
      auditoría lo guarda.
- [ ] **J1-3 · El servidor y la web:** el campo opcional "espera a" en el formulario y la carga.
- [ ] **J1-4 · Verificación:** `pytest tests/garantias`, las pruebas de la carga, `npm test` y `npm run build`
      en `web/`; revisión RDD por commit.
- [ ] **J1-5 · Prueba real en el celular** (con el usuario).

### J2 a J6

Se detallan al llegar a cada una, con su diseño corto.

- [ ] **J2 · Los objetivos desde la web.**
- [ ] **J3 · La carga por la web del equipo (Dirección y referentes), con el préstamo.**
- [ ] **J4 · El pedido de más tiempo y el cambio de fecha.**
- [ ] **J5 · La propuesta del integrante con la IA.**
- [ ] **J6 · Las jerarquías y los integrantes desde la web de Dirección.**

## Criterio de aceptación

Cada porción: sus garantías en verde, `tests/garantias` completa en verde, cada commit de código revisado por
RDD y la prueba del usuario en el celular. Al final, el ejemplo del usuario de punta a punta: Dirección crea
el objetivo del módem, el referente la tarea del estante, el integrante propone los tornillos con la ayuda de
Leda, quien revisa la aprueba y el atraso se explica por la espera.

## Entrega

Una sola rama, como hasta ahora: commits por unidad en `feat/motor-de-conversacion`, subida al cerrar cada
tramo (autorizado); `main` por avance rápido, cuando lo decida el usuario. Previsión: más de 400 líneas por
porción en las 3, 5 y 6; se revisan por tramos con RDD.

## Progreso y evidencia

- 2026-10-13: el usuario aceptó el ADR 0023 y este orden; documento creado.
