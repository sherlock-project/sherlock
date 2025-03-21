import os
import json
import urllib.request  # Imported only `request` to avoid namespace pollution
import pytest
from sherlock_project.sites import SitesInformation


@pytest.fixture(scope="module")  # Using `module` scope to reuse the object within a module
def sites_obj():
    """Fixture to provide a `SitesInformation` instance."""
    data_file_path = os.path.join(
        os.path.dirname(__file__),
        "../sherlock_project/resources/data.json"
    )
    if not os.path.exists(data_file_path):
        raise FileNotFoundError(f"Data file not found: {data_file_path}")
    sites_obj = SitesInformation(data_file_path=data_file_path)
    yield sites_obj


@pytest.fixture(scope="module")
def sites_info(sites_obj):
    """Fixture to provide a dictionary of site information."""
    sites_iterable = {
        site.name: site.information
        for site in sites_obj
    }
    yield sites_iterable


@pytest.fixture(scope="session")
def remote_schema():
    """Fixture to fetch and load the remote schema."""
    schema_url = (
        "https://raw.githubusercontent.com/sherlock-project/sherlock/master/"
        "sherlock_project/resources/data.schema.json"
    )
    try:
        with urllib.request.urlopen(schema_url) as response:
            if response.status != 200:
                raise ConnectionError(f"Failed to fetch schema: {schema_url}")
            schema_data = json.load(response)
        yield schema_data
    except Exception as e:
        raise RuntimeError(f"Error loading remote schema: {e}")
