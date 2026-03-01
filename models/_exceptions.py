from typing import Any, Dict

class SherlockBaseError(Exception):
    """Base exception for all Sherlock errors."""
    def __init__(self, message: str, code: str = None, details: Any = None):
        self.message = message
        self.code = code or "sherlock_error"
        self.details = details
        super().__init__(self.message)

class ValidationError(SherlockBaseError):
    """Raised when input validation fails."""
    def __init__(self, message: str = "Validation failed", details: Any = None):
        super().__init__(message, "validation_error", details)

class RateLimitError(SherlockBaseError):
    """Raised when rate limits are exceeded."""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        self.retry_after = retry_after
        details = {"retry_after": retry_after} if retry_after else None
        super().__init__(message, "rate_limit_exceeded", details)

class SiteError(SherlockBaseError):
    """Base exception for site-specific errors."""
    def __init__(self, site_name: str, message: str, code: str = "site_error", details: Any = None):
        self.site_name = site_name
        message = f"[{site_name}] {message}"
        super().__init__(message, code, details)

class SiteConfigurationError(SiteError):
    """Raised when there's an issue with site configuration."""
    def __init__(self, site_name: str, message: str, details: Any = None):
        super().__init__(site_name, message, "site_configuration_error", details)

class SiteNotSupportedError(SiteError):
    """Raised when a requested site is not supported."""
    def __init__(self, site_name: str):
        super().__init__(site_name, f"Site '{site_name}' is not supported", "site_not_supported")

class SiteTimeoutError(SiteError):
    """Raised when a request to a site times out."""
    def __init__(self, site_name: str, timeout: float):
        message = f"Request timed out after {timeout} seconds"
        super().__init__(site_name, message, "site_timeout", {"timeout": timeout})

class AuthenticationError(SherlockBaseError):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed", details: Any = None):
        super().__init__(message, "authentication_error", details)

class ExportError(SherlockBaseError):
    """Raised when there's an error during export operations."""
    def __init__(self, message: str = "Export failed", details: Any = None):
        super().__init__(message, "export_error", details)

class NotFoundError(SherlockBaseError):
    """Raised when a requested resource is not found."""
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type.capitalize()} '{resource_id}' not found"
        super().__init__(message, "not_found", {"resource_type": resource_type, "resource_id": resource_id})

class ServiceUnavailableError(SherlockBaseError):
    """Raised when a required service is unavailable."""
    def __init__(self, service_name: str, message: str = None):
        message = message or f"Service '{service_name}' is currently unavailable"
        super().__init__(message, "service_unavailable", {"service_name": service_name})

def create_error_response(error: Exception) -> Dict[str, Any]:
    """Convert an exception to a dictionary suitable for API responses."""
    if isinstance(error, SherlockBaseError):
        return {
            "error": {
                "code": error.code,
                "message": str(error),
                "details": error.details
            }
        }
    
    return {
        "error": {
            "code": "internal_error",
            "message": str(error) or "An unexpected error occurred",
            "details": None
        }
    }