"""Línea de comandos.

    python -m leda esquema                  aplica db/esquema.sql
    python -m leda importar corework        importa el pack (sin activar)
    python -m leda importar corework --activar
    python -m leda feriados corework        carga los feriados nacionales
    python -m leda sembrar corework --semilla espacios/corework.semilla-ficticia.yaml
    python -m leda despachar corework       vacía la cola una vez
    python -m leda escuchar corework        el motor de conversación, por long polling
    python -m leda servir                   webhook + tablero + el ciclo del motor
    python -m leda webhooks                 registra el webhook de cada bot
    python -m leda chatgpt login|estado|salir   la sesión de la suscripción de ChatGPT
    python -m leda modelo gpt-6-sol --proveedor chatgpt
"""

from __future__ import annotations

import argparse
import json
import sys

from .calendario import Calendario, cargar_feriados_ar
from .config import config
from .db import admin, conectar, espacio, registrar_auditoria
from .llm import PROVEEDORES_CON_SESION
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
        cur.execute("set role leda_admin")
        cur.execute("select id from workspace where slug = %s", (slug,))
        fila = cur.fetchone()
    if not fila:
        sys.exit(f"No existe el espacio '{slug}'.")
    return str(fila["id"])


def _verificar_esquema_o_salir(conn) -> int | None:
    """R4-003 (revisión 2026-09-28+3): sin `greeting_state` ni
    `message_outbox.es_bienvenida`, cada `despachar`/`enqueue_outbox` rompe
    con `UndefinedTable`/`UndefinedColumn` en el primer mensaje, tirando
    abajo todo el despacho. `servir` es el punto donde
    arranca el despacho sostenido -- rechazar arrancar acá, con un mensaje
    claro, es más barato que dejar que la falla aparezca recién en el
    primer envío real."""
    with admin(conn) as cur:
        falta = verificar_migraciones(cur)
    if falta is None:
        return None
    print(f"Falta aplicar la migración '{falta}'. Ejecutá "
          f"'python -m leda esquema' antes de arrancar.")
    return 1


def _parametros_del_modelo(texto: str | None, proveedor: str = "") -> dict | None:
    """Los parámetros de `modelo --parametros`, revisados como los lee el motor
    (`leda.motor.ia_real.validar_parametros`, o los de la suscripción de ChatGPT); se guardan
    como se escribieron, sin los de omisión. `None`, después de decir por qué, si no valen."""
    from .motor.ia_real import ParametrosInvalidos, validar_parametros

    if proveedor in PROVEEDORES_CON_SESION:
        from .motor.chatgpt import validar_parametros_chatgpt as validar_parametros

    if texto is None:
        return {}
    try:
        parametros = json.loads(texto)
    except ValueError as e:
        print(f"--parametros no es JSON ({e}).")
        return None
    if not isinstance(parametros, dict):
        print(f"--parametros tiene que ser un objeto JSON; vino {texto!r}.")
        return None
    try:
        validar_parametros(parametros)
    except ParametrosInvalidos as e:
        print(f"Los parámetros no valen: {e}")
        return None
    return parametros


def _resolver_integrante(cur, ws: str, nombre: str) -> list[dict]:
    """Empareja por subcadena, sin importar mayúsculas -- mismo punto de
    partida que `onboarding.generar_enlaces` con `--solo` (T7,
    `odd/tasks/leda-orienta.md`), pero además prefiere una coincidencia
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
            print(f"Incidentes registrados: {inc}  (python -m leda incidentes {slug})")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="leda")
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
                     help="ruta al YAML de datos ficticios (T7, odd/tasks/leda-orienta.md)")

    # `cadencia` y `escalera` corrían la cadencia y la escalera viejas, retiradas en la E3-7:
    # la escalera es la del motor (`escuchar`, `servir`) y las cadencias vuelven después de M3.
    des = sub.add_parser("despachar"); des.add_argument("slug")

    enl = sub.add_parser("enlaces")
    enl.add_argument("slug")
    enl.add_argument("--solo", nargs="*", help="nombres, para el piloto")

    adm = sub.add_parser("administrador")
    adm.add_argument("slug")
    adm.add_argument("nombre", help="nombre del integrante, entre comillas si tiene espacios")

    sub.add_parser("presentar").add_argument("slug")

    sub.add_parser("grupo").add_argument("slug")

    mod = sub.add_parser("modelo")
    mod.add_argument("nombre", nargs="?", help="identificador del modelo")
    mod.add_argument("--proveedor", default="gemini")
    mod.add_argument("--parametros", metavar="JSON",
                     help="parámetros del modelo (timeout_s, plazo_s, tope_jugadas, "
                          "tope_redaccion, cuerpo_extra...)")

    mds = sub.add_parser("modelos")   # pregunta al proveedor cuáles hay
    mds.add_argument("--proveedor", default="gemini")

    # La suscripción de ChatGPT (`leda.motor.chatgpt`): la sesión se guarda fuera del
    # repositorio y nunca se imprime.
    gpt = sub.add_parser("chatgpt", help="la sesión de la suscripción de ChatGPT")
    gpt.add_argument("accion", choices=("login", "estado", "salir"))
    gpt.add_argument("--manual", action="store_true",
                     help="sin servidor local: pegar la dirección a la que vuelve el navegador")
    sub.add_parser("estado").add_argument("slug")
    sub.add_parser("incidentes").add_argument("slug")

    sub.add_parser("escuchar").add_argument("slug")

    srv = sub.add_parser("servir")
    srv.add_argument("--puerto", type=int, default=8080)

    sub.add_parser("webhooks")

    a = p.parse_args(argv)

    if a.cmd == "esquema":
        # Sin psql: psycopg manda el archivo entero al servidor. Una sola
        # transacción, así que si algo falla no queda a medio aplicar.
        import psycopg

        sql = (config.raiz / "db" / "esquema.sql").read_text(encoding="utf-8")
        if a.recrear:
            sql = "drop schema if exists leda cascade;\n" + sql
        try:
            with psycopg.connect(config.db_url, autocommit=False) as c:
                c.execute(sql)
        except psycopg.OperationalError as e:
            print("No se pudo conectar a la base.")
            print(f"  {str(e).strip().splitlines()[0]}")
            print("\nRevisá LEDA_DB_URL en .env y que PostgreSQL esté corriendo.")
            return 1
        except psycopg.Error as e:
            print("La base rechazó el esquema:")
            print(f"  {str(e).strip().splitlines()[0]}")
            return 1
        print("Esquema aplicado.")
        return 0

    if a.cmd == "escuchar":
        # El escuchador del motor, por long polling: abre su propia conexión.
        from .motor.escucha import main as escuchar

        return escuchar([a.slug])

    if a.cmd == "servir":
        import uvicorn
        from .motor.fondo import montar

        conn_chequeo = conectar()
        try:
            codigo = _verificar_esquema_o_salir(conn_chequeo)
        finally:
            conn_chequeo.close()
        if codigo is not None:
            return codigo
        # El ciclo del motor (escalera, avisos guardados, despacho, mensajes sin respuesta)
        # para cada espacio activo con su bot, en un hilo de fondo (`leda.motor.fondo`).
        montar(lambda: conectar()).start()
        uvicorn.run("leda.entrada:app", host="0.0.0.0", port=a.puerto)
        return 0

    if a.cmd == "webhooks":
        # No necesita base: le dice a Telegram dónde entregar. Nunca imprime un token.
        from .entrada import registrar_webhooks

        try:
            resultado = registrar_webhooks()
        except LookupError as e:
            print(e)
            return 1
        if not resultado:
            print("No hay ningún bot configurado (LEDA_BOT_TOKEN_<ESPACIO>).")
            return 1
        for slug, ok in resultado.items():
            print(f"  {slug:16s} {'registrado' if ok else 'Telegram no lo aceptó'}")
        return 0 if all(resultado.values()) else 1

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

    if a.cmd == "chatgpt":
        # No necesita base ni el `.env`: la sesión vive fuera del repositorio.
        from .motor import chatgpt

        if a.accion == "login":
            return chatgpt.iniciar(manual=a.manual)
        if a.accion == "estado":
            return chatgpt.estado()
        return chatgpt.salir()

    if a.cmd == "modelos" and a.proveedor in PROVEEDORES_CON_SESION:
        # La suscripción no tiene una lista que se pueda pedir con una clave: la del catálogo
        # del cliente oficial de Codex.
        from .motor.chatgpt import MODELOS_CONOCIDOS

        for n in MODELOS_CONOCIDOS:
            print(f"  {n}")
        print("\nSon los del catálogo del cliente oficial de Codex. Elegí uno y corré:")
        print(f"  python -m leda modelo <identificador> --proveedor {a.proveedor}")
        return 0

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
        print(f"  python -m leda modelo <identificador> --proveedor {a.proveedor}")
        return 0

    if a.cmd == "modelo" and not a.nombre and a.parametros is not None:
        print("--parametros va con el identificador del modelo que se configura.")
        return 1
    if a.cmd == "modelo" and a.nombre:
        # Los mismos parámetros que lee el motor, revisados igual, antes de tocar la base: uno
        # que no vale no se guarda y el modelo activo queda como estaba.
        parametros = _parametros_del_modelo(a.parametros, a.proveedor)
        if parametros is None:
            return 1

    conn = conectar()

    if a.cmd == "modelo":
        with admin(conn) as cur:
            if not a.nombre:
                cur.execute(
                    "select proveedor, modelo, parametros, activo from model_config "
                    "where ambito = 'global'")
                filas = cur.fetchall()
                if not filas:
                    print("No hay modelo configurado.")
                    print("Ejemplo:  python -m leda modelo <identificador>")
                    return 1
                for f in filas:
                    marca = "activo" if f["activo"] else "inactivo"
                    print(f"  {f['proveedor']:12s} {f['modelo']:32s} {marca}"
                          + (f"  {json.dumps(f['parametros'], ensure_ascii=False)}"
                             if f["parametros"] else ""))
                return 0

            # Un solo modelo global activo por vez.
            cur.execute(
                "update model_config set activo = false where ambito = 'global'")
            cur.execute(
                """insert into model_config (ambito, proveedor, modelo, parametros, activo)
                   values ('global', %s, %s, %s, true)""",
                (a.proveedor, a.nombre, json.dumps(parametros)))
        conn.commit()
        print(f"Modelo configurado: {a.proveedor} / {a.nombre}")
        if parametros:
            print(f"  Parámetros: {json.dumps(parametros, ensure_ascii=False)}")
        if a.proveedor in PROVEEDORES_CON_SESION:
            # Sin clave: la sesión de la suscripción. Sólo se mira si hay una, nunca se muestra.
            from .motor.chatgpt import ruta_de_la_sesion

            try:
                hay_sesion = ruta_de_la_sesion().exists()
            except ValueError:
                hay_sesion = False
            if not hay_sesion:
                print("Ojo: no hay sesión de ChatGPT iniciada (python -m leda chatgpt login).")
        elif not config.clave_llm(a.proveedor):
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
                  "administración (LEDA_BOT_TOKEN_ADMIN) -- Telegram no "
                  "deja que un bot le escriba primero a quien nunca le "
                  "escribió, así que sin eso no hay a qué chat avisarle.")
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
            # de error, nunca su mensaje (T7b, `odd/tasks/leda-orienta.md`).
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

        if a.cmd == "despachar":
            from .despachador import TransporteTelegram, despachar
            transporte = TransporteTelegram(config.token_bot(a.slug))
            print(despachar(cur, ws, transporte, cal))

    conn.commit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
