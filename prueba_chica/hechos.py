"""El vocabulario de los hechos: qué significa cada dato que el código le pasa a la IA.

Revisión del contrato entre la IA y el código (usuario, 2026-10-05; ADR 0018, decisión 9),
después de la primera ronda real. Un hecho que llega sólo con su valor se lee como la IA cree
que se lee: el atraso de una previsión (el que tendrá la tarea si la previsión se cumple) se le
contó al referente como el atraso de hoy (conversaciones 15 y 16), y antes el estado de un aviso
guardado se contó como enviado (primer contacto real). "Si dice algo mal, primero se mira si la
cocina le pasó el hecho correcto" (`AGENTS.md`, la regla del mozo): el hecho correcto es el que
dice qué es.

Por eso:

- **Dos cosas distintas nunca comparten una clave** (`atraso_dias_habiles` es el de hoy;
  `atraso_si_se_cumple_la_prevision_dias_habiles`, el previsto).
- **Cada clave y cada código tiene su significado acá** (`SIGNIFICADOS`), una sola vez para
  todos los hechos: los de un turno, los de un aviso que Leda manda por su cuenta y lo que la
  IA recibe para elegir jugadas. Un código es un valor escrito como `palabra_con_guiones`; las
  jugadas toman el suyo de su ficha.
- **La IA recibe el significado de todo lo que le llega** en cada pedido (`bloque`), después de
  sus instrucciones, que remiten a esta lista sin repetirla.
- **Un hecho sin significado es una falla del motor** en la corrida (`sin_significado`, que el
  corredor mira en cada pedido a la IA).

Los significados describen datos, no casos: qué es cada cosa, nunca qué decir con ella.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Mapping
from typing import Any

from .fichas import FICHAS

# Un código: minúsculas y cifras, con al menos un guion bajo (un texto libre lleva espacios).
_CODIGO = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)+$")

SIGNIFICADOS: Mapping[str, str] = {
    # --- Lo que recibe la IA en cada pedido ----------------------------------------------------
    "hoy": "La fecha de hoy, en la hora del equipo.",
    "persona": "A quién le escribe Leda.",
    "mensaje": "Lo que la persona escribió ahora; vacío si tocó una opción o si Leda escribe "
               "por su cuenta.",
    "toco": "La opción que la persona tocó, en lugar de escribir.",
    "hechos": "Lo que el sistema hizo, comprobó o necesita en este turno: lo único que se "
              "cuenta como hecho.",
    "pregunta": "La única pregunta que se hace en este mensaje, con su tipo y su tarea; dentro "
                "de un hecho, el tipo de pregunta que ese hecho abrió y se hace ahora.",
    "pregunta_para_despues": "El tipo de una pregunta que el hecho abrió y quedó para "
                             "después: no se hace en este mensaje.",
    "otras_preguntas_para_despues": "Más preguntas que quedaron para después: no se hacen en "
                                    "este mensaje.",
    "ultimos_turnos": "Los últimos mensajes de la conversación con esta persona, del más viejo "
                      "al más nuevo, con lo que se hizo en cada uno: el registro de lo que ya "
                      "pasó y se dijo.",
    "sentido": "En un turno, si es un mensaje de la persona (entrada) o de Leda (salida).",
    "texto": "Lo que se escribió en ese turno.",
    "at": "Cuándo pasó ese turno.",
    "jugadas": "Lo que el sistema entendió de un mensaje, como jugadas de la lista cerrada.",
    "jugadas_posibles": "Las jugadas de la lista cerrada que se pueden elegir.",
    "nombre": "El nombre de una jugada.",
    "datos": "Los datos de una jugada, tal como se entendieron del mensaje.",
    "estado": "El estado de una tarea; o, dentro de un efecto que pasa después (un aviso, un "
              "pedido), si ya pasó o todavía no, con su código; como motivo, que el estado de "
              "la tarea no lo permite; o, para elegir jugadas, la pregunta abierta y las que "
              "quedaron para después.",
    "pregunta_abierta": "La pregunta de Leda que la persona tiene abierta ahora: lo que Leda "
                        "espera que conteste.",
    "para_despues": "Preguntas de Leda que quedaron para después, sin cerrar; como resultado, "
                    "que la pregunta quedó para después.",
    "ultimo_aviso": "El último aviso que Leda le mandó a la persona por su cuenta, y de qué "
                    "tarea o tareas habla.",
    "tareas": "Tareas, cada una con su alias y su título; las de la persona, si no dice otra "
              "cosa.",
    "alias": "El nombre corto de una tarea (T1, T2...) o de una opción (O1, O2...) en este "
             "pedido: es interno, nunca se le muestra a la persona.",
    "titulo": "El título de una tarea: así se la nombra ante la persona.",
    "fecha_objetivo": "La fecha y hora comprometidas de la tarea (su vencimiento).",
    "tipo": "El tipo de una pregunta o de un aviso, con su código.",
    "opciones": "Las opciones de una pregunta: salen como botones y también se pueden "
                "contestar escribiendo.",
    "opcion": "El alias de una opción.",
    "etiqueta": "Lo que dice una opción, como la ve la persona.",
    "propone": "Lo que Leda le propuso a la persona para que elija.",
    "desde_antes": "La pregunta ya se había hecho en un mensaje anterior: se vuelve a ella sin "
                   "pedir que se repita lo que la persona ya dijo.",
    # --- Lo que dice un hecho ------------------------------------------------------------------
    "jugada": "Qué entendió el sistema que dijo o pidió la persona (una jugada de la lista); "
              "dentro de un aviso, la jugada que lo causó.",
    "resultado": "Cómo terminó la jugada, con su código.",
    "tarea": "La tarea de la que se habla: por su alias para elegir jugadas; por su título en "
             "lo que se le cuenta a la persona.",
    "falta": "Los datos que faltan para poder hacer la jugada.",
    "puede_ser": "Las respuestas que sirven para el dato que falta.",
    "coinciden": "Los nombres que coinciden con lo que dijo la persona, cuando es más de uno.",
    "motivo": "Por qué: en una previsión, el porqué que dio la persona, con sus palabras; en "
              "algo que no se hizo o no salió, la razón, con su código.",
    "causa": "Lo que traba la tarea, como lo dijo la persona.",
    "prevision": "La fecha para la que la persona prevé terminar la tarea. No cambia la fecha "
                 "comprometida.",
    "fecha_comprometida": "La fecha comprometida de la tarea (su vencimiento): no cambia con "
                          "una previsión; cambiarla lo decide el referente.",
    "atraso_dias_habiles": "Los días hábiles que la tarea lleva atrasada hoy, contados desde "
                           "la fecha comprometida.",
    "atraso_si_se_cumple_la_prevision_dias_habiles":
        "Los días hábiles de atraso que tendrá la tarea si se cumple la previsión, contados "
        "desde la fecha comprometida hasta la prevista. No es el atraso de hoy: hoy la tarea "
        "puede no estar atrasada.",
    "dias_habiles_hasta_el_vencimiento": "Los días hábiles que faltan hasta la fecha "
                                         "comprometida.",
    "dependientes": "Las tareas abiertas que dependen de ésta.",
    "no_puede_arrancar_hasta_que_termine": "Esa tarea dependiente no puede arrancar hasta que "
                                           "termine ésta.",
    "aviso_al_referente": "El aviso a quien aprueba el trabajo de la persona, con a quién, su "
                          "estado y cuándo sale; vacío si no hay aviso.",
    "sin_aviso": "Por qué no hay aviso al referente, con su código.",
    "a": "A quién va un aviso.",
    "sale": "Cuándo sale un aviso guardado: todavía no salió.",
    "quien_destraba": "Quién puede destrabar el bloqueo: como dato, lo que dijo la persona; "
                      "como tipo de pregunta, Leda pregunta quién lo puede destrabar y espera "
                      "un nombre, que no sabe, o que le toca a ella.",
    "integrante": "Una persona del equipo.",
    "externo": "Alguien de afuera del equipo, como lo nombró la persona.",
    "no_sabe": "La persona dijo que no sabe quién puede destrabarlo.",
    "nadie_mas": "La persona dijo que nadie más puede destrabarlo: le toca a ella.",
    "salidas": "Lo que Leda le propone a la persona para salir de un bloqueo, para que elija.",
    "avance": "Lo que la persona contó de cómo viene la tarea, sin un hecho cierto.",
    "dijo": "Lo que dijo la persona, con sus palabras.",
    "el_pedido_de_estado": "Si Leda sigue esperando saber cómo viene la tarea.",
    "vuelve_a_pedir_el_estado": "Cuándo Leda vuelve a pedirle el estado de la tarea: todavía "
                                "no pasó.",
    "veces_sin_algo_cierto": "Cuántas respuestas seguidas sin un hecho cierto lleva este "
                             "pedido de estado.",
    "no_vuelve_a_pedir_el_estado": "Por qué Leda no vuelve a pedirle el estado.",
    "escalado_a": "A quiénes ya se les avisó que la persona no contestaba, con el estado de "
                  "cada aviso.",
    "vencida": "La tarea pasó su fecha de seguimiento: la fecha comprometida, el atraso de hoy "
               "y, si la había, la previsión que también pasó.",
    "prevision_vencida": "La previsión que la tarea también pasó.",
    "quien_decide": "Quién decide lo que la persona pidió.",
    "alternativa": "La jugada que Leda le ofrece a la persona en lugar de lo pedido.",
    "lo_que_puede_hacer": "Lo que Leda puede hacer por chat.",
    "solo_si_pregunta": "Algo cierto que Leda sabe y dice sólo si la persona lo pregunta.",
    "aviso_al_administrador": "El aviso al administrador de que se pidió algo que no está en "
                              "la lista, con su estado.",
    "vuelve_a": "Cómo quedó la tarea después de corregir: su estado, su previsión o su fecha "
                "comprometida.",
    "prevision_corregida": "La previsión que se corrigió: ya no vale.",
    "aviso_de_la_prevision_corregida": "Qué pasó con el aviso de la previsión que se corrigió.",
    "correccion_al_referente": "El aviso al referente de que una previsión que ya recibió no "
                               "vale, con su estado.",
    "aviso_de_la_prevision_anterior": "El aviso de la previsión que vuelve a valer, con su "
                                      "estado.",
    "prevision_que_no_vale": "La previsión que el referente recibió y ya no vale.",
    "corrige": "La jugada anotada que la persona dijo que estuvo mal.",
    "tarea_correcta": "La tarea en la que sí iba lo anotado.",
    "cerrada_con": "Con qué se había cerrado la pregunta: lo que la persona tocó o escribió no "
                   "cambió nada.",
    "cierre": "Cómo se cerró la pregunta, con su código.",
    "cuando": "El día en que pasó.",
    "aplicado": "Lo corregido, anotado en la tarea correcta: su resultado.",
    # --- Los datos de una jugada, como se entendieron del mensaje -----------------------------
    "palabras": "Lo que la persona contó de cómo viene la tarea, con sus palabras.",
    "quien": "Quién puede destrabar el bloqueo, como lo nombró la persona.",
    "que_pide": "Lo que la persona le pidió a Leda, resumido.",
    "eligio": "La opción que eligió la persona.",
    "no_se_anoto_nada": "No quedó nada anotado.",
    "pregunta_sigue_abierta": "La pregunta sigue abierta: la opción elegida ya no se podía "
                              "usar.",
    "cambios_pedidos": "Los cambios que pidió quien revisó la tarea.",
    "vence": "La fecha comprometida de la tarea (su vencimiento).",
    # --- Lo que dice un aviso que Leda manda por su cuenta ------------------------------------
    "aviso": "Qué aviso es, con su código.",
    "necesita_respuesta": "Si el aviso espera una respuesta de quien lo recibe.",
    "numero": "Qué número de pedido es, en la cuenta de pedidos sin respuesta.",
    "responsable": "La persona responsable de la tarea.",
    "prevision_vigente": "La previsión vigente de la tarea: su fecha, el atraso que tendrá si "
                         "se cumple, su porqué y el estado de su aviso al referente.",
    "fecha": "Una fecha.",
    "pide_el_estado_el": "El día en que Leda va a pedirle el estado: todavía no pasó.",
    "si_no_hay_respuesta": "Lo que pasa si la persona no contesta: a quién se le avisa. "
                           "Todavía no pasó.",
    "se_avisa_a": "A quiénes se les avisa.",
    "avance_anterior": "Lo que la persona contestó antes sin un hecho cierto, y cuándo.",
    "el": "El día en que pasó.",
    "espera_algo_cierto": "Lo que Leda necesita saber de la tarea: un hecho cierto.",
    "seguimiento_por": "Desde qué fecha corre el seguimiento: la previsión, si es posterior al "
                       "vencimiento.",
    "pedido_desde": "Desde cuándo se le pide el estado sin respuesta.",
    "pedidos_de_estado_sin_respuesta": "Cuántos pedidos de estado le llegaron a la persona sin "
                                       "que contestara.",
    "pedidos_anteriores_que_no_le_llegaron": "Pedidos anteriores que no le llegaron a la "
                                             "persona: no se le habla como si los hubiera "
                                             "recibido.",
    "pedidos_de_estado_que_no_le_llegaron": "Pedidos de estado que no le llegaron a la "
                                            "persona.",
    "avance_sin_algo_cierto": "Lo que la persona contestó antes sin un hecho cierto.",
    "ausencia": "La ausencia de la persona, con desde y hasta.",
    "desde": "Desde cuándo.",
    "hasta": "Hasta cuándo.",
    "sobre": "Lo anotado sobre lo que se pregunta.",
    "preguntas_sin_respuesta": "Cuántas veces se hizo la pregunta sin respuesta.",
    "preguntado_el": "Cuándo se hizo la pregunta por primera vez.",
    "lo_pendiente": "Lo que tenía el aviso que no salió.",
    "aviso_que_no_salio": "El aviso que no pudo salir: a quién iba y qué era.",
    # --- Códigos: cómo terminó una jugada ------------------------------------------------------
    "anotado": "Quedó anotado.",
    "falta_dato": "No se hizo: falta un dato (falta dice cuál).",
    "no_se_puede": "No se hizo: no se puede ahora (motivo dice por qué).",
    "no_por_chat": "Leda lo reconoce pero no lo hace por chat (motivo dice por qué).",
    "leido": "Se leyó de la base.",
    "corregido": "Se corrigió: lo anotado antes ya no vale.",
    "cancelado": "La pregunta quedó sin efecto, sin anotar nada.",
    "sin_efecto": "No tuvo efecto: no cambió nada.",
    "elegida": "La opción quedó elegida.",
    "fuera_de_la_lista": "Lo pedido no está en la lista de lo que Leda hace: no se hizo nada.",
    # --- Códigos: por qué no se hizo o no salió ------------------------------------------------
    "tarea_desconocida": "La tarea no está entre las de la persona.",
    "tarea_cerrada": "La tarea ya está cerrada.",
    "ninguna_tarea_posible": "Ninguna tarea de la persona admite esto ahora.",
    "no_autorizado": "La persona no tiene autoridad para esto.",
    "pide_otro_paso": "Esto necesita un paso que esta jugada no tiene.",
    "regla_del_trabajo": "Una regla del trabajo no lo permite.",
    "sin_fecha_comprometida": "La tarea no tiene fecha comprometida.",
    "sin_bloqueo_abierto": "La tarea no tiene un bloqueo abierto.",
    "nadie_pidio_el_estado": "Leda no le había pedido el estado de esa tarea.",
    "la_entrega_todavia_no_se_recibe_por_chat": "La entrega de una tarea todavía no se recibe "
                                                "por chat.",
    "cambiar_el_responsable_no_es_por_chat": "Cambiar quién es responsable de una tarea no se "
                                             "hace por chat.",
    "pregunta_cerrada": "La pregunta ya estaba cerrada.",
    "la_pregunta_espera_respuesta": "Esa pregunta no se puede dejar sin efecto: sigue "
                                    "esperando la respuesta.",
    "sin_opciones": "La pregunta no tiene opciones.",
    "sin_pregunta_abierta": "No hay una pregunta abierta.",
    "no_se_corrige": "Eso no se corrige.",
    "misma_tarea": "Es la misma tarea en la que ya estaba.",
    "nada_que_corregir": "No hay nada anotado que corregir.",
    "ya_se_escalo": "Ya se escaló porque no contestaba.",
    "misma_fecha_comprometida": "La previsión es la fecha comprometida: para el referente no "
                                "cambia nada.",
    "sin_referente": "La persona no tiene a alguien que apruebe su trabajo.",
    "se_anoto_en_la_tarea_equivocada": "Se había anotado en la tarea equivocada.",
    # --- Códigos: el estado de un efecto que pasa después --------------------------------------
    "guardado_sin_enviar": "Guardado, todavía sin enviar: sale cuando dice sale.",
    "en_cola_sin_enviar": "En la cola de su canal, todavía sin enviar: sale enseguida.",
    "retirado_sin_enviar": "Se retiró sin enviarse: nunca salió.",
    "enviado": "Ya salió.",
    "no_salio": "No salió.",
    "todavia_no": "Todavía no pasó.",
    "sigue_abierto": "Sigue abierto: Leda sigue esperando.",
    # --- Códigos: el estado de una tarea -------------------------------------------------------
    "asignada": "Asignada a la persona, todavía sin empezar.",
    "en_curso": "En curso: la persona la empezó.",
    "bloqueada": "Bloqueada: no puede avanzar por una causa anotada.",
    "en_revision": "Entregada, en revisión.",
    "terminada": "Terminada y aprobada.",
    "cancelada": "Cancelada: una tarea que se decidió no continuar, o una pregunta que la "
                 "persona dejó sin efecto.",
    "respondida": "La pregunta se cerró con la respuesta de la persona.",
    # --- Códigos: lo que Leda propone y lo que espera saber ------------------------------------
    "que_alguien_ayude": "Propuesta: que alguien del equipo ayude con el bloqueo.",
    "si_la_termino": "Si la persona terminó la tarea.",
    "para_cuando_la_termina": "Para qué fecha prevé terminarla.",
    "si_esta_trabada": "Si no puede avanzar con ella.",
    # --- Códigos: los tipos de pregunta (lo que la pregunta espera) ----------------------------
    "cual_tarea": "Pregunta de qué tarea habla la persona: espera que elija una.",
    "causa_del_bloqueo": "Pregunta qué traba la tarea: espera la causa.",
    "estado_de_la_tarea": "Pregunta cómo viene la tarea: espera algo cierto (si la terminó, "
                          "para cuándo o si está trabada).",
    "fecha_de_la_tarea": "Pregunta para qué día va a tener la tarea: espera una fecha.",
    "propuesta": "Leda le propuso algo a la persona: espera que elija una de las propuestas o "
                 "la deje.",
    # --- Códigos: los avisos que Leda manda por su cuenta --------------------------------------
    "aviso_previo": "Aviso de que la tarea vence pronto; no pide respuesta.",
    "vencimiento_proximo": "La tarea vence pronto; no pide respuesta.",
    "vencimiento_con_prevision": "La tarea vence hoy, pero la persona ya dio una previsión: "
                                 "no pide nada.",
    "pedido_de_estado": "Leda pide el estado de la tarea: espera algo cierto.",
    "reencuadre": "Leda retoma el seguimiento después de una ausencia.",
    "vuelta_de_ausencia": "La persona volvió de una ausencia: Leda retoma el seguimiento.",
    "escalamiento": "Aviso a quien corresponde de que la persona no contesta.",
    "falta_de_respuesta": "La persona no contestó los pedidos: se le avisa a quien "
                          "corresponde.",
    "repregunta_de_estado": "Leda vuelve a pedir el estado después de una respuesta sin un "
                            "hecho cierto.",
    "repregunta": "Leda vuelve a hacer una pregunta que no tuvo respuesta.",
    "escalamiento_de_una_pregunta": "Aviso a quien corresponde de que una pregunta quedó sin "
                                    "respuesta.",
    "nueva_prevision": "Aviso al referente: la persona responsable dio una previsión nueva "
                       "para su tarea. Es información para él; no pide respuesta.",
    "correccion_de_prevision": "Aviso al referente: una previsión que ya recibió no vale.",
    "falla_de_aviso": "Un aviso que la persona causó no pudo salir.",
    "no_salio_un_aviso": "Un aviso que la persona causó no pudo salir.",
}


def significado(nombre: str) -> str | None:
    """Qué significa una clave o un código; una jugada, por su ficha."""
    if nombre in SIGNIFICADOS:
        return SIGNIFICADOS[nombre]
    ficha = FICHAS.get(nombre)
    return f"La jugada de {ficha.para_que}." if ficha is not None else None


def _nombres(valor: Any) -> Iterator[str]:
    """Cada clave y cada código de un valor, en el orden en que aparecen."""
    if isinstance(valor, Mapping):
        for k, v in valor.items():
            yield str(k)
            yield from _nombres(v)
    elif isinstance(valor, (list, tuple)):
        for v in valor:
            yield from _nombres(v)
    elif isinstance(valor, str) and (_CODIGO.match(valor) or significado(valor) is not None):
        yield valor         # un código; uno de una sola palabra, si está en la lista


def sin_significado(valor: Any) -> set[str]:
    """Las claves y los códigos de un valor que no tienen significado."""
    return {n for n in _nombres(valor) if significado(n) is None}


def bloque(valor: Any) -> str:
    """Lo que significa cada clave y cada código de un pedido a la IA, una línea por nombre,
    sólo de lo que el pedido usa."""
    vistos = list(dict.fromkeys(n for n in _nombres(valor) if significado(n) is not None))
    return "\n".join(["Lista de significados de los datos y códigos de este pedido:"]
                     + [f"- {n}: {significado(n)}" for n in vistos])
