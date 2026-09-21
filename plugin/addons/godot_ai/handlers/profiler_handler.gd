@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

## Handles Godot Performance monitors, memory analysis, render metrics,
## and physics diagnostic queries.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func _format_bytes(bytes: int) -> String:
	if bytes >= 1073741824:
		return "%.2f GB" % (float(bytes) / 1073741824.0)
	elif bytes >= 1048576:
		return "%.2f MB" % (float(bytes) / 1048576.0)
	elif bytes >= 1024:
		return "%.2f KB" % (float(bytes) / 1024.0)
	return "%d B" % bytes


func get_monitors(_params: Dictionary) -> Dictionary:
	return {
		"data": {
			"fps": Performance.get_monitor(Performance.TIME_FPS),
			"process_time": Performance.get_monitor(Performance.TIME_PROCESS),
			"physics_process_time": Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS),
			"navigation_process_time": Performance.get_monitor(Performance.TIME_NAVIGATION_PROCESS),
			"memory_static": Performance.get_monitor(Performance.MEMORY_STATIC),
			"memory_static_max": Performance.get_monitor(Performance.MEMORY_STATIC_MAX),
			"memory_message_buffer_max": Performance.get_monitor(Performance.MEMORY_MESSAGE_BUFFER_MAX),
			"object_count": Performance.get_monitor(Performance.OBJECT_COUNT),
			"object_resource_count": Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT),
			"object_node_count": Performance.get_monitor(Performance.OBJECT_NODE_COUNT),
			"object_orphan_node_count": Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT),
			"render_total_objects": Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME),
			"render_total_primitives": Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),
			"render_total_draw_calls": Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
			"render_video_mem_used": Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED),
			"render_texture_mem_used": Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED),
			"render_buffer_mem_used": Performance.get_monitor(Performance.RENDER_BUFFER_MEM_USED),
			"audio_output_latency": Performance.get_monitor(Performance.AUDIO_OUTPUT_LATENCY),
		}
	}


func get_memory_info(_params: Dictionary) -> Dictionary:
	var mem_static := int(Performance.get_monitor(Performance.MEMORY_STATIC))
	var mem_static_max := int(Performance.get_monitor(Performance.MEMORY_STATIC_MAX))
	var mem_msg := int(Performance.get_monitor(Performance.MEMORY_MESSAGE_BUFFER_MAX))
	var tex_mem := int(Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED))
	var buffer_mem := int(Performance.get_monitor(Performance.RENDER_BUFFER_MEM_USED))
	var video_mem := int(Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED))

	return {
		"data": {
			"static_bytes": mem_static,
			"static_formatted": _format_bytes(mem_static),
			"static_max_bytes": mem_static_max,
			"static_max_formatted": _format_bytes(mem_static_max),
			"message_buffer_max_bytes": mem_msg,
			"message_buffer_max_formatted": _format_bytes(mem_msg),
			"texture_memory_bytes": tex_mem,
			"texture_memory_formatted": _format_bytes(tex_mem),
			"buffer_memory_bytes": buffer_mem,
			"buffer_memory_formatted": _format_bytes(buffer_mem),
			"video_memory_bytes": video_mem,
			"video_memory_formatted": _format_bytes(video_mem),
			"object_count": int(Performance.get_monitor(Performance.OBJECT_COUNT)),
			"resource_count": int(Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT)),
			"node_count": int(Performance.get_monitor(Performance.OBJECT_NODE_COUNT)),
			"orphan_node_count": int(Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT)),
		}
	}


func get_render_info(_params: Dictionary) -> Dictionary:
	return {
		"data": {
			"fps": Performance.get_monitor(Performance.TIME_FPS),
			"draw_calls": int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)),
			"primitives": int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)),
			"objects_in_frame": int(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)),
			"video_mem_bytes": int(Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)),
			"texture_mem_bytes": int(Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED)),
			"buffer_mem_bytes": int(Performance.get_monitor(Performance.RENDER_BUFFER_MEM_USED)),
		}
	}


func get_physics_info(_params: Dictionary) -> Dictionary:
	return {
		"data": {
			"physics_process_time": Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS),
			"physics_2d_active_objects": int(Performance.get_monitor(Performance.PHYSICS_2D_ACTIVE_OBJECTS)),
			"physics_2d_collision_pairs": int(Performance.get_monitor(Performance.PHYSICS_2D_COLLISION_PAIRS)),
			"physics_2d_island_count": int(Performance.get_monitor(Performance.PHYSICS_2D_ISLAND_COUNT)),
			"physics_3d_active_objects": int(Performance.get_monitor(Performance.PHYSICS_3D_ACTIVE_OBJECTS)),
			"physics_3d_collision_pairs": int(Performance.get_monitor(Performance.PHYSICS_3D_COLLISION_PAIRS)),
			"physics_3d_island_count": int(Performance.get_monitor(Performance.PHYSICS_3D_ISLAND_COUNT)),
		}
	}
