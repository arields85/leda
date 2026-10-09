"""La página web de una tarea (ADR 0019, 7c y 7d): lo que se sirve y cómo.

Lo que se prueba acá es la entrada HTTP sobre las funciones de la base (`test_pagina_de_la_
tarea.py` prueba quién ve qué), con `TestClient` y sin red:

- **Sólo lectura, en palabras de todos los días.** La tarea, su historia y su evidencia, con
  "en revisión" y no el nombre del estado en la base; sin identificadores, huellas ni
  nombres de la cocina (constitución §10); todo lo que viene de la base, escapado; nunca la
  conversación.
- **Un enlace que no sirve** (inexistente, revocado, de alguien que ya no puede ver la tarea, o
  de una membresía inactiva) recibe siempre la misma página genérica, con el mismo código.
- **Las cabeceras:** `Cache-Control: no-store`, `Referrer-Policy: no-referrer`, `X-Robots-Tag:
  noindex`, `nosniff` y una política de contenido que no deja ejecutar nada.
- **Los archivos:** con el tipo que detectó el código; las imágenes se ven y lo demás se
  descarga como adjunto; el id de una evidencia de otra tarea devuelve la página genérica.
"""

from __future__ import annotations

import pytest

from leda.db import admin

from tests.garantias.test_pagina_de_la_tarea import (JPEG, PDF, _emitir, _persona,  # noqa: F401
                                                     mundo)

CABECERAS = {"cache-control": "no-store", "referrer-policy": "no-referrer",
             "x-robots-tag": "noindex, nofollow", "x-content-type-options": "nosniff"}


@pytest.fixture
def web(conn, monkeypatch):
    from fastapi.testclient import TestClient

    from leda import entrada

    monkeypatch.setattr(entrada, "_conn_de_paginas", lambda: conn)
    return TestClient(entrada.app)


def _tiene_las_cabeceras(r) -> None:
    for nombre, valor in CABECERAS.items():
        assert r.headers.get(nombre) == valor, nombre
    politica = r.headers.get("content-security-policy", "")
    assert "default-src 'none'" in politica
    assert "script-src" not in politica, "la página no ejecuta nada"


def _generica(web, camino: str):
    r = web.get(camino)
    assert r.status_code == 404
    assert "no se puede abrir" in r.text
    _tiene_las_cabeceras(r)
    return r


# --- La página ------------------------------------------------------------------------------

def test_la_pagina_muestra_la_tarea_en_palabras_de_todos_los_dias(web, conn, mundo):
    r = web.get(f"/tarea/{_emitir(conn, mundo, 'Taylor Quinn')}")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    _tiene_las_cabeceras(r)
    assert "Calibrar la balanza" in r.text
    assert "en revisión" in r.text and "esperando aprobación" not in r.text
    assert "en_revision" not in r.text and "en_curso" not in r.text
    assert "Quality Guild" in r.text and "Sam Noble 1" in r.text
    assert "Taylor Quinn 1" in r.text          # quién aprueba
    assert "Que ande" in r.text                # el criterio de aceptación
    assert "Quedó andando" in r.text           # lo que escribió al entregar
    assert "pantalla.jpg" in r.text and "informe.pdf" in r.text
    assert "Pintar el galpón" not in r.text and "Secreto del oeste" not in r.text


def test_un_ejemplo_aceptado_figura_como_aceptado_y_no_como_escrito(web, conn, mundo):
    """D8 (G2, prueba por Telegram del 2026-10-08): el ejemplo que Leda propuso y la persona
    aceptó tal cual se leía como "Lo que escribió". La base guarda que fue aceptado (migración
    0039) y la página lo dice así."""
    with admin(conn) as cur:
        cur.execute(
            """insert into evidence (workspace_id, task_id, tipo, clase, texto, entregado_por,
                                     es_ejemplo_aceptado)
               values (%s, %s, 'texto', 'texto', 'Completa 20 ciclos sin fallas', %s, true)""",
            (mundo["norte"]["ws"], mundo["norte"]["id"], _persona(mundo, "Sam Noble")))
    conn.commit()
    r = web.get(f"/tarea/{_emitir(conn, mundo, 'Taylor Quinn')}")
    assert "Aceptó esta descripción: «Completa 20 ciclos sin fallas»" in r.text
    assert "Lo que escribió: «Completa 20 ciclos sin fallas»" not in r.text
    assert "Lo que escribió: «Quedó andando»" in r.text


def test_la_pagina_no_muestra_identificadores_ni_nombres_de_la_cocina(web, conn, mundo):
    token = _emitir(conn, mundo, "Taylor Quinn")
    r = web.get(f"/tarea/{token}")
    cuerpo = r.text
    for identificador in (mundo["norte"]["id"], mundo["north-lab"]["id"],
                          _persona(mundo, "Taylor Quinn"), _persona(mundo, "Sam Noble")):
        assert identificador not in cuerpo
    with admin(conn) as cur:
        cur.execute("select token_hash, sha256 from acceso_tarea, archivo limit 1")
        fila = cur.fetchone()
    assert fila["token_hash"] not in cuerpo and fila["sha256"] not in cuerpo
    for de_la_cocina in ("workspace", "membership", "evidence", "acceso_tarea",
                         "leer_pagina", "traceback", "psycopg", "imagen", "archivo_id"):
        assert de_la_cocina not in cuerpo.lower(), de_la_cocina


def test_la_pagina_muestra_la_imagen_y_ofrece_el_archivo_para_bajar(web, conn, mundo):
    token = _emitir(conn, mundo, "Taylor Quinn")
    r = web.get(f"/tarea/{token}")
    foto = mundo["norte"]["piezas"]["foto"]
    pdf = mundo["norte"]["piezas"]["pdf"]
    assert f'<img src="{token}/evidencia/{foto}"' in r.text
    assert f'href="{token}/evidencia/{pdf}"' in r.text


def test_la_pagina_cuenta_la_historia(web, conn, mundo):
    with admin(conn) as cur:
        ws, tarea = mundo["north-lab"]["id"], mundo["norte"]["id"]
        cur.execute(
            """insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                     aprobador_membership_id, decision, comentario)
               values (%s, 'tarea', %s, %s, 'rechazado', 'falta el informe de la pesa')""",
            (ws, tarea, _persona(mundo, "Taylor Quinn")))
        cur.execute("""insert into blocker (workspace_id, task_id, causa, abierto_por)
                       values (%s, %s, 'falta la pesa patrón', %s)""",
                    (ws, tarea, _persona(mundo, "Sam Noble")))
    conn.commit()
    r = web.get(f"/tarea/{_emitir(conn, mundo, 'Taylor Quinn')}")
    assert "pidió cambios" in r.text and "falta el informe de la pesa" in r.text
    assert "falta la pesa patrón" in r.text


def test_la_pagina_cuenta_lo_que_quedo_asentado_de_un_bloqueo(web, conn, mundo):
    """Decisión 49 del usuario (C-5c): lo asentado queda en la historia de la tarea, en palabras
    de todos los días y sin decir a quién se le informó."""
    from tests.garantias.test_pagina_de_la_tarea import asentar_un_bloqueo
    asentar_un_bloqueo(conn, mundo)

    r = web.get(f"/tarea/{_emitir(conn, mundo, 'Taylor Quinn')}")

    assert r.status_code == 200
    assert "Sam Noble 1 dijo que la destraba Taylor Quinn 1" in r.text
    assert "Taylor Quinn 1 dijo que la destraba el vie 23/10" in r.text
    assert "la traigo del depósito" in r.text
    assert "Quedó asentado que sigue trabada: 5 días hábiles" in r.text
    for palabra in ("asentar_", "blocker", "dicho_del_bloqueo", "a_membership_id"):
        assert palabra not in r.text


def test_la_pagina_escapa_lo_que_viene_de_la_base(web, conn, mundo):
    """Un comentario o un nombre de objetivo los escribe una persona."""
    with admin(conn) as cur:
        cur.execute("update objective set titulo = %s where id = %s",
                    ("<script>alert('x')</script>", mundo["north-lab"]["objectives"][0]))
        cur.execute(
            """insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                     aprobador_membership_id, decision, comentario)
               values (%s, 'tarea', %s, %s, 'rechazado', '<img src=x onerror=alert(1)>')""",
            (mundo["north-lab"]["id"], mundo["norte"]["id"], _persona(mundo, "Taylor Quinn")))
    conn.commit()
    r = web.get(f"/tarea/{_emitir(conn, mundo, 'Taylor Quinn')}")
    assert r.status_code == 200
    assert "<script>alert" not in r.text and "<img src=x" not in r.text
    assert "&lt;script&gt;" in r.text and "&lt;img src=x" in r.text


def test_la_pagina_no_muestra_la_conversacion(web, conn, mundo):
    with admin(conn) as cur:
        sam = mundo["north-lab"]["people"]["Sam Noble"]
        cur.execute("""insert into inbound_message (workspace_id, telegram_message_id, chat_id,
                                                    app_user_id, texto)
                       values (%s, 99, %s, %s, 'esto lo hablamos por chat')""",
                    (mundo["north-lab"]["id"], sam["telegram"], sam["app_user_id"]))
    conn.commit()
    r = web.get(f"/tarea/{_emitir(conn, mundo, 'Taylor Quinn')}")
    assert "esto lo hablamos por chat" not in r.text


def test_una_pieza_retirada_figura_como_retirada_y_no_se_ofrece(web, conn, mundo):
    with admin(conn) as cur:
        cur.execute("""insert into evidencia_retirada (workspace_id, evidence_id,
                                                       retirada_por_membership_id)
                       values (%s, %s, %s)""",
                    (mundo["north-lab"]["id"], mundo["norte"]["piezas"]["foto"],
                     _persona(mundo, "Sam Noble")))
    conn.commit()
    token = _emitir(conn, mundo, "Taylor Quinn")
    r = web.get(f"/tarea/{token}")
    assert "Retirada" in r.text
    assert f'{token}/evidencia/{mundo["norte"]["piezas"]["foto"]}' not in r.text


def test_una_pieza_retirada_no_muestra_su_contenido_ni_se_sirve(web, conn, mundo):
    """ADR 0019, decisión 3: una pieza retirada figura como retirada, y nada más. Ni lo que
    decía un texto, ni la dirección de un enlace, ni el nombre o el contenido de un archivo: si
    se retiró porque no tenía que estar, la página no lo sigue mostrando."""
    norte, ws = mundo["norte"], mundo["north-lab"]["id"]
    sam = _persona(mundo, "Sam Noble")
    with admin(conn) as cur:
        cur.execute("""insert into evidence (workspace_id, task_id, tipo, clase, uri,
                                             entregado_por)
                       values (%s, %s, 'enlace', 'enlace',
                               'https://ejemplo.invalid/clave-que-no-iba', %s)
                       returning id""", (ws, norte["id"], sam))
        enlace = str(cur.fetchone()["id"])
        for pieza in (*norte["piezas"].values(), enlace):
            cur.execute("""insert into evidencia_retirada (workspace_id, evidence_id,
                                                           retirada_por_membership_id)
                           values (%s, %s, %s)""", (ws, pieza, sam))
    conn.commit()
    token = _emitir(conn, mundo, "Taylor Quinn")
    r = web.get(f"/tarea/{token}")
    assert r.status_code == 200
    for contenido in ("Quedó andando", "pantalla.jpg", "informe.pdf", "clave-que-no-iba",
                      "/evidencia/"):
        assert contenido not in r.text, contenido
    assert r.text.count("Retirada el") == 4
    for pieza in (norte["piezas"]["foto"], norte["piezas"]["pdf"]):
        _generica(web, f"/tarea/{token}/evidencia/{pieza}")


def test_una_falla_al_armar_la_pagina_recibe_la_pagina_generica(web, conn, mundo, monkeypatch,
                                                                capsys):
    """Constitución §10: si algo falla al armar la página, la persona ve la página genérica,
    nunca un error del servidor. En la consola queda una línea sin el token ni el detalle, y la
    vista no queda registrada, porque no se sirvió (7e)."""
    from leda import tarea_vista

    def se_rompe(*a, **k):
        raise RuntimeError("detalle interno")

    monkeypatch.setattr(tarea_vista, "pagina", se_rompe)
    token = _emitir(conn, mundo, "Taylor Quinn")
    r = web.get(f"/tarea/{token}")
    assert r.status_code == 503
    assert "no se puede abrir" in r.text and "detalle interno" not in r.text
    _tiene_las_cabeceras(r)
    consola = capsys.readouterr().out
    assert "RuntimeError" in consola
    assert token not in consola and "detalle interno" not in consola
    with admin(conn) as cur:
        cur.execute("select count(*) as n from vista_de_tarea")
        assert cur.fetchone()["n"] == 0


def test_una_falla_al_servir_un_archivo_recibe_la_pagina_generica(web, conn, mundo,
                                                                  monkeypatch, capsys):
    from leda import pagina_de_tarea

    monkeypatch.setattr(pagina_de_tarea, "leer_archivo",
                        lambda cur, token, evidencia: {"contenido": b"x"})
    token = _emitir(conn, mundo, "Taylor Quinn")
    r = web.get(f"/tarea/{token}/evidencia/{mundo['norte']['piezas']['pdf']}")
    assert r.status_code == 503
    assert "no se puede abrir" in r.text
    _tiene_las_cabeceras(r)
    consola = capsys.readouterr().out
    assert "KeyError" in consola and token not in consola


# --- Un enlace que no sirve ----------------------------------------------------------------

def test_un_token_inventado_recibe_la_pagina_generica(web, conn, mundo):
    _generica(web, "/tarea/esto-no-es-un-token")


def test_un_token_revocado_recibe_la_misma_pagina_generica(web, conn, mundo):
    token = _emitir(conn, mundo, "Sam Noble")
    inventado = web.get("/tarea/esto-no-es-un-token")
    with admin(conn) as cur:
        cur.execute("update acceso_tarea set revocado_en = now()")
    conn.commit()
    assert _generica(web, f"/tarea/{token}").text == inventado.text


def test_quien_ya_no_puede_verla_recibe_la_misma_pagina_generica(web, conn, mundo):
    """Un cambio de quien aprueba se refleja en el siguiente pedido; una membresía inactiva,
    también."""
    aprobador = _emitir(conn, mundo, "Taylor Quinn")
    autoridad = _emitir(conn, mundo, "Morgan Hale")
    assert web.get(f"/tarea/{aprobador}").status_code == 200
    with admin(conn) as cur:
        cur.execute("update membership set aprobador_membership_id = %s where id = %s",
                    (_persona(mundo, "Morgan Hale"), _persona(mundo, "Sam Noble")))
        cur.execute("update membership set activo = false where id = %s",
                    (_persona(mundo, "Morgan Hale"),))
    conn.commit()
    inventado = web.get("/tarea/esto-no-es-un-token").text
    assert _generica(web, f"/tarea/{aprobador}").text == inventado
    assert _generica(web, f"/tarea/{autoridad}").text == inventado


def test_la_pagina_generica_no_filtra_detalle_tecnico(web, conn, mundo):
    cuerpo = _generica(web, "/tarea/token-inventado").text.lower()
    for filtracion in ("traceback", "psycopg", "select ", "postgres", "acceso_tarea",
                       "leer_pagina_de_tarea", ".py", "workspace_id"):
        assert filtracion not in cuerpo, filtracion


# --- Los archivos ---------------------------------------------------------------------------

def test_una_imagen_se_sirve_para_verla_con_su_tipo_detectado(web, conn, mundo):
    token = _emitir(conn, mundo, "Taylor Quinn")
    r = web.get(f"/tarea/{token}/evidencia/{mundo['norte']['piezas']['foto']}")
    assert r.status_code == 200
    assert r.content == JPEG + b"Calibrar la balanza"
    assert r.headers["content-type"] == "image/jpeg"
    assert r.headers["content-disposition"].startswith("inline")
    _tiene_las_cabeceras(r)
    assert "sandbox" in r.headers["content-security-policy"]


def test_otro_archivo_se_sirve_como_adjunto_para_bajar(web, conn, mundo):
    token = _emitir(conn, mundo, "Taylor Quinn")
    r = web.get(f"/tarea/{token}/evidencia/{mundo['norte']['piezas']['pdf']}")
    assert r.status_code == 200
    assert r.content == PDF + b"Calibrar la balanza"
    assert r.headers["content-type"] == "application/pdf"
    assert r.headers["content-disposition"].startswith("attachment")
    assert "informe.pdf" in r.headers["content-disposition"]
    _tiene_las_cabeceras(r)


def test_la_evidencia_de_otra_tarea_recibe_la_pagina_generica(web, conn, mundo):
    token = _emitir(conn, mundo, "Morgan Hale")
    inventado = web.get("/tarea/esto-no-es-un-token").text
    for ajena in (mundo["vecina"]["piezas"]["foto"], mundo["oeste"]["piezas"]["pdf"]):
        assert _generica(web, f"/tarea/{token}/evidencia/{ajena}").text == inventado
    assert _generica(web, f"/tarea/{token}/evidencia/no-es-un-id").text == inventado
    assert _generica(web, "/tarea/inventado/evidencia/"
                          f"{mundo['norte']['piezas']['foto']}").text == inventado
