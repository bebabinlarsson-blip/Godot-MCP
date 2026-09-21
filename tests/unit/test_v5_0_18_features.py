"""Unit tests for v5.0.18 features: omni_manage, shader_manage, physics_manage,
editor_eval, node_call_method.
"""

from __future__ import annotations

import asyncio

import pytest

from godot_ai.handlers import editor as editor_handlers
from godot_ai.handlers import node as node_handlers
from godot_ai.handlers import omni as omni_handlers
from godot_ai.handlers import physics as physics_handlers
from godot_ai.handlers import shader as shader_handlers
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
async def test_omni_eval_and_reflection_dispatch():
    runtime = _FakeRuntime()
    await omni_handlers.omni_eval(runtime, code="return 1 + 1", mode="expression")
    cmd, params = runtime.last_command
    assert cmd == "omni_eval"
    assert params["code"] == "return 1 + 1"
    assert params["mode"] == "expression"

    await omni_handlers.reflection_call(runtime, target="Player", method="take_damage", args=[10])
    cmd, params = runtime.last_command
    assert cmd == "reflection_call"
    assert params["target"] == "Player"
    assert params["method"] == "take_damage"
    assert params["args"] == [10]

    await omni_handlers.reflection_get(runtime, target="Player", property="health")
    cmd, params = runtime.last_command
    assert cmd == "reflection_get"
    assert params["property"] == "health"

    await omni_handlers.reflection_set(runtime, target="Player", property="health", value=100)
    cmd, params = runtime.last_command
    assert cmd == "reflection_set"
    assert params["value"] == 100

    await omni_handlers.reflection_inspect(runtime, target="Player")
    cmd, params = runtime.last_command
    assert cmd == "reflection_inspect"

    await omni_handlers.mcp_ping(runtime)
    cmd, _ = runtime.last_command
    assert cmd == "mcp_ping"


@pytest.mark.asyncio
async def test_omni_ui_and_prefab_dispatch():
    runtime = _FakeRuntime()
    await omni_handlers.ui_semantic_tree(runtime, max_depth=6)
    cmd, params = runtime.last_command
    assert cmd == "ui_semantic_tree"
    assert params["max_depth"] == 6

    await omni_handlers.ui_click_control(runtime, text="Save")
    cmd, params = runtime.last_command
    assert cmd == "ui_click_control"
    assert params["text"] == "Save"

    await omni_handlers.ui_type_text(runtime, text="Player1", target="NameEdit")
    cmd, params = runtime.last_command
    assert cmd == "ui_type_text"
    assert params["text"] == "Player1"

    await omni_handlers.scene_instantiate_prefab(
        runtime, scene_path="res://player.tscn", parent_path="World", node_name="Hero"
    )
    cmd, params = runtime.last_command
    assert cmd == "scene_instantiate_prefab"
    assert params["scene_path"] == "res://player.tscn"
    assert params["node_name"] == "Hero"


@pytest.mark.asyncio
async def test_shader_handlers_dispatch():
    runtime = _FakeRuntime()
    await shader_handlers.shader_create(
        runtime, path="res://shaders/test.gdshader", shader_type="canvas_item"
    )
    cmd, params = runtime.last_command
    assert cmd == "shader_create"
    assert params["path"] == "res://shaders/test.gdshader"

    await shader_handlers.shader_apply_preset(
        runtime,
        preset="outline_2d",
        target_node_path="Sprite2D",
        params={"outline_width": 2.0},
    )
    cmd, params = runtime.last_command
    assert cmd == "shader_apply_preset"
    assert params["preset"] == "outline_2d"
    assert params["target_node_path"] == "Sprite2D"
    assert params["params"] == {"outline_width": 2.0}

    await shader_handlers.shader_set_param(
        runtime, param="outline_width", value=3.5, target_node_path="Sprite2D"
    )
    cmd, params = runtime.last_command
    assert cmd == "shader_set_param"
    assert params["param"] == "outline_width"
    assert params["value"] == 3.5

    await shader_handlers.shader_get_params(runtime, target_node_path="Sprite2D")
    cmd, params = runtime.last_command
    assert cmd == "shader_get_params"
    assert params["target_node_path"] == "Sprite2D"


@pytest.mark.asyncio
async def test_physics_handlers_dispatch():
    runtime = _FakeRuntime()
    await physics_handlers.physics_raycast_2d(
        runtime, from_pos=[0, 0], to_pos=[100, 200], collision_mask=3
    )
    cmd, params = runtime.last_command
    assert cmd == "physics_raycast_2d"
    assert params["from_pos"] == [0, 0]
    assert params["to_pos"] == [100, 200]
    assert params["collision_mask"] == 3

    await physics_handlers.physics_raycast_3d(
        runtime, from_pos=[0, 10, 0], to_pos=[0, 0, 0], collision_mask=1
    )
    cmd, params = runtime.last_command
    assert cmd == "physics_raycast_3d"
    assert params["from_pos"] == [0, 10, 0]

    await physics_handlers.physics_query_point_2d(runtime, point=[50, 50], max_results=8)
    cmd, params = runtime.last_command
    assert cmd == "physics_query_point_2d"
    assert params["point"] == [50, 50]
    assert params["max_results"] == 8

    await physics_handlers.physics_scaffold_sensor(
        runtime, parent_path="Player", is_2d=True, sensor_name="GroundCheck"
    )
    cmd, params = runtime.last_command
    assert cmd == "physics_scaffold_sensor"
    assert params["parent_path"] == "Player"
    assert params["sensor_name"] == "GroundCheck"


@pytest.mark.asyncio
async def test_editor_and_node_expansion_dispatch():
    runtime = _FakeRuntime()
    await editor_handlers.editor_eval(runtime, code="print('editor eval')")
    cmd, params = runtime.last_command
    assert cmd == "editor_eval"
    assert params["code"] == "print('editor eval')"

    await editor_handlers.editor_execute_script(runtime, path="res://scripts/tool.gd")
    cmd, params = runtime.last_command
    assert cmd == "editor_execute_script"
    assert params["path"] == "res://scripts/tool.gd"

    await node_handlers.node_call_method(
        runtime, path="Player", method="jump", args=[1.5]
    )
    cmd, params = runtime.last_command
    assert cmd == "node_call_method"
    assert params["path"] == "Player"
    assert params["method"] == "jump"
    assert params["args"] == [1.5]


def test_server_total_tool_count_is_at_least_55():
    server = create_server()
    tools = asyncio.run(server.list_tools())
    tool_names = [t.name for t in tools]
    assert "omni_manage" in tool_names
    assert "shader_manage" in tool_names
    assert "physics_manage" in tool_names
    assert len(tool_names) >= 55
