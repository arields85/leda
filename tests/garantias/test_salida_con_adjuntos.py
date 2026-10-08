"""La salida con adjuntos (ADR 0019, decisión 6; migración 0035): la capa de garantías.

Lo que se prueba acá es la base, la salida y el despachador, no la conversación:

- **Aislamiento.** `message_outbox_adjunto` tiene `row level security` forzado con la política
  de siempre y el espacio obligatorio; un espacio no ve ni escribe los adjuntos de otro, y la base
  rechaza un adjunto que apunta a un archivo o a una fila de salida de otro espacio.
- **La frontera.** Un adjunto apunta al archivo del dominio, nunca a un identificador de Telegram,
  y `message_outbox` no suma columnas: cómo se manda un adjunto lo decide el despachador.
- **Sólo se agrega.** `leda_app` agrega y lee los adjuntos; no los cambia ni los borra.
- **Idempotencia.** Encolar dos veces el mismo álbum (la misma clave) no duplica la fila ni sus
  adjuntos.
- **Orden.** El texto y su álbum son dos filas de una misma respuesta: el álbum nunca sale antes
  que el texto, aunque el texto falle; si el texto no sale nunca, el álbum tampoco.
- **Cómo se manda.** El despachador reusa el identificador que Telegram le dio a una foto al
  recibirla y, si no sirve, sube la copia propia.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import psycopg
import pytest

from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.despachador import Adjunto, ErrorTelegram, TransporteDePrueba, TransporteTelegram, despachar
from leda.salida import PayloadValidationError, enqueue_outbox

AHORA = datetime(2026, 10, 8, 14, 0, tzinfo=timezone.utc)      # jueves, 11:00 en Buenos Aires
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01" + b"\x00" * 32 + b"\xff\xd9"
TABLA = "message_outbox_adjunto"

# Las columnas de `message_outbox` antes de la 0035: los adjuntos no le suman ninguna (riesgo 1
# de `docs/STATUS.md`, la salida atada a un transporte).
COLUMNAS_DE_LA_SALIDA = {
    "id", "workspace_id", "chat_id", "destinatario_membership_id", "tipo", "cuerpo",
    "es_respuesta", "es_bienvenida", "es_coordinacion", "bloque_copiable", "entrante_id",
    "respuesta_grupo", "requiere_confirmacion", "confirmado_por", "confirmado_en", "estado",
    "programado_para", "vence_en", "enviado_en", "telegram_message_id", "dedupe_key",
    "intentos", "ultimo_error", "pending_action_id"}


# --- Ayudas ---------------------------------------------------------------------------------

@pytest.fixture
def espacios(conn, intake_world) -> dict[str, dict]:
    """Sam North en cada espacio, con un mensaje entrante (para atar una foto recibida)."""
    resultado = {}
    with admin(conn) as cur:
        for slug in ("north-lab", "west-studio"):
            w = intake_world[slug]
            sam = w["people"]["Sam North"]
            cur.execute(
                """insert into inbound_message
                     (workspace_id, telegram_message_id, chat_id, app_user_id, texto)
                   values (%s, 10, %s, %s, 'las fotos') returning id""",
                (w["id"], sam["telegram"], sam["app_user_id"]))
            resultado[slug] = {"id": w["id"], "persona": sam["membership_id"],
                               "chat": sam["telegram"], "entrante": str(cur.fetchone()["id"])}
    conn.commit()
    return resultado


def _foto(cur, e: dict, marca: str, *, file_id: str | None = "AgAD-recibida") -> str:
    """Una foto recibida en el espacio `e` y, si `file_id`, atada al mensaje que la trajo."""
    contenido = JPEG + marca.encode()
    cur.execute(
        """insert into archivo (workspace_id, contenido, sha256, tamano, tipo, clase,
                                nombre_original, enviado_por_membership_id, recibido_en)
           values (%s, %s, %s, %s, 'image/jpeg', 'imagen', %s, %s, %s) returning id""",
        (e["id"], contenido, hashlib.sha256(contenido).hexdigest(), len(contenido),
         f"{marca}.jpg", e["persona"], AHORA))
    archivo = str(cur.fetchone()["id"])
    if file_id is not None:
        cur.execute(
            """insert into archivo_de_mensaje
                 (workspace_id, inbound_message_id, archivo_id, que_llego, telegram_message_id,
                  telegram_file_id, telegram_file_unique_id)
               values (%s, %s, %s, 'foto', %s, %s, %s)""",
            (e["id"], e["entrante"], archivo, abs(hash(marca)) % 1_000_000,
             f"{file_id}-{marca}", f"unico-{marca}"))
    return archivo


def _texto_y_album(cur, e: dict, fotos: list[str], clave: str = "aviso:1") -> None:
    """El texto y su álbum, dos filas de una misma respuesta, como los encola el motor."""
    enqueue_outbox(cur, workspace_id=e["id"], chat_id=e["chat"], text="Sam entregó la tarea.",
                   recipient_membership_id=e["persona"], dedupe_key=clave,
                   grupo_respuesta=clave, es_coordinacion=True, scheduled_for=AHORA)
    enqueue_outbox(cur, workspace_id=e["id"], chat_id=e["chat"], text="(adjuntos: 2)",
                   recipient_membership_id=e["persona"], dedupe_key=f"{clave}:adjuntos",
                   grupo_respuesta=clave, es_coordinacion=True, scheduled_for=AHORA,
                   adjuntos=fotos)


def _cuantas(cur, tabla: str, donde: str = "true", *args) -> int:
    cur.execute(f"select count(*) as n from {tabla} where {donde}", args)
    return cur.fetchone()["n"]


def _despachar(conn, ws: str, transporte, ahora: datetime = AHORA) -> dict[str, int]:
    with espacio(conn, ws) as cur:
        r = despachar(cur, ws, transporte, Calendario.desde_base(cur, ws), ahora)
    conn.commit()
    return r


# --- La tabla -------------------------------------------------------------------------------

def test_la_tabla_tiene_espacio_obligatorio_y_rls_forzado(conn):
    with admin(conn) as cur:
        cur.execute("""select relrowsecurity, relforcerowsecurity
                         from pg_class where oid = to_regclass(%s)""", (f"leda.{TABLA}",))
        fila = cur.fetchone()
        assert fila is not None, f"{TABLA} no existe"
        assert fila["relrowsecurity"] and fila["relforcerowsecurity"]
        cur.execute("select polname from pg_policy where polrelid = to_regclass(%s)",
                    (f"leda.{TABLA}",))
        assert [p["polname"] for p in cur.fetchall()] == ["aislamiento_espacio"]
        cur.execute("""select is_nullable from information_schema.columns
                        where table_schema = 'leda' and table_name = %s
                          and column_name = 'workspace_id'""", (TABLA,))
        assert cur.fetchone()["is_nullable"] == "NO"


def test_la_salida_no_suma_columnas_de_transporte_y_el_adjunto_es_del_dominio(conn):
    """Frontera, regla 2, y riesgo 1 de `docs/STATUS.md`: el adjunto apunta al archivo del
    dominio y `message_outbox` queda como estaba."""
    with admin(conn) as cur:
        cur.execute("""select table_name, column_name from information_schema.columns
                        where table_schema = 'leda'
                          and table_name in ('message_outbox', %s)""", (TABLA,))
        columnas: dict[str, set[str]] = {}
        for fila in cur.fetchall():
            columnas.setdefault(fila["table_name"], set()).add(fila["column_name"])
    assert columnas["message_outbox"] == COLUMNAS_DE_LA_SALIDA
    assert columnas[TABLA] == {"id", "workspace_id", "outbox_id", "archivo_id", "orden"}


def test_un_espacio_no_ve_los_adjuntos_del_otro(conn, espacios):
    norte, oeste = espacios["north-lab"], espacios["west-studio"]
    with espacio(conn, oeste["id"]) as cur:
        _texto_y_album(cur, oeste, [_foto(cur, oeste, "a"), _foto(cur, oeste, "b")])
    conn.commit()
    with espacio(conn, norte["id"]) as cur:
        assert _cuantas(cur, TABLA) == 0
    with espacio(conn, oeste["id"]) as cur:
        assert _cuantas(cur, TABLA) == 2


def test_la_base_rechaza_el_adjunto_de_un_archivo_de_otro_espacio(conn, espacios):
    """La comprobación de una clave foránea no pasa por la RLS: la clave lleva el espacio. Ni la
    administración puede atar a una fila de un espacio un archivo de otro, ni un archivo a una
    fila de salida de otro espacio; y un espacio no escribe adjuntos en otro."""
    norte, oeste = espacios["north-lab"], espacios["west-studio"]
    with admin(conn) as cur:
        del_oeste = _foto(cur, oeste, "ajena")
        del_norte = _foto(cur, norte, "propia")
        enqueue_outbox(cur, workspace_id=norte["id"], chat_id=norte["chat"], text="Hola",
                       dedupe_key="norte:texto")
        cur.execute("select id from message_outbox where dedupe_key = 'norte:texto'")
        salida_norte = str(cur.fetchone()["id"])
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            cur.execute("""insert into message_outbox_adjunto (workspace_id, outbox_id,
                                                               archivo_id, orden)
                           values (%s, %s, %s, 1)""", (norte["id"], salida_norte, del_oeste))
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            cur.execute("""insert into message_outbox_adjunto (workspace_id, outbox_id,
                                                               archivo_id, orden)
                           values (%s, %s, %s, 1)""", (oeste["id"], salida_norte, del_oeste))
    conn.commit()
    with espacio(conn, norte["id"]) as cur:
        # Por la salida, también: el archivo de otro espacio no se ve, y la base lo rechaza.
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            enqueue_outbox(cur, workspace_id=norte["id"], chat_id=norte["chat"],
                           text="(adjuntos: 1)", dedupe_key="norte:album",
                           adjuntos=[del_oeste])
        with pytest.raises((psycopg.errors.InsufficientPrivilege,
                            psycopg.errors.ForeignKeyViolation)), conn.transaction():
            cur.execute("""insert into message_outbox_adjunto (workspace_id, outbox_id,
                                                               archivo_id, orden)
                           values (%s, %s, %s, 1)""", (oeste["id"], salida_norte, del_norte))
        assert _cuantas(cur, TABLA) == 0


def test_leda_app_solo_agrega_y_lee_los_adjuntos(conn, espacios):
    norte = espacios["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        _texto_y_album(cur, norte, [_foto(cur, norte, "a"), _foto(cur, norte, "b")])
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute(f"update {TABLA} set orden = orden")
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute(f"delete from {TABLA}")
        assert _cuantas(cur, TABLA) == 2


def test_encolar_dos_veces_el_mismo_album_no_duplica_filas(conn, espacios):
    norte = espacios["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        fotos = [_foto(cur, norte, "a"), _foto(cur, norte, "b")]
        _texto_y_album(cur, norte, fotos)
        _texto_y_album(cur, norte, fotos)
        assert _cuantas(cur, "message_outbox") == 2
        assert _cuantas(cur, TABLA) == 2
        cur.execute(f"select archivo_id from {TABLA} order by orden")
        assert [str(f["archivo_id"]) for f in cur.fetchall()] == fotos


def test_un_album_va_solo_con_su_texto_de_hasta_diez_fotos_sin_partirse(conn, espacios):
    norte = espacios["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        fotos = [_foto(cur, norte, str(i)) for i in range(11)]
        with pytest.raises(PayloadValidationError):
            enqueue_outbox(cur, workspace_id=norte["id"], chat_id=norte["chat"],
                           text="(adjuntos)", dedupe_key="demasiadas", adjuntos=fotos)
        with pytest.raises(PayloadValidationError):
            enqueue_outbox(cur, workspace_id=norte["id"], chat_id=norte["chat"],
                           text="x " * 3000, dedupe_key="partido", adjuntos=fotos[:2],
                           allow_split=True)
        assert _cuantas(cur, "message_outbox") == 0


# --- El despacho ----------------------------------------------------------------------------

@dataclass
class TransporteQueFallaElTexto(TransporteDePrueba):
    """Un transporte que no puede mandar textos (`falla_texto`) y anota en qué orden llegó cada
    cosa."""

    falla_texto: bool = True
    orden: list[str] = field(default_factory=list)
    contenidos: list[list[bytes]] = field(default_factory=list)

    def enviar(self, chat_id, texto, botones=None, bloque=None):
        if self.falla_texto:
            raise ConnectionError("sin red")
        self.orden.append("texto")
        return super().enviar(chat_id, texto, botones, bloque)

    def enviar_album(self, chat_id, adjuntos):
        self.orden.append("album")
        # La copia propia se lee mientras se manda, en la transacción del despacho.
        self.contenidos.append([a.contenido() for a in adjuntos])
        return super().enviar_album(chat_id, adjuntos)


def test_el_album_sale_despues_de_su_texto(conn, espacios):
    norte = espacios["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        _texto_y_album(cur, norte, [_foto(cur, norte, "a"), _foto(cur, norte, "b")])
    conn.commit()
    transporte = TransporteQueFallaElTexto(falla_texto=False)
    assert _despachar(conn, norte["id"], transporte)["enviados"] == 2
    assert transporte.orden == ["texto", "album"]
    album = transporte.enviados[1]
    assert album.texto == "" and album.fotos == ["a.jpg", "b.jpg"]


def test_el_album_no_sale_antes_que_el_texto_aunque_el_texto_falle(conn, espacios):
    norte = espacios["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        _texto_y_album(cur, norte, [_foto(cur, norte, "a"), _foto(cur, norte, "b")])
        # El álbum, por su hora, iría primero: igual espera al texto.
        cur.execute("""update message_outbox set programado_para = %s
                        where dedupe_key = 'aviso:1:adjuntos'""", (AHORA - timedelta(hours=1),))
    conn.commit()
    transporte = TransporteQueFallaElTexto()
    _despachar(conn, norte["id"], transporte)
    assert transporte.orden == [] and transporte.enviados == []
    with admin(conn) as cur:
        cur.execute("select estado from message_outbox where dedupe_key = 'aviso:1:adjuntos'")
        assert cur.fetchone()["estado"] == "listo"

    # El texto se reintenta en la jornada (`despachador._fallo`): al salir, sale el álbum.
    transporte.falla_texto = False
    _despachar(conn, norte["id"], transporte, AHORA + timedelta(minutes=5))
    assert transporte.orden == ["texto", "album"]


def test_si_el_texto_no_sale_nunca_el_album_tampoco(conn, espacios):
    norte = espacios["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        _texto_y_album(cur, norte, [_foto(cur, norte, "a"), _foto(cur, norte, "b")])
        cur.execute("""update message_outbox set estado = 'fallido'
                        where dedupe_key = 'aviso:1'""")
    conn.commit()
    transporte = TransporteQueFallaElTexto(falla_texto=False)
    r = _despachar(conn, norte["id"], transporte)
    assert transporte.orden == [] and r["descartados"] == 1
    with admin(conn) as cur:
        cur.execute("select estado from message_outbox where dedupe_key = 'aviso:1:adjuntos'")
        assert cur.fetchone()["estado"] == "descartado"


def test_el_album_reusa_lo_recibido_y_sube_lo_que_no_tiene(conn, espacios):
    """Lo que le llega al transporte: el identificador que Telegram le dio a la foto al
    recibirla, si llegó como foto en este espacio; si no, sólo la copia propia."""
    norte = espacios["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        _texto_y_album(cur, norte, [_foto(cur, norte, "a"),
                                    _foto(cur, norte, "b", file_id=None)])
    conn.commit()
    transporte = TransporteQueFallaElTexto(falla_texto=False)
    _despachar(conn, norte["id"], transporte)
    [a, b] = transporte.albumes[0]
    assert a.file_id == "AgAD-recibida-a" and b.file_id is None
    assert transporte.contenidos[0] == [JPEG + b"a", JPEG + b"b"]


# --- El transporte de Telegram --------------------------------------------------------------

class _Respuesta:
    def __init__(self, cuerpo: dict, estado: int = 200) -> None:
        self.cuerpo, self.status_code = cuerpo, estado

    def json(self):
        return self.cuerpo

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class _ClienteFalso:
    """Telegram, que rechaza los identificadores que no conoce (`rechaza_ids`)."""

    def __init__(self, rechaza_ids: bool = False) -> None:
        self.rechaza_ids = rechaza_ids
        self.pedidos: list[dict] = []

    def post(self, url, data=None, files=None, json=None):
        metodo = url.rsplit("/", 1)[-1]
        self.pedidos.append({"metodo": metodo, "data": data, "files": files})
        if self.rechaza_ids and not files:
            return _Respuesta({"ok": False, "description": "wrong file identifier"}, 400)
        if metodo == "sendMediaGroup":
            return _Respuesta({"ok": True, "result": [{"message_id": 70}, {"message_id": 71}]})
        return _Respuesta({"ok": True, "result": {"message_id": 70}})


def _adjuntos(file_ids=("AgAD-1", "AgAD-2")) -> list[Adjunto]:
    return [Adjunto(f"f{i}.jpg", "image/jpeg", fid, lambda i=i: JPEG + bytes([i]))
            for i, fid in enumerate(file_ids)]


def test_telegram_manda_el_album_con_lo_recibido_sin_subir_nada():
    cliente = _ClienteFalso()
    t = TransporteTelegram("123:abc", cliente=cliente)
    assert t.enviar_album(5, _adjuntos()) == 70
    [pedido] = cliente.pedidos
    assert pedido["metodo"] == "sendMediaGroup" and not pedido["files"]
    assert [m["media"] for m in json.loads(pedido["data"]["media"])] == ["AgAD-1", "AgAD-2"]
    assert all(m["type"] == "photo" for m in json.loads(pedido["data"]["media"]))


def test_si_lo_recibido_no_sirve_telegram_sube_la_copia_propia():
    cliente = _ClienteFalso(rechaza_ids=True)
    t = TransporteTelegram("123:abc", cliente=cliente)
    assert t.enviar_album(5, _adjuntos()) == 70
    assert [p["metodo"] for p in cliente.pedidos] == ["sendMediaGroup", "sendMediaGroup"]
    subida = cliente.pedidos[1]
    assert [m["media"] for m in json.loads(subida["data"]["media"])] == [
        "attach://foto0", "attach://foto1"]
    assert subida["files"]["foto0"][1] == JPEG + bytes([0])


def test_una_sola_foto_sale_como_foto_y_un_error_no_lleva_el_token():
    cliente = _ClienteFalso()
    t = TransporteTelegram("123:abc", cliente=cliente)
    assert t.enviar_album(5, _adjuntos(("AgAD-1",))) == 70
    assert cliente.pedidos[0]["metodo"] == "sendPhoto"
    assert cliente.pedidos[0]["data"]["photo"] == "AgAD-1"

    sin_ids = _ClienteFalso(rechaza_ids=True)
    sin_ids.post = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("https://api/bot123:abc/"))
    with pytest.raises(ErrorTelegram) as e:
        TransporteTelegram("123:abc", cliente=sin_ids).enviar_album(5, _adjuntos((None,)))
    assert "123:abc" not in str(e.value)
