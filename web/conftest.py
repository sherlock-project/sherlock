import pytest
import responses

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
