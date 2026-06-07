""" Sherlock Module

This module contains the main logic to search for usernames at social
networks.

"""

from importlib.metadata import version as pkg_version, PackageNotFoundError
import pathlib
import tomli


def get_version() -> str:
    """Fetch the version number of the installed package."""
    try:
        return pkg_version("sherlock_project")
    except PackageNotFoundError:
        pyproject_path: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent / "pyproject.toml"
        with pyproject_path.open("rb") as f:
            pyproject_data = tomli.load(f)
        return pyproject_data["tool"]["poetry"]["version"]

# This variable is only used to check for ImportErrors induced by users running as script rather than as module or package
import_error_test_var = None

__shortname__   = "Sherlock"
__longname__    = "Sherlock: Find Usernames Across Social Networks"
__version__     = get_version()

forge_api_latest_release = "https://api.github.com/repos/sherlock-project/sherlock/releases/latest"


def get_search_history_summary() -> dict:
    """Return a summary of the local search history.

    Provides a high-level overview of persisted search data without
    requiring callers to import and instantiate LocalStorage directly.

    Returns:
        dict with keys:
            - total_searches (int): Number of saved search entries.
            - unique_usernames (int): Count of distinct usernames queried.
            - latest_search (dict | None): The most recent search entry,
              or None if history is empty.
            - storage_path (str): Path to the local history directory.
    """
    from sherlock_project.storage import LocalStorage

    storage = LocalStorage()
    history = storage.load_search_history()

    if not history:
        return {
            "total_searches": 0,
            "unique_usernames": 0,
            "latest_search": None,
            "storage_path": str(storage.history_dir),
        }

    unique_usernames = len({h.get("query", "") for h in history})
    return {
        "total_searches": len(history),
        "unique_usernames": unique_usernames,
        "latest_search": history[0],
        "storage_path": str(storage.history_dir),
    }
