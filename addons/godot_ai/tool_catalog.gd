@tool
class_name McpToolCatalog
extends RefCounted

## Mirror of src/godot_ai/tools/domains.py — drives the dock's Tools tab
## so the UI can render checkboxes, tool counts, and tooltips without
## round-tripping to a running server.
##
## DO NOT EDIT by hand. tests/unit/test_tool_domains.py verifies this file
## against actual tool registration and fails CI when they drift; the
## failure message prints the up-to-date catalog body for paste-over.
##
## The four core tools are always registered and cannot be excluded — they
## render as a single grayed-out "Core" row in the UI. Each non-core domain
## now exposes one or two named verbs plus a single rolled-up
## `<domain>_manage` tool.

const CORE_TOOLS := [
	"editor_state",
	"node_get_properties",
	"scene_get_hierarchy",
	"session_activate",
]

## Non-core tools that live in a NON-excludable domain (only `session`
## today), so they appear in no DOMAINS row yet are always registered.
## Counted alongside CORE_TOOLS so the dock's totals match the real
## server surface.
const ALWAYS_ON_TOOLS := [
	"ping",
	"session_manage",
]

## Ordered list of user-toggleable domains. Each entry:
##   id:    matches the name passed to `--exclude-domains`
##   label: human-friendly display (same as id for now, kept separate so
##          a future renaming doesn't break the setting)
##   count: number of NON-CORE tools in this domain
##   tools: flat list of tool names registered by this domain (non-core only)
const DOMAINS := [
	{"id": "animation", "label": "animation", "count": 2, "tools": ["animation_create", "animation_manage"]},
	{"id": "animation_tree", "label": "animation_tree", "count": 1, "tools": ["animation_tree_manage"]},
	{"id": "api", "label": "api", "count": 1, "tools": ["api_manage"]},
	{"id": "audio", "label": "audio", "count": 1, "tools": ["audio_manage"]},
	{"id": "audio_effect", "label": "audio_effect", "count": 1, "tools": ["audio_effect_manage"]},
	{"id": "autoload", "label": "autoload", "count": 1, "tools": ["autoload_manage"]},
	{"id": "batch", "label": "batch", "count": 1, "tools": ["batch_execute"]},
	{"id": "body", "label": "body", "count": 1, "tools": ["body_manage"]},
	{"id": "camera", "label": "camera", "count": 1, "tools": ["camera_manage"]},
	{"id": "character", "label": "character", "count": 1, "tools": ["character_manage"]},
	{"id": "client", "label": "client", "count": 1, "tools": ["client_manage"]},
	{"id": "cloud", "label": "cloud", "count": 1, "tools": ["cloud_manage"]},
	{"id": "compute", "label": "compute", "count": 1, "tools": ["compute_manage"]},
	{"id": "config", "label": "config", "count": 1, "tools": ["config_manage"]},
	{"id": "crypto", "label": "crypto", "count": 1, "tools": ["crypto_manage"]},
	{"id": "csg", "label": "csg", "count": 1, "tools": ["csg_manage"]},
	{"id": "curve", "label": "curve", "count": 1, "tools": ["curve_manage"]},
	{"id": "custom", "label": "custom", "count": 1, "tools": ["custom_manage"]},
	{"id": "dialogue", "label": "dialogue", "count": 1, "tools": ["dialogue_manage"]},
	{"id": "display", "label": "display", "count": 1, "tools": ["display_manage"]},
	{"id": "editor", "label": "editor", "count": 4, "tools": ["editor_manage", "editor_reload_plugin", "editor_screenshot", "logs_read"]},
	{"id": "editor_settings", "label": "editor_settings", "count": 1, "tools": ["editor_settings_manage"]},
	{"id": "export", "label": "export", "count": 1, "tools": ["export_manage"]},
	{"id": "filesystem", "label": "filesystem", "count": 1, "tools": ["filesystem_manage"]},
	{"id": "font", "label": "font", "count": 1, "tools": ["font_manage"]},
	{"id": "fsm", "label": "fsm", "count": 1, "tools": ["fsm_manage"]},
	{"id": "game", "label": "game", "count": 1, "tools": ["game_manage"]},
	{"id": "geometry", "label": "geometry", "count": 1, "tools": ["geometry_manage"]},
	{"id": "gi", "label": "gi", "count": 1, "tools": ["gi_manage"]},
	{"id": "gridmap", "label": "gridmap", "count": 1, "tools": ["gridmap_manage"]},
	{"id": "headless", "label": "headless", "count": 1, "tools": ["headless_manage"]},
	{"id": "http", "label": "http", "count": 1, "tools": ["http_manage"]},
	{"id": "input_event", "label": "input_event", "count": 1, "tools": ["input_event_manage"]},
	{"id": "input_map", "label": "input_map", "count": 1, "tools": ["input_map_manage"]},
	{"id": "joint", "label": "joint", "count": 1, "tools": ["joint_manage"]},
	{"id": "light", "label": "light", "count": 1, "tools": ["light_manage"]},
	{"id": "loader", "label": "loader", "count": 1, "tools": ["loader_manage"]},
	{"id": "localization", "label": "localization", "count": 1, "tools": ["localization_manage"]},
	{"id": "material", "label": "material", "count": 1, "tools": ["material_manage"]},
	{"id": "mesh", "label": "mesh", "count": 1, "tools": ["mesh_manage"]},
	{"id": "multiplayer", "label": "multiplayer", "count": 1, "tools": ["multiplayer_manage"]},
	{"id": "navigation", "label": "navigation", "count": 1, "tools": ["navigation_manage"]},
	{"id": "nav_query", "label": "nav_query", "count": 1, "tools": ["nav_query_manage"]},
	{"id": "network", "label": "network", "count": 1, "tools": ["network_manage"]},
	{"id": "node", "label": "node", "count": 4, "tools": ["node_create", "node_find", "node_manage", "node_set_property"]},
	{"id": "occluder", "label": "occluder", "count": 1, "tools": ["occluder_manage"]},
	{"id": "omni", "label": "omni", "count": 1, "tools": ["omni_manage"]},
	{"id": "parallax", "label": "parallax", "count": 1, "tools": ["parallax_manage"]},
	{"id": "particle", "label": "particle", "count": 1, "tools": ["particle_manage"]},
	{"id": "path", "label": "path", "count": 1, "tools": ["path_manage"]},
	{"id": "pck", "label": "pck", "count": 1, "tools": ["pck_manage"]},
	{"id": "physics", "label": "physics", "count": 1, "tools": ["physics_manage"]},
	{"id": "physics_query", "label": "physics_query", "count": 1, "tools": ["physics_query_manage"]},
	{"id": "plugin", "label": "plugin", "count": 1, "tools": ["plugin_manage"]},
	{"id": "profiler", "label": "profiler", "count": 1, "tools": ["profiler_manage"]},
	{"id": "project", "label": "project", "count": 2, "tools": ["project_manage", "project_run"]},
	{"id": "recording", "label": "recording", "count": 1, "tools": ["recording_manage"]},
	{"id": "rendering", "label": "rendering", "count": 1, "tools": ["rendering_manage"]},
	{"id": "resource", "label": "resource", "count": 1, "tools": ["resource_manage"]},
	{"id": "save", "label": "save", "count": 1, "tools": ["save_manage"]},
	{"id": "scene", "label": "scene", "count": 3, "tools": ["scene_manage", "scene_open", "scene_save"]},
	{"id": "script", "label": "script", "count": 4, "tools": ["script_attach", "script_create", "script_manage", "script_patch"]},
	{"id": "shader", "label": "shader", "count": 1, "tools": ["shader_manage"]},
	{"id": "shader_global", "label": "shader_global", "count": 1, "tools": ["shader_global_manage"]},
	{"id": "signal", "label": "signal", "count": 1, "tools": ["signal_manage"]},
	{"id": "skeleton", "label": "skeleton", "count": 1, "tools": ["skeleton_manage"]},
	{"id": "sprite", "label": "sprite", "count": 1, "tools": ["sprite_manage"]},
	{"id": "system", "label": "system", "count": 1, "tools": ["system_manage"]},
	{"id": "testing", "label": "testing", "count": 2, "tools": ["test_manage", "test_run"]},
	{"id": "texture", "label": "texture", "count": 1, "tools": ["texture_manage"]},
	{"id": "theme", "label": "theme", "count": 1, "tools": ["theme_manage"]},
	{"id": "tilemap", "label": "tilemap", "count": 1, "tools": ["tilemap_manage"]},
	{"id": "tileset", "label": "tileset", "count": 1, "tools": ["tileset_manage"]},
	{"id": "tween", "label": "tween", "count": 1, "tools": ["tween_manage"]},
	{"id": "ui", "label": "ui", "count": 1, "tools": ["ui_manage"]},
	{"id": "undo_redo", "label": "undo_redo", "count": 1, "tools": ["undo_redo_manage"]},
	{"id": "viewport", "label": "viewport", "count": 1, "tools": ["viewport_manage"]},
	{"id": "visual_shader", "label": "visual_shader", "count": 1, "tools": ["visual_shader_manage"]},
	{"id": "world", "label": "world", "count": 1, "tools": ["world_manage"]},
	{"id": "xr", "label": "xr", "count": 1, "tools": ["xr_manage"]},
]


## Whether `id` is a real, excludable domain in this plugin version. Used to
## drop stale names (e.g. a domain removed since the setting was written) so
## they never reach the server's `--exclude-domains`, whose `parse_exclude_list`
## hard-fails on unknown names.
static func is_excludable_domain(id: String) -> bool:
	for d in DOMAINS:
		if d["id"] == id:
			return true
	return false


## Total tool count when no domains are excluded. Used for the "Enabled: N / M"
## readout in the Tools tab without looping the catalog on every repaint.
static func total_tool_count() -> int:
	var n := CORE_TOOLS.size() + ALWAYS_ON_TOOLS.size()
	for d in DOMAINS:
		n += int(d["count"])
	return n


## Tool count remaining after excluding the given set of domain ids.
static func enabled_tool_count(excluded: PackedStringArray) -> int:
	var n := CORE_TOOLS.size() + ALWAYS_ON_TOOLS.size()
	for d in DOMAINS:
		if excluded.find(d["id"]) == -1:
			n += int(d["count"])
	return n


## Canonical comma-separated string for a set of domain ids — sorted and
## deduplicated so two equivalent settings (entered in different orders)
## hash to the same EditorSetting value. Matches `excluded_domains()` in
## client_configurator.gd.
static func canonical(excluded: PackedStringArray) -> String:
	var seen := PackedStringArray()
	for e in excluded:
		var t := e.strip_edges()
		if not t.is_empty() and seen.find(t) == -1:
			seen.append(t)
	seen.sort()
	return ",".join(seen)
