"""La credencial del tablero: las cinco propiedades del modelo de amenaza.

Un enlace que abre los datos de un cliente es una credencial, y se prueba como
tal. Cada prueba de acá abajo corresponde a una fila de la tabla de amenazas de
`odd/tasks/acceso-al-tablero.md`.
"""

from __future__ import annotations

import contextlib
from datetime import datetime, timedelta, timezone

import psycopg
import pytest

from leda import tablero
from leda.db import admin, espacio
from leda.lectura import tareas_por_estado

AHORA = datetime(2028, 3, 15, 12, 0, tzinfo=timezone.utc)


@contextlib.contextmanager
def sin_espacio(conn):
    """La aplicación antes de saber a qué espacio pertenece el pedido.

    Es la situación real de una petición HTTP: llega un token y todavía no hay
    ningún espacio fijado. Resolverlo es justamente lo que lo averigua.
    """
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local role leda_app")
            yield cur


def _emitir(conn, mundo, slug, persona="Taylor Quinn", ahora=AHORA):
    with espacio(conn, mundo[slug]["id"]) as cur:
        token = tablero.emitir(
            cur, mundo[slug]["people"][persona]["membership_id"], ahora)
    conn.commit()
    return token


def test_un_token_recien_emitido_resuelve_a_su_espacio_y_su_membresia(
        intake_world, conn):
    norte = intake_world["north-lab"]
    token = _emitir(conn, intake_world, "north-lab")

    with sin_espacio(conn) as cur:
        resuelto = tablero.resolver(cur, token)

    assert resuelto is not None
    assert resuelto["workspace_id"] == str(norte["id"])
    assert resuelto["membership_id"] == str(
        norte["people"]["Taylor Quinn"]["membership_id"])


def test_un_token_vencido_no_resuelve(intake_world, conn):
    """Vence: la ventana acota el reenvío, no lo evita."""
    hace_rato = datetime.now(timezone.utc) - timedelta(hours=2)
    token = _emitir(conn, intake_world, "north-lab", ahora=hace_rato)

    with sin_espacio(conn) as cur:
        assert tablero.resolver(cur, token) is None


def test_el_token_en_claro_no_queda_en_la_base(intake_world, conn):
    """Si se filtrara la base, los enlaces emitidos no tendrían que servir."""
    token = _emitir(conn, intake_world, "north-lab")

    with admin(conn) as cur:
        cur.execute("select * from acceso_tablero")
        filas = cur.fetchall()

    assert filas, "no se guardó ningún acceso"
    for fila in filas:
        for columna, valor in fila.items():
            assert token not in str(valor), (
                f"el token en claro apareció en la columna {columna}")


def test_una_membresia_dada_de_baja_pierde_el_acceso(intake_world, conn):
    """La autoridad se revalida en cada pedido, no sólo al emitir."""
    norte = intake_world["north-lab"]
    token = _emitir(conn, intake_world, "north-lab")

    with sin_espacio(conn) as cur:
        assert tablero.resolver(cur, token) is not None

    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (norte["people"]["Taylor Quinn"]["membership_id"],))
    conn.commit()

    with sin_espacio(conn) as cur:
        assert tablero.resolver(cur, token) is None


def test_un_token_no_alcanza_los_datos_de_otro_espacio(intake_world, conn):
    """El espacio sale del token, así que no hay nada que cambiar en la URL."""
    norte = intake_world["north-lab"]
    oeste = intake_world["west-studio"]

    with admin(conn) as cur:
        for slug, titulo in (("north-lab", "Trabajo del norte"),
                             ("west-studio", "Trabajo del oeste")):
            mundo = intake_world[slug]
            cur.execute(
                """insert into task (workspace_id, objective_id, titulo,
                                     area_id, responsable_membership_id, estado)
                   values (%s, %s, %s, %s, %s, 'asignada')""",
                (mundo["id"], mundo["objectives"][0], titulo,
                 mundo["areas"]["field"],
                 mundo["people"]["Taylor Quinn"]["membership_id"]))
    conn.commit()

    token = _emitir(conn, intake_world, "north-lab")
    with sin_espacio(conn) as cur:
        resuelto = tablero.resolver(cur, token)
    assert resuelto["workspace_id"] == str(norte["id"])
    assert resuelto["workspace_id"] != str(oeste["id"])

    # Leer con ese espacio trae lo propio y nada de lo ajeno.
    with espacio(conn, resuelto["workspace_id"]) as cur:
        cur.execute("select titulo from task")
        titulos = {fila["titulo"] for fila in cur.fetchall()}
        assert titulos == {"Trabajo del norte"}
        assert sum(f["tareas"] for f in tareas_por_estado(cur)) == 1


def test_la_aplicacion_no_puede_leer_la_tabla_ni_emitir_para_otro_espacio(
        intake_world, conn):
    """La tabla no tiene política: lo que la protege es que nadie la consulta."""
    norte = intake_world["north-lab"]
    oeste = intake_world["west-studio"]

    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), \
                conn.transaction():
            cur.execute("select * from acceso_tablero")

    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.Error), conn.transaction():
            tablero.emitir(
                cur, oeste["people"]["Taylor Quinn"]["membership_id"], AHORA)


# ---------------------------------------------------------------------------
# La pantalla
# ---------------------------------------------------------------------------


@pytest.fixture
def cliente_web(conn, monkeypatch):
    from fastapi.testclient import TestClient

    from leda import gateway

    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    return TestClient(gateway.app)


def _cargar_trabajo(conn, mundo, slug, titulo):
    """Una tarea reconocible en un espacio, para distinguirla de la del otro.

    Va vencida a propósito. El puerto de lectura no tiene ninguna consulta que
    liste tareas comunes por título —son todas agregadas—, así que una tarea
    `asignada` y sin fecha no aparecería en la pantalla ni con su nombre. Para
    comprobar que lo de un espacio no se filtra al otro hace falta un dato que
    la pantalla efectivamente muestre.
    """
    vencida = datetime.now(timezone.utc) - timedelta(days=3)
    with admin(conn) as cur:
        espacio_datos = mundo[slug]
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, estado,
                                 fecha_objetivo)
               values (%s, %s, %s, %s, %s, 'asignada', %s)""",
            (espacio_datos["id"], espacio_datos["objectives"][0], titulo,
             espacio_datos["areas"]["field"],
             espacio_datos["people"]["Taylor Quinn"]["membership_id"],
             vencida))
    conn.commit()


def test_el_tablero_muestra_lo_propio_y_nada_de_lo_ajeno(
        intake_world, conn, cliente_web):
    """Criterio 2: ninguna respuesta incluye datos de otro espacio."""
    _cargar_trabajo(conn, intake_world, "north-lab", "Cablear la comprimidora")
    _cargar_trabajo(conn, intake_world, "west-studio", "Secreto del oeste")

    token = _emitir(conn, intake_world, "north-lab")
    r = cliente_web.get(f"/tablero/{token}")

    assert r.status_code == 200
    assert "Cablear la comprimidora" in r.text
    assert "Secreto del oeste" not in r.text
    assert "West Studio" not in r.text


def test_un_token_invalido_no_abre_el_tablero(intake_world, conn, cliente_web):
    r = cliente_web.get("/tablero/esto-no-es-un-token")

    assert r.status_code == 401
    assert "ya no sirve" in r.text


def test_un_token_vencido_no_abre_el_tablero(intake_world, conn, cliente_web):
    hace_rato = datetime.now(timezone.utc) - timedelta(hours=2)
    token = _emitir(conn, intake_world, "north-lab", ahora=hace_rato)

    r = cliente_web.get(f"/tablero/{token}")

    assert r.status_code == 401


def test_el_rechazo_no_filtra_detalle_tecnico(intake_world, conn, cliente_web):
    """La constitución §10 prohíbe mostrar trazas, rutas y nombres internos."""
    r = cliente_web.get("/tablero/token-inventado")

    cuerpo = r.text.lower()
    for filtracion in ("traceback", "psycopg", "select ", "postgres",
                       "acceso_tablero", "resolver_acceso_tablero",
                       ".py", "workspace_id"):
        assert filtracion not in cuerpo, f"la página filtró «{filtracion}»"


def test_la_pantalla_escapa_lo_que_escribio_una_persona(
        intake_world, conn, cliente_web):
    """Un título de tarea lo escribe una persona, y puede escribir etiquetas."""
    _cargar_trabajo(conn, intake_world, "north-lab",
                    "<script>alert('x')</script>")

    token = _emitir(conn, intake_world, "north-lab")
    r = cliente_web.get(f"/tablero/{token}")

    assert r.status_code == 200
    assert "<script>alert" not in r.text
    assert "&lt;script&gt;" in r.text


def test_la_pantalla_dice_lo_que_todavia_no_puede_medir(
        intake_world, conn, cliente_web):
    """Criterio 5: una ausencia no se muestra como un cero."""
    token = _emitir(conn, intake_world, "north-lab")
    r = cliente_web.get(f"/tablero/{token}")

    assert "no significa cero" in r.text
    assert "Dependencias entre tareas" in r.text
    # Y lo vacío de verdad se dice como buena noticia, no como cifra.
    assert "No hay bloqueos abiertos" in r.text


# ---------------------------------------------------------------------------
# Pedir el enlace
# ---------------------------------------------------------------------------


def _solicitante(conn, mundo, slug, persona="Taylor Quinn"):
    from leda.autoridad import Canal, Solicitante

    datos = mundo[slug]
    return Solicitante(
        app_user_id=str(datos["people"][persona]["app_user_id"]),
        canal=Canal.ESPACIO, workspace_id=str(datos["id"]),
        membership_id=str(datos["people"][persona]["membership_id"]))


def test_pedir_el_enlace_desde_un_grupo_no_emite_nada(intake_world, conn,
                                                      monkeypatch):
    """Un enlace en el grupo es acceso para cualquiera que lea el historial."""
    import dataclasses

    from leda import herramientas as H

    monkeypatch.setattr(
        "leda.config.config",
        dataclasses.replace(__import__("leda.config", fromlist=["config"]).config,
                            base_url="https://leda.example"))

    quien = _solicitante(conn, intake_world, "north-lab")
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        # chat_id negativo: en Telegram, un grupo.
        resultado = H.ejecutar(cur, quien, "pedir_tablero", {}, chat_id=-1001)
    conn.commit()

    assert resultado["emitido"] is False
    assert "privado" in resultado["explicacion"]

    with admin(conn) as cur:
        cur.execute("select count(*) n from acceso_tablero")
        assert cur.fetchone()["n"] == 0, "se emitió un token para un grupo"


def test_pedir_el_enlace_por_privado_devuelve_uno_que_abre(
        intake_world, conn, cliente_web, monkeypatch):
    """El circuito entero: pedir, recibir el enlace, abrirlo, ver."""
    import dataclasses

    from leda import config as config_mod
    from leda import herramientas as H

    monkeypatch.setattr(
        config_mod, "config",
        dataclasses.replace(config_mod.config, base_url="https://leda.example"))

    _cargar_trabajo(conn, intake_world, "north-lab", "Tarea visible")

    quien = _solicitante(conn, intake_world, "north-lab")
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        resultado = H.ejecutar(cur, quien, "pedir_tablero", {}, chat_id=71001)
    conn.commit()

    assert resultado["emitido"] is True
    assert resultado["enlace"].startswith("https://leda.example/tablero/")

    token = resultado["enlace"].rsplit("/", 1)[1]
    r = cliente_web.get(f"/tablero/{token}")
    assert r.status_code == 200
    assert "Tarea visible" in r.text


def test_la_vigencia_es_configuracion_del_cliente(intake_world, conn):
    """Un administrador la cambia sin tocar código ni migrar nada."""
    norte = intake_world["north-lab"]

    with espacio(conn, norte["id"]) as cur:
        assert tablero.minutos_de_vigencia(cur) == tablero.MINUTOS_POR_DEFECTO

    with admin(conn) as cur:
        cur.execute(
            """insert into workspace_setting (workspace_id, clave, valor)
               values (%s, %s, %s)""",
            (norte["id"], tablero.CLAVE_VIGENCIA, "120"))
    conn.commit()

    with espacio(conn, norte["id"]) as cur:
        assert tablero.minutos_de_vigencia(cur) == 120
