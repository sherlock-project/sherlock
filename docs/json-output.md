# JSON output

Use `--json-output PATH` to save all requested usernames in one machine-readable
UTF-8 file. It can be combined with the existing TXT, CSV and XLSX exports.

```bash
sherlock user123 --json-output results.json
sherlock user1 user2 --json-output results.json
sherlock "user{?}name" --json-output results.json
```

Wildcard usernames are expanded before the report is built. Each expanded
username gets its own entry, in request order.

## Site manifests are separate

The existing `--json` / `-j` option selects a site manifest, not an output format.
Both options can be used together:

```bash
sherlock user123 --json custom-sites.json --json-output results.json
```

## Report format (schema version 1)

```json
{
  "schema_version": 1,
  "sherlock_version": "0.16.2",
  "results": [
    {
      "username": "example",
      "summary": {
        "Claimed": 1,
        "Available": 0,
        "Unknown": 0,
        "Illegal": 0,
        "WAF": 0
      },
      "sites": [
        {
          "name": "Example Site",
          "url_main": "https://example.org",
          "url_user": "https://example.org/example",
          "status": "Claimed",
          "http_status": 200,
          "response_time_s": 0.125,
          "context": null
        }
      ]
    }
  ]
}
```

- `sherlock_version` identifies the installed version used for the report.
- `summary` counts each query status for that username.
- `sites` contains **all** checked sites, regardless of `--print-found` or
  `--print-all`. A site is not necessarily a detected account.
- Statuses preserve Sherlock's existing verdicts: `Claimed`, `Available`,
  `Unknown`, `Illegal` and `WAF`. Blocked and failed checks remain distinguishable
  from both detected and unavailable usernames.
- Missing HTTP status codes and query times are JSON `null`. A measured
  `0.0` seconds remains a number.
- `context` contains the query's error context, when provided by Sherlock.
- Raw response bodies and internal request objects are not included.
- Non-ASCII usernames are written directly as UTF-8.

## Writing and errors

The report is written after all requested usernames finish. The destination's
parent directory must already exist. Relative paths use the current working
directory; they are independent of `--output` and `--folderoutput`.

An existing report is replaced only after the new JSON has been written
successfully to a temporary file in the same directory. Serialization or write
failures leave the existing report unchanged and remove the temporary file.
An interrupted scan does not replace an existing report.

If the report cannot be written, the CLI prints an error to stderr and exits
with status 1. Terminal results and other completed exports remain available.

## Development checks

```bash
python -m pytest tests/test_json_output.py -q
python -m pytest tests -m "not online and not validate_targets" -q
```

The JSON-report tests use mocked scans and block unexpected network requests.
They cover all query statuses, Unicode, multiple and wildcard usernames,
existing export compatibility, invalid JSON values and atomic-write failures.
