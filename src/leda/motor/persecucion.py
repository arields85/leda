"""La persecución de un bloqueo: escribirle a quien destraba (C-5, porciones 1 a 3; C-5d).

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

**Sin Leda conectada** (decisión 37 del usuario, 2026-10-09; C-5b): a quien no tiene un chat con
Leda, el administrador recibe el aviso para conectarlo, de verdad, por su canal (un incidente,
`avisar_para_que_lo_conecte`); el hecho dice que se le avisó y cuándo le llega, o que no le llega
si ningún administrador es alcanzable (`SE_LE_AVISO_AL_ADMINISTRADOR`). A la persona trabada, Leda
le ofrece salidas (`SALIDAS_SIN_LEDA_CONECTADA`, un tema abierto como toda propuesta): otra persona
que pueda destrabarlo, o que se lo pida ella y le cuente (lo que cuente cierra el tema: quién lo
destraba, o que ya puede seguir). Lo mismo para un pase a alguien sin Leda conectada (`pase.py`).

**A quien no contesta, Leda nunca lo abandona** (decisión 38 del usuario; C-5b): la escalera de
las preguntas le repite la pregunta los días 1 a 3 una vez por día y, desde el 4, cada 2 días
hábiles mientras siga el bloqueo, sin escalar (`escalera._un_paso_de_una_pregunta`); si escribe
por otra cosa, la pregunta vuelve en un mensaje aparte (decisión 50,
`pregunta_sin_contestar.al_terminar_el_turno`).

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
no sabe, otra fila de quién destraba dicha por esa persona. **La cadena llega hasta tres personas
preguntadas** (decisión 51, C-5d; `LIMITE_DE_LA_CADENA`), contadas en la vuelta (`_vuelta`: desde
la última vez que la persona trabada dijo por su cuenta quién lo destraba):

- **Mientras haya lugar**, quien no dice de quién es recibe una pregunta (quién se encarga; su
  pregunta sigue abierta y lo recuerda); si vuelve a no decirlo, es que no sabe. Si nombra a otro
  integrante, Leda le escribe a esa persona como a la primera (`preguntarle`, diciendo quién la
  nombró), y la persona trabada se entera, como información.
- **"Ni idea", con lugar** (decisión 49, C-5d): antes de asentarlo, Leda le pregunta a la persona
  trabada si se le ocurre otra persona (`avisos.QUIEN_MAS_PUEDE_DESTRABAR`, con lo que dijo quien
  no lo toma; abre su pregunta de quién lo destraba). Lo que conteste sigue la misma cadena: si
  nombra a alguien, Leda sigue con esa persona; si no, queda asentado (`sin_otra_persona`).
- **Si la cadena se corta** (la tercera tampoco lo toma, cualquiera sea lo que diga; alguien
  nombra a alguien de afuera, a la persona trabada o a alguien del equipo a quien Leda no le
  puede escribir; la persona trabada no sabe de nadie más), Leda no da más vueltas: le informa la
  cadena entera a quien decide quién lo resuelve (`avisos.CADENA_DEL_BLOQUEO`, `cadena`), sin
  pedirle nada. Le llega una sola vez por vuelta: lo que se diga después queda anotado, pero no
  se la manda otra vez (si todavía no salió, sale una, con lo último). **Nunca a alguien de la
  cadena** (decisión 24, C-5d; `a_quien_informar`): al referente del sector de la tarea trabada;
  si es la persona trabada o alguien de la cadena, a quien aprueba el trabajo de la persona
  trabada. A la persona trabada le llega lo que pasó y que quedó asentado, sin decir que se le
  informa a alguien ni nombrar a quién por su cuenta (decisiones 11 y 35: `queda_asentado`,
  `asentado.py`, `hechos.NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO`). Sin nadie a quien informar (sin
  referente ni quien apruebe fuera de la cadena, o sin Leda conectada), a nadie se le promete el
  aviso y el hecho lo dice (`sin_referente`), pero queda asentado igual (decisión 49; C-5b): en la
  historia de la tarea (`asentar_la_cadena_del_bloqueo`, en la auditoría), a la persona trabada se
  le dice que quedó asentado (que no le llega a nadie, sólo si lo pregunta) y queda un incidente
  para el administrador (`asentado.avisar_que_no_hay_a_quien`).

**Lo da por destrabado quien está trabado** (decisión 41, C-5d): a quien Leda le informó que la
tarea sigue trabada (el bloqueo viejo, `blocker.escalado_a`, o la cadena que nadie toma) la ve en
su lista (`SE_LE_INFORMO_QUE_SIGUE_TRABADA`) y lo que dice de eso ("ya está, llega mañana") queda
anotado y le llega a la persona trabada (`decir_cuando_destraba`, `_se_le_informo`); el bloqueo
sigue abierto hasta que ella diga que pudo seguir (`resolver_bloqueo` ya no deja cerrarlo a
`escalado_a`). Quien dijo que ya está se entera, como todos, cuando por fin se cierra
(`cerrar_el_tema`).

**Está trabado con algo suyo** (porción 4; decisión 6, bloqueos encadenados; conversación 35):
quien destraba puede decir que no puede porque una tarea suya está trabada (`su_tarea_trabada`).
Queda anotado con el bloqueo de esa tarea (`dicho_de_quien_destraba.espera_su_bloqueo_id`,
migración 0044), que enlaza los dos bloqueos, y a la persona trabada le llega con qué está
trabado y quién lo destraba. Lo que dice quien destraba le llega además, como un avance del
medio, a quien espera más abajo en la cadena (`encadenados.py`).

**Nunca un tema abierto sin que todos sepan cómo se cerró** (C-5c; decisión 39 del usuario,
2026-10-09, regla general; conversación 43; `cerrar_el_tema`). Cuando el tema se cierra sin quien
lo tenía abierto (a quien Leda le preguntó, o que ya habló de ese bloqueo, mientras lo último que
dijo no sea que no le corresponde; también quien dijo que ya está, porque lo da por destrabado la
persona trabada, C-5d), esa persona se entera y Leda deja de preguntarle
(`avisos.YA_NO_HACE_FALTA`, información, con el margen): se destrabó, lo destraba otra persona, la
persona trabada dice que ya lo hablaron ("no le escribas" después de que la pregunta salió,
derivado en la decisión 47; también si esa persona ya había dado un día, C-5d) o que se lo pide ella
directamente. A quien Leda
todavía no le escribió no hay nada que cerrarle: su mensaje no sale. Lo que esa persona contesta
después le llega a quien decide, la persona trabada (la ve en su lista mientras eso sea lo último
que Leda le mandó, `para_destrabar`).

**Lo que se dicen los dos, por Leda** (decisiones 47 y 48; conversación 33). Lo que una de las dos
partes dice de lo acordado le llega a la otra: quien destraba (`decir_cuando_destraba`) o la
persona trabada (`contar_lo_que_arreglaron`). Si es lo acordado (ya lo hablaron) o contesta algo
después de que el tema se cerró, llega para que la otra lo confirme: si es así, no hace falta que
haga nada; si no, que avise y Leda se lo pasa (`SE_LO_PASA_SI_CONTESTA`). Si contesta a eso (lo
corrige, o decide), llega como cierre del tema para los dos (`CIERRA_EL_TEMA`): no le pide nada
más a nadie. "Ya lo hablé" sin decir qué: Leda les pregunta a los dos qué arreglaron
(`avisos.PREGUNTA_A_QUIEN_ESTA_TRABADO`); vale lo que conteste el primero, y al otro se le cierra
la pregunta.

**"Se lo pido yo y te cuento"** (la salida de la decisión 37; `pedirselo_y_contar`): queda
anotado; Leda no le escribe a quien destraba (si el mensaje no salió, no sale; si Leda ya le
preguntaba, deja de hacerlo y se lo dice) y al día hábil siguiente le pregunta a la persona
trabada cómo le fue (`avisos.COMO_LE_FUE`, la pregunta de qué arreglaron, que la escalera de las
preguntas repite sin escalar: decisión 38).

Fuera de estas porciones (`odd/tasks/fase-c.md`, C-5): el bloqueo viejo (decisión 7).
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from ..incidentes import REFERENCIA_INBOUND_MESSAGE, registrar_incidente_y_si_se_aviso
from . import encadenados, preguntas
from .asentado import (QUEDA_ASENTADO, SIN_A_QUIEN_INFORMAR, avisar_que_no_hay_a_quien,
                       por_que_no_hay_a_quien, queda_asentado)
from .auditoria import auditar
from .avisos import (CADENA_DEL_BLOQUEO, CAMBIO_QUIEN_DESTRABA, COMO_LE_FUE, DIJO_ALGO_MAS_NUEVO,
                     LO_QUE_DIJO_QUIEN_DESTRABA, LO_QUE_DIJO_QUIEN_ESTA_TRABADO,
                     PREGUNTA_A_QUIEN_DESTRABA, PREGUNTA_A_QUIEN_ESTA_TRABADO,
                     QUIEN_MAS_PUEDE_DESTRABAR, VOLVIO_A_SER_QUIEN_DESTRABA,
                     YA_LO_CONTO_QUIEN_DESTRABA, YA_LO_CONTO_QUIEN_ESTA_TRABADO, YA_NO_HACE_FALTA,
                     YA_SE_DESTRABO, YA_SE_HABIA_DESTRABADO, Momento,
                     de_la_clave, guardar, integrante, leer_tarea, omitir, quien_destraba,
                     sigue_esperando_que_destrabe, ultimo_dicho_de_quien_destraba,
                     ultimo_quien_destraba)
from .fichas import (AVISO, LLEGA, NO_LE_LLEGO, NO_LE_VA_A_LLEGAR, PREGUNTA, YA_LE_LLEGO,
                     Contexto, _juntar, integrantes_que_coinciden, nombrar_efecto,
                     nombrar_tipo_de_pregunta, referente, tarea_hecho, vacio)
from .margen import sale_con_margen
from .tiempo import sale_el

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
# Quien destraba no tiene Leda conectada (decisión 37; C-5b): el aviso al administrador para que lo
# conecte (su incidente, por su canal) y las salidas que Leda le ofrece a la persona trabada: otra
# persona que pueda destrabarlo, o que se lo pida ella y le cuente.
ETAPA_SIN_LEDA_CONECTADA = "motor_sin_leda_conectada"
SE_LE_AVISO_AL_ADMINISTRADOR = "se_le_aviso_al_administrador"
PARA_QUE_CONECTE = "para_que_conecte"
PEDIRSELO_Y_CONTAR = "pedirselo_y_contar"
SALIDAS_SIN_LEDA_CONECTADA = ("anotar_quien_destraba", PEDIRSELO_Y_CONTAR)
# Cerrar el tema para todos (C-5c; decisión 39): cómo se cerró para quien Leda le preguntaba, y la
# lista de a quiénes se les avisa en los hechos de quien escribe.
COMO_SE_CERRO = "como_se_cerro"
DIJO_QUE_YA_LO_HABLARON = "dijo_que_ya_lo_hablaron"
SE_LO_PIDE_QUIEN_ESTA_TRABADO = "se_lo_pide_quien_esta_trabado"
QUEDO_SIN_EFECTO = "quedo_sin_efecto"
YA_NO_HACE_FALTA_QUE_DESTRABEN = "ya_no_hace_falta_que_destraben"
AVISO_A_QUIEN_DESTRABABA = "aviso_a_quien_destrababa"
# Lo que se dicen los dos, por Leda (decisiones 47 y 48): llega para confirmarlo (si no es así,
# que avise y Leda se lo pasa) o cierra el tema (y lo que dijo después de que se destrabó: avisos).
SE_LO_PASA_SI_CONTESTA = "se_lo_pasa_si_contesta"
CIERRA_EL_TEMA = "cierra_el_tema"
# La persona trabada cuenta lo que arregló, pero su bloqueo no tiene a otra persona que lo destraba.
SIN_QUIEN_DESTRABA = "sin_quien_destraba"

# La cadena llega hasta tres personas preguntadas (decisión 51 del usuario, 2026-10-09).
LIMITE_DE_LA_CADENA = 3
# La tarea trabada de otra persona que Leda le informó a quien escribe que sigue trabada (el
# bloqueo viejo o la cadena que nadie toma): lo que diga de eso queda anotado (decisión 41).
SE_LE_INFORMO_QUE_SIGUE_TRABADA = "se_le_informo_que_sigue_trabada"
# Por qué la pregunta de si se le ocurre otra persona ya no sale: ya contestó.
YA_CONTESTO = "ya_respondio"


def alcanzable(cur, membership_id: str) -> tuple[dict[str, Any] | None, str | None]:
    """La persona y, si Leda no le puede escribir por chat, por qué (constitución §7)."""
    persona = integrante(cur, membership_id)
    if persona is None or not persona["activo"]:
        return persona, INACTIVO
    if persona["telegram_user_id"] is None:
        return persona, SIN_TELEGRAM
    return persona, None


def avisar_para_que_lo_conecte(ctx: Contexto, nombre: str, para: str) -> dict[str, Any]:
    """El aviso al administrador para que conecte a esa persona, de verdad, por su canal (un
    incidente con su aviso; decisión 37): `para`, en palabras, para qué la necesita quien
    escribe. El hecho: a quién conectar y cuándo le llega al administrador, o que no le llega si
    ningún administrador es alcanzable (nunca se dice que se avisó si no salió)."""
    _id, avisado = registrar_incidente_y_si_se_aviso(
        ctx.cur, ctx.quien.workspace_id,
        f"{ctx.quien.nombre} necesita que Leda le escriba a {nombre} {para}, y {nombre} no tiene "
        f"un chat con Leda (no conectó su Telegram): Leda no le escribió. Hay que conectarlo.",
        severidad="media", etapa=ETAPA_SIN_LEDA_CONECTADA,
        referencia_tipo=REFERENCIA_INBOUND_MESSAGE if ctx.entrante_id else None,
        referencia_id=ctx.entrante_id, chat_id=ctx.chat_id, app_user_id=ctx.quien.app_user_id)
    return {PARA_QUE_CONECTE: nombre,
            LLEGA: (ctx.ahora.astimezone(ctx.calendario.zona).isoformat() if avisado
                    else NO_LE_VA_A_LLEGAR)}


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
        hecho = {"no_se_le_puede_escribir_a": {"a": destraba["nombre"], "motivo": motivo}}
        if motivo == SIN_TELEGRAM:
            hecho[SE_LE_AVISO_AL_ADMINISTRADOR] = avisar_para_que_lo_conecte(
                ctx, destraba["nombre"], f"para destrabar la tarea «{tarea['titulo']}»")
        return hecho
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


def al_destrabarse(ctx: Contexto, task_id: str, blocker_id: str | None = None,
                   como: str = YA_SE_DESTRABO) -> dict[str, Any]:
    """La tarea se destrabó: lo que se le preguntaba a quien la destraba ya no espera nada (sus
    avisos guardados no salen: `avisos.YA_SE_DESTRABO`), y a quien tenía el tema abierto se le
    avisa cómo se cerró (decisión 39; `como`: se destrabó, o el bloqueo quedó sin efecto por una
    corrección). Los hechos para quien escribe."""
    hecho = {}
    if blocker_id is not None:
        hecho = cerrar_el_tema(ctx, task_id, blocker_id, como)
    preguntas.cerrar_las_de_otras_personas(
        ctx, preguntas.CUANDO_SE_DESTRABA, task_id, "sin_efecto",
        {"tarea": task_id, "ya_se_destrabo": True})
    return hecho


# --- Cerrar el tema para todos (C-5c; decisión 39) ----------------------------------------------

def cerrar_el_tema(ctx: Contexto, task_id: str, blocker_id: str, como: str, *,
                   salvo: tuple[str, ...] = (), solo: set[str] | None = None) -> dict[str, Any]:
    """A cada persona que tenía abierto el tema de este bloqueo (`_con_el_tema_abierto`), salvo
    quien escribe, la persona trabada y `salvo` (y sólo `solo`, si se dice), Leda deja de
    preguntarle y le avisa cómo se cerró (`como`), terminado el margen para corregir. Los hechos
    para quien escribe: a quiénes y cuándo se enteran."""
    cur = ctx.cur
    cur.execute("""select b.causa, t.titulo, t.responsable_membership_id, i.nombre as responsable
                     from blocker b join task t on t.id = b.task_id
                     join integrante i on i.membership_id = t.responsable_membership_id
                    where b.id = %s""", (str(blocker_id),))
    bloqueo = cur.fetchone()
    if bloqueo is None:
        return {}
    fuera = {str(bloqueo["responsable_membership_id"]), ctx.quien.membership_id,
             *map(str, salvo)}
    avisados: list[dict[str, Any]] = []
    for tiene in _con_el_tema_abierto(cur, task_id, str(blocker_id)):
        persona = tiene["persona"]
        if persona in fuera or (solo is not None and persona not in solo):
            continue
        _ya_no_le_pregunta(ctx, persona, task_id)
        quien, motivo = alcanzable(cur, persona)
        if motivo is not None:
            continue                    # no se le puede escribir: nada que prometer
        sale = sale_con_margen(cur, ctx.calendario, ctx.quien.workspace_id, ctx.ahora)
        aviso_id, nuevo = guardar(
            cur, ctx.quien.workspace_id, YA_NO_HACE_FALTA, task_id=task_id, destinatario=persona,
            hechos={"aviso": YA_NO_HACE_FALTA, "necesita_respuesta": False,
                    "tarea": bloqueo["titulo"], "responsable": bloqueo["responsable"],
                    "causa": bloqueo["causa"], COMO_SE_CERRO: como,
                    **({"habia_dicho": tiene["habia_dicho"]} if tiene["habia_dicho"] else {})},
            programado_para=sale,
            # La persona va en la clave: sobre una misma fila pueden haber hablado dos (quien la
            # destrababa y a quien se le informó que seguía trabada, decisión 41).
            clave=f"motor:{YA_NO_HACE_FALTA}:{task_id}:u{tiene['fila']}:{como}:m{persona}",
            ahora=ctx.ahora)
        if not nuevo:
            continue
        ctx.avisos_guardados.append(aviso_id)
        avisado: dict[str, Any] = {AVISO_A_QUIEN_DESTRABABA: {"a": quien["nombre"],
                                                              LLEGA: sale.isoformat()}}
        nombrar_efecto(avisado, AVISO_A_QUIEN_DESTRABABA, AVISO, aviso_id)
        avisados.append(avisado)
    return {YA_NO_HACE_FALTA_QUE_DESTRABEN: avisados} if avisados else {}


def _con_el_tema_abierto(cur, task_id: str, blocker_id: str) -> list[dict[str, Any]]:
    """Quiénes tienen abierto el tema de un bloqueo: a quien Leda le preguntó por él, o que ya
    habló de él (también a quien se le informó que seguía trabada y dijo algo, decisión 41),
    mientras lo último que dijo no sea que no le corresponde (se fue de la cadena), y a quien
    todavía no se le avisó cómo se cerró desde la última vez que estuvo en el tema. Quien dijo
    que ya está también: el bloqueo lo da por destrabado la persona trabada (decisión 41), así
    que se entera de cuándo se cerró de verdad (derivado de la regla 39 en la C-5d). Cada una con la
    fila que la nombró por última vez (o sobre la que habló) y lo que había dicho."""
    cur.execute("""select u.id, u.destraba_membership_id from blocker_unblocker u
                    where u.blocker_id = %s and u.destraba_membership_id is not null
                    order by u.at, u.id""", (blocker_id,))
    filas: dict[str, list[str]] = {}
    for f in cur.fetchall():
        filas.setdefault(str(f["destraba_membership_id"]), []).append(str(f["id"]))
    cur.execute("""select d.dicho_por_membership_id, u.id from dicho_de_quien_destraba d
                     join blocker_unblocker u on u.id = d.blocker_unblocker_id
                    where u.blocker_id = %s order by d.at, d.id""", (blocker_id,))
    hablaron: dict[str, list[str]] = {}
    for f in cur.fetchall():
        persona = str(f["dicho_por_membership_id"])
        if persona not in filas and str(f["id"]) not in hablaron.get(persona, []):
            hablaron.setdefault(persona, []).append(str(f["id"]))
    filas.update(hablaron)
    abiertos = []
    for persona, ids in filas.items():
        cur.execute("""select max(abierta_en) as en from conversation_question
                        where membership_id = %s and tipo = %s and task_id = %s
                          and jugada ->> 'destraba_id' = any(%s)""",
                    (persona, preguntas.CUANDO_SE_DESTRABA, task_id, ids))
        preguntado = cur.fetchone()["en"]
        cur.execute("""select d.* from dicho_de_quien_destraba d
                         join blocker_unblocker u on u.id = d.blocker_unblocker_id
                        where u.blocker_id = %s and d.dicho_por_membership_id = %s
                        order by d.at desc, d.id desc limit 1""", (blocker_id, persona))
        ultimo = cur.fetchone()
        if preguntado is None and ultimo is None:
            continue                    # nunca le llegó nada ni habló: no hay nada que cerrarle
        if ultimo is not None and ultimo["no_le_corresponde"]:
            continue
        desde = max(x for x in (preguntado, ultimo["at"] if ultimo else None) if x is not None)
        cur.execute("""select 1 from scheduled_notice
                        where tipo = %s and task_id = %s and destinatario_membership_id = %s
                          and estado <> 'omitido' and creado_en >= %s
                          and substr(split_part(dedupe_key, ':', 4), 2) = any(%s)""",
                    (YA_NO_HACE_FALTA, task_id, persona, desde, ids))
        if cur.fetchone() is not None:
            continue                    # ya se le cerró, y no volvió al tema
        habia = {}
        if ultimo is not None:
            if ultimo["ya_esta"]:
                habia["ya_esta"] = True
            if ultimo["para_cuando"] is not None:
                habia["para_cuando"] = ultimo["para_cuando"].isoformat()
            if ultimo["lo_que_dice"]:
                habia["lo_que_dice"] = ultimo["lo_que_dice"]
        abiertos.append({"persona": persona, "fila": ids[-1], "habia_dicho": habia})
    return abiertos


def _ya_no_le_pregunta(ctx: Contexto, persona: str, task_id: str) -> None:
    """Lo que Leda le preguntaba a esa persona sobre la tarea de otra deja de esperar: su
    pregunta y su espera se cierran."""
    cur = ctx.cur
    cur.execute("""update conversation_question
                      set cerrada_en = %s, cierre = 'sin_efecto', cierre_detalle = %s
                    where membership_id = %s and task_id = %s and tipo = %s
                      and cerrada_en is null
                returning id""",
                (ctx.ahora, preguntas.json_de({"tarea": task_id, "ya_no_hace_falta": True}),
                 persona, task_id, preguntas.CUANDO_SE_DESTRABA))
    cerradas = [str(f["id"]) for f in cur.fetchall()]
    cur.execute("""update conversation_state set pregunta_abierta_id = null, actualizado_en = %s
                    where membership_id = %s and pregunta_abierta_id = any(%s::uuid[])""",
                (ctx.ahora, persona, cerradas))
    cur.execute("""update pending_reply set satisfecho_en = %s
                    where membership_id = %s and task_id = %s and tipo = %s
                      and satisfecho_en is null""",
                (ctx.ahora, persona, task_id, preguntas.CUANDO_SE_DESTRABA))


def _le_pregunta_todavia(cur, persona: str, task_id: str) -> bool:
    """Si Leda le sigue preguntando a esa persona por la tarea de otra (su pregunta sin cerrar)."""
    cur.execute("""select 1 from conversation_question
                    where membership_id = %s and task_id = %s and tipo = %s
                      and cerrada_en is null""",
                (persona, task_id, preguntas.CUANDO_SE_DESTRABA))
    return cur.fetchone() is not None


def vigencia_de_ya_no_hace_falta(m: Momento, aviso) -> tuple[str | None, dict[str, Any]]:
    """Que ya no hace falta sale salvo que deje de ser cierto: la persona trabada la volvió a
    nombrar, o esa persona ya habló después de que se guardó (ya contestó)."""
    fila = quien_destraba(m.cur, de_la_clave(aviso))
    if fila is None:
        return "tarea_inexistente", {}
    como = aviso["dedupe_key"].split(":")[4]
    persona = str(aviso["destinatario_membership_id"])
    if como == CAMBIO_QUIEN_DESTRABA:
        ultimo = ultimo_quien_destraba(m.cur, fila["blocker_id"])
        if (fila["resuelto_en"] is None and ultimo is not None
                and str(ultimo["destraba_membership_id"]) == persona):
            return VOLVIO_A_SER_QUIEN_DESTRABA, {}
    elif como in (DIJO_QUE_YA_LO_HABLARON, SE_LO_PIDE_QUIEN_ESTA_TRABADO):
        m.cur.execute("""select 1 from dicho_de_quien_destraba d
                           join blocker_unblocker u on u.id = d.blocker_unblocker_id
                          where u.blocker_id = %s and d.dicho_por_membership_id = %s
                            and d.at > %s""", (fila["blocker_id"], persona, aviso["creado_en"]))
        if m.cur.fetchone() is not None:
            return "ya_respondio", {}
    return None, dict(aviso["hechos"])


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
        vistas.setdefault(str(t["id"]), {**t, "espera_que_la_destrabe": True})
    # La que Leda le informó que sigue trabada (el bloqueo viejo o la cadena que nadie toma): lo
    # que diga de eso queda anotado y le llega a la persona trabada, sin cerrarlo (decisión 41).
    cur.execute(
        """select t.id, t.titulo, t.estado::text estado, t.fecha_objetivo,
                  i.nombre as responsable, b.causa
             from blocker b
             join task t on t.id = b.task_id
             join integrante i on i.membership_id = t.responsable_membership_id
            where b.resuelto_en is null and t.responsable_membership_id <> %s
              and t.estado not in ('terminada', 'cancelada')
              and (b.escalado_a = %s
                   or exists (select 1 from scheduled_notice a
                                join dicho_de_quien_destraba d
                                  on d.id::text = substr(split_part(a.dedupe_key, ':', 4), 2)
                                join blocker_unblocker u on u.id = d.blocker_unblocker_id
                               where a.tipo = %s and a.estado = 'enviado'
                                 and a.destinatario_membership_id = %s
                                 and u.blocker_id = b.id))
            order by t.fecha_objetivo nulls last, t.titulo, b.abierto_en""",
        (membership_id, membership_id, CADENA_DEL_BLOQUEO, membership_id))
    for t in cur.fetchall():
        vistas.setdefault(str(t["id"]), {**t, SE_LE_INFORMO_QUE_SIGUE_TRABADA: True})
    # La que ya no hace falta que destrabe, mientras sea lo último que Leda le mandó de ella: lo
    # que conteste a eso le llega a quien decide (decisión 39).
    tema = tema_del_ultimo_aviso(cur, membership_id)
    if tema is not None and tema["task_id"] not in vistas:
        cur.execute("""select t.id, t.titulo, t.estado::text estado, t.fecha_objetivo,
                              i.nombre as responsable, b.causa
                         from blocker_unblocker u
                         join blocker b on b.id = u.blocker_id
                         join task t on t.id = b.task_id
                         join integrante i on i.membership_id = t.responsable_membership_id
                        where u.id = %s and t.estado not in ('terminada', 'cancelada')""",
                    (tema["fila"],))
        fila = cur.fetchone()
        if fila is not None:
            vistas[tema["task_id"]] = {**fila, "ya_no_hace_falta_que_la_destrabe": True}
    return tuple(
        {"alias": f"T{i}", "id": str(t["id"]), "titulo": t["titulo"], "estado": t["estado"],
         "fecha_objetivo": t["fecha_objetivo"].isoformat() if t["fecha_objetivo"] else None,
         **{k: True for k in ("espera_que_la_destrabe", "ya_no_hace_falta_que_la_destrabe",
                              SE_LE_INFORMO_QUE_SIGUE_TRABADA)
            if t.get(k)},
         "responsable": t["responsable"], "causa": t["causa"]}
        for i, t in enumerate(vistas.values(), desde + 1))


def tema_del_ultimo_aviso(cur, membership_id: str) -> dict[str, str] | None:
    """El tema de un bloqueo que Leda le cerró a esa persona, si es lo último que le mandó: que ya
    no hace falta (`avisos.YA_NO_HACE_FALTA`) o lo que le pasó de la persona trabada para que lo
    confirme (`avisos.LO_QUE_DIJO_QUIEN_ESTA_TRABADO`, sin cerrar el tema). La tarea y la fila que
    la nombraba a ella."""
    cur.execute("""select a.tipo, a.dedupe_key, a.task_id, a.hechos
                     from conversation_state s
                     join scheduled_notice a on a.id = s.ultimo_aviso_id
                    where s.membership_id = %s and a.tipo = any(%s)""",
                (membership_id, [YA_NO_HACE_FALTA, LO_QUE_DIJO_QUIEN_ESTA_TRABADO]))
    aviso = cur.fetchone()
    if aviso is None:
        return None
    if aviso["tipo"] == YA_NO_HACE_FALTA:
        fila = de_la_clave(aviso)
    else:
        if not (aviso["hechos"] or {}).get(SE_LO_PASA_SI_CONTESTA):
            return None
        cur.execute("select blocker_unblocker_id from dicho_de_quien_destraba where id = %s",
                    (de_la_clave(aviso),))
        dicho = cur.fetchone()
        if dicho is None:
            return None
        fila = str(dicho["blocker_unblocker_id"])
    cur.execute("select destraba_membership_id from blocker_unblocker where id = %s", (fila,))
    nombrada = cur.fetchone()
    if nombrada is None or str(nombrada["destraba_membership_id"]) != str(membership_id):
        return None
    return {"task_id": str(aviso["task_id"]), "fila": fila}


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
    # Lo que contesta después de que Leda le dijo que ya no hace falta (decisión 39): queda
    # anotado sobre la fila que la nombraba y le llega a quien decide, la persona trabada.
    ya_no_hacia_falta = False
    if destraba is None:
        destraba = _lo_destrababa(ctx, tarea["id"])
        ya_no_hacia_falta = destraba is not None
    if destraba is None:
        destraba = _se_le_informo(ctx, tarea)
    if destraba is None:
        return {"resultado": "no_se_puede", "motivo": NO_LE_TOCA_DESTRABARLA,
                "tarea": tarea_hecho(tarea)}
    # Está trabado con algo suyo (porción 4): el bloqueo de esa tarea enlaza los dos.
    su_bloqueo = None
    if not vacio(datos.get("su_tarea_trabada")):
        suya = ctx.suya(str(datos["su_tarea_trabada"]).strip())
        if suya is None:
            return {"resultado": "no_se_puede", "motivo": "tarea_desconocida",
                    "tarea": tarea_hecho(tarea)}
        su_bloqueo = _su_bloqueo(ctx, suya)
        if su_bloqueo is None:
            return {"resultado": "no_se_puede", "motivo": encadenados.SU_TAREA_NO_ESTA_TRABADA,
                    "tarea": tarea_hecho(tarea), "su_tarea_trabada": tarea_hecho(suya)}
    # "Ya lo hablé con él" (porción 2): lo dice ahora o lo dijo antes, en la misma pregunta.
    pregunta = _su_pregunta(ctx, tarea["id"])
    jugada = dict((pregunta or {}).get("jugada") or {})
    lo_que_dice = _sus_palabras(datos, jugada)
    ya_lo_hablaron = (datos.get("ya_lo_hablaron") is True
                      or (jugada.get("datos") or {}).get(YA_LO_HABLARON) is True)
    if (ya_lo_hablaron and para_cuando is None and not ya_esta and su_bloqueo is None
            and not ya_no_hacia_falta and not jugada.get(PREGUNTO_QUE_ARREGLARON)):
        # Lo que queda asentado es lo que arreglaron y para cuándo: se pregunta una vez. Lo que
        # dijo queda en su pregunta y se anota con la respuesta. A la persona trabada, lo mismo:
        # vale lo que conteste el primero (decisión 48).
        hecho = _preguntar(ctx, tarea, destraba, pregunta,
                           {YA_LO_HABLARON: True,
                            **({"lo_que_dice": lo_que_dice} if lo_que_dice else {})},
                           PREGUNTO_QUE_ARREGLARON,
                           {"resultado": "falta_dato",
                            "falta": ["lo_que_arreglaron", "para_cuando"],
                            "tarea": tarea_hecho(tarea), YA_LO_HABLARON: True})
        _juntar(hecho, _preguntarle_a_quien_esta_trabado(ctx, tarea, destraba))
        return hecho
    if (para_cuando is None and not ya_esta and su_bloqueo is None
            and vacio(datos.get("lo_que_dice"))):
        return {"resultado": "falta_dato", "falta": ["para_cuando"],
                "puede_ser": ["para_cuando", "ya_esta", "lo_que_dice"],
                "tarea": tarea_hecho(tarea)}
    dice = {k: v for k, v in (("para_cuando", para_cuando.isoformat() if para_cuando else None),
                              ("ya_esta", ya_esta or None), ("lo_que_dice", lo_que_dice),
                              (YA_LO_HABLARON, ya_lo_hablaron or None),
                              ("su_tarea_trabada", su_bloqueo and su_bloqueo["dice"]))
            if v is not None}
    # Si contesta lo que Leda le pasó de la persona trabada, cierra el tema (decisiones 47 y 39):
    # se mira antes de anotar, porque lo anotado ya sería "algo que dijo después".
    cierra = _contesta_lo_que_se_le_paso(ctx.cur, destraba["blocker_id"],
                                         ctx.quien.membership_id)
    dicho_id = _anotar_lo_que_dice(ctx, tarea, destraba, dice, para_cuando=para_cuando,
                                   ya_esta=ya_esta, lo_que_dice=lo_que_dice,
                                   espera_su_bloqueo=su_bloqueo and su_bloqueo["id"])
    hecho: dict[str, Any] = {"resultado": "anotado", "tarea": tarea_hecho(tarea),
                             "dice_quien_destraba": dice}
    como_llega = _como_llega(cierra, acordado=ya_lo_hablaron or ya_no_hacia_falta)
    if destraba.get("resuelto_en") is not None:
        como_llega[YA_SE_HABIA_DESTRABADO] = True
    if cierra:
        hecho[CIERRA_EL_TEMA] = True
    _juntar(hecho, _avisar_a_quien_esta_trabado(ctx, tarea, destraba, dicho_id, dice,
                                                como_llega))
    if not ya_no_hacia_falta:
        _juntar(hecho, encadenados.dijo_quien_destraba(ctx, tarea["id"], dicho_id, dice))
    return hecho


def _como_llega(cierra: bool, *, acordado: bool) -> dict[str, Any]:
    """Cómo le llega a la otra persona lo que dice una de las dos (decisiones 47 y 39): si
    contesta lo que Leda le pasó, cierra el tema; si es lo acordado entre ellos (o lo que contesta
    después de que el tema se cerró), para que lo confirme, y si no es así, que avise y Leda se
    lo pasa; si no, información."""
    if cierra:
        return {CIERRA_EL_TEMA: True}
    return {SE_LO_PASA_SI_CONTESTA: True} if acordado else {}


def _contesta_lo_que_se_le_paso(cur, blocker_id, persona: str) -> bool:
    """Si lo que dice ahora esa persona contesta lo último que Leda le pasó de la otra para que lo
    confirme (`SE_LO_PASA_SI_CONTESTA`), sin que haya dicho otra cosa desde que le llegó."""
    cur.execute("""select a.hechos, a.resuelto_en from scheduled_notice a
                     join dicho_de_quien_destraba d
                       on d.id::text = substr(split_part(a.dedupe_key, ':', 4), 2)
                     join blocker_unblocker u on u.id = d.blocker_unblocker_id
                    where a.tipo = any(%s) and a.destinatario_membership_id = %s
                      and a.estado = 'enviado' and u.blocker_id = %s
                    order by a.resuelto_en desc, a.id desc limit 1""",
                ([LO_QUE_DIJO_QUIEN_DESTRABA, LO_QUE_DIJO_QUIEN_ESTA_TRABADO], persona,
                 str(blocker_id)))
    ultimo = cur.fetchone()
    if ultimo is None or not (ultimo["hechos"] or {}).get(SE_LO_PASA_SI_CONTESTA):
        return False
    cur.execute("""select 1 from dicho_de_quien_destraba d
                     join blocker_unblocker u on u.id = d.blocker_unblocker_id
                    where u.blocker_id = %s and d.dicho_por_membership_id = %s
                      and d.at > %s limit 1""", (str(blocker_id), persona, ultimo["resuelto_en"]))
    return cur.fetchone() is None


def _se_le_informo(ctx: Contexto, tarea: dict[str, Any]) -> dict[str, Any] | None:
    """A quien Leda le informó que la tarea sigue trabada (decisión 41): lo que dice se anota
    sobre la fila de quién la destraba ahora, dicho por esa persona; si nadie dijo nunca quién la
    destraba, sobre una fila nueva, dicha por ella misma, que dice que la destraba ella. Nunca
    cierra el bloqueo: lo da por destrabado la persona trabada. `None` si no se le informó."""
    vista = next((t for t in ctx.para_destrabar if t["id"] == tarea["id"]), None)
    if vista is None or not vista.get(SE_LE_INFORMO_QUE_SIGUE_TRABADA):
        return None
    cur = ctx.cur
    cur.execute("""select id from blocker where task_id = %s and resuelto_en is null
                    order by abierto_en desc, id desc limit 1""", (tarea["id"],))
    bloqueo = cur.fetchone()
    if bloqueo is None:
        return None
    ultimo = ultimo_quien_destraba(cur, bloqueo["id"])
    if ultimo is not None:
        return _la_fila(cur, str(ultimo["id"]))
    yo = {"membership_id": ctx.quien.membership_id, "nombre": ctx.quien.nombre}
    return _la_fila(cur, _anotar_quien_destraba(ctx, tarea, {"blocker_id": str(bloqueo["id"])},
                                                yo, None, False))


def _lo_destrababa(ctx: Contexto, task_id: str) -> dict[str, Any] | None:
    """La fila que nombraba a quien escribe en el tema que Leda le cerró, si es lo último que le
    mandó de esa tarea (`tema_del_ultimo_aviso`), con el mismo forma que `_lo_destraba`."""
    tema = tema_del_ultimo_aviso(ctx.cur, ctx.quien.membership_id)
    if tema is None or tema["task_id"] != str(task_id):
        return None
    return _la_fila(ctx.cur, tema["fila"])


def _la_fila(cur, fila_id: str) -> dict[str, Any] | None:
    """Una fila de quién destraba, con su bloqueo, la tarea y quién la tiene."""
    cur.execute(
        """select u.id, u.blocker_id, u.dicho_por_membership_id, u.destraba_membership_id,
                  u.destraba_externo, b.causa, b.resuelto_en, t.area_id,
                  t.responsable_membership_id, i.nombre as responsable
             from blocker_unblocker u
             join blocker b on b.id = u.blocker_id
             join task t on t.id = b.task_id
             join integrante i on i.membership_id = t.responsable_membership_id
            where u.id = %s""", (str(fila_id),))
    return cur.fetchone()


def _preguntarle_a_quien_esta_trabado(ctx: Contexto, tarea: dict[str, Any],
                                      destraba: dict[str, Any]) -> dict[str, Any]:
    """"Ya lo hablé" sin decir qué (decisión 48): Leda le pregunta lo mismo a la persona trabada,
    terminado el margen para corregir (`avisos.PREGUNTA_A_QUIEN_ESTA_TRABADO`, que al salir abre
    su pregunta de qué arreglaron). Los hechos para quien escribe: a quién y cuándo."""
    cur = ctx.cur
    responsable = str(destraba["responsable_membership_id"])
    quien, motivo = alcanzable(cur, responsable)
    if motivo is not None:
        return {}
    clave = f"motor:{PREGUNTA_A_QUIEN_ESTA_TRABADO}:{tarea['id']}:u{destraba['id']}"
    sale = sale_con_margen(cur, ctx.calendario, ctx.quien.workspace_id, ctx.ahora)
    aviso_id, nuevo = guardar(
        cur, ctx.quien.workspace_id, PREGUNTA_A_QUIEN_ESTA_TRABADO, task_id=tarea["id"],
        destinatario=responsable,
        hechos={"aviso": PREGUNTA_A_QUIEN_ESTA_TRABADO, "necesita_respuesta": True,
                "pregunta": preguntas.QUE_ARREGLARON, "tarea": tarea["titulo"],
                "quien_destraba": ctx.quien.nombre, "causa": destraba["causa"],
                YA_LO_HABLARON: True},
        programado_para=sale, clave=clave, ahora=ctx.ahora)
    if not nuevo:
        return {}
    ctx.avisos_guardados.append(aviso_id)
    hecho: dict[str, Any] = {"le_pregunta_tambien_a": {"a": quien["nombre"],
                                                       LLEGA: sale.isoformat()}}
    nombrar_efecto(hecho, "le_pregunta_tambien_a", AVISO, aviso_id)
    return hecho


def _ya_no_se_le_pregunta_a_quien_esta_trabado(ctx: Contexto, task_id: str,
                                               motivo: str) -> None:
    """Lo que se le preguntaba a la persona trabada de lo que arregló ya tiene respuesta (vale lo
    que contestó el primero, decisión 48): su pregunta y su espera se cierran, y la que todavía
    no le llegó no sale (con su motivo)."""
    cur = ctx.cur
    cur.execute("""update conversation_question
                      set cerrada_en = %s, cierre = 'sin_efecto', cierre_detalle = %s
                    where task_id = %s and tipo = %s and cerrada_en is null
                returning id, membership_id""",
                (ctx.ahora, preguntas.json_de({"tarea": task_id, motivo: True}), task_id,
                 preguntas.QUE_ARREGLARON))
    for fila in cur.fetchall():
        cur.execute("""update conversation_state set pregunta_abierta_id = null,
                                                     actualizado_en = %s
                        where membership_id = %s and pregunta_abierta_id = %s""",
                    (ctx.ahora, fila["membership_id"], fila["id"]))
    cur.execute("""update pending_reply set satisfecho_en = %s
                    where task_id = %s and tipo = %s and satisfecho_en is null""",
                (ctx.ahora, task_id, preguntas.QUE_ARREGLARON))
    cur.execute("""select id from scheduled_notice
                    where task_id = %s and tipo = any(%s) and estado = 'guardado'""",
                (task_id, [PREGUNTA_A_QUIEN_ESTA_TRABADO, COMO_LE_FUE]))
    for aviso in cur.fetchall():
        omitir(cur, str(aviso["id"]), motivo, ctx.ahora)


def _su_bloqueo(ctx: Contexto, suya: dict[str, Any]) -> dict[str, Any] | None:
    """El bloqueo abierto de una tarea de quien escribe, con lo que le llega de él a la persona
    trabada (la tarea, su causa y quién lo destraba); `None` si no está trabada."""
    ctx.cur.execute("""select id, causa from blocker where task_id = %s and resuelto_en is null
                        order by abierto_en desc, id desc limit 1""", (suya["id"],))
    bloqueo = ctx.cur.fetchone()
    if bloqueo is None:
        return None
    lo_destraba = encadenados.quien_lo_destraba(ctx.cur, bloqueo["id"])
    return {"id": str(bloqueo["id"]),
            "dice": {"tarea": suya["titulo"], "causa": bloqueo["causa"],
                     **({"lo_destraba": lo_destraba} if lo_destraba else {})}}


def _anotar_lo_que_dice(ctx: Contexto, tarea: dict[str, Any], destraba: dict[str, Any],
                        dice: dict[str, Any], *, para_cuando: date | None = None,
                        ya_esta: bool = False, lo_que_dice: str | None = None,
                        no_le_corresponde: bool = False,
                        espera_su_bloqueo: str | None = None) -> str:
    """Lo que dice quien destraba, como un hecho del bloqueo sobre la fila que lo nombró
    (`dicho_de_quien_destraba`, sólo se agrega), atribuido y auditado; su pregunta y su espera
    se cierran. El id de lo anotado."""
    cur = ctx.cur
    cur.execute(
        """insert into dicho_de_quien_destraba (workspace_id, blocker_unblocker_id,
                                                dicho_por_membership_id, para_cuando, ya_esta,
                                                lo_que_dice, no_le_corresponde,
                                                espera_su_bloqueo_id, at)
           values (%s, %s, %s, %s, %s, %s, %s, %s, %s) returning id""",
        (ctx.quien.workspace_id, destraba["id"], ctx.quien.membership_id, para_cuando, ya_esta,
         lo_que_dice, no_le_corresponde, espera_su_bloqueo, ctx.ahora))
    dicho_id = str(cur.fetchone()["id"])
    auditar(cur, accion=("anotar_que_no_le_toca" if no_le_corresponde
                         else "anotar_lo_que_dice_quien_destraba"),
            workspace_id=ctx.quien.workspace_id, sujeto_tipo="blocker",
            sujeto_id=destraba["blocker_id"], quien=ctx.quien,
            detalle={"dicho_id": dicho_id, "blocker_unblocker_id": str(destraba["id"]),
                     "task_id": tarea["id"], **dice, "at": ctx.ahora.isoformat(),
                     "inbound_message_id": ctx.entrante_id})
    _contestada(ctx, tarea["id"])
    # Vale lo que contestó el primero (decisión 48): lo que se le preguntaba a la persona trabada
    # de lo que arreglaron ya no espera nada.
    _ya_no_se_le_pregunta_a_quien_esta_trabado(ctx, tarea["id"], YA_LO_CONTO_QUIEN_DESTRABA)
    return dicho_id


def _avisar_a_quien_esta_trabado(ctx: Contexto, tarea: dict[str, Any], destraba: dict[str, Any],
                                 dicho_id: str, dice: dict[str, Any],
                                 mas: dict[str, Any] | None = None) -> dict[str, Any]:
    """Lo que dijo quien destraba le llega a la persona trabada como información, terminado el
    margen para corregir (`avisos.LO_QUE_DIJO_QUIEN_DESTRABA`), con lo que pasa después
    (`mas`: a quién le pregunta Leda ahora, o que quedó asentado). Lo que dijo antes y todavía no le
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
    # Hasta tres personas preguntadas (decisión 51): mientras haya lugar en la cadena, quien no
    # dice de quién es recibe una pregunta (quién se encarga) y, si vuelve a no decirlo, es que no
    # sabe; a quien nombra, Leda le escribe. Con las tres ya preguntadas, se corta.
    trabado = str(destraba["responsable_membership_id"])
    hay_lugar = len(_nombrados(_vuelta(cur, destraba["blocker_id"], trabado), trabado)) \
        < LIMITE_DE_LA_CADENA
    nombra = integrante is not None or externo is not None
    if hay_lugar and not nombra and not no_sabe:
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
    nueva = None
    if nombra or no_sabe:
        # A quién le toca, según quien no lo toma: otra fila de quién destraba, dicha por él.
        nueva = _anotar_quien_destraba(ctx, tarea, destraba, integrante, externo, no_sabe)
    hecho: dict[str, Any] = {"resultado": "anotado", "tarea": tarea_hecho(tarea),
                             "dice_quien_destraba": dice}
    bloqueo = {"causa": destraba["causa"]}
    sigue: dict[str, Any] = {}
    if hay_lugar and integrante is not None and str(integrante["membership_id"]) != trabado:
        # Leda sigue con esa persona, como siguió con la primera.
        sigue = preguntarle(ctx, {"id": tarea["id"], "titulo": tarea["titulo"]}, bloqueo,
                            nueva, integrante, responsable=destraba["responsable"],
                            nombrado_por=ctx.quien.nombre)
        _juntar(hecho, sigue)
    if "se_le_pregunta_a" in sigue:
        mas = {"se_le_pregunta_a": {"a": sigue["se_le_pregunta_a"]["a"]}}
    elif hay_lugar and no_sabe and nueva is not None and alcanzable(cur, trabado)[1] is None:
        # "Ni idea", con lugar en la cadena: antes de asentarlo, Leda le pregunta a la persona
        # trabada si se le ocurre otra persona (decisión 49). Lo que dijo va en esa pregunta.
        _juntar(hecho, _preguntarle_si_hay_otra(ctx, tarea, destraba, nueva, dice))
        _juntar(hecho, encadenados.dijo_quien_destraba(ctx, tarea["id"], dicho_id, dice))
        return hecho
    else:
        # La cadena se corta: a quien decide quién lo resuelve, con la cadena entera, como
        # información. También si a quien nombró no se le puede escribir: Leda no puede seguir
        # con esa persona, y la cadena no queda en silencio (revisión del 2026-10-09).
        sin_chat = sigue.get("no_se_le_puede_escribir_a")
        informe = _informar_la_cadena(ctx, tarea, destraba, dicho_id, sin_chat=sin_chat)
        _juntar(hecho, informe)
        mas = {**({"no_se_le_puede_escribir_a": sin_chat} if sin_chat else {}),
               **({SE_LE_AVISO_AL_ADMINISTRADOR: sigue[SE_LE_AVISO_AL_ADMINISTRADOR]}
                  if SE_LE_AVISO_AL_ADMINISTRADOR in sigue else {}),
               **_lo_que_queda_para_quien_esta_trabado(ctx, informe["aviso_de_la_cadena"])}
    _juntar(hecho, _avisar_a_quien_esta_trabado(ctx, tarea, destraba, dicho_id, dice, mas))
    # Quien espera esta tarea, más abajo en una cadena de bloqueos, se entera (porción 4).
    _juntar(hecho, encadenados.dijo_quien_destraba(ctx, tarea["id"], dicho_id, dice))
    return hecho


def _preguntarle_si_hay_otra(ctx: Contexto, tarea: dict[str, Any], destraba: dict[str, Any],
                             fila_id: str, dice: dict[str, Any]) -> dict[str, Any]:
    """Antes de asentar un "ni idea" (decisión 49): a la persona trabada, terminado el margen para
    corregir, lo que dijo quien no lo toma y si se le ocurre otra persona que pueda destrabarlo
    (`avisos.QUIEN_MAS_PUEDE_DESTRABAR`, que al salir abre su pregunta de quién lo destraba). La
    clave nombra la fila del "ni idea": lo que conteste sigue la misma cadena (`_vuelta`). Los
    hechos para quien escribe: a quién y cuándo se entera."""
    cur = ctx.cur
    trabado = str(destraba["responsable_membership_id"])
    quien = integrante(cur, trabado)
    sale = sale_con_margen(cur, ctx.calendario, ctx.quien.workspace_id, ctx.ahora)
    aviso_id, _ = guardar(
        cur, ctx.quien.workspace_id, QUIEN_MAS_PUEDE_DESTRABAR, task_id=tarea["id"],
        destinatario=trabado,
        hechos={"aviso": QUIEN_MAS_PUEDE_DESTRABAR, "necesita_respuesta": True,
                "pregunta": preguntas.QUIEN_DESTRABA, "tarea": tarea["titulo"],
                "causa": destraba["causa"], "quien_destraba": ctx.quien.nombre,
                "dice_quien_destraba": dice},
        programado_para=sale, clave=f"motor:{QUIEN_MAS_PUEDE_DESTRABAR}:{tarea['id']}:u{fila_id}",
        ahora=ctx.ahora)
    ctx.avisos_guardados.append(aviso_id)
    hecho: dict[str, Any] = {"aviso_a_quien_esta_trabado": {"a": quien["nombre"],
                                                            LLEGA: sale.isoformat()}}
    nombrar_efecto(hecho, "aviso_a_quien_esta_trabado", AVISO, aviso_id)
    return hecho


def vigencia_de_quien_mas(m: Momento, aviso) -> tuple[str | None, dict[str, Any]]:
    """La pregunta de si se le ocurre otra persona sale mientras la tarea siga trabada con el
    mismo responsable y el "ni idea" sea lo último que se dijo de quién la destraba: si la persona
    trabada ya contestó (o nombró a alguien por su cuenta), ya no hace falta."""
    tarea = leer_tarea(m.cur, aviso["task_id"])
    if tarea is None:
        return "tarea_inexistente", {}
    if tarea["estado"] in ("terminada", "cancelada"):
        return "tarea_cerrada", {}
    if str(tarea["responsable_membership_id"]) != str(aviso["destinatario_membership_id"]):
        return "cambio_el_responsable", {}
    fila = quien_destraba(m.cur, de_la_clave(aviso))
    if fila is None:
        return "tarea_inexistente", {}
    if fila["resuelto_en"] is not None:
        return YA_SE_DESTRABO, {}
    ultimo = ultimo_quien_destraba(m.cur, fila["blocker_id"])
    if ultimo is None or str(ultimo["id"]) != str(fila["id"]):
        return YA_CONTESTO, {}
    return None, dict(aviso["hechos"])


def sin_otra_persona(ctx: Contexto, tarea: dict[str, Any], fila_id: str) -> dict[str, Any]:
    """La persona trabada no sabe de otra persona que pueda destrabarlo (contesta la pregunta de la
    decisión 49): queda asentado. En la historia de la tarea, le llega a quien decide quién lo
    resuelve con la cadena entera (decisión 24; o, sin nadie, el incidente para el
    administrador) y a la persona trabada se le dice con la forma de la decisión 35. Los hechos
    para quien escribe."""
    destraba = _la_fila(ctx.cur, fila_id)
    dicho_id = ultimo_dicho_de_quien_destraba(ctx.cur, destraba["blocker_id"])
    informe = _informar_la_cadena(ctx, tarea, destraba, dicho_id)
    return _lo_que_queda_para_quien_esta_trabado(ctx, informe["aviso_de_la_cadena"])


def _lo_que_queda_para_quien_esta_trabado(ctx: Contexto, aviso: dict[str, Any]
                                          ) -> dict[str, Any]:
    """Lo que la persona trabada sabe del informe de la cadena: que quedó asentado (decisión
    35), sin decir que se le informa a alguien ni nombrar a nadie por su cuenta (a quién le
    llega, sólo si lo pregunta). Si no le va a llegar a nadie, quedó asentado igual (decisión 49;
    `_informar_la_cadena` lo dejó en la historia de la tarea): que no le llega a nadie, también
    sólo si lo pregunta."""
    if aviso.get(LLEGA) == NO_LE_VA_A_LLEGAR:
        return {QUEDA_ASENTADO: queda_asentado(ctx.cur, ctx.quien.workspace_id, a_nadie=True)}
    return {QUEDA_ASENTADO: queda_asentado(ctx.cur, ctx.quien.workspace_id, aviso.get("a"))}


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
                     en_la_cadena: set[str]) -> dict[str, Any] | None:
    """A quién va la cadena, o el bloqueo viejo: a quien decide quién lo resuelve (decisión 24
    del usuario, 2026-10-09, que reemplaza al sector de lo que falta de la decisión 5). Al referente
    del sector de la tarea trabada; si es la persona trabada o alguien de la cadena
    (`en_la_cadena`), a quien aprueba el trabajo de la persona trabada; nunca a alguien de la
    cadena. `None` si no hay ninguno."""
    trabado = str(destraba["responsable_membership_id"])
    fuera = {trabado, *map(str, en_la_cadena)}
    if destraba.get("area_id") is not None:
        cur.execute("""select i.membership_id, i.nombre from area a
                         join integrante i on i.membership_id = a.referente_membership_id
                        where a.id = %s""", (str(destraba["area_id"]),))
        fila = cur.fetchone()
        if fila is not None and str(fila["membership_id"]) not in fuera:
            return fila
    aprueba = referente(cur, trabado)
    if aprueba is not None and str(aprueba["membership_id"]) not in fuera:
        return aprueba
    return None


# --- La cadena: hasta tres personas preguntadas (C-5d; decisiones 24, 49 y 51) ------------------

def _filas_del_bloqueo(cur, blocker_id) -> list[dict[str, Any]]:
    """Quién dijo quién destraba el bloqueo, en orden, con los nombres."""
    cur.execute("""select u.id, u.destraba_membership_id, u.destraba_externo, u.no_sabe,
                          u.dicho_por_membership_id, u.at, d.nombre as destraba, p.nombre as de
                     from blocker_unblocker u
                     left join integrante d on d.membership_id = u.destraba_membership_id
                     join integrante p on p.membership_id = u.dicho_por_membership_id
                    where u.blocker_id = %s order by u.at, u.id""", (str(blocker_id),))
    return cur.fetchall()


def _se_le_pregunto_si_hay_otra(cur, fila_id) -> bool:
    """Si después de esa fila (un "ni idea") Leda le preguntó a la persona trabada si se le ocurre
    otra persona (`avisos.QUIEN_MAS_PUEDE_DESTRABAR`, cuya clave la nombra)."""
    cur.execute("""select 1 from scheduled_notice
                    where tipo = %s and split_part(dedupe_key, ':', 4) = %s limit 1""",
                (QUIEN_MAS_PUEDE_DESTRABAR, f"u{fila_id}"))
    return cur.fetchone() is not None


def _vuelta(cur, blocker_id, trabado: str) -> list[dict[str, Any]]:
    """Las filas de esta vuelta del bloqueo: desde la última vez que la persona trabada dijo por
    su cuenta quién lo destraba. Lo que contesta cuando Leda le pregunta si se le ocurre otra
    persona (decisión 49) sigue la misma cadena: no empieza otra."""
    filas = _filas_del_bloqueo(cur, blocker_id)
    inicio = 0
    for i, f in enumerate(filas):
        if str(f["dicho_por_membership_id"]) == trabado and not (
                i > 0 and _se_le_pregunto_si_hay_otra(cur, filas[i - 1]["id"])):
            inicio = i
    return filas[inicio:]


def _nombrados(filas: list[dict[str, Any]], trabado: str) -> set[str]:
    """Las personas del equipo que otra persona nombró como quien lo destraba: las de la cadena,
    a quienes Leda les preguntó (o les habría preguntado). Ni la persona trabada ni quien dijo
    que le toca a ella misma."""
    return {str(f["destraba_membership_id"]) for f in filas
            if f["destraba_membership_id"] is not None
            and str(f["destraba_membership_id"]) != str(f["dicho_por_membership_id"])
            and str(f["destraba_membership_id"]) != trabado}


def en_la_cadena(cur, blocker_id, trabado: str) -> set[str]:
    """Quiénes fueron parte de la cadena de un bloqueo, en toda su historia (el bloqueo viejo,
    decisión 24): a nadie de ellos le llega lo que se asienta."""
    return _nombrados(_filas_del_bloqueo(cur, blocker_id), trabado)


def contesta_si_hay_otra(cur, fila_id: str) -> bool:
    """Si esa fila, dicha por la persona trabada, contesta la pregunta de si se le ocurre otra
    persona (decisión 49): la fila anterior es el "ni idea" que la hizo hacer."""
    cur.execute("""select u.id from blocker_unblocker u
                     join blocker_unblocker f on f.blocker_id = u.blocker_id
                    where f.id = %s and (u.at, u.id) < (f.at, f.id)
                    order by u.at desc, u.id desc limit 1""", (str(fila_id),))
    anterior = cur.fetchone()
    return anterior is not None and _se_le_pregunto_si_hay_otra(cur, anterior["id"])


def _informar_la_cadena(ctx: Contexto, tarea: dict[str, Any], destraba: dict[str, Any],
                        dicho_id: str, *,
                        sin_chat: dict[str, Any] | None = None) -> dict[str, Any]:
    """La cadena entera le llega al referente como información, terminado el margen para
    corregir (`avisos.CADENA_DEL_BLOQUEO`): no le pide nada (ADR 0018, 9c, precisión del
    2026-10-09). `sin_chat`: a quién quedó nombrado y Leda no le puede escribir, y por qué.

    Le llega una sola vez por cadena (por vuelta, `_vuelta`; revisión del 2026-10-09): si ya
    salió, no se manda otra vez y los hechos dicen que ya le llegó; si todavía no salió, la
    anterior queda omitida (nunca se borra) y sale ésta, con lo último que se dijo. A quien decide
    quién lo resuelve, nunca a alguien de la cadena (`a_quien_informar`, decisión 24). Los hechos
    para quien escribe: a quién y cuándo, o por qué no le llega."""
    cur = ctx.cur
    trabado = str(destraba["responsable_membership_id"])
    vuelta = _vuelta(cur, destraba["blocker_id"], trabado)
    previas = _cadenas_de_esta_vuelta(cur, destraba, tarea["id"], vuelta)
    enviada = next((p for p in previas if p["estado"] == "enviado"), None)
    if enviada is not None:
        return {"aviso_de_la_cadena": {
            "a": enviada["a_nombre"], LLEGA: YA_LE_LLEGO,
            "el": enviada["resuelto_en"].astimezone(ctx.calendario.zona).date().isoformat()}}
    guardadas = [p for p in previas if p["estado"] == "guardado"]
    ref = a_quien_informar(cur, destraba, _nombrados(vuelta, trabado))
    quien, motivo = (alcanzable(cur, str(ref["membership_id"])) if ref is not None
                     else (None, SIN_REFERENTE))
    if motivo is not None:
        if guardadas:
            # La que ya estaba guardada sigue: es la que le llega.
            ultima = guardadas[-1]
            return {"aviso_de_la_cadena": {
                "a": ultima["a_nombre"],
                LLEGA: ultima["programado_para"].astimezone(ctx.calendario.zona).isoformat()}}
        _asentar_sin_a_quien(ctx, tarea, destraba, motivo)
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


def _asentar_sin_a_quien(ctx: Contexto, tarea: dict[str, Any], destraba: dict[str, Any],
                         motivo: str) -> None:
    """La cadena que no le llega a nadie queda asentada igual (decisión 49; C-5b): en la historia
    de la tarea (su auditoría, con la cadena entera y el motivo) y con un incidente para el
    administrador, para que complete quién decide."""
    eslabones = cadena(ctx.cur, destraba["blocker_id"], str(destraba["responsable_membership_id"]))
    auditar(ctx.cur, accion="asentar_la_cadena_del_bloqueo", workspace_id=ctx.quien.workspace_id,
            sujeto_tipo="blocker", sujeto_id=destraba["blocker_id"], quien=ctx.quien,
            detalle={"task_id": tarea["id"], "cadena": eslabones, SIN_A_QUIEN_INFORMAR: motivo,
                     "at": ctx.ahora.isoformat(), "inbound_message_id": ctx.entrante_id})
    avisar_que_no_hay_a_quien(
        ctx.cur, ctx.quien.workspace_id,
        f"La cadena del bloqueo de la tarea «{tarea['titulo']}» de {destraba['responsable']} se "
        f"cortó (nadie lo toma) y no le llega a nadie que decida: "
        f"{por_que_no_hay_a_quien(motivo)}. Quedó asentado en la historia de la tarea.",
        referencia_tipo=REFERENCIA_INBOUND_MESSAGE if ctx.entrante_id else None,
        referencia_id=ctx.entrante_id, chat_id=ctx.chat_id, app_user_id=ctx.quien.app_user_id)


def _cadenas_de_esta_vuelta(cur, destraba: dict[str, Any], task_id: str,
                           vuelta: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Los avisos de la cadena ya guardados para esta vuelta del bloqueo (`_vuelta`): los de lo
    que se dijo desde que empezó (la clave de cada uno nombra lo dicho, `avisos.de_la_clave`), del
    más viejo al más nuevo."""
    desde = vuelta[0] if vuelta else None
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
    """La cadena de un bloqueo, de quién dijo qué, en esta vuelta (`_vuelta`: desde la última vez
    que la persona trabada dijo por su cuenta quién lo destraba, con lo que contestó cuando Leda
    le preguntó si se le ocurría otra persona): a quién le toca según cada uno
    (`blocker_unblocker`), y si dijo que no le corresponde, con sus palabras
    (`dicho_de_quien_destraba`). Quien no lo tomó sin decir de quién es cierra la cadena con lo
    que dijo."""
    filas = _vuelta(cur, blocker_id, trabado)
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
        llego = {"se_le_pregunta_a": {"a": aviso["a_nombre"], LLEGA: YA_LE_LLEGO, "el": el}}
        persona = str(aviso["destinatario_membership_id"])
        fila = quien_destraba(cur, de_la_clave(aviso))
        if fila is not None and (_le_pregunta_todavia(cur, persona, de_la["id"])
                                 or _dio_un_dia(cur, persona, str(fila["blocker_id"]))):
            # Ya le llegó y Leda le sigue preguntando, o dio un día (Leda le volvería a
            # preguntar): deja de preguntarle y le cierra el tema (decisión 39, derivada en la 47
            # y, con un día dado, en la C-5d).
            cerrado = cerrar_el_tema(ctx, de_la["id"], str(fila["blocker_id"]),
                                     DIJO_QUE_YA_LO_HABLARON, solo={persona})
            auditar(cur, accion="no_escribirle", workspace_id=ctx.quien.workspace_id,
                    sujeto_tipo="scheduled_notice", sujeto_id=aviso["id"], quien=ctx.quien,
                    detalle={"aviso_id": str(aviso["id"]), "task_id": de_la["id"],
                             "destinatario_membership_id": persona, "ya_le_llego": True,
                             "at": ctx.ahora.isoformat(), "inbound_message_id": ctx.entrante_id})
            return {"resultado": "anotado", **hecho, **llego, **cerrado}
        return {"resultado": "no_se_puede", "motivo": YA_SE_LE_ESCRIBIO, **hecho, **llego}
    return {"resultado": "no_se_puede", "motivo": NO_LE_IBA_A_ESCRIBIR, **hecho,
            "se_le_pregunta_a": {"a": aviso["a_nombre"],
                                 LLEGA: NO_LE_LLEGO if aviso["estado"] == "fallido"
                                 else NO_LE_VA_A_LLEGAR,
                                 **({"motivo": aviso["motivo_omision"]}
                                    if aviso["motivo_omision"] else {})}}


def _dio_un_dia(cur, persona: str, blocker_id: str) -> bool:
    """Si lo último que dijo esa persona del bloqueo es un día para destrabarlo, sin que ya
    esté."""
    cur.execute("""select d.para_cuando, d.ya_esta from dicho_de_quien_destraba d
                     join blocker_unblocker u on u.id = d.blocker_unblocker_id
                    where u.blocker_id = %s and d.dicho_por_membership_id = %s
                    order by d.at desc, d.id desc limit 1""", (blocker_id, persona))
    ultimo = cur.fetchone()
    return ultimo is not None and ultimo["para_cuando"] is not None and not ultimo["ya_esta"]


def _titulo(ctx: Contexto, task_id) -> dict[str, str]:
    return tarea_hecho(next(t for t in ctx.tareas if t["id"] == str(task_id)))


# --- Lo que cuenta la persona trabada (C-5c; decisiones 47, 48 y 39) ----------------------------

def contar_lo_que_arreglaron(ctx: Contexto, datos: dict[str, Any],
                             tarea: dict[str, Any] | None) -> dict[str, Any]:
    """La persona trabada cuenta lo que arregló con quien destraba su tarea, lo corrige o le
    contesta algo que esa persona dijo: queda anotado sobre la fila de quien lo destraba
    (`dicho_de_quien_destraba`, dicho por ella) y le llega a esa persona, para confirmarlo o como
    cierre del tema (ver el módulo)."""
    cur = ctx.cur
    if tarea is None:
        tarea = _la_del_tema(ctx)
    if tarea is None:
        return {"resultado": "falta_dato", "falta": ["tarea"]}
    tema = _el_tema(cur, tarea["id"])
    if tema is None:
        return {"resultado": "no_se_puede", "motivo": SIN_QUIEN_DESTRABA,
                "tarea": tarea_hecho(tarea)}
    para_cuando = None
    if not vacio(datos.get("para_cuando")):
        try:
            para_cuando = date.fromisoformat(str(datos["para_cuando"]).strip())
        except ValueError:
            return {"resultado": "falta_dato", "falta": ["para_cuando"],
                    "tarea": tarea_hecho(tarea)}
    lo_que_dice = None if vacio(datos.get("lo_que_dice")) else str(datos["lo_que_dice"]).strip()
    if para_cuando is None and lo_que_dice is None:
        return {"resultado": "falta_dato", "falta": ["lo_que_arreglaron"],
                "tarea": tarea_hecho(tarea)}
    cierra = _contesta_lo_que_se_le_paso(cur, tema["blocker_id"], ctx.quien.membership_id)
    cur.execute(
        """insert into dicho_de_quien_destraba (workspace_id, blocker_unblocker_id,
                                                dicho_por_membership_id, para_cuando,
                                                lo_que_dice, at)
           values (%s, %s, %s, %s, %s, %s) returning id""",
        (ctx.quien.workspace_id, tema["id"], ctx.quien.membership_id, para_cuando, lo_que_dice,
         ctx.ahora))
    dicho_id = str(cur.fetchone()["id"])
    dice = {k: v for k, v in (("para_cuando", para_cuando.isoformat() if para_cuando else None),
                              ("lo_que_dice", lo_que_dice)) if v is not None}
    auditar(cur, accion="anotar_lo_que_arreglaron", workspace_id=ctx.quien.workspace_id,
            sujeto_tipo="blocker", sujeto_id=tema["blocker_id"], quien=ctx.quien,
            detalle={"dicho_id": dicho_id, "blocker_unblocker_id": str(tema["id"]),
                     "task_id": tarea["id"], **dice, "cierra_el_tema": cierra,
                     "at": ctx.ahora.isoformat(), "inbound_message_id": ctx.entrante_id})
    # Lo que se le preguntaba a ella ya tiene respuesta, y a quien destraba ya no se le pregunta:
    # vale lo que contestó el primero (decisión 48).
    _ya_no_se_le_pregunta_a_quien_esta_trabado(ctx, tarea["id"], YA_LO_CONTO_QUIEN_ESTA_TRABADO)
    destraba = (str(tema["destraba_membership_id"]) if tema["destraba_membership_id"]
                else None)
    if destraba is not None:
        _ya_no_le_pregunta(ctx, destraba, tarea["id"])
        cur.execute("""select id from scheduled_notice
                        where task_id = %s and tipo = %s and estado = 'guardado'
                          and destinatario_membership_id = %s""",
                    (tarea["id"], PREGUNTA_A_QUIEN_DESTRABA, destraba))
        for aviso in cur.fetchall():
            omitir(cur, str(aviso["id"]), YA_LO_CONTO_QUIEN_ESTA_TRABADO, ctx.ahora)
    hecho: dict[str, Any] = {"resultado": "anotado", "tarea": tarea_hecho(tarea),
                             "dice_quien_esta_trabado": dice}
    if cierra:
        hecho[CIERRA_EL_TEMA] = True
    if destraba is not None:
        _juntar(hecho, _avisar_a_quien_destraba(ctx, tarea, tema, destraba, dicho_id, dice,
                                                _como_llega(cierra, acordado=True)))
    return hecho


def _la_del_tema(ctx: Contexto) -> dict[str, Any] | None:
    """La tarea de la que habla la persona trabada sin nombrarla: la de su pregunta de qué
    arregló, o la de lo último que Leda le pasó de quien la destraba para que lo confirme."""
    cur = ctx.cur
    cur.execute("""select task_id from conversation_question
                    where membership_id = %s and tipo = %s and cerrada_en is null
                    order by para_despues_en nulls first, abierta_en desc, id limit 1""",
                (ctx.quien.membership_id, preguntas.QUE_ARREGLARON))
    fila = cur.fetchone()
    if fila is None:
        cur.execute("""select a.task_id, a.hechos from conversation_state s
                         join scheduled_notice a on a.id = s.ultimo_aviso_id
                        where s.membership_id = %s and a.tipo = %s""",
                    (ctx.quien.membership_id, LO_QUE_DIJO_QUIEN_DESTRABA))
        fila = cur.fetchone()
        if fila is not None and not (fila["hechos"] or {}).get(SE_LO_PASA_SI_CONTESTA):
            fila = None
    if fila is None:
        return None
    return next((t for t in ctx.tareas if t["id"] == str(fila["task_id"])), None)


def _el_tema(cur, task_id: str) -> dict[str, Any] | None:
    """El tema de la persona trabada con quien destraba su tarea: lo último que se dijo de quién
    destraba su bloqueo más nuevo (abierto o ya cerrado), si es otra persona del equipo o alguien
    de afuera. `None` si no hay nadie más (no sabe quién, o le toca a ella)."""
    cur.execute("""select b.id from blocker b where b.task_id = %s
                    order by b.abierto_en desc, b.id desc limit 1""", (task_id,))
    bloqueo = cur.fetchone()
    if bloqueo is None:
        return None
    ultimo = ultimo_quien_destraba(cur, bloqueo["id"])
    if ultimo is None:
        return None
    fila = _la_fila(cur, str(ultimo["id"]))
    otra = (fila["destraba_membership_id"] is not None
            and str(fila["destraba_membership_id"]) != str(fila["responsable_membership_id"]))
    return fila if otra or fila["destraba_externo"] else None


def _avisar_a_quien_destraba(ctx: Contexto, tarea: dict[str, Any], tema: dict[str, Any],
                             persona: str, dicho_id: str, dice: dict[str, Any],
                             como_llega: dict[str, Any]) -> dict[str, Any]:
    """Lo que dice la persona trabada le llega a quien destraba (o destrababa) su tarea,
    terminado el margen para corregir (`avisos.LO_QUE_DIJO_QUIEN_ESTA_TRABADO`): para que lo
    confirme o como cierre del tema (`como_llega`). Lo que dijo antes y todavía no le llegó queda
    atrás. Sin Leda conectada, nada se promete. Los hechos para quien escribe."""
    cur = ctx.cur
    quien, motivo = alcanzable(cur, persona)
    if motivo is not None:
        return {"no_se_le_puede_escribir_a": {"a": quien["nombre"] if quien else None,
                                              "motivo": motivo}}
    cur.execute("""select id from scheduled_notice
                    where task_id = %s and tipo = %s and estado = 'guardado'
                      and destinatario_membership_id = %s""",
                (tarea["id"], LO_QUE_DIJO_QUIEN_ESTA_TRABADO, persona))
    for viejo in cur.fetchall():
        omitir(cur, str(viejo["id"]), DIJO_ALGO_MAS_NUEVO, ctx.ahora)
    sale = sale_con_margen(cur, ctx.calendario, ctx.quien.workspace_id, ctx.ahora)
    aviso_id, _ = guardar(
        cur, ctx.quien.workspace_id, LO_QUE_DIJO_QUIEN_ESTA_TRABADO, task_id=tarea["id"],
        destinatario=persona,
        hechos={"aviso": LO_QUE_DIJO_QUIEN_ESTA_TRABADO, "necesita_respuesta": False,
                "tarea": tarea["titulo"], "quien_esta_trabado": ctx.quien.nombre,
                "causa": tema["causa"], "dice_quien_esta_trabado": dice, **como_llega},
        programado_para=sale,
        clave=f"motor:{LO_QUE_DIJO_QUIEN_ESTA_TRABADO}:{tarea['id']}:d{dicho_id}",
        ahora=ctx.ahora)
    ctx.avisos_guardados.append(aviso_id)
    hecho: dict[str, Any] = {"aviso_a_quien_destraba": {"a": quien["nombre"],
                                                        LLEGA: sale.isoformat()}}
    nombrar_efecto(hecho, "aviso_a_quien_destraba", AVISO, aviso_id)
    return hecho


def vigencia_de_lo_que_dijo_quien_esta_trabado(m: Momento, aviso
                                               ) -> tuple[str | None, dict[str, Any]]:
    """Lo que dijo la persona trabada sale salvo que después haya dicho algo más nuevo del mismo
    bloqueo (sale eso en su lugar)."""
    m.cur.execute("""select d.id, d.dicho_por_membership_id, u.blocker_id
                       from dicho_de_quien_destraba d
                       join blocker_unblocker u on u.id = d.blocker_unblocker_id
                      where d.id = %s""", (de_la_clave(aviso),))
    dicho = m.cur.fetchone()
    if dicho is None:
        return "tarea_inexistente", {}
    m.cur.execute("""select d.id from dicho_de_quien_destraba d
                       join blocker_unblocker u on u.id = d.blocker_unblocker_id
                      where u.blocker_id = %s and d.dicho_por_membership_id = %s
                      order by d.at desc, d.id desc limit 1""",
                  (dicho["blocker_id"], dicho["dicho_por_membership_id"]))
    if str(m.cur.fetchone()["id"]) != str(dicho["id"]):
        return DIJO_ALGO_MAS_NUEVO, {}
    return None, dict(aviso["hechos"])


def vigencia_de_que_arreglaron(m: Momento, aviso) -> tuple[str | None, dict[str, Any]]:
    """La pregunta a la persona trabada de qué arregló (o cómo le fue) sale mientras siga
    trabada con esa persona como quien lo destraba y nadie haya contado todavía lo que
    arreglaron."""
    tarea = leer_tarea(m.cur, aviso["task_id"])
    if tarea is None:
        return "tarea_inexistente", {}
    if tarea["estado"] in ("terminada", "cancelada"):
        return "tarea_cerrada", {}
    if str(tarea["responsable_membership_id"]) != str(aviso["destinatario_membership_id"]):
        return "cambio_el_responsable", {}
    fila = quien_destraba(m.cur, de_la_clave(aviso))
    if fila is None:
        return "tarea_inexistente", {}
    motivo = sigue_esperando_que_destrabe(m.cur, de_la_clave(aviso))
    if motivo is not None:
        return motivo, {}
    m.cur.execute("""select d.dicho_por_membership_id from dicho_de_quien_destraba d
                       join blocker_unblocker u on u.id = d.blocker_unblocker_id
                      where u.blocker_id = %s and d.at >= %s
                      order by d.at desc, d.id desc limit 1""",
                  (fila["blocker_id"], aviso["creado_en"]))
    contado = m.cur.fetchone()
    if contado is not None:
        return (YA_LO_CONTO_QUIEN_ESTA_TRABADO
                if str(contado["dicho_por_membership_id"]) == str(aviso["destinatario_membership_id"])
                else YA_LO_CONTO_QUIEN_DESTRABA), {}
    return None, dict(aviso["hechos"])


# --- "Se lo pido yo y te cuento" (la salida de la decisión 37) ---------------------------------

def pedirselo_y_contar(ctx: Contexto, datos: dict[str, Any],
                       tarea: dict[str, Any] | None) -> dict[str, Any]:
    """La persona trabada se lo pide directamente a quien destraba: Leda no le escribe, deja de
    preguntarle si ya le preguntaba, y al día hábil siguiente le pregunta a ella cómo le fue
    (ver el módulo)."""
    cur = ctx.cur
    if tarea is None:
        tarea = _la_trabada_de_lo_que_se_hablaba(ctx)
    if tarea is None:
        return {"resultado": "falta_dato", "falta": ["tarea"]}
    cur.execute("""select id, causa from blocker where task_id = %s and resuelto_en is null
                    order by abierto_en desc, id desc limit 1""", (tarea["id"],))
    bloqueo = cur.fetchone()
    if bloqueo is None:
        return {"resultado": "no_se_puede", "motivo": "sin_bloqueo_abierto",
                "tarea": tarea_hecho(tarea)}
    blocker_id = str(bloqueo["id"])
    hecho: dict[str, Any] = {"resultado": "anotado", "tarea": tarea_hecho(tarea)}
    ultimo = ultimo_quien_destraba(cur, blocker_id)
    texto = None if vacio(datos.get("quien")) else str(datos["quien"]).strip()
    coinciden = integrantes_que_coinciden(cur, texto) if texto else []
    if len(coinciden) > 1:
        return {"resultado": "falta_dato", "falta": ["integrante"],
                "coinciden": [c["nombre"] for c in coinciden], "tarea": tarea_hecho(tarea)}
    if coinciden and str(coinciden[0]["membership_id"]) == ctx.quien.membership_id:
        texto = None                    # nombrarse a sí misma no es decir a quién se lo pide
    if texto is not None:
        integrante_ = coinciden[0] if coinciden else None
        nuevo_id = str(integrante_["membership_id"]) if integrante_ else None
        if ultimo is None or (nuevo_id or texto) != (
                str(ultimo["destraba_membership_id"]) if ultimo["destraba_membership_id"]
                else ultimo["destraba_externo"]):
            # Otra persona que la destraba, dicha por ella: a quien Leda le preguntaba antes ya
            # no le hace falta (decisión 39).
            cur.execute(
                """insert into blocker_unblocker (workspace_id, blocker_id,
                                                  destraba_membership_id, destraba_externo,
                                                  dicho_por_membership_id, at)
                   values (%s, %s, %s, %s, %s, %s) returning *""",
                (ctx.quien.workspace_id, blocker_id, nuevo_id,
                 None if integrante_ else texto, ctx.quien.membership_id, ctx.ahora))
            ultimo = cur.fetchone()
            auditar(cur, accion="anotar_quien_destraba", workspace_id=ctx.quien.workspace_id,
                    sujeto_tipo="blocker", sujeto_id=blocker_id, quien=ctx.quien,
                    detalle={"blocker_unblocker_id": str(ultimo["id"]), "task_id": tarea["id"],
                             "destraba_membership_id": nuevo_id,
                             "destraba_externo": None if integrante_ else texto,
                             "no_sabe": False, "at": ctx.ahora.isoformat(),
                             "inbound_message_id": ctx.entrante_id})
            _juntar(hecho, cerrar_el_tema(ctx, tarea["id"], blocker_id, CAMBIO_QUIEN_DESTRABA,
                                          salvo=(nuevo_id,) if nuevo_id else ()))
    if ultimo is None or ultimo["no_sabe"] or (
            ultimo["destraba_membership_id"] is not None
            and str(ultimo["destraba_membership_id"]) == ctx.quien.membership_id):
        return {"resultado": "falta_dato", "falta": ["quien"], "tarea": tarea_hecho(tarea)}
    fila = str(ultimo["id"])
    persona = (str(ultimo["destraba_membership_id"]) if ultimo["destraba_membership_id"]
               else None)
    se_lo_pide_a = integrante(cur, persona)["nombre"] if persona else ultimo["destraba_externo"]
    # Leda no le escribe: lo que no salió no sale, y si ya le preguntaba, deja de hacerlo y se lo
    # dice (decisión 39).
    cur.execute("""select id from scheduled_notice
                    where task_id = %s and tipo = %s and estado = 'guardado'""",
                (tarea["id"], PREGUNTA_A_QUIEN_DESTRABA))
    for aviso in cur.fetchall():
        omitir(cur, str(aviso["id"]), SE_LO_PIDE_QUIEN_ESTA_TRABADO, ctx.ahora)
    if persona is not None and _le_pregunta_todavia(cur, persona, tarea["id"]):
        _juntar(hecho, cerrar_el_tema(ctx, tarea["id"], blocker_id, SE_LO_PIDE_QUIEN_ESTA_TRABADO,
                                      solo={persona}))
    # Al día hábil siguiente, a la hora en que Leda escribe, cómo le fue: la pregunta de qué
    # arregló, que la escalera de las preguntas no abandona (decisión 38).
    cal = ctx.calendario
    hoy = ctx.ahora.astimezone(cal.zona).date()
    cuando = sale_el(cal, cal.proximo_habil(hoy + timedelta(days=1)))
    aviso_id, _ = guardar(
        cur, ctx.quien.workspace_id, COMO_LE_FUE, task_id=tarea["id"],
        destinatario=ctx.quien.membership_id,
        hechos={"aviso": COMO_LE_FUE, "necesita_respuesta": True,
                "pregunta": preguntas.QUE_ARREGLARON, "tarea": tarea["titulo"],
                "se_lo_pide_a": se_lo_pide_a, "causa": bloqueo["causa"]},
        programado_para=cuando, clave=f"motor:{COMO_LE_FUE}:{tarea['id']}:u{fila}",
        ahora=ctx.ahora)
    ctx.avisos_guardados.append(aviso_id)
    auditar(cur, accion="pedirselo_y_contar", workspace_id=ctx.quien.workspace_id,
            sujeto_tipo="blocker", sujeto_id=blocker_id, quien=ctx.quien,
            detalle={"task_id": tarea["id"], "blocker_unblocker_id": fila,
                     "aviso_id": aviso_id, "at": ctx.ahora.isoformat(),
                     "inbound_message_id": ctx.entrante_id})
    hecho["se_lo_pide_a"] = se_lo_pide_a
    hecho["le_pregunta_como_le_fue"] = {LLEGA: cuando.isoformat()}
    nombrar_efecto(hecho, "le_pregunta_como_le_fue", AVISO, aviso_id)
    return hecho


def _la_trabada_de_lo_que_se_hablaba(ctx: Contexto) -> dict[str, Any] | None:
    """La tarea trabada de la que se hablaba: la de lo que Leda le propuso para salir del
    bloqueo o la de su pregunta de quién lo destraba; si no, la única trabada."""
    ctx.cur.execute("""select task_id from conversation_question
                        where membership_id = %s and cerrada_en is null
                          and task_id is not null
                          and (tipo = %s
                               or (tipo = %s and jugada ->> 'nombre' = 'anotar_quien_destraba'))
                        order by para_despues_en nulls first, abierta_en desc limit 1""",
                    (ctx.quien.membership_id, preguntas.QUIEN_DESTRABA, preguntas.PROPUESTA))
    fila = ctx.cur.fetchone()
    if fila is not None:
        return next((t for t in ctx.tareas if t["id"] == str(fila["task_id"])), None)
    trabadas = [t for t in ctx.tareas if t["estado"] == "bloqueada"]
    return trabadas[0] if len(trabadas) == 1 else None
