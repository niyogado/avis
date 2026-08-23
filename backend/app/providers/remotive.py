"""Remotive provider — official public API (https://remotive.com/api/remote-jobs).

Access method: documented public JSON API explicitly offered for
consumption by Remotive. No scraping involved.
"""
import re
from datetime import datetime
from typing import Any, Optional

import requests

from app.providers.base import NormalizedOpportunity, OpportunityProvider

API_URL = "https://remotive.com/api/remote-jobs"

_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def _html_to_text(html: str) -> str:
    text = _TAG_RE.sub(" ", html or "")
    return _WHITESPACE_RE.sub(" ", text).strip()


class ProviderUnavailableError(Exception):
    pass


def map_remotive_job(job: dict, fetched_at: Optional[datetime] = None) -> NormalizedOpportunity:
    """Map one Remotive API job into the normalized shape (pure function)."""
    published = None
    raw_published = job.get("publication_date")
    if raw_published:
        try:
            published = datetime.fromisoformat(str(raw_published).replace("Z", "+00:00"))
        except ValueError:
            published = None

    tags = [str(tag).strip() for tag in (job.get("tags") or []) if str(tag).strip()]
    url = str(job.get("url") or "").strip()
    logo = (
        str(job.get("company_logo") or job.get("company_logo_url") or "").strip() or None
    )

    return NormalizedOpportunity(
        title=str(job.get("title") or "").strip(),
        company=(str(job.get("company_name")).strip() if job.get("company_name") else None),
        location=(str(job.get("candidate_required_location")).strip() if job.get("candidate_required_location") else None),
        employment_type=(str(job.get("job_type")).replace("_", " ") if job.get("job_type") else None),
        description=_html_to_text(str(job.get("description") or "")),
        requirements=tags,
        source="Remotive",
        source_url=url,
        # Remotive lists jobs on the same page where the user applies.
        application_url=url or None,
        published_at=published,
        deadline=None,
        salary=(str(job.get("salary")).strip() if job.get("salary") else None),
        company_logo=(logo if _valid_application_url(logo) else None),
        sector=(str(job.get("category")).strip() if job.get("category") else None),
    )


def _valid_application_url(value: str | None) -> bool:
    """True only when the value is a real http(s) URL (strict validation rule).

    Any job missing a valid direct application link is rejected entirely so the
    frontend never renders a card with a broken, missing, or placeholder button.
    """
    if not value:
        return False
    value = value.strip()
    return value.lower().startswith(("http://", "https://"))


class RemotiveProvider(OpportunityProvider):
    name = "Remotive"
    available = True
    supports_remote = True
    regions = ("global-remote",)

    def search(self, query: str, limit: int = 10, categories: list[str] | None = None) -> list[NormalizedOpportunity]:
        params: dict[str, Any] = {
            "search": (query or "").strip(),
            "limit": max(1, min(limit, 20)),
        }
        # Best-effort industry filter. NOTE: Remotive has been observed to
        # ignore search/category params at times; AVIS therefore never trusts
        # this filter alone — the caller re-validates every card's domain.
        if categories:
            params["category"] = categories[0]
        response = requests.get(API_URL, params=params, timeout=20)
        response.raise_for_status()
        payload = response.json()
        jobs = payload.get("jobs") or []
        # Strict validation: drop any listing that lacks a valid application URL.
        return [
            job
            for job in (map_remotive_job(item) for item in jobs[:limit])
            if _valid_application_url(job.application_url)
        ]
