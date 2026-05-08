import pytest
from sherlock_project import sherlock
from sherlock_project.result import QueryStatus
from sherlock_interactives import Interactives
from sherlock_interactives import InteractivesSubprocessError


def test_remove_nsfw(sites_obj):
    nsfw_target: str = 'Pornhub'
    assert nsfw_target in {site.name: site.information for site in sites_obj}
    sites_obj.remove_nsfw_sites()
    assert nsfw_target not in {site.name: site.information for site in sites_obj}


# Parametrized sites should *not* include Motherless, which is acting as the control
@pytest.mark.parametrize('nsfwsites', [
    ['Pornhub'],
    ['Pornhub', 'Xvideos'],
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


def test_encode_username_for_url_preserves_safe_characters():
    assert sherlock.encode_username_for_url('user-name_1.@') == 'user-name_1.@'


def test_encode_username_for_url_escapes_special_characters():
    assert sherlock.encode_username_for_url('a/b c+') == 'a%2Fb%20c%2B'


def test_interpolate_string_uses_encoded_username_for_urls():
    encoded_username = sherlock.encode_username_for_url('a/b c+')
    assert sherlock.interpolate_string('https://example.com/{}', encoded_username) == 'https://example.com/a%2Fb%20c%2B'


def test_is_reddit_verification_page_detects_challenge_html():
    html = '''
    <title>Reddit - Please wait for verification</title>
    <form hidden method="GET" action="/user/j%20a%20c%20k%20s%20o%20n%20/">
      <input type="hidden" name="solution" />
      <input type="hidden" name="js_challenge" value="1"/>
      <input type="hidden" name="token" value="abc123"/>
      <input type="hidden" name="jsc_orig_r" value=""/>
    </form>
    '''
    assert sherlock.is_reddit_verification_page(html) is True


def test_is_reddit_verification_page_rejects_normal_html():
    html = '<html><head><title>Reddit - user page</title></head><body>normal content</body></html>'
    assert sherlock.is_reddit_verification_page(html) is False


def test_reddit_verification_page_is_classified_as_waf(monkeypatch):
    class FakeResponse:
        status_code = 200
        elapsed = 0.1
        encoding = 'utf-8'
        text = '''
        <title>Reddit - Please wait for verification</title>
        <form hidden method="GET" action="/user/j%20a%20c%20k%20s%20o%20n%20/">
          <input type="hidden" name="solution" />
          <input type="hidden" name="js_challenge" value="1"/>
          <input type="hidden" name="token" value="abc123"/>
          <input type="hidden" name="jsc_orig_r" value=""/>
        </form>
        '''

    class FakeFuture:
        def result(self):
            return FakeResponse()

    class FakeSherlockFuturesSession:
        def __init__(self, *args, **kwargs):
            pass

        def get(self, *args, **kwargs):
            return FakeFuture()

        def head(self, *args, **kwargs):
            return FakeFuture()

        def post(self, *args, **kwargs):
            return FakeFuture()

        def put(self, *args, **kwargs):
            return FakeFuture()

    monkeypatch.setattr(sherlock, 'SherlockFuturesSession', FakeSherlockFuturesSession)

    reddit_site = {
        'errorMsg': 'Sorry, nobody on Reddit goes by that name.',
        'errorType': 'message',
        'headers': {'accept-language': 'en-US,en;q=0.9'},
        'url': 'https://www.reddit.com/user/{}',
        'urlMain': 'https://www.reddit.com/',
        'username_claimed': 'blue',
    }

    results = sherlock.sherlock(
        username='j a c k s o n ',
        site_data={'Reddit': reddit_site},
        query_notify=sherlock.QueryNotify(),
    )

    assert results['Reddit']['status'].status is QueryStatus.WAF
    assert results['Reddit']['status'].context == 'Reddit verification page'


@pytest.mark.parametrize('cliargs', [
    '',
    '--site urghrtuight --egiotr',
    '--',
])
def test_no_usernames_provided(cliargs):
    with pytest.raises(InteractivesSubprocessError, match=r"error: the following arguments are required: USERNAMES"):
        Interactives.run_cli(cliargs)
