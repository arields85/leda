# Continuidad de trabajo en Prisma

Este archivo es el punto de entrada para futuras sesiones. Prisma se endurece y
extiende sobre la arquitectura actual; no se reestructura ni reescribe sin una
decisión explícita y documentada.

## Orden de lectura

1. Leer `docs/STATUS.md` para conocer fase, riesgos y próximo paso.
2. Leer `docs/INDEX.md` para elegir sólo el detalle necesario.
3. Leer `docs/ROADMAP.md` y el documento de la fase activa.
4. Leer los ADR aplicables antes de cambiar dominio o arquitectura.
5. Contrastar cualquier afirmación con código, esquema y pruebas actuales.

No leer archivos `.env*`, salvo `.env.ejemplo` cuando sea necesario revisar la
plantilla pública. Nunca mostrar secretos, tokens, credenciales, URLs privadas ni
contenido sensible de conversaciones.

## Fuentes de verdad

Orden de autoridad para describir lo que existe hoy:

1. `db/esquema.sql` y `src/prisma/`: comportamiento implementado.
2. `tests/` y `db/pruebas.sql`: comportamiento comprobado por pruebas, sólo si la
   ejecución y su resultado están registrados.
3. `docs/decisions/`: decisiones aceptadas que gobiernan cambios futuros.
4. `docs/STATUS.md` y `docs/ROADMAP.md`: estado y secuencia de trabajo vigentes.
5. `docs/product/functional-specification.md`: visión funcional general.
6. `README.md`, `PRUEBA-LOCAL.md` y `nucleo/`: guía operativa y reglas existentes;
   deben contrastarse con la implementación si hay discrepancias.

Una especificación expresa intención, no prueba implementación. Un test existente
no prueba que la suite pase hasta ejecutarlo.

## Invariantes vigentes

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

La fase actual conserva un monolito modular en Python y PostgreSQL. No construir
ahora:

- interfaz administrativa completa;
- dashboard avanzado;
- agenda o calendarios externos;
- aprendizaje persistente;
- motor genérico de workflows;
- microservicios.

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
2. Resolver las decisiones bloqueantes del documento de fase.
3. Elegir una unidad de trabajo revisable de principio a fin.
4. Mantener comportamiento, pruebas y documentación de esa unidad juntos.
5. Registrar comando, resultado exacto, escenario operativo y límite de rollback.

Al terminar una unidad:

- actualizar `docs/STATUS.md` con hechos comprobados, riesgos y próximo paso;
- marcar una prueba como ejecutada sólo con comando, fecha y resultado;
- actualizar `docs/ROADMAP.md` sólo si cambió la secuencia o el criterio de salida;
- crear un ADR numerado para decisiones de dominio o arquitectura duraderas;
- no borrar decisiones anteriores: registrar si una nueva las reemplaza.

Usar `PENDIENTE` para datos aún no comprobados o decisiones abiertas. No convertir
hipótesis, recomendaciones ni contenido del roadmap en estado implementado.
