"""Constancia administrativa neutral por espacio (rama auxiliar, G2c).

Lo que comparten los módulos de configuración por espacio (el alta con
correo, Google): el aviso administrativo deduplicado (`crear_aviso`,
`aviso_pendiente`) y la constancia de un valor de configuración corrupto
(`registrar_config_invalida`). Vive acá, sin depender de ningún módulo de
dominio, para que `google.credenciales` y `alta_correo` (y, después, el envío
del alta por Gmail) no formen un ciclo de importación. `alta_correo` los
reexporta con los mismos nombres.
"""

from __future__ import annotations

from datetime import datetime, timezone

import psycopg


def _ahora(valor: datetime | None) -> datetime:
    return valor or datetime.now(timezone.utc)


# Cuántas vueltas de "insertar o nada, si no está leer" tolera `crear_aviso`
# antes de rendirse (G1d-a3, ítem 5): dos alcanza en la práctica para
# cualquier carrera real (perder la carrera de inserción y no encontrar
# tampoco la fila del otro sólo pasa si alguien la resolvió justo en esa
# ventana angosta); una tercera vuelta es margen barato para una carrera
# encima de otra carrera, sin convertir esto en un reintento indefinido.
_MAX_INTENTOS_CREAR_AVISO = 3


def crear_aviso(cur: psycopg.Cursor, tipo: str, texto_saneado: str,
                 *, workspace_id: str | None = None,
                 referencia_tipo: str | None = None,
                 referencia_id: str | None = None,
                 ahora: datetime | None = None) -> str:
    """Crea un aviso administrativo -- o, si ya había uno igual y sin
    resolver, devuelve el id de ese (G1d, ítem 4: insertar o nada,
    garantizado por `aviso_administrativo_pendiente_unico` incluso bajo dos
    disparadores concurrentes del mismo aviso, no por el orden en que
    Python los ejecute).

    Dentro de `espacio()` el disparador `derivar_espacio_registro` fija el
    espacio desde la sesión y descarta lo que se pase acá -- igual que
    `audit_log` e `incident`. `workspace_id` sólo hace falta bajo una
    conexión de administración, donde no hay ningún espacio en la sesión.

    Sin referencia (`referencia_tipo`/`referencia_id` en `None`), el índice
    nunca colisiona -- Postgres trata cada `null` como distinto -- así que
    ese caso siempre inserta una fila nueva, como antes.

    El índice incluye `workspace_id` (G1d-a2, ítem 5): el mismo (tipo,
    referencia) en dos espacios distintos son dos avisos independientes,
    nunca uno pisando al otro.

    Nunca devuelve `None` ni revienta con `TypeError` (G1d-a2, ítem 5,
    hallazgo de la revisión): entre el "insertar o nada" que pierde la
    carrera y la lectura de abajo hay una ventana angosta en la que quien
    ganó la carrera puede haber marcado su aviso resuelto -- ahí ya no
    queda ningún pendiente vivo contra el que haber chocado, así que el
    próximo intento de este mismo bucle vuelve a insertar sin tropezar en
    vez de leer una fila que ya no está.

    Puede levantar `RuntimeError` (G1d-a3, ítem 5: antes esto no estaba
    dicho acá) si agota `_MAX_INTENTOS_CREAR_AVISO` intentos sin poder
    insertar ni encontrar ningún aviso pendiente -- una carrera inusualmente
    persistente, no un caso que quien llama deba esperar en el camino
    normal; nunca devuelve `None` en su lugar ni finge éxito."""
    ahora = _ahora(ahora)
    for _ in range(_MAX_INTENTOS_CREAR_AVISO):
        cur.execute(
            """insert into aviso_administrativo
                 (workspace_id, tipo, texto_saneado, referencia_tipo, referencia_id,
                  creado_en)
               values (%s, %s, %s, %s, %s, %s)
               on conflict (workspace_id, tipo, referencia_tipo, referencia_id)
                 where resuelto_en is null
               do nothing
               returning id""",
            (workspace_id, tipo, texto_saneado, referencia_tipo, referencia_id,
             ahora))
        fila = cur.fetchone()
        if fila is not None:
            return str(fila["id"])

        # Carrera perdida (o alguien se adelantó): ya hay uno pendiente
        # igual. `workspace_id` sólo filtra cuando quien llama lo dio
        # explícito (conexión de administración); dentro de `espacio()` la
        # RLS ya acota esto al espacio de la sesión.
        cur.execute(
            """select id from aviso_administrativo
                where (%s::uuid is null or workspace_id = %s)
                  and tipo = %s and referencia_tipo is not distinct from %s
                  and referencia_id is not distinct from %s and resuelto_en is null
                order by creado_en desc limit 1""",
            (workspace_id, workspace_id, tipo, referencia_tipo, referencia_id))
        fila = cur.fetchone()
        if fila is not None:
            return str(fila["id"])

    raise RuntimeError(
        "crear_aviso: no se pudo crear ni encontrar un aviso pendiente tras "
        "varios intentos (carrera inusual).")


def aviso_pendiente(cur: psycopg.Cursor, tipo: str, referencia_tipo: str,
                     referencia_id: str) -> bool:
    """`True` si ya hay un aviso de este tipo, sobre esta misma referencia,
    todavía sin resolver (G1b2, ítem 5: evita crear un segundo aviso
    idéntico mientras administración no marcó el anterior resuelto --
    "leído ≠ resuelto")."""
    cur.execute(
        """select 1 from aviso_administrativo
            where tipo = %s and referencia_tipo = %s and referencia_id = %s
              and resuelto_en is null
            limit 1""",
        (tipo, referencia_tipo, referencia_id))
    return cur.fetchone() is not None


def registrar_config_invalida(cur: psycopg.Cursor, workspace_id: str,
                              clave: str, trato: str, *, prefijo_aviso: str,
                              etapa: str) -> None:
    """Deja constancia de una configuración corrupta UNA vez mientras siga
    sin resolver: un aviso administrativo por espacio y clave hace de
    candado de deduplicación (`prisma_app` no puede leer `incident`), y
    recién cuando ese aviso es nuevo se registra el incidente. Así un valor
    roto no genera un incidente por cada mensaje que lo lee.

    Compartida con otros módulos de configuración por espacio (Google): cada
    uno pasa su propio `prefijo_aviso` y su propia `etapa`, para que el
    incidente nombre de dónde vino y no se confunda con el del correo."""
    tipo = f"{prefijo_aviso}:{clave}"
    if aviso_pendiente(cur, tipo, "workspace", workspace_id):
        return
    texto = (f"El valor guardado de {clave!r} no es válido -- se lo trató "
             f"como {trato}.")
    crear_aviso(cur, tipo, texto, workspace_id=workspace_id,
                referencia_tipo="workspace", referencia_id=workspace_id)
    from .incidentes import registrar_incidente

    registrar_incidente(cur, workspace_id, texto, severidad="media",
                        etapa=etapa)
