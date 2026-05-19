from __future__ import annotations

import time


class TTLCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[float, object]] = {}

    def get(self, key: str):
        row = self._store.get(key)
        if not row:
            return None
        expires, value = row
        if time.time() > expires:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: object, ttl: int = 300) -> None:
        self._store[key] = (time.time() + ttl, value)
