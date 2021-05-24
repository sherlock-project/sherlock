import warnings
import pytest
import os
import os.path
from sherlock import sherlock
from sherlock.sites import SitesInformation
from sherlock.notify import QueryNotify, QueryStatus
warnings.simplefilter('ignore', ResourceWarning)


def all_sites():
    sites = SitesInformation()
    all = []
    for site in sites:
        all.append(site.name)
    return all


@pytest.fixture(scope='function')
def sites_info(request):
    sites = SitesInformation()
    site_data_all = {}
    for site in sites:
        if site.name in request.param:
            site_data_all[site.name] = site.information
    return site_data_all


@pytest.fixture(scope='function')
def sites_excluded(request):
    excluded_sites_path = os.path.join(
        os.path.dirname(os.path.realpath(sherlock.__file__)),
        'tests/.excluded_sites'
    )
    print(excluded_sites_path)
    try:
        with open(excluded_sites_path, 'r', encoding='utf-8') as file:
            excluded_sites = file.read().splitlines()
    except FileNotFoundError:
        excluded_sites = []
    return excluded_sites


@pytest.fixture()
def query_notify():
    return QueryNotify()


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
        results = sherlock.sherlock(
            username,
            sites_info,
            query_notify
        )
        assert len(results) == 1
        result = list(results.values())[0]
        assert result['status'].status == expected


@pytest.mark.parametrize(
    'sites_info', all_sites(), indirect=True
)
@pytest.mark.parametrize(
    'expected', [QueryStatus.CLAIMED, QueryStatus.AVAILABLE]
)
def test_site_coverage(sites_info, expected):
    assert len(sites_info) == 1
    value = list(sites_info.values())[0]
    if expected == QueryStatus.AVAILABLE:
        username = value.get('username_unclaimed', None)
    else:
        username = value.get('username_claimed', None)
    assert username is not None
