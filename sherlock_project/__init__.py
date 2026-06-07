""" Sherlock Module

This module contains the main logic to search for usernames at social
networks.

"""

from importlib.metadata import version as pkg_version, PackageNotFoundError
import pathlib
import sys


def is_frozen() -> bool:
    """Return True when running as a PyInstaller standalone executable."""
    return getattr(sys, "frozen", False)


def get_package_path() -> pathlib.Path:
    """Return the directory containing the sherlock_project package."""
    if is_frozen():
        return pathlib.Path(sys._MEIPASS) / "sherlock_project"
    return pathlib.Path(__file__).resolve().parent


def get_resource_path(filename: str) -> pathlib.Path:
    """Return the absolute path to a file under sherlock_project/resources/."""
    return get_package_path() / "resources" / filename


def get_version() -> str:
    """Fetch the version number of the installed package."""
    try:
        return pkg_version("sherlock_project")
    except PackageNotFoundError:
        if is_frozen():
            version_file = get_resource_path("version.txt")
            if version_file.is_file():
                return version_file.read_text(encoding="utf-8").strip()
            return "0.0.0+standalone"
        pyproject_path: pathlib.Path = (
            pathlib.Path(__file__).resolve().parent.parent / "pyproject.toml"
        )
        import tomli
        with pyproject_path.open("rb") as f:
            pyproject_data = tomli.load(f)
        return pyproject_data["tool"]["poetry"]["version"]

# This variable is only used to check for ImportErrors induced by users running as script rather than as module or package
import_error_test_var = None

__shortname__   = "Sherlock"
__longname__    = "Sherlock: Find Usernames Across Social Networks"
__version__     = get_version()

forge_api_latest_release = "https://api.github.com/repos/sherlock-project/sherlock/releases/latest"
# Optional tools added for GUI site management and username variations

_optional_tools = {
    "site_manager": "sherlock_project.gui.site_manager.SiteManagerFrame",
    "username_generator": "sherlock_project.username_generator.UsernameGenerator",
}


def get_optional_tools():
    """Return optional helper tools added to the Sherlock package."""
    return _optional_tools.copy()


def has_optional_tool(tool_name: str) -> bool:
    """Check whether an optional helper tool is registered."""
    return tool_name in _optional_tools


def get_optional_tool_path(tool_name: str) -> str:
    """Return the import path of an optional helper tool."""
    return _optional_tools.get(tool_name, "")