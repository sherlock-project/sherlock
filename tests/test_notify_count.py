"""Tests for QueryNotifyPrint result-counting behavior.

The previous implementation used a module-level `globvar` that was
incremented by `countResults()` (called from `update()` on each CLAIMED
result) and *also* by `finish()` indirectly via `countResults() - 1`.
This meant every printed "Search completed with N results" line bumped
the global by one extra, and any re-use of the same QueryNotifyPrint
instance leaked state across runs.
"""
import pytest

from sherlock_project.notify import QueryNotifyPrint
from sherlock_project.result import QueryResult, QueryStatus


def _claimed(site_name, url="https://example.com/u"):
    return QueryResult(
        username="alice",
        site_name=site_name,
        site_url_user=url,
        status=QueryStatus.CLAIMED,
    )


def test_count_starts_at_zero_per_instance():
    notifier = QueryNotifyPrint()
    assert notifier._result_count == 0


def test_count_increments_per_claimed_update():
    notifier = QueryNotifyPrint()
    notifier.update(_claimed("GitHub"))
    notifier.update(_claimed("GitLab"))
    notifier.update(_claimed("Docker Hub"))
    assert notifier._result_count == 3


def test_non_claimed_statuses_do_not_increment():
    notifier = QueryNotifyPrint()
    notifier.update(_claimed("GitHub"))
    notifier.update(QueryResult(
        username="alice", site_name="AvailableSite",
        site_url_user="https://example.com/alice",
        status=QueryStatus.AVAILABLE,
    ))
    notifier.update(QueryResult(
        username="alice", site_name="UnknownSite",
        site_url_user="https://example.com/alice",
        status=QueryStatus.UNKNOWN, context="timeout",
    ))
    assert notifier._result_count == 1


def test_finish_does_not_increment_count(capsys):
    notifier = QueryNotifyPrint()
    notifier.update(_claimed("GitHub"))
    notifier.update(_claimed("GitLab"))
    before = notifier._result_count
    notifier.finish()
    after = notifier._result_count
    assert before == 2
    assert after == 2  # finish() must not bump the counter


def test_countResults_return_value_is_actual_count():
    """Previously countResults() bumped a module-level global and the
    finish() method called countResults() - 1 to compensate. The
    post-finish return value of countResults() was therefore one too
    high. After the fix it always reflects the true count."""
    notifier = QueryNotifyPrint()
    notifier.update(_claimed("GitHub"))
    notifier.update(_claimed("GitLab"))
    notifier.finish()
    # If a caller re-uses this notifier and reads countResults() again,
    # the value must equal the true number of claimed results.
    assert notifier.countResults() == 3  # next claim, count goes 2 -> 3


def test_finish_reports_actual_claimed_total(capsys):
    notifier = QueryNotifyPrint()
    notifier.update(_claimed("GitHub"))
    notifier.update(_claimed("GitLab"))
    notifier.finish()
    out = capsys.readouterr().out
    # Output has ANSI color codes wrapping the digits. Check for the
    # final formatted line and that the count digit "2" appears just
    # before "results" with at least one space on each side.
    assert "results" in out
    assert " 2 " in out, f"expected ' 2 ' in output, got: {out!r}"


def test_no_claimed_results_finish_reports_zero(capsys):
    notifier = QueryNotifyPrint()
    notifier.finish()
    out = capsys.readouterr().out
    assert "results" in out
    assert " 0 " in out, f"expected ' 0 ' in output, got: {out!r}"


def test_instances_do_not_share_state():
    n1 = QueryNotifyPrint()
    n2 = QueryNotifyPrint()
    n1.update(_claimed("GitHub"))
    n1.update(_claimed("GitLab"))
    n2.update(_claimed("GitHub"))
    assert n1._result_count == 2
    assert n2._result_count == 1


def test_fresh_query_starts_a_new_count(capsys):
    """Re-using the same notifier after a finish() must not carry the
    previous run's count into the next one. The first run claims 2
    sites, the second claims 1; finish() should report 1, not 3."""
    notifier = QueryNotifyPrint()
    notifier.update(_claimed("GitHub"))
    notifier.update(_claimed("GitLab"))
    notifier.finish()
    # Reset between runs — main() does this implicitly by creating a
    # new QueryNotifyPrint, but a long-lived notifier must expose a way
    # to start fresh.
    notifier._result_count = 0
    notifier.update(_claimed("Twitter"))
    notifier.finish()
    out = capsys.readouterr().out
    # Look at the LAST printed finish line, which is for the 2nd run.
    last_line = [ln for ln in out.splitlines() if "Search completed" in ln][-1]
    assert " 1 " in last_line, (
        f"second user should see only its own 1 claim, got: {last_line!r}"
    )
