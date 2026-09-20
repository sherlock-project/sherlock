#! /usr/bin/env python3

"""
Sherlock: Find Usernames Across Social Networks Module

This module contains the main logic to search for usernames at social
networks.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# First, we check the Python version so that the program gives a warning from the start if the system is incompatible.
if sys.version_info < (3, 9):
    python_version = sys.version.split()[0]
    print(f"Sherlock requires Python 3.9+\nYou are using Python {python_version}, which is not supported by Sherlock.")
    sys.exit(1)

from sherlock_project import sherlock

if __name__ == "__main__":
    # If the user did not enter any parameters or typed --gui, then start the GUI
    if len(sys.argv) == 1 or "--gui" in sys.argv:
        print("Starting Sherlock GUI...")

        # To prevent PyQt from giving an error, we delete the --gui parameter that we added ourselves.
        if "--gui" in sys.argv:
            sys.argv.remove("--gui")
        
        # We call the function that will launch the GUI.
        # (We specifically included the import process here so as not to slow down those who only want to use the terminal.)
        from sherlock_project.gui_app import run_gui
        run_gui()

    else:
        # We execute the original Sherlock code if the user enters standard arguments from the command line.
        sys.exit(sherlock.main())
   
