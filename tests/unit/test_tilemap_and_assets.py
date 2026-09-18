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
        await filesystem_handlers.filesystem_download_asset(runtime, "ftp://example.com/asset.png", "res://asset.png")

    with pytest.raises(ValueError, match="Path must be a 'res://' path"):
        await filesystem_handlers.filesystem_download_asset(runtime, "https://example.com/asset.png", "/tmp/asset.png")
