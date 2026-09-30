# ADR 0014: El flujo de un mensaje, con un dueño por etapa

- **Estado:** aceptada (decisión del usuario, 2026-09-30)
- **Fecha:** 2026-09-30
- **Alcance:** el camino de cada mensaje y de cada toque (`gateway`, `llm`, `jev`,
  `agente`, `contexto`, `ingreso_tareas`, `pendientes`, `herramientas`). Amplía el
  ADR 0013; no lo reemplaza.
- **Evidencia:** cuarta ronda por Telegram (R4b-H1 a H7, R4c-H1 a H10 en
  `odd/tasks/prisma-orienta.md`); observación del usuario del 2026-09-30 ("todo es muy
  robótico"); mapa del flujo por lectura de código del 2026-09-30.

## Contexto

La capa de datos funciona: Prisma sabe con quién habla, lee bien el estado y no mezcla
clientes. Pero la conversación se siente robótica, y cada ronda deja hallazgos nuevos
que se corrigen uno por uno. El usuario lo resumió así: estamos parchando, y así se
puede seguir al infinito.

El mapa del código explica por qué. El ADR 0013 declara "el modelo interpreta, el código
garantiza", pero se aplica sólo a una parte del camino:

- **El modelo clasifica el mensaje** contra la pregunta pendiente con una lista cerrada
  de comandos (`llm.py`, `respecto_pendiente`). Esto funciona.
- **Los valores los interpreta el código.** La fecha del alta la leen expresiones
  regulares (`ingreso_tareas.resolve_date`); una elección escrita exige la etiqueta
  exacta (`pendientes.opcion_escrita`, `ingreso_tareas.resolve_typed_choice`). Por eso
  "4de octubre" se rechaza y "revisar el variador" recibe "No encontré esa opción". La
  fecha que el modelo propone se descarta sin avisar si el código no la entiende.
- **La respuesta la redacta el modelo sin hechos cerrados, y el código la corrige
  después**: nombrar títulos, anteponer "sin cambios", reescribir si afirmó un cambio
  que no ocurrió (`agente.py`). El código parcha al modelo en vez de darle los hechos.
  De ahí salen respuestas falsas como "No puedo mostrarte la evidencia" (R4c-H3).
- **Varias decisiones tienen más de un dueño.** Las referencias a tareas las separa el
  modelo, las filtra una lista de estados en código y las resuelve Jev. Si una
  pregunta lleva botones lo decide una expresión regular sobre el texto del modelo
  (`deteccion_pregunta.hace_pregunta`), además de la herramienta `ofrecer_opciones`.
- **El rol de Jev no está declarado donde manda.** El ADR 0006 le asigna la duda de
  intención, pero el código sólo lo usa para referencias a tareas; ni
  `architecture/frontera.md` ni `nucleo/` lo mencionan.

Cada hallazgo nuevo cae en uno de estos huecos. Mientras el flujo no diga quién decide
cada cosa, cada corrección es un parche en el lugar donde se vio la falla.

## Decisión

Cada mensaje recorre seis etapas. Cada etapa tiene **un solo dueño**, y ninguna otra
pieza decide lo que le toca a ese dueño.

1. **Contexto (PostgreSQL).** Se lee el estado del trabajo (quién escribe, sus tareas,
   sus estados, quién aprueba, la evidencia), el estado de la conversación (la rama
   abierta, la pregunta pendiente, las opciones ofrecidas, los borradores y las vistas
   previas) y el historial reciente de lo que efectivamente se dijo (lo que la persona
   escribió y lo que Prisma envió, no lo que quedó en la cola). PostgreSQL guarda y
   entrega; quien comprende la conversación es el modelo (etapa 2). Nadie supone nada
   que no se leyó, ni siquiera qué se le preguntó recién a la persona.
2. **Interpretar (modelo).** El modelo devuelve el comando, de la lista cerrada del
   ADR 0013, **y los valores normalizados** que el mensaje trae para la pregunta
   pendiente: una fecha en formato ISO, la opción elegida por su identificador entre
   las ofrecidas (o "ninguna"), el texto de un motivo o de una evidencia tal como la
   persona lo quiso decir. El modelo nunca decide un efecto.
3. **Decidir con duda (Jev).** Cuando el mensaje apunta a algo de la base que no está
   entre las opciones ofrecidas (una tarea, una persona, un objetivo), Jev elige entre
   los candidatos con probabilidades, y el código aplica los cortes (clara, ambigua,
   ninguna). Con una opción ofrecida en pantalla decide el modelo (etapa 2); con un
   candidato de la base decide Jev.
4. **Garantizar (código).** El código valida los valores (fecha válida, opción
   existente, longitud), la autoridad y las precondiciones; arma la vista previa y
   ejecuta un manejo determinista por comando. Si un valor no vale, dice la razón real
   y qué sirve, sin jerga técnica.
5. **Persistir (PostgreSQL).** Las funciones y los disparadores son la última línea de
   las invariantes. No cambian con este ADR.
6. **Responder (a partir de hechos).** El código produce el **resultado del turno**,
   estructurado: qué cambió y qué no, el estado real leído de la base, qué falta y las
   opciones posibles. Las opciones (botones) salen de ese resultado, nunca del texto
   del modelo. Cómo se redacta el texto se decide por experimento (abajo).

Las decisiones que hoy tienen más de un dueño se pasan a su dueño a medida que el flujo
se aplica a cada camino, no todas a la vez. Mientras un camino no pasa al flujo, sigue
como está.

### Experimento: redacción A o B

Dos variantes de la etapa 6, seleccionables por configuración del espacio:

- **A. El modelo redacta toda respuesta** a partir del resultado del turno. El código
  verifica que el texto no afirme nada fuera del resultado (un cambio que no ocurrió,
  un estado distinto del leído). Si la verificación falla, sale la plantilla de B y
  queda registrado.
- **B. Plantillas para los efectos.** Lo que dice qué cambió, cómo quedó la tarea y qué
  falta sale de plantillas del código; el modelo redacta sólo la charla y las
  preguntas.

**Cómo se prueba.** El flujo se aplica primero, de forma acotada, a los caminos de los
hallazgos pendientes de la cuarta ronda. Esos hallazgos pasan a ser el guion de la
prueba: no se corrigen uno por uno, se comprueba si desaparecen con el flujo. La prueba
decisiva es por Telegram real, con datos ficticios en una base nueva y el mismo guion
corrido una vez con A y otra con B. Por cada respuesta el usuario anota si mejoró,
empeoró o quedó igual respecto de la ronda 4. Se registran además la latencia, las
llamadas al modelo, los incidentes y las veces que la verificación de A rechazó un
texto. Las pruebas deterministas cubren las garantías (validación, verificación del
texto, opciones desde el resultado), no la redacción.

**Para bajar el sesgo** (una sola corrida, evaluada por quien conoce el guion y opera
todas las cuentas):

- el banco real (`tests/banco/`, escenarios `modelo_real`) se corre también con A y con
  B, para tener una comparación con números además de la evaluación del usuario;
- las transcripciones de A y B se comparan lado a lado, mensaje por mensaje, no de
  memoria.

**Criterios fijados antes de ver los datos** (decisión del usuario, 2026-09-30):

- **Éxito:** de los siete hallazgos del alta guiada (R4c-H4 a H10), al menos cinco
  desaparecen sin código específico para ellos; ningún incidente nuevo; latencia
  mediana de cinco segundos o menos por respuesta.
- **Corte:** si A y B quedan parecidas y ninguna mejora claramente sobre la ronda 4, el
  problema no estaba en la redacción: se busca la causa en otro lado en vez de insistir
  con el flujo.
- **Retiro de lo viejo:** un camino cuenta como pasado al flujo sólo cuando se retiraron
  sus mecanismos anteriores (las expresiones regulares que interpretaban, las
  correcciones posteriores del texto). Si conviven los dos, no está terminado.
- **Expectativa:** el flujo no lleva los hallazgos a cero; una ronda nueva siempre prueba
  superficie nueva. Lo que se espera es que dejen de repetirse las mismas clases de
  falla.

**Moratoria.** Mientras dura el experimento no se agregan reglas ni parches de
conversación. Un hallazgo nuevo se registra y se clasifica por etapa del flujo.

El resultado del experimento se registra como enmienda de este ADR, con la variante
elegida (o la combinación) y su evidencia.

## Consecuencias

- Con A, cada turno suma una llamada al modelo para redactar sobre el resultado: más
  latencia y más costo. El experimento mide cuánto.
- Interpretar valores con el modelo hace que la respuesta a un dato pedido dependa de
  él. Si el modelo falla, el valor no se inventa: la pregunta queda abierta y se aplica
  el camino de falla de siempre (incidente y aviso neutro).
- Las expresiones regulares que hoy interpretan fechas y elecciones pasan a validar la
  salida estructurada del modelo, o se retiran.
- Las correcciones posteriores del texto del modelo (`agente.py`) dejan de hacer falta
  en los caminos que pasan al flujo; con A las reemplaza la verificación contra el
  resultado del turno.
- El rol de Jev queda declarado: decidir entre candidatos de la base con duda. Figura
  como puerto y adaptador en `architecture/frontera.md`.

## Alternativas consideradas

- **Seguir corrigiendo los hallazgos por prioridad.** Rechazada por el usuario: cada
  ronda trae hallazgos nuevos del mismo tipo y no termina.
- **Elegir A o B sin probar.** Rechazada por el usuario: la diferencia entre ambas sólo
  se ve en conversaciones reales.
- **Aplicar el flujo a todos los caminos de una vez.** Rechazada: es una reescritura
  sin evidencia. Se aplica primero donde hay hallazgos, se mide y después se extiende.
