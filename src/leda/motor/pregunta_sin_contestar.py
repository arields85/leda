"""Una pregunta de Leda sin contestar: cuánto frena los otros temas de la persona.

Decisión 21 del usuario (2026-10-08, opción B; `odd/tasks/fase-c.md`; conversación 30), del
`PENDIENTE` de la D5: con la regla de un tema a la vez (decisión 13, `avisos._un_tema_a_la_vez`),
una pregunta que nunca se contestaba frenaba para siempre los avisos que piden respuesta. Es una
regla general de la cocina, para todas las preguntas y todos los circuitos, no una regla para la
IA:

1. **La repetición del día** (`escalera`, `REPETICION_DEL_DIA`): la pregunta abierta frena los
   otros temas que piden respuesta hasta que Leda la repite, una sola vez en el día, a las 4 horas
   de haberla hecho (`ESPERA_POR_OMISION`, o `pregunta_sin_contestar_minutos` del espacio, como el
   margen para corregir). Sale haya o no otro tema esperando detrás (decisión 29 del usuario,
   2026-10-09: "las cuatro horas se cumplen justamente para evitar retrasos"), con las reglas de
   todo aviso: el horario y no interrumpir una conversación. Una pregunta que se hace una sola
   vez (decisión 12) o que no es de una tarea no se repite: su turno se cuenta igual, como si se
   hubiera repetido.
2. **El tema siguiente** (`termino_su_turno`): 4 horas después de la repetición, todavía en
   horario, la pregunta deja de frenar y sale aparte el tema siguiente más urgente
   (`avisos._un_tema_a_la_vez`); la pregunta queda para después. Una pregunta hecha un día
   anterior ya no frena: lo que espera sale de a uno, primero lo más urgente, que puede ser la
   misma pregunta repetida por su escalera ("al día siguiente sigue la escalera").
3. **La otra vuelve aparte** (`al_terminar_el_turno`, `VUELVE_LA_PREGUNTA`): las dos preguntas que
   quedaron abiertas a la vez porque un aviso hizo la segunda llevan `vuelve_aparte`. La persona
   contesta cualquiera, y cuando una se cierra el código trae la otra enseguida, en un mensaje
   aparte, que no espera los 30 minutos de la conversación (`no_interrumpir`) ni el horario: es
   parte de contestarle a la persona (mecánica §10) y sale como una respuesta (decidido por el
   coordinador a partir de la decisión 50).
4. **La pregunta que quedó por un cambio de tema vuelve aparte** (decisión 50 del usuario,
   2026-10-09, opción A; conversación 08): un mensaje, un tema. Si la respuesta del turno habló de
   otra cosa que la tarea de la pregunta que vuelve (`hablo_de_otro_tema`), la respuesta es sólo
   lo nuevo y la pregunta sale enseguida en su propio mensaje, por el mismo camino que la 3 (un
   aviso `VUELVE_LA_PREGUNTA`, que la IA redacta desde los hechos). El tema es la tarea: un
   mensaje sobre la pregunta misma ("y que pongo?", un botón viejo de esa entrega) o sobre su
   tarea la deja en la misma respuesta. La decide el código, nunca la IA. Una pregunta que no es
   de una tarea vuelve en la misma respuesta, como antes. Es la excepción acotada a "una respuesta
   visible por mensaje" (ADR 0013): el mensaje de la persona tiene una sola respuesta, y la
   pregunta que vuelve es un aviso aparte, como la de la regla 3.

5. **Una oferta opcional no es una pregunta sin contestar** (`preguntas.OPCIONAL`, "si lo
   necesitás"): no se repite (`se_repite`), no frena los otros temas (`termino_su_turno`) y no
   vuelve después de un cambio de tema (`al_terminar_el_turno`): sin respuesta es un no, y se
   cierra (la escalera la cierra a la hora en que se habría repetido;
   `escalera._repetir_las_preguntas_abiertas`).

**Cuándo se hizo una pregunta** (`preguntada_en`, migración 0040): la última vez que salió en un
mensaje de Leda, una respuesta (`al_terminar_el_turno`) o un aviso (`avisos._enviar`). Las filas de
antes de la migración cuentan desde `abierta_en`.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from . import preguntas

CLAVE = "pregunta_sin_contestar_minutos"
ESPERA_POR_OMISION = timedelta(hours=4)

# Los avisos que vuelven a hacer una pregunta sin contestar (`avisos.TIPOS`): la repetición del
# día, y la que vuelve aparte cuando se cerró la otra.
REPETICION_DEL_DIA = "repeticion_del_dia"
VUELVE_LA_PREGUNTA = "vuelve_la_pregunta"
# Por qué un aviso que repetía una pregunta no salió: la misma pregunta sale en otro aviso del
# mismo momento (su escalera), o la repetición era de otro día.
LA_MISMA_PREGUNTA_YA_SALE = "la_misma_pregunta_sale_en_otro_aviso"
YA_NO_ES_EL_DIA = "ya_no_es_el_dia_de_la_repeticion"


def espera_para_repetir(cur, workspace_id: str) -> timedelta:
    """La espera del espacio, o la del producto si no la configuró (o configuró algo que no es
    un número de minutos mayor que 0)."""
    cur.execute("select valor from workspace_setting where workspace_id = %s and clave = %s",
                (workspace_id, CLAVE))
    fila = cur.fetchone()
    valor = fila["valor"] if fila else None
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor <= 0:
        return ESPERA_POR_OMISION
    return timedelta(minutes=valor)


def se_repite(pregunta: dict[str, Any]) -> bool:
    """Si la pregunta se repite a las 4 horas: no si se hace una sola vez (decisión 12) ni si no
    es de una tarea (la duda de cuál, que vuelve en la respuesta siguiente)."""
    tipo = preguntas.TIPOS.get(pregunta["tipo"])
    return (pregunta["task_id"] is not None and tipo is not None
            and tipo.sin_elegir_queda is None and not preguntas.es_opcional(pregunta))


def preguntada_en(pregunta: dict[str, Any]) -> datetime:
    return pregunta.get("preguntada_en") or pregunta["abierta_en"]


def marcar_preguntada(cur, pregunta_id: str, ahora: datetime) -> None:
    cur.execute("update conversation_question set preguntada_en = %s where id = %s",
                (ahora, pregunta_id))


def clave_de_la_repeticion(pregunta: dict[str, Any], dia) -> str:
    """motor:repeticion_del_dia:<tarea>:q<pregunta>:<día>: una por pregunta y por día."""
    return f"motor:{REPETICION_DEL_DIA}:{pregunta['task_id']}:q{pregunta['id']}:{dia.isoformat()}"


def se_repitio_hoy(cur, pregunta: dict[str, Any], dia) -> bool:
    """Si la repetición del día de la pregunta ya salió."""
    cur.execute("""select 1 from scheduled_notice where dedupe_key = %s and estado = 'enviado'""",
                (clave_de_la_repeticion(pregunta, dia),))
    return cur.fetchone() is not None


def termino_su_turno(cur, cal, workspace_id: str, pregunta: dict[str, Any],
                     ahora: datetime) -> bool:
    """Si la pregunta abierta dejó de frenar los otros temas: se hizo un día anterior, o pasaron
    las 4 horas desde que se repitió hoy (la repetición la vuelve a hacer: cuenta desde ella).
    Una que no se repite, o cuya repetición no salió (omitida o fallida), cuenta las 4 horas de
    la repetición que no tuvo, más las del tema siguiente: nunca frena el resto del día."""
    if preguntas.es_opcional(pregunta):
        return True                     # una oferta opcional nunca frena nada
    zona = cal.zona
    hoy = ahora.astimezone(zona).date()
    desde = preguntada_en(pregunta)
    if desde.astimezone(zona).date() < hoy:
        return True
    espera = espera_para_repetir(cur, workspace_id)
    if se_repite(pregunta) and se_repitio_hoy(cur, pregunta, hoy):
        return ahora >= desde + espera
    return ahora >= desde + 2 * espera


def al_terminar_el_turno(ctx, temas: set[str] | None = None) -> dict[str, Any] | None:
    """La pregunta que se hace en la respuesta (`preguntas.al_terminar_el_turno`), salvo la que
    vuelve aparte; el código la trae enseguida en un mensaje aparte
    (`avisos.guardar_la_que_vuelve`):

    - si en este turno se cerró una de dos preguntas abiertas a la vez por un aviso, la otra
      (decisión 21);
    - si la pregunta viene de antes y el turno habló de otro tema (decisión 50): `temas`, las
      tareas de las que habló el mensaje (`turno.de_que_hablo`), o `None` si no habló de otra
      cosa que de la pregunta abierta.

    La que va en la respuesta queda preguntada ahora."""
    from .avisos import guardar_la_que_vuelve      # avisos importa este módulo

    pregunta = preguntas.al_terminar_el_turno(ctx)
    if pregunta is None:
        return None
    cur, persona = ctx.cur, ctx.quien.membership_id
    abierta = preguntas.actual(cur, persona)
    if pregunta["desde_antes"] and abierta["vuelve_aparte"] and _se_cerro_la_otra(ctx, abierta):
        guardar_la_que_vuelve(ctx, abierta)
        cur.execute("update conversation_question set vuelve_aparte = false where id = %s",
                    (abierta["id"],))
        return None
    if pregunta["desde_antes"] and hablo_de_otro_tema(abierta, temas):
        if preguntas.es_opcional(abierta):
            preguntas.caducar(cur, abierta, ctx.ahora)     # una oferta opcional no vuelve
            return None
        guardar_la_que_vuelve(ctx, abierta)
        return None
    marcar_preguntada(cur, str(abierta["id"]), ctx.ahora)
    return pregunta


def hablo_de_otro_tema(pregunta: dict[str, Any], temas: set[str] | None) -> bool:
    """Si el mensaje habló de otro tema que el de la pregunta (decisión 50): habló de algo
    (`temas` no es `None`) y ninguna de las tareas de las que habló es la de la pregunta. Una
    pregunta que no es de una tarea no tiene un tema que comparar: vuelve en la respuesta."""
    return (temas is not None and pregunta["task_id"] is not None
            and str(pregunta["task_id"]) not in temas)


def _se_cerro_la_otra(ctx, abierta: dict[str, Any]) -> bool:
    ctx.cur.execute("""select 1 from conversation_question
                        where membership_id = %s and vuelve_aparte and cerrada_en = %s
                          and id <> %s""", (ctx.quien.membership_id, ctx.ahora, abierta["id"]))
    return ctx.cur.fetchone() is not None


def quedaron_dos_abiertas(cur, antes: dict[str, Any] | None,
                          ahora: dict[str, Any] | None) -> None:
    """Un aviso hizo una pregunta y la que estaba abierta quedó para después: las dos vuelven
    aparte cuando se cierre la otra."""
    if antes is None or ahora is None or str(antes["id"]) == str(ahora["id"]):
        return
    las_dos = [str(antes["id"]), str(ahora["id"])]
    cur.execute("""select count(*) as n from conversation_question
                    where id = any(%s::uuid[]) and cerrada_en is null""", (las_dos,))
    if cur.fetchone()["n"] == 2:        # la de antes sigue sin cerrar: quedó para después
        cur.execute("""update conversation_question set vuelve_aparte = true
                        where id = any(%s::uuid[])""", (las_dos,))
