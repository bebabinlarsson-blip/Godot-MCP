"""Unit tests for v5.0.21 features: display_manage, loader_manage,
compute_manage, export_manage, xr_manage, and undo_redo_manage.
"""

from __future__ import annotations

import pytest

from godot_ai.handlers import compute as compute_handlers
from godot_ai.handlers import display as display_handlers
from godot_ai.handlers import export as export_handlers
from godot_ai.handlers import loader as loader_handlers
from godot_ai.handlers import undo_redo as undo_redo_handlers
from godot_ai.handlers import xr as xr_handlers
from tests.conftest import create_test_server as create_server


class _FakeRuntime:
    def __init__(self, session_id: str | None = "s1") -> None:
        self.active_session_id = session_id
        self.sent: list[dict] = []
        self.response: dict = {"status": "ok"}

    async def send_command(self, command, params=None, session_id=None, timeout=5.0):
        self.sent.append(
            {
                "command": command,
                "params": params,
                "session_id": session_id,
                "timeout": timeout,
            }
        )
        return self.response

    async def get_editor_state(self, session_id=None):
        return {"project_open": True, "writable": True, "readiness": "ready"}

    def get_active_session(self):
        return None

    @property
    def last_command(self) -> tuple[str, dict]:
        return self.sent[-1]["command"], self.sent[-1]["params"]


@pytest.mark.asyncio
async def test_display_handlers():
    runtime = _FakeRuntime()

    # set_mode
    await display_handlers.display_set_mode(
        runtime, mode="fullscreen", borderless=True, always_on_top=True
    )
    cmd, params = runtime.last_command
    assert cmd == "display_set_mode"
    assert params["mode"] == "fullscreen"
    assert params["borderless"] is True
    assert params["always_on_top"] is True

    # get_display_info
    await display_handlers.display_get_display_info(runtime)
    cmd, _ = runtime.last_command
    assert cmd == "display_get_display_info"

    # set_window_rect
    await display_handlers.display_set_window_rect(
        runtime, size=[1920, 1080], position=[100, 100]
    )
    cmd, params = runtime.last_command
    assert cmd == "display_set_window_rect"
    assert params["size"] == [1920, 1080]

    # set_vsync
    await display_handlers.display_set_vsync(runtime, vsync_mode="mailbox")
    cmd, params = runtime.last_command
    assert cmd == "display_set_vsync"
    assert params["vsync_mode"] == "mailbox"

    # set_mouse_mode
    await display_handlers.display_set_mouse_mode(runtime, mouse_mode="captured")
    cmd, params = runtime.last_command
    assert cmd == "display_set_mouse_mode"
    assert params["mouse_mode"] == "captured"

    # scaffold_subwindow
    await display_handlers.display_scaffold_subwindow(
        runtime,
        parent_path="UI",
        window_type="confirmation_dialog",
        name="QuitConfirm",
        title="Quit Game?",
        size=[350, 150],
        dialog_text="Are you sure you want to exit?",
    )
    cmd, params = runtime.last_command
    assert cmd == "display_scaffold_subwindow"
    assert params["window_type"] == "confirmation_dialog"
    assert params["title"] == "Quit Game?"


@pytest.mark.asyncio
async def test_loader_handlers():
    runtime = _FakeRuntime()

    # start_load
    await loader_handlers.loader_start_load(
        runtime, path="res://level_2.tscn", use_sub_threads=True
    )
    cmd, params = runtime.last_command
    assert cmd == "loader_start_load"
    assert params["path"] == "res://level_2.tscn"
    assert params["use_sub_threads"] is True

    # get_status
    await loader_handlers.loader_get_status(runtime, path="res://level_2.tscn")
    cmd, params = runtime.last_command
    assert cmd == "loader_get_status"
    assert params["path"] == "res://level_2.tscn"

    # get_resource
    await loader_handlers.loader_get_resource(runtime, path="res://level_2.tscn")
    cmd, params = runtime.last_command
    assert cmd == "loader_get_resource"
    assert params["path"] == "res://level_2.tscn"

    # scaffold_loading_screen
    await loader_handlers.loader_scaffold_loading_screen(
        runtime, save_path="res://scripts/my_loader.gd"
    )
    cmd, params = runtime.last_command
    assert cmd == "loader_scaffold_loading_screen"
    assert params["save_path"] == "res://scripts/my_loader.gd"


@pytest.mark.asyncio
async def test_compute_handlers():
    runtime = _FakeRuntime()

    # create_shader
    await compute_handlers.compute_create_shader(
        runtime, shader_path="res://compute.glsl", code="test"
    )
    cmd, params = runtime.last_command
    assert cmd == "compute_create_shader"
    assert params["shader_path"] == "res://compute.glsl"

    # get_device_info
    await compute_handlers.compute_get_device_info(runtime)
    cmd, _ = runtime.last_command
    assert cmd == "compute_get_device_info"

    # run_compute
    await compute_handlers.compute_run_compute(
        runtime,
        shader_path="res://compute.glsl",
        input_buffer=[1.0, 2.0, 3.0],
        x_groups=2,
    )
    cmd, params = runtime.last_command
    assert cmd == "compute_run_compute"
    assert params["input_buffer"] == [1.0, 2.0, 3.0]
    assert params["x_groups"] == 2


@pytest.mark.asyncio
async def test_export_handlers():
    runtime = _FakeRuntime()

    # list_presets
    await export_handlers.export_list_presets(runtime)
    cmd, _ = runtime.last_command
    assert cmd == "export_list_presets"

    # get_preset_info
    await export_handlers.export_get_preset_info(runtime, preset_name="Windows Desktop")
    cmd, params = runtime.last_command
    assert cmd == "export_get_preset_info"
    assert params["preset_name"] == "Windows Desktop"

    # run_export
    await export_handlers.export_run_export(
        runtime, preset_name="Windows Desktop", output_path="build/game.exe", debug=True
    )
    cmd, params = runtime.last_command
    assert cmd == "export_run_export"
    assert params["preset_name"] == "Windows Desktop"
    assert params["output_path"] == "build/game.exe"
    assert params["debug"] is True


@pytest.mark.asyncio
async def test_xr_handlers():
    runtime = _FakeRuntime()

    # scaffold_xr_rig
    await xr_handlers.xr_scaffold_xr_rig(
        runtime, parent_path="World", rig_name="VRPlayer"
    )
    cmd, params = runtime.last_command
    assert cmd == "xr_scaffold_xr_rig"
    assert params["rig_name"] == "VRPlayer"

    # get_xr_status
    await xr_handlers.xr_get_xr_status(runtime)
    cmd, _ = runtime.last_command
    assert cmd == "xr_get_xr_status"

    # generate_xr_startup_script
    await xr_handlers.xr_generate_xr_startup_script(
        runtime, save_path="res://scripts/xr_boot.gd"
    )
    cmd, params = runtime.last_command
    assert cmd == "xr_generate_xr_startup_script"
    assert params["save_path"] == "res://scripts/xr_boot.gd"


@pytest.mark.asyncio
async def test_undo_redo_handlers():
    runtime = _FakeRuntime()

    # get_history
    await undo_redo_handlers.undo_redo_get_history(runtime)
    cmd, _ = runtime.last_command
    assert cmd == "undo_redo_get_history"

    # undo
    await undo_redo_handlers.undo_redo_undo(runtime)
    cmd, _ = runtime.last_command
    assert cmd == "undo_redo_undo"

    # redo
    await undo_redo_handlers.undo_redo_redo(runtime)
    cmd, _ = runtime.last_command
    assert cmd == "undo_redo_redo"


@pytest.mark.asyncio
async def test_tools_registered_in_server():
    server = create_server()
    tools = {t.name for t in await server.list_tools()}

    assert "display_manage" in tools
    assert "loader_manage" in tools
    assert "compute_manage" in tools
    assert "export_manage" in tools
    assert "xr_manage" in tools
    assert "undo_redo_manage" in tools
