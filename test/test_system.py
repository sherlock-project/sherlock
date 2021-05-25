import warnings
import pytest
import os
import os.path
from sherlock import sherlock
from sherlock.sites import SitesInformation
from sherlock.notify import QueryNotify, QueryStatus
warnings.simplefilter('ignore', ResourceWarning)

all_sites_cached = None


def all_sites():
    global all_sites_cached
    if all_sites_cached is None:
        sites = SitesInformation()
        all_sites_cached = []
        for site in sites:
            all_sites_cached.append([site.name])
    return all_sites_cached


@pytest.fixture(scope='function')
def sites_info(request):
    site_data_all = request.config.cache.get('site_data_all', None)
    if site_data_all is None:
        sites = SitesInformation()
        site_data_all = {}
        for site in sites:
            site_data_all[site.name] = site.information
        request.config.cache.set('site_data_all', site_data_all)
    sought = {}
    for site in site_data_all:
        if site in request.param:
            sought[site] = site_data_all[site]
    return sought


@pytest.fixture(scope='function')
def sites_excluded(request):
    excluded_sites = request.config.cache.get('excluded_sites', None)
    if excluded_sites is None:
        excluded_sites_path = os.path.join(
            os.path.dirname(os.path.realpath(sherlock.__file__)),
            'tests/.excluded_sites'
        )
        try:
            with open(excluded_sites_path, 'r', encoding='utf-8') as file:
                excluded_sites = file.read().splitlines()
                request.config.cache.set('excluded_sites', excluded_sites)
        except FileNotFoundError:
            excluded_sites = []
            request.config.cache.set('excluded_sites', excluded_sites)
    return excluded_sites


@pytest.fixture()
def query_notify():
    return QueryNotify()


@pytest.mark.system
@pytest.mark.system_smoke
@pytest.mark.parametrize(
    'sites_info, error_type, query_notify, expected',
    [
        pytest.param(
            ['BinarySearch'], 'message', None, QueryStatus.CLAIMED
        ),
        pytest.param(
            ['BinarySearch'], 'message', None, QueryStatus.AVAILABLE
        ),
        pytest.param(
            ['Pinterest'], 'status_code', None, QueryStatus.CLAIMED
        ),
        pytest.param(
            ['Pinterest'], 'status_code', None, QueryStatus.AVAILABLE
        ),
        pytest.param(
            ['VK'], 'response_url', None, QueryStatus.CLAIMED
        ),
        pytest.param(
            ['VK'], 'response_url', None, QueryStatus.AVAILABLE
        )
    ], indirect=['sites_info', 'query_notify']
)
def test_specific_sites_response_to_usernames(
    sites_info,
    error_type,
    query_notify,
    expected
):
    assert len(sites_info) == 1
    value = list(sites_info.values())[0]
    assert value['errorType'] == error_type
    if expected == QueryStatus.AVAILABLE:
        username = value['username_unclaimed']
    else:
        username = value['username_claimed']
    results = sherlock.sherlock(
        username,
        sites_info,
        query_notify
    )
    assert len(results) == 1
    result = list(results.values())[0]
    assert result['status'].status == expected


@pytest.mark.system
@pytest.mark.system_full
@pytest.mark.parametrize(
    'sites_info', all_sites(), indirect=True
)
@pytest.mark.parametrize(
    'expected', [QueryStatus.CLAIMED, QueryStatus.AVAILABLE]
)
def test_all_known_sites(sites_info, expected, query_notify):
    assert len(sites_info) == 1
    value = list(sites_info.values())[0]
    if expected == QueryStatus.AVAILABLE:
        username = value.get('username_unclaimed', None)
    else:
        username = value.get('username_claimed', None)
    if username is not None:
        # Skip any site lacking testable username
        results = sherlock.sherlock(
            username,
            sites_info,
            query_notify
        )
        assert len(results) == 1
        result = list(results.values())[0]
        if result['status'].status == QueryStatus.UNKNOWN:
            pytest.skip(f"Skipping: `{username}`` for {sites_info.keys()}")
        assert result['status'].status == expected


@pytest.mark.system
@pytest.mark.system_config
@pytest.mark.parametrize(
    'sites_info', all_sites(), indirect=True
)
@pytest.mark.parametrize(
    'expected', [QueryStatus.CLAIMED, QueryStatus.AVAILABLE]
)
def test_site_coverage(sites_info, expected):
    if len(sites_info) != 1:
        print(sites_info)
    assert len(sites_info) == 1
    value = list(sites_info.values())[0]
    if expected == QueryStatus.AVAILABLE:
        username = value.get('username_unclaimed', None)
    else:
        username = value.get('username_claimed', None)
    assert username is not None
