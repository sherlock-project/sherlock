from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, HttpUrl

class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class ErrorType(str, Enum):
    STATUS_CODE = "status_code"
    MESSAGE = "message"
    RESPONSE_URL = "response_url"

class SiteValidation(BaseModel):
    """Validation rules for checking username existence on a site."""
    error_type: ErrorType = Field(..., description="Method used to detect if username exists")
    error_msg: Optional[str] = Field(
        None,
        description="Error message indicating username doesn't exist (if error_type is 'message')"
    )
    regex_check: Optional[str] = Field(
        None,
        description="Regex pattern for validating usernames before making requests"
    )
    request_method: HTTPMethod = Field(
        HTTPMethod.HEAD,
        description="HTTP method to use for the request"
    )
    request_headers: Optional[Dict[str, str]] = Field(
        None,
        description="Custom headers to include in the request"
    )
    request_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Data to send in the request body (for POST/PUT requests)"
    )
    request_json: Optional[Dict[str, Any]] = Field(
        None,
        description="JSON data to send in the request body"
    )

class SiteInfo(BaseModel):
    """Information about a social media site where usernames are checked."""
    name: str = Field(..., description="Name of the social media site")
    url_main: HttpUrl = Field(..., description="Main URL of the site")
    url_username_format: str = Field(..., description="URL format with {} as username placeholder")
    username_claimed: str = Field(..., description="Example of a claimed username")
    username_unclaimed: str = Field("no_one_would_create_this_username_123",
                                 description="Example of an unclaimed username")
    is_nsfw: bool = Field(False, description="Whether the site contains NSFW content")
    validation: SiteValidation = Field(..., description="Validation rules for this site")

    class Config:
        json_encoders = {
            HttpUrl: lambda v: str(v),
        }
        schema_extra = {
            "example": {
                "name": "GitHub",
                "url_main": "https://github.com/",
                "url_username_format": "https://github.com/{}",
                "username_claimed": "torvalds",
                "username_unclaimed": "no_one_would_create_this_username_123",
                "is_nsfw": False,
                "validation": {
                    "error_type": "status_code",
                    "request_method": "HEAD"
                }
            }
        }