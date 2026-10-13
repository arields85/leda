"""El enlace de un solo uso y la sesión de la puerta del equipo (ADR 0022, decisiones 4, 11 y 12;
migración 0057): la capa de garantías.

Lo que se prueba acá es la base y la credencial, no la API ni la web:

- **La credencial.** Sólo se guarda el hash SHA-256 de cada token, el del enlace y el de la
  sesión. `leda_app` no tiene ningún privilegio sobre `enlace_de_entrada` ni sobre `sesion_web`,
  sólo `execute` sobre las funciones que los emiten, los canjean, los leen y los cortan, que son
  `security definer` con dueño `leda_owner`.
- **El enlace sirve una sola vez** (decisión 4): el segundo canje no abre nada, tampoco si llegan
  los dos a la vez. Un enlace nuevo de la misma persona anula el que estaba sin usar. El que
  nadie usó vence a las 24 horas de emitido (migración 0065).
- **La sesión no vence** (decisiones 4 y 12): se revalida en cada pedido (la membresía sigue
  activa) y anota su último uso. Se corta sólo si la corta un administrador, si la persona avisa
  que perdió el celular o si deja el equipo; una sesión cortada no vuelve.
- **Aislamiento** (decisión 11): el espacio sale de la sesión o de la membresía, nunca de lo que
  diga quien llama. Una membresía o una sesión de otro espacio se tratan igual que una que no
  existe.
- **Auditoría** (constitución §12): emitir, canjear y cortar dejan su fila en `audit_log`, con su
  espacio y la versión del pack, sin el token ni su hash.
"""

from __future__ import annotations

import contextlib
import hashlib
import re
import secrets
import threading
import time
from pathlib import Path

import psycopg
import pytest

from leda.db import admin, conectar, espacio

TABLAS = ("enlace_de_entrada", "sesion_web")
FUNCIONES = ("emitir_enlace_de_entrada", "canjear_enlace_de_entrada", "sesion_vigente",
             "cortar_sesion", "cortar_sesiones_de_membresia")


# --- Ayudas ---------------------------------------------------------------------------------

def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@contextlib.contextmanager
def sin_espacio(conn):
    """La aplicación antes de saber de qué espacio es el pedido (el canje y cada pedido de la
    web)."""
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local role leda_app")
            yield cur


def _persona(mundo: dict, nombre: str, slug: str = "north-lab") -> str:
    return mundo[slug]["people"][nombre]["membership_id"]


def _emitir(conn, mundo: dict, nombre: str, slug: str = "north-lab",
            en: str | None = None) -> str | None:
    """Emite el enlace de una persona desde una sesión acotada a `en` (por omisión, su espacio).
    Devuelve el token en claro, o `None` si la base no lo emitió."""
    token = secrets.token_urlsafe(32)
    with espacio(conn, mundo[en or slug]["id"]) as cur:
        cur.execute("select emitir_enlace_de_entrada(%s, %s, null) as id",
                    (_persona(mundo, nombre, slug), _hash(token)))
        emitido = cur.fetchone()["id"]
    conn.commit()
    return token if emitido else None


def _canjear(conn, token: str) -> tuple[str | None, str]:
    """Canjea un enlace; devuelve el id de la sesión (o `None`) y el token de la sesión."""
    sesion = secrets.token_urlsafe(32)
    with sin_espacio(conn) as cur:
        cur.execute("select canjear_enlace_de_entrada(%s, %s) as id",
                    (_hash(token), _hash(sesion)))
        sesion_id = cur.fetchone()["id"]
    conn.commit()
    return (str(sesion_id) if sesion_id else None), sesion


def _entrar(conn, mundo: dict, nombre: str, slug: str = "north-lab") -> tuple[str, str]:
    """Una sesión abierta de una persona: su id y su token."""
    sesion_id, sesion = _canjear(conn, _emitir(conn, mundo, nombre, slug))
    assert sesion_id
    return sesion_id, sesion


def _vigente(conn, sesion: str) -> dict | None:
    with sin_espacio(conn) as cur:
        cur.execute("select * from sesion_vigente(%s)", (_hash(sesion),))
        fila = cur.fetchone()
    conn.commit()
    return fila


def _cortar(conn, mundo: dict, sesion_id: str, motivo: str = "administrador",
            en: str = "north-lab") -> bool:
    with espacio(conn, mundo[en]["id"]) as cur:
        cur.execute("select cortar_sesion(%s, %s, null) as cortada", (sesion_id, motivo))
        cortada = cur.fetchone()["cortada"]
    conn.commit()
    return cortada


def _auditoria(conn, accion: str) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select * from audit_log where accion = %s order by at, id", (accion,))
        return cur.fetchall()


def _sesion(conn, sesion_id: str) -> dict:
    with admin(conn) as cur:
        cur.execute("select * from sesion_web where id = %s", (sesion_id,))
        return cur.fetchone()


# --- Las tablas y las funciones -------------------------------------------------------------

def test_las_tablas_tienen_espacio_obligatorio_y_rls_forzado(conn):
    with admin(conn) as cur:
        for tabla in TABLAS:
            cur.execute("""select relrowsecurity, relforcerowsecurity
                             from pg_class where oid = to_regclass(%s)""", (f"leda.{tabla}",))
            fila = cur.fetchone()
            assert fila is not None, f"{tabla} no existe"
            assert fila["relrowsecurity"] and fila["relforcerowsecurity"], tabla
            cur.execute("""select is_nullable from information_schema.columns
                            where table_schema = 'leda' and table_name = %s
                              and column_name = 'workspace_id'""", (tabla,))
            assert cur.fetchone()["is_nullable"] == "NO", tabla
            cur.execute("select polname from pg_policy where polrelid = to_regclass(%s)",
                        (f"leda.{tabla}",))
            assert {p["polname"] for p in cur.fetchall()} == {
                "aislamiento_espacio", "resolver_por_token"}, tabla


def test_la_aplicacion_no_tiene_privilegios_sobre_los_enlaces_ni_las_sesiones(conn,
                                                                               intake_world):
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        for tabla in TABLAS:
            for orden in (f"select * from {tabla}", f"delete from {tabla}",
                          f"update {tabla} set workspace_id = workspace_id"):
                with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                    cur.execute(orden)


def test_las_funciones_son_elevadas_de_leda_owner_y_solo_las_ejecuta_la_aplicacion(conn):
    with admin(conn) as cur:
        cur.execute(
            """select p.proname, r.rolname, p.prosecdef, p.proconfig,
                      has_function_privilege('public', p.oid, 'execute') as de_public,
                      has_function_privilege('leda_app', p.oid, 'execute') as de_app
                 from pg_proc p join pg_roles r on r.oid = p.proowner
                 join pg_namespace n on n.oid = p.pronamespace
                where n.nspname = 'leda' and p.proname = any(%s)""", (list(FUNCIONES),))
        filas = {f["proname"]: f for f in cur.fetchall()}
    assert set(filas) == set(FUNCIONES)
    for nombre, f in filas.items():
        assert f["rolname"] == "leda_owner", nombre
        assert f["prosecdef"], f"{nombre} tiene que ser security definer"
        assert any(c.startswith("search_path=") and c.endswith("pg_temp")
                   for c in f["proconfig"] or []), nombre
        assert not f["de_public"], nombre
        assert f["de_app"], nombre


# --- La credencial --------------------------------------------------------------------------

def test_solo_se_guarda_el_hash_de_cada_token(conn, intake_world):
    enlace = _emitir(conn, intake_world, "Sam Noble")
    sesion_id, sesion = _canjear(conn, enlace)
    assert sesion_id
    with admin(conn) as cur:
        cur.execute("select * from enlace_de_entrada")
        enlaces = cur.fetchall()
        cur.execute("select * from sesion_web")
        sesiones = cur.fetchall()
    assert len(enlaces) == 1 and len(sesiones) == 1
    for fila in enlaces + sesiones:
        for columna, valor in fila.items():
            assert enlace not in str(valor), f"el enlace en claro apareció en {columna}"
            assert sesion not in str(valor), f"la sesión en claro apareció en {columna}"
    assert enlaces[0]["token_hash"] == _hash(enlace)
    assert sesiones[0]["token_hash"] == _hash(sesion)


def test_un_hash_mal_formado_no_se_guarda_ni_se_busca(conn, intake_world):
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            cur.execute("select emitir_enlace_de_entrada(%s, 'no-es-un-hash', null)",
                        (_persona(intake_world, "Sam Noble"),))
    conn.commit()
    with sin_espacio(conn) as cur:
        cur.execute("select canjear_enlace_de_entrada('', %s) as id", (_hash("x"),))
        assert cur.fetchone()["id"] is None
        cur.execute("select count(*) n from sesion_vigente(null)")
        assert cur.fetchone()["n"] == 0


# --- El enlace sirve una sola vez -----------------------------------------------------------

def test_el_enlace_abre_una_sesion_una_sola_vez(conn, intake_world):
    enlace = _emitir(conn, intake_world, "Sam Noble")
    primera, _ = _canjear(conn, enlace)
    segunda, sesion_reenviada = _canjear(conn, enlace)
    assert primera is not None
    assert segunda is None, "un enlace ya usado abrió otra sesión"
    assert _vigente(conn, sesion_reenviada) is None
    with admin(conn) as cur:
        cur.execute("select count(*) n from sesion_web")
        assert cur.fetchone()["n"] == 1
        cur.execute("select canjeado_en from enlace_de_entrada")
        assert cur.fetchone()["canjeado_en"] is not None


def test_dos_canjes_a_la_vez_abren_una_sola_sesion(conn, uri, intake_world):
    """Quien reenvía el mensaje y su dueño tocan el enlace al mismo tiempo: entra uno."""
    enlace = _emitir(conn, intake_world, "Sam Noble")
    otra = conectar(uri)
    resultado: dict = {}
    try:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("set local role leda_app")
                cur.execute("select canjear_enlace_de_entrada(%s, %s) as id",
                            (_hash(enlace), _hash(secrets.token_urlsafe(32))))
                resultado["primera"] = cur.fetchone()["id"]

                def segunda():
                    resultado["segunda"], _ = _canjear(otra, enlace)

                hilo = threading.Thread(target=segunda)
                hilo.start()
                time.sleep(0.5)  # la segunda espera el candado de la primera
        hilo.join(timeout=10)
        assert not hilo.is_alive()
    finally:
        otra.close()
    assert resultado["primera"] is not None
    assert resultado["segunda"] is None
    with admin(conn) as cur:
        cur.execute("select count(*) n from sesion_web")
        assert cur.fetchone()["n"] == 1


def test_un_enlace_nuevo_anula_el_que_estaba_sin_usar(conn, intake_world):
    viejo = _emitir(conn, intake_world, "Sam Noble")
    nuevo = _emitir(conn, intake_world, "Sam Noble")
    assert viejo != nuevo
    assert _canjear(conn, viejo)[0] is None, "el enlace reemplazado todavía abre"
    assert _canjear(conn, nuevo)[0] is not None


def _emitido_hace(conn, enlace: str, intervalo: str) -> None:
    """Corre hacia atrás el `emitido_en` de un enlace, con el `now()` real de la base."""
    with admin(conn) as cur:
        cur.execute("update enlace_de_entrada set emitido_en = now() - %s::interval"
                    " where token_hash = %s", (intervalo, _hash(enlace)))
        assert cur.rowcount == 1
    conn.commit()


def test_el_enlace_que_nadie_uso_vence_a_las_24_horas(conn, intake_world):
    """Decisión del usuario (acceso por chat, 2026-10-12; migración 0065): el enlace que nadie
    usó vence a las 24 horas de emitido. Vencido, el canje no abre nada, igual que un enlace ya
    usado: ni sesión, ni canje, ni fila de auditoría del canje."""
    enlace = _emitir(conn, intake_world, "Sam Noble")
    _emitido_hace(conn, enlace, "24 hours 1 minute")
    sesion_id, sesion = _canjear(conn, enlace)
    assert sesion_id is None, "un enlace de hace más de 24 horas abrió una sesión"
    assert _vigente(conn, sesion) is None
    with admin(conn) as cur:
        cur.execute("select count(*) n from sesion_web")
        assert cur.fetchone()["n"] == 0
        cur.execute("select canjeado_en from enlace_de_entrada")
        assert cur.fetchone()["canjeado_en"] is None
    assert _auditoria(conn, "canjear_enlace_de_entrada") == []


def test_el_enlace_de_hace_menos_de_24_horas_todavia_abre(conn, intake_world):
    enlace = _emitir(conn, intake_world, "Sam Noble")
    _emitido_hace(conn, enlace, "23 hours 59 minutes")
    assert _canjear(conn, enlace)[0] is not None, "un enlace de menos de 24 horas no abrió"


def test_despues_de_un_enlace_vencido_uno_nuevo_abre(conn, intake_world):
    """El vencido no queda marcado (se deduce de `emitido_en`) y sigue siendo el que estaba sin
    usar: pedir otro lo anula, como siempre, y el nuevo cuenta sus propias 24 horas."""
    viejo = _emitir(conn, intake_world, "Sam Noble")
    _emitido_hace(conn, viejo, "3 days")
    assert _canjear(conn, viejo)[0] is None
    nuevo = _emitir(conn, intake_world, "Sam Noble")
    assert nuevo is not None
    assert _canjear(conn, nuevo)[0] is not None
    with admin(conn) as cur:
        cur.execute("select anulado_en from enlace_de_entrada where token_hash = %s",
                    (_hash(viejo),))
        assert cur.fetchone()["anulado_en"] is not None


def test_un_token_inventado_no_abre_nada(conn, intake_world):
    _emitir(conn, intake_world, "Sam Noble")
    assert _canjear(conn, secrets.token_urlsafe(32))[0] is None
    assert _vigente(conn, secrets.token_urlsafe(32)) is None


# --- La sesión ------------------------------------------------------------------------------

def test_la_sesion_dice_su_espacio_y_su_membresia_y_fija_el_espacio(conn, intake_world):
    norte = intake_world["north-lab"]
    sesion_id, sesion = _entrar(conn, intake_world, "Sam Noble")
    with sin_espacio(conn) as cur:
        cur.execute("select * from sesion_vigente(%s)", (_hash(sesion),))
        fila = cur.fetchone()
        cur.execute("select current_setting('leda.workspace_id', true) as ws")
        fijado = cur.fetchone()["ws"]
    conn.commit()
    assert str(fila["sesion_id"]) == sesion_id
    assert str(fila["workspace_id"]) == norte["id"]
    assert str(fila["membership_id"]) == _persona(intake_world, "Sam Noble")
    assert fijado == norte["id"], "el espacio de la sesión no quedó fijado para el pedido"


def test_la_sesion_no_vence_y_anota_su_ultimo_uso(conn, intake_world):
    sesion_id, sesion = _entrar(conn, intake_world, "Sam Noble")
    with admin(conn) as cur:
        cur.execute("""update sesion_web set creada_en = now() - interval '400 days',
                                             ultimo_uso_en = now() - interval '400 days'
                        where id = %s""", (sesion_id,))
    conn.commit()
    assert _vigente(conn, sesion) is not None, "una sesión vieja dejó de entrar"
    assert _vigente(conn, sesion) is not None
    usada = _sesion(conn, sesion_id)
    assert usada["ultimo_uso_en"] > usada["creada_en"]
    assert usada["cortada_en"] is None


def test_una_sesion_cortada_no_entra_y_no_vuelve(conn, intake_world):
    sesion_id, sesion = _entrar(conn, intake_world, "Sam Noble")
    assert _cortar(conn, intake_world, sesion_id, "perdio_el_celular")
    assert _vigente(conn, sesion) is None
    assert not _cortar(conn, intake_world, sesion_id), "una sesión se cortó dos veces"
    cortada = _sesion(conn, sesion_id)
    assert cortada["cortada_en"] is not None
    assert cortada["motivo_de_corte"] == "perdio_el_celular"


def test_un_motivo_desconocido_no_corta(conn, intake_world):
    sesion_id, sesion = _entrar(conn, intake_world, "Sam Noble")
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        with pytest.raises(psycopg.Error), conn.transaction():
            cur.execute("select cortar_sesion(%s, 'porque si', null)", (sesion_id,))
    conn.commit()
    assert _vigente(conn, sesion) is not None


def test_cortar_las_sesiones_de_una_persona_corta_todas_y_anula_su_enlace(conn, intake_world):
    _, celular = _entrar(conn, intake_world, "Sam Noble")
    _, computadora = _entrar(conn, intake_world, "Sam Noble")
    pendiente = _emitir(conn, intake_world, "Sam Noble")
    _, de_otro = _entrar(conn, intake_world, "Sam North")
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        cur.execute("select cortar_sesiones_de_membresia(%s, 'administrador', null) as n",
                    (_persona(intake_world, "Sam Noble"),))
        assert cur.fetchone()["n"] == 2
    conn.commit()
    assert _vigente(conn, celular) is None
    assert _vigente(conn, computadora) is None
    assert _canjear(conn, pendiente)[0] is None, "el enlace pendiente sobrevivió al corte"
    assert _vigente(conn, de_otro) is not None, "se cortó la sesión de otra persona"


def test_quien_deja_el_equipo_no_entra_y_su_sesion_queda_cortada(conn, intake_world):
    sesion_id, sesion = _entrar(conn, intake_world, "Sam Noble")
    pendiente = _emitir(conn, intake_world, "Sam Noble")
    membresia = _persona(intake_world, "Sam Noble")
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s", (membresia,))
    conn.commit()
    assert _vigente(conn, sesion) is None
    assert _canjear(conn, pendiente)[0] is None
    cortada = _sesion(conn, sesion_id)
    assert cortada["motivo_de_corte"] == "dejo_el_equipo"
    # Si vuelve al equipo, la sesión cortada no revive: pide un enlace nuevo.
    with admin(conn) as cur:
        cur.execute("update membership set activo = true where id = %s", (membresia,))
    conn.commit()
    assert _vigente(conn, sesion) is None
    assert _canjear(conn, _emitir(conn, intake_world, "Sam Noble"))[0] is not None


def test_a_quien_ya_no_esta_no_se_le_emite_un_enlace(conn, intake_world):
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (_persona(intake_world, "Sam Noble"),))
    conn.commit()
    assert _emitir(conn, intake_world, "Sam Noble") is None


# --- Aislamiento entre espacios -------------------------------------------------------------

def test_no_se_emite_un_enlace_para_la_membresia_de_otro_espacio(conn, intake_world):
    """Desde North Lab, una membresía de West Studio es igual a una que no existe."""
    assert _emitir(conn, intake_world, "Sam Noble", slug="west-studio", en="north-lab") is None
    with admin(conn) as cur:
        cur.execute("select count(*) n from enlace_de_entrada")
        assert cur.fetchone()["n"] == 0


def test_el_espacio_sale_de_la_sesion_y_no_de_quien_llama(conn, intake_world):
    oeste = intake_world["west-studio"]
    _, sesion = _entrar(conn, intake_world, "Sam Noble", slug="west-studio")
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        cur.execute("select * from sesion_vigente(%s)", (_hash(sesion),))
        fila = cur.fetchone()
        cur.execute("select current_setting('leda.workspace_id', true) as ws")
        fijado = cur.fetchone()["ws"]
    conn.commit()
    assert str(fila["workspace_id"]) == oeste["id"]
    assert fijado == oeste["id"]


def test_un_token_que_no_entra_no_cambia_el_espacio_de_quien_llama(conn, intake_world):
    norte = intake_world["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        cur.execute("select count(*) n from sesion_vigente(%s)",
                    (_hash(secrets.token_urlsafe(32)),))
        assert cur.fetchone()["n"] == 0
        cur.execute("select canjear_enlace_de_entrada(%s, %s) as id",
                    (_hash(secrets.token_urlsafe(32)), _hash(secrets.token_urlsafe(32))))
        assert cur.fetchone()["id"] is None
        cur.execute("select current_setting('leda.workspace_id', true) as ws")
        assert cur.fetchone()["ws"] == norte["id"]
    conn.commit()


def test_el_canje_no_deja_fijado_el_espacio_del_enlace(conn, intake_world):
    """Canjear sólo abre la sesión: el pedido siguiente entra por la sesión."""
    enlace = _emitir(conn, intake_world, "Sam Noble", slug="west-studio")
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        cur.execute("select canjear_enlace_de_entrada(%s, %s) as id",
                    (_hash(enlace), _hash(secrets.token_urlsafe(32))))
        assert cur.fetchone()["id"] is not None
        cur.execute("select current_setting('leda.workspace_id', true) as ws")
        assert cur.fetchone()["ws"] == intake_world["north-lab"]["id"]
    conn.commit()


def test_un_espacio_no_corta_las_sesiones_de_otro(conn, intake_world):
    sesion_id, sesion = _entrar(conn, intake_world, "Sam Noble", slug="west-studio")
    assert not _cortar(conn, intake_world, sesion_id, en="north-lab")
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        cur.execute("select cortar_sesiones_de_membresia(%s, 'administrador', null) as n",
                    (_persona(intake_world, "Sam Noble", "west-studio"),))
        assert cur.fetchone()["n"] == 0
    conn.commit()
    assert _vigente(conn, sesion) is not None
    assert _sesion(conn, sesion_id)["cortada_en"] is None


def test_desde_un_espacio_no_se_ven_los_enlaces_ni_las_sesiones_de_otro(conn, intake_world):
    """La política por espacio rige también para el dueño de las funciones."""
    _entrar(conn, intake_world, "Sam Noble", slug="west-studio")
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local role leda_owner")
            cur.execute("select set_config('leda.workspace_id', %s, true)",
                        (intake_world["north-lab"]["id"],))
            for tabla in TABLAS:
                cur.execute(f"select count(*) n from {tabla}")
                assert cur.fetchone()["n"] == 0, f"{tabla}: se ven filas de otro espacio"
    conn.commit()


# --- Auditoría ------------------------------------------------------------------------------

def test_emitir_canjear_y_cortar_quedan_en_la_auditoria(conn, intake_world):
    norte = intake_world["north-lab"]
    membresia = _persona(intake_world, "Sam Noble")
    enlace = _emitir(conn, intake_world, "Sam Noble")
    sesion_id, sesion = _canjear(conn, enlace)
    assert _cortar(conn, intake_world, sesion_id, "administrador")

    emitidos = _auditoria(conn, "emitir_enlace_de_entrada")
    canjes = _auditoria(conn, "canjear_enlace_de_entrada")
    cortes = _auditoria(conn, "cortar_sesion_web")
    assert len(emitidos) == len(canjes) == len(cortes) == 1
    for fila in emitidos + canjes + cortes:
        assert str(fila["workspace_id"]) == norte["id"]
        assert fila["pack_hash"] == "hash-0"
        for valor in (enlace, sesion, _hash(enlace), _hash(sesion)):
            assert valor not in str(fila["detalle"]), "un token o su hash quedó en la auditoría"
    assert str(emitidos[0]["sujeto_id"]) == membresia
    assert emitidos[0]["actor_kind"] == "leda"
    assert canjes[0]["actor_kind"] == "persona"
    assert str(canjes[0]["actor_app_user_id"]) == (
        intake_world["north-lab"]["people"]["Sam Noble"]["app_user_id"])
    assert str(canjes[0]["sujeto_id"]) == sesion_id
    assert str(cortes[0]["sujeto_id"]) == sesion_id
    assert cortes[0]["detalle"]["motivo"] == "administrador"


def test_el_corte_dice_quien_lo_hizo(conn, intake_world):
    sesion_id, _ = _entrar(conn, intake_world, "Sam Noble")
    quien = intake_world["north-lab"]["people"]["Morgan Hale"]["app_user_id"]
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        cur.execute("select cortar_sesion(%s, 'administrador', %s) as cortada",
                    (sesion_id, quien))
        assert cur.fetchone()["cortada"]
    conn.commit()
    corte = _auditoria(conn, "cortar_sesion_web")[0]
    assert corte["actor_kind"] == "persona"
    assert str(corte["actor_app_user_id"]) == quien


def test_el_corte_por_dejar_el_equipo_queda_en_la_auditoria(conn, intake_world):
    sesion_id, sesion = _entrar(conn, intake_world, "Sam Noble")
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (_persona(intake_world, "Sam Noble"),))
    conn.commit()
    assert _vigente(conn, sesion) is None
    cortes = _auditoria(conn, "cortar_sesion_web")
    assert len(cortes) == 1
    assert cortes[0]["actor_kind"] == "sistema"
    assert cortes[0]["detalle"]["motivo"] == "dejo_el_equipo"
    assert str(cortes[0]["sujeto_id"]) == sesion_id


# --- La vuelta atrás ------------------------------------------------------------------------

def test_el_rollback_de_la_0057_se_niega_si_hay_enlaces_o_sesiones(conn, intake_world):
    """Deshacerla dejaría afuera, sin aviso, a quien tiene una sesión abierta o un enlace."""
    script = (Path(__file__).resolve().parents[2] / "db" / "rollbacks"
              / "0057_el_enlace_y_la_sesion_de_la_web.sql").read_text("utf-8")
    guarda = re.findall(r"do \$\$.*?end \$\$;", script, re.S)[-1]
    _entrar(conn, intake_world, "Sam Noble")
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.RaiseException, match="0057 rollback refused"),                 conn.transaction():
            cur.execute("set local search_path = leda, public")
            cur.execute(guarda)
        cur.execute("select count(*) n from sesion_web")
        assert cur.fetchone()["n"] == 1
