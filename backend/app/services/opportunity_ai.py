"""AI inspection & summarizer for opportunity cards.

Uses EjoChat (backend-only) to:
1. generate an industry-tailored match insight + clean description snippet
   for every card, based on the user's real CV context; and
2. suggest adjacent job titles/keywords for "Explore More" pagination when a
   profession's primary listings are exhausted.

Every function degrades gracefully: if EjoChat fails or returns malformed
JSON, callers receive the deterministic fallback instead of an error, and no
score or URL is ever invented here — the matcher owns scoring, providers own
URLs.
"""
import json
import re
from typing import Any

from app.services.ai_service import chat_with_ai


def _candidate_brief(context: dict[str, Any]) -> str:
    """Compact candidate brief built ONLY from confirmed/extracted context."""
    profile = context.get("profile") or {}
    confirmation = context.get("user_confirmation") or {}
    intent = context.get("career_intent") or {}
    evidence = context.get("cv_evidence") or {}

    role = (
        confirmation.get("primary_role")
        or context.get("confirmed_user_intent")
        or intent.get("current_role")
        or profile.get("headline")
        or ""
    )
    level = confirmation.get("professional_level") or ""
    skills = confirmation.get("confirmed_skills") or evidence.get("skills") or context.get("skills") or []
    interests = confirmation.get("career_interests") or []
    locations = confirmation.get("preferred_locations") or []

    parts = [f"Profession/target role: {role}" if role else "Profession: unknown"]
    if level:
        parts.append(f"Level: {level}")
    if skills:
        parts.append(f"Skills: {', '.join(map(str, skills[:12]))}")
    if interests:
        parts.append(f"Career interests: {', '.join(map(str, interests[:5]))}")
    if locations:
        parts.append(f"Preferred locations: {', '.join(map(str, locations[:5]))}")
    return "; ".join(parts)


_TAG_RE = re.compile(r"<[^>]+>")


def _fallback_snippet(job: dict[str, Any]) -> str:
    text = _TAG_RE.sub(" ", str(job.get("description") or ""))
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= 320:
        return text
    return text[:320].rsplit(" ", 1)[0] + "…"


def enrich_opportunities(
    jobs: list[dict[str, Any]],
    user_context: dict[str, Any],
) -> list[dict[str, Any]]:
    """Attach `ai_match_insight` and `description_snippet` to each card.

    The score/band on each card is untouched — EjoChat only writes prose.
    On any failure the original jobs are returned with rule-based snippets.
    """
    if not jobs:
        return jobs

    brief = _candidate_brief(user_context)
    compact = []
    for idx, job in enumerate(jobs):
        snippet_source = (job.get("description") or "")[:400]
        compact.append(
            f"[{idx}] TITLE: {job.get('title')} | ORG: {job.get('company') or 'n/a'} "
            f"| LOCATION: {job.get('location') or 'n/a'} | TYPE: {job.get('employment_type') or 'n/a'} "
            f"| SECTOR: {job.get('sector') or 'n/a'} | ABOUT: {snippet_source}"
        )

    prompt = f"""
You are AVIS, a career intelligence assistant. A candidate's verified context:

{brief}

Below are {len(compact)} REAL job listings from live providers. For EACH listing,
write insights tailored to THIS candidate's specific profession and background.

Return ONLY valid JSON: {{"insights": [{{"index": 0, "match_insight": "...", "snippet": "..."}}, ...]}}

Rules:
- match_insight: 1-2 sentences explaining why this listing fits (or does not fit)
  the candidate's specific field, skills, and experience level. Reference their
  actual domain (e.g. patient care for nurses, ledger reconciliation for
  accountants). Never invent experience or credentials they do not have.
- snippet: 2-3 sentence plain-text overview extracted strictly from the listing's
  ABOUT text. No marketing language, no invented duties.
- Keep every "index" exactly as given. Return all {len(compact)} entries.

LISTINGS:
{chr(10).join(compact)}
""".strip()

    try:
        raw = chat_with_ai(prompt)
        parsed = json.loads(re.search(r"\{.*\}", raw, flags=re.S).group(0))
        entries = parsed.get("insights")
        if not isinstance(entries, list):
            raise ValueError("no insights array")
        by_index = {
            int(e["index"]): e
            for e in entries
            if isinstance(e, dict) and str(e.get("index", "")).lstrip("-").isdigit()
        }
    except Exception:
        # Graceful degradation: keep deterministic matcher reasons.
        return [
            {
                **job,
                "ai_match_insight": None,
                "description_snippet": _fallback_snippet(job),
            }
            for job in jobs
        ]

    enriched = []
    for idx, job in enumerate(jobs):
        entry = by_index.get(idx) or {}
        insight = str(entry.get("match_insight") or "").strip() or None
        snippet = str(entry.get("snippet") or "").strip() or _fallback_snippet(job)
        enriched.append({
            **job,
            "ai_match_insight": insight,
            "description_snippet": snippet,
        })
    return enriched


def suggest_expansion_queries(user_context: dict[str, Any]) -> list[str]:
    """Adjacent titles/keywords for paginated exploration (AI, with fallback)."""
    brief = _candidate_brief(user_context)
    prompt = f"""
Candidate context: {brief}

List 8 alternative but adjacent job titles or search keywords that would find
roles this candidate could realistically pursue, including roles in their own
field, adjacent specializations, and one step up (e.g. senior/lead variants).

Return ONLY valid JSON: {{"queries": ["...", "..."]}}
- Each entry: 1-4 words, suitable as a job-board search keyword.
- No explanations.
""".strip()

    try:
        raw = chat_with_ai(prompt)
        parsed = json.loads(re.search(r"\{.*\}", raw, flags=re.S).group(0))
        queries = parsed.get("queries")
        if not isinstance(queries, list):
            raise ValueError("no queries array")
        cleaned: list[str] = []
        seen: set[str] = set()
        for item in queries:
            if not isinstance(item, str):
                continue
            value = re.sub(r"\s+", " ", item).strip()
            key = value.lower()
            if not value or len(value) > 60 or key in seen:
                continue
            seen.add(key)
            cleaned.append(value)
        if cleaned:
            return cleaned
        raise ValueError("empty queries")
    except Exception:
        return _fallback_expansion(user_context)


def _fallback_expansion(user_context: dict[str, Any]) -> list[str]:
    """Deterministic expansion from target roles and skills."""
    confirmation = user_context.get("user_confirmation") or {}
    intent = user_context.get("career_intent") or {}
    evidence = user_context.get("cv_evidence") or {}

    terms: list[str] = []
    terms += confirmation.get("target_roles") or []
    terms += confirmation.get("career_interests") or []
    if confirmation.get("primary_role"):
        terms.append(confirmation["primary_role"])
    terms += (intent.get("target_roles") or [])[:3]
    terms += (evidence.get("skills") or [])[:6]
    terms += (intent.get("historical_evidence") or {}).get("skills", [])[:4]

    cleaned: list[str] = []
    seen: set[str] = set()
    for term in terms:
        value = str(term).strip()
        key = value.lower()
        if not value or len(value) > 60 or key in seen:
            continue
        seen.add(key)
        cleaned.append(value)
    return cleaned

def ai_search_plan(user_context):
    """AI-driven adaptive career-search plan (never a fixed tech query)."""
    brief = _candidate_brief(user_context)
    prompt = (
        "You are AVIS, an adaptive career-search agent. Candidate verified info ONLY:\n"
        + brief +
        "\n\nBuild a SEARCH PLAN. Do NOT assume a profession. Return ONLY JSON:\n"
        '{"professions": ["..."], "interpretation": "...", "seniority": "entry|mid|senior|student/intern", '
        '"queries": [{"query": "2-5 word keyword", "location": "optional"}], "emphasis": ["..."]}\n'
        "Rules: 4-6 queries, clean 1-5 word keywords (no 'company','time','jobs'). "
        "Students: internship/graduate/entry-level queries. Never add facts the candidate did not provide."
    )
    try:
        raw = chat_with_ai(prompt)
        parsed = json.loads(re.search(r"\{.*\}", raw, flags=re.S).group(0))
        queries = []
        seen = set()
        for entry in (parsed.get("queries") or []):
            meta = entry if isinstance(entry, dict) else {}
            query = re.sub(r"\s+", " ", str(meta.get("query") or "")).strip()
            if len(query) < 2 or query.lower() in seen or len(query.split()) > 6 or len(query) > 60:
                continue
            seen.add(query.lower())
            queries.append({"query": query, "location": str(meta.get("location") or "").strip()[:40]})
        if len(queries) < 2:
            raise ValueError("not enough queries")
        return {
            "professions": _as_string_list(parsed.get("professions"))[:2],
            "interpretation": str(parsed.get("interpretation") or "").strip()[:260],
            "seniority": str(parsed.get("seniority") or "").strip()[:20],
            "queries": queries[:6],
            "skills": _as_string_list(parsed.get("emphasis"))[:8],
            "ai_driven": True,
        }
    except Exception:
        return _fallback_search_plan(user_context)


def _fallback_search_plan(user_context):
    """Deterministic plan when the AI provider is unreachable."""
    from app.services.domain_intelligence import build_search_queries
    confirmation = user_context.get("user_confirmation") or {}
    intent = user_context.get("career_intent") or {}
    evidence = user_context.get("cv_evidence") or {}
    skills = evidence.get("skills") or user_context.get("skills") or []
    profession = (confirmation.get("primary_role")
                  or (confirmation.get("target_roles") or [None])[0]
                  or intent.get("current_role") or "")
    roles = _as_string_list(confirmation.get("target_roles")
                            or intent.get("target_roles")
                            or ([profession] if profession else []))
    queries = []
    for q in build_search_queries(user_context, limit=6):
        if q and q.lower() not in {x["query"].lower() for x in queries}:
            queries.append({"query": q, "location": ""})
    return {
        "professions": roles or ([profession] if profession else []),
        "interpretation": (("Understood as " + profession) if profession
                           else "Profile is still thin — AVIS is exploring broadly until you confirm your career intent."),
        "seniority": str(confirmation.get("professional_level") or intent.get("professional_level") or "")[:20],
        "queries": queries or [{"query": "jobs", "location": ""}],
        "skills": skills[:8],
        "ai_driven": False,
    }


def _as_string_list(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    return [str(item).strip() for item in value if str(item).strip() and item not in (None, "")]
