"""Pruebas de las acciones pendientes.

Una acción pendiente es trabajo que Prisma entendió pero todavía no ejecutó,
porque falta un acto de una persona: confirmarlo, o elegir entre opciones.

Es la pieza que faltaba para que la confirmación humana sea algo más que un
freno. Hasta ahora la acción se frenaba y se perdía: el pedido salía a la cola
como texto y la herramienta con sus argumentos se descartaba, así que confirmar
no podía ejecutar nada.

Lo que se prueba acá es que la acción sobreviva a la espera, que la ejecute
sólo quien corresponde, y que se ejecute una sola vez.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from prisma import pendientes as P
from prisma.autoridad import Canal, Denegado, identificar
from prisma.db import espacio

BA = ZoneInfo("America/Argentina/Buenos_Aires")
AHORA = datetime(2026, 7, 27, 10, 0, tzinfo=BA)


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s",
                (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _registrar_confirmacion(cur, quien, **extra):
    return P.registrar(
        cur, quien,
        herramienta="cambiar_fecha",
        args={"tarea_id": "00000000-0000-0000-0000-000000000001",
              "fecha_objetivo": "2026-08-20"},
        resumen="mover la fecha de Programar PLC al 20/08",
        vence_en=AHORA + timedelta(days=2),
        **extra)


# ---------------------------------------------------------------------------
# Confirmación diferida
# ---------------------------------------------------------------------------

def test_la_accion_sobrevive_a_la_espera_con_sus_argumentos(corework, conn):
    """Lo que hoy se pierde: herramienta y argumentos tienen que quedar."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        p = _registrar_confirmacion(cur, quien)

        guardada = P.buscar(cur, p.id)
        assert guardada.herramienta == "cambiar_fecha"
        assert guardada.args["fecha_objetivo"] == "2026-08-20"
        assert guardada.resumen == "mover la fecha de Programar PLC al 20/08"


def test_confirmar_devuelve_la_accion_lista_para_ejecutar(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        p = _registrar_confirmacion(cur, quien)
        confirmar = P.opcion_por_etiqueta(cur, p.id, "Confirmar")

        r = P.resolver(cur, confirmar.token, app_user_id=quien.app_user_id,
                       ahora=AHORA)

        assert r.cancelada is False
        assert r.herramienta == "cambiar_fecha"
        assert r.args["fecha_objetivo"] == "2026-08-20"


def test_confirmar_dos_veces_ejecuta_una_sola(corework, conn):
    """Dos toques al mismo botón no pueden mover la fecha dos veces."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        p = _registrar_confirmacion(cur, quien)
        confirmar = P.opcion_por_etiqueta(cur, p.id, "Confirmar")

        primera = P.resolver(cur, confirmar.token,
                             app_user_id=quien.app_user_id, ahora=AHORA)
        segunda = P.resolver(cur, confirmar.token,
                             app_user_id=quien.app_user_id, ahora=AHORA)

        assert primera is not None
        assert segunda is None


def test_cancelar_no_deja_nada_para_ejecutar(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        p = _registrar_confirmacion(cur, quien)
        cancelar = P.opcion_por_etiqueta(cur, p.id, "Cancelar")

        r = P.resolver(cur, cancelar.token, app_user_id=quien.app_user_id,
                       ahora=AHORA)

        assert r.cancelada is True
        assert r.herramienta is None


# ---------------------------------------------------------------------------
# Quién puede resolver
# ---------------------------------------------------------------------------

def test_otro_integrante_no_puede_resolver_lo_ajeno(corework, conn):
    """En un grupo, cualquiera ve el botón. Apretarlo no lo habilita.

    Es el mismo agujero que evitan los enlaces de activación entregados uno a
    uno: sin esto, alguien confirma en nombre de otro.
    """
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        otro = _quien(cur, "Ariel De Simone", ws)
        p = _registrar_confirmacion(cur, marcos)
        confirmar = P.opcion_por_etiqueta(cur, p.id, "Confirmar")

        with pytest.raises(Denegado):
            P.resolver(cur, confirmar.token, app_user_id=otro.app_user_id,
                       ahora=AHORA)

        assert P.buscar(cur, p.id).estado == "esperando"


def test_una_accion_vencida_no_se_resuelve(corework, conn):
    """El botón sigue ahí tres días después. El contexto ya no."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        p = _registrar_confirmacion(cur, quien)
        confirmar = P.opcion_por_etiqueta(cur, p.id, "Confirmar")

        r = P.resolver(cur, confirmar.token, app_user_id=quien.app_user_id,
                       ahora=AHORA + timedelta(days=3))

        assert r is None
        assert P.buscar(cur, p.id).estado == "vencida"


def test_un_token_inventado_no_resuelve_nada(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        assert P.resolver(cur, "noexiste123", app_user_id=quien.app_user_id,
                          ahora=AHORA) is None


# ---------------------------------------------------------------------------
# Opciones — desambiguar sin escribir
# ---------------------------------------------------------------------------

def test_elegir_una_opcion_completa_el_argumento_que_faltaba(corework, conn):
    """El caso 'Marcos o Martín': la respuesta es un identificador, no texto.

    Acá está el fondo del asunto. Si la persona escribe 'marcos', hay que
    volver a adivinar. Si elige, vuelve el identificador exacto.
    """
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        # Los dos empiezan con "Mar": es exactamente el caso que hoy resuelve
        # un `ilike ... limit 1` quedándose con el primero que aparezca.
        cur.execute("select membership_id, nombre from integrante "
                    "where nombre in ('Marcos Tarquini', 'Martín Forte')")
        candidatos = {c["nombre"]: str(c["membership_id"]) for c in cur.fetchall()}
        assert len(candidatos) == 2, "el pack de prueba necesita los dos"

        p = P.registrar(
            cur, quien,
            herramienta="crear_tarea",
            args={"titulo": "Relevar tablero", "area_slug": "ot"},
            resumen="crear Relevar tablero",
            vence_en=AHORA + timedelta(hours=2),
            campo="responsable_membership_id",
            opciones=list(candidatos.items()))

        elegida = P.opcion_por_etiqueta(cur, p.id, "Martín Forte")
        r = P.resolver(cur, elegida.token, app_user_id=quien.app_user_id,
                       ahora=AHORA)

        assert r.args["responsable_membership_id"] == candidatos["Martín Forte"]
        assert r.args["titulo"] == "Relevar tablero"


def test_el_token_entra_en_el_callback_data_de_telegram(corework, conn):
    """Telegram corta callback_data en 64 bytes. No es negociable."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        p = _registrar_confirmacion(cur, quien)

        for o in P.opciones(cur, p.id):
            assert len(P.callback_data(o).encode("utf-8")) <= 64


def test_los_tokens_no_se_repiten(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        a = _registrar_confirmacion(cur, quien)
        b = _registrar_confirmacion(cur, quien)

        tokens = {o.token for o in P.opciones(cur, a.id)}
        tokens |= {o.token for o in P.opciones(cur, b.id)}
        assert len(tokens) == 4
