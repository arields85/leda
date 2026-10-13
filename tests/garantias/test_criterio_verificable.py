"""Un criterio de aceptación que se pueda comprobar, al cargar por la puerta de administración
(J2-9, J2-13 y J2-14 de `odd/tasks/plataforma-jerarquias.md`; mecánica §13: "¿el resultado
esperado es concreto y verificable?"): las garantías en la entrada HTTP, con una IA de mentira
(nunca la real).

Lo que encontró el usuario en el celular (2026-10-13): primero un criterio circular y una tarea
cargada con "No se" (J2-9 y J2-13); después, "El ups queda cambiado y funcionando" rechazado con
"Contame cómo se sabe que está terminada." aunque el área ya pedía la evidencia que dice cómo se
comprueba, y sin proponer nada (J2-14).

- **Con la evidencia del área (J2-14):** la persona escribe el resultado y cómo se comprueba sale
  de la evidencia que se elige en el formulario. Se carga lo que dice un resultado (lo juzga la
  IA por su sentido) y se guarda tal cual; se rechaza lo que no dice ninguno (422 `criterio` /
  `sin_resultado`) y lo igual al título (lo decide el código, diga lo que diga la IA), con un
  criterio propuesto por Leda (`propuesta`: J2-17, el que escribe la IA con sus palabras; el de
  reserva, el resultado más la evidencia del área, sólo si el suyo no pasa los controles). Sin
  propuesta (la IA caída o nada que pase los controles), el rechazo igual dice qué falta y queda
  un incidente (`propuesta_del_criterio`).
- **Sin evidencia del área (J2-13):** el criterio tiene que decir cómo se comprueba; la IA lo
  juzga por el sentido y copia la parte que lo dice; si no, 422 `sin_comprobacion`, también con
  un criterio propuesto (J2-17: "no sé" es un pedido de ayuda).
- **Si la IA no juzga, ni se traba ni se finge:** se carga con un aviso que no bloquea y un
  incidente (`criterio_al_cargar`); una carga repetida no suma otro.
- **Sin las opciones de la carga** (no se sabe qué evidencia pide el área), el criterio no se
  juzga con la regla de otra: se carga con el mismo aviso, o se rechaza sin la IA lo vacío o
  igual al título, y queda un incidente (`evidencia_del_criterio`).
- **La IA, sólo con una sesión vigente y fuera del candado de la web;** una sesión cortada
  mientras respondía no carga nada. Un rechazo del criterio no usa la clave.
"""

from __future__ import annotations

import pytest

from leda.db import admin
from tests.garantias.test_carga_de_tareas import (  # noqa: F401
    _contar, _cuerpo, _fila, _navegador_de_administracion, _navegador_del_equipo, _norte,
    _persona, _revocar, administradora, web)
from tests.test_ayuda_al_cargar import (CIRCULAR, COMO_CONCRETO, CONCRETO, ORDENADO, TITULO_PLC,
                                        TITULO_UPS, UPS_DEL_CELULAR, IADeLaCarga)

TEXTO_SIN_COMPROBACION = "No dice cómo se sabe que está terminada."
# El criterio que escribe la IA con sus palabras al rechazar uno (J2-17).
DE_LEDA_PLC = ("El PLC de la comprimidora Fette 2000 queda listo para integrarlo y se ven sus "
               "variables desde la interfaz.")
TEXTO_SIN_RESULTADO = "No dice qué tiene que quedar hecho para darla por terminada."
TEXTO_SIN_REVISAR = ("No pude revisar el criterio ahora: la tarea quedó cargada con el criterio "
                     "como lo escribiste.")
NO_LO_DICE = {"dice_como_se_comprueba": False, "como_se_comprueba": ""}
LO_DICE = {"dice_como_se_comprueba": True, "como_se_comprueba": COMO_CONCRETO}
RESULTADO_PLC = "El PLC de la comprimidora Fette 2000 queda listo para integrarlo"
PROPUESTO_PLC = f"{RESULTADO_PLC}. Se comprueba con lo que pide el área: test record."
DICE_UN_RESULTADO = {"dice_un_resultado": True, "resultado": RESULTADO_PLC}
SIN_RESULTADO = {"dice_un_resultado": False, "resultado": RESULTADO_PLC}


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


def _sin_evidencia(conn, intake_world) -> dict:
    """El área de calidad decide no pedir evidencia (`task_evidence_policy` vacía): lo que cambia
    en la carga, con Sam Noble y sin evidencia."""
    with admin(conn) as cur:
        cur.execute("""update task_evidence_policy set evidencia_requerida = '{}', version = 2
                        where area_id = %s""", (_norte(intake_world)["areas"]["quality"],))
    conn.commit()
    return {"responsable_id": _persona(intake_world, "Sam Noble"), "evidencia": []}


# --- Con la evidencia del área: el resultado alcanza (J2-14) -------------------------------------

@pytest.mark.parametrize("titulo, criterio", [(TITULO_UPS, UPS_DEL_CELULAR),
                                              ("Ordenar el depósito", ORDENADO),
                                              (TITULO_PLC, CIRCULAR)])
def test_un_resultado_con_la_evidencia_del_area_se_carga(web, conn, intake_world, administradora,
                                                         ia, titulo, criterio):
    """Los dos casos del celular, y el criterio circular de la J2-13: dicen un resultado, y cómo
    se comprueba lo dice la evidencia que pide el área. Se guarda tal cual se escribió."""
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append({"dice_un_resultado": True, "resultado": criterio})
    r = navegador.post(_camino(intake_world), json=_cuerpo(intake_world, titulo=titulo,
                                                           criterio=criterio))
    assert r.status_code == 201, r.text
    assert r.json()["avisos"] == []
    assert ia.entrada() == {"titulo": titulo, "descripcion": "", "criterio": criterio,
                            "evidencia_que_pide_el_area": ["test record"]}
    assert _fila(conn, "select criterio_aceptacion c from task where id = %s",
                 r.json()["task_id"])["c"] == criterio


def test_no_se_no_se_carga_y_trae_un_criterio_propuesto(web, conn, intake_world, administradora,
                                                        ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(SIN_RESULTADO)
    cuerpo = _cuerpo(intake_world, titulo=TITULO_PLC, criterio="No se")
    r = navegador.post(_camino(intake_world), json=cuerpo)
    assert r.status_code == 422, r.text
    (error,) = r.json()["errores"]
    assert error == {"campo": "criterio", "motivo": "sin_resultado",
                     "texto": TEXTO_SIN_RESULTADO, "propuesta": PROPUESTO_PLC}
    assert _contar(conn, "task") == 0 and _contar(conn, "carga_de_tarea") == 0
    assert _contar(conn, "incident", "etapa = 'propuesta_del_criterio'") == 0
    # Con la propuesta, la misma clave carga: el rechazo no la usó.
    ia.respuestas.append(DICE_UN_RESULTADO)
    r = navegador.post(_camino(intake_world), json={**cuerpo, "criterio": PROPUESTO_PLC})
    assert r.status_code == 201, r.text
    assert _contar(conn, "task") == 1


@pytest.mark.parametrize("respuesta", [DICE_UN_RESULTADO, SIN_RESULTADO])
def test_igual_al_titulo_no_se_carga_diga_lo_que_diga_la_ia(web, conn, intake_world,
                                                            administradora, ia, respuesta):
    """Lo decide el código; la IA sólo propone el resultado."""
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(respuesta)
    r = _cargar(navegador, intake_world, criterio=f"{TITULO_PLC.lower()}.")
    assert r.status_code == 422, r.text
    (error,) = r.json()["errores"]
    assert (error["motivo"], error["propuesta"]) == ("sin_resultado", PROPUESTO_PLC)
    assert len(ia.pedidos) == 1
    assert _contar(conn, "task") == 0


def test_el_rechazo_del_criterio_va_junto_con_lo_demas(web, conn, intake_world, administradora,
                                                       ia):
    """Todo junto, como siempre: lo que dice la base, sin repetir el criterio ni pedir la
    clave."""
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(SIN_RESULTADO)
    r = _cargar(navegador, intake_world, criterio="No se", decidio_id="")
    assert r.status_code == 422
    assert _errores(r) == {("criterio", "sin_resultado"), ("decidio", "falta")}
    assert _contar(conn, "task") == 0


def test_sin_propuesta_el_rechazo_igual_dice_que_falta_y_deja_un_incidente(
        web, conn, intake_world, administradora, monkeypatch):
    """Con la IA caída, lo igual al título se rechaza igual (no necesita a la IA para eso), sin
    propuesta: el aviso dice qué falta y la administración se entera (nunca en silencio)."""
    from leda import web_app
    from leda.motor.recibir import IANoConfigurada

    monkeypatch.setattr(web_app, "_ia_del_criterio",
                        lambda conn, espacio: IANoConfigurada("No hay modelo configurado."))
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _cargar(navegador, intake_world, criterio=TITULO_PLC)
    assert r.status_code == 422
    assert r.json()["errores"] == [{"campo": "criterio", "motivo": "sin_resultado",
                                    "texto": TEXTO_SIN_RESULTADO}]
    incidente = _fila(conn, "select * from incident where etapa = 'propuesta_del_criterio'")
    assert incidente is not None
    assert str(incidente["workspace_id"]) == _norte(intake_world)["id"]
    assert "LookupError" in incidente["referencia_cruda"]
    assert TITULO_PLC not in (incidente["resumen_sanitizado"] or "")
    assert _contar(conn, "incident", "etapa = 'criterio_al_cargar'") == 0
    assert _contar(conn, "task") == 0


def test_un_resultado_propuesto_con_un_dato_inventado_no_se_propone(web, conn, intake_world,
                                                                    administradora, ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append({"dice_un_resultado": False,
                          "resultado": "El PLC de las 4 comprimidoras queda listo"})
    r = _cargar(navegador, intake_world, criterio="No se")
    assert r.status_code == 422
    (error,) = r.json()["errores"]
    assert error["motivo"] == "sin_resultado" and "propuesta" not in error
    assert _contar(conn, "incident", "etapa = 'propuesta_del_criterio'") == 1


# --- Sin evidencia del área: el criterio dice cómo se comprueba (J2-13) -------------------------

def test_sin_evidencia_un_criterio_sin_comprobacion_no_se_carga(web, conn, intake_world,
                                                                administradora, ia):
    sin_evidencia = _sin_evidencia(conn, intake_world)
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append({**NO_LO_DICE, "criterio": DE_LEDA_PLC})
    r = _cargar(navegador, intake_world, criterio=UPS_DEL_CELULAR, **sin_evidencia)
    assert r.status_code == 422, r.text
    # J2-17: el rechazo sin evidencia también trae el criterio que escribe la IA, tal cual.
    assert r.json()["errores"] == [{"campo": "criterio", "motivo": "sin_comprobacion",
                                    "texto": TEXTO_SIN_COMPROBACION, "propuesta": DE_LEDA_PLC}]
    assert ia.entrada() == {"titulo": TITULO_PLC, "descripcion": "", "criterio": UPS_DEL_CELULAR}
    assert _contar(conn, "task") == 0
    assert _contar(conn, "incident", "etapa = 'propuesta_del_criterio'") == 0


def test_el_rechazo_trae_el_criterio_de_la_ia_y_no_la_plantilla(web, conn, intake_world,
                                                               administradora, ia):
    """J2-17: con la evidencia del área, el criterio propuesto es el que escribió la IA; la
    plantilla queda sólo de reserva."""
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append({**SIN_RESULTADO, "criterio": DE_LEDA_PLC})
    r = _cargar(navegador, intake_world, criterio="No se")
    assert r.status_code == 422, r.text
    (error,) = r.json()["errores"]
    assert error["propuesta"] == DE_LEDA_PLC
    assert "Se comprueba con lo que pide el área" not in error["propuesta"]


def test_sin_evidencia_un_criterio_con_una_comprobacion_concreta_se_carga(
        web, conn, intake_world, administradora, ia):
    sin_evidencia = _sin_evidencia(conn, intake_world)
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(LO_DICE)
    r = _cargar(navegador, intake_world, criterio=CONCRETO, **sin_evidencia)
    assert r.status_code == 201, r.text
    assert r.json()["avisos"] == []
    assert _contar(conn, "incident", "etapa = 'criterio_al_cargar'") == 0


def test_sin_evidencia_igual_al_titulo_se_rechaza_con_un_criterio_propuesto(
        web, conn, intake_world, administradora, ia):
    """Lo decide el código, diga lo que diga la IA; J2-17: la IA se llama igual, para escribir el
    criterio que Leda propone ("no sé" es un pedido de ayuda)."""
    sin_evidencia = _sin_evidencia(conn, intake_world)
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append({**LO_DICE, "criterio": DE_LEDA_PLC})
    r = _cargar(navegador, intake_world, criterio=f"{TITULO_PLC.lower()}.", **sin_evidencia)
    assert r.status_code == 422, r.text
    assert _errores(r) == {("criterio", "sin_comprobacion")}
    assert r.json()["errores"][0]["propuesta"] == DE_LEDA_PLC
    assert len(ia.pedidos) == 1


def test_sin_evidencia_y_la_ia_caida_vacio_se_rechaza_con_un_incidente(
        web, conn, intake_world, administradora, ia):
    from leda.motor.ia_real import PlazoAgotado

    sin_evidencia = _sin_evidencia(conn, intake_world)
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(PlazoAgotado(40))
    r = _cargar(navegador, intake_world, criterio=f"{TITULO_PLC}", **sin_evidencia)
    assert r.status_code == 422, r.text
    assert r.json()["errores"] == [{"campo": "criterio", "motivo": "sin_comprobacion",
                                    "texto": TEXTO_SIN_COMPROBACION}]
    assert _contar(conn, "incident", "etapa = 'propuesta_del_criterio'") == 1


def test_sin_evidencia_la_ia_que_dice_que_si_con_una_parte_que_no_esta_no_vale(
        web, conn, intake_world, administradora, ia):
    """El juicio no cierra: no se finge revisado ni se rechaza; se carga con el aviso."""
    sin_evidencia = _sin_evidencia(conn, intake_world)
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append({"dice_como_se_comprueba": True,
                          "como_se_comprueba": "las alarmas suenan en la sala"})
    r = _cargar(navegador, intake_world, criterio=CONCRETO, **sin_evidencia)
    assert r.status_code == 201, r.text
    assert [(a["campo"], a["motivo"]) for a in r.json()["avisos"]] == [("criterio",
                                                                        "sin_revisar")]


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


def test_con_la_ia_caida_no_se_se_carga_con_el_aviso(web, conn, intake_world, administradora,
                                                     monkeypatch):
    """J2-13: sin una lista de palabras, "No se" necesita a la IA; caída, no se finge la
    revisión: se carga con el aviso y el incidente, como cualquier otro criterio."""
    from leda import web_app
    from leda.motor.recibir import IANoConfigurada

    monkeypatch.setattr(web_app, "_ia_del_criterio",
                        lambda conn, espacio: IANoConfigurada("No hay modelo configurado."))
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _cargar(navegador, intake_world, criterio="No se")
    assert r.status_code == 201, r.text
    assert r.json()["avisos"] == [{"campo": "criterio", "motivo": "sin_revisar",
                                   "texto": TEXTO_SIN_REVISAR}]
    assert _contar(conn, "incident", "etapa = 'criterio_al_cargar'") == 1


# --- Las opciones de la carga que no se pueden leer (advertencia de `review-88b227055a98f635`) ---
#
# Sin las opciones no se sabe qué evidencia pide el área: juzgar el criterio sin ella sería
# juzgarlo con la regla de la J2-13 (decir cómo se comprueba) cuando el área ya lo dice, en
# silencio. No se juzga ni se finge: se carga con el aviso de que no se revisó, o se rechaza sin
# la IA lo que se rechaza sin ella, y en los dos casos queda un incidente (`evidencia_del_criterio`).

def _opciones_que_no_se_leen(monkeypatch, falla):
    from leda import web_app

    def leer(conn, token, espacio):
        if isinstance(falla, BaseException):
            raise falla
        return falla
    monkeypatch.setattr(web_app, "_opciones_para_el_juicio", leer)


@pytest.mark.parametrize("falla, causa", [(RuntimeError("la base no contestó"), "RuntimeError"),
                                          ({"ok": False, "error": "sin_permiso"}, "sin_permiso")])
def test_sin_las_opciones_no_se_juzga_se_carga_con_el_aviso_y_un_incidente(
        web, conn, intake_world, administradora, ia, monkeypatch, falla, causa):
    _opciones_que_no_se_leen(monkeypatch, falla)
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _cargar(navegador, intake_world, criterio=UPS_DEL_CELULAR)
    assert r.status_code == 201, r.text
    assert r.json()["avisos"] == [{"campo": "criterio", "motivo": "sin_revisar",
                                   "texto": TEXTO_SIN_REVISAR}]
    assert ia.pedidos == []
    incidente = _fila(conn, "select * from incident where etapa = 'evidencia_del_criterio'")
    assert incidente is not None
    assert str(incidente["workspace_id"]) == _norte(intake_world)["id"]
    assert causa in incidente["referencia_cruda"]
    assert UPS_DEL_CELULAR not in (incidente["resumen_sanitizado"] or "")
    assert _contar(conn, "incident", "etapa = 'criterio_al_cargar'") == 0
    assert _contar(conn, "task") == 1


def test_sin_las_opciones_lo_igual_al_titulo_se_rechaza_igual_con_un_incidente(
        web, conn, intake_world, administradora, ia, monkeypatch):
    """Lo que se rechaza sin la IA se rechaza también sin las opciones; sin la evidencia no hay
    propuesta, y la administración se entera."""
    _opciones_que_no_se_leen(monkeypatch, RuntimeError("la base no contestó"))
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _cargar(navegador, intake_world, criterio=TITULO_PLC)
    assert r.status_code == 422, r.text
    assert r.json()["errores"] == [{"campo": "criterio", "motivo": "sin_resultado",
                                    "texto": TEXTO_SIN_RESULTADO}]
    assert ia.pedidos == []
    assert _contar(conn, "incident", "etapa = 'evidencia_del_criterio'") == 1
    assert _contar(conn, "incident", "etapa = 'propuesta_del_criterio'") == 0
    assert _contar(conn, "task") == 0


# --- La puerta y el candado -------------------------------------------------------------------

def test_sin_sesion_de_administracion_no_se_llama_a_la_ia(web, conn, intake_world,
                                                          administradora, ia):
    ia.respuestas.append(DICE_UN_RESULTADO)
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
    ia.respuestas.append(DICE_UN_RESULTADO)
    ia.al_llamar = lambda: _revocar(conn, administradora)
    assert _cargar(navegador, intake_world, criterio=CONCRETO).status_code == 401
    assert _contar(conn, "task") == 0


def test_la_web_no_espera_a_la_ia_con_su_candado(web, conn, intake_world, administradora, ia):
    from leda import web_app

    navegador = _navegador_de_administracion(web, conn, administradora)
    candado = []
    ia.al_llamar = lambda: candado.append(web_app._WEB.locked())
    ia.respuestas.append(DICE_UN_RESULTADO)
    r = _cargar(navegador, intake_world, criterio=CONCRETO)
    assert r.status_code == 201 and r.json()["avisos"] == []
    assert candado == [False]


# --- Advertencia de RDD de la J2-17: una IA que no se puede preparar ------------------------------

@pytest.mark.parametrize("criterio", [TITULO_PLC, f"  {TITULO_PLC.lower()}. "])
def test_una_ia_que_no_se_puede_preparar_igual_rechaza_lo_igual_al_titulo(
        web, conn, intake_world, administradora, monkeypatch, criterio):
    """Sin la IA, lo igual al título se rechaza igual (`sin_resultado`, sin propuesta: sin la IA
    no hay un resultado escrito para armar el de reserva) y nunca se carga sin revisar."""
    from leda import web_app

    def rota(conn, espacio):
        raise RuntimeError("la configuración de la IA no se puede leer")
    monkeypatch.setattr(web_app, "_ia_del_criterio", rota)
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _cargar(navegador, intake_world, criterio=criterio)
    assert r.status_code == 422, r.text
    assert r.json()["errores"] == [{"campo": "criterio", "motivo": "sin_resultado",
                                    "texto": TEXTO_SIN_RESULTADO}]
    assert _contar(conn, "task") == 0
    incidente = _fila(conn, "select * from incident where etapa = 'propuesta_del_criterio'")
    assert incidente is not None and "RuntimeError" in incidente["referencia_cruda"]
    assert _contar(conn, "incident", "etapa = 'criterio_al_cargar'") == 0
