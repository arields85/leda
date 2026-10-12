"""La web compilada de la plataforma, servida por la misma aplicación en `/app/` (ADR 0022,
decisiones 12 y 17; porción 1, tarea P1-4).

Con una carpeta compilada de mentira (estas pruebas no dependen de compilar la web de verdad):

- `/app/` y cualquier página de la web devuelven su `index.html`, que no se guarda;
- los archivos con huella (`assets/`) se guardan por un año, con su tipo exacto;
- la política de contenido sólo deja scripts, estilos, letras, imágenes y pedidos del mismo
  origen;
- la API, el enlace de entrada y salir no quedan tapados por la web;
- nada fuera de la carpeta compilada se sirve, y sin compilar, la persona ve un mensaje humano.
"""

from __future__ import annotations

import pytest

BASE = "https://testserver"
INDICE = ('<!doctype html><html lang="es"><head>'
          '<script type="module" crossorigin src="/app/assets/index-abc123.js"></script>'
          '</head><body><div id="root"></div></body></html>')


@pytest.fixture
def dist(tmp_path, monkeypatch):
    from leda import web_app

    carpeta = tmp_path / "dist"
    (carpeta / "assets").mkdir(parents=True)
    (carpeta / "index.html").write_text(INDICE, encoding="utf-8")
    (carpeta / "assets" / "index-abc123.js").write_text("console.log('leda')", encoding="utf-8")
    (carpeta / "assets" / "index-abc123.css").write_text("body{margin:0}", encoding="utf-8")
    (carpeta / "assets" / "letra-abc123.woff2").write_bytes(b"wOF2fake")
    (tmp_path / "secreto.txt").write_text("no se sirve", encoding="utf-8")
    monkeypatch.setattr(web_app, "CARPETA_DE_LA_WEB", carpeta)
    return carpeta


@pytest.fixture
def web():
    from fastapi.testclient import TestClient

    from leda import entrada

    return TestClient(entrada.app, base_url=BASE, follow_redirects=False)


def _politica(r) -> dict[str, str]:
    partes = [p.strip() for p in r.headers["content-security-policy"].split(";") if p.strip()]
    return {p.split()[0]: " ".join(p.split()[1:]) for p in partes}


@pytest.mark.parametrize("camino", ["/app/", "/app/tareas", "/app/una/pagina/de/la/web"])
def test_la_web_y_sus_paginas_devuelven_el_indice_sin_guardarlo(dist, web, camino):
    r = web.get(camino)
    assert r.status_code == 200
    assert r.text == INDICE
    assert r.headers["content-type"].startswith("text/html")
    assert r.headers["cache-control"] == "no-store"
    assert r.headers["x-frame-options"] == "DENY"
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["referrer-policy"] == "no-referrer"


def test_la_politica_de_contenido_es_solo_del_mismo_origen(dist, web):
    r = web.get("/app/")
    politica = _politica(r)
    for directiva in ("script-src", "style-src", "font-src", "connect-src"):
        assert politica[directiva] == "'self'", directiva
    assert politica["default-src"] == "'self'"
    assert politica["frame-ancestors"] == "'none'" and politica["object-src"] == "'none'"
    texto = r.headers["content-security-policy"]
    assert "unsafe-inline" not in texto and "unsafe-eval" not in texto
    assert "http" not in texto and "*" not in texto


def test_app_sin_barra_lleva_a_la_web(dist, web):
    r = web.get("/app")
    assert r.status_code in (307, 308) and r.headers["location"] == "/app/"


@pytest.mark.parametrize("archivo, tipo", [("index-abc123.js", "text/javascript"),
                                            ("index-abc123.css", "text/css"),
                                            ("letra-abc123.woff2", "font/woff2")])
def test_los_archivos_con_huella_se_guardan_un_anio(dist, web, archivo, tipo):
    r = web.get(f"/app/assets/{archivo}")
    assert r.status_code == 200
    assert r.content == (dist / "assets" / archivo).read_bytes()
    assert r.headers["content-type"].split(";")[0] == tipo
    assert r.headers["cache-control"] == "public, max-age=31536000, immutable"
    assert r.headers["x-content-type-options"] == "nosniff"


@pytest.mark.parametrize("camino", ["/app/assets/no-existe.js", "/app/no-existe.css",
                                    "/app/assets/../../secreto.txt",
                                    "/app/assets/..%2f..%2fsecreto.txt",
                                    "/app/%2e%2e/secreto.txt",
                                    "/app/..%5c..%5csecreto.txt"])
def test_un_archivo_que_no_esta_no_es_el_indice_ni_sale_de_la_carpeta(dist, web, camino):
    r = web.get(camino)
    assert r.status_code == 404
    assert "no se sirve" not in r.text
    assert r.text != INDICE


def test_la_api_no_queda_tapada_por_la_web(dist, web):
    r = web.get("/app/api/yo")
    assert r.status_code == 401 and r.json() == {"error": "sin_sesion"}
    r = web.get("/app/api/no-existe")
    assert r.status_code == 404 and r.text != INDICE
    assert r.headers["content-type"].startswith("application/json")
    assert web.post("/app/salir").status_code == 401
    assert web.get("/app/salir").status_code == 404


def test_el_enlace_de_entrada_no_queda_tapado_por_la_web(dist, web):
    r = web.get("/app/entrar/un-token")
    assert r.status_code == 200 and ">Entrar<" in r.text and r.text != INDICE
    assert web.get("/app/entrar/").status_code == 404


def test_lo_que_no_es_de_la_web_sigue_igual(dist, web):
    assert web.get("/salud").json() == {"ok": True}
    assert web.get("/telegram/north-lab").status_code == 405     # sólo recibe POST


def test_sin_compilar_la_persona_ve_un_mensaje_humano(tmp_path, monkeypatch, web, capsys):
    from leda import web_app

    monkeypatch.setattr(web_app, "CARPETA_DE_LA_WEB", tmp_path / "no-existe")
    for camino in ("/app/", "/app/tareas", "/app/assets/index-abc123.js"):
        r = web.get(camino)
        assert r.status_code in (404, 503), camino
        texto = r.text.lower()
        for de_la_cocina in ("traceback", "no-existe", "dist", "error", str(tmp_path).lower()):
            assert de_la_cocina not in texto, (camino, de_la_cocina)
    r = web.get("/app/")
    assert r.status_code == 503 and "todavía no está lista" in r.text
    assert "script-src" not in r.headers["content-security-policy"]
    assert str(tmp_path) not in capsys.readouterr().out
