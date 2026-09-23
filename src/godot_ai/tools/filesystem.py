"""MCP tool for project filesystem read/write/search/reimport."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import filesystem as filesystem_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Project filesystem access via the Godot editor's EditorFileSystem.

Ops:
  • read_text(path)
        Read a text file at a ``res://`` path. Returns content, size,
        line_count.
  • write_text(path, content="")
        Create or overwrite a text file. Updates the editor filesystem
        entry for that one file (single-file update, not a full scan).
        Newly-created files include ``data.cleanup.rm`` for transient
        smoke tests; overwrite omits the field.
  • reimport(paths)
        Force-reimport the listed files via ``EditorFileSystem.update_file``.
        ``paths`` is a list of res:// paths.
        Intended for imported assets such as textures, models, and audio.
        Paths that are not imported resources (``.gd`` scripts, ``.tscn``,
        hand-written ``.tres``, or an asset the editor has not imported yet)
        report under ``skipped_non_imported`` rather than ``reimported``: their
        filesystem entry is refreshed, but no import runs, so a success there is
        not evidence that a script parsed or that diagnostics were produced. Use
        ``script_patch``/``script_create`` to save a script and receive fresh
        diagnostics, or ``scan`` for an asset awaiting its first import.
        Returns ``reimported``, ``skipped_non_imported``, ``not_found`` and their
        counts.
  • list(path="res://", recursive=False, max_depth=1)
        Browse the project's res:// tree (files, sizes, UIDs, and directories).
  • delete(path)
        Delete a file or directory from the project along with its .uid and .import sidecars.
  • move(from_path, to_path)
        Move or rename a file in the project, keeping sidecars consistent.
  • scan()
        Force a full ``EditorFileSystem.scan()`` and wait for it to settle.
        This is the headless equivalent of the editor regaining window focus:
        ``write_text``/``script_create`` register single files but do NOT
        rebuild the global ``class_name`` table, so a freshly-created
        ``class_name MyThing extends Resource`` is invisible to
        ``resource_manage``/type references until a scan runs. Call this once
        after adding ``class_name`` scripts when the editor isn't focused.
        Single-flight (awaits any in-progress scan rather than stacking another).
        Returns ``scan_completed`` and ``global_classes_registered_delta``.
  • search(name="", type="", path="", offset=0, limit=100)
        Find files by name, resource type, or path substring. At least one
        filter must be set. Paginated.
  • download_and_import(url, dest="", path="", extract=False, filter="", reimport=True)
        Download an asset or archive, optionally unpack, configure filter
        ("nearest" for pixel art), and trigger Godot reimport and scan.
  • download_asset(url, path="", dest="", extract=False, filter="", reimport=True)
        Download an asset or zip archive from the internet directly into the
        Godot project (res:// path). If extract=True or archive is zip, extracts
        into target directory. Automatically triggers editor reimport and scan.
        Returns: {url, path, size_bytes, is_archive, extracted_files, filter_applied}
  • search_assets(query="", category="all", limit=20)
        Search curated free/CC0 game assets (tilesets, audio, textures, UI, 3D models).
        Categories: "all", "tileset", "audio", "texture", "ui".
        Returns matching assets with direct download URLs ready for download_asset.
"""


def register_filesystem_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="filesystem_manage",
        description=_DESCRIPTION,
        ops={
            "read_text": filesystem_handlers.filesystem_read_text,
            "read_file": filesystem_handlers.filesystem_read_text,
            "read": filesystem_handlers.filesystem_read_text,
            "write_text": filesystem_handlers.filesystem_write_text,
            "write_file": filesystem_handlers.filesystem_write_text,
            "write": filesystem_handlers.filesystem_write_text,
            "list": filesystem_handlers.filesystem_list,
            "list_dir": filesystem_handlers.filesystem_list,
            "list_files": filesystem_handlers.filesystem_list,
            "ls": filesystem_handlers.filesystem_list,
            "tree": filesystem_handlers.filesystem_list,
            "delete": filesystem_handlers.filesystem_delete,
            "delete_file": filesystem_handlers.filesystem_delete,
            "move": filesystem_handlers.filesystem_move,
            "move_file": filesystem_handlers.filesystem_move,
            "reimport": filesystem_handlers.filesystem_reimport,
            "scan": filesystem_handlers.filesystem_scan,
            "search": filesystem_handlers.filesystem_search,
            "download_and_import": filesystem_handlers.filesystem_download_asset,
            "download_asset": filesystem_handlers.filesystem_download_asset,
            "download_file": filesystem_handlers.filesystem_download_asset,
            "search_assets": filesystem_handlers.filesystem_search_assets,
            "asset_search": filesystem_handlers.filesystem_search_assets,
        },
        read_resource_forms={
            ## File reads/searches/lists are per-call queries with arbitrary path
            ## or query inputs; no fixed-URI resource shape fits.
            "read_text": None,
            "read_file": None,
            "read": None,
            "list": None,
            "list_dir": None,
            "list_files": None,
            "ls": None,
            "tree": None,
            "search": None,
            ## `scan` is an editor action (not require_writable — it must run
            ## while readiness is "importing" to await an in-flight scan), so
            ## the lint classes it as a read; it has no resource-URI form.
            "scan": None,
            "search_assets": None,
            "asset_search": None,
        },
    )
