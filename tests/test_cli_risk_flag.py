from types import SimpleNamespace

import pytest

from sherlock_project import sherlock as cli
from sherlock_project.result import QueryResult, QueryStatus
from sherlock_project.risk import RiskAssessment, RiskSignal


class DummyAnalyzer:
    def __init__(self):
        self.calls = []

    def evaluate(self, username, site_name, response_text, site_metadata):
        self.calls.append((username, site_name, response_text))
        assessment = RiskAssessment(label="phishing", score=0.7, confidence=0.8)
        assessment.add_signal(RiskSignal(source="test", message="matched", weight=0.5))
        return assessment


class DummySitesInformation:
    def __init__(self, *args, **kwargs):
        self._site = SimpleNamespace(
            name="Example",
            information={
                "urlMain": "https://example.com",
                "url": "https://example.com/{}",
                "errorType": "status_code",
                "errorCode": [404],
                "username_claimed": "claimed",
                "riskHints": {
                    "threshold": 0.2,
                    "keywords": [{"pattern": "phishing", "weight": 0.5, "label": "phishing"}],
                },
            },
        )

    def remove_nsfw_sites(self, *_, **__):  # noqa: D401 - simple stub
        return self

    def __iter__(self):
        yield self._site


class DummyResponse:
    def __init__(self, payload: str = "{\"tag_name\": \"v0.16.0\", \"html_url\": \"\"}") -> None:
        self.text = payload
        self.status_code = 200

    def json(self):  # pragma: no cover - compatibility helper
        return {}


@pytest.fixture
def dummy_analyzer(monkeypatch):
    analyzer = DummyAnalyzer()

    def fake_builder(enabled, config_path, site_data):
        assert enabled is True
        return analyzer

    monkeypatch.setattr(cli, "build_risk_analyzer", fake_builder)
    return analyzer


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    monkeypatch.setattr(cli, "SitesInformation", DummySitesInformation)
    monkeypatch.setattr(cli.requests, "get", lambda *_, **__: DummyResponse())


def test_cli_invokes_risk_analyzer(monkeypatch, tmp_path, dummy_analyzer):
    # Prevent file creation by running in temporary directory and disabling txt export.
    monkeypatch.chdir(tmp_path)

    def fake_sherlock(username, site_data, query_notify, **kwargs):
        analyzer = kwargs.get("risk_analyzer")
        assert analyzer is dummy_analyzer
        risk = analyzer.evaluate(username, "Example", "phishing content", site_data["Example"])
        result = QueryResult(
            username=username,
            site_name="Example",
            site_url_user="https://example.com/user",
            status=QueryStatus.CLAIMED,
            query_time=0.12,
            risk=risk,
        )
        return {
            "Example": {
                "url_main": "https://example.com",
                "url_user": "https://example.com/user",
                "status": result,
                "http_status": 200,
                "response_text": "phishing content",
                "risk": risk,
            }
        }

    monkeypatch.setattr(cli, "sherlock", fake_sherlock)

    monkeypatch.setattr("sys.argv", ["sherlock", "--risk", "--no-txt", "testuser"])

    cli.main()

    assert dummy_analyzer.calls, "Risk analyzer should receive at least one evaluation call"
