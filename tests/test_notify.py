from sherlock_project.notify import QueryNotifyPrint
from sherlock_project.result import QueryResult, QueryStatus


def claimed_result():
    return QueryResult(
        username='example',
        site_name='Example',
        site_url_user='https://example.com/example',
        status=QueryStatus.CLAIMED,
    )


def test_result_count_is_scoped_to_each_notifier(capsys):
    first = QueryNotifyPrint()
    first.update(claimed_result())
    first.update(claimed_result())
    first.finish()

    assert ' 2 ' in capsys.readouterr().out
    assert first._result_count == 2

    second = QueryNotifyPrint()
    second.update(claimed_result())
    second.finish()

    assert ' 1 ' in capsys.readouterr().out
    assert second._result_count == 1
