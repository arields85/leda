"""El aviso previo, disparado a mano para el primer contacto real (E2-3b).

    python -m prueba_chica.avisar corework <persona> <palabras del título> [--de-nuevo]

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Avisos guardados"); ADR 0018, decisiones 8
y 9b. El aviso se guarda como hechos en `scheduled_notice` (la tarea, cuándo vence, cuántos días
hábiles faltan y que no pide respuesta), la IA lo redacta justo antes de encolarlo y recién
entonces entra al outbox; después se despacha. Lo que Leda inicia sale sólo dentro del horario
del espacio: fuera de él, el despachador lo pospone a la próxima jornada.

Para la prueba se dispara con este comando; el ciclo que lo dispara solo a su hora, la escalera
y los reintentos a los 1, 2, 4 y 8 minutos son de la E2-5 y la E2-6. Si la IA no redacta (un
reintento enseguida), el aviso queda guardado sin enviar, con su intento contado, y se vuelve
a intentar corriendo el comando otra vez: nunca sale un texto armado a mano.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any

import psycopg

from leda.calendario import Calendario
from leda.db import espacio
from leda.salida import enqueue_outbox

from .fichas import ESTADOS_ABIERTOS, integrantes_que_coinciden, palabras
from .ia import IA
from .tiempo import Reloj
from .turno import (IANoRespondio, leer_ultimos_turnos, no_vacio, pedir_a_la_ia,
                    registrar_salida)

TIPO = "aviso_previo"


@dataclass
class ResultadoAviso:
    estado: str                 # encolado | ya_enviado | sin_redactar
    aviso_id: str
    texto: str | None
    hechos: dict[str, Any]


def resolver(cur, persona: str, tarea: str) -> tuple[str, str, str]:
    """(membership, nombre, tarea) por palabras enteras del nombre y del título, entre las
    tareas abiertas de esa persona. Nada o más de uno es un error que dice qué hay."""
    personas = integrantes_que_coinciden(cur, persona)
    if len(personas) != 1:
        nombres = ", ".join(p["nombre"] for p in personas)
        raise ValueError(f"'{persona}' no es nadie del equipo." if not personas
                         else f"'{persona}' es más de una persona: {nombres}.")
    quien = personas[0]
    cur.execute("""select id, titulo from task
                    where responsable_membership_id = %s and estado::text = any(%s)
                    order by titulo""", (quien["membership_id"], sorted(ESTADOS_ABIERTOS)))
    buscadas = set(palabras(tarea))
    tareas = [t for t in cur.fetchall() if buscadas <= set(palabras(t["titulo"]))]
    if len(tareas) != 1:
        titulos = "; ".join(t["titulo"] for t in tareas)
        raise ValueError(f"{quien['nombre']} no tiene una tarea abierta con '{tarea}'."
                         if not tareas else f"Hay más de una: {titulos}.")
    return str(quien["membership_id"]), quien["nombre"], str(tareas[0]["id"])


def avisar_vencimiento(conn: psycopg.Connection, workspace_id: str, membership_id: str,
                       task_id: str, ia: IA, reloj: Reloj, *,
                       de_nuevo: bool = False) -> ResultadoAviso:
    """Guarda el aviso previo de la tarea como hechos, lo redacta y lo encola. Sin
    `de_nuevo`, un aviso ya enviado de la misma tarea y vencimiento no se repite."""
    ahora = reloj.ahora()
    with espacio(conn, workspace_id) as cur:
        cur.execute("""select t.titulo, t.estado::text estado, t.fecha_objetivo,
                              t.responsable_membership_id, i.nombre, i.telegram_user_id
                         from task t
                         join integrante i on i.membership_id = %s
                        where t.id = %s""", (membership_id, task_id))
        fila = cur.fetchone()
        if fila is None or str(fila["responsable_membership_id"]) != membership_id:
            raise ValueError("La tarea no es de esa persona.")
        if fila["estado"] not in ESTADOS_ABIERTOS:
            raise ValueError(f"La tarea no está abierta (está {fila['estado']}).")
        if fila["fecha_objetivo"] is None:
            raise ValueError("La tarea no tiene fecha comprometida.")
        if fila["telegram_user_id"] is None:
            raise ValueError(f"{fila['nombre']} todavía no activó su Telegram.")

        cal = Calendario.desde_base(cur, workspace_id)
        vence = fila["fecha_objetivo"].astimezone(cal.zona).date()
        hechos = {"aviso": "vencimiento_proximo", "tarea": fila["titulo"],
                  "vence": vence.isoformat(),
                  "dias_habiles_hasta_el_vencimiento": cal.habiles_entre(
                      ahora, fila["fecha_objetivo"]),
                  "necesita_respuesta": False}
        clave = f"motor:{TIPO}:{task_id}:{vence.isoformat()}"
        if de_nuevo:
            clave += f":{ahora.isoformat()}"
        cur.execute(
            """insert into scheduled_notice (workspace_id, tipo, task_id,
                                             destinatario_membership_id, hechos,
                                             programado_para, dedupe_key, creado_en)
               values (%s, %s, %s, %s, %s, %s, %s, %s)
               on conflict (workspace_id, dedupe_key) do nothing""",
            (workspace_id, TIPO, task_id, membership_id, json.dumps(hechos, ensure_ascii=False),
             ahora, clave, ahora))
        cur.execute("""select id, estado, hechos from scheduled_notice
                        where workspace_id = %s and dedupe_key = %s""", (workspace_id, clave))
        aviso = cur.fetchone()
        aviso_id = str(aviso["id"])
        if aviso["estado"] != "guardado":
            return ResultadoAviso("ya_enviado", aviso_id, None, aviso["hechos"])
        cur.execute("update scheduled_notice set intentos = intentos + 1 where id = %s",
                    (aviso_id,))

        pedido = {"hoy": ahora.astimezone(cal.zona).date().isoformat(),
                  "persona": fila["nombre"], "mensaje": None, "hechos": [aviso["hechos"]],
                  "ultimos_turnos": list(leer_ultimos_turnos(cur, membership_id))}
        try:
            texto = pedir_a_la_ia(lambda: no_vacio(ia.redactar(pedido)))
        except IANoRespondio:
            cur.execute("update scheduled_notice set proximo_intento_en = %s where id = %s",
                        (ahora, aviso_id))
            return ResultadoAviso("sin_redactar", aviso_id, None, aviso["hechos"])

        clave_outbox = f"motor:aviso:{aviso_id}"
        enqueue_outbox(cur, workspace_id=workspace_id, chat_id=fila["telegram_user_id"],
                       text=texto, dedupe_key=clave_outbox,
                       recipient_membership_id=membership_id, message_type="informativo",
                       scheduled_for=ahora)
        cur.execute("select id from message_outbox where dedupe_key = %s", (clave_outbox,))
        outbox_id = str(cur.fetchone()["id"])
        cur.execute("""update scheduled_notice
                          set estado = 'enviado', outbox_id = %s, resuelto_en = %s,
                              proximo_intento_en = null
                        where id = %s""", (outbox_id, ahora, aviso_id))
        registrar_salida(cur, workspace_id, membership_id, outbox_id, ia.nombre, ahora)
        cur.execute(
            """insert into conversation_state (membership_id, workspace_id, ultimo_aviso_id,
                                               actualizado_en)
               values (%s, %s, %s, %s)
               on conflict (membership_id) do update
                  set ultimo_aviso_id = excluded.ultimo_aviso_id,
                      actualizado_en = excluded.actualizado_en""",
            (membership_id, workspace_id, aviso_id, ahora))
        return ResultadoAviso("encolado", aviso_id, texto, aviso["hechos"])


def main(argv: list[str] | None = None) -> int:
    from leda.config import config
    from leda.db import admin, conectar
    from leda.despachador import TransporteTelegram, despachar, texto_error_seguro

    from .ia_real import desde_base
    from .tiempo import RelojDelSistema

    p = argparse.ArgumentParser(prog="python -m prueba_chica.avisar")
    p.add_argument("slug")
    p.add_argument("persona", help="nombre o apellido, entre comillas si son varias palabras")
    p.add_argument("tarea", help="palabras del título de la tarea")
    p.add_argument("--de-nuevo", action="store_true",
                   help="manda otro aviso aunque ya se haya mandado el de esa tarea")
    a = p.parse_args(argv)

    conn = conectar()
    with admin(conn) as cur:
        cur.execute("select id from workspace where slug = %s and activo", (a.slug,))
        fila = cur.fetchone()
    conn.commit()
    if fila is None:
        print(f"No hay un espacio activo '{a.slug}'.")
        return 1
    ws = str(fila["id"])
    reloj = RelojDelSistema()
    try:
        with espacio(conn, ws) as cur:
            membership_id, nombre, task_id = resolver(cur, a.persona, a.tarea)
            ia = desde_base(cur, ws, config)
        resultado = avisar_vencimiento(conn, ws, membership_id, task_id, ia, reloj,
                                       de_nuevo=a.de_nuevo)
        conn.commit()
    except (ValueError, LookupError) as e:
        conn.rollback()
        print(e)
        return 1

    if resultado.estado == "ya_enviado":
        print(f"El aviso de esa tarea ya se le mandó a {nombre}. Con --de-nuevo sale otro.")
        return 0
    if resultado.estado == "sin_redactar":
        print("La IA no respondió (dos intentos): el aviso quedó guardado sin enviar. "
              "Volvé a correr el comando.")
        return 1
    print(f"Aviso para {nombre} encolado:\n  {resultado.texto}")
    try:
        with espacio(conn, ws) as cur:
            r = despachar(cur, ws, TransporteTelegram(config.token_bot(a.slug)),
                          Calendario.desde_base(cur, ws), reloj.ahora())
        conn.commit()
    except Exception as e:  # noqa: BLE001 -- el aviso ya está en el outbox: sale después
        conn.rollback()
        print(f"No se pudo despachar ahora ({texto_error_seguro(e)}); "
              "sale con el escuchador.")
        return 1
    if r["pospuestos"]:
        print("Fuera del horario del espacio: sale al empezar la próxima jornada.")
    else:
        print(f"Despachado: {r['enviados']} enviado(s), {r['fallidos']} fallido(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
