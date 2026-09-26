"""Guard the HTTP handler's asynchronous response handoff."""

from __future__ import annotations

from pathlib import Path

from tests.unit._gdscript_text import get_func_block

HTTP_HANDLER = (
    Path(__file__).resolve().parents[2] / "addons" / "godot_ai" / "handlers" / "http_handler.gd"
)


def test_http_commands_return_deferred_sentinel_instead_of_coroutine_state() -> None:
    source = HTTP_HANDLER.read_text(encoding="utf-8")
    assert "const McpDispatcher := preload" not in source
    assert "const ScriptWork := preload" not in source

    for method, finisher in (
        ("send_request", "_finish_send_request_deferred"),
        ("download_file", "_finish_download_file_deferred"),
    ):
        block = get_func_block(source, method)
        assert f"{finisher}(_connection, request_id, params.duplicate(true))" in block
        assert "McpDispatcher.DEFERRED_RESPONSE.duplicate()" in block
        assert "return deferred" in block
        assert "await " not in block, f"{method} must return synchronously to the dispatcher"


def test_http_finisher_coroutines_are_static_and_send_final_reply() -> None:
    source = HTTP_HANDLER.read_text(encoding="utf-8")

    for signature in (
        "static func _finish_send_request_deferred("
        "connection, request_id: String, params: Dictionary) -> void:",
        "static func _finish_download_file_deferred("
        "connection, request_id: String, params: Dictionary) -> void:",
    ):
        block = get_func_block(source, signature)
        assert "ScriptWork.begin(" in block
        assert "await " in block
        assert "ScriptWork.finish(work)" in block

    for signature in (
        "static func _run_send_request_deferred("
        "connection, request_id: String, params: Dictionary) -> void:",
        "static func _run_download_file_deferred("
        "connection, request_id: String, params: Dictionary) -> void:",
    ):
        block = get_func_block(source, signature)
        assert "connection.send_deferred_response(request_id" in block
        assert "is_instance_valid(connection)" in block
