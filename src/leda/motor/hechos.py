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

Los significados describen datos, no casos: qué es cada cosa, nunca qué decir con ella. Y lo
que pasa después se describe como pasa en el mundo (usuario, 2026-10-06, de la prueba por
Telegram real): a quién le llega qué y cuándo (`llega`), nunca el estado interno de un aviso
(guardado, en cola, sin enviar), que la IA repetía. Y con palabras de todos los días (usuario,
2026-10-07, de la prueba por Telegram real: "que es prevision?"): un significado dice qué es el
dato para la persona (el día que dio para terminar, el día en que vence, quien aprueba su
trabajo), nunca el nombre del concepto en la cocina, que la IA repetía como palabra.

Con los significados reescritos, la IA seguía escribiendo "si se cumple esa previsión"
(usuario, 2026-10-07): el pedido de redacción traía el concepto en los nombres de sus claves,
de sus códigos y de las jugadas. Los nombres de la cocina no cambian (la base, las fichas, los
hechos guardados y el pedido para elegir jugadas, donde la IA elige por nombre); en el borde,
la redacción recibe cada uno que nombra un concepto (`CONCEPTOS_DE_LA_COCINA`) cambiado por el
que dice el hecho (`PARA_LA_REDACCION`, `para_redactar`), con el mismo significado.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Mapping
from datetime import date, timedelta
from typing import Any

from .. import salida
from ..incidentes import registrar_incidente
from .fichas import FICHAS

# Un código: minúsculas y cifras, con al menos un guion bajo (un texto libre lleva espacios).
_CODIGO = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)+$")

SIGNIFICADOS: Mapping[str, str] = {
    # --- Lo que recibe la IA en cada pedido ----------------------------------------------------
    "hoy": "La fecha de hoy, en la hora del equipo.",
    "dias": "El día de la semana de cada fecha de este pedido (para elegir jugadas, también "
            "de los próximos días; para escribir un mensaje, en la forma corta con que se "
            "escribe) y, si corresponde, si es hoy, ayer, mañana o pasado mañana. Lo da el "
            "código: se usa tal cual, nunca se calcula.",
    "persona": "A quién le escribe Leda.",
    "mensaje": "Lo que la persona escribió ahora; vacío si no escribió nada (tocó una opción "
               "o mandó sólo fotos o archivos) o si Leda escribe por su cuenta.",
    "toco": "La opción que la persona tocó, en lugar de escribir.",
    "hechos": "Lo que el sistema hizo, comprobó o necesita en este turno: lo único que vale "
              "como hecho.",
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
    "estado": "El estado de una tarea; como motivo, que el estado de la tarea no lo permite; "
              "o, para elegir jugadas, la pregunta abierta y las que quedaron para después.",
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
    "fecha_objetivo": "El día y la hora en que vence la tarea.",
    "tipo": "El tipo de una pregunta o de un aviso, con su código.",
    "opciones": "Las opciones de una pregunta: salen como botones y también se pueden "
                "contestar escribiendo.",
    "opcion": "El alias de una opción.",
    "etiqueta": "Lo que dice una opción, como la ve la persona.",
    "propone": "Lo que Leda le propuso a la persona para que elija.",
    "opcional": "Lo que Leda propone es por si la persona lo necesita: si no lo toma, no pasa "
                "nada y Leda no vuelve a ofrecerlo.",
    "desde_antes": "La pregunta ya se había hecho en un mensaje anterior: se vuelve a esa pregunta sin "
                   "pedir que se repita lo que la persona ya dijo.",
    # --- Lo que la persona mandó con su mensaje (ADR 0019, decisión 4) --------------------------
    "archivos": "Las fotos, videos o archivos que la persona mandó con este mensaje. El "
                "sistema sabe qué llegó y nunca su contenido: qué muestra una foto o qué dice "
                "un archivo no se sabe.",
    "que_llego": "Qué llegó: una foto, un video o un archivo.",
    "nombre_del_archivo": "El nombre con que llegó, tal como lo puso quien lo mandó.",
    "no_se_pudo_recibir": "Por qué no se pudo recibir lo que llegó, con su código: para el "
                          "sistema es como si no hubiera llegado.",
    "limite_mb": "El tamaño máximo que se puede recibir, en megabytes.",
    "en_cambio_puede": "Lo que la persona puede hacer en lugar de eso, para que elija.",
    "demasiado_grande": "Es más grande de lo que se puede recibir.",
    "tipo_no_admitido": "Es de un tipo de archivo que no se recibe (por ejemplo, un programa "
                        "o una página web).",
    "mandar_uno_mas_chico": "Mandar uno más chico o más corto.",
    "mandar_un_enlace": "Mandar un enlace para verlo o bajarlo de otro lado (por ejemplo, de "
                        "una carpeta compartida).",
    "contenido_retirado": "Es un archivo que la administración de Leda ya retiró: no se vuelve "
                          "a recibir.",
    "mandar_otro": "Mandar otra foto u otro archivo en su lugar.",
    # --- La entrega de una tarea con su evidencia (ADR 0019, decisiones 4 y 5) -----------------
    "evidencia_que_pide": "Lo que la tarea pide para entregarla, cada cosa con su código (para "
                          "nombrarla en una jugada) y cómo se le dice a la persona.",
    "tipo_de_evidencia": "El código de una cosa que pide la tarea para entregarla: sirve para "
                         "nombrarla en una jugada; a la persona se le dice con sus palabras.",
    "en_palabras": "Cómo se le dice a la persona esa cosa que pide la tarea.",
    "el_texto_cubre": "Los códigos de lo que pide la tarea que la persona describe con lo que "
                      "escribió (por ejemplo, cómo quedó y cómo lo probó).",
    "saca": "Las piezas (por su alias) que la persona saca de su entrega.",
    "entrega": "La entrega de la tarea, pieza por pieza, como se le muestra a la persona: lo "
               "que escribió, cada foto, video, archivo o enlace y lo que mandó antes durante la "
               "tarea, que entra sólo si lo deja.",
    "lo_mostrado": "Lo que Leda le mostró a la persona con esa pregunta: las piezas de la "
                   "entrega, con su alias.",
    "lo_entregado": "Lo que la persona ya entregó de esa tarea, pieza por pieza, con su alias "
                    "(para sacar una).",
    "pieza": "El alias de una pieza de la entrega (P1, P2...): es interno, nunca se le muestra "
             "a la persona.",
    "es": "Qué es la pieza, con su código.",
    "dice": "Lo que la persona escribió en esa pieza, tal cual.",
    "enlace": "El enlace que mandó la persona, tal cual.",
    "cubre": "Lo que pide la tarea que cubre esa pieza, en palabras de todos los días. Una "
             "pieza que no cubre nada va igual en la entrega.",
    "mandado_antes_el": "La pieza la mandó antes, durante la tarea, ese día: entra en la "
                        "entrega sólo si la persona la deja.",
    "le_falta": "Lo que pide la tarea y todavía no está en la entrega, en palabras de todos "
                "los días.",
    # --- Lo descrito frente al criterio de aceptación (decisión 10 del usuario, 2026-10-08) ----
    "criterio_de_aceptacion": "Lo que tiene que cumplir la tarea para darla por terminada, "
                              "punto por punto, como lo escribió quien la cargó: lo que la "
                              "persona describe al entregarla tiene que decirlo.",
    "punto": "El código de un punto del criterio de aceptación (C1, C2...): sirve para "
             "nombrarlo en una jugada; nunca se le muestra a la persona.",
    "lo_que_pide": "Lo que pide ese punto del criterio de aceptación, tal cual está escrito.",
    "lo_descrito_cubre": "Los códigos de los puntos del criterio de aceptación que dice lo que "
                         "la persona describió en la entrega, contando lo que sigue valiendo de "
                         "la entrega anterior (la_entrega_anterior).",
    "la_entrega_anterior": "Lo que la persona describió en la entrega anterior de esta tarea, "
                           "antes de que le pidieran cambios, y lo que pidió el pedido de "
                           "cambios (cambios_pedidos): sigue contando como lo que describe, "
                           "salvo lo que el pedido de cambios pide cambiar.",
    "lo_que_describio": "Los textos de esa entrega, cada uno con lo que dice y los puntos del "
                        "criterio que describía.",
    "acepta_el_ejemplo": "Si la persona aceptó, tal cual, el ejemplo que Leda le propuso para "
                         "describir lo que falta de la entrega.",
    "describe": "Los puntos del criterio de aceptación que dice lo que la persona escribió en "
                "esa pieza, como se leyó: la persona lo ve en la entrega y lo puede corregir.",
    "le_falta_del_criterio": "Los puntos del criterio de aceptación que la descripción de la "
                             "persona todavía no dice entero, tal cual están escritos. De cada "
                             "uno, lo que falta saber de la tarea es la parte que la descripción "
                             "no dice; lo demás del criterio ya está dicho.",
    "ejemplo": "Una descripción de lo que falta del criterio de aceptación, sacada del criterio "
               "y de lo que la persona ya dijo, sin ningún dato nuevo. Leda se la propone tal "
               "cual, como ejemplo: la persona la acepta o escribe la suya; mientras no la "
               "acepte, no es parte de la entrega.",
    "arranca_al_entregarla": "La tarea no figura como arrancada: al confirmar la entrega, la "
                             "historia dice que arrancó y se entregó en ese momento, sin otra "
                             "fecha de inicio.",
    "arranco_al_entregarla": "La tarea no figuraba como arrancada: la historia dice que arrancó "
                             "y se entregó en este momento, sin otra fecha de inicio.",
    "espera_otras_tareas": "La tarea no puede arrancar porque espera que terminen otras de las "
                           "que depende: así no se entrega, y no cambió nada.",
    "le_falta_algo": "La persona pidió que la entrega vaya así, pero le falta algo de lo que "
                     "pide la tarea (como_queda y lo que falta dicen qué).",
    "al_confirmar": "Lo que pasa cuando la persona confirme la entrega completa.",
    "queda_esperando_la_aprobacion_de": "Quién revisa la tarea entregada y decide si la aprueba "
                                        "o le pide cambios: hasta que decida, la tarea está en "
                                        "revisión.",
    "aviso_a_quien_aprueba": "Lo que se le avisa a quien revisa la tarea entregada: a quién (a) "
                             "y cuándo se entera (llega).",
    "lo_que_entrego": "Lo que entregó la persona responsable, pieza por pieza: lo que escribió, "
                      "cada foto, video, archivo o enlace, y lo que cubre de lo que pide la "
                      "tarea. El sistema sabe qué llegó y nunca su contenido: qué muestra una "
                      "foto o qué dice un archivo no se sabe.",
    "va_adjunta": "Si esa foto va adjunta, en un mensaje aparte que sale enseguida después de "
                  "éste. Lo que no va adjunto sólo se nombra: está con la entrega.",
    "fotos_adjuntas": "Cuántas fotos van adjuntas, en un mensaje aparte que sale enseguida "
                      "después de éste.",
    "la_revision_espera": "La persona sacó algo después de entregarla y a la entrega le falta "
                          "lo que se dice: mientras falte, la revisión espera; cuando esté "
                          "completa, quien la revisa recibe un aviso nuevo con todo.",
    "entrega_completa": "La entrega de la tarea, que ya estaba en revisión, quedó completa otra "
                        "vez: sigue en revisión, y quien la revisa recibe un aviso nuevo con "
                        "todo lo entregado.",
    "la_entrega_esta_incompleta": "A la entrega le falta algo porque la persona sacó una pieza "
                                  "después de entregarla: la revisión espera a que se complete.",
    "la_entrega_esta_incompleta_por_un_retiro_de_la_administracion": (
        "A la entrega le falta algo porque la administración de Leda retiró una pieza después "
        "de entregarla: la revisión espera a que la persona responsable mande una pieza nueva. "
        "Quién de la administración la retiró no se sabe."),
    "sumo": "Las piezas (por su alias) que se sumaron a la entrega con este mensaje.",
    "sacadas": "Las piezas que la persona sacó de la entrega antes de confirmarla: no van.",
    "retiradas": "Las piezas ya entregadas que la persona retiró: dejan de valer, nada se "
                 "borra.",
    # --- Lo que retira la administración (decisión 58 del usuario, 2026-10-10; porción 5b) ----
    "contenido_retirado_por_la_administracion": "Aviso a quien entregó una o más piezas de una "
                                                "entrega: la administración de Leda las "
                                                "retiró, por el motivo que dio "
                                                "(motivo_del_retiro), y dejaron de contar para "
                                                "la entrega. Quién de la administración lo hizo "
                                                "no se sabe. No pide respuesta.",
    "motivo_del_retiro": "Por qué la administración de Leda retiró esas piezas, como lo "
                         "escribió.",
    "piezas_retiradas_por_tarea": "De cada tarea, las piezas que se retiraron y, si su entrega "
                                  "está en revisión y quedó sin cubrir, lo que falta para que "
                                  "la revisen.",
    "piezas_retiradas": "Las piezas que se retiraron de esa tarea: qué era cada una, qué cubría "
                        "y qué día la entregó la persona. Su contenido ya no está.",
    "cubria": "Lo que pide la tarea que cubría esa pieza, en palabras de todos los días.",
    "la_entrego_el": "El día en que la persona entregó esa pieza.",
    "la_revision_espera_otra_pieza": "La entrega de esa tarea, que está en revisión, quedó sin "
                                     "algo de lo que pide (le_falta, le_falta_del_criterio): la "
                                     "revisión espera a que la persona lo mande; con eso, quien "
                                     "la revisa recibe un aviso nuevo con todo.",
    "la_entrega_espera_otra_pieza": "Aviso a quien revisa una entrega: la administración de "
                                    "Leda retiró una pieza y a la entrega le falta algo de lo "
                                    "que pide la tarea (le_falta, le_falta_del_criterio). La "
                                    "revisión espera a que la persona responsable lo mande; "
                                    "cuando esté completa, le llega un aviso nuevo con todo. No "
                                    "pide respuesta.",
    "entregas_que_esperan_otra_pieza": "Las entregas que esperan una pieza nueva, cada una con "
                                       "su tarea, su responsable y lo que le falta.",
    "ya_esta_aprobada": "La tarea ya está aprobada o cerrada: el retiro no le cambia nada.",
    "la_entrega_ya_esta_completa": "La entrega ya tiene otra vez todo lo que pide la tarea: "
                                   "quien la revisa recibe la entrega completa en su propio "
                                   "aviso.",
    "referencias": "Referencias internas del sistema: nunca se le muestran ni se le dicen a la "
                   "persona.",
    "como_queda": "Cómo queda lo que se confirmaba (la entrega o el pase) después de esto, con "
                  "su código.",
    "reemplazada": "Esa vista de la entrega dejó de valer porque cambió lo que mostraba: la "
                   "reemplazó otra.",
    "para_cuando_la_entregue": "Lo que la persona mandó y queda en la conversación para "
                               "mostrárselo cuando entregue esa tarea: no es parte de una "
                               "entrega todavía.",
    "le_ofrece_entregarla_con_esto": "A la tarea le pidieron cambios: con lo que mandó, Leda le "
                                     "ofrece volver a entregarla, con la entrega como se le "
                                     "muestra (entrega), lo que le falta si le falta algo y lo "
                                     "que pasa al confirmarla. No se entrega sin su sí; lo que "
                                     "mandó sigue con la tarea para cuando la entregue.",
    "lo_que_escribio": "Lo que escribió quien entrega la tarea: su descripción del trabajo.",
    "el_ejemplo_que_acepto": "Una descripción que Leda le propuso a quien entrega la tarea "
                             "para lo que faltaba y que esa persona aceptó tal cual: vale como "
                             "lo que describe; la aceptó, no la escribió.",
    "una_foto": "Una foto.",
    "un_video": "Un video.",
    "un_archivo": "Un archivo.",
    "un_enlace": "Un enlace.",
    "para_confirmar": "La entrega tiene todo lo que pide la tarea: espera que la persona la "
                      "confirme, con el botón o escribiendo.",
    "le_falta_evidencia": "A la entrega le falta algo de lo que pide la tarea: le_falta y "
                          "le_falta_del_criterio dicen qué.",
    "entregada": "La tarea quedó entregada y pasa a revisión, el paso que sigue a toda "
                 "entrega: quien aprueba el trabajo de la persona la revisa y decide si la "
                 "aprueba o le pide cambios; hasta entonces, no queda terminada.",
    "no_vale_la_confirmacion": "La confirmación no vale (motivo dice por qué) y se muestra otra "
                               "vez lo que se confirmaba, la entrega o el pase, como quedó "
                               "(como_queda).",
    "llego_algo_despues": "Llegó algo nuevo para la entrega después de mostrarla: lo que la "
                          "persona confirmaba ya no era lo último.",
    "cambio_lo_que_se_mostro": "Lo que se le mostró a la persona cambió desde entonces.",
    "no_es_lo_ultimo_que_vio": "Lo que se confirmaría no es lo último que la persona vio en "
                               "un mensaje anterior.",
    "nada_para_confirmar": "No hay nada mostrado que esté esperando una confirmación.",
    "sin_archivos": "El mensaje no trajo ningún archivo para dejar.",
    "ya_aprobada": "La tarea ya está aprobada: lo entregado ya no se saca.",
    "confirmar_la_entrega": "Pregunta si la persona entrega la tarea así: espera que la "
                            "confirme (con el botón o escribiendo) o que saque o corrija algo.",
    "lo_que_falta_de_la_entrega": "Espera lo que le falta a la entrega de la tarea.",
    # --- La decisión de quien aprueba una entrega (circuito 8; porción 3b de la C-3) -----------
    "para_decidir": "Una tarea de otra persona, entregada, que espera que la persona que "
                    "escribe la revise y decida: la apruebe o le pida cambios. No es una tarea "
                    "suya.",
    "ya_la_aprobo_el": "La persona que escribe ya la aprobó ese día: espera que se resuelva lo "
                       "que falta para cerrarse, sin otra aprobación.",
    "comentario": "Lo que dijo quien decide sobre la entrega, con sus palabras: en un pedido de "
                  "cambios, lo que falta o hay que cambiar; en una aprobación, algo que le pasa "
                  "a la persona responsable para que lo tenga en cuenta, que no es un cambio "
                  "pendiente: la tarea queda aprobada igual.",
    "de": "La persona cuyo trabajo se aprueba o se devuelve, como la nombró quien escribe.",
    "quien_aprueba": "Quién aprueba el trabajo de esa persona: quien decide sobre su entrega.",
    "quedo_terminada": "La tarea quedó terminada: aprobada y con todo lo demás que pide el "
                       "cierre, comprobado por el sistema.",
    "no_se_cierra_todavia": "La aprobación quedó anotada, pero la tarea todavía no queda "
                            "terminada: lo que falta para cerrarla, según el sistema.",
    "espera_que_terminen": "Las tareas que tienen que terminar antes de que ésta pueda "
                           "cerrarse, con su estado y su responsable.",
    "bloqueos_abiertos": "Lo que traba la tarea, como lo dijo la persona responsable: mientras "
                         "siga, no se cierra.",
    "falta_el_criterio_de_aceptacion": "A la tarea le falta decir qué tiene que cumplir para "
                                       "darla por terminada: así no se cierra.",
    "falta_algo_mas": "Falta algo más para cerrarla, que el sistema no detalla.",
    "se_cierra_sola": "Cuando se resuelva lo que falta, el sistema la cierra solo, sin otra "
                      "aprobación, y se les avisa a esas personas (se_avisa_a). Todavía no "
                      "pasó.",
    "aviso_al_responsable": "Lo que se le avisa a la persona responsable de la tarea: a quién "
                            "(a) y cuándo se entera (llega).",
    "lecturas": "Las dos cosas que puede querer decir el mensaje sobre la misma tarea: no se "
                "hizo ninguna y Leda consulta cuál.",
    "aprobada_por": "Quién aprobó la tarea.",
    "aprobada_el": "El día en que quien aprueba dio esa aprobación.",
    "pidio_cambios": "Quién le pidió cambios a la entrega.",
    "puede_volver_a_entregarla": "La persona responsable la vuelve a entregar cuando tenga lo "
                                 "que le pidieron.",
    "se_resolvio": "Lo que faltaba para cerrar la tarea y ya se resolvió.",
    "tareas_que_esperaba": "Las tareas que tenían que terminar antes de que ésta se cerrara, "
                           "con el estado en que quedaron.",
    "bloqueos_que_se_cerraron": "Lo que trababa la tarea y ya se resolvió.",
    "dos_lecturas": "El mensaje se puede leer de dos formas sobre la misma tarea (lecturas): "
                    "dice a la vez dos cosas opuestas, o aprueba con un comentario que le pide "
                    "algo a alguien. No se hizo ninguna y Leda consulta cuál de las dos.",
    "el_comentario_pide_algo": "Si el comentario de la aprobación le pide a la persona "
                               "responsable o a otra persona que haga o revise algo.",
    "su_propio_trabajo": "Es trabajo de la persona que escribe: no lo puede aprobar ni devolver "
                         "ella; lo decide quien aprueba su trabajo.",
    "no_es_quien_aprueba": "La persona que escribe no es quien aprueba ese trabajo: lo decide "
                           "otra persona (quien_aprueba), y no cambió nada.",
    "nada_para_decidir": "No hay una entrega de esa persona esperando la decisión de quien "
                         "escribe.",
    "persona_desconocida": "No hay nadie en el equipo con ese nombre.",
    "nombre_que_no_esta": "El nombre, como lo dijo la persona, que no es de nadie del equipo.",
    # --- Quién es alguien que nombró (ADR 0020; `apodos.py`) --------------------------------
    "quien_es": "Quién es la persona que nombró la persona que escribe: el nombre que dice, "
                "como lo dice.",
    "de_afuera": "Verdadero si la persona que escribe dice que a quien nombró no es del equipo.",
    "como_lo_nombro": "Cómo nombró la persona que escribe a alguien, con sus palabras: es lo que "
                      "dijo, nunca el nombre de nadie, y se cita entre comillas.",
    "quien_es_esa_persona": "Pregunta quién es alguien que nombró la persona (como_lo_nombro), "
                            "porque no hay nadie así en el equipo; lo que pidió espera la "
                            "respuesta y todavía no se hizo.",
    "confirmar_quien_es_esa_persona": "Pregunta si la persona del equipo que Leda reconoce "
                                      "(integrante, con nombre y apellido) es a quien nombró "
                                      "(como_lo_nombro); con su confirmación, Leda lo recuerda y "
                                      "hace lo que pidió.",
    "cual_de_esas_personas": "Pregunta a cuál de las personas del equipo (las opciones, con "
                             "nombre y apellido) se refería quien escribe con lo que dijo "
                             "(como_lo_nombro): son varias y Leda no elige.",
    "quien_es_para_confirmar": "Leda reconoce a la persona del equipo que dijo quien escribe "
                               "(integrante) y espera su confirmación: todavía no recuerda nada "
                               "ni hizo lo que pidió.",
    "aprendio_como_le_dicen_a": "La persona del equipo, por su nombre, que desde ahora Leda "
                                "también reconoce como la nombró quien escribe: lo confirmó esa "
                                "persona.",
    # --- De quién es un apodo, dicho sin que Leda lo pregunte (decisión 67) --------------------
    "apodo": "Un apodo, como lo dijo la persona que escribe.",
    "a_quienes_les_dicen_asi": "Pregunta si a todas las personas a las que ya les dicen así "
                               "(ya_le_dicen_asi_a) y a la que nombró quien escribe (integrante) "
                               "les dicen como lo dijo (como_lo_nombro), o sólo a esta: Leda no "
                               "cambia nada sin la respuesta.",
    "ya_le_dicen_asi_a": "A quiénes del equipo, por su nombre, Leda ya reconoce como lo dijo "
                         "quien escribe.",
    "sigue_reconociendo_asi_a": "A quiénes del equipo, por su nombre, Leda sigue reconociendo "
                                "también así.",
    "dejo_de_reconocer_asi_a": "A quiénes del equipo, por su nombre, Leda deja de reconocer "
                               "así desde ahora, porque lo dijo quien escribe.",
    "ya_lo_reconocia_asi": "Leda ya reconocía así a esa persona (integrante), y a nadie más: no "
                           "cambió nada.",
    "ya_la_aprobo": "La persona que escribe ya la había aprobado: no se anota otra vez.",
    "la_entrega_se_esta_completando": "La persona responsable sacó algo de lo que entregó y "
                                      "está completando la entrega: así todavía no se aprueba "
                                      "y no cambió nada.",
    "la_entrega_espera_lo_que_retiro_la_administracion": "La administración de Leda retiró una "
                                                         "pieza de lo que entregó la persona "
                                                         "responsable, y a la entrega le falta "
                                                         "lo que cubría: la revisión espera a "
                                                         "que la persona mande una pieza nueva. "
                                                         "Así todavía no se aprueba y no cambió "
                                                         "nada. Quién de la administración la "
                                                         "retiró no se sabe.",
    "se_le_avisa_cuando_este_completa": "Cuando la entrega esté completa, a quien la revisa le "
                                        "llega un aviso nuevo con todo. Todavía no pasó.",
    "cambio_la_entrega": "La entrega cambió desde el aviso que tenía ese botón: el botón ya no "
                         "vale; se decide sobre lo que vale ahora.",
    "decision_de_la_entrega": "Pregunta qué decide quien revisa la entrega, después de "
                              "revisarla: aprobarla o pedirle cambios; lo puede tocar o "
                              "escribir.",
    "que_cambios_pide": "Pregunta qué le falta o qué hay que cambiar de la entrega: espera lo "
                        "que pide quien la aprueba.",
    "cual_de_las_dos": "Pregunta, una sola vez, cuál de las dos cosas quiso decir la persona "
                       "sobre la tarea: su respuesta elige una (una opción, o esa decisión "
                       "escrita), y lo demás que diga es su comentario, no la otra cosa. Si no "
                       "elige, no se vuelve a consultar.",
    "no_eligio": "La persona contestó sin elegir ninguna opción de una pregunta que Leda hace "
                 "una sola vez: Leda no decide por ella ni lo vuelve a consultar. Lo que esperaba "
                 "esa decisión sigue esperándola, y las opciones van como botones en este mensaje "
                 "(botones), para cuando quiera; también lo puede escribir.",
    "pregunta_hecha_una_vez": "La pregunta, ya hecha, que no se vuelve a hacer: su tipo.",
    "botones": "Los botones que lleva este mensaje, por lo que dicen: atajos para cuando la "
               "persona quiera, que también se pueden escribir. No son una pregunta que espere "
               "respuesta.",
    # --- Las entregas en listas (decisión 17 del usuario, 2026-10-08; C-3d, D4) --------------
    "queda_por_revisar": "Las otras entregas que esperan la revisión de la persona que escribe, "
                         "cada una con quién la entregó: le quedan por revisar. Leda no insiste "
                         "hoy: se las recuerda el día de se_las_recuerda_el.",
    "se_las_recuerda_el": "El día hábil en que Leda le recuerda a la persona lo que le queda por "
                          "revisar. Todavía no pasó.",
    "fotos_que_trae": "Cuántas fotos trae esa entrega: se ven al abrirla con su botón; en este "
                      "mensaje no van.",
    "ver_la_entrega": "El botón que muestra la entrega de una tarea que espera la revisión de la "
                      "persona.",
    # --- Si cambia quién aprueba (decisión 16 del usuario, 2026-10-08; C-3d, D4) --------------
    "antes_la_revisaba_otra_persona": "La entrega ya esperaba la revisión de otra persona: ahora "
                                      "la revisa y la decide la persona que recibe este aviso.",
    "ya_no_le_corresponde": "La tarea ya no está entre las de la persona ni entre las que "
                            "esperan su decisión (cambió quién la tiene o quién la revisa, o ya "
                            "se decidió): no cambió nada. estado dice cómo está ahora.",
    "la_revisa_otra_persona": "La entrega sigue esperando una revisión, pero ya no la de la "
                              "persona que escribe: la revisa otra.",
    "tarea_aprobada": "Aviso a la persona responsable: quien aprueba su trabajo aprobó la "
                      "tarea. No pide respuesta.",
    "pedido_de_cambios": "Aviso a la persona responsable: quien aprueba su trabajo le pidió "
                         "cambios a la entrega, con lo que pidió. No pide respuesta.",
    "cerrada_con_la_aprobacion": "Aviso de que la tarea quedó terminada sola con la aprobación "
                                 "que ya tenía, porque se resolvió lo que faltaba. No pide "
                                 "respuesta.",
    "hay_una_decision_mas_nueva": "Después de esa aprobación, quien aprueba pidió cambios: ya "
                                  "no vale.",
    "se_cerro_despues": "La tarea quedó terminada después: otro aviso lo cuenta.",
    # --- Quien aprueba no contesta (porción 3c de la C-3) ------------------------------------
    "recordatorio_de_la_decision": "Leda le recuerda a quien aprueba que una entrega espera su "
                                   "revisión y su decisión: aprobarla o pedirle cambios; lo "
                                   "puede contestar escribiendo.",
    "veces_que_se_lo_recuerda": "Cuántas veces, contando ésta, Leda le recuerda a quien aprueba "
                                "que esa entrega espera su decisión.",
    "entregada_el": "El día en que la persona responsable entregó la tarea.",
    "si_sigue_sin_decidir": "Lo que va a pasar si quien aprueba sigue sin decidir: a quién se le "
                            "avisa (se_avisa_a), sólo para que lo sepa, y qué día (fecha). "
                            "Todavía no pasó.",
    "aprobacion_trabada": "Aviso a quien aprueba el trabajo de quien aprueba una entrega: esa "
                          "entrega espera desde hace días la revisión de quien_aprueba. Es sólo "
                          "para que lo sepa: no le pide nada y no la decide él; la decide "
                          "quien_aprueba. No pide respuesta.",
    "leda_se_lo_sigue_recordando": "Leda le sigue recordando a quien aprueba, un día hábil por "
                                   "vez, que la entrega espera su decisión.",
    "se_le_avisa_cuando_decida": "Cuando quien aprueba decida sobre la entrega, Leda se lo "
                                 "avisa a la persona a la que le escribe. Todavía no pasó.",
    "se_le_avisa_si_hace_falta_algo_mas": "Si quien revisa la entrega pide cambios porque hace "
                                          "falta algo más, Leda se lo avisa a la persona a la "
                                          "que le escribe, con lo que hace falta. Todavía no "
                                          "pasó.",
    "aprobacion_destrabada": "Aviso a quien sabía que una entrega esperaba la revisión de "
                             "quien_aprueba: ya decidió. No pide respuesta.",
    "aviso_de_que_se_destrabo": "Lo que se le avisa a quien sabía que esa entrega esperaba "
                                "esta decisión: a quién (a) y cuándo se entera (llega).",
    "ya_decidio": "Quien aprueba ya decidió sobre esa entrega.",
    "cambio_quien_esta_arriba": "Cambió quién aprueba el trabajo de quien aprueba la entrega.",
    # --- Lo que dice un hecho ------------------------------------------------------------------
    "jugada": "Qué entendió el sistema que dijo o pidió la persona (una jugada de la lista); "
              "dentro de un aviso, la jugada que lo causó.",
    "resultado": "Cómo terminó la jugada, con su código.",
    "tarea": "La tarea de la que se habla: por su alias para elegir jugadas; por su título en "
             "lo que se le dice a la persona.",
    "falta": "Los datos que faltan para poder hacer la jugada.",
    "puede_ser": "Las respuestas que sirven para el dato que falta.",
    "coinciden": "Los nombres que coinciden con lo que dijo la persona, cuando es más de uno.",
    "motivo": "Por qué: con el día que la persona dio para terminar una tarea, el porqué que "
              "dio, con sus palabras; en algo que no se hizo o que ya no va a pasar, la razón, "
              "con su código.",
    "causa": "Lo que traba la tarea, como lo dijo la persona.",
    "prevision": "El día que la persona dijo que va a terminar la tarea. No cambia el día en "
                 "que vence.",
    "fecha_comprometida": "El día en que vence la tarea. Que la persona diga otro día para "
                          "terminarla no lo cambia.",
    "atraso_dias_habiles": "Los días hábiles que la tarea lleva atrasada hoy, contados desde "
                           "el día en que venció.",
    "atraso_si_se_cumple_la_prevision_dias_habiles":
        "Los días hábiles de atraso que tendrá la tarea si se cumple el día que la persona dio "
        "para terminarla, contados desde el día en que vence hasta ése. No es el atraso de hoy: "
        "hoy la tarea puede no estar atrasada.",
    "dias_habiles_hasta_el_vencimiento": "Los días hábiles que faltan hasta el día en que "
                                         "vence la tarea.",
    "dependientes": "Las tareas abiertas que dependen de ésta.",
    "espera_a": "Las tareas que tienen que terminar antes de que ésta pueda arrancar, con su "
                "estado: ésta no puede arrancar todavía.",
    "estado_desde": "Desde qué día la tarea está en su estado, según lo que anotó Leda; "
                    "desconocido si Leda no lo anotó.",
    "desconocido": "El sistema no lo sabe.",
    "no_puede_arrancar_hasta_que_termine": "Esa otra tarea no puede arrancar hasta que termine "
                                           "ésta.",
    "aviso_al_referente": "Lo que se le avisa a quien aprueba el trabajo de la persona: a quién "
                          "(a) y cuándo se entera (llega); vacío si no se le avisa.",
    "sin_aviso": "Por qué no se le avisa a quien aprueba el trabajo de la persona, con su "
                 "código.",
    "espera_el_motivo": "El aviso espera el porqué que Leda le consultó a la persona: si lo "
                        "da antes, sale otro aviso que lo lleva; si no, sale a la hora de "
                        "llega y dice que todavía no lo dio.",
    "sin_motivo_todavia": "La persona todavía no dio el porqué de ese día: Leda se lo "
                          "consultó y espera la respuesta. No hay un porqué que contar.",
    "a": "A quién va un aviso.",
    "llega": "Cuándo se entera quien recibe el aviso (el dato dice a quién va; si no lo dice, "
             "la persona a la que Leda le escribe): una fecha es el día en que le llega, que "
             "todavía no pasó; si no, su código dice si ya le llegó, si no le va a llegar o si "
             "no le llegó.",
    "quien_destraba": "Quién puede destrabar el bloqueo: como dato, lo que dijo la persona; "
                      "como tipo de pregunta, Leda consulta quién lo puede destrabar y espera "
                      "un nombre, que no sabe, o que le toca a la persona que escribe "
                      "(nunca a Leda).",
    "integrante": "Una persona del equipo.",
    "externo": "Alguien de afuera del equipo, como lo nombró la persona.",
    "no_sabe": "La persona dijo que no sabe quién puede destrabarlo.",
    "nadie_mas": "La persona que escribe dijo que nadie más puede destrabarlo: le toca a "
                 "quien escribe, nunca a Leda.",
    "salidas": "Lo que Leda le propone a la persona para salir de un bloqueo, para que elija.",
    "bloqueo_resuelto": "El bloqueo que quedó cerrado porque la persona dijo que su causa ya no "
                        "está, con esa causa: la tarea ya no está trabada por eso.",
    "causas": "Las causas de los bloqueos abiertos de la tarea, como las dijo la persona.",
    "avance": "Lo que la persona contó de cómo viene la tarea, sin un hecho cierto.",
    "dijo": "Lo que dijo la persona, con sus palabras.",
    "el_pedido_de_estado": "Si Leda sigue esperando saber cómo viene la tarea.",
    "vuelve_a_pedir_el_estado": "Cuándo Leda le vuelve a consultar a la persona cómo viene "
                                "la tarea (llega, todavía no pasó); o que ya no se lo va a "
                                "consultar, y motivo dice por qué.",
    "veces_sin_algo_cierto": "Cuántas respuestas seguidas sin un hecho cierto tuvo esta "
                             "consulta de cómo viene la tarea.",
    "no_vuelve_a_pedir_el_estado": "Por qué Leda no le vuelve a consultar cómo viene la tarea.",
    "escalado_a": "A quiénes se les avisó que la persona no contestaba, y si les llegó "
                  "(llega).",
    "vencida": "La tarea pasó el día en que vencía y, si la persona había dado un día "
               "posterior para terminarla, también ése: el día en que vencía, el atraso de hoy "
               "y el otro día, si lo había.",
    "prevision_vencida": "El día que la persona había dado para terminarla, que también pasó.",
    "quien_decide": "Quién decide lo que la persona pidió.",
    "alternativa": "La jugada que Leda le ofrece a la persona en lugar de lo pedido.",
    "lo_que_puede_hacer": "Lo que Leda puede hacer por chat.",
    "otra_forma_de_hacerlo": "Otra forma de hacer lo que la persona pidió fuera de este chat o "
                             "con otra persona, con su código.",
    "solo_si_pregunta": "Algo cierto que Leda sabe y dice sólo si la persona lo pregunta.",
    "aviso_al_administrador": "El aviso al administrador de que se pidió algo que no está en "
                              "la lista, con cuándo le llega.",
    "vuelve_a": "Cómo quedó la tarea después de corregir: su estado, el día que la persona "
                "dio para terminarla o el día en que vence.",
    "prevision_corregida": "El día para terminarla que se corrigió: ya no vale.",
    "aviso_de_la_prevision_corregida": "Si quien aprueba el trabajo de la persona se entera "
                                       "del día que se corrigió (llega).",
    "correccion_al_referente": "El aviso a quien aprueba el trabajo de la persona de que el "
                               "día para terminarla que ya recibió no vale: a quién y cuándo "
                               "se entera.",
    "aviso_de_la_prevision_anterior": "El aviso a quien aprueba el trabajo de la persona del "
                                      "día para terminarla que vuelve a valer: a quién y "
                                      "cuándo se entera.",
    "prevision_que_no_vale": "El día para terminarla que recibió quien aprueba el trabajo de "
                             "la persona y que ya no vale.",
    "corrige": "La jugada anotada que la persona dijo que estuvo mal.",
    "tarea_correcta": "La tarea en la que sí iba lo anotado.",
    "cerrada_con": "Con qué se había cerrado la pregunta: lo que la persona tocó o escribió no "
                   "cambió nada.",
    "cierre": "Cómo se cerró la pregunta, con su código.",
    "cuando": "El día en que pasó.",
    "aplicado": "Lo corregido, anotado en la tarea correcta: su resultado.",
    "preguntas_ya_cerradas": "Las preguntas que el hecho abrió y que el mismo mensaje ya cerró "
                             "(otra jugada las contestó o las dejó sin efecto): no se hacen.",
    "lo_que_sigue": "Lo próximo que Leda hace en el seguimiento de esa tarea, como quedó al "
                    "terminar este mensaje. Todavía no pasó.",
    "proximo_aviso": "Lo próximo que Leda le va a escribir a la persona sobre esa tarea: qué "
                     "aviso es y cuándo le llega.",
    "seguimiento": "Cómo sigue el seguimiento de la tarea, con su código.",
    "detenido_mientras_siga_trabada": "Mientras la tarea siga trabada, Leda no le pide el "
                                      "estado: el seguimiento vuelve cuando la persona cuenta "
                                      "que se destrabó.",
    "ya_no_va_a_pasar": "Lo que Leda le contó a la persona en un mensaje anterior que iba a "
                        "pasar y ya no va a pasar, con su motivo.",
    "anuncio": "Lo que se había anunciado, con el nombre del dato con que se contó.",
    # --- Los datos de una jugada, como se entendieron del mensaje -----------------------------
    "palabras": "Lo que la persona contó de cómo viene la tarea, con sus palabras.",
    "quien": "Quién puede destrabar el bloqueo, como lo nombró la persona.",
    "que_pide": "Lo que la persona le pidió a Leda, resumido.",
    "contesta_la_pregunta": "Si lo que la persona pidió es su respuesta a la pregunta abierta "
                            "de Leda: entonces no es un pedido nuevo.",
    "eligio": "La opción que eligió la persona.",
    "no_se_anoto_nada": "No quedó nada anotado.",
    "pregunta_sigue_abierta": "La pregunta sigue abierta: la opción elegida ya no se podía "
                              "usar.",
    "cambios_pedidos": "Los cambios que pidió quien revisó la tarea.",
    "vence": "El día en que vence la tarea.",
    # --- Lo que dice un aviso que Leda manda por su cuenta ------------------------------------
    "aviso": "Qué aviso es, con su código.",
    "necesita_respuesta": "Si el aviso espera una respuesta de quien lo recibe.",
    "numero": "Cuántas veces seguidas, contando ésta, Leda le consulta cómo viene la tarea "
              "sin que conteste.",
    "responsable": "La persona responsable de la tarea.",
    "prevision_vigente": "El día que la persona dio para terminar la tarea y que vale ahora: "
                         "ese día, el atraso que tendrá si la termina ese día, su porqué y si "
                         "quien aprueba su trabajo ya se enteró o cuándo se entera.",
    "fecha": "Una fecha.",
    "pide_el_estado_el": "El día en que Leda le va a consultar cómo viene la tarea: todavía "
                         "no pasó.",
    "si_no_hay_respuesta": "Lo que va a pasar si la persona no contesta: va a quedar asentado "
                           "que la tarea está atrasada, o que la consulta quedó sin respuesta "
                           "(queda_asentado), y a quiénes les llega (se_avisa_a). Es sólo "
                           "información: nadie toma la tarea ni la destraba por eso. Todavía no "
                           "pasó.",
    "se_avisa_a": "A quiénes se les va a avisar.",
    "avance_anterior": "Lo que la persona contestó antes sin un hecho cierto, y cuándo.",
    "el": "El día en que pasó.",
    "espera_algo_cierto": "Lo que Leda necesita saber de la tarea: un hecho cierto.",
    "seguimiento_por": "Desde qué día Leda sigue la tarea: el día que la persona dio para "
                       "terminarla, si es posterior al día en que vence.",
    "pedido_desde": "Desde cuándo Leda le consulta cómo viene la tarea sin respuesta.",
    "pedidos_de_estado_sin_respuesta": "Cuántas veces Leda le consultó cómo viene la tarea "
                                       "sin que contestara.",
    "pedidos_anteriores_que_no_le_llegaron": "Consultas anteriores de cómo viene la tarea que "
                                             "no le llegaron a la persona: no se le habla como "
                                             "si las hubiera recibido.",
    "pedidos_de_estado_que_no_le_llegaron": "Consultas de cómo viene la tarea que no le "
                                            "llegaron a la persona.",
    "avance_sin_algo_cierto": "Lo que la persona contestó antes sin un hecho cierto.",
    "ausencia": "La ausencia de la persona, con desde y hasta.",
    "desde": "Desde cuándo.",
    "hasta": "Hasta cuándo.",
    "sobre": "Lo anotado sobre lo que se consulta.",
    "preguntas_sin_respuesta": "Cuántas veces se hizo la consulta sin respuesta.",
    "preguntado_el": "Cuándo se hizo la consulta por primera vez.",
    "lo_pendiente": "Lo que tenía el aviso que no salió.",
    "aviso_que_no_salio": "El aviso que no le llegó a quien iba: a quién y qué era.",
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
    "sin_fecha_comprometida": "La tarea no tiene un día en que vence.",
    "sin_bloqueo_abierto": "La tarea no tiene un bloqueo abierto.",
    "varios_bloqueos_abiertos": "La tarea tiene más de un bloqueo abierto: falta saber cuál se "
                                "resolvió (causas dice cuáles son).",
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
    "ya_se_escalo": "Ya se le avisó a quien corresponde que la persona no contestaba.",
    "misma_fecha_comprometida": "El día que dio la persona para terminarla es el día en que "
                                "vence: para quien aprueba su trabajo no cambia nada.",
    "sin_referente": "La persona no tiene a alguien que apruebe su trabajo.",
    "se_anoto_en_la_tarea_equivocada": "Se había anotado en la tarea equivocada.",
    # --- Códigos: si un aviso le llega a quien lo recibe ---------------------------------------
    "ninguna_definida": "No hay ninguna definida todavía.",
    "ya_le_llego": "Ya le llegó: quien lo recibe ya lo sabe.",
    "no_le_va_a_llegar": "No le va a llegar: ya no hace falta (motivo dice por qué).",
    "no_le_llego": "No le llegó: quien lo iba a recibir no lo sabe por este aviso.",
    "sigue_abierto": "Sigue abierto: Leda sigue esperando.",
    "ya_contesto": "Ya no sigue abierto: la persona ya contestó con algo cierto y Leda no "
                   "espera más esa respuesta.",
    # --- Códigos: por qué ya no va a pasar algo anunciado --------------------------------------
    "ya_respondio": "La persona ya contestó lo que el aviso iba a pedir.",
    "hay_una_prevision_mas_nueva": "La persona dio después otro día para terminarla: el "
                                   "aviso era del anterior.",
    "llego_el_motivo": "La persona dio después el porqué de ese mismo día: en lugar de este "
                       "aviso sale otro que lo lleva.",
    "volvio_a_la_fecha_comprometida": "El día que la persona dio para terminarla volvió a ser "
                                      "el día en que vence.",
    "tarea_entregada": "La tarea ya se entregó.",
    "bloqueo_abierto": "La tarea tiene un bloqueo abierto.",
    "cambio_el_vencimiento": "Cambió el día en que vence la tarea.",
    "cambio_el_responsable": "Cambió quién es responsable de la tarea.",
    "tarea_inexistente": "La tarea ya no existe.",
    "ya_vencio": "La tarea ya llegó a su vencimiento: un aviso previo ya no es previo.",
    "reemplazado_por_un_avance": "Lo reemplazó el pedido que sigue a un avance.",
    "reemplazado_por_el_reencuadre": "Lo reemplazó el reencuadre después de una ausencia.",
    "destinatario_inactivo": "Quien lo iba a recibir ya no está activo en el equipo.",
    "destinatario_sin_telegram": "Quien lo iba a recibir no tiene un chat con Leda.",
    "tipo_sin_declarar": "El aviso no es de un tipo que Leda manda.",
    "ya_no_esta_entregada": "La tarea ya no está entregada esperando su revisión.",
    "cambio_quien_aprueba": "Cambió quién aprueba el trabajo de la persona responsable.",
    "hay_una_entrega_mas_nueva": "La tarea tiene una entrega más nueva: sale otro aviso, con "
                                 "lo que vale ahora.",
    "ya_se_hablo_de_la_tarea": "La persona habló de esa tarea con Leda después de que el "
                               "aviso se guardó: ya está al tanto, y el aviso no se lo repite.",
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
    "pedirselo_y_contar": "Que la persona trabada se lo pida directamente a quien destraba y le "
                          "cuente a Leda lo que pase (lo que arreglaron, quién lo destraba, o "
                          "que ya puede seguir): Leda no le escribe a quien destraba y al día "
                          "hábil siguiente le consulta cómo le fue.",
    "pasarsela_a_otra_persona": "Pasarle la tarea a otra persona del equipo que tenga un chat "
                                "con Leda.",
    "si_la_termino": "Si la persona terminó la tarea.",
    "si_la_empezo": "Si la persona empezó la tarea.",
    "para_cuando_la_termina": "Para qué día la va a terminar.",
    "si_esta_trabada": "Si no puede avanzar con la tarea.",
    # --- Códigos: los tipos de pregunta (lo que la pregunta espera) ----------------------------
    "cual_tarea": "Pregunta de qué tarea habla la persona: espera que elija una.",
    "causa_del_bloqueo": "Pregunta qué traba la tarea: espera la causa.",
    "estado_de_la_tarea": "Pregunta cómo viene la tarea: espera algo cierto, según su estado "
                          "(espera_algo_cierto dice qué, cuando viene).",
    "fecha_de_la_tarea": "Pregunta para qué día va a tener la tarea: espera una fecha.",
    "motivo_del_atraso": "Pregunta qué atrasa la tarea hasta el día que la persona dio para "
                         "terminarla, que queda después del día en que vence: espera el "
                         "porqué de ese día, con sus palabras.",
    "propuesta": "Leda le propuso algo a la persona: espera que elija una de las propuestas o "
                 "la deje.",
    "como_vienen_sus_tareas": "Leda le consulta a la persona cómo viene cada una de sus tareas, "
                              "todas juntas en un solo mensaje, con el ritmo fijo del equipo: "
                              "espera algo cierto de cada una. Es una sola consulta, por la "
                              "lista entera.",
    "sus_tareas": "Las tareas abiertas de la persona en este mensaje, en una lista: cada una con "
                  "lo que se sabe de ella, también las trabadas y las entregadas, para que vea "
                  "todo junto y avise si algo cambió. Leda consulta cómo vienen sólo por las que "
                  "no están trabadas ni entregadas.",
    "sin_respuesta_desde": "Leda le consultó cómo viene esta tarea en un mensaje anterior, ese "
                           "día, y la persona todavía no le contó.",
    "solo_lo_que_cambio_o_falta": "Esta lista no es la primera de la semana: trae sólo las "
                                  "tareas que cambiaron o por las que la persona todavía no "
                                  "contó cómo vienen. Las demás siguen como las contó.",
    "sin_novedades_para_la_lista": "No había nada nuevo para la lista: ninguna tarea cambió y "
                                   "la persona ya había contado cómo venían todas.",
    "antes_le_recuerda_que_vence": "Antes de volver a consultarle, Leda le recuerda que la "
                                   "tarea vence pronto, sin pedirle nada (llega, todavía no "
                                   "pasó).",
    "de_la_lista": "Las tareas de la lista por las que Leda consulta: las que la persona todavía "
                   "no contó.",
    "vence_hoy": "La tarea vence hoy.",
    # --- El informe al grupo (C-6, decisión 25; `informe_al_grupo.py`) -------------------------
    "informe_al_grupo": "Mensaje al grupo del equipo, no a una persona: lo que pasó con las "
                        "tareas del equipo desde el informe anterior y lo que sigue igual, para "
                        "que todos estén al tanto y puedan ayudar. Cada tarea con quién la tiene "
                        "(la_tiene). Es información: no pide respuesta.",
    "terminadas": "Las tareas que quedaron terminadas (aprobadas) desde el informe anterior, "
                  "cada una con quién la hizo (la_tiene).",
    "atrasadas": "Las tareas cuyo atraso la persona ya habló con Leda en privado: el día en que "
                 "vencían (vence) y, si los dio, el día que dio para terminarla y su motivo. Es "
                 "información para el equipo.",
    "trabadas": "Las tareas trabadas: lo que las traba como lo dijo la persona (causas), desde "
                "cuándo, cuántos días hábiles lleva y, si quien la destraba dio un día, ese día "
                "(para_cuando).",
    "entregadas": "Las tareas entregadas que esperan la revisión.",
    "siguen": "Las tareas que siguen su curso: cada una con su estado y el día en que vence.",
    "sin_saber_como_vienen": "Las tareas de las que Leda no sabe cómo vienen: le consultó a "
                             "quien la tiene otro día y todavía no contestó. No están bien ni "
                             "atrasadas: no se sabe.",
    "todo_en_orden": "Lo comprobó el sistema: ninguna tarea atrasada, ninguna trabada y ninguna "
                     "de la que Leda no sepa cómo viene. Es una buena noticia para el equipo.",
    "semana_buena": "Lo comprobó el sistema con reglas fijas, desde el informe anterior: ningún "
                    "atraso nuevo, nada trabado, lo que vencía se entregó a tiempo y algo se "
                    "terminó o se entregó. Es un reconocimiento breve al equipo entero: no dice "
                    "nada de una persona frente a otra.",
    "sin_novedades_para_el_grupo": "Esta vez no hay nada que se le pueda contar al grupo. No "
                                   "quiere decir que esté todo en orden.",
    "nada_para_el_informe": "No había nada que contarle al grupo: ninguna tarea abierta ni "
                            "terminada desde el informe anterior.",
    "sin_grupo": "El espacio no tiene un grupo del equipo.",
    "ya_conto_como_viene": "La persona ya había contado cómo viene la tarea y no cambió nada: "
                           "no hacía falta consultárselo ese día.",
    "ya_paso_su_momento": "El día de ese mensaje ya pasó: no se manda otro día.",
    "no_es_dia_habil": "Ese día no es de trabajo para el equipo.",
    "sin_tareas_abiertas": "La persona no tiene tareas por las que consultarle.",
    # --- Códigos: los avisos que Leda manda por su cuenta --------------------------------------
    "aviso_previo": "Aviso de que la tarea vence pronto; no pide respuesta.",
    "vencimiento_proximo": "La tarea vence pronto; no pide respuesta.",
    "vencimiento_con_prevision": "La tarea vence hoy, pero la persona ya dijo otro día para "
                                 "terminarla: no pide nada.",
    "pedido_de_estado": "Leda consulta cómo viene la tarea: espera algo cierto.",
    "reencuadre": "Leda retoma el seguimiento después de una ausencia.",
    "vuelta_de_ausencia": "La persona volvió de una ausencia: Leda retoma el seguimiento.",
    "escalamiento": "Aviso a quien corresponde de que la persona no contesta.",
    "falta_de_respuesta": "La persona no contestó los pedidos: se le avisa a quien "
                          "corresponde.",
    "repregunta_de_estado": "Leda vuelve a consultar cómo viene la tarea después de una "
                            "respuesta sin un hecho cierto.",
    "repregunta": "Leda vuelve a hacer una consulta que no tuvo respuesta.",
    "repeticion_del_dia": "Leda vuelve a hacer, una sola vez en el día, una consulta que la "
                          "persona todavía no contestó.",
    "vuelve_la_pregunta": "Leda vuelve, en un mensaje aparte, a una pregunta que había "
                          "quedado sin contestar: la persona contestó la otra que estaba "
                          "abierta, o habló de otro tema.",
    "la_misma_pregunta_sale_en_otro_aviso": "La misma pregunta sale en otro mensaje de ese "
                                            "momento: no se repite dos veces.",
    "ya_no_es_el_dia_de_la_repeticion": "La repetición era para otro día: ese día ya pasó.",
    "escalamiento_de_una_pregunta": "Aviso a quien corresponde de que una consulta quedó sin "
                                    "respuesta.",
    "nueva_prevision": "Aviso a quien aprueba el trabajo de la persona responsable: dio un "
                       "día nuevo para terminar su tarea. Es información para él; no pide "
                       "respuesta.",
    "correccion_de_prevision": "Aviso a quien aprueba el trabajo de la persona responsable: "
                               "el día para terminar la tarea que ya recibió no vale.",
    "entrega_para_aprobar": "Aviso a quien aprueba el trabajo de la persona responsable: "
                            "entregó la tarea, que espera su revisión; después de revisarla, "
                            "decide: aprobarla o pedirle cambios, con un botón o escribiendo.",
    "lista_de_entregas_para_revisar": "Aviso a la persona con las entregas que esperan su "
                                      "revisión, que van juntas en este mensaje: cuántas son "
                                      "(cuantas) y, en los hechos que siguen, cada una. Cada "
                                      "una se abre con su botón para revisarla; en la lista no "
                                      "se decide nada.",
    "cuantas": "Cuántas son.",
    "entrega_en_la_lista": "Una de las entregas de la lista que esperan la revisión de la "
                           "persona: la tarea, quién la entregó y cuántas fotos trae. Se abre "
                           "con su botón para revisarla.",
    "falla_de_aviso": "Un aviso que la persona causó no le llegó a quien iba.",
    "lleva_el_enlace_a_la_pagina_de_la_tarea":
        "Al final de este mensaje, el código agrega un enlace personal a la página de la "
        "tarea, de sólo lectura, con la tarea, lo que fue pasando y lo que se entregó. La IA no "
        "lo ve ni lo escribe: no hay ninguna dirección para escribir.",
    "no_salio_un_aviso": "Un aviso que la persona causó no le llegó a quien iba.",
    # --- El enlace a la página de una tarea, pedido por chat (`enlace.py`) ---------------------
    "como_la_nombra": "Cómo nombró la persona una tarea que no está en su lista.",
    # --- El resumen para cualquiera, el detalle a pedido (decisión 33; `detalle.py`) -------------
    "solo_el_resumen": "La persona que escribe no ve el detalle de esa tarea (sus fotos, archivos "
                       "y correcciones), que ven sólo quienes tienen que ver con ella: recibe su "
                       "resumen, que ve cualquiera del equipo (la tarea, quién la tiene, cómo "
                       "está y cuándo vence), y ningún enlace.",
    "el_detalle_lo_ve": "El sector que ve el detalle de la tarea: el de la tarea.",
    "se_lo_puede_pedir_a": "A quién le puede pedir Leda el detalle de la tarea, si la persona "
                           "quiere: el encargado del sector de la tarea, que decide si se la "
                           "comparte. Leda se lo ofrece; no se lo pidió todavía.",
    "sin_encargado_del_sector": "El sector de la tarea no tiene un encargado que pueda "
                                "compartir su detalle: no hay a quién pedírselo.",
    "ya_se_lo_pidio_a": "La persona ya le pidió el detalle de esa tarea a esta persona, el "
                        "encargado del sector, que todavía no contestó: no se pide otra vez.",
    "ya_lo_pidio": "La persona ya pidió el detalle de esa tarea y todavía no le contestaron.",
    "ya_la_ve": "La persona ya ve el detalle de esa tarea: no hace falta pedirlo.",
    "detalle_pedido": "Quedó pedido el detalle de la tarea: Leda le consulta al encargado del "
                      "sector de la tarea si se la comparte y le avisa a la persona cuando "
                      "conteste. Todavía no se la compartió.",
    "compartir_el_detalle": "Pregunta al encargado del sector de una tarea si le comparte su "
                            "detalle a quien lo pidió, con dos botones; también se contesta "
                            "escribiendo.",
    "pedido_del_detalle": "Mensaje de Leda, como Leda, al encargado del sector de una tarea: "
                          "quién pide ver su detalle (pide_ver_el_detalle), de quién es la tarea "
                          "(la_tiene) y cuándo vence; consulta si se la comparte.",
    "pide_ver_el_detalle": "Quién pide ver el detalle de la tarea (sus fotos, archivos y "
                           "correcciones).",
    "espera_que_decida_si_la_comparte": "Una tarea de otra persona (la_tiene) cuyo detalle "
                                        "alguien pidió ver (pide_ver_el_detalle): espera que la "
                                        "persona que escribe, encargado de su sector, decida si "
                                        "se la comparte. No es una tarea suya.",
    "la_compartio": "Si el encargado del sector le compartió el detalle de la tarea a quien lo "
                    "pidió (verdadero: desde ahora ve su página) o no (falso: no cambió nada).",
    "aviso_a_quien_lo_pidio": "Lo que se le avisa a quien pidió el detalle, de cómo terminó: a "
                              "quién (a) y cuándo se entera (llega).",
    "aviso_a_quienes_lo_pidieron": "Lo que se les avisa a todos los que pidieron el detalle de "
                                   "esa tarea, de cómo terminó: a quiénes (a) y cuándo se "
                                   "enteran (llega).",
    "como_termino_el_pedido_del_detalle": "Aviso de cómo terminó el pedido del detalle de una "
                                          "tarea: si el encargado del sector (lo_decidio) se lo "
                                          "compartió (la_compartio) y, si dijo por qué, sus "
                                          "palabras (por_que); o que terminó porque el sector "
                                          "de la tarea se quedó sin encargado mientras "
                                          "esperaba (sin_encargado_del_sector, el_detalle_lo_ve), "
                                          "lo mismo que si no lo hubiera tenido al pedirlo; o, "
                                          "a quien Leda le consultaba si lo compartía, que ya "
                                          "no hace falta que conteste "
                                          "(ya_no_espera_su_respuesta). Es información: no pide "
                                          "respuesta.",
    "no_hay_un_pedido_del_detalle": "Ninguna tarea espera que la persona decida si comparte su "
                                    "detalle.",
    "el_pedido_ya_no_espera": "El pedido del detalle ya no espera esa decisión: ya se decidió.",
    "ninguna_tarea_con_ese_nombre": "Ninguna tarea del equipo se llama como la nombró la "
                                    "persona.",
    "la_pagina_no_esta_disponible": "La página de las tareas no está disponible ahora: no hay "
                                    "enlace para pasar.",
    "ya_lleva_el_enlace_de_otra_tarea": "Este mensaje ya lleva el enlace de otra tarea, y "
                                        "lleva uno solo: el de ésta se puede pedir aparte.",
    # --- La persecución del bloqueo (C-5, porción 1; `persecucion.py`) -------------------------
    "se_le_pregunta_a": "A quién le consulta Leda, como Leda y no en nombre de nadie, para "
                        "cuándo destraba la tarea (a), y cuándo le llega (llega).",
    "no_se_le_puede_escribir_a": "A quién Leda no le puede escribir por este chat (a), y por "
                                 "qué (motivo): no se le consulta nada ni se promete que se "
                                 "va a enterar.",
    "se_le_aviso_al_administrador": "El aviso al administrador para que conecte con Leda a esa "
                                    "persona (para_que_conecte), con cuándo le llega (llega), o "
                                    "que no le va a llegar.",
    "para_que_conecte": "La persona que el administrador tiene que conectar con Leda.",
    "espera_que_la_destrabe": "Una tarea de otra persona, trabada, que la persona que escribe "
                              "puede destrabar: lo dijo quien la tiene (responsable), con lo "
                              "que la traba (causa). No es una tarea suya.",
    "cuando_se_destraba": "Pregunta a quien puede destrabar la tarea de otra persona lo que "
                          "falta saber de eso (falta) o, si no dice qué falta, para cuándo lo "
                          "resuelve: espera su respuesta.",
    "pregunta_a_quien_destraba": "Mensaje de Leda, como Leda, a quien puede destrabar la tarea "
                                 "de otra persona: quién está trabado (responsable), con qué "
                                 "tarea y qué le falta (causa), como lo dijo esa persona, y la "
                                 "consulta de para cuándo lo puede resolver. No es un mensaje "
                                 "en nombre de nadie.",
    "lo_que_dijo_quien_destraba": "Aviso a la persona trabada con lo que dijo quien puede "
                                  "destrabar su tarea (quien_destraba). Es información: no "
                                  "pide respuesta; cuando pueda seguir, lo dice.",
    "dice_quien_destraba": "Lo que dijo quien puede destrabar la tarea: para cuándo, que ya "
                           "está o lo que pasa, con sus palabras.",
    "aviso_a_quien_esta_trabado": "El aviso a la persona trabada con lo que dijo quien escribe: "
                                  "a quién (a) y cuándo se entera (llega).",
    "para_cuando": "El día para el que se resuelve lo que traba la tarea, según quien lo dijo.",
    "ya_esta": "Quien puede destrabar la tarea dice que ya lo resolvió. La tarea sigue trabada "
               "hasta que la persona trabada diga que puede seguir.",
    "lo_que_dice": "Lo que dijo quien puede destrabar la tarea, o la persona trabada, con sus "
                   "palabras.",
    "pidio_que_no_le_escriba": "La persona trabada pidió que Leda no le escribiera a quien "
                               "puede destrabar su tarea.",
    "ya_se_le_escribio": "Leda ya le escribió a quien puede destrabar la tarea: lo que le "
                         "llegó no se puede retirar.",
    "no_le_iba_a_escribir": "Leda no le iba a escribir a nadie por esa tarea trabada.",
    "ya_se_destrabo": "La tarea ya no está trabada por eso.",
    "cambio_quien_destraba": "La persona trabada dijo después que la tarea la destraba otra "
                             "persona.",
    "no_sabe_quien_destraba": "La persona trabada dijo después que no sabe quién destraba la "
                              "tarea.",
    "nadie_mas_puede_destrabar": "La persona trabada dijo después que no hay nadie más que pueda "
                                 "destrabar la tarea.",
    "dijo_algo_mas_nuevo": "Quien puede destrabar la tarea dijo algo más nuevo, que sale en su "
                           "lugar.",
    "no_le_toca_destrabarla": "La persona que escribe no es quien puede destrabar esa tarea: "
                              "lo que dice no queda anotado.",
    # --- "Ya lo hablé con él" (C-5, porción 2; `persecucion.py`) -------------------------------
    "ya_lo_hablaron": "Quien puede destrabar la tarea dice que ya lo habló con la persona "
                      "trabada: lo que queda anotado es lo que arreglaron entre ellos.",
    "lo_que_arreglaron": "Qué arreglaron quien puede destrabar la tarea y la persona trabada, "
                         "para que quede asentado.",
    # --- Cerrar el tema para todos, lo acordado y "se lo pido yo" (C-5c; `persecucion.py`) -----
    "que_arreglaron": "Pregunta a la persona trabada qué arregló con quien puede destrabar su "
                      "tarea y para cuándo: espera su respuesta.",
    "pregunta_a_quien_esta_trabado": "Mensaje de Leda a la persona trabada: quien puede "
                                     "destrabar su tarea (quien_destraba) dice que ya lo "
                                     "hablaron, sin decir qué; la consulta de qué arreglaron y "
                                     "para cuándo. Vale lo que conteste primero cualquiera de "
                                     "los dos.",
    "como_le_fue_con_quien_destraba": "Mensaje de Leda a la persona trabada, el día hábil "
                                      "siguiente de que dijo que se lo pedía directamente a "
                                      "quien destraba su tarea (se_lo_pide_a): la consulta de "
                                      "cómo le fue, qué arreglaron y para cuándo.",
    "lo_que_dijo_quien_esta_trabado": "Aviso a quien puede destrabar (o destrababa) la tarea "
                                      "de otra persona con lo que dijo la persona trabada "
                                      "(quien_esta_trabado) sobre lo que arreglaron, o lo que "
                                      "contestó. Es información: no pide respuesta.",
    "ya_no_hace_falta_que_destrabe": "Aviso a quien Leda le consultaba por la tarea trabada de "
                                     "otra persona (responsable): el tema se cerró sin esa "
                                     "persona (como_se_cerro), así que ya no hace falta lo que "
                                     "se le pedía y Leda no le consulta más. Es información: no "
                                     "pide respuesta.",
    "se_lo_pasa_si_contesta": "Lo que llega es lo que dijo la otra persona de lo que "
                              "arreglaron, o lo que contestó: si es así, no hace falta que haga "
                              "nada; si no es lo que entendió, o quiere decirle algo, que lo "
                              "diga y Leda se lo pasa.",
    "cierra_el_tema": "Lo que llega contesta lo que la otra persona había dicho: con eso el tema "
                      "queda cerrado para los dos y no se le pide nada más a nadie.",
    "como_se_cerro": "Cómo se cerró el tema para quien recibe el aviso: la tarea ya no está "
                     "trabada por eso (ya_se_destrabo), la destraba otra persona "
                     "(cambio_quien_destraba), la persona trabada dijo que no sabe quién "
                     "la destraba (no_sabe_quien_destraba) o que no hay nadie más que pueda "
                     "destrabarla (nadie_mas_puede_destrabar), que ya lo hablaron "
                     "(dijo_que_ya_lo_hablaron) o que se lo pide directamente "
                     "(se_lo_pide_quien_esta_trabado), o el bloqueo se había anotado por error "
                     "(quedo_sin_efecto).",
    "habia_dicho": "Lo último que había dicho sobre eso quien recibe el aviso: para cuándo o sus "
                   "palabras.",
    "dijo_que_ya_lo_hablaron": "La persona trabada dijo que ya lo habló con quien destraba su "
                               "tarea.",
    "se_lo_pide_quien_esta_trabado": "La persona trabada dijo que se lo pide directamente a "
                                     "quien destraba su tarea.",
    "dijo_que_se_lo_pedia": "La persona trabada que, después de que quien recibe el aviso dio "
                            "su día, le dijo a Leda (no a quien recibe el aviso) que se lo iba "
                            "a pedir directamente. Ese día sigue valiendo, y por eso Leda le "
                            "consulta igual.",
    "quedo_sin_efecto": "El bloqueo se había anotado por error y quedó sin efecto.",
    "ya_no_hace_falta_que_destraben": "A quiénes Leda les consultaba por la tarea trabada y "
                                      "ahora les avisa que ya no hace falta "
                                      "(aviso_a_quien_destrababa).",
    "aviso_a_quien_destrababa": "El aviso de que ya no hace falta, a quien Leda le consultaba "
                                "por la tarea trabada: a quién (a) y cuándo se entera (llega).",
    # Un "no le escribas" corregido tarde (decisión 61): a quien ya le llegó que no hacía falta.
    "lo_de_antes_era_por_otra_tarea": "Lo que Leda le dijo antes a quien recibe el mensaje, que "
                                      "ya no hacía falta que destrabara esta tarea, era por otra "
                                      "tarea (la nombrada, si se nombra): se había anotado en la "
                                      "equivocada. Para esta tarea sigue haciendo falta. Si el "
                                      "mensaje no pregunta nada, Leda le consulta el día que "
                                      "había dicho (habia_dicho).",
    "aviso_de_que_sigue_haciendo_falta": "El aviso a quien Leda le había dicho que ya no hacía "
                                         "falta que destrabara la tarea: eso era por otra tarea y "
                                         "para ésta sigue haciendo falta. A quién (a) y cuándo se "
                                         "entera (llega).",
    "quien_esta_trabado": "Quién tiene la tarea trabada: la persona que dijo lo que llega.",
    "dice_quien_esta_trabado": "Lo que dijo la persona trabada sobre lo que arregló con quien "
                               "destraba su tarea, o lo que contestó: para cuándo y sus "
                               "palabras.",
    "aviso_a_quien_destraba": "El aviso con lo que dijo la persona que escribe, a quien destraba "
                              "su tarea: a quién (a) y cuándo se entera (llega).",
    "le_pregunta_tambien_a": "La misma consulta, qué arreglaron y para cuándo, también a la "
                             "persona trabada: a quién (a) y cuándo le llega (llega). Vale lo "
                             "que conteste primero cualquiera de los dos.",
    "ya_se_habia_destrabado": "Lo que dijo quien destrababa la tarea llegó después de que la "
                              "tarea ya no estaba trabada por eso.",
    "ya_no_hace_falta_que_la_destrabe": "Una tarea de otra persona que la persona que escribe "
                                        "iba a destrabar y ya no hace falta (Leda se lo avisó): "
                                        "lo que diga de eso le llega a quien la tiene. No es una "
                                        "tarea suya.",
    "se_lo_pide_a": "A quién se lo pide directamente la persona trabada.",
    "le_pregunta_como_le_fue": "Cuándo le consulta Leda a la persona trabada cómo le fue "
                               "(llega).",
    "ya_lo_conto_quien_destraba": "Quien puede destrabar la tarea ya contó lo que arreglaron: "
                                  "la consulta a la persona trabada ya no hace falta.",
    "ya_lo_conto_quien_esta_trabado": "La persona trabada ya contó lo que arreglaron: la "
                                      "consulta ya no hace falta.",
    "volvio_a_ser_quien_destraba": "La persona trabada volvió a decir que la destraba esa misma "
                                   "persona.",
    "sin_quien_destraba": "La tarea trabada no tiene a otra persona que la destrabe: no hay con "
                          "quién haber arreglado algo.",
    # --- "No me corresponde" y la cadena al referente (C-5, porción 3; `persecucion.py`) -------
    "no_le_corresponde": "Quien Leda creía que podía destrabar la tarea dice que no le "
                         "corresponde.",
    "le_toca_a": "A quién le toca destrabarla, según quien lo dijo.",
    "quien_se_encarga": "Quién se encarga de destrabar la tarea, si no es la persona que "
                        "escribe.",
    "nombrado_por": "Quién dijo que esta persona es la que puede destrabar la tarea, cuando no "
                    "lo dijo la persona trabada.",
    "cadena_del_bloqueo": "Aviso informativo a quien está a cargo de un sector: nadie toma el "
                          "bloqueo de una tarea y va la cadena entera, quién dijo qué (cadena), "
                          "para que determine quién lo resuelve. No le pide nada.",
    "cadena": "Quién dijo qué sobre quién destraba la tarea, en orden: de es quien lo dijo, "
              "le_toca_a a quién según esa persona, y si dijo que no le corresponde o que no "
              "sabe, con sus palabras.",
    "aviso_de_la_cadena": "El aviso que informa el bloqueo, con la cadena entera, para que se "
                          "decida quién lo resuelve: a quién (a) y cuándo se entera (llega), o "
                          "por qué no le llega.",
    "sin_referente": "No hay a quién informarle el bloqueo: el sector no tiene a nadie a "
                     "cargo.",
    # --- Hasta tres personas, "ni idea" y lo que dice a quien se le informó (C-5d) ------------
    "quien_mas_puede_destrabar": "Mensaje de Leda a la persona trabada: quien Leda creía que "
                                 "podía destrabar su tarea (quien_destraba) dice que no le "
                                 "corresponde y no sabe de quién es (dice_quien_destraba); la "
                                 "consulta de si se le ocurre otra persona que pueda "
                                 "destrabarla. Si no se le ocurre nadie, queda asentado.",
    "se_le_informo_que_sigue_trabada": "Una tarea de otra persona, trabada, que Leda le "
                                       "informó a la persona que escribe que sigue trabada: lo "
                                       "que diga de eso le llega a quien la tiene, que es quien "
                                       "la da por destrabada. No es una tarea suya.",
    # --- Los bloqueos encadenados (C-5, porción 4; `encadenados.py`) -------------------------
    "novedad_de_lo_que_espera": "Aviso informativo a una persona trabada: algo pasó con lo que "
                                "espera su tarea, más arriba en la cadena (novedad). No le pide "
                                "nada; su tarea sigue trabada hasta que diga que puede seguir.",
    "esperando_a": "Lo que espera la tarea trabada, en orden: la tarea de quien la destraba "
                   "(de es quien la tiene) y, si esa también espera otra, la siguiente. En una "
                   "novedad, la última es donde pasó; si no, la última es la que destraba quien "
                   "puede destrabarla.",
    "novedad": "Lo que pasó en la última tarea de esperando_a (de es quien la tiene): que se "
               "trabó, lo que dice quien la destraba, que se destrabó, el día que dio para "
               "terminarla, que la entregó o que quedó terminada.",
    "se_trabo": "La tarea quedó trabada: lo que la traba (causa) y quién la puede destrabar "
                "(lo_destraba), si se sabe.",
    "lo_destraba": "Quién puede destrabarla, según quien la tiene.",
    "se_destrabo": "Quien tiene esa tarea dijo que ya puede seguir con ella.",
    "la_entrego": "Quien tiene esa tarea la entregó: pasa a revisión.",
    "avisos_a_quienes_esperan": "Los avisos a las personas trabadas que esperan esta tarea, más "
                                "abajo en la cadena: cada uno, a quién y cuándo se entera.",
    "aviso_a_quien_espera": "El aviso a una persona trabada que espera esta tarea: a quién (a), "
                            "con qué tarea suya (tarea) y cuándo se entera (llega), o por qué "
                            "no le llega.",
    "su_tarea_trabada": "La tarea de quien puede destrabar la de otra persona que está trabada "
                        "y por eso no puede destrabarla: la tarea, lo que la traba (causa) y "
                        "quién la puede destrabar (lo_destraba).",
    # --- Seguir la cadena hasta quien puede destrabarla (C-5e; decisión 42) -------------------
    "ya_esta_trabado": "Quien puede destrabar la tarea (a) ya está trabado con lo que le falta: "
                       "Leda no le consulta lo que no puede dar. Lo que espera, hasta quien "
                       "puede destrabarlo (esperando_a: cada tarea con quién la tiene, lo que la "
                       "traba, quién la destraba y lo último que dijo esa persona).",
    "se_entera_de_cada_avance": "La persona trabada se va a enterar de cada avance de lo que "
                                "espera, con avisos que no piden respuesta.",
    "dice_quien_lo_destraba": "Lo último que dijo quien destraba esa tarea: para cuándo, que ya "
                              "está o sus palabras.",
    "lo_esperan": "Las tareas trabadas de otras personas que esperaban lo que la persona que "
                  "escribe acaba de destrabar: ahora puede dar lo que les falta, y Leda le "
                  "consulta para cuándo.",
    "le_pregunta_para_cuando": "La consulta a la persona que escribe de para cuándo destraba la "
                               "tarea de otra persona (responsable), con lo que le falta (causa) "
                               "y cuándo le llega (llega).",
    "le_vuelve_a_preguntar": "El día que dijo la persona que escribe, Leda le vuelve a consultar "
                             "si ya está (llega).",
    "se_le_cerro_el_tema": "Después de que esa persona dio un día, Leda le avisó que ya no hace "
                           "falta que destrabe la tarea y que no le va a consultar más: no se "
                           "le consulta.",
    "el_dia_que_dijo_quien_destraba": "Mensaje de Leda, como Leda, a quien puede destrabar la "
                                      "tarea de otra persona: hoy es el día que dijo "
                                      "(habia_dicho); la consulta de si ya está o para cuándo. "
                                      "Quién está trabado (responsable) y qué le falta (causa).",
    "su_tarea_no_esta_trabada": "La tarea suya con la que quien escribe dijo estar trabado "
                                "(su_tarea_trabada) no está trabada, ni después de todo lo que "
                                "dijo en este mensaje: lo que dice de la tarea de la otra persona "
                                "(tarea) no queda anotado así. No dice nada de cómo está la "
                                "tarea de la otra persona.",
    "ya_no_espera_esa_tarea": "La tarea de la persona ya no espera esa otra: cambió quién la "
                              "destraba o ya no está trabada.",
    "no_se_entero_que_se_trabo": "La persona no se había enterado de que esa tarea se trabó: "
                                 "que se destrabó no le dice nada.",
    # --- El bloqueo viejo (C-5, porción 5; `bloqueo_viejo.py`) -------------------------------
    "bloqueo_que_sigue_abierto": "Aviso informativo a quien está a cargo del sector de la "
                                 "tarea, o a quien aprueba el trabajo de la persona trabada si "
                                 "la persona trabada está a cargo del sector: la tarea sigue "
                                 "trabada desde hace varios días hábiles, con lo que la traba y "
                                 "todo lo que se dijo (historia) o, si ya se le había contado, "
                                 "lo que se dijo desde la vez anterior (desde_la_vez_anterior). "
                                 "No le pide nada.",
    "asentado_que_sigue_trabada": "Aviso informativo a la persona trabada: quedó asentado que "
                                  "su tarea sigue trabada desde hace varios días hábiles "
                                  "(queda_asentado). No le pide nada.",
    "la_vez_anterior": "El día en que se contó la vez anterior que la tarea seguía trabada.",
    "desde_la_vez_anterior": "Lo que se dijo de lo que traba la tarea desde la vez anterior, "
                             "como en historia; vacío si nadie dijo nada desde entonces.",
    # --- Quedó asentado (decisión 35; `asentado.py`) ------------------------------------------
    "queda_asentado": "Queda asentado en la historia de la tarea (si todavía no pasó, va a "
                      "quedar asentado). figura_en_el_informe_al_grupo dice si además figura en "
                      "el informe al grupo del espacio. A quién le llega (a), si se sabe.",
    "no_le_llega_a_nadie": "Lo asentado no le llega a nadie que decida: no hay quien esté a "
                           "cargo del sector ni quien apruebe el trabajo de la persona, o no "
                           "tiene Leda conectada. Quedó en la historia de la tarea y el "
                           "administrador está avisado.",
    "sin_a_quien_informar": "No hay a quién informarlo: nadie a cargo del sector ni quien "
                            "apruebe el trabajo de la persona, o no tiene Leda conectada.",
    "figura_en_el_informe_al_grupo": "Si figura en el informe al grupo del espacio, para que el "
                                     "equipo esté al tanto. Si es falso, no figura en ningún "
                                     "informe al grupo.",
    "trabada_desde": "El día en que la persona dijo que la tarea quedó trabada.",
    "dias_habiles_trabada": "Cuántos días hábiles lleva trabada la tarea, hasta hoy.",
    "historia": "Lo que se dijo de lo que traba la tarea, en el orden en que pasó, cada cosa con "
                "su día (el) y quién la dijo (de): a quién le toca destrabarla (le_toca_a), que "
                "no sabe, que le toca a quien lo dijo (nadie_mas), y lo que dijo quien la "
                "destraba: para cuándo, que ya está, que no le corresponde, con qué está trabado "
                "o sus palabras. Un día que alguien dio no es un hecho cumplido.",
    # --- Pasarle una tarea a otra persona (C-7; `pase.py`) --------------------------------------
    "pase_para_confirmar": "Lo que se mostró es el pase de una tarea a otra persona (pase), con "
                           "lo que pasa al confirmarlo (al_confirmar_el_pase): todavía no "
                           "cambió nada; espera que la persona lo confirme, con el botón o "
                           "escribiendo.",
    "pase": "Pasar la tarea a otra persona: quién la tiene (la_tiene) y a quién pasaría "
            "(pasaria_a).",
    "la_tiene": "Quién tiene la tarea ahora: quien la hace y da sus novedades.",
    "pasaria_a": "A quién pasaría la tarea con el pase.",
    "al_confirmar_el_pase": "Lo que pasa cuando la persona confirme el pase: si lo decide otra "
                            "persona, Leda se lo consulta primero (lo_decide); después, quien "
                            "la recibe tiene que decir que la toma (la_tiene_que_tomar). Hasta "
                            "que la tome, la tarea sigue con quien la tiene.",
    "lo_decide": "Quién decide si la tarea pasa: el encargado del sector de quien la recibe. "
                 "Leda se lo consulta antes que a quien la recibe.",
    "la_tiene_que_tomar": "Quién recibe la tarea: Leda le consulta si la toma, y sólo con su sí "
                          "pasa a ser suya.",
    "decide_y_la_toma": "Quien recibe la tarea es también quien decide: su sí vale como las "
                        "dos cosas.",
    "la_toma_al_confirmar": "Quien escribe se queda él con la tarea de alguien de su sector: pide, "
                            "decide y la toma la misma persona, así que al confirmar la tarea "
                            "pasa a ser suya, con la misma fecha y lo que pide para terminarla, "
                            "y Leda le avisa a quien la tenía.",
    "se_la_queda": "La persona que escribe se queda con la tarea de otra persona, para hacerla.",
    "pase_pedido": "El pase quedó pedido: la tarea sigue con quien la tiene hasta que la tomen, "
                   "y Leda le consulta a quien sigue.",
    "le_pregunta_a": "A quién le consulta Leda por el pase o por el detalle, como Leda y no en "
                     "nombre de nadie (a), y cuándo le llega (llega).",
    "aprobo_el_pase": "Si quien escribe aprobó que la tarea pase a otra persona (verdadero) o "
                      "no (falso).",
    "la_toma": "Si quien escribe toma la tarea que le querían pasar, o la de alguien de su sector "
               "con la que se queda: con su sí ya es suya, con la misma fecha y lo que pide para "
               "terminarla; con su no, sigue con quien la tenía.",
    "tambien_lo_decidia": "Quien escribe era también quien decidía el pase: su respuesta vale "
                          "como la decisión.",
    "sigue_con": "Quién sigue teniendo la tarea: no cambió de manos.",
    "aviso_a_quien_pidio": "Lo que se le avisa a quien pidió el pase, de cómo terminó: a quién "
                           "(a) y cuándo se entera (llega).",
    "aviso_a_quien_decidio": "Lo que se le avisa a quien decidió el pase, de cómo terminó: a "
                             "quién (a) y cuándo se entera (llega).",
    "confirmar_el_pase": "Pregunta si la persona confirma pasarle la tarea a la otra persona, "
                         "como lo muestra el pase: con el botón Confirmar o escribiendo. Se "
                         "puede dejar.",
    "decidir_el_pase": "Pregunta a quien decide si aprueba que la tarea de otra persona pase a "
                       "alguien de su sector, con dos botones; también se contesta escribiendo.",
    "tomar_la_tarea": "Pregunta a quien le quieren pasar una tarea si la toma, con dos botones; "
                      "también se contesta escribiendo.",
    "pase_para_decidir": "Mensaje de Leda, como Leda, a quien decide si una tarea de otra "
                         "persona pasa a alguien: quién lo pidió (pidio), quién la tiene "
                         "(la_tiene), a quién pasaría (pasaria_a) y para cuándo vence; consulta "
                         "si lo aprueba.",
    "pase_para_tomar": "Mensaje de Leda, como Leda, a quien le quieren pasar una tarea: quién lo "
                       "pidió (pidio), quién la tiene (la_tiene), para cuándo vence y, si "
                       "corresponde, quién lo aprobó (lo_aprobo) o que lo decide la misma "
                       "persona (tambien_lo_decide); consulta si la toma.",
    "como_termino_el_pase": "Aviso de cómo terminó el pase de una tarea: si quien la recibía "
                            "(pasaria_a) la tomó (la_tomo), si quien decidía no lo aprobó "
                            "(no_lo_aprobo, lo_decidio), si nadie contestó (sin_respuesta) o si "
                            "la tarea ya no se podía pasar (la_tarea_cambio), y quién la tiene "
                            "ahora (la_tiene). Es información: no pide respuesta.",
    "pidio": "Quién pidió pasar la tarea o, en el pedido del detalle, quién pidió verlo.",
    "lo_aprobo": "Quién aprobó que la tarea pase: el encargado del sector de quien la recibe.",
    "tambien_lo_decide": "Quien recibe este mensaje es también quien decide el pase: su "
                         "respuesta vale como la decisión.",
    "la_tomo": "Si quien recibía la tarea la tomó (verdadero) o no (falso).",
    "no_lo_aprobo": "Quien decidía no aprobó que la tarea pase: sigue con quien la tenía.",
    "lo_decidio": "Quién decidió el pase.",
    "por_que": "Por qué no aprobó el pase, no tomó la tarea o no compartió su detalle, con sus "
               "palabras.",
    "acepta": "Si la persona dice que sí (verdadero) o que no (falso).",
    "espera_su_decision_del_pase": "Una tarea de otra persona que quien la tiene (la_tiene) pidió "
                                   "pasar a alguien (pasaria_a): espera que la persona que "
                                   "escribe decida si lo aprueba. No es una tarea suya.",
    "espera_que_la_tome": "Una tarea de otra persona que le quieren pasar a la persona que "
                          "escribe (lo pidió pidio): espera que diga si la toma. Todavía no es "
                          "suya.",
    "otro_sector": "Quien escribe no puede pasarle la tarea a alguien de otro sector: eso lo "
                   "decide el encargado de su sector (quien_decide). No se le pasa el pedido a "
                   "nadie.",
    "sin_encargado": "El sector de quien recibiría la tarea no tiene a nadie que decida el "
                     "pase.",
    "es_la_misma_persona": "La persona nombró a sí misma: la tarea ya es suya.",
    "ya_hay_un_pase": "Ya se pidió pasar esa tarea (pase) y todavía no terminó: no se pide "
                      "otro.",
    "no_hay_un_pase": "Ninguna tarea espera que la persona decida un pase o que la tome.",
    "la_tarea_cambio": "La tarea ya no se puede pasar (se entregó o se cerró): el pase quedó "
                       "sin efecto.",
    "el_pase_ya_no_espera": "El pase ya no espera eso: se decidió, se tomó o terminó.",
    "cambio_quien_la_tiene": "La tarea pasó a otra persona: lo que se le consultaba a quien la "
                             "tenía ya no espera nada.",
    # Un pase que nadie contesta (decisión 26), el encargado que pasa una tarea de su gente (27) y
    # la revisión que sigue a quien era la tarea (28).
    "recordatorio_del_pase": "Mensaje de Leda, como Leda, que vuelve a hacer la consulta del "
                             "pase que la persona todavía no contestó (si lo aprueba o si toma "
                             "la tarea), por única vez; se contesta igual que la primera.",
    "se_lo_pregunto_el": "El día en que Leda le hizo la consulta por primera vez.",
    "si_sigue_sin_contestar": "Lo que pasa si la persona sigue sin contestar: ese día (fecha) "
                              "el pase termina y la tarea sigue con quien la tiene (sigue_con), "
                              "o el pedido del detalle termina sin compartirla "
                              "(no_se_comparte).",
    "no_se_comparte": "El detalle de la tarea no se comparte: nada cambia.",
    "sin_respuesta": "Nadie contestó la consulta del pase o del pedido del detalle (no_contesto "
                     "dice quién tenía que hacerlo), ni la primera vez ni cuando Leda la "
                     "repitió: terminó sin que nada cambie (la tarea sigue con quien la tenía; "
                     "el detalle no se compartió).",
    "no_contesto": "Quién tenía que contestar la consulta del pase o del pedido del detalle y no "
                   "contestó.",
    "puede_volver_a_pedirlo": "Quien pidió el detalle de la tarea puede volver a pedirlo.",
    "recordatorio_del_pedido_del_detalle": "Mensaje de Leda, como Leda, al encargado del sector "
                                           "de una tarea, que vuelve a hacer la consulta del "
                                           "pedido del detalle que todavía no contestó (si se lo "
                                           "comparte a pide_ver_el_detalle), por única vez; se "
                                           "contesta igual que la primera.",
    "puede_pedirselo_a_otra_persona": "Quien pidió el pase puede pedir pasarle la tarea a otra "
                                      "persona.",
    "era_suya": "La tarea era de quien recibe este mensaje: la pidió pasar el encargado de su "
                "sector (pidio), y ahora la tiene otra persona (la_tiene).",
    "aviso_a_quien_la_tenia": "Lo que se le avisa a quien tenía la tarea, que pasó a otra "
                              "persona: a quién (a) y cuándo se entera (llega).",
    "aviso_a_quien_se_le_preguntaba": "Lo que se le avisa a quien Leda le consultaba por el pase "
                                      "y no llegó a contestar, de cómo terminó: a quién (a) y "
                                      "cuándo se entera (llega).",
    "ya_no_espera_su_respuesta": "Leda le consultaba a quien recibe este mensaje por el pase "
                                 "(si lo aprobaba o si tomaba la tarea) o por el pedido del "
                                 "detalle (si lo compartía), que pidió pidio; terminó y ya no "
                                 "hace falta que conteste: Leda no le consulta más.",
    "no_es_de_su_sector": "La tarea nombrada es de otra persona (la_tiene) que no es de su "
                          "sector: quien escribe no la puede pasar.",
    "ya_la_tiene": "Quien recibiría la tarea es quien ya la tiene.",
    "la_aprueba_al_entregarla": "Quien entrega la tarea es quien la revisa (era de alguien de su "
                                "sector): al confirmarla queda aprobada por esa persona y, si no "
                                "falta nada más para cerrarla, terminada. Nadie más la revisa.",
    "la_aprobo_al_entregarla": "Quien entregó la tarea es quien la revisa: quedó aprobada por "
                               "esa persona; nadie más la revisa ni se entera para aprobarla.",
    "la_revisa_quien_la_hace": "Quien hace la tarea es también quien la revisa (era de alguien "
                               "de su sector): no hay a quién avisarle.",
}


# --- Los nombres para redactar (usuario, 2026-10-07) -----------------------------------------
#
# Los conceptos de la cocina: un nombre que lleva uno de éstos, o que es el de una jugada
# (`FICHAS`), nunca le llega a la IA que redacta.
#
# La espera de una decisión sobre una entrega es, para la persona, una revisión (decisión 18
# del usuario, 2026-10-08: "para aprobar" inclina la respuesta); "aprobar" queda para la
# decisión misma.
#
# Lo que escribe quien entrega es su descripción del trabajo (decisión 10: "describir", no
# "contar"), y a una entrega incompleta le falta algo para entregarla, no "evidencia" (C-3d, D7:
# la IA escribía "Sumé lo que contaste" y "Todavía no se puede entregar"; el modelo que aprobó
# el usuario dice "Sumé tu descripción" y "Para entregarla falta saber…").
#
# Cuando Leda le escribe a alguien para saber algo (después, a otra persona, o lo que ya le
# escribió antes), lo hace con una consulta, no con una pregunta (decisión 78 del usuario,
# 2026-10-12: "preguntar" suena a interrogatorio; la IA escribía "Le voy a preguntar a Ariel…" y
# "Te voy a preguntar cómo te fue"). "Pregunta" queda para la de este mensaje, el dato que nombra
# la instrucción de redacción, y para lo que pregunta la persona (`solo_si_pregunta`).
CONCEPTOS_DE_LA_COCINA = ("prevision", "comprometid", "referente", "dependiente", "escal",
                          "aviso_previo", "reencuadre", "repregunta", "de_estado", "el_estado",
                          "esperando_la_aprobacion", "para_aprobar", "aprobacion_trabada",
                          "aprobacion_destrabada", "lo_que_escribio", "falta_evidencia",
                          "le_pregunta", "a_preguntar", "pregunto", "preguntado",
                          "preguntas_sin", "pregunta_a_quien")


def es_un_concepto_de_la_cocina(nombre: str) -> bool:
    """Si un nombre nombra un concepto de la cocina: lleva uno o es el de una jugada."""
    return nombre in FICHAS or any(c in nombre for c in CONCEPTOS_DE_LA_COCINA)


# Cada nombre de la cocina que nombra un concepto, con el que recibe la IA que redacta: dice el
# hecho como lo vive la persona, con el mismo significado. Ninguno es un nombre de la cocina:
# dos cosas distintas nunca comparten un nombre.
PARA_LA_REDACCION: Mapping[str, str] = {
    # --- Claves de un hecho o de un aviso -------------------------------------------------------
    "prevision": "dia_que_dio_para_terminarla",
    "fecha_comprometida": "dia_en_que_vence",
    "atraso_si_se_cumple_la_prevision_dias_habiles":
        "atraso_si_la_termina_el_dia_que_dio_dias_habiles",
    "dependientes": "tareas_que_dependen_de_esta",
    "aviso_al_referente": "aviso_a_quien_aprueba_su_trabajo",
    "el_pedido_de_estado": "sigue_esperando_saber_como_viene",
    "vuelve_a_pedir_el_estado": "vuelve_a_consultar_como_viene",
    "no_vuelve_a_pedir_el_estado": "no_vuelve_a_consultar_como_viene",
    "escalado_a": "avisados_de_que_no_contestaba",
    "prevision_vencida": "el_dia_que_dio_para_terminarla_tambien_paso",
    "prevision_corregida": "dia_para_terminarla_corregido",
    "aviso_de_la_prevision_corregida": "aviso_del_dia_para_terminarla_corregido",
    "correccion_al_referente": "correccion_a_quien_aprueba_su_trabajo",
    "aviso_de_la_prevision_anterior": "aviso_del_dia_para_terminarla_que_vuelve_a_valer",
    "prevision_que_no_vale": "dia_para_terminarla_que_ya_no_vale",
    "prevision_vigente": "dia_para_terminarla_que_vale_ahora",
    "queda_esperando_la_aprobacion_de": "queda_esperando_la_revision_de",
    "pide_el_estado_el": "consulta_como_viene_el",
    "pedidos_de_estado_sin_respuesta": "veces_que_consulto_como_viene_sin_respuesta",
    "pedidos_de_estado_que_no_le_llegaron": "consultas_de_como_viene_que_no_le_llegaron",
    # A quién y cuándo le escribe Leda para saber algo (decisión 78).
    "le_pregunta_a": "le_consulta_a",
    "le_pregunta_como_le_fue": "le_consulta_como_le_fue",
    "le_pregunta_para_cuando": "le_consulta_para_cuando",
    "le_pregunta_tambien_a": "le_consulta_tambien_a",
    "le_vuelve_a_preguntar": "le_vuelve_a_consultar",
    "se_le_pregunta_a": "se_le_consulta_a",
    "se_lo_pregunto_el": "se_lo_consulto_el",
    "preguntado_el": "consultado_el",
    "preguntas_sin_respuesta": "consultas_sin_respuesta",
    "aviso_a_quien_se_le_preguntaba": "aviso_a_quien_se_le_consultaba",
    # --- Códigos: por qué no se hizo, no salió o ya no va a pasar ------------------------------
    "sin_fecha_comprometida": "sin_dia_en_que_vence",
    "nadie_pidio_el_estado": "no_le_habia_consultado_como_viene",
    "ya_se_escalo": "ya_se_aviso_que_no_contestaba",
    "misma_fecha_comprometida": "el_dia_que_dio_es_el_dia_en_que_vence",
    "sin_referente": "nadie_aprueba_su_trabajo",
    "hay_una_prevision_mas_nueva": "despues_dio_otro_dia_para_terminarla",
    "volvio_a_la_fecha_comprometida": "volvio_al_dia_en_que_vence",
    "reemplazado_por_el_reencuadre": "reemplazado_por_retomar_despues_de_la_ausencia",
    # --- Códigos: los avisos que Leda manda por su cuenta --------------------------------------
    "aviso_previo": "aviso_de_que_vence_pronto",
    "vencimiento_con_prevision": "vence_hoy_pero_dio_otro_dia_para_terminarla",
    "pedido_de_estado": "consulta_como_viene_la_tarea",
    "reencuadre": "retoma_despues_de_una_ausencia",
    "escalamiento": "aviso_de_que_no_contesta",
    "repregunta_de_estado": "vuelve_a_consultar_tras_una_respuesta_sin_algo_cierto",
    "repregunta": "vuelve_a_consultar_algo_sin_respuesta",
    "escalamiento_de_una_pregunta": "aviso_de_una_consulta_sin_respuesta",
    "pregunta_a_quien_destraba": "consulta_a_quien_destraba",
    "pregunta_a_quien_esta_trabado": "consulta_a_quien_esta_trabado",
    "nueva_prevision": "dio_otro_dia_para_terminar_su_tarea",
    "correccion_de_prevision": "el_dia_para_terminarla_que_recibio_ya_no_vale",
    "entrega_para_aprobar": "entrega_para_revisar",
    "lo_que_escribio": "su_descripcion",
    "le_falta_evidencia": "para_entregarla_falta",
    "aprobacion_trabada": "revision_trabada",
    "aprobacion_destrabada": "revision_destrabada",
    # --- Las jugadas, por lo que hacen (su ficha) ----------------------------------------------
    "anotar_bloqueo": "anotar_que_esta_trabada",
    "anotar_inicio": "anotar_que_arranco",
    "anotar_prevision": "anotar_para_cuando_la_termina",
    "anotar_quien_destraba": "anotar_quien_puede_destrabarla",
    "cancelar": "dejar_sin_efecto_la_pregunta",
    "consultar_pendientes": "contar_sus_tareas_pendientes",
    "corregir": "corregir_algo_ya_anotado",
    "dejar_para_despues": "dejar_la_pregunta_para_mas_tarde",
    "destrabar": "anotar_que_ya_puede_seguir",
    "elegir": "elegir_una_opcion",
    "entregar": "recibir_la_entrega",
    "confirmar": "confirmar_lo_que_vio",
    "guardar_para_la_entrega": "dejarlo_para_cuando_la_entregue",
    "informar_avance": "anotar_como_viene_sin_algo_cierto",
    "pedir_reasignacion": "pasarle_la_tarea_a_otra_persona",
    "contestar_el_pase": "decir_si_aprueba_el_pase_o_si_toma_la_tarea",
    "pedir_el_detalle": "pedirle_el_detalle_de_la_tarea_al_encargado_de_su_sector",
    "contestar_el_pedido_del_detalle": "decir_si_le_comparte_el_detalle_a_quien_lo_pidio",
    "aprobar": "aprobar_la_entrega",
    "pedir_cambios": "devolver_la_entrega_con_cambios",
    "ver_entrega": "mostrar_la_entrega_para_revisar",
    "pedir_enlace": "pasar_el_enlace_a_la_pagina_de_una_tarea",
    "decir_cuando_destraba": "anotar_para_cuando_destraba_la_tarea_de_otra_persona",
    "no_escribirle": "no_escribirle_a_quien_destraba",
    "decir_que_no_le_toca": "anotar_que_no_le_toca_destrabar_la_tarea_de_otra_persona",
    "contar_lo_que_arreglaron": "anotar_lo_que_arreglo_con_quien_la_destraba",
    "pedirselo_y_contar": "se_lo_pide_directamente_y_despues_cuenta",
    "decir_quien_es": "contestar_quien_es_alguien_que_nombro",
}
_DE_LA_COCINA = {para: de for de, para in PARA_LA_REDACCION.items()}

# Lo que alguien escribió, tal cual: un mensaje entero nunca se traduce, ni el nombre que alguien
# le puso a un archivo.
_LO_QUE_ALGUIEN_ESCRIBIO = frozenset({"mensaje", "texto", "nombre_del_archivo", "dice",
                                      "como_lo_nombro",
                                      "enlace", "lo_que_pide", "describe",
                                      "le_falta_del_criterio", "ejemplo", "lo_que_dice",
                                      "motivo_del_retiro", "referencias"})
# El nombre de un archivo nunca es un código, aunque se escriba como uno (`informe_final`).
# Ni lo que escribió en una pieza de una entrega, ni un enlace, ni el código de una cosa que
# pide la tarea, que es dato del pack (va con sus palabras, `en_palabras`).
_NUNCA_UN_CODIGO = frozenset({"nombre_del_archivo", "dice", "enlace", "tipo_de_evidencia",
                              "el_texto_cubre", "lo_que_pide", "describe",
                              "le_falta_del_criterio", "ejemplo", "lo_descrito_cubre",
                              "lo_que_dice", "motivo_del_retiro", "referencias",
                              "nombre_que_no_esta", "como_lo_nombro"})


def para_redactar(valor: Any) -> Any:
    """Una copia del pedido de redacción con el nombre de quien aprueba el trabajo de la persona
    dentro de `solo_si_pregunta` (`NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO`); a quién va cada aviso a
    otra persona y cuándo le llega, también (`AVISOS`, decisión 77); cada hora del reloj de un
    hecho, en su día; cada clave y cada código de la cocina que nombra un concepto cambiado por el
    suyo para redactar (`PARA_LA_REDACCION`) y cada día de `dias` en la forma corta con que se
    escribe (segunda vuelta del formato, 2026-10-07); de una tarea cerrada, nada de cuándo
    vencía (`_sin_vencimiento_si_cerro`); lo demás, tal cual."""
    return _traducir(_sin_nombre_ni_hora(_quien_aprueba_solo_si_pregunta(
        _sin_vencimiento_si_cerro(valor))))


def _traducir(valor: Any) -> Any:
    if isinstance(valor, Mapping):
        return {PARA_LA_REDACCION.get(k, k):
                v if k in _LO_QUE_ALGUIEN_ESCRIBIO
                else [_dia_para_redactar(d) for d in v]
                if k == "dias" and isinstance(v, (list, tuple))
                else _traducir(v)
                for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_traducir(v) for v in valor]
    if isinstance(valor, str):
        return PARA_LA_REDACCION.get(valor, valor)
    return valor


# --- Una tarea cerrada no vence (prueba por Telegram del 2026-10-12) ---------------------------
#
# A "pasame el link del dashboard de lotes", una tarea ya terminada, el resumen decía su estado y
# cuándo vencía, y Leda escribió "La tarea está terminada y aprobada. … vence pasado mañana." Un
# vencimiento no dice nada de una tarea que ya se cerró. La regla, en el borde de la redacción y
# para todos los hechos a la vez (los de la cocina no cambian: la base, el registro de turnos, las
# pruebas y la auditoría los leen): un dato que dice que su tarea está en un estado final no le
# pasa a la IA cuándo vencía, y `dias` deja de nombrar ese día si ningún otro dato lo trae.
ESTADOS_FINALES = frozenset({"terminada", "cancelada"})
CUANDO_VENCE = frozenset({"vence", "fecha_objetivo"})


def _sin_vencimiento_si_cerro(valor: Any) -> Any:
    """Una copia del valor sin cuándo vencía cada tarea que dice estar en un estado final
    (`ESTADOS_FINALES`) y, si el valor trae `dias`, sin el día de una fecha que ya no nombra
    ningún otro dato."""
    quitadas: set[date] = set()
    copia = _sin_vencimiento(valor, quitadas)
    if quitadas and isinstance(copia, dict) and isinstance(copia.get("dias"), (list, tuple)):
        sin_nombrar = quitadas - set(_fechas({k: v for k, v in copia.items() if k != "dias"}))
        copia["dias"] = [d for d in copia["dias"]
                         if not (isinstance(d, str) and _fecha_de_la_linea(d) in sin_nombrar)]
    return copia


def _sin_vencimiento(valor: Any, quitadas: set[date]) -> Any:
    if isinstance(valor, (list, tuple)):
        return [_sin_vencimiento(v, quitadas) for v in valor]
    if not isinstance(valor, Mapping):
        return valor
    cerro = valor.get("estado") in ESTADOS_FINALES
    copia: dict[str, Any] = {}
    for k, v in valor.items():
        if cerro and k in CUANDO_VENCE:
            quitadas.update(_fechas(v))
        elif k in _LO_QUE_ALGUIEN_ESCRIBIO:
            copia[k] = v
        else:
            copia[k] = _sin_vencimiento(v, quitadas)
    return copia


def _fecha_de_la_linea(linea: str) -> date | None:
    """La fecha de una línea de `dias` ("2026-10-16: viernes 16 de octubre, …")."""
    try:
        return date.fromisoformat(linea[:10])
    except ValueError:
        return None


# --- Quien aprueba el trabajo de la persona, sólo si lo pregunta (usuario, 2026-10-08) -------
#
# Decisión 11: Leda no nombra por su cuenta a quien aprueba el trabajo de la persona a la que le
# escribe (el referente de su área): ni como motivo (habla de la tarea) ni al contar un hecho
# ("La nueva fecha queda informada", no que esa persona será notificada). Si la persona
# pregunta a quién se le avisa o quién la revisa, Leda le dice el nombre.
#
# La IA escribe lo que dicen los hechos: el nombre a la vista invitaba a usarlo. Los hechos de
# la cocina no cambian (la base, el registro de turnos, las pruebas y la auditoría lo leen);
# en el borde, la redacción recibe el nombre dentro de `solo_si_pregunta`, en el mismo lugar
# del dato que lo nombra. La redacción ya trata siempre igual ese dato: lo cierto que dice sólo
# si la persona lo pregunta, también desde los últimos turnos. Lo demás del dato queda a la
# vista (cuándo se entera). Es por dato y no por persona: cada uno de éstos nombra siempre a
# quien aprueba el trabajo de la persona a la que Leda le escribe (a quien aprueba una entrega,
# el aviso de que se destrabó y lo que pasa si sigue sin decidir le nombran a quien está
# arriba, que aprueba su trabajo; quién aprobó o pidió cambios, en el aviso de la decisión a
# la persona responsable, es quien aprueba su trabajo, y a quien aprobó, él mismo). Los datos
# que nombran a otra persona quedan a la vista, salvo a quién va un aviso, que desde la decisión
# 77 nunca queda (`AVISOS`): a quien aprueba se le nombra a la persona
# responsable (`responsable`); a quien está arriba, quién tiene trabada
# la decisión (`quien_aprueba`); y a quien pide algo que decide otro, quién lo decide
# (`quien_decide`, `quien_aprueba` en `no_es_quien_aprueba`): es la respuesta a lo que pidió.
SOLO_SI_PREGUNTA = "solo_si_pregunta"

# Cada dato de la cocina que nombra a quien aprueba el trabajo de la persona, con la clave que
# lleva el nombre: la de un aviso (también en una lista de avisos), o `None` si el valor entero
# es el nombre (entonces el dato pasa entero a `solo_si_pregunta` del hecho que lo trae).
NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO: Mapping[str, str | None] = {
    "aviso_al_referente": "a",
    "aviso_a_quien_aprueba": "a",
    "correccion_al_referente": "a",
    "aviso_de_la_prevision_corregida": "a",
    "aviso_de_la_prevision_anterior": "a",
    "aviso_de_que_se_destrabo": "a",
    "escalado_a": "a",
    # La cadena de un bloqueo que nadie toma va al referente (C-5, porción 3): tampoco se lo
    # nombra por su cuenta (decisión 21: "voy a informar…").
    "aviso_de_la_cadena": "a",
    "si_no_hay_respuesta": "se_avisa_a",
    "si_sigue_sin_decidir": "se_avisa_a",
    # Lo que quedó asentado del atraso o del bloqueo de la persona (decisión 35): a quién le
    # llegó, sólo si lo pregunta.
    "queda_asentado": "a",
    "queda_esperando_la_aprobacion_de": None,
    "aprobada_por": None,
    "pidio_cambios": None,
}
# Lo anunciado antes que ya no va a pasar (`efectos.YA_NO_VA_A_PASAR`) dice con qué dato se
# contó: su nombre, en esta clave.
ANUNCIO = "anuncio"


def _quien_aprueba_solo_si_pregunta(valor: Any) -> Any:
    """Una copia del valor con el nombre de quien aprueba el trabajo de la persona dentro de
    `solo_si_pregunta`, en el mismo lugar del dato que lo nombra."""
    if isinstance(valor, (list, tuple)):
        return [_quien_aprueba_solo_si_pregunta(v) for v in valor]
    if not isinstance(valor, Mapping):
        return valor
    # Lo anunciado que ya no va a pasar nombra el dato con que se contó (`anuncio`, D7: "Ismael
    # no será informado…" al retirar un aviso): si ese dato nombra a quien aprueba el trabajo
    # de la persona, su nombre va aparte igual que en el dato mismo.
    anunciado = valor.get(ANUNCIO)
    clave_del_anuncio = (NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO.get(anunciado)
                         if isinstance(anunciado, str) else None)
    if clave_del_anuncio is not None:
        valor = _nombre_aparte(valor, clave_del_anuncio)
    copia: dict[str, Any] = {}
    aparte: dict[str, Any] = {}
    for k, v in valor.items():
        if k in _LO_QUE_ALGUIEN_ESCRIBIO:
            copia[k] = v
            continue
        if k in NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO:
            clave = NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO[k]
            if clave is None:
                aparte[k] = v
                continue
            v = _nombre_aparte(v, clave)
        copia[k] = _quien_aprueba_solo_si_pregunta(v)
    if aparte:
        copia[SOLO_SI_PREGUNTA] = {**copia.get(SOLO_SI_PREGUNTA, {}), **aparte}
    return copia


def _nombre_aparte(valor: Any, clave: str) -> Any:
    """Un aviso (o una lista de avisos) con `clave` dentro de su `solo_si_pregunta`. Si el aviso
    dice a quién va (`a`), también cuándo se entera, si es una hora (D8, prueba por Telegram del
    2026-10-08: "Quien la revisa será informado hoy a las 11:28"; el modelo del usuario, "Quedó
    entregada y pasa a revisión", no lo dice): como el nombre, se dice si la persona pregunta. Un
    código de si le llegó o no queda a la vista: es lo que pasó en el mundo."""
    if isinstance(valor, (list, tuple)):
        return [_nombre_aparte(v, clave) for v in valor]
    if not isinstance(valor, Mapping) or clave not in valor:
        return valor
    aparte = [clave]
    if clave == "a" and _es_una_hora(valor.get(LLEGA)):
        aparte.append(LLEGA)
    resto = {k: v for k, v in valor.items() if k not in aparte}
    resto[SOLO_SI_PREGUNTA] = {**resto.get(SOLO_SI_PREGUNTA, {}),
                               **{k: valor[k] for k in aparte}}
    return resto


# Cuándo se entera quien recibe un aviso (`fichas.LLEGA`): una fecha y hora, o un código.
LLEGA = "llega"


def _es_una_hora(valor: Any) -> bool:
    return isinstance(valor, str) and bool(re.match(r"^\d{4}-\d{2}-\d{2}T", valor))


# --- Un aviso a otra persona, sin su nombre ni su hora (decisión 77 del usuario, 2026-10-12) --
#
# En la prueba por Telegram, ocho mensajes dijeron a quién y a qué hora le llegaba un aviso
# ("Recibirá mi pregunta hoy a las 12:15", "Marcos será informado hoy de lo que dijiste",
# "Mañana a las 10:00 te voy a preguntar cómo te fue"): robótico, la hora del reloj no aporta y
# nombrar a quien se entera suena acusatorio. Ya lo pedían la constitución §8 ("Leda dice que
# algo quedó asentado, no a quién se lo contó") y la decisión 35. La IA escribe lo que dicen
# los hechos: cada hecho de un aviso le pasaba el destinatario (`a`) y la hora exacta (`llega`).
#
# La regla, para todos los avisos a la vez y no por mensaje, en el borde de la redacción (los
# hechos de la cocina no cambian): de un aviso a otra persona, la IA ve que hay un aviso (el
# dato que lo nombra) y si ya le llegó o no (un código); a quién va (`a`, `se_avisa_a`) y cuándo
# le llega, dentro de `solo_si_pregunta`. De lo que Leda le va a escribir a la misma persona
# (`AVISOS_A_LA_PERSONA`), cuándo: sólo el día, que la redacción escribe con las palabras de
# todos los días (`dias`: hoy, mañana, pasado mañana o su forma corta), y la hora aparte. Y
# ninguna otra hora del reloj de un hecho queda a la vista: su día, y la hora aparte. Si la
# persona pregunta a quién se le avisó y cuándo, la redacción lo tiene en `solo_si_pregunta`,
# también desde los últimos turnos (el paso 7 del guion de la Fase C).
#
# Un aviso es un dato con `llega`, o uno de éstos, que también se nombran sin `llega` (la persona
# trabada se entera de a quién le consulta Leda; lo que quedó asentado del atraso, decisión 35).
# `test_avisos_sin_nombre_ni_hora.py` recorre el código del motor: un aviso nuevo que no está acá
# hace fallar la prueba.
A = "a"
SE_AVISA_A = "se_avisa_a"
# Lo que Leda le va a escribir a la persona a la que le escribe ahora (nunca llevan `a`).
AVISOS_A_LA_PERSONA = frozenset({
    "proximo_aviso", "antes_le_recuerda_que_vence", "vuelve_a_pedir_el_estado",
    "le_vuelve_a_preguntar", "le_pregunta_como_le_fue", "le_pregunta_para_cuando"})
AVISOS = AVISOS_A_LA_PERSONA | frozenset({
    # A quien aprueba, revisa o está arriba.
    "aviso_al_referente", "aviso_a_quien_aprueba", "correccion_al_referente",
    "aviso_de_la_prevision_corregida", "aviso_de_la_prevision_anterior",
    "aviso_de_que_se_destrabo", "escalado_a", "queda_asentado", "aviso_de_la_cadena",
    # A la persona responsable, a la trabada y a quienes esperan.
    "aviso_al_responsable", "aviso_a_quien_esta_trabado", "aviso_a_quien_espera",
    # A quien destraba: la consulta de Leda y lo que se le avisa.
    "se_le_pregunta_a", "le_pregunta_tambien_a", "aviso_a_quien_destraba",
    "aviso_a_quien_destrababa", "aviso_de_que_sigue_haciendo_falta",
    # Un pase y un pedido del detalle: a quien decide, recibe, pidió o tenía la tarea.
    "le_pregunta_a", "aviso_a_quien_pidio", "aviso_a_quien_decidio", "aviso_a_quien_la_tenia",
    "aviso_a_quien_se_le_preguntaba", "aviso_a_quien_lo_pidio", "aviso_a_quienes_lo_pidieron",
    # Uno que no salió, y los del administrador, por su canal.
    "aviso_que_no_salio", "se_le_aviso_al_administrador", "aviso_al_administrador"})


def _sin_nombre_ni_hora(valor: Any, clave: str | None = None) -> Any:
    """Una copia del valor con a quién va cada aviso a otra persona y cuándo le llega dentro de
    `solo_si_pregunta`, y cada otra hora de un hecho en su día, con la hora ahí mismo. `clave`:
    el nombre del dato que trae el valor (el de una lista, para cada elemento)."""
    if isinstance(valor, (list, tuple)):
        return [_sin_nombre_ni_hora(v, clave) for v in valor]
    if not isinstance(valor, Mapping):
        return valor
    es_un_aviso = LLEGA in valor or clave in AVISOS
    a_la_persona = clave in AVISOS_A_LA_PERSONA and A not in valor
    # Cuándo pasó un turno de la conversación no es un hecho: el orden de los turnos lo dice.
    es_un_turno = "sentido" in valor
    copia: dict[str, Any] = {}
    aparte: dict[str, Any] = {}
    for k, v in valor.items():
        if k in _LO_QUE_ALGUIEN_ESCRIBIO or k == SOLO_SI_PREGUNTA or (es_un_turno and k == "at"):
            copia[k] = v
        elif k == SE_AVISA_A or (es_un_aviso and k == A):
            aparte[k] = v
        elif k == LLEGA and es_un_aviso and not a_la_persona and _es_una_hora(v):
            aparte[k] = v
        elif _es_una_hora(v):
            copia[k], aparte[k] = v[:10], v
        else:
            copia[k] = _sin_nombre_ni_hora(v, k)
    if aparte:
        copia[SOLO_SI_PREGUNTA] = {**copia.get(SOLO_SI_PREGUNTA, {}), **aparte}
    return copia


# --- Los días de las fechas (tercera vuelta de ajuste, usuario, 2026-10-06) ------------------
#
# Ronda 2: la IA calculó mal el día de la semana o el "mañana" desde una fecha AAAA-MM-DD. El
# código los sabe: cada pedido a la IA lleva, para cada fecha que trae, su día de la semana y,
# si corresponde, si es hoy, ayer, mañana o pasado mañana (`dias`); para elegir jugadas,
# también los de los próximos días, para que una fecha que la persona nombra por su día salga
# de ahí y no de una cuenta. Una fecha con hora se toma por su día tal como está escrita.

#
# Segunda vuelta del formato (usuario, 2026-10-07): en los mensajes, fechas cortas, el día
# abreviado y el número con el mes. La redacción recibe cada día ya en esa forma
# (`para_redactar`), para copiarlo; la elección de jugadas lo sigue recibiendo largo, porque
# la persona nombra los días enteros y así los encuentra.

_FECHA = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:$|T)")
_DIAS_DE_LA_SEMANA = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
_DIAS_CORTOS = ("lun", "mar", "mié", "jue", "vie", "sáb", "dom")
_MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
          "septiembre", "octubre", "noviembre", "diciembre")
_RELATIVOS = {-1: "ayer", 0: "hoy", 1: "mañana", 2: "pasado mañana"}


def _fechas(valor: Any) -> Iterator[date]:
    if isinstance(valor, Mapping):
        for v in valor.values():
            yield from _fechas(v)
    elif isinstance(valor, (list, tuple)):
        for v in valor:
            yield from _fechas(v)
    elif isinstance(valor, str):
        encontrada = _FECHA.match(valor)
        if encontrada:
            try:
                yield date.fromisoformat(encontrada.group(1))
            except ValueError:
                return


def dia(fecha: date, hoy: date | None = None) -> str:
    """"2026-10-23: viernes 23 de octubre", con ", mañana" (o hoy, ayer, pasado mañana) si
    corresponde."""
    texto = (f"{fecha.isoformat()}: {_DIAS_DE_LA_SEMANA[fecha.weekday()]} {fecha.day} de "
             f"{_MESES[fecha.month - 1]}")
    relativo = _RELATIVOS.get((fecha - hoy).days) if hoy is not None else None
    return f"{texto}, {relativo}" if relativo else texto


def dias(pedido: Mapping[str, Any], *, proximos: int = 0) -> list[str]:
    """El día de cada fecha del pedido (y de los `proximos` días desde hoy), en orden."""
    hoy = next(_fechas(pedido.get("hoy")), None)
    fechas = set(_fechas(pedido))
    if hoy is not None:
        fechas.update(hoy + timedelta(days=n) for n in range(proximos + 1))
    return [dia(f, hoy) for f in sorted(fechas)]


def dia_corto(fecha: date) -> str:
    """"vie 23/10": el día abreviado y el número con el mes, sin ceros."""
    return f"{_DIAS_CORTOS[fecha.weekday()]} {fecha.day}/{fecha.month}"


_DIA_LARGO = re.compile(r"^(\d{4}-\d{2}-\d{2}): [^,]+(, .+)?$")


def _dia_para_redactar(linea: Any) -> Any:
    """Un día de `dias` en la forma corta con que se escribe, con su relación con hoy: de
    "2026-10-23: viernes 23 de octubre, mañana" a "2026-10-23: vie 23/10, mañana". Lo que no
    tiene esa forma queda tal cual."""
    encontrada = _DIA_LARGO.match(linea) if isinstance(linea, str) else None
    if encontrada is None:
        return linea
    try:
        fecha = date.fromisoformat(encontrada.group(1))
    except ValueError:
        return linea
    return f"{fecha.isoformat()}: {dia_corto(fecha)}{encontrada.group(2) or ''}"


def significado(nombre: str) -> str | None:
    """Qué significa una clave o un código; una jugada, por su ficha; un nombre para redactar,
    lo mismo que el de la cocina que reemplaza."""
    nombre = _DE_LA_COCINA.get(nombre, nombre)
    if nombre in SIGNIFICADOS:
        return SIGNIFICADOS[nombre]
    ficha = FICHAS.get(nombre)
    return f"La jugada de {ficha.para_que}." if ficha is not None else None


def _nombres(valor: Any) -> Iterator[str]:
    """Cada clave y cada código de un valor, en el orden en que aparecen."""
    if isinstance(valor, Mapping):
        for k, v in valor.items():
            yield str(k)
            if k not in _NUNCA_UN_CODIGO:
                yield from _nombres(v)
    elif isinstance(valor, (list, tuple)):
        for v in valor:
            yield from _nombres(v)
    elif isinstance(valor, str) and (_CODIGO.match(valor) or significado(valor) is not None):
        yield valor         # un código; uno de una sola palabra, si está en la lista


def sin_significado(valor: Any) -> set[str]:
    """Las claves y los códigos de un valor que no tienen significado."""
    return {n for n in _nombres(valor) if significado(n) is None}


# Los significados son para que la IA entienda los datos, nunca un texto para decir: en la
# ronda 2 una línea de significado se le repitió a la persona (tercera vuelta, 2026-10-06).
ENCABEZADO_DEL_BLOQUE = (
    "Lista de significados de los datos y códigos de este pedido. Es sólo para entender los "
    "datos: nunca se le dice ni se le repite a la persona.")


def bloque(valor: Any) -> str:
    """Lo que significa cada clave y cada código de un pedido a la IA, una línea por nombre,
    sólo de lo que el pedido usa."""
    vistos = list(dict.fromkeys(n for n in _nombres(valor) if significado(n) is not None))
    return "\n".join([ENCABEZADO_DEL_BLOQUE]
                     + [f"- {n}: {significado(n)}" for n in vistos])


# --- Un ícono por estado en las listas de tareas (decisión 79 del usuario, 2026-10-12) ---------
#
# Con un solo ícono para todas hay que leer para saber cómo va; con uno por estado, "todo verde"
# ya es la buena noticia (constitución §8). El verde sólo dice lo que Leda sabe (§4). Los pone la
# cocina, no la IA (regla del mozo; decisión 74, la cocina da la forma del mensaje): el estado de
# cada tarea de una lista sale de los hechos que la cocina armó para ese mensaje, y la marca de su
# renglón se cambia en el texto (`salida.iconos_por_estado`). Las listas son las que la cocina arma
# como listas: el informe al grupo (`informe_al_grupo.py`), la lista de la cadencia de cada
# persona (`cadencias.py`), lo que la persona tiene pendiente (`consultar_pendientes`), la lista
# de entregas para revisar y un envío que junta avisos de varias tareas (`avisos.py`). Una lista
# es de dos tareas o más: el 📋 de un mensaje
# sobre una sola tarea no cambia. Las tareas que un hecho nombra al hablar de otra (las que
# dependen de ella, las que espera) no son una lista.

# El informe al grupo ya decidió en qué lista va cada tarea (un atraso, sólo el hablado en
# privado); las que siguen su curso, por su estado.
_ICONO_DE_CADA_LISTA_DEL_INFORME = {
    "terminadas": salida.ICONO_TERMINADA, "atrasadas": salida.ICONO_ATRASADA,
    "trabadas": salida.ICONO_TRABADA, "entregadas": salida.ICONO_ENTREGADA,
    "sin_saber_como_vienen": salida.ICONO_SIN_NOVEDADES}


def icono_del_estado(tarea: Mapping[str, Any], hoy: str) -> str:
    """El ícono del estado de una tarea, por lo que dicen sus hechos (`hoy`, AAAA-MM-DD):
    terminada; trabada; entregada (aunque haya vencido); atrasada si venció o si el día que dio la
    persona es posterior al vencimiento; sin novedades si Leda le preguntó cómo viene y no contó,
    o si no la empezó; y al día sólo en curso, sin nada de eso."""
    estado = tarea.get("estado")
    if estado == "terminada":
        return salida.ICONO_TERMINADA
    if estado == "bloqueada" or tarea.get("causas"):
        return salida.ICONO_TRABADA
    if estado == "en_revision":
        return salida.ICONO_ENTREGADA
    vence = tarea.get("vence")
    prevision = tarea.get("prevision_vigente")
    dio = prevision.get("fecha") if isinstance(prevision, Mapping) else None
    if vence and (vence < hoy or (dio and dio > vence)):
        return salida.ICONO_ATRASADA
    if estado != "en_curso" or tarea.get("sin_respuesta_desde"):
        return salida.ICONO_SIN_NOVEDADES
    return salida.ICONO_AL_DIA


def _tareas_de_las_listas(hecho: Mapping[str, Any], hoy: str) -> Iterator[tuple[str, str]]:
    """Cada tarea de una lista que trae el hecho, con el ícono de su estado."""
    if hecho.get("aviso") == "informe_al_grupo":
        for lista, icono in _ICONO_DE_CADA_LISTA_DEL_INFORME.items():
            for renglon in hecho.get(lista) or []:
                yield renglon["tarea"], icono
        for renglon in hecho.get("siguen") or []:
            yield renglon["tarea"], icono_del_estado(renglon, hoy)
    elif hecho.get("aviso") == "entrega_en_la_lista":
        yield hecho["tarea"], salida.ICONO_ENTREGADA
    elif hecho.get("aviso") and isinstance(hecho.get("tarea"), str):
        # Un aviso de una tarea; varios de distintas tareas en un mensaje son una lista
        # (`avisos._con_el_estado_de_cada_tarea`).
        yield hecho["tarea"], icono_del_estado(hecho, hoy)
    elif hecho.get("jugada") == "consultar_pendientes":
        for tarea in hecho.get("tareas") or []:
            yield tarea["titulo"], icono_del_estado(tarea, hoy)
    for renglon in hecho.get("sus_tareas") or []:
        yield renglon["tarea"], icono_del_estado(renglon, hoy)


def iconos_de_las_listas(pedido: Mapping[str, Any]) -> dict[str, str]:
    """El ícono del estado de cada tarea de las listas de un pedido de redacción, por su título
    completo; vacío si el mensaje no tiene una lista de dos tareas o más."""
    iconos: dict[str, str] = {}
    for hecho in pedido.get("hechos") or []:
        if isinstance(hecho, Mapping):
            iconos.update(_tareas_de_las_listas(hecho, str(pedido.get("hoy") or "")))
    return iconos if len(iconos) > 1 else {}


# Poner los íconos es lo último, después de que redacta la IA: si falla, el mensaje sale igual,
# tal como lo redactó la IA, y queda un incidente de severidad baja (nunca fallar en silencio;
# revisión RDD `review-fd5b12f57ba236dc`). Uno por espacio y por día: una falla del código se
# repetiría en cada mensaje.
ETAPA_ICONOS_POR_ESTADO = "motor_iconos_por_estado"


def con_los_iconos(texto: str, pedido: Mapping[str, Any], cur, workspace_id: str) -> str:
    """Lo que redactó la IA, con el ícono del estado de cada tarea de sus listas; si ponerlos
    falla, lo que redactó la IA, tal cual, con su incidente."""
    try:
        return salida.iconos_por_estado(texto, iconos_de_las_listas(pedido))
    except Exception as falla:  # noqa: BLE001 -- los íconos nunca frenan un mensaje
        try:
            with cur.connection.transaction():
                registrar_incidente(
                    cur, workspace_id,
                    "No se pudo poner el ícono del estado de cada tarea en un mensaje: salió "
                    "como lo redactó la IA, sin los íconos.",
                    severidad="baja", referencia_cruda=f"{type(falla).__name__}: {falla}",
                    etapa=ETAPA_ICONOS_POR_ESTADO,
                    clave=f"{ETAPA_ICONOS_POR_ESTADO}:{pedido.get('hoy')}")
        except Exception:  # noqa: BLE001 -- sin incidente, el mensaje igual sale
            pass
        return texto
