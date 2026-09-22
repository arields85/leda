"""La pantalla del tablero.

Adaptador de presentación sobre el puerto de lectura. No consulta la base:
recibe lo que `prisma.lectura` devolvió y lo convierte en HTML.

Dos reglas gobiernan este módulo.

**Todo lo que viene de la base se escapa.** Un título de tarea lo escribe una
persona, y una persona puede escribir `<script>`. `_e()` no es una cortesía de
estilo: es la única barrera entre el texto de un cliente y el navegador de
otro.

**Una sección vacía dice por qué está vacía.** No es lo mismo "no hay bloqueos
abiertos", que es una buena noticia, que "esto todavía no se puede medir". Un
cero que en realidad significa "nadie lo cargó nunca" es un número que miente,
y un tablero que miente con números es peor que no tenerlo.
"""

from __future__ import annotations

from html import escape
from typing import Any

# Lo que el tablero todavía no puede mostrar, y la razón. Se imprime al pie
# para que la ausencia no se lea como un cero. Cuando alguna se implemente,
# sale de esta lista y entra como sección.
CARENCIAS = (
    ("Dependencias entre tareas",
     "el modelo las contempla y todavía nada las crea"),
    ("Subtareas",
     "el modelo las contempla y todavía nada las crea"),
    ("Prioridad",
     "el campo existe y todavía nada lo completa"),
    ("Cierre de bloqueos",
     "un bloqueo se abre y por ahora no se puede marcar resuelto"),
)

_ESTILO = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body { margin: 0; padding: 1rem; font: 16px/1.5 system-ui, sans-serif;
       max-width: 46rem; margin-inline: auto; }
h1 { font-size: 1.3rem; margin: 0 0 .25rem; }
h2 { font-size: 1.05rem; margin: 2rem 0 .5rem; }
.sub { opacity: .7; font-size: .85rem; margin: 0 0 1rem; }
.fila { display: flex; justify-content: space-between; gap: .75rem;
        padding: .55rem 0; border-bottom: 1px solid rgba(128,128,128,.25); }
.fila > span:first-child { min-width: 0; overflow-wrap: anywhere; }
.n { font-variant-numeric: tabular-nums; white-space: nowrap; opacity: .85; }
.vacio { opacity: .7; font-style: italic; padding: .55rem 0; }
.pie { margin-top: 2.5rem; padding-top: 1rem;
       border-top: 1px solid rgba(128,128,128,.25);
       font-size: .85rem; opacity: .75; }
.pie li { margin: .3rem 0; }
"""


def _e(valor: Any) -> str:
    """Escapa cualquier valor que venga de la base."""
    return escape("" if valor is None else str(valor), quote=True)


def _seccion(titulo: str, filas: list[str], vacio: str) -> str:
    cuerpo = "\n".join(filas) if filas else f'<p class="vacio">{_e(vacio)}</p>'
    return f"<h2>{_e(titulo)}</h2>\n{cuerpo}"


def _fila(izquierda_html: str, derecha_html: str) -> str:
    """Ambos lados se interpolan tal cual: llegan ya escapados.

    Algunas filas llevan marcado propio —un `<br>`, un `<small>`—, así que esta
    función no puede escapar por su cuenta. El nombre de los parámetros es el
    contrato: lo que entra acá ya pasó por `_e()`.
    """
    return f'<div class="fila"><span>{izquierda_html}</span>' \
           f'<span class="n">{derecha_html}</span></div>'


def pagina(datos: dict[str, list[dict]], *, espacio: str, persona: str) -> str:
    """Arma la página con lo que devolvió el puerto de lectura."""
    partes: list[str] = []

    partes.append(_seccion(
        "Avance de objetivos",
        [_fila(_e(o["titulo"]),
               f'{o["terminadas"]}/{o["tareas"]}' if o["tareas"]
               else "sin tareas")
         for o in datos["objetivos"]],
        "Todavía no hay objetivos cargados."))

    partes.append(_seccion(
        "Tareas por estado",
        [_fila(_e(t["estado"]), _e(t["tareas"])) for t in datos["estados"]],
        "Todavía no hay tareas cargadas."))

    partes.append(_seccion(
        "Carga por persona",
        [_fila(_e(c["nombre"]), _e(c["activas"])) for c in datos["carga"]],
        "No hay integrantes activos."))

    partes.append(_seccion(
        "Tareas vencidas",
        [_fila(f'{_e(v["titulo"])}<br><small>{_e(v["nombre"])}</small>',
               f'{v["dias_vencida"]} d')
         for v in datos["vencidas"]],
        "Ninguna tarea está vencida."))

    partes.append(_seccion(
        "Bloqueos abiertos",
        [_fila(f'{_e(b["titulo"])}<br><small>{_e(b["causa"])}</small>',
               f'{b["dias"]} d')
         for b in datos["bloqueos"]],
        "No hay bloqueos abiertos."))

    partes.append(_seccion(
        "Esperando aprobación",
        [_fila(f'{_e(a["titulo"])}<br><small>{_e(a["sujeto_tipo"])}'
               f' · {_e(a["responsable"])}</small>',
               _e(a["estado"]))
         for a in datos["aprobacion"]],
        "No hay trabajo esperando una decisión."))

    carencias = "\n".join(
        f"<li><strong>{_e(q)}</strong>: {_e(porque)}.</li>"
        for q, porque in CARENCIAS)

    return f"""<!doctype html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Tablero · {_e(espacio)}</title>
<style>{_ESTILO}</style>
</head><body>
<h1>{_e(espacio)}</h1>
<p class="sub">Estado al momento de abrir este enlace. Hola, {_e(persona)}.</p>
{chr(10).join(partes)}
<div class="pie">
<p>Esto todavía no se muestra, y su ausencia no significa cero:</p>
<ul>
{carencias}
</ul>
</div>
</body></html>"""


def enlace_vencido() -> str:
    """Lo que ve quien abre un enlace que ya no sirve.

    Sin detalle técnico y sin distinguir entre vencido, inválido o de alguien
    que ya no está en el equipo: los tres son lo mismo para quien mira, y
    diferenciarlos confirmaría cuáles enlaces existieron.
    """
    return f"""<!doctype html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Enlace vencido</title>
<style>{_ESTILO}</style>
</head><body>
<h1>Este enlace ya no sirve</h1>
<p>Los enlaces al tablero duran un rato corto, a propósito.</p>
<p>Pedime uno nuevo por Telegram y te lo mando.</p>
</body></html>"""
