from unittest.mock import patch
from sherlock_project.sherlock import sherlock
from sherlock_project.notify import QueryNotify
from sherlock_project.result import QueryStatus, QueryResult


def test_sherlock_handles_unicode_decode_error_gracefully():
    """Test that Sherlock does not crash when a UnicodeDecodeError occurs."""
    error_to_raise: UnicodeDecodeError = UnicodeDecodeError('utf-8', b'\xe9', 0, 1, 'invalid continuation byte')

    with patch('concurrent.futures.Future.result', side_effect=error_to_raise):
        username: str = "tést-usér"
        site_data: dict[str, dict[str, str]] = {
            "ExampleSite": {
                "url": "https://www.example.com/{}",
                "errorType": "status_code"
            }
        }
        query_notify: QueryNotify = QueryNotify()

        results: dict[str, dict[str, str | QueryResult]] = sherlock(
            username=username,
            site_data=site_data,
            query_notify=query_notify
        )

        site_result: dict[str, str | QueryResult] = results["ExampleSite"]
        assert site_result is not None, "Results dictionary should contain the site"

        status_object = site_result["status"]

        assert status_object.status == QueryStatus.UNKNOWN, "The site status should be UNKNOWN"
        assert "Unicode Decode Error" in str(status_object.context), "The context should mention the specific error"
