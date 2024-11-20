import os
import json
import urllib
import pytest
from sherlock_project.sites import SitesInformation


# Fixture to initialize a SitesInformation object
@pytest.fixture()
def sites_obj():
    """
    Fixture for creating a SitesInformation instance with data loaded from the local JSON file.
    """
    data_file = os.path.join(os.path.dirname(__file__), "../sherlock_project/resources/data.json")
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Data file not found: {data_file}")
    yield SitesInformation(data_file_path=data_file)


# Fixture to provide site information as a dictionary (session-wide)
@pytest.fixture(scope="session")
def sites_info():
    """
    Fixture that provides site information as a dictionary of site names to site details.
    """
    data_file = os.path.join(os.path.dirname(__file__), "../sherlock_project/resources/data.json")
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Data file not found: {data_file}")

    sites_obj = SitesInformation(data_file_path=data_file)
    sites_iterable = {site.name: site.information for site in sites_obj}
    yield sites_iterable


# Fixture to fetch and load the remote schema file
@pytest.fixture(scope="session")
def remote_schema():
    """
    Fixture to fetch and parse the remote JSON schema for site data validation.
    """
    schema_url = 'https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock_project/resources/data.schema.json'
    try:
        with urllib.request.urlopen(schema_url) as remoteschema:
            schemadat = json.load(remoteschema)
        yield schemadat
    except urllib.error.URLError as e:
        raise ConnectionError(f"Unable to fetch schema from {schema_url}: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON from {schema_url}: {e}")


# Utility function to check if the data file exists
def validate_data_file(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file does not exist: {path}")
