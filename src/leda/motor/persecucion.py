"""La persecución de un bloqueo: escribirle a quien destraba (C-5, porciones 1 a 3).

Decisión 4 del usuario (`odd/tasks/fase-c.md`, 2026-10-08, opción A), primera mitad; ADR 0017,
decisión 3a (el seguimiento persigue los bloqueos hasta quien puede destrabarlos); ADR 0018, 9c,
paso 2; constitución §7 ("antes de prometer un envío, comprueba que el destinatario y el canal
estén conectados") y §8; conversación 32.

**Le escribe a quien destraba, como Leda** (`preguntarle`, desde `anotar_quien_destraba`).
Cuando la persona trabada nombra a otro integrante del equipo, Leda le guarda un aviso
(`avisos.PREGUNTA_A_QUIEN_DESTRABA`): quién está trabado, con qué tarea y qué le falta, y para
cuándo lo puede resolver. Sale terminado el margen para corregir (es por algo que dijo otra
persona, `margen.py`) y, al salir, abre la pregunta de quien destraba
(`preguntas.CUANDO_SE_DESTRABA`) con su propia espera: si no contesta, la escalera de las
preguntas la repite el día hábil siguiente, sin escalar, y vale la regla de una pregunta sin
contestar (decisión 21). La respuesta de la persona trabada dice que Leda le pregunta y cuándo le
llega (`se_le_pregunta_a`). Sin un chat con Leda, o fuera del equipo activo, no se guarda nada y
el hecho lo dice (`no_se_le_puede_escribir_a`): nunca se promete un mensaje que no va a salir. A
alguien de afuera del equipo Leda nunca le escribe (constitución §6): queda como antes.

**Lo que dice quien destraba** (`decir_cuando_destraba`): para cuándo lo resuelve, que ya está o
sus palabras. Queda como un hecho del bloqueo (`dicho_de_quien_destraba`, sólo se agrega),
atribuido y auditado, contesta su pregunta y su espera, y le llega a la persona trabada como
información, con el margen (`avisos.LO_QUE_DIJO_QUIEN_DESTRABA`). Un "ya está" no cierra el
bloqueo: quien destraba no es quien lo declaró ni el responsable (`resolver_bloqueo`), así que lo
cierra la persona trabada cuando dice que puede seguir (`destrabar`). Sólo lo dice quien destraba
la tarea ahora: la ve en su lista (`para_destrabar`), con su alias, después de las suyas.

**"Ya lo hablé con él"** (porción 2; decisión 4, segunda mitad; conversación 33): si quien
destraba dice que ya lo habló con la persona trabada sin decir para cuándo ni que ya está, no se
anota nada todavía: Leda le pregunta una vez qué arreglaron y para cuándo, para que quede
asentado (`_preguntar`: su pregunta sigue abierta, con su espera, y recuerda que ya lo hablaron).
Con la respuesta queda anotado, y a la persona trabada le llega como información, diciendo que lo
arreglaron entre ellos (`ya_lo_hablaron`). La respuesta no se vuelve a preguntar: si trae lo que
arreglaron sin una fecha, queda así. Lo que dijo cuando Leda le preguntó queda en su pregunta y
se anota junto con la respuesta (`_sus_palabras`): nada de lo que dice se pierde. Si quien
destraba habla antes de que le llegue el mensaje de Leda (la tarea ya está en su lista), ese
mensaje no sale (`avisos.ya_contesto_quien_destraba`).

**"No le escribas"** (`no_escribirle`): la persona trabada pide que Leda no le escriba a quien
destraba. Si el mensaje todavía no salió, queda omitido con su motivo (nunca se borra) y
auditado; si ya salió, el hecho dice que ya le llegó y cuándo: nunca se hace como que se retira.

Lo que espera de quien destraba se cierra cuando la tarea se destraba (`al_destrabarse`) o la
destraba otra persona (`preguntarle`); por cualquier otro camino, la escalera lo cierra al mirarlo
(`escalera._un_paso_de_una_pregunta`), y un aviso guardado no sale (su vigencia).

**"No me corresponde"** (porción 3; decisión 5, opción A con límite; ADR 0018, 9c, precisión
del 2026-10-09; conversación 34; `decir_que_no_le_toca`). Queda anotado que no le corresponde
(`dicho_de_quien_destraba.no_le_corresponde`, migración 0043) y, si dice quién se encarga o que
no sabe, otra fila de quién destraba dicha por esa persona. La cadena tiene un salto:

- **La primera persona** (la nombró quien está trabado) que no dice de quién es: Leda le pregunta
  una vez quién se encarga (su pregunta sigue abierta y lo recuerda); si vuelve a no decirlo, es
  que no sabe. Si nombra a otro integrante, Leda le escribe a esa persona como a la primera
  (`preguntarle`, diciendo quién la nombró), y la persona trabada se entera, como información.
- **Si la cadena se corta** (la segunda tampoco lo toma, cualquiera sea lo que diga; la primera no
  sabe, nombra a alguien de afuera o a la persona trabada, o nombra a alguien del equipo a quien
  Leda no le puede escribir), Leda no da más vueltas: le informa la cadena entera al referente
  (`avisos.CADENA_DEL_BLOQUEO`, `cadena`), sin pedirle nada, para que determine quién lo
  resuelve. Le llega una sola vez por cadena: lo que se diga después queda anotado, pero no se
  la manda otra vez (si todavía no salió, sale una, con lo último). Va al del sector de lo que
  falta si se sabe (el de la persona que quedó nombrada como quien se encarga) y, si no, al del
  sector de la tarea trabada; nunca a la persona trabada misma (entonces, a quien aprueba su
  trabajo; `a_quien_informar`). A la persona trabada le llega lo que pasó y que se informa, sin
  nombrar a quién por su cuenta (decisión 11: `hechos.NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO`,
  `aviso_de_la_cadena`). Sin referente, nada se promete y el hecho lo dice (`sin_referente`).

Fuera de estas porciones (`odd/tasks/fase-c.md`, C-5): los bloqueos encadenados y los avisos
hacia abajo (decisión 6) y el bloqueo viejo (7).
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from . import preguntas
from .auditoria import auditar
from .avisos import (CADENA_DEL_BLOQUEO, CAMBIO_QUIEN_DESTRABA, DIJO_ALGO_MAS_NUEVO,
                     LO_QUE_DIJO_QUIEN_DESTRABA, PREGUNTA_A_QUIEN_DESTRABA, guardar, integrante,
                     omitir)
from .fichas import (AVISO, LLEGA, NO_LE_LLEGO, NO_LE_VA_A_LLEGAR, PREGUNTA, YA_LE_LLEGO,
                     Contexto, _juntar, integrantes_que_coinciden, nombrar_efecto,
                     nombrar_tipo_de_pregunta, referente, tarea_hecho, vacio)
from .margen import sale_con_margen

# Por qué Leda no le escribe a quien destraba (los mismos códigos con que un aviso no sale).
SIN_TELEGRAM = "destinatario_sin_telegram"
INACTIVO = "destinatario_inactivo"
# Por qué no sale el mensaje a quien destraba: la persona trabada pidió que no le escriba.
PIDIO_QUE_NO_LE_ESCRIBA = "pidio_que_no_le_escriba"
# "No le escribas" que ya no puede hacer nada: el mensaje ya salió, o no había ninguno.
YA_SE_LE_ESCRIBIO = "ya_se_le_escribio"
NO_LE_IBA_A_ESCRIBIR = "no_le_iba_a_escribir"
# Quien escribe no es quien destraba esa tarea ahora.
NO_LE_TOCA_DESTRABARLA = "no_le_toca_destrabarla"
# Quien destraba dice que ya lo habló con la persona trabada (porción 2): lo recuerda su
# pregunta, en los datos de su jugada. Que Leda ya le preguntó qué arreglaron, en la jugada.
YA_LO_HABLARON = "ya_lo_hablaron"
PREGUNTO_QUE_ARREGLARON = "pregunto_que_arreglaron"
# Quien destraba dice que no le corresponde (porción 3): lo recuerda su pregunta, si Leda le
# pregunta quién se encarga; que ya se lo preguntó, en la jugada.
NO_LE_CORRESPONDE = "no_le_corresponde"
PREGUNTO_QUIEN_SE_ENCARGA = "pregunto_quien_se_encarga"
# Por qué la cadena no le llega a nadie: el sector no tiene referente ni hay quien apruebe el
# trabajo de la persona trabada.
SIN_REFERENTE = "sin_referente"


def alcanzable(cur, membership_id: str) -> tuple[dict[str, Any] | None, str | None]:
    """La persona y, si Leda no le puede escribir por chat, por qué (constitución §7)."""
    persona = integrante(cur, membership_id)
    if persona is None or not persona["activo"]:
        return persona, INACTIVO
    if persona["telegram_user_id"] is None:
        return persona, SIN_TELEGRAM
    return persona, None


# --- Le escribe a quien destraba ---------------------------------------------------------------

def preguntarle(ctx: Contexto, tarea: dict[str, Any], bloqueo: dict[str, Any], destraba_id: str,
                destraba: dict[str, Any], *, responsable: str | None = None,
                nombrado_por: str | None = None) -> dict[str, Any]:
    """Lo que pasa cuando la persona trabada nombra a otro integrante que destraba su tarea: lo
    que se le preguntaba a otra persona deja de esperar, y a ésta Leda le escribe si puede. Los
    hechos que se suman a los de `anotar_quien_destraba`. En la cadena (porción 3) la nombra
    quien no lo tomó: `responsable` es quien está trabado y `nombrado_por`, quien la nombró."""
    cur = ctx.cur
    task_id = str(tarea["id"])
    persona = str(destraba["membership_id"])
    preguntas.cerrar_las_de_otras_personas(
        ctx, preguntas.CUANDO_SE_DESTRABA, task_id, "sin_efecto",
        {"tarea": task_id, "cambio_quien_destraba": True}, salvo=persona)
    cur.execute("""select id, destinatario_membership_id, programado_para from scheduled_notice
                    where task_id = %s and tipo = %s and estado = 'guardado'""",
                (task_id, PREGUNTA_A_QUIEN_DESTRABA))
    # El que todavía no salió a otra persona queda atrás; el que va a esta misma persona es la
    # misma pregunta: sigue siendo ése, nunca dos.
    mismo = None
    for viejo in cur.fetchall():
        if str(viejo["destinatario_membership_id"]) == persona and mismo is None:
            mismo = viejo
        else:
            omitir(cur, str(viejo["id"]), CAMBIO_QUIEN_DESTRABA, ctx.ahora)
    quien, motivo = alcanzable(cur, persona)
    if motivo is not None:
        return {"no_se_le_puede_escribir_a": {"a": destraba["nombre"], "motivo": motivo}}
    if mismo is not None:
        hecho = {"se_le_pregunta_a": {"a": quien["nombre"],
                                      LLEGA: mismo["programado_para"].astimezone(
                                          ctx.calendario.zona).isoformat()}}
        nombrar_efecto(hecho, "se_le_pregunta_a", AVISO, mismo["id"])
        return hecho
    sale = sale_con_margen(cur, ctx.calendario, ctx.quien.workspace_id, ctx.ahora)
    aviso_id, _ = guardar(
        cur, ctx.quien.workspace_id, PREGUNTA_A_QUIEN_DESTRABA, task_id=task_id,
        destinatario=persona,
        hechos={"aviso": PREGUNTA_A_QUIEN_DESTRABA, "necesita_respuesta": True,
                "pregunta": preguntas.CUANDO_SE_DESTRABA, "tarea": tarea["titulo"],
                "responsable": responsable or ctx.quien.nombre, "causa": bloqueo["causa"],
                **({"nombrado_por": nombrado_por} if nombrado_por else {})},
        programado_para=sale, clave=f"motor:{PREGUNTA_A_QUIEN_DESTRABA}:{task_id}:u{destraba_id}",
        ahora=ctx.ahora)
    ctx.avisos_guardados.append(aviso_id)
    hecho: dict[str, Any] = {"se_le_pregunta_a": {"a": quien["nombre"], LLEGA: sale.isoformat()}}
    nombrar_efecto(hecho, "se_le_pregunta_a", AVISO, aviso_id)
    return hecho


def al_destrabarse(ctx: Contexto, task_id: str) -> None:
    """La tarea se destrabó: lo que se le preguntaba a quien la destraba ya no espera nada. Sus
    avisos guardados no salen (su vigencia: `avisos.YA_SE_DESTRABO`)."""
    preguntas.cerrar_las_de_otras_personas(
        ctx, preguntas.CUANDO_SE_DESTRABA, task_id, "sin_efecto",
        {"tarea": task_id, "ya_se_destrabo": True})


# --- Lo que la persona que destraba ve -------------------------------------------------------------

def para_destrabar(cur, membership_id: str, desde: int) -> tuple[dict[str, Any], ...]:
    """Las tareas de otras personas, trabadas, que destraba quien escribe (lo último que se dijo
    de su bloqueo abierto), con su alias (siguiendo los anteriores, desde `desde`), su
    responsable y su causa. No son tareas suyas."""
    cur.execute(
        """select t.id, t.titulo, t.estado::text estado, t.fecha_objetivo,
                  i.nombre as responsable, b.causa, b.abierto_en
             from blocker b
             join task t on t.id = b.task_id
             join integrante i on i.membership_id = t.responsable_membership_id
             join lateral (select u.destraba_membership_id from blocker_unblocker u
                            where u.blocker_id = b.id
                            order by u.at desc, u.id desc limit 1) u on true
            where b.resuelto_en is null and u.destraba_membership_id = %s
              and t.responsable_membership_id <> %s
              and t.estado not in ('terminada', 'cancelada')
            order by t.fecha_objetivo nulls last, t.titulo, b.abierto_en""",
        (membership_id, membership_id))
    vistas: dict[str, dict[str, Any]] = {}
    for t in cur.fetchall():
        vistas.setdefault(str(t["id"]), t)
    return tuple(
        {"alias": f"T{i}", "id": str(t["id"]), "titulo": t["titulo"], "estado": t["estado"],
         "fecha_objetivo": t["fecha_objetivo"].isoformat() if t["fecha_objetivo"] else None,
         "espera_que_la_destrabe": True, "responsable": t["responsable"], "causa": t["causa"]}
        for i, t in enumerate(vistas.values(), desde + 1))


# --- Lo que dice quien destraba -----------------------------------------------------------------

def decir_cuando_destraba(ctx: Contexto, datos: dict[str, Any],
                          tarea: dict[str, Any] | None) -> dict[str, Any]:
    """Quien destraba una tarea de otra persona dice para cuándo, que ya está o lo que pasa:
    queda anotado y la persona trabada se entera (ver el módulo)."""
    if tarea is None:
        tarea = _de_la_pregunta_abierta(ctx)
    if tarea is None:
        return {"resultado": "falta_dato", "falta": ["tarea"]}
    if not any(t["id"] == tarea["id"] for t in ctx.para_destrabar):
        return {"resultado": "no_se_puede", "motivo": NO_LE_TOCA_DESTRABARLA,
                "tarea": tarea_hecho(tarea)}
    para_cuando = None
    if not vacio(datos.get("para_cuando")):
        try:
            para_cuando = date.fromisoformat(str(datos["para_cuando"]).strip())
        except ValueError:
            return {"resultado": "falta_dato", "falta": ["para_cuando"],
                    "tarea": tarea_hecho(tarea)}
    ya_esta = datos.get("ya_esta") is True
    destraba = _lo_destraba(ctx, tarea["id"])
    if destraba is None:
        return {"resultado": "no_se_puede", "motivo": NO_LE_TOCA_DESTRABARLA,
                "tarea": tarea_hecho(tarea)}
    # "Ya lo hablé con él" (porción 2): lo dice ahora o lo dijo antes, en la misma pregunta.
    pregunta = _su_pregunta(ctx, tarea["id"])
    jugada = dict((pregunta or {}).get("jugada") or {})
    lo_que_dice = _sus_palabras(datos, jugada)
    ya_lo_hablaron = (datos.get("ya_lo_hablaron") is True
                      or (jugada.get("datos") or {}).get(YA_LO_HABLARON) is True)
    if (ya_lo_hablaron and para_cuando is None and not ya_esta
            and not jugada.get(PREGUNTO_QUE_ARREGLARON)):
        # Lo que queda asentado es lo que arreglaron y para cuándo: se pregunta una vez. Lo que
        # dijo queda en su pregunta y se anota con la respuesta.
        return _preguntar(ctx, tarea, destraba, pregunta,
                          {YA_LO_HABLARON: True,
                           **({"lo_que_dice": lo_que_dice} if lo_que_dice else {})},
                          PREGUNTO_QUE_ARREGLARON,
                          {"resultado": "falta_dato", "falta": ["lo_que_arreglaron", "para_cuando"],
                           "tarea": tarea_hecho(tarea), YA_LO_HABLARON: True})
    if para_cuando is None and not ya_esta and vacio(datos.get("lo_que_dice")):
        return {"resultado": "falta_dato", "falta": ["para_cuando"],
                "puede_ser": ["para_cuando", "ya_esta", "lo_que_dice"],
                "tarea": tarea_hecho(tarea)}
    dice = {k: v for k, v in (("para_cuando", para_cuando.isoformat() if para_cuando else None),
                              ("ya_esta", ya_esta or None), ("lo_que_dice", lo_que_dice),
                              (YA_LO_HABLARON, ya_lo_hablaron or None))
            if v is not None}
    dicho_id = _anotar_lo_que_dice(ctx, tarea, destraba, dice, para_cuando=para_cuando,
                                   ya_esta=ya_esta, lo_que_dice=lo_que_dice)
    hecho: dict[str, Any] = {"resultado": "anotado", "tarea": tarea_hecho(tarea),
                             "dice_quien_destraba": dice}
    _juntar(hecho, _avisar_a_quien_esta_trabado(ctx, tarea, destraba, dicho_id, dice))
    return hecho


def _anotar_lo_que_dice(ctx: Contexto, tarea: dict[str, Any], destraba: dict[str, Any],
                        dice: dict[str, Any], *, para_cuando: date | None = None,
                        ya_esta: bool = False, lo_que_dice: str | None = None,
                        no_le_corresponde: bool = False) -> str:
    """Lo que dice quien destraba, como un hecho del bloqueo sobre la fila que lo nombró
    (`dicho_de_quien_destraba`, sólo se agrega), atribuido y auditado; su pregunta y su espera
    se cierran. El id de lo anotado."""
    cur = ctx.cur
    cur.execute(
        """insert into dicho_de_quien_destraba (workspace_id, blocker_unblocker_id,
                                                dicho_por_membership_id, para_cuando, ya_esta,
                                                lo_que_dice, no_le_corresponde, at)
           values (%s, %s, %s, %s, %s, %s, %s, %s) returning id""",
        (ctx.quien.workspace_id, destraba["id"], ctx.quien.membership_id, para_cuando, ya_esta,
         lo_que_dice, no_le_corresponde, ctx.ahora))
    dicho_id = str(cur.fetchone()["id"])
    auditar(cur, accion=("anotar_que_no_le_toca" if no_le_corresponde
                         else "anotar_lo_que_dice_quien_destraba"),
            workspace_id=ctx.quien.workspace_id, sujeto_tipo="blocker",
            sujeto_id=destraba["blocker_id"], quien=ctx.quien,
            detalle={"dicho_id": dicho_id, "blocker_unblocker_id": str(destraba["id"]),
                     "task_id": tarea["id"], **dice, "at": ctx.ahora.isoformat(),
                     "inbound_message_id": ctx.entrante_id})
    _contestada(ctx, tarea["id"])
    return dicho_id


def _avisar_a_quien_esta_trabado(ctx: Contexto, tarea: dict[str, Any], destraba: dict[str, Any],
                                 dicho_id: str, dice: dict[str, Any],
                                 mas: dict[str, Any] | None = None) -> dict[str, Any]:
    """Lo que dijo quien destraba le llega a la persona trabada como información, terminado el
    margen para corregir (`avisos.LO_QUE_DIJO_QUIEN_DESTRABA`), con lo que pasa después
    (`mas`: a quién le pregunta Leda ahora, o que lo informa). Lo que dijo antes y todavía no le
    llegó queda atrás. Los hechos para quien escribe."""
    cur = ctx.cur
    responsable = str(destraba["responsable_membership_id"])
    quien, motivo = alcanzable(cur, responsable)
    if motivo is not None:
        return {"no_se_le_puede_escribir_a": {"a": quien["nombre"] if quien else None,
                                              "motivo": motivo}}
    cur.execute("""select a.id from scheduled_notice a
                    where a.task_id = %s and a.tipo = %s and a.estado = 'guardado'""",
                (tarea["id"], LO_QUE_DIJO_QUIEN_DESTRABA))
    for viejo in cur.fetchall():
        omitir(cur, str(viejo["id"]), DIJO_ALGO_MAS_NUEVO, ctx.ahora)
    sale = sale_con_margen(cur, ctx.calendario, ctx.quien.workspace_id, ctx.ahora)
    aviso_id, _ = guardar(
        cur, ctx.quien.workspace_id, LO_QUE_DIJO_QUIEN_DESTRABA, task_id=tarea["id"],
        destinatario=responsable,
        hechos={"aviso": LO_QUE_DIJO_QUIEN_DESTRABA, "necesita_respuesta": False,
                "tarea": tarea["titulo"], "quien_destraba": ctx.quien.nombre,
                "causa": destraba["causa"], "dice_quien_destraba": dice, **(mas or {})},
        programado_para=sale, clave=f"motor:{LO_QUE_DIJO_QUIEN_DESTRABA}:{tarea['id']}:d{dicho_id}",
        ahora=ctx.ahora)
    ctx.avisos_guardados.append(aviso_id)
    hecho: dict[str, Any] = {"aviso_a_quien_esta_trabado": {"a": quien["nombre"],
                                                            LLEGA: sale.isoformat()}}
    nombrar_efecto(hecho, "aviso_a_quien_esta_trabado", AVISO, aviso_id)
    return hecho


def _sus_palabras(datos: dict[str, Any], jugada: dict[str, Any]) -> str | None:
    """Lo que dice ahora quien destraba, junto con lo que dijo antes en la misma pregunta (lo
    recuerdan los datos de su jugada, `_preguntar`): nada de lo que dijo se pierde. Si una parte
    ya contiene a la otra, queda la más completa."""
    ahora = None if vacio(datos.get("lo_que_dice")) else str(datos["lo_que_dice"]).strip()
    antes = (jugada.get("datos") or {}).get("lo_que_dice")
    antes = None if vacio(antes) else str(antes).strip()
    if antes is None or ahora is None:
        return ahora or antes
    if antes in ahora or ahora in antes:
        return max(antes, ahora, key=len)
    return f"{antes} / {ahora}"


def _lo_destraba(ctx: Contexto, task_id: str) -> dict[str, Any] | None:
    """La fila de quién destraba el bloqueo abierto de esa tarea, si quien escribe es quien la
    destraba ahora (lo último que se dijo), con el bloqueo, la tarea y quién la tiene."""
    ctx.cur.execute(
        """select u.id, u.blocker_id, u.dicho_por_membership_id, b.causa, t.area_id,
                  t.responsable_membership_id, i.nombre as responsable
             from blocker b
             join task t on t.id = b.task_id
             join integrante i on i.membership_id = t.responsable_membership_id
             join lateral (select u.id, u.blocker_id, u.destraba_membership_id,
                                  u.dicho_por_membership_id
                             from blocker_unblocker u where u.blocker_id = b.id
                            order by u.at desc, u.id desc limit 1) u on true
            where b.task_id = %s and b.resuelto_en is null
              and u.destraba_membership_id = %s
            order by b.abierto_en desc, b.id desc limit 1""", (task_id, ctx.quien.membership_id))
    return ctx.cur.fetchone()


def _su_pregunta(ctx: Contexto, task_id: str) -> dict[str, Any] | None:
    """La pregunta sin cerrar de quien escribe sobre para cuándo destraba esa tarea, si la hay."""
    ctx.cur.execute("""select * from conversation_question
                        where membership_id = %s and tipo = %s and task_id = %s
                          and cerrada_en is null
                        order by abierta_en desc, id desc limit 1""",
                    (ctx.quien.membership_id, preguntas.CUANDO_SE_DESTRABA, task_id))
    return ctx.cur.fetchone()


def _preguntar(ctx: Contexto, tarea: dict[str, Any], destraba: dict[str, Any],
               pregunta: dict[str, Any] | None, recuerda: dict[str, Any], pregunto: str,
               hecho: dict[str, Any]) -> dict[str, Any]:
    """Lo que dijo quien destraba no alcanza para anotarlo: su pregunta sigue abierta, con su
    espera, y recuerda lo que ya dijo (`recuerda`, en los datos de su jugada: lo dice la
    repetición, `preguntas.lo_anotado`) y lo que Leda ya le preguntó (`pregunto`, aparte: no se
    vuelve a preguntar). Si el mensaje de Leda todavía no le llegó, se la hace
    ahora, atada a la misma fila que la habría abierto (`avisos._abre_cuando_se_destraba`); ese
    mensaje ya no sale (`avisos.ya_contesto_quien_destraba`). Los hechos la nombran como a toda
    pregunta."""
    if pregunta is not None:
        jugada = dict(pregunta["jugada"] or {})
    else:
        jugada = {"nombre": "anotar_quien_destraba",
                  "datos": {"responsable": destraba["responsable"], "causa": destraba["causa"]},
                  "destraba_id": str(destraba["id"])}
    jugada["datos"] = {**(jugada.get("datos") or {}), **recuerda}
    jugada[pregunto] = True
    ahora, pregunta_id = preguntas.abrir_con_id(ctx, preguntas.CUANDO_SE_DESTRABA, tarea["id"],
                                                jugada=jugada)
    clave = "pregunta" if ahora else "pregunta_para_despues"
    nombrar_efecto(hecho, clave, PREGUNTA, pregunta_id)
    nombrar_tipo_de_pregunta(hecho, clave, preguntas.CUANDO_SE_DESTRABA)
    return hecho


def _de_la_pregunta_abierta(ctx: Contexto) -> dict[str, Any] | None:
    """La tarea de la pregunta de quien destraba que la persona tiene sin cerrar (la abierta o
    una para después), o la única que destraba."""
    ctx.cur.execute("""select task_id from conversation_question
                        where membership_id = %s and tipo = %s and cerrada_en is null
                        order by para_despues_en nulls first, abierta_en, id limit 1""",
                    (ctx.quien.membership_id, preguntas.CUANDO_SE_DESTRABA))
    fila = ctx.cur.fetchone()
    if fila is not None:
        return next((t for t in ctx.para_destrabar if t["id"] == str(fila["task_id"])), None)
    return ctx.para_destrabar[0] if len(ctx.para_destrabar) == 1 else None


def _contestada(ctx: Contexto, task_id: str) -> None:
    """Su pregunta y su espera se cierran: ya contestó."""
    preguntas.cerrar_de_tipo(ctx, preguntas.CUANDO_SE_DESTRABA, task_id, "respondida",
                             {"jugada": "decir_cuando_destraba", "tarea": task_id})
    ctx.cur.execute("""update pending_reply set satisfecho_en = %s
                        where membership_id = %s and task_id = %s and tipo = %s
                          and satisfecho_en is null""",
                    (ctx.ahora, ctx.quien.membership_id, task_id,
                     preguntas.CUANDO_SE_DESTRABA))


# --- "No me corresponde" (porción 3) -----------------------------------------------------------

def decir_que_no_le_toca(ctx: Contexto, datos: dict[str, Any],
                         tarea: dict[str, Any] | None) -> dict[str, Any]:
    """Quien destraba una tarea de otra persona dice que no le corresponde y, si lo sabe, quién se
    encarga: Leda sigue con esa persona una vez o le informa la cadena al referente (ver el
    módulo)."""
    cur = ctx.cur
    if tarea is None:
        tarea = _de_la_pregunta_abierta(ctx)
    if tarea is None:
        return {"resultado": "falta_dato", "falta": ["tarea"]}
    if not any(t["id"] == tarea["id"] for t in ctx.para_destrabar):
        return {"resultado": "no_se_puede", "motivo": NO_LE_TOCA_DESTRABARLA,
                "tarea": tarea_hecho(tarea)}
    destraba = _lo_destraba(ctx, tarea["id"])
    if destraba is None:
        return {"resultado": "no_se_puede", "motivo": NO_LE_TOCA_DESTRABARLA,
                "tarea": tarea_hecho(tarea)}
    pregunta = _su_pregunta(ctx, tarea["id"])
    jugada = dict((pregunta or {}).get("jugada") or {})
    lo_que_dice = _sus_palabras(datos, jugada)
    no_sabe = datos.get("no_sabe") is True
    integrante, externo = None, None
    if not no_sabe and not vacio(datos.get("quien")):
        texto = str(datos["quien"]).strip()
        coinciden = integrantes_que_coinciden(cur, texto)
        if len(coinciden) > 1:
            return {"resultado": "falta_dato", "falta": ["integrante"],
                    "coinciden": [c["nombre"] for c in coinciden], "tarea": tarea_hecho(tarea)}
        if coinciden:
            # Nombrarse a sí misma no es decir de quién es.
            if str(coinciden[0]["membership_id"]) != ctx.quien.membership_id:
                integrante = coinciden[0]
        else:
            externo = texto
    # La primera persona de la cadena (la nombró quien está trabado) que no dice de quién es:
    # Leda le pregunta una vez quién se encarga. Si vuelve a no decirlo, es que no sabe.
    primera = str(destraba["dicho_por_membership_id"]) == str(
        destraba["responsable_membership_id"])
    nombra = integrante is not None or externo is not None
    if primera and not nombra and not no_sabe:
        if not jugada.get(PREGUNTO_QUIEN_SE_ENCARGA):
            return _preguntar(
                ctx, tarea, destraba, pregunta,
                {NO_LE_CORRESPONDE: True, **({"lo_que_dice": lo_que_dice} if lo_que_dice else {})},
                PREGUNTO_QUIEN_SE_ENCARGA,
                {"resultado": "falta_dato", "falta": ["quien_se_encarga"],
                 "tarea": tarea_hecho(tarea)})
        no_sabe = True

    le_toca_a = (integrante["nombre"] if integrante is not None else externo)
    dice = {k: v for k, v in ((NO_LE_CORRESPONDE, True), ("le_toca_a", le_toca_a),
                              ("no_sabe", no_sabe or None), ("lo_que_dice", lo_que_dice))
            if v is not None}
    dicho_id = _anotar_lo_que_dice(ctx, tarea, destraba, dice, lo_que_dice=lo_que_dice,
                                   no_le_corresponde=True)
    if nombra or no_sabe:
        # A quién le toca, según quien no lo toma: otra fila de quién destraba, dicha por él.
        nueva = _anotar_quien_destraba(ctx, tarea, destraba, integrante, externo, no_sabe)
    hecho: dict[str, Any] = {"resultado": "anotado", "tarea": tarea_hecho(tarea),
                             "dice_quien_destraba": dice}
    bloqueo = {"causa": destraba["causa"]}
    sigue: dict[str, Any] = {}
    if primera and integrante is not None and str(integrante["membership_id"]) != str(
            destraba["responsable_membership_id"]):
        # Leda sigue con esa persona, como siguió con la primera (una sola vez: el límite).
        sigue = preguntarle(ctx, {"id": tarea["id"], "titulo": tarea["titulo"]}, bloqueo,
                            nueva, integrante, responsable=destraba["responsable"],
                            nombrado_por=ctx.quien.nombre)
        _juntar(hecho, sigue)
    if "se_le_pregunta_a" in sigue:
        mas = {"se_le_pregunta_a": {"a": sigue["se_le_pregunta_a"]["a"]}}
    else:
        # La cadena se corta: al referente, con la cadena entera, como información. También si
        # a quien nombró la primera no se le puede escribir: Leda no puede seguir con esa
        # persona, y la cadena no queda en silencio (revisión del 2026-10-09).
        sin_chat = sigue.get("no_se_le_puede_escribir_a")
        informe = _informar_la_cadena(ctx, tarea, destraba, dicho_id,
                                      integrante["membership_id"] if integrante else None,
                                      sin_chat=sin_chat)
        _juntar(hecho, informe)
        mas = {**({"no_se_le_puede_escribir_a": sin_chat} if sin_chat else {}),
               "aviso_de_la_cadena": {k: v for k, v in informe["aviso_de_la_cadena"].items()
                                      if k != LLEGA or not _es_una_hora(v)}}
    _juntar(hecho, _avisar_a_quien_esta_trabado(ctx, tarea, destraba, dicho_id, dice, mas))
    return hecho


def _anotar_quien_destraba(ctx: Contexto, tarea: dict[str, Any], destraba: dict[str, Any],
                           integrante: dict[str, Any] | None, externo: str | None,
                           no_sabe: bool) -> str:
    """Quién destraba ahora, según quien escribe: otra fila de `blocker_unblocker`, dicha por
    esa persona y auditada como cuando lo dice quien está trabado. Su id."""
    ctx.cur.execute(
        """insert into blocker_unblocker (workspace_id, blocker_id, destraba_membership_id,
                                          destraba_externo, no_sabe,
                                          dicho_por_membership_id, at)
           values (%s, %s, %s, %s, %s, %s, %s) returning id""",
        (ctx.quien.workspace_id, destraba["blocker_id"],
         integrante["membership_id"] if integrante else None, externo, no_sabe,
         ctx.quien.membership_id, ctx.ahora))
    nueva = str(ctx.cur.fetchone()["id"])
    auditar(ctx.cur, accion="anotar_quien_destraba", workspace_id=ctx.quien.workspace_id,
            sujeto_tipo="blocker", sujeto_id=destraba["blocker_id"], quien=ctx.quien,
            detalle={"blocker_unblocker_id": nueva, "task_id": tarea["id"],
                     "destraba_membership_id": (str(integrante["membership_id"])
                                                if integrante else None),
                     "destraba_externo": externo, "no_sabe": no_sabe,
                     "at": ctx.ahora.isoformat(), "inbound_message_id": ctx.entrante_id})
    return nueva


def a_quien_informar(cur, destraba: dict[str, Any],
                     nombrado: str | None) -> dict[str, Any] | None:
    """El referente al que va la cadena (decisión 5): el del sector de lo que falta, si se sabe
    (el de la persona que quedó nombrada como quien se encarga); si no, el del sector de la tarea
    trabada. Nunca la persona trabada misma: si es ella, a quien aprueba su trabajo. `None` si no
    hay ninguno."""
    trabado = str(destraba["responsable_membership_id"])
    areas = []
    if nombrado is not None and str(nombrado) != trabado:
        persona = integrante(cur, nombrado)
        if persona is not None:
            areas.append(persona["area_id"])
    areas.append(destraba["area_id"])
    for area in areas:
        cur.execute("""select i.membership_id, i.nombre from area a
                         join integrante i on i.membership_id = a.referente_membership_id
                        where a.id = %s""", (str(area),))
        fila = cur.fetchone()
        if fila is not None and str(fila["membership_id"]) != trabado:
            return fila
    return referente(cur, trabado)


def _informar_la_cadena(ctx: Contexto, tarea: dict[str, Any], destraba: dict[str, Any],
                        dicho_id: str, nombrado: str | None, *,
                        sin_chat: dict[str, Any] | None = None) -> dict[str, Any]:
    """La cadena entera le llega al referente como información, terminado el margen para
    corregir (`avisos.CADENA_DEL_BLOQUEO`): no le pide nada (ADR 0018, 9c, precisión del
    2026-10-09). `sin_chat`: a quién quedó nombrado y Leda no le puede escribir, y por qué.

    Le llega una sola vez por cadena (desde la última vez que la persona trabada dijo quién lo
    destraba; revisión del 2026-10-09): si ya salió, no se manda otra vez y los hechos dicen que
    ya le llegó; si todavía no salió, la anterior queda omitida (nunca se borra) y sale ésta, con
    lo último que se dijo. Los hechos para quien escribe: a quién y cuándo, o por qué no le
    llega."""
    cur = ctx.cur
    previas = _cadenas_de_esta_vuelta(cur, destraba, tarea["id"])
    enviada = next((p for p in previas if p["estado"] == "enviado"), None)
    if enviada is not None:
        return {"aviso_de_la_cadena": {
            "a": enviada["a_nombre"], LLEGA: YA_LE_LLEGO,
            "el": enviada["resuelto_en"].astimezone(ctx.calendario.zona).date().isoformat()}}
    guardadas = [p for p in previas if p["estado"] == "guardado"]
    ref = a_quien_informar(cur, destraba, nombrado)
    quien, motivo = (alcanzable(cur, str(ref["membership_id"])) if ref is not None
                     else (None, SIN_REFERENTE))
    if motivo is not None:
        if guardadas:
            # La que ya estaba guardada sigue: es la que le llega.
            ultima = guardadas[-1]
            return {"aviso_de_la_cadena": {
                "a": ultima["a_nombre"],
                LLEGA: ultima["programado_para"].astimezone(ctx.calendario.zona).isoformat()}}
        if ref is None:
            return {"aviso_de_la_cadena": {LLEGA: NO_LE_VA_A_LLEGAR, "motivo": SIN_REFERENTE}}
        return {"aviso_de_la_cadena": {"a": ref["nombre"], LLEGA: NO_LE_VA_A_LLEGAR,
                                       "motivo": motivo}}
    for vieja in guardadas:
        omitir(cur, str(vieja["id"]), DIJO_ALGO_MAS_NUEVO, ctx.ahora)
    sale = sale_con_margen(cur, ctx.calendario, ctx.quien.workspace_id, ctx.ahora)
    eslabones = cadena(cur, destraba["blocker_id"], str(destraba["responsable_membership_id"]))
    aviso_id, _ = guardar(
        cur, ctx.quien.workspace_id, CADENA_DEL_BLOQUEO, task_id=tarea["id"],
        destinatario=str(ref["membership_id"]),
        hechos={"aviso": CADENA_DEL_BLOQUEO, "necesita_respuesta": False,
                "tarea": tarea["titulo"], "responsable": destraba["responsable"],
                "causa": destraba["causa"], "cadena": eslabones,
                **({"no_se_le_puede_escribir_a": sin_chat} if sin_chat else {})},
        programado_para=sale, clave=f"motor:{CADENA_DEL_BLOQUEO}:{tarea['id']}:d{dicho_id}",
        ahora=ctx.ahora)
    ctx.avisos_guardados.append(aviso_id)
    auditar(cur, accion="informar_la_cadena_del_bloqueo", workspace_id=ctx.quien.workspace_id,
            sujeto_tipo="blocker", sujeto_id=destraba["blocker_id"], quien=ctx.quien,
            detalle={"aviso_id": aviso_id, "task_id": tarea["id"],
                     "a_membership_id": str(ref["membership_id"]), "cadena": eslabones,
                     "at": ctx.ahora.isoformat(), "inbound_message_id": ctx.entrante_id})
    hecho: dict[str, Any] = {"aviso_de_la_cadena": {"a": quien["nombre"],
                                                    LLEGA: sale.isoformat()}}
    nombrar_efecto(hecho, "aviso_de_la_cadena", AVISO, aviso_id)
    return hecho


def _cadenas_de_esta_vuelta(cur, destraba: dict[str, Any], task_id: str) -> list[dict[str, Any]]:
    """Los avisos de la cadena ya guardados para esta vuelta del bloqueo: los de lo que se dijo
    desde la última vez que la persona trabada dijo quién lo destraba (la clave de cada uno
    nombra lo dicho, `avisos.de_la_clave`), del más viejo al más nuevo."""
    cur.execute("""select s.at, s.id from blocker_unblocker s
                    where s.blocker_id = %s and s.dicho_por_membership_id = %s
                    order by s.at desc, s.id desc limit 1""",
                (str(destraba["blocker_id"]), str(destraba["responsable_membership_id"])))
    desde = cur.fetchone()
    cur.execute(
        """select a.id, a.estado, a.programado_para, a.resuelto_en, i.nombre as a_nombre
             from scheduled_notice a
             join dicho_de_quien_destraba d
               on d.id::text = substr(split_part(a.dedupe_key, ':', 4), 2)
             join blocker_unblocker u on u.id = d.blocker_unblocker_id
             left join integrante i on i.membership_id = a.destinatario_membership_id
            where a.tipo = %s and a.task_id = %s and u.blocker_id = %s
              and (%s::timestamptz is null or (u.at, u.id) >= (%s::timestamptz, %s::uuid))
            order by a.creado_en, a.id""",
        (CADENA_DEL_BLOQUEO, str(task_id), str(destraba["blocker_id"]),
         desde["at"] if desde else None, desde["at"] if desde else None,
         str(desde["id"]) if desde else None))
    return cur.fetchall()


def cadena(cur, blocker_id, trabado: str) -> list[dict[str, Any]]:
    """La cadena de un bloqueo, de quién dijo qué, desde la última vez que la persona trabada
    dijo quién lo destraba: a quién le toca según cada uno (`blocker_unblocker`), y si dijo que
    no le corresponde, con sus palabras (`dicho_de_quien_destraba`). Quien no lo tomó sin decir
    de quién es cierra la cadena con lo que dijo."""
    cur.execute("""select u.id, u.destraba_membership_id, u.destraba_externo, u.no_sabe,
                          u.dicho_por_membership_id, d.nombre as destraba, p.nombre as de
                     from blocker_unblocker u
                     left join integrante d on d.membership_id = u.destraba_membership_id
                     join integrante p on p.membership_id = u.dicho_por_membership_id
                    where u.blocker_id = %s order by u.at, u.id""", (str(blocker_id),))
    filas = cur.fetchall()
    desde = max((i for i, f in enumerate(filas) if str(f["dicho_por_membership_id"]) == trabado),
                default=0)
    filas = filas[desde:]
    cur.execute("""select blocker_unblocker_id, dicho_por_membership_id, lo_que_dice
                     from dicho_de_quien_destraba
                    where blocker_unblocker_id = any(%s::uuid[]) and no_le_corresponde
                    order by at, id""", ([str(f["id"]) for f in filas],))
    no_les_toca = {(str(d["blocker_unblocker_id"]), str(d["dicho_por_membership_id"])): d
                   for d in cur.fetchall()}
    eslabones: list[dict[str, Any]] = []
    anterior = None
    for f in filas:
        eslabon: dict[str, Any] = {"de": f["de"]}
        dijo = (no_les_toca.get((str(anterior["id"]), str(f["dicho_por_membership_id"])))
                if anterior is not None else None)
        if dijo is not None:
            eslabon[NO_LE_CORRESPONDE] = True
        if f["destraba"] or f["destraba_externo"]:
            eslabon["le_toca_a"] = f["destraba"] or f["destraba_externo"]
        if f["no_sabe"]:
            eslabon["no_sabe"] = True
        if dijo is not None and dijo["lo_que_dice"]:
            eslabon["lo_que_dice"] = dijo["lo_que_dice"]
        eslabones.append(eslabon)
        anterior = f
    if anterior is not None and anterior["destraba_membership_id"] is not None:
        dijo = no_les_toca.get((str(anterior["id"]), str(anterior["destraba_membership_id"])))
        if dijo is not None:
            eslabones.append({"de": anterior["destraba"], NO_LE_CORRESPONDE: True,
                              **({"lo_que_dice": dijo["lo_que_dice"]}
                                 if dijo["lo_que_dice"] else {})})
    return eslabones


def _es_una_hora(valor: Any) -> bool:
    """Si cuándo se entera es una fecha y hora (y no un código, como que no le va a llegar)."""
    return isinstance(valor, str) and re.match(r"^\d{4}-\d{2}-\d{2}T", valor) is not None


# --- "No le escribas" ------------------------------------------------------------------------

def no_escribirle(ctx: Contexto, datos: dict[str, Any],
                  tarea: dict[str, Any] | None) -> dict[str, Any]:
    """La persona trabada pide que Leda no le escriba a quien destraba (ver el módulo)."""
    cur = ctx.cur
    suyas = [t for t in ctx.tareas if tarea is None or t["id"] == tarea["id"]]
    if not suyas:
        return {"resultado": "no_se_puede", "motivo": NO_LE_IBA_A_ESCRIBIR}
    cur.execute(
        """select distinct on (a.task_id) a.*, i.nombre as a_nombre
             from scheduled_notice a
             join integrante i on i.membership_id = a.destinatario_membership_id
            where a.tipo = %s and a.task_id = any(%s::uuid[])
            order by a.task_id, a.creado_en desc, a.id desc""",
        (PREGUNTA_A_QUIEN_DESTRABA, [t["id"] for t in suyas]))
    avisos = cur.fetchall()
    if not vacio(datos.get("quien")):
        nombrados = {str(c["membership_id"])
                     for c in integrantes_que_coinciden(cur, str(datos["quien"]))}
        avisos = [a for a in avisos if str(a["destinatario_membership_id"]) in nombrados]
    guardados = [a for a in avisos if a["estado"] == "guardado"]
    if len(guardados) > 1:
        return {"resultado": "falta_dato", "falta": ["tarea"],
                "coinciden": [_titulo(ctx, a["task_id"]) for a in guardados]}
    if not guardados and len(avisos) > 1:
        avisos = sorted(avisos, key=lambda a: (a["creado_en"], str(a["id"])))[-1:]
    aviso = (guardados or avisos or [None])[0]
    if aviso is None:
        hecho: dict[str, Any] = {"resultado": "no_se_puede", "motivo": NO_LE_IBA_A_ESCRIBIR}
        if tarea is not None:
            hecho["tarea"] = tarea_hecho(tarea)
        return hecho
    de_la = next(t for t in suyas if t["id"] == str(aviso["task_id"]))
    hecho = {"tarea": tarea_hecho(de_la)}
    if aviso["estado"] == "guardado":
        omitir(cur, str(aviso["id"]), PIDIO_QUE_NO_LE_ESCRIBA, ctx.ahora)
        auditar(cur, accion="no_escribirle", workspace_id=ctx.quien.workspace_id,
                sujeto_tipo="scheduled_notice", sujeto_id=aviso["id"], quien=ctx.quien,
                detalle={"aviso_id": str(aviso["id"]), "task_id": de_la["id"],
                         "destinatario_membership_id": str(aviso["destinatario_membership_id"]),
                         "at": ctx.ahora.isoformat(), "inbound_message_id": ctx.entrante_id})
        return {"resultado": "anotado", **hecho,
                "se_le_pregunta_a": {"a": aviso["a_nombre"], LLEGA: NO_LE_VA_A_LLEGAR,
                                     "motivo": PIDIO_QUE_NO_LE_ESCRIBA}}
    if aviso["estado"] == "enviado":
        el = aviso["resuelto_en"].astimezone(ctx.calendario.zona).date().isoformat()
        return {"resultado": "no_se_puede", "motivo": YA_SE_LE_ESCRIBIO, **hecho,
                "se_le_pregunta_a": {"a": aviso["a_nombre"], LLEGA: YA_LE_LLEGO, "el": el}}
    return {"resultado": "no_se_puede", "motivo": NO_LE_IBA_A_ESCRIBIR, **hecho,
            "se_le_pregunta_a": {"a": aviso["a_nombre"],
                                 LLEGA: NO_LE_LLEGO if aviso["estado"] == "fallido"
                                 else NO_LE_VA_A_LLEGAR,
                                 **({"motivo": aviso["motivo_omision"]}
                                    if aviso["motivo_omision"] else {})}}


def _titulo(ctx: Contexto, task_id) -> dict[str, str]:
    return tarea_hecho(next(t for t in ctx.tareas if t["id"] == str(task_id)))
