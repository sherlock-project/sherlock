import pytest
import responses
from django.template import Context

# this file was made to hold the shared fixtures amongst the apps
# (core, search, export).

@pytest.fixture
def mock_valid_username():
    return "torvalds"

@pytest.fixture(autouse=True)
def block_http_requests():
    """
    Blocks any HTTP requests made during the test suite.
    """
    with responses.RequestsMock() as rsps:
        yield rsps

def patched_context_copy(self):
    duplicate = Context()
    duplicate.dicts = self.dicts[:]
    return duplicate

Context.__copy__ = patched_context_copy