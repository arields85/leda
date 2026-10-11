# Transcripciones de la ronda fase-c-apodos-quien-destraba

Para leer contra lo que cada paso dice y no dice (decisión 10.3). Cada casilla la marca quien lee.

## 25 · Mensajes sin puntuación · vez 1

Fuente: `tests/conversaciones/25-sin-puntuacion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G FALLA · C FALLA · M ok · F FALLA.

**Paso 1.** Leda (2026-10-19 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-19) → Marcos:
  > Se acercan estos vencimientos:
  >
  > 🗓️ Programar PLC de la comprimidora — jue 22/10  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — jue 22/10
  >
  > No hace falta responder.
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- [ ] dice: las dos tareas de Marcos, cada una en su renglón con 🗓️ y su fecha corta, el jue 22/10
- [ ] dice: que no hace falta contestar, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-19 10:40): «con el PLC estoy compliacdo, me falta el cable para programar comunicaciones estimo que la tengo para el viernes 23»
- jugadas: `[{"nombre": "anotar_bloqueo", "causa": "me falta el cable para programar comunicaciones"}, {"nombre": "anotar_prevision", "fecha": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}, {"jugada": "anotar_prevision", "resultado": "falta_dato", "falta": ["tarea"], "pregunta_para_despues": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 11788 ms
- Leda → Marcos: [botones: PLC, COM]
  > Para anotar que te falta el cable para programar comunicaciones y que estimás terminar el viernes 23, necesito saber de cuál tarea hablás.
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿A cuál de las dos te referís? Podés tocar una opción o escribirla.
- [ ] dice: cada tarea en su bloque, primero su renglón con 📋 y su nombre solo y debajo, con ✏️, lo anotado: la del PLC está trabada porque le falta el cable para programar; la de comunicaciones la termina el vie 23/10
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, un día hábil de atraso
- [ ] dice: que la fecha nueva queda informada, en pasiva y en futuro, sin nombrar a Ismael
- [ ] dice: una sola pregunta, sola y en el último renglón: quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una causa del bloqueo que nombre las comunicaciones
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: dos preguntas juntas
- [ ] no dice: negrita
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'anotar_bloqueo', 'causa': 'me falta el cable para programar comunicaciones'}, {'nombre': 'anotar_prevision', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones'}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real {'escrito': [], 'faltan': [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}]}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real {'escrito': [], 'faltan': [{'tarea': 'PLC', 'causa': 'presente'}]}
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente', 'sin_motivo_todavia': True}}], real {'escrito': [], 'faltan': [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente', 'sin_motivo_todavia': True}}]}
- **falla** [comprension] botones: esperado [], real ['PLC', 'COM']
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real {'tipo': 'cual_tarea', 'opciones': [{'opcion': 'O1', 'etiqueta': 'PLC', 'tarea': 'PLC'}, {'opcion': 'O2', 'etiqueta': 'COM', 'tarea': 'COM'}], 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente', 'pregunta_para_despues': 'motivo_del_atraso', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-19T16:30', 'espera_el_motivo': True}}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}, {'jugada': 'anotar_prevision', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta_para_despues': 'cual_tarea'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real {'tipo': 'cual_tarea', 'tarea': None}
- **falla** [comprension] preguntas para después: esperado [{'tipo': 'motivo_del_atraso', 'tarea': 'COM'}], real [{'tipo': 'cual_tarea', 'tarea': None}]
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿A cuál de las dos te referís? Podés tocar una opción o escribirla.'

**Paso 3.** Marcos (2026-10-19 10:44): «no el 23 es comunicaciones el plc esta trabado nomas»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-23"}, {"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-23", "motivo": null, "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T16:30:00-03:00", "espera_el_motivo": true}, "pregunta": "motivo_del_atraso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones", "pregunta_para_despues": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "motivo_del_atraso", "tarea": "COM", "desde_antes": false}`
- latencia: 13992 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que estimás terminarla el vie 23/10.  
  > ⚠️ Vence el jue 22/10; si la terminás el viernes, sería un día hábil después. Se avisará a quien aprueba tu trabajo.  
  > Te voy a preguntar cómo viene el vie 23/10.
  >
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que está trabada porque te falta el cable para programar comunicaciones.  
  > Mientras siga trabada, no te voy a pedir cómo viene; retomaré cuando me cuentes que se destrabó.
  >
  > ¿Qué te lleva a estimar el vie 23/10 para comunicaciones?
- [ ] dice: en el bloque de la de comunicaciones, con 📋 primero y ✏️ debajo: que la termina el vie 23/10
- [ ] dice: que la fecha nueva queda informada hoy, en pasiva y en futuro, sin nombrar a Ismael
- [ ] dice: una sola pregunta, sola y en el último renglón: qué atrasa la de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Ismael ya se enteró de algo
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}, {'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real {'escrito': [{'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones', 'resuelto': False}], 'de_mas': [{'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones', 'resuelto': False}]}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-19T16:30', 'espera_el_motivo': True}, 'pregunta': 'motivo_del_atraso'}], real [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'motivo': None, 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T16:30:00-03:00', 'espera_el_motivo': True}, 'pregunta': 'motivo_del_atraso', 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-23'}}}, {'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones', 'pregunta_para_despues': 'quien_destraba', 'lo_que_sigue': {'seguimiento': 'detenido_mientras_siga_trabada'}}]

**Paso 4.** nadie (2026-10-19 10:50)
- (Leda no manda nada)

**Paso 5.** nadie (2026-10-19 10:55)
- (Leda no manda nada)

**Paso 6.** Marcos (2026-10-19 11:00): «el cable lo consigue martin de compras y comunicaciones al final es el lunes 26 xq me falta el switch tmb»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de compras"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-26", "motivo": "me falta el switch tmb"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "martin de compras", "tarea": "PLC", "pregunta": "quien_es_esa_persona"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-26", "motivo": "me falta el switch tmb", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T11:10:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-26"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Revisar comunicaciones industriales de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "hay_una_prevision_mas_nueva"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "martin de compras", "desde_antes": false}`
- latencia: 11932 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que estimás terminarla el lun 26/10 porque también te falta el switch.  
  > ⚠️ Vence el jue 22/10; si la terminás el lunes, serían dos días hábiles después.  
  > Te voy a preguntar cómo viene el lun 26/10.
  >
  > 📋 Programar PLC de la comprimidora  
  > Para anotar quién puede conseguir el cable, necesito saber a quién te referís con «martin de compras».
  >
  > ¿Quién es «martin de compras»?
- [ ] dice: en el bloque de la de comunicaciones, con 📋 primero y ✏️ debajo: que la termina el lun 26/10 porque le falta el switch
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, dos días hábiles de atraso
- [ ] dice: que la fecha nueva queda informada, en pasiva y en futuro, sin nombrar a Ismael
- [ ] dice: que no tiene a nadie en el equipo como "Martín de compras"
- [ ] dice: una sola pregunta, sola y en el último renglón: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: el switch como causa del bloqueo del PLC
- [ ] no dice: Martín en la tarea de comunicaciones
- [ ] no dice: que quedó anotado quién destraba la del PLC
- [ ] no dice: a alguien del equipo como si fuera Martín de compras
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién destraba la del PLC
- [ ] no dice: otra vez la pregunta de qué atrasa la de comunicaciones

**Paso 6b.** Marcos (2026-10-19 11:02): «no no es del equipo es de compras»
- jugadas: `[{"nombre": "decir_quien_es", "de_afuera": true}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 6452 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que Martín, de Compras, puede conseguir el cable.
  >
  > Mientras siga trabada, no te voy a pedir cómo viene. Avisame cuando se destrabe.
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que Martín de compras consigue el cable
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: a alguien del equipo como si fuera Martín de compras
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién es o la de quién destraba

**Paso 7.** Leda (2026-10-19 11:11)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el lun 26/10 porque le falta el switch.  
  > ⚠️ Vence el jue 22/10. Si la termina cuando dijo, tendrá 2 días hábiles de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "me falta el switch tmb", "prevision": "2026-10-26", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el lun 26/10 porque le falta el switch
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: dos días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: el cable o Martín
- [ ] no dice: que la fecha cambió

**Paso 8.** Marcos (2026-10-20 15:00): «ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "entregar", "tarea": "COM", "ejemplo": "Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora."}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el cable para programar comunicaciones"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-22"}}}, {"jugada": "entregar", "resultado": "le_falta_evidencia", "tarea": "COM", "entrega": [{"pieza": "P1", "es": "lo_que_escribio", "dice": "ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final", "cubre": []}], "le_falta_del_criterio": ["Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora"], "ejemplo": "Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora.", "sumo": ["P1"], "pregunta": "lo_que_falta_de_la_entrega"}]`
- pregunta: `{"tipo": "lo_que_falta_de_la_entrega", "tarea": "COM", "lo_mostrado": [{"es": "lo_que_escribio", "dice": "ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final", "cubre": [], "pieza": "P1"}], "le_falta_del_criterio": ["Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora"], "ejemplo": "Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora.", "desde_antes": false}`
- latencia: 15391 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que llegó el cable y que la tarea ya no está trabada por eso.  
  > Te voy a preguntar cómo viene pasado mañana.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Sumé lo que contaste a la entrega.  
  > ⚠️ Para darla por entregada, falta saber si los equipos se comunicaron con el PLC por la red de planta sin errores durante una hora.  
  > Te propongo esta descripción: «Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora».
  >
  > ¿Confirmás esa descripción o preferís escribir la tuya?
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que quedó anotado que se destrabó y sigue en curso
- [ ] dice: en el bloque de la de comunicaciones: qué falta para revisarla, con un ejemplo sacado del criterio para que lo acepte o lo escriba con sus palabras
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: que la tarea de comunicaciones quedó entregada, en revisión o terminada
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: que la del PLC está terminada
- [ ] no dice: otra vez la pregunta de quién lo destraba
- [ ] no dice: "contaste" o "contarlo": lo que escribió es su descripción (decisión 10; D7)

## 25 · Mensajes sin puntuación · vez 2

Fuente: `tests/conversaciones/25-sin-puntuacion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G FALLA · C FALLA · M ok · F FALLA.

**Paso 1.** Leda (2026-10-19 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-19) → Marcos:
  > Se acercan los vencimientos de estas tareas:
  >
  > 🗓️ Programar PLC de la comprimidora — vence jue 22/10  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence jue 22/10
  >
  > No hace falta responder.
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- [ ] dice: las dos tareas de Marcos, cada una en su renglón con 🗓️ y su fecha corta, el jue 22/10
- [ ] dice: que no hace falta contestar, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-19 10:40): «con el PLC estoy compliacdo, me falta el cable para programar comunicaciones estimo que la tengo para el viernes 23»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones"}, {"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones", "pregunta": "quien_destraba"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:50:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 15749 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que te falta el cable para programar comunicaciones y que estimás terminarla el vie 23/10.  
  > ⚠️ Vence el jue 22/10: si la terminás el viernes, sería un día hábil después.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Depende de que termines la programación del PLC.
  >
  > Mientras siga trabada, no te voy a pedir avances. Retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede conseguir el cable para destrabarla?
- [ ] dice: cada tarea en su bloque, primero su renglón con 📋 y su nombre solo y debajo, con ✏️, lo anotado: la del PLC está trabada porque le falta el cable para programar; la de comunicaciones la termina el vie 23/10
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, un día hábil de atraso
- [ ] dice: que la fecha nueva queda informada, en pasiva y en futuro, sin nombrar a Ismael
- [ ] dice: una sola pregunta, sola y en el último renglón: quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una causa del bloqueo que nombre las comunicaciones
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: dos preguntas juntas
- [ ] no dice: negrita
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones'}, {'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real {'escrito': [{'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}], 'de_mas': [{'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}]}
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente', 'sin_motivo_todavia': True}}], real {'escrito': [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:b1262667-2789-42a9-9cd4-347d8f97a1f2', 'outbox_id': None}], 'de_mas': [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:b1262667-2789-42a9-9cd4-347d8f97a1f2', 'outbox_id': None}]}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente', 'pregunta_para_despues': 'motivo_del_atraso', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-19T16:30', 'espera_el_motivo': True}}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:50:00-03:00'}, 'lo_que_sigue': {'seguimiento': 'detenido_mientras_siga_trabada'}}]
- **falla** [comprension] preguntas para después: esperado [{'tipo': 'motivo_del_atraso', 'tarea': 'COM'}], real []

**Paso 3.** Marcos (2026-10-19 10:44): «no el 23 es comunicaciones el plc esta trabado nomas»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_prevision", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "PLC", "vuelve_a": {"fecha_comprometida": "2026-10-22"}, "prevision_corregida": "2026-10-23", "aviso_de_la_prevision_corregida": {"a": "Ismael Soschinski", "llega": "no_le_va_a_llegar"}, "aplicado": {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-23", "motivo": null, "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T16:30:00-03:00", "espera_el_motivo": true}, "pregunta": "motivo_del_atraso"}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Programar PLC de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "prevision_corregida"}]`
- pregunta: `{"tipo": "motivo_del_atraso", "tarea": "COM", "desde_antes": false}`
- latencia: 11598 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Corregí lo del vie 23/10: esa fecha no era para el PLC. Sigue trabado y vence el jue 22/10.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que estimás terminarla el vie 23/10.  
  > ⚠️ Vence el jue 22/10; si la terminás el viernes, sería un día hábil después.
  >
  > ¿Qué te atrasa la revisión de comunicaciones hasta el vie 23/10?
- [ ] dice: en el bloque de la de comunicaciones, con 📋 primero y ✏️ debajo: que la termina el vie 23/10
- [ ] dice: que la fecha nueva queda informada hoy, en pasiva y en futuro, sin nombrar a Ismael
- [ ] dice: una sola pregunta, sola y en el último renglón: qué atrasa la de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Ismael ya se enteró de algo
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'corregir', 'corrige': 'anotar_prevision', 'tarea': 'PLC', 'tarea_correcta': 'COM'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real {'escrito': [{'tarea': 'PLC', 'fecha': '2026-10-22', 'motivo': None, 'es_correccion': True}, {'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': None, 'es_correccion': False}], 'de_mas': [{'tarea': 'PLC', 'fecha': '2026-10-22', 'motivo': None, 'es_correccion': True}]}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-19T16:30', 'espera_el_motivo': True}, 'pregunta': 'motivo_del_atraso'}], real [{'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'PLC', 'vuelve_a': {'fecha_comprometida': '2026-10-22'}, 'prevision_corregida': '2026-10-23', 'aviso_de_la_prevision_corregida': {'a': 'Ismael Soschinski', 'llega': 'no_le_va_a_llegar'}, 'aplicado': {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'motivo': None, 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T16:30:00-03:00', 'espera_el_motivo': True}, 'pregunta': 'motivo_del_atraso'}}]

**Paso 4.** nadie (2026-10-19 10:50)
- (Leda no manda nada)

**Paso 5.** nadie (2026-10-19 10:55)
- (Leda no manda nada)

**Paso 6.** Marcos (2026-10-19 11:00): «el cable lo consigue martin de compras y comunicaciones al final es el lunes 26 xq me falta el switch tmb»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de compras"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-26", "motivo": "me falta el switch tmb"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "martin de compras", "tarea": "PLC", "pregunta": "quien_es_esa_persona"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-26", "motivo": "me falta el switch tmb", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T11:10:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-26"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Programar PLC de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "hay_una_prevision_mas_nueva"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "martin de compras", "desde_antes": false}`
- latencia: 11443 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que ahora estimás terminarla el lun 26/10 porque también te falta el switch.  
  > ⚠️ Vence el jue 22/10; si la terminás ese lunes, serían dos días hábiles de atraso.  
  > El lun 26/10 te voy a preguntar cómo viene.
  >
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Para anotar quién puede conseguir el cable, necesito identificar a la persona que mencionaste.
  >
  > ¿Quién es «martin de compras»?
- [ ] dice: en el bloque de la de comunicaciones, con 📋 primero y ✏️ debajo: que la termina el lun 26/10 porque le falta el switch
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, dos días hábiles de atraso
- [ ] dice: que la fecha nueva queda informada, en pasiva y en futuro, sin nombrar a Ismael
- [ ] dice: que no tiene a nadie en el equipo como "Martín de compras"
- [ ] dice: una sola pregunta, sola y en el último renglón: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: el switch como causa del bloqueo del PLC
- [ ] no dice: Martín en la tarea de comunicaciones
- [ ] no dice: que quedó anotado quién destraba la del PLC
- [ ] no dice: a alguien del equipo como si fuera Martín de compras
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién destraba la del PLC
- [ ] no dice: otra vez la pregunta de qué atrasa la de comunicaciones

**Paso 6b.** Marcos (2026-10-19 11:02): «no no es del equipo es de compras»
- jugadas: `[{"nombre": "decir_quien_es", "de_afuera": true}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 3925 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que Martín, de Compras y de afuera del equipo, puede conseguir el cable.  
  > Mientras siga trabado, no te voy a pedir avances.
  >
  > Avisame cuando se destrabe y retomo el seguimiento.
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que Martín de compras consigue el cable
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: a alguien del equipo como si fuera Martín de compras
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién es o la de quién destraba

**Paso 7.** Leda (2026-10-19 11:11)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el lun 26/10 porque le falta el switch.  
  > ⚠️ Vence el jue 22/10. Si la termina el día que dijo, tendrá 2 días hábiles de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "me falta el switch tmb", "prevision": "2026-10-26", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el lun 26/10 porque le falta el switch
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: dos días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: el cable o Martín
- [ ] no dice: que la fecha cambió

**Paso 8.** Marcos (2026-10-20 15:00): «ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "informar_avance", "tarea": "PLC", "palabras": "sigo con el plc"}, {"nombre": "entregar", "tarea": "COM", "el_texto_cubre": [], "lo_descrito_cubre": [], "ejemplo": "Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora."}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el cable para programar comunicaciones"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-22"}}}, {"jugada": "informar_avance", "resultado": "no_se_puede", "motivo": "nadie_pidio_el_estado", "tarea": "PLC"}, {"jugada": "entregar", "resultado": "le_falta_evidencia", "tarea": "COM", "entrega": [{"pieza": "P1", "es": "lo_que_escribio", "dice": "ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final", "cubre": []}], "le_falta_del_criterio": ["Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora"], "ejemplo": "Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora.", "sumo": ["P1"], "pregunta": "lo_que_falta_de_la_entrega"}]`
- pregunta: `{"tipo": "lo_que_falta_de_la_entrega", "tarea": "COM", "lo_mostrado": [{"es": "lo_que_escribio", "dice": "ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final", "cubre": [], "pieza": "P1"}], "le_falta_del_criterio": ["Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora"], "ejemplo": "Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora.", "desde_antes": false}`
- latencia: 10823 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que llegó el cable y que la tarea ya no está trabada por eso.  
  > No anoté «sigo con el PLC» como avance porque todavía no te había preguntado cómo venía. Pasado mañana te voy a preguntar.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Sumé lo que contaste sobre comunicaciones, pero para darla por terminada falta confirmar que los equipos se comunican con el PLC por la red de planta sin errores durante una hora.  
  > Podés usar esta descripción o escribir la tuya: «Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora».
  >
  > ¿Confirmás esa descripción o preferís escribir otra?
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que quedó anotado que se destrabó y sigue en curso
- [ ] dice: en el bloque de la de comunicaciones: qué falta para revisarla, con un ejemplo sacado del criterio para que lo acepte o lo escriba con sus palabras
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: que la tarea de comunicaciones quedó entregada, en revisión o terminada
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: que la del PLC está terminada
- [ ] no dice: otra vez la pregunta de quién lo destraba
- [ ] no dice: "contaste" o "contarlo": lo que escribió es su descripción (decisión 10; D7)
- **falla** [comprension] jugadas: esperado [{'nombre': 'destrabar', 'tarea': 'PLC'}, {'nombre': 'entregar', 'tarea': 'COM', 'lo_descrito_cubre': [], 'puede_traer': ['lo_descrito_cubre', 'ejemplo']}], real [{'nombre': 'destrabar', 'tarea': 'PLC'}, {'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'sigo con el plc'}, {'nombre': 'entregar', 'tarea': 'COM', 'el_texto_cubre': [], 'lo_descrito_cubre': [], 'ejemplo': 'Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora.'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'estado': 'en_curso', 'vuelve_a_pedir_el_estado': 'ausente', 'pregunta': 'ausente'}, {'jugada': 'entregar', 'resultado': 'le_falta_evidencia', 'tarea': 'COM', 'pregunta': 'lo_que_falta_de_la_entrega', 'le_falta_del_criterio': ['Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora'], 'ejemplo': 'presente', 'al_confirmar': 'ausente'}], real [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'bloqueo_resuelto': {'causa': 'me falta el cable para programar comunicaciones'}, 'estado': 'en_curso', 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-22'}}}, {'jugada': 'informar_avance', 'resultado': 'no_se_puede', 'motivo': 'nadie_pidio_el_estado', 'tarea': 'PLC'}, {'jugada': 'entregar', 'resultado': 'le_falta_evidencia', 'tarea': 'COM', 'entrega': [{'pieza': 'P1', 'es': 'lo_que_escribio', 'dice': 'ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final', 'cubre': []}], 'le_falta_del_criterio': ['Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora'], 'ejemplo': 'Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora.', 'sumo': ['P1'], 'pregunta': 'lo_que_falta_de_la_entrega'}]
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '✏️ Sumé lo que contaste sobre comunicaciones, pero para darla por terminada falta confirmar que los equipos se comunican con el PLC por la red de planta sin errores durante una hora.'

## 25 · Mensajes sin puntuación · vez 3

Fuente: `tests/conversaciones/25-sin-puntuacion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G FALLA · C FALLA · M ok · F FALLA.

**Paso 1.** Leda (2026-10-19 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-19) → Marcos:
  > Se acercan estos vencimientos:
  >
  > 🗓️ Programar PLC de la comprimidora — jue 22/10  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — jue 22/10
  >
  > No hace falta responder.
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- [ ] dice: las dos tareas de Marcos, cada una en su renglón con 🗓️ y su fecha corta, el jue 22/10
- [ ] dice: que no hace falta contestar, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-19 10:40): «con el PLC estoy compliacdo, me falta el cable para programar comunicaciones estimo que la tengo para el viernes 23»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones"}, {"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones", "pregunta": "quien_destraba"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:50:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 12720 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Te falta el cable para programar comunicaciones.  
  > ✏️ Anoté que estimás terminarla el vie 23/10. Vence el jue 22/10: si la terminás el viernes, sería un día hábil de atraso.  
  > La revisión de comunicaciones industriales depende de esta tarea.  
  > Mientras siga trabada, no te voy a pedir avances; volveré a consultarte cuando me cuentes que se destrabó.
  >
  > ¿Quién puede conseguir el cable para destrabarla?
- [ ] dice: cada tarea en su bloque, primero su renglón con 📋 y su nombre solo y debajo, con ✏️, lo anotado: la del PLC está trabada porque le falta el cable para programar; la de comunicaciones la termina el vie 23/10
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, un día hábil de atraso
- [ ] dice: que la fecha nueva queda informada, en pasiva y en futuro, sin nombrar a Ismael
- [ ] dice: una sola pregunta, sola y en el último renglón: quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una causa del bloqueo que nombre las comunicaciones
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: dos preguntas juntas
- [ ] no dice: negrita
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones'}, {'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real {'escrito': [{'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}], 'de_mas': [{'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}]}
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente', 'sin_motivo_todavia': True}}], real {'escrito': [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:415a3105-af36-4c97-a9cb-29ab755cf5c2', 'outbox_id': None}], 'de_mas': [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:415a3105-af36-4c97-a9cb-29ab755cf5c2', 'outbox_id': None}]}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente', 'pregunta_para_despues': 'motivo_del_atraso', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-19T16:30', 'espera_el_motivo': True}}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:50:00-03:00'}, 'lo_que_sigue': {'seguimiento': 'detenido_mientras_siga_trabada'}}]
- **falla** [comprension] preguntas para después: esperado [{'tipo': 'motivo_del_atraso', 'tarea': 'COM'}], real []

**Paso 3.** Marcos (2026-10-19 10:44): «no el 23 es comunicaciones el plc esta trabado nomas»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_prevision", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "PLC", "vuelve_a": {"fecha_comprometida": "2026-10-22"}, "prevision_corregida": "2026-10-23", "aviso_de_la_prevision_corregida": {"a": "Ismael Soschinski", "llega": "no_le_va_a_llegar"}, "aplicado": {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-23", "motivo": null, "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T16:30:00-03:00", "espera_el_motivo": true}, "pregunta": "motivo_del_atraso"}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Programar PLC de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "prevision_corregida"}]`
- pregunta: `{"tipo": "motivo_del_atraso", "tarea": "COM", "desde_antes": false}`
- latencia: 14721 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Corregí lo anotado: el vie 23/10 no era para esta tarea. Sigue trabada por el cable y vence el jue 22/10.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que estimás terminarla el vie 23/10. Vence el jue 22/10: si la terminás ese día, sería un día hábil de atraso.  
  > Se avisará que estimás terminarla ese día.
  >
  > ¿Qué te demora la revisión de comunicaciones hasta el vie 23/10?
- [ ] dice: en el bloque de la de comunicaciones, con 📋 primero y ✏️ debajo: que la termina el vie 23/10
- [ ] dice: que la fecha nueva queda informada hoy, en pasiva y en futuro, sin nombrar a Ismael
- [ ] dice: una sola pregunta, sola y en el último renglón: qué atrasa la de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Ismael ya se enteró de algo
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'corregir', 'corrige': 'anotar_prevision', 'tarea': 'PLC', 'tarea_correcta': 'COM'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real {'escrito': [{'tarea': 'PLC', 'fecha': '2026-10-22', 'motivo': None, 'es_correccion': True}, {'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': None, 'es_correccion': False}], 'de_mas': [{'tarea': 'PLC', 'fecha': '2026-10-22', 'motivo': None, 'es_correccion': True}]}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-19T16:30', 'espera_el_motivo': True}, 'pregunta': 'motivo_del_atraso'}], real [{'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'PLC', 'vuelve_a': {'fecha_comprometida': '2026-10-22'}, 'prevision_corregida': '2026-10-23', 'aviso_de_la_prevision_corregida': {'a': 'Ismael Soschinski', 'llega': 'no_le_va_a_llegar'}, 'aplicado': {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'motivo': None, 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T16:30:00-03:00', 'espera_el_motivo': True}, 'pregunta': 'motivo_del_atraso'}}]

**Paso 4.** nadie (2026-10-19 10:50)
- (Leda no manda nada)

**Paso 5.** nadie (2026-10-19 10:55)
- (Leda no manda nada)

**Paso 6.** Marcos (2026-10-19 11:00): «el cable lo consigue martin de compras y comunicaciones al final es el lunes 26 xq me falta el switch tmb»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de compras"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-26", "motivo": "me falta el switch tmb"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "martin de compras", "tarea": "PLC", "pregunta": "quien_es_esa_persona"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-26", "motivo": "me falta el switch tmb", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T11:10:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-26"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Programar PLC de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "hay_una_prevision_mas_nueva"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "martin de compras", "desde_antes": false}`
- latencia: 11049 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que estimás terminarla el lun 26/10 porque te falta el switch. Vence el jue 22/10; si la terminás ese lunes, serían dos días hábiles de atraso.  
  > Te voy a preguntar cómo viene el lun 26/10.
  >
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Sigue trabada por el cable. Necesito identificar a «martin de compras» para dejar anotado quién puede conseguirlo.
  >
  > ¿Quién es «martin de compras»?
- [ ] dice: en el bloque de la de comunicaciones, con 📋 primero y ✏️ debajo: que la termina el lun 26/10 porque le falta el switch
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, dos días hábiles de atraso
- [ ] dice: que la fecha nueva queda informada, en pasiva y en futuro, sin nombrar a Ismael
- [ ] dice: que no tiene a nadie en el equipo como "Martín de compras"
- [ ] dice: una sola pregunta, sola y en el último renglón: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: el switch como causa del bloqueo del PLC
- [ ] no dice: Martín en la tarea de comunicaciones
- [ ] no dice: que quedó anotado quién destraba la del PLC
- [ ] no dice: a alguien del equipo como si fuera Martín de compras
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién destraba la del PLC
- [ ] no dice: otra vez la pregunta de qué atrasa la de comunicaciones
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '✏️ Anoté que estimás terminarla el lun 26/10 porque te falta el switch. Vence el jue 22/10; si la terminás ese lunes, serían dos días hábiles de atraso.'

**Paso 6b.** Marcos (2026-10-19 11:02): «no no es del equipo es de compras»
- jugadas: `[{"nombre": "decir_quien_es", "de_afuera": true}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 6102 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que Martín, de Compras, puede conseguir el cable. La tarea sigue trabada y, mientras sea así, no te voy a pedir avances.
  >
  > Cuando se destrabe, contame y retomo el seguimiento.
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que Martín de compras consigue el cable
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: a alguien del equipo como si fuera Martín de compras
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién es o la de quién destraba

**Paso 7.** Leda (2026-10-19 11:11)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminaría el lun 26/10 porque todavía le falta el switch.  
  > ⚠️ Vence el jue 22/10; si la termina ese día, serían 2 días hábiles de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "me falta el switch tmb", "prevision": "2026-10-26", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el lun 26/10 porque le falta el switch
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: dos días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: el cable o Martín
- [ ] no dice: que la fecha cambió

**Paso 8.** Marcos (2026-10-20 15:00): «ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "entregar", "tarea": "COM", "ejemplo": "Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora."}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el cable para programar comunicaciones"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-22"}}}, {"jugada": "entregar", "resultado": "le_falta_evidencia", "tarea": "COM", "entrega": [{"pieza": "P1", "es": "lo_que_escribio", "dice": "ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final", "cubre": []}], "le_falta_del_criterio": ["Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora"], "ejemplo": "Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora.", "sumo": ["P1"], "pregunta": "lo_que_falta_de_la_entrega"}]`
- pregunta: `{"tipo": "lo_que_falta_de_la_entrega", "tarea": "COM", "lo_mostrado": [{"es": "lo_que_escribio", "dice": "ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final", "cubre": [], "pieza": "P1"}], "le_falta_del_criterio": ["Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora"], "ejemplo": "Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora.", "desde_antes": false}`
- latencia: 9187 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que llegó el cable y que seguís con el PLC. Ya no está trabada por eso.  
  > Te voy a preguntar cómo viene pasado mañana.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que decís que terminaste la revisión.  
  > ⚠️ Para darla por entregada, falta saber si los equipos se comunicaron con el PLC por la red de planta sin errores durante una hora.  
  > Como descripción, podrías usar: «Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora».
  >
  > ¿Confirmás esa descripción o preferís escribir la tuya?
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que quedó anotado que se destrabó y sigue en curso
- [ ] dice: en el bloque de la de comunicaciones: qué falta para revisarla, con un ejemplo sacado del criterio para que lo acepte o lo escriba con sus palabras
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: que la tarea de comunicaciones quedó entregada, en revisión o terminada
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: que la del PLC está terminada
- [ ] no dice: otra vez la pregunta de quién lo destraba
- [ ] no dice: "contaste" o "contarlo": lo que escribió es su descripción (decisión 10; D7)

## 25 · Mensajes sin puntuación · vez 4

Fuente: `tests/conversaciones/25-sin-puntuacion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G FALLA · C FALLA · M ok · F ok.

**Paso 1.** Leda (2026-10-19 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-19) → Marcos:
  > Se acercan estos vencimientos:
  >
  > 🗓️ Programar PLC de la comprimidora — jue 22/10  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — jue 22/10
  >
  > No hace falta responder.
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- [ ] dice: las dos tareas de Marcos, cada una en su renglón con 🗓️ y su fecha corta, el jue 22/10
- [ ] dice: que no hace falta contestar, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-19 10:40): «con el PLC estoy compliacdo, me falta el cable para programar comunicaciones estimo que la tengo para el viernes 23»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones"}, {"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones", "pregunta": "quien_destraba"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:50:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 11635 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que te falta el cable para programar comunicaciones y que estimás terminarla el vie 23/10.  
  > Vence el jue 22/10: si la terminás el viernes, sería un día hábil después.  
  > ⚠️ La revisión de comunicaciones industriales depende de esta tarea.
  >
  > Mientras siga trabada, no te voy a pedir avances; retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede conseguir el cable para destrabarla?
- [ ] dice: cada tarea en su bloque, primero su renglón con 📋 y su nombre solo y debajo, con ✏️, lo anotado: la del PLC está trabada porque le falta el cable para programar; la de comunicaciones la termina el vie 23/10
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, un día hábil de atraso
- [ ] dice: que la fecha nueva queda informada, en pasiva y en futuro, sin nombrar a Ismael
- [ ] dice: una sola pregunta, sola y en el último renglón: quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una causa del bloqueo que nombre las comunicaciones
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: dos preguntas juntas
- [ ] no dice: negrita
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones'}, {'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real {'escrito': [{'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}], 'de_mas': [{'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}]}
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente', 'sin_motivo_todavia': True}}], real {'escrito': [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:d2a16279-7ca0-47a7-ab17-d0672319cd0f', 'outbox_id': None}], 'de_mas': [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:d2a16279-7ca0-47a7-ab17-d0672319cd0f', 'outbox_id': None}]}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente', 'pregunta_para_despues': 'motivo_del_atraso', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-19T16:30', 'espera_el_motivo': True}}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:50:00-03:00'}, 'lo_que_sigue': {'seguimiento': 'detenido_mientras_siga_trabada'}}]
- **falla** [comprension] preguntas para después: esperado [{'tipo': 'motivo_del_atraso', 'tarea': 'COM'}], real []

**Paso 3.** Marcos (2026-10-19 10:44): «no el 23 es comunicaciones el plc esta trabado nomas»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_prevision", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "PLC", "vuelve_a": {"fecha_comprometida": "2026-10-22"}, "prevision_corregida": "2026-10-23", "aviso_de_la_prevision_corregida": {"a": "Ismael Soschinski", "llega": "no_le_va_a_llegar"}, "aplicado": {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-23", "motivo": null, "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T16:30:00-03:00", "espera_el_motivo": true}, "pregunta": "motivo_del_atraso"}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Programar PLC de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "prevision_corregida"}]`
- pregunta: `{"tipo": "motivo_del_atraso", "tarea": "COM", "desde_antes": false}`
- latencia: 11373 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Corregí lo del vie 23/10: esa fecha no era para el PLC. Sigue trabado porque te falta el cable.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que estimás terminarla el vie 23/10. Vence el jue 22/10; si la terminás el viernes, sería un día hábil después.
  >
  > ¿Qué atrasa la revisión de comunicaciones hasta el vie 23/10?
- [ ] dice: en el bloque de la de comunicaciones, con 📋 primero y ✏️ debajo: que la termina el vie 23/10
- [ ] dice: que la fecha nueva queda informada hoy, en pasiva y en futuro, sin nombrar a Ismael
- [ ] dice: una sola pregunta, sola y en el último renglón: qué atrasa la de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Ismael ya se enteró de algo
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'corregir', 'corrige': 'anotar_prevision', 'tarea': 'PLC', 'tarea_correcta': 'COM'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real {'escrito': [{'tarea': 'PLC', 'fecha': '2026-10-22', 'motivo': None, 'es_correccion': True}, {'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': None, 'es_correccion': False}], 'de_mas': [{'tarea': 'PLC', 'fecha': '2026-10-22', 'motivo': None, 'es_correccion': True}]}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-19T16:30', 'espera_el_motivo': True}, 'pregunta': 'motivo_del_atraso'}], real [{'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'PLC', 'vuelve_a': {'fecha_comprometida': '2026-10-22'}, 'prevision_corregida': '2026-10-23', 'aviso_de_la_prevision_corregida': {'a': 'Ismael Soschinski', 'llega': 'no_le_va_a_llegar'}, 'aplicado': {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'motivo': None, 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T16:30:00-03:00', 'espera_el_motivo': True}, 'pregunta': 'motivo_del_atraso'}}]

**Paso 4.** nadie (2026-10-19 10:50)
- (Leda no manda nada)

**Paso 5.** nadie (2026-10-19 10:55)
- (Leda no manda nada)

**Paso 6.** Marcos (2026-10-19 11:00): «el cable lo consigue martin de compras y comunicaciones al final es el lunes 26 xq me falta el switch tmb»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de compras"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-26", "motivo": "me falta el switch tmb"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "martin de compras", "tarea": "PLC", "pregunta": "quien_es_esa_persona"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-26", "motivo": "me falta el switch tmb", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T11:10:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-26"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Programar PLC de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "hay_una_prevision_mas_nueva"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "martin de compras", "desde_antes": false}`
- latencia: 9816 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que estimás terminarla el lun 26/10 porque también te falta el switch.  
  > Vence el jue 22/10; si la terminás el lunes, serían dos días hábiles después.  
  > Ese lunes te voy a preguntar cómo viene.
  >
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Sigue trabado por el cable. Para anotar quién puede conseguirlo, necesito identificar a «martin de compras».
  >
  > ¿Quién es «martin de compras»?
- [ ] dice: en el bloque de la de comunicaciones, con 📋 primero y ✏️ debajo: que la termina el lun 26/10 porque le falta el switch
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, dos días hábiles de atraso
- [ ] dice: que la fecha nueva queda informada, en pasiva y en futuro, sin nombrar a Ismael
- [ ] dice: que no tiene a nadie en el equipo como "Martín de compras"
- [ ] dice: una sola pregunta, sola y en el último renglón: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: el switch como causa del bloqueo del PLC
- [ ] no dice: Martín en la tarea de comunicaciones
- [ ] no dice: que quedó anotado quién destraba la del PLC
- [ ] no dice: a alguien del equipo como si fuera Martín de compras
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién destraba la del PLC
- [ ] no dice: otra vez la pregunta de qué atrasa la de comunicaciones

**Paso 6b.** Marcos (2026-10-19 11:02): «no no es del equipo es de compras»
- jugadas: `[{"nombre": "decir_quien_es", "de_afuera": true}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 6209 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que Martín, de Compras, puede conseguir el cable.
  >
  > Avisame cuando se destrabe y retomaré el seguimiento.
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que Martín de compras consigue el cable
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: a alguien del equipo como si fuera Martín de compras
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién es o la de quién destraba

**Paso 7.** Leda (2026-10-19 11:11)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que va a terminarla el lun 26/10 porque todavía le falta el switch.  
  > ⚠️ Vence el jue 22/10. Si la termina el lun 26/10, tendrá 2 días hábiles de atraso.
  >
  > No hace falta que respondas.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "me falta el switch tmb", "prevision": "2026-10-26", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el lun 26/10 porque le falta el switch
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: dos días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: el cable o Martín
- [ ] no dice: que la fecha cambió

**Paso 8.** Marcos (2026-10-20 15:00): «ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "entregar", "tarea": "COM", "ejemplo": "Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora."}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el cable para programar comunicaciones"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-22"}}}, {"jugada": "entregar", "resultado": "le_falta_evidencia", "tarea": "COM", "entrega": [{"pieza": "P1", "es": "lo_que_escribio", "dice": "ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final", "cubre": []}], "le_falta_del_criterio": ["Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora"], "ejemplo": "Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora.", "sumo": ["P1"], "pregunta": "lo_que_falta_de_la_entrega"}]`
- pregunta: `{"tipo": "lo_que_falta_de_la_entrega", "tarea": "COM", "lo_mostrado": [{"es": "lo_que_escribio", "dice": "ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final", "cubre": [], "pieza": "P1"}], "le_falta_del_criterio": ["Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora"], "ejemplo": "Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora.", "desde_antes": false}`
- latencia: 9403 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que llegó el cable y que la tarea ya no está trabada por eso.  
  > Pasado mañana te voy a preguntar cómo viene.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Sumé a la entrega lo que contaste: que terminaste comunicaciones.  
  > ⚠️ Falta saber si los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora.  
  > Podés usar esta descripción: «Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora».
  >
  > ¿Confirmás esa descripción o preferís escribir la tuya?
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que quedó anotado que se destrabó y sigue en curso
- [ ] dice: en el bloque de la de comunicaciones: qué falta para revisarla, con un ejemplo sacado del criterio para que lo acepte o lo escriba con sus palabras
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: que la tarea de comunicaciones quedó entregada, en revisión o terminada
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: que la del PLC está terminada
- [ ] no dice: otra vez la pregunta de quién lo destraba
- [ ] no dice: "contaste" o "contarlo": lo que escribió es su descripción (decisión 10; D7)

## 25 · Mensajes sin puntuación · vez 5

Fuente: `tests/conversaciones/25-sin-puntuacion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G FALLA · C FALLA · M ok · F FALLA.

**Paso 1.** Leda (2026-10-19 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-19) → Marcos:
  > Se acercan estos vencimientos:
  >
  > 🗓️ Programar PLC de la comprimidora — jue 22/10  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — jue 22/10
  >
  > No hace falta que respondas.
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- [ ] dice: las dos tareas de Marcos, cada una en su renglón con 🗓️ y su fecha corta, el jue 22/10
- [ ] dice: que no hace falta contestar, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-19 10:40): «con el PLC estoy compliacdo, me falta el cable para programar comunicaciones estimo que la tengo para el viernes 23»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones"}, {"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones", "pregunta": "quien_destraba"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:50:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 14288 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que te falta el cable para programar comunicaciones y que estimás terminarla el vie 23/10.  
  > ⚠️ Vence el jue 22/10: si la terminás el viernes, será un día hábil de atraso.  
  > ⚠️ La revisión de comunicaciones industriales depende de esta tarea.
  >
  > Mientras siga trabada, no te voy a pedir avances. Retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede conseguir el cable para destrabarla?
- [ ] dice: cada tarea en su bloque, primero su renglón con 📋 y su nombre solo y debajo, con ✏️, lo anotado: la del PLC está trabada porque le falta el cable para programar; la de comunicaciones la termina el vie 23/10
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, un día hábil de atraso
- [ ] dice: que la fecha nueva queda informada, en pasiva y en futuro, sin nombrar a Ismael
- [ ] dice: una sola pregunta, sola y en el último renglón: quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una causa del bloqueo que nombre las comunicaciones
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: dos preguntas juntas
- [ ] no dice: negrita
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones'}, {'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real {'escrito': [{'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}], 'de_mas': [{'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}]}
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente', 'sin_motivo_todavia': True}}], real {'escrito': [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:03ea1809-685c-44ad-9aae-6b6c64e1a23c', 'outbox_id': None}], 'de_mas': [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:03ea1809-685c-44ad-9aae-6b6c64e1a23c', 'outbox_id': None}]}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente', 'pregunta_para_despues': 'motivo_del_atraso', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-19T16:30', 'espera_el_motivo': True}}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:50:00-03:00'}, 'lo_que_sigue': {'seguimiento': 'detenido_mientras_siga_trabada'}}]
- **falla** [comprension] preguntas para después: esperado [{'tipo': 'motivo_del_atraso', 'tarea': 'COM'}], real []

**Paso 3.** Marcos (2026-10-19 10:44): «no el 23 es comunicaciones el plc esta trabado nomas»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_prevision", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "PLC", "vuelve_a": {"fecha_comprometida": "2026-10-22"}, "prevision_corregida": "2026-10-23", "aviso_de_la_prevision_corregida": {"a": "Ismael Soschinski", "llega": "no_le_va_a_llegar"}, "aplicado": {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-23", "motivo": null, "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T16:30:00-03:00", "espera_el_motivo": true}, "pregunta": "motivo_del_atraso"}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Programar PLC de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "prevision_corregida"}]`
- pregunta: `{"tipo": "motivo_del_atraso", "tarea": "COM", "desde_antes": false}`
- latencia: 8052 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Corregí lo del vie 23/10: esa fecha no era para el PLC. Sigue trabado por falta del cable y vence el jue 22/10.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que estimás terminarla el vie 23/10.  
  > ⚠️ Vence el jue 22/10: si la terminás el viernes, será un día hábil de atraso.
  >
  > ¿Qué te lleva a estimar el viernes para la revisión de comunicaciones?
- [ ] dice: en el bloque de la de comunicaciones, con 📋 primero y ✏️ debajo: que la termina el vie 23/10
- [ ] dice: que la fecha nueva queda informada hoy, en pasiva y en futuro, sin nombrar a Ismael
- [ ] dice: una sola pregunta, sola y en el último renglón: qué atrasa la de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Ismael ya se enteró de algo
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'corregir', 'corrige': 'anotar_prevision', 'tarea': 'PLC', 'tarea_correcta': 'COM'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real {'escrito': [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': None, 'es_correccion': False}, {'tarea': 'PLC', 'fecha': '2026-10-22', 'motivo': None, 'es_correccion': True}], 'de_mas': [{'tarea': 'PLC', 'fecha': '2026-10-22', 'motivo': None, 'es_correccion': True}]}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-19T16:30', 'espera_el_motivo': True}, 'pregunta': 'motivo_del_atraso'}], real [{'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'PLC', 'vuelve_a': {'fecha_comprometida': '2026-10-22'}, 'prevision_corregida': '2026-10-23', 'aviso_de_la_prevision_corregida': {'a': 'Ismael Soschinski', 'llega': 'no_le_va_a_llegar'}, 'aplicado': {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'motivo': None, 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T16:30:00-03:00', 'espera_el_motivo': True}, 'pregunta': 'motivo_del_atraso'}}]

**Paso 4.** nadie (2026-10-19 10:50)
- (Leda no manda nada)

**Paso 5.** nadie (2026-10-19 10:55)
- (Leda no manda nada)

**Paso 6.** Marcos (2026-10-19 11:00): «el cable lo consigue martin de compras y comunicaciones al final es el lunes 26 xq me falta el switch tmb»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de compras"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-26", "motivo": "me falta el switch tmb"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "martin de compras", "tarea": "PLC", "pregunta": "quien_es_esa_persona"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-26", "motivo": "me falta el switch tmb", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T11:10:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-26"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Programar PLC de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "hay_una_prevision_mas_nueva"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "martin de compras", "desde_antes": false}`
- latencia: 10130 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que ahora estimás terminarla el lun 26/10 porque también te falta el switch.  
  > ⚠️ Vence el jue 22/10: si la terminás el lunes, serán dos días hábiles de atraso. El lunes te voy a preguntar cómo viene.
  >
  > 📋 Programar PLC de la comprimidora  
  > Para anotar quién puede conseguir el cable, necesito saber a quién te referís con «martin de compras».
  >
  > ¿Quién es?
- [ ] dice: en el bloque de la de comunicaciones, con 📋 primero y ✏️ debajo: que la termina el lun 26/10 porque le falta el switch
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, dos días hábiles de atraso
- [ ] dice: que la fecha nueva queda informada, en pasiva y en futuro, sin nombrar a Ismael
- [ ] dice: que no tiene a nadie en el equipo como "Martín de compras"
- [ ] dice: una sola pregunta, sola y en el último renglón: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: el switch como causa del bloqueo del PLC
- [ ] no dice: Martín en la tarea de comunicaciones
- [ ] no dice: que quedó anotado quién destraba la del PLC
- [ ] no dice: a alguien del equipo como si fuera Martín de compras
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién destraba la del PLC
- [ ] no dice: otra vez la pregunta de qué atrasa la de comunicaciones

**Paso 6b.** Marcos (2026-10-19 11:02): «no no es del equipo es de compras»
- jugadas: `[{"nombre": "decir_quien_es", "de_afuera": true}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 5651 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que Martín de compras, que no es del equipo, puede conseguir el cable.  
  > Mientras siga trabada, no te voy a pedir avances.
  >
  > Avisame cuando se destrabe para retomar el seguimiento.
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que Martín de compras consigue el cable
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: a alguien del equipo como si fuera Martín de compras
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién es o la de quién destraba

**Paso 7.** Leda (2026-10-19 11:11)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminaría el lun 26/10 porque le falta el switch.  
  > ⚠️ Vence el jue 22/10. Si la termina el día que dijo, serían 2 días hábiles de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "me falta el switch tmb", "prevision": "2026-10-26", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el lun 26/10 porque le falta el switch
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: dos días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: el cable o Martín
- [ ] no dice: que la fecha cambió

**Paso 8.** Marcos (2026-10-20 15:00): «ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "entregar", "tarea": "COM", "ejemplo": "Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora."}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el cable para programar comunicaciones"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-22"}}}, {"jugada": "entregar", "resultado": "le_falta_evidencia", "tarea": "COM", "entrega": [{"pieza": "P1", "es": "lo_que_escribio", "dice": "ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final", "cubre": []}], "le_falta_del_criterio": ["Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora"], "ejemplo": "Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora.", "sumo": ["P1"], "pregunta": "lo_que_falta_de_la_entrega"}]`
- pregunta: `{"tipo": "lo_que_falta_de_la_entrega", "tarea": "COM", "lo_mostrado": [{"es": "lo_que_escribio", "dice": "ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final", "cubre": [], "pieza": "P1"}], "le_falta_del_criterio": ["Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora"], "ejemplo": "Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora.", "desde_antes": false}`
- latencia: 14094 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que llegó el cable, que ya no está trabada por eso y que seguís con el PLC.  
  > Pasado mañana te voy a preguntar cómo viene.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que decís que la terminaste.  
  > ⚠️ Para recibir la entrega, falta saber si los equipos se comunicaron con el PLC por la red de planta sin errores durante una hora.
  >
  > Podés confirmar esta descripción o escribir la tuya: «Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora».
  >
  > ¿Fue así?
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que quedó anotado que se destrabó y sigue en curso
- [ ] dice: en el bloque de la de comunicaciones: qué falta para revisarla, con un ejemplo sacado del criterio para que lo acepte o lo escriba con sus palabras
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: que la tarea de comunicaciones quedó entregada, en revisión o terminada
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: que la del PLC está terminada
- [ ] no dice: otra vez la pregunta de quién lo destraba
- [ ] no dice: "contaste" o "contarlo": lo que escribió es su descripción (decisión 10; D7)
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real 'Podés confirmar esta descripción o escribir la tuya: «Los equipos de la comprimidora se comunican con el PLC por la red de planta sin errores durante una hora».'

## 30 · Una pregunta de Leda sin contestar · vez 1

Fuente: `tests/conversaciones/30-pregunta-sin-contestar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** nadie (2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, TAB, 2026-10-26) → Marcos:
  > Se acercan los vencimientos de estas tareas:  
  > 🗓️ Cablear tablero de la máquina 3 — vence pasado mañana.  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence jue 29/10.
  >
  > No hace falta responder.
- Leda, por su cuenta (aviso_previo PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence vie 30/10, en 3 días hábiles.
  >
  > No hace falta responder.

**Paso 1.** Marcos (2026-10-28 08:55): «el plc esta trabado, me falta el cable de programacion»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el cable de programacion"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable de programacion", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 6410 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que está trabada porque te falta el cable de programación.  
  > Mientras siga así, no te voy a pedir avances. Retomo el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabarla?
- [ ] dice: que quedó anotado el bloqueo del PLC por el cable
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** nadie (2026-10-28 10:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-28 12:55)
- Leda, por su cuenta (repeticion_del_dia PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Sigue trabada porque te falta el cable de programación.
  >
  > ¿Quién puede conseguirte el cable para destrabarla?
  - hechos: `{"aviso": "repeticion_del_dia", "sobre": {"causa": "me falta el cable de programacion", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-30", "estado": "bloqueada", "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo del PLC por el cable
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del tablero
- [ ] no dice: un reproche porque no contestó

**Paso 4.** nadie (2026-10-28 16:50)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 16:55)
- Leda, por su cuenta (pedido_de_estado TAB, 2026-10-28) → Marcos:
  > 📋 Cablear tablero de la máquina 3  
  > Vence hoy.
  >
  > ¿Cómo viene: ya la empezaste, para cuándo la terminás y hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "TAB", "vence": "2026-10-28", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que el tablero vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del PLC

**Paso 6.** Marcos (2026-10-28 16:57): «el tablero lo arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "TAB"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "TAB", "estado": "en_curso"}]`
- latencia: 6408 ms
- Leda → Marcos:
  > 📋 Cablear tablero de la máquina 3  
  > ✏️ Anoté que lo arrancaste hoy.
  >
  > Contame para cuándo calculás terminarlo y si hay algo que te trabe.
- [ ] dice: que quedó anotado que arrancó el tablero
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la pregunta de quién destraba el PLC

**Paso 7.** Leda (2026-10-28 16:58)
- Leda, por su cuenta (vuelve_la_pregunta PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Sigue trabada porque te falta el cable de programación.
  >
  > ¿Quién puede conseguirte el cable para destrabarla?
  - hechos: `{"aviso": "vuelve_la_pregunta", "sobre": {"causa": "me falta el cable de programacion", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-30", "estado": "bloqueada", "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo del PLC por el cable
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del tablero

**Paso 8.** Leda (2026-10-29 10:00)
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-29) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.
  >
  > ¿Ya la empezaste, para cuándo calculás terminarla y hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-29", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que comunicaciones vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del PLC

**Paso 9.** Marcos (2026-10-29 10:20): «el cable lo consigue pedro de compras»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "pedro de compras"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "pedro de compras", "tarea": "PLC", "pregunta": "quien_es_esa_persona"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "pedro de compras", "desde_antes": false}`
- latencia: 4603 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ No pude identificar a “pedro de compras”, así que todavía no quedó anotado quién consigue el cable.
  >
  > ¿Quién es “pedro de compras”?
- [ ] dice: que no tiene a nadie en el equipo como "Pedro de compras"
- [ ] dice: una sola pregunta: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que quedó anotado quién destraba
- [ ] no dice: a alguien del equipo como si fuera Pedro de compras
- [ ] no dice: la pregunta de cómo viene comunicaciones

**Paso 9b.** Marcos (2026-10-29 10:21): «no es del equipo, es el de compras»
- jugadas: `[{"nombre": "decir_quien_es", "de_afuera": true}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "pedro de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 5700 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que Pedro de compras, que no es del equipo, puede conseguir el cable de programación.  
  > ⚠️ La tarea sigue trabada. Mientras siga así, no te voy a pedir avances.
  >
  > Contame cuando se destrabe para retomar el seguimiento.
- [ ] dice: que quedó anotado que el cable lo consigue Pedro de compras
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la pregunta de cómo viene comunicaciones

**Paso 10.** Leda (2026-10-29 10:22)
- Leda, por su cuenta (vuelve_la_pregunta COM, 2026-10-29) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.
  >
  > ¿Ya la empezaste, para cuándo calculás terminarla y hay algo que te trabe?
  - hechos: `{"aviso": "vuelve_la_pregunta", "tarea": "COM", "vence": "2026-10-29", "pregunta": "estado_de_la_tarea", "necesita_respuesta": true}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del PLC

**Paso 11.** Marcos (2026-10-29 10:40): «comunicaciones la arranque recien»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 6051 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que la arrancaste recién.
  >
  > Contame para cuándo calculás terminarla y si hay algo que te trabe.
- [ ] dice: que quedó anotado que arrancó comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 12.** nadie (2026-10-29 11:15)
- (Leda no manda nada)

## 30 · Una pregunta de Leda sin contestar · vez 2

Fuente: `tests/conversaciones/30-pregunta-sin-contestar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** nadie (2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, TAB, 2026-10-26) → Marcos:
  > Se acercan estos vencimientos:
  >
  > 🗓️ Cablear tablero de la máquina 3 — pasado mañana  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — jue 29/10
  >
  > No hace falta responder.
- Leda, por su cuenta (aviso_previo PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 30/10, dentro de 3 días hábiles.
  >
  > No hace falta responder.

**Paso 1.** Marcos (2026-10-28 08:55): «el plc esta trabado, me falta el cable de programacion»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el cable de programacion"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable de programacion", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5873 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que está trabada porque te falta el cable de programación.  
  > Mientras siga así, no te voy a pedir avances. Retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede conseguir el cable para destrabarla?
- [ ] dice: que quedó anotado el bloqueo del PLC por el cable
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** nadie (2026-10-28 10:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-28 12:55)
- Leda, por su cuenta (repeticion_del_dia PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Sigue trabada porque te falta el cable de programación.
  >
  > ¿Quién puede conseguir el cable para destrabarla?
  - hechos: `{"aviso": "repeticion_del_dia", "sobre": {"causa": "me falta el cable de programacion", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-30", "estado": "bloqueada", "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo del PLC por el cable
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del tablero
- [ ] no dice: un reproche porque no contestó

**Paso 4.** nadie (2026-10-28 16:50)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 16:55)
- Leda, por su cuenta (pedido_de_estado TAB, 2026-10-28) → Marcos:
  > 📋 Cablear tablero de la máquina 3  
  > Vence hoy.
  >
  > ¿Cómo viene: ya la empezaste, para cuándo pensás terminarla y hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "TAB", "vence": "2026-10-28", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que el tablero vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del PLC

**Paso 6.** Marcos (2026-10-28 16:57): «el tablero lo arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "TAB"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "TAB", "estado": "en_curso"}]`
- latencia: 7258 ms
- Leda → Marcos:
  > 📋 Cablear tablero de la máquina 3  
  > ✏️ Quedó anotado que la empezaste hoy.
  >
  > Contame para cuándo pensás terminarla y si hay algo que te trabe.
- [ ] dice: que quedó anotado que arrancó el tablero
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la pregunta de quién destraba el PLC

**Paso 7.** Leda (2026-10-28 16:58)
- Leda, por su cuenta (vuelve_la_pregunta PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Sigue trabada porque te falta el cable de programación.
  >
  > ¿Quién puede conseguir el cable para destrabarla?
  - hechos: `{"aviso": "vuelve_la_pregunta", "sobre": {"causa": "me falta el cable de programacion", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-30", "estado": "bloqueada", "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo del PLC por el cable
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del tablero

**Paso 8.** Leda (2026-10-29 10:00)
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-29) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.
  >
  > ¿Cómo viene: ya la empezaste, para cuándo pensás terminarla y hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-29", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que comunicaciones vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del PLC

**Paso 9.** Marcos (2026-10-29 10:20): «el cable lo consigue pedro de compras»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "pedro de compras"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "pedro de compras", "tarea": "PLC", "pregunta": "quien_es_esa_persona"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "pedro de compras", "desde_antes": false}`
- latencia: 7110 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ No identifico a «pedro de compras» en el equipo, así que todavía no quedó anotado quién puede conseguir el cable.
  >
  > ¿Quién es «pedro de compras»?
- [ ] dice: que no tiene a nadie en el equipo como "Pedro de compras"
- [ ] dice: una sola pregunta: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que quedó anotado quién destraba
- [ ] no dice: a alguien del equipo como si fuera Pedro de compras
- [ ] no dice: la pregunta de cómo viene comunicaciones

**Paso 9b.** Marcos (2026-10-29 10:21): «no es del equipo, es el de compras»
- jugadas: `[{"nombre": "decir_quien_es", "de_afuera": true}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "pedro de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 7159 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que Pedro de compras, que no es del equipo, puede conseguir el cable.  
  > Mientras siga trabada, no te voy a pedir avances.
  >
  > Avisame cuando se destrabe y retomaré el seguimiento.
- [ ] dice: que quedó anotado que el cable lo consigue Pedro de compras
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la pregunta de cómo viene comunicaciones

**Paso 10.** Leda (2026-10-29 10:22)
- Leda, por su cuenta (vuelve_la_pregunta COM, 2026-10-29) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.
  >
  > ¿Cómo viene: ya la empezaste, para cuándo pensás terminarla y hay algo que te trabe?
  - hechos: `{"aviso": "vuelve_la_pregunta", "tarea": "COM", "vence": "2026-10-29", "pregunta": "estado_de_la_tarea", "necesita_respuesta": true}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del PLC

**Paso 11.** Marcos (2026-10-29 10:40): «comunicaciones la arranque recien»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 4465 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste recién.
  >
  > ¿Para cuándo pensás terminarla y hay algo que te trabe?
- [ ] dice: que quedó anotado que arrancó comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 12.** nadie (2026-10-29 11:15)
- (Leda no manda nada)

## 30 · Una pregunta de Leda sin contestar · vez 3

Fuente: `tests/conversaciones/30-pregunta-sin-contestar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** nadie (2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, TAB, 2026-10-26) → Marcos:
  > Se acercan estos vencimientos:
  >
  > 🗓️ Cablear tablero de la máquina 3 — pasado mañana  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — jue 29/10
  >
  > No hace falta responder.
- Leda, por su cuenta (aviso_previo PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 30/10, dentro de 3 días hábiles.
  >
  > No hace falta responder.

**Paso 1.** Marcos (2026-10-28 08:55): «el plc esta trabado, me falta el cable de programacion»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el cable de programacion"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable de programacion", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5669 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que está trabada porque te falta el cable de programación.  
  > No te voy a pedir avances mientras siga trabada; retomo el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede conseguir el cable?
- [ ] dice: que quedó anotado el bloqueo del PLC por el cable
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** nadie (2026-10-28 10:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-28 12:55)
- Leda, por su cuenta (repeticion_del_dia PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Sigue trabada porque te falta el cable de programación.
  >
  > ¿Quién puede conseguir el cable?
  - hechos: `{"aviso": "repeticion_del_dia", "sobre": {"causa": "me falta el cable de programacion", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-30", "estado": "bloqueada", "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo del PLC por el cable
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del tablero
- [ ] no dice: un reproche porque no contestó

**Paso 4.** nadie (2026-10-28 16:50)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 16:55)
- Leda, por su cuenta (pedido_de_estado TAB, 2026-10-28) → Marcos:
  > 📋 Cablear tablero de la máquina 3  
  > Vence hoy.
  >
  > ¿Ya la empezaste? Si no, ¿para cuándo la terminás o hay algo que te traba?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "TAB", "vence": "2026-10-28", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que el tablero vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del PLC
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿Ya la empezaste? Si no, ¿para cuándo la terminás o hay algo que te traba?'

**Paso 6.** Marcos (2026-10-28 16:57): «el tablero lo arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "TAB"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "TAB", "estado": "en_curso"}]`
- latencia: 6309 ms
- Leda → Marcos:
  > 📋 Cablear tablero de la máquina 3  
  > ✏️ Quedó anotado que lo arrancaste hoy.
  >
  > Seguí con el tablero.
- [ ] dice: que quedó anotado que arrancó el tablero
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la pregunta de quién destraba el PLC

**Paso 7.** Leda (2026-10-28 16:58)
- Leda, por su cuenta (vuelve_la_pregunta PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Sigue trabada porque te falta el cable de programación.
  >
  > ¿Quién puede conseguir el cable?
  - hechos: `{"aviso": "vuelve_la_pregunta", "sobre": {"causa": "me falta el cable de programacion", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-30", "estado": "bloqueada", "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo del PLC por el cable
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del tablero

**Paso 8.** Leda (2026-10-29 10:00)
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-29) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.
  >
  > ¿Cómo venís con esta tarea: la empezaste, para cuándo la terminás o hay algo que te traba?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-29", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que comunicaciones vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del PLC

**Paso 9.** Marcos (2026-10-29 10:20): «el cable lo consigue pedro de compras»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "pedro de compras"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "pedro de compras", "tarea": "PLC", "pregunta": "quien_es_esa_persona"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "pedro de compras", "desde_antes": false}`
- latencia: 5636 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ No sé quién es «pedro de compras», así que todavía no quedó anotado quién puede conseguir el cable.
  >
  > ¿Quién es Pedro?
- [ ] dice: que no tiene a nadie en el equipo como "Pedro de compras"
- [ ] dice: una sola pregunta: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que quedó anotado quién destraba
- [ ] no dice: a alguien del equipo como si fuera Pedro de compras
- [ ] no dice: la pregunta de cómo viene comunicaciones

**Paso 9b.** Marcos (2026-10-29 10:21): «no es del equipo, es el de compras»
- jugadas: `[{"nombre": "decir_quien_es", "de_afuera": true}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "pedro de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 5327 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que Pedro, de compras, puede conseguir el cable de programación.  
  > No te voy a pedir avances mientras siga trabada.
  >
  > Avisame cuando se destrabe.
- [ ] dice: que quedó anotado que el cable lo consigue Pedro de compras
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la pregunta de cómo viene comunicaciones

**Paso 10.** Leda (2026-10-29 10:22)
- Leda, por su cuenta (vuelve_la_pregunta COM, 2026-10-29) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy. Vuelvo a preguntarte por esta tarea.
  >
  > ¿La empezaste? Si no, ¿para cuándo la terminás o hay algo que te traba?
  - hechos: `{"aviso": "vuelve_la_pregunta", "tarea": "COM", "vence": "2026-10-29", "pregunta": "estado_de_la_tarea", "necesita_respuesta": true}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del PLC
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿La empezaste? Si no, ¿para cuándo la terminás o hay algo que te traba?'

**Paso 11.** Marcos (2026-10-29 10:40): «comunicaciones la arranque recien»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 4598 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la empezaste recién.
  >
  > Seguí con la revisión.
- [ ] dice: que quedó anotado que arrancó comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 12.** nadie (2026-10-29 11:15)
- (Leda no manda nada)

## 30 · Una pregunta de Leda sin contestar · vez 4

Fuente: `tests/conversaciones/30-pregunta-sin-contestar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** nadie (2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, TAB, 2026-10-26) → Marcos:
  > Se acercan estos vencimientos:
  >
  > 🗓️ Cablear tablero de la máquina 3 — pasado mañana  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — jue 29/10
  >
  > No hace falta responder.
- Leda, por su cuenta (aviso_previo PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 30/10, en 3 días hábiles.
  >
  > No hace falta responder.

**Paso 1.** Marcos (2026-10-28 08:55): «el plc esta trabado, me falta el cable de programacion»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el cable de programacion"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable de programacion", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5420 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que está trabada porque te falta el cable de programación.  
  > No te voy a pedir avances mientras siga trabada; retomo el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede conseguir el cable?
- [ ] dice: que quedó anotado el bloqueo del PLC por el cable
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** nadie (2026-10-28 10:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-28 12:55)
- Leda, por su cuenta (repeticion_del_dia PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Sigue trabada porque te falta el cable de programación. Vence pasado mañana.
  >
  > ¿Quién puede conseguir el cable?
  - hechos: `{"aviso": "repeticion_del_dia", "sobre": {"causa": "me falta el cable de programacion", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-30", "estado": "bloqueada", "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo del PLC por el cable
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del tablero
- [ ] no dice: un reproche porque no contestó

**Paso 4.** nadie (2026-10-28 16:50)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 16:55)
- Leda, por su cuenta (pedido_de_estado TAB, 2026-10-28) → Marcos:
  > 📋 Cablear tablero de la máquina 3  
  > Vence hoy.
  >
  > ¿La empezaste, para cuándo la terminás y hay algo que te impida avanzar?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "TAB", "vence": "2026-10-28", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que el tablero vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del PLC

**Paso 6.** Marcos (2026-10-28 16:57): «el tablero lo arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "TAB"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "TAB", "estado": "en_curso"}]`
- latencia: 6367 ms
- Leda → Marcos:
  > 📋 Cablear tablero de la máquina 3  
  > ✏️ Quedó anotado que la arrancaste hoy.
  >
  > Contame para cuándo calculás terminarla y si hay algo que te impida avanzar.
- [ ] dice: que quedó anotado que arrancó el tablero
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la pregunta de quién destraba el PLC

**Paso 7.** Leda (2026-10-28 16:58)
- Leda, por su cuenta (vuelve_la_pregunta PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Sigue trabada porque te falta el cable de programación. Vence pasado mañana.
  >
  > ¿Quién puede conseguir el cable?
  - hechos: `{"aviso": "vuelve_la_pregunta", "sobre": {"causa": "me falta el cable de programacion", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-30", "estado": "bloqueada", "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo del PLC por el cable
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del tablero

**Paso 8.** Leda (2026-10-29 10:00)
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-29) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.
  >
  > ¿La empezaste, para cuándo la terminás y hay algo que te impida avanzar?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-29", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que comunicaciones vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del PLC

**Paso 9.** Marcos (2026-10-29 10:20): «el cable lo consigue pedro de compras»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "pedro de compras"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "pedro de compras", "tarea": "PLC", "pregunta": "quien_es_esa_persona"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "pedro de compras", "desde_antes": false}`
- latencia: 5857 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ No encuentro a «pedro de compras» en el equipo, así que todavía no quedó anotado quién puede conseguir el cable.
  >
  > ¿A quién te referís con «pedro de compras»?
- [ ] dice: que no tiene a nadie en el equipo como "Pedro de compras"
- [ ] dice: una sola pregunta: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que quedó anotado quién destraba
- [ ] no dice: a alguien del equipo como si fuera Pedro de compras
- [ ] no dice: la pregunta de cómo viene comunicaciones

**Paso 9b.** Marcos (2026-10-29 10:21): «no es del equipo, es el de compras»
- jugadas: `[{"nombre": "decir_quien_es", "de_afuera": true}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "pedro de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 5147 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que Pedro, de compras y fuera del equipo, puede conseguir el cable.  
  > No te voy a pedir avances mientras siga trabada.
  >
  > Avisame cuando se destrabe.
- [ ] dice: que quedó anotado que el cable lo consigue Pedro de compras
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la pregunta de cómo viene comunicaciones

**Paso 10.** Leda (2026-10-29 10:22)
- Leda, por su cuenta (vuelve_la_pregunta COM, 2026-10-29) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.
  >
  > ¿La empezaste, para cuándo calculás terminarla y hay algo que te impida avanzar?
  - hechos: `{"aviso": "vuelve_la_pregunta", "tarea": "COM", "vence": "2026-10-29", "pregunta": "estado_de_la_tarea", "necesita_respuesta": true}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del PLC

**Paso 11.** Marcos (2026-10-29 10:40): «comunicaciones la arranque recien»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 6520 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste recién. Vence hoy.
  >
  > Contame para cuándo calculás terminarla y si hay algo que te impida avanzar.
- [ ] dice: que quedó anotado que arrancó comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 12.** nadie (2026-10-29 11:15)
- (Leda no manda nada)

## 30 · Una pregunta de Leda sin contestar · vez 5

Fuente: `tests/conversaciones/30-pregunta-sin-contestar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** nadie (2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, TAB, 2026-10-26) → Marcos:
  > Se acercan estos vencimientos:
  >
  > 🗓️ Cablear tablero de la máquina 3 — vence pasado mañana.  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence jue 29/10.
  >
  > No hace falta responder.
- Leda, por su cuenta (aviso_previo PLC, 2026-10-27) → Marcos:
  > 🗓️ Programar PLC de la comprimidora — vence vie 30/10.
  >
  > No hace falta responder.

**Paso 1.** Marcos (2026-10-28 08:55): «el plc esta trabado, me falta el cable de programacion»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el cable de programacion"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable de programacion", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5844 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que está trabada porque te falta el cable de programación.  
  > Mientras siga trabada, no te voy a pedir el estado; retomo cuando me cuentes que se destrabó.
  >
  > ¿Quién puede conseguir el cable para destrabarla: vos u otra persona?
- [ ] dice: que quedó anotado el bloqueo del PLC por el cable
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** nadie (2026-10-28 10:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-28 12:55)
- Leda, por su cuenta (repeticion_del_dia PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Sigue trabada porque te falta el cable de programación.
  >
  > ¿Quién puede conseguir el cable para destrabarla: vos u otra persona?
  - hechos: `{"aviso": "repeticion_del_dia", "sobre": {"causa": "me falta el cable de programacion", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-30", "estado": "bloqueada", "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo del PLC por el cable
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del tablero
- [ ] no dice: un reproche porque no contestó

**Paso 4.** nadie (2026-10-28 16:50)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 16:55)
- Leda, por su cuenta (pedido_de_estado TAB, 2026-10-28) → Marcos:
  > 📋 Cablear tablero de la máquina 3  
  > Vence hoy.
  >
  > ¿Cómo viene: ya la empezaste, para cuándo la terminás y hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "TAB", "vence": "2026-10-28", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que el tablero vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del PLC

**Paso 6.** Marcos (2026-10-28 16:57): «el tablero lo arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "TAB"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "TAB", "estado": "en_curso"}]`
- latencia: 6915 ms
- Leda → Marcos:
  > 📋 Cablear tablero de la máquina 3  
  > ✏️ Anoté que la empezaste hoy.
  >
  > Avisame cuando sepas para cuándo la terminás.
- [ ] dice: que quedó anotado que arrancó el tablero
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la pregunta de quién destraba el PLC

**Paso 7.** Leda (2026-10-28 16:58)
- Leda, por su cuenta (vuelve_la_pregunta PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Sigue trabada porque te falta el cable de programación.
  >
  > ¿Quién puede conseguir el cable para destrabarla: vos u otra persona?
  - hechos: `{"aviso": "vuelve_la_pregunta", "sobre": {"causa": "me falta el cable de programacion", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-30", "estado": "bloqueada", "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo del PLC por el cable
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del tablero

**Paso 8.** Leda (2026-10-29 10:00)
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-29) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.
  >
  > ¿Cómo viene: ya la empezaste, para cuándo la terminás y hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-29", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que comunicaciones vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del PLC

**Paso 9.** Marcos (2026-10-29 10:20): «el cable lo consigue pedro de compras»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "pedro de compras"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "pedro de compras", "tarea": "PLC", "pregunta": "quien_es_esa_persona"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "pedro de compras", "desde_antes": false}`
- latencia: 5558 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ No tengo identificado a “pedro de compras”, así que todavía no pude anotar quién puede conseguir el cable.
  >
  > ¿Quién es “pedro de compras”?
- [ ] dice: que no tiene a nadie en el equipo como "Pedro de compras"
- [ ] dice: una sola pregunta: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que quedó anotado quién destraba
- [ ] no dice: a alguien del equipo como si fuera Pedro de compras
- [ ] no dice: la pregunta de cómo viene comunicaciones

**Paso 9b.** Marcos (2026-10-29 10:21): «no es del equipo, es el de compras»
- jugadas: `[{"nombre": "decir_quien_es", "de_afuera": true}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "pedro de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 4134 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que Pedro de compras, que no es del equipo, puede conseguir el cable de programación.  
  > Mientras siga trabada, no te voy a pedir el estado.
  >
  > Avisame cuando se destrabe.
- [ ] dice: que quedó anotado que el cable lo consigue Pedro de compras
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la pregunta de cómo viene comunicaciones

**Paso 10.** Leda (2026-10-29 10:22)
- Leda, por su cuenta (vuelve_la_pregunta COM, 2026-10-29) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.
  >
  > ¿Cómo viene: ya la empezaste, para cuándo la terminás y hay algo que te trabe?
  - hechos: `{"aviso": "vuelve_la_pregunta", "tarea": "COM", "vence": "2026-10-29", "pregunta": "estado_de_la_tarea", "necesita_respuesta": true}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada del PLC

**Paso 11.** Marcos (2026-10-29 10:40): «comunicaciones la arranque recien»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 5166 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que la acabás de empezar.
  >
  > Avisame cuando sepas para cuándo la terminás y si hay algo que te trabe.
- [ ] dice: que quedó anotado que arrancó comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 12.** nadie (2026-10-29 11:15)
- (Leda no manda nada)

## 47 · Los apodos · vez 1

Fuente: `tests/conversaciones/47-apodos.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Nahuel (2026-10-20 10:00): «el plc esta trabado, me falta el plano del tablero y me lo tiene que pasar el tano»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el plano del tablero"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "el tano"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el plano del tablero", "pregunta_para_despues": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "el tano", "tarea": "PLC", "pregunta": "quien_es_esa_persona"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "el tano", "desde_antes": false}`
- latencia: 8938 ms
- Leda → Nahuel:
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Anoté que está trabada porque te falta el plano del tablero.  
  > No te voy a pedir avances mientras siga trabada; retomo cuando me cuentes que se destrabó.
  >
  > ¿Quién es «el tano»?
- [ ] dice: que quedó anotado que el PLC está trabado por el plano del tablero
- [ ] dice: que no tiene a nadie en el equipo como "el Tano"
- [ ] dice: una sola pregunta: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que le va a preguntar a alguien
- [ ] no dice: un nombre de alguien del equipo como si fuera "el Tano"

**Paso 2.** Nahuel (2026-10-20 10:01): «mariano»
- jugadas: `[{"nombre": "decir_quien_es", "quien_es": "mariano"}]`
- hechos: `[{"jugada": "decir_quien_es", "resultado": "quien_es_para_confirmar", "como_lo_nombro": "el tano", "integrante": "Mariano Naim", "pregunta": "confirmar_quien_es_esa_persona"}]`
- pregunta: `{"tipo": "confirmar_quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "el tano", "integrante": "Mariano Naim", "opciones": [{"opcion": "O1", "etiqueta": "Confirmar"}], "desde_antes": false}`
- latencia: 9744 ms
- Leda → Nahuel: [botones: Confirmar]
  > 📋 Programar el PLC de la envasadora  
  > Para anotar quién te tiene que pasar el plano, necesito confirmar a quién llamás «el tano».  
  > Podés tocar Confirmar o responder por escrito.
  >
  > ¿«El tano» es Mariano Naim?
- [ ] dice: la confirmación con nombre y apellido: si «el Tano» es Mariano Naim
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que ya lo anotó o que le pregunta a Mariano

**Paso 3.** Nahuel (2026-10-20 10:02): «[toca] Confirmar»
- jugadas: `[{"nombre": "elegir", "opcion": "Confirmar"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"integrante": "Mariano Naim"}, "se_le_pregunta_a": {"a": "Mariano Naim", "llega": "2026-10-20T10:12:00-03:00"}, "aprendio_como_le_dicen_a": "Mariano Naim", "eligio": {"opcion": "O1", "etiqueta": "Confirmar"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 5811 ms
- Leda → Nahuel:
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Anoté que Mariano puede destrabarla. Ya sé que a él le decís «el tano».  
  > Mariano será consultado hoy a las 10:12 sobre cuándo puede destrabarla.
  >
  > Cuando se destrabe, avisame y retomo el seguimiento.
- [ ] dice: que el PLC quedó trabado esperando el plano de Mariano
- [ ] dice: que le pregunta a Mariano para cuándo y le avisa apenas sepa algo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Tano» para nombrar a Mariano

**Paso 4.** Leda (2026-10-20 10:12)
- Leda, por su cuenta (pregunta_a_quien_destraba PLC, 2026-10-20) → Mariano:
  > 📋 Programar el PLC de la envasadora  
  > ⚠️ Nahuel está trabado porque le falta el plano del tablero.
  >
  > ¿Para cuándo podés pasarle el plano?
  - hechos: `{"aviso": "pregunta_a_quien_destraba", "causa": "me falta el plano del tablero", "tarea": "PLC", "pregunta": "cuando_se_destraba", "responsable": "Nahuel Gimenez", "necesita_respuesta": true}`
- [ ] dice: que Nahuel está trabado con el PLC porque le falta el plano del tablero
- [ ] dice: la pregunta: para cuándo se lo puede pasar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Tano»

**Paso 5.** Lucas (2026-10-20 11:00): «lo del rack esta trabado, el tano me tiene q pasar la medida del tablero»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "RACK", "causa": "me tiene q pasar la medida del tablero"}, {"nombre": "anotar_quien_destraba", "tarea": "RACK", "quien": "el tano"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "RACK", "causa": "me tiene q pasar la medida del tablero", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "RACK", "quien_destraba": {"integrante": "Mariano Naim"}, "se_le_pregunta_a": {"a": "Mariano Naim", "llega": "2026-10-20T11:10:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 7295 ms
- Leda → Lucas:
  > 📋 Armar el rack del servidor  
  > ✏️ Quedó anotado que está trabado porque te falta la medida del tablero y que Mariano puede destrabarlo.  
  > Mariano será consultado hoy a las 11:10 sobre cuándo puede destrabarlo.  
  > Mientras siga trabado, no te voy a pedir avances.
  >
  > Avisame cuando se destrabe.
- [ ] dice: que el rack quedó trabado esperando la medida del tablero de Mariano
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Tano» para nombrar a Mariano
- [ ] no dice: que no sabe quién es

**Paso 6.** Lucas (2026-10-20 11:30): «y lo del switch tambien, me falta que el chino me habilite el tablero»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "SW", "causa": "me falta que el chino me habilite el tablero"}, {"nombre": "anotar_quien_destraba", "tarea": "SW", "quien": "el chino"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "SW", "causa": "me falta que el chino me habilite el tablero", "pregunta_para_despues": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "el chino", "tarea": "SW", "pregunta": "quien_es_esa_persona"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "SW", "como_lo_nombro": "el chino", "desde_antes": false}`
- latencia: 8477 ms
- Leda → Lucas:
  > 📋 Configurar el switch de la planta  
  > ✏️ Quedó anotado que está trabada porque te falta que «el chino» te habilite el tablero.  
  > Mientras siga trabada, no te voy a pedir avances.
  >
  > ¿Quién es «el chino»?
- [ ] dice: que no tiene a nadie en el equipo como "el Chino"
- [ ] dice: una sola pregunta: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 7.** Lucas (2026-10-20 11:31): «mariano tambien»
- jugadas: `[{"nombre": "decir_quien_es", "quien_es": "mariano"}]`
- hechos: `[{"jugada": "decir_quien_es", "resultado": "quien_es_para_confirmar", "como_lo_nombro": "el chino", "integrante": "Mariano Naim", "pregunta": "confirmar_quien_es_esa_persona"}]`
- pregunta: `{"tipo": "confirmar_quien_es_esa_persona", "tarea": "SW", "como_lo_nombro": "el chino", "integrante": "Mariano Naim", "opciones": [{"opcion": "O1", "etiqueta": "Confirmar"}], "desde_antes": false}`
- latencia: 6684 ms
- Leda → Lucas: [botones: Confirmar]
  > 📋 Configurar el switch de la planta  
  > Para anotar quién puede destrabarla, necesito confirmar a quién llamás «el chino».  
  > Podés tocar Confirmar o responder por escrito.
  >
  > ¿«El chino» es Mariano Naim?
- [ ] dice: la confirmación con nombre y apellido: si «el Chino» es Mariano Naim
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 8.** Lucas (2026-10-20 11:32): «[toca] Confirmar»
- jugadas: `[{"nombre": "elegir", "opcion": "Confirmar"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "SW", "quien_destraba": {"integrante": "Mariano Naim"}, "se_le_pregunta_a": {"a": "Mariano Naim", "llega": "2026-10-20T11:42:00-03:00"}, "aprendio_como_le_dicen_a": "Mariano Naim", "eligio": {"opcion": "O1", "etiqueta": "Confirmar"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 4130 ms
- Leda → Lucas:
  > 📋 Configurar el switch de la planta  
  > ✏️ Quedó anotado que Mariano puede destrabarla. Ya sé que a él le decís «el chino».  
  > Mariano será consultado hoy a las 11:42 sobre cuándo puede destrabarla.  
  > Mientras siga trabada, no te voy a pedir avances.
  >
  > Avisame cuando se destrabe.
- [ ] dice: que el switch quedó trabado esperando que Mariano habilite el tablero
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Chino» o «el Tano» para nombrar a Mariano

**Paso 10.** Nahuel (2026-10-20 15:00): «la del plc ya no esta trabada por el plano, ahora me falta que el flaco me de acceso a la red»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta que el flaco me de acceso a la red"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "el flaco"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el plano del tablero"}, "estado": "en_curso", "ya_no_hace_falta_que_destraben": [{"aviso_a_quien_destrababa": {"a": "Mariano Naim", "llega": "2026-10-20T15:10:00-03:00"}}]}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta que el flaco me de acceso a la red", "pregunta_para_despues": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "el flaco", "coinciden": ["Marcos Tarquini", "Martín Forte"], "tarea": "PLC", "pregunta": "cual_de_esas_personas"}]`
- pregunta: `{"tipo": "cual_de_esas_personas", "tarea": "PLC", "como_lo_nombro": "el flaco", "opciones": [{"opcion": "O1", "etiqueta": "Marcos Tarquini"}, {"opcion": "O2", "etiqueta": "Martín Forte"}], "desde_antes": false}`
- latencia: 7981 ms
- Leda → Nahuel: [botones: Marcos Tarquini, Martín Forte]
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Anoté que ya no está trabada por el plano. Mariano será avisado hoy a las 15:10 de que ya no hace falta que la destrabe por eso.  
  > ⚠️ Anoté que ahora te falta acceso a la red. No te voy a pedir avances mientras siga trabada.
  >
  > Podés elegir Marcos Tarquini o Martín Forte, tocando la opción o escribiendo.
  >
  > ¿A cuál de ellos llamás «el flaco»?
- [ ] dice: la pregunta, con nombre y apellido de cada uno: si «el Flaco» es Martín Forte o Marcos Tarquini
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que lo destraba Martín o Marcos

**Paso 11.** Nahuel (2026-10-20 15:01): «[toca] Martín Forte»
- jugadas: `[{"nombre": "elegir", "opcion": "Martín Forte"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"integrante": "Martín Forte"}, "se_le_pregunta_a": {"a": "Martín Forte", "llega": "2026-10-20T15:11:00-03:00"}, "eligio": {"opcion": "O2", "etiqueta": "Martín Forte"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 3273 ms
- Leda → Nahuel:
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Anoté que Martín puede destrabarla.  
  > Martín será consultado hoy a las 15:11 sobre cuándo puede darte acceso a la red.
  >
  > Cuando tengas acceso, avisame y retomo el seguimiento.
- [ ] dice: que la del PLC quedó trabada esperando el acceso a la red de Martín
- [ ] dice: que le pregunta a Martín y le avisa apenas sepa algo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Flaco» para nombrar a Martín

## 47 · Los apodos · vez 2

Fuente: `tests/conversaciones/47-apodos.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M ok · F ok.

**Paso 1.** Nahuel (2026-10-20 10:00): «el plc esta trabado, me falta el plano del tablero y me lo tiene que pasar el tano»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el plano del tablero"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "el tano"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el plano del tablero", "pregunta_para_despues": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "el tano", "tarea": "PLC", "pregunta": "quien_es_esa_persona"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "el tano", "desde_antes": false}`
- latencia: 5933 ms
- Leda → Nahuel:
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Quedó anotado que está trabada porque te falta el plano del tablero.  
  > No te voy a pedir avances mientras siga trabada.
  >
  > ¿Quién es «el tano»?
- [ ] dice: que quedó anotado que el PLC está trabado por el plano del tablero
- [ ] dice: que no tiene a nadie en el equipo como "el Tano"
- [ ] dice: una sola pregunta: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que le va a preguntar a alguien
- [ ] no dice: un nombre de alguien del equipo como si fuera "el Tano"

**Paso 2.** Nahuel (2026-10-20 10:01): «mariano»
- jugadas: `[{"nombre": "decir_quien_es", "quien_es": "mariano"}]`
- hechos: `[{"jugada": "decir_quien_es", "resultado": "quien_es_para_confirmar", "como_lo_nombro": "el tano", "integrante": "Mariano Naim", "pregunta": "confirmar_quien_es_esa_persona"}]`
- pregunta: `{"tipo": "confirmar_quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "el tano", "integrante": "Mariano Naim", "opciones": [{"opcion": "O1", "etiqueta": "Confirmar"}], "desde_antes": false}`
- latencia: 5960 ms
- Leda → Nahuel: [botones: Confirmar]
  > 📋 Programar el PLC de la envasadora  
  > Falta confirmar quién te tiene que pasar el plano del tablero.  
  > Podés tocar Confirmar o responder escribiendo.
  >
  > ¿«El tano» es Mariano?
- [ ] dice: la confirmación con nombre y apellido: si «el Tano» es Mariano Naim
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que ya lo anotó o que le pregunta a Mariano

**Paso 3.** Nahuel (2026-10-20 10:02): «[toca] Confirmar»
- jugadas: `[{"nombre": "elegir", "opcion": "Confirmar"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"integrante": "Mariano Naim"}, "se_le_pregunta_a": {"a": "Mariano Naim", "llega": "2026-10-20T10:12:00-03:00"}, "aprendio_como_le_dicen_a": "Mariano Naim", "eligio": {"opcion": "O1", "etiqueta": "Confirmar"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 8326 ms
- Leda → Nahuel:
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Quedó anotado que Mariano puede destrabarla y que a él le decís «el tano».  
  > Mariano será consultado hoy a las 10:12 sobre cuándo podrá destrabarla.  
  > No te voy a pedir avances mientras siga trabada.
  >
  > Cuando se destrabe, avisame.
- [ ] dice: que el PLC quedó trabado esperando el plano de Mariano
- [ ] dice: que le pregunta a Mariano para cuándo y le avisa apenas sepa algo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Tano» para nombrar a Mariano

**Paso 4.** Leda (2026-10-20 10:12)
- Leda, por su cuenta (pregunta_a_quien_destraba PLC, 2026-10-20) → Mariano:
  > 📋 Programar el PLC de la envasadora  
  > ⚠️ Nahuel dijo que le falta el plano del tablero para avanzar.
  >
  > ¿Para cuándo podés resolver lo del plano?
  - hechos: `{"aviso": "pregunta_a_quien_destraba", "causa": "me falta el plano del tablero", "tarea": "PLC", "pregunta": "cuando_se_destraba", "responsable": "Nahuel Gimenez", "necesita_respuesta": true}`
- [ ] dice: que Nahuel está trabado con el PLC porque le falta el plano del tablero
- [ ] dice: la pregunta: para cuándo se lo puede pasar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Tano»

**Paso 5.** Lucas (2026-10-20 11:00): «lo del rack esta trabado, el tano me tiene q pasar la medida del tablero»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "RACK", "causa": "el tano me tiene q pasar la medida del tablero"}, {"nombre": "anotar_quien_destraba", "tarea": "RACK", "quien": "el tano"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "RACK", "causa": "el tano me tiene q pasar la medida del tablero", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "RACK", "quien_destraba": {"integrante": "Mariano Naim"}, "se_le_pregunta_a": {"a": "Mariano Naim", "llega": "2026-10-20T11:10:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 10233 ms
- Leda → Lucas:
  > 📋 Armar el rack del servidor  
  > ⚠️ Quedó anotado que está trabada porque necesitás la medida del tablero que te tiene que pasar el Tano.  
  > ✏️ También quedó anotado que Mariano puede destrabarla. Hoy a las 11:10, Mariano será consultado sobre cuándo podrá hacerlo.
  >
  > Mientras siga trabada, no te voy a pedir avances.
  >
  > Avisame cuando se destrabe para retomar el seguimiento.
- [ ] dice: que el rack quedó trabado esperando la medida del tablero de Mariano
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Tano» para nombrar a Mariano
- [ ] no dice: que no sabe quién es

**Paso 6.** Lucas (2026-10-20 11:30): «y lo del switch tambien, me falta que el chino me habilite el tablero»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "SW", "causa": "me falta que el chino me habilite el tablero"}, {"nombre": "anotar_quien_destraba", "tarea": "SW", "quien": "el chino"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "SW", "causa": "me falta que el chino me habilite el tablero", "pregunta_para_despues": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "el chino", "tarea": "SW", "pregunta": "quien_es_esa_persona"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "SW", "como_lo_nombro": "el chino", "desde_antes": false}`
- latencia: 7236 ms
- Leda → Lucas:
  > 📋 Configurar el switch de la planta  
  > ✏️ Quedó anotado que está trabada porque te falta que “el chino” te habilite el tablero.  
  > Mientras siga trabada, no te voy a pedir avances.  
  > ⚠️ No sé quién es “el chino”, así que todavía no quedó anotado quién puede destrabarla.
  >
  > ¿Quién es “el chino”?
- [ ] dice: que no tiene a nadie en el equipo como "el Chino"
- [ ] dice: una sola pregunta: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 7.** Lucas (2026-10-20 11:31): «mariano tambien»
- jugadas: `[{"nombre": "decir_quien_es", "quien_es": "Mariano"}]`
- hechos: `[{"jugada": "decir_quien_es", "resultado": "quien_es_para_confirmar", "como_lo_nombro": "el chino", "integrante": "Mariano Naim", "pregunta": "confirmar_quien_es_esa_persona"}]`
- pregunta: `{"tipo": "confirmar_quien_es_esa_persona", "tarea": "SW", "como_lo_nombro": "el chino", "integrante": "Mariano Naim", "opciones": [{"opcion": "O1", "etiqueta": "Confirmar"}], "desde_antes": false}`
- latencia: 7160 ms
- Leda → Lucas: [botones: Confirmar]
  > 📋 Configurar el switch de la planta  
  > Entendí que «el chino» podría ser Mariano Naim. Todavía no quedó anotado que él puede destrabarla.
  >
  > Podés tocar Confirmar o responder por escrito.
  >
  > ¿«El chino» es Mariano Naim?
- [ ] dice: la confirmación con nombre y apellido: si «el Chino» es Mariano Naim
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [comprension] jugadas: esperado [{'nombre': 'decir_quien_es', 'quien_es': 'mariano'}], real [{'nombre': 'decir_quien_es', 'quien_es': 'Mariano'}]

**Paso 8.** Lucas (2026-10-20 11:32): «[toca] Confirmar»
- jugadas: `[{"nombre": "elegir", "opcion": "Confirmar"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "SW", "quien_destraba": {"integrante": "Mariano Naim"}, "se_le_pregunta_a": {"a": "Mariano Naim", "llega": "2026-10-20T11:42:00-03:00"}, "aprendio_como_le_dicen_a": "Mariano Naim", "eligio": {"opcion": "O1", "etiqueta": "Confirmar"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 3591 ms
- Leda → Lucas:
  > 📋 Configurar el switch de la planta  
  > ✏️ Quedó anotado que Mariano puede destrabarla. Entendí que a él le decís «el chino».  
  > Hoy a las 11:42, Mariano será consultado sobre cuándo podrá hacerlo.
  >
  > Mientras siga trabada, no te voy a pedir avances.
  >
  > Avisame cuando se destrabe.
- [ ] dice: que el switch quedó trabado esperando que Mariano habilite el tablero
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Chino» o «el Tano» para nombrar a Mariano

**Paso 10.** Nahuel (2026-10-20 15:00): «la del plc ya no esta trabada por el plano, ahora me falta que el flaco me de acceso a la red»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta que el flaco me de acceso a la red"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "el flaco"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el plano del tablero"}, "estado": "en_curso", "ya_no_hace_falta_que_destraben": [{"aviso_a_quien_destrababa": {"a": "Mariano Naim", "llega": "2026-10-20T15:10:00-03:00"}}]}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta que el flaco me de acceso a la red", "pregunta_para_despues": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "el flaco", "coinciden": ["Marcos Tarquini", "Martín Forte"], "tarea": "PLC", "pregunta": "cual_de_esas_personas"}]`
- pregunta: `{"tipo": "cual_de_esas_personas", "tarea": "PLC", "como_lo_nombro": "el flaco", "opciones": [{"opcion": "O1", "etiqueta": "Marcos Tarquini"}, {"opcion": "O2", "etiqueta": "Martín Forte"}], "desde_antes": false}`
- latencia: 11858 ms
- Leda → Nahuel: [botones: Marcos Tarquini, Martín Forte]
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Quedó anotado que el plano del tablero ya no la traba.  
  > Mariano será avisado hoy a las 15:10 de que ya no hace falta que la destrabe.  
  > ✏️ Ahora está trabada porque te falta acceso a la red.  
  > No te voy a pedir avances mientras siga trabada.
  >
  > «El flaco» puede ser Marcos Tarquini o Martín Forte. Podés tocar una opción o responder escribiendo.
  >
  > ¿A cuál de los dos te referís?
- [ ] dice: la pregunta, con nombre y apellido de cada uno: si «el Flaco» es Martín Forte o Marcos Tarquini
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que lo destraba Martín o Marcos

**Paso 11.** Nahuel (2026-10-20 15:01): «[toca] Martín Forte»
- jugadas: `[{"nombre": "elegir", "opcion": "Martín Forte"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"integrante": "Martín Forte"}, "se_le_pregunta_a": {"a": "Martín Forte", "llega": "2026-10-20T15:11:00-03:00"}, "eligio": {"opcion": "O2", "etiqueta": "Martín Forte"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 2099 ms
- Leda → Nahuel:
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Quedó anotado que Martín puede destrabarla.  
  > Martín será consultado hoy a las 15:11 sobre cuándo podrá darte acceso a la red.  
  > No te voy a pedir avances mientras siga trabada.
  >
  > Cuando se destrabe, avisame.
- [ ] dice: que la del PLC quedó trabada esperando el acceso a la red de Martín
- [ ] dice: que le pregunta a Martín y le avisa apenas sepa algo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Flaco» para nombrar a Martín

## 47 · Los apodos · vez 3

Fuente: `tests/conversaciones/47-apodos.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M ok · F ok.

**Paso 1.** Nahuel (2026-10-20 10:00): «el plc esta trabado, me falta el plano del tablero y me lo tiene que pasar el tano»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el plano del tablero"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "el tano"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el plano del tablero", "pregunta_para_despues": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "el tano", "tarea": "PLC", "pregunta": "quien_es_esa_persona"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "el tano", "desde_antes": false}`
- latencia: 6871 ms
- Leda → Nahuel:
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Quedó anotado que está trabada porque te falta el plano del tablero.  
  > Mientras siga trabada, no te voy a pedir avances; retomo cuando me cuentes que se destrabó.
  >
  > ¿Quién es «el tano» que te tiene que pasar el plano?
- [ ] dice: que quedó anotado que el PLC está trabado por el plano del tablero
- [ ] dice: que no tiene a nadie en el equipo como "el Tano"
- [ ] dice: una sola pregunta: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que le va a preguntar a alguien
- [ ] no dice: un nombre de alguien del equipo como si fuera "el Tano"

**Paso 2.** Nahuel (2026-10-20 10:01): «mariano»
- jugadas: `[{"nombre": "decir_quien_es", "quien_es": "mariano"}]`
- hechos: `[{"jugada": "decir_quien_es", "resultado": "quien_es_para_confirmar", "como_lo_nombro": "el tano", "integrante": "Mariano Naim", "pregunta": "confirmar_quien_es_esa_persona"}]`
- pregunta: `{"tipo": "confirmar_quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "el tano", "integrante": "Mariano Naim", "opciones": [{"opcion": "O1", "etiqueta": "Confirmar"}], "desde_antes": false}`
- latencia: 6340 ms
- Leda → Nahuel: [botones: Confirmar]
  > 📋 Programar el PLC de la envasadora  
  > Antes de anotar quién te tiene que pasar el plano, necesito confirmar a quién llamás «el tano».
  >
  > Podés tocar Confirmar o responder escribiendo.
  >
  > ¿«El tano» es Mariano?
- [ ] dice: la confirmación con nombre y apellido: si «el Tano» es Mariano Naim
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que ya lo anotó o que le pregunta a Mariano

**Paso 3.** Nahuel (2026-10-20 10:02): «[toca] Confirmar»
- jugadas: `[{"nombre": "elegir", "opcion": "Confirmar"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"integrante": "Mariano Naim"}, "se_le_pregunta_a": {"a": "Mariano Naim", "llega": "2026-10-20T10:12:00-03:00"}, "aprendio_como_le_dicen_a": "Mariano Naim", "eligio": {"opcion": "O1", "etiqueta": "Confirmar"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 5836 ms
- Leda → Nahuel:
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Quedó anotado que Mariano puede destrabarla y que a él le decís «el tano».  
  > Mariano será consultado hoy a las 10:12 sobre cuándo podrá destrabarla.
  >
  > Cuando tengas el plano y se destrabe, avisame.
- [ ] dice: que el PLC quedó trabado esperando el plano de Mariano
- [ ] dice: que le pregunta a Mariano para cuándo y le avisa apenas sepa algo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Tano» para nombrar a Mariano

**Paso 4.** Leda (2026-10-20 10:12)
- Leda, por su cuenta (pregunta_a_quien_destraba PLC, 2026-10-20) → Mariano:
  > 📋 Programar el PLC de la envasadora  
  > Nahuel dijo que le falta el plano del tablero para avanzar.
  >
  > ¿Cuándo vas a poder pasárselo?
  - hechos: `{"aviso": "pregunta_a_quien_destraba", "causa": "me falta el plano del tablero", "tarea": "PLC", "pregunta": "cuando_se_destraba", "responsable": "Nahuel Gimenez", "necesita_respuesta": true}`
- [ ] dice: que Nahuel está trabado con el PLC porque le falta el plano del tablero
- [ ] dice: la pregunta: para cuándo se lo puede pasar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Tano»

**Paso 5.** Lucas (2026-10-20 11:00): «lo del rack esta trabado, el tano me tiene q pasar la medida del tablero»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "RACK", "causa": "el tano me tiene q pasar la medida del tablero"}, {"nombre": "anotar_quien_destraba", "tarea": "RACK", "quien": "el tano"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "RACK", "causa": "el tano me tiene q pasar la medida del tablero", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "RACK", "quien_destraba": {"integrante": "Mariano Naim"}, "se_le_pregunta_a": {"a": "Mariano Naim", "llega": "2026-10-20T11:10:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 5901 ms
- Leda → Lucas:
  > 📋 Armar el rack del servidor  
  > ✏️ Quedó anotado que está trabada porque Mariano tiene que pasarte la medida del tablero.  
  > Mariano será consultado hoy a las 11:10 sobre cuándo podrá pasártela.  
  > Mientras siga trabada, no te voy a pedir avances.
  >
  > Avisame cuando tengas la medida y puedas seguir.
- [ ] dice: que el rack quedó trabado esperando la medida del tablero de Mariano
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Tano» para nombrar a Mariano
- [ ] no dice: que no sabe quién es

**Paso 6.** Lucas (2026-10-20 11:30): «y lo del switch tambien, me falta que el chino me habilite el tablero»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "SW", "causa": "me falta que el chino me habilite el tablero"}, {"nombre": "anotar_quien_destraba", "tarea": "SW", "quien": "el chino"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "SW", "causa": "me falta que el chino me habilite el tablero", "pregunta_para_despues": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "el chino", "tarea": "SW", "pregunta": "quien_es_esa_persona"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "SW", "como_lo_nombro": "el chino", "desde_antes": false}`
- latencia: 7590 ms
- Leda → Lucas:
  > 📋 Configurar el switch de la planta  
  > ✏️ Quedó anotado que está trabada porque te falta que «el chino» te habilite el tablero.  
  > Mientras siga trabada, no te voy a pedir avances.
  >
  > ¿Quién es «el chino»?
- [ ] dice: que no tiene a nadie en el equipo como "el Chino"
- [ ] dice: una sola pregunta: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 7.** Lucas (2026-10-20 11:31): «mariano tambien»
- jugadas: `[{"nombre": "decir_quien_es", "quien_es": "Mariano"}]`
- hechos: `[{"jugada": "decir_quien_es", "resultado": "quien_es_para_confirmar", "como_lo_nombro": "el chino", "integrante": "Mariano Naim", "pregunta": "confirmar_quien_es_esa_persona"}]`
- pregunta: `{"tipo": "confirmar_quien_es_esa_persona", "tarea": "SW", "como_lo_nombro": "el chino", "integrante": "Mariano Naim", "opciones": [{"opcion": "O1", "etiqueta": "Confirmar"}], "desde_antes": false}`
- latencia: 8756 ms
- Leda → Lucas: [botones: Confirmar]
  > 📋 Configurar el switch de la planta  
  > Falta confirmar a quién llamás «el chino». Podés tocar Confirmar o responder por escrito.
  >
  > ¿«El chino» es Mariano?
- [ ] dice: la confirmación con nombre y apellido: si «el Chino» es Mariano Naim
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [comprension] jugadas: esperado [{'nombre': 'decir_quien_es', 'quien_es': 'mariano'}], real [{'nombre': 'decir_quien_es', 'quien_es': 'Mariano'}]

**Paso 8.** Lucas (2026-10-20 11:32): «[toca] Confirmar»
- jugadas: `[{"nombre": "elegir", "opcion": "Confirmar"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "SW", "quien_destraba": {"integrante": "Mariano Naim"}, "se_le_pregunta_a": {"a": "Mariano Naim", "llega": "2026-10-20T11:42:00-03:00"}, "aprendio_como_le_dicen_a": "Mariano Naim", "eligio": {"opcion": "O1", "etiqueta": "Confirmar"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 3072 ms
- Leda → Lucas:
  > 📋 Configurar el switch de la planta  
  > ✏️ Quedó anotado que Mariano puede destrabarla y que también le decís «el chino».  
  > Mariano será consultado hoy a las 11:42 sobre cuándo podrá habilitarte el tablero.  
  > Mientras siga trabada, no te voy a pedir avances.
  >
  > Avisame cuando te habilite el tablero y puedas seguir.
- [ ] dice: que el switch quedó trabado esperando que Mariano habilite el tablero
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Chino» o «el Tano» para nombrar a Mariano

**Paso 10.** Nahuel (2026-10-20 15:00): «la del plc ya no esta trabada por el plano, ahora me falta que el flaco me de acceso a la red»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta que el flaco me de acceso a la red"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "el flaco"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el plano del tablero"}, "estado": "en_curso", "ya_no_hace_falta_que_destraben": [{"aviso_a_quien_destrababa": {"a": "Mariano Naim", "llega": "2026-10-20T15:10:00-03:00"}}]}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta que el flaco me de acceso a la red", "pregunta_para_despues": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "el flaco", "coinciden": ["Marcos Tarquini", "Martín Forte"], "tarea": "PLC", "pregunta": "cual_de_esas_personas"}]`
- pregunta: `{"tipo": "cual_de_esas_personas", "tarea": "PLC", "como_lo_nombro": "el flaco", "opciones": [{"opcion": "O1", "etiqueta": "Marcos Tarquini"}, {"opcion": "O2", "etiqueta": "Martín Forte"}], "desde_antes": false}`
- latencia: 8023 ms
- Leda → Nahuel: [botones: Marcos Tarquini, Martín Forte]
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Quedó anotado que el plano ya no la traba y que ahora te falta que «el flaco» te dé acceso a la red.  
  > Mariano será avisado hoy a las 15:10 de que ya no hace falta que te pase el plano.  
  > Mientras siga trabada, no te voy a pedir avances.
  >
  > Podés elegir Marcos Tarquini o Martín Forte con los botones, o responder escribiendo.
  >
  > ¿A cuál de los dos le decís «el flaco»?
- [ ] dice: la pregunta, con nombre y apellido de cada uno: si «el Flaco» es Martín Forte o Marcos Tarquini
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que lo destraba Martín o Marcos

**Paso 11.** Nahuel (2026-10-20 15:01): «[toca] Martín Forte»
- jugadas: `[{"nombre": "elegir", "opcion": "Martín Forte"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"integrante": "Martín Forte"}, "se_le_pregunta_a": {"a": "Martín Forte", "llega": "2026-10-20T15:11:00-03:00"}, "eligio": {"opcion": "O2", "etiqueta": "Martín Forte"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 2805 ms
- Leda → Nahuel:
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Quedó anotado que Martín puede darte acceso a la red.  
  > Martín será consultado hoy a las 15:11 sobre cuándo podrá destrabarla.  
  > Mientras siga trabada, no te voy a pedir avances.
  >
  > Cuando tengas acceso y se destrabe, avisame.
- [ ] dice: que la del PLC quedó trabada esperando el acceso a la red de Martín
- [ ] dice: que le pregunta a Martín y le avisa apenas sepa algo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Flaco» para nombrar a Martín

## 47 · Los apodos · vez 4

Fuente: `tests/conversaciones/47-apodos.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Nahuel (2026-10-20 10:00): «el plc esta trabado, me falta el plano del tablero y me lo tiene que pasar el tano»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el plano del tablero"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "el tano"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el plano del tablero", "pregunta_para_despues": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "el tano", "tarea": "PLC", "pregunta": "quien_es_esa_persona"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "el tano", "desde_antes": false}`
- latencia: 8316 ms
- Leda → Nahuel:
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Quedó anotado que está trabada porque te falta el plano del tablero.  
  > No te voy a pedir avances mientras siga trabada; retomaré cuando me cuentes que se destrabó.
  >
  > ¿Quién es «el tano» que te tiene que pasar el plano?
- [ ] dice: que quedó anotado que el PLC está trabado por el plano del tablero
- [ ] dice: que no tiene a nadie en el equipo como "el Tano"
- [ ] dice: una sola pregunta: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que le va a preguntar a alguien
- [ ] no dice: un nombre de alguien del equipo como si fuera "el Tano"

**Paso 2.** Nahuel (2026-10-20 10:01): «mariano»
- jugadas: `[{"nombre": "decir_quien_es", "quien_es": "mariano"}]`
- hechos: `[{"jugada": "decir_quien_es", "resultado": "quien_es_para_confirmar", "como_lo_nombro": "el tano", "integrante": "Mariano Naim", "pregunta": "confirmar_quien_es_esa_persona"}]`
- pregunta: `{"tipo": "confirmar_quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "el tano", "integrante": "Mariano Naim", "opciones": [{"opcion": "O1", "etiqueta": "Confirmar"}], "desde_antes": false}`
- latencia: 8405 ms
- Leda → Nahuel: [botones: Confirmar]
  > 📋 Programar el PLC de la envasadora  
  > Todavía no quedó anotado quién te tiene que pasar el plano.  
  > Podés tocar Confirmar o responder por escrito.
  >
  > ¿Mariano es «el tano»?
- [ ] dice: la confirmación con nombre y apellido: si «el Tano» es Mariano Naim
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que ya lo anotó o que le pregunta a Mariano

**Paso 3.** Nahuel (2026-10-20 10:02): «[toca] Confirmar»
- jugadas: `[{"nombre": "elegir", "opcion": "Confirmar"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"integrante": "Mariano Naim"}, "se_le_pregunta_a": {"a": "Mariano Naim", "llega": "2026-10-20T10:12:00-03:00"}, "aprendio_como_le_dicen_a": "Mariano Naim", "eligio": {"opcion": "O1", "etiqueta": "Confirmar"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 9143 ms
- Leda → Nahuel:
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Quedó anotado que Mariano puede destrabarla. También voy a reconocerlo cuando le digas «el tano».  
  > Mariano será consultado hoy a las 10:12 sobre cuándo podrá destrabarla.
  >
  > No te voy a pedir avances mientras siga trabada.
  >
  > Avisame cuando se destrabe para retomar el seguimiento.
- [ ] dice: que el PLC quedó trabado esperando el plano de Mariano
- [ ] dice: que le pregunta a Mariano para cuándo y le avisa apenas sepa algo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Tano» para nombrar a Mariano

**Paso 4.** Leda (2026-10-20 10:12)
- Leda, por su cuenta (pregunta_a_quien_destraba PLC, 2026-10-20) → Mariano:
  > 📋 Programar el PLC de la envasadora  
  > Nahuel dijo que le falta el plano del tablero para avanzar.
  >
  > ¿Para cuándo podés resolver lo del plano?
  - hechos: `{"aviso": "pregunta_a_quien_destraba", "causa": "me falta el plano del tablero", "tarea": "PLC", "pregunta": "cuando_se_destraba", "responsable": "Nahuel Gimenez", "necesita_respuesta": true}`
- [ ] dice: que Nahuel está trabado con el PLC porque le falta el plano del tablero
- [ ] dice: la pregunta: para cuándo se lo puede pasar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Tano»

**Paso 5.** Lucas (2026-10-20 11:00): «lo del rack esta trabado, el tano me tiene q pasar la medida del tablero»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "RACK", "causa": "el tano me tiene q pasar la medida del tablero"}, {"nombre": "anotar_quien_destraba", "tarea": "RACK", "quien": "el tano"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "RACK", "causa": "el tano me tiene q pasar la medida del tablero", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "RACK", "quien_destraba": {"integrante": "Mariano Naim"}, "se_le_pregunta_a": {"a": "Mariano Naim", "llega": "2026-10-20T11:10:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 7434 ms
- Leda → Lucas:
  > 📋 Armar el rack del servidor  
  > ✏️ Quedó anotado que está trabada porque te falta la medida del tablero que tiene que pasarte Mariano.  
  > Mariano será consultado hoy a las 11:10 sobre cuándo puede destrabarla. Mientras siga trabada, no te voy a pedir avances.
  >
  > Avisame cuando se destrabe.
- [ ] dice: que el rack quedó trabado esperando la medida del tablero de Mariano
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Tano» para nombrar a Mariano
- [ ] no dice: que no sabe quién es

**Paso 6.** Lucas (2026-10-20 11:30): «y lo del switch tambien, me falta que el chino me habilite el tablero»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "SW", "causa": "me falta que el chino me habilite el tablero"}, {"nombre": "anotar_quien_destraba", "tarea": "SW", "quien": "el chino"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "SW", "causa": "me falta que el chino me habilite el tablero", "pregunta_para_despues": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "el chino", "tarea": "SW", "pregunta": "quien_es_esa_persona"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "SW", "como_lo_nombro": "el chino", "desde_antes": false}`
- latencia: 6931 ms
- Leda → Lucas:
  > 📋 Configurar el switch de la planta  
  > ✏️ Quedó anotado que está trabada porque te falta que “el chino” te habilite el tablero.  
  > Mientras siga trabada, no te voy a pedir avances.
  >
  > ⚠️ No sé quién es “el chino”, así que todavía no puedo anotar quién puede destrabarla.
  >
  > ¿Quién es “el chino”?
- [ ] dice: que no tiene a nadie en el equipo como "el Chino"
- [ ] dice: una sola pregunta: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 7.** Lucas (2026-10-20 11:31): «mariano tambien»
- jugadas: `[{"nombre": "decir_quien_es", "quien_es": "mariano"}]`
- hechos: `[{"jugada": "decir_quien_es", "resultado": "quien_es_para_confirmar", "como_lo_nombro": "el chino", "integrante": "Mariano Naim", "pregunta": "confirmar_quien_es_esa_persona"}]`
- pregunta: `{"tipo": "confirmar_quien_es_esa_persona", "tarea": "SW", "como_lo_nombro": "el chino", "integrante": "Mariano Naim", "opciones": [{"opcion": "O1", "etiqueta": "Confirmar"}], "desde_antes": false}`
- latencia: 10235 ms
- Leda → Lucas: [botones: Confirmar]
  > 📋 Configurar el switch de la planta  
  > Entendí que “el chino” es Mariano. Todavía no anoté que él puede destrabarla.
  >
  > Podés tocar Confirmar o responder por escrito.
  >
  > ¿“El chino” es Mariano?
- [ ] dice: la confirmación con nombre y apellido: si «el Chino» es Mariano Naim
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 8.** Lucas (2026-10-20 11:32): «[toca] Confirmar»
- jugadas: `[{"nombre": "elegir", "opcion": "Confirmar"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "SW", "quien_destraba": {"integrante": "Mariano Naim"}, "se_le_pregunta_a": {"a": "Mariano Naim", "llega": "2026-10-20T11:42:00-03:00"}, "aprendio_como_le_dicen_a": "Mariano Naim", "eligio": {"opcion": "O1", "etiqueta": "Confirmar"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 4218 ms
- Leda → Lucas:
  > 📋 Configurar el switch de la planta  
  > ✏️ Quedó anotado que Mariano puede destrabarla. Ya sé que le decís “el chino”.  
  > Mariano será consultado hoy a las 11:42 sobre cuándo puede destrabarla. Mientras siga trabada, no te voy a pedir avances.
  >
  > Avisame cuando se destrabe.
- [ ] dice: que el switch quedó trabado esperando que Mariano habilite el tablero
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Chino» o «el Tano» para nombrar a Mariano

**Paso 10.** Nahuel (2026-10-20 15:00): «la del plc ya no esta trabada por el plano, ahora me falta que el flaco me de acceso a la red»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta que el flaco me de acceso a la red"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "el flaco"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el plano del tablero"}, "estado": "en_curso", "ya_no_hace_falta_que_destraben": [{"aviso_a_quien_destrababa": {"a": "Mariano Naim", "llega": "2026-10-20T15:10:00-03:00"}}]}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta que el flaco me de acceso a la red", "pregunta_para_despues": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "el flaco", "coinciden": ["Marcos Tarquini", "Martín Forte"], "tarea": "PLC", "pregunta": "cual_de_esas_personas"}]`
- pregunta: `{"tipo": "cual_de_esas_personas", "tarea": "PLC", "como_lo_nombro": "el flaco", "opciones": [{"opcion": "O1", "etiqueta": "Marcos Tarquini"}, {"opcion": "O2", "etiqueta": "Martín Forte"}], "desde_antes": false}`
- latencia: 9236 ms
- Leda → Nahuel: [botones: Marcos Tarquini, Martín Forte]
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Quedó anotado que ya no está trabada por el plano, pero ahora te falta que «el flaco» te dé acceso a la red.  
  > Mariano será avisado hoy a las 15:10 de que ya no hace falta que destrabe lo del plano.  
  > No te pediré avances mientras siga trabada.
  >
  > Podés elegir Marcos Tarquini o Martín Forte tocando la opción o escribiendo.
  >
  > ¿A cuál de los dos le decís «el flaco»?
- [ ] dice: la pregunta, con nombre y apellido de cada uno: si «el Flaco» es Martín Forte o Marcos Tarquini
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que lo destraba Martín o Marcos

**Paso 11.** Nahuel (2026-10-20 15:01): «[toca] Martín Forte»
- jugadas: `[{"nombre": "elegir", "opcion": "Martín Forte"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"integrante": "Martín Forte"}, "se_le_pregunta_a": {"a": "Martín Forte", "llega": "2026-10-20T15:11:00-03:00"}, "eligio": {"opcion": "O2", "etiqueta": "Martín Forte"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 3500 ms
- Leda → Nahuel:
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Quedó anotado que Martín puede destrabar lo del acceso a la red.  
  > Martín será consultado hoy a las 15:11 sobre cuándo podrá destrabarla.  
  > No te pediré avances mientras siga trabada.
  >
  > Avisame cuando tengas acceso a la red para retomar el seguimiento.
- [ ] dice: que la del PLC quedó trabada esperando el acceso a la red de Martín
- [ ] dice: que le pregunta a Martín y le avisa apenas sepa algo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Flaco» para nombrar a Martín

## 47 · Los apodos · vez 5

Fuente: `tests/conversaciones/47-apodos.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Nahuel (2026-10-20 10:00): «el plc esta trabado, me falta el plano del tablero y me lo tiene que pasar el tano»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el plano del tablero"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "el tano"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el plano del tablero", "pregunta_para_despues": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "el tano", "tarea": "PLC", "pregunta": "quien_es_esa_persona"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "el tano", "desde_antes": false}`
- latencia: 5494 ms
- Leda → Nahuel:
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Anoté que está trabada porque te falta el plano del tablero.  
  > No te voy a pedir avances mientras siga trabada; retomo cuando me cuentes que se destrabó.
  >
  > ¿Quién es “el tano”?
- [ ] dice: que quedó anotado que el PLC está trabado por el plano del tablero
- [ ] dice: que no tiene a nadie en el equipo como "el Tano"
- [ ] dice: una sola pregunta: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que le va a preguntar a alguien
- [ ] no dice: un nombre de alguien del equipo como si fuera "el Tano"

**Paso 2.** Nahuel (2026-10-20 10:01): «mariano»
- jugadas: `[{"nombre": "decir_quien_es", "quien_es": "mariano"}]`
- hechos: `[{"jugada": "decir_quien_es", "resultado": "quien_es_para_confirmar", "como_lo_nombro": "el tano", "integrante": "Mariano Naim", "pregunta": "confirmar_quien_es_esa_persona"}]`
- pregunta: `{"tipo": "confirmar_quien_es_esa_persona", "tarea": "PLC", "como_lo_nombro": "el tano", "integrante": "Mariano Naim", "opciones": [{"opcion": "O1", "etiqueta": "Confirmar"}], "desde_antes": false}`
- latencia: 6581 ms
- Leda → Nahuel: [botones: Confirmar]
  > 📋 Programar el PLC de la envasadora  
  > Podés tocar Confirmar o responder escribiendo.
  >
  > ¿“El tano” es Mariano Naim?
- [ ] dice: la confirmación con nombre y apellido: si «el Tano» es Mariano Naim
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que ya lo anotó o que le pregunta a Mariano

**Paso 3.** Nahuel (2026-10-20 10:02): «[toca] Confirmar»
- jugadas: `[{"nombre": "elegir", "opcion": "Confirmar"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"integrante": "Mariano Naim"}, "se_le_pregunta_a": {"a": "Mariano Naim", "llega": "2026-10-20T10:12:00-03:00"}, "aprendio_como_le_dicen_a": "Mariano Naim", "eligio": {"opcion": "O1", "etiqueta": "Confirmar"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 5623 ms
- Leda → Nahuel:
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Anoté que Mariano puede destrabarla. Ya sé que también le decís «el tano».  
  > Mariano será consultado hoy a las 10:12 sobre cuándo puede destrabarla.
  >
  > Cuando se destrabe, contame y retomo el seguimiento.
- [ ] dice: que el PLC quedó trabado esperando el plano de Mariano
- [ ] dice: que le pregunta a Mariano para cuándo y le avisa apenas sepa algo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Tano» para nombrar a Mariano

**Paso 4.** Leda (2026-10-20 10:12)
- Leda, por su cuenta (pregunta_a_quien_destraba PLC, 2026-10-20) → Mariano:
  > 📋 Programar el PLC de la envasadora  
  > Nahuel dice que le falta el plano del tablero para avanzar.
  >
  > ¿Para cuándo podés resolver lo del plano?
  - hechos: `{"aviso": "pregunta_a_quien_destraba", "causa": "me falta el plano del tablero", "tarea": "PLC", "pregunta": "cuando_se_destraba", "responsable": "Nahuel Gimenez", "necesita_respuesta": true}`
- [ ] dice: que Nahuel está trabado con el PLC porque le falta el plano del tablero
- [ ] dice: la pregunta: para cuándo se lo puede pasar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Tano»

**Paso 5.** Lucas (2026-10-20 11:00): «lo del rack esta trabado, el tano me tiene q pasar la medida del tablero»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "RACK", "causa": "me tiene q pasar la medida del tablero"}, {"nombre": "anotar_quien_destraba", "tarea": "RACK", "quien": "el tano"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "RACK", "causa": "me tiene q pasar la medida del tablero", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "RACK", "quien_destraba": {"integrante": "Mariano Naim"}, "se_le_pregunta_a": {"a": "Mariano Naim", "llega": "2026-10-20T11:10:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 10639 ms
- Leda → Lucas:
  > 📋 Armar el rack del servidor  
  > ✏️ Quedó anotado que está trabada porque te falta la medida del tablero y que Mariano puede destrabarla.  
  > Mariano será consultado hoy a las 11:10 para saber cuándo puede destrabarla.
  >
  > Mientras siga trabada, no te voy a pedir avances.
  >
  > Cuando se destrabe, avisame para retomar el seguimiento.
- [ ] dice: que el rack quedó trabado esperando la medida del tablero de Mariano
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Tano» para nombrar a Mariano
- [ ] no dice: que no sabe quién es

**Paso 6.** Lucas (2026-10-20 11:30): «y lo del switch tambien, me falta que el chino me habilite el tablero»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "SW", "causa": "me falta que el chino me habilite el tablero"}, {"nombre": "anotar_quien_destraba", "tarea": "SW", "quien": "el chino"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "SW", "causa": "me falta que el chino me habilite el tablero", "pregunta_para_despues": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "el chino", "tarea": "SW", "pregunta": "quien_es_esa_persona"}]`
- pregunta: `{"tipo": "quien_es_esa_persona", "tarea": "SW", "como_lo_nombro": "el chino", "desde_antes": false}`
- latencia: 6537 ms
- Leda → Lucas:
  > 📋 Configurar el switch de la planta  
  > ✏️ Quedó anotado que está trabada porque te falta que «el chino» te habilite el tablero.  
  > Mientras siga trabada, no te voy a pedir avances.
  >
  > ¿Quién es «el chino»?
- [ ] dice: que no tiene a nadie en el equipo como "el Chino"
- [ ] dice: una sola pregunta: quién es
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 7.** Lucas (2026-10-20 11:31): «mariano tambien»
- jugadas: `[{"nombre": "decir_quien_es", "quien_es": "mariano"}]`
- hechos: `[{"jugada": "decir_quien_es", "resultado": "quien_es_para_confirmar", "como_lo_nombro": "el chino", "integrante": "Mariano Naim", "pregunta": "confirmar_quien_es_esa_persona"}]`
- pregunta: `{"tipo": "confirmar_quien_es_esa_persona", "tarea": "SW", "como_lo_nombro": "el chino", "integrante": "Mariano Naim", "opciones": [{"opcion": "O1", "etiqueta": "Confirmar"}], "desde_antes": false}`
- latencia: 9455 ms
- Leda → Lucas: [botones: Confirmar]
  > 📋 Configurar el switch de la planta  
  > Antes de anotar quién puede destrabarla, necesito confirmar a quién te referís con «el chino».
  >
  > Podés tocar Confirmar o responder por escrito.
  >
  > ¿«El chino» es Mariano?
- [ ] dice: la confirmación con nombre y apellido: si «el Chino» es Mariano Naim
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 8.** Lucas (2026-10-20 11:32): «[toca] Confirmar»
- jugadas: `[{"nombre": "elegir", "opcion": "Confirmar"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "SW", "quien_destraba": {"integrante": "Mariano Naim"}, "se_le_pregunta_a": {"a": "Mariano Naim", "llega": "2026-10-20T11:42:00-03:00"}, "aprendio_como_le_dicen_a": "Mariano Naim", "eligio": {"opcion": "O1", "etiqueta": "Confirmar"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 4789 ms
- Leda → Lucas:
  > 📋 Configurar el switch de la planta  
  > ✏️ Quedó anotado que Mariano puede destrabarla. También voy a reconocerlo cuando le digas «el chino».  
  > Mariano será consultado hoy a las 11:42 para saber cuándo puede destrabarla.  
  > Mientras siga trabada, no te voy a pedir avances.
  >
  > Cuando se destrabe, avisame para retomar el seguimiento.
- [ ] dice: que el switch quedó trabado esperando que Mariano habilite el tablero
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Chino» o «el Tano» para nombrar a Mariano

**Paso 10.** Nahuel (2026-10-20 15:00): «la del plc ya no esta trabada por el plano, ahora me falta que el flaco me de acceso a la red»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta que el flaco me de acceso a la red"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "el flaco"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el plano del tablero"}, "estado": "en_curso", "ya_no_hace_falta_que_destraben": [{"aviso_a_quien_destrababa": {"a": "Mariano Naim", "llega": "2026-10-20T15:10:00-03:00"}}]}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta que el flaco me de acceso a la red", "pregunta_para_despues": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_es"], "como_lo_nombro": "el flaco", "coinciden": ["Marcos Tarquini", "Martín Forte"], "tarea": "PLC", "pregunta": "cual_de_esas_personas"}]`
- pregunta: `{"tipo": "cual_de_esas_personas", "tarea": "PLC", "como_lo_nombro": "el flaco", "opciones": [{"opcion": "O1", "etiqueta": "Marcos Tarquini"}, {"opcion": "O2", "etiqueta": "Martín Forte"}], "desde_antes": false}`
- latencia: 10033 ms
- Leda → Nahuel: [botones: Marcos Tarquini, Martín Forte]
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Anoté que el plano ya no la traba y que ahora te falta acceso a la red.  
  > Mariano será avisado hoy a las 15:10 de que ya no hace falta que destrabe lo del plano.  
  > No te voy a pedir avances mientras siga trabada.
  >
  > Podés tocar Marcos Tarquini o Martín Forte, o responder escribiendo.
  >
  > ¿A cuál de los dos te referís con «el flaco»?
- [ ] dice: la pregunta, con nombre y apellido de cada uno: si «el Flaco» es Martín Forte o Marcos Tarquini
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que lo destraba Martín o Marcos

**Paso 11.** Nahuel (2026-10-20 15:01): «[toca] Martín Forte»
- jugadas: `[{"nombre": "elegir", "opcion": "Martín Forte"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"integrante": "Martín Forte"}, "se_le_pregunta_a": {"a": "Martín Forte", "llega": "2026-10-20T15:11:00-03:00"}, "eligio": {"opcion": "O2", "etiqueta": "Martín Forte"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 3276 ms
- Leda → Nahuel:
  > 📋 Programar el PLC de la envasadora  
  > ✏️ Anoté que Martín puede destrabar lo del acceso a la red.  
  > Martín será consultado hoy a las 15:11 sobre cuándo puede destrabarla.  
  > No te voy a pedir avances mientras siga trabada.
  >
  > Cuando se destrabe, contame y retomo el seguimiento.
- [ ] dice: que la del PLC quedó trabada esperando el acceso a la red de Martín
- [ ] dice: que le pregunta a Martín y le avisa apenas sepa algo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: «el Flaco» para nombrar a Martín

