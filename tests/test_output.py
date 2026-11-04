import importlib
import sys
from types import SimpleNamespace
import pytest

@pytest.fixture
def cli_runner(monkeypatch, tmp_path, capsys):
    sherlock_module = importlib.import_module("sherlock_project.sherlock")
    monkeypatch.chdir(tmp_path)

    class FakeSites:
        def __init__(self, *args, **kwargs):
            self.sites = [
                SimpleNamespace(name="GitHub", information={})
            ]

        def __iter__(self):
            return iter(self.sites)

        def remove_nsfw_sites(self, **kwargs):
            pass

    class FakeNotify:
        def __init__(self, *args, **kwargs):
            pass

        def finish(self):
            pass

    def fake_search(username, site_data, query_notify, **kwargs):
        print(f"SEARCHED: {username}")

        return {
            "GitHub": {
                "url_main": "https://github.com",
                "url_user": f"https://github.com/{username}",
                "status": SimpleNamespace(
                    status=sherlock_module.QueryStatus.CLAIMED,
                    query_time=0.1,
                ),
                "http_status": 200,
            }
        }

    monkeypatch.setattr(sherlock_module, "SitesInformation", FakeSites)
    monkeypatch.setattr(sherlock_module, "QueryNotifyPrint", FakeNotify)
    monkeypatch.setattr(sherlock_module, "sherlock", fake_search)

    def skip_update(*args, **kwargs):
        raise ConnectionError("Update check unavailable during tests")

    monkeypatch.setattr(sherlock_module.requests, "get", skip_update)

    def fake_to_excel(self, filename, **kwargs):
        with open(filename, "wb") as output:
            output.write(b"mock Excel output")

    monkeypatch.setattr(
        sherlock_module.pd.DataFrame,
        "to_excel",
        fake_to_excel
    )

    def run(*args):
        monkeypatch.setattr(
            sys,
            "argv",
            ["sherlock", "--local", "--site", "GitHub", *args]
        )

        sherlock_module.main()
        return capsys.readouterr()

    return run

# test 1
@pytest.mark.parametrize("option,extension,label", [
    ("--txt", "txt", "TXT"),
    ("--csv", "csv", "CSV"),
    ("--xlsx", "xlsx", "XLSX"),
])
def test_invalid_output_path_does_not_stop_next_username(
    cli_runner, tmp_path, option, extension, label
):
    output = cli_runner(option, "missing/first", "second")

    assert f"Could not save {label} results" in output.err
    assert f"missing/first.{extension}" in output.err

    assert "SEARCHED: missing/first" in output.out
    assert "SEARCHED: second" in output.out

    assert (tmp_path / f"second.{extension}").is_file()

# test 2
@pytest.mark.parametrize("option,extension", [
    ("--txt", "txt"),
    ("--csv", "csv"),
    ("--xlsx", "xlsx"),
])
def test_valid_output_path_creates_report(
    cli_runner, tmp_path, option, extension
):
    output = cli_runner(option, "validuser")

    assert "Could not save" not in output.err

    report = tmp_path / f"validuser.{extension}"

    assert report.is_file()
    assert report.stat().st_size > 0

# test 3
@pytest.mark.parametrize("option,extension,label", [
    ("--txt", "txt", "TXT"),
    ("--csv", "csv", "CSV"),
])
def test_invalid_output_folder_does_not_stop_processing(
    cli_runner, tmp_path, option, extension, label
):
    (tmp_path / "blocked").write_text(
        "not a directory",
        encoding="utf-8"
    )

    output = cli_runner(
        option,
        "--folderoutput",
        "blocked",
        "first",
        "second"
    )

    assert output.err.count(
        f"Could not save {label} results"
    ) == 2

    assert "SEARCHED: first" in output.out
    assert "SEARCHED: second" in output.out