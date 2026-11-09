import os
from unittest.mock import patch

from sherlock_project.sites import SitesInformation


def local_manifest_path():
    return os.path.join(
        os.path.dirname(__file__), '../sherlock_project/resources/data.json'
    )


class FakeResponse:
    """Minimal stub of requests.Response for the exclusions download."""

    def __init__(self, status_code, text=''):
        self.status_code = status_code
        self.text = text


def test_do_not_exclude_matches_case_insensitively():
    """do_not_exclude keeps excluded sites regardless of casing, while
    exclusions not named in do_not_exclude are still applied (#3168)."""
    exclusions_body = 'Reddit\nApple Developer\nTwitter\n'
    with patch(
        'sherlock_project.sites.requests.get',
        return_value=FakeResponse(200, exclusions_body),
    ):
        sites = SitesInformation(
            data_file_path=local_manifest_path(),
            do_not_exclude=['reddit', 'apple developer'],
        )
    assert 'Reddit' in sites.sites
    assert 'Apple Developer' in sites.sites
    assert 'Twitter' not in sites.sites


def test_non_200_exclusions_response_warns_and_keeps_sites(capsys):
    """A non-200 exclusions response warns and continues without
    exclusions, instead of silently leaving false positives in."""
    with patch(
        'sherlock_project.sites.requests.get',
        return_value=FakeResponse(403),
    ):
        sites = SitesInformation(data_file_path=local_manifest_path())
    captured = capsys.readouterr()
    assert 'Warning: Could not load exclusions' in captured.out
    assert 'Reddit' in sites.sites
    assert 'Twitter' in sites.sites
