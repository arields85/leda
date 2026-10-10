"""El acceso del administrador de plataforma a la página de una tarea (ADR 0019, 7b; porción 5 de
la C-3; migración 0052): la capa de garantías.

- **Atado a su usuario de plataforma, a una tarea de un espacio**, no a una membresía
  (`acceso_tarea.admin_app_user_id`): exactamente uno de los dos, una persona del equipo o un
  administrador. El acceso de un administrador sólo lo escribe la conexión administrativa y sólo
  para quien tiene el rol de plataforma; se revalida en cada pedido (sin el rol, la página
  genérica). Nunca abre nada de otra tarea ni de otro espacio.
- **Cada vista y cada descarga del administrador van además a `audit_log`** (7e y constitución
  §12), con su espacio y la versión del pack; las de una persona del equipo, no.
- **Revocar** (7a): los enlaces de una persona, de una tarea o de un administrador, auditado; un
  enlace ya mandado deja de abrir.
- **El retiro de contenido por la administración** (ADR 0019, decisión 3): la pieza no se borra;
  la página dice "retirado por la administración" y nunca su contenido (ni el texto, ni el
  enlace, ni el nombre del archivo); el archivo no se sirve, tampoco por otra pieza que apunte al
  mismo archivo; queda en `audit_log` con quién y por qué. Sólo lo hace la administración.
"""

from __future__ import annotations

import hashlib

import psycopg
import pytest

from leda import pagina_de_tarea as P
from leda import tarea_vista
from leda.db import admin, espacio

from tests.garantias.test_pagina_de_la_tarea import (  # noqa: F401 -- `mundo` es la fixture
    _emitir, _leer, _leer_archivo, _persona, mundo)


@pytest.fixture
def ada(conn, mundo) -> str:
    """Ada, administradora de plataforma: no es integrante de ningún equipo."""
    with admin(conn) as cur:
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (79001, 'Ada Admin') returning id""")
        usuario = str(cur.fetchone()["id"])
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                    (usuario,))
    conn.commit()
    return usuario


def _emitir_admin(conn, mundo, usuario: str, tarea: dict | None = None,
                  slug: str = "north-lab") -> str | None:
    tarea = tarea or mundo["norte"]
    with admin(conn) as cur:
        token = P.emitir_para_administrador(cur, usuario, mundo[slug]["id"], tarea["id"])
    conn.commit()
    return token


def _auditoria(conn, accion: str) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select * from audit_log where accion = %s order by at, id", (accion,))
        return cur.fetchall()


# --- La credencial --------------------------------------------------------------------------

def test_el_acceso_es_de_una_persona_o_de_un_administrador_nunca_de_los_dos(conn, mundo, ada):
    with admin(conn) as cur:
        for membresia, usuario in ((None, None), (_persona(mundo, "Sam Noble"), ada)):
            with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
                cur.execute(
                    """insert into acceso_tarea (workspace_id, membership_id, admin_app_user_id,
                                                 task_id, token_hash)
                       values (%s, %s, %s, %s, %s)""",
                    (mundo["north-lab"]["id"], membresia, usuario, mundo["norte"]["id"],
                     "a" * 64))
    conn.rollback()


def test_el_administrador_recibe_un_enlace_atado_a_su_usuario(conn, mundo, ada):
    token = _emitir_admin(conn, mundo, ada)
    assert token
    with admin(conn) as cur:
        cur.execute("select * from acceso_tarea")
        [fila] = cur.fetchall()
    assert str(fila["admin_app_user_id"]) == ada and fila["membership_id"] is None
    assert str(fila["task_id"]) == mundo["norte"]["id"]
    assert str(fila["workspace_id"]) == mundo["north-lab"]["id"]
    assert fila["token_hash"] == hashlib.sha256(token.encode()).hexdigest()
    for valor in fila.values():
        assert token not in str(valor)
    datos = _leer(conn, token)
    assert datos["tarea"]["titulo"] == "Calibrar la balanza"
    assert datos["persona"] == "Ada Admin"
    # La emisión queda auditada, con quién y sobre qué tarea.
    [emision] = _auditoria(conn, "emitir_acceso_tarea_de_administrador")
    assert str(emision["actor_app_user_id"]) == ada
    assert str(emision["workspace_id"]) == mundo["north-lab"]["id"]
    assert str(emision["sujeto_id"]) == mundo["norte"]["id"]


def test_quien_no_es_administrador_no_recibe_un_acceso_de_administrador(conn, mundo):
    """Sam Noble es del equipo, no administradora de plataforma."""
    usuario = mundo["north-lab"]["people"]["Sam Noble"]["app_user_id"]
    assert _emitir_admin(conn, mundo, usuario) is None
    with admin(conn) as cur:
        cur.execute("select count(*) n from acceso_tarea")
        assert cur.fetchone()["n"] == 0
        # Ni escribiéndolo a mano: la base lo rechaza.
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            cur.execute("""insert into acceso_tarea (workspace_id, admin_app_user_id, task_id,
                                                     token_hash)
                           values (%s, %s, %s, %s)""",
                        (mundo["north-lab"]["id"], usuario, mundo["norte"]["id"], "b" * 64))
    conn.rollback()


def test_una_tarea_de_otro_espacio_no_se_emite_para_este(conn, mundo, ada):
    assert _emitir_admin(conn, mundo, ada, mundo["oeste"]) is None


def test_el_enlace_del_administrador_lee_solo_su_tarea(conn, mundo, ada):
    token = _emitir_admin(conn, mundo, ada)
    texto = str(_leer(conn, token))
    assert "Pintar el galpón" not in texto and "Secreto del oeste" not in texto
    assert _leer_archivo(conn, token, mundo["norte"]["piezas"]["foto"]) is not None
    for ajena in (mundo["vecina"]["piezas"]["foto"], mundo["oeste"]["piezas"]["foto"],
                  mundo["oeste"]["piezas"]["pdf"]):
        assert _leer_archivo(conn, token, ajena) is None


def test_sin_el_rol_de_plataforma_el_enlace_deja_de_abrir(conn, mundo, ada):
    token = _emitir_admin(conn, mundo, ada)
    assert _leer(conn, token) is not None
    with admin(conn) as cur:
        cur.execute("delete from platform_role where app_user_id = %s", (ada,))
    conn.commit()
    assert _leer(conn, token) is None
    assert _leer_archivo(conn, token, mundo["norte"]["piezas"]["foto"]) is None


# --- Cada vista del administrador, en la auditoría -------------------------------------------

def test_cada_vista_y_cada_descarga_del_administrador_van_a_la_auditoria(conn, mundo, ada):
    token = _emitir_admin(conn, mundo, ada)
    _leer(conn, token)
    _leer_archivo(conn, token, mundo["norte"]["piezas"]["pdf"])
    _leer_archivo(conn, token, mundo["vecina"]["piezas"]["pdf"])     # no se sirve: no cuenta
    vistas = _auditoria(conn, "ver_pagina_de_tarea")
    bajadas = _auditoria(conn, "bajar_archivo_de_tarea")
    assert len(vistas) == 1 and len(bajadas) == 1
    for fila in vistas + bajadas:
        assert str(fila["actor_app_user_id"]) == ada
        assert fila["actor_kind"] == "persona"
        assert str(fila["workspace_id"]) == mundo["north-lab"]["id"]
        assert fila["pack_hash"] == "hash-0"
        assert fila["nucleo_hash"]
    assert str(vistas[0]["sujeto_id"]) == mundo["norte"]["id"]
    assert str(bajadas[0]["sujeto_id"]) == mundo["norte"]["piezas"]["pdf"]
    # Además del registro de vistas de siempre.
    with admin(conn) as cur:
        cur.execute("select que from vista_de_tarea order by at")
        assert [f["que"] for f in cur.fetchall()] == ["pagina", "archivo"]


def test_las_vistas_de_una_persona_del_equipo_no_van_a_la_auditoria(conn, mundo):
    token = _emitir(conn, mundo, "Taylor Quinn")
    _leer(conn, token)
    _leer_archivo(conn, token, mundo["norte"]["piezas"]["pdf"])
    assert _auditoria(conn, "ver_pagina_de_tarea") == []
    assert _auditoria(conn, "bajar_archivo_de_tarea") == []


# --- Revocar --------------------------------------------------------------------------------

def _revocar(conn, mundo, **criterio) -> int:
    with admin(conn) as cur:
        cantidad = P.revocar(cur, mundo["north-lab"]["id"], **criterio)
    conn.commit()
    return cantidad


def test_revocar_los_enlaces_de_una_persona_corta_los_ya_mandados(conn, mundo):
    de_sam = _emitir(conn, mundo, "Sam Noble")
    de_taylor = _emitir(conn, mundo, "Taylor Quinn")
    assert _revocar(conn, mundo, membership_id=_persona(mundo, "Sam Noble")) == 1
    assert _leer(conn, de_sam) is None
    assert _leer(conn, de_taylor) is not None
    [fila] = _auditoria(conn, "revocar_enlaces_de_tarea")
    assert fila["detalle"] == {"de": "persona", "cantidad": 1}
    assert str(fila["sujeto_id"]) == _persona(mundo, "Sam Noble")
    assert str(fila["workspace_id"]) == mundo["north-lab"]["id"]


def test_revocar_los_enlaces_de_una_tarea(conn, mundo, ada):
    de_la_tarea = [_emitir(conn, mundo, "Sam Noble"), _emitir(conn, mundo, "Morgan Hale"),
                   _emitir_admin(conn, mundo, ada)]
    de_otra = _emitir(conn, mundo, "Morgan Hale", mundo["vecina"])
    assert _revocar(conn, mundo, task_id=mundo["norte"]["id"]) == 3
    assert all(_leer(conn, t) is None for t in de_la_tarea)
    assert _leer(conn, de_otra) is not None
    # Lo revocado no se vuelve a revocar ni se cuenta otra vez.
    assert _revocar(conn, mundo, task_id=mundo["norte"]["id"]) == 0
    assert len(_auditoria(conn, "revocar_enlaces_de_tarea")) == 1


def test_revocar_los_accesos_de_un_administrador(conn, mundo, ada):
    del_admin = _emitir_admin(conn, mundo, ada)
    de_sam = _emitir(conn, mundo, "Sam Noble")
    assert _revocar(conn, mundo, admin_app_user_id=ada) == 1
    assert _leer(conn, del_admin) is None
    assert _leer(conn, de_sam) is not None


def test_se_revocan_los_accesos_de_quien_ya_no_es_administrador(conn, mundo, ada):
    _emitir_admin(conn, mundo, ada)
    with admin(conn) as cur:
        cur.execute("delete from platform_role where app_user_id = %s", (ada,))
    conn.commit()
    assert _revocar(conn, mundo, admin_app_user_id=ada) == 1


def test_revocar_en_un_espacio_no_toca_los_enlaces_de_otro(conn, mundo):
    del_oeste = _emitir(conn, mundo, "Morgan Hale", mundo["oeste"], slug="west-studio")
    # Un id de una tarea de otro espacio no revoca nada en éste.
    assert _revocar(conn, mundo, task_id=mundo["oeste"]["id"]) == 0
    assert _leer(conn, del_oeste) is not None


def test_revocar_pide_exactamente_un_criterio(conn, mundo, ada):
    with admin(conn) as cur:
        with pytest.raises(ValueError):
            P.revocar(cur, mundo["north-lab"]["id"])
        with pytest.raises(ValueError):
            P.revocar(cur, mundo["north-lab"]["id"], task_id=mundo["norte"]["id"],
                      admin_app_user_id=ada)
    conn.rollback()


# --- El retiro de contenido por la administración ---------------------------------------------

def _retirar(conn, mundo, usuario: str, pieza: str, motivo: str = "muestra una contraseña"):
    with admin(conn) as cur:
        retiradas = P.retirar_contenido(cur, mundo["north-lab"]["id"], pieza, usuario, motivo)
    conn.commit()
    return retiradas


def test_una_pieza_retirada_por_la_administracion_nunca_muestra_su_contenido(conn, mundo, ada):
    foto, texto = mundo["norte"]["piezas"]["foto"], mundo["norte"]["piezas"]["texto"]
    assert _retirar(conn, mundo, ada, foto) == [foto]
    assert _retirar(conn, mundo, ada, texto) == [texto]
    token = _emitir(conn, mundo, "Taylor Quinn")
    assert _leer_archivo(conn, token, foto) is None
    datos = _leer(conn, token)
    piezas = {p["id"]: p for p in datos["evidencia"]}
    for pieza in (foto, texto):
        assert piezas[pieza]["retirada"] and piezas[pieza]["retirada_por_la_administracion"]
        assert piezas[pieza]["texto"] is None and piezas[pieza]["nombre"] is None
        assert piezas[pieza]["enlace"] is None
    assert not piezas[mundo["norte"]["piezas"]["pdf"]]["retirada_por_la_administracion"]
    html = tarea_vista.pagina(datos, token=token)
    assert html.count("retirado por la administración") == 2
    assert "pantalla.jpg" not in html and "Quedó andando" not in html
    assert f"evidencia/{foto}" not in html
    assert "informe.pdf" in html


def test_el_retiro_no_borra_nada_y_queda_auditado(conn, mundo, ada):
    foto = mundo["norte"]["piezas"]["foto"]
    _retirar(conn, mundo, ada, foto, motivo="una contraseña en un papel")
    with admin(conn) as cur:
        cur.execute("select count(*) n from evidence where id = %s", (foto,))
        assert cur.fetchone()["n"] == 1
        cur.execute("""select count(*) n from archivo a join evidence e on e.archivo_id = a.id
                        where e.id = %s""", (foto,))
        assert cur.fetchone()["n"] == 1
        cur.execute("select * from evidencia_retirada where evidence_id = %s", (foto,))
        [fila] = cur.fetchall()
    assert str(fila["retirada_por_app_user_id"]) == ada
    assert fila["retirada_por_membership_id"] is None
    assert fila["motivo"] == "una contraseña en un papel"
    [auditada] = _auditoria(conn, "retirar_contenido_de_evidencia")
    assert str(auditada["actor_app_user_id"]) == ada
    assert str(auditada["sujeto_id"]) == foto
    assert auditada["detalle"]["motivo"] == "una contraseña en un papel"
    assert str(auditada["workspace_id"]) == mundo["north-lab"]["id"]


def test_el_mismo_archivo_por_otra_pieza_tampoco_se_sirve(conn, mundo, ada):
    """Un archivo se guarda una vez por huella: la misma foto mandada para otra tarea apunta al
    mismo archivo. Retirada su contenido, no se sirve por ninguna pieza."""
    ws = mundo["north-lab"]["id"]
    foto = mundo["norte"]["piezas"]["foto"]
    with admin(conn) as cur:
        cur.execute("select archivo_id from evidence where id = %s", (foto,))
        archivo = cur.fetchone()["archivo_id"]
        cur.execute(
            """insert into evidence (workspace_id, task_id, tipo, clase, archivo_id,
                                     entregado_por)
               values (%s, %s, 'imagen', 'imagen', %s, %s) returning id""",
            (ws, mundo["vecina"]["id"], archivo, _persona(mundo, "Sam North")))
        otra = str(cur.fetchone()["id"])
    conn.commit()
    assert set(_retirar(conn, mundo, ada, foto)) == {foto, otra}
    token = _emitir(conn, mundo, "Morgan Hale", mundo["vecina"])
    assert _leer_archivo(conn, token, otra) is None
    piezas = {p["id"]: p for p in _leer(conn, token)["evidencia"]}
    assert piezas[otra]["retirada_por_la_administracion"]


def test_una_pieza_ya_retirada_por_quien_la_entrego_tambien_se_retira(conn, mundo, ada):
    foto = mundo["norte"]["piezas"]["foto"]
    with admin(conn) as cur:
        cur.execute("""insert into evidencia_retirada (workspace_id, evidence_id,
                                                       retirada_por_membership_id, motivo)
                       values (%s, %s, %s, 'no era esa')""",
                    (mundo["north-lab"]["id"], foto, _persona(mundo, "Sam Noble")))
    conn.commit()
    assert _retirar(conn, mundo, ada, foto) == [foto]
    # Una segunda vez no agrega nada.
    assert _retirar(conn, mundo, ada, foto) == []
    token = _emitir(conn, mundo, "Sam Noble")
    pieza = next(p for p in _leer(conn, token)["evidencia"] if p["id"] == foto)
    assert pieza["retirada_por_la_administracion"]


def test_solo_la_administracion_retira_contenido(conn, mundo, ada):
    """Quien no es administrador de plataforma no puede, ni la aplicación aunque nombre a uno."""
    foto = mundo["norte"]["piezas"]["foto"]
    usuario = mundo["north-lab"]["people"]["Morgan Hale"]["app_user_id"]
    with admin(conn) as cur:
        with pytest.raises(ValueError):
            P.retirar_contenido(cur, mundo["north-lab"]["id"], foto, usuario, "no")
    conn.rollback()
    with espacio(conn, mundo["north-lab"]["id"]) as cur:
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            cur.execute("""insert into evidencia_retirada (workspace_id, evidence_id,
                                                           retirada_por_app_user_id, motivo)
                           values (%s, %s, %s, 'no')""",
                        (mundo["north-lab"]["id"], foto, ada))
    conn.rollback()


def test_una_pieza_de_otro_espacio_no_se_retira_desde_este(conn, mundo, ada):
    with admin(conn) as cur:
        with pytest.raises(ValueError):
            P.retirar_contenido(cur, mundo["north-lab"]["id"],
                                mundo["oeste"]["piezas"]["foto"], ada, "no")
    conn.rollback()
