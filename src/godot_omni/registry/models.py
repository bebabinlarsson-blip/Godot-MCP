"""Canonical Operation Data Models for Godot Omni."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class LatencyTier(str, Enum):
    INSTANT = "instant"           # In-memory dictionary / fast cache
    FRAME_BOUND = "frame_bound"   # Requires next engine frame / idle cycle
    DISK = "disk"                 # Reads or writes filesystem
    IMPORT = "import"             # Triggers asset reimport
    BUILD = "build"               # Project compilation or export
    RUNTIME = "runtime"           # Interacts with running game process
    LONG_JOB = "long_job"         # Asynchronous long-running process


class ExecutionContext(str, Enum):
    EDITOR = "editor"
    RUNTIME = "runtime"
    BOTH = "both"


class ReadWrite(str, Enum):
    READ = "read"
    WRITE = "write"


class OperationCategory(str, Enum):
    CURATED = "curated"
    GENERATED_CLASSDB = "generated_classdb"
    REFLECTION = "reflection"
    UI_AUTOMATION = "ui_automation"
    RUNTIME = "runtime"


@dataclass(frozen=True)
class ParameterDoc:
    name: str
    type_name: str
    description: str
    required: bool = False
    default: Any = None
    enum_values: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "name": self.name,
            "type": self.type_name,
            "description": self.description,
            "required": self.required,
        }
        if self.default is not None:
            data["default"] = self.default
        if self.enum_values:
            data["enum"] = list(self.enum_values)
        return data


@dataclass(frozen=True)
class OperationExample:
    title: str
    params: dict[str, Any]
    result: dict[str, Any]
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "params": self.params,
            "result": self.result,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class CanonicalOperation:
    id: str
    title: str
    description: str
    domain: str
    category: OperationCategory = OperationCategory.CURATED
    read_write: ReadWrite = ReadWrite.READ
    execution_context: ExecutionContext = ExecutionContext.EDITOR
    latency_tier: LatencyTier = LatencyTier.INSTANT
    parameters: tuple[ParameterDoc, ...] = ()
    result_schema: dict[str, Any] = field(default_factory=dict)
    supported_versions: str = ">=4.0"
    aliases: tuple[str, ...] = ()
    examples: tuple[OperationExample, ...] = ()
    handler_info: dict[str, Any] = field(default_factory=dict)
    deprecated: bool = False
    replacement: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "domain": self.domain,
            "category": self.category.value,
            "read_write": self.read_write.value,
            "execution_context": self.execution_context.value,
            "latency_tier": self.latency_tier.value,
            "parameters": [p.to_dict() for p in self.parameters],
            "result_schema": self.result_schema,
            "supported_versions": self.supported_versions,
            "aliases": list(self.aliases),
            "examples": [e.to_dict() for e in self.examples],
            "handler_info": self.handler_info,
            "deprecated": self.deprecated,
            "replacement": self.replacement,
        }
