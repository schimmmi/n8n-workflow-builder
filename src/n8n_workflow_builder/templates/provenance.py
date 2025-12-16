"""
Template Provenance & Trust Tracking

The underrated but critical feature for production use.

Tracks:
- Source & Author
- Adaptation history
- Success rates
- Usage statistics
- Trust metrics

Enables:
- "Prefer templates with high success rates"
- "Show me templates from trusted sources"
- "Which templates are most adapted?"
"""
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import json


@dataclass
class ProvenanceRecord:
    """Provenance record for a template"""

    # Identity
    template_id: str
    template_name: str
    source: str
    author: Optional[str] = None

    # Timestamps
    created_at: datetime = None
    last_used_at: datetime = None
    last_updated_at: datetime = None

    # Usage metrics
    usage_count: int = 0
    deployment_count: int = 0
    adaptation_count: int = 0

    # Success metrics
    successful_executions: int = 0
    failed_executions: int = 0
    total_executions: int = 0

    # Trust metrics (0.0-1.0)
    trust_score: float = 0.5  # Start with neutral
    reliability_score: float = 0.5
    security_score: float = 0.5

    # Quality indicators
    has_error_handling: bool = False
    has_documentation: bool = False
    has_tests: bool = False
    uses_best_practices: bool = False

    # Adaptation history
    adaptations: List[str] = None

    # User feedback
    rating: Optional[float] = None  # 0.0-5.0
    rating_count: int = 0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.adaptations is None:
            self.adaptations = []

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_executions == 0:
            return 0.0
        return self.successful_executions / self.total_executions

    @property
    def overall_trust_score(self) -> float:
        """Calculate overall trust score"""
        # Weighted average of trust factors
        weights = {
            "trust_score": 0.3,
            "reliability_score": 0.25,
            "security_score": 0.25,
            "success_rate": 0.2
        }

        score = (
            self.trust_score * weights["trust_score"] +
            self.reliability_score * weights["reliability_score"] +
            self.security_score * weights["security_score"] +
            self.success_rate * weights["success_rate"]
        )

        return min(score, 1.0)


class ProvenanceTracker:
    """Tracks template provenance and trust metrics"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path
        self.records: Dict[str, ProvenanceRecord] = {}

        # Load existing records if storage exists
        if storage_path:
            self._load()

    def track_template(self, template_id: str, template_name: str, source: str, author: Optional[str] = None) -> ProvenanceRecord:
        """Start tracking a template"""
        if template_id not in self.records:
            record = ProvenanceRecord(
                template_id=template_id,
                template_name=template_name,
                source=source,
                author=author
            )
            self.records[template_id] = record
            self._save()

        return self.records[template_id]

    def record_usage(self, template_id: str):
        """Record template usage"""
        if template_id in self.records:
            record = self.records[template_id]
            record.usage_count += 1
            record.last_used_at = datetime.now()
            self._save()

    def record_deployment(self, template_id: str):
        """Record template deployment"""
        if template_id in self.records:
            record = self.records[template_id]
            record.deployment_count += 1
            self._save()

    def record_adaptation(self, template_id: str, adaptation_description: str):
        """Record template adaptation"""
        if template_id in self.records:
            record = self.records[template_id]
            record.adaptation_count += 1
            record.adaptations.append({
                "timestamp": datetime.now().isoformat(),
                "description": adaptation_description
            })
            self._save()

    def record_execution(self, template_id: str, success: bool):
        """Record workflow execution result"""
        if template_id in self.records:
            record = self.records[template_id]
            record.total_executions += 1

            if success:
                record.successful_executions += 1
            else:
                record.failed_executions += 1

            # Update reliability score based on recent success rate
            record.reliability_score = record.success_rate

            self._save()

    def update_trust_score(self, template_id: str, score: float):
        """Update trust score (manual adjustment)"""
        if template_id in self.records:
            record = self.records[template_id]
            record.trust_score = max(0.0, min(1.0, score))
            self._save()

    def update_security_score(self, template_id: str, has_vulnerabilities: bool):
        """Update security score based on analysis"""
        if template_id in self.records:
            record = self.records[template_id]

            if has_vulnerabilities:
                record.security_score = max(0.0, record.security_score - 0.2)
            else:
                record.security_score = min(1.0, record.security_score + 0.1)

            self._save()

    def add_rating(self, template_id: str, rating: float):
        """Add user rating (0.0-5.0)"""
        if template_id in self.records:
            record = self.records[template_id]

            # Calculate new average rating
            total_rating = (record.rating or 0.0) * record.rating_count
            total_rating += rating
            record.rating_count += 1
            record.rating = total_rating / record.rating_count

            # Influence trust score
            normalized_rating = rating / 5.0  # Normalize to 0.0-1.0
            record.trust_score = (record.trust_score + normalized_rating) / 2

            self._save()

    def get_record(self, template_id: str) -> Optional[ProvenanceRecord]:
        """Get provenance record"""
        return self.records.get(template_id)

    def get_top_templates(self, limit: int = 10, sort_by: str = "trust") -> List[ProvenanceRecord]:
        """
        Get top templates

        Args:
            limit: Number of templates to return
            sort_by: "trust", "usage", "success_rate", "rating"
        """
        records = list(self.records.values())

        if sort_by == "trust":
            records.sort(key=lambda r: r.overall_trust_score, reverse=True)
        elif sort_by == "usage":
            records.sort(key=lambda r: r.usage_count, reverse=True)
        elif sort_by == "success_rate":
            records.sort(key=lambda r: r.success_rate, reverse=True)
        elif sort_by == "rating":
            records.sort(key=lambda r: r.rating or 0.0, reverse=True)

        return records[:limit]

    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        records = list(self.records.values())

        if not records:
            return {
                "total_templates": 0,
                "total_usage": 0,
                "total_deployments": 0,
                "total_executions": 0,
                "average_trust_score": 0.0,
                "average_success_rate": 0.0
            }

        total_usage = sum(r.usage_count for r in records)
        total_deployments = sum(r.deployment_count for r in records)
        total_executions = sum(r.total_executions for r in records)

        avg_trust = sum(r.overall_trust_score for r in records) / len(records)
        avg_success = sum(r.success_rate for r in records) / len(records) if records else 0.0

        return {
            "total_templates": len(records),
            "total_usage": total_usage,
            "total_deployments": total_deployments,
            "total_executions": total_executions,
            "average_trust_score": avg_trust,
            "average_success_rate": avg_success,
            "by_source": self._stats_by_source(records),
            "top_templates": [
                {"id": r.template_id, "name": r.template_name, "trust": r.overall_trust_score}
                for r in self.get_top_templates(5)
            ]
        }

    def _stats_by_source(self, records: List[ProvenanceRecord]) -> Dict:
        """Statistics by source"""
        by_source = {}

        for record in records:
            source = record.source
            if source not in by_source:
                by_source[source] = {
                    "count": 0,
                    "usage": 0,
                    "avg_trust": 0.0
                }

            by_source[source]["count"] += 1
            by_source[source]["usage"] += record.usage_count

        # Calculate averages
        for source in by_source:
            source_records = [r for r in records if r.source == source]
            by_source[source]["avg_trust"] = sum(r.overall_trust_score for r in source_records) / len(source_records)

        return by_source

    def filter_trusted(self, min_trust_score: float = 0.7) -> List[ProvenanceRecord]:
        """Get templates above minimum trust threshold"""
        return [
            record for record in self.records.values()
            if record.overall_trust_score >= min_trust_score
        ]

    def _save(self):
        """Save records to storage"""
        if not self.storage_path:
            return

        try:
            data = {
                template_id: self._serialize_record(record)
                for template_id, record in self.records.items()
            }

            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)

        except Exception as e:
            print(f"Error saving provenance data: {e}")

    def _load(self):
        """Load records from storage"""
        if not self.storage_path:
            return

        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)

            self.records = {
                template_id: self._deserialize_record(record_data)
                for template_id, record_data in data.items()
            }

        except FileNotFoundError:
            pass  # No existing data
        except Exception as e:
            print(f"Error loading provenance data: {e}")

    def _serialize_record(self, record: ProvenanceRecord) -> Dict:
        """Serialize record to dict"""
        data = asdict(record)

        # Convert datetime to ISO string
        if isinstance(data.get("created_at"), datetime):
            data["created_at"] = data["created_at"].isoformat()
        if isinstance(data.get("last_used_at"), datetime):
            data["last_used_at"] = data["last_used_at"].isoformat()
        if isinstance(data.get("last_updated_at"), datetime):
            data["last_updated_at"] = data["last_updated_at"].isoformat()

        return data

    def _deserialize_record(self, data: Dict) -> ProvenanceRecord:
        """Deserialize dict to record"""
        # Convert ISO string to datetime
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "last_used_at" in data and data["last_used_at"] and isinstance(data["last_used_at"], str):
            data["last_used_at"] = datetime.fromisoformat(data["last_used_at"])
        if "last_updated_at" in data and data["last_updated_at"] and isinstance(data["last_updated_at"], str):
            data["last_updated_at"] = datetime.fromisoformat(data["last_updated_at"])

        return ProvenanceRecord(**data)
