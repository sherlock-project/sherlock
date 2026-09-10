import os

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


def test_xlsx_honors_folderoutput(tmp_path, monkeypatch):
    def fake(username, site_data, query_notify, **kw):
        return {'Example': {
            'url_main': 'https://example.com',
            'url_user': f'https://example.com/{username}',
            'status': QueryResult(username, 'Example', f'https://example.com/{username}', QueryStatus.CLAIMED),
            'http_status': 200,
            'response_text': b'',
        }}

    captured = {}

    def spy_to_excel(self, path, *args, **kwargs):
        captured['path'] = path

    out_dir = tmp_path / 'sub'
    monkeypatch.setattr(sherlock, 'sherlock', fake)
    monkeypatch.setattr(sherlock.requests, 'get', lambda *a, **kw: (_ for _ in ()).throw(RuntimeError('offline')))
    monkeypatch.setattr(sherlock.pd.DataFrame, 'to_excel', spy_to_excel)
    monkeypatch.setattr('sys.argv', [
        'sherlock',
        '--local',
        '--xlsx',
        '--folderoutput', str(out_dir),
        'user_folderoutput',
    ])
    sherlock.main()
    assert out_dir.is_dir()
    assert captured['path'] == os.path.join(str(out_dir), 'user_folderoutput.xlsx')
