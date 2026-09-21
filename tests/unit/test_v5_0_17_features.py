"""Unit tests for v5.0.17 features: dialogue, save, fsm, theme presets, and sound manager."""

from __future__ import annotations

import pytest

from godot_ai.handlers import audio as audio_handlers
from godot_ai.handlers import dialogue as dialogue_handlers
from godot_ai.handlers import fsm as fsm_handlers
from godot_ai.handlers import save as save_handlers
from godot_ai.handlers import theme as theme_handlers


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
        return {"project_open": True, "writable": True}

    def get_active_session(self):
        return None

    @property
    def last_command(self) -> tuple[str, dict]:
        return self.sent[-1]["command"], self.sent[-1]["params"]


@pytest.mark.asyncio
async def test_dialogue_scaffold_system_dispatches():
    runtime = _FakeRuntime()
    result = await dialogue_handlers.dialogue_scaffold_system(
        runtime,
        name="DialogueManager",
        script_path="res://scripts/dialogue_manager.gd",
        scene_path="res://scenes/dialogue_box.tscn",
        register_autoload=True,
        typewriter_speed=0.04,
    )
    assert result is not None
    cmd, params = runtime.last_command
    assert cmd == "dialogue_scaffold_system"
    assert params["name"] == "DialogueManager"
    assert params["typewriter_speed"] == 0.04


@pytest.mark.asyncio
async def test_dialogue_create_dispatches():
    runtime = _FakeRuntime()
    result = await dialogue_handlers.dialogue_create(
        runtime,
        path="res://dialogues/quest.json",
        dialogue_id="quest_intro",
        nodes={"start": {"text": "Hello"}},
        overwrite=True,
    )
    assert result is not None
    cmd, params = runtime.last_command
    assert cmd == "dialogue_create"
    assert params["path"] == "res://dialogues/quest.json"
    assert params["dialogue_id"] == "quest_intro"
    assert params["overwrite"] is True


@pytest.mark.asyncio
async def test_save_scaffold_save_system_dispatches():
    runtime = _FakeRuntime()
    result = await save_handlers.save_scaffold_save_system(
        runtime,
        name="SaveManager",
        script_path="res://scripts/save_manager.gd",
        save_directory="user://saves/",
        register_autoload=True,
        enable_encryption=True,
        encryption_password="secret_passphrase",
    )
    assert result is not None
    cmd, params = runtime.last_command
    assert cmd == "save_scaffold_save_system"
    assert params["enable_encryption"] is True
    assert params["encryption_password"] == "secret_passphrase"


@pytest.mark.asyncio
async def test_save_slot_operations_dispatch():
    runtime = _FakeRuntime()
    await save_handlers.save_save_slot(
        runtime,
        slot_name="slot_test",
        data={"score": 100},
        directory="user://saves/",
    )
    cmd, params = runtime.last_command
    assert cmd == "save_save_slot"
    assert params["slot_name"] == "slot_test"
    assert params["data"] == {"score": 100}

    await save_handlers.save_load_slot(
        runtime,
        slot_name="slot_test",
        directory="user://saves/",
    )
    cmd, params = runtime.last_command
    assert cmd == "save_load_slot"
    assert params["slot_name"] == "slot_test"

    await save_handlers.save_list_slots(runtime, directory="user://saves/")
    cmd, params = runtime.last_command
    assert cmd == "save_list_slots"

    await save_handlers.save_delete_slot(runtime, slot_name="slot_test")
    cmd, params = runtime.last_command
    assert cmd == "save_delete_slot"
    assert params["slot_name"] == "slot_test"


@pytest.mark.asyncio
async def test_fsm_scaffold_fsm_dispatches():
    runtime = _FakeRuntime()
    result = await fsm_handlers.fsm_scaffold_fsm(
        runtime,
        target_node_path="Enemy",
        name="StateMachine",
        script_dir="res://scripts/fsm/",
        preset="enemy_ai",
        custom_states=["Idle", "Attack"],
        initial_state="Idle",
    )
    assert result is not None
    cmd, params = runtime.last_command
    assert cmd == "fsm_scaffold_fsm"
    assert params["target_node_path"] == "Enemy"
    assert params["preset"] == "enemy_ai"
    assert params["custom_states"] == ["Idle", "Attack"]


@pytest.mark.asyncio
async def test_theme_apply_preset_dispatches():
    runtime = _FakeRuntime()
    result = await theme_handlers.theme_apply_preset(
        runtime,
        preset="cyberpunk_neon",
        theme_path="res://assets/themes/cyberpunk.tres",
        node_path="UI",
        set_as_default=True,
        overwrite=True,
    )
    assert result is not None
    cmd, params = runtime.last_command
    assert cmd == "theme_apply_preset"
    assert params["preset"] == "cyberpunk_neon"
    assert params["theme_path"] == "res://assets/themes/cyberpunk.tres"
    assert params["set_as_default"] is True


@pytest.mark.asyncio
async def test_audio_scaffold_sound_manager_dispatches():
    runtime = _FakeRuntime()
    result = await audio_handlers.audio_scaffold_sound_manager(
        runtime,
        name="SoundManager",
        script_path="res://scripts/sound_manager.gd",
        pool_size=24,
        bus="SFX",
        register_autoload=True,
    )
    assert result is not None
    cmd, params = runtime.last_command
    assert cmd == "audio_scaffold_sound_manager"
    assert params["name"] == "SoundManager"
    assert params["pool_size"] == 24
