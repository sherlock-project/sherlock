from pathlib import Path

from beyond_naked_eye.cli import main
from beyond_naked_eye.core.first_launch import run_first_launch_init

if __name__ == "__main__":
    run_first_launch_init(Path(__file__).resolve().parent)
    main()
