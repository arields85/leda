"""La medición de la ayuda de la IA al cargar (porción J2 de `odd/tasks/plataforma-jerarquias.md`):
pedidos escritos como en un chat real, la misma función que usa la web y los mismos controles del
código, contra la IA que se elija. **No se corre sin permiso del usuario**: con una IA real gasta
unas 20 llamadas por vuelta (20 pedidos: 13 propuestas, cada una con una llamada más cuando la IA
da una manera de comprobarla, que se juzga por su sentido, J2-13; y 7 criterios escritos para
juzgar al cargar, de los que el igual al título se rechaza sin la IA).

    $env:PYTHONPATH = "src"
    .venv\\Scripts\\python.exe tools\\medir_ayuda_al_cargar.py --ia sol-suscripcion --veces 3

`--ia guionada` (lo de omisión) corre en seco, sin red: una IA de mentira con un guion para el
ejemplo del usuario, el sábado, "antes del jueves", el PLC, el UPS de la prueba del usuario (con
la comprobación circular que dio la IA real) y los juicios de los criterios (lo que tendría que
contestar una IA que entendió), y nada para los demás; así la corrida en seco prueba los controles
y la comparación: da 12 de 20 (sale con 1).
`--ia PROVEEDOR/MODELO` (o `sol-suscripcion`, la suscripción de ChatGPT del usuario) usa la IA
real. Sin base de datos: el equipo, los objetivos, las tareas y los días son fijos (hoy, el
miércoles 14 de octubre de 2026), y quién la hace se busca con la misma función que el servidor,
`fichas.integrantes_que_coinciden`, sobre el equipo fijo (`EquipoFijo`; un pedido puede traer sus
apodos, como el del UPS, donde "el tano" no es nadie, como en `leda_motor`). Cada pedido dice qué
tiene que proponer Leda y qué no; el informe dice, por pedido y por vuelta, qué propuso, qué no
pasó los controles y por qué, cuántos segundos tardó la IA, y separa lo que es de la IA (no
respondió) de un error del programa.

Sale con 0 si todo dio lo esperado, 1 si algo no, 3 si el programa falló (corta en ese pedido,
para no gastar más llamadas) y 4 si la IA se quedó sin cupo (como el corredor de las
conversaciones). Con `--salida`, el informe se escribe siempre, también al cortar.
"""

from __future__ import annotations

import argparse
import errno
import json
import socket
import ssl
import sys
import time
import traceback
from datetime import date, timedelta
from typing import Any

import httpx

from leda import ayuda_al_cargar
from leda.motor import fichas
from leda.motor.ia_real import RespuestaInvalida

ALIAS = {"sol": "openrouter/openai/gpt-6-sol", "sol-suscripcion": "chatgpt/gpt-6-sol"}
GUIONADA = "guionada"
ERROR_DEL_PROGRAMA = 3
SIN_CUPO = 4

HOY = date(2026, 10, 14)        # miércoles


def _habiles(desde: date, dias: int = 120) -> list[str]:
    return [(desde + timedelta(days=n)).isoformat() for n in range(dias)
            if (desde + timedelta(days=n)).weekday() < 5]


def _integrante(mid: str, nombre: str, area_id: str, area: str) -> dict[str, Any]:
    return {"membership_id": mid, "nombre": nombre, "area_id": area_id, "area": area,
            "autoridad_final": mid == "m-ismael", "conectado": True,
            "revisa": None if mid == "m-ismael" else {"membership_id": "m-ismael",
                                                      "nombre": "Ismael Soschinski"}}


OPCIONES: dict[str, Any] = {
    "espacio": {"id": "ws-medicion", "nombre": "CoreWork",
                "zona_horaria": "America/Argentina/Buenos_Aires"},
    "hoy": HOY.isoformat(),
    "objetivos": [
        {"id": "o-modem", "titulo": "Instalar el módem de la sala", "tipo": "operativo",
         "estado": "activo", "fecha_objetivo": "2026-10-30"},
        {"id": "o-linea", "titulo": "Puesta en marcha de la línea 3", "tipo": "operativo",
         "estado": "activo", "fecha_objetivo": "2026-11-20"},
        {"id": "o-anual", "titulo": "Mantenimiento anual", "tipo": "operativo",
         "estado": "activo", "fecha_objetivo": None},
    ],
    "tareas": [
        {"id": "t-tablero", "titulo": "Cablear el tablero de la máquina 3", "estado": "en_curso",
         "fecha_objetivo": "2026-10-15", "responsable": "Marcos Díaz",
         "objetivo": "Instalar el módem de la sala"},
        {"id": "t-plc", "titulo": "Programar el PLC de la línea 3", "estado": "asignada",
         "fecha_objetivo": "2026-10-23", "responsable": "Marcos Díaz",
         "objetivo": "Puesta en marcha de la línea 3"},
    ],
    "integrantes": [
        _integrante("m-lucas", "Lucas Pérez", "a-infra", "Infraestructura"),
        _integrante("m-marcos", "Marcos Díaz", "a-auto", "Automatización"),
        _integrante("m-ismael", "Ismael Soschinski", "a-dir", "Dirección"),
    ],
    "politicas": [
        {"area_id": "a-infra", "area": "Infraestructura", "evidencia_requerida": ["foto"],
         "version": 1, "tipos": {"foto": {"clases": ["imagen"], "en_palabras": "una foto"}}},
        {"area_id": "a-auto", "area": "Automatización", "evidencia_requerida": ["captura"],
         "version": 1, "tipos": {"captura": {"clases": ["imagen"],
                                             "en_palabras": "una captura de pantalla"}}},
    ],
    "calendario": {"dias": ["lunes", "martes", "miercoles", "jueves", "viernes"],
                   "hasta": "2027-04-14", "feriados": [], "dias_habiles": _habiles(HOY)},
}
OBJETIVO_DE = {"t-tablero": "o-modem", "t-plc": "o-linea"}
APODOS = {"m-marcos": ["el tano"]}

# Cada pedido: lo que escribió la persona, como en un chat real; lo que Leda tiene que proponer
# (con su valor, o `True` para un texto que sólo tiene que pasar los controles), lo que no y lo que
# tiene que descartar con su motivo (`descarta`). J2-13: sin quién la hace (o sin evidencia de su
# área) y sin que la persona diga cómo se comprueba, el criterio no se propone: el campo pide cómo
# se sabe (`sin_como_se_comprueba`).
SIN_COMO = ["criterio", "sin_como_se_comprueba"]
PEDIDOS: list[dict[str, Any]] = [
    {"nombre": "el ejemplo del usuario",
     "texto": "hay que colgar el estante del modem en la sala que lo haga lucas necesita 12 "
              "tornillos de 8 mm para el viernes no puede hasta que terminen de cablear el "
              "tablero de la maquina 3",
     "propone": {"titulo": True, "descripcion": True, "criterio": True,
                 "responsable_id": "m-lucas", "espera_id": "t-tablero",
                 "objetivo_id": "o-modem", "fecha": "2026-10-16"}},
    {"nombre": "los tornillos, sin quién ni cuándo",
     "texto": "faltan los tornillos para colgar el estante, necesito 12 de 8 mm",
     "propone": {"titulo": True},
     "no_propone": ["responsable_id", "fecha", "espera_id", "criterio"], "descarta": [SIN_COMO]},
    {"nombre": "un apodo y un día de la semana",
     "texto": "hay q cambiar el ups de la sala de servidores que lo vea el tano antes del "
              "jueves porq se corta todo",
     # "Antes del jueves" no es el jueves (el usuario, 2026-10-13): hoy es el miércoles 14 y es
     # hábil, así que el día hábil anterior al jueves 15 es hoy.
     "propone": {"titulo": True, "criterio": True, "responsable_id": "m-marcos",
                 "fecha": "2026-10-14"}},
    {"nombre": "mañana, con el nombre en el medio",
     "texto": "revisar las alarmas del scada q no suenan en la sala de control marcos lo tiene "
              "q hacer para mañana",
     "propone": {"titulo": True, "criterio": True, "responsable_id": "m-marcos",
                 "fecha": "2026-10-15"}},
    {"nombre": "sin apuro",
     "texto": "pedir presupuesto de cables para el tablero 4 sin apuro",
     "propone": {"titulo": True},
     "no_propone": ["responsable_id", "fecha", "espera_id", "criterio"], "descarta": [SIN_COMO]},
    {"nombre": "un sábado no es hábil",
     "texto": "lucas tiene que pintar el cartel de la entrada el sabado",
     "propone": {"titulo": True, "responsable_id": "m-lucas"},
     "no_propone": ["fecha"]},
    {"nombre": "alguien que no es del equipo",
     "texto": "que lo haga pepe, ordenar el deposito para la semana que viene",
     "propone": {"titulo": True},
     "no_propone": ["responsable_id"]},
    {"nombre": "dos personas nombradas",
     "texto": "lucas y marcos tienen q probar el modem nuevo cuando terminen de cablear el "
              "tablero de la maquina 3",
     "propone": {"titulo": True, "espera_id": "t-tablero", "objetivo_id": "o-modem"},
     "no_propone": ["responsable_id", "fecha"]},
    {"nombre": "el número del día",
     "texto": "configurar la vpn pa los de campo el 20 que lo haga lucas",
     "propone": {"titulo": True, "responsable_id": "m-lucas", "fecha": "2026-10-20"}},
    {"nombre": "una espera por su nombre de todos los días",
     "texto": "probar la linea 3 entera despues de q marcos termine el plc la semana q viene",
     "propone": {"titulo": True, "espera_id": "t-plc", "objetivo_id": "o-linea"}},
    {"nombre": "con faltas y todo junto",
     "texto": "cmabiar la bateria del ups lucas el lunes q biene no se puede antes xq falta la "
              "bateria q pidio ismael",
     "propone": {"titulo": True, "responsable_id": "m-lucas"},
     "no_propone": ["espera_id"]},
    # J2-9 y J2-13: la persona no dijo cómo se comprueba ni quién la hace: Leda no inventa una
    # manera (en el celular dio una circular), el campo pide cómo se sabe.
    {"nombre": "el PLC, sin quién ni cómo se comprueba",
     "texto": "hay que dejar el plc de la comprimidora fette 2000 y sus variables listos para "
              "que ariel la integre a la interfaz",
     "propone": {"titulo": True}, "no_propone": ["criterio"], "descarta": [SIN_COMO]},
    # J2-13: el pedido de la prueba del usuario, tal cual (2026-10-13). En `leda_motor` "el tano"
    # no es el apodo de nadie, así que no hay quién la hace ni evidencia de su área: la
    # comprobación circular que dio la IA real se rechaza por su sentido y no se inventa otra.
    {"nombre": "el UPS de la prueba del usuario",
     "texto": "hay que cambiar el ups de la sala de servidores que lo vea el tano antes del "
              "jueves se corta todo",
     "apodos": {},
     "propone": {"titulo": True, "fecha": "2026-10-14"},
     "no_propone": ["responsable_id", "criterio"], "descarta": [SIN_COMO]},
    # J2-9 y J2-13: el criterio que escribió la persona, juzgado al cargar por su sentido
    # (`juicio`: lo que tiene que decidir el código; `None` es que dice cómo se comprueba).
    {"nombre": "el criterio circular del usuario", "titulo": "Integrar el PLC de la Fette 2000",
     "criterio_escrito": "El PLC de la comprimidora Fette 2000 y sus variables quedan listos para "
                         "que Ariel la integre a la interfaz. Se comprueba revisando que el PLC "
                         "y sus variables estén listos para esa integración.",
     "juicio": "sin_comprobacion"},
    {"nombre": "un criterio con una comprobación concreta",
     "titulo": "Integrar el PLC de la Fette 2000",
     "criterio_escrito": "El PLC de la comprimidora Fette 2000 y sus variables quedan listos para "
                         "que Ariel la integre a la interfaz. Las variables del PLC se leen bien "
                         "desde la interfaz.",
     "juicio": None},
    {"nombre": "un criterio con palabras y sin comprobación", "titulo": "Colocar el estante",
     "criterio_escrito": "Hacerlo con cuidado y prolijidad", "juicio": "sin_comprobacion"},
    {"nombre": "no se", "titulo": "Colocar el estante", "criterio_escrito": "No se",
     "juicio": "sin_comprobacion"},
    {"nombre": "el UPS circular, escrito", "titulo": "Cambiar el UPS de la sala de servidores",
     "criterio_escrito": "El UPS de la sala de servidores está cambiado. Se comprueba verificando "
                         "en la sala de servidores que el UPS fue reemplazado.",
     "juicio": "sin_comprobacion"},
    # Sin la lista de palabras de la J2-9: "revisa" y "queda" no deciden nada.
    {"nombre": "un criterio concreto con palabras de revisar",
     "titulo": "Cambiar la batería del UPS",
     "criterio_escrito": "Se revisa que el UPS quede encendido con la batería nueva y aguante 10 "
                         "minutos sin luz.",
     "juicio": None},
    # La única guarda sin la IA: un criterio igual al título.
    {"nombre": "igual al título", "titulo": "Colocar el estante",
     "criterio_escrito": "Colocar el estante.", "juicio": "sin_comprobacion"},
]

VACIO = {c: "" for c in ayuda_al_cargar.CAMPOS}

# Lo que propone la IA en seco: lo que propondría una IA que entendió el ejemplo del usuario, un
# sábado (que los controles no dejan poner), "antes del jueves" (el miércoles) y el PLC; y, en el
# UPS de la prueba del usuario, lo que propuso la IA real (una comprobación circular). Los demás
# pedidos, sin guion: no propone nada.
GUION: dict[str, dict[str, str]] = {
    "el ejemplo del usuario": {
        "titulo": "Colgar el estante del módem en la sala",
        "descripcion": "Colgar el estante del módem en la sala. Hacen falta 12 tornillos de 8 mm. "
                       "No se puede empezar hasta que terminen de cablear el tablero de la "
                       "máquina 3.",
        "resultado": "El estante del módem está colgado en la sala con los 12 tornillos de 8 mm",
        "como_se_comprueba": "",
        "responsable": "lucas", "espera": "T1", "objetivo": "O1",
        "fecha": "2026-10-16", "como_dijo_la_fecha": "para el viernes"},
    "un sábado no es hábil": {
        "titulo": "Pintar el cartel de la entrada", "responsable": "lucas",
        "fecha": "2026-10-17", "como_dijo_la_fecha": "el sabado"},
    "un apodo y un día de la semana": {
        "titulo": "Cambiar el UPS de la sala de servidores",
        "resultado": "El UPS de la sala de servidores está cambiado", "como_se_comprueba": "",
        "responsable": "el tano", "fecha": "2026-10-14", "como_dijo_la_fecha": "antes del jueves"},
    "el PLC, sin quién ni cómo se comprueba": {
        "titulo": "Dejar listo el PLC de la comprimidora Fette 2000",
        "resultado": "El PLC de la comprimidora Fette 2000 y sus variables quedan listos para que "
                     "Ariel la integre a la interfaz",
        "como_se_comprueba": ""},
    "el UPS de la prueba del usuario": {
        "titulo": "Cambiar el UPS de la sala de servidores",
        "resultado": "El UPS de la sala de servidores está cambiado",
        "como_se_comprueba": "se comprueba verificando en la sala de servidores que el UPS fue "
                             "reemplazado",
        "responsable": "el tano", "fecha": "2026-10-14", "como_dijo_la_fecha": "antes del jueves"},
}
# Lo que contesta en seco el juicio de un criterio (escrito o propuesto), por su texto: lo que
# diría una IA que lo juzga por su sentido.
NO_LO_DICE = {"dice_como_se_comprueba": False, "como_se_comprueba": ""}
GUION_DEL_JUICIO: dict[str, dict[str, Any]] = {
    "El PLC de la comprimidora Fette 2000 y sus variables quedan listos para que Ariel la integre "
    "a la interfaz. Se comprueba revisando que el PLC y sus variables estén listos para esa "
    "integración.": NO_LO_DICE,
    "El PLC de la comprimidora Fette 2000 y sus variables quedan listos para que Ariel la integre "
    "a la interfaz. Las variables del PLC se leen bien desde la interfaz.":
        {"dice_como_se_comprueba": True,
         "como_se_comprueba": "Las variables del PLC se leen bien desde la interfaz"},
    "Hacerlo con cuidado y prolijidad": NO_LO_DICE,
    "No se": NO_LO_DICE,
    "El UPS de la sala de servidores está cambiado. Se comprueba verificando en la sala de "
    "servidores que el UPS fue reemplazado.": NO_LO_DICE,
    "Se revisa que el UPS quede encendido con la batería nueva y aguante 10 minutos sin luz.":
        {"dice_como_se_comprueba": True,
         "como_se_comprueba": "Se revisa que el UPS quede encendido con la batería nueva y "
                              "aguante 10 minutos sin luz"},
}


class EquipoFijo:
    """Un cursor sobre el equipo fijo, para buscar quién la hace con la función del servidor tal
    cual (`fichas.integrantes_que_coinciden`), sin base: contesta sus dos lecturas, los apodos
    vigentes (`apodos.vigentes`, los de `APODOS` o los del pedido) y los integrantes activos. Otra
    consulta es un error del programa, no una respuesta vacía."""

    def __init__(self, apodos: dict[str, list[str]] | None = None) -> None:
        self._filas: list[dict[str, Any]] = []
        self._apodos = APODOS if apodos is None else apodos

    def execute(self, sql: str, parametros: Any = None) -> None:
        consulta = " ".join(sql.split())
        if "from apodo" in consulta:
            self._filas = [{"membership_id": m, "apodo": a}
                           for m, apodos in self._apodos.items() for a in apodos]
        elif "from integrante" in consulta:
            self._filas = sorted(({"membership_id": i["membership_id"], "nombre": i["nombre"]}
                                  for i in OPCIONES["integrantes"]), key=lambda f: f["nombre"])
        else:
            raise RuntimeError(f"Consulta que el equipo fijo no sabe contestar: {consulta[:80]}")

    def fetchall(self) -> list[dict[str, Any]]:
        return self._filas


def coinciden(dicho: str, apodos: dict[str, list[str]] | None = None) -> list[dict[str, Any]]:
    """Los integrantes del equipo fijo que coinciden con lo dicho, con la función del servidor."""
    return fichas.integrantes_que_coinciden(EquipoFijo(apodos), dicho)


class IAEnSeco:
    """Sin red: contesta la herramienta con el guion del pedido (por su texto), o sin proponer
    nada."""

    nombre = GUIONADA

    def __init__(self) -> None:
        self.cliente = self
        self.parametros: dict[str, Any] = {}
        self._por_texto = {p["texto"]: GUION.get(p["nombre"], {}) for p in PEDIDOS
                           if "texto" in p}

    def completar(self, cuerpo: dict[str, Any], al_avanzar=None) -> dict[str, Any]:
        entrada = json.loads(next(m["content"] for m in cuerpo["messages"]
                                  if m["role"] == "user"))
        nombre = cuerpo["tools"][0]["function"]["name"]
        if nombre == ayuda_al_cargar.NOMBRE_DEL_JUICIO:
            datos: dict[str, Any] = GUION_DEL_JUICIO.get(entrada["criterio"], {})
        else:
            datos = self._por_texto.get(entrada["texto"], {})
        return {"choices": [{"finish_reason": "tool_calls", "message": {"tool_calls": [
            {"function": {"name": nombre,
                          "arguments": json.dumps(datos, ensure_ascii=False)}}]}}]}


def la_ia(texto: str):
    """La IA de `--ia`: en seco, o la real (la clave, del entorno; nunca se imprime)."""
    if texto == GUIONADA:
        return IAEnSeco()
    completo = ALIAS.get(texto, texto)
    proveedor, _, modelo = completo.partition("/")
    if not modelo:
        raise SystemExit(f"--ia es {GUIONADA}, {', '.join(ALIAS)} o PROVEEDOR/MODELO.")
    from leda.llm import BASE_URLS, PROVEEDORES_CON_SESION
    from leda.motor.ia_real import ClienteCompatible, IAReal, validar_parametros

    if proveedor in PROVEEDORES_CON_SESION:
        from leda.motor.chatgpt import (ClienteChatGPT, SesionChatGPT,
                                        validar_parametros_chatgpt)
        try:
            sesion = SesionChatGPT.abrir()
        except (LookupError, ValueError) as e:
            raise SystemExit(str(e)) from None
        cliente = ClienteChatGPT.crear(modelo, sesion, validar_parametros_chatgpt({}))
    else:
        from leda.config import config

        clave = config.clave_llm(proveedor)
        if not clave:
            raise SystemExit(f"Falta {config.variable_clave_llm(proveedor)} en el entorno.")
        cliente = ClienteCompatible.crear(modelo, clave, BASE_URLS[proveedor],
                                          validar_parametros({}))
    return IAReal(cliente, None, nombre=completo)


def _sin_cupo(falla: BaseException) -> bool:
    respuesta = getattr(falla, "response", None)
    return getattr(respuesta, "status_code", None) in (402, 429)


def _fallas_de_la_ia() -> tuple[type[BaseException], ...]:
    """Lo que dice que la IA no respondió, como lo trata la web (`ayuda_al_cargar.pedir`): sin
    configurar o sin sesión, una respuesta ilegible o cortada, el plazo, la red, el HTTP y un
    error del servicio de ChatGPT. Cualquier otra excepción es un error del programa: también
    `KeyError` e `IndexError`, que son `LookupError`, y un `OSError` que no es de la red, como un
    archivo que falta (revisión `review-f7886a8a6481af78`; `_es_de_la_ia`)."""
    fallas: tuple[type[BaseException], ...] = (RespuestaInvalida, LookupError, TimeoutError,
                                               ConnectionError, httpx.HTTPError)
    try:
        from leda.motor.chatgpt import ErrorDeChatGPT
    except ImportError:
        return fallas
    return (*fallas, ErrorDeChatGPT)


# Los errores de la red que no son `ConnectionError` ni `TimeoutError`: no encontrar el servidor,
# el certificado y una red inalcanzable (revisión `review-ded34de579ff3bc5`). Un archivo que falta
# sigue siendo un error del programa.
_DE_LA_RED = (socket.gaierror, socket.herror, ssl.SSLError)
_ERRNO_DE_LA_RED = frozenset(getattr(errno, n) for n in (
    "ENETUNREACH", "ENETDOWN", "ENETRESET", "EHOSTUNREACH", "EHOSTDOWN") if hasattr(errno, n))


def _es_de_la_ia(falla: BaseException) -> bool:
    if isinstance(falla, _DE_LA_RED) or (isinstance(falla, OSError)
                                         and falla.errno in _ERRNO_DE_LA_RED):
        return True
    return (isinstance(falla, _fallas_de_la_ia())
            and not isinstance(falla, (KeyError, IndexError)))


class SinCupo(Exception):
    """La IA se quedó sin cupo: la medición se corta."""


def _de_la_ia(falla: BaseException) -> dict[str, Any]:
    """Una falla al llamar a la IA: sin cupo, `SinCupo`; de la IA, el resultado que lo dice; un
    error del programa se levanta tal cual."""
    if _sin_cupo(falla):
        raise SinCupo() from falla
    if _es_de_la_ia(falla):
        return {"falla": "ia", "fallas": [f"la IA no respondió ({type(falla).__name__})"]}
    raise falla


def medir_el_juicio(ia, pedido: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    """Un criterio escrito, juzgado como al cargar (`juzgar_el_criterio`): si el código decidió
    lo esperado. Que la IA no lo juzgara (`sin_revisar`) es una falla de la IA o, si su causa no
    es de la IA, un error del programa."""
    desde = time.monotonic()
    juicio = ayuda_al_cargar.juzgar_el_criterio(ia, titulo=pedido["titulo"], descripcion="",
                                                criterio=pedido["criterio_escrito"])
    segundos = round(time.monotonic() - desde, 2)
    if juicio.motivo == "sin_revisar":
        return False, {**_de_la_ia(juicio.falla or RespuestaInvalida("sin juicio")),
                       "segundos": segundos}
    fallas = [] if juicio.motivo == pedido["juicio"] else [
        f"juicio: esperaba {pedido['juicio']!r}, vino {juicio.motivo!r}"]
    return not fallas, {"falla": None, "juicio": juicio.motivo, "segundos": segundos,
                        "fallas": fallas}


def medir(ia, pedido: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    """Un pedido, una vez: si dio lo esperado y lo que pasó. Una falla de la IA vuelve como un
    resultado (`falla: ia`); sin cupo, `SinCupo`; un error del programa se levanta tal cual."""
    if "criterio_escrito" in pedido:
        return medir_el_juicio(ia, pedido)
    entrada = ayuda_al_cargar.entrada_de_la_ia(pedido["texto"], VACIO, OPCIONES)
    desde = time.monotonic()
    try:
        crudo = ayuda_al_cargar.pedir(ia, entrada)
    except Exception as falla:
        return False, {**_de_la_ia(falla), "segundos": round(time.monotonic() - desde, 2)}
    segundos = round(time.monotonic() - desde, 2)
    # Como la web: la manera de comprobarla que dio la IA se juzga por su sentido (J2-13). Si el
    # juicio no responde, la propuesta sigue como en la web (con la evidencia del área), salvo sin
    # cupo o con un error del programa; y, como en `medir_el_juicio`, es una falla de la IA: el
    # pedido sale mal y el informe lo dice (revisión `review-bfa79042ca12447b`).
    desde = time.monotonic()
    juicio = ayuda_al_cargar.juzgar_la_propuesta(ia, crudo, VACIO)
    del_juicio = round(time.monotonic() - desde, 2) if juicio is not None else None
    falla_del_juicio = None
    if juicio is not None and juicio.motivo == "sin_revisar":
        (falla_del_juicio,) = _de_la_ia(juicio.falla or RespuestaInvalida("sin juicio"))["fallas"]
    apodos = pedido.get("apodos")
    r = ayuda_al_cargar.revisar(crudo, texto=pedido["texto"], escrito=VACIO, opciones=OPCIONES,
                                coinciden=lambda dicho: coinciden(dicho, apodos),
                                objetivo_de=OBJETIVO_DE.get, juicio=juicio)
    fallas = [] if falla_del_juicio is None else [f"juicio: {falla_del_juicio}"]
    for campo, esperado in pedido.get("propone", {}).items():
        valor = r.propuesta.get(campo)
        if valor is None or (esperado is not True and valor != esperado):
            fallas.append(f"{campo}: esperaba {'un texto' if esperado is True else esperado}, "
                          f"vino {valor!r}")
    for campo in pedido.get("no_propone", []):
        if campo in r.propuesta:
            fallas.append(f"{campo}: no tenía que proponerlo y propuso {r.propuesta[campo]!r}")
    for campo, motivo in pedido.get("descarta", []):
        if {"campo": campo, "motivo": motivo} not in r.descartados:
            fallas.append(f"{campo}: esperaba descartarlo por {motivo}")
    return not fallas, {"falla": None if falla_del_juicio is None else "ia",
                        "falla_del_juicio": falla_del_juicio, "propuesta": r.propuesta,
                        "avisos": [a["texto"] for a in r.avisos],
                        "descartados": r.descartados, "elegir": r.elegir,
                        "juicio": None if juicio is None else (juicio.motivo or "lo_dice"),
                        "segundos": segundos, "segundos_del_juicio": del_juicio,
                        "fallas": fallas}


def _al_menos_una(valor: str) -> int:
    veces = int(valor)
    if veces < 1:
        raise argparse.ArgumentTypeError("tiene que ser 1 o más")
    return veces


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--ia", default=GUIONADA)
    p.add_argument("--veces", type=_al_menos_una, default=1)
    p.add_argument("--salida", help="un archivo para el informe en JSON")
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")    # la consola de Windows
    except (AttributeError, ValueError):
        pass
    ia = la_ia(args.ia)
    nombre = getattr(ia, "nombre", args.ia)
    resultados: list[dict[str, Any]] = []
    bien = total = 0
    cortada: str | None = None
    for vuelta in range(1, args.veces + 1):
        for pedido in PEDIDOS:
            try:
                ok, detalle = medir(ia, pedido)
            except SinCupo:
                print("La IA se quedó sin cupo: la medición se corta acá.")
                cortada = "sin_cupo"
                break
            except Exception as falla:  # noqa: BLE001 -- se informa, nunca se esconde
                traceback.print_exc()
                print("Error del programa (no de la IA): la medición se corta acá.")
                ok, detalle = False, {"falla": "programa", "fallas": [
                    f"error del programa ({type(falla).__name__}: {str(falla)[:200]})"]}
                cortada = "error_del_programa"
            total += 1
            bien += ok
            resultados.append({"vuelta": vuelta, "pedido": pedido["nombre"], "bien": ok,
                               **detalle})
            print(f"[{vuelta}] {'bien' if ok else 'MAL '} · {pedido['nombre']}")
            for f in detalle.get("fallas", []):
                print(f"        {f}")
            if cortada:
                break
        if cortada:
            break
    print(f"\n{bien} de {total} bien (IA: {nombre})"
          f"{'; cortada: ' + cortada.replace('_', ' ') if cortada else ''}.")
    if args.salida:
        with open(args.salida, "w", encoding="utf-8") as archivo:
            json.dump({"ia": nombre, "veces": args.veces, "cortada": cortada, "bien": bien,
                       "total": total, "resultados": resultados},
                      archivo, ensure_ascii=False, indent=2)
    if cortada == "sin_cupo":
        return SIN_CUPO
    if cortada == "error_del_programa":
        return ERROR_DEL_PROGRAMA
    return 0 if bien == total else 1


if __name__ == "__main__":
    sys.exit(main())
