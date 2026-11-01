"""Offline CLI coverage for misspelled --site arguments."""
import sys
from types import SimpleNamespace

import pytest

from sherlock_project import sherlock


def run_site_selection(monkeypatch, capsys, requested, expect_exit=True):
    class FakeSites(list):
        def remove_nsfw_sites(self, **kwargs):
            pass

    sites = FakeSites([
        SimpleNamespace(name=name, information={})
        for name in ['GitHub', 'GitLab', 'Keybase']
    ])
    monkeypatch.setattr(sherlock, 'SitesInformation', lambda *a, **kw: sites)
    monkeypatch.setattr(sherlock.requests, 'get', lambda *a, **kw: SimpleNamespace(
        text='{"tag_name":"v' + sherlock.__version__ + '","html_url":"https://example.org"}'
    ))
    monkeypatch.setattr(sherlock.signal, 'signal', lambda *a: None)
    selected = []
    monkeypatch.setattr(sherlock, 'sherlock', lambda username, data, *a, **kw: selected.append(list(data)) or {})
    requested = [requested] if isinstance(requested, str) else requested
    args = [arg for site in requested for arg in ['--site', site]]
    monkeypatch.setattr(sys, 'argv', ['sherlock', '--local', '--no-color', *args, 'example'])
    if expect_exit:
        with pytest.raises(SystemExit) as error:
            sherlock.main()
        assert error.value.code == 1
        assert not selected
    else:
        sherlock.main()
    return capsys.readouterr().out, selected


@pytest.mark.parametrize('requested', ['GitHbu', 'githbu'])
def test_typo_suggests_canonical_site_name(monkeypatch, capsys, requested):
    output, _ = run_site_selection(monkeypatch, capsys, requested)
    assert 'Desired sites not found' in output
    assert "Did you mean 'GitHub'?" in output


def test_unrelated_site_has_no_suggestions(monkeypatch, capsys):
    output, _ = run_site_selection(monkeypatch, capsys, 'zzzzzzzz')
    assert 'Desired sites not found' in output
    assert 'Did you mean' not in output


def test_valid_case_insensitive_site_has_no_suggestion(monkeypatch, capsys):
    output, selected = run_site_selection(monkeypatch, capsys, 'github', expect_exit=False)
    assert 'Did you mean' not in output
    assert selected == [['GitHub']]


def test_mixed_selection_never_queries_the_suggestion(monkeypatch, capsys):
    output, selected = run_site_selection(monkeypatch, capsys, ['Keybase', 'GitHbu'], expect_exit=False)
    assert "Did you mean 'GitHub'?" in output
    assert selected == [['Keybase']]
