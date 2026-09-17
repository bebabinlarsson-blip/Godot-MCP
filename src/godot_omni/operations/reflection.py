"""Universal Object Reflection Operations (ClassDB Inspection, Object Handles, Method Calling)."""

from __future__ import annotations

from godot_omni.operations.builder import op
from godot_omni.registry.models import (
    CanonicalOperation,
    OperationCategory,
    ReadWrite,
)


def get_reflection_operations() -> list[CanonicalOperation]:
    ops: list[CanonicalOperation] = [
        op(
            "api.search_classes",
            "Search Godot Engine ClassDB",
            "Search all available engine classes by name substring or base class filter.",
            "api",
            category=OperationCategory.REFLECTION,
            read_write=ReadWrite.READ,
            params=[
                ("query", "string", "Class name substring", False, "", []),
                ("inherits", "string", "Base class filter (e.g. Node, Control, Resource)", False, "", []),
            ],
            aliases=["search_classes", "classdb_search"],
        ),
        op(
            "api.get_class",
            "Get Class Documentation & Metadata",
            "Retrieve complete ClassDB reflection data for a class including inheritance, methods, properties, and signals.",
            "api",
            category=OperationCategory.REFLECTION,
            read_write=ReadWrite.READ,
            params=[("class_name", "string", "Godot class name (e.g. Node3D, CharacterBody3D)", True, None, [])],
            aliases=["get_class_info", "classdb_get_class"],
        ),
        op(
            "api.list_methods",
            "List Methods of Class",
            "List method signatures, argument types, and return types exposed by ClassDB for a class.",
            "api",
            category=OperationCategory.REFLECTION,
            read_write=ReadWrite.READ,
            params=[
                ("class_name", "string", "Target class name", True, None, []),
                ("include_inherited", "boolean", "Include methods inherited from base classes", False, True, []),
            ],
            aliases=["class_list_methods", "api_list_methods"],
        ),
        op(
            "api.list_properties",
            "List Properties of Class",
            "List property names, types, hint strings, and usage flags exposed by ClassDB for a class.",
            "api",
            category=OperationCategory.REFLECTION,
            read_write=ReadWrite.READ,
            params=[
                ("class_name", "string", "Target class name", True, None, []),
                ("include_inherited", "boolean", "Include inherited properties", False, True, []),
            ],
            aliases=["class_list_properties", "api_list_properties"],
        ),
        op(
            "api.list_signals",
            "List Signals of Class",
            "List signals and parameter signatures declared on a class in ClassDB.",
            "api",
            category=OperationCategory.REFLECTION,
            read_write=ReadWrite.READ,
            params=[("class_name", "string", "Target class name", True, None, [])],
            aliases=["class_list_signals", "api_list_signals"],
        ),
        op(
            "api.call_static",
            "Call Engine Static Method",
            "Invoke a static ClassDB method on a Godot singleton or class (e.g. Engine, Time, OS).",
            "api",
            category=OperationCategory.REFLECTION,
            read_write=ReadWrite.WRITE,
            params=[
                ("class_name", "string", "Target class name", True, None, []),
                ("method", "string", "Static method name", True, None, []),
                ("args", "array", "Arguments list", False, [], []),
            ],
            aliases=["call_static_method", "api_call_static"],
        ),
        op(
            "api.construct",
            "Instantiate Object and Create Handle",
            "Instantiate any constructible Godot engine class or Resource, returning a stable session object handle ('obj://session/id').",
            "api",
            category=OperationCategory.REFLECTION,
            read_write=ReadWrite.WRITE,
            params=[
                ("class_name", "string", "Godot class name to instantiate", True, None, []),
                ("properties", "object", "Optional initial property values", False, {}, []),
            ],
            aliases=["construct_object", "api_construct"],
        ),
        op(
            "object.call_method",
            "Call Method on Object Handle",
            "Invoke an arbitrary method on an instantiated Godot object using its session handle.",
            "object",
            category=OperationCategory.REFLECTION,
            read_write=ReadWrite.WRITE,
            params=[
                ("handle", "string", "Object handle URI ('obj://...')", True, None, []),
                ("method", "string", "Method name to invoke", True, None, []),
                ("args", "array", "Arguments list", False, [], []),
            ],
            aliases=["object_call_method", "call_handle_method"],
        ),
        op(
            "object.get_property",
            "Get Property on Object Handle",
            "Read a property value from an instantiated object via its session handle.",
            "object",
            category=OperationCategory.REFLECTION,
            read_write=ReadWrite.READ,
            params=[
                ("handle", "string", "Object handle URI", True, None, []),
                ("property", "string", "Property name to read", True, None, []),
            ],
            aliases=["object_get_property"],
        ),
        op(
            "object.set_property",
            "Set Property on Object Handle",
            "Write a property value to an instantiated object via its session handle.",
            "object",
            category=OperationCategory.REFLECTION,
            read_write=ReadWrite.WRITE,
            params=[
                ("handle", "string", "Object handle URI", True, None, []),
                ("property", "string", "Property name to write", True, None, []),
                ("value", "any", "Value to assign", True, None, []),
            ],
            aliases=["object_set_property"],
        ),
        op(
            "object.release_handle",
            "Release Object Handle",
            "Release an object handle and allow the underlying engine instance to be freed.",
            "object",
            category=OperationCategory.REFLECTION,
            read_write=ReadWrite.WRITE,
            params=[("handle", "string", "Object handle URI to release", True, None, [])],
            aliases=["object_release_handle"],
        ),
    ]
    return ops
