import re
from sherlock_project.notify import QueryNotifyPrint
from sherlock_project.result import QueryResult, QueryStatus


def make_result(username, site):
    return QueryResult(
        username=username,
        site_name=site,
        site_url_user=f"https://example.com/{username}",
        status=QueryStatus.CLAIMED,
        query_time=None,
        context=None,
    )


def completed_count(out) -> str:
    match = re.search(r"completed with\x1b\[37m (\d+)", out)
    assert match is not None, f"no 'Search completed with N results' line in: {out!r}"
    return match.group(1)


def test_count_is_per_instance(capsys):
    qn_a = QueryNotifyPrint()
    qn_b = QueryNotifyPrint()

    qn_a.update(make_result("user1", "github"))
    qn_a.update(make_result("user1", "twitter"))
    qn_b.update(make_result("user2", "github"))

    qn_a.finish()
    assert completed_count(capsys.readouterr().out) == "2"

    qn_b.finish()
    assert completed_count(capsys.readouterr().out) == "1"


def test_count_resets_between_username_scans(capsys):
    qn = QueryNotifyPrint()

    qn.update(make_result("user1", "github"))
    qn.update(make_result("user1", "twitter"))
    qn.finish()
    assert completed_count(capsys.readouterr().out) == "2"

    qn.update(make_result("user2", "github"))
    qn.finish()
    assert completed_count(capsys.readouterr().out) == "1"