"""La respuesta del bot de administración sale por la cola (`admin_notice`), y el enlace se emite
al mandarla (porción 5 de la C-3, su `PENDIENTE`; la corrección chica; migración 0054).

Hasta acá la respuesta al pedido `/enlace` salía directo, sin cola, porque la cola guarda el texto
y el token en claro no puede quedar en la base (ADR 0019, 7a). Ahora, como el enlace de una
persona del equipo (`message_outbox_enlace`), la respuesta queda en la cola sin el enlace, con una
marca de qué tarea y para qué administrador (`admin_notice_enlace`), y el despachador emite el
acceso recién al mandarla, dentro del punto de retorno del envío:

- **la base guarda sólo el hash**, nunca el token: ni en la cola, ni en la marca;
- **si el envío falla, no queda ningún acceso** (el punto de retorno se deshace) y queda un
  incidente; se reintenta como todo aviso a la administración, y al salir se emite uno solo;
- **el rol se revalida al mandarla**: si quien lo pidió dejó de ser administrador, no sale ningún
  enlace, la respuesta se descarta y queda un incidente;
- **la aplicación no llega a la cola ni a la marca** (sólo la conexión administrativa), y una
  fila de la cola es un incidente o una respuesta, nunca otra cosa;
- lo de la porción 5 sigue: la emisión auditada, sólo en un chat privado, una respuesta por
  pedido aunque Telegram lo entregue dos veces.
"""

from __future__ import annotations

import dataclasses
import hashlib

import psycopg
import pytest

from leda import config as config_mod
from leda.db import admin
from leda.despachador import TransporteDePrueba, despachar_avisos_admin
from leda.motor.administracion import atender_admin

from tests.garantias.test_pagina_de_la_tarea import mundo  # noqa: F401 -- la fixture
from tests.motor.ayudantes import mensaje_de_telegram

DIRECCION = "https://leda.invalid/"
ADA = 79001


@pytest.fixture
def ada(conn, mundo, monkeypatch) -> str:
    """Ada, administradora de plataforma, sin membresía; la página tiene su dirección."""
    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url=DIRECCION))
    with admin(conn) as cur:
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (%s, 'Ada Admin') returning id""", (ADA,))
        usuario = str(cur.fetchone()["id"])
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                    (usuario,))
    conn.commit()
    return usuario


def _pedir(conn, salida: TransporteDePrueba, update_id: int = 1,
           texto: str = "/enlace north-lab balanza") -> None:
    atender_admin(conn, mensaje_de_telegram(update_id, texto, ADA), salida,
                  imprimir=lambda *_: None)


def _filas(conn, sql: str, *args) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(sql, args)
        filas = cur.fetchall()
    conn.commit()
    return filas


def _accesos(conn) -> list[dict]:
    return _filas(conn, "select * from acceso_tarea where admin_app_user_id is not null")


def _respuestas(conn) -> list[dict]:
    return _filas(conn, "select * from admin_notice where es_respuesta order by id")


def _despachar(conn, salida: TransporteDePrueba, **mas) -> dict[str, int]:
    with admin(conn) as cur:
        r = despachar_avisos_admin(cur, salida, **mas)
    conn.commit()
    return r


def _el_token(texto: str) -> str:
    ultimo = texto.rsplit("\n", 1)[-1]
    assert ultimo.startswith(f"{DIRECCION}tarea/")
    return ultimo.rsplit("/", 1)[-1]


# --- La cola guarda la respuesta sin el enlace ----------------------------------------------------

def test_la_respuesta_pasa_por_la_cola_y_la_base_guarda_solo_el_hash(conn, mundo, ada):
    salida = TransporteDePrueba()
    _pedir(conn, salida)

    [enviado] = salida.enviados
    assert enviado.chat_id == ADA and enviado.sin_vista_previa
    token = _el_token(enviado.texto)
    [respuesta] = _respuestas(conn)
    assert respuesta["estado"] == "enviado" and respuesta["incident_id"] is None
    assert respuesta["chat_id"] == ADA
    assert str(respuesta["destinatario_app_user_id"]) == ada
    assert "Calibrar la balanza" in respuesta["cuerpo"]
    [marca] = _filas(conn, "select * from admin_notice_enlace")
    assert (str(marca["admin_notice_id"]), str(marca["task_id"]),
            str(marca["admin_app_user_id"]), str(marca["workspace_id"])) == (
        str(respuesta["id"]), mundo["norte"]["id"], ada, mundo["north-lab"]["id"])
    # El token en claro está sólo en el mensaje: en la base, el hash.
    [acceso] = _accesos(conn)
    assert acceso["token_hash"] == hashlib.sha256(token.encode()).hexdigest()
    for fila in (respuesta, marca, acceso):
        assert all(token not in str(valor) for valor in fila.values())
    assert len(_filas(conn, """select 1 from audit_log
                               where accion = 'emitir_acceso_tarea_de_administrador'""")) == 1


def test_una_respuesta_sin_enlace_tambien_pasa_por_la_cola(conn, mundo, ada):
    salida = TransporteDePrueba()
    _pedir(conn, salida, texto="/enlace north-lab")
    [enviado] = salida.enviados
    assert "/enlace <espacio>" in enviado.texto
    [respuesta] = _respuestas(conn)
    assert respuesta["estado"] == "enviado"
    assert _filas(conn, "select * from admin_notice_enlace") == []
    assert _accesos(conn) == []


def test_el_mismo_pedido_entregado_dos_veces_tiene_una_sola_respuesta(conn, mundo, ada):
    salida = TransporteDePrueba()
    _pedir(conn, salida, update_id=7)
    _pedir(conn, salida, update_id=7)
    assert len(salida.enviados) == 1
    assert len(_respuestas(conn)) == 1 and len(_accesos(conn)) == 1


# --- Si no sale, no queda ningún acceso -----------------------------------------------------------

def test_si_el_envio_falla_no_queda_ningun_acceso_y_al_reintentar_sale_uno(conn, mundo, ada):
    falla = TransporteDePrueba(falla_en={ADA})
    _pedir(conn, falla)
    assert falla.enviados == []
    assert _accesos(conn) == []
    [respuesta] = _respuestas(conn)
    assert (respuesta["estado"], respuesta["intentos"]) == ("listo", 1)
    [incidente] = _filas(conn, "select etapa, resumen_sanitizado, referencia_cruda from incident")
    assert incidente["etapa"] == "respuesta_del_bot_de_administracion"
    assert DIRECCION not in (incidente["referencia_cruda"] or "")

    anda = TransporteDePrueba()
    r = _despachar(conn, anda, ahora=respuesta["programado_para"])
    assert r["enviados"] == 1
    [enviado] = anda.enviados
    token = _el_token(enviado.texto)
    [acceso] = _accesos(conn)
    assert acceso["token_hash"] == hashlib.sha256(token.encode()).hexdigest()


def test_si_deja_de_ser_administrador_antes_de_salir_no_sale_ningun_enlace(conn, mundo, ada):
    falla = TransporteDePrueba(falla_en={ADA})
    _pedir(conn, falla)
    with admin(conn) as cur:
        cur.execute("delete from platform_role where app_user_id = %s", (ada,))
    conn.commit()
    [respuesta] = _respuestas(conn)

    anda = TransporteDePrueba()
    r = _despachar(conn, anda, ahora=respuesta["programado_para"])
    assert anda.enviados == [] and r["enviados"] == 0
    assert _accesos(conn) == []
    [respuesta] = _respuestas(conn)
    assert respuesta["estado"] == "descartado"
    etapas = [f["etapa"] for f in _filas(conn, "select etapa from incident order by at")]
    assert etapas == ["respuesta_del_bot_de_administracion"] * 2


def test_sin_la_direccion_publica_al_salir_no_sale_un_enlace_inventado(conn, mundo, ada,
                                                                       monkeypatch):
    falla = TransporteDePrueba(falla_en={ADA})
    _pedir(conn, falla)
    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url=""))
    [respuesta] = _respuestas(conn)
    anda = TransporteDePrueba()
    _despachar(conn, anda, ahora=respuesta["programado_para"])
    assert anda.enviados == [] and _accesos(conn) == []
    assert _respuestas(conn)[0]["estado"] == "descartado"


def test_si_la_pasada_vuelve_atras_no_queda_ningun_acceso_vigente(conn, mundo, ada):
    """Revisión de la corrección chica (`despachador.py:1471-1480`): el acceso se emite dentro
    de la transacción de la pasada. Si la pasada entera vuelve atrás después de mandarla (el
    `commit` de quien llama falla), el acceso vuelve atrás con ella: el enlace que salió no abre
    nada, la respuesta vuelve a la cola y la pasada siguiente manda uno nuevo, el único
    vigente. Nunca queda un acceso de un envío que la base no registró."""
    falla = TransporteDePrueba(falla_en={ADA})
    _pedir(conn, falla)
    [respuesta] = _respuestas(conn)

    salio = TransporteDePrueba()
    with admin(conn) as cur:
        despachar_avisos_admin(cur, salio, ahora=respuesta["programado_para"])
        raise psycopg.Rollback()        # la pasada vuelve atrás: el commit no llegó
    [enviado] = salio.enviados
    perdido = hashlib.sha256(_el_token(enviado.texto).encode()).hexdigest()
    assert _accesos(conn) == []
    assert _respuestas(conn)[0]["estado"] == "listo"

    anda = TransporteDePrueba()
    _despachar(conn, anda, ahora=respuesta["programado_para"])
    [acceso] = _accesos(conn)
    assert acceso["token_hash"] == hashlib.sha256(_el_token(anda.enviados[0].texto)
                                                  .encode()).hexdigest()
    assert acceso["token_hash"] != perdido


class _ElDescarteFalla:
    """Un cursor cuya escritura del descarte de una respuesta falla con un error de la base."""

    def __init__(self, cur) -> None:
        self._cur = cur

    def execute(self, sql, params=None, **kw):
        if "set estado = 'descartado'" in sql:
            return self._cur.execute("select 1 / 0")
        return self._cur.execute(sql, params, **kw)

    def __getattr__(self, nombre):
        return getattr(self._cur, nombre)


def test_una_falla_de_otra_respuesta_no_deja_muerto_el_enlace_que_ya_salio(conn, mundo, ada):
    """Revisión de la corrección chica (el enlace muerto si la pasada vuelve atrás): en la misma
    pasada, la respuesta de Ada sale con su enlace y la de otra persona, que ya no es
    administradora, se descarta. Si ese descarte fallaba con un error de la base, la pasada
    entera volvía atrás y el enlace que Ada ya tenía en Telegram no abría (y le llegaba otro
    después). Ahora el descarte va aislado: el enlace de Ada sigue vigente, y la otra respuesta
    queda en la cola, sin ningún acceso, para la pasada siguiente."""
    from leda.despachador import encolar_respuesta_admin
    with admin(conn) as cur:
        encolar_respuesta_admin(cur, ada, ADA, "La página, sólo para vos.", clave="prueba:ada",
                                enlace_de=(mundo["north-lab"]["id"], mundo["norte"]["id"]))
    conn.commit()
    with admin(conn) as cur:
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (79002, 'Bob Ex') returning id""")
        bob = str(cur.fetchone()["id"])
        encolar_respuesta_admin(cur, bob, 79002, "La página, sólo para vos.", clave="prueba:bob",
                                enlace_de=(mundo["north-lab"]["id"], mundo["norte"]["id"]))
    conn.commit()
    hasta = max(f["programado_para"] for f in _respuestas(conn))

    salida = TransporteDePrueba()
    try:
        with admin(conn) as cur:
            despachar_avisos_admin(_ElDescarteFalla(cur), salida, ahora=hasta)
    except psycopg.Error:
        conn.rollback()
    else:
        conn.commit()
    [enviado] = salida.enviados
    assert enviado.chat_id == ADA
    [acceso] = _accesos(conn)
    assert acceso["token_hash"] == hashlib.sha256(_el_token(enviado.texto).encode()).hexdigest()
    assert str(acceso["admin_app_user_id"]) == ada
    estados = {str(f["destinatario_app_user_id"]): f["estado"] for f in _respuestas(conn)}
    assert estados == {ada: "enviado", bob: "listo"}


def test_dos_pedidos_distintos_con_el_mismo_texto_tienen_cada_uno_su_respuesta(conn, mundo,
                                                                               ada):
    """Sugerencia de la revisión (`administracion.py:80`, la clave de la respuesta): la clave es
    el chat y el mensaje del pedido. Dos mensajes distintos con el mismo texto son dos pedidos y
    tienen dos respuestas; el mismo mensaje que Telegram entrega otra vez (otro update, el mismo
    mensaje), una. Sin defecto: lo fija."""
    salida = TransporteDePrueba()
    atender_admin(conn, mensaje_de_telegram(11, "/enlace north-lab balanza", ADA,
                                            message_id=501), salida, imprimir=lambda *_: None)
    atender_admin(conn, mensaje_de_telegram(12, "/enlace north-lab balanza", ADA,
                                            message_id=502), salida, imprimir=lambda *_: None)
    atender_admin(conn, mensaje_de_telegram(13, "/enlace north-lab balanza", ADA,
                                            message_id=502), salida, imprimir=lambda *_: None)
    assert len(salida.enviados) == 2
    assert len(_respuestas(conn)) == 2 and len(_accesos(conn)) == 2


def test_la_respuesta_de_ahora_sale_aunque_el_reloj_de_la_base_vaya_adelantado(conn, mundo,
                                                                               ada):
    """Sugerencia de la revisión (`despachador.py:1347-1348`): la respuesta se manda enseguida
    (`solo`), con la hora de la aplicación, y la cola la anota con la hora de la base. Si la
    base iba un poco adelantada, la pasada inmediata no la encontraba y la respuesta esperaba
    al ciclo siguiente. Lo que se manda enseguida no espera su hora: ya es su hora."""
    from datetime import timedelta
    from leda.despachador import encolar_respuesta_admin
    with admin(conn) as cur:
        aviso = encolar_respuesta_admin(cur, ada, ADA, "Para pedir el enlace…",
                                        clave="prueba:reloj")
        cur.execute("""update admin_notice set programado_para = now() + interval '2 minutes'
                        where id = %s returning programado_para""", (aviso,))
        programado = cur.fetchone()["programado_para"]
    conn.commit()
    salida = TransporteDePrueba()
    r = _despachar(conn, salida, ahora=programado - timedelta(minutes=2), solo=[aviso])
    assert r["enviados"] == 1 and len(salida.enviados) == 1


def test_una_respuesta_que_ya_fallo_espera_su_reintento_aunque_se_pida_enseguida(conn, mundo,
                                                                                 ada):
    """Revisión de la corrección de casos de borde (`despachador.py:1373-1374`): sólo el primer
    envío de una respuesta es inmediato (`solo`). Una que ya falló espera la hora de su
    reintento, aunque se la vuelva a pedir enseguida: la espera creciente entre intentos rige
    también para ella."""
    falla = TransporteDePrueba(falla_en={ADA})
    _pedir(conn, falla)
    [respuesta] = _respuestas(conn)
    assert (respuesta["estado"], respuesta["intentos"]) == ("listo", 1)

    anda = TransporteDePrueba()
    r = _despachar(conn, anda, solo=[respuesta["id"]])
    assert anda.enviados == [] and r["enviados"] == 0
    [igual] = _respuestas(conn)
    assert (igual["estado"], igual["intentos"]) == ("listo", 1)

    r = _despachar(conn, anda, ahora=respuesta["programado_para"], solo=[respuesta["id"]])
    assert r["enviados"] == 1 and len(anda.enviados) == 1


class _AnotarElIntentoFalla:
    """Un cursor cuya anotación de un intento fallido falla con un error de la base."""

    def __init__(self, cur) -> None:
        self._cur = cur

    def execute(self, sql, params=None, **kw):
        if "set intentos = %s, ultimo_error = %s" in sql:
            return self._cur.execute("select 1 / 0")
        return self._cur.execute(sql, params, **kw)

    def __getattr__(self, nombre):
        return getattr(self._cur, nombre)


def test_si_falla_anotar_un_intento_la_pasada_sigue_y_el_enlace_que_salio_abre(conn, mundo,
                                                                              ada):
    """Revisión de la corrección de casos de borde (`despachador.py:1426-1430`, sin prueba): en
    la misma pasada sale la respuesta de Ada con su enlace y la de otra persona no sale; si
    anotar ese intento falla con un error de la base, la pasada no vuelve atrás: el enlace de
    Ada sigue vigente, y la otra respuesta queda en la cola como estaba, sin un intento contado
    y sin ningún acceso, para la pasada siguiente."""
    from leda.despachador import encolar_respuesta_admin
    with admin(conn) as cur:
        encolar_respuesta_admin(cur, ada, ADA, "La página, sólo para vos.", clave="prueba:ada",
                                enlace_de=(mundo["north-lab"]["id"], mundo["norte"]["id"]))
    conn.commit()
    with admin(conn) as cur:
        encolar_respuesta_admin(cur, ada, 79003, "Para pedir el enlace…", clave="prueba:otra")
    conn.commit()
    hasta = max(f["programado_para"] for f in _respuestas(conn))

    salida = TransporteDePrueba(falla_en={79003})
    with admin(conn) as cur:
        r = despachar_avisos_admin(_AnotarElIntentoFalla(cur), salida, ahora=hasta)
    conn.commit()

    assert (r["enviados"], r["fallidos"]) == (1, 1)
    [enviado] = salida.enviados
    assert enviado.chat_id == ADA
    [acceso] = _accesos(conn)
    assert acceso["token_hash"] == hashlib.sha256(_el_token(enviado.texto).encode()).hexdigest()
    filas = {f["chat_id"]: f for f in _respuestas(conn)}
    assert filas[ADA]["estado"] == "enviado"
    assert (filas[79003]["estado"], filas[79003]["intentos"]) == ("listo", 0)

    # La pasada siguiente la vuelve a intentar.
    anda = TransporteDePrueba()
    _despachar(conn, anda, ahora=hasta)
    assert [e.chat_id for e in anda.enviados] == [79003]


def test_una_respuesta_que_agota_los_intentos_deja_su_rastro_y_ningun_acceso(conn, mundo, ada):
    """Sugerencia de la revisión (`despachador.py:1387-1393`, los reintentos de una respuesta,
    sin prueba): cada intento que no sale deja su rastro; el quinto la da por perdida, con el
    incidente de severidad alta que dice que era una respuesta del bot de administración, sin
    avisar por el mismo canal, y nunca queda un acceso."""
    from leda.despachador import MAX_INTENTOS
    falla = TransporteDePrueba(falla_en={ADA})
    _pedir(conn, falla)
    for _ in range(MAX_INTENTOS - 1):
        [respuesta] = _respuestas(conn)
        _despachar(conn, falla, ahora=respuesta["programado_para"])
    [respuesta] = _respuestas(conn)
    assert (respuesta["estado"], respuesta["intentos"]) == ("fallido", MAX_INTENTOS)
    assert falla.enviados == [] and _accesos(conn) == []
    incidentes = _filas(conn, """select etapa, severidad, resumen_sanitizado, notificado_admin_en
                                   from incident order by at""")
    assert [i["etapa"] for i in incidentes] == (
        ["respuesta_del_bot_de_administracion"] * (MAX_INTENTOS - 1) + ["entrega_aviso_admin"])
    ultimo = incidentes[-1]
    assert ultimo["severidad"] == "alta" and ultimo["notificado_admin_en"] is None
    assert "respuesta del bot de administración" in ultimo["resumen_sanitizado"]
    assert len(_filas(conn, "select 1 from admin_notice where not es_respuesta")) == 0


# --- La base ---------------------------------------------------------------------------------------

def test_la_aplicacion_no_llega_a_la_cola_ni_a_la_marca(conn):
    with admin(conn) as cur:
        for tabla in ("admin_notice", "admin_notice_enlace"):
            for privilegio in ("select", "insert", "update", "delete"):
                cur.execute("select has_table_privilege('leda_app', %s, %s) as puede",
                            (f"leda.{tabla}", privilegio))
                assert cur.fetchone()["puede"] is False, (tabla, privilegio)
    conn.commit()


def test_una_fila_de_la_cola_es_un_incidente_o_una_respuesta(conn, mundo, ada):
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            cur.execute("""insert into admin_notice (incident_id, es_respuesta,
                                                     destinatario_app_user_id, chat_id, cuerpo,
                                                     dedupe_key)
                           values (null, false, %s, %s, 'x', 'prueba:sin-incidente')""",
                        (ada, ADA))
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            cur.execute("""insert into admin_notice (incident_id, es_respuesta,
                                                     destinatario_app_user_id, chat_id, cuerpo,
                                                     dedupe_key)
                           values (gen_random_uuid(), true, %s, %s, 'x', 'prueba:las-dos')""",
                        (ada, ADA))
    conn.rollback()


def test_la_marca_del_enlace_es_de_una_tarea_de_su_espacio(conn, mundo, ada):
    """Como `message_outbox_enlace`: la tarea de la marca es del espacio que dice la marca."""
    with admin(conn) as cur:
        cur.execute("""insert into admin_notice (es_respuesta, workspace_id,
                                                 destinatario_app_user_id, chat_id, cuerpo,
                                                 dedupe_key)
                       values (true, %s, %s, %s, 'x', 'prueba:marca') returning id""",
                    (mundo["north-lab"]["id"], ada, ADA))
        aviso = cur.fetchone()["id"]
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            cur.execute("""insert into admin_notice_enlace (admin_notice_id, workspace_id,
                                                            task_id, admin_app_user_id)
                           values (%s, %s, %s, %s)""",
                        (aviso, mundo["west-studio"]["id"], mundo["norte"]["id"], ada))
    conn.rollback()
