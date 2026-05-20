from __future__ import annotations

import random


def scanline_block(width: int = 64, rows: int = 4) -> str:
    """Simple text scanline/noise overlay for terminal panels."""
    lines = []
    for r in range(rows):
        fill = "-" if r % 2 == 0 else " "
        row = "".join(fill if random.random() > 0.08 else "." for _ in range(width))
        lines.append(row)
    return "\n".join(lines)


def terminal_flicker(text: str) -> str:
    if random.random() < 0.15:
        return text.replace("e", "").replace("a", "")
    return text


def rasterize_text(text: str) -> str:
    return "\n".join(line[:80] for line in text.splitlines())
