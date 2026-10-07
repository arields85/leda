"""La versión de las reglas con que se hizo algo (Constitución §12).

Toda acción con efecto queda auditada con la versión de las reglas del núcleo
(`nucleo_hash`) y del pack del espacio (`pack_hash`). Antes la calculaba
`contexto.py`, para armar las instrucciones de la IA, y la pasaba `agente.py` a
la auditoría; los dos se borraron con los flujos A y B (E3-4). Vive acá para que
la use cualquiera que audite, sin depender de cómo conversa Leda.
"""

from __future__ import annotations

import hashlib
from functools import lru_cache

import psycopg

from .config import config

# Los archivos del núcleo que entran en la huella, en este orden. Son los mismos
# que entraban en `contexto._nucleo`, así que la huella no cambió.
ARCHIVOS_DEL_NUCLEO = ("constitucion.md", "mecanica-pm.md")


@lru_cache(maxsize=1)
def nucleo_hash() -> str:
    """La huella de las reglas del núcleo, una vez por proceso: el núcleo no se
    cambia en caliente (Constitución, preámbulo). Si falta un archivo, falla: una
    huella sobre un núcleo ausente registraría una versión que no existe."""
    partes = []
    for nombre in ARCHIVOS_DEL_NUCLEO:
        ruta = config.nucleo / nombre
        if not ruta.exists():
            raise FileNotFoundError(f"falta el archivo del núcleo {nombre}")
        partes.append(ruta.read_text(encoding="utf-8"))
    return hashlib.sha256("\n\n".join(partes).encode("utf-8")).hexdigest()


def pack_hash(cur: psycopg.Cursor, workspace_id: str | None) -> str | None:
    """La huella del pack vigente del espacio, o `None` si no tiene ninguno
    importado (o si la operación no es de un espacio)."""
    if workspace_id is None:
        return None
    cur.execute(
        """select pack_hash from workspace_version
            where workspace_id = %s order by version desc limit 1""",
        (workspace_id,))
    fila = cur.fetchone()
    return fila["pack_hash"] if fila else None
