import json
import os

import pytest
from jsonschema import ValidationError, validate


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

def _local_schema() -> dict:
    schema_relative: str = '../sherlock_project/resources/data.schema.json'
    schema_path: str = os.path.join(os.path.dirname(__file__), schema_relative)
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _manifest_of(*targets: dict) -> dict:
    """Build a minimal manifest around the given targets, keeping the schema reference."""
    manifest: dict = {"$schema": "https://data.sherlockproject.xyz"}
    for target in targets:
        manifest.update(target)
    return manifest


def _target(**overrides) -> dict:
    target: dict = {
        "url": "https://example.invalid/{}",
        "urlMain": "https://example.invalid",
        "username_claimed": "blue",
    }
    target.update(overrides)
    return {"Example": target}


def test_schema_rejects_error_fields_of_other_detection_methods():
    """The schema must reject a target mixing an error field with an unrelated errorType.

    data.schema.json declares draft 2020-12 and encodes this rule with the keyword that
    superseded `dependencies` (which draft 2020-12 validators ignore entirely).
    """
    schema = _local_schema()

    mixed_message_with_error_code = _manifest_of(_target(
        errorType="message", errorMsg="No such user", errorCode=404,
    ))
    with pytest.raises(ValidationError):
        validate(instance=mixed_message_with_error_code, schema=schema)

    mixed_status_code_with_error_url = _manifest_of(_target(
        errorType="status_code", errorUrl="https://example.invalid/",
    ))
    with pytest.raises(ValidationError):
        validate(instance=mixed_status_code_with_error_url, schema=schema)


def test_schema_accepts_error_fields_of_combined_detection_methods():
    """A target detecting via several methods may carry each method's error field."""
    schema = _local_schema()

    combined = _manifest_of(_target(
        errorType=["message", "status_code"], errorMsg="No such user", errorCode=404,
    ))
    validate(instance=combined, schema=schema)


# Ensure that the expected values are beind returned by the site list
@pytest.mark.parametrize("target_name,target_expected_err_type", [
    ('GitHub', 'status_code'),
    ('GitLab', 'message'),
])
def test_site_list_iterability (sites_info, target_name, target_expected_err_type):
    assert sites_info[target_name]['errorType'] == target_expected_err_type
