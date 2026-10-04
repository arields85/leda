"""Follow a gentle-ai review lifecycle exactly as the provider issues it.

Usage: rdd_ciclo.py <cwd> <base-ref>
Runs the selectorless preflight STATUS with the given base, then only the commands
the provider returns: START, consent (the user pre-granted consent: picks the
provider-issued `granted` invocation), bound STATUS, reviewer captures (exact
tokens, in-process), and the final exact acknowledgement. Prints a summary.
"""
import json
import shlex
import subprocess
import sys

cwd, base = sys.argv[1], sys.argv[2]


def correr(cmd):
    if isinstance(cmd, str):
        args = shlex.split(cmd, posix=True)
    else:
        args = cmd
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    salida = (r.stdout or "") + (r.stderr or "")
    i = salida.find("{")
    if i < 0:
        return {"_crudo": salida[:500]}
    try:
        datos, _ = json.JSONDecoder().raw_decode(salida[i:])
        return datos
    except ValueError:
        return {"_crudo": salida[:500]}


def hallazgos(o, vistos):
    if isinstance(o, dict):
        if str(o.get("id", "")).startswith("R") and "severity" in o and o["id"] not in vistos:
            vistos[o["id"]] = (o.get("severity"), o.get("location"))
        for v in o.values():
            hallazgos(v, vistos)
    elif isinstance(o, list):
        for v in o:
            hallazgos(v, vistos)


d = correr(["gentle-ai", "review", "status", f"--cwd={cwd}",
            "--contract=gentle-ai.review-integration/v2", "--agent=claude-code",
            "--next-transition=true", f"--base-ref={base}", "--committed-only=true"])
vistos = {}
for paso in range(20):
    hallazgos(d, vistos)
    if d.get("schema", "").startswith("gentle-ai.review-acknowledged"):
        print("RECONOCIDA:", d.get("lineage_id"), "autoridad:", d.get("authority"))
        break
    if d.get("action") == "consent_required":
        g = [c for c in d.get("choices", []) if c.get("answer") == "granted"]
        print("consentimiento: granted (dado por el usuario)")
        d = correr(g[0]["invocation"])
        continue
    ack = d.get("acknowledgement")
    if ack and ack.get("command"):
        print("estado:", d.get("state"), "riesgo:", d.get("risk_level"))
        d = correr(ack["command"])
        continue
    nt = d.get("next_transition") or d.get("status_continuation") or {}
    tipo = nt.get("kind")
    if tipo == "execute":
        d = correr(nt["execute"]["command"])
        continue
    if tipo == "collect":
        resultados = []
        for entrada in nt["collect"]["inputs"]:
            tokens = [a["token"] for a in entrada["arguments"]]
            op = entrada["capture_operation"].split(".", 1)[1]
            print("captura:", entrada.get("artifact_subject", {}).get("lens"))
            resultados.append(correr(["gentle-ai", "review", op, *tokens]))
        d = resultados[-1]
        continue
    if tipo == "stop" or d.get("code"):
        print("PARADA:", d.get("code") or nt.get("reason_code"), d.get("message", "")[:300])
        break
    print("SIN TRANSICIÓN:", json.dumps(d, ensure_ascii=False)[:600])
    break
for k, (sev, loc) in vistos.items():
    print("  observación:", k, sev, loc)
