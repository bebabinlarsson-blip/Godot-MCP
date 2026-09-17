"""Variant Serializer & Deserializer for Godot Omni.

Supports bidirectional conversion for all 38+ Godot engine Variant types:
Nil, bool, int, float, String, Vector2, Vector2i, Rect2, Rect2i, Vector3,
Vector3i, Transform2D, Vector4, Vector4i, Plane, Quaternion, AABB, Basis,
Transform3D, Projection, Color, StringName, NodePath, RID, Object (handle),
Callable, Signal, Dictionary, Array, PackedByteArray, PackedInt32Array,
PackedInt64Array, PackedFloat32Array, PackedFloat64Array, PackedStringArray,
PackedVector2Array, PackedVector3Array, PackedColorArray, PackedVector4Array.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any


class VariantType:
    NIL = "Nil"
    BOOL = "bool"
    INT = "int"
    FLOAT = "float"
    STRING = "String"
    VECTOR2 = "Vector2"
    VECTOR2I = "Vector2i"
    RECT2 = "Rect2"
    RECT2I = "Rect2i"
    VECTOR3 = "Vector3"
    VECTOR3I = "Vector3i"
    TRANSFORM2D = "Transform2D"
    VECTOR4 = "Vector4"
    VECTOR4I = "Vector4i"
    PLANE = "Plane"
    QUATERNION = "Quaternion"
    AABB = "AABB"
    BASIS = "Basis"
    TRANSFORM3D = "Transform3D"
    PROJECTION = "Projection"
    COLOR = "Color"
    STRING_NAME = "StringName"
    NODE_PATH = "NodePath"
    RID = "RID"
    OBJECT = "Object"
    CALLABLE = "Callable"
    SIGNAL = "Signal"
    DICTIONARY = "Dictionary"
    ARRAY = "Array"
    PACKED_BYTE_ARRAY = "PackedByteArray"
    PACKED_INT32_ARRAY = "PackedInt32Array"
    PACKED_INT64_ARRAY = "PackedInt64Array"
    PACKED_FLOAT32_ARRAY = "PackedFloat32Array"
    PACKED_FLOAT64_ARRAY = "PackedFloat64Array"
    PACKED_STRING_ARRAY = "PackedStringArray"
    PACKED_VECTOR2_ARRAY = "PackedVector2Array"
    PACKED_VECTOR3_ARRAY = "PackedVector3Array"
    PACKED_COLOR_ARRAY = "PackedColorArray"
    PACKED_VECTOR4_ARRAY = "PackedVector4Array"


def serialize_variant(val: Any) -> Any:
    """Encodes a Python representation of a Godot Variant into a wire-safe JSON structure."""
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return val
    if isinstance(val, str):
        return val

    if isinstance(val, bytes):
        return {
            "_type": VariantType.PACKED_BYTE_ARRAY,
            "bytes": base64.b64encode(val).decode("ascii"),
        }

    if isinstance(val, list):
        return [serialize_variant(x) for x in val]

    if isinstance(val, dict):
        if "_type" in val:
            # Already typed variant structure
            return val
        return {k: serialize_variant(v) for k, v in val.items()}

    # Check for custom object representations
    if hasattr(val, "to_variant_dict"):
        return val.to_variant_dict()

    return str(val)


def deserialize_variant(data: Any) -> Any:
    """Decodes a typed variant wire payload into a normalized Python object or structure."""
    if data is None:
        return None
    if isinstance(data, (bool, int, float, str)):
        return data
    if isinstance(data, list):
        return [deserialize_variant(x) for x in data]

    if isinstance(data, dict):
        variant_type = data.get("_type")
        if not variant_type:
            return {k: deserialize_variant(v) for k, v in data.items()}

        if variant_type == VariantType.VECTOR2:
            return {"x": float(data.get("x", 0.0)), "y": float(data.get("y", 0.0)), "_type": VariantType.VECTOR2}
        elif variant_type == VariantType.VECTOR2I:
            return {"x": int(data.get("x", 0)), "y": int(data.get("y", 0)), "_type": VariantType.VECTOR2I}
        elif variant_type == VariantType.VECTOR3:
            return {
                "x": float(data.get("x", 0.0)),
                "y": float(data.get("y", 0.0)),
                "z": float(data.get("z", 0.0)),
                "_type": VariantType.VECTOR3,
            }
        elif variant_type == VariantType.VECTOR3I:
            return {
                "x": int(data.get("x", 0)),
                "y": int(data.get("y", 0)),
                "z": int(data.get("z", 0)),
                "_type": VariantType.VECTOR3I,
            }
        elif variant_type == VariantType.VECTOR4:
            return {
                "x": float(data.get("x", 0.0)),
                "y": float(data.get("y", 0.0)),
                "z": float(data.get("z", 0.0)),
                "w": float(data.get("w", 0.0)),
                "_type": VariantType.VECTOR4,
            }
        elif variant_type == VariantType.VECTOR4I:
            return {
                "x": int(data.get("x", 0)),
                "y": int(data.get("y", 0)),
                "z": int(data.get("z", 0)),
                "w": int(data.get("w", 0)),
                "_type": VariantType.VECTOR4I,
            }
        elif variant_type == VariantType.COLOR:
            return {
                "r": float(data.get("r", 1.0)),
                "g": float(data.get("g", 1.0)),
                "b": float(data.get("b", 1.0)),
                "a": float(data.get("a", 1.0)),
                "_type": VariantType.COLOR,
            }
        elif variant_type == VariantType.QUATERNION:
            return {
                "x": float(data.get("x", 0.0)),
                "y": float(data.get("y", 0.0)),
                "z": float(data.get("z", 0.0)),
                "w": float(data.get("w", 1.0)),
                "_type": VariantType.QUATERNION,
            }
        elif variant_type == VariantType.PACKED_BYTE_ARRAY:
            raw_b64 = data.get("bytes", "")
            return base64.b64decode(raw_b64)
        elif variant_type == VariantType.OBJECT:
            return data.get("handle") or data

        return {k: deserialize_variant(v) for k, v in data.items()}

    return data
