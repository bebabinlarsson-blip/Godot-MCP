"""Godot engine version compatibility matrix and status inspector."""

from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class VersionCompatibility:
    version: str
    status: str  # "Fully Supported", "Supported", "Legacy / Compatible", "Experimental"
    core_features: list[str]
    reflection_tier: str
    ui_automation: str
    notes: str


VERSION_MATRIX: list[VersionCompatibility] = [
    VersionCompatibility(
        version="4.1.x",
        status="Unsupported",
        core_features=["Node/Scene/Script Ops", "HTTP/WS Transport", "Basic ClassDB"],
        reflection_tier="Basic Object Call",
        ui_automation="Inspector & Node Path",
        notes="Godot AI v4 requires Godot 4.7 or newer; the plugin stays inactive on this version.",
    ),
    VersionCompatibility(
        version="4.2.x",
        status="Unsupported",
        core_features=["GDExtension 4.2", "TileMap Multi-layer", "Addon Auto-load"],
        reflection_tier="Method & Signal Discovery",
        ui_automation="Inspector & Scene Dock",
        notes="Godot AI v4 requires Godot 4.7 or newer; the plugin stays inactive on this version.",
    ),
    VersionCompatibility(
        version="4.3.x",
        status="Unsupported",
        core_features=["TileMapLayer Node", "Compositor Effects", "UID System", "AudioStreamInteractive"],
        reflection_tier="Full ClassDB Reflection",
        ui_automation="Semantic Control Tree",
        notes="Godot AI v4 requires Godot 4.7 or newer; the plugin stays inactive on this version.",
    ),
    VersionCompatibility(
        version="4.4.x",
        status="Unsupported",
        core_features=["Typed Dictionaries", "Jolt Physics Integration", "Lightmap Bicubic"],
        reflection_tier="Typed Variant Reflection",
        ui_automation="Semantic Control Tree + Shortcuts",
        notes="Godot AI v4 requires Godot 4.7 or newer; the plugin stays inactive on this version.",
    ),
    VersionCompatibility(
        version="4.5.x",
        status="Unsupported",
        core_features=["Modern Rendering Pipelines", "Shader Global Buffers", "Audio Effect Graphs"],
        reflection_tier="Universal Object Reflection (obj://)",
        ui_automation="Full Semantic UI Tree + Shortcuts",
        notes="Godot AI v4 requires Godot 4.7 or newer; the plugin stays inactive on this version.",
    ),
    VersionCompatibility(
        version="4.6.x",
        status="Unsupported",
        core_features=["Advanced NavigationServer3D", "Async Asset Pipeline", "Threaded Node Loading"],
        reflection_tier="Universal Object Reflection (obj://)",
        ui_automation="Full Semantic UI Tree + Native OS Fallback",
        notes="Godot AI v4 requires Godot 4.7 or newer; the plugin stays inactive on this version.",
    ),
    VersionCompatibility(
        version="4.7+",
        status="Supported (Stable)",
        core_features=["1,500+ Canonical Ops", "Universal Object Reflection", "Semantic UI Tree", "All 38+ Variant Types"],
        reflection_tier="Universal Object Reflection + Gen Tracking",
        ui_automation="Full Semantic UI Tree + OS Accessibility",
        notes="Production 4.7 baseline with complete engine coverage.",
    ),
    VersionCompatibility(
        version="4.8 (dev)",
        status="Experimental",
        core_features=[
            "Texture Streaming",
            "Trail3D",
            "Next-Gen Multi-Viewport",
            "Dynamic ClassDB 4.8",
            "Ephemeral GDScript Omnipotence",
            "Semantic Control Tree",
            "Modern GDScript Analyzer",
        ],
        reflection_tier="Universal Object Reflection + Gen Tracking + Dynamic ClassDB",
        ui_automation="Full Semantic UI Tree + Multi-Window + Accessibility API",
        notes=(
            "Development builds are not in the release-blocking test matrix; "
            "use Godot 4.7 for verified releases."
        ),
    ),
]


def detect_installed_godot_versions() -> list[str]:
    """Detects Godot versions from local configuration files and settings."""
    versions: list[str] = []
    if platform.system() == "Windows":
        appdata = os.environ.get("APPDATA", "")
        godot_dir = Path(appdata) / "Godot"
        if godot_dir.is_dir():
            for f in godot_dir.glob("editor_settings-*.tres"):
                # e.g. editor_settings-4.7.tres -> 4.7
                name = f.stem.replace("editor_settings-", "")
                if name and name not in versions:
                    versions.append(name)
    return sorted(versions)


def get_version_status() -> dict[str, Any]:
    installed = detect_installed_godot_versions()
    matrix_data = [
        {
            "version": v.version,
            "status": v.status,
            "reflection_tier": v.reflection_tier,
            "ui_automation": v.ui_automation,
            "core_features": v.core_features,
            "notes": v.notes,
        }
        for v in VERSION_MATRIX
    ]
    return {
        "detected_local_versions": installed,
        "recommended_version": "4.7+ (stable)",
        "matrix": matrix_data,
    }
