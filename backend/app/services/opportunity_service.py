"""Opportunity search: provider selection, dedup, and transparent matching.

Match scores are computed from real component overlaps (skills, role,
location). When the user context is too thin to score reliably, a
qualitative band (strong/potential/limited) is returned instead of a
fabricated percentage.
"""
import re
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from app.services.domain_intelligence import UserDomain

from app.providers.base import NormalizedOpportunity, ProviderStatus

_WORD_RE = re.compile(r"[a-z0-9+#./-]+")

_STOPWORDS = {
    "the", "and", "for", "with", "you", "your", "our", "are", "will", "job",
    "jobs", "role", "work", "team", "company", "experience", "years", "year",
    "senior", "junior", "remote", "full", "time", "part", "contract",
}


def tokenize(text: str) -> set[str]:
    return {token for token in _WORD_RE.findall((text or "").lower()) if token not in _STOPWORDS and len(token) > 1}


def _valid_http_url(value: str | None) -> bool:
    """Strict application-URL rule shared by every source.

    An opportunity is only renderable when it carries a real, direct http(s)
    application link. Missing/empty/non-http values are rejected and dropped.
    """
    value = (value or "").strip()
    return bool(value) and value.lower().startswith(("http://", "https://"))


def resolve_routing(preferred_locations: list[str], work_preference: str | None) -> dict[str, Any]:
    """Smart source routing based on confirmed user context.

    - Rwanda/local onsite preference -> local-capable providers only.
    - Remote (with or without Rwanda) -> local providers + global remote boards.
    - Unknown -> honest default including global remote boards.
    """
    locs = {(loc or "").strip().lower() for loc in (preferred_locations or []) if (loc or "").strip()}
    remote = (work_preference or "").strip().lower() == "remote" or "remote" in locs
    rwanda = any(
        loc == "rwanda" or "rwanda" in loc or loc == "kigali" or loc.startswith("kigali")
        for loc in locs
    )

    if remote and rwanda:
        return {
            "intent": "rwanda_remote",
            "show_remotive": True,
            "reason": "You prefer remote work and Rwanda-based opportunities. AVIS searches local-capable sources plus global remote boards.",
        }
    if rwanda and not remote:
        return {
            "intent": "rwanda_local",
            "show_remotive": False,
            "reason": "You prefer roles in or near Rwanda. AVIS prioritizes local-capable sources over international remote-only boards.",
        }
    if remote:
        return {
            "intent": "international_remote",
            "show_remotive": True,
            "reason": "You prefer remote/international roles. AVIS shows validated remote job cards from live providers.",
        }
    return {
        "intent": "unknown",
        "show_remotive": True,
        "reason": "No confirmed location preference yet. AVIS searches local-capable sources and global remote boards until you confirm.",
    }


def _contains_phrase(haystack_tokens: set[str], phrase: str) -> bool:
    """True when every word of `phrase` appears in the haystack tokens."""
    words = [word for word in _WORD_RE.findall(phrase.lower()) if word]
    if not words:
        return False
    return all(word in haystack_tokens for word in words)


@dataclass
class MatchResult:
    band: str  # strong | potential | limited | unknown
    score: int | None = None
    reasons: list[str] = field(default_factory=list)
    components: dict[str, Any] = field(default_factory=dict)


def match_opportunity(
    opportunity: NormalizedOpportunity,
    *,
    target_roles: list[str],
    confirmed_skills: list[str],
    evidence_skills: list[str],
    preferred_locations: list[str],
    provider_supports_remote: bool = False,
) -> MatchResult:
    title_tokens = tokenize(opportunity.title)
    body_tokens = title_tokens | tokenize(opportunity.description)

    # Skills: user-confirmed skills take priority; CV evidence fills in.
    skill_terms = confirmed_skills or evidence_skills
    matched_skills = [
        term for term in skill_terms
        if _contains_phrase(body_tokens, term) or _contains_phrase(set(opportunity.requirements), term)
    ]

    # Role: any confirmed target role overlapping the job title.
    role_hits = [role for role in target_roles if _contains_phrase(title_tokens | tokenize(role), role)]
    role_hit = bool(target_roles) and bool(role_hits)

    # Location: remote preference or overlap with preferred locations.
    job_location_tokens = tokenize(opportunity.location or "")
    location_hit = False
    for preferred in preferred_locations:
        pref = preferred.strip().lower()
        if pref == "remote":
            if provider_supports_remote:
                location_hit = True
                break
        elif _contains_phrase(job_location_tokens, preferred):
            location_hit = True
            break

    reasons = []
    for term in matched_skills[:6]:
        reasons.append(f"✓ Skill: {term}")
    if role_hit:
        reasons.append(f"✓ Role aligns with your target: {', '.join(role_hits[:2])}")
    if location_hit:
        reasons.append("✓ Location fits your preference")

    can_score = bool(skill_terms) and bool(opportunity.description)
    if can_score:
        skill_ratio = len(matched_skills) / max(1, min(len(skill_terms), 8))
        score = round(min(60, skill_ratio * 60)) + (25 if role_hit else 0) + (15 if location_hit else 0)
        score = max(0, min(100, score))
        band = "Strong match" if score >= 65 else "Potential match" if score >= 35 else "Limited match"
        return MatchResult(band=band, score=score, reasons=reasons, components={
            "skill_ratio": round(skill_ratio, 2),
            "role_hit": role_hit,
            "location_hit": location_hit,
        })

        # Not enough verified signal for a number — be honest with a band only.
    if matched_skills and (role_hit or location_hit):
        band = "Strong match"
    elif matched_skills or role_hit or location_hit:
        band = "Potential match"
    else:
        band = "Limited match"
    return MatchResult(band=band, score=None, reasons=reasons, components={
        "skill_ratio": None,
        "role_hit": role_hit,
        "location_hit": location_hit,
    })


def search_opportunities(
    *,
    queries: list[str],
    limit_per_query: int = 12,
    max_cards: int = 30,
    target_roles: list[str] | None = None,
    confirmed_skills: list[str] | None = None,
    evidence_skills: list[str] | None = None,
    preferred_locations: list[str] | None = None,
    include_global_remote: bool = True,
    user_domain: "UserDomain | None" = None,
) -> dict[str, Any]:
    """Search registered providers across multiple keyword queries.

    - Every query runs against every available provider (providers that only
      carry global-remote listings are skipped when routing says local-only,
      or when the candidate's domain is predominantly local/physical).
    - Results are de-duplicated, STRICTLY validated for a real application
      URL, checked against the candidate's professional domain, transparently
      matched against the user's context, and capped.
    - Providers without verified permitted access are reported as unavailable
      rather than scraped.
    """
    from app.services.domain_intelligence import PROVIDER_CATEGORIES, job_is_out_of_domain
    from app.providers import build_registry

    providers = build_registry()
    available = []
    unavailable = []
    for provider in providers:
        if not provider.available:
            unavailable.append(provider)
            continue
        # Global-remote-only boards are excluded for local-onsite intent.
        if provider.supports_remote and getattr(provider, "regions", ()) == ("global-remote",) and not include_global_remote:
            unavailable.append(provider)
            continue
        available.append(provider)

    raw_opportunities: list[NormalizedOpportunity] = []
    provider_statuses: list[dict[str, Any]] = []
    clean_queries = [q.strip() for q in (queries or []) if q and q.strip()]
    for provider in available:
        # Domain-aware category filter: providers that support categories get
        # the candidate's industry mapped in, so the payload reflects their CV
        # domain rather than whatever the board defaults to.
        categories: list[str] = []
        if user_domain is not None and user_domain.confident:
            categories = PROVIDER_CATEGORIES.get(provider.name.lower().split()[0], {}).get(
                user_domain.cluster or "", []
            )
        collected = 0
        errors: list[str] = []
        for query in clean_queries:
            try:
                results = provider.search(query, limit=limit_per_query, categories=categories)
                collected += len(results)
                raw_opportunities.extend(results)
            except Exception as exc:  # pragma: no cover - provider failure
                errors.append(str(exc))
        status: dict[str, Any] = {"name": provider.name, "available": True, "count": collected}
        if categories:
            status["categories"] = categories
        if errors:
            status["error"] = errors[0]
        provider_statuses.append(status)

            # De-duplicate by application_url (or source_url) then title+company.
    # While de-duplicating, collect the distinct source names that offered the
    # same opportunity so the frontend can show "Available from N sources".
    seen_urls: dict[str, list[str]] = {}
    kept_urls: set[str] = set()
    seen_titles: set[str] = set()
    unique: list[NormalizedOpportunity] = []
    for opp in raw_opportunities:
        dedup_key = opp.application_url or opp.source_url
        title_key = f"{opp.title}::{opp.company}".lower()
        if dedup_key:
            sources = seen_urls.setdefault(dedup_key, [])
            if opp.source and opp.source not in sources:
                sources.append(opp.source)
            # First occurrence of this URL: keep the card (with multi-source
            # list). Subsequent dups of the same URL: skip the card but the
            # accumulated sources remain on the kept card.
            if dedup_key in kept_urls:
                continue
            kept_urls.add(dedup_key)
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)
        unique.append(opp)
        # Attach multi-source information to each kept opportunity.
    for opp in unique:
        dedup_key = opp.application_url or opp.source_url
        if dedup_key and len(seen_urls.get(dedup_key, [])) > 1:
            opp.sources_offered = seen_urls[dedup_key]

    matched: list[dict[str, Any]] = []
    rejected_out_of_domain = 0
    for opp in unique:
        if len(matched) >= max_cards:
            break
        # Strict validation engine: reject any opportunity without a real
        # direct application URL. A card with a broken/missing apply button
        # must never reach the frontend.
        if not _valid_http_url(opp.application_url):
            continue
        # Post-fetch DOMAIN guard: a card whose industry clearly differs from
        # the candidate's CV evidence is discarded (e.g. software jobs for a
        # tourism candidate), never shown. The candidate's own skills count as
        # allowed vocabulary so adjacent roles stay visible.
        if user_domain is not None:
            rejected, reason = job_is_out_of_domain(
                opp.title,
                opp.description,
                user_domain,
                extra_terms=list(confirmed_skills or []) + list(evidence_skills or []),
            )
            if rejected:
                rejected_out_of_domain += 1
                continue
        result = match_opportunity(
            opp,
            target_roles=target_roles or [],
            confirmed_skills=confirmed_skills or [],
            evidence_skills=evidence_skills or [],
            preferred_locations=preferred_locations or [],
            provider_supports_remote=getattr(opp, "_provider_remote", False),
        )
        matched.append({
            "title": opp.title,
            "company": opp.company,
            "location": opp.location,
            "employment_type": opp.employment_type,
            "description": opp.description,
            "requirements": opp.requirements,
            "source": opp.source,
            "source_url": opp.source_url,
            "application_url": opp.application_url,
            # `url`/`job_url` aliases so any card consumer has one canonical
            # direct application link to render (per the strict-URL rule).
            "url": opp.application_url,
            "job_url": opp.application_url,
            "published_at": opp.published_at.isoformat() if opp.published_at else None,
            "deadline": opp.deadline.isoformat() if opp.deadline else None,
            "salary": opp.salary,
            "company_logo": opp.company_logo,
                        "sector": opp.sector,
            "match_score": result.score,
            "match_band": result.band,
            "match_reasons": result.reasons,
            "match_components": result.components,
            "sources_offered": (getattr(opp, "sources_offered", None) or None),
        })

    return {
        "jobs": matched,
        "rejected_out_of_domain": rejected_out_of_domain,
        "provider_statuses": provider_statuses + [
            {"name": p.name, "available": False, "reason": p.unavailable_reason}
            for p in unavailable
        ],
        "sources_queried": [p.name for p in available],
        "sources_unavailable": [p.name for p in unavailable],
    }
