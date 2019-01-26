"""Sherlock Tests

This package contains various submodules used to run tests.
"""
import sys
import os
import subprocess as sp
from time import sleep

# uncomment this if using nose
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../sherlock')))

# import sherlock