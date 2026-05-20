from __future__ import annotations

import hashlib
import json
import mimetypes
import re
import socket
import ssl
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from beyond_naked_eye.models import Finding


def _now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _hashes(path: Path) -> dict[str, str]:
    data = path.read_bytes()
    return {
        "md5": hashlib.md5(data).hexdigest(),
        "sha1": hashlib.sha1(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _entropy(data: bytes) -> float:
    if not data:
        return 0.0
    total = len(data)
    counts = Counter(data)
    import math

    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def analyze_url(url: str) -> list[Finding]:
    findings: list[Finding] = []
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http/https URLs are supported")
    findings.append(Finding("url", "submitted_url", url, 1.0, source="user_authorized"))
    findings.append(Finding("url", "domain", parsed.netloc, 0.95, source="local_parser"))

    try:
        req = Request(url, headers={"User-Agent": "BeyondTheNakedEye/1.1"}, method="GET")
        with urlopen(req, timeout=8) as resp:  # nosec - authorized user URL retrieval only
            headers = dict(resp.headers.items())
            html = resp.read(300000).decode("utf-8", errors="ignore")
            findings.append(Finding("url", "http_status", str(resp.status), 0.98, source="http_response"))
            findings.append(Finding("url", "content_type", headers.get("Content-Type", "unknown"), 0.95))
            title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
            if title_match:
                findings.append(Finding("url", "page_title", title_match.group(1).strip()[:200], 0.85))
            server = headers.get("Server")
            if server:
                findings.append(Finding("url", "server_header", server[:120], 0.8))
            redir = headers.get("Location")
            if redir:
                findings.append(Finding("url", "redirect_location", redir[:200], 0.8, severity="warning"))
    except Exception as exc:
        findings.append(Finding("url", "fetch_error", str(exc), 0.7, severity="warning"))

    if parsed.scheme == "https":
        host = parsed.hostname
        if host:
            try:
                context = ssl.create_default_context()
                with socket.create_connection((host, 443), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=host) as s:
                        cert = s.getpeercert()
                issuer = cert.get("issuer", [])
                issuer_line = ", ".join("=".join(x) for group in issuer for x in group) if issuer else "unknown"
                findings.append(Finding("url", "ssl_issuer", issuer_line[:200], 0.9))
            except Exception as exc:
                findings.append(Finding("url", "ssl_error", str(exc), 0.7, severity="warning"))

    return findings


def analyze_file(path_str: str) -> list[Finding]:
    path = Path(path_str).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    st = path.stat()
    mime, _ = mimetypes.guess_type(str(path))
    data = path.read_bytes()
    findings = [
        Finding("file", "path", str(path), 1.0, source="user_authorized"),
        Finding("file", "size_bytes", str(st.st_size), 1.0),
        Finding("file", "mime", mime or "application/octet-stream", 0.85),
        Finding("file", "modified", datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(), 0.9),
        Finding("file", "entropy", f"{_entropy(data):.4f}", 0.8),
    ]
    for algo, digest in _hashes(path).items():
        findings.append(Finding("hash", algo, digest, 1.0))

    text_sample = data[:100000].decode("utf-8", errors="ignore")
    for token in ("password", "secret", "apikey", "token"):
        if token in text_sample.lower():
            findings.append(Finding("risk", "sensitive_token_pattern", token, 0.65, severity="warning"))

    return findings


def analyze_archive(path_str: str) -> list[Finding]:
    path = Path(path_str).expanduser().resolve()
    findings = analyze_file(path_str)
    if not zipfile.is_zipfile(path):
        findings.append(Finding("archive", "format", "not_zip", 0.9, severity="warning"))
        return findings

    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        findings.append(Finding("archive", "entry_count", str(len(names)), 0.98))
        for n in names[:50]:
            findings.append(Finding("archive_entry", "member", n[:200], 0.75))
        dupes = [name for name, cnt in Counter(names).items() if cnt > 1]
        if dupes:
            findings.append(Finding("risk", "duplicate_entries", ", ".join(dupes)[:200], 0.8, severity="warning"))
        suspicious = [n for n in names if n.lower().endswith((".exe", ".dll", ".js", ".vbs", ".ps1"))]
        if suspicious:
            findings.append(Finding("risk", "suspicious_extensions", ", ".join(suspicious[:20])[:300], 0.8, severity="warning"))
    return findings


def analyze_source(path_str: str) -> list[Finding]:
    findings = analyze_file(path_str)
    p = Path(path_str)
    text = p.read_text(encoding="utf-8", errors="ignore")
    ext = p.suffix.lower()
    findings.append(Finding("source", "language_hint", ext or "unknown", 0.75))
    lines = text.splitlines()
    findings.append(Finding("source", "line_count", str(len(lines)), 0.95))
    regexes = [r"AKIA[0-9A-Z]{16}", r"-----BEGIN (?:RSA|EC|OPENSSH|DSA) PRIVATE KEY-----", r"(?i)api[_-]?key\s*[:=]"]
    for rg in regexes:
        if re.search(rg, text):
            findings.append(Finding("risk", "secret_pattern_detected", rg, 0.8, severity="warning"))
    return findings


def analyze_executable(path_str: str) -> list[Finding]:
    findings = analyze_file(path_str)
    p = Path(path_str)
    data = p.read_bytes()
    findings.append(Finding("executable", "static_analysis_only", "true", 1.0))
    if data[:2] == b"MZ":
        findings.append(Finding("executable", "pe_signature", "MZ", 0.95))
    imports = [token for token in [b"KERNEL32.dll", b"LoadLibrary", b"VirtualAlloc", b"WinExec", b"WS2_32.dll"] if token in data]
    for imp in imports:
        sev = "warning" if imp in {b"WinExec", b"VirtualAlloc", b"WS2_32.dll"} else "info"
        findings.append(Finding("executable", "import_indicator", imp.decode(errors="ignore"), 0.7, severity=sev))
    return findings


def analyze_image(path_str: str) -> list[Finding]:
    findings = analyze_file(path_str)
    p = Path(path_str)
    ext = p.suffix.lower()
    findings.append(Finding("image", "format", ext or "unknown", 0.9))
    # lightweight metadata only without external execution.
    if ext in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}:
        findings.append(Finding("image", "ocr_status", "not_enabled_local_default", 0.9))
    return findings


def export_analysis_bundle(output_path: Path, findings: list[Finding]) -> None:
    payload = {"created_at": _now(), "findings": [f.to_dict() for f in findings]}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
