from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from godot_ai.handlers import audio as audio_handlers
from godot_ai.handlers import autoload as autoload_handlers
from godot_ai.handlers import character as character_handlers
from godot_ai.handlers import environment as environment_handlers
from godot_ai.handlers import input_map as input_map_handlers
from godot_ai.handlers import project as project_handlers
from godot_ai.runtime.direct import DirectRuntime
from godot_ai.sessions.registry import SessionRegistry
from tests.conftest import create_test_server as create_server


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
        return {"ok": True}


@pytest.mark.asyncio
async def test_character_scaffold_2d_forwards_parameters():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    with patch("godot_ai.handlers.character.require_writable_async", new=AsyncMock()):
        await character_handlers.character_scaffold_2d(
            runtime,
            parent_path="/Root",
            name="Hero2D",
            genre="platformer",
            speed=250.0,
            jump_velocity=-400.0,
            acceleration=1500.0,
            friction=1200.0,
            coyote_time=0.15,
            jump_buffering=0.12,
            attach_camera=True,
            script_path="res://scripts/hero.gd",
        )

    assert client.calls[-1]["command"] == "character_scaffold_2d"
    assert client.calls[-1]["params"] == {
        "parent_path": "/Root",
        "name": "Hero2D",
        "genre": "platformer",
        "speed": 250.0,
        "jump_velocity": -400.0,
        "acceleration": 1500.0,
        "friction": 1200.0,
        "coyote_time": 0.15,
        "jump_buffering": 0.12,
        "attach_camera": True,
        "script_path": "res://scripts/hero.gd",
    }


@pytest.mark.asyncio
async def test_character_scaffold_3d_forwards_parameters():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    with patch("godot_ai.handlers.character.require_writable_async", new=AsyncMock()):
        await character_handlers.character_scaffold_3d(
            runtime,
            parent_path="/Level",
            name="PlayerFPS",
            genre="first_person",
            speed=6.0,
            sprint_speed=10.0,
            jump_velocity=5.0,
            mouse_sensitivity=0.003,
            script_path="res://scripts/player_fps.gd",
        )

    assert client.calls[-1]["command"] == "character_scaffold_3d"
    assert client.calls[-1]["params"] == {
        "parent_path": "/Level",
        "name": "PlayerFPS",
        "genre": "first_person",
        "speed": 6.0,
        "sprint_speed": 10.0,
        "jump_velocity": 5.0,
        "mouse_sensitivity": 0.003,
        "script_path": "res://scripts/player_fps.gd",
    }


@pytest.mark.asyncio
async def test_input_map_scaffold_preset():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    with patch("godot_ai.handlers.input_map.require_writable_async", new=AsyncMock()):
        await input_map_handlers.input_map_scaffold_preset(runtime, preset="wasd_topdown")

    assert client.calls[-1]["command"] == "input_map_scaffold_preset"
    assert client.calls[-1]["params"] == {"preset": "wasd_topdown"}


@pytest.mark.asyncio
async def test_project_apply_preset():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    with patch("godot_ai.handlers.project.require_writable_async", new=AsyncMock()):
        await project_handlers.project_apply_preset(
            runtime, preset="pixel_art_2d", viewport_width=320, viewport_height=180
        )

    assert client.calls[-1]["command"] == "project_apply_preset"
    assert client.calls[-1]["params"] == {
        "preset": "pixel_art_2d",
        "viewport_width": 320,
        "viewport_height": 180,
    }


@pytest.mark.asyncio
async def test_environment_setup_2d():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    with patch("godot_ai.handlers.environment.require_writable_async", new=AsyncMock()):
        await environment_handlers.environment_setup_2d(
            runtime,
            preset="midnight",
            parent_path="/Level2D",
            add_torch_to="/Level2D/Player",
            torch_energy=1.5,
            torch_radius=2.5,
            shadows=True,
        )

    assert client.calls[-1]["command"] == "environment_setup_2d"
    assert client.calls[-1]["params"] == {
        "preset": "midnight",
        "parent_path": "/Level2D",
        "add_torch_to": "/Level2D/Player",
        "torch_energy": 1.5,
        "torch_radius": 2.5,
        "shadows": True,
    }


@pytest.mark.asyncio
async def test_autoload_scaffold_game_manager():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    with patch("godot_ai.handlers.autoload.require_writable_async", new=AsyncMock()):
        await autoload_handlers.autoload_scaffold_game_manager(
            runtime,
            name="GameManager",
            script_path="res://scripts/game_manager.gd",
            max_lives=5,
        )

    assert client.calls[-1]["command"] == "autoload_scaffold_game_manager"
    assert client.calls[-1]["params"] == {
        "name": "GameManager",
        "script_path": "res://scripts/game_manager.gd",
        "max_lives": 5,
    }


@pytest.mark.asyncio
async def test_audio_scaffold_music_player():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    with patch("godot_ai.handlers.audio.require_writable_async", new=AsyncMock()):
        await audio_handlers.audio_scaffold_music_player(
            runtime,
            parent_path="/Root",
            name="BgmPlayer",
            stream_path="res://music/theme.ogg",
            autoplay=True,
            volume_db=-3.0,
            bus="Music",
            loop=True,
        )

    assert client.calls[-1]["command"] == "audio_scaffold_music_player"
    assert client.calls[-1]["params"] == {
        "parent_path": "/Root",
        "name": "BgmPlayer",
        "stream_path": "res://music/theme.ogg",
        "autoplay": True,
        "volume_db": -3.0,
        "bus": "Music",
        "loop": True,
    }


@pytest.mark.asyncio
async def test_server_registers_character_manage():
    server = create_server()
    tools = await server.list_tools()
    tool_names = {t.name for t in tools}
    assert "character_manage" in tool_names
