# Godot Omni — Godot Engine Version Compatibility Report

**Supported Godot Line**: Godot 4.7 and newer (including active 4.8 dev builds)
**Target Recommendation**: **Godot 4.7 stable**
**Local Installed Configurations Detected**: **Not verified in this checkout**

---

## 1. Version Compatibility Matrix

| Version | Status | Reflection Tier | UI Automation Support | Key Capabilities |
|:---|:---:|:---:|:---:|:---|
| **4.1.x–4.6.x** | **Unsupported** | — | — | The plugin refuses startup; backend support begins at 4.7. |
| **4.7.x** | Supported (Stable) | Universal Reflection + Gen Tracking | Full Semantic UI Tree + OS Accessibility | 1,500+ Canonical Ops, Universal Object Reflection, Semantic UI Tree, All 38+ Variant Types |
| **4.8 (dev)** | Experimental | Universal Reflection + Gen Tracking | Full Semantic UI Tree | Not included in the release-blocking engine matrix. |

---

## 2. Universal Object Reflection (`obj://`) Version Independence

Godot Omni's reflection architecture decouples tool registration from specific engine builds:
- Uses deterministic URI handles: `obj://<session_id>/<object_id>`
- Queries live ClassDB directly over the authenticated bridge
- Implements generation counters to immediately catch `OBJECT_FREED` exceptions
- Requires Godot 4.7 or newer, matching the runtime server's enforced minimum.

---

## 3. Local Installation Status

The checkout's CI uses Godot 4.7.0 for the release-blocking editor tests. A local Godot executable was not available during this audit, so local GUI loading was not verified here.
