"""Risk analysis entry points for Sherlock."""
from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Optional

from sherlock_project.risk.types import (
    RiskAssessment,
    RiskConfig,
    RiskSignal,
    merge_hints,
)

logger = logging.getLogger(__name__)


class BaseRiskDetector(ABC):
    """Simple interface for detectors used by the aggregated analyzer."""

    @abstractmethod
    def evaluate(
        self,
        username: str,
        site_name: str,
        response_text: Optional[str],
        site_metadata: Mapping[str, Any],
    ) -> Optional[RiskAssessment]:
        raise NotImplementedError


class HeuristicRiskDetector(BaseRiskDetector):
    """Lightweight detector that scores accounts using text heuristics."""

    def __init__(self, config: RiskConfig, global_hints: Optional[Mapping[str, Any]] = None):
        self._config = config
        self._global_hints = dict(global_hints or {})

    def evaluate(
        self,
        username: str,
        site_name: str,
        response_text: Optional[str],
        site_metadata: Mapping[str, Any],
    ) -> Optional[RiskAssessment]:
        hints = merge_hints(
            self._global_hints.get("default", {}),
            self._global_hints.get(site_name, {}),
            site_metadata.get("riskHints") or {},
            self._config.site_hint(site_name) or {},
        )
        if not hints:
            return None

        text = (response_text or "").lower()
        if not text:
            return None

        total_weight = 0.0
        greatest_signal = 0.0
        label_key: Optional[str] = hints.get("label")
        signals: List[RiskSignal] = []

        for keyword_hint in hints.get("keywords", []):
            pattern = keyword_hint.get("pattern")
            if not pattern:
                continue
            weight = float(keyword_hint.get("weight", 0.2))
            label_hint = keyword_hint.get("label")
            if pattern.lower() in text:
                total_weight += weight
                greatest_signal = max(greatest_signal, weight)
                if label_hint:
                    label_key = label_hint
                signals.append(
                    RiskSignal(
                        source="keyword",
                        message=f"matched keyword '{pattern}'",
                        weight=weight,
                    )
                )

        for regex_hint in hints.get("regex", []):
            pattern = regex_hint.get("pattern")
            if not pattern:
                continue
            try:
                compiled = re.compile(pattern, flags=re.IGNORECASE)
            except re.error:
                logger.debug("Invalid regex in risk hints for %s: %s", site_name, pattern)
                continue
            weight = float(regex_hint.get("weight", 0.3))
            label_hint = regex_hint.get("label")
            if compiled.search(text):
                total_weight += weight
                greatest_signal = max(greatest_signal, weight)
                if label_hint:
                    label_key = label_hint
                signals.append(
                    RiskSignal(
                        source="regex",
                        message=f"matched pattern '{pattern}'",
                        weight=weight,
                    )
                )

        threshold = float(hints.get("threshold", self._config.global_threshold))
        if total_weight <= 0:
            return None

        score = min(1.0, total_weight)
        confidence = min(1.0, greatest_signal + score / 2)
        label = self._config.label_for(label_key) if label_key else self._config.default_label
        assessment = RiskAssessment(label=label, score=score, confidence=confidence)
        for signal in signals:
            assessment.add_signal(signal)
        if score < threshold:
            # Treat as low-risk if the computed score does not meet threshold.
            assessment.label = self._config.label_for("low") if "low" in self._config.labels else self._config.default_label
        return assessment


class RiskAnalyzer:
    """Aggregates multiple detectors and returns the strongest verdict."""

    def __init__(self, detectors: Iterable[BaseRiskDetector], config: RiskConfig):
        self._detectors = list(detectors)
        self._config = config

    def evaluate(
        self,
        username: str,
        site_name: str,
        response_text: Optional[str],
        site_metadata: Mapping[str, Any],
    ) -> Optional[RiskAssessment]:
        best_assessment: Optional[RiskAssessment] = None
        for detector in self._detectors:
            try:
                assessment = detector.evaluate(username, site_name, response_text, site_metadata)
            except Exception:  # pragma: no cover - guard for third-party detectors
                logger.exception("Risk detector %s failed", detector.__class__.__name__)
                continue
            if assessment is None:
                continue
            if best_assessment is None:
                best_assessment = assessment
                continue

            best_score = best_assessment.score or 0.0
            score = assessment.score or 0.0
            if score > best_score:
                best_assessment = assessment
        return best_assessment


def _load_json(path: Path) -> Mapping[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Risk configuration file '{path}' not found")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_risk_analyzer(
    enabled: bool,
    config_path: Optional[str],
    site_data: Mapping[str, Any],
) -> Optional[RiskAnalyzer]:
    """Factory used by the CLI to build a risk analyzer instance."""

    if not enabled:
        return None

    config = RiskConfig()
    global_hints: Mapping[str, Any] = {}
    detectors: List[BaseRiskDetector] = []

    if config_path:
        payload = _load_json(Path(config_path))
        config = RiskConfig.from_mapping(payload.get("config", payload))
        global_hints = payload.get("hints", {})

    # Combine site level hints declared in the manifest.
    detectors.append(HeuristicRiskDetector(config=config, global_hints=global_hints))

    multimodal_detector = _maybe_create_multimodal_detector(config, global_hints)
    if multimodal_detector is not None:
        detectors.append(multimodal_detector)

    return RiskAnalyzer(detectors=detectors, config=config)


def _maybe_create_multimodal_detector(
    config: RiskConfig,
    global_hints: Mapping[str, Any],
) -> Optional[BaseRiskDetector]:
    """Create a multimodal detector if optional dependencies are present."""

    try:  # pragma: no cover - optional dependency, exercised via integration tests
        import importlib

        onnxruntime = importlib.import_module("onnxruntime")  # noqa: F401
        transformers = importlib.import_module("transformers")  # noqa: F401
    except ModuleNotFoundError:
        logger.debug("Multimodal risk detection disabled (missing optional deps)")
        return None

    model_hint = None
    if isinstance(global_hints, Mapping):
        multimodal_section = global_hints.get("multimodal", {})
        if isinstance(multimodal_section, Mapping):
            model_hint = multimodal_section.get("model")

    if not model_hint:
        return None

    class MultimodalRiskDetector(BaseRiskDetector):
        def evaluate(
            self,
            username: str,
            site_name: str,
            response_text: Optional[str],
            site_metadata: Mapping[str, Any],
        ) -> Optional[RiskAssessment]:
            logger.debug(
                "Multimodal detector placeholder invoked for %s on %s", username, site_name
            )
            # Placeholder implementation: return low confidence indicator to encourage
            # implementers to provide a concrete model.
            assessment = RiskAssessment(
                label=config.label_for("ai"),
                score=0.5,
                confidence=0.2,
            )
            assessment.add_signal(
                RiskSignal(
                    source="multimodal",
                    message="Optional multimodal detector not fully configured.",
                    weight=0.1,
                )
            )
            return assessment

    return MultimodalRiskDetector()
