# Transcripciones de la ronda sin-puntuacion-25

Para leer contra lo que cada paso dice y no dice (decisión 10.3). Cada casilla la marca quien lee.

## 25 · Mensajes sin puntuación · vez 1

Fuente: `tests/conversaciones/25-sin-puntuacion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G FALLA · C FALLA · M FALLA · F FALLA.

**Paso 1.** Leda (2026-10-19 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-19) → Marcos:
  > Estas tareas vencen el jue 22/10:
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
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones", "pregunta": "quien_destraba"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:40:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 11513 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que te falta el cable para programar comunicaciones y que estimás terminarla el vie 23/10.  
  > ⚠️ Vence el jue 22/10: si la terminás el vie 23/10, tendrá un día hábil de atraso. La revisión de comunicaciones depende de esta tarea.
  >
  > Ismael será notificado hoy a las 10:40. Mientras siga trabada, no te voy a pedir avances; retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede conseguir el cable para destrabarla?
- [ ] dice: cada tarea en su bloque, primero su renglón con 📋 y su nombre solo y debajo, con ✏️, lo anotado: la del PLC está trabada porque le falta el cable para programar; la de comunicaciones la termina el vie 23/10
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, un día hábil de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: una sola pregunta, sola y en el último renglón: quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una causa del bloqueo que nombre las comunicaciones
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: negrita
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones'}, {'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real [{'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:dc1e8900-f309-4cbd-9c75-7d853997f19a', 'outbox_id': None}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:40:00-03:00'}, 'lo_que_sigue': {'seguimiento': 'detenido_mientras_siga_trabada'}}]
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real 'Ismael será notificado hoy a las 10:40. Mientras siga trabada, no te voy a pedir avances; retomaré el seguimiento cuando me cuentes que se destrabó.'

**Paso 3.** Leda (2026-10-19 10:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-19) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el vie 23/10 porque le falta el cable para programar comunicaciones. Vence el jue 22/10.  
  > ⚠️ Si la termina ese día, tendrá 1 día hábil de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": "me falta el cable para programar comunicaciones", "prevision": "2026-10-23", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 1}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el vie 23/10, sin motivo
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: un día hábil
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado (el cable, el PLC)
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'motivo': 'ausente'}}, real [{'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['PLC'], 'el': '2026-10-19', 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['PLC'], 'el': '2026-10-19', 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}}

**Paso 4.** Marcos (2026-10-19 10:50): «el cable lo consigue martin de compras y comunicaciones al final es el lunes 26 xq me falta el switch tmb»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de compras"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-26", "motivo": "me falta el switch tmb"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-26", "motivo": "me falta el switch tmb", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:50:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-26"}}}]`
- latencia: 10840 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que Martín, de Compras, puede conseguir el cable.  
  > Mientras siga trabada, no te voy a pedir avances; retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que estimás terminarla el lun 26/10 porque también te falta el switch.  
  > ⚠️ Vence el jue 22/10. Si la terminás el lun 26/10, tendrá dos días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:50.
  >
  > Te voy a preguntar cómo viene la revisión el lun 26/10.
- [ ] dice: cada tarea en su bloque con 📋 primero: en la del PLC, con ✏️, que Martín de compras consigue el cable; en la de comunicaciones, con ✏️, que la termina el lun 26/10 porque le falta el switch
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, dos días hábiles de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: el switch como causa del bloqueo del PLC
- [ ] no dice: Martín en la tarea de comunicaciones
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién destraba la del PLC

**Paso 5.** Leda (2026-10-19 10:51)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el lun 26/10 porque también le falta el switch. Vence el jue 22/10.  
  > ⚠️ Si la termina ese día, tendrá 2 días hábiles de atraso.
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

**Paso 6.** Marcos (2026-10-20 15:00): «ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "entregar", "tarea": "COM"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el cable para programar comunicaciones"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "COM", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 8020 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que llegó el cable, que ya podés seguir y que estás trabajando en el PLC.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Entiendo que decís que la terminaste, pero todavía no puedo recibir la entrega por chat y no hay otra forma definida para hacerlo.
  >
  > Te voy a preguntar cómo viene el PLC el vie 23/10.
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que quedó anotado que se destrabó y sigue en curso
- [ ] dice: en el bloque de la de comunicaciones: con honestidad, que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: que la tarea de comunicaciones quedó entregada, en revisión o terminada
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: que la del PLC está terminada
- [ ] no dice: otra vez la pregunta de quién lo destraba

## 25 · Mensajes sin puntuación · vez 2

Fuente: `tests/conversaciones/25-sin-puntuacion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G FALLA · C FALLA · M FALLA · F FALLA.

**Paso 1.** Leda (2026-10-19 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-19) → Marcos:
  > Estas dos tareas vencen el jue 22/10:
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
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones", "pregunta": "quien_destraba"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:40:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 11209 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que te falta el cable para programar comunicaciones y que estimás terminarla el vie 23/10.  
  > ⚠️ Vence el jue 22/10: si la terminás el viernes, tendrá un día hábil de atraso. La revisión de comunicaciones depende de esta tarea.
  >
  > Ismael será notificado hoy a las 10:40. Mientras siga trabada, no te voy a pedir novedades; retomo el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede conseguir el cable para destrabarla?
- [ ] dice: cada tarea en su bloque, primero su renglón con 📋 y su nombre solo y debajo, con ✏️, lo anotado: la del PLC está trabada porque le falta el cable para programar; la de comunicaciones la termina el vie 23/10
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, un día hábil de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: una sola pregunta, sola y en el último renglón: quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una causa del bloqueo que nombre las comunicaciones
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: negrita
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones'}, {'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real [{'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:3ec5a605-0fa7-4c65-9e52-380cbccef851', 'outbox_id': None}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:40:00-03:00'}, 'lo_que_sigue': {'seguimiento': 'detenido_mientras_siga_trabada'}}]
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real 'Ismael será notificado hoy a las 10:40. Mientras siga trabada, no te voy a pedir novedades; retomo el seguimiento cuando me cuentes que se destrabó.'

**Paso 3.** Leda (2026-10-19 10:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-19) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el vie 23/10 porque le falta el cable para programar comunicaciones. Vence el jue 22/10.  
  > ⚠️ Si la termina ese día, tendrá un día hábil de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Depende de la programación del PLC.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": "me falta el cable para programar comunicaciones", "prevision": "2026-10-23", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 1}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el vie 23/10, sin motivo
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: un día hábil
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado (el cable, el PLC)
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'motivo': 'ausente'}}, real [{'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['PLC'], 'el': '2026-10-19', 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['PLC'], 'el': '2026-10-19', 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}}

**Paso 4.** Marcos (2026-10-19 10:50): «el cable lo consigue martin de compras y comunicaciones al final es el lunes 26 xq me falta el switch tmb»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de compras"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-26", "motivo": "me falta el switch tmb"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-26", "motivo": "me falta el switch tmb", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:50:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-26"}}}]`
- latencia: 10026 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que Martín de Compras puede conseguir el cable. Mientras siga trabada, no te voy a pedir novedades; contame cuando se destrabe.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que estimás terminarla el lun 26/10 porque también te falta el switch.  
  > ⚠️ Vence el jue 22/10. Si la terminás el lunes, tendrá dos días hábiles de atraso.
  >
  > Ismael será notificado hoy a las 10:50.
  >
  > El lun 26/10 te voy a preguntar cómo viene la revisión.
- [ ] dice: cada tarea en su bloque con 📋 primero: en la del PLC, con ✏️, que Martín de compras consigue el cable; en la de comunicaciones, con ✏️, que la termina el lun 26/10 porque le falta el switch
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, dos días hábiles de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: el switch como causa del bloqueo del PLC
- [ ] no dice: Martín en la tarea de comunicaciones
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién destraba la del PLC
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '✏️ Quedó anotado que Martín de Compras puede conseguir el cable. Mientras siga trabada, no te voy a pedir novedades; contame cuando se destrabe.'

**Paso 5.** Leda (2026-10-19 10:51)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el lun 26/10 porque también le falta el switch. Vence el jue 22/10.  
  > ⚠️ Si la termina ese día, tendrá dos días hábiles de atraso.
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

**Paso 6.** Marcos (2026-10-20 15:00): «ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "informar_avance", "tarea": "PLC", "palabras": "sigo con el plc"}, {"nombre": "entregar", "tarea": "COM"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el cable para programar comunicaciones"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "informar_avance", "resultado": "no_se_puede", "motivo": "nadie_pidio_el_estado", "tarea": "PLC"}, {"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "COM", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 11547 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que llegó el cable y que la tarea ya no está trabada por eso. Sigue en curso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Entiendo que la terminaste, pero todavía no puedo recibir la entrega por chat. No hay otra forma definida por ahora.
  >
  > El vie 23/10 te voy a preguntar cómo viene el PLC.
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que quedó anotado que se destrabó y sigue en curso
- [ ] dice: en el bloque de la de comunicaciones: con honestidad, que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: que la tarea de comunicaciones quedó entregada, en revisión o terminada
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: que la del PLC está terminada
- [ ] no dice: otra vez la pregunta de quién lo destraba
- **falla** [comprension] jugadas: esperado [{'nombre': 'destrabar', 'tarea': 'PLC'}, {'nombre': 'entregar', 'tarea': 'COM'}], real [{'nombre': 'destrabar', 'tarea': 'PLC'}, {'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'sigo con el plc'}, {'nombre': 'entregar', 'tarea': 'COM'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'estado': 'en_curso', 'vuelve_a_pedir_el_estado': 'ausente', 'pregunta': 'ausente'}, {'jugada': 'entregar', 'resultado': 'no_por_chat', 'tarea': 'COM'}], real [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'bloqueo_resuelto': {'causa': 'me falta el cable para programar comunicaciones'}, 'estado': 'en_curso', 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-23'}}}, {'jugada': 'informar_avance', 'resultado': 'no_se_puede', 'motivo': 'nadie_pidio_el_estado', 'tarea': 'PLC'}, {'jugada': 'entregar', 'resultado': 'no_por_chat', 'motivo': 'la_entrega_todavia_no_se_recibe_por_chat', 'tarea': 'COM', 'otra_forma_de_hacerlo': 'ninguna_definida'}]

## 25 · Mensajes sin puntuación · vez 3

Fuente: `tests/conversaciones/25-sin-puntuacion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G FALLA · C FALLA · M FALLA · F FALLA.

**Paso 1.** Leda (2026-10-19 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-19) → Marcos:
  > Estas dos tareas vencen el jue 22/10, dentro de 3 días hábiles:
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
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones", "pregunta": "quien_destraba"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:40:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 10570 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que te falta el cable para programar comunicaciones y que estimás terminarla el vie 23/10.  
  > ⚠️ Vence el jue 22/10: si la terminás el viernes, será un día hábil después. La revisión de comunicaciones de la comprimidora depende de esta tarea.
  >
  > Ismael será notificado hoy a las 10:40. Mientras siga trabada, no te voy a pedir el estado.
  >
  > ¿Quién puede destrabarla?
- [ ] dice: cada tarea en su bloque, primero su renglón con 📋 y su nombre solo y debajo, con ✏️, lo anotado: la del PLC está trabada porque le falta el cable para programar; la de comunicaciones la termina el vie 23/10
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, un día hábil de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: una sola pregunta, sola y en el último renglón: quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una causa del bloqueo que nombre las comunicaciones
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: negrita
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones'}, {'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real [{'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:4f173685-86fc-44bc-97a6-ed20afd690c1', 'outbox_id': None}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:40:00-03:00'}, 'lo_que_sigue': {'seguimiento': 'detenido_mientras_siga_trabada'}}]
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Vence el jue 22/10: si la terminás el viernes, será un día hábil después. La revisión de comunicaciones de la comprimidora depende de esta tarea.'

**Paso 3.** Leda (2026-10-19 10:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-19) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el vie 23/10 porque le falta el cable para programar comunicaciones. Vence el jue 22/10.  
  > ⚠️ Si la termina ese día, tendrá un día hábil de atraso. La revisión de comunicaciones depende de esta tarea.
  >
  > No hace falta que respondas.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": "me falta el cable para programar comunicaciones", "prevision": "2026-10-23", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 1}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el vie 23/10, sin motivo
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: un día hábil
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado (el cable, el PLC)
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'motivo': 'ausente'}}, real [{'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['PLC'], 'el': '2026-10-19', 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['PLC'], 'el': '2026-10-19', 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}}

**Paso 4.** Marcos (2026-10-19 10:50): «el cable lo consigue martin de compras y comunicaciones al final es el lunes 26 xq me falta el switch tmb»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de compras"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-26", "motivo": "me falta el switch tmb"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-26", "motivo": "me falta el switch tmb", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:50:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-26"}}}]`
- latencia: 7917 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que Martín de compras puede conseguir el cable. Mientras siga trabada, no te voy a pedir el estado.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que estimás terminarla el lun 26/10 porque también te falta el switch.  
  > ⚠️ Vence el jue 22/10. Si la terminás el lunes, serán dos días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:50.
  >
  > El lun 26/10 te voy a preguntar cómo viene la revisión.
- [ ] dice: cada tarea en su bloque con 📋 primero: en la del PLC, con ✏️, que Martín de compras consigue el cable; en la de comunicaciones, con ✏️, que la termina el lun 26/10 porque le falta el switch
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, dos días hábiles de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: el switch como causa del bloqueo del PLC
- [ ] no dice: Martín en la tarea de comunicaciones
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién destraba la del PLC

**Paso 5.** Leda (2026-10-19 10:51)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el lun 26/10 porque le falta el switch. Vence el jue 22/10.  
  > ⚠️ Si la termina ese día, tendrá dos días hábiles de atraso.
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

**Paso 6.** Marcos (2026-10-20 15:00): «ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "entregar", "tarea": "COM"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el cable para programar comunicaciones"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "COM", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 7999 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que llegó el cable y que ya podés seguir con el PLC.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Entiendo que decís que la terminaste. Todavía no puedo recibir la entrega por chat y no tengo otra forma definida para hacerlo.
  >
  > El vie 23/10 te voy a preguntar cómo viene el PLC.
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que quedó anotado que se destrabó y sigue en curso
- [ ] dice: en el bloque de la de comunicaciones: con honestidad, que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: que la tarea de comunicaciones quedó entregada, en revisión o terminada
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: que la del PLC está terminada
- [ ] no dice: otra vez la pregunta de quién lo destraba

## 25 · Mensajes sin puntuación · vez 4

Fuente: `tests/conversaciones/25-sin-puntuacion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G FALLA · C FALLA · M FALLA · F FALLA.

**Paso 1.** Leda (2026-10-19 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-19) → Marcos:
  > Estas dos tareas vencen el jue 22/10:
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
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones", "pregunta": "quien_destraba"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:40:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 12823 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que te falta el cable para programar comunicaciones y que estimás terminarla el vie 23/10. Vence el jue 22/10.  
  > ⚠️ Si la terminás el vie 23/10, tendrá un día hábil de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.
  >
  > Ismael será notificado hoy a las 10:40 sobre el bloqueo y tu estimación. Mientras siga trabada, no te voy a pedir el estado; retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede conseguir el cable para destrabarla?
- [ ] dice: cada tarea en su bloque, primero su renglón con 📋 y su nombre solo y debajo, con ✏️, lo anotado: la del PLC está trabada porque le falta el cable para programar; la de comunicaciones la termina el vie 23/10
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, un día hábil de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: una sola pregunta, sola y en el último renglón: quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una causa del bloqueo que nombre las comunicaciones
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: negrita
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones'}, {'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real [{'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:35f85314-e31e-4dbf-9d07-864a02071a1b', 'outbox_id': None}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:40:00-03:00'}, 'lo_que_sigue': {'seguimiento': 'detenido_mientras_siga_trabada'}}]
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás el vie 23/10, tendrá un día hábil de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.'

**Paso 3.** Leda (2026-10-19 10:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-19) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el vie 23/10 porque le falta el cable para programar comunicaciones. Vence el jue 22/10.  
  > ⚠️ Si la termina el día que dijo, tendrá un día hábil de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": "me falta el cable para programar comunicaciones", "prevision": "2026-10-23", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 1}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el vie 23/10, sin motivo
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: un día hábil
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado (el cable, el PLC)
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'motivo': 'ausente'}}, real [{'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['PLC'], 'el': '2026-10-19', 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['PLC'], 'el': '2026-10-19', 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}}
- **falla** [formato] formato del mensaje a Ismael: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la termina el día que dijo, tendrá un día hábil de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.'

**Paso 4.** Marcos (2026-10-19 10:50): «el cable lo consigue martin de compras y comunicaciones al final es el lunes 26 xq me falta el switch tmb»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de compras"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-26", "motivo": "me falta el switch tmb"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-26", "motivo": "me falta el switch tmb", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:50:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-26"}}}]`
- latencia: 7035 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que Martín, de compras, puede conseguir el cable. Mientras siga trabada, no te voy a pedir el estado.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que estimás terminarla el lun 26/10 porque también te falta el switch. Vence el jue 22/10.  
  > ⚠️ Si la terminás el lun 26/10, tendrá dos días hábiles de atraso.
  >
  > Ismael será notificado hoy a las 10:50 sobre la nueva estimación. El lun 26/10 te voy a preguntar cómo viene la revisión de comunicaciones.
- [ ] dice: cada tarea en su bloque con 📋 primero: en la del PLC, con ✏️, que Martín de compras consigue el cable; en la de comunicaciones, con ✏️, que la termina el lun 26/10 porque le falta el switch
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, dos días hábiles de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: el switch como causa del bloqueo del PLC
- [ ] no dice: Martín en la tarea de comunicaciones
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién destraba la del PLC

**Paso 5.** Leda (2026-10-19 10:51)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el lun 26/10 porque le falta el switch. Vence el jue 22/10.  
  > ⚠️ Si la termina ese día, tendrá dos días hábiles de atraso.
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

**Paso 6.** Marcos (2026-10-20 15:00): «ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "entregar", "tarea": "COM"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el cable para programar comunicaciones"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "COM", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 6676 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que llegó el cable y que la tarea ya no está trabada por eso. Seguís con el PLC.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Entiendo que la terminaste recién. Todavía no puedo recibir la entrega por este chat y no tengo otra forma definida para hacerlo.
  >
  > El vie 23/10 te voy a preguntar cómo viene el PLC.
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que quedó anotado que se destrabó y sigue en curso
- [ ] dice: en el bloque de la de comunicaciones: con honestidad, que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: que la tarea de comunicaciones quedó entregada, en revisión o terminada
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: que la del PLC está terminada
- [ ] no dice: otra vez la pregunta de quién lo destraba

## 25 · Mensajes sin puntuación · vez 5

Fuente: `tests/conversaciones/25-sin-puntuacion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G FALLA · C FALLA · M FALLA · F FALLA.

**Paso 1.** Leda (2026-10-19 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-19) → Marcos:
  > Estas dos tareas vencen el jue 22/10, dentro de tres días hábiles:  
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
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones", "pregunta": "quien_destraba"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:40:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 10636 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que te falta el cable para programar comunicaciones y que estimás terminarla el vie 23/10.  
  > ⚠️ Vence el jue 22/10: si la terminás el viernes, tendrá un día hábil de atraso. La revisión de comunicaciones depende de esta tarea.
  >
  > Ismael será notificado hoy a las 10:40. Mientras siga trabada, no te voy a pedir el estado; retomo el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede conseguir el cable para destrabarla?
- [ ] dice: cada tarea en su bloque, primero su renglón con 📋 y su nombre solo y debajo, con ✏️, lo anotado: la del PLC está trabada porque le falta el cable para programar; la de comunicaciones la termina el vie 23/10
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, un día hábil de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: una sola pregunta, sola y en el último renglón: quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una causa del bloqueo que nombre las comunicaciones
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: negrita
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones'}, {'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real [{'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:9f7f2a66-206a-46ce-afb4-606ff3e00dbd', 'outbox_id': None}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:40:00-03:00'}, 'lo_que_sigue': {'seguimiento': 'detenido_mientras_siga_trabada'}}]
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real 'Ismael será notificado hoy a las 10:40. Mientras siga trabada, no te voy a pedir el estado; retomo el seguimiento cuando me cuentes que se destrabó.'

**Paso 3.** Leda (2026-10-19 10:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-19) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el vie 23/10 porque le falta el cable para programar comunicaciones.  
  > Vence el jue 22/10.  
  > ⚠️ Si la termina ese día, tendrá un día hábil de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Esta tarea depende de la programación del PLC.
  >
  > No hace falta que respondas.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": "me falta el cable para programar comunicaciones", "prevision": "2026-10-23", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 1}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el vie 23/10, sin motivo
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: un día hábil
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado (el cable, el PLC)
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'motivo': 'ausente'}}, real [{'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['PLC'], 'el': '2026-10-19', 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['PLC'], 'el': '2026-10-19', 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}}

**Paso 4.** Marcos (2026-10-19 10:50): «el cable lo consigue martin de compras y comunicaciones al final es el lunes 26 xq me falta el switch tmb»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de compras"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-26", "motivo": "me falta el switch tmb"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-26", "motivo": "me falta el switch tmb", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:50:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-26"}}}]`
- latencia: 9392 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que Martín de compras puede conseguir el cable.  
  > Mientras siga trabada, no te voy a pedir el estado.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que estimás terminarla el lun 26/10 porque también te falta el switch.  
  > ⚠️ Vence el jue 22/10: si la terminás el lunes, tendrá dos días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:50. El lun 26/10 te voy a preguntar cómo viene.
  >
  > Avisame cuando se destrabe el PLC.
- [ ] dice: cada tarea en su bloque con 📋 primero: en la del PLC, con ✏️, que Martín de compras consigue el cable; en la de comunicaciones, con ✏️, que la termina el lun 26/10 porque le falta el switch
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, dos días hábiles de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: el switch como causa del bloqueo del PLC
- [ ] no dice: Martín en la tarea de comunicaciones
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién destraba la del PLC

**Paso 5.** Leda (2026-10-19 10:51)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el lun 26/10 porque también le falta el switch.  
  > Vence el jue 22/10.  
  > ⚠️ Si la termina ese día, tendrá dos días hábiles de atraso.
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

**Paso 6.** Marcos (2026-10-20 15:00): «ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "entregar", "tarea": "COM"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el cable para programar comunicaciones"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "COM", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 7626 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que llegó el cable: la tarea ya no está trabada por eso y seguís con el PLC.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Entiendo que la terminaste recién, pero todavía no puedo recibir la entrega por chat. Por ahora no tengo otra forma indicada para hacerlo.
  >
  > El vie 23/10 te voy a preguntar cómo viene el PLC.
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que quedó anotado que se destrabó y sigue en curso
- [ ] dice: en el bloque de la de comunicaciones: con honestidad, que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: que la tarea de comunicaciones quedó entregada, en revisión o terminada
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: que la del PLC está terminada
- [ ] no dice: otra vez la pregunta de quién lo destraba

