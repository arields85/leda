"""La medición de la ayuda de la IA al cargar (porción J2 de `odd/tasks/plataforma-jerarquias.md`):
pedidos escritos como en un chat real, la misma función que usa la web y los mismos controles del
código, contra la IA que se elija. **No se corre sin permiso del usuario**: con una IA real gasta
unas 41 llamadas por vuelta (27 pedidos: 14 propuestas, cada una con dos llamadas, la propuesta y
el juicio por el sentido del criterio que escribió la IA, J2-13 y J2-17; 10 criterios escritos
para juzgar al cargar, una llamada cada uno: J2-14, con la evidencia que pide el área basta un
resultado, y todo rechazo trae un criterio propuesto; y 3 correcciones de la ortografía, J2-17,
una llamada cada una).

    $env:PYTHONPATH = "src"
    .venv\\Scripts\\python.exe tools\\medir_ayuda_al_cargar.py --ia sol-suscripcion --veces 3

J2-17 (el usuario: la propuesta "parece sacada del código… muy estructurada"): cada texto que
propone Leda (título, descripción, criterio, y el criterio que trae un rechazo) se mira también
desde la medición, nunca en el código de Leda, por si no está escrito con naturalidad
(`sin_naturalidad`). J2-18: sólo lo que es estructura y no prosa (la ronda de la J2-17 marcaba de
más un punto y coma dentro de una oración y una evidencia dicha dentro de una oración natural):
la frase de la plantilla de reserva; una etiqueta de la evidencia de cuatro palabras o más pegada
como un fragmento (al principio de una oración o después de ":", ";" o "·", no como parte de una
oración); y una lista: un "·", o dos ";" o más en una misma oración. Así la ronda con la IA real
muestra si la IA escribe como una persona del equipo.

J2-18 (Leda completa todo lo que puede): los pedidos sin quién la hace esperan que Leda proponga a
alguien del equipo (y, en el de los tornillos, también evidencia además del mínimo del área); el
que nombra a alguien que no es del equipo, que no lo reemplace. Las áreas del equipo fijo conocen
los cinco tipos de evidencia del pack, como pide la J2-18 (el formulario ofrece los cinco y el
área fija un mínimo); en `leda_motor` hoy cada área conoce sólo su mínimo (lo que importa el
importador), así que la evidencia que Leda sume allí no pasa el control hasta que el importador le
dé a cada área los tipos del pack.

`--ia guionada` (lo de omisión) corre en seco, sin red: una IA de mentira con un guion para el
ejemplo del usuario, el sábado, "antes del jueves", el PLC, el UPS de la prueba del usuario (con
la comprobación circular que dio la IA real), "cirelabs", los tornillos (con quién la hace y la
evidencia que propone Leda), "pepe" (que no es del equipo), los juicios de los criterios y las
correcciones de la ortografía (lo que tendría que contestar una IA que entendió), y nada para los
demás; así la corrida en seco prueba los controles y la comparación: da 21 de 27 (sale con 1).
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
import re
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


# Los cinco tipos de evidencia del pack (`espacios/corework.yaml`, `evidencia.tipos`).
TIPOS_DEL_PACK: dict[str, Any] = {
    "explicacion": {"clases": ["texto"],
                    "en_palabras": "cómo quedó el trabajo, descrito por quien lo hizo"},
    "resultado_de_prueba": {"clases": ["texto", "archivo", "imagen", "enlace"],
                            "en_palabras": "cómo se probó y qué dio la prueba"},
    "captura": {"clases": ["imagen"], "en_palabras": "una foto o una captura de la pantalla"},
    "foto": {"clases": ["imagen"], "en_palabras": "una foto del trabajo terminado"},
    "archivo": {"clases": ["archivo", "imagen", "enlace"],
                "en_palabras": "un archivo del trabajo, por ejemplo el programa o la "
                               "configuración"},
}

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
        # J2-17: el nombre que la persona escribió mal en la prueba del celular ("cirelabs").
        {"id": "o-corelabs", "titulo": "Integrar el PLC con CoreLabs", "tipo": "operativo",
         "estado": "activo", "fecha_objetivo": "2026-11-27"},
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
    # Las etiquetas de la evidencia, las de `espacios/corework.yaml` (las que vio el usuario): cada
    # área pide su mínimo y conoce los cinco tipos del pack (J2-18).
    "politicas": [
        {"area_id": "a-infra", "area": "Infraestructura",
         "evidencia_requerida": ["explicacion", "resultado_de_prueba"], "version": 1,
         "tipos": TIPOS_DEL_PACK},
        {"area_id": "a-auto", "area": "Automatización",
         "evidencia_requerida": ["explicacion", "captura"], "version": 1,
         "tipos": TIPOS_DEL_PACK},
    ],
    "calendario": {"dias": ["lunes", "martes", "miercoles", "jueves", "viernes"],
                   "hasta": "2027-04-14", "feriados": [], "dias_habiles": _habiles(HOY)},
}
OBJETIVO_DE = {"t-tablero": "o-modem", "t-plc": "o-linea"}
APODOS = {"m-marcos": ["el tano"]}

# Cada pedido: lo que escribió la persona, como en un chat real; lo que Leda tiene que proponer
# (con su valor, o `True` para un texto que sólo tiene que pasar los controles), lo que no, lo que
# tiene que descartar con su motivo (`descarta`) y, para la ortografía (J2-17), las palabras que
# tienen que aparecer bien escritas en lo que propone (`bien_escrito`) y las que no (`mal_escrito`).
# J2-17: Leda propone siempre un criterio, también sin quién la hace ni evidencia de su área ("no
# sé" es un pedido de ayuda).
PEDIDOS: list[dict[str, Any]] = [
    {"nombre": "el ejemplo del usuario",
     "texto": "hay que colgar el estante del modem en la sala que lo haga lucas necesita 12 "
              "tornillos de 8 mm para el viernes no puede hasta que terminen de cablear el "
              "tablero de la maquina 3",
     "propone": {"titulo": True, "descripcion": True, "criterio": True,
                 "responsable_id": "m-lucas", "espera_id": "t-tablero",
                 "objetivo_id": "o-modem", "fecha": "2026-10-16"}},
    # J2-18: sin quién la hace, Leda propone a alguien del equipo por el trabajo y las áreas, y la
    # evidencia que sirve para esta tarea además del mínimo del área.
    {"nombre": "los tornillos, sin quién ni cuándo",
     "texto": "faltan los tornillos para colgar el estante, necesito 12 de 8 mm",
     "propone": {"titulo": True, "criterio": True, "responsable_id": True, "evidencia": True},
     "no_propone": ["fecha", "espera_id"]},
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
     "propone": {"titulo": True, "criterio": True, "responsable_id": True},
     "no_propone": ["fecha", "espera_id"]},
    {"nombre": "un sábado no es hábil",
     "texto": "lucas tiene que pintar el cartel de la entrada el sabado",
     "propone": {"titulo": True, "responsable_id": "m-lucas"},
     "no_propone": ["fecha"]},
    # J2-18: si nombró a alguien que no es del equipo, se dice en su campo y Leda no pone a otro.
    {"nombre": "alguien que no es del equipo",
     "texto": "que lo haga pepe, ordenar el deposito para la semana que viene",
     "propone": {"titulo": True},
     "no_propone": ["responsable_id"], "descarta": [["responsable", "no_encontrado"]]},
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
     "no_propone": ["espera_id"], "bien_escrito": ["batería"], "mal_escrito": ["cmabiar"]},
    # J2-9, J2-13 y J2-17: la persona no dijo cómo se comprueba ni quién la hace: Leda igual
    # propone un criterio, con sus palabras, sin inventar una manera; J2-18: y a quién la hace.
    {"nombre": "el PLC, sin quién ni cómo se comprueba",
     "texto": "hay que dejar el plc de la comprimidora fette 2000 y sus variables listos para "
              "que ariel la integre a la interfaz",
     "propone": {"titulo": True, "criterio": True, "responsable_id": True}},
    # J2-13: el pedido de la prueba del usuario, tal cual (2026-10-13). En `leda_motor` "el tano"
    # no es el apodo de nadie, así que no hay quién la hace (J2-18: Leda no pone a otro) ni
    # evidencia de su área: la comprobación circular que dio la IA real se rechaza por su sentido
    # y Leda propone otro criterio (J2-17), que no inventa cómo se comprueba (J2-18).
    {"nombre": "el UPS de la prueba del usuario",
     "texto": "hay que cambiar el ups de la sala de servidores que lo vea el tano antes del "
              "jueves se corta todo",
     "apodos": {},
     "propone": {"titulo": True, "fecha": "2026-10-14", "criterio": True},
     "no_propone": ["responsable_id"],
     "descarta": [["criterio", "sin_comprobacion"], ["responsable", "no_encontrado"]]},
    # J2-17: el nombre mal escrito de la segunda prueba del usuario en el celular: la IA eligió
    # bien el objetivo ("Integrar el PLC con CoreLabs") pero escribió "cirelabs". J2-18: y Leda
    # propone a quién la hace.
    {"nombre": "cirelabs",
     "texto": "hay q integrar el plc de la fette con cirelabs para q ariel lo vea en la "
              "interfaz",
     "propone": {"titulo": True, "criterio": True, "objetivo_id": "o-corelabs",
                 "responsable_id": True},
     "bien_escrito": ["CoreLabs"], "mal_escrito": ["cirelabs"]},
    # J2-9, J2-13 y J2-14: el criterio que escribió la persona, juzgado al cargar por su sentido
    # (`juicio`: lo que tiene que decidir el código; `None` es que sirve), con la evidencia que se
    # eligió en el formulario, en palabras de todos los días (`evidencia`). J2-14: con evidencia
    # basta un resultado (cómo se comprueba sale de ella), y lo que no dice ninguno se rechaza
    # (`sin_resultado`); sin evidencia, el criterio tiene que decir cómo se comprueba
    # (`sin_comprobacion`). J2-17: todo rechazo trae un criterio propuesto, que el pedido exige.
    {"nombre": "el criterio circular del usuario", "titulo": "Integrar el PLC de la Fette 2000",
     "evidencia": ["una foto o una captura de la pantalla"],
     "criterio_escrito": "El PLC de la comprimidora Fette 2000 y sus variables quedan listos para "
                         "que Ariel la integre a la interfaz. Se comprueba revisando que el PLC "
                         "y sus variables estén listos para esa integración.",
     "juicio": None},
    {"nombre": "un criterio con una comprobación concreta",
     "titulo": "Integrar el PLC de la Fette 2000",
     "evidencia": ["una foto o una captura de la pantalla"],
     "criterio_escrito": "El PLC de la comprimidora Fette 2000 y sus variables quedan listos para "
                         "que Ariel la integre a la interfaz. Las variables del PLC se leen bien "
                         "desde la interfaz.",
     "juicio": None},
    {"nombre": "un criterio con palabras y sin resultado", "titulo": "Colocar el estante",
     "evidencia": ["una foto del trabajo terminado"],
     "criterio_escrito": "Hacerlo con cuidado y prolijidad", "juicio": "sin_resultado"},
    {"nombre": "no se", "titulo": "Colocar el estante",
     "evidencia": ["una foto del trabajo terminado"], "criterio_escrito": "No se",
     "juicio": "sin_resultado"},
    {"nombre": "el UPS circular, escrito", "titulo": "Cambiar el UPS de la sala de servidores",
     "evidencia": ["una foto del trabajo terminado"],
     "criterio_escrito": "El UPS de la sala de servidores está cambiado. Se comprueba verificando "
                         "en la sala de servidores que el UPS fue reemplazado.",
     "juicio": None},
    # Sin la lista de palabras de la J2-9: "revisa" y "queda" no deciden nada.
    {"nombre": "un criterio concreto con palabras de revisar",
     "titulo": "Cambiar la batería del UPS", "evidencia": ["una foto del trabajo terminado"],
     "criterio_escrito": "Se revisa que el UPS quede encendido con la batería nueva y aguante 10 "
                         "minutos sin luz.",
     "juicio": None},
    # Lo igual al título lo rechaza el código, diga lo que diga la IA; la IA sólo propone.
    {"nombre": "igual al título", "titulo": "Colocar el estante",
     "evidencia": ["una foto del trabajo terminado"],
     "criterio_escrito": "Colocar el estante.", "juicio": "sin_resultado"},
    # J2-14: los dos criterios de la segunda prueba del usuario en el celular (2026-10-13), con la
    # evidencia que mostraba el formulario: dicen un resultado y se cargan.
    {"nombre": "el UPS del celular", "titulo": "Cambiar el UPS de la sala de servidores",
     "evidencia": ["cómo se probó y qué dio la prueba"],
     "criterio_escrito": "El ups queda cambiado y funcionando", "juicio": None},
    {"nombre": "ordenado y limpio", "titulo": "Ordenar el depósito",
     "evidencia": ["una foto del trabajo terminado"],
     "criterio_escrito": "Quedó ordenado y limpio", "juicio": None},
    # Sin evidencia del área, el mismo criterio no dice cómo se comprueba (J2-13), y el rechazo
    # trae uno propuesto (J2-17).
    {"nombre": "el UPS del celular, sin evidencia del área",
     "titulo": "Cambiar el UPS de la sala de servidores", "evidencia": [],
     "criterio_escrito": "El ups queda cambiado y funcionando", "juicio": "sin_comprobacion"},
    # J2-17: la ortografía de lo que la persona escribió a mano en los campos de texto, antes de
    # la vista previa (`ortografia`: los textos). `corrige`: las palabras que tienen que quedar
    # bien escritas (y que el código acepte la corrección); `igual`: los campos que no se tocan.
    {"nombre": "ortografía: el árbol y CoreLabs",
     "ortografia": {"titulo": "plantar el arvol de la entrada",
                    "descripcion": "coordinar con cirelabs la entrega del plc"},
     "corrige": {"titulo": ["árbol"], "descripcion": ["CoreLabs"]}},
    {"nombre": "ortografía: bien escrito no se toca",
     "ortografia": {"titulo": "Revisar el tablero de la línea 3",
                    "criterio": "El tablero queda revisado y Marcos lo ve funcionando."},
     "igual": ["titulo", "criterio"]},
    # Lo que se escribe como en un chat ("q") no es una falta para corregir con otra palabra: si la
    # IA lo cambia, el código deja esa palabra como estaba y corrige las demás (J2-18: antes
    # rechazaba la corrección entera).
    {"nombre": "ortografía: como en un chat",
     "ortografia": {"titulo": "cambiar la bateria del ups q no anda"},
     "corrige": {"titulo": ["batería"]}},
]

VACIO = {c: "" for c in ayuda_al_cargar.CAMPOS}

# Lo que propone la IA en seco: lo que propondría una IA que entendió el ejemplo del usuario, un
# sábado (que los controles no dejan poner), "antes del jueves" (el miércoles), el PLC y
# "cirelabs"; y, en el UPS de la prueba del usuario, lo que propuso la IA real (una comprobación
# circular). Los demás pedidos, sin guion: no propone nada.
GUION: dict[str, dict[str, str]] = {
    "el ejemplo del usuario": {
        "titulo": "Colgar el estante del módem en la sala",
        "descripcion": "Colgar el estante del módem en la sala. Hacen falta 12 tornillos de 8 mm. "
                       "No se puede empezar hasta que terminen de cablear el tablero de la "
                       "máquina 3.",
        "criterio": "El estante del módem queda colgado en la sala con los 12 tornillos de 8 mm, "
                    "firme y derecho.",
        "resultado": "El estante del módem está colgado en la sala con los 12 tornillos de 8 mm",
        "responsable": "lucas", "espera": "T1", "objetivo": "O1",
        "fecha": "2026-10-16", "como_dijo_la_fecha": "para el viernes"},
    "un sábado no es hábil": {
        "titulo": "Pintar el cartel de la entrada", "responsable": "lucas",
        "criterio": "El cartel de la entrada queda pintado y se ve terminado.",
        "fecha": "2026-10-17", "como_dijo_la_fecha": "el sabado"},
    "un apodo y un día de la semana": {
        "titulo": "Cambiar el UPS de la sala de servidores",
        "criterio": "El UPS de la sala de servidores queda cambiado y funcionando.",
        "resultado": "El UPS de la sala de servidores está cambiado",
        "responsable": "el tano", "fecha": "2026-10-14", "como_dijo_la_fecha": "antes del jueves"},
    "el PLC, sin quién ni cómo se comprueba": {
        "titulo": "Dejar listo el PLC de la comprimidora Fette 2000",
        "criterio": "El PLC de la comprimidora Fette 2000 y sus variables quedan listos, y Ariel "
                    "los ve desde la interfaz.",
        "quien_la_hace": "P2"},
    # J2-18: Leda propone a Lucas (Infraestructura) y una foto del trabajo terminado, dicha dentro
    # de una oración natural.
    "los tornillos, sin quién ni cuándo": {
        "titulo": "Conseguir los 12 tornillos de 8 mm para colgar el estante",
        "criterio": "Están los 12 tornillos de 8 mm y el estante queda colgado, y se puede ver en "
                    "una foto del trabajo terminado.",
        "quien_la_hace": "P1", "evidencia": "E4"},
    # J2-18: nombró a alguien que no es del equipo; la IA igual propone a otro, y el código no lo
    # pone.
    "alguien que no es del equipo": {
        "titulo": "Ordenar el depósito", "criterio": "El depósito queda ordenado.",
        "responsable": "pepe", "quien_la_hace": "P1"},
    "el UPS de la prueba del usuario": {
        "titulo": "Cambiar el UPS de la sala de servidores",
        "criterio": "El UPS de la sala de servidores está cambiado. Se comprueba verificando en la "
                    "sala de servidores que el UPS fue reemplazado.",
        "resultado": "El UPS de la sala de servidores está cambiado",
        "responsable": "el tano", "fecha": "2026-10-14", "como_dijo_la_fecha": "antes del jueves"},
    "cirelabs": {
        "titulo": "Integrar el PLC de la Fette con CoreLabs",
        "criterio": "El PLC de la Fette queda integrado con CoreLabs y Ariel lo ve en la "
                    "interfaz.",
        "objetivo": "O4", "quien_la_hace": "P2"},
}
# Lo que contesta en seco el juicio de un criterio (escrito o propuesto), por su texto: lo que
# diría una IA que lo juzga por su sentido y que, si no sirve, escribe el suyo con sus palabras
# (J2-17). Sin evidencia del área, si dice cómo se comprueba (`GUION_DEL_JUICIO`); con ella
# (J2-14), si dice un resultado (`GUION_DEL_RESULTADO`).
_UPS_DE_LEDA = ("El UPS de la sala de servidores queda cambiado y funcionando, y se lo ve encendido "
                "en la sala.")
GUION_DEL_JUICIO: dict[str, dict[str, Any]] = {
    "El PLC de la comprimidora Fette 2000 y sus variables quedan listos para que Ariel la integre "
    "a la interfaz. Se comprueba revisando que el PLC y sus variables estén listos para esa "
    "integración.": {"dice_como_se_comprueba": False, "como_se_comprueba": "", "criterio": ""},
    # J2-18: sin quién la hace, el criterio de Leda dice qué tiene que quedar hecho y no inventa
    # cómo se comprueba (lo dirá la evidencia de quien la haga).
    "El UPS de la sala de servidores está cambiado. Se comprueba verificando en la sala de "
    "servidores que el UPS fue reemplazado.":
        {"dice_como_se_comprueba": False, "como_se_comprueba": "",
         "criterio": "El UPS de la sala de servidores queda cambiado."},
    "El depósito queda ordenado.":
        {"dice_como_se_comprueba": False, "como_se_comprueba": "",
         "criterio": "El depósito queda ordenado."},
    "El ups queda cambiado y funcionando":
        {"dice_como_se_comprueba": False, "como_se_comprueba": "", "criterio": _UPS_DE_LEDA},
    "El PLC de la comprimidora Fette 2000 y sus variables quedan listos, y Ariel los ve desde la "
    "interfaz.":
        {"dice_como_se_comprueba": True, "como_se_comprueba": "Ariel los ve desde la interfaz",
         "criterio": ""},
    "El PLC de la Fette queda integrado con CoreLabs y Ariel lo ve en la interfaz.":
        {"dice_como_se_comprueba": True, "como_se_comprueba": "Ariel lo ve en la interfaz",
         "criterio": ""},
}
_ESTANTE = "El estante queda colocado"
_ESTANTE_DE_LEDA = "El estante queda colocado, firme y derecho, y quien lo revisa lo ve terminado."
GUION_DEL_RESULTADO: dict[str, dict[str, Any]] = {
    "El PLC de la comprimidora Fette 2000 y sus variables quedan listos para que Ariel la integre "
    "a la interfaz. Se comprueba revisando que el PLC y sus variables estén listos para esa "
    "integración.":
        {"dice_un_resultado": True,
         "resultado": "El PLC de la comprimidora Fette 2000 y sus variables quedan listos para "
                      "que Ariel la integre a la interfaz", "criterio": ""},
    "El PLC de la comprimidora Fette 2000 y sus variables quedan listos para que Ariel la integre "
    "a la interfaz. Las variables del PLC se leen bien desde la interfaz.":
        {"dice_un_resultado": True,
         "resultado": "El PLC de la comprimidora Fette 2000 y sus variables quedan listos para "
                      "que Ariel la integre a la interfaz", "criterio": ""},
    "Hacerlo con cuidado y prolijidad":
        {"dice_un_resultado": False, "resultado": _ESTANTE, "criterio": _ESTANTE_DE_LEDA},
    "No se": {"dice_un_resultado": False, "resultado": _ESTANTE, "criterio": _ESTANTE_DE_LEDA},
    "Colocar el estante.":
        {"dice_un_resultado": False, "resultado": _ESTANTE, "criterio": _ESTANTE_DE_LEDA},
    "El UPS de la sala de servidores está cambiado. Se comprueba verificando en la sala de "
    "servidores que el UPS fue reemplazado.":
        {"dice_un_resultado": True, "resultado": "El UPS de la sala de servidores está cambiado",
         "criterio": ""},
    "Se revisa que el UPS quede encendido con la batería nueva y aguante 10 minutos sin luz.":
        {"dice_un_resultado": True,
         "resultado": "El UPS queda encendido con la batería nueva y aguanta 10 minutos sin luz",
         "criterio": ""},
    "El ups queda cambiado y funcionando":
        {"dice_un_resultado": True, "resultado": "El UPS queda cambiado y funcionando",
         "criterio": ""},
    "Quedó ordenado y limpio":
        {"dice_un_resultado": True, "resultado": "El depósito queda ordenado y limpio",
         "criterio": ""},
    # Los criterios que propone la IA en seco, ya con la evidencia del área de quien la hace.
    "El estante del módem queda colgado en la sala con los 12 tornillos de 8 mm, firme y derecho.":
        {"dice_un_resultado": True, "resultado": "", "criterio": ""},
    "El UPS de la sala de servidores queda cambiado y funcionando.":
        {"dice_un_resultado": True, "resultado": "", "criterio": ""},
    "El cartel de la entrada queda pintado y se ve terminado.":
        {"dice_un_resultado": True, "resultado": "", "criterio": ""},
    # J2-18: con quién la hace propuesto por Leda, el juicio tiene la evidencia de su área.
    "El PLC de la comprimidora Fette 2000 y sus variables quedan listos, y Ariel los ve desde la "
    "interfaz.":
        {"dice_un_resultado": True, "resultado": "", "criterio": ""},
    "El PLC de la Fette queda integrado con CoreLabs y Ariel lo ve en la interfaz.":
        {"dice_un_resultado": True, "resultado": "", "criterio": ""},
    "Están los 12 tornillos de 8 mm y el estante queda colgado, y se puede ver en una foto del "
    "trabajo terminado.":
        {"dice_un_resultado": True, "resultado": "", "criterio": ""},
}
# Lo que corrige en seco la IA de la ortografía, por el primer texto del pedido: lo que haría una
# IA que entendió (sólo la ortografía, con los nombres de los datos).
GUION_DE_LA_ORTOGRAFIA: dict[str, dict[str, str]] = {
    "plantar el arvol de la entrada": {
        "titulo": "Plantar el árbol de la entrada",
        "descripcion": "Coordinar con CoreLabs la entrega del PLC"},
    "Revisar el tablero de la línea 3": {
        "titulo": "Revisar el tablero de la línea 3",
        "criterio": "El tablero queda revisado y Marcos lo ve funcionando."},
    # Como la IA real de la ronda de la J2-17: también cambia "q" por "que".
    "cambiar la bateria del ups q no anda": {"titulo": "Cambiar la batería del UPS que no anda"},
}

# J2-17, sólo en la medición: lo que delata un texto escrito con forma de código (el usuario: "muy
# estructurado… parece sacado del código"). J2-18: sólo la estructura, no la prosa. La frase de la
# plantilla de reserva; una etiqueta de la evidencia (de cuatro palabras o más: las cortas, como
# "una foto", se dicen naturalmente) pegada como un fragmento, es decir, al principio del texto o de
# una oración, o después de ":", ";" o "·" (dicha dentro de una oración, después de una palabra, es
# prosa: "se puede ver en una foto del trabajo terminado"); y una lista: un "·" (no es puntuación
# de una oración) o dos ";" o más en una misma oración (uno solo une dos oraciones).
_DE_LA_PLANTILLA = "se comprueba con lo que pide el area"
_ANTES_DE_UN_FRAGMENTO = ".!?:;·"
_FIN_DE_ORACION = re.compile(r"[.!?]+")


def _etiquetas(pedido: dict[str, Any]) -> list[str]:
    tipos = [t for p in OPCIONES["politicas"] for t in p["tipos"].values()]
    return list(dict.fromkeys([*(t["en_palabras"] for t in tipos),
                               *(pedido.get("evidencia") or [])]))


def _plano(texto: str) -> str:
    return " ".join(ayuda_al_cargar._normal(texto).split())


def _pegada_como_fragmento(texto: str, etiqueta: str) -> bool:
    """Si la etiqueta está tal cual en el texto (sin mayúsculas ni tildes) y pegada como un
    fragmento: lo que la precede es el principio, el fin de una oración, ":", ";" o "·"."""
    letras: list[str] = []
    lugar: list[int] = []
    for i, c in enumerate(texto):
        for n in ayuda_al_cargar._sin_marcas(c):
            letras.append(n if n.isalnum() else " ")
            lugar.append(i)
    plano = "".join(letras)
    buscada = _plano(etiqueta)
    for m in re.finditer(rf"(?<![^\W_]){re.escape(buscada).replace(r'\ ', r'\s+')}(?![^\W_])",
                         plano):
        antes = texto[:lugar[m.start()]].rstrip()
        if not antes or antes[-1] in _ANTES_DE_UN_FRAGMENTO:
            return True
    return False


def _es_una_lista(texto: str) -> bool:
    return "·" in texto or any(oracion.count(";") >= 2
                               for oracion in _FIN_DE_ORACION.split(texto))


def sin_naturalidad(texto: str, etiquetas: list[str]) -> list[str]:
    """Por qué un texto propuesto parece armado por el código y no escrito por una persona: la
    frase de la plantilla, una etiqueta de la evidencia de cuatro palabras o más pegada como un
    fragmento, o una lista (un "·", o dos ";" o más en una oración). Vacío si se lee natural."""
    plano = f" {_plano(texto)} "
    motivos = []
    if f" {_DE_LA_PLANTILLA} " in plano:
        motivos.append("la frase de la plantilla")
    for etiqueta in etiquetas:
        if len(_plano(etiqueta).split()) >= 4 and _pegada_como_fragmento(texto, etiqueta):
            motivos.append(f"la etiqueta «{etiqueta}» pegada como un fragmento")
    if _es_una_lista(texto):
        motivos.append("una lista con ; o ·")
    return motivos


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
            guion = (GUION_DEL_RESULTADO if "evidencia_que_pide_el_area" in entrada
                     else GUION_DEL_JUICIO)
            datos: dict[str, Any] = guion.get(entrada["criterio"], {})
        elif nombre == ayuda_al_cargar.NOMBRE_DE_LA_ORTOGRAFIA:
            primero = next(iter(entrada["textos"].values()), "")
            datos = GUION_DE_LA_ORTOGRAFIA.get(primero, {})
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
    """Un criterio escrito, juzgado como al cargar (`juzgar_el_criterio`, con la evidencia del
    pedido): si el código decidió lo esperado y, si lo rechazó, si trajo un criterio propuesto
    (J2-14 y J2-17) escrito con naturalidad. Que la IA no lo juzgara (`sin_revisar`), o un rechazo
    sin propuesta, es una falla de la IA o, si su causa no es de la IA, un error del programa."""
    desde = time.monotonic()
    juicio = ayuda_al_cargar.juzgar_el_criterio(ia, titulo=pedido["titulo"], descripcion="",
                                                criterio=pedido["criterio_escrito"],
                                                evidencia=pedido.get("evidencia") or [])
    segundos = round(time.monotonic() - desde, 2)
    sin_propuesta = (juicio.motivo in ("sin_resultado", "sin_comprobacion")
                     and juicio.propuesta is None)
    if juicio.motivo == "sin_revisar" or sin_propuesta:
        de_la_ia = _de_la_ia(juicio.falla or RespuestaInvalida("sin juicio"))
        if sin_propuesta:
            de_la_ia["fallas"] = [f"propuesta: {f}" for f in de_la_ia["fallas"]]
        return False, {**de_la_ia, "juicio": juicio.motivo, "segundos": segundos}
    fallas = [] if juicio.motivo == pedido["juicio"] else [
        f"juicio: esperaba {pedido['juicio']!r}, vino {juicio.motivo!r}"]
    naturalidad = (sin_naturalidad(juicio.propuesta, _etiquetas(pedido))
                   if juicio.propuesta else [])
    fallas += [f"propuesta sin naturalidad: {m}" for m in naturalidad]
    return not fallas, {"falla": None, "juicio": juicio.motivo, "propuesta": juicio.propuesta,
                        "de_reserva": juicio.de_reserva, "sin_naturalidad": naturalidad,
                        "segundos": segundos, "fallas": fallas}


def medir_la_ortografia(ia, pedido: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    """Los textos escritos a mano, corregidos como antes de la vista previa (J2-17): la misma
    llamada y el mismo control del código (`revisar_la_ortografia`). Sale mal si una palabra que
    se esperaba bien escrita no quedó así, si el código rechazó una corrección (cambió algo más
    que la ortografía) o si cambió un texto que estaba bien."""
    textos = pedido["ortografia"]
    entrada = ayuda_al_cargar.entrada_de_la_ortografia(textos, OPCIONES)
    desde = time.monotonic()
    try:
        crudo = ayuda_al_cargar.pedir_la_ortografia(ia, entrada)
    except Exception as falla:
        return False, {**_de_la_ia(falla), "segundos": round(time.monotonic() - desde, 2)}
    segundos = round(time.monotonic() - desde, 2)
    r = ayuda_al_cargar.revisar_la_ortografia(crudo, textos, OPCIONES)
    fallas = [f"{x['campo']}: el código no aceptó la corrección ({x['motivo']})"
              for x in r.rechazados]
    for campo, palabras in (pedido.get("corrige") or {}).items():
        texto = (r.corregidos.get(campo) or {}).get("texto") or textos[campo]
        for palabra in palabras:
            if palabra not in texto:
                fallas.append(f"{campo}: esperaba «{palabra}», quedó {texto!r}")
    for campo in pedido.get("igual") or []:
        if campo in r.corregidos:
            fallas.append(f"{campo}: estaba bien y lo cambió: {r.corregidos[campo]['texto']!r}")
    return not fallas, {"falla": None, "corregidos": r.corregidos, "rechazados": r.rechazados,
                        "palabras_rechazadas": r.palabras_rechazadas,
                        "segundos": segundos, "fallas": fallas}


def medir(ia, pedido: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    """Un pedido, una vez: si dio lo esperado y lo que pasó. Una falla de la IA vuelve como un
    resultado (`falla: ia`); sin cupo, `SinCupo`; un error del programa se levanta tal cual."""
    if "criterio_escrito" in pedido:
        return medir_el_juicio(ia, pedido)
    if "ortografia" in pedido:
        return medir_la_ortografia(ia, pedido)
    entrada = ayuda_al_cargar.entrada_de_la_ia(pedido["texto"], VACIO, OPCIONES)
    desde = time.monotonic()
    try:
        crudo = ayuda_al_cargar.pedir(ia, entrada)
    except Exception as falla:
        return False, {**_de_la_ia(falla), "segundos": round(time.monotonic() - desde, 2)}
    segundos = round(time.monotonic() - desde, 2)
    apodos = pedido.get("apodos")
    r = ayuda_al_cargar.revisar(crudo, texto=pedido["texto"], escrito=VACIO, opciones=OPCIONES,
                                coinciden=lambda dicho: coinciden(dicho, apodos),
                                objetivo_de=OBJETIVO_DE.get)
    # Como la web: el criterio que escribió la IA se juzga por su sentido, ya con la evidencia del
    # área de quien la hace (J2-13 y J2-17). Si el juicio no responde o no deja un criterio, la
    # propuesta sigue como en la web (con el de reserva, si hay evidencia), salvo sin cupo o con un
    # error del programa; y, como en `medir_el_juicio`, es una falla de la IA: el pedido sale mal y
    # el informe lo dice (revisión `review-bfa79042ca12447b`).
    desde = time.monotonic()
    juicio = ayuda_al_cargar.juzgar_la_propuesta(ia, r)
    del_juicio = round(time.monotonic() - desde, 2) if juicio is not None else None
    ayuda_al_cargar.cerrar_el_criterio(r, juicio)
    falla_del_juicio = None
    if juicio is not None and juicio.falla is not None:
        (falla_del_juicio,) = _de_la_ia(juicio.falla)["fallas"]
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
    # J2-17: lo que escribe Leda, con naturalidad y bien escrito.
    textos = {c: r.propuesta[c] for c in ayuda_al_cargar.CAMPOS_DE_TEXTO if c in r.propuesta}
    naturalidad = {c: m for c, t in textos.items() if (m := sin_naturalidad(t, _etiquetas(pedido)))}
    fallas += [f"{c}: sin naturalidad: {', '.join(m)}" for c, m in naturalidad.items()]
    todo = " ".join(textos.values())
    for palabra in pedido.get("bien_escrito", []):
        if palabra not in todo:
            fallas.append(f"ortografía: esperaba «{palabra}» en lo que propuso")
    for palabra in pedido.get("mal_escrito", []):
        if palabra.casefold() in todo.casefold():
            fallas.append(f"ortografía: propuso «{palabra}» tal cual")
    return not fallas, {"falla": None if falla_del_juicio is None else "ia",
                        "falla_del_juicio": falla_del_juicio, "propuesta": r.propuesta,
                        "criterio_de": r.criterio_de, "responsable_de": r.responsable_de,
                        "sin_naturalidad": naturalidad,
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
