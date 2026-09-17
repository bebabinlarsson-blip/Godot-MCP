"""Helper builder functions for canonical operations."""

from __future__ import annotations

from typing import Any

from godot_omni.registry.models import (
    CanonicalOperation,
    ExecutionContext,
    LatencyTier,
    OperationCategory,
    OperationExample,
    ParameterDoc,
    ReadWrite,
)


def op(
    id: str,
    title: str,
    description: str,
    domain: str,
    *,
    category: OperationCategory = OperationCategory.CURATED,
    read_write: ReadWrite = ReadWrite.READ,
    execution_context: ExecutionContext = ExecutionContext.EDITOR,
    latency_tier: LatencyTier = LatencyTier.INSTANT,
    params: list[tuple[str, str, str, bool, Any, list[str]]] | None = None,
    result_schema: dict[str, Any] | None = None,
    aliases: list[str] | None = None,
    examples: list[tuple[str, dict[str, Any], dict[str, Any], str]] | None = None,
    handler_info: dict[str, Any] | None = None,
    supported_versions: str = ">=4.0",
) -> CanonicalOperation:
    """Convenience factory for CanonicalOperation."""
    param_docs: list[ParameterDoc] = []
    if params:
        for p in params:
            name = p[0]
            type_name = p[1]
            desc = p[2]
            required = p[3] if len(p) > 3 else False
            default = p[4] if len(p) > 4 else None
            enum_vals = tuple(p[5]) if len(p) > 5 and p[5] else ()
            param_docs.append(
                ParameterDoc(
                    name=name,
                    type_name=type_name,
                    description=desc,
                    required=required,
                    default=default,
                    enum_values=enum_vals,
                )
            )

    example_objs: list[OperationExample] = []
    if examples:
        for ex in examples:
            example_objs.append(
                OperationExample(
                    title=ex[0],
                    params=ex[1],
                    result=ex[2],
                    explanation=ex[3] if len(ex) > 3 else "",
                )
            )

    return CanonicalOperation(
        id=id,
        title=title,
        description=description,
        domain=domain,
        category=category,
        read_write=read_write,
        execution_context=execution_context,
        latency_tier=latency_tier,
        parameters=tuple(param_docs),
        result_schema=result_schema or {},
        supported_versions=supported_versions,
        aliases=tuple(aliases or []),
        examples=tuple(example_objs),
        handler_info=handler_info or {},
    )
