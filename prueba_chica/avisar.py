"""El aviso previo, disparado a mano (E2-3b; desde la E2-5, por el camino de los avisos guardados).

    python -m prueba_chica.avisar corework <persona> <palabras del título> [--de-nuevo]

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Avisos guardados"); ADR 0018, decisiones 8
y 9b. La escalera (`escalera.py`) guarda el aviso previo sola, a su hora; este comando lo guarda
en el momento, con la misma clave (no se repite: el de la escalera y el del comando son el
mismo) y los mismos hechos (la tarea, cuándo vence, cuántos días hábiles faltan y que no pide
respuesta), y lo manda por el mismo camino que todo aviso guardado (`avisos.enviar_avisos`):
se vuelve a leer la tarea, la IA lo redacta y recién entonces entra al outbox; después se
despacha. Lo que Leda inicia sale sólo dentro del horario del espacio: fuera de él, el aviso
queda guardado. Si la IA no redacta, queda guardado sin enviar, con su intento contado, y se
vuelve a intentar corriendo el comando otra vez (sin esperar el próximo reintento): nunca sale
un texto armado a mano.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import Any

import psycopg

from leda.calendario import Calendario
from leda.db import espacio

from .avisos import Momento, enviar_avisos, guardar, hechos_de_la_escalera, leer_tarea
from .fichas import ESTADOS_ABIERTOS, integrantes_que_coinciden, palabras
from .ia import IA
from .tiempo import Reloj

TIPO = "aviso_previo"
HECHOS_DEL_AVISO_PREVIO = {"aviso": "vencimiento_proximo", "necesita_respuesta": False}


@dataclass
class ResultadoAviso:
    estado: str         # encolado | ya_enviado | sin_redactar | fuera_de_horario | omitido
    aviso_id: str
    texto: str | None
    hechos: dict[str, Any]
    motivo: str | None = None   # el de la omisión


def clave_del_aviso_previo(task_id: str, vence: str) -> str:
    """La misma para la escalera y el comando: un aviso previo por tarea y vencimiento."""
    return f"motor:{TIPO}:{task_id}:{vence}"


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
    """Guarda el aviso previo de la tarea como hechos y lo manda por el camino de los avisos
    guardados. Sin `de_nuevo`, un aviso ya enviado de la misma tarea y vencimiento no se
    repite."""
    ahora = reloj.ahora()
    with espacio(conn, workspace_id) as cur:
        cur.execute("""select nombre, telegram_user_id from integrante
                        where membership_id = %s""", (membership_id,))
        persona = cur.fetchone()
        tarea = leer_tarea(cur, task_id)
        if persona is None or tarea is None or                 str(tarea["responsable_membership_id"]) != membership_id:
            raise ValueError("La tarea no es de esa persona.")
        if tarea["estado"] not in ESTADOS_ABIERTOS:
            raise ValueError(f"La tarea no está abierta (está {tarea['estado']}).")
        if tarea["fecha_objetivo"] is None:
            raise ValueError("La tarea no tiene fecha comprometida.")
        if persona["telegram_user_id"] is None:
            raise ValueError(f"{persona['nombre']} todavía no activó su Telegram.")

        m = Momento(cur, workspace_id, Calendario.desde_base(cur, workspace_id), ahora)
        hechos = hechos_de_la_escalera(m, TIPO, tarea, HECHOS_DEL_AVISO_PREVIO)
        clave = clave_del_aviso_previo(task_id, hechos["vence"])
        if de_nuevo:
            clave += f":{ahora.isoformat()}"
        aviso_id, _ = guardar(cur, workspace_id, TIPO, task_id=task_id,
                              destinatario=membership_id, hechos=hechos,
                              programado_para=ahora, clave=clave, ahora=ahora)
        cur.execute("select estado, hechos from scheduled_notice where id = %s", (aviso_id,))
        antes = cur.fetchone()
    if antes["estado"] != "guardado":
        return ResultadoAviso("ya_enviado", aviso_id, None, antes["hechos"])

    resumen = enviar_avisos(conn, workspace_id, ia, reloj, solo=aviso_id, forzar=True)
    with espacio(conn, workspace_id) as cur:
        cur.execute("""select a.estado, a.hechos, a.motivo_omision, o.cuerpo
                         from scheduled_notice a
                         left join message_outbox o on o.id = a.outbox_id
                        where a.id = %s""", (aviso_id,))
        despues = cur.fetchone()
    if "fuera_de_horario" in resumen:
        return ResultadoAviso("fuera_de_horario", aviso_id, None, despues["hechos"])
    estado = {"enviado": "encolado", "omitido": "omitido"}.get(despues["estado"],
                                                               "sin_redactar")
    return ResultadoAviso(estado, aviso_id, despues["cuerpo"], despues["hechos"],
                          despues["motivo_omision"])


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
        print("La IA no respondió: el aviso quedó guardado sin enviar. "
              "Volvé a correr el comando.")
        return 1
    if resultado.estado == "fuera_de_horario":
        print("Fuera del horario del espacio: el aviso quedó guardado y sale en horario "
              "(volvé a correr el comando entonces).")
        return 0
    if resultado.estado == "omitido":
        print(f"El aviso ya no corresponde y quedó omitido ({resultado.motivo}).")
        return 0
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
