"""El corredor de las conversaciones de prueba (E2-7).

`odd/tasks/prueba-chica-del-motor.md`, sección 6 y tarea E2-7. Con la IA guionada: el estado
inicial de cada conversación se carga como dice su YAML; una conversación pasa entera cuando la
IA elige las jugadas esperadas y falla con una diferencia clara cuando no; la grabación de una
corrida la repite igual.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from leda.db import admin

from tests.conversaciones import comprobar as cp
from tests.conversaciones import informe, motores
from tests.conversaciones.carga import cargar
from tests.conversaciones.corredor import CARPETA, correr_conversacion, elegir, leer, todas
from tests.conversaciones.grabar import IAPerfecta, IAQueGraba, IARepetida


def _limpiar(conn) -> None:
    """Lo mismo que hace la fixture `conn` al terminar, para varias corridas en una prueba."""
    conn.rollback()
    with conn.cursor() as cur:
        cur.execute("set role leda_admin")
        cur.execute("""truncate workspace, app_user, platform_role, audit_log, incident,
                                admin_notice restart identity cascade""")
    conn.commit()


def _perfecta(conv) -> IAQueGraba:
    return IAQueGraba(IAPerfecta({k: t["titulo"] for k, t in conv["tareas"].items()}))


def _sin_corridas_variables(corrida) -> list:
    """Lo que tiene que repetirse igual: textos, jugadas, hechos y fallas de cada paso."""
    return [(p.paso, p.texto, p.jugadas, p.hechos, p.pregunta,
             # Dos mensajes del mismo momento pueden salir en cualquier orden.
             sorted((s.a, s.texto, s.botones, s.tipo, s.tareas) for s in p.salidas),
             [str(f) for f in p.fallas]) for p in corrida.pasos]


# --- Las conversaciones -------------------------------------------------------------------

def test_hay_cuarenta_y_siete_conversaciones_y_cada_una_nombra_su_fuente():
    # La 21 y la 22 corren desde la porción 2 de la C-3 (la entrega), la 23 desde la 3b (la
    # aprobación), la 24 desde la 3c (quien aprueba no contesta), la 27 desde la D3 de la C-3d
    # (la entrega frente al criterio), la 28 y la 29 desde la D4 (las entregas en listas y si
    # cambia quién revisa), la 26 desde la D5 (no interrumpir una conversación) y la 30 desde
    # la D5b (una pregunta de Leda sin contestar), la 31 desde la unidad de pedir el enlace
    # por chat (lo que quedó de la porción 4), la 32 desde la porción 1 de la C-5 (escribirle
    # a quien destraba), la 33 desde la porción 2 ("ya hablé con él") y la 34 desde la 3 ("no
    # me corresponde" y la cadena al referente), la 35 desde la 4 (los bloqueos encadenados), la
    # 36 desde la 5 (el bloqueo viejo), la 37 desde la C-6 (el pedido de estado con la lista) y
    # la 38 desde la C-7 (delegar) y la 39 desde sus decisiones 26 a 28 (el encargado pasa una
    # tarea de su gente, la revisión sigue a quien era la tarea y un pase sin respuesta), y la
    # 40 desde las decisiones 31, 32, 44 y 46 de la C-6 (la semana de las listas), y la 41 desde
    # la decisión 25 (el informe al grupo), y la 42 desde la C-5b (a quien destraba y no
    # contesta, Leda nunca lo abandona), y la 43 desde la C-5c (cerrar el tema para todos), y la
    # 44 desde la C-5e (seguir la cadena hasta quien puede destrabarla), y la 45 desde la
    # decisión 33 (el resumen para cualquiera, el detalle a pedido), y la 48 desde el aviso al
    # encargado anterior (el sector que se queda sin encargado), y la 49 desde las decisiones 57
    # a 60 (la administración retira una pieza), y la 47 desde la tercera porción de los apodos
    # (ADR 0020; decisión 65), y la 51 desde la T7 de las correcciones de la prueba por
    # Telegram (dejar una entrega sin terminar); la 50 está reservada para el acceso a la web.
    convs = todas()
    assert [c["numero"] for c in convs] == [f"{n:02d}" for n in range(1, 52)
                                            if n not in (46, 50)]
    raiz = CARPETA.parents[1]
    for c in convs:
        assert (raiz / c["fuente"]).exists(), c["fuente"]
        assert c["archivo"].startswith(c["numero"])


@pytest.mark.parametrize("ruta", sorted(CARPETA.glob("*.yaml")), ids=lambda p: p.stem)
def test_el_cargador_escribe_el_estado_inicial_de_cada_conversacion(conn, ruta):
    conv = leer(ruta)

    mundo = cargar(conn, conv)

    with admin(conn) as cur:
        cur.execute("""select t.titulo, t.estado::text estado, u.nombre, t.criterio_aceptacion,
                              (t.fecha_objetivo at time zone 'America/Argentina/Buenos_Aires')::date
                              vence
                         from task t join membership m on m.id = t.responsable_membership_id
                         join app_user u on u.id = m.app_user_id
                        where t.workspace_id = %s""", (mundo.workspace_id,))
        tareas = {f["titulo"]: f for f in cur.fetchall()}
        cur.execute("""select o.titulo origen, d.titulo destino from dependency x
                         join task o on o.id = x.origen_task_id
                         join task d on d.id = x.destino_task_id
                        where x.workspace_id = %s""", (mundo.workspace_id,))
        dependencias = {(f["origen"], f["destino"]) for f in cur.fetchall()}
        cur.execute("""select valor from workspace_setting
                        where workspace_id = %s and clave = 'aviso_previo_dias_habiles'""",
                    (mundo.workspace_id,))
        aviso_previo = cur.fetchone()["valor"]
        cur.execute("""select nombre, audiencia from cadence_job where workspace_id = %s""",
                    (mundo.workspace_id,))
        cadencias = {(f["nombre"], f["audiencia"]) for f in cur.fetchall()}
    conn.commit()
    assert aviso_previo == 3
    # Sólo las cadencias que nombra la conversación (la 37, C-6): las demás las suponen apagadas.
    assert cadencias == {(c["nombre"], c["audiencia"]) for c in conv.get("cadencias") or []}
    assert set(tareas) == {t["titulo"] for t in conv["tareas"].values()}
    for t in conv["tareas"].values():
        fila = tareas[t["titulo"]]
        assert fila["estado"] == t.get("estado", "asignada")
        assert fila["vence"].isoformat() == t["vence"]
        assert fila["nombre"].split()[0].startswith(t["responsable"][:4])
        # C-3d, D1: cada tarea, con un criterio de aceptación concreto, el de su YAML.
        assert t.get("criterio") and fila["criterio_aceptacion"] == t["criterio"], t["titulo"]
    assert dependencias == {(conv["tareas"][t["depende_de"]]["titulo"], t["titulo"])
                            for t in conv["tareas"].values() if t.get("depende_de")}


# --- Una corrida ----------------------------------------------------------------------------

def test_con_las_jugadas_esperadas_la_conversacion_pasa_entera(conn):
    [conv] = elegir(["01"])

    corrida = correr_conversacion(conn, conv, _perfecta(conv))

    assert corrida.error is None
    assert corrida.fallas() == []
    assert corrida.bien and corrida.garantias and corrida.comprension
    [aviso] = corrida.pasos[0].salidas
    assert (aviso.a, aviso.tipo, aviso.tareas, aviso.botones) == ("Marcos", "aviso_previo",
                                                                  ["PLC"], [])
    assert corrida.pasos[1].jugadas == [{"nombre": "anotar_inicio", "tarea": "PLC"}]


def test_el_aviso_de_una_entrega_cuenta_las_fotos_del_album_que_sigue_al_texto(conn):
    """Porción 3a de la C-3: el álbum es parte del aviso que salió antes a la misma persona, y
    lo esperado dice cuántas fotos lleva; otra cantidad es una falla del código."""
    [conv] = elegir(["21"])

    corrida = correr_conversacion(conn, conv, _perfecta(conv))

    assert corrida.error is None and corrida.fallas() == []
    [aviso] = corrida.pasos[-1].salidas
    assert (aviso.a, aviso.tipo, aviso.fotos, aviso.album_suelto) == (
        "Ismael", "entrega_para_aprobar", 3, False)
    # Porción 4: el enlace a la página de la tarea, al final, sin vista previa y nunca en la salida.
    assert aviso.enlace and aviso.sin_vista_previa
    assert "/tarea/" not in aviso.redactado and "/tarea/" not in aviso.texto

    _limpiar(conn)
    otra = copy.deepcopy(conv)
    otra["pasos"][-1]["salen"][0]["fotos"] = 2
    corrida = correr_conversacion(conn, otra, _perfecta(otra))
    assert [(paso, f.clase, f.que) for paso, f in corrida.fallas()] == [
        (8, cp.MOTOR, "no salió lo esperado"), (8, cp.MOTOR, "salió algo de más")]


def test_la_entrega_confirmada_por_otro_camino_no_es_una_falla_de_garantia(conn):
    """La falsa alarma de la 21 con la IA real (`resultados/fase-c-c3-regresion.md`, vez 1): la
    IA lee el primer mensaje sólo como el resultado de la prueba, Marcos suma un texto con la
    explicación y confirma nombrando la tarea. La cocina escribe lo que Marcos confirmó, que no
    es el camino ideal del YAML: es de comprensión o del motor, nunca de garantía."""
    [conv] = elegir(["21"])
    ia = _perfecta(conv)
    guion = copy.deepcopy(conv)
    por_paso = {p.get("paso"): p for p in guion["pasos"]}
    # Desde la D3 de la C-3d, lo descrito se juzga también frente al criterio de aceptación.
    por_paso[1]["jugadas"] = [{"nombre": "entregar", "tarea": "PLC",
                               "el_texto_cubre": ["resultado_de_prueba"],
                               "lo_descrito_cubre": ["C1"]}]
    # Desde la D7b el paso 5 espera `entregar` (suma la foto y lo que escribe); el otro camino es
    # `confirmar`, que suma sólo la foto.
    por_paso[5]["jugadas"] = [{"nombre": "confirmar", "tarea": "PLC"}]
    por_paso[6]["jugadas"] = [{"nombre": "confirmar", "tarea": "PLC"}]
    ia.ia.preparar = lambda paso: setattr(ia.ia, "paso", por_paso.get(paso.get("paso"), paso))

    corrida = correr_conversacion(conn, conv, ia)

    assert corrida.error is None
    assert corrida.garantias, [str(f) for _, f in corrida.fallas(cp.GARANTIA)]
    [escrito] = [f for paso, f in corrida.fallas() if paso == 6 and f.que.startswith("lo escrito")]
    assert escrito.que == "lo escrito no es el camino esperado: evidencia"
    assert escrito.clase in (cp.COMPRENSION, cp.MOTOR)
    # Lo escrito, en el orden en que se escribió; lo confirmado, en el de la vista previa.
    assert cp._mismas(escrito.real["escrito"], escrito.real["confirmado"])
    # Desde la D7 la 21 tiene un paso más, el 2: sin un ejemplo propuesto, su "si va asi" es un
    # texto más de la entrega; por `confirmar`, lo que escribió con la foto del paso 5 no entra.
    assert len(escrito.real["escrito"]) == 6


def test_la_aprobacion_corre_entera_con_los_botones_del_aviso_y_el_cierre_que_esperaba(conn):
    """Porción 3b de la C-3: el botón del aviso de una de varias entregas (`de_la_tarea`), lo que
    pasa aparte sin comprobarse (`aparte`) y el cierre que hace el sistema cuando se resuelve lo
    que faltaba, con su aviso a los dos."""
    [conv] = elegir(["23"])

    corrida = correr_conversacion(conn, conv, _perfecta(conv))

    assert corrida.error is None and corrida.fallas() == []
    del_viernes = [s for p in corrida.pasos if p.preludio for s in p.salidas
                   if s.tipo == "entrega_para_aprobar"]
    assert len(del_viernes) == 4
    assert all(s.botones == ["Aprobar", "Pedir cambios"] for s in del_viernes)
    cierre = next(p for p in corrida.pasos if p.paso == 11)
    assert sorted(s.a for s in cierre.salidas
                  if s.tipo == "cerrada_con_la_aprobacion") == ["Ismael", "Marcos"]


def test_otra_tarea_es_una_falla_de_garantia_con_su_diferencia(conn):
    [conv] = elegir(["01"])
    otra = copy.deepcopy(conv)
    # La IA elige la otra tarea: el guion de la IA cambia, lo esperado no.
    ia = _perfecta(conv)
    guion = copy.deepcopy(conv)
    guion["pasos"][1]["jugadas"] = [{"nombre": "anotar_inicio", "tarea": "COM"}]
    ia.ia.preparar = lambda paso: setattr(ia.ia, "paso", next(
        (p for p in guion["pasos"] if p.get("paso") == paso.get("paso")), paso))

    corrida = correr_conversacion(conn, otra, ia)

    assert not corrida.garantias and not corrida.comprension
    fallas = [f for _, f in corrida.fallas()]
    assert any(f.clase == cp.GARANTIA and f.que == "efecto de más: estado"
               and f.real == {"COM": "en_curso"} for f in fallas)
    assert any(f.clase == cp.COMPRENSION and f.que == "jugadas" for f in fallas)
    assert "esperado {'PLC': 'en_curso'}" in "\n".join(map(str, fallas))


def test_no_entender_y_no_hacer_nada_es_de_comprension_no_de_garantia(conn):
    [conv] = elegir(["01"])
    ia = _perfecta(conv)
    guion = copy.deepcopy(conv)
    guion["pasos"][1]["jugadas"] = [{"nombre": "anotar_inicio"}]       # pregunta cuál
    ia.ia.preparar = lambda paso: setattr(ia.ia, "paso", next(
        (p for p in guion["pasos"] if p.get("paso") == paso.get("paso")), paso))

    corrida = correr_conversacion(conn, conv, ia)

    assert corrida.garantias
    assert not corrida.comprension
    assert {f.que for _, f in corrida.fallas(cp.COMPRENSION)} >= {"jugadas",
                                                                   "falta un efecto: estado"}


# --- Otra lectura válida de un mensaje (`o_bien`; decisión 63, la 34) --------------------------

def _con_otra_lectura(conv, jugadas_de_la_otra, **de_la_otra):
    """La 01 con otra lectura válida del "arranqué" (paso 2): la IA no sabe de cuál tarea habla y
    pregunta; Marcos toca la del PLC (paso 2b) y la conversación vuelve a la principal."""
    otra = copy.deepcopy(conv)
    otra["pasos"][1]["o_bien"] = {
        "jugadas": jugadas_de_la_otra,
        "botones": ["PLC", "COM"],
        "pregunta": {"tipo": "cual_tarea"},
        **de_la_otra,
        "luego": [{"paso": "2b", "quien": "Marcos", "a_las": "2026-10-20 11:16", "toca": "PLC",
                   "efectos": {"estados": {"PLC": "en_curso"}},
                   "estado_despues": {"pregunta_abierta": None}}]}
    return otra


def _que_lee(conv, ia, jugadas_del_paso_2):
    """La IA guionada que lee el paso 2 como dicen `jugadas_del_paso_2`; los demás, como el YAML."""
    guion = copy.deepcopy(conv)
    guion["pasos"][1]["jugadas"] = jugadas_del_paso_2
    ia.ia.preparar = lambda paso: setattr(ia.ia, "paso", next(
        (p for p in guion["pasos"] if p.get("paso") == paso.get("paso")), paso))
    return ia


def test_la_otra_lectura_corre_sus_pasos_y_la_conversacion_vuelve_a_la_principal(conn):
    [conv] = elegir(["01"])
    pregunta = [{"nombre": "anotar_inicio"}]
    otra = _con_otra_lectura(conv, pregunta)

    corrida = correr_conversacion(conn, otra, _que_lee(conv, _perfecta(conv), pregunta))

    assert corrida.error is None and corrida.fallas() == [], corrida.fallas()
    assert [p.paso for p in corrida.pasos] == [1, 2, "2b", 3, 4]
    assert [p.lectura for p in corrida.pasos] == [None, cp.O_BIEN, None, None, None]

    # La guionada sigue la principal: los pasos de la otra no corren.
    _limpiar(conn)
    principal = correr_conversacion(conn, otra, _perfecta(conv))
    assert principal.error is None and principal.fallas() == [], principal.fallas()
    assert [p.paso for p in principal.pasos] == [1, 2, 3, 4]


def test_la_otra_lectura_no_saltea_las_garantias(conn):
    """Lo esperado de la otra lectura es sólo lo suyo: un efecto que no declara es de más, como
    en cualquier paso (la otra lectura nunca afloja una garantía)."""
    [conv] = elegir(["01"])
    la_otra_tarea = [{"nombre": "anotar_inicio", "tarea": "COM"}]
    otra = _con_otra_lectura(conv, la_otra_tarea, botones=[], pregunta=None)

    corrida = correr_conversacion(conn, otra, _que_lee(conv, _perfecta(conv), la_otra_tarea))

    paso_2 = next(p for p in corrida.pasos if p.paso == 2)
    assert paso_2.lectura == cp.O_BIEN
    assert any(f.clase == cp.GARANTIA and f.que == "efecto de más: estado"
               and f.real == {"COM": "en_curso"} for f in paso_2.fallas), paso_2.fallas


def test_la_34_vuelve_al_mismo_estado_por_los_dos_caminos_del_ni_idea(conn):
    """Decisión 63: si la IA no lee "no sabe" en el "ni idea" de Mariano (paso 7), Leda le
    pregunta una vez quién se encarga, él contesta que no (7b) y la conversación sigue igual."""
    [conv] = elegir(["34"])
    otra = next(p for p in conv["pasos"] if p["paso"] == 7)["o_bien"]["jugadas"]
    ia = _perfecta(conv)
    guion = copy.deepcopy(conv)
    next(p for p in guion["pasos"] if p["paso"] == 7)["jugadas"] = otra
    ia.ia.preparar = lambda paso: setattr(ia.ia, "paso", next(
        (p for p in guion["pasos"] if p.get("paso") == paso.get("paso")), paso))

    corrida = correr_conversacion(conn, conv, ia)

    assert corrida.error is None and corrida.fallas() == [], corrida.fallas()
    pasos = [p.paso for p in corrida.pasos]
    assert pasos[pasos.index(7):pasos.index(7) + 3] == [7, "7b", 8]


def test_la_23_por_la_otra_lectura_del_archivo_ofrece_la_misma_entrega(conn):
    """Decisión 68: si la IA lee la foto de Mariano (paso 12) como un archivo para la tarea y no
    como una entrega, Leda lo guarda y le ofrece volver a entregarla con eso: la misma vista
    previa, con Confirmar, y nada entregado."""
    [conv] = elegir(["23"])
    otra = next(p for p in conv["pasos"] if p["paso"] == 12)["o_bien"]["jugadas"]
    ia = _perfecta(conv)
    guion = copy.deepcopy(conv)
    next(p for p in guion["pasos"] if p["paso"] == 12)["jugadas"] = otra
    ia.ia.preparar = lambda paso: setattr(ia.ia, "paso", next(
        (p for p in guion["pasos"] if p.get("paso") == paso.get("paso")), paso))

    corrida = correr_conversacion(conn, conv, ia)

    assert corrida.error is None and corrida.fallas() == [], corrida.fallas()
    assert next(p for p in corrida.pasos if p.paso == 12).lectura == cp.O_BIEN


def _por_la_otra_lectura(conn, numero: str, paso: int, sin: tuple[str, ...] = (),
                         orden: tuple[int, ...] | None = None, cual: int = 0):
    """La conversación entera con la IA guionada que lee ese paso como su otra lectura (`o_bien`)
    y los demás como el YAML. `sin`: los datos de `puede_traer` que la IA no trae; `orden`: en qué
    orden nombra la IA las jugadas de la otra lectura (sus posiciones en el YAML); `cual`: cuál de
    las otras, si el paso tiene una lista (decisión 75)."""
    [conv] = elegir([numero])
    otras = next(p for p in conv["pasos"] if p["paso"] == paso)["o_bien"]
    otras = otras if isinstance(otras, list) else [otras]
    otra = [{k: v for k, v in j.items() if k not in sin} for j in otras[cual]["jugadas"]]
    if orden is not None:
        otra = [otra[i] for i in orden]
    ia = _perfecta(conv)
    guion = copy.deepcopy(conv)
    next(p for p in guion["pasos"] if p["paso"] == paso)["jugadas"] = otra
    ia.ia.preparar = lambda p: setattr(ia.ia, "paso", next(
        (q for q in guion["pasos"] if q.get("paso") == p.get("paso")), p))
    return correr_conversacion(conn, conv, ia)


@pytest.mark.parametrize("sin", [(), ("su_tarea_trabada",)], ids=["con_el_enlace", "sin_el_enlace"])
def test_la_35_por_la_otra_lectura_le_manda_a_marcos_un_solo_mensaje(conn, sin):
    """Decisión 72: si la IA también anota lo que dice Ariel del PLC (paso 4), lo que dijo y que
    se trabó le llegan a Marcos en un mensaje (paso 5), y la conversación sigue igual. Con el
    enlace a la tarea del servidor puesto antes de trabarla (ronda real de las decisiones 66 a 73,
    vez 3), lo mismo: se juzga con lo que deja el mensaje entero."""
    corrida = _por_la_otra_lectura(conn, "35", 4, sin)

    assert corrida.error is None and corrida.fallas() == [], corrida.fallas()
    paso_4 = next(p for p in corrida.pasos if p.paso == 4)
    assert paso_4.lectura == cp.O_BIEN
    [decir] = [j for j in paso_4.jugadas if j["nombre"] == "decir_cuando_destraba"]
    assert ("su_tarea_trabada" in decir) == (not sin)
    [a_marcos] = [s for s in next(p for p in corrida.pasos if p.paso == 5).salidas
                  if s.a == "Marcos"]
    assert a_marcos.tipos == ["lo_que_dijo_quien_destraba", "novedad_de_lo_que_espera"]


def test_la_35_por_la_otra_lectura_con_las_jugadas_en_otro_orden_pasa_igual(conn):
    """La ronda real `fase-c-formato` (la 35, vez 5, paso 4): la IA nombró las jugadas de la otra
    lectura en otro orden (el bloqueo, lo que dice del PLC y quién destraba). Leda hizo lo mismo,
    y el corredor no mira el orden: ni las jugadas ni sus hechos."""
    corrida = _por_la_otra_lectura(conn, "35", 4, orden=(1, 0, 2))

    assert corrida.error is None and corrida.fallas() == [], corrida.fallas()
    paso_4 = next(p for p in corrida.pasos if p.paso == 4)
    assert paso_4.lectura == cp.O_BIEN
    assert [j["nombre"] for j in paso_4.jugadas] == [
        "anotar_bloqueo", "decir_cuando_destraba", "anotar_quien_destraba"]


@pytest.mark.parametrize(("numero", "paso"), [("36", 20), ("39", 20), ("48", 10)])
def test_las_otras_lecturas_de_las_decisiones_69_y_71_llegan_al_mismo_lugar(conn, numero, paso):
    """Decisión 69 (la 48, paso 10: el pedido leído como fuera de la lista) y 71 (la 36, paso 20:
    la fecha sin "ya está"; la 39, paso 20: ninguna jugada para un pase cerrado): por la otra
    lectura, la conversación entera pasa sin fallas."""
    corrida = _por_la_otra_lectura(conn, numero, paso)

    assert corrida.error is None and corrida.fallas() == [], corrida.fallas()
    assert next(p for p in corrida.pasos if p.paso == paso).lectura == cp.O_BIEN


def test_la_48_por_la_lectura_sin_ninguna_jugada_pasa_sin_fallas(conn):
    """Decisión 75 (la ronda real `fase-c-formato-2`, la 48, vez 2, paso 10): la IA no elige
    ninguna jugada y Leda contesta por el contexto, sin hacer nada. Es la segunda otra lectura del
    paso (la primera, el pedido fuera de la lista de la decisión 69), y la conversación entera
    pasa sin fallas."""
    corrida = _por_la_otra_lectura(conn, "48", 10, cual=1)

    assert corrida.error is None and corrida.fallas() == [], corrida.fallas()
    paso_10 = next(p for p in corrida.pasos if p.paso == 10)
    assert paso_10.lectura == cp.O_BIEN and paso_10.jugadas == [] and paso_10.hechos == []


def test_una_grabacion_repite_la_corrida(conn):
    [conv] = elegir(["01"])
    grabada = correr_conversacion(conn, conv, _perfecta(conv))
    _limpiar(conn)

    repetida = correr_conversacion(conn, conv, IARepetida(copy.deepcopy(grabada.llamadas)))

    assert repetida.error is None
    assert _sin_corridas_variables(repetida) == _sin_corridas_variables(grabada)


class _ProveedorCaido(Exception):
    """Una falla del proveedor de la IA, con un texto que no puede llegar al informe."""


def _que_falla_al_redactar(ia, veces: int) -> list:
    """La IA guionada, con las primeras `veces` redacciones caídas como se cae el proveedor."""
    redactar = ia.ia.redactar
    pendientes = [_ProveedorCaido("ChatGPT respondió HTTP 503 (texto crudo del proveedor).")
                  for _ in range(veces)]

    def no_redacta(pedido):
        if pendientes:
            raise pendientes.pop()
        return redactar(pedido)

    ia.ia.redactar = no_redacta
    return pendientes


def test_un_aviso_que_la_ia_no_redacto_sale_en_su_paso_tras_el_reintento(conn):
    """Usuario, 2026-10-07, y la causa de los avisos que a veces no salían a su hora (1 o 2 de
    cada 95 corridas): una falla del servicio de la IA (429, 503, un plazo agotado) deja el aviso
    guardado para reintentarlo al minuto (decisión 8, caso 2). El ciclo del escuchador corre cada
    minuto y lo manda; el corredor sólo corría en los relojes del paso, así que el reintento no
    salía o caía en otro paso. Ahora el corredor adelanta su reloj al reintento y el aviso sale
    en el mismo paso. El intento fallido se informa como una falla del servicio, con la clase de
    la falla y su código HTTP, nunca con su texto (los informes se publican), y no es de Leda."""
    [conv] = elegir(["01"])
    ia = _perfecta(conv)
    pendientes = _que_falla_al_redactar(ia, 1)

    corrida = correr_conversacion(conn, conv, ia)

    assert corrida.error is None and not pendientes
    primero = corrida.pasos[0]
    [aviso] = primero.salidas
    assert (aviso.a, aviso.tipo, aviso.tareas) == ("Marcos", "aviso_previo", ["PLC"])
    [rastro] = primero.fallas
    assert rastro.que == cp.AVISO_SIN_REDACTAR
    assert (rastro.clase, rastro.real) == (cp.SERVICIO,
                                           {"falla": "_ProveedorCaido", "http": 503})
    # Lo de Leda está bien: la falla del servicio no se cuenta como suya.
    assert [f for _, f in corrida.fallas() if f.clase != cp.SERVICIO] == []
    assert corrida.bien and corrida.garantias and corrida.comprension and corrida.motor
    texto = (informe.resumen([corrida], ronda="r", cabecera={}, transcripciones="t.md")
             + informe.transcripciones([corrida], ronda="r"))
    assert "G ok · C ok · M ok · F ok" in texto
    assert "[servicio]" in texto and "[motor]" not in texto
    assert "_ProveedorCaido" in texto and "503" in texto
    assert "texto crudo" not in texto and "ChatGPT respondió" not in texto


def test_un_aviso_que_no_salio_tras_los_cinco_intentos_sigue_siendo_una_falla(conn):
    """Si el servicio falla los cinco intentos, el aviso queda `fallido` y no sale: eso sí es
    una falla, como hoy. Los cuatro reintentos corren dentro del mismo paso."""
    [conv] = elegir(["01"])
    ia = _perfecta(conv)
    pendientes = _que_falla_al_redactar(ia, 5)

    corrida = correr_conversacion(conn, conv, ia)

    assert corrida.error is None and not pendientes
    primero = corrida.pasos[0]
    assert primero.salidas == []
    del_paso = [(f.clase, f.que) for f in primero.fallas]
    assert del_paso.count((cp.SERVICIO, cp.AVISO_SIN_REDACTAR)) == 4
    assert (cp.MOTOR, "no salió lo esperado") in del_paso
    # El quinto fallo, en el mismo paso: el aviso `fallido` con su incidente.
    assert (cp.MOTOR, "incidente") in del_paso
    assert not corrida.motor and not corrida.bien


def test_un_texto_con_formato_se_enlaza_con_su_fila_y_el_informe_lo_muestra_entero(conn):
    """El formato de los mensajes (2026-10-07; conversación 20): el outbox guarda las marcas
    de la IA y el transporte entrega el texto plano. El corredor enlaza cada entregado con su
    fila igual, y la transcripción muestra el texto como lo escribió la IA, renglón por
    renglón, sin romper la lista del paso."""
    [conv] = elegir(["01"])
    ia = _perfecta(conv)
    redactar = ia.ia.redactar
    ia.ia.redactar = lambda pedido: f"**Anotado.**\n\n• {redactar(pedido)}\n• otra cosa"

    corrida = correr_conversacion(conn, conv, ia)

    assert corrida.error is None
    [aviso] = corrida.pasos[0].salidas
    assert aviso.texto.startswith("**Anotado.**\n\n• (IA guionada")
    assert aviso.texto.endswith("\n• otra cosa")
    assert aviso.redactado == aviso.texto
    transcripcion = informe.transcripciones([corrida], ronda="r")
    assert "- Leda, por su cuenta (aviso_previo PLC" in transcripcion
    assert "  > **Anotado.**\n  >\n  > • (IA guionada" in transcripcion
    assert "\n  > • otra cosa\n" in transcripcion
    # Desde la segunda vuelta del formato (2026-10-07), la negrita es una falla de formato de
    # cada mensaje, aparte: el código hizo lo esperado.
    assert corrida.garantias and corrida.comprension and corrida.motor
    assert not corrida.formato and not corrida.bien
    assert {(f.clase, f.esperado, f.real) for _, f in corrida.fallas()} == {
        (cp.FORMATO, cp.SIN_NEGRITA, "**Anotado.**")}
    resumen = informe.resumen([corrida], ronda="r", cabecera={}, transcripciones="t.md")
    assert "G ok · C ok · M ok · F FALLA" in resumen
    assert "| Garantías | Comprensión (provisional) | Formato | Lectura del usuario |" in resumen
    assert "| 1/1 | 1/1 | 0/1 |  |" in resumen


def test_un_boton_que_no_esta_es_una_falla_de_la_corrida_no_una_caida(conn):
    """Ronda 1, conversación 09, vez 5: sin la pregunta con botones, el toque siguiente hacía
    caer la corrida. Ahora es una falla del paso y la corrida sigue."""
    [conv] = elegir(["09"])
    ia = _perfecta(conv)
    guion = copy.deepcopy(conv)
    guion["pasos"][0]["jugadas"] = []           # no eligió nada: no hay botones
    ia.ia.preparar = lambda paso: setattr(ia.ia, "paso", next(
        (p for p in guion["pasos"] if p.get("paso") == paso.get("paso")), paso))

    corrida = correr_conversacion(conn, conv, ia)

    assert corrida.error is None
    assert len(corrida.pasos) == len(conv["pasos"])
    [falla] = [f for p, f in corrida.fallas() if p == 2 and f.que == "no hay un botón para tocar"]
    assert falla.clase == cp.COMPRENSION and falla.esperado == "COM"

# --- La línea de comandos --------------------------------------------------------------------

def _bases_del_corredor(conn) -> list[str]:
    with conn.cursor() as cur:
        cur.execute("select datname from pg_database where datname like 'leda_corrida_%'")
        nombres = [f["datname"] for f in cur.fetchall()]
    conn.commit()
    return nombres


def test_las_bases_viejas_de_corridas_muertas_se_borran_al_empezar(conn):
    """Una ejecución que se murió sin borrar su plantilla (revisión de la E2-7): la siguiente
    borra las bases del corredor que son viejas, y nunca una que puede ser de otra que corre ni
    una que el corredor no creó (sin la fecha de su nombre). El momento es fijo y anterior a
    toda base real del servidor: la prueba no depende de lo que haya quedado de otras."""
    import os
    from datetime import datetime, timezone

    import psycopg
    from psycopg.sql import SQL, Identifier

    from tests.conversaciones import correr

    url = os.environ["LEDA_TEST_DB_URL"]
    ahora = datetime(2020, 1, 1, 12, 30, tzinfo=timezone.utc)
    vieja = f"{correr.PREFIJO}plantilla_20200101000000_abcdef01"      # 12 h 30 antes
    reciente = f"{correr.PREFIJO}20200101060000_abcdef02"              # de otra que corre
    sin_fecha = f"{correr.PREFIJO}plantilla_0123456789"                # no es un nombre suyo
    ajena = f"{correr.PREFIJO}de_otro_20200101000000"                  # tampoco
    bases = correr.Bases(url)
    creadas = (vieja, reciente, sin_fecha, ajena, bases.plantilla)
    with psycopg.connect(url, autocommit=True) as c:
        for nombre in creadas:
            c.execute(SQL("create database {}").format(Identifier(nombre)))
    try:
        borradas = bases.limpiar_viejas(ahora)

        assert borradas == [vieja]
        assert set(_bases_del_corredor(conn)) & set(creadas) == set(creadas) - {vieja}
    finally:
        with psycopg.connect(url, autocommit=True) as c:
            for nombre in creadas:
                c.execute(SQL("drop database if exists {} with (force)").format(
                    Identifier(nombre)))


def test_la_corrida_en_seco_por_linea_de_comandos_graba_y_repite(conn, tmp_path, capsys):
    from tests.conversaciones import correr

    antes = _bases_del_corredor(conn)

    assert correr.main(["--conversacion", "01", "--veces", "1", "--sin-informe",
                        "--grabar", str(tmp_path)]) == 0
    [grabacion] = list(tmp_path.glob("01-leda.motor-guionada-1.json"))
    assert correr.main(["--repetir", str(grabacion), "--sin-informe"]) == 0

    salida = capsys.readouterr().out
    assert salida.count("01 vez 1: bien") == 2
    # Cada corrida en su base, y ninguna queda: ni las de las corridas ni la plantilla.
    assert _bases_del_corredor(conn) == antes


def test_cada_paso_en_que_leda_escribe_lleva_la_casilla_del_proximo_paso(conn):
    """La definición del usuario (2026-10-06): todo mensaje de Leda termina con un próximo paso
    concreto. La casilla para leerlo se agrega sola en cada paso en que Leda escribe, salvo que
    el paso ya diga cuál es su próximo paso; un paso en que Leda no manda nada no la lleva."""
    from tests.conversaciones.corredor import PROXIMO_PASO

    [conv] = elegir(["17"])
    corrida = correr_conversacion(conn, conv, _perfecta(conv))

    assert corrida.error is None
    for paso in corrida.pasos:
        con_el_suyo = [d for d in paso.dice if "próximo paso" in d]
        if paso.preludio or not (paso.texto or paso.salidas):
            assert PROXIMO_PASO not in paso.dice, paso.paso
        else:
            assert len(con_el_suyo) == 1, (paso.paso, paso.dice)
    primero = next(p for p in corrida.pasos if not p.preludio)     # el destrabe del paso 1
    assert PROXIMO_PASO not in primero.dice and any("próximo paso concreto" in d
                                                    for d in primero.dice)

# --- El motor que corre (E3-8) ---------------------------------------------------------------
#
# El corredor toma lo que usa del motor en un solo lugar (`motores.py`), y cada corrida dice
# cuál corrió. Hasta el 2026-10-07 también corría el de la prueba chica, ya borrada.

def test_el_motor_por_omision_es_el_definitivo():
    assert motores.MOTORES == ("leda.motor",)
    assert motores.POR_OMISION == "leda.motor"
    assert motores.cargar().procesar_turno.__module__ == "leda.motor.turno"
    with pytest.raises(ValueError, match="No hay un motor"):
        motores.cargar("otro")


def test_el_motor_corre_la_conversacion_con_su_propio_codigo(conn):
    motor = motores.cargar()
    [conv] = elegir(["17"])

    corrida = correr_conversacion(conn, conv, IAQueGraba(IAPerfecta(
        {k: t["titulo"] for k, t in conv["tareas"].items()}, jugada=motor.Jugada)), motor=motor)

    assert corrida.error is None
    assert corrida.fallas() == []
    assert corrida.motor_usado == "leda.motor"
    assert motor.procesar_turno.__module__ == "leda.motor.turno"
    assert motor.Ciclo.__module__ == "leda.motor.ciclo"


@pytest.mark.parametrize("nombre", motores.MOTORES)
def test_el_informe_y_la_grabacion_dicen_que_motor_corrio(conn, tmp_path, monkeypatch, nombre):
    from tests.conversaciones import correr, informe

    monkeypatch.setattr(informe, "RESULTADOS", tmp_path / "resultados")
    monkeypatch.setenv("LEDA_LOAD_DOTENV", "0")

    assert correr.main(["--motor", nombre, "--conversacion", "01", "--veces", "1",
                        "--ronda", "con-motor", "--grabar", str(tmp_path / "g")]) == 0

    resumen = (tmp_path / "resultados" / "con-motor.md").read_text("utf-8")
    transcripciones = (tmp_path / "resultados" / "con-motor-transcripciones.md").read_text(
        "utf-8")
    assert f"- **Motor:** {nombre}" in resumen
    assert f"Motor: `{nombre}`" in transcripciones
    [grabacion] = (tmp_path / "g").glob(f"01-{nombre}-guionada-1.json")
    assert json.loads(grabacion.read_text("utf-8"))["motor"] == nombre


def test_quien_aprueba_no_contesta_corre_entera_dia_por_dia(conn):
    """Porción 3c de la C-3: los recordatorios a quien aprueba, el aviso a quien está arriba
    (en un envío con lo suyo), los días sin nada (el fin de semana), el recordatorio guardado que
    se omite porque ya decidió y que se destrabó."""
    [conv] = elegir(["24"])

    corrida = correr_conversacion(conn, conv, _perfecta(conv))

    assert corrida.error is None and corrida.fallas() == [], corrida.fallas()
    al_responsable = [s for p in corrida.pasos if not p.preludio for s in p.salidas
                      if s.a == "Nahuel" and not s.es_respuesta]
    assert [s.tipo for s in al_responsable] == ["tarea_aprobada"]


def test_la_direccion_de_prueba_vale_mientras_corra_alguna_corrida():
    """D7b (la 28, vez 5, con `--paralelo`): una corrida que terminaba primero devolvía la
    dirección pública vacía mientras otra seguía, y a ésa le faltaba el enlace a la página de la
    tarea desde el paso 2. Dos corridas que se pisan, en orden fijo: la dirección de prueba vale
    hasta que termina la última, y después vuelve la de antes."""
    from leda import config as config_mod
    from tests.conversaciones import corredor

    antes = config_mod.config.base_url
    a = corredor._con_la_direccion_de_prueba()
    b = corredor._con_la_direccion_de_prueba()
    a.__enter__()
    b.__enter__()
    a.__exit__(None, None, None)
    try:
        assert config_mod.config.base_url == corredor.DIRECCION_DE_PRUEBA
    finally:
        b.__exit__(None, None, None)
    assert config_mod.config.base_url == antes


# --- Lo que hace la administración (`administracion`; la 48) ---------------------------------

def _la_27_hasta_el_aviso_a_ismael_y(paso_de_la_administracion) -> dict:
    """La 27 hasta que el aviso de la entrega del PLC, con su foto, le llega a Ismael (paso 6), y
    después un paso de la administración."""
    [conv] = elegir(["27"])
    otra = copy.deepcopy(conv)
    otra["pasos"] = [p for p in otra["pasos"] if p["paso"] <= 6] + [
        {"paso": 7, "quien": "Administracion", "a_las": "2026-10-22 16:00",
         **paso_de_la_administracion}]
    return otra


_RETIRAR_LA_FOTO = {"hace": "retirar_contenido", "tarea": "PLC", "clase": "imagen",
                    "motivo": "en la foto se ve la clave del PLC"}
_LOS_DOS_AVISOS = [
    {"tipo": "contenido_retirado_por_la_administracion", "tarea": "PLC", "a": "Marcos",
     "estado": "guardado"},
    {"tipo": "la_entrega_espera_otra_pieza", "tarea": "PLC", "a": "Ismael", "estado": "guardado"}]


def test_la_administracion_retira_el_contenido_como_la_consola_y_sus_efectos_se_comparan(conn):
    """El retiro corre la función de la consola (`pagina_de_tarea.retirar_contenido`), por el
    administrador de plataforma de la corrida y con el reloj del paso: la pieza queda retirada,
    no borrada, y se guardan los avisos a quien la entregó y a quien la revisa (decisión 58)."""
    conv = _la_27_hasta_el_aviso_a_ismael_y({
        "administracion": _RETIRAR_LA_FOTO,
        "efectos": {"retiradas": [{"tarea": "PLC", "clase": "imagen"}],
                    "avisos_guardados": _LOS_DOS_AVISOS},
        "hechos": [{"hace": "retirar_contenido", "tarea": "PLC", "piezas_retiradas": 1,
                    "piezas_que_siguen": 1, "contenidos_borrados": 1}]})

    corrida = correr_conversacion(conn, conv, _perfecta(conv))

    assert corrida.error is None and corrida.fallas() == [], corrida.fallas()
    paso = corrida.pasos[-1]
    assert paso.quien == "Administracion" and paso.texto.startswith("[administración]")
    assert paso.salidas == [] and paso.jugadas == []
    # No es un mensaje de Leda: no lleva la casilla del próximo paso.
    assert paso.dice == []
    with admin(conn) as cur:
        cur.execute("""select count(*) n from evidence e join evidencia_retirada w
                         on w.evidence_id = e.id where w.retirada_por_app_user_id is not null""")
        assert cur.fetchone()["n"] == 1
        cur.execute("""select count(*) n from audit_log
                        where accion = 'retirar_contenido_de_evidencia'""")
        assert cur.fetchone()["n"] == 1
    conn.commit()


def test_lo_que_hace_la_administracion_sin_esperarlo_es_de_garantia_y_lo_que_falta_del_motor(
        conn):
    """Nadie eligió jugadas: un efecto que no se esperaba es de garantía, como en un turno, y uno
    esperado que no pasó es del código, nunca de comprensión."""
    de_mas = _la_27_hasta_el_aviso_a_ismael_y({
        "administracion": _RETIRAR_LA_FOTO,
        "efectos": {"retiradas": [{"tarea": "PLC", "clase": "imagen"}]}})
    corrida = correr_conversacion(conn, de_mas, _perfecta(de_mas))
    assert corrida.error is None
    assert [(f.clase, f.que) for _, f in corrida.fallas()] == [
        (cp.GARANTIA, "efecto de más: aviso guardado")]

    _limpiar(conn)
    falta = _la_27_hasta_el_aviso_a_ismael_y({
        "administracion": _RETIRAR_LA_FOTO,
        "efectos": {"retiradas": [{"tarea": "PLC", "clase": "imagen"}],
                    "avisos_guardados": _LOS_DOS_AVISOS + [
                        {"tipo": "aviso_previo", "tarea": "PLC", "a": "Marcos"}]}})
    corrida = correr_conversacion(conn, falta, _perfecta(falta))
    assert corrida.error is None
    assert [(f.clase, f.que) for _, f in corrida.fallas()] == [
        (cp.MOTOR, "falta un efecto: aviso guardado")]


def test_una_operacion_que_la_administracion_no_hace_es_un_error_del_yaml(conn):
    [conv] = elegir(["01"])
    otra = copy.deepcopy(conv)
    otra["pasos"] = otra["pasos"][:1] + [
        {"paso": 2, "quien": "Administracion", "a_las": "2026-10-20 11:00",
         "administracion": {"hace": "borrar_la_tarea", "tarea": "PLC"}}]

    corrida = correr_conversacion(conn, otra, _perfecta(otra))

    assert corrida.error is not None and "borrar_la_tarea" in corrida.error
