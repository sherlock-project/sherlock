from sherlock_interactives import Interactives
import sherlock

def test_versioning() -> None:
    # Ensure __version__ matches version presented to the user
    assert sherlock.__version__ in Interactives.run_cli("--version")
    # Ensure __init__ is single source of truth for __version__ in package
    # Temporarily allows sherlock.py so as to not trigger early upgrades
    assert Interactives.walk_sherlock_for_files_with(r'__version__ *= *') == [ "sherlock/__init__.py", "sherlock/sherlock.py" ]
