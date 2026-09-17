"""Curated Gameplay Operations (Physics, Collision, Navigation, Audio, Animation, InputMap, TileMap, GridMap, CSG)."""

from __future__ import annotations

from godot_omni.operations.builder import op
from godot_omni.registry.models import (
    CanonicalOperation,
    LatencyTier,
    ReadWrite,
)


def get_curated_gameplay_operations() -> list[CanonicalOperation]:
    ops: list[CanonicalOperation] = [
        # --- PHYSICS & BODIES ---
        op(
            "physics.character_body_3d.create",
            "Create CharacterBody3D Controller Rig",
            "Scaffold a complete CharacterBody3D with collision shape, visual mesh, and camera pivot.",
            "physics",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("name", "string", "Node name", False, "Player", []),
                ("shape_type", "string", "Collision shape type", False, "CapsuleShape3D", ["CapsuleShape3D", "BoxShape3D", "CylinderShape3D"]),
                ("height", "number", "Character height in meters", False, 1.8, []),
                ("radius", "number", "Character radius in meters", False, 0.4, []),
            ],
            aliases=["create_character_body_3d", "physics_create_character_3d"],
        ),
        op(
            "physics.character_body_2d.create",
            "Create CharacterBody2D Rig",
            "Scaffold a 2D platformer/top-down CharacterBody2D with collision shape and sprite slot.",
            "physics",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("name", "string", "Node name", False, "Player2D", []),
            ],
            aliases=["create_character_body_2d", "physics_create_character_2d"],
        ),
        op(
            "physics.rigid_body_3d.create",
            "Create RigidBody3D with Physics",
            "Create a physics-simulated RigidBody3D with mass, gravity scale, and collision shape.",
            "physics",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("name", "string", "Node name", False, "RigidBody3D", []),
                ("mass", "number", "Object mass in kg", False, 1.0, []),
                ("shape_type", "string", "Collision shape type", False, "BoxShape3D", ["BoxShape3D", "SphereShape3D"]),
            ],
            aliases=["create_rigid_body_3d", "physics_create_rigid_3d"],
        ),
        op(
            "physics.collision.set_layers",
            "Configure Collision Layer & Mask",
            "Set the 32-bit collision layer and mask bitmasks on any 2D/3D physics body or Area.",
            "physics",
            read_write=ReadWrite.WRITE,
            params=[
                ("path", "string", "Physics node path", True, None, []),
                ("collision_layer", "integer", "Collision layer bitmask", False, None, []),
                ("collision_mask", "integer", "Collision mask bitmask", False, None, []),
            ],
            aliases=["set_collision_layers", "physics_set_layers"],
        ),

        # --- COLLISION SHAPE GENERATION ---
        op(
            "collision.shape_3d.create",
            "Add CollisionShape3D to Physics Body",
            "Create a CollisionShape3D child with Box, Sphere, Capsule, or Cylinder shape resource.",
            "collision",
            read_write=ReadWrite.WRITE,
            params=[
                ("body_path", "string", "Parent physics body or Area3D path", True, None, []),
                ("shape_type", "string", "Shape class", True, "BoxShape3D", ["BoxShape3D", "SphereShape3D", "CapsuleShape3D", "CylinderShape3D"]),
                ("size", "array", "Dimensions coordinates", False, None, []),
            ],
            aliases=["create_collision_shape_3d", "collision_create_shape_3d"],
        ),
        op(
            "collision.autofit_from_mesh",
            "Autofit Collision Shape from Mesh Bounds",
            "Automatically calculate and assign a bounding collision shape fitting a MeshInstance3D's AABB geometry.",
            "collision",
            read_write=ReadWrite.WRITE,
            params=[
                ("mesh_path", "string", "MeshInstance3D node path", True, None, []),
                ("shape_type", "string", "Fitting shape type", False, "BoxShape3D", ["BoxShape3D", "CapsuleShape3D", "SphereShape3D", "ConvexPolygonShape3D"]),
            ],
            aliases=["autofit_collision_from_mesh", "collision_autofit_mesh"],
        ),

        # --- NAVIGATION ---
        op(
            "navigation.region_3d.create",
            "Create NavigationRegion3D",
            "Create a 3D navigation region with NavigationMesh resource for pathfinding.",
            "navigation",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("name", "string", "Node name", False, "NavigationRegion3D", []),
            ],
            aliases=["create_navigation_region_3d", "navigation_create_region_3d"],
        ),
        op(
            "navigation.bake_navmesh",
            "Bake 3D Navigation Mesh",
            "Trigger navmesh generation from parsed scene geometry.",
            "navigation",
            read_write=ReadWrite.WRITE,
            latency_tier=LatencyTier.LONG_JOB,
            params=[("region_path", "string", "NavigationRegion3D node path", True, None, [])],
            aliases=["bake_navmesh", "navigation_bake_navmesh"],
        ),
        op(
            "navigation.agent_3d.create",
            "Create NavigationAgent3D Node",
            "Add a NavigationAgent3D with pathfinding and obstacle avoidance configuration.",
            "navigation",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent character node path", True, None, []),
                ("target_desired_distance", "number", "Acceptable arrival radius in meters", False, 1.0, []),
                ("avoidance_enabled", "boolean", "Enable RVO avoidance", False, True, []),
            ],
            aliases=["create_navigation_agent_3d", "navigation_create_agent_3d"],
        ),

        # --- AUDIO ---
        op(
            "audio.player_3d.create",
            "Create AudioStreamPlayer3D",
            "Add a spatial 3D audio emitter with falloff and bus routing.",
            "audio",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("stream_path", "string", "res:// path to AudioStream resource", False, "", []),
                ("bus", "string", "Target audio bus name", False, "Master", []),
                ("max_distance", "number", "Audible distance limit", False, 20.0, []),
            ],
            aliases=["create_audio_player_3d", "audio_create_player_3d"],
        ),
        op(
            "audio.bus.create",
            "Create Audio Bus",
            "Add a new named audio bus to Godot's AudioServer layout.",
            "audio",
            read_write=ReadWrite.WRITE,
            params=[
                ("name", "string", "New bus name (e.g. SFX, Music)", True, None, []),
                ("send_to", "string", "Parent bus to route into", False, "Master", []),
            ],
            aliases=["create_audio_bus", "audio_create_bus"],
        ),

        # --- ANIMATION ---
        op(
            "animation.player.create",
            "Create AnimationPlayer Node",
            "Add an AnimationPlayer node with root motion support.",
            "animation",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("name", "string", "Node name", False, "AnimationPlayer", []),
            ],
            aliases=["create_animation_player", "animation_create_player"],
        ),
        op(
            "animation.clip.create",
            "Create Animation Clip in Library",
            "Create a new Animation resource with duration and loop mode.",
            "animation",
            read_write=ReadWrite.WRITE,
            params=[
                ("player_path", "string", "AnimationPlayer node path", True, None, []),
                ("animation_name", "string", "Name of animation (e.g. walk, idle)", True, None, []),
                ("duration", "number", "Duration in seconds", False, 1.0, []),
                ("loop_mode", "string", "Loop behavior", False, "none", ["none", "linear", "pingpong"]),
            ],
            aliases=["animation_create", "animation_create_clip"],
        ),
        op(
            "animation.track.add_property_key",
            "Add Property Track Keyframe",
            "Insert a keyframe value at a specific time offset on a node property track.",
            "animation",
            read_write=ReadWrite.WRITE,
            params=[
                ("player_path", "string", "AnimationPlayer node path", True, None, []),
                ("animation_name", "string", "Animation clip name", True, None, []),
                ("node_path", "string", "Target node path relative to root", True, None, []),
                ("property_name", "string", "Property name (e.g. position, rotation)", True, None, []),
                ("time", "number", "Timestamp in seconds", True, 0.0, []),
                ("value", "any", "Keyframe value", True, None, []),
            ],
            aliases=["add_animation_key", "animation_add_key"],
        ),

        # --- INPUT MAP ---
        op(
            "input_map.list_actions",
            "List Input Actions",
            "List all registered InputMap action names and their configured event bindings.",
            "input_map",
            read_write=ReadWrite.READ,
            aliases=["list_actions", "input_map_list_actions"],
        ),
        op(
            "input_map.add_action",
            "Add Input Action",
            "Define a new custom action in the project's InputMap.",
            "input_map",
            read_write=ReadWrite.WRITE,
            latency_tier=LatencyTier.DISK,
            params=[
                ("action", "string", "Action identifier (e.g. move_jump, fire)", True, None, []),
                ("deadzone", "number", "Analog deadzone threshold", False, 0.5, []),
            ],
            aliases=["add_action", "input_map_add_action"],
        ),
        op(
            "input_map.bind_key",
            "Bind Keyboard Key to Action",
            "Bind a physical or logical keyboard key to an input action.",
            "input_map",
            read_write=ReadWrite.WRITE,
            latency_tier=LatencyTier.DISK,
            params=[
                ("action", "string", "Target action name", True, None, []),
                ("key", "string", "Key name (e.g. W, Space, Escape, Shift)", True, None, []),
            ],
            aliases=["bind_key", "input_map_bind_key"],
        ),

        # --- TILEMAP ---
        op(
            "tilemap.create",
            "Create TileMap / TileMapLayer",
            "Create a TileMap or TileMapLayer node and assign a TileSet.",
            "tilemap",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("name", "string", "Node name", False, "TileMap", []),
                ("tileset_path", "string", "res:// path to TileSet resource", False, "", []),
            ],
            aliases=["create_tilemap", "tilemap_create"],
        ),
        op(
            "tilemap.set_cell",
            "Set Tile Cell",
            "Place a tile in a TileMap at specified grid coordinates.",
            "tilemap",
            read_write=ReadWrite.WRITE,
            params=[
                ("path", "string", "TileMap node path", True, None, []),
                ("layer", "integer", "Layer index", False, 0, []),
                ("coords", "array", "Grid coordinates [x, y]", True, None, []),
                ("source_id", "integer", "TileSet source ID", True, 0, []),
                ("atlas_coords", "array", "Tile coordinates in atlas [x, y]", False, [0, 0], []),
            ],
            aliases=["set_tile_cell", "tilemap_set_cell"],
        ),
        op(
            "tilemap.fill_rect",
            "Bulk Fill Tile Rectangle",
            "Fill a rectangular region with a selected tile in a single bulk operation.",
            "tilemap",
            read_write=ReadWrite.WRITE,
            params=[
                ("path", "string", "TileMap node path", True, None, []),
                ("layer", "integer", "Layer index", False, 0, []),
                ("rect", "array", "[x, y, width, height] grid rectangle", True, None, []),
                ("source_id", "integer", "TileSet source ID", True, 0, []),
                ("atlas_coords", "array", "Atlas coords [x, y]", False, [0, 0], []),
            ],
            aliases=["fill_tile_rect", "tilemap_fill_rect"],
        ),

        # --- GRIDMAP (3D TILES) ---
        op(
            "gridmap.create",
            "Create GridMap 3D Node",
            "Create a 3D GridMap node with a MeshLibrary for modular 3D level building.",
            "gridmap",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("mesh_library_path", "string", "res:// path to MeshLibrary", False, "", []),
                ("cell_size", "array", "3D cell dimensions [x, y, z]", False, [2, 2, 2], []),
            ],
            aliases=["create_gridmap", "gridmap_create"],
        ),
        op(
            "gridmap.set_cell",
            "Set 3D GridMap Cell Item",
            "Place a 3D mesh item from the MeshLibrary into the GridMap.",
            "gridmap",
            read_write=ReadWrite.WRITE,
            params=[
                ("path", "string", "GridMap node path", True, None, []),
                ("coords", "array", "3D grid cell [x, y, z]", True, None, []),
                ("item_id", "integer", "Item ID from MeshLibrary (-1 to clear)", True, 0, []),
                ("orientation", "integer", "Item 3D orientation integer", False, 0, []),
            ],
            aliases=["set_gridmap_cell", "gridmap_set_cell"],
        ),

        # --- CSG ---
        op(
            "csg.box.create",
            "Create CSGBox3D with Boolean Operation",
            "Create a CSGBox3D with dimensions and boolean operation (Union, Intersection, Subtraction).",
            "csg",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("name", "string", "Node name", False, "CSGBox3D", []),
                ("size", "array", "Box dimensions [x, y, z]", False, [2, 2, 2], []),
                ("operation", "string", "CSG boolean operation", False, "union", ["union", "intersection", "subtraction"]),
                ("use_collision", "boolean", "Generate physical collision automatically", False, True, []),
            ],
            aliases=["create_csg_box", "csg_create_box"],
        ),
        op("csg.sphere.create", "Create CSGSphere3D", "Add a CSGSphere3D shape with radius and rings.", "csg", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("radius", "number", "Radius", False, 1.0, []), ("radial_segments", "integer", "Segments", False, 12, [])]),
        op("csg.cylinder.create", "Create CSGCylinder3D", "Add a CSGCylinder3D with height and radius.", "csg", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("radius", "number", "Radius", False, 1.0, []), ("height", "number", "Height", False, 2.0, [])]),
        op("csg.torus.create", "Create CSGTorus3D", "Add a CSGTorus3D with inner/outer radii.", "csg", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("inner_radius", "number", "Inner radius", False, 0.5, []), ("outer_radius", "number", "Outer radius", False, 1.0, [])]),
        op("csg.polygon.create", "Create CSGPolygon3D", "Extrude 2D polygon profile into 3D CSG geometry.", "csg", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("polygon", "array", "2D polygon vertices", True, None, []), ("depth", "number", "Extrusion depth", False, 1.0, [])]),
        op("csg.combiner.create", "Create CSGCombiner3D", "Add a CSGCombiner3D container for complex boolean hierarchies.", "csg", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", [])]),

        # --- PHYSICS & JOINTS (EXTENDED) ---
        op("physics.raycast_3d.create", "Create RayCast3D", "Add RayCast3D node with target vector and mask.", "physics", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("target_position", "array", "Ray vector [x, y, z]", False, [0, -1, 0], [])]),
        op("physics.raycast_2d.create", "Create RayCast2D", "Add RayCast2D node with target vector.", "physics", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("target_position", "array", "Ray vector [x, y]", False, [0, 50], [])]),
        op("physics.shapecast_3d.create", "Create ShapeCast3D", "Add ShapeCast3D node for swept collision detection.", "physics", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("shape_type", "string", "Shape class", False, "SphereShape3D", [])]),
        op("physics.area_2d.create", "Create Area2D Trigger", "Add Area2D node with collision shape for overlap detection.", "physics", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("name", "string", "Area name", False, "Area2D", [])]),
        op("physics.joint_3d.pin", "Create PinJoint3D", "Connect two 3D physics bodies with a ball-and-socket pin joint.", "physics", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("node_a", "string", "Body A path", True, None, []), ("node_b", "string", "Body B path", True, None, [])]),
        op("physics.joint_3d.hinge", "Create HingeJoint3D", "Connect two 3D bodies with a rotational hinge joint.", "physics", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("node_a", "string", "Body A path", True, None, []), ("node_b", "string", "Body B path", True, None, [])]),
        op("physics.joint_2d.pin", "Create PinJoint2D", "Connect two 2D physics bodies with a pin joint.", "physics", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("node_a", "string", "Body A path", True, None, []), ("node_b", "string", "Body B path", True, None, [])]),

        # --- COLLISION (EXTENDED) ---
        op("collision.shape_2d.create", "Create CollisionShape2D", "Add CollisionShape2D child with Circle, Rectangle, or Capsule shape.", "collision", read_write=ReadWrite.WRITE, params=[("body_path", "string", "Parent 2D body path", True, None, []), ("shape_type", "string", "Shape class", False, "RectangleShape2D", ["RectangleShape2D", "CircleShape2D", "CapsuleShape2D"])]),
        op("collision.polygon_2d.create", "Create CollisionPolygon2D", "Add CollisionPolygon2D with custom vertex array.", "collision", read_write=ReadWrite.WRITE, params=[("body_path", "string", "Parent body path", True, None, []), ("polygon", "array", "2D vertex points", True, None, [])]),
        op("collision.autofit_from_sprite", "Autofit 2D Collision from Sprite", "Generate CollisionPolygon2D or RectangleShape2D from Sprite2D bounds or alpha contour.", "collision", read_write=ReadWrite.WRITE, params=[("sprite_path", "string", "Sprite2D node path", True, None, []), ("use_alpha_contour", "boolean", "Trace transparent pixel outline", False, True, [])]),

        # --- ANIMATION (EXTENDED) ---
        op("animation.track.add_method_key", "Add Method Track Keyframe", "Add method invocation keyframe to Animation clip.", "animation", read_write=ReadWrite.WRITE, params=[("player_path", "string", "AnimationPlayer path", True, None, []), ("animation_name", "string", "Animation clip", True, None, []), ("node_path", "string", "Target node", True, None, []), ("method_name", "string", "Method name", True, None, []), ("time", "number", "Timestamp", True, 0.0, []), ("args", "array", "Method arguments", False, [], [])]),
        op("animation.track.add_audio_key", "Add Audio Track Keyframe", "Add AudioStream playback keyframe to Animation clip.", "animation", read_write=ReadWrite.WRITE, params=[("player_path", "string", "AnimationPlayer path", True, None, []), ("animation_name", "string", "Clip name", True, None, []), ("stream_path", "string", "res:// audio path", True, None, []), ("time", "number", "Timestamp", True, 0.0, [])]),
        op("animation.state_machine.create", "Create AnimationTree State Machine", "Create AnimationTree configured with AnimationNodeStateMachine.", "animation", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent node path", False, "", []), ("player_path", "string", "NodePath to AnimationPlayer", True, None, [])]),
        op("animation.state_machine.travel", "Travel State Machine to State", "Trigger state transition in active AnimationTree state machine.", "animation", read_write=ReadWrite.WRITE, params=[("tree_path", "string", "AnimationTree path", True, None, []), ("state_name", "string", "Destination state name", True, None, [])]),

        # --- TWEENS ---
        op("tween.property", "Create Property Tween", "Animate a node property over duration with ease and transition curves.", "tween", read_write=ReadWrite.WRITE, params=[("node_path", "string", "Target node path", True, None, []), ("property", "string", "Property name", True, None, []), ("final_val", "any", "Target value", True, None, []), ("duration", "number", "Duration in seconds", True, 1.0, []), ("trans_type", "string", "Transition curve", False, "linear", ["linear", "sine", "quad", "cubic", "quart", "quint", "expo", "elastic", "bounce", "back"]), ("ease_type", "string", "Ease mode", False, "in_out", ["in", "out", "in_out", "out_in"])]),
        op("tween.method", "Create Method Tween", "Call a method continuously with interpolated values over duration.", "tween", read_write=ReadWrite.WRITE, params=[("node_path", "string", "Target node path", True, None, []), ("method", "string", "Method name", True, None, []), ("from_val", "any", "Start value", True, None, []), ("to_val", "any", "Target value", True, None, []), ("duration", "number", "Duration", True, 1.0, [])]),

        # --- NAVIGATION (EXTENDED) ---
        op("navigation.link_3d.create", "Create NavigationLink3D", "Add off-mesh navigation link for jumping, climbing, or teleports.", "navigation", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("start_pos", "array", "Start [x, y, z]", True, None, []), ("end_pos", "array", "End [x, y, z]", True, None, []), ("bidirectional", "boolean", "Allow two-way traversal", False, True, [])]),
        op("navigation.obstacle_3d.create", "Create NavigationObstacle3D", "Add dynamic avoidance obstacle.", "navigation", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("radius", "number", "Avoidance radius", False, 1.0, [])]),

        # --- AUDIO (EXTENDED) ---
        op("audio.stream_player_2d.create", "Create AudioStreamPlayer2D", "Add 2D spatialized audio emitter.", "audio", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent path", False, "", []), ("stream_path", "string", "res:// audio path", False, "", [])]),
        op("audio.bus.set_volume", "Set Audio Bus Volume", "Set volume dB on an AudioServer bus.", "audio", read_write=ReadWrite.WRITE, params=[("bus_name", "string", "Bus name (Master, SFX, Music)", True, "Master", []), ("volume_db", "number", "Volume in dB (0 = nominal)", True, 0.0, [])]),
        op("audio.bus.add_effect", "Add Audio Bus Effect", "Insert effect (Reverb, EQ, Delay, Filter) into an audio bus.", "audio", read_write=ReadWrite.WRITE, params=[("bus_name", "string", "Target bus", True, "Master", []), ("effect_type", "string", "Effect class (AudioEffectReverb, AudioEffectEQ, AudioEffectDelay)", True, None, [])]),

        # --- TILEMAP & GRIDMAP (EXTENDED) ---
        op("tilemap.place_tile", "Place Tile with Transform", "Place a tile with rotation degrees, flip_h, flip_v flags.", "tilemap", read_write=ReadWrite.WRITE, params=[("path", "string", "TileMap path", True, None, []), ("source_id", "integer", "Source ID", True, 0, []), ("atlas_col", "integer", "Atlas X", True, 0, []), ("atlas_row", "integer", "Atlas Y", True, 0, []), ("map_x", "integer", "Map X", True, 0, []), ("map_y", "integer", "Map Y", True, 0, []), ("rotation_degrees", "integer", "Rotation (0, 90, 180, 270)", False, 0, []), ("flip_h", "boolean", "Flip horizontal", False, False, []), ("flip_v", "boolean", "Flip vertical", False, False, [])], aliases=["place_tile", "tilemap_place_tile"]),
        op("tilemap.rotate_cell", "Rotate Tile Cell", "Rotate an existing tile cell clockwise by degrees.", "tilemap", read_write=ReadWrite.WRITE, params=[("path", "string", "TileMap path", True, None, []), ("map_x", "integer", "Map X", True, 0, []), ("map_y", "integer", "Map Y", True, 0, []), ("degrees", "integer", "Degrees (90, 180, 270)", False, 90, [])], aliases=["rotate_tile_cell", "tilemap_rotate_cell"]),
        op("tilemap.flip_cell", "Flip Tile Cell", "Flip an existing tile cell horizontally or vertically.", "tilemap", read_write=ReadWrite.WRITE, params=[("path", "string", "TileMap path", True, None, []), ("map_x", "integer", "Map X", True, 0, []), ("map_y", "integer", "Map Y", True, 0, []), ("flip_h", "boolean", "Flip H", False, False, []), ("flip_v", "boolean", "Flip V", False, False, [])], aliases=["flip_tile_cell", "tilemap_flip_cell"]),
        op("tilemap.get_cell", "Get Tile Cell Info", "Inspect cell tile source, atlas coords, rotation, and flags.", "tilemap", read_write=ReadWrite.READ, params=[("path", "string", "TileMap path", True, None, []), ("map_x", "integer", "Map X", True, 0, []), ("map_y", "integer", "Map Y", True, 0, [])], aliases=["get_tile_cell", "tilemap_get_cell"]),
        op("tilemap.erase_cell", "Erase Tile Cell", "Clear a single tile cell from TileMap.", "tilemap", read_write=ReadWrite.WRITE, params=[("path", "string", "TileMap path", True, None, []), ("map_x", "integer", "Map X", False, 0, []), ("map_y", "integer", "Map Y", False, 0, []), ("coords", "array", "Grid coordinates [x, y]", False, None, [])]),
        op("tilemap.create_layer", "Add TileMap Layer", "Add an additional named layer to a TileMap.", "tilemap", read_write=ReadWrite.WRITE, params=[("path", "string", "TileMap path", True, None, []), ("layer_name", "string", "Layer title", True, None, [])]),
        op("gridmap.box_fill", "Box Fill 3D GridMap", "Fill a 3D bounding box volume with an item in a GridMap.", "gridmap", read_write=ReadWrite.WRITE, params=[("path", "string", "GridMap path", True, None, []), ("from_coords", "array", "Start [x, y, z]", True, None, []), ("to_coords", "array", "End [x, y, z]", True, None, []), ("item_id", "integer", "MeshLibrary item ID", True, 0, [])]),
        op("gridmap.clear", "Clear All GridMap Cells", "Erase all placed cells in a GridMap.", "gridmap", read_write=ReadWrite.WRITE, params=[("path", "string", "GridMap path", True, None, [])]),

        # --- ANIMATION PRESETS (EXTENDED) ---
        op("animation.preset_spin", "Preset: 360 Spin", "Create smooth 360-degree rotation animation clip.", "animation", read_write=ReadWrite.WRITE, params=[("player_path", "string", "AnimationPlayer path", True, None, []), ("target_path", "string", "Target node to spin", True, None, []), ("duration", "number", "Duration in seconds", False, 1.0, []), ("loops", "integer", "Number of rotations", False, 1, []), ("clockwise", "boolean", "Clockwise rotation", False, True, []), ("axis", "string", "3D axis (x, y, z)", False, "y", [])], aliases=["preset_spin", "animation_preset_spin"]),
        op("animation.preset_bounce", "Preset: Vertical Bounce", "Create smooth jump/bounce squash-and-stretch animation clip.", "animation", read_write=ReadWrite.WRITE, params=[("player_path", "string", "AnimationPlayer path", True, None, []), ("target_path", "string", "Target node to bounce", True, None, []), ("height", "number", "Bounce height in pixels/units", False, 40.0, []), ("duration", "number", "Duration in seconds", False, 0.6, [])], aliases=["preset_bounce", "animation_preset_bounce"]),

        # --- NODE SPATIAL TRANSFORMS ---
        op("node.rotate", "Rotate Node", "Rotate a 2D or 3D node by angle in degrees.", "node", read_write=ReadWrite.WRITE, params=[("path", "string", "Node path", True, None, []), ("degrees", "number", "Rotation degrees", True, 0.0, []), ("axis", "string", "3D axis (x, y, z)", False, "y", []), ("relative", "boolean", "Apply relative to current rotation", False, False, [])], aliases=["rotate_node", "node_rotate"]),
        op("node.scale", "Scale Node", "Scale a 2D, 3D, or Control node.", "node", read_write=ReadWrite.WRITE, params=[("path", "string", "Node path", True, None, []), ("scale", "any", "Scale factor (number, [x, y], or [x, y, z])", True, 1.0, []), ("relative", "boolean", "Multiply current scale", False, False, [])], aliases=["scale_node", "node_scale"]),
        op("node.translate", "Translate Node", "Translate / offset a node position.", "node", read_write=ReadWrite.WRITE, params=[("path", "string", "Node path", True, None, []), ("offset", "any", "Offset ([x, y] or [x, y, z])", True, [0.0, 0.0], []), ("relative", "boolean", "Relative to current position", False, True, [])], aliases=["translate_node", "node_translate"]),

        # --- INPUT BINDINGS (EXTENDED) ---
        op("input_map.bind_mouse", "Bind Mouse Button to Action", "Bind mouse button (Left, Right, Middle, Wheel) to an input action.", "input_map", read_write=ReadWrite.WRITE, latency_tier=LatencyTier.DISK, params=[("action", "string", "Action name", True, None, []), ("button_index", "integer", "Mouse button index", True, 1, [])]),
        op("input_map.bind_joypad", "Bind Gamepad Button to Action", "Bind joypad button to an input action.", "input_map", read_write=ReadWrite.WRITE, latency_tier=LatencyTier.DISK, params=[("action", "string", "Action name", True, None, []), ("button_index", "integer", "Joypad button index", True, 0, [])]),
        op("input_map.remove_action", "Remove Input Action", "Delete an action and all its bindings from InputMap.", "input_map", read_write=ReadWrite.WRITE, latency_tier=LatencyTier.DISK, params=[("action", "string", "Action name to delete", True, None, [])]),
    ]
    return ops
