"""Lo que lee el administrador cuando el motor registra un incidente (diseño probado en la
Etapa 2, E2-6).

`odd/tasks/prueba-chica-del-motor.md`, E2-5 (`PENDIENTE` de las etapas sin entrada) y sección 4
("Aviso al administrador"). Cada etapa del motor tiene su entrada en
`incidentes.EXPLICACION_POR_ETAPA`, con un título que dice lo que pasó: sin ella, el aviso usa
la explicación genérica y su título dice que Leda "no pudo responderle" a alguien, que acá no
es lo que pasó. Se prueba por el camino real: el incidente y su aviso en `admin_notice`.

Portada de `prueba_chica/test_incidentes_del_motor.py`.
"""

from __future__ import annotations

import pytest

from leda.db import espacio
from leda.incidentes import registrar_incidente
from leda.motor.avisos import ETAPA_AVISO_GUARDADO
from leda.motor.ciclo import ETAPA_CICLO
from leda.motor.escalera import ETAPA_ESCALERA

from tests.motor.ayudantes import administrador, uno


@pytest.mark.parametrize("etapa,titulo,que_paso", [
    (ETAPA_ESCALERA, "La escalera de recordatorios necesita atención",
     "La escalera de recordatorios del motor"),
    (ETAPA_AVISO_GUARDADO, "Un aviso de Leda no salió",
     "La IA no redactó un aviso guardado"),
    (ETAPA_CICLO, "Se cayó una parte del ciclo del motor",
     "Una parte del ciclo que corre cada minuto"),
], ids=lambda v: v if v.startswith("motor_") else "")
def test_cada_etapa_del_motor_tiene_su_explicacion(conn, mundo, etapa, titulo, que_paso):
    administrador(conn)
    with espacio(conn, mundo["id"]) as cur:
        registrar_incidente(cur, mundo["id"], "Resumen de prueba.", etapa=etapa)
    conn.commit()

    cuerpo = uno(conn, "select cuerpo from admin_notice")["cuerpo"]

    lineas = cuerpo.splitlines()
    assert lineas[0] == titulo
    assert lineas[2] == "Qué pasó" and lineas[3].startswith(que_paso)
    assert "no pudo responder" not in cuerpo and "todavía no tiene una explicación" not in cuerpo
