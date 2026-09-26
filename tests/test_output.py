import sys

from sherlock_project import sherlock
from sherlock_project.result import QueryResult, QueryStatus


def test_output_option_writes_text_file_without_txt(monkeypatch, tmp_path):
    output_file = tmp_path / 'results.txt'
    result = QueryResult(
        username='example',
        site_name='Example',
        site_url_user='https://example.com/example',
        status=QueryStatus.CLAIMED,
    )

    def offline(*args, **kwargs):
        raise OSError('offline')

    monkeypatch.setattr(
        sys,
        'argv',
        ['sherlock', '--local', '--output', str(output_file), 'example'],
    )
    monkeypatch.setattr(
        sherlock.requests,
        'get',
        offline,
    )
    monkeypatch.setattr(
        sherlock,
        'sherlock',
        lambda *args, **kwargs: {
            'Example': {
                'status': result,
                'url_user': result.site_url_user,
            }
        },
    )

    sherlock.main()

    assert output_file.read_text() == (
        'https://example.com/example\n'
        'Total Websites Username Detected On : 1\n'
    )
