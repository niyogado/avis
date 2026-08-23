"""Domain intelligence: industry inference, query building, relevance guard.

AVIS must serve ANY profession, not only technology. This module:

1. Infers the user's professional domain (tourism/hospitality, healthcare,
   finance, education, tech...) from real CV evidence — never a hardcoded
   tech assumption.
2. Builds short job-board search queries dynamically from the candidate's own
   roles, titles, field of study and skills. There is NO fixed default like
   "developer" or "software" anywhere; the last-resort fallback is the
   generic keyword "jobs".
3. Provides the post-fetch OUT-OF-DOMAIN guard: cards whose title/description
   belong to a clearly different industry than the candidate's evidence are
   rejected before they ever reach the frontend.
"""
import re
from dataclasses import dataclass, field
from typing import Any

_WORD_RE = re.compile(r"[a-z0-9+#]+")

# Strong technology signals. If a JOB TITLE contains any of these tokens the
# listing is a technology role regardless of how its description reads.
STRONG_TECH_TITLE_TOKENS = {
    "software", "developer", "frontend", "backend", "fullstack", "full",
    "devops", "sre", "golang", "react", "vue", "angular", "node", "nodejs",
    "python", "django", "laravel", "php", "ruby", "rails", "java", "javascript",
    "typescript", "kotlin", "swift", "flutter", "android", "ios", ".net",
    "c#", "sql", "data", "qa", "selenium", "devsecops", "programmer", "coder",
}

# Industry clusters with representative vocabulary. Used BOTH to infer the
# candidate's domain from their CV and to classify fetched listings.
DOMAIN_CLUSTERS: dict[str, set[str]] = {
    "tech": {
        "software", "developer", "development", "engineer", "engineering",
        "programming", "code", "coding", "frontend", "backend", "fullstack",
        "web", "app", "application", "react", "python", "javascript", "java",
        "php", "sql", "database", "api", "cloud", "aws", "azure", "docker",
        "kubernetes", "linux", "git", "github", "devops", "agile", "scrum",
        "algorithm", "machine", "learning", "ai", "data", "analytics",
        "cybersecurity",
    },
    "tourism_hospitality": {
        "tourism", "hospitality", "hotel", "hotels", "motel", "resort",
        "restaurant", "catering", "tour", "tours", "tourist", "travel",
        "guest", "guests", "reception", "receptionist", "housekeeping",
        "waiter", "waitress", "chef", "cook", "kitchen", "barista",
        "bartender", "banquet", "booking", "reservations", "concierge",
        "lodging", "flight", "airline", "aviation", "culinary", "food",
        "beverage", "event", "events", "venue", "museum", "attraction",
    },
    "healthcare": {
        "nurse", "nursing", "nurses", "health", "healthcare", "medical",
        "medicine", "clinical", "clinic", "patient", "patients", "hospital",
        "pharmacy", "pharmacist", "midwife", "midwifery", "doctor",
        "physician", "dentist", "dental", "surgical", "ward", "icu",
        "laboratory", "lab", "radiography", "physiotherapy", "therapy",
        "caregiver", "epidemiology", "nutrition",
    },
    "finance_accounting": {
        "accounting", "accountant", "finance", "financial", "bookkeeping",
        "bookkeeper", "audit", "auditor", "auditing", "tax", "taxation",
        "payroll", "budget", "budgeting", "banking", "banker", "investment",
        "treasury", "reconciliation", "quickbooks", "ifrs", "cpa",
        "controller", "credit", "loan", "microfinance", "insurance",
    },
    "education": {
        "teacher", "teaching", "tutor", "tutoring", "school", "schools",
        "classroom", "curriculum", "syllabus", "students", "pupil", "pupils",
        "education", "pedagogy", "lecturer", "professor", "academic",
        "kindergarten", "primary", "secondary", "university", "college",
        "lesson", "lessons", "exam", "exams",
    },
    "sales_marketing": {
        "sales", "marketing", "brand", "advertising", "seo", "social",
        "media", "content", "copywriting", "campaign", "leads", "prospecting",
        "telesales", "b2b", "b2c", "crm", "promotions", "market", "research",
        "ecommerce", "communication", "communications", "pr", "publicity",
    },
    "operations_support": {
        "customer", "service", "support", "helpdesk", "callcenter",
        "operations", "operational", "logistics", "coordination",
        "coordinator", "administration", "administrative", "office",
        "secretary", "secretarial", "clerk", "filing", "scheduling",
        "procurement", "supply", "inventory", "stock", "warehouse", "dispatch",
    },
    "legal": {
        "lawyer", "attorney", "legal", "law", "advocate", "paralegal",
        "contract", "contracts", "compliance", "regulatory", "litigation",
        "notary", "judiciary", "court",
    },
    "construction_trades": {
        "construction", "builder", "building", "electrician", "plumber",
        "plumbing", "carpenter", "carpentry", "welder", "welding", "mason",
        "masonry", "mechanic", "mechanical", "technician", "installation",
        "maintenance", "repair", "hvac", "foreman", "civil",
    },
    "agriculture": {
        "agriculture", "agricultural", "farm", "farming", "farmer", "crop",
        "crops", "livestock", "horticulture", "agronomy", "veterinary",
        "veterinarian", "irrigation", "harvest", "dairy", "poultry",
    },
}

# Domains whose roles are predominantly physical/on-site in a specific place.
# Global remote-only boards carry almost none of these, so AVIS does not pretend
# otherwise: those providers are skipped unless the user explicitly prefers remote.
LOCAL_PHYSICAL_DOMAINS = {"tourism_hospitality", "construction_trades", "agriculture"}

# Best-effort category mapping for providers that support category filters.
PROVIDER_CATEGORIES: dict[str, dict[str, list[str]]] = {
    "remotive": {
        "finance_accounting": ["finance-legal"],
        "legal": ["finance-legal"],
        "sales_marketing": ["sales", "marketing"],
        "operations_support": ["customer-support"],
    },
    "adzuna": {
        "tourism_hospitality": ["hospitality-catering"],
        "healthcare": ["healthcare-nursing"],
        "finance_accounting": ["accounting-finance"],
        "sales_marketing": ["sales", "pr-advertising-marketing"],
        "operations_support": ["customer-services"],
        "tech": ["it-jobs"],
        "legal": ["legal"],
        "construction_trades": ["trade-jobs"],
        "agriculture": ["agriculture-fishing-forestry"],
    },
}


@dataclass
class UserDomain:
    """The candidate's inferred professional domain from real CV evidence."""

    cluster: str | None = None          # key of DOMAIN_CLUSTERS or None if unknown
    confidence: float = 0.0             # 0..1 based on vocabulary hit volume
    terms: list[str] = field(default_factory=list)  # matched vocabulary words

    @property
    def confident(self) -> bool:
        return self.cluster is not None and self.confidence >= 0.34

    @property
    def local_physical(self) -> bool:
        return self.cluster in LOCAL_PHYSICAL_DOMAINS


def _tokens(text: str) -> list[str]:
    return [tok for tok in _WORD_RE.findall((text or "").lower()) if len(tok) > 1]


def _as_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if isinstance(item, str)]
    return []


def infer_user_domain(fields: dict[str, Any]) -> UserDomain:
    """Infer the candidate's industry cluster from CV-derived text fields."""
    weighted_text = " ".join(
        " ".join(_as_list(fields.get(name))) if name in ("skills", "experience", "education", "career_directions")
        else str(fields.get(name) or "")
        for name in ("headline", "skills", "professional_profile", "experience", "education", "career_directions")
    )
    tokens = _tokens(weighted_text)
    if not tokens:
        return UserDomain()

    counts: dict[str, int] = {}
    matched_terms: dict[str, list[str]] = {}
    for cluster, vocab in DOMAIN_CLUSTERS.items():
        hits = [token for token in tokens if token in vocab]
        counts[cluster] = len(hits)
        matched_terms[cluster] = sorted(set(hits))

    best_cluster = max(counts, key=lambda name: counts[name])
    best_count = counts[best_cluster]
    if best_count == 0:
        return UserDomain()

    total = sum(counts.values())
    dominance = best_count / max(1, total)
    volume = min(1.0, best_count / 8)
    confidence = round(0.6 * dominance + 0.4 * volume, 3)

    return UserDomain(
        cluster=best_cluster,
        confidence=confidence,
        terms=matched_terms[best_cluster][:25],
    )


def _job_cluster(title_tokens: set[str], body_tokens: set[str]) -> tuple[str | None, int]:
    """Classify one listing; the title weighs triple versus the body."""
    scores: dict[str, int] = {}
    for cluster, vocab in DOMAIN_CLUSTERS.items():
        scores[cluster] = len(title_tokens & vocab) * 3 + len(body_tokens & vocab)
    best = max(scores, key=lambda name: scores[name])
    return (best, scores[best]) if scores[best] > 0 else (None, 0)


def job_is_out_of_domain(
    job_title: str,
    job_description: str,
    user_domain: UserDomain,
    extra_terms: list[str] | None = None,
) -> tuple[bool, str]:
    """Post-fetch validation: reject listings outside the candidate's domain.

    Returns (rejected, reason). When the candidate's domain is unknown nothing
    is rejected — AVIS never guesses. `extra_terms` carries the candidate's own
    evidenced skills/roles so legitimately adjacent roles (e.g. hospitality ->
    customer support when the CV lists "customer service") are preserved.
    """
    if not user_domain.confident:
        return False, ""

    title_tokens = set(_tokens(job_title))
    body_tokens = title_tokens | set(_tokens(job_description))
    job_cluster, _strength = _job_cluster(title_tokens, body_tokens)

    user_vocab = set(_tokens(" ".join(user_domain.terms)))
    user_vocab |= set(_tokens(" ".join(extra_terms or [])))

    # Rule 1 — hard tech mismatch: a clearly-titled tech role is dropped for
    # every non-tech candidate ("Senior Golang Developer" for a tourism CV).
    if user_domain.cluster != "tech":
        tech_title_hits = sorted(title_tokens & STRONG_TECH_TITLE_TOKENS)
        if tech_title_hits and (job_cluster == "tech" or not job_cluster):
            return True, f"Technology role ('{tech_title_hits[0]}') does not match your professional domain."

    if job_cluster is None:
        # No recognizable industry signal: keep only when the listing overlaps
        # the candidate's own evidenced vocabulary (their skills/roles).
        if body_tokens & user_vocab:
            return False, ""
        return True, "Listing has no relation to your professional background."

    if job_cluster == user_domain.cluster:
        return False, ""

    # Different cluster: adjacent service roles are legitimate career paths
    # (e.g. hospitality -> customer support) when the listing genuinely overlaps
    # the candidate's evidenced vocabulary. Otherwise it is a mismatch.
    if body_tokens & user_vocab:
        return False, ""
    return True, f"Listing belongs to a different industry ({job_cluster.replace('_', ' ')})."


def _known_vocab(user_context: dict[str, Any]) -> set[str]:
    """Words the candidate has evidenced: domain vocabulary + their skills."""
    vocab = set().union(*DOMAIN_CLUSTERS.values())
    evidence = user_context.get("cv_evidence") or {}
    confirmation = user_context.get("user_confirmation") or {}
    intent = user_context.get("career_intent") or {}
    historical = intent.get("historical_evidence") or {}
    skill_sources = (
        _as_list(evidence.get("skills"))
        + _as_list(confirmation.get("confirmed_skills"))
        + _as_list(historical.get("skills"))
        + _as_list(evidence.get("experience"))
        + _as_list(historical.get("experience"))
    )
    for phrase in skill_sources:
        vocab |= set(_tokens(phrase))
    return vocab


def build_search_queries(user_context: dict[str, Any], limit: int = 5) -> list[str]:
    """Dynamic search keywords from the candidate's OWN evidence.

    Priority: confirmed/target roles -> headline/current role -> past job
    titles -> field of study -> domain vocabulary -> short skills. Every entry
    is a clean keyword phrase (<= 5 words); full AI sentences are dropped.
    NEVER returns a fixed tech default — the last resort is generic "jobs".
    """
    confirmation = user_context.get("user_confirmation") or {}
    intent = user_context.get("career_intent") or {}
    historical = intent.get("historical_evidence") or {}
    evidence = user_context.get("cv_evidence") or {}

    candidates: list[str] = []
    candidates += _as_list(confirmation.get("target_roles"))
    candidates += _as_list(confirmation.get("career_interests"))
    if confirmation.get("primary_role"):
        candidates.append(str(confirmation["primary_role"]))
    candidates += _as_list(intent.get("target_roles"))
    if intent.get("current_role"):
        candidates.append(str(intent["current_role"]))

    # Past job titles: take the leading words of each experience line.
    for line in (_as_list(evidence.get("experience")) + _as_list(historical.get("experience")))[:4]:
        head = re.split(r"\||—|–|,| at ", line.strip())[0]
        candidates.append(head.strip(" -"))

    # Field of study from education lines. Institution-only names ("Lycée de
    # Ruhango", "University of X") are useless as job keywords, so require the
    # line to contain at least one known industry/domain word.
    education_lines = _as_list(historical.get("education"))[:2] or _as_list(evidence.get("education"))[:2]
    domain_vocab = set().union(*DOMAIN_CLUSTERS.values())
    for line in education_lines:
        if set(_tokens(line)) & domain_vocab:
            candidates.append(line.strip())

    # Domain vocabulary inferred from the whole profile.
    domain = infer_user_domain({
        "headline": intent.get("current_role") or "",
        "skills": evidence.get("skills"),
        "professional_profile": evidence.get("professional_profile"),
        "experience": evidence.get("experience"),
        "education": evidence.get("education"),
        "career_directions": intent.get("target_roles"),
    })
    if domain.confident:
        candidates.extend(domain.terms[:4])

    # Short skill keywords last (they refine, not define, the domain).
    candidates.extend(_as_list(evidence.get("skills"))[:4])

    generic_words = {"roles", "role", "knowledge", "skills", "years", "experience", "jobs", "work"}
    # Never search for the candidate's own name (CV headers leak into
    # experience/education lines).
    name_tokens: set[str] = set()
    full_name = str((user_context.get("profile") or {}).get("full_name") or "")
    if full_name:
        name_tokens = {tok.lower() for tok in _tokens(full_name)}

    cleaned: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        value = re.sub(r"\s+", " ", str(item)).strip(" .•-*;:")
        if not value:
            continue
        words = value.split()
        if len(words) > 5 or len(value) > 48:
            continue  # sentence-like text is useless on job boards
        lowered = [w.lower().strip(",.!?") for w in words]
        if any(word in name_tokens for word in lowered):
            continue  # candidate name fragment, not a job keyword
        if len(words) == 1 and lowered[0] not in _known_vocab(user_context):
            # Single token matching nothing the candidate evidenced (no domain
            # vocabulary, no skill) is almost certainly a leaked personal-name
            # fragment from the CV header ("Odette"), not a job keyword.
            continue
        if all(word in generic_words for word in lowered):
            continue
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(value)
        if len(cleaned) >= limit:
            break

    return cleaned or ["jobs"]  # generic fallback only — never a tech term

