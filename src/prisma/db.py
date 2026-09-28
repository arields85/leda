"""Acceso a la base.

No hay ORM a propósito. El esquema es la fuente de verdad y buena parte de las
reglas viven en disparadores y funciones; duplicar las tablas en clases de
Python sólo agregaría una copia que se desincroniza.

Lo importante de este módulo es `espacio()`: abre una transacción con el rol
`prisma_app` y el espacio activo declarado, y a partir de ahí el aislamiento
entre equipos lo garantiza PostgreSQL, no el cuidado de quien escribe la
consulta.
"""

from __future__ import annotations

import contextlib
from collections.abc import Iterator
from typing import Any

import psycopg
from psycopg.rows import dict_row

from .config import config


def conectar(url: str | None = None) -> psycopg.Connection:
    conn = psycopg.connect(url or config.db_url, row_factory=dict_row)
    conn.execute("set search_path = prisma, public")
    # Sin este commit, la conexión queda "en transacción" desde el primer
    # `execute` (autocommit=False): el próximo `espacio()`/`admin()` no abre
    # una transacción real, sino un savepoint anidado dentro de ésta, que
    # nunca se confirma sola al salir limpio (Tanda 1, G1e, caso 16 --
    # "reinicio": una conexión nueva que sólo procesa un `/start pv_{token}`
    # -- `resolver_verificacion_correo`, que depende explícitamente de que
    # `espacio()` confirme sola -- dejaba la verificación sin persistir
    # hasta que algún commit posterior, ajeno, la arrastrara consigo; si el
    # proceso caía antes, la persona ya había recibido "✅ ... quedó
    # verificado" sin que quedara ningún recibo real en la base). Mismo
    # patrón que ya usa `conectar_autoridad()` acá abajo.
    conn.commit()
    return conn


def conectar_autoridad(url: str) -> psycopg.Connection:
    """Dedicated connection whose transactions are bounded by autoridad()."""
    conn = psycopg.connect(url, row_factory=dict_row)
    conn.execute("set search_path = prisma, public")
    conn.commit()
    return conn


@contextlib.contextmanager
def espacio(conn: psycopg.Connection, workspace_id: str) -> Iterator[psycopg.Cursor]:
    """Transacción acotada a un espacio de trabajo.

    Dentro de este bloque, cualquier consulta a las tablas por espacio devuelve
    únicamente filas de `workspace_id`. Es RLS, no un WHERE que hay que
    acordarse de poner.
    """
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local role prisma_app")
            cur.execute("select set_config('prisma.workspace_id', %s, true)",
                        (workspace_id,))
            yield cur


@contextlib.contextmanager
def admin(conn: psycopg.Connection) -> Iterator[psycopg.Cursor]:
    """Transacción de administración: ve todos los espacios.

    Sólo la usan el importador de packs y la consola. Nunca el agente
    conversacional.
    """
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local role prisma_admin")
            yield cur


@contextlib.contextmanager
def autoridad(conn: psycopg.Connection) -> Iterator[psycopg.Cursor]:
    """Dedicated boundary for task commitment authority.

    This connection must use PRISMA_AUTHORITY_DB_URL. The application role has
    no EXECUTE privilege on the commitment function.
    """
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local role prisma_gateway")
            yield cur


@contextlib.contextmanager
def sin_espacio(conn: psycopg.Connection) -> Iterator[psycopg.Cursor]:
    """Antes de saber a qué espacio pertenece el pedido.

    Existe para un solo caso: resolver una credencial que todavía no dijo de
    qué espacio es. Llega un token del tablero y averiguar su espacio es
    justamente lo que falta hacer, así que no se puede abrir `espacio()`.

    Dentro de este bloque **no hay espacio fijado**, de modo que la política
    de aislamiento no deja ver ninguna fila con alcance de espacio. Lo único
    que se puede hacer acá es llamar a la función acotada que resuelve el
    token. Cualquier otra consulta va a devolver vacío, y eso es deliberado.
    """
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local role prisma_app")
            yield cur


def registrar_auditoria(
    cur: psycopg.Cursor,
    *,
    accion: str,
    workspace_id: str | None = None,
    actor_app_user_id: str | None = None,
    actor_kind: str = "prisma",
    sujeto_tipo: str | None = None,
    sujeto_id: str | None = None,
    detalle: dict[str, Any] | None = None,
    pack_hash: str | None = None,
    nucleo_hash: str | None = None,
) -> None:
    import json

    cur.execute(
        """
        insert into audit_log (workspace_id, actor_app_user_id, actor_kind,
                               accion, sujeto_tipo, sujeto_id, detalle,
                               pack_hash, nucleo_hash)
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (workspace_id, actor_app_user_id, actor_kind, accion, sujeto_tipo,
         sujeto_id, json.dumps(detalle or {}), pack_hash, nucleo_hash),
    )
