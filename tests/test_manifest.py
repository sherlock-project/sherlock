import os
import json
import pytest
from jsonschema import validate

def validate_json(jsonfile: str, schemafile: str) -> bool:
    with open(jsonfile, 'r') as f:
        jsondat = json.load(f)
    with open(schemafile, 'r') as f:
        schemadat = json.load(f)
    validate(instance=jsondat, schema=schemadat)
    return True

def test_validate_manifest_against_schema():
    json_relative: str = '../sherlock/resources/data.json'
    schema_relative: str = '../sherlock/resources/data.schema.json'
    
    json_path: str = os.path.join(os.path.dirname(__file__), json_relative)
    schema_path: str = os.path.join(os.path.dirname(__file__), schema_relative)
    validate_json(jsonfile=json_path, schemafile=schema_path)

# Ensure that the expected values are beind returned by the site list
@pytest.mark.parametrize("target_name,target_expected_err_type", [
    ('GitHub', 'status_code'),
    ('GitLab', 'message'),
])
def test_site_list_iterability (sites_info, target_name, target_expected_err_type):
    assert sites_info[target_name]['errorType'] == target_expected_err_type
