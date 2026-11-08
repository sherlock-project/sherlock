import pytest

from sherlock_project.sherlock import pull_request_manifest_url


def test_missing_pull_request_is_not_found():
    with pytest.raises(LookupError):
        pull_request_manifest_url(404, {"message": "Not Found"})


def test_rate_limit_is_not_a_missing_pull_request():
    payload = {"message": "API rate limit exceeded for 1.2.3.4"}
    with pytest.raises(RuntimeError):
        pull_request_manifest_url(403, payload)


def test_successful_pull_request_returns_manifest_url():
    payload = {"head": {"sha": "abc123"}, "title": "example"}
    url = pull_request_manifest_url(200, payload)
    assert url == (
        "https://raw.githubusercontent.com/sherlock-project/sherlock/"
        "abc123/sherlock_project/resources/data.json"
    )


def test_message_field_on_success_does_not_hide_the_pull_request():
    payload = {"message": "not an error", "head": {"sha": "abc123"}}
    url = pull_request_manifest_url(200, payload)
    assert url.endswith("/abc123/sherlock_project/resources/data.json")
