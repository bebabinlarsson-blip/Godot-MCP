"""Handler functions routing Geometry commands to the connected Godot runtime."""

from __future__ import annotations

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def geometry_polygon_boolean(
    runtime: DirectRuntime,
    operation: str = "merge",
    poly_a: list[list[float]] | None = None,
    poly_b: list[list[float]] | None = None,
) -> dict:
    """Perform 2D constructive solid polygon operations via Geometry2D."""
    return await runtime.send_command(
        "geometry_polygon_boolean",
        {
            "operation": operation,
            "poly_a": poly_a or [],
            "poly_b": poly_b or [],
        },
        timeout=10.0,
    )


async def geometry_polygon_offset(
    runtime: DirectRuntime,
    polygon: list[list[float]] | None = None,
    delta: float = 5.0,
    join_type: str = "square",
) -> dict:
    """Deflate or inflate a 2D polygon via Geometry2D.offset_polygon."""
    return await runtime.send_command(
        "geometry_polygon_offset",
        {
            "polygon": polygon or [],
            "delta": delta,
            "join_type": join_type,
        },
        timeout=10.0,
    )


async def geometry_triangulate(
    runtime: DirectRuntime,
    polygon: list[list[float]] | None = None,
) -> dict:
    """Triangulate a 2D polygon into index arrays via Geometry2D.triangulate_polygon."""
    return await runtime.send_command(
        "geometry_triangulate",
        {"polygon": polygon or []},
        timeout=10.0,
    )


async def geometry_convex_hull(
    runtime: DirectRuntime,
    points: list[list[float]] | None = None,
) -> dict:
    """Compute 2D convex hull around an array of points via Geometry2D.convex_hull."""
    return await runtime.send_command(
        "geometry_convex_hull",
        {"points": points or []},
        timeout=10.0,
    )


async def geometry_scaffold_polygon_2d(
    runtime: DirectRuntime,
    parent_path: str = "",
    points: list[list[float]] | None = None,
    polygon_name: str = "CustomPolygon",
    is_collision: bool = False,
    color: list[float] | None = None,
) -> dict:
    """Scaffold a Polygon2D or CollisionPolygon2D in the active scene."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "geometry_scaffold_polygon_2d",
        {
            "parent_path": parent_path,
            "points": points or [[-50, -50], [50, -50], [50, 50], [-50, 50]],
            "polygon_name": polygon_name,
            "is_collision": is_collision,
            "color": color or [1.0, 1.0, 1.0, 1.0],
        },
        timeout=15.0,
    )


async def geometry_generate_mesh(
    runtime: DirectRuntime,
    mesh_type: str = "cube",
    size: list[float] | None = None,
    dest_path: str = "",
    parent_path: str = "",
) -> dict:
    """Generate procedural 3D mesh via SurfaceTool and save or attach to scene."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "geometry_generate_mesh",
        {
            "mesh_type": mesh_type,
            "size": size or [2.0, 2.0, 2.0],
            "dest_path": dest_path,
            "parent_path": parent_path,
        },
        timeout=20.0,
    )
