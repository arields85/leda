"""Línea de comandos.

    python -m prisma esquema                  aplica db/esquema.sql
    python -m prisma importar corework        importa el pack (sin activar)
    python -m prisma importar corework --activar
    python -m prisma feriados corework        carga los feriados nacionales
    python -m prisma sembrar corework --semilla espacios/corework.semilla-ficticia.yaml
    python -m prisma cadencia corework objetivos_semanales
    python -m prisma despachar corework       vacía la cola una vez
    python -m prisma escuchar corework         long polling + cadencias + escalera + despacho
    python -m prisma servir                   webhook + cadencias + escalera + despacho
    python -m prisma servir --sin-cadencias    igual, sin disparar cadencias automáticas
    python -m prisma correo-verificacion corework --activar
    python -m prisma correo-verificacion corework --desactivar
"""

from __future__ import annotations

import argparse
import subprocess
import sys

from .calendario import Calendario, cargar_feriados_ar
from .config import config
from .db import admin, conectar, espacio, registrar_auditoria
from .saludo import verificar_migraciones


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


def _verificar_esquema_o_salir(conn) -> int | None:
    """R4-003 (revisión 2026-09-28+3): sin `greeting_state` ni
    `message_outbox.es_bienvenida`, cada `despachar`/`enqueue_outbox` rompe
    con `UndefinedTable`/`UndefinedColumn` en el primer mensaje, tirando
    abajo todo el despacho. `servir` y `escuchar` son los dos puntos donde
    arranca el despacho sostenido -- rechazar arrancar acá, con un mensaje
    claro, es más barato que dejar que la falla aparezca recién en el
    primer envío real."""
    with admin(conn) as cur:
        falta = verificar_migraciones(cur)
    if falta is None:
        return None
    print(f"Falta aplicar la migración '{falta}'. Ejecutá "
          f"'python -m prisma esquema' antes de arrancar.")
    return 1


def _resolver_integrante(cur, ws: str, nombre: str) -> list[dict]:
    """Empareja por subcadena, sin importar mayúsculas -- mismo punto de
    partida que `onboarding.generar_enlaces` con `--solo` (T7,
    `odd/tasks/prisma-orienta.md`), pero además prefiere una coincidencia
    EXACTA sobre cualquier coincidencia parcial, cosa que `--solo` no hace:
    otorgar un rol privilegiado no puede quedar ambiguo sólo porque el
    nombre completo de alguien es substring del de otra persona. Busca
    sobre todo integrante activo del espacio, esté o no vinculado a
    Telegram: designar administrador no depende de que ya haya activado su
    cuenta (T11)."""
    cur.execute(
        """select m.app_user_id, u.nombre, u.telegram_user_id
             from membership m join app_user u on u.id = m.app_user_id
            where m.workspace_id = %s and m.activo
            order by u.nombre""",
        (ws,))
    buscado = nombre.lower()
    candidatos = [p for p in cur.fetchall() if buscado in p["nombre"].lower()]
    # Designa un rol privilegiado: si alguien coincide exacto, es esa
    # persona, aunque el fragmento también aparezca en otros nombres.
    exactos = [p for p in candidatos if p["nombre"].lower() == buscado]
    return exactos or candidatos


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


def _correo_verificacion(conn, ws: str, activar: bool) -> int:
    """Comando `correo-verificacion <espacio> --activar|--desactivar`
    (rama auxiliar, G1c). Enciende o apaga `correo_verificacion.habilitado`
    -- la misma clave que ya gobierna el alta con correo (G1a-G1b2) -- y,
    sólo al activar, atiende a quien YA estaba activo sin correo (C5: se le
    pide una vez, sin bloquearlo).

    Idempotente: `--activar` abre un ciclo en modo `existente` y encola el
    pedido sólo para quien esté activo, con Telegram ya vinculado, sin
    correo verificado y sin ningún ciclo abierto todavía -- correrlo dos
    veces no repite nada, porque la segunda vez esa condición ya no
    encuentra a nadie (quienes se procesaron en la primera ya tienen un
    ciclo abierto). Un integrante que todavía no activó su enlace no entra
    acá: le llega por el modo `alta` cuando lo haga.

    `--desactivar` sólo apaga la clave: los ciclos y datos ya creados quedan
    como están. `gate`/`atender_existente` (`alta_correo_flujo.py`) vuelven
    a comprobar la clave antes de actuar, así que con la clave apagada
    ninguno de los dos hace nada para nadie, tenga o no un ciclo a medio
    camino.

    G1c2, ítem 4: `--activar` toma un bloqueo consultivo de transacción,
    con clave en el espacio (mismo patrón que
    `ingreso_tareas.handle_active_text`), antes de leer la elegibilidad --
    dos corridas superpuestas para el mismo espacio se serializan, así
    ninguna puede abrir un ciclo ni encolar un pedido duplicado para la
    misma persona con la otra corrida todavía sin confirmar."""
    import json
    from datetime import datetime, timezone

    from . import alta_correo as AC
    from . import alta_correo_flujo as ACF
    from .db import registrar_auditoria

    ahora = datetime.now(timezone.utc)
    nombres_pendientes: list[str] = []
    with espacio(conn, ws) as cur:
        if activar:
            cur.execute(
                "select pg_advisory_xact_lock(hashtextextended(%s, 0))",
                (f"correo-verificacion:activar:{ws}",))
        cur.execute(
            """insert into workspace_setting (workspace_id, clave, valor)
                 values (%s, %s, %s)
               on conflict (workspace_id, clave) do update set valor = excluded.valor""",
            (ws, AC.CLAVE_HABILITADO, json.dumps(activar)))
        registrar_auditoria(
            cur, accion=("correo_verificacion_activado" if activar
                        else "correo_verificacion_desactivado"),
            workspace_id=ws, actor_kind="sistema")

        if activar:
            # `no verified contact` + `no open cycle`: el mismo integrante
            # nunca aparece dos veces en corridas distintas de este
            # comando, porque la primera corrida ya le abre un ciclo.
            for fila in AC.elegibles_existente(cur, ws):
                ACF.abrir_ciclo_existente(
                    cur, str(fila["membership_id"]), ws, fila["telegram_user_id"], ahora)
                nombres_pendientes.append(fila["nombre"])
            if nombres_pendientes:
                # Nombres, nunca correos ni cuerpos de mensaje -- la entrega
                # de este aviso por el bot de administración es G1d.
                AC.crear_aviso(
                    cur, "correo_existente_pendientes",
                    "Se les pidió el correo laboral a quienes ya estaban "
                    "activos sin uno: " + ", ".join(nombres_pendientes) + ".",
                    workspace_id=ws, referencia_tipo="workspace",
                    referencia_id=ws, ahora=ahora)
    conn.commit()

    if activar:
        print("Verificación de correo activada.")
        if nombres_pendientes:
            print(f"Se les pidió el correo a {len(nombres_pendientes)} "
                  "integrante(s) ya activo(s):")
            for nombre in nombres_pendientes:
                print(f"  {nombre}")
        else:
            print("Nadie quedó pendiente: todos ya tienen correo verificado "
                  "o un ciclo abierto.")
    else:
        print("Verificación de correo desactivada.")
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

    adm = sub.add_parser("administrador")
    adm.add_argument("slug")
    adm.add_argument("nombre", help="nombre del integrante, entre comillas si tiene espacios")

    sub.add_parser("presentar").add_argument("slug")

    esc = sub.add_parser("escuchar")
    esc.add_argument("slug")
    esc.add_argument("--sin-cadencias", action="store_true",
                     help="no dispara cadencias automáticas; escalera y despacho siguen")

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

    cve = sub.add_parser("correo-verificacion")   # rama auxiliar, G1c
    cve.add_argument("slug")
    cve_flags = cve.add_mutually_exclusive_group(required=True)
    cve_flags.add_argument("--activar", action="store_true")
    cve_flags.add_argument("--desactivar", action="store_true")

    goo = sub.add_parser("google")     # rama auxiliar, G2
    goo_sub = goo.add_subparsers(dest="google_cmd", required=True)
    goo_sub.add_parser("clave-nueva", help="genera una clave para "
                       "PRISMA_CLAVE_CREDENCIALES (no escribe archivos)")

    srv = sub.add_parser("servir")
    srv.add_argument("--puerto", type=int, default=8080)
    srv.add_argument("--sin-cadencias", action="store_true",
                     help="no dispara cadencias automáticas; escalera y despacho siguen")

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

    if a.cmd == "google" and a.google_cmd == "clave-nueva":
        # No necesita base ni archivos: sólo genera e imprime la clave.
        from .google.cifrado import VARIABLE_CLAVE, clave_nueva

        print("Clave nueva para cifrar las credenciales de Google:\n")
        print(clave_nueva())
        print(f"\nAgregala al archivo .env como {VARIABLE_CLAVE}=<clave>.")
        print("Para rotar: poné la clave nueva primero y conservá las "
              "anteriores después de una coma,")
        print("y después corré `python -m prisma google recifrar` "
              "(disponible más adelante).")
        return 0

    if a.cmd == "servir":
        import uvicorn
        from .reloj import montar

        conn_chequeo = conectar()
        try:
            codigo = _verificar_esquema_o_salir(conn_chequeo)
        finally:
            conn_chequeo.close()
        if codigo is not None:
            return codigo
        montar(lambda: conectar(), con_cadencias=not a.sin_cadencias).start()
        uvicorn.run("prisma.gateway:app", host="0.0.0.0", port=a.puerto)
        return 0

    if a.cmd == "grupo":
        # No necesita base: sólo pregunta a Telegram qué llegó.
        import httpx

        from .despachador import pedido_telegram

        token = config.token_bot(a.slug)
        pedido_telegram(
            httpx.post, f"https://api.telegram.org/bot{token}/deleteWebhook",
            timeout=15)
        print("Agregá el bot al grupo y escribí cualquier cosa ahí.")
        print("Esperando…\n")
        offset = 0
        for _ in range(12):
            r = pedido_telegram(
                httpx.get, f"https://api.telegram.org/bot{token}/getUpdates",
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

        clave = config.clave_llm(a.proveedor)
        if not clave:
            print(f"{config.variable_clave_llm(a.proveedor)} está vacío en .env.")
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
        if not config.clave_llm(a.proveedor):
            print(f"Ojo: {config.variable_clave_llm(a.proveedor)} está vacío "
                  "en .env.")
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

        from .despachador import pedido_telegram
        from .onboarding import generar_enlaces, pendientes_de_activar

        token = config.token_bot(a.slug)
        r = pedido_telegram(
            httpx.get, f"https://api.telegram.org/bot{token}/getMe", timeout=15)
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

    if a.cmd == "administrador":
        with admin(conn) as cur:
            candidatos = _resolver_integrante(cur, ws, a.nombre)
            if not candidatos:
                print(f"No encontré a nadie llamado «{a.nombre}» en '{a.slug}'.")
                return 1
            if len(candidatos) > 1:
                print(f"«{a.nombre}» es ambiguo en '{a.slug}': hay "
                      f"{len(candidatos)} personas que coinciden:")
                for c in candidatos:
                    print(f"  {c['nombre']}")
                print("Usá un nombre más específico.")
                return 1

            persona = candidatos[0]
            cur.execute(
                """insert into platform_role (app_user_id, rol)
                     values (%s, 'administrador')
                   on conflict do nothing
                   returning app_user_id""",
                (persona["app_user_id"],))
            nuevo = cur.fetchone() is not None
            if nuevo:
                registrar_auditoria(
                    cur, accion="otorgar_administrador", actor_kind="sistema",
                    sujeto_tipo="app_user", sujeto_id=persona["app_user_id"],
                    detalle={"nombre": persona["nombre"]})
        conn.commit()

        print(f"{persona['nombre']}: administrador de plataforma "
              + ("otorgado." if nuevo else "(ya lo era)."))
        if not persona["telegram_user_id"]:
            print("Todavía no vinculó su Telegram (falta 'enlaces'): los "
                  "avisos de incidente no le van a llegar hasta que active "
                  "su cuenta y le escriba una vez al bot de administración.")
        else:
            print("Próximo paso: que le escriba una vez al bot de "
                  "administración (PRISMA_BOT_TOKEN_ADMIN) -- Telegram no "
                  "deja que un bot le escriba primero a quien nunca le "
                  "escribió, así que sin eso no hay a qué chat avisarle.")
        return 0

    if a.cmd == "escuchar":
        from .local import escuchar
        codigo = _verificar_esquema_o_salir(conn)
        if codigo is not None:
            return codigo
        escuchar(conn, a.slug, ws, con_cadencias=not a.sin_cadencias)
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

    if a.cmd == "correo-verificacion":
        return _correo_verificacion(conn, ws, a.activar)

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
