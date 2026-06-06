import csv
import io
import json
from typing import List

from apps.core.dtos import SiteResult


def to_csv(results: List[SiteResult]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["site_name", "url", "status"])
    for r in results:
        writer.writerow([r.site_name, r.url, r.status])
    return output.getvalue()


def to_json(results: List[SiteResult], username: str) -> str:
    hits = [
        {
            "site_name": r.site_name,
            "url": r.url,
            "status": r.status,
            "response_time_ms": r.response_time_ms,
            "error_message": r.error_message,
        }
        for r in results
    ]
    return json.dumps({"username": username, "hits": hits})
