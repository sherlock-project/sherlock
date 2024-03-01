import subprocess
import sys
from typing import Annotated

from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.get("/")
async def root(
    usernames: Annotated[list[str] | None, Query()] = None,
    f: Annotated[list[str] | None, Query()] = None,
):
    command = ["python3", "/opt/sherlock/sherlock/sherlock.py"]

    if usernames:
        for name in usernames:
            command.append(name)

    if f:
        for flag in f:
            command.append("--"+flag)

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=sys.stderr)

    response = []

    for line in iter(process.stdout.readline, b''):
        line = line.decode("utf-8").rstrip("\n").rstrip("\r")[4:]

        if line == "":
            continue

        if line.startswith("Checking username"):
            continue

        if line.startswith("Search complete"):
            continue

        data = line.split(": ")

        response.append(dict(name= data[0], link= data[1]))

    return response