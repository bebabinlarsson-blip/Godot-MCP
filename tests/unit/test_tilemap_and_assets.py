"""Unit tests for TileMap authoring and Asset search/download handlers."""

from __future__ import annotations

import pytest

from godot_ai.handlers import filesystem as filesystem_handlers
from godot_ai.handlers import tilemap as tilemap_handlers
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


async def test_tilemap_place_tile_forwards_rotation_and_flips():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    await tilemap_handlers.tilemap_place_tile(
        runtime,
        path="/Main/TileMapLayer",
        source_id=1,
        atlas_col=2,
        atlas_row=3,
        map_x=10,
        map_y=15,
        rotation_degrees=90,
        flip_h=True,
        flip_v=False,
    )

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["command"] == "tilemap_place_tile"
    assert call["params"] == {
        "path": "/Main/TileMapLayer",
        "source_id": 1,
        "atlas_col": 2,
        "atlas_row": 3,
        "map_x": 10,
        "map_y": 15,
        "rotation_degrees": 90,
        "flip_h": True,
        "flip_v": False,
        "alternative_tile": -1,
    }


async def test_tilemap_rotate_and_flip_handlers():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    await tilemap_handlers.tilemap_rotate_cell(
        runtime,
        path="/Main/TileMapLayer",
        map_x=5,
        map_y=6,
        degrees=180,
    )
    assert client.calls[-1]["command"] == "tilemap_rotate_cell"
    assert client.calls[-1]["params"] == {
        "path": "/Main/TileMapLayer",
        "map_x": 5,
        "map_y": 6,
        "degrees": 180,
    }

    await tilemap_handlers.tilemap_flip_cell(
        runtime,
        path="/Main/TileMapLayer",
        map_x=5,
        map_y=6,
        flip_h=True,
        flip_v=True,
    )
    assert client.calls[-1]["command"] == "tilemap_flip_cell"
    assert client.calls[-1]["params"] == {
        "path": "/Main/TileMapLayer",
        "map_x": 5,
        "map_y": 6,
        "flip_h": True,
        "flip_v": True,
    }


async def test_tilemap_generate_layout_forwards_genre_and_dimensions():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    await tilemap_handlers.tilemap_generate_layout(
        runtime,
        path="/Main/TileMapLayer",
        genre="dungeon",
        rect_w=40,
        rect_h=25,
        rect_x=2,
        rect_y=3,
        source_id=0,
        floor_col=0,
        floor_row=0,
        wall_col=1,
        wall_row=0,
    )

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["command"] == "tilemap_generate_layout"
    assert call["params"]["genre"] == "dungeon"
    assert call["params"]["rect_w"] == 40
    assert call["params"]["rect_h"] == 25
    assert call["params"]["rect_x"] == 2
    assert call["params"]["rect_y"] == 3


def test_asset_search_catalog():
    runtime = DirectRuntime(registry=SessionRegistry(), client=StubClient())

    res_all = filesystem_handlers.filesystem_search_assets(runtime, query="platformer")
    assert res_all["total_results"] >= 1
    assert any("platformer" in a["id"] for a in res_all["assets"])

    res_audio = filesystem_handlers.filesystem_search_assets(runtime, query="", category="audio")
    assert res_audio["total_results"] >= 1
    for a in res_audio["assets"]:
        assert a["category"] == "audio"

    res_none = filesystem_handlers.filesystem_search_assets(runtime, query="xyznonexistent123")
    assert res_none["total_results"] == 0


async def test_download_asset_validations():
    runtime = DirectRuntime(registry=SessionRegistry(), client=StubClient())

    with pytest.raises(ValueError, match="Invalid URL scheme"):
        await filesystem_handlers.filesystem_download_asset(
            runtime, "ftp://example.com/asset.png", "res://asset.png"
        )

    with pytest.raises(ValueError, match="Path must be a 'res://' path"):
        await filesystem_handlers.filesystem_download_asset(
            runtime, "https://example.com/asset.png", "/tmp/asset.png"
        )


async def test_tilemap_paint_terrain_import_matrix_scatter():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    await tilemap_handlers.tilemap_paint_terrain(
        runtime,
        path="/Main/TileMapLayer",
        terrain_set=0,
        terrain_id=1,
        cells=[[0, 0], [1, 0], [2, 0]],
    )
    assert client.calls[-1]["command"] == "tilemap_paint_terrain"
    assert client.calls[-1]["params"]["terrain_set"] == 0
    assert client.calls[-1]["params"]["terrain_id"] == 1
    assert client.calls[-1]["params"]["cells"] == [[0, 0], [1, 0], [2, 0]]

    await tilemap_handlers.tilemap_import_matrix(
        runtime,
        path="/Main/TileMapLayer",
        origin_x=10,
        origin_y=20,
        map_array=["###", "#.#", "###"],
        legend={"#": {"source_id": 0, "atlas_col": 1, "atlas_row": 0}},
    )
    assert client.calls[-1]["command"] == "tilemap_import_matrix"
    assert client.calls[-1]["params"]["origin_x"] == 10
    assert client.calls[-1]["params"]["map_array"] == ["###", "#.#", "###"]

    await tilemap_handlers.tilemap_scatter_props(
        runtime,
        parent_path="/Main/Props",
        prop_scenes=["res://tree.tscn"],
        region_rect={"x": 0, "y": 0, "w": 100, "h": 100},
        count=5,
    )
    assert client.calls[-1]["command"] == "tilemap_scatter_props"
    assert client.calls[-1]["params"]["count"] == 5


async def test_animation_and_tileset_new_handlers():
    from godot_ai.handlers import animation as animation_handlers
    from godot_ai.handlers import tileset as tileset_handlers

    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    await animation_handlers.animation_create_spritesheet_track(
        runtime,
        player_path="/Main/Player/AnimationPlayer",
        animation_name="walk",
        sprite_path="/Main/Player/Sprite2D",
        hframes=4,
        vframes=1,
        frame_count=4,
        fps=8.0,
    )
    assert client.calls[-1]["command"] == "animation_create_spritesheet_track"
    assert client.calls[-1]["params"]["fps"] == 8.0

    await animation_handlers.animation_create_animated_sprite(
        runtime,
        parent_path="/Main",
        node_name="HeroSprite",
        texture_path="res://hero.png",
        animation_name="idle",
        hframes=6,
        frame_count=6,
    )
    assert client.calls[-1]["command"] == "animation_create_animated_sprite"
    assert client.calls[-1]["params"]["node_name"] == "HeroSprite"

    await animation_handlers.animation_scaffold_state_machine(
        runtime,
        parent_path="/Main/Player",
        player_path="/Main/Player/AnimationPlayer",
        states=["idle", "run", "jump"],
    )
    assert client.calls[-1]["command"] == "animation_scaffold_state_machine"
    assert client.calls[-1]["params"]["states"] == ["idle", "run", "jump"]

    await tileset_handlers.tileset_create_from_texture(
        runtime,
        texture_path="res://tiles.png",
        save_path="res://tiles.tres",
        tile_width=32,
        tile_height=32,
    )
    assert client.calls[-1]["command"] == "tileset_create_from_texture"
    assert client.calls[-1]["params"]["tile_width"] == 32

    await tileset_handlers.tileset_create_collision_polygon(
        runtime,
        tileset_path="res://tiles.tres",
        source_id=0,
        atlas_col=1,
        atlas_row=2,
        shape_type="box",
    )
    assert client.calls[-1]["command"] == "tileset_create_collision_polygon"
    assert client.calls[-1]["params"]["shape_type"] == "box"


async def test_tilemap_paint_terrain_alias():
    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    await tilemap_handlers.tilemap_paint_terrain(
        runtime,
        path="/Main/TileMapLayer",
        terrain_set=0,
        terrain=2,
        cells=[[1, 2], [3, 4]],
    )
    assert client.calls[-1]["command"] == "tilemap_paint_terrain"
    assert client.calls[-1]["params"]["terrain_id"] == 2
    assert client.calls[-1]["params"]["terrain"] == 2
    assert client.calls[-1]["params"]["cells"] == [[1, 2], [3, 4]]


async def test_spritesheet_animation_scaffolding():
    from godot_ai.handlers import animation as animation_handlers

    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    await animation_handlers.animation_create_spritesheet_animation(
        runtime,
        target="/Player",
        texture="res://assets/player_sheet.png",
        animations={
            "idle": [0, 1, 2, 3],
            "walk": [4, 5, 6, 7],
        },
        hframes=4,
        vframes=2,
        fps=12.0,
        loop=True,
    )
    assert client.calls[-1]["command"] == "create_spritesheet_animation"
    assert client.calls[-1]["params"]["target"] == "/Player"
    assert client.calls[-1]["params"]["texture"] == "res://assets/player_sheet.png"
    assert client.calls[-1]["params"]["hframes"] == 4
    assert client.calls[-1]["params"]["vframes"] == 2
    assert client.calls[-1]["params"]["fps"] == 12.0
    assert client.calls[-1]["params"]["animations"] == {
        "idle": [0, 1, 2, 3],
        "walk": [4, 5, 6, 7],
    }


async def test_scene_instantiate_batch():
    from godot_ai.handlers import scene as scene_handlers

    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    instances = [
        {"scene_path": "res://scenes/tree.tscn", "position": {"x": 100, "y": 200}},
        {"scene_path": "res://scenes/enemy.tscn", "position": {"x": 300, "y": 400}},
    ]
    await scene_handlers.scene_instantiate_batch(
        runtime,
        instances=instances,
        parent_path="/World/Props",
    )
    assert client.calls[-1]["command"] == "instantiate_batch"
    assert client.calls[-1]["params"]["parent_path"] == "/World/Props"
    assert client.calls[-1]["params"]["instances"] == instances


async def test_game_simulate_input():
    from godot_ai.handlers import game as game_handlers

    client = StubClient()
    runtime = DirectRuntime(registry=SessionRegistry(), client=client)

    # Test action simulation with duration -> maps to input_sequence
    await game_handlers.game_simulate_input(
        runtime,
        action="move_right",
        duration=1.0,
        strength=1.0,
    )
    assert client.calls[-1]["command"] == "game_command"
    assert client.calls[-1]["params"]["op"] == "input_sequence"
    steps = client.calls[-1]["params"]["params"]["steps"]
    assert len(steps) == 2
    assert steps[0]["action"] == "move_right"
    assert steps[0]["pressed"] is True
    assert steps[0]["at_frame"] == 0
    assert steps[1]["action"] == "move_right"
    assert steps[1]["pressed"] is False
    assert steps[1]["at_frame"] == 60

