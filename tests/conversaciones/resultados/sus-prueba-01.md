# Ronda sus-prueba-01

- **Fecha:** 2026-10-07 08:54
- **Commit:** b01ab4d
- **Motor:** leda.motor
- **IA:** chatgpt/gpt-6-sol
- **Veces:** 1
- **Gasto de la etapa:** USD 27.47 de 30
- **Parámetros de la IA:** ninguno (los de omisión)
- **Transcripciones:** [sus-prueba-01-transcripciones.md](sus-prueba-01-transcripciones.md)

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas.

| Conversación | Vez 1 | Garantías | Comprensión (provisional) | Lectura del usuario |
|---|---|---|---|---|
| 01 Arranqué (garantias) | G ok · C FALLA · M FALLA | 1/1 | 0/1 |  |

## Fallas

- **01, vez 1, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "aviso_previo", "tarea": "PLC", "hechos": {"vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}}`; real `[]`
- **01, vez 1, paso 1** [motor] último aviso de Marcos: esperado `"PLC"`; real `null`
- **01, vez 1, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`; real `[]`
- **01, vez 1, paso 2** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **01, vez 1, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **01, vez 1, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`; real `[]`
- **01, vez 1, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "motor_aviso_guardado", "severidad": "media"}]`
- **01, vez 1, paso 4** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "vence": "2026-10-23", "atraso_dias_habiles": 0, "estado": "en_curso", "estado_desde": "2026-10-20"}}`; real `[]`
- **01, vez 1, paso 4** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 01 | 1 | 1024 | 1024 |
| **Todas** | 1 | 1024 | 1024 |

## Costo

- Llamadas a la IA: 8 (0 con el costo estimado); tokens de entrada 0, de salida 0.
- **Total de la ronda: USD 0.0000.**
