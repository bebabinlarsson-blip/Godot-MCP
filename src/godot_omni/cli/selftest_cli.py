"""CLI handlers for 'godot-omni self-test' command."""

from __future__ import annotations

import argparse
import json
import sys

from godot_omni.selftest import SelfTestRunner


def handle_self_test(args: argparse.Namespace) -> int:
    runner = SelfTestRunner()
    passed, results = runner.run_all()

    if getattr(args, "json", False):
        out = {
            "all_passed": passed,
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "message": r.message,
                    "duration_ms": round(r.duration_ms, 2),
                }
                for r in results
            ],
        }
        print(json.dumps(out, indent=2))
        return 0 if passed else 1

    print("\n==================================================")
    print("           GODOT OMNI END-TO-END SELF-TEST        ")
    print("==================================================")
    for r in results:
        badge = "[PASS]" if r.passed else "[FAIL]"
        print(f"{badge} {r.name:<55} ({r.duration_ms:>6.2f} ms)")
        print(f"       {r.message}")

    print("==================================================")
    if passed:
        print("[SUCCESS] All self-tests passed cleanly.\n")
        return 0
    else:
        print("[FAILURE] One or more self-tests failed.\n", file=sys.stderr)
        return 1
