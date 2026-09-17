"""The plugin may only reload itself through a deferred static call.

``McpPluginReload.reload_enabled_plugin`` disables and re-enables the plugin,
which frees the running ``plugin.gd`` instance. Calling it synchronously from
any method of that instance, including a method that was itself deferred,
returns into a freed script and takes the editor down with SIGBUS/SIGABRT
("SCRIPT ERROR: Bad address index"). Two real clicks on the dock's "Reload
Plugin" button crashed Godot 4.7 that way on 2026-09-07. The only safe shape
is deferring the static callable itself.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.unit._gdscript_text import get_func_block

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_GD = ROOT / "plugin" / "addons" / "godot_ai" / "plugin.gd"
DEFERRED_STATIC_RELOAD = "PluginReload.reload_enabled_plugin.call_deferred()"


def _plugin_source() -> str:
    return PLUGIN_GD.read_text(encoding="utf-8")


def test_plugin_never_reloads_itself_synchronously() -> None:
    source = _plugin_source()
    synchronous = re.findall(r"reload_enabled_plugin\s*\(", source)
    assert synchronous == [], (
        "plugin.gd must not call reload_enabled_plugin() on one of its own frames; "
        f"found {len(synchronous)} direct call(s)"
    )
    assert DEFERRED_STATIC_RELOAD in source


def test_dock_reload_request_defers_the_static_callable() -> None:
    block = get_func_block(
        _plugin_source(), "func _on_dock_plugin_reload_requested(reason: String) -> void:"
    )
    assert DEFERRED_STATIC_RELOAD in block
    # The crash shape: a deferred *method* of this instance that then reloads.
    assert re.search(r"_reload_plugin\w*\.call_deferred\(", block) is None


def test_failed_update_reload_keeps_the_same_shape() -> None:
    block = get_func_block(_plugin_source(), "func _reload_plugin_after_failed_update() -> void:")
    assert DEFERRED_STATIC_RELOAD in block
