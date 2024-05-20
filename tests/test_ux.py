import pytest
from sherlock import sherlock

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
    assert sherlock.multiple_usernames('test{?}test') == ["test_test" , "test-test" , "test.test"]



#def test_area(self):
#    test_usernames = ["test{?}test" , "test{?feo" , "test"]
#    for name in test_usernames:
#        if(sh.check_for_parameter(name)):
#            self.assertAlmostEqual(sh.multiple_usernames(name), ["test_test" , "test-test" , "test.test"])
#        else:
#            self.assertAlmostEqual(name, name)
