from __future__ import annotations

from pathlib import Path
import json

APPDATA_ROOT = Path.home() / "AppData" / "Roaming" / "BeyondTheNakedEye"
PROGRAM_RUNTIME_DIRS = [
    "modules",
    "themes",
    "assets",
    "cache",
    "database",
    "logs",
    "exports",
    "sessions",
    "plugins",
    "analysis",
    "sandbox",
    "yara_rules",
    "uploads",
    "quarantine",
    "temp_processing",
]
USER_RUNTIME_DIRS = [
    "configs",
    "sessions",
    "cache",
    "settings",
    "history",
    "logs",
]


def ensure_runtime_layout(base_dir: Path) -> None:
    for folder in PROGRAM_RUNTIME_DIRS:
        (base_dir / folder).mkdir(parents=True, exist_ok=True)


def ensure_user_layout() -> None:
    APPDATA_ROOT.mkdir(parents=True, exist_ok=True)
    for folder in USER_RUNTIME_DIRS:
        (APPDATA_ROOT / folder).mkdir(parents=True, exist_ok=True)


def ensure_database_stub(base_dir: Path) -> None:
    db_file = base_dir / "database" / "bne.db"
    db_file.parent.mkdir(parents=True, exist_ok=True)
    db_file.touch(exist_ok=True)


def ensure_default_config() -> None:
    config_path = APPDATA_ROOT / "configs" / "default.json"
    if config_path.exists():
        return
    payload = {
        "theme": "retro_crt",
        "terminal_mode": "monochrome",
        "scanline_overlay": True,
        "warning_color": "muted_red",
    }
    config_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run_first_launch_init(base_dir: Path) -> None:
    ensure_runtime_layout(base_dir)
    ensure_user_layout()
    ensure_database_stub(base_dir)
    ensure_default_config()
