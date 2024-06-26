import os
import json
import pytest
from jsonschema import validate

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
