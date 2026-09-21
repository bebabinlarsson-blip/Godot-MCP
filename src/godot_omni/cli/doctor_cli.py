"""CLI handlers for 'godot-omni doctor' command."""

from __future__ import annotations

import argparse
import json

from godot_omni.doctor import OmniDoctor


def handle_doctor(args: argparse.Namespace) -> int:
    doctor = OmniDoctor()
    report = doctor.run_all()

    if getattr(args, "json", False):
        print(json.dumps(report, indent=2))
        return 0 if report["all_passed"] else 1

    print("\n==================================================")
    print("               GODOT OMNI DOCTOR                  ")
    print("==================================================")
    for section in report["sections"]:
        sym = "OK" if section["passed"] else "WARN"
        print(f"\n[{sym:^4}] {section['title']}")
        print("-" * 50)
        for d in section["details"]:
            print(f"  * {d}")
        if section["recommendations"]:
            print("  Recommendations:")
            for r in section["recommendations"]:
                print(f"    ! {r}")

    print("\n==================================================")
    if report["all_passed"]:
        print("[SUCCESS] All system, engine, client, and registry diagnostics passed.\n")
        return 0
    else:
        print("[WARNING] Some diagnostics reported warnings or recommendations.\n")
        return 0
