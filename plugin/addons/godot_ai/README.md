# Godot MCP Core

Connect AI assistants to a live Godot editor via the
[Model Context Protocol](https://modelcontextprotocol.io/introduction) (MCP).

Godot MCP Core is the editor-side component of
[Godot MCP](https://github.com/bebabinlarsson-blip/Godot-MCP). It bridges
Google Antigravity, Claude Code, Cursor, Windsurf, VS Code, OpenAI Codex, and
other MCP clients with your editor — inspect scenes, create nodes, modify
properties, run tests, evaluate GDScript, and more, all from a prompt.

Install **Godot MCP Omni** (`addons/godot_omni`) alongside this addon for the
full 1,820-operation engine surface.

## Quick Start

1. Copy this `addons/godot_ai/` folder (and `addons/godot_omni/`) into your
   project so they sit under `res://addons/`.
2. Enable the plugins: **Project > Project Settings > Plugins > Godot MCP Core**
   and **Godot MCP Omni**.
3. Install the Python server: `pip install -e .` or `uv sync`, then configure
   your MCP client with `godot-omni clients configure <client>`.

The plugin auto-starts the MCP server and connects over WebSocket. No manual
configuration required.

## Requirements

- **Godot:** 4.7 or newer
- **Python:** 3.11, 3.12, 3.13, or 3.14 with `godot-omni` installed

## Documentation

Full documentation and source: [github.com/bebabinlarsson-blip/Godot-MCP](https://github.com/bebabinlarsson-blip/Godot-MCP)

## License

[MIT](LICENSE)

## Credits and AI use

Project credits: Ghosty and Bebabin. AI assistance was used for code and
documentation contributions in this release.
