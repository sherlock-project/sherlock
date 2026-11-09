"""Regression tests for result files escaping the output folder.

Result files are named after the username, so a username containing path
separators (e.g. "../poc_escape") used to write the .txt/.csv/.xlsx
reports outside --folderoutput (or the working directory). See #3207.
"""
import sys

import pytest
import requests

from sherlock_project import sherlock as sherlock_module
from sherlock_project.result import QueryResult, QueryStatus


@pytest.mark.parametrize(
    "username,expected",
    [
        ("../poc_escape", "poc_escape"),
        ("..\\..\\win_evil", "win_evil"),
        ("/abs_evil", "abs_evil"),
        ("a/b/c", "c"),
        ("....//poc", "poc"),
        ("normal.user-1", "normal.user-1"),
        ("john.doe", "john.doe"),
    ],
)
def test_safe_result_filename_reduces_to_single_component(username, expected):
    assert sherlock_module.safe_result_filename(username) == expected


@pytest.mark.parametrize(
    "username",
    [
        "..",
        ".",
        "",
        "../",
        "/",
        "a/",
        "a\x00b",
        "\x00",
    ],
)
def test_safe_result_filename_rejects_unusable_names(username):
    with pytest.raises(ValueError):
        sherlock_module.safe_result_filename(username)


def _fake_sherlock(username, site_data, query_notify, **kwargs):
    url = f"https://example.com/{username}"
    return {
        "Example": {
            "url_main": "https://example.com/",
            "url_user": url,
            "status": QueryResult(
                username, "Example", url, QueryStatus.CLAIMED, query_time=0.1
            ),
            "http_status": 200,
        }
    }


def _run_main(monkeypatch, tmp_path, username, extra_args):
    """Run main() offline: search stubbed, update check forced to fail."""
    workdir = tmp_path / "work"
    workdir.mkdir()
    outdir = workdir / "out"

    def offline_get(*args, **kwargs):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(requests, "get", offline_get)
    monkeypatch.setattr(sherlock_module, "sherlock", _fake_sherlock)
    monkeypatch.chdir(workdir)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "sherlock",
            username,
            "--folderoutput",
            str(outdir),
            "--local",
            *extra_args,
        ],
    )
    sherlock_module.main()
    return workdir, outdir


def test_traversal_username_results_stay_in_output_folder(
    monkeypatch, tmp_path
):
    workdir, outdir = _run_main(
        monkeypatch, tmp_path, "../poc_escape", ["--txt", "--csv", "--xlsx"]
    )

    # Reports land inside the folder output (txt/csv) or the working
    # directory (xlsx) under the reduced filename.
    assert (outdir / "poc_escape.txt").is_file()
    assert (outdir / "poc_escape.csv").is_file()
    assert (workdir / "poc_escape.xlsx").is_file()

    # Nothing was written outside the working directory.
    escaped = [p for p in tmp_path.rglob("poc_escape.*") if workdir not in p.parents]
    assert escaped == []


def test_absolute_username_results_stay_in_output_folder(
    monkeypatch, tmp_path
):
    workdir, outdir = _run_main(
        monkeypatch, tmp_path, "/abs_evil", ["--txt", "--csv", "--xlsx"]
    )

    assert (outdir / "abs_evil.txt").is_file()
    assert (outdir / "abs_evil.csv").is_file()
    assert (workdir / "abs_evil.xlsx").is_file()
    escaped = [p for p in tmp_path.rglob("abs_evil.*") if workdir not in p.parents]
    assert escaped == []


def test_dotdot_username_rejected_before_writing(monkeypatch, tmp_path):
    with pytest.raises(SystemExit) as excinfo:
        _run_main(monkeypatch, tmp_path, "..", ["--txt", "--csv", "--xlsx"])
    assert excinfo.value.code == 1
    assert [p for p in tmp_path.rglob("*") if p.is_file()] == []


def test_normal_username_filenames_unchanged(monkeypatch, tmp_path):
    workdir, outdir = _run_main(
        monkeypatch, tmp_path, "normal.user-1", ["--txt", "--csv", "--xlsx"]
    )

    assert (outdir / "normal.user-1.txt").is_file()
    assert (outdir / "normal.user-1.csv").is_file()
    assert (workdir / "normal.user-1.xlsx").is_file()


def test_dotdot_username_without_file_output_still_searches(
    monkeypatch, tmp_path
):
    # No --txt/--csv/--xlsx: nothing is written, so the run must not be
    # rejected just because the username cannot name a result file.
    _run_main(monkeypatch, tmp_path, "..", [])
    assert [p for p in tmp_path.rglob("*") if p.is_file()] == []
