import os
import pytest
from sherlock_project import sherlock
from sherlock_project.result import QueryResult, QueryStatus
from tests.sherlock_interactives import Interactives, InteractivesSubprocessError

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


def test_folderoutput_honored_by_xlsx_and_csv(tmp_path, monkeypatch):
    out_dir = str(tmp_path / "custom_output")
    dummy_results = {
        "ExampleSite": {
            "url_main": "https://example.com",
            "url_user": "https://example.com/user/testuser",
            "status": QueryResult(
                "testuser",
                "ExampleSite",
                "https://example.com/user/testuser",
                QueryStatus.CLAIMED,
                query_time=0.5,
            ),
            "http_status": 200,
        }
    }
    monkeypatch.setattr(sherlock, "sherlock", lambda *args, **kwargs: dummy_results)
    monkeypatch.setattr(sherlock, "check_for_parameter", lambda u: False)
    test_args = [
        "sherlock",
        "--local",
        "--folderoutput",
        out_dir,
        "--txt",
        "--csv",
        "--xlsx",
        "testuser",
    ]
    monkeypatch.setattr("sys.argv", test_args)
    sherlock.main()

    assert (tmp_path / "custom_output" / "testuser.txt").is_file()
    assert (tmp_path / "custom_output" / "testuser.csv").is_file()
    assert (tmp_path / "custom_output" / "testuser.xlsx").is_file()
    assert not os.path.exists("testuser.xlsx")

