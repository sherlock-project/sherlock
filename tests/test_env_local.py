import os

from sherlock_project import sherlock


def test_load_local_environment_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env.local"
    env_file.write_text(
        '\n'.join(
            [
                'NUMVERIFY_API_KEY="numverify"',
                "GOOGLECSE_CX=custom-search-engine",
                "GOOGLE_API_KEY='google-api-key'",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("NUMVERIFY_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLECSE_CX", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    loaded_path = sherlock.load_local_environment()

    assert loaded_path == env_file
    assert os.environ["NUMVERIFY_API_KEY"] == "numverify"
    assert os.environ["GOOGLECSE_CX"] == "custom-search-engine"
    assert os.environ["GOOGLE_API_KEY"] == "google-api-key"


def test_load_local_environment_respects_existing_value(tmp_path, monkeypatch):
    env_file = tmp_path / ".env.local"
    env_file.write_text('NUMVERIFY_API_KEY="from-file"', encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NUMVERIFY_API_KEY", "pre-existing")

    sherlock.load_local_environment()

    assert os.environ["NUMVERIFY_API_KEY"] == "pre-existing"


def test_load_local_environment_skips_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert sherlock.load_local_environment() is None


def test_load_environment_file_raises_for_invalid_line(tmp_path):
    env_file = tmp_path / ".env.local"
    env_file.write_text("NOT_VALID", encoding="utf-8")

    try:
        sherlock.load_environment_file(env_file)
        assert False, "Expected load_environment_file to raise ValueError."
    except ValueError as error:
        assert "KEY=VALUE" in str(error)
