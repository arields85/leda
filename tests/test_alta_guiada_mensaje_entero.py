"""El alta guiada con la variante A escribe el mensaje ENTERO (ADR 0014, etapa 6
completa): el modelo recibe lo que entendió, lo que falta, el estado real y para
qué sirven las opciones, y devuelve un único mensaje; las plantillas sólo quedan
de respaldo. Los botones siguen saliendo del código.

El modelo de redacción se guiona con borradores JSON; el ruteo, con
`_RoutingProvider`. Ninguna prueba toca la red.
"""

from __future__ import annotations

import json
from datetime import timedelta

import pytest

from prisma import incidentes, redaccion
from prisma import ingreso_tareas as I
from prisma.db import admin, atar_al_entrante, espacio
from prisma.llm import ProveedorGuionado
from prisma.resultado_turno import Rechazo
from prisma.valores import TipoValor

from tests.test_alta_enviar_a_aprobacion import _alta_en_revision, _tocar, _fila, _acciones
from tests.test_alta_eleccion_confirmacion import _usuario
from tests.test_alta_guiada_flujo import (CHAT, TITULO, _alta_en_el_objetivo, _campo,
                                          _cuerpos, _decir_fecha, _empezar, _en_la_fecha,
                                          _escribir, _nuevas, _ruta, _salidas, _slot)
from tests.test_task_intake import NOW, _RoutingProvider, _actor, _callback_client


def _json(texto, pregunta=None, afirma=()):
    return json.dumps({"texto": texto, "pregunta": pregunta, "afirma": list(afirma)},
                      ensure_ascii=False)


class _Modelo(ProveedorGuionado):
    """El modelo de redacción: borradores JSON en orden; cada llamada deja sus
    hechos ya leídos en `hechos`."""

    def __init__(self, *borradores):
        super().__init__(guion=[], borradores=list(borradores))

    @property
    def hechos(self) -> list[dict]:
        return [json.loads(h) for _, h in self.redactados]

    def redactar(self, sistema, hechos, **_):
        return super().redactar(sistema, hechos)


class _Eco(_Modelo):
    """Un buen modelo mínimo: dice lo entendido, el rechazo y pide el dato con
    signos de pregunta, desde los hechos."""

    def redactar(self, sistema, hechos, **_):
        self.redactados.append((sistema, hechos))
        d = json.loads(hechos)
        if "resumen" in d:
            return _json("Listo, ya está el borrador. Revisalo:")
        partes = []
        if d.get("entendido"):
            partes.append("Anoté " + ", ".join(e["valor"] for e in d["entendido"]) + ".")
        if "rechazo" in d:
            partes.append(f"{d['rechazo']['razon']} {d['rechazo']['se_acepta']}")
        pregunta = None
        if "falta" in d:
            pregunta = d["falta"]["campo"]
            frase = d["falta"].get("pregunta") or "¿Cuál?"
            partes.append(frase if "?" in frase else frase + " ¿Cuál?")
        return _json(" ".join(partes), pregunta)


def _a(conn, ws, monkeypatch, modelo):
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, 'redaccion', %s::jsonb)
                       on conflict (workspace_id, clave)
                       do update set valor = excluded.valor""",
                    (ws, json.dumps({"variante": "A"})))
    conn.commit()
    monkeypatch.setattr(redaccion, "proveedor_de_redaccion",
                        lambda cur, workspace_id: modelo)


def _intentos(conn, ws) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select detalle from audit_log where workspace_id = %s "
                    "and accion = %s order by at", (ws, redaccion.ACCION_REDACCION_A))
        return [f["detalle"] for f in cur.fetchall()]


# ------------------------------------------------- la pregunta, entera, del modelo

def test_la_pregunta_sale_entera_del_modelo_con_lo_que_se_entendio(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    mensaje = (f"Tomé «{TITULO}» como título. Ahora decime de cuál de estos "
               "objetivos es, ¿cuál corresponde?")
    modelo = _Modelo(_json(mensaje, "objective"))
    _a(conn, ws, monkeypatch, modelo)

    with espacio(conn, ws) as cur:
        _, outcome = _empezar(cur, intake_world, title=TITULO)
        cuerpos = _cuerpos(cur, outcome.request_id)

    assert outcome.text == mensaje and cuerpos == [mensaje]     # una sola, del modelo
    (hechos,) = modelo.hechos
    assert hechos["entendido"] == [{"dato": "el título", "valor": TITULO}]
    assert hechos["falta"]["campo"] == "objective"
    assert hechos["falta"]["tipo"] == "opcion"
    # Las opciones llegan como contexto (sin íconos), nunca como acciones.
    assert any("Reduce service delay" in o for o in hechos["opciones"])
    assert all(o == o.strip() and not o.startswith(("📌", "⭐")) for o in hechos["opciones"])
    assert [i["resultado"] for i in _intentos(conn, ws)] == ["aceptada"]


def test_el_modelo_puede_nombrar_a_quien_escribe_y_a_prisma(
        intake_world, conn, monkeypatch):
    """Los nombres que el turno ya conoce (la persona, el asistente) no son
    "nombres inventados": el verificador los deja pasar sin que estén en los
    hechos (R-verificador). Los de otras personas siguen sin pasar."""
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        nombre = _actor(cur, intake_world).nombre
    mensaje = (f"Dale, {nombre}: tomé «{TITULO}» como título y Prisma sigue con "
               "vos. ¿De cuál de estos objetivos es?")
    modelo = _Modelo(_json(mensaje, "objective"))
    _a(conn, ws, monkeypatch, modelo)

    with espacio(conn, ws) as cur:
        _, outcome = _empezar(cur, intake_world, title=TITULO)
        cuerpos = _cuerpos(cur, outcome.request_id)

    assert cuerpos == [mensaje]
    assert [i["resultado"] for i in _intentos(conn, ws)] == ["aceptada"]


def test_un_nombre_de_otra_persona_sigue_rechazado(intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    modelo = _Modelo(_json(f"Dale, Zulema: tomé «{TITULO}» como título. "
                           "¿De cuál de estos objetivos es?", "objective"))
    _a(conn, ws, monkeypatch, modelo)
    with espacio(conn, ws) as cur:
        _empezar(cur, intake_world, title=TITULO)
    (intento,) = _intentos(conn, ws)
    assert intento["resultado"] == "rechazada"
    assert intento["motivo"].startswith("nombre_inventado")


def test_una_fecha_aceptada_llega_como_entendida_y_el_mensaje_la_dice(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, rid, _ = _en_la_fecha(cur, intake_world)
    modelo = _Modelo(_json(
        "Dejé la fecha para el 4 de octubre. ¿Cómo sabemos que la tarea quedó "
        "terminada?", "acceptance_criterion"))
    _a(conn, ws, monkeypatch, modelo)

    with espacio(conn, ws) as cur:
        # Otro turno: otro reloj (lo entendido es lo que cambió en ESTE turno).
        inbound = _entrante(cur, ws, actor)
        resultado = I.consume_pending_text(
            cur, actor, chat_id=CHAT, source_inbound_id=inbound,
            source_raw_text="el 4 de octubre", now=NOW + timedelta(minutes=1),
            valor={"fecha_iso": "2028-10-04"})

    assert resultado.text.startswith("Dejé la fecha para el 4 de octubre.")
    (hechos,) = modelo.hechos
    assert hechos["entendido"] == [{"dato": "la fecha objetivo", "valor": "04/10/2028"}]
    assert hechos["falta"]["campo"] == "acceptance_criterion"
    assert "opciones" not in hechos                  # una pregunta de texto


def _entrante(cur, ws, actor, texto="el 4 de octubre", n=830):
    from tests.test_alta_guiada_flujo import _entrante as e
    return e(cur, ws, actor, texto, n=n)


def test_lo_que_el_sistema_completa_solo_no_cuenta_como_entendido(
        intake_world, conn, monkeypatch):
    """La descripción vacía, la evidencia y un dato con una sola opción los
    completa el código: no son algo que la persona dijo."""
    ws = intake_world["north-lab"]["id"]
    modelo = _Eco()
    _a(conn, ws, monkeypatch, modelo)
    with espacio(conn, ws) as cur:
        _empezar(cur, intake_world, title=TITULO)
    (hechos,) = modelo.hechos
    assert [e["dato"] for e in hechos["entendido"]] == ["el título"]


# ------------------------------------------------- el rechazo y la pregunta, juntos

def test_un_rechazo_y_la_pregunta_salen_en_un_solo_mensaje_con_una_sola_llamada(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, rid, _ = _en_la_fecha(cur, intake_world)
    modelo = _Eco()
    _a(conn, ws, monkeypatch, modelo)

    with espacio(conn, ws) as cur:
        resultado = _decir_fecha(cur, intake_world, actor, rid, ws,
                                 {"fecha_iso": "2028-02-01"})   # ya pasó
        assert resultado.inert and _slot(cur, rid) == "due_date"
        assert _cuerpos(cur, rid).count(resultado.text) == 1

    assert len(modelo.redactados) == 1                          # no dos llamadas
    (hechos,) = modelo.hechos
    assert hechos["rechazo"]["razon"] == "Esa fecha ya pasó."
    assert hechos["falta"]["campo"] == "due_date"
    assert "Esa fecha ya pasó." in resultado.text and "¿" in resultado.text


def test_si_el_modelo_falla_el_rechazo_sale_como_el_de_b(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, rid, _ = _en_la_fecha(cur, intake_world)
    _a(conn, ws, monkeypatch, _Modelo(TimeoutError("colgado")))

    with espacio(conn, ws) as cur:
        resultado = _decir_fecha(cur, intake_world, actor, rid, ws,
                                 {"fecha_iso": "2028-02-01"})

    assert resultado.text == ("Esa fecha ya pasó. Decime una fecha desde hoy en "
                              "adelante.")
    assert [i["resultado"] for i in _intentos(conn, ws)] == ["timeout"]


def test_una_opcion_que_no_se_ofrecio_sale_en_un_solo_mensaje_con_sus_botones(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    user, rid = _alta_en_el_objetivo(conn, intake_world)
    modelo = _Eco()
    _a(conn, ws, monkeypatch, modelo)
    antes = _salidas(conn, user)

    _escribir(conn, monkeypatch, intake_world,
              _RoutingProvider([_ruta({"opcion_id": "9"})]), "la novena")

    (ultimo,) = _nuevas(conn, user, antes)
    assert ultimo["intake_choice_set_id"]                       # con sus botones
    assert "no está entre las que te ofrecí" in ultimo["cuerpo"]
    assert len(modelo.redactados) == 1
    (hechos,) = modelo.hechos
    assert hechos["falta"]["campo"] == "objective" and hechos["opciones"]
    assert hechos["rechazo"]["razon"].startswith("Esa opción no está")


def test_una_busqueda_sin_resultados_se_dice_como_rechazo_y_se_vuelve_a_preguntar(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    user, rid = _alta_en_el_objetivo(conn, intake_world)
    modelo = _Eco()
    _a(conn, ws, monkeypatch, modelo)
    antes = _salidas(conn, user)

    _escribir(conn, monkeypatch, intake_world,
              _RoutingProvider([_ruta({"opcion_id": "ninguna", "texto": "zzz"})]),
              "algo que no existe")

    (ultimo,) = _nuevas(conn, user, antes)
    assert ultimo["intake_choice_set_id"]
    (hechos,) = modelo.hechos
    assert "No encontré nada parecido a «zzz»" in hechos["rechazo"]["razon"]
    assert hechos["falta"]["pregunta"] == "¿A qué objetivo pertenece la tarea?"


# ------------------------------------------------- un efecto: sólo lo que ocurrió

def test_el_borrador_enviado_se_cuenta_como_un_efecto_del_resultado(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    rid, pid = _alta_en_revision(conn, intake_world)
    modelo = _Modelo(_json(
        "Listo, le mandé el borrador a Morgan Hale 1 para que lo confirme. La "
        "tarea se crea cuando lo confirme.", afirma=["borrador_enviado"]))
    _a(conn, ws, monkeypatch, modelo)

    client = _callback_client(conn, monkeypatch)
    _tocar(client, conn, _usuario(intake_world), pid, "Enviar a aprobación")

    (hechos,) = modelo.hechos
    assert [c["id"] for c in hechos["cambios"]] == ["borrador_enviado"]
    assert "Morgan Hale 1" in json.dumps(hechos, ensure_ascii=False)
    with admin(conn) as cur:
        cur.execute("""select cuerpo from message_outbox
                        where dedupe_key like %s""", (f"intake:{rid}:sent:%",))
        (fila,) = cur.fetchall()
    assert fila["cuerpo"].startswith("Listo, le mandé el borrador a Morgan Hale 1")


@pytest.mark.parametrize("borrador", [
    _json("Listo, le mandé el borrador y ya creé la tarea.",
          afirma=["borrador_enviado", "tarea_creada"]),     # un efecto que no hubo
    _json("Listo, le mandé el borrador a Morgan Hale 1.", afirma=[]),   # no lo declara
    TimeoutError("colgado"),
])
def test_si_el_texto_no_sirve_el_aviso_de_envio_es_el_de_siempre(
        borrador, intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    rid, pid = _alta_en_revision(conn, intake_world)
    _a(conn, ws, monkeypatch, _Modelo(borrador))

    client = _callback_client(conn, monkeypatch)
    _tocar(client, conn, _usuario(intake_world), pid, "Enviar a aprobación")

    with admin(conn) as cur:
        cur.execute("""select cuerpo from message_outbox
                        where dedupe_key like %s""", (f"intake:{rid}:sent:%",))
        (fila,) = cur.fetchall()
    assert fila["cuerpo"] == I.draft_sent_text("Morgan Hale 1")


# ------------------------------------------------- B no cambia

def test_con_b_el_modelo_no_se_llama_y_los_textos_son_los_de_siempre(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    modelo = _Eco()
    monkeypatch.setattr(redaccion, "proveedor_de_redaccion",
                        lambda cur, workspace_id: modelo)
    with espacio(conn, ws) as cur:
        actor, rid, _ = _en_la_fecha(cur, intake_world)
        resultado = _decir_fecha(cur, intake_world, actor, rid, ws,
                                 {"fecha_iso": "2028-02-01"})
        assert resultado.text == ("Esa fecha ya pasó. Decime una fecha desde hoy en "
                                  "adelante.")
    assert modelo.redactados == [] and _intentos(conn, ws) == []


# ------------------------------------------------- lo que se confirma, tal cual

CRITERIO = ("Acta de prueba firmada por el responsable de planta, con fotos del "
            "tablero antes y después de la intervención")


class _ModeloConCriterio(_Eco):
    """Un buen modelo en todo menos en la confirmación del criterio, que se
    guiona."""

    def __init__(self, *borradores):
        super().__init__()
        self.del_criterio = list(borradores)

    def redactar(self, sistema, hechos, **_):
        d = json.loads(hechos)
        if d.get("falta", {}).get("campo") == "acceptance_criterion":
            self.redactados.append((sistema, hechos))
            return self.del_criterio.pop(0)
        return super().redactar(sistema, hechos)


def _hasta_la_confirmacion_del_criterio(conn, world, monkeypatch, modelo):
    """El alta con un criterio propuesto por el mensaje: lo último que se
    contesta es la fecha y lo que sigue es "¿Confirmás este criterio?"."""
    ws = world["north-lab"]["id"]
    _a(conn, ws, monkeypatch, modelo)
    with espacio(conn, ws) as cur:
        actor, outcome = _empezar(cur, world, title=TITULO,
                                  acceptance_criterion=CRITERIO)
        rid = outcome.request_id
        from tests.test_alta_guiada_flujo import _elegir, _conjunto_activo
        _elegir(cur, actor, rid, "Reduce service delay")
        _elegir(cur, actor, rid, "Sam North")
        if _conjunto_activo(cur, rid) == "area":
            _elegir(cur, actor, rid, "Field Services")
        assert _slot(cur, rid) == "due_date"
        inbound = _entrante(cur, ws, actor)
        resultado = I.consume_pending_text(
            cur, actor, chat_id=CHAT, source_inbound_id=inbound,
            source_raw_text="el 4 de octubre", now=NOW + timedelta(minutes=2),
            valor={"fecha_iso": "2028-10-04"})
    return ws, resultado


def test_lo_que_se_pide_confirmar_sale_tal_cual_en_el_mensaje(
        intake_world, conn, monkeypatch):
    texto = (f"Dejé la fecha para el 4 de octubre. Tengo este criterio de "
             f"aceptación: {CRITERIO}. ¿Lo confirmás?")
    modelo = _ModeloConCriterio(_json(texto, "acceptance_criterion"))

    ws, resultado = _hasta_la_confirmacion_del_criterio(
        conn, intake_world, monkeypatch, modelo)

    assert resultado.text == texto
    hechos = modelo.hechos[-1]
    assert hechos["valores_aceptados"] == [
        {"dato": "el criterio de aceptación", "mostrado": CRITERIO}]
    assert hechos["falta"]["campo"] == "acceptance_criterion"


def test_si_el_mensaje_cambia_lo_que_se_confirma_sale_el_texto_de_siempre(
        intake_world, conn, monkeypatch):
    parafraseado = ("Dejé la fecha para el 4 de octubre. El criterio es un acta "
                    "firmada con fotos. ¿Lo confirmás?")
    modelo = _ModeloConCriterio(_json(parafraseado, "acceptance_criterion"))

    ws, resultado = _hasta_la_confirmacion_del_criterio(
        conn, intake_world, monkeypatch, modelo)

    assert resultado.text == f"¿Confirmás este criterio de aceptación? {CRITERIO}"
    motivos = [i.get("motivo", "") for i in _intentos(conn, ws)]
    assert any(m.startswith("falta_hecho") for m in motivos)


# ------------------------------------------- lo entendido en ESTE turno, robusto

def _alta_con_titulo(cur, world):
    actor, outcome = _empezar(cur, world, title=TITULO)
    cur.execute("select source_inbound_id::text i from task_intake_field "
                "where request_id = %s and campo = 'title'", (outcome.request_id,))
    return actor, outcome.request_id, cur.fetchone()["i"]


def _titulo_entendido(cur, rid, now=NOW):
    return [v.mostrado for v in I._entendido_del_turno(cur, rid, now)]


def test_lo_entendido_sale_del_mensaje_del_turno_aunque_la_hora_no_coincida(
        intake_world, conn):
    """Una hora distinta de la del turno (un reloj de la base, una escritura
    tardía) no deja al modelo sin saber lo que la persona acaba de decir."""
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        _, rid, inbound = _alta_con_titulo(cur, intake_world)
        cur.execute("update task_intake_field set actualizado_en = %s "
                    "where request_id = %s", (NOW - timedelta(seconds=7), rid))
        assert _titulo_entendido(cur, rid) == []               # sin turno atado
        atar_al_entrante(cur, inbound)
        assert _titulo_entendido(cur, rid) == [TITULO]


def test_lo_dicho_en_otro_mensaje_no_es_de_este_turno(intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        _, rid, _ = _alta_con_titulo(cur, intake_world)
        cur.execute("update task_intake_field set actualizado_en = %s "
                    "where request_id = %s", (NOW - timedelta(seconds=7), rid))
        atar_al_entrante(cur, "00000000-0000-0000-0000-00000000dead")
        assert _titulo_entendido(cur, rid) == []


def test_un_toque_sigue_leyendo_lo_confirmado_con_la_hora_del_turno(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        _, rid, _ = _alta_con_titulo(cur, intake_world)
        assert _titulo_entendido(cur, rid) == [TITULO]          # misma hora, sin atar


def test_un_dato_sin_sujeto_cae_a_b_sin_romper_y_queda_registrado(
        intake_world, conn, monkeypatch):
    """Si un campo confirmado en el turno no tiene cómo nombrarse, no es un
    `KeyError`: sale el texto de B, el modelo no se llama y queda un incidente."""
    ws = intake_world["north-lab"]["id"]
    modelo = _Modelo(_json("no debería salir", "objective"))
    _a(conn, ws, monkeypatch, modelo)
    with espacio(conn, ws) as cur:
        actor, rid, _ = _alta_con_titulo(cur, intake_world)
        llamadas = len(modelo.redactados)          # las del alta misma
        cur.execute("select * from task_intake_request where id = %s", (rid,))
        request = cur.fetchone()
        monkeypatch.delitem(I._SUJETO_DEL_CAMPO, "title")
        texto = I._decir_pregunta(cur, request, "objective", TipoValor.OPCION,
                                  "¿A qué objetivo pertenece la tarea?", NOW)
    assert texto == "¿A qué objetivo pertenece la tarea?"
    assert len(modelo.redactados) == llamadas
    with admin(conn) as cur:
        cur.execute("select referencia_cruda from incident where workspace_id = %s "
                    "and etapa = %s and referencia_cruda like 'campo:%%'",
                    (ws, incidentes.ETAPA_REDACCION_RECHAZADA))
        assert [f["referencia_cruda"] for f in cur.fetchall()] == ["campo: objective"]


def test_un_campo_sin_sujeto_no_se_redacta(intake_world, conn, monkeypatch):
    """La evidencia no tiene un sujeto para el modelo: B, sin `KeyError`."""
    ws = intake_world["north-lab"]["id"]
    modelo = _Modelo(_json("no debería salir"))
    _a(conn, ws, monkeypatch, modelo)
    with espacio(conn, ws) as cur:
        _, rid, _ = _alta_con_titulo(cur, intake_world)
        llamadas = len(modelo.redactados)
        cur.execute("select * from task_intake_request where id = %s", (rid,))
        texto = I._decir_pregunta(cur, cur.fetchone(), "evidence", TipoValor.TEXTO,
                                  "¿Qué evidencia vas a adjuntar?", NOW)
    assert texto == "¿Qué evidencia vas a adjuntar?"
    assert len(modelo.redactados) == llamadas


# ------------------- un rechazo con una elección cerrada no llama al modelo

def test_un_rechazo_sobre_una_eleccion_cerrada_no_llama_al_modelo(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    modelo = _Modelo(_json("no debería salir", "objective"))
    _a(conn, ws, monkeypatch, modelo)
    with espacio(conn, ws) as cur:
        actor, rid, _ = _alta_con_titulo(cur, intake_world)
        cur.execute("select id::text from task_intake_choice_set "
                    "where request_id = %s and estado = 'active'", (rid,))
        conjunto = cur.fetchone()["id"]
        cur.execute("select * from task_intake_request where id = %s", (rid,))
        request = cur.fetchone()
        cur.execute("update task_intake_choice_set set estado = 'invalidated' "
                    "where id = %s", (conjunto,))
        antes = len(_cuerpos(cur, rid))
        llamadas = len(modelo.redactados)
        resultado = I._rechazo_entero(
            cur, request, actor, "objective", Rechazo("No sirve.", "Elegí uno."),
            "No sirve.\n\n", None, conjunto, NOW)
        assert len(_cuerpos(cur, rid)) == antes                # no encola nada
        assert len(modelo.redactados) == llamadas
    assert resultado.inert and resultado.text == ""
