from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

from leda import gateway, onboarding
from leda.agente import responder
from leda.autoridad import Canal, identificar
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.llm import ProveedorGuionado, Respuesta
from leda.salida import (BUTTON_LABEL_LIMIT,
                             ETIQUETA_CANCELAR, ETIQUETA_CONFIRMAR,
                             ICONO_CANCELAR, ICONO_CONFIRMAR,
                             ICONO_OTRA_OPCION, ICONO_SALIR_OPCIONES,
                             ICONO_TAREA, ICONO_VER_MAS,
                             OBJETIVO_ETIQUETA_BOTON,
                             TELEGRAM_TEXT_LIMIT, TRUNCAR_ETIQUETA_BOTON,
                             acortar_etiqueta_boton, con_icono, costo_icono,
                             etiqueta_sin_icono, etiquetas_de_tarea,
                             etiquetas_boton_distinguibles,
                             etiquetas_coinciden,
                             prepare_buttons,
                             telegram_utf16_units, truncar_etiqueta_boton)


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 8, 14, 15, 0, tzinfo=timezone.utc)


def test_agent_arbitrary_long_model_output_is_split_before_enqueue(corework, conn):
    ws = corework.workspace_id
    long_answer = "👩\u200d🔧 status " * 900
    with espacio(conn, ws) as cur:
        cur.execute("select telegram_user_id from integrante where nombre = %s",
                    ("Marcos Tarquini",))
        who = identificar(cur, cur.fetchone()["telegram_user_id"],
                          Canal.ESPACIO, ws)
        result = responder(
            cur, who, "status", ProveedorGuionado([Respuesta(texto=long_answer)]),
            Calendario.desde_base(cur, ws), chat_id=9002, ahora=NOW,
        )
        cur.execute("select cuerpo, dedupe_key from message_outbox order by dedupe_key")
        rows = cur.fetchall()
        assert result.texto == long_answer.strip()
        assert len(rows) > 1
        assert len({row["dedupe_key"] for row in rows}) == len(rows)
        assert all(telegram_utf16_units(row["cuerpo"]) <= TELEGRAM_TEXT_LIMIT
                   for row in rows)


def test_gateway_and_onboarding_split_long_informational_copy(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    long_copy = "Welcome 👋 " * 900
    with admin(conn) as cur:
        cur.execute(
            """select u.telegram_user_id
                 from membership m join app_user u on u.id = m.app_user_id
                where m.workspace_id = %s and u.telegram_user_id is not null
                order by u.nombre limit 1""", (ws,))
        telegram_id = cur.fetchone()["telegram_user_id"]
    monkeypatch.setattr(onboarding, "bienvenida", lambda *args: long_copy)
    gateway._activacion(conn, ws, "/start", telegram_id, telegram_id)
    with admin(conn) as cur:
        cur.execute("select cuerpo from message_outbox order by dedupe_key")
        rows = cur.fetchall()
        assert len(rows) > 1
        assert all(telegram_utf16_units(row["cuerpo"]) <= TELEGRAM_TEXT_LIMIT
                   for row in rows)


# ---------------------------------------------------------------------------
# Etiquetas de botón cortas (hallazgo 2, sesión 2 por Telegram): las
# etiquetas que arma el servidor a partir de un título de tarea se cortan en
# un límite de PALABRA, no a mitad de una, y a un objetivo bastante más chico
# que el tope técnico de Telegram (`TRUNCAR_ETIQUETA_BOTON`, 48) para que
# entren cómodas en un botón inline de ancho completo en un teléfono chico
# (`OBJETIVO_ETIQUETA_BOTON`, ver su comentario en `salida.py`).
# ---------------------------------------------------------------------------


def test_acortar_etiqueta_boton_no_corta_si_ya_entra_en_el_objetivo():
    corto = "Cablear tablero máq. 3"
    assert len(corto) <= OBJETIVO_ETIQUETA_BOTON
    assert acortar_etiqueta_boton(corto) == corto        # sin "…": no se tocó


def test_acortar_etiqueta_boton_corta_en_limite_de_palabra_con_elipsis():
    largo = "Revisar comunicaciones industriales de la compresora principal"
    assert len(largo) > OBJETIVO_ETIQUETA_BOTON

    corta = acortar_etiqueta_boton(largo)

    assert corta.endswith("…")
    sin_elipsis = corta[:-1]
    assert len(sin_elipsis) <= OBJETIVO_ETIQUETA_BOTON
    assert largo.startswith(sin_elipsis.rstrip())
    # Nunca corta a mitad de palabra: lo que quedó antes de "…" es un prefijo
    # de palabras completas del título original.
    assert sin_elipsis.rstrip() in [
        " ".join(largo.split(" ")[:n]) for n in range(len(largo.split(" ")) + 1)]


def test_acortar_etiqueta_boton_primera_palabra_larga_cae_al_corte_duro():
    # Una sola "palabra" (sin espacios) más larga que el objetivo no tiene
    # límite de palabra donde cortar: cae al corte duro de siempre
    # (`TRUNCAR_ETIQUETA_BOTON`, 48), nunca deja una etiqueta vacía.
    una_palabra = "Supercalifragilisticoexpialidocosisimo" * 2
    assert len(una_palabra) > TRUNCAR_ETIQUETA_BOTON

    corta = acortar_etiqueta_boton(una_palabra)

    assert corta.endswith("…")
    assert len(corta) == TRUNCAR_ETIQUETA_BOTON


def test_acortar_etiqueta_boton_es_seguro_para_prepare_buttons_con_acentos():
    largo = "Revisar el tablero eléctrico de la máquina número tres del área"
    corta = acortar_etiqueta_boton(largo)
    etiqueta, _ = prepare_buttons([(corta, "p:x")])[0]
    assert etiqueta == corta
    assert telegram_utf16_units(corta) <= 80


# ---------------------------------------------------------------------------
# Un conjunto de etiquetas nunca queda ambiguo: si dos títulos distintos
# cortan igual, se extienden palabra por palabra hasta distinguirse.
# ---------------------------------------------------------------------------


def test_etiquetas_boton_distinguibles_extiende_las_que_colisionan():
    titulos = ["Revisar tablero de la línea de producción 3",
               "Revisar tablero de la línea de producción 4"]
    cortas_sin_distinguir = [acortar_etiqueta_boton(t) for t in titulos]
    assert cortas_sin_distinguir[0] == cortas_sin_distinguir[1]     # colisionan

    distinguidas = etiquetas_boton_distinguibles(titulos)

    assert len(set(distinguidas)) == 2
    assert distinguidas[0] != distinguidas[1]
    assert "3" in distinguidas[0] and "4" in distinguidas[1]


def test_un_titulo_ordinario_entra_entero_en_su_boton():
    """R4-H4 (decisión del usuario, 2026-09-30): los botones de lista cortaban
    "Dashboard de lotes…" aunque el título entero entraba de sobra. Con el
    objetivo de 40 caracteres un título ordinario sale entero, con su ícono."""
    titulo = "Dashboard de lotes de producción"

    assert len(titulo) < OBJETIVO_ETIQUETA_BOTON - costo_icono(ICONO_TAREA)
    assert etiquetas_de_tarea([titulo]) == [f"📋 {titulo}"]


def test_los_titulos_ordinarios_siguen_siendo_distinguibles_entre_si():
    titulos = ["Dashboard de lotes de producción", "Dashboard de lotes de calidad"]

    etiquetas = etiquetas_de_tarea(titulos)

    assert etiquetas == [f"📋 {t}" for t in titulos]
    assert len(set(etiquetas)) == 2


def test_etiquetas_boton_distinguibles_no_toca_las_que_no_colisionan():
    titulos = ["Programar PLC", "Cablear tablero máq. 3"]
    assert etiquetas_boton_distinguibles(titulos) == titulos


def test_etiquetas_boton_distinguibles_respeta_etiquetas_fijas_como_obstaculo():
    # Una etiqueta "fija" (por ejemplo, la que ya eligió el modelo en
    # `ofrecer_opciones`) nunca se hace crecer -- sólo cuenta como obstáculo
    # para que las demás no la pisen.
    titulos = ["Programar PLC", "Programar PLC de la comprimidora principal"]
    distinguidas = etiquetas_boton_distinguibles(
        titulos, fijas=[True, False])
    assert distinguidas[0] == "Programar PLC"
    assert distinguidas[1] != "Programar PLC"
    assert len(set(distinguidas)) == 2


# ---------------------------------------------------------------------------
# Hallazgo 7 (sesión 2 por Telegram, 2026-09-27, confirmado por el usuario):
# el corte de palabra no puede dejar una palabra de función (preposición,
# artículo, conjunción) justo antes de la elipsis -- "Backup de servidores
# de…", "Configurar access points de…", "Cambiar switch industrial de…".
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("largo, esperado", [
    ("Backup de servidores de la sucursal norte", "Backup de servidores…"),
    ("Configurar access points de la planta baja", "Configurar access points…"),
    ("Cambiar switch industrial de la línea dos", "Cambiar switch industrial…"),
])
def test_acortar_etiqueta_boton_no_termina_en_palabra_de_funcion(largo, esperado):
    # La regla de la palabra de función no depende del objetivo por omisión (que
    # subió de 30 a 40, R4-H4): se prueba con el objetivo de los títulos de acá.
    objetivo = 30
    assert len(largo) > objetivo

    corta = acortar_etiqueta_boton(largo, objetivo=objetivo)

    assert corta == esperado
    ultima_palabra = corta[:-1].rstrip().rsplit(" ", 1)[-1].casefold()
    assert ultima_palabra not in {
        "de", "del", "la", "el", "los", "las", "en", "al", "a", "y", "e",
        "o", "u", "para", "con", "por", "sin", "sobre", "un", "una"}


def test_acortar_etiqueta_boton_nunca_deja_vacio_si_todo_es_funcion():
    # Caso degenerado (no realista para un título): si sólo queda una
    # palabra tras el corte de palabra, se conserva aunque sea de función --
    # nunca una etiqueta vacía.
    largo = "de " * 20 + "cosa"
    corta = acortar_etiqueta_boton(largo, objetivo=4)
    assert corta.strip("…") != ""


# ---------------------------------------------------------------------------
# Seguimiento (a) a la revisión de la sesión de etiquetas (review-af418dd9):
# el corte duro de `acortar_etiqueta_boton` (cuando ni una palabra entra en
# el objetivo) ignoraba `limite` y usaba siempre 48.
# ---------------------------------------------------------------------------


def test_acortar_etiqueta_boton_corte_duro_honra_un_limite_no_default():
    una_palabra = "Supercalifragilisticoexpialidocosisimo" * 2
    limite_custom = 20
    assert len(una_palabra) > limite_custom

    corta = acortar_etiqueta_boton(una_palabra, limite=limite_custom)

    assert corta.endswith("…")
    assert len(corta) == limite_custom


def test_truncar_etiqueta_boton_honra_un_limite_no_default():
    largo = "x" * 60
    assert truncar_etiqueta_boton(largo, limite=10) == "x" * 9 + "…"
    assert truncar_etiqueta_boton(largo) == "x" * 47 + "…"       # default: 48


# ---------------------------------------------------------------------------
# Seguimiento (c): `fijas` más corta que `titulos` no descarta etiquetas en
# silencio.
# ---------------------------------------------------------------------------


def test_etiquetas_boton_distinguibles_fijas_de_otro_largo_levanta_error():
    with pytest.raises(ValueError):
        etiquetas_boton_distinguibles(["A", "B", "C"], fijas=[True])


# ---------------------------------------------------------------------------
# Seguimiento (b): la numeración de último recurso -- antes sin ninguna
# prueba -- no colisiona con una etiqueta ya presente y nunca toca una fija.
# ---------------------------------------------------------------------------


def test_etiquetas_boton_distinguibles_numera_titulos_identicos():
    # Dos títulos literalmente idénticos: crecer palabra por palabra no
    # alcanza para distinguirlos (ya están completos) -- último recurso, la
    # numeración.
    titulos = ["Backup de servidores", "Backup de servidores"]

    distinguidas = etiquetas_boton_distinguibles(titulos)

    assert distinguidas == ["Backup de servidores", "Backup de servidores (2)"]


def test_etiquetas_boton_distinguibles_numera_saltando_una_colision_existente():
    # La segunda "Backup" repetida numeraría "(2)" por default -- pero ese
    # texto ya lo usa la tercera opción tal cual, así que salta a "(3)".
    titulos = ["Backup", "Backup", "Backup (2)"]

    distinguidas = etiquetas_boton_distinguibles(titulos)

    assert distinguidas[0] == "Backup"
    assert distinguidas[2] == "Backup (2)"          # la literal, sin tocar
    assert distinguidas[1] == "Backup (3)"          # saltea el 2, ya ocupado
    assert len(set(distinguidas)) == 3


def test_etiquetas_boton_distinguibles_nunca_numera_ni_modifica_una_fija():
    # Una movible que coincide con una fija nunca puede quedar igual a ella
    # -- la fija nunca se toca, y la movible se numera (arrancando en 2,
    # como si la fija ocupara el primer lugar).
    titulos = ["Backup de servidores", "Backup de servidores"]

    distinguidas = etiquetas_boton_distinguibles(titulos, fijas=[True, False])

    assert distinguidas[0] == "Backup de servidores"        # fija: intacta
    assert distinguidas[1] == "Backup de servidores (2)"    # nunca igual a la fija
    assert len(set(distinguidas)) == 2


# ---------------------------------------------------------------------------
# Íconos de botón (decisión del usuario, 2026-09-28): cada categoría de botón
# lleva un ícono fijo, nunca decorativo. Single source of truth: `salida.py`.
# ---------------------------------------------------------------------------

def test_con_icono_antepone_el_icono_con_un_espacio():
    assert con_icono("Confirmar", ICONO_CONFIRMAR) == "✅ Confirmar"
    assert con_icono("Ver más", ICONO_VER_MAS) == "➕ Ver más"


def test_etiquetas_fijas_de_confirmar_y_cancelar():
    # Únicas -- todo el código que arma el par Confirmar/Cancelar reusa estas
    # dos constantes, nunca un literal repetido.
    assert ETIQUETA_CONFIRMAR == "✅ Confirmar"
    assert ETIQUETA_CANCELAR == "✖️ Cancelar"


def test_costo_icono_mide_en_unidades_utf16_no_en_caracteres():
    # 📋 es del plano astral: dos unidades UTF-16 aunque Python lo cuente
    # como un solo carácter (`len()` daría 1). Con el espacio que lo separa
    # del texto, el costo real es 3, no 2.
    assert len(ICONO_TAREA) == 1                    # un solo `str` codepoint
    assert telegram_utf16_units(ICONO_TAREA) == 2    # dos unidades UTF-16
    assert costo_icono(ICONO_TAREA) == 3
    assert costo_icono(ICONO_TAREA) == telegram_utf16_units(f"{ICONO_TAREA} ")


def test_etiqueta_sin_icono_quita_solo_un_icono_conocido_al_principio():
    assert etiqueta_sin_icono("📋 Revisar tablero") == "Revisar tablero"
    assert etiqueta_sin_icono("✅ Confirmar") == "Confirmar"
    # Sin ícono conocido al frente: se devuelve intacta.
    assert etiqueta_sin_icono("Revisar tablero") == "Revisar tablero"
    assert etiqueta_sin_icono("Modificar") == "Modificar"


def test_etiquetas_coinciden_ignora_el_icono_de_cualquiera_de_las_dos():
    assert etiquetas_coinciden("Confirmar", "✅ Confirmar")
    assert etiquetas_coinciden("✅ Confirmar", "Confirmar")
    assert etiquetas_coinciden("✅ Confirmar", "✅ Confirmar")
    assert not etiquetas_coinciden("Confirmar", "✖️ Cancelar")
    assert not etiquetas_coinciden("Confirmar", "Cancelar")


def test_etiqueta_de_tarea_con_icono_y_titulo_largo_sigue_entrando_en_el_limite():
    """El ícono cuenta hacia el límite de la etiqueta (decisión del usuario):
    quien arma un botón de tarea tiene que descontar `costo_icono` del
    objetivo/límite ANTES de truncar el texto -- el mismo patrón que usan
    `agente._opciones_lista_tareas`, `herramientas._ofrecer_opciones` y
    `gateway._candidatas_para_botones`/`_mostrar_mas_tareas`/`_pedir_
    eleccion_dependencia`."""
    titulo_largo = "Revisar comunicaciones industriales de la compresora principal"
    costo = costo_icono(ICONO_TAREA)

    corto = acortar_etiqueta_boton(
        titulo_largo, objetivo=OBJETIVO_ETIQUETA_BOTON - costo,
        limite=TRUNCAR_ETIQUETA_BOTON - costo)
    etiqueta = con_icono(corto, ICONO_TAREA)

    assert etiqueta.startswith(f"{ICONO_TAREA} ")
    assert titulo_largo.startswith(etiqueta_sin_icono(etiqueta).rstrip("…"))
    # El total (ícono + texto) sigue en el mismo objetivo "lindo" que tenía
    # el texto solo, y muy por debajo del límite técnico real de Telegram.
    assert telegram_utf16_units(etiqueta) <= OBJETIVO_ETIQUETA_BOTON
    assert telegram_utf16_units(etiqueta) <= BUTTON_LABEL_LIMIT


def test_etiquetas_de_tarea_que_colisionan_siguen_distinguibles_con_icono():
    titulo_a = "Revisar tablero de la máquina 3"
    titulo_b = "Revisar tablero de la máquina 4"
    costo = costo_icono(ICONO_TAREA)

    cortas = etiquetas_boton_distinguibles(
        [titulo_a, titulo_b], objetivo=OBJETIVO_ETIQUETA_BOTON - costo,
        limite=TRUNCAR_ETIQUETA_BOTON - costo)
    etiquetas = [con_icono(e, ICONO_TAREA) for e in cortas]

    assert len(set(etiquetas)) == 2                  # siguen distinguibles
    assert all(e.startswith(f"{ICONO_TAREA} ") for e in etiquetas)
    assert all(telegram_utf16_units(e) <= BUTTON_LABEL_LIMIT for e in etiquetas)
    # Tocar por la etiqueta pelada (una prueba, el banco) sigue resolviendo
    # la opción real ya armada con su ícono.
    assert etiquetas_coinciden(etiquetas[0], etiqueta_sin_icono(etiquetas[0]))


# --- T10-3 (R3-H10): Modificar lleva su ícono, como Confirmar y Cancelar, y su
# etiqueta se define una sola vez.


def test_modificar_lleva_el_icono_de_alternativa_junto_a_confirmar_y_cancelar():
    from leda.salida import ETIQUETA_MODIFICAR

    assert ETIQUETA_MODIFICAR == con_icono("Modificar", ICONO_OTRA_OPCION)
    assert ETIQUETA_MODIFICAR.startswith("✏️ ")
    assert etiqueta_sin_icono(ETIQUETA_MODIFICAR) == "Modificar"
    # Un toque simulado con la etiqueta pelada sigue resolviendo la opción real.
    assert etiquetas_coinciden(ETIQUETA_MODIFICAR, "Modificar")


def test_ningun_modulo_arma_el_boton_modificar_con_un_literal():
    """El botón se arma sólo con `salida.ETIQUETA_MODIFICAR`: un literal
    "Modificar" suelto en una lista de opciones vuelve a dejar el botón sin
    ícono en ese camino."""
    literales = []
    for archivo in (ROOT / "src" / "leda").glob("*.py"):
        if archivo.name == "salida.py":
            continue
        for numero, linea in enumerate(archivo.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r'\(\s*"Modificar"\s*,', linea):
                literales.append(f"{archivo.name}:{numero}")
    assert literales == []
