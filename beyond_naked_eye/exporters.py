from __future__ import annotations

import csv
import json
from pathlib import Path

from beyond_naked_eye.models import InvestigationSession


def export_session(session: InvestigationSession, fmt: str, out_dir: str = "exports") -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    fmt = fmt.lower()
    target = out / f"{session.name}.{fmt}"

    if fmt == "json":
        target.write_text(json.dumps(session.to_dict(), indent=2), encoding="utf-8")
    elif fmt == "txt":
        lines = [f"Session: {session.name}", ""]
        lines += [f"[{f.category}] {f.title}: {f.value} (confidence={f.confidence:.2f})" for f in session.findings]
        target.write_text("\n".join(lines), encoding="utf-8")
    elif fmt == "csv":
        with target.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["category", "title", "value", "confidence", "severity", "source", "timestamp"])
            for f in session.findings:
                writer.writerow([f.category, f.title, f.value, f.confidence, f.severity, f.source, f.timestamp])
    elif fmt == "html":
        rows = "\n".join(
            f"<tr><td>{f.category}</td><td>{f.title}</td><td>{f.value}</td><td>{f.confidence:.2f}</td></tr>"
            for f in session.findings
        )
        html = f"""<html><body style='background:black;color:#53f7ff;font-family:monospace'>
<h1>BEYOND THE NAKED EYE - {session.name}</h1>
<table border='1' cellpadding='6' cellspacing='0'><tr><th>Category</th><th>Title</th><th>Value</th><th>Confidence</th></tr>{rows}</table>
</body></html>"""
        target.write_text(html, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported export format: {fmt}")

    return target
