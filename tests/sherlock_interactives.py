import os
import re
import shlex
import subprocess
import sys

class Interactives:
    def run_cli(args: str | list[str] = "") -> str:
        """Run CLI arguments; strings use POSIX quoting, lists preserve paths verbatim."""
        # Use the test environment, not a launcher or executable from PATH.
        arguments = shlex.split(args) if isinstance(args, str) else args
        command = [sys.executable, "-m", "sherlock_project", *arguments]

        proc_out:str = ""
        try:
            proc_out = subprocess.check_output(
                command, stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            return proc_out
        except subprocess.CalledProcessError as e:
            raise InteractivesSubprocessError(e.output)


    def walk_sherlock_for_files_with(pattern: str) -> list[str]:
        """Check all files within the Sherlock package for matching patterns"""
        pattern:re.Pattern = re.compile(pattern)
        matching_files:list[str] = []
        for root, dirs, files in os.walk("sherlock_project"):
            for file in files:
                file_path = os.path.join(root,file)
                if "__pycache__" in file_path:
                    continue
                with open(file_path, 'r', errors='ignore') as f:
                    if pattern.search(f.read()):
                        matching_files.append(file_path)
        return matching_files

class InteractivesSubprocessError(Exception):
    pass
