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
        status="Supported",
        core_features=["Node/Scene/Script Ops", "HTTP/WS Transport", "Basic ClassDB"],
        reflection_tier="Basic Object Call",
        ui_automation="Inspector & Node Path",
        notes="First production 4.x baseline. Fast and stable.",
    ),
    VersionCompatibility(
        version="4.2.x",
        status="Supported",
        core_features=["GDExtension 4.2", "TileMap Multi-layer", "Addon Auto-load"],
        reflection_tier="Method & Signal Discovery",
        ui_automation="Inspector & Scene Dock",
        notes="Full support for GDExtension workflows and custom types.",
    ),
    VersionCompatibility(
        version="4.3.x",
        status="Supported",
        core_features=["TileMapLayer Node", "Compositor Effects", "UID System", "AudioStreamInteractive"],
        reflection_tier="Full ClassDB Reflection",
        ui_automation="Semantic Control Tree",
        notes="TileMapLayer separation natively handled; UID tracking active.",
    ),
    VersionCompatibility(
        version="4.4.x",
        status="Supported",
        core_features=["Typed Dictionaries", "Jolt Physics Integration", "Lightmap Bicubic"],
        reflection_tier="Typed Variant Reflection",
        ui_automation="Semantic Control Tree + Shortcuts",
        notes="Strongly typed variant validation active.",
    ),
    VersionCompatibility(
        version="4.5.x",
        status="Supported",
        core_features=["Modern Rendering Pipelines", "Shader Global Buffers", "Audio Effect Graphs"],
        reflection_tier="Universal Object Reflection (obj://)",
        ui_automation="Full Semantic UI Tree + Shortcuts",
        notes="Zero-copy buffer support and modern shader parameters.",
    ),
    VersionCompatibility(
        version="4.6.x",
        status="Supported",
        core_features=["Advanced NavigationServer3D", "Async Asset Pipeline", "Threaded Node Loading"],
        reflection_tier="Universal Object Reflection (obj://)",
        ui_automation="Full Semantic UI Tree + Native OS Fallback",
        notes="Thread-safe operation queuing active.",
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
        status="Fully Supported (Active Dev)",
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
        notes="Direct first-class support for Godot 4.8 development builds (dev snapshots), Texture Streaming, Trail3D, and updated ClassDB.",
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
        "recommended_version": "4.7+ / 4.8 (dev)",
        "matrix": matrix_data,
    }
