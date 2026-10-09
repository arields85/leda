"""La página de una tarea (ADR 0019, decisión 7c).

Adaptador de presentación, como `tablero_vista.py`: no consulta la base. Recibe lo que devolvió
`pagina_de_tarea.leer` (la función de la base que ya decidió quién ve qué) y lo convierte en
HTML.

- **Todo lo que viene de la base se escapa** (`_e`): un título, un comentario o el nombre de un
  archivo los escribió una persona.
- **En palabras de todos los días** (decisión del usuario del 2026-10-07): "en revisión"
  (decisión 18 del 2026-10-08: primero se revisa y después se decide; corrige el "esperando
  aprobación" del ADR 0019, 7c), no el nombre del estado en la base; sin identificadores,
  huellas, nombres de herramientas ni errores técnicos (constitución §10). El único
  identificador que aparece es el del archivo de una evidencia, dentro de la dirección que lo
  pide: la base comprueba que sea de la tarea del enlace.
- **Sólo lectura:** sin botones, formularios ni nada que se ejecute (la página sale con una
  política de contenido que no lo deja, `entrada.py`).
- **No muestra la conversación:** sólo los hechos de la tarea.
"""

from __future__ import annotations

from datetime import date, datetime
from html import escape
from typing import Any
from zoneinfo import ZoneInfo

# Los estados de una tarea, como los dice una persona.
ESTADOS = {
    "propuesta": "propuesta",
    "pendiente_aprobacion": "esperando que la aprueben para empezar",
    "asignada": "asignada, sin empezar",
    "en_curso": "en curso",
    "bloqueada": "trabada",
    "en_revision": "en revisión",
    "terminada": "terminada",
    "cancelada": "cancelada",
}
_DIAS = ("lun", "mar", "mié", "jue", "vie", "sáb", "dom")
# Las imágenes que un navegador muestra; las demás (HEIC) se bajan.
IMAGENES_QUE_SE_VEN = ("image/jpeg", "image/png", "image/webp")

# Lo único que se dice de una pieza retirada: qué clase de cosa era.
QUE_ERA = {"texto": "Un texto", "enlace": "Un enlace", "imagen": "Una foto",
           "archivo": "Un archivo"}

_ESTILO = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body { margin: 0; padding: 1rem; font: 16px/1.5 system-ui, sans-serif;
       max-width: 46rem; margin-inline: auto; }
h1 { font-size: 1.3rem; margin: 0 0 .25rem; overflow-wrap: anywhere; }
h2 { font-size: 1.05rem; margin: 2rem 0 .5rem; }
.sub { opacity: .7; font-size: .85rem; margin: 0 0 1rem; }
dl { display: grid; grid-template-columns: max-content 1fr; gap: .3rem .9rem; margin: 0; }
dt { opacity: .7; }
dd { margin: 0; overflow-wrap: anywhere; }
ul { padding-left: 1.2rem; }
li { margin: .45rem 0; overflow-wrap: anywhere; }
.pieza { padding: .6rem 0; border-bottom: 1px solid rgba(128,128,128,.25); }
.pieza img { display: block; max-width: 100%; height: auto; margin: .4rem 0; }
.quien { opacity: .7; font-size: .85rem; }
.retirada { opacity: .6; }
.vacio { opacity: .7; font-style: italic; }
"""


def _e(valor: Any) -> str:
    """Escapa cualquier valor que venga de la base."""
    return escape("" if valor is None else str(valor), quote=True)


def _cuando(valor: str | None, zona: ZoneInfo) -> str:
    """Una fecha con hora, corta y en la hora del equipo: "jue 22/10 15:26"."""
    if not valor:
        return ""
    momento = datetime.fromisoformat(valor).astimezone(zona)
    return f"{_DIAS[momento.weekday()]} {momento:%d/%m %H:%M}"


def _dia(valor: str | None, zona: ZoneInfo) -> str:
    """Un día: "vie 23/10". Una fecha con hora se toma en la hora del equipo."""
    if not valor:
        return ""
    if len(valor) == 10:
        dia = date.fromisoformat(valor)
    else:
        dia = datetime.fromisoformat(valor).astimezone(zona).date()
    return f"{_DIAS[dia.weekday()]} {dia:%d/%m}"


def _estado(valor: str | None) -> str:
    return ESTADOS.get(valor or "", "sin estado")


def _hecho(h: dict[str, Any], zona: ZoneInfo) -> str:
    """Un renglón de la historia, ya escapado."""
    quien = _e(h.get("quien")) or "Leda"
    que = h.get("que")
    if que == "estado":
        texto = f"Quedó {_e(_estado(h.get('a')))}"
        if h.get("quien"):
            texto += f", por {quien}"
    elif que == "aprobacion":
        texto = f"{quien} la aprobó"
        if h.get("comentario"):
            texto += f": «{_e(h['comentario'])}»"
    elif que == "pedido_de_cambios":
        texto = f"{quien} pidió cambios"
        if h.get("comentario"):
            texto += f": «{_e(h['comentario'])}»"
    elif que == "bloqueo":
        texto = f"Se trabó: {_e(h.get('causa'))}"
        if h.get("quien"):
            texto += f" (lo dijo {quien})"
        if h.get("resuelto_en"):
            texto += f". Se destrabó el {_e(_cuando(h['resuelto_en'], zona))}"
    elif que == "prevision":
        verbo = "corrigió el día en que la termina" if h.get("es_correccion") \
            else "dijo que la termina"
        texto = f"{quien} {verbo}: {_e(_dia(h.get('fecha'), zona))}"
    elif que == "quien_destraba":
        if h.get("no_sabe"):
            texto = f"{quien} dijo que no sabe quién la destraba"
        elif h.get("nadie_mas"):
            texto = f"{quien} dijo que no hay otra persona que la destrabe"
        else:
            texto = f"{quien} dijo que la destraba {_e(h.get('destraba'))}"
    elif que == "dicho_del_bloqueo":
        texto = _lo_que_dijo_del_bloqueo(h, quien, zona)
    elif que == "asentado":
        if h.get("por") == "sigue_trabada":
            texto = "Quedó asentado que sigue trabada"
            if h.get("dias_habiles") is not None:
                texto += f": {_e(h['dias_habiles'])} días hábiles"
        else:
            texto = "Quedó asentado que nadie toma el bloqueo"
    else:
        return ""
    return (f'<li>{texto} <span class="quien">· {_e(_cuando(h.get("cuando"), zona))}'
            f"</span></li>")


def _lo_que_dijo_del_bloqueo(h: dict[str, Any], quien: str, zona: ZoneInfo) -> str:
    """Lo que dijo quien destraba (o la persona trabada sobre lo que arreglaron), ya escapado:
    para cuándo, que ya está o que no le corresponde, y sus palabras (C-5c, decisión 49: lo
    asentado queda en la historia de la tarea)."""
    if h.get("no_le_corresponde"):
        texto = f"{quien} dijo que no le corresponde"
    elif h.get("ya_esta"):
        texto = f"{quien} dijo que ya está"
    elif h.get("para_cuando"):
        texto = f"{quien} dijo que la destraba el {_e(_dia(h['para_cuando'], zona))}"
    else:
        texto = f"{quien} dijo"
    if h.get("lo_que_dice"):
        texto += f": «{_e(h['lo_que_dice'])}»"
    return texto


def _pieza(p: dict[str, Any], token: str, palabras: dict[str, str], zona: ZoneInfo) -> str:
    """Una pieza de la evidencia, ya escapada: qué es, quién la mandó y cuándo, y qué cubre. Una
    imagen se ve; otro archivo se baja; una pieza retirada sólo figura como retirada (ADR 0019,
    decisión 3): ni su texto, ni su enlace, ni el nombre o el contenido de su archivo. Se mira
    primero, antes que la clase, para que ninguna clase muestre lo retirado."""
    clase, retirada = p.get("clase"), bool(p.get("retirada"))
    archivo = f'{_e(token)}/evidencia/{_e(p.get("id"))}'
    nombre = _e(p.get("nombre"))
    if retirada:
        contenido = f"{QUE_ERA.get(clase, 'Una pieza')} que se retiró"
    elif clase == "texto" and p.get("ejemplo_aceptado"):
        # Lo propuso Leda y la persona lo aceptó tal cual: nunca "lo que escribió" (D8).
        contenido = f"Aceptó esta descripción: «{_e(p.get('texto'))}»"
    elif clase == "texto":
        contenido = f"Lo que escribió: «{_e(p.get('texto'))}»"
    elif clase == "enlace":
        enlace = p.get("enlace") or ""
        contenido = f"Un enlace: {_e(enlace)}"
        if enlace.startswith(("https://", "http://")):
            contenido = (f'Un enlace: <a href="{_e(enlace)}" rel="noopener noreferrer nofollow">'
                         f"{_e(enlace)}</a>")
    elif clase == "imagen" and p.get("tipo_de_archivo") in IMAGENES_QUE_SE_VEN:
        contenido = (f'Una foto: {nombre}<img src="{archivo}" alt="{nombre or "foto"}" '
                     f'loading="lazy">')
    else:
        que = "Una foto" if clase == "imagen" else "Un archivo"
        contenido = f'{que}: <a href="{archivo}">{nombre or "bajar"}</a>'
    cubre = [palabras.get(t) or t.replace("_", " ") for t in p.get("cubre") or []]
    partes = [f'<div class="pieza{" retirada" if retirada else ""}">', f"<div>{contenido}</div>",
              f'<div class="quien">{_e(p.get("quien")) or "Alguien del equipo"} · '
              f"{_e(_cuando(p.get('cuando'), zona))}</div>"]
    if cubre:
        partes.append(f'<div class="quien">Cubre: {_e(", ".join(cubre))}</div>')
    if retirada:
        partes.append(f'<div class="quien">Retirada el {_e(_cuando(p.get("retirada_el"), zona))}'
                      "</div>")
    partes.append("</div>")
    return "".join(partes)


def pagina(datos: dict[str, Any], *, token: str) -> str:
    """Arma la página con lo que devolvió la base para este enlace."""
    zona = ZoneInfo(datos.get("zona_horaria") or "UTC")
    t = datos.get("tarea") or {}
    pide = datos.get("pide") or []
    palabras = {p["tipo"]: p.get("en_palabras") for p in pide if p.get("en_palabras")}

    filas = [("Estado", _estado(t.get("estado"))),
             ("Objetivo", t.get("objetivo")),
             ("Área", t.get("area")),
             ("Responsable", t.get("responsable")),
             ("Quién la aprueba", t.get("quien_aprueba") or "nadie"),
             ("Vence", _dia(t.get("fecha_objetivo"), zona) or "sin fecha")]
    prevision = t.get("prevision")
    if prevision:
        filas.append(("Dio para terminarla", _dia(prevision.get("fecha"), zona)))
    filas.append(("Qué tiene que cumplir", t.get("criterio_aceptacion") or "sin escribir"))
    ficha = "\n".join(f"<dt>{_e(a)}</dt><dd>{_e(b)}</dd>" for a, b in filas if b)

    if pide:
        lo_que_pide = "<ul>" + "".join(
            f"<li>{_e(p.get('en_palabras') or p['tipo'].replace('_', ' '))}: "
            f"{'está' if p.get('cubierto') else 'falta'}</li>" for p in pide) + "</ul>"
    else:
        lo_que_pide = '<p class="vacio">Esta tarea no pide evidencia.</p>'

    historia = [r for r in (_hecho(h, zona) for h in datos.get("historia") or []) if r]
    evidencia = [_pieza(p, token, palabras, zona) for p in datos.get("evidencia") or []]

    return f"""<!doctype html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="referrer" content="no-referrer">
<title>Tarea · {_e(datos.get('espacio'))}</title>
<style>{_ESTILO}</style>
</head><body>
<h1>{_e(t.get('titulo'))}</h1>
<p class="sub">{_e(datos.get('espacio'))} · Sólo para ver. Hola, {_e(datos.get('persona'))}.</p>
<dl>
{ficha}
</dl>
<h2>Lo que pide para entregarla</h2>
{lo_que_pide}
<h2>Lo que se entregó</h2>
{"".join(evidencia) or '<p class="vacio">Todavía no se entregó nada.</p>'}
<h2>Lo que fue pasando</h2>
{"<ul>" + "".join(historia) + "</ul>" if historia else '<p class="vacio">Todavía nada.</p>'}
</body></html>"""


def no_se_puede_abrir() -> str:
    """Lo que ve quien abre un enlace que no sirve: inexistente, revocado, de alguien que ya no
    puede ver la tarea, o el archivo de otra tarea. Los cuatro son lo mismo para quien mira, y
    distinguirlos confirmaría cuáles enlaces existieron."""
    return f"""<!doctype html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="referrer" content="no-referrer">
<title>Enlace</title>
<style>{_ESTILO}</style>
</head><body>
<h1>Este enlace no se puede abrir</h1>
<p>Si te hace falta ver esta tarea, escribile a Leda por Telegram.</p>
</body></html>"""
