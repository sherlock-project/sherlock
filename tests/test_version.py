import os
from sherlock_interactives import Interactives
import sherlock_project
from sherlock_project import get_resource_path, is_frozen

def test_versioning() -> None:
    # Ensure __version__ matches version presented to the user
    assert sherlock_project.__version__ in Interactives.run_cli("--version")
    # Ensure __init__ is single source of truth for __version__ in package
    # Temporarily allows sherlock.py so as to not trigger early upgrades
    found:list = Interactives.walk_sherlock_for_files_with(r'__version__ *= *')
    expected:list = [
        # Normalization is REQUIRED for Windows ( / vs \ )
        os.path.normpath("sherlock_project/__init__.py"),
    ]
    # Sorting is REQUIRED for Mac
    assert sorted(found) == sorted(expected)


def test_standalone_helpers() -> None:
    assert is_frozen() is False
    data_json = get_resource_path("data.json")
    assert data_json.name == "data.json"
    assert data_json.is_file()
    package_path = sherlock_project.get_package_path()
    assert (package_path / "sherlock.py").is_file()
    assert (package_path / "resources" / "data.json").is_file()


def test_format_version_string() -> None:
    from sherlock_project.sherlock import format_version_string
    version_string = format_version_string()
    assert sherlock_project.__version__ in version_string
    assert "standalone executable" not in version_string
