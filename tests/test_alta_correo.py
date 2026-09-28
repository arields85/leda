"""Alta con correo verificado (rama auxiliar/alta-y-google, G1a).

El ciclo de alta con correo (`alta_correo_evento` / `alta_correo_estado`),
el token de verificación (`alta_correo_verificacion`, patrón
`acceso_tablero`), el contacto verificado (`alta_correo_contacto`) y los
avisos administrativos (`aviso_administrativo`). Nada de esto lo usa
`onboarding.py` todavía -- ese recorrido es G1b/G1c/G1d -- así que estas
pruebas ejercitan la base y `alta_correo.py` directamente.
"""

from __future__ import annotations

import contextlib
import threading
from datetime import datetime, timedelta, timezone

import psycopg
import pytest

from prisma import alta_correo as AC
from prisma.db import admin, conectar, espacio

AHORA = datetime(2028, 3, 15, 12, 0, tzinfo=timezone.utc)


@contextlib.contextmanager
def sin_espacio(conn):
    """La aplicación antes de saber a qué espacio pertenece el pedido.

    Mismo patrón que `test_tablero.py`: `alta_correo_verificacion` no lleva
    política de aislamiento, así que resolver un token no necesita (ni
    puede) declarar un espacio de antemano.
    """
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local role prisma_app")
            yield cur


def _membership(mundo, slug, persona="Taylor Quinn"):
    return mundo[slug]["people"][persona]["membership_id"]


# ---------------------------------------------------------------------------
# El ciclo de estados (§4 del pack)
# ---------------------------------------------------------------------------


def test_el_ciclo_alta_recorre_los_cinco_estados(intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
        assert AC.estado(cur, m)["estado"] == "pending_welcome"
        assert AC.estado(cur, m)["modo"] == "alta"
        assert AC.estado(cur, m)["ciclo"] == 1

        AC.transicionar(cur, m, "awaiting_email", ahora=AHORA)
        assert AC.estado(cur, m)["estado"] == "awaiting_email"

        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        assert AC.estado(cur, m)["estado"] == "pending_email_verification"

        AC.transicionar(cur, m, "active", ahora=AHORA)
        assert AC.estado(cur, m)["estado"] == "active"

        AC.transicionar(cur, m, "revoked", ahora=AHORA)
        assert AC.estado(cur, m)["estado"] == "revoked"
    conn.commit()


def test_el_modo_existente_empieza_en_awaiting_email(intake_world, conn):
    """C5: a quien ya estaba activo se le pide el correo sin pending_welcome."""
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        AC.iniciar_ciclo(cur, m, "existente", ahora=AHORA)
        fila = AC.estado(cur, m)
        assert fila["estado"] == "awaiting_email"
        assert fila["modo"] == "existente"
    conn.commit()


def test_correccion_de_correo_vuelve_de_pending_verification_a_awaiting_email(
        intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
        AC.transicionar(cur, m, "awaiting_email", ahora=AHORA)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.transicionar(cur, m, "awaiting_email", ahora=AHORA)
        assert AC.estado(cur, m)["estado"] == "awaiting_email"
    conn.commit()


@pytest.mark.parametrize("desde,hacia", [
    ("pending_welcome", "pending_email_verification"),
    ("pending_welcome", "active"),
    ("awaiting_email", "active"),
    ("pending_email_verification", "revoked"),
    ("active", "awaiting_email"),
])
def test_las_transiciones_invalidas_las_rechaza_la_base(
        intake_world, conn, desde, hacia):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
        # Llega hasta el estado de partida por el camino válido.
        camino = ["awaiting_email", "pending_email_verification", "active"]
        for paso in camino:
            if AC.estado(cur, m)["estado"] == desde:
                break
            AC.transicionar(cur, m, paso, ahora=AHORA)

        with pytest.raises(psycopg.Error), conn.transaction():
            AC.transicionar(cur, m, hacia, ahora=AHORA)
    conn.commit()


def test_revoked_es_terminal_y_no_reactiva_con_el_ciclo_viejo(intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
        AC.transicionar(cur, m, "awaiting_email", ahora=AHORA)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.transicionar(cur, m, "active", ahora=AHORA)
        AC.transicionar(cur, m, "revoked", ahora=AHORA)

        with pytest.raises(psycopg.Error), conn.transaction():
            AC.transicionar(cur, m, "awaiting_email", ahora=AHORA)
    conn.commit()


def test_no_se_puede_abrir_un_ciclo_nuevo_sin_revocar_el_anterior(
        intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
        AC.transicionar(cur, m, "awaiting_email", ahora=AHORA)

        with pytest.raises(psycopg.Error), conn.transaction():
            AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
    conn.commit()


def test_una_nueva_alta_administrativa_abre_el_ciclo_siguiente_tras_revocar(
        intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
        AC.transicionar(cur, m, "awaiting_email", ahora=AHORA)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.transicionar(cur, m, "active", ahora=AHORA)
        AC.transicionar(cur, m, "revoked", ahora=AHORA)

        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
        fila = AC.estado(cur, m)
        assert fila["ciclo"] == 2
        assert fila["estado"] == "pending_welcome"
    conn.commit()


def test_el_estado_no_se_escribe_con_update_directo(intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
    conn.commit()

    with admin(conn) as cur:
        with pytest.raises(psycopg.Error, match="no se escribe directamente"), \
                conn.transaction():
            cur.execute(
                "update alta_correo_estado set estado = 'active' "
                "where membership_id = %s", (m,))
    conn.commit()


# ---------------------------------------------------------------------------
# review_required y la bienvenida entregada
# ---------------------------------------------------------------------------


def test_review_required_se_marca_y_se_resuelve_por_evento(intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
        AC.marcar_revision(cur, m, "Gmail no respondió", ahora=AHORA)
        fila = AC.estado(cur, m)
        assert fila["review_required"] is True
        assert fila["review_required_causa"] == "Gmail no respondió"
        assert fila["review_required_desde"] is not None

        # Leer la marca no la resuelve: sigue vigente hasta un evento aparte.
        AC.resolver_revision(cur, m, ahora=AHORA)
        fila = AC.estado(cur, m)
        assert fila["review_required"] is False
        assert fila["review_required_causa"] is None
    conn.commit()


def test_un_ciclo_nuevo_no_hereda_la_marca_de_revision_del_anterior(
        intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
        AC.marcar_revision(cur, m, "correo rebotado", ahora=AHORA)
        AC.transicionar(cur, m, "awaiting_email", ahora=AHORA)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.transicionar(cur, m, "active", ahora=AHORA)
        AC.transicionar(cur, m, "revoked", ahora=AHORA)

        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
        fila = AC.estado(cur, m)
        assert fila["review_required"] is False
        assert fila["review_required_causa"] is None
    conn.commit()


def test_la_bienvenida_entregada_queda_registrada_una_vez_por_ciclo(
        intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
        AC.bienvenida_entregada(cur, m, ahora=AHORA)
        assert AC.estado(cur, m)["bienvenida_entregada_en"] is not None

        with pytest.raises(psycopg.Error), conn.transaction():
            AC.bienvenida_entregada(cur, m, ahora=AHORA)
    conn.commit()


# ---------------------------------------------------------------------------
# El token de verificación
# ---------------------------------------------------------------------------


def _hasta_awaiting_email(cur, m, ahora=AHORA):
    AC.iniciar_ciclo(cur, m, "alta", ahora=ahora)
    AC.transicionar(cur, m, "awaiting_email", ahora=ahora)


def test_recorrido_completo_de_verificacion_de_correo(intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, m)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)

        resultado = AC.emitir_verificacion(
            cur, m, "Persona@Example.com", "token-uno", ahora=AHORA)
        assert resultado.ok is True

        reserva = AC.reservar_verificacion(cur, "token-uno", m, ahora=AHORA)
        assert reserva.ok is True
        assert reserva.email == "persona@example.com"

        completado = AC.completar_verificacion(cur, "token-uno", m, ahora=AHORA)
        assert completado.ok is True

        assert AC.estado(cur, m)["estado"] == "active"
        assert AC.contacto_verificado(cur, m)["email"] == "persona@example.com"
    conn.commit()


def test_si_el_estado_cambio_completar_no_deja_un_contacto_a_medias(
        intake_world, conn):
    """Un fallo por estado cambiado no deja el correo registrado como
    verificado ni consume el token: el ciclo sigue donde estaba."""
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, m)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(cur, m, "persona@example.com", "token-uno",
                               ahora=AHORA)
        assert AC.reservar_verificacion(cur, "token-uno", m, ahora=AHORA).ok
        # La persona corrige el correo mientras el enlace viejo está abierto.
        AC.transicionar(cur, m, "awaiting_email", ahora=AHORA)

        completado = AC.completar_verificacion(cur, "token-uno", m, ahora=AHORA)

        assert completado.ok is False
        assert completado.motivo == "verification_state_changed"
        assert AC.contacto_verificado(cur, m) is None
        assert AC.estado(cur, m)["estado"] == "awaiting_email"
    conn.commit()


def test_completar_sin_reserva_previa_devuelve_ocupado_y_no_deja_rastro(
        intake_world, conn):
    """Nunca se reservó el token: `completar` lo trata como ocupado (nadie
    lo tiene, pero tampoco es de quien llama todavía), no deja contacto y no
    lo consume (G1a2, cobertura de caminos de falla)."""
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, m)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(cur, m, "persona@example.com", "token-sin-reserva",
                               ahora=AHORA)

        completado = AC.completar_verificacion(cur, "token-sin-reserva", m, ahora=AHORA)

        assert completado.ok is False
        assert completado.motivo == "verification_token_busy"
        assert AC.contacto_verificado(cur, m) is None
        assert AC.estado(cur, m)["estado"] == "pending_email_verification"

        # Nunca estuvo reservado: se puede reservar normalmente ahora.
        reserva = AC.reservar_verificacion(cur, "token-sin-reserva", m, ahora=AHORA)
        assert reserva.ok is True
    conn.commit()


def test_completar_con_reserva_vencida_devuelve_ocupado_y_no_deja_rastro(
        intake_world, conn):
    """La reserva vive 5 minutos: pasado ese plazo, `completar` la trata
    igual que si nunca se hubiera reservado (G1a2, cobertura de caminos de
    falla)."""
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, m)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(cur, m, "persona@example.com", "token-vencido-reserva",
                               ahora=AHORA)
        assert AC.reservar_verificacion(
            cur, "token-vencido-reserva", m, ahora=AHORA).ok

        vencida = AHORA + timedelta(minutes=6)
        completado = AC.completar_verificacion(
            cur, "token-vencido-reserva", m, ahora=vencida)

        assert completado.ok is False
        assert completado.motivo == "verification_token_busy"
        assert AC.contacto_verificado(cur, m) is None
        assert AC.estado(cur, m)["estado"] == "pending_email_verification"

        # La reserva vencida no bloquea una reserva nueva: queda liberada de hecho.
        reserva = AC.reservar_verificacion(
            cur, "token-vencido-reserva", m, ahora=vencida)
        assert reserva.ok is True
    conn.commit()


def test_completar_falla_por_correo_verificado_por_otro_durante_la_reserva(
        intake_world, conn):
    """email_in_use en `completar`: otro integrante del espacio verificó el
    mismo correo mientras el primero seguía con el token reservado (G1a2,
    cobertura de caminos de falla)."""
    norte = intake_world["north-lab"]
    m1 = _membership(intake_world, "north-lab", "Taylor Quinn")
    m2 = _membership(intake_world, "north-lab", "Sam North")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, m1)
        AC.transicionar(cur, m1, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(cur, m1, "compartido@example.com", "token-primero",
                               ahora=AHORA)
        assert AC.reservar_verificacion(cur, "token-primero", m1, ahora=AHORA).ok

        # Mientras el token de m1 sigue reservado, m2 verifica el mismo correo primero.
        _hasta_awaiting_email(cur, m2)
        AC.transicionar(cur, m2, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(cur, m2, "compartido@example.com", "token-segundo",
                               ahora=AHORA)
        AC.reservar_verificacion(cur, "token-segundo", m2, ahora=AHORA)
        assert AC.completar_verificacion(cur, "token-segundo", m2, ahora=AHORA).ok

        completado = AC.completar_verificacion(cur, "token-primero", m1, ahora=AHORA)

        assert completado.ok is False
        assert completado.motivo == "email_in_use"
        assert AC.contacto_verificado(cur, m1) is None
        assert AC.estado(cur, m1)["estado"] == "pending_email_verification"

        # La reserva quedó liberada y el token no se consumió.
        reintento = AC.reservar_verificacion(cur, "token-primero", m1, ahora=AHORA)
        assert reintento.ok is True
    conn.commit()


def test_completar_desde_una_sesion_sin_espacio_declarado_verifica_el_camino_feliz(
        intake_world, conn):
    """El `/start pv_{token}` de Telegram llega antes de saber a qué equipo
    pertenece: `completar_verificacion_correo` tiene que resolver el camino
    feliz igual, fijando el espacio del token antes de tocar tablas con
    política de aislamiento (G1a2, hallazgo de la revisión)."""
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, m)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(cur, m, "persona@example.com", "token-sin-espacio",
                               ahora=AHORA)
    conn.commit()

    with sin_espacio(conn) as cur:
        assert AC.reservar_verificacion(cur, "token-sin-espacio", m, ahora=AHORA).ok
        completado = AC.completar_verificacion(cur, "token-sin-espacio", m, ahora=AHORA)
        assert completado.ok is True
        assert completado.motivo is None
    conn.commit()

    with espacio(conn, norte["id"]) as cur:
        assert AC.estado(cur, m)["estado"] == "active"
        assert AC.contacto_verificado(cur, m)["email"] == "persona@example.com"


def test_el_correo_se_normaliza_en_un_solo_lugar(intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, m)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(
            cur, m, "  Persona@Example.com  ", "token-normalizado", ahora=AHORA)
        AC.reservar_verificacion(cur, "token-normalizado", m, ahora=AHORA)
        AC.completar_verificacion(cur, "token-normalizado", m, ahora=AHORA)

        assert AC.contacto_verificado(cur, m)["email"] == "persona@example.com"
    conn.commit()


def test_confirmar_el_mismo_correo_del_mismo_integrante_es_idempotente(
        intake_world, conn):
    """Corrección dentro del mismo ciclo, antes de llegar a `active`: mismo
    correo, token nuevo -- el contacto no choca contra sí mismo."""
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, m)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(cur, m, "persona@example.com", "token-a", ahora=AHORA)

        # Todavía no se completó: se corrige (mismo correo) y se reenvía.
        AC.transicionar(cur, m, "awaiting_email", ahora=AHORA)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(cur, m, "persona@example.com", "token-b", ahora=AHORA)
        AC.reservar_verificacion(cur, "token-b", m, ahora=AHORA)
        resultado = AC.completar_verificacion(cur, "token-b", m, ahora=AHORA)

        assert resultado.ok is True
        assert AC.contacto_verificado(cur, m)["email"] == "persona@example.com"
    conn.commit()


def test_reverificar_el_mismo_correo_en_un_ciclo_nuevo_es_idempotente(
        intake_world, conn):
    """El mismo integrante puede volver a verificar el mismo correo en un
    ciclo posterior (tras revocar) sin chocar contra su propio contacto."""
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, m)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(cur, m, "persona@example.com", "token-1", ahora=AHORA)
        AC.reservar_verificacion(cur, "token-1", m, ahora=AHORA)
        AC.completar_verificacion(cur, "token-1", m, ahora=AHORA)
        primero = AC.contacto_verificado(cur, m)
        AC.transicionar(cur, m, "revoked", ahora=AHORA)

        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
        AC.transicionar(cur, m, "awaiting_email", ahora=AHORA)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(cur, m, "persona@example.com", "token-2", ahora=AHORA)
        AC.reservar_verificacion(cur, "token-2", m, ahora=AHORA)
        resultado = AC.completar_verificacion(cur, "token-2", m, ahora=AHORA)

        assert resultado.ok is True
        assert AC.contacto_verificado(cur, m)["email"] == primero["email"]
    conn.commit()


def test_un_correo_activo_de_otro_integrante_del_espacio_se_rechaza(
        intake_world, conn):
    norte = intake_world["north-lab"]
    m1 = _membership(intake_world, "north-lab", "Taylor Quinn")
    m2 = _membership(intake_world, "north-lab", "Sam North")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, m1)
        AC.transicionar(cur, m1, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(cur, m1, "compartido@example.com", "token-1", ahora=AHORA)
        AC.reservar_verificacion(cur, "token-1", m1, ahora=AHORA)
        AC.completar_verificacion(cur, "token-1", m1, ahora=AHORA)

        _hasta_awaiting_email(cur, m2)
        AC.transicionar(cur, m2, "pending_email_verification", ahora=AHORA)
        resultado = AC.emitir_verificacion(
            cur, m2, "compartido@example.com", "token-2", ahora=AHORA)
        assert resultado.ok is False
        assert resultado.motivo == "email_in_use"
    conn.commit()


def test_token_vencido_no_se_puede_reservar_ni_completar(intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")
    emitido = AHORA - timedelta(hours=25)

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, m, ahora=emitido)
        AC.transicionar(cur, m, "pending_email_verification", ahora=emitido)
        AC.emitir_verificacion(
            cur, m, "persona@example.com", "token-viejo", ahora=emitido)

        reserva = AC.reservar_verificacion(cur, "token-viejo", m, ahora=AHORA)
        assert reserva.ok is False
        assert reserva.motivo == "verification_token_expired"

        completado = AC.completar_verificacion(cur, "token-viejo", m, ahora=AHORA)
        assert completado.ok is False
        assert completado.motivo == "verification_token_expired"
    conn.commit()


def test_token_consumido_no_reactiva_un_ciclo_ya_revocado(intake_world, conn):
    """Un enlace viejo no reactiva: ni consumido, ni tras revocar el ciclo."""
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, m)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(cur, m, "persona@example.com", "token-1", ahora=AHORA)
        AC.reservar_verificacion(cur, "token-1", m, ahora=AHORA)
        AC.completar_verificacion(cur, "token-1", m, ahora=AHORA)
        AC.transicionar(cur, m, "revoked", ahora=AHORA)

        reserva = AC.reservar_verificacion(cur, "token-1", m, ahora=AHORA)
        assert reserva.ok is False
        assert reserva.motivo == "verification_token_consumed"
    conn.commit()


def test_un_enlace_reenviado_a_otra_cuenta_no_verifica(intake_world, conn):
    """A04: el token sólo verifica a la membresía que lo originó."""
    norte = intake_world["north-lab"]
    propietario = _membership(intake_world, "north-lab", "Taylor Quinn")
    otro = _membership(intake_world, "north-lab", "Sam North")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, propietario)
        AC.transicionar(cur, propietario, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(
            cur, propietario, "propietario@example.com", "token-ajeno", ahora=AHORA)

        reserva = AC.reservar_verificacion(cur, "token-ajeno", otro, ahora=AHORA)
        assert reserva.ok is False
        assert reserva.motivo == "verification_token_invalid"

        completado = AC.completar_verificacion(cur, "token-ajeno", otro, ahora=AHORA)
        assert completado.ok is False
        assert completado.motivo == "verification_token_invalid"

        # La membresía correcta todavía puede verificarlo.
        assert AC.reservar_verificacion(cur, "token-ajeno", propietario, ahora=AHORA).ok
    conn.commit()


def test_la_reserva_es_de_exclusion_mutua_por_cinco_minutos(intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, m)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(cur, m, "persona@example.com", "token-1", ahora=AHORA)

        primera = AC.reservar_verificacion(cur, "token-1", m, ahora=AHORA)
        assert primera.ok is True

        ocupada = AC.reservar_verificacion(
            cur, "token-1", m, ahora=AHORA + timedelta(minutes=2))
        assert ocupada.ok is False
        assert ocupada.motivo == "verification_token_busy"

        libre = AC.reservar_verificacion(
            cur, "token-1", m, ahora=AHORA + timedelta(minutes=6))
        assert libre.ok is True
    conn.commit()


def test_limite_de_tres_envios_por_hora(intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, m, ahora=AHORA)
        for i in range(3):
            resultado = AC.emitir_verificacion(
                cur, m, "persona@example.com", f"token-{i}",
                ahora=AHORA + timedelta(minutes=i))
            assert resultado.ok is True, resultado.motivo

        cuarto = AC.emitir_verificacion(
            cur, m, "persona@example.com", "token-cuarto",
            ahora=AHORA + timedelta(minutes=30))
        assert cuarto.ok is False
        assert cuarto.motivo == "verification_rate_limited"

        # Una hora después, la ventana rodante ya lo permite.
        pasada_la_hora = AC.emitir_verificacion(
            cur, m, "persona@example.com", "token-quinto",
            ahora=AHORA + timedelta(hours=1, minutes=1))
        assert pasada_la_hora.ok is True
    conn.commit()


def test_limite_de_cinco_envios_por_ciclo_incluye_el_inicial(intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, m, ahora=AHORA)
        for i in range(5):
            resultado = AC.emitir_verificacion(
                cur, m, "persona@example.com", f"token-{i}",
                ahora=AHORA + timedelta(hours=2 * i))
            assert resultado.ok is True, resultado.motivo

        sexto = AC.emitir_verificacion(
            cur, m, "persona@example.com", "token-sexto",
            ahora=AHORA + timedelta(hours=20))
        assert sexto.ok is False
        assert sexto.motivo == "verification_send_limit"
    conn.commit()


def test_no_se_puede_emitir_verificacion_sin_un_ciclo_abierto(intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        resultado = AC.emitir_verificacion(
            cur, m, "persona@example.com", "token-sin-ciclo", ahora=AHORA)
        assert resultado.ok is False
        assert resultado.motivo == "verification_no_cycle"
    conn.commit()


def test_no_se_puede_emitir_verificacion_en_pending_welcome_ni_en_active(
        intake_world, conn):
    """Sólo `awaiting_email` y `pending_email_verification` piden o reenvían
    el correo (G1a2, hallazgo de la revisión): antes de la bienvenida, o ya
    verificado, un envío es un error de programación, no un caso de negocio."""
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
        assert AC.estado(cur, m)["estado"] == "pending_welcome"

        resultado = AC.emitir_verificacion(
            cur, m, "persona@example.com", "token-en-pending-welcome", ahora=AHORA)
        assert resultado.ok is False
        assert resultado.motivo == "verification_state_invalid"

        AC.transicionar(cur, m, "awaiting_email", ahora=AHORA)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(cur, m, "persona@example.com", "token-real", ahora=AHORA)
        AC.reservar_verificacion(cur, "token-real", m, ahora=AHORA)
        AC.completar_verificacion(cur, "token-real", m, ahora=AHORA)
        assert AC.estado(cur, m)["estado"] == "active"

        resultado = AC.emitir_verificacion(
            cur, m, "persona@example.com", "token-en-active", ahora=AHORA)
        assert resultado.ok is False
        assert resultado.motivo == "verification_state_invalid"
    conn.commit()


def test_dos_emisiones_concurrentes_no_rompen_los_limites_ni_el_indice_unico(
        intake_world, conn, uri):
    """El `for update` sobre la proyección serializa dos emisiones
    concurrentes para la misma membresía: ninguna de las dos ve una
    excepción cruda y, al terminar, hay exactamente una fila vigente (G1a2,
    hallazgo de la revisión sobre la carrera en el índice único)."""
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, m, ahora=AHORA)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
    conn.commit()

    # Con tiempos de espera acotados: si un hilo falla antes de la barrera, el
    # otro no queda esperando para siempre y la prueba falla en vez de colgarse.
    barrier = threading.Barrier(2, timeout=30)
    outcomes = []
    failures = []

    def emitir(index):
        other = None
        try:
            other = conectar(uri)
            with espacio(other, norte["id"]) as cur:
                barrier.wait()
                outcomes.append(AC.emitir_verificacion(
                    cur, m, "persona@example.com", f"token-concurrente-{index}",
                    ahora=AHORA))
            other.commit()
        except Exception as exc:  # probamos que ninguna excepción cruda escapa
            failures.append(exc)
            barrier.abort()
            if other is not None:
                other.rollback()
        finally:
            if other is not None:
                other.close()

    threads = [threading.Thread(target=emitir, args=(index,)) for index in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)
    assert not any(thread.is_alive() for thread in threads), "un hilo quedó colgado"

    assert failures == []
    assert all(outcome.ok for outcome in outcomes), outcomes

    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from alta_correo_verificacion "
            "where membership_id = %s and vigente", (m,))
        assert cur.fetchone()["n"] == 1
        cur.execute(
            "select count(*) n from alta_correo_verificacion where membership_id = %s",
            (m,))
        assert cur.fetchone()["n"] == 2


def test_el_token_en_claro_no_queda_en_la_base(intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, m, ahora=AHORA)
        AC.emitir_verificacion(
            cur, m, "persona@example.com", "token-secreto-en-claro", ahora=AHORA)
    conn.commit()

    with admin(conn) as cur:
        cur.execute("select * from alta_correo_verificacion")
        filas = cur.fetchall()

    assert filas, "no se guardó ningún envío de verificación"
    for fila in filas:
        for columna, valor in fila.items():
            assert "token-secreto-en-claro" not in str(valor), (
                f"el token en claro apareció en la columna {columna}")


# ---------------------------------------------------------------------------
# Privilegios: nada de esto lo toca prisma_app directamente
# ---------------------------------------------------------------------------


def test_prisma_app_no_tiene_privilegios_directos_sobre_el_token(
        intake_world, conn):
    norte = intake_world["north-lab"]

    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute("select * from alta_correo_verificacion")

    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute(
                "insert into alta_correo_verificacion "
                "(workspace_id, membership_id, ciclo, email, token_hash, expira_en) "
                "values (%s, %s, 1, 'x@example.com', 'hash', now())",
                (norte["id"], _membership(intake_world, "north-lab")))


def test_prisma_app_no_puede_escribir_el_contacto_verificado_directo(
        intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute(
                "insert into alta_correo_contacto (membership_id, workspace_id, email) "
                "values (%s, %s, 'x@example.com')", (m, norte["id"]))

    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute(
                "update alta_correo_contacto set email = 'y@example.com' "
                "where membership_id = %s", (m,))
        # select sí está permitido: no hace falta pasar por una función para leer.
        cur.execute("select * from alta_correo_contacto")
        assert cur.fetchall() == []


def test_prisma_app_solo_inserta_eventos_de_alta_correo(intake_world, conn):
    norte = intake_world["north-lab"]
    m = _membership(intake_world, "north-lab")

    with espacio(conn, norte["id"]) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)

    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute("select * from alta_correo_evento")

    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute(
                "update alta_correo_evento set causa = 'x' where membership_id = %s",
                (m,))


# ---------------------------------------------------------------------------
# Aislamiento entre espacios
# ---------------------------------------------------------------------------


def test_un_espacio_no_ve_el_ciclo_de_alta_del_otro(intake_world, conn):
    norte = intake_world["north-lab"]
    oeste = intake_world["west-studio"]
    mn = _membership(intake_world, "north-lab")
    mo = _membership(intake_world, "west-studio")

    with espacio(conn, norte["id"]) as cur:
        AC.iniciar_ciclo(cur, mn, "alta", ahora=AHORA)
    with espacio(conn, oeste["id"]) as cur:
        AC.iniciar_ciclo(cur, mo, "existente", ahora=AHORA)
    conn.commit()

    with espacio(conn, norte["id"]) as cur:
        cur.execute("select membership_id from alta_correo_estado")
        vistos = {str(f["membership_id"]) for f in cur.fetchall()}
        assert vistos == {mn}

    with espacio(conn, oeste["id"]) as cur:
        cur.execute("select membership_id from alta_correo_estado")
        vistos = {str(f["membership_id"]) for f in cur.fetchall()}
        assert vistos == {mo}


def test_el_mismo_correo_en_dos_espacios_distintos_no_choca(intake_world, conn):
    """La unicidad del correo verificado es por espacio, no global."""
    norte = intake_world["north-lab"]
    oeste = intake_world["west-studio"]
    mn = _membership(intake_world, "north-lab")
    mo = _membership(intake_world, "west-studio")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, mn)
        AC.transicionar(cur, mn, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(cur, mn, "compartido@example.com", "token-norte", ahora=AHORA)
        AC.reservar_verificacion(cur, "token-norte", mn, ahora=AHORA)
        AC.completar_verificacion(cur, "token-norte", mn, ahora=AHORA)
    conn.commit()

    with espacio(conn, oeste["id"]) as cur:
        _hasta_awaiting_email(cur, mo)
        AC.transicionar(cur, mo, "pending_email_verification", ahora=AHORA)
        resultado = AC.emitir_verificacion(
            cur, mo, "compartido@example.com", "token-oeste", ahora=AHORA)
        assert resultado.ok is True
        AC.reservar_verificacion(cur, "token-oeste", mo, ahora=AHORA)
        completado = AC.completar_verificacion(cur, "token-oeste", mo, ahora=AHORA)
        assert completado.ok is True
        assert AC.contacto_verificado(cur, mo)["email"] == "compartido@example.com"
    conn.commit()


def test_un_token_de_otro_espacio_no_verifica_con_una_membresia_ajena(
        intake_world, conn):
    norte = intake_world["north-lab"]
    mn = _membership(intake_world, "north-lab")
    mo = _membership(intake_world, "west-studio")

    with espacio(conn, norte["id"]) as cur:
        _hasta_awaiting_email(cur, mn)
        AC.transicionar(cur, mn, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(
            cur, mn, "persona@example.com", "token-cruzado", ahora=AHORA)

    with sin_espacio(conn) as cur:
        reserva = AC.reservar_verificacion(cur, "token-cruzado", mo, ahora=AHORA)
        assert reserva.ok is False
        assert reserva.motivo == "verification_token_invalid"


# ---------------------------------------------------------------------------
# La clave del espacio
# ---------------------------------------------------------------------------


def test_la_clave_de_correo_esta_apagada_por_defecto(intake_world, conn):
    norte = intake_world["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        assert AC.habilitado(cur, norte["id"]) is False


def test_la_clave_de_correo_es_configuracion_del_espacio(intake_world, conn):
    norte = intake_world["north-lab"]

    with admin(conn) as cur:
        cur.execute(
            "insert into workspace_setting (workspace_id, clave, valor) "
            "values (%s, %s, 'true')", (norte["id"], AC.CLAVE_HABILITADO))
    conn.commit()

    with espacio(conn, norte["id"]) as cur:
        assert AC.habilitado(cur, norte["id"]) is True


def test_habilitado_filtra_por_el_espacio_explicito_no_solo_por_rls(
        intake_world, conn):
    """`admin()` ve todos los espacios: sin el filtro explícito por
    `workspace_id`, una conexión de administración podría leer la clave de
    un espacio ajeno en vez de la propia."""
    norte = intake_world["north-lab"]
    oeste = intake_world["west-studio"]

    with admin(conn) as cur:
        cur.execute(
            "insert into workspace_setting (workspace_id, clave, valor) "
            "values (%s, %s, 'true')", (oeste["id"], AC.CLAVE_HABILITADO))
    conn.commit()

    with admin(conn) as cur:
        assert AC.habilitado(cur, norte["id"]) is False
        assert AC.habilitado(cur, oeste["id"]) is True


# ---------------------------------------------------------------------------
# Avisos administrativos -- leído no es resuelto
# ---------------------------------------------------------------------------


def test_un_aviso_leido_no_queda_resuelto(intake_world, conn):
    norte = intake_world["north-lab"]
    admin_id = norte["people"]["Morgan Hale"]["app_user_id"]

    with espacio(conn, norte["id"]) as cur:
        aviso_id = AC.crear_aviso(
            cur, "correo_pendiente",
            "3 integrantes todavía no dieron su correo laboral.",
            ahora=AHORA)
        AC.marcar_leido(cur, aviso_id, admin_id, ahora=AHORA)

        [fila] = AC.avisos(cur)
        assert fila["leido_en"] is not None
        assert fila["resuelto_en"] is None

        pendientes = AC.avisos(cur, solo_no_resueltos=True)
        assert len(pendientes) == 1

        AC.marcar_resuelto(cur, aviso_id, admin_id, ahora=AHORA)
        assert AC.avisos(cur, solo_no_resueltos=True) == []
    conn.commit()


def test_aviso_pendiente_ve_el_no_resuelto_e_ignora_el_resuelto(
        intake_world, conn):
    """G1b2, ítem 5: la base para "crear el aviso una sola vez" -- mientras
    quede sin resolver, `aviso_pendiente` lo encuentra; una vez resuelto,
    deja de contar (un nuevo golpe del mismo límite sí puede crear otro)."""
    norte = intake_world["north-lab"]
    m = norte["people"]["Morgan Hale"]["membership_id"]
    admin_id = norte["people"]["Morgan Hale"]["app_user_id"]

    with espacio(conn, norte["id"]) as cur:
        assert AC.aviso_pendiente(cur, "correo_limite_agotado", "membership", m) is False

        aviso_id = AC.crear_aviso(
            cur, "correo_limite_agotado", "texto", referencia_tipo="membership",
            referencia_id=m, ahora=AHORA)
        assert AC.aviso_pendiente(cur, "correo_limite_agotado", "membership", m) is True
        # Otro tipo, o otra referencia, no cuenta.
        assert AC.aviso_pendiente(cur, "correo_sin_emisor", "membership", m) is False

        AC.marcar_resuelto(cur, aviso_id, admin_id, ahora=AHORA)
        assert AC.aviso_pendiente(cur, "correo_limite_agotado", "membership", m) is False
    conn.commit()


def test_los_avisos_administrativos_estan_aislados_por_espacio(
        intake_world, conn):
    norte = intake_world["north-lab"]
    oeste = intake_world["west-studio"]

    with espacio(conn, norte["id"]) as cur:
        AC.crear_aviso(cur, "correo_pendiente", "aviso del norte", ahora=AHORA)
    with espacio(conn, oeste["id"]) as cur:
        AC.crear_aviso(cur, "correo_pendiente", "aviso del oeste", ahora=AHORA)
    conn.commit()

    with espacio(conn, norte["id"]) as cur:
        textos = {f["texto_saneado"] for f in AC.avisos(cur)}
        assert textos == {"aviso del norte"}


def test_ningun_aviso_administrativo_lleva_cuerpo_de_conversacion(
        intake_world, conn):
    """Regla de seguridad de AGENTS.md: nunca cuerpos de mensaje ni secretos."""
    norte = intake_world["north-lab"]
    texto = "Reenvío agotado para Sam North; revisar manualmente."

    with espacio(conn, norte["id"]) as cur:
        AC.crear_aviso(cur, "verificacion_agotada", texto, ahora=AHORA)
        [fila] = AC.avisos(cur)
        assert fila["texto_saneado"] == texto
        assert "token" not in fila["texto_saneado"].lower()
    conn.commit()
