from __future__ import annotations

from beyond_naked_eye.analysis.intelligence import threat_scores
from beyond_naked_eye.models import Finding


def summarize_findings(findings: list[Finding]) -> str:
    categories = sorted({f.category for f in findings})
    scores = threat_scores(findings)
    return (
        f"Summary: {len(findings)} findings across {', '.join(categories)}. "
        f"Exposure risk={scores.exposure_risk:.2f}, scam probability={scores.scam_probability:.2f}. "
        "Suggested pivots: monitor usernames, track domain changes, and archive profile snapshots."
    )
