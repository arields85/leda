"""Traduce archivos de la historia de Git anteriores al renombre a los nombres actuales.

El producto se llamó Prisma hasta el ADR 0015. Las pruebas que arman una base "vieja"
con `git show <commit>:db/esquema.sql` leen un esquema con roles `prisma_*` y variables
de sesión `prisma.*`, y después le aplican migraciones que ya dicen `leda`. La historia
de Git no cambia de nombre, así que la traducción tiene que vivir acá para siempre.

Es la misma sustitución que hizo el renombre (`tools/renombrar_a_leda.py`), y este
archivo está excluido de ese script: tiene que seguir nombrando lo viejo.
"""

RENOMBRE = (("PRISMA", "LEDA"), ("Prisma", "Leda"), ("prisma", "leda"))


def a_nombres_actuales(texto: str) -> str:
    for viejo, nuevo in RENOMBRE:
        texto = texto.replace(viejo, nuevo)
    return texto
