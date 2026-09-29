"""Cifrado de credenciales de Google en la aplicación (rama auxiliar, G2a).

La credencial se cifra en Python antes de guardarse (Fernet, de
`cryptography`) con una o varias claves de `PRISMA_CLAVE_CREDENCIALES`,
separadas por coma: la primera cifra y todas descifran, así se rota sin cortar
el servicio (la clave nueva va primero, las viejas se conservan hasta re-cifrar
todo con `python -m prisma google recifrar`, que usa `rotar`).

Reglas:
- Sin clave, no hay cifrado y no hay uso de Google: se lanza un error tipado.
  Nunca se guarda ni se devuelve un dato sin cifrar como respaldo.
- Ningún mensaje de error contiene material de clave ni texto plano.
- La fuente de la clave es inyectable (`desde_texto`); `cargar` sólo la lee del
  entorno. Las pruebas pasan claves descartables.
"""

from __future__ import annotations

import os

from cryptography.fernet import Fernet, InvalidToken, MultiFernet

VARIABLE_CLAVE = "PRISMA_CLAVE_CREDENCIALES"


class ErrorCifrado(Exception):
    """Base de los errores de cifrado de credenciales."""


class ClaveCredencialesAusente(ErrorCifrado):
    """No hay clave configurada: no se cifra ni se usa Google."""


class ClaveCredencialesInvalida(ErrorCifrado):
    """La configuración de claves está mal formada."""


class TokenNoDescifrable(ErrorCifrado):
    """Ninguna de las claves configuradas descifra el dato."""


class Cifrador:
    """Cifra con la primera clave y descifra con cualquiera de las
    configuradas. No expone las claves ni en `repr`."""

    __slots__ = ("_multi",)

    def __init__(self, multi: MultiFernet) -> None:
        self._multi = multi

    def __repr__(self) -> str:
        return "Cifrador()"

    def cifrar(self, plano: str | bytes) -> bytes:
        if isinstance(plano, str):
            plano = plano.encode("utf-8")
        elif not isinstance(plano, (bytes, bytearray)):
            raise TypeError("Sólo se puede cifrar texto o bytes.")
        return self._multi.encrypt(bytes(plano))

    def descifrar(self, token: bytes | str) -> bytes:
        return self._o_no_descifrable(self._multi.decrypt, token)

    def descifrar_texto(self, token: bytes | str) -> str:
        # Un dato que descifra pero no es UTF-8 tampoco es un texto nuestro:
        # mismo error tipado, sin volcar los bytes.
        return self._o_no_descifrable(
            lambda t: self.descifrar(t).decode("utf-8"), token)

    def rotar(self, token: bytes | str) -> bytes:
        """Vuelve a cifrar el dato con la primera clave (la vigente)."""
        return self._o_no_descifrable(self._multi.rotate, token)

    @staticmethod
    def _o_no_descifrable(operacion, token):
        """Único lugar donde una falla de descifrado se vuelve el error
        tipado: el mensaje nunca lleva material de clave ni de dato."""
        try:
            return operacion(token)
        except (InvalidToken, TypeError, ValueError):
            raise TokenNoDescifrable(
                "Ninguna clave configurada descifra el dato.") from None


def desde_texto(crudo: str | None) -> Cifrador:
    """Arma el cifrador desde claves Fernet separadas por coma."""
    if crudo is None or not crudo.strip():
        raise ClaveCredencialesAusente(
            f"Falta {VARIABLE_CLAVE}: sin clave no se guardan ni se usan "
            "credenciales de Google.")
    fernets = []
    for posicion, parte in enumerate(crudo.split(","), start=1):
        clave = parte.strip()
        if not clave:
            raise ClaveCredencialesInvalida(
                f"{VARIABLE_CLAVE} tiene una entrada vacía (posición "
                f"{posicion}).")
        try:
            fernets.append(Fernet(clave.encode("ascii")))
        except (ValueError, UnicodeEncodeError):
            raise ClaveCredencialesInvalida(
                f"{VARIABLE_CLAVE} tiene una clave que no es una clave "
                f"Fernet válida (posición {posicion}).") from None
    return Cifrador(MultiFernet(fernets))


def cargar() -> Cifrador:
    """Lee la clave del entorno en el momento de la llamada (no al importar)."""
    return desde_texto(os.environ.get(VARIABLE_CLAVE))


def clave_nueva() -> str:
    """Genera una clave Fernet nueva, lista para el `.env`."""
    return Fernet.generate_key().decode("ascii")
