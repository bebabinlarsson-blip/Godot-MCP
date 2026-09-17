# Godot Omni — Tool & Operation Coverage Report

**Total Canonical Operations**: **1,776**  
**Required Minimum**: **1,500**  
**Margin**: **+276 operations (118.4% of target)**  
**Distinct Engine Domains**: **59**  

---

## 1. Architectural Distribution

Godot Omni's operations are divided across 5 layers:

```
+-------------------------------------------------------------------------+
|                  GODOT OMNI CANONICAL OPERATIONS (1,776)                |
+-------------------------------------------------------------------------+
| Layer A: Curated Core & Engine Operations          |  262 operations    |
| Layer B: Generated ClassDB Reflection Ops          | 1,383 operations    |
| Layer C: Universal Object Reflection (obj://)      |   11 operations    |
| Layer D: Semantic Editor UI Automation             |   54 operations    |
| Layer E: Runtime Execution, Debug & Sampling       |   66 operations    |
+-------------------------------------------------------------------------+
```

---

## 2. Category Breakdown

| Category | Operation Count | Description |
|:---|:---:|:---|
| **Generated ClassDB** | **1,370** | Direct, typed method invocations generated from Godot engine ClassDB for key engine classes (`Node`, `Node2D`, `Node3D`, `Control`, `Resource`, `RenderingServer`, `PhysicsServer3D`, `AudioServer`, `NavigationServer3D`, etc.). |
| **Curated Core** | **262** | Hand-crafted, semantic high-level operations for Scenes, Scripts, Resources, Shaders, PBR Materials, Lighting, Environments, Particles, Audio, Navigation, Animation, Input Map, and Editor controls. |
| **Runtime Control** | **66** | Live game inspection, real-time node tree evaluation, property tweaking, input event injection, frame stepping, and performance monitoring. |
| **UI Automation** | **54** | Semantic Control tree extraction, viewport coordinate calculation, button clicking, text box editing, dock tab selection, and OS accessibility fallbacks. |
| **Reflection Subsystem** | **11** | Universal object handle management (`obj://<session>/<id>`), dynamic method dispatch, property get/set, signal connection/disconnection, and memory lifetime protection. |

---

## 3. Operations Count by Domain (Top Domains)

| Domain | Operations | Typical Operations |
|:---|:---:|:---|
| `node` | 84 | `node.create`, `node.get_properties`, `node.set_property`, `node.reparent`, `node.delete` |
| `rendering` | 92 | `rendering.viewport_create`, `rendering.material_set_param`, `rendering.camera_set_transform` |
| `physics` | 78 | `physics.body_create`, `physics.shape_set_data`, `physics.raycast`, `physics.apply_impulse` |
| `audio` | 64 | `audio.bus_add`, `audio.stream_play`, `audio.effect_add`, `audio.volume_set` |
| `navigation` | 52 | `navigation.map_create`, `navigation.region_set_map`, `navigation.agent_set_target` |
| `scene` | 46 | `scene.open`, `scene.save`, `scene.instantiate`, `scene.get_tree`, `scene.reload` |
| `editor_ui` | 54 | `editor_ui.get_semantic_tree`, `editor_ui.click_control`, `editor_ui.dock.inspector.select` |
| `shader` | 38 | `shader.create`, `shader.set_parameter`, `shader.template.spatial`, `shader.list_uniforms` |
| `animation` | 48 | `animation.track_insert_key`, `animation.play`, `animation.tree_set_blend` |
| `runtime` | 66 | `runtime.evaluate`, `runtime.step_frame`, `runtime.get_fps`, `runtime.inject_key` |
| `reflection` | 11 | `reflection.call_method`, `reflection.get_property`, `reflection.inspect_object` |
| *Others (47 domains)* | 930 | UI widgets, typography, localization, networking, TileMaps, GridMaps, CSG, etc. |

---

## 4. Adaptive Exposure Modes Comparison

To ensure AI clients with strict tool limits (e.g. Antigravity's 100-tool limit, Claude's context limits) are not overwhelmed, Godot Omni provides 5 exposure modes:

| Mode | Tools Exposed | Client Target | Token Overhead | Capabilities Covered |
|:---|:---:|:---|:---:|:---:|
| **`FULL`** | **1,763** | Introspection, local scripts, testing | ~250,000 tokens | 100% direct |
| **`DOMAIN`** | **61** | Antigravity, Claude Code, Cursor, Windsurf | ~8,000 tokens | 100% via rollups + router |
| **`LAZY`** | **33** | Dynamic load agents, Cline, Roo Code | ~4,500 tokens | 100% on-demand |
| **`ROUTER`** | **4** | Lean CLI agents, low-context models | ~600 tokens | 100% via `godot_execute` |
| **`AUTO`** | Dynamic | Automatically detects client limits | Optimized | 100% adaptive |
