"""Acceso a la base.

No hay ORM a propósito. El esquema es la fuente de verdad y buena parte de las
reglas viven en disparadores y funciones; duplicar las tablas en clases de
Python sólo agregaría una copia que se desincroniza.

Lo importante de este módulo es `espacio()`: abre una transacción con el rol
`leda_app` y el espacio activo declarado, y a partir de ahí el aislamiento
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
    conn.execute("set search_path = leda, public")
    return conn


def conectar_autoridad(url: str) -> psycopg.Connection:
    """Dedicated connection whose transactions are bounded by autoridad()."""
    conn = psycopg.connect(url, row_factory=dict_row)
    conn.execute("set search_path = leda, public")
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
            cur.execute("set local role leda_app")
            cur.execute("select set_config('leda.workspace_id', %s, true)",
                        (workspace_id,))
            yield cur


def atar_al_entrante(cur: psycopg.Cursor, entrante_id: str | None) -> None:
    """Todo lo que esta transacción encole en `message_outbox` queda atado al
    mensaje entrante `entrante_id` (T9-R2, migración 0021): el valor por
    omisión de `entrante_id` lee esta configuración local, así que el control de
    "una respuesta por mensaje" ve lo encolado para ese mensaje sin que cada
    `insert` lo pase, incluso los de las funciones de la base. Local a la
    transacción: se va con el commit o el rollback."""
    if entrante_id:
        cur.execute("select set_config('leda.entrante_id', %s, true)",
                    (str(entrante_id),))


@contextlib.contextmanager
def admin(conn: psycopg.Connection) -> Iterator[psycopg.Cursor]:
    """Transacción de administración: ve todos los espacios.

    Sólo la usan el importador de packs y la consola. Nunca el agente
    conversacional.
    """
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local role leda_admin")
            yield cur


@contextlib.contextmanager
def autoridad(conn: psycopg.Connection) -> Iterator[psycopg.Cursor]:
    """Dedicated boundary for task commitment authority.

    This connection must use LEDA_AUTHORITY_DB_URL. The application role has
    no EXECUTE privilege on the commitment function.
    """
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local role leda_gateway")
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
            cur.execute("set local role leda_app")
            yield cur


def registrar_auditoria(
    cur: psycopg.Cursor,
    *,
    accion: str,
    workspace_id: str | None = None,
    actor_app_user_id: str | None = None,
    actor_kind: str = "leda",
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
