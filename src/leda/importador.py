"""Importador de packs de espacio de trabajo.

Convierte un YAML de `espacios/` en filas de la base, corriendo antes las
validaciones de `nucleo/alta-de-equipo.md`.

Dos niveles:
  - Bloqueantes: el espacio no se activa. El núcleo las exige.
  - Advertencias: se importan igual, pero quedan registradas y se le muestran
    al administrador para que las responda a conciencia.

El pack se guarda con su hash. Cada decisión que Leda registre después va a
poder decir con qué versión exacta de la configuración se tomó.
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import psycopg
import yaml
from psycopg.types.json import Jsonb

from .db import admin, registrar_auditoria


class PackInvalido(Exception):
    def __init__(self, problemas: list[str]) -> None:
        self.problemas = problemas
        super().__init__("El pack no se puede activar:\n  - " + "\n  - ".join(problemas))


@dataclass
class Resultado:
    workspace_id: str
    slug: str
    version: int
    pack_hash: str
    activo: bool
    advertencias: list[str] = field(default_factory=list)
    pendientes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Validación
# ---------------------------------------------------------------------------

def _pendientes(nodo: Any, ruta: str = "") -> list[str]:
    """Todo valor literal PENDIENTE. Leda no los completa: quedan a la vista."""
    encontrados: list[str] = []
    if isinstance(nodo, dict):
        for k, v in nodo.items():
            encontrados += _pendientes(v, f"{ruta}.{k}" if ruta else str(k))
    elif isinstance(nodo, list):
        for i, v in enumerate(nodo):
            encontrados += _pendientes(v, f"{ruta}[{i}]")
    elif isinstance(nodo, str) and nodo.strip() == "PENDIENTE":
        encontrados.append(ruta)
    return encontrados


def _definido(valor: Any) -> bool:
    """PENDIENTE es un marcador de ausencia, no un valor."""
    return valor is not None and str(valor).strip() != "PENDIENTE"


# El usuario público del bot del equipo (`telegram.bot_usuario`, opcional): la web abre con él el
# chat con Leda (`https://t.me/<usuario>`; decisión 8 del usuario, 2026-10-12). Un usuario de
# Telegram: de 5 a 32 letras, números o "_", empezando con una letra (la base lo vuelve a exigir,
# migración 0060). No es un secreto; el token del bot, sí, y no va en el pack.
USUARIO_DEL_BOT = re.compile(r"[A-Za-z][A-Za-z0-9_]{4,31}")
BOT_USUARIO = "bot_usuario"


def usuario_del_bot(pack: dict[str, Any]) -> str | None:
    """El usuario del bot del equipo que declara el pack, sin "@", o `None` si no declara uno
    válido."""
    valor = (pack.get("telegram") or {}).get(BOT_USUARIO)
    if not _definido(valor):
        return None
    usuario = str(valor).strip().removeprefix("@")
    return usuario if USUARIO_DEL_BOT.fullmatch(usuario) else None


# Los nombres visibles de los niveles de objetivo (`niveles` del pack; mecánica §1), con la clave
# del tipo en la base. La web los muestra al crear un objetivo (ADR 0023, punto 11; migración
# 0068); sin uno, usa el del núcleo. Los de tarea y subtarea no se guardan.
NIVELES = "niveles"
NIVELES_DE_OBJETIVO = {"objetivo_estrategico": "estrategico", "hito": "hito",
                       "objetivo_operativo": "operativo"}
LARGO_MAXIMO_DE_UN_NIVEL = 60


def niveles_del_pack(pack: dict[str, Any]) -> tuple[dict[str, str], list[str]]:
    """Los nombres de los niveles de objetivo que declara el pack, por tipo, y las claves del
    pack cuyo nombre no sirve (vacío, que no es un texto o más largo que el tope de la base)."""
    niveles = pack.get(NIVELES)
    if not isinstance(niveles, dict):
        return {}, []
    nombres: dict[str, str] = {}
    malos: list[str] = []
    for clave, tipo in NIVELES_DE_OBJETIVO.items():
        if clave not in niveles or not _definido(niveles[clave]):
            continue
        valor = niveles[clave]
        nombre = valor.strip() if isinstance(valor, str) else ""
        if nombre and len(nombre) <= LARGO_MAXIMO_DE_UN_NIVEL:
            nombres[tipo] = nombre
        else:
            malos.append(clave)
    return nombres, malos


CLAVES_PROHIBIDAS = {
    "constitucion", "invariantes", "prohibiciones",
    "permitir_cierre_sin_evidencia", "desactivar_auditoria",
    "desactivar_confirmacion_humana", "permitir_comunicaciones_externas",
}


def validar(pack: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Devuelve (bloqueantes, advertencias)."""
    bloqueantes: list[str] = []
    advertencias: list[str] = []

    # Un pack no puede tocar el núcleo.
    for clave in pack:
        if clave in CLAVES_PROHIBIDAS:
            bloqueantes.append(
                f"El pack intenta modificar una regla del núcleo: '{clave}'.")

    roles = pack.get("roles") or []
    areas = {a["slug"] for a in pack.get("areas") or []}
    personas = pack.get("personas") or []

    finales = [r for r in roles if r.get("autoridad_final")]
    if not finales:
        bloqueantes.append(
            "Ningún rol tiene autoridad final. Sin eso no hay forma de "
            "desempatar y el núcleo no lo permite.")
    elif len(finales) > 1:
        bloqueantes.append(
            f"Hay {len(finales)} roles con autoridad final. Tiene que haber uno.")

    slugs_rol = {r["slug"] for r in roles}
    for p in personas:
        if not p.get("area"):
            bloqueantes.append(f"{p.get('nombre','?')} no tiene área asignada.")
        elif p["area"] not in areas:
            bloqueantes.append(
                f"{p['nombre']} tiene un área que no existe: '{p['area']}'.")
        if p.get("rol") not in slugs_rol:
            bloqueantes.append(
                f"{p.get('nombre','?')} tiene un rol que no existe: '{p.get('rol')}'.")

    # Cadena de aprobación: cada persona declara quién revisa su trabajo.
    ids = {p.get("id") for p in personas if p.get("id")}

    # El referente de cada área (ADR 0019, decisión 7b): una persona del pack, por su id.
    for a in pack.get("areas") or []:
        if a.get("referente") is not None and a["referente"] not in ids:
            bloqueantes.append(
                f"El área '{a.get('slug')}' declara un referente que no existe: "
                f"'{a['referente']}'.")
    raices = []
    for p in personas:
        jefe = p.get("aprobado_por")
        if "aprobado_por" not in p:
            bloqueantes.append(
                f"{p.get('nombre','?')} no declara quién aprueba su trabajo. "
                f"Poné 'aprobado_por', o 'null' si es la raíz de la cadena.")
        elif jefe is None:
            raices.append(p)
        elif jefe not in ids:
            bloqueantes.append(
                f"{p.get('nombre','?')} declara un aprobador que no existe: "
                f"'{jefe}'.")
        elif jefe == p.get("id"):
            bloqueantes.append(f"{p.get('nombre','?')} se aprueba a sí mismo.")

    if not raices:
        bloqueantes.append(
            "Nadie es la raíz de la cadena de aprobación. Alguien tiene que "
            "tener 'aprobado_por: null'.")
    elif len(raices) > 1:
        advertencias.append(
            "Hay más de una persona sin aprobador: "
            + ", ".join(r["nombre"] for r in raices)
            + ". Su trabajo no lo revisa nadie.")
    else:
        advertencias.append(
            f"El trabajo de {raices[0]['nombre']} no lo revisa nadie: es la "
            f"raíz de la cadena.")

    # Ciclos en la cadena.
    padre = {p["id"]: p.get("aprobado_por") for p in personas if p.get("id")}
    for inicio in padre:
        visto, actual = set(), inicio
        while actual is not None:
            if actual in visto:
                bloqueantes.append(
                    f"La cadena de aprobación tiene un ciclo en '{inicio}'.")
                break
            visto.add(actual)
            actual = padre.get(actual)

    # Un aprobador sin suplente frena al equipo cuando no está.
    for rol in finales:
        cuantos = sum(1 for p in personas if p.get("rol") == rol["slug"])
        if cuantos == 1:
            advertencias.append(
                f"El rol '{rol['slug']}' lo ocupa una sola persona y no tiene "
                f"suplente. Si no está, no se aprueba nada.")

    # Cadencia fuera del calendario declarado.
    dias_ok = set((pack.get("calendario") or {}).get("dias") or [])
    for job in pack.get("cadencia") or []:
        cuando = str(job.get("cuando", "")).lower()
        for dia in ("lunes", "martes", "miercoles", "jueves", "viernes",
                    "sabado", "domingo"):
            if dia in cuando and dias_ok and dia not in dias_ok:
                advertencias.append(
                    f"La cadencia '{job.get('nombre')}' cae en {dia}, "
                    f"pero el equipo no trabaja ese día.")

    # Volumen de contacto contra el tope declarado.
    tope = (pack.get("limites_de_contacto") or {}).get(
        "max_mensajes_automaticos_por_persona_por_dia")
    if tope:
        privados: dict[str, int] = {}
        for job in pack.get("cadencia") or []:
            if job.get("audiencia") == "privado_cada_integrante":
                dia = str(job.get("cuando", "")).split()[0].lower()
                privados[dia] = privados.get(dia, 0) + 1
        excedidos = {d: n for d, n in privados.items() if n > tope}
        if excedidos:
            advertencias.append(
                f"Con esta cadencia hay días que superan el tope de {tope} "
                f"mensajes por persona: {excedidos}.")

    bloqueantes.extend(_validar_tipos_de_evidencia(pack))

    tg = pack.get("telegram") or {}
    # El token NO se declara acá: es un secreto y vive en el entorno. El pack
    # se versiona en git, así que no puede contener credenciales.
    slug = ((pack.get("espacio") or {}).get("slug") or "").upper()
    if slug and not os.environ.get(f"LEDA_BOT_TOKEN_{slug}"):
        bloqueantes.append(
            f"Falta LEDA_BOT_TOKEN_{slug} en el entorno. El token del bot va "
            f"en .env, nunca en el pack.")
    if not _definido(tg.get("grupo_gestion_id")):
        bloqueantes.append("Falta el identificador del grupo de gestión.")
    if _definido(tg.get(BOT_USUARIO)) and usuario_del_bot(pack) is None:
        advertencias.append(
            "El usuario del bot (telegram.bot_usuario) no es un usuario de Telegram: se "
            "ignora y la web no muestra el botón para consultar a Leda.")
    _, niveles_malos = niveles_del_pack(pack)
    if niveles_malos:
        advertencias.append(
            "Hay nombres de niveles que no sirven (niveles: " + ", ".join(niveles_malos)
            + "): tienen que ser un texto de hasta "
            f"{LARGO_MAXIMO_DE_UN_NIVEL} caracteres. Se usa el nombre del núcleo.")
    if not pack.get("calendario"):
        bloqueantes.append(
            "Falta el calendario laboral. Toda la escalera de recordatorios "
            "se calcula sobre él.")

    return bloqueantes, advertencias


# ---------------------------------------------------------------------------
# Importación
# ---------------------------------------------------------------------------

def importar(
    conn: psycopg.Connection,
    ruta: Path,
    *,
    activar: bool = False,
    aprobado_por: str | None = None,
) -> Resultado:
    crudo = ruta.read_text(encoding="utf-8")
    pack = yaml.safe_load(crudo)
    pack_hash = hashlib.sha256(crudo.encode("utf-8")).hexdigest()

    pendientes = _pendientes(pack)
    bloqueantes, advertencias = validar(pack)

    # Los identificadores de Telegram no salen del pack: llegan cuando cada
    # persona abre su enlace de activación. Un espacio puede activarse antes
    # de que nadie lo haya hecho; hasta entonces sus integrantes existen,
    # tienen tareas y cuentan para los informes, pero no reciben privados.
    # El pack puede declarar qué pendientes no impiden arrancar.
    tolerados = set((pack.get("pendientes") or {}).get("no_bloqueantes") or [])

    faltan = [p for p in pendientes
              if not p.endswith("telegram_user_id") and p not in tolerados]
    sin_activar = sum(1 for p in pendientes if p.endswith("telegram_user_id"))

    if activar and faltan:
        bloqueantes.append(
            f"Hay {len(faltan)} valores sin definir: " + ", ".join(faltan[:5])
            + ("…" if len(faltan) > 5 else ""))

    if activar and bloqueantes:
        raise PackInvalido(bloqueantes)

    slug = pack["espacio"]["slug"]

    with admin(conn) as cur:
        cur.execute(
            """
            insert into workspace (slug, nombre, zona_horaria, grupo_chat_id, activo)
            values (%s, %s, %s, %s, %s)
            on conflict (slug) do update
               set nombre = excluded.nombre,
                   zona_horaria = excluded.zona_horaria
            returning id
            """,
            (slug, pack["espacio"]["nombre"],
             pack["espacio"].get("zona_horaria", "America/Argentina/Buenos_Aires"),
             _entero(pack.get("telegram", {}).get("grupo_gestion_id")),
             activar),
        )
        ws = cur.fetchone()["id"]

        cur.execute(
            "select coalesce(max(version), 0) + 1 as v from workspace_version "
            "where workspace_id = %s", (ws,))
        version = cur.fetchone()["v"]

        cur.execute(
            """insert into workspace_version
                 (workspace_id, version, pack_hash, aprobado_por)
               values (%s, %s, %s, %s)""",
            (ws, version, pack_hash, aprobado_por),
        )

        # El pack sólo arma un equipo vacío (J7-2; usuario, 2026-10-15, J7 punto 1): con gente,
        # el equipo lo gobierna la web y el archivo no lo pisa.
        cur.execute("select exists (select 1 from membership where workspace_id = %s) as hay",
                    (ws,))
        equipo_existente = cur.fetchone()["hay"]
        if equipo_existente:
            advertencias.append(AVISO_EQUIPO_EXISTENTE)
        else:
            if sin_activar:
                advertencias.append(
                    f"{sin_activar} persona(s) todavía no activaron su enlace de "
                    f"Telegram. Hasta que lo hagan no reciben seguimiento privado.")
            _importar_equipo(cur, ws, pack)

        _importar_configuracion(cur, ws, pack)
        _importar_politica_evidencia(cur, ws, pack, equipo_existente=equipo_existente)
        _importar_cadencia(cur, ws, pack)
        _importar_ajustes(cur, ws, pack)
        _importar_objetivo_inicial(cur, ws, pack)

        registrar_auditoria(
            cur, accion="importar_pack", workspace_id=ws,
            actor_app_user_id=aprobado_por, actor_kind="persona",
            sujeto_tipo="workspace", sujeto_id=ws, pack_hash=pack_hash,
            detalle={"version": version, "activado": activar,
                     "equipo_del_pack": "no_aplicado" if equipo_existente else "aplicado",
                     "advertencias": advertencias, "pendientes": pendientes},
        )

    return Resultado(
        workspace_id=str(ws), slug=slug, version=version, pack_hash=pack_hash,
        activo=activar, advertencias=advertencias, pendientes=pendientes,
    )


def _entero(v: Any) -> int | None:
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


# Lo que dice el importador cuando el espacio ya tiene gente (J7-2).
AVISO_EQUIPO_EXISTENTE = (
    "El equipo ya existe: las personas, las áreas y quién aprueba a quién se cambian desde la "
    "web; el archivo no los tocó.")


def _importar_equipo(cur, ws, pack) -> None:
    """Las áreas, los roles, las personas con su aprobador, los referentes, la política de
    aprobación y las rutas de escalamiento: sólo en un espacio sin gente (J7-2)."""
    _importar_areas_y_roles(cur, ws, pack)
    _importar_personas(cur, ws, pack)
    _importar_politica(cur, ws, pack)
    _importar_escalamiento(cur, ws, pack)


def _importar_areas_y_roles(cur, ws, pack) -> None:
    for a in pack.get("areas") or []:
        cur.execute(
            """insert into area (workspace_id, slug, nombre) values (%s, %s, %s)
               on conflict (workspace_id, slug) do update set nombre = excluded.nombre""",
            (ws, a["slug"], a["nombre"]))

    # El índice parcial impide dos autoridades finales; para no chocar contra él
    # al reimportar, primero bajamos todas y después subimos la que corresponde.
    cur.execute("update rol set autoridad_final = false where workspace_id = %s", (ws,))
    for r in pack.get("roles") or []:
        cur.execute(
            """insert into rol (workspace_id, slug, nombre, autoridad_final)
               values (%s, %s, %s, false)
               on conflict (workspace_id, slug) do update set nombre = excluded.nombre""",
            (ws, r["slug"], r["nombre"]))
    for r in pack.get("roles") or []:
        if r.get("autoridad_final"):
            cur.execute(
                "update rol set autoridad_final = true where workspace_id = %s and slug = %s",
                (ws, r["slug"]))


def _importar_configuracion(cur, ws, pack) -> None:
    """El calendario, el glosario y cómo habla Leda: se aplican en cada importación."""
    cal = pack.get("calendario") or {}
    if cal:
        inicio, _, fin = str(cal.get("horario", "09:00-17:00")).partition("-")
        cur.execute(
            """insert into work_calendar (workspace_id, dias, hora_inicio, hora_fin)
               values (%s, %s, %s, %s)
               on conflict (workspace_id) do update
                 set dias = excluded.dias,
                     hora_inicio = excluded.hora_inicio,
                     hora_fin = excluded.hora_fin""",
            (ws, cal.get("dias") or [], inicio.strip(), fin.strip()))

    for g in pack.get("glosario") or []:
        cur.execute(
            """insert into glossary_term
                 (workspace_id, termino, definicion, variantes_incorrectas, fuera_de_alcance)
               values (%s, %s, %s, %s, %s)
               on conflict (workspace_id, termino) do update
                 set definicion = excluded.definicion,
                     variantes_incorrectas = excluded.variantes_incorrectas,
                     fuera_de_alcance = excluded.fuera_de_alcance""",
            (ws, g["termino"], g.get("definicion"),
             g.get("variantes_incorrectas") or [], bool(g.get("fuera_de_alcance"))))

    p = pack.get("persona") or {}
    if p:
        cur.execute(
            """insert into persona_config
                 (workspace_id, nombre_visible, registro, formalidad, longitud,
                  emojis, presentacion)
               values (%s, %s, %s, %s, %s, %s, %s)
               on conflict (workspace_id) do update
                 set nombre_visible = excluded.nombre_visible,
                     registro = excluded.registro,
                     formalidad = excluded.formalidad,
                     longitud = excluded.longitud,
                     emojis = excluded.emojis,
                     presentacion = excluded.presentacion""",
            (ws, p.get("nombre_visible", "Leda"), p.get("registro", "vos"),
             p.get("formalidad", "profesional_cordial"), p.get("longitud", "breve"),
             bool(p.get("emojis")), p.get("presentacion")))


def _importar_personas(cur, ws, pack) -> None:
    por_id: dict[str, str] = {}

    for p in pack.get("personas") or []:
        tg = _entero(p.get("telegram_user_id"))
        if tg is not None:
            cur.execute(
                """insert into app_user (telegram_user_id, nombre) values (%s, %s)
                   on conflict (telegram_user_id) do update set nombre = excluded.nombre
                   returning id""",
                (tg, p["nombre"]))
            usuario = cur.fetchone()["id"]
        else:
            # Todavía no activó su enlace. Existe como persona del equipo, sin
            # identidad de Telegram: sus tareas pueden crearse igual.
            cur.execute("select id from app_user where nombre = %s and telegram_user_id is null",
                        (p["nombre"],))
            fila = cur.fetchone()
            if fila:
                usuario = fila["id"]
            else:
                cur.execute("insert into app_user (nombre) values (%s) returning id",
                            (p["nombre"],))
                usuario = cur.fetchone()["id"]

        cur.execute(
            """insert into membership (workspace_id, app_user_id, area_id, rol_id)
               select %s, %s,
                      (select id from area where workspace_id = %s and slug = %s),
                      (select id from rol  where workspace_id = %s and slug = %s)
               on conflict (workspace_id, app_user_id) do update
                 set area_id = excluded.area_id, rol_id = excluded.rol_id
               returning id""",
            (ws, usuario, ws, p["area"], ws, p["rol"]))
        if p.get("id"):
            por_id[p["id"]] = cur.fetchone()["id"]

    # Segunda pasada: la cadena es auto-referencial, así que las membresías
    # tienen que existir todas antes de poder enlazarlas.
    for p in pack.get("personas") or []:
        if not p.get("id"):
            continue
        jefe = por_id.get(p.get("aprobado_por")) if p.get("aprobado_por") else None
        cur.execute(
            "update membership set aprobador_membership_id = %s where id = %s",
            (jefe, por_id[p["id"]]))

    # El referente de cada área (ADR 0019, decisión 7b; migración 0036): un dato del espacio,
    # no el nombre de un rol. Un área sin `referente` queda sin él (también al reimportar).
    for a in pack.get("areas") or []:
        cur.execute(
            "update area set referente_membership_id = %s where workspace_id = %s and slug = %s",
            (por_id.get(a.get("referente")) if a.get("referente") else None, ws, a["slug"]))


def _importar_politica(cur, ws, pack) -> None:
    cur.execute("""delete from approval_policy where workspace_id = %s""", (ws,))
    for r in (pack.get("aprobacion") or {}).get("reglas") or []:
        declarada = r.get("autoaprobacion_declarada")
        cur.execute(
            """insert into approval_policy
                 (workspace_id, sujeto, area_id, autoaprobacion_declarada, motivo)
               values (%s, %s,
                       (select id from area where workspace_id = %s and slug = %s),
                       %s, %s)
               returning id""",
            (ws, r["sujeto"], ws, r.get("area"), declarada is True, r.get("motivo")))
        pol = cur.fetchone()["id"]

        for req in r.get("requiere") or []:
            if req == "aprobacion_de_cada_area_participante":
                cur.execute(
                    "insert into approval_requirement (approval_policy_id, tipo) "
                    "values (%s, 'cada_area_participante')", (pol,))
            elif str(req).startswith("rol:"):
                # "rol:referente@ot" significa el referente DE OT, no
                # cualquier referente. Sin el área, el referente de otra área
                # podría aprobar trabajo que no le corresponde.
                slug, _, area_req = str(req)[4:].partition("@")
                cur.execute(
                    """insert into approval_requirement
                         (approval_policy_id, tipo, rol_id, area_id)
                       values (%s, 'rol',
                         (select id from rol  where workspace_id = %s and slug = %s),
                         (select id from area where workspace_id = %s and slug = %s))""",
                    (pol, ws, slug, ws, area_req or None))
            elif str(req).startswith("area:"):
                cur.execute(
                    """insert into approval_requirement (approval_policy_id, tipo, area_id)
                       values (%s, 'area', (select id from area where workspace_id = %s and slug = %s))""",
                    (pol, ws, str(req)[5:]))


def _importar_escalamiento(cur, ws, pack) -> None:
    cur.execute("delete from escalation_route where workspace_id = %s", (ws,))
    for i, e in enumerate(pack.get("escalamiento") or []):
        destino = str(e.get("destino", ""))
        rol_slug = destino[4:] if destino.startswith("rol:") else None
        cur.execute(
            """insert into escalation_route
                 (workspace_id, disparador, area_id, destino_rol_id,
                  destino_membership_id, orden)
               values (%s, %s,
                 (select id from area where workspace_id = %s and slug = %s),
                 (select id from rol  where workspace_id = %s and slug = %s),
                 (select m.id from membership m join app_user u on u.id = m.app_user_id
                   where m.workspace_id = %s and u.nombre = %s),
                 %s)""",
            (ws, e["disparador"], ws, e.get("area"), ws, rol_slug,
              ws, _nombre_de(pack, destino), i + 1))


# Las clases de evidencia que fija el código por el contenido (ADR 0019, decisión 5).
CLASES_DE_EVIDENCIA = ("texto", "imagen", "archivo", "enlace")


def _validar_tipos_de_evidencia(pack: dict[str, Any]) -> list[str]:
    """Cada tipo que pide una política de evidencia, y cada tipo que describe el pack, declara qué
    clases lo cubren y cómo se le dice a la persona (`evidencia.tipos`; ADR 0019, decisión 5). Sin
    eso, ninguna pieza lo cubriría y la tarea no se podría entregar nunca: se rechaza al importar,
    no al entregar. Desde la J2-18 cada área conoce todos los tipos del pack (`_tipos_del_area`):
    uno mal formado que ninguna área pide también llegaría a todas, así que se revisa igual."""
    evidencia = pack.get("evidencia") or {}
    tipos = evidencia.get("tipos") or {}
    if not isinstance(tipos, dict):
        return ["Los tipos de evidencia del pack (evidencia.tipos) no describen cada tipo con "
                "sus clases y sus palabras."]
    errores = []
    usados = {t for lista in (evidencia.get("por_area") or {}).values() for t in lista or []}
    for tipo in sorted(usados | set(tipos), key=str):
        definido = tipos.get(tipo)
        clases = (definido or {}).get("clases") if isinstance(definido, dict) else None
        palabras = (definido or {}).get("en_palabras") if isinstance(definido, dict) else None
        if not isinstance(clases, list) or not clases:
            errores.append(
                f"El tipo de evidencia '{tipo}' no declara qué clases lo cubren "
                f"(evidencia.tipos.{tipo}.clases).")
        elif any(c not in CLASES_DE_EVIDENCIA for c in clases):
            errores.append(
                f"El tipo de evidencia '{tipo}' declara una clase que no existe; valen "
                f"{', '.join(CLASES_DE_EVIDENCIA)}.")
        if not isinstance(palabras, str) or not palabras.strip():
            errores.append(
                f"El tipo de evidencia '{tipo}' no dice cómo se le nombra a la persona "
                f"(evidencia.tipos.{tipo}.en_palabras).")
    return errores


def _tipos_del_area(pack: dict[str, Any]) -> dict[str, Any]:
    """Las clases y las palabras de todos los tipos de evidencia del pack: cada área conoce todos,
    y lo que pide su política es un dato que Leda tiene en cuenta al proponer, no un límite (J2-18
    y J2-19). Un tipo mal formado lo rechaza `validar` antes de importar; si igual llegara uno, no
    se agrega a medias ni rompe la importación: queda afuera."""
    tipos = (pack.get("evidencia") or {}).get("tipos") or {}
    if not isinstance(tipos, dict):
        return {}
    return {t: {"clases": list(d["clases"]), "en_palabras": d["en_palabras"]}
            for t, d in tipos.items()
            if isinstance(d, dict) and isinstance(d.get("clases"), list) and d["clases"]
            and isinstance(d.get("en_palabras"), str) and d["en_palabras"].strip()}


def _importar_politica_evidencia(cur, ws, pack, *, equipo_existente: bool = False) -> None:
    """La evidencia que pide cada área del archivo. En un espacio vacío, el archivo arma todo: la
    de un área que no nombra se borra. Con gente (J7-4), las áreas que no nombra son de la web y
    conservan la suya: sin ella, sus tareas no se podrían cargar."""
    por_area = (pack.get("evidencia") or {}).get("por_area") or {}
    if not equipo_existente:
        cur.execute(
            """delete from task_evidence_policy p
                where p.workspace_id = %s
                  and not exists (
                    select 1 from area a
                     where a.id = p.area_id and a.slug = any(%s))""",
            (ws, list(por_area)))
    for area_slug, evidencia in por_area.items():
        # Las clases de cada tipo van con la política, y la versión cambia también si cambian
        # ellas (ADR 0019, decisión 5: dato del pack, versionado con la política).
        cur.execute(
            """insert into task_evidence_policy
                 (workspace_id, area_id, evidencia_requerida, tipos)
               select %s, a.id, %s, %s
                 from area a where a.workspace_id = %s and a.slug = %s
               on conflict (workspace_id, area_id) do update
                 set evidencia_requerida = excluded.evidencia_requerida,
                     tipos = excluded.tipos,
                     version = case
                       when task_evidence_policy.evidencia_requerida is distinct from
                            excluded.evidencia_requerida
                         or task_evidence_policy.tipos is distinct from excluded.tipos
                       then task_evidence_policy.version + 1
                       else task_evidence_policy.version
                     end,
                     actualizado_en = case
                       when task_evidence_policy.evidencia_requerida is distinct from
                            excluded.evidencia_requerida
                         or task_evidence_policy.tipos is distinct from excluded.tipos
                       then now() else task_evidence_policy.actualizado_en
                     end""",
            (ws, evidencia or [], Jsonb(_tipos_del_area(pack)), ws,
             area_slug))


def _nombre_de(pack: dict, destino: str) -> str | None:
    if not destino.startswith("persona:"):
        return None
    pid = destino[len("persona:"):]
    for p in pack.get("personas") or []:
        if p.get("id") == pid:
            return p["nombre"]
    return None


def _importar_cadencia(cur, ws, pack) -> None:
    cur.execute("delete from cadence_job where workspace_id = %s", (ws,))
    for job in pack.get("cadencia") or []:
        cur.execute(
            """insert into cadence_job
                 (workspace_id, nombre, cron, audiencia, plantilla_clave)
               values (%s, %s, %s, %s, %s)""",
            (ws, job["nombre"], _a_cron(job["cuando"]),
             job.get("audiencia", "grupo"), job.get("nombre")))


DIAS_CRON = {"lunes": 1, "martes": 2, "miercoles": 3, "miércoles": 3,
             "jueves": 4, "viernes": 5, "sabado": 6, "sábado": 6, "domingo": 0}


def _a_cron(cuando: str) -> str:
    """'lunes 09:15' -> '15 9 * * 1'. 'lunes a sabado 06:15' -> '15 6 * * 1-6'.

    Lo que no se puede traducir se guarda tal cual: el planificador sabe leer
    expresiones cron y también descripciones que APScheduler entiende.
    """
    texto = str(cuando).strip().lower()
    partes = texto.split()
    hora = next((p for p in partes if ":" in p), None)
    if not hora:
        return texto
    hh, _, mm = hora.partition(":")
    dias = [DIAS_CRON[p] for p in partes if p in DIAS_CRON]
    if not dias:
        return f"{int(mm)} {int(hh)} * * *"
    if " a " in texto and len(dias) == 2:
        return f"{int(mm)} {int(hh)} * * {dias[0]}-{dias[1]}"
    return f"{int(mm)} {int(hh)} * * {','.join(str(d) for d in sorted(set(dias)))}"


def _importar_objetivo_inicial(cur, ws, pack) -> None:
    """Crea el objetivo estratégico del pack si todavía no existe.

    Sin al menos un objetivo no se puede cargar ninguna tarea: el núcleo no
    admite trabajo suelto.
    """
    obj = pack.get("objetivo_inicial")
    if not obj:
        return

    cur.execute(
        "select id from objective where workspace_id = %s and titulo = %s",
        (ws, obj["titulo"]))
    if cur.fetchone():
        return

    cur.execute(
        """insert into objective (workspace_id, tipo, titulo, descripcion, estado)
           values (%s, 'estrategico', %s, %s, 'activo') returning id""",
        (ws, obj["titulo"], obj.get("descripcion")))
    raiz = cur.fetchone()["id"]
    cur.execute(
        """insert into objective_state_event (objective_id, estado_nuevo, actor_kind, motivo)
           values (%s, 'activo', 'sistema', 'creado al importar el pack')""",
        (raiz,))

    # Cada frente del pack pasa a ser un objetivo operativo colgado de la raíz.
    for f in obj.get("frentes") or []:
        cur.execute(
            """insert into objective (workspace_id, parent_id, tipo, titulo, estado)
               values (%s, %s, 'operativo', %s, 'activo') returning id""",
            (ws, raiz, f["titulo"]))
        hijo = cur.fetchone()["id"]
        cur.execute(
            """insert into objective_state_event (objective_id, estado_nuevo, actor_kind)
               values (%s, 'activo', 'sistema')""", (hijo,))


def _importar_ajustes(cur, ws, pack) -> None:
    import json

    ajustes: dict[str, Any] = {}
    umbral = (pack.get("aprobacion") or {}).get("umbral_reaprobacion")
    if umbral:
        ajustes["umbral_reaprobacion"] = umbral
    limites = pack.get("limites_de_contacto")
    if limites:
        ajustes["limites_de_contacto"] = limites
    bloqueos = pack.get("bloqueos")
    if bloqueos:
        ajustes["bloqueos"] = bloqueos
    tiempos = pack.get("tiempos_de_respuesta")
    if tiempos:
        ajustes["tiempos_de_respuesta"] = tiempos
    urgencia = pack.get("urgencia")
    if urgencia:
        ajustes["urgencia"] = urgencia

    bot = usuario_del_bot(pack)
    if bot:
        ajustes[BOT_USUARIO] = bot
    else:
        # Sacarlo del pack (o declararlo mal) lo saca de la web.
        cur.execute("delete from workspace_setting where workspace_id = %s and clave = %s",
                    (ws, BOT_USUARIO))

    niveles, _ = niveles_del_pack(pack)
    if niveles:
        ajustes[NIVELES] = niveles
    else:
        # Sin niveles en el pack, la web usa los nombres del núcleo.
        cur.execute("delete from workspace_setting where workspace_id = %s and clave = %s",
                    (ws, NIVELES))

    for clave, valor in ajustes.items():
        cur.execute(
            """insert into workspace_setting (workspace_id, clave, valor)
               values (%s, %s, %s)
               on conflict (workspace_id, clave) do update set valor = excluded.valor""",
            (ws, clave, json.dumps(valor, ensure_ascii=False)))
