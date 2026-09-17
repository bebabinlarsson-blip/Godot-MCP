# Godot Omni — Client Compatibility & Configuration Report

**Clients Evaluated**: 12 known AI coding clients  
**Local Installed Clients Detected**: 10 clients  
**Active Configured Integrations**: 6 clients  
**Configuration Format Support**: JSON, TOML, YAML, CLI Templates  

---

## 1. Client Support Matrix

| Client | Config Format | Primary Configuration Path | Detection | Auto-Config Support |
|:---|:---:|:---|:---:|:---:|
| **Antigravity** | JSON | `~/.gemini/config/mcp_config.json` | Installed & Configured | Fully Supported |
| **Claude Code** | CLI / JSON | `~/.claude.json` / `claude mcp add` | Installed | Fully Supported |
| **Claude Desktop** | JSON | `%APPDATA%\Claude\claude_desktop_config.json` | Installed & Configured | Fully Supported |
| **OpenAI Codex** | TOML | `~/.codex/config.toml` | Installed | Fully Supported |
| **Visual Studio Code**| JSON | `%APPDATA%\Code\User\settings.json` | Installed | Fully Supported |
| **Cursor** | JSON | `~/.cursor/mcp.json` | Installed & Configured | Fully Supported |
| **Windsurf** | JSON | `~/.codeium/windsurf/mcp_config.json` | Installed & Configured | Fully Supported |
| **Cline** | JSON | `.../saoudrizwan.claude-dev/cline_mcp_settings.json`| Installed & Configured | Fully Supported |
| **Roo Code** | JSON | `.../rooveterinaryinc.roo-cline/cline_mcp_settings.json`| Path Check | Fully Supported |
| **OpenCode** | JSON | `~/.config/opencode/opencode.json` | Installed | Fully Supported |
| **Zed** | JSON | `%APPDATA%\Zed\settings.json` | Installed & Configured | Fully Supported |
| **Gemini CLI** | JSON | `~/.gemini/config.json` | Path Check | Fully Supported |

---

## 2. Configuration Commands

Any client can be inspected or configured using the unified CLI:

```bash
# Detect presence of all clients
godot-omni clients detect

# Check status of configured servers
godot-omni clients status

# Configure a specific client
godot-omni clients configure --client claude_code
godot-omni clients configure --client codex

# Configure all detected clients in one pass
godot-omni clients configure --all

# Run diagnostics and recommendations
godot-omni clients doctor
```

---

## 3. Atomic Mutation Safeguards

- **Atomic Writes**: Writes to a hidden temporary sibling file (`.config.json.tmp.<pid>`), flushes buffers, and executes an atomic replace (`os.replace`) with exponential retry backoff on Windows file locks.
- **Key-Path Preservation**: Only injects or modifies the `godot-omni` (or `godot-ai`) server key; never overwrites or reorders other MCP servers.
- **User Field Preservation**: Custom fields (such as `disabled`, `disabledTools`, `env`, `startup_timeout_sec`) are preserved across re-configuration.
