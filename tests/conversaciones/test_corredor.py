"""El corredor de las conversaciones de prueba (E2-7).

`odd/tasks/prueba-chica-del-motor.md`, sección 6 y tarea E2-7. Con la IA guionada: el estado
inicial de cada conversación se carga como dice su YAML; una conversación pasa entera cuando la
IA elige las jugadas esperadas y falla con una diferencia clara cuando no; la grabación de una
corrida la repite igual.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

from leda.db import admin

from tests.conversaciones import comprobar as cp
from tests.conversaciones import motores
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


# Lo único en que el motor definitivo se aparta a propósito de la prueba chica: sus hechos
# cuentan lo que pasa después como pasa en el mundo (`llega`), no con el estado interno de un
# aviso (usuario, 2026-10-06; conversación 18). Para comparar, la forma vieja se traduce.
_HUELLA = re.compile(r" · [0-9a-f]{6}\)")
# Lo que la prueba chica falla, y sólo por eso, en las conversaciones con la forma nueva.
_SOLO_LA_FORMA_DE_LOS_HECHOS = {(cp.MOTOR, "hechos"), (cp.MOTOR, "no salió lo esperado"),
                                (cp.MOTOR, "salió algo de más")}
_DE_LA_COCINA_AL_MUNDO = {"enviado": "ya_le_llego", "no_salio": "no_le_llego",
                          "retirado_sin_enviar": "no_le_va_a_llegar"}


def _como_en_el_mundo(valor):
    if isinstance(valor, list):
        return [_como_en_el_mundo(v) for v in valor]
    if not isinstance(valor, dict):
        return valor
    valor = {k: _como_en_el_mundo(v) for k, v in valor.items()}
    estado = valor.get("estado")
    if estado == "guardado_sin_enviar" and "sale" in valor:
        valor = {k: v for k, v in valor.items() if k not in ("estado", "sale")} | {
            "llega": valor["sale"]}
    elif estado == "todavia_no":
        valor = {k: v for k, v in valor.items() if k != "estado"}
    elif estado in _DE_LA_COCINA_AL_MUNDO and ("a" in valor or "motivo" in valor
                                                or len(valor) == 1):
        valor = {k: v for k, v in valor.items() if k != "estado"} | {
            "llega": _DE_LA_COCINA_AL_MUNDO[estado]}
    if "ya_no_sale" in valor:
        valor["ya_no_va_a_pasar"] = valor.pop("ya_no_sale")
    return valor


# --- Las conversaciones -------------------------------------------------------------------

def test_hay_dieciocho_conversaciones_y_cada_una_nombra_su_fuente():
    convs = todas()
    assert [c["numero"] for c in convs] == [f"{n:02d}" for n in range(1, 19)]
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

# --- Los dos motores (E3-8) -------------------------------------------------------------------
#
# Un solo corredor para el motor de la prueba chica y el definitivo (`motores.py`): la misma
# conversación, con la IA guionada, da lo mismo en los dos, y cada corrida dice cuál corrió.

def test_el_motor_por_omision_es_el_definitivo():
    assert motores.POR_OMISION == "leda.motor"
    assert motores.cargar().procesar_turno.__module__ == "leda.motor.turno"
    with pytest.raises(ValueError, match="No hay un motor"):
        motores.cargar("otro")


@pytest.mark.parametrize("nombre", motores.MOTORES)
def test_cada_motor_corre_la_conversacion_con_su_propio_codigo(conn, nombre):
    motor = motores.cargar(nombre)
    [conv] = elegir(["17"])

    corrida = correr_conversacion(conn, conv, IAQueGraba(IAPerfecta(
        {k: t["titulo"] for k, t in conv["tareas"].items()}, jugada=motor.Jugada)), motor=motor)

    assert corrida.error is None
    if nombre == motores.POR_OMISION:
        assert corrida.fallas() == []
    else:       # la prueba chica se quedó con la forma vieja de los hechos (conversación 18)
        assert {(f.clase, f.que) for _, f in corrida.fallas()} <= _SOLO_LA_FORMA_DE_LOS_HECHOS
    assert corrida.motor_usado == nombre
    assert motor.procesar_turno.__module__ == f"{nombre}.turno"
    assert motor.Ciclo.__module__ == f"{nombre}.ciclo"


def test_los_dos_motores_dan_lo_mismo_con_la_ia_guionada(conn):
    [conv] = elegir(["02"])
    por_motor = {}
    for nombre in motores.MOTORES:
        motor = motores.cargar(nombre)
        corrida = correr_conversacion(conn, conv, IAPerfecta(
            {k: t["titulo"] for k, t in conv["tareas"].items()}, jugada=motor.Jugada),
            motor=motor)
        _limpiar(conn)
        assert corrida.error is None
        por_motor[nombre] = corrida

    definitivo, chica = (por_motor[n] for n in motores.MOTORES)
    # El definitivo cumple la conversación entera; la prueba chica, que se quedó con la forma
    # vieja de los hechos, falla sólo en ellos.
    assert definitivo.fallas() == []
    assert {(f.clase, f.que) for _, f in chica.fallas()} <= _SOLO_LA_FORMA_DE_LOS_HECHOS
    # Traducidos los hechos, todo lo demás es igual. El texto de la IA guionada lleva la huella
    # de los hechos que recibió, que por eso cambia: se compara sin ella.
    for corrida in (definitivo, chica):
        for p in corrida.pasos:
            p.hechos, p.fallas = _como_en_el_mundo(p.hechos), []
            p.texto = _HUELLA.sub(")", p.texto) if p.texto else p.texto
            for s in p.salidas:
                s.texto = _HUELLA.sub(")", s.texto) if s.texto else s.texto
    assert _sin_corridas_variables(definitivo) == _sin_corridas_variables(chica)


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
