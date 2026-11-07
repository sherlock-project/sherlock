import json
import sys
from types import SimpleNamespace

import pytest
from sherlock_interactives import Interactives, InteractivesSubprocessError

from sherlock_project import sherlock

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


@pytest.mark.parametrize(
    "manifest",
    [
        {},
        {
            "Example": {
                "url": "https://example.invalid/users/{}",
                "urlMain": "https://example.invalid",
                "username_claimed": "fixture",
                "errorType": "status_code",
                "isNSFW": True,
                "regexCheck": "^fixture$",
            },
        },
    ],
    ids=["empty-manifest", "all-sites-filtered"],
)
def test_no_sites_available(tmp_path, monkeypatch, capsys, manifest):
    manifest_path = tmp_path / "sites.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    release = SimpleNamespace(text=json.dumps({"tag_name": f"v{sherlock.__version__}"}))
    monkeypatch.setattr(sherlock.requests, "get", lambda *args, **kwargs: release)
    monkeypatch.setattr(sherlock.signal, "signal", lambda *args: None)
    monkeypatch.setattr(
        sys, "argv",
        ["sherlock", "--json", str(manifest_path), "--ignore-exclusions", "example"],
    )

    with pytest.raises(SystemExit) as error:
        sherlock.main()

    assert error.value.code == 1
    assert "No sites available to search" in capsys.readouterr().out
