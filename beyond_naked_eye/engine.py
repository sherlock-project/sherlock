from __future__ import annotations

import asyncio
from collections import defaultdict

from beyond_naked_eye.models import Finding
from beyond_naked_eye.modules import scanners


class ScanEngine:
    def __init__(self) -> None:
        self.dispatch = {
            "username": scanners.username_scan,
            "email": scanners.email_scan,
            "phone": scanners.phone_scan,
            "name": scanners.name_scan,
            "domain": scanners.domain_scan,
            "address": scanners.address_scan,
            "metadata": scanners.metadata_scan,
            "image": scanners.image_intel_scan,
        }

    async def scan(self, scan_type: str, value: str) -> list[Finding]:
        fn = self.dispatch.get(scan_type)
        if not fn:
            raise ValueError(f"Unsupported scan type: {scan_type}")
        return self.correlate(await fn(value))

    def correlate(self, findings: list[Finding]) -> list[Finding]:
        seen = set()
        buckets = defaultdict(int)
        out = []
        for f in findings:
            k = (f.category, f.value)
            if k in seen:
                continue
            seen.add(k)
            buckets[f.category] += 1
            f.confidence = min(1.0, f.confidence + min(0.2, buckets[f.category] * 0.02))
            out.append(f)
        return out

    async def batch_scan(self, requests: list[tuple[str, str]]) -> list[Finding]:
        rows = await asyncio.gather(*[self.scan(t, v) for t, v in requests])
        return [f for group in rows for f in group]
