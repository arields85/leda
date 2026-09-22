# Continuidad de trabajo en Prisma

Este archivo es el punto de entrada para futuras sesiones. Prisma se endurece y
extiende sobre la arquitectura actual; no se reestructura ni reescribe sin una
decisión explícita y documentada.

> **Este archivo es la fuente única de estas instrucciones.** `CLAUDE.md`
> contiene sólo `@AGENTS.md`, que las importa. Claude Code lee `AGENTS.md` de
> forma nativa, pero esa lectura depende de un indicador remoto y no se activa
> en Bedrock o Vertex, con telemetría deshabilitada, ni en la primera sesión
> posterior a una instalación o actualización; la importación funciona siempre.
> Editar siempre este archivo, nunca `CLAUDE.md`.

## Orden de lectura

1. Leer `docs/product/que-es-prisma.md` para conocer qué es el producto y qué es
   configuración de cada cliente.
2. Leer `docs/architecture/frontera.md` para conocer dónde termina el núcleo y qué
   reglas lo gobiernan.
3. Leer `docs/STATUS.md` para conocer estado, riesgos y próximo paso.
4. Leer `docs/ROADMAP.md` para conocer el orden de trabajo vigente.
5. Leer `docs/INDEX.md` para elegir sólo el detalle necesario.
6. Leer los ADR aplicables antes de cambiar dominio o arquitectura.
7. Contrastar cualquier afirmación con código, esquema y pruebas actuales.

No leer archivos `.env*`, salvo `.env.ejemplo` cuando sea necesario revisar la
plantilla pública. Nunca mostrar secretos, tokens, credenciales, URLs privadas ni
contenido sensible de conversaciones.

## Fuentes de verdad

Orden de autoridad para describir lo que existe hoy:

1. `db/esquema.sql` y `src/prisma/`: comportamiento implementado.
2. `tests/` y `db/pruebas.sql`: comportamiento comprobado por pruebas, sólo si la
   ejecución y su resultado están registrados.
3. `docs/architecture/frontera.md`: gobierna la arquitectura. Ante una discrepancia
   entre documentos de arquitectura, prevalece esta frontera.
4. `docs/product/que-es-prisma.md`: define el producto y qué es configuración de cada
   cliente frente a núcleo.
5. `docs/decisions/`: decisiones aceptadas que gobiernan cambios futuros, salvo las
   marcadas como superadas.
6. `docs/STATUS.md` y `docs/ROADMAP.md`: estado y orden de trabajo vigentes.
7. `README.md`, `PRUEBA-LOCAL.md` y `nucleo/`: guía operativa y reglas existentes;
   deben contrastarse con la implementación si hay discrepancias.

`docs/product/functional-specification.md` quedó superada por el cambio de alcance a
producto multi-tenant. Se conserva como insumo histórico y no describe el alcance
vigente; contrastarla contra la frontera antes de usar cualquier parte.

Una especificación expresa intención, no prueba implementación. Un test existente
no prueba que la suite pase hasta ejecutarlo.

## Invariantes vigentes

- El aislamiento entre clientes es la garantía número uno del producto. Ninguna tabla
  con alcance de espacio queda sin `workspace_id` ni sin `row level security` forzado,
  y ninguna función `security definer` queda sin propietario explícito y verificado.
- PostgreSQL es la fuente oficial del estado operativo.
- La conversación y la memoria ayudan a interpretar; no reemplazan una lectura
  vigente ni conceden autoridad.
- El modelo sólo actúa mediante herramientas autorizadas del servidor.
- Los efectos relevantes requieren validación, confirmación cuando corresponda,
  ejecución única, verificación y auditoría.
- El aislamiento entre espacios no debe depender de recordar un filtro manual.
- Los mensajes visibles salen por outbox; el ACK técnico de Telegram es la
  excepción acotada existente.
- Una solicitud incompleta es un borrador sin efectos.
- Una tarea comprometida exige objetivo, responsable, fecha objetivo, criterio de
  aceptación y política de evidencia.
- La conversión de borrador a tarea es explícita, confirmada y auditable.
- Actualización, evidencia, aprobación y cierre son hechos distintos.
- No poder consultar datos no equivale a que no existan.

## Límites de alcance

El producto conserva un monolito modular en Python y PostgreSQL.

Fuera del producto por ahora. No construir sin una decisión explícita y documentada:

- agenda o calendarios externos;
- aprendizaje persistente;
- motor genérico de workflows;
- microservicios;
- interfaz administrativa completa.

Dentro del producto pero todavía no: la API de lectura y el dashboard pertenecen al
producto y están ordenados en `docs/ROADMAP.md`. No se construyen todavía porque
tienen precondiciones —cierre del aislamiento entre clientes y desacople del
transporte—, no porque estén fuera de alcance. Aplicar el orden del roadmap, no
tratarlos como prohibidos.

No cambiar lógica, esquema, dependencias o arquitectura durante trabajo puramente
documental. No reestructurar carpetas o módulos sin un ADR aceptado.

## Comandos verificados por inspección

Estos comandos existen en `README.md`, `PRUEBA-LOCAL.md`, `pyproject.toml` o
`src/prisma/cli.py`. Su disponibilidad fue inspeccionada; su resultado actual no
se presume.

```bash
docker compose up -d postgres
python -m prisma esquema
python -m prisma importar corework
python -m prisma importar corework --activar
python -m prisma feriados corework
python -m prisma enlaces corework --solo <nombres>
python -m prisma escuchar corework
python -m prisma estado corework
python -m prisma correr corework <cadencia>
python -m prisma escalera corework
python -m prisma despachar corework
python -m prisma incidentes corework
python -m prisma servir --puerto 8080
python -m pytest
```

`python -m prisma esquema --recrear` borra los datos. No ejecutarlo sin una
autorización explícita y un entorno descartable confirmado.

## Reglas de seguridad

- No leer, imprimir, versionar ni incluir en diagnósticos archivos `.env*`, salvo
  la plantilla permitida `.env.ejemplo`.
- No inspeccionar untracked antes de asegurar las exclusiones sensibles en
  `.gitignore`.
- No ejecutar SQL destructivo, pruebas contra una base no confirmada como
  descartable ni comandos de despliegue sin autorización.
- No registrar cuerpos de conversaciones ni errores crudos en documentación.
- No afirmar que una prueba, restore, backup o rollback funciona sin evidencia de
  una ejecución registrada.
- No hacer commits, cambiar configuración Git o agregar archivos al índice salvo
  pedido explícito.

## Cómo trabajar y registrar continuidad

Antes de implementar una fase:

1. Confirmar que `docs/STATUS.md` sigue vigente contra el repositorio.
2. Elegir el menor circuito útil de extremo a extremo que pruebe comprensión,
   respuesta, coordinación o reducción de carga humana.
3. Resolver sólo las decisiones y guardas que bloquean ese circuito; no adelantar
   hardening de producción sin evidencia.
4. Mantener comportamiento, verificación focalizada, replay/regresión y documentación
   de esa unidad juntos.
5. Registrar comando, resultado exacto, escenario operativo y límite de rollback.

Al terminar una unidad:

- actualizar `docs/STATUS.md` con hechos comprobados, riesgos y próximo paso;
- marcar una prueba como ejecutada sólo con comando, fecha y resultado;
- después de la verificación técnica, evaluar el gate de sesión progresiva del
  protocolo canónico; si el circuito es elegible, programar su prueba por Telegram
  real con datos ficticios sin esperar a completar las Fases 1-4; si no lo es, usar
  harness determinista o `TestClient` y registrar la condición pendiente;
- comprobar como mínimo workspace local o de prueba controlado, ausencia de datos y
  trabajo real, secreto de Telegram protegido, efectos inspeccionables y reversibles,
  backup, pausa o rollback proporcionado, ninguna operación destructiva y cero
  `CRITICAL` o `HIGH` abiertos en el circuito;
- inspeccionar respuesta visible, PostgreSQL, herramientas/efectos y
  auditoría/historia; corregir la causa raíz observada y agregar replay/regresión antes
  de reanudar;
- si el comportamiento es aceptable, elegir el siguiente circuito pequeño y endurecer
  proporcionalmente según evidencia;
- actualizar `docs/ROADMAP.md` sólo si cambió la secuencia o el criterio de salida;
- crear un ADR numerado para decisiones de dominio o arquitectura duraderas;
- no borrar decisiones anteriores: registrar si una nueva las reemplaza.

La sesión progresiva aporta evidencia de desarrollo y regresión, pero no aprueba el
piloto ni usa el holdout. Registrar su resultado en continuidad sólo cuando cambie un
hecho relevante; no editar documentación únicamente para dejar constancia de que se
evaluó el gate.

ADR 0003 quedó superada por el cambio de alcance a producto multi-tenant y está
marcada como tal. Su modelo de amenaza fue escrito cuando la amenaza principal era el
compromiso de la credencial de aplicación dentro de un solo equipo; en un producto
multi-tenant la amenaza principal es el cruce entre clientes. No se borra ni se
implementa en su secuencia original.

Su Corte 0 —el catálogo ejecutable de propietarios, membresías, grants y ACL— deja de
estar diferido: es insumo urgente de la unidad de cierre del aislamiento entre
clientes de `docs/ROADMAP.md`, porque es el control que habría detectado que las
tablas de eventos de estado reciben `grant insert` sin `workspace_id` ni RLS. Los
controles avanzados de privacidad y producción permanecen en el horizonte posterior
del roadmap.

Antes de cerrar una sesión, y después de su última modificación, operación o commit,
contrastar `docs/STATUS.md` y los documentos de continuidad afectados con el estado
actual de Git, código, esquema, pruebas y operación. Si cambió un hecho relevante,
actualizar los documentos correspondientes antes del cierre; si no cambió, no editar
documentación sólo para registrar la sesión.

Usar `PENDIENTE` para datos aún no comprobados o decisiones abiertas. No convertir
hipótesis, recomendaciones ni contenido del roadmap en estado implementado.
