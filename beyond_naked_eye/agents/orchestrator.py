from __future__ import annotations

import asyncio
from dataclasses import dataclass

from beyond_naked_eye.analysis.assistant import summarize_findings
from beyond_naked_eye.analysis.intelligence import behavioral_pattern
from beyond_naked_eye.engine import ScanEngine
from beyond_naked_eye.models import Finding


@dataclass
class AgentResult:
    agent: str
    findings: list[Finding]


class MultiAgentOrchestrator:
    def __init__(self) -> None:
        self.engine = ScanEngine()

    async def run(self, target: str, value: str) -> list[AgentResult]:
        plan = [
            ("Social Agent", "username", value),
            ("Domain Agent", "domain", value if target == "domain" else "example.com"),
            ("Metadata Agent", "metadata", value if target == "metadata" else __file__),
            ("Breach Agent", "email", value if target == "email" else f"{value}@example.com"),
            ("Correlation Agent", target, value),
        ]
        async def _exec(agent: str, scan_type: str, scan_value: str) -> AgentResult:
            return AgentResult(agent, await self.engine.scan(scan_type, scan_value))

        results = await asyncio.gather(*[_exec(*p) for p in plan])
        combined = [f for r in results for f in r.findings]
        combined.extend(behavioral_pattern(combined))
        combined.append(Finding("assistant", "AI summary", summarize_findings(combined), 0.65))
        results.append(AgentResult("Timeline Agent", combined[-4:]))
        return results
