"""El ciclo del motor detrás del webhook (`leda.motor.fondo`; E3-7).

`servir` corre en un hilo de fondo el mismo ciclo que el escuchador corre en cada vuelta, para
cada espacio activo con su bot. Reloj fijo, IA que redacta, transportes de prueba: nada sale a
Telegram ni a un proveedor de IA.
"""

from __future__ import annotations

from leda.db import espacio
from leda.despachador import TransporteDePrueba
from leda.incidentes import registrar_incidente
from leda.motor.ciclo import ETAPA_CICLO
from leda.motor.fondo import ETAPA_SIN_BOT, Fondo
from leda.motor.tiempo import RelojFijo

from tests.motor.ayudantes import IAQueRedacta, administrador, cuantas, octubre, todos


def _fondo(conn, tokens: dict[str, str], at=None):
    transportes: dict[str, TransporteDePrueba] = {}

    def transporte_de(token: str) -> TransporteDePrueba:
        return transportes.setdefault(token, TransporteDePrueba())

    fondo = Fondo(lambda: conn, tokens=lambda: tokens, ia_de=lambda cur, ws: IAQueRedacta(),
                  transporte_de=transporte_de, reloj_de=lambda: RelojFijo(at or octubre(9, 10)),
                  imprimir=lambda *_: None)
    return fondo, transportes


def test_una_vuelta_corre_el_ciclo_de_cada_espacio_con_su_bot(conn, mundo, espacio_con_escalera):
    fondo, transportes = _fondo(conn, {"prueba": "7001:bot-de-prueba"})

    resultado = fondo.vuelta()

    assert resultado["prueba"]["escalera"] == {"pedido_de_estado": 1}
    assert [e.texto for e in transportes["7001:bot-de-prueba"].enviados] == ["Aviso 1."]


def test_los_avisos_a_la_administracion_salen_por_su_bot(conn, mundo):
    administrador(conn)
    with espacio(conn, mundo["id"]) as cur:
        registrar_incidente(cur, mundo["id"], "Algo para avisar.", etapa=ETAPA_CICLO)
    conn.commit()
    fondo, transportes = _fondo(conn, {"prueba": "7001:bot", "admin": "7009:bot-admin"})

    fondo.vuelta()

    assert [e.chat_id for e in transportes["7009:bot-admin"].enviados] == [90000]


def test_un_espacio_activo_sin_bot_deja_un_incidente_una_sola_vez(conn, mundo):
    fondo, transportes = _fondo(conn, {})

    assert fondo.vuelta() == {}
    fondo.vuelta()

    [incidente] = todos(conn, "select etapa, workspace_id from incident")
    assert incidente["etapa"] == ETAPA_SIN_BOT and str(incidente["workspace_id"]) == mundo["id"]
    assert transportes == {}


def test_si_la_base_no_contesta_se_descarta_la_conexion_y_reconecta(conn, mundo):
    class Rota:
        closed = False

        def cursor(self, *a, **k):
            raise OSError("la base no contesta")

        def transaction(self, *a, **k):
            raise OSError("la base no contesta")

        def close(self):
            self.closed = True

    conexiones = [Rota(), conn]
    fondo = Fondo(lambda: conexiones.pop(0), tokens=lambda: {"prueba": "7001:bot"},
                  ia_de=lambda cur, ws: IAQueRedacta(), transporte_de=lambda t: TransporteDePrueba(),
                  reloj_de=lambda: RelojFijo(octubre(9, 10)), imprimir=lambda *_: None)

    assert fondo.vuelta() == {}
    assert "prueba" in fondo.vuelta()
    assert cuantas(conn, "incident") == 0
