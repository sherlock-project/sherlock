import csv
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from sherlock_project import sherlock as sherlock_module
from sherlock_project.result import QueryResult, QueryStatus


@pytest.fixture()
def stubbed_env(monkeypatch, tmp_path):
    """Run main() offline: no manifest fetch, no update check, no site queries."""
    monkeypatch.chdir(tmp_path)

    def fake_sherlock(username, site_data, query_notify, **kwargs):
        url_user = f"https://example.com/{username}"
        return {
            "Example": {
                "url_main": "https://example.com",
                "url_user": url_user,
                "http_status": 200,
                "status": QueryResult(
                    username, "Example", url_user, QueryStatus.CLAIMED, query_time=0.01
                ),
            }
        }

    monkeypatch.setattr(sherlock_module, "sherlock", fake_sherlock)
    monkeypatch.setattr(
        sherlock_module.requests,
        "get",
        lambda *args, **kwargs: SimpleNamespace(
            text=json.dumps(
                {"tag_name": f"v{sherlock_module.__version__}", "html_url": ""}
            )
        ),
    )

    def run(*cliargs):
        monkeypatch.setattr(sys, "argv", ["sherlock", *cliargs])
        return sherlock_module.main()

    return run


def test_csv_honors_output_flag(stubbed_env):
    stubbed_env("--local", "--csv", "--output", "out.csv", "daniel")

    assert Path("out.csv").is_file()
    assert not Path("daniel.csv").exists()
    with open("out.csv", newline="", encoding="utf-8") as report:
        rows = list(csv.reader(report))
    assert rows[0] == [
        "username",
        "name",
        "url_main",
        "url_user",
        "exists",
        "http_status",
        "response_time_s",
    ]
    assert rows[1][0] == "daniel"
    assert rows[1][4] == "Claimed"


def test_xlsx_honors_output_flag(stubbed_env):
    stubbed_env("--local", "--xlsx", "--output", "out.xlsx", "daniel")

    assert Path("out.xlsx").is_file()
    assert not Path("daniel.xlsx").exists()
    report = pd.read_excel("out.xlsx")
    assert list(report["username"]) == ["daniel"]
    assert list(report["exists"]) == ["Claimed"]


@pytest.mark.parametrize("formats", ["--csv --txt", "--csv --xlsx", "--txt --xlsx"])
def test_output_refused_with_multiple_formats(stubbed_env, capsys, formats):
    with pytest.raises(SystemExit) as exit_info:
        stubbed_env("--local", *formats.split(), "--output", "out", "daniel")

    assert exit_info.value.code == 1
    assert "single output format" in capsys.readouterr().out
    assert not Path("out").exists()
