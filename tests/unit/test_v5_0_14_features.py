"""Unit tests for Godot-MCP v5.0.14 features:
1. Feature 1: Automatic Alternative Tile Collision Matrix
2. Feature 2: Terrain Bitmask Scaffolder
3. Feature 3: 8-Way Locomotion BlendSpace Generator
4. Feature 4: Particle Preset Generator (CPUParticles2D)
5. Feature 5: In-Engine Automated Playtest Runner
6. Dev Environment Fix: PyPI vs Local Git Lockout
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from godot_ai.handlers import animation as animation_handlers
from godot_ai.handlers import game as game_handlers
from godot_ai.handlers import particle as particle_handlers
from godot_ai.handlers import tileset as tileset_handlers
from godot_ai.runtime.direct import DirectRuntime
from godot_ai.sessions.registry import SessionRegistry

ROOT = Path(__file__).resolve().parents[2]
ADDONS = ROOT / "addons" / "godot_ai"
PLUGIN_ADDONS = ROOT / "plugin" / "addons" / "godot_ai"


class _StubClient:
    def __init__(self, result: dict | None = None) -> None:
        self.calls: list[dict] = []
        self._result = result or {"ok": True}

    async def send(
        self,
        command: str,
        params: dict | None = None,
        session_id: str | None = None,
        timeout: float = 5.0,
        hint_policy=None,
    ) -> dict:
        self.calls.append(
            {
                "command": command,
                "params": params or {},
                "session_id": session_id,
                "timeout": timeout,
            }
        )
        return self._result


def _runtime(client: _StubClient) -> DirectRuntime:
    return DirectRuntime(registry=SessionRegistry(), client=client)


# ============================================================================
# Feature 1: Alternative Tile Collision Synchronization
# ============================================================================


def test_tilemap_handler_has_collision_sync_and_matrix():
    source = (ADDONS / "handlers" / "tilemap_handler.gd").read_text(encoding="utf-8")
    plugin_source = (PLUGIN_ADDONS / "handlers" / "tilemap_handler.gd").read_text(encoding="utf-8")

    assert source == plugin_source
    assert "func _sync_alternative_tile_collision(" in source
    assert "Vector2(-pt.y, pt.x)" in source  # 90 deg
    assert "Vector2(-pt.x, -pt.y)" in source  # 180 deg
    assert "Vector2(pt.y, -pt.x)" in source  # 270 deg
    assert "p.x = -p.x" in source  # flip_h
    assert "p.y = -p.y" in source  # flip_v

    # Verify callers call _sync_alternative_tile_collision
    assert "_sync_alternative_tile_collision(node, src, atlas, alt, rot, flip_h, flip_v)" in source
    assert "_sync_alternative_tile_collision(node, prev.source_id" in source
    assert "new_alt, degrees)" in source
    assert "alt, 0, flip_h, flip_v)" in source


# ============================================================================
# Feature 2: Terrain Bitmask Scaffolder
# ============================================================================


@pytest.mark.asyncio
async def test_tileset_scaffold_terrain_bitmasks_python_handler():
    client = _StubClient({"data": {"tileset_path": "res://tiles.tres", "tiles_configured": 9}})
    runtime = _runtime(client)

    res = await tileset_handlers.tileset_scaffold_terrain_bitmasks(
        runtime,
        tileset_path="res://tiles.tres",
        source_id=0,
        terrain_set=0,
        terrain_id=0,
        template="simple_box",
    )

    assert client.calls[-1]["command"] == "tileset_scaffold_terrain_bitmasks"
    assert client.calls[-1]["params"]["template"] == "simple_box"
    assert res["data"]["tiles_configured"] == 9


def test_tileset_handler_gdscript_has_scaffold_templates():
    source = (ADDONS / "handlers" / "tileset_handler.gd").read_text(encoding="utf-8")
    plugin_source = (PLUGIN_ADDONS / "handlers" / "tileset_handler.gd").read_text(encoding="utf-8")

    assert source == plugin_source
    assert "func scaffold_terrain_bitmasks(" in source
    assert '"simple_box":' in source
    assert '"kenney_3x3_minimal":' in source
    assert '"rpgmaker_47":' in source
    assert "set_terrain_peering_bit" in source

    # Check plugin dispatcher registration
    plugin_gd = (ADDONS / "plugin.gd").read_text(encoding="utf-8")
    assert '"tileset_scaffold_terrain_bitmasks"' in plugin_gd


# ============================================================================
# Feature 3: 8-Way Locomotion BlendSpace Generator
# ============================================================================


@pytest.mark.asyncio
async def test_animation_scaffold_locomotion_tree_python_handler():
    client = _StubClient(
        {"data": {"path": "/World/Player/AnimationTree", "states": ["Idle", "Walk"]}}
    )
    runtime = _runtime(client)

    states = {
        "Idle": {"(0, 1)": "idle_down", "(0, -1)": "idle_up"},
        "Walk": {"(0, 1)": "walk_down", "(0, -1)": "walk_up"},
    }
    res = await animation_handlers.animation_scaffold_locomotion_tree(
        runtime,
        player_path="/World/Player",
        states=states,
    )

    assert client.calls[-1]["command"] == "animation_scaffold_locomotion_tree"
    assert client.calls[-1]["params"]["player_path"] == "/World/Player"
    assert client.calls[-1]["params"]["states"] == states
    assert res["data"]["states"] == ["Idle", "Walk"]


def test_animation_handler_gdscript_has_locomotion_tree():
    source = (ADDONS / "handlers" / "animation_handler.gd").read_text(encoding="utf-8")
    p_path = PLUGIN_ADDONS / "handlers" / "animation_handler.gd"
    plugin_source = p_path.read_text(encoding="utf-8")

    assert source == plugin_source
    assert "func scaffold_locomotion_tree(" in source
    assert "AnimationNodeBlendSpace2D.new()" in source
    assert "add_blend_point(" in source
    assert "func _parse_2d_coord(" in source

    plugin_gd = (ADDONS / "plugin.gd").read_text(encoding="utf-8")
    assert '"animation_scaffold_locomotion_tree"' in plugin_gd


# ============================================================================
# Feature 4: Particle Preset Generator
# ============================================================================


@pytest.mark.asyncio
async def test_particle_spawn_preset_2d_python_handler():
    client = _StubClient({"data": {"path": "/World/DustParticles", "preset": "dust_puff"}})
    runtime = _runtime(client)

    res = await particle_handlers.particle_spawn_preset_2d(
        runtime,
        parent_path="/World",
        preset="dust_puff",
        emitting=True,
    )

    assert client.calls[-1]["command"] == "particle_spawn_preset_2d"
    assert client.calls[-1]["params"]["preset"] == "dust_puff"
    assert res["data"]["preset"] == "dust_puff"


def test_particle_handler_gdscript_has_spawn_preset_2d():
    source = (ADDONS / "handlers" / "particle_handler.gd").read_text(encoding="utf-8")
    plugin_source = (PLUGIN_ADDONS / "handlers" / "particle_handler.gd").read_text(encoding="utf-8")

    assert source == plugin_source
    assert "func spawn_preset_2d(" in source
    assert "CPUParticles2D.new()" in source
    assert '"dust_puff":' in source
    assert '"sparks":' in source
    assert '"smoke":' in source
    assert '"ambient_leaves":' in source

    plugin_gd = (ADDONS / "plugin.gd").read_text(encoding="utf-8")
    assert '"particle_spawn_preset_2d"' in plugin_gd


# ============================================================================
# Feature 5: In-Engine Automated Playtest Runner
# ============================================================================


@pytest.mark.asyncio
async def test_game_run_playtest_suite_python_handler():
    client = _StubClient({"data": {"passed": True, "assertions_passed": 2, "assertions_total": 2}})
    runtime = _runtime(client)

    steps: list[dict[str, Any]] = [
        {"action": "move_right", "duration": 0.5},
        {
            "assert_node_property": {
                "path": "/World/Player",
                "property": "global_position.x",
                "greater_than": 50,
            }
        },
        {"assert_expression": "1 + 1 == 2"},
    ]

    res = await game_handlers.game_run_playtest_suite(runtime, steps=steps, timeout=5.0)

    assert client.calls[-1]["command"] == "game_command"
    assert client.calls[-1]["params"]["op"] == "run_playtest_suite"
    assert client.calls[-1]["params"]["params"]["steps"] == steps
    assert client.calls[-1]["params"]["params"]["timeout"] == 5.0
    assert res["data"]["passed"] is True


def test_game_helper_gdscript_has_run_playtest_suite():
    source = (ADDONS / "runtime" / "game_helper.gd").read_text(encoding="utf-8")
    plugin_source = (PLUGIN_ADDONS / "runtime" / "game_helper.gd").read_text(encoding="utf-8")

    assert source == plugin_source
    assert '"run_playtest_suite":' in source
    assert "func _run_playtest_suite(" in source
    assert "assert_node_property" in source
    assert "assert_expression" in source
    assert "func _reply_playtest_suite_ok(" in source
    assert "func _reply_playtest_suite_error(" in source

    editor_source = (ADDONS / "handlers" / "editor_handler.gd").read_text(encoding="utf-8")
    assert 'op == "run_playtest_suite"' in editor_source


# ============================================================================
# Dev Environment Fix: PyPI vs Local Git Lockout
# ============================================================================


def test_client_configurator_has_local_repo_discovery():
    source = (ADDONS / "client_configurator.gd").read_text(encoding="utf-8")
    plugin_source = (PLUGIN_ADDONS / "client_configurator.gd").read_text(encoding="utf-8")

    assert source == plugin_source
    assert "static func _find_local_repo_root() -> String:" in source
    assert "var repo_root := _find_local_repo_root()" in source
    assert "if is_dev_checkout() or not repo_root.is_empty():" in source
