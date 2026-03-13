from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl

from ._base import SiteValidation, SiteInfo

class SearchRequest(BaseModel):
    """Request model for searching usernames across multiple sites."""
    usernames: List[str] = Field(
        ...,
        min_items=1,
        max_items=50,
        description="List of usernames to search for"
    )
    sites: Optional[List[str]] = Field(
        None,
        description="Specific sites to check (defaults to all)"
    )
    include_nsfw: bool = Field(
        False,
        description="Include NSFW sites in the search"
    )
    timeout: int = Field(
        10,
        ge=1,
        le=60,
        description="Request timeout in seconds"
    )
    use_tor: bool = Field(
        False,
        description="Route requests through Tor network"
    )
    unique_tor: bool = Field(
        False,
        description="Use a new Tor circuit for each request"
    )
    proxy: Optional[HttpUrl] = Field(
        None,
        description="Proxy URL to use for requests"
    )

    class Config:
        schema_extra = {
            "example": {
                "usernames": ["example"],
                "sites": ["github", "twitter"],
                "include_nsfw": False,
                "timeout": 10,
                "use_tor": False
            }
        }

class SiteCreateRequest(BaseModel):
    """Request model for adding a new site to check."""
    name: str = Field(..., min_length=2, max_length=100)
    url_main: HttpUrl
    url_username_format: str
    username_claimed: str
    username_unclaimed: Optional[str] = "no_one_would_create_this_username_123"
    is_nsfw: bool = False
    validation: SiteValidation

class SiteUpdateRequest(BaseModel):
    """Request model for updating an existing site."""
    url_main: Optional[HttpUrl] = None
    url_username_format: Optional[str] = None
    username_claimed: Optional[str] = None
    username_unclaimed: Optional[str] = None
    is_nsfw: Optional[bool] = None
    validation: Optional[SiteValidation] = None

class BulkImportRequest(BaseModel):
    """Request model for bulk importing sites."""
    sites: Dict[str, SiteInfo] = Field(
        ...,
        description="Dictionary of site names to site information"
    )
    overwrite: bool = Field(
        False,
        description="Overwrite existing sites with the same name"
    )

class ExportFormat(str, Enum):
    """Supported export formats for search results."""
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"

class ExportRequest(BaseModel):
    """Request model for exporting search results."""
    format: ExportFormat = Field(
        ExportFormat.JSON,
        description="Output format for the export"
    )
    include_all: bool = Field(
        False,
        description="Include all results (including not found) in the export"
    )