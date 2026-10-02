"""Aviso de incidente a la administración en lenguaje llano y hora local
(T10-2, R3-H1 y R3-H2, formato y texto aprobados por el usuario).

El aviso abre con lo que le pasó a la persona, explica qué pasó y qué hacer
desde una tabla determinista por etapa (nunca el modelo) y deja lo técnico al
final. Estas pruebas no necesitan base: `incidentes.armar_aviso_admin` recibe
todo ya resuelto.
"""

from __future__ import annotations

import ast
import re
from datetime import datetime, timezone
from pathlib import Path

from leda import gateway, incidentes, local, respuesta_unica
from leda.incidentes import (EXPLICACION_POR_ETAPA, NOTICIA_NEUTRA_INCIDENTE,
                               armar_aviso_admin)

ZONA_AR = "America/Argentina/Buenos_Aires"
# 02:30 UTC del 30/09 son las 23:30 del 29/09 en Buenos Aires.
MOMENTO = datetime(2026, 9, 30, 2, 30, tzinfo=timezone.utc)


def _aviso(**cambios) -> str:
    datos = dict(
        incident_id="ab12cd34-0000-0000-0000-000000000000", slug="corework",
        zona_horaria=ZONA_AR, momento=MOMENTO, etapa=gateway.ETAPA_TURNO_TEXTO,
        severidad="alta", resumen="Excepción no manejada en 'turno_texto' (RuntimeError).",
        nombre="Nahuel Gimenez", mensaje="arranco con esto")
    datos.update(cambios)
    return armar_aviso_admin(**datos)


def _etapas_conocidas() -> set[str]:
    """Cada etapa con la que el código registra un incidente: las constantes
    `ETAPA_*` de los módulos y los literales `etapa="..."` de `src/`."""
    etapas = {valor for modulo in (gateway, respuesta_unica, local, incidentes)
              for nombre, valor in vars(modulo).items()
              if nombre.startswith("ETAPA_") and isinstance(valor, str)}
    for archivo in Path(incidentes.__file__).parent.glob("*.py"):
        etapas.update(re.findall(r'etapa="([a-z_]+)"', archivo.read_text(encoding="utf-8")))
    return etapas


def test_el_aviso_neutro_a_la_persona_es_el_texto_aprobado():
    assert NOTICIA_NEUTRA_INCIDENTE == (
        "Tuve un problema y no pude responder tu mensaje. Ya quedó registrado "
        "para que lo revise un administrador.")
    assert gateway.NOTICIA_NEUTRA_INCIDENTE == NOTICIA_NEUTRA_INCIDENTE


def test_cada_etapa_conocida_tiene_su_explicacion():
    etapas = _etapas_conocidas()
    assert {"turno_texto", "toque_boton", "sin_respuesta", "mensaje_admin",
            "saludo_diario", "ciclo_de_fondo"} <= etapas
    assert etapas - set(EXPLICACION_POR_ETAPA) == set()
    for etapa, explicacion in EXPLICACION_POR_ETAPA.items():
        assert explicacion.que_paso.strip() and explicacion.que_hacer.strip(), etapa
        assert explicacion.que_vio.strip(), etapa


def _llamadas_sin_etapa_valida(fuente: str, nombre: str = "x.py") -> list[str]:
    """Llamadas a `registrar_incidente` cuya etapa no está nombrada de forma
    verificable: sin `etapa=`, con `etapa=None`, o con los argumentos pasados
    sólo por `**kwargs` (no se puede saber si traen la etapa)."""
    malas = []
    for nodo in ast.walk(ast.parse(fuente)):
        if not (isinstance(nodo, ast.Call)
                and getattr(nodo.func, "id", getattr(nodo.func, "attr", None))
                == "registrar_incidente"):
            continue
        etapa = next((k.value for k in nodo.keywords if k.arg == "etapa"), None)
        es_none = isinstance(etapa, ast.Constant) and etapa.value is None
        if etapa is None or es_none:
            malas.append(f"{nombre}:{nodo.lineno}")
    return malas


def test_ningun_incidente_se_registra_sin_etapa():
    """Cada `registrar_incidente(...)` de `src/` nombra su etapa (T10-2b): un
    incidente sin etapa cae en la explicación genérica del aviso a la
    administración, que no dice qué vio la persona."""
    sin_etapa = []
    for archivo in sorted(Path(incidentes.__file__).parent.glob("*.py")):
        sin_etapa += _llamadas_sin_etapa_valida(
            archivo.read_text(encoding="utf-8"), archivo.name)
    assert sin_etapa == []


def test_la_prueba_de_etapas_rechaza_las_formas_que_no_nombran_una():
    """T10-2c: la prueba de arriba no se deja engañar por `etapa=None` ni por
    llamadas con los argumentos pasados sólo por `**kwargs`."""
    assert _llamadas_sin_etapa_valida(
        "registrar_incidente(cur, ws, 'r')") == ["x.py:1"]
    assert _llamadas_sin_etapa_valida(
        "registrar_incidente(cur, ws, 'r', etapa=None)") == ["x.py:1"]
    assert _llamadas_sin_etapa_valida(
        "incidentes.registrar_incidente(cur, ws, 'r', **datos)") == ["x.py:1"]
    assert _llamadas_sin_etapa_valida(
        "registrar_incidente(cur, ws, 'r', etapa='turno_texto', **extra)") == []
    assert _llamadas_sin_etapa_valida(
        "registrar_incidente(cur, ws, 'r', etapa=ETAPA_TURNO_TEXTO)") == []


def test_el_aviso_sigue_el_formato_aprobado_en_orden():
    texto = _aviso()
    lineas = texto.split("\n")
    assert lineas[0] == "⚠️ Leda no pudo responderle a Nahuel Gimenez"
    encabezados = ["Qué pasó", "Qué vio Nahuel Gimenez", "Qué hacer", "Mensaje",
                   "Detalle técnico"]
    posiciones = [lineas.index(h) for h in encabezados]
    assert posiciones == sorted(posiciones)


def test_que_pasó_y_que_hacer_salen_de_la_tabla_de_la_etapa():
    texto = _aviso(etapa=gateway.ETAPA_TURNO_TEXTO)
    explicacion = EXPLICACION_POR_ETAPA[gateway.ETAPA_TURNO_TEXTO]
    assert explicacion.que_paso in texto
    assert explicacion.que_hacer.format(nombre="Nahuel Gimenez") in texto


def test_que_vio_la_persona_es_el_aviso_neutro_cuando_la_etapa_lo_manda():
    texto = _aviso(etapa=gateway.ETAPA_TURNO_TEXTO)
    assert f"Qué vio Nahuel Gimenez\n{NOTICIA_NEUTRA_INCIDENTE}" in texto


def test_el_mensaje_es_el_disparador_tal_cual():
    texto = _aviso(mensaje="arranco con esto")
    assert "Mensaje\narranco con esto" in texto


def test_el_detalle_tecnico_conserva_id_espacio_etapa_y_resumen():
    texto = _aviso()
    detalle = texto.split("Detalle técnico\n", 1)[1]
    assert "ab12cd34" in detalle
    assert "corework" in detalle
    assert "turno_texto" in detalle
    assert "alta" in detalle
    assert "Excepción no manejada en 'turno_texto' (RuntimeError)." in detalle


def test_la_hora_sale_en_la_zona_del_espacio_no_en_utc():
    texto = _aviso()
    assert "29/09 23:30" in texto
    assert "02:30" not in texto
    assert "UTC" not in texto


def test_sin_espacio_la_hora_se_dice_utc_sin_inventar_una_zona():
    texto = _aviso(slug=None, zona_horaria=None)
    assert "30/09 02:30 UTC" in texto
    assert "espacio global" in texto


def test_una_etapa_desconocida_o_ausente_usa_el_texto_generico():
    for etapa in ("etapa_que_no_existe", None):
        texto = _aviso(etapa=etapa)
        assert "Qué pasó" in texto and "Qué hacer" in texto
        assert "python -m leda incidentes" in texto
        # Nunca se afirma qué vio la persona cuando no se sabe.
        assert NOTICIA_NEUTRA_INCIDENTE not in texto


def test_sin_persona_identificada_no_se_inventa_un_nombre():
    texto = _aviso(nombre=None)
    assert texto.split("\n")[0] == "⚠️ Leda tuvo un problema"
    assert "Qué vio la persona" in texto
