import os
import pytest
from sherlock.sites import SitesInformation

@pytest.fixture()
def sites_obj():
    sites_obj = SitesInformation(data_file_path=os.path.join(os.path.dirname(__file__), "../sherlock/resources/data.json"))
    yield sites_obj

@pytest.fixture(scope="session")
def sites_info():
    sites_obj = SitesInformation(data_file_path=os.path.join(os.path.dirname(__file__), "../sherlock/resources/data.json"))
    sites_iterable = {site.name: site.information for site in sites_obj}
    yield sites_iterable
