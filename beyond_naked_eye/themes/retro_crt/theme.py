from __future__ import annotations

from dataclasses import dataclass, field
from rich.theme import Theme


@dataclass(frozen=True)
class CRTTheme:
    name: str = "retro_crt"
    palette: dict[str, str] = field(default_factory=lambda: {
        "bg": "#000000",
        "fg": "#d8d8d8",
        "panel": "#151515",
        "border": "#606060",
        "warn": "#8b2f2f",
        "accent": "#6f806f",
    })

    def rich_theme(self) -> Theme:
        return Theme(
            {
                "crt.fg": self.palette["fg"],
                "crt.dim": "#8a8a8a",
                "crt.panel": self.palette["panel"],
                "crt.warn": self.palette["warn"],
                "crt.accent": self.palette["accent"],
                "crt.border": self.palette["border"],
                "crt.prompt": "bold #cfcfcf",
            }
        )


def get_default_theme() -> CRTTheme:
    return CRTTheme()
