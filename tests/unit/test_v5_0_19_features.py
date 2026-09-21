"""Unit tests for v5.0.19 features: localization_manage, geometry_manage,
audio bus management, physics 3D queries, and project get_info.
"""

from __future__ import annotations

import pytest

from godot_ai.handlers import audio as audio_handlers
from godot_ai.handlers import geometry as geom_handlers
from godot_ai.handlers import localization as loc_handlers
from godot_ai.handlers import physics as physics_handlers
from godot_ai.handlers import project as project_handlers
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
async def test_localization_handlers():
    runtime = _FakeRuntime()

    # scaffold_csv
    await loc_handlers.localization_scaffold_csv(
        runtime, path="res://locale.csv", languages=["en", "fr"]
    )
    cmd, params = runtime.last_command
    assert cmd == "localization_scaffold_csv"
    assert params["path"] == "res://locale.csv"
    assert params["languages"] == ["en", "fr"]

    # add_entry
    await loc_handlers.localization_add_entry(
        runtime, path="res://locale.csv", key="KEY_PLAY", translations={"en": "Play", "fr": "Jouer"}
    )
    cmd, params = runtime.last_command
    assert cmd == "localization_add_entry"
    assert params["key"] == "KEY_PLAY"
    assert params["translations"]["en"] == "Play"

    # get_locales
    await loc_handlers.localization_get_locales(runtime)
    cmd, _ = runtime.last_command
    assert cmd == "localization_get_locales"

    # set_locale
    await loc_handlers.localization_set_locale(runtime, locale="fr")
    cmd, params = runtime.last_command
    assert cmd == "localization_set_locale"
    assert params["locale"] == "fr"

    # translate
    await loc_handlers.localization_translate(runtime, message="KEY_PLAY")
    cmd, params = runtime.last_command
    assert cmd == "localization_translate"
    assert params["message"] == "KEY_PLAY"

    # extract_strings
    await loc_handlers.localization_extract_strings(runtime, root_dir="res://scripts")
    cmd, params = runtime.last_command
    assert cmd == "localization_extract_strings"
    assert params["root_dir"] == "res://scripts"


@pytest.mark.asyncio
async def test_geometry_handlers():
    runtime = _FakeRuntime()

    # polygon_boolean
    await geom_handlers.geometry_polygon_boolean(
        runtime,
        operation="intersect",
        poly_a=[[0, 0], [10, 0], [10, 10]],
        poly_b=[[5, 5], [15, 5], [15, 15]],
    )
    cmd, params = runtime.last_command
    assert cmd == "geometry_polygon_boolean"
    assert params["operation"] == "intersect"

    # polygon_offset
    await geom_handlers.geometry_polygon_offset(
        runtime, polygon=[[0, 0], [10, 0], [10, 10]], delta=2.0
    )
    cmd, params = runtime.last_command
    assert cmd == "geometry_polygon_offset"
    assert params["delta"] == 2.0

    # triangulate
    await geom_handlers.geometry_triangulate(runtime, polygon=[[0, 0], [10, 0], [10, 10]])
    cmd, params = runtime.last_command
    assert cmd == "geometry_triangulate"

    # convex_hull
    await geom_handlers.geometry_convex_hull(runtime, points=[[0, 0], [5, 5], [10, 0]])
    cmd, params = runtime.last_command
    assert cmd == "geometry_convex_hull"

    # scaffold_polygon_2d
    await geom_handlers.geometry_scaffold_polygon_2d(
        runtime, parent_path="/root", points=[[0, 0], [10, 0], [10, 10]], is_collision=True
    )
    cmd, params = runtime.last_command
    assert cmd == "geometry_scaffold_polygon_2d"
    assert params["is_collision"] is True

    # generate_mesh
    await geom_handlers.geometry_generate_mesh(
        runtime, mesh_type="cube", size=[2.0, 2.0, 2.0], parent_path="/root"
    )
    cmd, params = runtime.last_command
    assert cmd == "geometry_generate_mesh"
    assert params["mesh_type"] == "cube"


@pytest.mark.asyncio
async def test_physics_new_handlers():
    runtime = _FakeRuntime()

    # query_point_3d
    await physics_handlers.physics_query_point_3d(runtime, point=[1.0, 2.0, 3.0])
    cmd, params = runtime.last_command
    assert cmd == "physics_query_point_3d"
    assert params["point"] == [1.0, 2.0, 3.0]

    # shapecast_scaffold
    await physics_handlers.physics_shapecast_scaffold(
        runtime, parent_path="/root", shape_type="box", is_2d=True
    )
    cmd, params = runtime.last_command
    assert cmd == "physics_shapecast_scaffold"
    assert params["shape_type"] == "box"
    assert params["is_2d"] is True

    # set_layer_names
    await physics_handlers.physics_set_layer_names(
        runtime, layer_type="3d_physics", layers={"1": "World", "2": "Enemies"}
    )
    cmd, params = runtime.last_command
    assert cmd == "physics_set_layer_names"
    assert params["layer_type"] == "3d_physics"
    assert params["layers"] == {"1": "World", "2": "Enemies"}

    # get_layer_names
    await physics_handlers.physics_get_layer_names(runtime, layer_type="2d_physics")
    cmd, params = runtime.last_command
    assert cmd == "physics_get_layer_names"
    assert params["layer_type"] == "2d_physics"


@pytest.mark.asyncio
async def test_audio_bus_handlers():
    runtime = _FakeRuntime()

    # bus_list
    await audio_handlers.audio_bus_list(runtime)
    cmd, _ = runtime.last_command
    assert cmd == "audio_bus_list"

    # bus_add
    await audio_handlers.audio_bus_add(runtime, name="Dialogue", send="Master")
    cmd, params = runtime.last_command
    assert cmd == "audio_bus_add"
    assert params["name"] == "Dialogue"
    assert params["send"] == "Master"

    # bus_remove
    await audio_handlers.audio_bus_remove(runtime, bus="Dialogue")
    cmd, params = runtime.last_command
    assert cmd == "audio_bus_remove"
    assert params["bus"] == "Dialogue"

    # bus_set_properties
    await audio_handlers.audio_bus_set_properties(runtime, bus="Master", volume_db=-3.0, mute=False)
    cmd, params = runtime.last_command
    assert cmd == "audio_bus_set_properties"
    assert params["bus"] == "Master"
    assert params["volume_db"] == -3.0

    # bus_add_effect
    await audio_handlers.audio_bus_add_effect(runtime, bus="Master", effect_type="Reverb")
    cmd, params = runtime.last_command
    assert cmd == "audio_bus_add_effect"
    assert params["effect_type"] == "Reverb"

    # bus_save_layout
    await audio_handlers.audio_bus_save_layout(runtime, path="res://default_bus_layout.tres")
    cmd, params = runtime.last_command
    assert cmd == "audio_bus_save_layout"
    assert params["path"] == "res://default_bus_layout.tres"


@pytest.mark.asyncio
async def test_project_get_info():
    runtime = _FakeRuntime()
    await project_handlers.project_get_info(runtime)
    cmd, _ = runtime.last_command
    assert cmd == "project_get_info"


@pytest.mark.asyncio
async def test_server_tools_registration():
    server = create_server()
    tools = await server.list_tools()
    tool_names = {t.name for t in tools}

    assert "localization_manage" in tool_names
    assert "geometry_manage" in tool_names
    assert "physics_manage" in tool_names
    assert "audio_manage" in tool_names
    assert "project_manage" in tool_names
