"""Integrantes ya activos cuando se enciende la clave (rama auxiliar, G1c).

C5 (resuelta por el usuario, "Decisiones del usuario para G1"): a quien ya
estaba activo se le pide el correo una vez, SIN bloquearlo -- sigue
trabajando normal; sólo un mensaje que sea, de punta a punta, un correo
entra al recorrido de verificación. El comando `correo-verificacion` de
`cli.py` es lo que abre esos ciclos en modo `existente` al encender la
clave.

Reutiliza los dobles y fixtures de `tests/alta_correo_ayudas.py` (compartidos
con `test_alta_correo_flujo.py`, G1b/G1b2): mismo mundo (`intake_world`),
mismo doble de envío de correo, mismo cliente de pruebas contra el webhook.
"""

from __future__ import annotations

import threading
from datetime import datetime

from prisma import alta_correo as AC
from prisma import alta_correo_flujo as ACF
from prisma import cli
from prisma.db import admin, conectar, espacio

from tests.alta_correo_ayudas import (
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
    _token_boton,
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


def test_solo_un_correo_rechaza_url_con_arroba():
    """G1c2, ítem 2: una URL con credenciales tiene un único `@`, pero no
    es "exactamente una dirección de correo" -- el `.` esperando el nombre
    de usuario en la parte local no puede llevar `://`."""
    assert ACF._solo_un_correo("http://taylor@empresa.com") is None
    assert ACF._solo_un_correo("https://taylor.quinn@empresa.com/ruta") is None


def test_solo_un_correo_rechaza_host_con_puerto_o_ruta():
    assert ACF._solo_un_correo("taylor@empresa.com:8080") is None
    assert ACF._solo_un_correo("taylor@empresa.com/ruta") is None


def test_solo_un_correo_rechaza_dos_arrobas():
    assert ACF._solo_un_correo("taylor@empresa.com@otra.com") is None


def test_solo_un_correo_rechaza_puntuacion_final():
    assert ACF._solo_un_correo("taylor.quinn@empresa.com.") is None
    assert ACF._solo_un_correo("taylor.quinn@empresa.com,") is None
    assert ACF._solo_un_correo("taylor.quinn@empresa.com!") is None


def test_solo_un_correo_rechaza_puntos_invalidos_en_parte_local():
    """G1d, seguimiento de la revisión de G1c2: la parte local estricta
    aceptaba un `.` al inicio, al final o dos seguidos -- formas que RFC
    5321 no admite y que un correo real nunca tiene."""
    assert ACF._solo_un_correo(".taylor@empresa.com") is None
    assert ACF._solo_un_correo("taylor.@empresa.com") is None
    assert ACF._solo_un_correo("taylor..quinn@empresa.com") is None


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


def test_activar_reabre_ciclo_revocado_sin_verificar_y_pide_de_nuevo(
        conn, intake_world, monkeypatch):
    """G1c2, ítem 1: la clave de dedupe del pedido de correo tiene que
    incluir el ciclo. Sin eso, un ciclo `existente` revocado antes de
    verificar (nunca llegó a crear `alta_correo_contacto`, así que la
    elegibilidad vuelve a contarlo) abre el ciclo 2 en la próxima
    `--activar`, pero el pedido nuevo se deduplica en silencio contra la
    clave del ciclo 1 y nunca sale -- una falla silenciosa."""
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")

    codigo1 = _correo_verificacion(monkeypatch, conn, "north-lab", activar=True)
    assert codigo1 == 0
    with espacio(conn, ws) as cur:
        assert AC.estado(cur, m)["ciclo"] == 1
    assert _outbox_textos(conn, 71001) == [ACF.TEXTO_PEDIDO_CORREO]

    # El ciclo 1 se revoca sin haber verificado nunca (nunca se llamó
    # `completar_verificacion`, así que jamás se creó
    # `alta_correo_contacto`) -- transiciones directas, mismo mecanismo que
    # usa `test_alta_correo.py` para probar el grafo de estados.
    with espacio(conn, ws) as cur:
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.transicionar(cur, m, "active", ahora=AHORA)
        AC.transicionar(cur, m, "revoked", ahora=AHORA)
    conn.commit()

    codigo2 = _correo_verificacion(monkeypatch, conn, "north-lab", activar=True)
    assert codigo2 == 0

    with espacio(conn, ws) as cur:
        fila = AC.estado(cur, m)
        assert fila["ciclo"] == 2
        assert fila["estado"] == "awaiting_email"
        assert fila["modo"] == "existente"
    # El pedido del ciclo 2 tiene que salir aparte -- nunca deduplicado
    # contra la clave del ciclo 1.
    assert _outbox_textos(conn, 71001) == \
        [ACF.TEXTO_PEDIDO_CORREO, ACF.TEXTO_PEDIDO_CORREO]


# ===========================================================================
# B2. G1c2, ítem 4: filtro explícito por espacio y bloqueo de corridas
#     superpuestas de `--activar`
# ===========================================================================


def test_elegibles_existente_nunca_devuelve_datos_de_otro_espacio_bajo_admin(
        conn, intake_world):
    """Bajo `admin()` (bypassa RLS), la vista `integrante` ya está acotada a
    la sesión: si el filtro de esta consulta dependiera sólo de eso y no
    del parámetro explícito `workspace_id` (mismo motivo que ya exige
    `habilitado()`, G1a2), pedir north-lab mientras la sesión quedó en
    west-studio devolvería el elenco de west-studio, mal etiquetado como
    si fuera la respuesta de north-lab.

    Seguimiento de la revisión de G1c2: para que probar que eso no pasa
    tenga sentido, primero hay que confirmar que west-studio de verdad
    tiene su propio elenco elegible no vacío -- si no lo tuviera, la lista
    vacía de abajo no probaría el filtro, sólo que no había nada para
    filtrar."""
    ws_a = intake_world["north-lab"]["id"]
    ws_b = intake_world["west-studio"]["id"]

    with admin(conn) as cur:
        cur.execute("select set_config('prisma.workspace_id', %s, true)", (ws_b,))
        filas_b = AC.elegibles_existente(cur, ws_b)
        assert filas_b, "west-studio tiene que tener su propio elenco elegible"

        filas = AC.elegibles_existente(cur, ws_a)

    assert filas == []


def test_elegibles_existente_devuelve_los_del_espacio_pedido(conn, intake_world):
    ws_a = intake_world["north-lab"]["id"]

    with admin(conn) as cur:
        cur.execute("select set_config('prisma.workspace_id', %s, true)", (ws_a,))
        filas = AC.elegibles_existente(cur, ws_a)

    nombres = {f["nombre"] for f in filas}
    assert nombres == {p["name"] for p in intake_world["north-lab"]["people"].values()}


def test_activar_toma_un_bloqueo_por_espacio_para_corridas_superpuestas(
        conn, intake_world, uri, monkeypatch):
    """G1c2, ítem 4: dos `--activar` superpuestas para el mismo espacio no
    pueden abrir ciclos ni encolar pedidos duplicados. Se prueba que la
    corrida real toma un bloqueo consultivo de transacción, con clave en el
    espacio (mismo patrón que `ingreso_tareas.handle_active_text`) --
    mientras lo tiene tomado y sin confirmar, otra conexión que lo pida sin
    esperar (`pg_try_advisory_xact_lock`) tiene que fallar."""
    ws = intake_world["north-lab"]["id"]
    conn.commit()
    clave = f"correo-verificacion:activar:{ws}"

    tomado = threading.Event()
    seguir = threading.Event()
    original = AC.elegibles_existente

    def _pausa(cur, workspace_id):
        tomado.set()
        assert seguir.wait(timeout=5), "nunca llegó la señal de continuar"
        return original(cur, workspace_id)

    monkeypatch.setattr(AC, "elegibles_existente", _pausa)

    conexion_hilo = conectar(uri)
    monkeypatch.setattr(cli, "conectar", lambda: conexion_hilo)

    # G1d, seguimiento de la revisión de G1c2: sin capturar el código de
    # salida de la corrida de fondo, esta prueba podía pasar aunque
    # `cli.main` reventara adentro del hilo -- `threading.Thread` traga la
    # excepción y sólo la imprime, `hilo.join()` no la propaga.
    resultado_hilo: list[int] = []

    def _correr_de_fondo() -> None:
        resultado_hilo.append(
            cli.main(["correo-verificacion", "north-lab", "--activar"]))

    hilo = threading.Thread(target=_correr_de_fondo)
    hilo.start()
    try:
        assert tomado.wait(timeout=5), "la corrida de fondo nunca tomó el bloqueo"

        segunda = conectar(uri)
        try:
            with espacio(segunda, ws) as cur2:
                cur2.execute(
                    "select pg_try_advisory_xact_lock(hashtextextended(%s, 0)) ok",
                    (clave,))
                assert cur2.fetchone()["ok"] is False
            segunda.rollback()
        finally:
            segunda.close()
    finally:
        seguir.set()
        hilo.join(timeout=5)
        assert not hilo.is_alive(), "la corrida de fondo no terminó"
        conexion_hilo.close()

    assert resultado_hilo == [0], "la corrida de fondo tiene que terminar en éxito"

    # La corrida de fondo tiene que haber hecho el trabajo real, no sólo
    # devuelto 0 sin tocar nada: los ciclos `existente` quedaron abiertos y
    # el pedido de correo, encolado, para el elenco elegible de north-lab.
    elegibles = {p["name"]: p for p in intake_world["north-lab"]["people"].values()}
    for persona in elegibles.values():
        estado = _estado(conn, ws, persona["membership_id"])
        assert estado is not None, f"no se abrió ciclo para {persona['name']}"
        assert estado["modo"] == "existente"
        assert estado["estado"] == "awaiting_email"
        assert _outbox_textos(conn, persona["telegram"]) == [ACF.TEXTO_PEDIDO_CORREO]

    # Liberado (la corrida terminó y confirmó): una tercera conexión puede
    # tomarlo sin esperar.
    tercera = conectar(uri)
    try:
        with espacio(tercera, ws) as cur3:
            cur3.execute(
                "select pg_try_advisory_xact_lock(hashtextextended(%s, 0)) ok", (clave,))
            assert cur3.fetchone()["ok"] is True
        tercera.rollback()
    finally:
        tercera.close()


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


def test_existente_pending_verification_mismo_correo_va_al_agente_sin_recordatorio(
        con_agente, conn, intake_world, monkeypatch):
    """G1c2, ítem 3(a): en `pending_email_verification`, el mismo correo que
    ya está vigente no es una instrucción nueva -- pasa de largo hacia el
    agente, nunca un recordatorio con botones (a diferencia del modo
    `alta`, donde cualquier texto libre en ese estado sí lo ofrece)."""
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _abrir_existente(conn, ws, m)
    _post(con_agente, "taylor.quinn@empresa.com", 71001)
    assert _estado(conn, ws, m)["estado"] == "pending_email_verification"

    _post(con_agente, "taylor.quinn@empresa.com", 71001)

    assert _outbox_textos(conn, 71001)[-1] == "Anotado."
    assert len(doble.enviados) == 1                         # sin reenvío
    assert _estado(conn, ws, m)["estado"] == "pending_email_verification"


def test_existente_pending_verification_correo_distinto_propone_cambio(
        con_agente, conn, intake_world, monkeypatch):
    """G1c2, ítem 3(a): una dirección distinta a la vigente sí es una
    instrucción nueva -- la propuesta de cambio (`Cambiar correo a X` /
    `Mantener correo anterior`), igual que en modo `alta`."""
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    doble = DobleEnvioCorreo()
    _sender(conn, ws, monkeypatch, doble)
    _abrir_existente(conn, ws, m)
    _post(con_agente, "taylor.quinn@empresa.com", 71001)
    assert _estado(conn, ws, m)["estado"] == "pending_email_verification"

    _post(con_agente, "taylor.q@otradireccion.com", 71001)

    assert _outbox_textos(conn, 71001)[-1] == ACF.TEXTO_PROPONE_CAMBIO
    assert _token_boton(conn, ws, m, ACF.etiqueta_cambiar_a("taylor.q@otradireccion.com"))
    assert len(doble.enviados) == 1                         # ningún envío nuevo todavía
    assert _estado(conn, ws, m)["estado"] == "pending_email_verification"


def test_desactivar_deja_de_bloquear_en_grupo_a_mitad_del_alta(
        con_agente, conn, intake_world, monkeypatch):
    """G1c2, ítem 3(b): con la clave apagada, un integrante a mitad del
    `alta` deja de estar bloqueado también en un chat de GRUPO -- su
    mensaje llega a procesamiento normal (regresión: `bloqueada_para_negocio`
    ya comprueba la clave, este es el caso que faltaba probar)."""
    ws = intake_world["north-lab"]["id"]
    m = _membership_id(intake_world, "north-lab", "Taylor Quinn")
    _habilitar(conn, ws)
    _abrir_awaiting_email(conn, ws, m)

    codigo = _correo_verificacion(monkeypatch, conn, "north-lab", activar=False)
    assert codigo == 0

    resp = _post_grupo(con_agente, "hola equipo", 71001, chat_id=-5001)

    assert resp.status_code == 200
    assert _outbox_textos(conn, -5001)[-1] == "Anotado."
    assert _estado(conn, ws, m)["estado"] == "awaiting_email"      # ciclo intacto, sin tocar


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
