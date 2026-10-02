# Relevamiento: Hermes Agent (Nous Research)

- **Fecha:** 2026-09-30
- **Pedido:** del usuario, para ver si resuelve algo en lo que Leda está trabado.
- **Fuentes:** sitio y documentación oficial (https://hermes-agent.nousresearch.com/),
  repositorio https://github.com/NousResearch/hermes-agent (clon superficial de `main`,
  último commit del 2026-09-30 22:42Z, alrededor de 400 contribuidores, versión
  v0.21.5 del 2026-09-24, licencia MIT). Las rutas citadas son del repositorio.
- **Veredicto:** no sirve como base de Leda. Tiene tres ideas que conviene tomar,
  dentro del monolito y sin la dependencia.

## Qué es

Un agente personal de propósito general: un bucle de agente con más de 70
herramientas, un gateway de mensajería con más de 25 adaptadores (Telegram incluido),
tareas programadas y memoria persistente. Acepta OpenRouter y otros proveedores.
Sigue en versión 0.x, con parches cada pocos días
(https://github.com/NousResearch/hermes-agent/releases).

## Por qué no sirve como base

Verificado en el código:

- **La fuente de verdad no es PostgreSQL.** Las sesiones viven en SQLite
  (`~/.hermes/state.db`) y la memoria en dos archivos Markdown con tope de caracteres
  (`tools/memory_tool.py:36-39`). PostgreSQL aparece sólo como almacén vectorial
  opcional del complemento Mem0 (`plugins/memory/mem0/_setup.py`), no como estado de
  la aplicación.
- **No aísla clientes.** La clave de sesión separa conversaciones por plataforma, chat
  y participante (`gateway/session.py:682-725`), pero la memoria es común a todo un
  perfil. Varios perfiles se aíslan por directorio (`GATEWAY_MULTIPLEX_PROFILES`,
  `gateway/config.py:46`), no por fila con `workspace_id` y RLS. No hay roles por
  usuario ni un registro de acciones por usuario.
- **Aprende solo, y por defecto.** La revisión en segundo plano está activa por defecto
  (`agent/background_review.py`, `hermes_cli/config_defaults.py:814`) y, si la
  configuración no se puede leer, queda activa. `AGENTS.md` deja fuera el aprendizaje
  persistente sin una decisión explícita.
- **La confirmación es un sí/no sobre la llamada.** Un complemento puede pedir
  aprobación humana antes de una herramienta (`hermes_cli/plugins.py:2038-2050`,
  `tools/approval.py:1104-1116`), pero no hay vista previa guardada, ejecución única,
  verificación ni auditoría como hechos del dominio. Por defecto, la aprobación de
  comandos peligrosos la decide otro modelo: lo opuesto a "el código garantiza".
- **No toca los problemas de conversación de Leda.** No hay nada sobre interpretar
  valores dichos de forma desprolija, responder a partir de hechos, impedir que se
  afirme una acción que no ocurrió ni conversar con una sola rama abierta. Eso lo
  resuelve el [`ADR 0014`](../decisions/0014-flujo-de-un-mensaje.md), no Hermes.

## Ideas que conviene tomar

1. **Proponer lo que se puede aprender después de cada corrección.** Después de un turno,
   un paso aparte revisa la conversación y propone memorias a partir de las
   correcciones de la persona (`agent/background_review.py`). Con `write_approval`, lo
   propuesto queda pendiente hasta que alguien lo aprueba (`tools/write_approval.py`).
   Para Leda, el mecanismo se adapta a las reglas ya fijadas: se aprende sólo de lo
   confirmado, por espacio, a la vista, borrable, auditado y como pista para Jev, no
   como decisión ([`ADR 0005`](../decisions/0005-interpretacion-y-confirmacion.md)
   punto 5; [`ROADMAP.md`](../ROADMAP.md), "Aprendizaje de apodos y de aclaraciones").
2. **Registro durable de entregas.** El gateway detecta un envío que quedó a medias
   (el proceso cayó mientras enviaba) y lo reenvía, marcando la recuperación. Comparar
   con el outbox de Leda antes de decidir si hace falta.
3. **Emparejamiento por mensaje directo con código de un solo uso**, con vencimiento de
   una hora y bloqueo tras cinco intentos fallidos (`gateway/pairing.py`). Comparar con
   los enlaces de activación de Leda (`python -m leda enlaces`).

Ninguna de las tres es urgente. La primera entra en la unidad de aprendizaje del
roadmap; las otras dos, en el endurecimiento del transporte.

## No verificado

- El detalle de `run_agent.py:295` (`skip_background_review`) y qué omite exactamente.
- `gateway/delivery.py`, y los complementos ByteRover, Supermemory y OpenViking.
- El rendimiento con modelos chicos como el que usa Leda.

## Cómo arma las instrucciones del agente (relevamiento del 2026-10-02)

Pedido del usuario, a partir de C0-13 (`odd/tasks/circuitos-al-flujo-nuevo.md`, rama de
flujo): Leda le manda al modelo el núcleo entero en cada turno del camino general (~6.400
tokens) y el alta conducida no lo lee. Clon superficial de `main` en `1a4508e` (2026-10-02);
documentación en `website/docs/` del repositorio, publicada en
https://hermes-agent.nousresearch.com/docs/. Verificado en el código por el agente:
`tools/memory_tool.py:56`, `agent/system_prompt.py:1-8` y `agent/prompt_builder.py:160-168`.

- **`SOUL.md`: identidad y voz, nada más.** Vive en `$HERMES_HOME`, la escribe el usuario,
  va primera y reemplaza la identidad por omisión (`agent/prompt_builder.py:1626-1669`).
  No lleva reglas de proyecto ni rutas (`website/docs/.../personality.md:66-90`). La
  identidad por omisión es una **especificación de conducta** de unas 120 palabras, con
  prohibiciones con nombre y ejemplos ("una pregunta de una línea tiene una respuesta de
  una línea"); el código anota que las listas de rasgos "no cambian nada"
  (`prompt_builder.py:160-168`).
- **El segundo archivo no son reglas: es memoria.** `MEMORY.md` (notas del agente) y
  `USER.md` (perfil del usuario), escritos por el agente, con tope duro de 2.200 y 1.375
  caracteres; una escritura que lo pasa da error y obliga a consolidar
  (`tools/memory_tool.py:56`). Las reglas de proyecto van en `AGENTS.md` y los
  procedimientos, en *skills*.
- **Instrucciones armadas una vez por sesión, en tres capas:** estable (identidad, guías),
  contexto (archivos del proyecto) y volátil (índice de skills, memoria, fecha). El orden
  existe para que el proveedor reuse el comienzo idéntico del texto (caché de prefijo); la
  fecha lleva sólo el día para no romperlo (`agent/system_prompt.py:1-8, 734-797,
  487-490`). Lo que cambia en cada turno no va en las instrucciones: se agrega al mensaje
  del usuario (`agent/turn_context.py:781-785`).
- **Detalle a demanda:** las instrucciones llevan sólo un índice de skills (nombre y
  descripción); el modelo pide el cuerpo con `skill_view` cuando lo necesita
  (`prompt_builder.py:1443-1500`). Medido por Hermes: el texto de skills llegó a ser el 34 %
  de los bytes de resultados de herramientas y se recortó el preámbulo
  (`agent/oneshot_footprint.py:1-17`).
- **Guías según el modelo:** bloques que se agregan sólo a familias de modelos con fallas
  observadas (`prompt_builder.py:340-379`).
- **Un cambio en esos archivos vale desde la sesión siguiente** (o reiniciando).

**Qué sirve para Leda (a decidir con el usuario, C0-13):** separar una "voz" corta de
Leda, siempre presente y escrita como especificación de conducta con ejemplos, de las
reglas que garantiza el código; elegir en el código (no el modelo) qué sección del núcleo
lleva cada circuito, desde los mismos archivos; poner primero lo estable y al final lo que
cambia; y un tope de tamaño por circuito que falle a la vista. **Qué no sirve:** que el
modelo elija sus skills (Leda rutea de forma determinista y usa un modelo chico), la
memoria escrita por el agente (aprendizaje persistente sin decisión) y los archivos por
directorio en lugar de PostgreSQL. **Sin verificar:** si el proveedor de Leda tiene caché
de prefijo, y cuánto pesa el tamaño de las instrucciones en la latencia de un modelo chico.
