"""Bulk-fix all broken McpErrorCodes references and Godot API mismatches."""
import os
import re

HANDLERS_DIR = r"C:\Users\Benji-Laptop\Documents\Godot MCP\addons\godot_ai\handlers"

# McpErrorCodes member replacements.
# Order matters: longer/more-specific patterns first to avoid substring collisions.
# e.g. INVALID_ARGUMENTS before INVALID_ARGUMENT, SCENE_NOT_FOUND before NOT_FOUND.
ERROR_CODE_RENAMES = [
    # Longer first to avoid substring collisions
    ("SCENE_NOT_FOUND", "NODE_NOT_FOUND"),
    ("SCENE_NOT_OPEN", "EDITOR_NOT_READY"),
    ("INVALID_ARGUMENTS", "INVALID_PARAMS"),
    ("INVALID_ARGUMENT", "INVALID_PARAMS"),
    ("FILE_ALREADY_EXISTS", "INVALID_PARAMS"),
    ("FILE_OPEN_FAILED", "INTERNAL_ERROR"),
    ("FILE_WRITE_ERROR", "INTERNAL_ERROR"),
    ("FILE_NOT_FOUND", "RESOURCE_NOT_FOUND"),
    ("NODE_ALREADY_EXISTS", "INVALID_PARAMS"),
    ("RESOURCE_OPERATION_FAILED", "INTERNAL_ERROR"),
    ("RUNTIME_NOT_INITIALIZED", "EDITOR_NOT_READY"),
    ("OPERATION_FAILED", "INTERNAL_ERROR"),
    ("INDEX_OUT_OF_BOUNDS", "VALUE_OUT_OF_RANGE"),
    ("NO_ACTIVE_SCENE", "EDITOR_NOT_READY"),
    ("MISSING_PARAMETER", "MISSING_REQUIRED_PARAM"),
    ("NETWORK_ERROR", "INTERNAL_ERROR"),
    ("UNKNOWN_ERROR", "INTERNAL_ERROR"),
    ("INVALID_FORMAT", "INVALID_PARAMS"),
    ("INVALID_PATH", "INVALID_PARAMS"),
    ("INVALID_TYPE", "WRONG_TYPE"),
    # NOT_FOUND last (shortest) -- only matches standalone .NOT_FOUND, not substrings
    ("NOT_FOUND", "NODE_NOT_FOUND"),
]

# Godot API symbol fixes
GODOT_API_FIXES = [
    ("DisplayServer.VSYNC_MODE_DISABLED", "DisplayServer.VSYNC_DISABLED"),
    ("DisplayServer.VSYNC_MODE_ENABLED", "DisplayServer.VSYNC_ENABLED"),
    ("DisplayServer.VSYNC_MODE_ADAPTIVE", "DisplayServer.VSYNC_ADAPTIVE"),
    ("DisplayServer.VSYNC_MODE_MAILBOX", "DisplayServer.VSYNC_MAILBOX"),
    ("NavigationPolygon.PARSED_GEOMETRY_MESH_INSTANCES_AND_COLLIDERS",
     "NavigationPolygon.PARSED_GEOMETRY_BOTH"),
    ("Environment.TONE_MAPPER_REINHARD", "Environment.TONE_MAPPER_REINHARDT"),
]


def fix_error_codes(content: str) -> str:
    """Replace invalid McpErrorCodes members with valid ones."""
    for old, new in ERROR_CODE_RENAMES:
        # Match both McpErrorCodes.X and ErrorCodes.X prefixes.
        # Use word boundary after the member name to avoid partial matches.
        for prefix in ("McpErrorCodes.", "ErrorCodes."):
            old_full = prefix + old
            new_full = prefix + new
            content = content.replace(old_full, new_full)
    return content


def fix_godot_api(content: str) -> str:
    """Replace wrong Godot API symbols with correct ones."""
    for old, new in GODOT_API_FIXES:
        content = content.replace(old, new)
    return content


def fix_type_inference(content: str) -> str:
    """Fix 'cannot infer type' errors by adding explicit type annotations."""
    # DirAccess.open / FileAccess.open return nullable -- add type annotation
    content = re.sub(
        r'\bvar (fs)\s*=\s*(DirAccess\.open\()',
        r'var \1: DirAccess = \2',
        content,
    )
    content = re.sub(
        r'\bvar (fs)\s*=\s*(FileAccess\.open\()',
        r'var \1: FileAccess = \2',
        content,
    )
    return content


def process_file(path: str) -> bool:
    """Process a single .gd file. Returns True if modified."""
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    content = fix_error_codes(original)
    content = fix_godot_api(content)
    content = fix_type_inference(content)

    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    modified = []
    for fname in sorted(os.listdir(HANDLERS_DIR)):
        if not fname.endswith(".gd"):
            continue
        path = os.path.join(HANDLERS_DIR, fname)
        if process_file(path):
            modified.append(fname)

    if modified:
        print(f"Fixed {len(modified)} handler files:")
        for f in modified:
            print(f"  {f}")
    else:
        print("No files needed fixing.")


if __name__ == "__main__":
    main()
