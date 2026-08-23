"""Adzuna provider — official publisher API (https://developer.adzuna.com).

Access method: documented REST API for approved publishers; free tier keys
are read from environment variables. Adzuna covers every professional
industry and supports country-specific search, including Rwanda (`rw`).
Without configured credentials the provider reports itself unavailable
rather than degrading to scraping or invented listings.
"""
import os
from datetime import datetime
from typing import Any, Optional

import requests

from app.providers.base import NormalizedOpportunity, OpportunityProvider

API_BASE = "https://api.adzuna.com/v1/api/jobs"

# Countries with meaningful listing volume; Rwanda included per product need.
SUPPORTED_COUNTRIES = ("rw", "ke", "tz", "ug", "us", "gb", "de", "ca", "in", "za")


def _valid_http_url(value: Optional[str]) -> bool:
    if not value:
        return False
    value = value.strip()
    return bool(value) and value.lower().startswith(("http://", "https://"))


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def map_adzuna_job(job: dict, source_country: str) -> NormalizedOpportunity:
    """Map one Adzuna result into the normalized shape (pure function)."""
    # redirect_url points at the real apply page on the employer/Adzuna board.
    url = str(job.get("redirect_url") or "").strip()
    contract = str(job.get("contract_time") or "").strip() or None
    location = job.get("location") or {}
    company = job.get("company") or {}
    tags: list[str] = []
    if job.get("category"):
        tags.append(str(job["category"]).strip())

    return NormalizedOpportunity(
        title=str(job.get("title") or "").replace("<strong>", "").replace("</strong>", "").strip(),
        company=(str(company.get("display_name")).strip() if company.get("display_name") else None),
        location=(str(location.get("display_name")).strip() if location.get("display_name") else None),
        employment_type=contract,
        description=str(job.get("description") or "").strip(),
        requirements=[t for t in tags if t],
        source=f"Adzuna ({source_country.upper()})",
        source_url=url,
        application_url=url or None,
        published_at=_parse_date(job.get("created")),
        deadline=None,
        salary=(
            f"{int(job['salary_min']):,} - {int(job['salary_max']):,}"
            if job.get("salary_min") and job.get("salary_max")
            else None
        ),
        company_logo=None,
        sector=(str(job.get("category")).strip() if job.get("category") else None),
    )


class AdzunaProvider(OpportunityProvider):
    name = "Adzuna"
    supports_remote = True
    regions = tuple(SUPPORTED_COUNTRIES)

    def __init__(self, app_id: Optional[str] = None, app_key: Optional[str] = None):
        self.app_id = app_id or os.getenv("ADZUNA_APP_ID", "").strip()
        self.app_key = app_key or os.getenv("ADZUNA_APP_KEY", "").strip()
        self.available = bool(self.app_id and self.app_key)
        self.unavailable_reason = (
            None if self.available
            else "Adzuna API credentials are not configured (set ADZUNA_APP_ID / ADZUNA_APP_KEY)."
        )

    def search(self, query: str, limit: int = 10, categories: list[str] | None = None, countries: tuple[str, ...] = ("rw",)) -> list[NormalizedOpportunity]:
        if not self.available:
            return []
        results: list[NormalizedOpportunity] = []
        for country in countries or ("rw",):
            payload = self._fetch(country, query, limit, categories)
            if not payload and categories:
                # Category slug mismatch safety net: retry unfiltered rather
                # than silently returning nothing.
                payload = self._fetch(country, query, limit, None)
            for item in (payload or {}).get("results") or []:
                mapped = map_adzuna_job(item, country)
                if _valid_http_url(mapped.application_url):
                    results.append(mapped)
        return results[:limit]

    def _fetch(self, country: str, query: str, limit: int, categories: list[str] | None) -> dict | None:
        params: dict[str, Any] = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": max(1, min(limit, 30)),
            "what": (query or "").strip(),
            "content-type": "application/json",
        }
        if categories:
            params["category"] = categories[0]
        try:
            response = requests.get(
                f"{API_BASE}/{country}/search/1",
                params=params,
                timeout=20,
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None  # reported via status list by the caller
