from sherlock_project.risk import RiskAssessment, build_risk_analyzer


def test_build_risk_analyzer_returns_none_when_disabled():
    analyzer = build_risk_analyzer(enabled=False, config_path=None, site_data={})
    assert analyzer is None


def test_heuristic_detector_scores_keyword_matches():
    site_data = {
        "ExampleSite": {
            "riskHints": {
                "threshold": 0.2,
                "keywords": [
                    {"pattern": "phishing", "weight": 0.4, "label": "phishing"},
                    {"pattern": "flag", "weight": 0.1},
                ],
            }
        }
    }

    analyzer = build_risk_analyzer(enabled=True, config_path=None, site_data=site_data)
    assert analyzer is not None

    assessment = analyzer.evaluate(
        username="example",
        site_name="ExampleSite",
        response_text="This profile is phishing new users.",
        site_metadata=site_data["ExampleSite"],
    )

    assert isinstance(assessment, RiskAssessment)
    assert assessment.label == "phishing"
    assert assessment.score is not None and assessment.score >= 0.4
    assert assessment.has_signals


def test_heuristic_detector_below_threshold_uses_default_label():
    site_data = {
        "LowSignal": {
            "riskHints": {
                "threshold": 0.8,
                "keywords": [
                    {"pattern": "maybe", "weight": 0.2}
                ],
            }
        }
    }

    analyzer = build_risk_analyzer(enabled=True, config_path=None, site_data=site_data)
    assert analyzer is not None

    assessment = analyzer.evaluate(
        username="user",
        site_name="LowSignal",
        response_text="maybe suspicious",
        site_metadata=site_data["LowSignal"],
    )

    assert isinstance(assessment, RiskAssessment)
    assert assessment.label == "unknown"
    assert assessment.score is not None and assessment.score < 0.8
