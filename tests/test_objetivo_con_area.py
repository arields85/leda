"""F-B11 (0027): el objetivo tiene un área, y el área de un objetivo es del
mismo espacio. El pack da el área de cada frente; reimportar completa las que
faltan (datos anteriores a la migración) sin tocar las que ya la tienen."""

from __future__ import annotations

import psycopg
import pytest

from prisma.db import admin, espacio

AREA_DE_CADA_FRENTE = {
    "Conectar y automatizar equipos para que produzcan y entreguen datos": "ot",
    "Planos eléctricos correctos y documentación útil": "ot",
    "Fortalecer servidores y mejorar EPPI": "it",
    "Construir o adaptar tableros preparados para la integración": "electricidad",
    "Robustecer la plataforma e integrar los datos": "corelabs",
}


def _areas_de_los_objetivos(conn, ws):
    with espacio(conn, ws) as cur:
        cur.execute(
            """select o.titulo, o.tipo, a.slug from objective o
                 left join area a on a.id = o.area_id order by o.titulo""")
        return {f["titulo"]: (f["tipo"], f["slug"]) for f in cur.fetchall()}


def test_el_pack_da_su_area_a_cada_objetivo_operativo(corework, conn):
    por_titulo = _areas_de_los_objetivos(conn, corework.workspace_id)
    operativos = {t: slug for t, (tipo, slug) in por_titulo.items()
                  if tipo == "operativo"}
    assert operativos == AREA_DE_CADA_FRENTE


def test_el_objetivo_estrategico_no_tiene_area(corework, conn):
    por_titulo = _areas_de_los_objetivos(conn, corework.workspace_id)
    estrategicos = [slug for tipo, slug in por_titulo.values()
                    if tipo == "estrategico"]
    assert estrategicos == [None]


def test_reimportar_completa_el_area_que_falta_y_no_pisa_la_que_hay(
        corework, conn, tmp_path):
    import yaml
    from prisma.importador import importar
    from tests.conftest import RAIZ

    ws = corework.workspace_id
    with admin(conn) as cur:
        cur.execute(
            """update objective set area_id = null
                where titulo = 'Fortalecer servidores y mejorar EPPI'""")
        # Un dato corregido a mano: la reimportación no lo toca.
        cur.execute(
            """update objective
                  set area_id = (select id from area where slug = 'it'
                                  and workspace_id = objective.workspace_id)
                where titulo = 'Robustecer la plataforma e integrar los datos'""")
    conn.commit()

    pack = yaml.safe_load((RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    pack["telegram"]["grupo_gestion_id"] = -1001
    for i, p in enumerate(pack["personas"]):
        p["telegram_user_id"] = 9000 + i
    pack["evidencia"]["estructura_drive"] = "drive://corework"
    ruta = tmp_path / "otra.yaml"
    ruta.write_text(yaml.safe_dump(pack, allow_unicode=True), "utf-8")
    importar(conn, ruta, activar=True)

    por_titulo = _areas_de_los_objetivos(conn, ws)
    assert por_titulo["Fortalecer servidores y mejorar EPPI"][1] == "it"
    assert por_titulo["Robustecer la plataforma e integrar los datos"][1] == "it"


def test_un_objetivo_no_puede_apuntar_al_area_de_otro_espacio(corework, conn):
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        with admin(conn) as cur:
            cur.execute(
                "insert into workspace (slug, nombre) values ('otro', 'Otro') returning id")
            otro = cur.fetchone()["id"]
            cur.execute(
                "insert into area (workspace_id, slug, nombre) values (%s, 'x', 'X') "
                "returning id", (otro,))
            area_ajena = cur.fetchone()["id"]
            cur.execute(
                "update objective set area_id = %s where tipo = 'operativo'",
                (area_ajena,))


def test_el_objetivo_sigue_aislado_por_espacio(corework, conn):
    with conn.cursor() as cur:
        cur.execute(
            """select relrowsecurity, relforcerowsecurity from pg_class
                where oid = to_regclass('prisma.objective')""")
        fila = cur.fetchone()
    assert fila["relrowsecurity"] and fila["relforcerowsecurity"]
    with conn.cursor() as cur:
        cur.execute("set role prisma_app")
        cur.execute("select count(*) n from objective")
        assert cur.fetchone()["n"] == 0
