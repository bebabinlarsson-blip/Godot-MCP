@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles Godot TranslationServer localization workflows, CSV translation files,
## and locale switching.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func scaffold_csv(params: Dictionary) -> Dictionary:
	var path: String = params.get("path", "res://localization.csv")
	if not path.begins_with("res://"):
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "Path must begin with res://")

	var languages: Array = params.get("languages", ["en", "es", "fr", "de", "ja", "zh"])
	if languages.is_empty():
		languages = ["en"]

	var header_line := "keys," + ",".join(languages)
	var sample_entries: Array[String] = [
		header_line,
		"ui_start,Start,Iniciar,Commencer,Starten,開始,开始",
		"ui_quit,Quit,Salir,Quitter,Beenden,終了,退出",
		"ui_options,Options,Opciones,Options,Optionen,設定,选项",
		"ui_back,Back,Atrás,Retour,Zurück,戻る,返回",
	]

	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to create CSV at %s: error %d" % [path, FileAccess.get_open_error()])

	for line in sample_entries:
		file.store_line(line)
	file.close()

	## Register translation CSV in ProjectSettings under internationalization/locale/translations
	var current_translations: PackedStringArray = ProjectSettings.get_setting("internationalization/locale/translations", PackedStringArray())
	var path_found := false
	for t in current_translations:
		if t == path:
			path_found = true
			break

	if not path_found:
		current_translations.append(path)
		ProjectSettings.set_setting("internationalization/locale/translations", current_translations)
		var err := ProjectSettings.save()
		if err != OK:
			push_warning("Failed to persist translations setting: " + str(err))

	return {
		"data": {
			"path": path,
			"languages": languages,
			"starter_keys": ["ui_start", "ui_quit", "ui_options", "ui_back"],
			"registered_in_settings": true
		}
	}


func add_entry(params: Dictionary) -> Dictionary:
	var path: String = params.get("path", "res://localization.csv")
	var key: String = params.get("key", "").strip_edges()
	var translations: Dictionary = params.get("translations", {})

	if key.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: key")

	if not FileAccess.file_exists(path):
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "Translation file not found at %s" % path)

	var read_file := FileAccess.open(path, FileAccess.READ)
	if read_file == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to read CSV at %s" % path)

	var lines: Array[String] = []
	while not read_file.eof_reached():
		var l := read_file.get_line()
		if not l.is_empty() or not read_file.eof_reached():
			lines.append(l)
	read_file.close()

	if lines.is_empty():
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Empty CSV file at %s" % path)

	var header := lines[0].split(",")
	if header.size() < 2 or header[0].strip_edges() != "keys":
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "Invalid CSV header at %s. Expected 'keys,lang1,lang2...'" % path)

	var lang_indices: Dictionary = {}
	for i in range(1, header.size()):
		lang_indices[header[i].strip_edges()] = i

	var key_found := false
	for line_idx in range(1, lines.size()):
		var parts := lines[line_idx].split(",")
		if parts.size() > 0 and parts[0].strip_edges() == key:
			key_found = true
			var updated_parts: Array[String] = []
			for p in parts:
				updated_parts.append(p)
			while updated_parts.size() < header.size():
				updated_parts.append("")
			for lang in translations.keys():
				if lang_indices.has(lang):
					var col: int = lang_indices[lang]
					updated_parts[col] = str(translations[lang])
			lines[line_idx] = ",".join(updated_parts)
			break

	if not key_found:
		var new_row: Array[String] = [key]
		for i in range(1, header.size()):
			var lang := header[i].strip_edges()
			new_row.append(str(translations.get(lang, "")))
		lines.append(",".join(new_row))

	var write_file := FileAccess.open(path, FileAccess.WRITE)
	if write_file == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to write CSV at %s" % path)
	for l in lines:
		write_file.store_line(l)
	write_file.close()

	return {
		"data": {
			"path": path,
			"key": key,
			"updated_existing": key_found,
			"translations": translations
		}
	}


func get_locales(params: Dictionary = {}) -> Dictionary:
	var loaded_locales: PackedStringArray = TranslationServer.get_loaded_locales()
	var current_locale: String = TranslationServer.get_locale()
	var all_locales: PackedStringArray = TranslationServer.get_all_languages()

	var configured_translations: PackedStringArray = ProjectSettings.get_setting("internationalization/locale/translations", PackedStringArray())

	return {
		"data": {
			"current_locale": current_locale,
			"loaded_locales": Array(loaded_locales),
			"configured_translation_files": Array(configured_translations),
			"total_all_languages_count": all_locales.size()
		}
	}


func set_locale(params: Dictionary) -> Dictionary:
	var locale: String = params.get("locale", "").strip_edges()
	if locale.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: locale")

	var old_locale: String = TranslationServer.get_locale()
	TranslationServer.set_locale(locale)
	var new_locale: String = TranslationServer.get_locale()

	return {
		"data": {
			"previous_locale": old_locale,
			"current_locale": new_locale
		}
	}


func translate(params: Dictionary) -> Dictionary:
	var message: String = params.get("message", "").strip_edges()
	var context: String = params.get("context", "")

	if message.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: message")

	var translated: StringName
	if context.is_empty():
		translated = TranslationServer.translate(StringName(message))
	else:
		translated = TranslationServer.translate(StringName(message), StringName(context))

	return {
		"data": {
			"message": message,
			"context": context,
			"translation": str(translated),
			"locale": TranslationServer.get_locale()
		}
	}


func extract_strings(params: Dictionary) -> Dictionary:
	var root_dir: String = params.get("root_dir", "res://")
	var regex := RegEx.new()
	## Matches tr("string") and tr('string')
	regex.compile("tr\\(\\s*[\"']([^\"']+)[\"']\\s*\\)")

	var results: Dictionary = {}
	var total_found := 0

	var queue: Array[String] = [root_dir]
	while not queue.is_empty():
		var dir_path: String = queue.pop_front()
		var dir := DirAccess.open(dir_path)
		if dir == null:
			continue
		dir.list_dir_begin()
		var item := dir.get_next()
		while not item.is_empty():
			if not item.begins_with("."):
				var full_item := dir_path.path_join(item)
				if dir.current_is_dir():
					queue.append(full_item)
				elif full_item.ends_with(".gd") or full_item.ends_with(".tscn"):
					var file := FileAccess.open(full_item, FileAccess.READ)
					if file != null:
						var text := file.get_as_text()
						file.close()
						for m in regex.search_all(text):
							var key := m.get_string(1)
							if not results.has(key):
								results[key] = []
							results[key].append(full_item)
							total_found += 1
			item = dir.get_next()
		dir.list_dir_end()

	return {
		"data": {
			"root_dir": root_dir,
			"unique_keys_count": results.size(),
			"total_occurrences": total_found,
			"keys": results
		}
	}
