import pytest
from sherlock_project.sherlock import check_for_parameter, multiple_usernames

# White-box (Branch Coverage with some Statement Coverage) tests, complemented by black-box logic

def test_returns_true_when_marker_present():
    assert check_for_parameter("user{?}") is True

def test_returns_false_when_marker_absent():
    assert check_for_parameter("johndoe") is False

def test_returns_true_for_marker_only():
    assert check_for_parameter("{?}") is True

def test_multiple_usernames_produces_three_variants_in_order():
    result = multiple_usernames("user{?}")
    assert result == ["user_", "user-", "user."]

def test_multiple_usernames_replaces_all_occurrences():
    results = multiple_usernames("{?}user{?}")
    for variant in results:
        assert "{?}" not in variant
    assert len(results) == 3