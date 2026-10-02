# ADR 0012: Ruteo en paralelo con la primera respuesta

- **Estado:** revertida el 2026-09-29 (ver "Reversión" al final); aceptada el 2026-09-28
- **Fecha:** 2026-09-28
- **Alcance:** `src/leda/agente.py` (`preparar`, `Especulacion`, `especular`,
  `responder`); `src/leda/gateway.py` (`_turno`, `_avanzar_aclaracion`);
  `src/leda/llm.py` (`admite_especulacion`); `tests/banco/corrida.py`
  (`ProveedorGrabador`); `tests/test_especulacion.py` (nuevo).
- **Evidencia:** banco real con `nan/deepseek-v4-flash`, 2026-09-28 (T8b y
  T8c-1 en `odd/tasks/leda-orienta.md`): 29 de 36 escenarios rutean a
  conversación normal; el ruteo tarda ~2,5 s de mediana y la primera llamada
  del responder ~3,6 s; NaN admite 7 pedidos concurrentes. Lectura del código
  de `gateway._turno` y `agente.responder`.

## Contexto

Un turno de texto hace hoy, en serie: ruteo tipado (`route_intent`, hasta dos
intentos), resolución de referencias a tareas y, en el caso simple, el ciclo
del responder. T8c-1 ya cortó la última llamada del ciclo cuando la vuelta
deja algo pendiente; queda la espera inicial: en 29 de 36 escenarios el ruteo
elige conversación normal y el responder arranca recién cuando termina.

Verificado por lectura del código: sin corrección abierta, con ruteo a
conversación normal y sin referencias que resolver (sin bloque de contexto,
sin tareas resueltas, sin preguntas por botón), lo que el responder le manda
al modelo (`sistema`, `mensajes`, `esquemas`) no depende del resultado del
ruteo. Su primera llamada puede correr a la vez que el ruteo y ahorrar
aproximadamente `min(ruteo, primera llamada)`, unos 2,5 s por turno de ese tipo.

## Decisión

1. **Llamada especulativa sólo en el caso simple.** En `_turno`, si no hay
   corrección abierta (`modificacion is None`) y el proveedor lo declara
   (`admite_especulacion`), la primera llamada del responder arranca en un
   hilo trabajador a la vez que el ruteo.
2. **La preparación se separa del ciclo.** `agente.preparar` hace las lecturas
   de la base (contexto, historial) y arma `sistema`, `mensajes` y `esquemas`
   en el hilo principal. La misma `Preparacion` alimenta la llamada
   especulativa y, si se usa, el ciclo de `responder`: mandan exactamente lo
   mismo por construcción, con el mismo `ahora`.
3. **Nada de base fuera del hilo principal.** El trabajador recibe datos ya
   preparados (texto, listas, esquemas) y sólo llama a `proveedor.responder`;
   nunca toca el cursor, la cola ni Telegram. Los hilos salen de un
   `ThreadPoolExecutor` de módulo, acotado a 4.
4. **Cuándo se usa y cuándo se descarta.** Se usa únicamente si el ruteo tuvo
   éxito, eligió conversación normal y la resolución de referencias no produjo
   nada (sin bloque, sin tareas resueltas claras, sin preguntas por botón).
   Entonces la primera vuelta del ciclo toma el resultado del futuro en vez de
   llamar al modelo; si el futuro falló, la excepción se relanza dentro del
   mismo `try` del ciclo: mismo incidente y misma disculpa que hoy. En
   cualquier otro caso (alta guiada, referencias, botones de aclaración, falla
   del ruteo) se descarta: su resultado no se usa nunca y no escribe nada; la
   llamada puede terminar en segundo plano.
5. **Opt-in por proveedor.** `ProveedorCompatible`, `ProveedorGemini` y
   `ProveedorAnthropic` lo declaran (HTTP puro, cliente seguro entre hilos).
   `ProveedorGuionado` no, salvo que un constructor lo pida: las pruebas y los
   replays deterministas siguen llamando en serie.
6. **El grabador del banco no graba lo descartado.** `ProveedorGrabador`
   reenvía la bandera del proveedor interno y expone
   `descartar_respuesta(respuesta)`; la `Especulacion` lo llama (vía
   `getattr`, no-op si falta) cuando descarta una llamada, y el grabador
   quita esa entrada exacta de `respuestas`. Un replay no especula, así que
   consumiría una respuesta que nunca debió existir. `a_json` espera
   (acotado) a las llamadas en vuelo antes de serializar.

## Consecuencias

- Los turnos de alta guiada, con referencias o con falla de ruteo gastan una
  llamada al modelo que se descarta (tokens y una de las 7 conexiones de NaN
  durante unos segundos). Es el costo aceptado por adelantar el caso
  dominante; el ruteo y el responder concurrentes usan a lo sumo 2 conexiones
  por turno.
- El orden de las llamadas ya no es determinista con proveedores reales; los
  replays lo conservan porque el guionado no especula y el grabador retira
  lo descartado. Queda una ventana mínima entre el fin de la llamada y el
  aviso de descarte: `a_json` sólo la cubre si la llamada sigue en vuelo.
- Un error SQL al preparar (contexto, historial) ahora ocurre antes del
  ruteo, también en turnos que no lo necesitarían; sin corrección abierta el
  camino normal hace las mismas lecturas de todos modos.
- La primera llamada especulativa no se cancela (una petición HTTP en curso no
  es interrumpible de forma segura); su costo lo paga el descarte.

## Alternativas consideradas

- **Especular también con corrección abierta o referencias.** Rechazada: el
  contexto depende del resultado del ruteo o de Jev, así que casi siempre se
  descartaría.
- **Descartar esperando al trabajador.** Rechazada: agregaría al turno de alta
  guiada justo la espera que esta unidad quiere quitar.
- **Preparar dentro del trabajador.** Rechazada: un cursor de psycopg no puede
  usarse desde otro hilo.

## Reversión (2026-09-29)

El código de esta decisión (commit `46278f3`) se revirtió por decisión del usuario,
con esta evidencia del banco real (`nan/deepseek-v4-flash`):

- **Alcance real menor al supuesto.** La especulación sólo se usa cuando el ruteo elige
  conversación normal *y* el mensaje no nombra ninguna tarea: 10 de 36 escenarios. En
  22 se descarta, porque la mayoría de los mensajes nombra una tarea y eso pasa por
  Jev. La cifra de "29 de 36" del contexto no contaba las referencias.
- **Ganancia chica.** Comparación A/B con el mismo código (especulación apagada y
  encendida), 10 escenarios elegibles x 3 corridas: tiempo de pared mediano 9,9 s
  apagada y 9,4 s encendida; diferencia mediana por escenario -1,1 s. Sobre todos los
  turnos, unos -0,3 s en promedio.
- **Más cuelgues largos con pedidos simultáneos (indicio).** NaN cuelga a veces un
  pedido unos 93-95 s. En serie: 5 de 385 llamadas (~1,3 %); con especulación: 7 de
  180 (~3,9 %). La muestra es chica, pero combinado con los avisos de la revisión
  `review-31b767dbe1a4c1f6` (una llamada descartada colgada ocupa un hilo del pool
  compartido; la especulación usada puede quedar en cola detrás) el riesgo no compensa
  la ganancia.

En su lugar se acota el tiempo de cada llamada al modelo con reintento (T8c-4 en
`odd/tasks/leda-orienta.md`), que ataca directamente los turnos de más de 90 s.
Esta decisión queda como registro: si en el futuro los turnos sin referencias
dominaran o el proveedor no tuviera cuelgues, se puede reconsiderar con esta
evidencia.
