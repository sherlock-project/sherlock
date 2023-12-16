import sys

def handler(signal_received, frame):
    """Exit gracefully without throwing errors

    Source: https://www.devdungeon.com/content/python-catch-sigint-ctrl-c
    """
    sys.exit(0)