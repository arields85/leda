"""La ayuda de la IA al cargar, por la puerta de administración (ADR 0023, punto 4; porción J2 de
`odd/tasks/plataforma-jerarquias.md`): las garantías en la base y en la entrada HTTP, con una IA
de mentira (nunca la real).

- **La puerta:** sólo una sesión de administración vigente (ni la del equipo ni ninguna), con la
  protección contra otros sitios de la carga; un espacio que no existe, 404.
- **El aislamiento:** un dato de otro espacio se rechaza sin llamar a la IA, y la IA no recibe
  nada de otro espacio (ni los nombres del equipo: devuelve las palabras con que se nombró a la
  persona, y el código la busca en ese espacio, con sus apodos).
- **Sólo lo vacío:** Leda propone lo que el formulario no tiene; lo escrito no se pide ni vuelve.
- **Nunca en silencio:** si la IA no responde, 503 con un texto humano y un incidente
  (`ayuda_al_cargar`), y nada cambia.
- **El criterio** (J2-13 y J2-17): lo escribe la IA entero, con sus palabras, y se juzga por su
  sentido fuera del candado, ya con la evidencia del área de quien la hace; llega tal cual, sin
  que el código le agregue nada. Si no vale, el que escribe el juicio; si el juicio no responde,
  el de reserva (con la evidencia del área) y un incidente, nunca el de la IA sin juzgar.
- **La auditoría** (`proponer_al_cargar`): quién pidió, qué se pidió, qué se propuso y qué no, con
  la huella de cada texto propuesto y nunca el texto.
- **El candado de la web no espera a la IA:** la llamada se hace fuera de él.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from leda.db import admin
from tests.garantias.test_carga_de_tareas import (  # noqa: F401
    _cargar, _contar, _fila, _navegador_de_administracion, _navegador_del_equipo, _norte,
    _persona, administradora, sesion, web)
from tests.test_ayuda_al_cargar import (CIRCULAR_UPS, CRITERIO_DEL_EJEMPLO, DEL_JUICIO, EJEMPLO,
                                        RESULTADO_DEL_EJEMPLO, RESULTADO_UPS, TITULO_UPS, UPS,
                                        IADeLaCarga, juez, juzga_que_si)

TEXTO_SI_LA_IA_FALLA = ("Leda no pudo completar ahora. Lo que escribiste sigue acá: completalo "
                        "vos o probá de nuevo en un rato.")


def _camino(espacio_id: str) -> str:
    return f"/app/admin/api/espacios/{espacio_id}/ayuda"


def _viernes_real() -> str:
    """El próximo viernes después de hoy (la web mira el reloj de verdad)."""
    dia = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).date() + timedelta(days=1)
    while dia.weekday() != 4:
        dia += timedelta(days=1)
    return dia.isoformat()


def _respuesta(**cambios) -> dict:
    respuesta = {
        "titulo": "Colgar el estante del módem en la sala",
        "descripcion": "Colgar el estante del módem en la sala. Hacen falta 12 tornillos de 8 mm.",
        "criterio": CRITERIO_DEL_EJEMPLO,
        "resultado": RESULTADO_DEL_EJEMPLO,
        "responsable": "lucas",
        "espera": "T1",
        "objetivo": "O3",
        "fecha": _viernes_real(),
        "como_dijo_la_fecha": "para el viernes",
    }
    respuesta.update(cambios)
    return {k: v for k, v in respuesta.items() if v is not None}


@pytest.fixture
def ia(monkeypatch):
    """La IA de mentira del espacio: cada prueba le carga sus respuestas; el juicio de la manera
    de comprobarla dice que sí, salvo que la prueba lo cambie."""
    from leda import web_app

    falsa = IADeLaCarga(juzga=juzga_que_si)
    monkeypatch.setattr(web_app, "_ia_de_la_ayuda", lambda conn, espacio: falsa)
    return falsa


@pytest.fixture
def con_lucas(conn, intake_world, sesion):
    """North Lab con "lucas" como apodo de Sam North y una tarea abierta para esperar: "Cablear el
    tablero de la maquina 3", cargada como se carga."""
    norte = _norte(intake_world)
    with admin(conn) as cur:
        cur.execute(
            """insert into apodo (workspace_id, membership_id, apodo, ensenado_por_app_user_id,
                                  canal, at)
               values (%s, %s, 'lucas', %s, 'plataforma', now())""",
            (norte["id"], _persona(intake_world, "Sam North"),
             norte["people"]["Morgan Hale"]["app_user_id"]))
    conn.commit()
    r = _cargar(conn, sesion, intake_world, titulo="Cablear el tablero de la maquina 3")
    assert r["ok"] is True, r
    return r["task_id"]


def _pedir(navegador, espacio_id: str, **cuerpo):
    datos = {"texto": EJEMPLO, "objetivo_id": "", "titulo": "", "descripcion": "",
             "responsable_id": "", "fecha": "", "espera_id": "", "criterio": ""}
    datos.update(cuerpo)
    return navegador.post(_camino(espacio_id), json=datos)


# --- El ejemplo del usuario, de punta a punta -------------------------------------------------

def test_el_ejemplo_del_usuario_propone_cada_dato_de_su_espacio(web, conn, intake_world,
                                                               administradora, con_lucas, ia):
    norte = _norte(intake_world)
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta())
    r = _pedir(navegador, norte["id"])
    assert r.status_code == 200, r.text
    assert r.headers["cache-control"] == "no-store"
    propuesta = r.json()["propuesta"]
    assert propuesta == {
        "titulo": "Colgar el estante del módem en la sala",
        "descripcion": "Colgar el estante del módem en la sala. Hacen falta 12 tornillos de 8 mm.",
        "criterio": CRITERIO_DEL_EJEMPLO,
        # "lucas" es el apodo de Sam North, buscado en su espacio.
        "responsable_id": _persona(intake_world, "Sam North"),
        "espera_id": con_lucas,
        # El objetivo de la tarea que espera.
        "objetivo_id": norte["objectives"][0],
        "fecha": _viernes_real(),
    }
    assert r.json()["avisos"] == [] and r.json()["elegir"] == []
    # Nada se cargó: proponer no es cargar.
    assert _contar(conn, "task") == 1


def test_la_ia_no_recibe_nada_de_otro_espacio(web, conn, intake_world, administradora, sesion,
                                             con_lucas, ia):
    """J2-18: la IA recibe el equipo de este espacio (para proponer quién la hace), y nada de
    otro: ni sus tareas, ni sus objetivos, ni su gente."""
    oeste = intake_world["west-studio"]
    _cargar(conn, sesion, intake_world, espacio=oeste["id"], objetivo=oeste["objectives"][0],
            responsable=_persona(intake_world, "Sam North", "west-studio"),
            decidio=_persona(intake_world, "Morgan Hale", "west-studio"),
            titulo="Tarea secreta del oeste")
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta())
    assert _pedir(navegador, _norte(intake_world)["id"]).status_code == 200
    plano = json.dumps(ia.pedidos[0], ensure_ascii=False)
    assert "Tarea secreta del oeste" not in plano
    for persona in oeste["people"].values():
        assert persona["name"] not in plano
    # Sólo quien puede hacerla: Morgan Hale no tiene quién la revise.
    assert [m["nombre"] for m in ia.entrada()["equipo"]] == [
        "Sam Noble 1", "Sam North 1", "Taylor Quinn 1"]
    for objetivo in oeste["objectives"]:
        assert objetivo not in plano
    entrada = ia.entrada()
    assert [t["titulo"] for t in entrada["tareas_abiertas"]] == ["Cablear el tablero de la maquina 3"]
    assert {o["titulo"] for o in entrada["objetivos"]} == {
        "Reduce service delay 1", "Raise delivery quality 1", "Expand regional coverage 1"}


def test_dos_personas_con_ese_nombre_se_muestran_para_elegir(web, conn, intake_world,
                                                            administradora, ia):
    """ADR 0020, decisión 3: "sam" es Sam North y Sam Noble; Leda no elige."""
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta(responsable="sam", espera=None))
    r = _pedir(navegador, _norte(intake_world)["id"], texto=EJEMPLO.replace("lucas", "sam"))
    assert r.status_code == 200, r.text
    assert "responsable_id" not in r.json()["propuesta"]
    elegir = {e["membership_id"]: e for e in r.json()["elegir"]}
    assert set(elegir) == {_persona(intake_world, "Sam North"), _persona(intake_world, "Sam Noble")}
    assert {e["area"] for e in elegir.values()} == {"Field Services", "Quality Guild"}
    (aviso,) = [a for a in r.json()["avisos"] if a["campo"] == "responsable"]
    assert "elegí quién la hace" in aviso["texto"]


def test_alguien_de_otro_espacio_no_se_encuentra(web, conn, intake_world, administradora, ia):
    """"Sam North 2" es del oeste: en North Lab no hay nadie con "north 2"."""
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta(responsable="north 2", espera=None))
    r = _pedir(navegador, _norte(intake_world)["id"],
               texto=EJEMPLO.replace("lucas", "north 2"))
    assert "responsable_id" not in r.json()["propuesta"]
    assert {"campo": "responsable", "motivo": "no_encontrado",
            "texto": "No encontré a «north 2» en el equipo; elegí quién la hace."} \
        in r.json()["avisos"]


def test_una_fecha_que_nadie_dijo_no_se_propone(web, conn, intake_world, administradora, ia):
    """Constitución §4 (revisión `review-6a44e26466b95395`): "12 tornillos" no es el 12, y un día
    que la IA calculó distinto del que dicen las palabras de la persona tampoco vale."""
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta(espera=None, como_dijo_la_fecha="12"))
    r = _pedir(navegador, _norte(intake_world)["id"])
    assert r.status_code == 200, r.text
    assert "fecha" not in r.json()["propuesta"]
    assert {"campo": "fecha", "motivo": "no_entendida",
            "texto": 'No puse la fecha: no entendí qué día es "12"; elegila en el calendario.'}         in r.json()["avisos"]
    ia.respuestas.append(_respuesta(espera=None, como_dijo_la_fecha="para el lunes"))
    r = _pedir(navegador, _norte(intake_world)["id"])
    assert "fecha" not in r.json()["propuesta"]
    assert [a["motivo"] for a in r.json()["avisos"] if a["campo"] == "fecha"] == ["no_dicha"]


def test_un_rango_no_es_una_fecha(web, conn, intake_world, administradora, ia):
    """Revisión `review-6eec478c3a4ddc11`: "del 10-12" es del 10 al 12, no el 10 de diciembre."""
    navegador = _navegador_de_administracion(web, conn, administradora)
    texto = EJEMPLO.replace("para el viernes", "del 10-12")
    ia.respuestas.append(_respuesta(espera=None, fecha="2026-12-10", como_dijo_la_fecha="del 10-12"))
    r = _pedir(navegador, _norte(intake_world)["id"], texto=texto)
    assert r.status_code == 200, r.text
    assert "fecha" not in r.json()["propuesta"]
    assert [a["motivo"] for a in r.json()["avisos"] if a["campo"] == "fecha"] == ["no_entendida"]


def test_antes_de_un_dia_es_el_dia_habil_anterior_del_espacio(web, conn, intake_world,
                                                             administradora, ia):
    """El usuario (2026-10-13): "antes del jueves" es el miércoles, no el jueves; el día hábil
    anterior lo da el calendario del espacio en la base (`es_dia_habil`)."""
    norte = _norte(intake_world)
    hoy = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).date()
    viernes = hoy + timedelta(days=7 - hoy.weekday() + 4)       # el de la semana que viene
    anterior = viernes - timedelta(days=1)
    with admin(conn) as cur:
        while True:
            cur.execute("select es_dia_habil(%s, %s) as habil", (norte["id"], anterior))
            if cur.fetchone()["habil"]:
                break
            anterior -= timedelta(days=1)
    navegador = _navegador_de_administracion(web, conn, administradora)
    texto = EJEMPLO.replace("para el viernes", "antes del viernes de la semana que viene")
    ia.respuestas.append(_respuesta(espera=None, fecha=anterior.isoformat(),
                                    como_dijo_la_fecha="antes del viernes de la semana que viene"))
    r = _pedir(navegador, norte["id"], texto=texto)
    assert r.status_code == 200, r.text
    assert r.json()["propuesta"]["fecha"] == anterior.isoformat()
    # El viernes mismo no vale: la persona dijo "antes".
    ia.respuestas.append(_respuesta(espera=None, fecha=viernes.isoformat(),
                                    como_dijo_la_fecha="antes del viernes de la semana que viene"))
    r = _pedir(navegador, norte["id"], texto=texto)
    assert "fecha" not in r.json()["propuesta"]


# --- Sólo lo vacío ----------------------------------------------------------------------------

def test_lo_escrito_no_se_pide_ni_vuelve(web, conn, intake_world, administradora, con_lucas, ia):
    norte = _norte(intake_world)
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta())
    r = _pedir(navegador, norte["id"], titulo="Poner el estante",
               responsable_id=_persona(intake_world, "Sam Noble"))
    assert r.status_code == 200, r.text
    assert "titulo" not in r.json()["propuesta"]
    assert "responsable_id" not in r.json()["propuesta"]
    # J2-18 y J2-19: con el criterio por pedir y nada tildado, también la evidencia.
    assert set(ia.entrada()["pide"]) == {"descripcion", "criterio", "espera", "objetivo", "fecha",
                                         "evidencia"}


def test_sin_texto_o_sin_nada_vacio_no_se_llama_a_la_ia(web, conn, intake_world, administradora,
                                                       ia):
    norte = _norte(intake_world)
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _pedir(navegador, norte["id"], texto="   ")
    assert r.status_code == 422
    assert r.json()["errores"][0]["campo"] == "texto"
    assert r.json()["errores"][0]["texto"].startswith("Contame primero")
    lleno = {"objetivo_id": norte["objectives"][0], "titulo": "x", "descripcion": "x",
             "responsable_id": _persona(intake_world, "Sam North"), "fecha": _viernes_real(),
             "espera_id": "", "criterio": "x"}
    # La espera es opcional: con todo lo demás escrito y sin tareas para esperar, no queda nada.
    r = _pedir(navegador, norte["id"], **lleno)
    assert r.status_code == 422
    assert (r.json()["errores"][0]["campo"], r.json()["errores"][0]["motivo"]) == (
        "ayuda", "nada_que_completar")
    r = _pedir(navegador, norte["id"], texto="x" * 1001)
    assert (r.json()["errores"][0]["campo"], r.json()["errores"][0]["motivo"]) == (
        "texto", "demasiado_largo")
    assert ia.pedidos == []


def test_un_dato_de_otro_espacio_se_rechaza_sin_llamar_a_la_ia(web, conn, intake_world,
                                                              administradora, ia):
    norte, oeste = _norte(intake_world), intake_world["west-studio"]
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _pedir(navegador, norte["id"], objetivo_id=oeste["objectives"][0],
               responsable_id=_persona(intake_world, "Sam North", "west-studio"),
               espera_id="00000000-0000-0000-0000-000000000000")
    assert r.status_code == 422, r.text
    assert {(e["campo"], e["motivo"]) for e in r.json()["errores"]} == {
        ("objetivo", "no_existe"), ("responsable", "no_es_integrante_activo"),
        ("espera", "no_existe")}
    r = _pedir(navegador, norte["id"], objetivo_id="no-es-un-id")
    assert ("objetivo", "mal_formado") in {(e["campo"], e["motivo"]) for e in r.json()["errores"]}
    assert ia.pedidos == []


# --- La puerta --------------------------------------------------------------------------------

def test_sin_sesion_de_administracion_no_hay_ayuda(web, conn, intake_world, administradora, ia):
    norte = _norte(intake_world)
    ia.respuestas.append(_respuesta())
    assert _pedir(web(), norte["id"]).status_code == 401
    equipo = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    assert _pedir(equipo, norte["id"]).status_code == 401
    navegador = _navegador_de_administracion(web, conn, administradora)
    for origen in ("https://otro.example", "null"):
        r = navegador.post(_camino(norte["id"]), json={"texto": EJEMPLO},
                           headers={"origin": origen})
        assert r.status_code == 403
    r = navegador.post(_camino(norte["id"]), content="texto=x",
                       headers={"content-type": "application/x-www-form-urlencoded"})
    assert r.status_code == 415
    r = navegador.post(_camino(norte["id"]), content=json.dumps({"texto": "x" * 70000}),
                       headers={"content-type": "application/json"})
    assert r.status_code == 413
    assert _pedir(navegador, "00000000-0000-0000-0000-000000000000").status_code == 404
    assert _pedir(navegador, "no-es-un-id").status_code == 404
    assert ia.pedidos == []
    assert _contar(conn, "audit_log", "accion = 'proponer_al_cargar'") == 0


def test_una_sesion_cortada_mientras_responde_la_ia_no_recibe_nada(web, conn, intake_world,
                                                                  administradora, ia):
    from tests.garantias.test_carga_de_tareas import _revocar

    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta(espera=None))
    ia.al_llamar = lambda: _revocar(conn, administradora)
    assert _pedir(navegador, _norte(intake_world)["id"]).status_code == 401
    assert _contar(conn, "audit_log", "accion = 'proponer_al_cargar'") == 0


# --- La IA que no responde --------------------------------------------------------------------

def test_si_la_ia_no_responde_queda_un_incidente_y_un_texto_humano(web, conn, intake_world,
                                                                  administradora, ia):
    from leda.motor.ia_real import PlazoAgotado

    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(PlazoAgotado(40))
    r = _pedir(navegador, _norte(intake_world)["id"])
    assert r.status_code == 503
    assert r.json() == {"error": "sin_ayuda", "texto": TEXTO_SI_LA_IA_FALLA}
    incidente = _fila(conn, "select * from incident where etapa = 'ayuda_al_cargar'")
    assert incidente is not None
    assert incidente["workspace_id"] is not None
    assert str(incidente["workspace_id"]) == _norte(intake_world)["id"]
    assert "PlazoAgotado" in incidente["referencia_cruda"]
    assert EJEMPLO not in (incidente["resumen_sanitizado"] or "")
    auditoria = _fila(conn, "select detalle from audit_log where accion = 'proponer_al_cargar'")
    assert auditoria["detalle"]["respondio"] is False
    assert _contar(conn, "task") == 0


def test_sin_ia_configurada_tambien(web, conn, intake_world, administradora, monkeypatch):
    from leda import web_app
    from leda.motor.recibir import IANoConfigurada

    monkeypatch.setattr(web_app, "_ia_de_la_ayuda",
                        lambda conn, espacio: IANoConfigurada("No hay modelo configurado."))
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _pedir(navegador, _norte(intake_world)["id"])
    assert r.status_code == 503 and r.json()["texto"] == TEXTO_SI_LA_IA_FALLA
    assert _contar(conn, "incident", "etapa = 'ayuda_al_cargar'") == 1


def test_la_web_no_espera_a_la_ia_con_su_candado(web, conn, intake_world, administradora, ia):
    from leda import web_app

    navegador = _navegador_de_administracion(web, conn, administradora)
    candado = []
    ia.al_llamar = lambda: candado.append(web_app._WEB.locked())
    ia.respuestas.append(_respuesta(espera=None))
    assert _pedir(navegador, _norte(intake_world)["id"]).status_code == 200
    # La propuesta y el juicio de la manera de comprobarla, los dos sin el candado.
    assert candado == [False, False]


# --- La auditoría -----------------------------------------------------------------------------

def test_la_auditoria_guarda_lo_propuesto_con_su_huella_y_sin_el_texto(
        web, conn, intake_world, administradora, con_lucas, ia):
    norte = _norte(intake_world)
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta(titulo="Colgar el estante con 14 tornillos"))
    r = _pedir(navegador, norte["id"])
    assert r.status_code == 200
    fila = _fila(conn, """select workspace_id, actor_app_user_id, actor_kind, sujeto_tipo,
                                 sujeto_id, detalle, pack_hash, nucleo_hash
                            from audit_log where accion = 'proponer_al_cargar'""")
    assert str(fila["workspace_id"]) == norte["id"]
    assert str(fila["actor_app_user_id"]) == administradora
    assert (fila["actor_kind"], fila["sujeto_tipo"]) == ("persona", "workspace")
    assert fila["pack_hash"] == "hash-0" and fila["nucleo_hash"]
    detalle = fila["detalle"]
    assert detalle["origen"] == "web" and detalle["respondio"] is True
    assert detalle["ia"] == "de-mentira"
    assert detalle["sesion_de_administracion_id"]
    assert set(detalle["pide"]) == {"titulo", "descripcion", "criterio", "responsable_id",
                                    "espera_id", "objetivo_id", "fecha"}
    assert set(detalle["propuestos"]) == {"descripcion", "criterio", "responsable_id",
                                          "espera_id", "objetivo_id", "fecha"}
    assert {"campo": "titulo", "motivo": "dato"} in detalle["descartados"]
    criterio = r.json()["propuesta"]["criterio"]
    assert detalle["huellas"]["criterio"] == hashlib.sha256(criterio.encode()).hexdigest()
    assert detalle["responsable_membership_id"] == _persona(intake_world, "Sam North")
    assert detalle["espera_task_id"] == con_lucas
    plano = json.dumps(detalle, ensure_ascii=False)
    for texto in (criterio, EJEMPLO, "Colgar el estante"):
        assert texto not in plano


# --- El criterio: con las palabras de Leda y juzgado por su sentido (J2-13 y J2-17) --------------

def _auditoria(conn) -> dict:
    return _fila(conn, """select detalle from audit_log where accion = 'proponer_al_cargar'
                           order by at desc limit 1""")["detalle"]


def test_el_criterio_de_la_ia_llega_tal_cual_sin_plantilla(web, conn, intake_world,
                                                          administradora, con_lucas, ia):
    """J2-17: la IA escribe el criterio entero y el juicio, con la evidencia que propone Leda para
    la tarea de Sam North ("lucas", Field Services; J2-19: "test record", E1), dice que sirve:
    llega tal cual, sin que el código le pegue nada."""
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta(espera=None, evidencia="E1"))
    r = _pedir(navegador, _norte(intake_world)["id"])
    assert r.status_code == 200, r.text
    criterio = r.json()["propuesta"]["criterio"]
    assert criterio == CRITERIO_DEL_EJEMPLO
    assert "Se comprueba con lo que pide el área" not in criterio
    juicio = json.loads(next(m["content"] for m in ia.pedidos[1]["messages"]
                             if m["role"] == "user"))
    assert juicio["evidencia_que_pide_el_area"] == ["test record"]
    assert _auditoria(conn)["criterio_de"] == "ia"


def test_el_ups_circular_del_usuario_se_reemplaza_por_el_del_juicio(web, conn, intake_world,
                                                                    administradora, ia):
    """La prueba del usuario: "el tano" no es nadie del espacio, la IA inventó una comprobación
    circular con sinónimos y el juicio por el sentido la rechaza; sin evidencia de un área, Leda
    igual propone el criterio que escribió el juicio (J2-17)."""
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.juzga = juez(CIRCULAR_UPS, propone=DEL_JUICIO)
    ia.respuestas.append({"titulo": TITULO_UPS, "criterio": CIRCULAR_UPS,
                          "resultado": RESULTADO_UPS, "responsable": "el tano"})
    r = _pedir(navegador, _norte(intake_world)["id"], texto=UPS)
    assert r.status_code == 200, r.text
    assert r.json()["propuesta"]["criterio"] == DEL_JUICIO
    avisos = {a["campo"]: a["texto"] for a in r.json()["avisos"]}
    assert "criterio" not in avisos
    assert avisos["responsable"] == "No encontré a «el tano» en el equipo; elegí quién la hace."
    assert len(ia.pedidos) == 2
    assert _auditoria(conn)["juicio_del_criterio"] == "sin_comprobacion"
    assert _auditoria(conn)["criterio_de"] == "juicio"
    assert _contar(conn, "incident", "etapa = 'ayuda_al_cargar'") == 0


def test_j2_26_un_criterio_que_nombra_a_alguien_del_espacio_no_se_propone(
        web, conn, intake_world, administradora, con_lucas, ia):
    """J2-26: "lucas" es el apodo de Sam North en este espacio (de la base, no de lo que nombró
    la persona): el criterio de la IA que lo dice no se propone; el del juicio, sin nombres, sí.
    La auditoría lo dice, sin incidente (hubo un criterio para proponer)."""
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.juzga = lambda entrada: {"dice_como_se_comprueba": False, "como_se_comprueba": "",
                                "criterio": DEL_JUICIO}
    ia.respuestas.append(_respuesta(
        responsable=None, espera=None,
        criterio="El estante del módem queda colgado y lucas lo deja firme en la sala."))
    r = _pedir(navegador, _norte(intake_world)["id"])
    assert r.status_code == 200, r.text
    assert r.json()["propuesta"]["criterio"] == DEL_JUICIO
    assert {"campo": "criterio", "motivo": "nombra_a_alguien"} in _auditoria(conn)["descartados"]
    assert _auditoria(conn)["criterio_de"] == "juicio"
    assert _contar(conn, "incident", "etapa = 'ayuda_al_cargar'") == 0


def test_j2_26_si_tampoco_el_del_juicio_sirve_se_dice_y_queda_un_incidente(
        web, conn, intake_world, administradora, con_lucas, ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.juzga = lambda entrada: {"dice_como_se_comprueba": False, "como_se_comprueba": "",
                                "criterio": "Sam deja el estante del módem colgado y firme."}
    ia.respuestas.append(_respuesta(
        responsable=None, espera=None,
        criterio="Sam North cuelga el estante del módem en la sala y lo deja firme."))
    r = _pedir(navegador, _norte(intake_world)["id"])
    assert r.status_code == 200, r.text
    assert "criterio" not in r.json()["propuesta"]
    avisos = {a["campo"]: a["texto"] for a in r.json()["avisos"]}
    assert avisos["criterio"] == (
        "No pude proponer el criterio con lo que escribiste; contame cómo se comprueba.")
    incidente = _fila(conn, "select * from incident where etapa = 'ayuda_al_cargar'")
    assert incidente is not None and "nombra_a_alguien" in incidente["referencia_cruda"]
    assert "Sam" not in incidente["referencia_cruda"]


def test_si_el_juicio_no_responde_al_proponer_queda_un_incidente(web, conn, intake_world,
                                                                  administradora, con_lucas, ia):
    from leda.motor.ia_real import PlazoAgotado

    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.juzga = lambda entrada: PlazoAgotado(40)
    ia.respuestas.append(_respuesta(espera=None, evidencia="E1"))
    r = _pedir(navegador, _norte(intake_world)["id"])
    assert r.status_code == 200, r.text
    # El criterio de la IA no se propone sin juzgar: vale el de reserva, con la evidencia que
    # propuso Leda.
    assert r.json()["propuesta"]["criterio"] == (
        f"{RESULTADO_DEL_EJEMPLO}. Se comprueba con lo que pide el área: test record.")
    incidente = _fila(conn, "select * from incident where etapa = 'ayuda_al_cargar'")
    assert incidente is not None and "PlazoAgotado" in incidente["referencia_cruda"]
    assert _auditoria(conn)["juicio_del_criterio"] == "sin_revisar"
    assert _auditoria(conn)["criterio_de"] == "reserva"


def test_una_sesion_cortada_antes_del_juicio_no_recibe_nada(web, conn, intake_world,
                                                            administradora, con_lucas, ia):
    """Entre la propuesta y el juicio, el código revisa con el candado y la sesión otra vez."""
    from tests.garantias.test_carga_de_tareas import _revocar

    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta(espera=None))
    llamadas = []

    def al_llamar():
        llamadas.append(1)
        if len(llamadas) == 1:
            _revocar(conn, administradora)
    ia.al_llamar = al_llamar
    assert _pedir(navegador, _norte(intake_world)["id"]).status_code == 401
    assert len(llamadas) == 1
    assert _contar(conn, "audit_log", "accion = 'proponer_al_cargar'") == 0


# --- J2-18: Leda completa todo lo que puede ---------------------------------------------------------

def _con_fotos(conn, intake_world) -> None:
    """El área de Sam North (field) conoce también una foto, además de lo que pide."""
    with admin(conn) as cur:
        cur.execute("""update task_evidence_policy
                          set tipos = '{"foto": {"clases": ["imagen"], "en_palabras": "una foto"}}'
                        where area_id = %s""", (_norte(intake_world)["areas"]["field"],))
    conn.commit()


def test_leda_propone_quien_la_hace_y_la_evidencia_aunque_no_se_dijo(web, conn, intake_world,
                                                                    administradora, ia):
    _con_fotos(conn, intake_world)
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta(responsable=None, espera=None, quien_la_hace="P2",
                                    evidencia="E1"))
    r = _pedir(navegador, _norte(intake_world)["id"],
               texto=EJEMPLO.replace("que lo haga lucas ", ""))
    assert r.status_code == 200, r.text
    propuesta = r.json()["propuesta"]
    assert propuesta["responsable_id"] == _persona(intake_world, "Sam North")
    assert propuesta["evidencia"] == ["foto"]
    juicio = json.loads(next(m["content"] for m in ia.pedidos[1]["messages"]
                             if m["role"] == "user"))
    # J2-19: el criterio se juzga con exactamente la evidencia que propuso Leda, sin la del área.
    assert juicio["evidencia_que_pide_el_area"] == ["una foto"]
    detalle = _auditoria(conn)
    assert detalle["responsable_de"] == "leda"
    assert detalle["evidencia_propuesta"] == ["foto"]
    assert detalle["responsable_membership_id"] == _persona(intake_world, "Sam North")


def test_quien_no_es_del_equipo_no_se_reemplaza_por_otro(web, conn, intake_world,
                                                         administradora, ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta(responsable="pepe", espera=None, quien_la_hace="P2"))
    r = _pedir(navegador, _norte(intake_world)["id"],
               texto=EJEMPLO.replace("lucas", "pepe"))
    assert r.status_code == 200, r.text
    assert "responsable_id" not in r.json()["propuesta"]
    avisos = {a["campo"]: a["texto"] for a in r.json()["avisos"]}
    assert avisos["responsable"] == "No encontré a «pepe» en el equipo; elegí quién la hace."


def test_la_evidencia_que_ya_tildo_la_persona_no_se_vuelve_a_proponer(
        web, conn, intake_world, administradora, ia):
    _con_fotos(conn, intake_world)
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta(responsable=None, espera=None, evidencia="E1"))
    r = _pedir(navegador, _norte(intake_world)["id"],
               responsable_id=_persona(intake_world, "Sam North"),
               evidencia=["test record", "foto"])
    assert r.status_code == 200, r.text
    assert "evidencia" not in r.json()["propuesta"]
    assert "evidencia" not in ia.entrada()["pide"]
    assert ia.entrada()["ya_escrito"]["evidencia_elegida"] == ["test record", "una foto"]


def test_una_evidencia_mal_formada_se_rechaza_sin_llamar_a_la_ia(web, conn, intake_world,
                                                                administradora, ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _pedir(navegador, _norte(intake_world)["id"], evidencia="foto")
    assert r.status_code == 422
    assert ("evidencia", "mal_formada") in {(e["campo"], e["motivo"])
                                            for e in r.json()["errores"]}
    assert ia.pedidos == []


def test_una_ia_de_la_ayuda_que_no_se_puede_preparar_deja_un_incidente(
        web, conn, intake_world, administradora, monkeypatch):
    from leda import web_app

    def rota(conn, espacio):
        raise RuntimeError("la configuración de la IA no se puede leer")
    monkeypatch.setattr(web_app, "_ia_de_la_ayuda", rota)
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _pedir(navegador, _norte(intake_world)["id"])
    assert r.status_code == 503 and r.json()["texto"] == TEXTO_SI_LA_IA_FALLA
    incidente = _fila(conn, "select * from incident where etapa = 'ayuda_al_cargar'")
    assert incidente is not None and "RuntimeError" in incidente["referencia_cruda"]


# --- J2-19: la evidencia tildada, revisada antes de usarla ------------------------------------

@pytest.mark.parametrize("quien", [None, "Sam North"])
def test_una_evidencia_que_el_area_no_conoce_se_rechaza_sin_llamar_a_la_ia(
        web, conn, intake_world, administradora, ia, quien):
    """Advertencia de RDD de la J2-18 (`R3-evidencia-escrita-sin-validar`): la evidencia que manda
    el formulario se usaba tal cual, también para decidir que la persona ya eligió. Ahora se revisa
    como en la carga: cada tipo, de los que conoce el área de quien la hace (sin ella, de los del
    pack del espacio)."""
    navegador = _navegador_de_administracion(web, conn, administradora)
    cuerpo = {"evidencia": ["test record", "inventada"]}
    if quien:
        cuerpo["responsable_id"] = _persona(intake_world, quien)
    r = _pedir(navegador, _norte(intake_world)["id"], **cuerpo)
    assert r.status_code == 422, r.text
    errores = {(e["campo"], e["motivo"]): e["texto"] for e in r.json()["errores"]}
    assert ("evidencia", "tipo_no_es_de_la_politica") in errores
    assert errores[("evidencia", "tipo_no_es_de_la_politica")]
    assert ia.pedidos == []


def test_la_evidencia_conocida_y_repetida_se_toma_una_vez(web, conn, intake_world,
                                                          administradora, ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta(responsable=None, espera=None))
    r = _pedir(navegador, _norte(intake_world)["id"],
               responsable_id=_persona(intake_world, "Sam North"),
               evidencia=["test record", "test record"])
    assert r.status_code == 200, r.text
    assert ia.entrada()["ya_escrito"]["evidencia_elegida"] == ["test record"]


# --- Advertencia de RDD de la J2-19: la evidencia, con el área de quien la hace -------------------
#
# `review-13a33db35d62cdde` (`R3-responsable-match`): la evidencia escrita se revisaba buscando a
# quien la hace y su área con una búsqueda propia, distinta de la que usa la propuesta. Ahora es la
# misma (`ayuda_al_cargar.quien_y_su_politica`): un tipo que conoce otra área del espacio pero no la
# de quien la hace se rechaza; sin quien la hace, vale cualquiera del pack del espacio.

def _plano_en_calidad(conn, intake_world) -> None:
    """El área de Sam Noble (calidad) conoce un plano; la de Sam North (campo), no."""
    with admin(conn) as cur:
        cur.execute("""update task_evidence_policy
                          set tipos = '{"plano": {"clases": ["archivo"], "en_palabras": "un plano"}}'
                        where area_id = %s""", (_norte(intake_world)["areas"]["quality"],))
    conn.commit()


@pytest.mark.parametrize("quien, vale", [("Sam North", False), ("Sam Noble", True), (None, True)])
def test_la_evidencia_escrita_se_revisa_con_el_area_de_quien_la_hace(
        web, conn, intake_world, administradora, ia, quien, vale):
    _plano_en_calidad(conn, intake_world)
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta(responsable=None, espera=None))
    cuerpo = {"evidencia": ["plano"]}
    if quien:
        cuerpo["responsable_id"] = _persona(intake_world, quien)
    r = _pedir(navegador, _norte(intake_world)["id"], **cuerpo)
    if vale:
        assert r.status_code == 200, r.text
        if quien:
            assert ia.entrada()["ya_escrito"]["evidencia_elegida"] == ["un plano"]
    else:
        assert r.status_code == 422, r.text
        assert ("evidencia", "tipo_no_es_de_la_politica") in {
            (e["campo"], e["motivo"]) for e in r.json()["errores"]}
        assert ia.pedidos == []


def test_la_evidencia_escrita_de_un_area_sin_politica_se_rechaza(web, conn, intake_world,
                                                                  administradora, ia):
    with admin(conn) as cur:
        cur.execute("delete from task_evidence_policy where area_id = %s",
                    (_norte(intake_world)["areas"]["field"],))
    conn.commit()
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _pedir(navegador, _norte(intake_world)["id"],
               responsable_id=_persona(intake_world, "Sam North"), evidencia=["test record"])
    assert r.status_code == 422, r.text
    assert ("evidencia", "sin_politica_del_area") in {(e["campo"], e["motivo"])
                                                      for e in r.json()["errores"]}
    assert ia.pedidos == []


def test_el_ayudante_del_pedido_controla_en_el_mismo_orden_que_antes(web, conn, intake_world,
                                                                    administradora, ia):
    """RDD de la J3-4 (R3-pedido-helper-equivalence): el ayudante compartido
    (`_el_pedido_que_escribe`, desde `21ccaca3`) controla en el mismo orden y con los mismos
    estados que el código de antes: otro sitio (403), JSON (415), la cookie (401) y el tamaño
    (413), en ese orden; con la sesión, un cuerpo que no se puede leer, o que no es un objeto, es
    un pedido sin datos (422, sin llamar a la IA)."""
    camino = _camino(_norte(intake_world)["id"])
    sin_cookie = web()
    formulario = {"content-type": "application/x-www-form-urlencoded"}
    grande = json.dumps({"texto": "x" * 70000})
    # Otro sitio, antes que el JSON y que la cookie.
    r = sin_cookie.post(camino, content="texto=x",
                        headers={**formulario, "origin": "https://otro.example"})
    assert (r.status_code, r.json()["error"]) == (403, "origen_no_verificado")
    # El JSON, antes que la cookie.
    r = sin_cookie.post(camino, content="texto=x", headers=formulario)
    assert (r.status_code, r.json()["error"]) == (415, "se_espera_json")
    # La cookie, antes que el tamaño.
    r = sin_cookie.post(camino, content=grande, headers={"content-type": "application/json"})
    assert r.status_code == 401
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = navegador.post(camino, content=grande, headers={"content-type": "application/json"})
    assert (r.status_code, r.json()["error"]) == (413, "demasiado_grande")
    for cuerpo in ("{no es json", "[1, 2]", "[" * 5000):
        r = navegador.post(camino, content=cuerpo,
                           headers={"content-type": "application/json; charset=utf-8"})
        assert r.status_code == 422, (cuerpo[:12], r.text)
        assert [(e["campo"], e["motivo"]) for e in r.json()["errores"]][:1] == [("texto", "falta")]
    assert ia.pedidos == []
