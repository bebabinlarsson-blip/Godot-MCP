<div align="center">

# Godot MCP

### Production-Grade Model Context Protocol Server and Automation Plugin for the Godot Engine

[![MCP Protocol](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-8A2BE2?style=flat&labelColor=333A41)](https://modelcontextprotocol.io)
[![Release](https://img.shields.io/badge/Release-v5.0.4-blue.svg?style=flat&labelColor=333A41)](https://github.com/bebabinlarsson-blip/Godot-MCP/releases)
[![Godot](https://img.shields.io/badge/Godot-4.1%20to%204.8+-478CBF?style=flat&logo=godotengine&logoColor=white&labelColor=333A41)](https://godotengine.org)
[![Python](https://img.shields.io/badge/Python-3.11%20|%203.12%20|%203.13%20|%203.14-3776AB?style=flat&logo=python&logoColor=white&labelColor=333A41)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat&labelColor=333A41)](LICENSE)
[![Author](https://img.shields.io/badge/Author-bebabin-2ea44f.svg?style=flat&labelColor=333A41)](https://github.com/bebabinlarsson-blip)

<br>

<img src="docs/hero.png" alt="Godot MCP Banner" width="100%">

<br>

**Compatible AI Clients**

[Claude Code](https://claude.ai) | [Cursor](https://www.cursor.com) | [Antigravity](https://antigravity.google) | [VS Code / Cline](https://code.visualstudio.com) | [Windsurf](https://codeium.com/windsurf) | [GitHub Copilot](https://github.com/features/copilot) | [OpenAI Codex](https://openai.com)

</div>

---

## Overview

Godot MCP connects AI assistants directly to the Godot Editor through the Model Context Protocol (MCP). It equips any modern language model or autonomous agent with complete programmatic control over the Godot Engine, bridging natural language prompts with real-time in-editor creation, modification, inspection, and verification.

Unlike wrappers requiring external cloud compilation or specialized .NET setups, Godot MCP operates via pure GDScript in-engine execution coupled with a high-performance local MCP server. It runs natively across all Godot 4.x installations on Windows, macOS, and Linux without requiring C# Mono builds or external cloud proxies.

### Key Architectural Strengths

* Universal Compatibility: Runs seamlessly on both Standard (GDScript) and .NET (Mono) builds of Godot 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, and 4.8+ Dev.
* Complete Feature Parity: 59 domain families encompassing 1,820 canonical engine operations, from granular scene and node transformations to procedural animation and tile manipulation.
* Live GDScript Execution: Direct arbitrary script evaluation inside the editor process with full access to EditorInterface, ProjectSettings, singletons, and ClassDB.
* Universal Reflection: Inspect, read, write, and invoke methods on any Godot Object, Resource, Node, or Singleton with typed argument conversion and handle safety.
* Single Unified Dock: Clean, native editor panel positioned beside the Inspector dock with live tool activity tracking, connection status, memory indicators, and port conflict resolution.
* Zero Cloud Dependency: All MCP traffic routes over secure local loopback WebSocket and standard I/O pipes. Your project code and game assets never leave your computer.

---

## Tool Families and Capabilities Matrix

Godot MCP exposes 59 domain families covering the entire surface of the Godot Engine:

| Family | Key Operations | Description |
| :--- | :--- | :--- |
| **ping** | `ping`, `mcp_ping` | Diagnostic readiness probe echoing engine status, version, process frames, and memory metrics. |
| **node** | `node_create`, `node_set_property`, `node_get_properties`, `node_find`, `node_manage` | Find, spawn, modify, reparent, reorder, duplicate, delete, rotate, scale, and translate nodes in 2D and 3D with undo/redo. |
| **scene** | `scene_open`, `scene_save`, `scene_get_hierarchy`, `scene_manage` | Open, save, create, close, inspect root hierarchies, and instantiate PackedScene prefabs. |
| **script** | `script_create`, `script_patch`, `script_attach`, `script_manage` | Create, anchor-patch, read, detach, inspect symbols, validate syntax/compilation, and delete GDScript files. |
| **filesystem** | `filesystem_manage` | List files and directories with UIDs, read/write text, delete, move, force reimport assets, and trigger editor scans. |
| **resource** | `resource_manage` | Search, load, assign, introspect, create, delete, and move .tres/.res assets, curve profiles, and environment setups. |
| **screenshot** | `editor_screenshot`, `camera_manage` | High-fidelity captures of the 3D viewport, 2D viewport, active cameras, running game frames, and isolated node framing. |
| **editor** | `editor_state`, `editor_manage`, `editor_reload_plugin` | Read editor lifecycle, inspect/set node selections, query performance monitors, clear logs, and execute safe restarts. |
| **console** | `logs_read`, `editor_manage(logs_clear)` | Real-time structured log streaming from plugin events, editor output, debugger errors, and game runtime stdout/stderr. |
| **reflection** | `omni_eval`, `omni_manage(call, get, set, inspect)` | Universal object reflection, dynamic method invocation, property getters/setters, and ClassDB discovery. |
| **tilemap** | `tilemap_manage` | Paint cells, rotate tiles (90, 180, 270 degrees), flip horizontally/vertically, erase, query coordinates, and inspect layers. |
| **tileset** | `tileset_manage` | Inspect atlas source tiles, extract texture slices, and introspect physics and navigation layers. |
| **animation** | `animation_create`, `animation_manage` | Create AnimationPlayers, add property/method tracks, insert keyframes, set autoplay, and apply procedural motion presets. |
| **physics** | `collision_shape_create`, `physics_shape_autofit` | Generate 2D and 3D collision bodies, autofit shapes to visual mesh bounds, and configure collision layers. |
| **mesh** | `mesh_create_primitive` | Procedural generation of BoxMesh, SphereMesh, CylinderMesh, PlaneMesh, CapsuleMesh, and PrismMesh objects with materials. |
| **shader** | `shader_create`, `material_manage` | Author GDShader files, create ShaderMaterials, set uniforms, and assign materials to CanvasItem or MeshInstance3D nodes. |
| **game** | `game_manage`, `project_run` | Launch, stop, restart, and command the running game instance with game helper diagnostics. |
| **input** | `input_map_manage` | Configure InputMap actions, bind keyboard and gamepad events, and query registered input actions. |
| **ui** | `ui_manage`, `ui_semantic_tree`, `ui_click`, `ui_type` | Inspect the semantic control hierarchy of the editor UI, click buttons/tabs, and simulate input keystrokes. |

---

## Quick Start

### Step 1: Install the Godot Plugin

#### Option A: From Release Archive (Recommended)

1. Download `godot-mcp-v5.0.4.zip` from the [GitHub Releases](https://github.com/bebabinlarsson-blip/Godot-MCP/releases) page.
2. Extract the archive into your Godot project root folder.
3. Verify that your directory structure looks like this:

```text
your-godot-project/
└── addons/
    ├── godot_ai/
    │   ├── plugin.cfg
    │   ├── plugin.gd
    │   ├── godot_mcp_dock.gd
    │   ├── connection.gd
    │   ├── dispatcher.gd
    │   └── handlers/
    └── godot_omni/
        ├── plugin.cfg
        ├── plugin.gd
        ├── omni_dock.gd
        ├── omni_reflection.gd
        └── omni_ui_tree.gd
```

#### Option B: Automated via Terminal

```bash
# Clone the repository
git clone https://github.com/bebabinlarsson-blip/Godot-MCP.git

# Copy addons to your project
Copy-Item -Path "Godot-MCP/addons/*" -Destination "YourProject/addons/" -Recurse -Force
```

### Step 2: Enable the Plugin in Godot

1. Open your project in the Godot Editor.
2. Navigate to **Project -> Project Settings -> Plugins**.
3. Enable **Godot MCP Core** and **Godot MCP Omni**.
4. The single **Godot MCP** inspector tab will immediately appear on the right side beside the Inspector dock.

---

## AI Client Configuration

Godot MCP can be run via `uvx` directly from GitHub, through a local Python installation, or via the `godot-omni` CLI.

### Cursor

Add this entry to `.cursor/mcp.json` in your project or global Cursor settings:

```json
{
  "mcpServers": {
    "godot-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/bebabinlarsson-blip/Godot-MCP.git",
        "godot-ai"
      ]
    }
  }
}
```

### Claude Desktop

Add this configuration to `claude_desktop_config.json`:

* Windows: `%APPDATA%\Claude\claude_desktop_config.json`
* macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "godot-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/bebabinlarsson-blip/Godot-MCP.git",
        "godot-ai"
      ]
    }
  }
}
```

### Google Antigravity

In Antigravity or Gemini CLI, add the server to your configuration:

```json
{
  "mcpServers": {
    "godot-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/bebabinlarsson-blip/Godot-MCP.git",
        "godot-ai"
      ]
    }
  }
}
```

### VS Code (Cline / Roo Code)

Add this configuration to your Cline MCP settings:

```json
{
  "mcpServers": {
    "godot-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/bebabinlarsson-blip/Godot-MCP.git",
        "godot-ai"
      ]
    }
  }
}
```

### Windsurf

Add this configuration to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "godot-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/bebabinlarsson-blip/Godot-MCP.git",
        "godot-ai"
      ]
    }
  }
}
```

---

## In-Editor Inspector Dock

The Godot MCP dock integrates directly into the Godot Editor on the right dock bar beside the Inspector:

* Live Status Indicator: Real-time visual feedback showing server connection state and engine bridge health.
* Operation Activity Stream: Displays incoming tool calls with execution status, operation name, and response duration in milliseconds.
* Diagnostic Controls: Run immediate self-tests, verify readiness probes (`ping`), and measure active session latency directly inside the editor.
* Memory & Performance Telemetry: Displays static memory allocation, process frame counts, and active scene root details.
* Free Port & Replace Server: One-click resolution for occupied HTTP/WebSocket ports, freeing port 8000 safely if an orphaned background process was left running.

---

## System Architecture

```mermaid
flowchart TD
    subgraph AI_Clients [AI Clients & Agents]
        Claude[Claude Code / Desktop]
        Cursor[Cursor IDE]
        Antigravity[Google Antigravity]
        VSCode[VS Code / Cline / Roo]
        Windsurf[Windsurf IDE]
    end

    subgraph MCP_Server [Godot MCP Server (FastMCP / Python)]
        Stdio[Standard I/O Pipe]
        HttpSSE[Streamable HTTP / SSE]
        Router[Adaptive Domain Router]
        DirectRuntime[Direct Runtime Bridge]
    end

    subgraph Godot_Engine [Godot Engine Editor]
        WSBridge[McpConnection WebSocket Server]
        Dispatcher[McpDispatcher]
        OmniHandler[Omni & Reflection Handler]
        DomainHandlers[59 Domain Handlers]
        EditorDock[Godot MCP Inspector Dock]
    end

    AI_Clients -->|MCP JSON-RPC| Stdio
    AI_Clients -->|MCP HTTP/SSE| HttpSSE
    Stdio --> Router
    HttpSSE --> Router
    Router --> DirectRuntime
    DirectRuntime <-->|Loopback WebSocket :8000| WSBridge
    WSBridge <--> Dispatcher
    Dispatcher --> OmniHandler
    Dispatcher --> DomainHandlers
    Dispatcher --> EditorDock
```

---

## Verification and Diagnostics

You can verify your installation and test end-to-end communication from the terminal:

```bash
# Run the complete automated test suite
uv run godot-omni self-test

# Display tool registry metrics across all domains
uv run godot-omni tools stats

# Check client configuration health
uv run godot-omni doctor
```

### Sample Python Interactive Verification

```python
import asyncio
from godot_ai.runtime.direct import DirectRuntime

async def main():
    runtime = DirectRuntime()
    # Ping the active Godot editor
    result = await runtime.send_command("ping", {})
    print("Ping response:", result)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Troubleshooting

### Port 8000 Already in Use
If another process is using port 8000:
1. In the Godot Editor, open the **Godot MCP** dock tab beside the Inspector.
2. Click **Free Port & Replace Server**.
3. Or from PowerShell:
   ```powershell
   Get-NetTCPConnection -LocalPort 8000 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
   ```

### Headless Execution
To run Godot headlessly in CI or terminal automation, set the environment variable:
```bash
# Linux/macOS
export GODOT_AI_ALLOW_HEADLESS=1

# Windows PowerShell
$env:GODOT_AI_ALLOW_HEADLESS="1"
```

---

## Author and License

* Author: [bebabin](https://github.com/bebabinlarsson-blip) (`bebabinlarsson@gmail.com`)
* License: [MIT License](LICENSE)