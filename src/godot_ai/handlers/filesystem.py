"""Shared handlers for filesystem tools."""

from __future__ import annotations

import io
from pathlib import Path
import zipfile

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
        "id": "kenney-pixel-platformer",
        "title": "Kenney Pixel Platformer",
        "category": "tileset",
        "tags": ["2d", "platformer", "pixel", "tileset", "characters"],
        "description": "18x18 pixel art tileset with grass, dirt, snow, ice, spikes, coins, and characters.",
        "url": "https://raw.githubusercontent.com/KenneyNL/Starter-Kits/master/2D%20Platformer/assets/tilemap-characters_packed.png",
        "format": "png",
        "license": "CC0 (Public Domain)",
    },
    {
        "id": "kenney-tiny-dungeon",
        "title": "Kenney Tiny Dungeon",
        "category": "tileset",
        "tags": ["2d", "dungeon", "rpg", "pixel", "topdown", "fantasy"],
        "description": "16x16 topdown dungeon tileset with stone walls, floors, doors, chests, monsters, and heroes.",
        "url": "https://raw.githubusercontent.com/KenneyNL/Starter-Kits/master/2D%20Dungeon/assets/tilemap_packed.png",
        "format": "png",
        "license": "CC0 (Public Domain)",
    },
    {
        "id": "kenney-1bit-pack",
        "title": "Kenney 1-Bit Pack",
        "category": "tileset",
        "tags": ["2d", "retro", "1bit", "roguelike", "monochrome"],
        "description": "Monochrome 16x16 retro roguelike tiles, monsters, weapons, and terrain.",
        "url": "https://raw.githubusercontent.com/KenneyNL/Starter-Kits/master/2D%20Roguelike/assets/monochrome_tilemap_packed.png",
        "format": "png",
        "license": "CC0 (Public Domain)",
    },
    {
        "id": "kenney-topdown-shooter",
        "title": "Kenney Topdown Shooter",
        "category": "tileset",
        "tags": ["2d", "topdown", "shooter", "action", "military"],
        "description": "Topdown terrain, asphalt, barricades, soldiers, weapons, and blood splatters.",
        "url": "https://raw.githubusercontent.com/KenneyNL/Starter-Kits/master/2D%20Top-Down%20Shooter/assets/tilemap_packed.png",
        "format": "png",
        "license": "CC0 (Public Domain)",
    },
    {
        "id": "kenney-retro-sfx-jump",
        "title": "Retro SFX - Jump",
        "category": "audio",
        "tags": ["audio", "sfx", "retro", "jump", "platformer", "8bit"],
        "description": "Classic 8-bit jump sound effect for platformers.",
        "url": "https://raw.githubusercontent.com/KenneyNL/Starter-Kits/master/2D%20Platformer/audio/jump.ogg",
        "format": "ogg",
        "license": "CC0 (Public Domain)",
    },
    {
        "id": "kenney-retro-sfx-coin",
        "title": "Retro SFX - Coin / Pickup",
        "category": "audio",
        "tags": ["audio", "sfx", "retro", "coin", "pickup", "item"],
        "description": "Chime sound for collecting coins or powerups.",
        "url": "https://raw.githubusercontent.com/KenneyNL/Starter-Kits/master/2D%20Platformer/audio/coin.ogg",
        "format": "ogg",
        "license": "CC0 (Public Domain)",
    },
    {
        "id": "kenney-retro-sfx-hit",
        "title": "Retro SFX - Hurt / Damage",
        "category": "audio",
        "tags": ["audio", "sfx", "retro", "hurt", "damage", "impact"],
        "description": "Crunchy hit sound for player or enemy taking damage.",
        "url": "https://raw.githubusercontent.com/KenneyNL/Starter-Kits/master/2D%20Platformer/audio/hurt.ogg",
        "format": "ogg",
        "license": "CC0 (Public Domain)",
    },
    {
        "id": "kenney-ui-click",
        "title": "UI SFX - Click",
        "category": "audio",
        "tags": ["audio", "sfx", "ui", "button", "click"],
        "description": "Crisp interface button press sound.",
        "url": "https://raw.githubusercontent.com/KenneyNL/Starter-Kits/master/2D%20Platformer/audio/click.ogg",
        "format": "ogg",
        "license": "CC0 (Public Domain)",
    },
    {
        "id": "kenney-prototype-textures",
        "title": "Kenney Prototype Textures",
        "category": "texture",
        "tags": ["3d", "texture", "grid", "prototype", "graybox"],
        "description": "Level prototyping grid textures with metric markings.",
        "url": "https://raw.githubusercontent.com/KenneyNL/Starter-Kits/master/3D%20Platformer/assets/textures/prototype_grid.png",
        "format": "png",
        "license": "CC0 (Public Domain)",
    },
    {
        "id": "kenney-crosshair-pack",
        "title": "Kenney Crosshair Pack",
        "category": "ui",
        "tags": ["2d", "ui", "crosshair", "fps", "hud"],
        "description": "Vector and pixel crosshairs for shooters and first-person games.",
        "url": "https://raw.githubusercontent.com/KenneyNL/Starter-Kits/master/3D%20FPS/assets/crosshair.png",
        "format": "png",
        "license": "CC0 (Public Domain)",
    },
]


async def filesystem_download_asset(
    runtime: DirectRuntime,
    url: str,
    path: str,
    extract: bool = False,
    reimport: bool = True,
) -> dict:
    """Download an asset from the internet directly into the Godot project.

    Writes the asset to `path` (must be a res:// path).
    If extract is True (or if URL/path ends in .zip), extracts the archive into `path`.
    Automatically triggers Godot's reimport and scan so the editor immediately indexes it.
    """
    await require_writable_async(runtime)

    if not url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid URL scheme, must be http:// or https://: {url}")

    if not path.startswith("res://"):
        raise ValueError(f"Path must be a 'res://' path, got: {path}")

    active = runtime._registry.active_session
    if active and active.project_path:
        project_root = Path(active.project_path)
    else:
        project_root = Path.cwd()

    rel_subpath = path[6:].lstrip("/\\")
    dest_path = project_root / rel_subpath

    async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        content = response.content

    is_zip = extract or url.lower().endswith(".zip") or path.lower().endswith(".zip")
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
                reimported_info = await runtime.send_command("reimport", {"paths": [path]})
            else:
                reimported_info = await runtime.send_command("scan_filesystem", {})
        except Exception:
            pass

    return {
        "url": url,
        "path": path,
        "size_bytes": len(content),
        "is_archive": is_zip,
        "extracted_files": extracted_files,
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
            searchable = f"{item['id']} {item['title']} {item['description']} {' '.join(item['tags'])}".lower()
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


