"""Lo retirado por la administración deja de contar, y Leda avisa (decisión 58 del usuario,
2026-10-10; porción 5b de la C-3; `leda.motor.retiro_de_la_administracion`).

- **A quien entregó la pieza**, si la tarea no está aprobada: que la administración la retiró,
  con el motivo, y, si la entrega en revisión quedó sin cubrir, lo que falta para que la
  revisen. Nunca el nombre de quien la retiró.
- **A quien revisa la tarea**, si está en revisión y quedó sin cubrir: que la entrega espera esa
  pieza nueva. Sin el motivo.
- **Una tarea aprobada no avisa a nadie.** Si al salir la entrega ya está completa otra vez, el
  aviso a quien revisa no sale (queda omitido, con su motivo).
- **Varias piezas a la vez, un aviso por persona.**
- Son avisos de coordinación del motor (mecánica §10), con los hechos de la cocina: los redacta
  la IA, salen dentro del horario y su envío queda auditado como todo envío de Leda.
- **La misma foto mandada otra vez** no se guarda: lo que llegó no se pudo recibir, con su motivo.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import timedelta

import pytest

from leda import pagina_de_tarea
from leda.autoridad import identificar_en_espacio
from leda.db import admin, espacio
from leda.motor import archivos, hechos
from leda.motor.ia import IAGuionada, Jugada
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import procesar_turno

from tests.motor.ayudantes import (AHORA, VIERNES_16, IAQueRedacta, avisos_guardados, enviar,
                                   todos, uno)

TIPOS = {"explicacion": {"clases": ["texto"], "en_palabras": "cómo quedó el trabajo"},
         "foto": {"clases": ["imagen"], "en_palabras": "una foto del trabajo terminado"}}
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01" + b"\x00" * 32 + b"\xff\xd9"
MOTIVO = "se ve una contraseña en la pantalla"
RETIRO = AHORA + timedelta(minutes=30)           # lunes, en horario
AL_SALIR = AHORA + timedelta(minutes=40)
A_QUIEN_LA_ENTREGO = "contenido_retirado_por_la_administracion"
A_QUIEN_LA_REVISA = "la_entrega_espera_otra_pieza"
EN_CADA_TAREA = "piezas_retiradas_por_tarea"
QUE_ESPERAN = "entregas_que_esperan_otra_pieza"


# --- Ayudas ---------------------------------------------------------------------------------

@pytest.fixture
def ada(conn, mundo) -> str:
    with admin(conn) as cur:
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (79201, 'Ada Admin') returning id""")
        usuario = str(cur.fetchone()["id"])
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                    (usuario,))
    conn.commit()
    return usuario


def _archivo(cur, mundo, contenido: bytes) -> str:
    """Una foto de Marcos, guardada una vez por huella."""
    huella = hashlib.sha256(contenido).hexdigest()
    cur.execute("select id from archivo where workspace_id = %s and sha256 = %s",
                (mundo["id"], huella))
    fila = cur.fetchone()
    if fila is not None:
        return str(fila["id"])
    cur.execute(
        """insert into archivo (workspace_id, contenido, sha256, tamano, tipo, clase,
                                nombre_original, enviado_por_membership_id, recibido_en)
           values (%s, %s, %s, %s, 'image/jpeg', 'imagen', 'tablero.jpg', %s, %s)
           returning id""",
        (mundo["id"], contenido, huella, len(contenido),
         mundo["personas"]["Marcos"]["membership_id"], AHORA))
    return str(cur.fetchone()["id"])


def _entregada(conn, mundo, titulo: str = "Armar el tablero", fotos=(JPEG,),
               estado: str = "en_revision", aviso_de_la_entrega: str = "enviado") -> dict:
    """Una tarea de Marcos que pide su explicación y una foto, entregada con lo que escribió y
    `fotos`, con el aviso de la entrega a Ismael en `aviso_de_la_entrega` (`guardado`: todavía
    no le llegó, por ejemplo dentro del margen para corregir). Las piezas, por clave: `texto`,
    `foto0`, `foto1`..."""
    marcos = mundo["personas"]["Marcos"]["membership_id"]
    with admin(conn) as cur:
        cur.execute("""insert into task_evidence_policy (workspace_id, area_id,
                                                         evidencia_requerida, tipos)
                       values (%s, %s, %s, %s)
                       on conflict (workspace_id, area_id) do nothing""",
                    (mundo["id"], mundo["area"], ["explicacion", "foto"], json.dumps(TIPOS)))
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, estado, fecha_objetivo,
                                 evidencia_requerida)
               values (%s, %s, %s, %s, %s, %s, %s, %s) returning id""",
            (mundo["id"], mundo["objetivo"], titulo, mundo["area"], marcos, estado, VIERNES_16,
             ["explicacion", "foto"]))
        tarea = str(cur.fetchone()["id"])
        piezas = {}
        cur.execute("""insert into evidence (workspace_id, task_id, tipo, clase, texto, cubre,
                                             entregado_por)
                       values (%s, %s, 'texto', 'texto', 'quedó armado', %s, %s)
                       returning id""", (mundo["id"], tarea, ["explicacion"], marcos))
        piezas["texto"] = str(cur.fetchone()["id"])
        for i, contenido in enumerate(fotos):
            cur.execute("""insert into evidence (workspace_id, task_id, tipo, clase, archivo_id,
                                                 cubre, entregado_por)
                           values (%s, %s, 'imagen', 'imagen', %s, %s, %s) returning id""",
                        (mundo["id"], tarea, _archivo(cur, mundo, contenido), ["foto"],
                         marcos))
            piezas[f"foto{i}"] = str(cur.fetchone()["id"])
        if estado == "en_revision":
            cur.execute(
                """insert into scheduled_notice (workspace_id, tipo, task_id,
                                                 destinatario_membership_id, hechos,
                                                 programado_para, estado, dedupe_key, creado_en,
                                                 resuelto_en)
                   values (%s, 'entrega_para_aprobar', %s, %s, '{}', %s, %s, %s, %s, %s)""",
                (mundo["id"], tarea, mundo["personas"]["Ismael"]["membership_id"], AHORA,
                 aviso_de_la_entrega, f"prueba:entrega:{tarea}", AHORA,
                 AHORA if aviso_de_la_entrega == "enviado" else None))
    conn.commit()
    return {"id": tarea, "titulo": titulo, "piezas": piezas}


def _retirar(conn, mundo, ada: str, pieza: str, motivo: str = MOTIVO) -> list[str]:
    with admin(conn) as cur:
        retiradas = pagina_de_tarea.retirar_contenido(cur, mundo["id"], pieza, ada, motivo,
                                                      ahora=RETIRO)
    conn.commit()
    return retiradas


def _avisos_del_retiro(conn) -> dict[str, list[dict]]:
    return {tipo: avisos_guardados(conn, tipo) for tipo in (A_QUIEN_LA_ENTREGO,
                                                            A_QUIEN_LA_REVISA)}


def _de(conn, mundo, avisos: list[dict]) -> list[str]:
    nombres = {p["membership_id"]: n for n, p in mundo["personas"].items()}
    return sorted(nombres[str(a["destinatario_membership_id"])] for a in avisos)


def _pedido_para(ia: IAQueRedacta, persona: str) -> dict:
    [pedido] = [p for p in ia.pedidos_de_redaccion if p["persona"] == persona]
    return pedido


# --- A quién le llega qué -------------------------------------------------------------------

def test_si_la_entrega_queda_sin_cubrir_se_enteran_quien_la_entrego_y_quien_la_revisa(
        conn, mundo, ada):
    tarea = _entregada(conn, mundo)
    assert _retirar(conn, mundo, ada, tarea["piezas"]["foto0"]) == [tarea["piezas"]["foto0"]]

    guardados = _avisos_del_retiro(conn)
    assert _de(conn, mundo, guardados[A_QUIEN_LA_ENTREGO]) == ["Marcos"]
    assert _de(conn, mundo, guardados[A_QUIEN_LA_REVISA]) == ["Ismael"]
    for aviso in guardados[A_QUIEN_LA_ENTREGO] + guardados[A_QUIEN_LA_REVISA]:
        assert str(aviso["task_id"]) == tarea["id"]
        assert aviso["programado_para"] == RETIRO

    ia = IAQueRedacta()
    assert enviar(conn, mundo, ia, AL_SALIR) == {"enviado": 2}

    a_marcos = _pedido_para(ia, "Marcos")
    [hecho] = a_marcos["hechos"]
    assert hecho["aviso"] == A_QUIEN_LA_ENTREGO
    assert hecho["motivo_del_retiro"] == MOTIVO
    [de_la_tarea] = hecho[EN_CADA_TAREA]
    assert de_la_tarea["tarea"] == "Armar el tablero"
    assert [(p["es"], p["cubria"]) for p in de_la_tarea["piezas_retiradas"]] == [
        ("una_foto", ["una foto del trabajo terminado"])]
    assert de_la_tarea["la_revision_espera_otra_pieza"] is True
    assert de_la_tarea["le_falta"] == ["una foto del trabajo terminado"]

    a_ismael = _pedido_para(ia, "Ismael")
    [hecho] = a_ismael["hechos"]
    assert hecho["aviso"] == A_QUIEN_LA_REVISA
    [de_la_tarea] = hecho[QUE_ESPERAN]
    assert de_la_tarea == {"tarea": "Armar el tablero", "responsable": "Marcos",
                           "le_falta": ["una foto del trabajo terminado"]}
    # El motivo es para quien la entregó; el nombre de quien la retiró, para nadie.
    assert MOTIVO not in json.dumps(a_ismael, ensure_ascii=False)
    for pedido in ia.pedidos_de_redaccion:
        assert "Ada" not in json.dumps(pedido, ensure_ascii=False)
        assert hechos.sin_significado(pedido["hechos"]) == set()

    # Avisos de coordinación (fuera del tope), cada uno con su envío auditado.
    salida = todos(conn, "select es_coordinacion from message_outbox where not es_respuesta")
    assert len(salida) == 2 and all(f["es_coordinacion"] for f in salida)
    assert uno(conn, "select count(*) n from audit_log where accion = 'enviar_aviso'")["n"] == 2


def test_a_quien_revisa_no_le_llega_si_todavia_no_recibio_la_entrega(conn, mundo, ada):
    """Decisión 60 del usuario (2026-10-10): si el retiro cae antes de que la entrega le llegue
    a quien revisa (dentro del margen para corregir), no le llega nada de una entrega que nunca
    vio; cuando quien la entregó mande la pieza nueva, le llega la entrega como siempre."""
    tarea = _entregada(conn, mundo, aviso_de_la_entrega="guardado")
    _retirar(conn, mundo, ada, tarea["piezas"]["foto0"])

    guardados = _avisos_del_retiro(conn)
    assert _de(conn, mundo, guardados[A_QUIEN_LA_ENTREGO]) == ["Marcos"]
    assert guardados[A_QUIEN_LA_REVISA] == []


def test_si_la_entrega_le_llego_a_otra_persona_a_quien_revisa_ahora_no_le_llega(conn, mundo,
                                                                                  ada):
    """Revisión de la decisión 60 (`retiro_de_la_administracion.py:143-149`): la última entrega
    le llegó a otra persona (quien revisaba antes): a quien revisa ahora no se le avisa de una
    entrega que nunca vio."""
    tarea = _entregada(conn, mundo)
    with admin(conn) as cur:
        cur.execute("""update scheduled_notice set destinatario_membership_id = %s
                        where dedupe_key = %s""",
                    (mundo["personas"]["Marcos"]["membership_id"],
                     f"prueba:entrega:{tarea['id']}"))
    conn.commit()
    _retirar(conn, mundo, ada, tarea["piezas"]["foto0"])

    guardados = _avisos_del_retiro(conn)
    assert _de(conn, mundo, guardados[A_QUIEN_LA_ENTREGO]) == ["Marcos"]
    assert guardados[A_QUIEN_LA_REVISA] == []


def test_si_la_entrega_sigue_cubierta_solo_se_entera_quien_la_entrego(conn, mundo, ada):
    tarea = _entregada(conn, mundo, fotos=(JPEG + b"1", JPEG + b"2"))
    _retirar(conn, mundo, ada, tarea["piezas"]["foto0"])

    guardados = _avisos_del_retiro(conn)
    assert _de(conn, mundo, guardados[A_QUIEN_LA_ENTREGO]) == ["Marcos"]
    assert guardados[A_QUIEN_LA_REVISA] == []

    ia = IAQueRedacta()
    assert enviar(conn, mundo, ia, AL_SALIR) == {"enviado": 1}
    [hecho] = _pedido_para(ia, "Marcos")["hechos"]
    [de_la_tarea] = hecho[EN_CADA_TAREA]
    assert "la_revision_espera_otra_pieza" not in de_la_tarea and "le_falta" not in de_la_tarea


def test_una_tarea_aprobada_no_avisa_a_nadie(conn, mundo, ada):
    tarea = _entregada(conn, mundo, estado="terminada")
    assert _retirar(conn, mundo, ada, tarea["piezas"]["foto0"]) == [tarea["piezas"]["foto0"]]
    assert _avisos_del_retiro(conn) == {A_QUIEN_LA_ENTREGO: [], A_QUIEN_LA_REVISA: []}


def test_una_aprobada_que_todavia_no_cerro_tampoco(conn, mundo, ada):
    """Quien la revisa ya la aprobó (falta otra cosa para cerrarla): está aprobada."""
    tarea = _entregada(conn, mundo)
    with admin(conn) as cur:
        cur.execute("""insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                             aprobador_membership_id, decision)
                       values (%s, 'tarea', %s, %s, 'aprobado')""",
                    (mundo["id"], tarea["id"], mundo["personas"]["Ismael"]["membership_id"]))
    conn.commit()
    _retirar(conn, mundo, ada, tarea["piezas"]["foto0"])
    assert _avisos_del_retiro(conn) == {A_QUIEN_LA_ENTREGO: [], A_QUIEN_LA_REVISA: []}


def test_varias_piezas_a_la_vez_un_aviso_por_persona(conn, mundo, ada):
    """La misma foto entregada en dos tareas es un solo archivo: retirarla retira las dos
    piezas, y cada persona recibe un solo aviso, con las dos tareas."""
    una = _entregada(conn, mundo, titulo="Armar el tablero")
    otra = _entregada(conn, mundo, titulo="Cablear el tablero")
    retiradas = _retirar(conn, mundo, ada, una["piezas"]["foto0"])
    assert set(retiradas) == {una["piezas"]["foto0"], otra["piezas"]["foto0"]}

    guardados = _avisos_del_retiro(conn)
    assert _de(conn, mundo, guardados[A_QUIEN_LA_ENTREGO]) == ["Marcos"]
    assert _de(conn, mundo, guardados[A_QUIEN_LA_REVISA]) == ["Ismael"]

    ia = IAQueRedacta()
    assert enviar(conn, mundo, ia, AL_SALIR) == {"enviado": 2}
    [hecho] = _pedido_para(ia, "Marcos")["hechos"]
    assert sorted(t["tarea"] for t in hecho[EN_CADA_TAREA]) == ["Armar el tablero",
                                                          "Cablear el tablero"]
    [hecho] = _pedido_para(ia, "Ismael")["hechos"]
    assert sorted(t["tarea"] for t in hecho[QUE_ESPERAN]) == ["Armar el tablero",
                                                          "Cablear el tablero"]


def test_fuera_del_horario_espera_a_la_jornada(conn, mundo, ada):
    tarea = _entregada(conn, mundo)
    _retirar(conn, mundo, ada, tarea["piezas"]["foto0"])
    ia = IAQueRedacta()
    noche = AHORA + timedelta(hours=10)                  # lunes, 20:00 en Buenos Aires
    assert enviar(conn, mundo, ia, noche) == {"fuera_de_horario": 1}
    assert ia.pedidos_de_redaccion == []
    assert enviar(conn, mundo, ia, AHORA + timedelta(days=1)) == {"enviado": 2}


def test_una_falla_al_guardar_los_avisos_sube_tal_cual(conn, mundo, monkeypatch):
    """Revisión de la porción 5b (`retiro_de_la_administracion.py:73-76`): si guardar los avisos
    falla, la transacción queda abortada y devolver el espacio en el `finally` fallaba también,
    tapando el error de verdad con otro (`InFailedSqlTransaction`). Sube el de verdad; el espacio
    vuelve solo con el rollback (`set_config` local a la transacción)."""
    import psycopg

    from leda.motor import retiro_de_la_administracion as retiro

    def se_cae(cur, *_a):
        cur.execute("select 1 / 0")

    monkeypatch.setattr(retiro, "_avisar", se_cae)
    with pytest.raises(psycopg.errors.DivisionByZero):
        with admin(conn) as cur:
            retiro.avisar(cur, mundo["id"], ["x"], MOTIVO, RETIRO)
    conn.rollback()


def test_si_sale_bien_el_espacio_vuelve_a_como_estaba(conn, mundo):
    from leda.motor import retiro_de_la_administracion as retiro

    with admin(conn) as cur:
        cur.execute("select set_config('leda.workspace_id', '', true)")
        assert retiro.avisar(cur, mundo["id"], [], MOTIVO, RETIRO) == 0
        cur.execute("select current_setting('leda.workspace_id', true) as ws")
        assert cur.fetchone()["ws"] == ""
    conn.rollback()


# --- La pieza nueva ---------------------------------------------------------------------------

def _manda_otra_foto_y_confirma(conn, mundo, contenido: bytes = JPEG + b"nueva") -> None:
    """Marcos manda otra foto para la tarea entregada y confirma la entrega por escrito."""
    persona = mundo["personas"]["Marcos"]
    for minuto, (jugada, archivo) in enumerate(
            ((Jugada("entregar", {"tarea": "T2"}), contenido), (Jugada("confirmar", {}), None)),
            start=50):
        at = AHORA + timedelta(minutes=minuto)
        with espacio(conn, mundo["id"]) as cur:
            quien = identificar_en_espacio(cur, persona["telegram"], mundo["id"])
            cur.execute(
                """insert into inbound_message (workspace_id, telegram_message_id, chat_id,
                                                app_user_id, texto, at)
                   values (%s, %s, %s, %s, %s, %s) returning id""",
                (mundo["id"], uuid.uuid4().int % 1_000_000, persona["telegram"],
                 persona["app_user_id"], "va otra" if archivo else "dale", at))
            entrante = str(cur.fetchone()["id"])
            if archivo is not None:
                archivo_id = archivos.guardar(
                    cur, workspace_id=mundo["id"], contenido=archivo,
                    tipo=archivos.Tipo("image/jpeg", archivos.IMAGEN), nombre="otra.jpg",
                    enviado_por=persona["membership_id"], ahora=at)
                archivos.anotar(cur, workspace_id=mundo["id"], entrante_id=entrante,
                                llegada=archivos.Llegada("foto", "f", "u", "otra.jpg", None, 1),
                                archivo_id=archivo_id)
        conn.commit()
        r = procesar_turno(conn, quien, entrante,
                           IAGuionada(jugadas=[[jugada]], redacciones=["Listo."]),
                           RelojFijo(at))
        conn.commit()
        assert r.error is None, r.error


def test_con_la_pieza_nueva_la_entrega_se_completa_y_el_aviso_a_quien_revisa_no_sale(
        conn, mundo, ada):
    tarea = _entregada(conn, mundo)
    _retirar(conn, mundo, ada, tarea["piezas"]["foto0"])
    _manda_otra_foto_y_confirma(conn, mundo)
    assert uno(conn, "select count(*) n from evidence where task_id = %s and clase = 'imagen'",
               tarea["id"])["n"] == 2

    # Pasada la media hora en que Marcos está conversando (decisión 13).
    ia = IAQueRedacta()
    enviar(conn, mundo, ia, AHORA + timedelta(minutes=85))
    [espera] = avisos_guardados(conn, A_QUIEN_LA_REVISA)
    assert espera["estado"] == "omitido"
    assert espera["motivo_omision"] == "la_entrega_ya_esta_completa"
    # A Marcos le llega igual que se retiró, sin pedirle nada más.
    [a_marcos] = avisos_guardados(conn, A_QUIEN_LA_ENTREGO)
    assert a_marcos["estado"] == "enviado"
    [hecho] = _pedido_para(ia, "Marcos")["hechos"]
    assert "le_falta" not in hecho[EN_CADA_TAREA][0]
    # Y quien la revisa recibe la entrega completa, como siempre (decisión 15).
    [entrega] = [a for a in avisos_guardados(conn, "entrega_para_aprobar")
                 if a["estado"] == "enviado" and not a["dedupe_key"].startswith("prueba:")]
    assert str(entrega["destinatario_membership_id"]) == \
        mundo["personas"]["Ismael"]["membership_id"]


def test_si_la_primera_entrega_nunca_le_llego_con_la_pieza_nueva_le_llega_completa(conn, mundo,
                                                                                    ada):
    """Decisión 60, la segunda mitad (revisión de `dbb03cf`): el retiro cae antes de que la
    entrega le llegue a quien revisa; a Ismael no le llega nada del retiro, y cuando Marcos manda
    la pieza nueva, le llega la entrega completa, una sola vez."""
    tarea = _entregada(conn, mundo, aviso_de_la_entrega="guardado")
    _retirar(conn, mundo, ada, tarea["piezas"]["foto0"])
    assert _avisos_del_retiro(conn)[A_QUIEN_LA_REVISA] == []
    # Al salir, la entrega incompleta no sale (decisión 15); a Marcos le llega el retiro.
    assert enviar(conn, mundo, IAQueRedacta(), AL_SALIR) == {
        "enviado": 1, "omitido": 1}
    [primera] = [a for a in avisos_guardados(conn, "entrega_para_aprobar")]
    assert primera["estado"] == "omitido"
    _manda_otra_foto_y_confirma(conn, mundo)

    enviar(conn, mundo, IAQueRedacta(), AHORA + timedelta(minutes=85))
    entregas = [a for a in avisos_guardados(conn, "entrega_para_aprobar")
                if not a["dedupe_key"].startswith("prueba:")]
    [entrega] = [a for a in entregas if a["estado"] == "enviado"]
    assert str(entrega["destinatario_membership_id"]) == \
        mundo["personas"]["Ismael"]["membership_id"]
    assert avisos_guardados(conn, A_QUIEN_LA_REVISA) == []


# --- Lo retirado no vuelve -------------------------------------------------------------------

def test_la_misma_foto_mandada_otra_vez_no_se_guarda(conn, mundo, ada):
    tarea = _entregada(conn, mundo)
    _retirar(conn, mundo, ada, tarea["piezas"]["foto0"])
    with espacio(conn, mundo["id"]) as cur:
        with pytest.raises(archivos.Rechazo) as rechazo:
            archivos.guardar(cur, workspace_id=mundo["id"], contenido=JPEG,
                             tipo=archivos.Tipo("image/jpeg", archivos.IMAGEN), nombre="x.jpg",
                             enviado_por=mundo["personas"]["Marcos"]["membership_id"],
                             ahora=AL_SALIR)
    conn.rollback()
    assert rechazo.value.motivo == archivos.CONTENIDO_RETIRADO
    assert hechos.significado(archivos.CONTENIDO_RETIRADO) is not None
    # Lo que le dice el turno: no se pudo recibir, y qué puede hacer en cambio.
    from leda.motor.turno import EN_CAMBIO_PUEDE
    assert all(hechos.significado(c) for c in EN_CAMBIO_PUEDE[archivos.CONTENIDO_RETIRADO])


def test_la_misma_foto_por_telegram_queda_rechazada_y_la_ia_lo_sabe(conn, mundo, ada):
    """Revisión de la porción 5b (`recibir.py:531-538`, sin prueba): por la entrada de verdad
    (bajar, revisar, guardar), la foto cuyo contenido retiró la administración no se guarda: el
    mensaje queda con su rechazo y la IA sabe que no se pudo recibir, con qué puede hacer."""
    from tests.motor.test_archivos import Bajadas, _foto, _recepcion, _recibir

    tarea = _entregada(conn, mundo)
    _retirar(conn, mundo, ada, tarea["piezas"]["foto0"])
    ia = IAGuionada(jugadas=[[]], redacciones=["Esa foto no la puedo recibir."])

    _recibir(_recepcion(conn, mundo, ia, Bajadas({"F9": JPEG})),
             _foto(990, "F9", contenido=JPEG))

    atado = uno(conn, "select archivo_id, rechazo from archivo_de_mensaje")
    assert (atado["archivo_id"], atado["rechazo"]) == (None, archivos.CONTENIDO_RETIRADO)
    assert uno(conn, "select count(*) n from archivo where contenido is not null")["n"] == 0
    [llego] = ia.pedidos_de_jugadas[0]["archivos"]
    assert llego["no_se_pudo_recibir"] == archivos.CONTENIDO_RETIRADO


def test_la_base_acepta_el_motivo_de_un_rechazo_por_contenido_retirado(conn, mundo):
    with espacio(conn, mundo["id"]) as cur:
        cur.execute(
            """insert into inbound_message (workspace_id, telegram_message_id, chat_id,
                                            app_user_id, texto)
               values (%s, 1, %s, %s, '') returning id""",
            (mundo["id"], mundo["personas"]["Marcos"]["telegram"],
             mundo["personas"]["Marcos"]["app_user_id"]))
        entrante = str(cur.fetchone()["id"])
        archivos.anotar(cur, workspace_id=mundo["id"], entrante_id=entrante,
                        llegada=archivos.Llegada("foto", "f", "u", None, None, 1),
                        rechazo=archivos.CONTENIDO_RETIRADO)
    conn.commit()
    assert uno(conn, "select rechazo from archivo_de_mensaje")["rechazo"] == \
        archivos.CONTENIDO_RETIRADO


def test_un_archivo_retirado_no_entra_en_una_entrega(conn, mundo, ada):
    """Ni por la cocina: una pieza que apunta a un archivo cuyo contenido se retiró es un
    error, como un archivo que no existe."""
    from leda import herramientas

    tarea = _entregada(conn, mundo)
    archivo = uno(conn, "select archivo_id from evidence where id = %s",
                  tarea["piezas"]["foto0"])["archivo_id"]
    _retirar(conn, mundo, ada, tarea["piezas"]["foto0"])
    persona = mundo["personas"]["Marcos"]
    with espacio(conn, mundo["id"]) as cur:
        quien = identificar_en_espacio(cur, persona["telegram"], mundo["id"])
        r = herramientas.ejecutar(cur, quien, "entregar_tarea", {
            "tarea_id": tarea["id"],
            "piezas": [{"archivo_id": str(archivo), "cubre": ["foto"]}]},
            ya_confirmada=True)
    conn.commit()
    assert r == {"en_revision": False, "error": "pieza inválida: archivo"}
    assert uno(conn, "select count(*) n from evidence where task_id = %s and clase = 'imagen'",
               tarea["id"])["n"] == 1
