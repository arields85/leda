"""Lo que el motor audita por su cuenta (constitución §12).

Toda acción de Leda con efecto queda en `audit_log` con quién la originó, cuándo, sobre qué y
con la versión de las reglas del núcleo y del pack del espacio (`versiones`), en la misma
transacción que el efecto: si la jugada se deshace (su punto de guardado), su fila también.

Lo que pasa por la cocina (`herramientas.ejecutar`: un inicio, un bloqueo, destrabar, una
consulta) ya deja su fila allá, con la misma versión; acá va sólo lo que el motor escribe
directo. La regla, por escritura (crear, asignar, cambiar de estado, aprobar, enviar,
configurar):

- **Se audita** lo que agrega un hecho del trabajo o llega a otra persona por cuenta de Leda:
  una previsión (`anotar_prevision`) y su corrección (`corregir_prevision`), quién destraba un
  bloqueo (`anotar_quien_destraba`), un avance (`informar_avance`), que crean un hecho
  atribuido a quien lo dijo; y cada aviso guardado que sale (`enviar_aviso`), que es un envío
  de Leda, también a otras personas.
- **No se audita** lo que es la conversación misma, que queda entera en su registro de turnos
  (constitución §9): la respuesta a un mensaje, las preguntas y sus opciones, las esperas de
  respuesta y el estado de la conversación. Tampoco guardar o retirar un aviso que todavía no
  salió: es una intención, con su motivo en la fila del aviso; lo que se audita es el envío.
  Un aviso que no sale deja su incidente (`avisos`), no un envío.

El actor es quien dijo el hecho (`persona`) o, en un envío, Leda (`leda`). El momento del motor
va en el detalle (`at`): la fila lleva además la hora de la base.
"""

from __future__ import annotations

import json
from typing import Any

import psycopg

from .. import versiones
from ..autoridad import Solicitante
from ..db import registrar_auditoria


def auditar(cur: psycopg.Cursor, *, accion: str, workspace_id: str, sujeto_tipo: str,
            sujeto_id: Any, detalle: dict[str, Any], quien: Solicitante | None = None) -> None:
    """La fila de `audit_log` de una escritura directa del motor. `quien`: la persona que dijo
    el hecho; sin ella, la acción es de Leda. El detalle pasa por JSON con `default=str`, porque
    una fecha o un identificador también viajan."""
    registrar_auditoria(
        cur, accion=accion, workspace_id=workspace_id,
        actor_app_user_id=quien.app_user_id if quien is not None else None,
        actor_kind="persona" if quien is not None else "leda",
        sujeto_tipo=sujeto_tipo, sujeto_id=str(sujeto_id),
        detalle=json.loads(json.dumps(detalle, default=str)),
        pack_hash=versiones.pack_hash(cur, workspace_id),
        nucleo_hash=versiones.nucleo_hash())
