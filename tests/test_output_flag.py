"""Tests for --output flag writing output without requiring --txt."""
import os
from unittest.mock import patch, MagicMock
from sherlock_project.result import QueryStatus


def _make_fake_results(claimed=True):
    """Return a minimal results dict that sherlock() would produce."""
    status = MagicMock()
    status.status = QueryStatus.CLAIMED if claimed else QueryStatus.AVAILABLE
    return {
        "FakeSite": {
            "status": status,
            "url_user": "https://fakesite.com/testuser",
        }
    }


class TestOutputFlag:
    def test_output_creates_file_without_txt_flag(self, tmp_path):
        """--output alone must write the file; --txt should not be required."""
        out_file = str(tmp_path / "results.txt")

        # Patch sherlock() so no real HTTP requests are made, and stub out the
        # site database so main() does not load the real data file.
        with patch("sherlock_project.sherlock.sherlock", return_value=_make_fake_results()):
            with patch("sherlock_project.sherlock.SitesInformation") as mock_si:
                mock_si.return_value = MagicMock(sites=[])
                from sherlock_project.sherlock import main
                with patch("sys.argv", ["sherlock", "--output", out_file, "testuser"]):
                    main()

        # File must exist regardless of whether --txt was passed.
        assert os.path.exists(out_file), (
            "--output specified but file was not created (bug: output gated on --txt)"
        )
        # And it must contain the detected result, not be an empty stub.
        with open(out_file, encoding="utf-8") as fh:
            contents = fh.read()
        assert "https://fakesite.com/testuser" in contents
        assert "Total Websites Username Detected On : 1" in contents

    def test_txt_flag_still_creates_file(self, tmp_path):
        """--txt must still write <username>.txt (regression guard for old behavior)."""
        out_file = str(tmp_path / "testuser.txt")

        with patch("sherlock_project.sherlock.sherlock", return_value=_make_fake_results()):
            with patch("sherlock_project.sherlock.SitesInformation") as mock_si:
                mock_si.return_value = MagicMock(sites=[])
                from sherlock_project.sherlock import main
                with patch(
                    "sys.argv",
                    ["sherlock", "--txt", "--folderoutput", str(tmp_path), "testuser"],
                ):
                    main()

        assert os.path.exists(out_file), "--txt no longer writes its output file"
        with open(out_file, encoding="utf-8") as fh:
            assert "https://fakesite.com/testuser" in fh.read()
