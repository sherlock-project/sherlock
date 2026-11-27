import re

from sherlock_project.notify import QueryNotifyPrint
from sherlock_project.result import QueryResult, QueryStatus


def _claimed(site_name: str) -> QueryResult:
    return QueryResult("user", site_name, "https://example.com/user", QueryStatus.CLAIMED)


def _reported_count(output: str) -> int:
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    match = re.search(r"Search completed with (\d+) results", plain)
    assert match is not None, plain
    return int(match.group(1))


def test_finish_reports_count_without_shared_state(capsys):
    first = QueryNotifyPrint()
    first.update(_claimed("First"))
    first.finish()
    assert _reported_count(capsys.readouterr().out) == 1

    second = QueryNotifyPrint()
    second.update(_claimed("Second"))
    second.finish()
    assert _reported_count(capsys.readouterr().out) == 1

    second.finish()
    assert _reported_count(capsys.readouterr().out) == 1
