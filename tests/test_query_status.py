import pytest
from sherlock_project.result import QueryStatus, QueryResult

# White-box (Branch Coverage with some Statement Coverage) tests, complemented by black-box logic

@pytest.mark.parametrize("member, expected_str", [
    (QueryStatus.CLAIMED,   "Claimed"),
    (QueryStatus.AVAILABLE, "Available"),
    (QueryStatus.UNKNOWN,   "Unknown"),
    (QueryStatus.ILLEGAL,   "Illegal"),
])
def test_str_returns_human_readable_value(member, expected_str):
    assert str(member) == expected_str

def test_query_result_stores_status_and_context():
    result = QueryResult(
        username="johndoe",
        site_name="GitHub",
        site_url_user="https://github.com/johndoe",
        status=QueryStatus.CLAIMED,
    )
    assert result.status == QueryStatus.CLAIMED
    assert result.context is None

def test_query_result_stores_explicit_context():
    result = QueryResult(
        username="johndoe",
        site_name="GitHub",
        site_url_user="https://github.com/johndoe",
        status=QueryStatus.UNKNOWN,
        context="Timeout Error",
    )
    assert result.status == QueryStatus.UNKNOWN
    assert result.context == "Timeout Error"

def test_enum_members_are_singletons():
    a = QueryStatus.CLAIMED
    b = QueryStatus["CLAIMED"]
    assert a is b