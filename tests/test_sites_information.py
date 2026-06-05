import pytest
import json
from unittest.mock import patch
from sherlock_project.sites import SitesInformation

# Black-box tests (Error partitioning and boundary value analysis), complemented by white box logic

# Inexistent File
def test_sitesinformation_partition_file_not_found(tmp_path):
    fake_path = tmp_path / "data.json"
    
    with pytest.raises(FileNotFoundError):
        SitesInformation(data_file_path=str(fake_path))

# Corrupted File
def test_sitesinformation_partition_corrupted_json(tmp_path):
    bad_file = tmp_path / "bad_data.json"
    bad_file.write_text("This is not a { JSON } file.", encoding="utf-8")
    
    with pytest.raises(ValueError) as exc_info:
        SitesInformation(data_file_path=str(bad_file))
    
    assert "Problem parsing json contents" in str(exc_info.value)

# Lower Bound
@patch('sherlock_project.sites.requests.get')
def test_sitesinformation_boundary_empty_string(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "FakeWebsite": {
            "urlMain": "https://fakewebsite.com",
            "url": "https://fakewebsite.com/{}",
            "username_claimed": "john_doe"
        }
    }
    mock_get.return_value.text.splitlines.return_value = []

    sites_info = SitesInformation(data_file_path="")

    called_urls = [call.kwargs.get("url") for call in mock_get.call_args_list]
    assert "https://data.sherlockproject.xyz" in called_urls
    assert "FakeWebsite" in sites_info.sites