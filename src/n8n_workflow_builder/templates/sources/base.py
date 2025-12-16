"""Base Template Source Interface"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TemplateMetadata:
    """Normalized template metadata across all sources"""

    # Identification
    id: str
    source: str  # "n8n_official", "github", "local", "community"

    # Basic Info
    name: str
    description: str
    category: str
    tags: List[str]

    # Version & Compatibility
    n8n_version: str  # e.g. ">=1.20"
    template_version: str  # e.g. "1.0.0"

    # Structure
    nodes: List[Dict]
    connections: Dict
    settings: Dict

    # Complexity & Difficulty
    complexity: str  # "beginner", "intermediate", "advanced"
    node_count: int
    estimated_setup_time: str  # e.g. "15 minutes"

    # Intent Metadata (extracted)
    intent: Optional[str] = None
    purpose: Optional[str] = None
    assumptions: Optional[List[str]] = None
    risks: Optional[List[str]] = None
    external_systems: Optional[List[str]] = None
    trigger_type: Optional[str] = None
    data_flow: Optional[str] = None

    # Provenance & Trust
    author: Optional[str] = None
    source_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    success_rate: Optional[float] = None  # 0.0-1.0
    usage_count: int = 0
    adaptation_count: int = 0

    # Quality Indicators
    has_error_handling: bool = False
    has_documentation: bool = False
    uses_credentials: bool = False
    deprecated_nodes: List[str] = None

    def __post_init__(self):
        if self.deprecated_nodes is None:
            self.deprecated_nodes = []


class TemplateSource(ABC):
    """Abstract base class for template sources"""

    def __init__(self, source_name: str):
        self.source_name = source_name

    @abstractmethod
    async def fetch_templates(self) -> List[TemplateMetadata]:
        """Fetch all templates from this source"""
        pass

    @abstractmethod
    async def get_template(self, template_id: str) -> Optional[TemplateMetadata]:
        """Get a specific template by ID"""
        pass

    @abstractmethod
    async def search_templates(self, query: str) -> List[TemplateMetadata]:
        """Search templates by query"""
        pass

    @abstractmethod
    async def refresh(self) -> int:
        """Refresh template cache, return number of templates"""
        pass

    def normalize_template(self, raw_template: Dict) -> TemplateMetadata:
        """Convert raw template data to normalized TemplateMetadata"""
        # This should be overridden by specific sources if needed
        raise NotImplementedError("Subclass must implement normalize_template")
