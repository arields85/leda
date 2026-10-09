# El Motor

**Rama:** `feat/motor-de-conversacion` · **Carpeta:** `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`
**Abierta:** 2026-10-04 · **Copia en Engram:** tema `odd/motor-de-conversacion/tasks` (proyecto `prisma-pm`)

Documento de la unidad, reducido a lo que sirve en cada inicio (2026-10-09). La historia de las etapas 0 a
3, con sus tareas, su evidencia y lo que se trajo de la rama congelada, está literal en
[`docs/historial/motor-de-conversacion-hasta-fase-c.md`](../../docs/historial/motor-de-conversacion-hasta-fase-c.md)
y, hasta M1, en [`motor-de-conversacion-hasta-M1.md`](../../docs/historial/motor-de-conversacion-hasta-M1.md).
Las decisiones duraderas están en los ADR [0017](../../docs/decisions/0017-por-chat-los-hechos-por-la-web-la-estructura.md),
[0018](../../docs/decisions/0018-motor-de-conversacion.md) y 0019; las pruebas reales, en la bitácora de flujos.

## Objetivo

Que Leda converse sobre el seguimiento del trabajo sin perderse ni trabarse, con un motor de conversación chico,
propio y único, apoyado sólo en la capa sólida (base, garantías, operaciones del dominio, salida y auditoría).

## Por qué existe

La conversación eran unas 16.000 líneas escritas a mano por situación, sin un modelo de la conversación, con
tres flujos conviviendo y pruebas que miraban el código. El 2026-10-04 la prueba real volvió a fallar con la
misma clase de falla y el usuario frenó el parcheo (análisis en `docs/research/`).

## Decisiones del usuario que le dan origen (2026-10-04)

1. Motor chico de conversación dentro de Leda, sin marcos de terceros; Engram sólo como referencia.
2. Tres partes: estado exacto, registro completo de la conversación (con los toques) y memoria (después, con su
   ADR).
3. *Por chat, hechos del trabajo; por la web, su estructura.* Leda no crea tareas ni objetivos por chat; las
   carga el administrador en la plataforma web, con su propio ADR (ADR 0017, decisiones 2 y 5). Delegar por
   chat entró con la enmienda a la decisión 2 (2026-10-09).
4. Los flujos A, B y C1 a C6 quedaron congelados en `respaldo-flujos-antes-de-d`.
5. Los botones son atajos (ADR 0018, decisión 2) y un tema a la vez (decisión 4).

## Etapas

| Etapa | Qué | Terminó |
|---|---|---|
| 1 | Diseño: ADR 0017 y 0018, conversaciones de prueba | M1, 2026-10-04 |
| 2 | Prueba chica y descartable, por Telegram real | M2, 2026-10-06 |
| 3 | Motor definitivo en `src/leda/motor/`, flujos A y B borrados, garantías en verde | M3, 2026-10-07 (`odd/tasks/motor-definitivo.md`) |

## Próximo paso

Las tres etapas terminaron. Sigue la **Fase C** (lo que a Leda le falta por chat), con su plan en
[`fase-c.md`](fase-c.md), y después la plataforma web. El punto exacto para retomar está en `docs/STATUS.md`.
