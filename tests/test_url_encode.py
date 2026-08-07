"""Regression tests for URL-safe username encoding in sherlock.

The per-site URL is built by interpolating the username into a format
string (e.g. ``https://example.com/users/{}``). The previous code
percent-encoded only spaces (``username.replace(' ', '%20')``) and let
every other URL-special character through raw, which broke usernames
containing ``?``, ``#``, ``&``, ``+``, ``/``, ``%``, or any non-ASCII
byte. The fix routes the username through ``encode_username_for_url``,
which uses ``urllib.parse.quote`` with ``safe=''`` and matches the form
the receiving site is expected to URL-decode.
"""

import pytest

from sherlock_project.sherlock import encode_username_for_url


class TestEncodeUsernameForUrl:
    """Pure-function coverage: no sherlock() call required."""

    def test_plain_username_passes_through(self):
        assert encode_username_for_url("alice") == "alice"

    def test_underscore_dot_dash_tilde_are_unreserved(self):
        assert encode_username_for_url("a.b_c-d~e") == "a.b_c-d~e"

    def test_space_is_encoded_as_percent_20(self):
        assert encode_username_for_url("alice bob") == "alice%20bob"

    def test_question_mark_is_encoded(self):
        # ?  would otherwise start a query string
        assert encode_username_for_url("a?b") == "a%3Fb"

    def test_hash_is_encoded(self):
        # # would otherwise start a fragment
        assert encode_username_for_url("a#b") == "a%23b"

    def test_ampersand_is_encoded(self):
        assert encode_username_for_url("a&b") == "a%26b"

    def test_plus_is_encoded(self):
        # + would otherwise decode to space in form-encoded bodies
        assert encode_username_for_url("a+b") == "a%2Bb"

    def test_percent_is_encoded(self):
        # % must itself be escaped or the next two chars are read as a hex escape
        assert encode_username_for_url("a%b") == "a%25b"

    def test_slash_is_encoded(self):
        # / would otherwise insert an extra path segment
        assert encode_username_for_url("a/b") == "a%2Fb"

    def test_non_ascii_latin_is_encoded(self):
        assert encode_username_for_url("é") == "%C3%A9"

    def test_emoji_is_encoded(self):
        # astral codepoint: é would be broken if any other encoding were used
        result = encode_username_for_url("🦊")
        assert "%" in result
        # the four-byte UTF-8 of the fox emoji
        assert result == "%F0%9F%A6%8A"

    def test_empty_username_encodes_to_empty(self):
        assert encode_username_for_url("") == ""

    def test_digits_only_unchanged(self):
        assert encode_username_for_url("12345") == "12345"

    def test_mixed_path_unsafe_characters(self):
        # the kind of username that actually triggers the bug
        # — combination of space, query, fragment, and percent
        assert encode_username_for_url("a b?c#d%e") == "a%20b%3Fc%23d%25e"

    def test_all_unreserved_passes_through_unchanged(self):
        # RFC 3986 unreserved set: ALPHA / DIGIT / "-" / "." / "_" / "~"
        assert encode_username_for_url("ABCabc0123-._~") == "ABCabc0123-._~"
