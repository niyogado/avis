"""Opportunity search: strict application-URL validation, routing, AI layer."""
from unittest.mock import patch

from app.providers.adzuna import map_adzuna_job
from app.providers.base import NormalizedOpportunity
from app.services.opportunity_ai import enrich_opportunities, suggest_expansion_queries
from app.services.opportunity_service import (
    _valid_http_url,
    resolve_routing,
    search_opportunities,
)


def _opp(**overrides):
    base = dict(
        title="Backend Developer",
        company="Acme",
        location="Remote",
        employment_type="full_time",
        description="Build APIs with Python, FastAPI and PostgreSQL.",
        requirements=["Python", "FastAPI"],
        source="Test",
        source_url="https://example.test/job/1",
        application_url="https://example.test/job/1",
    )
    base.update(overrides)
    return NormalizedOpportunity(**base)


def _fake_registry(monkeypatch, provider):
    import app.providers as providers_pkg

    monkeypatch.setattr(providers_pkg, "build_registry", lambda: [provider])


def test_valid_http_url_accepts_only_real_links():
    assert _valid_http_url("https://remotive.com/job/1")
    assert _valid_http_url("http://example.org/x")
    assert not _valid_http_url(None)
    assert not _valid_http_url("")
    assert not _valid_http_url("   ")
    assert not _valid_http_url("javascript:alert(1)")
    assert not _valid_http_url("/relative/path")
    assert not _valid_http_url("remotive.com/job")


def test_search_drops_opportunities_without_application_url(monkeypatch):
    class FakeProvider:
        name = "Fake"
        available = True
        supports_remote = True
        regions = ("global-remote",)
        unavailable_reason = None

        def search(self, query, limit=10, categories=None):
            return [
                _opp(title="Valid job"),
                _opp(title="No url job", application_url=None),
                _opp(title="Empty url job", application_url=""),
            ]

    _fake_registry(monkeypatch, FakeProvider())
    results = search_opportunities(queries=["Backend Developer"], target_roles=["Backend Developer"])
    titles = [job["title"] for job in results["jobs"]]
    assert titles == ["Valid job"]
    for job in results["jobs"]:
        assert job["application_url"].startswith("http")
        assert job["url"] == job["application_url"]


def test_search_multi_query_dedupes_and_caps(monkeypatch):
    class FakeProvider:
        name = "Fake"
        available = True
        supports_remote = True
        regions = ("global-remote",)
        unavailable_reason = None

        def search(self, query, limit=10, categories=None):
            # Same listing returned for every query must appear only once.
            return [_opp(title="Duplicate"), _opp(title=f"{query} role")]

    _fake_registry(monkeypatch, FakeProvider())
    results = search_opportunities(
        queries=["nurse", "healthcare"],
        target_roles=["Nurse"],
        max_cards=3,
    )
    titles = [job["title"] for job in results["jobs"]]
    assert len(titles) == len(set(titles))
    assert len(titles) <= 3


def test_routing_rwanda_local_skips_global_remote():
    routing = resolve_routing(["Kigali"], "onsite")
    assert routing["intent"] == "rwanda_local"
    assert routing["show_remotive"] is False


def test_routing_rwanda_remote_includes_global_remote():
    routing = resolve_routing(["Kigali", "Remote"], "remote")
    assert routing["intent"] == "rwanda_remote"
    assert routing["show_remotive"] is True


def test_routing_international_remote_and_unknown():
    assert resolve_routing(["Remote"], "remote")["intent"] == "international_remote"
    unknown = resolve_routing([], None)
    assert unknown["intent"] == "unknown"
    assert unknown["show_remotive"] is True


def test_enrich_falls_back_gracefully_when_ai_fails():
    jobs = [{
        "title": "Staff Nurse",
        "description": "Ward care <p>and</p> patient support duties. " * 10,
        "match_reasons": ["✓ Skill: patient care"],
        "application_url": "https://hospital.example/apply",
    }]
    with patch(
        "app.services.opportunity_ai.chat_with_ai",
        side_effect=RuntimeError("EjoChat down"),
    ):
        enriched = enrich_opportunities(jobs, {"user_confirmation": {"primary_role": "Clinical Nurse"}})

    assert enriched[0]["ai_match_insight"] is None
    assert "patient support" in enriched[0]["description_snippet"]
    assert "<p>" not in enriched[0]["description_snippet"]
    assert enriched[0]["application_url"] == "https://hospital.example/apply"


def test_enrich_uses_ai_insight_when_valid_json():
    jobs = [{"title": "Accountant", "description": "Ledgers", "application_url": "https://x.example/a"}]
    ai_payload = '{"insights": [{"index": 0, "match_insight": "Matches your ledger reconciliation background.", "snippet": "Handles ledgers."}]}'
    with patch("app.services.opportunity_ai.chat_with_ai", return_value=ai_payload):
        enriched = enrich_opportunities(jobs, {"user_confirmation": {"primary_role": "Financial Accountant"}})
    assert enriched[0]["ai_match_insight"] == "Matches your ledger reconciliation background."
    assert enriched[0]["description_snippet"] == "Handles ledgers."


def test_expansion_queries_fallback_when_ai_fails():
    context = {
        "user_confirmation": {
            "primary_role": "Clinical Nurse",
            "target_roles": ["Nurse Educator"],
            "career_interests": ["Healthcare Management"],
        },
    }
    with patch("app.services.opportunity_ai.chat_with_ai", side_effect=RuntimeError("down")):
        terms = suggest_expansion_queries(context)
    assert "Clinical Nurse" in terms
    assert "Nurse Educator" in terms


def test_adzuna_mapper_requires_redirect_url_shape():
    mapped = map_adzuna_job({
        "title": "<strong>Ward</strong> Nurse",
        "company": {"display_name": "Kigali Clinic"},
        "location": {"display_name": "Kigali, Rwanda"},
        "contract_time": "full_time",
        "description": "Provide ward care.",
        "redirect_url": "https://www.adzuna.com/r/apply/123",
        "created": "2026-08-20T00:00:00Z",
        "salary_min": 500000,
        "salary_max": 900000,
        "category": "Healthcare",
    }, "rw")
    assert mapped.title == "Ward Nurse"
    assert mapped.application_url.startswith("https://")
    assert mapped.source == "Adzuna (RW)"
    assert mapped.sector == "Healthcare"