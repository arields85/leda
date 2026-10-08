"""La credencial de la página de una tarea (ADR 0019, decisión 7; migración 0036).

Un enlace personal abre una página de sólo lectura con una tarea, su historia y su evidencia.
Ese enlace **es una credencial**, hermana de la del tablero (`tablero.py`), con las mismas
reglas y una diferencia, decidida por el usuario: no vence (ADR 0019, decisión 1).

- **Sólo se guarda el hash.** El valor en claro viaja una vez, en el mensaje que lo lleva, y no
  queda en la base, ni en la salida, ni en el registro de turnos: lo emite el despachador al
  mandar (`despachador.py`).
- **El espacio y la tarea salen del token, nunca de la URL.** La dirección lleva el token y,
  para un archivo, el id de su evidencia: la base comprueba que esa evidencia sea de la tarea
  del token, así que cambiar el id no abre nada de otra tarea ni de otro espacio.
- **Lo acota, sin vencimiento,** que el derecho a ver la tarea se revalida en cada pedido (ver
  `puede_ver_tarea` en `db/esquema.sql`: el responsable, quien aprueba su trabajo y quien ya
  decidió sobre ella, el referente del área y la autoridad final del espacio), y que la
  administración puede revocarlo (`acceso_tarea.revocado_en`).
- **La regla de quién ve qué vive en SQL**, en funciones `security definer` con dueño
  `leda_owner`: este módulo no filtra nada, sólo pasa el hash.

Un token inexistente, revocado o de alguien que ya no puede ver la tarea devuelven lo mismo,
`None`: distinguirlos le diría a quien prueba enlaces cuáles existieron.
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from typing import Any

# El camino de la página, después de la dirección pública (`config.base_url`).
CAMINO = "/tarea/"
# Lo más largo que puede ser un enlace sin la dirección pública: el camino y el token
# (`secrets.token_urlsafe(32)` da 43 caracteres). La salida le reserva ese lugar al texto que
# lo va a llevar (`salida.enqueue_outbox`, `enlace_de_tarea`).
LARGO_DEL_TOKEN = 43


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def emitir(cur, membership_id: str, task_id: str) -> str | None:
    """Emite un enlace de `membership_id` a la tarea `task_id` y devuelve el token en claro, o
    `None` si esa persona no puede ver la tarea (o no es del espacio de la transacción). La
    base guarda sólo el hash: si el token se pierde, se emite otro."""
    token = secrets.token_urlsafe(32)
    cur.execute("select emitir_acceso_tarea(%s, %s, %s) as id",
                (str(membership_id), str(task_id), _hash(token)))
    fila = cur.fetchone()
    return token if fila and fila["id"] is not None else None


def enlace(base_url: str, token: str) -> str:
    """La dirección de la página para un token, sobre la dirección pública configurada."""
    return f"{base_url.rstrip('/')}{CAMINO}{token}"


def leer(cur, token: str) -> dict[str, Any] | None:
    """Lo que muestra la página de un token (la tarea, su historia, su evidencia y lo que pide
    la política), o `None`. Cada lectura queda registrada (ADR 0019, 7e)."""
    if not token:
        return None
    cur.execute("select leer_pagina_de_tarea(%s) as datos", (_hash(token),))
    fila = cur.fetchone()
    return fila["datos"] if fila else None


def leer_archivo(cur, token: str, evidence_id: str) -> dict[str, Any] | None:
    """El archivo de una evidencia de la tarea del token (contenido, tipo detectado, clase y
    nombre), o `None` si el token no sirve, la evidencia no es de esa tarea, no tiene archivo o
    se retiró. Cada descarga queda registrada."""
    try:
        evidencia = str(uuid.UUID(str(evidence_id)))
    except ValueError:
        return None
    if not token:
        return None
    cur.execute(
        """select archivo_contenido, archivo_tipo, archivo_clase, archivo_nombre
             from leer_archivo_de_tarea(%s, %s)""", (_hash(token), evidencia))
    fila = cur.fetchone()
    if fila is None:
        return None
    return {"contenido": bytes(fila["archivo_contenido"]), "tipo": fila["archivo_tipo"],
            "clase": fila["archivo_clase"], "nombre": fila["archivo_nombre"]}
