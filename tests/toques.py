"""Ayuda compartida por las pruebas de los toques (T9-R4). Sin dependencias de
otras pruebas, para que cualquiera la importe sin ciclos."""

from __future__ import annotations

from prisma.db import admin
from prisma.gateway import VENTANA_TOQUE_REPETIDO

# Segundos que dejan un toque ya registrado fuera de la ventana, derivados de ella
# (T9-R4b): si la ventana cambia, las pruebas la siguen.
FUERA_DE_LA_VENTANA = int(VENTANA_TOQUE_REPETIDO.total_seconds()) + 1
# Dos envejecimientos de esta cantidad sacan el primer toque de la ventana; uno solo
# no.
MITAD_DE_LA_VENTANA_MAS_UNO = int(VENTANA_TOQUE_REPETIDO.total_seconds() // 2) + 1


def envejecer_toques(conn, segundos: int) -> None:
    """Corre hacia atrás el reloj de los toques ya registrados: el segundo toque
    del mismo botón cae fuera de la ventana del toque repetido
    (`gateway.VENTANA_TOQUE_REPETIDO`)."""
    with admin(conn) as cur:
        cur.execute("update inbound_message set at = at - make_interval(secs => %s) "
                    "where boton_callback is not null", (segundos,))
    conn.commit()


_IDS_DE_MENSAJE = __import__("itertools").count(1000)


def id_de_mensaje() -> int:
    """Un `message_id` distinto por mensaje, como los numera Telegram: dos
    mensajes con el mismo id en el mismo chat son un reenvío y se absorben
    (T9-H19b)."""
    return next(_IDS_DE_MENSAJE)
