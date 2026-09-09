import pytest
from sherlock_project import sherlock
from sherlock_project.notify import QueryNotify
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


def test_sherlock_does_not_mutate_input_site_data(monkeypatch):
    class FakeResponse:
        status_code = 404
        text = ""
        encoding = "UTF-8"
        elapsed = None

    class FakeFuture:
        def result(self):
            return FakeResponse()

    class FakeFuturesSession:
        def __init__(self, *args, **kwargs):
            pass

        def head(self, **kwargs):
            return FakeFuture()

        get = head
        post = head
        put = head

    monkeypatch.setattr(sherlock.requests, "session", lambda: object())
    monkeypatch.setattr(sherlock, "SherlockFuturesSession", FakeFuturesSession)
    site_data = {
        "Example": {
            "urlMain": "https://example.com",
            "url": "https://example.com/{}",
            "errorType": "status_code",
            "errorCode": 404,
        }
    }
    original_site_data = {name: dict(info) for name, info in site_data.items()}

    sherlock.sherlock(
        username="alice",
        site_data=site_data,
        query_notify=QueryNotify(),
        timeout=1,
    )

    assert site_data == original_site_data


@pytest.mark.parametrize('cliargs', [
    '',
    '--site urghrtuight --egiotr',
    '--',
])
def test_no_usernames_provided(cliargs):
    with pytest.raises(InteractivesSubprocessError, match=r"error: the following arguments are required: USERNAMES"):
        Interactives.run_cli(cliargs)
