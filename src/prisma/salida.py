"""Single Telegram-visible payload contract for producers and transport."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable


TELEGRAM_TEXT_LIMIT = 4096
BUTTON_TEXT_LIMIT = 3900
BUTTON_LABEL_LIMIT = 80
CALLBACK_DATA_BYTES = 64
# Lo que entra en el botón de copiar de Telegram (`copy_text`): 1 a 256. Se mide
# en unidades UTF-16, la medida de siempre de este módulo, que es la más
# estricta de las dos posibles.
COPY_TEXT_LIMIT = 256
_SPLIT_BODY_LIMIT = 4000
# Cuántos caracteres de una etiqueta de botón entran cómodos en una pantalla
# de teléfono antes de truncar con "…" (medido a ojo; más chico que
# `BUTTON_LABEL_LIMIT`, que es el tope técnico de Telegram). Un sufijo
# agregado después de truncar (p. ej. " — <nombre>" en
# `gateway._etiqueta_boton`) nunca se recorta.
TRUNCAR_ETIQUETA_BOTON = 48
# Objetivo de largo para una etiqueta de botón "linda" (hallazgo de sesión 2
# por Telegram, 2026-09-27: una etiqueta server-armada con el título completo
# recortado a mitad de palabra -- "Revisar comunicaciones industriales de la
# compr…" -- no entra cómoda en un botón inline de ancho completo en un
# teléfono chico). Un botón inline de Telegram ocupa el ancho disponible del
# chat; en una pantalla angosta de referencia (iPhone SE, ~320pt de ancho) el
# texto del botón, con su padding, entra sin ajustar renglón hasta unos
# 28-32 caracteres con la tipografía de sistema que usa Telegram -- 30 queda
# en el medio de ese rango, con margen de sobra para acentos y mayúsculas
# más anchas. Bastante más chico que `TRUNCAR_ETIQUETA_BOTON` (48, el corte
# duro histórico, ahora sólo el último recurso cuando ni una palabra entera
# entra en el objetivo).
OBJETIVO_ETIQUETA_BOTON = 30
# Iconos de botón (decisión del usuario, 2026-09-28, pack 06 §6: "función,
# no decoración"). Única fuente de la verdad de qué ícono le corresponde a
# cada categoría de botón -- nunca repetido en cada módulo que arma botones.
# `➕`/`💬`/`✅`/`✖️`/`✏️` son fijos, uno por categoría; `📋` marca cualquier
# botón que representa una tarea (lista de tareas, candidatas de aclaración o
# de dependencia, acciones del menú de una tarea, candidatas del alta
# conversacional).
ICONO_TAREA = "📋"
ICONO_VER_MAS = "➕"
ICONO_SALIR_OPCIONES = "💬"
ICONO_CONFIRMAR = "✅"
ICONO_CANCELAR = "✖️"
ICONO_OTRA_OPCION = "✏️"
ICONO_COPIAR = "📄"
_ICONOS_CONOCIDOS = (ICONO_TAREA, ICONO_VER_MAS, ICONO_SALIR_OPCIONES,
                    ICONO_CONFIRMAR, ICONO_CANCELAR, ICONO_OTRA_OPCION,
                    ICONO_COPIAR)

NO_EFFECT_STATUS = "Estado: sin cambios."
_NO_EFFECT_PATTERNS = tuple(re.compile(pattern, re.IGNORECASE) for pattern in (
    r"\bno se (?:registr[oó]|modific[oó]|cambi[oó]) (?:nada|ning[uú]n cambio)\b",
    r"\bno se registr[oó] (?:la|una|ninguna) (?:tarea|operaci[oó]n|actualizaci[oó]n|solicitud)\b",
    r"\bnada (?:se )?(?:registr[oó]|modific[oó]|cambi[oó])\b",
    r"\bsin cambios\b",
    r"\bno pude (?:hacer|realizar|aplicar|completar) (?:el|ese|ning[uú]n) cambio(?: solicitado)?\b",
    r"\bnothing (?:was |has been )?(?:changed|modified|updated|saved|applied)\b",
    r"\bno changes? (?:were |was |have been )?(?:made|saved|applied|recorded)\b",
))


class PayloadValidationError(ValueError):
    """The visible payload cannot be represented safely by Telegram."""


@dataclass(frozen=True)
class PreparedPayload:
    text: str
    dedupe_key: str


def telegram_utf16_units(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def con_icono(etiqueta: str, icono: str) -> str:
    """Antepone el ícono de una categoría a una etiqueta de botón ya armada
    (truncada y desambiguada): el ícono va siempre al PRINCIPIO, como prefijo,
    y nunca se recorta -- mismo criterio de "nunca se recorta" que el sufijo
    de responsable en `gateway._etiqueta_boton` (que sí va al final; el
    ícono y ese sufijo son los dos extremos de la misma etiqueta)."""
    return f"{icono} {etiqueta}"


def costo_icono(icono: str) -> int:
    """Cuánto le resta un ícono, más el espacio que lo separa del texto, al
    presupuesto de una etiqueta de botón -- en unidades UTF-16
    (`telegram_utf16_units`), la misma medida que usa Telegram para decidir
    si un botón entra. Un emoji del plano astral como `ICONO_TAREA` ocupa dos
    unidades UTF-16 aunque Python lo cuente como un solo carácter
    (`len()`): quien arma una etiqueta de tarea tiene que descontar esto del
    objetivo/límite ANTES de truncar el texto, para que el total (ícono +
    texto) siga entrando en el mismo presupuesto que tenía el texto solo."""
    return telegram_utf16_units(f"{icono} ")


def etiqueta_sin_icono(etiqueta: str) -> str:
    """La etiqueta sin su ícono de categoría, si tiene uno de los fijos de
    arriba. El ícono es una marca visual, nunca parte de la identidad de la
    opción -- ver `etiquetas_coinciden`."""
    for icono in _ICONOS_CONOCIDOS:
        prefijo = f"{icono} "
        if etiqueta.startswith(prefijo):
            return etiqueta[len(prefijo):]
    return etiqueta


def etiquetas_coinciden(a: str, b: str) -> bool:
    """Compara dos etiquetas de botón ignorando el ícono de categoría de
    cualquiera de las dos -- para que un toque simulado con la etiqueta
    "pelada" (bancos, pruebas, código anterior a los íconos) siga resolviendo
    la opción real, ya armada con su ícono."""
    return etiqueta_sin_icono(a) == etiqueta_sin_icono(b)


ETIQUETA_CONFIRMAR = con_icono("Confirmar", ICONO_CONFIRMAR)
ETIQUETA_CANCELAR = con_icono("Cancelar", ICONO_CANCELAR)
# El tercer botón de la vista previa (ADR 0005 decisión 1); sin ícono, como en las
# demás vistas previas.
ETIQUETA_MODIFICAR = "Modificar"
# El botón que copia al portapapeles lo que la persona había escrito (T9-R1c-3).
# Redacción pendiente de revisión de voz en T10.
ETIQUETA_COPIAR = con_icono("Copiar", ICONO_COPIAR)


def normalize_visible_text(raw: Any) -> str:
    text = unicodedata.normalize("NFC", str(raw or ""))
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    dangerous_format_controls = {
        "\u00ad", "\u061c", "\u200b", "\u200e", "\u200f", "\ufeff",
        *map(chr, range(0x202A, 0x202F)),
        *map(chr, range(0x2066, 0x206A)),
    }
    text = "".join(
        char for char in text
        if char in "\n\t"
        or (unicodedata.category(char) != "Cc"
            and char not in dangerous_format_controls)
    )
    return re.sub(r"[ ]{2,}", " ", text).strip()


def with_no_effect_status(raw: Any, *, required: bool = True) -> str:
    text = normalize_visible_text(raw)
    marker = re.compile(
        rf"(?im)^\s*{re.escape(NO_EFFECT_STATUS)}\s*$")
    text = normalize_visible_text(marker.sub("", text))
    if not required:
        return text
    for pattern in _NO_EFFECT_PATTERNS:
        text = pattern.sub("", text)
    text = normalize_visible_text(text).strip(" .,;:-")
    return f"{text}\n\n{NO_EFFECT_STATUS}" if text else NO_EFFECT_STATUS


def truncar_etiqueta_boton(texto: str, *, limite: int = TRUNCAR_ETIQUETA_BOTON) -> str:
    """Recorta una etiqueta a `limite` caracteres (por omisión,
    `TRUNCAR_ETIQUETA_BOTON`), con "…" al final si hizo falta. Reusado por la
    aclaración con botones (`gateway._etiqueta_boton`) y por
    `ofrecer_opciones` (T1, ADR 0007): la misma regla de truncado para toda
    etiqueta de botón, en vez de una por cada lugar que arma botones.

    Corrección de la revisión sobre las etiquetas de botón (seguimiento a):
    antes el corte duro de `acortar_etiqueta_boton` llamaba acá sin pasar
    `limite` -- quedaba siempre en 48 aunque quien llamara a
    `acortar_etiqueta_boton` hubiera pedido otro."""
    texto = texto.strip()
    if len(texto) <= limite:
        return texto
    return texto[:limite - 1].rstrip() + "…"


# Palabras de función que no aportan nada como última palabra visible antes
# de "…" (hallazgo 7, sesión 2 por Telegram, 2026-09-27: "Backup de
# servidores de…", "Configurar access points de…", "Cambiar switch
# industrial de…"). Lista chica y cerrada, en minúsculas -- se compara
# siempre con `casefold()`.
_PALABRAS_FUNCION_FINALES = frozenset({
    "de", "del", "la", "el", "los", "las", "en", "al", "a", "y", "e", "o",
    "u", "para", "con", "por", "sin", "sobre", "un", "una",
})


def _sin_palabras_funcion_finales(palabras: list[str]) -> list[str]:
    """Saca palabras de función del final de una lista de palabras, una por
    una, sin dejarla nunca vacía -- si sólo queda una palabra, se conserva
    aunque sea de función (mejor que una etiqueta vacía)."""
    palabras = list(palabras)
    while len(palabras) > 1 and palabras[-1].casefold() in _PALABRAS_FUNCION_FINALES:
        palabras.pop()
    return palabras


def acortar_etiqueta_boton(texto: str, *, objetivo: int = OBJETIVO_ETIQUETA_BOTON,
                           limite: int = TRUNCAR_ETIQUETA_BOTON) -> str:
    """Acorta una etiqueta de botón armada por el servidor a partir de un
    título (hallazgo de sesión 2 por Telegram): corta en un límite de
    PALABRA, nunca a mitad de una, con "…" al final sólo cuando de verdad
    hizo falta cortar algo. Si el título entero ya entra en `objetivo`, se
    devuelve tal cual -- sin "…" -- porque no se cortó nada.

    Si la primera palabra sola ya supera `objetivo` (no hay ningún límite de
    palabra dentro del objetivo donde cortar), cae al corte duro de siempre
    (`truncar_etiqueta_boton`, a `limite`) en vez de devolver una etiqueta
    vacía.

    El corte de palabra nunca deja la etiqueta terminando en una palabra de
    función (hallazgo 7: `_sin_palabras_funcion_finales`) -- "Backup de
    servidores de…" pasa a "Backup de servidores…".

    Reusada por todo lugar que arma botones de tarea a partir de un título
    (T3, "Ver más", tareas propias, candidatas de aclaración y de
    dependencia) y por `herramientas._ofrecer_opciones` cuando el modelo no
    dio una etiqueta corta propia."""
    texto = texto.strip()
    if len(texto) <= objetivo:
        return texto

    palabras = texto.split(" ")
    acumulado = ""
    for palabra in palabras:
        candidato = f"{acumulado} {palabra}".strip()
        if len(candidato) > objetivo:
            break
        acumulado = candidato

    if not acumulado:
        return truncar_etiqueta_boton(texto, limite=limite)
    acumulado = " ".join(_sin_palabras_funcion_finales(acumulado.split(" ")))
    return acumulado + "…"


def etiquetas_boton_distinguibles(
        titulos: list[str], *, fijas: list[bool] | None = None,
        objetivo: int = OBJETIVO_ETIQUETA_BOTON,
        limite: int = TRUNCAR_ETIQUETA_BOTON) -> list[str]:
    """La versión "de conjunto" de `acortar_etiqueta_boton` (hallazgo de
    sesión 2 por Telegram): un juego de botones nunca puede quedar ambiguo,
    así que si acortar dos títulos DISTINTOS los deja iguales (p. ej.
    "Revisar tablero de la máquina 3" y "...máquina 4" cortando los dos en
    "Revisar tablero de la máquina…"), las que colisionan se extienden
    palabra por palabra -- pueden superar `objetivo` para esto, hasta
    `limite` (el corte duro histórico) -- hasta volver a distinguirse.

    `fijas[i]` marca una etiqueta que ya vino elegida (la que puso el modelo
    en `ofrecer_opciones`, por ejemplo): nunca se hace crecer, sólo cuenta
    como obstáculo para que las demás no la pisen -- respeta la elección del
    modelo tal cual pidió T1.

    Último recurso: si dos títulos son indistinguibles incluso enteros (o en
    su corte duro a `limite`), se numeran -- nunca dos botones ambiguos en el
    mismo mensaje. Una etiqueta fija nunca se numera (respeta la elección del
    modelo igual que no se hace crecer); si la numeración nueva coincidiría
    con una etiqueta ya presente en el conjunto (fija o no), se salta ese
    número (seguimiento b a la revisión de la sesión de etiquetas)."""
    titulos = [t.strip() for t in titulos]
    fijas = list(fijas) if fijas is not None else [False] * len(titulos)
    if len(fijas) != len(titulos):
        raise ValueError(
            f"fijas tiene que tener el mismo largo que titulos "
            f"({len(fijas)} != {len(titulos)}); si no hay ninguna fija, no "
            "pasar `fijas` en vez de una lista más corta.")

    resultado = [
        t if fija else acortar_etiqueta_boton(t, objetivo=objetivo, limite=limite)
        for t, fija in zip(titulos, fijas)]

    crecibles = [i for i, fija in enumerate(fijas) if not fija]
    palabras = {i: titulos[i].split(" ") for i in crecibles}
    n_palabras = {i: len(resultado[i].rstrip("…").split(" ")) for i in crecibles}

    avanzo = True
    while avanzo:
        avanzo = False
        # Colisiones contra una foto del arranque de esta pasada -- no
        # contra `resultado` mientras se lo va mutando en la misma pasada:
        # si no, la primera etiqueta que crece dentro del `for` deja de
        # "colisionar" contra sí misma y las demás de su mismo grupo se
        # saltean de largo sin crecer (dos etiquetas iguales, una sola se
        # distingue).
        foto = list(resultado)
        for i in crecibles:
            otras = foto[:i] + foto[i + 1:]
            if foto[i] not in otras:
                continue
            if n_palabras[i] >= len(palabras[i]):
                continue
            n_palabras[i] += 1
            candidato = " ".join(palabras[i][:n_palabras[i]])
            if len(candidato) > limite:
                candidato = titulos[i][:limite - 1].rstrip() + "…"
                n_palabras[i] = len(palabras[i])
            elif n_palabras[i] < len(palabras[i]):
                candidato = candidato + "…"
            resultado[i] = candidato
            avanzo = True

    conteo: dict[str, int] = {}
    for etiqueta in resultado:
        conteo[etiqueta] = conteo.get(etiqueta, 0) + 1
    # Una etiqueta fija "ocupa" su texto sin poder cederlo -- si una o más
    # movibles coinciden con ella, TODAS se numeran (nunca sólo la segunda):
    # la primera libre de un grupo sin ninguna fija sigue quedando tal cual,
    # igual que antes.
    fija_ocupa = {etiqueta for i, etiqueta in enumerate(resultado) if fijas[i]}
    # Todas las etiquetas ya en uso -- una fija nunca se numera (se conserva
    # tal cual), y ninguna etiqueta nueva puede coincidir con una que ya está
    # en el conjunto, sea fija o el resultado de una numeración anterior.
    ocupadas = set(resultado)
    vistos: dict[str, int] = {}
    for i, etiqueta in enumerate(resultado):
        if fijas[i] or conteo[etiqueta] <= 1:
            continue
        vistos[etiqueta] = vistos.get(etiqueta, 0) + 1
        # Si una fija ya ocupa este texto, cuenta como la ocurrencia 1 -- la
        # numeración de las movibles arranca en 2 aunque sea la primera que
        # se ve acá (nunca queda una movible igual a la fija).
        indice_ocurrencia = vistos[etiqueta] + (1 if etiqueta in fija_ocupa else 0)
        if indice_ocurrencia == 1:
            # La primera aparición de un grupo repetido sin ninguna fija se
            # deja tal cual -- sólo las siguientes se numeran, igual que
            # antes.
            continue
        sufijo = indice_ocurrencia
        candidata = f"{etiqueta} ({sufijo})"
        while candidata in ocupadas:
            sufijo += 1
            candidata = f"{etiqueta} ({sufijo})"
        resultado[i] = candidata
        ocupadas.add(candidata)
    return resultado


def etiquetas_de_tarea(titulos: list[str], *, fijas: list[bool] | None = None,
                       objetivo: int = OBJETIVO_ETIQUETA_BOTON,
                       limite: int = TRUNCAR_ETIQUETA_BOTON) -> list[str]:
    """La receta completa de un botón de tarea (íconos, decisión del usuario,
    2026-09-28): descuenta `costo_icono(ICONO_TAREA)` de `objetivo`/`limite`
    ANTES de truncar y desambiguar -- para que el ícono cuente hacia el mismo
    presupuesto que el texto, nunca aparte -- y antepone `ICONO_TAREA` recién
    DESPUÉS, sobre cada etiqueta ya corta y distinguible.

    Única fuente de esta cuenta (R2-002, revisión 2026-09-28+1): antes estaba
    copiada a mano en `agente._opciones_lista_tareas`,
    `herramientas._ofrecer_opciones`, `gateway._mostrar_mas_tareas`,
    `_pedir_eleccion_dependencia`, `_candidatas_para_botones` e
    `ingreso_tareas._open_entity_page` -- la última de ésas se había quedado
    afuera de la cuenta (R3-003), exactamente el riesgo de copiarla en vez de
    compartirla."""
    costo = costo_icono(ICONO_TAREA)
    cortas = etiquetas_boton_distinguibles(
        titulos, fijas=fijas, objetivo=objetivo - costo, limite=limite - costo)
    return [con_icono(etiqueta, ICONO_TAREA) for etiqueta in cortas]


def prepare_buttons(buttons: Iterable[Any]) -> list[tuple]:
    """Valida los botones. Uno de callback sale como `(etiqueta, callback)`; uno
    de copiar (`copiar`, el texto que copia al tocarlo, 1 a `COPY_TEXT_LIMIT`
    unidades) como `(etiqueta, "", copiar)`: no lleva callback."""
    prepared = []
    for button in buttons:
        as_tuple = isinstance(button, tuple)
        label = normalize_visible_text(
            getattr(button, "etiqueta", button[0] if as_tuple else ""))
        if not label or telegram_utf16_units(label) > BUTTON_LABEL_LIMIT:
            raise PayloadValidationError(
                f"La etiqueta de un botón excede {BUTTON_LABEL_LIMIT} unidades UTF-16.")
        copiar = getattr(button, "copiar", button[2] if as_tuple and len(button) > 2
                         else None)
        if copiar is not None:
            if not copiar or telegram_utf16_units(copiar) > COPY_TEXT_LIMIT:
                raise PayloadValidationError(
                    f"El texto de un botón de copiar tiene de 1 a {COPY_TEXT_LIMIT} "
                    "unidades UTF-16.")
            prepared.append((label, "", copiar))
            continue
        callback = str(getattr(
            button, "callback_data", button[1] if as_tuple else ""))
        if not callback or len(callback.encode("utf-8")) > CALLBACK_DATA_BYTES:
            raise PayloadValidationError(
                f"El callback de un botón excede {CALLBACK_DATA_BYTES} bytes.")
        prepared.append((label, callback))
    return prepared


def cabe_en_boton_de_copiar(bloque: str) -> bool:
    """Si `bloque` entra en el botón de copiar de Telegram (1 a 256)."""
    return 0 < telegram_utf16_units(bloque) <= COPY_TEXT_LIMIT


def entidad_de_bloque(texto: str, bloque: str) -> dict:
    """La entidad `pre` de Telegram que marca `bloque` -- un bloque que se copia
    con un toque -- dentro de `texto`. El bloque es siempre el final del texto:
    su posición se calcula sobre el texto que de verdad se manda (con el saludo
    diario ya antepuesto, si lo hubo), en unidades UTF-16, y no se guarda en
    ninguna parte. Un bloque vacío o que no es el final del texto: error."""
    if not bloque or not texto.endswith(bloque):
        raise PayloadValidationError(
            "El bloque copiable tiene que ser el final del texto del mensaje.")
    return {"type": "pre",
            "offset": telegram_utf16_units(texto[:len(texto) - len(bloque)]),
            "length": telegram_utf16_units(bloque)}


def prepare_payload(text: Any, *, dedupe_key: str, has_buttons: bool = False,
                    buttons: Iterable[Any] = (), allow_split: bool = False,
                    margen: int = 0) -> list[PreparedPayload]:
    """`margen` reserva unidades UTF-16 del límite real de Telegram, sin
    ocuparlas todavía -- lo usa `enqueue_outbox` para cualquier mensaje
    dirigido a una persona (saludo diario, revisión 2026-09-28+2): el
    texto se recorta o se parte ACÁ, al encolar, mucho antes de que
    `despachador._intentar_envio` sepa si le va a anteponer el saludo del
    día -- sin este margen, un mensaje ya justo en el límite se pasaría en
    cuanto se le antepusiera "👋 Buenas noches\\n\\n". Por omisión es 0: no
    cambia nada para quien no lo pasa (transporte, banco, cualquier llamada
    vieja)."""
    normalized = normalize_visible_text(text)
    if not normalized:
        raise PayloadValidationError("El mensaje visible no puede quedar vacío.")
    prepared_buttons = prepare_buttons(buttons)
    has_buttons = has_buttons or bool(prepared_buttons)
    limit = (BUTTON_TEXT_LIMIT if has_buttons else TELEGRAM_TEXT_LIMIT) - margen
    if telegram_utf16_units(normalized) <= limit:
        return [PreparedPayload(normalized, dedupe_key)]
    if has_buttons:
        raise PayloadValidationError(
            f"Un mensaje con botones no puede exceder {limit} unidades UTF-16.")
    if not allow_split:
        raise PayloadValidationError(
            f"El mensaje no puede exceder {limit} unidades UTF-16.")

    chunks = _split(normalized)
    total = len(chunks)
    result = []
    for index, chunk in enumerate(chunks, 1):
        rendered = f"({index}/{total})\n{chunk}"
        if telegram_utf16_units(rendered) > TELEGRAM_TEXT_LIMIT - margen:
            raise PayloadValidationError("No se pudo dividir el mensaje de forma segura.")
        result.append(PreparedPayload(
            rendered, f"{dedupe_key}:part:{index:03d}-of-{total:03d}"))
    return result


def _split(text: str) -> list[str]:
    chunks = []
    remaining = text
    while telegram_utf16_units(remaining) > _SPLIT_BODY_LIMIT:
        end = _prefix_index(remaining, _SPLIT_BODY_LIMIT)
        candidate = remaining[:end]
        floor = max(1, int(end * 0.6))
        boundaries = [candidate.rfind("\n\n", floor),
                      candidate.rfind("\n", floor),
                      candidate.rfind(" ", floor)]
        boundary = max(boundaries)
        if boundary > 0:
            end = boundary
        chunks.append(remaining[:end].rstrip())
        remaining = remaining[end:].lstrip()
    if remaining:
        chunks.append(remaining)
    return chunks


def _prefix_index(text: str, max_units: int) -> int:
    low, high = 0, len(text)
    while low < high:
        middle = (low + high + 1) // 2
        if telegram_utf16_units(text[:middle]) <= max_units:
            low = middle
        else:
            high = middle - 1
    return low


def margen_saludo(*, personal: bool) -> int:
    """Cuánto hay que reservarle al saludo diario en el presupuesto de un
    mensaje -- `saludo.MARGEN_SALUDO` si `personal` (tiene
    `recipient_membership_id`: nunca uno de grupo), 0 si no. Importado
    adentro, no al nivel del módulo: `saludo.py` ya importa de acá
    (`telegram_utf16_units`); importarlo arriba armaría un ciclo.

    Única fuente de este número (R4-001, revisión 2026-09-28+3): antes
    `enqueue_outbox` lo calculaba a mano y `agente._encolar_texto_con_
    opciones` decidía si un texto "entra con los botones" contra el límite
    COMPLETO, sin este descuento -- un texto en esa ventana exacta pasaba
    esa decisión y `enqueue_outbox` lo rechazaba después, en todos los
    reintentos. Todo el que decida si un texto entra, antes de encolarlo,
    tiene que usar `cabe_en_mensaje` (más abajo), que ya aplica este mismo
    margen."""
    if not personal:
        return 0
    from .saludo import MARGEN_SALUDO
    return MARGEN_SALUDO


def cabe_en_mensaje(texto: Any, *, has_buttons: bool, personal: bool = True) -> bool:
    """Si `texto` entra en un mensaje de Telegram, con el mismo margen del
    saludo diario que después va a aplicar `enqueue_outbox`/`prepare_payload`
    -- la única función que cualquier punto de salida tiene que usar para
    decidir "entra o no entra" ANTES de encolar (por ejemplo, para elegir si
    manda el texto largo junto con los botones o aparte), en vez de comparar
    a mano contra `BUTTON_TEXT_LIMIT`/`TELEGRAM_TEXT_LIMIT` -- eso fue
    exactamente el bug de R4-001."""
    limite = (BUTTON_TEXT_LIMIT if has_buttons else TELEGRAM_TEXT_LIMIT) - \
        margen_saludo(personal=personal)
    return telegram_utf16_units(normalize_visible_text(texto)) <= limite


def enqueue_outbox(cur, *, workspace_id: str, chat_id: int,
                   text: Any, dedupe_key: str,
                   recipient_membership_id: str | None = None,
                   message_type: str = "normal", state: str = "listo",
                   scheduled_for: datetime | None = None,
                   expires_at: datetime | None = None,
                   is_response: bool = False,
                   pending_action_id: str | None = None,
                   intake_choice_set_id: str | None = None,
                   allow_split: bool = False,
                   es_bienvenida: bool = False,
                   bloque_copiable: str | None = None,
                   grupo_respuesta: str | None = None) -> int:
    """Encola un mensaje visible. `grupo_respuesta` (T9-R2) nombra la respuesta
    de la que esta fila es una parte cuando una respuesta se encola en varias
    llamadas (el texto y aparte el mensaje con los botones): el control de "una
    respuesta por mensaje" cuenta un grupo como UNA respuesta. Sin él, cada
    llamada es su propia respuesta. `bloque_copiable` (T9-R1c-3) es lo que la
    persona había escrito, para que lo copie con un toque: el final del texto
    (`entidad_de_bloque`), que el transporte marca como bloque y, si entra en
    `COPY_TEXT_LIMIT`, también sale con el botón de copiar. Un mensaje con
    bloque no se parte."""
    if bloque_copiable is not None:
        bloque_copiable = normalize_visible_text(bloque_copiable)
        if allow_split or not normalize_visible_text(text).endswith(bloque_copiable):
            raise PayloadValidationError(
                "El bloque copiable tiene que ser el final de un mensaje que "
                "no se parte.")
        entidad_de_bloque(normalize_visible_text(text), bloque_copiable)
    has_buttons = (pending_action_id is not None or intake_choice_set_id is not None
                   or (bloque_copiable is not None
                       and cabe_en_boton_de_copiar(bloque_copiable)))
    # Cualquier mensaje dirigido a una persona (nunca uno de grupo, que no
    # trae `recipient_membership_id`) reserva el margen del saludo diario
    # ANTES de partir/recortar -- `despachador._intentar_envio` decide recién
    # al enviar si de verdad le antepone el saludo (revisión 2026-09-28+2).
    margen = margen_saludo(personal=recipient_membership_id is not None)
    payloads = prepare_payload(
        text, dedupe_key=dedupe_key, has_buttons=has_buttons,
        allow_split=allow_split, margen=margen,
    )
    # Defecto pre-existente encontrado en la revisión del orquestador sobre
    # T3a (`tests/test_lista_botones.py:511-512`): un mensaje partido manda
    # todas sus partes con el mismo `scheduled_for`, y `despachador.despachar`
    # sólo ordena `by programado_para` (`despachador.py:299`) -- el `id` de
    # `message_outbox` es un `uuid` al azar que no sirve de desempate, así que
    # el orden entre partes con la misma marca queda librado al azar del
    # orden físico con el que Postgres devuelva las filas. Cada parte avanza
    # un microsegundo sobre la anterior a partir de la misma base; sin
    # `scheduled_for`, esa base sigue siendo `now()` de la base de datos (la
    # hora de inicio de la transacción, igual para todas las filas del bucle:
    # justamente por eso el desplazamiento por parte alcanza para desempatar),
    # nunca el reloj de la aplicación. Postgres guarda `timestamptz` con
    # precisión de microsegundos, y el caso de siempre (un solo mensaje,
    # desplazamiento 0) no cambia.
    inserted = 0
    for index, payload in enumerate(payloads):
        cur.execute(
            """insert into message_outbox
                 (workspace_id, chat_id, destinatario_membership_id, tipo, cuerpo,
                  estado, programado_para, vence_en, dedupe_key, es_respuesta,
                  pending_action_id, intake_choice_set_id, es_bienvenida,
                  bloque_copiable, respuesta_grupo)
               values (%s, %s, %s, %s, %s, %s,
                       coalesce(%s, now()) + %s * interval '1 microsecond',
                       %s, %s, %s, %s, %s, %s, %s, %s)
               on conflict (dedupe_key) do nothing""",
            (workspace_id, chat_id, recipient_membership_id, message_type,
             payload.text, state, scheduled_for, index,
             expires_at, payload.dedupe_key,
             is_response, pending_action_id, intake_choice_set_id, es_bienvenida,
             bloque_copiable, grupo_respuesta),
        )
        inserted += cur.rowcount
    return inserted
