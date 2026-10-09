"""El indicador de actividad y la respuesta que se ve mientras la IA la escribe
(`despachador.mantener_chat_activo`; ADR 0011, decisión 2).

Pedido del usuario (2026-10-07): traer de la rama congelada lo que ya funcionó en Telegram
real, el "escribiendo…", los tres puntos del borrador nativo sembrado con un carácter invisible
y el texto de la respuesta que aparece mientras la IA lo escribe. El borrador es efímero: no
pasa por el outbox ni se audita.

Pedido del usuario (2026-10-07): "La función del escribiendo y el '…' es mostrar que Leda está
activa, no generar demora en la respuesta." Cuando sigue un mensaje (`sigue_la_respuesta`), el
mensaje de verdad, el del outbox, es el que reemplaza al borrador (Bot API, `sendMessageDraft`:
el borrador es una vista previa efímera, y al terminar se manda el mensaje con `sendMessage`):
cerrar el indicador no espera nada ni retira nada. Sólo un turno sin mensaje retira el borrador.
Telegram es un cliente HTTP falso que guarda cada llamada; nada sale a la red.
"""

from __future__ import annotations

import threading
import time

from leda.despachador import SEMILLA_INDICADOR, mantener_chat_activo

CHAT = 123


class Respuesta:
    def __init__(self, cliente: "TelegramDeMentira", url: str, codigo: int = 200,
                 cuerpo: dict | None = None) -> None:
        self._cliente, self._url = cliente, url
        self.status_code = codigo
        self._cuerpo = cuerpo

    def raise_for_status(self):
        return None

    def json(self):
        if self._cuerpo is not None:
            return self._cuerpo
        if self._url.endswith("/sendMessage"):
            self._cliente.siguiente_id += 1
            return {"ok": True, "result": {"message_id": self._cliente.siguiente_id}}
        return {"ok": True, "result": True}


class TelegramDeMentira:
    """El cliente HTTP del indicador, de mentira: guarda cada llamada en orden. `falla_en` hace
    fallar los métodos nombrados; `ritmo` contesta un 429 a los primeros borradores con texto."""

    def __init__(self, falla_en: frozenset[str] = frozenset(), ritmo: int = 0,
                 borrador_lento: float = 0.0) -> None:
        self.llamadas: list[tuple[str, dict]] = []
        self.horas: list[float] = []          # cuándo empezó cada llamada (`time.monotonic`)
        self.vueltas: list[tuple[str, float]] = []    # cuándo volvió cada una
        self.falla_en = falla_en
        self.ritmo = ritmo
        # Un borrador con texto queda en vuelo hasta `borrador_lento` segundos, o hasta `soltar`.
        self.borrador_lento = borrador_lento
        self.borrador_en_vuelo = threading.Event()
        self.soltar = threading.Event()
        self.siguiente_id = 900
        self._candado = threading.RLock()     # los predicados de `esperar` lo vuelven a tomar
        self._hubo = threading.Condition(self._candado)

    def post(self, url, json=None):
        metodo = url.rsplit("/", 1)[-1]
        with self._hubo:
            self.llamadas.append((metodo, dict(json or {})))
            self.horas.append(time.monotonic())
            self._hubo.notify_all()
        if metodo in self.falla_en:
            raise ConnectionError("fallo simulado")
        if (metodo == "sendMessageDraft" and self.borrador_lento
                and (json or {}).get("text") != SEMILLA_INDICADOR):
            self.borrador_en_vuelo.set()
            self.soltar.wait(self.borrador_lento)
        with self._hubo:
            self.vueltas.append((metodo, time.monotonic()))
            self._hubo.notify_all()
        if (metodo == "sendMessageDraft" and (json or {}).get("text") != SEMILLA_INDICADOR
                and self.ritmo > 0):
            self.ritmo -= 1
            return Respuesta(self, url, 429, {"ok": False, "parameters": {"retry_after": 0.05}})
        return Respuesta(self, url)

    def metodos(self) -> list[str]:
        with self._candado:
            return [m for m, _ in self.llamadas]

    def borradores_con_texto(self) -> list[str]:
        with self._candado:
            return [p["text"] for m, p in self.llamadas
                    if m == "sendMessageDraft" and p["text"] != SEMILLA_INDICADOR]

    def esperar(self, condicion, timeout: float = 2.0) -> bool:
        with self._hubo:
            return self._hubo.wait_for(condicion, timeout)


def _indicador(telegram, **opciones):
    """Sin umbral por omisión, salvo que la prueba lo pida: el texto llega antes."""
    return mantener_chat_activo("token-prueba", CHAT, cliente=telegram,
                                **{"chat_type": "private", "umbral": 10.0, "intervalo": 10.0,
                                   "intervalo_borrador": 0.2, **opciones})


def test_el_borrador_muestra_el_texto_que_crece_sin_un_pedido_por_letra():
    telegram = TelegramDeMentira()
    with _indicador(telegram) as indicador:
        indicador.actualizar_borrador("Ho")
        assert telegram.esperar(lambda: telegram.borradores_con_texto() == ["Ho"])
        for parcial in ("Hol", "Hola", "Hola, M", "Hola, Marcos."):
            indicador.actualizar_borrador(parcial)
        assert telegram.esperar(lambda: telegram.borradores_con_texto()[-1:] == ["Hola, Marcos."])

    # El primero sale enseguida; lo que llega antes del intervalo se junta y sale lo último.
    assert telegram.borradores_con_texto() == ["Ho", "Hola, Marcos."]
    borradores = [p for m, p in telegram.llamadas if m == "sendMessageDraft"]
    assert len({p["draft_id"] for p in borradores}) == 1        # siempre el mismo borrador
    # Con texto en el borrador, la semilla ya no se manda: lo taparía.
    assert all(p["text"] != SEMILLA_INDICADOR for p in borradores)


def test_las_marcas_del_formato_no_se_ven_en_el_borrador():
    """El borrador es texto plano: las negritas llegan con el mensaje de verdad."""
    telegram = TelegramDeMentira()
    with _indicador(telegram, intervalo_borrador=0.0) as indicador:
        indicador.actualizar_borrador("Tu tarea **Revisar el tablero** vence hoy.\n- uno\n- **dos")
        assert telegram.esperar(lambda: telegram.borradores_con_texto())

    [texto] = telegram.borradores_con_texto()
    assert texto == "Tu tarea Revisar el tablero vence hoy.\n• uno\n• dos"


def _respuesta_de_verdad(telegram: TelegramDeMentira, texto: str = "Anoté que arrancaste."):
    """Lo que hace el despacho del outbox después del turno: el mensaje de verdad, con
    `sendMessage` (`despachador.TransporteTelegram`), por el mismo cliente."""
    telegram.post("https://api.telegram.org/bottoken-prueba/sendMessage",
                  json={"chat_id": CHAT, "text": texto, "disable_notification": False})


def _hilos_del_indicador() -> set[threading.Thread]:
    return {h for h in threading.enumerate()
            if h.name in ("leda-typing", "leda-borrador") and h.is_alive()}


def _sin_hilos_nuevos(antes: set[threading.Thread], timeout: float = 1.0) -> bool:
    """Ningún hilo del indicador que haya nacido en la prueba sigue vivo (acotado)."""
    limite = time.monotonic() + timeout
    while time.monotonic() < limite:
        if not (_hilos_del_indicador() - antes):
            return True
        time.sleep(0.01)
    return False


def test_si_sigue_la_respuesta_lo_proximo_es_el_mensaje_de_verdad_sin_retiro():
    """Pedido del usuario (2026-10-07): el indicador no demora la respuesta. Después de la
    redacción, lo próximo que le llega a Telegram por ese chat es el `sendMessage` de la
    respuesta: ni el mensaje silencioso de la semilla, ni su borrado, ni otro "escribiendo…",
    ni otro borrador. Y ningún borrador sale después de la respuesta."""
    telegram = TelegramDeMentira()
    antes = _hilos_del_indicador()
    with _indicador(telegram, umbral=0.0) as indicador:
        assert telegram.esperar(lambda: "sendChatAction" in telegram.metodos())
        indicador.actualizar_borrador("Anoté que arrancaste.")
        assert telegram.esperar(lambda: telegram.borradores_con_texto())
        redactado = len(telegram.llamadas)          # la redacción terminó acá
        indicador.sigue_la_respuesta()
    _respuesta_de_verdad(telegram)
    indicador.actualizar_borrador("Anoté que arrancaste. Y algo más")    # tarde: no sale
    time.sleep(0.3)

    assert telegram.metodos()[redactado:] == ["sendMessage"]
    [final] = [p for m, p in telegram.llamadas if m == "sendMessage"]
    assert final["text"] == "Anoté que arrancaste." and final["disable_notification"] is False
    assert "deleteMessage" not in telegram.metodos()
    assert _sin_hilos_nuevos(antes)


def test_despues_del_mensaje_el_borrador_se_retira_sin_otro_escribiendo():
    """Prueba por Telegram del 2026-10-08 (D8): los tres puntos quedaban a la vista, porque el
    mensaje de verdad no siempre reemplaza al borrador. Después de que salió, quien lo despachó
    pide el retiro (`retirar_tras_la_respuesta`): la semilla como mensaje silencioso y su
    borrado, como en un turno sin mensaje, pero sin otro "escribiendo…" (ya no hay nada que
    esperar). Una sola vez."""
    telegram = TelegramDeMentira()
    antes = _hilos_del_indicador()
    with _indicador(telegram) as indicador:
        indicador.actualizar_borrador("Anoté que arrancaste.")
        assert telegram.esperar(lambda: telegram.borradores_con_texto())
        indicador.sigue_la_respuesta()
    redactado = len(telegram.llamadas)
    _respuesta_de_verdad(telegram)

    assert indicador.retirar_tras_la_respuesta() is None
    assert indicador.retirar_tras_la_respuesta() is None        # ya no queda nada

    assert telegram.metodos()[redactado:] == ["sendMessage", "sendMessage", "deleteMessage"]
    final, semilla = [p for m, p in telegram.llamadas if m == "sendMessage"]
    assert final["text"] == "Anoté que arrancaste."
    assert semilla["text"] == SEMILLA_INDICADOR and semilla["disable_notification"] is True
    assert _sin_hilos_nuevos(antes)


def test_el_borrador_en_vuelo_vuelve_antes_de_que_salga_el_mensaje():
    """D8: un envío del borrador en vuelo al cerrar podía llegarle a Telegram después del
    mensaje y volver a mostrar el borrador. El cierre espera a que vuelva (es un pedido ya en
    vuelo, no un retiro antes del mensaje), así que el mensaje sale después."""
    telegram = TelegramDeMentira(borrador_lento=0.3)
    antes = _hilos_del_indicador()
    with _indicador(telegram, intervalo_borrador=0.0) as indicador:
        indicador.actualizar_borrador("Anoté que arrancaste.")
        assert telegram.borrador_en_vuelo.wait(1.0)
        indicador.sigue_la_respuesta()
    _respuesta_de_verdad(telegram)

    [(_, volvio)] = [v for v in telegram.vueltas if v[0] == "sendMessageDraft"]
    enviado = telegram.horas[telegram.metodos().index("sendMessage")]
    assert enviado >= volvio
    assert telegram.metodos() == ["sendMessageDraft", "sendMessage"]
    assert _sin_hilos_nuevos(antes)


def test_un_borrador_colgado_no_retiene_el_cierre_mas_que_su_tope():
    """Un envío del borrador que no vuelve: el cierre espera sólo hasta `timeout_borrador` y el
    mensaje sale igual. El retiro de después tampoco se arriesga a llegar antes que ese borrador:
    no se hace, y la falla vuelve para que quien despachó deje el incidente."""
    telegram = TelegramDeMentira(borrador_lento=3.0)
    try:
        with _indicador(telegram, intervalo_borrador=0.0, timeout_borrador=0.2) as indicador:
            indicador.actualizar_borrador("Anoté que arrancaste.")
            assert telegram.borrador_en_vuelo.wait(1.0)
            cerrando = time.monotonic()
            indicador.sigue_la_respuesta()
        assert time.monotonic() - cerrando < 1.0

        falla = indicador.retirar_tras_la_respuesta()

        assert isinstance(falla, TimeoutError)
        assert "deleteMessage" not in telegram.metodos()
    finally:
        telegram.soltar.set()


def test_sin_nada_a_la_vista_no_hay_nada_que_retirar():
    """Una respuesta rápida (antes del umbral) no mostró nada: después del mensaje no se manda
    nada más."""
    telegram = TelegramDeMentira()
    with _indicador(telegram) as indicador:
        indicador.sigue_la_respuesta()
    _respuesta_de_verdad(telegram)

    assert indicador.retirar_tras_la_respuesta() is None
    assert telegram.metodos() == ["sendMessage"]


def test_sin_mensaje_que_siga_el_borrador_se_retira_y_ya_no_recibe_texto():
    """Un turno que no deja mensaje (por ejemplo, uno ya respondido): nada va a reemplazar al
    borrador, así que se retira, como antes. Es el único caso con retiro, y no hay ningún
    mensaje al que pueda demorar."""
    telegram = TelegramDeMentira()
    antes = _hilos_del_indicador()
    with _indicador(telegram) as indicador:
        indicador.actualizar_borrador("Anoté que arrancaste.")
        assert telegram.esperar(lambda: telegram.borradores_con_texto())
    indicador.actualizar_borrador("Anoté que arrancaste. Y algo más")
    time.sleep(0.3)

    metodos = telegram.metodos()
    # El retiro: la semilla como mensaje silencioso y su borrado; después, un "escribiendo…".
    assert metodos[-3:] == ["sendMessage", "deleteMessage", "sendChatAction"]
    [envio] = [p for m, p in telegram.llamadas if m == "sendMessage"]
    assert envio["text"] == SEMILLA_INDICADOR and envio["disable_notification"] is True
    assert telegram.borradores_con_texto() == ["Anoté que arrancaste."]
    assert _sin_hilos_nuevos(antes)


def test_en_un_grupo_el_texto_no_va_a_ningun_borrador():
    telegram = TelegramDeMentira()
    with _indicador(telegram, chat_type="group", umbral=0.0, intervalo=0.01) as indicador:
        assert not indicador.admite_borrador
        indicador.actualizar_borrador("Hola")
        assert telegram.esperar(lambda: "sendChatAction" in telegram.metodos())

    assert set(telegram.metodos()) == {"sendChatAction"}


def test_una_falla_del_borrador_con_texto_se_avisa_una_vez_y_no_insiste(capsys):
    telegram = TelegramDeMentira(falla_en=frozenset({"sendMessageDraft"}))
    procesado = []
    with _indicador(telegram, intervalo_borrador=0.0) as indicador:
        indicador.actualizar_borrador("Uno")
        assert telegram.esperar(lambda: "sendMessageDraft" in telegram.metodos())
        time.sleep(0.05)
        indicador.actualizar_borrador("Uno dos")
        indicador.actualizar_borrador("Uno dos tres")
        procesado.append(True)

    assert procesado == [True]
    assert telegram.metodos().count("sendMessageDraft") == 1
    salida = capsys.readouterr().out
    assert len([linea for linea in salida.splitlines() if "(stream)" in linea]) == 1
    assert "token-prueba" not in salida


def test_si_telegram_pide_ir_mas_despacio_espera_y_sigue_con_lo_ultimo():
    telegram = TelegramDeMentira(ritmo=1)
    with _indicador(telegram, intervalo_borrador=0.0) as indicador:
        indicador.actualizar_borrador("Uno")
        # El primero recibe el 429: se espera lo que pide Telegram y se vuelve a mandar.
        assert telegram.esperar(lambda: telegram.borradores_con_texto() == ["Uno", "Uno"])
        indicador.actualizar_borrador("Uno dos")
        assert telegram.esperar(lambda: telegram.borradores_con_texto()[-1:] == ["Uno dos"])

    assert telegram.borradores_con_texto() == ["Uno", "Uno", "Uno dos"]


def test_sin_texto_queda_la_semilla_de_los_tres_puntos():
    """Una IA que no escribe en vivo (u OpenRouter): sólo los tres puntos, y la respuesta los
    reemplaza sin retiro."""
    telegram = TelegramDeMentira()
    with _indicador(telegram, umbral=0.01, intervalo=10.0) as indicador:
        assert telegram.esperar(lambda: "sendChatAction" in telegram.metodos())
        indicador.sigue_la_respuesta()
    _respuesta_de_verdad(telegram)

    [borrador] = [p for m, p in telegram.llamadas if m == "sendMessageDraft"]
    assert borrador["text"] == SEMILLA_INDICADOR
    assert telegram.metodos() == ["sendMessageDraft", "sendChatAction", "sendMessage"]
