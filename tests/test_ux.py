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


@pytest.mark.parametrize('timeout_val', ['abc', 'xyz', '1.2.3', '', 'None'])
def test_invalid_timeout_raises_argparse_error(timeout_val):
    """Non-numeric --timeout values should raise a clean argparse error, not a raw ValueError."""
    with pytest.raises(InteractivesSubprocessError, match=r"error: argument --timeout: invalid"):
        Interactives.run_cli(f'--timeout {timeout_val} someuser')


@pytest.mark.parametrize('timeout_val', ['-1', '0', '-0.5'])
def test_non_positive_timeout_raises_argparse_error(timeout_val):
    """Zero or negative --timeout values should raise a clean argparse error."""
    with pytest.raises(InteractivesSubprocessError, match=r"error: argument --timeout: invalid"):
        Interactives.run_cli(f'--timeout {timeout_val} someuser')
