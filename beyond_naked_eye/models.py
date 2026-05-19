from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


@dataclass
class Finding:
    category: str
    title: str
    value: str
    confidence: float
    severity: str = "info"
    source: str = "public"
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class InvestigationSession:
    name: str
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    findings: list[Finding] = field(default_factory=list)
    timeline: list[dict[str, Any]] = field(default_factory=list)

    def add_findings(self, entries: list[Finding], note: str) -> None:
        self.findings.extend(entries)
        self.updated_at = utc_now_iso()
        self.timeline.append({"at": self.updated_at, "event": note, "count": len(entries)})

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "findings": [f.to_dict() for f in self.findings],
            "timeline": self.timeline,
        }
