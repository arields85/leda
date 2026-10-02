"""Con la intención explícita de crear, el título de la tarea nueva no se busca
entre las existentes (F-C1, ADR 0014 etapas 2 y 3).

"necesito crear una tarea: calibrar los sensores de la línea 2" abría una
aclaración de Jev ("¿A cuál te referís con «…»?") con dos tareas existentes: el
título de la tarea que se pide crear se trató además como la referencia a una tarea
que ya existe. Dos dueños para lo mismo. El ruteo ya dice qué es la tarea nueva
(`task.title`): esa frase no es una referencia, y el ruteo no la lista en
`trabajos`; lo que sí lista (una tarea que ya existe y de la que el mensaje
depende) se sigue resolviendo.
"""

from __future__ import annotations

import pytest

import leda.llm as llm
from leda import gateway
from leda import jev as jev_modulo
from leda.db import admin, espacio
from leda.llm import IntentAction, IntentRoute

from tests.test_resolucion_referencias import _quien, _tarea

TITULO = "Calibrar los sensores de la línea 2"


class _Jev:
    """Una credencial de Jev falsa: lo que se busca llega a `referencias`."""


def _con_jev(monkeypatch):
    llegaron: list[tuple[str, ...]] = []
    monkeypatch.setattr(jev_modulo, "desde_base", lambda api_key: _Jev())

    def resolver(cliente, *, texto, referencias, **_):
        llegaron.append(tuple(referencias))
        return {r: (None, jev_modulo.JevError("sin respuesta"))
                for r in referencias}

    monkeypatch.setattr(gateway, "_resolver_en_paralelo", resolver)
    return llegaron


def _resolver(conn, ws, route, texto="necesito crear una tarea"):
    with admin(conn) as cur:
        _tarea(cur, ws)
    conn.commit()
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        return gateway._resolver_referencias_del_turno(
            cur, quien, texto, route, ws)


def _crear(trabajos, titulo=TITULO):
    return IntentRoute(IntentAction.START_TASK_INTAKE, {"title": titulo},
                       trabajos=tuple(trabajos))


@pytest.mark.parametrize("referencia", [
    TITULO, TITULO.lower(), f"  {TITULO}.  ", "calibrar los sensores de la linea 2"])
def test_el_titulo_de_la_tarea_que_se_crea_no_se_busca_entre_las_existentes(
        referencia, corework, conn, monkeypatch):
    ws = corework.workspace_id
    llegaron = _con_jev(monkeypatch)

    resultado = _resolver(conn, ws, _crear([referencia]))

    assert resultado is None and llegaron == []     # ni Jev ni botones


def test_lo_demas_que_menciona_el_mensaje_se_sigue_resolviendo(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    llegaron = _con_jev(monkeypatch)

    _resolver(conn, ws, _crear([TITULO, "el plc de la 3"]))

    assert llegaron == [("el plc de la 3",)]


def test_sin_intencion_de_crear_el_mismo_texto_se_busca_como_siempre(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    llegaron = _con_jev(monkeypatch)
    ruta = IntentRoute(IntentAction.NORMAL_CONVERSATION, {}, trabajos=(TITULO,))

    _resolver(conn, ws, ruta, texto=TITULO)

    assert llegaron == [(TITULO,)]


def test_crear_sin_titulo_propuesto_no_descarta_nada(corework, conn, monkeypatch):
    ws = corework.workspace_id
    llegaron = _con_jev(monkeypatch)
    ruta = IntentRoute(IntentAction.START_TASK_INTAKE, {}, trabajos=("el plc",))

    _resolver(conn, ws, ruta)

    assert llegaron == [("el plc",)]


def test_el_ruteo_no_lista_la_tarea_que_se_crea_como_una_referencia():
    """La regla es del ruteo (etapa 2), general: sin frases ni casos."""
    assert "la tarea nueva y su título no son una referencia" in llm.ROUTER_SYSTEM
