"""Tests for QueryNotifyPrint result counter behaviour."""
import pytest
from sherlock_project.notify import QueryNotifyPrint
from sherlock_project.result import QueryResult, QueryStatus


def _make_result(status):
    return QueryResult(
        username="testuser",
        site_name="TestSite",
        site_url_user="https://testsite.com/testuser",
        status=status,
    )


class TestResultCounter:
    def test_count_starts_at_zero(self):
        notify = QueryNotifyPrint()
        assert notify._result_count == 0

    def test_count_increments_on_claimed(self):
        notify = QueryNotifyPrint()
        notify.update(_make_result(QueryStatus.CLAIMED))
        notify.update(_make_result(QueryStatus.CLAIMED))
        assert notify._result_count == 2

    def test_count_does_not_increment_on_available(self):
        notify = QueryNotifyPrint()
        notify.update(_make_result(QueryStatus.AVAILABLE))
        assert notify._result_count == 0

    def test_independent_instances_do_not_share_count(self):
        """Two QueryNotifyPrint objects must not share a global counter."""
        n1 = QueryNotifyPrint()
        n2 = QueryNotifyPrint()
        n1.update(_make_result(QueryStatus.CLAIMED))
        n1.update(_make_result(QueryStatus.CLAIMED))
        n1.update(_make_result(QueryStatus.CLAIMED))
        # n2 was never updated — its count must still be 0
        assert n2._result_count == 0

    def test_second_username_count_is_not_cumulative(self):
        """Simulates two separate username scans using separate notify objects."""
        notify1 = QueryNotifyPrint()
        notify1.update(_make_result(QueryStatus.CLAIMED))
        notify1.update(_make_result(QueryStatus.CLAIMED))

        notify2 = QueryNotifyPrint()
        notify2.update(_make_result(QueryStatus.CLAIMED))

        # Each object tracks its own scan independently
        assert notify1._result_count == 2
        assert notify2._result_count == 1
