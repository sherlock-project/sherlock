import pytest
from sherlock_project import sherlock
from sherlock_project.result import QueryResult, QueryStatus
from sherlock_interactives import Interactives
from sherlock_interactives import InteractivesSubprocessError

def test_remove_nsfw(sites_obj):
    nsfw_target: str = 'Xvideos'
    assert nsfw_target in {site.name: site.information for site in sites_obj}
    sites_obj.remove_nsfw_sites()
    assert nsfw_target not in {site.name: site.information for site in sites_obj}


# Parametrized sites should *not* include Motherless, which is acting as the control
@pytest.mark.parametrize('nsfwsites', [
    ['Xvideos'],
    ['Xvideos', 'Erome'],
])
def test_nsfw_explicit_selection(sites_obj, nsfwsites):
    for site in nsfwsites:
        assert site in {site.name: site.information for site in sites_obj}
    sites_obj.remove_nsfw_sites(do_not_remove=nsfwsites)
    for site in nsfwsites:
        assert site in {site.name: site.information for site in sites_obj}
        assert 'Motherless' not in {site.name: site.information for site in sites_obj}

def test_wildcard_username_expansion():
    assert sherlock.check_for_parameter('test{?}test') is True
    assert sherlock.check_for_parameter('test{.}test') is False
    assert sherlock.check_for_parameter('test{}test') is False
    assert sherlock.check_for_parameter('testtest') is False
    assert sherlock.check_for_parameter('test{?test') is False
    assert sherlock.check_for_parameter('test?}test') is False
    assert sherlock.multiple_usernames('test{?}test') == ["test_test" , "test-test" , "test.test"]


@pytest.mark.parametrize('cliargs', [
    '',
    '--site urghrtuight --egiotr',
    '--',
])
def test_no_usernames_provided(cliargs):
    with pytest.raises(InteractivesSubprocessError, match=r"error: the following arguments are required: USERNAMES"):
        Interactives.run_cli(cliargs)


@pytest.fixture()
def offline_sherlock_main(monkeypatch):
    """Stub out sherlock() and all network access so main() runs fully offline"""
    def fake(username, site_data, query_notify, **kw):
        return {'Example': {
            'url_main': 'https://example.com',
            'url_user': f'https://example.com/{username}',
            'status': QueryResult(username, 'Example', f'https://example.com/{username}', QueryStatus.CLAIMED),
            'http_status': 200,
            'response_text': b'',
        }}

    monkeypatch.setattr(sherlock, 'sherlock', fake)
    monkeypatch.setattr(sherlock.requests, 'get', lambda *a, **kw: (_ for _ in ()).throw(RuntimeError('offline')))


def test_txt_report_write_failure_is_fail_soft(tmp_path, monkeypatch, offline_sherlock_main, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr('sys.argv', [
        'sherlock',
        '--local',
        '--txt',
        'a/b',
        'ok1',
    ])
    sherlock.main()
    captured = capsys.readouterr()
    assert "ERROR: Failed to write TXT report for 'a/b'" in captured.out
    assert (tmp_path / 'ok1.txt').exists()
    assert 'Total Websites Username Detected On : 1' in (tmp_path / 'ok1.txt').read_text()
    assert 'Search completed with' in captured.out


def test_csv_report_write_failure_is_fail_soft(tmp_path, monkeypatch, offline_sherlock_main, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr('sys.argv', [
        'sherlock',
        '--local',
        '--csv',
        'a/b',
        'ok1',
    ])
    sherlock.main()
    captured = capsys.readouterr()
    assert "ERROR: Failed to write CSV report for 'a/b'" in captured.out
    csv_lines = (tmp_path / 'ok1.csv').read_text().splitlines()
    assert csv_lines[0] == 'username,name,url_main,url_user,exists,http_status,response_time_s'
    assert csv_lines[1].startswith('ok1,Example')
    assert 'Search completed with' in captured.out


def test_xlsx_report_write_failure_is_fail_soft(tmp_path, monkeypatch, offline_sherlock_main, capsys):
    captured = {}

    def fake_to_excel(self, path, *args, **kwargs):
        if 'a/b' in path:
            raise OSError('disk full')
        captured['ok1_path'] = path

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sherlock.pd.DataFrame, 'to_excel', fake_to_excel)
    monkeypatch.setattr('sys.argv', [
        'sherlock',
        '--local',
        '--xlsx',
        'a/b',
        'ok1',
    ])
    sherlock.main()
    out = capsys.readouterr().out
    assert "ERROR: Failed to write XLSX report for 'a/b'" in out
    assert captured['ok1_path'].endswith('ok1.xlsx')
    assert 'Search completed with' in out
