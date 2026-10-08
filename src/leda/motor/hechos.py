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
                         "la persona describió en la entrega.",
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
    "sumo": "Las piezas (por su alias) que se sumaron a la entrega con este mensaje.",
    "sacadas": "Las piezas que la persona sacó de la entrega antes de confirmarla: no van.",
    "retiradas": "Las piezas ya entregadas que la persona retiró: dejan de valer, nada se "
                 "borra.",
    "como_queda": "Cómo queda la entrega después de esto, con su código.",
    "reemplazada": "Esa vista de la entrega dejó de valer porque cambió lo que mostraba: la "
                   "reemplazó otra.",
    "para_cuando_la_entregue": "Lo que la persona mandó y queda en la conversación para "
                               "mostrárselo cuando entregue esa tarea: no es parte de una "
                               "entrega todavía.",
    "lo_que_escribio": "Lo que escribió quien entrega la tarea: su descripción del trabajo.",
    "el_ejemplo_que_acepto": "El ejemplo que Leda le propuso para lo que faltaba y la persona "
                             "aceptó tal cual: vale como lo que describe, aunque no lo "
                             "escribió ella.",
    "una_foto": "Una foto.",
    "un_video": "Un video.",
    "un_archivo": "Un archivo.",
    "un_enlace": "Un enlace.",
    "para_confirmar": "La entrega tiene todo lo que pide la tarea: espera que la persona la "
                      "confirme, con el botón o escribiendo.",
    "le_falta_evidencia": "A la entrega le falta algo de lo que pide la tarea: le_falta y "
                          "le_falta_del_criterio dicen qué.",
    "entregada": "La tarea quedó entregada y pasa a revisión: espera que quien aprueba el "
                 "trabajo de la persona la revise y decida. No está terminada ni aprobada.",
    "no_vale_la_confirmacion": "La confirmación no vale (motivo dice por qué) y se muestra la "
                               "entrega como quedó (como_queda).",
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
                "hizo ninguna y Leda pregunta cuál.",
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
                    "dice a la vez dos cosas opuestas, o aprueba con un comentario para la "
                    "persona responsable. No se hizo ninguna y Leda pregunta cuál de las dos.",
    "su_propio_trabajo": "Es trabajo de la persona que escribe: no lo puede aprobar ni devolver "
                         "ella; lo decide quien aprueba su trabajo.",
    "no_es_quien_aprueba": "La persona que escribe no es quien aprueba ese trabajo: lo decide "
                           "otra persona (quien_aprueba), y no cambió nada.",
    "nada_para_decidir": "No hay una entrega de esa persona esperando la decisión de quien "
                         "escribe.",
    "persona_desconocida": "No hay nadie en el equipo con ese nombre.",
    "ya_la_aprobo": "La persona que escribe ya la había aprobado: no se anota otra vez.",
    "la_entrega_se_esta_completando": "La persona responsable sacó algo de lo que entregó y "
                                      "está completando la entrega: así todavía no se aprueba "
                                      "y no cambió nada.",
    "se_le_avisa_cuando_este_completa": "Cuando la entrega esté completa, a quien la revisa le "
                                        "llega un aviso nuevo con todo. Todavía no pasó.",
    "cambio_la_entrega": "La entrega cambió desde el aviso que tenía ese botón: el botón ya no "
                         "vale; se decide sobre lo que vale ahora.",
    "decision_de_la_entrega": "Pregunta si quien aprueba aprueba la entrega o le pide cambios: "
                              "lo puede tocar o escribir.",
    "que_cambios_pide": "Pregunta qué le falta o qué hay que cambiar de la entrega: espera lo "
                        "que pide quien la aprueba.",
    "cual_de_las_dos": "Pregunta, una sola vez, cuál de las dos cosas quiso decir la persona "
                       "sobre la tarea: su respuesta elige una (una opción, o esa decisión "
                       "escrita), y lo demás que diga es su comentario, no la otra cosa. Si no "
                       "elige, no se vuelve a preguntar.",
    "no_eligio": "La persona contestó sin elegir ninguna opción de una pregunta que Leda hace "
                 "una sola vez: Leda no decide por ella ni la vuelve a preguntar. Lo que esperaba "
                 "esa decisión sigue esperándola, y las opciones van como botones en este mensaje "
                 "(botones), para cuando quiera; también lo puede escribir.",
    "pregunta_hecha_una_vez": "La pregunta, ya hecha, que no se vuelve a hacer: su tipo.",
    "botones": "Los botones que lleva este mensaje, por lo que dicen: atajos para cuando la "
               "persona quiera, que también se pueden escribir. No son una pregunta que espere "
               "respuesta.",
    # --- Las entregas en listas (decisión 17 del usuario, 2026-10-08; C-3d, D4) --------------
    "queda_por_revisar": "Las otras entregas que esperan la revisión de la persona que escribe, "
                         "cada una con quién la entregó: le quedan por revisar. Leda no insiste "
                         "hoy; mañana se las recuerda.",
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
    "espera_el_motivo": "El aviso espera el porqué que Leda le preguntó a la persona: si lo "
                        "da antes, sale otro aviso que lo lleva; si no, sale a la hora de "
                        "llega y dice que todavía no lo dio.",
    "sin_motivo_todavia": "La persona todavía no dio el porqué de ese día: Leda se lo "
                          "preguntó y espera la respuesta. No hay un porqué que contar.",
    "a": "A quién va un aviso.",
    "llega": "Cuándo se entera quien recibe el aviso (a; sin a, la persona a la que Leda le "
             "escribe): una fecha y hora es el momento en que le llega, que todavía no pasó; "
             "si no, su código dice si ya le llegó, si no le va a llegar o si no le llegó.",
    "quien_destraba": "Quién puede destrabar el bloqueo: como dato, lo que dijo la persona; "
                      "como tipo de pregunta, Leda pregunta quién lo puede destrabar y espera "
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
    "vuelve_a_pedir_el_estado": "Cuándo Leda le vuelve a preguntar a la persona cómo viene "
                                "la tarea (llega, todavía no pasó); o que ya no se lo va a "
                                "preguntar, y motivo dice por qué.",
    "veces_sin_algo_cierto": "Cuántas respuestas seguidas sin un hecho cierto tuvo esta "
                             "pregunta de cómo viene la tarea.",
    "no_vuelve_a_pedir_el_estado": "Por qué Leda no le vuelve a preguntar cómo viene la tarea.",
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
    "numero": "Cuántas veces seguidas, contando ésta, Leda le pregunta cómo viene la tarea "
              "sin que conteste.",
    "responsable": "La persona responsable de la tarea.",
    "prevision_vigente": "El día que la persona dio para terminar la tarea y que vale ahora: "
                         "ese día, el atraso que tendrá si la termina ese día, su porqué y si "
                         "quien aprueba su trabajo ya se enteró o cuándo se entera.",
    "fecha": "Una fecha.",
    "pide_el_estado_el": "El día en que Leda le va a preguntar cómo viene la tarea: todavía "
                         "no pasó.",
    "si_no_hay_respuesta": "Lo que va a pasar si la persona no contesta: a quién se le va a "
                           "avisar. Todavía no pasó.",
    "se_avisa_a": "A quiénes se les va a avisar.",
    "avance_anterior": "Lo que la persona contestó antes sin un hecho cierto, y cuándo.",
    "el": "El día en que pasó.",
    "espera_algo_cierto": "Lo que Leda necesita saber de la tarea: un hecho cierto.",
    "seguimiento_por": "Desde qué día Leda sigue la tarea: el día que la persona dio para "
                       "terminarla, si es posterior al día en que vence.",
    "pedido_desde": "Desde cuándo Leda le pregunta cómo viene la tarea sin respuesta.",
    "pedidos_de_estado_sin_respuesta": "Cuántas veces Leda le preguntó cómo viene la tarea "
                                       "sin que contestara.",
    "pedidos_anteriores_que_no_le_llegaron": "Preguntas anteriores de cómo viene la tarea que "
                                             "no le llegaron a la persona: no se le habla como "
                                             "si las hubiera recibido.",
    "pedidos_de_estado_que_no_le_llegaron": "Preguntas de cómo viene la tarea que no le "
                                            "llegaron a la persona.",
    "avance_sin_algo_cierto": "Lo que la persona contestó antes sin un hecho cierto.",
    "ausencia": "La ausencia de la persona, con desde y hasta.",
    "desde": "Desde cuándo.",
    "hasta": "Hasta cuándo.",
    "sobre": "Lo anotado sobre lo que se pregunta.",
    "preguntas_sin_respuesta": "Cuántas veces se hizo la pregunta sin respuesta.",
    "preguntado_el": "Cuándo se hizo la pregunta por primera vez.",
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
    # --- Códigos: los avisos que Leda manda por su cuenta --------------------------------------
    "aviso_previo": "Aviso de que la tarea vence pronto; no pide respuesta.",
    "vencimiento_proximo": "La tarea vence pronto; no pide respuesta.",
    "vencimiento_con_prevision": "La tarea vence hoy, pero la persona ya dijo otro día para "
                                 "terminarla: no pide nada.",
    "pedido_de_estado": "Leda pregunta cómo viene la tarea: espera algo cierto.",
    "reencuadre": "Leda retoma el seguimiento después de una ausencia.",
    "vuelta_de_ausencia": "La persona volvió de una ausencia: Leda retoma el seguimiento.",
    "escalamiento": "Aviso a quien corresponde de que la persona no contesta.",
    "falta_de_respuesta": "La persona no contestó los pedidos: se le avisa a quien "
                          "corresponde.",
    "repregunta_de_estado": "Leda vuelve a preguntar cómo viene la tarea después de una "
                            "respuesta sin un hecho cierto.",
    "repregunta": "Leda vuelve a hacer una pregunta que no tuvo respuesta.",
    "escalamiento_de_una_pregunta": "Aviso a quien corresponde de que una pregunta quedó sin "
                                    "respuesta.",
    "nueva_prevision": "Aviso a quien aprueba el trabajo de la persona responsable: dio un "
                       "día nuevo para terminar su tarea. Es información para él; no pide "
                       "respuesta.",
    "correccion_de_prevision": "Aviso a quien aprueba el trabajo de la persona responsable: "
                               "el día para terminar la tarea que ya recibió no vale.",
    "entrega_para_aprobar": "Aviso a quien aprueba el trabajo de la persona responsable: "
                            "entregó la tarea, que espera su revisión y su decisión: aprobarla "
                            "o pedirle cambios, con un botón o escribiendo.",
    "falla_de_aviso": "Un aviso que la persona causó no le llegó a quien iba.",
    "lleva_el_enlace_a_la_pagina_de_la_tarea":
        "Al final de este mensaje, el código agrega un enlace personal a la página de la "
        "tarea, de sólo lectura, con la tarea, lo que fue pasando y lo que se entregó. La IA no "
        "lo ve ni lo escribe: no hay ninguna dirección para escribir.",
    "no_salio_un_aviso": "Un aviso que la persona causó no le llegó a quien iba.",
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
CONCEPTOS_DE_LA_COCINA = ("prevision", "comprometid", "referente", "dependiente", "escal",
                          "aviso_previo", "reencuadre", "repregunta", "de_estado", "el_estado",
                          "esperando_la_aprobacion", "para_aprobar", "aprobacion_trabada",
                          "aprobacion_destrabada", "lo_que_escribio", "falta_evidencia")


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
    "vuelve_a_pedir_el_estado": "vuelve_a_preguntar_como_viene",
    "no_vuelve_a_pedir_el_estado": "no_vuelve_a_preguntar_como_viene",
    "escalado_a": "avisados_de_que_no_contestaba",
    "prevision_vencida": "el_dia_que_dio_para_terminarla_tambien_paso",
    "prevision_corregida": "dia_para_terminarla_corregido",
    "aviso_de_la_prevision_corregida": "aviso_del_dia_para_terminarla_corregido",
    "correccion_al_referente": "correccion_a_quien_aprueba_su_trabajo",
    "aviso_de_la_prevision_anterior": "aviso_del_dia_para_terminarla_que_vuelve_a_valer",
    "prevision_que_no_vale": "dia_para_terminarla_que_ya_no_vale",
    "prevision_vigente": "dia_para_terminarla_que_vale_ahora",
    "queda_esperando_la_aprobacion_de": "queda_esperando_la_revision_de",
    "pide_el_estado_el": "pregunta_como_viene_el",
    "pedidos_de_estado_sin_respuesta": "veces_que_pregunto_como_viene_sin_respuesta",
    "pedidos_de_estado_que_no_le_llegaron": "preguntas_de_como_viene_que_no_le_llegaron",
    # --- Códigos: por qué no se hizo, no salió o ya no va a pasar ------------------------------
    "sin_fecha_comprometida": "sin_dia_en_que_vence",
    "nadie_pidio_el_estado": "no_le_habia_preguntado_como_viene",
    "ya_se_escalo": "ya_se_aviso_que_no_contestaba",
    "misma_fecha_comprometida": "el_dia_que_dio_es_el_dia_en_que_vence",
    "sin_referente": "nadie_aprueba_su_trabajo",
    "hay_una_prevision_mas_nueva": "despues_dio_otro_dia_para_terminarla",
    "volvio_a_la_fecha_comprometida": "volvio_al_dia_en_que_vence",
    "reemplazado_por_el_reencuadre": "reemplazado_por_retomar_despues_de_la_ausencia",
    # --- Códigos: los avisos que Leda manda por su cuenta --------------------------------------
    "aviso_previo": "aviso_de_que_vence_pronto",
    "vencimiento_con_prevision": "vence_hoy_pero_dio_otro_dia_para_terminarla",
    "pedido_de_estado": "pregunta_como_viene_la_tarea",
    "reencuadre": "retoma_despues_de_una_ausencia",
    "escalamiento": "aviso_de_que_no_contesta",
    "repregunta_de_estado": "vuelve_a_preguntar_tras_una_respuesta_sin_algo_cierto",
    "repregunta": "vuelve_a_hacer_una_pregunta_sin_respuesta",
    "escalamiento_de_una_pregunta": "aviso_de_una_pregunta_sin_respuesta",
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
    "aprobar": "aprobar_la_entrega",
    "pedir_cambios": "devolver_la_entrega_con_cambios",
    "ver_entrega": "mostrar_la_entrega_para_revisar",
}
_DE_LA_COCINA = {para: de for de, para in PARA_LA_REDACCION.items()}

# Lo que alguien escribió, tal cual: un mensaje entero nunca se traduce, ni el nombre que alguien
# le puso a un archivo.
_LO_QUE_ALGUIEN_ESCRIBIO = frozenset({"mensaje", "texto", "nombre_del_archivo", "dice",
                                      "enlace", "lo_que_pide", "describe",
                                      "le_falta_del_criterio", "ejemplo"})
# El nombre de un archivo nunca es un código, aunque se escriba como uno (`informe_final`).
# Ni lo que escribió en una pieza de una entrega, ni un enlace, ni el código de una cosa que
# pide la tarea, que es dato del pack (va con sus palabras, `en_palabras`).
_NUNCA_UN_CODIGO = frozenset({"nombre_del_archivo", "dice", "enlace", "tipo_de_evidencia",
                              "el_texto_cubre", "lo_que_pide", "describe",
                              "le_falta_del_criterio", "ejemplo", "lo_descrito_cubre"})


def para_redactar(valor: Any) -> Any:
    """Una copia del pedido de redacción con el nombre de quien aprueba el trabajo de la persona
    dentro de `solo_si_pregunta` (`NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO`), cada clave y cada
    código de la cocina que nombra un concepto cambiado por el suyo para redactar
    (`PARA_LA_REDACCION`) y cada día de `dias` en la forma corta con que se escribe (segunda
    vuelta del formato, 2026-10-07); lo demás, tal cual."""
    return _traducir(_quien_aprueba_solo_si_pregunta(valor))


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
# que nombran a otra persona quedan a la vista: a quien aprueba se le nombra a la persona
# responsable (`aviso_al_responsable`, `responsable`); a quien está arriba, quién tiene trabada
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
    "si_no_hay_respuesta": "se_avisa_a",
    "si_sigue_sin_decidir": "se_avisa_a",
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
    """Un aviso (o una lista de avisos) con `clave` dentro de su `solo_si_pregunta`."""
    if isinstance(valor, (list, tuple)):
        return [_nombre_aparte(v, clave) for v in valor]
    if not isinstance(valor, Mapping) or clave not in valor:
        return valor
    resto = {k: v for k, v in valor.items() if k != clave}
    resto[SOLO_SI_PREGUNTA] = {**resto.get(SOLO_SI_PREGUNTA, {}), clave: valor[clave]}
    return resto


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
