"""Corre una revisión RDD de un tramo de commits ejecutando, tal cual, las transiciones
que devuelve `gentle-ai` (preflight STATUS, START, consentimiento, capturas de los
lentes, STATUS ligado y reconocimiento). Se detiene e imprime ante cualquier cosa que
no sea el camino normal (falla, corrección pedida, presupuesto excedido).

Uso: python tools/rdd_por_tramos.py <repo> <base-ref> <etiqueta>
  <repo>      checkout a revisar (por ejemplo el worktree de la rama);
  <base-ref>  último commit ya revisado (la frontera): se revisa base..HEAD;
  <etiqueta>  carpeta donde quedan las respuestas JSON de cada paso.

El consentimiento se concede solo: el usuario dio consentimiento permanente para las
revisiones RDD (memoria `autonomia-commits-rdd`). Si el tramo no entra en el
presupuesto del revisor (`lens_context_budget_exceeded`), revisar commit por commit:
dejar el checkout en cada commit (`git checkout --detach <c>`) con la base en el
anterior, y volver a la rama al final. Nunca con el listener corriendo sobre ese
checkout.
"""
import json
import shlex
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO, BASE, TAG = sys.argv[1], sys.argv[2], sys.argv[3]
OUT = Path(__file__).parent / "_rdd" / TAG
OUT.mkdir(parents=True, exist_ok=True)
step = 0


def run(argv, name):
    global step
    step += 1
    p = subprocess.run(argv, cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    (OUT / f"{step:02d}-{name}.json").write_text(p.stdout + "\n--stderr--\n" + p.stderr,
                                                 encoding="utf-8")
    try:
        return json.JSONDecoder().raw_decode(p.stdout.lstrip())[0]
    except Exception:
        print("UNPARSEABLE", name, p.returncode, p.stdout[:800], p.stderr[:800])
        sys.exit(2)


def op_argv(operation, args):
    return ["gentle-ai", *operation.split(".")] + [a["token"] for a in args]


d = run(["gentle-ai", "review", "status", "--cwd", REPO, "--contract",
         "gentle-ai.review-integration/v2", "--agent", "claude-code", "--next-transition",
         "--base-ref", BASE, "--committed-only"], "preflight")
bound = None
for _ in range(20):
    schema = d.get("schema", "")
    if "consent" in schema:
        inv = next(c["invocation"] for c in d["choices"] if c["answer"] == "granted")
        print("consent granted (durable user authorization)")
        d = run(shlex.split(inv), "granted")
        continue
    if "failure" in schema or d.get("state") in ("correction_required",):
        print("STOP", json.dumps(d, indent=1, ensure_ascii=False)[:3000])
        sys.exit(1)
    if schema == "gentle-ai.review-acknowledged/v1":
        print("ACKNOWLEDGED", d["lineage_id"], d["authority"])
        sys.exit(0)
    if "last-event-closure" in schema:
        print("CLOSURE", d.get("state"))
        for f in (d.get("advisory_findings") or {}).get("findings", []):
            print("  advisory", f["severity"], f["id"], f["location"])
        cont = d.get("status_continuation")
        if cont:
            d = run(op_argv(cont["operation"], cont["arguments"]), "continuation")
            continue
        if bound is None:
            print("STOP no bound status")
            sys.exit(1)
        d = run(bound, "status")
        continue
    nt = d.get("next_transition") or {}
    kind = nt.get("kind")
    if kind == "execute":
        e = nt["execute"]
        if e["operation"] == "review.start":
            d = run(op_argv(e["operation"], e["arguments"]), "start")
        elif e["operation"] == "review.status":
            bound = op_argv(e["operation"], e["arguments"])
            d = run(bound, "status")
        elif e["operation"] == "review.acknowledge-approved":
            d = run(op_argv(e["operation"], e["arguments"]), e["operation"].split(".")[1])
        else:
            print("STOP unexpected execute", e["operation"])
            sys.exit(1)
        continue
    if kind == "collect":
        inputs = nt["collect"]["inputs"]
        if any(i.get("capture_operation") != "review.capture-result" for i in inputs):
            print("STOP non-reviewer collect", json.dumps(inputs, indent=1)[:2000])
            sys.exit(1)
        print(f"capturing {len(inputs)} lens(es):", [
            next(a["value"] for a in i["arguments"] if a["name"] == "lens") for i in inputs])
        with ThreadPoolExecutor(len(inputs)) as ex:
            results = list(ex.map(
                lambda i: run(op_argv(i["capture_operation"], i["arguments"]), "capture"),
                inputs))
        d = results[-1]
        # Reconcile through the bound status of the final capture, or the bound one.
        if "last-event-closure" not in d.get("schema", ""):
            print("capture result schema:", d.get("schema"), d.get("action"))
            if bound is None:
                print("STOP no bound status"); sys.exit(1)
            d = run(bound, "status")
        continue
    print("STOP", d.get("schema"), d.get("action"), json.dumps(nt, indent=1)[:2000])
    sys.exit(1)
print("STOP too many steps")
sys.exit(1)
