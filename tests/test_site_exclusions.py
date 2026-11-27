"""Explicitly requested excluded sites keep their manifest entry in any casing.

`--site` matching is case-insensitive everywhere else, so asking for an
excluded site as `reddit` or `REDDIT` must behave like `Reddit`: the site is
kept for the request instead of being dropped by the exclusion list.
"""
import json

import pytest

from sherlock_project.sites import SitesInformation

REDDIT_MANIFEST = {
    "Reddit": {
        "urlMain": "https://www.reddit.com/",
        "url": "https://www.reddit.com/user/{}",
        "username_claimed": "reddit",
        "errorType": "status_code",
    }
}


class _ExclusionResponse:
    status_code = 200
    text = "Reddit\nApple Developer\n"


@pytest.fixture()
def local_manifest(tmp_path):
    path = tmp_path / "data.json"
    path.write_text(json.dumps(REDDIT_MANIFEST), encoding="utf-8")
    return str(path)


@pytest.fixture()
def exclusion_list(monkeypatch):
    monkeypatch.setattr(
        "sherlock_project.sites.requests.get",
        lambda *args, **kwargs: _ExclusionResponse(),
    )


@pytest.mark.parametrize("spelling", ["Reddit", "reddit", "REDDIT"])
def test_do_not_exclude_matches_any_case(local_manifest, exclusion_list, spelling):
    sites = SitesInformation(
        data_file_path=local_manifest, do_not_exclude=[spelling]
    )
    assert "Reddit" in sites.sites


def test_exclusion_still_applies_when_not_requested(local_manifest, exclusion_list):
    sites = SitesInformation(data_file_path=local_manifest)
    assert "Reddit" not in sites.sites
