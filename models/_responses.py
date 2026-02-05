from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field, HttpUrl

from ._base import SiteInfo

class ResultStatus(str, Enum):
    """Possible statuses for a username check result."""
    CLAIMED = "claimed"
    AVAILABLE = "available"
    UNKNOWN = "unknown"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"

class CheckResult(BaseModel):
    """Result of checking a single username on a single site."""
    site_name: str = Field(..., description="Name of the social media site")
    site_url: str = Field(..., description="URL of the user's profile")
    status: ResultStatus = Field(..., description="Status of the username check")
    http_status: Optional[int] = Field(
        None,
        description="HTTP status code of the response"
    )
    response_time: Optional[float] = Field(
        None,
        description="Response time in seconds"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if the check failed"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the check was performed"
    )

class UserResult(BaseModel):
    """Results for a single username across multiple sites."""
    username: str = Field(..., description="The username that was checked")
    results: Dict[str, CheckResult] = Field(
        default_factory=dict,
        description="Mapping of site names to check results"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the search was performed"
    )

    @property
    def claimed_count(self) -> int:
        """Number of sites where the username is claimed."""
        return sum(1 for r in self.results.values() if r.status == ResultStatus.CLAIMED)

class SearchResponse(BaseModel):
    """Response model for username search operations."""
    usernames: Dict[str, UserResult] = Field(
        ...,
        description="Mapping of usernames to their results"
    )
    total_checks: int = Field(
        ...,
        description="Total number of site checks performed"
    )
    success_rate: float = Field(
        ...,
        ge=0,
        le=1,
        description="Ratio of successful checks to total checks"
    )
    duration: float = Field(
        ...,
        ge=0,
        description="Total search duration in seconds"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the search"
    )

class SiteResponse(SiteInfo):
    """Extended site information with additional metadata."""
    is_active: bool = Field(
        True,
        description="Whether the site is currently being checked"
    )
    last_checked: Optional[datetime] = Field(
        None,
        description="When the site was last checked"
    )
    success_rate: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Historical success rate of checks"
    )

class StatsResponse(BaseModel):
    """System statistics and metrics."""
    total_sites: int = Field(..., description="Total number of configured sites")
    active_sites: int = Field(..., description="Number of active sites")
    total_checks: int = Field(..., description="Total checks performed")
    success_rate: float = Field(..., description="Overall success rate")
    uptime: float = Field(..., description="Service uptime in seconds")
    last_updated: datetime = Field(..., description="When stats were last updated")
    site_stats: Dict[str, Dict[str, Union[int, float]]] = Field(
        default_factory=dict,
        description="Per-site statistics"
    )

class ExportResponse(BaseModel):
    """Response model for export operations."""
    export_id: str = Field(..., description="Unique ID for the export")
    format: str = Field(..., description="Export format")
    url: Optional[HttpUrl] = Field(
        None,
        description="URL to download the exported file"
    )
    expires_at: Optional[datetime] = Field(
        None,
        description="When the export will expire"
    )
    status: str = Field(..., description="Export status")
    size: Optional[int] = Field(
        None,
        ge=0,
        description="Size of the exported file in bytes"
    )