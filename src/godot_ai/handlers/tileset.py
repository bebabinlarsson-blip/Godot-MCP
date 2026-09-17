"""Shared handlers for TileSet management tools."""

from __future__ import annotations

from godot_ai.runtime.direct import DirectRuntime


async def tileset_get_atlas_tiles(
    runtime: DirectRuntime,
    tileset_path: str,
    source_id: int,
) -> dict:
    """Return all occupied atlas positions for one source in a TileSet.

    Calls the GDScript ``get_atlas_tiles`` handler (read-only) and returns
    its result unchanged.

    Args:
        runtime:       In-process runtime adapter.
        tileset_path:  ``res://`` path to the ``.tres`` TileSet resource.
        source_id:     Integer index of the ``TileSetAtlasSource`` to query.

    Returns:
        ``{"data": {"tiles": [{"col": int, "row": int}, ...], "count": int}}`` on
        success, or an error dict from the GDScript handler.
    """
    return await runtime.send_command(
        "tileset_get_atlas_tiles",
        {
            "tileset_path": tileset_path,
            "source_id": source_id,
        },
    )


async def tileset_get_atlas_image(
    runtime: DirectRuntime,
    tileset_path: str,
    source_id: int,
    max_size: int = 0,
) -> dict:
    """Return the atlas texture of a TileSetAtlasSource as a Base64-encoded PNG.

    Reads the ``TileSetAtlasSource.texture`` directly from the resource —
    no UI interaction required.  The image can optionally be downscaled for
    faster transfer.

    Args:
        runtime:       In-process runtime adapter.
        tileset_path:  ``res://`` path to the ``.tres`` TileSet resource.
        source_id:     Integer index of the ``TileSetAtlasSource`` to query.
        max_size:      If > 0, scale the image so its longest edge is at most
                       this many pixels.  0 (default) = full resolution.

    Returns:
          ``{"data": {"image_base64": str, "width": int, "height": int,
              "original_width": int, "original_height": int, "format": "png"}}``
        on success, or an error dict from the GDScript handler.
    """
    return await runtime.send_command(
        "tileset_get_atlas_image",
        {
            "tileset_path": tileset_path,
            "source_id": source_id,
            "max_size": max_size,
        },
    )
