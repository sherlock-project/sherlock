from __future__ import annotations

import json
from pathlib import Path

from beyond_naked_eye.models import Finding, InvestigationSession


class SessionStore:
    def __init__(self, base: str = "sessions") -> None:
        self.base = Path(base)
        self.base.mkdir(parents=True, exist_ok=True)

    def save(self, session: InvestigationSession) -> Path:
        path = self.base / f"{session.name}.json"
        path.write_text(json.dumps(session.to_dict(), indent=2), encoding="utf-8")
        return path

    def load(self, name: str) -> InvestigationSession:
        path = self.base / f"{name}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        session = InvestigationSession(name=payload["name"], created_at=payload["created_at"], updated_at=payload["updated_at"])
        session.findings = [Finding(**item) for item in payload.get("findings", [])]
        session.timeline = payload.get("timeline", [])
        return session
