"""Unit tests for Godot-MCP v5.0.15 features.

Validates:
- Procedural audio synthesizer and audio bus scaffolding
- Responsive UI screen scaffolding (menus, HUD, game over, dialogs)
- 2D and 3D navigation regions, agents, and baking
- 3D environment and lighting scaffolding with presets
- 2D follow camera scaffolding with trauma-based screen shake
- Scene diagnostics / scene doctor
- Adaptive client timeouts for heavy engine operations
"""

from __future__ import annotations

import pytest

from godot_ai.godot_client.client import _ADAPTIVE_COMMAND_TIMEOUTS
from godot_ai.handlers import audio as audio_handlers
from godot_ai.handlers import camera as camera_handlers
from godot_ai.handlers import environment as environment_handlers
from godot_ai.handlers import navigation as nav_handlers
from godot_ai.handlers import scene as scene_handlers
from godot_ai.handlers import ui as ui_handlers
from godot_ai.runtime.direct import DirectRuntime
from godot_ai.sessions.registry import SessionRegistry


class StubClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def send(
        self,
        command,
        params=None,
        session_id=None,
        timeout=5.0,
        hint_policy=None,
    ):
        self.calls.append(
            {
                "command": command,
                "params": params or {},
                "session_id": session_id,
                "timeout": timeout,
                "hint_policy": hint_policy,
            }
        )
        return {"data": {"ok": True}}


@pytest.mark.asyncio
async def test_audio_generate_procedural_sfx_forwarding():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    await audio_handlers.audio_generate_procedural_sfx(
        runtime,
        preset="jump",
        dest_path="res://audio/jump.wav",
        duration=0.3,
        sample_rate=22050,
    )

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["command"] == "audio_generate_procedural_sfx"
    assert call["params"] == {
        "preset": "jump",
        "dest_path": "res://audio/jump.wav",
        "duration": 0.3,
        "sample_rate": 22050,
    }


@pytest.mark.asyncio
async def test_audio_scaffold_buses_forwarding():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    await audio_handlers.audio_scaffold_buses(
        runtime,
        volumes={"Music": -6.0, "SFX": 0.0, "UI": -3.0},
    )

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["command"] == "audio_scaffold_buses"
    assert call["params"] == {"volumes": {"Music": -6.0, "SFX": 0.0, "UI": -3.0}}


@pytest.mark.asyncio
async def test_ui_scaffold_screen_forwarding():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    await ui_handlers.ui_scaffold_screen(
        runtime,
        kind="main_menu",
        name="TitleMenu",
        title="Epic Adventure",
        layer=5,
        buttons=["Play", "Settings", "Exit"],
    )

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["command"] == "ui_scaffold_screen"
    assert call["params"] == {
        "kind": "main_menu",
        "parent_path": "",
        "name": "TitleMenu",
        "title": "Epic Adventure",
        "layer": 5,
        "buttons": ["Play", "Settings", "Exit"],
    }


@pytest.mark.asyncio
async def test_navigation_setup_region_2d_forwarding():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    await nav_handlers.navigation_setup_region_2d(
        runtime,
        name="LevelNavRegion",
        polygon=[[-100.0, -100.0], [100.0, -100.0], [100.0, 100.0], [-100.0, 100.0]],
        cell_size=2.0,
        agent_radius=12.0,
    )

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["command"] == "navigation_setup_region_2d"
    assert call["params"]["name"] == "LevelNavRegion"
    assert len(call["params"]["polygon"]) == 4
    assert call["params"]["cell_size"] == 2.0
    assert call["params"]["agent_radius"] == 12.0


@pytest.mark.asyncio
async def test_navigation_attach_agent_2d_forwarding():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    await nav_handlers.navigation_attach_agent_2d(
        runtime,
        node_path="/root/Scene/Enemy",
        agent_name="NavAgent",
        radius=20.0,
        max_speed=200.0,
    )

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["command"] == "navigation_attach_agent_2d"
    assert call["params"]["node_path"] == "/root/Scene/Enemy"
    assert call["params"]["radius"] == 20.0
    assert call["params"]["max_speed"] == 200.0


@pytest.mark.asyncio
async def test_navigation_bake_2d_forwarding():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    await nav_handlers.navigation_bake_2d(runtime, region_path="/root/Scene/NavRegion")

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["command"] == "navigation_bake_2d"
    assert call["params"]["region_path"] == "/root/Scene/NavRegion"


@pytest.mark.asyncio
async def test_navigation_setup_region_3d_forwarding():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    await nav_handlers.navigation_setup_region_3d(
        runtime,
        name="NavRegion3D",
        cell_size=0.5,
        agent_radius=0.6,
    )

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["command"] == "navigation_setup_region_3d"
    assert call["params"]["cell_size"] == 0.5
    assert call["params"]["agent_radius"] == 0.6


@pytest.mark.asyncio
async def test_environment_setup_3d_forwarding():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    await environment_handlers.environment_setup_3d(
        runtime,
        preset="sunset",
        create_sun=True,
        volumetric_fog=True,
    )

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["command"] == "environment_setup_3d"
    assert call["params"]["preset"] == "sunset"
    assert call["params"]["create_sun"] is True
    assert call["params"]["volumetric_fog"] is True


@pytest.mark.asyncio
async def test_camera_scaffold_follow_2d_forwarding():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    await camera_handlers.camera_scaffold_follow_2d(
        runtime,
        target_path="/root/Scene/Player",
        smoothing_speed=8.0,
        enable_shake=True,
        zoom=[1.5, 1.5],
    )

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["command"] == "camera_scaffold_follow_2d"
    assert call["params"]["target_path"] == "/root/Scene/Player"
    assert call["params"]["smoothing_speed"] == 8.0
    assert call["params"]["enable_shake"] is True
    assert call["params"]["zoom"] == [1.5, 1.5]


@pytest.mark.asyncio
async def test_scene_diagnose_forwarding():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    await scene_handlers.scene_diagnose(runtime, root_path="/root/Scene")

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["command"] == "scene_diagnose"
    assert call["params"]["root_path"] == "/root/Scene"


def test_adaptive_command_timeouts_configuration():
    assert "filesystem_scan" in _ADAPTIVE_COMMAND_TIMEOUTS
    assert "navigation_bake_2d" in _ADAPTIVE_COMMAND_TIMEOUTS
    assert "navigation_bake_3d" in _ADAPTIVE_COMMAND_TIMEOUTS
    assert "scene_diagnose" in _ADAPTIVE_COMMAND_TIMEOUTS
    assert _ADAPTIVE_COMMAND_TIMEOUTS["navigation_bake_2d"] >= 30.0
    assert _ADAPTIVE_COMMAND_TIMEOUTS["scene_diagnose"] >= 30.0
