from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _function_body(source: str, function_name: str) -> str:
    start = source.index(f"func {function_name}(")
    next_function = source.find("\nfunc ", start + 1)
    return source[start:] if next_function < 0 else source[start:next_function]


def test_test_connection_reports_bridge_state_without_fake_ping() -> None:
    dock = (ROOT / "addons/godot_ai/godot_mcp_dock.gd").read_text(encoding="utf-8")
    body = _function_body(dock, "_on_test_connection_pressed")

    assert "status_snapshot_requested.emit()" in body
    assert "live_server_probe_requested.emit(_http_port)" in body
    assert "Bridge not connected" in body
    assert "record_tool_call" not in body
    assert "Engine.get_process_frames()" not in body


def test_starting_dock_exposes_server_proof_phase_and_reason() -> None:
    lifecycle = (ROOT / "addons/godot_ai/utils/server_lifecycle.gd").read_text(encoding="utf-8")
    dock = (ROOT / "addons/godot_ai/godot_mcp_dock.gd").read_text(encoding="utf-8")

    status_body = _function_body(lifecycle, "get_status_dict")
    assert '"proof_pending_reason"' in status_body
    assert '"proof_deadline_remaining_sec"' in status_body
    assert '"PROVE"' in dock
    assert "_proof_pending_reason" in dock


def test_authenticated_status_pending_reason_keeps_safe_probe_detail() -> None:
    lifecycle = (ROOT / "addons/godot_ai/utils/server_lifecycle.gd").read_text(encoding="utf-8")
    prove_body = _function_body(lifecycle, "_effect_prove")
    reason_body = _function_body(lifecycle, "_authenticated_status_pending_reason")

    assert "_authenticated_status_pending_reason(live, capability)" in prove_body
    assert 'live.get("error"' in reason_body
    assert "unexpected_service" in reason_body
    assert "instance_mismatch" in reason_body
