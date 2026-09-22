"""Unit tests for v5.0.25 features: 6 new engine management domains."""

from __future__ import annotations

import pytest

from godot_ai.handlers import audio_effect as audio_effect_handlers
from godot_ai.handlers import body as body_handlers
from godot_ai.handlers import cloud as cloud_handlers
from godot_ai.handlers import headless as headless_handlers
from godot_ai.handlers import nav_query as nav_query_handlers
from godot_ai.handlers import world as world_handlers
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
async def test_body_handlers():
    runtime = _FakeRuntime()
    await body_handlers.body_configure_body(runtime, node_path="Player", properties={"mass": 2.5})
    cmd, params = runtime.last_command
    assert cmd == "body_configure_body"
    assert params["node_path"] == "Player"
    assert params["properties"] == {"mass": 2.5}

    await body_handlers.body_apply_impulse(runtime, node_path="Ball", impulse=[10.0, -5.0])
    cmd, params = runtime.last_command
    assert cmd == "body_apply_impulse"
    assert params["node_path"] == "Ball"
    assert params["impulse"] == [10.0, -5.0]

    await body_handlers.body_set_collision_layer_mask(
        runtime, node_path="Player", collision_layer=2, collision_mask=5
    )
    cmd, params = runtime.last_command
    assert cmd == "body_set_collision_layer_mask"
    assert params["collision_layer"] == 2
    assert params["collision_mask"] == 5

    await body_handlers.body_scaffold_character_body(
        runtime, parent_path="World", node_name="Hero", is_3d=True
    )
    cmd, params = runtime.last_command
    assert cmd == "body_scaffold_character_body"
    assert params["node_name"] == "Hero"
    assert params["is_3d"] is True

    await body_handlers.body_get_body_info(runtime, node_path="Player")
    cmd, params = runtime.last_command
    assert cmd == "body_get_body_info"
    assert params["node_path"] == "Player"


@pytest.mark.asyncio
async def test_world_handlers():
    runtime = _FakeRuntime()
    await world_handlers.world_configure_world_environment(
        runtime, node_path="WorldEnv", properties={"glow_enabled": True}
    )
    cmd, params = runtime.last_command
    assert cmd == "world_configure_world_environment"
    assert params["properties"] == {"glow_enabled": True}

    await world_handlers.world_create_sky_material(runtime, sky_type="procedural")
    cmd, params = runtime.last_command
    assert cmd == "world_create_sky_material"
    assert params["sky_type"] == "procedural"

    await world_handlers.world_set_volumetric_fog(runtime, enabled=True, density=0.05)
    cmd, params = runtime.last_command
    assert cmd == "world_set_volumetric_fog"
    assert params["enabled"] is True
    assert params["density"] == 0.05

    await world_handlers.world_configure_camera_attributes(runtime, attribute_type="practical")
    cmd, params = runtime.last_command
    assert cmd == "world_configure_camera_attributes"
    assert params["attribute_type"] == "practical"

    await world_handlers.world_get_world_info(runtime)
    cmd, params = runtime.last_command
    assert cmd == "world_get_world_info"


@pytest.mark.asyncio
async def test_audio_effect_handlers():
    runtime = _FakeRuntime()
    await audio_effect_handlers.audio_effect_add_effect_to_bus(
        runtime, bus_name="Master", effect_class="AudioEffectReverb", at_position=-1
    )
    cmd, params = runtime.last_command
    assert cmd == "audio_effect_add_effect_to_bus"
    assert params["effect_class"] == "AudioEffectReverb"

    await audio_effect_handlers.audio_effect_configure_effect(
        runtime, bus_name="Master", effect_index=0, enabled=True
    )
    cmd, params = runtime.last_command
    assert cmd == "audio_effect_configure_effect"
    assert params["enabled"] is True

    await audio_effect_handlers.audio_effect_remove_effect(
        runtime, bus_name="Master", effect_index=0
    )
    cmd, params = runtime.last_command
    assert cmd == "audio_effect_remove_effect"

    await audio_effect_handlers.audio_effect_list_bus_effects(runtime, bus_name="Master")
    cmd, params = runtime.last_command
    assert cmd == "audio_effect_list_bus_effects"


@pytest.mark.asyncio
async def test_nav_query_handlers():
    runtime = _FakeRuntime()
    await nav_query_handlers.nav_query_query_path_2d(runtime, start=[0.0, 0.0], end=[100.0, 50.0])
    cmd, params = runtime.last_command
    assert cmd == "nav_query_query_path_2d"
    assert params["start"] == [0.0, 0.0]
    assert params["end"] == [100.0, 50.0]

    await nav_query_handlers.nav_query_query_path_3d(
        runtime, start=[0.0, 0.0, 0.0], end=[10.0, 0.0, 10.0]
    )
    cmd, params = runtime.last_command
    assert cmd == "nav_query_query_path_3d"

    await nav_query_handlers.nav_query_scaffold_nav_link(
        runtime, parent_path="World", is_3d=True, bidirectional=True
    )
    cmd, params = runtime.last_command
    assert cmd == "nav_query_scaffold_nav_link"
    assert params["is_3d"] is True

    await nav_query_handlers.nav_query_scaffold_nav_obstacle(
        runtime, parent_path="World", radius=45.0, is_3d=False
    )
    cmd, params = runtime.last_command
    assert cmd == "nav_query_scaffold_nav_obstacle"
    assert params["radius"] == 45.0

    await nav_query_handlers.nav_query_get_nav_map_info(runtime, is_3d=True)
    cmd, params = runtime.last_command
    assert cmd == "nav_query_get_nav_map_info"
    assert params["is_3d"] is True


@pytest.mark.asyncio
async def test_headless_handlers():
    runtime = _FakeRuntime()
    await headless_handlers.headless_run_script(
        runtime, script_path="res://test.gd", inline_code=""
    )
    cmd, params = runtime.last_command
    assert cmd == "headless_run_script"
    assert params["script_path"] == "res://test.gd"

    await headless_handlers.headless_run_headless_scene(
        runtime, scene_path="res://Main.tscn", quit_after_frames=120
    )
    cmd, params = runtime.last_command
    assert cmd == "headless_run_headless_scene"
    assert params["scene_path"] == "res://Main.tscn"

    await headless_handlers.headless_export_project_cli(
        runtime, preset="Windows Desktop", output_path="build/game.exe"
    )
    cmd, params = runtime.last_command
    assert cmd == "headless_export_project_cli"
    assert params["preset"] == "Windows Desktop"

    await headless_handlers.headless_reimport_assets_cli(runtime)
    cmd, params = runtime.last_command
    assert cmd == "headless_reimport_assets_cli"

    await headless_handlers.headless_get_engine_info(runtime)
    cmd, params = runtime.last_command
    assert cmd == "headless_get_engine_info"


@pytest.mark.asyncio
async def test_cloud_handlers():
    runtime = _FakeRuntime()
    await cloud_handlers.cloud_get_tunnel_status(runtime)
    cmd, params = runtime.last_command
    assert cmd == "cloud_get_tunnel_status"

    await cloud_handlers.cloud_get_action_schema_url(runtime, host="https://tunnel.example.com")
    cmd, params = runtime.last_command
    assert cmd == "cloud_get_action_schema_url"
    assert params["host"] == "https://tunnel.example.com"

    await cloud_handlers.cloud_test_cloud_connection(runtime)
    cmd, params = runtime.last_command
    assert cmd == "cloud_test_cloud_connection"


@pytest.mark.asyncio
async def test_server_registers_v5_0_25_tools():
    server = create_server()
    tools = {t.name for t in await server.list_tools()}
    expected = {
        "body_manage",
        "world_manage",
        "audio_effect_manage",
        "nav_query_manage",
        "headless_manage",
        "cloud_manage",
    }
    assert expected.issubset(tools)
    assert len(tools) >= 96
