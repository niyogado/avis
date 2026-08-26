"""Normalized opportunity format shared by every AVIS provider."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NormalizedOpportunity(BaseModel):
    """One opportunity in AVIS' single normalized shape.

    source_url  -> where AVIS found it (always set).
    application_url -> where the user actually applies. May equal
    source_url for boards without a distinct apply endpoint. Never invented.
    """

    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    description: str = ""
    requirements: list[str] = Field(default_factory=list)
    source: str
    source_url: str
    application_url: Optional[str] = None
    published_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    salary: Optional[str] = None
    # Rich-card extras (all optional; never fabricated by AVIS).
    company_logo: Optional[str] = None
    sector: Optional[str] = None
    # When the same opportunity (by application_url) was offered by more than
    # one verified provider before de-duplication, this lists every source that
    # offered it (e.g. ["Remotive", "Adzuna (RW)"]). Absent for single-source cards.
    sources_offered: Optional[list] = None


class ProviderStatus(BaseModel):
    name: str
    available: bool
    reason: Optional[str] = None


class OpportunityProvider:
    """Base class every opportunity source implements.

    Implementations must only use access methods that are technically and
    legally appropriate for the source (official API, documented public
    endpoint, RSS intended for redistribution, partner integration).
    Anything else stays unavailable rather than being scraped.
    """

    name: str = "unnamed"
    available: bool = False
    unavailable_reason: Optional[str] = None
    supports_remote: bool = False
    regions: tuple[str, ...] = ()

    def search(self, query: str, limit: int = 10, categories: list[str] | None = None) -> list[NormalizedOpportunity]:
        """Fetch listings; `categories` is an optional industry filter the
        source may apply (best effort — AVIS always re-validates relevance)."""
        raise NotImplementedError

    def status(self) -> ProviderStatus:
        return ProviderStatus(name=self.name, available=self.available, reason=self.unavailable_reason)
