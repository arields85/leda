from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dispatch_and_gateway_contain_stale_preview_and_callback_guards():
    dispatch = (ROOT / "src" / "leda" / "despachador.py").read_text("utf-8")
    gateway = (ROOT / "src" / "leda" / "gateway.py").read_text("utf-8")
    assert "def _preview_vigente" in dispatch
    # Un solo reloj: la vigencia de la vista previa usa el `ahora` de la pasada.
    assert "p.vence_en > %s as no_vencida" in dispatch
    assert "clock_timestamp()" not in dispatch
    assert "update message_outbox set estado = 'descartado'" in dispatch
    draft_callback = gateway.split("def _resolver_toque_borrador", 1)[1]
    assert "with espacio(conn, workspace_id)" in draft_callback
    callback_body = draft_callback.split("def _responder", 1)[0]
    assert "The Unit 1A authority function persisted the terminal visible outbox" \
        in callback_body
    assert "if resuelta is not None" in callback_body
