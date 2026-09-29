"""Configuración por entorno.

Regla: acá viven credenciales y rutas, nada de política. Qué modelo usar, con
qué cadencia trabajar y quién aprueba qué son datos de la base, no variables
de entorno.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _cargar_dotenv(ruta: Path) -> None:
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, _, valor = linea.partition("=")
        os.environ.setdefault(clave.strip(), valor.strip())


RAIZ = Path(__file__).resolve().parents[2]
if os.environ.get("PRISMA_LOAD_DOTENV", "1") != "0":
    _cargar_dotenv(RAIZ / ".env")


def recargar_dotenv() -> None:
    """Vuelve a leer `.env` sin pisar lo que ya está en el entorno
    (`_cargar_dotenv` usa `setdefault`). Hace falta porque la carga de
    arriba sólo corre una vez, al importar este módulo: un proceso de larga
    vida -- el listener local (`local.Escucha`) -- puede arrancar antes de
    que `.env` tenga, por ejemplo, `PRISMA_BOT_TOKEN_ADMIN`, y sin releer el
    archivo ese token nunca se vería hasta reiniciar el proceso."""
    if os.environ.get("PRISMA_LOAD_DOTENV", "1") != "0":
        _cargar_dotenv(RAIZ / ".env")


# Campos con credencial: fuera del repr por defecto (`field(repr=False)`).
# `config` es un singleton de módulo que circula por todo el proceso, así
# que aparece fácil en una traza sin capturar -- mismo riesgo que se vio con
# `ClienteJev.api_key` (fallo real de pytest que imprimió la clave entera).
@dataclass(frozen=True)
class Config:
    db_url: str = field(repr=False, default=os.environ.get("PRISMA_DB_URL", ""))
    authority_db_url: str = field(
        repr=False, default=os.environ.get("PRISMA_AUTHORITY_DB_URL", ""))
    llm_api_key: str = field(
        repr=False, default=os.environ.get("PRISMA_LLM_API_KEY", ""))
    openrouter_api_key: str = field(
        repr=False, default=os.environ.get("PRISMA_OPENROUTER_API_KEY", ""))
    webhook_secret: str = field(
        repr=False, default=os.environ.get("PRISMA_WEBHOOK_SECRET", ""))
    base_url: str = os.environ.get("PRISMA_BASE_URL", "")
    raiz: Path = RAIZ
    nucleo: Path = RAIZ / "nucleo"
    espacios: Path = RAIZ / "espacios"
    plantillas: Path = RAIZ / "plantillas"

    def clave_llm(self, proveedor: str) -> str:
        """Credencial del modelo conversacional según el proveedor: OpenRouter
        usa la suya (la misma de Jev) y el resto `PRISMA_LLM_API_KEY`. Nunca
        se manda la clave de un proveedor a otro."""
        if proveedor == "openrouter":
            return self.openrouter_api_key
        return self.llm_api_key

    def variable_clave_llm(self, proveedor: str) -> str:
        """Nombre de la variable de entorno que `clave_llm` lee."""
        if proveedor == "openrouter":
            return "PRISMA_OPENROUTER_API_KEY"
        return "PRISMA_LLM_API_KEY"

    def token_bot(self, slug_espacio: str) -> str:
        """Token del bot de un espacio. Un bot por equipo: si dos espacios
        compartieran token, un integrante podría recibir mensajes del otro."""
        clave = f"PRISMA_BOT_TOKEN_{slug_espacio.upper()}"
        token = os.environ.get(clave, "")
        if not token:
            raise LookupError(f"Falta {clave} en el entorno")
        return token

    def espacios_con_token(self) -> dict[str, str]:
        prefijo = "PRISMA_BOT_TOKEN_"
        return {
            k[len(prefijo):].lower(): v
            for k, v in os.environ.items()
            if k.startswith(prefijo) and v
        }


config = Config()
