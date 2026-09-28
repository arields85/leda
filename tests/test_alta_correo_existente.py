"""Integrantes ya activos cuando se enciende la clave (rama auxiliar, G1c).

C5 (resuelta por el usuario, "Decisiones del usuario para G1"): a quien ya
estaba activo se le pide el correo una vez, SIN bloquearlo -- sigue
trabajando normal; sólo un mensaje que sea, de punta a punta, un correo
entra al recorrido de verificación. El comando `correo-verificacion` de
`cli.py` es lo que abre esos ciclos en modo `existente` al encender la
clave.

Reutiliza los dobles y fixtures de `test_alta_correo_flujo.py` (G1b/G1b2):
mismo mundo (`intake_world`), mismo doble de envío de correo, mismo cliente
de pruebas contra el webhook.
"""

from __future__ import annotations

from datetime import datetime

from prisma import alta_correo as AC
from prisma import alta_correo_flujo as ACF
from prisma import cli
from prisma.db import admin, espacio

from tests.test_alta_correo_flujo import (
    AHORA,
    DobleEnvioCorreo,
    _abrir_awaiting_email,
    _avisos,
    _estado,
    _habilitar,
    _membership_id,
    _outbox_textos,
    _post,
    _post_grupo,
    _sender,
    _token_de_enlace,
    cliente,
    con_agente,
)

# ---------------------------------------------------------------------------
# Helpers propios de este archivo
# ---------------------------------------------------------------------------


def _correo_verificacion(monkeypatch, conn, slug: str, *, activar: bool) -> int:
    """Corre `python -m prisma correo-verificacion <slug> --activar|
    --desactivar` contra la conexión de prueba, igual que `cliente`
    monkeypatchea `gateway._conn` para el webhook."""
    monkeypatch.setattr(cli, "conectar", lambda: conn)
    bandera = "--activar" if activar else "--desactivar"
    return cli.main(["correo-verificacion", slug, bandera])


def _abrir_existente(conn, ws: str, m: str, ahora: datetime = AHORA) -> None:
    """Deja a `m` directamente en modo `existente`/`awaiting_email`, como si
    el comando `--activar` ya hubiera corrido para esa membresía. No usa
    `ACF.abrir_ciclo_existente` a propósito -- ese camino completo lo
    ejercitan las pruebas del comando; acá sólo interesa el estado de
    partida para probar el control no bloqueante."""
    with espacio(conn, ws) as cur:
        AC.iniciar_ciclo(cur, m, "existente", ahora=ahora)
    conn.commit()


def _agregar_pendiente_de_activar(conn, ws: str, area_id: str, nombre: str) -> str:
    """Una membresía activa pero sin Telegram vinculado todavía -- el caso
    de quien recibió su enlace y no lo usó. No tiene que pasarle nada al
    encender la clave."""
    with admin(conn) as cur:
        cur.execute("select id from rol where workspace_id = %s and slug = 'member'", (ws,))
        rol_id = cur.fetchone()["id"]
        cur.execute("insert into app_user (nombre) values (%s) returning id", (nombre,))
        app_user_id = str(cur.fetchone()["id"])
        cur.execute(
            """insert into membership (workspace_id, app_user_id, area_id, rol_id)
               values (%s, %s, %s, %s) returning id""",
            (ws, app_user_id, area_id, rol_id))
        m = str(cur.fetchone()["id"])
    conn.commit()
    return m


def _audit_count(conn, ws: str, accion: str) -> int:
    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from audit_log where workspace_id = %s and accion = %s",
            (ws, accion))
        return cur.fetchone()["n"]


# ===========================================================================
# A. `_solo_un_correo` -- función pura
# ===========================================================================


def test_solo_un_correo_exacto():
    assert ACF._solo_un_correo("  taylor.quinn@empresa.com  ") == "taylor.quinn@empresa.com"


def test_solo_un_correo_ninguno_para_texto_vacio_o_sin_arroba():
    assert ACF._solo_un_correo("") is None
    assert ACF._solo_un_correo("   ") is None
    assert ACF._solo_un_correo("hola, todo bien") is None


def test_solo_un_correo_ninguno_si_hay_otras_palabras():
    assert ACF._solo_un_correo("mi correo es taylor.quinn@empresa.com, gracias") is None
    assert ACF._solo_un_correo("taylor.quinn@empresa.com y otra cosa") is None


# ===========================================================================
# B. CLI `correo-verificacion --activar`
# ===========================================================================


def test_activar_abre_ciclo_pide_correo_avisa_y_es_idempotente(
        conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    personas = intake_world["north-lab"]["people"]
    nombres = {p["name"] for p in personas.values()}
    telegrams = {p["telegram"] for p in personas.values()}

    codigo = _correo_verificacion(monkeypatch, conn, "north-lab", activar=True)
    assert codigo == 0

    with espacio(conn, ws) as cur:
        assert AC.habilitado(cur, ws) is True
        for p in personas.values():
            fila = AC.estado(cur, p["membership_id"])
            assert fila["modo"] == "existente"
            assert fila["estado"] == "awaiting_email"
            assert fila["ciclo"] == 1

    for tg in telegrams:
        assert _outbox_textos(conn, tg) == [ACF.TEXTO_PEDIDO_CORREO]

    avisos = [a for a in _avisos(conn, ws) if a["tipo"] == "correo_existente_pendientes"]
    assert len(avisos) == 1
    assert all(nombre in avisos[0]["texto_saneado"] for nombre in nombres)
    assert "@" not in avisos[0]["texto_saneado"]     # nunca correos, sólo nombres

    assert _audit_count(conn, ws, "correo_verificacion_activado") == 1

    # Segunda corrida: idempotente -- nada nuevo, para nadie.
    codigo2 = _correo_verificacion(monkeypatch, conn, "north-lab", activar=True)
    assert codigo2 == 0
    for tg in telegrams:
        assert _outbox_textos(conn, tg) == [ACF.TEXTO_PEDIDO_CORREO]
    with espacio(conn, ws) as cur:
        for p in personas.values():
            assert AC.estado(cur, p["membership_id"])["ciclo"] == 1
    avisos2 = [a for a in _avisos(conn, ws) if a["tipo"] == "correo_existente_pendientes"]
    assert len(avisos2) == 1


def test_activar_no_toca_a_quien_no_esta_activado_todavia(conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    area_id = intake_world["north-lab"]["areas"]["field"]
    m_pendiente = _agregar_pendiente_de_activar(conn, ws, area_id, "Pendiente Activar")

    _correo_verificacion(monkeypatch, conn, "north-lab", activar=True)

    with espacio(conn, ws) as cur:
        assert AC.estado(cur, m_pendiente) is None


def test_activar_no_toca_a_quien_ya_tiene_correo_verificado_aunque_su_ciclo_este_revocado(
        conn, intake_world, monkeypatch):
    """El correo verificado sobrevive a una revocación (queda en
    `alta_correo_contacto`); sin este chequeo aparte, la condición de "sin
    ciclo abierto" sola (cualquier proyección ausente o `revoked`) volvería
    a marcar a esta persona como elegible y le abriría un ciclo nuevo -- a
    pesar de que ya dio y verificó su correo antes."""
    from prisma.autoridad import identificar_en_espacio

    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    doble = DobleEnvioCorreo()
    monkeypatch.setattr(ACF, "obtener_emisor_configurado", lambda cur, workspace_id: doble)
    with espacio(conn, ws) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
        AC.transicionar(cur, m, "awaiting_email", ahora=AHORA)
        quien = identificar_en_espacio(cur, 71001, ws)
        ACF._emitir_y_enviar(cur, quien, "taylor.quinn@empresa.com", ws, 71001, AHORA,
                             lambda: "prisma_bot", "Taylor", ACF.TEXTO_GRACIAS_ENVIADO)
    conn.commit()
    token = _token_de_enlace(doble.enviados[-1].enlace)
    with espacio(conn, ws) as cur:
        AC.reservar_verificacion(cur, token, m, ahora=AHORA)
        AC.completar_verificacion(cur, token, m, ahora=AHORA)
        AC.transicionar(cur, m, "revoked", ahora=AHORA)
    conn.commit()
    with espacio(conn, ws) as cur:
        assert AC.contacto_verificado(cur, m) is not None
        assert AC.estado(cur, m)["estado"] == "revoked"

    _correo_verificacion(monkeypatch, conn, "north-lab", activar=True)

    with espacio(conn, ws) as cur:
        fila = AC.estado(cur, m)
        assert fila["estado"] == "revoked"    # nunca se le abrió un ciclo nuevo
        assert fila["ciclo"] == 1
    # Nada nuevo encolado para esta membresía -- sólo lo que ya había del
    # camino `alta` de arriba.
    assert _outbox_textos(conn, 71001) == [ACF.TEXTO_GRACIAS_ENVIADO]


def test_activar_no_toca_a_quien_ya_tiene_un_ciclo_abierto(conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _abrir_existente(conn, ws, m, ahora=AHORA)

    _correo_verificacion(monkeypatch, conn, "north-lab", activar=True)

    with espacio(conn, ws) as cur:
        fila = AC.estado(cur, m)
        assert fila["ciclo"] == 1
        assert fila["estado"] == "awaiting_email"
    assert _outbox_textos(conn, 71001) == []    # el pedido de _abrir_existente no pasó por outbox


# ===========================================================================
# C. CLI `correo-verificacion --desactivar`
# ===========================================================================


def test_desactivar_apaga_la_clave_y_deja_de_interceptar_a_alta_y_existente(
        con_agente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m_alta = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    m_existente = _membership_id(intake_world, "north-lab", "Sam North")
    _habilitar(conn, ws)
    _abrir_awaiting_email(conn, ws, m_alta)
    _abrir_existente(conn, ws, m_existente)

    codigo = _correo_verificacion(monkeypatch, conn, "north-lab", activar=False)
    assert codigo == 0
    with espacio(conn, ws) as cur:
        assert AC.habilitado(cur, ws) is False

    _post(con_agente, "hola, sigo con mis tareas", 71001)     # gateado en `alta`
    _post(con_agente, "hola desde el otro lado", 71002)        # `existente`

    assert _outbox_textos(conn, 71001)[-1] == "Anotado."
    assert _outbox_textos(conn, 71002)[-1] == "Anotado."
    # Los ciclos y datos quedan como estaban -- apagar la clave no los borra.
    assert _estado(conn, ws, m_alta)["estado"] == "awaiting_email"
    assert _estado(conn, ws, m_existente)["estado"] == "awaiting_email"
    assert _audit_count(conn, ws, "correo_verificacion_desactivado") == 1


# ===========================================================================
# D. Modo `existente`: no bloqueante (C5)
# ===========================================================================


def test_existente_mensaje_normal_llega_al_agente(con_agente, conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    _abrir_existente(conn, ws, m)

    _post(con_agente, "hola, todo bien por aquí", 71001)

    assert _outbox_textos(conn, 71001)[-1] == "Anotado."
    assert _estado(conn, ws, m)["estado"] == "awaiting_email"    # nada bloqueado, nada cambiado


def test_existente_correo_exacto_entra_al_flujo_y_manda_uno(
        cliente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _abrir_existente(conn, ws, m)

    _post(cliente, "taylor.quinn@empresa.com", 71001)

    assert len(doble.enviados) == 1
    assert doble.enviados[0].destinatario == "taylor.quinn@empresa.com"
    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_GRACIAS_ENVIADO
    assert _estado(conn, ws, m)["estado"] == "pending_email_verification"


def test_existente_correo_entre_otras_palabras_va_al_agente(
        con_agente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _abrir_existente(conn, ws, m)

    _post(con_agente, "mi correo es taylor.quinn@empresa.com por si hace falta", 71001)

    assert _outbox_textos(conn, 71001)[-1] == "Anotado."
    assert doble.enviados == []
    assert _estado(conn, ws, m)["estado"] == "awaiting_email"    # nunca se emitió nada


def test_existente_verificacion_exitosa_muestra_variante_sin_bloqueo(
        con_agente, conn, intake_world, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _abrir_existente(conn, ws, m)
    _post(con_agente, "taylor.quinn@empresa.com", 71001)
    token = _token_de_enlace(doble.enviados[-1].enlace)

    resp = _post(con_agente, f"/start pv_{token}", 71001)
    assert resp.status_code == 200

    texto = _outbox_textos(conn, 71001)[-1]
    assert texto == ACF.texto_verificado_existente("Taylor")
    assert "conversar conmigo normalmente" not in texto
    assert _estado(conn, ws, m)["estado"] == "active"


def test_existente_grupo_no_cambia_nada(con_agente, conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    _abrir_existente(conn, ws, m)

    resp = _post_grupo(con_agente, "taylor.quinn@empresa.com", 71001, chat_id=-5001)

    assert resp.status_code == 200
    assert _outbox_textos(conn, -5001)[-1] == "Anotado."
    assert _outbox_textos(conn, 71001) == []
    assert _estado(conn, ws, m)["estado"] == "awaiting_email"    # nunca se procesó el correo


# ===========================================================================
# E. Regresión -- modo `alta` sin cambios
# ===========================================================================


def test_alta_sigue_bloqueando_igual_que_antes(cliente, conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    _abrir_awaiting_email(conn, ws, m)

    _post(cliente, "quiero crear una tarea nueva", 71001)

    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_NO_RECONOCIDO
    assert _estado(conn, ws, m)["estado"] == "awaiting_email"
