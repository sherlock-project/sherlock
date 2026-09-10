import pytest
import random
import re
import rstr

from sherlock_project.sherlock import sherlock
from sherlock_project.notify import QueryNotify
from sherlock_project.result import QueryResult, QueryStatus


FALSE_POSITIVE_ATTEMPTS: int = 2    # Since the usernames are randomly generated, it's POSSIBLE that a real username can be hit
FALSE_POSITIVE_QUANTIFIER_UPPER_BOUND: int = 15  # If a pattern uses quantifiers such as `+` `*` or `{n,}`, limit the upper bound (0 to disable)
FALSE_POSITIVE_DEFAULT_PATTERN: str = r'^[a-zA-Z0-9]{7,20}$'  # Used in absence of a regexCheck entry


OPEN_ENDED_REPETITION: re.Pattern = re.compile(r'\{(\d+),\}')  # {n,}


def set_pattern_upper_bound(pattern: str, upper_bound: int = FALSE_POSITIVE_QUANTIFIER_UPPER_BOUND) -> str:
    """Set upper bound for regex patterns that use quantifiers such as `+` `*` or `{n,}`.

    Only quantifiers are rewritten. Inside a character class `+` and `*` are ordinary
    members, so rewriting them there would alter which characters the pattern accepts
    and produce handles the target itself rejects.
    """
    def bounded(lower_bound: int) -> str:
        return f'{{{lower_bound},{max(lower_bound, upper_bound)}}}'

    bounded_pattern: list[str] = []
    index: int = 0
    within_class: bool = False

    while index < len(pattern):
        char: str = pattern[index]

        # An escaped character is a literal, never a quantifier
        if char == '\\':
            bounded_pattern.append(pattern[index:index + 2])
            index += 2
            continue

        if within_class:
            within_class = char != ']'
            bounded_pattern.append(char)
            index += 1
            continue

        if char == '[':
            bounded_pattern.append(char)
            index += 1
            within_class = True
            # A leading `^` negates the class, and a `]` in first position is a
            # literal member rather than the end of the class
            if pattern[index:index + 1] == '^':
                bounded_pattern.append('^')
                index += 1
            if pattern[index:index + 1] == ']':
                bounded_pattern.append(']')
                index += 1
            continue

        if char in '+*':
            bounded_pattern.append(bounded(1 if char == '+' else 0))
            index += 1
            continue

        open_ended: re.Match | None = OPEN_ENDED_REPETITION.match(pattern, index)
        if open_ended:
            bounded_pattern.append(bounded(int(open_ended.group(1))))
            index = open_ended.end()
            continue

        bounded_pattern.append(char)
        index += 1

    return ''.join(bounded_pattern)

def false_positive_check(sites_info: dict[str, dict[str, str]], site: str, pattern: str) -> QueryStatus:
    """Check if a site is likely to produce false positives."""
    status: QueryStatus = QueryStatus.UNKNOWN

    for _ in range(FALSE_POSITIVE_ATTEMPTS):
        query_notify: QueryNotify = QueryNotify()
        username: str = rstr.xeger(pattern)

        result: QueryResult | str = sherlock(
            username=username,
            site_data=sites_info,
            query_notify=query_notify,
        )[site]['status']

        if not hasattr(result, 'status'):
            raise TypeError(f"Result for site {site} does not have 'status' attribute. Actual result: {result}")
        if type(result.status) is not QueryStatus: # type: ignore
            raise TypeError(f"Result status for site {site} is not of type QueryStatus. Actual type: {type(result.status)}") # type: ignore
        status = result.status # type: ignore

        if status in (QueryStatus.AVAILABLE, QueryStatus.WAF):
            return status

    return status


def false_negative_check(sites_info: dict[str, dict[str, str]], site: str) -> QueryStatus:
    """Check if a site is likely to produce false negatives."""
    status: QueryStatus = QueryStatus.UNKNOWN
    query_notify: QueryNotify = QueryNotify()

    result: QueryResult | str = sherlock(
        username=sites_info[site]['username_claimed'],
        site_data=sites_info,
        query_notify=query_notify,
    )[site]['status']

    if not hasattr(result, 'status'):
            raise TypeError(f"Result for site {site} does not have 'status' attribute. Actual result: {result}")
    if type(result.status) is not QueryStatus: # type: ignore
        raise TypeError(f"Result status for site {site} is not of type QueryStatus. Actual type: {type(result.status)}") # type: ignore
    status = result.status # type: ignore

    return status

@pytest.mark.validate_targets
@pytest.mark.online
class Test_All_Targets:

    @pytest.mark.validate_targets_fp
    def test_false_pos(self, chunked_sites: dict[str, dict[str, str]]):
        """Iterate through all sites in the manifest to discover possible false-positive inducting targets."""
        pattern: str
        for site in chunked_sites:
            try:
                pattern = chunked_sites[site]['regexCheck']
            except KeyError:
                pattern = FALSE_POSITIVE_DEFAULT_PATTERN

            if FALSE_POSITIVE_QUANTIFIER_UPPER_BOUND > 0:
                pattern = set_pattern_upper_bound(pattern)

            result: QueryStatus = false_positive_check(chunked_sites, site, pattern)
            assert result is QueryStatus.AVAILABLE, f"{site} produced false positive with pattern {pattern}, result was {result}"

    @pytest.mark.validate_targets_fn
    def test_false_neg(self, chunked_sites: dict[str, dict[str, str]]):
        """Iterate through all sites in the manifest to discover possible false-negative inducting targets."""
        for site in chunked_sites:
            result: QueryStatus = false_negative_check(chunked_sites, site)
            assert result is QueryStatus.CLAIMED, f"{site} produced false negative, result was {result}"


@pytest.mark.parametrize('pattern,expected', [
    # Quantifiers are bounded
    (r'^[a-z]+$', r'^[a-z]{1,15}$'),
    (r'^[a-z]*$', r'^[a-z]{0,15}$'),
    (r'^[a-z]{3,}$', r'^[a-z]{3,15}$'),
    (r'^(ab)+$', r'^(ab){1,15}$'),
    # Closed ranges and escaped literals are not quantifiers to bound
    (r'^[a-z]{3,10}$', r'^[a-z]{3,10}$'),
    (r'^a\+b$', r'^a\+b$'),
    (r'^a\*b$', r'^a\*b$'),
    # An escaped backslash is a literal, so the quantifier after it still applies
    (r'^a\\+$', r'^a\\{1,15}$'),
    # `+` and `*` inside a character class are members rather than quantifiers
    (r'^[a-zA-Z0-9_.+-]{1,40}$', r'^[a-zA-Z0-9_.+-]{1,40}$'),    # Wordnik
    (r'^[^\/:*?"<>|@]{3,50}$', r'^[^\/:*?"<>|@]{3,50}$'),        # CyberDefenders
    (r'^[]+]$', r'^[]+]$'),                                      # leading `]` is a member
    # A lower bound above the cap lifts the bound for that quantifier alone
    (r'^[a-z]{20,}x[0-9]+$', r'^[a-z]{20,20}x[0-9]{1,15}$'),
])
def test_set_pattern_upper_bound(pattern: str, expected: str):
    """Bounding should constrain quantifiers without rewriting anything else."""
    assert set_pattern_upper_bound(pattern) == expected


def test_bounded_manifest_patterns_generate_legal_usernames(sites_info):
    """Every regexCheck must still accept the usernames generated from its bounded form.

    A bound that alters the pattern yields usernames the target itself rejects, which
    reports as a false positive against an otherwise healthy target.
    """
    lookaround: re.Pattern = re.compile(r'\(\?[=!<]')
    random.seed(0)

    for site, site_info in sites_info.items():
        pattern: str | None = site_info.get('regexCheck')
        # rstr cannot honor lookarounds, so those patterns may generate a rejected
        # username no matter how they are bounded
        if not pattern or lookaround.search(pattern):
            continue

        bounded: str = set_pattern_upper_bound(pattern)
        for _ in range(20):
            username: str = rstr.xeger(bounded)
            assert re.search(pattern, username), \
                f"{site}: bounded pattern {bounded} generated '{username}', which its own regexCheck {pattern} rejects"

