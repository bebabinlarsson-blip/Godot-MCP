# Security Policy

## Supported Versions

Security fixes are actively provided for the following releases:

| Version | Supported          |
| ------- | ------------------ |
| 5.0.x   | :white_check_mark: |
| 4.1.x   | :white_check_mark: |
| < 4.1.0 | :x:                |

---

## Architecture & Security Model

Godot MCP operates on a defense-in-depth, local-isolation security model:

1. **Loopback Only**: The WebSocket bridge between the Python MCP server and the Godot editor runs strictly over `127.0.0.1`. It never listens on external network interfaces.
2. **Rotating Cryptographic Capabilities**: Access between clients, server, and editor uses rotating capability tokens stored with restrictive filesystem permissions (e.g. `0700` user-only access). Unauthenticated connections are strictly rejected.
3. **Handle Protection**: Reflection handles (`obj://session/id`) use generational counters to prevent use-after-free and object manipulation across stale sessions.
4. **Isolated GDScript Execution**: GDScript evaluation (`godot_eval`) is ephemeral, executed within the editor process without persisting arbitrary bytecode to disk.

---

## Reporting a Vulnerability

If you discover a security vulnerability within Godot MCP, please **do not open a public issue**.

Instead, please report security issues responsibly via:
- GitHub Security Advisory: Create a private report under the **Security** tab of this repository.
- Or email the security team directly at: `security@hi-godot.org` (or project maintainers).

Please include:
- A description of the issue and potential impact
- Reproduction steps or proof-of-concept
- Any relevant logs or environment details

We will acknowledge receipt within 48 hours and work with you on a coordinated disclosure timeline.
