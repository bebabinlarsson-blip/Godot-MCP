"""Unit tests for v5.0.26 features: 4 new engine management domains."""

from __future__ import annotations

import pytest

from godot_ai.handlers import curve as curve_handlers
from godot_ai.handlers import gi as gi_handlers
from godot_ai.handlers import input_event as input_event_handlers
from godot_ai.handlers import physics_query as physics_query_handlers
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
async def test_gi_handlers():
    runtime = _FakeRuntime()
    await gi_handlers.gi_create_decal(
        runtime, parent_path="World", name="BulletHole", size=[1.0, 1.0, 1.0]
    )
    cmd, params = runtime.last_command
    assert cmd == "gi_create_decal"
    assert params["name"] == "BulletHole"
    assert params["size"] == [1.0, 1.0, 1.0]

    await gi_handlers.gi_configure_decal(
        runtime, node_path="BulletHole", emission_energy=2.0
    )
    cmd, params = runtime.last_command
    assert cmd == "gi_configure_decal"
    assert params["emission_energy"] == 2.0

    await gi_handlers.gi_create_reflection_probe(
        runtime, parent_path="World", size=[10.0, 10.0, 10.0]
    )
    cmd, params = runtime.last_command
    assert cmd == "gi_create_reflection_probe"
    assert params["size"] == [10.0, 10.0, 10.0]

    await gi_handlers.gi_create_voxel_gi(
        runtime, parent_path="World", subdivide=2
    )
    cmd, params = runtime.last_command
    assert cmd == "gi_create_voxel_gi"
    assert params["subdivide"] == 2

    await gi_handlers.gi_create_lightmap_gi(
        runtime, parent_path="World", bounces=4
    )
    cmd, params = runtime.last_command
    assert cmd == "gi_create_lightmap_gi"
    assert params["bounces"] == 4

    await gi_handlers.gi_get_gi_info(runtime, node_path="BulletHole")
    cmd, params = runtime.last_command
    assert cmd == "gi_get_gi_info"
    assert params["node_path"] == "BulletHole"


@pytest.mark.asyncio
async def test_input_event_handlers():
    runtime = _FakeRuntime()
    await input_event_handlers.input_event_simulate_action(
        runtime, action="jump", pressed=True, strength=1.0
    )
    cmd, params = runtime.last_command
    assert cmd == "input_event_simulate_action"
    assert params["action"] == "jump"
    assert params["pressed"] is True

    await input_event_handlers.input_event_simulate_key(
        runtime, key="Space", pressed=True
    )
    cmd, params = runtime.last_command
    assert cmd == "input_event_simulate_key"
    assert params["key"] == "Space"

    await input_event_handlers.input_event_simulate_mouse_button(
        runtime, button_index=1, pressed=True, position=[100.0, 200.0]
    )
    cmd, params = runtime.last_command
    assert cmd == "input_event_simulate_mouse_button"
    assert params["button_index"] == 1
    assert params["position"] == [100.0, 200.0]

    await input_event_handlers.input_event_simulate_mouse_motion(
        runtime, position=[150.0, 250.0], relative=[5.0, 5.0]
    )
    cmd, params = runtime.last_command
    assert cmd == "input_event_simulate_mouse_motion"
    assert params["position"] == [150.0, 250.0]

    await input_event_handlers.input_event_replay_macro(
        runtime, events=[{"type": "action", "action": "jump"}]
    )
    cmd, params = runtime.last_command
    assert cmd == "input_event_replay_macro"
    assert len(params["events"]) == 1

    await input_event_handlers.input_event_get_input_state(
        runtime, action="jump"
    )
    cmd, params = runtime.last_command
    assert cmd == "input_event_get_input_state"
    assert params["action"] == "jump"


@pytest.mark.asyncio
async def test_physics_query_handlers():
    runtime = _FakeRuntime()
    await physics_query_handlers.physics_query_intersect_ray_3d(
        runtime, from_pos=[0.0, 10.0, 0.0], to_pos=[0.0, 0.0, 0.0]
    )
    cmd, params = runtime.last_command
    assert cmd == "physics_query_intersect_ray_3d"
    assert params["from_pos"] == [0.0, 10.0, 0.0]

    await physics_query_handlers.physics_query_intersect_ray_2d(
        runtime, from_pos=[0.0, 0.0], to_pos=[100.0, 0.0]
    )
    cmd, params = runtime.last_command
    assert cmd == "physics_query_intersect_ray_2d"
    assert params["to_pos"] == [100.0, 0.0]

    await physics_query_handlers.physics_query_intersect_point_3d(
        runtime, position=[1.0, 2.0, 3.0]
    )
    cmd, params = runtime.last_command
    assert cmd == "physics_query_intersect_point_3d"
    assert params["position"] == [1.0, 2.0, 3.0]

    await physics_query_handlers.physics_query_intersect_point_2d(
        runtime, position=[50.0, 50.0]
    )
    cmd, params = runtime.last_command
    assert cmd == "physics_query_intersect_point_2d"
    assert params["position"] == [50.0, 50.0]

    await physics_query_handlers.physics_query_intersect_shape_3d(
        runtime, shape_type="box", radius=2.0
    )
    cmd, params = runtime.last_command
    assert cmd == "physics_query_intersect_shape_3d"
    assert params["shape_type"] == "box"

    await physics_query_handlers.physics_query_cast_motion_3d(
        runtime, shape_type="sphere", radius=0.5, motion=[0.0, -5.0, 0.0]
    )
    cmd, params = runtime.last_command
    assert cmd == "physics_query_cast_motion_3d"
    assert params["motion"] == [0.0, -5.0, 0.0]


@pytest.mark.asyncio
async def test_curve_handlers():
    runtime = _FakeRuntime()
    await curve_handlers.curve_create_curve_1d(
        runtime, points=[[0.0, 0.0], [1.0, 2.0]], min_value=0.0, max_value=2.0
    )
    cmd, params = runtime.last_command
    assert cmd == "curve_create_curve_1d"
    assert params["max_value"] == 2.0

    await curve_handlers.curve_create_curve_2d(
        runtime, points=[[0.0, 0.0], [50.0, 50.0]]
    )
    cmd, params = runtime.last_command
    assert cmd == "curve_create_curve_2d"
    assert params["points"] == [[0.0, 0.0], [50.0, 50.0]]

    await curve_handlers.curve_create_curve_3d(
        runtime, points=[[0.0, 0.0, 0.0], [1.0, 2.0, 3.0]]
    )
    cmd, params = runtime.last_command
    assert cmd == "curve_create_curve_3d"
    assert params["points"] == [[0.0, 0.0, 0.0], [1.0, 2.0, 3.0]]

    await curve_handlers.curve_create_gradient(
        runtime, offsets=[0.0, 1.0], colors=["#ff0000", "#00ff00"]
    )
    cmd, params = runtime.last_command
    assert cmd == "curve_create_gradient"
    assert params["colors"] == ["#ff0000", "#00ff00"]

    await curve_handlers.curve_create_gradient_texture(
        runtime, width=512, is_2d=True, height=512
    )
    cmd, params = runtime.last_command
    assert cmd == "curve_create_gradient_texture"
    assert params["width"] == 512
    assert params["is_2d"] is True

    await curve_handlers.curve_sample_curve(
        runtime, curve_path="res://curve.tres", offset=0.75
    )
    cmd, params = runtime.last_command
    assert cmd == "curve_sample_curve"
    assert params["offset"] == 0.75

    await curve_handlers.curve_sample_gradient(
        runtime, gradient_path="res://gradient.tres", offset=0.3
    )
    cmd, params = runtime.last_command
    assert cmd == "curve_sample_gradient"
    assert params["offset"] == 0.3


@pytest.mark.asyncio
async def test_server_registers_v5_0_26_tools():
    server = create_server()
    tools = {t.name for t in await server.list_tools()}
    expected = {
        "gi_manage",
        "input_event_manage",
        "physics_query_manage",
        "curve_manage",
    }
    assert expected.issubset(tools)
    assert len(tools) == 100
