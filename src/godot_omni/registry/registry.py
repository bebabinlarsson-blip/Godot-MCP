"""Canonical Operation Registry for Godot Omni."""

from __future__ import annotations

import difflib
import re
from typing import Any

from godot_omni.registry.models import (
    CanonicalOperation,
    OperationCategory,
    ReadWrite,
)


class CanonicalOperationRegistry:
    """Central registry for all canonical Godot operations."""

    def __init__(self) -> None:
        self._operations: dict[str, CanonicalOperation] = {}
        self._alias_index: dict[str, str] = {}
        self._domain_index: dict[str, list[str]] = {}
        self._category_index: dict[OperationCategory, list[str]] = {
            cat: [] for cat in OperationCategory
        }
        self._token_index: dict[str, set[str]] = {}

    def register(self, op: CanonicalOperation) -> None:
        """Register a canonical operation."""
        self._operations[op.id] = op
        self._alias_index[op.id.lower()] = op.id
        for alias in op.aliases:
            self._alias_index[alias.lower()] = op.id

        if op.domain not in self._domain_index:
            self._domain_index[op.domain] = []
        if op.id not in self._domain_index[op.domain]:
            self._domain_index[op.domain].append(op.id)

        if op.id not in self._category_index[op.category]:
            self._category_index[op.category].append(op.id)

        # Inverted index for fast search
        text = f"{op.id} {op.domain} {op.title} {' '.join(op.aliases)}"
        words = set(re.split(r"[\s_.:/-]+", text.lower()))
        for w in words:
            if len(w) >= 2:
                if w not in self._token_index:
                    self._token_index[w] = set()
                self._token_index[w].add(op.id)

    def register_many(self, ops: list[CanonicalOperation]) -> None:
        for op in ops:
            self.register(op)

    def get(self, id_or_alias: str) -> CanonicalOperation | None:
        """Retrieve operation by canonical ID or alias."""
        norm = id_or_alias.strip().lower()
        if norm in self._alias_index:
            canonical_id = self._alias_index[norm]
            return self._operations.get(canonical_id)
        # Also try replacing dots with underscores or vice versa
        alt = norm.replace(".", "_")
        if alt in self._alias_index:
            return self._operations.get(self._alias_index[alt])
        alt2 = norm.replace("_", ".")
        if alt2 in self._alias_index:
            return self._operations.get(self._alias_index[alt2])
        return None

    # Alias for convenience
    get_operation = get

    def list_all(self) -> list[CanonicalOperation]:
        """Return all registered operations sorted by ID."""
        return sorted(self._operations.values(), key=lambda op: op.id)

    def list_domains(self) -> list[str]:
        """Return sorted list of all active domain names."""
        return sorted(self._domain_index.keys())

    def list_by_domain(self, domain: str) -> list[CanonicalOperation]:
        """Return operations in a given domain."""
        ids = self._domain_index.get(domain, [])
        return [self._operations[i] for i in ids if i in self._operations]

    def stats(self) -> dict[str, Any]:
        """Compute registry statistics."""
        curated_count = len(self._category_index[OperationCategory.CURATED])
        generated_count = len(self._category_index[OperationCategory.GENERATED_CLASSDB])
        ui_count = len(self._category_index[OperationCategory.UI_AUTOMATION])
        runtime_count = len(self._category_index[OperationCategory.RUNTIME])
        reflection_count = len(self._category_index[OperationCategory.REFLECTION])

        total = len(self._operations)
        domains_count = len(self._domain_index)

        return {
            "canonical_operations": total,
            "curated_operations": curated_count,
            "generated_classdb_operations": generated_count,
            "ui_automation_operations": ui_count,
            "runtime_operations": runtime_count,
            "reflection_operations": reflection_count,
            "flat_mcp_tools_available": total,
            "compact_domains_available": domains_count,
            "dynamic_reflection_supported": True,
            "custom_extension_operations": "dynamic",
        }

    get_stats = stats

    def search(
        self,
        query: str,
        *,
        domain: str | None = None,
        read_write: ReadWrite | str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Search operations using keyword relevance scoring and fuzzy ranking."""
        tokens = [t.lower() for t in re.split(r"[\s_.:/-]+", query.strip()) if t]
        if not tokens:
            return []

        # Rapid candidate gathering from index
        candidate_ids: set[str] = set()
        for t in tokens:
            if t in self._token_index:
                candidate_ids.update(self._token_index[t])
            else:
                for k, ids in self._token_index.items():
                    if t in k:
                        candidate_ids.update(ids)

        candidates = [self._operations[cid] for cid in candidate_ids] if candidate_ids else list(self._operations.values())
        results: list[tuple[float, CanonicalOperation]] = []

        rw_filter = None
        if read_write:
            rw_filter = read_write.value if isinstance(read_write, ReadWrite) else str(read_write).lower()

        for op in candidates:
            if domain and op.domain.lower() != domain.lower():
                continue
            if rw_filter and op.read_write.value != rw_filter:
                continue

            score = 0.0
            id_lower = op.id.lower()
            title_lower = op.title.lower()
            desc_lower = op.description.lower()
            domain_lower = op.domain.lower()

            # Exact ID match gets highest priority
            if query.lower() == id_lower or any(query.lower() == a.lower() for a in op.aliases):
                score += 100.0

            # Substring in ID
            if query.lower() in id_lower:
                score += 40.0

            for token in tokens:
                if token in id_lower:
                    score += 25.0
                if token in domain_lower:
                    score += 20.0
                if token in title_lower:
                    score += 15.0
                if token in desc_lower:
                    score += 5.0
                for alias in op.aliases:
                    if token in alias.lower():
                        score += 15.0

            if score > 0:
                results.append((score, op))

        results.sort(key=lambda item: item[0], reverse=True)
        return [
            {
                "score": round(score, 1),
                "operation": op.to_dict(),
            }
            for score, op in results[:limit]
        ]

    def suggest_similar(self, candidate: str, limit: int = 5) -> list[str]:
        """Suggest closest valid canonical IDs for a typo."""
        norm = candidate.strip().lower()
        all_keys = list(self._alias_index.keys())
        matches = difflib.get_close_matches(norm, all_keys, n=limit, cutoff=0.5)
        # Map back to canonical ID
        canonical_matches: list[str] = []
        for m in matches:
            cid = self._alias_index[m]
            if cid not in canonical_matches:
                canonical_matches.append(cid)
        return canonical_matches

    def export_json(self) -> list[dict[str, Any]]:
        """Export full registry to serializable JSON-compatible list."""
        return [op.to_dict() for op in self.list_all()]


_GLOBAL_REGISTRY: CanonicalOperationRegistry | None = None


def get_global_registry() -> CanonicalOperationRegistry:
    """Get or instantiate the process-wide canonical operation registry."""
    global _GLOBAL_REGISTRY
    if _GLOBAL_REGISTRY is None:
        _GLOBAL_REGISTRY = CanonicalOperationRegistry()
        from godot_omni.operations.catalog import populate_registry
        populate_registry(_GLOBAL_REGISTRY)
    return _GLOBAL_REGISTRY
