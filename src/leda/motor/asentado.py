"""Quedó asentado (decisión 35 del usuario, 2026-10-09; C-5a).

Leda no dice que informó a alguien ni nombra a nadie por su cuenta: dice que quedó asentado y,
sólo si es verdad que va a figurar en el informe al grupo del espacio, que es para que el equipo
esté al tanto. Si la persona pregunta a quién se le avisó, Leda dice la verdad. Corrige la forma de
las decisiones 21 (lo que pasa si no contesta) y 34 (el bloqueo viejo, a la persona trabada) y de
todo aviso a una persona sobre su propio atraso o su propio bloqueo. El porqué, del usuario: es más
honesto, y le saca a quien está arriba el papel del vigilante.

**La cocina, no frases** (regla del mozo): el hecho `queda_asentado` dice que queda asentado (o que
va a quedar, si todavía no pasó) y si figura en el informe al grupo
(`figura_en_el_informe_al_grupo`). A quién le llega, cuando se sabe, va en el mismo hecho (`a`) y
la redacción lo recibe dentro de `solo_si_pregunta` (`hechos.NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO`).

**Si figura en el informe al grupo** es un hecho del código, no del momento: el espacio tiene un
grupo (`workspace.grupo_chat_id`, del pack `telegram.grupo_gestion_id`) y al menos una cadencia
activa al grupo (`cadence_job.audiencia = 'grupo'`, como `resumen_grupal` e `informe_semanal` de
CoreWork) con un ritmo que se entiende (`cadencias.leer_ritmo`). Es el predicado único con el que
el informe al grupo (C-6, decisión 25; `informe_al_grupo.py`) decide si se guarda: verdadero sólo
cuando ese informe de verdad corre para el espacio.

**Sin nadie a quien informar** (decisión 49 del usuario, qué es dejar asentado, y "nunca fallar en
silencio"; C-5b): si no hay referente ni quien apruebe el trabajo de la persona trabada, o esa
persona no tiene Leda conectada, queda asentado igual: en la historia de la tarea (la auditoría de
quien lo asienta), en el informe al grupo si el espacio lo tiene, y a la persona trabada se le dice
con la misma forma; que no le llega a nadie, sólo si lo pregunta (`NO_LE_LLEGA_A_NADIE`, dentro de
`solo_si_pregunta`). Y queda un incidente para el administrador, por su canal, para que complete
quién decide (`avisar_que_no_hay_a_quien`).
"""

from __future__ import annotations

from typing import Any

# Lo que la persona sabe y Leda dice sólo si lo pregunta (`turno.SOLO_SI_PREGUNTA`).
SOLO_SI_PREGUNTA = "solo_si_pregunta"

QUEDA_ASENTADO = "queda_asentado"
# Lo asentado sin nadie a quien informar (C-5b): por qué (el motivo, en la auditoría y en el aviso
# omitido de esa vez), lo que la persona sabe sólo si lo pregunta, y la etapa de su incidente.
SIN_A_QUIEN_INFORMAR = "sin_a_quien_informar"
NO_LE_LLEGA_A_NADIE = "no_le_llega_a_nadie"
ETAPA_SIN_A_QUIEN_INFORMAR = "motor_sin_a_quien_informar"
FIGURA_EN_EL_INFORME_AL_GRUPO = "figura_en_el_informe_al_grupo"
# La audiencia de una cadencia al grupo (`cadence_job.audiencia`, como la carga el importador).
AL_GRUPO = "grupo"


def hay_informe_al_grupo(cur, workspace_id: str) -> bool:
    """Si el espacio tiene informe al grupo que de verdad corre: su grupo y una cadencia activa
    al grupo con un ritmo que se entiende."""
    from .cadencias import leer_ritmo   # cadencias importa `avisos`, que importa este módulo

    cur.execute("""select w.grupo_chat_id is not null as con_grupo,
                          array(select c.cron from cadence_job c
                                 where c.workspace_id = w.id and c.activo
                                   and c.audiencia = %s) as ritmos
                     from workspace w where w.id = %s""", (AL_GRUPO, workspace_id))
    fila = cur.fetchone()
    return bool(fila and fila["con_grupo"]
                and any(leer_ritmo(cron) is not None for cron in fila["ritmos"]))


def queda_asentado(cur, workspace_id: str, a: str | None = None, *,
                   a_nadie: bool = False) -> dict[str, Any]:
    """El hecho de que queda asentado: si figura en el informe al grupo y, si se sabe, a quién
    le llega (que la redacción dice sólo si la persona lo pregunta). `a_nadie`: no le llega a
    nadie, que también se dice sólo si lo pregunta."""
    hecho: dict[str, Any] = {FIGURA_EN_EL_INFORME_AL_GRUPO: hay_informe_al_grupo(cur,
                                                                                 workspace_id)}
    if a is not None:
        hecho["a"] = a
    if a_nadie:
        hecho[SOLO_SI_PREGUNTA] = {NO_LE_LLEGA_A_NADIE: True}
    return hecho


def avisar_que_no_hay_a_quien(cur, workspace_id: str, resumen: str, **referencia: Any) -> None:
    """El incidente para el administrador, por su canal, de un bloqueo asentado que no le llega a
    nadie que decida. `resumen`, sin texto de mensajes: la tarea, quién está trabado y por qué
    no hay a quién."""
    from ..incidentes import registrar_incidente
    registrar_incidente(cur, workspace_id, resumen, severidad="media",
                        etapa=ETAPA_SIN_A_QUIEN_INFORMAR, **referencia)


def por_que_no_hay_a_quien(motivo: str) -> str:
    """Por qué el bloqueo no le llega a nadie, en palabras para el resumen del incidente."""
    from .persecucion import SIN_REFERENTE
    if motivo == SIN_REFERENTE:
        return ("su sector no tiene referente y nadie aprueba el trabajo de la persona trabada "
                "(o el referente es ella misma)")
    return f"quien tendría que recibirlo no tiene Leda conectada ({motivo})"
