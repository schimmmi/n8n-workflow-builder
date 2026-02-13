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
    
    def generate_report(self) -> str:
        """Generate a detailed report for this template"""
        report = f"# 📄 Template Details: {self.name}\n\n"
        report += f"**Template ID:** `{self.id}`\n"
        report += f"**Source:** {self.source}\n"
        report += f"**Category:** {self.category}\n"
        report += f"**Complexity:** {self.complexity}\n"
        report += f"**Node Count:** {self.node_count}\n"
        report += f"**Estimated Setup Time:** {self.estimated_setup_time}\n"
        
        if self.author:
            report += f"**Author:** {self.author}\n"
        if self.source_url:
            report += f"**Source URL:** {self.source_url}\n"
        
        report += f"\n## Description\n\n{self.description}\n\n"
        
        if self.purpose:
            report += f"## Purpose\n\n{self.purpose}\n\n"
        
        if self.tags:
            report += "## Tags\n\n"
            report += ", ".join(f"`{tag}`" for tag in self.tags)
            report += "\n\n"
        
        if self.assumptions:
            report += "## Assumptions\n\n"
            for assumption in self.assumptions:
                report += f"- {assumption}\n"
            report += "\n"
        
        if self.risks:
            report += "## Risks\n\n"
            for risk in self.risks:
                report += f"- {risk}\n"
            report += "\n"
        
        if self.external_systems:
            report += "## External Systems\n\n"
            for system in self.external_systems:
                report += f"- {system}\n"
            report += "\n"
        
        if self.trigger_type:
            report += f"## Trigger Type\n\n{self.trigger_type}\n\n"
        
        if self.data_flow:
            report += f"## Data Flow\n\n{self.data_flow}\n\n"
        
        report += "## Node Structure\n\n"
        for idx, node in enumerate(self.nodes, 1):
            node_name = node.get('name', f'Node {idx}')
            node_type = node.get('type', 'unknown')
            report += f"{idx}. **{node_name}** (`{node_type}`)\n"
        report += "\n"
        
        report += "## Quality Indicators\n\n"
        report += f"- Error Handling: {'✅' if self.has_error_handling else '❌'}\n"
        report += f"- Documentation: {'✅' if self.has_documentation else '❌'}\n"
        report += f"- Uses Credentials: {'✅' if self.uses_credentials else '❌'}\n"
        
        if self.deprecated_nodes:
            report += f"\n⚠️ **Warning:** Uses deprecated nodes: {', '.join(self.deprecated_nodes)}\n"
        
        report += "\n## Usage Statistics\n\n"
        report += f"- Total Usage: {self.usage_count} times\n"
        report += f"- Adaptations: {self.adaptation_count}\n"
        if self.success_rate is not None:
            report += f"- Success Rate: {self.success_rate*100:.1f}%\n"
        
        report += "\n## Implementation Guide\n\n"
        report += "1. Use this template as a starting point for your workflow\n"
        report += "2. Customize node names and parameters to match your requirements\n"
        report += "3. Configure credentials for nodes that require authentication\n"
        report += "4. Test with sample data before deploying to production\n"
        report += "5. Add error handling and monitoring as needed\n\n"
        
        report += f"💡 **Compatibility:** Requires n8n {self.n8n_version}\n"
        
        return report



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
