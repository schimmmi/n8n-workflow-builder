"""Template Source Adapters"""

from .base import TemplateSource, TemplateMetadata
from .n8n_official import N8nOfficialSource
from .github import GitHubSource
from .local import LocalSource
from .registry import TemplateRegistry

__all__ = [
    "TemplateSource",
    "TemplateMetadata",
    "N8nOfficialSource",
    "GitHubSource",
    "LocalSource",
    "TemplateRegistry"
]
