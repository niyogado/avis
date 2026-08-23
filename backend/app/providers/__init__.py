"""Opportunity providers package.

Every source implements the same normalized contract. Sources without a
verified permitted access method stay registered but unavailable — AVIS
reports them honestly instead of scraping or inventing jobs.
"""
from app.providers.adzuna import AdzunaProvider  # noqa: F401
from app.providers.base import NormalizedOpportunity, OpportunityProvider, ProviderStatus  # noqa: F401
from app.providers.remotive import RemotiveProvider  # noqa: F401

# Honest availability notes for the user-requested regional sources. Each
# becomes implementable later by swapping the stub for a real subclass.
SOURCE_NOTES = {
    "Job in Rwanda": (
        "Drupal site whose /search/ paths are disallowed in robots.txt and no "
        "public API/RSS exists. AVIS will not bypass the site's crawl rules."
    ),
    "Kigali Stores": "Host unreachable during access verification.",
    "IniRwanda Opportunities": "Host unreachable during access verification.",
    "FDO.net.rw": "Website reachable but no public API/RSS found yet; HTML-only pages will not be scraped.",
}


def build_registry() -> list[OpportunityProvider]:
    registry: list[OpportunityProvider] = [RemotiveProvider(), AdzunaProvider()]

    class UnavailableProvider(OpportunityProvider):
        def __init__(self, name: str, reason: str, *, remote: bool, regions: tuple[str, ...]):
            self.name = name
            self.unavailable_reason = reason
            self.available = False
            self.supports_remote = remote
            self.regions = regions

        def search(self, query: str, limit: int = 10):  # pragma: no cover - never called
            return []

    for source_name, reason in SOURCE_NOTES.items():
        rwanda = "rwanda" in source_name.lower() or source_name == "FDO.net.rw"
        registry.append(
            UnavailableProvider(
                name=source_name,
                reason=reason,
                remote=False,
                regions=("rwanda",) if rwanda else (),
            )
        )
    return registry
