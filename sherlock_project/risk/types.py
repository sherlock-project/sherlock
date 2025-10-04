"""Risk module data structures.

Provides common dataclasses that are shared between the risk analyzers and the
rest of the Sherlock code base.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional


@dataclass(slots=True)
class RiskSignal:
    """Trace data that contributed to a risk decision."""

    source: str
    message: str
    weight: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "message": self.message,
            "weight": self.weight,
        }


@dataclass(slots=True)
class RiskAssessment:
    """Normalized representation of a risk verdict."""

    label: str
    score: Optional[float] = None
    confidence: Optional[float] = None
    signals: List[RiskSignal] = field(default_factory=list)

    def add_signal(self, signal: RiskSignal) -> None:
        self.signals.append(signal)

    @property
    def has_signals(self) -> bool:
        return bool(self.signals)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "label": self.label,
            "score": self.score,
            "confidence": self.confidence,
        }
        if self.signals:
            data["signals"] = [signal.to_dict() for signal in self.signals]
        return data


@dataclass(slots=True)
class RiskConfig:
    """Runtime configuration accepted by the risk engine."""

    global_threshold: float = 0.6
    default_label: str = "unknown"
    labels: Mapping[str, str] = field(default_factory=dict)
    site_overrides: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)

    def label_for(self, label_key: str) -> str:
        return self.labels.get(label_key, label_key)

    def site_hint(self, site_name: str) -> Mapping[str, Any]:
        return self.site_overrides.get(site_name, {})

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "RiskConfig":
        return cls(
            global_threshold=float(payload.get("global_threshold", 0.6)),
            default_label=str(payload.get("default_label", "unknown")),
            labels=payload.get("labels", {}),
            site_overrides=payload.get("site_overrides", {}),
        )


def merge_hints(*hint_sets: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    """Merge multiple hint dictionaries, later values winning."""

    merged: Dict[str, Any] = {}
    for hints in hint_sets:
        if not hints:
            continue
        for key, value in hints.items():
            merged[key] = value
    return merged
