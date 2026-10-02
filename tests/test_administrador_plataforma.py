"""CLI para designar administradores de plataforma (T11).

Hasta esta unidad, nadie podía llegar a ser "alcanzable"
(`db/esquema.sql`, `avisar_incidente_admin`) en desarrollo local: ningún
comando otorgaba `platform_role`, sólo lo insertaban las pruebas a mano.
`python -m leda administrador <slug> <nombre>` resuelve a la persona por
nombre entre los integrantes del espacio -- mismo punto de partida que
`enlaces --solo` (emparejar por subcadena, `cli._resolver_integrante`), pero
además prefiere una coincidencia exacta sobre cualquier coincidencia
parcial, cosa que `--solo` no hace -- y le otorga el rol de forma
idempotente (`on conflict do nothing`), auditando sólo la vez que de verdad
se otorga.

Cubre: coincidencia única otorga y audita; nombre ambiguo y nombre
inexistente no otorgan nada y salen con código distinto de cero; una
segunda corrida es idempotente (no duplica el rol ni la auditoría); y la
persona sin Telegram vinculado igual recibe el rol, con una advertencia de
que los avisos no le van a llegar todavía.
"""

from __future__ import annotations

import leda.cli as cli
from leda.db import admin


def test_cli_administrador_otorga_y_audita_con_coincidencia_unica(
        corework, conn, monkeypatch, capsys):
    monkeypatch.setattr(cli, "conectar", lambda: conn)

    codigo = cli.main(["administrador", "corework", "Nahuel Gimenez"])

    assert codigo == 0
    salida = capsys.readouterr().out
    assert "Nahuel Gimenez" in salida
    assert "otorgado" in salida
    # El fixture `corework` ya vincula a todo el mundo (telegram_user_id):
    # el mensaje tiene que ser el de "ya puede recibir avisos", no la
    # advertencia de Telegram sin vincular.
    assert "Todavía no vinculó" not in salida

    with admin(conn) as cur:
        cur.execute(
            """select p.rol from platform_role p
                 join app_user u on u.id = p.app_user_id
                where u.nombre = 'Nahuel Gimenez'""")
        filas = cur.fetchall()
        assert [f["rol"] for f in filas] == ["administrador"]

        cur.execute(
            """select actor_kind, sujeto_tipo, sujeto_id, detalle
                 from audit_log where accion = 'otorgar_administrador'""")
        auditoria = cur.fetchall()

    assert len(auditoria) == 1
    fila = auditoria[0]
    assert fila["actor_kind"] == "sistema"
    assert fila["sujeto_tipo"] == "app_user"
    assert fila["detalle"] == {"nombre": "Nahuel Gimenez"}


def test_cli_administrador_nombre_ambiguo_no_otorga_nada(corework, conn, monkeypatch, capsys):
    monkeypatch.setattr(cli, "conectar", lambda: conn)

    # "Mar" empareja a Martín Forte, Marcos Tarquini y Mariano Naim -- las
    # tres personas de `espacios/corework.yaml` cuyo nombre empieza así.
    codigo = cli.main(["administrador", "corework", "Mar"])

    assert codigo == 1
    salida = capsys.readouterr().out
    assert "ambiguo" in salida
    assert "Martín Forte" in salida
    assert "Marcos Tarquini" in salida
    assert "Mariano Naim" in salida

    with admin(conn) as cur:
        cur.execute("select count(*) as n from platform_role")
        assert cur.fetchone()["n"] == 0
        cur.execute(
            "select count(*) as n from audit_log where accion = 'otorgar_administrador'")
        assert cur.fetchone()["n"] == 0


def test_cli_administrador_prefiere_la_coincidencia_exacta(corework, conn, monkeypatch, capsys):
    """Designa un rol privilegiado: un nombre exacto no es ambiguo aunque el
    mismo fragmento aparezca en otros nombres."""
    monkeypatch.setattr(cli, "conectar", lambda: conn)
    with admin(conn) as cur:
        cur.execute("update app_user set nombre = 'Mar' where nombre = 'Martín Forte'")
    conn.commit()

    codigo = cli.main(["administrador", "corework", "mar"])

    assert codigo == 0
    with admin(conn) as cur:
        cur.execute(
            """select u.nombre from platform_role p
                 join app_user u on u.id = p.app_user_id""")
        assert [f["nombre"] for f in cur.fetchall()] == ["Mar"]


def test_cli_administrador_nombre_inexistente_no_otorga_nada(corework, conn, monkeypatch, capsys):
    monkeypatch.setattr(cli, "conectar", lambda: conn)

    codigo = cli.main(["administrador", "corework", "Persona Que No Existe"])

    assert codigo == 1
    salida = capsys.readouterr().out
    assert "No encontré a nadie" in salida

    with admin(conn) as cur:
        cur.execute("select count(*) as n from platform_role")
        assert cur.fetchone()["n"] == 0


def test_cli_administrador_es_idempotente(corework, conn, monkeypatch, capsys):
    monkeypatch.setattr(cli, "conectar", lambda: conn)

    primero = cli.main(["administrador", "corework", "Ismael Soschinski"])
    assert primero == 0
    assert "otorgado" in capsys.readouterr().out

    segundo = cli.main(["administrador", "corework", "Ismael Soschinski"])
    assert segundo == 0
    salida_segunda = capsys.readouterr().out
    assert "ya lo era" in salida_segunda

    with admin(conn) as cur:
        cur.execute(
            """select count(*) as n from platform_role p
                 join app_user u on u.id = p.app_user_id
                where u.nombre = 'Ismael Soschinski'""")
        assert cur.fetchone()["n"] == 1  # la segunda corrida no duplicó el rol

        cur.execute(
            "select count(*) as n from audit_log where accion = 'otorgar_administrador'")
        assert cur.fetchone()["n"] == 1  # ni la auditoría: sólo se audita lo que de verdad se otorga


def test_cli_administrador_sin_telegram_vinculado_igual_otorga_pero_avisa(
        corework, conn, monkeypatch, capsys):
    """Requisito A: alguien que nunca activó su cuenta (`enlaces`) igual
    puede ser designado -- el rol no depende de `telegram_user_id` -- pero
    los avisos de incidente no le van a llegar hasta que la active y le
    escriba una vez al bot de administración (`avisar_incidente_admin`
    exige `telegram_user_id` para siquiera identificarlo, y un `chat_id`
    real de `mensaje_admin` para saber a dónde mandarle algo)."""
    monkeypatch.setattr(cli, "conectar", lambda: conn)

    with admin(conn) as cur:
        cur.execute(
            "update app_user set telegram_user_id = null where nombre = 'Mariano Naim'")
    conn.commit()

    codigo = cli.main(["administrador", "corework", "Mariano Naim"])

    assert codigo == 0
    salida = capsys.readouterr().out
    assert "otorgado" in salida
    assert "Todavía no vinculó" in salida

    with admin(conn) as cur:
        cur.execute(
            """select count(*) as n from platform_role p
                 join app_user u on u.id = p.app_user_id
                where u.nombre = 'Mariano Naim'""")
        assert cur.fetchone()["n"] == 1
