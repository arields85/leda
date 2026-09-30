"""Interruptor de redacción, resultado del turno y variante B (ADR 0014, F1).

El interruptor es un dato del espacio (`workspace_setting['redaccion']`),
sembrado desde el pack; `resultado_turno` guarda los hechos de un turno y
`redaccion.redactar` los convierte en texto. Ninguna de estas piezas conoce
el transporte.
"""

from __future__ import annotations

import dataclasses

import pytest
import yaml

from prisma import redaccion
from prisma.db import admin, espacio
from prisma.resultado_turno import (
    Cambio, Falta, OpcionDisponible, ResultadoTurno, SinCambio, Estado,
    ValorAceptado,
)
from prisma.valores import TipoValor
from tests.conftest import RAIZ


@pytest.fixture(autouse=True)
def _sin_anomalias_reportadas():
    redaccion._anomalias_reportadas.clear()
    yield
    redaccion._anomalias_reportadas.clear()


# ---------------------------------------------------------------------------
# El interruptor como dato del espacio
# ---------------------------------------------------------------------------

def _poner(conn, ws, valor_json: str | None) -> None:
    with admin(conn) as cur:
        cur.execute(
            "delete from workspace_setting "
            "where workspace_id = %s and clave = 'redaccion'", (ws,))
        if valor_json is not None:
            cur.execute(
                "insert into workspace_setting (workspace_id, clave, valor) "
                "values (%s, 'redaccion', %s::jsonb)", (ws, valor_json))


def _incidentes(conn, ws) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(
            "select severidad, resumen_sanitizado, etapa from incident "
            "where workspace_id = %s order by at", (ws,))
        return cur.fetchall()


def test_el_pack_de_corework_siembra_la_variante_b(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        cur.execute(
            "select valor from workspace_setting "
            "where workspace_id = %s and clave = 'redaccion'", (ws,))
        assert cur.fetchone()["valor"] == {"variante": "B"}


@pytest.mark.parametrize("variante", ["A", "B"])
def test_el_importador_siembra_la_variante_que_declara_el_pack(
        conn, tmp_path, variante):
    from prisma.importador import importar

    pack = yaml.safe_load(
        (RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    pack["conversacion"] = {"redaccion": variante}
    ruta = tmp_path / "p.yaml"
    ruta.write_text(yaml.safe_dump(pack, allow_unicode=True), "utf-8")
    r = importar(conn, ruta)

    with admin(conn) as cur:
        assert redaccion.variante_redaccion(cur, r.workspace_id) == variante


def test_un_pack_sin_seccion_de_conversacion_no_siembra_nada(conn, tmp_path):
    from prisma.importador import importar

    pack = yaml.safe_load(
        (RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    pack.pop("conversacion", None)
    ruta = tmp_path / "p.yaml"
    ruta.write_text(yaml.safe_dump(pack, allow_unicode=True), "utf-8")
    r = importar(conn, ruta)

    with admin(conn) as cur:
        cur.execute(
            "select 1 from workspace_setting "
            "where workspace_id = %s and clave = 'redaccion'",
            (r.workspace_id,))
        assert cur.fetchone() is None


def test_un_pack_con_una_variante_desconocida_advierte(conn, tmp_path):
    from prisma.importador import importar

    pack = yaml.safe_load(
        (RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    pack["conversacion"] = {"redaccion": "Z"}
    ruta = tmp_path / "p.yaml"
    ruta.write_text(yaml.safe_dump(pack, allow_unicode=True), "utf-8")
    r = importar(conn, ruta)

    assert any("redaccion" in a for a in r.advertencias)


@pytest.mark.parametrize("variante", ["A", "B"])
def test_lee_la_variante_guardada(corework, conn, variante):
    ws = corework.workspace_id
    _poner(conn, ws, f'{{"variante": "{variante}"}}')
    with admin(conn) as cur:
        assert redaccion.variante_redaccion(cur, ws) == variante
    assert _incidentes(conn, ws) == []


def test_sin_la_clave_es_b_y_no_es_un_incidente(corework, conn):
    ws = corework.workspace_id
    _poner(conn, ws, None)
    with admin(conn) as cur:
        assert redaccion.variante_redaccion(cur, ws) == "B"
    assert _incidentes(conn, ws) == []


VALORES_DESCONOCIDOS = [
    {"variante": "Z"},      # variante que no existe
    {"variante": "a"},      # no se adivina la mayúscula
    {"variante": None},
    {"variante": 1},
    {},
    "A",                    # forma equivocada: no es un objeto
    ["A"],
    None,
]


@pytest.mark.parametrize("valor", VALORES_DESCONOCIDOS)
def test_un_valor_desconocido_se_interpreta_como_b_y_anomalo(valor):
    assert redaccion.interpretar_variante(valor) == ("B", True)


@pytest.mark.parametrize("variante", ["A", "B"])
def test_un_valor_valido_se_interpreta_tal_cual(variante):
    assert redaccion.interpretar_variante({"variante": variante}) == (
        variante, False)


@pytest.mark.parametrize("valor_json", [
    '{"variante": "Z"}', '{"variante": null}', '{}', '"A"', '["A"]', 'null',
])
def test_un_valor_desconocido_es_b_y_queda_registrado(corework, conn, valor_json):
    ws = corework.workspace_id
    _poner(conn, ws, valor_json)
    with admin(conn) as cur:
        assert redaccion.variante_redaccion(cur, ws) == "B"

    incidentes = _incidentes(conn, ws)
    assert len(incidentes) == 1
    assert incidentes[0]["etapa"] == redaccion.ETAPA_INTERRUPTOR_REDACCION
    assert "variante B" in incidentes[0]["resumen_sanitizado"]


def test_la_anomalia_se_registra_una_vez_por_espacio_y_valor(corework, conn):
    ws = corework.workspace_id
    _poner(conn, ws, '{"variante": "Z"}')
    for _ in range(3):
        with admin(conn) as cur:
            assert redaccion.variante_redaccion(cur, ws) == "B"
    assert len(_incidentes(conn, ws)) == 1

    # Otro valor desconocido es otro hecho: se registra de nuevo.
    _poner(conn, ws, '{"variante": "Y"}')
    with admin(conn) as cur:
        redaccion.variante_redaccion(cur, ws)
    assert len(_incidentes(conn, ws)) == 2


def test_se_lee_y_se_registra_con_el_rol_de_la_aplicacion(corework, conn):
    ws = corework.workspace_id
    _poner(conn, ws, '{"variante": "Z"}')
    with espacio(conn, ws) as cur:
        assert redaccion.variante_redaccion(cur, ws) == "B"
    assert len(_incidentes(conn, ws)) == 1


def test_el_interruptor_no_cruza_espacios(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        cur.execute(
            "insert into workspace (slug, nombre, zona_horaria, activo) "
            "values ('otro', 'Otro', 'America/Argentina/Buenos_Aires', true) "
            "returning id")
        otro = str(cur.fetchone()["id"])
    _poner(conn, ws, '{"variante": "A"}')
    with admin(conn) as cur:
        assert redaccion.variante_redaccion(cur, ws) == "A"
        assert redaccion.variante_redaccion(cur, otro) == "B"


class _CursorQueAnota:
    """Un cursor que sólo anota lo que se le manda (sin base)."""

    def __init__(self):
        self.ejecutados: list[tuple[str, tuple]] = []

    def execute(self, sql, params=()):
        self.ejecutados.append((sql, tuple(params)))


def _ajustes_sembrados(pack: dict) -> dict:
    import json
    from prisma.importador import _importar_ajustes

    cur = _CursorQueAnota()
    _importar_ajustes(cur, "ws-1", pack)
    return {params[1]: json.loads(params[2]) for _, params in cur.ejecutados}


def test_el_importador_siembra_redaccion_desde_la_seccion_conversacion():
    assert _ajustes_sembrados({"conversacion": {"redaccion": "A"}}) == {
        "redaccion": {"variante": "A"}}


def test_el_importador_no_siembra_redaccion_sin_la_seccion():
    assert "redaccion" not in _ajustes_sembrados({"urgencia": {"x": 1}})
    assert "redaccion" not in _ajustes_sembrados({"conversacion": {}})


def test_el_pack_de_corework_declara_la_variante_b():
    pack = yaml.safe_load(
        (RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    assert _ajustes_sembrados(pack)["redaccion"] == {"variante": "B"}


def test_el_pack_no_rechaza_la_seccion_conversacion():
    from prisma.importador import validar

    pack = yaml.safe_load(
        (RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    bloqueantes, advertencias = validar(pack)
    assert not any("conversacion" in b for b in bloqueantes)


def test_validar_advierte_de_una_variante_desconocida():
    from prisma.importador import validar

    pack = yaml.safe_load(
        (RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    pack["conversacion"] = {"redaccion": "Z"}
    _, advertencias = validar(pack)
    assert any("redaccion" in a and "Z" in a for a in advertencias)


# ---------------------------------------------------------------------------
# El resultado del turno
# ---------------------------------------------------------------------------

def test_el_resultado_del_turno_es_inmutable_y_sin_transporte():
    r = ResultadoTurno(cambios=(Cambio("la tarea «Revisar PLC»", "quedó creada"),))
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.cambios = ()
    campos = {f.name for f in dataclasses.fields(ResultadoTurno)}
    assert campos == {"cambios", "sin_cambios", "estado", "falta", "opciones",
                      "valores_aceptados"}
    # Frontera regla 2: ni chat ni formato de Telegram en el resultado.
    assert not {"chat_id", "teclado", "html", "parse_mode"} & campos


def test_un_resultado_vacio_se_reconoce():
    assert ResultadoTurno().vacio
    assert not ResultadoTurno(falta=Falta("la fecha", TipoValor.FECHA)).vacio


# ---------------------------------------------------------------------------
# La variante B (plantillas)
# ---------------------------------------------------------------------------

JERGA = ("(hasta", "request_id", "campo", "pending", "None", "null",
         "Sin descripción", "Al confirmar", "_", "{", "}")


def _sin_jerga(texto: str) -> None:
    for marca in JERGA:
        assert marca not in texto, (marca, texto)


def test_b_dice_que_cambio():
    texto = redaccion.redactar(ResultadoTurno(cambios=(
        Cambio("la tarea «Revisar PLC»", "quedó en curso"),)), "B")
    assert texto == "Listo: la tarea «Revisar PLC» quedó en curso."


def test_b_con_varios_cambios_los_lista():
    texto = redaccion.redactar(ResultadoTurno(cambios=(
        Cambio("la tarea «A»", "quedó en curso"),
        Cambio("la tarea «B»", "quedó cancelada"))), "B")
    assert texto == ("Listo:\n- la tarea «A» quedó en curso\n"
                     "- la tarea «B» quedó cancelada")


def test_b_dice_que_no_cambio_y_por_que():
    texto = redaccion.redactar(ResultadoTurno(sin_cambios=(
        SinCambio("la tarea «Revisar PLC»", "ya estaba en curso"),)), "B")
    assert texto == "No cambié la tarea «Revisar PLC»: ya estaba en curso."


def test_b_muestra_el_valor_aceptado_para_confirmar():
    texto = redaccion.redactar(ResultadoTurno(valores_aceptados=(
        ValorAceptado("la fecha objetivo", "04/10/2026"),)), "B")
    assert texto == "Anoté la fecha objetivo: 04/10/2026."


def test_b_muestra_el_estado_leido_de_la_base():
    texto = redaccion.redactar(ResultadoTurno(estado=(
        Estado("«Revisar PLC»", "en curso"),)), "B")
    assert texto == "«Revisar PLC» está en curso."


def test_b_pregunta_lo_que_falta():
    texto = redaccion.redactar(ResultadoTurno(
        falta=Falta("la fecha objetivo", TipoValor.FECHA)), "B")
    assert texto == "Me falta la fecha objetivo."


def test_b_usa_la_pregunta_de_lo_que_falta_si_la_hay():
    texto = redaccion.redactar(ResultadoTurno(falta=Falta(
        "la fecha objetivo", TipoValor.FECHA,
        pregunta="¿Para cuándo la querés?")), "B")
    assert texto == "¿Para cuándo la querés?"


def test_b_junta_los_hechos_en_orden_y_la_pregunta_va_al_final():
    texto = redaccion.redactar(ResultadoTurno(
        cambios=(Cambio("la tarea «A»", "quedó creada"),),
        sin_cambios=(SinCambio("el área", "no hacía falta"),),
        valores_aceptados=(ValorAceptado("la fecha objetivo", "04/10/2026"),),
        estado=(Estado("«A»", "borrador"),),
        falta=Falta("el objetivo", TipoValor.TEXTO),
        opciones=(OpcionDisponible("Cancelar", "cancelar"),)), "B")
    partes = texto.split("\n\n")
    assert partes == [
        "Listo: la tarea «A» quedó creada.",
        "No cambié el área: no hacía falta.",
        "Anoté la fecha objetivo: 04/10/2026.",
        "«A» está borrador.",
        "Me falta el objetivo."]
    _sin_jerga(texto)


def test_las_opciones_no_son_texto_las_dibuja_el_transporte():
    texto = redaccion.redactar(ResultadoTurno(
        cambios=(Cambio("la tarea «A»", "quedó creada"),),
        opciones=(OpcionDisponible("Ver evidencia", "ver_evidencia"),)), "B")
    assert "Ver evidencia" not in texto


def test_b_nunca_deja_jerga_ni_claves_internas():
    texto = redaccion.redactar(ResultadoTurno(
        cambios=(Cambio("la tarea «A»", "quedó creada"),),
        falta=Falta("la descripción", TipoValor.TEXTO)), "B")
    _sin_jerga(texto)


def test_un_resultado_vacio_no_se_redacta_en_silencio():
    with pytest.raises(ValueError):
        redaccion.redactar(ResultadoTurno(), "B")


def test_una_variante_que_no_existe_no_se_redacta_en_silencio():
    with pytest.raises(ValueError):
        redaccion.redactar(ResultadoTurno(
            cambios=(Cambio("x", "y"),)), "C")


def test_a_todavia_cae_en_b():
    r = ResultadoTurno(cambios=(Cambio("la tarea «A»", "quedó creada"),))
    assert redaccion.redactar(r, "A") == redaccion.redactar(r, "B")
