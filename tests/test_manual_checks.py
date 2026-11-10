import json
import os

import pytest

from sherlock_interactives import Interactives
from sherlock_interactives import InteractivesSubprocessError
from sherlock_project.manual_checks import (
    MANUAL_CHECK_SITES,
    build_manual_check_links,
    select_manual_check_sites,
)


def test_all_sites_selected_by_default():
    sites, unknown = select_manual_check_sites([])
    assert [site.name for site in sites] == list(MANUAL_CHECK_SITES)
    assert unknown == []


def test_site_filter_is_case_insensitive_and_deduplicated():
    sites, unknown = select_manual_check_sites(['douyin', 'Douyin', 'NotASite'])
    assert [site.name for site in sites] == ['Douyin']
    assert unknown == ['NotASite']


@pytest.mark.parametrize('username, expected', [
    ('example', 'example'),
    ('山水', '%E5%B1%B1%E6%B0%B4'),
    ('a b/c?d&e#f', 'a%20b%2Fc%3Fd%26e%23f'),
])
def test_username_is_url_encoded(username, expected):
    links = build_manual_check_links(username, list(MANUAL_CHECK_SITES.values()))
    by_site = {link.site_name: link.url for link in links}
    assert by_site['Douyin'] == f'https://www.douyin.com/search/{expected}?type=user'
    assert by_site['Xiaohongshu'] == f'https://www.xiaohongshu.com/search_result/?keyword={expected}'


def test_links_are_https_and_unverified():
    for link in build_manual_check_links('example', list(MANUAL_CHECK_SITES.values())):
        assert link.url.startswith('https://')
        assert link.verified is False


def test_manual_check_sites_stay_out_of_manifest():
    """Manual-check sites must never be probed by automatic detection."""
    manifest_path = os.path.join(os.path.dirname(__file__), '../sherlock_project/resources/data.json')
    with open(manifest_path, encoding='utf-8') as file:
        manifest_names = {name.lower() for name in json.load(file)}
    for name in MANUAL_CHECK_SITES:
        assert name.lower() not in manifest_names


def test_cli_prints_links_for_expanded_usernames(tmp_path):
    output = Interactives.run_cli(f'--manual-check --no-color --csv --txt -fo "{tmp_path}" ab{{?}}cd')
    for name in ('ab_cd', 'ab-cd', 'ab.cd'):
        assert f'https://www.douyin.com/search/{name}?type=user' in output
        assert f'https://www.xiaohongshu.com/search_result/?keyword={name}' in output
    assert 'unverified' in output
    # Unverified links are never written to reports
    assert list(tmp_path.iterdir()) == []


def test_cli_site_filter():
    output = Interactives.run_cli('--manual-check --no-color --site douyin example')
    assert 'douyin.com' in output
    assert 'xiaohongshu.com' not in output


def test_cli_rejects_sites_without_manual_check():
    with pytest.raises(InteractivesSubprocessError, match=r"not available for --manual-check: 'GitHub'"):
        Interactives.run_cli('--manual-check --site GitHub example')
