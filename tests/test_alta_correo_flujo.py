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
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from prisma import alta_correo as AC
from prisma import alta_correo_flujo as ACF
from prisma import gateway
from prisma.db import admin, espacio
from prisma.llm import ProveedorGuionado, Respuesta

# UTC 14:00 -> America/Argentina/Buenos_Aires 11:00 -> "Buen día" (5-12).
AHORA = datetime(2028, 3, 15, 14, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Doble del puerto de correo
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class EnvioRegistrado:
    destinatario: str
    asunto: str
    cuerpo: str
    nombre_preferido: str
    enlace: str
    vence_en: datetime


class DobleEnvioCorreo:
    """Registra cada envío; puede fallar a pedido -- nunca manda nada real."""

    def __init__(self, falla: bool = False):
        self.enviados: list[EnvioRegistrado] = []
        self.falla = falla

    def enviar_verificacion(self, *, destinatario, asunto, cuerpo, nombre_preferido,
                            enlace, vence_en):
        if self.falla:
            raise ConnectionError("el doble está configurado para fallar")
        self.enviados.append(EnvioRegistrado(
            destinatario, asunto, cuerpo, nombre_preferido, enlace, vence_en))
        return ACF.Recibo(message_id="doble-msg", thread_id="doble-thread")


def _token_de_enlace(enlace: str) -> str:
    return enlace.rsplit("pv_", 1)[1]


# ---------------------------------------------------------------------------
# Fixtures y helpers -- mundo ligero (`intake_world`, gente ya vinculada)
# ---------------------------------------------------------------------------


def _no_debe_llamarse(*_args, **_kwargs):
    raise AssertionError("no debía llamarse al proveedor de LLM: el control "
                         "de alta con correo tiene que interceptar antes")


@pytest.fixture
def cliente(intake_world, conn, monkeypatch):
    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, webhook_secret="s3cr3t"))
    monkeypatch.setattr("prisma.llm.desde_base", _no_debe_llamarse)
    monkeypatch.setattr(gateway, "_bot_username", lambda slug: "prisma_bot")
    # Sólo lo necesita el camino que SÍ llega a `_turno` (mantiene el
    # indicador de "escribiendo" con el token del bot): las pruebas del
    # control de alta con correo nunca deberían llegar hasta ahí, pero
    # `test_sin_ciclo_abierto_el_turno_llega_al_agente` sí, a propósito.
    monkeypatch.setenv("PRISMA_BOT_TOKEN_NORTH-LAB", "prueba:token")
    return TestClient(gateway.app)


@pytest.fixture
def con_agente(cliente, monkeypatch):
    """Variante donde SÍ hay un agente conversacional detrás -- para probar
    que, una vez `active`, la conversación de negocio vuelve a llegar."""
    monkeypatch.setattr(
        "prisma.llm.desde_base",
        lambda cur, ws, key: ProveedorGuionado([Respuesta(texto="Anotado.")]))
    return cliente


def _habilitar(conn, ws: str) -> None:
    with admin(conn) as cur:
        cur.execute(
            "insert into workspace_setting (workspace_id, clave, valor) "
            "values (%s, %s, 'true')", (ws, AC.CLAVE_HABILITADO))
    conn.commit()


def _sender(conn, ws: str, monkeypatch, doble: DobleEnvioCorreo | None) -> None:
    monkeypatch.setattr(ACF, "obtener_emisor_configurado",
                        lambda cur, workspace_id: doble)


def _post(cliente, texto, user_id, slug="north-lab"):
    return cliente.post(
        f"/telegram/{slug}",
        json={"message": {"message_id": 1, "text": texto,
                          "chat": {"id": user_id}, "from": {"id": user_id}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _post_toque(cliente, token, user_id, slug="north-lab"):
    return cliente.post(
        f"/telegram/{slug}",
        json={"callback_query": {"id": "cb1", "data": f"p:{token}",
                                 "from": {"id": user_id},
                                 "message": {"chat": {"id": user_id}}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _membership_id(intake_world, workspace_key: str, persona: str) -> str:
    return intake_world[workspace_key]["people"][persona]["membership_id"]


def _abrir_awaiting_email(conn, ws: str, m: str, ahora=AHORA) -> None:
    with espacio(conn, ws) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=ahora)
        AC.transicionar(cur, m, "awaiting_email", ahora=ahora)
    conn.commit()


def _estado(conn, ws: str, m: str) -> dict | None:
    with espacio(conn, ws) as cur:
        return AC.estado(cur, m)


def _outbox_textos(conn, chat_id: int) -> list[str]:
    with admin(conn) as cur:
        cur.execute(
            "select cuerpo from message_outbox where chat_id = %s "
            "order by programado_para, id", (chat_id,))
        return [f["cuerpo"] for f in cur.fetchall()]


def _token_boton(conn, ws: str, m: str, etiqueta: str) -> str | None:
    with admin(conn) as cur:
        cur.execute(
            """select o.token from pending_action_option o
                 join pending_action p on p.id = o.pending_action_id
                where p.workspace_id = %s and p.membership_id = %s
                  and o.etiqueta = %s and o.activa and p.estado = 'esperando'
                order by p.creado_en desc limit 1""",
            (ws, m, etiqueta))
        fila = cur.fetchone()
        return fila["token"] if fila else None


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


def _avisos(conn, ws: str) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(
            "select tipo, texto_saneado from aviso_administrativo "
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
