"""Un solo aviso neutro (T10-2b, U3; R3-H2, texto aprobado por el usuario).

Toda falla que deja un incidente y le contesta a la persona usa el mismo texto,
`incidentes.NOTICIA_NEUTRA_INCIDENTE`: ninguna disculpa propia en otro lugar.
"""

from __future__ import annotations

from pathlib import Path

from leda import incidentes

SRC = Path(incidentes.__file__).parent


def test_ningun_modulo_escribe_su_propia_disculpa_de_falla():
    """El texto de una falla con incidente vive sólo en `incidentes.py`: ningún otro
    archivo de `src/` repite "Ya quedó registrado" con su propia redacción."""
    propios = []
    for archivo in sorted(SRC.glob("*.py")):
        if archivo.name == "incidentes.py":
            continue
        texto = " ".join(archivo.read_text(encoding="utf-8").split())
        for frase in ("Ya quedó registrado", "Perdón, no pude"):
            if frase in texto:
                propios.append(f"{archivo.name}: {frase}")
    assert propios == []
