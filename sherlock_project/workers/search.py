#! /usr/bin/env python3

"""
Sherlock: Async Worker module for searching usernames

This module contains the core logic for performing the username search on social networks using asyncio and httpx.
"""

import asyncio
import re
from typing import Optional, List, Coroutine

import httpx

from ..result import QueryStatus, QueryResult
from ..notify import QueryNotify
from ..utils.text import interpolate_string


async def search_username(
    username: str,
    site_data: dict,
    query_notify: QueryNotify,
    tor: bool = False,
    unique_tor: bool = False,
    proxy: Optional[str] = None,
    timeout: int = 60,
) -> dict:
    """Run Sherlock Analysis asynchronously.

    Checks for existence of username on various social media sites.

    Args:
        username: Username to search for.
        site_data: Dictionary containing site information.
        query_notify: Object for notifying query results.
        tor: Use Tor for requests.
        unique_tor: Use new Tor circuit for each request.
        proxy: Proxy URL to use.
        timeout: Request timeout in seconds.

    Returns:
        Dictionary containing results from all sites checked.
    """
    query_notify.start(username)
    results_total = {}
    
    # TODO: Investigate async-friendly Tor solutions like httpx-socks
    if tor or unique_tor:
        print("Warning: Async mode does not support Tor yet. Using regular requests.")

    async with httpx.AsyncClient(proxy=proxy, timeout=timeout) as client:
        coroutines: List[Coroutine] = []
        for social_network, net_info in site_data.items():
            results_site = {"url_main": net_info.get("urlMain")}
            
            # Check username against regex if provided
            regex_check = net_info.get("regexCheck")
            if regex_check and not re.search(regex_check, username):
                results_site["status"] = QueryResult(username, social_network, net_info["url"], QueryStatus.ILLEGAL)
                query_notify.update(results_site["status"])
            else:
                coroutine = _make_request(client, username, social_network, net_info)
                coroutines.append(coroutine)

            results_total[social_network] = results_site

        responses = await asyncio.gather(*coroutines, return_exceptions=True)

        for response in responses:
            if isinstance(response, Exception):
                # Handle exceptions during request (e.g., network errors)
                # This part needs more context on how to log or handle these errors
                continue

            social_network = response["social_network"]
            net_info = site_data[social_network]
            result = await _process_response(username, social_network, net_info, response["response"])
            results_total[social_network].update(result)
            query_notify.update(result["status"])
            
    return results_total


async def _make_request(client: httpx.AsyncClient, username: str, social_network: str, net_info: dict) -> dict:
    """Helper function to create and execute a single async request."""
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"}
    if "headers" in net_info:
        headers.update(net_info["headers"])

    url = interpolate_string(net_info["url"], username)
    url_probe = net_info.get("urlProbe")
    if url_probe:
        url_probe = interpolate_string(url_probe, username)
    else:
        url_probe = url

    method = net_info.get("request_method", "GET").upper()
    payload = net_info.get("request_payload")
    if payload:
        payload = interpolate_string(payload, username)

    try:
        if method == "POST":
            response = await client.post(url_probe, headers=headers, data=payload)
        elif method == "HEAD":
            response = await client.head(url_probe, headers=headers)
        else: # Default to GET
            response = await client.get(url_probe, headers=headers)
        return {"response": response, "social_network": social_network}
    except httpx.RequestError as e:
        return {"response": e, "social_network": social_network}


async def _process_response(username: str, social_network: str, net_info: dict, response) -> dict:
    """Helper function to process the response from a site."""
    url = interpolate_string(net_info["url"], username)
    error_type = net_info.get("errorType", "status_code")
    
    if isinstance(response, httpx.RequestError):
        status = QueryResult(username, social_network, url, QueryStatus.ERROR, error_text=str(response))
        return {"status": status, "http_status": "?", "response_text": str(response)}

    status_code = response.status_code
    response_text = response.text

    # Check for WAF blocks
    WAF_HIT_PATTERNS = [
        r'.loading-spinner{visibility:hidden}',
        r'<span id="challenge-error-text">',
        r'AwsWafIntegration.forceRefreshToken',
        r'{return l.onPageView}}),Object.defineProperty'
    ]
    if any(pattern in response_text for pattern in WAF_HIT_PATTERNS):
        status = QueryResult(username, social_network, url, QueryStatus.ERROR, error_text="Cloudflare WAF detected")
        return {"status": status, "http_status": status_code, "response_text": "Cloudflare WAF detected"}

    if error_type == "message":
        error_msg = net_info.get("errorMsg", "")
        if isinstance(error_msg, list):
            if any(msg in response_text for msg in error_msg):
                status = QueryResult(username, social_network, url, QueryStatus.AVAILABLE)
            else:
                status = QueryResult(username, social_network, url, QueryStatus.CLAIMED)
        elif error_msg in response_text:
            status = QueryResult(username, social_network, url, QueryStatus.AVAILABLE)
        else:
            status = QueryResult(username, social_network, url, QueryStatus.AVAILABLE)
    
    elif error_type == "status_code":
        if status_code >= 200 and status_code < 300:
            status = QueryResult(username, social_network, url, QueryStatus.CLAIMED)
        else:
            status = QueryResult(username, social_network, url, QueryStatus.AVAILABLE)
    
    elif error_type == "response_url":
        if response.url == url:
            status = QueryResult(username, social_network, url, QueryStatus.AVAILABLE)
        else:
            status = QueryResult(username, social_network, url, QueryStatus.CLAIMED)
    else:
        # Should not happen, but as a fallback
        status = QueryResult(username, social_network, url, QueryStatus.ERROR, error_text="Unknown error type")

    return {
        "status": status,
        "http_status": status_code,
        "response_text": response_text,
        "url_user": url
    }
