"""El corredor de las conversaciones de prueba (E2-7).

`odd/tasks/prueba-chica-del-motor.md`, sección 6 y tarea E2-7. Con la IA guionada: el estado
inicial de cada conversación se carga como dice su YAML; una conversación pasa entera cuando la
IA elige las jugadas esperadas y falla con una diferencia clara cuando no; la grabación de una
corrida la repite igual; Jev, consultado en paralelo, no cambia ninguna decisión.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from leda.db import admin
from leda.jev import ClienteJevGuionado

from prueba_chica import comprobar as cp
from prueba_chica.carga import cargar
from prueba_chica.corredor import CARPETA, correr_conversacion, elegir, leer, todas
from prueba_chica.grabar import IAPerfecta, IAQueGraba, IARepetida


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

def test_hay_quince_conversaciones_y_cada_una_nombra_su_fuente():
    convs = todas()
    assert [c["numero"] for c in convs] == [f"{n:02d}" for n in range(1, 16)]
    raiz = CARPETA.parents[1]
    for c in convs:
        assert (raiz / c["fuente"]).exists(), c["fuente"]
        assert c["archivo"].startswith(c["numero"])


@pytest.mark.parametrize("ruta", sorted(CARPETA.glob("*.yaml")), ids=lambda p: p.stem)
def test_el_cargador_escribe_el_estado_inicial_de_cada_conversacion(conn, ruta):
    conv = leer(ruta)

    mundo = cargar(conn, conv)

    with admin(conn) as cur:
        cur.execute("""select t.titulo, t.estado::text estado, u.nombre,
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


def test_jev_en_paralelo_no_cambia_ninguna_decision(conn):
    [conv] = elegir(["13"])
    sin_jev = correr_conversacion(conn, conv, _perfecta(conv))
    _limpiar(conn)
    respuesta = {"alcance": {"probabilities": {"una_tarea": 0.9, "varias_tareas": 0.05,
                                                "ninguna": 0.05}},
                 "tarea": {"probabilities": {"T1": 0.97, "T2": 0.02, "T3": 0.01}}}
    verificacion = {"misma": {"noul": 0.9}, "rival": {"noul": 0.1}}
    jev = ClienteJevGuionado([respuesta, verificacion] * 4)

    con_jev = correr_conversacion(conn, conv, _perfecta(conv), jev=jev)

    assert _sin_corridas_variables(con_jev) == _sin_corridas_variables(sin_jev)
    consultas = [p.jev for p in con_jev.pasos if p.jev]
    assert len(consultas) == 2
    assert consultas[0]["tipo"] == "clara" and consultas[0]["eligio"] == "PLC"
    assert consultas[0]["acierta"] is False          # lo correcto era preguntar
    assert consultas[0]["probabilidades"]["PLC"] == 0.97
    assert [p.eleccion_de_la_ia for p in con_jev.pasos if p.jev] == ["preguntar", "PLC"]

# --- La línea de comandos --------------------------------------------------------------------

def _bases_del_corredor(conn) -> list[str]:
    with conn.cursor() as cur:
        cur.execute("select datname from pg_database where datname like 'leda_corrida_%'")
        nombres = [f["datname"] for f in cur.fetchall()]
    conn.commit()
    return nombres


def test_las_bases_viejas_de_corridas_muertas_se_borran_al_empezar(conn):
    """Una ejecución que se murió sin borrar su plantilla (revisión de la E2-7): la siguiente
    borra las bases del corredor que son viejas, y nunca una que puede ser de otra que corre."""
    import os

    import psycopg
    from psycopg.sql import SQL, Identifier

    from prueba_chica import correr

    url = os.environ["LEDA_TEST_DB_URL"]
    vieja = f"{correr.PREFIJO}plantilla_20200101000000_abcdef"
    sin_fecha = f"{correr.PREFIJO}plantilla_0123456789"         # el nombre de antes
    bases = correr.Bases(url)
    with psycopg.connect(url, autocommit=True) as c:
        for nombre in (vieja, sin_fecha):
            c.execute(SQL("create database {}").format(Identifier(nombre)))
        c.execute(SQL("create database {}").format(Identifier(bases.plantilla)))
    try:
        borradas = bases.limpiar_viejas()

        assert sorted(borradas) == sorted([vieja, sin_fecha])
        assert set(_bases_del_corredor(conn)) & {vieja, sin_fecha} == set()
        assert bases.plantilla in _bases_del_corredor(conn)     # la nueva queda
    finally:
        for nombre in (vieja, sin_fecha, bases.plantilla):
            bases.borrar(nombre)


def test_la_corrida_en_seco_por_linea_de_comandos_graba_y_repite(conn, tmp_path, capsys):
    from prueba_chica import correr

    antes = _bases_del_corredor(conn)

    assert correr.main(["--conversacion", "01", "--veces", "1", "--sin-informe",
                        "--grabar", str(tmp_path)]) == 0
    [grabacion] = list(tmp_path.glob("01-guionada-1.json"))
    assert correr.main(["--repetir", str(grabacion), "--sin-informe"]) == 0

    salida = capsys.readouterr().out
    assert salida.count("01 vez 1: bien") == 2
    # Cada corrida en su base, y ninguna queda: ni las de las corridas ni la plantilla.
    assert _bases_del_corredor(conn) == antes
