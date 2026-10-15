---
name: Leda
description: La estructura del trabajo de cada equipo, en el celular dentro de Telegram.
colors:
  slate-top: "#2a3134"
  slate-bottom: "#1b2023"
  slate-raised: "#283034"
  ink: "#ecebe6"
  ink-soft: "#b9bab5"
  ink-mute: "#9fa19e"
  hairline: "rgba(236, 235, 230, 0.08)"
  line: "rgba(236, 235, 230, 0.12)"
  line-strong: "rgba(236, 235, 230, 0.30)"
  state-waiting: "#e3a27a"
  state-doing: "#9cc7a4"
typography:
  display:
    fontFamily: "Source Sans 3, system-ui, sans-serif"
    fontSize: "38px"
    fontWeight: 600
    lineHeight: "44px"
    letterSpacing: "-0.02em"
    fontFeature: "\"tnum\" 1, \"lnum\" 1"
  title:
    fontFamily: "Source Sans 3, system-ui, sans-serif"
    fontSize: "17px"
    fontWeight: 600
    lineHeight: "24px"
    letterSpacing: "-0.005em"
    fontFeature: "\"tnum\" 1, \"lnum\" 1"
  body:
    fontFamily: "Source Sans 3, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: "22px"
    fontFeature: "\"tnum\" 1, \"lnum\" 1"
  body-sm:
    fontFamily: "Source Sans 3, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: "20px"
    fontFeature: "\"tnum\" 1, \"lnum\" 1"
  label:
    fontFamily: "Source Sans 3, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: "20px"
    fontFeature: "\"tnum\" 1, \"lnum\" 1"
  numeral:
    fontFamily: "Source Sans 3, system-ui, sans-serif"
    fontSize: "20px"
    fontWeight: 400
    lineHeight: "24px"
    fontFeature: "\"tnum\" 1, \"lnum\" 1"
  caption:
    fontFamily: "Source Sans 3, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: "16px"
    fontFeature: "\"tnum\" 1, \"lnum\" 1"
  micro:
    fontFamily: "Source Sans 3, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: "16px"
    fontFeature: "\"tnum\" 1, \"lnum\" 1"
rounded:
  focus: "4px"
  day: "8px"
  group: "12px"
  pill: "999px"
spacing:
  hair: "2px"
  xxs: "4px"
  xs: "6px"
  sm: "8px"
  bar-inset: "12px"
  row: "14px"
  gutter: "16px"
  section: "20px"
  hero: "28px"
components:
  button-new:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.pill}"
    padding: "0 16px 0 12px"
    height: "40px"
  task-group:
    backgroundColor: "{colors.slate-raised}"
    textColor: "{colors.ink}"
    rounded: "{rounded.group}"
  task-row:
    textColor: "{colors.ink}"
    typography: "{typography.title}"
    padding: "14px 16px"
  done-group:
    backgroundColor: "rgba(236, 235, 230, 0.02)"
    textColor: "{colors.ink-mute}"
    rounded: "{rounded.group}"
    padding: "12px 16px"
  week-day:
    textColor: "{colors.ink-mute}"
    typography: "{typography.caption}"
    rounded: "{rounded.day}"
    padding: "8px 0"
  week-day-today:
    backgroundColor: "rgba(236, 235, 230, 0.04)"
    textColor: "{colors.ink}"
    rounded: "{rounded.day}"
  tab-bar:
    backgroundColor: "{colors.slate-bottom}"
    padding: "6px 12px"
    width: "390px"
  tab-item:
    textColor: "{colors.ink-mute}"
    typography: "{typography.caption}"
    height: "52px"
  tab-item-active:
    textColor: "{colors.ink}"
    typography: "{typography.caption}"
    fontWeight: 600
  tab-item-active-rule:
    backgroundColor: "{colors.ink}"
    rounded: "{rounded.focus}"
    width: "28px"
    height: "2px"
---

# Design System: Leda

> **Estado (2026-10-15).** Este sistema se registró a partir de las dos referencias aprobadas por el usuario,
> `.impeccable/mocks/decision/r7-profundidad.html` (Marcos, referente: «Mis tareas», «Mi área», «Mis pedidos») y
> `.impeccable/mocks/decision/r7-profundidad-direccion.html` (Ismael, Dirección: «Mis tareas», «Áreas», «Equipo»); las dos
> llevan tres pestañas en la barra pegada al borde de abajo que el usuario aceptó en `live` el 2026-10-15. **La app real
> de `web/` todavía no se migró**: sigue con el estilo anterior (oscuro, monoespaciado). Lo que aquí se describe
> es la dirección elegida, con ajustes pendientes que el usuario anunció; la pantalla de una tarea abierta aún no
> existe en este estilo. Al migrar `web/`, volver a documentar desde el código.

## Overview

**Creative North Star: "El pizarrón técnico con profundidad"**

Leda en el celular se lee como un pizarrón de obra bien llevado: lo más importante del día dicho en grande,
y todo lo demás en calma. El fondo es una pizarra oscura que baja de un gris azulado a otro más profundo, con
una luz muy suave en la parte de arriba, como si el pizarrón estuviera iluminado desde el techo. Sobre ese
fondo, una tinta clara y cálida escribe todo; el color aparece sólo cuando un estado tiene algo que decir.

La densidad es la de una herramienta que se mira en segundos: una cabecera con quién soy y qué día es, un
resumen grande con lo que vence, la semana con hoy recuadrado, la lista de tareas agrupada en una superficie
apenas elevada y, al pie, una barra pegada al borde para cambiar de vista con el pulgar. Nada brilla, nada es vidrio,
nada está dibujado a mano: la profundidad sale del gradiente, de una superficie un tono más clara y de filetes
casi invisibles.

Este mundo rechaza explícitamente la lista gris con un único acento y la letra monoespaciada como voz
principal del estilo anterior, los prefijos «> » en los botones, el trazo de tiza o dibujado a mano, el brillo,
el vidrio y el neón, los íconos dentro de círculos y el amarillo como color principal.

**Key Characteristics:**
- Fondo pizarra en degradé vertical con una luz suave arriba, fijo detrás del contenido.
- Una sola familia, Source Sans 3, en dos pesos (400 y 600), con cifras tabulares y de línea.
- Color sólo en el estado: esperando en durazno tostado, en curso en verde salvia.
- Un resumen grande arriba; el resto, chico y tranquilo.
- Tareas agrupadas en una superficie elevada con filetes entre filas.
- Barra de pestañas pegada al borde de abajo, de ancho completo, con ícono de trazo y palabra en cada pestaña.

## Colors

Una paleta de pizarra y tinta, sin acento de marca: el único color es el del estado de una tarea.

### Primary
- **Tinta de tiza limpia** (ink): todo el texto principal, los títulos de tarea, el número del día de hoy, el
  borde del botón al pasar el puntero, el contorno de foco y el fondo de la selección. Es un blanco cálido, no
  puro, para que el contraste sobre la pizarra no corte.

### Secondary
- **Durazno tostado** (state-waiting): el estado «esperando», la cifra del resumen grande cuando habla de lo que
  vence y el aviso «1 vence» bajo un día de la semana. Es el color de lo que necesita atención; nunca un fondo.
- **Verde salvia** (state-doing): el estado «en curso». Sólo como texto del estado.

### Neutral
- **Pizarra alta** (slate-top) y **pizarra honda** (slate-bottom): los dos extremos del fondo, de arriba hacia
  abajo. La honda también es el color del `html`, el del texto sobre la selección y el fondo liso de la barra
  de pestañas, que así se funde con el pie del degradé.
- **Pizarra elevada** (slate-raised): la superficie del grupo de tareas abiertas, un tono por encima del fondo.
- **Tinta suave** (ink-soft): la explicación del resumen, las fechas de cada tarea, el detalle de lo que falta,
  los números de los días que no son hoy, los nombres de las terminadas.
- **Tinta apagada** (ink-mute): el área junto al nombre, la fecha de hoy, el conteo, los encabezados de sección,
  el estado «sin empezar», las pestañas no activas.
- **Filete** (hairline): el borde de los grupos y la línea entre filas.
- **Línea** (line): el filete superior de la barra de pestañas, su único borde.
- **Línea marcada** (line-strong): el borde del botón «Nueva» y el recuadro del día de hoy.

Los velos de tinta (la misma tinta a 2 %, 3 %, 4 %, 5 % y 6 % de opacidad) dan los estados de hover, de
presión, el fondo de las terminadas, el día de hoy y la luz de arriba; están en el sidecar.

### Named Rules
**La regla del color que dice algo.** El color aparece sólo donde un estado tiene algo que decir: esperando,
en curso, lo que vence. Ningún título, botón, fondo ni ícono lleva color de estado por decoración.

**La regla sin amarillo.** El amarillo nunca es color principal ni de realce. Lo que pide atención va en durazno
tostado.

## Typography

**Display Font:** Source Sans 3 (con system-ui, sans-serif)
**Body Font:** Source Sans 3 (con system-ui, sans-serif)

**Character:** una sans humanista técnica, nítida y sin estridencia; dos pesos alcanzan para toda la jerarquía
porque la escala de tamaños y los tonos de tinta hacen el resto. Todas las cifras son tabulares y de línea
(`"tnum" 1, "lnum" 1`), para que fechas y conteos se alineen como en una planilla.

### Hierarchy
- **Display** (600, 38px, 44px de línea, -0.02em): sólo el resumen grande («1 vence mañana»). Una por pantalla.
- **Title** (600, 17px, 24px, -0.005em): el título de cada tarea y el nombre de la persona en la cabecera (este
  último sin el ajuste de letra).
- **Body** (400, 16px, 22px): la explicación del resumen: qué tarea y qué le falta.
- **Body small** (400, 15px, 20px): el detalle de una tarea («Falta la firma de Ismael; se ocupa Ismael.»). Las
  fechas de tarea, las terminadas y el botón «Nueva» usan 15px con 24px de línea; el botón, en 600.
- **Label** (400, 14px, 20px): el estado de una tarea, el conteo, la fecha de hoy. En 600 y tinta apagada, el
  encabezado de sección («Terminadas esta semana»). Siempre en minúscula de oración, nunca en versalitas.
- **Numeral** (400, 20px, 24px): el número de cada día de la semana; 600 y tinta plena en hoy.
- **Caption** (400, 13px, 16px): el nombre del día y la palabra de cada pestaña.
- **Micro** (400, 12px, 16px): «hoy» y «1 vence» bajo el día.

### Named Rules
**La regla de los dos pesos.** Sólo 400 y 600. La jerarquía se arma con tamaño y tono de tinta, no con negritas
extra ni con otra familia.

**La regla de las cifras parejas.** Toda cifra es tabular. Una fecha nunca baila de ancho entre filas.

## Layout

Una columna para el celular dentro de Telegram, pensada a 390px de ancho con un margen lateral de 16px (gutter).
El orden de la primera pantalla es fijo: cabecera (nombre y área a la izquierda, fecha debajo; «Nueva» a la
derecha), resumen grande, semana, lista agrupada, terminadas, y la barra de pestañas pegada al borde de abajo.

El ritmo vertical es de 20px entre bloques (cabecera arriba, semana, lista, encabezado de sección), 28px antes
del resumen grande para darle aire, y 6px entre las líneas del resumen. La semana es una grilla de cinco
columnas iguales (lunes a viernes) con 8px de separación. Cada fila de tarea es una grilla de dos columnas
(título a la izquierda, fecha a la derecha, 16px entre ellas) con el estado y el detalle en renglones de ancho
completo debajo, separados 2px.

El contenido reserva abajo el alto de la barra (unos 110px más el área segura del dispositivo) para que la última
fila nunca quede tapada. La barra ocupa el ancho completo (de 0 a 390px, sin margen) y suma debajo de las
pestañas 10px más `env(safe-area-inset-bottom)`.

## Elevation & Depth

La profundidad es tonal, no de sombras. El fondo es un degradé vertical de pizarra alta a pizarra honda, fijo
al viewport, con una elipse de luz al 5 % de tinta centrada arriba que se apaga hacia el 72 %. Encima, el grupo
de tareas sube un tono (pizarra elevada) y se separa con un filete; las terminadas apenas se insinúan con un velo
al 2 %. La barra de pestañas tampoco flota: se apoya en el borde de abajo, con el fondo liso de pizarra honda
y un filete arriba que la separa del contenido. El sistema no tiene sombras.

### Shadow Vocabulary
- **Ninguna.** No hay `box-shadow` en el sistema; la separación la dan el tono, el filete y el degradé.

### Named Rules
**La regla de la luz de arriba.** La profundidad viene del degradé y de la luz suave del techo, no de sombras
sobre cada tarjeta. Ninguna superficie lleva sombra, tampoco la barra de pestañas.

**La regla sin brillo.** Nada de resplandores, desenfoque de fondo, vidrio ni neón. Si algo tiene que destacar,
lo hace con tamaño o con el color de su estado.

## Shapes

Esquinas suaves y consistentes, de más chicas a más grandes según el tamaño del objeto: 4px en el contorno de
foco y en la raya de la pestaña activa, 8px en cada día de la semana, 12px en los grupos de tareas y
terminadas, y forma de píldora (999px) para el botón «Nueva». La barra de pestañas no tiene esquinas: va de
borde a borde. Los bordes son siempre de 1px y de tinta
translúcida; ningún borde es de color. Los íconos son de trazo (1.5px, extremos y uniones redondeados, sin
relleno), a 20px en el botón y 24px en las pestañas, y nunca van dentro de un círculo o una caja.

## Components

### Buttons
Un único botón visible por pantalla, sobrio y táctil.
- **Shape:** píldora (999px), 40px de alto.
- **«Nueva»:** sin fondo, borde de 1px en línea marcada, tinta plena, 15px en 600, un ícono «+» de trazo de 20px
  a la izquierda con 6px de separación; relleno de 12px a la izquierda y 16px a la derecha. Lleva
  `aria-label="Nueva tarea"`.
- **Hover / Focus:** el borde pasa a tinta plena; al presionar, un velo de tinta al 6 %. Foco: contorno de 1.5px
  en tinta, separado 3px, con esquina de 4px.

### Cards / Containers
- **Grupo de tareas abiertas:** lista ordenada sobre pizarra elevada, borde de filete, esquina de 12px, sin
  sombra, con un filete entre filas.
- **Fila de tarea:** es un botón entero. Relleno de 14px por 16px. Título (Title) y fecha comprometida (15px,
  tinta suave, alineada a la derecha); debajo, el estado (Label) en su color: esperando en durazno, en curso en
  salvia, sin empezar en tinta apagada; y, si hace falta, el detalle en tinta suave que dice qué falta y quién se
  ocupa, o quién la pidió. Hover: velo al 3 %; presión: velo al 6 %.
- **Terminadas esta semana:** encabezado de sección (14px, 600, tinta apagada) y un grupo silencioso con velo al
  2 %, filete y 12px de esquina; cada fila con el nombre en tinta suave y la fecha en tinta apagada.

### Navigation
- **Barra de pestañas pegada al borde:** fija al pie del viewport, de ancho completo (390px, desde el borde
  izquierdo), fondo liso de pizarra honda, un filete de 1px en línea sólo arriba, sin esquinas y sin sombra.
  Siempre tres pestañas, en una grilla de tres columnas iguales: para un referente «Mis tareas», «Mi área» y
  «Mis pedidos»; para Dirección «Mis tareas», «Áreas» y «Equipo». Relleno de 6px arriba y 12px a los lados, y
  debajo 10px más el área segura.
- **Cada pestaña:** ícono de trazo de 24px arriba y la palabra abajo, siempre los dos, 52px de alto mínimo, 4px
  entre ícono y palabra, la palabra en Caption (13px con 16px de línea).
- **Estados:** sin fondo ni píldora en ningún estado. Inactiva en tinta apagada; hover en tinta plena; activa
  (`aria-current="page"`) en tinta plena y 600, con una raya de tinta de 28px por 2px y esquina de 4px apoyada
  sobre la pestaña, 7px por encima de su borde superior.

### Resumen grande (signature)
Lo primero que se lee. Una frase en Display con la cifra destacada en durazno tostado («**1** vence mañana»),
debajo la tarea y lo que le falta en Body y tinta suave, y el conteo («3 abiertas · 1 esperando») en Label y
tinta apagada, separados por un punto medio. Sale siempre de datos reales: si dice «2 vencen esta semana», tiene
que haber dos.

### Semana (signature)
Cinco días hábiles en columnas iguales: nombre del día (Caption), número (Numeral) y una línea Micro reservada
para «hoy» o «N vence» (en durazno). Hoy va recuadrado: borde en línea marcada, velo al 4 %, esquina de 8px,
número en 600 y tinta plena, con `aria-current="date"`.

## Do's and Don'ts

### Do:
- **Do** usar el degradé de pizarra alta a pizarra honda con la luz suave de arriba como único fondo de pantalla.
- **Do** escribir todo en Source Sans 3, en 400 y 600, con cifras tabulares y de línea.
- **Do** reservar el color para el estado de una tarea y para lo que vence (durazno tostado y verde salvia).
- **Do** abrir cada vista con el resumen grande y dejar el resto en tamaños chicos y tintas suaves.
- **Do** agrupar las tareas en la superficie elevada con filetes entre filas y 12px de esquina.
- **Do** mantener la barra de pestañas pegada al borde de abajo, de ancho completo y con fondo liso, con ícono
  y palabra en cada una de las tres pestañas, y marcar la activa con la raya de tinta de arriba.
- **Do** decir en el detalle de una tarea qué falta y quién se ocupa, en palabras de todos los días.

### Don't:
- **Don't** usar una letra monoespaciada como voz principal.
- **Don't** poner prefijos «> » ni otros signos de terminal en los botones.
- **Don't** usar trazos de tiza, texturas o dibujos a mano, aunque el mundo sea un pizarrón.
- **Don't** usar brillo, resplandor, vidrio, desenfoque de fondo ni neón.
- **Don't** meter íconos dentro de círculos o cajas; el ícono va suelto, de trazo.
- **Don't** usar el amarillo como color principal ni de realce.
- **Don't** volver a la lista gris con un único acento de color.
- **Don't** agregar sombras a nada: ni a tarjetas, ni a filas, ni a la barra de pestañas.
- **Don't** volver a la barra flotante en cápsula ni marcar la pestaña activa con una píldora de fondo.
