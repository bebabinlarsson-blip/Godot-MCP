"""Unit tests for v5.0.22 features: path_manage, mesh_manage,
rendering_manage, skeleton_manage, crypto_manage, and plugin_manage.
"""

from __future__ import annotations

import pytest

from godot_ai.handlers import crypto as crypto_handlers
from godot_ai.handlers import mesh as mesh_handlers
from godot_ai.handlers import path as path_handlers
from godot_ai.handlers import plugin as plugin_handlers
from godot_ai.handlers import rendering as rendering_handlers
from godot_ai.handlers import skeleton as skeleton_handlers
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
async def test_path_handlers():
    runtime = _FakeRuntime()

    # create_curve_2d
    await path_handlers.path_create_curve_2d(
        runtime, points=[[0, 0], [10, 10]], closed=True, save_path="res://curve.tres"
    )
    cmd, params = runtime.last_command
    assert cmd == "path_create_curve_2d"
    assert params["closed"] is True
    assert params["save_path"] == "res://curve.tres"

    # create_curve_3d
    await path_handlers.path_create_curve_3d(
        runtime, points=[[0, 0, 0], [5, 5, 5]], closed=False
    )
    cmd, params = runtime.last_command
    assert cmd == "path_create_curve_3d"

    # scaffold_path
    await path_handlers.path_scaffold_path(
        runtime, parent_path="Root", type="Path3D", name="MyPath", with_follow=True
    )
    cmd, params = runtime.last_command
    assert cmd == "path_scaffold_path"
    assert params["name"] == "MyPath"

    # sample_baked_points
    await path_handlers.path_sample_baked_points(
        runtime, path_node_path="Root/MyPath", interval=2.0
    )
    cmd, params = runtime.last_command
    assert cmd == "path_sample_baked_points"
    assert params["interval"] == 2.0

    # generate_spline
    await path_handlers.path_generate_spline(
        runtime, shape="circle", radius=10.0, points_count=20
    )
    cmd, params = runtime.last_command
    assert cmd == "path_generate_spline"
    assert params["shape"] == "circle"


@pytest.mark.asyncio
async def test_mesh_handlers():
    runtime = _FakeRuntime()

    # generate_surface_mesh
    await mesh_handlers.mesh_generate_surface_mesh(
        runtime,
        vertices=[[0, 0, 0], [1, 0, 0], [0, 1, 0]],
        indices=[0, 1, 2],
        generate_normals=True,
    )
    cmd, params = runtime.last_command
    assert cmd == "mesh_generate_surface_mesh"
    assert len(params["vertices"]) == 3
    assert params["generate_normals"] is True

    # deform_mesh
    await mesh_handlers.mesh_deform_mesh(
        runtime, mesh_path="res://mesh.tres", mode="displace", factor=2.0
    )
    cmd, params = runtime.last_command
    assert cmd == "mesh_deform_mesh"
    assert params["factor"] == 2.0

    # create_primitive
    await mesh_handlers.mesh_create_primitive(
        runtime, primitive="SphereMesh", properties={"radius": 2.5}
    )
    cmd, params = runtime.last_command
    assert cmd == "mesh_create_primitive"
    assert params["primitive"] == "SphereMesh"

    # get_mesh_info
    await mesh_handlers.mesh_get_mesh_info(runtime, mesh_path="res://mesh.tres")
    cmd, params = runtime.last_command
    assert cmd == "mesh_get_mesh_info"


@pytest.mark.asyncio
async def test_rendering_handlers():
    runtime = _FakeRuntime()

    # scaffold_world_environment
    await rendering_handlers.rendering_scaffold_world_environment(
        runtime, sky_mode="procedural", tonemap_mode="aces"
    )
    cmd, params = runtime.last_command
    assert cmd == "rendering_scaffold_world_environment"
    assert params["sky_mode"] == "procedural"

    # set_environment_effects
    await rendering_handlers.rendering_set_environment_effects(
        runtime, glow_enabled=True, glow_intensity=0.8, ssao_enabled=True
    )
    cmd, params = runtime.last_command
    assert cmd == "rendering_set_environment_effects"
    assert params["glow_enabled"] is True

    # set_camera_attributes
    await rendering_handlers.rendering_set_camera_attributes(
        runtime, camera_path="Root/Camera3D", attributes_type="practical"
    )
    cmd, params = runtime.last_command
    assert cmd == "rendering_set_camera_attributes"

    # apply_lighting_preset
    await rendering_handlers.rendering_apply_lighting_preset(
        runtime, preset="scifi_cyberpunk"
    )
    cmd, params = runtime.last_command
    assert cmd == "rendering_apply_lighting_preset"
    assert params["preset"] == "scifi_cyberpunk"

    # get_environment_info
    await rendering_handlers.rendering_get_environment_info(runtime)
    cmd, _ = runtime.last_command
    assert cmd == "rendering_get_environment_info"


@pytest.mark.asyncio
async def test_skeleton_handlers():
    runtime = _FakeRuntime()

    # get_skeleton_info
    await skeleton_handlers.skeleton_get_skeleton_info(runtime, skeleton_path="Root/Skeleton3D")
    cmd, params = runtime.last_command
    assert cmd == "skeleton_get_skeleton_info"

    # set_bone_pose
    await skeleton_handlers.skeleton_set_bone_pose(
        runtime, skeleton_path="Root/Skeleton3D", bone_name="Head", position=[0, 1.5, 0]
    )
    cmd, params = runtime.last_command
    assert cmd == "skeleton_set_bone_pose"
    assert params["bone_name"] == "Head"

    # scaffold_bone_attachment
    await skeleton_handlers.skeleton_scaffold_bone_attachment(
        runtime, skeleton_path="Root/Skeleton3D", bone_name="RightHand"
    )
    cmd, params = runtime.last_command
    assert cmd == "skeleton_scaffold_bone_attachment"

    # scaffold_ragdoll
    await skeleton_handlers.skeleton_scaffold_ragdoll(
        runtime, skeleton_path="Root/Skeleton3D", total_mass=80.0
    )
    cmd, params = runtime.last_command
    assert cmd == "skeleton_scaffold_ragdoll"
    assert params["total_mass"] == 80.0


@pytest.mark.asyncio
async def test_crypto_handlers():
    runtime = _FakeRuntime()

    # hash_file
    await crypto_handlers.crypto_hash_file(runtime, file_path="res://icon.svg", algorithm="sha256")
    cmd, params = runtime.last_command
    assert cmd == "crypto_hash_file"
    assert params["algorithm"] == "sha256"

    # hash_string
    await crypto_handlers.crypto_hash_string(runtime, content="hello", algorithm="md5")
    cmd, params = runtime.last_command
    assert cmd == "crypto_hash_string"

    # generate_random_bytes
    await crypto_handlers.crypto_generate_random_bytes(runtime, size=16, format="hex")
    cmd, params = runtime.last_command
    assert cmd == "crypto_generate_random_bytes"
    assert params["size"] == 16

    # generate_rsa_key
    await crypto_handlers.crypto_generate_rsa_key(runtime, key_size=2048, save_path="res://key.key")
    cmd, params = runtime.last_command
    assert cmd == "crypto_generate_rsa_key"

    # generate_self_signed_cert
    await crypto_handlers.crypto_generate_self_signed_cert(
        runtime, cert_save_path="res://cert.crt", common_name="localhost"
    )
    cmd, params = runtime.last_command
    assert cmd == "crypto_generate_self_signed_cert"

    # hmac_digest
    await crypto_handlers.crypto_hmac_digest(runtime, key="secret", message="payload")
    cmd, params = runtime.last_command
    assert cmd == "crypto_hmac_digest"


@pytest.mark.asyncio
async def test_plugin_handlers():
    runtime = _FakeRuntime()

    # list_plugins
    await plugin_handlers.plugin_list_plugins(runtime, addons_dir="res://addons")
    cmd, params = runtime.last_command
    assert cmd == "plugin_list_plugins"

    # set_plugin_enabled
    await plugin_handlers.plugin_set_plugin_enabled(runtime, plugin_name="godot_ai", enabled=True)
    cmd, params = runtime.last_command
    assert cmd == "plugin_set_plugin_enabled"
    assert params["enabled"] is True

    # scaffold_plugin
    await plugin_handlers.plugin_scaffold_plugin(
        runtime, plugin_id="test_addon", plugin_name="Test Addon", with_dock=True
    )
    cmd, params = runtime.last_command
    assert cmd == "plugin_scaffold_plugin"
    assert params["plugin_id"] == "test_addon"


@pytest.mark.asyncio
async def test_server_registers_v5_0_22_tools():
    server = create_server()
    tools = {t.name for t in await server.list_tools()}
    expected = {
        "path_manage",
        "mesh_manage",
        "rendering_manage",
        "skeleton_manage",
        "crypto_manage",
        "plugin_manage",
    }
    assert expected.issubset(tools)
    assert len(tools) >= 73
