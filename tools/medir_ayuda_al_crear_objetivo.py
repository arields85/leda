"""La medición de la ayuda de la IA al crear un objetivo (porción J3, tarea J3-4 de
`odd/tasks/plataforma-jerarquias.md`): pedidos escritos como en un chat real (sin puntuación, con
faltas de ortografía, todo seguido), la misma función que usa la web
(`ayuda_al_crear_objetivo.pedir` y `revisar`) y los mismos controles del código, contra la IA que
se elija. **No se corre con la IA real sin el coordinador**: gasta una llamada por pedido (19 por
vuelta).

    $env:PYTHONPATH = "src"
    .venv\\Scripts\\python.exe tools\\medir_ayuda_al_crear_objetivo.py --ia sol-suscripcion --veces 3

Cada pedido dice qué tiene que proponer Leda y qué no: de qué cuelga (de la lista), el tipo (uno que
vaya ahí), el referente (sólo un referente de área nombrado en el texto; con dos, para elegir; con
nadie, se dice; J3-4b: si no se nombró a nadie, el del área de la que trata, si se entiende, y si
no, ninguno) y la fecha (sólo si se dijo y el código la entiende, en día hábil; si vence después
que el padre, igual). El nombre y la descripción, que la IA los escriba con naturalidad
(`sin_naturalidad` de la medición de la carga) y sin dejar mal escrito un nombre de los datos.

Comparte con la medición de la carga (`medir_ayuda_al_cargar.py`) la corrida (`correr`: las vueltas,
el informe y la salida), la IA real (`la_ia`), lo que es una falla de la IA o un error del programa
y el corte sin cupo. `--ia guionada` (lo de omisión) corre en seco, sin red: una IA de mentira con
un guion para nueve pedidos (lo que contestaría una IA que entendió) y nada para los demás; da 9 de
19 (sale con 1). Sin base de datos: el equipo, los objetivos y los días son fijos (hoy, el miércoles
14 de octubre de 2026), y el referente se busca con la misma función que el servidor,
`fichas.integrantes_que_coinciden`, sobre el equipo fijo.

Sale con 0 si todo dio lo esperado, 1 si algo no, 3 si el programa falló y 4 si la IA se quedó sin
cupo. Con `--salida`, el informe se escribe siempre, también al cortar.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import medir_ayuda_al_cargar as base  # noqa: E402 -- la medición de la carga, al lado

from leda import ayuda_al_crear_objetivo as ayuda  # noqa: E402
from leda.motor import fichas  # noqa: E402

GUIONADA = base.GUIONADA
ERROR_DEL_PROGRAMA = base.ERROR_DEL_PROGRAMA
SIN_CUPO = base.SIN_CUPO
HOY = base.HOY                  # miércoles 14 de octubre de 2026

OPCIONES: dict[str, Any] = {
    "espacio": {"id": "ws-medicion", "nombre": "CoreWork",
                "zona_horaria": "America/Argentina/Buenos_Aires"},
    "hoy": HOY.isoformat(),
    "niveles": {"estrategico": "objetivo estratégico", "hito": "hito",
                "operativo": "objetivo operativo"},
    "sin_padre": ["estrategico"],
    # Como los ordena la base: por su nombre.
    "padres": [
        {"id": "o-planta", "titulo": "Abrir la planta nueva", "tipo": "estrategico",
         "estado": "activo", "fecha_objetivo": "2026-12-18", "padre_id": None,
         "tipos": ["hito", "operativo"]},
        {"id": "o-linea", "titulo": "Arrancar la línea 3", "tipo": "hito", "estado": "activo",
         "fecha_objetivo": "2026-11-27", "padre_id": "o-planta", "tipos": ["operativo"]},
        {"id": "o-iso", "titulo": "Certificar la ISO 9001", "tipo": "estrategico",
         "estado": "activo", "fecha_objetivo": None, "padre_id": None,
         "tipos": ["hito", "operativo"]},
    ],
    "referentes": [
        {"membership_id": "m-ismael", "nombre": "Ismael Soschinski", "areas": ["Dirección"]},
        {"membership_id": "m-lucas", "nombre": "Lucas Pérez", "areas": ["Infraestructura"]},
        {"membership_id": "m-nahuel", "nombre": "Nahuel Gómez", "areas": ["Calidad"]},
    ],
    "calendario": {"dias": ["lunes", "martes", "miercoles", "jueves", "viernes"],
                   "hasta": "2027-10-14", "feriados": [],
                   "dias_habiles": base._habiles(HOY, 366)},
}

# El equipo entero, para buscar a quien se nombró: Marcos no es referente de ningún área.
EQUIPO = [{"membership_id": "m-ismael", "nombre": "Ismael Soschinski"},
          {"membership_id": "m-lucas", "nombre": "Lucas Pérez"},
          {"membership_id": "m-marcos", "nombre": "Marcos Díaz"},
          {"membership_id": "m-nahuel", "nombre": "Nahuel Gómez"}]
APODOS = {"m-marcos": ["el tano"]}
# Un apodo de dos referentes: Leda no elige (ADR 0020, decisión 3).
DOS_CON_EL_COLO = {"m-lucas": ["el colo"], "m-nahuel": ["el colo"]}

VACIO = {c: "" for c in ayuda.CAMPOS}

PEDIDOS: list[dict[str, Any]] = [
    {"nombre": "el módem colgado",
     "texto": "hay q dejar la sala de servidores ordenada con el modem colgado en la pared q lo "
              "lleve lucas para el viernes 30",
     "propone": {"titulo": True, "tipo": "estrategico", "referente_id": "m-lucas",
                 "fecha": "2026-10-30"},
     "no_propone": ["padre_id"]},
    {"nombre": "parte de la planta nueva, antes de un día",
     "texto": "dentro de lo de la planta nueva tenemos que arrancar la produccion del envasado "
              "antes del 20 de noviembre referente nahuel",
     "propone": {"padre_id": "o-planta", "referente_id": "m-nahuel", "fecha": "2026-11-19"},
     "tipo_en": ["hito", "operativo"]},
    {"nombre": "los operarios de la línea 3",
     "texto": "para arrancar la linea 3 hay que capacitar a los operarios del turno noche, lo ve "
              "ismael, para el 13/11",
     "propone": {"padre_id": "o-linea", "tipo": "operativo", "referente_id": "m-ismael",
                 "fecha": "2026-11-13"}},
    {"nombre": "alguien que no es referente",
     "texto": "objetivo para automatizar el envasado q lo lleve marcos",
     "no_propone": ["referente_id", "fecha"],
     "descarta": [("referente", "no_encontrado")]},
    {"nombre": "un apodo que no es de un referente",
     "texto": "q lo lleve el tano, mejorar el mantenimiento preventivo de las compresoras",
     "no_propone": ["referente_id"],
     "descarta": [("referente", "no_encontrado")]},
    {"nombre": "dos referentes con el mismo apodo",
     "texto": "armar el plan de backups de todos los servidores, que lo lleve el colo",
     "apodos": DOS_CON_EL_COLO,
     "no_propone": ["referente_id", "fecha"],
     "elegir": ["m-lucas", "m-nahuel"]},
    {"nombre": "sin fecha",
     "texto": "hay q preparar la auditoria interna para la iso nahuel se encarga",
     "propone": {"padre_id": "o-iso", "referente_id": "m-nahuel"},
     "no_propone": ["fecha"]},
    {"nombre": "un sábado no es hábil",
     "texto": "renovar los matafuegos de la planta, lo lleva lucas, para el sabado 24",
     "propone": {"referente_id": "m-lucas"},
     "no_propone": ["fecha"],
     "descarta": [("fecha", "no_es_habil")]},
    {"nombre": "un número que no es una fecha",
     "texto": "bajar 15 por ciento el consumo de energia de la planta nueva lo lleva ismael",
     "propone": {"titulo": True, "referente_id": "m-ismael"},
     "no_propone": ["fecha"]},
    {"nombre": "antes de que termine el mes",
     "texto": "nesesitamos el labo de calidad andando antes d q termine noviembre lo ve nahuel",
     "propone": {"referente_id": "m-nahuel"},
     "no_propone": ["fecha"]},
    {"nombre": "alguien de afuera",
     "texto": "q lo lleve pepe, ordenar el deposito de repuestos",
     "no_propone": ["referente_id"],
     "descarta": [("referente", "no_encontrado")]},
    {"nombre": "el viernes de la semana que viene",
     "texto": "migrar el correo a la nube, lucas, para el viernes de la semana que viene",
     "propone": {"referente_id": "m-lucas", "fecha": "2026-10-23"}},
    {"nombre": "mañana",
     "texto": "para mañana dejar listo el informe de la auditoria lo ve ismael",
     "propone": {"referente_id": "m-ismael", "fecha": "2026-10-15"}},
    {"nombre": "con faltas de ortografía",
     "texto": "q cuelge de la planta nueba: armar el layout del deposito, nahuel",
     "propone": {"padre_id": "o-planta", "referente_id": "m-nahuel"},
     "mal_escrito": ["nueba"]},
    {"nombre": "vence después que su padre",
     "texto": "para la linea 3 hay que tener los repuestos criticos en stock para el 4 de "
              "diciembre lo lleva lucas",
     "propone": {"padre_id": "o-linea", "tipo": "operativo", "referente_id": "m-lucas",
                 "fecha": "2026-12-04"}},
    # J3-4b: el referente por el área de lo que se describe, aunque nadie lo nombre.
    {"nombre": "nadie nombrado y el área clara",
     "texto": "hay q mejorar como medimos las piesas en el control de calidad antes de despacharlas",
     "propone": {"titulo": True, "referente_id": "m-nahuel"},
     "no_propone": ["fecha"]},
    {"nombre": "nadie nombrado y el área no se sabe",
     "texto": "organizar algo lindo para el aniversario de la empresa",
     "propone": {"titulo": True},
     "no_propone": ["referente_id", "fecha"]},
    {"nombre": "el referente nombrado gana sobre el área",
     "texto": "migrar los servidores y la red a la nube lo lleva nahuel",
     "propone": {"referente_id": "m-nahuel"}},
    {"nombre": "alguien que no es referente, aunque el área se entienda",
     "texto": "cambiar todo el cableado de red del galpon q lo lleve marcos",
     "no_propone": ["referente_id"],
     "descarta": [("referente", "no_encontrado")]},
]

# Lo que contestaría una IA que entendió, para la corrida en seco.
GUION: dict[str, dict[str, Any]] = {
    "el módem colgado": {
        "titulo": "Ordenar la sala de servidores",
        "descripcion": "Dejar la sala de servidores ordenada, con el módem colgado en la pared.",
        "padre": "", "tipo": "estrategico", "referente": "lucas", "fecha": "2026-10-30",
        "como_dijo_la_fecha": "para el viernes 30"},
    "los operarios de la línea 3": {
        "titulo": "Capacitar a los operarios del turno noche",
        "descripcion": "Capacitar a los operarios del turno noche para arrancar la línea 3.",
        "padre": "P2", "tipo": "operativo", "referente": "ismael", "fecha": "2026-11-13",
        "como_dijo_la_fecha": "para el 13/11"},
    "dos referentes con el mismo apodo": {
        "titulo": "Armar el plan de backups de los servidores",
        "descripcion": "Armar el plan de backups de todos los servidores.",
        "tipo": "estrategico", "referente": "el colo"},
    "un sábado no es hábil": {
        "titulo": "Renovar los matafuegos de la planta",
        "descripcion": "Renovar los matafuegos de la planta.",
        "tipo": "estrategico", "referente": "lucas", "fecha": "2026-10-24",
        "como_dijo_la_fecha": "para el sabado 24"},
    "antes de que termine el mes": {
        "titulo": "Poner en marcha el laboratorio de calidad",
        "descripcion": "Tener el laboratorio de calidad andando antes de que termine noviembre.",
        "padre": "P1", "tipo": "operativo", "referente": "nahuel", "fecha": "2026-11-27",
        "como_dijo_la_fecha": "antes d q termine noviembre"},
    "nadie nombrado y el área clara": {
        "titulo": "Mejorar cómo se miden las piezas en el control de calidad",
        "descripcion": "Mejorar cómo se miden las piezas en el control de calidad antes de "
                       "despacharlas.",
        "tipo": "estrategico", "referente": "", "area": "A1"},
    "nadie nombrado y el área no se sabe": {
        "titulo": "Organizar el aniversario de la empresa",
        "descripcion": "Organizar algo lindo para el aniversario de la empresa.",
        "tipo": "estrategico", "referente": "", "area": ""},
    "el referente nombrado gana sobre el área": {
        "titulo": "Migrar los servidores y la red a la nube",
        "descripcion": "Migrar los servidores y la red a la nube.",
        "tipo": "estrategico", "referente": "nahuel", "area": "A3"},
    "alguien que no es referente, aunque el área se entienda": {
        "titulo": "Cambiar el cableado de red del galpón",
        "descripcion": "Cambiar todo el cableado de red del galpón.",
        "tipo": "estrategico", "referente": "marcos", "area": "A3"},
}


class EquipoFijo(base.EquipoFijo):
    """El equipo fijo de esta medición (con Nahuel, referente de Calidad), con la misma forma que
    el de la carga: contesta los apodos vigentes y los integrantes activos."""

    def execute(self, sql: str, parametros: Any = None) -> None:
        if "from integrante" in " ".join(sql.split()):
            self._filas = sorted(EQUIPO, key=lambda f: f["nombre"])
        else:
            super().execute(sql, parametros)


def coinciden(dicho: str, apodos: dict[str, list[str]] | None = None) -> list[dict[str, Any]]:
    """Los integrantes del equipo fijo que coinciden con lo dicho, con la función del servidor."""
    return fichas.integrantes_que_coinciden(EquipoFijo(APODOS if apodos is None else apodos),
                                            dicho)


class IAEnSeco:
    """Sin red: contesta la herramienta con el guion del pedido (por su texto), o sin proponer
    nada."""

    nombre = GUIONADA

    def __init__(self) -> None:
        self.cliente = self
        self.parametros: dict[str, Any] = {}
        self._por_texto = {p["texto"]: GUION.get(p["nombre"], {}) for p in PEDIDOS}

    def completar(self, cuerpo: dict[str, Any], al_avanzar=None) -> dict[str, Any]:
        entrada = json.loads(next(m["content"] for m in cuerpo["messages"]
                                  if m["role"] == "user"))
        datos = self._por_texto.get(entrada["texto"], {})
        return {"choices": [{"finish_reason": "tool_calls", "message": {"tool_calls": [
            {"function": {"name": cuerpo["tools"][0]["function"]["name"],
                          "arguments": json.dumps(datos, ensure_ascii=False)}}]}}]}


def la_ia(texto: str):
    """La IA de `--ia`: en seco, o la real (la de la medición de la carga)."""
    return IAEnSeco() if texto == GUIONADA else base.la_ia(texto)


def medir(ia, pedido: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    """Un pedido, una vez: si dio lo esperado y lo que pasó. Una falla de la IA vuelve como un
    resultado (`falla: ia`); sin cupo, `SinCupo`; un error del programa se levanta tal cual."""
    entrada = ayuda.entrada_de_la_ia(pedido["texto"], VACIO, OPCIONES)
    desde = time.monotonic()
    try:
        crudo = ayuda.pedir(ia, entrada)
    except Exception as falla:
        return False, {**base._de_la_ia(falla), "segundos": round(time.monotonic() - desde, 2)}
    segundos = round(time.monotonic() - desde, 2)
    r = ayuda.revisar(crudo, texto=pedido["texto"], escrito=VACIO, opciones=OPCIONES,
                      coinciden=lambda dicho: coinciden(dicho, pedido.get("apodos")))
    fallas: list[str] = []
    for campo, esperado in (pedido.get("propone") or {}).items():
        valor = r.propuesta.get(campo)
        if valor is None or (esperado is not True and valor != esperado):
            fallas.append(f"{campo}: esperaba {'un texto' if esperado is True else esperado}, "
                          f"vino {valor!r}")
    if pedido.get("tipo_en") and r.propuesta.get("tipo") not in pedido["tipo_en"]:
        fallas.append(f"tipo: esperaba uno de {pedido['tipo_en']}, vino "
                      f"{r.propuesta.get('tipo')!r}")
    for campo in pedido.get("no_propone") or []:
        if campo in r.propuesta:
            fallas.append(f"{campo}: no tenía que proponerlo y propuso {r.propuesta[campo]!r}")
    for campo, motivo in pedido.get("descarta") or []:
        if {"campo": campo, "motivo": motivo} not in r.descartados:
            fallas.append(f"{campo}: esperaba descartarlo por {motivo}")
    if "elegir" in pedido:
        elegidos = sorted(e["membership_id"] for e in r.elegir)
        if elegidos != sorted(pedido["elegir"]):
            fallas.append(f"elegir: esperaba {sorted(pedido['elegir'])}, vino {elegidos}")
    # El nombre y la descripción, con naturalidad y con los nombres de los datos bien escritos.
    textos = {c: r.propuesta[c] for c in ("titulo", "descripcion") if c in r.propuesta}
    naturalidad = {c: m for c, t in textos.items() if (m := base.sin_naturalidad(t, []))}
    fallas += [f"{c}: sin naturalidad: {', '.join(m)}" for c, m in naturalidad.items()]
    todo = " ".join(textos.values())
    # Sin el nombre ni la descripción no hay cómo ver la ortografía: no pasa sin mirar nada (RDD
    # de la J3-4, R3-001).
    if pedido.get("mal_escrito") and not textos:
        fallas.append("ortografía: no propuso el nombre ni la descripción, y no se pudo ver cómo "
                      "escribió los nombres de los datos")
    for palabra in pedido.get("mal_escrito") or []:
        if palabra.casefold() in todo.casefold():
            fallas.append(f"ortografía: propuso «{palabra}» tal cual")
    return not fallas, {"falla": None, "propuesta": r.propuesta,
                        "avisos": [a["texto"] for a in r.avisos],
                        "descartados": r.descartados, "elegir": r.elegir,
                        "sin_naturalidad": naturalidad, "segundos": segundos, "fallas": fallas}


def main(argv: list[str] | None = None) -> int:
    return base.correr(argv, PEDIDOS, medir, la_ia, __doc__)


if __name__ == "__main__":
    sys.exit(main())
