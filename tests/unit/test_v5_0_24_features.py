"""Unit tests for v5.0.24 features: 11 new engine management domains."""

from __future__ import annotations

import pytest

from godot_ai.handlers import animation_tree as animation_tree_handlers
from godot_ai.handlers import config as config_handlers
from godot_ai.handlers import editor_settings as editor_settings_handlers
from godot_ai.handlers import font as font_handlers
from godot_ai.handlers import joint as joint_handlers
from godot_ai.handlers import network as network_handlers
from godot_ai.handlers import occluder as occluder_handlers
from godot_ai.handlers import parallax as parallax_handlers
from godot_ai.handlers import sprite as sprite_handlers
from godot_ai.handlers import texture as texture_handlers
from godot_ai.handlers import visual_shader as visual_shader_handlers
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
async def test_texture_handlers():
    runtime = _FakeRuntime()
    await texture_handlers.texture_create_image(
        runtime, width=128, height=128, format="rgb8", fill_color="#ff0000"
    )
    cmd, params = runtime.last_command
    assert cmd == "texture_create_image"
    assert params["width"] == 128
    assert params["height"] == 128
    assert params["format"] == "rgb8"
    assert params["fill_color"] == "#ff0000"

    await texture_handlers.texture_create_atlas(
        runtime, atlas_path="res://sheet.png", region_rect=[0, 0, 16, 16]
    )
    cmd, params = runtime.last_command
    assert cmd == "texture_create_atlas"
    assert params["atlas_path"] == "res://sheet.png"
    assert params["region_rect"] == [0, 0, 16, 16]

    await texture_handlers.texture_get_texture_info(runtime, path="res://icon.svg")
    cmd, params = runtime.last_command
    assert cmd == "texture_get_texture_info"
    assert params["path"] == "res://icon.svg"


@pytest.mark.asyncio
async def test_font_handlers():
    runtime = _FakeRuntime()
    await font_handlers.font_create_system_font(
        runtime, font_names=["Arial"], italic=True, weight=700
    )
    cmd, params = runtime.last_command
    assert cmd == "font_create_system_font"
    assert params["font_names"] == ["Arial"]
    assert params["italic"] is True
    assert params["weight"] == 700

    await font_handlers.font_create_label_settings(
        runtime, font_size=24, font_color="#ffff00"
    )
    cmd, params = runtime.last_command
    assert cmd == "font_create_label_settings"
    assert params["font_size"] == 24
    assert params["font_color"] == "#ffff00"


@pytest.mark.asyncio
async def test_network_handlers():
    runtime = _FakeRuntime()
    await network_handlers.network_scaffold_tcp_server(
        runtime, port=9999, bind_address="127.0.0.1"
    )
    cmd, params = runtime.last_command
    assert cmd == "network_scaffold_tcp_server"
    assert params["port"] == 9999
    assert params["bind_address"] == "127.0.0.1"

    await network_handlers.network_get_network_interfaces(runtime)
    cmd, params = runtime.last_command
    assert cmd == "network_get_network_interfaces"


@pytest.mark.asyncio
async def test_visual_shader_handlers():
    runtime = _FakeRuntime()
    await visual_shader_handlers.visual_shader_create_visual_shader(
        runtime, shader_type="canvas_item"
    )
    cmd, params = runtime.last_command
    assert cmd == "visual_shader_create_visual_shader"
    assert params["shader_type"] == "canvas_item"

    await visual_shader_handlers.visual_shader_connect_nodes(
        runtime, shader_path="res://test.tres", from_node=1, to_node=2
    )
    cmd, params = runtime.last_command
    assert cmd == "visual_shader_connect_nodes"
    assert params["from_node"] == 1
    assert params["to_node"] == 2


@pytest.mark.asyncio
async def test_animation_tree_handlers():
    runtime = _FakeRuntime()
    await animation_tree_handlers.animation_tree_scaffold_state_machine(
        runtime, anim_player_path="AnimationPlayer"
    )
    cmd, params = runtime.last_command
    assert cmd == "animation_tree_scaffold_state_machine"
    assert params["anim_player_path"] == "AnimationPlayer"

    await animation_tree_handlers.animation_tree_add_state(
        runtime, tree_path="AnimationTree", state_name="idle", animation_name="idle"
    )
    cmd, params = runtime.last_command
    assert cmd == "animation_tree_add_state"
    assert params["state_name"] == "idle"


@pytest.mark.asyncio
async def test_sprite_handlers():
    runtime = _FakeRuntime()
    await sprite_handlers.sprite_create_sprite_frames(
        runtime, animations=[{"name": "walk", "fps": 10.0, "loop": True}]
    )
    cmd, params = runtime.last_command
    assert cmd == "sprite_create_sprite_frames"
    assert params["animations"][0]["name"] == "walk"

    await sprite_handlers.sprite_scaffold_multimesh(
        runtime, mesh_type="sphere", instance_count=50
    )
    cmd, params = runtime.last_command
    assert cmd == "sprite_scaffold_multimesh"
    assert params["mesh_type"] == "sphere"
    assert params["instance_count"] == 50


@pytest.mark.asyncio
async def test_editor_settings_handlers():
    runtime = _FakeRuntime()
    await editor_settings_handlers.editor_settings_get_setting(
        runtime, setting_name="interface/theme/accent_color"
    )
    cmd, params = runtime.last_command
    assert cmd == "editor_settings_get_setting"
    assert params["setting_name"] == "interface/theme/accent_color"

    await editor_settings_handlers.editor_settings_get_editor_paths(runtime)
    cmd, params = runtime.last_command
    assert cmd == "editor_settings_get_editor_paths"


@pytest.mark.asyncio
async def test_joint_handlers():
    runtime = _FakeRuntime()
    await joint_handlers.joint_scaffold_joint_2d(
        runtime, joint_type="pin", node_a_path="BodyA", node_b_path="BodyB"
    )
    cmd, params = runtime.last_command
    assert cmd == "joint_scaffold_joint_2d"
    assert params["joint_type"] == "pin"
    assert params["node_a_path"] == "BodyA"

    await joint_handlers.joint_scaffold_joint_3d(
        runtime, joint_type="hinge", node_a_path="BodyA3D"
    )
    cmd, params = runtime.last_command
    assert cmd == "joint_scaffold_joint_3d"
    assert params["joint_type"] == "hinge"


@pytest.mark.asyncio
async def test_occluder_handlers():
    runtime = _FakeRuntime()
    await occluder_handlers.occluder_scaffold_occluder_3d(
        runtime, occluder_type="box", size=[2.0, 2.0, 2.0]
    )
    cmd, params = runtime.last_command
    assert cmd == "occluder_scaffold_occluder_3d"
    assert params["occluder_type"] == "box"
    assert params["size"] == [2.0, 2.0, 2.0]


@pytest.mark.asyncio
async def test_config_handlers():
    runtime = _FakeRuntime()
    await config_handlers.config_config_write(
        runtime, file_path="user://save.cfg", section="player", key="hp", value=100
    )
    cmd, params = runtime.last_command
    assert cmd == "config_config_write"
    assert params["section"] == "player"
    assert params["value"] == 100

    await config_handlers.config_json_parse(runtime, json_string='{"score": 42}')
    cmd, params = runtime.last_command
    assert cmd == "config_json_parse"
    assert params["json_string"] == '{"score": 42}'


@pytest.mark.asyncio
async def test_parallax_handlers():
    runtime = _FakeRuntime()
    await parallax_handlers.parallax_scaffold_parallax(
        runtime, scroll_scale=[0.5, 0.5], repeat_size=[512.0, 0.0]
    )
    cmd, params = runtime.last_command
    assert cmd == "parallax_scaffold_parallax"
    assert params["scroll_scale"] == [0.5, 0.5]
    assert params["repeat_size"] == [512.0, 0.0]

    await parallax_handlers.parallax_scaffold_canvas_layer(
        runtime, layer=2, follow_viewport=True
    )
    cmd, params = runtime.last_command
    assert cmd == "parallax_scaffold_canvas_layer"
    assert params["layer"] == 2
    assert params["follow_viewport"] is True


@pytest.mark.asyncio
async def test_server_registers_v5_0_24_tools():
    server = create_server()
    tools = {t.name for t in await server.list_tools()}
    expected = {
        "texture_manage",
        "font_manage",
        "network_manage",
        "visual_shader_manage",
        "animation_tree_manage",
        "sprite_manage",
        "editor_settings_manage",
        "joint_manage",
        "occluder_manage",
        "config_manage",
        "parallax_manage",
    }
    assert expected.issubset(tools)
    assert len(tools) == 90
