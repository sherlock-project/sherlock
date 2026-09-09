import os
import json
from unittest.mock import Mock

import pytest
from jsonschema import validate

from sherlock_project.sites import SitesInformation


@pytest.mark.parametrize("manifest_name", ["http-manifest.json", "https-manifest.json"])
def test_local_manifest_filename_starting_with_http(manifest_name, tmp_path, monkeypatch):
    manifest = tmp_path / manifest_name
    manifest.write_text(
        json.dumps(
            {
                "Example": {
                    "urlMain": "https://example.com",
                    "url": "https://example.com/{}",
                    "username_claimed": "taken",
                    "errorType": "status_code",
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    sites = SitesInformation(manifest.name, honor_exclusions=False)

    assert sites.site_name_list() == ["Example"]


@pytest.mark.parametrize("manifest_url", [
    "http://example.com/manifest.json",
    "https://example.com/manifest.json",
])
def test_manifest_http_url_is_fetched(manifest_url, monkeypatch):
    response = Mock(status_code=200)
    response.json.return_value = {}
    get = Mock(return_value=response)
    monkeypatch.setattr("sherlock_project.sites.requests.get", get)

    sites = SitesInformation(manifest_url, honor_exclusions=False)

    assert sites.site_name_list() == []
    get.assert_called_once_with(url=manifest_url, timeout=30)

def test_validate_manifest_against_local_schema():
    """Ensures that the manifest matches the local schema, for situations where the schema is being changed."""
    json_relative: str = '../sherlock_project/resources/data.json'
    schema_relative: str = '../sherlock_project/resources/data.schema.json'

    json_path: str = os.path.join(os.path.dirname(__file__), json_relative)
    schema_path: str = os.path.join(os.path.dirname(__file__), schema_relative)

    with open(json_path, 'r') as f:
        jsondat = json.load(f)
    with open(schema_path, 'r') as f:
        schemadat = json.load(f)

    validate(instance=jsondat, schema=schemadat)


@pytest.mark.online
def test_validate_manifest_against_remote_schema(remote_schema):
    """Ensures that the manifest matches the remote schema, so as to not unexpectedly break clients."""
    json_relative: str = '../sherlock_project/resources/data.json'
    json_path: str = os.path.join(os.path.dirname(__file__), json_relative)

    with open(json_path, 'r') as f:
        jsondat = json.load(f)

    validate(instance=jsondat, schema=remote_schema)

# Ensure that the expected values are beind returned by the site list
@pytest.mark.parametrize("target_name,target_expected_err_type", [
    ('GitHub', 'status_code'),
    ('GitLab', 'message'),
])
def test_site_list_iterability (sites_info, target_name, target_expected_err_type):
    assert sites_info[target_name]['errorType'] == target_expected_err_type
