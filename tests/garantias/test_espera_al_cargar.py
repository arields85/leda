"""La espera al cargar una tarea desde la puerta de administración (ADR 0023, decisión 2; mecánica
§4; porción J1 de `odd/tasks/plataforma-jerarquias.md`; migración 0067).

- **Una sola espera, opcional y siempre bloqueante:** la tarea nueva espera a otra tarea
  comprometida y abierta del mismo espacio (`dependency`: la esperada es el origen, la nueva el
  destino).
- **Lo que no se carga**, junto con lo demás: una espera de otro espacio o que no existe, una
  cerrada (terminada o cancelada) y una propuesta sin comprometer (punto 9: una propuesta nunca
  traba una tarea comprometida).
- **El ciclo:** si la guarda de la base (`evitar_ciclo_dependencia`) salta, la carga entera se
  deshace y vuelve como un rechazo más, con su motivo, nunca como un error crudo.
- **La regla de §4 sigue en la base:** la que espera no pasa a `en_curso` mientras la esperada no
  está terminada.
- **La auditoría** de la carga guarda la espera; **sin espera**, la carga queda como antes, también
  su clave de un solo uso.
"""

from __future__ import annotations

import secrets

import psycopg
import pytest

from leda.db import admin, espacio
from tests.garantias.test_carga_de_tareas import (  # noqa: F401
    _cuerpo, _datos, _errores, _fila, _hash, _navegador_de_administracion, _norte, _persona,
    administradora, sesion, sin_espacio, web)
from tests.garantias.test_carga_de_tareas import _contar

FIRMA_DE_LA_0064 = ("leda.cargar_tarea(text, uuid, uuid, text, text, uuid, date, text, text[], "
                    "uuid, text, timestamptz)")
FIRMA_DE_LA_0067 = FIRMA_DE_LA_0064[:-1] + ", uuid)"


# --- Ayudas ---------------------------------------------------------------------------------

def _llamar(cur, sesion: str, d: dict) -> dict:
    """La carga con la espera (`None`: sin espera)."""
    cur.execute(
        """select cargar_tarea(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) as r""",
        (_hash(sesion), d["espacio"], d["objetivo"], d["titulo"], d["descripcion"],
         d["responsable"], d["fecha"], d["criterio"], d["evidencia"], d["decidio"],
         d["clave"], d["ahora"], d.get("espera")))
    return cur.fetchone()["r"]


def _cargar(conn, sesion: str, mundo: dict, **cambios) -> dict:
    with sin_espacio(conn) as cur:
        resultado = _llamar(cur, sesion, _datos(mundo, **cambios))
    conn.commit()
    return resultado


def _cargada(conn, sesion: str, mundo: dict, **cambios) -> str:
    r = _cargar(conn, sesion, mundo, **cambios)
    assert r["ok"] is True, r
    return r["task_id"]


def _en_el_oeste(mundo: dict, **cambios) -> dict:
    oeste = mundo["west-studio"]
    return {"espacio": oeste["id"], "objetivo": oeste["objectives"][0],
            "responsable": _persona(mundo, "Sam North", "west-studio"),
            "decidio": _persona(mundo, "Morgan Hale", "west-studio"), **cambios}


def _esperas(conn) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select workspace_id::text ws, origen_task_id::text origen, "
                    "destino_task_id::text destino, tipo::text tipo from dependency")
        filas = cur.fetchall()
    conn.commit()
    return filas


def _terminar(conn, mundo: dict, tarea: str) -> None:
    """La cierra como se cierra: con su evidencia (un texto) y aprobada por quien revisa a Sam
    North (Taylor Quinn)."""
    norte = _norte(mundo)
    with admin(conn) as cur:
        cur.execute(
            """update task_evidence_policy
                  set tipos = '{"test record": {"clases": ["texto"], "en_palabras": "un registro"}}'
                where area_id = %s""", (norte["areas"]["field"],))
        cur.execute(
            """insert into evidence (workspace_id, task_id, tipo, clase, texto, cubre)
               values (%s, %s, 'test record', 'texto', 'Quedó colocado', array['test record'])""",
            (norte["id"], tarea))
        cur.execute(
            """insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                     aprobador_membership_id, decision)
               values (%s, 'tarea', %s, %s, 'aprobado')""",
            (norte["id"], tarea, _persona(mundo, "Taylor Quinn")))
        cur.execute(
            """insert into task_state_event (task_id, estado_anterior, estado_nuevo, actor_kind)
               values (%s, 'asignada', 'terminada', 'persona')""", (tarea,))
    conn.commit()


def _cancelar(conn, tarea: str) -> None:
    with admin(conn) as cur:
        cur.execute(
            """insert into task_state_event (task_id, estado_anterior, estado_nuevo, actor_kind,
                                             motivo)
               values (%s, 'asignada', 'cancelada', 'persona', 'ya no hace falta')""", (tarea,))
    conn.commit()


def _propuesta(conn, mundo: dict) -> str:
    """Una tarea propuesta y sin comprometer (sin ningún evento: queda `propuesta`)."""
    norte = _norte(mundo)
    with admin(conn) as cur:
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id)
               values (%s, %s, 'Comprar los tornillos', %s, %s) returning id""",
            (norte["id"], norte["objectives"][0], norte["areas"]["field"],
             _persona(mundo, "Sam North")))
        tarea = str(cur.fetchone()["id"])
    conn.commit()
    return tarea


# --- La función -----------------------------------------------------------------------------

def test_la_carga_tiene_la_espera_como_ultimo_dato_y_la_firma_vieja_no_queda(conn):
    with admin(conn) as cur:
        cur.execute("select to_regprocedure(%s) is not null as nueva, "
                    "to_regprocedure(%s) is not null as vieja",
                    (FIRMA_DE_LA_0067, FIRMA_DE_LA_0064))
        fila = cur.fetchone()
    conn.commit()
    assert (fila["nueva"], fila["vieja"]) == (True, False)


# --- Una carga con espera -------------------------------------------------------------------

def test_la_espera_se_carga_bloqueante_y_queda_en_la_auditoria(conn, intake_world, sesion):
    norte = _norte(intake_world)
    estante = _cargada(conn, sesion, intake_world, titulo="Colocar el estante")
    otro_objetivo = norte["objectives"][1]
    tornillos = _cargada(conn, sesion, intake_world, titulo="Comprar los tornillos",
                         objetivo=otro_objetivo, espera=estante)
    assert _esperas(conn) == [{"ws": norte["id"], "origen": estante, "destino": tornillos,
                               "tipo": "bloqueante"}]
    auditoria = _fila(conn, "select detalle from audit_log where accion = 'cargar_tarea' "
                            "and sujeto_id = %s", tornillos)
    assert auditoria["detalle"]["espera_task_id"] == estante
    assert auditoria["detalle"]["espera_tipo"] == "bloqueante"


def test_sin_espera_la_carga_queda_como_antes(conn, intake_world, sesion):
    """Ni espera ni rastro de ella en la auditoría; y la clave de una carga sin espera, hecha con
    la firma de antes, se reconoce igual (la huella no cambia)."""
    from tests.garantias.test_carga_de_tareas import _llamar as _llamar_como_antes

    datos = _datos(intake_world)
    with sin_espacio(conn) as cur:
        primera = _llamar_como_antes(cur, sesion, datos)
    conn.commit()
    assert primera["ok"] is True
    with sin_espacio(conn) as cur:
        otra = _llamar(cur, sesion, {**datos, "espera": None})
    conn.commit()
    assert otra["ok"] is True and otra["repetida"] is True
    assert otra["task_id"] == primera["task_id"]
    assert _esperas(conn) == []
    auditoria = _fila(conn, "select detalle from audit_log where accion = 'cargar_tarea'")
    assert "espera_task_id" not in auditoria["detalle"]
    assert "espera_tipo" not in auditoria["detalle"]


def test_la_misma_clave_con_otra_espera_es_otra_carga(conn, intake_world, sesion):
    a = _cargada(conn, sesion, intake_world, titulo="Colocar el estante")
    b = _cargada(conn, sesion, intake_world, titulo="Pintar la pared")
    clave = secrets.token_urlsafe(18)
    primera = _cargar(conn, sesion, intake_world, clave=clave, espera=a)
    assert primera["ok"] is True and primera["repetida"] is False
    repetida = _cargar(conn, sesion, intake_world, clave=clave, espera=a)
    assert repetida["repetida"] is True and repetida["task_id"] == primera["task_id"]
    for distinta in (b, None):
        assert _errores(_cargar(conn, sesion, intake_world, clave=clave, espera=distinta)) == {
            ("clave", "usada_con_otros_datos")}
    assert len(_esperas(conn)) == 1


# --- Lo que no se carga ---------------------------------------------------------------------

def test_una_espera_de_otro_espacio_o_que_no_existe_no_se_carga(conn, intake_world, sesion):
    del_oeste = _cargada(conn, sesion, intake_world, **_en_el_oeste(intake_world))
    antes = _contar(conn, "task")
    for ajena in (del_oeste, "00000000-0000-0000-0000-000000000000"):
        assert _errores(_cargar(conn, sesion, intake_world, espera=ajena)) == {
            ("espera", "no_existe")}
    assert _contar(conn, "task") == antes
    assert _esperas(conn) == []


def test_una_espera_cerrada_no_se_carga(conn, intake_world, sesion):
    terminada = _cargada(conn, sesion, intake_world, titulo="Colocar el estante")
    _terminar(conn, intake_world, terminada)
    cancelada = _cargada(conn, sesion, intake_world, titulo="Pintar la pared")
    _cancelar(conn, cancelada)
    antes = _contar(conn, "task")
    for cerrada in (terminada, cancelada):
        assert _errores(_cargar(conn, sesion, intake_world, espera=cerrada)) == {
            ("espera", "esta_cerrada")}
    assert _contar(conn, "task") == antes
    assert _esperas(conn) == []


def test_una_propuesta_sin_comprometer_no_traba_una_tarea_comprometida(conn, intake_world,
                                                                       sesion):
    propuesta = _propuesta(conn, intake_world)
    assert _errores(_cargar(conn, sesion, intake_world, espera=propuesta)) == {
        ("espera", "no_esta_comprometida")}
    assert _esperas(conn) == []


def test_la_espera_se_rechaza_junto_con_lo_demas(conn, intake_world, sesion):
    assert _errores(_cargar(conn, sesion, intake_world, titulo="", criterio=None,
                            espera="00000000-0000-0000-0000-000000000000")) == {
        ("titulo", "falta"), ("criterio", "falta"), ("espera", "no_existe")}


# --- El ciclo -------------------------------------------------------------------------------

def test_la_guarda_de_la_base_sigue_rechazando_un_ciclo_entre_tareas_cargadas(
        conn, intake_world, sesion):
    estante = _cargada(conn, sesion, intake_world, titulo="Colocar el estante")
    tornillos = _cargada(conn, sesion, intake_world, titulo="Comprar los tornillos",
                         espera=estante)
    with espacio(conn, _norte(intake_world)["id"]) as cur:
        with pytest.raises(psycopg.errors.RaiseException, match="ciclo"), conn.transaction():
            cur.execute(
                """insert into dependency (workspace_id, origen_task_id, destino_task_id)
                   values (%s, %s, %s)""", (_norte(intake_world)["id"], tornillos, estante))
    conn.commit()
    assert len(_esperas(conn)) == 1


def test_si_salta_la_guarda_del_ciclo_la_carga_se_rechaza_con_su_motivo(
        conn, intake_world, sesion):
    """Al cargar, la tarea es nueva y nadie la espera: una sola espera no puede cerrar un
    círculo. Si la guarda de la base salta igual (acá se la hace saltar siempre, sólo dentro de
    esta transacción), la carga no deja nada y lo dice como un rechazo más."""
    estante = _cargada(conn, sesion, intake_world, titulo="Colocar el estante")
    antes = (_contar(conn, "task"), _contar(conn, "task_state_event"),
             _contar(conn, "carga_de_tarea"), _contar(conn, "audit_log"))
    with conn.transaction(force_rollback=True):
        with conn.cursor() as cur:
            cur.execute("""create or replace function leda.evitar_ciclo_dependencia()
                           returns trigger as $$
                           begin raise exception 'La dependencia crea un ciclo.'; end
                           $$ language plpgsql""")
        with sin_espacio(conn) as cur:
            r = _llamar(cur, sesion, _datos(intake_world, espera=estante))
    assert _errores(r) == {("espera", "haria_un_ciclo")}
    assert (_contar(conn, "task"), _contar(conn, "task_state_event"),
            _contar(conn, "carga_de_tarea"), _contar(conn, "audit_log")) == antes
    assert _esperas(conn) == []


# --- La regla de la mecánica §4 -------------------------------------------------------------

def test_la_que_espera_no_arranca_hasta_que_la_otra_este_terminada(conn, intake_world, sesion):
    estante = _cargada(conn, sesion, intake_world, titulo="Colocar el estante")
    tornillos = _cargada(conn, sesion, intake_world, titulo="Comprar los tornillos",
                         espera=estante)
    arrancar = """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                actor_kind)
                  values (%s, 'asignada', 'en_curso', 'persona')"""
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.RaiseException, match="en curso"), conn.transaction():
            cur.execute(arrancar, (tornillos,))
    conn.commit()
    assert _fila(conn, "select estado from task where id = %s", tornillos)["estado"] == "asignada"
    _terminar(conn, intake_world, estante)
    with admin(conn) as cur:
        cur.execute(arrancar, (tornillos,))
    conn.commit()
    assert _fila(conn, "select estado from task where id = %s", tornillos)["estado"] == "en_curso"


# --- Las opciones ---------------------------------------------------------------------------

def _opciones(conn, sesion: str, espacio_id: str) -> dict:
    with sin_espacio(conn) as cur:
        cur.execute("select opciones_de_la_carga(%s, %s, now()) as r", (_hash(sesion), espacio_id))
        r = cur.fetchone()["r"]
    conn.commit()
    return r


def test_las_opciones_ofrecen_para_esperar_solo_las_tareas_abiertas_del_espacio(
        conn, intake_world, sesion):
    norte = _norte(intake_world)
    abierta = _cargada(conn, sesion, intake_world, titulo="Colocar el estante")
    terminada = _cargada(conn, sesion, intake_world, titulo="Pintar la pared")
    _terminar(conn, intake_world, terminada)
    cancelada = _cargada(conn, sesion, intake_world, titulo="Limpiar el piso")
    _cancelar(conn, cancelada)
    propuesta = _propuesta(conn, intake_world)
    del_oeste = _cargada(conn, sesion, intake_world, **_en_el_oeste(intake_world))
    r = _opciones(conn, sesion, norte["id"])
    assert r["ok"] is True
    assert [t["id"] for t in r["tareas"]] == [abierta]
    (tarea,) = r["tareas"]
    assert tarea["titulo"] == "Colocar el estante"
    assert tarea["responsable"] == "Sam North 1"
    assert tarea["objetivo"] == "Reduce service delay 1"
    assert tarea["estado"] == "asignada"
    texto = str(r)
    for ajena in (terminada, cancelada, propuesta, del_oeste):
        assert ajena not in texto


# --- La entrada HTTP ------------------------------------------------------------------------

def test_cargar_por_la_api_con_una_espera(web, conn, intake_world, administradora):
    from leda import web_app

    norte = _norte(intake_world)
    camino = f"/app/admin/api/espacios/{norte['id']}/tareas"
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = navegador.post(camino, json=_cuerpo(intake_world, titulo="Colocar el estante"))
    assert r.status_code == 201, r.text
    estante = r.json()["task_id"]
    opciones = navegador.get(f"/app/admin/api/espacios/{norte['id']}/opciones").json()
    assert [t["id"] for t in opciones["tareas"]] == [estante]

    r = navegador.post(camino, json=_cuerpo(intake_world, espera_id=estante))
    assert r.status_code == 201, r.text
    assert _esperas(conn)[0]["origen"] == estante

    r = navegador.post(camino, json=_cuerpo(intake_world, espera_id="no-es-un-id"))
    assert r.status_code == 422
    assert {(e["campo"], e["motivo"]) for e in r.json()["errores"]} == {
        ("espera", "mal_formada")}

    _cancelar(conn, estante)
    r = navegador.post(camino, json=_cuerpo(intake_world, espera_id=estante))
    assert r.status_code == 422
    (error,) = r.json()["errores"]
    assert (error["campo"], error["motivo"]) == ("espera", "esta_cerrada")
    assert error["texto"] == web_app.TEXTOS_DE_LA_CARGA[("espera", "esta_cerrada")]
    assert len(_esperas(conn)) == 1


def test_cada_rechazo_de_la_espera_tiene_su_texto_humano():
    from leda import web_app

    for motivo in ("no_existe", "esta_cerrada", "no_esta_comprometida", "haria_un_ciclo"):
        texto = web_app.TEXTOS_DE_LA_CARGA[("espera", motivo)]
        for de_la_cocina in ("ciclo de dependencia", "dependency", "sql", "trigger"):
            assert de_la_cocina not in texto.lower()
