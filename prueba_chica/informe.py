"""El informe de una ronda de conversaciones de prueba (E2-7).

`odd/tasks/prueba-chica-del-motor.md`, secciones 6 y 10.3. Dos archivos Markdown por ronda en
`prueba_chica/resultados/`, versionados porque son la evidencia (las grabaciones crudas, no):

- **el resumen** (`<ronda>.md`): la tabla de conversaciones por corridas con lo que se comprobó
  solo (garantías, comprensión provisional y lo del código), las fallas con su diferencia, la
  columna de la lectura del usuario (vacía: su lectura es la que vale, 10.3), las latencias por
  turno (mediana y peor caso, sin umbral), el costo y, en la 13 y la 14, Jev contra la IA;
- **las transcripciones** (`<ronda>-transcripciones.md`): cada corrida como se lee, quién dijo
  qué, lo que Leda contestó o mandó, con sus botones, las jugadas y los hechos, y lo que cada
  paso "dice" y "no dice" para marcar al leer.

La comprensión automática es provisional: compara las jugadas y los efectos; si Leda preguntó
cuando no entendió lo dice el texto, y eso lo lee una persona.
"""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from .corredor import Corrida

RESULTADOS = Path(__file__).resolve().parent / "resultados"


def _ok(valor: bool) -> str:
    return "ok" if valor else "FALLA"


def _celda(c: Corrida) -> str:
    if c.error:
        return "ERROR"
    return f"G {_ok(c.garantias)} · C {_ok(c.comprension)} · M {_ok(c.motor)}"


def _json(valor: Any) -> str:
    return json.dumps(valor, ensure_ascii=False, default=str)


def resumen(corridas: list[Corrida], *, ronda: str, cabecera: dict[str, Any],
            transcripciones: str, cortes: list[dict[str, Any]] | None = None) -> str:
    por_conv: dict[str, list[Corrida]] = defaultdict(list)
    for c in sorted(corridas, key=lambda c: (c.numero, c.vez)):
        por_conv[c.numero].append(c)
    veces = max((len(v) for v in por_conv.values()), default=0)
    lineas = [f"# Ronda {ronda}", ""]
    lineas += [f"- **{k}:** {v}" for k, v in cabecera.items()]
    lineas += [f"- **Transcripciones:** [{transcripciones}]({transcripciones})", ""]
    if cortes:
        # Una ronda cortada lo dice antes que nada (revisión de la E2-7): lo que no corrió no
        # está en la tabla, y la ronda no vale como completa.
        lineas += ["## Ronda cortada", "",
                   f"{len(cortes)} corrida(s) no corrieron o no terminaron; lo que la IA ya "
                   "había gastado quedó en la libreta del gasto.", ""]
        lineas += [f"- **{c['conversacion']}, vez {c['vez']}:** "
                   + ("llegó al techo de gasto. " if c["techo"] else "se cortó. ")
                   + f"`{c['motivo']}`" for c in cortes]
        lineas.append("")
    lineas += ["## Resultado por conversación", "",
               "G: garantías (5b, se comprueban solas). C: comprensión automática, "
               "**provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). "
               "M: lo que hace el código con las jugadas esperadas.", ""]
    encabezado = ["Conversación", *[f"Vez {i}" for i in range(1, veces + 1)],
                  "Garantías", "Comprensión (provisional)", "Lectura del usuario"]
    lineas += ["| " + " | ".join(encabezado) + " |",
               "|" + "---|" * len(encabezado)]
    for numero, cs in por_conv.items():
        celdas = [_celda(c) for c in cs] + [""] * (veces - len(cs))
        g = sum(c.garantias for c in cs)
        comp = sum(c.comprension for c in cs)
        lineas.append(f"| {numero} {cs[0].titulo} ({cs[0].mide}) | " + " | ".join(celdas)
                      + f" | {g}/{len(cs)} | {comp}/{len(cs)} |  |")
    lineas += ["", "## Fallas", ""]
    alguna = False
    for numero, cs in por_conv.items():
        for c in cs:
            if c.error:
                alguna = True
                lineas += [f"- **{numero}, vez {c.vez}:** la corrida se cayó:", "",
                           "```", c.error, "```", ""]
            for paso, f in c.fallas():
                alguna = True
                lineas.append(f"- **{numero}, vez {c.vez}, paso {paso}** [{f.clase}] {f.que}: "
                              f"esperado `{_json(f.esperado)}`; real `{_json(f.real)}`")
    if not alguna:
        lineas.append("Ninguna.")
    lineas += ["", "## Latencia por turno", "",
               "Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta "
               "encolada (las dos llamadas a la IA). Sin umbral (sección 6).", "",
               "| Conversación | Turnos | Mediana (ms) | Peor (ms) |", "|---|---|---|---|"]
    todas: list[int] = []
    for numero, cs in por_conv.items():
        lat = [x for c in cs for x in c.latencias()]
        todas += lat
        if lat:
            lineas.append(f"| {numero} | {len(lat)} | {statistics.median(lat):.0f} | "
                          f"{max(lat)} |")
    if todas:
        lineas.append(f"| **Todas** | {len(todas)} | {statistics.median(todas):.0f} | "
                      f"{max(todas)} |")
    lineas += ["", "## Costo", ""]
    costos = [c.costo for c in corridas if c.costo]
    if costos:
        usd = sum(x["usd"] + x.get("jev_usd", 0.0) for x in costos)
        estimadas = sum(x["llamadas_estimadas"] for x in costos)
        lineas += [f"- Llamadas a la IA: {sum(x['llamadas'] for x in costos)} "
                   f"({estimadas} con el costo estimado); tokens de entrada "
                   f"{sum(x['tokens_entrada'] for x in costos)}, de salida "
                   f"{sum(x['tokens_salida'] for x in costos)}.",
                   f"- Jev: {sum(x.get('jev_llamadas', 0) for x in costos)} llamadas, USD "
                   f"{sum(x.get('jev_usd', 0.0) for x in costos):.4f} (estimado).",
                   f"- **Total de la ronda: USD {usd:.4f}.**"]
    else:
        lineas.append("Sin gasto: la IA no es un proveedor real.")
    jev = [(c, p) for c in corridas for p in c.pasos if p.jev]
    if jev:
        lineas += ["", "## Jev contra la IA (decisión 7)", "",
                   "Jev corre en paralelo y no decide nada. Correcta: lo que el paso espera "
                   "(`preguntar` o la tarea).", "",
                   "| Conv. | Vez | Paso | Referencia | Correcta | IA | Jev | Probabilidades "
                   "| IA acierta | Jev acierta |", "|---|---|---|---|---|---|---|---|---|---|"]
        for c, p in sorted(jev, key=lambda x: (x[0].numero, x[1].paso, x[0].vez)):
            j = p.jev
            correcta = j.get("correcta")
            ia_acierta = p.eleccion_de_la_ia == correcta
            jev_dijo = j.get("error") or f"{j.get('tipo')} {j.get('eligio') or ''}".strip()
            lineas.append(
                f"| {c.numero} | {c.vez} | {p.paso} | {j['referencia']} | {correcta} | "
                f"{p.eleccion_de_la_ia} | {jev_dijo} | {_json(j.get('probabilidades'))} | "
                f"{_ok(ia_acierta)} | {_ok(bool(j.get('acierta')))} |")
    return "\n".join(lineas) + "\n"


def transcripciones(corridas: list[Corrida], *, ronda: str) -> str:
    lineas = [f"# Transcripciones de la ronda {ronda}", "",
              "Para leer contra lo que cada paso dice y no dice (decisión 10.3). Cada casilla "
              "la marca quien lee.", ""]
    for c in sorted(corridas, key=lambda c: (c.numero, c.vez)):
        lineas += [f"## {c.numero} · {c.titulo} · vez {c.vez}", "",
                   f"Fuente: `{c.fuente}`. IA: `{c.ia}`. Automático: {_celda(c)}.", ""]
        if c.error:
            lineas += ["```", c.error, "```", ""]
        for p in c.pasos:
            etiqueta = "Preludio" if p.preludio else f"Paso {p.paso}"
            if p.texto is not None:
                lineas.append(f"**{etiqueta}.** {p.quien} ({p.cuando}): «{p.texto}»")
                if not p.preludio:
                    lineas.append(f"- jugadas: `{_json(p.jugadas)}`")
                    lineas.append(f"- hechos: `{_json(p.hechos)}`")
                    if p.pregunta:
                        lineas.append(f"- pregunta: `{_json(p.pregunta)}`")
                    if p.latencia_ms is not None:
                        lineas.append(f"- latencia: {p.latencia_ms} ms")
                    if p.jev:
                        lineas.append(f"- Jev: `{_json(p.jev)}`")
            else:
                lineas.append(f"**{etiqueta}.** {p.quien} ({p.cuando})")
            for s in p.salidas:
                quien = "Leda" + (f", por su cuenta ({s.tipo} {', '.join(s.tareas)}, {s.el})"
                                  if not s.es_respuesta else "")
                botones = f" [botones: {', '.join(s.botones)}]" if s.botones else ""
                lineas.append(f"- {quien} → {s.a}: «{s.texto}»{botones}")
                if not s.es_respuesta and s.hechos is not None and not p.preludio:
                    lineas.append(f"  - hechos: `{_json(s.hechos)}`")
            if not p.salidas and not p.preludio:
                lineas.append("- (Leda no manda nada)")
            for d in p.dice:
                lineas.append(f"- [ ] dice: {d}")
            for d in p.no_dice:
                lineas.append(f"- [ ] no dice: {d}")
            for f in p.fallas:
                lineas.append(f"- **falla** {f}")
            lineas.append("")
    return "\n".join(lineas) + "\n"


def escribir(corridas: list[Corrida], *, ronda: str, cabecera: dict[str, Any],
             carpeta: Path | None = None,
             cortes: list[dict[str, Any]] | None = None) -> tuple[Path, Path]:
    carpeta = carpeta or RESULTADOS
    carpeta.mkdir(parents=True, exist_ok=True)
    nombre_t = f"{ronda}-transcripciones.md"
    ruta_r, ruta_t = carpeta / f"{ronda}.md", carpeta / nombre_t
    ruta_t.write_text(transcripciones(corridas, ronda=ronda), "utf-8", newline="\n")
    ruta_r.write_text(resumen(corridas, ronda=ronda, cabecera=cabecera,
                              transcripciones=nombre_t, cortes=cortes), "utf-8",
                      newline="\n")
    return ruta_r, ruta_t
