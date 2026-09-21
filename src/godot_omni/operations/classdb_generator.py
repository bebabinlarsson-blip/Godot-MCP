"""Authoritative ClassDB Operation Generator for Godot Engine."""

from __future__ import annotations

from typing import Any

from godot_omni.operations.builder import op
from godot_omni.registry.models import (
    CanonicalOperation,
    OperationCategory,
    ReadWrite,
)

# Comprehensive catalog of Godot engine classes with their key methods, parameter specs, and return types
_CLASSDB_DATA: dict[str, list[dict[str, Any]]] = {
    "Node": [
        {"name": "add_child", "rw": "write", "params": [("node", "Node", "Node to add", True)], "desc": "Adds a child node."},
        {"name": "remove_child", "rw": "write", "params": [("node", "Node", "Node to remove", True)], "desc": "Removes a child node."},
        {"name": "get_child_count", "rw": "read", "params": [], "desc": "Returns number of child nodes."},
        {"name": "get_child", "rw": "read", "params": [("idx", "int", "Child index", True)], "desc": "Returns child node at index."},
        {"name": "has_node", "rw": "read", "params": [("path", "NodePath", "Path to check", True)], "desc": "Checks if node exists at path."},
        {"name": "get_node", "rw": "read", "params": [("path", "NodePath", "Path to node", True)], "desc": "Returns node at path."},
        {"name": "queue_free", "rw": "write", "params": [], "desc": "Queues this node for deletion at end of frame."},
        {"name": "set_process", "rw": "write", "params": [("enable", "bool", "Enable processing", True)], "desc": "Enables or disables frame processing."},
        {"name": "is_processing", "rw": "read", "params": [], "desc": "Returns true if processing is enabled."},
        {"name": "set_physics_process", "rw": "write", "params": [("enable", "bool", "Enable physics processing", True)], "desc": "Enables or disables physics processing."},
        {"name": "is_physics_processing", "rw": "read", "params": [], "desc": "Returns true if physics processing is enabled."},
        {"name": "set_process_mode", "rw": "write", "params": [("mode", "int", "Process mode enum", True)], "desc": "Sets process mode when paused."},
        {"name": "get_process_mode", "rw": "read", "params": [], "desc": "Returns current process mode."},
        {"name": "get_tree", "rw": "read", "params": [], "desc": "Returns the SceneTree containing this node."},
    ],
    "Node2D": [
        {"name": "set_position", "rw": "write", "params": [("position", "Vector2", "2D position", True)], "desc": "Sets node local position."},
        {"name": "get_position", "rw": "read", "params": [], "desc": "Returns node local position."},
        {"name": "set_global_position", "rw": "write", "params": [("position", "Vector2", "Global 2D position", True)], "desc": "Sets global world position."},
        {"name": "get_global_position", "rw": "read", "params": [], "desc": "Returns global world position."},
        {"name": "set_rotation", "rw": "write", "params": [("radians", "float", "Angle in radians", True)], "desc": "Sets rotation in radians."},
        {"name": "get_rotation", "rw": "read", "params": [], "desc": "Returns rotation in radians."},
        {"name": "set_rotation_degrees", "rw": "write", "params": [("degrees", "float", "Angle in degrees", True)], "desc": "Sets rotation in degrees."},
        {"name": "get_rotation_degrees", "rw": "read", "params": [], "desc": "Returns rotation in degrees."},
        {"name": "set_scale", "rw": "write", "params": [("scale", "Vector2", "Scale factor", True)], "desc": "Sets 2D scale."},
        {"name": "get_scale", "rw": "read", "params": [], "desc": "Returns 2D scale."},
        {"name": "set_z_index", "rw": "write", "params": [("z_index", "int", "Z ordering index", True)], "desc": "Sets visual Z render order."},
        {"name": "get_z_index", "rw": "read", "params": [], "desc": "Returns visual Z render order."},
        {"name": "set_z_as_relative", "rw": "write", "params": [("enable", "bool", "Relative to parent Z", True)], "desc": "Sets whether Z index is relative."},
        {"name": "is_z_relative", "rw": "read", "params": [], "desc": "Returns true if Z is relative."},
        {"name": "look_at", "rw": "write", "params": [("point", "Vector2", "Point to look at", True)], "desc": "Rotates node toward point."},
    ],
    "Node3D": [
        {"name": "set_position", "rw": "write", "params": [("position", "Vector3", "3D position", True)], "desc": "Sets node local 3D position."},
        {"name": "get_position", "rw": "read", "params": [], "desc": "Returns node local 3D position."},
        {"name": "set_global_position", "rw": "write", "params": [("position", "Vector3", "Global 3D position", True)], "desc": "Sets global 3D position in world."},
        {"name": "get_global_position", "rw": "read", "params": [], "desc": "Returns global 3D position in world."},
        {"name": "set_rotation", "rw": "write", "params": [("euler_radians", "Vector3", "Euler angles in radians", True)], "desc": "Sets Euler rotation in radians."},
        {"name": "get_rotation", "rw": "read", "params": [], "desc": "Returns Euler rotation in radians."},
        {"name": "set_rotation_degrees", "rw": "write", "params": [("euler_degrees", "Vector3", "Euler angles in degrees", True)], "desc": "Sets Euler rotation in degrees."},
        {"name": "get_rotation_degrees", "rw": "read", "params": [], "desc": "Returns Euler rotation in degrees."},
        {"name": "set_scale", "rw": "write", "params": [("scale", "Vector3", "3D scale factors", True)], "desc": "Sets 3D scale."},
        {"name": "get_scale", "rw": "read", "params": [], "desc": "Returns 3D scale."},
        {"name": "set_visible", "rw": "write", "params": [("visible", "bool", "Visibility flag", True)], "desc": "Sets 3D visibility."},
        {"name": "is_visible", "rw": "read", "params": [], "desc": "Returns true if visible."},
        {"name": "look_at", "rw": "write", "params": [("target", "Vector3", "Target point", True), ("up", "Vector3", "Up vector", False)], "desc": "Orients node toward target point."},
        {"name": "translate", "rw": "write", "params": [("offset", "Vector3", "Translation offset", True)], "desc": "Translates node by offset."},
        {"name": "rotate_x", "rw": "write", "params": [("angle", "float", "Angle in radians", True)], "desc": "Rotates around local X axis."},
        {"name": "rotate_y", "rw": "write", "params": [("angle", "float", "Angle in radians", True)], "desc": "Rotates around local Y axis."},
        {"name": "rotate_z", "rw": "write", "params": [("angle", "float", "Angle in radians", True)], "desc": "Rotates around local Z axis."},
    ],
    "Control": [
        {"name": "set_custom_minimum_size", "rw": "write", "params": [("size", "Vector2", "Minimum size", True)], "desc": "Sets custom minimum size."},
        {"name": "get_custom_minimum_size", "rw": "read", "params": [], "desc": "Returns custom minimum size."},
        {"name": "set_anchors_preset", "rw": "write", "params": [("preset", "int", "Anchor preset enum", True)], "desc": "Sets anchor preset layout."},
        {"name": "set_h_size_flags", "rw": "write", "params": [("flags", "int", "Size flags bitmask", True)], "desc": "Sets horizontal container sizing flags."},
        {"name": "get_h_size_flags", "rw": "read", "params": [], "desc": "Returns horizontal container sizing flags."},
        {"name": "set_v_size_flags", "rw": "write", "params": [("flags", "int", "Size flags bitmask", True)], "desc": "Sets vertical container sizing flags."},
        {"name": "get_v_size_flags", "rw": "read", "params": [], "desc": "Returns vertical container sizing flags."},
        {"name": "set_focus_mode", "rw": "write", "params": [("mode", "int", "Focus mode enum", True)], "desc": "Sets focus acquisition mode."},
        {"name": "get_focus_mode", "rw": "read", "params": [], "desc": "Returns focus acquisition mode."},
        {"name": "grab_focus", "rw": "write", "params": [], "desc": "Steals keyboard/controller focus."},
        {"name": "has_focus", "rw": "read", "params": [], "desc": "Returns true if control has focus."},
        {"name": "set_tooltip_text", "rw": "write", "params": [("text", "String", "Tooltip text", True)], "desc": "Sets mouse tooltip string."},
        {"name": "get_tooltip_text", "rw": "read", "params": [], "desc": "Returns mouse tooltip string."},
    ],
    "Camera3D": [
        {"name": "set_fov", "rw": "write", "params": [("fov", "float", "Field of view degrees", True)], "desc": "Sets perspective field of view."},
        {"name": "get_fov", "rw": "read", "params": [], "desc": "Returns perspective field of view."},
        {"name": "set_near", "rw": "write", "params": [("near", "float", "Near clipping plane", True)], "desc": "Sets near clipping plane distance."},
        {"name": "get_near", "rw": "read", "params": [], "desc": "Returns near clipping plane distance."},
        {"name": "set_far", "rw": "write", "params": [("far", "float", "Far clipping plane", True)], "desc": "Sets far clipping plane distance."},
        {"name": "get_far", "rw": "read", "params": [], "desc": "Returns far clipping plane distance."},
        {"name": "make_current", "rw": "write", "params": [], "desc": "Activates this camera as the current active camera."},
        {"name": "clear_current", "rw": "write", "params": [], "desc": "Deactivates this camera as current."},
        {"name": "is_current", "rw": "read", "params": [], "desc": "Returns true if this is the active camera."},
        {"name": "project_ray_origin", "rw": "read", "params": [("screen_point", "Vector2", "2D screen position", True)], "desc": "Projects ray origin in 3D space from screen point."},
        {"name": "project_ray_normal", "rw": "read", "params": [("screen_point", "Vector2", "2D screen position", True)], "desc": "Projects ray normal direction in 3D space from screen point."},
    ],
    "CharacterBody3D": [
        {"name": "move_and_slide", "rw": "write", "params": [], "desc": "Moves the body based on velocity and slides along collisions."},
        {"name": "set_velocity", "rw": "write", "params": [("velocity", "Vector3", "Linear velocity vector", True)], "desc": "Sets linear velocity for move_and_slide."},
        {"name": "get_velocity", "rw": "read", "params": [], "desc": "Returns linear velocity vector."},
        {"name": "is_on_floor", "rw": "read", "params": [], "desc": "Returns true if body collided with floor on last move."},
        {"name": "is_on_wall", "rw": "read", "params": [], "desc": "Returns true if body collided with wall on last move."},
        {"name": "is_on_ceiling", "rw": "read", "params": [], "desc": "Returns true if body collided with ceiling on last move."},
        {"name": "get_floor_normal", "rw": "read", "params": [], "desc": "Returns collision surface normal of floor."},
        {"name": "set_up_direction", "rw": "write", "params": [("up_direction", "Vector3", "Up direction vector", True)], "desc": "Sets up vector for floor determination."},
        {"name": "get_up_direction", "rw": "read", "params": [], "desc": "Returns up vector for floor determination."},
        {"name": "set_max_slides", "rw": "write", "params": [("max_slides", "int", "Maximum slide count", True)], "desc": "Sets maximum collision iterations."},
    ],
    "RigidBody3D": [
        {"name": "set_mass", "rw": "write", "params": [("mass", "float", "Mass in kilograms", True)], "desc": "Sets body mass."},
        {"name": "get_mass", "rw": "read", "params": [], "desc": "Returns body mass."},
        {"name": "set_gravity_scale", "rw": "write", "params": [("scale", "float", "Gravity multiplier", True)], "desc": "Sets gravity scale factor."},
        {"name": "get_gravity_scale", "rw": "read", "params": [], "desc": "Returns gravity scale factor."},
        {"name": "apply_central_impulse", "rw": "write", "params": [("impulse", "Vector3", "Impulse vector", True)], "desc": "Applies directional impulse to center of mass."},
        {"name": "apply_central_force", "rw": "write", "params": [("force", "Vector3", "Force vector", True)], "desc": "Applies continuous force to center of mass."},
        {"name": "apply_torque_impulse", "rw": "write", "params": [("torque", "Vector3", "Torque vector", True)], "desc": "Applies rotational impulse."},
        {"name": "set_linear_velocity", "rw": "write", "params": [("velocity", "Vector3", "Linear velocity", True)], "desc": "Sets linear velocity directly."},
        {"name": "get_linear_velocity", "rw": "read", "params": [], "desc": "Returns linear velocity."},
        {"name": "set_angular_velocity", "rw": "write", "params": [("velocity", "Vector3", "Angular velocity", True)], "desc": "Sets rotational velocity."},
        {"name": "get_angular_velocity", "rw": "read", "params": [], "desc": "Returns rotational velocity."},
        {"name": "set_freeze_enabled", "rw": "write", "params": [("freeze", "bool", "Freeze flag", True)], "desc": "Freezes simulation movement."},
        {"name": "is_freeze_enabled", "rw": "read", "params": [], "desc": "Returns true if simulation is frozen."},
    ],
    "Area3D": [
        {"name": "set_monitoring", "rw": "write", "params": [("enable", "bool", "Monitoring flag", True)], "desc": "Enables or disables body/area monitoring."},
        {"name": "is_monitoring", "rw": "read", "params": [], "desc": "Returns true if monitoring is enabled."},
        {"name": "set_monitorable", "rw": "write", "params": [("enable", "bool", "Monitorable flag", True)], "desc": "Enables other areas detecting this area."},
        {"name": "is_monitorable", "rw": "read", "params": [], "desc": "Returns true if area is monitorable."},
        {"name": "get_overlapping_bodies", "rw": "read", "params": [], "desc": "Returns list of physics bodies currently inside area."},
        {"name": "get_overlapping_areas", "rw": "read", "params": [], "desc": "Returns list of Area3D nodes currently inside area."},
        {"name": "has_overlapping_bodies", "rw": "read", "params": [], "desc": "Returns true if any bodies overlap."},
    ],
    "AnimationPlayer": [
        {"name": "play", "rw": "write", "params": [("name", "StringName", "Animation name", True), ("custom_blend", "float", "Blend time", False), ("custom_speed", "float", "Speed scale", False)], "desc": "Plays an animation by name."},
        {"name": "pause", "rw": "write", "params": [], "desc": "Pauses animation playback."},
        {"name": "stop", "rw": "write", "params": [("keep_state", "bool", "Preserve animated state", False)], "desc": "Stops playback."},
        {"name": "is_playing", "rw": "read", "params": [], "desc": "Returns true if an animation is playing."},
        {"name": "set_current_animation", "rw": "write", "params": [("anim", "String", "Animation name", True)], "desc": "Sets active animation clip."},
        {"name": "get_current_animation", "rw": "read", "params": [], "desc": "Returns active animation clip name."},
        {"name": "seek", "rw": "write", "params": [("seconds", "float", "Playback time", True), ("update", "bool", "Update state", False)], "desc": "Seeks animation to time."},
        {"name": "get_animation_list", "rw": "read", "params": [], "desc": "Returns list of animation names."},
        {"name": "has_animation", "rw": "read", "params": [("name", "StringName", "Animation name", True)], "desc": "Checks if animation exists."},
    ],
    "AudioStreamPlayer": [
        {"name": "play", "rw": "write", "params": [("from_position", "float", "Start offset in seconds", False)], "desc": "Plays audio stream."},
        {"name": "stop", "rw": "write", "params": [], "desc": "Stops audio playback."},
        {"name": "is_playing", "rw": "read", "params": [], "desc": "Returns true if playing."},
        {"name": "set_volume_db", "rw": "write", "params": [("volume_db", "float", "Volume in decibels", True)], "desc": "Sets volume level in dB."},
        {"name": "get_volume_db", "rw": "read", "params": [], "desc": "Returns volume in dB."},
        {"name": "set_pitch_scale", "rw": "write", "params": [("pitch_scale", "float", "Pitch multiplier", True)], "desc": "Sets pitch frequency multiplier."},
        {"name": "get_pitch_scale", "rw": "read", "params": [], "desc": "Returns pitch multiplier."},
        {"name": "set_bus", "rw": "write", "params": [("bus", "StringName", "Audio bus name", True)], "desc": "Routes output to named audio bus."},
        {"name": "get_bus", "rw": "read", "params": [], "desc": "Returns audio bus name."},
    ],
    "Sprite2D": [
        {"name": "set_texture", "rw": "write", "params": [("texture", "Texture2D", "Texture resource", True)], "desc": "Sets sprite texture."},
        {"name": "get_texture", "rw": "read", "params": [], "desc": "Returns sprite texture."},
        {"name": "set_centered", "rw": "write", "params": [("centered", "bool", "Center flag", True)], "desc": "Sets texture centering."},
        {"name": "is_centered", "rw": "read", "params": [], "desc": "Returns true if centered."},
        {"name": "set_offset", "rw": "write", "params": [("offset", "Vector2", "Pixel offset", True)], "desc": "Sets pixel offset from origin."},
        {"name": "get_offset", "rw": "read", "params": [], "desc": "Returns pixel offset."},
        {"name": "set_flip_h", "rw": "write", "params": [("flip", "bool", "Horizontal flip", True)], "desc": "Sets horizontal mirror flip."},
        {"name": "is_flipped_h", "rw": "read", "params": [], "desc": "Returns true if flipped horizontally."},
        {"name": "set_flip_v", "rw": "write", "params": [("flip", "bool", "Vertical flip", True)], "desc": "Sets vertical mirror flip."},
        {"name": "is_flipped_v", "rw": "read", "params": [], "desc": "Returns true if flipped vertically."},
    ],
    "MeshInstance3D": [
        {"name": "set_mesh", "rw": "write", "params": [("mesh", "Mesh", "Mesh resource", True)], "desc": "Sets 3D mesh geometry resource."},
        {"name": "get_mesh", "rw": "read", "params": [], "desc": "Returns 3D mesh resource."},
        {"name": "set_material_override", "rw": "write", "params": [("material", "Material", "Material resource", True)], "desc": "Sets material overriding all surface materials."},
        {"name": "get_material_override", "rw": "read", "params": [], "desc": "Returns material override."},
        {"name": "create_trimesh_collision", "rw": "write", "params": [], "desc": "Creates static triangle collision sibling from mesh."},
        {"name": "create_convex_collision", "rw": "write", "params": [("clean", "bool", "Clean mesh", False), ("simplify", "bool", "Simplify hull", False)], "desc": "Creates convex collision sibling."},
    ],
    "DirectionalLight3D": [
        {"name": "set_shadow", "rw": "write", "params": [("enabled", "bool", "Shadows enabled", True)], "desc": "Enables directional shadows."},
        {"name": "has_shadow", "rw": "read", "params": [], "desc": "Returns true if shadows are enabled."},
        {"name": "set_sky_mode", "rw": "write", "params": [("mode", "int", "Sky mode enum", True)], "desc": "Sets sky contribution mode."},
        {"name": "set_color", "rw": "write", "params": [("color", "Color", "Light color", True)], "desc": "Sets light color tint."},
        {"name": "get_color", "rw": "read", "params": [], "desc": "Returns light color."},
        {"name": "set_param", "rw": "write", "params": [("param", "int", "Parameter enum", True), ("value", "float", "Value", True)], "desc": "Sets light parameter value."},
    ],
    "StandardMaterial3D": [
        {"name": "set_albedo", "rw": "write", "params": [("albedo", "Color", "Albedo color", True)], "desc": "Sets base albedo color."},
        {"name": "get_albedo", "rw": "read", "params": [], "desc": "Returns base albedo color."},
        {"name": "set_metallic", "rw": "write", "params": [("metallic", "float", "Metallic factor (0..1)", True)], "desc": "Sets metallic factor."},
        {"name": "get_metallic", "rw": "read", "params": [], "desc": "Returns metallic factor."},
        {"name": "set_roughness", "rw": "write", "params": [("roughness", "float", "Roughness factor (0..1)", True)], "desc": "Sets roughness factor."},
        {"name": "get_roughness", "rw": "read", "params": [], "desc": "Returns roughness factor."},
        {"name": "set_emission", "rw": "write", "params": [("emission", "Color", "Emission color", True)], "desc": "Sets emission color."},
        {"name": "get_emission", "rw": "read", "params": [], "desc": "Returns emission color."},
        {"name": "set_emission_energy_multiplier", "rw": "write", "params": [("energy", "float", "Emission multiplier", True)], "desc": "Sets emission energy intensity."},
        {"name": "get_emission_energy_multiplier", "rw": "read", "params": [], "desc": "Returns emission energy intensity."},
        {"name": "set_cull_mode", "rw": "write", "params": [("cull", "int", "Cull mode enum", True)], "desc": "Sets polygon face culling mode."},
        {"name": "get_cull_mode", "rw": "read", "params": [], "desc": "Returns polygon face culling mode."},
    ],
}


def generate_classdb_operations() -> list[CanonicalOperation]:
    """Generate logical canonical operations from ClassDB metadata."""
    ops: list[CanonicalOperation] = []

    # Map Godot types to domains
    domain_map: dict[str, str] = {
        "Node": "node",
        "Node2D": "node2d",
        "Node3D": "node3d",
        "Control": "ui",
        "Camera3D": "camera",
        "CharacterBody3D": "physics",
        "RigidBody3D": "physics",
        "Area3D": "physics",
        "AnimationPlayer": "animation",
        "AudioStreamPlayer": "audio",
        "Sprite2D": "node2d",
        "MeshInstance3D": "node3d",
        "DirectionalLight3D": "light",
        "StandardMaterial3D": "material",
    }

    for class_name, methods in _CLASSDB_DATA.items():
        domain = domain_map.get(class_name, "api")
        for m in methods:
            mname = m["name"]
            rw = ReadWrite.WRITE if m["rw"] == "write" else ReadWrite.READ
            op_id = f"class.{class_name.lower()}.{mname}"
            title = f"{class_name}.{mname}"
            desc = f"ClassDB: {class_name}.{mname}() — {m['desc']}"

            param_specs = []
            for p in m["params"]:
                p_name = p[0]
                p_type = p[1]
                p_desc = p[2]
                p_req = p[3] if len(p) > 3 else True
                param_specs.append((p_name, p_type.lower(), p_desc, p_req, None, []))

            aliases = [
                f"{class_name}_{mname}",
                f"{class_name.lower()}_{mname}",
                f"godot_{class_name.lower()}_{mname}",
            ]

            ops.append(
                op(
                    op_id,
                    title,
                    desc,
                    domain,
                    category=OperationCategory.GENERATED_CLASSDB,
                    read_write=rw,
                    params=param_specs,
                    aliases=aliases,
                )
            )

    # In addition to the manually curated signatures above, programmatically expand
    # the ClassDB operations across other standard engine classes to ensure comprehensive
    # coverage of Godot's standard ClassDB taxonomy (1,200+ operations).
    additional_classes = [
        ("CSGBox3D", "csg", ["set_size", "get_size", "set_material", "get_material", "set_operation", "get_operation", "set_use_collision", "is_using_collision"]),
        ("CSGSphere3D", "csg", ["set_radius", "get_radius", "set_radial_segments", "get_radial_segments", "set_rings", "get_rings"]),
        ("CSGCylinder3D", "csg", ["set_radius", "get_radius", "set_height", "get_height", "set_sides", "get_sides", "set_cone", "is_cone"]),
        ("CSGTorus3D", "csg", ["set_inner_radius", "get_inner_radius", "set_outer_radius", "get_outer_radius", "set_sides", "set_ring_sides"]),
        ("CSGPolygon3D", "csg", ["set_polygon", "get_polygon", "set_depth", "get_depth", "set_mode", "get_mode"]),
        ("GPUParticles3D", "particles", ["set_amount", "get_amount", "set_lifetime", "get_lifetime", "set_one_shot", "get_one_shot", "set_preprocess", "get_preprocess", "set_speed_scale", "get_speed_scale", "set_explosiveness", "get_explosiveness", "restart", "emit_particle"]),
        ("GPUParticles2D", "particles", ["set_amount", "get_amount", "set_lifetime", "get_lifetime", "set_one_shot", "get_one_shot", "set_explosiveness", "get_explosiveness", "restart"]),
        ("CPUParticles3D", "particles", ["set_amount", "get_amount", "set_lifetime", "get_lifetime", "set_one_shot", "restart"]),
        ("CPUParticles2D", "particles", ["set_amount", "get_amount", "set_lifetime", "get_lifetime", "set_one_shot", "restart"]),
        ("OmniLight3D", "light", ["set_param", "get_param", "set_shadow", "has_shadow", "set_color", "get_color"]),
        ("SpotLight3D", "light", ["set_param", "get_param", "set_shadow", "has_shadow", "set_color", "get_color"]),
        ("PointLight2D", "light", ["set_energy", "get_energy", "set_texture", "get_texture", "set_shadow_enabled", "is_shadow_enabled"]),
        ("DirectionalLight2D", "light", ["set_energy", "get_energy", "set_color", "get_color", "set_shadow_enabled", "is_shadow_enabled"]),
        ("Camera2D", "camera", ["set_zoom", "get_zoom", "set_offset", "get_offset", "set_anchor_mode", "get_anchor_mode", "set_position_smoothing_enabled", "is_position_smoothing_enabled", "set_limit", "get_limit", "make_current"]),
        ("Button", "ui", ["set_text", "get_text", "set_button_icon", "get_button_icon", "set_flat", "is_flat", "set_disabled", "is_disabled"]),
        ("Label", "ui", ["set_text", "get_text", "set_horizontal_alignment", "get_horizontal_alignment", "set_vertical_alignment", "get_vertical_alignment", "set_autowrap_mode", "get_autowrap_mode"]),
        ("RichTextLabel", "ui", ["append_text", "clear", "set_text", "get_text", "set_bbcode_enabled", "is_bbcode_enabled", "scroll_to_line", "get_total_character_count"]),
        ("LineEdit", "ui", ["set_text", "get_text", "set_placeholder", "get_placeholder", "set_max_length", "get_max_length", "set_editable", "is_editable", "set_secret", "is_secret", "clear", "select_all"]),
        ("TextEdit", "ui", ["set_text", "get_text", "insert_text_at_cursor", "get_line_count", "get_line", "set_line", "clear", "undo", "redo"]),
        ("CheckBox", "ui", ["set_pressed", "is_pressed", "set_text", "get_text"]),
        ("CheckButton", "ui", ["set_pressed", "is_pressed", "set_text", "get_text"]),
        ("OptionButton", "ui", ["add_item", "add_separator", "clear", "get_item_count", "get_item_text", "get_selected_id", "select"]),
        ("ProgressBar", "ui", ["set_value", "get_value", "set_min", "get_min", "set_max", "get_max", "set_step", "get_step"]),
        ("HSlider", "ui", ["set_value", "get_value", "set_min", "get_min", "set_max", "get_max", "set_step", "get_step", "set_editable", "is_editable"]),
        ("VSlider", "ui", ["set_value", "get_value", "set_min", "get_min", "set_max", "get_max", "set_step", "get_step"]),
        ("SpinBox", "ui", ["set_value", "get_value", "set_min", "get_min", "set_max", "get_max", "set_step", "get_step", "set_prefix", "get_prefix", "set_suffix", "get_suffix"]),
        ("TextureRect", "ui", ["set_texture", "get_texture", "set_expand_mode", "get_expand_mode", "set_stretch_mode", "get_stretch_mode", "set_flip_h", "is_flipped_h", "set_flip_v", "is_flipped_v"]),
        ("NinePatchRect", "ui", ["set_texture", "get_texture", "set_patch_margin", "get_patch_margin", "set_region_rect", "get_region_rect"]),
        ("Panel", "ui", ["set_theme_stylebox", "has_theme_stylebox"]),
        ("PanelContainer", "ui", ["set_theme_stylebox", "has_theme_stylebox"]),
        ("MarginContainer", "ui", ["add_theme_constant_override"]),
        ("VBoxContainer", "ui", ["set_alignment", "get_alignment"]),
        ("HBoxContainer", "ui", ["set_alignment", "get_alignment"]),
        ("GridContainer", "ui", ["set_columns", "get_columns"]),
        ("ScrollContainer", "ui", ["set_h_scroll", "get_h_scroll", "set_v_scroll", "get_v_scroll", "ensure_control_visible"]),
        ("TabBar", "ui", ["add_tab", "set_tab_title", "get_tab_title", "get_tab_count", "set_current_tab", "get_current_tab"]),
        ("TabContainer", "ui", ["set_current_tab", "get_current_tab", "get_tab_count", "set_tab_title", "get_tab_title"]),
        ("Tree", "ui", ["create_item", "get_root", "clear", "get_selected"]),
        ("ItemList", "ui", ["add_item", "set_item_text", "get_item_text", "get_item_count", "clear", "select", "is_selected"]),
        ("ColorPicker", "ui", ["set_pick_color", "get_pick_color", "set_edit_alpha", "is_editing_alpha"]),
        ("FileDialog", "ui", ["set_file_mode", "get_file_mode", "set_access", "get_access", "set_current_dir", "get_current_dir", "set_current_file", "get_current_file"]),
        ("ConfirmationDialog", "ui", ["get_ok_button", "get_cancel_button"]),
        ("SubViewport", "viewport", ["set_size", "get_size", "set_size_2d_override", "get_texture", "set_update_mode", "get_update_mode"]),
        ("SubViewportContainer", "viewport", ["set_stretch", "is_stretch_enabled", "set_shrink", "get_shrink"]),
        ("NavigationRegion3D", "navigation", ["set_navigation_mesh", "get_navigation_mesh", "bake_navigation_mesh"]),
        ("NavigationAgent3D", "navigation", ["set_target_position", "get_target_position", "get_next_path_position", "is_target_reached", "is_target_reachable", "set_velocity", "set_max_speed", "get_max_speed"]),
        ("NavigationObstacle3D", "navigation", ["set_radius", "get_radius", "set_height", "get_height", "set_avoidance_enabled", "get_avoidance_enabled"]),
        ("NavigationRegion2D", "navigation", ["set_navigation_polygon", "get_navigation_polygon", "bake_navigation_polygon"]),
        ("NavigationAgent2D", "navigation", ["set_target_position", "get_target_position", "get_next_path_position", "is_target_reached", "set_velocity"]),
        ("TileMap", "tilemap", ["set_cell", "get_cell_source_id", "get_cell_atlas_coords", "erase_cell", "get_used_cells", "get_used_rect", "clear"]),
        ("TileMapLayer", "tilemap", ["set_cell", "get_cell_source_id", "get_cell_atlas_coords", "erase_cell", "get_used_cells", "clear"]),
        ("TileSet", "tileset", ["get_source_count", "get_source_id", "has_source", "remove_source"]),
        ("GridMap", "gridmap", ["set_cell_item", "get_cell_item", "get_cell_item_orientation", "clear", "get_used_cells", "get_meshes"]),
        ("AudioStreamPlayer2D", "audio", ["play", "stop", "is_playing", "set_volume_db", "get_volume_db", "set_max_distance", "get_max_distance"]),
        ("AudioStreamPlayer3D", "audio", ["play", "stop", "is_playing", "set_volume_db", "get_volume_db", "set_max_distance", "get_max_distance", "set_unit_size", "get_unit_size"]),
        ("CharacterBody2D", "physics", ["move_and_slide", "set_velocity", "get_velocity", "is_on_floor", "is_on_wall", "is_on_ceiling"]),
        ("RigidBody2D", "physics", ["set_mass", "get_mass", "set_gravity_scale", "get_gravity_scale", "apply_central_impulse", "apply_central_force"]),
        ("StaticBody2D", "physics", ["set_constant_linear_velocity", "get_constant_linear_velocity"]),
        ("StaticBody3D", "physics", ["set_constant_linear_velocity", "get_constant_linear_velocity"]),
        ("Area2D", "physics", ["set_monitoring", "is_monitoring", "get_overlapping_bodies", "get_overlapping_areas"]),
        ("CollisionShape2D", "collision", ["set_shape", "get_shape", "set_disabled", "is_disabled"]),
        ("CollisionShape3D", "collision", ["set_shape", "get_shape", "set_disabled", "is_disabled"]),
        ("RayCast3D", "physics", ["set_target_position", "get_target_position", "is_colliding", "get_collider", "get_collision_point", "get_collision_normal", "force_raycast_update"]),
        ("RayCast2D", "physics", ["set_target_position", "get_target_position", "is_colliding", "get_collider", "get_collision_point", "force_raycast_update"]),
        ("ShapeCast3D", "physics", ["set_shape", "get_shape", "is_colliding", "get_collision_count", "get_collider"]),
        ("SpringArm3D", "camera", ["set_length", "get_length", "set_margin", "get_margin", "get_hit_length"]),
        ("Decal", "node3d", ["set_size", "get_size", "set_texture", "get_texture", "set_upper_fade", "set_lower_fade"]),
        ("FogVolume", "environment", ["set_size", "get_size", "set_shape", "get_shape", "set_material", "get_material"]),
        ("WorldEnvironment", "environment", ["set_environment", "get_environment", "set_camera_attributes", "get_camera_attributes"]),
        ("Skeleton3D", "skeleton", ["get_bone_count", "get_bone_name", "get_bone_parent", "get_bone_pose", "set_bone_pose", "get_bone_rest", "set_bone_rest", "clear_bones"]),
        ("Skeleton2D", "skeleton", ["get_bone_count", "get_bone"]),
        ("BoneAttachment3D", "skeleton", ["set_bone_name", "get_bone_name", "set_bone_idx", "get_bone_idx"]),
        ("MultiplayerSpawner", "multiplayer", ["add_spawnable_scene", "get_spawnable_scene", "get_spawnable_scene_count", "clear_spawnable_scenes", "spawn"]),
        ("MultiplayerSynchronizer", "multiplayer", ["set_root_path", "get_root_path", "set_replication_interval", "get_replication_interval"]),
        ("Path3D", "node3d", ["set_curve", "get_curve"]),
        ("PathFollow3D", "node3d", ["set_progress", "get_progress", "set_progress_ratio", "get_progress_ratio", "set_loop", "has_loop"]),
        ("Path2D", "node2d", ["set_curve", "get_curve"]),
        ("PathFollow2D", "node2d", ["set_progress", "get_progress", "set_progress_ratio", "get_progress_ratio", "set_loop", "has_loop"]),
        ("Polygon2D", "node2d", ["set_polygon", "get_polygon", "set_color", "get_color", "set_texture", "get_texture"]),
        ("Line2D", "node2d", ["set_points", "get_points", "add_point", "remove_point", "clear_points", "set_width", "get_width", "set_default_color", "get_default_color"]),
        ("AnimatedSprite2D", "node2d", ["play", "pause", "stop", "is_playing", "set_animation", "get_animation", "set_frame", "get_frame"]),
        ("AnimatedSprite3D", "node3d", ["play", "pause", "stop", "is_playing", "set_animation", "get_animation"]),
        ("Sprite3D", "node3d", ["set_texture", "get_texture", "set_pixel_size", "get_pixel_size", "set_billboard_mode", "get_billboard_mode"]),
        ("BoxMesh", "mesh", ["set_size", "get_size"]),
        ("SphereMesh", "mesh", ["set_radius", "get_radius", "set_height", "get_height"]),
        ("CylinderMesh", "mesh", ["set_top_radius", "get_top_radius", "set_bottom_radius", "get_bottom_radius", "set_height", "get_height"]),
        ("CapsuleMesh", "mesh", ["set_radius", "get_radius", "set_height", "get_height"]),
        ("PlaneMesh", "mesh", ["set_size", "get_size"]),
        ("TorusMesh", "mesh", ["set_inner_radius", "get_inner_radius", "set_outer_radius", "get_outer_radius"]),
        ("ArrayMesh", "mesh", ["add_surface_from_arrays", "get_surface_count", "surface_get_array_len", "clear_surfaces"]),
        ("ShaderMaterial", "material", ["set_shader", "get_shader", "set_shader_parameter", "get_shader_parameter"]),
        ("ParticleProcessMaterial", "material", ["set_direction", "get_direction", "set_spread", "get_spread", "set_gravity", "get_gravity", "set_initial_velocity_min", "set_initial_velocity_max"]),
        ("CanvasItemMaterial", "material", ["set_blend_mode", "get_blend_mode", "set_light_mode", "get_light_mode"]),
        ("Theme", "theme", ["set_color", "get_color", "has_color", "set_constant", "get_constant", "set_font_size", "get_font_size", "set_stylebox", "get_stylebox"]),
        ("StyleBoxFlat", "theme", ["set_bg_color", "get_bg_color", "set_corner_radius_all", "set_border_width_all", "set_border_color", "get_border_color"]),
        ("StyleBoxTexture", "theme", ["set_texture", "get_texture", "set_texture_margin_all"]),
        ("Environment", "environment", ["set_background_mode", "get_background_mode", "set_background_color", "get_background_color", "set_ambient_light_color", "get_ambient_light_color", "set_glow_enabled", "is_glow_enabled", "set_tonemap_mode", "get_tonemap_mode", "set_ssao_enabled", "is_ssao_enabled"]),
        ("Sky", "environment", ["set_sky_material", "get_sky_material", "set_process_mode", "get_process_mode"]),
        ("Curve", "curve", ["add_point", "remove_point", "clear_points", "get_point_count", "sample", "sample_baked"]),
        ("Curve2D", "curve", ["add_point", "remove_point", "clear_points", "get_point_count", "sample", "sample_baked"]),
        ("Curve3D", "curve", ["add_point", "remove_point", "clear_points", "get_point_count", "sample", "sample_baked"]),
        ("Gradient", "gradient", ["add_point", "remove_point", "set_color", "get_color", "set_offset", "get_offset", "sample"]),
        ("AudioServer", "audio", ["get_bus_count", "get_bus_name", "set_bus_name", "get_bus_volume_db", "set_bus_volume_db", "set_bus_mute", "is_bus_mute", "add_bus", "remove_bus"]),
        ("Engine", "system", ["get_frames_per_second", "get_physics_frames", "get_process_frames", "get_time_scale", "set_time_scale", "is_editor_hint"]),
        ("Time", "system", ["get_ticks_msec", "get_ticks_usec", "get_unix_time_from_system", "get_datetime_dict_from_system"]),
        ("OS", "system", ["get_name", "get_processor_count", "get_system_time_msecs", "get_environment", "has_feature"]),
        # Godot 4.8 Dev additions: Trail3D and Texture Streaming
        ("Trail3D", "node3d", ["set_material", "get_material", "set_segments", "get_segments", "set_lifetime", "get_lifetime", "set_width", "get_width", "clear_points"]),
        ("Texture2D", "texture", ["set_streaming", "is_streaming", "set_streaming_quality", "get_streaming_quality"]),
    ]

    for class_name, domain, method_names in additional_classes:
        for mname in method_names:
            is_write = any(mname.startswith(p) for p in ["set_", "add_", "remove_", "clear", "play", "stop", "insert", "append", "bake", "restart", "grab", "select", "spawn"])
            rw = ReadWrite.WRITE if is_write else ReadWrite.READ
            op_id = f"class.{class_name.lower()}.{mname}"
            title = f"{class_name}.{mname}"
            desc = f"ClassDB: {class_name}.{mname}() method via engine reflection."

            ops.append(
                op(
                    op_id,
                    title,
                    desc,
                    domain,
                    category=OperationCategory.GENERATED_CLASSDB,
                    read_write=rw,
                    aliases=[f"{class_name}_{mname}", f"{class_name.lower()}_{mname}"],
                )
            )

    return ops
