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
        return b"Sherlock output\n"

    monkeypatch.setattr(subprocess, "check_output", check_output)
    assert Interactives.run_cli('--site "Some Site" --version') == "Sherlock output\n"
    assert calls == [(
        [interpreter, "-m", "sherlock_project", "--site", "Some Site", "--version"],
        {"stderr": subprocess.STDOUT},
    )]


def test_run_cli_preserves_cli_error_output(monkeypatch):
    def check_output(command, **kwargs):
        raise subprocess.CalledProcessError(2, command, output=b"CLI error\n")

    monkeypatch.setattr(subprocess, "check_output", check_output)
    with pytest.raises(InteractivesSubprocessError, match="CLI error"):
        Interactives.run_cli()
