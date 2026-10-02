# Acceso al tablero por enlace personal

**Estado:** en curso
**Creado:** 2026-09-22
**Precondición cumplida:** puerto de lectura (`70685f3`) y aislamiento entre
clientes (`675184a`).

## Decisión de producto tomada

Una persona le pide el tablero a Leda por Telegram y recibe un enlace
personal que vence. Sin usuarios, sin contraseñas.

Se eligió sobre las alternativas —clave compartida por empresa, o registro con
usuario y contraseña por persona— porque **reusa la identidad que ya funciona**.
Telegram ya dice quién escribe, y Leda ya vincula esa persona con su
membresía, su área y su autoridad. No hay que construir un sistema de usuarios
nuevo ni que nadie recuerde otra contraseña.

Un registro por persona se puede agregar después si un cliente lo pide; esta
decisión no lo impide.

## Modelo de amenaza

Un enlace que da acceso a los datos de un cliente es una credencial. Contra qué
protege el diseño:

| Amenaza | Control |
|---|---|
| El enlace se reenvía o queda en un historial | Vence. La ventana acota el daño, no lo evita. |
| Se filtra la base | Sólo se guarda el hash del token, nunca el valor. |
| Alguien pide el tablero de otro espacio | El token se emite contra la membresía de quien lo pide; el espacio sale del token, no de la URL. |
| Una persona deja el equipo | La membresía se revalida **en cada pedido**, no sólo al emitir. |
| El enlace se publica en el grupo | Sólo se entrega por chat privado. |
| Un token permite escribir más de lo que corresponde | Alcanza el puerto de lectura y la configuración del propio espacio, nada más. Ningún efecto de dominio, ningún dato de plataforma, y cada escritura atribuida en la auditoría. |

No protege contra alguien que controla el Telegram de la persona. Eso ya vale
para todo el resto del sistema.

## Decisiones de diseño

**D1 — Sólo se guarda el hash.** El valor viaja una vez, en el enlace, y no
queda en la base. Mismo principio que las capacidades de ADR 0003.

**D2 — El enlace vale varias veces dentro de su ventana.** De un solo uso
rompería al recargar la página. La ventana es el control, no el conteo.

**D3 — El espacio sale del token, nunca de la URL.** Una URL con
`?workspace=` sería el mismo error que la frontera ya rechaza en
`confirmar_borrador_tarea`: confiar el espacio a quien llama.

**D4 — La autoridad se revalida en cada pedido.** Tener un token vigente no
alcanza: la membresía tiene que seguir activa. Es la regla 6 de la frontera.

**D5 — Resolver el token necesita una frontera propia.** La búsqueda ocurre
*antes* de conocer el espacio, así que no puede correr bajo `espacio()`. Va por
una función acotada, al estilo de la frontera dedicada que ya existe para la
conversión de Unidad 1A (`src/leda/db.py:68`). No se le da a la aplicación
una consulta general de tokens.

**D6 — CORREGIDA. Lectura y configuración propia.** Decía "sólo lectura: el
adaptador expone el puerto de lectura y nada más". Quedó incorrecta el mismo
día: el usuario aclaró que el tablero no es un visualizador, sino la superficie
desde la que un cliente configura Leda. Telegram es el intercomunicador; la
configuración viene del tablero.

Lo que sí se conserva del espíritu original: el tablero alcanza **un solo
espacio**, el propio, y nunca datos de plataforma. Y toda escritura de
configuración desde una superficie web queda **atribuida en la auditoría**,
igual que cualquier otro efecto. Ver
[`ADR 0004`](../../docs/decisions/0004-dos-superficies-separadas.md).

**D7 — La duración es configuración del cliente, no una constante.** El
usuario confirmó que un administrador va a poder cambiarla desde el tablero
cuando exista esa pantalla. Según la tabla de `docs/product/que-es-leda.md`,
eso la ubica del lado de la configuración por cliente, no del núcleo: vive en
`workspace_setting`, con 30 minutos por defecto cuando no hay fila. Mismo
patrón que el tope diario de mensajes (`src/leda/despachador.py:271`).

Decidirlo ahora cuesta nada; hacerlo después exigiría una migración y tocar el
núcleo. La pantalla de administración, cuando llegue, sólo escribe ese valor.
`src/leda/autoridad.py:89` ya distingue a un administrador, así que esa
pantalla tendrá contra qué autorizar.

## Alcance: el menor circuito útil

Una persona pide el tablero por Telegram, recibe su enlace, lo abre, y ve el
estado de su espacio. Entero, punta a punta. Tres capas parciales sin nada
visible serían la deriva que este proyecto ya conoce.

## Checklist

- [ ] **T1 (ROJO)** — Pruebas de las cinco propiedades del modelo de amenaza:
      token vencido rechazado, token de otro espacio no alcanza a este, hash y
      no valor en la base, membresía dada de baja pierde acceso, y el enlace no
      sale por el grupo.
- [ ] **T2** — Migración `0006`: tabla de accesos con RLS, función acotada de
      resolución, y la frontera de conexión que la ejecuta.
- [ ] **T3** — `src/leda/tablero.py`: emitir y resolver.
- [ ] **T4** — Entrega por Telegram: la persona pide, Leda responde con el
      enlace por privado.
- [ ] **T5** — Adaptador HTTP en `gateway.py` sirviendo el puerto de lectura.
- [ ] **T6 (VERDE)** — T1 pasa y el circuito completo funciona.
- [ ] **T7** — `frontera.md`: el adaptador HTTP de lectura pasa a existir.

## Criterios de aceptación

1. Las cinco propiedades del modelo de amenaza tienen prueba.
2. El valor del token no aparece en la base bajo ninguna consulta.
3. Ninguna respuesta del adaptador incluye datos de otro espacio.
4. El adaptador expone lectura y configuración del propio espacio, y nada más:
   ningún efecto de dominio y ningún dato de plataforma. Toda escritura queda
   atribuida en la auditoría a la persona del token.
5. La suite completa sigue en verde.

## Resuelto con el usuario

- **Duración: 30 minutos**, y configurable por administrador desde el tablero
  cuando exista. Por eso vive en `workspace_setting`, no en el código. Ver D7.

## Abierto, sin bloquear esta unidad

- **Qué ve cada persona.** Por ahora, todo el espacio: un integrante y un
  referente ven lo mismo. Acotarlo por rol es otra decisión de producto, y hoy
  el puerto de lectura no distingue. Conviene decidirlo antes de que el tablero
  se le muestre a un cliente real.

## Verificación aplicable

TDD habilitado. Runner: `.venv/Scripts/python.exe -m pytest -q`.

## Estrategia de entrega

`ask-on-risk`. Estimo por encima de las 400 líneas autoradas. Si al implementar
se confirma, se parte en dos: la credencial y su entrega, después el adaptador.

## Progreso

- 2026-09-22 — Documento creado con el modelo de amenaza y las decisiones de
  diseño. D7 agregada al confirmarse que la duración será configurable.
- 2026-09-22 — D6 corregida: el tablero no es de sólo lectura.

## EN PAUSA — implementación sin comitear

La credencial se implementó parcialmente y **quedó sin comitear**. Hay archivos
nuevos en el árbol de trabajo:

- `db/migrations/0006_dashboard_access.sql` y su rollback
- `src/leda/tablero.py`
- `tests/test_tablero.py`
- cambios en `db/esquema.sql` y `tests/test_task_intake.py`

El estado era coherente y verde cuando se detuvo (88 pruebas de los dos
archivos afectados). Quedaba pendiente terminar de sumar la tabla a la prueba
de paridad.

**Por qué se pausó:** la entrevista de alta se le adelantó. Sin ella, cada
cliente nuevo exige que alguien escriba un paquete a mano; y además la
entrevista es la que define qué configuración existe, que es justamente lo que
este tablero tendría que dejar editar.

Nada de lo construido se pierde: la credencial identifica persona y espacio, y
eso sirve igual para leer y para configurar.

## Próximo paso

Retomar después de la entrevista de alta y del panel de plataforma. Al hacerlo,
revisar el alcance del adaptador contra la D6 corregida: además del puerto de
lectura, consume el de configuración.
