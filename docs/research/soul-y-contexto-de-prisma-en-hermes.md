# Aprendizajes: SOUL.md y contexto operativo de Prisma en Hermes

- **Fecha:** 2026-10-02
- **Fuente:** paquete interno del usuario `PRISMA-PACK-SOUL-Y-CONTEXTO-HERMES-20261002`
  (fuera del repositorio, uso interno: contiene nombres y contexto del equipo). Es trabajo
  propio del usuario: el intento anterior de construir Prisma sobre Hermes, con otra IA.
  Huellas del manifiesto verificadas el 2026-10-02.
- **Para qué:** diseñar C0-13, la voz de Leda (`odd/tasks/circuitos-al-flujo-nuevo.md`,
  rama de flujo). Complementa [`hermes-agent.md`](hermes-agent.md), "Cómo arma las
  instrucciones del agente".
- **Qué no se copia acá:** los originales ni ningún nombre o responsabilidad del equipo;
  el repositorio es público.

## La separación que funcionó

Dos archivos con preguntas distintas: `SOUL.md` responde **quién es y cómo se expresa**;
el contexto del proyecto (`.hermes.md`) responde **en qué trabaja y qué reglas estables
respeta al interpretar el trabajo**. Ninguno concede permisos ni reemplaza datos oficiales.
La personalidad no absorbe el negocio y el contexto no se vuelve una segunda personalidad.

## Dónde va cada frase (antes de escribirla)

1. ¿Describe cómo es y cómo habla? → la voz.
2. ¿Explica el negocio o una regla operativa estable? → el contexto.
3. ¿Es un dato que cambia mientras se trabaja? → la fuente oficial (en Leda, PostgreSQL).
4. ¿Impide una operación no autorizada? → un control en el código, no sólo texto.
5. ¿Es un procedimiento extenso? → un procedimiento aparte.
6. ¿Es una preferencia de una persona? → una preferencia gobernada, no la voz global.

## Cómo se escribe una regla

Conducta observable, no adjetivos: "cálida" se traduce en reconocer lo que la persona dijo
y preguntar sin acusar. Cada regla responde **condición, conducta, límite y comprobación**.
Una norma por párrafo, sin depender de mayúsculas ni repeticiones para darle prioridad;
ejemplos rotulados como ejemplos, nunca como respuestas para copiar; sin nombres propios
en los ejemplos.

## Qué no va en ninguno

Credenciales; identificadores del canal usados como permisos; estados vivos de tareas;
historial de conversaciones; el documento maestro entero; promesas de capacidades no
habilitadas; reglas para reconocer una frase de una prueba. Un archivo más largo no es más
fiel: suma conflictos, consume contexto y esconde reglas en la parte que se trunca.

## Reglas de voz que conviene llevar a Leda

- **Cuatro frases que no son lo mismo:** "gracias por avisarme" (acuse), "quedó guardado"
  (efecto, sólo con comprobante real), "puedo preparar el cambio" (propuesta) y "no pude
  verificarlo" (límite de la evidencia, no prueba de que no exista). No decir "queda
  registrado" sin una confirmación real.
- **No encontrar no es que no exista;** no poder consultar es otra cosa.
- **Cuando falta un dato:** explicar brevemente para qué hace falta y hacer una sola
  pregunta clara.
- **Reconocer primero** lo que la persona dijo o hizo.
- **No anunciar** "voy a consultar": consultar y responder con el resultado.
- **Firme sin hostilidad;** que sea seguro decir "no sé todavía" o "necesito ayuda".
- **Brevedad por defecto, sin dejar a la persona sin el próximo paso.** El original
  limitaba tanto que podía dejar a alguien sin saber cómo seguir; en Leda lo resuelve la
  constitución §8.

## Lo que el texto no puede hacer solo

Saludar una vez por persona y por día necesita reloj y estado persistente, no una frase;
confidencialidad necesita filtrar los datos antes de que lleguen al modelo; una
prohibición escrita no reemplaza un bloqueo en el código. El archivo correcto en disco, el
contenido que efectivamente se cargó y el comportamiento real son **tres evidencias
distintas**.

## Cómo validar un cambio de voz

Cuatro evidencias separadas: (1) el texto está bien escrito y no se contradice; (2) se
cargó la versión correcta (huella); (3) los controles impiden efectos aunque el modelo se
equivoque; (4) una persona recibe respuestas veraces, claras y con próximo paso. Primero
una tanda de casos humanos por el recorrido real (familias de casos, no un guion), después
Telegram con datos ficticios, una interacción por vez. Ante el primer fallo: parar,
clasificar la causa y corregir el mecanismo, no la frase.

## Cómo se cambia la voz

Sólo a pedido de quien administra Leda; con la diferencia legible (antes, después, motivo y
qué conducta cambia), lo que no cambia, una versión identificable y el rollback exacto; y
verificando la carga y el comportamiento después de reiniciar.
