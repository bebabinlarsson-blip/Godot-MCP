"""Unit tests for v5.0.23 features: pck_manage, system_manage,
light_manage, http_manage, shader_global_manage, and recording_manage.
"""

from __future__ import annotations

import pytest

from godot_ai.handlers import http as http_handlers
from godot_ai.handlers import light as light_handlers
from godot_ai.handlers import pck as pck_handlers
from godot_ai.handlers import recording as recording_handlers
from godot_ai.handlers import shader_global as shader_global_handlers
from godot_ai.handlers import system as system_handlers
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
async def test_pck_handlers():
    runtime = _FakeRuntime()

    # create_pck
    await pck_handlers.pck_create_pck(
        runtime, pck_path="res://dlc.pck", files=["res://mod.tscn"], alignment=64
    )
    cmd, params = runtime.last_command
    assert cmd == "pck_create_pck"
    assert params["pck_path"] == "res://dlc.pck"
    assert params["files"] == ["res://mod.tscn"]
    assert params["alignment"] == 64

    # load_pck
    await pck_handlers.pck_load_pck(runtime, pck_path="res://dlc.pck", replace_files=False)
    cmd, params = runtime.last_command
    assert cmd == "pck_load_pck"
    assert params["replace_files"] is False

    # inspect_pck
    await pck_handlers.pck_inspect_pck(runtime, pck_path="res://dlc.pck")
    cmd, params = runtime.last_command
    assert cmd == "pck_inspect_pck"
    assert params["pck_path"] == "res://dlc.pck"


@pytest.mark.asyncio
async def test_system_handlers():
    runtime = _FakeRuntime()

    # get_system_info
    await system_handlers.system_get_system_info(runtime)
    cmd, params = runtime.last_command
    assert cmd == "system_get_system_info"
    assert params == {}

    # get_time
    await system_handlers.system_get_time(runtime)
    cmd, params = runtime.last_command
    assert cmd == "system_get_time"
    assert params == {}

    # set_time_scale
    await system_handlers.system_set_time_scale(runtime, time_scale=2.5)
    cmd, params = runtime.last_command
    assert cmd == "system_set_time_scale"
    assert params["time_scale"] == 2.5

    # get_clipboard
    await system_handlers.system_get_clipboard(runtime)
    cmd, params = runtime.last_command
    assert cmd == "system_get_clipboard"

    # set_clipboard
    await system_handlers.system_set_clipboard(runtime, text="test copy")
    cmd, params = runtime.last_command
    assert cmd == "system_set_clipboard"
    assert params["text"] == "test copy"

    # get_env
    await system_handlers.system_get_env(runtime, var_name="PATH")
    cmd, params = runtime.last_command
    assert cmd == "system_get_env"
    assert params["var_name"] == "PATH"

    # set_env
    await system_handlers.system_set_env(runtime, var_name="MY_VAR", value="123")
    cmd, params = runtime.last_command
    assert cmd == "system_set_env"
    assert params["value"] == "123"


@pytest.mark.asyncio
async def test_light_handlers():
    runtime = _FakeRuntime()

    # scaffold_light_3d
    await light_handlers.light_scaffold_light_3d(
        runtime,
        type="OmniLight3D",
        parent_path="Root",
        name="Torch",
        color=[1.0, 0.8, 0.6],
        energy=2.0,
        range=10.0,
    )
    cmd, params = runtime.last_command
    assert cmd == "light_scaffold_light_3d"
    assert params["type"] == "OmniLight3D"
    assert params["name"] == "Torch"
    assert params["range"] == 10.0

    # scaffold_light_2d
    await light_handlers.light_scaffold_light_2d(
        runtime,
        type="PointLight2D",
        parent_path="Root2D",
        name="Lamp2D",
        energy=1.5,
    )
    cmd, params = runtime.last_command
    assert cmd == "light_scaffold_light_2d"
    assert params["name"] == "Lamp2D"

    # scaffold_decal
    await light_handlers.light_scaffold_decal(
        runtime,
        parent_path="Root",
        name="BloodStain",
        size=[1.0, 1.0, 1.0],
        texture_albedo="res://blood.png",
    )
    cmd, params = runtime.last_command
    assert cmd == "light_scaffold_decal"
    assert params["texture_albedo"] == "res://blood.png"

    # scaffold_probe
    await light_handlers.light_scaffold_probe(
        runtime,
        type="ReflectionProbe",
        parent_path="Root",
        name="RoomReflection",
        size=[5.0, 5.0, 5.0],
    )
    cmd, params = runtime.last_command
    assert cmd == "light_scaffold_probe"
    assert params["type"] == "ReflectionProbe"

    # set_light_properties
    await light_handlers.light_set_light_properties(
        runtime,
        light_path="Root/Torch",
        energy=3.0,
        volumetric_fog_energy=0.5,
    )
    cmd, params = runtime.last_command
    assert cmd == "light_set_light_properties"
    assert params["energy"] == 3.0
    assert params["volumetric_fog_energy"] == 0.5

    # get_light_info
    await light_handlers.light_get_light_info(runtime, light_path="Root/Torch")
    cmd, params = runtime.last_command
    assert cmd == "light_get_light_info"
    assert params["light_path"] == "Root/Torch"


@pytest.mark.asyncio
async def test_http_handlers():
    runtime = _FakeRuntime()

    # scaffold_http_request
    await http_handlers.http_scaffold_http_request(
        runtime, parent_path="Root", name="ApiRequester", timeout=15.0
    )
    cmd, params = runtime.last_command
    assert cmd == "http_scaffold_http_request"
    assert params["name"] == "ApiRequester"
    assert params["timeout"] == 15.0

    # send_request
    await http_handlers.http_send_request(
        runtime,
        url="https://api.example.com/data",
        method="POST",
        headers=["Content-Type: application/json"],
        body='{"query": "test"}',
        timeout=12.0,
    )
    cmd, params = runtime.last_command
    assert cmd == "http_send_request"
    assert params["method"] == "POST"
    assert params["body"] == '{"query": "test"}'

    # download_file
    await http_handlers.http_download_file(
        runtime,
        url="https://example.com/asset.zip",
        target_path="user://asset.zip",
        timeout=45.0,
    )
    cmd, params = runtime.last_command
    assert cmd == "http_download_file"
    assert params["target_path"] == "user://asset.zip"


@pytest.mark.asyncio
async def test_shader_global_handlers():
    runtime = _FakeRuntime()

    # list_globals
    await shader_global_handlers.shader_global_list_globals(runtime)
    cmd, params = runtime.last_command
    assert cmd == "shader_global_list_globals"
    assert params == {}

    # set_global
    await shader_global_handlers.shader_global_set_global(
        runtime, name="player_position", value=[10.0, 5.0, 2.0]
    )
    cmd, params = runtime.last_command
    assert cmd == "shader_global_set_global"
    assert params["name"] == "player_position"
    assert params["value"] == [10.0, 5.0, 2.0]

    # add_global
    await shader_global_handlers.shader_global_add_global(
        runtime, name="wind_direction", type="vec3", value=[1.0, 0.0, 0.0]
    )
    cmd, params = runtime.last_command
    assert cmd == "shader_global_add_global"
    assert params["type"] == "vec3"

    # remove_global
    await shader_global_handlers.shader_global_remove_global(runtime, name="wind_direction")
    cmd, params = runtime.last_command
    assert cmd == "shader_global_remove_global"
    assert params["name"] == "wind_direction"


@pytest.mark.asyncio
async def test_recording_handlers():
    runtime = _FakeRuntime()

    # capture_viewport
    await recording_handlers.recording_capture_viewport(
        runtime, target_path="res://frame.png", viewport_path="Root/SubViewport"
    )
    cmd, params = runtime.last_command
    assert cmd == "recording_capture_viewport"
    assert params["target_path"] == "res://frame.png"
    assert params["viewport_path"] == "Root/SubViewport"

    # configure_movie_writer
    await recording_handlers.recording_configure_movie_writer(
        runtime, movie_file="res://gameplay.avi", fps=30, quality=0.9
    )
    cmd, params = runtime.last_command
    assert cmd == "recording_configure_movie_writer"
    assert params["movie_file"] == "res://gameplay.avi"
    assert params["fps"] == 30
    assert params["quality"] == 0.9

    # get_writer_status
    await recording_handlers.recording_get_writer_status(runtime)
    cmd, params = runtime.last_command
    assert cmd == "recording_get_writer_status"
    assert params == {}


@pytest.mark.asyncio
async def test_server_registers_v5_0_23_tools():
    server = create_server()
    tools = {t.name for t in await server.list_tools()}
    expected = {
        "pck_manage",
        "system_manage",
        "light_manage",
        "http_manage",
        "shader_global_manage",
        "recording_manage",
    }
    assert expected.issubset(tools)
    assert len(tools) >= 79
