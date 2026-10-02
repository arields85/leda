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
