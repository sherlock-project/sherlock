import pytest

from sherlock_project.sherlock import sherlock
from sherlock_project.notify import QueryNotify
from sherlock_project.result import QueryStatus

# Regression test for https://github.com/sherlock-project/sherlock/issues/2970
# A username ending in '.' (e.g. "alice.") combined with a subdomain-style
# site template (https://{username}.example.com) used to produce an invalid
# URL (https://alice..example.com) that crashed the request and aborted the
# whole run. It must now be reported as ILLEGAL without raising and without
# making a network request.


def test_trailing_dot_username_is_flagged_illegal():
    site_data = {
        "SubdomainExample": {
            "url": "https://{username}.example.com",
        }
    }
    results = sherlock(
        username="alice.",
        site_data=site_data,
        query_notify=QueryNotify(),
    )
    assert results["SubdomainExample"]["status"].status == QueryStatus.ILLEGAL


def test_leading_dot_username_is_flagged_illegal():
    site_data = {
        "SubdomainExample": {
            "url": "https://{username}.example.com",
        }
    }
    results = sherlock(
        username=".alice",
        site_data=site_data,
        query_notify=QueryNotify(),
    )
    assert results["SubdomainExample"]["status"].status == QueryStatus.ILLEGAL


def test_normal_username_not_flagged_illegal_by_host_check():
    # A valid subdomain username must not be caught by the host check; the
    # request path proceeds normally (no ILLEGAL due to host).
    site_data = {
        "SubdomainExample": {
            "url": "https://{username}.example.com",
        }
    }
    results = sherlock(
        username="alice",
        site_data=site_data,
        query_notify=QueryNotify(),
    )
    assert results["SubdomainExample"]["status"].status != QueryStatus.ILLEGAL
