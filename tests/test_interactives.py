import subprocess
import sys

import pytest

from sherlock_interactives import Interactives, InteractivesSubprocessError


def test_run_cli_uses_current_interpreter_and_preserves_quoted_arguments(monkeypatch):
    interpreter = "/a path with spaces/python"
    monkeypatch.setattr(sys, "executable", interpreter)
    calls = []

    def check_output(command, **kwargs):
        calls.append((command, kwargs))
        return "Sherlock output\n"

    monkeypatch.setattr(subprocess, "check_output", check_output)
    assert Interactives.run_cli('--site "Some Site" --version') == "Sherlock output\n"
    assert len(calls) == 1
    command, options = calls[0]
    assert command == [interpreter, "-m", "sherlock_project", "--site", "Some Site", "--version"]
    assert options["stderr"] == subprocess.STDOUT
    assert options["text"] is True
    assert options["encoding"] == "utf-8"
    assert options["env"]["PYTHONIOENCODING"] == "utf-8"
    assert "shell" not in options


def test_run_cli_argument_list_preserves_windows_paths(monkeypatch):
    arguments = ["--output", r"C:\Users\Some Name\out.txt"]
    commands = []

    def check_output(command, **kwargs):
        commands.append(command)
        return ""

    monkeypatch.setattr(subprocess, "check_output", check_output)
    Interactives.run_cli(arguments)
    assert commands == [[sys.executable, "-m", "sherlock_project", *arguments]]


def test_run_cli_preserves_cli_error_output(monkeypatch):
    def check_output(command, **kwargs):
        raise subprocess.CalledProcessError(2, command, output="CLI error: café\n")

    monkeypatch.setattr(subprocess, "check_output", check_output)
    with pytest.raises(InteractivesSubprocessError, match="CLI error: café"):
        Interactives.run_cli()
