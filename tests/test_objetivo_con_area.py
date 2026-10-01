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


# ------------------------------- un área del pack que no existe no pasa en silencio

def _pack(**cambios):
    import copy

    import yaml
    from tests.conftest import RAIZ

    pack = yaml.safe_load((RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    pack = copy.deepcopy(pack)
    # Los mismos datos que el fixture `corework`: sin ellos se crearían personas
    # nuevas con los mismos nombres.
    pack["telegram"]["grupo_gestion_id"] = -1001
    for i, p in enumerate(pack["personas"]):
        p["telegram_user_id"] = 9000 + i
    pack["evidencia"]["estructura_drive"] = "drive://corework"
    pack.update(cambios)
    return pack


def _escribir(tmp_path, pack):
    import yaml

    ruta = tmp_path / "pack.yaml"
    ruta.write_text(yaml.safe_dump(pack, allow_unicode=True), "utf-8")
    return ruta


def _con_area(area, indice=2):
    pack = _pack()
    frente = pack["objetivo_inicial"]["frentes"][indice]
    if area is None:
        frente.pop("area")
    else:
        frente["area"] = area
    return pack, frente["titulo"]


@pytest.mark.parametrize("area", ["itt", "IT", "tecnologia", "", None])
def test_validar_bloquea_un_frente_con_un_area_que_no_existe_o_sin_area(area):
    from prisma.importador import validar

    pack, titulo = _con_area(area)
    bloqueantes, _ = validar(pack)
    assert any(titulo in b and "área" in b for b in bloqueantes), bloqueantes


def test_validar_no_bloquea_los_frentes_del_pack_vigente():
    from prisma.importador import validar

    bloqueantes, _ = validar(_pack())
    assert not any("frente" in b.lower() for b in bloqueantes)


@pytest.mark.parametrize("area", ["itt", None])
def test_importar_un_espacio_nuevo_con_un_area_mala_falla_y_no_deja_nada(
        conn, tmp_path, area):
    from prisma.importador import PackInvalido, importar

    pack, titulo = _con_area(area)
    pack["espacio"]["slug"] = "nuevo-por-area"
    with pytest.raises(PackInvalido) as error:
        importar(conn, _escribir(tmp_path, pack))
    assert titulo in str(error.value)
    with admin(conn) as cur:
        cur.execute("select count(*) n from objective o join workspace w "
                    "on w.id = o.workspace_id where w.slug = 'nuevo-por-area'")
        assert cur.fetchone()["n"] == 0


def test_reimportar_con_un_area_mala_falla_y_no_toca_nada(corework, conn, tmp_path):
    from prisma.importador import PackInvalido, importar

    ws = corework.workspace_id
    with admin(conn) as cur:
        cur.execute("update objective set area_id = null where titulo = %s",
                    ("Fortalecer servidores y mejorar EPPI",))
    conn.commit()
    pack, _ = _con_area("itt")
    with pytest.raises(PackInvalido):
        importar(conn, _escribir(tmp_path, pack))
    assert _areas_de_los_objetivos(conn, ws)[
        "Fortalecer servidores y mejorar EPPI"][1] is None


def test_completar_las_areas_informa_cuantas_actualizo(corework, conn, tmp_path):
    from prisma.importador import importar

    with admin(conn) as cur:
        cur.execute("update objective set area_id = null where tipo = 'operativo' "
                    "and titulo in (%s, %s)",
                    ("Fortalecer servidores y mejorar EPPI",
                     "Planos eléctricos correctos y documentación útil"))
    conn.commit()
    resultado = importar(conn, _escribir(tmp_path, _pack()))
    assert any("2 objetivo" in a and "área" in a for a in resultado.advertencias), \
        resultado.advertencias
    assert _areas_de_los_objetivos(conn, corework.workspace_id)[
        "Fortalecer servidores y mejorar EPPI"][1] == "it"


def test_completar_las_areas_avisa_del_frente_que_no_encuentra(
        corework, conn, tmp_path):
    from prisma.importador import importar

    pack = _pack()
    pack["objetivo_inicial"]["frentes"][2]["titulo"] = "Un frente que se renombró"
    resultado = importar(conn, _escribir(tmp_path, pack))
    avisos = [a for a in resultado.advertencias if "Un frente que se renombró" in a]
    assert len(avisos) == 1 and "área" in avisos[0]


def test_reimportar_sin_nada_que_completar_no_agrega_avisos_de_area(
        corework, conn, tmp_path):
    from prisma.importador import importar

    resultado = importar(conn, _escribir(tmp_path, _pack()))
    assert not [a for a in resultado.advertencias if "frente" in a.lower()]


def test_el_esquema_documenta_la_columna_como_la_migracion():
    from tests.conftest import RAIZ

    esquema = (RAIZ / "db" / "esquema.sql").read_text("utf-8")
    migracion = (RAIZ / "db" / "migrations" / "0027_objetivo_con_area.sql"
                 ).read_text("utf-8")
    comentario = next(l for l in migracion.splitlines()
                      if l.strip().startswith("'F-B11: el área a la que"))
    assert "comment on column objective.area_id is" in esquema
    assert comentario.strip() in esquema
