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
  administración puede revocarlo (`acceso_tarea.revocado_en`; `revocar`, abajo).
- **El administrador de plataforma** (ADR 0019, 7b; porción 5) tiene su propio enlace, atado a
  su usuario de plataforma y a una tarea de un espacio, que pide por el bot de administración
  (`leda.motor.administracion`); vale mientras tenga el rol y cada vista suya queda además en
  `audit_log`, con la versión del núcleo que esta capa le pasa a la base
  (`leda.nucleo_hash`). La administración también retira el contenido de una pieza
  (`retirar_contenido`): la página dice "retirado por la administración".
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


def _con_la_version_del_nucleo(cur) -> None:
    """La versión de las reglas del núcleo, para la auditoría de una vista de un administrador
    (constitución §12): la base no lee los archivos del núcleo. Local a la transacción."""
    from . import versiones

    cur.execute("select set_config('leda.nucleo_hash', %s, true)", (versiones.nucleo_hash(),))


def leer(cur, token: str) -> dict[str, Any] | None:
    """Lo que muestra la página de un token (la tarea, su historia, su evidencia y lo que pide
    la política), o `None`. Cada lectura queda registrada (ADR 0019, 7e)."""
    if not token:
        return None
    _con_la_version_del_nucleo(cur)
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
    _con_la_version_del_nucleo(cur)
    cur.execute(
        """select archivo_contenido, archivo_tipo, archivo_clase, archivo_nombre
             from leer_archivo_de_tarea(%s, %s)""", (_hash(token), evidencia))
    fila = cur.fetchone()
    if fila is None:
        return None
    return {"contenido": bytes(fila["archivo_contenido"]), "tipo": fila["archivo_tipo"],
            "clase": fila["archivo_clase"], "nombre": fila["archivo_nombre"]}


# --- La administración de plataforma (ADR 0019, decisiones 3 y 7; porción 5 de la C-3) --------
#
# Corren bajo la conexión administrativa (`db.admin`), nunca bajo la de un espacio: el sombrero
# lo define el canal (constitución §2). Lo que hacen queda en `audit_log` (constitución §12).

def es_administrador(cur, app_user_id: str) -> bool:
    """Si el usuario tiene hoy el rol de administrador de plataforma."""
    cur.execute("""select 1 from platform_role
                    where app_user_id = %s and rol = 'administrador'""", (str(app_user_id),))
    return cur.fetchone() is not None


def _auditar(cur, workspace_id: str, accion: str, **campos: Any) -> None:
    from . import versiones
    from .db import registrar_auditoria

    registrar_auditoria(cur, accion=accion, workspace_id=str(workspace_id),
                        pack_hash=versiones.pack_hash(cur, str(workspace_id)),
                        nucleo_hash=versiones.nucleo_hash(), **campos)


def emitir_para_administrador(cur, admin_app_user_id: str, workspace_id: str,
                              task_id: str) -> str | None:
    """Emite el enlace de un administrador de plataforma a una tarea de un espacio (ADR 0019,
    7b): atado a su usuario de plataforma, no a una membresía, y auditado. Devuelve el token en
    claro, o `None` si no es administrador o la tarea no es de ese espacio. La base guarda sólo
    el hash y revalida el rol en cada pedido (`acceso_tarea_vigente`); cada vista suya queda en
    `audit_log`."""
    if not es_administrador(cur, admin_app_user_id):
        return None
    cur.execute("select 1 from task where id = %s and workspace_id = %s",
                (str(task_id), str(workspace_id)))
    if cur.fetchone() is None:
        return None
    token = secrets.token_urlsafe(32)
    cur.execute(
        """insert into acceso_tarea (workspace_id, admin_app_user_id, task_id, token_hash)
           values (%s, %s, %s, %s) returning id""",
        (str(workspace_id), str(admin_app_user_id), str(task_id), _hash(token)))
    acceso = str(cur.fetchone()["id"])
    _auditar(cur, workspace_id, "emitir_acceso_tarea_de_administrador",
             actor_app_user_id=str(admin_app_user_id), actor_kind="persona",
             sujeto_tipo="task", sujeto_id=str(task_id), detalle={"acceso_tarea_id": acceso})
    return token


# De qué son los enlaces que se revocan: la columna de `acceso_tarea` y el sujeto auditado.
_REVOCAR = {"persona": ("membership_id", "membership"), "tarea": ("task_id", "task"),
            "administrador": ("admin_app_user_id", "app_user")}


def revocar(cur, workspace_id: str, *, membership_id: str | None = None,
            task_id: str | None = None, admin_app_user_id: str | None = None) -> int:
    """Revoca los enlaces vigentes de una persona, de una tarea o de un administrador de
    plataforma, en un espacio (ADR 0019, 7a), y devuelve cuántos. Un enlace ya mandado deja de
    abrir: la base lo mira en cada pedido. Exactamente un criterio. Sólo lo que de verdad se
    revocó queda auditado."""
    dados = {de: valor for de, valor in (("persona", membership_id), ("tarea", task_id),
                                         ("administrador", admin_app_user_id)) if valor}
    if len(dados) != 1:
        raise ValueError("revocar pide exactamente uno: persona, tarea o administrador")
    [(de, valor)] = dados.items()
    columna, sujeto = _REVOCAR[de]
    cur.execute(
        f"""update acceso_tarea set revocado_en = now()
             where workspace_id = %s and {columna} = %s and revocado_en is null""",
        (str(workspace_id), str(valor)))
    cantidad = cur.rowcount
    if cantidad:
        _auditar(cur, workspace_id, "revocar_enlaces_de_tarea", actor_kind="sistema",
                 sujeto_tipo=sujeto, sujeto_id=str(valor),
                 detalle={"de": de, "cantidad": cantidad})
    return cantidad


def retirar_contenido(cur, workspace_id: str, evidence_id: str, admin_app_user_id: str,
                      motivo: str) -> list[str]:
    """El retiro del contenido de una pieza de evidencia por la administración (ADR 0019,
    decisión 3): la pieza y su archivo no se borran; la página dice "retirado por la
    administración" y nunca su contenido, y el archivo no se sirve. Un archivo se guarda una vez
    por huella, así que se retiran también las otras piezas del espacio con el mismo archivo.
    Devuelve las piezas que se retiraron ahora (una ya retirada por la administración no se
    vuelve a retirar). Queda en `audit_log` con quién y por qué.

    `ValueError` si quien lo hace no es administrador de plataforma, si falta el motivo o si la
    pieza no es de ese espacio."""
    if not es_administrador(cur, admin_app_user_id):
        raise ValueError("sólo un administrador de plataforma retira contenido")
    if not (motivo or "").strip():
        raise ValueError("falta el motivo")
    cur.execute("select archivo_id from evidence where id = %s and workspace_id = %s",
                (str(evidence_id), str(workspace_id)))
    fila = cur.fetchone()
    if fila is None:
        raise ValueError("esa pieza no es de este espacio")
    piezas = [str(evidence_id)]
    if fila["archivo_id"] is not None:
        cur.execute("""select id from evidence
                        where workspace_id = %s and archivo_id = %s and id <> %s
                        order by at, id""",
                    (str(workspace_id), fila["archivo_id"], str(evidence_id)))
        piezas += [str(f["id"]) for f in cur.fetchall()]
    retiradas = []
    for pieza in piezas:
        cur.execute(
            """insert into evidencia_retirada (workspace_id, evidence_id,
                                               retirada_por_app_user_id, motivo, at)
               values (%s, %s, %s, %s, clock_timestamp())
               on conflict do nothing returning id""",
            (str(workspace_id), pieza, str(admin_app_user_id), motivo.strip()))
        if cur.fetchone() is not None:
            retiradas.append(pieza)
    if retiradas:
        _auditar(cur, workspace_id, "retirar_contenido_de_evidencia",
                 actor_app_user_id=str(admin_app_user_id), actor_kind="persona",
                 sujeto_tipo="evidence", sujeto_id=str(evidence_id),
                 detalle={"motivo": motivo.strip(), "piezas": retiradas})
    return retiradas
