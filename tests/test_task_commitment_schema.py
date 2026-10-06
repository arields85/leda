from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dispatch_contains_stale_preview_guard():
    # La guarda del toque del borrador vivía en `gateway.py`, que se retiró con los
    # flujos A y B (E3-4); queda la del despacho.
    dispatch = (ROOT / "src" / "leda" / "despachador.py").read_text("utf-8")
    assert "def _preview_vigente" in dispatch
    # Un solo reloj: la vigencia de la vista previa usa el `ahora` de la pasada.
    assert "p.vence_en > %s as no_vencida" in dispatch
    assert "clock_timestamp()" not in dispatch
    assert "update message_outbox set estado = 'descartado'" in dispatch
