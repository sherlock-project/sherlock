# Sherlock Master Summary

## Overview

Sherlock is a Python CLI OSINT tool for checking whether a username exists across 400+ social networks. It runs large batches of site checks in parallel, classifies each result (claimed, available, unknown, illegal, or WAF-blocked), and can export findings to text, CSV, and XLSX outputs.

## Product Scope

- **Primary use case:** Username reconnaissance across many social platforms.
- **Execution modes:** Local CLI, Docker image, package-manager installs, and an Apify Actor wrapper for cloud/serverless usage.
- **Data source model:** Site definitions are loaded from a JSON manifest (remote by default, local optional) with optional false-positive exclusions.

## Core Architecture

| Area | Responsibility | Key Files |
| - | - | - |
| CLI entrypoint | Validates Python version and launches CLI flow | `sherlock_project/__main__.py` |
| Main engine | Parses arguments, runs concurrent network checks, evaluates detection logic | `sherlock_project/sherlock.py` |
| Site catalog loader | Loads site metadata from local/remote JSON and applies exclusions/NSFW filters | `sherlock_project/sites.py` |
| Result model | Standard query states and per-site result objects | `sherlock_project/result.py` |
| User output/notifications | Console reporting, optional browser opening, result counting | `sherlock_project/notify.py` |

## Runtime Behavior

1. User provides one or more usernames (with optional `{?}` variants).
2. Site definitions are loaded from the live manifest by default (`https://data.sherlockproject.xyz`) unless a local/alternate JSON source is explicitly provided.
3. Sherlock builds request jobs for selected sites and executes them concurrently.
4. Responses are evaluated using per-site rules (`errorType`, response text, redirect behavior, status code, regex constraints, etc.).
5. Results are emitted to terminal and optionally written to files (`.txt`, `.csv`, `.xlsx`).

## Configuration and Dependencies

- **Python support:** 3.9+ (project targets modern Python versions up to 3.13 in metadata).
- **Core dependencies:** `requests`, `requests-futures`, `PySocks`, `colorama`, `pandas`, `openpyxl`.
- **Packaging/build:** Poetry metadata in `pyproject.toml`, CLI command exposed as `sherlock`.

## Security and Reliability Notes

- Only the latest Sherlock release is considered supported per project policy.
- Vulnerability disclosure is handled through GitHub Security Advisories.
- Some platforms are intentionally excluded or removed when deterministic username detection is no longer reliable (`docs/removed-sites.md`).

## Operational Ecosystem

- **Documentation hub:** `docs/README.md`
- **Packaging mini-readme (PyPI):** `docs/pyproject/README.md`
- **Cloud wrapper documentation:** `.actor/README.md`
- **Site-data/exclusion lifecycle automation:** repository workflows under `.github/workflows/`

## Practical Takeaway

Sherlock is a mature, concurrency-first username enumeration tool with a clear separation between detection logic, site metadata, and reporting/output layers. The project emphasizes broad platform coverage, practical CLI ergonomics, and controlled quality via exclusions and documented removals when site behavior changes.
