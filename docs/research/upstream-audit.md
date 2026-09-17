# Upstream Architecture Audit: hi-godot/godot-ai (v4.1.0)

**Date**: 2026-09-17  
**Author**: Godot Omni Engineering Team  
**Upstream Commit**: `2485994` (v4.1.0)

---

## 1. Executive Summary

`hi-godot/godot-ai` is a well-engineered MCP integration for Godot 4.x. It features a persistent Python FastMCP server communicating over authenticated loopback HTTP/SSE/stdio with AI clients, and an authenticated WebSocket (:9500) connection to an EditorPlugin running inside Godot.

However, upstream was designed around a compact rollup strategy (46 total MCP tools) to fit under strict tool caps, leaving hundreds of Godot classes, thousands of methods, and deep editor/runtime capabilities unexposed or requiring cumbersome manual invocation.

Our objective with **Godot Omni** is to transform this foundation into a universal AI control plane:
- Expanding from ~150 logical operations to **1,500+ canonical operations** (curated + generated ClassDB + dynamic reflection).
- Implementing **Adaptive Tool Exposure** (`AUTO`, `FULL`, `LAZY`, `DOMAIN`, `ROUTER`) so every client (from 50-tool-capped clients like Antigravity to unlimited-tool clients) has access to 100% of capabilities without context bloat.
- Providing **Universal Object Reflection** with session-scoped object handles (`obj://session/id`).
- Adding **Editor UI Semantic Tree & Input Automation** and **OS Accessibility Fallback** (Windows UI Automation, macOS Accessibility, Linux AT-SPI).
- Implementing a unified CLI (`godot-omni`) with tools stats, discovery, benchmarking, doctor, and client management.

---

## 2. What Works Well (Components Worth Preserving)

1. **Security & Transport Architecture**:
   - Loopback-only binding with capability token authentication (`.godot-ai-capabilities.json`).
   - Distinct secrets for HTTP and WebSocket channels, rotating per launch.
   - Private capability files avoiding leak in public configs or git.

2. **Session & Multi-Editor Management**:
   - Session registry tracking multiple running Godot instances with `<project-slug>@<16hex>` IDs.
   - Explicit session pinning via `session_activate` and optional `session_id` routing on every tool call.

3. **Logging & Real-Time Diagnostics**:
   - Ring buffers for editor logs, game logs, and debugger errors.
   - Incremental cursor-based reads (`since_cursor`, `since_run_id`).
   - "Doorbell" notifications (`new_errors_since_last_call`) alerting agents to freshly occurred errors without separate polling.

4. **Client Configuration System**:
   - Declarative, data-only descriptors for 23+ AI clients in `plugin/addons/godot_ai/clients/`.
   - Atomic config writes (`_atomic_write.gd`) with backup, fsync, and rollback.
   - Account-wide global mutation lock (`McpClientMutationLock`) preventing concurrent writer corruption.

5. **Batch Execution & Undo/Redo**:
   - `batch_execute` supporting multi-command transactions with automatic rollback on error.
   - Deep integration with Godot's `UndoRedo` system for scene and resource edits.

6. **Game Runtime Helper**:
   - `_mcp_game_helper` autoload detecting game liveness, crash/break state in remote debugger, and capturing runtime framebuffers.

---

## 3. What Is Missing / Limitations

1. **Operation Surface & Completeness**:
   - Currently only 46 MCP tools and ~150 logical operations across 27 domain rollups.
   - No direct access to 85%+ of Godot engine classes (Shaders, Navigation, Multiplayer, XR, Physics 2D/3D, CSG, Curves, Gradients, Meshes, Skeletons, Lighting, Environment, Viewports).
   - No dynamic reflection bridge allowing agents to query ClassDB, inspect arbitrary classes/methods/properties/signals, construct arbitrary Objects/Resources, or call methods.

2. **Adaptive Tool Exposure**:
   - Currently, the server only supports `--exclude-domains`, which permanently drops entire domains.
   - No client-adaptive schema negotiation (`FULL` for unrestricted clients, `DOMAIN` rollups, `ROUTER` with discovery tools, `LAZY` on-demand loading).
   - Constrained clients either exceed their tool limits or lose access to essential domains.

3. **Tool Discovery & Semantic Search**:
   - No in-band tool search (`tools.search`, `tools.describe`, `tools.list_domains`, `tools.examples`).
   - AI agents cannot discover which operation achieves a natural language goal (e.g., "make glowing 3d material").

4. **Editor UI Semantic Tree & Physical Automation**:
   - Currently, the AI cannot inspect editor dock controls, buttons, dialogs, or menus.
   - No semantic click/type operations (`editor_ui.click`, `editor_ui.type`, `editor_ui.menu_click`).
   - No OS accessibility fallback (Windows UI Automation) when an editor control is not exposed via Godot's internal tree.

5. **CLI & Operational Tooling**:
   - No `godot-omni` unified CLI command for:
     - `tools stats` (asserting >= 1,500 canonical operations)
     - `benchmark` (measuring latency p50/p95 for router, read, write, batch)
     - `doctor` (health diagnostics across Python, Godot, ports, clients)
     - `versions status` (tested engine compatibility matrix)
     - `self-test` (end-to-end headless verification)

6. **Version Compatibility**:
   - Highly coupled to Godot 4.x (specifically 4.2–4.8).
   - No clean adapter structure for Godot 3.x or legacy fallback modes (CLI/filesystem/project parsing).

---

## 4. Bottlenecks & Transport Overhead

1. **Startup Overhead**:
   - If invoked cold via `uvx`, client startup waits for environment resolution. Prewarming and local install tiers (`godot-omni attach`) are critical.
2. **Serialization**:
   - Full property queries (`node_get_properties`) without field filtering return up to 150 properties per node. Field filtering and concise modes mitigate this.
   - Large tilemaps, mesh geometry, and binary files must use chunked/file-based transfer rather than huge JSON base64 payloads.
3. **Dispatch Latency**:
   - Router dispatch overhead must remain <= 5 ms p50, and simple editor reads <= 10 ms p50.

---

## 5. Implementation Strategy for Godot Omni

We will build the **Universal Godot AI MCP** on top of this solid foundation by introducing:

- **Layer A (Curated High-Level Operations)**: 400+ rich, developer-centric operations spanning all 50+ Godot domains.
- **Layer B (Generated ClassDB Operations)**: 1,100+ version-specific ClassDB operations generated from Godot engine reflection and ClassDB metadata.
- **Layer C (Universal Object Reflection & Handles)**: Stable `obj://session/handle` references, dynamic method invocation, and variant serialization for all 38+ Godot variant types.
- **Layer D (Editor UI Semantic Tree & Automation)**: Traversing editor `Control` hierarchy, semantic click, menu selection, and modal dialog automation.
- **Layer E (OS Accessibility Fallback)**: Windows UI Automation / OS accessibility bridge for editor UI elements outside Godot's public control tree.
- **Adaptive Tool Exposure Engine**: Default `AUTO` mode detecting client profile, alongside `FULL`, `LAZY`, `DOMAIN`, and `ROUTER` modes.
- **Unified CLI (`godot-omni`)**: Full CLI command suite including `tools stats`, `benchmark`, `doctor`, `clients`, `self-test`.
