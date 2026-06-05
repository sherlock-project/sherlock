import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't find Django :(... Did you remember to activate your venv?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
