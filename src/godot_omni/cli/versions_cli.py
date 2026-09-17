"""CLI handlers for 'godot-omni versions' commands."""

from __future__ import annotations

import argparse
import json

from godot_omni.versions import get_version_status


def handle_versions_status(args: argparse.Namespace) -> int:
    status = get_version_status()

    if getattr(args, "json", False):
        print(json.dumps(status, indent=2))
        return 0

    print("\n================================================================================")
    print("                      GODOT ENGINE VERSION COMPATIBILITY MATRIX                 ")
    print("================================================================================")
    if status["detected_local_versions"]:
        print(f"Detected Local Configurations: {', '.join(status['detected_local_versions'])}")
    print(f"Recommended Target Version   : {status['recommended_version']}")
    print("-" * 80)
    print(f"{'Version':<10} {'Status':<30} {'Reflection':<25} {'UI Automation'}")
    print("-" * 80)

    for row in status["matrix"]:
        print(f"{row['version']:<10} {row['status']:<30} {row['reflection_tier']:<25} {row['ui_automation']}")
        print(f"           Features: {', '.join(row['core_features'])}")
        print(f"           Notes   : {row['notes']}\n")

    print("================================================================================\n")
    return 0
