from types import SimpleNamespace

import pytest
from sherlock_project import sherlock
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



def test_handler_raises_keyboard_interrupt():
    with pytest.raises(KeyboardInterrupt):
        sherlock.handler(None, None)



def test_main_exits_cleanly_on_keyboard_interrupt(monkeypatch, capsys):
    args = SimpleNamespace(
        proxy=None,
        no_color=True,
        output=None,
        folderoutput=None,
        username=["jackson"],
        local=True,
        json_file=None,
        ignore_exclusions=False,
        site_list=[],
        nsfw=True,
        verbose=False,
        print_all=False,
        print_found=True,
        browse=False,
        dump_response=False,
        timeout=1,
        output_txt=False,
        csv=False,
        xlsx=False,
    )

    monkeypatch.setattr(sherlock.ArgumentParser, "parse_args", lambda self: args)
    monkeypatch.setattr(sherlock.signal, "signal", lambda *args, **kwargs: None)
    monkeypatch.setattr(sherlock, "init", lambda *args, **kwargs: None)

    class FakeReleaseResponse:
        text = '{"tag_name": "v' + sherlock.__version__ + '", "html_url": "https://example.com"}'

    monkeypatch.setattr(sherlock.requests, "get", lambda *args, **kwargs: FakeReleaseResponse())

    class FakeSitesInformation:
        def __init__(self, *args, **kwargs):
            pass

        def remove_nsfw_sites(self, do_not_remove=None):
            return None

        def __iter__(self):
            return iter([])

    monkeypatch.setattr(sherlock, "SitesInformation", FakeSitesInformation)

    finish_called = []

    class FakeQueryNotifyPrint:
        def __init__(self, result=None, verbose=False, print_all=False, browse=False):
            self.result = result

        def start(self, message=None):
            return None

        def update(self, result):
            return None

        def finish(self, message="The processing has been finished."):
            finish_called.append(message)

    monkeypatch.setattr(sherlock, "QueryNotifyPrint", FakeQueryNotifyPrint)
    monkeypatch.setattr(sherlock, "sherlock", lambda *args, **kwargs: (_ for _ in ()).throw(KeyboardInterrupt()))

    with pytest.raises(SystemExit) as exit_info:
        sherlock.main()

    assert exit_info.value.code == 130
    assert finish_called == []
    assert "Search interrupted by user." in capsys.readouterr().out
