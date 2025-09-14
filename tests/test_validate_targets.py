import pytest
import rstr

from sherlock_project.sherlock import sherlock
from sherlock_project.notify import QueryNotify
from sherlock_project.result import QueryResult, QueryStatus


FALSE_POSITIVE_ATTEMPTS: int = 2    # Since the usernames are randomly generated, it's POSSIBLE that a real username can be hit


def false_positive_check(sites_info: dict[str, dict[str, str]], site: str, pattern: str) -> QueryStatus:
    """Check if a site is likely to produce false positives."""
    status: QueryStatus = QueryStatus.UNKNOWN

    for _ in range(FALSE_POSITIVE_ATTEMPTS):
        query_notify: QueryNotify = QueryNotify()
        username: str = rstr.xeger(pattern)

        result: QueryResult | str = sherlock(
            username=username,
            site_data=sites_info,
            query_notify=query_notify,
        )[site]['status']

        if not hasattr(result, 'status'):
            raise TypeError(f"Result for site {site} does not have 'status' attribute. Actual result: {result}")
        if type(result.status) is not QueryStatus: # type: ignore
            raise TypeError(f"Result status for site {site} is not of type QueryStatus. Actual type: {type(result.status)}") # type: ignore
        status = result.status # type: ignore

        if status in (QueryStatus.AVAILABLE, QueryStatus.WAF):
            return status

    return status


def false_negative_check(sites_info: dict[str, dict[str, str]], site: str) -> QueryStatus:
    """Check if a site is likely to produce false negatives."""
    status: QueryStatus = QueryStatus.UNKNOWN
    query_notify: QueryNotify = QueryNotify()

    result: QueryResult | str = sherlock(
        username=sites_info[site]['username_claimed'],
        site_data=sites_info,
        query_notify=query_notify,
    )[site]['status']

    if not hasattr(result, 'status'):
            raise TypeError(f"Result for site {site} does not have 'status' attribute. Actual result: {result}")
    if type(result.status) is not QueryStatus: # type: ignore
        raise TypeError(f"Result status for site {site} is not of type QueryStatus. Actual type: {type(result.status)}") # type: ignore
    status = result.status # type: ignore

    return status

@pytest.mark.validate_targets
@pytest.mark.online
class Test_All_Targets:

    def test_manifest_false_pos(self, chunked_sites: dict[str, dict[str, str]]):
        """Iterate through all sites in the manifest to discover possible false-positive inducting targets."""
        pattern: str
        for site in chunked_sites:
            try:
                pattern = chunked_sites[site]['regexCheck']
            except KeyError:
                pattern = r'^[a-zA-Z0-9._-]{7,20}$'
            result: QueryStatus = false_positive_check(chunked_sites, site, pattern)
            assert result is QueryStatus.AVAILABLE, f"{site} produced false positive with pattern {pattern}, result was {result}"

    def test_manifest_false_neg(self, chunked_sites: dict[str, dict[str, str]]):
        """Iterate through all sites in the manifest to discover possible false-negative inducting targets."""
        for site in chunked_sites:
            result: QueryStatus = false_negative_check(chunked_sites, site)
            assert result is QueryStatus.CLAIMED, f"{site} produced false negative, result was {result}"

