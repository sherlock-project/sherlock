import subprocess
import platform
import re
from pathlib import Path


class Interactives:
    """
    A helper class to interact with the Sherlock CLI and perform
    file pattern searches within the sherlock_project directory.
    """

    @staticmethod
    def run_cli(args: str = "") -> str:
        """
        Run the Sherlock CLI with given arguments.

        Args:
            args (str): Command-line arguments for Sherlock.

        Returns:
            str: Output from the Sherlock command.

        Raises:
            InteractivesSubprocessError: If the subprocess returns a non-zero exit code.
        """
        command = "py -m sherlock_project" if platform.system() == "Windows" else "sherlock"
        full_command = f"{command} {args}".strip()

        try:
            result = subprocess.check_output(full_command, shell=True, stderr=subprocess.STDOUT)
            return result.decode()
        except subprocess.CalledProcessError as e:
            raise InteractivesSubprocessError(
                f"Command failed:\n{full_command}\n\nError Output:\n{e.output.decode()}"
            )

    @staticmethod
    def walk_sherlock_for_files_with(pattern: str) -> list[str]:
        """
        Recursively search for files containing a regex pattern in the sherlock_project directory.

        Args:
            pattern (str): Regular expression pattern to search for.

        Returns:
            list[str]: List of file paths containing the pattern.
        """
        compiled_pattern = re.compile(pattern)
        base_path = Path("sherlock_project")
        matching_files = []

        for file_path in base_path.rglob("*"):
            if file_path.is_file() and "__pycache__" not in str(file_path):
                try:
                    text = file_path.read_text(encoding="utf-8", errors="ignore")
                    if compiled_pattern.search(text):
                        matching_files.append(str(file_path))
                except Exception as e:
                    print(f"Skipping file {file_path}: {e}")

        return matching_files


class InteractivesSubprocessError(Exception):
    """Custom exception for subprocess errors."""
    pass


if __name__ == "__main__":
    # Example usage for testing before making a pull request
    print("Running example CLI command...")
    try:
        print(Interactives.run_cli("--help"))
    except InteractivesSubprocessError as e:
        print(e)

    print("\nSearching for pattern 'def ' in project files...")
    matches = Interactives.walk_sherlock_for_files_with(r"def ")
    print(f"Found {len(matches)} files containing 'def':")
    for match in matches:
        print(f" - {match}")
