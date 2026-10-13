"""La medición de la ayuda de la IA al cargar (porción J2 de `odd/tasks/plataforma-jerarquias.md`):
pedidos escritos como en un chat real, la misma función que usa la web y los mismos controles del
código, contra la IA que se elija. **No se corre sin permiso del usuario**: con una IA real gasta
una llamada por pedido y vuelta (11 pedidos).

    $env:PYTHONPATH = "src"
    .venv\\Scripts\\python.exe tools\\medir_ayuda_al_cargar.py --ia sol-suscripcion --veces 3

`--ia guionada` (lo de omisión) corre en seco, sin red: una IA de mentira que no propone nada, para
probar la herramienta. `--ia PROVEEDOR/MODELO` (o `sol-suscripcion`, la suscripción de ChatGPT del
usuario) usa la IA real. Sin base de datos: el equipo, los objetivos, las tareas y los días son
fijos (hoy, el miércoles 14 de octubre de 2026), y quién la hace se busca con las mismas reglas que
`fichas.integrantes_que_coinciden` (nombre y apodos). Cada pedido dice qué tiene que proponer Leda
y qué no; el informe dice, por pedido y por vuelta, qué propuso, qué no pasó los controles y por
qué. Sale con 0 si todo dio lo esperado, 1 si algo no, y 4 si la IA se quedó sin cupo (como el
corredor de las conversaciones).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from typing import Any

from leda import ayuda_al_cargar
from leda.motor.fichas import palabras

ALIAS = {"sol": "openrouter/openai/gpt-6-sol", "sol-suscripcion": "chatgpt/gpt-6-sol"}
GUIONADA = "guionada"
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
# (con su valor, o `True` para un texto que sólo tiene que pasar los controles) y lo que no.
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
     "propone": {"titulo": True, "criterio": True},
     "no_propone": ["responsable_id", "fecha", "espera_id"]},
    {"nombre": "un apodo y un día de la semana",
     "texto": "hay q cambiar el ups de la sala de servidores que lo vea el tano antes del "
              "jueves porq se corta todo",
     "propone": {"titulo": True, "criterio": True, "responsable_id": "m-marcos",
                 "fecha": "2026-10-15"}},
    {"nombre": "mañana, con el nombre en el medio",
     "texto": "revisar las alarmas del scada q no suenan en la sala de control marcos lo tiene "
              "q hacer para mañana",
     "propone": {"titulo": True, "criterio": True, "responsable_id": "m-marcos",
                 "fecha": "2026-10-15"}},
    {"nombre": "sin apuro",
     "texto": "pedir presupuesto de cables para el tablero 4 sin apuro",
     "propone": {"titulo": True, "criterio": True},
     "no_propone": ["responsable_id", "fecha", "espera_id"]},
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
]

VACIO = {c: "" for c in ayuda_al_cargar.CAMPOS}


def coinciden(dicho: str) -> list[dict[str, Any]]:
    """Como `fichas.integrantes_que_coinciden`, sobre el equipo fijo."""
    buscadas = set(palabras(dicho))
    if not buscadas:
        return []
    return [{"membership_id": m["membership_id"], "nombre": m["nombre"]}
            for m in OPCIONES["integrantes"]
            if buscadas <= set(palabras(m["nombre"]))
            or any(buscadas <= set(a.split()) for a in APODOS.get(m["membership_id"], []))]


class IAEnSeco:
    """Sin red: contesta la herramienta sin proponer nada."""

    nombre = GUIONADA

    def __init__(self) -> None:
        self.cliente = self
        self.parametros: dict[str, Any] = {}

    def completar(self, cuerpo: dict[str, Any], al_avanzar=None) -> dict[str, Any]:
        return {"choices": [{"finish_reason": "tool_calls", "message": {"tool_calls": [
            {"function": {"name": ayuda_al_cargar.NOMBRE_HERRAMIENTA, "arguments": "{}"}}]}}]}


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


def medir(ia, pedido: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    """Un pedido, una vez: si dio lo esperado y lo que pasó."""
    entrada = ayuda_al_cargar.entrada_de_la_ia(pedido["texto"], VACIO, OPCIONES)
    crudo = ayuda_al_cargar.pedir(ia, entrada)
    r = ayuda_al_cargar.revisar(crudo, texto=pedido["texto"], escrito=VACIO, opciones=OPCIONES,
                                coinciden=coinciden, objetivo_de=OBJETIVO_DE.get)
    fallas = []
    for campo, esperado in pedido.get("propone", {}).items():
        valor = r.propuesta.get(campo)
        if valor is None or (esperado is not True and valor != esperado):
            fallas.append(f"{campo}: esperaba {'un texto' if esperado is True else esperado}, "
                          f"vino {valor!r}")
    for campo in pedido.get("no_propone", []):
        if campo in r.propuesta:
            fallas.append(f"{campo}: no tenía que proponerlo y propuso {r.propuesta[campo]!r}")
    return not fallas, {"propuesta": r.propuesta, "avisos": [a["texto"] for a in r.avisos],
                        "descartados": r.descartados, "elegir": r.elegir, "fallas": fallas}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--ia", default=GUIONADA)
    p.add_argument("--veces", type=int, default=1)
    p.add_argument("--salida", help="un archivo para el informe en JSON")
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")    # la consola de Windows
    except (AttributeError, ValueError):
        pass
    ia = la_ia(args.ia)
    informe: list[dict[str, Any]] = []
    bien = total = 0
    for vuelta in range(1, args.veces + 1):
        for pedido in PEDIDOS:
            total += 1
            try:
                ok, detalle = medir(ia, pedido)
            except Exception as falla:  # noqa: BLE001 -- se informa, nunca se esconde
                if _sin_cupo(falla):
                    print("La IA se quedó sin cupo: la medición se corta acá.")
                    return SIN_CUPO
                ok, detalle = False, {"fallas": [f"la IA no respondió ({type(falla).__name__})"]}
            bien += ok
            informe.append({"vuelta": vuelta, "pedido": pedido["nombre"], "bien": ok, **detalle})
            print(f"[{vuelta}] {'bien' if ok else 'MAL '} · {pedido['nombre']}")
            for f in detalle.get("fallas", []):
                print(f"        {f}")
    print(f"\n{bien} de {total} bien (IA: {getattr(ia, 'nombre', args.ia)}).")
    if args.salida:
        with open(args.salida, "w", encoding="utf-8") as archivo:
            json.dump(informe, archivo, ensure_ascii=False, indent=2)
    return 0 if bien == total else 1


if __name__ == "__main__":
    sys.exit(main())
