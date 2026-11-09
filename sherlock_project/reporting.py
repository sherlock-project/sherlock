from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from sherlock_project import __version__
from sherlock_project.result import QueryStatus


def build_username_report(username: str, results: dict) -> dict:
    summary = {status.value: 0 for status in QueryStatus}
    sites = []
    for site_name, site_data in results.items():
        result = site_data["status"]
        status = result.status.value
        summary[status] += 1
        http_status = site_data.get("http_status")
        sites.append(
            {
                "name": site_name,
                "url_main": site_data.get("url_main"),
                "url_user": site_data.get("url_user"),
                "status": status,
                "http_status": http_status if isinstance(http_status, int) else None,
                "response_time_s": result.query_time,
                "context": result.context,
            }
        )
    return {"username": username, "summary": summary, "sites": sites}


def write_json_report(path: str | Path, reports: list[dict]) -> None:
    destination = Path(path)
    temporary_path = None
    try:
        with NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            json.dump(
                {
                    "schema_version": 1,
                    "sherlock_version": __version__,
                    "results": reports,
                },
                stream,
                ensure_ascii=False,
                indent=2,
                allow_nan=False,
            )
            stream.write("\n")
        os.replace(temporary_path, destination)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
