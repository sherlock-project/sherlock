import json

import pytest

from apps.core.dtos import SiteResult
from apps.export.exporters import to_csv, to_json


@pytest.fixture
def sample_results():
    return [
        SiteResult(site_name="GitHub", url="https://github.com/torvalds", status="found"),
        SiteResult(site_name="Twitter", url="https://twitter.com/torvalds", status="not_found"),
    ]


# --- to_csv ---

def test_to_csv_has_expected_headers(sample_results):
    output = to_csv(sample_results)
    assert output.splitlines()[0] == "site_name,url,status"


def test_to_csv_writes_one_row_per_result(sample_results):
    output = to_csv(sample_results)
    assert len(output.splitlines()) == 3  # 1 header + 2 rows


def test_to_csv_escapes_commas_in_fields():
    results = [SiteResult(site_name="Site, A", url="https://example.com", status="found")]
    output = to_csv(results)
    assert '"Site, A"' in output.splitlines()[1]


def test_to_json_is_valid_and_has_expected_shape(sample_results):
    output = to_json(sample_results, "torvalds")
    data = json.loads(output)
    assert data["username"] == "torvalds"
    assert isinstance(data["hits"], list)
    assert len(data["hits"]) == 2
    first = data["hits"][0]
    assert first["site_name"] == "GitHub"
    assert first["url"] == "https://github.com/torvalds"
    assert first["status"] == "found"


# --- ExportView ---

@pytest.mark.django_db
def test_export_view_csv_returns_text_csv_content_type(client, mocker, mock_valid_username):
    mocker.patch(
        "apps.export.views.SherlockService.search",
        return_value=iter([
            SiteResult(site_name="GitHub", url="https://github.com/torvalds", status="found"),
        ]),
    )
    response = client.get(f"/export/?username={mock_valid_username}&format=csv")
    assert response.status_code == 200
    assert "text/csv" in response["Content-Type"]


@pytest.mark.django_db
def test_export_view_json_returns_application_json(client, mocker, mock_valid_username):
    mocker.patch(
        "apps.export.views.SherlockService.search",
        return_value=iter([
            SiteResult(site_name="GitHub", url="https://github.com/torvalds", status="found"),
        ]),
    )
    response = client.get(f"/export/?username={mock_valid_username}&format=json")
    assert response.status_code == 200
    assert "application/json" in response["Content-Type"]


@pytest.mark.django_db
def test_export_view_unknown_format_returns_400(client, mock_valid_username):
    response = client.get(f"/export/?username={mock_valid_username}&format=xml")
    assert response.status_code == 400


@pytest.mark.django_db
def test_export_view_missing_username_returns_400(client):
    response = client.get("/export/?format=csv")
    assert response.status_code == 400
