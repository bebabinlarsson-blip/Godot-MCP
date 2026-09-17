"""V4 self-update must not resurrect automatic orphan recovery authority."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "plugin" / "addons" / "godot_ai"


def test_update_markers_never_mint_process_or_replacement_authority() -> None:
    plugin = (PLUGIN / "plugin.gd").read_text(encoding="utf-8")
    lifecycle = (PLUGIN / "utils" / "server_lifecycle.gd").read_text(encoding="utf-8")

    assert "_pending_self_update_succeeded" not in lifecycle
    assert "authorize_replacement" not in plugin
    assert "request_replacement" in plugin


def test_transport_secret_is_not_persisted_in_editor_settings() -> None:
    plugin = (PLUGIN / "plugin.gd").read_text(encoding="utf-8")
    assert "managed_server_ws_token" not in plugin
    assert "GODOT_AI_WS_TOKEN" not in plugin  # lifecycle owns the spawn boundary
