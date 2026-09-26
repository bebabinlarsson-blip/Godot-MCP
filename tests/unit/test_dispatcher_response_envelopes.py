"""Guard dispatcher compatibility with built-in GDScript handler responses."""

from __future__ import annotations

from pathlib import Path

from tests.unit._gdscript_text import get_func_block

DISPATCHER = Path(__file__).resolve().parents[2] / "addons" / "godot_ai" / "dispatcher.gd"


def test_dispatcher_wraps_legacy_success_and_error_payloads() -> None:
    source = DISPATCHER.read_text(encoding="utf-8")
    normalizer = get_func_block(
        source,
        "static func _normalize_handler_result(raw_result: Variant) -> Dictionary:",
    )

    assert 'typeof(raw_result.get("success")) == TYPE_BOOL' in normalizer
    assert 'return {"data": raw_result}' in normalizer
    assert 'raw_result.get("error")' in normalizer
    assert "ErrorCodes.make(error_code, str(error_value))" in normalizer
    assert 'raw_result.has("data") or raw_result.has("_deferred")' in normalizer


def test_dispatcher_normalizes_before_malformed_result_guard() -> None:
    source = DISPATCHER.read_text(encoding="utf-8")
    call_handler = get_func_block(
        source,
        "func _call_handler(command: String, params: Dictionary) -> Dictionary:",
    )

    assert "var raw_result: Variant = _handlers[command].call(params)" in call_handler
    assert "var result: Dictionary = _normalize_handler_result(raw_result)" in call_handler
    assert "Handler '%s' returned malformed result" in call_handler
