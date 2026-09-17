"""Curated Systems Operations (UI, Theme, Multiplayer, Autoload, Batch, Test, Build, Localization, XR, Workflows)."""

from __future__ import annotations

from godot_omni.operations.builder import op
from godot_omni.registry.models import (
    CanonicalOperation,
    LatencyTier,
    ReadWrite,
)


def get_curated_systems_operations() -> list[CanonicalOperation]:
    ops: list[CanonicalOperation] = [
        # --- UI & CONTAINERS ---
        op(
            "ui.button.create",
            "Create Button Control",
            "Add a Button Control with text label and custom layout anchors.",
            "ui",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent control or node path", False, "", []),
                ("name", "string", "Button node name", False, "Button", []),
                ("text", "string", "Button display text", False, "Click Me", []),
            ],
            aliases=["create_button", "ui_create_button"],
        ),
        op(
            "ui.label.create",
            "Create Label / RichTextLabel Control",
            "Add a text Label or BBCode-enabled RichTextLabel.",
            "ui",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("text", "string", "Display text or BBCode", False, "Hello World", []),
                ("is_rich_text", "boolean", "Use RichTextLabel with BBCode formatting", False, False, []),
            ],
            aliases=["create_label", "ui_create_label"],
        ),
        op(
            "ui.container.create",
            "Create Layout Container",
            "Add a VBoxContainer, HBoxContainer, GridContainer, or PanelContainer.",
            "ui",
            read_write=ReadWrite.WRITE,
            params=[
                ("container_type", "string", "Container class", True, "VBoxContainer", ["VBoxContainer", "HBoxContainer", "GridContainer", "MarginContainer", "PanelContainer", "ScrollContainer", "CenterContainer"]),
                ("parent_path", "string", "Parent node path", False, "", []),
                ("name", "string", "Node name", False, "", []),
            ],
            aliases=["create_container", "ui_create_container"],
        ),
        op(
            "ui.layout.set_anchor_preset",
            "Set Control Anchor Preset",
            "Apply layout preset (Full Rect, Center, Top Wide, Bottom Wide, etc.) to a Control.",
            "ui",
            read_write=ReadWrite.WRITE,
            params=[
                ("path", "string", "Control node path", True, None, []),
                ("preset", "string", "Anchor preset name", True, "full_rect", ["full_rect", "center", "top_wide", "bottom_wide", "left_wide", "right_wide", "top_left", "center_top"]),
            ],
            aliases=["set_anchor_preset", "ui_set_anchor_preset"],
        ),
        op(
            "ui.layout.inspect",
            "Inspect Control Layout Hierarchy",
            "Explain the exact sizing rules, size flags, anchor offsets, and container constraints of a UI element.",
            "ui",
            read_write=ReadWrite.READ,
            params=[("path", "string", "Control node path", True, None, [])],
            aliases=["inspect_layout", "ui_inspect_layout"],
        ),

        # --- THEMES ---
        op(
            "theme.create",
            "Create Theme Resource",
            "Create a new Theme (.tres) resource for application-wide or node-specific styling.",
            "theme",
            read_write=ReadWrite.WRITE,
            latency_tier=LatencyTier.DISK,
            params=[
                ("path", "string", "res:// path to Theme resource", True, None, []),
                ("default_font_size", "integer", "Base font size in points", False, 16, []),
            ],
            aliases=["create_theme", "theme_create"],
        ),
        op(
            "theme.set_stylebox_flat",
            "Configure StyleBoxFlat",
            "Create or configure a StyleBoxFlat with background color, corner radii, and borders.",
            "theme",
            read_write=ReadWrite.WRITE,
            latency_tier=LatencyTier.DISK,
            params=[
                ("path", "string", "res:// path to StyleBoxFlat resource", True, None, []),
                ("bg_color", "string", "Background color hex string", False, "#202020", []),
                ("corner_radius", "integer", "Corner rounding radius in pixels", False, 4, []),
                ("border_width", "integer", "Border thickness", False, 0, []),
                ("border_color", "string", "Border color hex string", False, "#404040", []),
            ],
            aliases=["set_stylebox_flat", "theme_set_stylebox_flat"],
        ),

        # --- AUTOLOADS ---
        op(
            "autoload.list",
            "List Project Autoload Singletons",
            "List all registered singleton scripts or scenes configured as autoloads.",
            "autoload",
            read_write=ReadWrite.READ,
            aliases=["list_autoloads", "autoload_list"],
        ),
        op(
            "autoload.add",
            "Register Project Autoload Singleton",
            "Add a global autoload singleton script or scene to project.godot.",
            "autoload",
            read_write=ReadWrite.WRITE,
            latency_tier=LatencyTier.DISK,
            params=[
                ("name", "string", "Global singleton name (e.g. GameManager)", True, None, []),
                ("path", "string", "res:// path to script or scene", True, None, []),
            ],
            aliases=["add_autoload", "autoload_add"],
        ),
        op(
            "autoload.remove",
            "Remove Project Autoload",
            "Remove an autoload singleton from project.godot.",
            "autoload",
            read_write=ReadWrite.WRITE,
            latency_tier=LatencyTier.DISK,
            params=[("name", "string", "Autoload singleton name to remove", True, None, [])],
            aliases=["remove_autoload", "autoload_remove"],
        ),

        # --- BATCH & TRANSACTIONS ---
        op(
            "batch.execute",
            "Execute Transactional Batch Commands",
            "Execute an atomic sequence of operations with rollback on failure.",
            "batch",
            read_write=ReadWrite.WRITE,
            params=[
                ("commands", "array", "List of command objects with 'command' and 'params'", True, None, []),
                ("atomic", "boolean", "Rollback on error if true", False, True, []),
            ],
            aliases=["batch_execute"],
        ),

        # --- TESTING ---
        op(
            "test.run",
            "Run In-Editor Test Suites",
            "Execute GDScript test suites inheriting from McpTestSuite inside the editor.",
            "testing",
            read_write=ReadWrite.READ,
            latency_tier=LatencyTier.RUNTIME,
            params=[
                ("test_file", "string", "res:// path to test script", False, "", []),
                ("filter", "string", "Test method name filter", False, "", []),
            ],
            aliases=["test_run", "run_test"],
        ),

        # --- BUILD & EXPORT ---
        op(
            "build.list_presets",
            "List Export Presets",
            "Retrieve export presets defined in export_presets.cfg (Windows, Linux, macOS, Web, Android).",
            "build",
            read_write=ReadWrite.READ,
            aliases=["list_export_presets", "build_list_presets"],
        ),
        op(
            "build.export",
            "Export Project Package",
            "Export project binary or .pck using an export preset.",
            "build",
            read_write=ReadWrite.WRITE,
            latency_tier=LatencyTier.BUILD,
            params=[
                ("preset_name", "string", "Export preset identifier", True, None, []),
                ("output_path", "string", "Destination binary file path", True, None, []),
                ("debug", "boolean", "Export with debug flags and symbols", False, True, []),
            ],
            aliases=["export_project", "build_export"],
        ),

        # --- MULTIPLAYER & NETWORKING ---
        op(
            "multiplayer.status",
            "Inspect Multiplayer State",
            "Inspect MultiplayerAPI peer connection state, connected peers, and authority IDs.",
            "multiplayer",
            read_write=ReadWrite.READ,
            aliases=["multiplayer_status"],
        ),
        op(
            "multiplayer.spawner.create",
            "Create MultiplayerSpawner Node",
            "Add a MultiplayerSpawner node with configured spawn paths.",
            "multiplayer",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("spawn_path", "string", "Node path where spawned nodes will be added", True, None, []),
                ("auto_spawn_scenes", "array", "List of res:// scene paths allowed to spawn", False, [], []),
            ],
            aliases=["create_multiplayer_spawner", "multiplayer_create_spawner"],
        ),

        # --- WORKFLOW MACROS ---
        op(
            "macro.create_third_person_controller",
            "Macro: Scaffold 3D Third-Person Controller",
            "Construct a complete third-person player rig including CharacterBody3D, CapsuleShape3D, CameraPivot, SpringArm3D, Camera3D, and movement script in a single step.",
            "workflow",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path (empty for root)", False, "", []),
                ("character_name", "string", "Player node name", False, "Player", []),
                ("add_input_actions", "boolean", "Automatically register move_forward/back/left/right/jump actions", False, True, []),
            ],
            aliases=["macro_create_third_person_controller"],
        ),
        op(
            "macro.create_pause_menu",
            "Macro: Scaffold UI Pause Menu",
            "Construct a modal pause menu CanvasLayer with resume, restart, and quit buttons wired with signals.",
            "workflow",
            read_write=ReadWrite.WRITE,
            aliases=["macro_create_pause_menu"],
        ),
        op("macro.create_audio_manager", "Macro: Scaffold Audio Manager Singleton", "Create an autoload audio manager with sound pools and volume fading.", "workflow", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent node path", False, "", [])]),
        op("macro.create_save_system", "Macro: Scaffold Save/Load System", "Generate a JSON/ConfigFile game save and restore system script.", "workflow", read_write=ReadWrite.WRITE),
        op("macro.create_fps_counter", "Macro: Add In-Game FPS Overlay", "Create a lightweight CanvasLayer label displaying real-time FPS and draw calls.", "workflow", read_write=ReadWrite.WRITE),

        # --- UI WIDGETS (EXTENDED) ---
        op("ui.line_edit.create", "Create LineEdit Text Input", "Add a single-line text input control with placeholder text.", "ui", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("placeholder", "string", "Placeholder text", False, "Enter text...", [])]),
        op("ui.text_edit.create", "Create TextEdit Multi-Line Input", "Add a multi-line code/text editor control.", "ui", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", [])]),
        op("ui.checkbox.create", "Create CheckBox Toggle", "Add a CheckBox toggle control.", "ui", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("text", "string", "Checkbox label", False, "Enabled", [])]),
        op("ui.option_button.create", "Create OptionButton Dropdown", "Add a dropdown selection control with menu items.", "ui", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("items", "array", "Initial item strings", False, [], [])]),
        op("ui.progress_bar.create", "Create ProgressBar Bar", "Add a progress bar indicator with min/max values.", "ui", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("min_val", "number", "Min value", False, 0.0, []), ("max_val", "number", "Max value", False, 100.0, [])]),
        op("ui.slider.create", "Create Slider Control (HSlider/VSlider)", "Add a horizontal or vertical draggable slider.", "ui", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("vertical", "boolean", "Use vertical slider", False, False, [])]),
        op("ui.spin_box.create", "Create SpinBox Number Input", "Add a numerical SpinBox with step and range.", "ui", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("min_val", "number", "Min", False, 0.0, []), ("max_val", "number", "Max", False, 100.0, [])]),
        op("ui.tab_container.create", "Create TabContainer Layout", "Add a multi-tab layout container.", "ui", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", [])]),
        op("ui.texture_rect.create", "Create TextureRect Control", "Add a TextureRect image display control with stretch modes.", "ui", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("texture_path", "string", "res:// image path", False, "", [])]),
        op("ui.theme_override.font_size", "Override Control Font Size", "Set font_size theme override on a Control node.", "ui", read_write=ReadWrite.WRITE, params=[("path", "string", "Control node path", True, None, []), ("font_size", "integer", "Font size in pt", True, 18, [])]),
        op("ui.theme_override.font_color", "Override Control Font Color", "Set font_color theme override on a Control node.", "ui", read_write=ReadWrite.WRITE, params=[("path", "string", "Control node path", True, None, []), ("color", "string", "Hex color (#ffffff)", True, None, [])]),

        # --- MULTIPLAYER (EXTENDED) ---
        op("multiplayer.peer.create_enet", "Create ENet Multiplayer Host/Client", "Configure ENetMultiplayerPeer as server host or client connection.", "multiplayer", read_write=ReadWrite.WRITE, params=[("is_server", "boolean", "Host server if true, join client if false", True, True, []), ("port", "integer", "Network port", False, 7777, []), ("address", "string", "Host IP address (client only)", False, "127.0.0.1", [])]),
        op("multiplayer.synchronizer.create", "Create MultiplayerSynchronizer", "Add a MultiplayerSynchronizer with replicated property paths.", "multiplayer", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent node path", True, None, []), ("properties", "array", "Property paths to sync", False, [], [])]),

        # --- LOCALIZATION (EXTENDED) ---
        op("localization.add_translation", "Add Translation Resource", "Register a Translation (.translation) resource in Project Settings.", "localization", read_write=ReadWrite.WRITE, latency_tier=LatencyTier.DISK, params=[("path", "string", "res:// path to translation resource", True, None, [])]),
        op("localization.set_locale", "Set Active Project Locale", "Switch the running game/editor test locale (e.g. 'en', 'es', 'ja').", "localization", read_write=ReadWrite.WRITE, params=[("locale", "string", "ISO locale code", True, "en", [])]),
        op("localization.get_locale", "Get Active Locale", "Retrieve the current active project locale.", "localization", read_write=ReadWrite.READ),

        # --- XR / OPENXR ---
        op("xr.get_capabilities", "Query XR / OpenXR Capabilities", "Inspect XRServer interfaces, active headset trackers, and refresh rates.", "xr", read_write=ReadWrite.READ),
        op("xr.origin_3d.create", "Create XROrigin3D Rig", "Create XROrigin3D with XRCamera3D and left/right XRController3D nodes.", "xr", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent node path", False, "", [])]),

        # --- DEBUGGER & PROFILING ---
        op("debug.breakpoints.list", "List Active Breakpoints", "List source files and line numbers of set script breakpoints.", "debug", read_write=ReadWrite.READ),
        op("debug.breakpoints.set", "Set Script Breakpoint", "Insert a debugger breakpoint at a specific line in a GDScript file.", "debug", read_write=ReadWrite.WRITE, params=[("script_path", "string", "res:// script path", True, None, []), ("line", "integer", "1-based line number", True, None, [])]),
        op("debug.breakpoints.clear", "Clear Breakpoints", "Clear all script breakpoints.", "debug", read_write=ReadWrite.WRITE),
        op("debug.stack.get", "Get Debug Callstack", "Retrieve active execution stack frames when game is paused at a break.", "debug", read_write=ReadWrite.READ),

        # --- PLUGIN MANAGEMENT ---
        op("plugin.list", "List Project Addons & Plugins", "List all installed plugins in res://addons/ and their enabled/disabled state.", "plugin", read_write=ReadWrite.READ),
        op("plugin.enable", "Enable Editor Plugin", "Enable an installed Godot editor plugin by name.", "plugin", read_write=ReadWrite.WRITE, latency_tier=LatencyTier.DISK, params=[("plugin_name", "string", "Folder name in res://addons/", True, None, [])]),
        op("plugin.disable", "Disable Editor Plugin", "Disable an editor plugin safely.", "plugin", read_write=ReadWrite.WRITE, latency_tier=LatencyTier.DISK, params=[("plugin_name", "string", "Folder name in res://addons/", True, None, [])]),

        # --- TRANSACTIONS & WORKFLOW ---
        op("transaction.begin", "Begin Atomic Transaction", "Start grouping subsequent mutating operations into an isolated rollback group.", "transaction", read_write=ReadWrite.WRITE),
        op("transaction.commit", "Commit Atomic Transaction", "Commit the open transaction and push a single unified undo/redo entry.", "transaction", read_write=ReadWrite.WRITE),
        op("transaction.rollback", "Rollback Transaction", "Abort the open transaction and restore prior scene and filesystem state.", "transaction", read_write=ReadWrite.WRITE),
        op("workflow.plan", "Dry-Run Plan Operation Workflow", "Inspect the sequence of primitive operations a high-level tool will execute without running them.", "workflow", read_write=ReadWrite.READ, params=[("action", "string", "High-level action name", True, None, []), ("params", "object", "Action arguments", False, {}, [])]),
    ]
    return ops
