from __future__ import annotations

from collections import defaultdict

from beyond_naked_eye.models import Finding


def build_relationship_ascii(findings: list[Finding]) -> str:
    buckets = defaultdict(list)
    for f in findings:
        buckets[f.category].append(f.value)
    lines = ["[Entity Relationship Tree]"]
    for cat, values in sorted(buckets.items()):
        lines.append(f"|- {cat}")
        for v in values[:8]:
            lines.append(f"|  |- {v}")
    return "\n".join(lines)
