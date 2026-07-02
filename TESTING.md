Testing and CI
===============

Run tests locally (recommended inside a virtualenv):

```bash
python3 -m pip install -r requirements-dev.txt
SSL_CERT_FILE=$(python3 -c "import certifi;print(certifi.where())") PYTHONPATH=. PATH=.:$PATH pytest -q
```

Notes:
- `SSL_CERT_FILE` points `urllib` to `certifi`'s CA bundle to avoid local macOS Python certificate issues.
- `PYTHONPATH` and `PATH` ensure the local package and `sherlock` launcher are used by tests.
