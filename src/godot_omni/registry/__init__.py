"""Canonical Operation Registry package."""

from godot_omni.registry.models import (
    CanonicalOperation,
    ExecutionContext,
    LatencyTier,
    OperationCategory,
    OperationExample,
    ParameterDoc,
    ReadWrite,
)
from godot_omni.registry.registry import (
    CanonicalOperationRegistry,
    get_global_registry,
)

__all__ = [
    "CanonicalOperation",
    "CanonicalOperationRegistry",
    "ExecutionContext",
    "LatencyTier",
    "OperationCategory",
    "OperationExample",
    "ParameterDoc",
    "ReadWrite",
    "get_global_registry",
]
