"""Credencial de Google por espacio (rama auxiliar, G2b).

Capa Python sobre las funciones `security definer` de la migración 0101. La
credencial se cifra ACÁ antes de guardarse y se descifra ACÁ después de
leerse (`cifrado.py`): la base sólo ve un token Fernet opaco, y `prisma_app`
sólo llega a él por funciones estrechas. Sin clave, `cifrado.cargar()` lanza
su error tipado y no se guarda ni se devuelve nada (nunca "seguimos sin
cifrar").

Dos caminos, separados por rol:

- Runtime (cursor de `espacio()`): `estado`, `leer`, `marcar_reautorizacion`.
  El espacio sale de la sesión, no de un argumento.
- Operación (cursor de `admin()`): `guardar`, `revocar`, `recifrar_todo`. Van
  con el espacio explícito; `prisma_app` no las puede ejecutar.

También las claves de `workspace_setting` que gobiernan Google por espacio
(apagado por defecto, cerrado ante un valor corrupto).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

import psycopg

from . import cifrado
from ..config_espacio import registrar_config_invalida

CLAVE_HABILITADO = "google.habilitado"
CLAVE_SCOPES = "google.scopes_habilitados"

# Los estados que devuelve `estado()`. "sin_autorizar" es no tener ninguna
# fila de proyección; el resto es la de `credencial_google_estado`. Un valor
# fuera de esta lista es un error, no un estado (`_validar_estado`).
ESTADOS = ("sin_autorizar", "vigente", "requiere_reautorizacion", "revocada")

# Lo que devuelve `marcar_reautorizacion` (los mismos valores que la función
# de la base).
MARCADA = "marcada"
SIN_CAMBIO = "sin_cambio"
CREDENCIAL_CAMBIO = "credencial_cambio"


class EstadoDesconocido(RuntimeError):
    """La base devolvió un estado que este código no conoce: se falla en vez
    de tratarlo como uno válido."""


class ResultadoDesconocido(RuntimeError):
    """`marcar_reautorizacion_google` devolvió algo fuera de sus tres
    resultados: se falla en vez de pasarlo a quien llama."""


@dataclass(frozen=True)
class CredencialGoogle:
    """La credencial ya descifrada. `secreto` no aparece en `repr`."""

    secreto: str = field(repr=False)
    cuenta_email: str
    scopes: tuple[str, ...]
    estado: str
    # Identifica ESTA autorización: quien avisa que Google la rechazó lo
    # devuelve a `marcar_reautorizacion` para no pisar una más nueva.
    autorizado_en: datetime


@dataclass(frozen=True)
class ResultadoRecifrado:
    """Qué hizo `recifrar_todo`: cuántos se re-cifraron y de qué espacios
    (sólo el slug, nunca contenido) no se pudo descifrar el dato
    (`ilegibles`) o cambió mientras se rotaba (`cambiadas`: se volvió a
    autorizar o se revocó entre la lectura y el reemplazo)."""

    recifradas: int
    ilegibles: tuple[str, ...]
    cambiadas: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Configuración por espacio (workspace_setting)
# ---------------------------------------------------------------------------


def _leer_setting(cur: psycopg.Cursor, workspace_id: str, clave: str):
    """`(existe, valor)`. El espacio se filtra explícitamente, no sólo por la
    RLS de la sesión: una conexión de administración ve todos los espacios."""
    cur.execute(
        "select valor from workspace_setting where workspace_id = %s and clave = %s",
        (workspace_id, clave))
    fila = cur.fetchone()
    return (True, fila["valor"]) if fila else (False, None)


def _config_invalida(cur: psycopg.Cursor, workspace_id: str, clave: str) -> None:
    """Un valor corrupto deja constancia UNA vez mientras siga sin resolver:
    el mismo mecanismo (un aviso administrativo por espacio y clave, que hace
    de candado, y un incidente saneado) que ya usa el alta con correo, con el
    aviso y la etapa propios de Google."""
    registrar_config_invalida(
        cur, workspace_id, clave, "apagado",
        prefijo_aviso="google_config_invalida",
        etapa="google_config_invalida")


def habilitado(cur: psycopg.Cursor, workspace_id: str) -> bool:
    """Si Google está encendido para el espacio. Ausente = apagado (todo lo
    nuevo nace apagado). Sólo el booleano JSON cuenta: cualquier otro valor
    es corrupto, se trata como apagado -- degradarse hacia MENOS efecto es
    el lado seguro -- y deja un incidente en vez de adivinar."""
    existe, valor = _leer_setting(cur, workspace_id, CLAVE_HABILITADO)
    if not existe:
        return False
    if isinstance(valor, bool):
        return valor
    _config_invalida(cur, workspace_id, CLAVE_HABILITADO)
    return False


def scopes_habilitados(cur: psycopg.Cursor, workspace_id: str) -> tuple[str, ...]:
    """Los permisos de Google habilitados para el espacio: dato de
    `workspace_setting`, separado de lo que la credencial efectivamente
    concedió. Ausente o lista vacía = ninguno. Sólo se lee una lista de
    textos no vacíos; cualquier otra cosa es corrupta, se lee como ninguno
    y deja un incidente."""
    existe, valor = _leer_setting(cur, workspace_id, CLAVE_SCOPES)
    if not existe:
        return ()
    if (isinstance(valor, list)
            and all(isinstance(s, str) and s for s in valor)):
        return tuple(valor)
    _config_invalida(cur, workspace_id, CLAVE_SCOPES)
    return ()


# ---------------------------------------------------------------------------
# Runtime: el espacio sale de la sesión (`espacio()`)
# ---------------------------------------------------------------------------


def _validar_estado(valor: str) -> str:
    if valor not in ESTADOS:
        raise EstadoDesconocido(
            "La base devolvió un estado de credencial de Google desconocido.")
    return valor


def estado(cur: psycopg.Cursor) -> str:
    """El estado de la credencial del espacio de la sesión."""
    cur.execute("select estado_credencial_google() as estado")
    return _validar_estado(cur.fetchone()["estado"])


def leer(cur: psycopg.Cursor, *,
         cifrador: cifrado.Cifrador | None = None) -> CredencialGoogle | None:
    """La credencial descifrada del espacio de la sesión, o `None` si no hay
    ninguna guardada (sin autorizar o revocada). Una credencial que
    `requiere_reautorizacion` sí se devuelve, con su estado: quien la usa
    decide. Sin clave o con una que no descifra, se propaga el error tipado
    de `cifrado`; la clave se carga ANTES de tocar la base."""
    cifrador = cifrador or cifrado.cargar()
    cur.execute("select * from leer_credencial_google()")
    fila = cur.fetchone()
    if fila is None:
        return None
    estado_leido = _validar_estado(fila["estado"])
    return CredencialGoogle(
        secreto=cifrador.descifrar_texto(fila["token_cifrado"]),
        cuenta_email=fila["cuenta_email"],
        scopes=tuple(fila["scopes"]),
        estado=estado_leido,
        autorizado_en=fila["autorizado_en"])


def marcar_reautorizacion(cur: psycopg.Cursor, motivo: str,
                         autorizado_en: datetime) -> str:
    """Google rechazó la credencial: pasa de `vigente` a
    `requiere_reautorizacion`. `motivo` es un código corto (minúsculas,
    dígitos y guion bajo), nunca el cuerpo de un error.

    `autorizado_en` es el de la credencial que quien llama efectivamente
    usó (`CredencialGoogle.autorizado_en`): la marca es una comparación, y si
    entre la lectura y el rechazo se volvió a autorizar, el rechazo es de la
    credencial vieja y no se toca la nueva. Devuelve `MARCADA`, `SIN_CAMBIO`
    (no había una vigente: ya requería reautorización, revocada o ninguna) o
    `CREDENCIAL_CAMBIO` (la vigente ya no es la usada). Ninguno es un
    error."""
    cur.execute("select marcar_reautorizacion_google(%s, %s) as resultado",
                (motivo, autorizado_en))
    resultado = cur.fetchone()["resultado"]
    if resultado not in (MARCADA, SIN_CAMBIO, CREDENCIAL_CAMBIO):
        raise ResultadoDesconocido(
            "La base devolvió un resultado de reautorización de Google "
            "desconocido.")
    return resultado


# ---------------------------------------------------------------------------
# Operación: el espacio se recibe (`admin()`)
# ---------------------------------------------------------------------------


def guardar(cur: psycopg.Cursor, workspace_id: str, secreto: str | bytes,
            cuenta_email: str, scopes: tuple[str, ...] | list[str], *,
            cifrador: cifrado.Cifrador | None = None) -> None:
    """Cifra el secreto y guarda (o reemplaza) la credencial del espacio; el
    estado pasa a `vigente`. La clave se carga y el dato se cifra ANTES de
    tocar la base: sin clave no se escribe nada. `cuenta_email` llega ya
    normalizado (minúsculas, sin espacios)."""
    cifrador = cifrador or cifrado.cargar()
    token = cifrador.cifrar(secreto).decode("ascii")
    cur.execute(
        "select guardar_credencial_google(%s::uuid, %s, %s, %s)",
        (workspace_id, token, cuenta_email, list(scopes)))


def revocar(cur: psycopg.Cursor, workspace_id: str, motivo: str) -> bool:
    """Revoca la credencial del espacio y borra el payload cifrado. Devuelve
    `False`, sin emitir nada, si no había nada que revocar."""
    cur.execute("select revocar_credencial_google(%s::uuid, %s) as cambio",
                (workspace_id, motivo))
    return cur.fetchone()["cambio"]


def recifrar_todo(cur: psycopg.Cursor,
                  cifrador: cifrado.Cifrador) -> ResultadoRecifrado:
    """Vuelve a cifrar cada payload guardado con la primera clave (la
    vigente). Un payload que ninguna clave configurada descifra se cuenta por
    slug y se deja intacto -- nunca se descarta ni se muestra --, y el resto
    igual se re-cifra. El reemplazo compara contra lo leído: si el espacio
    se volvió a autorizar o se revocó en el medio, no se pisa y el slug queda
    en `cambiadas` -- nunca se descarta en silencio."""
    cur.execute("select * from credenciales_google_cifradas()")
    filas = cur.fetchall()
    recifradas = 0
    ilegibles: list[str] = []
    cambiadas: list[str] = []
    for fila in filas:
        viejo = fila["token_cifrado"]
        try:
            nuevo = cifrador.rotar(viejo).decode("ascii")
        except cifrado.TokenNoDescifrable:
            ilegibles.append(fila["slug"])
            continue
        cur.execute("select reemplazar_token_google(%s::uuid, %s, %s) as ok",
                    (fila["workspace_id"], viejo, nuevo))
        if cur.fetchone()["ok"]:
            recifradas += 1
        else:
            cambiadas.append(fila["slug"])
    return ResultadoRecifrado(recifradas, tuple(ilegibles), tuple(cambiadas))
