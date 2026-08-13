# Plantilla de manifiesto del corpus de validación

Esta plantilla registra únicamente metadatos, cobertura y resultados agregados. El
holdout no se almacena en este archivo, en el repositorio ni en Engram. No incluir
escenarios, prompts, mensajes, respuestas esperadas, evidencia literal, secretos ni
contenido de trabajo real.

## Identificación

| Campo | Valor |
|---|---|
| Versión del manifiesto | `PENDIENTE` |
| Fecha de actualización | `AAAA-MM-DD` |
| Responsable del registro | `PENDIENTE` |
| Versión del corpus de desarrollo | `PENDIENTE` |
| Versión opaca del holdout | `PENDIENTE` |

## Custodia y separación

| Control | Registro |
|---|---|
| Corpus de desarrollo versionado en el repositorio | `SÍ / NO` |
| Holdout fuera del repositorio | `SÍ / NO` |
| Holdout fuera de Engram | `SÍ / NO` |
| Custodio humano del holdout | `PENDIENTE` |
| Revelación limitada al momento de ejecución | `SÍ / NO` |
| Escritores/correctores sin acceso a contenido ni resultados esperados | `SÍ / NO` |
| Contaminación conocida | `NINGUNA / REGISTRADA FUERA DE ESTE MANIFIESTO` |

## Cobertura agregada

No incluir IDs de casos, frases ni detalles que permitan reconstruir el holdout.

| Capacidad o riesgo | Escenarios base | Variantes humanas | Replays | Casos críticos holdout | Observaciones de cobertura |
|---|---:|---:|---:|---:|---|
| `PENDIENTE` | 0 | 0 | 0 | 0 | `PENDIENTE` |

## Ejecuciones agregadas

| Fecha | Versión desarrollo | Versión opaca holdout | Cobertura ejecutada | Resultado agregado | Críticos aprobados | Fallos altos abiertos | Patrón repetido | Baseline operativa |
|---|---|---|---|---|---|---|---|---|
| `AAAA-MM-DD` | `PENDIENTE` | `PENDIENTE` | `PENDIENTE` | `PENDIENTE` | `SÍ / NO` | `SÍ / NO` | `SÍ / NO` | `latencia / costo / duplicados / omisiones / intervención manual` |

## Renovación

| Campo | Valor |
|---|---|
| Última renovación | `AAAA-MM-DD / NO APLICA` |
| Motivo | `contaminación / cambio importante de capacidades / cambio de proveedor / pérdida de representatividad / otro` |
| Casos contaminados transferidos a desarrollo | `cantidad agregada` |
| Reemplazos no derivados de la misma frase | `cantidad agregada` |
| Próxima revisión | `AAAA-MM-DD / por evento` |

## Confirmación

- [ ] El manifiesto contiene sólo metadatos, cobertura y resultados agregados.
- [ ] El holdout permanece bajo custodia del usuario y fuera del repositorio y Engram.
- [ ] Ningún dato registrado permite reconstruir escenarios o resultados esperados.
- [ ] Los casos usados para diagnóstico dejaron el holdout y fueron reemplazados.
