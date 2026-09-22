"""Fix remaining type inference issues across handler files."""
import os
import re

HANDLERS_DIR = r"C:\Users\Benji-Laptop\Documents\Godot MCP\addons\godot_ai\handlers"


def fix_file(path: str) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    content = original

    # Fix: var fs := editor_interface.get_resource_filesystem()
    # Engine.get_singleton() returns Object, so := can't infer the type
    content = content.replace(
        "var fs := editor_interface.get_resource_filesystem()",
        "var fs = editor_interface.get_resource_filesystem()",
    )

    # Fix: var add_err := packer.pck_add_file(...)
    # pck_add_file returns Error enum which := can't always infer
    content = re.sub(
        r"var add_err := (packer\.pck_add_file\()",
        r"var add_err: int = \1",
        content,
    )

    # Fix: var flush_err := packer.flush(...)
    content = re.sub(
        r"var flush_err := (packer\.flush\()",
        r"var flush_err: int = \1",
        content,
    )

    # Fix undo_redo_handler type inference issues:
    # UndoRedo methods that return Variant through the editor undo/redo system
    # var action_name := ...get_current_action_name()  -> use =
    # var has_undo := ...has_undo()  -> use =
    # var has_redo := ...has_redo()  -> use =
    # var prev_action := ...  -> use =
    # var success := ...undo()  -> use =
    # var new_action := ...  -> use =
    content = re.sub(
        r"var (action_name|has_undo|has_redo|prev_action|success|new_action) := ",
        r"var \1 = ",
        content,
    )

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
        if fix_file(path):
            modified.append(fname)

    if modified:
        print(f"Fixed {len(modified)} files:")
        for f in modified:
            print(f"  {f}")
    else:
        print("No files needed fixing.")


if __name__ == "__main__":
    main()
