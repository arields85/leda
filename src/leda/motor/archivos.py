"""Los archivos que llegan por chat: qué se acepta y cómo se guarda (ADR 0019, decisiones 2 y 3;
migración 0033).

- **Dónde.** En `archivo`, con su contenido (`bytea`), su huella, su tamaño, el tipo que detectó
  el código, el nombre con que llegó, quién lo mandó y cuándo. Es del dominio: ningún
  identificador de Telegram (frontera, regla 2); el mensaje que lo trajo y los identificadores
  del canal quedan en `archivo_de_mensaje`, del lado del transporte (`anotar`, que usa el
  adaptador, `recibir.py`). Nada de lo
  que lee la evidencia, el tablero o los avisos arrastra el contenido: sólo se lee acá, y nunca
  con `select *`.
- **La base garantiza** que la huella es la del contenido y el tamaño el suyo, que un mismo
  archivo se guarda una vez por espacio (nunca se comparte entre espacios) y que nada se
  modifica ni se borra (`leda_app` sólo agrega y lee; un disparador rechaza el resto).
- **Tamaño** (`limite`): 60 MB por archivo, límite del producto (usuario, 2026-10-07), que un
  espacio puede bajar con `workspace_setting` (`archivo_tamano_maximo_mb`, un entero de 1 a 60).
  El canal tiene el suyo, que aplica su adaptador (`recibir.LIMITE_DE_TELEGRAM`).
- **Tipo** (`detectar`): una lista permitida del producto, igual para todos los clientes,
  juzgada por el contenido y nunca por la extensión ni por lo que declara quien manda.
  Imágenes (JPEG, PNG, WebP, HEIC), PDF, documentos de oficina, texto plano y CSV, videos, y
  comprimidos o archivos de proyecto, que Leda nunca abre ni ejecuta: de un comprimido sólo se
  miran los nombres que trae a la vista, para saber si es un documento de oficina. Quedan
  afuera los ejecutables, los scripts, el HTML y el SVG. El nombre sólo puede sumar un
  rechazo: un script es texto plano por su contenido, y un `.jar` es un comprimido, así que
  una extensión de algo que se ejecuta (`EXTENSIONES_QUE_SE_EJECUTAN`) se rechaza aunque el
  contenido sea de la lista.
- **Fuera de límite** (`Rechazo`, con su motivo): nunca en silencio. El adaptador anota qué
  llegó y por qué no se guardó, y la IA se lo cuenta a la persona (`hechos.SIGNIFICADOS`).
"""

from __future__ import annotations

import codecs
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime

MB = 1024 * 1024
TAMANO_MAXIMO = 60 * MB             # el del producto (usuario, 2026-10-07)
CLAVE_DEL_LIMITE = "archivo_tamano_maximo_mb"

# Por qué no se guardó lo que llegó (los códigos de `archivo_de_mensaje.rechazo`).
DEMASIADO_GRANDE = "demasiado_grande"
TIPO_NO_ADMITIDO = "tipo_no_admitido"

# Las clases de lo que se guarda (`archivo.clase`).
IMAGEN, VIDEO, PDF, DOCUMENTO, TEXTO, COMPRIMIDO = (
    "imagen", "video", "pdf", "documento", "texto", "comprimido")

# Lo que se ejecuta al abrirlo (en la máquina o en el navegador de quien lo abre). Sólo suma
# rechazos: lo permitido lo decide el contenido.
EXTENSIONES_QUE_SE_EJECUTAN = frozenset({
    "exe", "msi", "msp", "com", "scr", "pif", "cpl", "dll", "sys", "drv", "ocx",
    "bat", "cmd", "ps1", "psm1", "psd1", "vbs", "vbe", "js", "jse", "mjs", "wsf", "wsh",
    "hta", "jar", "apk", "app", "appx", "msix", "appimage", "deb", "rpm", "sh", "bash", "zsh",
    "csh", "ksh", "command", "py", "pyw", "pl", "rb", "php", "lnk", "reg", "inf", "scf", "url",
    "html", "htm", "xhtml", "xht", "shtml", "mht", "mhtml", "svg", "svgz", "xsl", "xslt",
})

# Lo que, dentro de un texto, es HTML, SVG o un script (en minúsculas).
_MARCAS_DE_CODIGO = (b"<svg", b"<html", b"<script", b"<!doctype html", b"<?php", b"<iframe",
                     b"<object", b"<embed", b"javascript:", b"http://www.w3.org/1999/xhtml",
                     b"http://www.w3.org/2000/svg")

_MARCAS_HEIC = frozenset({b"heic", b"heix", b"hevc", b"hevx", b"heim", b"heis", b"hevm",
                          b"hevs", b"mif1", b"msf1"})
_MARCAS_DE_VIDEO = frozenset({b"isom", b"iso2", b"iso4", b"iso5", b"iso6", b"mp41", b"mp42",
                              b"avc1", b"M4V ", b"M4VH", b"M4VP", b"qt  ", b"3gp4", b"3gp5",
                              b"3gp6", b"3g2a", b"mmp4", b"dash", b"f4v "})
_MUESTRA = 64 * 1024        # lo que se mira de un texto para juzgarlo


@dataclass(frozen=True)
class Tipo:
    """El tipo que detectó el código: el de la web (`mime`) y la clase (`clase`)."""

    mime: str
    clase: str


class Rechazo(Exception):
    """Lo que llegó no se guarda, por `motivo` (`DEMASIADO_GRANDE` o `TIPO_NO_ADMITIDO`)."""

    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo = motivo


# --- El tipo, por el contenido ------------------------------------------------------------

def detectar(contenido: bytes, nombre: str | None = None) -> Tipo | None:
    """El tipo de `contenido` si es de la lista permitida, o `None`. `nombre` sólo distingue un
    CSV de otro texto plano: nunca hace permitido lo que el contenido no es."""
    c = contenido
    if c.startswith(b"\xff\xd8\xff"):
        return Tipo("image/jpeg", IMAGEN)
    if c.startswith(b"\x89PNG\r\n\x1a\n"):
        return Tipo("image/png", IMAGEN)
    if c.startswith(b"RIFF") and c[8:12] == b"WEBP":
        return Tipo("image/webp", IMAGEN)
    if c.startswith(b"RIFF") and c[8:12] == b"AVI ":
        return Tipo("video/x-msvideo", VIDEO)
    if c[4:8] == b"ftyp":
        return _caja_ftyp(c)
    if c.startswith(b"\x1a\x45\xdf\xa3"):
        return Tipo("video/webm", VIDEO)
    if c.startswith(b"%PDF-"):
        return Tipo("application/pdf", PDF)
    if c.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")):
        return _de_un_zip(c)
    if c.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        return Tipo("application/x-ole-storage", DOCUMENTO)      # .doc, .xls, .ppt
    if c.startswith(b"{\\rtf"):
        return Tipo("application/rtf", DOCUMENTO)
    if c.startswith(b"7z\xbc\xaf\x27\x1c"):
        return Tipo("application/x-7z-compressed", COMPRIMIDO)
    if c.startswith(b"Rar!\x1a\x07"):
        return Tipo("application/vnd.rar", COMPRIMIDO)
    if c.startswith(b"\x1f\x8b"):
        return Tipo("application/gzip", COMPRIMIDO)
    if c.startswith(b"BZh"):
        return Tipo("application/x-bzip2", COMPRIMIDO)
    if c.startswith(b"\xfd7zXZ\x00"):
        return Tipo("application/x-xz", COMPRIMIDO)
    if c[257:262] == b"ustar":
        return Tipo("application/x-tar", COMPRIMIDO)
    return _texto(c, nombre)


def _caja_ftyp(c: bytes) -> Tipo | None:
    """HEIC o un video de la familia MP4 (MP4, MOV, 3GP), por sus marcas. AVIF y el audio
    suelto no están en la lista."""
    tamano = int.from_bytes(c[0:4], "big")
    fin = min(max(tamano, 16), len(c), 4096)
    marcas = {c[8:12]} | {c[i:i + 4] for i in range(16, fin - 3, 4)}
    if marcas & {b"avif", b"avis"}:
        return None
    if marcas & _MARCAS_HEIC:
        return Tipo("image/heic", IMAGEN)
    principal = c[8:12]
    if principal in _MARCAS_DE_VIDEO or marcas & _MARCAS_DE_VIDEO:
        if principal == b"qt  ":
            return Tipo("video/quicktime", VIDEO)
        if principal.startswith(b"3g"):
            return Tipo("video/3gpp", VIDEO)
        return Tipo("video/mp4", VIDEO)
    return None


def _de_un_zip(c: bytes) -> Tipo:
    """Un documento de oficina (que es un zip) o un comprimido. No se abre: los nombres de lo
    que trae están a la vista en el propio archivo."""
    if c[30:38] == b"mimetype" and b"application/vnd.oasis.opendocument" in c[38:200]:
        return Tipo("application/vnd.oasis.opendocument", DOCUMENTO)
    for marca, mime in (
            (b"word/document.xml", "application/vnd.openxmlformats-officedocument."
                                   "wordprocessingml.document"),
            (b"xl/workbook.xml", "application/vnd.openxmlformats-officedocument."
                                 "spreadsheetml.sheet"),
            (b"ppt/presentation.xml", "application/vnd.openxmlformats-officedocument."
                                      "presentationml.presentation")):
        if marca in c:
            return Tipo(mime, DOCUMENTO)
    return Tipo("application/zip", COMPRIMIDO)


def _texto(c: bytes, nombre: str | None) -> Tipo | None:
    """Texto plano, CSV o XML (por ejemplo, el programa de un PLC exportado), si no trae HTML,
    SVG ni un script, ni bytes de control que un texto no tiene."""
    muestra = c[:_MUESTRA]
    if not muestra or b"\x00" in muestra:
        return None
    sin_bom = muestra[3:] if muestra.startswith(b"\xef\xbb\xbf") else muestra
    try:
        texto = codecs.getincrementaldecoder("utf-8")().decode(sin_bom, final=False)
    except UnicodeDecodeError:
        texto = sin_bom.decode("latin-1")
    control = sum(1 for ch in texto if (ord(ch) < 32 and ch not in "\t\n\r\f\v")
                  or ord(ch) == 127)
    if control > len(texto) // 100:
        return None
    minusculas = sin_bom.lower()
    if sin_bom.lstrip().startswith(b"#!") or any(m in minusculas for m in _MARCAS_DE_CODIGO):
        return None
    if sin_bom.lstrip().startswith(b"<"):
        return Tipo("application/xml", TEXTO)
    if _extension(nombre) == "csv":
        return Tipo("text/csv", TEXTO)
    return Tipo("text/plain", TEXTO)


def _extension(nombre: str | None) -> str:
    if not nombre or "." not in nombre:
        return ""
    return nombre.rsplit(".", 1)[1].strip().lower()


def revisar(contenido: bytes, nombre: str | None, limite_bytes: int) -> Tipo:
    """El tipo de lo que llegó, si se puede guardar; si no, `Rechazo` con su motivo. Primero el
    tamaño, después el tipo por el contenido y, al final, el nombre de algo que se ejecuta."""
    if len(contenido) > min(limite_bytes, TAMANO_MAXIMO):
        raise Rechazo(DEMASIADO_GRANDE)
    tipo = detectar(contenido, nombre)
    if tipo is None or _extension(nombre) in EXTENSIONES_QUE_SE_EJECUTAN:
        raise Rechazo(TIPO_NO_ADMITIDO)
    return tipo


# --- El tamaño ----------------------------------------------------------------------------

def limite(cur, workspace_id: str) -> int:
    """El tamaño máximo de un archivo en el espacio, en bytes: el del producto, o el que fijó el
    espacio si es menor. La base sólo acepta un entero de 1 a 60 MB; si no lo hay, el del
    producto."""
    cur.execute("select valor from workspace_setting where workspace_id = %s and clave = %s",
                (workspace_id, CLAVE_DEL_LIMITE))
    fila = cur.fetchone()
    valor = fila["valor"] if fila else None
    if isinstance(valor, str):
        valor = json.loads(valor)
    if isinstance(valor, (int, float)) and not isinstance(valor, bool) and valor >= 1:
        return min(int(valor) * MB, TAMANO_MAXIMO)
    return TAMANO_MAXIMO


# --- Guardar ------------------------------------------------------------------------------

def guardar(cur, *, workspace_id: str, contenido: bytes, tipo: Tipo, nombre: str | None,
            enviado_por: str, ahora: datetime) -> str:
    """El id del archivo guardado. Si el espacio ya lo tenía (la misma huella), el de entonces:
    se guarda una vez, con el nombre y quien lo mandó la primera vez."""
    huella = hashlib.sha256(contenido).hexdigest()
    cur.execute(
        """insert into archivo (workspace_id, contenido, sha256, tamano, tipo, clase,
                                nombre_original, enviado_por_membership_id, recibido_en)
           values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
           on conflict (workspace_id, sha256) do nothing
           returning id""",
        (workspace_id, contenido, huella, len(contenido), tipo.mime, tipo.clase,
         nombre_valido(nombre), enviado_por, ahora))
    fila = cur.fetchone()
    if fila is None:
        cur.execute("select id from archivo where workspace_id = %s and sha256 = %s",
                    (workspace_id, huella))
        fila = cur.fetchone()
    return str(fila["id"])


def nombre_valido(nombre: str | None) -> str | None:
    """El nombre con que llegó, como lo acepta la base: sin espacios a los costados, de a lo
    sumo 255 caracteres, y ninguno si queda vacío."""
    if nombre is None or not nombre.strip():
        return None
    return nombre.strip()[:255]


# --- Del lado del transporte: qué trajo cada mensaje (`archivo_de_mensaje`) -----------------

# Qué llegó, como se le cuenta a la persona (`archivo_de_mensaje.que_llego`).
FOTO, UN_VIDEO, UN_ARCHIVO = "foto", "video", "archivo"


@dataclass(frozen=True)
class Llegada:
    """Un archivo que trajo un mensaje de Telegram, como lo describe el canal: qué es, sus
    identificadores, el nombre y el tamaño que declara (si los dice), el número del mensaje y,
    en un álbum, su grupo."""

    que_llego: str
    file_id: str
    file_unique_id: str
    nombre: str | None
    tamano_declarado: int | None
    message_id: int
    media_group_id: str | None = None


def anotar(cur, *, workspace_id: str, entrante_id: str, llegada: Llegada,
           archivo_id: str | None = None, rechazo: str | None = None) -> None:
    """Ata lo que llegó al mensaje entrante: el archivo guardado o el motivo por el que no se
    guardó, uno de los dos. Un mensaje de Telegram que vuelve a llegar no se anota dos veces."""
    cur.execute(
        """insert into archivo_de_mensaje
             (workspace_id, inbound_message_id, archivo_id, que_llego, nombre_original,
              rechazo, telegram_message_id, telegram_file_id, telegram_file_unique_id,
              telegram_media_group_id)
           values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           on conflict (inbound_message_id, telegram_message_id) do nothing""",
        (workspace_id, entrante_id, archivo_id, llegada.que_llego,
         nombre_valido(llegada.nombre), rechazo, llegada.message_id, llegada.file_id,
         llegada.file_unique_id, llegada.media_group_id))


def del_mensaje(cur, entrante_id: str) -> list[dict]:
    """Lo que trajo un mensaje entrante, en el orden en que llegó: qué es, con qué nombre, la
    clase de lo guardado o por qué no se guardó. Nunca el contenido."""
    cur.execute(
        """select m.que_llego, m.nombre_original, m.rechazo, a.clase
             from archivo_de_mensaje m
             left join archivo a on a.workspace_id = m.workspace_id and a.id = m.archivo_id
            where m.inbound_message_id = %s
            order by m.telegram_message_id, m.at""", (entrante_id,))
    return [dict(f) for f in cur.fetchall()]
