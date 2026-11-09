import csv
import json
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from sherlock_project import __version__, reporting, sherlock
from sherlock_project.result import QueryResult, QueryStatus


def scan_results(username):
    results = {}
    for status in QueryStatus:
        name = status.value + "Site"
        results[name] = {
            "url_main": "https://example.org",
            "url_user": ""
            if status is QueryStatus.ILLEGAL
            else f"https://example.org/{username}",
            "http_status": {
                QueryStatus.CLAIMED: 200,
                QueryStatus.AVAILABLE: 404,
                QueryStatus.UNKNOWN: "?",
                QueryStatus.ILLEGAL: "",
                QueryStatus.WAF: 403,
            }[status],
            "status": QueryResult(
                username,
                name,
                f"https://example.org/{username}",
                status,
                query_time=0.0 if status is QueryStatus.CLAIMED else None,
                context="Timeout Error" if status is QueryStatus.UNKNOWN else None,
            ),
            "response_text": b"RAW_RESPONSE_MUST_NOT_BE_EXPORTED",
        }
    return results


def test_json_report_preserves_statuses_zero_timings_and_error_context():
    report = reporting.build_username_report("Örnek", scan_results("Örnek"))
    assert report["username"] == "Örnek"
    assert report["summary"] == {
        "Claimed": 1,
        "Available": 1,
        "Unknown": 1,
        "Illegal": 1,
        "WAF": 1,
    }
    by_status = {site["status"]: site for site in report["sites"]}
    assert by_status["Claimed"]["response_time_s"] == 0.0
    assert by_status["Unknown"]["context"] == "Timeout Error"
    assert by_status["Unknown"]["http_status"] is None
    assert by_status["Illegal"]["http_status"] is None
    assert by_status["WAF"]["http_status"] == 403
    assert "response_text" not in json.dumps(report)
    assert "RAW_RESPONSE" not in json.dumps(report)


def test_empty_results_have_zero_status_counts():
    report = reporting.build_username_report("example", {})
    assert report["sites"] == []
    assert report["summary"] == {status.value: 0 for status in QueryStatus}


def test_json_file_preserves_unicode_and_multiple_usernames(tmp_path):
    reports = [
        reporting.build_username_report(name, scan_results(name))
        for name in ["Örnek", "ユーザー"]
    ]
    output = tmp_path / "report.json"
    reporting.write_json_report(output, reports)
    text = output.read_text(encoding="utf-8")
    payload = json.loads(text)
    assert payload == {
        "schema_version": 1,
        "sherlock_version": __version__,
        "results": reports,
    }
    assert "Örnek" in text and "ユーザー" in text
    assert set(tmp_path.iterdir()) == {output}


@pytest.mark.parametrize("invalid_value", [object(), float("nan"), float("inf")])
def test_invalid_json_preserves_previous_report(tmp_path, invalid_value):
    output = tmp_path / "report.json"
    output.write_text("previous report", encoding="utf-8")
    with pytest.raises((TypeError, ValueError)):
        reporting.write_json_report(output, [{"invalid": invalid_value}])
    assert output.read_text(encoding="utf-8") == "previous report"
    assert set(tmp_path.iterdir()) == {output}


def test_failed_atomic_replace_preserves_previous_report(tmp_path, monkeypatch):
    output = tmp_path / "report.json"
    output.write_text("previous report", encoding="utf-8")
    monkeypatch.setattr(
        reporting.os, "replace", Mock(side_effect=PermissionError("locked"))
    )
    with pytest.raises(PermissionError, match="locked"):
        reporting.write_json_report(output, [])
    assert output.read_text(encoding="utf-8") == "previous report"
    assert set(tmp_path.iterdir()) == {output}


@pytest.fixture
def cli_scan(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    site_entries = [
        SimpleNamespace(name=status.value + "Site", information={})
        for status in QueryStatus
    ]
    sites = Mock()
    sites.__iter__ = Mock(return_value=iter(site_entries))
    factory = Mock(return_value=sites)
    scanner = Mock(side_effect=lambda username, *args, **kwargs: scan_results(username))
    monkeypatch.setattr(sherlock, "SitesInformation", factory)
    monkeypatch.setattr(sherlock, "sherlock", scanner)
    monkeypatch.setattr(sherlock, "QueryNotifyPrint", Mock())
    monkeypatch.setattr(sherlock.signal, "signal", Mock())

    def version_request(url, *args, **kwargs):
        assert url == sherlock.forge_api_latest_release, "Unexpected network request"
        return SimpleNamespace(text=json.dumps({"tag_name": "v" + __version__}))

    monkeypatch.setattr(sherlock.requests, "get", version_request)
    monkeypatch.setattr(
        sherlock.requests.sessions.Session,
        "request",
        Mock(side_effect=AssertionError("Tests must not make network requests")),
    )
    return scanner, factory


def run_cli(monkeypatch, *arguments):
    monkeypatch.setattr(sys, "argv", ["sherlock", *arguments])
    sherlock.main()


def test_cli_exports_all_usernames_and_all_statuses(cli_scan, monkeypatch, tmp_path):
    output = tmp_path / "report.json"
    run_cli(monkeypatch, "Örnek", "second", "--json-output", str(output))
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert [r["username"] for r in payload["results"]] == ["Örnek", "second"]
    assert all(len(r["sites"]) == len(QueryStatus) for r in payload["results"])
    assert cli_scan[0].call_count == 2


def test_cli_exports_expanded_wildcard_usernames(cli_scan, monkeypatch, tmp_path):
    output = tmp_path / "report.json"
    run_cli(monkeypatch, "example{?}name", "--json-output", str(output))
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert [r["username"] for r in payload["results"]] == [
        "example_name",
        "example-name",
        "example.name",
    ]


def test_input_json_manifest_and_output_json_are_independent(
    cli_scan, monkeypatch, tmp_path
):
    output = tmp_path / "report.json"
    run_cli(
        monkeypatch,
        "example",
        "--json",
        "custom-sites.json",
        "--json-output",
        str(output),
    )
    assert cli_scan[1].call_args.kwargs["data_file_path"] == "custom-sites.json"
    assert json.loads(output.read_text(encoding="utf-8"))["schema_version"] == 1


def test_no_json_report_is_written_without_the_flag(cli_scan, monkeypatch, tmp_path):
    writer = Mock()
    monkeypatch.setattr(sherlock, "write_json_report", writer)
    run_cli(monkeypatch, "example")
    writer.assert_not_called()
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("print_all", [False, True])
def test_json_can_coexist_with_existing_txt_and_csv_exports(
    cli_scan, monkeypatch, tmp_path, print_all
):
    args = ["example", "--txt", "--csv", "--json-output", "report.json"]
    if print_all:
        args.append("--print-all")
    run_cli(monkeypatch, *args)
    assert (
        "Total Websites Username Detected On : 1"
        in (tmp_path / "example.txt").read_text()
    )
    with (tmp_path / "example.csv").open(newline="", encoding="utf-8") as stream:
        assert len(list(csv.DictReader(stream))) == (5 if print_all else 1)
    payload = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert len(payload["results"][0]["sites"]) == 5


def test_cli_reports_a_json_write_error_cleanly(cli_scan, monkeypatch, capsys):
    monkeypatch.setattr(
        sherlock, "write_json_report", Mock(side_effect=PermissionError("locked"))
    )
    with pytest.raises(SystemExit) as error:
        run_cli(monkeypatch, "example", "--json-output", "report.json")
    assert error.value.code == 1
    assert "Could not write JSON report" in capsys.readouterr().err


def test_cli_reports_a_missing_output_directory(
    cli_scan, monkeypatch, tmp_path, capsys
):
    output = tmp_path / "missing" / "report.json"
    with pytest.raises(SystemExit) as error:
        run_cli(monkeypatch, "example", "--json-output", str(output))
    assert error.value.code == 1
    assert str(output) in capsys.readouterr().err
    assert not output.parent.exists()
