"""Unit tests for v5.0.20 features: viewport_manage, multiplayer_manage,
tween_manage, and profiler_manage.
"""

from __future__ import annotations

import pytest

from godot_ai.handlers import multiplayer as mp_handlers
from godot_ai.handlers import profiler as prof_handlers
from godot_ai.handlers import tween as tween_handlers
from godot_ai.handlers import viewport as vp_handlers
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
async def test_viewport_handlers():
    runtime = _FakeRuntime()

    # create_subviewport
    await vp_handlers.viewport_create_subviewport(
        runtime,
        parent_path="Root",
        name="MiniMap",
        size=[256, 256],
        render_target_update_mode=3,
        transparent_bg=True,
        own_world_3d=True,
        as_container=True,
    )
    cmd, params = runtime.last_command
    assert cmd == "viewport_create_subviewport"
    assert params["name"] == "MiniMap"
    assert params["size"] == [256, 256]
    assert params["transparent_bg"] is True
    assert params["as_container"] is True

    # scaffold_splitscreen
    await vp_handlers.viewport_scaffold_splitscreen(
        runtime, layout="4p_quad", is_3d=True, parent_path="UI"
    )
    cmd, params = runtime.last_command
    assert cmd == "viewport_scaffold_splitscreen"
    assert params["layout"] == "4p_quad"
    assert params["is_3d"] is True

    # wire_render_texture
    await vp_handlers.viewport_wire_render_texture(
        runtime, viewport_path="SubViewport", target_node_path="ScreenMesh"
    )
    cmd, params = runtime.last_command
    assert cmd == "viewport_wire_render_texture"
    assert params["viewport_path"] == "SubViewport"
    assert params["target_node_path"] == "ScreenMesh"

    # get_viewport_tree
    await vp_handlers.viewport_get_viewport_tree(runtime)
    cmd, _ = runtime.last_command
    assert cmd == "viewport_get_viewport_tree"

    # set_properties
    await vp_handlers.viewport_set_properties(
        runtime,
        viewport_path="SubViewport",
        size=[1024, 768],
        msaa_2d=2,
        msaa_3d=3,
        transparent_bg=False,
    )
    cmd, params = runtime.last_command
    assert cmd == "viewport_set_properties"
    assert params["size"] == [1024, 768]
    assert params["msaa_2d"] == 2
    assert params["msaa_3d"] == 3


@pytest.mark.asyncio
async def test_multiplayer_handlers():
    runtime = _FakeRuntime()

    # scaffold_network_manager
    await mp_handlers.multiplayer_scaffold_network_manager(
        runtime,
        save_path="res://network.gd",
        default_port=9000,
        max_clients=16,
        as_autoload=True,
        autoload_name="Network",
    )
    cmd, params = runtime.last_command
    assert cmd == "multiplayer_scaffold_network_manager"
    assert params["save_path"] == "res://network.gd"
    assert params["default_port"] == 9000
    assert params["as_autoload"] is True

    # scaffold_spawner
    await mp_handlers.multiplayer_scaffold_spawner(
        runtime,
        parent_path="Players",
        spawner_name="PlayerSpawner",
        spawnable_scenes=["res://player.tscn"],
    )
    cmd, params = runtime.last_command
    assert cmd == "multiplayer_scaffold_spawner"
    assert params["spawner_name"] == "PlayerSpawner"
    assert params["spawnable_scenes"] == ["res://player.tscn"]

    # scaffold_synchronizer
    await mp_handlers.multiplayer_scaffold_synchronizer(
        runtime,
        parent_path="Player",
        properties=[":position", ":rotation"],
    )
    cmd, params = runtime.last_command
    assert cmd == "multiplayer_scaffold_synchronizer"
    assert params["properties"] == [":position", ":rotation"]

    # get_network_status
    await mp_handlers.multiplayer_get_network_status(runtime)
    cmd, _ = runtime.last_command
    assert cmd == "multiplayer_get_network_status"


@pytest.mark.asyncio
async def test_tween_handlers():
    runtime = _FakeRuntime()

    # create
    await tween_handlers.tween_create(
        runtime,
        node_path="PlayerSprite",
        property="modulate:a",
        target_value=0.5,
        duration=1.0,
        trans_type="sine",
        ease_type="out",
    )
    cmd, params = runtime.last_command
    assert cmd == "tween_create"
    assert params["property"] == "modulate:a"
    assert params["target_value"] == 0.5
    assert params["trans_type"] == "sine"

    # preset_animation
    await tween_handlers.tween_preset_animation(
        runtime,
        node_path="ScoreLabel",
        preset="punch_scale",
        duration=0.4,
        punch_factor=1.3,
    )
    cmd, params = runtime.last_command
    assert cmd == "tween_preset_animation"
    assert params["preset"] == "punch_scale"
    assert params["punch_factor"] == 1.3

    # generate_code
    await tween_handlers.tween_generate_code(
        runtime,
        target_var="self",
        property="position",
        target_value="Vector2(200, 300)",
        duration=0.8,
    )
    cmd, params = runtime.last_command
    assert cmd == "tween_generate_code"
    assert params["property"] == "position"
    assert params["target_value"] == "Vector2(200, 300)"


@pytest.mark.asyncio
async def test_profiler_handlers():
    runtime = _FakeRuntime()

    # get_monitors
    await prof_handlers.profiler_get_monitors(runtime)
    cmd, _ = runtime.last_command
    assert cmd == "profiler_get_monitors"

    # get_memory_info
    await prof_handlers.profiler_get_memory_info(runtime)
    cmd, _ = runtime.last_command
    assert cmd == "profiler_get_memory_info"

    # get_render_info
    await prof_handlers.profiler_get_render_info(runtime)
    cmd, _ = runtime.last_command
    assert cmd == "profiler_get_render_info"

    # get_physics_info
    await prof_handlers.profiler_get_physics_info(runtime)
    cmd, _ = runtime.last_command
    assert cmd == "profiler_get_physics_info"


@pytest.mark.asyncio
async def test_tools_registered_in_server():
    server = create_server()
    tools = {t.name for t in await server.list_tools()}

    assert "viewport_manage" in tools
    assert "multiplayer_manage" in tools
    assert "tween_manage" in tools
    assert "profiler_manage" in tools
