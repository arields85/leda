# ADR 0004: el panel de plataforma y el tablero de cliente son dos aplicaciones

- **Estado:** aceptada
- **Fecha:** 2026-09-22
- **Alcance:** toda superficie que no sea la conversacional

## Decisión

Prisma tiene dos superficies web separadas, no una con niveles de permiso.

| | Panel de plataforma | Tablero de cliente |
|---|---|---|
| Quién entra | Quien opera Prisma | Integrantes de un espacio |
| Qué alcanza | Todos los espacios | Sólo el suyo |
| Qué hace | Da de alta clientes, conduce la entrevista de alta | Consulta su estado y ajusta su configuración |
| Cómo se autentica | Credencial propia de plataforma | Enlace personal entregado por Telegram |

## Por qué

**Un error de permisos no puede exponer otro cliente.** En una sola aplicación
con roles, la lista de todos los espacios vive a un `if` de distancia de un
usuario de cliente. Separadas, ese dato no está en el proceso que atiende al
cliente: no hay `if` que equivocar.

Para un producto multi-tenant, que un cliente vea a otro no es un defecto más.
Es el que termina la relación comercial.

**Y la autenticación no puede ser la misma.** El enlace por Telegram funciona
porque Prisma ya conoce a la persona: tiene membresía en un espacio. Un cliente
que todavía no existe no tiene nada de eso, así que la entrevista de alta —que
por definición ocurre antes del espacio— no puede autenticarse así. Es anterior
a la identidad que ese mecanismo necesita.

## Consecuencia sobre la entrevista de alta

`nucleo/alta-de-equipo.md` la define conducida por un administrador de
plataforma. Vive entonces en el panel de plataforma, como formulario guiado y
no como chat: cargar veinte personas con su área y su rol por Telegram es
hostil, y la practicidad acá tiene un costo real en adopción.

Se conserva la disciplina que ese documento pide y que un formulario común
pierde: un bloque por vez, ningún valor completado por defecto en silencio
—cuando hay uno habitual se muestra y se pide confirmación— y lo que no se
contestó queda como faltante, no como vacío.

## Alternativas rechazadas

- **Una sola aplicación con niveles de permiso.** Rechazada por lo de arriba:
  pone el dato de todos los clientes al alcance de un error de autorización.
- **La entrevista por Telegram.** Rechazada por dos motivos: no puede
  autenticar a quien todavía no tiene espacio, y cargar datos estructurados en
  volumen por chat es hostil.
- **El cliente se configura solo desde su tablero.** Rechazada para el alta: el
  documento de núcleo pide que un administrador de plataforma lea y apruebe el
  pack antes de activar el espacio. Ajustar su configuración después sí es
  suyo.

## Consecuencias

- El tablero de cliente **no es de sólo lectura**: ajusta configuración. Esto
  corrige lo que se había escrito al diseñar su credencial.
- La credencial por enlace de Telegram sirve al tablero de cliente y no al
  panel de plataforma, que necesita la suya. Esa decisión queda abierta.
- El pack YAML deja de ser un archivo que alguien escribe y pasa a ser un
  formato de transporte: lo produce la entrevista, una exportación o el
  desarrollo, y lo consume el importador una sola vez para sembrar el espacio.
  Después manda la base.
- Toda escritura de configuración desde una superficie web tiene que quedar
  atribuida en la auditoría, igual que cualquier otro efecto.
