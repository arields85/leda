"""Recorrido conversacional del alta con correo (rama auxiliar, G1b).

`test_alta_correo.py` (G1a/G1a2) ejercita la base y `alta_correo.py`
directamente. Estas pruebas son de gateway: el webhook de Telegram, el
control (`gate`) antepuesto al despacho conversacional, los botones y
`/start pv_{token}`, con un doble de puerto de correo -- nunca un envío
real -- y (para la activación) el paquete `corework` real, como
`test_onboarding.py`.
"""

from __future__ import annotations

import contextlib
import dataclasses
import re
import threading
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from prisma import alta_correo as AC
from prisma import alta_correo_flujo as ACF
from prisma import gateway
from prisma.db import admin, conectar, espacio
from prisma.llm import ProveedorGuionado, Respuesta

from tests.alta_correo_ayudas import (
    AHORA,
    DobleEnvioCorreo,
    EnvioRegistrado,
    _abrir_awaiting_email,
    _avisos,
    _estado,
    _habilitar,
    _membership_id,
    _outbox_textos,
    _post,
    _post_grupo,
    _post_toque,
    _sender,
    _token_boton,
    _token_de_enlace,
    cliente,
    con_agente,
)


def _reenviar(cliente, conn, ws, m, tg_user):
    """Escribe algo que no es un correo (dispara el recordatorio con
    botones) y aprieta Reenviar correo."""
    _post(cliente, "hola, sigo esperando?", tg_user)
    token = _token_boton(conn, ws, m, ACF.ETIQUETA_REENVIAR)
    assert token, "no se ofreció el botón Reenviar correo"
    return _post_toque(cliente, token, tg_user)


def _incidentes(conn, ws: str) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(
            "select severidad, resumen_sanitizado, referencia_cruda from incident "
            "where workspace_id = %s", (ws,))
        return cur.fetchall()


def _verificaciones(conn, m: str) -> list[dict]:
    """Sólo lo puede leer `prisma_admin`: `alta_correo_verificacion` no
    concede nada a `prisma_app` -- ver `alta_correo.py`."""
    with admin(conn) as cur:
        cur.execute(
            "select email, vigente, consumido_en from alta_correo_verificacion "
            "where membership_id = %s", (m,))
        return cur.fetchall()


@contextlib.contextmanager
def _sin_espacio(conn):
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local role prisma_app")
            yield cur


# ===========================================================================
# Funciones puras: extracción, formato, saludo
# ===========================================================================


def test_extraer_correos_ninguno():
    assert ACF.extraer_correos("hola, ¿cómo va todo?") == []


def test_extraer_correos_uno_con_puntuacion_al_final():
    candidatos = ACF.extraer_correos("mi correo es juan.perez@empresa.com.")
    assert candidatos == ["juan.perez@empresa.com"]


def test_extraer_correos_dos_en_una_frase():
    candidatos = ACF.extraer_correos(
        "probá con juan@empresa.com o con juan.perez@otra.com, cualquiera")
    assert {c.lower() for c in candidatos} == {"juan@empresa.com", "juan.perez@otra.com"}


def test_extraer_correos_dedup_por_normalizado():
    candidatos = ACF.extraer_correos("Juan@Empresa.com y juan@empresa.com")
    assert len(candidatos) == 1


def test_formato_incompleto_sin_dominio_con_punto():
    assert ACF._formato_valido("juan@empresa") is False
    assert ACF._formato_valido("juan@empresa.com") is True


def test_saludo_por_hora_local():
    from zoneinfo import ZoneInfo

    zona = ZoneInfo("America/Argentina/Buenos_Aires")
    assert ACF.saludo_para(datetime(2028, 1, 1, 14, 0, tzinfo=timezone.utc), zona) \
        == "👋 Buen día"
    assert ACF.saludo_para(datetime(2028, 1, 1, 20, 0, tzinfo=timezone.utc), zona) \
        == "👋 Buenas tardes"
    assert ACF.saludo_para(datetime(2028, 1, 1, 4, 0, tzinfo=timezone.utc), zona) \
        == "👋 Buenas noches"


def test_cuerpo_de_verificacion_no_ofrece_responder_el_correo():
    """C7/ADR 0010: excluida la verificación por respuesta de correo."""
    cuerpo = ACF.cuerpo_verificacion("Marcos", "https://t.me/bot?start=pv_abc")
    assert "responder" not in cuerpo.lower()
    assert "24 horas" in cuerpo
    assert "https://t.me/bot?start=pv_abc" in cuerpo


# ===========================================================================
# A. Clave apagada: activación idéntica a hoy
# ===========================================================================


@pytest.fixture
def sin_activar(conn, tmp_path):
    import os

    import yaml
    from prisma.importador import importar
    from tests.conftest import RAIZ

    os.environ["PRISMA_BOT_TOKEN_COREWORK"] = "prueba:token"
    pack = yaml.safe_load((RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    pack["telegram"]["grupo_gestion_id"] = -1001
    pack["evidencia"]["estructura_drive"] = "drive://corework"
    for p in pack["personas"]:
        p["telegram_user_id"] = "PENDIENTE"
    ruta = tmp_path / "cw.yaml"
    ruta.write_text(yaml.safe_dump(pack, allow_unicode=True), "utf-8")
    r = importar(conn, ruta, activar=True)
    conn.commit()
    return r


@pytest.fixture
def cliente_corework(sin_activar, conn, monkeypatch):
    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, webhook_secret="s3cr3t"))
    monkeypatch.setattr(
        "prisma.llm.desde_base",
        lambda cur, ws, key: ProveedorGuionado([Respuesta(texto="Anotado.")]))
    monkeypatch.setattr(gateway, "_bot_username", lambda slug: "prisma_bot")
    return TestClient(gateway.app)


def _token_vigente(cur, ws, persona):
    from prisma.onboarding import generar_enlaces

    return generar_enlaces(cur, ws, "bot", solo=[persona],
                           ahora=datetime.now(timezone.utc))[0].token


def test_clave_apagada_activacion_igual_que_hoy(cliente_corework, conn, sin_activar):
    """Regresión: sin la clave, `/start {token}` se comporta byte a byte
    como antes de G1b -- la bienvenida vieja, sin ciclo de alta con
    correo."""
    ws = sin_activar.workspace_id
    with admin(conn) as cur:
        token = _token_vigente(cur, ws, "Marcos")
    conn.commit()

    resp = _post(cliente_corework, f"/start {token}", 555001, slug="corework")
    assert resp.status_code == 200

    textos = _outbox_textos(conn, 555001)
    assert len(textos) == 1
    assert "Listo, Marcos" in textos[0]
    assert "coordinadora digital" not in textos[0]

    with admin(conn) as cur:
        cur.execute(
            "select m.id from membership m join app_user u on u.id = m.app_user_id "
            "where m.workspace_id = %s and u.telegram_user_id = 555001", (ws,))
        m = str(cur.fetchone()["id"])
    fila = _estado(conn, ws, m)
    assert fila is None  # nunca se abrió ciclo de alta con correo


# ===========================================================================
# B. Clave encendida: bienvenida + pedido de correo del pack
# ===========================================================================


def test_activacion_con_clave_encendida_manda_bienvenida_y_pedido(
        cliente_corework, conn, sin_activar):
    ws = sin_activar.workspace_id
    _habilitar(conn, ws)
    with admin(conn) as cur:
        token = _token_vigente(cur, ws, "Nahuel")
    conn.commit()

    resp = _post(cliente_corework, f"/start {token}", 555002, slug="corework")
    assert resp.status_code == 200

    textos = _outbox_textos(conn, 555002)
    assert len(textos) == 2
    assert "coordinadora digital del equipo" in textos[0]
    assert "Nahuel" in textos[0]
    assert textos[0] != ACF.TEXTO_PEDIDO_CORREO
    assert textos[1] == ACF.TEXTO_PEDIDO_CORREO
    # La bienvenida VIEJA (con tareas abiertas) no se manda (C6).
    assert not any("Listo, Nahuel" in t for t in textos)

    with admin(conn) as cur:
        cur.execute(
            "select m.id from membership m join app_user u on u.id = m.app_user_id "
            "where m.workspace_id = %s and u.telegram_user_id = 555002", (ws,))
        m = str(cur.fetchone()["id"])
    fila = _estado(conn, ws, m)
    assert fila["estado"] == "awaiting_email"
    assert fila["modo"] == "alta"
    assert fila["bienvenida_entregada_en"] is not None


# ===========================================================================
# C. El control: nada de negocio corre para quien no verificó
# ===========================================================================


def test_gate_bloquea_el_turno_del_agente(cliente, conn, intake_world):
    """`_no_debe_llamarse` revienta si `_turno` (o `handle_active_text`, que
    también llega a rutear) se ejecuta -- confirma que el control interceptó
    antes de cualquier herramienta de negocio."""
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    _abrir_awaiting_email(conn, ws, m)

    resp = _post(cliente, "quiero crear una tarea nueva para mañana", 71001)
    assert resp.status_code == 200
    # Si `_no_debe_llamarse` se hubiera llamado, habría reventado dentro del
    # webhook y `procesar_update` lo habría atrapado como incidente -- en vez
    # de eso, el mensaje se atendió como "no reconocí un correo".
    textos = _outbox_textos(conn, 71001)
    assert textos[-1] == ACF.TEXTO_NO_RECONOCIDO


def test_sin_ciclo_abierto_el_turno_llega_al_agente(con_agente, conn, intake_world):
    """Sin clave (ni ciclo de alta con correo abierto), el turno sigue
    llegando al agente exactamente como hoy -- el control no interfiere."""
    _post(con_agente, "hola", 71001)

    assert _outbox_textos(conn, 71001)[-1] == "Anotado."


# ===========================================================================
# D. `awaiting_email`: A02, formato, dominio, correo en uso
# ===========================================================================


def test_dos_correos_ofrece_botones_sin_elegir_por_orden(cliente, conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    _abrir_awaiting_email(conn, ws, m)

    _post(cliente, "capaz taylor@empresa.com o taylor.quinn@empresa.com", 71001)

    textos = _outbox_textos(conn, 71001)
    assert textos[-1] == ACF.TEXTO_MULTIPLES_CORREOS
    fila = _estado(conn, ws, m)
    assert fila["estado"] == "awaiting_email"          # no eligió por orden
    assert _token_boton(conn, ws, m, "taylor@empresa.com")
    assert _token_boton(conn, ws, m, "taylor.quinn@empresa.com")


def test_ningun_correo_reconocido(cliente, conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    _abrir_awaiting_email(conn, ws, m)

    _post(cliente, "no tengo uno laboral todavía", 71001)

    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_NO_RECONOCIDO


def test_direccion_incompleta(cliente, conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    _abrir_awaiting_email(conn, ws, m)

    _post(cliente, "mi correo es taylor@empresa", 71001)

    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_DIRECCION_INCOMPLETA


def test_dominio_no_habilitado(cliente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    _abrir_awaiting_email(conn, ws, m)
    with admin(conn) as cur:
        cur.execute(
            "insert into workspace_setting (workspace_id, clave, valor) "
            "values (%s, 'correo_verificacion.dominios', '[\"empresa.com\"]')",
            (ws,))
    conn.commit()

    _post(cliente, "taylor@otraempresa.com", 71001)

    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_DOMINIO_NO_HABILITADO


def test_correo_ya_asociado_a_otro_integrante(cliente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m1 = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    m2 = _membership_id(intake_world, "north-lab", "Sam North")
    _habilitar(conn, ws)
    _abrir_awaiting_email(conn, ws, m1)
    _abrir_awaiting_email(conn, ws, m2)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)

    _post(cliente, "sam.north@empresa.com", 71002)  # Sam North lo verifica
    token_sam = _token_de_enlace(doble.enviados[-1].enlace)
    with espacio(conn, ws) as cur:
        reserva = AC.reservar_verificacion(cur, token_sam, m2, ahora=datetime.now(timezone.utc))
        assert reserva.ok
        completado = AC.completar_verificacion(cur, token_sam, m2, ahora=datetime.now(timezone.utc))
        assert completado.ok
    conn.commit()

    _post(cliente, "sam.north@empresa.com", 71001)  # Taylor intenta el mismo

    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_CORREO_EN_USO


# ===========================================================================
# E. Envío válido, falla de envío, emisor sin configurar
# ===========================================================================


def test_correo_valido_manda_por_el_doble_y_pasa_a_pending_verification(
        cliente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    _abrir_awaiting_email(conn, ws, m)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)

    _post(cliente, "taylor.quinn@empresa.com", 71001)

    assert len(doble.enviados) == 1
    envio = doble.enviados[0]
    assert envio.destinatario == "taylor.quinn@empresa.com"
    assert envio.asunto == ACF.ASUNTO_VERIFICACION
    assert "?start=pv_" in envio.enlace
    # `vence_en` sale del reloj real (`gate` no recibe un "ahora" de prueba),
    # no de la constante `AHORA`: se compara contra el reloj real, con
    # margen para lo que tarda la petición.
    ahora_real = datetime.now(timezone.utc)
    assert timedelta(hours=23, minutes=59) <= envio.vence_en - ahora_real \
        <= timedelta(hours=24)

    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_GRACIAS_ENVIADO
    fila = _estado(conn, ws, m)
    assert fila["estado"] == "pending_email_verification"


def test_falla_de_envio_no_deja_token_valido_ni_cambia_estado(
        cliente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    _abrir_awaiting_email(conn, ws, m)
    doble = DobleEnvioCorreo(falla=True)
    _sender(conn, ws, monkeypatch, doble)

    _post(cliente, "taylor.quinn@empresa.com", 71001)

    assert _outbox_textos(conn, 71001)[-1] == gateway.NOTICIA_NEUTRA_INCIDENTE
    fila = _estado(conn, ws, m)
    assert fila["estado"] == "awaiting_email"          # sin cambios
    assert _verificaciones(conn, m) == []               # ningún envío contado
    incidentes = _incidentes(conn, ws)
    assert any("envío del correo" in i["resumen_sanitizado"] for i in incidentes)
    for i in incidentes:
        assert "taylor.quinn@empresa.com" not in (i["resumen_sanitizado"] or "")
        assert "taylor.quinn@empresa.com" not in (i["referencia_cruda"] or "")


def test_sin_emisor_configurado_incidente_y_aviso_administrativo(
        cliente, conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    _abrir_awaiting_email(conn, ws, m)
    # No se parchea `obtener_emisor_configurado`: sigue devolviendo `None`.

    _post(cliente, "taylor.quinn@empresa.com", 71001)

    assert _outbox_textos(conn, 71001)[-1] == gateway.NOTICIA_NEUTRA_INCIDENTE
    fila = _estado(conn, ws, m)
    assert fila["estado"] == "awaiting_email"
    assert _verificaciones(conn, m) == []
    avisos = _avisos(conn, ws)
    assert any(a["tipo"] == "correo_sin_emisor" for a in avisos)
    for a in avisos:
        assert "taylor.quinn@empresa.com" not in a["texto_saneado"]


def test_ningun_correo_ni_token_en_incidentes_ni_avisos(
        cliente, conn, intake_world, monkeypatch):
    """Cobertura agregada de la regla de saneado sobre los dos caminos de
    falla anteriores."""
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    _abrir_awaiting_email(conn, ws, m)
    doble = DobleEnvioCorreo(falla=True)
    _sender(conn, ws, monkeypatch, doble)
    _post(cliente, "taylor.quinn@empresa.com", 71001)

    for fila in _incidentes(conn, ws) + _avisos(conn, ws):
        volcado = " ".join(str(v) for v in fila.values() if v)
        assert "@" not in volcado


# ===========================================================================
# F. `pending_email_verification`: recordatorio, cambiar/mantener, límites
# ===========================================================================


def _hasta_pending_verification(cliente, conn, ws, m, tg_user, doble):
    _abrir_awaiting_email(conn, ws, m)
    _post(cliente, "taylor.quinn@empresa.com", tg_user)
    return doble.enviados[-1]


def test_texto_libre_pendiente_ofrece_recordatorio_con_botones(
        cliente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _hasta_pending_verification(cliente, conn, ws, m, 71001, doble)

    _post(cliente, "¿todavía falta algo?", 71001)

    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_RECORDATORIO_PENDIENTE
    assert _token_boton(conn, ws, m, ACF.ETIQUETA_REENVIAR)
    assert _token_boton(conn, ws, m, ACF.ETIQUETA_CAMBIAR)


def test_correo_distinto_mientras_pendiente_propone_sin_cambiar_en_silencio(
        cliente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _hasta_pending_verification(cliente, conn, ws, m, 71001, doble)

    _post(cliente, "en realidad usá taylor.q@otradireccion.com", 71001)

    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_PROPONE_CAMBIO
    assert _token_boton(conn, ws, m, ACF.etiqueta_cambiar_a("taylor.q@otradireccion.com"))
    assert _token_boton(conn, ws, m, ACF.ETIQUETA_MANTENER)
    fila = _estado(conn, ws, m)
    assert fila["estado"] == "pending_email_verification"      # nada cambió todavía
    assert len(doble.enviados) == 1                             # ningún envío nuevo


def test_boton_mantener_no_cambia_nada(cliente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _hasta_pending_verification(cliente, conn, ws, m, 71001, doble)
    _post(cliente, "en realidad usá taylor.q@otradireccion.com", 71001)
    token = _token_boton(conn, ws, m, ACF.ETIQUETA_MANTENER)

    _post_toque(cliente, token, 71001)

    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_MANTENER_CONFIRMADO
    assert len(doble.enviados) == 1
    assert _estado(conn, ws, m)["estado"] == "pending_email_verification"


def test_boton_cambiar_a_pasa_por_awaiting_email_y_manda_al_correo_nuevo(
        cliente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _hasta_pending_verification(cliente, conn, ws, m, 71001, doble)
    _post(cliente, "en realidad usá taylor.q@otradireccion.com", 71001)
    token = _token_boton(conn, ws, m, ACF.etiqueta_cambiar_a("taylor.q@otradireccion.com"))

    _post_toque(cliente, token, 71001)

    assert len(doble.enviados) == 2
    assert doble.enviados[-1].destinatario == "taylor.q@otradireccion.com"
    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_GRACIAS_ENVIADO
    assert _estado(conn, ws, m)["estado"] == "pending_email_verification"


def test_boton_cambiar_correo_pide_de_nuevo(cliente, conn, intake_world, monkeypatch):
    """`Cambiar correo` del recordatorio (sin dirección todavía) vuelve a
    `awaiting_email` y repite el pedido."""
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _hasta_pending_verification(cliente, conn, ws, m, 71001, doble)
    _post(cliente, "cualquier cosa", 71001)
    token = _token_boton(conn, ws, m, ACF.ETIQUETA_CAMBIAR)

    _post_toque(cliente, token, 71001)

    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_PEDIDO_CORREO
    assert _estado(conn, ws, m)["estado"] == "awaiting_email"


def test_reenviar_respeta_el_limite_de_tres_por_hora(
        cliente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _hasta_pending_verification(cliente, conn, ws, m, 71001, doble)   # envío 1

    _reenviar(cliente, conn, ws, m, 71001)                             # envío 2
    _reenviar(cliente, conn, ws, m, 71001)                             # envío 3
    assert len(doble.enviados) == 3

    _reenviar(cliente, conn, ws, m, 71001)                             # rechazado
    assert len(doble.enviados) == 3
    assert "última hora" in _outbox_textos(conn, 71001)[-1]
    assert _estado(conn, ws, m)["estado"] == "pending_email_verification"


# ===========================================================================
# G. `/start pv_{token}`
# ===========================================================================


def test_verificacion_exitosa_y_vuelve_la_conversacion_normal(
        con_agente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _hasta_pending_verification(con_agente, conn, ws, m, 71001, doble)
    token = _token_de_enlace(doble.enviados[-1].enlace)

    resp = _post(con_agente, f"/start pv_{token}", 71001)
    assert resp.status_code == 200

    assert _outbox_textos(conn, 71001)[-1] == ACF.texto_verificado("Taylor")
    assert _estado(conn, ws, m)["estado"] == "active"
    contacto = None
    with espacio(conn, ws) as cur:
        contacto = AC.contacto_verificado(cur, m)
    assert contacto["email"] == "taylor.quinn@empresa.com"

    # Ya `active`: el mensaje siguiente llega al agente (`con_agente` no
    # revienta, y el texto de la firma del doble aparece).
    _post(con_agente, "qué tengo pendiente", 71001)
    assert _outbox_textos(conn, 71001)[-1] == "Anotado."


def test_enlace_vencido_ofrece_reenviar(cliente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _hasta_pending_verification(cliente, conn, ws, m, 71001, doble)
    token = _token_de_enlace(doble.enviados[-1].enlace)
    # `expira_en` sale del reloj real al emitirse; forzarlo al pasado (no a
    # la constante `AHORA`, que en este calendario de prueba es futura) es
    # lo único que hace falta para simular el vencimiento de las 24 horas
    # sin esperarlas. `prisma_admin` es el único rol con privilegio directo
    # sobre esta tabla (`alta_correo_verificacion` no concede nada a
    # `prisma_app`).
    vencido = datetime.now(timezone.utc) - timedelta(hours=1)
    with admin(conn) as cur:
        cur.execute("update alta_correo_verificacion set expira_en = %s "
                    "where membership_id = %s", (vencido, m))
    conn.commit()

    _post(cliente, f"/start pv_{token}", 71001)

    assert _token_boton(conn, ws, m, ACF.ETIQUETA_REENVIAR)
    assert _estado(conn, ws, m)["estado"] == "pending_email_verification"


def test_enlace_ya_usado_no_reactiva_nada(cliente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _hasta_pending_verification(cliente, conn, ws, m, 71001, doble)
    token = _token_de_enlace(doble.enviados[-1].enlace)
    _post(cliente, f"/start pv_{token}", 71001)
    assert _estado(conn, ws, m)["estado"] == "active"

    _post(cliente, f"/start pv_{token}", 71001)

    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_ENLACE_USADO
    assert _estado(conn, ws, m)["estado"] == "active"       # sigue activo


def test_enlace_de_otra_persona_no_revela_de_quien_es(
        cliente, conn, intake_world, monkeypatch):
    """A04: el enlace de Taylor, apretado por Sam North (otro integrante ya
    vinculado del mismo espacio) -- nunca dice de quién es."""
    ws = intake_world["north-lab"]["id"]
    m_taylor = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    m_sam = _membership_id(intake_world, "north-lab", "Sam North")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _hasta_pending_verification(cliente, conn, ws, m_taylor, 71001, doble)
    token = _token_de_enlace(doble.enviados[-1].enlace)

    _post(cliente, f"/start pv_{token}", 71002)   # Sam North (tg 71002)

    assert _outbox_textos(conn, 71002)[-1] == ACF.TEXTO_ENLACE_INVALIDO
    assert _estado(conn, ws, m_taylor)["estado"] == "pending_email_verification"
    assert _estado(conn, ws, m_sam) is None


def test_doble_toque_ocupado_no_revela_nada(cliente, conn, intake_world, monkeypatch):
    """A05: una reserva vigente (5 minutos) sobre el mismo token hace que el
    segundo intento reciba 'ocupado', no un resultado distinto."""
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _hasta_pending_verification(cliente, conn, ws, m, 71001, doble)
    token = _token_de_enlace(doble.enviados[-1].enlace)
    with _sin_espacio(conn) as cur:
        AC.reservar_verificacion(cur, token, m, ahora=datetime.now(timezone.utc))
    conn.commit()

    _post(cliente, f"/start pv_{token}", 71001)

    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_VERIFICACION_OCUPADA
    assert _estado(conn, ws, m)["estado"] == "pending_email_verification"


def test_remitente_desconocido_no_recibe_nada(cliente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _hasta_pending_verification(cliente, conn, ws, m, 71001, doble)
    token = _token_de_enlace(doble.enviados[-1].enlace)

    resp = _post(cliente, f"/start pv_{token}", 999999)

    assert resp.status_code == 200
    assert _outbox_textos(conn, 999999) == []
    assert _estado(conn, ws, m)["estado"] == "pending_email_verification"


# ===========================================================================
# H. Botones bindeados a la membresía
# ===========================================================================


def test_boton_apretado_por_otra_persona_no_hace_nada(
        cliente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    _abrir_awaiting_email(conn, ws, m)
    _post(cliente, "juan@empresa.com o juan.perez@empresa.com", 71001)
    token = _token_boton(conn, ws, m, "juan@empresa.com")

    # Sam North (71002) aprieta el botón que le corresponde a Taylor.
    _post_toque(cliente, token, 71002)

    assert _outbox_textos(conn, 71002)[-1] == "Eso se lo pregunté a otra persona del equipo."
    assert _estado(conn, ws, m)["estado"] == "awaiting_email"


def test_una_falla_al_resolver_el_bot_no_filtra_su_token(monkeypatch):
    """El error de `getMe` lleva la URL con el token del bot; ese texto
    termina en `incident.referencia_cruda`. Lo que sube tiene que estar
    saneado: nunca el token."""
    import types

    import httpx

    from prisma import gateway

    secreto = "123456:token-secreto-del-bot"
    monkeypatch.setattr(gateway, "config",
                        types.SimpleNamespace(token_bot=lambda slug: secreto))
    monkeypatch.setattr(gateway._bot_username, "_cache", {})

    def falla(url, **kwargs):
        pedido = httpx.Request("GET", url)
        raise httpx.HTTPStatusError(
            f"401 Unauthorized for url {url}", request=pedido,
            response=httpx.Response(401, request=pedido))

    monkeypatch.setattr(httpx, "get", falla)

    with pytest.raises(Exception) as info:
        gateway._bot_username("north-lab")
    assert secreto not in str(info.value)
    assert secreto not in repr(info.value)
    assert info.value.__cause__ is None


# ===========================================================================
# I. Endurecimiento G1b2 -- 1: la compuerta sólo actúa en chat privado
# ===========================================================================


def test_grupo_no_procesa_nada_de_un_integrante_gateado(cliente, conn, intake_world):
    """Un integrante en modo `alta` por debajo de `active` escribe en un
    grupo: no se le pide, muestra ni procesa ningún correo, y el mensaje
    tampoco llega a ninguna herramienta de negocio (todavía no está
    verificado). Nada en el grupo, nada en su privado, nunca un error."""
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    _abrir_awaiting_email(conn, ws, m)

    resp = _post_grupo(cliente, "taylor.quinn@empresa.com", 71001, chat_id=-5001)

    assert resp.status_code == 200
    assert _outbox_textos(conn, -5001) == []
    assert _outbox_textos(conn, 71001) == []
    assert _estado(conn, ws, m)["estado"] == "awaiting_email"      # sin cambios
    assert _verificaciones(conn, m) == []                          # nunca se emitió
    assert _incidentes(conn, ws) == []


def test_grupo_sigue_llegando_al_agente_para_quien_no_esta_gateado(
        con_agente, conn, intake_world):
    """Regresión: sin ningún ciclo de alta con correo abierto (el caso de
    hoy, o alguien ya `active`), un mensaje de grupo sigue llegando al
    agente exactamente como antes de este endurecimiento."""
    resp = _post_grupo(con_agente, "hola equipo", 71001, chat_id=-5001)

    assert resp.status_code == 200
    assert _outbox_textos(conn, -5001)[-1] == "Anotado."


# ===========================================================================
# J. Endurecimiento G1b2 -- 2 y 4: atomicidad de "Cambiar correo a X" y el
#    envío como último efecto
# ===========================================================================


def _hasta_propone_cambio(cliente, conn, ws, m, tg_user, doble):
    _hasta_pending_verification(cliente, conn, ws, m, tg_user, doble)
    _post(cliente, "en realidad usá taylor.q@otradireccion.com", tg_user)


def test_cambiar_a_con_correo_en_uso_no_deja_el_ciclo_en_awaiting_email(
        cliente, conn, intake_world, monkeypatch):
    """Si "Cambiar correo a X" se rechaza (X ya está asociado a otra
    persona), el ciclo tiene que quedar EXACTAMENTE como estaba --
    `pending_email_verification`, con la verificación anterior todavía
    vigente -- no varado en `awaiting_email`."""
    ws = intake_world["north-lab"]["id"]
    m1 = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    m2 = _membership_id(intake_world, "north-lab", "Sam North")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    # Sam North ya verificó la dirección que Taylor va a intentar "cambiar a".
    _abrir_awaiting_email(conn, ws, m2)
    _post(cliente, "sam.north@empresa.com", 71002)
    token_sam = _token_de_enlace(doble.enviados[-1].enlace)
    with espacio(conn, ws) as cur:
        AC.reservar_verificacion(cur, token_sam, m2, ahora=datetime.now(timezone.utc))
        AC.completar_verificacion(cur, token_sam, m2, ahora=datetime.now(timezone.utc))
    conn.commit()

    _hasta_pending_verification(cliente, conn, ws, m1, 71001, doble)
    envios_antes = len(doble.enviados)
    with espacio(conn, ws) as cur:
        vigente_antes_valor = AC.verificacion_vigente(cur, m1)

    _post(cliente, "en realidad usá sam.north@empresa.com", 71001)
    token_cambiar = _token_boton(conn, ws, m1, ACF.etiqueta_cambiar_a("sam.north@empresa.com"))
    assert token_cambiar

    _post_toque(cliente, token_cambiar, 71001)

    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_CORREO_EN_USO
    assert len(doble.enviados) == envios_antes            # ningún envío nuevo
    fila = _estado(conn, ws, m1)
    assert fila["estado"] == "pending_email_verification"  # nunca awaiting_email
    with espacio(conn, ws) as cur:
        assert AC.verificacion_vigente(cur, m1) == vigente_antes_valor  # sin tocar


def test_cambiar_a_sin_emisor_configurado_no_deja_el_ciclo_en_awaiting_email(
        cliente, conn, intake_world, monkeypatch):
    """Mismo invariante, pero por falta de emisor en vez de un rechazo
    tipado: tampoco puede quedar el ciclo en `awaiting_email`."""
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _hasta_propone_cambio(cliente, conn, ws, m, 71001, doble)
    token = _token_boton(conn, ws, m, ACF.etiqueta_cambiar_a("taylor.q@otradireccion.com"))
    assert token
    # A partir de ahora, sin emisor configurado (como si G2 no estuviera).
    monkeypatch.setattr(ACF, "obtener_emisor_configurado", lambda cur, workspace_id: None)

    _post_toque(cliente, token, 71001)

    assert _outbox_textos(conn, 71001)[-1] == gateway.NOTICIA_NEUTRA_INCIDENTE
    assert len(doble.enviados) == 1                        # sin envíos nuevos
    assert _estado(conn, ws, m)["estado"] == "pending_email_verification"


def test_cambiar_a_con_falla_de_envio_no_deja_el_ciclo_en_awaiting_email(
        cliente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _hasta_propone_cambio(cliente, conn, ws, m, 71001, doble)
    token = _token_boton(conn, ws, m, ACF.etiqueta_cambiar_a("taylor.q@otradireccion.com"))
    assert token
    doble.falla = True     # el envío de esta segunda dirección va a fallar

    _post_toque(cliente, token, 71001)

    assert _outbox_textos(conn, 71001)[-1] == gateway.NOTICIA_NEUTRA_INCIDENTE
    assert len(doble.enviados) == 1                         # el envío que falló no se contó
    assert _estado(conn, ws, m)["estado"] == "pending_email_verification"
    assert _verificaciones(conn, m)[-1]["email"] == "taylor.quinn@empresa.com"  # la anterior, intacta


def test_cambiar_a_respeta_el_limite_de_reenvios_sin_dejar_el_ciclo_varado(
        cliente, conn, intake_world, monkeypatch):
    """El rechazo por límite (3/hora) también es un motivo tipado -- el
    mismo invariante de arriba, con `verification_rate_limited`."""
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _hasta_pending_verification(cliente, conn, ws, m, 71001, doble)   # envío 1
    _reenviar(cliente, conn, ws, m, 71001)                             # envío 2
    _reenviar(cliente, conn, ws, m, 71001)                             # envío 3
    assert len(doble.enviados) == 3
    _post(cliente, "en realidad usá taylor.q@otradireccion.com", 71001)
    token = _token_boton(conn, ws, m, ACF.etiqueta_cambiar_a("taylor.q@otradireccion.com"))
    assert token

    _post_toque(cliente, token, 71001)                                 # 4to envío: rechazado

    assert len(doble.enviados) == 3
    assert "última hora" in _outbox_textos(conn, 71001)[-1]
    assert _estado(conn, ws, m)["estado"] == "pending_email_verification"


def test_transicion_falla_despues_del_envio_no_cuenta_el_envio_como_hecho(
        cliente, conn, intake_world, monkeypatch):
    """G1b2, ítem 4: si algo escrito en la base FALLA después de mandar el
    correo, ese envío no puede haber pasado -- el envío tiene que ser el
    último efecto dentro del savepoint. Se simula la falla de escritura
    (no la de red) parchando la transición que sigue al registro del envío;
    si el envío fuera anterior a esa escritura, el doble ya habría
    registrado el mensaje pese a que todo se revierte."""
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    _abrir_awaiting_email(conn, ws, m)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)

    original_transicionar = AC.transicionar

    def _transicionar_que_falla(cur, membership_id, estado_nuevo, **kwargs):
        if estado_nuevo == "pending_email_verification":
            raise RuntimeError("falla simulada de escritura")
        return original_transicionar(cur, membership_id, estado_nuevo, **kwargs)

    monkeypatch.setattr(AC, "transicionar", _transicionar_que_falla)

    _post(cliente, "taylor.quinn@empresa.com", 71001)

    assert doble.enviados == []                             # nunca se llegó a mandar
    assert _outbox_textos(conn, 71001)[-1] == gateway.NOTICIA_NEUTRA_INCIDENTE
    assert _estado(conn, ws, m)["estado"] == "awaiting_email"  # revertido entero
    assert _verificaciones(conn, m) == []


# ===========================================================================
# K. Endurecimiento G1b2 -- 3: los botones relean el estado antes de actuar
# ===========================================================================


def test_boton_elegir_correo_viejo_tras_otro_envio_no_hace_nada(
        cliente, conn, intake_world, monkeypatch):
    """Se ofrecen dos candidatos por botón (`awaiting_email`); antes de
    elegir, otro mensaje ya manda una dirección distinta y avanza el ciclo a
    `pending_email_verification`. El botón viejo de "elegir" queda gateado
    a `awaiting_email`: al apretarlo, no tiene que emitir nada ni cambiar
    el correo en verificación."""
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    _abrir_awaiting_email(conn, ws, m)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)

    _post(cliente, "capaz taylor@empresa.com o taylor.quinn@empresa.com", 71001)
    token_viejo = _token_boton(conn, ws, m, "taylor@empresa.com")
    assert token_viejo

    _post(cliente, "mejor taylor.quinn@empresa.com", 71001)   # avanza el ciclo
    assert _estado(conn, ws, m)["estado"] == "pending_email_verification"
    envios_antes = len(doble.enviados)

    _post_toque(cliente, token_viejo, 71001)

    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_ESTADO_CAMBIO
    assert len(doble.enviados) == envios_antes                 # nada nuevo
    assert _estado(conn, ws, m)["estado"] == "pending_email_verification"
    assert _incidentes(conn, ws) == []                          # nunca un incidente


def test_botones_de_recordatorio_viejos_tras_quedar_active_no_hacen_nada(
        con_agente, conn, intake_world, monkeypatch):
    """Reenviar/Cambiar del recordatorio, apretados después de que la
    persona ya quedó `active` por otro camino: no tienen que reactivar
    nada ni mandar un correo nuevo.

    Cada botón sale de un recordatorio DISTINTO (dos mensajes de texto
    libre separados, cada uno abre su propio `pending_action`): así, apretar
    el primero no deja "vencida" -- a nivel de `pendientes.resolver`, por la
    resolución del `pending_action` entero -- la pregunta por el segundo, y
    la prueba llega a ejercitar la relectura de estado de `resolver_toque`
    (G1b2, ítem 3) en vez de la vigencia genérica de un botón, que es un
    mecanismo distinto y anterior."""
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _hasta_pending_verification(con_agente, conn, ws, m, 71001, doble)
    _post(con_agente, "¿todavía falta algo?", 71001)
    token_reenviar = _token_boton(conn, ws, m, ACF.ETIQUETA_REENVIAR)
    assert token_reenviar
    _post(con_agente, "¿sigue pendiente?", 71001)
    token_cambiar = _token_boton(conn, ws, m, ACF.ETIQUETA_CAMBIAR)
    assert token_cambiar
    token_verificacion = _token_de_enlace(doble.enviados[-1].enlace)
    _post(con_agente, f"/start pv_{token_verificacion}", 71001)
    assert _estado(conn, ws, m)["estado"] == "active"
    envios_antes = len(doble.enviados)

    _post_toque(con_agente, token_reenviar, 71001)

    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_ESTADO_CAMBIO
    assert len(doble.enviados) == envios_antes
    assert _estado(conn, ws, m)["estado"] == "active"
    assert _incidentes(conn, ws) == []

    _post_toque(con_agente, token_cambiar, 71001)

    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_ESTADO_CAMBIO
    assert len(doble.enviados) == envios_antes
    assert _estado(conn, ws, m)["estado"] == "active"
    assert _incidentes(conn, ws) == []

    # Y ya `active`, el turno normal del agente sigue andando.
    _post(con_agente, "qué tengo pendiente", 71001)
    assert _outbox_textos(conn, 71001)[-1] == "Anotado."


def test_boton_cambiar_a_viejo_tras_quedar_active_no_hace_nada(
        cliente, conn, intake_world, monkeypatch):
    """"Cambiar correo a X" ofrecido durante `pending_email_verification`,
    apretado después de que la persona ya verificó (quedó `active`) por
    otra vía: sin efecto, sin incidente -- nunca intenta la transición
    imposible `active -> awaiting_email`, que antes de este endurecimiento
    llegaba cruda hasta el disparador de la base."""
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _hasta_propone_cambio(cliente, conn, ws, m, 71001, doble)
    token_cambiar = _token_boton(conn, ws, m, ACF.etiqueta_cambiar_a("taylor.q@otradireccion.com"))
    assert token_cambiar
    token_verificacion = _token_de_enlace(doble.enviados[-1].enlace)
    _post(cliente, f"/start pv_{token_verificacion}", 71001)
    assert _estado(conn, ws, m)["estado"] == "active"
    envios_antes = len(doble.enviados)

    _post_toque(cliente, token_cambiar, 71001)

    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_ESTADO_CAMBIO
    assert len(doble.enviados) == envios_antes
    assert _estado(conn, ws, m)["estado"] == "active"
    assert _incidentes(conn, ws) == []


# ===========================================================================
# L. Endurecimiento G1b2 -- 5: pruebas faltantes señaladas en la revisión
# ===========================================================================


def test_recuperacion_desde_pending_welcome_es_idempotente(conn, intake_world):
    """Si algo dejó el ciclo a mitad en `pending_welcome` y la recuperación
    se ejecuta dos veces (un reintento, dos llamadas concurrentes que
    ambas llegaron a leer `pending_welcome`), la segunda no tiene que
    duplicar ni el outbox ni el evento de bienvenida entregada -- y no
    puede reventar."""
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    with espacio(conn, ws) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
    conn.commit()

    with espacio(conn, ws) as cur:
        ACF._completar_bienvenida(cur, m, ws, 71001, "Taylor Quinn", AHORA)
        ACF._completar_bienvenida(cur, m, ws, 71001, "Taylor Quinn", AHORA)
    conn.commit()

    textos = _outbox_textos(conn, 71001)
    assert len(textos) == 2
    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from alta_correo_evento "
            "where membership_id = %s and tipo = 'bienvenida_entregada'", (m,))
        assert cur.fetchone()["n"] == 1
    assert _estado(conn, ws, m)["estado"] == "awaiting_email"


def test_dos_completar_bienvenida_concurrentes_no_revientan(conn, intake_world, uri):
    """G1d, seguimiento de la revisión de G1b2: dos mensajes simultáneos
    pueden llegar a leer `pending_welcome` los dos, antes de que ninguno
    haya escrito nada -- sin bloquear la proyección, el segundo termina
    reventando contra el índice único de `bienvenida_entregada`
    (`alta_correo_evento_bienvenida_unica`) en vez de ver la proyección ya
    avanzada y no hacer nada. No corrompe datos (`preparar_evento_alta_
    correo()` ya toma su propio `for update` antes de aplicar), pero es un
    incidente de más que bloquear la proyección al leer evita del todo."""
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    with espacio(conn, ws) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
    conn.commit()

    barrier = threading.Barrier(2, timeout=30)
    outcomes: list[str] = []
    failures: list[Exception] = []

    def completar() -> None:
        other = None
        try:
            other = conectar(uri)
            with espacio(other, ws) as cur:
                barrier.wait()
                ACF._completar_bienvenida(cur, m, ws, 71001, "Taylor Quinn", AHORA)
            other.commit()
            outcomes.append("ok")
        except Exception as exc:  # noqa: BLE001 -- justo lo que se prueba que no pase
            failures.append(exc)
            barrier.abort()
            other.rollback()
        finally:
            if other is not None:
                other.close()

    threads = [threading.Thread(target=completar) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)
    assert not any(thread.is_alive() for thread in threads), "un hilo quedó colgado"

    assert failures == [], [type(e).__name__ for e in failures]
    assert outcomes == ["ok", "ok"]

    textos = _outbox_textos(conn, 71001)
    assert len(textos) == 2
    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from alta_correo_evento "
            "where membership_id = %s and tipo = 'bienvenida_entregada'", (m,))
        assert cur.fetchone()["n"] == 1
    assert _estado(conn, ws, m)["estado"] == "awaiting_email"


def test_limite_de_cinco_por_ciclo_agota_y_crea_aviso_una_vez(
        conn, intake_world, monkeypatch):
    """El sexto intento de envío dentro del mismo ciclo (el límite cuenta el
    inicial) tiene que rechazarse con el texto de límite agotado y crear el
    aviso administrativo `correo_limite_agotado` exactamente una vez, incluso
    si se lo vuelve a golpear después."""
    from prisma.autoridad import identificar_en_espacio

    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    doble = DobleEnvioCorreo()
    monkeypatch.setattr(ACF, "obtener_emisor_configurado",
                        lambda cur, workspace_id: doble)
    with espacio(conn, ws) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
        AC.transicionar(cur, m, "awaiting_email", ahora=AHORA)
    conn.commit()

    # Espaciados más de una hora entre sí para no chocar con el límite de
    # 3/hora -- este intento es específicamente sobre el de 5/ciclo.
    for i in range(5):
        instante = AHORA + timedelta(hours=2 * i)
        with espacio(conn, ws) as cur:
            quien = identificar_en_espacio(cur, 71001, ws)
            ACF._emitir_y_enviar(
                cur, quien, "taylor.quinn@empresa.com", ws, 71001, instante,
                lambda: "prisma_bot", "Taylor", ACF.TEXTO_GRACIAS_ENVIADO)
        conn.commit()
    assert len(doble.enviados) == 5

    instante_6 = AHORA + timedelta(hours=2 * 5)
    with espacio(conn, ws) as cur:
        quien = identificar_en_espacio(cur, 71001, ws)
        ACF._emitir_y_enviar(
            cur, quien, "taylor.quinn@empresa.com", ws, 71001, instante_6,
            lambda: "prisma_bot", "Taylor", ACF.TEXTO_GRACIAS_ENVIADO)
    conn.commit()

    assert len(doble.enviados) == 5      # el sexto se rechazó, no se mandó
    assert _outbox_textos(conn, 71001)[-1] == \
        ACF._TEXTOS_MOTIVO_EMISION["verification_send_limit"]
    avisos = [a for a in _avisos(conn, ws) if a["tipo"] == "correo_limite_agotado"]
    assert len(avisos) == 1

    # Un séptimo golpe (mismo motivo) no crea un segundo aviso.
    instante_7 = AHORA + timedelta(hours=2 * 6)
    with espacio(conn, ws) as cur:
        quien = identificar_en_espacio(cur, 71001, ws)
        ACF._emitir_y_enviar(
            cur, quien, "taylor.quinn@empresa.com", ws, 71001, instante_7,
            lambda: "prisma_bot", "Taylor", ACF.TEXTO_GRACIAS_ENVIADO)
    conn.commit()
    avisos = [a for a in _avisos(conn, ws) if a["tipo"] == "correo_limite_agotado"]
    assert len(avisos) == 1


def test_nombre_vacio_no_revienta_y_saluda_sin_nombre():
    """Un `nombre` vacío o de sólo espacios no puede levantar `IndexError`
    (`"".split()[0]`) -- el pack admite saludar sin nombre cuando no hay
    ninguno disponible."""
    assert ACF._nombre_preferido("") == ""
    assert ACF._nombre_preferido("   ") == ""
    assert ACF._nombre_preferido("Taylor Quinn") == "Taylor"

    saludo = ACF.texto_bienvenida("👋 Buen día", ACF._nombre_preferido(""))
    assert "👋 Buen día. Soy Prisma" in saludo
    assert ", ." not in saludo
    assert ",." not in saludo

    verificado = ACF.texto_verificado(ACF._nombre_preferido("   "))
    assert verificado.startswith("✅ Gracias. Tu correo")

    cuerpo = ACF.cuerpo_verificacion(ACF._nombre_preferido(""), "https://t.me/bot?start=pv_x")
    assert cuerpo.startswith("Hola.\n\n")


def test_abrir_ciclo_con_nombre_vacio_no_revienta(conn, intake_world):
    """Mismo caso, a través del recorrido real de apertura del ciclo (donde
    antes del arreglo `nombre.split()[0]` reventaba con `IndexError`)."""
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")

    with espacio(conn, ws) as cur:
        ACF.abrir_ciclo_alta(cur, m, ws, 71001, "   ", AHORA)
    conn.commit()

    textos = _outbox_textos(conn, 71001)
    assert len(textos) == 2
    assert textos[0].startswith("👋")
    assert ", ." not in textos[0] and ",." not in textos[0]
    assert _estado(conn, ws, m)["estado"] == "awaiting_email"
