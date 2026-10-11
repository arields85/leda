"""La forma de un mensaje la da la cocina (chequeo de rumbo del formato, 2026-10-11;
`odd/tasks/fase-c.md`, "Formato").

La IA ya sabe el formato entero (`motor/instrucciones.py`) y aun así, en las rondas reales,
escribe renglones de más de `RENGLON_MAXIMO` caracteres y deja el cierre pegado a lo anterior:
la misma clase de falla en cada ronda. Es presentación, no comprensión, así que la cocina le da
la forma a lo que la IA escribió (`salida.dar_forma`), sin cambiar, agregar ni quitar una
palabra:

- un renglón de más del tope se parte entre oraciones, una por renglón, en el mismo bloque; una
  oración sola más larga que el tope queda como está. La marca (✏️ ⚠️) o la viñeta queda en el
  primer pedazo y los que siguen van sin marca: la marca dice qué es ese renglón, y lo que
  sigue debajo, en el mismo bloque, es su continuación. Un renglón de una tarea (📋 o 🗓️) nunca
  se toca;
- el cierre, la última oración del mensaje, va solo en su renglón con un renglón en blanco
  antes, cuando hoy comparte renglón o bloque con lo anterior. Un mensaje de un solo renglón
  corto, de una o de varias oraciones, queda como está: no tiene de qué separarse, y así quedan
  los textos fijos de la cocina. Un último renglón con una marca o una viñeta que es una sola
  oración es un renglón de su bloque (una lista, lo anotado): no se separa.

La forma se da donde entra todo mensaje visible a su cola (`enqueue_outbox` y la respuesta del
bot de administración), antes de calcular las entidades de Telegram: la cola guarda el texto ya
con su forma, que es lo que sale y lo que mide el corredor.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from leda.db import admin, espacio
from leda.salida import RENGLON_MAXIMO, dar_forma, enqueue_outbox, formatear

BA = ZoneInfo("America/Argentina/Buenos_Aires")
AHORA = datetime(2026, 7, 27, 10, 0, tzinfo=BA)   # lunes, en horario

# Oraciones de las rondas reales (`fase-c-decisiones-66-73.md`), que juntas pasan el tope.
UNA = "Marcos dijo que le toca a Ariel."
DOS = ("Ariel primero dijo que la tendría para el jue 22/10; después avisó que se le complicó "
       "con otra cosa y que la tendría ayer.")
TRES = "No hay confirmación de que ya esté."
LARGO = f"{UNA} {DOS} {TRES}"
TITULO = "Revisar comunicaciones industriales de la compresora de la planta 2"


def _renglones(texto: str) -> list[str]:
    return texto.split("\n")


# --- El renglón largo -----------------------------------------------------------------------

def test_un_renglon_largo_se_parte_entre_oraciones_en_el_mismo_bloque():
    assert len(LARGO) > RENGLON_MAXIMO
    texto = f"{LARGO}\n\n¿Querés que le pregunte a Ariel?"

    assert dar_forma(texto) == f"{UNA}\n{DOS}\n{TRES}\n\n¿Querés que le pregunte a Ariel?"


def test_un_renglon_corto_con_varias_oraciones_queda_como_esta():
    texto = "Quedó anotado. Te aviso el jueves.\n\n¿Algo más?"

    assert dar_forma(texto) == texto


def test_una_oracion_sola_mas_larga_que_el_tope_queda_como_esta():
    oracion = ("Si confirmás, Martín será consultado primero para decidir si la tarea pasa a "
               "Lucas, y si está de acuerdo, Lucas será consultado para ver si la toma.")
    assert len(oracion) > RENGLON_MAXIMO
    texto = f"{oracion}\n\n¿Lo confirmás?"

    assert dar_forma(texto) == texto


def test_el_renglon_con_una_marca_la_deja_en_el_primer_pedazo():
    texto = (f"📋 {TITULO}\n"
             "✏️ Quedó asentado que seguís trabado porque te falta la IP del servidor de "
             "Corelabs. Van 10 días hábiles desde que lo contaste, el mar 20/10.\n\n"
             "¿Seguís esperando la IP?")

    assert _renglones(dar_forma(texto)) == [
        f"📋 {TITULO}",
        "✏️ Quedó asentado que seguís trabado porque te falta la IP del servidor de Corelabs.",
        "Van 10 días hábiles desde que lo contaste, el mar 20/10.",
        "",
        "¿Seguís esperando la IP?"]


def test_la_vineta_queda_en_el_primer_pedazo_y_la_continuacion_va_sin_vineta():
    texto = f"Lo que sigue:\n• {LARGO}\n• Lucas, el lun 26/10.\n\nNo hace falta responder."

    assert _renglones(dar_forma(texto)) == [
        "Lo que sigue:", f"• {UNA}", DOS, TRES, "• Lucas, el lun 26/10.", "",
        "No hace falta responder."]


@pytest.mark.parametrize("marca", ["📋", "🗓️"])
def test_el_renglon_de_una_tarea_nunca_se_toca(marca):
    renglon = f"{marca} {TITULO}. {TITULO}. {TITULO}."
    assert len(renglon) > RENGLON_MAXIMO
    texto = f"{renglon}\n\nNo hace falta responder."

    assert dar_forma(texto) == texto


def test_no_se_parte_dentro_de_una_negrita():
    """Una negrita abre y cierra en el mismo renglón (`formatear`): partirla dejaría los
    asteriscos a la vista."""
    texto = f"**{UNA} {DOS}** {TRES}\n\n¿Seguimos?"

    forma = dar_forma(texto)

    assert _renglones(forma)[:2] == [f"**{UNA} {DOS}**", TRES]
    assert "**" not in formatear(forma)[0]


def test_una_minuscula_despues_del_punto_no_empieza_otra_oracion():
    texto = ("Faltan los planos, los guardamotores, el switch, etc. y todo lo que Lucas pidió "
             "para la sala de servidores de la planta 2 antes del viernes. ¿Lo pedís vos?")

    assert _renglones(dar_forma(texto)) == [
        "Faltan los planos, los guardamotores, el switch, etc. y todo lo que Lucas pidió para "
        "la sala de servidores de la planta 2 antes del viernes.", "", "¿Lo pedís vos?"]


# --- El cierre ------------------------------------------------------------------------------

def test_la_pregunta_que_comparte_el_renglon_va_aparte():
    texto = "📋 Programar PLC\nQuedó pedido el pase a Lucas. ¿Querés que le avise a Martín?"

    assert _renglones(dar_forma(texto)) == [
        "📋 Programar PLC", "Quedó pedido el pase a Lucas.", "", "¿Querés que le avise a Martín?"]


def test_que_no_hace_falta_responder_va_aparte():
    texto = ("📋 Programar PLC\n⚠️ Sigue frenada porque falta el switch nuevo.\n\n"
             "Cuando puedas seguir, avisame. No hace falta que respondas.")

    assert _renglones(dar_forma(texto))[-4:] == [
        "", "Cuando puedas seguir, avisame.", "", "No hace falta que respondas."]


def test_el_cierre_en_su_renglon_pero_en_el_mismo_bloque_se_separa():
    texto = f"📋 {TITULO}\n✏️ Quedó anotado que la terminás el jueves.\nNo hace falta responder."

    assert _renglones(dar_forma(texto)) == [
        f"📋 {TITULO}", "✏️ Quedó anotado que la terminás el jueves.", "",
        "No hace falta responder."]


def test_un_cierre_que_no_es_pregunta_tambien_va_aparte():
    """Todo mensaje termina con su próximo paso (`instrucciones.py`): el cierre es la última
    oración, diga lo que diga."""
    texto = "📋 Programar PLC\n✏️ Quedó anotado el inicio.\nTe aviso el jueves si sigue igual."

    assert _renglones(dar_forma(texto))[-2:] == ["", "Te aviso el jueves si sigue igual."]


def test_un_mensaje_de_una_sola_oracion_queda_como_esta():
    for texto in ("Listo.", "¿Me pasás la fecha?", "No hace falta responder."):
        assert dar_forma(texto) == texto


def test_un_mensaje_de_un_solo_renglon_corto_queda_como_esta():
    """Se lee de una vez: no tiene de qué separar su cierre. Así quedan también los textos fijos
    de la cocina, como el aviso neutro de un incidente."""
    from leda.incidentes import NOTICIA_NEUTRA_INCIDENTE

    for texto in ("Quedó pedido el pase a Lucas. ¿Querés que le avise a Martín?",
                  "Cuando puedas seguir, avisame. No hace falta que respondas.",
                  NOTICIA_NEUTRA_INCIDENTE):
        assert dar_forma(texto) == texto


def test_el_cierre_ya_aparte_queda_como_esta():
    texto = f"📋 {TITULO}\n✏️ Quedó anotado.\n\n¿La entregás hoy?"

    assert dar_forma(texto) == texto


def test_un_ultimo_renglon_con_marca_de_una_sola_oracion_es_de_su_bloque():
    """El último renglón de una lista o lo anotado no es un cierre suelto: no se separa."""
    for texto in (f"Tenés dos:\n🗓️ {TITULO}, vie 16/10\n🗓️ Programar PLC, lun 19/10",
                  "Esto quedó:\n• Lucas, el lun 26/10.",
                  f"📋 {TITULO}\n⚠️ Espera la IP del servidor."):
        assert dar_forma(texto) == texto


def test_la_ultima_oracion_de_un_renglon_con_marca_se_separa():
    texto = f"📋 {TITULO}\n⚠️ Falta la IP del servidor. ¿Se la pedís a Ariel?"

    assert _renglones(dar_forma(texto)) == [
        f"📋 {TITULO}", "⚠️ Falta la IP del servidor.", "", "¿Se la pedís a Ariel?"]


def test_un_renglon_largo_al_final_se_parte_y_su_ultima_oracion_es_el_cierre():
    assert _renglones(dar_forma(LARGO)) == [UNA, DOS, "", TRES]


# --- Siempre: las mismas palabras, en el mismo orden, y dos veces da lo mismo ----------------

CASOS = [
    f"{LARGO}\n\n¿Querés que le pregunte a Ariel?",
    LARGO,
    "📋 Programar PLC\nQuedó pedido el pase a Lucas. ¿Querés que le avise a Martín?",
    "Cuando puedas seguir, avisame. No hace falta que respondas.",
    f"📋 {TITULO}\n✏️ Quedó anotado que la terminás el jueves.\nNo hace falta responder.",
    f"Lo que sigue:\n• {LARGO}\n• Lucas, el lun 26/10.\n\nNo hace falta responder.",
    f"📋 {TITULO}\n⚠️ Falta la IP del servidor. ¿Se la pedís a Ariel?",
    f"**{UNA} {DOS}** {TRES}\n\n¿Seguimos?",
    "¿Es Mariano Naim? Podés tocar «Confirmar» o responder por escrito.",
    "Listo.",
]


@pytest.mark.parametrize("texto", CASOS)
def test_ninguna_palabra_cambia_ni_cambia_de_orden(texto):
    assert dar_forma(texto).split() == texto.split()


@pytest.mark.parametrize("texto", CASOS)
def test_dar_forma_dos_veces_da_lo_mismo(texto):
    assert dar_forma(dar_forma(texto)) == dar_forma(texto)


# --- Donde se da: la cola guarda el texto con su forma ---------------------------------------

def _persona(conn, ws: str, nombre: str = "Marcos Tarquini") -> str:
    with admin(conn) as cur:
        cur.execute(
            """select m.id from membership m join app_user u on u.id = m.app_user_id
                where m.workspace_id = %s and u.nombre = %s""", (ws, nombre))
        return str(cur.fetchone()["id"])


def test_la_cola_guarda_el_mensaje_con_su_forma(corework, conn):
    ws = corework.workspace_id
    persona = _persona(conn, ws)
    with espacio(conn, ws) as cur:
        enqueue_outbox(cur, workspace_id=ws, chat_id=500, text=f"{LARGO} ¿Le pregunto?",
                       scheduled_for=AHORA, dedupe_key="forma-1", is_response=True,
                       recipient_membership_id=persona)
        cur.execute("select cuerpo from message_outbox where dedupe_key = 'forma-1'")
        assert cur.fetchone()["cuerpo"] == f"{UNA}\n{DOS}\n{TRES}\n\n¿Le pregunto?"


def test_el_bloque_copiable_queda_literal_y_lo_de_antes_no_se_separa(corework, conn):
    """El bloque es lo que la persona escribió, al final: se copia tal cual, y la oración que lo
    presenta no es un cierre."""
    ws = corework.workspace_id
    persona = _persona(conn, ws)
    bloque = f"{UNA} {DOS} {TRES}"
    texto = f"No pude anotarlo. Te lo dejo para copiar:\n\n{bloque}"
    with espacio(conn, ws) as cur:
        enqueue_outbox(cur, workspace_id=ws, chat_id=500, text=texto, scheduled_for=AHORA,
                       dedupe_key="forma-2", is_response=True, recipient_membership_id=persona,
                       bloque_copiable=bloque)
        cur.execute("select cuerpo from message_outbox where dedupe_key = 'forma-2'")
        assert cur.fetchone()["cuerpo"] == texto


def test_la_respuesta_del_bot_de_administracion_tambien_tiene_su_forma(conn):
    from leda.despachador import encolar_respuesta_admin

    with admin(conn) as cur:
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (79101, 'Ada Admin') returning id""")
        ada = str(cur.fetchone()["id"])
        encolar_respuesta_admin(cur, ada, 79101, f"{LARGO} ¿Algo más?", clave="forma:ada")
        cur.execute("select cuerpo from admin_notice where dedupe_key = 'forma:ada'")
        assert cur.fetchone()["cuerpo"] == f"{UNA}\n{DOS}\n{TRES}\n\n¿Algo más?"
