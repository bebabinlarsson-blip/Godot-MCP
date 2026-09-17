"""Reflection exports for Godot Omni."""

from godot_omni.reflection.handle_manager import HandleManager, ObjectHandle
from godot_omni.reflection.variant_serializer import (
    VariantType,
    deserialize_variant,
    serialize_variant,
)

__all__ = [
    "HandleManager",
    "ObjectHandle",
    "VariantType",
    "serialize_variant",
    "deserialize_variant",
]
