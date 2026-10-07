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
  hechos, la pregunta, el estado después, lo que Leda manda por su cuenta);
- `formato`: un mensaje de Leda que no tiene la forma que pidió el usuario (segunda vuelta del
  formato, 2026-10-07; `fallas_de_formato`). Es aparte de las otras tres: dice cómo se lee un
  mensaje, no qué hizo el código ni si la IA entendió.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from leda.db import admin
from leda.motor.avisos import ETAPA_AVISO_REINTENTO

from .carga import ZONA, Mundo
from .motores import Motor
from .motores import cargar as cargar_motor

GARANTIA, COMPRENSION, MOTOR, FORMATO = "garantia", "comprension", "motor", "formato"

# Los datos de una jugada que son palabras de la persona: se compara sólo si están. Con
# `puede_traer`, pueden venir, pero sólo con las palabras de la persona (revisión del contrato,
# 2026-10-05): uno inventado sigue siendo una falla.
DATOS_LIBRES = frozenset({"motivo", "causa", "palabras", "quien", "a", "que_pide"})
FUERA_DE_LA_LISTA = "fuera_de_la_lista"
ETAPA_FUERA_DE_LA_LISTA = "motor_fuera_de_la_lista"
# Un aviso cuya redacción falló y se reintenta (usuario, 2026-10-07): en la corrida es un aviso
# que no salió a su hora. El informe se publica: de la falla dice sólo su clase y su código
# HTTP, nunca su texto (`falla_sin_texto`).
AVISO_SIN_REDACTAR = "el aviso no salió a su hora: la IA no lo redactó"
_CLASE = re.compile(r"[A-Za-z_][A-Za-z0-9_.]*")
_HTTP = re.compile(r"\bHTTP (\d{3})\b|'(\d{3}) [A-Z]")


@dataclass
class Falla:
    clase: str              # garantia | comprension | motor | formato
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
                # quien lo dijo (nombrarse a sí misma es "le toca a la persona que escribe").
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
        cur.execute("""select id, etapa, severidad, referencia_cruda from incident
                        where workspace_id = %s""", (ws,))
        incidentes = {str(f["id"]): {"etapa": f["etapa"], "severidad": f["severidad"]}
                      | ({"falla": falla_sin_texto(f["referencia_cruda"])}
                         if f["etapa"] == ETAPA_AVISO_REINTENTO else {})
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


def falla_sin_texto(referencia: str | None) -> dict[str, Any]:
    """De la referencia técnica de un incidente (`Clase: texto`), lo que puede ir a un informe
    publicado: la clase de la excepción y, si la tiene, el código HTTP. Nunca el texto."""
    antes = (referencia or "").split(":", 1)[0].strip()
    falla: dict[str, Any] = {"falla": antes if _CLASE.fullmatch(antes) else "desconocida"}
    codigo = _HTTP.search(referencia or "")
    if codigo:
        falla["http"] = int(codigo.group(1) or codigo.group(2))
    return falla


def comprobar_incidentes(c: Comprobacion, incidentes: list[dict[str, Any]]) -> None:
    """Los incidentes nuevos de un paso, salvo los de un pedido fuera de la lista (que se
    comparan con los avisos al administrador esperados). Un intento de redactar un aviso que
    falló se dice como lo que es, con su falla sin texto; cualquier otro, como incidente."""
    for i in incidentes:
        if i["etapa"] == ETAPA_AVISO_REINTENTO:
            c.falla(MOTOR, AVISO_SIN_REDACTAR, None, i["falla"])
    otros = [i for i in incidentes
             if i["etapa"] not in (ETAPA_FUERA_DE_LA_LISTA, ETAPA_AVISO_REINTENTO)]
    if otros:
        c.falla(MOTOR, "incidente", [], otros)


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


def jugada_coincide(esperada: dict[str, Any], real: dict[str, Any],
                    mensaje: str | None = None, *, motor: Motor | None = None) -> bool:
    """Una jugada elegida contra la esperada: el nombre (`fuera_de_la_lista` es cualquiera que
    no esté en la lista del `motor`), los datos estructurados iguales, y los libres presentes si
    y sólo si se esperan (salvo los de `puede_traer`, que pueden venir si son palabras de la
    persona: todas las del dato están en su `mensaje`, sin importar mayúsculas ni acentos)."""
    motor = motor or cargar_motor()
    FICHAS, palabras = motor.FICHAS, motor.palabras     # noqa: N806 -- los nombres del motor

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
            r = datos_r.get(k)
            if (mensaje is not None and k in DATOS_LIBRES and isinstance(r, str)
                    and not set(palabras(r)) <= set(palabras(mensaje))):
                return False
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


def comprobar_jugadas(c: Comprobacion, esperadas: list[dict], reales: list[dict],
                      mensaje: str | None = None, *, motor: Motor | None = None) -> bool:
    ok = len(esperadas) == len(reales) and all(
        jugada_coincide(e, r, mensaje, motor=motor) for e, r in zip(esperadas, reales))
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
    comprobar_incidentes(c, hubo["incidentes"])
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


# --- El formato de los mensajes (segunda vuelta, usuario, 2026-10-07) ------------------------
#
# Lo que pidió el usuario después de verlo en Telegram (`odd/tasks/motor-definitivo.md`, "El
# formato, segunda vuelta"): sin negrita; un renglón por idea; cada tarea en su renglón, con 📋
# (su nombre solo) o con 📅 (con su vencimiento, en una lista); el nombre completo de una tarea,
# una sola vez por mensaje; fechas cortas; y el cierre (la pregunta, o que no hace falta
# responder) solo en su renglón, aparte y al final. Se mide solo, en cada mensaje de una corrida,
# para no depender de leer las transcripciones. Se comprueba sobre el texto que escribió la IA,
# sin el saludo del día que agrega el sistema. Lo que no se puede medir sin juzgar el texto (que
# el primer renglón diga lo que pasó, que una idea no se parta) lo sigue leyendo una persona.
#
# El tope del renglón: 140 caracteres son tres o cuatro renglones en la pantalla de un teléfono,
# lo que ocupa una idea con el nombre completo de una tarea y su fecha; los párrafos de la
# primera vuelta pasaban de 200.
RENGLON_MAXIMO = 140
MARCAS_DE_TAREA = ("📋", "📅")
MARCA_DE_LA_TAREA_SOLA = "📋"

SIN_NEGRITA = "sin negrita (**)"
TAREA_EN_SU_RENGLON = "el nombre completo de una tarea, en un renglón que empieza con 📋 o 📅"
TAREA_SOLA = "un renglón con 📋 lleva sólo el nombre de la tarea"
TAREA_UNA_VEZ = "el nombre completo de una tarea, una sola vez por mensaje"
RENGLON_CORTO = f"ningún renglón de más de {RENGLON_MAXIMO} caracteres"
FECHA_CORTA = "las fechas, cortas: nunca el día con el nombre del mes"
PREGUNTA_AL_FINAL = "la pregunta, una sola y en el último renglón"
NO_HACE_FALTA_AL_FINAL = "que no hace falta responder, en el último renglón"
CIERRE_APARTE = "el cierre, solo en su renglón y con un renglón en blanco antes"

_MESES = ("enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|"
          "noviembre|diciembre")
_FECHA_LARGA = re.compile(rf"\b\d{{1,2}} de ({_MESES})\b", re.IGNORECASE)
# Que no hace falta contestar, dicho de las formas en que se dice. Es una medida del corredor
# sobre el texto, no algo que Leda tenga que decir así.
_NO_HACE_FALTA = re.compile(r"\b(no hace falta|no hay que|no necesit\w*|sin necesidad de)\b"
                            r"[^.?!\n]*\b(respond|contest)", re.IGNORECASE)
_ORACION = re.compile(r"(?<=[.!?…])\s+(?=\S)")


def _es_pregunta(renglon: str) -> bool:
    return "?" in renglon or "¿" in renglon


def _solo_el_titulo(renglon: str, titulo: str) -> bool:
    """Si un renglón con 📋 lleva sólo ese título (sin contar la marca ni la puntuación)."""
    resto = renglon.strip()[len(MARCA_DE_LA_TAREA_SOLA):].lstrip("️ ").rstrip(" .:")
    return resto.casefold() == titulo.casefold()


def fallas_de_formato(texto: str, titulos: Iterable[str]) -> list[tuple[str, str]]:
    """Las reglas del formato que un mensaje de Leda no cumple, cada una una sola vez y con el
    primer renglón que la rompe (o el título, si es una tarea nombrada dos veces). `titulos`
    son los de las tareas de la conversación."""
    fallas: dict[str, str] = {}
    renglones = texto.split("\n")
    for renglon in renglones:
        if "**" in renglon:
            fallas.setdefault(SIN_NEGRITA, renglon)
        if len(renglon.strip()) > RENGLON_MAXIMO:
            fallas.setdefault(RENGLON_CORTO, renglon)
        if _FECHA_LARGA.search(renglon):
            fallas.setdefault(FECHA_CORTA, renglon)
    # Las tareas, de la más larga a la más corta: un título que está dentro de otro no se cuenta
    # en el renglón del otro.
    tapados = [r.casefold() for r in renglones]
    for titulo in sorted({t for t in titulos if t}, key=len, reverse=True):
        buscado, veces = titulo.casefold(), 0
        for i, renglon in enumerate(tapados):
            if buscado not in renglon:
                continue
            veces += renglon.count(buscado)
            tapados[i] = renglon.replace(buscado, "\0" * len(buscado))
            if not renglones[i].strip().startswith(MARCAS_DE_TAREA):
                fallas.setdefault(TAREA_EN_SU_RENGLON, renglones[i])
            elif (renglones[i].strip().startswith(MARCA_DE_LA_TAREA_SOLA)
                  and not _solo_el_titulo(renglones[i], titulo)):
                fallas.setdefault(TAREA_SOLA, renglones[i])
        if veces > 1:
            fallas.setdefault(TAREA_UNA_VEZ, titulo)
    # El cierre: la pregunta o que no hace falta responder, en el último renglón, solo y aparte.
    llenos = [i for i, r in enumerate(renglones) if r.strip()]
    if llenos:
        ultimo = llenos[-1]
        antes = [i for i in llenos if _es_pregunta(renglones[i]) and i != ultimo]
        if antes:
            fallas.setdefault(PREGUNTA_AL_FINAL, renglones[antes[0]])
        antes = [i for i in llenos if _NO_HACE_FALTA.search(renglones[i]) and i != ultimo]
        if antes:
            fallas.setdefault(NO_HACE_FALTA_AL_FINAL, renglones[antes[0]])
        cierre = renglones[ultimo]
        if _es_pregunta(cierre) or _NO_HACE_FALTA.search(cierre):
            solo = len(_ORACION.split(cierre.strip())) == 1
            aparte = len(llenos) == 1 or not renglones[ultimo - 1].strip()
            if not (solo and aparte):
                fallas.setdefault(CIERRE_APARTE, cierre)
    return list(fallas.items())


def comprobar_formato(c: Comprobacion, texto: str, titulos: Iterable[str], *,
                      a: str | None) -> None:
    """El formato de un mensaje de Leda a `a`: una falla de `formato` por regla que no cumple,
    con la regla como lo esperado y el renglón como lo real."""
    for regla, renglon in fallas_de_formato(texto, titulos):
        c.falla(FORMATO, f"formato del mensaje a {a}", regla, renglon)


def dia(momento) -> str:
    return momento.astimezone(ZONA).date().isoformat()
