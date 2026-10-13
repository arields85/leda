"""Un ícono por estado en las listas de tareas (decisión 79 del usuario, 2026-10-12, "muy bueno,
me gusta"; constitución §4 y §8; `odd/tasks/correcciones-prueba-telegram.md`, T1).

Con un solo ícono para todas hay que leer para saber cómo va; con uno por estado, "todo verde" ya
es la buena noticia. El verde sólo dice lo que Leda sabe:

- 🏁 terminada;
- 🟢 en curso y al día (sin un pedido de estado sin contestar, sin un día dado después del
  vencimiento y sin haber vencido);
- ⚪ sin empezar, o sin novedades porque la persona no contó cómo viene;
- 🔵 entregada, esperando la revisión;
- 🟠 atrasada (en el informe al grupo, sólo la ya hablada en privado, como lo decide el informe);
- 🔴 trabada.

Los pone la cocina, no la IA (regla del mozo; decisión 74: la cocina ya da la forma del mensaje):
de los hechos que ella misma armó sabe el estado de cada tarea de una lista
(`hechos.iconos_de_las_listas`) y cambia la marca del renglón de cada una, que reconoce por su
título completo (`salida.iconos_por_estado`). Una lista es de dos tareas o más: el 📋 de un
mensaje sobre una sola tarea no cambia.

El reloj es el de `test_escalera.py`: "Revisar el tablero" (T1) de Marcos vence el viernes 9 de
octubre de 2026; el lunes 12 es feriado.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from leda import salida
from leda.db import admin
from leda.motor import hechos as hechos_mod
from leda.motor.ia import IAGuionada, Jugada
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import procesar_turno

from tests.motor.ayudantes import nueva_tarea, octubre, todos

T1 = "Revisar el tablero"
T2, T3, T4, T5 = ("Probar las comunicaciones", "Instalar el panel", "Cablear la línea 2",
                  "Cambiar el motor")
GRUPO = -100_500

TERMINADA, AL_DIA, SIN_NOVEDADES, ENTREGADA, ATRASADA, TRABADA = "🏁", "🟢", "⚪", "🔵", "🟠", "🔴"


# --- La forma: la marca del renglón de cada tarea ---------------------------------------------

def test_la_marca_de_cada_tarea_de_la_lista_es_la_de_su_estado():
    texto = (f"Así vienen tus tareas:\n🗓️ {T1}, vence vie 9/10\n🗓 {T2}: en curso, vie 30/10\n"
             f"\n¿Cómo vienen?")

    assert salida.iconos_por_estado(texto, {T1: SIN_NOVEDADES, T2: AL_DIA}) == (
        f"Así vienen tus tareas:\n⚪ {T1}, vence vie 9/10\n🟢 {T2}: en curso, vie 30/10\n"
        f"\n¿Cómo vienen?")


def test_cambia_cualquier_marca_de_tarea_o_vineta_y_conserva_el_resto_del_renglon():
    texto = f"📋 {T1}\n• {T2} (Marcos)\n- {T3} (Marcos)\n  📅 {T4}, lun 19/10"
    iconos = {T1: TERMINADA, T2: ENTREGADA, T3: TRABADA, T4: ATRASADA}

    assert salida.iconos_por_estado(texto, iconos) == (
        f"🏁 {T1}\n🔵 {T2} (Marcos)\n🔴 {T3} (Marcos)\n  🟠 {T4}, lun 19/10")


def test_reconoce_el_titulo_sin_importar_mayusculas_y_el_mas_largo_primero():
    largo = f"{T1} 2"
    texto = f"🗓️ {T1.lower()}, vie 9/10\n🗓️ {largo}, vie 16/10"

    assert salida.iconos_por_estado(texto, {T1: AL_DIA, largo: TRABADA}) == (
        f"🟢 {T1.lower()}, vie 9/10\n🔴 {largo}, vie 16/10")


def test_un_renglon_sin_marca_de_tarea_o_sin_una_tarea_de_la_lista_no_cambia():
    texto = (f"Quedó anotado lo de {T1}.\n✏️ {T2}: la arrancaste hoy.\n🗓️ Otra tarea, vie 9/10\n"
             f"⚠️ {T3} espera a otra.")

    assert salida.iconos_por_estado(texto, {T1: AL_DIA, T2: AL_DIA, T3: TRABADA}) == texto


def test_dos_veces_da_lo_mismo_que_una_y_un_estado_nuevo_reemplaza_al_anterior():
    texto = f"🗓️ {T1}\n🗓️ {T2}"
    una = salida.iconos_por_estado(texto, {T1: AL_DIA, T2: SIN_NOVEDADES})

    assert salida.iconos_por_estado(una, {T1: AL_DIA, T2: SIN_NOVEDADES}) == una
    assert salida.iconos_por_estado(una, {T1: ATRASADA, T2: SIN_NOVEDADES}) == (
        f"🟠 {T1}\n⚪ {T2}")
    assert salida.iconos_por_estado(texto, {}) == texto


def test_el_renglon_de_una_tarea_con_su_estado_nunca_se_parte():
    """La forma del mensaje (decisión 74) no parte el renglón de una tarea: tampoco con el ícono
    de su estado."""
    renglon = (f"🟠 {T1} (Marcos): vencía el vie 9/10. La termina el mié 14/10. "
               f"Falta que llegue el cable de programación que pidió al proveedor nuevo.")
    assert len(renglon) > salida.RENGLON_MAXIMO
    texto = f"Así vienen:\n{renglon}\n🟢 {T2} (Marcos)\n\nNo hace falta responder."

    assert salida.dar_forma(texto) == texto


# --- El estado de cada tarea, de los hechos de la cocina ---------------------------------------

def _pedido(*hechos: dict, hoy: str = "2026-10-13") -> dict:
    return {"hoy": hoy, "hechos": list(hechos)}


def test_el_informe_al_grupo_da_el_estado_de_cada_lista():
    informe = {"aviso": "informe_al_grupo", "necesita_respuesta": False,
               "terminadas": [{"tarea": T1, "la_tiene": "Marcos"}],
               "atrasadas": [{"tarea": T2, "la_tiene": "Marcos", "vence": "2026-10-09"}],
               "trabadas": [{"tarea": T3, "la_tiene": "Marcos", "causas": ["el cable"]}],
               "entregadas": [{"tarea": T4, "la_tiene": "Lucas"}],
               "sin_saber_como_vienen": [{"tarea": T5, "la_tiene": "Lucas"}],
               "siguen": [{"tarea": "Medir", "la_tiene": "Lucas", "estado": "en_curso",
                           "vence": "2026-10-23"},
                          {"tarea": "Pintar", "la_tiene": "Lucas", "estado": "asignada",
                           "vence": "2026-10-23"}]}

    assert hechos_mod.iconos_de_las_listas(_pedido(informe)) == {
        T1: TERMINADA, T2: ATRASADA, T3: TRABADA, T4: ENTREGADA, T5: SIN_NOVEDADES,
        "Medir": AL_DIA, "Pintar": SIN_NOVEDADES}


def test_la_lista_de_la_persona_da_verde_solo_a_lo_que_leda_sabe_que_va_bien():
    """En la lista de la cadencia: en curso y al día, verde; vencida o con un día dado después del
    vencimiento, atrasada; sin contestar lo que Leda preguntó, sin novedades; la entregada, aunque
    haya vencido, entregada."""
    filas = [
        {"tarea": "al dia", "estado": "en_curso", "vence": "2026-10-16"},
        {"tarea": "vence hoy", "estado": "en_curso", "vence": "2026-10-13", "vence_hoy": True},
        {"tarea": "antes", "estado": "en_curso", "vence": "2026-10-16",
         "prevision_vigente": {"fecha": "2026-10-14"}},
        {"tarea": "sin empezar", "estado": "asignada", "vence": "2026-10-16"},
        {"tarea": "vencida", "estado": "en_curso", "vence": "2026-10-09",
         "atraso_dias_habiles": 1},
        {"tarea": "despues", "estado": "en_curso", "vence": "2026-10-16",
         "prevision_vigente": {"fecha": "2026-10-20"}},
        {"tarea": "sin contestar", "estado": "en_curso", "vence": "2026-10-16",
         "sin_respuesta_desde": "2026-10-09"},
        {"tarea": "trabada", "estado": "bloqueada", "vence": "2026-10-16", "causas": ["x"]},
        {"tarea": "entregada", "estado": "en_revision", "vence": "2026-10-09"},
        {"tarea": "sin vencimiento", "estado": "en_curso"}]
    lista = {"aviso": "como_vienen_sus_tareas", "necesita_respuesta": True, "sus_tareas": filas}

    assert hechos_mod.iconos_de_las_listas(_pedido(lista)) == {
        "al dia": AL_DIA, "vence hoy": AL_DIA, "antes": AL_DIA, "sin empezar": SIN_NOVEDADES,
        "vencida": ATRASADA, "despues": ATRASADA, "sin contestar": SIN_NOVEDADES,
        "trabada": TRABADA, "entregada": ENTREGADA, "sin vencimiento": AL_DIA}


def test_lo_que_tiene_pendiente_y_la_lista_de_entregas_tambien_son_listas():
    pendientes = {"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [
        {"alias": "T1", "titulo": T1, "estado": "asignada", "vence": "2026-10-09"},
        {"alias": "T2", "titulo": T2, "estado": "en_curso", "vence": "2026-10-23"}]}
    entregas = [{"aviso": "lista_de_entregas_para_revisar", "cuantas": 2},
                {"aviso": "entrega_en_la_lista", "tarea": T3, "fotos_que_trae": 0},
                {"aviso": "entrega_en_la_lista", "tarea": T4, "fotos_que_trae": 1}]

    assert hechos_mod.iconos_de_las_listas(_pedido(pendientes)) == {T1: ATRASADA, T2: AL_DIA}
    assert hechos_mod.iconos_de_las_listas(_pedido(*entregas)) == {T3: ENTREGADA,
                                                                   T4: ENTREGADA}


def test_los_avisos_de_varias_tareas_en_un_mensaje_son_una_lista():
    previo = {"aviso": "aviso_previo", "necesita_respuesta": False, "tarea": T1,
              "vence": "2026-10-16", "estado": "asignada", "dias_habiles_hasta_el_vencimiento": 3}
    pedido = {"aviso": "pedido_de_estado", "necesita_respuesta": True, "tarea": T2,
              "vence": "2026-10-13", "estado": "en_curso"}
    vencida = {"aviso": "repregunta_de_estado", "tarea": T3, "vence": "2026-10-09",
               "estado": "en_curso", "atraso_dias_habiles": 2}

    assert hechos_mod.iconos_de_las_listas(_pedido(previo, pedido, vencida)) == {
        T1: SIN_NOVEDADES, T2: AL_DIA, T3: ATRASADA}


def test_un_mensaje_sobre_una_sola_tarea_no_es_una_lista():
    una = {"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [
        {"alias": "T1", "titulo": T1, "estado": "en_curso", "vence": "2026-10-23"}]}
    inicio = {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": T1}
    aviso = {"aviso": "pedido_de_estado", "tarea": T1, "estado": "en_curso",
             "vence": "2026-10-13"}

    for pedido in (_pedido(una), _pedido(inicio, aviso), _pedido()):
        assert hechos_mod.iconos_de_las_listas(pedido) == {}


# --- De punta a punta: lo que sale -------------------------------------------------------------

@dataclass
class IAQueNombra:
    """Una IA que escribe cada tarea que traen los hechos en su renglón con 🗓️, como lo pide el
    formato de los mensajes en una lista; la marca del estado la pone la cocina."""

    titulos: tuple[str, ...]
    nombre: str = "guionada"
    pedidos_de_redaccion: list[dict[str, Any]] = field(default_factory=list)

    def redactar(self, pedido: dict[str, Any], al_avanzar=None) -> str:
        self.pedidos_de_redaccion.append(pedido)
        vistos = json.dumps(pedido["hechos"], ensure_ascii=False)
        renglones = [f"🗓️ {t}" for t in self.titulos if f'"{t}"' in vistos]
        return "\n".join(["Así vienen las tareas:", *renglones, "", "No hace falta responder."])

    def elegir_jugadas(self, situacion):
        raise AssertionError("Lo que Leda manda por su cuenta no elige jugadas.")


def _estado(conn, mundo, titulo: str, estado: str, at, *, vence=None,
            bloqueo: str | None = None) -> str:
    """Otra tarea de Marcos en ese estado desde `at` (como `test_informe_al_grupo._estado`)."""
    with admin(conn) as cur:
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, estado, fecha_objetivo,
                                 criterio_aceptacion)
               values (%s, %s, %s, %s, %s, 'asignada', %s, 'Queda hecho y probado')
               returning id""",
            (mundo["id"], mundo["objetivo"], titulo, mundo["area"],
             mundo["personas"]["Marcos"]["membership_id"], vence or octubre(30, 17)))
        tarea = str(cur.fetchone()["id"])
        if bloqueo:
            cur.execute("""insert into blocker (workspace_id, task_id, causa, abierto_en,
                                                abierto_por)
                           values (%s, %s, %s, %s, %s)""",
                        (mundo["id"], tarea, bloqueo, at,
                         mundo["personas"]["Marcos"]["membership_id"]))
        if estado == "terminada":
            cur.execute("""insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                                 aprobador_membership_id, decision)
                           values (%s, 'tarea', %s, %s, 'aprobado')""",
                        (mundo["id"], tarea, mundo["personas"]["Ismael"]["membership_id"]))
        if estado != "asignada":
            cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                         actor_kind, motivo, at)
                           values (%s, 'asignada', %s, 'sistema', 'estado inicial de la prueba',
                                   %s)""", (tarea, estado, at))
    conn.commit()
    return tarea


def _cadencia(conn, mundo, cron: str, audiencia: str) -> None:
    with admin(conn) as cur:
        if audiencia == "grupo":
            cur.execute("update workspace set grupo_chat_id = %s where id = %s",
                        (GRUPO, mundo["id"]))
        cur.execute("""insert into cadence_job (workspace_id, nombre, cron, audiencia,
                                                plantilla_clave)
                       values (%s, 'cadencia', %s, %s, 'cadencia')""", (mundo["id"], cron,
                                                                         audiencia))
    conn.commit()


def test_el_informe_al_grupo_sale_con_el_icono_del_estado_de_cada_tarea(conn, mundo, dias):
    _cadencia(conn, mundo, "15 16 * * 5", "grupo")
    _estado(conn, mundo, T2, "terminada", octubre(7, 11))
    _estado(conn, mundo, T3, "en_revision", octubre(8, 11))
    _estado(conn, mundo, T4, "bloqueada", octubre(6, 10), bloqueo="esperando el repuesto")
    _estado(conn, mundo, T5, "en_curso", octubre(5, 10), vence=octubre(23, 17))
    dias.ia = IAQueNombra((T1, T2, T3, T4, T5))

    dias.ciclo(octubre(9, 16, 15))

    [fila] = todos(conn, "select cuerpo from message_outbox where chat_id = %s", GRUPO)
    assert fila["cuerpo"].split("\n") == [
        "Así vienen las tareas:", f"⚪ {T1}", f"🏁 {T2}", f"🔵 {T3}", f"🔴 {T4}", f"🟢 {T5}",
        "", "No hace falta responder."]


def test_la_lista_de_la_cadencia_no_da_verde_a_lo_que_la_persona_no_contesto(conn, mundo, dias):
    """La lista del lunes 5 le pregunta a Marcos cómo vienen sus tareas y no contesta. La primera
    lista de la otra semana (el lunes 19; el 12 es feriado) trae todas otra vez: la que está en
    curso y no vence no es verde, porque Leda no sabe cómo viene; la que venció, atrasada."""
    _cadencia(conn, mundo, "15 9 * * 1", "privado_cada_integrante")
    nueva_tarea(conn, mundo, T2, estado="en_curso", fecha=octubre(30, 17))
    dias.ciclo(octubre(5, 10))
    dias.ia = IAQueNombra((T1, T2))

    [lista] = [h for p in dias.ciclo(octubre(19, 10)) for h in p["hechos"]
               if h.get("aviso") == "como_vienen_sus_tareas"]

    [_, de_t2] = lista["sus_tareas"]
    assert de_t2["sin_respuesta_desde"] == "2026-10-05"
    assert hechos_mod.sin_significado(lista) == set()
    salio = todos(conn, """select cuerpo from message_outbox
                            where chat_id = %s and cuerpo like %s
                            order by programado_para desc limit 1""",
                  mundo["personas"]["Marcos"]["telegram"], f"%{T2}%")[0]["cuerpo"]
    assert f"🟠 {T1}" in salio.split("\n") and f"⚪ {T2}" in salio.split("\n")


def _pendientes(conn, escribe, at) -> Any:
    quien, entrante = escribe("Marcos", "que tengo pendiente?", at=at)
    ia = IAGuionada(jugadas=[[Jugada("consultar_pendientes")]], redacciones=[
        f"Tenés estas:\n🗓️ {T1}, vie 9/10\n🗓️ {T2}, vie 30/10\n🗓️ {T3}, vie 30/10\n\n"
        f"Avisame si algo cambió."])
    resultado = procesar_turno(conn, quien, entrante, ia, RelojFijo(at))
    conn.commit()
    assert resultado.error is None
    return resultado


def test_lo_que_tiene_pendiente_sale_con_el_icono_del_estado_de_cada_tarea(conn, mundo,
                                                                          escribe):
    """El martes 13 el tablero ya venció (atrasada); las comunicaciones siguen en curso y al día;
    el panel está trabado."""
    nueva_tarea(conn, mundo, T2, estado="en_curso", fecha=octubre(30, 17))
    _estado(conn, mundo, T3, "bloqueada", octubre(6, 10), bloqueo="esperando el repuesto",
            vence=octubre(30, 17))

    resultado = _pendientes(conn, escribe, octubre(13, 10))

    assert resultado.texto.split("\n")[1:4] == [f"🟠 {T1}, vie 9/10", f"🟢 {T2}, vie 30/10",
                                                f"🔴 {T3}, vie 30/10"]
    [fila] = todos(conn, "select cuerpo from message_outbox where es_respuesta")
    assert fila["cuerpo"] == resultado.texto


def test_lo_que_tiene_pendiente_dice_el_dia_que_dio_y_lo_que_no_contesto(conn, mundo, escribe,
                                                                        dias):
    """Lo que hace falta para no darle verde a lo que Leda no sabe sale de la cocina, con los
    datos de siempre: el día que dio la persona, si es otro que el vencimiento, y desde cuándo no
    contestó lo que Leda le preguntó. La lista del lunes 5 le preguntó por el tablero y las
    comunicaciones y no contestó; el martes 6 pregunta qué tiene pendiente."""
    _cadencia(conn, mundo, "15 9 * * 1", "privado_cada_integrante")
    nueva_tarea(conn, mundo, T2, estado="en_curso", fecha=octubre(30, 17))
    dias.ciclo(octubre(5, 10))
    nueva_tarea(conn, mundo, T3, estado="en_curso", fecha=octubre(30, 17))

    resultado = _pendientes(conn, escribe, octubre(6, 10))

    [hecho] = resultado.hechos[:1]
    por_titulo = {t["titulo"]: t for t in hecho["tareas"]}
    assert por_titulo[T1]["sin_respuesta_desde"] == "2026-10-05"
    assert por_titulo[T2]["sin_respuesta_desde"] == "2026-10-05"
    assert "sin_respuesta_desde" not in por_titulo[T3]
    assert hechos_mod.sin_significado(hecho) == set()
    assert resultado.texto.split("\n")[1:4] == [f"⚪ {T1}, vie 9/10", f"⚪ {T2}, vie 30/10",
                                                f"🟢 {T3}, vie 30/10"]


def test_un_dia_dado_despues_del_vencimiento_es_un_atraso_en_lo_que_tiene_pendiente(
        conn, mundo, escribe):
    nueva_tarea(conn, mundo, T2, estado="en_curso", fecha=octubre(30, 17))
    nueva_tarea(conn, mundo, T3, estado="en_curso", fecha=octubre(30, 17))
    quien, entrante = escribe("Marcos", "la del tablero la termino el 14", at=octubre(6, 10))
    procesar_turno(conn, quien, entrante, IAGuionada(
        jugadas=[[Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-14",
                                              "motivo": "falta el cable"})]],
        redacciones=["Listo."]), RelojFijo(octubre(6, 10)))
    conn.commit()

    resultado = _pendientes(conn, escribe, octubre(6, 11))

    [hecho] = resultado.hechos[:1]
    de_t1 = next(t for t in hecho["tareas"] if t["titulo"] == T1)
    assert de_t1["prevision_vigente"]["fecha"] == "2026-10-14"
    assert resultado.texto.split("\n")[1] == f"🟠 {T1}, vie 9/10"


def test_un_aviso_previo_de_dos_tareas_sale_con_el_estado_de_cada_una(conn, mundo, dias):
    """Dos tareas que vencen el mismo día: los avisos de que vencen pronto salen en un solo
    mensaje, una lista. El aviso previo no dice el estado de su tarea; en una lista, lo dice para
    el ícono."""
    nueva_tarea(conn, mundo, T2, estado="en_curso", fecha=octubre(9, 17))
    dias.ia = IAQueNombra((T1, T2))

    [pedido] = dias.ciclo(octubre(6, 10))

    assert {h["tarea"]: h["estado"] for h in pedido["hechos"]} == {T1: "asignada",
                                                                   T2: "en_curso"}
    [fila] = todos(conn, "select cuerpo from message_outbox where chat_id = %s",
                   mundo["personas"]["Marcos"]["telegram"])
    assert fila["cuerpo"].split("\n")[1:3] == [f"⚪ {T1}", f"🟢 {T2}"]


# --- Si poner los íconos falla, el mensaje sale igual (revisión `review-fd5b12f57ba236dc`) ------
#
# Los íconos se ponen después de que redacta la IA: una falla ahí no puede frenar la respuesta ni
# el aviso. Sale el texto tal como lo redactó la IA, sin los íconos, y queda un incidente de
# severidad baja (nunca fallar en silencio).

def _que_falle(monkeypatch) -> None:
    def falla(pedido):
        raise RuntimeError("falla de prueba al poner los íconos")
    monkeypatch.setattr(hechos_mod, "iconos_de_las_listas", falla)


def _incidentes_de_los_iconos(conn) -> list[dict]:
    return todos(conn, "select severidad, resumen_sanitizado, referencia_cruda from incident "
                       "where etapa = %s", hechos_mod.ETAPA_ICONOS_POR_ESTADO)


def test_si_poner_los_iconos_falla_la_respuesta_sale_como_la_redacto_la_ia(conn, mundo, escribe,
                                                                         monkeypatch):
    nueva_tarea(conn, mundo, T2, estado="en_curso", fecha=octubre(30, 17))
    _que_falle(monkeypatch)

    resultado = _pendientes(conn, escribe, octubre(13, 10))

    assert resultado.texto.split("\n")[1:3] == [f"🗓️ {T1}, vie 9/10", f"🗓️ {T2}, vie 30/10"]
    [fila] = todos(conn, "select cuerpo from message_outbox where es_respuesta")
    assert fila["cuerpo"] == resultado.texto
    [incidente] = _incidentes_de_los_iconos(conn)
    assert incidente["severidad"] == "baja"
    assert "RuntimeError" in incidente["referencia_cruda"]


def test_si_poner_los_iconos_falla_el_aviso_sale_igual(conn, mundo, dias, monkeypatch):
    nueva_tarea(conn, mundo, T2, estado="en_curso", fecha=octubre(9, 17))
    dias.ia = IAQueNombra((T1, T2))
    _que_falle(monkeypatch)

    dias.ciclo(octubre(6, 10))

    [fila] = todos(conn, "select cuerpo from message_outbox where chat_id = %s",
                   mundo["personas"]["Marcos"]["telegram"])
    assert fila["cuerpo"].split("\n")[1:3] == [f"🗓️ {T1}", f"🗓️ {T2}"]
    [incidente] = _incidentes_de_los_iconos(conn)
    assert incidente["severidad"] == "baja"
