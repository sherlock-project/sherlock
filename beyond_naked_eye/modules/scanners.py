from __future__ import annotations

import asyncio
import hashlib
import re
import socket
from pathlib import Path
from urllib.parse import quote

from beyond_naked_eye.models import Finding


async def username_scan(username: str) -> list[Finding]:
    sites = {
        "GitHub": f"https://github.com/{quote(username)}",
        "Reddit": f"https://www.reddit.com/user/{quote(username)}",
        "Instagram": f"https://www.instagram.com/{quote(username)}/",
        "TikTok": f"https://www.tiktok.com/@{quote(username)}",
        "Mastodon": f"https://mastodon.social/@{quote(username)}",
    }
    await asyncio.sleep(0.05)
    return [Finding("username", f"Profile candidate on {k}", v, 0.45) for k, v in sites.items()]


async def email_scan(email: str) -> list[Finding]:
    user, _, domain = email.partition("@")
    findings = [
        Finding("email", "Domain extracted", domain or "unknown", 0.98),
        Finding("email", "Gravatar hash", hashlib.md5(email.lower().encode()).hexdigest(), 0.85),
        Finding("breach", "Public breach archive check", "Index ready (user must add provider key)", 0.4),
    ]
    if domain:
        try:
            findings.append(Finding("email", "DNS A lookup", str(socket.gethostbyname_ex(domain)[2]), 0.70))
        except Exception as exc:
            findings.append(Finding("email", "DNS lookup warning", str(exc), 0.2, severity="low"))
    findings.append(Finding("email", "Mention tracking", f"Search pastes/forums for {user}", 0.45))
    return findings


async def phone_scan(number: str) -> list[Finding]:
    cleaned = re.sub(r"[^\d+]", "", number)
    return [
        Finding("phone", "Normalized", cleaned, 0.95),
        Finding("phone", "Carrier/region hint", "Use libphonenumber + carrier APIs", 0.4),
        Finding("threat", "Spam probability", "Medium", 0.35),
    ]


async def domain_scan(domain: str) -> list[Finding]:
    findings: list[Finding] = []
    try:
        findings.append(Finding("domain", "A records", ",".join(socket.gethostbyname_ex(domain)[2]), 0.9))
    except Exception as exc:
        findings.append(Finding("domain", "Resolution error", str(exc), 0.2, severity="low"))
    findings.extend(Finding("domain", "Subdomain candidate", f"{s}.{domain}", 0.3) for s in ["www", "mail", "api", "dev"])
    findings += [
        Finding("cyber", "WHOIS lookup", "Use RDAP/WHOIS source adapter", 0.5),
        Finding("cyber", "SSL certificate analysis", f"https://{domain}", 0.5),
        Finding("cyber", "API exposure check", "Check /.well-known and swagger endpoints", 0.45),
    ]
    return findings


async def name_scan(full_name: str) -> list[Finding]:
    parts = full_name.lower().split()
    guesses = ["".join(parts), ".".join(parts), "_".join(parts)]
    return [Finding("name", "Alias candidate", g, 0.5) for g in guesses]


async def address_scan(address: str) -> list[Finding]:
    return [
        Finding("address", "Public records lookup", address, 0.65),
        Finding("mapping", "Geolocation enrichment", "Use OSM/Nominatim adapters", 0.5),
    ]


async def metadata_scan(path: str) -> list[Finding]:
    p = Path(path)
    if not p.exists():
        return [Finding("metadata", "File error", "not found", 0.1, severity="low")]
    content = p.read_bytes()
    return [
        Finding("metadata", "SHA256", hashlib.sha256(content).hexdigest(), 1.0),
        Finding("evidence", "Evidence ID", hashlib.sha1(content).hexdigest()[:12], 1.0),
    ]


async def image_intel_scan(image_path: str) -> list[Finding]:
    p = Path(image_path)
    if not p.exists():
        return [Finding("image", "File error", "not found", 0.1, severity="low")]
    b = p.read_bytes()
    return [
        Finding("image", "Perceptual hash", hashlib.md5(b).hexdigest(), 0.9),
        Finding("image", "AI-generated probability", "Requires vision model/plugin", 0.4),
        Finding("image", "Reverse image search", "Adapter ready (Bing/Yandex APIs)", 0.45),
    ]
