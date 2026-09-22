@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles SurfaceTool procedural mesh synthesis, MeshDataTool deformation,
## and PrimitiveMesh generation.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func _get_scene_root() -> Node:
	if Engine.is_editor_hint():
		var tree := Engine.get_main_loop() as SceneTree
		if tree != null and Engine.has_singleton("EditorInterface"):
			var editor_interface := Engine.get_singleton("EditorInterface")
			if editor_interface.has_method("get_edited_scene_root"):
				var root: Node = editor_interface.get_edited_scene_root()
				if root != null:
					return root
		if tree != null and tree.edited_scene_root != null:
			return tree.edited_scene_root
		if tree != null and tree.current_scene != null:
			return tree.current_scene
		if tree != null and tree.root != null:
			return tree.root
	return null


func _resolve_node(scene_root: Node, node_path: String) -> Node:
	if node_path.is_empty():
		return scene_root
	return scene_root.get_node_or_null(NodePath(node_path))


func generate_surface_mesh(params: Dictionary) -> Dictionary:
	var st := SurfaceTool.new()
	var prim_type_str: String = params.get("primitive_type", "TRIANGLES").to_upper()
	var prim_type := Mesh.PRIMITIVE_TRIANGLES
	match prim_type_str:
		"LINES":
			prim_type = Mesh.PRIMITIVE_LINES
		"LINE_STRIP":
			prim_type = Mesh.PRIMITIVE_LINE_STRIP
		"POINTS":
			prim_type = Mesh.PRIMITIVE_POINTS
		"TRIANGLE_STRIP":
			prim_type = Mesh.PRIMITIVE_TRIANGLE_STRIP
		_:
			prim_type = Mesh.PRIMITIVE_TRIANGLES

	st.begin(prim_type)

	var vertices: Array = params.get("vertices", [])
	var normals: Array = params.get("normals", [])
	var uvs: Array = params.get("uvs", [])
	var colors: Array = params.get("colors", [])
	var indices: Array = params.get("indices", [])

	for i in range(vertices.size()):
		var v_raw = vertices[i]
		var v := Vector3.ZERO
		if v_raw is Array and v_raw.size() >= 3:
			v = Vector3(float(v_raw[0]), float(v_raw[1]), float(v_raw[2]))

		if i < normals.size():
			var n_raw = normals[i]
			if n_raw is Array and n_raw.size() >= 3:
				st.set_normal(Vector3(float(n_raw[0]), float(n_raw[1]), float(n_raw[2])))

		if i < uvs.size():
			var uv_raw = uvs[i]
			if uv_raw is Array and uv_raw.size() >= 2:
				st.set_uv(Vector2(float(uv_raw[0]), float(uv_raw[1])))

		if i < colors.size():
			var c_raw = colors[i]
			if c_raw is Array and c_raw.size() >= 4:
				st.set_color(Color(float(c_raw[0]), float(c_raw[1]), float(c_raw[2]), float(c_raw[3])))

		st.add_vertex(v)

	for idx in indices:
		st.add_index(int(idx))

	var gen_normals: bool = params.get("generate_normals", false)
	if gen_normals and normals.is_empty():
		st.generate_normals()

	var gen_tangents: bool = params.get("generate_tangents", false)
	if gen_tangents:
		st.generate_tangents()

	var mesh: ArrayMesh = st.commit()
	var save_path: String = params.get("save_path", "")
	var saved := false
	if not save_path.is_empty():
		if not save_path.begins_with("res://"):
			save_path = "res://" + save_path
		var err := ResourceSaver.save(mesh, save_path)
		if err == OK:
			saved = true

	var attach_to: String = params.get("attach_to", "")
	var attached := false
	var scene_root := _get_scene_root()
	if not attach_to.is_empty() and scene_root != null:
		var target := _resolve_node(scene_root, attach_to)
		if target != null:
			var mi := MeshInstance3D.new()
			mi.name = "MeshInstance3D"
			mi.mesh = mesh
			target.add_child(mi)
			mi.owner = scene_root
			attached = true

	return {
		"success": true,
		"vertex_count": vertices.size(),
		"surface_count": mesh.get_surface_count(),
		"saved": saved,
		"save_path": save_path if saved else "",
		"attached": attached
	}


func deform_mesh(params: Dictionary) -> Dictionary:
	var mesh_path: String = params.get("mesh_path", "")
	var mode: String = params.get("mode", "displace").to_lower()
	var axis: String = params.get("axis", "y").to_lower()
	var factor: float = float(params.get("factor", 1.0))
	var save_path: String = params.get("save_path", "")

	if mesh_path.is_empty():
		return {"error": "mesh_path is required", "code": ErrorCodes.INVALID_PARAMS}

	if not mesh_path.begins_with("res://"):
		mesh_path = "res://" + mesh_path

	var res := ResourceLoader.load(mesh_path)
	if not (res is ArrayMesh):
		return {"error": "Target resource is not an ArrayMesh: %s" % mesh_path, "code": ErrorCodes.INVALID_PARAMS}

	var mdt := MeshDataTool.new()
	var err := mdt.create_from_surface(res, 0)
	if err != OK:
		return {"error": "Failed to create MeshDataTool from surface 0", "code": ErrorCodes.INTERNAL_ERROR}

	var vert_count := mdt.get_vertex_count()
	for i in range(vert_count):
		var v := mdt.get_vertex(i)
		match mode:
			"displace":
				var norm := mdt.get_vertex_normal(i)
				v += norm * factor
			"taper":
				var scale := 1.0 + v.y * factor
				v.x *= scale
				v.z *= scale
			"scale":
				match axis:
					"x":
						v.x *= factor
					"z":
						v.z *= factor
					_:
						v.y *= factor
		mdt.set_vertex(i, v)

	var new_mesh := ArrayMesh.new()
	mdt.commit_to_surface(new_mesh)

	var target_save := save_path if not save_path.is_empty() else mesh_path
	if not target_save.begins_with("res://"):
		target_save = "res://" + target_save

	var save_err := ResourceSaver.save(new_mesh, target_save)
	return {
		"success": (save_err == OK),
		"modified_vertices": vert_count,
		"mode": mode,
		"save_path": target_save
	}


func create_primitive(params: Dictionary) -> Dictionary:
	var prim_type: String = params.get("primitive", "BoxMesh")
	var props: Dictionary = params.get("properties", {})
	var save_path: String = params.get("save_path", "")
	var attach_to: String = params.get("attach_to", "")

	var mesh: PrimitiveMesh = null
	match prim_type.to_lower():
		"spheremesh":
			var sm := SphereMesh.new()
			if props.has("radius"): sm.radius = float(props["radius"])
			if props.has("height"): sm.height = float(props["height"])
			if props.has("radial_segments"): sm.radial_segments = int(props["radial_segments"])
			if props.has("rings"): sm.rings = int(props["rings"])
			mesh = sm
		"cylindermesh":
			var cm := CylinderMesh.new()
			if props.has("top_radius"): cm.top_radius = float(props["top_radius"])
			if props.has("bottom_radius"): cm.bottom_radius = float(props["bottom_radius"])
			if props.has("height"): cm.height = float(props["height"])
			if props.has("radial_segments"): cm.radial_segments = int(props["radial_segments"])
			mesh = cm
		"capsulemesh":
			var cap := CapsuleMesh.new()
			if props.has("radius"): cap.radius = float(props["radius"])
			if props.has("height"): cap.height = float(props["height"])
			if props.has("radial_segments"): cap.radial_segments = int(props["radial_segments"])
			mesh = cap
		"torusmesh":
			var tm := TorusMesh.new()
			if props.has("inner_radius"): tm.inner_radius = float(props["inner_radius"])
			if props.has("outer_radius"): tm.outer_radius = float(props["outer_radius"])
			if props.has("rings"): tm.rings = int(props["rings"])
			if props.has("ring_segments"): tm.ring_segments = int(props["ring_segments"])
			mesh = tm
		"planemesh":
			var pm := PlaneMesh.new()
			if props.has("size") and props["size"] is Array and props["size"].size() >= 2:
				pm.size = Vector2(float(props["size"][0]), float(props["size"][1]))
			if props.has("subdivide_width"): pm.subdivide_width = int(props["subdivide_width"])
			if props.has("subdivide_depth"): pm.subdivide_depth = int(props["subdivide_depth"])
			mesh = pm
		"prismmesh":
			var prm := PrismMesh.new()
			if props.has("left_to_right"): prm.left_to_right = float(props["left_to_right"])
			if props.has("size") and props["size"] is Array and props["size"].size() >= 3:
				prm.size = Vector3(float(props["size"][0]), float(props["size"][1]), float(props["size"][2]))
			mesh = prm
		_:
			var bm := BoxMesh.new()
			if props.has("size") and props["size"] is Array and props["size"].size() >= 3:
				bm.size = Vector3(float(props["size"][0]), float(props["size"][1]), float(props["size"][2]))
			if props.has("subdivide_width"): bm.subdivide_width = int(props["subdivide_width"])
			if props.has("subdivide_height"): bm.subdivide_height = int(props["subdivide_height"])
			if props.has("subdivide_depth"): bm.subdivide_depth = int(props["subdivide_depth"])
			mesh = bm

	var saved := false
	if not save_path.is_empty():
		if not save_path.begins_with("res://"):
			save_path = "res://" + save_path
		var err := ResourceSaver.save(mesh, save_path)
		if err == OK:
			saved = true

	var attached := false
	var scene_root := _get_scene_root()
	if not attach_to.is_empty() and scene_root != null:
		var target := _resolve_node(scene_root, attach_to)
		if target != null:
			var mi := MeshInstance3D.new()
			mi.name = prim_type
			mi.mesh = mesh
			target.add_child(mi)
			mi.owner = scene_root
			attached = true

	return {
		"success": true,
		"primitive": prim_type,
		"saved": saved,
		"save_path": save_path if saved else "",
		"attached": attached
	}


func get_mesh_info(params: Dictionary) -> Dictionary:
	var mesh_path: String = params.get("mesh_path", "")
	var node_path: String = params.get("node_path", "")

	var mesh: Mesh = null
	if not mesh_path.is_empty():
		if not mesh_path.begins_with("res://"):
			mesh_path = "res://" + mesh_path
		var res := ResourceLoader.load(mesh_path)
		if res is Mesh:
			mesh = res
	elif not node_path.is_empty():
		var scene_root := _get_scene_root()
		if scene_root != null:
			var node := _resolve_node(scene_root, node_path)
			if node is MeshInstance3D and node.mesh != null:
				mesh = node.mesh

	if mesh == null:
		return {"error": "Could not resolve a valid Mesh resource from parameters", "code": ErrorCodes.RESOURCE_NOT_FOUND}

	var aabb := mesh.get_aabb()
	return {
		"success": true,
		"mesh_class": mesh.get_class(),
		"surface_count": mesh.get_surface_count(),
		"aabb_position": [aabb.position.x, aabb.position.y, aabb.position.z],
		"aabb_size": [aabb.size.x, aabb.size.y, aabb.size.z]
	}
