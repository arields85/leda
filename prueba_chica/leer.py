"""El lector del registro de turnos del motor (E2-6). Sólo lee.

    python -m prueba_chica.leer corework [--persona X] [--desde HH:MM | "AAAA-MM-DD HH:MM"]
                                         [--completo]

`odd/tasks/prueba-chica-del-motor.md`, secciones 7 y 9: para leer una prueba real sin
capturas. `tools/leer_conversacion.py` muestra el outbox y los toques como su código; éste lee
el registro de turnos del motor (`conversation_turn`) y su estado:

- **Turnos**, en orden: hora local del espacio, número del turno de la persona, sentido (`←` lo
  que escribió o tocó, `→` lo que salió de Leda, con el estado del mensaje), el texto, la
  opción tocada, las jugadas que eligió la IA, los hechos del resultado, la IA, la latencia y el
  error, si lo hubo.
- **Preguntas abiertas y para después**, con sus opciones si es una duda.
- **Esperas de respuesta** (`pending_reply`) sin contestar, con sus recordatorios y si escaló.
- **Avisos guardados**, con su estado, intentos y el motivo si se omitieron.

`--persona` filtra por palabras enteras del nombre (sus turnos, sus preguntas y esperas, los
avisos para ella); `--desde` deja los turnos y los avisos desde esa hora del reloj de Leda (sólo
la hora: la de hoy de Leda). Corre en una transacción de sólo lectura del espacio (`row level
security`) y no escribe nada. Sin `--completo`, cada texto se corta en 300 caracteres.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, time
from typing import Any
from zoneinfo import ZoneInfo

import psycopg

from leda.db import espacio

from .fichas import integrantes_que_coinciden

SECCIONES = ("Turnos", "Preguntas abiertas y para después", "Esperas de respuesta",
             "Avisos guardados")
CORTE = 300


def leer(conn: psycopg.Connection, workspace_id: str, *, persona: str | None = None,
         desde: datetime | None = None, completo: bool = False) -> str:
    """El registro de turnos y el estado, como texto. Nunca escribe."""
    try:
        with espacio(conn, workspace_id) as cur:
            cur.execute("set transaction read only")
            cur.execute("select zona_horaria from workspace where id = %s", (workspace_id,))
            zona = ZoneInfo(cur.fetchone()["zona_horaria"])
            quien = _persona(cur, persona) if persona else None
            lineas = [SECCIONES[0], *_turnos(cur, quien, desde, zona, completo),
                      "", SECCIONES[1], *_preguntas(cur, quien, zona),
                      "", SECCIONES[2], *_esperas(cur, quien, zona),
                      "", SECCIONES[3], *_avisos(cur, quien, desde, zona)]
    finally:
        conn.rollback()
    return "\n".join(lineas)


def desde_texto(texto: str, ahora: datetime, zona: ZoneInfo) -> datetime:
    """`HH:MM` es la hora de hoy (del reloj de Leda); `AAAA-MM-DD HH:MM`, una fecha y hora."""
    try:
        if len(texto) <= 5:
            hoy: date = ahora.astimezone(zona).date()
            return datetime.combine(hoy, time.fromisoformat(texto), tzinfo=zona)
        return datetime.fromisoformat(texto).replace(tzinfo=zona)
    except ValueError:
        raise ValueError(f"'{texto}' no es HH:MM ni AAAA-MM-DD HH:MM.") from None


# --- Lo que se lee ------------------------------------------------------------------------------

def _persona(cur, palabras: str) -> str:
    coinciden = integrantes_que_coinciden(cur, palabras)
    if len(coinciden) != 1:
        nombres = ", ".join(p["nombre"] for p in coinciden)
        raise ValueError(f"'{palabras}' no es nadie del equipo." if not coinciden
                         else f"'{palabras}' es más de una persona: {nombres}.")
    return str(coinciden[0]["membership_id"])


def _turnos(cur, quien: str | None, desde: datetime | None, zona: ZoneInfo,
            completo: bool) -> list[str]:
    cur.execute(
        """select t.numero, t.sentido, t.at, t.jugadas, t.resultado, t.ia, t.latencia_ms,
                  t.error, p.nombre, coalesce(i.texto, o.cuerpo) texto, o.estado salida,
                  op.etiqueta toco
             from conversation_turn t
             join integrante p on p.membership_id = t.membership_id
             left join inbound_message i on i.id = t.inbound_message_id
             left join message_outbox o on o.id = t.outbox_id
             left join conversation_option op on op.id = t.option_id
            where (%(quien)s::uuid is null or t.membership_id = %(quien)s::uuid)
              and (%(desde)s::timestamptz is null or t.at >= %(desde)s)
            order by t.at, t.membership_id, t.numero""", {"quien": quien, "desde": desde})
    lineas = []
    for t in cur.fetchall():
        cabeza = f"{_hora(t['at'], zona)}  #{t['numero']} "
        if t["sentido"] == "salida":
            lineas.append(f"{cabeza}Leda → {t['nombre']} [{t['salida'] or '?'}]: "
                          f"{_cita(t['texto'], completo)}")
        elif t["toco"]:
            lineas.append(f"{cabeza}{t['nombre']} tocó «{t['toco']}»")
        else:
            lineas.append(f"{cabeza}{t['nombre']} ← {_cita(t['texto'], completo)}")
        if t["jugadas"] is not None:
            jugadas = "; ".join(f"{j['nombre']} {_json(j.get('datos', {}))}"
                                for j in t["jugadas"]) or "ninguna"
            lineas.append(f"      jugadas: {jugadas}")
        if t["resultado"] is not None:
            hechos = t["resultado"].get("hechos", t["resultado"])
            lineas.append(f"      hechos: {_corto(_json(hechos), completo)}")
        if t["sentido"] == "entrada" or t["ia"]:
            latencia = f" · {t['latencia_ms']} ms" if t["latencia_ms"] is not None else ""
            lineas.append(f"      ia: {t['ia'] or '-'}{latencia}")
        if t["error"]:
            lineas.append(f"      error: {t['error']}")
    return lineas or ["  (ninguno)"]


def _preguntas(cur, quien: str | None, zona: ZoneInfo) -> list[str]:
    cur.execute(
        """select q.tipo, q.abierta_en, q.para_despues_en, q.se_puede_dejar, p.nombre,
                  t.titulo, s.pregunta_abierta_id = q.id es_la_abierta,
                  (select string_agg(o.etiqueta, ' | ' order by o.orden)
                     from conversation_option o where o.question_id = q.id) opciones
             from conversation_question q
             join integrante p on p.membership_id = q.membership_id
             left join task t on t.id = q.task_id
             left join conversation_state s on s.membership_id = q.membership_id
            where q.cerrada_en is null
              and (%(quien)s::uuid is null or q.membership_id = %(quien)s::uuid)
            order by p.nombre, q.abierta_en""", {"quien": quien})
    lineas = []
    for q in cur.fetchall():
        linea = f"  {q['nombre']} · {q['tipo']} · {q['titulo'] or '(sin tarea)'} · " + (
            "abierta" if q["es_la_abierta"] else
            f"para después desde {_hora(q['para_despues_en'], zona)}"
            if q["para_despues_en"] else "sin abrir")
        linea += f" desde {_hora(q['abierta_en'], zona)}"
        if not q["se_puede_dejar"]:
            linea += " · no se puede dejar"
        if q["opciones"]:
            linea += f" · opciones: {q['opciones']}"
        lineas.append(linea)
    return lineas or ["  (ninguna)"]


def _esperas(cur, quien: str | None, zona: ZoneInfo) -> list[str]:
    cur.execute(
        """select p.nombre, t.titulo, e.preguntado_en, e.vence_en, e.recordatorios,
                  e.escalado_en
             from pending_reply e
             join integrante p on p.membership_id = e.membership_id
             left join task t on t.id = e.task_id
            where e.satisfecho_en is null
              and (%(quien)s::uuid is null or e.membership_id = %(quien)s::uuid)
            order by p.nombre, e.preguntado_en""", {"quien": quien})
    lineas = []
    for e in cur.fetchall():
        linea = (f"  {e['nombre']} · {e['titulo'] or '(sin tarea)'} · preguntado "
                 f"{_hora(e['preguntado_en'], zona)} · vence {_hora(e['vence_en'], zona)} · "
                 f"recordatorios {e['recordatorios']}")
        if e["escalado_en"]:
            linea += f" · escalada {_hora(e['escalado_en'], zona)}"
        lineas.append(linea)
    return lineas or ["  (ninguna)"]


def _avisos(cur, quien: str | None, desde: datetime | None, zona: ZoneInfo) -> list[str]:
    cur.execute(
        """select a.tipo, a.estado, a.programado_para, a.intentos, a.proximo_intento_en,
                  a.motivo_omision, p.nombre, t.titulo
             from scheduled_notice a
             join integrante p on p.membership_id = a.destinatario_membership_id
             left join task t on t.id = a.task_id
            where (%(quien)s::uuid is null or a.destinatario_membership_id = %(quien)s::uuid)
              and (%(desde)s::timestamptz is null or a.creado_en >= %(desde)s
                   or a.estado = 'guardado')
            order by a.programado_para, a.creado_en""", {"quien": quien, "desde": desde})
    lineas = []
    for a in cur.fetchall():
        linea = (f"  {_hora(a['programado_para'], zona)}  {a['tipo']} → {a['nombre']} · "
                 f"{a['titulo'] or '(sin tarea)'} · {a['estado']} · intentos {a['intentos']}")
        if a["proximo_intento_en"]:
            linea += f" · próximo intento {_hora(a['proximo_intento_en'], zona)}"
        if a["motivo_omision"]:
            linea += f" · motivo: {a['motivo_omision']}"
        lineas.append(linea)
    return lineas or ["  (ninguno)"]


# --- Formato -------------------------------------------------------------------------------------

def _hora(momento: datetime | None, zona: ZoneInfo) -> str:
    return momento.astimezone(zona).strftime("%d/%m %H:%M:%S") if momento else "-"


def _json(valor: Any) -> str:
    return json.dumps(valor, ensure_ascii=False, default=str)


def _corto(texto: str, completo: bool) -> str:
    return texto if completo or len(texto) <= CORTE else texto[:CORTE] + "…"


def _cita(texto: str | None, completo: bool) -> str:
    return '"' + _corto((texto or "").replace("\n", " / "), completo) + '"'


def main(argv: list[str] | None = None) -> int:
    from leda.db import admin, conectar

    from .reloj import RelojDeLeda

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")    # la consola de Windows no es UTF-8
    p = argparse.ArgumentParser(prog="python -m prueba_chica.leer")
    p.add_argument("slug")
    p.add_argument("--persona", help="palabras enteras del nombre")
    p.add_argument("--desde", help='HH:MM (de hoy, en el reloj de Leda) o "AAAA-MM-DD HH:MM"')
    p.add_argument("--completo", action="store_true", help="los textos sin cortar")
    a = p.parse_args(argv)

    conn = conectar()
    with admin(conn) as cur:
        cur.execute("select id, zona_horaria from workspace where slug = %s", (a.slug,))
        fila = cur.fetchone()
    conn.rollback()
    if fila is None:
        print(f"No hay un espacio '{a.slug}'.")
        return 1
    ws = str(fila["id"])
    try:
        desde = None
        if a.desde:
            reloj = RelojDeLeda()
            reloj.refrescar(conn, ws)
            conn.rollback()
            desde = desde_texto(a.desde, reloj.ahora(), ZoneInfo(fila["zona_horaria"]))
        print(leer(conn, ws, persona=a.persona, desde=desde, completo=a.completo))
    except ValueError as e:
        print(e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
