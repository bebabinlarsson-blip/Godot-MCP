"""Curated Graphics Operations (2D, 3D, Transforms, Shaders, Materials, Lighting, Environment, Cameras, Particles, Meshes)."""

from __future__ import annotations

from godot_omni.operations.builder import op
from godot_omni.registry.models import (
    CanonicalOperation,
    LatencyTier,
    ReadWrite,
)


def get_curated_graphics_operations() -> list[CanonicalOperation]:
    ops: list[CanonicalOperation] = [
        # --- 2D & 3D TRANSFORMS ---
        op(
            "transform.get",
            "Get Node Transform (2D/3D)",
            "Get position, rotation, and scale in local and global space for Node2D or Node3D.",
            "transform",
            read_write=ReadWrite.READ,
            params=[("path", "string", "Node path in scene", True, None, [])],
            aliases=["get_transform", "transform_get"],
        ),
        op(
            "transform.set_position",
            "Set Node Position",
            "Set local position of a Node2D (Vector2) or Node3D (Vector3).",
            "transform",
            read_write=ReadWrite.WRITE,
            params=[
                ("path", "string", "Node path", True, None, []),
                ("position", "array", "Position coordinates [x, y] or [x, y, z]", True, None, []),
                ("global_space", "boolean", "Apply as global position", False, False, []),
            ],
            aliases=["set_position", "transform_set_position"],
        ),
        op(
            "transform.set_rotation",
            "Set Node Rotation",
            "Set rotation in radians or degrees (Euler angles for 3D, scalar angle for 2D).",
            "transform",
            read_write=ReadWrite.WRITE,
            params=[
                ("path", "string", "Node path", True, None, []),
                ("rotation", "any", "Rotation value (scalar angle for 2D, [pitch, yaw, roll] for 3D)", True, None, []),
                ("degrees", "boolean", "True if angles are given in degrees, false for radians", False, True, []),
            ],
            aliases=["set_rotation", "transform_set_rotation"],
        ),
        op(
            "transform.set_scale",
            "Set Node Scale",
            "Set local scale of a Node2D or Node3D.",
            "transform",
            read_write=ReadWrite.WRITE,
            params=[
                ("path", "string", "Node path", True, None, []),
                ("scale", "array", "Scale factors [x, y] or [x, y, z]", True, None, []),
            ],
            aliases=["set_scale", "transform_set_scale"],
        ),
        op(
            "transform.look_at",
            "Orient Node Toward Target",
            "Point a Node3D or Node2D toward a target world position.",
            "transform",
            read_write=ReadWrite.WRITE,
            params=[
                ("path", "string", "Node path", True, None, []),
                ("target_position", "array", "World coordinates [x, y, z] or [x, y] to look at", True, None, []),
                ("up_vector", "array", "Up orientation for 3D [x, y, z]", False, [0, 1, 0], []),
            ],
            aliases=["look_at", "transform_look_at"],
        ),
        op(
            "transform.snap_to_grid",
            "Snap Node to Grid",
            "Snap node coordinates to a spatial grid step.",
            "transform",
            read_write=ReadWrite.WRITE,
            params=[
                ("path", "string", "Node path", True, None, []),
                ("grid_size", "number", "Grid snapping increment (e.g. 1.0 or 0.5)", False, 1.0, []),
            ],
            aliases=["snap_to_grid", "transform_snap_to_grid"],
        ),

        # --- 2D NODES ---
        op(
            "2d.sprite.create",
            "Create Sprite2D with Texture",
            "Create a Sprite2D node and optionally assign a texture resource.",
            "node2d",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("name", "string", "Node name", False, "Sprite2D", []),
                ("texture_path", "string", "res:// path to texture image", False, "", []),
                ("position", "array", "Initial position [x, y]", False, [0, 0], []),
            ],
            aliases=["create_sprite_2d", "sprite2d_create"],
        ),
        op(
            "2d.sprite.set_region",
            "Set Sprite2D Texture Region",
            "Configure texture region rect and enable region mode on a Sprite2D.",
            "node2d",
            read_write=ReadWrite.WRITE,
            params=[
                ("path", "string", "Sprite2D node path", True, None, []),
                ("region_rect", "array", "[x, y, width, height] region", True, None, []),
            ],
            aliases=["set_sprite_region", "sprite2d_set_region"],
        ),
        op(
            "2d.polygon.create",
            "Create Polygon2D Node",
            "Create a Polygon2D with specified vertex points and fill color.",
            "node2d",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("polygon_points", "array", "List of [x, y] coordinates forming the polygon", True, None, []),
                ("color", "string", "Hex fill color string (e.g. #ff0000)", False, "#ffffff", []),
            ],
            aliases=["create_polygon_2d", "polygon2d_create"],
        ),
        op(
            "2d.line.create",
            "Create Line2D Node",
            "Create a Line2D with vertex points, width, and color.",
            "node2d",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("points", "array", "List of [x, y] coordinates", True, None, []),
                ("width", "number", "Line width in pixels", False, 10.0, []),
                ("default_color", "string", "Line color hex string", False, "#ffffff", []),
            ],
            aliases=["create_line_2d", "line2d_create"],
        ),

        # --- 3D MESHES & NODES ---
        op(
            "3d.mesh.create_primitive",
            "Create MeshInstance3D with Primitive",
            "Add a MeshInstance3D with a primitive mesh (Box, Sphere, Cylinder, Plane, Capsule).",
            "node3d",
            read_write=ReadWrite.WRITE,
            params=[
                ("primitive_type", "string", "Primitive shape", True, "BoxMesh", ["BoxMesh", "SphereMesh", "CylinderMesh", "PlaneMesh", "CapsuleMesh", "TorusMesh"]),
                ("parent_path", "string", "Parent node path", False, "", []),
                ("name", "string", "Node name", False, "MeshInstance3D", []),
                ("size", "array", "Dimensions [x, y, z] for box/plane or radius/height", False, None, []),
            ],
            aliases=["create_primitive_3d", "mesh_create_primitive"],
        ),
        op(
            "3d.mesh.assign_material",
            "Assign Material Override to MeshInstance3D",
            "Set material_override on a MeshInstance3D node.",
            "node3d",
            read_write=ReadWrite.WRITE,
            params=[
                ("path", "string", "MeshInstance3D node path", True, None, []),
                ("material_path", "string", "res:// path to Material resource", True, None, []),
            ],
            aliases=["assign_mesh_material", "mesh_assign_material"],
        ),
        op(
            "3d.decal.create",
            "Create Decal Node",
            "Add a 3D Decal projector with albedo and normal textures.",
            "node3d",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("size", "array", "Decal bounding box [x, y, z]", False, [2, 2, 2], []),
                ("texture_albedo", "string", "res:// path to albedo texture", False, "", []),
            ],
            aliases=["create_decal", "decal_create"],
        ),

        # --- MATERIALS ---
        op(
            "material.create_standard",
            "Create StandardMaterial3D Resource",
            "Create and save a new StandardMaterial3D resource with PBR properties.",
            "material",
            read_write=ReadWrite.WRITE,
            latency_tier=LatencyTier.DISK,
            params=[
                ("path", "string", "res:// destination path", True, None, []),
                ("albedo_color", "string", "Albedo hex color (#ffffff)", False, "#ffffff", []),
                ("metallic", "number", "Metallic factor (0.0 to 1.0)", False, 0.0, []),
                ("roughness", "number", "Roughness factor (0.0 to 1.0)", False, 0.5, []),
                ("emission_enabled", "boolean", "Enable emission", False, False, []),
                ("emission_color", "string", "Emission hex color", False, "#000000", []),
            ],
            aliases=["create_standard_material", "material_create_standard"],
        ),
        op(
            "material.set_emission",
            "Configure Material Emission / Glow",
            "Enable and tune emission energy and color on a StandardMaterial3D.",
            "material",
            read_write=ReadWrite.WRITE,
            latency_tier=LatencyTier.DISK,
            params=[
                ("material_path", "string", "res:// path to Material resource", True, None, []),
                ("enabled", "boolean", "Enable emission", False, True, []),
                ("color", "string", "Emission color hex string", False, "#ffffff", []),
                ("energy_multiplier", "number", "Emission energy intensity multiplier", False, 2.0, []),
            ],
            aliases=["set_material_emission", "material_set_emission"],
        ),

        # --- SHADERS ---
        op(
            "shader.create",
            "Create Godot Shader Resource",
            "Create a new .gdshader file with specified shader type and template.",
            "shader",
            read_write=ReadWrite.WRITE,
            latency_tier=LatencyTier.DISK,
            params=[
                ("path", "string", "res:// path to .gdshader file", True, None, []),
                ("shader_type", "string", "Shader domain type", False, "spatial", ["spatial", "canvas_item", "particles", "sky", "fog"]),
                ("code", "string", "Shader source code (if empty, template is used)", False, "", []),
            ],
            aliases=["create_shader", "shader_create"],
        ),
        op(
            "shader.set_parameter",
            "Set Shader Material Uniform Parameter",
            "Set a uniform parameter value on a ShaderMaterial resource.",
            "shader",
            read_write=ReadWrite.WRITE,
            params=[
                ("material_path", "string", "res:// path to ShaderMaterial", True, None, []),
                ("parameter_name", "string", "Name of the uniform parameter", True, None, []),
                ("value", "any", "Parameter value to assign", True, None, []),
            ],
            aliases=["set_shader_parameter", "shader_set_parameter"],
        ),

        # --- CAMERAS ---
        op(
            "camera.create_3d",
            "Create Camera3D Node",
            "Add a Camera3D node to the scene and optionally set as active camera.",
            "camera",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("name", "string", "Node name", False, "Camera3D", []),
                ("fov", "number", "Field of view in degrees", False, 75.0, []),
                ("make_current", "boolean", "Activate camera as current view", False, True, []),
            ],
            aliases=["create_camera_3d", "camera_create_3d"],
        ),
        op(
            "camera.create_2d",
            "Create Camera2D Node",
            "Add a Camera2D node with zoom and position smoothing.",
            "camera",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("name", "string", "Node name", False, "Camera2D", []),
                ("zoom", "array", "Zoom factor [x, y]", False, [1.0, 1.0], []),
                ("position_smoothing_enabled", "boolean", "Enable smooth follow", False, True, []),
            ],
            aliases=["create_camera_2d", "camera_create_2d"],
        ),

        # --- LIGHTING ---
        op(
            "light.create_directional_3d",
            "Create DirectionalLight3D",
            "Create a sun light source with shadow mapping.",
            "light",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("name", "string", "Node name", False, "DirectionalLight3D", []),
                ("shadow_enabled", "boolean", "Enable shadow rendering", False, True, []),
                ("light_energy", "number", "Intensity factor", False, 1.0, []),
                ("light_color", "string", "Color hex (#ffffff)", False, "#ffffff", []),
            ],
            aliases=["create_directional_light", "light_create_directional"],
        ),
        op(
            "light.create_omni_3d",
            "Create OmniLight3D (Point Light)",
            "Create an omnidirectional point light with radius attenuation.",
            "light",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("omni_range", "number", "Light reach distance in meters", False, 10.0, []),
                ("light_energy", "number", "Light intensity", False, 1.5, []),
                ("light_color", "string", "Color hex", False, "#ffffff", []),
            ],
            aliases=["create_omni_light", "light_create_omni"],
        ),

        # --- ENVIRONMENT ---
        op(
            "environment.configure_world",
            "Configure WorldEnvironment & Post-Processing",
            "Create or configure WorldEnvironment with glow, tonemapping, SSAO, and fog.",
            "environment",
            read_write=ReadWrite.WRITE,
            params=[
                ("glow_enabled", "boolean", "Enable HDR bloom/glow", False, True, []),
                ("glow_intensity", "number", "Glow intensity", False, 1.0, []),
                ("ssao_enabled", "boolean", "Screen-space ambient occlusion", False, True, []),
                ("fog_enabled", "boolean", "Distance fog", False, False, []),
                ("volumetric_fog_enabled", "boolean", "Enable 3D volumetric fog", False, False, []),
            ],
            aliases=["configure_world_environment", "environment_configure_world"],
        ),

        # --- PARTICLES ---
        op(
            "particle.create_gpu_3d",
            "Create GPUParticles3D Emitter",
            "Create a 3D GPU particle emitter with ParticleProcessMaterial.",
            "particle",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("amount", "integer", "Total particle count", False, 64, []),
                ("lifetime", "number", "Lifetime in seconds", False, 1.5, []),
                ("explosiveness", "number", "Emission burst factor (0.0 to 1.0)", False, 0.0, []),
            ],
            aliases=["create_gpu_particles_3d", "particle_create_gpu_3d"],
        ),
        op(
            "particle.create_gpu_2d",
            "Create GPUParticles2D Emitter",
            "Create a 2D GPU particle emitter with ParticleProcessMaterial.",
            "particle",
            read_write=ReadWrite.WRITE,
            params=[
                ("parent_path", "string", "Parent node path", False, "", []),
                ("amount", "integer", "Total particle count", False, 32, []),
                ("lifetime", "number", "Lifetime in seconds", False, 1.0, []),
            ],
            aliases=["create_gpu_particles_2d", "particle_create_gpu_2d"],
        ),

        # --- MATERIALS (EXTENDED) ---
        op("material.create_orm", "Create ORMMaterial3D", "Create ORM material (Occlusion, Roughness, Metallic channel-packed).", "material", read_write=ReadWrite.WRITE, latency_tier=LatencyTier.DISK, params=[("path", "string", "res:// path", True, None, [])]),
        op("material.create_shader", "Create ShaderMaterial", "Create ShaderMaterial assigned to a .gdshader file.", "material", read_write=ReadWrite.WRITE, latency_tier=LatencyTier.DISK, params=[("path", "string", "res:// path", True, None, []), ("shader_path", "string", "res:// shader path", True, None, [])]),
        op("material.set_albedo_texture", "Set Material Albedo Texture", "Assign albedo texture to a material.", "material", read_write=ReadWrite.WRITE, params=[("material_path", "string", "res:// path", True, None, []), ("texture_path", "string", "res:// texture path", True, None, [])]),
        op("material.set_normal_texture", "Set Material Normal Map", "Assign normal map texture and enable normal mapping.", "material", read_write=ReadWrite.WRITE, params=[("material_path", "string", "res:// path", True, None, []), ("texture_path", "string", "res:// normal texture", True, None, []), ("scale", "number", "Normal map scale factor", False, 1.0, [])]),
        op("material.set_roughness_texture", "Set Material Roughness Texture", "Assign roughness map texture.", "material", read_write=ReadWrite.WRITE, params=[("material_path", "string", "res:// path", True, None, []), ("texture_path", "string", "res:// texture", True, None, [])]),
        op("material.set_metallic_texture", "Set Material Metallic Texture", "Assign metallic map texture.", "material", read_write=ReadWrite.WRITE, params=[("material_path", "string", "res:// path", True, None, []), ("texture_path", "string", "res:// texture", True, None, [])]),
        op("material.set_triplanar", "Enable Triplanar UV Mapping", "Enable triplanar texturing on material for terrain or organic meshes.", "material", read_write=ReadWrite.WRITE, params=[("material_path", "string", "res:// path", True, None, []), ("enabled", "boolean", "Enable triplanar", False, True, [])]),
        op("material.set_cull_mode", "Set Material Cull Mode", "Set face culling mode (Back, Front, Disabled/Double-sided).", "material", read_write=ReadWrite.WRITE, params=[("material_path", "string", "res:// path", True, None, []), ("cull_mode", "string", "Cull mode", True, "back", ["back", "front", "disabled"])]),
        op("material.set_transparency", "Set Material Transparency", "Configure transparency mode (Alpha, Alpha Scissor, Depth Prepass).", "material", read_write=ReadWrite.WRITE, params=[("material_path", "string", "res:// path", True, None, []), ("mode", "string", "Transparency mode", True, "alpha", ["disabled", "alpha", "alpha_scissor", "alpha_hash"])]),

        # --- SHADERS (EXTENDED) ---
        op("shader.get_code", "Get Shader Source Code", "Read source text of a .gdshader file.", "shader", read_write=ReadWrite.READ, params=[("path", "string", "res:// path", True, None, [])]),
        op("shader.set_code", "Set Shader Source Code", "Write source text to a .gdshader file.", "shader", read_write=ReadWrite.WRITE, latency_tier=LatencyTier.DISK, params=[("path", "string", "res:// path", True, None, []), ("code", "string", "Shader code", True, None, [])]),
        op("shader.list_uniforms", "List Shader Uniform Parameters", "Parse and list uniform parameters declared in a shader.", "shader", read_write=ReadWrite.READ, params=[("path", "string", "res:// path", True, None, [])]),
        op("shader.template.spatial", "Generate Spatial PBR Shader Template", "Create a 3D spatial shader with vertex and fragment stages.", "shader", read_write=ReadWrite.WRITE, latency_tier=LatencyTier.DISK, params=[("path", "string", "res:// path", True, None, [])]),
        op("shader.template.canvas", "Generate 2D Canvas Shader Template", "Create a 2D canvas_item shader for UI or 2D sprites.", "shader", read_write=ReadWrite.WRITE, latency_tier=LatencyTier.DISK, params=[("path", "string", "res:// path", True, None, [])]),
        op("shader.template.particles", "Generate Particle Shader Template", "Create custom particle process shader.", "shader", read_write=ReadWrite.WRITE, latency_tier=LatencyTier.DISK, params=[("path", "string", "res:// path", True, None, [])]),

        # --- 3D MESHES & LIGHTING ---
        op("3d.mesh.create_trimesh_collision", "Generate Triangle Collision from Mesh", "Create a ConcavePolygonShape3D static collision sibling from mesh vertices.", "node3d", read_write=ReadWrite.WRITE, params=[("mesh_path", "string", "MeshInstance3D node path", True, None, [])]),
        op("3d.mesh.create_convex_collision", "Generate Convex Collision from Mesh", "Create a ConvexPolygonShape3D collision sibling from mesh hull.", "node3d", read_write=ReadWrite.WRITE, params=[("mesh_path", "string", "MeshInstance3D node path", True, None, [])]),
        op("3d.mesh.set_cast_shadows", "Set Shadow Casting on Mesh", "Configure mesh shadow casting (On, Off, Double-Sided, Shadows-Only).", "node3d", read_write=ReadWrite.WRITE, params=[("mesh_path", "string", "MeshInstance3D node path", True, None, []), ("setting", "string", "Shadow mode", True, "on", ["on", "off", "double_sided", "shadows_only"])]),
        op("3d.multimesh.create", "Create MultiMeshInstance3D", "Add MultiMeshInstance3D for GPU batch rendering of thousands of meshes.", "node3d", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent node path", False, "", []), ("mesh_path", "string", "res:// path to Mesh", True, None, []), ("instance_count", "integer", "Capacity count", False, 100, [])]),
        op("3d.fog_volume.create", "Create 3D Fog Volume", "Add a localized FogVolume with density and emission color.", "environment", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent node path", False, "", []), ("size", "array", "Dimensions [x, y, z]", False, [4, 4, 4], []), ("density", "number", "Fog density", False, 0.5, [])]),
        op("3d.reflection_probe.create", "Create ReflectionProbe Node", "Add a ReflectionProbe for local environment reflections.", "light", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent node path", False, "", []), ("size", "array", "Probe extents [x, y, z]", False, [20, 20, 20], []), ("box_projection", "boolean", "Enable box projection", False, True, [])]),
        op("3d.voxel_gi.create", "Create VoxelGI Node", "Add VoxelGI node for real-time global illumination.", "light", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent node path", False, "", []), ("size", "array", "Extents [x, y, z]", False, [20, 20, 20], [])]),
        op("light.create_spot_3d", "Create SpotLight3D", "Create a focused cone spotlight.", "light", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent node path", False, "", []), ("spot_range", "number", "Range in meters", False, 15.0, []), ("spot_angle", "number", "Cone angle in degrees", False, 45.0, [])]),
        op("light.create_point_2d", "Create PointLight2D", "Create 2D point light emitter.", "light", read_write=ReadWrite.WRITE, params=[("parent_path", "string", "Parent node path", False, "", []), ("texture_path", "string", "res:// light mask texture", False, "", [])]),
        op("light.set_shadow_bias", "Tune Shadow Bias", "Set shadow bias and normal bias to eliminate shadow acne.", "light", read_write=ReadWrite.WRITE, params=[("light_path", "string", "Light node path", True, None, []), ("bias", "number", "Shadow bias", False, 0.1, [])]),

        # --- CAMERAS & POST-PROCESSING ---
        op("camera.set_dof_blur", "Configure Depth-of-Field Blur", "Tune Camera3D cinematic depth of field distance and blur amount.", "camera", read_write=ReadWrite.WRITE, params=[("camera_path", "string", "Camera3D node path", True, None, []), ("far_distance", "number", "Blur start distance", False, 10.0, []), ("far_transition", "number", "Transition falloff", False, 5.0, [])]),
        op("camera.shake.add_trauma", "Add Camera Screen Shake", "Trigger screen shake impulse on an active camera shake rig.", "camera", read_write=ReadWrite.WRITE, params=[("amount", "number", "Shake trauma (0.0 to 1.0)", False, 0.5, [])]),

        # --- ENVIRONMENT & POST-PROCESSING ---
        op("environment.set_ambient_light", "Configure Ambient Light", "Set ambient sky/color illumination.", "environment", read_write=ReadWrite.WRITE, params=[("color", "string", "Ambient color hex (#404040)", False, "#404040", []), ("energy", "number", "Ambient energy factor", False, 1.0, [])]),
        op("environment.set_ssao", "Configure Screen-Space Ambient Occlusion", "Tune SSAO radius, intensity, and power.", "environment", read_write=ReadWrite.WRITE, params=[("enabled", "boolean", "Enable SSAO", False, True, []), ("radius", "number", "Sampling radius", False, 1.0, []), ("intensity", "number", "Occlusion darkness", False, 2.0, [])]),
        op("environment.set_sdfgi", "Configure Signed Distance Field GI", "Enable and tune real-time SDFGI global illumination.", "environment", read_write=ReadWrite.WRITE, params=[("enabled", "boolean", "Enable SDFGI", False, True, []), ("cascades", "integer", "Number of cascades", False, 4, [])]),
        op("environment.set_sky", "Configure Procedural Sky", "Assign procedural sky material with sun azimuth and elevation.", "environment", read_write=ReadWrite.WRITE, params=[("sky_top_color", "string", "Zenith color", False, "#385e9f", []), ("sky_horizon_color", "string", "Horizon color", False, "#a4b5d0", [])]),

        # --- IMAGES & TEXTURES ---
        op("image.create", "Create Empty Image", "Create a blank Image resource with dimensions and format.", "image", read_write=ReadWrite.WRITE, params=[("width", "integer", "Image width", True, 256, []), ("height", "integer", "Image height", True, 256, []), ("format", "string", "Color format", False, "rgba8", ["rgba8", "rgb8", "rf", "r8"])]),
        op("image.save_png", "Save Image to PNG File", "Save an Image to a .png file on disk.", "image", read_write=ReadWrite.WRITE, latency_tier=LatencyTier.DISK, params=[("path", "string", "res:// output path", True, None, []), ("image_path", "string", "Source image path or handle", True, None, [])]),
        op("image.fill_color", "Fill Image with Color", "Fill an entire Image buffer with a single solid color.", "image", read_write=ReadWrite.WRITE, params=[("path", "string", "res:// image path", True, None, []), ("color", "string", "Hex fill color", True, "#ffffff", [])]),
        op("image.set_pixel", "Set Image Pixel Color", "Set color of a single pixel at (x, y) coordinates.", "image", read_write=ReadWrite.WRITE, params=[("path", "string", "res:// image path", True, None, []), ("x", "integer", "X coordinate", True, 0, []), ("y", "integer", "Y coordinate", True, 0, []), ("color", "string", "Hex color", True, "#ffffff", [])]),
        op("image.resize", "Resize Image", "Scale an Image to new dimensions with interpolation filter.", "image", read_write=ReadWrite.WRITE, params=[("path", "string", "res:// image path", True, None, []), ("width", "integer", "Target width", True, None, []), ("height", "integer", "Target height", True, None, []), ("interpolation", "string", "Filter", False, "bilinear", ["bilinear", "nearest", "bicubic"])]),
        op("texture.create_atlas_region", "Create AtlasTexture Region", "Create an AtlasTexture slicing a sub-rect from a sprite sheet.", "image", read_write=ReadWrite.WRITE, latency_tier=LatencyTier.DISK, params=[("path", "string", "res:// destination path", True, None, []), ("atlas_path", "string", "res:// sheet texture path", True, None, []), ("region", "array", "[x, y, width, height]", True, None, [])]),
        op("texture.create_noise", "Create FastNoiseTexture2D", "Generate a procedural Simplex/Perlin noise texture.", "image", read_write=ReadWrite.WRITE, latency_tier=LatencyTier.DISK, params=[("path", "string", "res:// path", True, None, []), ("width", "integer", "Width", False, 512, []), ("height", "integer", "Height", False, 512, []), ("frequency", "number", "Noise frequency", False, 0.05, [])]),

        # --- CURVES & GRADIENTS ---
        op("curve.create", "Create Curve Resource", "Create a Curve (.tres) for falloff, animation easing, or particle ramps.", "curve", read_write=ReadWrite.WRITE, latency_tier=LatencyTier.DISK, params=[("path", "string", "res:// path", True, None, [])]),
        op("curve.add_point", "Add Point to Curve", "Insert a control point with left/right tangents into a Curve.", "curve", read_write=ReadWrite.WRITE, params=[("path", "string", "res:// Curve path", True, None, []), ("position", "array", "Coordinates [x, y]", True, None, []), ("left_tangent", "number", "Left slope tangent", False, 0.0, []), ("right_tangent", "number", "Right slope tangent", False, 0.0, [])]),
        op("curve.sample", "Sample Value from Curve", "Evaluate a Curve at offset X (0.0 to 1.0).", "curve", read_write=ReadWrite.READ, params=[("path", "string", "res:// Curve path", True, None, []), ("offset", "number", "Offset X", True, 0.5, [])]),
        op("gradient.create", "Create Gradient Resource", "Create a Gradient (.tres) resource.", "gradient", read_write=ReadWrite.WRITE, latency_tier=LatencyTier.DISK, params=[("path", "string", "res:// path", True, None, [])]),
        op("gradient.add_color_stop", "Add Color Stop to Gradient", "Insert a color stop at an offset in a Gradient.", "gradient", read_write=ReadWrite.WRITE, params=[("path", "string", "res:// Gradient path", True, None, []), ("offset", "number", "Offset (0.0 to 1.0)", True, None, []), ("color", "string", "Hex color", True, None, [])]),

        # --- SKELETONS & BONES ---
        op("skeleton.list_bones", "List Bones in Skeleton3D", "List all bone names, indices, and rest transforms in a Skeleton3D.", "skeleton", read_write=ReadWrite.READ, params=[("skeleton_path", "string", "Skeleton3D node path", True, None, [])]),
        op("skeleton.get_bone_pose", "Get Bone Pose Transform", "Read current local or global pose transform of a bone.", "skeleton", read_write=ReadWrite.READ, params=[("skeleton_path", "string", "Skeleton3D node path", True, None, []), ("bone_name", "string", "Name of bone", True, None, [])]),
        op("skeleton.set_bone_pose", "Set Bone Pose Transform", "Set pose position/rotation on a bone in Skeleton3D.", "skeleton", read_write=ReadWrite.WRITE, params=[("skeleton_path", "string", "Skeleton3D node path", True, None, []), ("bone_name", "string", "Name of bone", True, None, []), ("position", "array", "Optional position [x, y, z]", False, None, []), ("rotation", "array", "Optional quaternion [x, y, z, w]", False, None, [])]),
        op("skeleton.reset_pose", "Reset Skeleton to Rest Pose", "Revert all bone poses to their rest positions.", "skeleton", read_write=ReadWrite.WRITE, params=[("skeleton_path", "string", "Skeleton3D node path", True, None, [])]),
    ]
    return ops
