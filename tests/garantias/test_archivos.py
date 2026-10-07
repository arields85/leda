"""Los archivos recibidos (ADR 0019, decisiones 2 y 3; migración 0033): la capa de garantías.

Lo que se prueba acá es la base y la revisión del contenido, no la conversación:

- **Aislamiento.** `archivo` y `archivo_de_mensaje` tienen `row level security` forzado con la
  política de siempre y el espacio obligatorio; un espacio no lee ni escribe los archivos de otro,
  y una fila no puede apuntar a un archivo o a un mensaje de otro espacio.
- **La frontera.** `archivo` es del dominio: ningún identificador de Telegram. Los de Telegram
  viven en `archivo_de_mensaje`, del lado del transporte.
- **Inmutabilidad.** `leda_app` sólo agrega y lee; un disparador rechaza cualquier cambio o
  borrado, también para la administración. La huella y el tamaño los garantiza la base.
- **Un archivo por huella y espacio**, nunca compartido entre espacios.
- **Límites.** El tamaño (60 MB del producto, que un espacio puede bajar) y el tipo, juzgado
  por el contenido y no por la extensión: un ejecutable renombrado `.pdf`, un SVG, un HTML o
  un script se rechazan.
"""

from __future__ import annotations

import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone

import psycopg
import pytest

from leda.db import admin, espacio
from leda.motor import archivos

AHORA = datetime(2026, 10, 7, 13, 0, tzinfo=timezone.utc)
NUEVAS = ("archivo", "archivo_de_mensaje")


# --- Contenidos de ejemplo, por sus primeros bytes ------------------------------------------

JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01" + b"\x00" * 64 + b"\xff\xd9"
PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 64
WEBP = b"RIFF\x24\x00\x00\x00WEBPVP8 " + b"\x00" * 64
HEIC = b"\x00\x00\x00\x18ftypheic\x00\x00\x00\x00mif1heic" + b"\x00" * 64
MP4 = b"\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2avc1mp41" + b"\x00" * 64
PDF = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<>>\nendobj\n%%EOF\n"
CSV = "fecha,ciclos\n2026-10-07,20\n".encode("utf-8")
EXE = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff" + b"\x00" * 64
ELF = b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 64
SVG = (b'<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg">'
       b'<script>alert(1)</script></svg>')
HTML = b"<!DOCTYPE html>\n<html><body><script>alert(1)</script></body></html>"
SCRIPT = b"#!/bin/sh\necho hola\n"


def _zip(nombres: list[str]) -> bytes:
    memoria = io.BytesIO()
    with zipfile.ZipFile(memoria, "w") as z:
        for nombre in nombres:
            z.writestr(nombre, "x")
    return memoria.getvalue()


ZIP = _zip(["programa/main.st", "programa/io.st"])
DOCX = _zip(["[Content_Types].xml", "word/document.xml"])


# --- Los espacios ---------------------------------------------------------------------------

@pytest.fixture
def espacios(conn, intake_world) -> dict[str, dict]:
    """Un mensaje entrante de Sam North en cada espacio."""
    resultado = {}
    with admin(conn) as cur:
        for slug in ("north-lab", "west-studio"):
            w = intake_world[slug]
            sam = w["people"]["Sam North"]
            cur.execute(
                """insert into inbound_message
                     (workspace_id, telegram_message_id, chat_id, app_user_id, texto)
                   values (%s, 10, %s, %s, 'la foto') returning id""",
                (w["id"], sam["telegram"], sam["app_user_id"]))
            resultado[slug] = {"id": w["id"], "persona": sam["membership_id"],
                               "entrante": str(cur.fetchone()["id"])}
    conn.commit()
    return resultado


def _archivo(cur, e: dict, contenido: bytes = JPEG, *, ws: str | None = None,
             huella: str | None = None, tamano: int | None = None) -> str:
    cur.execute(
        """insert into archivo (workspace_id, contenido, sha256, tamano, tipo, clase,
                                nombre_original, enviado_por_membership_id, recibido_en)
           values (%s, %s, %s, %s, 'image/jpeg', 'imagen', null, %s, %s) returning id""",
        (ws or e["id"], contenido, huella or hashlib.sha256(contenido).hexdigest(),
         len(contenido) if tamano is None else tamano, e["persona"], AHORA))
    return str(cur.fetchone()["id"])


def _de_mensaje(cur, e: dict, archivo: str | None, *, ws: str | None = None,
                entrante: str | None = None, rechazo: str | None = None,
                message_id: int = 10) -> str:
    cur.execute(
        """insert into archivo_de_mensaje
             (workspace_id, inbound_message_id, archivo_id, que_llego, rechazo,
              telegram_message_id, telegram_file_id, telegram_file_unique_id)
           values (%s, %s, %s, 'foto', %s, %s, 'AgAD-file', 'AQAD-unico') returning id""",
        (ws or e["id"], entrante or e["entrante"], archivo, rechazo, message_id))
    return str(cur.fetchone()["id"])


def _cuantas(cur, tabla: str) -> int:
    cur.execute(f"select count(*) as n from {tabla}")
    return cur.fetchone()["n"]


# --- Aislamiento ----------------------------------------------------------------------------

def test_las_tablas_nuevas_tienen_espacio_obligatorio_y_rls_forzado(conn):
    with admin(conn) as cur:
        for tabla in NUEVAS:
            cur.execute("""select relrowsecurity, relforcerowsecurity
                             from pg_class where oid = to_regclass(%s)""", (f"leda.{tabla}",))
            fila = cur.fetchone()
            assert fila is not None, f"{tabla} no existe"
            assert fila["relrowsecurity"] and fila["relforcerowsecurity"], tabla
            cur.execute("select polname from pg_policy where polrelid = to_regclass(%s)",
                        (f"leda.{tabla}",))
            assert [p["polname"] for p in cur.fetchall()] == ["aislamiento_espacio"], tabla
            cur.execute("""select is_nullable from information_schema.columns
                            where table_schema = 'leda' and table_name = %s
                              and column_name = 'workspace_id'""", (tabla,))
            assert cur.fetchone()["is_nullable"] == "NO", tabla


def test_el_archivo_es_del_dominio_y_lo_de_telegram_queda_del_lado_del_transporte(conn):
    """Frontera, regla 2: ningún identificador de Telegram en `archivo`."""
    with admin(conn) as cur:
        cur.execute("""select table_name, column_name from information_schema.columns
                        where table_schema = 'leda'
                          and table_name in ('archivo', 'archivo_de_mensaje')""")
        columnas: dict[str, set[str]] = {}
        for fila in cur.fetchall():
            columnas.setdefault(fila["table_name"], set()).add(fila["column_name"])
    assert not {c for c in columnas["archivo"]
                if c.startswith("telegram") or c in {"chat_id", "file_id"}}
    assert {"telegram_file_id", "telegram_file_unique_id",
            "telegram_media_group_id"} <= columnas["archivo_de_mensaje"]


def test_un_espacio_no_ve_los_archivos_del_otro(conn, espacios):
    norte, oeste = espacios["north-lab"], espacios["west-studio"]
    with admin(conn) as cur:
        _de_mensaje(cur, oeste, _archivo(cur, oeste))
    conn.commit()

    with espacio(conn, norte["id"]) as cur:
        for tabla in NUEVAS:
            assert _cuantas(cur, tabla) == 0, tabla
    with espacio(conn, oeste["id"]) as cur:
        for tabla in NUEVAS:
            assert _cuantas(cur, tabla) == 1, tabla


def test_un_espacio_no_escribe_archivos_en_otro(conn, espacios):
    norte, oeste = espacios["north-lab"], espacios["west-studio"]
    with espacio(conn, norte["id"]) as cur:
        with pytest.raises((psycopg.errors.InsufficientPrivilege,
                            psycopg.errors.ForeignKeyViolation)), conn.transaction():
            _archivo(cur, norte, ws=oeste["id"])
        with pytest.raises((psycopg.errors.InsufficientPrivilege,
                            psycopg.errors.ForeignKeyViolation)), conn.transaction():
            _de_mensaje(cur, oeste, None, rechazo="demasiado_grande")
    with espacio(conn, oeste["id"]) as cur:
        for tabla in NUEVAS:
            assert _cuantas(cur, tabla) == 0, tabla


def test_una_fila_no_apunta_a_un_archivo_ni_a_un_mensaje_de_otro_espacio(conn, espacios):
    """La comprobación de una clave foránea no pasa por la RLS: la clave lleva el espacio."""
    norte, oeste = espacios["north-lab"], espacios["west-studio"]
    with admin(conn) as cur:
        del_oeste = _archivo(cur, oeste)
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            _de_mensaje(cur, norte, del_oeste)
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            _de_mensaje(cur, norte, None, entrante=oeste["entrante"],
                        rechazo="demasiado_grande")
        # Quien lo mandó es del mismo espacio que el archivo.
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            _archivo(cur, {"id": norte["id"], "persona": oeste["persona"]}, PNG)


# --- Inmutabilidad --------------------------------------------------------------------------

def test_leda_app_solo_agrega_y_lee_archivos(conn, espacios):
    norte = espacios["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        _de_mensaje(cur, norte, _archivo(cur, norte))
        for tabla in NUEVAS:
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                cur.execute(f"update {tabla} set workspace_id = workspace_id")
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                cur.execute(f"delete from {tabla}")


def test_un_archivo_no_se_modifica_ni_se_borra_ni_con_la_administracion(conn, espacios):
    """ADR 0019, decisión 3: un disparador, como garantía aparte de los privilegios."""
    norte = espacios["north-lab"]
    with admin(conn) as cur:
        _archivo(cur, norte)
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            cur.execute("update archivo set nombre_original = 'otra.jpg'")
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            cur.execute("delete from archivo")
        assert _cuantas(cur, "archivo") == 1


def test_la_huella_y_el_tamano_los_garantiza_la_base(conn, espacios):
    norte = espacios["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            _archivo(cur, norte, JPEG, huella=hashlib.sha256(PNG).hexdigest())
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            _archivo(cur, norte, JPEG, tamano=len(JPEG) + 1)
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            _archivo(cur, norte, b"", huella=hashlib.sha256(b"").hexdigest())
    with admin(conn) as cur:
        cur.execute("""select pg_get_constraintdef(oid) as d from pg_constraint
                        where conrelid = 'leda.archivo'::regclass""")
        definiciones = " ".join(f["d"] for f in cur.fetchall())
    # El límite del producto, 60 MB, también en la base.
    assert str(60 * 1024 * 1024) in definiciones


def test_un_archivo_guardado_o_rechazado_es_exactamente_uno(conn, espacios):
    norte = espacios["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        archivo = _archivo(cur, norte)
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            _de_mensaje(cur, norte, None)
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            _de_mensaje(cur, norte, archivo, rechazo="demasiado_grande")
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            _de_mensaje(cur, norte, None, rechazo="porque_si")


def test_el_mismo_archivo_se_guarda_una_vez_por_espacio_y_nunca_se_comparte(conn, espacios):
    norte, oeste = espacios["north-lab"], espacios["west-studio"]
    with espacio(conn, norte["id"]) as cur:
        tipo = archivos.revisar(JPEG, None, archivos.TAMANO_MAXIMO)
        primero = archivos.guardar(cur, workspace_id=norte["id"], contenido=JPEG, tipo=tipo,
                                   nombre=None, enviado_por=norte["persona"], ahora=AHORA)
        otra_vez = archivos.guardar(cur, workspace_id=norte["id"], contenido=JPEG,
                                    tipo=tipo, nombre="foto.jpg",
                                    enviado_por=norte["persona"], ahora=AHORA)
        assert otra_vez == primero and _cuantas(cur, "archivo") == 1
        with pytest.raises(psycopg.errors.UniqueViolation), conn.transaction():
            _archivo(cur, norte, JPEG)
    with espacio(conn, oeste["id"]) as cur:
        en_el_oeste = archivos.guardar(cur, workspace_id=oeste["id"], contenido=JPEG,
                                       tipo=tipo, nombre=None,
                                       enviado_por=oeste["persona"], ahora=AHORA)
        assert en_el_oeste != primero and _cuantas(cur, "archivo") == 1


def test_un_mensaje_que_vuelve_a_llegar_no_anota_su_archivo_dos_veces(conn, espacios):
    norte = espacios["north-lab"]
    llegada = archivos.Llegada(archivos.FOTO, "AgAD-file", "AQAD-unico", None, len(JPEG), 10)
    with espacio(conn, norte["id"]) as cur:
        tipo = archivos.revisar(JPEG, None, archivos.TAMANO_MAXIMO)
        guardado = archivos.guardar(cur, workspace_id=norte["id"], contenido=JPEG, tipo=tipo,
                                    nombre=None, enviado_por=norte["persona"], ahora=AHORA)
        for _ in range(2):
            archivos.anotar(cur, workspace_id=norte["id"], entrante_id=norte["entrante"],
                            llegada=llegada, archivo_id=guardado)
        assert archivos.del_mensaje(cur, norte["entrante"]) == [
            {"que_llego": "foto", "nombre_original": None, "rechazo": None,
             "clase": "imagen"}]


# --- Límites --------------------------------------------------------------------------------

@pytest.mark.parametrize(("contenido", "nombre", "clase"), [
    (JPEG, None, "imagen"),
    (PNG, "captura.png", "imagen"),
    (WEBP, "foto.webp", "imagen"),
    (HEIC, "IMG_0001.HEIC", "imagen"),
    (MP4, "prueba.mp4", "video"),
    (PDF, "informe.pdf", "pdf"),
    (DOCX, "informe.docx", "documento"),
    (CSV, "medicion.csv", "texto"),
    (b"Probado 20 ciclos sin falla.\n", "notas.txt", "texto"),
    (ZIP, "programa-plc.zip", "comprimido"),
])
def test_la_lista_permitida_se_juzga_por_el_contenido(contenido, nombre, clase):
    assert archivos.revisar(contenido, nombre, archivos.TAMANO_MAXIMO).clase == clase


@pytest.mark.parametrize(("contenido", "nombre"), [
    (EXE, "informe.pdf"),           # un ejecutable renombrado
    (ELF, "foto.jpg"),
    (SVG, "plano.png"),             # puede ejecutar código en el navegador de quien lo abre
    (SVG, "plano.svg"),
    (HTML, "notas.txt"),
    (SCRIPT, "notas.txt"),
    (b"echo hola\r\n", "limpiar.bat"),      # un script es texto: lo delata su nombre
    (_zip(["META-INF/MANIFEST.MF"]), "programa.jar"),
    (b"\x00\x01\x02\x03" * 32, "proyecto.bin"),     # nada que se reconozca
])
def test_fuera_de_la_lista_se_rechaza_aunque_la_extension_diga_otra_cosa(contenido, nombre):
    with pytest.raises(archivos.Rechazo) as rechazo:
        archivos.revisar(contenido, nombre, archivos.TAMANO_MAXIMO)
    assert rechazo.value.motivo == archivos.TIPO_NO_ADMITIDO


def test_un_archivo_por_encima_del_limite_vigente_se_rechaza():
    limite = 1024
    archivos.revisar(PDF + b"\x00" * (limite - len(PDF)), "justo.pdf", limite)
    with pytest.raises(archivos.Rechazo) as rechazo:
        archivos.revisar(PDF + b"\x00" * (limite - len(PDF) + 1), "grande.pdf", limite)
    assert rechazo.value.motivo == archivos.DEMASIADO_GRANDE


def test_el_limite_es_el_del_producto_y_un_espacio_puede_bajarlo(conn, espacios):
    norte, oeste = espacios["north-lab"], espacios["west-studio"]
    assert archivos.TAMANO_MAXIMO == 60 * 1024 * 1024

    def fijar(cur, valor):
        cur.execute(
            """insert into workspace_setting (workspace_id, clave, valor)
               values (%s, %s, %s)
               on conflict (workspace_id, clave) do update set valor = excluded.valor""",
            (norte["id"], archivos.CLAVE_DEL_LIMITE, json.dumps(valor)))

    with espacio(conn, norte["id"]) as cur:
        assert archivos.limite(cur, norte["id"]) == archivos.TAMANO_MAXIMO
        fijar(cur, 10)
        assert archivos.limite(cur, norte["id"]) == 10 * 1024 * 1024
        # Bajarlo sí; subirlo por encima del producto, no.
        for invalido in (0, 61, 2.5, "diez", None):
            with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
                fijar(cur, invalido)
    with espacio(conn, oeste["id"]) as cur:
        assert archivos.limite(cur, oeste["id"]) == archivos.TAMANO_MAXIMO
