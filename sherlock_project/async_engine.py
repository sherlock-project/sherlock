"""Sherlock Async Engine Module

Drop-in async replacement for the synchronous sherlock() function.
Uses aiohttp for non-blocking I/O with configurable concurrency,
providing significant speedup over the ThreadPoolExecutor approach.

Usage:
    from sherlock_project.async_engine import sherlock_async
    import asyncio

    results = asyncio.run(sherlock_async(username, site_data, query_notify))

The return value is identical to the synchronous sherlock() function.
"""

import asyncio
import re
from time import monotonic
from typing import Optional

import aiohttp

from sherlock_project.result import QueryStatus, QueryResult
from sherlock_project.notify import QueryNotify



# WAF fingerprints — kept in sync with sherlock.py
WAF_HIT_MSGS = [
    r'.loading-spinner{visibility:hidden}body.no-js .challenge-running{display:none}body.dark{background-color:#222;color:#d9d9d9}body.dark a{color:#fff}body.dark a:hover{color:#ee730a;text-decoration:underline}body.dark .lds-ring div{border-color:#999 transparent transparent}body.dark .font-red{color:#b20f03}body.dark',  # Cloudflare
    r'<span id="challenge-error-text">',  # Cloudflare error page
    r'AwsWafIntegration.forceRefreshToken',  # Cloudfront (AWS)
    r'{return l.onPageView}}),Object.defineProperty(r,"perimeterxIdentifiers",{enumerable:',  # PerimeterX
]

DEFAULT_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"
def interpolate_string(input_object, username):
    """Insert username into placeholders."""
    if isinstance(input_object, str):
        return input_object.replace("{}", username)
    elif isinstance(input_object, dict):
        return {k: interpolate_string(v, username) for k, v in input_object.items()}
    elif isinstance(input_object, list):
        return [interpolate_string(i, username) for i in input_object]
    return input_object

async def check_site(
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    username: str,
    social_network: str,
    net_info: dict,
    query_notify: QueryNotify,
    proxy: Optional[str] = None,
    timeout: int = 60,
) -> tuple[str, dict]:
    """Check a single site for username existence.

    This is the async equivalent of the per-site logic in the synchronous
    sherlock() function. It runs within a semaphore to control concurrency.

    Keyword Arguments:
    session                -- aiohttp ClientSession for making requests.
    semaphore              -- asyncio Semaphore to limit concurrency.
    username               -- String indicating username to check.
    social_network         -- String identifying the social network.
    net_info               -- Dictionary containing site configuration.
    query_notify           -- QueryNotify instance for result callbacks.
    proxy                  -- Optional proxy URL string.
    timeout                -- Request timeout in seconds (default: 60).

    Return Value:
    Tuple of (social_network_name, results_dict) matching the format
    of the synchronous sherlock() function.
    """
    results_site = {"url_main": net_info.get("urlMain")}

    # Build headers
    headers = {"User-Agent": DEFAULT_USER_AGENT}
    if "headers" in net_info:
        headers.update(net_info["headers"])

    # Build URL
    url = interpolate_string(net_info["url"], username.replace(" ", "%20"))

    # Check regex constraint
    regex_check = net_info.get("regexCheck")
    if regex_check and re.search(regex_check, username) is None:
        results_site["status"] = QueryResult(
            username, social_network, url, QueryStatus.ILLEGAL
        )
        results_site["url_user"] = ""
        results_site["http_status"] = ""
        results_site["response_text"] = ""
        query_notify.update(results_site["status"])
        return social_network, results_site

    results_site["url_user"] = url

    # Determine probe URL
    url_probe = net_info.get("urlProbe")
    if url_probe is None:
        url_probe = url
    else:
        url_probe = interpolate_string(url_probe, username)

    # Determine HTTP method and payload
    request_method = net_info.get("request_method", None)
    request_payload = net_info.get("request_payload")
    if request_payload is not None:
        request_payload = interpolate_string(request_payload, username)

    error_type = net_info["errorType"]
    if isinstance(error_type, str):
        error_type = [error_type]

    # Choose method: default to HEAD for status_code checks, GET otherwise
    if request_method is None:
        if "status_code" in error_type:
            method = "HEAD"
        else:
            method = "GET"
    else:
        method = request_method.upper()

    # Redirect handling
    allow_redirects = "response_url" not in error_type

    # Acquire semaphore and make the request
    async with semaphore:
        error_context = None
        start_time = monotonic()

        try:
            client_timeout = aiohttp.ClientTimeout(total=timeout)
            async with session.request(
                method,
                url_probe,
                headers=headers,
                allow_redirects=allow_redirects,
                timeout=client_timeout,
                json=request_payload if method in ("POST", "PUT") else None,
                proxy=proxy,
                ssl=False,
            ) as resp:
                response_time = monotonic() - start_time
                http_status = resp.status
                response_text = await resp.text(errors="replace")

        except aiohttp.ClientProxyConnectionError:
            error_context = "Proxy Error"
            response_time = None
            http_status = "?"
            response_text = ""
        except aiohttp.ClientConnectorError:
            error_context = "Error Connecting"
            response_time = None
            http_status = "?"
            response_text = ""
        except asyncio.TimeoutError:
            error_context = "Timeout Error"
            response_time = None
            http_status = "?"
            response_text = ""
        except aiohttp.ClientError:
            error_context = "Unknown Error"
            response_time = None
            http_status = "?"
            response_text = ""
        except Exception:
            error_context = "General Unknown Error"
            response_time = None
            http_status = "?"
            response_text = ""

    # Determine query status using the same logic as the synchronous version
    query_status = QueryStatus.UNKNOWN

    if error_context is not None:
        pass  # Status stays UNKNOWN, error_context is set

    elif any(hitMsg in response_text for hitMsg in WAF_HIT_MSGS):
        query_status = QueryStatus.WAF

    else:
        if any(
            errtype not in ["message", "status_code", "response_url"]
            for errtype in error_type
        ):
            error_context = f"Unknown error type '{error_type}' for {social_network}"
            query_status = QueryStatus.UNKNOWN
        else:
            if "message" in error_type:
                error_flag = True
                errors = net_info.get("errorMsg")
                if isinstance(errors, str):
                    if errors in response_text:
                        error_flag = False
                else:
                    for error in errors:
                        if error in response_text:
                            error_flag = False
                            break
                if error_flag:
                    query_status = QueryStatus.CLAIMED
                else:
                    query_status = QueryStatus.AVAILABLE

            if "status_code" in error_type and query_status is not QueryStatus.AVAILABLE:
                error_codes = net_info.get("errorCode")
                query_status = QueryStatus.CLAIMED

                if isinstance(error_codes, int):
                    error_codes = [error_codes]

                if error_codes is not None and http_status in error_codes:
                    query_status = QueryStatus.AVAILABLE
                elif isinstance(http_status, int) and (
                    http_status >= 300 or http_status < 200
                ):
                    query_status = QueryStatus.AVAILABLE

            if (
                "response_url" in error_type
                and query_status is not QueryStatus.AVAILABLE
            ):
                if isinstance(http_status, int) and 200 <= http_status < 300:
                    query_status = QueryStatus.CLAIMED
                else:
                    query_status = QueryStatus.AVAILABLE

    # Build and notify result
    result = QueryResult(
        username=username,
        site_name=social_network,
        site_url_user=url,
        status=query_status,
        query_time=response_time,
        context=error_context,
    )
    query_notify.update(result)

    results_site["status"] = result
    results_site["http_status"] = http_status
    results_site["response_text"] = (
        response_text.encode("utf-8", errors="replace")
        if isinstance(response_text, str)
        else response_text
    )

    return social_network, results_site


async def sherlock_async(
    username: str,
    site_data: dict[str, dict[str, str]],
    query_notify: QueryNotify,
    dump_response: bool = False,
    proxy: Optional[str] = None,
    timeout: int = 60,
    max_concurrent: int = 100,
) -> dict[str, dict[str, str | QueryResult]]:
    """Run Sherlock Analysis using async I/O.

    Drop-in replacement for the synchronous sherlock() function with
    an additional max_concurrent parameter for tuning concurrency.

    Keyword Arguments:
    username               -- String indicating username that report
                              should be created against.
    site_data              -- Dictionary containing all of the site data.
    query_notify           -- Object with base type of QueryNotify().
                              This will be used to notify the caller about
                              query results.
    dump_response          -- Boolean to dump raw responses (for debugging).
    proxy                  -- String indicating the proxy URL.
    timeout                -- Time in seconds to wait before timing out request.
                              Default is 60 seconds.
    max_concurrent         -- Maximum number of concurrent requests.
                              Default is 100.

    Return Value:
    Dictionary containing results from report, with the same structure
    as the synchronous sherlock() function.
    """
    query_notify.start(username)

    semaphore = asyncio.Semaphore(max_concurrent)

    connector = aiohttp.TCPConnector(
        limit=max_concurrent,
        limit_per_host=3,
        ttl_dns_cache=300,
        enable_cleanup_closed=True,
    )

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for social_network, net_info in site_data.items():
            task = asyncio.create_task(
                check_site(
                    session=session,
                    semaphore=semaphore,
                    username=username,
                    social_network=social_network,
                    net_info=net_info,
                    query_notify=query_notify,
                    proxy=proxy,
                    timeout=timeout,
                )
            )
            tasks.append(task)

        completed = await asyncio.gather(*tasks, return_exceptions=True)

    # Build results dictionary, skipping any tasks that raised exceptions
    results_total = {}
    for item in completed:
        if isinstance(item, Exception):
            continue
        social_network, results_site = item
        results_total[social_network] = results_site

    return results_total
