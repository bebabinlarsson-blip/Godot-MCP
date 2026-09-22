@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles cryptographic operations, secure random bytes, RSA key generation,
## self-signed X509 certificates, and file/string hashing.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection
var _crypto: Crypto


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection
	_crypto = Crypto.new()


func hash_file(params: Dictionary) -> Dictionary:
	var file_path: String = params.get("file_path", "")
	var algo: String = params.get("algorithm", "sha256").to_lower()

	if file_path.is_empty():
		return {"error": "file_path is required", "code": ErrorCodes.INVALID_PARAMS}

	if not file_path.begins_with("res://") and not file_path.begins_with("user://"):
		file_path = "res://" + file_path

	if not FileAccess.file_exists(file_path):
		return {"error": "File does not exist: %s" % file_path, "code": ErrorCodes.RESOURCE_NOT_FOUND}

	var ctx := HashingContext.new()
	var hash_type := HashingContext.HASH_SHA256
	if algo == "sha1":
		hash_type = HashingContext.HASH_SHA1
	elif algo == "md5":
		hash_type = HashingContext.HASH_MD5

	var err := ctx.start(hash_type)
	if err != OK:
		return {"error": "Failed to initialize HashingContext", "code": ErrorCodes.INTERNAL_ERROR}

	var f := FileAccess.open(file_path, FileAccess.READ)
	if f == null:
		return {"error": "Failed to open file: %s" % file_path, "code": ErrorCodes.INTERNAL_ERROR}

	while f.get_position() < f.get_length():
		var chunk := f.get_buffer(65536)
		if chunk.is_empty():
			break
		ctx.update(chunk)

	var digest := ctx.finish()
	return {
		"success": true,
		"file_path": file_path,
		"algorithm": algo,
		"digest": digest.hex_encode()
	}


func hash_string(params: Dictionary) -> Dictionary:
	var content: String = params.get("content", "")
	var algo: String = params.get("algorithm", "sha256").to_lower()

	var digest_hex := ""
	match algo:
		"md5":
			digest_hex = content.md5_text()
		"sha1":
			var ctx := HashingContext.new()
			ctx.start(HashingContext.HASH_SHA1)
			ctx.update(content.to_utf8_buffer())
			digest_hex = ctx.finish().hex_encode()
		_:
			digest_hex = content.sha256_text()

	return {
		"success": true,
		"algorithm": algo,
		"digest": digest_hex
	}


func generate_random_bytes(params: Dictionary) -> Dictionary:
	var size: int = int(params.get("size", 32))
	if size < 1: size = 1
	if size > 1048576: size = 1048576

	var format: String = params.get("format", "hex").to_lower()
	var bytes := _crypto.generate_random_bytes(size)

	var output_str := ""
	if format == "base64":
		output_str = Marshalls.raw_to_base64(bytes)
	else:
		output_str = bytes.hex_encode()

	return {
		"success": true,
		"size": size,
		"format": format,
		"output": output_str
	}


func generate_rsa_key(params: Dictionary) -> Dictionary:
	var key_size: int = int(params.get("key_size", 2048))
	if key_size not in [1024, 2048, 4096]:
		key_size = 2048

	var save_path: String = params.get("save_path", "")
	var key := _crypto.generate_rsa(key_size)
	if key == null:
		return {"error": "Failed to generate RSA key", "code": ErrorCodes.INTERNAL_ERROR}

	var saved := false
	if not save_path.is_empty():
		if not save_path.begins_with("res://") and not save_path.begins_with("user://"):
			save_path = "res://" + save_path
		var err := key.save(save_path)
		if err == OK:
			saved = true

	return {
		"success": true,
		"key_size": key_size,
		"saved": saved,
		"save_path": save_path if saved else ""
	}


func generate_self_signed_cert(params: Dictionary) -> Dictionary:
	var key_path: String = params.get("key_path", "")
	var cert_save_path: String = params.get("cert_save_path", "")
	var common_name: String = params.get("common_name", "localhost")
	var issuer_name: String = params.get("issuer_name", "GodotMCP")

	var key: CryptoKey = null
	if not key_path.is_empty():
		if not key_path.begins_with("res://") and not key_path.begins_with("user://"):
			key_path = "res://" + key_path
		key = CryptoKey.new()
		var load_err := key.load(key_path)
		if load_err != OK:
			return {"error": "Failed to load CryptoKey from: %s" % key_path, "code": ErrorCodes.INTERNAL_ERROR}
	else:
		key = _crypto.generate_rsa(2048)

	var cert := _crypto.generate_self_signed_certificate(key, "CN=" + common_name + ",O=" + issuer_name)
	if cert == null:
		return {"error": "Failed to generate self-signed certificate", "code": ErrorCodes.INTERNAL_ERROR}

	var saved := false
	if not cert_save_path.is_empty():
		if not cert_save_path.begins_with("res://") and not cert_save_path.begins_with("user://"):
			cert_save_path = "res://" + cert_save_path
		var save_err := cert.save(cert_save_path)
		if save_err == OK:
			saved = true

	return {
		"success": true,
		"common_name": common_name,
		"issuer_name": issuer_name,
		"saved": saved,
		"cert_save_path": cert_save_path if saved else ""
	}


func hmac_digest(params: Dictionary) -> Dictionary:
	var key_str: String = params.get("key", "")
	var msg_str: String = params.get("message", "")
	var algo: String = params.get("algorithm", "sha256").to_lower()

	var hash_type := HashingContext.HASH_SHA256
	if algo == "sha1":
		hash_type = HashingContext.HASH_SHA1
	elif algo == "md5":
		hash_type = HashingContext.HASH_MD5

	var key_bytes := key_str.to_utf8_buffer()
	var msg_bytes := msg_str.to_utf8_buffer()
	var digest := _crypto.hmac_digest(hash_type, key_bytes, msg_bytes)

	return {
		"success": true,
		"algorithm": algo,
		"digest": digest.hex_encode()
	}
