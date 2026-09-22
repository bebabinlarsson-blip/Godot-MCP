@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles AudioStreamPlayer / 2D / 3D authoring — node creation, stream
## assignment, playback-property edits, and real editor preview playback.
##
## Stream assignment loads a Godot-imported AudioStream resource from
## res:// (the editor's import step converts .ogg / .wav / .mp3 into a
## streamable AudioStream subclass before we ever see it).
##
## play() / stop() call the live node method directly — no undo, no
## persistence; they match what the inspector's play button does.


const _VALID_TYPES := {
	"1d": "AudioStreamPlayer",
	"2d": "AudioStreamPlayer2D",
	"3d": "AudioStreamPlayer3D",
}

## Whitelist of playback properties settable via audio_player_set_playback.
## Each value is the expected Variant type of the param dict value.
const _PLAYBACK_KEYS := {
	"volume_db": TYPE_FLOAT,
	"pitch_scale": TYPE_FLOAT,
	"autoplay": TYPE_BOOL,
	"bus": TYPE_STRING,
}


var _undo_redo: EditorUndoRedoManager


func _init(undo_redo: EditorUndoRedoManager) -> void:
	_undo_redo = undo_redo


# ============================================================================
# audio_player_create
# ============================================================================

func create_player(params: Dictionary) -> Dictionary:
	var parent_path: String = params.get("parent_path", "")
	var node_name: String = params.get("name", "AudioStreamPlayer")
	var type_str: String = params.get("type", "1d")

	if not _VALID_TYPES.has(type_str):
		return ErrorCodes.make(
			ErrorCodes.VALUE_OUT_OF_RANGE,
			"Invalid audio player type '%s'. Valid: %s" % [type_str, ", ".join(_VALID_TYPES.keys())]
		)

	var _scene_check := McpNodeValidator.require_scene_or_error()
	if _scene_check.has("error"):
		return _scene_check
	var scene_root: Node = _scene_check.scene_root

	var parent: Node = scene_root
	if not parent_path.is_empty():
		parent = McpScenePath.resolve(parent_path, scene_root)
		if parent == null:
			return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, McpScenePath.format_parent_error(parent_path, scene_root))

	var node := _instantiate_player(type_str)
	if node == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to instantiate audio player")
	if not node_name.is_empty():
		node.name = node_name

	_undo_redo.create_action("MCP: Create %s '%s'" % [_VALID_TYPES[type_str], node.name])
	_undo_redo.add_do_method(parent, "add_child", node, true)
	_undo_redo.add_do_method(node, "set_owner", scene_root)
	_undo_redo.add_do_reference(node)
	_undo_redo.add_undo_method(parent, "remove_child", node)
	_undo_redo.commit_action()

	return {
		"data": {
			"path": McpScenePath.from_node(node, scene_root),
			"parent_path": McpScenePath.from_node(parent, scene_root),
			"name": String(node.name),
			"type": type_str,
			"class": _VALID_TYPES[type_str],
			"undoable": true,
		}
	}


# ============================================================================
# audio_player_set_stream
# ============================================================================

func set_stream(params: Dictionary) -> Dictionary:
	var player_path: String = params.get("player_path", "")
	var stream_path: String = params.get("stream_path", "")

	if player_path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: player_path")
	if stream_path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: stream_path")

	var stream_path_err = McpPathValidator.loadable_error(stream_path, "stream_path")
	if stream_path_err != null:
		return stream_path_err

	var resolved := _resolve_player(player_path)
	if resolved.has("error"):
		return resolved
	var player: Node = resolved.player

	if not ResourceLoader.exists(stream_path):
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "AudioStream not found: %s" % stream_path)
	var loaded := ResourceLoader.load(stream_path)
	if loaded == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to load AudioStream: %s" % stream_path)
	if not (loaded is AudioStream):
		return ErrorCodes.make(
			ErrorCodes.WRONG_TYPE,
			"Resource at %s is not an AudioStream (got %s)" % [stream_path, loaded.get_class()]
		)

	var old_stream: AudioStream = player.stream

	_undo_redo.create_action("MCP: Set audio stream on %s" % player.name)
	_undo_redo.add_do_property(player, "stream", loaded)
	_undo_redo.add_undo_property(player, "stream", old_stream)
	_undo_redo.commit_action()

	return {
		"data": {
			"player_path": player_path,
			"stream_path": stream_path,
			"stream_class": loaded.get_class(),
			"duration_seconds": float(loaded.get_length()),
			"undoable": true,
		}
	}


# ============================================================================
# audio_player_set_playback
# ============================================================================

func set_playback(params: Dictionary) -> Dictionary:
	var player_path: String = params.get("player_path", "")
	if player_path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: player_path")

	var resolved := _resolve_player(player_path)
	if resolved.has("error"):
		return resolved
	var player: Node = resolved.player

	var updates: Dictionary = {}
	for key in _PLAYBACK_KEYS:
		if params.has(key):
			var expected_type: int = _PLAYBACK_KEYS[key]
			var value = params.get(key)
			var coerced = _coerce_playback_value(value, expected_type)
			if coerced == null:
				return ErrorCodes.make(
					ErrorCodes.INVALID_PARAMS,
					"Invalid value for %s: expected %s, got %s" % [
						key, type_string(expected_type), type_string(typeof(value))
					]
				)
			updates[key] = coerced

	if updates.is_empty():
		return ErrorCodes.make(
			ErrorCodes.MISSING_REQUIRED_PARAM,
			"At least one of %s is required" % ", ".join(_PLAYBACK_KEYS.keys())
		)

	var old_values: Dictionary = {}
	for key in updates:
		old_values[key] = player.get(key)

	_undo_redo.create_action("MCP: Update playback on %s" % player.name)
	for key in updates:
		_undo_redo.add_do_property(player, key, updates[key])
		_undo_redo.add_undo_property(player, key, old_values[key])
	_undo_redo.commit_action()

	return {
		"data": {
			"player_path": player_path,
			"applied": updates.keys(),
			"values": updates,
			"undoable": true,
		}
	}


# ============================================================================
# audio_play  (runtime preview — not saved with scene)
# ============================================================================

func play(params: Dictionary) -> Dictionary:
	var player_path: String = params.get("player_path", "")
	var from_position: float = float(params.get("from_position", 0.0))

	if player_path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: player_path")

	var resolved := _resolve_player(player_path)
	if resolved.has("error"):
		return resolved
	var player: Node = resolved.player

	if player.stream == null:
		return ErrorCodes.make(
			ErrorCodes.MISSING_REQUIRED_PARAM,
			"Player has no stream assigned — call audio_player_set_stream first"
		)

	player.play(from_position)

	return {
		"data": {
			"player_path": player_path,
			"from_position": from_position,
			"playing": bool(player.playing),
			"undoable": false,
			"reason": "Runtime playback state — not saved with scene",
		}
	}


# ============================================================================
# audio_stop  (runtime preview — not saved with scene)
# ============================================================================

func stop(params: Dictionary) -> Dictionary:
	var player_path: String = params.get("player_path", "")
	if player_path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: player_path")

	var resolved := _resolve_player(player_path)
	if resolved.has("error"):
		return resolved
	var player: Node = resolved.player

	player.stop()

	return {
		"data": {
			"player_path": player_path,
			"playing": bool(player.playing),
			"undoable": false,
			"reason": "Runtime playback state — not saved with scene",
		}
	}


# ============================================================================
# audio_list  (read — scan project for AudioStream resources)
# ============================================================================

func list_streams(params: Dictionary) -> Dictionary:
	var root: String = params.get("root", "res://")
	var include_duration: bool = bool(params.get("include_duration", true))

	var root_err = McpPathValidator.path_error(root, "root")
	if root_err != null:
		return root_err

	var efs := EditorInterface.get_resource_filesystem()
	if efs == null:
		return ErrorCodes.make_not_ready(
			ErrorCodes.SUB_EDITOR_UNAVAILABLE,
			"EditorFileSystem not available", false)

	var results: Array[Dictionary] = []
	var start_dir := efs.get_filesystem_path(root)
	if start_dir == null:
		start_dir = efs.get_filesystem()
	_scan_audio(start_dir, root, include_duration, results)
	return {
		"data": {
			"root": root,
			"streams": results,
			"count": results.size(),
		}
	}


func _scan_audio(dir: EditorFileSystemDirectory, root: String, include_duration: bool, out: Array[Dictionary]) -> void:
	if dir == null:
		return
	for i in dir.get_file_count():
		var file_path := dir.get_file_path(i)
		if not file_path.begins_with(root):
			continue
		var file_type := dir.get_file_type(i)
		var is_audio := file_type == "AudioStream" or ClassDB.is_parent_class(file_type, "AudioStream")
		if not is_audio:
			continue
		var entry: Dictionary = {
			"path": file_path,
			"class": file_type,
		}
		if include_duration:
			var res := ResourceLoader.load(file_path)
			if res is AudioStream:
				entry["duration_seconds"] = float((res as AudioStream).get_length())
			else:
				entry["duration_seconds"] = 0.0
		out.append(entry)
	for i in dir.get_subdir_count():
		_scan_audio(dir.get_subdir(i), root, include_duration, out)


# ============================================================================
# Helpers
# ============================================================================

static func _instantiate_player(type_str: String) -> Node:
	match type_str:
		"1d":
			return AudioStreamPlayer.new()
		"2d":
			return AudioStreamPlayer2D.new()
		"3d":
			return AudioStreamPlayer3D.new()
	return null


func _resolve_player(player_path: String) -> Dictionary:
	var resolved := McpNodeValidator.resolve_or_error(player_path, "player_path")
	if resolved.has("error"):
		return resolved
	var node: Node = resolved.node
	var is_player := node is AudioStreamPlayer \
		or node is AudioStreamPlayer2D \
		or node is AudioStreamPlayer3D
	if not is_player:
		return ErrorCodes.make(
			ErrorCodes.WRONG_TYPE,
			"Node at %s is not an AudioStreamPlayer/2D/3D (got %s)" % [player_path, node.get_class()]
		)
	return {"player": node}


## Coerce a playback param value to the expected type. int→float and
## strictly-numeric strings are allowed so JSON integers and stringified
## floats (#964) pass through; everything else requires the exact type.
## Returns the coerced value, or null on type mismatch.
static func _coerce_playback_value(value: Variant, expected_type: int) -> Variant:
	match expected_type:
		TYPE_FLOAT:
			var parsed: Variant = McpJsonValues.parse_float(value)
			if parsed != null:
				return parsed
		TYPE_BOOL:
			if value is bool:
				return value
		TYPE_STRING:
			if value is String:
				return value
	return null


# ============================================================================
# generate_procedural_sfx
# ============================================================================

func generate_procedural_sfx(params: Dictionary) -> Dictionary:
	var preset: String = params.get("preset", "jump").to_lower()
	var dest_path: String = params.get("dest_path", "")
	if dest_path.is_empty():
		dest_path = "res://audio/%s.wav" % preset
	if not dest_path.begins_with("res://"):
		dest_path = "res://" + dest_path
	if not dest_path.ends_with(".wav"):
		dest_path += ".wav"

	var sample_rate: int = int(params.get("sample_rate", 22050))
	var duration: float = float(params.get("duration", 0.0))
	if duration <= 0.0:
		match preset:
			"jump", "laser":
				duration = 0.25
			"coin":
				duration = 0.3
			"hit":
				duration = 0.15
			"explosion":
				duration = 0.45
			"powerup":
				duration = 0.4
			"step", "click":
				duration = 0.06
			_:
				duration = 0.25

	var total_samples := int(duration * sample_rate)
	var samples := PackedByteArray()
	samples.resize(total_samples * 2)

	var phase := 0.0
	for i in range(total_samples):
		var progress: float = float(i) / float(total_samples)
		var sample_val := 0.0

		match preset:
			"jump":
				var freq: float = 150.0 + 400.0 * (progress * progress)
				phase += freq / float(sample_rate)
				var env: float = 1.0 - progress
				var sq: float = 1.0 if fmod(phase, 1.0) < 0.5 else -1.0
				sample_val = sq * env * 0.6
			"coin":
				var freq: float = 987.77 if progress < 0.35 else 1318.51
				phase += freq / float(sample_rate)
				var env: float = (1.0 - progress * 0.8)
				var sq: float = 1.0 if fmod(phase, 1.0) < 0.5 else -1.0
				sample_val = sq * env * 0.5
			"laser":
				var freq: float = 900.0 * (1.0 - progress) + 80.0
				phase += freq / float(sample_rate)
				var env: float = 1.0 - progress
				var sq: float = 1.0 if fmod(phase, 1.0) < 0.5 else -1.0
				sample_val = sq * env * 0.7
			"hit":
				var freq: float = 160.0 * (1.0 - progress * 0.8) + 40.0
				phase += freq / float(sample_rate)
				var env: float = 1.0 - progress
				var sq: float = 1.0 if fmod(phase, 1.0) < 0.5 else -1.0
				var noise: float = randf_range(-1.0, 1.0)
				sample_val = (sq * 0.6 + noise * 0.4) * env * 0.8
			"explosion":
				var noise: float = randf_range(-1.0, 1.0)
				var env: float = pow(1.0 - progress, 2.0)
				sample_val = noise * env * 0.85
			"powerup":
				var freq: float = 330.0
				if progress > 0.66:
					freq = 659.25
				elif progress > 0.33:
					freq = 440.0
				phase += freq / float(sample_rate)
				var env: float = 1.0 - progress * 0.5
				var tri: float = 4.0 * abs(fmod(phase, 1.0) - 0.5) - 1.0
				sample_val = tri * env * 0.7
			"step":
				var noise: float = randf_range(-1.0, 1.0)
				var env: float = 1.0 - progress
				sample_val = noise * env * 0.4
			"click":
				var freq: float = 1200.0
				phase += freq / float(sample_rate)
				var env: float = pow(1.0 - progress, 3.0)
				sample_val = sin(phase * TAU) * env * 0.5
			_:
				var freq: float = 440.0
				phase += freq / float(sample_rate)
				sample_val = sin(phase * TAU) * (1.0 - progress) * 0.5

		var int_val := int(clamp(sample_val, -1.0, 1.0) * 32767.0)
		if int_val < 0:
			int_val += 65536
		samples[i * 2] = int_val & 0xFF
		samples[i * 2 + 1] = (int_val >> 8) & 0xFF

	var wav_bytes := PackedByteArray()
	wav_bytes.resize(44 + samples.size())
	wav_bytes[0] = 0x52; wav_bytes[1] = 0x49; wav_bytes[2] = 0x46; wav_bytes[3] = 0x46
	var file_len := 36 + samples.size()
	wav_bytes[4] = file_len & 0xFF
	wav_bytes[5] = (file_len >> 8) & 0xFF
	wav_bytes[6] = (file_len >> 16) & 0xFF
	wav_bytes[7] = (file_len >> 24) & 0xFF
	wav_bytes[8] = 0x57; wav_bytes[9] = 0x41; wav_bytes[10] = 0x56; wav_bytes[11] = 0x45
	wav_bytes[12] = 0x66; wav_bytes[13] = 0x6D; wav_bytes[14] = 0x74; wav_bytes[15] = 0x20
	wav_bytes[16] = 16; wav_bytes[17] = 0; wav_bytes[18] = 0; wav_bytes[19] = 0
	wav_bytes[20] = 1; wav_bytes[21] = 0
	wav_bytes[22] = 1; wav_bytes[23] = 0
	wav_bytes[24] = sample_rate & 0xFF
	wav_bytes[25] = (sample_rate >> 8) & 0xFF
	wav_bytes[26] = (sample_rate >> 16) & 0xFF
	wav_bytes[27] = (sample_rate >> 24) & 0xFF
	var byte_rate := sample_rate * 2
	wav_bytes[28] = byte_rate & 0xFF
	wav_bytes[29] = (byte_rate >> 8) & 0xFF
	wav_bytes[30] = (byte_rate >> 16) & 0xFF
	wav_bytes[31] = (byte_rate >> 24) & 0xFF
	wav_bytes[32] = 2; wav_bytes[33] = 0
	wav_bytes[34] = 16; wav_bytes[35] = 0
	wav_bytes[36] = 0x64; wav_bytes[37] = 0x61; wav_bytes[38] = 0x74; wav_bytes[39] = 0x61
	var data_size := samples.size()
	wav_bytes[40] = data_size & 0xFF
	wav_bytes[41] = (data_size >> 8) & 0xFF
	wav_bytes[42] = (data_size >> 16) & 0xFF
	wav_bytes[43] = (data_size >> 24) & 0xFF

	for j in range(samples.size()):
		wav_bytes[44 + j] = samples[j]

	var dir_path: String = dest_path.get_base_dir()
	if not DirAccess.dir_exists_absolute(dir_path):
		DirAccess.make_dir_recursive_absolute(dir_path)

	var f := FileAccess.open(dest_path, FileAccess.WRITE)
	if not f:
		return ErrorCodes.make(
			ErrorCodes.INTERNAL_ERROR,
			"Cannot open '%s' for writing: %s" % [dest_path, error_string(FileAccess.get_open_error())]
		)
	f.store_buffer(wav_bytes)
	f.close()

	if EditorInterface.get_resource_filesystem():
		EditorInterface.get_resource_filesystem().reindex_file(dest_path)

	return {
		"path": dest_path,
		"preset": preset,
		"duration": duration,
		"sample_rate": sample_rate,
		"bytes_written": wav_bytes.size(),
	}


# ============================================================================
# scaffold_buses
# ============================================================================

func scaffold_buses(params: Dictionary) -> Dictionary:
	var standard_buses: Array = ["Music", "SFX", "UI"]
	var bus_volumes: Dictionary = params.get("volumes", {
		"Master": 0.0,
		"Music": -6.0,
		"SFX": 0.0,
		"UI": -3.0,
	})

	for bus_name in standard_buses:
		var idx := AudioServer.get_bus_index(bus_name)
		if idx == -1:
			AudioServer.add_bus()
			idx = AudioServer.bus_count - 1
			AudioServer.set_bus_name(idx, bus_name)
			AudioServer.set_bus_send(idx, &"Master")

	for bus_name in bus_volumes.keys():
		var idx := AudioServer.get_bus_index(bus_name)
		if idx != -1:
			var vol: float = float(bus_volumes[bus_name])
			AudioServer.set_bus_volume_db(idx, vol)

	var configured: Array[Dictionary] = []
	for i in range(AudioServer.bus_count):
		configured.append({
			"index": i,
			"name": AudioServer.get_bus_name(i),
			"send": AudioServer.get_bus_send(i),
			"volume_db": AudioServer.get_bus_volume_db(i),
			"solo": AudioServer.is_bus_solo(i),
			"mute": AudioServer.is_bus_mute(i),
		})

	return {
		"buses": configured,
		"bus_count": AudioServer.bus_count,
	}


# ============================================================================
# scaffold_music_player
# ============================================================================

func scaffold_music_player(params: Dictionary) -> Dictionary:
	var _scene_check := McpNodeValidator.require_scene_or_error()
	if _scene_check.has("error"):
		return _scene_check
	var scene_root: Node = _scene_check.scene_root

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = scene_root
	if not parent_path.is_empty():
		parent = McpScenePath.resolve(parent_path, scene_root)
		if parent == null:
			return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, McpScenePath.format_parent_error(parent_path, scene_root))

	var player_name: String = params.get("name", "MusicPlayer")
	var stream_path: String = params.get("stream_path", "")
	var autoplay: bool = bool(params.get("autoplay", true))
	var volume_db: float = float(params.get("volume_db", 0.0))
	var bus: String = params.get("bus", "Music")
	var loop: bool = bool(params.get("loop", true))

	# Ensure bus exists
	if AudioServer.get_bus_index(bus) == -1:
		AudioServer.add_bus()
		var idx := AudioServer.bus_count - 1
		AudioServer.set_bus_name(idx, bus)
		AudioServer.set_bus_send(idx, &"Master")

	var player := AudioStreamPlayer.new()
	player.name = player_name
	player.bus = bus
	player.volume_db = volume_db
	player.autoplay = autoplay

	if not stream_path.is_empty():
		if ResourceLoader.exists(stream_path):
			var res := load(stream_path)
			if res is AudioStream:
				if loop:
					if res is AudioStreamWAV:
						res.loop_mode = AudioStreamWAV.LOOP_FORWARD
					elif res.has_method("set_loop"):
						res.set_loop(true)
				player.stream = res

	_undo_redo.create_action("MCP: Scaffold Music Player '%s'" % player_name)
	_undo_redo.add_do_method(parent, "add_child", player, true)
	_undo_redo.add_do_method(player, "set_owner", scene_root)
	_undo_redo.add_do_reference(player)
	_undo_redo.add_undo_method(parent, "remove_child", player)
	_undo_redo.commit_action()

	return {
		"data": {
			"player_path": McpScenePath.from_node(player, scene_root),
			"name": player_name,
			"bus": bus,
			"autoplay": autoplay,
			"volume_db": volume_db,
			"stream": stream_path,
			"undoable": true,
		}
	}


# ============================================================================
# scaffold_sound_manager
# ============================================================================

func scaffold_sound_manager(params: Dictionary) -> Dictionary:
	var mgr_name: String = params.get("name", "SoundManager")
	var script_path: String = params.get("script_path", "res://scripts/sound_manager.gd")
	var pool_size: int = int(params.get("pool_size", 16))
	var default_bus: String = params.get("bus", "SFX")
	var register_autoload: bool = bool(params.get("register_autoload", true))

	var path_err = McpPathValidator.path_error(script_path, "script_path")
	if path_err != null:
		return path_err

	var base_dir := script_path.get_base_dir()
	if not DirAccess.dir_exists_absolute(base_dir):
		DirAccess.make_dir_recursive_absolute(base_dir)

	# Ensure SFX bus exists
	if AudioServer.get_bus_index(default_bus) == -1:
		AudioServer.add_bus()
		var idx := AudioServer.bus_count - 1
		AudioServer.set_bus_name(idx, default_bus)
		AudioServer.set_bus_send(idx, &"Master")

	var sound_code := """extends Node

@export var default_bus: String = "%s"
@export var pool_size: int = %d

var _players: Array[AudioStreamPlayer] = []
var _next_player_idx: int = 0

func _ready() -> void:
	for i in range(pool_size):
		var player := AudioStreamPlayer.new()
		player.name = "SFXPlayer_" + str(i)
		player.bus = default_bus
		add_child(player)
		_players.append(player)

func play_sfx(stream: Variant, pitch_variance: float = 0.1, volume_db: float = 0.0, bus_override: String = "") -> AudioStreamPlayer:
	var sound_stream: AudioStream = null
	if stream is String:
		if ResourceLoader.exists(stream):
			sound_stream = load(stream) as AudioStream
	elif stream is AudioStream:
		sound_stream = stream

	if sound_stream == null:
		push_warning("SoundManager: Invalid audio stream provided.")
		return null

	var target_player: AudioStreamPlayer = null
	for p in _players:
		if not p.playing:
			target_player = p
			break

	if target_player == null:
		target_player = _players[_next_player_idx]
		_next_player_idx = (_next_player_idx + 1) %% _players.size()

	target_player.stream = sound_stream
	target_player.volume_db = volume_db
	target_player.bus = bus_override if not bus_override.is_empty() else default_bus

	if pitch_variance > 0.0:
		target_player.pitch_scale = maxf(0.05, 1.0 + randf_range(-pitch_variance, pitch_variance))
	else:
		target_player.pitch_scale = 1.0

	target_player.play()
	return target_player

func play_sfx_at_position(stream: Variant, global_pos: Vector2, pitch_variance: float = 0.1, volume_db: float = 0.0, bus_override: String = "") -> AudioStreamPlayer2D:
	var sound_stream: AudioStream = null
	if stream is String:
		if ResourceLoader.exists(stream):
			sound_stream = load(stream) as AudioStream
	elif stream is AudioStream:
		sound_stream = stream

	if sound_stream == null:
		push_warning("SoundManager: Invalid audio stream provided.")
		return null

	var p2d := AudioStreamPlayer2D.new()
	p2d.stream = sound_stream
	p2d.global_position = global_pos
	p2d.volume_db = volume_db
	p2d.bus = bus_override if not bus_override.is_empty() else default_bus
	if pitch_variance > 0.0:
		p2d.pitch_scale = maxf(0.05, 1.0 + randf_range(-pitch_variance, pitch_variance))
	get_tree().root.add_child(p2d)
	p2d.finished.connect(func(): p2d.queue_free())
	p2d.play()
	return p2d

func stop_all() -> void:
	for p in _players:
		p.stop()
""" % [default_bus, pool_size]

	var file := FileAccess.open(script_path, FileAccess.WRITE)
	if file == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to create sound manager script at: %s" % script_path)
	file.store_string(sound_code)
	file.close()

	var autoload_ok := false
	if register_autoload:
		var key := "autoload/%s" % mgr_name
		ProjectSettings.set_setting(key, "*" + script_path)
		ProjectSettings.set_initial_value(key, "")
		ProjectSettings.set_as_basic(key, true)
		autoload_ok = (ProjectSettings.save() == OK)

	var efs := EditorInterface.get_resource_filesystem()
	if efs != null:
		efs.update_file(script_path)

	return {
		"data": {
			"name": mgr_name,
			"script_path": script_path,
			"pool_size": pool_size,
			"bus": default_bus,
			"register_autoload": register_autoload,
			"autoload_saved": autoload_ok,
		}
	}


# ============================================================================
# Audio Bus & DSP Effects
# ============================================================================

func _resolve_bus_index(bus_val) -> int:
	if bus_val is int:
		if bus_val >= 0 and bus_val < AudioServer.bus_count:
			return bus_val
		return -1
	var name_str := str(bus_val).strip_edges()
	if name_str.is_valid_int():
		var idx := int(name_str)
		if idx >= 0 and idx < AudioServer.bus_count:
			return idx
	for i in range(AudioServer.bus_count):
		if AudioServer.get_bus_name(i) == name_str:
			return i
	return -1


func bus_list(params: Dictionary = {}) -> Dictionary:
	var buses: Array = []
	for i in range(AudioServer.bus_count):
		var eff_count := AudioServer.get_bus_effect_count(i)
		var effects: Array = []
		for e in range(eff_count):
			var eff := AudioServer.get_bus_effect(i, e)
			effects.append({
				"index": e,
				"name": AudioServer.get_bus_effect_instance(i, e).get_class() if AudioServer.get_bus_effect_instance(i, e) != null else "",
				"class": eff.get_class() if eff != null else "",
				"enabled": AudioServer.is_bus_effect_enabled(i, e)
			})
		buses.append({
			"index": i,
			"name": AudioServer.get_bus_name(i),
			"volume_db": AudioServer.get_bus_volume_db(i),
			"send": AudioServer.get_bus_send(i),
			"solo": AudioServer.is_bus_solo(i),
			"mute": AudioServer.is_bus_mute(i),
			"bypass_effects": AudioServer.is_bus_bypassing_effects(i),
			"effect_count": eff_count,
			"effects": effects
		})

	return {
		"data": {
			"bus_count": AudioServer.bus_count,
			"buses": buses
		}
	}


func bus_add(params: Dictionary) -> Dictionary:
	var bus_name: String = params.get("name", "").strip_edges()
	if bus_name.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: name")

	for i in range(AudioServer.bus_count):
		if AudioServer.get_bus_name(i) == bus_name:
			return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "Audio bus '%s' already exists at index %d" % [bus_name, i])

	var at_pos: int = int(params.get("at_pos", -1))
	AudioServer.add_bus(at_pos)
	var new_idx := AudioServer.bus_count - 1 if at_pos < 0 or at_pos >= AudioServer.bus_count else at_pos
	AudioServer.set_bus_name(new_idx, bus_name)

	var send_target: String = params.get("send", "Master")
	if not send_target.is_empty() and send_target != bus_name:
		AudioServer.set_bus_send(new_idx, StringName(send_target))

	var volume_db: float = float(params.get("volume_db", 0.0))
	AudioServer.set_bus_volume_db(new_idx, volume_db)

	return {
		"data": {
			"index": new_idx,
			"name": bus_name,
			"send": str(AudioServer.get_bus_send(new_idx)),
			"volume_db": volume_db
		}
	}


func bus_remove(params: Dictionary) -> Dictionary:
	var bus_val = params.get("bus", "")
	var idx := _resolve_bus_index(bus_val)
	if idx < 0:
		return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Audio bus not found: %s" % str(bus_val))
	if idx == 0:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Cannot remove Master audio bus (index 0)")

	var removed_name := AudioServer.get_bus_name(idx)
	AudioServer.remove_bus(idx)

	return {
		"data": {
			"removed_index": idx,
			"removed_name": removed_name,
			"remaining_bus_count": AudioServer.bus_count
		}
	}


func bus_set_properties(params: Dictionary) -> Dictionary:
	var bus_val = params.get("bus", "")
	var idx := _resolve_bus_index(bus_val)
	if idx < 0:
		return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Audio bus not found: %s" % str(bus_val))

	if params.has("volume_db"):
		AudioServer.set_bus_volume_db(idx, float(params["volume_db"]))
	if params.has("send"):
		AudioServer.set_bus_send(idx, StringName(str(params["send"])))
	if params.has("solo"):
		AudioServer.set_bus_solo(idx, bool(params["solo"]))
	if params.has("mute"):
		AudioServer.set_bus_mute(idx, bool(params["mute"]))
	if params.has("bypass_effects"):
		AudioServer.set_bus_bypass_effects(idx, bool(params["bypass_effects"]))

	return {
		"data": {
			"index": idx,
			"name": AudioServer.get_bus_name(idx),
			"volume_db": AudioServer.get_bus_volume_db(idx),
			"send": str(AudioServer.get_bus_send(idx)),
			"solo": AudioServer.is_bus_solo(idx),
			"mute": AudioServer.is_bus_mute(idx),
			"bypass_effects": AudioServer.is_bus_bypassing_effects(idx)
		}
	}


func bus_add_effect(params: Dictionary) -> Dictionary:
	var bus_val = params.get("bus", "Master")
	var idx := _resolve_bus_index(bus_val)
	if idx < 0:
		return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Audio bus not found: %s" % str(bus_val))

	var effect_type: String = params.get("effect_type", "reverb").to_lower()
	var effect_params: Dictionary = params.get("params", {})
	var effect: AudioEffect = null

	match effect_type:
		"reverb":
			var rev := AudioEffectReverb.new()
			if effect_params.has("room_size"): rev.room_size = float(effect_params["room_size"])
			if effect_params.has("damping"): rev.damping = float(effect_params["damping"])
			if effect_params.has("wet"): rev.wet = float(effect_params["wet"])
			if effect_params.has("dry"): rev.dry = float(effect_params["dry"])
			effect = rev
		"delay":
			var dly := AudioEffectDelay.new()
			if effect_params.has("feedback_active"): dly.feedback_active = bool(effect_params["feedback_active"])
			if effect_params.has("feedback_delay_ms"): dly.feedback_delay_ms = float(effect_params["feedback_delay_ms"])
			if effect_params.has("tap1_delay_ms"): dly.tap1_delay_ms = float(effect_params["tap1_delay_ms"])
			effect = dly
		"chorus":
			var cho := AudioEffectChorus.new()
			if effect_params.has("voice_count"): cho.voice_count = int(effect_params["voice_count"])
			if effect_params.has("wet"): cho.wet = float(effect_params["wet"])
			effect = cho
		"distortion":
			var dis := AudioEffectDistortion.new()
			if effect_params.has("drive"): dis.drive = float(effect_params["drive"])
			effect = dis
		"pitch_shift":
			var ps := AudioEffectPitchShift.new()
			if effect_params.has("pitch_scale"): ps.pitch_scale = float(effect_params["pitch_scale"])
			effect = ps
		"low_pass":
			var lpf := AudioEffectLowPassFilter.new()
			if effect_params.has("cutoff_hz"): lpf.cutoff_hz = float(effect_params["cutoff_hz"])
			effect = lpf
		"high_pass":
			var hpf := AudioEffectHighPassFilter.new()
			if effect_params.has("cutoff_hz"): hpf.cutoff_hz = float(effect_params["cutoff_hz"])
			effect = hpf
		"compressor":
			var cmp := AudioEffectCompressor.new()
			if effect_params.has("threshold"): cmp.threshold = float(effect_params["threshold"])
			if effect_params.has("ratio"): cmp.ratio = float(effect_params["ratio"])
			effect = cmp
		_:
			return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE,
				"Unknown effect_type '%s'. Valid: reverb, delay, chorus, distortion, pitch_shift, low_pass, high_pass, compressor" % effect_type)

	var at_pos: int = int(params.get("at_pos", -1))
	AudioServer.add_bus_effect(idx, effect, at_pos)
	var eff_index := AudioServer.get_bus_effect_count(idx) - 1 if at_pos < 0 else at_pos

	return {
		"data": {
			"bus_index": idx,
			"bus_name": AudioServer.get_bus_name(idx),
			"effect_index": eff_index,
			"effect_type": effect_type,
			"effect_class": effect.get_class()
		}
	}


func bus_save_layout(params: Dictionary = {}) -> Dictionary:
	var path: String = params.get("path", "res://default_bus_layout.tres")
	if not path.begins_with("res://"):
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "Path must begin with res://")

	var layout: AudioBusLayout = AudioServer.generate_bus_layout()
	var err := ResourceSaver.save(layout, path)
	if err != OK:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to save audio bus layout to %s (error %d)" % [path, err])

	return {
		"data": {
			"path": path,
			"bus_count": layout.get_bus_count()
		}
	}
