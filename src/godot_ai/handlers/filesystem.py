"""Shared handlers for filesystem tools."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import httpx

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime
from godot_ai.tools._pagination import paginate


async def filesystem_read_text(runtime: DirectRuntime, path: str) -> dict:
    return await runtime.send_command("read_file", {"path": path})


async def filesystem_write_text(runtime: DirectRuntime, path: str, content: str = "") -> dict:
    await require_writable_async(runtime)
    return await runtime.send_command(
        "write_file",
        {"path": path, "content": content},
    )


async def filesystem_reimport(runtime: DirectRuntime, paths: list[str]) -> dict:
    await require_writable_async(runtime)
    return await runtime.send_command("reimport", {"paths": paths})


async def filesystem_scan(runtime: DirectRuntime) -> dict:
    """Force a full editor filesystem scan and wait for it to settle.

    Registers ``class_name`` scripts added since the last scan into the global
    class table — the headless equivalent of the editor regaining window focus.

    Deliberately not ``require_writable``-gated: a scan is a refresh and must
    run even while the editor reports ``"importing"`` (a scan already in
    flight), where the plugin's single-flight handler simply awaits the running
    scan. A full scan can exceed the default command timeout on large projects,
    and the plugin caps its own wait at 28s, so a 35s command timeout leaves
    headroom.
    """
    return await runtime.send_command("scan_filesystem", {}, timeout=35.0)


async def filesystem_search(
    runtime: DirectRuntime,
    name: str = "",
    type: str = "",
    path: str = "",
    offset: int = 0,
    limit: int = 100,
) -> dict:
    params: dict[str, str] = {}
    if name:
        params["name"] = name
    if type:
        params["type"] = type
    if path:
        params["path"] = path
    result = await runtime.send_command("search_filesystem", params)
    return paginate(result.get("files", []), offset, limit, key="files")


async def filesystem_list(
    runtime: DirectRuntime,
    path: str = "res://",
    recursive: bool = False,
    max_depth: int = 1,
) -> dict:
    return await runtime.send_command(
        "list_files",
        {"path": path, "recursive": recursive, "max_depth": max_depth},
    )


async def filesystem_delete(runtime: DirectRuntime, path: str) -> dict:
    await require_writable_async(runtime)
    return await runtime.send_command("delete_file", {"path": path})


async def filesystem_move(
    runtime: DirectRuntime,
    from_path: str,
    to_path: str,
) -> dict:
    await require_writable_async(runtime)
    return await runtime.send_command(
        "move_file",
        {"from_path": from_path, "to_path": to_path},
    )


CC0_ASSET_CATALOG: list[dict] = [
    {
        "id": "godot-platformer-tiles",
        "title": "Godot Platformer Tileset",
        "category": "tileset",
        "tags": ["2d", "platformer", "tileset", "terrain", "tiles"],
        "description": "High-quality 2D platformer tileset with grass, dirt, stone, and hazards.",
        "url": "https://raw.githubusercontent.com/godotengine/godot-demo-projects/master/2d/platformer/level/tiles.webp",
        "format": "webp",
        "license": "CC0 / MIT (Godot Demo)",
    },
    {
        "id": "kenney-coin-sprite",
        "title": "Kenney Animated Coin",
        "category": "texture",
        "tags": ["2d", "spritesheet", "coin", "pickup", "gold"],
        "description": "Gold coin sprite for collectibles and currency.",
        "url": "https://raw.githubusercontent.com/KenneyNL/Starter-Kit-3D-Platformer/main/sprites/coin.png",
        "format": "png",
        "license": "CC0 (Public Domain)",
    },
    {
        "id": "godot-platformer-props",
        "title": "Godot Foliage Prop - Tree",
        "category": "texture",
        "tags": ["2d", "prop", "tree", "foliage", "nature"],
        "description": "Tree prop for 2D level decoration.",
        "url": "https://raw.githubusercontent.com/godotengine/godot-demo-projects/master/2d/platformer/level/props/tree_1.webp",
        "format": "webp",
        "license": "CC0 / MIT (Godot Demo)",
    },
    {
        "id": "godot-dodge-enemy",
        "title": "Godot 2D Enemy Character",
        "category": "texture",
        "tags": ["2d", "enemy", "character", "sprite", "creature"],
        "description": "Walking creature enemy sprite for 2D games.",
        "url": "https://raw.githubusercontent.com/godotengine/godot-demo-projects/master/2d/dodge_the_creeps/art/enemyWalking_1.png",
        "format": "png",
        "license": "CC0 / MIT (Godot Demo)",
    },
    {
        "id": "kenney-sfx-jump",
        "title": "Sound Effect - Jump",
        "category": "audio",
        "tags": ["audio", "sfx", "jump", "action"],
        "description": "Crisp jump sound effect.",
        "url": "https://raw.githubusercontent.com/KenneyNL/Starter-Kit-3D-Platformer/main/sounds/jump.ogg",
        "format": "ogg",
        "license": "CC0 (Public Domain)",
    },
    {
        "id": "kenney-sfx-coin",
        "title": "Sound Effect - Coin Pickup",
        "category": "audio",
        "tags": ["audio", "sfx", "coin", "pickup", "chime"],
        "description": "Chime sound for collecting coins or items.",
        "url": "https://raw.githubusercontent.com/KenneyNL/Starter-Kit-3D-Platformer/main/sounds/coin.ogg",
        "format": "ogg",
        "license": "CC0 (Public Domain)",
    },
    {
        "id": "kenney-sfx-break",
        "title": "Sound Effect - Break / Impact",
        "category": "audio",
        "tags": ["audio", "sfx", "break", "smash", "impact"],
        "description": "Crunchy break and impact sound effect.",
        "url": "https://raw.githubusercontent.com/KenneyNL/Starter-Kit-3D-Platformer/main/sounds/break.ogg",
        "format": "ogg",
        "license": "CC0 (Public Domain)",
    },
    {
        "id": "godot-sfx-gameover",
        "title": "Sound Effect - Game Over",
        "category": "audio",
        "tags": ["audio", "sfx", "gameover", "fail", "retro"],
        "description": "Classic game over fanfare sound effect.",
        "url": "https://raw.githubusercontent.com/godotengine/godot-demo-projects/master/2d/dodge_the_creeps/art/gameover.wav",
        "format": "wav",
        "license": "CC0 / MIT (Godot Demo)",
    },
    {
        "id": "godot-platformer-music",
        "title": "Background Music - Platformer Theme",
        "category": "audio",
        "tags": ["audio", "music", "bgm", "soundtrack", "theme"],
        "description": "Full looping background music track for action and platformer games.",
        "url": "https://raw.githubusercontent.com/godotengine/godot-demo-projects/master/2d/platformer/music.ogg",
        "format": "ogg",
        "license": "CC0 / MIT (Godot Demo)",
    },
    {
        "id": "kenney-palette-texture",
        "title": "Kenney Color Palette Texture",
        "category": "texture",
        "tags": ["texture", "palette", "colormap", "materials"],
        "description": "Color atlas map for low-poly models and prototyping.",
        "url": "https://raw.githubusercontent.com/KenneyNL/Starter-Kit-3D-Platformer/main/models/Textures/colormap.png",
        "format": "png",
        "license": "CC0 (Public Domain)",
    },
]


async def filesystem_download_asset(
    runtime: DirectRuntime,
    url: str,
    path: str = "",
    dest: str = "",
    extract: bool = False,
    filter: str = "",
    reimport: bool = True,
) -> dict:
    """Download an asset from the internet directly into the Godot project.

    Writes the asset to `path` or `dest` (must be a res:// path).
    If extract is True (or if URL/path ends in .zip), extracts the archive into the target folder.
    If filter is 'nearest', configures project-wide nearest-neighbor texture filtering.
    Automatically triggers Godot's reimport and scan so the editor immediately indexes it.
    """
    await require_writable_async(runtime)

    if not url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid URL scheme, must be http:// or https://: {url}")

    effective_path = path or dest
    if not effective_path:
        url_file = Path(url.split("?")[0]).name or "downloaded_asset"
        effective_path = f"res://assets/{url_file}"

    if not effective_path.startswith("res://"):
        raise ValueError(f"Path must be a 'res://' path, got: {effective_path}")

    filter_applied = None
    if filter and filter.lower() in ("nearest", "pixel", "nearest_neighbor"):
        try:
            await runtime.send_command(
                "set_project_setting",
                {"key": "rendering/textures/canvas_textures/default_texture_filter", "value": 0},
            )
            filter_applied = "nearest"
        except Exception:
            filter_applied = "nearest (fallback)"

    active = runtime._registry.get_active()
    if active and active.project_path:
        project_root = Path(active.project_path)
    else:
        project_root = Path.cwd()

    rel_subpath = effective_path[6:].lstrip("/\\")
    dest_path = project_root / rel_subpath

    async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        content = response.content

    is_zip = extract or url.lower().endswith(".zip") or effective_path.lower().endswith(".zip")
    extracted_files: list[str] = []

    if is_zip:
        dest_path.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            for member in zf.infolist():
                target = (dest_path / member.filename).resolve()
                if not target.is_relative_to(dest_path.resolve()):
                    continue
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(member) as src, open(target, "wb") as dst:
                        dst.write(src.read())
                    extracted_files.append(str(target.relative_to(project_root)).replace("\\", "/"))
    else:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_bytes(content)

    reimported_info = {}
    if reimport:
        try:
            if not is_zip:
                reimported_info = await runtime.send_command(
                    "reimport", {"paths": [effective_path]}
                )
            else:
                reimported_info = await runtime.send_command("scan_filesystem", {})
        except Exception:
            pass

    return {
        "url": url,
        "path": effective_path,
        "dest": effective_path,
        "size_bytes": len(content),
        "is_archive": is_zip,
        "extracted_files": extracted_files,
        "filter_applied": filter_applied,
        "reimport_result": reimported_info,
    }


def filesystem_search_assets(
    runtime: DirectRuntime,
    query: str = "",
    category: str = "all",
    limit: int = 20,
) -> dict:
    """Search vetted free / CC0 game assets (tilesets, audio, textures, UI, 3D models).

    Returns ready-to-download asset specs with direct URLs.
    """
    q = query.lower().strip()
    cat = category.lower().strip()

    matches = []
    for item in CC0_ASSET_CATALOG:
        if cat != "all" and item["category"].lower() != cat:
            continue
        if q:
            tags_str = " ".join(item["tags"])
            searchable = f"{item['id']} {item['title']} {item['description']} {tags_str}".lower()
            if q not in searchable:
                tokens = q.split()
                if not all(t in searchable for t in tokens):
                    continue
        matches.append(item)
        if len(matches) >= limit:
            break

    return {
        "query": query,
        "category": category,
        "total_results": len(matches),
        "assets": matches,
    }


