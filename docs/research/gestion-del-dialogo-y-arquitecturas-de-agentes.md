# Relevamiento: gestión del diálogo, mercado y arquitecturas de agentes conversacionales

- **Fecha:** 2026-10-04
- **Pedido:** del usuario, después de la prueba real de la tarea 0-35: un análisis
  adversarial sobre si se puede lograr que Leda se comporte como un project manager, si la
  estructura Jev + SQL + IA es la correcta, qué existe en el mercado y por qué cada circuito
  termina en parches repetidos.
- **Fuentes:** tres, todas de sólo lectura.
  1. Investigación externa del 2026-10-04, con búsqueda y lectura web. Las páginas se leyeron
     a través de un resumidor, así que las cifras son las extraídas, no comprobadas byte a
     byte. Los enlaces sin fecha son documentación viva leída ese día.
  2. Revisión interna del repositorio: el código de la rama de flujo en `b463a4a` (el mismo
     código que la etiqueta `respaldo-flujos-antes-de-d`) y los documentos de `main`. Los
     conteos salen de `git`, del árbol sintáctico y de expresiones regulares; no se corrió
     ninguna prueba. Las referencias `archivo:línea` de la sección 6 son de `b463a4a`, salvo
     las que dicen `main`.
  3. Repositorio y documentación de Engram, y la versión instalada (3.0.0).
- **Marcas:** [V] fuente primaria abierta; [VC] afirmación del vendedor; [3P] fuente
  secundaria; [I] inferencia de quien investigó.
- **Veredicto:** la base de Leda es la correcta y coincide con el patrón dominante: el modelo
  interpreta y redacta; el código es dueño del estado, las reglas, las aprobaciones y la
  ejecución. La falla está en la capa de conversación: está escrita a mano, situación por
  situación y sin un modelo de la conversación, cosa que ninguno de los productos y marcos
  relevados hace. Ningún producto verificado cubre el circuito completo de Leda dentro del
  chat del equipo. Una conversación sin fallas en todas las situaciones no la logra nadie:
  las garantías tienen que vivir fuera del modelo.

Las decisiones que el usuario tomó a partir de este relevamiento están en la sección 8.

## 1. Mercado

### Agentes dentro de las suites de gestión

Todos viven dentro de la suite y actúan cuando se los asigna, se los menciona, se los
programa o los dispara una regla.

- **Asana AI Teammates:** vista previa pública el 25 de septiembre de 2025
  ([Computerworld](https://www.computerworld.com/article/4063082/asana-puts-ai-teammate-agents-to-work.html));
  21 agentes prearmados como complemento pago
  ([Asana, 17 de marzo de 2026](https://asana.com/resources/ai-teammates-overview)) [V]. No hay
  nada documentado sobre perseguir a las personas; "2x faster" es [VC].
- **ClickUp Super Agents**
  ([10 de febrero de 2026](https://clickup.com/learn/topic/project-management/tools/clickup/news/)):
  mención, mensaje directo, asignación, programación o automatización; sólo dentro de ClickUp
  ([página del producto](https://clickup.com/brain/agents)) [V]. Un usuario informa de un
  agente que dejó de funcionar de forma consistente
  ([tablero de comentarios de ClickUp, 26 de febrero de 2026](https://feedback.clickup.com/ai-super-agents/p/super-agent-stopped-working-properly))
  [V].
- **monday.com:** sidekick, constructor de agentes en beta e inscripción para agentes externos
  ([11 de marzo de 2026](https://ir.monday.com/news-and-events/news-releases/news-details/2026/monday-com-Welcomes-AI-Agents-to-Its-Platform-Marking-a-Shift-in-How-Work-Gets-Done/default.aspx))
  [V].
- **Atlassian Rovo:** a los agentes se les puede asignar trabajo de Jira; 3 millones de
  usuarios mensuales, sobre todo de búsqueda y chat
  ([TechTarget, octubre de 2025](https://www.techtarget.com/searchitoperations/video/Atlassian-Rovo-AI-grows-to-3-million-monthly-users))
  [3P].
- **Notion Custom Agents** ([24 de febrero de 2026](https://www.notion.com/releases/2026-02-24)):
  disparadores por programación, Slack y base de datos; medidos por créditos desde el 4 de mayo
  de 2026 [V].
- **Wrike AI Agents**
  ([5 de febrero de 2026](https://www.wrike.com/newsroom/wrike-launches-ai-agents-delivering-six-days-of-output-in-a-five-day-work-week/)):
  Intake, Triaging y Risk Status Reporter; "10 hours a week saved" es [VC].
- **Otros:** Linear for Agents
  ([20 de mayo de 2025](https://linear.app/changelog/2025-05-20-linear-for-agents)) vuelve a los
  agentes compañeros asignables, con foco en desarrolladores [V]. Motion cuesta entre 19 y 29
  dólares por puesto y planifica y agenda ([precios](https://www.usemotion.com/pricing)) [V].
  Dart afirma tener "100,000 teams" ([sitio](https://www.dartai.com/)) [VC]. De Smartsheet,
  Taskade y el Planner Agent de Microsoft sólo se encontró cobertura secundaria [3P].
- **Un fracaso:** Height apostó a la "autonomous project management" y cerró el 24 de
  septiembre de 2025
  ([AlternativeTo, 24 de marzo de 2025](https://alternativeto.net/news/2025/3/height-project-management-tool-to-shut-down-by-september-2025/))
  [3P].

### Asistentes que viven en el chat

- **Bots de standup:** Geekbot (2,5 dólares por participante por mes;
  [precios](https://geekbot.com/pricing/)) y DailyBot (Slack, Teams, Google Chat, Discord;
  [sitio](https://dailybot.com/)) hacen chequeos programados, recordatorios y aprobaciones con
  botones [V]. Standuply se sigue vendiendo [3P]. Ninguno hace un alta conversada.
- **Chaser** (Slack, lanzamiento pago el 25 de junio de 2026): un mensaje se convierte en una
  tarea con responsable y fecha, los recordatorios salen antes y después del vencimiento, y los
  informes de estado se publican en un canal; entre 7 y 16 dólares por puesto
  ([blog del vendedor, 24 de junio de 2026](https://www.trychaser.com/blog/slack-ai-tools)). El
  fundador afirma tener 175 empresas pagando
  ([reseña de un competidor, 12 de agosto de 2026](https://www.thisandthat.chat/blog/chaser-review-2026/))
  [VC]. Es un seguimiento determinista, sin diálogo para completar los datos que faltan.
- **Otros:** Spinach vende hoy un "AI meeting agent" ([sitio](https://www.spinach.ai/)) [V].
  Viktor ([reseña de un competidor, 26 de agosto de 2026](https://www.lindy.ai/blog/viktor-review))
  y el nuevo Slackbot
  ([No Jitter, 1 de abril de 2026](https://www.nojitter.com/digital-workplace/slack-turns-slackbot-into-the-ultimate-ai-teammate))
  son compañeros de IA generales [3P].

### Español, Latinoamérica, equipos de campo, WhatsApp y Telegram

- **PIA** ([soypia.com](https://soypia.com/)): un audio de WhatsApp se convierte en tareas con
  responsable, el cierre exige evidencia y el seguimiento escala: "48 horas sin cierre. PIA le
  escribe al responsable. No responde en 24 horas. Se escala al supervisor"
  ([página](https://soypia.com/seguimiento-tareas-whatsapp/)). Afirma estar en 8 países, con
  más de 185.000 interacciones y clientes como P&G [VC]. Vende a operaciones de campo de
  empresas grandes; sin precio público.
- **MiChamba** (México): asignación de tareas por WhatsApp, evidencia con foto y
  recordatorios, con una capa de IA en el plan más alto; 2,25 millones de dólares de
  inversión presemilla, más de 15 clientes y unos 100.000 dólares de ingresos anuales
  recurrentes
  ([Forbes México, 24 de noviembre de 2025](https://forbes.com.mx/esta-startup-quiere-convertir-el-caos-de-whatsapp-en-trabajo-organizado/))
  [3P].
- **Otros:** Tasks.Bot es una herramienta india de tareas por WhatsApp, en beta
  ([artículo promocional, 10 de agosto de 2026](https://sheetsbase.com/why-is-tasks-bot-the-best-for-auto-assignment-smart-reminders/))
  [3P]. Fracttal es un sistema de mantenimiento donde las órdenes de trabajo se crean, asignan
  y cierran por mensaje o audio de WhatsApp, en español
  ([sitio](https://www.fracttal.com/en/integrations-whatsapp)) [V]. MaintainX afirma tener
  "14,000 companies" y tiene interfaz en español ([sitio](https://www.getmaintainx.com/)) [VC].
  En Telegram sólo se encontraron bots de tareas por comandos [3P].

### Conclusión de mercado

No se encontró ningún producto verificado que haga todo dentro del chat del equipo: alta
conversada que completa los datos que faltan, aprobación del borrador, escalera de
recordatorios, evidencia y aprobaciones, con garantías sobre el estado.

- PIA es el más cercano por función, pero apunta a la ejecución en campo de empresas grandes
  y se apoya en afirmaciones del vendedor.
- Chaser persigue sin conversar.
- Los agentes de las suites conversan, pero no viven en el chat ni garantizan el seguimiento.

[I] La categoría se está abordando desde tres lados y no está resuelta. Lo que hoy se vende es
seguimiento firme con poca conversación.

## 2. Arquitecturas

### Por producto o marco

- **Rasa CALM.** El modelo sólo emite comandos (iniciar o cancelar un flujo, fijar un dato,
  aclarar, saltear). Un gestor determinista corre flujos declarados, y los comandos "can only
  leverage existing flows and knowledge bases"
  ([documentación](https://www.rasa.com/docs/learn/concepts/dialogue-understanding.md)). La
  digresión, la corrección, la cancelación, las preguntas salteadas, la aclaración, la
  reanudación de un flujo interrumpido y el "no puedo atender eso" son patrones incorporados
  ([referencia](https://www.rasa.com/docs/reference/primitives/patterns)). La documentación
  muestra que un texto escrito en lugar de tocar un botón se resuelve por el mismo mecanismo.
- **Sierra.** SDK declarativo con habilidades componibles, "deterministic API interactions" y
  modelos supervisores
  ([11 de julio de 2024](https://sierra.ai/blog/meet-the-ai-agent-engineer)); el determinismo
  se fija por flujo de trabajo ([página del producto](https://sierra.ai/product/agent-sdk));
  recorridos en lenguaje natural desde Agent OS 2.0
  ([5 de noviembre de 2025](https://sierra.ai/blog/agent-os-2-0)).
- **Decagon AOP.** Procedimientos en lenguaje natural, con "key validation steps in code" para
  las acciones sensibles ([8 de abril de 2025](https://decagon.ai/blog/why-we-built-aop)).
- **Intercom Fin Procedures.** Pasos en lenguaje natural más condiciones en código, conectores
  de datos y aprobaciones humanas; Fin se mueve "non-linearly across steps"
  ([explicación](https://fin.ai/help/en/articles/13976187-fin-procedures-explained)). Las Fin
  Tasks anteriores se cerraron a construcciones nuevas el 12 de marzo de 2026
  ([transición](https://www.intercom.com/help/en/articles/13459670-transitioning-from-fin-tasks-to-procedures)).
- **Parlant.** La selección de pautas está separada de la generación del mensaje
  ([motor](https://www.parlant.io/docs/engine-internals/overview)). Los recorridos pueden "jump
  multiple states" o volver a visitarlos
  ([recorridos](https://parlant.io/docs/concepts/customization/journeys)). El modo estricto sólo
  envía mensajes aprobados de antemano
  ([respuestas enlatadas](https://www.parlant.io/docs/concepts/customization/canned-responses)).
- **OpenAI Agents SDK y AgentKit.** Bucle conducido por el modelo, con guardas de entrada, de
  salida y de herramientas, y traspasos
  ([guardas](https://openai.github.io/openai-agents-python/guardrails/)); `needs_approval`
  detiene la corrida hasta que decide una persona
  ([aprobaciones](https://openai.github.io/openai-agents-python/human_in_the_loop/)).
- **Anthropic.** Usar "the simplest solution possible"; los flujos de trabajo son caminos de
  código predefinidos y los agentes se dirigen solos
  ([19 de diciembre de 2024](https://www.anthropic.com/engineering/building-effective-agents)).
  En el Claude Agent SDK, los ganchos y las reglas de denegación son código del desarrollador
  que corre antes de cada llamada a una herramienta
  ([documentación](https://code.claude.com/docs/en/agent-sdk/permissions)).
- **LangGraph.** Grafo de estados explícito; `interrupt()` guarda el estado y reanuda con un
  valor que da una persona. El nodo se vuelve a ejecutar al reanudar, así que los efectos
  tienen que ser idempotentes
  ([documentación](https://docs.langchain.com/oss/python/langgraph/interrupts)).
- **Copilot Studio.** La orquestación generativa es el modo por omisión: elige temas y
  herramientas por su descripción y escribe las preguntas de los datos que faltan. Entre los
  límites documentados están la falta de desambiguación y un comportamiento que depende del
  modelo
  ([26 de agosto de 2026](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions)).
- **Google ADK.** Agentes con modelo más agentes de flujo secuenciales, paralelos y de bucle,
  para "interweave" los modelos "with deterministic code"; confirmación de herramientas
  ([documentación](https://adk.dev/agents/)).
- **12-factor agents.** Los productos que se presentan como agentes son "mostly deterministic
  code, with LLM steps sprinkled in"; el control del flujo es propio; a las personas se llega
  mediante llamadas a herramientas
  ([repositorio](https://github.com/humanlayer/12-factor-agents)).
- **Salesforce Agentforce.** Pasó de razonar sólo con instrucciones a Agent Script, "push logic
  to code by default", y cita inconsistencia y estado perdido
  ([guía de arquitectura](https://architect.salesforce.com/docs/architect/fundamentals/guide/hybrid-reasoning-agentforce-builder-agent-script))
  y "doom-prompting"
  ([blog de ingeniería](https://engineering.salesforce.com/agentforces-agent-graph-toward-guided-determinism-with-hybrid-reasoning/)).

### Los tres patrones y sus costos

[I] El patrón dominante en 2026 es híbrido: el modelo interpreta y redacta; el código
determinista es dueño del estado, las reglas, las aprobaciones y la ejecución; y cada entrega
pasa antes por simulaciones.

1. **Conversación conducida por el modelo, con herramientas vigiladas.** Absorbe los giros no
   previstos con el menor código y mejora con los modelos. La obediencia a las reglas es
   probabilística (sección 3), cuesta más llamadas y se ajusta iterando instrucciones.
2. **Del modelo a comandos, más flujos declarados.** La lógica queda auditable y las
   reparaciones se resuelven una sola vez para todos los flujos. Los flujos hay que
   escribirlos, y lo que queda fuera cae en un camino de respaldo. La prueba del propio Rasa
   informa 0,04 dólares y 2,1 s por mensaje, contra 0,10 dólares y 7,4 s de un agente con
   llamadas a funciones
   ([8 de agosto de 2024](https://rasa.com/blog/cutting-ai-assistant-costs-the-power-of-enhancing-llms-with-business))
   [VC].
3. **Código de diálogo escrito a mano.** Da control total, pero los caminos se multiplican.
   Salesforce lo llama "unmanageable, interdependent logic" y Decagon dice que los árboles de
   decisión necesitan "constant maintenance". Ninguno de los relevados escribe a mano una rama
   por situación.

[I] Leda es el patrón 2 en la intención (ADR 0013 y
[ADR 0014](../decisions/0014-flujo-de-un-mensaje.md)) y el patrón 3 en la implementación,
circuito por circuito.

## 3. Confiabilidad

Tabla oficial de τ-bench, que mantiene Sierra, con cuatro corridas por tarea
([entregas](https://github.com/sierra-research/tau2-bench/tree/main/web/leaderboard/public/submissions),
[sitio](https://taubench.com/); del 26 de febrero al 2 de marzo de 2026). Los valores son
pass^1 → pass^4, en porcentaje: resolver bien una vez, y resolver bien las cuatro seguidas.

| Modelo | Aerolínea | Comercio | Telecomunicaciones |
|---|---|---|---|
| Claude Opus 4.5 (razonamiento alto) | 84,0 → 70,0 | 79,6 → 51,8 | 92,3 → 78,1 |
| GPT-5.2 (razonamiento alto) | 83,0 → 72,0 | 81,6 → 51,8 | 89,7 → 71,9 |
| GPT-5.2 (sin razonamiento) | 52,5 → 22,0 | 75,0 → 45,6 | 57,2 → 30,7 |
| Gemini 3 Pro | 80,5 → 66,0 | 75,9 → 47,4 | 91,0 → 74,6 |
| Qwen3.5-397B | 81,5 → 68,0 | 84,4 → 59,7 | 97,8 → 92,1 |

- **Dominio bancario, con mucho conocimiento** (4 de agosto de 2026): Qwen 3.8 Max 55,2 → 35,1;
  Claude Opus 5 48,7 → 32,0; GPT-5.6-sol 46,9 → 27,8.
- **Historia:** en 2024, GPT-4o resolvía menos del 50 % una vez y cerca del 25 % ocho veces
  seguidas en comercio ([Sierra, 20 de junio de 2024](https://sierra.ai/blog/benchmarking-ai-agents)).
  Parte de la brecha vieja era error del banco de pruebas: se corrigieron 53 tareas y el pass^1
  de aerolínea subió entre 14 y 20 puntos
  ([febrero de 2026](https://taubench.com/blog/tau3-task-fixes.html)).
- **Banco comparable:** CRMArena-Pro (Salesforce, junio de 2025) encontró 58 % de éxito en un
  turno y 35 % en varios; casi la mitad de las fallas muestreadas fue no preguntar la
  información que faltaba
  ([The Decoder, 15 de junio de 2025](https://the-decoder.com/salesforces-crm-benchmark-finds-ai-agents-struggle-in-real-world-business-scenarios/))
  [3P].

**Qué implica.** Con razonamiento, estos modelos completan entre el 76 y el 98 % de las
conversaciones simples sujetas a reglas en un intento, y entre el 47 y el 92 % cuatro veces
seguidas. Sin razonamiento, la única corrida de GPT-5.2 muestra entre 52 y 75 %, y entre 22 y
46 %. Los usuarios simulados son más dóciles que las personas (sección 4), así que las cifras
reales probablemente sean menores. La autoridad, los datos obligatorios, la confirmación antes
de un efecto, el aislamiento y la auditoría tienen que imponerse en el código y en la base.

## 4. Cómo se prueba un agente conversacional

- **Repetición de conversaciones reales.** Sierra convierte cada conversación de producción
  anotada en una prueba "simulated against mock APIs" y corre miles antes de cada entrega; las
  entregas son copias inmutables
  ([3 de junio de 2024](https://sierra.ai/blog/agent-development-life-cycle)).
- **Usuarios simulados con jueces.**
  - Decagon usa repeticiones de mensajes como pruebas unitarias, simulaciones con personajes y
    control de calidad continuo
    ([23 de julio de 2025](https://decagon.ai/blog/the-future-of-ai-agents-is-test-driven)).
  - Las simulaciones de Fin usan un cliente de IA y criterios de pase o falla (artículo de
    Procedures citado arriba).
  - Los escenarios de Google ADK son una consigna inicial más un plan de conversación
    ([7 de noviembre de 2025](https://developers.googleblog.com/en/announcing-user-simulation-in-adk-evaluation/)).
  - Código abierto: LangWatch Scenario, con pytest y vitest en integración continua
    ([sitio](https://langwatch.ai/scenarios)), y la simulación de varios turnos de LangSmith
    ([documentación](https://docs.smith.langchain.com/evaluation/how_to_guides/multi_turn_simulation)).
- **Comprobaciones deterministas.** Las pruebas de punta a punta de Rasa comprueban datos,
  flujos y acciones en cada turno, convierten conversaciones de muestra en pruebas e informan
  la cobertura de los flujos
  ([documentación](https://rasa.com/docs/rasa-pro/testing/e2e-testing-assertions/assertions-introduction)).
- **Método.** La guía de Anthropic recomienda un usuario simulado más comprobaciones de estado,
  límites de transcripción y una rúbrica evaluada por un modelo: empezar con 20 a 50 tareas
  sacadas de fallas reales, mantener una suite de regresión cerca del 100 % e informar pass^k,
  porque 75 % por corrida es 42 % para tres seguidas
  ([9 de enero de 2026](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)).
- **Advertencia.** El éxito medido se mueve hasta 9 puntos según el modelo que simula
  ([arXiv 2601.17087, enero de 2026](https://arxiv.org/abs/2601.17087)). En una comparación de
  31 simuladores con 451 personas, los simuladores resultaron "excessively cooperative"
  ([arXiv 2603.11245, marzo de 2026](https://arxiv.org/abs/2603.11245)). La simulación atrapa
  regresiones; las situaciones nuevas las siguen encontrando las personas.

## 5. Límites

- **Confianza.** El 64 % de los trabajadores considera poco confiables a los agentes de IA, y
  el 39 % dice que nadie responde por sus errores (encuesta de Asana;
  [UNLEASH, 25 de septiembre de 2025](https://www.unleash.ai/artificial-intelligence/asana-64-of-employees-believe-ai-agents-are-unreliable-calling-for-more-training-clarity-and-guardrails))
  [3P].
- **Expectativas.** Gartner espera que más del 40 % de los proyectos de IA con agentes se
  cancele antes de fines de 2027, y cuenta unos 130 proveedores genuinos de agentes
  ([25 de junio de 2025](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027))
  [3P].
- **Juicio.** Se atribuye al PMI la estimación de que la IA automatiza entre el 25 y el 30 %
  de las tareas de gestión de proyectos; el juicio y el trato con los interesados siguen
  siendo humanos ([4PMTI](https://www.4pmti.com/learn/ai-in-project-management/)) [3P].
- **Proactividad.** Un estudio de CHI 2025 sobre asistentes de programación proactivos
  encontró menos coordinación manual, pero más interrupción y pérdida de control
  ([arXiv 2502.18658](https://arxiv.org/abs/2502.18658)). Extenderlo al cansancio por
  seguimiento es [I]; no se encontró ningún estudio sobre bots que persiguen tareas.
- **Datos inventados.** A Air Canada la hicieron responsable de una política de reembolso que
  inventó su chatbot (2024). El bot de soporte de Cursor inventó una regla de un solo
  dispositivo que provocó cancelaciones (abril de 2025)
  ([AI Incident Database](https://incidentdatabase.ai/cite/1039/)) [3P]. Klarna volvió a
  contratar agentes humanos en 2025
  ([Entrepreneur](https://www.entrepreneur.com/business-news/klarna-ceo-reverses-course-by-hiring-more-humans-not-ai/491396))
  [3P].

## 6. Revisión interna del proyecto

**Titular** [I]: las fallas registradas no se agrupan en Jev, en SQL ni en la comprensión del
modelo. Se agrupan en la capa que hay entre ellos: unas 16.000 líneas de manejo de conversación
escritas a mano, con estado implícito, repartidas en tres flujos que conviven, y producidas más
rápido de lo que ninguna revisión o prueba puede comprobar. La capa de garantías es sólida.

### Tamaño y movimiento

- `src/leda`: 40 archivos, 30.495 líneas, 982 funciones. `gateway.py` 5.729 (156 funciones),
  `ingreso_tareas.py` 3.917, `herramientas.py` 2.415, `despachador.py` 1.790, `alta_turno.py`
  1.658, `llm.py` 1.621, `alta_conducida.py` 1.501, `agente.py` 1.335. Los tamaños de
  `gateway.py`, `ingreso_tareas.py`, `alta_turno.py`, `alta_conducida.py` y `agente.py` se
  volvieron a contar aparte y coinciden.
- Pruebas: 163 archivos Python, 69.975 líneas (2,3 veces el código), 2.758 funciones de prueba
  y 111 escenarios del banco.
- Historia: 593 commits, 592 entre el 2026-09-22 y el 2026-10-04, que suman unas 141.000
  líneas en 13 días.
- Rama de flujo desde `7c1e17b`: 254 commits entre el 2026-09-30 y el 2026-10-04 (24, 80, 60, 78
  y 12 por día; 133 de documentación, 55 `fix` y 50 `feat`). 42 arreglos apuntan al alta, a su
  redacción o a su verificador. Código: +13.774 / −3.572 líneas; pruebas: +23.401 / −3.714.
- Módulos de conversación en toda la historia: unas 25.200 líneas escritas y 6.200 quitadas,
  el 81 % de todo el código borrado.
- De los 119 commits de código de la rama, 102 tocan archivos del alta o de la redacción. El
  movimiento de código es 68 % alta y redacción, 22 % otra conversación y 8 % dominio. De los
  11 circuitos, sólo el alta se pasó al flujo nuevo, y ninguno quedó cerrado.

### Cómo se procesa un mensaje

- No hay un despachador único. El texto se bifurca en tres en `gateway.py:604-648` (alta C6,
  alta guiada y `_turno`). Los toques se bifurcan en `_toque` (`:935-1149`) sobre dos espacios
  de nombres de tokens, y después en una cadena de condiciones sobre cinco marcas
  (`:1741-1776`). `alta_conducida.py` tiene 14 puntos de entrada, llamados desde 35 lugares. La
  regla de una respuesta visible la impone después un conciliador (`respuesta_unica.py:1-41`).
- Flujo B: una llamada de ruteo (herramienta forzada, dos intentos), Jev por cada referencia a
  un trabajo, un bucle de agente de hasta cinco llamadas (`agente.py:48,179`), una llamada
  opcional de reescritura (`:317-323`), y después el código edita el texto del modelo.
- Alta C6: una llamada que interpreta, la validación y la decisión del código
  (`alta_turno.py:1009-1033`), una llamada que redacta y el verificador
  (`alta_conducida.py:524-616`). Un cambio de tema en medio del alta cuesta interpretar,
  rutear, una nota y el agente del flujo B (`gateway.py:3764-3815`).
- Las llamadas a la IA corren dentro de una transacción que retiene bloqueos `for update`
  (`alta_conducida.py:205-207,468-471`).

### Dónde vive el estado de la conversación

- `pending_action` (`db/esquema.sql:654-705`), con once marcas de texto que nombran clases de
  pendientes (`gateway.py:65-91`, `pendientes.py:49-92`).
- `task_intake_request` (`db/esquema.sql:737-769`): `estado`, `enviada_en` y una columna JSON
  llamada `terminal_result` que guarda marcas que no son terminales: `pausado`, `devuelto`,
  `criterio_propuesto` y `sin_objetivo_avisado` (`ingreso_tareas.py:1066-1078`).
- Además: filas de datos, juegos de opciones y espacios de texto libre
  (`db/esquema.sql:771-867`); `task_draft.estado`, que duplica el de la solicitud; columnas del
  outbox; variables de contexto por turno y cachés de proceso.
- Historial que recibe la IA: seis horas, doce mensajes, sólo texto (`contexto.py:305-306`);
  los toques de botones quedan afuera (`gateway.py:856-858`).
- No hay máquina de estados ni tabla de transiciones, ni en el código ni en los documentos.
  "Qué está abierto" es una cadena de cuatro consultas con precedencia
  (`pendientes.py:516-547`); el alta C6 usa otra definición (`alta_conducida.py:201-217`).
- Un borrador del alta tiene al menos 14 estados implícitos, cada uno detectado por
  combinaciones de columnas, JSON o existencia de filas: juntando datos, esperando un botón,
  selector de Modificar, esperando un dato de texto, resumen esperando Confirmar, resumen
  esperando Enviar, pausado, enviado, quien confirma con la pregunta del motivo, pedido de
  confirmación vencido, devuelto, devuelto y en espera detrás de otro borrador, cancelado y
  convertido. Un solo lector deriva 11 resultados de seis columnas de tres tablas
  (`gateway.py:1507-1553`).

### Jev

- `typesafe/jev-1.13`, por `api/alpha/decisions` de OpenRouter; plazo de 60 s y cuatro
  intentos (`jev.py:24-26,105`). Recibe el mensaje, la referencia, el vocabulario del equipo y
  quién escribe; devuelve una probabilidad por opción.
- Tres usos: referencias a tareas en el flujo B, orden de los objetivos y un nombre fuera de
  las opciones en el alta C6.
- Límites registrados en el
  [ADR 0006](../decisions/0006-jev-para-resolver-referencias-e-intencion.md): beta y no
  determinista; ofrece tareas parecidas para cosas que no existen; falsas alarmas en una de
  cada tres frases claras; validado con lotes de 15 y 45 mensajes contra `deepseek-v4-flash`.
  Su papel para la duda de intención nunca se construyó.
- Su aporte frente al modelo más capaz que se usa hoy (GPT-6 sol) no está medido.

### Contrato con la IA

- Proveedores: compatible con OpenAI, Gemini, Anthropic y un doble guionado. Modelos probados:
  `deepseek-v4-flash`, GPT-6 luna, GPT-6 sol (el elegido) y Gemini 3.8 flash.
- Herramienta forzada en el ruteo y en las dos llamadas del alta; plazo de 20 s con dos
  reintentos del SDK; dos intentos por llamada del alta y, después, un incidente y un aviso
  neutro fijo.
- El verificador es léxico (números, fechas, meses, títulos entre comillas, palabras con
  mayúscula, largo; `verificador_redaccion.py:226-273`), más controles de estructura sobre los
  botones de cierre, las propuestas y el dato que la IA declara haber preguntado
  (`alta_turno.py:1329-1363`). No puede comprobar causas, quién hizo qué, promesas ni sentido.
- Instrucciones por llamada: interpretar el alta, 2.352 caracteres; redactar, 3.224 más el
  tono; ruteo, 1.712. El flujo B manda en cada llamada un preámbulo de 4.003 caracteres, la
  constitución entera (12.110) y la mecánica entera (13.338), incluida la mecánica de
  capacidades que no tienen código (`contexto.py:37-44,233-235`).

### Pruebas

- Clases: unitarias, y conversaciones guionadas de varios turnos con la IA simulada
  (`ProveedorGuionado`, 66 archivos), escritas por el mismo escritor que el código.
- Banco con el modelo real: 111 escenarios, excluidos por omisión, con cuatro entradas de la
  persona como máximo. Ningún archivo de `tests/banco` ejercita el alta C6 (vuelto a comprobar
  aparte: cero archivos).
- Ninguna prueba tiene un modelo haciendo de usuario. No se conservan transcripciones reales
  como regresión.
- Unas 150 líneas de comprobación citan el texto de las instrucciones, 21 lugares leen el
  código fuente o su árbol sintáctico y `monkeypatch` aparece 2.181 veces. Cerca del 73 % de
  las funciones de prueba está atado al lado de la conversación.
- Pases por el motivo equivocado, ya registrados en la tarea: el doble completaba solo un dato
  y escondió omisiones en 213 casos; una prueba de Cancelar pasaba por un camino de falla; las
  guardas aceptaban cualquier incidente y cualquier texto de la IA.
- En `main` (exploración aparte): de 94 archivos de prueba, 60 importan `gateway`, `agente` o
  `ingreso_tareas` y sólo unos 17 son limpios. Las pruebas de aislamiento entre clientes, de
  dueños de funciones `security definer` y de paridad de migraciones viven en
  `tests/test_task_intake.py`, que importa el código de conversación; `tests/conftest.py`
  importa `gateway` en cada prueba.

### Recurrencia

| Fecha | Suceso | Hallazgos |
|---|---|---|
| 2026-09-25 | Sesión 1 | 4 |
| 2026-09-27 | Sesión 2 | 10 |
| 2026-09-28 | Ronda 3, cortada; sigue el ADR 0013 | 21 (4 críticos) |
| 2026-09-30 | Ronda 4; siguen el ADR 0014 y el congelamiento | 28 |
| 2026-10-01 | C1 | 83 % de los turnos aceptados al primer intento; 5 turnos fallidos |
| 2026-10-02 | Rondas 0-A a 0-4; C2, C3 (sin prueba real) y C4 (retroceso) | 8 |
| 2026-10-03 | C5 y C6; corridas con flash, luna y sol | 6, 5 y, después, un bucle |
| 2026-10-03 y 04 | Auditorías 1 a 5 | 14, 7, 7, 6, 7 |

- La cuenta no tiende a cero. Las auditorías quedan planas después de la primera. La severidad
  bajó en general, pero la cuarta auditoría volvió a encontrar el bucle del borrador devuelto y
  la quinta encontró una violación de la regla central.
- Clases que se repiten: estado viejo o implícito; la IA que afirma lo que el sistema no hizo o
  no puede hacer; costuras entre la salida del modelo y el contrato; textos fijos y muletillas;
  falla silenciosa.
- El proyecto ya lo había dicho: "estamos parchando, y así se puede seguir al infinito" (ADR
  0014); "cada ronda probaba superficie nueva y los hallazgos no bajaban"
  ([`ROADMAP.md`](../ROADMAP.md)); "arreglar un problema genera el siguiente" y "los controles
  automáticos que escribe el mismo escritor tienen sus mismos puntos ciegos"
  ([bitácora de flujos](../product/bitacora-de-flujos.md)).

### Cobertura del trabajo de un project manager

- Construido: escalera de recordatorios por vencimiento; apertura, cierre y escalamiento solo
  de los bloqueos; dependencias; cadencias; aprobación; entrega con evidencia; reglas de
  cierre; ausencias; objetivos; puerto de lectura y tablero. El tope de contacto es por espacio
  y no por persona.
- Sólo diseñado: entrevista de alta de espacios, panel de plataforma, calendario, correo,
  almacenamiento documental, reuniones e informes, conversación de bloqueos, umbral de
  re-aprobación, privacidad y cambios sobre una tarea comprometida.
- Sólo esquema: aprendizaje, subtareas, prioridad, el ciclo de `pending_reply` y el registro de
  acceso a conversaciones.

### Lo sólido

- RLS forzado (`db/esquema.sql:2178-2217`); el rol de la aplicación no puede escribir tareas ni
  eventos de estado directamente y sólo inserta filas de auditoría.
- El estado como proyección de eventos, con disparadores de cierre, dependencias y bloqueos.
- Confirmación: una acción pendiente congelada y una huella del estado que se vuelve a calcular
  al confirmar (`herramientas.py:102,532-584`); una tarea sólo se crea con
  `confirmar_borrador_tarea`.
- Outbox con clave única de deduplicación y despacho con `skip locked`; 29 migraciones y 28
  rollbacks.
- En ninguna ronda figura un efecto mal hecho. La peor falla de conversación, H5, inventó texto
  y no cambió nada.

### Causas estructurales [I]

1. **La política del diálogo es código imperativo disperso.** Confirmado. Hay centralización
   parcial (una regla para lo que pregunta el alta C6, un manejador de siete comandos en el
   flujo B), cada una local a su flujo. Un mapa aparte sobre `b463a4a` contó unos 30 lugares
   que deciden, cada uno por su cuenta, si va el resumen, qué botones salen y qué se ofrece.
2. **El estado es implícito y está repartido.** Confirmado, y es causa directa: el bucle, los
   botones viejos, los avisos viejos, las filas que quedan esperando y el borrador que vuelve
   en silencio son fallas de derivación del estado.
3. **"La IA no decide nada", como amplificador.** Extendida de los efectos a cada movimiento
   de la conversación, obliga al código a enumerar cada situación: sólo el alta tiene 25
   identificadores de sucesos con hechos redactados por el código. Las plantillas no
   desaparecieron: pasaron a ser textos de hechos más una llamada que los parafrasea. El
   extremo opuesto también falló (H5), así que el problema es el alcance de la regla, no las
   garantías.
4. **Mundos paralelos.** Son tres: el interruptor del alta tiene 52 puntos de bifurcación, los
   flujos A y B siguen vivos y el alta C6 incumplió la regla de una sola rama del ADR 0013
   desde el 2026-10-01 hasta que se notó el 2026-10-04.
5. **Las pruebas verifican la implementación.** La suite llegó a 3.997 en verde mientras cada
   prueba real seguía dando hallazgos, y el flujo elegido no tiene regresión con el modelo real.
6. **El método corre más rápido que el diseño.** Un circuito se rediseñó seis veces en tres
   días. No se encontró ninguna revisión registrada como bloqueante. El cambio de C5 y C6, de
   3.335 líneas, excedía el contexto del revisor y sigue sin revisar.

Dos causas más: no hay un oráculo estable (la calidad la juzga una sola persona que conoce el
guion, con corridas únicas de un modelo no determinista y con criterios que se movieron), y el
contrato quedó ajustado a un modelo (cada cambio de modelo abrió costuras nuevas).

No quedan implicados por la evidencia: la comprensión del modelo, la capa SQL y Jev.

Evidencia en contra: C6 sacó el contenido inventado del alta, los arreglos recientes borran
estado y reglas en lugar de sumarlos, y la severidad de las auditorías baja. Vale para un
circuito de once, cuya prueba real final seguía pendiente.

### Qué es capa sólida y qué es manejo de conversación

Estimación del revisor, en líneas.

| Lado | Módulos | Líneas |
|---|---|---|
| Capa de garantías y dominio, reutilizable | `esquema.sql` y migraciones; `herramientas`, `autoridad`, `db`, `calendario`, `reloj`, `escalera`, `ciclo`, `importador`, `incidentes`, `lectura`, `tablero*`, `valores`, `menu_tarea`, `salida`, `jev`; casi todo `despachador`; el mecanismo de tokens de `pendientes`; los adaptadores de proveedores de `llm`; linaje del borrador, confirmar, aprobar y rechazar en `ingreso_tareas` | unas 14.000 de Python y 2.300 de SQL |
| Manejo de conversación que otro enfoque reemplazaría | `gateway`, `agente`, `alta_turno`, `alta_conducida`, `redaccion`, `verificador_redaccion`, `contexto`, `respuesta_unica`, `saludo`, `instrucciones`, `resultado_turno`, `deteccion_pregunta`; el diálogo del alta guiada en `ingreso_tareas`; la detección de ramas en `pendientes`; las instrucciones del ruteo en `llm` | unas 16.000 de Python |

`ingreso_tareas.py` mezcla los dos lados y hoy no se separa limpio.

### Separación de la capa sólida en `main`

Exploración aparte, sobre `main`.

- **Las operaciones se pueden usar sin el código de conversación.** Todo pasa por
  `herramientas.ejecutar(cur, quien, nombre, args, …)` (`src/leda/herramientas.py:532-598`, en
  `main`), que sólo necesita un cursor de `db.espacio()` y un `Solicitante`. La vista previa
  con huella (`Preparacion`, `pendientes.registrar`, `pendientes.resolver` y la función SQL
  `resolver_pendiente`) también es reutilizable. `menu_tarea.calcular_menu` es pura.
- **Los módulos sí están enredados:**
  1. Entregar una tarea crea estado de conversación que sólo `gateway` sabe resolver
     (`herramientas.py:1361, 1987-2057`: botones Aprobar y Pedir cambios).
  2. El despachador arma botones y retiene mensajes con código de conversación
     (`despachador.py:482-511, 626-653`).
  3. El ciclo de fondo carga el código congelado (`huerfanos.py:64-66` importa `gateway`, y
     `ciclo` importa `huerfanos`).
  4. Los pasos de entrada de un mensaje (secreto del webhook, identidad, registro y
     deduplicación, acuse, indicador de escritura, una respuesta por mensaje, incidentes) son
     funciones privadas de `gateway.py`, mezcladas con el flujo A; la aplicación HTTP vive en
     `gateway.py`.
  5. Hay imports dentro de funciones que llegan a `ingreso_tareas` desde `herramientas.py:778`,
     `pendientes.py:533` y `despachador.py:496`.
- **Al seguimiento le falta:** enlazar la respuesta de una persona con el recordatorio que la
  originó (no hay enlace); `pending_reply`, que nunca se escribe; una operación para "necesito
  más tiempo" (la fecha objetivo es inmutable); y los textos de recordatorios y cadencias, que
  están fijos en `escalera.py` y `reloj.py`.
- **Carga sin conversación:** `python -m leda sembrar` corre una sola vez por espacio (exige
  cero tareas) y es más débil que el compromiso normal de `confirmar_borrador_tarea`: la fecha
  y el criterio son opcionales, la lista de evidencia no se controla contra la política y hay
  una sola fila de auditoría con conteos.

### Qué trae la rama de flujo frente a `main`

- En código, `main` es exactamente la base común (`7c1e17b`) más el renombre a Leda: no tiene
  nada del alta C1-C6. Conserva el alta guiada (flujo A) y el flujo B.
- `main` tiene la documentación al día y `tools/`; la rama de flujo no.
- Diferencia de árbol entre `main` y `b463a4a`: en `src/leda`, 10.741 líneas sólo en la rama y
  539 sólo en `main`; en pruebas, 19.918 y 242; en `db`, 929 y 14.
- Peso muerto si se partiera de la punta de la rama: unas 8.900 líneas de código, 17.400 de
  pruebas y 600 de base, todas del alta.
- Infraestructura general de la rama que conviene traer a propósito, unas 2.000 líneas: orden
  de despacho y bloqueo por espacio; quitar botones vencidos y escribir la opción tocada
  (migración `0028`); avisos guardados como hechos y redactados al salir, con reintentos
  (columnas de la `0029` y ADR 0016, que sólo existe en la rama; el redactor vive en módulos
  del alta y hay que rehacerlo); el control contra datos inventados
  (`verificador_redaccion.verificar_afirmaciones`); mejoras de `llm.py` (historial al ruteo,
  topes por modelo, plazo total por llamada, llamada estructurada forzada en los tres
  proveedores, escritura progresiva); el tono del cliente como instrucciones
  (`instrucciones.py`); el área de los objetivos (migración `0027`).

## 7. Engram

Pedido del usuario del 2026-10-04: volver a analizar si Engram sirve, dado que el 2026-09-24
había propuesto una memoria por integrante inspirada en él ([`ROADMAP.md`](../ROADMAP.md),
"Aprendizaje de apodos y de aclaraciones").

Verificado el 2026-10-04 en <https://github.com/Gentleman-Programming/engram>, en su `DOCS.md`
(<https://raw.githubusercontent.com/Gentleman-Programming/engram/main/DOCS.md>) y en la versión
3.0.0 instalada:

- Licencia MIT. Un binario en Go con SQLite y búsqueda de texto FTS5; el archivo vive por
  omisión en `~/.engram/engram.db`. Se define como "a curated project memory, not a transcript
  sink", para agentes de programación.
- API HTTP local (`engram serve`, `127.0.0.1:7437`). El token opcional (`ENGRAM_HTTP_TOKEN`)
  sólo protege los borrados, la exportación y la importación; sin token, las rutas quedan
  abiertas.
- Los datos se separan por nombre de proyecto y por alcance (`project`, `personal`, `global`).
  No hay ningún mecanismo documentado que impida leer las memorias de otro proyecto en la misma
  base local.
- Engram Cloud se puede alojar por cuenta propia sobre PostgreSQL, con permisos por proyecto
  denegados por omisión. Es una capa de sincronización: la base SQLite local sigue siendo la
  autoritativa.
- Las relaciones entre observaciones (`supersedes`, `conflicts_with`, `compatible` y otras) las
  juzga el agente con el modelo. La búsqueda documentada es FTS5; existe una columna para
  embeddings, pero no se describe una búsqueda por significado.
- No está documentado como biblioteca: desde Python sería un proceso aparte, por HTTP.

Lectura:

- **Estado y memoria son dos necesidades distintas.** La falla de la conversación es de estado
  (qué tiene abierto cada persona y qué puede hacer ahora), que tiene que ser exacto, cambiar en
  la misma transacción que los efectos y quedar aislado por cliente. Engram guarda notas y las
  encuentra por texto: como almacén de estado sumaría una segunda fuente que se puede desfasar
  de PostgreSQL, que es la clase de falla que ya existe.
- **Para la memoria por integrante, la idea vale.** Hoy la IA recibe sólo doce mensajes o seis
  horas, sin los toques de botones. De Engram conviene tomar el diseño: observaciones con tipo y
  clave de tema que se actualizan en lugar de duplicarse, resúmenes por conversación, búsqueda
  que acerca sólo lo relacionado, fechas de revisión y de vencimiento, y la relación "esto
  reemplaza a aquello".
- **No como componente:** el aislamiento entre clientes dependería de un nombre que pasa quien
  llama; sería un segundo almacén al que hacerle respaldo, borrado y auditoría; y sería un
  proceso aparte, en otro lenguaje, con una interfaz que cambia rápido. Su núcleo es chico de
  construir en PostgreSQL, que ya trae búsqueda de texto.

## 8. Veredicto para Leda y decisiones del usuario

**Qué se puede lograr.** Un project manager digital que organiza, sigue, recuerda y deja todo
registrado se puede lograr, y en constancia, memoria, disponibilidad y trazabilidad puede
superar a una persona. El juicio, las prioridades y el trato con las personas siguen siendo
humanos; la constitución ya lo establece. Una conversación sin fallas en todas las situaciones
no es una meta alcanzable hoy: la meta realista es que nunca haya un efecto mal hecho, que la
persona siempre tenga una salida y que la conversación sea buena la mayoría de las veces.

**La estructura.** PostgreSQL con las garantías en el código, y la IA que interpreta y redacta,
son correctos. Jev es la pieza menos probada y falta medir su aporte. Lo que hay que cambiar
es el cimiento de la conversación: estado explícito, circuitos declarados, situaciones
generales resueltas una sola vez, y pruebas hechas con conversaciones reales contra el modelo
real, corridas varias veces.

**Lo incómodo.** Lo que el mercado vende hoy es seguimiento firme con poca conversación, y buena
parte de eso Leda ya lo tiene construido. El esfuerzo de los últimos cinco días se fue en la
conversación de un circuito de once, con datos ficticios y un solo evaluador que conoce el
guion. Ningún equipo real usó Leda todavía.

**Decisiones del usuario (2026-10-04).** El usuario llama **el Motor** a la línea de trabajo que
forman (definición en [`AGENTS.md`](../../AGENTS.md), "Nombres que usamos").

1. Construir un motor chico de conversación dentro de Leda, sin marcos de terceros con licencia.
2. No usar Engram como componente; tomar su diseño para una memoria por integrante en
   PostgreSQL, más adelante y con su propio ADR. El motor de conversación se diseña en tres partes: estado
   exacto, registro completo de la conversación y memoria.
3. Recortar el alcance: por ahora Leda no crea tareas ni objetivos por chat; hace seguimiento.
   Principio: por chat, hechos del trabajo; por la web, su estructura.
4. Cargar las tareas primero con una importación por archivo que hace el administrador y,
   después, con un formulario en el tablero del cliente.
5. Arrancar limpio en una rama nueva (`feat/motor-de-conversacion`), con los flujos A, B y C
   congelados, y escribir el diseño antes del código en los ADR 0017 y 0018.
6. Reglas de trabajo: cada hallazgo de conversación es primero una conversación de prueba; la
   evidencia son conversaciones reales contra la IA real, corridas varias veces; una suite en
   verde o la auditoría de otro agente no prueban que la conversación funcione.
7. Reglas de conversación para el motor de conversación: los botones son atajos (lo que hace un botón también
   vale escrito) y un tema a la vez, con tres salidas ante un cambio de tema.

Quedan sin decidir, para esos dos ADR: qué circuitos quedan por chat, qué contesta Leda si le
piden una tarea por chat, cómo es la importación, qué decide la IA y qué decide el código (la
regla del mozo), si una confirmación que crea o cambia algo puede hacerse por escrito, los
criterios de la prueba chica, la IA a usar y el aporte de Jev.

El estado y el orden de trabajo están en [`STATUS.md`](../STATUS.md); los resultados de cada
flujo, en la [bitácora de flujos](../product/bitacora-de-flujos.md).

## 9. Qué quedó sin verificar

- Todas las cifras marcadas [VC]: PIA, MiChamba, Chaser, Wrike, Asana y ClickUp.
- Si algún agente de suite implementa una escalera garantizada o una máquina de estados de
  aprobación. No se encontró en las páginas leídas, lo que no prueba que no exista. No cargaron
  el centro de ayuda de Asana ni las páginas de Gartner y BusinessWire.
- La mayoría de los puntos de la sección 5 (Gartner, PMI, el estudio de CHI, Air Canada, Cursor
  y Klarna) sale de resúmenes de resultados de búsqueda; esas páginas no se abrieron.
- El pass^k oficial en los dominios de texto para los modelos de mediados de 2026 (GPT-5.6-sol,
  Claude Opus 5, DeepSeek flash) no está publicado. Hay tablas de terceros con hasta 99 % sin
  pass^k, que no son comparables.
- La comparación de costo y latencia de Rasa es investigación del vendedor, con GPT-4, de 2024.
- No se encontraron mediciones para diálogos en español, por Telegram o de gestión de proyectos
  en equipos chicos.
- El recorte de Spinach a reuniones se leyó sólo en su página de inicio actual.
- De Engram no están documentados la concurrencia de varios procesos que escriben ni su uso
  como biblioteca; `mem_judge` se conoce por su interfaz, no por su implementación.
- En la revisión interna no se corrió ninguna prueba, así que no se sabe si la suite pasa en
  cada lado. El reparto entre capa sólida y conversación dentro de los archivos mezclados es
  una estimación. No se comprobó si los cambios de la rama de flujo se pueden traer a `main`
  sin conflictos.
- Hay una diferencia sin resolver entre los dos relevamientos de `llm.py`: uno informa que no
  existe un plazo total por llamada (un turno quedó en silencio y el arreglo está decidido y sin
  construir); el otro informa que la rama tiene `llamar_con_plazo`. Hay que contrastarlo con el
  código antes de traer esa pieza.
