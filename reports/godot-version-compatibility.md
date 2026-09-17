# Godot Omni — Godot Engine Version Compatibility Report

**Supported Godot Line**: Godot 4.1 through Godot 4.8+ (including active 4.8 dev builds)  
**Target Recommendation**: **Godot 4.7+ / Godot 4.8 (dev)**  
**Local Installed Configurations Detected**: **Godot 4.7, Godot 4.8**  

---

## 1. Version Compatibility Matrix

| Version | Status | Reflection Tier | UI Automation Support | Key Capabilities |
|:---|:---:|:---:|:---:|:---|
| **4.1.x** | Supported | Basic Object Call | Inspector & Node Path | Node/Scene/Script Ops, HTTP/WS Transport, Basic ClassDB |
| **4.2.x** | Supported | Method & Signal Discovery | Inspector & Scene Dock | GDExtension 4.2, TileMap Multi-layer, Addon Auto-load |
| **4.3.x** | Supported | Full ClassDB Reflection | Semantic Control Tree | TileMapLayer Node, Compositor Effects, UID System, AudioStreamInteractive |
| **4.4.x** | Supported | Typed Variant Reflection | Semantic Control Tree + Shortcuts | Typed Dictionaries, Jolt Physics Integration, Lightmap Bicubic |
| **4.5.x** | Supported | Universal Object Reflection (`obj://`) | Full Semantic UI Tree + Shortcuts | Modern Rendering Pipelines, Shader Global Buffers, Audio Effect Graphs |
| **4.6.x** | Supported | Universal Object Reflection (`obj://`) | Semantic UI Tree + Native Fallback | Advanced NavigationServer3D, Async Asset Pipeline, Threaded Node Loading |
| **4.7.x** | Supported (Stable) | Universal Reflection + Gen Tracking | Full Semantic UI Tree + OS Accessibility | 1,500+ Canonical Ops, Universal Object Reflection, Semantic UI Tree, All 38+ Variant Types |
| **4.8 (dev)** | **Fully Supported (Active Dev)** | **Universal Reflection + Gen Tracking + Dynamic ClassDB** | **Full Semantic UI Tree + Multi-Window + Accessibility API** | **Texture Streaming, Trail3D, Next-Gen Multi-Viewport, Dynamic ClassDB 4.8, Ephemeral GDScript Omnipotence, Modern GDScript Analyzer** |

---

## 2. Universal Object Reflection (`obj://`) Version Independence

Godot Omni's reflection architecture decouples tool registration from specific engine builds:
- Uses deterministic URI handles: `obj://<session_id>/<object_id>`
- Queries live ClassDB directly over the authenticated bridge
- Implements generation counters to immediately catch `OBJECT_FREED` exceptions
- Preserves backwards compatibility with legacy Godot 4.1+ nodes while unlocking full next-gen 4.7+ capabilities.

---

## 3. Local Installation Status

On this host:
- Local configurations found in `%APPDATA%\Godot`:
  - `editor_settings-4.7.tres`
  - `editor_settings-4.8.tres`
- The Godot Omni plugin (`res://addons/godot_omni/`) is engineered for plug-and-play installation across all modern Godot 4 installations.
