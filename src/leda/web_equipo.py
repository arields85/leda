"""Ver el equipo desde la web (J7-3 de `odd/tasks/plataforma-jerarquias.md`; ADR 0023, decisiones 4
y 5; migración 0082).

Dos puertas con la misma forma: la del equipo, sólo para Dirección (el rol con la autoridad final),
que ve el suyo (`GET /app/api/equipo`); y la de administración, el administrador de plataforma, que
ve el de cualquier espacio (`GET /app/admin/api/espacios/{id}/equipo`). Lo decide la base
(`equipo_de` y `cambios_del_equipo`): la sesión de la puerta en cada llamada y el espacio fijado por
ella. Un referente o un integrante reciben 403, aunque la web les esconda la vista.

Devuelve las áreas, las personas, los roles, los problemas del equipo, la historia de sus cambios
(lo más nuevo primero) y los tipos de evidencia del espacio, para elegir los de un área nueva.

Las áreas (J7-4; migración 0083): crear, renombrar y archivar, primero con la vista previa
(`POST …/equipo/areas/revisar`: lo que cambiaría, su huella y los problemas que dejaría) y después
la confirmación con la clave de un solo uso y esa huella (`POST …/equipo/areas`). Lo valida y lo
hace la base (`vista_previa_de_area`, `crear_area`, `renombrar_area`, `archivar_area`); acá se lee
el pedido y se dice cada rechazo con palabras.

El alta de una persona (J7-5; migración 0084): `POST …/equipo/personas/revisar` y `POST
…/equipo/personas`, con la misma forma (nombre, área, rol y quién la aprueba; o volver a sumar a
quien estuvo, `accion: reactivar`), y `POST …/equipo/personas/enlace`: el enlace de activación de
quien no conectó su Telegram. El token se arma acá, se muestra una sola vez y la base guarda sólo su
huella. Los demás cambios del equipo son de las porciones que siguen de la J7, y cada uno va a vivir
en este módulo.
"""

from __future__ import annotations

import secrets
import uuid
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import Response
from psycopg.types.json import Jsonb

from .db import sin_espacio
from .onboarding import huella_del_token
from .web_app import (PUERTA_DE_ADMINISTRACION, PUERTA_DEL_EQUIPO, TEXTO_DE_UN_DATO_MAL_FORMADO,
                      con_la_version_del_nucleo, escribir_por_la_puerta, hash_del_token,
                      json_de_la_web, leer_por_la_puerta, rechazo_de_la_base)

router = APIRouter(prefix="/app")

TEXTO_SIN_AUTORIDAD = "Organizar el equipo le corresponde a Dirección."


def _el_equipo(conn, puerta: str, token: str, espacio: str | None) -> Response:
    """El equipo, sus cambios y los tipos de evidencia del espacio, en una sola transacción; o lo
    que la base rechaza."""
    with sin_espacio(conn) as cur:
        con_la_version_del_nucleo(cur)
        cur.execute("select equipo_de(%s, %s, %s) as r", (puerta, hash_del_token(token), espacio))
        equipo: dict[str, Any] = cur.fetchone()["r"]
        rechazo = rechazo_de_la_base(equipo, puerta, TEXTO_SIN_AUTORIDAD)
        if rechazo is not None:
            return rechazo
        cur.execute("select cambios_del_equipo(%s, %s, %s) as r",
                    (puerta, hash_del_token(token), espacio))
        cambios: dict[str, Any] = cur.fetchone()["r"]
        cur.execute("select opciones_de_areas(%s, %s, %s) as r",
                    (puerta, hash_del_token(token), espacio))
        opciones: dict[str, Any] = cur.fetchone()["r"]
    for resultado in (cambios, opciones):
        rechazo = rechazo_de_la_base(resultado, puerta, TEXTO_SIN_AUTORIDAD)
        if rechazo is not None:
            return rechazo
    return json_de_la_web({**{k: v for k, v in equipo.items() if k != "ok"},
                           "cambios": cambios["cambios"],
                           "tipos_de_evidencia": opciones["tipos_de_evidencia"]})


@router.get("/api/equipo")
def el_equipo_de_direccion(request: Request):
    """El equipo de la sesión, sólo para Dirección (403 a los demás)."""
    return leer_por_la_puerta(
        request, PUERTA_DEL_EQUIPO, None,
        lambda conn, token, espacio: _el_equipo(conn, PUERTA_DEL_EQUIPO, token, espacio))


@router.get("/admin/api/espacios/{espacio_id}/equipo")
def el_equipo_en_la_administracion(espacio_id: str, request: Request):
    """El equipo de un espacio, por la puerta de administración (ADR 0023, decisión 5)."""
    return leer_por_la_puerta(
        request, PUERTA_DE_ADMINISTRACION, espacio_id,
        lambda conn, token, espacio: _el_equipo(conn, PUERTA_DE_ADMINISTRACION, token, espacio))


# --- Las áreas (J7-4) ----------------------------------------------------------------------------

ACCIONES_DE_AREA = ("crear", "renombrar", "archivar")

TEXTO_SIN_CONFIRMAR = "No se pudo confirmar. Recargá la página y probá de nuevo."
TEXTO_SIN_VISTA_PREVIA = "Revisá la vista previa antes de confirmar."
TEXTOS_DE_LAS_AREAS: dict[tuple[str, str], str] = {
    ("accion", "no_existe"): "Eso no se puede hacer con un área.",
    ("area", "falta"): "Elegí el área.",
    ("area", "no_existe"): "Esa área no está en este equipo.",
    ("area", "archivada"): "Esa área está archivada: su nombre ya no se cambia.",
    ("area", "ya_archivada"): "Esa área ya está archivada.",
    ("nombre", "falta"): "Falta el nombre del área.",
    ("nombre", "demasiado_largo"): "El nombre es demasiado largo: hasta 80 caracteres.",
    ("nombre", "ya_existe"): "Ya hay un área con ese nombre.",
    ("nombre", "sin_cambio"): "Es el mismo nombre que tiene ahora.",
    ("aprobacion", "falta"): "Elegí quién aprueba el trabajo del área.",
    ("aprobacion", "no_existe"): "Esa forma de aprobar no existe.",
    ("referente", "falta"): "Elegí quién es el referente.",
    ("referente", "no_es_integrante_activo"): "Esa persona no es integrante activo de este equipo.",
    ("referente", "no_corresponde"): "Sin referente no se elige a nadie.",
    ("evidencia", "falta"): "Elegí qué evidencia piden sus tareas, o «No pide evidencia».",
    ("evidencia", "contradice"):
        "Elegiste evidencia y también «No pide evidencia»: quedate con una de las dos.",
    ("evidencia", "no_es_del_espacio"): "Esa evidencia no es de este equipo.",
    ("huella", "falta"): TEXTO_SIN_VISTA_PREVIA,
    ("huella", "mal_formada"): TEXTO_SIN_VISTA_PREVIA,
    ("huella", "el_equipo_cambio"): "El equipo cambió desde la vista previa: revisala de nuevo.",
    ("clave", "falta"): TEXTO_SIN_CONFIRMAR,
    ("clave", "mal_formada"): TEXTO_SIN_CONFIRMAR,
    ("clave", "usada_con_otros_datos"):
        "Este envío ya hizo otro cambio. Recargá la página para hacer uno nuevo.",
    ("equipo", "no_cuadra"): "Con este cambio el equipo no cuadraría: no se hizo.",
}

# Los datos del pedido: los ids y los textos, con el `campo` con que los nombra la base.
_IDS = {"area_id": "area", "referente_id": "referente"}
_TEXTOS = {"nombre": "nombre", "aprobacion": "aprobacion", "clave": "clave", "huella": "huella"}
_FEMENINOS = {"area", "aprobacion", "evidencia", "clave", "huella"}
_PARA_LA_VISTA_PREVIA = ("area_id", "nombre", "aprobacion", "referente_id", "evidencia",
                         "sin_evidencia")


def _mal_formado(campo: str) -> dict[str, str]:
    return {"campo": campo, "motivo": "mal_formada" if campo in _FEMENINOS else "mal_formado"}


def _cuantas(n: int, una: str, varias: str) -> str:
    return f"{n} {una if n == 1 else varias}"


def _con_texto(fila: dict[str, Any]) -> dict[str, str]:
    """Un rechazo con sus palabras; el de archivar, con cuántas personas o tareas lo impiden."""
    campo, motivo = str(fila.get("campo", "")), str(fila.get("motivo", ""))
    n = fila.get("cuantas") if isinstance(fila.get("cuantas"), int) else 0
    if (campo, motivo) == ("area", "tiene_personas"):
        texto = (f"No se puede archivar: tiene {_cuantas(n, 'persona', 'personas')}. "
                 "Pasalas a otra área antes.")
    elif (campo, motivo) == ("area", "tiene_tareas_abiertas"):
        texto = (f"No se puede archivar: tiene {_cuantas(n, 'tarea abierta', 'tareas abiertas')}."
                 " Primero se terminan o se cancelan.")
    elif motivo.startswith("mal_formad"):
        texto = TEXTO_DE_UN_DATO_MAL_FORMADO
    else:
        texto = TEXTOS_DE_LAS_AREAS.get((campo, motivo), TEXTO_SIN_CONFIRMAR)
    return {"campo": campo, "motivo": motivo, "texto": texto}


def leer_el_cambio(cuerpo: Any) -> tuple[dict[str, Any], list[dict[str, str]]]:
    """Los datos de un cambio de área como los recibe la base, y los que llegaron con una forma
    que no sirve. Lo que falta lo dice la base, todo junto."""
    cuerpo = cuerpo if isinstance(cuerpo, dict) else {}
    datos: dict[str, Any] = {}
    errores: list[dict[str, str]] = []
    accion = cuerpo.get("accion")
    datos["accion"] = accion if isinstance(accion, str) and accion in ACCIONES_DE_AREA else None
    if datos["accion"] is None:
        errores.append({"campo": "accion", "motivo": "no_existe"})
    for clave, campo in _IDS.items():
        valor = cuerpo.get(clave)
        datos[clave] = None
        if valor in (None, ""):
            continue
        try:
            datos[clave] = str(uuid.UUID(valor)) if isinstance(valor, str) else None
        except ValueError:
            pass
        if datos[clave] is None:
            errores.append(_mal_formado(campo))
    for clave, campo in _TEXTOS.items():
        valor = cuerpo.get(clave)
        datos[clave] = valor if isinstance(valor, str) else None
        if valor is not None and not isinstance(valor, str):
            errores.append(_mal_formado(campo))
    evidencia = cuerpo.get("evidencia")
    datos["evidencia"] = None
    if isinstance(evidencia, list) and all(isinstance(e, str) for e in evidencia):
        datos["evidencia"] = evidencia
    elif evidencia is not None:
        errores.append(_mal_formado("evidencia"))
    sin_evidencia = cuerpo.get("sin_evidencia")
    datos["sin_evidencia"] = sin_evidencia if isinstance(sin_evidencia, bool) else False
    if sin_evidencia is not None and not isinstance(sin_evidencia, bool):
        errores.append(_mal_formado("evidencia"))
    return datos, errores


def _rechazos(mal_formados: list[dict[str, str]], de_la_base: list[dict[str, Any]]) -> Response:
    """422 con todo lo que hay que corregir: lo mal formado y, de lo que dice la base, lo de los
    demás datos (un dato mal formado le llega como si faltara)."""
    ya_dichos = {e["campo"] for e in mal_formados}
    errores = [*mal_formados, *(e for e in de_la_base if e.get("campo") not in ya_dichos)]
    return json_de_la_web({"errores": [_con_texto(e) for e in errores]}, 422)


def _revisar(conn, puerta: str, token: str, espacio: str | None, cuerpo: Any) -> Response:
    """La vista previa: 200 con lo que cambiaría, su huella y los problemas que dejaría; 422 con
    lo que no se puede. No escribe nada."""
    datos, mal_formados = leer_el_cambio(cuerpo)
    if datos["accion"] is None:
        return _rechazos(mal_formados, [])
    with sin_espacio(conn) as cur:
        con_la_version_del_nucleo(cur)
        cur.execute("select vista_previa_de_area(%s, %s, %s, %s, %s) as r",
                    (puerta, hash_del_token(token), espacio, datos["accion"],
                     Jsonb({k: datos[k] for k in _PARA_LA_VISTA_PREVIA})))
        resultado: dict[str, Any] = cur.fetchone()["r"]
    rechazo = rechazo_de_la_base(resultado, puerta, TEXTO_SIN_AUTORIDAD)
    if rechazo is not None:
        return rechazo
    if not resultado.get("ok") or mal_formados:
        return _rechazos(mal_formados, resultado.get("errores") or [])
    return json_de_la_web({k: v for k, v in resultado.items() if k != "ok"})


def _confirmar(conn, puerta: str, token: str, espacio: str | None, cuerpo: Any) -> Response:
    """La confirmación: 201 con el área; la misma clave con la misma huella, 200 con la misma;
    422 con lo que no se puede. Con un dato mal formado no se escribe nada: la clave no llega."""
    datos, mal_formados = leer_el_cambio(cuerpo)
    if datos["accion"] is None:
        return _rechazos(mal_formados, [])
    clave = None if mal_formados else datos["clave"]
    puerta_y_sesion = (puerta, hash_del_token(token), espacio)
    with sin_espacio(conn) as cur:
        con_la_version_del_nucleo(cur)
        if datos["accion"] == "crear":
            cur.execute(
                "select crear_area(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) as r",
                (*puerta_y_sesion, datos["nombre"], datos["aprobacion"], datos["referente_id"],
                 datos["evidencia"], datos["sin_evidencia"], clave, datos["huella"]))
        elif datos["accion"] == "renombrar":
            cur.execute("select renombrar_area(%s, %s, %s, %s, %s, %s, %s) as r",
                        (*puerta_y_sesion, datos["area_id"], datos["nombre"], clave,
                         datos["huella"]))
        else:
            cur.execute("select archivar_area(%s, %s, %s, %s, %s, %s) as r",
                        (*puerta_y_sesion, datos["area_id"], clave, datos["huella"]))
        resultado: dict[str, Any] = cur.fetchone()["r"]
    rechazo = rechazo_de_la_base(resultado, puerta, TEXTO_SIN_AUTORIDAD)
    if rechazo is not None:
        return rechazo
    if resultado.get("ok") and not mal_formados:
        repetida = bool(resultado.get("repetida"))
        return json_de_la_web({"area_id": str(resultado["area_id"]), "repetida": repetida},
                              200 if repetida else 201)
    # Sin la clave (porque había un dato mal formado), la base dice que falta: no es lo que pasó.
    errores = [e for e in resultado.get("errores") or []
               if not (mal_formados and (e.get("campo"), e.get("motivo")) == ("clave", "falta"))]
    return _rechazos(mal_formados, errores)


@router.post("/api/equipo/areas/revisar")
async def revisar_un_cambio_de_area(request: Request):
    """La vista previa de un cambio de área, por la puerta del equipo (sólo Dirección)."""
    return await escribir_por_la_puerta(
        request, PUERTA_DEL_EQUIPO, None,
        lambda conn, token, espacio, cuerpo: _revisar(conn, PUERTA_DEL_EQUIPO, token, espacio,
                                                      cuerpo))


@router.post("/api/equipo/areas")
async def confirmar_un_cambio_de_area(request: Request):
    """Crear, renombrar o archivar un área, por la puerta del equipo (sólo Dirección)."""
    return await escribir_por_la_puerta(
        request, PUERTA_DEL_EQUIPO, None,
        lambda conn, token, espacio, cuerpo: _confirmar(conn, PUERTA_DEL_EQUIPO, token, espacio,
                                                        cuerpo))


@router.post("/admin/api/espacios/{espacio_id}/equipo/areas/revisar")
async def revisar_un_cambio_de_area_en_la_administracion(espacio_id: str, request: Request):
    """La vista previa de un cambio de área en un espacio, por la puerta de administración."""
    return await escribir_por_la_puerta(
        request, PUERTA_DE_ADMINISTRACION, espacio_id,
        lambda conn, token, espacio, cuerpo: _revisar(conn, PUERTA_DE_ADMINISTRACION, token,
                                                      espacio, cuerpo))


@router.post("/admin/api/espacios/{espacio_id}/equipo/areas")
async def confirmar_un_cambio_de_area_en_la_administracion(espacio_id: str, request: Request):
    """Crear, renombrar o archivar un área de un espacio, por la puerta de administración."""
    return await escribir_por_la_puerta(
        request, PUERTA_DE_ADMINISTRACION, espacio_id,
        lambda conn, token, espacio, cuerpo: _confirmar(conn, PUERTA_DE_ADMINISTRACION, token,
                                                        espacio, cuerpo))


# --- El alta de una persona (J7-5) --------------------------------------------------------------

ACCIONES_DE_PERSONA = ("alta", "reactivar")
VIGENCIA_DEL_ENLACE_EN_DIAS = 14

TEXTO_SIN_ENLACE = "No se pudo armar el enlace. Probá de nuevo."
TEXTOS_DE_LAS_PERSONAS: dict[tuple[str, str], str] = {
    ("accion", "no_existe"): "Eso no se puede hacer con una persona.",
    ("persona", "falta"): "Elegí a la persona.",
    ("persona", "no_existe"): "Esa persona no está en este equipo.",
    ("persona", "ya_esta_en_el_equipo"): "Esa persona ya está en el equipo.",
    ("persona", "no_esta_en_el_equipo"): "Esa persona ya no está en el equipo.",
    ("persona", "ya_conectada"): "Esa persona ya conectó su Telegram.",
    ("nombre", "falta"): "Falta el nombre.",
    ("nombre", "demasiado_largo"): "El nombre es demasiado largo: hasta 80 caracteres.",
    ("area", "falta"): "Elegí el área.",
    ("area", "no_existe"): "Esa área no está en este equipo.",
    ("area", "archivada"): "Esa área está archivada: elegí otra.",
    ("rol", "falta"): "Elegí el rol.",
    ("rol", "no_existe"): "Ese rol no es de este equipo.",
    ("rol", "es_de_direccion"): "La autoridad final no se da con un alta: se pasa.",
    ("aprobador", "falta"): "Elegí quién aprueba su trabajo.",
    ("aprobador", "no_es_integrante_activo"): "Esa persona no es integrante activo de este equipo.",
    ("aprobador", "es_la_misma_persona"): "Nadie aprueba su propio trabajo.",
    ("bot", "sin_usuario"):
        "Todavía no se puede armar el enlace: falta configurar el bot del equipo.",
    ("enlace", "mal_formado"): TEXTO_SIN_ENLACE,
    ("huella", "falta"): TEXTO_SIN_VISTA_PREVIA,
    ("huella", "mal_formada"): TEXTO_SIN_VISTA_PREVIA,
    ("huella", "el_equipo_cambio"): "El equipo cambió desde la vista previa: revisala de nuevo.",
    ("clave", "falta"): TEXTO_SIN_CONFIRMAR,
    ("clave", "mal_formada"): TEXTO_SIN_CONFIRMAR,
    ("clave", "usada_con_otros_datos"):
        "Este envío ya hizo otro cambio. Recargá la página para hacer uno nuevo.",
    ("equipo", "no_cuadra"): "Con este cambio el equipo no cuadraría: no se hizo.",
}

# Los datos del pedido, con el `campo` con que los nombra la base.
_IDS_DE_PERSONA = {"membership_id": "persona", "area_id": "area", "rol_id": "rol",
                   "aprobador_id": "aprobador"}
_TEXTOS_DE_PERSONA = {"nombre": "nombre", "clave": "clave", "huella": "huella"}
_FEMENINOS_DE_PERSONA = {"persona", "area", "clave", "huella"}
_PARA_LA_VISTA_PREVIA_DE_PERSONA = ("membership_id", "nombre", "area_id", "rol_id",
                                    "aprobador_id")


def _mal_formado_de_persona(campo: str) -> dict[str, str]:
    return {"campo": campo,
            "motivo": "mal_formada" if campo in _FEMENINOS_DE_PERSONA else "mal_formado"}


def _texto_de_persona(fila: dict[str, Any]) -> dict[str, str]:
    """Un rechazo del alta con sus palabras."""
    campo, motivo = str(fila.get("campo", "")), str(fila.get("motivo", ""))
    if motivo.startswith("mal_formad") and (campo, motivo) not in TEXTOS_DE_LAS_PERSONAS:
        texto = TEXTO_DE_UN_DATO_MAL_FORMADO
    else:
        texto = TEXTOS_DE_LAS_PERSONAS.get((campo, motivo), TEXTO_SIN_CONFIRMAR)
    return {"campo": campo, "motivo": motivo, "texto": texto}


def _uuid(valor: Any) -> str | None:
    if not isinstance(valor, str):
        return None
    try:
        return str(uuid.UUID(valor))
    except ValueError:
        return None


def leer_la_persona(cuerpo: Any) -> tuple[dict[str, Any], list[dict[str, str]]]:
    """Los datos de un alta (o de volver a sumar a alguien) como los recibe la base, y los que
    llegaron con una forma que no sirve. Lo que falta lo dice la base, todo junto."""
    cuerpo = cuerpo if isinstance(cuerpo, dict) else {}
    datos: dict[str, Any] = {}
    errores: list[dict[str, str]] = []
    accion = cuerpo.get("accion")
    datos["accion"] = accion if isinstance(accion, str) and accion in ACCIONES_DE_PERSONA else None
    if datos["accion"] is None:
        errores.append({"campo": "accion", "motivo": "no_existe"})
    for clave, campo in _IDS_DE_PERSONA.items():
        valor = cuerpo.get(clave)
        datos[clave] = None if valor in (None, "") else _uuid(valor)
        if valor not in (None, "") and datos[clave] is None:
            errores.append(_mal_formado_de_persona(campo))
    for clave, campo in _TEXTOS_DE_PERSONA.items():
        valor = cuerpo.get(clave)
        datos[clave] = valor if isinstance(valor, str) else None
        if valor is not None and not isinstance(valor, str):
            errores.append(_mal_formado_de_persona(campo))
    return datos, errores


def _rechazos_de_persona(mal_formados: list[dict[str, str]],
                         de_la_base: list[dict[str, Any]]) -> Response:
    """422 con todo lo que hay que corregir, como `_rechazos`."""
    ya_dichos = {e["campo"] for e in mal_formados}
    errores = [*mal_formados, *(e for e in de_la_base if e.get("campo") not in ya_dichos)]
    return json_de_la_web({"errores": [_texto_de_persona(e) for e in errores]}, 422)


def _revisar_la_persona(conn, puerta: str, token: str, espacio: str | None,
                        cuerpo: Any) -> Response:
    """La vista previa de un alta: 200 con lo que haría, quién la aprueba, su huella y los
    problemas que dejaría; 422 con lo que no se puede. No escribe nada."""
    datos, mal_formados = leer_la_persona(cuerpo)
    if datos["accion"] is None:
        return _rechazos_de_persona(mal_formados, [])
    with sin_espacio(conn) as cur:
        con_la_version_del_nucleo(cur)
        cur.execute("select vista_previa_de_alta(%s, %s, %s, %s, %s) as r",
                    (puerta, hash_del_token(token), espacio, datos["accion"],
                     Jsonb({k: datos[k] for k in _PARA_LA_VISTA_PREVIA_DE_PERSONA})))
        resultado: dict[str, Any] = cur.fetchone()["r"]
    rechazo = rechazo_de_la_base(resultado, puerta, TEXTO_SIN_AUTORIDAD)
    if rechazo is not None:
        return rechazo
    if not resultado.get("ok") or mal_formados:
        return _rechazos_de_persona(mal_formados, resultado.get("errores") or [])
    return json_de_la_web({k: v for k, v in resultado.items() if k != "ok"})


def _confirmar_la_persona(conn, puerta: str, token: str, espacio: str | None,
                          cuerpo: Any) -> Response:
    """La confirmación: 201 con la persona; la misma clave con la misma huella, 200 con la misma;
    422 con lo que no se puede. Con un dato mal formado no se escribe nada: la clave no llega."""
    datos, mal_formados = leer_la_persona(cuerpo)
    if datos["accion"] is None:
        return _rechazos_de_persona(mal_formados, [])
    clave = None if mal_formados else datos["clave"]
    puerta_y_sesion = (puerta, hash_del_token(token), espacio)
    with sin_espacio(conn) as cur:
        con_la_version_del_nucleo(cur)
        if datos["accion"] == "alta":
            cur.execute("select dar_de_alta(%s, %s, %s, %s, %s, %s, %s, %s, %s) as r",
                        (*puerta_y_sesion, datos["nombre"], datos["area_id"], datos["rol_id"],
                         datos["aprobador_id"], clave, datos["huella"]))
        else:
            cur.execute("select reactivar_integrante(%s, %s, %s, %s, %s, %s, %s, %s, %s) as r",
                        (*puerta_y_sesion, datos["membership_id"], datos["area_id"],
                         datos["rol_id"], datos["aprobador_id"], clave, datos["huella"]))
        resultado: dict[str, Any] = cur.fetchone()["r"]
    rechazo = rechazo_de_la_base(resultado, puerta, TEXTO_SIN_AUTORIDAD)
    if rechazo is not None:
        return rechazo
    if resultado.get("ok") and not mal_formados:
        repetida = bool(resultado.get("repetida"))
        return json_de_la_web({"membership_id": str(resultado["membership_id"]),
                               "repetida": repetida}, 200 if repetida else 201)
    # Sin la clave (porque había un dato mal formado), la base dice que falta: no es lo que pasó.
    errores = [e for e in resultado.get("errores") or []
               if not (mal_formados and (e.get("campo"), e.get("motivo")) == ("clave", "falta"))]
    return _rechazos_de_persona(mal_formados, errores)


def _emitir_el_enlace(conn, puerta: str, token: str, espacio: str | None,
                      cuerpo: Any) -> Response:
    """El enlace de activación de quien no conectó su Telegram (ADR 0024), una sola vez: 200 con
    el enlace de Telegram; 422 con lo que no se puede. El token se arma acá y sólo sale en esta
    respuesta: la base recibe su huella, la que busca `onboarding.canjear`."""
    cuerpo = cuerpo if isinstance(cuerpo, dict) else {}
    valor = cuerpo.get("membership_id")
    persona = _uuid(valor)
    if valor not in (None, "") and persona is None:
        return _rechazos_de_persona([_mal_formado_de_persona("persona")], [])
    del_enlace = secrets.token_urlsafe(24)
    with sin_espacio(conn) as cur:
        con_la_version_del_nucleo(cur)
        cur.execute("select emitir_enlace_de_activacion(%s, %s, %s, %s, %s) as r",
                    (puerta, hash_del_token(token), espacio, persona,
                     huella_del_token(del_enlace)))
        resultado: dict[str, Any] = cur.fetchone()["r"]
    rechazo = rechazo_de_la_base(resultado, puerta, TEXTO_SIN_AUTORIDAD)
    if rechazo is not None:
        return rechazo
    if not resultado.get("ok"):
        return _rechazos_de_persona([], resultado.get("errores") or [])
    return json_de_la_web({
        "membership_id": str(resultado["membership_id"]),
        "nombre": resultado["nombre"],
        "enlace": f"https://t.me/{resultado['bot_usuario']}?start={del_enlace}",
        "expira_en": resultado["expira_en"],
        "vence_en_dias": VIGENCIA_DEL_ENLACE_EN_DIAS,
    })


@router.post("/api/equipo/personas/revisar")
async def revisar_un_alta(request: Request):
    """La vista previa de un alta, por la puerta del equipo (sólo Dirección)."""
    return await escribir_por_la_puerta(
        request, PUERTA_DEL_EQUIPO, None,
        lambda conn, token, espacio, cuerpo: _revisar_la_persona(conn, PUERTA_DEL_EQUIPO, token,
                                                                 espacio, cuerpo))


@router.post("/api/equipo/personas")
async def confirmar_un_alta(request: Request):
    """Dar de alta a una persona o volver a sumar a quien estuvo, por la puerta del equipo."""
    return await escribir_por_la_puerta(
        request, PUERTA_DEL_EQUIPO, None,
        lambda conn, token, espacio, cuerpo: _confirmar_la_persona(conn, PUERTA_DEL_EQUIPO, token,
                                                                   espacio, cuerpo))


@router.post("/api/equipo/personas/enlace")
async def emitir_un_enlace_de_activacion(request: Request):
    """El enlace de activación de una persona sin conectar, por la puerta del equipo."""
    return await escribir_por_la_puerta(
        request, PUERTA_DEL_EQUIPO, None,
        lambda conn, token, espacio, cuerpo: _emitir_el_enlace(conn, PUERTA_DEL_EQUIPO, token,
                                                               espacio, cuerpo))


@router.post("/admin/api/espacios/{espacio_id}/equipo/personas/revisar")
async def revisar_un_alta_en_la_administracion(espacio_id: str, request: Request):
    """La vista previa de un alta en un espacio, por la puerta de administración."""
    return await escribir_por_la_puerta(
        request, PUERTA_DE_ADMINISTRACION, espacio_id,
        lambda conn, token, espacio, cuerpo: _revisar_la_persona(
            conn, PUERTA_DE_ADMINISTRACION, token, espacio, cuerpo))


@router.post("/admin/api/espacios/{espacio_id}/equipo/personas")
async def confirmar_un_alta_en_la_administracion(espacio_id: str, request: Request):
    """Dar de alta o volver a sumar a alguien en un espacio, por la puerta de administración."""
    return await escribir_por_la_puerta(
        request, PUERTA_DE_ADMINISTRACION, espacio_id,
        lambda conn, token, espacio, cuerpo: _confirmar_la_persona(
            conn, PUERTA_DE_ADMINISTRACION, token, espacio, cuerpo))


@router.post("/admin/api/espacios/{espacio_id}/equipo/personas/enlace")
async def emitir_un_enlace_de_activacion_en_la_administracion(espacio_id: str, request: Request):
    """El enlace de activación de una persona sin conectar de un espacio, por la puerta de
    administración."""
    return await escribir_por_la_puerta(
        request, PUERTA_DE_ADMINISTRACION, espacio_id,
        lambda conn, token, espacio, cuerpo: _emitir_el_enlace(
            conn, PUERTA_DE_ADMINISTRACION, token, espacio, cuerpo))
