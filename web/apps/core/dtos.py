from dataclasses import dataclass
from typing import Literal, Optional, List

@dataclass
class SiteResult:
    site_name: str
    url: str
    status: Literal["found", "not_found", "error", "timeout"]
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None

@dataclass
class SearchRequest:
    username: str
    sites: Optional[List[str]] = None
    timeout: float = 30.0