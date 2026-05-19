from __future__ import annotations

import asyncio
from typing import Awaitable, TypeVar

T = TypeVar("T")


class AsyncTaskManager:
    async def gather_limited(self, tasks: list[Awaitable[T]], limit: int = 20) -> list[T]:
        semaphore = asyncio.Semaphore(limit)

        async def _run(task: Awaitable[T]) -> T:
            async with semaphore:
                return await task

        return await asyncio.gather(*[_run(t) for t in tasks])
