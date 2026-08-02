"""
Example usage of Sherlock Pydantic models with async functionality.

This module demonstrates how to use the async Sherlock functionality in a FastAPI application.
It includes sample API routes and demonstrates proper async/await patterns.
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import httpx
from httpx import AsyncClient

from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse

# Import our models
from ._base import SiteInfo
from ._requests import SearchRequest, SiteCreateRequest
from ._responses import CheckResult, ResultStatus, UserResult, SearchResponse
from ._exceptions import (
    SherlockBaseError, 
    create_error_response
)

# Import async search functionality
from sherlock_project.workers.search import search_username
from sherlock_project.notify import QueryNotifyPrint

# Initialize FastAPI app
app = FastAPI(
    title="Sherlock API (Async)",
    description="Async API for checking username availability across social media",
    version="0.1.0"
)

# In-memory storage for demonstration
sites_db: Dict[str, SiteInfo] = {}
search_results: Dict[str, UserResult] = {}

# Sample site for demonstration
SAMPLE_SITE = SiteInfo(
    name="example",
    url_main="https://example.com",
    url_username_format="https://example.com/users/{}",
    username_claimed="admin",
    username_unclaimed="no_one_would_create_this_123",
    validation={
        "error_type": "status_code",
        "request_method": "HEAD"
    }
)

# HTTP client for making requests
class AsyncHTTPClient:
    """Async HTTP client wrapper for making requests."""
    
    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
        
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
            
    async def check_username_available(self, url: str, username: str) -> bool:
        """Check if a username is available at the given URL."""
        if not self.client:
            raise RuntimeError("Client not initialized. Use async with")
            
        try:
            response = await self.client.head(url, follow_redirects=True)
            return response.status_code == 404
        except httpx.RequestError:
            return False

@app.post("/sites/", response_model=SiteInfo, status_code=status.HTTP_201_CREATED)
async def create_site(site: SiteCreateRequest):
    """Add a new site to check."""
    if site.name in sites_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Site '{site.name}' already exists"
        )
    
    # Convert SiteCreateRequest to SiteInfo
    site_info = SiteInfo(
        name=site.name,
        url_main=site.url_main,
        url_username_format=site.url_username_format,
        username_claimed=site.username_claimed,
        username_unclaimed=site.username_unclaimed or f"no_one_would_create_this_{site.name}",
        validation=site.validation
    )
    
    sites_db[site.name] = site_info
    return site_info

@app.get("/sites/{site_name}", response_model=SiteInfo)
async def get_site(site_name: str):
    """Get information about a specific site."""
    if site_name not in sites_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Site '{site_name}' not found"
        )
    return sites_db[site_name]

@app.post("/search/", response_model=SearchResponse)
async def search_usernames(
    search: SearchRequest,
    background_tasks: BackgroundTasks
):
    """Search for usernames across multiple sites asynchronously.
    
    This endpoint demonstrates how to use Sherlock's async functionality
    to check username availability across multiple sites efficiently.
    """
    results = {}
    total_checks = 0
    
    # Initialize notification system
    query_notify = QueryNotifyPrint(verbose=True, print_all=True)
    
    # Convert our site data to the format expected by the search worker
    site_data = {}
    sites_to_check = search.sites if search.sites else list(sites_db.keys())
    
    for site_name in sites_to_check:
        if site_name in sites_db:
            site = sites_db[site_name]
            site_data[site_name] = {
                "url": site.url_main,
                "urlMain": site.url_main,
                "urlProbe": site.url_username_format.format("{" + "}"),
                "errorType": site.validation.error_type,
                "request_method": site.validation.request_method,
                "username_claimed": site.username_claimed,
                "username_unclaimed": site.username_unclaimed,
            }
    
    # Process each username asynchronously
    for username in search.usernames:
        try:
            # Perform the async search
            search_results = await search_username(
                username=username,
                site_data=site_data,
                query_notify=query_notify,
                tor=False,  # Enable Tor if needed
                timeout=search.timeout or 30
            )
            
            # Process the results
            user_results = {}
            for site_name, result in search_results.items():
                if "status" not in result:
                    continue
                    
                status_obj = result["status"]
                user_results[site_name] = CheckResult(
                    site_name=site_name,
                    site_url=result.get("url_user", ""),
                    status=ResultStatus.CLAIMED if status_obj.status == "Claimed" else ResultStatus.AVAILABLE,
                    http_status=result.get("http_status", 0),
                    response_time=status_obj.query_time if hasattr(status_obj, "query_time") else 0,
                    context=status_obj.context if hasattr(status_obj, "context") else None
                )
                total_checks += 1
            
            results[username] = UserResult(
                username=username,
                results=user_results
            )
            
        except Exception as e:
            # Log the error but continue with other usernames
            print(f"Error processing username {username}: {str(e)}")
            results[username] = UserResult(
                username=username,
                results={"error": str(e)},
                error=True
            )
    
    # Calculate success rate (simple implementation)
    success_rate = 1.0 if not results else (
        sum(1 for r in results.values() if not getattr(r, 'error', False)) / len(results)
    )
    
    # Return the response
    return SearchResponse(
        usernames=results,
        total_checks=total_checks,
        success_rate=success_rate,
        duration=0  # In a real app, you'd track actual duration
    )

@app.exception_handler(SherlockBaseError)
async def sherlock_exception_handler(request, exc: SherlockBaseError):
    """Handle Sherlock-specific exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=create_error_response(exc)
    )

async def run_example():
    """Run example usage of the async functionality."""
    # Add a sample site
    sites_db["example"] = SiteInfo(
        name="example",
        url_main="https://example.com",
        url_username_format="https://example.com/users/{}",
        username_claimed="admin",
        username_unclaimed="no_one_would_create_this_123",
        validation={
            "error_type": "status_code",
            "request_method": "HEAD"
        }
    )
    
    # Create a search request
    search = SearchRequest(
        usernames=["testuser", "admin"],
        sites=["example"],
        timeout=10
    )
    
    # Initialize FastAPI test client
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Test the search endpoint
    print("Running example search...")
    response = client.post("/search/", json=search.dict())
    
    if response.status_code == 200:
        results = SearchResponse(**response.json())
        
        # Print results
        print("\nSearch Results:")
        for username, user_result in results.usernames.items():
            print(f"\nUsername: {username}")
            if hasattr(user_result, 'error') and user_result.error:
                print(f"  Error: {user_result.results.get('error', 'Unknown error')}")
            else:
                for site_name, result in user_result.results.items():
                    print(f"  - {site_name}: {result.status.value} (HTTP {result.http_status})")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_example())
