CONTRIBUTING
============

Thank you for contributing to Sherlock. This document explains how to set up
the project locally, run tests, and propose changes (including site manifest
updates such as `confirmRegex` or `require_profile_evidence`).

Local setup
-----------

1. Recommended Python: 3.11+ (3.10 is also supported). Use a virtualenv:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

2. If you encounter macOS SSL certificate issues, configure `SSL_CERT_FILE`:

```bash
export SSL_CERT_FILE=$(python3 -c "import certifi;print(certifi.where())")
```

Running tests
-------------

Run the full test suite from the project root:

```bash
SSL_CERT_FILE=$(python3 -c "import certifi;print(certifi.where())") \
PYTHONPATH=. PATH=.:$PATH pytest -q
```

Quick live test
---------------

To run a short live demo against a single username (uses the local `data.json`):

```bash
LIVE_TEST_USERNAME=your_username_here python3 devel/live_test.py
```

Manifest changes (site-specific confirmation)
--------------------------------------------

To increase accuracy for a specific site, edit the site entry in
`sherlock_project/resources/data.json` and add one (or both) of these fields:

- `confirmRegex`: a regular expression applied to the site's HTML to
  positively identify a profile page.

- `require_profile_evidence`: boolean; when `true` Sherlock will require the
  presence of profile markers or the username in the HTML to claim a match.

Notes:
- Prefer `confirmRegex` when possible — it is authoritative and site-specific.
- Use `require_profile_evidence` only when the site returns 200 for many
  non-profile pages and you want stricter checks.

Submitting changes
------------------

- Fork the repo and create a feature branch for your change.
- Run tests and ensure they pass locally.
- Open a PR describing the change, include rationale, and reference any
  sites or examples demonstrating the change.

Style and best practices
------------------------

- Keep changes small and focused. Add unit tests for new behavior where
  practical.
- Avoid adding global heuristics where a per-site rule is feasible.

Contact
-------
If you have questions, open an issue on the repository and tag core maintainers.
