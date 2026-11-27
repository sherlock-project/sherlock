from sherlock_project.sites import SiteInformation


def test_site_information_honors_explicit_unclaimed_username():
    site = SiteInformation(
        "Example",
        "https://example.com",
        "https://example.com/{}",
        "claimed",
        {},
        False,
        username_unclaimed="known-unclaimed",
    )

    assert site.username_unclaimed == "known-unclaimed"
