"""La ayuda de la IA al crear un objetivo, por las dos puertas (ADR 0023, punto 4 y decisiones 1 y
5; porción J3, tarea J3-4 de `odd/tasks/plataforma-jerarquias.md`): las garantías en la base y en
la entrada HTTP, con una IA de mentira (nunca la real).

- **Las puertas:** la de administración, con su sesión, en cualquier espacio
  (`/app/admin/api/espacios/{id}/objetivos/ayuda`); la del equipo, sólo para Dirección y en su
  espacio (`/app/api/objetivos/ayuda`): un integrante o un referente no la usan (403) y la IA no
  se llama. Cada puerta, con su propia cookie, los controles de otro sitio, JSON y tamaño.
- **La sesión antes y después de la IA:** cortada mientras responde la IA, no recibe nada ni deja
  auditoría.
- **El aislamiento:** un dato de otro espacio se rechaza sin llamar a la IA, y la IA no recibe
  nada de otro espacio.
- **El candado de la web no espera a la IA.**
- **La auditoría** (`proponer_al_crear_objetivo`): la puerta, la sesión, la IA, qué se pidió, qué
  se propuso y qué no (campo y motivo), con la huella de cada texto y nunca el texto.
- **Nunca en silencio:** si la IA no responde, 503 con un texto humano y un incidente
  (`ayuda_al_crear_objetivo`).
- **Lo que decide el código:** el referente, sólo un referente de área del espacio (decisión 3 del
  usuario, 2026-10-14), y con dos, la persona elige; nunca una fecha que nadie dijo.
"""

from __future__ import annotations

import hashlib
import json

import pytest

from leda.db import admin, espacio
from tests.garantias.test_ayuda_al_cargar import _viernes_real
from tests.garantias.test_carga_de_tareas import (  # noqa: F401 -- las fixtures
    _navegador_de_administracion, _navegador_del_equipo, _revocar, administradora, sesion, web)
from tests.garantias.test_creacion_de_objetivos import (  # noqa: F401 -- la fixture automática
    _contar, _fila, _norte, _objetivo, _persona, _referentes_de_area)
from tests.test_ayuda_al_cargar import IADeLaCarga

EJEMPLO = ("hay q dejar el deposito ordenado con las estanterias nuevas, q lo lleve taylor, para "
           "el viernes")
TEXTO_SI_LA_IA_FALLA = ("Leda no pudo completar ahora. Lo que escribiste sigue acá: completalo "
                        "vos o probá de nuevo en un rato.")
EQUIPO = "/app/api/objetivos/ayuda"


def _administracion(espacio_id: str) -> str:
    return f"/app/admin/api/espacios/{espacio_id}/objetivos/ayuda"


def _respuesta(**cambios) -> dict:
    respuesta = {"titulo": "Ordenar el depósito con las estanterías nuevas",
                 "descripcion": "Dejar el depósito ordenado con las estanterías nuevas.",
                 "padre": "", "tipo": "estrategico", "referente": "taylor",
                 "fecha": _viernes_real(), "como_dijo_la_fecha": "para el viernes"}
    respuesta.update(cambios)
    return {k: v for k, v in respuesta.items() if v is not None}


@pytest.fixture
def ia(monkeypatch):
    """La IA de mentira del espacio (la misma que usa la ayuda de la carga)."""
    from leda import web_app

    falsa = IADeLaCarga()
    monkeypatch.setattr(web_app, "_ia_de_la_ayuda", lambda conn, espacio_id: falsa)
    return falsa


def _pedir(navegador, camino: str, **cuerpo):
    datos = {"texto": EJEMPLO, "titulo": "", "descripcion": "", "padre_id": "", "tipo": "",
             "referente_id": "", "fecha": ""}
    datos.update(cuerpo)
    return navegador.post(camino, json=datos)


def _las_dos_puertas(web, conn, intake_world, administradora):
    return ((_navegador_de_administracion(web, conn, administradora),
             _administracion(_norte(intake_world)["id"])),
            (_navegador_del_equipo(web, conn, intake_world, "Morgan Hale"), EQUIPO))


def _auditorias(conn) -> int:
    return _contar(conn, "audit_log", "accion = 'proponer_al_crear_objetivo'")


# --- El ejemplo, por las dos puertas ----------------------------------------------------------

def test_las_dos_puertas_proponen_cada_dato_de_su_espacio(web, conn, intake_world,
                                                          administradora, ia):
    for navegador, camino in _las_dos_puertas(web, conn, intake_world, administradora):
        ia.respuestas.append(_respuesta())
        r = _pedir(navegador, camino)
        assert r.status_code == 200, r.text
        assert r.headers["cache-control"] == "no-store"
        assert r.json() == {
            "propuesta": {"titulo": "Ordenar el depósito con las estanterías nuevas",
                          "descripcion": "Dejar el depósito ordenado con las estanterías nuevas.",
                          "tipo": "estrategico",
                          # "taylor" es Taylor Quinn, referente de Field Services.
                          "referente_id": _persona(intake_world, "Taylor Quinn"),
                          "fecha": _viernes_real()},
            "elegir": [], "avisos": []}
    # Nada se creó: proponer no es crear.
    assert _contar(conn, "objective", "titulo like 'Ordenar%%'") == 0
    assert _auditorias(conn) == 2


def test_de_que_cuelga_sale_de_los_objetivos_del_espacio(web, conn, intake_world,
                                                        administradora, ia):
    """Los objetivos del mundo de prueba son operativos (de ellos no cuelga otro): el estratégico
    de North Lab es el único de la lista, y la IA lo recibe con su código, nunca con su id."""
    norte = _norte(intake_world)
    padre = _objetivo(conn, norte["id"], "estrategico", "Abrir la planta nueva")
    _objetivo(conn, intake_world["west-studio"]["id"], "estrategico", "Planta del oeste")
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta(padre="P1", tipo="hito"))
    r = _pedir(navegador, _administracion(norte["id"]))
    assert r.status_code == 200, r.text
    assert [(p["codigo"], p["titulo"]) for p in ia.entrada()["objetivos"]] == [
        ("P1", "Abrir la planta nueva")]
    assert padre not in json.dumps(ia.pedidos[0])
    assert r.json()["propuesta"]["padre_id"] == padre
    assert r.json()["propuesta"]["tipo"] == "hito"
    # Un código que no está en la lista no se propone, y el tipo vuelve a ser el que va sin padre.
    ia.respuestas.append(_respuesta(padre="P2", tipo="hito"))
    r = _pedir(navegador, _administracion(norte["id"]))
    assert "padre_id" not in r.json()["propuesta"]
    assert r.json()["propuesta"]["tipo"] == "estrategico"


# --- Quién puede ------------------------------------------------------------------------------

def test_la_puerta_del_equipo_es_solo_para_direccion(web, conn, intake_world, ia):
    ia.respuestas.append(_respuesta())
    for nombre in ("Sam North", "Taylor Quinn"):
        r = _pedir(_navegador_del_equipo(web, conn, intake_world, nombre), EQUIPO)
        assert r.status_code == 403, (nombre, r.text)
        assert r.json()["error"] == "sin_autoridad"
    assert ia.pedidos == []
    assert _auditorias(conn) == 0


def test_cada_puerta_pide_su_propia_sesion(web, conn, intake_world, administradora, ia):
    norte = _norte(intake_world)
    ia.respuestas.append(_respuesta())
    assert _pedir(web(), _administracion(norte["id"])).status_code == 401
    assert _pedir(web(), EQUIPO).status_code == 401
    equipo = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    assert _pedir(equipo, _administracion(norte["id"])).status_code == 401
    administracion = _navegador_de_administracion(web, conn, administradora)
    assert _pedir(administracion, EQUIPO).status_code == 401
    for navegador, camino in ((administracion, _administracion(norte["id"])), (equipo, EQUIPO)):
        for origen in ("https://otro.example", "null"):
            r = navegador.post(camino, json={"texto": EJEMPLO}, headers={"origin": origen})
            assert r.status_code == 403
        r = navegador.post(camino, content="texto=x",
                           headers={"content-type": "application/x-www-form-urlencoded"})
        assert r.status_code == 415
        r = navegador.post(camino, content=json.dumps({"texto": "x" * 70000}),
                           headers={"content-type": "application/json"})
        assert r.status_code == 413
    assert _pedir(administracion, _administracion("00000000-0000-0000-0000-000000000000")
                  ).status_code == 404
    assert _pedir(administracion, _administracion("no-es-un-id")).status_code == 404
    assert ia.pedidos == []
    assert _auditorias(conn) == 0


def test_una_sesion_cortada_mientras_responde_la_ia_no_recibe_nada(web, conn, intake_world,
                                                                  administradora, ia):
    from leda import web_app

    norte = _norte(intake_world)
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta())
    ia.al_llamar = lambda: _revocar(conn, administradora)
    assert _pedir(navegador, _administracion(norte["id"])).status_code == 401

    def cortar():
        with espacio(conn, norte["id"]) as cur:
            web_app.cortar_sesiones(cur, _persona(intake_world, "Morgan Hale"))
        conn.commit()

    equipo = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    ia.respuestas.append(_respuesta())
    ia.al_llamar = cortar
    assert _pedir(equipo, EQUIPO).status_code == 401
    assert len(ia.pedidos) == 2
    assert _auditorias(conn) == 0


# --- El aislamiento ---------------------------------------------------------------------------

def test_un_dato_de_otro_espacio_se_rechaza_sin_llamar_a_la_ia(web, conn, intake_world,
                                                              administradora, ia):
    oeste = intake_world["west-studio"]
    for navegador, camino in _las_dos_puertas(web, conn, intake_world, administradora):
        r = _pedir(navegador, camino, padre_id=oeste["objectives"][0],
                   referente_id=_persona(intake_world, "Taylor Quinn", "west-studio"))
        assert r.status_code == 422, r.text
        assert {(e["campo"], e["motivo"]) for e in r.json()["errores"]} == {
            ("padre", "no_existe"), ("referente", "no_es_referente_de_un_area")}
        r = _pedir(navegador, camino, padre_id="no-es-un-id", tipo=7)
        assert {(e["campo"], e["motivo"]) for e in r.json()["errores"]} == {
            ("padre", "mal_formado"), ("tipo", "mal_formado")}
        for error in r.json()["errores"]:
            assert error["texto"]
    assert ia.pedidos == []


def test_la_ia_no_recibe_nada_de_otro_espacio(web, conn, intake_world, administradora, ia):
    oeste = intake_world["west-studio"]
    for navegador, camino in _las_dos_puertas(web, conn, intake_world, administradora):
        ia.respuestas.append(_respuesta())
        assert _pedir(navegador, camino).status_code == 200
    for i in (0, 1):
        plano = json.dumps(ia.pedidos[i], ensure_ascii=False)
        for persona in oeste["people"].values():
            assert persona["name"] not in plano
        for objetivo in oeste["objectives"]:
            assert objetivo not in plano
        entrada = ia.entrada(i)
        assert {r["nombre"] for r in entrada["referentes"]} == {"Taylor Quinn 1", "Sam Noble 1"}
        assert {p["titulo"] for p in entrada["objetivos"]} <= {
            "Reduce service delay 1", "Raise delivery quality 1", "Expand regional coverage 1"}


def test_sin_texto_o_sin_nada_vacio_no_se_llama_a_la_ia(web, conn, intake_world, administradora,
                                                       ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    camino = _administracion(_norte(intake_world)["id"])
    r = _pedir(navegador, camino, texto="   ")
    assert r.status_code == 422
    assert r.json()["errores"][0]["campo"] == "texto"
    r = _pedir(navegador, camino, texto="x" * 1001)
    assert (r.json()["errores"][0]["campo"], r.json()["errores"][0]["motivo"]) == (
        "texto", "demasiado_largo")
    norte = _norte(intake_world)
    padre = _objetivo(conn, norte["id"], "estrategico", "Abrir la planta nueva")
    lleno = {"titulo": "x", "descripcion": "x", "padre_id": padre,
             "tipo": "hito", "referente_id": _persona(intake_world, "Taylor Quinn"),
             "fecha": _viernes_real()}
    r = _pedir(navegador, camino, **lleno)
    assert r.status_code == 422
    assert (r.json()["errores"][0]["campo"], r.json()["errores"][0]["motivo"]) == (
        "ayuda", "nada_que_completar")
    assert ia.pedidos == []


# --- El candado y la IA que no responde --------------------------------------------------------

def test_la_web_no_espera_a_la_ia_con_su_candado(web, conn, intake_world, administradora, ia):
    from leda import web_app

    candado = []
    ia.al_llamar = lambda: candado.append(web_app._WEB.locked())
    for navegador, camino in _las_dos_puertas(web, conn, intake_world, administradora):
        ia.respuestas.append(_respuesta())
        assert _pedir(navegador, camino).status_code == 200
    assert candado == [False, False]


def test_si_la_ia_no_responde_queda_un_incidente_y_un_texto_humano(web, conn, intake_world,
                                                                  administradora, ia):
    from leda.motor.ia_real import PlazoAgotado

    norte = _norte(intake_world)
    for navegador, camino in _las_dos_puertas(web, conn, intake_world, administradora):
        ia.respuestas.append(PlazoAgotado(40))
        r = _pedir(navegador, camino)
        assert r.status_code == 503
        assert r.json() == {"error": "sin_ayuda", "texto": TEXTO_SI_LA_IA_FALLA}
    assert _contar(conn, "incident", "etapa = 'ayuda_al_crear_objetivo'") == 2
    incidente = _fila(conn, "select * from incident where etapa = 'ayuda_al_crear_objetivo' "
                            "limit 1")
    assert str(incidente["workspace_id"]) == norte["id"]
    assert "PlazoAgotado" in incidente["referencia_cruda"]
    assert EJEMPLO not in (incidente["resumen_sanitizado"] or "")
    auditoria = _fila(conn, "select detalle from audit_log "
                            "where accion = 'proponer_al_crear_objetivo' limit 1")
    assert auditoria["detalle"]["respondio"] is False


def test_sin_ia_configurada_tambien(web, conn, intake_world, monkeypatch):
    from leda import web_app
    from leda.motor.recibir import IANoConfigurada

    monkeypatch.setattr(web_app, "_ia_de_la_ayuda",
                        lambda conn, espacio_id: IANoConfigurada("No hay modelo configurado."))
    equipo = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    r = _pedir(equipo, EQUIPO)
    assert r.status_code == 503 and r.json()["texto"] == TEXTO_SI_LA_IA_FALLA
    assert _contar(conn, "incident", "etapa = 'ayuda_al_crear_objetivo'") == 1


# --- La auditoría -----------------------------------------------------------------------------

def test_la_auditoria_guarda_lo_propuesto_con_su_huella_y_sin_el_texto(
        web, conn, intake_world, administradora, ia):
    norte = _norte(intake_world)
    (administracion, camino_a), (equipo, camino_e) = _las_dos_puertas(web, conn, intake_world,
                                                                      administradora)
    ia.respuestas.append(_respuesta(descripcion="Lo pidió Ariel."))
    r = _pedir(administracion, camino_a)
    assert r.status_code == 200
    fila = _fila(conn, """select workspace_id, actor_app_user_id, actor_kind, sujeto_tipo,
                                 sujeto_id, detalle, pack_hash, nucleo_hash
                            from audit_log where accion = 'proponer_al_crear_objetivo'""")
    assert str(fila["workspace_id"]) == norte["id"]
    assert str(fila["actor_app_user_id"]) == administradora
    assert (fila["actor_kind"], fila["sujeto_tipo"]) == ("persona", "workspace")
    assert fila["pack_hash"] and fila["nucleo_hash"]
    detalle = fila["detalle"]
    assert (detalle["origen"], detalle["puerta"], detalle["ia"]) == (
        "web", "administracion", "de-mentira")
    assert detalle["respondio"] is True and detalle["sesion_de_administracion_id"]
    # Sin objetivos de los que colgar (los del mundo de prueba son operativos), eso no se pide.
    assert set(detalle["pide"]) == {"titulo", "descripcion", "tipo", "referente_id", "fecha"}
    assert set(detalle["propuestos"]) == {"titulo", "tipo", "referente_id", "fecha"}
    assert {"campo": "descripcion", "motivo": "nombre"} in detalle["descartados"]
    titulo = r.json()["propuesta"]["titulo"]
    assert detalle["huellas"] == {"titulo": hashlib.sha256(titulo.encode()).hexdigest()}
    assert detalle["referente_membership_id"] == _persona(intake_world, "Taylor Quinn")
    plano = json.dumps(detalle, ensure_ascii=False)
    for texto in (titulo, EJEMPLO, "Ariel"):
        assert texto not in plano
    # Por la puerta del equipo, la sesión del equipo y quién es Dirección.
    ia.respuestas.append(_respuesta())
    assert _pedir(equipo, camino_e).status_code == 200
    fila = _fila(conn, """select actor_app_user_id, detalle from audit_log
                           where accion = 'proponer_al_crear_objetivo'
                             and detalle ->> 'puerta' = 'equipo'""")
    assert str(fila["actor_app_user_id"]) == administradora     # Morgan Hale, Dirección
    assert fila["detalle"]["sesion_web_id"]
    assert "sesion_de_administracion_id" not in fila["detalle"]


# --- Lo que decide el código ------------------------------------------------------------------

def test_quien_no_es_referente_de_un_area_nunca_se_propone(web, conn, intake_world,
                                                          administradora, ia):
    """Decisión 3 del usuario: Sam North está en el equipo, pero no es referente de un área."""
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta(referente="north"))
    r = _pedir(navegador, _administracion(_norte(intake_world)["id"]),
               texto=EJEMPLO.replace("taylor", "north"))
    assert r.status_code == 200, r.text
    assert "referente_id" not in r.json()["propuesta"]
    assert r.json()["avisos"] == [{
        "campo": "referente", "motivo": "no_encontrado",
        "texto": "No encontré a «north» entre los referentes de área; elegí el referente."}]


def test_sam_es_solo_sam_noble_porque_sam_north_no_es_referente(web, conn, intake_world, ia):
    equipo = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    ia.respuestas.append(_respuesta(referente="sam"))
    r = _pedir(equipo, EQUIPO, texto=EJEMPLO.replace("taylor", "sam"))
    assert r.json()["propuesta"]["referente_id"] == _persona(intake_world, "Sam Noble")
    assert r.json()["elegir"] == []


def test_dos_referentes_con_esas_palabras_se_muestran_para_elegir(web, conn, intake_world, ia):
    """ADR 0020, decisión 3: "el jefe" es el apodo de Taylor Quinn y de Sam Noble; Leda no
    elige."""
    norte = _norte(intake_world)
    with admin(conn) as cur:
        for nombre in ("Taylor Quinn", "Sam Noble"):
            cur.execute(
                """insert into apodo (workspace_id, membership_id, apodo,
                                      ensenado_por_app_user_id, canal, at)
                   values (%s, %s, 'el jefe', %s, 'plataforma', now())""",
                (norte["id"], _persona(intake_world, nombre),
                 norte["people"]["Morgan Hale"]["app_user_id"]))
    conn.commit()
    equipo = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    ia.respuestas.append(_respuesta(referente="el jefe"))
    r = _pedir(equipo, EQUIPO, texto=EJEMPLO.replace("taylor", "el jefe"))
    assert r.status_code == 200, r.text
    assert "referente_id" not in r.json()["propuesta"]
    assert {e["membership_id"] for e in r.json()["elegir"]} == {
        _persona(intake_world, "Taylor Quinn"), _persona(intake_world, "Sam Noble")}
    assert [a["motivo"] for a in r.json()["avisos"]] == ["varios"]


def test_una_fecha_que_nadie_dijo_no_se_propone(web, conn, intake_world, administradora, ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    texto = "hay q dejar el deposito ordenado, q lo lleve taylor"
    ia.respuestas.append(_respuesta())
    r = _pedir(navegador, _administracion(_norte(intake_world)["id"]), texto=texto)
    assert r.status_code == 200, r.text
    assert "fecha" not in r.json()["propuesta"]
    assert [a["motivo"] for a in r.json()["avisos"] if a["campo"] == "fecha"] == ["no_dicha"]


def test_lo_escrito_no_se_pide_ni_vuelve(web, conn, intake_world, administradora, ia):
    norte = _norte(intake_world)
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(_respuesta())
    r = _pedir(navegador, _administracion(norte["id"]), titulo="Ordenar el depósito",
               referente_id=_persona(intake_world, "Sam Noble"))
    assert r.status_code == 200, r.text
    assert "titulo" not in r.json()["propuesta"]
    assert "referente_id" not in r.json()["propuesta"]
    assert set(ia.entrada()["pide"]) == {"descripcion", "tipo", "fecha"}


def test_sin_nadie_nombrado_leda_propone_el_referente_del_area(web, conn, intake_world,
                                                              administradora, ia):
    """J3-4b ("Leda completa todo lo que puede", como la J2-18): la IA recibe las áreas con
    referente de ese espacio, con un código y sin ids, y dice de qué área es el objetivo; el
    código propone a su referente y la auditoría dice que lo propuso Leda."""
    equipo = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    texto = "hay q revisar como se miden las piezas antes de mandarlas"
    ia.respuestas.append(_respuesta(referente="", area="A2", fecha="", como_dijo_la_fecha="",
                                    titulo="Revisar cómo se miden las piezas",
                                    descripcion="Revisar cómo se miden las piezas antes de "
                                                "mandarlas."))
    r = _pedir(equipo, EQUIPO, texto=texto)
    assert r.status_code == 200, r.text
    assert ia.entrada()["areas"] == [{"codigo": "A1", "area": "Field Services"},
                                     {"codigo": "A2", "area": "Quality Guild"}]
    assert _persona(intake_world, "Sam Noble") not in json.dumps(ia.pedidos[0])
    assert r.json()["propuesta"]["referente_id"] == _persona(intake_world, "Sam Noble")
    assert r.json()["avisos"] == []
    detalle = _fila(conn, """select detalle from audit_log
                              where accion = 'proponer_al_crear_objetivo'""")["detalle"]
    assert detalle["referente_de"] == "leda"
    assert detalle["referente_membership_id"] == _persona(intake_world, "Sam Noble")
    # Nombrado alguien que no es referente, el área no lo reemplaza.
    ia.respuestas.append(_respuesta(referente="north", area="A2"))
    r = _pedir(equipo, EQUIPO, texto=EJEMPLO.replace("taylor", "north"))
    assert "referente_id" not in r.json()["propuesta"]
    assert [a["motivo"] for a in r.json()["avisos"]] == ["no_encontrado"]
