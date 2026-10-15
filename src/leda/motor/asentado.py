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

from datetime import date
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


ETAPA_SECTOR_SIN_ENCARGADO = "motor_sector_sin_encargado"


def avisar_que_el_sector_no_tiene_encargado(cur, workspace_id: str, area_id: str, para: str,
                                            hoy: date) -> None:
    """El incidente para el administrador, por su canal, de un sector sin encargado (el
    referente de su área) cuando alguien necesitaba que decidiera algo: sólo la administración
    lo puede completar (la corrección chica de la Fase C). Una vez por sector y por día (`clave`):
    los pedidos de ese día no repiten el aviso, y si sigue así al día siguiente, vuelve. `para`,
    en palabras y sin texto de mensajes: qué hacía falta decidir. A la persona no le llega nada
    técnico (constitución §10): sus hechos siguen diciendo sólo que no hay encargado."""
    from ..incidentes import registrar_incidente
    cur.execute("select nombre from area where id = %s", (str(area_id),))
    fila = cur.fetchone()
    nombre = fila["nombre"] if fila else "(sin nombre)"
    registrar_incidente(
        cur, workspace_id,
        f"El sector «{nombre}» no tiene encargado (el referente de su área), y {para}: nadie lo "
        f"puede decidir hasta que tenga uno.",
        severidad="media", etapa=ETAPA_SECTOR_SIN_ENCARGADO, referencia_tipo="area",
        referencia_id=str(area_id),
        clave=f"{ETAPA_SECTOR_SIN_ENCARGADO}:{area_id}:{hoy.isoformat()}")


def por_que_no_hay_a_quien(motivo: str) -> str:
    """Por qué el bloqueo no le llega a nadie, en palabras para el resumen del incidente."""
    from .persecucion import INACTIVO, SIN_REFERENTE
    if motivo == SIN_REFERENTE:
        return ("su sector no tiene referente y nadie aprueba el trabajo de la persona que "
                "tiene la tarea (o el referente es ella misma)")
    # Each reason in words, never its code (task "Lenguaje"): `alcanzable` gives INACTIVO or
    # SIN_TELEGRAM; anything else reads as the latter, without the code.
    if motivo == INACTIVO:
        return "quien tendría que recibirlo ya no está activo en el equipo"
    return "quien tendría que recibirlo todavía no tiene Leda conectada"
