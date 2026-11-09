import os
import json
from unittest.mock import Mock

import pytest
from jsonschema import validate

from sherlock_project.sites import SitesInformation


@pytest.mark.parametrize("manifest", [[], None, "not a site list"])
def test_reject_manifest_without_top_level_object(tmp_path, manifest):
    filename = tmp_path / "sites.json"
    filename.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match=r"sites\.json.*expected a JSON object"):
        SitesInformation(str(filename), honor_exclusions=False)


def test_reject_remote_manifest_without_top_level_object(monkeypatch):
    response = Mock(status_code=200)
    response.json.return_value = []
    monkeypatch.setattr("sherlock_project.sites.requests.get", Mock(return_value=response))

    with pytest.raises(ValueError, match=r"sites\.json.*expected a JSON object"):
        SitesInformation("https://example.com/sites.json", honor_exclusions=False)

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
