"""Importador de packs de espacio de trabajo.

Convierte un YAML de `espacios/` en filas de la base, corriendo antes las
validaciones de `nucleo/alta-de-equipo.md`.

Dos niveles:
  - Bloqueantes: el espacio no se activa. El núcleo las exige.
  - Advertencias: se importan igual, pero quedan registradas y se le muestran
    al administrador para que las responda a conciencia.

El pack se guarda con su hash. Cada decisión que Prisma registre después va a
poder decir con qué versión exacta de la configuración se tomó.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import psycopg
import yaml

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
    """Todo valor literal PENDIENTE. Prisma no los completa: quedan a la vista."""
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

    redaccion = (pack.get("conversacion") or {}).get("redaccion")
    if redaccion is not None and redaccion not in ("A", "B"):
        advertencias.append(
            f"conversacion.redaccion vale '{redaccion}': las variantes son A y "
            f"B. Sin una variante válida Prisma usa B y lo registra.")

    # Cada frente del objetivo inicial pertenece a un área que el pack declara: sin
    # eso el objetivo quedaría sin área y el alta lo trataría como estratégico.
    for f in (pack.get("objetivo_inicial") or {}).get("frentes") or []:
        if not f.get("area"):
            bloqueantes.append(
                f"El frente «{f.get('titulo', '?')}» no tiene área asignada.")
        elif f["area"] not in areas:
            bloqueantes.append(
                f"El frente «{f.get('titulo', '?')}» tiene un área que no existe: "
                f"'{f['area']}'.")

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

    tg = pack.get("telegram") or {}
    # El token NO se declara acá: es un secreto y vive en el entorno. El pack
    # se versiona en git, así que no puede contener credenciales.
    slug = ((pack.get("espacio") or {}).get("slug") or "").upper()
    if slug and not os.environ.get(f"PRISMA_BOT_TOKEN_{slug}"):
        bloqueantes.append(
            f"Falta PRISMA_BOT_TOKEN_{slug} en el entorno. El token del bot va "
            f"en .env, nunca en el pack.")
    if not _definido(tg.get("grupo_gestion_id")):
        bloqueantes.append("Falta el identificador del grupo de gestión.")
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
    if sin_activar:
        advertencias.append(
            f"{sin_activar} persona(s) todavía no activaron su enlace de "
            f"Telegram. Hasta que lo hagan no reciben seguimiento privado.")

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

        _importar_taxonomia(cur, ws, pack)
        _importar_personas(cur, ws, pack)
        _importar_politica(cur, ws, pack)
        _importar_politica_evidencia(cur, ws, pack)
        _importar_cadencia(cur, ws, pack)
        _importar_ajustes(cur, ws, pack)
        advertencias += _importar_objetivo_inicial(cur, ws, pack)

        registrar_auditoria(
            cur, accion="importar_pack", workspace_id=ws,
            actor_app_user_id=aprobado_por, actor_kind="persona",
            sujeto_tipo="workspace", sujeto_id=ws, pack_hash=pack_hash,
            detalle={"version": version, "activado": activar,
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


def _importar_taxonomia(cur, ws, pack) -> None:
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
            (ws, p.get("nombre_visible", "Prisma"), p.get("registro", "vos"),
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


def _importar_politica_evidencia(cur, ws, pack) -> None:
    por_area = (pack.get("evidencia") or {}).get("por_area") or {}
    cur.execute(
        """delete from task_evidence_policy p
            where p.workspace_id = %s
              and not exists (
                select 1 from area a
                 where a.id = p.area_id and a.slug = any(%s))""",
        (ws, list(por_area)))
    for area_slug, evidencia in por_area.items():
        cur.execute(
            """insert into task_evidence_policy
                 (workspace_id, area_id, evidencia_requerida)
               select %s, a.id, %s
                 from area a where a.workspace_id = %s and a.slug = %s
               on conflict (workspace_id, area_id) do update
                 set evidencia_requerida = excluded.evidencia_requerida,
                     version = case
                       when task_evidence_policy.evidencia_requerida is distinct from
                            excluded.evidencia_requerida
                       then task_evidence_policy.version + 1
                       else task_evidence_policy.version
                     end,
                     actualizado_en = case
                       when task_evidence_policy.evidencia_requerida is distinct from
                            excluded.evidencia_requerida
                       then now() else task_evidence_policy.actualizado_en
                     end""",
            (ws, evidencia or [], ws, area_slug))


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


def _importar_objetivo_inicial(cur, ws, pack) -> list[str]:
    """Crea el objetivo estratégico del pack si todavía no existe.

    Sin al menos un objetivo no se puede cargar ninguna tarea: el núcleo no
    admite trabajo suelto.
    """
    obj = pack.get("objetivo_inicial")
    if not obj:
        return []

    cur.execute(
        "select id from objective where workspace_id = %s and titulo = %s",
        (ws, obj["titulo"]))
    if cur.fetchone():
        # Datos anteriores a la migración 0027: el objetivo no tenía área. Se
        # completa la que falta; la que ya tiene no se toca.
        return _completar_area_de_los_frentes(cur, ws, obj)

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
            """insert into objective (workspace_id, parent_id, tipo, titulo, estado,
                                      area_id)
               values (%s, %s, 'operativo', %s, 'activo', %s)
               returning id""",
            (ws, raiz, f["titulo"], _area_del_frente(cur, ws, f)))
        hijo = cur.fetchone()["id"]
        cur.execute(
            """insert into objective_state_event (objective_id, estado_nuevo, actor_kind)
               values (%s, 'activo', 'sistema')""", (hijo,))
    return []


def _area_del_frente(cur, ws, frente) -> str:
    """El área que el pack asigna a un frente. Un frente sin área, o con un slug
    que el espacio no tiene, es un pack inválido: nunca un objetivo sin área en
    silencio (el alta lo trataría como estratégico, de todas las áreas)."""
    slug = frente.get("area")
    if slug:
        cur.execute("select id from area where workspace_id = %s and slug = %s",
                    (ws, slug))
        fila = cur.fetchone()
        if fila:
            return fila["id"]
    razon = (f"tiene un área que no existe: '{slug}'" if slug
             else "no tiene área asignada")
    raise PackInvalido([f"El frente «{frente.get('titulo', '?')}» {razon}."])


def _completar_area_de_los_frentes(cur, ws, obj) -> list[str]:
    """Da a cada frente del pack, si todavía no la tiene, el área que el pack le
    asigna (F-B11). Nunca cambia un área ya puesta. Devuelve los avisos para el
    administrador: cuántos objetivos se completaron y qué frentes del pack no
    existen como objetivo operativo del espacio (no se les pudo poner área)."""
    completados = 0
    sin_objetivo: list[str] = []
    for f in obj.get("frentes") or []:
        area = _area_del_frente(cur, ws, f)
        cur.execute(
            """update objective set area_id = %s
                where workspace_id = %s and tipo = 'operativo' and titulo = %s
                  and area_id is null returning id""",
            (area, ws, f["titulo"]))
        completados += len(cur.fetchall())
        cur.execute(
            """select 1 from objective
                where workspace_id = %s and tipo = 'operativo' and titulo = %s""",
            (ws, f["titulo"]))
        if not cur.fetchone():
            sin_objetivo.append(f["titulo"])
    avisos = []
    if completados:
        avisos.append(
            f"Se completó el área de {completados} objetivo(s) operativo(s) que "
            f"no la tenían (datos anteriores a la migración 0027).")
    for titulo in sin_objetivo:
        avisos.append(
            f"El frente «{titulo}» del pack no existe como objetivo operativo del "
            f"espacio: no se le pudo asignar el área.")
    return avisos


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
    # Cómo se redactan las respuestas (ADR 0014): el interruptor A/B del
    # experimento, un dato del espacio. `redaccion.variante_redaccion` lo lee.
    variante = (pack.get("conversacion") or {}).get("redaccion")
    if variante:
        ajustes["redaccion"] = {"variante": variante}

    for clave, valor in ajustes.items():
        cur.execute(
            """insert into workspace_setting (workspace_id, clave, valor)
               values (%s, %s, %s)
               on conflict (workspace_id, clave) do update set valor = excluded.valor""",
            (ws, clave, json.dumps(valor, ensure_ascii=False)))
