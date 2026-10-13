"""La ortografía al cargar, por la puerta de administración (J2-17 de
`odd/tasks/plataforma-jerarquias.md`): las garantías en la base y en la entrada HTTP, con una IA de
mentira (nunca la real).

El usuario (2026-10-13): "no es cambiar el significado de mis palabras, es corregir la ortografía…
me está ayudando". Antes de la vista previa, Leda corrige la ortografía de lo que la persona
escribió en los campos de texto y pone los nombres como están en los datos del equipo; la cocina
acepta una corrección sólo si cambió nada más que la ortografía, palabra por palabra.

- **La puerta:** como la ayuda: sólo una sesión de administración vigente, la protección contra
  otros sitios, JSON y un tope de tamaño; un espacio que no existe, 404.
- **El aislamiento:** la IA recibe los nombres de ese espacio y de ningún otro.
- **Nunca en silencio:** una corrección que cambia algo más que la ortografía no se acepta (queda
  el texto de la persona) y deja un incidente; si la IA no responde, nada se bloquea: el texto
  queda como se escribió, con un aviso y un incidente.
- **La auditoría** (`corregir_al_cargar`): qué se pidió, qué se corrigió y qué no, con la huella de
  cada texto corregido y nunca el texto.
- **El candado de la web no espera a la IA.**
"""

from __future__ import annotations

import hashlib
import json

import pytest

from tests.garantias.test_carga_de_tareas import (  # noqa: F401
    _contar, _fila, _navegador_de_administracion, _navegador_del_equipo, _norte, administradora,
    sesion, web)
from tests.test_ayuda_al_cargar import IADeLaCarga

TEXTO_SIN_REVISAR = ("No pude revisar la ortografía ahora: quedó como lo escribiste.")


def _camino(espacio_id: str) -> str:
    return f"/app/admin/api/espacios/{espacio_id}/ortografia"


@pytest.fixture
def ia(monkeypatch):
    from leda import web_app

    falsa = IADeLaCarga()
    monkeypatch.setattr(web_app, "_ia_de_la_ortografia", lambda conn, espacio: falsa)
    return falsa


def _pedir(navegador, espacio_id: str, **textos):
    return navegador.post(_camino(espacio_id), json=textos)


def test_corrige_la_ortografia_y_los_nombres_del_equipo(web, conn, intake_world, administradora,
                                                         ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append({"titulo": "Revisar el tablero con Sam North",
                          "criterio": "El tablero queda revisado."})
    r = _pedir(navegador, _norte(intake_world)["id"], titulo="revisar el tablero con sam norht",
               criterio="El tablero queda revisado.")
    assert r.status_code == 200, r.text
    assert r.headers["cache-control"] == "no-store"
    assert r.json() == {"corregidos": {"titulo": {
        "texto": "Revisar el tablero con Sam North",
        "cambios": [{"antes": "revisar", "despues": "Revisar"},
                    {"antes": "sam", "despues": "Sam"}, {"antes": "norht", "despues": "North"}]}},
        "sin_revisar": []}
    assert ia.entrada()["textos"] == {"titulo": "revisar el tablero con sam norht",
                                      "criterio": "El tablero queda revisado."}
    assert _contar(conn, "incident", "etapa = 'ortografia_al_cargar'") == 0
    detalle = _fila(conn, "select detalle from audit_log where accion = 'corregir_al_cargar'")[
        "detalle"]
    assert detalle["pide"] == ["titulo", "criterio"] and detalle["corregidos"] == ["titulo"]
    assert detalle["huellas"]["titulo"] == hashlib.sha256(
        "Revisar el tablero con Sam North".encode("utf-8")).hexdigest()
    assert "Sam North" not in json.dumps(detalle, ensure_ascii=False)


def test_una_correccion_que_cambia_la_redaccion_no_se_acepta_y_deja_un_incidente(
        web, conn, intake_world, administradora, ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append({"titulo": "Instalar el tablero nuevo"})
    r = _pedir(navegador, _norte(intake_world)["id"], titulo="colgar el tablero")
    assert r.status_code == 200, r.text
    assert r.json() == {"corregidos": {}, "sin_revisar": ["titulo"], "aviso": TEXTO_SIN_REVISAR}
    incidente = _fila(conn, "select * from incident where etapa = 'ortografia_al_cargar'")
    assert incidente is not None and "no_es_ortografia" in incidente["referencia_cruda"]
    assert "colgar el tablero" not in json.dumps(incidente, default=str)
    assert "Instalar" not in json.dumps(incidente, default=str)


def test_si_la_ia_no_responde_nada_se_bloquea_y_queda_un_incidente(web, conn, intake_world,
                                                                    administradora, ia):
    from leda.motor.ia_real import PlazoAgotado

    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append(PlazoAgotado(40))
    r = _pedir(navegador, _norte(intake_world)["id"], titulo="colgar el arvol",
               descripcion="")
    assert r.status_code == 200, r.text
    assert r.json() == {"corregidos": {}, "sin_revisar": ["titulo"], "aviso": TEXTO_SIN_REVISAR}
    incidente = _fila(conn, "select * from incident where etapa = 'ortografia_al_cargar'")
    assert incidente is not None and "PlazoAgotado" in incidente["referencia_cruda"]
    assert _fila(conn, "select detalle from audit_log where accion = 'corregir_al_cargar'")[
        "detalle"]["respondio"] is False


def test_sin_ia_configurada_tampoco_se_bloquea(web, conn, intake_world, administradora,
                                               monkeypatch):
    from leda import web_app
    from leda.motor.recibir import IANoConfigurada

    monkeypatch.setattr(web_app, "_ia_de_la_ortografia",
                        lambda conn, espacio: IANoConfigurada("No hay modelo configurado."))
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _pedir(navegador, _norte(intake_world)["id"], titulo="colgar el arvol")
    assert r.status_code == 200 and r.json()["sin_revisar"] == ["titulo"]
    assert _contar(conn, "incident", "etapa = 'ortografia_al_cargar'") == 1


def test_sin_textos_no_se_llama_a_la_ia(web, conn, intake_world, administradora, ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _pedir(navegador, _norte(intake_world)["id"], titulo="  ", criterio="")
    assert r.status_code == 200 and r.json() == {"corregidos": {}, "sin_revisar": []}
    assert ia.pedidos == []


def test_un_dato_mal_formado_se_rechaza_sin_llamar_a_la_ia(web, conn, intake_world,
                                                           administradora, ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _pedir(navegador, _norte(intake_world)["id"], titulo=3)
    assert r.status_code == 422
    assert r.json()["errores"][0]["campo"] == "titulo"
    assert ia.pedidos == []


def test_la_puerta_es_la_de_administracion(web, conn, intake_world, administradora, ia):
    norte = _norte(intake_world)
    ia.respuestas.append({"titulo": "Colgar el árbol"})
    assert _pedir(web(), norte["id"], titulo="colgar el arvol").status_code == 401
    equipo = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    assert _pedir(equipo, norte["id"], titulo="colgar el arvol").status_code == 401
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = navegador.post(_camino(norte["id"]), json={"titulo": "x"},
                       headers={"origin": "https://otro.example"})
    assert r.status_code == 403
    r = navegador.post(_camino(norte["id"]), content="titulo=x",
                       headers={"content-type": "application/x-www-form-urlencoded"})
    assert r.status_code == 415
    r = navegador.post(_camino(norte["id"]), content=json.dumps({"titulo": "x" * 70000}),
                       headers={"content-type": "application/json"})
    assert r.status_code == 413
    assert _pedir(navegador, "00000000-0000-0000-0000-000000000000",
                  titulo="x").status_code == 404
    assert ia.pedidos == []
    assert _contar(conn, "audit_log", "accion = 'corregir_al_cargar'") == 0


def test_la_ia_recibe_solo_los_nombres_de_su_espacio(web, conn, intake_world, administradora,
                                                     ia):
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append({"titulo": "Colgar el árbol"})
    assert _pedir(navegador, _norte(intake_world)["id"],
                  titulo="colgar el arvol").status_code == 200
    nombres = ia.entrada()["nombres"]
    # En el mundo de prueba, las personas de North Lab terminan en 1 y las de West Studio en 2.
    assert "Sam North 1" in nombres
    plano = json.dumps(nombres, ensure_ascii=False)
    for persona in intake_world["west-studio"]["people"].values():
        assert persona["name"] not in plano


def test_la_web_no_espera_a_la_ia_con_su_candado(web, conn, intake_world, administradora, ia):
    from leda import web_app

    navegador = _navegador_de_administracion(web, conn, administradora)
    candado = []
    ia.al_llamar = lambda: candado.append(web_app._WEB.locked())
    ia.respuestas.append({"titulo": "Colgar el árbol"})
    assert _pedir(navegador, _norte(intake_world)["id"],
                  titulo="colgar el arvol").status_code == 200
    assert candado == [False]


# --- J2-18 y los avisos de RDD de la J2-17 -----------------------------------------------------------

def test_cada_palabra_que_pasa_se_corrige_y_la_que_no_queda_como_se_escribio(
        web, conn, intake_world, administradora, ia):
    """La ronda de la J2-17: "q" anulaba la corrección del campo entero. Ahora "q" queda como se
    escribió, lo demás se corrige, y el incidente cuenta la palabra rechazada sin decir cuál."""
    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append({"titulo": "Cambiar la batería del UPS que no anda"})
    r = _pedir(navegador, _norte(intake_world)["id"],
               titulo="cambiar la bateria del ups q no anda")
    assert r.status_code == 200, r.text
    assert r.json() == {"corregidos": {"titulo": {
        "texto": "Cambiar la batería del UPS q no anda",
        "cambios": [{"antes": "cambiar", "despues": "Cambiar"},
                    {"antes": "bateria", "despues": "batería"},
                    {"antes": "ups", "despues": "UPS"}]}}, "sin_revisar": []}
    incidente = _fila(conn, "select * from incident where etapa = 'ortografia_al_cargar'")
    assert incidente is not None
    assert incidente["referencia_cruda"] == "titulo: 1 palabra no aceptada"
    plano = json.dumps(incidente, default=str, ensure_ascii=False)
    for palabra in ("bateria", "batería", "que no anda"):
        assert palabra not in plano
    detalle = _fila(conn, "select detalle from audit_log where accion = 'corregir_al_cargar'")[
        "detalle"]
    assert detalle["palabras_rechazadas"] == [{"campo": "titulo", "cantidad": 1}]


def test_una_ia_que_no_se_puede_preparar_no_bloquea_y_deja_un_incidente(
        web, conn, intake_world, administradora, monkeypatch):
    """Advertencia de RDD de la J2-17: preparar la IA no tenía guarda y una falla era un 503 sin
    rastro. Ahora es una IA que no responde: queda como se escribió, con el aviso y el
    incidente."""
    from leda import web_app

    def rota(conn, espacio):
        raise RuntimeError("la configuración de la IA no se puede leer")
    monkeypatch.setattr(web_app, "_ia_de_la_ortografia", rota)
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = _pedir(navegador, _norte(intake_world)["id"], titulo="colgar el arvol")
    assert r.status_code == 200, r.text
    assert r.json() == {"corregidos": {}, "sin_revisar": ["titulo"], "aviso": TEXTO_SIN_REVISAR}
    incidente = _fila(conn, "select * from incident where etapa = 'ortografia_al_cargar'")
    assert incidente is not None and "RuntimeError" in incidente["referencia_cruda"]


def test_una_sesion_cortada_mientras_responde_la_ia_no_recibe_nada(web, conn, intake_world,
                                                                  administradora, ia):
    """Advertencia de RDD de la J2-17: el caso de la sesión cortada mientras la IA corregía."""
    from tests.garantias.test_carga_de_tareas import _revocar

    navegador = _navegador_de_administracion(web, conn, administradora)
    ia.respuestas.append({"titulo": "Colgar el árbol"})
    ia.al_llamar = lambda: _revocar(conn, administradora)
    r = _pedir(navegador, _norte(intake_world)["id"], titulo="colgar el arvol")
    assert r.status_code == 401
    assert "corregidos" not in r.text
    assert _contar(conn, "audit_log", "accion = 'corregir_al_cargar'") == 0
    assert _contar(conn, "incident", "etapa = 'ortografia_al_cargar'") == 0
