import os
import platform
import re
import subprocess

class Interactives:
    def run_cli(args:str = "") -> str:
        """Pass arguments to Sherlock as a normal user on the command line"""
        # Adapt for platform differences (Windows likes to be special)
        if platform.system() == "Windows":
            command:str = f"py -m sherlock_project {args}"
        else:
            command:str = f"sherlock {args}"

        proc_out:str = ""
        try:
            proc_out = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return proc_out.decode()
        except subprocess.CalledProcessError as e:
            raise InteractivesSubprocessError(e.output.decode())


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
