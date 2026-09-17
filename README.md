<p align="center">
  <img src="docs/hero.png" alt="Godot MCP Banner" width="800">
</p>

# Godot MCP

The Model Context Protocol (MCP) server and official plugin for Godot Engine automation.

Built by bebabin. Supports Godot 4.1 through 4.8+ Dev.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Godot Engine](https://img.shields.io/badge/Godot-4.1%20to%204.8+%20(dev)-478CBF?logo=godotengine&logoColor=white)](https://godotengine.org)
[![MCP Protocol](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-8A2BE2)](https://modelcontextprotocol.io)
[![Author](https://img.shields.io/badge/Author-bebabin-green.svg)](https://github.com/bebabinlarsson-blip)

---

## Overview

Godot MCP connects AI assistants directly to the Godot Editor through the Model Context Protocol. It allows an AI agent to operate the engine programmatically, performing tasks that previously required manual editor interaction.

The system provides 1,820 canonical engine operations across 59 domains, along with direct GDScript evaluation and semantic editor UI automation. Supported AI clients include Google Antigravity, Claude Code, Cursor, Windsurf, VS Code, and OpenAI Codex.

### What the AI Can Automate in Godot

* Complete Scene Authoring: Create, open, save, and compose 2D and 3D scenes.
* Prefab Instantiation: Instantiate any .tscn scene into the current active scene hierarchy.
* TileMap Editing: Paint tiles, rotate cells by 90, 180, or 270 degrees, flip tiles horizontally and vertically, and query cell metadata.
* Spatial Transformations: Translate, rotate, and scale nodes in 2D and 3D with full Undo/Redo integration.
* Procedural Animations: Insert property and method tracks, add keyframes, and generate motion presets such as spin, bounce, pulse, fade, and slide.
* Shaders and Materials: Create GDShader files, configure ShaderMaterial uniform parameters, and assign materials to CanvasItem or MeshInstance3D nodes.
* 3D Primitives and Colliders: Generate BoxMesh, SphereMesh, CylinderMesh, PlaneMesh, CapsuleMesh, and PrismMesh objects, along with matching 2D and 3D collision shapes.
* Live GDScript Execution: Run arbitrary in-memory GDScript code using godot_eval with full access to EditorInterface, ProjectSettings, singletons, and ClassDB.
* Universal Reflection: Read, write, inspect, and call methods on any Godot object, resource, or node handle.
* Editor UI Automation: Traverse editor control trees, click buttons, select tabs, type into inputs, and trigger command palette actions.
* In-Editor Inspector Dock: Monitor live AI tool invocations, verify connection health, and test expressions directly inside Godot.

---

## Requirements

* Godot Engine: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, or 4.8+ (including dev builds)
* Python: 3.11, 3.12, 3.13, or 3.14
* Package Manager: Astral uv (recommended) or pip

---

## Installation and Setup

### Step 1: Install the Godot Plugin

#### Option A: From Release Archive (Recommended)
1. Download godot-mcp-v5.0.2.zip from the [Releases](https://github.com/bebabinlarsson-blip/Godot-MCP/releases) page.
2. Extract the archive directly into your Godot project root so that ddons/godot_omni and ddons/godot_ai sit in es://addons/.

#### Option B: Clone or Copy Manually
Copy the ddons/godot_omni and ddons/godot_ai directories from this repository into your project:

`	ext
your-godot-project/
└── addons/
    ├── godot_omni/
    │   ├── plugin.cfg
    │   ├── plugin.gd
    │   ├── omni_dock.gd
    │   ├── mcp_event_bus.gd
    │   ├── omni_reflection.gd
    │   └── omni_ui_tree.gd
    └── godot_ai/
        ├── plugin.cfg
        ├── plugin.gd
        ├── dispatcher.gd
        ├── connection.gd
        └── handlers/
`

### Step 2: Enable the Plugins in Godot
1. Open your project in Godot.
2. Go to **Project -> Project Settings -> Plugins**.
3. Enable **Godot MCP Omni** and **Godot MCP Core**.

The plugin starts the local loopback WebSocket server and attaches the **Godot MCP** tab directly beside your Inspector.

---

### Step 3: Install the Python MCP Server

`ash
# Clone the repository
git clone https://github.com/bebabinlarsson-blip/Godot-MCP.git
cd "Godot-MCP"

# Install with dependencies using uv
uv sync

# Or install with pip
pip install -e .
`

Verify your installation from the terminal:
`ash
godot-omni self-test
godot-omni tools stats
`

---

### Step 4: Configure Your AI Client

You can auto-configure supported clients using the CLI:

`ash
# Configure all detected clients
godot-omni clients configure all

# Or configure a specific client:
godot-omni clients configure antigravity
godot-omni clients configure claude-code
godot-omni clients configure claude-desktop
godot-omni clients configure cursor
godot-omni clients configure windsurf
godot-omni clients configure vscode
`

#### Manual Configuration (JSON)
For manual setup, add the entry below to your client's MCP configuration file:

`json
{
  "mcpServers": {
    "godot-mcp": {
      "command": "godot-omni",
      "args": ["attach"]
    }
  }
}
`

---

## AI Agent Decision Framework

When an AI assistant automates tasks in Godot, it should follow this 6-step execution workflow:

### 1. State Inspection
Always inspect the current project state before mutating scenes:
`json
call("godot-ai", "editor_state", {})
call("godot-ai", "scene_get_hierarchy", {"max_depth": 5})
`

### 2. Scene and Prefab Composition
Create nodes, instantiate sub-scenes (.tscn), or generate 3D primitives:
`json
// Instantiate a prefab:
call("godot-ai", "omni_manage", {
  "op": "instantiate_prefab",
  "scene_path": "res://scenes/coin.tscn",
  "parent_path": "Items",
  "node_name": "Coin_01",
  "position": [100.0, 200.0]
})

// Generate a 3D Box primitive:
call("godot-ai", "omni_manage", {
  "op": "mesh_primitive",
  "primitive_type": "box",
  "node_name": "Crate",
  "size": [1.0, 1.0, 1.0],
  "albedo_color": [0.6, 0.4, 0.2, 1.0],
  "position": [0.0, 0.5, 0.0]
})
`

### 3. Environment Construction (TileMaps)
Paint and manipulate tiles in TileMapLayer or TileMap nodes:
`json
// Place a rotated tile:
call("godot-ai", "tilemap_manage", {
  "op": "tilemap_place_tile",
  "path": "TileMapLayer",
  "source_id": 0,
  "atlas_col": 3,
  "atlas_row": 1,
  "map_x": 12,
  "map_y": 8,
  "rotation_degrees": 90,
  "flip_h": false
})
`

### 4. Node Transforms
Apply translation, rotation, and scaling with native Undo/Redo:
`json
call("godot-ai", "node_manage", {
  "op": "rotate",
  "path": "Player",
  "degrees": 90.0,
  "relative": true
})
`

### 5. Animation Authoring
Generate keyframes and motion clips using presets or custom tracks:
`json
call("godot-ai", "animation_manage", {
  "op": "preset_spin",
  "player_path": "AnimationPlayer",
  "target_path": "Icon",
  "duration": 1.2,
  "loop": true
})
`

### 6. Live GDScript Omnipotence (godot_eval)
When a bespoke operation is needed that has no pre-packaged tool, execute ephemeral GDScript:
`json
call("godot-ai", "omni_eval", {
  "code": "return EditorInterface.get_editor_settings().get_setting('interface/editor/main_font_size')"
})
`

---

## The Godot MCP Inspector Dock

Godot MCP adds an official editor dock placed directly in the upper-right dock area beside the **Inspector** tab (Inspector | Node | History | Godot MCP).

### Dock Features
1. Connection Status and Diagnostics:
   * Displays active bridge state (ACTIVE / CONNECTING / OFFLINE).
   * Shows HTTP port (9500) and WebSocket port (9501).
   * Displays running Godot version, domain count, and operation count.
   * Includes a Test Connection button that executes an immediate roundtrip ping and prints measured latency in milliseconds.
2. Live Tool Call Activity Monitor:
   * Real-time stream of all tool calls dispatched by the AI.
   * Displays timestamp, tool name, success or error status badges, and execution duration.
   * Includes formatted arguments and return value previews.
   * Filter controls allow viewing All calls, Succeeded calls, or Errors only.
   * Auto-scroll toggle and Clear History button.
3. Interactive GDScript Sandbox:
   * LineEdit console allowing developers and agents to run live GDScript in the editor context and inspect return values immediately.

---

## Customization and Advanced Configuration

### 1. Registering Custom Add-on Tools
You can expose custom GDScript tools to the AI by placing scripts in es://addons/godot_ai/custom_tools/:

`gdscript
# res://addons/godot_ai/custom_tools/spawn_enemy_tool.gd
@tool
extends RefCounted

func get_tool_name() -> String:
    return "spawn_custom_enemy"

func get_tool_description() -> String:
    return "Spawns a specialized enemy with custom health and behavior parameters."

func execute(params: Dictionary) -> Dictionary:
    var enemy_type = params.get("type", "goblin")
    var health = int(params.get("health", 100))
    # Custom game logic executed inside the editor
    return {"status": "ok", "spawned": enemy_type, "hp": health}
`

The plugin automatically registers these custom tools into the MCP tool catalog without requiring Python server modifications.

### 2. Adaptive Tool Exposure Modes
Set the exposure strategy via the CLI to match client context capacities:

`ash
# Auto-detect client capabilities (default)
godot-omni server --exposure AUTO

# Force domain-grouped rollups (fits under 100-tool client caps)
godot-omni server --exposure DOMAIN

# Expose full unconstrained catalog (1,820 granular tools)
godot-omni server --exposure FULL

# Minimal router mode (4 tools: execute, search, describe, stats)
godot-omni server --exposure ROUTER
`

### 3. Network and Port Configuration
Customize ports in Godot under **Project Settings -> Editor Settings -> Plugins -> Godot AI**:

* godot_ai/http_port: Default 9500 (range: 1024 - 65535)
* godot_ai/ws_port: Default 9501 (range: 1024 - 65535)
* godot_ai/mcp_logging: Enable or disable console echoing of MCP tool calls.

To allow remote host access across a local network subnet, launch the server with:
`ash
godot-omni server --allow-host 192.168.1.0/24
`

---

## Architecture

`	ext
┌─────────────────────────────────────────────────────────────┐
│                       AI Assistant                          │
│     (Antigravity, Claude Code, Cursor, Windsurf, ...)       │
└──────────────────────────────┬──────────────────────────────┘
                               │  stdio (FastMCP Protocol)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Godot MCP Python Server                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │   Adaptive Exposure Engine (AUTO, FULL, DOMAIN, LAZY) │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │   Canonical Registry: 1,820 Operations / 59 Domains   │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │   Universal Reflection Handle Manager (obj://...)     │  │
│  └───────────────────────────┬───────────────────────────┘  │
└──────────────────────────────┼──────────────────────────────┘
                               │  Loopback WebSocket (Port 9500/9501)
                               │  (Token-authenticated)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               Godot Editor Plugin (addons/)                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │   OmniDock (Inspector Tab: Status, Live Monitor, Eval)│  │
│  ├───────────────────────────────────────────────────────┤  │
│  │   McpEventBus (Real-Time In-Editor Dispatch Broker)   │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │   omni_handler.gd (Engine Operation Dispatcher)       │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │   godot_eval (In-Memory Ephemeral GDScript Runner)    │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │   omni_reflection.gd (Variant Serialization)          │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │   omni_ui_tree.gd (Semantic Editor UI Automation)     │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │   Godot Engine APIs: ClassDB, EditorInterface, Nodes  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
`

---

## Command-Line Interface Reference

The godot-omni CLI provides tools for management, diagnostics, and testing:

`ash
# Tools and Registry
godot-omni tools stats                       # Summary of 1,820 operations across 59 domains
godot-omni tools search "tilemap"            # Search operations across domains
godot-omni tools describe tilemap_place_tile # View parameters, schemas, and return formats
godot-omni tools list --domain animation     # List all operations in a specific domain
godot-omni tools export schema.json          # Export complete JSON catalog

# Client Setup and Diagnostics
godot-omni clients detect                    # Detect installed AI clients
godot-omni clients status                    # Check registration status across 12 clients
godot-omni clients configure <client_name>   # Configure a specific client
godot-omni clients configure all             # Auto-configure all detected clients
godot-omni clients doctor                    # Validate client configs and check paths

# Performance and Diagnostics
godot-omni benchmark all                     # Run end-to-end latency benchmarks
godot-omni doctor                            # Environment check: Python, Godot, ports
godot-omni self-test                         # In-process test suite
godot-omni versions status                   # Compatibility status across Godot 4.1 to 4.8+
`

---

## Security

* Local Loopback Binding: Sockets bind strictly to 127.0.0.1. No external ports or listening interfaces are exposed.
* Authenticated Communication: WebSockets use session tokens generated per editor launch with restricted user permissions.
* Ephemeral Code Execution: Dynamic code runs strictly in memory via @tool scripts and leaves no residual files on disk.
* Telemetry Opt-Out: Telemetry can be disabled at any time by setting GODOT_AI_DISABLE_TELEMETRY=true. No code, scene structure, or file paths are ever transmitted.

See [SECURITY.md](SECURITY.md) for vulnerability reporting procedures.

---

## Author and Maintainer

Created and maintained by **[bebabin](https://github.com/bebabinlarsson-blip)**.

---

## Contributing

Contributions, issues, and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and testing guidelines.

---

## License

This project is open-source software licensed under the [MIT License](LICENSE).
