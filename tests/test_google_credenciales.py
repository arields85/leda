"""Credencial de Google por espacio (rama auxiliar, G2b).

La tabla `credencial_google` (payload cifrado), su proyección de estado
`credencial_google_estado` y los eventos `credencial_google_evento` no le dan
ningún privilegio a `prisma_app`: se llega sólo por funciones `security
definer` de `prisma_owner`, igual que `acceso_tablero` y
`alta_correo_verificacion`. Ninguna clave de estas pruebas sale del entorno
real: se generan acá mismo.
"""

from __future__ import annotations

import contextlib
import json
from datetime import datetime, timezone

import psycopg
import pytest
from cryptography.fernet import Fernet

from prisma import cli
from prisma.db import admin, espacio, sin_espacio
from prisma.google import cifrado
from prisma.google import credenciales as GC

CUENTA = "prisma@example.com"
SCOPES = (
    "openid", "email",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.events",
)

TABLAS = ("credencial_google", "credencial_google_estado",
          "credencial_google_evento")

# Lo que el runtime necesita (leer para usar, marcar reautorización, leer el
# estado) y lo que sólo hace el camino de operación/administración.
FUNCIONES_APP = (
    "leer_credencial_google()",
    "estado_credencial_google()",
    "marcar_reautorizacion_google(text,timestamptz)",
)
FUNCIONES_ADMIN = (
    "guardar_credencial_google(uuid,text,text,text[])",
    "revocar_credencial_google(uuid,text)",
    "credenciales_google_cifradas()",
    "reemplazar_token_google(uuid,text,text)",
)
FUNCIONES_ELEVADAS = tuple(
    f.split("(")[0] for f in FUNCIONES_APP + FUNCIONES_ADMIN
) + ("preparar_evento_credencial_google", "aplicar_evento_credencial_google")


def _clave() -> str:
    return Fernet.generate_key().decode("ascii")


def _cifrador(*claves: str) -> cifrado.Cifrador:
    return cifrado.desde_texto(",".join(claves))


def _autorizar(conn, workspace_id, cifrador, secreto="refresh-token-de-prueba"):
    with admin(conn) as cur:
        GC.guardar(cur, workspace_id, secreto, CUENTA, SCOPES, cifrador=cifrador)
    conn.commit()


AHORA = datetime.now(timezone.utc)


def _leida(conn, workspace_id, cifrador):
    """La credencial tal como la leería el runtime."""
    with espacio(conn, workspace_id) as cur:
        return GC.leer(cur, cifrador=cifrador)


def _crudo(conn, workspace_id):
    """La columna tal como quedó en la base, leída como operador."""
    with admin(conn) as cur:
        cur.execute("select token_cifrado from credencial_google "
                    "where workspace_id = %s", (workspace_id,))
        fila = cur.fetchone()
    return fila["token_cifrado"] if fila else None


def _eventos(conn, workspace_id):
    with admin(conn) as cur:
        cur.execute("select tipo, motivo, actor_kind from credencial_google_evento "
                    "where workspace_id = %s order by at, id", (workspace_id,))
        return cur.fetchall()


# ---------------------------------------------------------------------------
# Privilegios: nada de esto lo toca prisma_app directamente
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("tabla", TABLAS)
@pytest.mark.parametrize("sentencia", [
    "select * from {t}",
    "insert into {t} default values",
    "update {t} set workspace_id = workspace_id",
    "delete from {t}",
])
def test_prisma_app_no_tiene_ningun_privilegio_directo(
        intake_world, conn, tabla, sentencia):
    norte = intake_world["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute(sentencia.format(t=tabla))


def test_los_privilegios_de_las_funciones_son_exactamente_los_previstos(conn):
    con_permiso = {}
    with admin(conn) as cur:
        for firma in FUNCIONES_APP + FUNCIONES_ADMIN:
            cur.execute(
                """select to_regprocedure(%s) is not null existe,
                          has_function_privilege('public', %s, 'execute') publico,
                          has_function_privilege('prisma_app', %s, 'execute') app,
                          has_function_privilege('prisma_admin', %s, 'execute') adm""",
                (f"prisma.{firma}",) * 4)
            con_permiso[firma] = cur.fetchone()

    for firma, p in con_permiso.items():
        assert p["existe"], f"falta {firma}"
        assert p["publico"] is False, f"{firma} es ejecutable por public"
    assert {f for f, p in con_permiso.items() if p["app"]} == set(FUNCIONES_APP)
    assert {f for f, p in con_permiso.items() if p["adm"]} == set(FUNCIONES_ADMIN)


def test_las_funciones_son_security_definer_de_prisma_owner_con_search_path_fijo(conn):
    with admin(conn) as cur:
        cur.execute(
            """select p.proname, p.prosecdef, r.rolname, p.proconfig
                 from pg_proc p
                 join pg_roles r on r.oid = p.proowner
                 join pg_namespace n on n.oid = p.pronamespace
                where n.nspname = 'prisma' and p.proname = any(%s)""",
            (list(FUNCIONES_ELEVADAS),))
        filas = cur.fetchall()

    assert {f["proname"] for f in filas} == set(FUNCIONES_ELEVADAS)
    for f in filas:
        assert f["prosecdef"], f"{f['proname']} no es security definer"
        assert f["rolname"] == "prisma_owner", f"{f['proname']}: dueño {f['rolname']}"
        assert "search_path=prisma, public, pg_temp" in (f["proconfig"] or []), (
            f"{f['proname']} no fija el search_path")


@pytest.mark.parametrize("tabla", TABLAS)
def test_las_tres_tablas_tienen_espacio_obligatorio_y_rls_forzada(conn, tabla):
    with admin(conn) as cur:
        cur.execute(
            "select relrowsecurity, relforcerowsecurity from pg_class "
            "where oid = to_regclass(%s)", (f"prisma.{tabla}",))
        seguridad = cur.fetchone()
        cur.execute(
            "select polname from pg_policy where polrelid = to_regclass(%s)",
            (f"prisma.{tabla}",))
        politicas = [p["polname"] for p in cur.fetchall()]
        cur.execute(
            "select is_nullable from information_schema.columns "
            "where table_schema = 'prisma' and table_name = %s "
            "and column_name = 'workspace_id'", (tabla,))
        nulable = cur.fetchone()["is_nullable"]

    assert seguridad == {"relrowsecurity": True, "relforcerowsecurity": True}
    assert politicas == ["aislamiento_espacio"]
    assert nulable == "NO"


def test_las_funciones_de_operacion_no_las_ejecuta_prisma_app(intake_world, conn):
    """Guardar y revocar son del camino de autorización (un comando de
    operación): un runtime comprometido no puede plantar una credencial ni
    revocar la del espacio."""
    norte = intake_world["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute("select revocar_credencial_google(%s::uuid, 'x')",
                        (norte["id"],))
    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute(
                "select guardar_credencial_google(%s::uuid, 't', 'a@b.c', array['x'])",
                (norte["id"],))


def test_las_funciones_del_runtime_exigen_un_espacio_declarado(intake_world, conn):
    with pytest.raises(psycopg.errors.RaiseException):
        with sin_espacio(conn) as cur:
            GC.estado(cur)
    with pytest.raises(psycopg.errors.RaiseException):
        with sin_espacio(conn) as cur:
            cur.execute("select * from leer_credencial_google()")


# ---------------------------------------------------------------------------
# Estados proyectados desde los eventos
# ---------------------------------------------------------------------------


def test_el_ciclo_completo_de_estados(intake_world, conn):
    norte = intake_world["north-lab"]["id"]
    cifrador = _cifrador(_clave())

    with espacio(conn, norte) as cur:
        assert GC.estado(cur) == "sin_autorizar"
        assert GC.leer(cur, cifrador=cifrador) is None

    _autorizar(conn, norte, cifrador, "secreto-1")
    with espacio(conn, norte) as cur:
        assert GC.estado(cur) == "vigente"
        cred = GC.leer(cur, cifrador=cifrador)
        assert cred.secreto == "secreto-1"
        assert cred.autorizada_en is not None
        assert cred.cuenta_email == CUENTA
        assert cred.scopes == SCOPES
        assert cred.estado == "vigente"

    with espacio(conn, norte) as cur:
        assert GC.marcar_reautorizacion(
            cur, "invalid_grant", cred.autorizada_en) == GC.MARCADA
    conn.commit()
    with espacio(conn, norte) as cur:
        assert GC.estado(cur) == "requiere_reautorizacion"
        # Sigue habiendo credencial guardada, pero declara su estado.
        assert GC.leer(cur, cifrador=cifrador).estado == "requiere_reautorizacion"

    _autorizar(conn, norte, cifrador, "secreto-2")
    with espacio(conn, norte) as cur:
        assert GC.estado(cur) == "vigente"
        assert GC.leer(cur, cifrador=cifrador).secreto == "secreto-2"

    with admin(conn) as cur:
        assert GC.revocar(cur, norte, "revocada_por_administracion") is True
    conn.commit()
    with espacio(conn, norte) as cur:
        assert GC.estado(cur) == "revocada"
        assert GC.leer(cur, cifrador=cifrador) is None
    # La revocación borra el payload cifrado.
    assert _crudo(conn, norte) is None

    assert [(e["tipo"], e["motivo"]) for e in _eventos(conn, norte)] == [
        ("autorizada", None),
        ("reautorizacion_requerida", "invalid_grant"),
        ("autorizada", None),
        ("revocada", "revocada_por_administracion"),
    ]


def test_marcar_o_revocar_sin_credencial_vigente_no_emite_nada(intake_world, conn):
    norte = intake_world["north-lab"]["id"]
    cifrador = _cifrador(_clave())

    with espacio(conn, norte) as cur:
        assert GC.marcar_reautorizacion(
            cur, "invalid_grant", AHORA) == GC.SIN_CAMBIO
    with admin(conn) as cur:
        assert GC.revocar(cur, norte, "x") is False
    conn.commit()
    assert _eventos(conn, norte) == []

    _autorizar(conn, norte, cifrador)
    cred = _leida(conn, norte, cifrador)
    with espacio(conn, norte) as cur:
        assert GC.marcar_reautorizacion(
            cur, "invalid_grant", cred.autorizada_en) == GC.MARCADA
    conn.commit()
    # Idempotente: ya requiere reautorización, no se repite el evento.
    with espacio(conn, norte) as cur:
        assert GC.marcar_reautorizacion(
            cur, "invalid_grant", cred.autorizada_en) == GC.SIN_CAMBIO
    conn.commit()
    assert len(_eventos(conn, norte)) == 2

    with admin(conn) as cur:
        assert GC.revocar(cur, norte, "revocada_por_administracion") is True
        assert GC.revocar(cur, norte, "revocada_por_administracion") is False
    conn.commit()
    assert len(_eventos(conn, norte)) == 3
    with espacio(conn, norte) as cur:
        assert GC.marcar_reautorizacion(
            cur, "invalid_grant", cred.autorizada_en) == GC.SIN_CAMBIO


def test_una_credencial_revocada_devuelve_sin_cambio_aunque_coincida(
        intake_world, conn):
    norte = intake_world["north-lab"]["id"]
    cifrador = _cifrador(_clave())
    _autorizar(conn, norte, cifrador)
    cred = _leida(conn, norte, cifrador)
    with admin(conn) as cur:
        GC.revocar(cur, norte, "revocada_por_administracion")
    conn.commit()
    with espacio(conn, norte) as cur:
        assert GC.marcar_reautorizacion(
            cur, "invalid_grant", cred.autorizada_en) == GC.SIN_CAMBIO


def test_un_invalid_grant_tardio_no_pisa_una_credencial_reautorizada(
        intake_world, conn):
    """R4-001: el runtime leyo el token A, el administrador autorizo el B, y
    recien ahi llega el `invalid_grant` de A. B sigue vigente."""
    norte = intake_world["north-lab"]["id"]
    cifrador = _cifrador(_clave())
    _autorizar(conn, norte, cifrador, "token-A")
    leida_a = _leida(conn, norte, cifrador)
    _autorizar(conn, norte, cifrador, "token-B")

    with espacio(conn, norte) as cur:
        assert GC.marcar_reautorizacion(
            cur, "invalid_grant", leida_a.autorizada_en) == GC.CREDENCIAL_CAMBIO
    conn.commit()

    with espacio(conn, norte) as cur:
        assert GC.estado(cur) == "vigente"
        assert GC.leer(cur, cifrador=cifrador).secreto == "token-B"
    assert [e["tipo"] for e in _eventos(conn, norte)] == ["autorizada", "autorizada"]

    # Con lo que si leyo de B, marca.
    leida_b = _leida(conn, norte, cifrador)
    with espacio(conn, norte) as cur:
        assert GC.marcar_reautorizacion(
            cur, "invalid_grant", leida_b.autorizada_en) == GC.MARCADA


def test_recifrar_no_cambia_la_identidad_de_la_credencial_leida(intake_world, conn):
    """Rotar la clave no es una nueva autorizacion: quien leyo antes de rotar
    todavia puede marcar."""
    norte = intake_world["north-lab"]["id"]
    vieja, nueva = _clave(), _clave()
    _autorizar(conn, norte, _cifrador(vieja))
    leida = _leida(conn, norte, _cifrador(vieja))
    with admin(conn) as cur:
        GC.recifrar_todo(cur, _cifrador(nueva, vieja))
    conn.commit()
    with espacio(conn, norte) as cur:
        assert GC.marcar_reautorizacion(
            cur, "invalid_grant", leida.autorizada_en) == GC.MARCADA


@pytest.mark.parametrize("motivo", [
    "", "con espacios", "Mayusculas", 'invalid_grant: {"error": "x"}',
    "a" * 65, "acentuación",
])
def test_el_motivo_es_un_codigo_corto_saneado(intake_world, conn, motivo):
    norte = intake_world["north-lab"]["id"]
    cifrador = _cifrador(_clave())
    _autorizar(conn, norte, cifrador)
    cred = _leida(conn, norte, cifrador)
    with espacio(conn, norte) as cur:
        with pytest.raises(psycopg.errors.CheckViolation):
            GC.marcar_reautorizacion(cur, motivo, cred.autorizada_en)
    conn.rollback()
    assert [e["tipo"] for e in _eventos(conn, norte)] == ["autorizada"]


@contextlib.contextmanager
def _como_dueno(conn, workspace_id):
    """Como `prisma_owner` con el espacio fijado: el dueño de las funciones,
    para probar los disparadores sin pasar por ellas. Ni `prisma_app` ni
    `prisma_admin` tienen `insert` sobre estas tablas."""
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local role prisma_owner")
            cur.execute("select set_config('prisma.workspace_id', %s, true)",
                        (workspace_id,))
            yield cur


def test_la_base_rechaza_una_transicion_invalida_aunque_se_inserte_el_evento_directo(
        intake_world, conn):
    norte = intake_world["north-lab"]["id"]
    with _como_dueno(conn, norte) as cur:
        for tipo in ("reautorizacion_requerida", "revocada"):
            with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
                cur.execute(
                    "insert into credencial_google_evento "
                    "(workspace_id, tipo, motivo, actor_kind) "
                    "values (%s, %s, 'x', 'sistema')", (norte, tipo))


def test_la_proyeccion_no_se_escribe_con_update_directo(intake_world, conn):
    norte = intake_world["north-lab"]["id"]
    _autorizar(conn, norte, _cifrador(_clave()))
    with _como_dueno(conn, norte) as cur:
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            cur.execute(
                "update credencial_google_estado set estado = 'revocada' "
                "where workspace_id = %s", (norte,))


def test_prisma_admin_no_escribe_las_tablas_directo(intake_world, conn):
    """El camino de operación pasa por las funciones (que validan y emiten el
    evento): `prisma_admin` sólo lee estas tablas."""
    norte = intake_world["north-lab"]["id"]
    with admin(conn) as cur:
        for sentencia in (
            "insert into credencial_google_evento (workspace_id, tipo, motivo, actor_kind) "
            "values (%s, 'revocada', 'x', 'persona')",
            "update credencial_google_estado set estado = 'vigente' where workspace_id = %s",
            "delete from credencial_google where workspace_id = %s",
        ):
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                cur.execute(sentencia, (norte,))


# ---------------------------------------------------------------------------
# Aislamiento entre espacios
# ---------------------------------------------------------------------------


def test_un_espacio_no_lee_ni_marca_la_credencial_del_otro(intake_world, conn):
    norte = intake_world["north-lab"]["id"]
    oeste = intake_world["west-studio"]["id"]
    cifrador = _cifrador(_clave())
    _autorizar(conn, norte, cifrador, "secreto-norte")

    with espacio(conn, oeste) as cur:
        assert GC.estado(cur) == "sin_autorizar"
        assert GC.leer(cur, cifrador=cifrador) is None
        assert GC.marcar_reautorizacion(
            cur, "invalid_grant", AHORA) == GC.SIN_CAMBIO
        cur.execute("select * from leer_credencial_google()")
        assert cur.fetchall() == []
    conn.commit()

    with espacio(conn, norte) as cur:
        assert GC.estado(cur) == "vigente"
        assert GC.leer(cur, cifrador=cifrador).secreto == "secreto-norte"
    assert _eventos(conn, oeste) == []


def test_revocar_un_espacio_no_toca_al_otro(intake_world, conn):
    norte = intake_world["north-lab"]["id"]
    oeste = intake_world["west-studio"]["id"]
    cifrador = _cifrador(_clave())
    _autorizar(conn, norte, cifrador, "secreto-norte")
    _autorizar(conn, oeste, cifrador, "secreto-oeste")

    with admin(conn) as cur:
        assert GC.revocar(cur, norte, "revocada_por_administracion") is True
    conn.commit()

    with espacio(conn, oeste) as cur:
        assert GC.estado(cur) == "vigente"
        assert GC.leer(cur, cifrador=cifrador).secreto == "secreto-oeste"
    assert _crudo(conn, norte) is None
    assert _crudo(conn, oeste) is not None


def test_guardar_para_un_espacio_inexistente_falla_y_no_deja_nada(conn):
    inexistente = "00000000-0000-0000-0000-000000000000"
    with pytest.raises(psycopg.Error):
        with admin(conn) as cur:
            GC.guardar(cur, inexistente, "s", CUENTA, SCOPES,
                       cifrador=_cifrador(_clave()))
    conn.rollback()
    with admin(conn) as cur:
        cur.execute("select count(*) n from credencial_google")
        assert cur.fetchone()["n"] == 0


# ---------------------------------------------------------------------------
# Cifrado: la base nunca ve el texto plano
# ---------------------------------------------------------------------------


def test_lo_guardado_es_un_token_fernet_que_no_contiene_el_texto_plano(
        intake_world, conn):
    norte = intake_world["north-lab"]["id"]
    clave = _clave()
    secreto = "1//refresh-token-muy-secreto-de-prueba"
    _autorizar(conn, norte, _cifrador(clave), secreto)

    crudo = _crudo(conn, norte)
    assert secreto not in crudo
    assert Fernet(clave.encode("ascii")).decrypt(crudo.encode("ascii")) == \
        secreto.encode("utf-8")
    # Nada más en las tablas contiene el secreto, ni los eventos.
    with admin(conn) as cur:
        for tabla in TABLAS:
            cur.execute(f"select * from {tabla}")
            for fila in cur.fetchall():
                assert secreto not in json.dumps(fila, default=str)


def test_sin_clave_no_se_guarda_nada_y_el_error_es_el_tipado(
        intake_world, conn, monkeypatch):
    norte = intake_world["north-lab"]["id"]
    monkeypatch.delenv(cifrado.VARIABLE_CLAVE, raising=False)

    with pytest.raises(cifrado.ClaveCredencialesAusente):
        with admin(conn) as cur:
            GC.guardar(cur, norte, "secreto", CUENTA, SCOPES)
    conn.rollback()

    assert _crudo(conn, norte) is None
    assert _eventos(conn, norte) == []


def test_sin_clave_leer_no_devuelve_nada_sin_cifrar(intake_world, conn, monkeypatch):
    norte = intake_world["north-lab"]["id"]
    _autorizar(conn, norte, _cifrador(_clave()))
    monkeypatch.delenv(cifrado.VARIABLE_CLAVE, raising=False)

    with espacio(conn, norte) as cur:
        with pytest.raises(cifrado.ClaveCredencialesAusente):
            GC.leer(cur)


def test_leer_con_una_clave_que_no_descifra_falla_tipado_sin_filtrar(
        intake_world, conn):
    norte = intake_world["north-lab"]["id"]
    _autorizar(conn, norte, _cifrador(_clave()), "secreto-que-no-debe-salir")
    with espacio(conn, norte) as cur:
        with pytest.raises(cifrado.TokenNoDescifrable) as e:
            GC.leer(cur, cifrador=_cifrador(_clave()))
    assert "secreto-que-no-debe-salir" not in str(e.value) + repr(e.value)


def test_el_secreto_no_aparece_en_el_repr_de_la_credencial(intake_world, conn):
    norte = intake_world["north-lab"]["id"]
    cifrador = _cifrador(_clave())
    _autorizar(conn, norte, cifrador, "secreto-en-repr")
    with espacio(conn, norte) as cur:
        cred = GC.leer(cur, cifrador=cifrador)
    assert "secreto-en-repr" not in repr(cred) + str(cred)


def test_las_cuentas_y_scopes_se_validan_al_guardar(intake_world, conn):
    norte = intake_world["north-lab"]["id"]
    cifrador = _cifrador(_clave())
    with pytest.raises(psycopg.errors.CheckViolation):
        with admin(conn) as cur:
            GC.guardar(cur, norte, "s", "Prisma@Example.com", SCOPES, cifrador=cifrador)
    conn.rollback()
    with pytest.raises(psycopg.errors.CheckViolation):
        with admin(conn) as cur:
            GC.guardar(cur, norte, "s", CUENTA, (), cifrador=cifrador)
    conn.rollback()
    assert _crudo(conn, norte) is None


class _CursorFalso:
    def __init__(self, fila):
        self._fila = fila

    def execute(self, *a, **k):
        pass

    def fetchone(self):
        return self._fila


def test_un_estado_desconocido_falla_cerrado_en_vez_de_devolverse():
    with pytest.raises(GC.EstadoDesconocido):
        GC.estado(_CursorFalso({"estado": "algo_nuevo"}))
    fila = {"token_cifrado": "x", "cuenta_email": CUENTA, "scopes": ["a"],
            "estado": "algo_nuevo", "autorizado_en": AHORA}
    with pytest.raises(GC.EstadoDesconocido):
        GC.leer(_CursorFalso(fila), cifrador=_cifrador(_clave()))


# ---------------------------------------------------------------------------
# Configuración por espacio: apagado por defecto, cerrada ante lo corrupto
# ---------------------------------------------------------------------------


def _guardar_setting(conn, workspace_id, clave, valor_json):
    with admin(conn) as cur:
        cur.execute(
            """insert into workspace_setting (workspace_id, clave, valor)
               values (%s, %s, %s::jsonb)
               on conflict (workspace_id, clave) do update set valor = excluded.valor""",
            (workspace_id, clave, valor_json))
    conn.commit()


def _incidentes_config(conn, workspace_id):
    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from incident where workspace_id = %s "
            "and etapa = 'google_config_invalida'", (workspace_id,))
        return cur.fetchone()["n"]


def test_una_configuracion_corrupta_usa_la_etapa_y_el_aviso_de_google_no_los_del_correo(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    _guardar_setting(conn, ws, GC.CLAVE_HABILITADO, "1")
    with espacio(conn, ws) as cur:
        assert GC.habilitado(cur, ws) is False
    conn.commit()
    with admin(conn) as cur:
        cur.execute("select etapa from incident where workspace_id = %s", (ws,))
        assert [f["etapa"] for f in cur.fetchall()] == ["google_config_invalida"]
        cur.execute("select tipo from aviso_administrativo where workspace_id = %s",
                    (ws,))
        assert [f["tipo"] for f in cur.fetchall()] == [
            "google_config_invalida:google.habilitado"]


def test_las_claves_de_configuracion_tienen_los_nombres_acordados():
    assert GC.CLAVE_HABILITADO == "google.habilitado"
    assert GC.CLAVE_SCOPES == "google.scopes_habilitados"


def test_google_esta_apagado_y_sin_scopes_por_defecto(intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        assert GC.habilitado(cur, ws) is False
        assert GC.scopes_habilitados(cur, ws) == ()
    conn.commit()
    assert _incidentes_config(conn, ws) == 0


def test_habilitado_lee_el_booleano_del_propio_espacio(intake_world, conn):
    norte = intake_world["north-lab"]["id"]
    oeste = intake_world["west-studio"]["id"]
    _guardar_setting(conn, norte, GC.CLAVE_HABILITADO, "true")

    with espacio(conn, norte) as cur:
        assert GC.habilitado(cur, norte) is True
    with espacio(conn, oeste) as cur:
        assert GC.habilitado(cur, oeste) is False
    # Una conexión de administración ve todos los espacios: el filtro
    # explícito evita leer la clave de otro.
    with admin(conn) as cur:
        assert GC.habilitado(cur, oeste) is False
        assert GC.habilitado(cur, norte) is True

    _guardar_setting(conn, norte, GC.CLAVE_HABILITADO, "false")
    with espacio(conn, norte) as cur:
        assert GC.habilitado(cur, norte) is False


@pytest.mark.parametrize("valor", ["1", '"true"', "[true]", '{"on": true}', "null"])
def test_una_clave_corrupta_nunca_enciende_google(intake_world, conn, valor):
    ws = intake_world["north-lab"]["id"]
    _guardar_setting(conn, ws, GC.CLAVE_HABILITADO, valor)

    with espacio(conn, ws) as cur:
        assert GC.habilitado(cur, ws) is False
    conn.commit()
    assert _incidentes_config(conn, ws) == 1


def test_los_scopes_habilitados_se_leen_como_tupla_de_textos(intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    _guardar_setting(conn, ws, GC.CLAVE_SCOPES,
                     json.dumps(["gmail.send", "calendar.events"]))
    with espacio(conn, ws) as cur:
        assert GC.scopes_habilitados(cur, ws) == ("gmail.send", "calendar.events")

    _guardar_setting(conn, ws, GC.CLAVE_SCOPES, "[]")
    with espacio(conn, ws) as cur:
        assert GC.scopes_habilitados(cur, ws) == ()
    conn.commit()
    assert _incidentes_config(conn, ws) == 0


@pytest.mark.parametrize("valor", [
    '"gmail.send"', "[1, 2]", '{"a": 1}', '["ok", 2]', "null", "true", '[""]'])
def test_scopes_corruptos_se_leen_como_ninguno(intake_world, conn, valor):
    ws = intake_world["north-lab"]["id"]
    _guardar_setting(conn, ws, GC.CLAVE_SCOPES, valor)
    with espacio(conn, ws) as cur:
        assert GC.scopes_habilitados(cur, ws) == ()
    conn.commit()
    assert _incidentes_config(conn, ws) == 1


def test_una_configuracion_corrupta_deja_un_solo_incidente_aunque_se_lea_muchas_veces(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    _guardar_setting(conn, ws, GC.CLAVE_HABILITADO, "1")
    for _ in range(3):
        with espacio(conn, ws) as cur:
            GC.habilitado(cur, ws)
        conn.commit()
    assert _incidentes_config(conn, ws) == 1


# ---------------------------------------------------------------------------
# Re-cifrado: `python -m prisma google recifrar`
# ---------------------------------------------------------------------------


class _ConexionEspia:
    """Delega en la conexion de la prueba, pero registra `close`/`rollback`
    sin cerrar la conexion compartida."""

    def __init__(self, real):
        self._real = real
        self.cerrada = False
        self.rollbacks = 0

    def close(self):
        self.cerrada = True

    def rollback(self):
        self.rollbacks += 1
        self._real.rollback()

    def __getattr__(self, nombre):
        return getattr(self._real, nombre)


@pytest.fixture
def cli_con_base(conn, monkeypatch):
    llamadas = []

    def conectar(*a, **k):
        llamadas.append(1)
        return _ConexionEspia(conn)

    monkeypatch.setattr(cli, "conectar", conectar)
    return llamadas


def test_recifrar_pasa_todo_a_la_clave_vigente(intake_world, conn, cli_con_base,
                                               monkeypatch, capsys):
    norte = intake_world["north-lab"]["id"]
    oeste = intake_world["west-studio"]["id"]
    vieja, nueva = _clave(), _clave()
    _autorizar(conn, norte, _cifrador(vieja), "secreto-norte")
    _autorizar(conn, oeste, _cifrador(vieja), "secreto-oeste")
    antes = (_crudo(conn, norte), _crudo(conn, oeste))

    monkeypatch.setenv(cifrado.VARIABLE_CLAVE, f"{nueva},{vieja}")
    assert cli.main(["google", "recifrar"]) == 0
    salida = capsys.readouterr().out

    assert (_crudo(conn, norte), _crudo(conn, oeste)) != antes
    solo_nueva = _cifrador(nueva)
    with espacio(conn, norte) as cur:
        assert GC.leer(cur, cifrador=solo_nueva).secreto == "secreto-norte"
    with espacio(conn, oeste) as cur:
        assert GC.leer(cur, cifrador=solo_nueva).secreto == "secreto-oeste"
    assert salida.splitlines() == [
        "Credenciales re-cifradas con la clave vigente: 2."]
    # Re-cifrar no es un cambio de estado: no emite eventos.
    assert [e["tipo"] for e in _eventos(conn, norte)] == ["autorizada"]


def test_recifrar_sin_credenciales_termina_bien(intake_world, conn, cli_con_base,
                                                monkeypatch, capsys):
    monkeypatch.setenv(cifrado.VARIABLE_CLAVE, _clave())
    assert cli.main(["google", "recifrar"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "No hay credenciales de Google guardadas."]


def test_recifrar_sin_clave_no_cambia_nada_ni_abre_la_base(
        intake_world, conn, cli_con_base, monkeypatch, capsys):
    norte = intake_world["north-lab"]["id"]
    _autorizar(conn, norte, _cifrador(_clave()), "secreto-norte")
    antes = _crudo(conn, norte)
    monkeypatch.delenv(cifrado.VARIABLE_CLAVE, raising=False)

    assert cli.main(["google", "recifrar"]) != 0
    salida = capsys.readouterr().out

    assert cifrado.VARIABLE_CLAVE in salida
    assert "Revisá" in salida
    assert _crudo(conn, norte) == antes
    assert cli_con_base == []


def test_recifrar_con_una_clave_invalida_no_cambia_nada(
        intake_world, conn, cli_con_base, monkeypatch, capsys):
    norte = intake_world["north-lab"]["id"]
    _autorizar(conn, norte, _cifrador(_clave()), "secreto-norte")
    antes = _crudo(conn, norte)
    monkeypatch.setenv(cifrado.VARIABLE_CLAVE, "esto-no-es-una-clave-SECRETO123")

    assert cli.main(["google", "recifrar"]) != 0
    salida = capsys.readouterr().out

    assert "SECRETO123" not in salida
    assert _crudo(conn, norte) == antes
    assert cli_con_base == []


def test_recifrar_informa_los_que_ninguna_clave_descifra_sin_contenido(
        intake_world, conn, cli_con_base, monkeypatch, capsys):
    norte = intake_world["north-lab"]["id"]
    oeste = intake_world["west-studio"]["id"]
    perdida, vieja, nueva = _clave(), _clave(), _clave()
    _autorizar(conn, norte, _cifrador(perdida), "secreto-norte")
    _autorizar(conn, oeste, _cifrador(vieja), "secreto-oeste")
    crudo_norte = _crudo(conn, norte)

    monkeypatch.setenv(cifrado.VARIABLE_CLAVE, f"{nueva},{vieja}")
    assert cli.main(["google", "recifrar"]) != 0
    salida = capsys.readouterr().out

    # Se informa por slug, sin ningún contenido.
    assert "north-lab" in salida
    assert "west-studio" not in salida
    assert crudo_norte not in salida
    assert "secreto" not in salida
    # Lo ilegible queda intacto; lo demás sí se re-cifró.
    assert _crudo(conn, norte) == crudo_norte
    with espacio(conn, oeste) as cur:
        assert GC.leer(cur, cifrador=_cifrador(nueva)).secreto == "secreto-oeste"


def test_reemplazar_token_no_pisa_una_credencial_que_cambio_en_el_medio(
        intake_world, conn):
    """El re-cifrado lee y escribe en pasos distintos: si mientras tanto se
    volvió a autorizar, el reemplazo por comparación no debe pisar lo nuevo."""
    norte = intake_world["north-lab"]["id"]
    cifrador = _cifrador(_clave())
    _autorizar(conn, norte, cifrador, "secreto-1")
    leido = _crudo(conn, norte)
    _autorizar(conn, norte, cifrador, "secreto-2")
    vigente = _crudo(conn, norte)

    with admin(conn) as cur:
        cur.execute("select reemplazar_token_google(%s::uuid, %s, %s) ok",
                    (norte, leido, cifrador.rotar(leido).decode("ascii")))
        assert cur.fetchone()["ok"] is False
    conn.commit()
    assert _crudo(conn, norte) == vigente


class _CifradorQueInterviene:
    """Un cifrador que, al rotar, hace `intervencion()`: simula que la
    credencial cambio entre que se listo y que se reemplazo."""

    def __init__(self, real, intervencion):
        self._real = real
        self._intervencion = intervencion

    def rotar(self, token):
        self._intervencion()
        return self._real.rotar(token)


def test_recifrar_todo_cuenta_las_que_cambiaron_mientras_se_rotaba(intake_world, conn):
    norte = intake_world["north-lab"]["id"]
    oeste = intake_world["west-studio"]["id"]
    vieja, nueva = _clave(), _clave()
    _autorizar(conn, norte, _cifrador(vieja), "secreto-norte")
    _autorizar(conn, oeste, _cifrador(vieja), "secreto-oeste")
    reautorizada = _cifrador(vieja)

    with admin(conn) as cur:
        hecho = []

        def cambia_norte():
            # Sólo la primera vez (norte va primero, por slug).
            if not hecho:
                hecho.append(1)
                GC.guardar(cur, norte, "secreto-nuevo", CUENTA, SCOPES,
                           cifrador=reautorizada)

        r = GC.recifrar_todo(
            cur, _CifradorQueInterviene(_cifrador(nueva, vieja), cambia_norte))
    conn.commit()

    assert r.recifradas == 1
    assert r.cambiadas == ("north-lab",)
    assert r.ilegibles == ()
    # Lo nuevo de norte no se pisó.
    with espacio(conn, norte) as cur:
        assert GC.leer(cur, cifrador=reautorizada).secreto == "secreto-nuevo"


def test_recifrar_informa_las_que_cambiaron_y_falla_aunque_sean_todas(
        intake_world, conn, cli_con_base, monkeypatch, capsys):
    norte = intake_world["north-lab"]["id"]
    vieja, nueva = _clave(), _clave()
    _autorizar(conn, norte, _cifrador(vieja), "secreto-norte")
    real = cifrado.desde_texto(f"{nueva},{vieja}")

    def revoca_en_el_medio():
        with conn.cursor() as c:
            c.execute("select revocar_credencial_google(%s::uuid, 'x_y')", (norte,))

    monkeypatch.setattr(
        cifrado, "cargar", lambda: _CifradorQueInterviene(real, revoca_en_el_medio))
    assert cli.main(["google", "recifrar"]) == 1
    salida = capsys.readouterr().out

    assert salida.splitlines() == [
        "Credenciales re-cifradas con la clave vigente: 0.",
        "Cambiaron mientras se rotaba 1 credencial(es); no se re-cifraron:",
        "  north-lab",
        "Volvé a correr `python -m prisma google recifrar` para terminarlas.",
    ]
    assert "No hay credenciales" not in salida
    assert "secreto" not in salida


def test_recifrar_cierra_la_conexion_al_terminar_bien(
        intake_world, conn, monkeypatch):
    espia = _ConexionEspia(conn)
    monkeypatch.setattr(cli, "conectar", lambda *a, **k: espia)
    monkeypatch.setenv(cifrado.VARIABLE_CLAVE, _clave())
    assert cli.main(["google", "recifrar"]) == 0
    assert espia.cerrada


def test_recifrar_cierra_la_conexion_y_deshace_si_algo_falla(
        intake_world, conn, monkeypatch):
    espia = _ConexionEspia(conn)
    monkeypatch.setattr(cli, "conectar", lambda *a, **k: espia)
    monkeypatch.setenv(cifrado.VARIABLE_CLAVE, _clave())

    def falla(cur, cifrador):
        raise RuntimeError("falla de prueba")

    monkeypatch.setattr(GC, "recifrar_todo", falla)
    with pytest.raises(RuntimeError):
        cli.main(["google", "recifrar"])
    assert espia.cerrada
    assert espia.rollbacks >= 1
