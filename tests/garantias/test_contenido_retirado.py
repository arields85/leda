"""Lo que retira la administración se borra de verdad (decisiones 57 y 59 del usuario,
2026-10-10; porción 5b de la C-3; migración 0053): la capa de garantías.

- **Se borra el contenido, queda la huella.** Retirar el contenido de una pieza vacía el
  contenido del archivo en la base (`archivo.contenido` nulo, `contenido_retirado_en` con la
  hora); la fila queda, con su huella, su tamaño, su tipo y quién lo mandó, para reconocerlo si
  alguien lo vuelve a mandar y para la auditoría. No tiene vuelta atrás.
- **Es la única excepción a que un archivo no cambia**, y la garantiza la base: sólo la conexión
  administrativa (`leda_admin`), sólo para vaciar el contenido de un archivo que la
  administración retiró, nunca para cambiar la huella ni ninguna otra columna, ni para volver a
  poner un contenido, ni para borrar la fila. Ninguna otra conexión puede.
- **Ningún camino que lee el contenido se cae ni manda un archivo vacío**: la página no lo
  sirve, y el despachador saca de un álbum ya encolado lo que se retiró después (si no queda
  nada, el álbum no sale), con un incidente de severidad baja: nunca en silencio, nunca un error
  técnico a una persona.
- **Lo que muestra la página** (decisión 59): "contenido retirado por la administración" y el
  motivo, sin el nombre de quien lo retiró, que queda guardado adentro.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

import psycopg
import pytest

from leda import pagina_de_tarea as P
from leda import tarea_vista
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.despachador import Adjunto, Entregado, despachar
from leda.salida import enqueue_outbox

from tests.garantias.test_pagina_de_la_tarea import (  # noqa: F401 -- `mundo` es la fixture
    _emitir, _leer, _leer_archivo, _persona, mundo)

AHORA = datetime(2026, 10, 22, 14, 0, tzinfo=timezone.utc)     # jueves, en horario
MOTIVO = "se ve una contraseña en la pantalla"


@pytest.fixture
def ada(conn, mundo) -> str:
    """Ada, administradora de plataforma: no es integrante de ningún equipo."""
    with admin(conn) as cur:
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (79101, 'Ada Admin') returning id""")
        usuario = str(cur.fetchone()["id"])
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                    (usuario,))
    conn.commit()
    return usuario


def _retirar(conn, mundo, ada: str, pieza: str, motivo: str = MOTIVO) -> list[str]:
    with admin(conn) as cur:
        retiradas = P.retirar_contenido(cur, mundo["north-lab"]["id"], pieza, ada, motivo,
                                        ahora=AHORA)
    conn.commit()
    return retiradas


def _archivo_de(conn, pieza: str) -> dict:
    with admin(conn) as cur:
        cur.execute("""select a.* from archivo a join evidence e on e.archivo_id = a.id
                        where e.id = %s""", (pieza,))
        fila = cur.fetchone()
    conn.commit()
    return fila


# --- Se borra el contenido, queda la huella (decisión 57) ------------------------------------

def test_retirar_el_contenido_lo_borra_de_la_base_y_deja_la_huella(conn, mundo, ada):
    foto = mundo["norte"]["piezas"]["foto"]
    antes = _archivo_de(conn, foto)
    assert antes["contenido"] is not None and antes["contenido_retirado_en"] is None

    _retirar(conn, mundo, ada, foto)

    despues = _archivo_de(conn, foto)
    assert despues["contenido"] is None
    assert despues["contenido_retirado_en"] is not None
    for columna in ("id", "workspace_id", "sha256", "tamano", "tipo", "clase",
                    "nombre_original", "enviado_por_membership_id", "recibido_en"):
        assert despues[columna] == antes[columna], columna
    # La pieza y su retiro siguen; la página no la sirve.
    token = _emitir(conn, mundo, "Taylor Quinn")
    assert _leer_archivo(conn, token, foto) is None


def test_un_texto_retirado_no_toca_ningun_archivo(conn, mundo, ada):
    texto = mundo["norte"]["piezas"]["texto"]
    _retirar(conn, mundo, ada, texto)
    with admin(conn) as cur:
        cur.execute("select count(*) n from archivo where contenido is null")
        assert cur.fetchone()["n"] == 0
    conn.commit()


def _vaciar(cur, archivo: str) -> None:
    cur.execute("""update archivo set contenido = null, contenido_retirado_en = now()
                    where id = %s""", (archivo,))


def test_la_aplicacion_no_puede_vaciar_ni_cambiar_un_archivo(conn, mundo, ada):
    foto = mundo["norte"]["piezas"]["foto"]
    archivo = str(_archivo_de(conn, foto)["id"])
    with espacio(conn, mundo["north-lab"]["id"]) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            _vaciar(cur, archivo)
    conn.rollback()


def test_la_administracion_no_vacia_un_archivo_que_no_retiro(conn, mundo, ada):
    """Sin un retiro de la administración de una pieza con ese archivo, ni la conexión
    administrativa lo vacía."""
    archivo = str(_archivo_de(conn, mundo["norte"]["piezas"]["pdf"])["id"])
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            _vaciar(cur, archivo)
    conn.rollback()


def test_otra_conexion_no_vacia_un_archivo_aunque_este_retirado(conn, mundo, ada):
    """La guarda mira el rol: la conexión de pruebas (el dueño, sin `leda_admin`) tampoco."""
    foto = mundo["norte"]["piezas"]["foto"]
    with admin(conn) as cur:
        cur.execute("""insert into evidencia_retirada (workspace_id, evidence_id,
                                                       retirada_por_app_user_id, motivo)
                       values (%s, %s, %s, 'prueba')""", (mundo["north-lab"]["id"], foto, ada))
    conn.commit()
    archivo = str(_archivo_de(conn, foto)["id"])
    with conn.transaction(), conn.cursor() as cur:
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            _vaciar(cur, archivo)
    conn.rollback()


@pytest.mark.parametrize("cambio", [
    "sha256 = repeat('0', 64)",
    "tamano = tamano + 1",
    "tipo = 'image/png'",
    "clase = 'pdf'",
    "nombre_original = 'otra.jpg'",
    "recibido_en = now()",
])
def test_ni_la_administracion_cambia_otra_columna_de_un_archivo(conn, mundo, ada, cambio):
    """Ni al vaciarlo ni después: la huella y lo demás no cambian nunca."""
    foto = mundo["norte"]["piezas"]["foto"]
    archivo = str(_archivo_de(conn, foto)["id"])
    with admin(conn) as cur:
        cur.execute("""insert into evidencia_retirada (workspace_id, evidence_id,
                                                       retirada_por_app_user_id, motivo)
                       values (%s, %s, %s, 'prueba')""", (mundo["north-lab"]["id"], foto, ada))
        with pytest.raises((psycopg.errors.RaiseException, psycopg.errors.CheckViolation)), \
                conn.transaction():
            cur.execute(f"""update archivo set contenido = null,
                                                contenido_retirado_en = now(), {cambio}
                             where id = %s""", (archivo,))
    conn.rollback()
    _retirar(conn, mundo, ada, foto)
    with admin(conn) as cur:
        with pytest.raises((psycopg.errors.RaiseException, psycopg.errors.CheckViolation)), \
                conn.transaction():
            cur.execute(f"update archivo set {cambio} where id = %s", (archivo,))
    conn.rollback()


def test_no_tiene_vuelta_atras_ni_se_borra_la_fila(conn, mundo, ada):
    foto = mundo["norte"]["piezas"]["foto"]
    archivo = str(_archivo_de(conn, foto)["id"])
    _retirar(conn, mundo, ada, foto)
    with admin(conn) as cur:
        with pytest.raises((psycopg.errors.RaiseException, psycopg.errors.CheckViolation)), \
                conn.transaction():
            cur.execute("""update archivo set contenido = '\\xffd8'::bytea,
                                              contenido_retirado_en = null where id = %s""",
                        (archivo,))
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            cur.execute("update archivo set contenido_retirado_en = now() where id = %s",
                        (archivo,))
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            cur.execute("delete from archivo where id = %s", (archivo,))
    conn.rollback()


def test_la_base_exige_contenido_o_la_marca_del_retiro(conn, mundo):
    """Un archivo sin contenido y sin la hora del retiro (o al revés) no se puede guardar."""
    persona = _persona(mundo, "Sam Noble")
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            cur.execute(
                """insert into archivo (workspace_id, contenido, sha256, tamano, tipo, clase,
                                        enviado_por_membership_id, recibido_en)
                   values (%s, null, repeat('a', 64), 10, 'image/jpeg', 'imagen', %s, now())""",
                (mundo["north-lab"]["id"], persona))
    conn.rollback()


# --- Lo que muestra la página (decisión 59) ---------------------------------------------------

def test_la_pagina_dice_el_motivo_sin_el_nombre_de_quien_lo_retiro(conn, mundo, ada):
    foto = mundo["norte"]["piezas"]["foto"]
    _retirar(conn, mundo, ada, foto, motivo="se ve una <contraseña>")
    token = _emitir(conn, mundo, "Sam Noble")
    datos = _leer(conn, token)
    pieza = next(p for p in datos["evidencia"] if p["id"] == foto)
    assert pieza["retirada_por_la_administracion"]
    assert pieza["motivo_del_retiro"] == "se ve una <contraseña>"
    texto = str(datos)
    assert "Ada Admin" not in texto
    html = tarea_vista.pagina(datos, token=token)
    assert "contenido retirado por la administración" in html
    assert "se ve una &lt;contraseña&gt;" in html and "<contraseña>" not in html
    assert "Ada Admin" not in html
    # Quién lo retiró queda adentro (constitución §12).
    with admin(conn) as cur:
        cur.execute("""select retirada_por_app_user_id from evidencia_retirada
                        where evidence_id = %s""", (foto,))
        assert str(cur.fetchone()["retirada_por_app_user_id"]) == ada
    conn.commit()


def test_el_motivo_de_quien_la_entrego_no_se_muestra_como_de_la_administracion(conn, mundo):
    foto = mundo["norte"]["piezas"]["foto"]
    with admin(conn) as cur:
        cur.execute("""insert into evidencia_retirada (workspace_id, evidence_id,
                                                       retirada_por_membership_id, motivo)
                       values (%s, %s, %s, 'no era esa')""",
                    (mundo["north-lab"]["id"], foto, _persona(mundo, "Sam Noble")))
    conn.commit()
    datos = _leer(conn, _emitir(conn, mundo, "Sam Noble"))
    pieza = next(p for p in datos["evidencia"] if p["id"] == foto)
    assert pieza["retirada"] and not pieza["retirada_por_la_administracion"]
    assert pieza.get("motivo_del_retiro") is None


# --- El despachador: un adjunto ya encolado cuyo contenido se retiró --------------------------

@dataclass
class TransporteQueLeeLosAdjuntos:
    """Un transporte que, como el de Telegram al subir la copia propia, lee el contenido de cada
    adjunto."""

    enviados: list[Entregado] = field(default_factory=list)
    contenidos: list[list[bytes]] = field(default_factory=list)

    def enviar(self, chat_id, texto, botones=None, bloque=None, sin_vista_previa=False) -> int:
        self.enviados.append(Entregado(chat_id, texto, []))
        return len(self.enviados)

    def enviar_album(self, chat_id, adjuntos: list[Adjunto]) -> int:
        self.contenidos.append([a.contenido() for a in adjuntos])
        self.enviados.append(Entregado(chat_id, "", [], fotos=[a.nombre for a in adjuntos]))
        return len(self.enviados)


def _album(conn, mundo, piezas: list[str]) -> None:
    """El texto de un aviso y su álbum con los archivos de `piezas`, ya encolados."""
    ws = mundo["north-lab"]["id"]
    persona = _persona(mundo, "Taylor Quinn")
    chat = mundo["north-lab"]["people"]["Taylor Quinn"]["telegram"]
    with espacio(conn, ws) as cur:
        archivos = []
        for pieza in piezas:
            cur.execute("select archivo_id from evidence where id = %s", (pieza,))
            archivos.append(str(cur.fetchone()["archivo_id"]))
        enqueue_outbox(cur, workspace_id=ws, chat_id=chat, text="Sam entregó la tarea.",
                       recipient_membership_id=persona, dedupe_key="aviso:1",
                       grupo_respuesta="aviso:1", es_coordinacion=True, scheduled_for=AHORA)
        enqueue_outbox(cur, workspace_id=ws, chat_id=chat, text="(adjuntos)",
                       recipient_membership_id=persona, dedupe_key="aviso:1:adjuntos",
                       grupo_respuesta="aviso:1", es_coordinacion=True, scheduled_for=AHORA,
                       adjuntos=archivos)
    conn.commit()


def _despachar(conn, mundo, transporte) -> dict[str, int]:
    ws = mundo["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        r = despachar(cur, ws, transporte, Calendario.desde_base(cur, ws), AHORA)
    conn.commit()
    return r


def _incidentes(conn) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("""select severidad, etapa, referencia_tipo, resumen_sanitizado
                         from incident where etapa = 'contenido_retirado_del_envio'""")
        filas = cur.fetchall()
    conn.commit()
    return filas


def _con_otra_foto(conn, mundo) -> str:
    """Otra foto entregada en la misma tarea, que no se retira."""
    from tests.garantias.test_pagina_de_la_tarea import JPEG, _archivo
    ws = mundo["north-lab"]["id"]
    persona = _persona(mundo, "Sam Noble")
    with admin(conn) as cur:
        archivo = _archivo(cur, ws, persona, JPEG + b"otra", "image/jpeg", "imagen", "otra.jpg")
        cur.execute("""insert into evidence (workspace_id, task_id, tipo, clase, archivo_id,
                                             entregado_por)
                       values (%s, %s, 'imagen', 'imagen', %s, %s) returning id""",
                    (ws, mundo["norte"]["id"], archivo, persona))
        pieza = str(cur.fetchone()["id"])
    conn.commit()
    return pieza


def test_un_adjunto_ya_encolado_cuyo_contenido_se_retiro_no_sale(conn, mundo, ada):
    foto = mundo["norte"]["piezas"]["foto"]
    otra = _con_otra_foto(conn, mundo)
    _album(conn, mundo, [foto, otra])
    _retirar(conn, mundo, ada, foto)

    transporte = TransporteQueLeeLosAdjuntos()
    r = _despachar(conn, mundo, transporte)
    assert r["enviados"] == 2
    [album] = [e for e in transporte.enviados if e.fotos is not None]
    assert album.fotos == ["otra.jpg"]
    assert transporte.contenidos == [[transporte.contenidos[0][0]]]
    assert all(c for c in transporte.contenidos[0])         # nunca un archivo vacío
    [incidente] = _incidentes(conn)
    assert incidente["severidad"] == "baja"
    assert incidente["referencia_tipo"] == "message_outbox"
    assert MOTIVO not in incidente["resumen_sanitizado"]


def test_un_album_con_todo_retirado_no_sale_y_deja_un_incidente(conn, mundo, ada):
    foto = mundo["norte"]["piezas"]["foto"]
    _album(conn, mundo, [foto])
    _retirar(conn, mundo, ada, foto)

    transporte = TransporteQueLeeLosAdjuntos()
    r = _despachar(conn, mundo, transporte)
    assert r["enviados"] == 1 and r["descartados"] == 1      # el texto sale; el álbum, no
    assert transporte.contenidos == []
    assert [e.fotos for e in transporte.enviados] == [None]
    with admin(conn) as cur:
        cur.execute("select estado from message_outbox where dedupe_key = 'aviso:1:adjuntos'")
        assert cur.fetchone()["estado"] == "descartado"
    conn.commit()
    [incidente] = _incidentes(conn)
    assert incidente["severidad"] == "baja"
    # Una segunda pasada no repite el incidente.
    _despachar(conn, mundo, transporte)
    assert len(_incidentes(conn)) == 1


# --- La vuelta atrás ---------------------------------------------------------------------------

def test_el_rollback_de_la_0053_se_niega_con_un_contenido_borrado(conn, mundo, ada):
    """Volver atrás pondría `contenido` otra vez obligatorio: con un contenido ya borrado no se
    puede, y el borrado no tiene vuelta atrás. Se ejercita la guarda tal como está escrita."""
    import re
    from pathlib import Path

    script = (Path(__file__).resolve().parents[2] / "db" / "rollbacks"
              / "0053_lo_que_retira_la_administracion.sql").read_text("utf-8")
    guarda = next(b for b in re.findall(r"do \$\$.*?end \$\$;", script, re.S)
                  if "se niega" in b)
    _retirar(conn, mundo, ada, mundo["norte"]["piezas"]["foto"])
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.RaiseException, match="0053"), conn.transaction():
            cur.execute("set local search_path = leda, public")
            cur.execute(guarda)
    conn.rollback()
