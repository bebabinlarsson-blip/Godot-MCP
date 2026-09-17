"""CLI handlers for 'godot-omni clients' commands."""

from __future__ import annotations

import argparse
import json
import sys

from godot_omni.clients import ClientManager, ClientStatus


def handle_clients_detect(args: argparse.Namespace) -> int:
    cm = ClientManager()
    reports = cm.detect_all()

    if getattr(args, "json", False):
        print(json.dumps([r.to_dict() for r in reports], indent=2))
        return 0

    print("\n==================================================")
    print("             AI MCP CLIENTS DETECTION             ")
    print("==================================================")
    for r in reports:
        status_symbol = "OK" if r.installed else "  "
        print(f"[{status_symbol:^4}] {r.display_name:<25} Status: {r.status.value:<20}")
        if r.config_path:
            print(f"       Config: {r.config_path}")
        if r.binary_path:
            print(f"       Binary: {r.binary_path}")
    print("==================================================\n")
    return 0


def handle_clients_status(args: argparse.Namespace) -> int:
    cm = ClientManager()
    reports = cm.detect_all()
    installed = [r for r in reports if r.installed]

    if getattr(args, "json", False):
        print(json.dumps([r.to_dict() for r in installed], indent=2))
        return 0

    print("\n==================================================")
    print("             AI MCP CLIENTS STATUS                ")
    print("==================================================")
    for r in installed:
        badge = "ACTIVE" if r.status == ClientStatus.CONFIGURED else r.status.value.upper()
        print(f"* {r.display_name:<25} [{badge}]")
        if r.details:
            print(f"    Details: {r.details}")
        if r.config_path:
            print(f"    Path   : {r.config_path}")
    print("==================================================\n")
    return 0


def handle_clients_configure(args: argparse.Namespace) -> int:
    cm = ClientManager()
    client_id = getattr(args, "client", None)
    configure_all = getattr(args, "all", False)

    if not client_id and not configure_all:
        print("[ERROR] Specify --client <client_id> or --all to configure.", file=sys.stderr)
        return 1

    targets: list[str] = []
    if configure_all:
        reports = cm.detect_all()
        targets = [r.client_id for r in reports if r.installed]
        if not targets:
            print("No installed AI clients found to configure.")
            return 0
    else:
        targets = [client_id]

    errors = 0
    print(f"\nConfiguring {len(targets)} client(s)...")
    print("-" * 60)
    for cid in targets:
        success, msg = cm.configure(cid)
        symbol = "OK" if success else "FAIL"
        print(f"[{symbol:^4}] {cid:<20}: {msg}")
        if not success:
            errors += 1
    print("-" * 60 + "\n")
    return 0 if errors == 0 else 1


def handle_clients_remove(args: argparse.Namespace) -> int:
    cm = ClientManager()
    client_id = getattr(args, "client", None)
    remove_all = getattr(args, "all", False)

    if not client_id and not remove_all:
        print("[ERROR] Specify --client <client_id> or --all to remove.", file=sys.stderr)
        return 1

    targets: list[str] = []
    if remove_all:
        reports = cm.detect_all()
        targets = [r.client_id for r in reports if r.status in (ClientStatus.CONFIGURED, ClientStatus.CONFIGURED_MISMATCH)]
        if not targets:
            print("No configured AI clients found to remove.")
            return 0
    else:
        targets = [client_id]

    errors = 0
    print(f"\nRemoving Godot Omni from {len(targets)} client(s)...")
    print("-" * 60)
    for cid in targets:
        success, msg = cm.remove(cid)
        symbol = "OK" if success else "FAIL"
        print(f"[{symbol:^4}] {cid:<20}: {msg}")
        if not success:
            errors += 1
    print("-" * 60 + "\n")
    return 0 if errors == 0 else 1


def handle_clients_doctor(args: argparse.Namespace) -> int:
    cm = ClientManager()
    report = cm.doctor()

    if getattr(args, "json", False):
        print(json.dumps(report, indent=2))
        return 0

    summary = report["summary"]
    print("\n==================================================")
    print("             AI MCP CLIENTS DOCTOR                ")
    print("==================================================")
    print(f"Known Supported Clients: {summary['total_known_clients']}")
    print(f"Installed Clients      : {summary['installed_clients']}")
    print(f"Configured Clients     : {summary['configured_clients']}")
    print("-" * 50)
    for c in report["checks"]:
        sym = "OK" if c["status"] == "configured" else ("-" if not c["installed"] else "WARN")
        print(f"[{sym:^4}] {c['client']:<25} ({c['status']})")
        if c["details"]:
            print(f"       {c['details']}")
    print("==================================================\n")
    return 0
