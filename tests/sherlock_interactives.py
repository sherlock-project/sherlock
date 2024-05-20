import os
import re
import subprocess

class Interactives:
    def run_cli(args: str = "") -> str:
        command = [f"sherlock {args}"]
        proc_out = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return proc_out.decode()

    def walk_sherlock_for_files_with(pattern: str) -> list[str]:
        pattern: re.Pattern = re.compile(pattern)
        matching_files: list[str] = []
        for root, dirs, files in os.walk("sherlock"):
            for file in files:
                file_path = os.path.join(root,file)
                if "__pycache__" in file_path:
                    continue
                with open(file_path, 'r', errors='ignore') as f:
                    if pattern.search(f.read()):
                        matching_files.append(file_path)
        return matching_files
