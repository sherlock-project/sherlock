"""Sherlock Manual Check Module

Some platforms cannot be checked automatically and reliably. For example, the
public handle may differ from the ID in the profile URL, or the site may block
requests from outside its region. For these platforms Sherlock can instead
print a user-search link that an operator opens and inspects by hand.

Manual-check links are always *unverified*. They are kept separate from the
site manifest (data.json), are never sent as requests, and are never counted
as detected accounts or written to report files.
"""

from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote


@dataclass(frozen=True)
class ManualCheckSite:
    """A platform that supports manual (operator-driven) account checks."""

    name: str
    url_main: str
    search_url: str  # "{}" is replaced by the percent-encoded username
    instructions: str


@dataclass(frozen=True)
class ManualCheckLink:
    """An unverified search link for one username on one platform."""

    site_name: str
    username: str
    url: str
    instructions: str
    verified: bool = False  # Never verified; the operator must confirm by hand


MANUAL_CHECK_SITES: dict[str, ManualCheckSite] = {
    site.name: site
    for site in (
        ManualCheckSite(
            name="Douyin",
            url_main="https://www.douyin.com/",
            search_url="https://www.douyin.com/search/{}?type=user",
            instructions=(
                "Opens the Users tab of the search results. Compare the exact "
                "Douyin ID shown on each candidate profile."
            ),
        ),
        ManualCheckSite(
            name="Xiaohongshu",
            url_main="https://www.xiaohongshu.com/",
            search_url="https://www.xiaohongshu.com/search_result/?keyword={}",
            instructions=(
                "Select the Users tab of the search results (sign-in may be "
                "required), or search for the handle in the Xiaohongshu app. "
                "Compare the exact Xiaohongshu ID on each candidate profile; it "
                "can differ from the ID in the profile URL."
            ),
        ),
    )
}


def select_manual_check_sites(
    site_filter: Optional[list[str]] = None,
) -> tuple[list[ManualCheckSite], list[str]]:
    """Select manual-check sites, optionally limited by a list of site names.

    Keyword Arguments:
    site_filter            -- Site names to include (case-insensitive). An
                              empty list or None selects every site.

    Return Value:
    Tuple of (selected sites in a stable order, names from site_filter that
    do not match any manual-check site).
    """
    if not site_filter:
        return list(MANUAL_CHECK_SITES.values()), []

    by_lower_name = {name.lower(): site for name, site in MANUAL_CHECK_SITES.items()}
    selected: list[ManualCheckSite] = []
    unknown: list[str] = []
    for requested in site_filter:
        site = by_lower_name.get(requested.lower())
        if site is None:
            unknown.append(requested)
        elif site not in selected:
            selected.append(site)
    return selected, unknown


def build_manual_check_links(
    username: str, sites: list[ManualCheckSite]
) -> list[ManualCheckLink]:
    """Build unverified search links for a username. Sends no requests.

    Keyword Arguments:
    username               -- Username (handle) to search for.
    sites                  -- Manual-check sites to build links for.

    Return Value:
    List of ManualCheckLink objects, one per site.
    """
    encoded = quote(username, safe="")
    return [
        ManualCheckLink(
            site_name=site.name,
            username=username,
            url=site.search_url.format(encoded),
            instructions=site.instructions,
        )
        for site in sites
    ]
