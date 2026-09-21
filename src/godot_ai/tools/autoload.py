"""MCP tool for autoload (singleton) management."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import autoload as autoload_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Autoload (global singleton) management. Autoloads are scripts or scenes
loaded automatically at project start, accessible globally by name when
``singleton=True``. Persisted to ``project.godot``.

Ops:
  • list()
        List autoloads with name, path, and singleton flag.
  • add(name, path, singleton=True)
        Register an autoload (script or PackedScene) by ``res://`` path.
  • remove(name)
        Unregister an autoload by name. The underlying file is not deleted.
  • scaffold_game_manager(name="GameManager",
                          script_path="res://scripts/game_manager.gd",
                          max_lives=3)
        Scaffold and register a production-ready GameManager singleton with
        score, lives, level tracking, typed signals, and scene transition methods.
"""


def register_autoload_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="autoload_manage",
        description=_DESCRIPTION,
        ops={
            "list": autoload_handlers.autoload_list,
            "add": autoload_handlers.autoload_add,
            "remove": autoload_handlers.autoload_remove,
            "scaffold_game_manager": autoload_handlers.autoload_scaffold_game_manager,
        },
        read_resource_forms={
            "list": None,  ## No aggregate autoload resource yet.
        },
    )
