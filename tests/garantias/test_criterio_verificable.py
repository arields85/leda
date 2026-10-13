"""Un criterio que diga cómo se comprueba, al cargar por la puerta de administración (J2-9 de
`odd/tasks/plataforma-jerarquias.md`; mecánica §13: "¿el resultado esperado es concreto y
verificable?"): las garantías en la entrada HTTP, con una IA de mentira (nunca la real).

Lo que encontró el usuario en el celular (2026-10-13): un criterio circular, cuya parte de cómo se
comprueba sólo repetía el resultado, y una tarea cargada con el criterio "No se".

- **Lo que no dice nada se rechaza sin la IA:** "No se" no agrega nada al título (422, sin
  llamarla).
- **El juicio de la IA, la regla del código:** la IA copia la parte del criterio que dice cómo se
  comprueba; si vuelve vacía o no agrega nada al resto del criterio ni al título, 422 `criterio`
  / `sin_comprobacion`, "Contame cómo se sabe que está terminada.", y no se carga nada (la base
  igual dice lo demás, y la clave queda libre).
- **Si la IA no responde, ni se traba ni se finge:** se carga con un aviso que no bloquea y un
  incidente (`criterio_al_cargar`); una carga repetida no suma otro.
- **La IA, sólo con una sesión vigente y fuera del candado de la web;** una sesión cortada
  mientras respondía no carga nada.
"""

from __future__ import annotations

import pytest

from tests.garantias.test_carga_de_tareas import (  # noqa: F401
    _contar, _cuerpo, _fila, _navegador_de_administracion, _navegador_del_equipo, _norte,
    _revocar, administradora, web)
from tests.test_ayuda_al_cargar import (CIRCULAR, COMO_CIRCULAR, COMO_CONCRETO, CONCRETO,
                                        TITULO_PLC, IADeLaCarga)

TEXTO_SIN_COMPROBACION = "Contame cómo se sabe que está terminada."
TEXTO_SIN_REVISAR = ("No pude revisar el criterio ahora: la tarea quedó cargada con el criterio "
                     "como lo escribiste.")


@pytest.fixture
def ia(web, monkeypatch):
    """La IA de mentira del juicio del criterio: cada prueba le carga sus respuestas."""
    from leda import web_app

    falsa = IADeLaCarga()
    monkeypatch.setattr(web_app, "_ia_del_criterio", lambda conn, espacio: falsa)
    return falsa


def _camino(intake_world) -> str:
    return f"/app/admin/api/espacios/{_norte(intake_world)['id']}/tareas"


def _cargar(navegador, intake_world, **cambios):
    return navegador.post(_camino(intake_world),
                          json=_cuerpo(intake_world, titulo=TITULO_PLC, **cambios))


def _errores(r) -> set[tuple[str, str]]:
    return {(e["campo"], e["motivo"]) for e in r.json()["errores"]}


# --- El ejemplo del usuario -------------------------------------------------------------------

def test_el_criterio_circular_del_usuario_no_se_carga(web, conn, intake_world, administradora,
                                                     ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append({"como_se_comprueba": COMO_CIRCULAR})
    cuerpo = _cuerpo(intake_world, titulo=TITULO_PLC, criterio=CIRCULAR)
    r = navegador.post(_camino(intake_world), json=cuerpo)
    assert r.status_code == 422, r.text
    (error,) = r.json()["errores"]
    assert error == {"campo": "criterio", "motivo": "sin_comprobacion",
                     "texto": TEXTO_SIN_COMPROBACION}
    assert _contar(conn, "task") == 0 and _contar(conn, "carga_de_tarea") == 0
    assert len(ia.pedidos) == 1
    # La IA recibió sólo la tarea: el título, la descripción y el criterio.
    assert ia.entrada()["criterio"] == CIRCULAR
    # Corregido, la misma clave carga: el rechazo no la usó.
    ia.respuestas.append({"como_se_comprueba": COMO_CONCRETO})
    r = navegador.post(_camino(intake_world), json={**cuerpo, "criterio": CONCRETO})
    assert r.status_code == 201, r.text
    assert r.json()["avisos"] == []
    assert _contar(conn, "task") == 1


def test_no_se_no_se_carga_y_no_hace_falta_la_ia(web, conn, intake_world, administradora, ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _cargar(navegador, intake_world, criterio="No se")
    assert r.status_code == 422, r.text
    assert _errores(r) == {("criterio", "sin_comprobacion")}
    assert ia.pedidos == []
    assert _contar(conn, "task") == 0


def test_un_criterio_sin_comprobacion_segun_la_ia_no_se_carga(web, conn, intake_world,
                                                              administradora, ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append({"como_se_comprueba": ""})
    r = _cargar(navegador, intake_world, criterio="Hacerlo con cuidado y prolijidad")
    assert r.status_code == 422
    assert _errores(r) == {("criterio", "sin_comprobacion")}
    assert _contar(conn, "task") == 0


def test_el_rechazo_del_criterio_va_junto_con_lo_demas(web, conn, intake_world, administradora,
                                                       ia):
    """Todo junto, como siempre: lo que dice la base, sin repetir el criterio ni pedir la
    clave."""
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append({"como_se_comprueba": COMO_CIRCULAR})
    r = _cargar(navegador, intake_world, criterio=CIRCULAR, decidio_id="")
    assert r.status_code == 422
    assert _errores(r) == {("criterio", "sin_comprobacion"), ("decidio", "falta")}
    assert _contar(conn, "task") == 0


def test_un_criterio_con_una_comprobacion_concreta_se_carga(web, conn, intake_world,
                                                            administradora, ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append({"como_se_comprueba": COMO_CONCRETO})
    r = _cargar(navegador, intake_world, criterio=CONCRETO)
    assert r.status_code == 201, r.text
    assert r.json()["avisos"] == []
    assert _contar(conn, "incident", "etapa = 'criterio_al_cargar'") == 0


# --- La IA que no responde --------------------------------------------------------------------

def test_si_la_ia_no_responde_se_carga_con_un_aviso_y_un_incidente(web, conn, intake_world,
                                                                  administradora, ia):
    from leda.motor.ia_real import PlazoAgotado

    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(PlazoAgotado(40))
    cuerpo = _cuerpo(intake_world, titulo=TITULO_PLC, criterio=CONCRETO)
    r = navegador.post(_camino(intake_world), json=cuerpo)
    assert r.status_code == 201, r.text
    assert r.json()["avisos"] == [{"campo": "criterio", "motivo": "sin_revisar",
                                   "texto": TEXTO_SIN_REVISAR}]
    assert _contar(conn, "task") == 1
    incidente = _fila(conn, "select * from incident where etapa = 'criterio_al_cargar'")
    assert incidente is not None
    assert str(incidente["workspace_id"]) == _norte(intake_world)["id"]
    assert "PlazoAgotado" in incidente["referencia_cruda"]
    assert CONCRETO not in (incidente["resumen_sanitizado"] or "")
    # La misma carga otra vez: la misma tarea, sin otro aviso ni otro incidente.
    ia.respuestas.append(PlazoAgotado(40))
    otra = navegador.post(_camino(intake_world), json=cuerpo)
    assert otra.status_code == 200 and otra.json()["repetida"] is True
    assert otra.json()["avisos"] == []
    assert _contar(conn, "incident", "etapa = 'criterio_al_cargar'") == 1
    assert _contar(conn, "task") == 1


def test_sin_ia_configurada_tambien_se_carga_con_el_aviso(web, conn, intake_world,
                                                         administradora, monkeypatch):
    from leda import web_app
    from leda.motor.recibir import IANoConfigurada

    monkeypatch.setattr(web_app, "_ia_del_criterio",
                        lambda conn, espacio: IANoConfigurada("No hay modelo configurado."))
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _cargar(navegador, intake_world, criterio=CONCRETO)
    assert r.status_code == 201, r.text
    assert [(a["campo"], a["motivo"]) for a in r.json()["avisos"]] == [("criterio",
                                                                        "sin_revisar")]
    assert _contar(conn, "incident", "etapa = 'criterio_al_cargar'") == 1


def test_una_ia_que_no_se_puede_preparar_tampoco_traba_la_carga(web, conn, intake_world,
                                                               administradora, monkeypatch):
    from leda import web_app

    def rota(conn, espacio):
        raise RuntimeError("la configuración de la IA no se puede leer")
    monkeypatch.setattr(web_app, "_ia_del_criterio", rota)
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _cargar(navegador, intake_world, criterio=CONCRETO)
    assert r.status_code == 201, r.text
    assert [(a["campo"], a["motivo"]) for a in r.json()["avisos"]] == [("criterio",
                                                                        "sin_revisar")]
    assert _contar(conn, "incident", "etapa = 'criterio_al_cargar'") == 1


def test_con_la_ia_caida_no_se_igual_se_rechaza(web, conn, intake_world, administradora,
                                                monkeypatch):
    """Lo que no dice nada no necesita a la IA: con la IA caída, "No se" tampoco se carga."""
    from leda import web_app
    from leda.motor.recibir import IANoConfigurada

    monkeypatch.setattr(web_app, "_ia_del_criterio",
                        lambda conn, espacio: IANoConfigurada("No hay modelo configurado."))
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _cargar(navegador, intake_world, criterio="No se")
    assert r.status_code == 422 and _errores(r) == {("criterio", "sin_comprobacion")}
    assert _contar(conn, "incident", "etapa = 'criterio_al_cargar'") == 0


# --- La puerta y el candado -------------------------------------------------------------------

def test_sin_sesion_de_administracion_no_se_llama_a_la_ia(web, conn, intake_world,
                                                          administradora, ia):
    ia.respuestas.append({"como_se_comprueba": COMO_CONCRETO})
    assert web().post(_camino(intake_world), json=_cuerpo(
        intake_world, criterio=CONCRETO)).status_code == 401
    equipo = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    assert equipo.post(_camino(intake_world), json=_cuerpo(
        intake_world, criterio=CONCRETO)).status_code == 401
    assert ia.pedidos == []
    assert _contar(conn, "task") == 0


def test_un_dato_mal_formado_no_llama_a_la_ia(web, conn, intake_world, administradora, ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _cargar(navegador, intake_world, criterio=CONCRETO, fecha="31/12/2026")
    assert r.status_code == 422
    assert ia.pedidos == []


def test_una_sesion_cortada_mientras_responde_la_ia_no_carga(web, conn, intake_world,
                                                             administradora, ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append({"como_se_comprueba": COMO_CONCRETO})
    ia.al_llamar = lambda: _revocar(conn, administradora)
    assert _cargar(navegador, intake_world, criterio=CONCRETO).status_code == 401
    assert _contar(conn, "task") == 0


def test_la_web_no_espera_a_la_ia_con_su_candado(web, conn, intake_world, administradora, ia):
    from leda import web_app

    navegador = _navegador_de_administracion(web, conn, administradora)
    candado = []
    ia.al_llamar = lambda: candado.append(web_app._WEB.locked())
    ia.respuestas.append({"como_se_comprueba": COMO_CONCRETO})
    assert _cargar(navegador, intake_world, criterio=CONCRETO).status_code == 201
    assert candado == [False]
