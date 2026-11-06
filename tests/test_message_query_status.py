"""Offline unit tests for message-type query status detection."""

from sherlock_project.result import QueryStatus
from sherlock_project.sherlock import check_message_query_status


def test_available_when_not_found_message_present():
    assert (
        check_message_query_status('{"valid":true}', '"valid":true', 200)
        == QueryStatus.AVAILABLE
    )


def test_claimed_when_message_absent_and_response_ok():
    assert (
        check_message_query_status('{"status":"success"}', '"valid":true', 200)
        == QueryStatus.CLAIMED
    )


def test_unknown_on_server_error_instead_of_false_claimed():
    # 502 body lacks the "not found" message; must not be reported as Claimed.
    # Regression for https://github.com/sherlock-project/sherlock/issues/2950
    assert (
        check_message_query_status("Bad Gateway", '"valid":true', 502)
        == QueryStatus.UNKNOWN
    )


def test_supports_list_of_error_messages():
    assert (
        check_message_query_status("user not found", ["no such user", "not found"], 200)
        == QueryStatus.AVAILABLE
    )
