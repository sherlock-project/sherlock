"""
Example usage of Sherlock Pydantic models in a FastAPI application.

This module demonstrates how to use the models in API routes and includes
sample data for testing and development.
"""
from datetime import datetime
from typing import Dict, List

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

# Import our models
from ._base import SiteValidation, SiteInfo
from ._requests import SearchRequest, SiteCreateRequest
from ._responses import CheckResult, ResultStatus, UserResult, SearchResponse
from ._exceptions import (
    SherlockBaseError, 
    create_error_response
)

# Initialize FastAPI app
app = FastAPI(
    title="Sherlock API",
    description="API for checking username availability across social media",
    version="0.1.0"
)

# In-memory storage for demonstration
sites_db: Dict[str, SiteInfo] = {}
search_results: Dict[str, UserResult] = {}

# Sample data for demonstration
SAMPLE_SITE = SiteInfo(
    name="example",
    url_main="https://example.com",
    url_username_format="https://example.com/users/{}",
    username_claimed="admin",
    username_unclaimed="no_one_would_create_this_123",
    validation=SiteValidation(
        error_type="status_code",
        request_method="HEAD"
    )
)

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
async def search_usernames(search: SearchRequest):
    """Search for usernames across multiple sites."""
    results = {}
    total_checks = 0
    
    # For demonstration, we'll just simulate checking the usernames
    for username in search.usernames:
        user_results = {}
        
        # Get sites to check (all if none specified)
        sites_to_check = search.sites if search.sites else list(sites_db.keys())
        
        for site_name in sites_to_check:
            if site_name not in sites_db:
                continue
                
            # Simulate checking the username (in a real app, this would make HTTP requests)
            site = sites_db[site_name]
            is_claimed = username == site.username_claimed
            
            result = CheckResult(
                site_name=site_name,
                site_url=site.url_username_format.format(username),
                status=ResultStatus.CLAIMED if is_claimed else ResultStatus.AVAILABLE,
                http_status=200 if is_claimed else 404,
                response_time=0.5  # Simulated response time
            )
            
            user_results[site_name] = result
            total_checks += 1
        
        results[username] = UserResult(
            username=username,
            results=user_results
        )
    
    # Create and return the response
    return SearchResponse(
        usernames=results,
        total_checks=total_checks,
        success_rate=1.0,  # Simulated success rate
        duration=0.5 * total_checks  # Simulated duration
    )

@app.exception_handler(SherlockBaseError)
async def sherlock_exception_handler(request, exc: SherlockBaseError):
    """Handle Sherlock-specific exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=create_error_response(exc)
    )

def run_example():
    """Run example usage of the models."""
    # Add a sample site
    sites_db["example"] = SAMPLE_SITE
    
    # Create a search request
    search = SearchRequest(
        usernames=["testuser", "admin"],
        sites=["example"],
        timeout=10
    )
    
    # Simulate a search
    print("Running example search...")
    response = search_usernames(search)
    
    # Print results
    print("\nSearch Results:")
    for username, user_result in response.usernames.items():
        print(f"\nUsername: {username}")
        for site_name, result in user_result.results.items():
            print(f"  - {site_name}: {result.status.value}")

if __name__ == "__main__":
    run_example()
