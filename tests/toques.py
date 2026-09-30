"""Ayuda compartida por las pruebas de los toques (T9-R4). Sin dependencias de
otras pruebas, para que cualquiera la importe sin ciclos."""

from __future__ import annotations

from prisma.db import admin


def envejecer_toques(conn, segundos: int) -> None:
    """Corre hacia atrás el reloj de los toques ya registrados: el segundo toque
    del mismo botón cae fuera de la ventana del toque repetido
    (`gateway.VENTANA_TOQUE_REPETIDO`, 10 s)."""
    with admin(conn) as cur:
        cur.execute("update inbound_message set at = at - make_interval(secs => %s) "
                    "where boton_callback is not null", (segundos,))
    conn.commit()
