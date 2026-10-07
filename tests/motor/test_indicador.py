"""El indicador de actividad y la respuesta que se ve mientras la IA la escribe
(`despachador.mantener_chat_activo`; ADR 0011, decisión 2).

Pedido del usuario (2026-10-07): traer de la rama congelada lo que ya funcionó en Telegram
real, el "escribiendo…", los tres puntos del borrador nativo sembrado con un carácter invisible
y el texto de la respuesta que aparece mientras la IA lo escribe. El borrador es efímero: no
pasa por el outbox ni se audita, y se retira antes de que salga el mensaje de verdad, que es el
del outbox. Telegram es un cliente HTTP falso que guarda cada llamada; nada sale a la red.
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

    def __init__(self, falla_en: frozenset[str] = frozenset(), ritmo: int = 0) -> None:
        self.llamadas: list[tuple[str, dict]] = []
        self.falla_en = falla_en
        self.ritmo = ritmo
        self.siguiente_id = 900
        self._candado = threading.RLock()     # los predicados de `esperar` lo vuelven a tomar
        self._hubo = threading.Condition(self._candado)

    def post(self, url, json=None):
        metodo = url.rsplit("/", 1)[-1]
        with self._hubo:
            self.llamadas.append((metodo, dict(json or {})))
            self._hubo.notify_all()
        if metodo in self.falla_en:
            raise ConnectionError("fallo simulado")
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


def test_al_terminar_el_borrador_se_retira_y_ya_no_recibe_texto():
    telegram = TelegramDeMentira()
    with _indicador(telegram) as indicador:
        indicador.actualizar_borrador("Anoté que arrancaste.")
        assert telegram.esperar(lambda: telegram.borradores_con_texto())
    indicador.actualizar_borrador("Anoté que arrancaste. Y algo más")
    time.sleep(0.3)

    metodos = telegram.metodos()
    # El retiro: la semilla como mensaje silencioso y su borrado; después, un "escribiendo…"
    # que cubre el hueco hasta que llega la respuesta de verdad.
    assert metodos[-3:] == ["sendMessage", "deleteMessage", "sendChatAction"]
    [envio] = [p for m, p in telegram.llamadas if m == "sendMessage"]
    assert envio["text"] == SEMILLA_INDICADOR and envio["disable_notification"] is True
    assert telegram.borradores_con_texto() == ["Anoté que arrancaste."]


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
    """Una IA que no escribe en vivo (u OpenRouter): sólo los tres puntos y el retiro."""
    telegram = TelegramDeMentira()
    with _indicador(telegram, umbral=0.01, intervalo=0.01):
        assert telegram.esperar(lambda: "sendMessageDraft" in telegram.metodos())

    [borrador] = [p for m, p in telegram.llamadas if m == "sendMessageDraft"]
    assert borrador["text"] == SEMILLA_INDICADOR
    assert "deleteMessage" in telegram.metodos()
