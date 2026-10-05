"""Lo que se comprueba solo en cada paso de una conversación de prueba (E2-7).

`odd/tasks/prueba-chica-del-motor.md`, sección 6 ("Se comprueba solo"); ADR 0018, decisión 5b.
Una vez para todas las conversaciones: ninguna regla sabe de qué conversación es el paso.

- **La foto** (`foto`) es lo que hay en la base después de un paso: el estado de cada tarea, las
  previsiones, los bloqueos y quién los destraba, los avisos guardados con sus hechos, lo que
  salió, los incidentes, los avances anotados, las esperas, las preguntas y el último aviso de
  cada persona. **Los efectos** de un paso son lo nuevo entre dos fotos.
- **Las tareas se nombran por su clave** en la conversación (`PLC`, `COM`): los alias del turno
  (`T1`), los títulos y las opciones (`O1`) se traducen a la clave (`normalizar`).
- **Lo esperado** de cada paso viene del YAML, que copia la flecha del `.md`. Un valor `presente`
  pide que el dato esté; `ausente`, que no esté; uno que empieza con `~`, que el texto empiece
  así. Un diccionario esperado es un subconjunto del real; una lista, elemento por elemento.

**Cómo se clasifica una falla** (5b, la vez que no entiende tiene que ser una pregunta):

- `garantia`: un efecto que no estaba esperado (otra tarea, otra fecha, un aviso o un aviso al
  administrador de más), botones de más, más o menos de una respuesta por mensaje, o un mensaje
  de Leda de más sobre una tarea de la conversación;
- `comprension`: las jugadas no son las esperadas o falta un efecto esperado, sin ningún efecto
  de más (no entendió, pero no hizo otra cosa: que haya preguntado lo lee una persona);
- `motor`: con las jugadas esperadas, algo que el código hace distinto de lo esperado (los
  hechos, la pregunta, el estado después, lo que Leda manda por su cuenta).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from leda.db import admin

from .carga import ZONA, Mundo

GARANTIA, COMPRENSION, MOTOR = "garantia", "comprension", "motor"

# Los datos de una jugada que son palabras de la persona: se compara sólo si están.
DATOS_LIBRES = frozenset({"motivo", "causa", "palabras", "quien", "a", "que_pide"})
FUERA_DE_LA_LISTA = "fuera_de_la_lista"
ETAPA_FUERA_DE_LA_LISTA = "motor_fuera_de_la_lista"


@dataclass
class Falla:
    clase: str              # garantia | comprension | motor
    que: str                # qué se comprobó
    esperado: Any
    real: Any

    def __str__(self) -> str:
        return f"[{self.clase}] {self.que}: esperado {self.esperado!r}, real {self.real!r}"


@dataclass
class Comprobacion:
    fallas: list[Falla] = field(default_factory=list)

    def falla(self, clase: str, que: str, esperado: Any, real: Any) -> None:
        self.fallas.append(Falla(clase, que, esperado, real))

    def de(self, clase: str) -> list[Falla]:
        return [f for f in self.fallas if f.clase == clase]


# --- La foto ---------------------------------------------------------------------------------

def foto(conn, mundo: Mundo) -> dict[str, Any]:
    """Lo que hay en la base del espacio, con las tareas por su clave y las personas por su
    nombre corto. Sólo lee (como `admin`, para ver también el registro de auditoría)."""
    clave = {v: k for k, v in mundo.tareas.items()}

    def tarea(task_id) -> str | None:
        return clave.get(str(task_id)) if task_id is not None else None

    def persona(membership_id) -> str | None:
        return mundo.persona_de_membresia(membership_id) if membership_id else None

    ws = mundo.workspace_id
    with admin(conn) as cur:
        cur.execute("select id, estado::text e from task where workspace_id = %s", (ws,))
        estados = {tarea(f["id"]): f["e"] for f in cur.fetchall()}
        cur.execute("""select f.id, f.task_id, f.fecha_prevista, f.motivo, f.es_correccion
                         from task_forecast f join task t on t.id = f.task_id
                        where t.workspace_id = %s""", (ws,))
        previsiones = {str(f["id"]): {"tarea": tarea(f["task_id"]),
                                      "fecha": f["fecha_prevista"].isoformat(),
                                      "motivo": f["motivo"], "es_correccion": f["es_correccion"]}
                       for f in cur.fetchall()}
        cur.execute("""select id, task_id, causa, resuelto_en from blocker
                        where workspace_id = %s""", (ws,))
        bloqueos = {str(f["id"]): {"tarea": tarea(f["task_id"]), "causa": f["causa"],
                                   "resuelto": f["resuelto_en"] is not None}
                    for f in cur.fetchall()}
        cur.execute("""select u.id, b.task_id, u.destraba_membership_id, u.destraba_externo,
                              u.no_sabe, u.dicho_por_membership_id
                         from blocker_unblocker u join blocker b on b.id = u.blocker_id
                        where u.workspace_id = %s""", (ws,))
        destraban = {}
        for f in cur.fetchall():
            quien = persona(f["destraba_membership_id"])
            destraban[str(f["id"])] = {
                "tarea": tarea(f["task_id"]), "no_sabe": f["no_sabe"],
                "integrante": quien, "externo": f["destraba_externo"],
                # Otra persona que lo destraba: alguien de afuera o un integrante que no es
                # quien lo dijo (nombrarse a sí misma es "le toca a ella").
                "alguien": bool(f["destraba_externo"]) or (
                    f["destraba_membership_id"] is not None
                    and f["destraba_membership_id"] != f["dicho_por_membership_id"])}
        cur.execute("""select * from scheduled_notice where workspace_id = %s""", (ws,))
        avisos = {str(f["id"]): {"tipo": f["tipo"], "tarea": tarea(f["task_id"]),
                                 "a": persona(f["destinatario_membership_id"]),
                                 "estado": f["estado"], "motivo": f["motivo_omision"],
                                 "hechos": f["hechos"], "clave": f["dedupe_key"],
                                 "outbox_id": str(f["outbox_id"]) if f["outbox_id"] else None}
                  for f in cur.fetchall()}
        cur.execute("""select id, destinatario_membership_id, es_respuesta, tipo, cuerpo, estado,
                              dedupe_key
                         from message_outbox where workspace_id = %s""", (ws,))
        salidas = {str(f["id"]): {"a": persona(f["destinatario_membership_id"]),
                                  "es_respuesta": f["es_respuesta"], "tipo": f["tipo"],
                                  "cuerpo": f["cuerpo"], "estado": f["estado"]}
                   for f in cur.fetchall()}
        cur.execute("select id, etapa, severidad from incident where workspace_id = %s", (ws,))
        incidentes = {str(f["id"]): {"etapa": f["etapa"], "severidad": f["severidad"]}
                      for f in cur.fetchall()}
        # Los del espacio de la corrida, no los de toda la base (revisión de la E2-7).
        cur.execute("select count(*) n from admin_notice where workspace_id = %s", (ws,))
        avisos_admin = cur.fetchone()["n"]
        cur.execute("""select id, sujeto_id from audit_log
                        where workspace_id = %s and accion = 'informar_avance'""", (ws,))
        avances = {str(f["id"]): {"tarea": tarea(f["sujeto_id"])} for f in cur.fetchall()}
        cur.execute("""select id, task_id, satisfecho_en, escalado_en from pending_reply
                        where workspace_id = %s""", (ws,))
        esperas = {str(f["id"]): {"tarea": tarea(f["task_id"]),
                                  "abierta": f["satisfecho_en"] is None}
                   for f in cur.fetchall()}
        cur.execute("""select q.membership_id, q.tipo, q.task_id, q.para_despues_en,
                              (s.pregunta_abierta_id = q.id) as abierta
                         from conversation_question q
                         left join conversation_state s on s.membership_id = q.membership_id
                        where q.workspace_id = %s and q.cerrada_en is null
                        order by q.abierta_en""", (ws,))
        preguntas: dict[str, dict[str, Any]] = {}
        for f in cur.fetchall():
            de = preguntas.setdefault(persona(f["membership_id"]),
                                      {"abierta": None, "para_despues": []})
            dicha = {"tipo": f["tipo"], "tarea": tarea(f["task_id"])}
            if f["abierta"]:
                de["abierta"] = dicha
            elif f["para_despues_en"] is not None:
                de["para_despues"].append(dicha)
        # El último aviso es un envío: su tarea, o sus tareas si juntó varias (mecánica §10).
        cur.execute("""select s.membership_id,
                              array(select b.task_id from scheduled_notice b
                                     where b.outbox_id = a.outbox_id
                                       and b.task_id is not null) as tareas
                         from conversation_state s
                         join scheduled_notice a on a.id = s.ultimo_aviso_id
                        where s.workspace_id = %s""", (ws,))
        ultimo_aviso = {}
        for f in cur.fetchall():
            de_las = sorted({tarea(t) for t in f["tareas"] or []} - {None})
            ultimo_aviso[persona(f["membership_id"])] = (
                de_las[0] if len(de_las) == 1 else de_las or None)
    conn.commit()
    return {"estados": estados, "previsiones": previsiones, "bloqueos": bloqueos,
            "destraban": destraban, "avisos": avisos, "salidas": salidas,
            "incidentes": incidentes, "avisos_admin": avisos_admin, "avances": avances,
            "esperas": esperas, "preguntas": preguntas, "ultimo_aviso": ultimo_aviso}


def efectos(antes: dict[str, Any], despues: dict[str, Any]) -> dict[str, Any]:
    """Lo nuevo de un paso: lo que cambió en las tareas y las filas que aparecieron."""
    def nuevas(tabla: str) -> list[dict[str, Any]]:
        return [v for k, v in despues[tabla].items() if k not in antes[tabla]]

    return {
        "estados": {k: v for k, v in despues["estados"].items()
                    if antes["estados"].get(k) != v},
        "previsiones": nuevas("previsiones"),
        "bloqueos": nuevas("bloqueos"),
        "bloqueos_resueltos": [v["tarea"] for k, v in despues["bloqueos"].items()
                               if v["resuelto"] and not antes["bloqueos"].get(k, {}).get(
                                   "resuelto", False)],
        "destraban": nuevas("destraban"),
        "avisos_guardados": [v for k, v in despues["avisos"].items() if k not in antes["avisos"]],
        "salidas": nuevas("salidas"),
        "incidentes": nuevas("incidentes"),
        "avisos_al_administrador": despues["avisos_admin"] - antes["avisos_admin"],
        "avances": nuevas("avances"),
    }


# --- Traducir a claves --------------------------------------------------------------------------

def normalizar(valor: Any, titulos: dict[str, str]) -> Any:
    """Las tareas de unos hechos, por su clave: un título, o un `{alias, titulo}`, pasa a ser la
    clave de la tarea; un dict que además trae otros datos conserva esos datos con `titulo`
    traducido."""
    por_titulo = {t: k for k, t in titulos.items()}
    if isinstance(valor, str):
        return por_titulo.get(valor, valor)
    if isinstance(valor, list):
        return [normalizar(v, titulos) for v in valor]
    if isinstance(valor, dict):
        if set(valor) <= {"alias", "titulo"} and valor.get("titulo") in por_titulo:
            return por_titulo[valor["titulo"]]
        return {k: normalizar(v, titulos) for k, v in valor.items() if k != "alias"}
    return valor


# --- Comparar ---------------------------------------------------------------------------------

def coincide(esperado: Any, real: Any) -> bool:
    """Si lo real cumple lo esperado (ver el módulo: `presente`, `ausente`, `~prefijo`,
    subconjunto de un dict, lista elemento por elemento)."""
    if esperado == "presente":
        return real not in (None, "", [], {})
    if esperado == "ausente":
        return real in (None, "", [], {}, False)
    if isinstance(esperado, str) and esperado.startswith("~"):
        return isinstance(real, str) and real.startswith(esperado[1:])
    if isinstance(esperado, dict):
        if not isinstance(real, dict):
            return False
        return all(coincide(v, real.get(k)) for k, v in esperado.items())
    if isinstance(esperado, list):
        return isinstance(real, list) and len(esperado) == len(real) and all(
            coincide(e, r) for e, r in zip(esperado, real))
    if isinstance(esperado, (int, float)) and isinstance(real, (int, float)) \
            and not isinstance(esperado, bool):
        return esperado == real
    return esperado == real or (str(esperado) == str(real) and esperado is not None
                                and not isinstance(esperado, bool))


def jugada_coincide(esperada: dict[str, Any], real: dict[str, Any]) -> bool:
    """Una jugada elegida contra la esperada: el nombre (`fuera_de_la_lista` es cualquiera que
    no esté en la lista), los datos estructurados iguales, y los libres presentes si y sólo si
    se esperan (salvo los de `puede_traer`)."""
    from .fichas import FICHAS

    nombre = esperada["nombre"]
    if nombre == FUERA_DE_LA_LISTA:
        return real["nombre"] not in FICHAS
    if real["nombre"] != nombre:
        return False
    libres = set(esperada.get("puede_traer") or ())
    datos_e = {k: v for k, v in esperada.items() if k not in ("nombre", "puede_traer")}
    datos_r = {k: v for k, v in real.items() if k != "nombre"}
    for k in set(datos_e) | set(datos_r):
        if k in libres:
            continue
        e, r = datos_e.get(k), datos_r.get(k)
        if k in DATOS_LIBRES:
            if (e is not None) != (r not in (None, "")):
                return False
        elif e is None:
            if r not in (None, False, ""):
                return False
        elif not coincide(e, r):
            return False
    return True


def comprobar_jugadas(c: Comprobacion, esperadas: list[dict], reales: list[dict]) -> bool:
    ok = len(esperadas) == len(reales) and all(
        jugada_coincide(e, r) for e, r in zip(esperadas, reales))
    if not ok:
        c.falla(COMPRENSION, "jugadas", esperadas, reales)
    return ok


def _cuenta(lista: list) -> dict[str, int]:
    out: dict[str, int] = {}
    for x in lista:
        out[repr(x)] = out.get(repr(x), 0) + 1
    return out


def _emparejar(esperados: list[dict], reales: list[dict]) -> tuple[list[dict], list[dict]]:
    """(los esperados sin uno real que los cumpla, los reales que sobran), con el mayor número
    de pares posible: un esperado general no se queda con el real que otro más preciso necesita
    (revisión de la E2-7; caminos de aumento, las listas de un paso son cortas)."""
    puede = [[j for j, r in enumerate(reales) if coincide(e, r)] for e in esperados]
    de_real: dict[int, int] = {}            # real → el esperado con que quedó emparejado

    def emparejar(i: int, vistos: set[int]) -> bool:
        for j in puede[i]:
            if j in vistos:
                continue
            vistos.add(j)
            if j not in de_real or emparejar(de_real[j], vistos):
                de_real[j] = i
                return True
        return False

    for i in range(len(esperados)):
        emparejar(i, set())
    con_par = set(de_real.values())
    return ([e for i, e in enumerate(esperados) if i not in con_par],
            [r for j, r in enumerate(reales) if j not in de_real])


def comprobar_efectos(c: Comprobacion, esperados: dict[str, Any], hubo: dict[str, Any],
                      titulos: dict[str, str]) -> tuple[bool, bool]:
    """Los efectos del turno contra los esperados. Devuelve (hubo uno de más, faltó uno). Lo que
    no se nombra en lo esperado se espera vacío. Los avisos que el turno retiró sin salir no son
    efectos (no pasó nada): se miran en el estado (`estado_avisos`)."""
    de_mas = falta = False
    esperados = esperados or {}
    estados_e = esperados.get("estados") or {}
    if estados_e != hubo["estados"]:
        extra = {k: v for k, v in hubo["estados"].items() if estados_e.get(k) != v}
        if extra:
            de_mas = True
            c.falla(GARANTIA, "efecto de más: estado", estados_e, hubo["estados"])
        if any(hubo["estados"].get(k) != v for k, v in estados_e.items()):
            falta = True
            if not extra:
                c.falla(COMPRENSION, "falta un efecto: estado", estados_e, hubo["estados"])

    def filas(nombre: str, reales: list[dict], que: str) -> None:
        nonlocal de_mas, falta
        esperadas = esperados.get(nombre) or []
        reales = [normalizar(r, titulos) for r in reales]
        faltan, sobran = _emparejar(esperadas, reales)
        if sobran:
            de_mas = True
            c.falla(GARANTIA, f"efecto de más: {que}", esperadas, sobran)
        if faltan:
            falta = True
            if not sobran:
                c.falla(COMPRENSION, f"falta un efecto: {que}", faltan, reales)

    filas("previsiones", hubo["previsiones"], "previsión")
    filas("bloqueos", hubo["bloqueos"], "bloqueo")
    filas("destraban", hubo["destraban"], "quién destraba")
    filas("avances", hubo["avances"], "avance")
    filas("avisos_guardados", [a for a in hubo["avisos_guardados"]], "aviso guardado")
    # Como las demás filas: uno de más es de garantía; uno que falta, de comprensión (revisión
    # de la E2-7: antes, los dos eran de garantía).
    filas("bloqueos_resueltos", hubo["bloqueos_resueltos"], "bloqueo resuelto")
    al_admin_e = esperados.get("avisos_al_administrador", 0)
    fuera = [i for i in hubo["incidentes"] if i["etapa"] == ETAPA_FUERA_DE_LA_LISTA]
    if len(fuera) != al_admin_e:
        if len(fuera) > al_admin_e:
            de_mas = True
            c.falla(GARANTIA, "aviso al administrador de más", al_admin_e, len(fuera))
        else:
            falta = True
            c.falla(COMPRENSION, "falta el aviso al administrador", al_admin_e, len(fuera))
    otros = [i for i in hubo["incidentes"] if i["etapa"] != ETAPA_FUERA_DE_LA_LISTA]
    if otros:
        c.falla(MOTOR, "incidente", [], otros)
    a_otros = [s for s in hubo["salidas"] if not s["es_respuesta"]]
    if a_otros:
        de_mas = True
        c.falla(GARANTIA, "mensaje de Leda por su cuenta en un turno", [], a_otros)
    return de_mas, falta


def comprobar_estado(c: Comprobacion, esperado: dict[str, Any], f: dict[str, Any],
                     persona: str, clase: str = MOTOR) -> None:
    """El estado después del paso, sólo lo que el paso nombra: la pregunta abierta y las de
    después de la persona, las esperas abiertas y el último aviso de cada una."""
    if not esperado:
        return
    preguntas = f["preguntas"].get(persona, {"abierta": None, "para_despues": []})
    if "pregunta_abierta" in esperado:
        e, r = esperado["pregunta_abierta"], preguntas["abierta"]
        if (e is None) != (r is None) or (e is not None and not coincide(e, r)):
            c.falla(clase, "pregunta abierta después", e, r)
    if "para_despues" in esperado:
        if not coincide(esperado["para_despues"], preguntas["para_despues"]):
            c.falla(clase, "preguntas para después", esperado["para_despues"],
                    preguntas["para_despues"])
    if "esperas_abiertas" in esperado:
        reales = sorted({e["tarea"] for e in f["esperas"].values() if e["abierta"]})
        if sorted(esperado["esperas_abiertas"]) != reales:
            c.falla(clase, "esperas abiertas después", sorted(esperado["esperas_abiertas"]),
                    reales)
    for quien, tarea in (esperado.get("ultimo_aviso") or {}).items():
        if f["ultimo_aviso"].get(quien) != tarea:
            c.falla(clase, f"último aviso de {quien}", tarea, f["ultimo_aviso"].get(quien))


def comprobar_avisos_en_estado(c: Comprobacion, esperados: list[dict], f: dict[str, Any],
                               titulos: dict[str, str]) -> None:
    """Avisos que tienen que existir así después del paso (por ejemplo, uno omitido con su
    motivo: nunca en silencio)."""
    reales = [normalizar({k: v for k, v in a.items() if k != "clave"}, titulos)
              for a in f["avisos"].values()]
    for e in esperados or []:
        if not any(coincide(e, r) for r in reales):
            c.falla(MOTOR, "aviso en el estado", e,
                    [r for r in reales if r.get("tarea") == e.get("tarea")])


def dia(momento) -> str:
    return momento.astimezone(ZONA).date().isoformat()
