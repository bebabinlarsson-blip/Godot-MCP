@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles Godot 4 GPU Compute Shaders, RenderingDevice pipelines,
## uniform storage buffers, GPU dispatch, and buffer readback.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func create_shader(params: Dictionary) -> Dictionary:
	var shader_path: String = params.get("shader_path", "res://shaders/compute_example.glsl")
	var custom_code: String = params.get("code", "")

	var default_code := """#[compute]
#version 450

layout(local_size_x = 8, local_size_y = 1, local_size_z = 1) in;

layout(set = 0, binding = 0, std430) buffer DataBuffer {
    float data[];
} my_buffer;

void main() {
    uint idx = gl_GlobalInvocationID.x;
    my_buffer.data[idx] *= 2.0;
}
"""

	var final_code := custom_code if not custom_code.is_empty() else default_code

	var global_path := ProjectSettings.globalize_path(shader_path)
	var dir_path := global_path.get_base_dir()
	if not DirAccess.dir_exists_absolute(dir_path):
		DirAccess.make_dir_recursive_absolute(dir_path)

	var file := FileAccess.open(shader_path, FileAccess.WRITE)
	if file == null:
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "Failed to write %s: %d" % [shader_path, FileAccess.get_open_error()])

	file.store_string(final_code)
	file.close()

	if Engine.has_singleton("EditorInterface"):
		var editor_interface := Engine.get_singleton("EditorInterface")
		var fs = editor_interface.get_resource_filesystem()
		if fs != null:
			fs.update_file(shader_path)

	return {
		"data": {
			"shader_path": shader_path,
			"created": true,
		}
	}


func get_device_info(_params: Dictionary) -> Dictionary:
	var rd := RenderingServer.get_rendering_device()
	if rd == null:
		rd = RenderingServer.create_local_rendering_device()

	if rd == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "RenderingDevice is not available in current rendering method")

	return {
		"data": {
			"device_name": rd.get_device_name(),
			"vendor_name": rd.get_device_vendor_name(),
			"driver_name": rd.get_driver_name(),
			"driver_version": rd.get_driver_version(),
			"max_compute_workgroup_size": [
				rd.limit_get(RenderingDevice.LIMIT_MAX_COMPUTE_WORKGROUP_SIZE_X),
				rd.limit_get(RenderingDevice.LIMIT_MAX_COMPUTE_WORKGROUP_SIZE_Y),
				rd.limit_get(RenderingDevice.LIMIT_MAX_COMPUTE_WORKGROUP_SIZE_Z),
			],
			"max_compute_invocations": rd.limit_get(RenderingDevice.LIMIT_MAX_COMPUTE_WORKGROUP_INVOCATIONS),
		}
	}


func run_compute(params: Dictionary) -> Dictionary:
	var shader_path: String = params.get("shader_path", "")
	if shader_path.is_empty():
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "shader_path must be specified")

	var rd := RenderingServer.create_local_rendering_device()
	if rd == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to create local RenderingDevice")

	var shader_file = load(shader_path)
	if shader_file == null or not (shader_file is RDShaderFile):
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "RDShaderFile not found or invalid at %s" % shader_path)

	var spirv: RDShaderSPIRV = shader_file.get_spirv()
	var shader := rd.shader_create_from_spirv(spirv)
	if not shader.is_valid():
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to compile compute shader from SPIR-V")

	var raw_floats: Array = params.get("input_buffer", [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
	var input_data := PackedFloat32Array()
	for f in raw_floats:
		input_data.append(float(f))

	var input_bytes := input_data.to_byte_array()
	var buffer := rd.storage_buffer_create(input_bytes.size(), input_bytes)

	var uniform := RDUniform.new()
	uniform.uniform_type = RenderingDevice.UNIFORM_TYPE_STORAGE_BUFFER
	uniform.binding = 0
	uniform.add_id(buffer)

	var uniform_set := rd.uniform_set_create([uniform], shader, 0)
	var pipeline := rd.compute_pipeline_create(shader)

	var x_groups: int = int(params.get("x_groups", 1))
	var y_groups: int = int(params.get("y_groups", 1))
	var z_groups: int = int(params.get("z_groups", 1))

	var compute_list := rd.compute_list_begin()
	rd.compute_list_bind_compute_pipeline(compute_list, pipeline)
	rd.compute_list_bind_uniform_set(compute_list, uniform_set, 0)
	rd.compute_list_dispatch(compute_list, x_groups, y_groups, z_groups)
	rd.compute_list_end()

	rd.submit()
	rd.sync()

	var output_bytes := rd.buffer_get_data(buffer)
	var output_floats := output_bytes.to_float32_array()

	var result_array: Array = []
	for val in output_floats:
		result_array.append(val)

	rd.free_rid(pipeline)
	rd.free_rid(uniform_set)
	rd.free_rid(buffer)
	rd.free_rid(shader)

	return {
		"data": {
			"shader_path": shader_path,
			"elements_computed": result_array.size(),
			"output_buffer": result_array,
		}
	}
