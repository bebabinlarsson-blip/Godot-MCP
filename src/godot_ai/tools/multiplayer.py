"""MCP tool for Godot High-Level Multiplayer networking scaffolding."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import multiplayer as mp_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
High-Level Godot Multiplayer Networking Scaffolding and Topology Inspection.

Ops:
  * scaffold_network_manager(save_path="res://scripts/network_manager.gd",
                             default_port=8910, max_clients=32, as_autoload=false,
                             autoload_name="NetworkManager")
        Generate an ENetMultiplayerPeer network manager script with host/join/disconnect
        methods and peer signal handling.

  * scaffold_spawner(parent_path="", spawner_name="MultiplayerSpawner", spawn_path="..",
                     spawnable_scenes=[...], auto_spawn=true)
        Attach and configure a MultiplayerSpawner node with spawnable scene paths.

  * scaffold_synchronizer(parent_path="", synchronizer_name="MultiplayerSynchronizer",
                          root_path="..", properties=[":position", ":rotation"])
        Attach and configure a MultiplayerSynchronizer node with SceneReplicationConfig.

  * get_network_status()
        Query active multiplayer peer state, server role, unique ID, and connected peers.
"""


def register_multiplayer_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="multiplayer_manage",
        description=_DESCRIPTION,
        ops={
            "scaffold_network_manager": mp_handlers.multiplayer_scaffold_network_manager,
            "scaffold_spawner": mp_handlers.multiplayer_scaffold_spawner,
            "scaffold_synchronizer": mp_handlers.multiplayer_scaffold_synchronizer,
            "get_network_status": mp_handlers.multiplayer_get_network_status,
        },
        read_resource_forms={
            "get_network_status": None,
        },
    )
