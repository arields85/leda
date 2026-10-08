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

def test_hay_veintinueve_conversaciones_y_cada_una_nombra_su_fuente():
    # La 21 y la 22 corren desde la porción 2 de la C-3 (la entrega), la 23 desde la 3b (la
    # aprobación), la 24 desde la 3c (quien aprueba no contesta), la 27 desde la D3 de la C-3d
    # (la entrega frente al criterio), la 28 y la 29 desde la D4 (las entregas en listas y si
    # cambia quién revisa), y la 26 desde la D5 (no interrumpir una conversación).
    convs = todas()
    assert [c["numero"] for c in convs] == [f"{n:02d}" for n in range(1, 30)]
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
    conn.commit()
    assert aviso_previo == 3
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


def test_una_grabacion_repite_la_corrida(conn):
    [conv] = elegir(["01"])
    grabada = correr_conversacion(conn, conv, _perfecta(conv))
    _limpiar(conn)

    repetida = correr_conversacion(conn, conv, IARepetida(copy.deepcopy(grabada.llamadas)))

    assert repetida.error is None
    assert _sin_corridas_variables(repetida) == _sin_corridas_variables(grabada)


class _ProveedorCaido(Exception):
    """Una falla del proveedor de la IA, con un texto que no puede llegar al informe."""


def test_un_aviso_que_la_ia_no_redacto_a_su_hora_se_informa_sin_el_texto_de_la_falla(conn):
    """Usuario, 2026-10-07: en las rondas con la IA real, a veces un aviso no salía a su hora y
    no quedaba rastro de por qué. El intento fallido deja su incidente, y el informe lo dice
    con la clase de la falla y su código HTTP, nunca con su texto: los informes se publican."""
    [conv] = elegir(["01"])
    ia = _perfecta(conv)
    redactar = ia.ia.redactar
    pendientes = [_ProveedorCaido("ChatGPT respondió HTTP 503 (texto crudo del proveedor).")]

    def una_vez_no(pedido):
        if pendientes:
            raise pendientes.pop()
        return redactar(pedido)

    ia.ia.redactar = una_vez_no

    corrida = correr_conversacion(conn, conv, ia)

    assert corrida.error is None and not pendientes
    primero = corrida.pasos[0].paso
    del_paso = [f for p, f in corrida.fallas() if p == primero]
    [rastro] = [f for f in del_paso if f.que == cp.AVISO_SIN_REDACTAR]
    assert rastro.que == "el aviso no salió a su hora: la IA no lo redactó"
    assert (rastro.clase, rastro.real) == (cp.MOTOR, {"falla": "_ProveedorCaido", "http": 503})
    assert any(f.que == "no salió lo esperado" for f in del_paso)
    assert not any(f.que == "incidente" for f in del_paso)     # no se cuenta dos veces
    texto = (informe.resumen([corrida], ronda="r", cabecera={}, transcripciones="t.md")
             + informe.transcripciones([corrida], ronda="r"))
    assert "la IA no lo redactó" in texto and "_ProveedorCaido" in texto and "503" in texto
    assert "texto crudo" not in texto and "ChatGPT respondió" not in texto


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
