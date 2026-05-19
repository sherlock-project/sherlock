from __future__ import annotations

import difflib
import hashlib
from collections import Counter
from dataclasses import dataclass

from beyond_naked_eye.models import Finding


@dataclass
class RiskAssessment:
    exposure_risk: float
    scam_probability: float
    bot_probability: float
    fake_identity_score: float
    sockpuppet_score: float


def alias_similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def writing_fingerprint(text: str) -> str:
    norm = " ".join(text.lower().split())
    return hashlib.sha256(norm.encode()).hexdigest()[:16]


def behavioral_pattern(findings: list[Finding]) -> list[Finding]:
    time_buckets = Counter(f.metadata.get("hour", 12) for f in findings if isinstance(f.metadata, dict))
    peak = max(time_buckets, key=time_buckets.get) if time_buckets else 12
    sleep_cycle = "00:00-06:00 UTC" if peak > 16 else "01:00-07:00 UTC"
    return [
        Finding("behavior", "Estimated active hour UTC", str(peak), 0.45),
        Finding("behavior", "Estimated sleep cycle", sleep_cycle, 0.35),
        Finding("behavior", "Timezone inference", "UTC-5 to UTC-8 likely", 0.30),
    ]


def threat_scores(findings: list[Finding]) -> RiskAssessment:
    breach_hits = sum(1 for f in findings if "breach" in f.title.lower())
    duplicate_aliases = sum(1 for f in findings if "alias" in f.title.lower())
    return RiskAssessment(
        exposure_risk=min(1.0, 0.2 + breach_hits * 0.15),
        scam_probability=min(1.0, 0.1 + duplicate_aliases * 0.1),
        bot_probability=0.3,
        fake_identity_score=0.25,
        sockpuppet_score=min(1.0, 0.2 + duplicate_aliases * 0.08),
    )
