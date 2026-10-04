"""Banco de latencia, tokens de salida y costo por modelo (tarea 0-24, flujo C6).

Escrito para el código de la rama de flujo en `3243b2c` (worktree `flujo-c6`); el
contrato de las llamadas cambió después (0-31 a 0-34: `pregunta_por`, `se_pide`,
`se_ofrece`, `mantiene`), así que hay que adaptarlo antes de medir la versión
actual. Los resultados se escriben en `tools/_mediciones/` (no versionado).

Uso (cwd = el worktree, para que cargue su configuración; este script nunca lee
ni imprime nada del `.env`):

    cd D:/Proyectos/Leda-PM-worktrees/flujo-c6
    PYTHONPATH=src D:/Proyectos/Leda-PM/.venv/Scripts/python.exe \
        D:/Proyectos/Leda-PM/tools/medir_modelos.py --salida corrida [--n 3]
        [--escenarios s1,s3] [--modelos flash,luna,sol,gemini] [--topes base,alto]
    ... --salida corrida --recalcular      # sólo rehace el resumen desde el JSON

Un mensaje recorre el camino de producción del flujo C6, sin base:
- ruteo (`route_intent`, hasta 2 intentos como `gateway._rutear`) si el mensaje
  llega sin borrador en curso; con borrador en curso (s4) no hay ruteo
  (`gateway`: el alta conducida no pasa por el ruteo).
- si es un alta: `interpretar_alta` (hasta 2 intentos, `leer_interpretacion`,
  `aplicar_valores`), el código decide (`ResultadoTurno`) y `conducir_alta` en
  stream (hasta 2 intentos, `leer_redaccion`, `verificar_redaccion`).
Las instrucciones de la redacción (tono de CoreWork) se leen UNA vez de
`leda_flujo` en una transacción de sólo lectura que se descarta.

Cada llamada lleva un `user` único (el gateway cachea pedidos idénticos) y, en
OpenRouter, `usage: {include: true}` para leer `usage.cost`.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import threading
import time
import uuid
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent / "_mediciones"
AQUI.mkdir(exist_ok=True)

ap = argparse.ArgumentParser()
ap.add_argument("--salida", required=True)
ap.add_argument("--n", type=int, default=3)
ap.add_argument("--escenarios", default=None)
ap.add_argument("--modelos", default="flash,luna,sol,gemini")
ap.add_argument("--topes", default="base,alto")
ap.add_argument("--recalcular", action="store_true")
ARGS = ap.parse_args()

PRECIOS = json.loads((AQUI / "precios_openrouter.json").read_text(encoding="utf-8"))

MODELOS = {
    "flash": ("nan", "deepseek-v4-flash"),
    "luna": ("openrouter", "openai/gpt-6-luna"),
    "sol": ("openrouter", "openai/gpt-6-sol"),
    "gemini": ("openrouter", "google/gemini-3.8-flash"),
}
# Precio de referencia para nan (no publica precios): el de OpenRouter del mismo modelo.
REFERENCIA_PRECIO = {"flash": "deepseek/deepseek-v4-flash"}
TOPES = {"base": {}, "alto": {"tope_conduccion": 4000, "tope_ruteo": 3000}}


# ---------------------------------------------------------------------------
# Resumen (no necesita leda)
# ---------------------------------------------------------------------------

def pct(xs, p):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    k = (len(xs) - 1) * p
    i = int(k)
    j = min(i + 1, len(xs) - 1)
    return round(xs[i] + (xs[j] - xs[i]) * (k - i), 2)


def costo_de(llamada, modelo_clave):
    u = llamada.get("usage") or {}
    if u.get("cost") is not None:
        return float(u["cost"]), "openrouter"
    ref = REFERENCIA_PRECIO.get(modelo_clave)
    if ref and u:
        p = PRECIOS[ref]
        return (u.get("prompt_tokens", 0) * float(p["prompt"])
                + u.get("completion_tokens", 0) * float(p["completion"])), "estimado"
    return None, None


def resumir(mensajes):
    grupos = {}
    for m in mensajes:
        grupos.setdefault((m["modelo"], m["tope"]), []).append(m)
    filas = {}
    for (modelo, tope), ms in sorted(grupos.items()):
        llamadas = [ll for m in ms for ll in m["llamadas"]]
        por_tipo = {}
        for tipo in ("ruteo", "interpreta", "redacta"):
            ls = [ll for ll in llamadas if ll["tipo"] == tipo]
            if not ls:
                continue
            por_tipo[tipo] = {
                "llamadas": len(ls),
                "lat_p50": pct([ll["s"] for ll in ls], .5),
                "lat_p90": pct([ll["s"] for ll in ls], .9),
                "tok_salida_p50": pct([(ll.get("usage") or {}).get("completion_tokens")
                                       for ll in ls], .5),
                "razonamiento_p50": pct([ll.get("razonamiento") for ll in ls], .5),
                "primer_texto_p50": pct([ll.get("primer_texto_s") for ll in ls], .5),
                "length": sum(1 for ll in ls if ll.get("finish") == "length"),
                "error": sum(1 for ll in ls if ll["resultado"] == "error"),
                "rechazada": sum(1 for ll in ls if ll["resultado"] == "rechazada"),
                "motivos": sorted({ll.get("motivo", "")[:90] for ll in ls
                                   if ll["resultado"] != "aceptada"} - {""}),
            }
        altas = [m for m in ms if m["alta"]]
        costos, fuente = [], None
        for m in ms:
            c = 0.0
            for ll in m["llamadas"]:
                v, f = costo_de(ll, modelo)
                if v is not None:
                    c += v
                    fuente = f
            m["usd"] = c
        costos_alta = [m["usd"] for m in altas]
        filas[f"{modelo}|{tope}"] = {
            "modelo": modelo, "tope": tope, "mensajes": len(ms),
            "llamadas": len(llamadas),
            "msg_p50": pct([m["total_s"] for m in altas], .5),
            "msg_p90": pct([m["total_s"] for m in altas], .9),
            "aviso_neutro": sum(1 for m in altas if m["fallo"]),
            "mal_ruteo": sum(1 for m in ms if m.get("ruteo_ok") is False),
            "ruteo_caido": sum(1 for m in ms if m.get("ruteo_caido")),
            "usd_msg_media": round(statistics.mean(costos_alta), 6) if costos_alta else None,
            "usd_msg_p50": pct(costos_alta, .5) if costos_alta else None,
            "usd_total": round(sum(m["usd"] for m in ms), 5),
            "fuente_costo": fuente,
            "por_tipo": por_tipo,
        }
    return filas


def markdown(filas, meta):
    def f(x, n=1):
        return "-" if x is None else (f"{x:.{n}f}" if isinstance(x, float) else str(x))
    lin = [f"# Banco 0-24 (flujo C6) — {meta['fecha']}", "",
           f"Escenarios {meta['escenarios']}, n={meta['n']}. Mensaje = ruteo (si no hay "
           "borrador en curso) + interpreta + redacta, con los reintentos de producción; "
           "latencias en segundos; tokens de salida incluyen razonamiento.", "",
           "| modelo | tope | msg p50 | msg p90 | redacta p50 | 1er texto p50 | tok sal. p50 (rut/int/red) | fallas (len/err/rech) | aviso neutro | mal ruteo | USD/msg |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, r in filas.items():
        pt = r["por_tipo"]
        tok = "/".join(f(pt.get(t, {}).get("tok_salida_p50"), 0)
                       for t in ("ruteo", "interpreta", "redacta"))
        ln = sum(v["length"] for v in pt.values())
        er = sum(v["error"] for v in pt.values())
        re_ = sum(v["rechazada"] for v in pt.values())
        usd = r["usd_msg_media"]
        usd_s = "-" if usd is None else f"{usd:.5f}" + (" (est.)" if r["fuente_costo"] == "estimado" else "")
        lin.append(f"| {r['modelo']} | {r['tope']} | {f(r['msg_p50'])} | {f(r['msg_p90'])} | "
                   f"{f(pt.get('redacta', {}).get('lat_p50'))} | "
                   f"{f(pt.get('redacta', {}).get('primer_texto_p50'))} | {tok} | "
                   f"{ln}/{er}/{re_} | {r['aviso_neutro']} | {r['mal_ruteo']} | {usd_s} |")
    lin += ["", "## Por tipo de llamada", "",
            "| modelo | tope | tipo | n | p50 | p90 | tok p50 | razon. p50 | len | err | rech |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, r in filas.items():
        for t, v in r["por_tipo"].items():
            lin.append(f"| {r['modelo']} | {r['tope']} | {t} | {v['llamadas']} | {f(v['lat_p50'])} | "
                       f"{f(v['lat_p90'])} | {f(v['tok_salida_p50'], 0)} | {f(v['razonamiento_p50'], 0)} | "
                       f"{v['length']} | {v['error']} | {v['rechazada']} |")
    lin += ["", "## Motivos de falla", ""]
    for k, r in filas.items():
        for t, v in r["por_tipo"].items():
            if v["motivos"]:
                lin.append(f"- {k} {t}: " + " · ".join(v["motivos"]))
    return "\n".join(lin) + "\n"


def escribir(mensajes, meta):
    filas = resumir(mensajes)
    (AQUI / f"{ARGS.salida}.json").write_text(
        json.dumps({"meta": meta, "resumen": filas, "mensajes": mensajes},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    (AQUI / f"{ARGS.salida}.md").write_text(markdown(filas, meta), encoding="utf-8")
    return filas


if ARGS.recalcular:
    datos = json.loads((AQUI / f"{ARGS.salida}.json").read_text(encoding="utf-8"))
    escribir(datos["mensajes"], datos["meta"])
    print((AQUI / f"{ARGS.salida}.md").read_text(encoding="utf-8"))
    sys.exit(0)

# ---------------------------------------------------------------------------
# leda
# ---------------------------------------------------------------------------

from leda import alta_turno as T  # noqa: E402
from leda import db, llm, redaccion  # noqa: E402
from leda import instrucciones as INS  # noqa: E402
from leda.config import config  # noqa: E402

print("leda desde:", Path(T.__file__).resolve().parent)


def instrucciones_reales():
    conn = db.conectar()
    try:
        conn.commit()
        conn.read_only = True
        with conn.cursor() as cur:
            cur.execute("select current_database() as d")
            if cur.fetchone()["d"] != "leda_flujo":
                sys.exit("La base configurada no es leda_flujo; no sigo.")
            cur.execute("set role leda_admin")
            cur.execute("select id from workspace where slug = 'corework'")
            ws = str(cur.fetchone()["id"])
            cur.execute("reset role")
        with db.espacio(conn, ws) as cur:
            return INS.instrucciones_alta_del_espacio(cur, ws)
    finally:
        conn.rollback()
        conn.close()


def _dump(u):
    if u is None:
        return None
    try:
        return u.model_dump(exclude_none=True)
    except Exception:  # noqa: BLE001
        return dict(u) if isinstance(u, dict) else None


class Medidor:
    """Envuelve el cliente OpenAI: `user` único, `usage` (con costo en
    OpenRouter) y `finish_reason` de cada llamada (con o sin stream)."""

    def __init__(self, cliente, openrouter: bool):
        self._c = cliente
        self._or = openrouter
        self.ultimo = None
        self.chat = self
        self.completions = self

    def create(self, **kw):
        kw.setdefault("user", "medicion-" + uuid.uuid4().hex[:12])
        if self._or:
            extra = dict(kw.get("extra_body") or {})
            extra["usage"] = {"include": True}
            kw["extra_body"] = extra
        reg = {"finish": None, "usage": None}
        self.ultimo = reg
        if kw.get("stream"):
            kw.setdefault("stream_options", {"include_usage": True})
            return self._mirar(self._c.chat.completions.create(**kw), reg)
        r = self._c.chat.completions.create(**kw)
        reg["finish"] = r.choices[0].finish_reason if r.choices else None
        reg["usage"] = _dump(getattr(r, "usage", None))
        return r

    def _mirar(self, flujo, reg):
        try:
            for trozo in flujo:
                if getattr(trozo, "usage", None):
                    reg["usage"] = _dump(trozo.usage)
                for c in trozo.choices or []:
                    if c.finish_reason:
                        reg["finish"] = c.finish_reason
                yield trozo
        finally:
            cerrar = getattr(flujo, "close", None)
            if cerrar:
                cerrar()

    def with_options(self, **kw):
        return Medidor(self._c.with_options(**kw), self._or)

    def __getattr__(self, nombre):
        return getattr(self._c, nombre)


def proveedor(clave_modelo, tope):
    prov_nombre, modelo = MODELOS[clave_modelo]
    p = llm.ProveedorCompatible(modelo, config.clave_llm(prov_nombre),
                                llm.BASE_URLS[prov_nombre], dict(TOPES[tope]))
    med = Medidor(p._c, prov_nombre == "openrouter")
    p._c = med
    return p, med


# ---------------------------------------------------------------------------
# Escenarios (CoreWork sintético; hoy fijo: sábado 03/10/2026)
# ---------------------------------------------------------------------------

HOY = date(2026, 10, 3)
LIMITE = date(2026, 12, 3)
QUIEN = "Ariel De Simone"
ENVIAR = "Enviar a aprobación"
OBJETIVOS = [
    "Conectar y automatizar equipos para que produzcan y entreguen datos",
    "Planos eléctricos correctos y documentación útil",
    "Fortalecer servidores y mejorar EPPI",
    "Construir o adaptar tableros preparados para la integración",
    "Robustecer la plataforma e integrar los datos",
]
RESPONSABLES = [
    ("Ariel De Simone", "Software e interfaz HMI", "Explicación, Captura"),
    ("Marcos Tarquini", "OT y automatización",
     "Explicación, Resultado de prueba, Captura, Archivo"),
    ("Martín Forte", "Infraestructura IT", "Explicación, Resultado de prueba"),
    ("Nahuel Gimenez", "OT y automatización",
     "Explicación, Resultado de prueba, Captura, Archivo"),
]

ESCENARIOS = [
    {"id": "s1", "nombre": "fecha fuera de margen", "alta": True, "rutear": True,
     "mensaje": "tengo que cambiar los filtros del compresor de aire para el 15 de diciembre",
     "borrador": {}, "historial": []},
    {"id": "s2", "nombre": "título vago", "alta": True, "rutear": True,
     "mensaje": "anotame lo del tablero", "borrador": {}, "historial": []},
    {"id": "s3", "nombre": "datos completos", "alta": True, "rutear": True,
     "mensaje": "revisar el sensor de nivel del tanque 2 para el viernes, la hago yo",
     "borrador": {}, "historial": []},
    {"id": "s4", "nombre": "qué sugerís (falta criterio)", "alta": True, "rutear": False,
     "mensaje": "no sé, qué sugerís?",
     "borrador": {
         "title": ("Actualizar el plano del tablero 5", "Actualizar el plano del tablero 5"),
         "objective": (OBJETIVOS[1], "obj-2"),
         "responsible": (QUIEN, "mem-1"),
         "due_date": ("07/10/2026", "2026-10-07")},
     "historial": [
         {"role": "user", "content": "actualizar el plano del tablero 5 para el "
                                     "miércoles que viene, la hago yo"},
         {"role": "assistant", "content": "Perfecto 👍 ¿Cómo vamos a saber que el "
                                          "plano quedó actualizado? Con eso armamos "
                                          "el criterio de aceptación."}]},
    {"id": "s5", "nombre": "fecha relativa", "alta": True, "rutear": True,
     "mensaje": "preparar el informe de lotes para el jueves que viene",
     "borrador": {}, "historial": []},
    {"id": "s6", "nombre": "sólo ruteo: consulta", "alta": False, "rutear": True,
     "mensaje": "qué tareas tengo pendientes?", "borrador": {}, "historial": [],
     "ruta_esperada": ("normal_conversation",)},
    {"id": "s7", "nombre": "sólo ruteo: nada", "alta": False, "rutear": True,
     "mensaje": "no nada, no quiero hacer nada", "borrador": {}, "historial": [],
     "ruta_esperada": ("normal_conversation", "bare_greeting")},
]


def opciones():
    objs = tuple(T.OpcionAlta(f"O{n}", t, {"id": f"obj-{n}", "title": t})
                 for n, t in enumerate(OBJETIVOS, 1))
    resp = tuple(T.OpcionAlta(f"R{n}", nom, {"id": f"mem-{n}", "name": nom},
                              es_quien_escribe=(nom == QUIEN), boton_final=ENVIAR)
                 for n, (nom, _, _) in enumerate(RESPONSABLES, 1))
    return objs, resp


def borrador(confirmados):
    b = {c: T.CampoBorrador("falta") for c in T.CAMPOS}
    for campo, (mostrado, ref) in confirmados.items():
        b[campo] = T.CampoBorrador("confirmado", mostrado, ref)
    return b


def area_de(b):
    r = b["responsible"]
    if r.estado != "confirmado":
        return "", ""
    for n, (_, area, ev) in enumerate(RESPONSABLES, 1):
        if r.ref == f"mem-{n}":
            return area, ev
    return "", ""


def hechos(esc, b, rechazos):
    objs, resp = opciones()
    area, ev = area_de(b)
    return T.HechosTurno(
        hoy=HOY, limite_fecha=LIMITE, meses_horizonte=2, quien_escribe=QUIEN,
        borrador=b, area=area, evidencia=ev, objetivos=objs, responsables=resp,
        rechazos_anteriores=rechazos, evento={"mensaje": esc["mensaje"]},
        conversacion=tuple(m["content"] for m in esc["historial"]))


def con_asignaciones(b, asignaciones):
    nuevo = dict(b)
    for a in asignaciones:
        estado = {"confirmed": "confirmado", "proposed": "propuesto"}[a.estado]
        nuevo[a.campo] = T.CampoBorrador(estado, a.mostrado, a.ref)
    return nuevo


# ---------------------------------------------------------------------------
# Un mensaje
# ---------------------------------------------------------------------------

def _llamar(tipo, intento, med, fn):
    reg = {"tipo": tipo, "intento": intento}
    med.ultimo = None
    inicio = time.perf_counter()
    try:
        salida = fn(inicio, reg)
        reg["resultado"] = "pendiente"
    except Exception as exc:  # noqa: BLE001
        salida = None
        reg["resultado"] = "error"
        reg["motivo"] = redaccion._motivo_de_error(exc)
    reg["s"] = round(time.perf_counter() - inicio, 2)
    u = med.ultimo or {}
    reg["finish"] = u.get("finish")
    reg["usage"] = u.get("usage")
    det = (reg["usage"] or {}).get("completion_tokens_details") or {}
    reg["razonamiento"] = det.get("reasoning_tokens")
    if reg["resultado"] == "error" and reg["finish"] == "length":
        reg["motivo"] = "length: " + reg.get("motivo", "")
    return reg, salida


def mensaje(esc, clave, tope, rep, prov, med, instr_int, instr_red):
    out = {"modelo": clave, "tope": tope, "escenario": esc["id"], "rep": rep,
           "alta": esc["alta"], "llamadas": [], "fallo": False}
    t0 = time.perf_counter()
    if esc["rutear"]:
        ruta = None
        for intento in (1, 2):
            reg, ruta = _llamar("ruteo", intento, med,
                                lambda i, r: prov.route_intent(esc["mensaje"]))
            if ruta is not None:
                reg["resultado"] = "aceptada"
                reg["salida"] = {"action": ruta.action.value,
                                 "task": dict(ruta.task)}
            out["llamadas"].append(reg)
            if ruta is not None:
                break
        esperado = esc.get("ruta_esperada", ("start_task_intake",))
        out["ruta"] = ruta.action.value if ruta else None
        out["ruteo_caido"] = ruta is None
        out["ruteo_ok"] = ruta is not None and ruta.action.value in esperado
    if esc["alta"]:
        _alta(esc, out, prov, med, instr_int, instr_red)
    out["total_s"] = round(time.perf_counter() - t0, 2)
    return out


def _alta(esc, out, prov, med, instr_int, instr_red):
    b = borrador(esc["borrador"])
    permite_otro_tema = bool(esc["borrador"])
    rechazos: tuple[str, ...] = ()
    asignaciones = []
    interpretacion = None
    aplicacion = T.Aplicacion()
    for intento in (1, 2):
        h = hechos(esc, b, rechazos)
        reg, crudo = _llamar("interpreta", intento, med,
                             lambda i, r: prov.interpretar_alta(
                                 instr_int.texto, esc["historial"], T.hechos_a_json(h)))
        out["llamadas"].append(reg)
        if reg["resultado"] == "error":
            out["fallo"] = "interpreta: error"
            return
        reg["salida"] = crudo
        salida = T.leer_interpretacion(crudo)
        aplicacion = T.Aplicacion()
        if isinstance(salida, str):
            problemas = [salida]
        elif salida.intencion == "otro_tema" and not permite_otro_tema:
            problemas = ["intencion: otro_tema sólo vale con un mensaje de la "
                         "persona sobre algo distinto del alta"]
        else:
            aplicacion = T.aplicar_valores(salida, h)
            problemas = list(aplicacion.errores)
            if aplicacion.asignaciones:
                asignaciones += aplicacion.asignaciones
                b = con_asignaciones(b, aplicacion.asignaciones)
        if not problemas:
            reg["resultado"] = "aceptada"
            interpretacion = salida
            break
        reg["resultado"] = "rechazada"
        reg["motivo"] = "; ".join(problemas)[:300]
        rechazos = tuple(problemas)
    if interpretacion is None:
        out["fallo"] = "interpreta: dos rechazos"
        return
    out["intencion"] = interpretacion.intencion
    out["asignado"] = [{"campo": a.campo, "mostrado": a.mostrado} for a in asignaciones]
    out["rechazado"] = [{"campo": r.campo, "motivo": r.motivo} for r in aplicacion.rechazos]
    if interpretacion.intencion == "otro_tema":
        return                                   # se pausa; sin redacción
    efecto = {"cancelar": T.EFECTO_CANCELADA,
              "dejar": T.EFECTO_GUARDADA}.get(interpretacion.intencion)
    h = hechos(esc, b, ())
    resultado = T.ResultadoTurno(
        intencion=interpretacion.intencion, aplicado=tuple(asignaciones),
        rechazados=aplicacion.rechazos, corrige=interpretacion.corrige,
        efecto=efecto, criterio_no_verificable=aplicacion.criterio_no_verificable,
        saludo=None,
        resumen_sigue=(efecto is None and not h.faltan and bool(asignaciones)))
    rechazos = ()
    for intento in (1, 2):
        def llamar(inicio, reg, rechazos=rechazos):
            def al_avanzar(_t):
                reg.setdefault("primer_texto_s", round(time.perf_counter() - inicio, 2))
            return prov.conducir_alta(instr_red.texto, esc["historial"],
                                      T.resultado_a_json(h, resultado, rechazos),
                                      al_avanzar=al_avanzar)
        reg, crudo = _llamar("redacta", intento, med, llamar)
        out["llamadas"].append(reg)
        if reg["resultado"] == "error":
            out["fallo"] = "redacta: error"
            return
        reg["salida"] = crudo
        red = T.leer_redaccion(crudo)
        motivo = red if isinstance(red, str) else T.verificar_redaccion(red, h, resultado)
        if motivo is None:
            reg["resultado"] = "aceptada"
            out["texto"] = red.texto
            out["pregunta"] = list(red.pregunta)
            return
        reg["resultado"] = "rechazada"
        reg["motivo"] = motivo[:300]
        rechazos = (motivo,)
    out["fallo"] = "redacta: dos rechazos"


# ---------------------------------------------------------------------------
# Corrida
# ---------------------------------------------------------------------------

def main():
    instr_red = instrucciones_reales()
    instr_int = INS.instrucciones_interpretacion()
    escenarios = [e for e in ESCENARIOS
                  if not ARGS.escenarios or e["id"] in ARGS.escenarios.split(",")]
    configs = [(m, t) for m in ARGS.modelos.split(",") for t in ARGS.topes.split(",")]
    meta = {"fecha": time.strftime("%Y-%m-%d %H:%M"), "n": ARGS.n,
            "escenarios": [e["id"] for e in escenarios],
            "configs": configs, "hoy": HOY.isoformat(), "limite": LIMITE.isoformat(),
            "instrucciones_redacta_hash": instr_red.hash,
            "instrucciones_interpreta_hash": instr_int.hash}
    mensajes, candado = [], threading.Lock()
    parcial = AQUI / f"{ARGS.salida}.jsonl"
    parcial.write_text("", encoding="utf-8")

    def correr(clave, tope):
        prov, med = proveedor(clave, tope)
        for rep in range(1, ARGS.n + 1):
            for esc in escenarios:
                m = mensaje(esc, clave, tope, rep, prov, med, instr_int, instr_red)
                with candado:
                    mensajes.append(m)
                    with parcial.open("a", encoding="utf-8") as f:
                        f.write(json.dumps(m, ensure_ascii=False) + "\n")
                    print(f"{clave:6} {tope:4} r{rep} {esc['id']} {m['total_s']:6.1f}s "
                          f"llamadas={len(m['llamadas'])} fallo={m['fallo']} "
                          f"ruta={m.get('ruta')}", flush=True)

    hilos = [threading.Thread(target=correr, args=c, daemon=True) for c in configs]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    filas = escribir(mensajes, meta)
    print((AQUI / f"{ARGS.salida}.md").read_text(encoding="utf-8"))
    print("llamadas totales:", sum(len(m["llamadas"]) for m in mensajes),
          "| USD total:", round(sum(r["usd_total"] for r in filas.values()), 4))


main()
