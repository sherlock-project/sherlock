"""
Sherlock Async Engine - Asenkron HTTP motoru
aiohttp ile requests-futures yerine gecis
"""

import asyncio
import aiohttp
import aiofiles
from aiohttp import ClientTimeout, TCPConnector
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from time import monotonic
import json
from pathlib import Path

from sherlock_project.result import QueryStatus, QueryResult
from sherlock_project.sites import SitesInformation
from sherlock_project.notify import QueryNotify


@dataclass
class ScanConfig:
    """Tarama konfigurasyonu"""
    max_concurrent: int = 20
    timeout: float = 10.0
    max_retries: int = 3
    retry_delay: float = 1.0


class AsyncSherlock:
    """Asenkron Sherlock motoru"""

    def __init__(
        self,
        sites: SitesInformation,
        config: ScanConfig = None,
        notifier: Optional[QueryNotify] = None,
        proxy: Optional[str] = None
    ):
        self.sites = sites
        self.config = config or ScanConfig()
        self.notifier = notifier
        self.proxy = proxy
        self.results: List[QueryResult] = []
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager giris"""
        connector = TCPConnector(
            limit=self.config.max_concurrent * 2,
            limit_per_host=5,
            enable_cleanup_closed=True,
            force_close=True,
        )
        timeout = ClientTimeout(total=self.config.timeout)

        self._session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager cikis"""
        if self._session:
            await self._session.close()