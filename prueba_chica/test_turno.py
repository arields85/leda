"""Un turno del motor de conversación y su registro (E2-2).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Un turno" y "Fallas de la IA"); ADR 0018,
decisiones 1, 3 y 8 (caso 1). Acá se prueba el esqueleto con
manejadores de prueba; las fichas de la E2-3, en `test_fichas.py`. La IA es guionada.
"""

from __future__ import annotations

from prueba_chica.conftest import AHORA
from prueba_chica.fichas import JUGADAS
from prueba_chica.ia import IAGuionada, Jugada
from prueba_chica.tiempo import RelojFijo
from prueba_chica.turno import TEXTO_SI_LA_IA_FALLA, procesar_turno

from leda.db import admin
from leda.incidentes import ETAPA_TURNO_CONVERSACION, NOTICIA_NEUTRA_INCIDENTE


def _turnos(conn, membership_id: str) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("""select sentido, inbound_message_id, outbox_id, jugadas, resultado,
                              ia, latencia_ms, error, at
                         from conversation_turn where membership_id = %s
                        order by sentido""", (membership_id,))
        return cur.fetchall()


def _salidas(conn) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("""select id, cuerpo, es_respuesta, destinatario_membership_id,
                              programado_para, entrante_id
                         from message_outbox order by programado_para""")
        return cur.fetchall()


def _incidentes(conn) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("""select etapa, severidad, referencia_tipo, referencia_id, app_user_id
                         from incident""")
        return cur.fetchall()


def test_un_turno_lee_pide_jugadas_redacta_encola_y_registra(conn, mundo, escribe):
    quien, entrante = escribe("Marcos", "arranqué")
    ia = IAGuionada(jugadas=[[]], redacciones=["Hola, Marcos."])

    resultado = procesar_turno(conn, quien, entrante, ia, RelojFijo(AHORA))
    conn.commit()

    assert resultado.texto == "Hola, Marcos." and resultado.error is None
    # (1) la IA recibe lo leído: el mensaje, hoy y las tareas de la persona con su alias.
    situacion = ia.pedidos_de_jugadas[0]
    assert situacion["mensaje"] == "arranqué"
    assert situacion["hoy"] == "2026-10-05"
    assert [(t["alias"], t["titulo"]) for t in situacion["tareas"]] == [
        ("T1", "Revisar el tablero")]
    assert situacion["jugadas_posibles"] == sorted(JUGADAS)
    # (5) la IA redacta desde los hechos.
    assert ia.pedidos_de_redaccion[0]["hechos"] == []

    [salida] = _salidas(conn)
    assert salida["cuerpo"] == "Hola, Marcos."
    assert salida["es_respuesta"] is True
    assert str(salida["destinatario_membership_id"]) == quien.membership_id
    assert str(salida["entrante_id"]) == entrante
    assert salida["programado_para"] == AHORA

    entrada, sale = _turnos(conn, quien.membership_id)
    assert entrada["sentido"] == "entrada" and str(entrada["inbound_message_id"]) == entrante
    assert entrada["jugadas"] == [] and entrada["resultado"] == {"hechos": []}
    assert entrada["ia"] == "guionada" and entrada["error"] is None
    assert entrada["latencia_ms"] == 0
    # Los momentos los pone el motor con su reloj, nunca la base.
    assert entrada["at"] == AHORA and sale["at"] == AHORA
    assert sale["sentido"] == "salida" and sale["outbox_id"] == salida["id"]


def test_los_turnos_anteriores_llegan_a_la_ia(conn, mundo, escribe):
    quien, primero = escribe("Marcos", "hola")
    procesar_turno(conn, quien, primero, IAGuionada(jugadas=[[]], redacciones=["Buen día."]),
                   RelojFijo(AHORA))
    conn.commit()
    _, segundo = escribe("Marcos", "arranqué")
    ia = IAGuionada(jugadas=[[]], redacciones=["Bien."])

    procesar_turno(conn, quien, segundo, ia, RelojFijo(AHORA))

    assert [(t["sentido"], t["texto"]) for t in ia.pedidos_de_jugadas[0]["ultimos_turnos"]] == [
        ("entrada", "hola"), ("salida", "Buen día.")]


def test_una_jugada_de_la_lista_la_maneja_su_manejador(conn, mundo, escribe):
    quien, entrante = escribe("Marcos", "arranqué")
    vistos = []

    def probar(contexto, jugada):
        vistos.append(contexto.tarea(jugada.datos["tarea"])["id"])
        return {"jugada": jugada.nombre, "resultado": "hecho"}

    ia = IAGuionada(jugadas=[[Jugada("probar", {"tarea": "T1"})]], redacciones=["Listo."])
    resultado = procesar_turno(conn, quien, entrante, ia, RelojFijo(AHORA),
                               jugadas={"probar": probar})

    assert vistos == [mundo["tarea"]]
    assert resultado.hechos == [{"jugada": "probar", "resultado": "hecho"}]
    assert ia.pedidos_de_jugadas[0]["jugadas_posibles"] == ["probar"]


def test_si_la_ia_falla_una_vez_el_turno_sigue(conn, mundo, escribe):
    quien, entrante = escribe("Marcos", "arranqué")
    ia = IAGuionada(jugadas=[ConnectionError("sin red"), []],
                    redacciones=["", "Anotado."])     # una redacción vacía es no responder

    resultado = procesar_turno(conn, quien, entrante, ia, RelojFijo(AHORA))
    conn.commit()

    assert resultado.texto == "Anotado." and resultado.error is None
    assert len(ia.pedidos_de_jugadas) == 2 and len(ia.pedidos_de_redaccion) == 2
    assert [s["cuerpo"] for s in _salidas(conn)] == ["Anotado."]
    assert _incidentes(conn) == []


def test_si_la_ia_falla_dos_veces_nada_se_ejecuta_y_sale_el_texto_fijo(conn, mundo, escribe):
    quien, entrante = escribe("Marcos", "arranqué")
    llamado = []
    ia = IAGuionada(jugadas=[ConnectionError("sin red"), TimeoutError("tarde")])

    resultado = procesar_turno(conn, quien, entrante, ia, RelojFijo(AHORA),
                               jugadas={"probar": lambda c, j: llamado.append(j)})
    conn.commit()

    # Un reintento, enseguida; sin IA no hay jugada ni redacción.
    assert len(ia.pedidos_de_jugadas) == 2 and ia.pedidos_de_redaccion == []
    assert llamado == [] and resultado.jugadas == []
    # El único texto fijo, el de la constitución §10.
    assert TEXTO_SI_LA_IA_FALLA == NOTICIA_NEUTRA_INCIDENTE
    assert resultado.texto == TEXTO_SI_LA_IA_FALLA
    [salida] = _salidas(conn)
    assert salida["cuerpo"] == TEXTO_SI_LA_IA_FALLA and salida["es_respuesta"] is True
    # Un incidente para el administrador, que apunta al mensaje.
    [incidente] = _incidentes(conn)
    assert incidente["etapa"] == ETAPA_TURNO_CONVERSACION
    assert incidente["referencia_tipo"] == "inbound_message"
    assert str(incidente["referencia_id"]) == entrante
    assert str(incidente["app_user_id"]) == quien.app_user_id
    # El turno queda registrado, con su error.
    entrada, sale = _turnos(conn, quien.membership_id)
    assert str(entrada["inbound_message_id"]) == entrante
    assert entrada["error"] == "ia_no_respondio: TimeoutError"
    assert entrada["jugadas"] is None and entrada["resultado"] is None
    assert entrada["at"] == AHORA
    assert sale["outbox_id"] == salida["id"] and sale["ia"] is None


def test_si_la_redaccion_falla_dos_veces_se_deshace_lo_ejecutado(conn, mundo, escribe):
    quien, entrante = escribe("Marcos", "arranqué")

    def anota(contexto, jugada):
        contexto.cur.execute(
            """insert into conversation_question (workspace_id, membership_id, tipo,
                                                  se_puede_dejar, abierta_en)
               values (%s, %s, 'prueba', true, %s)""",
            (contexto.quien.workspace_id, contexto.quien.membership_id, contexto.ahora))
        return {"jugada": jugada.nombre, "resultado": "hecho"}

    ia = IAGuionada(jugadas=[[Jugada("anota", {})]],
                    redacciones=[RuntimeError("caída"), RuntimeError("caída")])
    resultado = procesar_turno(conn, quien, entrante, ia, RelojFijo(AHORA),
                               jugadas={"anota": anota})
    conn.commit()

    assert resultado.texto == TEXTO_SI_LA_IA_FALLA
    assert resultado.error == "ia_no_respondio: RuntimeError"
    with admin(conn) as cur:
        cur.execute("select count(*) n from conversation_question")
        assert cur.fetchone()["n"] == 0
    assert [s["cuerpo"] for s in _salidas(conn)] == [TEXTO_SI_LA_IA_FALLA]
    assert len(_incidentes(conn)) == 1
    entrada, _ = _turnos(conn, quien.membership_id)
    # Lo que la IA eligió queda en el registro aunque no se haya ejecutado.
    assert entrada["jugadas"] == [{"nombre": "anota", "datos": {}}]
    assert entrada["resultado"] is None


def test_un_mensaje_procesado_dos_veces_corre_sus_jugadas_una_sola_vez(conn, mundo, escribe):
    """Revisión de la E2-2: si el mismo mensaje entra dos veces al turno (un reintento del
    escuchador, dos procesos), la segunda no pide jugadas, no ejecuta y no responde."""
    quien, entrante = escribe("Marcos", "arranqué")
    llamadas = []

    def anota(contexto, jugada):
        llamadas.append(jugada.nombre)
        return {"jugada": jugada.nombre, "resultado": "hecho"}

    primera = IAGuionada(jugadas=[[Jugada("anota", {})]], redacciones=["Anotado."])
    procesar_turno(conn, quien, entrante, primera, RelojFijo(AHORA), jugadas={"anota": anota})
    conn.commit()
    segunda = IAGuionada(jugadas=[[Jugada("anota", {})]], redacciones=["Anotado otra vez."])

    resultado = procesar_turno(conn, quien, entrante, segunda, RelojFijo(AHORA),
                               jugadas={"anota": anota})
    conn.commit()

    assert resultado.repetido is True and resultado.jugadas == [] and resultado.hechos == []
    assert llamadas == ["anota"]
    assert segunda.pedidos_de_jugadas == [] and segunda.pedidos_de_redaccion == []
    assert [s["cuerpo"] for s in _salidas(conn)] == ["Anotado."]
    assert [t["sentido"] for t in _turnos(conn, quien.membership_id)] == ["entrada", "salida"]


def test_los_turnos_llegan_a_la_ia_en_orden_aunque_tengan_la_misma_hora(conn, mundo, escribe):
    """Revisión de la E2-2: con el reloj fijo todos los turnos tienen la misma hora; el
    orden en que se registraron decide, no el sentido."""
    quien, _ = escribe("Marcos", "-")
    for texto, respuesta in (("hola", "Buen día."), ("arranqué", "Anotado.")):
        _, entrante = escribe("Marcos", texto)
        procesar_turno(conn, quien, entrante, IAGuionada(jugadas=[[]], redacciones=[respuesta]),
                       RelojFijo(AHORA))
        conn.commit()
    _, tercero = escribe("Marcos", "¿y ahora?")
    ia = IAGuionada(jugadas=[[]], redacciones=["Bien."])

    procesar_turno(conn, quien, tercero, ia, RelojFijo(AHORA))

    assert [(t["sentido"], t["texto"]) for t in ia.pedidos_de_jugadas[0]["ultimos_turnos"]] == [
        ("entrada", "hola"), ("salida", "Buen día."),
        ("entrada", "arranqué"), ("salida", "Anotado.")]
