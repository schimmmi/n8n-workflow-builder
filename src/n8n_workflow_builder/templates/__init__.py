"""
Template System v2.0

Intelligent template system with:
- Multi-source adapters (official, GitHub, local)
- Intent extraction ("WHY" not just "WHAT")
- Intent-based matching (describe goal → get suggestions)
- Template adaptation (2022 template → 2025-ready workflow)
- Provenance tracking (trust & success metrics)
"""

from .sources import (
    TemplateSource,
    TemplateMetadata,
    N8nOfficialSource,
    GitHubSource,
    LocalSource,
    TemplateRegistry
)
from .intent_extractor import TemplateIntentExtractor
from .matcher import TemplateMatcher
from .adapter import TemplateAdapter
from .provenance import ProvenanceTracker, ProvenanceRecord

__all__ = [
    # Sources
    "TemplateSource",
    "TemplateMetadata",
    "N8nOfficialSource",
    "GitHubSource",
    "LocalSource",
    "TemplateRegistry",

    # Intelligence
    "TemplateIntentExtractor",
    "TemplateMatcher",
    "TemplateAdapter",

    # Tracking
    "ProvenanceTracker",
    "ProvenanceRecord"
]
