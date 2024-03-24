import subprocess
import sys
from typing import Annotated
from pydantic import BaseModel

from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse

app = FastAPI()

class Body(BaseModel):
    usernames: list[str]
    sites: list[str]
    f: list[str]


@app.post("/")
async def root(body: Body):
    command = ["python3", "/opt/sherlock/sherlock/sherlock.py"]

    usernames = body.usernames
    sites = body.sites
    f = body.f

    if usernames:
        for name in usernames:
            command.append(name)

    if sites:
        for site in sites:
            command.append("--site")
            command.append(site)

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

        response.append(dict(name= data[0], url= data[1]))

    return response