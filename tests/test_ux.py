import os
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


@pytest.mark.parametrize('username', [
    '../poc_escape',
    r'..\poc_escape',
    '/tmp/poc_escape',
    r'C:\temp\poc_escape',
])
@pytest.mark.parametrize('extension', ['txt', 'csv', 'xlsx'])
def test_output_filename_stays_within_output_folder(username, extension):
    filename = f"{sherlock.safe_filename_component(username)}.{extension}"
    output_folder = os.path.abspath('out')
    result_file = os.path.abspath(os.path.join(output_folder, filename))

    assert os.path.commonpath([output_folder, result_file]) == output_folder


@pytest.mark.parametrize('username', ['', '.', '..', '../'])
def test_invalid_output_filename_component(username):
    with pytest.raises(ValueError, match='cannot be used as an output filename'):
        sherlock.safe_filename_component(username)


@pytest.mark.parametrize('cliargs', [
    '',
    '--site urghrtuight --egiotr',
    '--',
])
def test_no_usernames_provided(cliargs):
    with pytest.raises(InteractivesSubprocessError, match=r"error: the following arguments are required: USERNAMES"):
        Interactives.run_cli(cliargs)
