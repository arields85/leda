"""Credencial de acceso al tablero.

Una persona pide el tablero por Telegram y recibe un enlace personal. Ese
enlace **es una credencial**: quien lo tenga ve los datos de ese espacio.

Tres propiedades lo acotan, y las tres viven en la base, no acá:

- **Sólo se guarda el hash.** El valor en claro viaja una vez, en el enlace, y
  no queda persistido en ninguna parte. Si se filtrara la base, los enlaces
  emitidos no servirían.
- **Vence.** La ventana acota el daño de un reenvío o de un historial; no lo
  evita. Cuánto dura es configuración del cliente, no una constante del
  producto: sale de `workspace_setting` y un administrador podrá cambiarla.
- **El espacio sale del token, nunca de la URL.** Una dirección con el espacio
  adentro sería confiarle a quien llama el dato que lo aísla, que es
  exactamente lo que la regla 1 de la frontera prohíbe.

La membresía se revalida en cada resolución: tener un token vigente no alcanza
si la persona ya no está en el equipo.
"""

from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timedelta

CLAVE_VIGENCIA = "tablero.minutos_de_vigencia"
MINUTOS_POR_DEFECTO = 30


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def minutos_de_vigencia(cur) -> int:
    """Cuánto dura un enlace en este espacio.

    Es configuración del cliente: un administrador la cambia sin tocar código
    ni migrar nada. Sin fila, el valor por defecto del producto.
    """
    cur.execute("select valor from workspace_setting where clave = %s",
                (CLAVE_VIGENCIA,))
    fila = cur.fetchone()
    if not fila:
        return MINUTOS_POR_DEFECTO
    valor = fila["valor"]
    if isinstance(valor, str):
        valor = json.loads(valor)
    if isinstance(valor, dict):
        valor = valor.get("minutos", MINUTOS_POR_DEFECTO)
    try:
        minutos = int(valor)
    except (TypeError, ValueError):
        return MINUTOS_POR_DEFECTO
    return minutos if minutos > 0 else MINUTOS_POR_DEFECTO


def emitir(cur, membership_id: str, ahora: datetime) -> str:
    """Emite un enlace para una membresía y devuelve el token en claro.

    El valor devuelto es lo único que viaja y no queda guardado: la base sólo
    conserva su hash. Si se pierde, se emite otro; no se puede recuperar.
    """
    token = secrets.token_urlsafe(32)
    vence_en = ahora + timedelta(minutes=minutos_de_vigencia(cur))
    cur.execute("select emitir_acceso_tablero(%s, %s, %s) as id",
                (membership_id, _hash(token), vence_en))
    return token


def resolver(cur, token: str) -> dict | None:
    """Resuelve un token a su espacio y su membresía, o `None`.

    Devuelve `None` tanto si el token no existe como si venció o si la
    membresía dejó de estar activa: los tres casos son indistinguibles desde
    afuera a propósito, para no confirmar cuáles enlaces existieron.

    **No recibe el instante actual**, a diferencia de las consultas del puerto
    de lectura. Allá el momento sólo cambia qué se ve; acá decide si una
    credencial vale, y aceptarlo de quien llama permitiría revivir un token
    vencido pasando un momento anterior. El vencimiento lo juzga el reloj del
    servidor, dentro de la función.
    """
    cur.execute(
        "select workspace_id, membership_id from resolver_acceso_tablero(%s)",
        (_hash(token),))
    fila = cur.fetchone()
    if not fila:
        return None
    return {"workspace_id": str(fila["workspace_id"]),
            "membership_id": str(fila["membership_id"])}
