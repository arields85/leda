"""Línea de comandos.

    python -m prisma esquema                  aplica db/esquema.sql
    python -m prisma importar corework        importa el pack (sin activar)
    python -m prisma importar corework --activar
    python -m prisma feriados corework        carga los feriados nacionales
    python -m prisma sembrar corework --semilla espacios/corework.semilla-ficticia.yaml
    python -m prisma cadencia corework objetivos_semanales
    python -m prisma despachar corework       vacía la cola una vez
    python -m prisma servir                   webhook + planificador
"""

from __future__ import annotations

import argparse
import subprocess
import sys

from .calendario import Calendario, cargar_feriados_ar
from .config import config
from .db import admin, conectar, espacio


def _revertir_sin_traza(conn) -> None:
    """`conn.rollback()` puede volver a fallar si la conexión ya está rota
    (T7c, seguimiento a review-05906dd3) -- sin este guard, esa segunda
    falla tapaba el mensaje limpio que la rama que la llama ya decidió
    mostrar y terminaba en una traza cruda de la propia falla del rollback.
    Si el rollback en sí falla, no hay nada más para hacer con esta
    conexión: se ignora acá para que el comando pueda terminar con su
    mensaje y su código de salida."""
    try:
        conn.rollback()
    except Exception:
        pass


def _id_de(conn, slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("set role prisma_admin")
        cur.execute("select id from workspace where slug = %s", (slug,))
        fila = cur.fetchone()
    if not fila:
        sys.exit(f"No existe el espacio '{slug}'.")
    return str(fila["id"])


def _estado(conn, ws: str, slug: str) -> int:
    """Una foto de cómo va la prueba, sin entrar a la base."""
    with admin(conn) as cur:
        print(f"== {slug} ==\n")

        cur.execute(
            """select u.nombre, a.slug as area, r.slug as rol,
                      u.telegram_user_id is not null as activo
                 from membership m
                 join app_user u on u.id = m.app_user_id
                 join area a on a.id = m.area_id
                 join rol r on r.id = m.rol_id
                where m.workspace_id = %s order by u.nombre""", (ws,))
        print("Integrantes")
        for p in cur.fetchall():
            marca = "activo" if p["activo"] else "sin activar"
            print(f"  {p['nombre']:22s} {p['area']:14s} {p['rol']:11s} {marca}")

        cur.execute(
            """select t.titulo, t.estado, t.fecha_objetivo, u.nombre,
                      motivo_no_cierra_tarea(t.id) as falta
                 from task t
                 left join membership m on m.id = t.responsable_membership_id
                 left join app_user u on u.id = m.app_user_id
                where t.workspace_id = %s
                order by t.fecha_objetivo nulls last""", (ws,))
        tareas = cur.fetchall()
        print(f"\nTareas ({len(tareas)})")
        for t in tareas:
            fecha = f"{t['fecha_objetivo']:%d/%m}" if t["fecha_objetivo"] else "sin fecha"
            print(f"  {t['titulo'][:34]:34s} {t['estado']:12s} "
                  f"{(t['nombre'] or '—')[:16]:16s} {fecha}")
            if t["falta"] and t["estado"] != "terminada":
                print(f"      para cerrar falta: {t['falta']}")

        cur.execute(
            """select o.titulo, o.tipo, o.estado,
                      motivo_no_cierra_objetivo(o.id) as falta
                 from objective o where o.workspace_id = %s order by o.tipo""", (ws,))
        objetivos = cur.fetchall()
        if objetivos:
            print(f"\nObjetivos ({len(objetivos)})")
            for o in objetivos:
                print(f"  {o['titulo'][:34]:34s} {o['tipo']:12s} {o['estado']}")
                if o["falta"] and o["estado"] != "terminado":
                    print(f"      para cerrar falta: {o['falta']}")

        cur.execute(
            """select b.causa, t.titulo,
                      extract(day from now() - b.abierto_en)::int as dias
                 from blocker b join task t on t.id = b.task_id
                where b.workspace_id = %s and b.resuelto_en is null""", (ws,))
        bloqueos = cur.fetchall()
        if bloqueos:
            print(f"\nBloqueos abiertos ({len(bloqueos)})")
            for b in bloqueos:
                print(f"  {b['titulo'][:30]:30s} {b['causa'][:40]:40s} {b['dias']}d")

        cur.execute(
            """select estado, count(*) n from message_outbox
                where workspace_id = %s group by estado""", (ws,))
        cola = {f["estado"]: f["n"] for f in cur.fetchall()}
        print("\nCola de salida:", cola or "vacía")

        cur.execute(
            "select count(*) n from incident where workspace_id = %s", (ws,))
        inc = cur.fetchone()["n"]
        if inc:
            print(f"Incidentes registrados: {inc}  (python -m prisma incidentes {slug})")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="prisma")
    sub = p.add_subparsers(dest="cmd", required=True)

    esq = sub.add_parser("esquema")
    esq.add_argument("--recrear", action="store_true",
                     help="borra todo y vuelve a crear. Se pierden los datos.")

    imp = sub.add_parser("importar")
    imp.add_argument("slug")
    imp.add_argument("--activar", action="store_true")

    fer = sub.add_parser("feriados"); fer.add_argument("slug")

    sem = sub.add_parser("sembrar")
    sem.add_argument("slug")
    sem.add_argument("--semilla", required=True,
                     help="ruta al YAML de datos ficticios (T7, odd/tasks/prisma-orienta.md)")

    cad = sub.add_parser("cadencia")
    cad.add_argument("slug"); cad.add_argument("nombre")

    des = sub.add_parser("despachar"); des.add_argument("slug")
    esc = sub.add_parser("escalera"); esc.add_argument("slug")

    enl = sub.add_parser("enlaces")
    enl.add_argument("slug")
    enl.add_argument("--solo", nargs="*", help="nombres, para el piloto")

    sub.add_parser("presentar").add_argument("slug")
    sub.add_parser("escuchar").add_argument("slug")
    sub.add_parser("grupo").add_argument("slug")

    mod = sub.add_parser("modelo")
    mod.add_argument("nombre", nargs="?", help="identificador del modelo")
    mod.add_argument("--proveedor", default="gemini")

    mds = sub.add_parser("modelos")   # pregunta al proveedor cuáles hay
    mds.add_argument("--proveedor", default="gemini")
    sub.add_parser("estado").add_argument("slug")
    sub.add_parser("incidentes").add_argument("slug")

    cor = sub.add_parser("correr")     # dispara una cadencia a mano
    cor.add_argument("slug"); cor.add_argument("nombre")

    srv = sub.add_parser("servir")
    srv.add_argument("--puerto", type=int, default=8080)

    a = p.parse_args(argv)

    if a.cmd == "esquema":
        # Sin psql: psycopg manda el archivo entero al servidor. Una sola
        # transacción, así que si algo falla no queda a medio aplicar.
        import psycopg

        sql = (config.raiz / "db" / "esquema.sql").read_text(encoding="utf-8")
        if a.recrear:
            sql = "drop schema if exists prisma cascade;\n" + sql
        try:
            with psycopg.connect(config.db_url, autocommit=False) as c:
                c.execute(sql)
        except psycopg.OperationalError as e:
            print("No se pudo conectar a la base.")
            print(f"  {str(e).strip().splitlines()[0]}")
            print("\nRevisá PRISMA_DB_URL en .env y que PostgreSQL esté corriendo.")
            return 1
        except psycopg.Error as e:
            print("La base rechazó el esquema:")
            print(f"  {str(e).strip().splitlines()[0]}")
            return 1
        print("Esquema aplicado.")
        return 0

    if a.cmd == "servir":
        import uvicorn
        from .reloj import montar

        montar(lambda: conectar()).start()
        uvicorn.run("prisma.gateway:app", host="0.0.0.0", port=a.puerto)
        return 0

    if a.cmd == "grupo":
        # No necesita base: sólo pregunta a Telegram qué llegó.
        import httpx

        token = config.token_bot(a.slug)
        httpx.post(f"https://api.telegram.org/bot{token}/deleteWebhook", timeout=15)
        print("Agregá el bot al grupo y escribí cualquier cosa ahí.")
        print("Esperando…\n")
        offset = 0
        for _ in range(12):
            r = httpx.get(f"https://api.telegram.org/bot{token}/getUpdates",
                          params={"offset": offset, "timeout": 20}, timeout=30)
            vistos = set()
            for u in r.json().get("result", []):
                offset = u["update_id"] + 1
                chat = (u.get("message") or {}).get("chat") or {}
                if chat.get("type") in ("group", "supergroup") \
                        and chat["id"] not in vistos:
                    vistos.add(chat["id"])
                    print(f"  {chat.get('title','(sin título)')}")
                    print(f"  grupo_gestion_id: {chat['id']}\n")
            if vistos:
                print("Copiá ese número a espacios/"
                      f"{a.slug}.yaml, en telegram.grupo_gestion_id.")
                return 0
        print("No llegó ningún mensaje de grupo. Revisá que el bot esté "
              "agregado y que alguien haya escrito.")
        return 1

    if a.cmd == "modelos":
        # No necesita base: le pregunta directo al proveedor.
        from .llm import BASE_URLS

        clave = config.llm_api_key
        if not clave:
            print("PRISMA_LLM_API_KEY está vacío en .env.")
            return 1
        try:
            if a.proveedor == "gemini":
                import httpx

                from .llm import GEMINI_BASE

                r = httpx.get(f"{GEMINI_BASE}/models",
                              headers={"x-goog-api-key": clave}, timeout=30)
                r.raise_for_status()
                nombres = [m["name"].removeprefix("models/")
                           for m in r.json().get("models", [])
                           if "generateContent" in m.get("supportedGenerationMethods", [])]
            elif a.proveedor == "anthropic":
                import anthropic

                nombres = [m.id for m in
                           anthropic.Anthropic(api_key=clave).models.list(limit=40).data]
            else:
                import openai

                base = BASE_URLS.get(a.proveedor)
                if not base:
                    print(f"No conozco la dirección de '{a.proveedor}'.")
                    print("Conocidos:", ", ".join(sorted(BASE_URLS)))
                    return 1
                nombres = [m.id for m in
                           openai.OpenAI(api_key=clave, base_url=base).models.list().data]
        except Exception as e:  # noqa: BLE001
            print("No se pudo consultar al proveedor:")
            print(f"  {type(e).__name__}: {str(e)[:300]}")
            return 1

        for n in sorted(nombres):
            print(f"  {n}")
        print(f"\nElegí uno y corré:")
        print(f"  python -m prisma modelo <identificador> --proveedor {a.proveedor}")
        return 0

    conn = conectar()

    if a.cmd == "modelo":
        with admin(conn) as cur:
            if not a.nombre:
                cur.execute(
                    "select proveedor, modelo, activo from model_config "
                    "where ambito = 'global'")
                filas = cur.fetchall()
                if not filas:
                    print("No hay modelo configurado.")
                    print("Ejemplo:  python -m prisma modelo <identificador>")
                    return 1
                for f in filas:
                    marca = "activo" if f["activo"] else "inactivo"
                    print(f"  {f['proveedor']:12s} {f['modelo']:32s} {marca}")
                return 0

            # Un solo modelo global activo por vez.
            cur.execute(
                "update model_config set activo = false where ambito = 'global'")
            cur.execute(
                """insert into model_config (ambito, proveedor, modelo, activo)
                   values ('global', %s, %s, true)""",
                (a.proveedor, a.nombre))
        conn.commit()
        print(f"Modelo configurado: {a.proveedor} / {a.nombre}")
        if not config.llm_api_key:
            print("Ojo: PRISMA_LLM_API_KEY está vacío en .env.")
        return 0

    if a.cmd == "importar":
        from .importador import PackInvalido, importar

        ruta = config.espacios / f"{a.slug}.yaml"
        try:
            r = importar(conn, ruta, activar=a.activar)
        except PackInvalido as e:
            print("No se puede activar el espacio:")
            for problema in e.problemas:
                print("  ·", problema)
            return 1
        conn.commit()
        print(f"{r.slug} v{r.version} — {r.pack_hash[:12]} — "
              f"{'activo' if r.activo else 'importado sin activar'}")
        for adv in r.advertencias:
            print("  advertencia:", adv)
        if r.pendientes:
            print(f"  {len(r.pendientes)} valores sin definir:",
                  ", ".join(r.pendientes[:6]))
        return 0

    ws = _id_de(conn, a.slug)

    if a.cmd == "enlaces":
        import httpx

        from .onboarding import generar_enlaces, pendientes_de_activar

        token = config.token_bot(a.slug)
        r = httpx.get(f"https://api.telegram.org/bot{token}/getMe", timeout=15)
        usuario = r.json()["result"]["username"]

        with admin(conn) as cur:
            enlaces = generar_enlaces(cur, ws, usuario, solo=a.solo)
            faltan = pendientes_de_activar(cur, ws)
        conn.commit()

        if not enlaces:
            print("No hay nadie pendiente de activar.")
            return 0
        print("Mandale a cada uno SU enlace, por privado.")
        print("Publicarlos en el grupo permitiría que alguien tome la identidad")
        print("de otro y reciba su seguimiento.\n")
        for e in enlaces:
            print(f"  {e.nombre:24s} {e.url}")
        print(f"\nVencen el {enlaces[0].expira_en:%d/%m/%Y}.")
        print(f"Pendientes de activar: {len(faltan)}")
        return 0

    if a.cmd == "escuchar":
        from .local import escuchar
        escuchar(conn, a.slug, ws)
        return 0

    if a.cmd == "estado":
        return _estado(conn, ws, a.slug)

    if a.cmd == "incidentes":
        with admin(conn) as cur:
            cur.execute(
                """select at, severidad, resumen_sanitizado, referencia_cruda,
                          etapa, referencia_tipo, referencia_id, chat_id,
                          notificado_en
                     from incident where workspace_id = %s
                    order by at desc limit 20""", (ws,))
            filas = cur.fetchall()
        if not filas:
            print("Sin incidentes.")
        for f in filas:
            print(f"\n{f['at']:%d/%m %H:%M}  [{f['severidad']}] {f['resumen_sanitizado']}")
            # Trazabilidad (T2b): etapa + referencia a la fila que originó
            # esto (nunca su texto -- eso se abre aparte, desde esa fila) +
            # si se avisó a la persona. Nunca se imprime un secreto acá.
            detalle = []
            if f["etapa"]:
                detalle.append(f"etapa={f['etapa']}")
            if f["referencia_tipo"] and f["referencia_id"]:
                detalle.append(f"{f['referencia_tipo']}={f['referencia_id']}")
            if f["chat_id"]:
                detalle.append(f"chat={f['chat_id']}")
            detalle.append("avisado" if f["notificado_en"] else "sin avisar")
            if detalle:
                print(f"    {' · '.join(detalle)}")
            if f["referencia_cruda"]:
                print(f"    {f['referencia_cruda'][:300]}")
        return 0

    if a.cmd == "correr":
        from .local import Escucha
        e = Escucha(conn, a.slug, ws, token="")
        print("encolados:", e.correr_cadencia(a.nombre))
        return 0

    if a.cmd == "presentar":
        from .onboarding import encolar_presentacion

        with admin(conn) as cur:
            ok = encolar_presentacion(cur, ws)
        conn.commit()
        print("presentación encolada" if ok
              else "no hay presentación o falta el grupo")
        return 0

    if a.cmd == "feriados":
        with admin(conn) as cur:
            cargar_feriados_ar(cur, ws)
        conn.commit()
        print("feriados cargados")
        return 0

    if a.cmd == "sembrar":
        from pathlib import Path

        import psycopg

        from .siembra import SiembraInvalida, sembrar

        try:
            with admin(conn) as cur:
                r = sembrar(cur, ws, Path(a.semilla))
        except SiembraInvalida as e:
            _revertir_sin_traza(conn)
            print(str(e))
            return 1
        except psycopg.Error as e:
            # Nunca el DETAIL crudo de la base acá: puede traer la fila
            # entera que la violó (títulos de tarea incluidos). Sólo el tipo
            # de error, nunca su mensaje (T7b, `odd/tasks/prisma-orienta.md`).
            _revertir_sin_traza(conn)
            print(f"La base rechazó la siembra ({type(e).__name__}). No se guardó nada.")
            return 1
        conn.commit()
        print(f"{r.tareas} tareas y {r.dependencias} dependencias sembradas.")
        for estado, n in sorted(r.estados.items()):
            print(f"  {estado}: {n}")
        return 0

    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)

        if a.cmd == "cadencia":
            from .reloj import ejecutar_cadencia
            print("encolados:", ejecutar_cadencia(cur, ws, a.nombre, cal))

        elif a.cmd == "escalera":
            from .reloj import ejecutar_escalera
            print("encolados:", ejecutar_escalera(cur, ws, cal))

        elif a.cmd == "despachar":
            from .despachador import TransporteTelegram, despachar
            transporte = TransporteTelegram(config.token_bot(a.slug))
            print(despachar(cur, ws, transporte, cal))

    conn.commit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
